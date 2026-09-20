"""Three- and four-number cells keep their pairs (ledger K-P4-06).

THE DRIFT. The record of landing L7's review round 3 (plan, and the
changelog's forty-seed paragraph) measured this battery at 550 of 2,160
pair agreements outside G12.9's window and 0 of 2,160 above-counts
missed. The merged tree of stage 2b gave 597 and 7. Bisected with the
battery over every first-parent commit from the round to e53d5f4, one
harness, forty seeds:

- `554da75` (round 3, the recorded tree): 550 and 0;
- `da73c1c` (round 4 of L7, still Phase 4): 550 and 1 -- the anti-lockout
  turn of the proposal (A-P4-52), whose one miss is battery column 0 at
  seed 4, pair (2, 4), 111 rows against 110, and is still there today;
- `8a59eee` (Phase 4 closed): 554 and 1;
- `d14969c` (landing 2b.1): 562 and 1;
- `f545bf1` (first commit of carried-fix-numbers): 615 and 6 -- plan
  P4-D147, the fill of a saturated integer grid;
- `b93b285` (G6.5a reconciled): 597 and 7, which is e53d5f4;
- `91f3586` (the carried-f-numbers merge, at the integration of the gap
  passes on 2026-09-19): 609 and 3. Withdrawing one rule at a time on the
  merged tree: without G6.5a's push of a collision along its band, 594
  and 7; without the band fill, 603 and 3; without the mode pass, 609
  and 3. The push trades twelve agreements for four above-counts, all in
  column 9 (110 and 6 to 117 and 0) and column 11 (68 and 0 to 63 and 2).

THE CEILING, ACCEPTED BY THE ORCHESTRATOR 2026-09-19 (not an owner
ruling; the owner may reverse it): the carried-f-numbers push (G6.5a)
repairs a twin that missed its own distinct-value count on a nearly full
band, and on this battery it trades 12 more agreements outside the 0.02
window (597 to 609 of 2,160) for 4 fewer missed rows-above counts (7 to
3). The ceiling is 609 and 3 from here; the target stays 550 and 0 (the
pairing walk, stage 6). Ceilings move in their own commit, never inside
a merge.

WHY THE FILL STAYS. P4-D147 gives stratum `k` the `k`-th integer
whatever integer the ladder put it at, so a column on a saturated grid
holds every number it publishes -- and the plan holds a joined position
to that count exactly (`tests/test_p2c4f1_disposition_registry.py`).
Inside a joined position the fill moves a run of strata one integer off
the ladder, and that moves which rows stand above another position's
numbers. Three other rules were measured against it on this battery:

- the walk alone inside positions: 546 outside and 1 missed, by leaving
  185 more position runs of 1,680 short of their published count;
- the walk, then the points it left empty each taken by the doubled
  stratum of least size times distance: 604 and 1. It was withdrawn in
  review: on a length-of-stay column it moved a large low stratum onto
  an empty point far out in the tail -- the first position's spread 11.6
  where the real one is 7.4, its ninetieth percentile 30 where the real
  one is 16 -- and on a repeated-reading column (`a/a/c/50 - a`) it
  missed a published above-count of 0 in 7 runs of 40;
- that rule held to moves no costlier than the fill in order, or an
  order-keeping cascade toward each empty point: the marginals return,
  and 5 or all 6 of the recovered above-counts are lost again.

So the six above-counts are bought only by long moves that break the
marginals, and the trade -- agreement windows and above-counts against
the positions' shape -- is the owner's decision, not a repair. The open
cause is G6B.4's pairing walk, which cannot trade a few order breaks
for an exact above-count.

WHERE THE BATTERY IS MEASURED, AND WHAT IS PINNED HERE. The whole
battery -- twelve columns, forty seeds, 2,160 pairs -- is the SLOW
driver `tools/measurements/kpi_joined_battery.py`, which the ledger
names as K-P4-06's source and which reads the L7 driver's own printed
totals. This file pins THREE of those columns, serially, and the two
shapes the withdrawn rule broke. The pin's own figures, what it still
catches and what it does not are stated on the test below.
"""

from __future__ import annotations

import pathlib
import random

import fixtures
import joined_battery
import kpi_rules
from synthtwin import contract, generation
from tests.test_stage2_round_trip import _round_trip

# THE CEILINGS: the ledger's own rule for K-P4-06, "no worse than the
# figures measured on the tree it stands on". They were e53d5f4's 597
# outside and 7 missed; the integrated tree of 2026-09-19 measures 609
# and 3, moved by G6.5a's push, and the orchestrator accepted that trade
# on 2026-09-19 (THE CEILING, above) -- the missed count tightened with
# it. The recorded 550 and 0 are the target and are not met.
#
# THE WHOLE BATTERY IS THE DRIVER'S, NOT THIS FILE'S (below), so these
# three numbers are READ FROM THE LEDGER and not restated here. They
# were restated, as three literals no code read, under a comment saying
# the pin below was derived from them -- a count written in two places
# with nothing holding the two equal, which is the way this repository
# has drifted before (finding 6 of this landing's review). The pin is
# derived from them in
# `test_the_pin_is_derived_from_the_whole_batterys_ceiling` below, which
# is what makes a moved ceiling re-derive the pin instead of leaving
# these stale.
BATTERY = kpi_rules.entries_by_id(kpi_rules.load_ledger())["K-P4-06"]
OUTSIDE_CEILING = BATTERY["expected"]["agreements_outside"]
MISSED_CEILING = BATTERY["expected"]["above_counts_missed"]
PAIRS = BATTERY["value_at"]["value"]["pairs"]

# THE PIN THIS FILE KEEPS, and the three columns it is taken over.
# Measured on the tree of this commit, one column at a time, forty seeds
# each (`(pairs, outside, missed)` per column, 94.6 s for all twelve):
#
#     0: 120  14  1     4: 120  40  0     8: 120  39  0
#     1: 240  40  0     5: 240  38  0     9: 240 117  0
#     2: 120  40  0     6: 120  37  0    10: 120  33  0
#     3: 240  51  0     7: 240  97  0    11: 240  63  2
#
# Columns 0, 9 and 11 are the pin: 0 is a three-position column and 9
# and 11 are four-position ones, they hold ALL THREE of the battery's
# missed above-counts (1 in column 0, 2 in column 11), and 9 and 11 are
# the two columns G6.5a's push moved (9 from 110 and 6 to 117 and 0, 11
# from 68 and 0 to 63 and 2). Withdrawing that push therefore turns this
# pin red on the missed count -- 6 in column 9 against its ceiling of 0
# -- which is the regression the whole battery reports as 7 missed.
# 24.6 s of the battery's 94.6.
PINNED_COLUMNS = (0, 9, 11)
PINNED_CEILINGS = {
    # column: (pairs, agreements outside the window, above-counts missed)
    0: (120, 14, 1),
    9: (240, 117, 0),
    11: (240, 63, 2),
}

# Battery column 9 and the seed its witness is taken at.
FOURTH_COLUMN = 9
COUNT_SEED = 7


def _column_nine(folder: pathlib.Path) -> "tuple[contract.Profile, contract.JoinedFacts]":
    rows = joined_battery.battery_rows()[FOURTH_COLUMN]
    loaded = joined_battery.described(rows, folder)
    facts = loaded.columns[0].facts
    assert isinstance(facts, contract.JoinedFacts), loaded.columns[0].role
    assert facts.n_parts == 4, facts.n_parts
    return loaded, facts


def _stay_cells() -> "list[str]":
    """Length of stay over days in intensive care: 845 cells.

    800 stays drawn with `random.Random(11)` -- the stay one plus an
    exponential of rate 0.18 capped at 45 days, the intensive-care days
    an exponential of rate 0.35 capped at the stay -- and one stay of
    each length from 1 to 45 with no intensive-care day, so the first
    position is a saturated integer grid of 45 points, crowded at its
    low end and thin in its tail.
    """
    draw = random.Random(11)
    cells: "list[str]" = []
    for _ in range(800):
        stay = min(45, 1 + int(draw.expovariate(0.18)))
        care = max(0, min(stay, int(draw.expovariate(0.35))))
        cells += [f"{stay}/{care}"]
    for stay in range(1, 46):
        cells += [f"{stay}/0"]
    return cells


def _repeated_cells() -> "list[str]":
    """A reading taken twice, beside two others: 300 cells `a/a/c/50 - a`.

    Drawn with `random.Random(99)`, `a` from 5 to 35 and `c` from 1 to
    20. The first two positions are equal on every row, so the
    description publishes 0 rows holding the first above the second.
    """
    draw = random.Random(99)
    cells: "list[str]" = []
    for _ in range(300):
        first = draw.randint(5, 35)
        third = draw.randint(1, 20)
        cells += [f"{first}/{first}/{third}/{50 - first}"]
    return cells


def _spread_and_tail(numbers: "list[float]") -> "tuple[float, float]":
    """The population spread and the ninetieth percentile, nearest rank."""
    mean = sum(numbers) / len(numbers)
    total = 0.0
    for number in numbers:
        total = total + (number - mean) ** 2
    ordered = sorted(numbers)
    return (total / len(numbers)) ** 0.5, ordered[int(0.9 * len(ordered))]


def test_a_saturated_position_holds_every_number_it_publishes(
    tmp_path: pathlib.Path,
) -> None:
    """Battery column 9 at seed 7: positions 1 and 4 hold 51 of 51.

    Both are saturated integer grids -- 51 different numbers from 10 to
    60, and from 40 to 90, the fourth being `100 - first` -- and the
    count is the exact fact the fill exists for. It is why the walk
    alone, which reaches 546 agreements outside on the battery, is not
    taken.

    MUTATION, RE-MEASURED 2026-09-20 (finding 1 of this landing's
    review), because the line here was stale: withdrawing the fill does
    NOT move this any more. `_saturated_integers` answering nothing
    holds 51 and 51 -- so do `_saturated_levels` (P4-D178) and
    `_saturated_bands` withdrawn beside it, all three together, and the
    separation walk itself withdrawn as well. The fill is reached on
    this column (instrumented: four calls, two of them answering, at
    this seed) and the count no longer depends on it: the walk of
    A-P4-55 runs three rounds and reaches 51 on its own, where the tree
    that recorded "50 and 49" walked once.

    So what this test pins is the COUNT, not the statement that reaches
    it, and no mutation tried here turns it red. The fill's own guard is
    `tests/test_carried_numbers.py::test_the_column_wide_fill_holds_a_point_free_grid_alone`
    (four parametrised seeds red under exactly that mutation) and
    `test_the_column_wide_fill_is_what_holds_it` beside it.
    """
    loaded, facts = _column_nine(tmp_path)
    twin = generation.generate(loaded, COUNT_SEED)
    held = joined_battery.position_numbers(list(twin.columns[0]), facts)
    counts = [
        (place, len(set(held[place])), facts.parts[place].n_distinct_values)
        for place in (0, 3)
    ]
    assert [count[2] for count in counts] == [51, 51], counts
    assert all(count[1] == count[2] for count in counts), (
        f"(position, held, published) at seed {COUNT_SEED}: {counts}"
    )


def test_the_battery_of_three_and_four_positions_keeps_its_figures() -> None:
    """Three battery columns, forty seeds, 600 pairs: each at its own ceiling.

    WHY THREE COLUMNS AND NOT TWELVE. This test ran all twelve over a
    `concurrent.futures.ProcessPoolExecutor`, and the suite is
    NETWORK-DEAD by design: the pool's own machinery takes a socket, the
    conftest guard fires on it, and every test cell of the first CI run
    failed here with `_GuardError`. No test may open a process pool, a
    thread pool that takes a socket, or any socket at all, so the choice
    was between running the twelve serially in the suite and keeping a
    smaller pin here. MEASURED on this tree, one column at a time:
    94.6 s for all twelve, 24.6 s for these three. The whole battery is
    already measured, unchanged, by `tools/measurements/kpi_joined_battery.py`
    -- the SLOW driver the ledger names as K-P4-06's source, which reads
    the L7 driver's own printed totals -- so running all twelve here
    bought no measurement the ledger does not already have, at 70 s a
    suite run on a suite that already costs hours.

    WHAT THIS PIN STILL CATCHES, exactly. The three columns hold all
    three of the battery's missed above-counts and 194 of its 609
    agreements outside the window, and two of them are the two the
    accepted trade moved. Two mechanisms were measured against it, and
    only the first of them is this test's to catch:

    * MUTATION, measured on this tree: with `_pushed_apart` returning
      its arguments unchanged -- G6.5a's push of a collision along its
      band withdrawn, and nothing else -- column 0 reads 11 and 1,
      column 9 reads 110 and SIX missed against its ceiling of 0, and
      column 11 reads 68 and 0. This test goes red on column 9, and the
      figures are the ones the bisect recorded for the whole battery
      (7 missed against the ceiling of 3);
    * MUTATION, the other mechanism: `_saturated_integers` answering
      nothing -- the column-wide fill of P4-D147 withdrawn -- leaves
      these three columns at 14/1, 117/0 and 63/2 UNCHANGED, and so does
      withdrawing `_saturated_levels` (P4-D178) and `_saturated_bands`
      beside it. The fill is pinned, and not here: under that same
      mutation
      `tests/test_carried_numbers.py::test_the_column_wide_fill_holds_a_point_free_grid_alone`
      fails on all four of its parametrised seeds, and
      `test_the_column_wide_fill_is_what_holds_it` beside it withdraws
      the fill itself and holds 33 numbers against 34. This bullet named
      `test_a_saturated_position_holds_every_number_it_publishes` above,
      which does NOT go red: see its own docstring for the measurement,
      and the review's finding 1 for how it was found.

    WHAT IT DOES NOT CATCH: a regression confined to one of the other
    nine columns -- in EITHER of the battery's numbers, its agreements
    outside the window or its above-counts missed. All three of today's
    missed above-counts sit in pinned columns, but that is a property of
    today's measurement and not of the pin: six missed counts appearing
    in column 3 or column 7 would be green here and green in CI. That is
    the driver's to report, and the ledger's rule for K-P4-06 is measured
    there.
    """
    kpi_rules.guard_this_tree()
    measured = {
        case: joined_battery.one_column(case) for case in PINNED_COLUMNS
    }
    assert {case: count[0] for case, count in measured.items()} == {
        case: ceiling[0] for case, ceiling in PINNED_CEILINGS.items()
    }, measured
    worse = [
        f"column {case}: {measured[case][1]} outside and {measured[case][2]} missed, "
        f"against the ceiling {PINNED_CEILINGS[case][1]} and {PINNED_CEILINGS[case][2]}"
        for case in PINNED_COLUMNS
        if measured[case][1] > PINNED_CEILINGS[case][1]
        or measured[case][2] > PINNED_CEILINGS[case][2]
    ]
    assert not worse, "; ".join(worse)


def test_the_pin_is_derived_from_the_whole_batterys_ceiling() -> None:
    """The three pinned columns against K-P4-06's own numbers, arithmetic and all.

    THE CEILINGS WERE THREE LITERALS NO CODE READ, under a comment
    saying the pin was derived from them (finding 6 of this landing's
    review): when the driver's ceiling next moved they would have gone
    stale in silence, and the promised derivation had nothing behind it.
    They are read from the ledger now, and the derivation is asserted
    here:

    * every pinned column's pairs, agreements and misses are inside the
      whole battery's;
    * the pinned columns hold EVERY above-count the battery misses --
      which is the reason these three were chosen, and the sentence a
      moved ceiling must be re-derived against. A ceiling that rises
      with the new misses in another column turns this red, and the pin
      must then be re-chosen rather than quietly left behind.
    """
    assert sorted(PINNED_CEILINGS) == sorted(PINNED_COLUMNS)
    assert sum(ceiling[0] for ceiling in PINNED_CEILINGS.values()) <= PAIRS
    assert sum(ceiling[1] for ceiling in PINNED_CEILINGS.values()) <= OUTSIDE_CEILING
    assert sum(ceiling[2] for ceiling in PINNED_CEILINGS.values()) == MISSED_CEILING, (
        "the pin no longer holds every above-count the battery misses: "
        f"{PINNED_CEILINGS} against K-P4-06's {MISSED_CEILING}"
    )
    assert (PAIRS, OUTSIDE_CEILING, MISSED_CEILING) == (2160, 609, 3), (
        "K-P4-06's ceiling moved; re-derive the pin above, then this line"
    )


def test_a_crowded_saturated_position_keeps_its_spread_and_its_tail(
    tmp_path: pathlib.Path,
) -> None:
    """Length of stay: the twin's first position keeps the real shape.

    The real first position has a spread of 7.373 and a ninetieth
    percentile of 16 days. At seeds 0 and 1 the twin must hold its 45
    numbers, a spread within a tenth of the real one, and a ninetieth
    percentile within two days of it. The fill in order gives 7.320 and
    17 at both seeds.

    Mutation: the withdrawn leftover rule moves a doubled stratum of the
    crowded low end onto an empty point of the tail -- spread 10.635
    and 11.441, ninetieth percentile 30 at both seeds -- and this test
    goes red, while `synthtwin validate` exits 0 on that twin.

    The line that stood here, "withdrawing the fill (the walk alone)
    holds 43 of the 45 numbers", was stale and is corrected
    (finding 1 of this landing's review): re-measured 2026-09-20, with
    `_saturated_integers` answering nothing this holds 45 of 45 at both
    seeds, spread 7.320 and tail 17 unchanged, and so it does with
    `_saturated_levels` and `_saturated_bands` withdrawn beside it and
    with all three gone at once. The repeated walk of A-P4-55 reaches
    this grid without them.
    """
    cells = _stay_cells()
    real = [float(cell.split("/")[0]) for cell in cells]
    real_spread, real_tail = _spread_and_tail(real)
    assert (round(real_spread, 3), real_tail) == (7.373, 16.0)
    loaded = joined_battery.described(cells, tmp_path)
    facts = loaded.columns[0].facts
    assert isinstance(facts, contract.JoinedFacts), loaded.columns[0].role
    assert facts.parts[0].n_distinct_values == 45
    for seed in (0, 1):
        twin = generation.generate(loaded, seed)
        held = joined_battery.position_numbers(list(twin.columns[0]), facts)
        spread, tail = _spread_and_tail(held[0])
        assert len(set(held[0])) == 45, (seed, len(set(held[0])))
        assert abs(spread - real_spread) <= 0.1 * real_spread, (
            seed, spread, real_spread
        )
        assert abs(tail - real_tail) <= 2.0, (seed, tail, real_tail)


def test_a_reading_taken_twice_never_stands_above_itself(
    tmp_path: pathlib.Path,
) -> None:
    """`a/a/c/50 - a`: the published 0 rows above, at seven seeds.

    The seeds are the seven of forty where the withdrawn rule missed
    it: each of the two equal positions was walked on its own and they
    stopped landing on the same numbers, so 1 to 6 rows held the first
    above the second. The fill in order meets 0 at all forty.

    Mutation: the withdrawn rule gives 3, 1, 6, 1, 3, 3 and 5 rows above
    at seeds 1, 5, 16, 18, 22, 26 and 32, and so does withdrawing the
    fill: the break is the walk taking the fill's place, not the
    leftover points, which it never reached here.

    WHICH FILL, MEASURED 2026-09-20 (finding 1 of this landing's
    review). "The fill" was `_saturated_integers` alone when that line
    was written, and two more statements fill the same grid now
    (`_saturated_levels`, plan P4-D178, and `_saturated_bands`, the
    carried numbers pass). Withdrawing `_saturated_integers` by itself
    leaves 0 rows above at all seven seeds today; withdrawing all three
    gives exactly 3, 1, 6, 1, 3, 3 and 5, and this test goes RED. So
    this test does pin the fill, and it takes all three withdrawals to
    show it.
    """
    loaded = joined_battery.described(_repeated_cells(), tmp_path)
    facts = loaded.columns[0].facts
    assert isinstance(facts, contract.JoinedFacts), loaded.columns[0].role
    assert facts.n_parts == 4
    assert facts.part_above[0] == 0, facts.part_above
    missed: "list[tuple[int, int]]" = []
    for seed in (1, 5, 16, 18, 22, 26, 32):
        twin = generation.generate(loaded, seed)
        held = joined_battery.position_numbers(list(twin.columns[0]), facts)
        above = joined_battery.pair_scores(held, facts)[0][1]
        if above != 0:
            missed += [(seed, above)]
    assert not missed, f"(seed, rows above) against a published 0: {missed}"


def test_a_saturated_pressure_comes_back_whole_through_the_commands(
    tmp_path: pathlib.Path,
) -> None:
    """The round trip, on the demonstration's own blood pressure.

    `fixtures.joined_column_text()`: 240 readings whose systolic position
    publishes 120 different numbers between 100 and 219 and whose
    diastolic publishes 100, both saturated integer grids. Described,
    generated at seed 7, the twin described again, and `synthtwin
    validate` run on the twin and on the real table: both exit 0, the
    twin holds every number of both positions, and the rows with the
    first number above the second are the published count.

    Mutation, RE-MEASURED 2026-09-20 (finding 1 of this landing's
    review): the line here said withdrawing the fill leaves the
    diastolic position 98 numbers of 100, and it no longer does.
    `_saturated_integers` answering nothing holds 120 and 100 of 120 and
    100 at this seed, and so do `_saturated_levels` and
    `_saturated_bands` withdrawn beside it and all three at once. What
    this test pins is the round trip through the commands, not the fill;
    the fill's own guard is in `tests/test_carried_numbers.py`.
    """
    cells = fixtures.joined_column_text(240)
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "trip",
        cells,
        flags=("--measurement", "pressure"),
        seed="7",
        header="pressure",
    )
    assert (twin_exit, real_exit) == (0, 0)
    assert first["role"] == "joined_numbers" == second["role"]
    parts = first["parts"]
    assert isinstance(parts, list)
    for place in range(2):
        block = parts[place]
        assert isinstance(block, dict)
        held = {cell.split("/")[place] for cell in written}
        assert len(held) == block["n_distinct_values"], (
            place, len(held), block["n_distinct_values"]
        )
    above = sum(
        1
        for cell in written
        if int(cell.split("/")[0]) > int(cell.split("/")[1])
    )
    assert [above] == first["part_above"], (above, first["part_above"])
