"""P4-D417 (lane PS): dates and times beside a person column, pooled in people.

THE DEFECT (measured at batch 4e's integration, the health data zoo at 600
rows). Plan P4-D406 counts every point a column of dates or times publishes
in PEOPLE, and a column one of whose points one to ten people hold was held
WHOLE: its twin wrote made-up figures in the date's layout (`4191-54-63`,
`77:21`), so analyst code that parses the column failed on the twin, and the
zoo fell from 20 to 14 of 40 kinds passing end to end.

THE RULE. (1) THE G1 FLOOR: a held column of dates, stamps, clock times or
counted dates writes VALID values in each of its own layouts, drawn inside
the spans its record publishes or the method's fixed span, never from the
table. (2) POOLING IN PEOPLE: such a column is described at a coarser
calendar grain instead -- every published point a bucket the floor's number
of people hold, the tails pooled into the first and the last -- at the rung
its own published facts choose (the rows and the spans: `grains.ladder_walk`), and
its twin draws each value inside its bucket.

THE GATE: every zoo kind's date column parses on the twin; grains at day,
month and year; a pooled tail; a mode a few people hold never printed;
the record's rung the one its facts choose (the loader refuses any other);
the product's draw equal to the oracle's (method G7.13); the contract's
refusals; and, red on their mutants (`wave6/PS/mutants.log`): rows counted
for people, a point at a grain fewer than eleven people hold, a twin cell
that does not parse, the grain chosen from failing points, a tail published
as itself.
"""

from __future__ import annotations

import contextlib
import csv
import datetime
import io
import json
import pathlib
import random

import pytest

from synthtwin import cli, contract, errors, generation, grains, validation

import health_zoo
import persons_counted
import unanswered_identifier_shapes as shapes

FLOOR = 11


# -- the tables ------------------------------------------------------------


def _visits(
    rows: int,
    patients: int,
    first: datetime.date,
    days: int,
    seed: int,
    written: str = "iso",
    extra: "list[tuple[int, datetime.date]] | None" = None,
) -> str:
    """Visits: a patient key, a date of each row, a measurement.

    Each row is a random patient on a random day of ``days`` from
    ``first``; ``extra`` adds rows of chosen patients on chosen days.
    """
    draw = random.Random(seed)
    lines = ["patient,seen,value"]
    picked: "list[tuple[int, datetime.date]]" = []
    for _row in range(rows):
        picked += [(draw.randrange(patients), first + datetime.timedelta(days=draw.randrange(days)))]
    picked += extra or []
    for person, day in picked:
        seen = day.isoformat() if written == "iso" else day.strftime("%m/%d/%Y")
        if written == "stamp":
            seen = f"{day.isoformat()} {draw.randint(0, 23):02d}:{draw.randint(0, 59):02d}"
        lines += [f"REC{80000000 + 7 * person:08d},{seen},{draw.uniform(3, 150):.1f}"]
    return "\n".join(lines) + "\n"


def _clocks(rows: int, patients: int, seed: int) -> str:
    """Theatre times of day, to the minute, from 07:00 to 18:59, beside a patient key."""
    draw = random.Random(seed)
    lines = ["patient,start,value"]
    for _row in range(rows):
        lines += [
            f"REC{80000000 + 7 * draw.randrange(patients):08d},"
            f"{draw.randint(7, 18):02d}:{draw.randint(0, 59):02d},{draw.uniform(3, 150):.1f}"
        ]
    return "\n".join(lines) + "\n"


def _profiled(folder: pathlib.Path, stem: str, text: str, *extra: str) -> "dict[str, object]":
    path = folder / f"{stem}.csv"
    path.write_text(text, encoding="utf-8", newline="\n")
    screen = io.StringIO()
    with shapes.nobody_at_the_keyboard():
        with contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
            code = cli.main(["profile", f"{path}", "--out-dir", f"{folder}", "--replace", *extra])
    assert code == 0, screen.getvalue()[-2000:]
    return json.loads((folder / f"{stem}-profile.json").read_text(encoding="utf-8"))


def _generated_and_validated(folder: pathlib.Path, stem: str) -> "tuple[set[str], set[str]]":
    """The twin generated at seed 0; the columns the twin and the real table each miss.

    A census of repetition drawn from published counts -- the person
    column's pooled in people, a held column's implied by its counts (plan
    P4-D406) -- is not the table's own, so the real table may miss it, as
    NF126 states; every other miss is named.
    """
    quiet = io.StringIO()
    with contextlib.redirect_stdout(quiet), contextlib.redirect_stderr(quiet):
        made = cli.main(["generate", f"{folder / (stem + '-profile.json')}", "--out-dir",
                         f"{folder}", "--seed", "0", "--replace"])
    assert made == 0
    described = contract.load_profile(f"{folder / (stem + '-profile.json')}")
    found: "list[set[str]]" = []
    for path in (folder / f"{stem}-twin.csv", folder / f"{stem}.csv"):
        outcome = validation.measure(described, f"{path}")
        found += [{
            f"{check.column}" for check in outcome.checks if check.verdict == validation.MISSED
            and "occurrences" not in f"{check.subcheck}"
        }]
    return found[0], found[1]


def _column(path: pathlib.Path, name: str) -> "list[str]":
    with open(path, encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    place = rows[0].index(name)
    return [row[place] for row in rows[1:]]


def _block(described: "dict[str, object]", name: str) -> "dict[str, object]":
    return [one for one in described["columns"] if one["name"] == name][0]  # type: ignore[index, union-attr]


def _counted_few(folder: pathlib.Path, stem: str) -> int:
    return int(persons_counted.count_files(folder / f"{stem}.csv", folder)["few"])


def _parses(cells: "list[str]", form: str) -> int:
    """How many present cells do NOT parse in the source's own format (an analyst's read)."""
    bad = 0
    for cell in cells:
        if not cell:
            continue
        try:
            datetime.datetime.strptime(cell, form)
        except ValueError:
            bad = bad + 1
    return bad


# -- (1) every zoo kind's date column parses on the twin --------------------

# The analyst checks of the zoo that read a date or a time held beside its
# people as such, each a check the held columns failed at batch 4e's
# integration (the zoo's HELD_DATES lines, lane PS's).
_DATE_CHECKS = (
    "service_date parses as %m/%d/%Y", "consent_date parses", "ts parses to the second",
    "anes_start parses as %H:%M:%S", "in_room parses as %H:%M", "incision_time parses as %I:%M %p",
    "serial dates read from 1899-12-30", "created_dttm with milliseconds", "durations as HH:MM",
    "collected_at parses as %Y-%m-%d %H:%M", "taken_at parses", "recorded_at parses",
    "DA dates parse as %Y%m%d", "first_treatment_month parses as %Y-%m",
    "admit_ts parses with its offset", "discharge_ts parses with its offset",
)
_ZOO_TABLES = (
    "claims", "redcap", "wearables", "perioperative", "sql_server", "labs", "vitals",
    "flowsheet", "imaging", "encounters", "tumor_registry",
)


@pytest.mark.parametrize("name", _ZOO_TABLES)
def test_every_zoo_kinds_dates_parse_on_the_twin(tmp_path: pathlib.Path, name: str) -> None:
    """At 600 rows each 'parses' check of a table holding dates beside its patients holds on the twin."""
    place = [table.name for table in health_zoo.TABLES].index(name)
    with shapes.nobody_at_the_keyboard():
        result = health_zoo.run_table(health_zoo.TABLES[place], tmp_path, 600, 20261016 + place)
    assert result["steps"]["generate"]["exit"] == 0, result["steps"]
    failed = [failure for failure in result["analyst"] if failure[1] in _DATE_CHECKS]
    assert failed == [], failed
    described = json.loads((tmp_path / f"{name}-profile.json").read_text(encoding="utf-8"))
    grained: "list[str]" = []
    for block in described["columns"]:
        grain = block.get("time_grain")
        if isinstance(grain, dict):
            assert grain["rung"] in grains.RUNGS + (grains.HELD,)
            grained += [f"{block['name']}"]
    # ...and the counter written apart finds no value of a grained column
    # that one to ten people hold (other columns are lane HX2's, K-S3-65).
    named = persons_counted.count_files(tmp_path / f"{name}.csv", tmp_path)["named"]
    assert [one for one in named if one.split("=")[0].split(":")[0] in grained] == [], named


# -- (2) a grain at day, month and year -------------------------------------


@pytest.mark.parametrize(
    ("rung", "rows", "patients", "days", "written", "form"),
    (
        ("day", 6000, 1500, 90, "stamp", "%Y-%m-%d %H:%M"),
        ("month", 1200, 400, 730, "us", "%m/%d/%Y"),
        ("year", 300, 150, 5 * 365, "us", "%m/%d/%Y"),
    ),
)
def test_a_grain_at_day_month_and_year(
    tmp_path: pathlib.Path, rung: str, rows: int, patients: int, days: int, written: str, form: str
) -> None:
    """The walk's rung moves with the visits a bucket would hold; every point at it holds eleven people."""
    text = _visits(rows, patients, datetime.date(2023, 1, 1), days, 7, written)
    described = _profiled(tmp_path, "visits", text, "--identifier", "patient")
    block = _block(described, "seen")
    grain = block["time_grain"]
    assert isinstance(grain, dict) and grain["rung"] == rung, grain
    assert block["role"] in ("datetime", "constant", "binary")
    assert "coarser grain" in f"{block['detection_evidence']}"
    twin, real = _generated_and_validated(tmp_path, "visits")
    assert (twin, real) == (set(), set())
    assert _parses(_column(tmp_path / "visits-twin.csv", "seen"), form) == 0
    assert _counted_few(tmp_path, "visits") == 0
    loaded = contract.load_profile(f"{tmp_path / 'visits-profile.json'}")
    record = [one for one in loaded.columns if one.name == "seen"][0].time_grain
    assert record is not None and grains.walk_holds(record, FLOOR)


def test_the_twin_draws_inside_each_published_bucket(tmp_path: pathlib.Path) -> None:
    """Each twin date falls in a bucket the description publishes, and not every one on its first day."""
    text = _visits(600, 200, datetime.date(2023, 1, 1), 730, 11)
    _profiled(tmp_path, "visits", text, "--identifier", "patient")
    _generated_and_validated(tmp_path, "visits")
    cells = _column(tmp_path / "visits-twin.csv", "seen")
    assert all(cell[8:10] == "01" for cell in cells) is False
    real = sorted({cell[:7] for cell in _column(tmp_path / "visits.csv", "seen")})
    assert {cell[:7] for cell in cells} <= set(real)


# -- (3) a pooled tail -------------------------------------------------------


def test_a_tail_three_people_hold_is_pooled_into_the_first_bucket(tmp_path: pathlib.Path) -> None:
    """Three patients' visits of 2015 are counted in the first month eleven people hold, never published."""
    early = [(900 + one, datetime.date(2015, 6, 3 + one)) for one in range(3)]
    text = _visits(600, 200, datetime.date(2023, 1, 1), 730, 13, "iso", early)
    described = _profiled(tmp_path, "visits", text, "--identifier", "patient")
    block = _block(described, "seen")
    grain = block["time_grain"]
    assert isinstance(grain, dict) and grain["rung"] != grains.HELD, grain
    assert grain["spans"][0][1][:4] == "2023", grain["spans"]
    assert "2015" not in json.dumps(described)
    twin, real = _generated_and_validated(tmp_path, "visits")
    assert (twin, real) == (set(), set())
    assert not any(cell.startswith("2015") for cell in _column(tmp_path / "visits-twin.csv", "seen"))
    assert _counted_few(tmp_path, "visits") == 0


# -- (4) a mode a few people hold is never printed ---------------------------


def test_a_mode_three_people_hold_is_never_printed(tmp_path: pathlib.Path) -> None:
    """Three patients hold 300 rows of June 2023 and nobody else: no point names June, and the twin parses."""
    june = [(950 + one % 3, datetime.date(2023, 6, 10 + one % 5)) for one in range(300)]
    text = _visits(600, 200, datetime.date(2023, 1, 1), 730, 17, "iso", [])
    lines = text.splitlines()
    kept = [lines[0]] + [line for line in lines[1:] if line.split(",")[1][:7] != "2023-06"]
    draw = random.Random(3)
    for person, day in june:
        kept += [f"REC{80000000 + 7 * person:08d},{day.isoformat()},{draw.uniform(3, 150):.1f}"]
    described = _profiled(tmp_path, "visits", "\n".join(kept) + "\n", "--identifier", "patient")
    shown = json.dumps(_block(described, "seen"))
    assert "2023-06" not in shown, shown
    twin, real = _generated_and_validated(tmp_path, "visits")
    assert twin == set() and "seen" not in real
    assert _parses(_column(tmp_path / "visits-twin.csv", "seen"), "%Y-%m-%d") == 0
    assert _counted_few(tmp_path, "visits") == 0


def test_a_held_column_writes_valid_dates_from_its_spans(tmp_path: pathlib.Path) -> None:
    """The G1 floor: where no grain serves, the held column's twin parses in its own layout."""
    june = [(950 + one % 3, datetime.date(2023, 6, 10 + one % 5)) for one in range(300)]
    text = _visits(600, 200, datetime.date(2023, 1, 1), 730, 17, "us", [])
    lines = text.splitlines()
    kept = [lines[0]] + [line for line in lines[1:] if line.split(",")[1][:2] != "06"]
    draw = random.Random(3)
    for person, day in june:
        kept += [f"REC{80000000 + 7 * person:08d},{day.strftime('%m/%d/%Y')},{draw.uniform(3, 150):.1f}"]
    described = _profiled(tmp_path, "visits", "\n".join(kept) + "\n", "--identifier", "patient")
    block = _block(described, "seen")
    if block["role"] == "identifier":
        assert block["time_grain"]["rung"] == grains.HELD
        assert any("drawn inside the last span" in f"{remark}" for remark in block["remarks"])
    twin, _real = _generated_and_validated(tmp_path, "visits")
    assert twin == set()
    cells = _column(tmp_path / "visits-twin.csv", "seen")
    assert _parses(cells, "%m/%d/%Y") == 0, cells[:5]
    assert _counted_few(tmp_path, "visits") == 0


def test_a_column_of_a_few_patients_dates_is_held_and_parses(tmp_path: pathlib.Path) -> None:
    """A hundred and fifty patients' 300 visits over a hundred years: no year holds eleven, so the column is held, and its twin parses."""
    text = _visits(300, 150, datetime.date(1925, 1, 1), 100 * 365, 19, "us")
    described = _profiled(tmp_path, "visits", text, "--identifier", "patient")
    block = _block(described, "seen")
    assert block["role"] == "identifier", block["role"]
    assert block["time_grain"]["rung"] == grains.HELD
    assert block["time_grain"]["spans"] == []
    twin, _real = _generated_and_validated(tmp_path, "visits")
    assert twin == set()
    cells = _column(tmp_path / "visits-twin.csv", "seen")
    assert _parses(cells, "%m/%d/%Y") == 0, cells[:5]
    years = {int(cell[-4:]) for cell in cells}
    assert min(years) >= 2000 and max(years) <= 2029


# -- (5) the grain's choice: fixed by published facts only -------------------


def test_the_grain_is_chosen_from_published_facts_and_not_from_failing_points(
    tmp_path: pathlib.Path,
) -> None:
    """Two weeks of visits at either end of two years: every day there holds eleven people, yet the rung is the quarter.

    A walk chosen by which finer points fail would describe the column by
    day; the rows (400) and the year's span (two years) choose the quarter,
    which is what the record says and the loader checks.
    """
    extra = [(one % 100, datetime.date(2023, 1, 2) + datetime.timedelta(days=one % 7)) for one in range(200)]
    extra += [(one % 100, datetime.date(2024, 12, 24) + datetime.timedelta(days=one % 7)) for one in range(200)]
    text = _visits(0, 1, datetime.date(2023, 1, 1), 1, 23, "stamp", extra)
    described = _profiled(tmp_path, "visits", text, "--identifier", "patient")
    grain = _block(described, "seen")["time_grain"]
    assert isinstance(grain, dict) and grain["rung"] == "quarter", grain
    loaded = contract.load_profile(f"{tmp_path / 'visits-profile.json'}")
    record = [one for one in loaded.columns if one.name == "seen"][0].time_grain
    assert record is not None and grains.walk_holds(record, FLOOR)


def test_a_record_whose_rung_its_facts_do_not_choose_is_refused(tmp_path: pathlib.Path) -> None:
    """TG1: a description naming a finer or a coarser rung than its rows, people and spans choose is not loaded."""
    text = _visits(1200, 400, datetime.date(2023, 1, 1), 730, 7)
    _profiled(tmp_path, "visits", text, "--identifier", "patient")
    path = tmp_path / "visits-profile.json"
    original = json.loads(path.read_text(encoding="utf-8"))
    assert _block(original, "seen")["time_grain"]["rung"] == "month"
    for change in ("finer", "coarser", "rows", "people", "held", "reading", "key", "start"):
        document = json.loads(json.dumps(original))
        grain = _block(document, "seen")["time_grain"]
        if change == "finer":
            grain["spans"] += [["day", "2023-01-01", "2024-12-31"]]
            grain["rung"] = "day"
        elif change == "coarser":
            grain["spans"] = grain["spans"][:2]
            grain["rung"] = "quarter"
        elif change == "rows":
            grain["rows"] = 1199
        elif change == "people":
            grain["people"] = 200
        elif change == "held":
            grain["rung"] = grains.HELD
        elif change == "reading":
            grain["reading"] = "month-first-date"
        elif change == "key":
            grain["extra"] = 1
        else:
            grain["spans"][2][1] = "2023-01-02"
        path.write_text(json.dumps(document), encoding="utf-8", newline="\n")
        with pytest.raises(errors.ProfileError):
            contract.load_profile(f"{path}")


def test_the_walk_reads_its_record_alone() -> None:
    """`walk_holds` recomputes the rung from the rows, the people and the spans; every other rung is refused."""
    day = 86400 * 10**9
    first = 19358 * day
    reading = grains.Reading(grains.DATE, "iso-date")
    spans = (
        ("year", first, grains.start_of(first + 400 * day, "year")),
        ("quarter", first, grains.start_of(first + 700 * day, "quarter")),
        ("month", first, grains.start_of(first + 720 * day, "month")),
    )
    # 600 rows of 200 people: about 346 visits, 22 a bucket reach eight
    # quarters and not twenty-four months.
    assert grains.estimate(600, 200) == 346
    assert grains.walk_holds(grains.Grain("quarter", reading, 600, spans[:2], "day", 200), FLOOR)
    assert not grains.walk_holds(grains.Grain("month", reading, 600, spans, "day", 200), FLOOR)
    assert grains.walk_holds(grains.Grain("month", reading, 600, spans, "day", 600), FLOOR)
    assert not grains.walk_holds(grains.Grain("quarter", reading, 600, spans[:2], "day", 600), FLOOR)
    assert grains.walk_holds(grains.Grain(grains.HELD, reading, 600, spans, "day", 600), FLOOR)
    assert grains.walk_holds(grains.Grain(grains.HELD, reading, 600, (), "day", 0), FLOOR)
    assert not grains.walk_holds(grains.Grain("day", reading, 600, spans, "day", 600), FLOOR)


# -- (6) clocks, stamps and counted dates ------------------------------------


def test_clock_times_are_pooled_by_the_hour_and_parse(tmp_path: pathlib.Path) -> None:
    text = _clocks(1200, 400, 29)
    described = _profiled(tmp_path, "theatre", text, "--identifier", "patient")
    grain = _block(described, "start")["time_grain"]
    assert isinstance(grain, dict) and grain["rung"] in ("hour", "four hours"), grain
    twin, real = _generated_and_validated(tmp_path, "theatre")
    assert (twin, real) == (set(), set())
    cells = _column(tmp_path / "theatre-twin.csv", "start")
    assert _parses(cells, "%H:%M") == 0
    assert len({cell[3:5] for cell in cells}) > 10
    assert _counted_few(tmp_path, "theatre") == 0


def test_the_draw_is_the_oracles() -> None:
    """Method G7.13: the product's draw inside a bucket is the oracle's, word for word."""
    # The oracle as the witnesses' test runs it (one route that runs it,
    # `tests/test_version_reach.py`'s ROUTES_THAT_RUN_SOURCE).
    from test_oracle_rule_witnesses import ORACLE_MODULE as module

    draw = random.Random(41)
    cases = (
        ("03/01/2024", "month-first-date", grains.DATE, "month"),
        ("01/01/2024", "month-first-date", grains.DATE, "year"),
        ("01/03/2024", "day-first-date", grains.DATE, "month"),
        ("2024-04-01", "iso-date", grains.DATE, "quarter"),
        ("2024-05-01T08:00:00", "iso-datetime", grains.STAMP, "hour"),
        ("2024-05-01 00:00", "iso-datetime", grains.STAMP, "day"),
        ("08:00", "hh-mm", grains.CLOCK, "hour"),
        ("08:00:00", "hh-mm-ss", grains.CLOCK, "four hours"),
        ("45108", "excel-1900", grains.COUNTED, "month"),
    )
    for cell, member, kind, rung in cases:
        for _one in range(60):
            word = draw.getrandbits(64)
            product = grains.drawn_inside(cell, grains.Reading(kind, member), rung, word)
            assert product == module.pooled_drawn_inside(cell, member, rung, word), (cell, rung, word)


@pytest.mark.parametrize(
    ("cell", "member", "kind"),
    (
        ("41/91/5463", "month-first-date", grains.DATE),
        ("4191-54-63", "iso-date", grains.DATE),
        ("4191-54-63Q77:21:93", "iso-datetime", grains.STAMP),
        ("4191-54-63 77:21:93.123-91:37", "iso-datetime", grains.STAMP),
        ("77:21", "hh-mm", grains.CLOCK),
        ("77:21 QX", "hh-mm AM-PM", grains.CLOCK),
        ("Qzr 41, 5463", "textual-month-first-date", grains.DATE),
        ("91537", "excel-1900", grains.COUNTED),
    ),
)
def test_a_made_up_cell_is_filled_with_a_valid_value_in_its_layout(cell: str, member: str, kind: str) -> None:
    """The G1 floor's fill keeps every run's width and reads under the member, from the fixed span."""
    reading = grains.Reading(kind, member)
    taken: "dict[str, bool]" = {}
    for word in (1, 2**62, 2**63, 2**64 - 1):
        made = grains.filled(cell, reading, word, grains.fixed_span(kind), True, taken)
        assert made is not None and made not in taken
        taken[made] = True
        assert len(made) == len(cell)
        assert grains.moment_of(made, reading) is not None
        if kind != grains.CLOCK:
            moment = grains.moment_of(made, reading)
            first, end = grains.fixed_span(kind)
            assert moment is not None and first <= moment < end


def test_a_table_with_no_subject_column_carries_no_grain(tmp_path: pathlib.Path) -> None:
    """Byte identity's ground: without a repeating subject column nothing is counted, nothing pooled."""
    text = _visits(600, 200, datetime.date(2023, 1, 1), 730, 7)
    lines = text.splitlines()
    alone = "\n".join([f"{line.split(',')[1]},{line.split(',')[2]}" for line in lines]) + "\n"
    described = _profiled(tmp_path, "alone", alone)
    assert "time_grain" not in json.dumps(described)
    assert _block(described, "seen")["role"] == "datetime"
    keyed = "\n".join([lines[0]] + [f"REC{90000000 + place},{line.split(',', 1)[1]}"
                                    for place, line in enumerate(lines[1:])]) + "\n"
    described = _profiled(tmp_path, "keyed", keyed, "--identifier", "patient")
    assert "time_grain" not in json.dumps(described)


def test_the_twin_is_one_function_of_the_description_and_the_seed(tmp_path: pathlib.Path) -> None:
    """Two runs at one seed write one twin; the grain's words move no column before the grained one."""
    text = _visits(600, 200, datetime.date(2023, 1, 1), 730, 7)
    _profiled(tmp_path, "visits", text, "--identifier", "patient")
    loaded = contract.load_profile(f"{tmp_path / 'visits-profile.json'}")
    first = generation.generate(loaded, 5)
    second = generation.generate(loaded, 5)
    assert first.columns == second.columns
    plan = generation.plan_generation(loaded)
    assert first.words_drawn == plan.words_planned
