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
the record's spans a walk its facts allow (the loader refuses any other);
the product's draw equal to the oracle's (method G7.13); the contract's
refusals; and, red on their mutants (`wave6/PS/mutants.log`): rows counted
for people, a point at a grain fewer than eleven people hold, a twin cell
that does not parse, the grain chosen from failing points, a tail published
as itself.

REPAIR ROUND 1 (the lane's two skeptics): no count of one to ten people is
left to subtraction -- a bucket inside the span, the unread cells, a
written form or offset -- and the walk steps back a rung where the rung it
reached cannot keep that; the finer span's own buckets and its reach of
the coarser ends choose the walk; TG1 refusals by their own rule, written
canonically; the G1 floor for stand-ins no date wears. Each case below is
red on its one-edit mutant (`wave6/PS/r1/mut_r1.py`, `mutants-r1b.log`):
rows_for_people, thin_off, unread_off, forms_off, stepped_keeps_finer_spans,
reach_off, span_of_the_coarser_rung, filler_fallback_off, length_refill_off,
held_ignores_spans, loader_accepts_any_rung and the build's eight.

REPAIR ROUND 2 (the combined verify and Codex's review): an absent date
stays absent; a held column draws from the first span wide enough for its
count; a published layout no date wears stays made up, and a length no
valid date wears is named in the twin's report; the count at the rung
never moves a tail's row; TG1 bounds the people by the rows; the offset,
pinned, and the counter written apart keyed by offset and shape. Red on
`wave6/PS/r2/mut_r2.py`'s mutants (`mutants-r2.log`): offset_off,
unread_one_key, population_unbounded, absent_read_as_moment,
redescription_reads_absent, validator_reads_absent,
coarse_keeps_absent_off, span_chain_off, published_form_kept_off,
measured_before_conversion, g1_length_reason_off, fences_off,
protections_skip_boundary, unpadded_off, counter_nobody_off and
counter_offset_off, beside the verify's list.

REPAIR ROUND 3 (the second verify): a date for nobody that three people
write stays absent in the validator; a held column's spans hold its
published count, measured at its finest written detail, the fixed span
widened by whole decades; the repeat in the last span pinned; the twin's
report on an absent date names no deviation. Red on
`wave6/PS/r3/mut_r3.py`'s mutants (`mutants-r3.log`, `mutants-r3b.log`):
absent_read_dropped, validator_absent_read_off,
redescription_reads_coarse, repeat_off, fixed_unwidened,
capacity_in_days, room_of_one, count_from_the_cells and
gen_recount_holes_off.
"""

from __future__ import annotations

import contextlib
import csv
import dataclasses
import datetime
import io
import json
import pathlib
import random

import pytest

from synthtwin import cli, contract, errors, generation, grains, validation

import fixtures
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
    # The dates' own counts: the record numbers' final pass (P4-D432) moves
    # cells of the held values' dense layouts, which the identifier gate holds.
    fixtures.profile_without_exclusions(folder / f"{stem}-profile.json")
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
    """Three patients hold 300 rows of June 2023 and nobody else: no point names June, and the twin parses.

    The walk reaches the month (1,500 rows of about 400 people), where
    June would be the column's commonest point, held by three people: the
    month is refused and the walk steps back to the quarter (repair round
    1), whose every bucket the floor's number of people hold.
    """
    june = [(950 + one % 3, datetime.date(2023, 6, 10 + one % 5)) for one in range(300)]
    text = _visits(1200, 400, datetime.date(2023, 1, 1), 730, 17, "iso", [])
    lines = text.splitlines()
    kept = [lines[0]] + [line for line in lines[1:] if line.split(",")[1][:7] != "2023-06"]
    draw = random.Random(3)
    for person, day in june:
        kept += [f"REC{80000000 + 7 * person:08d},{day.isoformat()},{draw.uniform(3, 150):.1f}"]
    described = _profiled(tmp_path, "visits", "\n".join(kept) + "\n", "--identifier", "patient")
    block = _block(described, "seen")
    shown = json.dumps(block)
    assert "2023-06" not in shown, shown
    assert block["role"] == "datetime" and block["time_grain"]["rung"] == "quarter", block["time_grain"]
    assert [span[0] for span in block["time_grain"]["spans"]] == ["year", "quarter"]
    twin, real = _generated_and_validated(tmp_path, "visits")
    assert (twin, real) == (set(), set())
    assert _parses(_column(tmp_path / "visits-twin.csv", "seen"), "%Y-%m-%d") == 0
    assert _counted_few(tmp_path, "visits") == 0


def _years_apart(written: str) -> str:
    """Four years of 200 patients' visits, 2041 to 2045, and between them 2043 held by three patients alone."""
    draw = random.Random(31)
    lines = ["patient,seen,value"]
    for _row in range(600):
        year = draw.choice((2041, 2042, 2044, 2045))
        day = datetime.date(year, 1, 1) + datetime.timedelta(days=draw.randrange(365))
        lines += [f"REC{80000000 + 7 * draw.randrange(200):08d},{day.strftime(written)},{draw.uniform(3, 150):.1f}"]
    for one in range(15):
        day = datetime.date(2043, 3 + one % 3, 2 + one)
        lines += [f"REC{80000000 + 7 * (900 + one % 3):08d},{day.strftime(written)},{draw.uniform(3, 150):.1f}"]
    return "\n".join(lines) + "\n"


def test_a_held_column_writes_valid_dates_from_its_spans(tmp_path: pathlib.Path) -> None:
    """The G1 floor: where no rung serves, the held column's twin parses in its own layout, inside its record's last span.

    2043 lies inside the years' span and three patients alone hold it, so
    every rung is thin and the column is held; its twin draws inside the
    span its record publishes (2041 to 2045), never the method's fixed
    span (2000 to 2029), and never prints 2043.
    """
    described = _profiled(tmp_path, "visits", _years_apart("%m/%d/%Y"), "--identifier", "patient")
    block = _block(described, "seen")
    assert block["role"] == "identifier" and block["time_grain"]["rung"] == grains.HELD
    assert any("drawn inside the last span" in f"{remark}" for remark in block["remarks"])
    assert "2043" not in json.dumps(block)
    loaded = contract.load_profile(f"{tmp_path / 'visits-profile.json'}")
    record = [one for one in loaded.columns if one.name == "seen"][0].time_grain
    assert record is not None and record.spans
    # The record's own last span, read apart from `grains.held_span`.
    rung, first, last = record.spans[-1]
    end = grains.after(last, rung)
    assert grains.span_text(first, grains.DATE)[:4] == "2041" and grains.span_text(last, grains.DATE)[:4] == "2045"
    twin, _real = _generated_and_validated(tmp_path, "visits")
    assert twin == set()
    cells = _column(tmp_path / "visits-twin.csv", "seen")
    assert _parses(cells, "%m/%d/%Y") == 0, cells[:5]
    for cell in cells:
        moment = grains.moment_of(cell, record.reading)
        assert moment is not None and first <= moment < end, (cell, record.spans)
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
    """TG1: a description whose grain record its own rows, people and spans do not allow is not loaded.

    Each edit is written in the canonical form (`fixtures.write_profile`), so
    the record's own rule refuses it, by its name, and not the form check
    (the skeptic's item 4); and a refusal is a ProfileError, never a
    KeyError.
    """
    text = _visits(1200, 400, datetime.date(2023, 1, 1), 730, 7)
    _profiled(tmp_path, "visits", text, "--identifier", "patient")
    path = tmp_path / "visits-profile.json"
    original = json.loads(path.read_text(encoding="utf-8"))
    assert _block(original, "seen")["time_grain"]["rung"] == "month"
    changes = {
        "finer": "TG1", "mismatched": "TG1", "unreached": "TG1", "rows": "TG1", "people": "TG1",
        "start": "TG1", "held": "NF129", "reading": "NF128", "population": "TG1",
    }
    for change, rule in changes.items():
        document = json.loads(json.dumps(original))
        grain = _block(document, "seen")["time_grain"]
        if change == "finer":
            grain["spans"] += [["day", "2023-01-01", "2024-12-31"]]
            grain["rung"] = "day"
        elif change == "mismatched":
            grain["rung"] = "quarter"
        elif change == "unreached":
            grain["spans"][2][1] = "2023-04-01"
        elif change == "rows":
            grain["rows"] = 1199
        elif change == "people":
            grain["people"] = 200
        elif change == "population":
            # Codex's item 5 (repair round 2): more people than the table's rows.
            grain["people"] = 1000000
        elif change == "held":
            grain["rung"] = grains.HELD
        elif change == "reading":
            grain["reading"] = "month-first-date"
        else:
            grain["spans"][2][1] = "2023-01-02"
        fixtures.write_profile(tmp_path, "visits-profile.json", document)
        with pytest.raises(errors.ProfileError) as refused:
            contract.load_profile(f"{path}")
        assert rule in f"{refused.value}", (change, f"{refused.value}")
    # ...and the very document written back loads, so the form check is not what refused.
    fixtures.write_profile(tmp_path, "visits-profile.json", original)
    contract.load_profile(f"{path}")


def test_the_walk_reads_its_record_alone() -> None:
    """`walk_holds` checks every span the record publishes from the rows, the people and the spans alone.

    Each finer span must reach both ends of the one before and hold at
    most the estimate's buckets at two floors a bucket; the rung is the
    last span's. Where the walk stopped is not checked: a record that
    stops above where its spans would let it go is the step back, which
    publishes nothing of why (plan P4-D417, repair round 1).
    """
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
    # The step back: a record stopping above where its spans would go.
    assert grains.walk_holds(grains.Grain("quarter", reading, 600, spans[:2], "day", 600), FLOOR)
    assert grains.walk_holds(grains.Grain(grains.HELD, reading, 600, spans, "day", 600), FLOOR)
    assert grains.walk_holds(grains.Grain(grains.HELD, reading, 600, (), "day", 0), FLOOR)
    assert not grains.walk_holds(grains.Grain("day", reading, 600, spans, "day", 600), FLOOR)
    assert not grains.walk_holds(grains.Grain("quarter", reading, 600, spans, "day", 600), FLOOR)
    # A finer span that does not reach the coarser one's ends is refused:
    # its tails would leave the end buckets the coarser rung pools them in.
    short = (spans[0], ("quarter", grains.start_of(first + 400 * day, "quarter"), spans[1][2]))
    assert not grains.walk_holds(grains.Grain("quarter", reading, 600, short, "day", 600), FLOOR)
    # The finer span's OWN buckets are what the estimate covers: one day
    # inside a month of a year (the statistics skeptic's item 2).
    session = (("year", first, first), ("quarter", first, first), ("month", first, first),
               ("day", first, first))
    assert grains.walk_holds(grains.Grain("day", reading, 60, session, "day", 10), FLOOR)
    assert grains.walk_holds(grains.Grain("day", reading, 25, session, "day", 25), FLOOR)
    assert not grains.walk_holds(grains.Grain("day", reading, 21, session, "day", 21), FLOOR)


# -- (5b) repair round 1: what the description at a rung may not name -------


def _hole(rows_in_july: int) -> str:
    """Two hundred patients' ten visits a month apart over 2022 and 2023, July 2022 held by ``rows_in_july`` of them."""
    draw = random.Random(2)
    lines = ["patient,seen"]
    months = [(2022 + month // 12, 1 + month % 12) for month in range(24)]
    for person in range(200):
        for _visit in range(10):
            year, month = months[draw.randrange(24)]
            while (year, month) == (2022, 7):
                year, month = months[draw.randrange(24)]
            lines += [f"P{100000 + person},{year}-{month:02d}-{1 + draw.randrange(28):02d}"]
    for one in range(rows_in_july):
        lines += [f"P{100000 + one},2022-07-{10 + one:02d}"]
    return "\n".join(lines) + "\n"


def _buckets_held(path: pathlib.Path, name: str, grain: "dict[str, object]") -> "dict[str, set[str]]":
    """The people each bucket at a record's rung holds, read apart from the product (`persons_counted`)."""
    names = _column(path, "patient")
    cells = _column(path, name)
    held: "dict[str, set[str]]" = {}
    for cell, person in zip(persons_counted.at_the_grain(cells, {"time_grain": grain}), names):
        if cell:
            held.setdefault(cell, set()).add(person)
    return held


@pytest.mark.parametrize("rows_in_july", (1, 10))
def test_a_bucket_inside_the_span_a_few_people_hold_is_never_named(
    tmp_path: pathlib.Path, rows_in_july: int
) -> None:
    """July 2022 holds one (or ten) patients: the month would name it by subtraction, so the walk steps back to the quarter.

    At the month every other month holds the floor's number of rows and is
    listed among the heavy dates, the count of different values says July
    holds someone, and its rows are the present rows less every listed
    count (the skeptic's item 1, b1.csv and b10.csv). Every bucket at the
    rung the description takes holds the floor's number of people.
    """
    text = _hole(rows_in_july)
    described = _profiled(tmp_path, "visits", text, "--identifier", "patient")
    block = _block(described, "seen")
    grain = block["time_grain"]
    assert grain["rung"] == "quarter", grain
    assert [span[0] for span in grain["spans"]] == ["year", "quarter"]
    held = _buckets_held(tmp_path / "visits.csv", "seen", grain)
    assert held and min(len(people) for people in held.values()) >= FLOOR, {
        bucket: len(people) for bucket, people in held.items()}
    assert all(point["date"][5:7] in ("01", "04", "07", "10") for point in block["heavy_dates"])
    twin, real = _generated_and_validated(tmp_path, "visits")
    assert (twin, real) == (set(), set())
    assert _counted_few(tmp_path, "visits") == 0


def test_a_quarter_three_people_hold_steps_the_stamps_back_to_the_year(tmp_path: pathlib.Path) -> None:
    """Stamps over eight quarters, 2022's fourth held by three patients: the quarter is refused, the year serves (q.csv)."""
    draw = random.Random(5)
    lines = ["patient,seen"]
    for _row in range(600):
        quarter = draw.choice((0, 1, 2, 4, 5, 6, 7))
        day = datetime.date(2022 + quarter // 4, 3 * (quarter % 4) + 1, 1) + datetime.timedelta(
            days=draw.randrange(88))
        lines += [f"P{100000 + draw.randrange(100)},{day.isoformat()} {draw.randint(0, 23):02d}:{draw.randint(0, 59):02d}"]
    for one in range(3):
        lines += [f"P{100000 + one},2022-{10 + one}-{10 + one} 10:00"]
    described = _profiled(tmp_path, "visits", "\n".join(lines) + "\n", "--identifier", "patient")
    grain = _block(described, "seen")["time_grain"]
    assert grain["rung"] == "year" and len(grain["spans"]) == 1, grain
    assert "2022-10" not in json.dumps(described)
    twin, real = _generated_and_validated(tmp_path, "visits")
    assert (twin, real) == (set(), set())
    assert _parses(_column(tmp_path / "visits-twin.csv", "seen"), "%Y-%m-%d %H:%M") == 0
    assert _counted_few(tmp_path, "visits") == 0


def _two_writings(person_rows: int, people: int, stamp: str) -> str:
    """Two hundred patients' dates; ``people`` of them write ``person_rows`` rows a person as ``stamp`` does instead."""
    draw = random.Random(9)
    lines = ["patient,seen"]
    for person in range(200):
        for _visit in range(10):
            day = datetime.date(2022, 1, 1) + datetime.timedelta(days=draw.randrange(730))
            if person < people and _visit < person_rows:
                lines += [f"P{100000 + person},{day.strftime(stamp)}"]
            else:
                lines += [f"P{100000 + person},{day.isoformat()}"]
    return "\n".join(lines) + "\n"


def test_cells_no_date_reads_that_one_person_writes_hold_the_column(tmp_path: pathlib.Path) -> None:
    """One patient writes ten stamps beside 1,990 dates: the ten read as no date at any rung, a count one person holds (m1.csv).

    Every description of the column publishes them as `n_unparsed`, so no
    rung serves and the column is held, its twin valid dates.
    """
    described = _profiled(tmp_path, "visits", _two_writings(10, 1, "%Y-%m-%d %H:%M"),
                          "--identifier", "patient")
    block = _block(described, "seen")
    assert block["role"] == "identifier" and block["time_grain"]["rung"] == grains.HELD, block.get("time_grain")
    twin, _real = _generated_and_validated(tmp_path, "visits")
    assert twin == set()
    assert _counted_few(tmp_path, "visits") == 0


def test_a_written_member_three_people_hold_is_never_counted(tmp_path: pathlib.Path) -> None:
    """Three patients write their thirty visits with a clock beside 1,970 dates: `resolution_mix` would count them (m2.csv).

    The joint column's two members are each counted in people; one that
    one to ten people hold leaves no rung serving, and the column is held.
    """
    described = _profiled(tmp_path, "visits", _two_writings(10, 3, "%Y-%m-01 08:00"),
                          "--identifier", "patient")
    block = _block(described, "seen")
    assert block["role"] == "identifier" and block["time_grain"]["rung"] == grains.HELD, block.get("time_grain")
    assert "resolution_mix" not in block or "iso-datetime" not in block["resolution_mix"]
    twin, _real = _generated_and_validated(tmp_path, "visits")
    assert twin == set()
    assert _counted_few(tmp_path, "visits") == 0


@pytest.mark.parametrize(
    ("written", "census", "entry"),
    (
        ("%Y-%m-%dT%H:%M", "datetime_separators", "upper_t"),
        ("{year}-{month}-{day} %H:%M", "date_field_widths", "unpadded"),
    ),
)
def test_a_written_form_three_people_use_is_never_counted(
    tmp_path: pathlib.Path, written: str, census: str, entry: str
) -> None:
    """Three patients write their stamps with a `T`, or with fields of one figure: no census of the column's written forms counts them.

    At the month every bucket holds the floor, but `datetime_separators`
    and `date_field_widths` would count the three patients' thirty rows
    (repair round 1: the skeptic's item 2, met wherever a census counts
    how a date is written). Every written shape is counted in people; one
    that one to ten people write leaves no rung serving.
    """
    draw = random.Random(9)
    lines = ["patient,seen"]
    for person in range(200):
        for _visit in range(10):
            when = datetime.datetime(2022, 1, 1) + datetime.timedelta(minutes=draw.randrange(730 * 1440))
            text = when.strftime("%Y-%m-%d %H:%M")
            if person < 3:
                text = when.strftime(written.format(year=when.year, month=when.month, day=when.day))
            lines += [f"P{100000 + person},{text}"]
    described = _profiled(tmp_path, "visits", "\n".join(lines) + "\n", "--identifier", "patient")
    block = _block(described, "seen")
    assert block["role"] == "identifier" and block["time_grain"]["rung"] == grains.HELD, block.get("time_grain")
    assert entry not in json.dumps(block.get(census, {}))
    twin, _real = _generated_and_validated(tmp_path, "visits")
    assert twin == set()
    # The G1 floor: every twin cell reads under the record's reading, even
    # where every layout is withheld and the made-up cells no date wears.
    loaded = contract.load_profile(f"{tmp_path / 'visits-profile.json'}")
    record = [one for one in loaded.columns if one.name == "seen"][0].time_grain
    assert record is not None
    cells = _column(tmp_path / "visits-twin.csv", "seen")
    assert [cell for cell in cells if grains.moment_of(cell, record.reading) is None] == []
    assert _counted_few(tmp_path, "visits") == 0


def test_the_walks_ends_are_counted_in_people_never_in_rows(tmp_path: pathlib.Path) -> None:
    """One patient's thirty rows of 2019 and three patients' forty-five of 2025 never end a span (a.csv).

    Counted in rows each would hold the floor and end the years' span;
    counted in people neither does, so they are pooled into 2022 and 2023.
    """
    text = _visits(2000, 200, datetime.date(2022, 1, 1), 730, 37, "iso")
    lines = text.splitlines()
    for one in range(30):
        lines += [f"REC{80000000 + 7 * 990:08d},2019-0{1 + one % 9}-1{one % 10},5.0"]
    for one in range(45):
        lines += [f"REC{80000000 + 7 * (991 + one % 3):08d},2025-03-{1 + one % 28:02d},5.0"]
    described = _profiled(tmp_path, "visits", "\n".join(lines) + "\n", "--identifier", "patient")
    grain = _block(described, "seen")["time_grain"]
    named = json.dumps(grain["spans"])
    assert "2019" not in named and "2025" not in named, grain["spans"]
    assert grain["spans"][0][1:] == ["2022-01-01", "2023-01-01"], grain["spans"]
    assert "2019" not in json.dumps(described) and "2025-" not in json.dumps(described)
    twin, real = _generated_and_validated(tmp_path, "visits")
    assert (twin, real) == (set(), set())
    assert _counted_few(tmp_path, "visits") == 0


def test_a_rung_no_bucket_of_which_holds_the_floor_leaves_the_year(tmp_path: pathlib.Path) -> None:
    """Twelve patients a year over ten years, three a quarter: no quarter holds the floor, so the years describe the column (f.csv).

    The walk stops where the finer rung has no span (the step back the
    plan's proof covers, repair round 1); every year holds twelve people,
    and the description loads and validates.
    """
    draw = random.Random(43)
    lines = ["patient,seen"]
    for year in range(10):
        for quarter in range(4):
            for one in range(3):
                person = 100000 + year * 12 + quarter * 3 + one
                for _visit in range(100):
                    day = datetime.date(2014 + year, 3 * quarter + 1, 1) + datetime.timedelta(days=draw.randrange(89))
                    lines += [f"P{person},{day.isoformat()}"]
    described = _profiled(tmp_path, "visits", "\n".join(lines) + "\n", "--identifier", "patient")
    block = _block(described, "seen")
    grain = block["time_grain"]
    assert block["role"] == "datetime" and grain["rung"] == "year", grain
    assert grain["spans"] == [["year", "2014-01-01", "2023-01-01"]]
    loaded = contract.load_profile(f"{tmp_path / 'visits-profile.json'}")
    record = [one for one in loaded.columns if one.name == "seen"][0].time_grain
    assert record is not None and grains.walk_holds(record, FLOOR)
    twin, real = _generated_and_validated(tmp_path, "visits")
    assert (twin, real) == (set(), set())
    assert _counted_few(tmp_path, "visits") == 0


def test_a_seventy_minute_session_is_described_by_the_hour(tmp_path: pathlib.Path) -> None:
    """A wearable's 70-minute session to the second: the finer span's own buckets choose the hour (statistics item 2).

    Counted over the day's 24 hours the walk stopped at the day, and the
    twin spread the session over the whole day (the zoo's wearables, day
    and hour TVD 0.96 and 0.90 at 600 rows); counted over its own two
    hours the walk reaches the hour, and the twin stays inside them.
    """
    draw = random.Random(47)
    lines = ["patient,ts"]
    start = datetime.datetime(2024, 5, 1, 8, 0, 1)
    for _row in range(600):
        when = start + datetime.timedelta(seconds=draw.randrange(70 * 60 - 7))
        lines += [f"P{100000 + draw.randrange(120)},{when.strftime('%Y-%m-%d %H:%M:%S')}"]
    _profiled(tmp_path, "session", "\n".join(lines) + "\n", "--identifier", "patient")
    described = json.loads((tmp_path / "session-profile.json").read_text(encoding="utf-8"))
    grain = _block(described, "ts")["time_grain"]
    assert grain["rung"] == "hour", grain
    twin, real = _generated_and_validated(tmp_path, "session")
    assert (twin, real) == (set(), set())
    cells = _column(tmp_path / "session-twin.csv", "ts")
    assert _parses(cells, "%Y-%m-%d %H:%M:%S") == 0
    assert all("2024-05-01 08:00:00" <= cell <= "2024-05-01 09:59:59" for cell in cells), (min(cells), max(cells))


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


# -- (5) the count of different values, met at the rung ----------------------


def _months_of_years(years: int, patients_a_year: int, seed: int) -> str:
    """Each year from 1990 its own patients, each with two months of treatment written `%Y-%m`."""
    draw = random.Random(seed)
    lines = ["patient,first_month,value"]
    for year in range(years):
        for one in range(patients_a_year):
            person = year * patients_a_year + one
            for _visit in range(2):
                lines += [
                    f"REC{80000000 + 7 * person:08d},{1990 + year}-{draw.randint(1, 12):02d},"
                    f"{draw.uniform(3, 150):.1f}"
                ]
    return "\n".join(lines) + "\n"


def test_a_column_written_to_the_month_holds_its_count_of_years(tmp_path: pathlib.Path) -> None:
    """A month column pooled by the year meets every count: its twin writes as many years as it publishes.

    Thirty years of fifteen patients each: every year holds the floor, no
    quarter does, so the column is described by the year. The
    description's machinery builds its count of different values by the
    month, and two built months of one year once left the twin years short
    (the catalogue's tumor registry, 23 of 29, K-S3-65 on lane PS's first
    head); the rows moved to the empty years between the same two
    published points meet it (method G7.13).
    """
    described = _profiled(tmp_path, "registry", _months_of_years(30, 15, 41), "--identifier", "patient")
    block = _block(described, "first_month")
    assert block["time_grain"]["rung"] == "year", block["time_grain"]
    twin, real = _generated_and_validated(tmp_path, "registry")
    assert (twin, real) == (set(), set())
    years = {cell[:4] for cell in _column(tmp_path / "registry-twin.csv", "first_month")}
    assert len(years) == block["n_distinct"] == 30
    assert _parses(_column(tmp_path / "registry-twin.csv", "first_month"), "%Y-%m") == 0


def test_the_tumor_registrys_month_column_is_held_and_parses(tmp_path: pathlib.Path) -> None:
    """The catalogue's tumor registry, unanswered: 32 people over 29 years leave years inside the span that one to ten hold.

    So no rung serves (the skeptic's item 1: a bucket inside the span is
    named by the count of different values and its rows by subtraction),
    the column is held, and its twin still parses as `%Y-%m`.
    """
    table = [one for one in health_zoo.runnable_tables() if one.name == "tumor_registry"][0]
    place = [one.name for one in health_zoo.runnable_tables()].index("tumor_registry")
    path = pathlib.Path(health_zoo.write_table(table, tmp_path, 600, 20261016 + place))
    screen = io.StringIO()
    with shapes.nobody_at_the_keyboard():
        with contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
            assert cli.main(["profile", f"{path}", "--out-dir", f"{tmp_path}", "--replace"]) == 0
    described = json.loads((tmp_path / "tumor_registry-profile.json").read_text(encoding="utf-8"))
    grain = _block(described, "first_treatment_month")["time_grain"]
    assert isinstance(grain, dict) and grain["rung"] == grains.HELD, grain
    twin, _real = _generated_and_validated(tmp_path, "tumor_registry")
    assert "first_treatment_month" not in twin, twin
    cells = _column(tmp_path / "tumor_registry-twin.csv", "first_treatment_month")
    assert _parses(cells, "%Y-%m") == 0, cells[:5]


def test_the_count_at_the_rung_is_the_oracles() -> None:
    """Method G7.13's count at the rung: the product's moved rows are the oracle's, row for row."""
    from test_oracle_rule_witnesses import ORACLE_MODULE as module

    def moment(when: datetime.datetime) -> int:
        made = grains.canonical_moment(when.strftime("%Y-%m-%d %H:%M:%S"), "datetime")
        assert made is not None
        return made

    draw = random.Random(43)
    shapes_of = (
        ("year", grains.DATE, "month", datetime.datetime(1995, 1, 1)),
        ("year", grains.DATE, "day", datetime.datetime(2001, 1, 1)),
        ("month", grains.DATE, "day", datetime.datetime(2023, 1, 1)),
        ("quarter", grains.COUNTED, "day", datetime.datetime(2019, 1, 1)),
        ("day", grains.STAMP, "minute", datetime.datetime(2024, 2, 1)),
        ("hour", grains.STAMP, "second", datetime.datetime(2024, 5, 1, 6)),
        ("hour", grains.CLOCK, "minute", datetime.datetime(2000, 1, 1)),
    )
    moves = 0
    for _case in range(150):
        rung, kind, finest, base = shapes_of[draw.randrange(len(shapes_of))]
        starts = [base]
        for _one in range(draw.randint(4, 60)):
            starts += [module.pooled_bucket(starts[-1], rung)[1]]
        held = sorted(draw.sample(starts, draw.randint(2, len(starts))))
        cells: "list[datetime.datetime | None]" = []
        for bucket in held:
            cells += [bucket] * draw.choice((1, 1, 2, 3, 7))
        cells += [None] * draw.randint(0, 3)
        draw.shuffle(cells)
        points = sorted(draw.sample(held, draw.randint(0, min(6, len(held)))))
        below: "dict[datetime.datetime, int]" = {}
        seen = 0
        for bucket in held:
            below[bucket] = seen
            seen += cells.count(bucket)
        pinned: "dict[datetime.datetime, tuple[int, int]]" = {}
        for point in points:
            if draw.random() < 0.7:
                low = below[point] + draw.randrange(cells.count(point))
                pinned[point] = (low, draw.randint(low, below[point] + cells.count(point) - 1))
        target = len(held) + draw.randint(1, 12)
        first, last = starts[0], starts[-1]
        # Repair round 2: a tail's fences, at a published point or none.
        fences: "tuple[datetime.datetime | None, datetime.datetime | None]" = (None, None)
        if points and draw.random() < 0.5:
            fences = (points[0] if draw.random() < 0.7 else None, points[-1] if draw.random() < 0.7 else None)
        product = grains.count_filled(
            [None if cell is None else moment(cell) for cell in cells],
            [moment(point) for point in points], (moment(first), moment(last)), rung, kind,
            finest, target, {moment(point): ranks for point, ranks in pinned.items()},
            (None if fences[0] is None else moment(fences[0]), None if fences[1] is None else moment(fences[1])),
        )
        oracle = module.pooled_count_filled(cells, points, first, last, rung, kind, finest, target, pinned, fences)
        assert product == {row: moment(start) for row, start in oracle.items()}, (rung, kind, finest)
        moves += len(product)
    assert moves > 100


# -- repair round 2 (the combined verify's items 1 to 4, Codex's items 1 to 5) --


def test_an_offset_few_people_write_is_never_printed(tmp_path: pathlib.Path) -> None:
    """The verify's item 1: three patients' `+05:30` beside 297 patients' `+00:00` is printed nowhere.

    The walk counts each offset in people with the stamps' written shapes
    (`_grain_walk`'s shaped key); the counter written apart keys each
    readable cell by its offset and its shape too, so K-S3-65 sees the
    route (red on `offset_off` either way).
    """
    described = _profiled(tmp_path, "offs", persons_counted.offset_stamps_table(), "--identifier", "patient")
    block = _block(described, "event_ts")
    # The counter first: on `offset_off` it names the offset by itself.
    assert _counted_few(tmp_path, "offs") == 0, block.get("utc_offsets")
    assert "+05:30" not in json.dumps(block), block.get("utc_offsets")
    twin, _real = _generated_and_validated(tmp_path, "offs")
    assert "event_ts" not in twin, twin
    assert _parses(_column(tmp_path / "offs-twin.csv", "event_ts"), "%Y-%m-%dT%H:%M:%S%z") == 0


def test_a_published_layout_no_date_wears_is_written_as_made_up(tmp_path: pathlib.Path) -> None:
    """The verify's item 2: twelve people's `pending` beside ISO dates keeps its published layout on the twin.

    The column is held (three people's `NOT DONE YET`); the made-up cells of
    the layout `&&&&&&&` no date wears stand for real cells that do not
    read either and leave as made up, every other cell is a valid date, and
    the one miss left is the longest length, a withheld form's, named in
    the twin's report as the G1 floor's limit (P4-D417, repair round 2).
    Since plan P4-D432 the made-up cells of `&&&&&&&` are spelled inside
    that layout's excluded template, so none is a real cell's spelling; a
    column of dates at a grain gives nothing else up (method G9.6b).
    """
    described = _profiled(tmp_path, "unread", persons_counted.unread_dates_table(), "--identifier", "patient")
    block = _block(described, "visit_date")
    assert block["role"] == "identifier" and block["layout_forms"].get("&&&&&&&") == 12, block["layout_forms"]
    quiet = io.StringIO()
    with contextlib.redirect_stdout(quiet), contextlib.redirect_stderr(quiet):
        assert cli.main(["generate", f"{tmp_path / 'unread-profile.json'}", "--out-dir", f"{tmp_path}",
                         "--seed", "0", "--replace"]) == 0
    cells = _column(tmp_path / "unread-twin.csv", "visit_date")
    unread = [cell for cell in cells if _parses([cell], "%Y-%m-%d")]
    assert len(unread) == 12 and all(len(cell) == 7 and cell.isalpha() for cell in unread), unread
    outcome = validation.measure(contract.load_profile(f"{tmp_path / 'unread-profile.json'}"),
                                 f"{tmp_path / 'unread-twin.csv'}")
    missed = sorted({f"{check.subcheck}" for check in outcome.checks if check.verdict == validation.MISSED})
    assert missed == ["length.max"], missed
    assert "max_length" in (tmp_path / "unread-twin-report.txt").read_text(encoding="utf-8")
    # ...and every made-up cell of `&&&&&&&` wears the layout's excluded template (plan P4-D432).
    written = block["layout_exclusions"]["&&&&&&&"]
    place = [at for at in range(7) if written[at] != "&"][0]
    assert all(cell[place] == written[place] for cell in unread), (written, unread)


@pytest.mark.parametrize("shape", ("pending", "short"))
def test_a_length_no_valid_date_wears_is_named_in_the_twins_report(tmp_path: pathlib.Path, shape: str) -> None:
    """The verify's item 2 (`pending`, three people) and Codex's item 4 (one cell `x`): the report names the length.

    The G1 floor writes valid dates, and no valid ISO date is seven or one
    character long: `validate` misses `min_length`, and the twin's own
    report, measured on the cells as they leave, names the same miss.
    """
    text = persons_counted.unread_dates_table(3, 0) if shape == "pending" else persons_counted.one_short_cell_table()
    column = "visit_date" if shape == "pending" else "seen"
    described = _profiled(tmp_path, shape, text, "--identifier", "patient")
    assert _block(described, column)["role"] == "identifier"
    quiet = io.StringIO()
    with contextlib.redirect_stdout(quiet), contextlib.redirect_stderr(quiet):
        assert cli.main(["generate", f"{tmp_path / (shape + '-profile.json')}", "--out-dir", f"{tmp_path}",
                         "--seed", "0", "--replace"]) == 0
    assert _parses(_column(tmp_path / f"{shape}-twin.csv", column), "%Y-%m-%d") == 0
    outcome = validation.measure(contract.load_profile(f"{tmp_path / (shape + '-profile.json')}"),
                                 f"{tmp_path / (shape + '-twin.csv')}")
    missed = sorted({f"{check.subcheck}" for check in outcome.checks if check.verdict == validation.MISSED})
    assert missed == ["length.min"], missed
    report = (tmp_path / f"{shape}-twin-report.txt").read_text(encoding="utf-8")
    assert "min_length" in report and "no valid one of its reading" in " ".join(report.split()), report[-3000:]


def test_a_span_too_narrow_for_the_count_never_leaves_a_made_up_cell(tmp_path: pathlib.Path) -> None:
    """Codex's item 1: eight different held values against a deepest span of one day.

    The capacity is resolved before any cell is filled (`grains.held_spans`):
    the twin draws from the first published span wide enough, so every
    cell is a valid date and the count of different values holds.
    """
    described = _profiled(tmp_path, "narrow", persons_counted.short_span_table(), "--identifier", "patient")
    block = _block(described, "seen")
    assert block["role"] == "identifier" and block["n_distinct"] == 8, block["n_distinct"]
    assert block["time_grain"]["spans"][-1] == ["day", "2024-06-15", "2024-06-15"], block["time_grain"]
    twin, _real = _generated_and_validated(tmp_path, "narrow")
    cells = _column(tmp_path / "narrow-twin.csv", "seen")
    assert _parses(cells, "%m/%d/%Y") == 0, sorted(set(cells))[:5]
    assert len(set(cells)) == 8 and "seen" not in twin, (sorted(set(cells)), twin)


def test_a_tail_keeps_its_rows_when_the_count_is_filled(tmp_path: pathlib.Path) -> None:
    """Codex's item 2: the count at the year never moves a row into or out of a tail.

    1980's thirty rows are the low tail (boundary `1982-01`, which the p05
    rank also holds); at seed 2 the count at the rung once moved a row of
    1982 into 1981, giving the tail 31 rows and a second value.
    """
    described = _profiled(tmp_path, "years", persons_counted.alternate_years_table(), "--identifier", "patient")
    block = _block(described, "seen")
    assert block["time_grain"]["rung"] == "year" and block["low_tail"]["rows"] == 30, block["low_tail"]
    quiet = io.StringIO()
    with contextlib.redirect_stdout(quiet), contextlib.redirect_stderr(quiet):
        assert cli.main(["generate", f"{tmp_path / 'years-profile.json'}", "--out-dir", f"{tmp_path}",
                         "--seed", "2", "--replace"]) == 0
    outcome = validation.measure(contract.load_profile(f"{tmp_path / 'years-profile.json'}"),
                                 f"{tmp_path / 'years-twin.csv'}")
    missed = sorted({f"{check.subcheck}" for check in outcome.checks if check.verdict == validation.MISSED})
    assert missed == [], missed


def test_the_counts_protections_are_the_oracles(tmp_path: pathlib.Path) -> None:
    """Method G7.13, repair round 2: the buckets that give no row and the fences, product against oracle."""
    from test_oracle_rule_witnesses import ORACLE_MODULE as module

    for stem, text in (("years", persons_counted.alternate_years_table()),
                       ("visits", _visits(1200, 400, datetime.date(2023, 1, 1), 730, 7))):
        _profiled(tmp_path, stem, text, "--identifier", "patient")
        loaded = contract.load_profile(f"{tmp_path / (stem + '-profile.json')}")
        column = [one for one in loaded.columns if one.name == "seen"][0]
        block = _block(json.loads((tmp_path / f"{stem}-profile.json").read_text(encoding="utf-8")), "seen")
        grain = column.time_grain
        assert grain is not None and isinstance(column.facts, contract.DatetimeFacts)
        rung, first, last = grain.spans[-1]
        found = generation._count_protections(column.facts, rung, first, last)
        assert found is not None
        kept, fences = found

        def when(moment: int) -> datetime.datetime:
            return datetime.datetime(1970, 1, 1) + datetime.timedelta(microseconds=moment // 1000)

        oracle_kept, oracle_fences = module.pooled_protections(block, rung, when(first), when(last))
        assert sorted({when(one) for one in kept}) == oracle_kept, stem
        assert tuple(None if one is None else when(one) for one in fences) == oracle_fences, stem


@pytest.mark.parametrize(("spelling", "extra"), (("2020-06-15", ("--missing-value", "2020-06-15")),
                                                 ("1900-01-01", ())))
def test_an_absent_date_stays_absent(tmp_path: pathlib.Path, spelling: str, extra: "tuple[str, ...]") -> None:
    """Codex's item 3: thirty patients' spelling of no value that reads as a date is never pooled into a present cell.

    The walk reads it as no moment, so it enters no span; the description
    loads (TG1's rows are the present cells); and `validate` keeps it
    absent on the real table and on the twin, in the whole-table reading
    and in the redescription. The twin's own report, which recounts the
    column at its rung as it leaves, names no deviation of it either (the
    second verify's item 3: a recount that read the spelling as a present
    date named `n_not_numeric` and the 25th and 75th percentiles).
    """
    described = _profiled(tmp_path, "absent", persons_counted.absent_dates_table(spelling), "--identifier",
                          "patient", *extra)
    block = _block(described, "seen")
    assert block["n_present"] == 510 and block["n_missing"] == 90, (block["n_present"], block["n_missing"])
    grain = block["time_grain"]
    assert grain["rung"] != grains.HELD and grain["spans"][0][1] >= "2022", grain
    twin, real = _generated_and_validated(tmp_path, "absent")
    assert twin == set() and real == set(), (twin, real)
    assert _column(tmp_path / "absent-twin.csv", "seen").count(spelling) == 90
    made = generation.generate(contract.load_profile(f"{tmp_path / 'absent-profile.json'}"), 0)
    named = [f"{one.fact}" for one in made.deviations if one.column == "seen"]
    assert named == [], named


def _validated_exit(folder: pathlib.Path, stem: str, checked: pathlib.Path) -> int:
    """`synthtwin validate`'s exit code on ``checked`` against the stem's description."""
    quiet = io.StringIO()
    with contextlib.redirect_stdout(quiet), contextlib.redirect_stderr(quiet):
        return cli.main(["validate", f"{folder / (stem + '-profile.json')}", "--out-dir", f"{folder}",
                         "--replace", "--twin", f"{checked}"])


def test_a_date_for_nobody_three_people_write_stays_absent(tmp_path: pathlib.Path) -> None:
    """The second verify's item 1 (Codex's item 3, its shape `c3d`): an undeclared `1900-01-01` three patients write.

    The column's own reading takes the nine cells as no value, and three
    people are too few for its block to name the spelling: the validator
    keeps as written every cell that reading takes as absent (the
    redescription handed the cells as written, `profile.build_document`'s
    ``absent_read``), so both the real table and the twin pass. Before,
    the cells were pooled into the first bucket and the real table
    missed its presence, its tails and `n_not_numeric` at exit 3.
    """
    described = _profiled(tmp_path, "few", persons_counted.absent_dates_table("1900-01-01", 3), "--identifier",
                          "patient")
    block = _block(described, "seen")
    assert block["n_present"] == 591 and block["n_missing"] == 9, (block["n_present"], block["n_missing"])
    assert "1900-01-01" not in block["missing_by_source"], block["missing_by_source"]
    assert block["time_grain"]["rung"] != grains.HELD, block["time_grain"]
    quiet = io.StringIO()
    with contextlib.redirect_stdout(quiet), contextlib.redirect_stderr(quiet):
        assert cli.main(["generate", f"{tmp_path / 'few-profile.json'}", "--out-dir", f"{tmp_path}",
                         "--seed", "0", "--replace"]) == 0
    assert _validated_exit(tmp_path, "few", tmp_path / "few.csv") == 0
    assert _validated_exit(tmp_path, "few", tmp_path / "few-twin.csv") == 0


@pytest.mark.parametrize(("shape", "name", "count"), (("rep4", "birth_month", 530), ("rep2", "born", 600)))
def test_a_held_month_column_holds_its_count_in_the_widened_span(
    tmp_path: pathlib.Path, shape: str, name: str, count: int
) -> None:
    """The second verify's item 2 (its shapes `rep4` and `rep2`): 530 and 600 birth months, held with no span.

    The capacity is measured in the layout's finest written detail (months
    for `%Y-%m`, `grains.held_spans`) and the fixed span widened by whole
    decades from 2000 to twice the published count (`grains.fixed_span_holding`):
    every twin cell is a valid month and the twin holds every one. Before,
    the 360 months of 2000 to 2029 left `rep4`'s 530 at 360 (n_distinct,
    `_by_occurrences` and `_folded` missed at exit 3); a span of exactly
    `rep2`'s 600 months left 582 (room of one).
    """
    table = persons_counted.birth_months_table() if shape == "rep4" else persons_counted.one_birth_month_a_year_table()
    described = _profiled(tmp_path, shape, table, "--identifier", "patient")
    block = _block(described, name)
    assert block["time_grain"]["rung"] == grains.HELD and block["time_grain"]["spans"] == [], block["time_grain"]
    assert block["n_distinct"] == count and block["time_grain"]["finest"] == "month", block["n_distinct"]
    twin, _real = _generated_and_validated(tmp_path, shape)
    cells = _column(tmp_path / f"{shape}-twin.csv", name)
    assert _parses(cells, "%Y-%m") == 0, sorted(set(cells))[:5]
    assert len(set(cells)) == count and name not in twin, (len(set(cells)), twin)
    assert _validated_exit(tmp_path, shape, tmp_path / f"{shape}-twin.csv") == 0


def test_a_value_no_span_can_take_unrepeated_repeats_a_valid_one(tmp_path: pathlib.Path) -> None:
    """The G1 floor's last step (the second verify's item 2): a made-up value no span takes unrepeated.

    The birth-month column's block, its count set below its 530 made-up
    values (as no description the walk writes publishes), gives spans of
    2000 to 2029 alone: 360 months for 530 values. Each value the walk
    cannot take unrepeated repeats a valid month in the last span; none
    is left as made up. Without the repeat the cells no walk placed stayed
    stand-ins.
    """
    _profiled(tmp_path, "born", persons_counted.birth_months_table(), "--identifier", "patient")
    loaded = contract.load_profile(f"{tmp_path / 'born-profile.json'}")
    column = [one for one in loaded.columns if one.name == "birth_month"][0]
    short = dataclasses.replace(column, n_distinct=10)
    assert grains.held_spans(short.time_grain, 10) == [grains.fixed_span(grains.DATE)]  # type: ignore[arg-type]
    cells = _column(tmp_path / "born.csv", "birth_month")
    draw = random.Random(0)
    words = [draw.getrandbits(64) for _cell in cells]
    found, unwritten = generation._inside_the_grain(short, cells, words)
    assert unwritten == 0 and _parses(found, "%Y-%m") == 0, (unwritten, sorted(set(found))[:5])
    assert len(set(found)) <= 360 < len(set(cells)), (len(set(found)), len(set(cells)))


def test_the_counter_reads_every_spelling_of_nobody(tmp_path: pathlib.Path) -> None:
    """The verify's item 3: two people's `N/A` beside a pooled date is no unread cell to the counter written apart."""
    described = _profiled(tmp_path, "nobody", persons_counted.nobody_dates_table(), "--identifier", "patient")
    assert _block(described, "visit_date")["time_grain"]["rung"] != grains.HELD
    named = persons_counted.count_files(tmp_path / "nobody.csv", tmp_path)["named"]
    assert not [one for one in named if "unread" in one], named


def test_the_counter_keys_each_cell_by_its_offset(tmp_path: pathlib.Path) -> None:
    """The verify's item 1, the counter's half: three people's `+05:30` at a pooled rung is named by the counter alone.

    `grain_groups` is handed the offset table as a description at the
    month would print it (the product holds it, so the counter is asked
    of the shape directly): it names the offset three people write, and
    nothing else.
    """
    described = _profiled(tmp_path, "offs", persons_counted.offset_stamps_table(), "--identifier", "patient")
    held = _block(described, "event_ts")["time_grain"]
    grain = dict(held, rung="month", spans=[["month", "2022-01-01 00:00:00", "2023-12-01 00:00:00"]])
    rows = list(csv.reader(io.StringIO(persons_counted.offset_stamps_table())))[1:]
    raw = [row[1] for row in rows]
    found = persons_counted.grain_groups(raw, [cell[:7] for cell in raw], [row[0] for row in rows],
                                         {"time_grain": grain, "missing_by_source": {}})
    assert found == ["offset +05:30"], found
