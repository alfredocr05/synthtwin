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
    3,000 and 5,000 rows without it, short at 8,000 at seeds 0 and 1)."""
    described = _one_column(tmp_path, "clinic", shapes.clinic(random.Random(72012), 8000))
    written = kpi_shapes.twin_text(described, 0)
    assert kpi_shapes.missed(kpi_shapes.measure(described, written, "t.csv")) == []
    monkeypatch.setattr(generation, "_clock_short_spread", lambda *_args, **_named: None)
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


# What 2341173 missed on the small bursty tables of the lane's skeptic (item 3):
# the ceiling, by rows and seed.
SMALL_BURSTS_CEILING = {(300, 2): ["bursts:distinct.n_distinct", "bursts:distinct.n_distinct_folded"]}


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
        written = kpi_shapes.twin_text(described, seed)
        twin = _field_counts(shapes.cells_of(written, "bursts"), shapes.US, "minute")
        assert max(twin[value] for value in range(60) if value not in heaps) <= 3 * busiest, seed
        assert kpi_shapes.missed(kpi_shapes.measure(described, written, f"t{seed}.csv")) == [], seed


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
    if step == "midnight_count":
        moved = list(case["ordinals"])
        first, last = case["body"]
        module._clock_midnight_count_kept(
            case["counted"], moved, list(case["pinned"]), first, last, case["written_unit"],
            case["away"], list(case["lows"]), list(case["highs"]),
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
    elif step == "room":
        module._clock_midnight_room_made(
            state, list(case["counts"]), first, last, pinned, list(case["tail_pins"]),
            case["written_unit"], case["away"],
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
        "            target = _clock_escape(\n                state, here, low, high, 1, have, want, standing, anyday, kin\n            )",
        "            target = None",
    ),
    "the tails keep no count at midnight": (
        "field_midnight_tails",
        "        if at > counted and here:\n            if moved[rank] + away <= gap_highs[rank]:",
        "        if False:\n            if moved[rank] + away <= gap_highs[rank]:",
    ),
    "a gap's shares not split over its kin groups": (
        "field_kin_shares",
        "        if state.kin and _clock_kin_shares_moved(state, ranks, want):",
        "        if False and _clock_kin_shares_moved(state, ranks, want):",
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
    "no PUT BACK after the exchange": (
        "field_exchange_put_back",
        "    for last_resort in (False, True):\n        if state.keep_units and _weekday_count(state) > wanted and",
        "    for last_resort in ():\n        if state.keep_units and _weekday_count(state) > wanted and",
    ),
    "the tails make no room at midnight": (
        "field_midnight_room",
        "    if not state.no_midnight or state.where.count(state.where[0]) != 1:\n        return\n    zero = state.where[0]\n    found = _clock_found(",
        "    if True:\n        return\n    zero = state.where[0]\n    found = _clock_found(",
    ),
    "a narrow stratum keeps its midnight": (
        "field_midnight_narrow",
        "            elif moved[rank] + step <= gap_highs[rank]:\n                # A STRATUM",
        "            elif False:\n                # A STRATUM",
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
        "    if state.no_midnight and state.where.count(state.where[0]) == 1:\n        zero = state.where[0]",
        "    if False:\n        zero = state.where[0]",
    ),
    "the ranks free to take value 0 not counted": (
        "field_midnight_share",
        "                    if not _written_at_midnight(\n",
        "                    if False and not _written_at_midnight(\n",
    ),
    "a draw laid on no unit": (
        "field_floor",
        "    floored = value - value % unit\n    if floored >= low:\n        return floored",
        "    floored = value\n    if floored >= low:\n        return floored",
    ),
}

CLOCK_MUTANTS = {
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
