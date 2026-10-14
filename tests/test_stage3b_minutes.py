"""THE MINUTES' GATE (stage 3b landing 3b.4, lane T3, plan P4-D372): the minutes and seconds of a timestamp come back, met with the hour.

Before this landing a column of moments published nothing about the
minute of the hour or the second of the minute, and the twin drew them
evenly: clinic slots 70 per cent on :00 or :30 came back at 3 to 4 per
cent, cells written `HH:MM:00` came back with seconds at random. A column
of moments now publishes, beside its hour census, `minute_heaps` and
`minute_census` -- the minutes standing out and how the rest fall, in
groups the one merge rule chooses -- and, written to the second,
`second_heaps` and `second_census`; the loader holds them to MC1 to MC6,
SE1 to SE6, MH1, MH2, SH1 and SH2, the generator meets them (method
G7.3h, through G7.3g's one clock pass, and G7.3's drawing rule) and the
validator recounts them (V5-M1, V5-S1).

The clauses, each red on its own mutant (named beside it):

* `test_the_clock_battery_publishes_its_census` -- the heaped columns
  publish, the flat control publishes nothing and says nothing, the
  three-hour span is withheld with its sentence (MC4), and night charting
  on the hour beside day entries at any minute is withheld with its
  sentence (M3); every published census is the merge recomputed here from
  the cells, and the loader's own checks find nothing at the census line
  and at a floor of one (mutants: the span rule and the hour rule
  withdrawn);
* `test_the_clock_battery_twins_meet_their_census` -- at seeds 0 and 4
  nothing is MISSED, V5-M1 and V5-S1 are HELD on every published field,
  and the statistics hold: BOUND, CAP and SHAPE on the minute and second
  TVDs; INDEPENDENCE, in each hour group the share of each single-minute
  group within the bound and three sampling scales of the census share;
  and the twin's hour groups and weekdays are the ones the same seed
  writes with G7.3h withdrawn; the real table's own cells meet
  INDEPENDENCE, and 4,000 clinic slots meet it through KIN SHARES and
  miss it without;
* the frozen states of vectors file 20: the product gives every case the
  oracle's answer, and each case is red on its own mutant (`STEP_MUTANTS`);
* the witnesses: bursts keep their count through SUBSTITUTE, clinic slots
  through SPREAD, cells written `HH:MM:00` keep their seconds through the
  drawing rule, a pure grid keeps its heaps, and a flat twin misses the
  census; validating never produces a census of the clock;
* the loader's rules, one refused description each, and every
  description the producer writes on the battery loads at floors 1, 11
  and 36 (the producer-always-loads battery);
* the work: the producer's tests and the field passes are counted in
  operations up to 1,000,000 rows, machine-free;
* the review round's witnesses (the lane's skeptic 1): minutes depending
  on the hour publish where one count is closer to every hour than an even
  draw (M3's second question); a second census of a few values says so
  (NF120); the skeptic's fuzzed columns and small bursty tables keep their
  count, 2341173's misses the ceiling; heaps beside a withheld rest pin no
  lattice; a step off midnight keeps the drawing unit; and the second's kin
  keys hold each pair of groups apart -- each red on its own withdrawal.

Every table is built here or in `clock_field_shapes`, seeded and neutral
(plan D13).
"""

from __future__ import annotations

import collections
import copy
import dataclasses
import datetime
import importlib.util
import json
import pathlib
import random
import sys
import types

import pytest

import clock_field_shapes as shapes
import fixtures
import kpi_shapes
from synthtwin import (
    calendar_clock,
    calendar_rules,
    contract,
    errors,
    generation,
    profile,
    reading,
    rendering,
    taxonomy,
    validation,
)

REPOSITORY = pathlib.Path(__file__).resolve().parent.parent
VECTORS = REPOSITORY / "tests" / "reference" / "generation-branch-vectors-20.json"
ORACLE = REPOSITORY / "tools" / "reference" / "make_generation_reference_vectors.py"
SOURCE = pathlib.Path(generation.__file__).read_text(encoding="utf-8")
LINE = 11
DAY = 86400


# -- the battery --------------------------------------------------------------


@pytest.fixture(scope="module")
def thousand(tmp_path_factory: pytest.TempPathFactory) -> "tuple[kpi_shapes.Described, dict[str, tuple[list[str], str]], str]":
    columns = shapes.thousand()
    text = shapes.table_text(columns)
    described = kpi_shapes.describe(tmp_path_factory.mktemp("minutes"), "minutes", text, LINE)
    return described, columns, text


def _moment(cell: str, form: str) -> "datetime.datetime | None":
    try:
        return datetime.datetime.strptime(cell, form)
    except ValueError:
        return None


def _field_counts(cells: "list[str]", form: str, field: str) -> "list[int]":
    """How many cells fall on each value of a field, as written."""
    counts = [0] * 60
    for cell in cells:
        moment = _moment(cell, form)
        if moment is not None:
            counts[moment.minute if field == "minute" else moment.second] += 1
    return counts


def _tvd(first: "list[int]", second: "list[int]") -> float:
    one, two = sum(first), sum(second)
    return 0.5 * sum(abs(a / one - b / two) for a, b in zip(first, second))


def _restated_merge(bins: "list[int]", sure: "list[int]", line: int) -> "list[tuple[int, int, int]]":
    """The one merge rule on a line, restated here: every value alone and
    each run of empty values one group; while a group's count, or its count
    less its sure cells, is one to line - 1 (or below nought), the shortest
    joins its smaller non-zero neighbour (the earlier on a tie). One group
    over every value, or a short group with no neighbour, publishes
    nothing."""
    size = len(bins)
    groups: "list[list[int]]" = []
    value = 0
    while value < size:
        if bins[value]:
            groups += [[value, value, bins[value], sure[value]]]
            value += 1
            continue
        end = value
        held = sure[value]
        while end + 1 < size and bins[end + 1] == 0:
            end += 1
            held += sure[end]
        groups += [[value, end, 0, held]]
        value = end + 1

    def short(group: "list[int]") -> bool:
        left = group[2] - group[3]
        return (0 < group[2] < line) or left < 0 or (0 < left < line)

    while True:
        shorts = [index for index in range(len(groups)) if short(groups[index])]
        if not shorts:
            break
        pick = min(shorts, key=lambda index: (groups[index][2], index))
        before = next((index for index in range(pick - 1, -1, -1) if groups[index][2]), None)
        after = next((index for index in range(pick + 1, len(groups)) if groups[index][2]), None)
        if before is None and after is None:
            return []
        if after is None or (before is not None and groups[before][2] <= groups[after][2]):
            start, stop = before, pick
        else:
            start, stop = pick, after
        joined = [groups[start][0], groups[stop][1], sum(g[2] for g in groups[start:stop + 1]), sum(g[3] for g in groups[start:stop + 1])]
        groups = groups[:start] + [joined] + groups[stop + 1:]
    if len(groups) == 1:
        return []
    return [(first, last, count) for first, last, count, _sure in groups]


def _published(block: dict, field: str) -> "tuple[list[tuple[int, int, int]], list[tuple[int, int]]]":
    census_key, heaps_key = calendar_clock.FIELD_KEYS[field]
    return (
        [(group["first"], group["last"], group["count"]) for group in block[census_key]],
        [(heap["value"], heap["count"]) for heap in block[heaps_key]],
    )


def _body_texts(block: dict, cells: "list[str]", form: str) -> "list[datetime.datetime]":
    moments = sorted(moment for moment in (_moment(cell, form) for cell in cells) if moment is not None)
    low, high = block["low_tail"]["rows"], block["high_tail"]["rows"]
    return moments[low: len(moments) - high]


def _sure(block: dict, cells: "list[str]", form: str, field: str) -> "list[int]":
    """The sure cells, recomputed from the cells: each boundary and rung,
    with every rank between two of one value, at its value, and rule 4's
    cells at midnight at value 0."""
    moments = sorted(moment for moment in (_moment(cell, form) for cell in cells) if moment is not None)
    parsed = len(moments)
    low, high = block["low_tail"]["rows"], block["high_tail"]["rows"]
    published = [(low, moments[low]), (parsed - 1 - high, moments[parsed - 1 - high])]
    for percent, key in ((1, "p01"), (5, "p05"), (10, "p10"), (25, "p25"), (50, "p50"), (75, "p75"), (90, "p90"), (95, "p95"), (99, "p99")):
        if block["date_percentiles"][key] is not None:
            rank = min(parsed - 1, ((parsed - 1) * percent) // 100)
            published += [(rank, moments[rank])]
    known = dict(published)
    ordered = sorted(published)
    for (first, here), (last, there) in zip(ordered, ordered[1:]):
        if here == there:
            for rank in range(first, last + 1):
                known[rank] = here
    sure = [0] * 60
    zero = 0
    for moment in known.values():
        if moment.time() == datetime.time(0, 0):
            zero += 1
        else:
            sure[moment.minute if field == "minute" else moment.second] += 1
    counted = block["n_at_midnight"]
    if counted is not None:
        for side in ("low_tail", "high_tail"):
            values = block[side]["values"]
            if values and all(value.endswith("00:00:00") for value in values):
                counted -= block[side]["rows"]
        zero = max(zero, max(counted, 0))
    sure[0] += zero
    return sure


def _expected(block: dict, cells: "list[str]", form: str, field: str) -> "tuple[list[tuple[int, int, int]], list[tuple[int, int]]]":
    """The heaps and census the cells give, recomputed here: a value standing
    out at the line and three times the median of the five each side on the
    cycle, written at the line's different values, its sure cells held;
    then the merge over the rest, left out where its groups stand on a few
    different values."""
    body = _body_texts(block, cells, form)
    values = [moment.minute if field == "minute" else moment.second for moment in body]
    bins = [0] * 60
    different: "list[set[datetime.datetime]]" = [set() for _value in range(60)]
    for moment, value in zip(body, values):
        bins[value] += 1
        different[value].add(moment)
    sure = _sure(block, cells, form, field)
    heaps: "list[tuple[int, int]]" = []
    for value in range(60):
        around = sorted(bins[(value + step) % 60] for step in (-5, -4, -3, -2, -1, 1, 2, 3, 4, 5))
        median2 = around[4] + around[5]
        left = bins[value] - sure[value]
        if (
            bins[value] >= LINE and 2 * bins[value] >= 3 * median2 and len(different[value]) >= LINE
            and left >= 0 and (left == 0 or left >= LINE)
        ):
            heaps += [(value, bins[value])]
    on_heaps = {value for value, _count in heaps}
    rest = [0 if value in on_heaps else bins[value] for value in range(60)]
    rest_sure = [0 if value in on_heaps else sure[value] for value in range(60)]
    groups = _restated_merge(rest, rest_sure, LINE)
    held = [sum(len(different[v]) for v in range(first, last + 1) if v not in on_heaps) for first, last, count in groups if count > 0]
    if held and (min(held) < 3 or sum(held) < 8 * len(held)):
        groups = []
    return groups, heaps


def test_the_clock_battery_publishes_its_census(thousand) -> None:
    """The heaped columns publish, the rest withheld as they should be, each the merge recomputed here.

    Every heaped column publishes its minute heaps or census, and the
    columns written `HH:MM:00` their second heaps; each field's lists
    equal `_expected`, recomputed from the cells; the loader's own checks
    find nothing at the census line and at a floor of one; the flat
    control publishes nothing and says nothing of its minutes; the
    three-hour session is withheld with MC4's sentence and night charting
    on the hour with M3's. The real table meets its own description.
    """
    described, columns, text = thousand
    assert kpi_shapes.missed(kpi_shapes.measure(described, text, "real.csv")) == []
    notes = described.document["publication_notes"]
    for name, (cells, form) in columns.items():
        block = described.block(name)
        said = [note["note"] for note in notes if note["column"] == name and "of the hour this column" in note["note"]]
        census, heaps = _published(block, "minute")
        if name in shapes.FLAT:
            assert census == [] and heaps == [] and said == [], name
            continue
        if name in shapes.SHORT_SPAN:
            assert census == [] and heaps == [] and len(said) == 1 and "fewer than four hours" in said[0], name
            continue
        if name in shapes.WITH_THE_HOUR:
            assert census == [] and heaps == [] and len(said) == 1 and "changes with the hour" in said[0], name
            continue
        assert census or heaps, name
        assert (census, heaps) == _expected(block, cells, form, "minute"), name
        body = block["n_present"] - block["n_unparsed"] - block["low_tail"]["rows"] - block["high_tail"]["rows"]
        held = sum(count for _value, count in heaps)
        sure = [0] * 60
        for line in (LINE, 2):
            if census:
                assert calendar_clock.field_breach(tuple(census), body - held, line, sure, "minute") is None, name
            assert calendar_clock.heaps_breach(tuple(heaps), body, LINE, sure, "minute", bool(census)) is None, name
        seconds = _published(block, "second")
        if name in shapes.SECONDS_PUBLISHED:
            assert seconds[1] and seconds[1][0][0] == 0, name
            assert seconds == _expected(block, cells, form, "second"), name
        else:
            assert seconds == ([], []), name


def test_red_when_the_span_rule_is_withdrawn(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MC4's mutant: with no span rule a three-hour session publishes its minutes."""
    monkeypatch.setattr(calendar_clock, "span_long_enough_for", lambda _low, _high, _field: True)
    block = _described_alone(tmp_path, shapes.three_hours(random.Random(5), 1000), LINE, loads=False)
    assert block["minute_heaps"] or block["minute_census"]


def test_red_when_the_hour_rule_is_withdrawn(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """M3's mutant: with no hour rule night charting beside day entries publishes its minutes."""
    monkeypatch.setattr(calendar_clock, "depends_on_the_hour", lambda *_arguments: False)
    block = _described_alone(tmp_path, shapes.night_and_day(random.Random(5), 1000), LINE, loads=False)
    assert block["minute_heaps"] or block["minute_census"]


def _described_alone(folder: pathlib.Path, cells: "list[str]", floor: int, loads: bool = True) -> dict:
    """One column described the way `synthtwin profile` describes it; its block."""
    folder.mkdir(parents=True, exist_ok=True)
    table = fixtures.write(folder, "real.csv", "seen_at\n" + "\n".join(cells) + "\n")
    settings = taxonomy.Settings(small_cell_floor=floor)
    document = profile.build_document(reading.read_table(str(table), small_cell_floor=floor), settings, [], [], [])
    if loads:
        contract.load_profile(str(fixtures.write_profile(folder, "real-profile.json", document)))
    return next(block for block in document["columns"] if block["name"] == "seen_at")


# -- the twins -------------------------------------------------------------------


def _statistics_failures(block: dict, real: "list[str]", twin: "list[str]", form: str, field: str) -> "list[str]":
    """BOUND, CAP and SHAPE on one field's TVD, for one twin.

    BOUND: the twin's TVD within (the rows of a tail listing no values +
    the UNRESOLVED cells, those of census groups of several values and,
    beside heaps with no census, the rest) / parsed. CAP, at a floor of
    eleven and 1,000 rows or more, where nothing is unresolved: that bound
    at most 0.10 below 10,000 rows and 0.02 from them. SHAPE: the twin's
    gap at most a quarter of the real column's distance from flat wherever
    that distance is three sampling scales.
    """
    parsed = block["n_present"] - block["n_unparsed"]
    tails = sum(block[side]["rows"] for side in ("low_tail", "high_tail") if block[side]["values"] is None)
    census, heaps = _published(block, field)
    body = parsed - block["low_tail"]["rows"] - block["high_tail"]["rows"]
    unresolved = sum(count for first, last, count in census if last > first)
    if not census:
        unresolved = body - sum(count for _value, count in heaps)
    real_counts, twin_counts = _field_counts(real, form, field), _field_counts(twin, form, field)
    gap = _tvd(real_counts, twin_counts)
    bound = (tails + unresolved) / parsed
    found: "list[str]" = []
    if gap > bound + 1e-12:
        found += [f"BOUND {gap:.4f} > {bound:.4f}"]
    if parsed >= 1000 and unresolved == 0:
        cap = 0.02 if parsed >= 10000 else 0.10
        if bound > cap:
            found += [f"CAP {bound:.4f} > {cap}"]
    total = sum(real_counts)
    share = [count / total for count in real_counts]
    flat = 0.5 * sum(abs(value - 1 / 60) for value in share)
    scale = 0.5 * sum((value * (1 - value) / total) ** 0.5 for value in share)
    if flat > 3 * scale and gap > max(0.25 * flat, bound):
        found += [f"SHAPE {gap:.4f} > a quarter of {flat:.4f}"]
    return found


def _independence_failures(block: dict, real: "list[str]", twin: "list[str]", form: str) -> "list[str]":
    """INDEPENDENCE (the design skeptic's B1): in each hour group holding
    four lines of the body's cells off a written midnight, the twin's share
    of them on each single-minute group lies within BOUND -- (the rows of a
    tail listing no values + the unresolved cells) / parsed -- and three
    sampling scales of the census share, so the units the pass moves do not
    bend the heap by hour.

    TWO READINGS THE REAL TABLE ITSELF FAILED, measured on the battery at
    10,000 rows and floor 11 (the 10k run of K-S3-42's driver): cells at a
    written midnight -- bare days, a third of the admissions -- stand in
    hour 0 on minute 0 whatever the pass does, so they are left out of the
    hour groups and of the census share (admissions' real cells failed the
    clause 115 times); and a group the hour group expects fewer than the
    census line's cells of, or fewer than the line's cells off, is not
    asked, a few events no sampling scale states (vitals', the cells written
    `HH:MM:00` and their near-pure sibling's real cells failed it 5, 11 and
    13 times, the discharges' and the epoch placeholder's 3 each; and the
    twin of a column on the hour but for three cells failed it once in the
    KPI's ten twins at 10,000 rows, 0.991 against 1.000 in hours 0 and 1,
    where three sampling scales come to about one cell). The real table's cells now fail it
    nowhere (`test_the_real_table_meets_the_independence_clause`).

    AND A THIRD (the lane's skeptic, item 8): where the column's seconds are
    pinned to 0 -- written to the minute, or its second's facts pinning
    second 0 -- a cell of hour 0 on minute 0 is a written midnight, so the
    cells off midnight of an hour group holding hour 0 stand on minute 0 only
    in its other hours; minute 0's share is then asked of the cells free to
    take it -- off midnight and off hour 0 -- and an hour group expects it
    of its own cells off hour 0 alone (cells written `HH:MM:00` at 10,000
    rows and a floor of 36 failed the clause at every seed, hour 0 a group
    of its own and expected 0.366 on minute 0, and were right to come back
    with none). A column written in bursts -- more than one and a half cells
    to each different value -- is not asked (below)."""
    census, heaps = _published(block, "minute")
    singles = [(value, count) for value, count in heaps] + [(first, count) for first, last, count in census if first == last and count > 0]
    if not singles or not block["hour_census"]:
        return []
    parsed = block["n_present"] - block["n_unparsed"]
    body = parsed - block["low_tail"]["rows"] - block["high_tail"]["rows"]
    unresolved = sum(count for first, last, count in census if last > first)
    if not census:
        unresolved = body - sum(count for _value, count in heaps)
    bound = (sum(block[side]["rows"] for side in ("low_tail", "high_tail") if block[side]["values"] is None) + unresolved) / parsed
    found: "list[str]" = []
    moments = _body_texts(block, twin, form)
    # Asked where a value is mostly one cell: a share over cells written in
    # bursts swings with each burst -- the real burst column's own share of
    # minute 30 runs from 0.09 to 0.41 hour by hour against 0.23 in all --
    # and no sampling scale of cells states it.
    if len(moments) > 1.5 * len(set(moments)):
        return []
    off = [moment for moment in moments if (moment.hour, moment.minute, moment.second, moment.microsecond) != (0, 0, 0, 0)]
    at_midnight = len(moments) - len(off)
    second_census, second_heaps = _published(block, "second")
    pinned = block["time_precision"] == "minute" or calendar_clock.field_lattice(
        tuple(second_census), tuple(second_heaps), [], body, LINE
    ) == calendar_clock.FIELD_VALUES
    hour_zero = len([moment for moment in off if moment.hour == 0]) if pinned else 0
    for group in block["hour_census"]:
        inside = [moment for moment in off if group["first"] <= moment.hour <= group["last"]]
        if len(inside) < 4 * LINE:
            continue
        for value, count in singles:
            expected = (count - (at_midnight if value == 0 else 0)) / (body - at_midnight)
            if value == 0 and hour_zero:
                free = len([moment for moment in inside if moment.hour != 0])
                expected = (count - at_midnight) / (body - at_midnight - hour_zero) * free / len(inside)
            if expected * len(inside) < LINE or (1 - expected) * len(inside) < LINE:
                continue
            share = sum(1 for moment in inside if moment.minute == value) / len(inside)
            scale = (expected * (1 - expected) / len(inside)) ** 0.5
            if abs(share - expected) > bound + 3 * scale:
                found += [f"hours {group['first']}-{group['last']} minute {value}: {share:.3f} against {expected:.3f}"]
    return found


def test_the_real_table_meets_the_independence_clause(thousand) -> None:
    """A clause the real cells fail cannot judge a twin: on the battery's own
    columns, every one publishing a field, INDEPENDENCE finds nothing."""
    described, columns, _text = thousand
    asked = 0
    for name, (cells, form) in columns.items():
        block = described.block(name)
        if any(_published(block, "minute")):
            asked = asked + 1
            assert _independence_failures(block, cells, cells, form) == [], name
    assert asked >= 10, asked


def test_each_hour_takes_its_share_of_the_heaps(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """KIN SHARES (method G7.3h): 4,000 clinic slots, every hour of the day
    35 per cent on :00 in the real column, meet INDEPENDENCE; with each gap's
    shares left whole -- G7.3f's moves, nearest first and whole runs first
    -- hour 8 came back 23 per cent on :00 and 25 on :45 against 12."""
    cells = shapes.clinic(random.Random(72003), 4000)
    described = kpi_shapes.describe(tmp_path / "kin", "clinic", "clinic\n" + "\n".join(cells) + "\n", LINE)
    block = described.block("clinic")
    assert block["minute_heaps"] and block["hour_census"]
    twin = shapes.cells_of(kpi_shapes.twin_text(described, 0), "clinic")
    assert _independence_failures(block, cells, twin, shapes.ISO_M) == []
    monkeypatch.setattr(generation, "_clock_kin_shares_moved", lambda *_arguments: False)
    bent = shapes.cells_of(kpi_shapes.twin_text(described, 0), "clinic")
    assert len(_independence_failures(block, cells, bent, shapes.ISO_M)) >= 2


@pytest.mark.parametrize("seed", [0, 4])
def test_the_clock_battery_twins_meet_their_census(thousand, seed: int, monkeypatch: pytest.MonkeyPatch) -> None:
    """Nothing missed, V5-M1 and V5-S1 held, BOUND, CAP, SHAPE and INDEPENDENCE; hours and weekdays kept.

    Every twin validates with nothing MISSED and every published field
    HELD; its minute and second statistics lie inside BOUND, CAP and SHAPE
    (`_statistics_failures`) and INDEPENDENCE (`_independence_failures`);
    and its body's hour groups and its weekday groups are the ones the
    same seed writes with G7.3h withdrawn -- its moves keep every hour
    group and day standing.
    """
    described, columns, text = thousand
    written = kpi_shapes.twin_text(described, seed)
    outcome = kpi_shapes.measure(described, written, f"twin-{seed}.csv")
    assert kpi_shapes.missed(outcome) == [], seed
    for field in ("minute", "second"):
        facts = [f"datetime.{key}" for key in calendar_clock.FIELD_KEYS[field]]
        held = [check for check in outcome.checks if check.fact in facts]
        # One check per published census and one per field's published heaps.
        published = [
            listed for name in columns for listed in _published(described.block(name), field) if listed
        ]
        assert len(held) == len(published) and all(check.verdict == validation.HELD for check in held), field
    monkeypatch.setattr(generation, "_clock_fields_settled", lambda column, facts, ordinals, *rest, **named: (ordinals, []))
    flat = kpi_shapes.twin_text(described, seed)
    monkeypatch.undo()
    for name, (cells, form) in columns.items():
        block = described.block(name)
        twin = shapes.cells_of(written, name)
        for field in ("minute", "second"):
            if any(_published(block, field)):
                assert _statistics_failures(block, cells, twin, form, field) == [], (name, field, seed)
        assert _independence_failures(block, cells, twin, form) == [], (name, seed)
        without = shapes.cells_of(flat, name)
        if any(_published(block, "minute")) or any(_published(block, "second")):
            if block["hour_census"]:
                # The BODY's hours, which the hour census counts: G7.3h's
                # tails may step a cell off midnight into another hour.
                hours = [moment.hour for moment in _body_texts(block, twin, form)]
                hours_without = [moment.hour for moment in _body_texts(block, without, form)]
                assert [
                    sum(1 for hour in hours if group["first"] <= hour <= group["last"])
                    for group in block["hour_census"]
                ] == [
                    sum(1 for hour in hours_without if group["first"] <= hour <= group["last"])
                    for group in block["hour_census"]
                ], (name, seed)
            if block["weekday_census"]:
                days = [_moment(cell, form).weekday() for cell in twin if _moment(cell, form)]
                days_without = [_moment(cell, form).weekday() for cell in without if _moment(cell, form)]
                assert [
                    sum(1 for day in days if group["first"] <= day <= group["last"])
                    for group in block["weekday_census"]
                ] == [
                    sum(1 for day in days_without if group["first"] <= day <= group["last"])
                    for group in block["weekday_census"]
                ], (name, seed)
        else:
            assert twin == without, (name, seed)


def test_a_flat_twin_misses_the_minute_census(thousand, monkeypatch: pytest.MonkeyPatch) -> None:
    """G7.3h and the drawing rule withdrawn, every published field is MISSED, and no count below the line is printed."""
    described, columns, _text = thousand
    monkeypatch.setattr(generation, "_clock_fields_settled", lambda column, facts, ordinals, *rest, **named: (ordinals, []))
    monkeypatch.setattr(generation, "_draw_unit", lambda *_facts: 1)
    monkeypatch.setattr(generation, "_tail_unit", lambda *_facts: 1)
    written = kpi_shapes.twin_text(described, 0)
    outcome = kpi_shapes.measure(described, written, "flat.csv")
    checks = [check for check in outcome.checks if check.fact in ("datetime.minute_census", "datetime.second_census", "datetime.minute_heaps", "datetime.second_heaps")]
    assert checks and all(check.verdict == validation.MISSED for check in checks)
    for check in checks:
        for shown in check.achieved.split(", "):
            last = shown.split(" ")[-1]
            if last.isdigit():
                assert int(last) == 0 or int(last) >= LINE, check.achieved


def test_validating_never_produces_a_clock_census(thousand, monkeypatch: pytest.MonkeyPatch) -> None:
    """The validator recounts the file's fields and never asks the producer for a census."""
    described, _columns, text = thousand

    def refused(*_args: object, **_named: object) -> object:
        raise AssertionError("the validator asked the producer for a census of the clock")

    monkeypatch.setattr(taxonomy, "clock_field_decision", refused)
    outcome = kpi_shapes.measure(described, text, "again.csv")
    assert kpi_shapes.missed(outcome) == []
    assert any(check.fact == "datetime.minute_census" for check in outcome.checks)


# -- the witnesses ---------------------------------------------------------------------


def _one_column(folder: pathlib.Path, name: str, cells: "list[str]", floor: int = LINE) -> kpi_shapes.Described:
    return kpi_shapes.describe(folder, name, f"{name}\n" + "\n".join(cells) + "\n", floor)


def _unit_of(described: kpi_shapes.Described, name: str, floor: int = LINE) -> int:
    """The body's drawing unit of a described column, read as the layout reads it."""
    block = described.block(name)
    body = block["n_present"] - block["n_unparsed"] - block["low_tail"]["rows"] - block["high_tail"]["rows"]
    return generation._draw_unit(described.loaded.columns[0].facts, body, floor)


def test_tied_bursts_keep_their_count(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Bursts of one to six check-ins on one minute publish their heaps and leave
    out the census of the rest, whose groups stand on a few different values
    each, and keep their count of different values at seeds 0 to 2; with the
    few-values rule withdrawn the census of the rest is published, and its
    twins come back long or missing a count at some seed (SUBSTITUTE's own
    red case is the frozen state `field_substitute`)."""
    cells = shapes.bursts(random.Random(72011), 1000)
    described = _one_column(tmp_path / "kept", "bursts", cells)
    block = described.block("bursts")
    assert block["minute_heaps"] and block["minute_census"] == []
    for seed in (0, 1, 2):
        written = kpi_shapes.twin_text(described, seed)
        assert kpi_shapes.missed(kpi_shapes.measure(described, written, f"t{seed}.csv")) == [], seed
    monkeypatch.setattr(calendar_clock, "few_values", lambda _groups, _units, _heaps: False)
    fine = _one_column(tmp_path / "fine", "bursts", cells)
    assert fine.block("bursts")["minute_census"]


def test_the_count_is_put_back_by_spread(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Clinic slots on the quarter hour at 8,000 rows keep their count of different
    values; with SPREAD withdrawn the count comes back short (measured: met at
    3,000 and 5,000 rows without it, short at 8,000 at seeds 0 and 1) -- SPREAD
    and, beside the weekday census the clinic publishes, the two steps after it
    (lane J2)."""
    described = _one_column(tmp_path, "clinic", shapes.clinic(random.Random(72012), 8000))
    written = kpi_shapes.twin_text(described, 0)
    assert kpi_shapes.missed(kpi_shapes.measure(described, written, "t.csv")) == []
    monkeypatch.setattr(generation, "_clock_short_spread", lambda *_args, **_named: None)
    monkeypatch.setattr(generation, "_clock_paid_spread", lambda *_args, **_named: None)
    monkeypatch.setattr(generation, "_clock_spread_substituted", lambda *_args, **_named: None)
    written = kpi_shapes.twin_text(described, 0)
    assert "clinic:distinct.n_distinct" in kpi_shapes.missed(kpi_shapes.measure(described, written, "m.csv"))


def test_cells_written_on_the_minute_keep_their_seconds(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Cells written `HH:MM:00` at 2,000 rows come back with every second on 0 and
    their second census met (the drawing rule); with the drawing unit
    withdrawn the second census, or the count, is missed."""
    described = _one_column(tmp_path, "rounds", shapes.zero_seconds(random.Random(72013), 2000))
    assert _unit_of(described, "rounds") == 60
    written = kpi_shapes.twin_text(described, 0)
    assert kpi_shapes.missed(kpi_shapes.measure(described, written, "t.csv")) == []
    # Every cell but the two ends, each tail's outermost rank standing where
    # its published distances put it, to the second.
    twin = sorted(cell for cell in shapes.cells_of(written, "rounds") if cell)
    assert all(cell.endswith(":00") for cell in twin[1:-1])
    monkeypatch.setattr(generation, "_draw_unit", lambda *_facts: 1)
    monkeypatch.setattr(generation, "_tail_unit", lambda *_facts: 1)
    written = kpi_shapes.twin_text(described, 0)
    twin = sorted(cell for cell in shapes.cells_of(written, "rounds") if cell)
    assert not all(cell.endswith(":00") for cell in twin[1:-1])


def test_a_step_off_midnight_keeps_the_drawing_unit(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Cells written `HH:MM:00` at 10,000 rows -- the gate's table -- miss nothing,
    and with G7.3h withheld every body cell already stands on second 0: both
    steps at midnight step a body rank off one by the drawing unit, a minute,
    and a tail rank by its tail's (`_midnight_step_of`, the design skeptic's
    m2). Stepped by the written second, seven body cells stood at second 1
    for G7.3h's own passes to take back (the lane's skeptic, item 5: since
    the repair round those passes take them back, and the twin's counts are
    met either way)."""
    cells, _form = shapes.thousand(10000)["zero_seconds"]
    described = _one_column(tmp_path, "rounds", cells)
    assert kpi_shapes.missed(kpi_shapes.measure(described, kpi_shapes.twin_text(described, 0), "t.csv")) == []
    block = described.block("rounds")
    low, high = block["low_tail"]["rows"], block["high_tail"]["rows"]

    def off_the_lattice() -> int:
        written = sorted(shapes.cells_of(kpi_shapes.twin_text(described, 0), "rounds"))
        return sum(1 for cell in written[low: len(written) - high] if not cell.endswith(":00"))

    monkeypatch.setattr(generation, "_clock_fields_settled", lambda _column, _facts, ordinals, *_rest, **_named: (list(ordinals), []))
    assert off_the_lattice() == 0
    monkeypatch.setattr(generation, "_midnight_step_of", lambda _layout, _rank, step: step)
    assert off_the_lattice() > 0


def test_a_pure_grid_is_drawn_on_its_lattice(tmp_path: pathlib.Path) -> None:
    """A half-hour grid is drawn on thirty minutes and every twin cell stands on :00 or :30."""
    described = _one_column(tmp_path, "grid", shapes.grid(random.Random(72014), 1000, 30))
    assert _unit_of(described, "grid") == 1800
    written = kpi_shapes.twin_text(described, 0)
    assert kpi_shapes.missed(kpi_shapes.measure(described, written, "t.csv")) == []
    # The body's cells: the tails of a column written to the minute draw
    # at any minute (a stated limit, method G7.3's drawing rule).
    block = described.block("grid")
    twin = sorted(cell for cell in shapes.cells_of(written, "grid") if cell)
    body = twin[block["low_tail"]["rows"]: len(twin) - block["high_tail"]["rows"]]
    assert all(cell[-2:] in ("00", "30") for cell in body)


def test_a_flat_column_publishes_nothing_and_its_twin_is_unchanged(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A column at any minute and second publishes no census of the clock, and its
    twin is the one the same seed writes with every step of this landing withdrawn."""
    described = _one_column(tmp_path, "arrivals", shapes.emergency(random.Random(72015), 1000))
    block = described.block("arrivals")
    assert all(block[key] == [] for key in ("minute_census", "minute_heaps", "second_census", "second_heaps"))
    written = kpi_shapes.twin_text(described, 0)
    monkeypatch.setattr(generation, "_clock_fields_settled", lambda column, facts, ordinals, *rest, **named: (ordinals, []))
    assert kpi_shapes.twin_text(described, 0) == written


def test_days_beside_a_few_timed_cells_withhold_their_minutes(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """989 days at midnight beside 11 cells at 09:30 -- and 970 beside 30 -- withhold
    the minute's heaps and say why (NF118), and their twins at seeds 0 and 1
    miss nothing; with the rule withdrawn the heap on minute 30 is published
    and missed, the twins' tails standing some of their cells off a midnight
    and their bodies left fewer than the heap counts (the builder's
    measurement of 2026-10-12: 6 of 11)."""
    for timed, seed in ((11, 72030), (30, 72046)):
        cells = shapes.days_and_a_few_times(random.Random(seed), 1000, timed)
        described = _one_column(tmp_path / f"kept-{timed}", "days", cells)
        block = described.block("days")
        assert block["minute_heaps"] == [] and block["minute_census"] == [], timed
        said = [note["note"] for note in described.document["publication_notes"] if note["column"] == "days"]
        assert taxonomy.rendered(taxonomy.NOTE_MINUTE_WITHHELD_OFF_MIDNIGHT, ()) in said, timed
        for drawn in (0, 1):
            written = kpi_shapes.twin_text(described, drawn)
            assert kpi_shapes.missed(kpi_shapes.measure(described, written, f"t{drawn}.csv")) == [], (timed, drawn)
    monkeypatch.setattr(calendar_clock, "off_midnight_short", lambda *_arguments: False)
    cells = shapes.days_and_a_few_times(random.Random(72030), 1000, 11)
    described = _one_column(tmp_path / "withdrawn", "days", cells)
    assert described.block("days")["minute_heaps"] == [{"value": 30, "count": 11}]
    written = kpi_shapes.twin_text(described, 0)
    assert "days:minute_heaps.counts" in kpi_shapes.missed(kpi_shapes.measure(described, written, "m.csv"))


def _regular_series(step: int, rows: int, every: int = 0) -> "list[str]":
    """Lane J2's skeptic, item 1: one stamp every `step` minutes from 2015-01-01, as vital signs
    or scheduled observations are written; every `every`-th written twice where it is given."""
    start = datetime.datetime(2015, 1, 1)
    cells: "list[str]" = []
    place = 0
    while len(cells) < rows:
        text = (start + datetime.timedelta(minutes=step * place)).strftime("%Y-%m-%d %H:%M:%S")
        cells += [text] * (2 if every and place % every == every - 1 else 1)
        place = place + 1
    return cells[:rows]


def test_a_regular_series_withholds_the_clock_facts_it_crowds(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Lane J2's skeptic, item 1 (NF121, NF122): stamps one, five, fifteen and sixty minutes
    apart, every one different, at 1,000 and 3,800 rows, and five minutes apart at 3,800 rows
    with every tenth written twice, crowd the lattice their minute's and second's facts would
    pin: those facts are withheld, said once a field, and the twins miss nothing -- as on the
    pushed head 45191fa, where no minute fact was published. Mutant: the rule withdrawn, the
    five-minute series at 1,000 rows publishes its heaps, its twin comes back 903 values of
    1,000, and the report names the clock pass's short count as the cause."""
    shapes_asked = [(step, rows, LINE, 0) for step in (1, 5, 15, 60) for rows in (1000, 3800)]
    shapes_asked += [(5, 3800, 36, 0), (5, 3800, LINE, 10)]
    for step, rows, floor, every in shapes_asked:
        described = _one_column(tmp_path / f"s{step}-{rows}-{floor}-{every}", "c", _regular_series(step, rows, every), floor)
        block = described.block("c")
        for key in ("minute_census", "minute_heaps", "second_census", "second_heaps"):
            assert block[key] == [], (step, rows, floor, every, key)
        said = [note["note"] for note in described.document["publication_notes"] if note["column"] == "c"]
        assert taxonomy.rendered(taxonomy.NOTE_SECOND_WITHHELD_CROWDED, ()) in said, (step, rows, floor, every)
        written = kpi_shapes.twin_text(described, 0)
        assert kpi_shapes.missed(kpi_shapes.measure(described, written, "t.csv")) == [], (step, rows, floor, every)
    assert calendar_clock.lattice_crowded(300, 0, 299_700, 500)
    assert not calendar_clock.lattice_crowded(300, 0, 299_700, 499)
    assert calendar_clock.lattice_crowded(300, 0, 299_700, 334, True)
    assert not calendar_clock.lattice_crowded(300, 0, 299_700, 333, True)
    assert not calendar_clock.lattice_crowded(1, 0, 299_700, 1000, True)
    monkeypatch.setattr(calendar_clock, "lattice_crowded", lambda *_arguments: False)
    described = _one_column(tmp_path / "withdrawn", "c", _regular_series(5, 1000))
    assert described.block("c")["second_heaps"] == [{"value": 0, "count": 978}]
    twin = generation.generate(described.loaded, 0)
    written = rendering.twin_csv(twin)
    assert "c:distinct.n_distinct" in kpi_shapes.missed(kpi_shapes.measure(described, written, "m.csv"))
    causes = [note.note for note in twin.deviations if note.fact == "n_distinct"]
    assert generation._CLOCK_FIELDS_LEFT_SHORT in causes, causes


def _dense_grid(kind: str, rows: int, days: int) -> "list[str]":
    """Lane J2's second skeptic, item 1: `rows` moments drawn at random over `days` days from
    2015-01-01 -- on the hour (`hour`), on 30-, 15- and 5-minute slots (`half`, `q15`, `min5`),
    or at any minute with seconds `:00` (`min0`, an EHR datetime written to the minute) -- in
    rank order, repeats kept."""
    pick = random.Random(11)
    minutes = {"hour": 60, "half": 30, "q15": 15, "min5": 5, "min0": 1}[kind]
    start = datetime.datetime(2015, 1, 1)
    cells: "list[str]" = []
    for _row in range(rows):
        moment = start + datetime.timedelta(minutes=minutes * pick.randrange(days * 1440 // minutes))
        cells += [moment.strftime("%Y-%m-%d %H:%M:%S")]
    return sorted(cells)


# The seven dense grids of lane J2's second skeptic, item 1, as (kind, rows, days).
_DENSE_GRIDS = (
    ("hour", 3000, 60), ("min0", 10000, 7), ("q15", 10000, 30), ("min5", 10000, 14),
    ("half", 10000, 60), ("min0", 7500, 7), ("min0", 6000, 5),
)


def _twice_series(step: int, rows: int) -> "list[str]":
    """Codex's review of lane J2, item 2: `rows // 2` stamps `step` minutes apart from
    2015-01-01 00:00:00, each written twice."""
    start = datetime.datetime(2015, 1, 1)
    cells: "list[str]" = []
    for place in range(rows // 2):
        cells += [(start + datetime.timedelta(minutes=step * place)).strftime("%Y-%m-%d %H:%M:%S")] * 2
    return cells


def test_a_short_grid_written_twice_keeps_its_clock_facts(tmp_path: pathlib.Path) -> None:
    """Codex's review of lane J2, item 2 (NF121, NF122): 2,000 rows, 1,000 stamps from
    2015-01-01 00:00:00 five minutes apart -- and a minute apart -- each written twice, fill
    their lattice 0.144 above a uniform draw of their rows; e69e534 withheld their minute's and
    second's facts as crowded, and its seed-0 twin wrote 49 cells at second 0. Where some value
    repeats and no count at midnight is published, the rule asks a fifth: both publish, the
    second's heap at 0 holding every body cell, and their twins at seeds 0 to 2, floors 11 and
    36, miss nothing. The protection stands where a count at midnight is published: 10,000 rows
    five minutes apart, each written twice -- whose twins with the facts came back 34 to 90
    values short -- stay withheld and meet their count."""
    for step in (5, 1):
        cells = _twice_series(step, 2000)
        for floor in (11, 36):
            described = _one_column(tmp_path / f"twice-{step}-{floor}", "c", cells, floor)
            block = described.block("c")
            assert block.get("n_at_midnight") is None, (step, floor)
            heaps = block["second_heaps"]
            body = 2000 - block["low_tail"]["rows"] - block["high_tail"]["rows"]
            assert heaps == [{"value": 0, "count": body}], (step, floor, heaps)
            for seed in (0, 1, 2):
                written = kpi_shapes.twin_text(described, seed)
                assert kpi_shapes.missed(kpi_shapes.measure(described, written, f"t{seed}.csv")) == [], (step, floor, seed)
    described = _one_column(tmp_path / "twice-5-10000", "c", _twice_series(5, 10000))
    block = described.block("c")
    assert block.get("n_at_midnight") is not None
    assert block["second_heaps"] == [] and block["minute_heaps"] == []
    written = kpi_shapes.twin_text(described, 0)
    assert kpi_shapes.missed(kpi_shapes.measure(described, written, "t.csv")) == []
    # By hand: 1,000 values on 1,000 points of 300 seconds, 2,000 rows, 0.135 above the draw.
    assert not calendar_clock.lattice_crowded(300, 0, 299_700, 1000, False, 2000, False)
    assert calendar_clock.lattice_crowded(300, 0, 299_700, 1000, False, 2000, True)
    assert calendar_clock.lattice_crowded(300, 0, 299_700, 1000, True, 1000, False)


def _half_kept_series(step: int, rows: int, times: int) -> "list[str]":
    """Stamps `step` minutes apart from 2015-01-01, each slot kept with chance one half
    (`random.Random(5)`), each kept slot written `times` times."""
    pick = random.Random(5)
    start = datetime.datetime(2015, 1, 1)
    cells: "list[str]" = []
    place = 0
    while len(cells) < rows:
        text = (start + datetime.timedelta(minutes=step * place)).strftime("%Y-%m-%d %H:%M:%S")
        place = place + 1
        if pick.random() < 0.5:
            continue
        cells += [text] * times
    return cells[:rows]


def test_a_half_kept_quarter_hour_series_meets_its_count_at_midnight(tmp_path: pathlib.Path) -> None:
    """Codex's review of lane J2, the leftover regression: 4,000 stamps every fifteen
    minutes, half the slots kept, each written 3, 4 or 6 times, publish their minute's and
    second's heaps on a fifteen-minute lattice. On e69e534 5 of these 12 twins missed
    `midnight.count` and `second_heaps.counts` (45191fa, publishing no clock facts, met all
    12): a pair the hour pass moved onto midnight took `00:00:01` (G7.3g step 4, a written
    unit at a time), where no field pass could put it on second 0 but at midnight, and the
    count there came back a cell long. Step 4 now asks the body's lattice first
    (`_clock_nearest_on`): every twin misses nothing, 30 of 30 at seeds 0 to 4; with that
    withdrawn, 2 of these 12 miss `second_heaps.counts`."""
    for times in (3, 4, 6):
        cells = _half_kept_series(15, 4000, times)
        for floor in (11, 36):
            described = _one_column(tmp_path / f"x{times}-{floor}", "c", cells, floor)
            block = described.block("c")
            assert block["minute_heaps"] and block["second_heaps"], (times, floor)
            assert block.get("n_at_midnight") is not None, (times, floor)
            for seed in (0, 1):
                written = kpi_shapes.twin_text(described, seed)
                assert kpi_shapes.missed(kpi_shapes.measure(described, written, f"t{seed}.csv")) == [], (times, floor, seed)


def test_a_dense_grid_of_random_times_keeps_its_clock_facts(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Lane J2's second skeptic, item 1 (NF121, NF122): random times on the hour, on 30-, 15-
    and 5-minute slots, and stamps written to the minute with seconds `:00`, 3,000 to 10,000
    rows, fill half or more of their lattice yet no more than a uniform draw of their rows
    would, so they are not crowded: they publish their heaps, at least 98 % of the twin's cells
    stand at second 0, and the twins miss nothing at floors 11 and 36 -- the half-hour grid
    but `second_heaps.counts`, lane T3's own (P4-D372), missed at floor 36 by 2399488 alike.
    Mutant: the fill alone asked, as the rule was built at 79d7440, the facts are withheld and
    7 % or less of the twin's cells stand at second 0."""
    for kind, rows, days in _DENSE_GRIDS:
        cells = _dense_grid(kind, rows, days)
        for floor in (11, 36):
            described = _one_column(tmp_path / f"{kind}-{rows}-{floor}", "c", cells, floor)
            block = described.block("c")
            assert block["second_heaps"], (kind, rows, floor)
            if kind != "min0":
                assert block["minute_heaps"], (kind, rows, floor)
            written = kpi_shapes.twin_text(described, 0)
            missed = kpi_shapes.missed(kpi_shapes.measure(described, written, "t.csv"))
            allowed = {"c:second_heaps.counts"} if kind == "half" else set()
            assert set(missed) <= allowed, (kind, rows, floor, missed)
            twin = shapes.cells_of(written, "c")
            assert sum(1 for cell in twin if cell.endswith(":00")) >= 0.98 * len(twin), (kind, rows, floor)
    assert not calendar_clock.lattice_crowded(300, 0, 299_700, 600, False, 900)
    assert calendar_clock.lattice_crowded(300, 0, 299_700, 600, False, 0)
    assert calendar_clock.lattice_crowded(300, 0, 299_700, 1000, True, 1000)
    assert calendar_clock.lattice_crowded(300, 0, 299_700, 500, False, 500)
    plain = calendar_clock.lattice_crowded
    monkeypatch.setattr(
        calendar_clock, "lattice_crowded",
        lambda unit, low, high, distinct, all_different=False, parsed=0, midnight_counted=True: plain(
            unit, low, high, distinct, all_different
        ),
    )
    described = _one_column(tmp_path / "fill-alone", "c", _dense_grid("hour", 3000, 60))
    assert described.block("c")["second_heaps"] == []
    twin = shapes.cells_of(kpi_shapes.twin_text(described, 0), "c")
    assert sum(1 for cell in twin if cell.endswith(":00")) < 0.1 * len(twin)


def _mostly_at_midnight(rows: int, days: int, timed: int, heavy: int, drawn: int) -> "list[str]":
    """Lane J2's second skeptic, item 2: dates written as datetimes, `rows` of them over `days`
    days from 2015-01-01, the first `timed` drawn at a random minute off midnight; where
    `heavy` is given, that many dates take about three in ten rows between them."""
    pick = random.Random(drawn)
    heavy_days = [pick.randrange(days) for _day in range(heavy)]
    start = datetime.datetime(2015, 1, 1)
    cells: "list[str]" = []
    for row in range(rows):
        day = heavy_days[pick.randrange(heavy)] if heavy and pick.random() < 0.3 else pick.randrange(days)
        moment = start + datetime.timedelta(days=day)
        if row < timed:
            moment = moment + datetime.timedelta(seconds=60 * pick.randrange(1, 1440))
        cells += [moment.strftime("%Y-%m-%d %H:%M:%S")]
    return sorted(cells)


# The mostly-midnight columns 45191fa met, as (rows, days, timed, heavy, drawn, floor).
_MOSTLY_AT_MIDNIGHT = (
    (1000, 60, 5, 0, 3, 11), (1000, 60, 5, 0, 3, 36), (1000, 60, 10, 0, 3, 11),
    (5000, 365, 8, 0, 3, 11), (5000, 365, 8, 0, 3, 36), (5000, 365, 8, 3, 3, 36),
    (1000, 20, 20, 0, 3, 11), (3000, 90, 30, 0, 3, 11), (3000, 90, 30, 0, 3, 36),
    (1000, 60, 10, 0, 5, 36), (1000, 60, 10, 0, 6, 11), (1000, 60, 10, 0, 6, 36),
)


def test_dates_written_as_datetimes_keep_a_count_at_midnight_withheld(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Lane J2's second skeptic, item 2 (NF123, NF124 since Codex's review, item 4): a column
    mostly at midnight whose count there is withheld for its size -- fewer cells than the line
    off 00:00:00 -- withholds its minute's and second's facts, so the twin is not left whole hours to
    stand the ranks it owes a midnight on; every column of this battery 45191fa met is met at seeds 0 to
    2. Mutant: the rule withdrawn, the 1,000 dates over 60 days with 10 timed publish both
    heaps and their twin misses `midnight.withheld` with 983 of 990 at midnight."""
    for rows, days, timed, heavy, drawn, floor in _MOSTLY_AT_MIDNIGHT:
        shape = (rows, days, timed, heavy, drawn, floor)
        cells = _mostly_at_midnight(rows, days, timed, heavy, drawn)
        described = _one_column(tmp_path / "-".join(str(part) for part in shape), "c", cells, floor)
        block = described.block("c")
        if block.get("n_at_midnight") is None:
            for key in ("minute_census", "minute_heaps", "second_census", "second_heaps"):
                assert block[key] == [], (shape, key)
        for seed in (0, 1, 2):
            written = kpi_shapes.twin_text(described, seed)
            assert kpi_shapes.missed(kpi_shapes.measure(described, written, f"t{seed}.csv")) == [], (shape, seed)
    monkeypatch.setattr(taxonomy, "_off_midnight_below_the_line", lambda *_arguments: False)
    described = _one_column(tmp_path / "withdrawn", "c", _mostly_at_midnight(1000, 60, 10, 0, 3))
    assert described.block("c")["minute_heaps"] and described.block("c")["second_heaps"]
    written = kpi_shapes.twin_text(described, 0)
    assert "c:midnight.withheld" in kpi_shapes.missed(kpi_shapes.measure(described, written, "m.csv"))


def test_a_column_at_midnight_says_its_own_reason(tmp_path: pathlib.Path) -> None:
    """Codex's review of lane J2, item 4 (NF123, NF124): 1,000 dates over 60 days from
    2015-01-01 (each day `random.Random(3).randrange(60)`), the first ten at 09:00:00 and the
    rest at midnight, floor 11: every minute and second is 0, so no count away from value 0
    stands and NF118's reason is not this column's (e69e534 said it). Its count at midnight
    withheld, both fields are withheld with the notes of their own, and the twins at seeds 0
    to 2 miss nothing."""
    pick = random.Random(3)
    start = datetime.datetime(2015, 1, 1)
    cells: "list[str]" = []
    for row in range(1000):
        moment = start + datetime.timedelta(days=pick.randrange(60))
        if row < 10:
            moment = moment + datetime.timedelta(hours=9)
        cells += [moment.strftime("%Y-%m-%d %H:%M:%S")]
    described = _one_column(tmp_path / "midnight", "c", sorted(cells))
    block = described.block("c")
    assert block.get("n_at_midnight") is None
    for key in ("minute_census", "minute_heaps", "second_census", "second_heaps"):
        assert block[key] == [], key
    said = [note["note"] for note in described.document["publication_notes"] if note["column"] == "c"]
    for form in (taxonomy.NOTE_MINUTE_WITHHELD_MIDNIGHT_UNCOUNTED, taxonomy.NOTE_SECOND_WITHHELD_MIDNIGHT_UNCOUNTED):
        assert taxonomy.rendered(form, ()) in said, form
    for form in (taxonomy.NOTE_MINUTE_WITHHELD_OFF_MIDNIGHT, taxonomy.NOTE_SECOND_WITHHELD_OFF_MIDNIGHT):
        assert taxonomy.rendered(form, ()) not in said, form
    for seed in (0, 1, 2):
        written = kpi_shapes.twin_text(described, seed)
        assert kpi_shapes.missed(kpi_shapes.measure(described, written, f"t{seed}.csv")) == [], seed


def test_minutes_on_the_hour_publish_where_one_count_is_closer(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Mornings 70 per cent on :00 or :30 beside afternoons at 40 depend on the
    hour, yet one count over every hour is closer to each than a flat field:
    they publish at 1,000 rows and floors 11 and 36 and their twins miss
    nothing, mornings and afternoons both nearer their real share than a flat
    twin (the lane's skeptic, item 7: withheld, both came back at 4 to 5 per
    cent against 73.5 and 41.5); with M3's second question withdrawn they are
    withheld (night charting beside day entries is withheld either way, in
    `test_the_clock_battery_publishes_its_census`)."""
    cells = shapes.two_shifts(random.Random(76000), 1000)

    def morning_share(written: "list[str]", morning: bool) -> float:
        inside = [cell for cell in written if (int(cell[11:13]) < 12) == morning]
        return sum(1 for cell in inside if cell[14:16] in ("00", "30")) / len(inside)

    for floor in (11, 36):
        described = _one_column(tmp_path / f"f{floor}", "shifts", cells, floor)
        assert described.block("shifts")["minute_heaps"], floor
        written = kpi_shapes.twin_text(described, 0)
        assert kpi_shapes.missed(kpi_shapes.measure(described, written, "t.csv")) == [], floor
        twin = shapes.cells_of(written, "shifts")
        for morning in (True, False):
            assert abs(morning_share(twin, morning) - morning_share(cells, morning)) < morning_share(cells, morning) - 2 / 60, (floor, morning)
    monkeypatch.setattr(calendar_clock, "misled_by_the_count", lambda *_arguments: True)
    assert _one_column(tmp_path / "withdrawn", "shifts", cells).block("shifts")["minute_heaps"] == []


def test_a_second_census_of_a_few_values_says_so(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Seventy moments on seconds 0 to 9, each written five times, publish no second
    census and say why (NF120, the lane's skeptic, item 6: it had said nothing);
    with the few-values rule withdrawn a census of the seconds is published."""
    cells = shapes.second_few(random.Random(74000), 1000)
    described = _one_column(tmp_path / "few", "few", cells)
    block = described.block("few")
    assert block["second_census"] == [] and block["second_heaps"] == []
    said = [note["note"] for note in described.document["publication_notes"] if note["column"] == "few"]
    assert taxonomy.rendered(taxonomy.NOTE_SECOND_WITHHELD_FEW_VALUES, ()) in said
    monkeypatch.setattr(calendar_clock, "few_values", lambda _groups, _units, _heaps: False)
    assert _one_column(tmp_path / "withdrawn", "few", cells).block("few")["second_census"]


# THE SKEPTIC'S FUZZED COLUMNS (`clock_field_shapes.fuzzed`, seed 1) whose count
# of different values G7.3h had cost and 2341173, which publishes no minute or
# second fact, had held: subsecond columns -- the twin writes no figure below
# the second -- and columns at the second in bursts beside cells at midnight.
FUZZED = (1, 28, 58, 86, 105, 120, 194, 199)


@pytest.mark.parametrize("number", FUZZED)
def test_the_fuzzed_columns_keep_their_count(tmp_path: pathlib.Path, number: int) -> None:
    """Each describes, loads and comes back at seed 0 with nothing MISSED, as on
    2341173 (the lane's skeptic, item 3); a subsecond column publishes no
    second census (SE3)."""
    cells, floor, precision = shapes.fuzzed(1, number)
    described = _one_column(tmp_path, "c", cells, floor)
    block = described.block("c")
    if precision == "subsecond":
        assert block["second_census"] == [] and block["second_heaps"] == [], number
    written = kpi_shapes.twin_text(described, 0)
    assert kpi_shapes.missed(kpi_shapes.measure(described, written, "t.csv")) == [], number


# THE SECOND SKEPTIC'S SUBSECOND COLUMNS (`clock_field_shapes.fuzzed`, seed 3, item 2)
# that published a minute fact their twin, writing no figure below the second, could
# not meet beside the count -- a heap at minute 21 holding 2,126 cells of one day
# came back 2,960 values to 2,315 -- with what 2341173 missed on each, the ceiling.
SUBSECOND_MINUTES = {
    76: [],
    136: [],
    147: ["c:distinct.n_distinct", "c:distinct.n_distinct_folded"],
}


@pytest.mark.parametrize("number", sorted(SUBSECOND_MINUTES))
def test_subsecond_minutes_stand_only_where_the_second_keeps_the_count(
    tmp_path: pathlib.Path, number: int
) -> None:
    """A column written finer than the second whose body, cut to the second,
    holds fewer different values publishes no minute fact, says nothing, and
    its twin at seed 0 misses nothing 2341173 held (the lane's second
    skeptic, item 2)."""
    cells, floor, precision = shapes.fuzzed(3, number)
    assert precision == "subsecond"
    described = _one_column(tmp_path, "c", cells, floor)
    block = described.block("c")
    assert block["minute_heaps"] == [] and block["minute_census"] == [], number
    written = kpi_shapes.twin_text(described, 0)
    missed = kpi_shapes.missed(kpi_shapes.measure(described, written, "t.csv"))
    assert set(missed) <= set(SUBSECOND_MINUTES[number]), (number, missed)


def test_red_when_the_subsecond_minute_rule_is_withdrawn(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Withdrawn, the 1,500 cells each written apart by the millisecond publish a
    heap at minute 14 and come back about two hundred values short."""
    monkeypatch.setattr(taxonomy, "_cut_to_the_second_merges", lambda *_arguments: False)
    cells, floor, _precision = shapes.fuzzed(3, 136)
    described = _one_column(tmp_path, "c", cells, floor)
    assert described.block("c")["minute_heaps"]
    written = kpi_shapes.twin_text(described, 0)
    assert "c:distinct.n_distinct" in kpi_shapes.missed(kpi_shapes.measure(described, written, "t.csv"))


# What 2341173 missed on the small bursty tables of the lane's skeptic (item 3):
# the ceiling, by rows and seed.
SMALL_BURSTS_CEILING = {(300, 2): ["bursts:distinct.n_distinct", "bursts:distinct.n_distinct_folded"]}
# ...AND BESIDE LANE D2'S WEEKDAY CENSUS (lane J2's merge of this landing): these
# tables publish one, and the hour pass then leaves their count long -- measured on
# 45191fa, which publishes no minute or second fact, at all ten twins (61 to 67 for
# 59 at 200 rows, 95 to 105 for 84 at 300); the minute pass, paid back, meets it at
# 200 rows seeds 0 and 3 and leaves the rest long, named.
SMALL_BURSTS_CEILING.update(
    {
        key: ["bursts:distinct.n_distinct", "bursts:distinct.n_distinct_folded"]
        for key in [(200, 1), (200, 2), (200, 4)] + [(300, seed) for seed in range(5)]
    }
)


def test_small_bursty_tables_keep_their_count(tmp_path: pathlib.Path) -> None:
    """Check-ins in bursts at 200 and 300 rows, floor 11, seeds 0 to 4, miss nothing
    2341173 held: SUBSTITUTE asked again while a round puts a value back, its join
    reaching the kin on other days (measured: 3 of 10 twins came back long
    after one round; 1 of 10 after three without the kin on other days)."""
    for rows in (200, 300):
        cells = shapes.bursts(random.Random(72011 + rows), rows)
        described = _one_column(tmp_path / f"b{rows}", "bursts", cells)
        for seed in range(5):
            written = kpi_shapes.twin_text(described, seed)
            missed = kpi_shapes.missed(kpi_shapes.measure(described, written, f"t{seed}.csv"))
            ceiling = SMALL_BURSTS_CEILING[(rows, seed)] if (rows, seed) in SMALL_BURSTS_CEILING else []
            assert set(missed) <= set(ceiling), (rows, seed, missed)


# THE SECOND SKEPTIC'S SMALL BURSTY TABLES (item 1): check-ins in bursts from tables
# 95000, 96000 and 97000 at 200, 300 and 500 rows, floors 11 and 36, seeds 0 to 4.
# What 2341173 missed on them (its twins missing the count of different values),
# measured by the skeptic -- the ceiling, beside the twins whose census stood and
# whose count gave way, named (the plan's RESIDUAL; method G7.3h) -- and the values
# off over each table's thirty twins at a floor of 36, measured with the whole-unit
# rule (fcfc8ef: 157 over the three tables; 2341173, publishing no minute census: 74).
BURSTS_BASE_MISSED = (
    {(95000, 200, 36, seed) for seed in range(5)}
    | {(95000, 300, 36, seed) for seed in (2, 3, 4)}
    | {(96000, 200, 36, seed) for seed in range(5)}
    | {(96000, 300, 36, seed) for seed in range(5)}
    | {(97000, 200, 11, 1)}
)
# ...and what 45191fa misses on them beside lane D2's weekday census, publishing no
# minute or second fact (lane J2's merge of this landing): the hour pass leaves the
# count long, 85 of the 105 twins, and the minute pass paid back leaves 83.
BURSTS_BASE_MISSED |= (
    {(95000, 200, 11, seed) for seed in (0, 2, 3, 4)}
    | {(95000, rows, floor, seed) for rows in (300, 500) for floor in (11, 36) for seed in range(5)}
    | {(96000, 300, floor, seed) for floor in (11, 36) for seed in range(5)}
    | {(96000, 500, 11, seed) for seed in range(5)}
    | {(97000, 300, floor, seed) for floor in (11, 36) for seed in range(5)}
    | {(97000, 500, floor, seed) for floor in (11, 36) for seed in range(5)}
)
BURSTS_COUNT_GIVES_WAY = {(97000, 200, 36, seed) for seed in range(5)} | {(97000, 300, 36, 2), (97000, 300, 36, 4)}
# 97000 at 9: KIN SHARES' CLAIMS (the verifier's item 10 on the Codex round)
# keep a kin group's carried share from the kin groups before it, and the
# fifteen twins at 36 come back 9 values off where ddc5263's came back 6,
# the one more twin missing its count named, as 707cf99's was.
# Beside lane D2's weekday census the values off are the hour pass's: 67, 85 and 51
# over the fifteen twins at 36 (lane J2; 45191fa, no minute fact: 67, 84 and 54).
BURSTS_VALUES_OFF = {95000: 67, 96000: 85, 97000: 51}
COUNT_ONLY = {"bursts:distinct.n_distinct", "bursts:distinct.n_distinct_folded"}


def _twin_and_cause(described: kpi_shapes.Described, seed: int) -> "tuple[str, bool]":
    """The twin's bytes, and whether its report names the clock pass's long cause."""
    twin = generation.generate(described.loaded, seed)
    named = any(
        deviation.fact == "n_distinct" and deviation.note == generation._CLOCK_FIELDS_LEFT_LONG
        for deviation in twin.deviations
    )
    return rendering.twin_csv(twin), named


@pytest.mark.parametrize("table", sorted(BURSTS_VALUES_OFF))
def test_small_bursty_tables_keep_their_count_at_both_floors(tmp_path: pathlib.Path, table: int) -> None:
    """Each twin misses at most the count of different values, and only where
    2341173 missed it or the census stood and the count gave way, named in the
    report; the values off at a floor of 36 stay within what the whole-unit rule
    measured (the lane's second skeptic, item 1: fcfc8ef newly missed the count on
    11 of the 45 twins at 36, 87 to 88, 49 to 52, 90 to 94; red with a shared unit
    split by a single move, or no unit carried past its groups' room)."""
    off = 0
    for rows in (200, 300, 500):
        cells = shapes.bursts(random.Random(table + rows), rows)
        for floor in (11, 36):
            described = _one_column(tmp_path / f"b{rows}-{floor}", "bursts", cells, floor)
            for seed in range(5):
                key = (table, rows, floor, seed)
                written, named = _twin_and_cause(described, seed)
                missed = set(kpi_shapes.missed(kpi_shapes.measure(described, written, f"t{seed}.csv")))
                assert missed <= COUNT_ONLY, (key, missed)
                if missed:
                    assert key in BURSTS_BASE_MISSED | BURSTS_COUNT_GIVES_WAY, (key, missed)
                if missed and key not in BURSTS_BASE_MISSED:
                    assert named, key
                if floor == 36:
                    off = off + abs(len(set(shapes.cells_of(written, "bursts"))) - len(set(cells)))
    assert off <= BURSTS_VALUES_OFF[table], (table, off)


def test_a_fuzzed_column_of_heaps_names_its_count(tmp_path: pathlib.Path) -> None:
    """The second skeptic's fuzz seed 3, case 111 (minute precision, 60 rows, three
    heaps, floor 1): its heaps are met, and the count of different values the
    census cost, 27 to 29, is named in the report as the clock pass's."""
    cells, floor, _precision = shapes.fuzzed(3, 111)
    described = _one_column(tmp_path, "c", cells, floor)
    assert described.block("c")["minute_heaps"]
    written, named = _twin_and_cause(described, 0)
    missed = set(kpi_shapes.missed(kpi_shapes.measure(described, written, "t.csv")))
    assert missed <= {"c:distinct.n_distinct", "c:distinct.n_distinct_folded"}, missed
    if missed:
        assert named


def test_heaps_beside_a_withheld_rest_pin_no_lattice(tmp_path: pathlib.Path) -> None:
    """Bursts of check-ins publish heaps at minutes 0 and 30 beside a census of the
    rest withheld for its few values, a third of the body off them: no lattice
    is pinned, and no minute off the heaps comes back above three times the
    real column's busiest (the lane's skeptic, item 2: drawn on half hours,
    the rest piled on :01 or :29, 15 to 24 per cent of every cell against 1.2
    to 1.8 real; the frozen case `lattice_rest_withheld` holds the rule)."""
    cells = shapes.bursts(random.Random(73011), 1000)
    described = _one_column(tmp_path, "bursts", cells)
    block = described.block("bursts")
    assert block["minute_heaps"] and block["minute_census"] == []
    assert _unit_of(described, "bursts") == 1
    heaps = {heap["value"] for heap in block["minute_heaps"]}
    real = _field_counts(cells, shapes.US, "minute")
    busiest = max(real[value] for value in range(60) if value not in heaps)
    for seed in (0, 1, 2):
        written, named = _twin_and_cause(described, seed)
        twin = _field_counts(shapes.cells_of(written, "bursts"), shapes.US, "minute")
        assert max(twin[value] for value in range(60) if value not in heaps) <= 3 * busiest, seed
        missed = kpi_shapes.missed(kpi_shapes.measure(described, written, f"t{seed}.csv"))
        # Beside lane D2's weekday census the hour pass leaves this table's count long
        # (45191fa, no minute fact: 289 to 303 for 286 at seeds 0 to 4); the minute pass
        # paid back meets it but at seed 0, 292, named (lane J2).
        assert set(missed) == (set() if seed else COUNT_ONLY), (seed, missed)
        assert named == bool(missed), seed


def test_the_counts_off_midnight_by_hand() -> None:
    """The counts away from value 0 must fit in the body less its count at midnight."""
    assert calendar_clock.off_midnight_short((), ((30, 11),), 977, 989)
    assert not calendar_clock.off_midnight_short((), ((30, 11),), 977, None)
    assert not calendar_clock.off_midnight_short((), ((30, 11),), 977, 966)
    assert calendar_clock.off_midnight_short((), ((30, 11),), 977, 967)
    # A heap on 0 holds the cells at midnight; a group lying over 0 too,
    # where 0 is no heap.
    assert not calendar_clock.off_midnight_short(((1, 59, 500),), ((0, 400),), 977, 300)
    assert calendar_clock.off_midnight_short(((1, 59, 700),), ((0, 200),), 977, 300)
    assert not calendar_clock.off_midnight_short(((0, 29, 500), (30, 59, 400)), (), 977, 500)
    assert calendar_clock.off_midnight_short(((0, 29, 400), (30, 59, 500)), (), 977, 500)


# -- the loader's rules ------------------------------------------------------------------


def _refusal(folder: pathlib.Path, document: dict) -> str:
    """What the loader says when it refuses this document."""
    path = fixtures.write_profile(folder, "refused-profile.json", document)
    with pytest.raises(errors.ProfileError) as raised:
        contract.load_profile(str(path))
    return f"{raised.value}"


def _edited(described: kpi_shapes.Described, name: str, **changes: object) -> dict:
    document = copy.deepcopy(described.document)
    for entry in document["columns"]:
        if entry["name"] == name:
            entry.update(changes)
    return document


def test_mc1_the_groups_cover_the_minutes_in_order(thousand, tmp_path: pathlib.Path) -> None:
    described, _columns, _text = thousand
    groups = described.block("discharges")["minute_census"]
    shifted = [dict(groups[0], first=1)] + groups[1:]
    assert "MC1" in _refusal(tmp_path, _edited(described, "discharges", minute_census=shifted))


def test_mc2_every_count_is_nought_or_at_the_line(thousand, tmp_path: pathlib.Path) -> None:
    described, _columns, _text = thousand
    groups = copy.deepcopy(described.block("discharges")["minute_census"])
    first = next(index for index in range(len(groups)) if groups[index]["count"] > LINE + 1)
    moved = groups[first]["count"] - 5
    groups[first]["count"] = 5
    groups[first + 1]["count"] += moved
    assert "MC2" in _refusal(tmp_path, _edited(described, "discharges", minute_census=groups))


def test_mc3_the_scope_and_the_total(thousand, tmp_path: pathlib.Path) -> None:
    """A total off the body less the heaps is refused; and a census on a column read on
    the shared clock, wholly at midnight or with no tails is refused by the reader."""
    described, _columns, _text = thousand
    groups = copy.deepcopy(described.block("discharges")["minute_census"])
    groups[-1]["count"] += LINE
    assert "MC3" in _refusal(tmp_path, _edited(described, "discharges", minute_census=groups))
    column = next(column for column in described.loaded.columns if column.name == "discharges")
    facts = column.facts
    assert isinstance(facts, contract.DatetimeFacts)
    block = described.block("discharges")
    mapping = {key: block[key] for key in ("minute_census", "second_census", "minute_heaps", "second_heaps")}
    for scope in ({"datetimes_read_at": "utc"}, {"all_at_midnight": True}, {"low_tail": None}):
        with pytest.raises(errors.ProfileError) as raised:
            contract._clock_field_censuses(
                mapping, "here", LINE, column.n_present, column.n_distinct, (), (),
                dataclasses.replace(facts, **scope),
            )
        assert contract.INVARIANTS["MC3"] in f"{raised.value}", scope


@pytest.mark.parametrize("precision", ["minute", "subsecond"])
def test_sc3_a_second_census_needs_seconds(thousand, precision: str) -> None:
    """A second census on a column written to the minute, or finer than the
    second, is refused (SE3; the twin writes no figure below the second)."""
    described, _columns, _text = thousand
    column = next(column for column in described.loaded.columns if column.name == "zero_seconds")
    facts = column.facts
    assert isinstance(facts, contract.DatetimeFacts)
    block = described.block("zero_seconds")
    mapping = {key: block[key] for key in ("minute_census", "second_census", "minute_heaps", "second_heaps")}
    with pytest.raises(errors.ProfileError) as raised:
        contract._clock_field_censuses(
            mapping, "here", LINE, column.n_present, column.n_distinct, (), (),
            dataclasses.replace(facts, time_precision=precision),
        )
    assert contract.INVARIANTS["SE3"] in f"{raised.value}"


def test_mc4_the_middle_half_spans_four_hours(thousand, tmp_path: pathlib.Path) -> None:
    described, _columns, _text = thousand
    block = described.block("three_hours")
    body = block["n_present"] - block["low_tail"]["rows"] - block["high_tail"]["rows"]
    heaps = [{"value": 0, "count": body}]
    said = _refusal(tmp_path, _edited(described, "three_hours", minute_heaps=heaps))
    assert contract.INVARIANTS["MC4"] in said, said


def test_mc5_a_group_holds_its_sure_cells(thousand, tmp_path: pathlib.Path) -> None:
    """A group the rest of the description places more cells in than it counts is refused:
    admissions count their bare days at midnight in the group holding minute 0."""
    described, _columns, _text = thousand
    block = described.block("admissions")
    groups = copy.deepcopy(block["minute_census"])
    assert groups[0]["first"] == 0 and block["n_at_midnight"] is not None
    shift = groups[0]["count"] - LINE
    groups[0]["count"] -= shift
    groups[1]["count"] += shift
    assert "MC5" in _refusal(tmp_path, _edited(described, "admissions", minute_census=groups))


def test_mh1_a_heap_counts_at_least_the_line_in_order(thousand, tmp_path: pathlib.Path) -> None:
    described, _columns, _text = thousand
    heaps = copy.deepcopy(described.block("quarter_grid")["minute_heaps"])
    reversed_heaps = list(reversed(heaps))
    assert "MH1" in _refusal(tmp_path, _edited(described, "quarter_grid", minute_heaps=reversed_heaps))
    small = copy.deepcopy(heaps)
    small[0]["count"] = 5
    assert "MH1" in _refusal(tmp_path, _edited(described, "quarter_grid", minute_heaps=small))


def test_mh2_the_heaps_hold_no_more_than_the_body(thousand, tmp_path: pathlib.Path) -> None:
    described, _columns, _text = thousand
    heaps = copy.deepcopy(described.block("quarter_grid")["minute_heaps"])
    heaps[0]["count"] += 5000
    assert "MH2" in _refusal(tmp_path, _edited(described, "quarter_grid", minute_heaps=heaps))


def test_sh1_and_sh2_second_heaps(thousand, tmp_path: pathlib.Path) -> None:
    described, _columns, _text = thousand
    heaps = copy.deepcopy(described.block("zero_seconds")["second_heaps"])
    heaps[0]["count"] += 5000
    assert "SH2" in _refusal(tmp_path, _edited(described, "zero_seconds", second_heaps=heaps))
    twice = [dict(heaps[0], count=heaps[0]["count"] - 5000)] * 2
    assert "SH1" in _refusal(tmp_path, _edited(described, "zero_seconds", second_heaps=twice))
    out_of_range = [{"value": 60, "count": heaps[0]["count"] - 5000}]
    _refusal(tmp_path, _edited(described, "zero_seconds", second_heaps=out_of_range))


def test_mc6_and_sc6_one_storage_per_workbook_column() -> None:
    """MC6 and SE6 read the published cell classes, as HC6 does."""
    assert calendar_rules.published_one_way({"date": 300, "text": 12}) is False
    assert "MC6" in contract.INVARIANTS and "SE6" in contract.INVARIANTS


@pytest.mark.parametrize("floor", [1, 11, 36])
def test_every_description_the_producer_writes_loads(tmp_path: pathlib.Path, floor: int) -> None:
    """THE PRODUCER-ALWAYS-LOADS BATTERY: every shape at 300 and 1,000 rows, described at
    floors 1, 11 and 36, loads -- the new rules refuse nothing the producer writes."""
    for rows in (300, 1000):
        columns = shapes.thousand(rows, 72100 + rows + floor)
        described = kpi_shapes.describe(tmp_path / f"r{rows}", "battery", shapes.table_text(columns), floor)
        assert described.loaded is not None


# -- the frozen states: vectors file 20 -----------------------------------------------------

_FILE = json.loads(VECTORS.read_text(encoding="utf-8"))


def _state(case: dict, module=generation):
    field = case["field_unit"]
    state = module._WeekdayPass(
        moved=list(case["ordinals"]), held={}, where=tuple(case["where"]), facts=None,
        word="", widths=False, kinds={}, holes=frozenset(case["holes"]), lows=list(case["lows"]),
        highs=list(case["highs"]), keep_units=case["reachable"], unit=field,
        step=case["written_unit"], day=DAY, bins="minute" if field == 60 else "second",
        period=60, keeps="hour" if field == 60 else "minute", count_steps=False,
        kin=tuple(case["kin"]), no_midnight=case["no_midnight"],
        whole_units=case.get("whole_units", False),
    )
    for ordinal in state.moved:
        module._weekday_tally(state.held, ordinal // state.step, 1)
        if state.unit != state.step:
            module._weekday_tally(state.units_held, ordinal // state.unit, 1)
    return state


def _answer(case: dict, module=generation, clock=calendar_clock) -> object:
    """What the product's step makes of a case, in the file's own form."""
    step = case["step"]
    if step == "lattice":
        return clock.drawing_unit(
            case["precision"],
            (
                tuple((g["first"], g["last"], g["count"]) for g in case["minute_census"]),
                tuple((h["value"], h["count"]) for h in case["minute_heaps"]),
            ),
            (
                tuple((g["first"], g["last"], g["count"]) for g in case["second_census"]),
                tuple((h["value"], h["count"]) for h in case["second_heaps"]),
            ),
            list(case["texts"]),
            case["body"],
            case["line"],
        )
    if step == "floor":
        return [module._on_draw_unit(value, case["unit"], low, high) for value, low, high in case["draws"]]
    if step == "tail_end":
        column = case["column"]
        body = case["parsed"] - column["low_tail"]["rows"] - column["high_tail"]["rows"]

        def kept(name: str, field: str) -> tuple:
            if name == "heaps":
                return tuple((h["value"], h["count"]) for h in column[f"{field}_heaps"])
            return tuple((g["first"], g["last"], g["count"]) for g in column[f"{field}_census"])

        room = [clock.tail_ends_midnight_room(
            column["n_at_midnight"],
            clock.body_sure_at_midnight(
                [(g["first"], g["last"], g["count"]) for g in column["hour_census"]],
                (kept("census", "minute"), kept("heaps", "minute")),
                (kept("census", "second"), kept("heaps", "second")),
                column["time_precision"], body,
            ),
            [(column[side]["rows"], column[side]["values"]) for side in ("low_tail", "high_tail")],
        )]
        holes = {unit: True for unit in case["holes"]}
        return [module._tail_end_held(end, at, low, holes, case["seconds"], room) for end, at, low in case["ends"]]
    if step == "midnight_count":
        moved = list(case["ordinals"])
        first, last = case["body"]
        module._clock_midnight_count_kept(
            case["counted"], moved, list(case["pinned"]), first, last, case["written_unit"],
            case["away"], list(case["lows"]), list(case["highs"]), case.get("owed", False),
            set(case.get("hole_days", [])),
        )
        return moved
    state = _state(case, module)
    first, last = case["body"]
    pinned = list(case["pinned"])
    standing = tuple(case["standing"])
    kin = tuple(case["kin"])
    if step == "field":
        module._clock_field_settled(
            state, list(case["counts"]), first, last, pinned, case["wanted"], standing,
            case["anyday"], kin, case["published"],
        )
    elif step == "exchange":
        module._clock_off_midnight_exchanged(state, list(case["before"]), first, last, pinned, kin)
    elif step == "substitute":
        module._clock_split_substituted(state, first, last, pinned, case["wanted"], standing, case["anyday"], kin)
    elif step == "spread":
        module._clock_short_spread(state, first, last, pinned, case["wanted"], standing, case["anyday"], kin)
    elif step == "paid_spread":
        module._clock_paid_spread(state, first, last, pinned, case["wanted"], standing, kin)
    elif step == "paid_put_back":
        module._clock_paid_put_back(state, first, last, pinned, case["wanted"], standing)
    elif step == "spread_substitute":
        module._clock_spread_substituted(state, first, last, pinned, case["wanted"])
    elif step == "room":
        module._clock_midnight_room_made(
            state, list(case["counts"]), first, last, pinned, list(case["tail_pins"]),
            case["written_unit"], case["away"],
        )
    elif step == "room_kept":
        module._clock_midnight_room_kept(
            state, list(case["counts"]), first, last, pinned, list(case["tail_pins"]),
            case["written_unit"], case["away"], case["wanted"], standing, case["anyday"], kin,
        )
    return state.moved


def _oracle():
    spec = importlib.util.spec_from_file_location("make_generation_reference_vectors_t3", ORACLE)
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def _mutant(monkeypatch: pytest.MonkeyPatch, before: str, after: str):
    """The product's generation module with ONE source edit, built beside it (applied
    exactly once: an edit that no longer applies turns the test red)."""
    assert SOURCE.count(before) == 1, before
    name = "synthtwin._generation_minutes_mutant"
    module = types.ModuleType(name)
    module.__file__ = generation.__file__
    monkeypatch.setitem(sys.modules, name, module)
    exec(compile(SOURCE.replace(before, after), generation.__file__, "exec"), module.__dict__)
    return module


class _Clock:
    """`calendar_clock` with ONE edit, for the drawing rule's mutants."""

    def __init__(self, before: str, after: str) -> None:
        source = pathlib.Path(calendar_clock.__file__).read_text(encoding="utf-8")
        assert source.count(before) == 1, before
        name = "synthtwin._calendar_clock_minutes_mutant"
        module = types.ModuleType(name)
        module.__file__ = calendar_clock.__file__
        sys.modules[name] = module
        try:
            exec(compile(source.replace(before, after), calendar_clock.__file__, "exec"), module.__dict__)
        finally:
            del sys.modules[name]
        self.module = module


# Each case's mutant: the one edit that withdraws or bends the step the case
# freezes, and the case it turns red.
STEP_MUTANTS = {
    "the minute's bin rule withdrawn": (
        "field_minute_heaps",
        '    if rule == "minute":\n        return (ordinal // 60) % 60\n',
        '    if rule == "minute":\n        return (ordinal // 3600) % 60\n',
    ),
    "the minute's parent not kept": (
        "field_minute_heaps",
        "    if state.keeps in _PARENT_SPANS:\n        return ordinal // _PARENT_SPANS[state.keeps]\n    return 0\n",
        "    return 0\n",
    ),
    "the second's bin rule withdrawn": (
        "field_second_zero",
        '    if rule == "second":\n        return ordinal % 60\n',
        '    if rule == "second":\n        return (ordinal // 60) % 60\n',
    ),
    "the exchange off midnight withdrawn": (
        "field_exchange_swap",
        "                state, whole, by_kind, into, len(members), own, members\n            ) is None:\n                continue\n            for rank in members:",
        "                state, whole, by_kind, into, len(members), own, members\n            ) is None or True:\n                continue\n            for rank in members:",
    ),
    "the exchange's kin answer withdrawn": (
        "field_exchange_kin",
        "            kept = _clock_off_midnight_elsewhere(state, members, here, kin)",
        "            kept = None",
    ),
    "the exchange made with no run to take the place": (
        "field_exchange_stays",
        "                state, whole, by_kind, into, len(members), own, members\n            ) is None:\n                continue\n            for rank in members:",
        "                state, whole, by_kind, into, len(members), own, members\n            ) is None:\n                pass\n            for rank in members:",
    ),
    "SUBSTITUTE withdrawn": (
        "field_substitute",
        "        joined = _clock_join_target(state, first, by_parent, standing, anyday, kin)",
        "        joined = None",
    ),
    "SPREAD's escape withdrawn": (
        "field_spread",
        "            target = _clock_escape(\n                state, here, low, high, 1, have, want, standing, anyday, kin, days\n            )",
        "            target = None",
    ),
    "the tails keep no count at midnight": (
        "field_midnight_tails",
        "        if at > counted and here:\n            if moved[rank] + away <= gap_highs[rank]:",
        "        if False:\n            if moved[rank] + away <= gap_highs[rank]:",
    ),
    "a gap's shares not split over its kin groups": (
        "field_kin_shares",
        "        split = bool(state.kin) and _clock_kin_shares_moved(state, ranks, want)",
        "        split = False and _clock_kin_shares_moved(state, ranks, want)",
    ),
    "a kin group's rank may split a unit it shares": (
        "field_kin_no_split",
        "        _weekday_singles_moved(state, members, have, share, _WEEKDAY_SINGLE_ROUNDS, False, False)",
        "        _weekday_singles_moved(state, members, have, share, _WEEKDAY_SINGLE_ROUNDS, False, True)",
    ),
    "a kin group's rounding not carried to the next gap": (
        "field_kin_carry",
        "            state.kin_carry[(kin, group)] if (kin, group) in state.kin_carry else 0\n",
        "            0\n",
    ),
    "a kin group's carry not reconciled against what it holds": (
        "field_kin_blocked",
        "        if split:\n            _clock_kin_carry_reconciled(state, len(counts))\n",
        "        if False:\n            _clock_kin_carry_reconciled(state, len(counts))\n",
    ),
    "a kin group asked the parts of a group its ranks never reach": (
        "field_kin_unreachable",
        "    if not blocked:\n        parts = {",
        "    if True:\n        parts = {",
    ),
    "a kin group given room on value 0 beyond its free ranks": (
        "field_midnight_zero_room",
        "            min(free[kin], reach[kin][group]) if group == zero else reach[kin][group]\n            for group in range(groups)\n        ]\n    parts",
        "            reach[kin][group]\n            for group in range(groups)\n        ]\n    parts",
    ),
    "no claims kept for the kin groups after": (
        "field_kin_partial",
        "        kept = [max(taken[group], want[group] - after[position][group]) for group in range(groups)]",
        "        kept = [want[group] for group in range(groups)]",
    ),
    "no PUT BACK after the exchange": (
        "field_exchange_put_back",
        "    for last_resort in (False, True):\n        if state.keep_units and _weekday_count(state) > wanted and",
        "    for last_resort in ():\n        if state.keep_units and _weekday_count(state) > wanted and",
    ),
    "the tails make no room at midnight": (
        "field_midnight_room",
        "    if not state.no_midnight or not _clock_zero_alone(state):\n        return\n    zero = state.where[0]\n    found = _clock_found(",
        "    if True:\n        return\n    zero = state.where[0]\n    found = _clock_found(",
    ),
    "a narrow stratum keeps its midnight": (
        "field_midnight_narrow",
        "            elif moved[rank] + step <= gap_highs[rank]:\n                # A STRATUM",
        "            elif False:\n                # A STRATUM",
    ),
    "the tails never give way to a count owed for its size": (
        "field_midnight_owed",
        "    if owed and at < counted and 2 * counted > parsed:\n        _clock_owed_midnight(",
        "    if False:\n        _clock_owed_midnight(",
    ),
    "the owed step stands a tail rank on a hole day": (
        "field_midnight_owed_hole",
        "    hole_days: \"set[int]\",\n) -> None:\n    \"\"\"A count at midnight withheld for its size",
        "    hole_days: \"set[int]\",\n) -> None:\n    hole_days = set()\n    \"\"\"A count at midnight withheld for its size",
    ),
    "the tails take no midnight where the count is short": (
        "field_midnight_short",
        "        elif at < counted and not here:",
        "        elif False:",
    ),
    "a written midnight no kind of its own": (
        "field_midnight_kin",
        "    if state.no_midnight and _written_at_midnight(ordinal, 0, state.step):\n        width, keep, pair = state.kinds[grain]\n",
        "    if False:\n        width, keep, pair = state.kinds[grain]\n",
    ),
    "hour 0 takes its share of a heap at minute 0": (
        "field_midnight_spread",
        "    if state.no_midnight and _clock_zero_alone(state):\n        zero = state.where[0]",
        "    if False:\n        zero = state.where[0]",
    ),
    "the ranks free to take value 0 not counted": (
        "field_midnight_share",
        "                    if not _written_at_midnight(\n",
        "                    if False and not _written_at_midnight(\n",
    ),
    "the tails make room raising the count": (
        "field_midnight_room_keep",
        "            if not (state.keep_units and change + shift > 0):",
        "            if True:",
    ),
    "no SPREAD after the tails make room": (
        "field_midnight_room_spread",
        "    if state.keep_units and _weekday_count(state) < wanted:\n        _clock_short_spread(\n            state, body_low, body_high, pinned, wanted, standing, anyday, kin\n        )\n    # ...and paid back where a weekday census stands (lane J2).\n    if state.keep_units and not anyday and _weekday_count(state) < wanted:\n        _clock_paid_spread(state, body_low, body_high, pinned, wanted, standing, kin)\n        _clock_spread_substituted(state, body_low, body_high, pinned, wanted)\n\n\ndef _clock_second_kin(",
        "    if False:\n        pass\n\n\ndef _clock_second_kin(",
    ),
    # -- lane J2: the field passes' count steps paid back beside a weekday census
    "SPREAD not paid back": (
        "field_paid_spread",
        "            target = _clock_paid_escape(\n                state, book, [rank], low, high, have, want, standing, refused, True\n            )\n",
        "            target = None\n",
    ),
    "a payer taken that changes the count": (
        "field_paid_spread_strict",
        "    if strict:\n        return None\n",
        "    if False:\n        return None\n",
    ),
    "PUT BACK not paid back": (
        "field_paid_put_back",
        "        target = _clock_paid_merge_target(state, book, members, by_parent, standing, refused)\n",
        "        target = None\n",
    ),
    "a payer taken off the unit a run joins": (
        "field_paid_put_back_avoid",
        "    if avoid is not None and state.moved[rank] // state.step == avoid:\n",
        "    if False:\n",
    ),
    "a payer placed on the unit a run leaves": (
        "field_paid_put_back_leaving",
        "    if leaving is not None and place // state.step == leaving:\n",
        "    if False:\n",
    ),
    # Codex's review of lane J2, item 1: -1 for no unit reads every unit before 1970 as none.
    "the unit a run joins excluded only after 1970": (
        "field_paid_put_back_avoid_1947",
        "    if avoid is not None and state.moved[rank] // state.step == avoid:\n",
        "    if avoid is not None and avoid >= 0 and state.moved[rank] // state.step == avoid:\n",
    ),
    "the unit a run leaves excluded only after 1970": (
        "field_paid_put_back_leaving_1947",
        "    if leaving is not None and place // state.step == leaving:\n",
        "    if leaving is not None and leaving >= 0 and place // state.step == leaving:\n",
    ),
    "no SPREAD by substitute": (
        "field_spread_substitute",
        "                if into is None:\n                    continue\n                _weekday_step(state, swap, into)\n",
        "                if True:\n                    continue\n                _weekday_step(state, swap, into)\n",
    ),
    "a run asked as listed": (
        "field_paid_put_back_standing",
        "        members, whole_now = _clock_unit_standing(state, listed, key)\n",
        "        members, whole_now = listed, True\n",
    ),
    "a shared unit split by a single move": (
        "field_whole_unit",
        "    units_whole = state.whole_units and state.keep_units\n",
        "    units_whole = False\n",
    ),
    "no unit carried past its groups' room": (
        "field_whole_unit_past",
        "                elif allow and changing and _weekday_unit_judged(\n                    state, judged, whole, rank, offer[1], have, want, overshot\n                ):\n                    offers +=",
        "                elif False and _weekday_unit_judged(\n                    state, judged, whole, rank, offer[1], have, want, overshot\n                ):\n                    offers +=",
    ),
    "a tail's END left at a midnight the count leaves it none of": (
        "tail_end",
        "    if room[0] <= 0:\n        return calendar_clock.end_stepped_off(end, at, low_side, holes, seconds, True)\n",
        "    if False:\n        return calendar_clock.end_stepped_off(end, at, low_side, holes, seconds, True)\n",
    ),
    "a draw laid on no unit": (
        "field_floor",
        "    floored = value - value % unit\n    if floored >= low:\n        return floored",
        "    floored = value\n    if floored >= low:\n        return floored",
    ),
}

CLOCK_MUTANTS = {
    "a listed tail charged only for the epoch's midnight": (
        "tail_end_listed",
        '        at = [value for value in values if value[11:19] == "00:00:00"]',
        "        at = [value for value in values if len(value) >= 16 and seconds_of(value) == 0]",
    ),
    "a rest of the line or more pins a lattice": (
        "lattice_rest_withheld",
        "        if body < 0 or body - sum(count for _value, count in heaps) >= line:\n            return 0",
        "        if body < 0:\n            return 0",
    ),
    "the heaps' lattice is the minute": (
        "lattice_half_hour",
        "        for value, _count in heaps:\n            step = common_divisor(step, value)\n        return step",
        "        for value, _count in heaps:\n            step = common_divisor(step, value)\n        return 1",
    ),
    "the minute widens no unit": (
        "lattice_on_the_hour_seconds",
        "    return FIELD_VALUES * minutes\n",
        "    return FIELD_VALUES\n",
    ),
    "the seconds pin nothing": (
        "lattice_seconds_only",
        "    if seconds < FIELD_VALUES:\n        return seconds\n",
        "    if seconds < FIELD_VALUES or True:\n        return 1\n",
    ),
    "one group pins nothing": (
        "lattice_one_group",
        "        if len(holding) != 1 or holding[0][0] != 0:\n            return 0",
        "        if True:\n            return 0",
    ),
}


def test_every_case_is_asked_and_the_oracle_agrees() -> None:
    """The file holds every case the oracle states, each with the oracle's own answer,
    and every case has a mutant here."""
    oracle = _oracle()
    document = oracle.clock_field_step_document()
    assert json.loads(json.dumps(document)) == _FILE
    mutated = {case for case, _before, _after in STEP_MUTANTS.values()} | {case for case, _b, _a in CLOCK_MUTANTS.values()}
    assert mutated == set(_FILE["cases"])


@pytest.mark.parametrize("name", sorted(_FILE["cases"]))
def test_the_product_gives_every_case_its_answer(name: str) -> None:
    case = _FILE["cases"][name]
    assert _answer(case) == case["answer"], name


@pytest.mark.parametrize("mutant", sorted(STEP_MUTANTS))
def test_each_step_case_is_red_on_its_mutant(mutant: str, monkeypatch: pytest.MonkeyPatch) -> None:
    name, before, after = STEP_MUTANTS[mutant]
    case = _FILE["cases"][name]
    assert _answer(case, _mutant(monkeypatch, before, after)) != case["answer"], mutant


@pytest.mark.parametrize("mutant", sorted(CLOCK_MUTANTS))
def test_each_drawing_unit_case_is_red_on_its_mutant(mutant: str) -> None:
    name, before, after = CLOCK_MUTANTS[mutant]
    case = _FILE["cases"][name]
    assert _answer(case, clock=_Clock(before, after).module) != case["answer"], mutant


def test_the_payer_exclusions_hold_before_1970() -> None:
    """Codex's review of lane J2, item 1: file 20's two exclusion cases moved back 28,000 days
    (4,000 weeks: every weekday, clock and gap kept, every written unit negative). Each answer
    is derived here from the 2024 case's frozen answer, moved back with it, not from the
    oracle; it holds as many values as asked (4 and 5) and is the file's 1947 case's. With -1
    for no unit (e69e534), a negative unit read as none and the two held 5 and 6."""
    shift = 28000 * DAY
    for name in ("field_paid_put_back_avoid", "field_paid_put_back_leaving"):
        frozen = _FILE["cases"][name]
        case = copy.deepcopy(frozen)
        for key in ("ordinals", "lows", "highs"):
            case[key] = [value - shift for value in frozen[key]]
        assert max(case["ordinals"]) < 0, name
        answer = _answer(case)
        assert answer == [value - shift for value in frozen["answer"]], name
        assert len({value // case["written_unit"] for value in answer}) == case["wanted"], name
        assert _FILE["cases"][name + "_1947"]["answer"] == answer, name


# -- by hand -----------------------------------------------------------------------------------


def test_a_sixtieth_second_counts_in_its_written_minute_and_second() -> None:
    """`23:59:60` counts in minute 59 and second 59 of its own minute, never the next."""
    assert calendar_clock.written_minute("2024-01-05 23:59:60") == 59
    assert calendar_clock.written_second("2024-01-05 23:59:60") == 59
    assert calendar_clock.written_second("2024-01-05 23:59:07") == 7


def test_the_tests_of_flat_and_of_the_hour_by_hand() -> None:
    """Flat departs at chi-squared per degree of freedom of four; the hour rule needs
    that and a Cramer's V of 0.2."""
    assert not calendar_clock.departs_from_flat([10] * 60)
    assert calendar_clock.departs_from_flat([100] + [10] * 59)
    night = [hour for hour in range(24) for _copy in range(20)]
    minutes = [0 if (hour >= 19 or hour < 7) else (hour * 7 + copy) % 60 for hour in range(24) for copy in range(20)]
    assert calendar_clock.depends_on_the_hour(night, minutes, LINE)
    even = [(hour * 7 + copy) % 60 for hour in range(24) for copy in range(20)]
    assert not calendar_clock.depends_on_the_hour(night, even, LINE)


def test_the_seconds_kin_keys_each_pair_apart(monkeypatch: pytest.MonkeyPatch) -> None:
    """The second's kin keys hold each pair of hour group and minute group apart
    (the build's defect 4; the lane's skeptic, item 5, found no twin of the
    battery red without it): heaps at minutes 0 and 30 beside a census of
    sixty single minutes make sixty-two minute groups, and keyed by sixty,
    07:30 of one hour group and 08:01 of the next shared a key."""
    hour_where = tuple(0 if hour < 8 else 1 for hour in range(24))
    where, _counts = generation._clock_field_where(
        tuple((value, value, 10) for value in range(60)), ((0, 50), (30, 50)), 800
    )
    assert max(where) + 1 == 62
    pairs = {(hour_where[place // 60], where[place % 60]) for place in range(1440)}
    kin = generation._clock_second_kin(hour_where, where)
    assert kin[7 * 60 + 30] != kin[8 * 60 + 1]
    assert len(set(kin)) == len(pairs)
    bent = _mutant(
        monkeypatch,
        "        hour_where[place // 60] * (max(minute_where) + 1) + minute_where[place % 60]",
        "        hour_where[place // 60] * 60 + minute_where[place % 60]",
    )
    kin = bent._clock_second_kin(hour_where, where)
    assert kin[7 * 60 + 30] == kin[8 * 60 + 1]


def test_a_heap_needs_the_lines_different_values() -> None:
    """A minute standing out over fewer different values than the line is no heap."""
    bins = [2] * 60
    bins[23] = 15
    sure = [0] * 60
    assert calendar_clock.field_heaps(bins, sure, LINE, [15] * 60) == ((23, 15),)
    assert calendar_clock.field_heaps(bins, sure, LINE, [3] * 60) == ()


# -- the work, counted -----------------------------------------------------------------------


def _lines_run(function: "object", *arguments: object) -> int:
    """How many lines `function` and everything it calls ran: a growth measure
    with no clock (`tests/test_stage3b_hour_review.py`'s)."""
    code = function.__code__  # type: ignore[attr-defined]
    ran = [0]
    inside = [False]

    def below(frame: object, event: str, argument: object) -> object:
        if event == "line":
            ran[0] += 1
        return below

    def top(frame: object, event: str, argument: object) -> object:
        if event == "line":
            ran[0] += 1
        elif event == "return":
            inside[0] = False
        return top

    def calls(frame: object, event: str, argument: object) -> object:
        if event != "call":
            return None
        if frame.f_code is code and not inside[0]:  # type: ignore[attr-defined]
            inside[0] = True
            return top
        return below if inside[0] else None

    previous = sys.gettrace()
    sys.settrace(calls)  # type: ignore[arg-type]
    try:
        function(*arguments)  # type: ignore[operator]
    finally:
        sys.settrace(previous)
    return ran[0]


def test_the_producers_tests_grow_with_the_cells() -> None:
    """The flatness test, the hour rule and the heaps, at 20,000 and 200,000 cells:
    the lines run grow no faster than the cells (within 1.25 times), so a million
    cells cost five times 200,000's -- machine-free."""
    spent: "list[int]" = []
    for rows in (20000, 200000):
        draw = random.Random(rows)
        hours = [draw.randrange(24) for _row in range(rows)]
        minutes = [0 if draw.random() < 0.5 else draw.randrange(60) for _row in range(rows)]
        bins = calendar_clock.field_bins(minutes)
        count = _lines_run(calendar_clock.field_bins, minutes)
        count += _lines_run(calendar_clock.depends_on_the_hour, hours, minutes, LINE)
        count += _lines_run(calendar_clock.field_heaps, bins, [0] * 60, LINE, [rows] * 60)
        count += _lines_run(calendar_clock.departs_from_flat, bins)
        spent += [count]
    assert spent[1] <= 1.25 * 10 * spent[0], spent


def _spread_state(days: int):
    """A state of minutes: on each of `days` days, every hour from 1 to 23 holds two
    ranks sharing 00 of its minute 0, one heap group; the count asked is one
    more value a day, which SPREAD finds on the day's hour 0... none, so on the
    next hour of the day with minute 0 free -- none -- and so on: the work
    of a full search, per rank."""
    moved: "list[int]" = []
    for day in range(days):
        for hour in range(1, 24):
            moved += [(19000 + day) * DAY + hour * 3600] * 2
    rows = len(moved)
    where = tuple([1] + [0] * 59)
    state = generation._WeekdayPass(
        moved=moved, held={}, where=where, facts=None, word="", widths=False, kinds={},
        holes=frozenset(), lows=[moved[0]] * rows, highs=[moved[-1] + 3599] * rows, keep_units=True,
        unit=60, step=60, day=DAY, bins="minute", period=60, keeps="hour",
    )
    for ordinal in moved:
        generation._weekday_tally(state.held, ordinal // 60, 1)
    return state, rows


def test_spread_grows_with_the_rows() -> None:
    """SPREAD where nothing can be spread, at 3 and 27 days: the lines grow with the
    rows times the days a search may ask -- the gap's -- and each group, place in
    the day and gap that found nothing is not asked again, so they grow no faster
    than the rows (within 1.25 times nine)."""
    spent: "list[int]" = []
    for days in (3, 27):
        state, rows = _spread_state(days)
        count = generation._weekday_count(state)
        spent += [_lines_run(
            generation._clock_short_spread, state, 0, rows - 1, [False] * rows, count + days,
            tuple(range(7)), True, tuple([0] * 24),
        )]
    assert spent[1] <= 1.25 * 9 * spent[0], spent


def _paid_state(weeks: int, merging: bool):
    """Lane J2: `weeks` weeks of minutes in one gap from a Sunday, a weekday census standing
    (each weekday its own standing), each hour its own kin group, minute 0 the heap's group.
    For SPREAD each Monday's hours 1 to 6 hold two ranks sharing minute 0 and each Sunday's a
    rank alone at minute 40; for PUT BACK each Monday's hours hold a rank alone at minute 20
    and each Sunday's one at 20 and one at 40. No Monday holds a place for them, so each
    takes one on the Sunday before, paid by a Sunday rank moving a whole day onto Monday."""
    moved: "list[int]" = []
    for week in range(weeks):
        sunday = 19729 + 7 * week  # 2024-01-07, a Sunday
        for hour in range(1, 7):
            moved += [sunday * DAY + hour * 3600 + minute * 60 for minute in ((20, 40) if merging else (40,))]
        for hour in range(1, 7):
            moved += [(sunday + 1) * DAY + hour * 3600 + (20 * 60 if merging else 0)] * (1 if merging else 2)
    moved = sorted(moved)
    rows = len(moved)
    state = generation._WeekdayPass(
        moved=moved, held={}, where=tuple([1] + [0] * 59), facts=None, word="", widths=False,
        kinds={}, holes=frozenset(), lows=[moved[0] - 3600] * rows, highs=[moved[-1] + 3600] * rows,
        keep_units=True, unit=60, step=60, day=DAY, bins="minute", period=60, keeps="hour",
        count_steps=False, kin=tuple(range(24)),
    )
    for ordinal in moved:
        generation._weekday_tally(state.held, ordinal // 60, 1)
    return state, rows


def _paid_spread_failing_state(weeks: int):
    """Lane J2's skeptic, item 4: `weeks` weeks in one gap, each Monday's hours 1 to 6 holding
    two ranks sharing minute 0 and no other rank anywhere, so SPREAD PAID BACK finds no payer
    for any of them -- the search that fails, asked once for each group, place and gap."""
    moved: "list[int]" = []
    for week in range(weeks):
        monday = 19730 + 7 * week  # 2024-01-08, a Monday
        for hour in range(1, 7):
            moved += [monday * DAY + hour * 3600] * 2
    moved = sorted(moved)
    rows = len(moved)
    state = generation._WeekdayPass(
        moved=moved, held={}, where=tuple([1] + [0] * 59), facts=None, word="", widths=False,
        kinds={}, holes=frozenset(), lows=[moved[0] - 3600] * rows, highs=[moved[-1] + 3600] * rows,
        keep_units=True, unit=60, step=60, day=DAY, bins="minute", period=60, keeps="hour",
        count_steps=False, kin=tuple(range(24)),
    )
    for ordinal in moved:
        generation._weekday_tally(state.held, ordinal // 60, 1)
    return state, rows


def _substitute_spread_state(days: int):
    """Lane J2: `days` days each its own gap, a weekday census standing, each hour its own kin
    group, minute 0 the heap's group. Each day's hours 1 to 6 hold two ranks sharing minute 0,
    with no other place of the heap's on their hour nor another day in the gap; hours 7 to 12
    each hold one rank alone at minute 30, the rest's group, minute 0 free."""
    moved: "list[int]" = []
    lows: "list[int]" = []
    highs: "list[int]" = []
    for day in range(days):
        start = (19724 + day) * DAY
        cells = [start + hour * 3600 for hour in range(1, 7) for _copy in range(2)]
        cells += [start + hour * 3600 + 30 * 60 for hour in range(7, 13)]
        moved += cells
        lows += [start] * len(cells)
        highs += [start + DAY - 1] * len(cells)
    rows = len(moved)
    state = generation._WeekdayPass(
        moved=moved, held={}, where=tuple([1] + [0] * 59), facts=None, word="", widths=False,
        kinds={}, holes=frozenset(), lows=lows, highs=highs, keep_units=True, unit=60, step=60,
        day=DAY, bins="minute", period=60, keeps="hour", count_steps=False, kin=tuple(range(24)),
    )
    for ordinal in moved:
        generation._weekday_tally(state.held, ordinal // 60, 1)
    return state, rows


def test_spread_by_substitute_grows_with_the_rows() -> None:
    """Lane J2: SPREAD BY SUBSTITUTE at 3 and 27 days, one value put back for each of every day's
    six pairs, a run of the rest taking the heap's free place on its own hour each time: the
    lines run grow no faster than the rows (within 1.25 times nine), every group's count kept and
    the count met -- machine-free. Each pair of groups keeps a cursor past the runs it asked."""
    spent: "list[int]" = []
    for days in (3, 27):
        state, rows = _substitute_spread_state(days)
        count = generation._weekday_count(state)
        groups = collections.Counter((ordinal // 60) % 60 == 0 for ordinal in state.moved)
        spent += [_lines_run(
            generation._clock_spread_substituted, state, 0, rows - 1, [False] * rows, count + 6 * days,
        )]
        assert generation._weekday_count(state) == count + 6 * days, days
        assert collections.Counter((ordinal // 60) % 60 == 0 for ordinal in state.moved) == groups, days
    assert spent[1] <= 1.25 * 9 * spent[0], spent


def test_the_paid_count_steps_grow_with_the_rows() -> None:
    """Lane J2: SPREAD and PUT BACK paid back at 3 and 27 weeks, every Monday rank placed on the
    Sunday before it while a Sunday rank moves onto Monday -- the lines run grow no faster than
    the rows (within 1.25 times nine; measured 9,291 and 85,755 lines for SPREAD's 54 and 486
    ranks, 12,117 and 117,033 for PUT BACK's), so a million ranks cost about two thousand times
    27 weeks', and the count asked is met with every weekday count kept -- machine-free. Each
    step's failed searches are not asked again: without that, PUT BACK's runs on the Sundays
    walked every day of the gap and 27 weeks cost 55 times 3 weeks'."""
    for merging in (False, True):
        spent: "list[int]" = []
        for weeks in (3, 27):
            state, rows = _paid_state(weeks, merging)
            count = generation._weekday_count(state)
            weekdays = collections.Counter((ordinal // DAY + 3) % 7 for ordinal in state.moved)
            wanted = count - 6 * weeks if merging else count + 6 * weeks
            pinned = [False] * rows
            if merging:
                spent += [_lines_run(
                    generation._clock_paid_put_back, state, 0, rows - 1, pinned, wanted, tuple(range(7)),
                )]
            else:
                spent += [_lines_run(
                    generation._clock_paid_spread, state, 0, rows - 1, pinned, wanted, tuple(range(7)),
                )]
            assert generation._weekday_count(state) == wanted, (merging, weeks)
            assert collections.Counter((ordinal // DAY + 3) % 7 for ordinal in state.moved) == weekdays, (merging, weeks)
        assert spent[1] <= 1.25 * 9 * spent[0], (merging, spent)
    # ...AND WHERE SPREAD PAID BACK FINDS NOTHING (lane J2's skeptic, item 4): Monday pairs at
    # minute 0 with no payer anywhere, every search failing. Its failed-search memo keeps the
    # lines linear (measured 10,396 and 82,732); without it they grew 40 times (15,364 and
    # 616,612), and the passing states above never failed a search to show it.
    spent = []
    for weeks in (3, 27):
        state, rows = _paid_spread_failing_state(weeks)
        count = generation._weekday_count(state)
        spent += [_lines_run(
            generation._clock_paid_spread, state, 0, rows - 1, [False] * rows, count + 6 * weeks,
            tuple(range(7)),
        )]
        assert generation._weekday_count(state) == count, weeks
    assert spent[1] <= 1.25 * 9 * spent[0], ("failing", spent)


def _far_state(weeks: int, merging: bool, payers: str, blocked: bool = False):
    """Codex's review of lane J2, item 3: `weeks` Mondays from 2024-01-08 in one gap, each
    weekday its own standing, each hour its own kin group, minute 0 the heap's group. PUT
    BACK (`merging`): each Monday holds one rank alone at 01:20; the last of them a pinned
    01:40, and the Tuesday after it a pinned 01:20, the one unit of another standing each run
    can join, `weeks` days away and more. SPREAD: each Monday holds two ranks at 01:00; the last
    a pinned 01:30. The payers stand at 01:40 (01:30 for SPREAD): `weeks + 1` of them on that
    last Tuesday (`payers` "one"), or one alone on each of the `weeks + 1` Tuesdays after it
    ("each"), every payer far from most runs. Where `blocked` (SPREAD), a pinned rank holds
    01:00 on each Tuesday before the last, so each run's place is far too. Asked: `weeks`
    values fewer (PUT BACK) or more (SPREAD)."""
    first = 19730  # 2024-01-08, a Monday
    last = first + 7 * (weeks - 1)
    cells: "list[tuple[int, bool]]" = []
    clock = 1 * 3600 + (20 if merging else 0) * 60
    pay = 1 * 3600 + (40 if merging else 30) * 60
    for week in range(weeks):
        monday = first + 7 * week
        cells += [(monday * DAY + clock, False)] * (1 if merging else 2)
        if blocked and week < weeks - 1:
            cells += [((monday + 1) * DAY + 3600, True)]
    cells += [(last * DAY + pay, True)]
    if merging:
        cells += [((last + 1) * DAY + clock, True)]
    if payers == "one":
        cells += [((last + 1) * DAY + pay, False)] * (weeks + 1)
    else:
        cells += [((last + 1 + 7 * week) * DAY + pay, False) for week in range(1, weeks + 2)]
    cells = sorted(cells)
    moved = [cell[0] for cell in cells]
    rows = len(moved)
    state = generation._WeekdayPass(
        moved=moved, held={}, where=tuple([1] + [0] * 59), facts=None, word="", widths=False,
        kinds={}, holes=frozenset(), lows=[moved[0] - 3600] * rows, highs=[moved[-1] + 3600] * rows,
        keep_units=True, unit=60, step=60, day=DAY, bins="minute", period=60, keeps="hour",
        count_steps=False, kin=tuple(range(24)),
    )
    for ordinal in moved:
        generation._weekday_tally(state.held, ordinal // 60, 1)
    return state, rows, [cell[1] for cell in cells]


def _far_lines(weeks: int, merging: bool, payers: str, blocked: bool = False) -> int:
    """The lines one far state's paid step runs, its count met and every weekday count kept."""
    state, rows, pinned = _far_state(weeks, merging, payers, blocked)
    count = generation._weekday_count(state)
    weekdays = collections.Counter((ordinal // DAY + 3) % 7 for ordinal in state.moved)
    wanted = count - weeks if merging else count + weeks
    step = generation._clock_paid_put_back if merging else generation._clock_paid_spread
    spent = _lines_run(step, state, 0, rows - 1, pinned, wanted, tuple(range(7)))
    assert generation._weekday_count(state) == wanted, (weeks, merging, payers, blocked)
    assert collections.Counter((ordinal // DAY + 3) % 7 for ordinal in state.moved) == weekdays
    return spent


@pytest.mark.parametrize(
    "merging, payers, blocked",
    [(True, "one", False), (True, "each", False), (False, "one", False), (False, "each", False),
     (False, "each", True)],
)
def test_the_paid_searches_grow_with_the_rows_however_far(merging: bool, payers: str, blocked: bool) -> None:
    """Codex's review of lane J2, item 3: PUT BACK's runs join a unit of another standing
    `weeks` days away and more, and SPREAD's payers -- and, `blocked`, its places -- stand as
    far; every merge and spread succeeds. On e69e534 the day checks grew four times as the rows
    doubled (PUT BACK 1,990 / 8,180 / 33,160 / 133,520 at 43 / 83 / 163 / 323 rows; SPREAD
    3W^2/4 + W occupied-day comparisons). The searches now read only the days of the standing
    they ask that hold a place, a unit to join or a payer not yet spent, each found by halving,
    so doubling the rows at most a little more than doubles the lines run (n log n)."""
    spent = [_far_lines(weeks, merging, payers, blocked) for weeks in (40, 80, 160)]
    assert spent[1] <= 2.4 * spent[0] and spent[2] <= 2.4 * spent[1], spent


def _wall_state(weeks: int, merging: bool):
    """Lane J2's Codex verifier, item 3: `_far_state`'s runs (PUT BACK, `merging`: one rank
    alone at 01:20 each Monday, a pinned final-Monday 01:40 and final-Tuesday 01:20; SPREAD:
    two ranks at 01:00 each Monday, a pinned final-Monday 01:30), and, nearer than every payer
    that keeps the count, a WALL: `weeks` Tuesdays from the last on, each holding a pair at the
    payers' clock (01:40, 01:30 for SPREAD) whose place on the Monday before is free -- a pair's
    rank moving there keeps no count -- then `weeks + 1` Tuesdays each holding one payer alone.
    SPREAD's Mondays after the last hold a pinned 01:00 each. Asked: `weeks` values fewer (PUT
    BACK) or more (SPREAD)."""
    first = 19730  # 2024-01-08, a Monday
    last = first + 7 * (weeks - 1)
    clock = 1 * 3600 + (20 if merging else 0) * 60
    pay = 1 * 3600 + (40 if merging else 30) * 60
    cells: "list[tuple[int, bool]]" = []
    for week in range(weeks):
        cells += [((first + 7 * week) * DAY + clock, False)] * (1 if merging else 2)
    cells += [(last * DAY + pay, True)]
    start = last + 8 if merging else last + 1
    if merging:
        cells += [((last + 1) * DAY + clock, True)]
    for week in range(weeks):
        cells += [((start + 7 * week) * DAY + pay, False)] * 2
    cells += [((start + 7 * (weeks + week)) * DAY + pay, False) for week in range(weeks + 1)]
    if not merging:
        cells += [((last + 7 * week) * DAY + 3600, True) for week in range(1, 2 * weeks + 3)]
    cells = sorted(cells)
    moved = [cell[0] for cell in cells]
    rows = len(moved)
    state = generation._WeekdayPass(
        moved=moved, held={}, where=tuple([1] + [0] * 59), facts=None, word="", widths=False,
        kinds={}, holes=frozenset(), lows=[moved[0] - 3600] * rows, highs=[moved[-1] + 3600] * rows,
        keep_units=True, unit=60, step=60, day=DAY, bins="minute", period=60, keeps="hour",
        count_steps=False, kin=tuple(range(24)),
    )
    for ordinal in moved:
        generation._weekday_tally(state.held, ordinal // 60, 1)
    return state, rows, [cell[1] for cell in cells]


@pytest.mark.parametrize("merging", [True, False])
def test_the_paid_searches_grow_with_the_rows_behind_a_wall(merging: bool) -> None:
    """Lane J2's Codex verifier, item 3: a wall of pairs whose moves keep no count stands
    between the runs and the payers that keep it; every merge and spread succeeds. On cdd3add
    each payer read the wall again -- `_clock_payer_place` asked 23,375 / 93,314 / 374,626
    times (PUT BACK) and 31,001 / 124,501 / 499,001 (SPREAD) at 125 / 250 / 500 weeks, the
    lines run 3.4 to 3.9 times as the rows doubled. Each payer's status is now kept as the
    ranks move and each payer found by halving (`_ClockKeeps`): doubling the rows at most a
    little more than doubles the lines run, the count met and every weekday count kept."""
    spent: "list[int]" = []
    for weeks in (40, 80, 160):
        state, rows, pinned = _wall_state(weeks, merging)
        count = generation._weekday_count(state)
        weekdays = collections.Counter((ordinal // DAY + 3) % 7 for ordinal in state.moved)
        wanted = count - weeks if merging else count + weeks
        step = generation._clock_paid_put_back if merging else generation._clock_paid_spread
        spent += [_lines_run(step, state, 0, rows - 1, pinned, wanted, tuple(range(7)))]
        assert generation._weekday_count(state) == wanted, (weeks, merging)
        assert collections.Counter((ordinal // DAY + 3) % 7 for ordinal in state.moved) == weekdays
    assert spent[1] <= 2.4 * spent[0] and spent[2] <= 2.4 * spent[1], spent


def _substitute_state(days: int):
    """A state of minutes no run of which can join another group: on each of `days`
    days, every hour from 1 to 23 holds one rank alone at minute 30, the rest's
    group, and nothing stands at minute 0; the count asked is one fewer, so
    SUBSTITUTE asks every run and finds nothing -- the full search, per run."""
    moved: "list[int]" = []
    for day in range(days):
        for hour in range(1, 24):
            moved += [(19000 + day) * DAY + hour * 3600 + 30 * 60]
    rows = len(moved)
    state = generation._WeekdayPass(
        moved=moved, held={}, where=tuple([1] + [0] * 59), facts=None, word="", widths=False,
        kinds={}, holes=frozenset(), lows=[moved[0]] * rows, highs=[moved[-1]] * rows,
        keep_units=True, unit=60, step=60, day=DAY, bins="minute", period=60, keeps="hour",
    )
    for ordinal in moved:
        generation._weekday_tally(state.held, ordinal // 60, 1)
    return state, rows


def test_substitute_grows_with_the_rows(monkeypatch: pytest.MonkeyPatch) -> None:
    """SUBSTITUTE where no run can join, at 3 and 27 days: each group, place in the
    day and gap that found nothing is not asked again, so its lines grow no faster
    than the rows (within 1.25 times nine; measured 3.6 times); asking every run
    again, put back by one edit, grows 20 times and is held to show it."""
    uncached = _mutant(
        monkeypatch,
        "        if asked in failed:\n            continue\n        joined = _clock_join_target(",
        "        if False:\n            continue\n        joined = _clock_join_target(",
    )
    grown: "dict[str, float]" = {}
    for name, module in (("shipped", generation), ("uncached", uncached)):
        spent: "list[int]" = []
        for days in (3, 27):
            built, rows = _substitute_state(days)
            state = module._WeekdayPass(**{
                field.name: getattr(built, field.name)
                for field in dataclasses.fields(built)
                if field.name not in ("units_held", "indexes", "gap_sizes")
            })
            count = module._weekday_count(state)
            spent += [_lines_run(
                module._clock_split_substituted, state, 0, rows - 1, [False] * rows, count - 1,
                tuple(range(7)), True, tuple([0] * 24),
            )]
        grown[name] = spent[1] / spent[0]
    assert grown["shipped"] <= 1.25 * 9, grown
    assert grown["uncached"] >= 1.5 * 9, grown


def _kin_state(days: int):
    """A state of minutes for KIN SHARES: on each of `days` days, hours 8 to 16
    hold four ranks each at minutes 7, 22, 37 and 52, the hours each a kin
    group of their own, one gap over every rank; the heap at minute 0 is
    owed a quarter of them, one a day in each hour -- each a move onto a
    place no rank holds, so every one keeps the count."""
    moved: "list[int]" = []
    for day in range(days):
        for hour in range(8, 17):
            moved += [(19000 + day) * DAY + hour * 3600 + minute * 60 for minute in (7, 22, 37, 52)]
    rows = len(moved)
    state = generation._WeekdayPass(
        moved=moved, held={}, where=tuple([1] + [0] * 59), facts=None, word="", widths=False,
        kinds={}, holes=frozenset(), lows=[moved[0] - 3600] * rows, highs=[moved[-1]] * rows,
        keep_units=True, unit=60, step=60, day=DAY, bins="minute", period=60, keeps="hour",
        count_steps=False, kin=tuple(range(24)),
    )
    for ordinal in moved:
        generation._weekday_tally(state.held, ordinal // 60, 1)
    state.gap_sizes[(moved[0] - 3600, moved[-1])] = rows
    heap = rows // 4
    return state, list(range(rows)), [rows - heap, heap]


def test_kin_shares_grow_with_the_rows() -> None:
    """KIN SHARES at 3 and 27 days, 108 and 972 ranks: the shares of each kin
    group and their moves, G7.3f's steps 5 and 6 on its own ranks, grow no
    faster than the rows (within 1.25 times nine), so a million ranks cost a
    thousand times 972's -- machine-free -- and every hour takes its quarter."""
    spent: "list[int]" = []
    for days in (3, 27):
        state, ranks, want = _kin_state(days)
        spent += [_lines_run(generation._clock_kin_shares_moved, state, ranks, want)]
        on_zero = [0 for _hour in range(24)]
        for ordinal in state.moved:
            if (ordinal // 60) % 60 == 0:
                on_zero[(ordinal // 3600) % 24] += 1
        assert on_zero[8:17] == [days] * 9, on_zero
    assert spent[1] <= 1.25 * 9 * spent[0], spent


# -- the Codex review of landing 3b.4 (plan P4-D372) -----------------------------------------


def _repeated_stamps() -> "list[str]":
    """Item 1: 30 days, one stamp an hour, hours before 07 and from 19 on minute
    00, the others at (day index * 12 + hour - 7) % 60, each written 30 times."""
    start = datetime.datetime(2023, 3, 1)
    cells: "list[str]" = []
    for day in range(30):
        for hour in range(24):
            minute = 0 if (hour < 7 or hour >= 19) else (day * 12 + hour - 7) % 60
            moment = start + datetime.timedelta(days=day, hours=hour, minutes=minute)
            cells += [moment.strftime("%Y-%m-%d %H:%M")] * 30
    return cells


def _two_hours() -> "list[str]":
    """Item 2: 30 days, every minute of hour 08 once a day and minutes 00 to 19 of
    hour 20 three times a day, written to the second at second 00: 3,600 rows,
    every minute under a twentieth of the body."""
    start = datetime.datetime(2023, 3, 1)
    cells: "list[str]" = []
    for day in range(30):
        for minute in range(60):
            cells += [(start + datetime.timedelta(days=day, hours=8, minutes=minute)).strftime("%Y-%m-%d %H:%M:%S")]
        for minute in range(20):
            cells += [(start + datetime.timedelta(days=day, hours=20, minutes=minute)).strftime("%Y-%m-%d %H:%M:%S")] * 3
    return cells


def test_m3_keeps_a_complete_dependence_however_often_each_stamp_repeats(tmp_path: pathlib.Path) -> None:
    """The Codex review, item 1: the design effect of the ties divides the
    chi-squared M3 asks, never the strength -- divided, 30 copies of every stamp
    sank a complete dependence of the minute on the hour below 0.2, the minute's
    heap of 10,920 was published and the twin put 5,192 to 5,556 of its 10,800
    daytime cells on minute 0 against 180 real. Withheld, it says why (NF99) and
    the twin keeps its days near 180."""
    cells = _repeated_stamps()
    hours = [int(cell[11:13]) for cell in cells]
    minutes = [int(cell[14:16]) for cell in cells]
    assert calendar_clock.depends_on_the_hour(hours, minutes, LINE, 30 * len(cells))
    described = _one_column(tmp_path, "stamps", cells)
    block = described.block("stamps")
    assert block["minute_heaps"] == [] and block["minute_census"] == []
    said = [note["note"] for note in described.document["publication_notes"] if note["column"] == "stamps"]
    assert taxonomy.rendered(taxonomy.NOTE_MINUTE_WITHHELD_WITH_THE_HOUR, ()) in said
    twin = shapes.cells_of(kpi_shapes.twin_text(described, 0), "stamps")
    days = [cell for cell in twin if 7 <= int(cell[11:13]) < 19]
    assert sum(1 for cell in days if cell[14:16] == "00") < 2 * 180, len(days)


def test_m3_bursts_whose_minute_does_not_follow_the_hour_score_no_strength() -> None:
    """The strength less what the ties give a table with no dependence: bursts of
    one to six check-ins at any minute of any hour score below 0.2 whatever the
    design effect, where 30 copies of night on the hour beside days at any minute
    score near one (`test_m3_keeps_a_complete_dependence_however_often_each_stamp_repeats`)."""
    draw = random.Random(91001)
    hours: "list[int]" = []
    minutes: "list[int]" = []
    squares = 0
    while len(hours) < 1000:
        size = 1 + draw.randrange(6)
        hour, minute = draw.randrange(24), draw.randrange(60)
        hours += [hour] * size
        minutes += [minute] * size
        squares += size * size
    assert not calendar_clock.depends_on_the_hour(hours, minutes, LINE, squares)


def test_m3_sees_dependence_spread_over_minutes_each_under_a_twentieth(tmp_path: pathlib.Path) -> None:
    """The Codex review, item 2: M3's columns are the field's groups by the one
    merge rule on the line, as its rows are the hour's. Pooled under a twentieth of
    the body, every minute of 3,600 rows fell in one column, both questions said
    no, 60 minute groups were published and the twin put 1,209 of its 1,800 morning
    cells on minutes 00 to 19 against 600 real (583 on 2341173). Now withheld,
    said why, and the twin's mornings stand near 600."""
    cells = _two_hours()
    described = _one_column(tmp_path, "rounds", cells)
    block = described.block("rounds")
    assert block["minute_heaps"] == [] and block["minute_census"] == []
    said = [note["note"] for note in described.document["publication_notes"] if note["column"] == "rounds"]
    assert taxonomy.rendered(taxonomy.NOTE_MINUTE_WITHHELD_WITH_THE_HOUR, ()) in said
    twin = shapes.cells_of(kpi_shapes.twin_text(described, 0), "rounds")
    mornings = [cell for cell in twin if cell[11:13] == "08"]
    early = sum(1 for cell in mornings if int(cell[14:16]) < 20)
    assert abs(early - len(mornings) / 3) < 100, (early, len(mornings))


def _hourly(night_copies: int, day_copies: int, burst: int) -> "list[str]":
    """The verifier's item 8: item 1's 30 days, night stamps written
    `night_copies` times and day stamps `day_copies` times, and one stamp at
    14:37 on day 15 written `burst` times."""
    start = datetime.datetime(2023, 3, 1)
    cells: "list[str]" = []
    for day in range(30):
        for hour in range(24):
            night = hour < 7 or hour >= 19
            minute = 0 if night else (day * 12 + hour - 7) % 60
            moment = start + datetime.timedelta(days=day, hours=hour, minutes=minute)
            cells += [moment.strftime("%Y-%m-%d %H:%M")] * (night_copies if night else day_copies)
    cells += [(start + datetime.timedelta(days=15, hours=14, minutes=37)).strftime("%Y-%m-%d %H:%M")] * burst
    return cells


def _events_of(cells: "list[str]") -> "tuple[list[int], list[int], list[bool]]":
    """The cells' hours, minutes and marks as the first of their written value,
    in written order -- as the producer hands them to M3."""
    ordered = sorted(cells)
    starts = [place == 0 or ordered[place] != ordered[place - 1] for place in range(len(ordered))]
    return [int(cell[11:13]) for cell in ordered], [int(cell[14:16]) for cell in ordered], starts


@pytest.mark.parametrize(
    ("night_copies", "day_copies", "burst", "real", "bound"),
    [(1, 1, 100, 6, 30), (1, 30, 0, 180, 360)],
    ids=["one_burst", "days_in_panels"],
)
def test_m3_counts_each_written_value_once(
    tmp_path: pathlib.Path, night_copies: int, day_copies: int, burst: int, real: int, bound: int
) -> None:
    """The verifier's item 8 on the Codex round: M3's table counts events, each
    different written value once, in the rows and columns the cells draw. One
    global design effect over uneven ties sank a strong dependence -- one stamp
    written 100 times among 720 (design effect 13.07) and day stamps written 30
    times beside night stamps once -- the minute's facts were published and the
    twin put 205 of 459, and 436 of 10,792, daytime cells on minute 0 against 6
    and 180 real. Now withheld, said why, the twin's days near the real."""
    cells = _hourly(night_copies, day_copies, burst)
    described = _one_column(tmp_path, "stamps", cells)
    block = described.block("stamps")
    assert block["minute_heaps"] == [] and block["minute_census"] == []
    said = [note["note"] for note in described.document["publication_notes"] if note["column"] == "stamps"]
    assert taxonomy.rendered(taxonomy.NOTE_MINUTE_WITHHELD_WITH_THE_HOUR, ()) in said
    days = [cell for cell in cells if 7 <= int(cell[11:13]) < 19]
    assert sum(1 for cell in days if cell[14:16] == "00") == real
    twin = shapes.cells_of(kpi_shapes.twin_text(described, 0), "stamps")
    days = [cell for cell in twin if 7 <= int(cell[11:13]) < 19]
    assert sum(1 for cell in days if cell[14:16] == "00") < bound, len(days)


def test_m3_calls_no_burst_among_independent_minutes_a_dependence() -> None:
    """Counted by event, one stamp written 1,000 times among a year of stamps
    at any minute is one event: no table says the minute follows the hour (each
    hour group divided by its own design effect, the rest of the hours' cells
    against the burst's column still scored 36.3 and 0.54)."""
    draw = random.Random(1)
    start = datetime.datetime(2023, 3, 1)
    cells: "list[str]" = []
    for day in range(365):
        for hour in range(24):
            cells += [(start + datetime.timedelta(days=day, hours=hour, minutes=draw.randrange(60))).strftime("%Y-%m-%d %H:%M")]
    cells += [(start + datetime.timedelta(days=182, hours=14, minutes=37)).strftime("%Y-%m-%d %H:%M")] * 1000
    hours, minutes, starts = _events_of(cells)
    for fine in (False, True):
        assert not calendar_clock.depends_on_the_hour(hours, minutes, LINE, 0, fine, starts), fine
    hours, minutes, starts = _events_of(_hourly(1, 1, 1000))
    assert calendar_clock.depends_on_the_hour(hours, minutes, LINE, 0, False, starts)


def _rounds(noise: int) -> "list[str]":
    """The verifier's item 9: item 2's rounds, hour 20's at seconds 00, 20 and 40,
    beside `noise` cells at any minute of twelve other hours, 30 days."""
    draw = random.Random(5)
    start = datetime.datetime(2023, 3, 1)
    cells: "list[str]" = []
    for day in range(30):
        for minute in range(60):
            cells += [(start + datetime.timedelta(days=day, hours=8, minutes=minute)).strftime("%Y-%m-%d %H:%M:%S")]
        for minute in range(20):
            for second in (0, 20, 40):
                moment = start + datetime.timedelta(days=day, hours=20, minutes=minute, seconds=second)
                cells += [moment.strftime("%Y-%m-%d %H:%M:%S")]
    for _cell in range(noise):
        moment = start + datetime.timedelta(
            days=draw.randrange(30),
            hours=draw.choice((1, 2, 3, 4, 5, 11, 12, 13, 14, 15, 16, 17)),
            minutes=draw.randrange(60),
            seconds=draw.randrange(60),
        )
        cells += [moment.strftime("%Y-%m-%d %H:%M:%S")]
    return cells


def test_m3_reads_each_hour_group_against_the_rest(tmp_path: pathlib.Path) -> None:
    """The verifier's item 9 on the Codex round: over fourteen hour groups and
    sixty minute groups the whole table's strength fell under the bar -- one less
    than its shorter side, 13, divides it -- 60 minute groups were published and
    the twin put 828 of its 1,800 cells of hour 08 on minutes 00 to 19 against
    600 real. M3 also asks each hour group against the rest of the body, test and
    strength: withheld, said why, the twin's hour 08 near 600."""
    cells = _rounds(6000)
    described = _one_column(tmp_path, "rounds", cells)
    block = described.block("rounds")
    assert block["minute_heaps"] == [] and block["minute_census"] == []
    said = [note["note"] for note in described.document["publication_notes"] if note["column"] == "rounds"]
    assert taxonomy.rendered(taxonomy.NOTE_MINUTE_WITHHELD_WITH_THE_HOUR, ()) in said
    twin = shapes.cells_of(kpi_shapes.twin_text(described, 0), "rounds")
    mornings = [cell for cell in twin if cell[11:13] == "08"]
    early = sum(1 for cell in mornings if int(cell[14:16]) < 20)
    assert abs(early - len(mornings) / 3) < 100, (early, len(mornings))


def test_the_heap_remark_names_its_sure_cell_remainder(tmp_path: pathlib.Path) -> None:
    """The Codex review, item 7: 1,000 dates from 2023-01-01 at 09:30:00, day
    indexes 11 to 21 at 09:00:00, at floor 11 -- the 11 values on minute 0 stand
    out at the line's values and rows, but the low boundary is a sure cell of
    theirs, leaving 10, so the producer withholds that heap and publishes minute
    30 alone; the remark (NF93, and NF94 in the same words) says a value counted
    alone also holds, besides its sure cells, nought or at least the line."""
    start = datetime.datetime(2023, 1, 1, 9, 30)
    cells = [
        (start + datetime.timedelta(days=day, minutes=-30 if 11 <= day <= 21 else 0)).strftime("%Y-%m-%d %H:%M:%S")
        for day in range(1000)
    ]
    described = _one_column(tmp_path, "visits", cells)
    assert [heap["value"] for heap in described.block("visits")["minute_heaps"]] == [30]
    for form in (taxonomy.REMARK_MINUTE_CENSUS, taxonomy.REMARK_SECOND_CENSUS):
        remark = taxonomy.rendered(form, (LINE,))
        assert (
            "at least three times the median of the five on either side of it and, besides the rows "
            "the rest of this description places there for certain, nought or at least 11 rows is "
            "counted alone"
        ) in remark, form


def _burst_state(module, size: int):
    """The Codex review, item 5: `size` movable ranks sharing 08:30, one written
    unit, in a gap of 08:00 to 08:59, minute 0 owed half of them -- the unit may
    not move whole, and every one of its ranks asks."""
    at = 19000 * DAY + 8 * 3600
    moved = [at + 30 * 60] * size
    state = module._WeekdayPass(
        moved=moved, held={}, where=tuple([1] + [0] * 59), facts=None, word="", widths=False,
        kinds={}, holes=frozenset(), lows=[at] * size, highs=[at + 59 * 60] * size,
        keep_units=True, unit=60, step=60, day=DAY, bins="minute", period=60, keeps="hour",
        count_steps=False, whole_units=True,
    )
    for ordinal in moved:
        module._weekday_tally(state.held, ordinal // 60, 1)
    return state, list(range(size)), [size, 0], [size - size // 2, size // 2]


def test_a_shared_unit_is_judged_once_a_round() -> None:
    """The Codex review, item 5: a burst of 100, 200 and 400 ranks on one written
    unit, which may not move whole -- each rank asked the whole unit's move and
    walked all its members (21,000, 82,000 and 324,000 lines; a 10,000-row burst in
    a million rows, some 100 million checks a round). A unit is judged once for
    each place it is offered in a round, so the lines grow no faster than the
    ranks (within 1.25 times four from 100 to 400; 707cf99 ran 294,944, 669,844
    and 1,659,644, 5.6 times), and nothing moves."""
    spent: "list[int]" = []
    for size in (100, 200, 400):
        state, ranks, have, want = _burst_state(generation, size)
        spent += [_lines_run(
            generation._weekday_singles_moved, state, ranks, have, want,
            generation._WEEKDAY_SINGLE_ROUNDS, False,
        )]
        assert state.moved == [19000 * DAY + 8 * 3600 + 30 * 60] * size
    assert spent[2] <= 1.25 * 4 * spent[0], spent


def _room_state(tails: int):
    """The Codex review, item 6: `tails` tail ranks at midnight on days of their own,
    each free to step a minute off, then as many body ranks at 00:01 of later
    days, each owed its day's midnight by a heap at minute 0 alone."""
    moved = [(18000 + day) * DAY for day in range(tails)]
    moved += [(19000 + day) * DAY + 60 for day in range(tails)]
    rows = len(moved)
    lows = [ordinal - 3600 for ordinal in moved[:tails]] + [ordinal - 60 for ordinal in moved[tails:]]
    highs = [ordinal + 3600 for ordinal in moved[:tails]] + [ordinal + 3540 for ordinal in moved[tails:]]
    state = generation._WeekdayPass(
        moved=moved, held={}, where=tuple([1] + [0] * 59), facts=None, word="", widths=False,
        kinds={}, holes=frozenset(), lows=lows, highs=highs, keep_units=True, unit=60, step=60,
        day=DAY, bins="minute", period=60, keeps="hour", count_steps=False, no_midnight=True,
    )
    for ordinal in moved:
        generation._weekday_tally(state.held, ordinal // 60, 1)
    return state, rows


def test_midnight_room_grows_with_the_rows() -> None:
    """The Codex review, item 6: 200, 400 and 800 tails stepping off midnight for as
    many body ranks -- each body rank's search started at the first tail and walked
    every one taken (t(t+1)/2 checks, 50,005,000 at a million rows). It starts past
    the tails taken, so the lines grow no faster than the ranks (within 1.25 times
    four from 200 to 800), and every body rank takes its midnight."""
    spent: "list[int]" = []
    for tails in (200, 800):
        state, rows = _room_state(tails)
        spent += [_lines_run(
            generation._clock_midnight_room_made, state, [0, tails], tails, rows - 1,
            [False] * rows, [False] * rows, 60, 60,
        )]
        assert all(ordinal % DAY == 0 for ordinal in state.moved[tails:]), tails
        assert all(ordinal % DAY == 60 for ordinal in state.moved[:tails]), tails
    assert spent[1] <= 1.25 * 4 * spent[0], spent


def test_a_tail_end_leaves_the_body_its_cells_at_midnight(tmp_path: pathlib.Path) -> None:
    """The Codex review, item 4: a column on the hour at 1,000 rows and floor 11
    owes 11 cells at midnight, and its body holds all of them for certain -- hour 0 counts
    11 alone, minute 0 the whole body of 978, every cell on second 0 -- while its
    high tail's END was derived at 2024-12-31 00:00 and pinned: room-making left a
    body cell at 00:01 and the heap at minute 0 came back 977 at seeds 0 to 4. The
    END now steps a unit inward off a midnight the count leaves it none of, as off
    a hole, and the checker's window reads it so: 978 on minute 0, 11 at midnight,
    nothing missed."""
    cells = shapes.on_the_hour(random.Random(42), 1000)
    described = _one_column(tmp_path, "hours", cells)
    block = described.block("hours")
    body = len(cells) - block["low_tail"]["rows"] - block["high_tail"]["rows"]
    assert block["minute_heaps"] == [{"value": 0, "count": body}] and block["n_at_midnight"] == 11
    for seed in range(5):
        written = kpi_shapes.twin_text(described, seed)
        assert kpi_shapes.missed(kpi_shapes.measure(described, written, f"t{seed}.csv")) == [], seed
        twin = sorted(shapes.cells_of(written, "hours"))
        inside = twin[block["low_tail"]["rows"] : len(twin) - block["high_tail"]["rows"]]
        assert sum(1 for cell in inside if cell[14:16] == "00") == body, seed
        assert sum(1 for cell in twin if cell[11:16] == "00:00") == 11, seed
    assert calendar_clock.body_sure_at_midnight(
        [(group["first"], group["last"], group["count"]) for group in block["hour_census"]],
        ((), ((0, body),)), ((), ()), "minute", body,
    ) == 11


def test_the_body_sure_at_midnight_by_hand() -> None:
    """`calendar_clock.body_sure_at_midnight`: hour 0's count alone less the body's
    cells off minute 0 and off second 0, never below nought; nought where hour 0 is
    grouped or the column is written finer than the second."""
    hours = [(0, 0, 11), (1, 23, 989)]
    assert calendar_clock.body_sure_at_midnight(hours, ((), ((0, 1000),)), ((), ()), "minute", 1000) == 11
    assert calendar_clock.body_sure_at_midnight(hours, ((), ((0, 995),)), ((), ()), "minute", 1000) == 6
    assert calendar_clock.body_sure_at_midnight(hours, (((0, 0, 995), (1, 59, 5)), ()), ((), ((0, 998),)), "second", 1000) == 4
    assert calendar_clock.body_sure_at_midnight(hours, ((), ((0, 980),)), ((), ()), "minute", 1000) == 0
    assert calendar_clock.body_sure_at_midnight([(0, 1, 30), (2, 23, 970)], ((), ((0, 1000),)), ((), ()), "minute", 1000) == 0
    assert calendar_clock.body_sure_at_midnight(hours, ((), ((0, 1000),)), ((), ((0, 1000),)), "subsecond", 1000) == 0
