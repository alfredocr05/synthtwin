"""The checks of lane PS2's gate (plan P4-D433), shared by the suite and K-HZ-07's driver (plan P4-D444).

THE SUITE'S TIME (the orchestrator's rule of 2026-10-26; batch 4l OWES 1,
lane SPD): `tests/test_dates_held_by_the_floor.py` took 738.7 s, nearly all
of it in cases at 20,000 rows. The suite keeps ONE of them
(`KEPT_SHAPE`'s count, the floor-size proof) beside the cases that need no
table; every other case at 20,000 rows runs in
`tools/measurements/kpi_dates_held.py` under `kpi_run.py --slow` (K-HZ-07),
one item a case, through the functions below, so a moved case keeps its
exact check: one function, never two copies. Each takes ``described``, the
getter the gate's fixture was -- a sweep shape and a size to the table's
path and the folder holding its description, each made once through the
zoo's own path (`dates_held.answered`) -- or a folder of its own.
"""

from __future__ import annotations

import contextlib
import datetime
import io
import json
import pathlib
import random
import typing

from synthtwin import cli, contract, profile, taxonomy, validation

import dates_held
import unanswered_identifier_shapes as shapes

Described = typing.Callable[[str, int], "tuple[pathlib.Path, pathlib.Path]"]

# The one case at 20,000 rows the suite keeps (every table of the sweep is
# written by one writer, `dates_held._table`'s CSV): birth, admission and
# death dates on one row a person, counted in rows.
KEPT_SHAPE = "one_row"
ROWS = 20000

# K-HZ-07's item lines: what the check being run counted, noted before its
# asserts judge it, so a failing item prints its count as a passing one
# does. The checks that read no count (a block's words, a digest, an exit)
# note nothing and the line says so. The driver clears it before each item.
COUNTED: "dict[str, int]" = {}


def _noted(found: "dict[str, object]") -> None:
    """The count `dates_held.dates_held_few` found, kept for the driver's line."""
    COUNTED["few"] = COUNTED.get("few", 0) + int(found["few"])  # type: ignore[call-overload]
    COUNTED["printed"] = COUNTED.get("printed", 0) + len(found["printed"])  # type: ignore[arg-type]


def counted_words() -> str:
    """The driver's words for the item just run: each count, or that its check reads none."""
    return " ".join(f"{key}={COUNTED[key]}" for key in sorted(COUNTED)) or "no count in this check"


# -- (A): no date one to ten people or rows hold is published -------------


def no_date_one_to_ten_people_or_rows_hold_is_published(described: Described, shape: str, rows: int) -> None:
    source, folder = described(shape, rows)
    found = dates_held.dates_held_few(source, folder, dates_held.options_of(shape)[1])
    _noted(found)
    assert found["dated"], f"{shape}: no column read as dates"
    assert found["few"] == 0, found["named"][:20]  # type: ignore[index]
    assert found["printed"] == [], found["printed"][:20]  # type: ignore[index]


# Lane E0c's two exposures, each column by name: counted in rows (one row a
# person, no person column that repeats), and every date it publishes held.
EXPOSED = (
    ("demographics", ("dob_iso", "dob_us", "dob_text")),
    ("phi_registry", ("birth_date",)),
)


def lane_e0c_exposures_are_counted_in_rows_and_held(described: Described, shape: str,
                                                    columns: "tuple[str, ...]", rows: int) -> None:
    source, folder = described(shape, rows)
    found = dates_held.dates_held_few(source, folder)
    _noted(found)
    assert found["counted_in"] == "rows"
    for column in columns:
        assert column in found["dated"]  # type: ignore[operator]
        block = dates_held.block_of(folder, dates_held.SWEEP[shape].name, column)
        grain = block.get("time_grain")
        # Pooled at a grain coarser than the day, or held: never the day.
        assert isinstance(grain, dict) and grain["rung"] in ("year", "quarter", "month", "held"), (column, grain)


# -- a column whose day grain the floor holds keeps its bytes --------------


def a_date_column_the_floor_holds_at_the_day_keeps_its_bytes(described: Described, shape: str, column: str,
                                                             rows: int) -> None:
    source, folder = described(shape, rows)
    block = dates_held.block_of(folder, dates_held.SWEEP[shape].name, column)
    assert "time_grain" not in block, block.get("time_grain")
    assert dates_held.dense_digest(folder, shape, column) == dates_held.DENSE_DIGESTS[(shape, column, rows)]


def a_stamp_whose_days_the_floor_holds_keeps_its_time_of_day(described: Described) -> None:
    """The dense stamp to the minute, no person column, at 20,000 rows: its hours still published."""
    source, folder = described("dense_only", 20000)
    block = dates_held.block_of(folder, "dense_only", "arrived_at")
    assert block["role"] == "datetime"
    percentiles = block["date_percentiles"]
    assert isinstance(percentiles, dict)
    assert any(isinstance(point, str) and not point.endswith("00:00:00") for point in percentiles.values())


# -- the twin ---------------------------------------------------------------


def the_twin_writes_valid_dates_and_meets_its_description(described: Described, shape: str) -> None:
    source, folder = described(shape, 20000)
    name = dates_held.SWEEP[shape].name
    quiet = io.StringIO()
    with contextlib.redirect_stdout(quiet), contextlib.redirect_stderr(quiet):
        made = cli.main(["generate", f"{folder / (name + '-profile.json')}", "--out-dir", f"{folder}",
                         "--seed", "0", "--replace"])
    assert made == 0, quiet.getvalue()[-2000:]
    found = dates_held.dates_held_few(source, folder)
    _noted(found)
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
    # Repair round 2: the births at +14:00 and -10:00, pooled at the month in
    # people on the shared clock (wave6/PS2/repair2/g1.log), the same limit.
    "utc_split": {"born_at.date-ladder.p25", "born_at.day_of_month_census.groups", "born_at.tails.high.rows",
                  "born_at.tails.high.values", "born_at.tails.low.boundary", "born_at.tails.low.rows"},
}


# -- a day-first date written at a grain keeps its order --------------------


def a_day_first_date_written_at_a_grain_reads_day_first_and_its_twin_is_made(tmp_path: pathlib.Path) -> None:
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


def birth_dates_beside_ten_patients_stay_held_in_people(tmp_path: pathlib.Path) -> None:
    """Lane HX2's `dob_ten` at 20,000 rows: ten patients' birth dates, each on 2,000 rows.

    The patient key holds fewer than the floor's people, so no subject column
    counts in people and the rows are counted too -- but the key, attached to
    the column and telling its people apart, still holds it (P4-D406): each
    date falls on far more than ten rows, and counted in rows alone all ten
    would be published.
    """
    seen = shapes.run(tmp_path, "dob_ten", 20000)
    COUNTED.update(description_values=int(seen["description_values"]),  # type: ignore[call-overload]
                   twin_cells=int(seen["twin_cells"]))  # type: ignore[call-overload]
    assert seen["profile_exit"] == 0 and seen["validate_exit"] == 0, seen
    assert seen["description_values"] == 0 and seen["twin_cells"] == 0, seen
    # Since lane SH2's merge (batch 4m, P4-D434) these births, 1930 on, reach
    # the Safe Harbor question first, which holds the column before the count.
    assert seen["evidence"] == taxonomy.rendered(taxonomy.EVIDENCE_UNANSWERED_IDENTITY, ())


# -- the words: rows, not people ---------------------------------------------


def the_description_and_its_summary_say_rows_where_rows_are_counted(described: Described) -> None:
    """NF130 and NF131 where each row is its own holder; NF128 where a person column counts in people."""
    source, folder = described("no_person", 20000)
    held = dates_held.block_of(folder, "no_person", "event_date")
    births = dates_held.block_of(folder, "no_person", "birth_date")
    assert held["role"] == "identifier"
    assert held["detection_evidence"] == taxonomy.rendered(taxonomy.EVIDENCE_HELD_IN_ROWS, ())
    # Births from 1930 on reach the Safe Harbor question, answered `yes` by the
    # zoo's truthful answers, since lane SH2's merge (batch 4m, P4-D434); the
    # pooled sentence is pinned on dates that are no one's birth, in the kept
    # file's `test_dates_too_sparse_by_the_day_are_pooled_in_rows_and_say_so`.
    assert births["role"] == "identifier"
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
    assert beside["role"] == "identifier"


# -- repair round 1 -----------------------------------------------------------


def no_question_is_put_on_a_column_the_count_in_rows_held(described: Described) -> None:
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


def the_raised_floor_holds_every_published_date(described: Described) -> None:
    """Skeptic 1, item 4: days on 18 or 19 rows keep the day at 11 and are pooled under `--smallest-group 20`."""
    source, folder = described("even_days_20", 20000)
    found = dates_held.dates_held_few(source, folder, 20)
    _noted(found)
    assert found["few"] == 0 and found["printed"] == [], found
    block = dates_held.block_of(folder, "even_days", "admit_date")
    grain = block.get("time_grain")
    assert isinstance(grain, dict) and grain["rung"] in ("month", "quarter", "year", "held"), grain
    _source, eleven = described("even_days", 20000)
    assert "time_grain" not in dates_held.block_of(eleven, "even_days", "admit_date")


OWN_CLOCK_SHAPES = ("excel_births", "unix_afternoons", "unix_millis", "utc_offsets")


def dates_read_by_their_own_clock_and_count_are_held(described: Described, shape: str) -> None:
    """Skeptic 1, item 5 and Codex's items 1 and 2: each date counted on the day it truly names.

    Excel days declared; Unix seconds at 13:00, whose day's own rendering
    rounds to the next day; milliseconds a millisecond before midnight;
    stamps published on the shared clock, one a day there. Each published
    a real date on one row before; each column is now pooled or held.
    """
    source, folder = described(shape, 20000)
    found = dates_held.dates_held_few(source, folder)
    _noted(found)
    assert found["counted_in"] == "rows" and found["dated"], found
    assert found["few"] == 0 and found["printed"] == [], found
    for column in found["dated"]:  # type: ignore[union-attr]
        grain = dates_held.block_of(folder, dates_held.SWEEP[shape].name, f"{column}").get("time_grain")
        assert isinstance(grain, dict) and grain["rung"] != "day", (column, grain)


def a_month_first_column_under_day_first_is_described_at_its_grain(described: Described) -> None:
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


def an_older_description_is_met_by_its_unchanged_source(tmp_path: pathlib.Path) -> None:
    """Codex's item 3: validation reads the grain a description published, its absence included.

    20,000 consecutive days from 1950, written by a description made before
    the count in rows (the count switched off), published every day; the
    validator once pooled the unchanged source and missed eleven checks.
    The count is switched off for the one profile and put back after it,
    as the gate's `monkeypatch.context()` did.
    """
    first = datetime.date(1950, 1, 1)
    lines = [[(first + datetime.timedelta(days=index)).isoformat(), "BA"[index % 2]] for index in range(20000)]
    source = tmp_path / "days.csv"
    source.write_bytes(dates_held.health_zoo.csv_bytes(["seen_on", "group"], lines))
    counting = profile._dates_few_in_rows
    profile._dates_few_in_rows = lambda *arguments, **keywords: False  # type: ignore[assignment]
    try:
        quiet = io.StringIO()
        with shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(quiet), contextlib.redirect_stderr(quiet):
            assert cli.main(["profile", f"{source}", "--out-dir", f"{tmp_path}", "--replace"],
                            small_tables_refused=True) == 0, quiet.getvalue()[-1500:]
    finally:
        profile._dates_few_in_rows = counting  # type: ignore[assignment]
    described = json.loads((tmp_path / "days-profile.json").read_text(encoding="utf-8"))
    assert "time_grain" not in [block for block in described["columns"] if block["name"] == "seen_on"][0]
    loaded = contract.load_profile(f"{tmp_path / 'days-profile.json'}")
    outcome = validation.measure(loaded, f"{source}")
    missed = [f"{check.column}.{check.subcheck}" for check in outcome.checks if check.verdict == validation.MISSED]
    assert missed == [], missed


def the_evidence_never_denies_repeated_people(tmp_path: pathlib.Path) -> None:
    """Codex's item 6: 1,000 declared patients on 20 rows each, `--smallest-group 2000`, event dates that vary.

    The person column repeats but names fewer people than the raised
    floor; its dates are counted in those people (repair round 2, the
    combined verify's item 1), so no bucket reaches the floor and the
    column is held in people; the sentences never say that no column names
    a person on several rows.
    """
    draw = random.Random(dates_held.SEED)
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


def a_raised_floor_above_the_tables_people_still_counts_its_dates_in_people(described: Described) -> None:
    """The combined verify's item 1: 1,000 patients, one of them on 2,500 rows all on one day, `--smallest-group 2000`.

    Counted in rows, those 2,500 rows passed the raised floor and the one
    patient's day was published as the low tail, beside points 929 to 940
    people hold. Counted in its people, whatever their number, no date
    reaches 2,000 people and the column is held; at the owner's 11 its
    block is the base's, byte for byte.
    """
    source, folder = described("few_visit_days_2000", 20000)
    found = dates_held.dates_held_few(source, folder, 2000)
    _noted(found)
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


def dates_on_the_shared_clock_are_counted_in_people_there(described: Described) -> None:
    """The combined verify's item 2: births at local midnight at +14:00 and -10:00, ten rows a person.

    Every local day holds 12 people; on the shared clock, where the block
    publishes the column, each day holds 6. Counted under its local text,
    every point and both tails printed a moment 6 people hold.
    """
    source, folder = described("utc_split", 20000)
    found = dates_held.dates_held_few(source, folder)
    _noted(found)
    assert found["counted_in"] == "people" and found["dated"] == ["born_at"], found
    assert found["few"] == 0 and found["printed"] == [], found
    block = dates_held.block_of(folder, "utc_split", "born_at")
    grain = block.get("time_grain")
    assert block.get("datetimes_read_at") == "utc" or isinstance(grain, dict), block
    assert isinstance(grain, dict) and grain["rung"] != "day", grain


def moved_cases() -> "list[tuple[str, str, typing.Callable[[Described, pathlib.Path], None]]]":
    """Every case at 20,000 rows the gate moved here: the item's name, the gate's node it was, and its call.

    The call takes the getter and a fresh folder of its own.
    """
    gate = "tests/test_dates_held_by_the_floor.py::"
    found: "list[tuple[str, str, typing.Callable[[Described, pathlib.Path], None]]]" = []

    def each(name: str, node: str, call: "typing.Callable[[Described, pathlib.Path], None]") -> None:
        nonlocal found
        found += [(name, gate + node, call)]

    for shape in sorted(dates_held.SWEEP):
        if shape != KEPT_SHAPE:
            each(f"no_date_few:{shape}", f"test_no_date_one_to_ten_people_or_rows_hold_is_published[{shape}-at20k]",
                 lambda get, _folder, shape=shape: no_date_one_to_ten_people_or_rows_hold_is_published(get, shape, ROWS))
    for place, (shape, columns) in enumerate(EXPOSED):
        each(f"e0c_exposure:{shape}",
             f"test_lane_e0c_exposures_are_counted_in_rows_and_held[{shape}-columns{place}-at20k]",
             lambda get, _folder, shape=shape, columns=columns: lane_e0c_exposures_are_counted_in_rows_and_held(
                 get, shape, columns, ROWS))
    for shape in sorted(dates_held.DENSE):
        for column in dates_held.DENSE[shape]:
            each(f"dense_bytes:{shape}:{column}",
                 f"test_a_date_column_the_floor_holds_at_the_day_keeps_its_bytes[{shape}-{column}-at20k]",
                 lambda get, _folder, shape=shape, column=column:
                 a_date_column_the_floor_holds_at_the_day_keeps_its_bytes(get, shape, column, ROWS))
    each("stamp_time_of_day", "test_a_stamp_whose_days_the_floor_holds_keeps_its_time_of_day",
         lambda get, _folder: a_stamp_whose_days_the_floor_holds_keeps_its_time_of_day(get))
    for shape in sorted(dates_held.SWEEP):
        each(f"twin_valid:{shape}", f"test_the_twin_writes_valid_dates_and_meets_its_description[{shape}]",
             lambda get, _folder, shape=shape: the_twin_writes_valid_dates_and_meets_its_description(get, shape))
    each("day_first_registry", "test_a_day_first_date_written_at_a_grain_reads_day_first_and_its_twin_is_made",
         lambda _get, folder: a_day_first_date_written_at_a_grain_reads_day_first_and_its_twin_is_made(folder))
    each("ten_patients_in_people", "test_birth_dates_beside_ten_patients_stay_held_in_people",
         lambda _get, folder: birth_dates_beside_ten_patients_stay_held_in_people(folder))
    each("words_say_rows", "test_the_description_and_its_summary_say_rows_where_rows_are_counted",
         lambda get, _folder: the_description_and_its_summary_say_rows_where_rows_are_counted(get))
    each("no_question_rows_held", "test_no_question_is_put_on_a_column_the_count_in_rows_held",
         lambda get, _folder: no_question_is_put_on_a_column_the_count_in_rows_held(get))
    each("raised_floor", "test_the_raised_floor_holds_every_published_date",
         lambda get, _folder: the_raised_floor_holds_every_published_date(get))
    for shape in OWN_CLOCK_SHAPES:
        each(f"own_clock:{shape}", f"test_dates_read_by_their_own_clock_and_count_are_held[{shape}]",
             lambda get, _folder, shape=shape: dates_read_by_their_own_clock_and_count_are_held(get, shape))
    each("month_first_day_first", "test_a_month_first_column_under_day_first_is_described_at_its_grain",
         lambda get, _folder: a_month_first_column_under_day_first_is_described_at_its_grain(get))
    each("older_description", "test_an_older_description_is_met_by_its_unchanged_source",
         lambda _get, folder: an_older_description_is_met_by_its_unchanged_source(folder))
    each("never_denies_people", "test_the_evidence_never_denies_repeated_people",
         lambda _get, folder: the_evidence_never_denies_repeated_people(folder))
    each("raised_floor_above_people", "test_a_raised_floor_above_the_tables_people_still_counts_its_dates_in_people",
         lambda get, _folder: a_raised_floor_above_the_tables_people_still_counts_its_dates_in_people(get))
    each("shared_clock_people", "test_dates_on_the_shared_clock_are_counted_in_people_there",
         lambda get, _folder: dates_on_the_shared_clock_are_counted_in_people_there(get))
    return found
