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
import math
import pathlib

import fixtures
from synthtwin import contract, generation, profile, reading, taxonomy


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

    The published `max_length` is NOT held here and that is correct
    rather than a second defect: holding it would mean writing a value
    this format can hold. The twin comes out one character wider and
    the report names it, which is the trade this whole file is about.
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
    # And the width it could not hold is NAMED rather than faked.
    longest = max(len(cell) for cell in cells)
    if longest != source["max_length"]:
        assert "max_length" in {note.fact for note in notes}


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
