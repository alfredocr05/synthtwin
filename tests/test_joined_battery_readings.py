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
- `f545bf1` (the final Codex review of the number censuses, first commit
  of carried-fix-numbers): 615 and 6 -- plan P4-D147, the fill of a
  saturated integer grid;
- `b93b285` (G6.5a reconciled): 597 and 7, which is e53d5f4.

WHAT P4-D147 IS FOR, AND WHAT IT DID HERE. It exists so that a column on
a saturated grid -- 400 rows of `+1.0` to `+400.0` -- holds every number
it publishes, and the plan holds a joined position to that count exactly
too (`tests/test_p2c4f1_disposition_registry.py` refuses a position
short of it). It gives stratum `k` the `k`-th integer whatever integer
the ladder put it at, so the whole run of strata between a doubled point
and an empty one moves one integer off the ladder together. Inside a
joined position that moves which rows stand above the other position's
numbers: on battery column 9, `first/second/third/100 - first`, the
column went from 54 agreements outside and 0 above-counts missed to 110
and 6.

THE REPAIR, AND WHAT IT DOES NOT RESTORE. Inside a joined position the
walk now runs first and only the points it leaves empty are filled, each
by the doubled stratum moving the fewest rows the least distance (method
G6.5a), so every position still holds its count. Measured on the
repaired tree with the same harness: 604 outside and 1 missed. The six
above-counts the fill cost are back; the one left is Phase 4's own.
The agreements are NOT back to 550: the fill in order leaves 597, the
walk and its leftover fill 604, and only withdrawing the fill from
positions altogether reaches 546 -- by leaving 185 more position runs of
the battery's 1,680 short of their count, an exact fact the registry
test holds, and by turning that test red. Every assignment meeting a
saturated position's count moves the position off its ladder somewhere,
and column 9 carries most of the difference (110 or 115 outside with a
fill, 56 without).
"""

from __future__ import annotations

import concurrent.futures
import importlib.util
import os
import pathlib

import fixtures
import joined_battery
import synthtwin
from synthtwin import contract, generation
from tests.test_stage2_round_trip import _round_trip

# THE CEILINGS. Above-counts: 1, restored -- the recorded 0 was true of
# round 3 only; round 4 of the same landing (da73c1c, Phase 4) missed one
# and the record was not moved. Agreements: 604, the figure of the rule
# as it stands, which is 7 above e53d5f4's 597 and 54 above the recorded
# 550; the docstring above says why no rule keeping every position's
# count reaches below it on this battery.
OUTSIDE_CEILING = 604
MISSED_CEILING = 1
PAIRS = 2160

ORACLE = (
    pathlib.Path(__file__).resolve().parents[1]
    / "tools"
    / "reference"
    / "make_generation_reference_vectors.py"
)

# Battery column 9 and the seed its witness is taken at.
FOURTH_COLUMN = 9
ABOVE_SEED = 7


def _column_nine(folder: pathlib.Path) -> "tuple[contract.Profile, contract.JoinedFacts]":
    rows = joined_battery.battery_rows()[FOURTH_COLUMN]
    loaded = joined_battery.described(rows, folder)
    facts = loaded.columns[0].facts
    assert isinstance(facts, contract.JoinedFacts), loaded.columns[0].role
    assert facts.n_parts == 4, facts.n_parts
    return loaded, facts


def test_a_saturated_position_keeps_its_count_and_its_pairs_keep_theirs(
    tmp_path: pathlib.Path,
) -> None:
    """Battery column 9 at seed 7, where the fill in order cost a row.

    Its first and fourth positions are saturated integer grids: 51
    different numbers from 10 to 60, and from 40 to 90, the fourth being
    `100 - first`, published at an agreement of -1.0 with 22 rows holding
    the first above the fourth. The twin must hold both exact facts at
    once: every one of the 51 numbers in each position, and every
    published above-count.

    Mutation, both halves: taking the fill in order inside the positions
    (e53d5f4's rule) holds the counts and misses pair (1, 4) at 23 rows
    against 22; withdrawing the leftover fill (the walk alone) meets the
    above-counts and holds 50 and 49 of the 51 numbers.
    """
    loaded, facts = _column_nine(tmp_path)
    seat = 2
    assert facts.part_agreements[seat] == -1.0, facts.part_agreements
    assert facts.part_above[seat] == 22, facts.part_above
    twin = generation.generate(loaded, ABOVE_SEED)
    held = joined_battery.position_numbers(list(twin.columns[0]), facts)
    counts = [
        (place, len(set(held[place])), facts.parts[place].n_distinct_values)
        for place in (0, 3)
    ]
    assert all(count[1] == count[2] for count in counts), (
        f"(position, held, published) at seed {ABOVE_SEED}: {counts}"
    )
    scores = joined_battery.pair_scores(held, facts)
    missed = [
        (place, scores[place][1], facts.part_above[place])
        for place in range(len(scores))
        if scores[place][1] != facts.part_above[place]
    ]
    assert not missed, f"(pair, held, published) at seed {ABOVE_SEED}: {missed}"


def test_the_battery_of_three_and_four_positions_keeps_its_figures(
) -> None:
    """Twelve columns, forty seeds, 2,160 pairs: 604 outside, 1 missed.

    The KPI of ledger K-P4-06, measured the way the driver measures it.
    The columns are spread over worker processes because each takes
    about twenty-five seconds; a worker builds its own column from the
    recipe, so nothing crosses the process boundary but three counts.

    Mutation: the fill in order inside joined positions gives 597
    outside and 7 missed, which is e53d5f4's figure, and this test red
    on the above-counts.
    """
    workers = max(1, min(6, os.cpu_count() or 1))
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
        counts = list(
            pool.map(joined_battery.one_column, range(joined_battery.COLUMNS))
        )
    imported = {count[3] for count in counts}
    assert imported == {str(synthtwin.__file__)}, imported
    pairs = sum(count[0] for count in counts)
    outside = sum(count[1] for count in counts)
    missed = sum(count[2] for count in counts)
    assert pairs == PAIRS, pairs
    assert outside <= OUTSIDE_CEILING, (
        f"{outside} of {pairs} agreements outside G12.9's window, against "
        f"the ceiling {OUTSIDE_CEILING}; by column: "
        f"{[count[:3] for count in counts]}"
    )
    assert missed <= MISSED_CEILING, (
        f"{missed} of {pairs} above-counts missed, against the ceiling "
        f"{MISSED_CEILING}; by column: {[count[:3] for count in counts]}"
    )


def test_the_oracle_case_holds_every_number_only_through_the_leftover_fill(
    monkeypatch,
) -> None:
    """The frozen case's second half, beside its registered mutant.

    `joined_saturated_position`'s registered mutant takes the fill in
    order inside the positions. This withdraws the other half instead --
    the leftover fill -- and the oracle's positions then hold twenty-one
    numbers of the twenty-two each publishes, with twenty-four cells
    moved, so both halves of the rule are held up by committed bytes.
    """
    spec = importlib.util.spec_from_file_location("oracle_k_p4_06", ORACLE)
    assert spec is not None and spec.loader is not None
    oracle = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(oracle)
    shipped, _claims = oracle.build_case("joined_saturated_position")
    cells = shipped["cells"]
    for place in range(2):
        assert len({cell.split("/")[place] for cell in cells}) == 22
    monkeypatch.setattr(oracle, "RECOUNT_DISTINCT", False)
    monkeypatch.setattr(
        oracle,
        "onto_leftover_points",
        lambda walked, _points, _sizes, _bands, _figures: walked,
    )
    walked, _claims = oracle.build_case("joined_saturated_position")
    moved = sum(
        1 for row in range(len(cells)) if walked["cells"][row] != cells[row]
    )
    assert moved == 24, moved
    for place in range(2):
        assert len({cell.split("/")[place] for cell in walked["cells"]}) == 21


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

    Mutation: withdrawing the leftover fill leaves the diastolic position
    98 numbers of 100 at this seed.
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
