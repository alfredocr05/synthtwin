"""P4-D32: no value stands where the description says there is none.

WHAT THIS FILE PINS, AND WHY EACH PIECE IS HERE. A column with two
clusters and nothing between them publishes a middle rung BETWEEN the
clusters -- the median of a hundred and fifty values around twenty and
a hundred and fifty around eighty is 49.65, a number no cell of that
column holds -- and the value stage interpolated the rungs and honoured
it (residual R-P4-136). The key `empty_bins` names the bins holding
NOBODY, published whatever the smallest group size is because there is
no group smaller than nobody, and method G6.7 makes the value stage
read it.

**The repair is in the VALUE DRAW**, so the witness has to be a whole
run: build the CSV, describe it with the real producer, load it with
the real loader, generate, and recount the twin's own finished cells
against the bin rule all three modules share. Every table here is built
by the seeded neutral builders of `fixtures.py` (plan D13); no
committed data file is read.

THE MEASUREMENT EACH WITNESS STANDS ON, taken on the tree this landing
branched from and on this one, forty seeds each, at the default floor
and again at a floor of eleven:

* 150 around 20 + 150 around 80: 4-6 cells of 300 in a bin the source
  leaves empty, against 0 at every seed;
* 250 around 10 + 50 around 90: 2-3 of 300, against 0 at every seed;
* 150 around 40 + 150 around 60: 3-6 of 300, against 0 at every seed.

`test_a_two_cluster_column_writes_nothing_in_its_empty_middle` is the
one that turns red when the pass alone is withdrawn.

AND WHAT IS **NOT** CLAIMED IS PINNED TOO, in
`test_the_fact_reaches_only_bin_resolution` (residual R-P4-138): the
bins are a thirty-second of the column's reach, so a cell moved to the
edge of the nearest occupied bin is still inside the stretch the SOURCE
left empty. What the landing buys there is measured rather than
asserted -- the furthest such cell falls from about 16-23 units from a
real value to 1.0 -- and a test that claimed the source's own gap was
cleared would be claiming something the published fact cannot carry.
"""

import pathlib
import random

import fixtures
import pytest
from synthtwin import (
    contract,
    errors,
    generation,
    parsing,
    profile,
    quality,
    reading,
    summary,
    taxonomy,
    validation,
)

# THE SEEDS, FIXED AND WRITTEN OUT. A witness that draws its own seeds
# is a witness whose failure nobody can reproduce.
SEEDS = (0, 3, 11, 29, 47)


def _two_tight_rows() -> "list[str]":
    """R-P4-136's own column: 150 around 20 and 150 around 80.

    Drawn from `random.Random(11)` and written out by this file rather
    than committed, which is plan D13's rule; the seed is fixed, so the
    column is a function of this file and of nothing else.
    """
    draw = random.Random(11)
    return (
        [f"{round(draw.gauss(20, 2), 1)}" for _index in range(150)]
        + [f"{round(draw.gauss(80, 3), 1)}" for _index in range(150)]
    )


def _uneven_rows() -> "list[str]":
    """250 around 10 and 50 around 90: the clusters are not the same size."""
    draw = random.Random(12)
    return (
        [f"{round(draw.gauss(10, 2), 1)}" for _index in range(250)]
        + [f"{round(draw.gauss(90, 3), 1)}" for _index in range(50)]
    )


def _closer_rows() -> "list[str]":
    """150 around 40 and 150 around 60: a NARROW empty middle.

    It matters because the stretch is a handful of bins rather than
    nineteen, and because the bins it leaves empty are not contiguous:
    one bin between the clusters holds a single value, so the rule has
    two stretches to keep out of and not one.
    """
    draw = random.Random(13)
    return (
        [f"{round(draw.gauss(40, 2), 1)}" for _index in range(150)]
        + [f"{round(draw.gauss(60, 3), 1)}" for _index in range(150)]
    )


def _described(
    folder: pathlib.Path,
    name: str,
    rows: "list[str]",
    floor: int = 1,
    header: str = "amount",
) -> "tuple[dict, contract.Profile]":
    """The real reader, the real producer and the real loader."""
    path = fixtures.write(
        folder, f"{name}.csv", header + "\n" + "\n".join(rows) + "\n"
    )
    table = reading.read_table(
        str(path), first_row=reading.FIRST_ROW_AUTOMATIC
    )
    document = profile.build_document(
        table, taxonomy.Settings(small_cell_floor=floor), []
    )
    loaded = contract.load_profile(
        str(fixtures.write_profile(folder, f"{name}-profile.json", document))
    )
    return document, loaded


def _empty_of(rows: "list[str]") -> "tuple[float, float, list[int]]":
    """The bins the SOURCE leaves empty, by the shipped bin rule.

    Computed here from the rows rather than read out of the
    description, so the assertion below compares the twin against the
    TABLE and not against the key under test. A recount that read the
    key would pass on a producer that published the wrong bins.
    """
    numbers = [float(one) for one in rows]
    lowest = min(numbers)
    highest = max(numbers)
    held = {
        parsing.histogram_bin(one, lowest, highest) for one in numbers
    }
    return lowest, highest, [
        place
        for place in range(parsing.HISTOGRAM_BINS)
        if place not in held
    ]


def _cells_in(
    twin: generation.Twin, lowest: float, highest: float, barred: "set[int]"
) -> "list[str]":
    """Every cell of the twin's one column standing in a barred bin."""
    found: list[str] = []
    for cell in twin.columns[0]:
        if cell == "":
            continue
        value = parsing.parse_number(cell)
        if value is None:
            continue
        if parsing.histogram_bin(value, lowest, highest) in barred:
            found = found + [cell]
    return found


# -- the producer publishes the fact ----------------------------------


def test_a_two_cluster_column_publishes_the_bins_that_hold_nothing(
    tmp_path: pathlib.Path,
) -> None:
    """The description names exactly the bins the table leaves empty."""
    rows = _two_tight_rows()
    lowest, highest, barred = _empty_of(rows)
    document, _loaded = _described(tmp_path, "tight", rows)
    assert barred, "this column is chosen for having an empty middle"
    assert document["columns"][0]["empty_bins"] == barred
    assert lowest == document["columns"][0]["percentiles"]["min"]
    assert highest == document["columns"][0]["percentiles"]["max"]


def test_the_fact_survives_a_floor_the_census_beside_it_does_not(
    tmp_path: pathlib.Path,
) -> None:
    """The whole reason the key exists beside `value_histogram`.

    The census is all or nothing, so it vanishes at every floor above
    one on exactly the columns whose shape matters most: a two-cluster
    column has thin bins at the edges of each cluster. The empty-bin
    list is under no floor and says the same thing at every one.
    """
    rows = _two_tight_rows()
    _lowest, _highest, barred = _empty_of(rows)
    seen = []
    for floor in (1, 2, 3, 5, 11):
        document, _loaded = _described(
            tmp_path, f"floors-{floor}", rows, floor=floor
        )
        block = document["columns"][0]
        seen = seen + [len(block["value_histogram"])]
        assert block["empty_bins"] == barred, floor
    assert seen[0] > 0, "at a floor of one the census is publishable"
    assert seen[1:] == [0, 0, 0, 0], (
        "above a floor of one this column's census is withheld, which is "
        "the measurement plan P4-D32 rests on"
    )


def test_a_column_with_no_empty_stretch_names_none(
    tmp_path: pathlib.Path,
) -> None:
    """A check that CAN fail the other way.

    A rule that named bins on every column would pass every assertion
    above and be useless, so one column with values spread over its
    whole range is described here and must name nothing.
    """
    rows = [f"{index * 0.5:.1f}" for index in range(400)]
    document, _loaded = _described(tmp_path, "even", rows)
    assert document["columns"][0]["empty_bins"] == []


# -- the loader refuses what no column could be ------------------------


def _tampered(
    tmp_path: pathlib.Path, name: str, bins: "list[int]"
) -> "str | None":
    """Load a description whose empty-bin list has been rewritten.

    BUILT AT A RAISED FLOOR, so the census beside it is legitimately
    absent and the complement condition has nothing to say. Editing a
    floor-one description instead put the census and the list in
    disagreement, and the loader then refused on Q15 -- which is a real
    refusal about the wrong fact, and would have let a missing Q20
    condition pass unnoticed.
    """
    document, _loaded = _described(
        tmp_path, name, _two_tight_rows(), floor=11
    )
    assert document["columns"][0]["value_histogram"] == {}
    document["columns"][0]["empty_bins"] = bins
    path = fixtures.write_profile(tmp_path, f"{name}-edited.json", document)
    try:
        contract.load_profile(str(path))
    except errors.ProfileError as refusal:
        return f"{refusal}"
    return None


def test_the_loader_refuses_a_repeated_bin(tmp_path: pathlib.Path) -> None:
    """Each bin named once, in order (invariant Q20)."""
    refusal = _tampered(tmp_path, "repeat", [5, 5, 6])
    assert refusal is not None
    assert "Q20" in refusal or "ascending" in refusal


def test_the_loader_refuses_a_bin_out_of_order(
    tmp_path: pathlib.Path,
) -> None:
    """A list a producer may write two ways is one two producers differ on."""
    refusal = _tampered(tmp_path, "order", [7, 6])
    assert refusal is not None


def test_the_loader_refuses_an_end_bin(tmp_path: pathlib.Path) -> None:
    """The smallest value is in the first bin and the largest in the last."""
    assert _tampered(tmp_path, "first", [0, 5]) is not None
    assert _tampered(
        tmp_path, "last", [5, parsing.HISTOGRAM_BINS - 1]
    ) is not None


def test_the_loader_refuses_a_bin_the_census_names(
    tmp_path: pathlib.Path,
) -> None:
    """ONE FACT WRITTEN TWICE, and the guard against one copy moving.

    Where the census is published it names every bin that holds
    something, so the two are complements. A description whose two
    shape facts disagree is refused rather than read.
    """
    document, _loaded = _described(tmp_path, "clash", _two_tight_rows())
    block = document["columns"][0]
    named = sorted(int(key) for key in block["value_histogram"])
    assert named, "this column publishes its census at the default floor"
    block["empty_bins"] = sorted(set(block["empty_bins"]) | {named[1]})
    path = fixtures.write_profile(tmp_path, "clash-edited.json", document)
    with pytest.raises(errors.ProfileError):
        contract.load_profile(str(path))


def test_the_loader_refuses_a_bin_the_census_accounts_for_neither_way(
    tmp_path: pathlib.Path,
) -> None:
    """The other half of the complement, and it fails differently.

    Dropping a bin from the empty list while the census still names
    only what it named leaves one bin claimed by neither fact. A
    one-directional check would pass this.
    """
    document, _loaded = _described(tmp_path, "hole", _two_tight_rows())
    block = document["columns"][0]
    assert block["empty_bins"], "this column has an empty middle"
    block["empty_bins"] = block["empty_bins"][1:]
    path = fixtures.write_profile(tmp_path, "hole-edited.json", document)
    with pytest.raises(errors.ProfileError):
        contract.load_profile(str(path))


# -- the twin keeps out of the stretches -------------------------------


@pytest.mark.parametrize(
    "name,build",
    (
        ("tight", _two_tight_rows),
        ("uneven", _uneven_rows),
        ("closer", _closer_rows),
    ),
)
def test_a_two_cluster_column_writes_nothing_in_its_empty_middle(
    tmp_path: pathlib.Path, name: str, build
) -> None:
    """THE WITNESS. Before this landing, 4-6, 2-3 and 3-6 cells of 300.

    Recounted off the twin's own finished text, against the bins
    computed from the SOURCE rows, so neither side of the comparison
    is the key under test.
    """
    rows = build()
    lowest, highest, barred = _empty_of(rows)
    assert barred, f"{name} is chosen for having an empty middle"
    _document, loaded = _described(tmp_path, f"gap-{name}", rows)
    for seed in SEEDS:
        twin = generation.generate(loaded, seed)
        found = _cells_in(twin, lowest, highest, set(barred))
        assert found == [], (
            f"{name} at seed {seed}: the twin wrote {found} where the "
            f"description says the real column holds nothing"
        )


def test_the_twin_keeps_out_at_a_raised_floor_too(
    tmp_path: pathlib.Path,
) -> None:
    """At a floor of eleven the census is gone and the fact is not.

    This is the assertion the key exists for: the same repair on the
    same column with `value_histogram` withheld.
    """
    rows = _two_tight_rows()
    lowest, highest, barred = _empty_of(rows)
    _document, loaded = _described(tmp_path, "gap-raised", rows, floor=11)
    assert loaded.columns[0].facts.value_histogram == {}
    assert list(loaded.columns[0].facts.empty_bins) == barred
    for seed in SEEDS:
        twin = generation.generate(loaded, seed)
        assert _cells_in(twin, lowest, highest, set(barred)) == []


def test_the_twin_still_meets_everything_else_it_used_to(
    tmp_path: pathlib.Path,
) -> None:
    """The pass takes nothing back from the passes before it.

    Measured at forty seeds on the tree this branched from and on this
    one: the quality report on these twins misses exactly
    `widths.published.1` at every seed and `ladder.p90` at some, both
    PRE-EXISTING (residual R-P4-139). What must not appear is a new
    miss -- an end of the ladder, a sign count, `n_zero`, or the style
    census -- so those are named here rather than left to a total.
    """
    rows = _two_tight_rows()
    _document, loaded = _described(tmp_path, "keeps", rows)
    guarded = (
        "ladder.min",
        "ladder.max",
        "counts.n_zero",
        "counts.n_negative",
        "counts.n_used_in_statistics",
        "counts.n_left_out_of_statistics",
        "type.integer_valued",
    )
    for seed in SEEDS:
        twin = generation.generate(loaded, seed)
        path = fixtures.write(
            tmp_path,
            f"keeps-{seed}.csv",
            fixtures.rows_to_csv(
                list(twin.names), [list(row) for row in twin.rows]
            ),
        )
        outcome = validation.measure(loaded, f"{path}")
        missed = {
            check.subcheck
            for check in outcome.checks
            if check.verdict == validation.MISSED
        }
        for one in guarded:
            assert one not in missed, (
                f"seed {seed} missed {one}, which this landing must not "
                f"cost: {sorted(missed)}"
            )
        for one in ("styles.published.plain", "styles.published.decimal"):
            assert one not in missed, f"seed {seed} missed {one}"


def test_the_fact_reaches_only_bin_resolution(
    tmp_path: pathlib.Path,
) -> None:
    """WHAT IS NOT CLAIMED (residual R-P4-138), pinned as a number.

    A bin is a thirty-second of the column's reach, so the bins the
    source leaves empty are strictly INSIDE the stretch the source
    actually leaves empty, and a cell moved to the edge of the nearest
    occupied bin is still inside that stretch. What the landing buys
    is that the cell is near a real value instead of in the middle of
    the gap: measured at forty seeds, the furthest such cell fell from
    15.7-23.0 units from a real value to 1.0. The bound asserted here
    is loose enough to survive a draw and far below the before figure.
    """
    rows = _two_tight_rows()
    numbers = sorted(float(one) for one in rows)
    widest = (0.0, 0.0, 0.0)
    for low, high in zip(numbers, numbers[1:]):
        if high - low > widest[0]:
            widest = (high - low, low, high)
    _document, loaded = _described(tmp_path, "resolution", rows)
    deepest = 0.0
    for seed in SEEDS:
        twin = generation.generate(loaded, seed)
        for cell in twin.columns[0]:
            if cell == "":
                continue
            value = parsing.parse_number(cell)
            if value is None or not widest[1] < value < widest[2]:
                continue
            deepest = max(
                deepest, min(value - widest[1], widest[2] - value)
            )
    assert deepest > 0.0, (
        "cells DO remain inside the source's own gap, which is the "
        "residual this test records; an assertion that none did would "
        "claim more than the published fact carries"
    )
    assert deepest < 4.0, (
        f"a cell sits {deepest} from the nearest real value; before this "
        f"landing the furthest sat 15.7 to 23.0 away, and the repair is "
        f"what keeps them at the edges of the real clusters"
    )


def test_where_the_twin_cannot_move_a_value_it_says_so(
    tmp_path: pathlib.Path,
) -> None:
    """The report is never silent about a cell that had to stay.

    A whole-numbered column whose bins are barely wider than a unit
    leaves the neighbouring bin with no free whole number, which is one
    of the two families residual R-P4-140 records. The obligation this
    pins is not that the move succeeds -- it cannot always -- but that
    a failure reaches the person reading the twin's report.
    """
    rows = (
        [f"{1 + (index * 3) % 18}" for index in range(100)]
        + [f"{50 + (index * 7) % 15}" for index in range(100)]
    )
    lowest, highest, barred = _empty_of(rows)
    assert barred
    _document, loaded = _described(tmp_path, "whole-gap", rows)
    spoke = 0
    stayed = 0
    for seed in range(40):
        twin = generation.generate(loaded, seed)
        left = _cells_in(twin, lowest, highest, set(barred))
        named = [
            note for note in twin.deviations if note.fact == "empty_bins"
        ]
        if left:
            stayed = stayed + 1
            assert named, (
                f"seed {seed} left {left} in a stretch the description "
                f"says is empty and the report said nothing"
            )
        if named:
            spoke = spoke + 1
    assert spoke or not stayed
    assert stayed < 40, (
        "a column on which the move NEVER succeeds is not the witness "
        "this test means to be"
    )


# -- the fact reaches the pages a person reads -------------------------


def test_the_summary_says_the_column_held_nothing_in_a_stretch(
    tmp_path: pathlib.Path,
) -> None:
    """A person reading the summary is told, in words.

    Every other numeric line of that page names where the values ARE,
    and a two-cluster column looks in all of them exactly like one
    smooth column.
    """
    document, _loaded = _described(tmp_path, "summary", _two_tight_rows())
    page = summary.render(document, "")
    assert "held no value at all in" in page
    assert "equal steps between its smallest value and its largest" in page


def test_the_quality_report_lists_the_fact_rather_than_checking_it(
    tmp_path: pathlib.Path,
) -> None:
    """REPORT-ONLY, and the page says so where a person meets it."""
    rows = _two_tight_rows()
    _document, loaded = _described(tmp_path, "listed", rows)
    twin = generation.generate(loaded, 3)
    path = fixtures.write(
        tmp_path,
        "listed-twin.csv",
        fixtures.rows_to_csv(
            list(twin.names), [list(row) for row in twin.rows]
        ),
    )
    outcome = validation.measure(loaded, f"{path}")
    facts = {listing.fact for listing in outcome.listings}
    assert "numeric.empty_bins" in facts
    for check in outcome.checks:
        assert check.fact != "numeric.empty_bins", (
            "the fact is REPORT-ONLY on the measurement plan P4-D32 "
            "carries; a check here would hold a file to it"
        )
    page = quality.quality_report(loaded, outcome)
    assert "held no value at all" in page


# -- the rules of the move, each pinned where it is decided ------------
#
# EVERY TEST BELOW WAS WRITTEN AGAINST A SILENT MUTANT. The mutation run
# of this landing withdrew each rule of method G6.7 from the shipped
# generator in turn and ran 535 tests against each: the pass itself, the
# written-form test, and all four loader and producer rules turned the
# suite red, and these six did not. A rule a twin's BYTES cannot
# separate is pinned where it is decided instead -- which is the
# treatment residual R-P4-126 names for exactly this shape of gap -- so
# each one drives the named function directly rather than hoping a
# column can be found whose cells move when it is withdrawn.

# The scale these use: ends 0 to 320, so a bin is ten wide and the
# stretch of bins 10 to 19 runs from 100 to 200.
_ENDS = (0.0, 320.0)
_BARRED = {place: 1 for place in range(10, 20)}
_RUN = (10, 19)
_WIDTHS = (-1, 1)


def test_a_value_nearer_the_top_of_a_stretch_goes_up() -> None:
    """The nearer edge, and not always the same one (G6.7.5).

    Withdrawn, every stratum went DOWN and 535 tests stayed green,
    because the twin's OWN ladder still put its cells in two clusters
    and no published count separates "moved down" from "was always
    down". The rule is what keeps a cell near the cluster it was
    drawn beside.
    """
    high = generation._cleared_value(
        _ENDS, _BARRED, _RUN, 190.0, generation._BAND_POSITIVE,
        {}, {}, False, _WIDTHS,
    )
    assert high is not None and high >= 200.0, high
    low = generation._cleared_value(
        _ENDS, _BARRED, _RUN, 110.0, generation._BAND_POSITIVE,
        {}, {}, False, _WIDTHS,
    )
    assert low is not None and low < 100.0, low


def test_the_move_stops_at_the_bin_next_to_the_stretch() -> None:
    """The reach, stated in the fact's own terms (G6.7.5).

    A value moves out of the stretch and into the bin beside it, and
    no further. Ten wide here, so a value sent up lands in [200, 210)
    and one sent down in [90, 100).
    """
    high = generation._cleared_value(
        _ENDS, _BARRED, _RUN, 190.0, generation._BAND_POSITIVE,
        {}, {}, False, _WIDTHS,
    )
    assert 200.0 <= high < 210.0, high
    low = generation._cleared_value(
        _ENDS, _BARRED, _RUN, 110.0, generation._BAND_POSITIVE,
        {}, {}, False, _WIDTHS,
    )
    assert 90.0 <= low < 100.0, low


def test_no_two_strata_of_one_stretch_take_one_cell() -> None:
    """The spelling-distinctness rule (G6.7.4, clause 5).

    Two values a thousandth apart are two values and ONE cell. The
    walk is told what is already spoken for and must land on a text
    none of it reads as.
    """
    # A NARROW SCALE, so the walk's own step is finer than the width
    # the cells are written at. That is the whole condition the rule
    # exists for: on the wide scale above, two neighbouring candidates
    # are two different cells anyway and a run that checked only the
    # NUMBERS would pass. Ends 0 to 3.2 make a bin a tenth wide and a
    # step a six-hundred-and-fortieth, so sixteen consecutive
    # candidates all read `2.0` at one figure after the point.
    narrow = (0.0, 3.2)
    first = generation._cleared_value(
        narrow, _BARRED, _RUN, 1.9, generation._BAND_POSITIVE,
        {}, {}, False, _WIDTHS,
    )
    spoken = {
        spelling: 1
        for spelling in generation._spellings_of(first, _WIDTHS, False)
    }
    second = generation._cleared_value(
        narrow, _BARRED, _RUN, 1.9, generation._BAND_POSITIVE,
        spoken, {first: 1}, False, _WIDTHS,
    )
    assert second is not None and second != first
    assert not (
        set(generation._spellings_of(second, _WIDTHS, False))
        & set(spoken)
    ), (
        f"the second stratum lands on {second}, which reads back the way "
        f"the first one does at a width the census could reach it at"
    )


def test_a_moved_value_keeps_the_form_it_was_written_in() -> None:
    """The written form is kept (G6.7.4, clause 4).

    `_pool_enough` puts a column's pooled cells on the strata whose
    values carry a point and `_whole_enough` puts the point-free count
    on the ones that do not, so a move that changed which was which
    would take back the count those two just met.
    """
    pointed = generation._cleared_value(
        _ENDS, _BARRED, _RUN, 190.5, generation._BAND_POSITIVE,
        {}, {}, False, _WIDTHS,
    )
    assert pointed is not None
    assert not generation._carries_plainly(pointed, False), pointed
    plain = generation._cleared_value(
        _ENDS, _BARRED, _RUN, 190.0, generation._BAND_POSITIVE,
        {}, {}, False, _WIDTHS,
    )
    assert plain is not None
    assert generation._carries_plainly(plain, False), plain


def test_a_moved_value_never_crosses_zero() -> None:
    """The sign band (G6.7.4, clause 3).

    A stratum in the negative band whose nearer edge is above zero has
    nowhere to go, and the answer is None -- which the caller turns
    into the deviation that names the stretch -- rather than a positive
    value that would take a cell out of the negative count.
    """
    # THE STRETCH ENDS AT ZERO, so the nearer edge of it for a value
    # just below zero is the bin ABOVE, and the bin above is positive.
    # A stretch whose nearer edge is still negative would pass whether
    # the rule were there or not, which is the shape this test had
    # first and the reason it saw nothing.
    ends = (-100.0, 220.0)
    barred = {place: 1 for place in range(5, 10)}
    found = generation._cleared_value(
        ends, barred, (5, 9), -5.0, generation._BAND_NEGATIVE,
        {}, {}, False, (-1, 1),
    )
    assert found is None or found < 0.0, found
    # ...and the mirror, so the test cannot pass by the walk simply
    # failing: a POSITIVE stratum in the same stretch does get a value,
    # and it is above zero.
    other = generation._cleared_value(
        ends, barred, (5, 9), -5.0, generation._BAND_POSITIVE,
        {}, {}, False, (-1, 1),
    )
    assert other is not None and other > 0.0, other


def test_a_stratum_in_the_zero_band_is_never_moved(
    tmp_path: pathlib.Path,
) -> None:
    """The zero band (G6.7.4, clause 2), so the count of zeroes stands.

    Driven through the whole pass rather than through `_cleared_value`,
    because the rule lives in the gathering step and not in the walk:
    the zero stratum is never put in a queue at all.
    """
    rows = (
        ["0"] * 40
        + [f"{-90 - (index * 3) % 20}" for index in range(80)]
        + [f"{90 + (index * 3) % 20}" for index in range(80)]
    )
    _document, loaded = _described(tmp_path, "zeroes", rows)
    facts = loaded.columns[0].facts
    assert facts.n_zero == 40
    assert facts.empty_bins, "this column has an empty middle"
    for seed in SEEDS:
        twin = generation.generate(loaded, seed)
        held = [cell for cell in twin.columns[0] if cell == "0"]
        assert len(held) == 40, (
            f"seed {seed} wrote {len(held)} zeroes against a published 40"
        )


def test_a_stratum_is_gathered_by_its_spelling_and_not_only_its_value(
) -> None:
    """The queue reads the SPELLINGS (G6.7.6).

    A value a thousandth outside a stretch is written back inside it at
    the width the fraction census gives that cell, which is exactly the
    defect the walk's own candidate test exists to stop. The gathering
    step had the same hole and this is the rule that closes it: 99.96
    is in bin 9 as a value and reads `100.0` at one figure, which is in
    bin 10 and barred.
    """
    assert parsing.histogram_bin(99.96, *_ENDS) == 9
    assert generation._barred_bin(99.96, _ENDS, _BARRED, _WIDTHS, False) == 10
    assert not generation._reads_outside(
        99.96, _ENDS, _BARRED, _WIDTHS, False
    )
    # ...and a value that reads outside at every width is left alone.
    assert generation._barred_bin(80.0, _ENDS, _BARRED, _WIDTHS, False) == -1
    assert generation._reads_outside(80.0, _ENDS, _BARRED, _WIDTHS, False)
