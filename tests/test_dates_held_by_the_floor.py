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

THE SUITE'S TIME (the orchestrator's rule of 2026-10-26; batch 4l OWES 1,
lane SPD, plan P4-D444): this file took 738.7 s, nearly all of it in cases
at 20,000 rows. It keeps ONE of them -- the count over the sweep's
`dates_held_checks.KEPT_SHAPE`, the floor-size proof -- beside every case
that needs no table and the refusal one row under the floor; every other
case at 20,000 rows runs in K-HZ-07's driver,
`tools/measurements/kpi_dates_held.py`, under `kpi_run.py --slow`, one item
a case, through the same checks (`tests/dates_held_checks.py`). LANE SPD
RULINGS 1 (2026-11-01): each change that lets a real date out keeps a case
here too, at the smallest size that goes red on it (the section below).
"""

from __future__ import annotations

import contextlib
import datetime
import io
import os
import pathlib
import random
import subprocess
import sys
import types

import pytest

from synthtwin import cli, grains, parsing, profile, taxonomy

import dates_held
import dates_held_checks as checks
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
# The other shapes, and every other case at 20,000 rows, run in K-HZ-07's
# driver (`dates_held_checks.moved_cases`, plan P4-D444).


@pytest.mark.parametrize("rows", SIZES, ids=SIZE_IDS)
@pytest.mark.parametrize("shape", [checks.KEPT_SHAPE])
def test_no_date_one_to_ten_people_or_rows_hold_is_published(described, shape: str, rows: int) -> None:
    checks.no_date_one_to_ten_people_or_rows_hold_is_published(described, shape, rows)


# -- a real date let out goes red here, never only under --slow -------------
# LANE SPD RULINGS 1 (the orchestrator, 2026-11-01, HIPAA first): CI does not
# run `kpi_run --slow`, so each change that puts a real date in a description
# keeps a case in the suite, the smallest that goes red on it. The count in
# rows starts at the table floor, so each case lowers the floor to its own
# size and takes the command's real path, with the check and the counter of
# the 20,000-row case K-HZ-07 still runs. Each mutant named is in
# wave6/SPD/repair1/ (`mut_suite.log`).


@pytest.mark.parametrize(("shape", "rows"), [
    ("one_row_open", 600),  # rows_without_person_only
    ("excel_births", 600),  # counted_unread
    ("utc_offsets", 600),  # utc_unread
    ("unix_millis", 600),  # day_rendering_only, true_day_dropped, rows_at_precision
    ("month_first", 600),  # order_one_way, order_unpinned
    ("utc_split", 4000),  # shared_clock_unread
])
def test_a_real_date_let_out_goes_red_at_a_small_size(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, shape: str, rows: int
) -> None:
    monkeypatch.setattr(parsing, "TABLE_ROW_FLOOR", rows)
    options, _floor = dates_held.options_of(shape)
    source = dates_held.answered(dates_held.SWEEP[shape], tmp_path, rows, options)
    checks.no_date_one_to_ten_people_or_rows_hold_is_published(lambda *_a: (source, tmp_path), shape, rows)


def _profiled(folder: pathlib.Path, name: str, header: "list[str]", lines: "list[list[str]]", *typed: str) -> pathlib.Path:
    """`synthtwin profile` on a small table the test writes, the table floor already lowered to its size."""
    source = folder / f"{name}.csv"
    source.write_bytes(dates_held.health_zoo.csv_bytes(header, lines))
    quiet = io.StringIO()
    with shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(quiet), contextlib.redirect_stderr(quiet):
        assert cli.main(["profile", f"{source}", "--out-dir", f"{folder}", "--replace", *typed]) == 0, quiet.getvalue()[-1500:]
    return source


def test_a_raised_floor_holds_days_the_owners_floor_would_publish(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mutant `floor_fixed_at_11`: 32 days on 18 or 19 rows under `--smallest-group 20` printed 11 real days."""
    monkeypatch.setattr(parsing, "TABLE_ROW_FLOOR", 600)
    first = datetime.date(2022, 1, 1)
    lines = [[(first + datetime.timedelta(days=index % 32)).isoformat(), "AB"[index % 2]] for index in range(600)]
    source = _profiled(tmp_path, "days19", ["admit_date", "group"], lines, "--smallest-group", "20")
    found = dates_held.dates_held_few(source, tmp_path, 20)
    assert found["dated"] == ["admit_date"], found
    assert found["few"] == 0 and found["printed"] == [], found


def test_a_raised_floor_above_the_tables_people_never_counts_their_dates_in_rows(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mutant `rows_below_the_floor`: one of 120 patients on 300 rows, one day, floor 150, printed that patient's day."""
    monkeypatch.setattr(parsing, "TABLE_ROW_FLOOR", 1500)
    draw = random.Random(dates_held.SEED)
    day = datetime.date(2023, 6, 15)
    others = [day + datetime.timedelta(days=step) for step in range(1, 8)]
    owners = [0] * 300 + [1 + index % 119 for index in range(1200)]
    lines = [[f"P{1000000 + owner:07d}", (day if owner == 0 else draw.choice(others)).isoformat(),
              f"{draw.uniform(40, 140):.1f}"] for owner in owners]
    draw.shuffle(lines)
    source = _profiled(tmp_path, "oneday", ["patient_id", "visit_date", "weight"], lines,
                       "--identifier", "patient_id", "--smallest-group", "150")
    found = dates_held.dates_held_few(source, tmp_path, 150)
    assert found["counted_in"] == "people" and found["dated"] == ["visit_date"], found
    assert found["few"] == 0 and found["printed"] == [], found


# -- what K-HZ-07's driver runs for the gate ---------------------------------


def test_the_driver_keeps_every_moved_case() -> None:
    """Skeptic 1 of lane SPD item 2: K-HZ-07's value has no item count, so a dropped shape would stay green."""
    cases = checks.moved_cases()
    names = [name for name, _node, _call in cases]
    nodes = [node for _name, node, _call in cases]
    assert len(cases) == 59
    assert len(set(names)) == len(names) and len(set(nodes)) == len(nodes)
    sweep = set(dates_held.SWEEP)
    assert {name.split(":")[1] for name in names if name.startswith("no_date_few:")} == sweep - {checks.KEPT_SHAPE}
    assert {name.split(":")[1] for name in names if name.startswith("twin_valid:")} == sweep
    assert {tuple(name.split(":")[1:]) for name in names if name.startswith("dense_bytes:")} == {
        (shape, column) for shape, columns in dates_held.DENSE.items() for column in columns
    }
    assert {name.split(":")[1] for name in names if name.startswith("own_clock:")} == set(checks.OWN_CLOCK_SHAPES)
    assert {name.split(":")[1] for name in names if name.startswith("e0c_exposure:")} == {
        shape for shape, _columns in checks.EXPOSED
    }


def test_a_failing_count_is_noted_before_it_is_judged(monkeypatch: pytest.MonkeyPatch) -> None:
    """Skeptic 1 of lane SPD item 1: K-HZ-07's items printed a verdict and no count."""
    monkeypatch.setattr(dates_held, "dates_held_few", lambda *a: {
        "dated": ["born"], "few": 3, "printed": ["1950-01-02"], "named": ["born"]})
    checks.COUNTED.clear()
    with pytest.raises(AssertionError):
        checks.no_date_one_to_ten_people_or_rows_hold_is_published(
            lambda *a: (pathlib.Path("t.csv"), pathlib.Path("f")), checks.KEPT_SHAPE, 20000)
    assert checks.counted_words() == "few=3 printed=1"
    checks.COUNTED.clear()
    assert checks.counted_words() == "no count in this check"


@pytest.mark.parametrize(("typed", "code", "said"), [
    (["--kpi", "--only", "dense_bytes:*"], 2, "needs --moved-only"),
    (["--moved-only", "--only", "own_clok:*"], 1, "nothing was measured"),
])
def test_the_driver_refuses_a_partial_record_and_an_empty_choice(
    tmp_path: pathlib.Path, typed: "list[str]", code: int, said: str
) -> None:
    """Codex's items 1 and 3: `--only` wrote a whole KPI record over 7 of 59, and a typo exited 0."""
    driver = pathlib.Path(__file__).resolve().parents[1] / "tools" / "measurements" / "kpi_dates_held.py"
    run = subprocess.run([sys.executable, f"{driver}"] + typed, capture_output=True, text=True, timeout=300,
                         env={**os.environ, "TMPDIR": f"{tmp_path}", "TEMP": f"{tmp_path}", "TMP": f"{tmp_path}"})
    assert run.returncode == code, run.stdout + run.stderr
    assert said in run.stdout + run.stderr
    assert "KPI " not in run.stdout


def test_a_failing_moved_item_fails_the_driver_and_names_its_assert(tmp_path: pathlib.Path) -> None:
    """Verify of lane SPD items 1 and 4: K-HZ-07's value holds no count of its 59 moved items, so the exit is their
    only signal to kpi_run, and a bare assert has no message outside pytest."""
    root = pathlib.Path(__file__).resolve().parents[1]
    driver = root / "tools" / "measurements" / "kpi_dates_held.py"
    script = tmp_path / "drive.py"
    script.write_text(
        "import runpy, sys\n"
        f"sys.path[:0] = [{str(root / 'tests')!r}, {str(root / 'src')!r}]\n"
        "import dates_held_checks\n"
        "def failing(described, folder):\n"
        "    assert described is None\n"
        "dates_held_checks.moved_cases = lambda: [('stubbed', 'tests/stubbed.py::stubbed', failing)]\n"
        f"sys.argv = [{str(driver)!r}, '--moved-only']\n"
        f"runpy.run_path({str(driver)!r}, run_name='__main__')\n",
        encoding="utf-8", newline="\n",
    )
    run = subprocess.run([sys.executable, f"{script}"], capture_output=True, text=True, timeout=300,
                         env={**os.environ, "TMPDIR": f"{tmp_path}", "TEMP": f"{tmp_path}", "TMP": f"{tmp_path}"})
    assert run.returncode == 1, run.stdout + run.stderr
    assert "moved stubbed (tests/stubbed.py::stubbed): FAIL" in run.stdout
    assert "assert described is None" in run.stdout


# -- the twin's layouts -------------------------------------------------------


def test_a_cell_in_another_layout_than_its_columns_own_is_out() -> None:
    """The twin's check reads each cell in its column's own layouts only (skeptic 1, item 8)."""
    assert dates_held.in_its_layouts("03/17/2024", ("%m/%d/%Y",))
    assert not dates_held.in_its_layouts("2024-03-17", ("%m/%d/%Y",))
    assert not dates_held.in_its_layouts("17-Mar-2024", ("%Y-%m-%d",))
    assert dates_held.in_its_layouts("45000", ("count:excel-1900",))
    assert not dates_held.in_its_layouts("2023-03-15", ("count:excel-1900",))


def test_dates_too_sparse_by_the_day_are_pooled_in_rows_and_say_so(tmp_path: pathlib.Path) -> None:
    """NF131 on a table naming nobody: ten years of days under the floor, every month over it.

    The birth dates that pinned this sentence are held since lane SH2's merge.
    """

    def spread(rows: int, seed: int) -> "tuple[list[str], list[list[str]]]":
        draw = random.Random(seed)
        start = datetime.date(2015, 1, 1)
        return ["admit_date", "ward"], [
            [(start + datetime.timedelta(days=draw.randrange(3650))).isoformat(), draw.choice(("A", "B"))]
            for _row in range(rows)
        ]

    table = dates_held._table("spread", spread, ("admit_date", "ward"), {})
    dates_held.answered(table, tmp_path, 20000, ())
    block = dates_held.block_of(tmp_path, "spread", "admit_date")
    assert block["detection_evidence"] == taxonomy.rendered(taxonomy.EVIDENCE_POOLED_IN_ROWS, ())


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


def test_the_true_day_of_a_count_is_never_rounded_forward() -> None:
    """Codex's item 2, the product's own part: the instant floored to its midnight."""
    seconds = profile._CellReading("seconds-since-1970")
    assert profile._counted_true_day(f"{946684800 + 13 * 3600}", seconds) == "2000-01-01"
    millis = profile._CellReading("milliseconds-since-1970")
    assert profile._counted_true_day(f"{946684800000 + 86399999}", millis) == "2000-01-01"
    assert profile._counted_true_day("45000.75", profile._CellReading("excel-1900")) == "2023-03-15"
    assert profile._counted_true_day("x", seconds) == ""


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
