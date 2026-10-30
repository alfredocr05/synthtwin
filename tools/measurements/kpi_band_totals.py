"""K-S6-02, layer L0: every within-column fact unchanged with and without L0; the column meets its L0 band totals (plan P4-D429).

Lane BT's stamp of `K-S6-02` as method G5.7h rewords it, on the product's
own twins of invented tables (no real data), each described with the
chain's switch (`chain.describe`, a fixed test key), loaded behind it
(`contract.load_profile(..., chain=True)`) and generated with and without
its ladder:

- (i) THE SWITCH OFF: every switched description, its ladder emptied,
  makes byte for byte the twin of the same table described without the
  chain, at every seed: `switch_off_differences`, target 0, over
  `switch_off_checked` pairs;
- (ii) THE SAME CELLS: each eligible column's cells, as a multiset, are
  the cells the interface G16 calls hands over plus the reserved ones
  (`generation.cells_by_band`): `multiset_differences`, target 0;
- (iii) THE BAND TOTALS: each eligible column laid with its band totals,
  read back the way the profile reads a table (`chain.read_column`, the
  first `E` records holding nothing no tabled row), holds every
  published `L0` band count: `rows_off`, target 0, over `bands_checked`
  bands of `columns_checked` columns (a column rule B3 names is neither
  checked nor counted); the twin without L0, read the same way, misses
  them by `bare_rows_off` rows, which shows the battery discriminates;
- (iv) NO FACT LOST: every check of the quality report
  (`validation.measure`, today's windows of G12.2, G12.3 and G12.3a at
  G12.2's half unit, against the description without its chain), on
  every column and on the file, that the twin without L0 holds and the
  twin with it misses: `facts_lost`, target 0, each named; and every
  note of the twin's own report -- a deviation, the mode's among them, or
  a rung or moment outside its window -- present with L0 and absent
  without it, rule B3's notes aside: `notes_gained`, target 0, each named;
- (v) THE SHAPE: on every eligible column of numbers (a count, a
  continuous column, an affixed column read by its core), the
  Kolmogorov-Smirnov distance between the twin and the real column is
  no larger with L0 than without it, and no value the real column holds
  on the floor's rows or more is emptied with L0 where the twin without
  it holds it: `shape_regressions`, target 0, each named;
- (vi) THE KEYS KEPT: on every eligible column whose real cells all
  differ, the different values the twin with L0 writes fall short of the
  real column's by `keys_lost`, target 0, each named (the orchestrator's
  ruling (c) on lane BT's skeptic 1, MAJOR 4: no value of an all-different
  column lost at 20,000 or 200,000 rows);
- (vii) THE EDGE VALUES: on every eligible column of numbers, each edge
  value the real column holds whose count with L0 lies further from the
  real count than without it: `edge_values_worse` over
  `edge_values_checked`, each column named with how many of its edges
  (lane BT's skeptic 1, item 6: the band totals move the cells a cut
  crosses onto the nearest value inside the piece, which on a uniform
  whole-number column sits beside the edge);
- the columns made without their band totals (rule B3, named by exact
  column name): `made_without`, reported; the tables whose switched
  description its own loader refused: `chain_refused`, reported.

    PYTHONPATH=src:tests python tools/measurements/kpi_band_totals.py --kpi [--rows 5000,20000] [--seeds 0,1,2] [--draws 7,11] [--no-zoo] [--zoo-only claims,surveys]

The battery: G5.7i's ten-column table at 5,000 and 20,000 rows, each at
TWO table draws (table seeds 7 and 11), the count of few values of
G14.3a case 1 at 20,000, an invented ward of 20,000 rows holding records
that hold nothing (E > 0) both as a text file and as a workbook, seeds 0
to 2; the every-role table at 2,000 rows, seeds 0 to 4; and the health
zoo's 25 exports at 20,000 rows (table seed 0) at seeds 0 and 1, unless
`--no-zoo`. One process of a few hundred megabytes, about an hour with the
zoo. The 200,000-row leg is a separate run under the heavy-slot guard
(`--rows 200000 --seeds 0,1,2,3,4 --draws 7 --no-zoo`, one table draw).
"""

import dataclasses
import datetime
import io
import json
import pathlib
import random
import sys
import tempfile
import time
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import fixtures  # noqa: E402
import workbooks  # noqa: E402

from synthtwin import (  # noqa: E402
    canonical,
    chain,
    chain_rules,
    contract,
    dialect,
    errors,
    generation,
    parsing,
    profile,
    reading,
    rendering,
    sheetwriting,
    taxonomy,
    validation,
)

FLOOR = 11
TEST_KEY = bytes(range(32))
SPELLED = {"code": False, "measurement": False, "decimal_comma": False}
RANGED = ("count", "continuous", "datetime", "time_of_day", "affixed_number")
LABELS = ("binary", "categorical", "long_tail_labels", "constant")
NUMBERS = ("count", "continuous", "affixed_number")
# Each table whose switched description its own loader refused, with the
# loader's words: the chain's profile side's, reported and never judged.
REFUSED: "dict[str, str]" = {}


def _ten(rows: int, seed: int = 7) -> "tuple[list[str], list[list[str]]]":
    """G5.7i's invented ten-column table: an age, a pressure, a stay, a count of few values, visits, money, a change, a date, a clock."""
    draw = random.Random(seed)
    body: "list[list[str]]" = []
    for place in range(rows):
        age = draw.randint(1, 9) * 10 + draw.randint(0, 9)
        pressure = "" if draw.random() < 0.05 else f"{round(draw.gauss(120, 15), 1)}"
        stay = f"{round(draw.lognormvariate(1.2, 0.8), 2)}"
        few = min(int(draw.expovariate(0.6)), 12)
        visits = min(int(draw.gammavariate(2, 2)), 25)
        money = f"{round(draw.lognormvariate(5, 1), 2):.2f}"
        change = f"{round(draw.gauss(0, 2), 1)}"
        day = draw.randint(0, 364)
        visit = f"2023-{1 + day // 31 if day // 31 < 12 else 12:02d}-{1 + day % 28:02d}"
        if draw.random() < 0.15:
            clock = "08:00"
        else:
            minutes = int(min(max(draw.gauss(13 * 60, 150), 6 * 60), 22 * 60))
            clock = f"{minutes // 60:02d}:{minutes % 60:02d}"
        body += [[f"R{place:06d}", str(age), pressure, stay, str(few), str(visits), money, change, visit, clock, draw.choice(["F", "M"])]]
    return ["id", "age", "pressure", "stay", "few", "visits", "money", "change", "visit_date", "clock", "gender"], body


def _few(rows: int) -> "tuple[list[str], list[list[str]]]":
    """G14.3a case 1 (b): a count of few values with one rare high value, scaled to ``rows``."""
    counts = [1568, 8436, 5813, 2464, 1018, 425, 162, 59, 30, 14, 7, 1, 2]
    cells: "list[str]" = []
    for value in range(len(counts)):
        cells += [str(value)] * round(counts[value] * rows / 20000)
    cells += ["16"]
    while len(cells) < rows:
        cells += ["1"]
    cells = cells[:rows]
    draw = random.Random(5)
    draw.shuffle(cells)
    return ["id", "count", "group"], [[f"R{place:06d}", cells[place], draw.choice(["a", "b"])] for place in range(rows)]


def _ward(rows: int) -> "tuple[list[str], list[list[str]]]":
    """An invented ward of records some of which hold nothing (E > 0): a stay, a lab, a change, a date with heavy days, a stamp, two clocks."""
    draw = random.Random(20261024)
    heavy = ["2022-01-01", "2023-07-04"]
    body: "list[list[str]]" = []
    for place in range(rows):
        if draw.random() < 0.005:
            body += [[""] * 9]
            continue
        u = draw.random()
        stay = 0 if u < 0.2 else 1 if u < 0.35 else min(int(draw.lognormvariate(1.3, 1.0)), 400)
        lab = "NA" if draw.random() < 0.03 else "4.00" if draw.random() < 0.06 else f"{draw.lognormvariate(1.5, 0.5):.2f}"
        change = "0.0" if draw.random() < 0.1 else f"{draw.gauss(0, 3):.1f}"
        v = draw.random()
        day = heavy[0] if v < 0.08 else heavy[1] if v < 0.12 else datetime.date.fromordinal(738156 + draw.randint(0, 3 * 365)).isoformat()
        minutes = draw.randint(0, 1439)
        stamp = f"{day} {minutes // 60:02d}:{minutes % 60:02d}:00"
        w = draw.random()
        if w < 0.04:
            arrival = ""
        elif w < 0.14:
            arrival = "08:00"
        elif w < 0.2:
            arrival = "12:00"
        else:
            m = int(min(max(draw.gauss(14 * 60, 180), 0), 1439))
            arrival = f"{m // 60:02d}:{m % 60:02d}"
        s = int(min(max(draw.gauss(10 * 3600, 12000), 0), 86399))
        given = f"{s // 3600:02d}:{(s // 60) % 60:02d}:{s % 60:02d}"
        body += [[f"R{place:07d}", str(stay), lab, change, day, stamp, arrival, given, draw.choice(["F", "M"])]]
    return ["record", "stay", "lab", "change", "admit_date", "stamp", "arrival", "given_at", "gender"], body


def _ward_book(rows: int) -> bytes:
    """The ward's stay, lab, change, admission date, arrival and gender as a workbook: dates as day counts, clocks as day fractions, its records holding nothing formatted blank cells (lane BT's second repair: a workbook holding date and clock columns too)."""
    _header, body = _ward(rows)
    names = ["stay", "lab", "change", "admit_date", "arrival", "gender"]
    picked = [1, 2, 3, 4, 6, 8]
    strings: "list[str]" = [name for name in names] + ["NA", "F", "M"]
    index_of = {text: place for place, text in enumerate(strings)}
    letters = "ABCDEF"
    epoch = datetime.date(1899, 12, 30)
    sheet_rows = [(1, [workbooks.cell(f"{letters[k]}1", str(k), "s") for k in range(6)])]
    for place in range(len(body)):
        number = place + 2
        row = body[place]
        if not any(row):
            sheet_rows += [(number, [workbooks.cell(f"{letters[k]}{number}", "", "", workbooks.HEADER_STYLE) for k in range(6)])]
            continue
        cells: "list[str]" = []
        for k in range(6):
            text = row[picked[k]]
            reference = f"{letters[k]}{number}"
            if names[k] == "admit_date":
                cells += [workbooks.cell(reference, str((datetime.date.fromisoformat(text) - epoch).days), "", 1)]
            elif names[k] == "arrival":
                if text:
                    hours, minutes = text.split(":")
                    cells += [workbooks.cell(reference, repr((int(hours) * 60 + int(minutes)) / 1440), "", 3)]
            elif text in index_of:
                cells += [workbooks.cell(reference, str(index_of[text]), "s")]
            else:
                cells += [workbooks.cell(reference, text)]
        sheet_rows += [(number, cells)]
    return workbooks.package([
        ("[Content_Types].xml", workbooks._content_types(1, True, False, False)),
        ("_rels/.rels", workbooks._root_rels()),
        ("xl/workbook.xml", workbooks._workbook([("Data", "")])),
        ("xl/_rels/workbook.xml.rels", workbooks._workbook_rels(1, True)),
        ("xl/styles.xml", workbooks._styles()),
        ("xl/sharedStrings.xml", workbooks._shared_strings(strings)),
        ("xl/worksheets/sheet1.xml", workbooks.sheet(sheet_rows, dimension=f"A1:F{len(body) + 1}")),
    ])


def _zipf(values: "tuple[str, ...]") -> "tuple[list[str], list[float]]":
    return [value for value in values], [1.0 / (rank + 1) for rank in range(len(values))]


def _codes(rows: int) -> "tuple[list[str], list[list[str]]]":
    """Invented codes drawn as a payer's files draw them, a dose on a few levels, a score in steps of five, and two keys (the gate's former table, its checks moved here by lane BT's second repair)."""
    draw = random.Random(17)
    drg = _zipf(("470", "291", "871", "392", "190", "065", "064", "189", "292", "872"))
    revenue = _zipf(("0450", "0250", "0300", "0320", "0360", "0636", "0730", "0120"))
    apc = _zipf(("5012", "5521", "5072", "5302", "5734", "5822", "5113"))
    classes = _zipf(("98", "49", "108", "127", "205", "106", "59", "651", "101", "53"))
    amounts = (["250", "500", "750", "1000", "1500", "2000"], [0.20, 0.35, 0.10, 0.25, 0.06, 0.04])
    serial = [str(1 + step) for step in range(rows)]
    draw.shuffle(serial)
    body: "list[list[str]]" = []
    for place in range(rows):
        barthel = 5 * min(20, max(0, int(round(draw.gauss(13, 4.5)))))
        body += [[
            f"CLM{200000000 + place}",
            serial[place],
            draw.choices(drg[0], drg[1])[0],
            draw.choices(revenue[0], revenue[1])[0],
            draw.choices(apc[0], apc[1])[0],
            draw.choices(classes[0], classes[1])[0],
            draw.choices(amounts[0], amounts[1])[0],
            str(barthel),
        ]]
    return ["claim", "serial", "drg", "revenue_code", "apc", "clinical_class", "dose_mg", "barthel"], body


def _sparse(rows: int) -> "tuple[list[str], list[list[str]]]":
    """Sparse number columns beside a key: a count on about 115 rows, a wide count on about 300, a one-figure reading on about 150, bands of 11 to 24 rows (lane BT's verify, item 1)."""
    draw = random.Random(1001)
    body: "list[list[str]]" = []
    for place in range(rows):
        few = str(draw.randint(0, 60)) if draw.random() < 115 / rows else ""
        wide = str(draw.randint(0, 200)) if draw.random() < 300 / rows else ""
        reading_ = f"{draw.gauss(7, 2):.1f}" if draw.random() < 150 / rows else ""
        body += [[f"S{place:06d}", few, wide, reading_, draw.choice(["p", "q"])]]
    return ["key", "sparse_count", "sparse_wide", "sparse_reading", "arm"], body


def _lab(rows: int) -> "tuple[list[str], list[list[str]]]":
    """A laboratory value at one figure with sentinel heaps at 10.0, 600.0 and 650.0, some absent, beside a score and an arm (lane BT's verify, item 1)."""
    draw = random.Random(77)
    body: "list[list[str]]" = []
    for _place in range(rows):
        w = draw.random()
        lab = "600.0" if w < 0.015 else "650.0" if w < 0.021 else "10.0" if w < 0.033 else ("" if w < 0.05 else f"{draw.gauss(100, 15):.1f}")
        score = 3 if draw.random() < 0.22 else min(int(draw.gammavariate(2.5, 1.6)), 20)
        body += [[lab, str(score), draw.choice(["p", "q"])]]
    return ["lab_value", "score", "arm"], body


@dataclasses.dataclass
class _Described:
    path: pathlib.Path
    table: reading.Table
    document: "dict[str, object]"
    statistical: "dict[str, object] | None"
    loaded: "contract.Profile | None"
    plain: contract.Profile
    workbook: bool


def _described(folder: pathlib.Path, name: str, path: pathlib.Path) -> _Described:
    settings = taxonomy.Settings(small_cell_floor=FLOOR)
    table = reading.read_table(str(path), small_cell_floor=FLOOR)
    document = profile.build_document(table, settings, [], [], [])
    plain_path = folder / f"{name}-plain.json"
    plain_path.write_text(canonical.serialize(document), encoding="utf-8", newline="\n")
    plain = contract.load_profile(str(plain_path))
    workbook = plain.source.workbook is not None
    chained = chain.describe(table, document, settings, chain.ChainSwitch(name, TEST_KEY))
    if chained.statistical is None:
        return _Described(path, table, document, None, None, plain, workbook)
    written = dict(document)
    relationships = dict(written["relationships"])  # type: ignore[call-overload]
    relationships["statistical"] = chained.statistical
    written["relationships"] = relationships
    on = folder / f"{name}-switched.json"
    on.write_text(canonical.serialize(written), encoding="utf-8", newline="\n")
    try:
        loaded = contract.load_profile(str(on), chain=True)
    except errors.ProfileError as refused:
        REFUSED[name] = f"{refused}"[:200]
        return _Described(path, table, document, None, None, plain, workbook)
    return _Described(path, table, document, chained.statistical, loaded, plain, workbook)


def _twin_file(folder: pathlib.Path, described: _Described, profile_: contract.Profile, twin: generation.Twin, tag: str) -> pathlib.Path:
    if described.workbook:
        out = folder / f"twin-{tag}.xlsx"
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            for member, text in sheetwriting.workbook_members(profile_, twin):
                archive.writestr(member, text)
        out.write_bytes(buffer.getvalue())
        return out
    out = folder / f"twin-{tag}.csv"
    out.write_text("".join(rendering.twin_csv_pieces(twin)), encoding="utf-8", newline="")
    return out


def _l0_totals(path: pathlib.Path, described: _Described) -> "dict[str, list[int]]":
    """Each eligible column's L0 totals in a twin, read the way the profile reads the table: the first `E` records holding nothing no tabled row."""
    back = reading.read_table(str(path), small_cell_floor=FLOOR)
    settings = taxonomy.Settings(small_cell_floor=FLOOR)
    blocks: "dict[str, tuple[int, dict[str, object]]]" = {}
    for place, block in enumerate(described.document["columns"]):  # type: ignore[arg-type]
        blocks[f"{block['name']}"] = (place, block)
    blank = chain_rules.records_holding_nothing(described.document)
    held = [reading.column_values(back, place) for place in range(len(back.column_names))]
    skipped: "set[int]" = set()
    for row in range(back.n_rows):
        if len(skipped) >= blank:
            break
        if all(dialect.holds_nothing(column[row]) for column in held):
            skipped |= {row}
    held = []
    found: "dict[str, list[int]]" = {}
    assert described.statistical is not None
    for entry in described.statistical["ladder"]:  # type: ignore[union-attr]
        place, block = blocks[entry["column"]]
        read = chain.read_column(back, place, block, settings, SPELLED, "", blank)
        if read is None:
            continue
        start = [0] * len(read.start.names)
        for row in range(back.n_rows):
            if row not in skipped:
                start[read.codes[row]] += 1
        totals: "list[int]" = []
        for band in entry["l0"]:
            names = [tuple(item) if isinstance(item, list) else item for item in band]
            totals += [sum(start[k] for k in range(len(read.start.names)) if read.start.names[k] in names)]
        found[entry["column"]] = totals
    return found


def _missed(plain: contract.Profile, path: pathlib.Path) -> "set[tuple[str, str, str]]":
    """Every check of the quality report the twin misses, every column's and the file's."""
    outcome = validation.measure(plain, str(path))
    return {(f"{check.column}", check.fact, check.subcheck) for check in outcome.checks if check.verdict == validation.MISSED}


def _notes(twin: generation.Twin) -> "set[tuple[str, str]]":
    """The twin's own report: each deviation (rule B3's aside) and each rung or moment outside its window."""
    found = {(note.column, note.fact) for note in twin.deviations if note.fact != "band totals"}
    found |= {(approximation.column, f"{approximation.fact} outside its window") for approximation in twin.approximations if not approximation.inside}
    return found


def _core(cell: str, affixed: bool) -> "float | None":
    """A cell's number: as written, or on an affixed column its core, the characters before its first digit and after its last set aside."""
    text = cell.strip()
    if not text:
        return None
    value = parsing.parse_number(text)
    if value is not None or not affixed:
        return value
    start = 0
    while start < len(text) and not (text[start].isdigit() or text[start] in "+-."):
        start += 1
    end = len(text)
    while end > start and not text[end - 1].isdigit():
        end -= 1
    return parsing.parse_number(text[start:end]) if end > start else None


def _numbers(cells: "list[str] | tuple[str, ...]", affixed: bool = False) -> "dict[float, int]":
    counts: "dict[float, int]" = {}
    for cell in cells:
        value = _core(cell, affixed)
        if value is not None:
            counts[value] = counts.get(value, 0) + 1
    return counts


def _ks(left: "dict[float, int]", right: "dict[float, int]") -> int:
    """The Kolmogorov-Smirnov distance between two columns of numbers, in rows."""
    worst = 0
    up = 0
    down = 0
    for value in sorted(set(left) | set(right)):
        up += left.get(value, 0)
        down += right.get(value, 0)
        worst = max(worst, abs(up - down))
    return worst


def _tables(
    rows_list: "list[int]", folder: pathlib.Path, zoo: bool, only: "list[str]", draws: "list[int]"
) -> "list[tuple[str, pathlib.Path, list[int]]]":
    """Every table of the battery: its name, its file and the seeds it is generated at (``only``: the zoo's tables named, alone)."""
    out: "list[tuple[str, pathlib.Path, list[int]]]" = []
    if only:
        import health_zoo

        for spec in health_zoo.TABLES:
            if spec.name in only:
                out += [(f"zoo.{spec.name}", health_zoo.write_table(spec, folder / "zoo", 20000, 0), [0, 1])]
        if out:
            return out

    def written(name: str, made: "tuple[list[str], list[list[str]]]") -> pathlib.Path:
        path = folder / f"{name}.csv"
        path.write_text(fixtures.rows_to_csv(made[0], made[1]), encoding="utf-8", newline="\n")
        return path

    for rows in rows_list:
        for table_seed in draws:
            out += [(f"ten{rows}@{table_seed}", written(f"ten{rows}-{table_seed}", _ten(rows, table_seed)), [])]
    if only:
        # ``only`` names tables of the battery (not of the zoo): those alone.
        small_only = min(max(rows_list), 20000)
        builders = {"few": _few, "ward": _ward, "codes": _codes, "sparse": _sparse, "lab": _lab}
        picked: "list[tuple[str, pathlib.Path, list[int]]]" = [entry for entry in out if entry[0] in only]
        for name in only:
            if name in builders:
                seeds = [0, 1] if name == "codes" else [0, 1, 2, 3, 4] if name in ("sparse", "lab") else []
                picked += [(name, written(name, builders[name](small_only)), seeds)]
            if name == "ward-book":
                book_only = folder / "ward-book.xlsx"
                book_only.write_bytes(_ward_book(small_only))
                picked += [("ward-book", book_only, [])]
        return picked
    small = min(max(rows_list), 20000)
    out += [("few", written("few", _few(small)), [])]
    out += [("ward", written("ward", _ward(small)), [])]
    book = folder / "ward-book.xlsx"
    book.write_bytes(_ward_book(small))
    out += [("ward-book", book, [])]
    # ...and the shapes lane BT's verify and its gate's former checks hold
    # (its second repair): sparse codes and keys, sparse columns of bands
    # of 11 to 24 rows, a laboratory value with sentinel heaps.
    out += [("codes", written("codes", _codes(small)), [0, 1])]
    out += [("sparse", written("sparse", _sparse(small)), [0, 1, 2, 3, 4])]
    out += [("lab", written("lab", _lab(small)), [0, 1, 2, 3, 4])]
    every = folder / "every_role.csv"
    every.write_text(fixtures.every_role_table(n_rows=2000), encoding="utf-8", newline="\n")
    out += [("every_role", every, [0, 1, 2, 3, 4])]
    if zoo:
        import health_zoo

        for spec in health_zoo.TABLES:
            path = health_zoo.write_table(spec, folder / "zoo", 20000, 0)
            out += [(f"zoo.{spec.name}", path, [0, 1])]
    return out


def measure(
    rows_list: "list[int]",
    seeds: "list[int]",
    zoo: bool = True,
    only: "list[str] | None" = None,
    draws: "tuple[int, ...]" = (7, 11),
) -> "dict[str, object]":
    started = time.time()
    value: "dict[str, object]" = {
        "switch_off_differences": 0,
        "switch_off_checked": 0,
        "multiset_differences": 0,
        "rows_off": 0,
        "bare_rows_off": 0,
        "bands_checked": 0,
        "columns_checked": 0,
        "facts_lost": 0,
        "notes_gained": 0,
        "shape_regressions": 0,
        "keys_lost": 0,
        "keys_checked": 0,
        "edge_values_worse": 0,
        "edge_values_checked": 0,
        "made_up": 0,
        "twins": 0,
    }
    named: "dict[str, list[str]]" = {
        "facts_lost_named": [],
        "notes_gained_named": [],
        "shape_regressions_named": [],
        "keys_lost_named": [],
        "edge_values_worse_named": [],
        "made_up_named": [],
    }
    made_without: "list[str]" = []
    reach: "list[str]" = []
    with tempfile.TemporaryDirectory(prefix="synthtwin-band-totals-") as kept:
        folder = pathlib.Path(kept)
        for name, path, own_seeds in _tables(rows_list, folder, zoo, only or [], list(draws)):
            described = _described(folder, name.replace("/", "-"), path)
            loaded = described.loaded
            statistical = described.statistical
            if loaded is None or statistical is None:
                path.unlink(missing_ok=True)
                continue
            roles = {column.name: column.statistical_type for column in loaded.columns}
            published = {entry["column"]: entry["totals"] for entry in statistical["ladder"]}  # type: ignore[union-attr, index]
            without: "set[str]" = set()
            edges_of: "dict[str, tuple[float, ...]]" = {}
            for column_name, (cut, why) in generation._l0_columns(loaded).items():
                if cut is None:
                    made_without += [f"{name}.{column_name}: {why}"]
                    without |= {column_name}
                else:
                    edges_of[column_name] = tuple(cut.edges)
            judged = [column for column in published if column not in without and (roles[column] in RANGED or roles[column] in LABELS)]
            reach += [f"{name}: {len(judged)} column(s) laid with their band totals, {len(without)} made without"]
            affixed = {column: roles[column] == "affixed_number" for column in judged}
            real = {
                column: _numbers(reading.column_values(described.table, described.table.column_names.index(column)), affixed[column])
                for column in judged
                if roles[column] in NUMBERS
            }
            keys: "dict[str, int]" = {}
            for column in judged:
                cells = [cell for cell in reading.column_values(described.table, described.table.column_names.index(column)) if cell.strip()]
                if cells and len(set(cells)) == len(cells):
                    keys[column] = len(cells)
                cells = []
            for seed in (own_seeds or seeds):
                handed: "list[tuple[str, list[int], int]]" = []
                built = generation._row_placement

                def hooked(step, profile_, content, drawn, finished, reserved=None, readings=None):  # type: ignore[no-untyped-def]
                    found = generation.cells_by_band(profile_, step, content, drawn, reserved, readings)
                    if found is not None:
                        cells = sorted([cell for group in found.groups for cell in group] + list(found.reserved))
                        handed.append((found.column, cells, len(content)))
                    if reserved is None:
                        return built(step, profile_, content, drawn, finished)
                    return built(step, profile_, content, drawn, finished, reserved, readings)

                generation._row_placement = hooked
                try:
                    twin = generation.generate_held(loaded, seed)
                finally:
                    generation._row_placement = built
                for _column, cells, count in handed:
                    if cells != list(range(count)):
                        value["multiset_differences"] = int(value["multiset_differences"]) + 1  # type: ignore[call-overload]
                bare = generation.generate_held(described.plain, seed)
                value["twins"] = int(value["twins"]) + 2  # type: ignore[call-overload]
                stripped = dataclasses.replace(
                    loaded, relationships=dataclasses.replace(loaded.relationships, ladder=(), families=0)
                )
                left = "".join(rendering.twin_csv_pieces(generation.generate_held(stripped, seed)))
                value["switch_off_checked"] = int(value["switch_off_checked"]) + 1  # type: ignore[call-overload]
                if left != "".join(rendering.twin_csv_pieces(bare)):
                    value["switch_off_differences"] = int(value["switch_off_differences"]) + 1  # type: ignore[call-overload]
                left = ""
                with_path = _twin_file(folder, described, loaded, twin, f"{seed}-l0")
                bare_path = _twin_file(folder, described, described.plain, bare, f"{seed}-bare")
                found_totals = _l0_totals(with_path, described)
                bare_totals = _l0_totals(bare_path, described)
                for column_name in judged:
                    if column_name not in found_totals:
                        continue
                    value["columns_checked"] = int(value["columns_checked"]) + 1  # type: ignore[call-overload]
                    value["bands_checked"] = int(value["bands_checked"]) + len(found_totals[column_name])  # type: ignore[call-overload]
                    off = sum(abs(a - b) for a, b in zip(found_totals[column_name], published[column_name])) // 2
                    value["rows_off"] = int(value["rows_off"]) + off  # type: ignore[call-overload]
                    if roles[column_name] in RANGED:
                        bare_off = sum(abs(a - b) for a, b in zip(bare_totals[column_name], published[column_name])) // 2
                        value["bare_rows_off"] = int(value["bare_rows_off"]) + bare_off  # type: ignore[call-overload]
                lost = _missed(described.plain, with_path) - _missed(described.plain, bare_path)
                value["facts_lost"] = int(value["facts_lost"]) + len(lost)  # type: ignore[call-overload]
                named["facts_lost_named"] += [f"{name}@{seed}: {column}.{fact}.{subcheck}" for column, fact, subcheck in sorted(lost)]
                gained = _notes(twin) - _notes(bare)
                value["notes_gained"] = int(value["notes_gained"]) + len(gained)  # type: ignore[call-overload]
                named["notes_gained_named"] += [f"{name}@{seed}: {column}.{fact}" for column, fact in sorted(gained)]
                names_of = [column.name for column in loaded.columns]
                for column_name in real:
                    place = names_of.index(column_name)
                    with_counts = _numbers(generation.twin_column(twin, place), affixed[column_name])
                    bare_counts = _numbers(generation.twin_column(bare, place), affixed[column_name])
                    worse = _ks(with_counts, real[column_name]) - _ks(bare_counts, real[column_name])
                    emptied = [
                        held for held, count in real[column_name].items()
                        if count >= FLOOR and with_counts.get(held, 0) == 0 and bare_counts.get(held, 0) > 0
                    ]
                    further: "list[float]" = []
                    for edge in edges_of.get(column_name, ()):
                        held = real[column_name].get(edge, 0)
                        if held <= 0:
                            continue
                        value["edge_values_checked"] = int(value["edge_values_checked"]) + 1  # type: ignore[call-overload]
                        if abs(with_counts.get(edge, 0) - held) > abs(bare_counts.get(edge, 0) - held):
                            further += [edge]
                    # ...REPORTED: values the twin with L0 writes that neither the
                    # real column nor the twin without L0 holds (the gate's former
                    # bar on sparse codes; the count rule's free point beside a
                    # stratum, G5.7c step 3, writes one where none else can keep
                    # today's count of different values).
                    made_up = [held for held in with_counts if held not in real[column_name] and held not in bare_counts]
                    if made_up:
                        value["made_up"] = int(value["made_up"]) + len(made_up)  # type: ignore[call-overload]
                        named["made_up_named"] += [f"{name}@{seed}: {column_name} {len(made_up)} value(s), {sorted(made_up)[:4]}"]
                    if further:
                        value["edge_values_worse"] = int(value["edge_values_worse"]) + len(further)  # type: ignore[call-overload]
                        named["edge_values_worse_named"] += [f"{name}@{seed}: {column_name} {len(further)} of {len(edges_of[column_name])}"]
                    if worse > 0 or emptied:
                        value["shape_regressions"] = int(value["shape_regressions"]) + 1  # type: ignore[call-overload]
                        named["shape_regressions_named"] += [
                            f"{name}@{seed}: {column_name} Kolmogorov-Smirnov {worse:+d} rows, {len(emptied)} value(s) emptied"
                        ]
                for column_name, different in keys.items():
                    written = {cell for cell in generation.twin_column(twin, names_of.index(column_name)) if cell.strip()}
                    value["keys_checked"] = int(value["keys_checked"]) + 1  # type: ignore[call-overload]
                    if len(written) < different:
                        value["keys_lost"] = int(value["keys_lost"]) + different - len(written)  # type: ignore[call-overload]
                        today = {cell for cell in generation.twin_column(bare, names_of.index(column_name)) if cell.strip()}
                        named["keys_lost_named"] += [
                            f"{name}@{seed}: {column_name} {len(written)} different of {different} ({len(today)} without L0)"
                        ]
                with_path.unlink()
                bare_path.unlink()
            path.unlink(missing_ok=True)
    for key, listed in named.items():
        value[key] = listed
    value["made_without"] = sorted(set(made_without))
    value["reach"] = reach
    value["chain_refused"] = sorted(f"{name}: {why}" for name, why in REFUSED.items())
    value["seconds"] = round(time.time() - started, 1)
    return value


def _argument(flag: str, default: "list[int]") -> "list[int]":
    if flag in sys.argv:
        place = sys.argv.index(flag)
        return [int(item) for item in sys.argv[place + 1].split(",")]
    return default


def main() -> int:
    only = sys.argv[sys.argv.index("--zoo-only") + 1].split(",") if "--zoo-only" in sys.argv else []
    if "--only-tables" in sys.argv:
        only = sys.argv[sys.argv.index("--only-tables") + 1].split(",")
    value = measure(
        _argument("--rows", [5000, 20000]),
        _argument("--seeds", [0, 1, 2]),
        "--no-zoo" not in sys.argv,
        only,
        tuple(_argument("--draws", [7, 11])),
    )
    if "--kpi" in sys.argv:
        print("KPI " + json.dumps({"id": "K-S6-02", "value": value, "detail": "layer L0's band totals (lane BT)"}, sort_keys=True))
    else:
        print(json.dumps(value, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
