"""The chain's reader reads a column under what its description was told and settled (lane BT3a's repair 2, plan P4-D467).

THE SECOND GATE FILE OF P4-D467 (the first, tests/test_stage6_chain_recount.py,
holds the clinic, long and year-of-birth tables and the helpers read here
as `gate`; this one
is apart to keep each file under three minutes), each table through `cli.main`
with the chain's switch and the fixed test key, at the owner's table floor
(each `synthtwin profile` command built here, `_profiled`, and run through
the first file's recorders):

- two invented long tables of 24,000 rows and 1,200 patients with a
  year column the rows' description top-codes at 1937 (batch 4p's
  sibling sweep: a year that runs with the visit, a year repeated
  across patients), unanswered;
- an invented table of 20,000 rows whose two counts the age top-code
  reaches each hold a spelling the column's own reading counts absent
  and the plain absent spellings do not (a declared missing number
  written `99.0`, the stand-in `-999`);

and two cases of Codex's review of the lane (LANE BT3 RULINGS 6 (1) and (2)):

- the comma the rows settled: 1,200 patients of 20 visits, a measurement fixed
  by patient written `12,34` with one `56,7` among its rows; the rows'
  description infers the comma, each patient's first cell alone does not, and
  the patient table, described under the person's commas alone, published the
  column categorical. It is described and read under the settled comma;
- the unit an age was answered in: 20,000 rows of an `age` counted in days,
  none of it 90 years or more, beside 100 cells of 50000 the description holds
  as dates in disguise; answered `days`, its block carries no mark, and the
  reader, handed no unit, read it in years and blanked 19,900 cells, turning the
  chain off. It is handed the answered unit.

and one case of batch 4r's merge of the lane beside lane RO's rule steps (LANE
BT3 RULINGS 1 (3)): the 20,000-row table of the two counts with the rule steps
on, whose column read twice hands the steps the cells of its second reading.

Every fixture is invented here; the key is a fixed test key.
"""

import fractions
import json
import pathlib
import random

import pytest

import fixtures
import test_stage6_chain_recount as gate

from synthtwin import asking, contract, patient_rules, taxonomy
from synthtwin import chain_rules as rules


def _profiled(folder: pathlib.Path, name: str, text: str, options: "list[str]", rows_per_person: str) -> "dict[str, object]":
    """``text`` written as ``name``.csv in ``folder`` and described by a switched `synthtwin profile` command built
    here, run through the first gate file's recorders (`gate._switched_command`): every description this module reads
    or loads was written by a command it built itself."""
    table = fixtures.write(folder, f"{name}.csv", text)
    return gate._switched_command(folder, name, ["profile", str(table), "--out-dir", str(folder / "out")] + options, rows_per_person)


YEAR_TABLES = ("year_run_aligned", "year_repeated")


@pytest.fixture(scope="module")
def years(tmp_path_factory):
    found: "dict[str, dict[str, object]]" = {}
    for name in YEAR_TABLES:
        text, arguments = gate._year_table(name)
        found[name] = _profiled(tmp_path_factory.mktemp(name), name, text, arguments, "")
    return found


SENTINEL_COLUMNS = ["ward", "refills", "units"]


def _sentinels() -> "tuple[str, dict[str, list[str]]]":
    """An invented table of 20,000 rows: a label control, and two counts from 0 to 100 that the age top-code reaches.

    Run with `--missing-value 99`: `refills` writes that declared missing
    number `99.0` on about 3 rows in 400 (its own reading counts it
    absent by its number; the plain absent spellings, compared as
    written, do not); `units` writes the stand-in `-999` on about 3 rows
    in 200 (its own reading counts it absent as a stand-in number, an
    outlier of its rows).
    """
    draw = random.Random(20261107)
    cells: "dict[str, list[str]]" = {name: [] for name in SENTINEL_COLUMNS}
    lines = [",".join(SENTINEL_COLUMNS)]
    for _row in range(gate.ROWS):
        written = [
            "ABCDE"[min(int(draw.expovariate(0.7)), 4)],
            "99.0" if draw.random() < 0.0075 else f"{min(int(draw.expovariate(1.0 / 15)), 100)}",
            "-999" if draw.random() < 0.015 else f"{min(int(draw.expovariate(1.0 / 15)), 100)}",
        ]
        for name, cell in zip(SENTINEL_COLUMNS, written):
            cells[name] += [cell]
        lines += [",".join(written)]
    return "\n".join(lines) + "\n", cells


@pytest.fixture(scope="module")
def sentinels(tmp_path_factory):
    text, cells = _sentinels()
    found = _profiled(tmp_path_factory.mktemp("sentinels"), "sentinels", text, ["--missing-value", "99"], asking.ANSWER_ONE_ROW_EACH)
    found["cells"] = cells
    return found


# -- THE YEAR TOP-CODE: batch 4p's sibling sweep through the command --------


def _below_the_cut(values: "list[object]", cut: int) -> "list[object]":
    """The entries of a published list (decimal texts) or of readings (numbers) that read as a year below ``cut``."""
    out: "list[object]" = []
    for one in values:
        found = patient_rules.fraction_read(one) if isinstance(one, str) else None
        if isinstance(one, (int, float)) and not isinstance(one, bool):
            found = fractions.Fraction(one)
        if found is not None and 1800 <= found < cut:
            out += [one]
    return out


@pytest.mark.parametrize("name", ["year_run_aligned", "year_repeated"])
def test_a_year_the_rows_top_coded_stands_in_no_position_list_or_derived_edge_below_the_cut(years, name):
    """A year column of the rows top-coded at 1937 (`top_coded_year`): the patient layer reads it so (LANE BT3 RULINGS 4 (2)).

    Read with the year step skipped, the year that runs with the visit
    was published as a position list 1925 to 1936 and the repeated year
    as an own-mean edge of 1936.1 (the batch's sibling sweep): years the
    description pooled as 1937 or earlier.
    """
    run = years[name]
    assert run["code"] == 0
    written = run["document"]
    cut = gate._blocks(written)["year"].get("top_coded_year")
    read = run["reads"]["year"]
    assert read[4]["top_coded_year"] == 1937 and read[0].agrees
    assert cut in (None, 1937)
    grain = written["relationships"]["grain"]
    assert grain is not None
    for entry in grain["positions"]:
        if entry["column"] == "year":
            assert not _below_the_cut(entry["values"], 1937), entry
    for entry in grain["derived"]:
        if entry["source"] == "year":
            assert not _below_the_cut(entry["edges"], 1937), entry
    assert not _below_the_cut(gate._figures(gate._blocks(written)["year"]), 1937)
    assert not _below_the_cut([value for value, _rows in read[0].readings], 1937)


# -- A SPELLING THE COLUMN'S OWN READING COUNTS ABSENT ---------------------


def test_a_column_read_with_its_own_absent_spellings_keeps_the_chain(sentinels):
    """Two counts the top-code reaches, each with a spelling its own reading counts absent and the plain spellings do not.

    `refills`: the declared missing number 99 written `99.0`, read as
    absent by its number; read with the plain absent spellings it is a
    value from 90 written 90, so the first recount disagrees and the
    column is read again with its own (the read made again, LANE BT3
    RULINGS 5 (2)). `units`: the stand-in `-999`, which the age reach
    would set aside; its own reading counts it absent first, and the
    description keeps an absent cell's spelling, so the chain's cells
    keep it (the exact reading after a cell is written blank).
    """
    assert sentinels["code"] == 0
    assert sentinels["document"]["relationships"]["statistical"] is not None
    blocks = gate._blocks(sentinels["document"])
    cells = sentinels["cells"]
    for name in ("refills", "units"):
        assert blocks[name]["top_coded"] == 90, name
        read, _same, described, _declared, _block = sentinels["reads"][name]
        assert read.agrees, name
        kept = {"refills": "99.0", "units": "-999"}[name]
        assert [two for one, two in zip(cells[name], described) if one == kept] == [kept] * cells[name].count(kept), name
    assert blocks["refills"]["n_missing"] == len([cell for cell in cells["refills"] if float(cell) == 99])
    assert blocks["units"]["n_missing"] == len([cell for cell in cells["units"] if cell == "-999" or float(cell) == 99])
    expected = {
        "refills": gate._number_readings(cells["refills"], lambda cell: None if float(cell) == 99 else min(float(cell), 90.0)),
        "units": gate._number_readings(cells["units"], lambda cell: None if cell == "-999" or float(cell) == 99 else min(float(cell), 90.0)),
    }
    for name, wanted in expected.items():
        assert dict(sentinels["reads"][name][0].readings) == wanted, name


def test_the_rule_steps_gather_the_cells_of_the_reading_that_stands(tmp_path, monkeypatch):
    """BATCH 4r'S MERGE OF LANE BT3a (LANE BT3 RULINGS 1 (3)): the rule steps read a column after the transforms.

    The table above through the command with lane RO's rule steps on
    (plan P4-D459): `refills` is read twice by `chain.read_as_described`,
    first with the plain absent spellings (its declared missing number
    written `99.0` then reads as a value from 90 and is written 90), then
    with its own (`99.0` absent, kept as written), and the cells the rule
    steps gather for it are the second reading's, the one the chain stands
    on: every `99.0` of the file stands in them, no 90 in its place. Red
    where the reader keeps both readings in the steps' list, whose first
    they take (the merge's mutant: `del kept[:]` dropped).
    """
    from synthtwin import chain_order, cli

    text, cells = _sentinels()
    table = fixtures.write(tmp_path, "sentinels.csv", text)
    data = gate._installation(tmp_path)
    (tmp_path / "out").mkdir()
    gathered: "dict[str, list[str]]" = {}
    real = chain_order.gather

    def watching(store, name, block, texts, spelled, declared, tabled_rows):  # type: ignore[no-untyped-def]
        gathered[name] = list(texts)
        return real(store, name, block, texts, spelled, declared, tabled_rows)

    monkeypatch.setattr(chain_order, "gather", watching)
    command = ["profile", str(table), "--out-dir", str(tmp_path / "out"), "--missing-value", "99"]
    code = cli.main(command, chain=cli.ChainRun(rows_per_person=asking.ANSWER_ONE_ROW_EACH, folder=str(data), rules=True))
    assert code == 0
    written = cells["refills"].count("99.0")
    assert written > 0
    assert len(gathered["refills"]) == len(cells["refills"])
    assert gathered["refills"].count("99.0") == written
    assert [two for one, two in zip(cells["refills"], gathered["refills"]) if one == "99.0"] == ["99.0"] * written


# -- A MEASUREMENT THE PATIENT TABLE READS UNDER THE COMMA THE ROWS SETTLED ---


def _settled_comma_table() -> str:
    """Codex's case (LANE BT3 RULINGS 6 (1)): 1,200 patients of 20 visits; `measure`, fixed by patient, written
    `12,34` to `31,53` (patient p writes `{12 + p % 20},{34 + p % 20}`), one cell `56,7` on the sixth row; an arm and a
    reading beside it. The rows settle the comma; each patient's first cell alone does not."""
    draw = random.Random(20261108)
    lines = ["pid,arm,measure,value"]
    for patient in range(1200):
        for visit in range(20):
            row = patient * 20 + visit
            measure = "56,7" if row == 5 else f"{12 + patient % 20},{34 + patient % 20}"
            lines += [f'P{patient:05d},{"a" if patient % 2 == 0 else "b"},"{measure}",{draw.gauss(100, 12):.1f}']
    return "\n".join(lines) + "\n"


@pytest.fixture(scope="module")
def settled(tmp_path_factory):
    text = _settled_comma_table()
    return _profiled(tmp_path_factory.mktemp("settled"), "settled", text, ["--identifier", "pid", "--measurement", "measure"], "")


def test_the_patient_table_reads_a_measurement_under_the_comma_the_rows_settled(settled):
    """Codex's item 1 (LANE BT3 RULINGS 6 (1)): the row description inferred `measure`'s comma and published it a
    measurement; the patient table, told only the person's commas, published it categorical (no moments, no
    ranges). The settled comma is carried into the patient table's description and its rereading: the published
    patient-fixed block is a measurement whose figures lie within the column's values, read under the comma, its
    recount agreeing. MUTANTS pt_person_commas (the patient table described and read under the person's commas
    alone) and description_person_commas (described so, read under the settled comma): red here."""
    assert settled["code"] == 0
    document = settled["document"]
    assert "measure" in document["settings"]["forced_decimal_commas"]
    assert settled["sized"][(24_000, "measure")][4]["role"] in rules.NUMBER_ROLES
    grain = document["relationships"]["grain"]
    assert grain is not None
    assert {entry["column"]: entry["class"] for entry in grain["classes"]}["measure"] == patient_rules.CLASS_FIXED
    block = gate._blocks(document)["measure"]
    assert block["role"] in rules.NUMBER_ROLES and block["n_present"] == 1200
    figures = gate._figures(block)
    assert figures and all(12.34 <= one <= 31.53 for one in figures)
    read, _same, _cells, declared, pt_block = settled["sized"][(1200, "measure")]
    assert declared["decimal_comma"] and read.agrees and pt_block["role"] in rules.NUMBER_ROLES
    assert contract.load_profile(str(settled["out"] / "settled-profile.json"), chain=True) is not None


# -- AN AGE COLUMN ANSWERED IN DAYS, NO VALUE OF IT TOP-CODED ----------------


def _days_table() -> str:
    """Codex's case (LANE BT3 RULINGS 6 (2)): 20,000 rows; `age` 10000 to 19900 in steps of 100 on 19,800 rows, `100` on
    100 and `50000` on 100; a ward and a dose beside it."""
    draw = random.Random(20261109)
    lines = ["ward,age,dose"]
    for row in range(gate.ROWS):
        age = "100" if row % 200 == 7 else "50000" if row % 200 == 107 else f"{10000 + (row % 100) * 100}"
        lines += [f'{"ABCDE"[min(int(draw.expovariate(0.7)), 4)]},{age},{draw.uniform(1.0, 50.0):.1f}']
    return "\n".join(lines) + "\n"


@pytest.fixture(scope="module")
def days(tmp_path_factory):
    """The days table profiled in rounds, as a person answers its questions file: `age`, held at first as record
    numbers (five-figure values), is answered `keep`; its Safe Harbor question then offers the units and is answered
    `days`; the last round is the one read."""
    text = _days_table()
    arguments: "list[str]" = []
    for round_number in range(4):
        folder = tmp_path_factory.mktemp(f"days{round_number}")
        found = _profiled(folder, "days", text, arguments, asking.ANSWER_ONE_ROW_EACH)
        questions = json.loads(found["written"]["days-questions.json"])
        given = ""
        for entry in questions["asked"]:
            offered = [choice["answer"] for choice in entry["answers_you_can_give"]]
            if entry["column"] == "age" and not given:
                given = "days" if "days" in offered else asking.ANSWER_KEEP if asking.ANSWER_KEEP in offered else ""
                entry["your_answer"] = given
        if not given:
            found["rounds"] = round_number + 1
            return found
        answers = folder / "answers.json"
        answers.write_text(json.dumps(questions), encoding="utf-8", newline="\n")
        arguments = ["--answers", str(answers)]
    raise AssertionError("the days table's questions were not settled in four rounds")


def test_an_age_answered_in_days_is_read_in_days_with_no_mark(days):
    """Codex's item 2 (LANE BT3 RULINGS 6 (2)): answered `days`, the description holds only the 100 values 50000 as
    dates in disguise (past 125 years in days), publishing 19,900 present and 100 missing, the dated remark and no
    `top_coded`. The reader, handed no unit, read the column in years and blanked 19,900 cells, and the chain was off
    for a recount. Handed the answered unit, it reads the profiler's census, and the chain stands.
    MUTANTS unit_unread (the answered unit not read where the block carries no mark) and command_hands_none (the
    command hands the chain no answered unit): red here."""
    assert days["code"] == 0
    block = gate._blocks(days["document"])["age"]
    assert "top_coded" not in block and taxonomy.rendered(taxonomy.REMARK_DATED_VALUES_HELD, ()) in block["remarks"]
    assert (block["n_present"], block["n_missing"]) == (19_900, 100)
    read, _same, cells, _declared, _block = days["reads"]["age"]
    assert read.agrees
    assert sum(rows for _value, rows in read.readings) == 19_900
    assert cells.count("") == 100 and "50000" not in cells
    assert days["document"]["relationships"]["statistical"] is not None
