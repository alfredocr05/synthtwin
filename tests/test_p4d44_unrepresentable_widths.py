"""P4-D4.4: the unholdable column's two widths, and staying unholdable.

The `numeric_unrepresentable` role publishes `min_length` and
`max_length` -- the character counts of the narrowest and widest
numeric-looking cell in the real table -- and the generator writes
within that window instead of writing every such column at one made-up
400-figure canonical width. That closes residual R-P2-1: two columns of
overflowing values, one about 400 characters wide and one about 4,000,
used to describe identically, so code that measures how wide the
written values are read a different answer on the twin than on the real
table.

**THE THING THIS FILE EXISTS TO STOP is a twin that meets the published
widths by writing values the format CAN hold.** A column of this role
says its values are outside binary64. A twin of it whose cells are
inside binary64 is not a narrower version of that column; it is a
DIFFERENT KIND of column, and every piece of code that dispatches on
the type meets something else. Width fidelity is worth having and it is
worth strictly less than that, so where the two conflict the twin stays
unholdable, comes out wider than the published width, and the recount
names the width it missed.

**WHAT THE FIRST TEST PINS, AND WHAT IT DOES NOT.** The fraction
spelling is `0.`, a run of zeros, and a figure body -- and the figure
body GROWS as the walk enumerates distinct values (`1`, `2`, ... `9`,
`10`, `11`). Sizing the zero run as "whatever is left of the asked
width" therefore SHRINKS it as the body grows, and the value climbs
back up: written at 327 characters, the twenty-fifth distinct fraction
comes out 5e-324, the smallest subnormal there is. The zero run now
takes a floor of its own, measured -- the largest figure body of every
length from one to six digits underflows behind 324 zeros, and behind
323 none of them does.

**THIS FILE FIRST SAID THAT STATE WAS UNREACHABLE, AND IT WAS WRONG.**
The claim rested on a randomised trial over 300 built columns holding
at most 40 distinct values each, in which the too-small spelling never
reached an index that mattered. Such a trial shows a defect present and
never shows one absent, and the shape it does not build is the shape it
tells you nothing about. A reviewer supplied that shape: 271
distinct fractions at widths 327 and 328, which a real table can hold
perfectly well. Without the zero-run floor, that column's twin holds 48
cells binary64 CAN represent against a published count of zero, and
reprofiles with `n_out_of_range` down from 542 to 494.

Both tests below are therefore kept and both are mutation-sensitive:
one on the SPELLING, which is where the guarantee belongs, and one on
the reviewer's whole column, which is what a person meets.
"""

import csv
import importlib.util
import math
import pathlib

import fixtures
from synthtwin import (
    contract,
    generation,
    parsing,
    profile,
    reading,
    taxonomy,
    validation,
)


def _round_trip(
    folder: pathlib.Path, name: str, values: "list[str]"
) -> "tuple[dict, list[str], dict, list[generation.Deviation]]":
    """Describe a column, build its twin, and describe the twin again."""
    table = folder / f"{name}.csv"
    with table.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["reading"])
        for value in values:
            writer.writerow([value])
    document = profile.build_document(
        reading.read_table(f"{table}"), taxonomy.Settings(), []
    )
    written = fixtures.write_profile(folder, f"{name}-profile.json", document)
    twin = generation.generate(contract.load_profile(f"{written}"), 5)
    twin_table = folder / f"{name}-twin.csv"
    with twin_table.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["reading"])
        for cell in twin.columns[0]:
            writer.writerow([cell])
    again = profile.build_document(
        reading.read_table(f"{twin_table}"), taxonomy.Settings(), []
    )
    return (
        document["columns"][0],
        [cell for cell in twin.columns[0] if cell],
        again["columns"][0],
        list(twin.deviations),
    )


def _holdable(cells: "list[str]") -> "list[str]":
    """Every cell of the twin this file format CAN hold."""
    held: list[str] = []
    for cell in cells:
        value = float(cell)
        if math.isinf(value):
            continue
        if value == 0.0:
            continue
        held = held + [cell]
    return held


def test_the_fraction_spelling_is_unholdable_at_every_index(
    tmp_path: pathlib.Path,
) -> None:
    """THE SPELLING'S OWN GUARANTEE, at the width where it is tightest.

    Asked for the floor width, every distinct fraction the walk can
    enumerate must still be a value binary64 cannot hold -- including
    the ones whose figure body has grown to two and three characters,
    which is what eats the zero run. Removing the zero-run floor turns
    this red at the twenty-fifth spelling.

    This is asserted on the spelling rather than on a round trip
    because no description reaches that state through the generator:
    only nine distinct unholdable fractions fit at the floor width. See
    this module's docstring for the measurement.
    """
    states: "dict[str, list[int]]" = {}
    used: "dict[str, int]" = {}
    width = generation._UNDERFLOW_PLACES
    holdable: list[str] = []
    for _index in range(60):
        spelling = generation._wide_number(
            2, False, states, used, (), width
        )
        assert spelling is not None
        value = float(spelling)
        if not (math.isinf(value) or value == 0.0):
            holdable = holdable + [spelling]
    assert holdable == [], (
        "the fraction spelling produced values this file format can "
        f"hold: {[cell[:12] + '...' for cell in holdable[:3]]}"
    )


def test_the_reviewers_column_holds_its_published_class_counts(
    tmp_path: pathlib.Path,
) -> None:
    """THE COLUMN A SWEEP OF 300 DID NOT CONTAIN (item P4-G3-R5-F1).

    271 distinct fractions across two widths, every one of them below
    the smallest subnormal. The walk enumerates far enough that the
    figure body reaches three characters, which is what eats the zero
    run. Without the floor this twin holds 48 representable cells
    against a published zero.

    **THE PUBLISHED `max_length` IS HELD NOW, and this docstring said
    the opposite until method G10.5 revision 5** (residuals R-P4-48 and
    R-P4-68). It said the trade this whole file is about had to be
    made here -- that holding the width would mean writing a value this
    format can hold, so the twin came out one character wider and the
    report named it. That was true of a walk with ONE spelling family.
    Measured before and after on this column: twin widths 327, 328 and
    329 with a `max_length` deviation, against 327 and 328 with no
    deviation at all, 48 of its cells written by the exponent family.
    The trade is real and it is now made only where neither family can
    write the asked width.
    """
    values: list[str] = []
    for figure in range(1, 25):
        values = values + ["0." + f"{figure}".zfill(325)] * 2
    for figure in range(1, 248):
        values = values + ["0." + f"{figure}".zfill(326)] * 2
    source, cells, again, notes = _round_trip(tmp_path, "deep", values)
    assert source["role"] == taxonomy.ROLE_UNREPRESENTABLE
    assert source["n_distinct"] == 271
    assert source["n_numeric"] == 0
    assert _holdable(cells) == []
    # THE CLASS COUNTS, which is what the defect actually cost.
    assert again["n_out_of_range"] == source["n_out_of_range"]
    assert again["n_numeric"] == 0
    assert again["role"] == taxonomy.ROLE_UNREPRESENTABLE
    # AND BOTH PUBLISHED WIDTHS ARE HELD, unconditionally. This read
    # `if longest != max_length: assert the deviation is named`, which
    # was a fair shape while the width could not be met and became a
    # check that cannot fail the moment it could: the branch stopped
    # being taken and the test went on passing.
    assert sorted({len(cell) for cell in cells}) == [
        source["min_length"], source["max_length"]
    ]
    assert [note.fact for note in notes] == []
    # 48 of them come from the second spelling family, which is what
    # made the difference: the digit string cannot say these values at
    # this width without a zero more than the width allows.
    assert len([cell for cell in cells if "e" in cell]) == 48


def test_a_column_of_many_fractions_keeps_its_kind(
    tmp_path: pathlib.Path,
) -> None:
    """And the round trip a person actually meets, on thirty of them."""
    values: list[str] = []
    for index in range(30):
        values = values + ["0." + "0" * 400 + f"{index + 1}"] * 8
    source, cells, again, _notes = _round_trip(tmp_path, "tiny", values)
    assert source["role"] == taxonomy.ROLE_UNREPRESENTABLE
    assert source["n_distinct"] == 30
    assert _holdable(cells) == []
    assert again["role"] == taxonomy.ROLE_UNREPRESENTABLE
    assert again["n_numeric"] == 0


def test_both_published_widths_are_held_where_the_shapes_allow(
    tmp_path: pathlib.Path,
) -> None:
    """The window is carried at BOTH ends, not merely respected at one.

    `min_length` is the width of the narrowest value in your table, not
    a floor the twin may sit above. An earlier revision tested only
    `shortest < min_length` and so passed a column published at 250
    whose twin started at 310.
    """
    values = ["9" * 320] * 120 + ["1" * 400] * 120
    source, cells, again, notes = _round_trip(tmp_path, "window", values)
    assert source["role"] == taxonomy.ROLE_UNREPRESENTABLE
    assert (source["min_length"], source["max_length"]) == (320, 400)
    assert (again["min_length"], again["max_length"]) == (320, 400), (
        "the twin does not hold the two widths its description publishes"
    )
    assert not [note for note in notes if note.fact == "min_length"]
    assert not [note for note in notes if note.fact == "max_length"]


def test_a_width_the_shapes_cannot_reach_is_named_and_not_faked(
    tmp_path: pathlib.Path,
) -> None:
    """Where the twin cannot hold a published width, it SAYS so.

    A value narrow enough for this format to hold is a value of another
    kind, so the twin stays wide and the recount names the width it
    missed. A run that quietly wrote the published width instead would
    be the R-P2-1 defect again with the numbers rearranged.
    """
    # Every cell here is a fraction below the smallest subnormal, so
    # every group takes a shape with a floor of its own; the published
    # floor is narrower than any of them can be written at.
    values = ["0." + "0" * 330 + "7"] * 100 + ["0." + "0" * 400 + "3"] * 100
    source, cells, _again, notes = _round_trip(tmp_path, "unreachable", values)
    assert source["role"] == taxonomy.ROLE_UNREPRESENTABLE
    assert _holdable(cells) == []
    shortest = min(len(cell) for cell in cells)
    named = {note.fact for note in notes}
    if shortest != source["min_length"]:
        assert "min_length" in named, (
            f"the twin's narrowest cell is {shortest} characters against a "
            f"published {source['min_length']} and nothing said so"
        )
    longest = max(len(cell) for cell in cells)
    if longest != source["max_length"]:
        assert "max_length" in named


def test_no_width_miss_is_ever_silent(tmp_path: pathlib.Path) -> None:
    """Across a spread of shapes: every miss is named, on both ends.

    A check that cannot fail is a defect, and the point of this one is
    that it walks columns whose shapes DO conflict with their published
    widths beside ones that do not.
    """
    shapes = [
        (["9" * 320] * 120 + ["1" * 400] * 120, "wholes"),
        (["9" * 400] * 100 + ["0." + "0" * 398 + "1"] * 100, "mixed"),
        (["-" + "9" * 400] * 100 + ["1" * 380] * 100, "signed"),
        (["9" * 320] * 240, "uniform"),
    ]
    for index in range(len(shapes)):
        values, name = shapes[index]
        source, cells, _again, notes = _round_trip(tmp_path, name, values)
        assert source["role"] == taxonomy.ROLE_UNREPRESENTABLE, name
        named = {note.fact for note in notes}
        shortest = min(len(cell) for cell in cells)
        longest = max(len(cell) for cell in cells)
        if shortest != source["min_length"]:
            assert "min_length" in named, name
        if longest != source["max_length"]:
            assert "max_length" in named, name
        assert _holdable(cells) == [], name


def test_a_fold_partner_does_not_eat_the_ceiling(
    tmp_path: pathlib.Path,
) -> None:
    """THE WIDTH-PINNED PARTNER CLAUSE (plan P4-D4.4, item P4-G3-R5-F4).

    A fold-collision partner is a respelling of a value already
    written, and while this role published no length at all its edge
    spacing was held to no window. Once both ends are published, a
    partner free of the window consumes the group the ceiling was
    assigned to: this column's parent lands at 310 and its partner used
    to land at 311, so no cell held the published 312.
    """
    base = "9" * 310
    values = [base] * 100 + [base + "  "] * 100
    source, cells, again, notes = _round_trip(tmp_path, "partner", values)
    assert source["role"] == taxonomy.ROLE_UNREPRESENTABLE
    assert (source["min_length"], source["max_length"]) == (310, 312)
    assert source["n_distinct"] == 2
    assert source["n_distinct_folded"] == 1, (
        "the fixture no longer collides, so it pins nothing"
    )
    assert (again["min_length"], again["max_length"]) == (310, 312), (
        "the partner is not being held to the width its group was asked "
        f"for: the twin holds {sorted({len(cell) for cell in cells})}"
    )
    assert not [note for note in notes if note.fact == "max_length"]


def test_a_collision_inside_one_width_keeps_its_fold(
    tmp_path: pathlib.Path,
) -> None:
    """THE SHAPE AN ARGUMENT OF MINE SAID COULD NOT EXIST.

    Pinning a fold partner to its group's width means a parent that
    already fills that width has no partner reachable by spacing, since
    spacing only LENGTHENS. I argued that could never bite here: a
    partner differs from its parent in case or in edge spacing, a
    numeral holds no letter, so every collision on this role is spacing
    -- which changes the width -- so a colliding column always
    publishes two different widths.

    **The last step is false, and a reviewer supplied the
    counterexample.** Spacing changes the width by the NUMBER of spaces
    and not by where they go, so `N + " "` and `" " + N` are two raw
    values of one width folding to one identity. Under the pin alone
    that column lost its fold: it published a folded count of 1 and its
    twin held 2, a published count given up to hold a width, which is
    the wrong way round.

    So the pin falls back to an open window, and this test pins the
    ORDER of the two: the fold is the obligation, the width is the
    preference, and the width that could not be held is named.
    """
    body = "9" * 310
    values = [body + " "] * 100 + [" " + body] * 100
    source, cells, again, notes = _round_trip(tmp_path, "onewidth", values)
    assert source["role"] == taxonomy.ROLE_UNREPRESENTABLE
    # The premise the old argument denied: one width, and a collision.
    assert source["min_length"] == source["max_length"]
    assert source["n_distinct"] == 2
    assert source["n_distinct_folded"] == 1, (
        "the fixture no longer collides, so it pins nothing"
    )
    # THE FOLD IS KEPT. This is the assertion that was failing.
    assert again["n_distinct_folded"] == 1, (
        "the twin gave up the published folded count to hold a width"
    )
    assert not [note for note in notes if note.fact == "n_distinct_folded"]
    # AND THE WIDTH IT COULD NOT HOLD IS NAMED, not faked.
    longest = max(len(cell) for cell in cells)
    if longest != source["max_length"]:
        assert "max_length" in {note.fact for note in notes}


def test_the_zero_run_is_no_wider_than_the_value_needs(
    tmp_path: pathlib.Path,
) -> None:
    """A FIXED UNDERFLOW FLOOR WRITES GOOD BODIES TOO WIDE (P4-G3-R6-F2).

    The zero run was a constant, 324, chosen as the point where the
    largest body of every length underflows. But what decides is the
    VALUE, so the figures decide it too: behind 323 zeros the body `10`
    underflows and the body `9` does not, and a six-figure body needs
    only 319. A floor high enough for the worst body therefore wrote
    every better one a character wider than the description asked, and
    this column -- ten fractions all exactly 327 characters -- came out
    holding a 328.

    The run now grows until the value underflows, asked of each
    spelling. Both halves are asserted: the width is held AND nothing
    became representable.
    """
    values: list[str] = []
    for figure in range(1, 10):
        values = values + ["0." + "0" * 324 + f"{figure}"] * 8
    values = values + ["0." + "0" * 323 + "10"] * 8
    source, cells, again, notes = _round_trip(tmp_path, "tenwide", values)
    assert source["role"] == taxonomy.ROLE_UNREPRESENTABLE
    assert source["min_length"] == source["max_length"] == 327
    assert _holdable(cells) == []
    assert sorted({len(cell) for cell in cells}) == [327], (
        "the zero run is wider than the value needs: the twin holds "
        f"{sorted({len(cell) for cell in cells})}"
    )
    assert not [note for note in notes if note.fact == "max_length"]


def test_a_fraction_with_no_leading_zero_can_carry_the_floor(
    tmp_path: pathlib.Path,
) -> None:
    """`.5` IS TWO CHARACTERS AND THIS FORMAT HOLDS IT (P4-G3-R6-F3).

    The in-range fraction shape wrote `1.5`, `2.5`, `3.5` behind a run
    of zeros, so the narrowest cell it could produce was three
    characters -- and the table of narrowest spellings said so. A
    column whose narrowest numeric-looking cell is the two characters
    `.5` therefore had no group able to carry its published floor and
    missed it. The parser accepts a fraction with no leading zero, so
    at two characters the body is the point and one figure.
    """
    values = [".5"] * 100 + ["9" * 310] * 100
    source, cells, again, notes = _round_trip(tmp_path, "pointfive", values)
    assert source["role"] == taxonomy.ROLE_UNREPRESENTABLE
    assert (source["min_length"], source["max_length"]) == (2, 310)
    assert (again["min_length"], again["max_length"]) == (2, 310), (
        "the two-character floor was not carried: the twin holds "
        f"{sorted({len(cell) for cell in cells})}"
    )
    assert not [note for note in notes if note.fact == "min_length"]


def test_this_role_never_publishes_a_two_character_ceiling(
    tmp_path: pathlib.Path,
) -> None:
    """WHY THE NARROW FRACTION FORM NEEDS NO MORE THAN NINE SPELLINGS.

    `.1` through `.9` are nine distinct two-character fractions, and a
    tenth does not exist -- the family reports itself spent and
    generation refuses with a plain message. That would be a poor
    outcome, so it is worth knowing it cannot arise, and worth knowing
    it HERE rather than as a remark somebody has to re-derive.

    The mechanism: a cell is unrepresentable only by being very wide,
    so a column whose widest numeric-looking cell is two characters
    holds nothing this format cannot hold and takes another role
    entirely. Only ONE group is ever asked for the floor, so the narrow
    form is asked for at most one spelling per column.

    A previous argument of mine about this role's widths turned out to
    be false (see the same-width collision test above), so this one is
    written as a test rather than a comment: if the premise ever stops
    holding, this goes red instead of going unnoticed.
    """
    for name, values in (
        ("twochar", [".5"] * 100 + [".7"] * 100),
        ("twocharmix", [".5"] * 80 + ["12"] * 80 + ["-1"] * 80),
        ("twocharcontra", [".5"] * 80 + ["(1)"] * 80),
    ):
        table = tmp_path / f"{name}.csv"
        with table.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["reading"])
            for value in values:
                writer.writerow([value])
        column = profile.build_document(
            reading.read_table(f"{table}"), taxonomy.Settings(), []
        )["columns"][0]
        assert column["role"] != taxonomy.ROLE_UNREPRESENTABLE, (
            f"{name} took the unrepresentable role with a two-character "
            "ceiling, so the narrow fraction form can be asked for more "
            "spellings than it has"
        )
    # And the control: one wide cell IS what makes the role, and its
    # narrow floor is then carried by the two-character form.
    source, _cells, again, notes = _round_trip(
        tmp_path, "control", [".5"] * 60 + ["9" * 310] * 60
    )
    assert source["role"] == taxonomy.ROLE_UNREPRESENTABLE
    assert (source["min_length"], source["max_length"]) == (2, 310)
    assert (again["min_length"], again["max_length"]) == (2, 310)
    assert not [note for note in notes if note.fact == "min_length"]


def _oracle():
    """The independent reference implementation, loaded from its path.

    It never imports synthtwin and implements the method specification
    from that document alone, which is the whole point of comparing
    against it.
    """
    where = (
        pathlib.Path(__file__).resolve().parent.parent
        / "tools"
        / "reference"
        / "make_generation_reference_vectors.py"
    )
    spec = importlib.util.spec_from_file_location("oracle_for_widths", where)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _oracle_walk(oracle, shape: str, sign, width: int, wanted: int) -> "list":
    """The oracle's own family walk for one shape and sign, ``wanted`` deep.

    Method G10.5 step 4 as revision 5 states it: each shape-and-sign
    pair walks each family from that family's own start, and a group the
    first family refuses is written by the next. This mirrors the loop
    inside the oracle's `_unrepresentable_content` rather than
    re-deciding anything, so what is compared below is the oracle's rule
    and not this file's reading of it.
    """
    spent: "dict[tuple, int]" = {}
    walked: "list" = []
    for _step in range(wanted):
        spelling = None
        for family in oracle._spelling_families(shape, width, sign):
            key = (shape, sign, family)
            spelling = oracle._unrepresentable_spelling(
                shape, sign, spent.get(key, 0), width, family
            )
            spent[key] = spent.get(key, 0) + 1
            if spelling is not None:
                break
        walked = walked + [spelling]
    return walked


def test_the_oracle_agrees_past_the_ninth_fraction(tmp_path: pathlib.Path) -> None:
    """THE TWO IMPLEMENTATIONS AGREE WHERE THEY USED TO PART (P4-G3-R7-F3).

    The reference tool refused to write a tenth too-small spelling at
    one width -- a limit written when the zero run was whatever the
    asked width left over, so the first two-character figure body had
    no stated answer. The run now grows until the value underflows,
    which answers every order, and a generator that kept going while
    the oracle refused is a disagreement the frozen vectors could never
    show, because no frozen case asks for ten.

    **AND IT NOW REACHES THE SECOND SPELLING FAMILY** (method G10.5
    revision 5, residual R-P4-48). At 327 characters the digit-string
    family runs out at twenty-four spellings -- the twenty-fifth needs
    one zero more than the width allows -- and the exponent family
    writes every order after that. Forty orders at each width therefore
    crosses the hand-over on two of the four, which is what makes this
    comparison bind on the new family rather than only on the old one.

    Compared here directly: forty orders at four widths and both signs,
    each side walked by its own rule.
    """
    oracle = _oracle()
    mismatched: "list[tuple]" = []
    crossed: "list[tuple]" = []
    for width in (327, 328, 330, 400):
        for negative in (False, True):
            states: "dict[str, list[int]]" = {}
            used: "dict[str, int]" = {}
            sign = oracle.SIGN_NEGATIVE if negative else oracle.SIGN_POSITIVE
            theirs = _oracle_walk(oracle, "too_small", sign, width, 40)
            for order in range(40):
                mine = generation._wide_number(
                    2,
                    negative,
                    states,
                    used,
                    (),
                    generation._wide_width(2, width, negative),
                )
                if mine != theirs[order]:
                    mismatched = mismatched + [
                        (width, negative, order, mine, theirs[order])
                    ]
                elif mine is not None and "e" in mine:
                    crossed = crossed + [(width, negative, order)]
    assert mismatched == [], (
        "the two implementations do not write the same too-small "
        f"spelling: {mismatched[:4]}"
    )
    # AND THE COMPARISON REACHED THE NEW FAMILY, asserted rather than
    # hoped for: a walk that never crossed the hand-over would compare
    # forty digit strings and say nothing at all about revision 5.
    # The three that cross are the three whose ROOM is 327: both signs
    # at a width of 327 -- a negative cell there is widened to 328 by
    # its own sign, since the floors are counts of the room after it --
    # and the negative at 328. At 330 and 400 the digit-string family
    # has room for a wider figure body and forty orders do not exhaust
    # it, so those walks compare the old family only.
    reached = sorted({(width, negative) for width, negative, _order in crossed})
    assert reached == [(327, False), (327, True), (328, True)], reached


# THE MEASURED CAPACITY OF THE EXPONENT FAMILY AT ITS NARROWEST WIDTH,
# found by walking it and asking the shipped parser rather than by
# arithmetic written here a second time. The walk steps its exponent
# outward from 400 -- up to 999, then down from 399 -- steps PAST every
# candidate the parser turns down, and gives the family up once a whole
# exponent's worth of them has gone by without one accepted.
#
# The two shapes end DIFFERENTLY and the difference is worth having in
# front of a reader, because the pair of them is what makes "step past
# it" the right rule and "stop at it" the wrong one. Inside one
# exponent the mantissa ascends, so the refusals are contiguous at one
# END of it: a SUFFIX for the too-small shape, whose values grow past
# the smallest subnormal, and a PREFIX for the too-large one, whose
# values grow past the largest number this format holds.
#
# * The too-small shape's first refusal is its last accepted spelling's
#   successor: `1e-324` and `2e-324` are below the smallest subnormal
#   and `3e-324` rounds up onto it, so it ends two spellings into its
#   677th exponent, and stopping there is right.
# * The too-large shape's first refusal is `1e308`, a number this
#   format holds -- and `2e308` through `9e308` do not. Stopping there
#   threw eight spellings away and made a real 6,220-value column
#   refuse (review item P4-A2-R3, item 1). This number read 6,219 for
#   one landing and the test below PINNED it.
_LARGE_NARROW_CAPACITY = 6227
_LARGE_NARROW_WHOLE_EXPONENTS = 6219
_SMALL_NARROW_CAPACITY = 6077
_SMALLEST_HOLDABLE_MANTISSA = int(
    "24703282292062327208828439643411068618"
    "252990130716238221279284125033775363511"
)


def test_the_oracle_agrees_with_the_too_large_shape_across_its_refusal() -> None:
    """THE COMPARISON R-P4-68'S CLOSURE SAID DID NOT EXIST.

    That closure named what its measurements did NOT cover: "the
    too-large shape's two walks are not compared against the oracle
    order by order, because the comparison that exists was written for
    the too-small one". The item that follows is exactly what that gap
    hid -- one implementation stopping at `1e308` and one carrying on
    past it would have parted company at order 6,219 and nothing would
    have said so.

    Walked here across the refusal at both narrow widths and both
    signs, order by order, each side by its own rule: 6,215 orders in,
    over the eight spellings behind `1e308` and up to the family's last.
    """
    oracle = _oracle()
    mismatched: "list[tuple]" = []
    reached: "list[tuple]" = []
    for width in (5, 6):
        for negative in (False, True):
            sign = oracle.SIGN_NEGATIVE if negative else oracle.SIGN_POSITIVE
            room = width - (1 if negative else 0)
            if room < generation._EXPONENT_LARGE_ROOM:
                continue
            states: "dict[str, list[int]]" = {}
            used: "dict[str, int]" = {}
            spent: "dict[tuple, int]" = {}
            start = 0
            if room == generation._EXPONENT_LARGE_ROOM:
                start = _LARGE_NARROW_WHOLE_EXPONENTS - 4
                states = {f"exponent/1/{'-' if negative else ''}": [start]}
                spent[("too_large", sign, oracle.SPELLING_EXPONENT)] = start
            for step in range(12):
                key = ("too_large", sign, oracle.SPELLING_EXPONENT)
                theirs = oracle._unrepresentable_spelling(
                    "too_large", sign, spent.get(key, 0), width,
                    oracle.SPELLING_EXPONENT,
                )
                spent[key] = spent.get(key, 0) + 1
                mine = generation._wide_number(
                    1, negative, states, used, (),
                    generation._wide_width(1, width, negative),
                )
                if mine != theirs:
                    mismatched = mismatched + [
                        (width, negative, start + step, mine, theirs)
                    ]
                elif mine is not None and mine.endswith("e308"):
                    reached = reached + [(width, negative, mine)]
    assert mismatched == [], (
        "the two implementations do not write the same too-large "
        f"spelling: {mismatched[:4]}"
    )
    # AND THE COMPARISON CROSSED THE REFUSAL, asserted rather than
    # hoped for: a walk that never reached `1e308` would compare the
    # part of the family neither rule ever disagreed about.
    behind = [f"{body}e308" for body in range(2, 10)]
    assert sorted({cell for _width, _sign, cell in reached}) == sorted(
        behind + [f"-{cell}" for cell in behind]
    ), sorted({cell for _width, _sign, cell in reached})


def test_the_exponent_family_asks_the_parser_and_that_is_what_ends_it() -> None:
    """G10.5 revision 5's question, shown to DECIDE the family's reach.

    The family writes a spelling only where the shipped parser reads it
    back as out of range AND settles it as the shape's own whole-number
    status, and that question is what ends the walk -- which is why no
    309 and no 325 is written into the construction. Both edges are
    asserted here, at the level the rule lives, with the capacity each
    one leaves.

    THE CAPACITY IS THE POINT AND NOT A CURIOSITY. The first build of
    this family fixed the exponent at 400, which left nine spellings at
    five characters where the shape itself has thousands, and a real
    sixteen-value column was then REFUSED by the generator. The test
    below this one is that column.

    **AND A REFUSED CANDIDATE IS STEPPED PAST rather than ending the
    walk** (review item P4-A2-R3, item 1). This test pinned the other
    rule and pinned it wrong: it asserted that the too-large shape was
    spent at `1e308`, which is a number this format HOLDS, while
    `2e308` through `9e308` -- eight spellings the shape really has --
    stood unclaimed behind it. A 6,220-value column of that width was
    refused for them. The capacity is 6,227.
    """
    # THE TOO-LARGE SHAPE, whose refusal is a PREFIX of its exponent.
    room = generation._EXPONENT_LARGE_ROOM
    last = generation._wide_exponent_number(
        1, "", room, _LARGE_NARROW_WHOLE_EXPONENTS - 1
    )
    assert last == "9e309"
    assert generation._wide_reads_back(1, last)
    over = generation._wide_exponent_number(
        1, "", room, _LARGE_NARROW_WHOLE_EXPONENTS
    )
    assert over == "1e308"
    assert not generation._wide_reads_back(1, over)
    assert parsing.classify_number(over) == parsing.NUMBER
    # ...AND THE EIGHT BEHIND IT ARE WRITTEN, which is the whole item.
    for step in range(1, 9):
        after = generation._wide_exponent_number(
            1, "", room, _LARGE_NARROW_WHOLE_EXPONENTS + step
        )
        assert after == f"{step + 1}e308", after
        assert generation._wide_reads_back(1, after), after
    # The eight accepted candidates sit BEHIND one refused one, so the
    # last of them stands at candidate 6,227 while the accepted count
    # is 6,227 -- the one place the two countings differ by exactly the
    # refusal, which is the arithmetic the old rule threw away.
    assert (
        generation._wide_exponent_number(
            1, "", room, _LARGE_NARROW_WHOLE_EXPONENTS + 8
        )
        == "9e308"
    )
    assert _LARGE_NARROW_CAPACITY == _LARGE_NARROW_WHOLE_EXPONENTS + 8
    # THE TOO-SMALL SHAPE, whose refusal is a SUFFIX of its exponent, so
    # its own last accepted spelling really is the one before the first
    # refusal and its capacity does not move.
    room = generation._EXPONENT_SMALL_ROOM
    last = generation._wide_exponent_number(2, "", room, _SMALL_NARROW_CAPACITY - 1)
    assert last == "2e-324"
    assert generation._wide_reads_back(2, last)
    over = generation._wide_exponent_number(2, "", room, _SMALL_NARROW_CAPACITY)
    assert over == "3e-324"
    assert not generation._wide_reads_back(2, over)
    assert parsing.classify_number(over) == parsing.NUMBER
    # AND THE WALK ENDS AT THE LAST SPELLING THE SHAPE HAS rather than
    # at the first candidate turned down, and rather than writing a
    # holdable value into a column described as holding none. Both
    # edges are asserted from the walk itself: standing at the last
    # accepted candidate it hands that spelling back, and asked again
    # it hands back nothing. The pair is what separates "the family is
    # spent" from "the family gave up early".
    for kind, room, standing, last in (
        (
            1,
            generation._EXPONENT_LARGE_ROOM,
            _LARGE_NARROW_WHOLE_EXPONENTS + 8,
            "9e308",
        ),
        (
            2,
            generation._EXPONENT_SMALL_ROOM,
            _SMALL_NARROW_CAPACITY - 1,
            "2e-324",
        ),
    ):
        states: "dict[str, list[int]]" = {f"exponent/{kind}/": [standing]}
        walking: "dict[str, int]" = {}
        assert generation._wide_family_number(
            generation._WIDE_EXPONENT, kind, "", room, states, walking, (),
        ) == last
        assert generation._wide_family_number(
            generation._WIDE_EXPONENT, kind, "", room, states, walking, (),
        ) is None
    # AND THE WHOLE WALK UP TO THAT POINT WRITES NOTHING HOLDABLE,
    # which is the claim the two numbers above are only the edge of.
    # Counted over the ACCEPTED spellings, since the walk now steps past
    # candidates rather than stopping at the first one it turns down.
    for kind, room, capacity, visited in (
        (1, generation._EXPONENT_LARGE_ROOM, _LARGE_NARROW_CAPACITY, 6238),
        (2, generation._EXPONENT_SMALL_ROOM, _SMALL_NARROW_CAPACITY, 6087),
    ):
        states = {}
        used: "dict[str, int]" = {}
        holdable = []
        written = 0
        while True:
            spelling = generation._wide_family_number(
                generation._WIDE_EXPONENT, kind, "", room, states, used, (),
            )
            if spelling is None:
                break
            written = written + 1
            if parsing.classify_number(spelling) != parsing.NUMBER_OUT_OF_RANGE:
                holdable = holdable + [spelling]
        assert holdable == [], (kind, holdable[:3])
        assert written == capacity, (kind, written, capacity)
        # AND THE WALK GAVE THE FAMILY UP rather than walking the whole
        # three-figure field to its end. That is the other half of the
        # stopping rule and it is what makes "step past a refusal" safe
        # to state at every width: one exponent's worth of consecutive
        # refusals ENDS it, so the walk visits eleven candidates past
        # its last spelling and not the 1,873 the field still holds.
        # A room where the mantissa is wide has a rejection run wider
        # than any column could walk, and an unbounded skip would sit
        # in it.
        assert states[f"exponent/{kind}/"][0] == visited, (
            kind, states[f"exponent/{kind}/"][0]
        )
        assert visited < generation._exponent_span(kind, room) * 900
    # THE MANTISSA'S OWN EDGE, measured and much further out: it needs a
    # room of 82 characters, so no width a description carries reaches
    # it and the exponent's edge is the one that binds.
    edge = _SMALLEST_HOLDABLE_MANTISSA
    assert len(str(edge)) == 77
    assert parsing.number_out_of_range(f"{edge - 1}e-400")
    assert not parsing.number_out_of_range(f"{edge}e-400")


def test_a_real_column_of_many_narrow_wide_values_still_generates(
    tmp_path: pathlib.Path,
) -> None:
    """THE REGRESSION THE FIRST BUILD OF THIS FAMILY INTRODUCED.

    Sixteen distinct five-character values a real table holds -- `1e400`
    through `4e403`. Before the exponent family existed this column
    generated at three hundred and ten characters and missed both
    published widths. With the family's exponent FIXED at 400 it had
    nine spellings to offer sixteen groups, and `synthtwin generate`
    stopped with the domain-too-small refusal of G9.4: a shipped
    command refusing a description the profiler had just written from a
    real table, which is worse than the width miss the family was
    added to close. *A repair can move a hazard.*

    The exponent moves now, so the family's capacity at a width is the
    SHAPE's own. This asserts the whole outcome: every distinct value
    held, both widths held, nothing missed.
    """
    values: "list[str]" = []
    for tail in range(4):
        for body in range(1, 5):
            values = values + [f"{body}e40{tail}"] * 10
    assert len({value for value in values}) == 16
    assert {len(value) for value in values} == {5}
    source, cells, again, notes = _round_trip(tmp_path, "narrow-many", values)
    assert source["role"] == taxonomy.ROLE_UNREPRESENTABLE
    assert source["n_distinct"] == 16
    assert (source["min_length"], source["max_length"]) == (5, 5)
    assert sorted({len(cell) for cell in cells}) == [5]
    assert len(set(cells)) == 16
    assert _holdable(cells) == []
    assert [note.fact for note in notes] == []
    assert again["role"] == taxonomy.ROLE_UNREPRESENTABLE


def test_a_real_column_of_6220_narrow_wide_values_still_generates(
    tmp_path: pathlib.Path,
) -> None:
    """THE EIGHT SPELLINGS THE FIRST REFUSAL THREW AWAY (P4-A2-R3, item 1).

    Every five-character positive whole value this format cannot hold,
    and there are 6,227 of them: `1e309` through `9e999`, which is 691
    whole exponents of nine mantissas each, and `2e308` through `9e308`,
    which sit BEHIND the refused `1e308`. A real table can hold any
    6,220 of them.

    The walk used to read `1e308` as the family being spent, so it
    offered 6,219 spellings to a description asking for 6,220 and
    `synthtwin generate` REFUSED with the domain-too-small message of
    G9.4 -- a shipped command refusing a description the profiler had
    just written from a real table, which is the same hazard the fixed
    exponent moved here in the first place. Measured end to end before
    and after: **refused, against 6,220 distinct values at the published
    width of five, no deviation named, and nothing missed by
    `synthtwin validate`.**
    """
    values: "list[str]" = []
    for power in range(309, 1000):
        for body in range(1, 10):
            values = values + [f"{body}e{power}"]
    values = values + ["2e308"]
    assert len(set(values)) == 6220
    assert {len(value) for value in values} == {5}
    source, cells, again, notes = _round_trip(tmp_path, "sixthousand", values)
    assert source["role"] == taxonomy.ROLE_UNREPRESENTABLE
    assert source["n_distinct"] == 6220
    assert (source["min_length"], source["max_length"]) == (5, 5)
    assert len(set(cells)) == 6220, len(set(cells))
    assert sorted({len(cell) for cell in cells}) == [5]
    assert _holdable(cells) == []
    assert [note.fact for note in notes] == []
    assert again["role"] == taxonomy.ROLE_UNREPRESENTABLE
    assert again["n_distinct"] == 6220


def _hole_round_trip(
    folder: pathlib.Path,
    name: str,
    header: "list[str]",
    rows: "list[list[str]]",
    declared: "tuple[str, ...]",
) -> "tuple[dict, list[list[str]], list[str], list[str]]":
    """Describe a table under a declaration, build its twin, check it.

    Returns the description, the twin's columns, the facts the twin's
    own report named as deviations, and the `column/fact` of every
    subcheck `synthtwin validate` reported MISSED -- the real
    profile-generate-validate path and no unit stub.
    """
    settings = taxonomy.Settings(declared_missing_values=declared)
    table = folder / f"{name}.csv"
    with table.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        for row in rows:
            writer.writerow(row)
    document = profile.build_document(
        reading.read_table(f"{table}"), settings, []
    )
    written = fixtures.write_profile(folder, f"{name}-profile.json", document)
    loaded = contract.load_profile(f"{written}")
    twin = generation.generate(loaded, 5)
    twin_table = folder / f"{name}-twin.csv"
    with twin_table.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        for place in range(len(twin.columns[0])):
            writer.writerow([column[place] for column in twin.columns])
    outcome = validation.measure(loaded, f"{twin_table}")
    missed = [
        f"{check.column}/{check.fact}"
        for check in outcome.checks
        if check.verdict == validation.MISSED
    ]
    return (
        document,
        [list(column) for column in twin.columns],
        sorted({note.fact for note in twin.deviations}),
        missed,
    )


def test_the_wide_walk_refuses_a_hole_spelling_another_column_published(
    tmp_path: pathlib.Path,
) -> None:
    """THE CROSS-COLUMN CASE (review item P4-A2-R3, item 2).

    A `--missing-value` declaration is made once and reaches the whole
    table. This role publishes NOTHING -- it is one of
    `taxonomy.ROLES_PUBLISHING_NOTHING` -- so its own
    `missing_by_source` is empty on every column there is, and a walk
    reading only that map was reading a map that is always empty. The
    exponent family then handed the wide column its very first
    spelling, `1e400`, as a PRESENT cell.

    Measured before and after on this table: **eight subchecks MISSED
    on the wide column -- `universal.n_present`, `universal.n_missing`,
    `universal.n_out_of_range` and five of the role's own counts --
    against a generation report that named nothing at all; and
    afterwards nothing missed.**
    """
    left = ["alpha"] * 14 + ["beta"] * 14 + ["1e400"] * 12
    right = [
        f"{body}e{power}" for power in (700, 701, 702) for body in range(1, 10)
    ]
    right = right + ["3e703"] * 13
    rows = [[left[place], right[place]] for place in range(len(left))]
    document, columns, named, missed = _hole_round_trip(
        tmp_path, "crosshole", ["kind", "reading"], rows, ("1e400",)
    )
    # The premise: the declaration IS published, by the other column.
    assert document["columns"][0]["missing_by_source"] == {"1e400": 12}
    assert document["columns"][1]["missing_by_source"] == {}, (
        "this role publishes no hole spellings of its own, which is why "
        "the table-wide set is the only way it can learn one"
    )
    assert document["columns"][1]["role"] == taxonomy.ROLE_UNREPRESENTABLE
    assert "1e400" not in columns[1], (
        "the wide walk claimed a spelling the table publishes as absent"
    )
    assert named == []
    assert missed == [], missed


def test_the_wide_walk_refuses_a_hole_its_own_cells_wore(
    tmp_path: pathlib.Path,
) -> None:
    """THE SAME-COLUMN CASE, which this role cannot see on its own.

    Here the wide column's OWN absent cells wore `1e400`, and it still
    publishes an empty `missing_by_source`, because the role publishes
    no value of the table anywhere in its block. So even the same
    column's holes reach this walk only through the document, which is
    what makes the table-wide set the whole of the rule rather than a
    cross-column extra.
    """
    wide = [f"{body}e{power}" for power in (700, 701) for body in range(1, 10)]
    wide = wide + ["1e400"] * 12
    labels = ["alpha"] * 15 + ["beta"] * 3 + ["1e400"] * 12
    rows = [[labels[place], wide[place]] for place in range(len(wide))]
    document, columns, named, missed = _hole_round_trip(
        tmp_path, "ownhole", ["kind", "reading"], rows, ("1e400",)
    )
    assert document["columns"][1]["role"] == taxonomy.ROLE_UNREPRESENTABLE
    assert document["columns"][1]["missing_by_source"] == {}
    assert document["columns"][1]["n_missing"] == 12
    assert named == []
    assert missed == [], missed


def test_a_reserved_spelling_costs_the_family_one_and_the_count_says_so(
) -> None:
    """CAPACITY EXCLUDES THE RESERVED SPELLINGS (P4-A2-R3, item 2).

    A refused candidate is a spelling the family does not have, so the
    number the refusal of G9.4 reports has to count it out. Walked at
    the narrowest width with one spelling reserved and with none: the
    reserved walk writes exactly one fewer, and the one it does not
    write is the reserved one.
    """
    room = generation._EXPONENT_LARGE_ROOM
    written: "dict[bool, list[str]]" = {}
    for reserving in (False, True):
        holes = ("2e400",) if reserving else ()
        states: "dict[str, list[int]]" = {}
        used: "dict[str, int]" = {}
        walked: "list[str]" = []
        for _each in range(40):
            spelling = generation._wide_family_number(
                generation._WIDE_EXPONENT, 1, "", room, states, used, holes
            )
            assert spelling is not None
            walked = walked + [spelling]
        written[reserving] = walked
    assert "2e400" in written[False]
    assert "2e400" not in written[True]
    assert set(written[False]) - set(written[True]) == {"2e400"}
