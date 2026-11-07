"""The polish's sort, held to a plain sort (lane MPg's repair 4, plan P4-D456; LANE MPg RULINGS 14 (3)).

G16.3 re-assigns each frame group's places to its rows sorted by score,
ties to the lower row; repair 2 sorts them as one whole number a row
(`generation._score_key`: the score's exponent and fraction, then the row)
to save memory, and only the battery's ST2 and ST4 digests showed that this
is the same order, which no test held: lane MPg's verify 2 found two
mutants of the key living through the whole gate (the key's fraction cut
to 20 bits; ties to the higher row). WHAT IS HELD, each case red on both:

- the shipped twin of an invented table of two cohorts at 20,000 rows, with
  every kind of target the polish aims at, is byte for byte the twin whose
  every column step is tests/moment_polish_reference.py's, the step as
  repair 3 shipped it with each frame group sorted as plain (score, row)
  tuples;
- two equal scores take their places in row order, and two scores apart
  only past the twentieth bit of their fraction in the order of their
  scores, on a column step of their own.

THIS FILE IS THE NET FOR LANE ARR-b, which rewrites the polish's sorts and
sums with the audited array helper: whatever that lane writes, these bytes
stand. It stands apart from tests/test_moment_polish.py because the gate
file passed 180 CPU seconds with it (LANE MPg RULINGS 13 (2)).
"""

import math
import random

import fixtures
import pytest

from synthtwin import chain, chain_walk, contract, generation, profile, reading, rendering, taxonomy


def _first_parting(shipped: str, referenced: str) -> str:
    """Where two twins' texts first part: the line, and each twin's line there."""
    ours = shipped.split("\n")
    theirs = referenced.split("\n")
    for at in range(min(len(ours), len(theirs))):
        if ours[at] != theirs[at]:
            return f"line {at}: {ours[at]!r} against the reference's {theirs[at]!r}"
    return f"{len(ours)} lines against the reference's {len(theirs)}"


def _two_cohorts_text(n_rows: int, seed: int) -> str:
    """An invented table of two cohorts (lane MPg's repair 4), a fixed function of `seed`: four rows in five hold two
    near measurements `pa` and `pb` and a third, `lab`, blank on one in four of them; the fifth holds a `dose` alone;
    every row holds a three-level `kind` and a yes/no `flag`. Every reading lies far above 125, so no column reads as
    an age. The dose's targets are band means alone, so two of its rows with the same hidden sum and bands tie."""
    draw = random.Random(seed)
    lines = ["kind,pa,pb,lab,dose,flag"]
    for _row in range(n_rows):
        kind = draw.choice(["a", "b", "c"])
        level = "abc".index(kind)
        if draw.random() < 0.8:
            pa = 300.0 + 20.0 * level + draw.gauss(0.0, 30.0)
            pb = pa + draw.gauss(0.0, 12.0)
            lab = "" if draw.random() < 0.25 else f"{200.0 + 0.5 * (pa - 300.0) + draw.gauss(0.0, 15.0):.1f}"
            flag = "1" if draw.random() < 1.0 / (1.0 + math.exp(-(pa - 320.0) / 20.0)) else "0"
            lines += [f"{kind},{pa:.1f},{pb:.1f},{lab},,{flag}"]
        else:
            dose = 500.0 + 40.0 * level + draw.gauss(0.0, 25.0)
            flag = "1" if draw.random() < 0.3 + 0.2 * level else "0"
            lines += [f"{kind},,,,{dose:.1f},{flag}"]
    return "\n".join(lines) + "\n"


def test_the_shipped_twin_is_the_tuple_sort_reference_s_byte_for_byte(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    """THE NET FOR LANE ARR-b (repair 4, LANE MPg RULINGS 14 (3); the carried survivors of lane MPg's verify 2): lane
    ARR-b rewrites the polish's sorts and sums with the audited array helper, and whatever it writes, the shipped twin
    must stay these bytes. On an invented table of two cohorts at 20,000 rows (`_two_cohorts_text`: five polished
    columns, every kind of target, pairs, band means, a binary's splits and shares, blanks; twin seed 0), the shipped
    twin's text equals, byte for byte, the text of the twin whose every column step is
    tests/moment_polish_reference.py's: the step as repair 3 shipped it, each frame group's rows sorted as plain
    (score, row) tuples, the row last, its places by a plain sort, never `_score_key`'s one whole number a row; the
    reference takes every step the shipped twin takes. Repair 2's key is exact only if this holds (until now only the
    battery's ST2 and ST4 digests showed it, and no test held them). On this twin the 55 steps sort 746,955 rows in
    825 groups, 105 of them tied with the row before (the dose's targets are band means alone), and 237 rows a
    score's twentieth bit of fraction would put before a lower score. Mutants, both red here: the key's fraction cut
    to 20 bits; ties to the higher row (the step below pins the ties on their own). It costs about 37 s of process
    time (user plus system; 78 s of wall-clock at a one-minute load near 100)."""
    import moment_polish_reference

    source = tmp_path / "cohorts.csv"
    source.write_text(_two_cohorts_text(20000, 4), encoding="utf-8", newline="\n")
    settings = taxonomy.Settings(small_cell_floor=11)
    table = reading.read_table(str(source), small_cell_floor=11)
    document = profile.build_document(table, settings, [], [], [])
    chained = chain.describe(table, document, settings, chain.ChainSwitch("cohorts", bytes(range(32)), rows_per_person=chain.ROWS_UNASKED))
    assert chained.statistical is not None and chained.statistical["moments"] is not None
    written = dict(document)
    written["relationships"] = dict(written["relationships"], statistical=chained.statistical)
    path = fixtures.write_profile(tmp_path, "cohorts-profile.json", written)
    loaded = contract.load_profile(str(path), chain=True)
    planned = generation._polish_plan(loaded)
    kinds = {target.kind for _name, targets in planned for target in targets}
    assert {name for name, _targets in planned} == {"pa", "pb", "lab", "dose", "flag"}, planned
    assert kinds == {"pair", "within", "by", "share"}, kinds
    shipped_steps: "list[str]" = []
    reference_steps: "list[str]" = []
    inner = generation._polish_column

    def shipped_step(column, name, targets, sums, state, walk, adjust):  # type: ignore[no-untyped-def]
        shipped_steps.extend([name])
        inner(column, name, targets, sums, state, walk, adjust)

    def reference_step(column, name, targets, sums, state, walk, adjust):  # type: ignore[no-untyped-def]
        reference_steps.extend([name])
        moment_polish_reference.polish_column(column, name, targets, sums, state, walk, adjust)

    monkeypatch.setattr(generation, "_polish_column", shipped_step)
    shipped = "".join(rendering.twin_csv_pieces(generation.generate_held(loaded, 0)))
    monkeypatch.setattr(generation, "_polish_column", reference_step)
    referenced = "".join(rendering.twin_csv_pieces(generation.generate_held(loaded, 0)))
    assert len(shipped_steps) == 55 and reference_steps == shipped_steps, (shipped_steps, reference_steps)
    assert shipped.count("\n") == 20001
    assert shipped == referenced, _first_parting(shipped, referenced)


def test_two_equal_scores_take_their_places_in_row_order() -> None:
    """THE TIES (repair 4, LANE MPg RULINGS 14 (3)): G16.3's frame group takes its places by its rows sorted as
    (score, row) pairs, so of two equal scores the lower row takes the lower place. One column step with no target, so
    each row's score is its hidden score alone, `z = (S - 393210) / 65536`: 14 rows in two frame groups (a row's band
    at its chain level, even and odd rows), each group's places listed in reverse of its rows, holding equal scores
    (0.0, 3.0, -1.5 and 5.0, on two or three rows each) and a pair 2 ** -16 apart at 200 (a sum its three bytes hold)
    whose larger score stands on the lower row. The shipped step gives every row the place a plain sort of
    (score, row) tuples gives it, and each tied pair its places in row order. Mutants (lane MPg's verify 2's
    survivors): ties to the higher row; the key's fraction cut to 20 bits (the near pair then ties and goes in row
    order)."""
    rows = 14
    centre = chain_walk.SCORE_CENTRE
    unit = chain_walk.SCORE_UNIT
    high = centre + 200 * unit
    # Each row's hidden sum: even rows (group 0) then odd rows (group 1), as (row, sum).
    sums_of = {
        0: centre + 3 * unit, 2: centre, 4: centre + 3 * unit, 6: high + 1, 8: centre, 10: centre - unit - unit // 2, 12: high,
        1: centre - unit - unit // 2, 3: centre - unit - unit // 2, 5: centre + 5 * unit, 7: centre - unit - unit // 2,
        9: centre, 11: centre + unit, 13: centre + 5 * unit,
    }
    scores = {row: chain_walk.hidden_score(total) for row, total in sums_of.items()}
    assert scores[6] == 200.0 + 2.0**-16 and scores[12] == 200.0 and scores[10] == -1.5
    column = generation._WalkColumn(0, 0, ((), (), ()), (2, 2, 2), ())
    column.codes = bytearray(row % 2 for row in range(rows))
    column.width = 1
    column.index_width = 3
    column.index = bytearray(3 * rows)
    for row in range(rows):
        chain_walk.write_code(column.index, 3, row, rows - 1 - row)
    column.slot_l0 = bytearray(rows)
    column.slot_codes = bytearray(10 * place for place in range(rows))
    sums = chain_walk.packed(rows, chain_walk.SUM_WIDTH)
    for row, total in sums_of.items():
        chain_walk.put(sums, row, total)
    state = generation._PolishState(
        [("x", [])], rows, {"x": bytearray(rows)}, {"x": bytearray([1] * rows)}, {}, {}, {"x": (0.0, 1.0)}, [], {}
    )
    generation._polish_column(column, "x", [], sums, state, None, False)  # type: ignore[arg-type]
    placed = [chain_walk.read_code(column.index, 3, row) for row in range(rows)]
    # The reference: a plain sort of (score, row) tuples inside each group, its places rising.
    expected = [0 for _row in range(rows)]
    for group in (0, 1):
        members = [row for row in range(rows) if row % 2 == group]
        places = sorted(rows - 1 - row for row in members)
        for place, (_score, row) in zip(places, sorted((scores[row], row) for row in members)):
            expected[row] = place
    assert placed == expected, (placed, expected)
    assert [state.codes["x"][row] for row in range(rows)] == [10 * place for place in expected]
    for low, later in ((2, 8), (0, 4), (1, 3), (3, 7), (5, 13)):
        assert scores[low] == scores[later] and placed[low] < placed[later], (low, later, placed)
    assert placed[12] < placed[6], placed
