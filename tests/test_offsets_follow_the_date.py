"""Offsets that follow the date (lane DST, plan P4-D474, method G7.4r).

A column of stamps written with their UTC offsets wears, in every modern
export, the offset its zone had in force on each stamp's own date. The
twin used to spend the offset census by counts, so a winter date came back
at the summer offset (6,390 of 20,000 cells of the health zoo's
`encounters.admit_ts`), and a cell could land in the hour the clocks skip.
Where every stamp agrees with one of `offset_rules`' closed families, the
description publishes `offset_rule`, and the twin writes each cell at the
offset in force on its date: the census is met by where its instants
stand, a pooled column's buckets are read at the offset in force at their
start, and validation names the rule as a fact the twin must keep.

The families are checked here against a calendar written from their text
with the standard library's dates (never `zoneinfo`), on quarter hours
sampled over four decades and beside every change; the reading against
generated columns; the product against
the reference oracle (A-P4-59); and the twin end to end on the zoo's own
tables at 600 rows and on one table at the owner's floor of 20,000 rows.
"""

from __future__ import annotations

import contextlib
import dataclasses
import csv
import datetime
import io
import json
import pathlib
import random
import runpy
import sys

import pytest

from synthtwin import cli, contract, dialect, errors, generation, grains, offset_rules, parsing, profile, reading, taxonomy

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "tests"))

import fixtures  # noqa: E402
import health_zoo as zoo  # noqa: E402
import health_zoo_wide as wide  # noqa: E402

ORACLE = REPOSITORY / "tools" / "reference" / "make_generation_reference_vectors.py"
_EPOCH = datetime.datetime(1970, 1, 1)


# -- the families, from their own text ------------------------------------


def _sunday(year: int, month: int, nth: int) -> datetime.date:
    """A month's nth Sunday, or its last for nth 0, by the calendar."""
    if nth:
        first = datetime.date(year, month, 1)
        return first + datetime.timedelta(days=(6 - first.weekday()) % 7 + 7 * (nth - 1))
    following = datetime.date(year + (month == 12), month % 12 + 1, 1)
    last = following - datetime.timedelta(days=1)
    return last - datetime.timedelta(days=(last.weekday() + 1) % 7)


def _spans(family: str, standard: int, year: int) -> "tuple[datetime.datetime, datetime.datetime]":
    """Summer time's start and end in a year as UTC moments, read off the family's own words."""
    hour = datetime.timedelta(hours=1)
    zone = datetime.timedelta(seconds=standard)
    if family == "us":
        start, end = ((_sunday(year, 3, 2), _sunday(year, 11, 1)) if year >= 2007
                      else (_sunday(year, 4, 1), _sunday(year, 10, 0)))
        return (datetime.datetime.combine(start, datetime.time(2)) - zone,
                datetime.datetime.combine(end, datetime.time(2)) - zone - hour)
    if family == "eu":
        return (datetime.datetime.combine(_sunday(year, 3, 0), datetime.time(1)),
                datetime.datetime.combine(_sunday(year, 10, 0), datetime.time(1)))
    start = _sunday(year, 10, 1) if family == "au" else _sunday(year, 9, 0)
    return (datetime.datetime.combine(start, datetime.time(2)) - zone,
            datetime.datetime.combine(_sunday(year, 4, 1), datetime.time(3)) - zone - hour)


def _wall_offsets(family: str, standard: int, local: datetime.datetime) -> "tuple[int, ...]":
    """Every offset a wall clock may wear, summer time's first: a fold-aware reading, no zone database."""
    found: "tuple[int, ...]" = ()
    for offset in (standard + 3600, standard):
        moment = local - datetime.timedelta(seconds=offset)
        year = (moment + datetime.timedelta(seconds=standard)).year
        start, end = _spans(family, standard, year)
        summer = (moment < end or moment >= start) if family in ("au", "nz") else start <= moment < end
        if (standard + 3600 if summer else standard) == offset:
            found = found + (offset,)
    return found


ZONES = (("us", -5 * 3600), ("us", -6 * 3600), ("us", -8 * 3600), ("us", -10 * 3600), ("eu", 0),
         ("eu", 3600), ("eu", 7200), ("au", 10 * 3600), ("au", 34200), ("nz", 12 * 3600))


@pytest.mark.parametrize("family,standard", ZONES)
def test_quarter_hours_sampled_over_four_decades_read_as_the_calendar_says(family: str, standard: int) -> None:
    """Generated, not every quarter hour (Codex's item 10): for each year from the family's first admitted one (`us`
    1987, `au` and `nz` 2008; `eu` from 1988, its rule's words the same before 1996) to 2030, the 25 quarter hours
    from three hours before each of its two changes to three hours after, and 300 quarter hours drawn over the year:
    each wall clock's offsets in force, against the calendar written from the family's own words."""
    rule = offset_rules.Rule(family, standard)
    years: "dict[tuple[str, int, int], tuple[int, int]]" = {}
    draw = random.Random(f"{family}{standard}")
    checked = 0
    for year in range({"us": 1987, "eu": 1988, "au": 2008, "nz": 2008}[family], 2031):
        start, end = _spans(family, standard, year)
        for change in (start, end):
            base = change + datetime.timedelta(seconds=standard)
            for step in range(-12, 13):
                local = base + datetime.timedelta(minutes=15 * step)
                seconds = int((local - _EPOCH).total_seconds())
                assert offset_rules.in_force(rule, seconds, years) == _wall_offsets(family, standard, local), local
                checked += 1
        for _draw in range(300):
            local = datetime.datetime(year, 1, 1) + datetime.timedelta(minutes=15 * draw.randrange(35000))
            seconds = int((local - _EPOCH).total_seconds())
            assert offset_rules.in_force(rule, seconds, years) == _wall_offsets(family, standard, local), local
            checked += 1
    assert checked >= 7700


def test_the_hour_skipped_wears_none_and_the_hour_repeated_both() -> None:
    """The zoo's own Eastern oracle at the changes of 2024 (the zoo plan's section 3, item (c))."""
    rule = offset_rules.parsed_rule("us -05:00")
    assert rule is not None
    for local in (datetime.datetime(2024, 3, 10, 2, 30), datetime.datetime(2024, 11, 3, 1, 30),
                  datetime.datetime(2024, 7, 1, 12), datetime.datetime(2024, 1, 15, 9)):
        seconds = int((local - _EPOCH).total_seconds())
        wanted = tuple(offset_rules.offset_seconds(key) for key in zoo.eastern_offsets(local))
        assert offset_rules.in_force(rule, seconds) == wanted


# -- the reading ------------------------------------------------------------


def _stamps(family: str, standard: int, rows: int, seed: int, both: bool = True) -> "list[tuple[str, str]]":
    """(canonical text, offset key) pairs of a column of wall clocks at the offsets in force, the changes' days among them."""
    draw = random.Random(seed)
    found: "list[tuple[str, str]]" = []
    while len(found) < rows:
        local = datetime.datetime(2023, 1, 1) + datetime.timedelta(seconds=draw.randrange(2 * 365 * 86400))
        here = _wall_offsets(family, standard, local)
        if not here:
            continue
        offset = draw.choice(here) if both else here[0]
        found += [(local.strftime("%Y-%m-%d %H:%M:%S"), offset_rules.offset_text(offset))]
    return found


@pytest.mark.parametrize("family,standard", ZONES)
def test_a_column_at_the_offsets_in_force_reads_as_its_rule(family: str, standard: int) -> None:
    """The first family every stamp agrees with is read, with the zone's standard offset."""
    pairs = _stamps(family, standard, 2000, 7)
    found = offset_rules.rule_of(pairs)
    parsed = offset_rules.parsed_rule(found)
    assert parsed is not None and parsed.standard == standard
    assert all(
        offset_rules.offset_seconds(offset) in offset_rules.in_force(parsed, offset_rules.local_seconds(text) or 0)
        for text, offset in pairs
    )


def test_a_column_off_its_rule_by_one_cell_reads_none() -> None:
    """A stamp in the skipped hour, a winter stamp at the summer offset, a third offset, `Z`, one offset: no rule."""
    pairs = _stamps("us", -5 * 3600, 500, 3)
    assert offset_rules.rule_of(pairs) == "us -05:00"
    assert offset_rules.rule_of(pairs + [("2024-03-10 02:30:00", "-05:00")]) == ""
    assert offset_rules.rule_of(pairs + [("2024-01-15 10:00:00", "-04:00")]) == ""
    assert offset_rules.rule_of(pairs + [("2024-01-15 10:00:00", "-03:00")]) == ""
    assert offset_rules.rule_of(pairs + [("2024-01-15 10:00:00", "")]) == ""
    assert offset_rules.rule_of([(text, "Z" if key == "+00:00" else key) for text, key in _stamps("eu", 0, 300, 4)]) == ""
    assert offset_rules.rule_of([pair for pair in pairs if pair[1] == "-05:00"]) == ""
    assert offset_rules.rule_of([("1979-07-01 10:00:00", "-04:00"), ("1979-01-01 10:00:00", "-05:00")]) == ""


# -- the product against the reference oracle (A-P4-59) ---------------------


@pytest.fixture(scope="module")
def oracle() -> "dict[str, object]":
    return runpy.run_path(str(ORACLE))


def test_the_draw_inside_a_bucket_is_the_oracles(oracle: "dict[str, object]") -> None:
    """G7.13 under G7.4r: 4,000 drawn stamps, month and day buckets, three rules, cell for cell."""
    draw = random.Random(11)
    reading = grains.Reading(grains.STAMP, "iso-datetime")
    for family, standard in (("us", -18000), ("eu", 3600), ("au", 36000)):
        rule = offset_rules.Rule(family, standard)
        for _case in range(1334):
            local = datetime.datetime(2023, 1, 1) + datetime.timedelta(seconds=draw.randrange(2 * 365 * 86400))
            here = offset_rules.in_force(rule, int((local - _EPOCH).total_seconds()))
            if not here:
                continue
            cell = local.strftime("%Y-%m-%d %H:%M:%S") + offset_rules.offset_text(here[0])
            rung = draw.choice((grains.MONTH, grains.DAY, grains.HOUR))
            word = draw.getrandbits(64)
            mine = grains.drawn_inside(cell, reading, rung, word, rule)
            theirs = oracle["pooled_drawn_inside"](cell, "iso-datetime", rung, word, (family, standard, rung))
            assert mine == theirs, (cell, rung, word)
            read = parsing.parse_datetime(mine, "iso-datetime")
            assert read is not None
            local_seconds = offset_rules.local_seconds(read[0])
            assert local_seconds is not None
            assert offset_rules.offset_seconds(read[1]) in offset_rules.in_force(rule, local_seconds)


def test_an_offset_written_again_from_the_callers_reading_is_the_same_text() -> None:
    """The statistics check's item 4: the draw under a rule hands `grains.with_offset` the reading it holds, so a cell is
    read once less; 3,000 generated cells in four spellings of the offset, each written at both offsets of its rule,
    come back byte for byte as when the function reads the cell itself."""
    draw = random.Random(71)
    reading = grains.Reading(grains.STAMP, "iso-datetime")
    for _case in range(3000):
        local = datetime.datetime(2023, 1, 1) + datetime.timedelta(seconds=draw.randrange(2 * 365 * 86400))
        offset = draw.choice((-18000, -14400, 3600, 7200, 36000, 39600))
        text = offset_rules.offset_text(offset)
        cell = local.strftime(draw.choice(("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"))) + draw.choice(
            (text, text[0:3] + text[4:6], text[0:3] if text.endswith("00") else text)
        )
        held = parsing.parse_datetime(cell, reading.member)
        for seconds in (offset, offset + 3600, offset - 3600):
            assert grains.with_offset(cell, reading, seconds, held) == grains.with_offset(cell, reading, seconds), cell


def test_the_census_step_and_the_cut_gaps_are_the_oracles(oracle: "dict[str, object]") -> None:
    """G7.4r's helpers on 3,000 generated runs: the offset worn, the side counted, the changes around, the census step."""
    draw = random.Random(5)
    years: "dict[tuple[str, int, int], tuple[int, int]]" = {}
    for family, standard in (("us", -21600), ("eu", 3600), ("nz", 43200)):
        for rung in ("", grains.MONTH, grains.QUARTER, grains.DAY):
            clock = generation._RuleClock(offset_rules.Rule(family, standard), rung)
            theirs = (family, standard, rung)
            for _case in range(250):
                instant = 1672531200 + draw.randrange(2 * 365 * 86400)
                assert generation._rule_offset_at(clock, instant, years) == oracle["rule_offset_for"](theirs, instant)
                assert generation._rule_summer(clock, instant, years) == oracle["rule_summer"](theirs, instant)
                assert generation._rule_changes_around(clock, instant, years) == oracle["rule_bounds"](theirs, instant)


# -- the twin, end to end -----------------------------------------------------


def _quiet(arguments: "list[str]", floor: bool) -> int:
    sink = io.StringIO()
    with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
        return cli.main(arguments, small_tables_refused=floor)


def _column(path: pathlib.Path, name: str) -> "list[str]":
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    place = rows[0].index(name)
    return [row[place] for row in rows[1:]]


def _off(cells: "list[str]", rule: "offset_rules.Rule") -> int:
    """Cells whose offset is not one in force on their date and time (a cell in the skipped hour among them)."""
    wrong = 0
    for cell in cells:
        read = parsing.parse_datetime(cell, "iso-datetime")
        local = offset_rules.local_seconds(read[0]) if read is not None else None
        if read is None or local is None or offset_rules.offset_seconds(read[1]) not in offset_rules.in_force(rule, local):
            wrong += 1
    return wrong


def _central_table(rows: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Central stamps, a quarter on the days the clocks change, a third of the autumn ones in the hour they repeat."""
    draw = random.Random(seed)
    found: "list[list[str]]" = []
    for index in range(rows):
        moment = wide._in_the_hour_twice(draw, wide._stamp_on_a_change_day(draw), wide.central_offsets, 1)
        found += [[f"EV{700000 + index}", moment.strftime("%Y-%m-%d %H:%M:%S") + wide._either(draw, wide.central_offsets(moment))]]
    return ["event_ref", "central_ts"], found


def _run(folder: pathlib.Path, header: "list[str]", rows: "list[list[str]]", floor: bool) -> "tuple[dict, list[str], int]":
    folder.mkdir(parents=True, exist_ok=True)
    source = folder / "events.csv"
    source.write_bytes(zoo.csv_bytes(header, rows))
    assert _quiet(["profile", f"{source}", "--replace", "--identifier", "event_ref"], floor) == 0
    profile_path = folder / "events-profile.json"
    assert _quiet(["generate", f"{profile_path}", "--replace", "--seed", "0"], floor) == 0
    code = _quiet(["validate", f"{profile_path}", "--replace"], floor)
    block = [column for column in json.loads(profile_path.read_text())["columns"] if column["name"] == "central_ts"][0]
    return block, _column(folder / "events-twin.csv", "central_ts"), code


def test_at_the_owners_floor_every_twin_stamp_wears_the_offset_in_force(tmp_path: pathlib.Path) -> None:
    """20,000 rows through the shipped command: the rule read, no cell off it or in the skipped hour, the census met,
    validate clean, the hour the clocks repeat at both its offsets. The repair's tables at the floor -- six zones even
    and heaped, a decade of a person's visits in two zones, two years of four zones at ten times the rows -- are
    K-HZ-27's (`tools/measurements/kpi_zoo_offsets.py`, under kpi_run --slow, the suite's time rule)."""
    header, rows = _central_table(20000, 20261109)
    block, cells, code = _run(tmp_path, header, rows, True)
    assert block["offset_rule"] == "us -06:00"
    rule = offset_rules.parsed_rule("us -06:00")
    assert rule is not None and _off(cells, rule) == 0
    written: "dict[str, int]" = {}
    for cell in cells:
        written[cell[19:]] = written.get(cell[19:], 0) + 1
    assert written == block["utc_offsets"]
    assert code == 0
    # ...and the hour the clocks repeat is written at both its offsets.
    repeated = [cell for cell in cells if cell[0:10] in ("2023-11-05", "2024-11-03") and cell[11:13] == "01"]
    assert {cell[19:] for cell in repeated} == {"-05:00", "-06:00"}


def test_the_zoos_tables_at_600_rows_keep_every_offset_in_force(tmp_path: pathlib.Path) -> None:
    """The pooled path (a person's encounters, month or quarter buckets) and the shared clock (US Central and Europe)."""
    for name in ("encounters", "zoned_stamps"):
        result = zoo.run_zoo(tmp_path / name, zoo.SMOKE_ROWS, tables=(zoo.table_named(name),))[0]
        assert result["steps"]["validate"]["exit"] == 0, (name, result["misses"])
        failing = [check for _kind, check, _why in result["analyst"]]
        assert not [check for check in failing if "offset in force" in check], (name, failing)


def test_a_twin_spending_the_census_by_counts_is_named_by_validate(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The mutant: G7.4r withdrawn from the generator, the twin's offsets off their dates, and `offsets.rule` misses."""
    header, rows = _central_table(600, 3)
    monkeypatch.setattr(generation, "_column_rule", lambda column, facts: None)
    block, cells, code = _run(tmp_path, header, rows, False)
    rule = offset_rules.parsed_rule(block["offset_rule"])
    assert rule is not None and _off(cells, rule) > 0
    assert code == 3
    quality = (tmp_path / "events-twin-quality.txt").read_text(encoding="utf-8")
    assert "offsets.rule [datetime.offset_rule]: MISSED" in quality


def test_a_column_of_one_offset_or_of_mixed_offsets_publishes_no_rule(tmp_path: pathlib.Path) -> None:
    """Every column outside the shape keeps its description: one offset, `Z` beside offsets, offsets off any rule."""
    draw = random.Random(9)
    rows: "list[list[str]]" = []
    for index in range(600):
        local = datetime.datetime(2024, 1, 1) + datetime.timedelta(seconds=draw.randrange(300 * 86400))
        stamp = local.strftime("%Y-%m-%d %H:%M:%S")
        rows += [[f"EV{index}", stamp + "-05:00", stamp + draw.choice(("Z", "+01:00")), stamp + draw.choice(("-05:00", "-04:00"))]]
    folder = tmp_path / "plain"
    folder.mkdir()
    source = folder / "events.csv"
    source.write_bytes(zoo.csv_bytes(["event_ref", "one", "mixed", "off"], rows))
    assert _quiet(["profile", f"{source}", "--replace", "--identifier", "event_ref"], False) == 0
    described = json.loads((folder / "events-profile.json").read_text())
    for column in described["columns"]:
        assert "offset_rule" not in column, column["name"]
    loaded = contract.load_profile(f"{folder / 'events-profile.json'}")
    for column in loaded.columns:
        if isinstance(column.facts, contract.DatetimeFacts):
            assert column.facts.offset_rule == ""


def test_the_census_step_moves_the_ranks_the_oracle_moves(oracle: "dict[str, object]") -> None:
    """G7.4r step 2 on 600 generated columns: body runs between pins, a census short or over, three rules, two rungs."""
    import types

    draw = random.Random(23)
    moved_any = 0
    for case in range(600):
        family, standard = (("us", -21600), ("eu", 3600), ("nz", 43200))[case % 3]
        rung = (grains.MONTH if case % 2 else "")
        parsed = draw.randrange(40, 160)
        low = 1672531200 + draw.randrange(86400 * 200)
        ordinals = sorted(low + draw.randrange(2 * 365 * 86400) for _rank in range(parsed))
        pins = sorted({0, parsed - 1} | {draw.randrange(parsed) for _pin in range(draw.randrange(2, 7))})
        lows = [0] * parsed
        highs = [0] * parsed
        for left, right in zip(pins, pins[1:]):
            for rank in range(left, right + 1):
                lows[rank], highs[rank] = ordinals[left], ordinals[right]
        for pin in pins:
            lows[pin] = highs[pin] = ordinals[pin]
        clock = generation._RuleClock(offset_rules.Rule(family, standard), rung)
        summer = sum(1 for value in ordinals if generation._rule_summer(clock, value, {}))
        wanted = max(0, min(parsed, summer + draw.randrange(-parsed // 4, parsed // 4 + 1)))
        census = {offset_rules.offset_text(standard + 3600): wanted, offset_rules.offset_text(standard): parsed - wanted}
        tails = draw.randrange(0, 3)
        facts = types.SimpleNamespace(utc_offsets=census, offset_rule=f"{family} {offset_rules.offset_text(standard)}")
        layout = types.SimpleNamespace(
            low=types.SimpleNamespace(rows=tails) if tails else None,
            high=types.SimpleNamespace(rows=tails) if tails else None,
            listed={},
        )
        mine, _notes = generation._census_by_rule(
            types.SimpleNamespace(name="t"), facts, clock, list(ordinals), (lows, highs), layout, set(pins)
        )
        block = {"utc_offsets": census, "heavy_dates": [],
                 "low_tail": {"rows": tails} if tails else None, "high_tail": {"rows": tails} if tails else None}
        theirs = oracle["census_by_rule"](block, (family, standard, rung), list(ordinals), lows, highs, set(pins), parsed)
        assert mine == theirs, case
        moved_any += mine != ordinals
    assert moved_any > 300


def test_the_combined_case_zone_words_follow_the_date_once_they_are_read(tmp_path: pathlib.Path) -> None:
    """The zoo plan's section 3 item (d), carried by whichever of lanes DST and TR merges second.

    Lane TR (plan P4-D473) reads a stamp followed by its zone word (`EDT`,
    `EST`); the word is a function of the offset, so once it is read the
    column takes its rule and every twin word is the one in force on its
    date. Until the word is read this case has nothing to hold and says so.
    """
    if not parsing.layouts_of("2024-10-29 09:28:34 EDT"):
        pytest.skip("a stamp's zone word is not read on this tree: lane TR's reading (plan P4-D473)")
    draw = random.Random(31)
    rows: "list[list[str]]" = []
    for index in range(600):
        moment = wide._stamp_on_a_change_day(draw)
        word = " EDT" if wide._either(draw, zoo.eastern_offsets(moment)) == "-04:00" else " EST"
        rows += [[f"EV{index}", moment.strftime("%Y-%m-%d %H:%M:%S") + word]]
    folder = tmp_path / "words"
    folder.mkdir()
    source = folder / "events.csv"
    source.write_bytes(zoo.csv_bytes(["event_ref", "zoned_word"], rows))
    assert _quiet(["profile", f"{source}", "--replace", "--identifier", "event_ref"], False) == 0
    block = [column for column in json.loads((folder / "events-profile.json").read_text())["columns"]
             if column["name"] == "zoned_word"][0]
    assert block.get("offset_rule") == "us -05:00"
    assert _quiet(["generate", f"{folder / 'events-profile.json'}", "--replace", "--seed", "0"], False) == 0
    cells = _column(folder / "events-twin.csv", "zoned_word")
    assert wide._wrong_offsets_by(  # type: ignore[attr-defined]
        __import__("pandas").Series(cells), wide._zone_words_in_force, "%Y-%m-%d %H:%M:%S", 19
    ) == 0


# -- repair 1: the census step thins a stretch evenly, and the take-back keeps each rank in its gap ----------


def test_every_stretch_of_a_moved_run_is_laid_over_its_whole_stretch() -> None:
    """Skeptic 1's item 1, generated: 3,000 runs a change runs through, a census short or over by up to a third of the
    run; after the census step every stretch of a moved run holding ranks has its first rank within one spacing of the
    stretch's start and its last within one spacing of its end, so the hours beside a change keep their share (a giving
    stretch that kept its ranks where they stood left the side next to the change empty)."""
    draw = random.Random(61)
    years: "dict[tuple[str, int, int], tuple[int, int]]" = {}
    checked = 0
    for case in range(3000):
        family, standard = (("us", -18000), ("eu", 3600), ("au", 36000), ("nz", 43200))[case % 4]
        clock = generation._RuleClock(offset_rules.Rule(family, standard), "")
        low = 1672531200 + draw.randrange(400 * 86400)
        high = low + draw.randrange(20, 120) * 86400
        size = draw.randrange(8, 400)
        before = sorted(low + 1 + draw.randrange(high - low - 1) for _rank in range(size))
        stretches = generation._stretches_between_changes(clock, low, high, years)
        if len(stretches) < 2:
            continue
        summer = sum(1 for value in before if generation._rule_summer(clock, value, years))
        change = draw.randrange(-size // 3, size // 3 + 1)
        change = max(-summer, min(size - summer, change))
        if change == 0:
            continue
        moved = list(before)
        generation._run_laid_out(moved, 0, size, stretches, change)
        assert moved == sorted(moved) and all(low < value < high for value in moved), case
        for start, stop, _summer in stretches:
            group = [value for value in moved if start <= value <= stop]
            if not group:
                continue
            spacing = (stop - start) // len(group) + 2
            assert group[0] - start <= spacing and stop - group[-1] <= spacing, (case, start, stop, len(group))
            checked += 1
    assert checked > 2000


def test_a_pooled_rank_wears_its_census_sides_offset_beside_every_bound() -> None:
    """Generated, four families, three rungs, 2009 to 2030: on a pooled clock every instant within two hours of each
    bound the census side changes at wears the offset of its side, so a pass on its own clock sets it on its side's
    midnight (the zoo's encounters wrote two discharge stamps an hour early, at 23:00 on 31 December, where the
    hour after December's first bucket wore summer time's offset on winter's side)."""
    years: "dict[tuple[str, int, int], tuple[int, int]]" = {}
    checked = 0
    for family, standard in (("us", -18000), ("eu", 3600), ("au", 36000), ("nz", 43200)):
        rule = offset_rules.Rule(family, standard)
        for rung in (grains.MONTH, grains.QUARTER, grains.DAY):
            clock = generation._RuleClock(rule, rung)
            for year in range(2009, 2031):
                for change in offset_rules.changes(rule, year):
                    _before, bound = generation._rule_changes_around(clock, change, years)
                    for step in range(-24, 25):
                        instant = bound + 300 * step
                        side = generation._rule_summer(clock, instant, years)
                        worn = generation._rule_offset_at(clock, instant, years)
                        assert (worn == standard + 3600) == side, (family, rung, year, instant)
                        checked += 1
    assert checked > 20000


def _fall_back_frame(draw: random.Random, rule: "offset_rules.Rule") -> "dict[str, object]":
    """One run between two pins across a change where the clocks go back, framed on its ranks' own clocks, its places
    sorted across the run as a pass sorts it (`generation._runs_sorted`)."""
    year = draw.randrange(2009, 2030)
    _start, change = offset_rules.changes(rule, year)
    below = change - draw.randrange(1, 3600)
    above = change + draw.randrange(1800, 4 * 3600)
    size = draw.randrange(4, 80)
    instants = sorted(below + 1 + draw.randrange(above - below - 1) for _rank in range(size))
    before = [below] + instants + [above]
    count = len(before)
    shifts = [offset_rules.offset_at(rule, value) for value in before]
    lows = [below if value < change else change for value in before]
    highs = [change - 1 if value < change else above for value in before]
    lows[0] = highs[0] = below
    lows[-1] = highs[-1] = above
    framed = sorted(before[rank] + shifts[rank] for rank in range(1, count - 1))
    return {
        "before": before, "framed": [before[0] + shifts[0]] + framed + [before[-1] + shifts[-1]],
        "shifts": shifts, "offsets": [offset_rules.offset_text(value) for value in shifts],
        "whole": [False] * count, "pinned": [rank in (0, count - 1) for rank in range(count)],
        "body": (0, count - 1), "lows": lows, "highs": highs, "change": change,
    }


def test_the_take_back_keeps_each_rank_inside_its_cut_gap(oracle: "dict[str, object]") -> None:
    """Skeptic 1's item 2, generated: 1,200 runs across a change where the clocks go back (the us, eu, au and nz
    families), each run's places sorted as one run by a pass; taken back under the rule, every rank stands inside its
    own cut gap at the offset in force at its instant, in instant order -- no rank at the other occurrence of its wall
    clock, none across the pin below -- as the oracle takes it back (A-P4-59). Without the rule's hand-back the same
    frames put ranks of the run before the change an hour early, below its pin."""
    draw = random.Random(67)
    crossed = 0
    for case in range(1200):
        family, standard = (("us", -18000), ("eu", 3600), ("au", 36000), ("nz", 43200))[case % 4]
        rule = offset_rules.Rule(family, standard)
        frame = _fall_back_frame(draw, rule)
        arguments = (
            frame["before"], frame["framed"], frame["shifts"], frame["offsets"], frame["whole"], frame["pinned"],
            frame["body"], (frame["lows"], frame["highs"]), 1,
        )
        moved, given = generation._off_own_clocks(*arguments, True)  # type: ignore[arg-type]
        lows, highs = frame["lows"], frame["highs"]  # type: ignore[misc]
        for rank in range(len(moved)):
            assert lows[rank] <= moved[rank] <= highs[rank], (case, rank)  # type: ignore[index]
            assert given[rank] == offset_rules.offset_text(offset_rules.offset_at(rule, moved[rank])), (case, rank)
        assert moved == sorted(moved), case
        theirs = oracle["own_clock_unframed"](
            frame["before"], frame["framed"], frame["shifts"], frame["offsets"], frame["whole"], frame["pinned"],
            frame["body"], lows, highs, 1, True,
        )
        assert (moved, given) == (theirs[0], theirs[1]), case  # type: ignore[index]
        unruled, _keys = generation._off_own_clocks(*arguments)  # type: ignore[arg-type]
        crossed += any(not lows[rank] <= unruled[rank] <= highs[rank] for rank in range(len(unruled)))  # type: ignore[index]
    assert crossed > 100, "premise: the frames reach the hand-back"


# -- the cases each surviving mutant of repair 1 is red on (skeptic 1's item 4) ----------


def _eastern_visits(rows: int, people: int, seed: int, first: int, years: int) -> "tuple[list[str], list[list[str]]]":
    """A person's visits at US Eastern's offsets in force, ``years`` years from ``first``, each a second of the wall clock."""
    draw = random.Random(seed)
    found: "list[list[str]]" = []
    start = datetime.datetime(first, 1, 1)
    while len(found) < rows:
        local = start + datetime.timedelta(seconds=draw.randrange(years * 365 * 86400))
        here = _wall_offsets("us", -5 * 3600, local)
        if not here:
            continue
        found += [[f"PT{500000 + len(found) % people}", local.strftime("%Y-%m-%d %H:%M:%S") + offset_rules.offset_text(here[0])]]
    return ["patient_ref", "seen_at"], found


def _person_document(folder: pathlib.Path, header: "list[str]", rows: "list[list[str]]") -> "tuple[pathlib.Path, dict]":
    """The table described by the library under its person column (`patient_ref`), and the file written."""
    folder.mkdir(parents=True, exist_ok=True)
    source = folder / "visits.csv"
    source.write_bytes(zoo.csv_bytes(header, rows))
    document = profile.build_document(
        reading.read_table(str(source)), taxonomy.Settings(), ["patient_ref"], [], [], subjects=["patient_ref"]
    )
    return fixtures.write_profile(folder, "visits-profile.json", document), document


def _southern_visits(rows: int, people: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """A person's visits in a south-eastern zone (`au +10:00`) over 2015 to 2024 at the offsets in force."""
    draw = random.Random(seed)
    found: "list[list[str]]" = []
    while len(found) < rows:
        local = datetime.datetime(2015, 1, 1) + datetime.timedelta(seconds=draw.randrange(3652 * 86400))
        here = _wall_offsets("au", 36000, local)
        if here:
            found += [[f"PT{600000 + len(found) % people}", local.strftime("%Y-%m-%d %H:%M:%S") + offset_rules.offset_text(here[0])]]
    return ["patient_ref", "seen_at"], found


def test_a_pooled_column_of_a_rule_is_walked_by_the_bucket_it_prints(tmp_path: pathlib.Path) -> None:
    """The statistics check's item 1: a change of the clocks cuts each April quarter of a south-eastern zone thinly
    (summer time to its first Sunday), so a walk counting each bucket's two offsets apart called the quarter thin and
    stepped back to the year, where no rule stands. Counted as its description prints it -- one start a bucket, at the
    offset in force there -- the quarter holds, the rule is published at it, and the twin keeps it."""
    _path, document = _person_document(tmp_path / "south", *_southern_visits(3000, 300, 53))
    block = [column for column in document["columns"] if column["name"] == "seen_at"][0]
    assert (block.get("time_grain") or {}).get("rung") in (grains.MONTH, grains.QUARTER), block.get("time_grain")
    assert block["offset_rule"] == "au +10:00"


def test_a_repeated_hours_bucket_starts_at_its_first_occurrence() -> None:
    """M11: an hour bucket of the fall-back day is written at its start's FIRST occurrence, from either occurrence of a cell inside it."""
    reading_ = grains.Reading(grains.STAMP, "iso-datetime")
    rule = offset_rules.parsed_rule("us -05:00")
    assert rule is not None
    wide_span = (0, 2**62)
    for cell in ("2024-11-03 01:30:00-04:00", "2024-11-03 01:30:00-05:00"):
        made = grains.coarse_cell(cell, reading_, grains.HOUR, wide_span[0], wide_span[1], True, rule)
        assert made == "2024-11-03 01:00:00-04:00", cell
    # ...and the hour after it, which the clocks do not repeat, at the offset in force there.
    assert grains.coarse_cell("2024-11-03 02:10:00-05:00", reading_, grains.HOUR, 0, 2**62, True, rule) == "2024-11-03 02:00:00-05:00"


def test_the_loader_refuses_a_rule_off_its_census_or_its_clock(tmp_path: pathlib.Path) -> None:
    """M14, invariant OR1: a rule that names no family, a rule beside a census that is not its two offsets, and a rule on
    a column read on its own clock (one offset, so contract rule D5 lets it stand there) are each refused."""
    header, rows = _eastern_visits(400, 400, 41, 2023, 2)
    source = tmp_path / "plain.csv"
    source.write_bytes(zoo.csv_bytes(header[1:], [row[1:] for row in rows]))
    document = profile.build_document(reading.read_table(str(source)), taxonomy.Settings(), [])
    assert document["columns"][0]["offset_rule"] == "us -05:00", "premise: the column publishes its rule"
    contract.load_profile(str(fixtures.write_profile(tmp_path, "kept-profile.json", document)))
    present = document["columns"][0]["n_present"]
    for place, changes in enumerate((
        {"offset_rule": "mars -05:00"},
        {"offset_rule": "eu +01:00"},
        {"datetimes_read_at": "local", "utc_offsets": {"-05:00": present}},
    )):
        changed = json.loads(json.dumps(document))
        changed["columns"][0].update(changes)
        with pytest.raises(errors.ProfileError, match="offset_rule"):
            contract.load_profile(str(fixtures.write_profile(tmp_path, f"changed{place}-profile.json", changed)))


def test_a_pooled_twin_off_its_rule_is_named_by_validate(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """M16 (`grains.keeps_the_rule`): G7.4r withdrawn from the generator on a person's visits pooled at the quarter, the
    bucket starts spent by counts, and `offsets.rule` misses: the twin is read cell by cell before its grain (contract
    6.6.2), so a twin breaking the rule is coarsened as written and read as breaking it."""
    path, document = _person_document(tmp_path / "pooled", *_eastern_visits(600, 60, 43, 2023, 2))
    block = [column for column in document["columns"] if column["name"] == "seen_at"][0]
    assert (block.get("time_grain") or {}).get("rung") in (grains.MONTH, grains.QUARTER), "premise: pooled"
    assert block["offset_rule"] == "us -05:00", "premise: the rule read at the grain"
    monkeypatch.setattr(generation, "_column_rule", lambda column, facts: None)
    monkeypatch.setattr(generation, "_grain_rule", lambda column: None)
    assert _quiet(["generate", f"{path}", "--replace", "--seed", "0"], False) == 0
    assert _quiet(["validate", f"{path}", "--replace"], False) == 3
    quality = (tmp_path / "pooled" / "visits-twin-quality.txt").read_text(encoding="utf-8")
    assert "offsets.rule [datetime.offset_rule]: MISSED" in quality


def test_a_column_pooled_at_the_year_keeps_its_description_without_the_rule(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """M17 (`grains.two_offsets`): every year's bucket starts in winter, so under the rule its starts would wear one
    offset; the coarse column keeps each cell's own offset instead, as it was described before the rule, and publishes
    no rule."""
    _path, document = _person_document(tmp_path / "with", *_eastern_visits(1000, 100, 47, 2004, 20))
    block = [column for column in document["columns"] if column["name"] == "seen_at"][0]
    assert (block.get("time_grain") or {}).get("rung") == grains.YEAR, "premise: the column pools at the year"
    assert "offset_rule" not in block and sorted(block["utc_offsets"]) == ["-04:00", "-05:00"]
    monkeypatch.setattr(grains, "cell_rule", lambda rule_text, reading_: None)
    _path, without = _person_document(tmp_path / "without", *_eastern_visits(1000, 100, 47, 2004, 20))
    assert [column for column in without["columns"] if column["name"] == "seen_at"][0] == block


# -- repair 2: one definition admits a rule, and the raw cells decide it (Codex's items 3, 4, 6, 7 and 8) ----------


def _admitted_by_hand(standard: int) -> bool:
    """The admission written from P4-D474's own words: -12:00 to +13:00, the minutes 00, 30 or 45."""
    return -12 * 3600 <= standard <= 13 * 3600 and abs(standard) % 3600 in (0, 1800, 2700)


def _seasons_table(standard: int) -> "reading.Table":
    """48 events, January and July noons: a northern column (winter at ``standard``) and a southern one."""
    north: "list[str]" = []
    south: "list[str]" = []
    winter, summer = offset_rules.offset_text(standard), offset_rules.offset_text(standard + 3600)
    for index in range(48):
        month = (1, 7)[index % 2]
        day = 1 + index // 2
        north += [f"2024-{month:02d}-{day:02d} 12:00:00" + (winter if month == 1 else summer)]
        south += [f"2024-{month:02d}-{day:02d} 12:00:00" + (summer if month == 1 else winter)]
    keys = [f"EV{900000 + index}" for index in range(48)]
    return reading.Table(
        ["event_ref", "north_ts", "south_ts"], [keys, north, south], 48, dialect.ENCODING_UTF8, False,
        reading.HEADER_FROM_FILE, reading._TAKEN_BY_CONVENTION, True,
    )


def test_one_definition_admits_a_rule_in_inference_publication_generation_and_validation() -> None:
    """Codex's items 7 and 8, generated: every pair of offsets an hour apart from -14:00 to +14:00 by quarter hours,
    and pairs at minutes no zone wears (:01, :07, :59), north and south of the equator. Inference reads a rule exactly
    where P4-D474's admission does (-12:00 to +13:00, minutes 00, 30 or 45); the producer publishes it, the loader
    takes it, the twin's offsets under it are each in force (generation) and read back as the same rule (validation);
    every other column keeps its description without a rule and profiles (at -13:00 the profile aborted on the
    publication guard: inference admitted what publication refused)."""
    standards = list(range(-14 * 3600, 13 * 3600 + 1, 900)) + [60, -420, 3540, 12 * 3600 + 60]
    years: "dict[tuple[str, int, int], tuple[int, int]]" = {}
    draw = random.Random(83)
    admitted = 0
    for standard in standards:
        document = profile.build_document(_seasons_table(standard), taxonomy.Settings(), ["event_ref"])
        loaded = contract._validated(document)
        for name, family in (("north_ts", "us"), ("south_ts", "au")):
            block = [column for column in document["columns"] if column["name"] == name][0]
            wanted = f"{family} {offset_rules.offset_text(standard)}" if _admitted_by_hand(standard) else ""
            assert block.get("offset_rule", "") == wanted, (standard, name, block.get("offset_rule"))
            facts = [column for column in loaded.columns if column.name == name][0].facts
            assert isinstance(facts, contract.DatetimeFacts) and facts.offset_rule == wanted, (standard, name)
            if not wanted:
                continue
            admitted += 1
            rule = offset_rules.parsed_rule(wanted)
            assert rule is not None and offset_rules.admitted(rule)
            clock = generation._RuleClock(rule, "")
            pairs: "list[tuple[str, str]]" = []
            for _instant in range(120):
                instant = 1230768000 + draw.randrange(22 * 365 * 86400)
                worn = generation._rule_offset_at(clock, instant, years)
                local = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=instant + worn)
                pairs += [(local.strftime("%Y-%m-%d %H:%M:%S"), offset_rules.offset_text(worn))]
            assert all(offset_rules.offset_seconds(key) in offset_rules.in_force(rule, offset_rules.local_seconds(text) or 0)
                       for text, key in pairs), (standard, family)
            assert offset_rules.parsed_rule(offset_rules.rule_of(pairs)) in (
                rule, offset_rules.Rule("eu" if family == "us" else "nz", standard)), (standard, family)
    assert admitted == 2 * sum(1 for standard in standards if _admitted_by_hand(standard))


def test_a_rule_is_read_off_the_offsets_the_cells_wear_not_the_census() -> None:
    """Codex's item 4, generated over offset pairs: a column of two offsets an hour apart at the offsets in force reads
    its rule; the same column with ONE more cell at a third offset, which the census absorbs into the commonest, reads
    none (10,000 January stamps at -05:00, 9,999 July stamps at -04:00 and one January stamp at -06:00 published
    `us -05:00`)."""
    for standard in range(-12 * 3600, 13 * 3600 + 1, 1800):
        winter, summer = offset_rules.offset_text(standard), offset_rules.offset_text(standard + 3600)
        pairs = [("2024-01-15 12:00:00", winter)] * 40 + [("2024-07-15 12:00:00", summer)] * 39
        for third, odd in ((standard - 3600, "2024-01-15 12:00:00"), (standard + 7200, "2024-07-15 12:00:00")):
            if not -14 * 3600 <= third <= 14 * 3600:
                continue
            for extra in ([], [(odd, offset_rules.offset_text(third))]):
                cells = pairs + extra
                sources = [text.replace(" ", "T") + key for text, key in cells]
                details = taxonomy._datetime_details("iso-datetime", cells, sources, 0, taxonomy.Settings())
                published = details.get("offset_rule", "")
                assert published == ("" if extra else f"us {winter}"), (standard, third, extra, published)


def _codex_months(rows: int, people: int) -> "tuple[list[str], list[list[str]]]":
    """Codex's table of item 3 (codex-w3/verdict-DST.md), its generator as written: a person's 2024 visits at US
    Eastern's offsets in force, March on its 1st to 9th, November on its 1st and 2nd, every other month on its 1st to
    28th, so each month's stamps wear one offset and the column pools at the month under `us -05:00`."""
    draw = random.Random(701)
    found: "list[list[str]]" = []
    for index in range(rows):
        month = index % 12 + 1
        day = draw.randrange(1, 10) if month == 3 else draw.randrange(1, 3) if month == 11 else draw.randrange(1, 29)
        offset = "-04:00" if 4 <= month <= 11 else "-05:00"
        clock = f"{draw.randrange(24):02d}:{draw.randrange(60):02d}:{draw.randrange(60):02d}"
        found += [[f"PT{500000 + index % people}", f"2024-{month:02d}-{day:02d} {clock}{offset}"]]
    return ["patient_ref", "seen_at"], found


def _validated_with(
    path: pathlib.Path, change: "dict[int, str]", checked: "tuple[list[str], list[list[str]]] | None" = None
) -> str:
    """The quality text of one file checked against the description at ``path``: the twin generated at seed 0, or the
    rows ``checked`` (header and body) where given, with the named rows' cells of `seen_at` replaced."""
    twin = path.parent / path.name.replace("-profile.json", "-twin.csv")
    if checked is None:
        assert _quiet(["generate", f"{path}", "--replace", "--seed", "0"], False) == 0
        with twin.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle))
    else:
        rows = [list(checked[0])] + [list(row) for row in checked[1]]
    place = rows[0].index("seen_at")
    for row, cell in change.items():
        rows[row][place] = cell
    twin.write_bytes(zoo.csv_bytes(rows[0], rows[1:]))
    _quiet(["validate", f"{path}", "--replace"], False)
    return path.parent.joinpath(path.name.replace("-profile.json", "-twin-quality.txt")).read_text(encoding="utf-8")


def test_a_twin_cell_in_the_skipped_hour_is_named_before_its_grain(tmp_path: pathlib.Path) -> None:
    """Codex's item 3 on its own shape and its own probe (the 20,000-row table is K-HZ-27's): the column pools at the
    month under its rule, and the file checked is its own rows with one March cell replaced by
    `2024-03-10 02:30:00-05:00`, in the hour the clocks skip. Coarsened at its own offset that cell named the valid
    bucket start `2024-03-01 00:00:00-05:00`, every other March cell wearing the winter offset too, and the column read
    back at its grain passed the rule. The verdict is now read off the cells as written, before the grain: the rows as
    they are hold the rule, and with that cell `offsets.rule` misses."""
    header, rows = _codex_months(1200, 100)
    path, document = _person_document(tmp_path / "months", header, rows)
    block = [column for column in document["columns"] if column["name"] == "seen_at"][0]
    assert (block.get("time_grain") or {}).get("rung") == grains.MONTH and block["offset_rule"] == "us -05:00"
    assert "offsets.rule [datetime.offset_rule]: HELD" in _validated_with(path, {}, (header, rows))
    broken = _validated_with(path, {3: "2024-03-10 02:30:00-05:00"}, (header, rows))
    # ...on the cells as written and at the grain alike: neither reading passes it.
    assert "offsets.rule [datetime.offset_rule]: MISSED" in broken
    assert "offsets.rule [datetime.offset_rule]: HELD" not in broken


def test_a_published_rule_is_checked_over_its_familys_whole_calendar(tmp_path: pathlib.Path) -> None:
    """Codex's item 6: a source of 2099 alone reads `us -05:00` (its years are the family's); the twin's tail of one
    stamp in January 2100 and one in December 2098 wears the offsets the family's calendar puts in force there, as the
    generator extrapolates it, and validate holds the rule (it missed it: the check read the rule again only over the
    years a rule is inferred on)."""
    draw = random.Random(89)
    rows: "list[list[str]]" = []
    while len(rows) < 600:
        local = datetime.datetime(2099, 1, 1) + datetime.timedelta(seconds=draw.randrange(364 * 86400))
        here = _wall_offsets("us", -5 * 3600, local)
        if here:
            rows += [[f"EV{800000 + len(rows)}", local.strftime("%Y-%m-%d %H:%M:%S") + offset_rules.offset_text(here[0])]]
    folder = tmp_path / "far"
    folder.mkdir()
    source = folder / "events.csv"
    source.write_bytes(zoo.csv_bytes(["event_ref", "seen_at"], rows))
    assert _quiet(["profile", f"{source}", "--replace", "--identifier", "event_ref"], False) == 0
    path = folder / "events-profile.json"
    block = [column for column in json.loads(path.read_text())["columns"] if column["name"] == "seen_at"][0]
    assert block["offset_rule"] == "us -05:00" and "time_grain" not in block, "premise: the rule at its own precision"
    quality = _validated_with(path, {1: "2100-01-03 10:00:00-05:00", 2: "2098-12-30 10:00:00-05:00"})
    assert "offsets.rule [datetime.offset_rule]: HELD" in quality
    quality = _validated_with(path, {1: "2100-07-03 10:00:00-05:00"})
    assert "offsets.rule [datetime.offset_rule]: MISSED" in quality
    # ...and a file of one offset alone, every stamp in force, is no column of the rule: both offsets are worn.
    winter = {row: f"2099-01-{1 + row % 28:02d} 10:00:00-05:00" for row in range(1, 601)}
    assert "offsets.rule [datetime.offset_rule]: MISSED" in _validated_with(path, winter)


def test_a_tail_before_its_familys_first_year_keeps_the_rule(tmp_path: pathlib.Path) -> None:
    """Codex's item 6 at its other end, built as a unit case: a source of 1987 alone, the first year the US rule of
    1987 to 2006 is admitted, reads `us -05:00`; a twin's tail at `1986-12-31 23:48:32-05:00`, a year before the
    family's own, wears the offset its nearest era puts in force there, as the generator writes it, and validate holds
    the rule (it missed it: the check read the rule again only over the years a rule is inferred on); a July 1986 stamp
    at the standard offset is still named."""
    draw = random.Random(97)
    rows: "list[list[str]]" = []
    while len(rows) < 600:
        local = datetime.datetime(1987, 1, 1) + datetime.timedelta(seconds=draw.randrange(364 * 86400))
        here = _wall_offsets("us", -5 * 3600, local)
        if here:
            rows += [[f"EV{810000 + len(rows)}", local.strftime("%Y-%m-%d %H:%M:%S") + offset_rules.offset_text(here[0])]]
    folder = tmp_path / "early"
    folder.mkdir()
    source = folder / "events.csv"
    source.write_bytes(zoo.csv_bytes(["event_ref", "seen_at"], rows))
    assert _quiet(["profile", f"{source}", "--replace", "--identifier", "event_ref"], False) == 0
    path = folder / "events-profile.json"
    block = [column for column in json.loads(path.read_text())["columns"] if column["name"] == "seen_at"][0]
    assert block["offset_rule"] == "us -05:00" and "time_grain" not in block, "premise: the rule at its own precision"
    assert "offsets.rule [datetime.offset_rule]: HELD" in _validated_with(path, {1: "1986-12-31 23:48:32-05:00"})
    assert "offsets.rule [datetime.offset_rule]: MISSED" in _validated_with(path, {1: "1986-07-01 10:00:00-05:00"})


def test_the_census_step_shares_by_weight_none_past_its_cap_and_counts_what_it_achieved() -> None:
    """Codex's item 5: `_capped_shares([1, 1], [100, 100], 13)` gave 6 and 6, the weights read as rooms; two runs of 100
    winter ranks each offering one summer second beside 1,000 winter seconds met a summer census of 13 with 12 ranks
    and said nothing. Now the weights are weights and the caps caps (3,000 generated draws), the census is met exactly,
    and a census the runs cannot hold is the report's, with the count achieved."""
    import types

    assert generation._capped_shares([1, 1], [100, 100], 13) == [7, 6]
    draw = random.Random(97)
    for _case in range(3000):
        size = draw.randrange(1, 7)
        weights = [draw.choice((0, 1, 2, 5, 1000, 86400)) for _place in range(size)]
        caps = [draw.randrange(0, 40) for _place in range(size)]
        owed = draw.randrange(0, 120)
        shares = generation._capped_shares(weights, caps, owed)
        reach = sum(caps[place] for place in range(size) if weights[place] > 0)
        assert all(0 <= shares[place] <= caps[place] for place in range(size)), (weights, caps, owed, shares)
        assert sum(shares) == min(owed, reach), (weights, caps, owed, shares)
    rule = offset_rules.Rule("us", -18000)
    clock = generation._RuleClock(rule, "")
    starts = [offset_rules.changes(rule, year)[0] for year in (2023, 2024)]
    ordinals: "list[int]" = []
    lows: "list[int]" = []
    highs: "list[int]" = []
    pins: "set[int]" = set()
    for start in starts:
        pins.add(len(ordinals))
        ordinals += [start - 1001]
        lows += [start - 1001]
        highs += [start - 1001]
        for rank in range(100):
            ordinals += [start - 1000 + rank * 9]
            lows += [start - 1001]
            highs += [start]
        pins.add(len(ordinals))
        ordinals += [start + 1]
        lows += [start + 1]
        highs += [start + 1]
    layout = types.SimpleNamespace(low=None, high=None, listed={})
    for wanted, achieved in ((13, 13), (250, 202)):
        facts = types.SimpleNamespace(
            utc_offsets={"-04:00": wanted, "-05:00": len(ordinals) - wanted}, offset_rule="us -05:00"
        )
        moved, notes = generation._census_by_rule(
            types.SimpleNamespace(name="t"), facts, clock, list(ordinals), (lows, highs), layout, set(pins)
        )
        summer = sum(1 for value in moved if generation._rule_summer(clock, value, {}))
        assert summer == achieved, (wanted, summer)
        assert (notes == []) == (wanted == achieved), (wanted, notes)
        if notes:
            assert notes[0].achieved == f"{achieved} written at it", notes[0]
    # ...and a run whose summer side is two stretches of one second each, a winter between, takes three: all three are
    # given (by width alone, never capped at it), the run stays in order and none is left unplaced.
    first_end = offset_rules.changes(rule, 2023)[1]
    second_start = offset_rules.changes(rule, 2024)[0]
    stretches = [(first_end - 1, first_end - 1, True), (first_end, second_start - 1, False), (second_start, second_start, True)]
    before = sorted(first_end + 5000 + 997 * rank for rank in range(40))
    moved = list(before)
    generation._run_laid_out(moved, 0, len(moved), stretches, 3)
    assert moved == sorted(moved)
    assert sum(1 for value in moved if generation._rule_summer(clock, value, {})) == 3, moved


def test_every_bucket_of_a_fall_back_day_draws_inside_itself(oracle: "dict[str, object]") -> None:
    """Codex's item 2, generated: every minute bucket of a fall-back day and every second bucket of its repeated hour and
    the two minutes either side, four families: each draw stays in its bucket's wall clock at an offset in force there,
    a bucket inside the repeated hour draws both its occurrences, and the product draws as the oracle does (A-P4-59).
    The minute bucket 01:59 of 2024-11-03 under `us -05:00` and the word 2**63 drew 01:29:30-05:00: its instants ran
    from the first occurrence's 01:59 to the second occurrence's end, the whole second occurrence among them."""
    reading_ = grains.Reading(grains.STAMP, "iso-datetime")
    draw = random.Random(101)
    for family, standard in (("us", -18000), ("eu", 3600), ("au", 36000), ("nz", 43200)):
        rule = offset_rules.Rule(family, standard)
        back = offset_rules.changes(rule, 2024)[1]
        day = (back + standard) // 86400 * 86400
        repeated = back + standard
        buckets = [(grains.MINUTE, day + 60 * step) for step in range(1440)]
        buckets += [(grains.SECOND, repeated - 120 + step) for step in range(3840)]
        both = 0
        for rung, local in buckets:
            here = offset_rules.in_force(rule, local)
            stamp = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=local)
            cell = stamp.strftime("%Y-%m-%d %H:%M:%S") + offset_rules.offset_text(here[0])
            seen: "set[str]" = set()
            for word in (0, 2**63, 2**64 - 1):
                made = grains.drawn_inside(cell, reading_, rung, word, rule)
                read = parsing.parse_datetime(made, "iso-datetime")
                assert read is not None, (cell, word)
                wall = offset_rules.local_seconds(read[0])
                assert wall is not None and offset_rules.offset_seconds(read[1]) in offset_rules.in_force(rule, wall)
                assert wall - wall % (60 if rung == grains.MINUTE else 1) == local, (cell, rung, word, made)
                seen.add(read[1])
            if local % 13 == 0:
                word = draw.getrandbits(64)
                made = grains.drawn_inside(cell, reading_, rung, word, rule)
                theirs = oracle["pooled_drawn_inside"](cell, "iso-datetime", rung, word, (family, standard, rung))
                assert made == theirs, (cell, rung, word)
            both += len(seen) == 2
        assert both >= 60 + 3600, (family, both)


def _fall_back_run(draw: random.Random, clock: "generation._RuleClock") -> "tuple[list[int], list[int], list[int], set[int]]":
    """Sorted instants across a change where the clocks go back, at a pooled rung, pins at both ends and a few inside,
    none in a dead hour (a pin is a bucket's start, which never stands in one)."""
    back = offset_rules.changes(clock.rule, draw.randrange(2010, 2030))[1]
    reach = {grains.SECOND: 4000, grains.MINUTE: 5400, grains.HOUR: 3 * 86400, grains.DAY: 9 * 86400,
             grains.MONTH: 80 * 86400}[clock.rung]
    size = draw.randrange(20, 160)
    ordinals = sorted(back - reach + draw.randrange(2 * reach) for _rank in range(size))
    ordinals = [back - reach - 1] + ordinals + [back + reach + 1]
    pins = {0, len(ordinals) - 1}
    lows = [0] * len(ordinals)
    highs = [0] * len(ordinals)
    live = [rank for rank in range(len(ordinals)) if not generation._rule_dead(clock, ordinals[rank], {})]
    marks = sorted(pins | {draw.choice(live) for _pin in range(draw.randrange(0, 3))})
    for left, right in zip(marks, marks[1:]):
        for rank in range(left, right + 1):
            lows[rank], highs[rank] = ordinals[left], ordinals[right]
    for pin in marks:
        lows[pin] = highs[pin] = ordinals[pin]
    return ordinals, lows, highs, set(marks)


def test_the_census_is_counted_as_the_twin_is_read_back_at_every_rung_of_a_fall_back(oracle: "dict[str, object]") -> None:
    """Codex's item 1 and the verify's fragility, generated: 400 runs across a fall-back change, four families, the
    hour, minute and second rungs beside the day and the month; after the dead hour is left (`_off_dead_hours`), the
    census step and the cut gaps, every rank's census side is the side its written wall clock is read back on, no
    rank stands in a dead hour or outside its cut gap, the count read back is the census or the step names the
    shortfall, and the oracle takes every step alike on a quarter of them, the cut gaps on a twentieth (A-P4-59).
    Under `us -05:00` at the minute rung a rank of the second occurrence was counted winter while its written
    `01:30-05:00` read back as summer time's bucket."""
    import types

    draw = random.Random(103)
    years: "dict[tuple[str, int, int], tuple[int, int]]" = {}
    dead_seen = 0
    for case in range(400):
        family, standard = (("us", -18000), ("eu", 3600), ("au", 36000), ("nz", 43200))[case % 4]
        rung = (grains.HOUR, grains.MINUTE, grains.SECOND, grains.DAY, grains.MONTH)[case % 5]
        clock = generation._RuleClock(offset_rules.Rule(family, standard), rung)
        theirs_clock = (family, standard, rung)
        ordinals, lows, highs, pins = _fall_back_run(draw, clock)
        dead_seen += any(generation._rule_dead(clock, value, years) for value in ordinals)
        body = (0, len(ordinals) - 1)
        snapped = generation._off_dead_hours(clock, list(ordinals), (lows, highs), pins, body)
        mirrored = case % 4 == 0
        if mirrored:
            assert snapped == oracle["off_dead_hours"](theirs_clock, list(ordinals), lows, highs, pins, 0, len(ordinals) - 1)
        assert snapped == sorted(snapped), case
        summer = sum(1 for value in snapped if generation._rule_summer(clock, value, years))
        wanted = max(0, min(len(snapped), summer + draw.randrange(-len(snapped) // 4, len(snapped) // 4 + 1)))
        census = {offset_rules.offset_text(standard + 3600): wanted, offset_rules.offset_text(standard): len(snapped) - wanted}
        facts = types.SimpleNamespace(utc_offsets=census, offset_rule=f"{family} {offset_rules.offset_text(standard)}")
        layout = types.SimpleNamespace(low=None, high=None, listed={})
        moved, notes = generation._census_by_rule(
            types.SimpleNamespace(name="t"), facts, clock, list(snapped), (lows, highs), layout, set(pins)
        )
        block = {"utc_offsets": census, "heavy_dates": [], "low_tail": None, "high_tail": None}
        cut_lows, cut_highs = generation._gaps_cut_at_changes(clock, moved, lows, highs, len(moved))
        whole = [False] * len(moved)
        back = generation._rule_read_back(clock, moved, whole, len(moved))
        if mirrored:
            assert moved == oracle["census_by_rule"](block, theirs_clock, list(snapped), lows, highs, set(pins), len(snapped))
            if case % 20 == 0:
                assert (cut_lows, cut_highs) == oracle["gaps_cut_by_rule"](theirs_clock, moved, lows, highs, len(moved))
            assert back == oracle["rule_read_back"](theirs_clock, moved, whole, len(moved))
        for rank, value in enumerate(moved):
            assert not generation._rule_dead(clock, value, years), (case, rank)
            assert cut_lows[rank] <= value <= cut_highs[rank], (case, rank)
            assert not generation._rule_dead(clock, cut_lows[rank], years), (case, rank)
            worn = generation._rule_offset_at(clock, value, years)
            side = generation._rule_side(clock, value + worn, years) == standard + 3600
            assert side == generation._rule_summer(clock, value, years), (case, rank, value)
        assert (back == wanted) == (notes == []), (case, back, wanted, notes)
    assert dead_seen > 80, "premise: the runs reach the dead hours"


def _fall_back_visits(
    family: str, standard: int, rows: int, people: int, reach: "tuple[tuple[int, int], ...]", seed: int,
    fraction: bool = False,
) -> "tuple[list[str], list[list[str]]]":
    """A person's stamps drawn evenly among the INSTANTS of ``reach`` (seconds from a fall-back change of 2024, each pair
    a span), each at the offset in force there by the gate's own calendar, so both occurrences of the repeated hour are
    written where the spans reach them."""
    _start, back = _spans(family, standard, 2024)
    draw = random.Random(seed)
    found: "list[list[str]]" = []
    for index in range(rows):
        low, high = draw.choice(reach)
        moment = back + datetime.timedelta(seconds=draw.randrange(low, high))
        year = (moment + datetime.timedelta(seconds=standard)).year
        summer_start, summer_end = _spans(family, standard, year)
        if family in ("au", "nz"):
            summer = moment < summer_end or moment >= summer_start
        else:
            summer = summer_start <= moment < summer_end
        offset = standard + 3600 if summer else standard
        local = moment + datetime.timedelta(seconds=offset)
        clock = local.strftime("%Y-%m-%d %H:%M:%S") + (f".{draw.randrange(1000):03d}" if fraction else "")
        found += [[f"PT{700000 + index % people}", clock + offset_rules.offset_text(offset)]]
    return ["patient_ref", "seen_at"], found


def _verdicts(quality: str, prefixes: "tuple[str, ...]") -> "dict[str, str]":
    """Each subcheck of the quality text whose name starts with one of the prefixes, and its verdict."""
    found: "dict[str, str]" = {}
    for line in quality.splitlines():
        text = line.strip()
        if text.startswith(prefixes) and "]: " in text:
            found[text.split(" ")[0]] = text.rsplit("]: ", 1)[1]
    return found


@pytest.mark.parametrize("family,standard", (("us", -18000), ("eu", 3600), ("au", 36000)))
def test_a_fall_back_pooled_at_the_hour_keeps_its_census_and_midnight_count(
    tmp_path: pathlib.Path, family: str, standard: int
) -> None:
    """Codex's item 1 at the hour rung, three families (the 20,000-row tables are K-HZ-27's): stamps within twelve hours
    of a fall-back change pool at the hour under their rule; the twin's rule, offset census and count at midnight are
    the published ones (the verify's hour-rung tables missed the census by 173 and 22 cells, and the European one
    its midnight count, 1,060 against 828), and no cell is off its date."""
    header, rows = _fall_back_visits(family, standard, 2400, 200, ((-12 * 3600, 12 * 3600),), 7)
    path, document = _person_document(tmp_path / family, header, rows)
    block = [column for column in document["columns"] if column["name"] == "seen_at"][0]
    assert (block.get("time_grain") or {}).get("rung") == grains.HOUR, block.get("time_grain")
    assert block["offset_rule"] == f"{family} {offset_rules.offset_text(standard)}"
    found = _verdicts(_validated_with(path, {}), ("offsets.", "midnight."))
    assert found and set(found.values()) == {"HELD"}, found
    rule = offset_rules.parsed_rule(block["offset_rule"])
    assert rule is not None and _off(_column(path.parent / "visits-twin.csv", "seen_at"), rule) == 0


def test_a_rule_is_not_admitted_finer_than_the_hour_across_a_fall_back(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Codex's item 1 below the hour: each minute or second bucket of a repeated hour holds both its occurrences while
    its start names the first alone, so no twin keeps both its census and its buckets' counts. A column read under its
    rule at the minute rung -- Codex's shape, local stamps from 01:55 to 02:04:59 on a fall-back day, as forcing the
    admission shows -- is walked again as without the rule and keeps that description byte for byte (RULINGS 3's
    general rule): the same block as a profile with no rule read at all. The second rung is refused the same way, and
    a span the clocks do not go back in, or a rung of an hour or more, keeps its rule."""
    header, rows = _fall_back_visits("us", -18000, 2000, 100, ((-300, 0), (3300, 3900)), 11)
    with monkeypatch.context() as forced:
        forced.setattr(profile, "_rule_admitted_at", lambda rule_text, span: True)
        _path, admitted = _person_document(tmp_path / "forced", header, rows)
    block = [column for column in admitted["columns"] if column["name"] == "seen_at"][0]
    assert (block.get("time_grain") or {}).get("rung") == grains.MINUTE and block.get("offset_rule") == "us -05:00"
    _path, document = _person_document(tmp_path / "ruled", header, rows)
    block = [column for column in document["columns"] if column["name"] == "seen_at"][0]
    assert "offset_rule" not in block
    with monkeypatch.context() as plain:
        plain.setattr(offset_rules, "rule_of", lambda pairs: "")
        _path, without = _person_document(tmp_path / "plain", header, rows)
    assert [column for column in without["columns"] if column["name"] == "seen_at"][0] == block
    nanoseconds = 10**9
    back = offset_rules.changes(offset_rules.Rule("us", -18000), 2024)[1] - 18000
    for rung, first, last, admitted_here in (
        (grains.SECOND, back + 3590, back + 3610, False), (grains.MINUTE, back - 600, back + 300, False),
        (grains.MINUTE, back + 7200, back + 9000, True), (grains.HOUR, back - 7200, back + 7200, True),
        (grains.SECOND, back - 7200, back - 3700, True),
    ):
        span = (rung, first * nanoseconds, last * nanoseconds)
        assert profile._rule_admitted_at("us -05:00", span) == admitted_here, (rung, first - back, last - back)


def test_a_census_the_twin_does_not_read_back_is_the_reports(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's item 1, the count said once more as the twin is read back: with the census step withdrawn and its own
    line with it (a mutant), the hour-rung twin's census misses at validate and its report still names the shortfall --
    the line is counted off the twin's own written buckets after every pass, never an empty list (the report named
    nothing while the twin read back 14,916 and 5,084 against 10,100 and 9,900)."""
    header, rows = _fall_back_visits("us", -18000, 2400, 200, ((-12 * 3600, 12 * 3600),), 7)
    path, _document = _person_document(tmp_path / "left", header, rows)
    monkeypatch.setattr(generation, "_census_by_rule", lambda column, facts, clock, ordinals, gaps, layout, fixed: (ordinals, []))
    found = _verdicts(_validated_with(path, {}), ("offsets.",))
    assert found["offsets.-04:00"] == "MISSED" and found["offsets.rule"] == "HELD", found
    report = (path.parent / "visits-twin-report.txt").read_text(encoding="utf-8")
    assert "values at summer time's offset under the rule us -05:00" in report


def test_a_row_filling_the_count_stays_on_its_side_of_the_census(
    tmp_path: pathlib.Path, oracle: "dict[str, object]", monkeypatch: pytest.MonkeyPatch
) -> None:
    """The verify's item 1: method G7.13 fills a pooled column's count of different values by moving rows to empty
    buckets between the same two published points; under a rule it moved a row from a winter month to an empty summer
    one (the statistics check's event table: `nz_iso` 11,637 at summer time's offset against 11,636 published). A
    south-eastern column at the month, published points at May 2019 and January 2020, rows in every month between but
    December (summer time), the only spare rows in September (winter): no row moves, the census stands and the count gives
    way, said for the report (`_count_short_by_rule`); without the rule a September row filled
    December, both months starting on a Sunday as the weekday census keeps them.
    The twin of the case's own shaped column, made by `generation.generate_held`, names that cause for `seen_at` (the
    scoped verify 2's item 3, P4-D369 (a)'s order: the census stands and the count gives way, named), red where
    generation drops its give-way line (the verify's mutant M1c).
    And `grains.count_filled` keeps every move on its side as the oracle does (A-P4-59), 400 generated cases."""
    _path, document = _person_document(tmp_path / "south", *_southern_visits(3000, 300, 53))
    loaded = contract._validated(document)
    column = [block for block in loaded.columns if block.name == "seen_at"][0]
    assert column.time_grain is not None and isinstance(column.facts, contract.DatetimeFacts)
    assert column.facts.offset_rule == "au +10:00"
    nanoseconds = 10**9

    def month(year: int, number: int) -> int:
        return parsing.days_from_civil(year, number, 1) * 86400 * nanoseconds

    first, last = month(2019, 5), month(2020, 1)
    rungs = tuple(["2019-05-01 00:00:00"] * 5 + ["2020-01-01 00:00:00"] * 6)
    ladder = contract.DateLadder(rungs, None, *rungs[1:10], None)
    facts = dataclasses.replace(column.facts, date_percentiles=ladder, low_tail=None, high_tail=None, heavy_dates=())
    grain = dataclasses.replace(column.time_grain, rung=grains.MONTH, spans=((grains.MONTH, first, last),))
    shaped = dataclasses.replace(column, facts=facts, time_grain=grain, n_distinct=9)
    cells = [f"2019-{number:02d}-15 10:00:00+10:00" for number in (5, 6, 7, 8, 9, 9, 9, 10, 11)]
    cells += ["2020-01-15 10:00:00+11:00"]
    written = generation._filled_to_the_count(shaped, cells, ())
    assert not [cell for cell in written if cell.startswith("2019-12")], written
    assert generation._count_short_by_rule(shaped, cells, ())
    unruled = dataclasses.replace(shaped, facts=dataclasses.replace(facts, offset_rule=""))
    assert [cell for cell in generation._filled_to_the_count(unruled, cells, ()) if cell.startswith("2019-12")]
    assert not generation._count_short_by_rule(unruled, cells, ())
    # THE TWIN OF THE CASE'S OWN SHAPED COLUMN (the scoped verify 2's item 3): the loaded profile with that column
    # replaced, through `generation.generate_held`. Two things are set by hand, each for a measured reason. The
    # column's built cells are the case's own, with the rest of its rows at its first published point (May 2019, a
    # bucket a published point names, which gives no row): the description's machinery writes this hand-shaped
    # block at one value (one different value at seeds 0, 1 and 7). And its count is read as held exactly: a rule
    # column's count is judged inside G12.5's envelope, never exactly (two offsets, so
    # `contract.datetime_counts_reachable` is False), and here the envelope (2 to 28) holds both the published 9
    # and the twin's 8, so the report settles the count's line and its cause with it (R-P4-152).
    padded = cells + [cells[0]] * (shaped.n_present - len(cells))
    real_content = generation._content_of
    judged = contract.datetime_count_held_exactly

    def built(plan: object, words: "list[int]", short: object = None, readings: object = None) -> object:
        content, notes = real_content(plan, words, short, readings)  # type: ignore[arg-type]
        return (list(padded) if plan.column.name == "seen_at" else content), notes  # type: ignore[attr-defined]

    with monkeypatch.context() as handed:
        handed.setattr(generation, "_content_of", built)
        handed.setattr(contract, "datetime_count_held_exactly",
                       lambda block, published, window: block.name == "seen_at" or judged(block, published, window))
        replaced = tuple(shaped if block.name == "seen_at" else block for block in loaded.columns)
        twin = generation.generate_held(dataclasses.replace(loaded, columns=replaced), 0)
    twin_cells = generation.twin_column(twin, list(twin.names).index("seen_at"))
    assert len(twin_cells) == shaped.n_present, len(twin_cells)
    assert not [cell for cell in twin_cells if cell.startswith("2019-12")], twin_cells[:12]
    named = [deviation.note for deviation in twin.deviations if deviation.column == "seen_at"]
    assert generation._RULE_COUNT_SHORT in named, named
    draw = random.Random(107)
    rule = offset_rules.Rule("au", 36000)
    for _case in range(400):
        base = datetime.datetime(2018 + draw.randrange(4), 1, 1)
        starts = [base]
        for _one in range(draw.randint(6, 30)):
            starts += [oracle["pooled_bucket"](starts[-1], grains.MONTH)[1]]
        held = sorted(draw.sample(starts, draw.randint(2, len(starts))))
        rows: "list[datetime.datetime | None]" = []
        for bucket in held:
            rows += [bucket] * draw.choice((1, 1, 2, 3))
        draw.shuffle(rows)
        points = sorted(draw.sample(held, draw.randint(0, min(3, len(held)))))
        target = len(held) + draw.randint(1, 8)

        def moment(value: datetime.datetime) -> int:
            return int((value - datetime.datetime(1970, 1, 1)).total_seconds()) * nanoseconds

        mine = grains.count_filled(
            [None if row is None else moment(row) for row in rows], [moment(point) for point in points],
            (moment(starts[0]), moment(starts[-1])), grains.MONTH, grains.STAMP, grains.SECOND, target, {},
            (None, None), rule,
        )
        theirs = oracle["pooled_count_filled"](
            rows, points, starts[0], starts[-1], grains.MONTH, "stamp", "second", target, {}, (None, None),
            ("au", 36000, grains.MONTH),
        )
        assert mine == {row: moment(start) for row, start in theirs.items()}
        for row, start in mine.items():
            source = moment(rows[row])  # type: ignore[arg-type]
            sides = [offset_rules.in_force(rule, value // nanoseconds)[0] for value in (source, start)]
            assert sides[0] == sides[1], (rows[row], start)


def test_k_hz_27_counts_a_table_that_did_not_check_as_unchecked(monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's item 9, on its own probe: the driver of K-HZ-27 read each table's misses and analyst failures and never
    the steps' exits, so an `encounters` whose generation failed (empty misses, empty failures) counted its two
    columns as checked and right. Now a table whose profile, answers or generation did not complete, whose validate
    did not run, whose real side went unread or whose description lacks a column checked is unchecked, named in
    `checks_incomplete`, whose target is 0; a table that ran stays checked."""
    driver = runpy.run_path(str(REPOSITORY / "tools" / "measurements" / "kpi_zoo_offsets.py"))
    ran = {"steps": {"profile": {"exit": 0}, "answers": {"exit": 0}, "generate": {"exit": 0}, "validate": {"exit": 3}},
           "misses": [], "analyst": [], "analyst_real_errors": [], "roles": {}}
    results: "dict[str, dict[str, object]]" = {}
    for table, column, _check in driver["CHECKS"]:
        results.setdefault(table, json.loads(json.dumps(ran)))["roles"][column] = "datetime"  # type: ignore[index]
    probe = json.loads(json.dumps(results["encounters"]))
    probe["steps"]["generate"] = {"exit": 1, "error": "the probe's failure"}
    for failed in (probe, {"steps": {}, "misses": [], "analyst": []}):
        value = driver["tally"]({**results, "encounters": failed}, {}, None, 20000)
        assert value["checks_incomplete"] == 1 and value["checks_incomplete_named"].startswith("encounters:"), value
        assert value["columns_wrong"] == 0 and value["validate_misses"] == 0
    assert driver["tally"](results, {}, None, 20000)["checks_incomplete"] == 0
    unread = {**results, "fhir_observations": {**results["fhir_observations"], "analyst_real_errors": ["x"]}}
    assert driver["tally"](unread, {}, None, 20000)["checks_incomplete"] == 1
    lost = {**results, "hl7_obx": {**results["hl7_obx"], "roles": {}}}
    assert driver["tally"](lost, {}, None, 20000)["checks_incomplete_named"] == "hl7_obx: no column msh_7"
    invented = {"six_zones_even": {"ruled": 0, "off": 0, "misses": 0, "empty": 0, "minute": "", "why": "generate exit 1"}}
    assert driver["tally"](results, invented, None, 20000)["checks_incomplete"] == 1
