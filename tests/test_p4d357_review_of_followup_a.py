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
        n_distinct_values=21, empty_edges=(), integer_valued=False, numeric_styles={"decimal": 21}
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
