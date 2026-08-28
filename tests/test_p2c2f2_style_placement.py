"""Review item P2-C2-F2: a placeable numeric form is PLACED, not reported.

Owner decision 10 makes the form of every numeric cell a published
fact, and the contract calls `numeric_styles` EXACT-OBSERVABLE. Round 2
found the generator choosing a style from the remaining quota and the
sign alone, without asking whether the finished text would read back as
that style. On a column publishing `integer_valued: false` the
canonical spelling of the whole value `100` is `100.0`, which the
contract's own ladder counts as `decimal`, so a genuine input of eleven
fractions and forty whole numbers published forty `plain` cells and the
twin wrote none -- naming both misses, which the item refused: the
source's own values prove the exact map is reachable.

WHAT THIS FILE HOLDS THE REPAIR TO:

1. the point-free spelling of a whole value exists and reads back as
   exactly that value, and the styles that need one are offered only to
   cells that have one;
2. the values step puts whole values where the published map needs
   them, and never at the cost of `n_zero`, `n_negative` or the count of
   different values;
3. the look-ahead keeps a quota placeable to the end of the column,
   which is what makes the map come out exactly rather than nearly;
4. the map that genuinely cannot be placed is still named -- the repair
   removes the excuse, not the report.

The descriptions are built by the REAL producer from seeded neutral
tables, so what is exercised is the path from table to twin.
"""

import pathlib

import fixtures
from synthtwin import (
    contract,
    generation,
    parsing,
    profile,
    reading,
    taxonomy,
)


# The publication floor these fixtures were counted against. A floor of
# one became the default under the owner ruling recorded as plan
# amendment A-P4-37 -- contract invariant C5-S13 says that at a floor of
# one nothing whatever is held back -- and pooling is a SUBJECT here:
# the counts below are the counts a description publishes when a form
# carried by fewer than eleven cells is pooled into `(withheld)`. So the
# floor is stated rather than inherited, and it is the eleven every
# docstring in this file counts against.
SMALL_CELL_FLOOR = 11


def _described(
    folder: pathlib.Path, values: "list[str]"
) -> "tuple[dict, contract.Profile]":
    """Write a one-column table, describe it, load the description."""
    path = fixtures.write(
        folder, "table.csv", fixtures.single_column_table("amount", values)
    )
    table = reading.read_table(str(path))
    document = profile.build_document(
        table, taxonomy.Settings(small_cell_floor=SMALL_CELL_FLOOR), []
    )
    target = fixtures.write_profile(folder, "table-profile.json", document)
    return document, contract.load_profile(str(target))


def _styles(twin: generation.Twin) -> "dict[str, int]":
    """The form of every numeric cell, read off the contract's own ladder."""
    counted: dict[str, int] = {}
    for cell in twin.columns[0]:
        if cell == "" or parsing.classify_number(cell) != parsing.NUMBER:
            continue
        style = parsing.numeric_style(cell)
        counted[style] = counted.get(style, 0) + 1
    return counted


# -- 1. the point-free spelling ---------------------------------------


def test_a_whole_value_has_a_point_free_spelling_that_reads_back() -> None:
    """Point 1: the spelling exists, and it is the same number.

    A style that changes the value would be worse than a style that was
    missed, so every point-free spelling is read back through the
    shipped number reader and compared to the value it came from.
    """
    for value in (0.0, -0.0, 5.0, -12.0, 100.0, 1e15):
        written = generation._point_free(
            value, generation._canonical_number(value, False)
        )
        assert "." not in written
        assert "e" not in written and "E" not in written
        assert parsing.parse_number(written) == value
        assert parsing.numeric_style(written) in ("plain", "leading_zero")
    assert generation._point_free(
        -0.0, generation._canonical_number(-0.0, False)
    ) == "0"


def test_a_value_with_no_point_free_spelling_is_not_offered_one() -> None:
    """The other half of point 1: the rule refuses what it cannot write.

    A value that is not whole has no spelling without a point, so it may
    wear none of the three styles that need one. `12.5`, `1e-05` and
    `-2.5` are those values.

    A WHOLE VALUE HAS ONE AT ANY WIDTH (owner decision 10, 2026-08-13).
    This test used to put `1e+16` on the refusing side, because the
    contract's fixed-point window stops there -- but that window governs
    the canonical spelling of a number in the profile document, not the
    spelling of a plain cell in the twin, and a whole value's full digit
    expansion reads back exactly however wide it is. So the wide whole
    numbers move to the side that CAN be written plainly, which is what
    stops a column of them from coming back as a decimal one.
    """
    for value in (12.5, 1e-05, -2.5):
        assert not generation._carries_plainly(value, False)
    for value in (0.0, 5.0, 1e15, 1e16, 1e20):
        assert generation._carries_plainly(value, False)


# -- 2 and 3. the case round 2 named ----------------------------------


def test_the_feasible_style_map_of_the_reviewed_column_comes_out_exactly(
    tmp_path: pathlib.Path,
) -> None:
    """Points 2 and 3, on the genuine input the item names.

    Eleven values carrying a point and forty whole ones publish forty
    `plain` cells and eleven `decimal` ones. The twin used to write
    nought and fifty-one. It now writes forty and eleven, so nothing
    about the map reaches the report -- and the forty cells a pattern
    check would read as whole numbers are whole numbers.
    """
    values = [f"{n}.5" for n in range(1, 12)] + [
        str(100 + n) for n in range(40)
    ]
    document, loaded = _described(tmp_path, values)
    assert document["columns"][0]["numeric_styles"] == {
        "plain": 40, "decimal": 11,
    }
    assert document["columns"][0]["integer_valued"] is False

    twin = generation.generate(loaded, 0)
    assert _styles(twin) == {"plain": 40, "decimal": 11}
    assert [
        note for note in twin.deviations if note.fact == "numeric_styles"
    ] == []


def test_the_values_step_never_moves_a_cell_across_zero(
    tmp_path: pathlib.Path,
) -> None:
    """Point 2's guard: the sign and zero counts are not traded for a form.

    A column whose values straddle zero with a `plain` quota could have
    a stratum rounded onto zero, which would move a cell out of the
    negative count and into the zero count -- two EXACT-OBSERVABLE facts
    traded for one. The rule leaves such a stratum alone, and this
    recounts both facts on the finished cells.
    """
    values = (
        [f"-0.{n}" for n in range(1, 10)]
        + [f"0.{n}" for n in range(1, 10)]
        + [str(n) for n in range(1, 21)]
        + ["0"] * 5
    )
    _document, loaded = _described(tmp_path, values)
    block = loaded.columns[0]
    facts = block.facts
    assert isinstance(facts, contract.NumericFacts)
    assert facts.n_negative > 0 and facts.n_zero > 0

    twin = generation.generate(loaded, 0)
    numbers = [
        parsing.parse_number(cell)
        for cell in twin.columns[0]
        if cell != "" and parsing.classify_number(cell) == parsing.NUMBER
    ]
    assert len([value for value in numbers if value is not None and value < 0]) == (
        facts.n_negative
    )
    assert len([value for value in numbers if value == 0.0]) == facts.n_zero
    assert [
        note for note in twin.deviations
        if note.fact in ("n_zero", "n_negative")
    ] == []


def test_a_column_with_no_point_free_style_keeps_its_values_untouched(
    tmp_path: pathlib.Path,
) -> None:
    """The vacuity floor under point 2: no demand, no rounding.

    A column publishing only `decimal` cells asks for no point-free
    form, so no stratum is taken to a whole number and the rung window
    keeps the tighter half unit it had.
    """
    values = [f"{n}.25" for n in range(1, 41)]
    document, loaded = _described(tmp_path, values)
    assert set(document["columns"][0]["numeric_styles"]) == {"decimal"}
    block = loaded.columns[0]
    facts = block.facts
    assert isinstance(facts, contract.NumericFacts)
    assert generation._whole_demand(facts) == 0

    twin = generation.generate(loaded, 0)
    written = [cell for cell in twin.columns[0] if cell != ""]
    assert _styles(twin) == {"decimal": len(written)}


# -- 4. the miss that remains is still named --------------------------


def test_a_style_with_nowhere_to_go_is_still_named(
    tmp_path: pathlib.Path,
) -> None:
    """Point 4: the repair removes the excuse, not the report.

    THE FIXTURE THIS TEST USED TO CARRY WAS THE DEFECT (review item
    P2-C4-F3). It was the 51-cell column of eleven `1.5`, twenty `100`
    and twenty `200.5`, whose published map of twenty `plain` cells the
    source's OWN values prove -- and this test required the twin to
    miss it, on the reasoning that the stratum between the two ends
    covered too few cells. How many cells a stratum covers is the
    twin's own choice, not a published fact, so that was a miss the
    generator chose. It is now placed exactly, and this test's fixture
    is a column where the arithmetic really does run out.

    AND THE FIXTURE MOVED AGAIN, because the Phase 3 plan repaired the
    shape it had been moved to (P3-D8.1, closing the registry's open
    P2-C5-F3). That shape was a producer column of forty named `plain`
    cells and six pooled ones whose published ends carry points: under
    the withdrawn rule every pooled cell was owed the plain form, which
    the two end cells have no spelling for, so the twin was required to
    miss a total no generator could reach. A pooled cell has no
    published form, so it is now spelled by its own value and nothing
    is missed there. What is left for this test is a NAMED count with
    nowhere to go, which a producer cannot emit and a hand-written
    description can: forty-six `leading_plus` cells on a column two of
    whose cells must read back as numbers with no point-free spelling
    at all. That miss is the twin's to name, and it names it.
    """
    values = ["0.5"] * 3 + ["7"] * 40 + ["9.25"] * 3
    document, loaded = _described(tmp_path, values)
    assert document["columns"][0]["numeric_styles"] == {
        "plain": 40, "(withheld)": 6,
    }

    twin = generation.generate(loaded, 0)
    written = _styles(twin)
    assert written == {"plain": 44, "decimal": 2}
    named = [note for note in twin.deviations if note.fact == "numeric_styles"]
    assert named == [], [note.published for note in named]

    document["columns"][0]["numeric_styles"] = {"leading_plus": 46}
    # The census of widths moves with the forms map, because P5 ties the
    # two together: a map that names no `decimal` cells is a map whose
    # census names no width, and a hand-edited document that kept the
    # old census would be refused at the door instead of reaching the
    # placement this test is about.
    document["columns"][0]["fraction_widths"] = {}
    target = fixtures.write_profile(tmp_path, "edited-profile.json", document)
    edited = contract.load_profile(str(target))
    twin = generation.generate(edited, 0)
    written = _styles(twin)
    assert written.get("leading_plus", 0) == 44
    named = [note for note in twin.deviations if note.fact == "numeric_styles"]
    assert named, "a named count with nowhere to go must be spoken"
    assert any("leading_plus" in note.published for note in named), [
        note.published for note in named
    ]


def test_the_placement_rule_refuses_a_style_the_cell_cannot_wear() -> None:
    """The look-ahead and the feasibility filter, on the shipped function.

    Two cells, one whole and one not, against a `plain` quota of one and
    a `decimal` quota of one. Largest-remaining alone spends the whole
    cell on `decimal` -- the tie goes to `plain` by enumeration order,
    but a cell that cannot wear `plain` must not take it either -- and
    the quota then arrives at a cell with no point-free spelling. The
    look-ahead is what puts the plain cell where it can be written.
    """
    quotas = {name: 0 for name in contract.NUMERIC_STYLES}
    quotas["plain"] = 1
    quotas["decimal"] = 1
    assert generation._style_places(quotas, [5.0, 2.5], False) == [
        "plain", "decimal",
    ]
    assert generation._style_places(quotas, [2.5, 5.0], False) == [
        "decimal", "plain",
    ]
