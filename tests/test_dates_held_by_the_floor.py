"""P4-D433 (lane PS2): every published date held by the floor, in people or else in rows.

THE DEFECT (lane E0c's leak scan, `kpi_run.py --slow --only 'K-HZ-*'` on
93d57414). Lane PS (plan P4-D417) pools a column of dates beside a person
column whose people have several rows; a table of ONE ROW A PERSON, or of
NO PERSON COLUMN, published day-grain dates that one to ten people or rows
hold: the zoo's `patients.csv` printed 11 real birth dates (`dob_iso`'s
date percentiles p05 to p95 and both tail boundaries, each one person's
date) at 20,000 rows, and lane E0c's `phi_registry.csv` 40 (`birth_date`,
which no question flags). A full birth date is a HIPAA identifier element.

THE RULE. Where no subject column beside a column of dates counts it in
people, each ROW is its own holder: every date the description publishes
-- a percentile, a tail boundary or value, a mode, a heavy date, a census
entry -- is read as the calendar day it names (its month or quarter where
it names only that), and one that one to ten rows fall on sends the column
down lane PS's ladder (day, month, quarter, year), each row a holder, or
holds it with valid made-up dates in its own layouts where no grain serves
(`profile._dates_few_in_rows`, `profile.rows_as_holders`). On a table of
one row a person a row IS a person. A column whose every published day the
floor's rows already hold keeps its bytes -- the dense admission day stays
at the day, a stamp to the minute keeps its time of day -- and a column a
subject column counts in people is counted as lane PS counts it.

THE GATE, at 20,000 rows (the owner's table floor; the same tables at
200,000 rows are K-HZ-07's slow leg, `tools/measurements/kpi_dates_held.py`,
by the orchestrator's ruling 2 on the build), every table through the zoo's
own path (profile, the general answers, profile --answers): the sweep's
birth dates over seventy years, death dates, sparse event dates and dense
admission days on one row a person, several rows a person and no person
column, and lane E0c's two exposures; 0 real dates of one to ten people or
rows published (`dates_held.dates_held_few`, written apart from the
product's count), the dense columns' bytes pinned to the base's
(ccebc947), the twins valid in their own layouts. Red on the mutants of
`wave6/PS2/mut_ps2.py` (`mutants.log`).

REPAIR ROUND 1 (the lane's skeptic 1 and Codex's review): the user's raised
floor (`even_days_20`), a declared count of Excel days (`excel_births`),
stamps published on the shared clock (`utc_offsets`, `utc_shifted`),
declared Unix seconds at 13:00 and milliseconds a millisecond before
midnight (`unix_afternoons`, `unix_millis`), month-first dates under
`--day-first` (`month_first`), no question put on a column the count in
rows held, an older description still met by its unchanged source, and
the evidence that never denies repeated people.
"""

from __future__ import annotations

import contextlib
import datetime
import io
import json
import pathlib
import types

import pytest

from synthtwin import cli, contract, grains, parsing, profile, taxonomy, validation

import dates_held
import unanswered_identifier_shapes as shapes

# The floor size alone in the suite; 200,000 rows run in K-HZ-07's slow leg.
SIZES = (20000,)
# Named apart, so `-k at20k` never selects another size too.
SIZE_IDS = ("at20k",)


@pytest.fixture(scope="module")
def described(tmp_path_factory: pytest.TempPathFactory):
    """Each shape at each size through the zoo's path, once: its table's path and folder."""
    made: "dict[tuple[str, int], tuple[pathlib.Path, pathlib.Path]]" = {}

    def get(shape: str, rows: int) -> "tuple[pathlib.Path, pathlib.Path]":
        if (shape, rows) not in made:
            folder = tmp_path_factory.mktemp(f"{shape}-{rows}")
            options, _floor = dates_held.options_of(shape)
            made[(shape, rows)] = (dates_held.answered(dates_held.SWEEP[shape], folder, rows, options), folder)
        return made[(shape, rows)]

    return get


# -- (A): no date one to ten people or rows hold is published -------------


@pytest.mark.parametrize("rows", SIZES, ids=SIZE_IDS)
@pytest.mark.parametrize("shape", sorted(dates_held.SWEEP))
def test_no_date_one_to_ten_people_or_rows_hold_is_published(described, shape: str, rows: int) -> None:
    source, folder = described(shape, rows)
    found = dates_held.dates_held_few(source, folder, dates_held.options_of(shape)[1])
    assert found["dated"], f"{shape}: no column read as dates"
    assert found["few"] == 0, found["named"][:20]
    assert found["printed"] == [], found["printed"][:20]


# Lane E0c's two exposures, each column by name: counted in rows (one row a
# person, no person column that repeats), and every date it publishes held.
EXPOSED = (
    ("demographics", ("dob_iso", "dob_us", "dob_text")),
    ("phi_registry", ("birth_date",)),
)


@pytest.mark.parametrize("rows", SIZES, ids=SIZE_IDS)
@pytest.mark.parametrize(("shape", "columns"), EXPOSED)
def test_lane_e0c_exposures_are_counted_in_rows_and_held(described, shape: str, columns: "tuple[str, ...]",
                                                         rows: int) -> None:
    source, folder = described(shape, rows)
    found = dates_held.dates_held_few(source, folder)
    assert found["counted_in"] == "rows"
    for column in columns:
        assert column in found["dated"]
        block = dates_held.block_of(folder, dates_held.SWEEP[shape].name, column)
        grain = block.get("time_grain")
        # Pooled at a grain coarser than the day, or held: never the day.
        assert isinstance(grain, dict) and grain["rung"] in ("year", "quarter", "month", "held"), (column, grain)


# -- a column whose day grain the floor holds keeps its bytes --------------

@pytest.mark.parametrize("rows", SIZES, ids=SIZE_IDS)
@pytest.mark.parametrize(("shape", "column"), [(shape, column) for shape in sorted(dates_held.DENSE)
                                                for column in dates_held.DENSE[shape]])
def test_a_date_column_the_floor_holds_at_the_day_keeps_its_bytes(described, shape: str, column: str,
                                                                  rows: int) -> None:
    source, folder = described(shape, rows)
    block = dates_held.block_of(folder, dates_held.SWEEP[shape].name, column)
    assert "time_grain" not in block, block.get("time_grain")
    assert dates_held.dense_digest(folder, shape, column) == dates_held.DENSE_DIGESTS[(shape, column, rows)]


def test_a_stamp_whose_days_the_floor_holds_keeps_its_time_of_day(described) -> None:
    """The dense stamp to the minute, no person column, at 20,000 rows: its hours still published."""
    source, folder = described("dense_only", 20000)
    block = dates_held.block_of(folder, "dense_only", "arrived_at")
    assert block["role"] == "datetime"
    percentiles = block["date_percentiles"]
    assert isinstance(percentiles, dict)
    assert any(isinstance(point, str) and not point.endswith("00:00:00") for point in percentiles.values())


# -- the twin ---------------------------------------------------------------


@pytest.mark.parametrize("shape", sorted(dates_held.SWEEP))
def test_the_twin_writes_valid_dates_and_meets_its_description(described, shape: str) -> None:
    source, folder = described(shape, 20000)
    name = dates_held.SWEEP[shape].name
    quiet = io.StringIO()
    with contextlib.redirect_stdout(quiet), contextlib.redirect_stderr(quiet):
        made = cli.main(["generate", f"{folder / (name + '-profile.json')}", "--out-dir", f"{folder}",
                         "--seed", "0", "--replace"])
    assert made == 0, quiet.getvalue()[-2000:]
    found = dates_held.dates_held_few(source, folder)
    loaded = contract.load_profile(f"{folder / (name + '-profile.json')}")
    twin = folder / f"{name}-twin.csv"
    names, columns = dates_held.persons_counted.table_columns(twin)
    for column in found["dated"]:  # type: ignore[union-attr]
        # Each cell read in ITS column's own source layouts, and no other
        # (skeptic 1, item 8): ISO in a column written 03/17/2024 is out.
        layouts = dates_held.LAYOUTS[(shape, column)]
        for cell in columns[names.index(column)]:
            if cell:
                assert dates_held.in_its_layouts(cell, layouts), (column, cell, layouts)
    outcome = validation.measure(loaded, f"{twin}")
    missed = {f"{check.column}.{check.subcheck}" for check in outcome.checks if check.verdict == validation.MISSED
              and f"{check.column}" in found["dated"]}  # type: ignore[operator]
    assert missed <= TWIN_LIMITS.get(shape, set()), sorted(missed)
    # ...and the real table meets its own description, every date column
    # (the count by occurrences aside, lane PS's own residual, as the
    # registry case below reads it).
    real = validation.measure(loaded, f"{source}")
    assert not [f"{check.column}.{check.subcheck}" for check in real.checks
                if check.verdict == validation.MISSED and f"{check.column}" in found["dated"]  # type: ignore[operator]
                and "occurrences" not in f"{check.subcheck}"]


# A NAMED LIMIT, NOT THIS LANE'S (P4-D417's stamps with UTC offsets, lane
# DST): a stamp published on the shared clock and pooled at a rung is drawn
# inside its local bucket, so its twin misses two points and the weekday
# census read on that clock, while the real table meets every one. Measured
# at 20,000 rows, seed 0 (wave6/PS2/repair1/diag-utc.log); pinned so it
# cannot grow unseen.
TWIN_LIMITS: "dict[str, set[str]]" = {
    "utc_offsets": {"arrived_at.date-ladder.p75", "arrived_at.date-ladder.p99", "arrived_at.weekday_census.groups"},
}


def test_a_cell_in_another_layout_than_its_columns_own_is_out() -> None:
    """The twin's check reads each cell in its column's own layouts only (skeptic 1, item 8)."""
    assert dates_held.in_its_layouts("03/17/2024", ("%m/%d/%Y",))
    assert not dates_held.in_its_layouts("2024-03-17", ("%m/%d/%Y",))
    assert not dates_held.in_its_layouts("17-Mar-2024", ("%Y-%m-%d",))
    assert dates_held.in_its_layouts("45000", ("count:excel-1900",))
    assert not dates_held.in_its_layouts("2023-03-15", ("count:excel-1900",))


# -- a day-first date written at a grain keeps its order --------------------


def test_a_day_first_date_written_at_a_grain_reads_day_first_and_its_twin_is_made(tmp_path: pathlib.Path) -> None:
    """The zoo's `registry_extract` at 20,000 rows: day-first dates pooled at the month.

    Every bucket starts on the first (`01/03/2022`), which reads either way;
    read with the tie given to the month the block published
    `month-first-date` beside a record reading `day-first-date`, and
    `generate` refused the description (exit 1, the whole export lost).
    """
    table = [one for one in dates_held.health_zoo.TABLES if one.name == "registry_extract"][0]
    source = dates_held.answered(table, tmp_path, 20000)
    described = json.loads((tmp_path / "registry_extract-profile.json").read_text(encoding="utf-8"))
    grained = 0
    for block in described["columns"]:
        grain = block.get("time_grain")
        if isinstance(grain, dict) and grain["rung"] != "held":
            grained += 1
            assert block["format"] == grain["reading"], (block["name"], block["format"], grain["reading"])
    assert grained >= 2
    quiet = io.StringIO()
    with contextlib.redirect_stdout(quiet), contextlib.redirect_stderr(quiet):
        made = cli.main(["generate", f"{tmp_path / 'registry_extract-profile.json'}", "--out-dir", f"{tmp_path}",
                         "--seed", "0", "--replace"])
    assert made == 0, quiet.getvalue()[-1500:]
    loaded = contract.load_profile(f"{tmp_path / 'registry_extract-profile.json'}")
    for path in (tmp_path / "registry_extract-twin.csv", source):
        outcome = validation.measure(loaded, f"{path}")
        assert not [check for check in outcome.checks if check.verdict == validation.MISSED
                    and "occurrences" not in f"{check.subcheck}"], path.name


# -- in people first --------------------------------------------------------


def test_birth_dates_beside_ten_patients_stay_held_in_people(tmp_path: pathlib.Path) -> None:
    """Lane HX2's `dob_ten` at 20,000 rows: ten patients' birth dates, each on 2,000 rows.

    The patient key holds fewer than the floor's people, so no subject column
    counts in people and the rows are counted too -- but the key, attached to
    the column and telling its people apart, still holds it (P4-D406): each
    date falls on far more than ten rows, and counted in rows alone all ten
    would be published.
    """
    seen = shapes.run(tmp_path, "dob_ten", 20000)
    assert seen["profile_exit"] == 0 and seen["validate_exit"] == 0, seen
    assert seen["description_values"] == 0 and seen["twin_cells"] == 0, seen
    assert seen["evidence"] == taxonomy.rendered(taxonomy.EVIDENCE_HELD_IN_PEOPLE, ())


# -- the words: rows, not people ---------------------------------------------


def test_the_description_and_its_summary_say_rows_where_rows_are_counted(described) -> None:
    """NF130 and NF131 where each row is its own holder; NF128 where a person column counts in people."""
    source, folder = described("no_person", 20000)
    held = dates_held.block_of(folder, "no_person", "event_date")
    pooled = dates_held.block_of(folder, "no_person", "birth_date")
    assert held["role"] == "identifier"
    assert held["detection_evidence"] == taxonomy.rendered(taxonomy.EVIDENCE_HELD_IN_ROWS, ())
    assert pooled["detection_evidence"] == taxonomy.rendered(taxonomy.EVIDENCE_POOLED_IN_ROWS, ())
    summary = (folder / "no_person-profile.txt").read_text(encoding="utf-8")
    assert "because too few rows hold its dates" in summary
    # ...and the screen says rows too, never "several rows a person".
    again = folder / "again"
    again.mkdir()
    screen = io.StringIO()
    with shapes.nobody_at_the_keyboard():
        with contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
            assert cli.main(["profile", f"{source}", "--out-dir", f"{again}", "--replace"],
                            small_tables_refused=True) == 0
    said = screen.getvalue()
    assert "DATES HELD BY FEWER THAN 11 ROWS" in said and "event_date" in said, said[-1500:]
    assert "VALUES HELD BY FEWER THAN" not in said
    assert "each row is counted as its own, and some date" in summary
    _source, people = described("several_rows", 20000)
    beside = dates_held.block_of(people, "several_rows", "birth_date")
    assert beside["detection_evidence"] == taxonomy.rendered(taxonomy.EVIDENCE_POOLED_IN_PEOPLE, ())


# -- below the floor: refused by the command --------------------------------


def test_below_the_table_floor_the_command_refuses_the_table_writing_nothing(tmp_path: pathlib.Path) -> None:
    """The count in rows reaches every table the command describes; one row fewer is refused (plan P4-D425).

    The library keeps its bytes below `parsing.TABLE_ROW_FLOOR` rows, where
    the suite's small fixtures test what each date column does; the
    command never publishes a description there.
    """
    table = dates_held.SWEEP["one_row"]
    source = dates_held.health_zoo.write_table(table, tmp_path, parsing.TABLE_ROW_FLOOR - 1, dates_held.SEED)
    screen = io.StringIO()
    with contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
        # explicitly, as tests/test_table_floor.py does: the suite's conftest
        # switches the floor off for every other call
        code = cli.main(["profile", f"{source}", "--out-dir", f"{tmp_path}", "--replace"], small_tables_refused=True)
    assert code != 0
    assert "below its floor" in screen.getvalue()
    assert not (tmp_path / "one_row-profile.json").exists()


# -- the product's own parts -----------------------------------------------


def test_the_parts_a_published_date_names() -> None:
    assert profile._date_parts("2023-01-05 18:07:00") == ("2023-01-05", "2023-01", "2023-q1")
    assert profile._date_parts("2023-11") == ("2023-11", "2023-q4")
    assert profile._date_parts("2023-q3") == ("2023-q3",)
    for word in ("2023", "18:07:00", "2023-13-01", "abcd-01-01", ""):
        assert profile._date_parts(word) == ()


@pytest.mark.parametrize(("published", "rows", "few"), [
    ("2023-01-05", 10, True), ("2023-01-05", 11, False),
    ("2023-01-05 18:07:00", 10, True), ("2023-01", 10, True), ("2023-01", 11, False),
    ("2023-q1", 10, True), ("2023-q1", 11, False),
])
def test_a_published_date_on_ten_rows_is_few_and_on_eleven_is_not(
    monkeypatch: pytest.MonkeyPatch, published: str, rows: int, few: bool
) -> None:
    """The count in rows at the floor: a published day, month or quarter one to ten rows fall on, and no more."""
    monkeypatch.setattr(profile, "_column_block", lambda column: {"format": "iso-date"})
    monkeypatch.setattr(profile, "_published_in", lambda block, rungs: profile._Published(
        frozenset({published}), frozenset(), (), "iso-date"))
    column = types.SimpleNamespace(absent_spellings=())
    cells = ["2023-01-05"] * rows + ["2023-06-01"] * 50 + [""] * 5
    assert profile._dates_few_in_rows(column, cells, 11) is few  # type: ignore[arg-type]


def test_a_rung_publishing_another_member_than_its_record_reads_does_not_serve() -> None:
    """TG1 as the loader holds it, asked before a rung is kept; and the day-first order read."""
    day_first = grains.Reading(grains.DATE, "day-first-date")
    assert not profile._reads_its_member(types.SimpleNamespace(details={"format": "month-first-date"}), day_first)  # type: ignore[arg-type]
    assert profile._reads_its_member(types.SimpleNamespace(details={"format": "day-first-date"}), day_first)  # type: ignore[arg-type]
    assert profile._reads_its_member(types.SimpleNamespace(details={}), day_first)  # type: ignore[arg-type]
    assert profile._reads_its_member(types.SimpleNamespace(details={"format": "x"}), grains.Reading(grains.CLOCK, "hh:mm"))  # type: ignore[arg-type]
    for member, first in (("day-first-date", True), ("dotted-day-first-date", True), ("month-first-date", False),
                          ("iso-date", False), ("layout {DD}/{MM}/{YY1900}", True), ("layout {MM}/{DD}/{YY1900}", False),
                          ("layout {DD}-{MON}-{YY}", False)):
        assert profile._day_before_month(member) is first, member


def test_rows_as_holders_tells_every_row_apart() -> None:
    holders = profile.rows_as_holders(1000)
    assert len(holders) == 1000 and len(set(holders)) == 1000


# -- repair round 1 -----------------------------------------------------------


def test_no_question_is_put_on_a_column_the_count_in_rows_held(described) -> None:
    """Skeptic 1, item 3: the sparse event with no person column is held in rows and asked nothing.

    Q6 (`asking.BECAUSE_MOSTLY_DATES`) once asked it whether it holds
    dates, though no answer could publish one, and said its blank cells
    were "written another way".
    """
    source, folder = described("no_person", 20000)
    held = dates_held.block_of(folder, "no_person", "event_date")
    assert held["detection_evidence"] == taxonomy.rendered(taxonomy.EVIDENCE_HELD_IN_ROWS, ())
    asked = folder / "no_person-questions.json"
    document = json.loads(asked.read_text(encoding="utf-8")) if asked.exists() else {}
    named = [entry.get("column") for entry in document.get("asked", []) if isinstance(entry, dict)]
    assert "event_date" not in named, named


def test_the_raised_floor_holds_every_published_date(described) -> None:
    """Skeptic 1, item 4: days on 18 or 19 rows keep the day at 11 and are pooled under `--smallest-group 20`."""
    source, folder = described("even_days_20", 20000)
    found = dates_held.dates_held_few(source, folder, 20)
    assert found["few"] == 0 and found["printed"] == [], found
    block = dates_held.block_of(folder, "even_days", "admit_date")
    grain = block.get("time_grain")
    assert isinstance(grain, dict) and grain["rung"] in ("month", "quarter", "year", "held"), grain
    _source, eleven = described("even_days", 20000)
    assert "time_grain" not in dates_held.block_of(eleven, "even_days", "admit_date")


@pytest.mark.parametrize("shape", ["excel_births", "unix_afternoons", "unix_millis", "utc_offsets"])
def test_dates_read_by_their_own_clock_and_count_are_held(described, shape: str) -> None:
    """Skeptic 1, item 5 and Codex's items 1 and 2: each date counted on the day it truly names.

    Excel days declared; Unix seconds at 13:00, whose day's own rendering
    rounds to the next day; milliseconds a millisecond before midnight;
    stamps published on the shared clock, one a day there. Each published
    a real date on one row before; each column is now pooled or held.
    """
    source, folder = described(shape, 20000)
    found = dates_held.dates_held_few(source, folder)
    assert found["counted_in"] == "rows" and found["dated"], found
    assert found["few"] == 0 and found["printed"] == [], found
    for column in found["dated"]:  # type: ignore[union-attr]
        grain = dates_held.block_of(folder, dates_held.SWEEP[shape].name, f"{column}").get("time_grain")
        assert isinstance(grain, dict) and grain["rung"] != "day", (column, grain)


def test_the_true_day_of_a_count_is_never_rounded_forward() -> None:
    """Codex's item 2, the product's own part: the instant floored to its midnight."""
    seconds = profile._CellReading("seconds-since-1970")
    assert profile._counted_true_day(f"{946684800 + 13 * 3600}", seconds) == "2000-01-01"
    millis = profile._CellReading("milliseconds-since-1970")
    assert profile._counted_true_day(f"{946684800000 + 86399999}", millis) == "2000-01-01"
    assert profile._counted_true_day("45000.75", profile._CellReading("excel-1900")) == "2023-03-15"
    assert profile._counted_true_day("x", seconds) == ""


def test_a_month_first_column_under_day_first_is_described_at_its_grain(described) -> None:
    """Codex's item 4: days above twelve settled the column month-first; `--day-first` must not hold it.

    At the month every bucket is `MM/01/YYYY`, which reads either way; read
    day first it published another member than its record, every rung was
    refused and the column was held as record numbers.
    """
    source, folder = described("month_first", 20000)
    block = dates_held.block_of(folder, "month_first", "seen_on")
    grain = block.get("time_grain")
    assert block["role"] == "datetime", block["role"]
    assert isinstance(grain, dict) and grain["rung"] not in ("held", "day"), grain
    assert block["format"] == grain["reading"] == "month-first-date", (block.get("format"), grain)


def test_an_older_description_is_met_by_its_unchanged_source(tmp_path: pathlib.Path,
                                                             monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's item 3: validation reads the grain a description published, its absence included.

    20,000 consecutive days from 1950, written by a description made before
    the count in rows (the count switched off), published every day; the
    validator once pooled the unchanged source and missed eleven checks.
    """
    first = datetime.date(1950, 1, 1)
    lines = [[(first + datetime.timedelta(days=index)).isoformat(), "BA"[index % 2]] for index in range(20000)]
    source = tmp_path / "days.csv"
    source.write_bytes(dates_held.health_zoo.csv_bytes(["seen_on", "group"], lines))
    with monkeypatch.context() as patched:
        patched.setattr(profile, "_dates_few_in_rows", lambda *arguments, **keywords: False)
        quiet = io.StringIO()
        with shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(quiet), contextlib.redirect_stderr(quiet):
            assert cli.main(["profile", f"{source}", "--out-dir", f"{tmp_path}", "--replace"],
                            small_tables_refused=True) == 0, quiet.getvalue()[-1500:]
    described = json.loads((tmp_path / "days-profile.json").read_text(encoding="utf-8"))
    assert "time_grain" not in [block for block in described["columns"] if block["name"] == "seen_on"][0]
    loaded = contract.load_profile(f"{tmp_path / 'days-profile.json'}")
    outcome = validation.measure(loaded, f"{source}")
    missed = [f"{check.column}.{check.subcheck}" for check in outcome.checks if check.verdict == validation.MISSED]
    assert missed == [], missed


def test_the_evidence_never_denies_repeated_people(tmp_path: pathlib.Path) -> None:
    """Codex's item 6: 1,000 declared patients on 20 rows each, `--smallest-group 2000`, event dates that vary.

    The person column repeats but names fewer people than the raised
    floor; its dates are counted in those people (repair round 2, the
    combined verify's item 1), so no bucket reaches the floor and the
    column is held in people; the sentences never say that no column names
    a person on several rows.
    """
    draw = __import__("random").Random(dates_held.SEED)
    lines = [[f"P{1000000 + index % 1000:07d}",
              (datetime.date(1990, 1, 1) + datetime.timedelta(days=draw.randrange(10950))).isoformat(),
              f"{draw.uniform(40, 140):.1f}"] for index in range(20000)]
    source = tmp_path / "visits.csv"
    source.write_bytes(dates_held.health_zoo.csv_bytes(["patient_id", "event_date", "weight"], lines))
    quiet = io.StringIO()
    with shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(quiet), contextlib.redirect_stderr(quiet):
        assert cli.main(["profile", f"{source}", "--out-dir", f"{tmp_path}", "--replace", "--identifier",
                         "patient_id", "--smallest-group", "2000"], small_tables_refused=True) == 0
    said = quiet.getvalue()
    described = json.loads((tmp_path / "visits-profile.json").read_text(encoding="utf-8"))
    block = [one for one in described["columns"] if one["name"] == "event_date"][0]
    evidence = f"{block['detection_evidence']}"
    assert evidence == taxonomy.rendered(taxonomy.EVIDENCE_HELD_IN_PEOPLE, ()), evidence
    for text in (evidence, said, (tmp_path / "visits-profile.txt").read_text(encoding="utf-8")):
        assert "names a person on several rows, so" not in text
        assert "No column of this table names a person" not in text


# -- repair round 2: the combined verify's items 1 and 2 -------------------

# The sha256 of `few_visit_days`' visit_date block at the owner's floor on
# the base, ccebc947, through the same path (wave6/PS2/repair2/base-digest.log).
FEW_VISIT_DAYS_AT_11 = "7355021785b9916289b50d383ed38898bfd4ad3eec1087d41ff005c8eeb130c0"


def test_a_raised_floor_above_the_tables_people_still_counts_its_dates_in_people(described) -> None:
    """The combined verify's item 1: 1,000 patients, one of them on 2,500 rows all on one day, `--smallest-group 2000`.

    Counted in rows, those 2,500 rows passed the raised floor and the one
    patient's day was published as the low tail, beside points 929 to 940
    people hold. Counted in its people, whatever their number, no date
    reaches 2,000 people and the column is held; at the owner's 11 its
    block is the base's, byte for byte.
    """
    source, folder = described("few_visit_days_2000", 20000)
    found = dates_held.dates_held_few(source, folder, 2000)
    assert found["counted_in"] == "people" and found["dated"] == ["visit_date"], found
    assert found["few"] == 0 and found["printed"] == [], found
    block = dates_held.block_of(folder, "few_visit_days", "visit_date")
    assert "2023-06-15" not in json.dumps(block), block
    assert block["detection_evidence"] == taxonomy.rendered(taxonomy.EVIDENCE_HELD_IN_PEOPLE, ()), block
    _source, eleven = described("few_visit_days", 20000)
    digest = dates_held.hashlib.sha256(
        json.dumps(dates_held.block_of(eleven, "few_visit_days", "visit_date"), sort_keys=True).encode("utf-8")
    ).hexdigest()
    assert digest == FEW_VISIT_DAYS_AT_11


def test_dates_on_the_shared_clock_are_counted_in_people_there(described) -> None:
    """The combined verify's item 2: births at local midnight at +14:00 and -10:00, ten rows a person.

    Every local day holds 12 people; on the shared clock, where the block
    publishes the column, each day holds 6. Counted under its local text,
    every point and both tails printed a moment 6 people hold.
    """
    source, folder = described("utc_split", 20000)
    found = dates_held.dates_held_few(source, folder)
    assert found["counted_in"] == "people" and found["dated"] == ["born_at"], found
    assert found["few"] == 0 and found["printed"] == [], found
    block = dates_held.block_of(folder, "utc_split", "born_at")
    grain = block.get("time_grain")
    assert block.get("datetimes_read_at") == "utc" or isinstance(grain, dict), block
    assert isinstance(grain, dict) and grain["rung"] != "day", grain


def test_the_walk_counts_each_bucket_and_offset_apart() -> None:
    """The walk on the shared clock: one bucket written at two offsets is two published texts, each its own people."""
    cells = [f"1950-01-0{1 + 2 * (person // 12)}T00:00:00{'+14:00' if person % 12 < 6 else '-10:00'}"
             for person in range(24)]
    people = [f"P{person}" for person in range(24)]
    reading = grains.Reading(grains.STAMP, "iso-datetime")
    local = profile._grain_walk(cells, 24, reading, [people], [True], 11)
    shared = profile._grain_walk(cells, 24, reading, [people], [True], 11, frozenset(), True)
    assert local.thin.get(grains.DAY) is False and local.grain.rung != grains.HELD, (local.thin, local.grain)
    assert shared.thin.get(grains.DAY) is True, shared.thin


def test_a_cell_is_counted_in_people_under_the_instant_the_block_prints() -> None:
    """The count in people on the shared clock: `+14:00` local midnight is counted as the UTC instant printed."""
    printed = profile._Published(frozenset({"1950-01-02 10:00:00"}), frozenset(), (), "iso-datetime", at_utc=True)
    assert profile._keys_of("1950-01-03T00:00:00+14:00", printed, {}) == ("w1950-01-02 10:00:00",)
    local = profile._Published(frozenset({"1950-01-03 00:00:00"}), frozenset(), (), "iso-datetime")
    assert profile._keys_of("1950-01-03T00:00:00+14:00", local, {}) == ("w1950-01-03 00:00:00",)
