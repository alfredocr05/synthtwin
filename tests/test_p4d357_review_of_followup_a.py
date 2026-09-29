"""Plan P4-D357 A: the review of follow-up A (P4-D353), item by item.

1. THE COST RULE DECIDES ON THE BLOCK THE LOADER READS. An affixed column
   wearing one wrapper set its two cell-population keys after the tail
   rule had run, so the rule asked the windows of a block nobody reads:
   `1 mg` to `99 mg`, `210 mg` and one text cell published the high
   tail's pair at a floor of eleven where the published block, both
   pairs withheld, keeps both moments. Held for every nested numeric
   role by asking, of each block a cost-rule call returns, that it IS
   the block published and that the call asked the loader's own reading
   of it.
2. NO TWIN CELL ON A STAND-IN NUMBER THE COLUMN DOES NOT HOLD, anywhere in
   value construction: G6.5a's fills, walk and push were exempt, and on 9000
   to 9998 beside 10000 and 10001 every twin wrote `9999` once.
3. A STAND-IN MOVED ON A GRID FINER THAN BINARY64 LEAVES IT: one step of
   fourteen places beside `-999` read back as `-999`, in the product and in
   the oracle alike.
4. ONE SIDE WITHHELD FOR ANY REASON CLOSES THE OTHER'S PAIR, binary64's
   among them.
5. A PINNED SIDE SAYS WHAT ITS PAIR GIVES BACK: every value, the outermost,
   or a count -- held against competing multisets, not against the enum.
6. "EVERY VALUE IS DIFFERENT" ONLY WHERE EVERY CELL IS, as written, as
   folded and as the role reads it.

And the second review of this landing: A STAND-IN THE COLUMN KEEPS IS ITS
OWN VALUE. The refusals of item 2 asked only whether a point was one of the
three, so a heap the description publishes as `kept_as_a_number` came back
in no cell; every pass now passes over only a stand-in the column does not
keep, one held below the floor included.

Every table is built at test time from a fixed seed string or a closed
formula; no data-format file enters the repository (plan D13).
"""

from __future__ import annotations

import copy
import dataclasses
import math
import pathlib
import random

import pytest

import complement_reader as columns
import cost_rule_window as window
import kpi_shapes
from synthtwin import contract, parsing, summary, taxonomy, validation


def _one_column(cells: "list[str]") -> str:
    return "value\n" + "\n".join(cells) + "\n"


# -- 1. the cost rule decides on the final block ------------------------------

# The review's shape: ninety-nine consecutive amounts and one far one, each
# wearing ` mg`, beside one cell of ordinary text.
_REVIEW_AFFIXED = [f"{value} mg" for value in range(1, 100)] + ["210 mg", "review_marker"]


def _loader_windows(described: kpi_shapes.Described, block: "dict") -> "dict[str, bool]":
    """Per moment, does the window the LOADER's reading of this column draws miss its value?"""
    facts = described.loaded.columns[0].facts
    assert isinstance(facts, contract.AffixedFacts)
    drawn = validation._windows_of(None, facts.numbers, described.loaded.settings.small_cell_floor)
    return {
        name: name in drawn and not drawn[name][0] <= block[name] <= drawn[name][1]
        for name in ("mean", "std")
    }


def test_an_affixed_pair_is_published_only_where_the_published_block_would_miss(
    tmp_path: pathlib.Path,
) -> None:
    """The review's affixed column withholds both pairs: its final block keeps both moments without them.

    PREMISE, from the checker's own windows over the loaded block: with
    neither pair the mean and the spread both lie inside their windows. So
    the owner's "only where it costs" publishes neither, and the twin still
    meets both moments at seeds 0, 4 and 9. On the base 2af1f03 the high
    pair was published, decided on a block whose `n_left_out_of_statistics`
    still read 0 and whose spread window ended at 32.734867, short of the
    published 32.751590.
    """
    described = kpi_shapes.describe(tmp_path, "affixed", _one_column(_REVIEW_AFFIXED), 11)
    block = described.document["columns"][0]
    assert block["role"] == "affixed_number" and block["n_left_out_of_statistics"] == 1, (
        "premise: one straggler beside a hundred cores"
    )
    assert _loader_windows(described, window.withheld(block, ("low", "high"))) == {
        "mean": False,
        "std": False,
    }, "premise: the final block with both pairs withheld keeps both moments"
    published = [side for side in ("low", "high") if block["tails"][side]["mean_distance"] is not None]
    assert published == [], f"the rule published {published} where withholding costs nothing"
    for seed in (0, 4, 9):
        text = kpi_shapes.twin_text(described, seed)
        outcome = kpi_shapes.measure(described, text, f"twin-{seed}.csv")
        moments = [one for one in kpi_shapes.missed(outcome) if "moments." in one]
        assert moments == [], f"seed {seed}: {moments}"


def _nested_blocks(block: "dict") -> "list[tuple[str, dict]]":
    """Every numeric block a published column holds, named."""
    role = block["role"]
    if role in (taxonomy.ROLE_COUNT, taxonomy.ROLE_CONTINUOUS):
        return [("column", block)]
    if role == taxonomy.ROLE_AFFIXED:
        found = [("commonest wrapper", block)]
        for place, entry in enumerate(block["affix_variants"]):
            found += [(f"wrapper {place}", entry["numbers"])]
        return found
    if role == taxonomy.ROLE_JOINED:
        return [(f"part {place}", part) for place, part in enumerate(block["parts"])]
    if role == taxonomy.ROLE_COMPOUND:
        return [("numbers", block["numbers"])]
    return []


def _nested_facts(facts: object) -> "list[contract.NumericFacts]":
    """The loader's reading of each block `_nested_blocks` names, in the same order."""
    if isinstance(facts, contract.NumericFacts):
        return [facts]
    if isinstance(facts, contract.AffixedFacts):
        return [facts.numbers] + [entry.numbers for entry in facts.affix_variants]
    if isinstance(facts, contract.JoinedFacts):
        return list(facts.parts)
    if isinstance(facts, contract.CompoundFacts):
        return [facts.numbers]
    return []


def _spelling_free(facts: contract.NumericFacts) -> contract.NumericFacts:
    """The facts without a count column's spelling census, which the role adds after the block."""
    return dataclasses.replace(facts, number_spellings={})


_CORES = [str(value) for value in range(1, 100)] + ["210"]


def _pairs() -> "list[str]":
    draw = random.Random("p4d357/joined")
    return [f"{core}/{draw.randint(40, 90)}" for core in _CORES]


# (name, cells, the role): every role whose block holds a numeric block with
# tails, each beside cells its population keys count and its cores do not.
_NESTED_SHAPES = (
    ("count_beside_text", _CORES + ["review_marker"], taxonomy.ROLE_COUNT),
    ("continuous_beside_text", [f"-{core}" for core in _CORES] + ["review_marker"], taxonomy.ROLE_CONTINUOUS),
    ("affixed_beside_text", _REVIEW_AFFIXED, taxonomy.ROLE_AFFIXED),
    ("affixed_beside_a_bare_number", [f"{core} mg" for core in _CORES] + ["300"], taxonomy.ROLE_AFFIXED),
    ("affixed_two_wrappers", [f"{core} mg" for core in _CORES] + [f"{core} kg" for core in _CORES] + ["review_marker"], taxonomy.ROLE_AFFIXED),
    ("joined_beside_text", _pairs() + ["review_marker"], taxonomy.ROLE_JOINED),
    ("joined_far_in_both", [f"{core}/{core}" for core in _CORES] + ["review_marker"], taxonomy.ROLE_JOINED),
    ("numbers_beside_labels", _CORES + ["absent"] * 12, taxonomy.ROLE_COMPOUND),
)


@pytest.mark.parametrize("name,cells,role", _NESTED_SHAPES, ids=[case[0] for case in _NESTED_SHAPES])
def test_every_nested_block_the_cost_rule_decides_is_the_block_the_loader_reads(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, name: str, cells: "list[str]", role: str
) -> None:
    """Each block a cost-rule call returns IS the nested block published, and the call asked its loaded reading.

    Two halves, and each is a way the producer's question can part from the
    checker's: a key set on the block after the rule ran (review item 1:
    the affixed column's two cell-population keys), and a count handed to
    the loader's reading that is not the one the loader uses for that
    block (`taxonomy._Population`). The memo is emptied before every call,
    so every candidate is asked afresh.
    """
    asked: "list[contract.NumericFacts]" = []
    returned: "list[tuple[dict, list[contract.NumericFacts]]]" = []
    reading = contract.numeric_block_facts
    deciding = taxonomy._pairs_that_cost

    def spy_reading(*arguments: object, **named: object) -> contract.NumericFacts:
        found = reading(*arguments, **named)  # type: ignore[arg-type]
        asked.extend([found])
        return found

    def spy_deciding(*arguments: object, **named: object) -> "dict":
        taxonomy._MOMENTS_MISSED.clear()
        start = len(asked)
        found = deciding(*arguments, **named)  # type: ignore[arg-type]
        returned.extend([(copy.deepcopy(found), list(asked[start:]))])
        return found

    monkeypatch.setattr(contract, "numeric_block_facts", spy_reading)
    monkeypatch.setattr(taxonomy, "_pairs_that_cost", spy_deciding)
    described = kpi_shapes.describe(tmp_path, name, _one_column(cells), 11)
    block = described.document["columns"][0]
    assert block["role"] == role, f"premise: read as {role}, not {block['role']}"
    blocks = _nested_blocks(block)
    loaded = _nested_facts(described.loaded.columns[0].facts)
    assert len(blocks) == len(loaded)
    decided = 0
    for (label, published), facts in zip(blocks, loaded):
        mine = [
            (answer, readings)
            for answer, readings in returned
            if answer["tails"] == published["tails"]
            and answer["percentiles"] == published["percentiles"]
            and answer["mean"] == published["mean"]
        ]
        if not mine:
            continue
        decided = decided + 1
        for answer, readings in mine:
            moved = [key for key in answer if key not in published or published[key] != answer[key]]
            assert moved == [], f"{label}: set after the cost rule decided: {moved}"
            assert _spelling_free(facts) in [_spelling_free(one) for one in readings], (
                f"{label}: the cost rule asked a reading the loader does not make of the published block"
            )
    assert decided > 0, "premise: the cost rule decided at least one published block"


# -- 4. the cross-side closure, whatever withheld the first side ---------------


def _far_apart(low_first: bool) -> "list[str]":
    """Eleven values near `-1.7e308` beside 89 near `1.68e308` (the review's item 4), or its mirror."""
    near = [str((-17000 + place) * 1e304) for place in range(11)]
    far = [str((16800 + place) * 1e304) for place in range(89)]
    if low_first:
        return near + far
    return [str(-float(cell)) for cell in near + far]


@pytest.mark.parametrize("unheld", ("low", "high"))
def test_a_side_binary64_cannot_hold_closes_the_other_side_s_pair(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, unheld: str
) -> None:
    """The other side's pair is withheld, and says why, where it keeps no moment.

    PREMISE: the far side's own pair is too large for binary64 (its remark
    says so) and the other side's back-solve leaves it open. The cross-side
    rule (plan P4-D353 part 2) withholds that open pair wherever the rule
    publishes nothing, and it asks nothing about why the first side has no
    pair: on 2af1f03 the pair was published, about `6.38e304` and
    `7.254e304`, and the checker's windows missed both moments with it and
    without it.
    """
    other = "high" if unheld == "low" else "low"
    cells = _one_column(_far_apart(unheld == "low"))
    with monkeypatch.context() as patched:
        patched.setattr(taxonomy, "_pairs_that_cost", lambda _cells, shaped, *_rest: shaped)
        opened = kpi_shapes.describe(tmp_path / "open", "far", cells, 11).document["columns"][0]
    described = kpi_shapes.describe(tmp_path, f"far-{unheld}", cells, 11)
    block = described.document["columns"][0]
    remarks = block["remarks"]
    assert taxonomy.tail_withheld_because(remarks, unheld) == taxonomy.TAIL_WITHHELD_UNHOLDABLE, (
        "premise: binary64 cannot hold the far side's pair"
    )
    assert opened["tails"][other]["mean_distance"] is not None, "premise: the other side's own walk leaves it open"
    assert window.missed(opened, 11) == window.missed(block, 11), "premise: the pair keeps no moment the closure loses"
    assert block["tails"][other]["mean_distance"] is None, (
        f"the {other} side published its pair beside a side binary64 cannot hold"
    )
    assert taxonomy.tail_withheld_because(remarks, other) == taxonomy.TAIL_WITHHELD_FOR_THE_OTHER


# -- 2 and 3. no twin cell on a stand-in number the column does not hold -------

_STAND_INS = tuple(parsing.NUMERIC_SENTINELS)


def _oracle() -> object:
    """The reference oracle (`tools/reference`), as the reference test already loads it."""
    import test_generation_reference as reference

    return reference.gen


def _held_stand_ins(written: "list[str]", cells: "list[str]") -> "list[str]":
    """The twin cells that read as a stand-in number the source column never holds."""
    held = {float(cell) for cell in cells if cell}
    return [cell for cell in written if float(cell) in _STAND_INS and float(cell) not in held]


def _read_at(value: float, figures: int) -> float:
    """What a value written at ``figures`` places reads back as."""
    return float(f"{value:.{figures}f}")


# The grid widths finer than binary64 beside every stand-in: at 14 figures a
# grid step is under half the binary64 gap beside `-999`, `9999` and `-9999`
# alike, and at 16 it is under a tenth of it.
_FINE_GRIDS = (14, 16)


@pytest.mark.parametrize("figures", _FINE_GRIDS)
@pytest.mark.parametrize("stand_in", _STAND_INS)
def test_a_drawn_stand_in_on_a_fine_grid_moves_to_a_number_the_format_tells_apart(
    stand_in: float, figures: int
) -> None:
    """G5.4's last rule moves a stand-in to a different binary64, in the generator and the oracle alike.

    On 2af1f03 the step of one grid unit toward nought read back as the
    stand-in itself, so the rule answered the value unchanged and the
    oracle, reading the same sentence, agreed: agreement masked the defect
    (review item 3). Both now answer a number that is not the stand-in and
    whose written text at the grid's width does not read back as one.
    """
    from synthtwin import generation

    lowest, highest = (stand_in - 50.0, stand_in + 50.0)
    rungs = (lowest,) + (stand_in,) * 99 + (highest,)
    ours = generation._drawn_off_the_stand_ins(stand_in, rungs, 1, 2, figures)
    theirs = _oracle().drawn_off_the_stand_ins(stand_in, lowest, highest, figures)
    assert ours != stand_in and _read_at(ours, figures) not in _STAND_INS, (
        f"{stand_in} at {figures} places stayed on a stand-in: {ours!r}"
    )
    assert abs(ours) < abs(stand_in), f"{stand_in} moved away from nought: {ours!r}"
    assert ours == theirs, f"the generator moves {stand_in} to {ours!r}, the oracle to {theirs!r}"


@pytest.mark.parametrize("figures", _FINE_GRIDS)
@pytest.mark.parametrize("stand_in", _STAND_INS)
@pytest.mark.parametrize("low", (True, False))
def test_a_derived_end_or_staircase_row_on_a_fine_grid_leaves_the_stand_in(
    stand_in: float, figures: int, low: bool
) -> None:
    """G5.3b step 5's end and its staircase row, on a fine grid, in the generator and the oracle alike.

    The end moves toward its boundary and the row outward, each by a number
    binary64 can tell from the stand-in; the review measured
    `contract._off_the_stand_ins(-999, True, -998, 14)` answering `-999`.
    """
    boundary = stand_in + 1.0 if low else stand_in - 1.0
    end = contract._off_the_stand_ins(stand_in, low, boundary, figures)
    their_end = _oracle().off_the_stand_ins(stand_in, low, boundary, figures)
    assert end != stand_in and _read_at(end, figures) not in _STAND_INS, f"the end stayed on {end!r}"
    assert (stand_in < end <= boundary) if low else (boundary <= end < stand_in)
    assert end == their_end, f"the generator's end {end!r}, the oracle's {their_end!r}"
    far = stand_in - 5.0 if low else stand_in + 5.0
    side = contract.TailReader(
        low=low, percent=1, boundary=boundary, rows=11, numbers=1000, flat=False,
        power=1, blend=0.0, reach=0.0, end=far, listed=(), counts=(),
    )
    row = contract._row_off_the_stand_ins(stand_in, side, figures)
    their_row = _oracle().row_off_the_stand_ins(stand_in, far, low, figures)
    assert row != stand_in and _read_at(row, figures) not in _STAND_INS, f"the row stayed on {row!r}"
    assert (far <= row < stand_in) if low else (stand_in < row <= far)
    assert row == their_row, f"the generator's row {row!r}, the oracle's {their_row!r}"


def _fine_around(stand_in: float) -> "list[str]":
    """200 values a few binary64 steps either side of a stand-in, at fourteen places, none of them it (review item 3)."""
    return [f"{stand_in + place * math.ulp(stand_in):.14f}" for place in range(-100, 101) if place]


@pytest.mark.parametrize("stand_in", _STAND_INS)
def test_no_twin_of_a_fine_grid_around_a_stand_in_writes_it(tmp_path: pathlib.Path, stand_in: float) -> None:
    """The whole twin, at seeds 0, 4 and 9: no cell reads as the stand-in the column does not hold.

    On 2af1f03 every twin wrote the stand-in once at fourteen places, and
    validation reported no miss. THE COST, named: the column's own values
    are every binary64 number of the range but the stand-in, so the only
    number left for the stratum the draw put there lies outside the range,
    and the twin holds one different number fewer than the 200 published
    (`distinct.n_distinct_values`), and misses nothing else.
    """
    cells = _fine_around(stand_in)
    assert [cell for cell in cells if float(cell) in _STAND_INS] == [], "premise: the column holds no stand-in"
    described = kpi_shapes.describe(tmp_path, "fine", _one_column(cells), 11)
    for seed in (0, 4, 9):
        text = kpi_shapes.twin_text(described, seed)
        written = [line for line in text.split("\n")[1:] if line]
        assert _held_stand_ins(written, cells) == [], f"seed {seed}: {_held_stand_ins(written, cells)}"
        missed = kpi_shapes.missed(kpi_shapes.measure(described, text, f"twin-{seed}.csv"))
        assert [one for one in missed if not one.endswith(":distinct.n_distinct_values")] == [], (
            f"seed {seed}: {missed}"
        )


def _normal_whole(centre: float, spread: float, rows: int, name: str) -> "list[str]":
    draw = random.Random(f"p4d357/{name}")
    cells = [str(round(draw.gauss(centre, spread))) for _row in range(rows)]
    return [cell for cell in cells if float(cell) not in _STAND_INS]


def _normal_tenths(centre: float, spread: float, rows: int, name: str) -> "list[str]":
    draw = random.Random(f"p4d357/{name}")
    cells = [f"{draw.gauss(centre, spread):.1f}" for _row in range(rows)]
    return [cell for cell in cells if float(cell) not in _STAND_INS]


# (name, cells): ordinary columns whose values run across a stand-in number
# without holding it -- the review's run of 9000 to 9998 beside 10000 and
# 10001, a gap at -999 inside whole numbers and inside tenths, and seeded
# normal readings around each stand-in, whole and in tenths. On 2af1f03 these
# wrote 1 to 3 stand-in cells a twin, every one through G6.5a.
_ACROSS_A_STAND_IN = (
    ("run_9000_9998_beside_10000", [str(value) for value in range(9000, 9999)] + ["10000", "10001"]),
    ("gap_at_minus_999", [str(value) for value in range(-1400, -999)] + [str(value) for value in range(-998, -500)]),
    ("tenths_gap_at_minus_999", [f"{tenths / 10:.1f}" for tenths in range(-10100, -9900) if tenths != -9990]),
    ("normal_whole_9999", _normal_whole(9999.0, 30.0, 600, "w9999")),
    ("normal_whole_minus_999", _normal_whole(-999.0, 30.0, 600, "wm999")),
    ("normal_whole_minus_9999", _normal_whole(-9999.0, 30.0, 600, "wm9999")),
    ("normal_tenths_minus_999", _normal_tenths(-999.0, 4.0, 600, "tm999")),
    ("normal_tenths_9999", _normal_tenths(9999.0, 4.0, 600, "t9999")),
)


@pytest.mark.parametrize("name,cells", _ACROSS_A_STAND_IN, ids=[case[0] for case in _ACROSS_A_STAND_IN])
def test_no_value_pass_puts_a_twin_cell_on_a_stand_in_the_column_does_not_hold(
    tmp_path: pathlib.Path, name: str, cells: "list[str]"
) -> None:
    """Every construction of G5 and G6 -- draw, end, rows, fills, walks, pushes -- refuses the three.

    PREMISE: the column holds no stand-in number and runs across one. At
    seeds 0, 4 and 9 the twin writes none and misses nothing: G6.5a's fill,
    walk and push pass a stand-in over as a point another stratum holds,
    which is the exemption plan P4-D353 part 4 made and P4-D357 A withdrew.
    """
    held = [float(cell) for cell in cells]
    assert [one for one in held if one in _STAND_INS] == [], "premise: no stand-in held"
    assert [one for one in _STAND_INS if min(held) < one < max(held)], "premise: the column runs across one"
    described = kpi_shapes.describe(tmp_path, name, _one_column(cells), 11)
    for seed in (0, 4, 9):
        text = kpi_shapes.twin_text(described, seed)
        written = [line for line in text.split("\n")[1:] if line]
        assert _held_stand_ins(written, cells) == [], f"seed {seed}: {_held_stand_ins(written, cells)}"
        missed = kpi_shapes.missed(kpi_shapes.measure(described, text, f"twin-{seed}.csv"))
        assert missed == [], f"seed {seed}: {missed}"


# THE PASSES NO SEEDED COLUMN ABOVE REACHES, each asked where its own next
# candidate is a stand-in: the generator's answer is not one, and where the
# oracle states the same step it gives the same answer. Each case below was
# the stand-in itself on e07020e.


def test_the_carrier_walk_takes_no_stand_in() -> None:
    """G6.4's walk to a whole number: `-999.3` rounds to `-999`, which is refused for `-998`."""
    from synthtwin import generation

    ours = generation._whole_inside(-999.3, "negative", (-1000.0, -998.0), (-2000.0, 0.0), 10, {})
    theirs = _oracle().whole_inside(-999.3, "negative", (-1000.0, -998.0), (-2000.0, 0.0), 10, {})
    assert ours not in _STAND_INS and ours == theirs == -998.0, (ours, theirs)


def test_the_separation_walk_passes_a_stand_in_over() -> None:
    """G6.5a's walk from `9998` with `9997` written: `9999` is refused and `9996` taken, in both."""
    from synthtwin import generation

    written = {generation._grid_text(9997.0, 0): 1, generation._grid_text(9998.0, 0): 2}
    ours = generation._apart_inside(9998.0, 0, "positive", (9990.0, 10010.0), (0.0, 20000.0), written)
    theirs = _oracle().apart_inside(9998.0, 0, "positive", (9990.0, 10010.0), (0.0, 20000.0), written)
    assert ours not in _STAND_INS and ours == theirs == 9996.0, (ours, theirs)


def test_the_sign_step_passes_a_stand_in_over() -> None:
    """G5.5's grid step of sign with every tenth down to `-998.9` held: `-999.0` is passed for `-999.1`."""
    from synthtwin import generation

    held = {-(tenths / 10): 1 for tenths in range(1, 9990)}
    ladder = (-2000.0,) + (0.0,) * 99 + (5.0,)
    ours = generation._grid_step_of_sign("negative", ladder, 1, held, 10000)
    theirs = _oracle().grid_step_of_sign("negative", ladder, 1, held, 10000)
    assert ours not in _STAND_INS and ours == theirs == -999.1, (ours, theirs)


def test_the_representable_grid_steps_off_a_stand_in() -> None:
    """G6.5a's last resort: a middle stratum on `9999` takes the next binary64 above it, in both."""
    import types

    from synthtwin import generation

    values = [9998.0, 9999.0, 10000.0]
    ours = generation._apart_on_the_representable_grid(types.SimpleNamespace(bands=["positive"] * 3), values)
    theirs = _oracle().representable_grid(3, ["positive"] * 3, values)
    assert [one for one in ours if one in _STAND_INS] == [] and ours == theirs, (ours, theirs)


def test_the_marks_run_passes_a_stand_in_over() -> None:
    """The grouping run's free points (plan P4-D185): `9999` is passed over, and `999` where the column is turned about nought."""
    from synthtwin import generation

    assert generation._free_grid_points(9998, 1, 2, 0, {}) == [9998, 10000]
    assert generation._free_grid_points(998, 1, 2, 0, {}, -1.0) == [998, 1000]
    assert generation._free_grid_points(998, 1, 2, 0, {}) == [998, 999], "a positive 999 is no stand-in"


def test_the_clearing_walk_takes_no_stand_in() -> None:
    """G6.7 moving `-900` out of a stretch whose lower edge is `-999`: the edge itself is refused."""
    from synthtwin import generation

    found = generation._cleared_value(
        (-2000.0, 0.0), {}, (0, 0), (-999.0, -500.0), ((-999.0, -500.0),), -900.0,
        "negative", True, {}, {-900.0: 1}, True, (-1,),
    )
    assert found is not None and found not in _STAND_INS, found


def test_the_twice_written_fill_counts_no_stand_in_among_its_points() -> None:
    """Plan P4-D193's fill of tenths from 9998.0 to 10000.0: twenty points once `9999.0` is refused, not 21."""
    import types

    from synthtwin import generation

    points = [9998.0 + tenths / 10 for tenths in range(21)]
    facts = types.SimpleNamespace(
        n_distinct_values=21,
        empty_edges=(),
        integer_valued=False,
        numeric_styles={"decimal": 21},
        kept_stand_ins=(),
    )
    layout = types.SimpleNamespace(bands=["positive"] * 21, sizes=[1] * 21)
    rungs = (9998.0,) + (9999.0,) * 99 + (10000.0,)
    filled = generation._twice_filled(facts, layout, rungs, points, 1)  # type: ignore[arg-type]
    assert filled is None or [one for one in filled if one in _STAND_INS] == [], filled


# -- 5. a pinned side says what its pair gives back: every value, or less ------


def _review_item_5() -> "list[str]":
    """0 to 1,089 once each, `1089` seven more times, and `1090`, `1093`, `1093`, `1189` (the review's column)."""
    return [str(value) for value in list(range(1090)) + [1089] * 7 + [1090, 1093, 1093, 1189]]


def test_a_pinned_tail_two_multisets_fit_says_only_its_outermost_value(tmp_path: pathlib.Path) -> None:
    """The review's column: two multisets of distances fit the high tail, so its pages name the outermost value, not every value.

    THE COMPETING MULTISETS, written out: `[0]*7 + [1, 4, 4, 100]` (the
    column's own, above the boundary `1089`) and `[0]*7 + [2, 2, 5, 100]`
    both hold eleven rows, sum 109 and sum of squares 10033, so the pair
    beside those rows fixes the outermost value `1189` and not the four
    between it and the boundary. On 2af1f03 the summary and the quality
    report both said the two distances would give those values back one
    by one; the remark, the summary's line and the report's sentence now
    say at least the outermost.
    """
    real = [0] * 7 + [1, 4, 4, 100]
    other = [0] * 7 + [2, 2, 5, 100]
    assert sorted(real) != sorted(other)
    assert (len(real), sum(real), sum(one * one for one in real)) == (len(other), sum(other), sum(one * one for one in other))
    described = kpi_shapes.describe(tmp_path, "review5", _one_column(_review_item_5()), 11)
    block = described.document["columns"][0]
    tail = block["tails"]["high"]
    assert tail["rows"] == 11 and tail["mean_distance"] is None and not tail["values"], "premise: eleven rows, withheld"
    boundary = validation._file_rung(block, tail["percent"])
    outer = sorted(float(cell) for cell in _review_item_5())[-11:]
    assert sorted(int(value - boundary) for value in outer) == sorted(real), "premise: those are the tail's distances"
    assert taxonomy.tail_withheld_because(block["remarks"], "high") == taxonomy.TAIL_PINS_END
    page = summary.render(described.document, "")
    line = [one for one in page.split("\n") if "the 11 largest values are not published" in one]
    assert len(line) == 1 and "would give back at least the outermost of those values" in line[0], line
    assert "one by one" not in line[0]
    report = validation._tail_withheld_reason(block, "high")
    assert "would give back at least the file's own outermost cell" in report and "one by one" not in report


def _reading_by_enumeration(distances: "list[int]", floor: int, edge: int, distinct: bool, least: int) -> "str | None":
    """What the facts of a tail fix, by listing every multiset they admit (tests/complement_reader.py's walk)."""
    total = sum(distances)
    squares = sum(one * one for one in distances)
    found, finished = columns._tail_multisets(
        len(distances), total, squares, least, edge, 1 if distinct else 0, cap=100_000, budget=5_000_000
    )
    if not finished:
        return None
    assert sorted(distances) in found, "the enumeration misses the real multiset"
    if len(found) == 1:
        return taxonomy.TAIL_PINS_EVERY
    top = max(distances)
    if {max(one) for one in found} == {top} and distances.count(top) < floor:
        return taxonomy.TAIL_PINS_END
    return taxonomy.TAIL_PINS_A_COUNT


def test_every_pinned_reading_is_the_one_the_multisets_give() -> None:
    """Over 3,000 seeded small tails the back-solve PINS, the reading equals a brute-force enumeration's.

    Parts from nought (a numeric tail) or one (a date or clock tail), all
    different or not, capped by an edge: where `_tail_verdict` answers
    PINNED, `_pinned_reach` says every value exactly where one multiset
    fits, the outermost exactly where every fitting multiset shares the
    largest part and fewer rows than the floor hold it, and a count
    otherwise -- each of the three reached (premise), and a count among them
    on tails whose largest part the floor does not protect.
    """
    draw = random.Random("p4d357/reach")
    seen: "dict[str, int]" = {}
    for _case in range(3000):
        least = draw.choice((0, 1))
        distinct = draw.random() < 0.3
        size = draw.randint(3, 9)
        edge = draw.randint(least + size + 1, 30)
        if distinct:
            distances = draw.sample(range(least, edge + 1), size)
        else:
            reach = draw.choice((2, 5, edge - least))
            distances = [draw.randint(least, least + reach) for _row in range(size)]
        floor = draw.randint(2, 11)
        if not distinct and draw.random() < 0.3:
            # A LARGEST PART THE FLOOR DOES NOT PROTECT: held `floor` times.
            distances = distances + [max(distances)] * (floor - distances.count(max(distances)))
        if taxonomy._tail_verdict(distances, floor, edge, distinct, least) != taxonomy.TAIL_PINNED:
            continue
        expected = _reading_by_enumeration(distances, floor, edge, distinct, least)
        if expected is None:
            continue
        found = taxonomy._pinned_reach(distances, floor, edge, distinct, least)
        assert found == expected, (distances, floor, edge, distinct, least, found, expected)
        seen[found] = seen.get(found, 0) + 1
    assert sorted(seen) == sorted(
        (taxonomy.TAIL_PINS_EVERY, taxonomy.TAIL_PINS_END, taxonomy.TAIL_PINS_A_COUNT)
    ), f"premise: every reading reached, {seen}"


# -- 6. "every value in this column is different" only where every one is -----

_EVERY = "every value in this column is different"
_NEARLY = "nearly every value in this column is different"


def _profiled(values: "list[str]") -> "taxonomy.ColumnProfile":
    return taxonomy.profile_column("column", 1, values, len(values), taxonomy.Settings(), False)


def _said(values: "list[str]") -> "tuple[str, list[str]]":
    """The role and the all-different sentences one column's remarks carry."""
    described = _profiled(values)
    return described.role, [
        remark for remark in described.remarks if _EVERY in remark and "tail boundary" not in remark
    ]


def _minutes(count: int, name: str) -> "list[str]":
    return ["%02d:%02d" % divmod(minute, 60) for minute in random.Random(name).sample(range(24 * 60), count)]


def _codes(count: int, name: str) -> "list[str]":
    draw = random.Random(name)
    letters = "qxzjkvw"
    return ["".join(draw.choice(letters) for _place in range(6)) + "#" + str(place) for place in range(count)]


# (name, a column no two cells of which hold one value, the same column with a
# few repeats and still over the uniqueness line, the role, the forms): the
# review's counts, and the three other roles that print the sentence.
_UNIQUE_AND_NEARLY = (
    ("counts", [str(value) for value in range(1101)], _review_item_5(), taxonomy.ROLE_COUNT),
    ("counts_spelled_twice", [str(value) for value in range(1, 400)], [str(value) for value in range(1, 399)] + ["0398"], taxonomy.ROLE_COUNT),
    ("affixed", [f"{value} mg" for value in range(300)], [f"{value} mg" for value in range(296)] + ["5 mg"] * 4, taxonomy.ROLE_AFFIXED),
    ("clock", _minutes(900, "p4d357/clock"), _minutes(890, "p4d357/clock") + _minutes(890, "p4d357/clock")[:10], taxonomy.ROLE_CLOCK),
    ("text", _codes(300, "p4d357/codes"), _codes(292, "p4d357/codes") + _codes(292, "p4d357/codes")[:8], taxonomy.ROLE_TEXT),
    # Every cell different as written, two alike once folded: the second
    # review's case, where the sentence's own "as folded" clause decides.
    ("text_alike_as_folded", _codes(300, "p4d357/folded"), _codes(299, "p4d357/folded") + [_codes(299, "p4d357/folded")[0].upper()], taxonomy.ROLE_TEXT),
)


@pytest.mark.parametrize(
    "name,unique,nearly,role", _UNIQUE_AND_NEARLY, ids=[case[0] for case in _UNIQUE_AND_NEARLY]
)
def test_the_all_different_sentence_is_printed_only_where_every_value_differs(
    name: str, unique: "list[str]", nearly: "list[str]", role: str
) -> None:
    """The exact sentence where no two cells hold one value; the near one, with no count, where some do.

    On 2af1f03 both columns of each pair printed "every value in this
    column is different": the line is `identifier_uniqueness`, 0.95 of the
    present cells, and the review's 1,101 counts hold `1089` eight times
    and `1093` twice. `0398` beside `398` is two spellings of one number;
    `5 mg` five times, ten clock times twice and eight codes twice are the
    other roles' repeats, and one code beside itself in capitals is two
    cells alike only as folded. Each near column is still over the line
    (premise), so it is told the near sentence.
    """
    for values, exact in ((unique, True), (nearly, False)):
        described_role, said = _said(values)
        assert described_role == role, f"premise: {name} read as {described_role}"
        assert len(said) == 1, f"{name}: {said}"
        if exact:
            assert said[0].startswith(_EVERY), f"{name}: {said[0][:80]}"
        else:
            assert said[0].startswith(_NEARLY), f"{name}: the near column was told {said[0][:80]!r}"
            assert not [one for one in said[0].split(".") if "shared" in one and any(ch.isdigit() for ch in one)], (
                "the near sentence names no count"
            )


# -- the second review: a stand-in the column keeps is its own value ----------


def _kept_published(block: "dict") -> "dict[float, int]":
    """The stand-ins a block's decisions publish as kept numbers, with their rows."""
    return {
        float(entry["candidate"]): entry["n_occurrences"]
        for entry in block["sentinel_verdicts"]
        if entry["verdict"] == "kept_as_a_number"
    }


def _held_heaps() -> "tuple[tuple[str, list[str]], ...]":
    """Seeded columns holding a stand-in in a heap the outlier rule keeps as a number."""
    bimodal = random.Random("p4d357/held/bimodal")
    tenths = random.Random("p4d357/held/tenths")
    whole = random.Random("p4d357/held/m9999")
    cents = random.Random("p4d357/held/cents")
    dosed = random.Random("p4d357/held/affixed/40")
    return (
        (
            "dense_bimodal",
            [str(round(bimodal.gauss(10000.0, 5.0))) for _row in range(600)]
            + [str(round(bimodal.gauss(-1000.0, 5.0))) for _row in range(600)],
        ),
        ("tenths_around_minus_999", [f"{tenths.gauss(-999.0, 0.5):.1f}" for _row in range(1000)]),
        ("integers_around_minus_9999", [str(whole.randint(-10050, -9950)) for _row in range(2000)]),
        (
            "prices_in_cents",
            [str(cents.choice((499, 999, 1499, 1999, 2999, 4999, 9999, 9999, 12999))) for _row in range(900)]
            + [str(cents.randint(100, 15000)) for _row in range(300)],
        ),
        # An affixed column, whose decisions are about its cores.
        ("affixed_mg_around_9999", [f"{round(dosed.gauss(9999.0, 40.0))} mg" for _row in range(2000)]),
    )


def _core(cell: str) -> float:
    """The number a cell of `_HELD_HEAPS` holds, its unit taken off."""
    return float(cell[: len(cell) - 3] if cell.endswith(" mg") else cell)


_HELD_HEAPS = _held_heaps()


@pytest.mark.parametrize("name,cells", _HELD_HEAPS, ids=[case[0] for case in _HELD_HEAPS])
def test_a_stand_in_the_column_keeps_comes_back_near_its_published_rows(
    tmp_path: pathlib.Path, name: str, cells: "list[str]"
) -> None:
    """A heap published `kept_as_a_number` is written, near its published rows, at seeds 0, 4 and 9.

    PREMISE: every stand-in the column holds is published kept, with its
    rows, at a floor of eleven, and the loader reads it so. The published
    decision names the value and its count, so writing it reveals nothing
    the description does not. On 7a70fad every value pass refused the three
    as points no row holds and no check noticed: 1,200 whole numbers around
    `-1000` and `10000` holding `-999` 44 times and `9999` 47 times came
    back holding neither, and a price column in cents holding `9999` 196
    times held none from 2af1f03 on (d93fd43 wrote 183). The twin now holds
    each within a quarter of its published rows or one percent of the
    numbers, a rung's worth, whichever is more, and misses nothing.
    """
    described = kpi_shapes.describe(tmp_path, name, _one_column(cells), 11)
    block = described.document["columns"][0]
    kept = _kept_published(block)
    held = {one: len([cell for cell in cells if _core(cell) == one]) for one in _STAND_INS}
    assert kept and kept == {one: rows for one, rows in held.items() if rows}, (
        f"premise: every stand-in held is published kept ({kept} against {held})"
    )
    assert min(kept.values()) >= 11, "premise: each heap is over the floor"
    facts = described.loaded.columns[0].facts
    if isinstance(facts, contract.AffixedFacts):
        facts = facts.numbers
    assert isinstance(facts, contract.NumericFacts)
    assert facts.kept_stand_ins == tuple(one for one in _STAND_INS if one in kept), (
        f"the loader reads {facts.kept_stand_ins}"
    )
    numbers = block["n_used_in_statistics"]
    for seed in (0, 4, 9):
        text = kpi_shapes.twin_text(described, seed)
        written = [_core(line) for line in text.split("\n")[1:] if line]
        for one, rows in kept.items():
            got = len([value for value in written if value == one])
            assert abs(got - rows) <= max(rows // 4, numbers // 100), (
                f"seed {seed}: {one} is published kept in {rows} rows and the twin holds it in {got}"
            )
        missed = kpi_shapes.missed(kpi_shapes.measure(described, text, f"twin-{seed}.csv"))
        assert missed == [], f"seed {seed}: {missed}"


def test_a_stand_in_held_below_the_floor_is_still_refused(tmp_path: pathlib.Path) -> None:
    """Three rows of `-999` among 600 whole numbers publish no decision, and the twin writes it in no cell."""
    draw = random.Random("p4d357/held/below")
    cells = [str(draw.randint(-1100, -900)) for _row in range(600)]
    assert 0 < len([cell for cell in cells if cell == "-999"]) < 11, "premise: held, below the floor"
    described = kpi_shapes.describe(tmp_path, "below", _one_column(cells), 11)
    block = described.document["columns"][0]
    assert block["sentinel_verdicts"] == [] and block["n_sentinel_candidates_unpublished"] == 1, (
        "premise: the decision is counted, not named"
    )
    facts = described.loaded.columns[0].facts
    assert isinstance(facts, contract.NumericFacts) and facts.kept_stand_ins == ()
    for seed in (0, 4, 9):
        text = kpi_shapes.twin_text(described, seed)
        written = [float(line) for line in text.split("\n")[1:] if line]
        assert -999.0 not in written, f"seed {seed}: the twin wrote a stand-in no decision names"
        assert kpi_shapes.missed(kpi_shapes.measure(described, text, f"twin-{seed}.csv")) == []


def test_the_loader_reads_the_kept_stand_ins_off_the_published_decisions() -> None:
    """Only a `kept_as_a_number` decision about one of the three numbers names a kept stand-in."""

    def decision(candidate: str, verdict: str) -> contract.SentinelVerdict:
        return contract.SentinelVerdict(
            candidate=candidate, verdict=verdict, reason="not_an_outlier", n_occurrences=20, spellings=()
        )

    kept = "kept_as_a_number"
    decisions = (
        decision("-9999", contract.VERDICT_MISSING),
        decision("-999", kept),
        decision("9999", kept),
        decision("1900-01-01", kept),
    )
    assert contract._kept_stand_ins(decisions) == (-999.0, 9999.0)
    assert contract._kept_stand_ins(decisions[:1]) == ()


def _refused_and_kept() -> "dict[str, tuple[object, object, object]]":
    """Per value pass: its answer with the stand-in refused, with it kept, and the oracle's with it kept (or None)."""
    import types

    from synthtwin import generation

    oracle = _oracle()
    every = tuple(_STAND_INS)
    written = {generation._grid_text(9997.0, 0): 1, generation._grid_text(9998.0, 0): 2}
    held = {-(tenths / 10): 1 for tenths in range(1, 9990)}
    signed = (-2000.0,) + (0.0,) * 99 + (5.0,)
    three = types.SimpleNamespace(bands=["positive"] * 3)
    cleared = (
        (-2000.0, 0.0), {}, (0, 0), (-999.0, -500.0), ((-999.0, -500.0),), -900.0,
        "negative", True, {}, {-900.0: 1}, True, (-1,),
    )
    tenths = [9998.0 + step / 10 for step in range(21)]
    twenty_one = types.SimpleNamespace(bands=["positive"] * 21, sizes=[1] * 21)
    tenths_ladder = (9998.0,) + (9999.0,) * 99 + (10000.0,)
    five = types.SimpleNamespace(bands=["positive"] * 5, sizes=[1] * 5)
    five_ladder = (9997.0,) + (9998.0,) * 99 + (10001.0,)
    draw_ladder = (-1049.0,) + (-999.0,) * 99 + (-949.0,)

    def twice(kept: "tuple[float, ...]") -> object:
        facts = types.SimpleNamespace(
            n_distinct_values=21, empty_edges=(), integer_valued=False,
            numeric_styles={"decimal": 21}, kept_stand_ins=kept,
        )
        return generation._twice_filled(facts, twenty_one, tenths_ladder, tenths, 1)  # type: ignore[arg-type]

    def saturated(kept: "tuple[float, ...]") -> object:
        facts = types.SimpleNamespace(n_distinct_values=5, kept_stand_ins=kept)
        return generation._saturated_integers(
            five, five_ladder, [9997.0, 9998.0, 9998.0, 10000.0, 10001.0], 0, facts  # type: ignore[arg-type]
        )

    return {
        "carrier walk": (
            generation._whole_inside(-999.3, "negative", (-1000.0, -998.0), (-2000.0, 0.0), 10, {}),
            generation._whole_inside(-999.3, "negative", (-1000.0, -998.0), (-2000.0, 0.0), 10, {}, kept=every),
            oracle.whole_inside(-999.3, "negative", (-1000.0, -998.0), (-2000.0, 0.0), 10, {}, every),
        ),
        "separation walk": (
            generation._apart_inside(9998.0, 0, "positive", (9990.0, 10010.0), (0.0, 20000.0), written),
            generation._apart_inside(9998.0, 0, "positive", (9990.0, 10010.0), (0.0, 20000.0), written, kept=every),
            oracle.apart_inside(9998.0, 0, "positive", (9990.0, 10010.0), (0.0, 20000.0), written, kept=every),
        ),
        "sign step": (
            generation._grid_step_of_sign("negative", signed, 1, held, 10000),
            generation._grid_step_of_sign("negative", signed, 1, held, 10000, kept=every),
            oracle.grid_step_of_sign("negative", signed, 1, held, 10000, every),
        ),
        "representable grid": (
            generation._apart_on_the_representable_grid(three, [9998.0, 9999.0, 10000.0]),  # type: ignore[arg-type]
            generation._apart_on_the_representable_grid(three, [9998.0, 9999.0, 10000.0], kept=every),  # type: ignore[arg-type]
            oracle.representable_grid(3, ["positive"] * 3, [9998.0, 9999.0, 10000.0], every),
        ),
        "marks run": (
            generation._free_grid_points(9998, 1, 2, 0, {}),
            generation._free_grid_points(9998, 1, 2, 0, {}, kept=every),
            None,
        ),
        "clearing walk": (
            generation._cleared_value(*cleared),  # type: ignore[arg-type]
            generation._cleared_value(*cleared, kept=every),  # type: ignore[arg-type]
            None,
        ),
        "twice-written fill": (twice(()), twice(every), None),
        "push": (
            generation._band_step(9998, 1, 9990, 10010, 0, ()),
            generation._band_step(9998, 1, 9990, 10010, 0, (), kept=every),
            None,
        ),
        "band fill": (
            generation._band_points(9997, 10001, 0, (), 5),
            generation._band_points(9997, 10001, 0, (), 5, kept=every),
            None,
        ),
        "saturated fill": (
            saturated(()),
            saturated(every),
            oracle.saturated_grid(5, 0, 5, ["positive"] * 5, five_ladder, every),
        ),
        "width walk": (
            generation._figured_inside((9990.0, 10010.0), {}, "positive", 4, 10005.0, True),
            generation._figured_inside((9990.0, 10010.0), {}, "positive", 4, 10005.0, True, kept=every),
            None,
        ),
        "draw": (
            generation._drawn_off_the_stand_ins(-999.0, draw_ladder, 1, 2, 0),
            generation._drawn_off_the_stand_ins(-999.0, draw_ladder, 1, 2, 0, kept=every),
            oracle.drawn_off_the_stand_ins(-999.0, -1049.0, -949.0, 0, every),
        ),
    }


def _stand_ins_in(answer: object) -> "list[float]":
    """The stand-in numbers one answer holds, a point or a list of points (grid units read as numbers)."""
    found = answer if isinstance(answer, list) else [answer]
    return [float(one) for one in found if isinstance(one, (int, float)) and float(one) in _STAND_INS]


def test_every_value_pass_writes_a_stand_in_the_column_keeps() -> None:
    """Each refusal of item 2, asked with the stand-in kept: it is the pass's answer, in the oracle alike.

    Refused, each pass answers another point (the tests above); kept, the
    same call answers the stand-in, and where the oracle states the step it
    answers the same. The twelve are every place a value pass asks whether a
    point is one of the three.
    """
    for name, (refused, kept, theirs) in _refused_and_kept().items():
        assert _stand_ins_in(refused) == [], f"{name}: premise: refused, no stand-in ({refused!r})"
        assert _stand_ins_in(kept) != [], f"{name}: the kept stand-in was still refused ({kept!r})"
        if theirs is not None:
            assert theirs == kept, f"{name}: the generator answers {kept!r}, the oracle {theirs!r}"


# The value passes that ask a helper whether a point is a stand-in, by the
# helper each hands the column's kept stand-ins to.
_HANDED_KEPT = (
    "_drawn_off_the_stand_ins",
    "_grid_step_of_sign",
    "_whole_inside",
    "_rehomed",
    "_apart_inside",
    "_push_plan",
    "_band_step",
    "_band_points",
    "_apart_on_the_representable_grid",
    "_figured_inside",
    "_cleared_value",
)


def _handing_shapes() -> "tuple[tuple[str, int, list[str]], ...]":
    """Seeded columns holding a kept stand-in, which between them reach every pass of `_HANDED_KEPT`."""
    tenths = random.Random("p4d357/handed/tenths")
    edge = random.Random("p4d357/handed/edge")
    widths = random.Random("p4d357/handed/widths")
    pooled = random.Random("p4d357/handed/pooled")
    changes = random.Random("p4d357/handed/changes")
    return (
        # G5.4's draw on a grid of tenths, and the band fill.
        ("tenths_around_minus_999", 11, [f"{tenths.gauss(-999.0, 0.5):.1f}" for _row in range(1000)]),
        # The draw off a grid, the walk at its three reaches, the push, the
        # band fill, G6.6's width walk and G6.7's clearing walk.
        (
            "gap_at_the_edge_of_a_heap",
            11,
            [str(edge.randint(-1400, -999)) for _row in range(500)]
            + [str(edge.randint(-500, -1)) for _row in range(500)]
            + ["-999"] * 30,
        ),
        # G6.4's carrier walk and its trades, beside five widths.
        (
            "five_widths_around_minus_999",
            11,
            [repr(round(widths.gauss(-999.0, 2.0), widths.choice((2, 3, 4, 5, 6)))) for _row in range(600)]
            + ["-999"] * 20,
        ),
        # Widths each held below the floor: the representable grid.
        (
            "pooled_widths_around_minus_999",
            36,
            [f"{pooled.gauss(-999.0, 5.0):.{pooled.randint(1, 6)}f}" for _row in range(150)] + ["-999"] * 40,
        ),
        # Changes at two places beside a rare kept heap: G5.5's grid step of sign.
        ("changes_beside_a_rare_heap", 11, [f"{changes.gauss(0.2, 0.6):.2f}" for _row in range(3000)] + ["-999.00"] * 12),
    )


def test_every_value_pass_is_handed_the_stand_ins_the_column_keeps(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Every call a value pass makes to a refusing helper carries the column's kept stand-ins.

    The helpers' own answers are held above; this holds the threading, which
    no seeded heap's count can: where one pass refuses a kept stand-in another
    often puts the heap back, so a pass handed nothing left the counts near
    their published rows. PREMISE: each column keeps a stand-in, and between
    them the columns reach every helper of `_HANDED_KEPT`, at seeds 0, 4 and 9.
    """
    from synthtwin import generation

    handed: "list[tuple[str, object]]" = []

    def spied(name: str) -> object:
        shipped = getattr(generation, name)

        def spy(*arguments: object, **named: object) -> object:
            handed.extend([(name, named.get("kept", "not handed"))])
            return shipped(*arguments, **named)

        return spy

    for name in _HANDED_KEPT:
        monkeypatch.setattr(generation, name, spied(name))
    reached: "set[str]" = set()
    for shape, floor, cells in _handing_shapes():
        described = kpi_shapes.describe(tmp_path / shape, shape, _one_column(cells), floor)
        facts = described.loaded.columns[0].facts
        assert isinstance(facts, contract.NumericFacts) and facts.kept_stand_ins, f"premise: {shape} keeps a stand-in"
        for seed in (0, 4, 9):
            handed.clear()
            kpi_shapes.twin_text(described, seed)
            wrong = [(name, kept) for name, kept in handed if kept != facts.kept_stand_ins]
            assert wrong == [], f"{shape} at seed {seed}: handed {wrong[:4]} against {facts.kept_stand_ins}"
            reached = reached | {name for name, _kept in handed}
    assert reached == set(_HANDED_KEPT), f"premise: never reached {sorted(set(_HANDED_KEPT) - reached)}"
