"""The chain's reader reads every cell as its description read it (lane BT3a, plan P4-D467; contract 4.6b.2).

THE GATE OF P4-D467. The command describes many columns from cells it
has changed -- the Safe Harbor age top-code, its placeholders past 125
set aside, a top category fewer than the floor's rows hold pooled below
the mark, a comma it inferred read as the decimal point -- and publishes
the counts of the changed cells. Read as the file wrote them, the
chain's recount of such a column disagreed and turned the WHOLE table's
chain off (OFF_RECOUNT), and the patient layer with it, on ordinary
count, padded-code and decimal-comma columns. `chain.described_cells`
and `chain.declarations_read` read each cell as the description read it.

Three tables, each through `cli.main` with the chain's switch and the
fixed test key, at the owner's table floor (the two other year tables,
the absent-spelling table and the cases of lane BT3a's repair 2 that
need tables of their own stand in
tests/test_stage6_chain_recount_settled.py, so each file keeps under
three minutes):

- an invented clinic table of 20,000 rows: a declared code of seven
  figures padded with noughts and topped at 120, a count with every
  whole number from 126 to 400 once beside its bulk (222 and 333 among
  them), a measurement written with a decimal comma nobody declared, a
  measurement the top-code reaches whose counts agree either way, a
  count whose top category of 7 rows at 90 or more is pooled, an amount
  whose values of five figures read as day counts the description holds
  (dates in disguise, plan P4-D446), and two ordinary controls (labels, and a measurement whose bulk lies past
  the age reach, a sixth of it from 90 to 125);
- an invented long table of 2,600 patients and 21,359 rows with up to
  400 visits a patient and the patient column declared (K-S6-08's
  heavy table, through the command) and five patient-fixed columns
  beside it (lane BT3a's repair 1: an amount of five figures on about 3
  in 100 patients, which the rows' description holds as dates in
  disguise; a score with 222 and 333 among its values; a reading
  written with a decimal comma nobody declared; its repair 2: two ages
  whose top category of one and of ten patients the rows' description
  pools below the mark): its rows, and its patient table, whose cells
  are each patient-fixed column's cells as the rows' description read
  them, read as that table's own description read it; and the same
  table with the switch off, whose questions and summary the switched
  run's must keep;
- an invented long table of 24,000 rows and 1,200 patients with a year
  of birth fixed by patient that the rows' description top-codes at
  1937 (batch 4p's sibling sweep), unanswered.

Clause (x)'s scan (tools/measurements/kpi_chain_recount.py) is checked
here too, machine-free: the one accepted case named apart, every
set-aside spelling checked, and each found wherever the private report
writes it, the report's JSON decoded and read word by word (LANE I4r
RULINGS 2 (1)), against a brute-force walk over generated reports.

Each is checked four ways: the chain is not off for a recount; every
eligible column's recount agrees; each starting total equals its
published count; and each column's rows a value as the chain reads them
equal those of the cells the description was built from, written here
from the rules' own words (no product function computes them). A
column the description did not change is read as the file wrote it, the
same cells. No value the rows' description top-coded or held stands in
a published block, position list or derived edge, or in any file the
command writes. Every fixture is invented here; the key is a fixed test
key.
"""

import contextlib
import io
import json
import os
import pathlib
import random
import re
import unicodedata

import pytest

import fixtures
import patient_enumeration

from synthtwin import asking, chain, cli, contract, patient_rules, reading, taxonomy
from synthtwin import chain_rules as rules

TEST_KEY = bytes(range(32))
ROWS = 20_000
COLUMNS = ["ward", "padded_code", "visit_count", "temp_c", "weight", "stay", "chol", "charge"]


def _installation(folder: pathlib.Path) -> pathlib.Path:
    """A data folder holding the fixed test key."""
    data = folder / "data"
    data.mkdir(mode=0o700)
    if os.name != "nt":
        data.chmod(0o700)
    key = data / "chain-key"
    key.touch(mode=0o600)
    if os.name != "nt":
        key.chmod(0o600)
    key.write_bytes(TEST_KEY)
    return data


def _clinic() -> "tuple[str, dict[str, list[str]]]":
    """The invented clinic table's text and its columns as written."""
    draw = random.Random(20261106)
    tail_rows = set(draw.sample(range(ROWS), 275))
    tail_values = list(range(126, 401))
    draw.shuffle(tail_values)
    pooled_rows = sorted(draw.sample(range(ROWS), 7))
    cells: "dict[str, list[str]]" = {name: [] for name in COLUMNS}
    lines = [",".join(COLUMNS)]
    for row in range(ROWS):
        written = [
            "ABCDE"[min(int(draw.expovariate(0.7)), 4)],
            f"{min(int(draw.expovariate(4.0 / 120)), 119):07d}",
            f"{tail_values.pop() if row in tail_rows else min(int(draw.expovariate(1.0 / 15)), 100)}",
            f"{draw.gauss(37.0, 0.5):.1f}".replace(".", ","),
            f"{draw.gauss(72.0, 12.0):.1f}",
            f"{92 + pooled_rows.index(row) if row in pooled_rows else min(int(draw.expovariate(1.0 / 8)), 60)}",
            f"{draw.uniform(80.0, 300.0):.1f}",
            f"{draw.uniform(10000.0, 30000.0) if draw.random() < 0.02 else draw.uniform(100.0, 9999.99):.2f}",
        ]
        for name, cell in zip(COLUMNS, written):
            cells[name] += [cell]
        lines += [",".join(f'"{cell}"' if "," in cell else cell for cell in written)]
    return "\n".join(lines) + "\n", cells


def _switched_run(folder: pathlib.Path, name: str, text: str, arguments: "list[str]", rows_per_person: str) -> "dict[str, object]":
    """One switched `synthtwin profile` run of ``text``, written as ``name``.csv in ``folder`` (`_switched_command`)."""
    table = fixtures.write(folder, f"{name}.csv", text)
    return _switched_command(folder, name, ["profile", str(table), "--out-dir", str(folder / "out")] + arguments, rows_per_person)


def _switched_command(folder: pathlib.Path, name: str, command: "list[str]", rows_per_person: str) -> "dict[str, object]":
    """``command``, a `synthtwin profile` command its caller built to write ``name``'s files into ``folder``/out, run
    with the chain's switch; what the chain's reader read, column by column, and what was written."""
    data = _installation(folder)
    out = folder / "out"
    out.mkdir()
    reads: "dict[str, list[object]]" = {}
    sized: "dict[tuple[int, str], list[object]]" = {}
    private: "list[str]" = []
    real = chain.read_column
    real_describe = chain.describe

    def recording(table_read, place, block, settings, declared, stored_as, blank_rows, cells=None, kept=None, spellings_kept=None):
        # Lanes RO's and CHs's two readings are handed on as given (batch 4r's merge: the reader hands
        # them to `read_column` beside the cells, LANE BT3 RULINGS 1 (3)).
        found = real(table_read, place, block, settings, declared, stored_as, blank_rows, cells, kept, spellings_kept)
        written = reading.column_values(table_read, place)
        reads[f"{block['name']}"] = [found, cells is None or cells == written, written if cells is None else cells, dict(declared), block]
        # The same by the table's rows too: the patient table (one row a patient) apart from the rows.
        sized[(table_read.n_rows, f"{block['name']}")] = reads[f"{block['name']}"]
        return found

    def describing(*given, **named):
        # The chain's private notes and moments, which no file holds, are read as the files are.
        nonlocal private
        chained = real_describe(*given, **named)
        private += [json.dumps({"notes": list(chained.notes), "moments": chained.moments}, sort_keys=True, default=str)]
        return chained

    chain.read_column = recording
    chain.describe = describing
    said = io.StringIO()
    try:
        with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
            code = cli.main(command, chain=cli.ChainRun(rows_per_person=rows_per_person, folder=str(data)))
    finally:
        chain.read_column = real
        chain.describe = real_describe
    document = json.loads((out / f"{name}-profile.json").read_text(encoding="utf-8"))
    written_files = {path.name: path.read_text(encoding="utf-8", errors="replace") for folder_read in (out, data) for path in sorted(folder_read.iterdir()) if path.is_file() and path.name != "chain-key"}
    written_files["(printed)"] = said.getvalue()
    written_files["(private notes)"] = "\n".join(private)
    return {"code": code, "reads": reads, "sized": sized, "document": document, "written": written_files, "out": out}


@pytest.fixture(scope="module")
def clinic(tmp_path_factory):
    folder = tmp_path_factory.mktemp("clinic")
    text, cells = _clinic()
    found = _switched_run(folder, "clinic", text, ["--code", "padded_code"], asking.ANSWER_ONE_ROW_EACH)
    found["cells"] = cells
    return found


def _long_with_fixed_columns() -> "tuple[list[str], list[list[str]], dict[str, dict[str, str]]]":
    """K-S6-08's heavy long table at up to 400 visits a patient and five patient-fixed columns beside it.

    `fee`: 100 to 900 in steps of 100, or 15000, 20000 or 25000 on about
    3 in 100 patients (amounts the rows' description reads as day counts
    and holds); `score`: 0 to 100 in steps of 5, or 222 or 333 on about 2
    in 100 (set aside by the age reach); `base_temp`: a reading of one
    place from 36,0 to 37,9 written with a decimal comma, each of its 20
    values held by many patients (lane BT3a's skeptic 1); `onset_age` and
    `entry_age`: ages from 20 to 85, the first with one patient at 97 and
    the second with ten patients at 91 to 100, a top category the rows'
    description pools below the mark, counted in patients (lane BT3a's
    repair 2, its verify's item 1).
    """
    held_at = patient_enumeration.VISITS_MAX
    patient_enumeration.VISITS_MAX = 400
    try:
        header, rows = patient_enumeration._long_rows(2600, 7, False)
    finally:
        patient_enumeration.VISITS_MAX = held_at
    draw = random.Random(99)
    ages = random.Random(98)
    fixed: "dict[str, dict[str, str]]" = {"fee": {}, "score": {}, "base_temp": {}, "onset_age": {}, "entry_age": {}}
    for row in rows:
        if row[0] not in fixed["fee"]:
            fixed["fee"][row[0]] = f"{draw.choice([15000, 20000, 25000]) if draw.random() < 0.03 else 100 * draw.randint(1, 9)}"
            fixed["score"][row[0]] = f"{draw.choice([222, 333]) if draw.random() < 0.02 else 5 * draw.randint(0, 20)}"
            fixed["base_temp"][row[0]] = f"{36.0 + 0.1 * draw.randrange(20):.1f}".replace(".", ",")
            seen = len(fixed["onset_age"])
            fixed["onset_age"][row[0]] = "97" if seen == 100 else f"{ages.randint(20, 85)}"
            fixed["entry_age"][row[0]] = f"{91 + (seen - 200) // 10}" if 200 <= seen < 300 and seen % 10 == 0 else f"{ages.randint(20, 85)}"
    return header + list(fixed), [row + [fixed[name][row[0]] for name in fixed] for row in rows], fixed


def _plain_run(folder: pathlib.Path, name: str, text: str, arguments: "list[str]") -> "dict[str, object]":
    """The same `synthtwin profile` run with the chain's switch off, as shipped: its questions file and its summary."""
    table = fixtures.write(folder, f"{name}.csv", text)
    out = folder / "out"
    out.mkdir()
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        code = cli.main(["profile", str(table), "--out-dir", str(out)] + arguments)
    return {
        "code": code,
        "questions": json.loads((out / f"{name}-questions.json").read_text(encoding="utf-8")),
        "summary": (out / f"{name}-profile.txt").read_text(encoding="utf-8"),
    }


@pytest.fixture(scope="module")
def visits(tmp_path_factory):
    folder = tmp_path_factory.mktemp("visits")
    header, rows, fixed = _long_with_fixed_columns()
    text = ",".join(header) + "\n" + "".join(",".join(f'"{cell}"' if "," in cell else cell for cell in row) + "\n" for row in rows)
    found = _switched_run(folder, "visits", text, ["--identifier", "pid"], "")
    found["rows"] = rows
    found["fixed"] = fixed
    found["plain"] = _plain_run(tmp_path_factory.mktemp("visits_plain"), "visits", text, ["--identifier", "pid"])
    return found


def _year_table(name: str) -> "tuple[str, list[str]]":
    """One of batch 4p's sibling-sweep tables: 24,000 rows, 1,200 patients of 20 visits, a year column, an arm and a reading.

    `year_fixed`: a year of birth fixed by patient, 1925 to 1960; the two
    others a year column that runs with the visit from 1925, or repeats
    across patients and visits from 1925 to 1960; each with one stray
    cell `19` on a patient's sixth row, the shape the rows' description
    top-codes at 1937. Its text and its declarations.
    """
    draw = random.Random(20261106)
    column = "birth_year" if name == "year_fixed" else "year"
    rows: "list[list[str]]" = []
    for patient in range(1200):
        for visit in range(20):
            year = {"year_fixed": 1925 + patient % 36, "year_run_aligned": 1925 + visit, "year_repeated": 1925 + (patient + visit) % 36}[name]
            rows += [[f"P{patient:05d}", "a" if patient % 2 == 0 else "b", f"{year}", f"{draw.gauss(100, 12):.1f}"]]
    rows[5][2] = "19"
    text = "\n".join([",".join(["pid", "arm", column, "value"])] + [",".join(row) for row in rows]) + "\n"
    return text, ["--identifier", "pid", "--measurement", column, "--measurement", "value"]


@pytest.fixture(scope="module")
def year_fixed(tmp_path_factory):
    text, arguments = _year_table("year_fixed")
    return _switched_run(tmp_path_factory.mktemp("year_fixed"), "year_fixed", text, arguments, "")


def _blocks(document: "dict[str, object]") -> "dict[str, dict[str, object]]":
    return {f"{block['name']}": block for block in document["columns"] if isinstance(block, dict)}


def _starting_totals(read: object, block: "dict[str, object]") -> "dict[object, int]":
    """Each starting band's rows over every row, by its published descriptor."""
    totals: "dict[object, int]" = {}
    start = getattr(read, "start")
    for code in getattr(read, "codes"):
        name = start.names[code]
        totals[name] = totals[name] + 1 if name in totals else 1
    return totals


def _number_readings(written: "list[str]", rule) -> "dict[float, int]":
    """Each value's rows, the cells read by ``rule`` (None: no value)."""
    out: "dict[float, int]" = {}
    for cell in written:
        value = rule(cell)
        if value is not None:
            out[value] = out[value] + 1 if value in out else 1
    return out


def _below_the_mark(written: "list[str]") -> float:
    return max(float(cell) for cell in written if float(cell) < 90)


# -- THE CLINIC TABLE: four causes, one check each way ---------------------


def test_the_clinic_table_keeps_its_chain(clinic):
    """The chain is not off for a recount; every eligible column of the seven was read and agrees."""
    assert clinic["code"] == 0
    statistical = clinic["document"]["relationships"]["statistical"]
    assert statistical is not None
    assert set(clinic["reads"]) == set(COLUMNS)
    for name, (read, _same, _cells, _declared, _block) in clinic["reads"].items():
        assert read is not None and read.agrees, name


def test_the_described_columns_carry_the_marks_this_gate_reads(clinic):
    """The description top-coded four columns, pooled one top category, inferred one comma; the controls carry no mark."""
    blocks = _blocks(clinic["document"])
    for name in ("padded_code", "visit_count", "weight", "stay"):
        assert blocks[name]["top_coded"] == 90, name
        assert blocks[name]["top_category_pooled"] == 11, name
    assert blocks["visit_count"]["n_missing"] == 2
    held = taxonomy.rendered(taxonomy.REMARK_DATED_VALUES_HELD, ())
    assert held in blocks["charge"]["remarks"]
    assert blocks["charge"]["n_missing"] == len([cell for cell in clinic["cells"]["charge"] if float(cell) >= 10000])
    assert clinic["document"]["settings"]["forced_decimal_commas"] == ["temp_c"]
    for name in ("ward", "chol", "temp_c", "charge"):
        assert "top_coded" not in blocks[name] and "top_coded_year" not in blocks[name], name


def test_each_starting_total_is_its_published_count(clinic):
    """Missing and value rows equal `n_missing` and `n_used_in_statistics`; each level's rows its published count."""
    blocks = _blocks(clinic["document"])
    for name, (read, _same, _cells, _declared, _block) in clinic["reads"].items():
        block = blocks[name]
        totals = _starting_totals(read, block)
        missing = totals[rules.MISSING] if rules.MISSING in totals else 0
        assert missing == block["n_missing"], name
        if block["role"] in rules.LABEL_ROLES:
            for label, count in rules.label_levels(block):
                assert (totals[(label,)] if (label,) in totals else 0) == count, (name, label)
        else:
            values = sum(totals[band] for band, is_value in zip(read.start.names, read.start.value) if is_value and band in totals)
            assert values == block["n_used_in_statistics"], name


def test_each_column_is_read_as_the_description_read_it(clinic):
    """Each number column's rows a value as the chain reads them, against the rules' words applied here.

    visit_count: 90 to 125 read 90, past 125 read 90 but the placeholder
    spellings 222 and 333 set aside; weight: 90 or more read 90; stay: its
    top category of 7 rows read as the largest value below 90; temp_c: the
    comma the decimal point; charge: its values of five figures held as
    day counts; chol (no mark): as written.
    """
    cells = clinic["cells"]
    reads = clinic["reads"]

    def visits(cell: str) -> "float | None":
        value = float(cell)
        if cell in ("222", "333"):
            return None
        return 90.0 if value >= 90 else value

    below = _below_the_mark(cells["stay"])
    expected = {
        "visit_count": _number_readings(cells["visit_count"], visits),
        "weight": _number_readings(cells["weight"], lambda cell: min(float(cell), 90.0)),
        "stay": _number_readings(cells["stay"], lambda cell: below if float(cell) >= 90 else float(cell)),
        "temp_c": _number_readings(cells["temp_c"], lambda cell: float(cell.replace(",", "."))),
        "chol": _number_readings(cells["chol"], float),
        "charge": _number_readings(cells["charge"], lambda cell: None if float(cell) >= 10000 else float(cell)),
    }
    for name, wanted in expected.items():
        assert dict(reads[name][0].readings) == wanted, name
    # The pooled seven read as the value below the mark, never as 90.
    assert 90.0 not in dict(reads["stay"][0].readings)


def test_a_column_the_description_did_not_change_is_read_as_written(clinic):
    """The controls and the comma column are handed the file's own cells, the same list (byte for byte as before)."""
    for name in ("ward", "chol", "temp_c"):
        assert clinic["reads"][name][1], name
    for name in ("padded_code", "visit_count", "weight", "stay", "charge"):
        assert not clinic["reads"][name][1], name
    assert clinic["reads"]["temp_c"][3]["decimal_comma"]
    assert not clinic["reads"]["chol"][3]["decimal_comma"]


def test_the_declared_code_is_read_at_its_published_levels(clinic):
    """Every cell of the declared code from 90 is read as the published `0000090`, none in the pool."""
    read, _same, described, _declared, _block = clinic["reads"]["padded_code"]
    written = clinic["cells"]["padded_code"]
    tops = [cell for cell in written if int(cell) >= 90]
    assert len(tops) > 10
    assert [one for one in described if int(one) >= 90] == ["0000090"] * len(tops)
    totals = _starting_totals(read, _blocks(clinic["document"])["padded_code"])
    assert totals[("0000090",)] == len(tops)
    assert (totals[rules.POOL] if rules.POOL in totals else 0) == 0


# -- THE LONG TABLE: the patient layer reads the cells the same way --------


def test_the_heavy_long_table_keeps_its_patient_layer(visits):
    """400 visits a patient: the visit number past 125 is reached as an age (222 and 333 set aside) and the layer stands."""
    rows = visits["rows"]
    assert len(rows) >= 20_000 and len({row[0] for row in rows}) >= 1_000
    written = [row[7] for row in rows]
    assert "222" in written and "333" in written
    assert visits["code"] == 0
    relationships = visits["document"]["relationships"]
    assert relationships["grain"] is not None
    assert relationships["statistical"] is not None
    # The row description's block the layer read (the layer publishes the column's block emptied).
    read, same, described, _declared, block = visits["reads"]["visit_no"]
    assert block["top_coded"] == 90
    assert read.agrees and not same
    assert all(value <= 90 for value, _rows in read.readings)
    assert sum(1 for cell in described if cell == "") == block["n_missing"]


def test_the_heavy_long_table_s_patient_table_is_read_as_its_own_description_read_it(visits):
    """The patient table holds each patient's fixed age as the rows' description read it, and is read so.

    Taken as the file wrote them, its cells held every age past 90 the
    description wrote as 90 (the counts agree either way, so no recount
    could tell): the patient layer's groups were drawn on values the
    description never published. Each patient's cell is now the rows'
    described one, 90 for every age of 90 or more, counted here from the
    rule's words.
    """
    rows = visits["rows"]
    assert max(int(row[3]) for row in rows) > 90
    first: "dict[str, str]" = {}
    for row in rows:
        first.setdefault(row[0], row[3])
    read, _same, described, _declared, block = visits["sized"][(len(first), "age")]
    assert block["top_coded"] == 90
    assert read.agrees
    wanted: "dict[str, int]" = {}
    for age in first.values():
        cell = "90" if int(age) >= 90 else age
        wanted[cell] = wanted[cell] + 1 if cell in wanted else 1
    found: "dict[str, int]" = {}
    for cell in described:
        found[cell] = found[cell] + 1 if cell in found else 1
    assert found == wanted
    assert all(value <= 90 for value, _rows in read.readings)
    assert any(value == 90 for value, _rows in read.readings)


def _figures(block: "dict[str, object]") -> "list[float]":
    """Every value a number block publishes (its ends, mean, mode, rungs, tails and empty edges), never a count."""
    found: "list[object]" = [block.get(key) for key in ("min", "max", "mean", "median", "mode")]
    for key in ("percentiles", "percentiles_between"):
        part = block.get(key)
        found += list(part.values()) if isinstance(part, dict) else []
    tails = block.get("tails")
    for side in tails.values() if isinstance(tails, dict) else []:
        if isinstance(side, dict) and isinstance(side.get("values"), list):
            found += list(side["values"])
    edges = block.get("empty_edges")
    for pair in edges if isinstance(edges, list) else []:
        found += list(pair) if isinstance(pair, list) else []
    return [float(one) for one in found if isinstance(one, (int, float)) and not isinstance(one, bool)]


# A held amount as a description, summary or note writes a value: its figures with no group mark, a point and noughts
# after them perhaps (`25000`, `25000.0`); counts are written with group marks (the questions file's `20,000 rows`).
HELD_FEES = re.compile(r"(?<![\d.,])(?:15|20|25)000(?:\.0+)?(?![\d])")
# The chain's procedure names its self-test's sample size, 20000 rows, a constant of the method and no value.
PROCEDURE_SAMPLE = '"selftest_sample": 20000'


def test_a_fixed_amount_held_as_dates_reaches_the_patient_table_blank(visits):
    """Lane BT3a's skeptic 1, item 1 (HIPAA, behind the switch): the patient table took the amounts as the file wrote them.

    The rows' description reads `fee`'s five-figure values as day counts
    and holds them (plan P4-D446). Taken as the file wrote them, the
    patient table's own description, told nothing of the hold, published
    them: `max` 25000, `p99` 20000, empty edges up to 20000, `n_missing`
    0, and the summary printed 25000 as the largest value. Each held
    patient now reaches the patient table blank: the published block
    counts them missing, keeps the rows' remark that the column's dates
    are held, and no written file names a held amount.
    """
    held = [pid for pid, cell in visits["fixed"]["fee"].items() if int(cell) >= 10_000]
    assert len(held) >= 11
    relationships = visits["document"]["relationships"]
    assert relationships["grain"] is not None
    classes = {entry["column"]: entry["class"] for entry in relationships["grain"]["classes"]}
    assert classes["fee"] == patient_rules.CLASS_FIXED
    block = _blocks(visits["document"])["fee"]
    assert block["n_missing"] == len(held)
    assert _figures(block) and not [one for one in _figures(block) if one >= 10_000]
    assert taxonomy.rendered(taxonomy.REMARK_DATED_VALUES_HELD, ()) in block["remarks"]
    for name, text in visits["written"].items():
        assert not HELD_FEES.findall(text.replace(PROCEDURE_SAMPLE, "")), name
    assert contract.load_profile(str(visits["out"] / "visits-profile.json"), chain=True) is not None


def test_the_patient_table_reads_a_comma_its_own_description_inferred(visits):
    """`base_temp`, fixed by patient and written `36,8`, is read under the comma the patient table's description inferred.

    Nobody declared the comma: the rows' description and the patient
    table's own each infer it and publish it in their settings. Read under
    the person's declarations alone, the patient table's recount of it
    disagreed and turned the patient layer off.
    """
    patients = len(visits["fixed"]["base_temp"])
    assert "base_temp" in visits["document"]["settings"]["forced_decimal_commas"]
    read, _same, _described, declared, block = visits["sized"][(patients, "base_temp")]
    assert declared["decimal_comma"] and read.agrees
    assert block["role"] in rules.NUMBER_ROLES and block["n_present"] == patients
    assert visits["document"]["relationships"]["grain"] is not None


def _safe_harbor_asked(questions: "dict[str, object]") -> "dict[str, list[str]]":
    """Each column the questions file puts the Safe Harbor question to, and the answers it offers."""
    out: "dict[str, list[str]]" = {}
    for entry in questions["asked"]:  # type: ignore[union-attr]
        if asking.safe_harbor_sentence(entry["column"]) in entry["what_synthtwin_saw"]:
            out[entry["column"]] = sorted(choice["answer"] for choice in entry["answers_you_can_give"])
    return out


def _summary_lines(summary: str, column: str) -> "list[str]":
    """The summary's lines about one column: its name's line and those under it."""
    found: "list[str]" = []
    inside = False
    for line in summary.split("\n"):
        if line.startswith("  ") and not line.startswith("   "):
            inside = line.strip() == column
            continue
        if inside:
            found += [line]
    return found


def test_a_patient_fixed_age_the_rows_pooled_keeps_its_safe_harbor_question(visits):
    """Lane BT3a's repair 2 (its verify's item 1): the patient table's cells are already pooled, so its own block
    carried no `top_coded`, and the switched questions file dropped the Safe Harbor question the run with the
    switch off puts to `onset_age` (one patient at 97) and `entry_age` (ten at 91 to 100), the summary its 'ages
    over 89' sentence. The published patient-fixed block keeps the rows' marks: the questions, and every column's
    sentence, are those of the run with the switch off; every published figure lies below the mark.
    MUTANT no_marks_carried: the marks left on the rows' block alone (red here)."""
    plain = visits["plain"]
    assert plain["code"] == 0 and visits["code"] == 0
    grain = visits["document"]["relationships"]["grain"]
    classes = {entry["column"]: entry["class"] for entry in grain["classes"]}
    blocks = _blocks(visits["document"])
    switched = json.loads(visits["written"]["visits-questions.json"])
    asked = _safe_harbor_asked(switched)
    for name in ("onset_age", "entry_age"):
        assert classes[name] == patient_rules.CLASS_FIXED, name
        assert name in asked, name
        sentence = [line for line in _summary_lines(visits["written"]["visits-profile.txt"], name) if "ages over 89" in line]
        assert sentence and sentence == [line for line in _summary_lines(plain["summary"], name) if "ages over 89" in line], name
        row_block = visits["sized"][(len(visits["rows"]), name)][4]
        assert row_block["top_coded"] == 90 and row_block["top_category_pooled"] == 11, name
        assert blocks[name]["top_coded"] == 90 and blocks[name]["top_category_pooled"] == 11, name
        assert blocks[name]["top_category_people"] == row_block["top_category_people"] == ["pid"], name
        assert _figures(blocks[name]) and max(_figures(blocks[name])) < 90, name
    assert asked == _safe_harbor_asked(plain["questions"])
    assert switched["asked"] == plain["questions"]["asked"]
    assert contract.load_profile(str(visits["out"] / "visits-profile.json"), chain=True) is not None


# -- THE YEAR OF BIRTH FIXED BY PATIENT: batch 4p's sibling sweep through the command --


def test_a_fixed_year_of_birth_reaches_the_patient_table_as_the_description_top_coded_it(year_fixed):
    # The sibling sweep of Codex's item 1 (HIPAA), at the table floor through the switched command: 24,000
    # rows, 1,200 patients of 20 visits, a year of birth fixed by patient from 1925 to 1960 (each year held
    # by 33 or more patients) and one stray cell `19` on a patient's sixth row, the shape the row description
    # top-codes at 1937. The patient table took each patient's first cell as the file wrote it, held no stray,
    # and its own description published years of 1925 and on in the column's block and a band of 102
    # patients below its p10 in the patient chain. Read as the row description read it, the patient table
    # holds 1937 for every earlier year: no published figure and no band of patients lies below the cut.
    # MUTANT raw_patient_table: the patient table's cells read as the file wrote them again (batch 4p's fix
    # round, 59ad9d3b; lane BT3a's repair 1, LANE BT3 RULINGS 4 (1)).
    run = year_fixed
    assert run["code"] == 0
    written = run["document"]
    grain = written["relationships"]["grain"]
    assert grain is not None and {entry["column"]: entry["class"] for entry in grain["classes"]}["birth_year"] == patient_rules.CLASS_FIXED
    block = _blocks(written)["birth_year"]
    assert block["n_present"] == 1200 and _figures(block)
    assert not [one for one in _figures(block) if one < 1937]
    rungs = {**(block.get("percentiles") or {}), **(block.get("percentiles_between") or {})}
    for entry in written["relationships"]["statistical"]["ladder"]:
        if entry["column"] != "birth_year":
            continue
        for band, total in zip(entry["l0"], entry["totals"]):
            if not all(isinstance(one, list) and len(one) == 2 for one in band):
                continue
            low, high = band[0][0], band[-1][1]
            assert not (low is None and high is not None and rungs[high] <= 1937 and total), (band, total)
    assert contract.load_profile(str(run["out"] / "year_fixed-profile.json"), chain=True) is not None


def test_a_fixed_year_of_birth_keeps_its_year_question_and_sentence(year_fixed):
    """Lane BT3a's repair 2 (its verify's item 1; P4-D467's limit (12)): year_fixed's switched questions file asks
    the year question the run with the switch off asks, and the patient-fixed block publishes the rows' year cut
    `top_coded_year`, so the summary says every year up to 1937 is read as 1937."""
    run = year_fixed
    asked = _safe_harbor_asked(json.loads(run["written"]["year_fixed-questions.json"]))
    assert "birth_year" in asked
    lines = _summary_lines(run["written"]["year_fixed-profile.txt"], "birth_year")
    assert [line for line in lines if "every year up to 1937 is read as 1937" in line]
    assert _blocks(run["document"])["birth_year"]["top_coded_year"] == 1937


# -- CLAUSE (x)'S SCAN: THE ACCEPTED CASE BY NAME, EVERY HELD SPELLING ------


def _clause_x():
    """tools/measurements/kpi_chain_recount.py loaded as a module (it runs nothing on import)."""
    import importlib.util
    import sys

    import kpi_rules

    held = list(sys.path)
    spec = importlib.util.spec_from_file_location("kpi_chain_recount_gate", kpi_rules.MEASUREMENTS / "kpi_chain_recount.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path[:] = held
    return module


def _chained(position_values: "list[str]") -> "dict[str, object]":
    """A chained description of one invented column `amount`, its patient layer listing ``position_values``."""
    return {
        "columns": [{"name": "amount", "role": "continuous", "min": 100.0, "max": 900.0}],
        "relationships": {
            "statistical": {"chain": [{"table": [[40, 60], [55, 45]]}], "moments": None},
            "grain": {"rows": [], "census": {"bands": []}, "positions": [{"column": "amount", "values": position_values}], "derived": []},
        },
    }


def test_clause_x_counts_every_hit_but_the_one_accepted_by_name():
    """Codex's item 3 (LANE BT3 RULINGS 6 (3)): `scan_hits` at most 1 let any single hit pass. The accepted case (the
    vitals export's weight read past 125 as no age) is named apart and K-S6-02 bounds every other hit at 0: the weight
    case alone meets the bound; exchanged for a private note quoting one held spelling (Codex's construction, the
    scan's own hit), the check fails, and a reading of that weight from the mark to 125 is no accepted case.
    MUTANT accepted_by_table: every hit of the vitals export accepted (red here)."""
    import kpi_rules

    driver = _clause_x()
    entry = kpi_rules.entries_by_id(kpi_rules.load_ledger())["K-S6-02"]
    bound = {"rule_kind": "at_most", "expected": {"scan_hits": entry["expected"]["scan_hits"]}, "status": "GREEN"}
    assert bound["expected"]["scan_hits"] == 0
    weight = driver._reading_hit("weight", ((80.0, 900), (90.0, 400), (125.1, 2), (129.9, 1)), 90)
    accepted, counted = driver._counted("zoo:vitals", weight)
    assert accepted == ["zoo:vitals: a reading of weight past 125, kept as no age"] and counted == []
    assert kpi_rules.judge(bound, {"scan_hits": len(counted)}).word == kpi_rules.PASS
    note = driver._scan(_chained([]), '{"notes": ["the census quoted 50000 for amount"]}', {"amount": frozenset({"50000"})}, 11, {})
    assert note == ["the set-aside spelling 50000 of amount in a note or the chain"]
    accepted, counted = driver._counted("zoo:vitals", note)
    assert accepted == [] and len(counted) == 1
    assert kpi_rules.judge(bound, {"scan_hits": len(counted)}).word == kpi_rules.FAIL
    below = driver._reading_hit("weight", ((80.0, 900), (90.0, 400), (95.5, 3)), 90)
    assert driver._counted("zoo:vitals", below) == ([], ["zoo:vitals: a reading of weight above its mark"])


def test_clause_x_checks_every_spelling_set_aside():
    """Codex's item 4 (LANE BT3 RULINGS 6 (4)): the scan kept the first 20 set-aside spellings of a column, so the
    twenty-first, 10021, escaped a position list holding it. Every one is kept for the check.
    MUTANT first_twenty: the set cut to its first 20 spellings (red here)."""
    driver = _clause_x()
    written = [f"{10001 + at}" for at in range(21)] + ["500", "700"]
    aside = {"amount": driver._set_aside(written, [""] * 21 + ["500", "700"])}
    assert len(aside["amount"]) == 21
    hits = driver._scan(_chained(["500", "10021"]), "{}", aside, 11, {})
    assert hits == ["a set-aside spelling in a position list of amount"]


# -- CLAUSE (x)'S SCAN READS THE PRIVATE REPORT DECODED, WORD BY WORD -------


def _report(notes: "list[str]", moments: object = None) -> str:
    """A private report as the driver writes one: the notes and the moments, keys sorted, objects it cannot write as
    JSON written as text."""
    return json.dumps({"notes": list(notes), "moments": moments}, sort_keys=True, default=str)


HELD_HIT = ["the set-aside spelling 50000 of amount in a note or the chain"]


@pytest.mark.parametrize(
    "private, spellings, expected",
    [
        pytest.param(_report(["50000"]), ["50000"], HELD_HIT, id="whole_note"),
        pytest.param(_report(["value 50000"]), ["50000"], HELD_HIT, id="end_of_note"),
        pytest.param(_report(["the value 50000.", "kept 120"]), ["50000"], HELD_HIT, id="period"),
        pytest.param(_report(["held 50000, kept 120"]), ["50000"], HELD_HIT, id="comma"),
        pytest.param(_report(["held 50000; kept 120"]), ["50000"], HELD_HIT, id="semicolon"),
        pytest.param(_report(["held (120 and 50000) kept"]), ["50000"], HELD_HIT, id="closing_bracket"),
        pytest.param(_report(['held "50000" kept']), ["50000"], HELD_HIT, id="closing_double_quote"),
        pytest.param(_report(["held '50000' kept"]), ["50000"], HELD_HIT, id="closing_single_quote"),
        pytest.param(_report(["held:\t50000\nkept: 120"]), ["50000"], HELD_HIT, id="tab_and_line_break"),
        pytest.param(_report([], {"sums": [{"labels": ["kept 120", ["held 50000"]]}]}), ["50000"], HELD_HIT, id="nested_lists_and_objects"),
        pytest.param(_report(["température 50000°"]), ["50000"], HELD_HIT, id="non_ascii_text"),
        pytest.param(_report(["valor não informado"]), ["não"], ["the set-aside spelling não of amount in a note or the chain"], id="non_ascii_spelling"),
        pytest.param(_report(["value 50000", "again «50000»."]), ["50000"], HELD_HIT, id="the_same_value_twice"),
        pytest.param(_report(["500001 150000 50000.5 x50000 50000kg 50000_1"]), ["50000"], [], id="prefix_or_suffix_of_a_longer_word"),
        pytest.param(_report(["the result was not done."]), ["not done"], ["the set-aside spelling not done of amount in a note or the chain"], id="two_words"),
        pytest.param(_report(["held -1.", "x-1 -10 1-"]), ["-1"], ["the set-aside spelling -1 of amount in a note or the chain"], id="its_own_punctuation"),
        pytest.param(_report([], {"50000": [1, 2]}), ["50000"], HELD_HIT, id="a_key"),
        pytest.param('{"notes": ["value 50000"], "notes": []}', ["50000"], HELD_HIT, id="a_key_written_twice"),
        pytest.param(_report([], {"n": 50000, "mean": 50000.0}), ["50000"], [], id="a_number"),
        pytest.param("held value 50000.", ["50000"], HELD_HIT, id="not_json"),
    ],
)
def test_clause_x_finds_a_set_aside_spelling_wherever_the_private_report_writes_it(private, spellings, expected):
    """Codex's one item on batch 4r (LANE I4r RULINGS 2 (1)): the scan split the SERIALIZED report on spaces, so a
    closing quotation mark stayed on a note's last word and a set-aside spelling there, after punctuation, beside an
    escaped tab or line break, or written in letters JSON escapes was no hit (`value 50000` returned []). The report's
    JSON is decoded and every key and string read word by word, each word's ends shed of punctuation and quotation
    marks: a spelling counts once however often it stands, never inside a longer word (`500001`, `50000.5`), a JSON
    number is no spelling, and a report that is no JSON is read as one text. Red on the start head 820d55c3 (the split
    scan) but for the cases `prefix_or_suffix_of_a_longer_word` and `a_number`, which are red on their MUTANTS
    substring (a spelling found anywhere in a text) and numbers_read (a number leaf read as its text); MUTANTS
    once_an_occurrence (`the_same_value_twice`), keys_skipped (`a_key`), last_key_kept (`a_key_written_twice`),
    not_json_skipped (`not_json`), no_shedding (the punctuation and quotation cases), split_on_spaces
    (`tab_and_line_break`): red here."""
    driver = _clause_x()
    assert driver._scan(_chained([]), private, {"amount": frozenset(spellings)}, 11, {}) == expected


def _words(text: str) -> "list[str]":
    """``text``'s words, walked character by character: the runs holding no whitespace."""
    words: "list[str]" = []
    word = ""
    for one in text:
        if one.isspace():
            words += [word] if word else []
            word = ""
        else:
            word += one
    return words + ([word] if word else [])


def _shed(one: str) -> bool:
    """Whether a word's end sheds ``one``: no letter, figure or combining mark."""
    return not unicodedata.category(one).startswith(("L", "N", "M"))


def _texts_walked(found: object) -> "list[str]":
    """Every key and string of a decoded report, depth first; an object arrives as ("object", its pairs)."""
    if isinstance(found, str):
        return [found]
    if isinstance(found, tuple):
        out: "list[str]" = []
        for key, value in found[1]:
            out += [key] + _texts_walked(value)
        return out
    if isinstance(found, list):
        out = []
        for value in found:
            out += _texts_walked(value)
        return out
    return []


def _stands(spelling: str, private: str) -> bool:
    """THE BRUTE FORCE: whether ``spelling``'s words stand in turn in one text of the report, the first word ending a
    word whose front sheds, the last starting a word whose back sheds, any words between equal."""
    try:
        texts = _texts_walked(json.loads(private, object_pairs_hook=lambda pairs: ("object", pairs)))
    except ValueError:
        texts = [private]
    words = _words(spelling)
    for text in texts if words else []:
        tokens = _words(text)
        for first in range(len(tokens) - len(words) + 1):
            window = tokens[first:first + len(words)]
            if len(words) == 1:
                token, word = window[0], words[0]
                if any(token.startswith(word, at) and all(_shed(one) for one in token[:at] + token[at + len(word):]) for at in range(len(token) - len(word) + 1)):
                    return True
            elif (window[0].endswith(words[0]) and all(_shed(one) for one in window[0][:len(window[0]) - len(words[0])])
                  and window[1:-1] == words[1:-1]
                  and window[-1].startswith(words[-1]) and all(_shed(one) for one in window[-1][len(words[-1]):])):
                return True
    return False


SWEEP_SPELLINGS = ("50000", "-1", "999", "N/A", "36,8", "12.5", "não", "unknown", "not done", "?", "1937", "2021-03-04",
                   "<5", "(none)", "x", "0", "-999", "99.0", "n/a", "无", "a b c")
SWEEP_WORDS = ("value", "held", "kept", "500001", "150000", "50000.5", "x50000", "50000kg", "1", "a", "é", "-", "--", "»",
               "2021", "03", "none", "done", "not", "N", "A", "36", "8", "12", "5", "b", "c", "<", "(", "?!")
SWEEP_FRONTS = ("", "", "", '"', "'", "(", "[", "{", "«", "“", "`", "​", "¿", "-", "x", "1", "é", "_", "$", "+", "é")
SWEEP_BACKS = ("", "", "", '"', "'", ")", "]", "}", "»", "”", "`", ".", ",", ";", ":", "!", "?", "%", "°", "​", "x", "1",
               "é", "-", "_", ".5", "́", "\\")
SWEEP_GAPS = (" ", " ", " ", "  ", "\t", "\n", "\r\n", " ", " ", " \t ")


def _generated(count: int, seed: int) -> "list[tuple[str, tuple[str, ...]]]":
    """``count`` invented private reports and the spellings set aside beside each: notes of words drawn from spellings
    and other words, each with a front and a back that shed or do not, at every place in a note, joined by every kind
    of whitespace, nested in lists and objects or written as keys, escaped or not, a key written twice, or no JSON."""
    draw = random.Random(seed)
    out: "list[tuple[str, tuple[str, ...]]]" = []
    for _case in range(count):
        held = tuple(draw.sample(SWEEP_SPELLINGS, draw.randint(1, 4)))
        notes: "list[str]" = []
        for _note in range(draw.randint(1, 4)):
            note = draw.choice(("", "", " ", "\n"))
            for _word in range(draw.randint(0, 6)):
                word = draw.choice(held + SWEEP_SPELLINGS) if draw.random() < 0.45 else draw.choice(SWEEP_WORDS)
                note += draw.choice(SWEEP_FRONTS) + draw.choice(SWEEP_GAPS).join(word.split()) + draw.choice(SWEEP_BACKS) + draw.choice(SWEEP_GAPS)
            notes += [note[:-1] if note and draw.random() < 0.5 else note]
        shape = draw.randrange(6)
        if shape == 0:
            private = json.dumps({"notes": notes, "moments": None}, sort_keys=True, ensure_ascii=draw.random() < 0.5)
        elif shape == 1:
            moments = {"sums": [{"labels": notes[1:], "n": draw.randint(0, 60000), "mean": draw.random()}], notes[0]: [notes[0]]}
            private = json.dumps({"notes": notes[:1], "moments": moments}, sort_keys=True, ensure_ascii=draw.random() < 0.5)
        elif shape == 2:
            private = json.dumps({"notes": [notes], "moments": {"a": {"b": [[notes[-1]], {"c": notes[0]}]}}}, ensure_ascii=False)
        elif shape == 3:
            private = '{"notes": ' + json.dumps(notes) + ', "notes": []}'
        elif shape == 4:
            private = json.dumps({"notes": notes, "moments": {"sizes": {draw.choice(SWEEP_WORDS): draw.randint(0, 99)}, "set": {"kept"}}}, default=str)
        else:
            private = draw.choice(("", " ", "\n")).join(notes)
        out += [(private, held)]
    return out


def test_clause_x_scan_matches_a_brute_force_walk_on_generated_reports():
    """THE CLASS (LANE I4r RULINGS 2 (1)): over 6,000 generated private reports (a spelling at a note's start, middle
    or end, alone, before or after punctuation, quotation marks, brackets, symbols and invisible characters, or inside
    a longer word; joined by spaces, tabs, line breaks and other whitespace; in nested lists and objects, as a key, a
    key written twice, escaped or written as is, or no JSON at all), the scan names exactly the spellings the brute
    force `_stands` finds, column by column; the sweep finds both kinds by the thousand. Red on the start head 820d55c3
    (2,699 of the 2,716 spellings that stand missed) and on MUTANTS substring, no_shedding, split_on_spaces,
    once_an_occurrence, keys_skipped, last_key_kept and not_json_skipped."""
    driver = _clause_x()
    standing = missing = 0
    for private, held in _generated(6000, 20261109):
        aside = {f"c{at}": frozenset({spelling}) for at, spelling in enumerate(held)}
        found = sorted(hit.rsplit(" of ", 1)[1][: -len(" in a note or the chain")] for hit in driver._scan(_chained([]), private, aside, 11, {}))
        expected = sorted(name for name, spellings in aside.items() if _stands(next(iter(spellings)), private))
        assert found == expected, (private, held)
        standing += len(expected)
        missing += len(aside) - len(expected)
    assert standing > 2000 and missing > 2000, (standing, missing)


def test_clause_x_hands_the_chain_every_argument_the_command_gives():
    """Batch 4r's merge put lane CHs's kept readings (plan P4-D462) ninth among the arguments the command hands
    `chain.describe`, beside clause (x)'s wrapper of it, which took eight: the driver's first table stopped with a
    TypeError, so K-S6-02's clause (x) could not run on the merged head. The wrapper takes the arguments as given and
    reads them by `chain.describe`'s own names. Red on the start head 820d55c3."""
    import ast
    import inspect

    driver = _clause_x()
    [wrapper] = [node for node in ast.walk(ast.parse(inspect.getsource(driver.run_table))) if isinstance(node, ast.FunctionDef) and node.name == "describing"]
    taken = {one.arg for one in wrapper.args.posonlyargs + wrapper.args.args + wrapper.args.kwonlyargs}
    assert (wrapper.args.vararg is not None and wrapper.args.kwarg is not None) or set(inspect.signature(chain.describe).parameters) <= taken


# -- ONCE A SPELLING: the same cells as every row read in turn -------------


def test_the_cells_read_once_a_spelling_are_the_cells_read_with_the_column_s_own_absent_spellings(clinic, tmp_path):
    """`described_cells` with the plain absent spellings (the default) and with the column's own (`exact`) agree cell for cell."""
    table = fixtures.write(tmp_path, "clinic.csv", _clinic()[0])
    read = reading.read_table(str(table), small_cell_floor=11)
    settings = taxonomy.Settings(small_cell_floor=11)
    blocks = _blocks(clinic["document"])
    for place, name in enumerate(COLUMNS):
        declared = clinic["reads"][name][3]
        quick = chain.described_cells(read, place, blocks[name], settings, declared, "")
        exact = chain.described_cells(read, place, blocks[name], settings, declared, "", True)
        assert quick == exact, name
        assert quick == clinic["reads"][name][2], name


def test_a_top_category_is_counted_in_rows_not_in_spellings(tmp_path):
    """Twenty rows of one spelling past the mark are a top category of twenty, written 90 and never pooled; seven rows
    of seven spellings are pooled below the mark, as `taxonomy.top_category_pooled` reads every row."""
    lines = ["many,few"]
    for row in range(400):
        lines += [f"{'95' if row < 20 else row % 61},{92 + row if row < 7 else row % 61}"]
    read = reading.read_table(str(fixtures.write(tmp_path, "tops.csv", "\n".join(lines) + "\n")), small_cell_floor=11)
    settings = taxonomy.Settings(small_cell_floor=11)
    declared = {"code": False, "measurement": False, "decimal_comma": False}
    for place, name in enumerate(("many", "few")):
        block = {"name": name, "role": "count", "top_coded": 90, "top_category_pooled": 11, "top_category_people": []}
        quick = chain.described_cells(read, place, block, settings, declared, "")
        assert quick == chain.described_cells(read, place, block, settings, declared, "", True), name
        written = reading.column_values(read, place)
        moved = {one: two for one, two in zip(written, quick) if one != two}
        assert moved == ({"95": "90"} if name == "many" else {f"{92 + row}": "60" for row in range(7)}), name
