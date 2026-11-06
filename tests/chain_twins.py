"""The chain's twins and files for V12's gate and its KPI driver (lane CHv, plan P4-D430).

Shared by `tests/test_stage6_validate_chain.py` and
`tools/measurements/kpi_chain_validate.py`: an invented clinic table, a
switched description of it written by `synthtwin profile` with the
chain's switch and the oracle's fixed test key, `synthtwin validate`
run on a file of rows with the switch, the report's V12 section read
back, a twin the oracle's walk (method G16.2,
`tools/reference/chain_oracle.py`) deals from a published chain, and
V12.4's data mutants as row builders. Every table is invented here.
"""

import contextlib
import hashlib
import importlib.util
import io
import json
import os
import pathlib
import random
import re
from fractions import Fraction

from synthtwin import cli

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
FLOOR = 11
HEADER = ["age", "gender", "group", "pressure", "event"]


def _load_oracle(name):
    spec = importlib.util.spec_from_file_location("chv_" + name, REPOSITORY / "tools" / "reference" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


co = _load_oracle("chain_oracle")
oc = _load_oracle("oracle_cases")


# -- the fixtures -----------------------------------------------------------


def _clinic_rows(n_rows=800, seed=7):
    """An invented clinic: age, gender, a group that follows age, a pressure that follows age, an event that follows age."""
    draw = random.Random(seed)
    rows = []
    for _place in range(n_rows):
        age = draw.randint(18, 90)
        gender = draw.choice(["f", "m"])
        group = draw.choice(["a", "b", "c"]) if age < 50 else draw.choice(["c", "d"])
        pressure = f"{round(100 + age * 0.5 + draw.gauss(0, 8), 1)}"
        event = "1" if draw.random() < 0.05 + age / 120 else "0"
        rows += [[f"{age}", gender, group, pressure, event]]
    return rows


def _write(path, header, rows, empty_at=()):
    lines = [",".join(header)]
    for at in range(len(rows)):
        if at in empty_at:
            lines += [",".join([""] * len(header))]
        lines += [",".join(rows[at])]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return path


def _quiet(call):
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        code = call()
    return code, out.getvalue()


class Described:
    """One switched description and what the tests read from it."""

    def __init__(self, folder, header, rows, empty_at=()):
        self.folder = folder
        self.header = header
        self.rows = rows
        self.table = _write(folder / "clinic.csv", header, rows, empty_at)
        data = folder / "data"
        data.mkdir(mode=0o700)
        if os.name != "nt":
            data.chmod(0o700)
        key = data / "chain-key"
        key.touch(mode=0o600)
        if os.name != "nt":
            key.chmod(0o600)
        key.write_bytes(oc.TEST_KEY)
        self.data = data
        code, said = _quiet(lambda: cli.main(["profile", str(self.table), "--out-dir", str(folder)], chain=cli.ChainRun(folder=str(data))))
        assert code == 0, said
        # A column held by an open question (lane HX: a three-figure
        # measurement read as possible record numbers) holds the chain back;
        # each question is answered as the data is, `measurement` or `keep`,
        # and the table described again with the answers. The Safe Harbor
        # question an age of 90 opens (lane SH, plan P4-D427; batch 4k's
        # merge) offers neither and is left open: the column is published
        # top-coded at 90, which its ages of 18 to 90 already are.
        questions = folder / "clinic-questions.json"
        asked = json.loads(questions.read_text(encoding="utf-8"))
        if asked["asked"]:
            for entry in asked["asked"]:
                offered = str(entry["answers_you_can_give"])
                if "'measurement'" in offered:
                    entry["your_answer"] = "measurement"
                elif "'keep'" in offered:
                    entry["your_answer"] = "keep"
            questions.write_text(json.dumps(asked, indent=1) + "\n", encoding="utf-8", newline="\n")
            code, said = _quiet(
                lambda: cli.main(
                    ["profile", str(self.table), "--out-dir", str(folder), "--answers", str(questions)],
                    chain=cli.ChainRun(folder=str(data), replace_description=True),
                )
            )
            assert code == 0, said
        self.path = folder / "clinic-profile.json"
        self.document = json.loads(self.path.read_text(encoding="utf-8"))
        self.statistical = self.document["relationships"]["statistical"]
        assert self.statistical is not None and self.statistical["chain"], said
        self.blocks = {block["name"]: block for block in self.document["columns"]}
        self._runs = 0

    def validate(self, rows, switched=True, empty_at=(), header=None, description=None):
        """Validate a file of `rows` against this description; return (code, written report, screen)."""
        self._runs += 1
        place = self.folder / f"run{self._runs}"
        place.mkdir()
        measured = _write(place / "twin.csv", header or self.header, rows, empty_at)
        run = cli.ChainRun() if switched else None
        code, said = _quiet(
            lambda: cli.main(["validate", str(description or self.path), "--twin", str(measured), "--out-dir", str(place)], chain=run)
        )
        written = place / "twin-quality.txt"
        return code, written.read_text(encoding="utf-8") if written.exists() else "", said


def _section(report):
    """The chain's section of a written report (V12)."""
    start = report.index("BETWEEN COLUMNS: THE CHAIN'S FAMILY TABLES (V12)")
    end = report.index("pair(s) read 'implied'.", start)
    return report[start:end]


def _verdicts(report):
    """Each band-total line's and each family line's verdict, by column or family index."""
    section = _section(report)
    totals = dict(re.findall(r"^  '([^']+)': (HELD|MISSED|NOT CHECKABLE);", section, re.M))
    families = {int(at): verdict for at, verdict in re.findall(r"^  family (\d+): .*: (HELD|MISSED|WITHHELD|NOT CHECKABLE)$", section, re.M)}
    return totals, families


def _families(described):
    return described.statistical["chain"]


def _holding(described, column):
    return [at for at, family in enumerate(_families(described)) if column == family["child"] or column in [p["column"] for p in family["parents"]]]


# -- the oracle's walk: a twin dealt from the published chain (method G16.2) --


def _label_of(block):
    """Each published spelling of a label column to its level (`levels[].variants`), the label itself too."""
    out = {}
    for entry in block["levels"]:
        out[entry["label"]] = entry["label"]
        for spelling in entry.get("variants") or {}:
            out[spelling] = entry["label"]
    return out


def _oracle_ladder(name, block, raw, floor=FLOOR, position=0):
    role = block["role"]
    if role in ("binary", "categorical", "long_tail_labels", "constant"):
        levels = [(entry["label"], entry["count"]) for entry in block["levels"]]
        label_of = _label_of(block)
        cells = [("missing",) if v == "" else (("level", label_of[v]) if v in label_of else ("held",)) for v in raw]
        return co.ladder_of(name, role, cells, levels=levels, floor=floor, position=position)
    rungs = dict(block.get("percentiles") or {})
    rungs.update(block.get("percentiles_between") or {})
    rungs = {key: Fraction(value) for key, value in rungs.items() if value is not None}
    # A reading and a published rung are both read as the binary64 they
    # name (the product's reading, `chain.read_column`): the description
    # writes a rung as the JSON float `114.7`, whose exact value is not
    # the decimal 114.7 a cell writes, so reading the cell as an exact
    # decimal puts a cell equal to a rung below it (3 rows of `pressure`
    # on the clinic fixture; CHo's own product case holds whole numbers).
    cells = [("missing",) if v == "" else ("value", Fraction(float(v))) for v in raw]
    return co.ladder_of(name, role, cells, rungs=rungs, floor=floor, position=position)


def _oracle_chain(statistical):
    return [
        co.Family(f["child"], int(f["level"][1]), [(p["column"], int(p["level"][1])) for p in f["parents"]], f["anchor"], f["table"])
        for f in statistical["chain"]
    ]


def _words(families, n_rows, salt):
    words = {}
    for at in range(families):
        rows = []
        for row in range(n_rows):
            digest = hashlib.blake2b(f"{salt}/{at}/{row}".encode("ascii"), digest_size=24).digest()
            rows += [[int.from_bytes(digest[k : k + 8], "big") for k in (0, 8, 16)]]
        words[at] = rows
    return words


def _rungs(block):
    """A number column's published rungs, each the binary64 its JSON float names, read exactly."""
    rungs = dict(block.get("percentiles") or {})
    rungs.update(block.get("percentiles_between") or {})
    return {key: Fraction(float(value)) for key, value in rungs.items() if value is not None}


def _cell_band(lad, block, text):
    """A cell's `L0` band on a published ladder (the oracle's `l0` descriptors), or None where it stands in none."""
    numeric = block["role"] in ("count", "continuous")
    rungs = _rungs(block) if numeric else {}
    for band, members in enumerate(lad.l0):
        for one in members:
            if one == "missing" and text == "":
                return band
            if isinstance(one, tuple) and one[0] == "range" and numeric and text != "":
                x = Fraction(float(text))
                low = rungs[one[1]] if one[1] is not None else None
                high = rungs[one[2]] if one[2] is not None else None
                if (low is None or low <= x) and (high is None or x < high):
                    return band
            if isinstance(one, tuple) and one[0] == "level" and not numeric and text != "":
                label = _label_of(block).get(text)
                if one[1] == label or (one[1] == "held back" and label is None):
                    return band
    return None


def _walk_twin(described, chain=None, salt="chv", cells_from=None):
    """A twin the oracle's walk deals from the published chain (method G16.2).

    Each column's cells are the table's own, or, with `cells_from`, the
    cells of another file of rows (a twin's, made column by column), each
    put in its `L0` band of the published ladder and arranged into rows by
    the walk; a family whose cells cannot meet its published table is
    dealt its moved table (G16.6), as the oracle's walk does.
    """
    header = described.header
    values = {name: [row[at] for row in described.rows] for at, name in enumerate(header)}
    source = cells_from if cells_from is not None else described.rows
    dealt = {name: [row[at] for row in source] for at, name in enumerate(header)}
    lads = {}
    for entry in described.statistical["ladder"]:
        name = entry["column"]
        lads[name] = _oracle_ladder(name, described.blocks[name], values[name], position=header.index(name))
        assert lads[name].totals == entry["totals"], name
    cells = {}
    for name in lads:
        bands = [[] for _band in lads[name].l0]
        for row in range(len(source)):
            text = dealt[name][row]
            band = lads[name].row_l0[row] if cells_from is None else _cell_band(lads[name], described.blocks[name], text)
            if band is None:
                raise AssertionError(f"a cell of {name} stands in no published band")
            reading = None if text == "" or described.blocks[name]["role"] not in ("count", "continuous") else Fraction(float(text))
            bands[band] += [(text, reading)]
        cells[name] = bands
    families = chain if chain is not None else _oracle_chain(described.statistical)
    index, listing, _dealt = co.walk_rows(families, lads, cells, _words(len(families), len(source), salt))
    rows = []
    for row in range(len(source)):
        rows += [[listing[name][index[name][row]][0] if name in lads else dealt[name][row] for name in header]]
    return rows


def _family_with_parents(described):
    """The first family with a parent whose child is a number column."""
    for at, family in enumerate(_families(described)):
        if family["parents"] and described.blocks[family["child"]]["role"] in ("count", "continuous"):
            return at, family
    raise AssertionError("no family of a number child with a parent")


def _band_codes(described, rows):
    """Each row's band at every level of every eligible column, read by the oracle on the TABLE's ladder."""
    header = described.header
    values = {name: [row[at] for row in rows] for at, name in enumerate(header)}
    real = {name: [row[at] for row in described.rows] for at, name in enumerate(header)}
    out = {}
    for entry in described.statistical["ladder"]:
        name = entry["column"]
        lad = _oracle_ladder(name, described.blocks[name], real[name])
        by_text = {}
        for row in range(len(described.rows)):
            by_text[real[name][row]] = lad.row_l0[row]
        out[name] = (lad, [by_text[text] for text in values[name]])
    return out


def _dropped_parent(described):
    """The chain with its last family of two or more parents losing its last parent, the table summed over it."""
    families = _oracle_chain(described.statistical)
    at = max(i for i, family in enumerate(families) if len(family.parents) >= 2)
    family = families[at]
    dropped, _level = family.parents[-1]
    sizes = []
    for name, level in family.parents:
        entry = next(e for e in described.statistical["ladder"] if e["column"] == name)
        sizes += [len(entry["l0"]) if level == 0 else len(entry["l1"] if level == 1 else entry["l2"])]
    width = sizes[-1]
    table = []
    for cell in range(len(family.table) // width):
        row = [0] * len(family.table[0])
        for k in range(width):
            for band, count in enumerate(family.table[cell * width + k]):
                row[band] += count
        table += [row]
    kept = family.parents[:-1]
    anchor = next(i for i, f in enumerate(families) if all(p in f.members() for p, _ in kept))
    families[at] = co.Family(family.child, family.level, kept, anchor, table)
    return at, dropped, families


def _off_by(clinic, moved):
    """The table with `moved` readings of `pressure`'s lowest band written above its highest rung."""
    place = clinic.header.index("pressure")
    lowest = sorted(range(len(clinic.rows)), key=lambda r: Fraction(clinic.rows[r][place]))[:moved]
    rows = [list(row) for row in clinic.rows]
    for at in lowest:
        rows[at][place] = "999.0"
    return rows
