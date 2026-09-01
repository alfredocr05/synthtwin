"""Review item P2-C4-F3: a published style map that CAN be placed IS.

Owner decision 10 says the twin writes every numeric style in its
published count, because the form controls the type a reader infers,
and the contract calls `numeric_styles` EXACT-OBSERVABLE. Round 4 found
a producer description whose own values prove its map -- fifty-one
cells holding eleven `1.5`, twenty `100` and twenty `200.5`, published
as twenty `plain` and thirty-one `decimal` -- and the twin wrote twelve
and thirty-nine on every seed and named both counts as missed.

WHY IT MISSED, WHICH IS THE POINT. The three point-free styles need a
cell whose value can be written with no point, and how many such cells
a column HAS is decided by the STRATA: the even split of method G5.2
gave the one stratum that could hold a whole number seventeen of the
fifty-one cells. Nothing publishes those sizes. A numeric block carries
no multiplicity map, so how many cells hold each different value is the
twin's own choice, while `numeric_styles` is a published, exact fact.
The choice gave way to the fact (method G5.2's carrier step), which is
the order plan P2-D6's feasibility rule 4 already fixes.

WHAT THIS FILE HOLDS THE REPAIR TO:

1. the reviewed column writes 20/31 exactly, on the seeds the item
   names and on every reference-vector seed;
2. over a battery of descriptions built by the REAL producer, every
   NAMED published style count comes out exactly, on every seed;
3. where the map still cannot come out whole, the twin writes the
   largest number of point-free cells the published ends leave -- the
   most any conforming generator can write -- and nothing but the
   anonymous pooled remainder falls short;
4. the facts the repair is not allowed to spend -- `n_zero`,
   `n_negative`, both ladder ends, the count of different values, and
   every approximated bound -- are recounted from the finished cells;
5. four mutants, one per rule the repair rests on, each of which must
   put a producer's map back out of reach.
"""

import dataclasses
import pathlib

import pytest

import fixtures
from synthtwin import (
    contract,
    generation,
    parsing,
    profile,
    reading,
    rendering,
    taxonomy,
    validation,
)

# The seeds of the item's own closure check, and the seed of every
# frozen reference-vector case, so the claim is not one seed wide.
SEEDS = (0, 1, 2, 3, 63, 12345) + tuple(range(101, 114))

# The column of review item P2-C4-F3, written out once so that every
# test that needs it is looking at the same fifty-one cells.
REVIEWED = ["1.5"] * 11 + ["100"] * 20 + ["200.5"] * 20

# A column whose negative side holds eleven cells over TWO values and,
# under the ladder share of G5.2, ONE stratum -- the pinned `min` of
# `-20.5`, which carries a point. The ladder reads that band as three
# plateaus against the positive side's eight, so the five strata shared
# in that proportion leave the negatives one, and every negative cell is
# stuck on the fractional end until the band step of the carrier rule
# gives that side a second stratum.
BAND = (
    ["-20.5"]
    + ["-20"] * 10
    + ["00"] * 12
    + ["1"] * 4
    + ["6"] * 3
    + ["9"] * 3
)

# A 22-cell column on which two strata can reach the same whole number
# and only one of them has another. Its ladder is FLAT at `6` from the
# third quartile up, so the pinned top stratum holds `6` and the nine
# cells under it -- whose share runs (4.91, 6.0) -- have `5` as the one
# whole number left inside their reach. The two cells below sit in
# (4.0, 4.91) and round ONTO that same `5` whenever the draw puts them
# above 4.5. Which of the two gets it used to turn on the draw, so the
# published `plain` count came out 11 on some seeds and 9 on others.
CONTENDED = (
    ["2.5"] * 3
    + ["4"] * 3
    + ["5.25"] * 8
    + ["6"] * 8
)

# A column whose ladder crowds four different values between 17 and 18.
FLAT = (
    ["+18"] * 19
    + ["37.75"] * 5
    + ["1.700000E+01"] * 5
    + ["060"] * 4
    + ["-4.5"] * 4
    + ["11"] * 2
)

# Descriptions built by the REAL producer, chosen to reach every shape
# the placement has an opinion about: a point-free quota beyond the
# even split, a quota carried by the smallest stratum, a ladder whose
# flat half puts the commonest value ON the published minimum and on
# the published maximum, negatives, zeros, a leading-plus quota that
# only the positive band can carry, a pooled remainder beside a named
# point-free count, an all-decimal column that asks for nothing, and
# columns whose other classes take a share of the spellings.
BATTERY = (
    ("the reviewed column", REVIEWED),
    ("a quota beyond the even split", ["0.5"] * 8 + ["7"] * 40 + ["9.5"] * 8),
    ("the mode is the minimum", ["4"] * 30 + ["7.5"] * 8 + ["12.5"] * 8),
    ("the mode is the maximum", ["1.5"] * 8 + ["4.5"] * 8 + ["9"] * 30),
    ("a flat lower half", ["4"] * 30 + ["9.5"] * 10 + ["12.5"] * 8),
    ("three whole blocks", ["1.5"] * 7 + ["10"] * 15 + ["20"] * 15 + ["30"] * 15 + ["44.5"] * 7),
    ("negatives, zeros and positives", ["-3.5"] * 8 + ["-2"] * 12 + ["0"] * 6 + ["4"] * 14 + ["19.5"] * 7),
    ("whole negatives", ["-9.5"] * 6 + ["-4"] * 30 + ["0"] * 6 + ["7.5"] * 6),
    ("a leading plus the positives carry", ["-1.5"] * 10 + ["+5"] * 20 + ["200.5"] * 10),
    ("a whole column", [str(number) for number in range(60)]),
    ("a whole column with a plus", [f"+{number}" for number in range(30)] + [str(number) for number in range(30, 60)]),
    ("nothing but decimals", [f"{number}.25" for number in range(1, 41)]),
    ("one whole value among fractions", ["0.5"] * 20 + ["3"] * 6 + ["9.5"] * 20),
    ("a named count beside a pool", ["1.5"] * 5 + ["007"] * 25 + ["88.5"] * 5),
    ("many different values", [f"{number}.5" for number in range(1, 21)] + ["100"] * 25),
    ("wide magnitudes", ["1.5"] * 11 + ["10000000000000000"] * 20 + ["2e20"] * 10),
    ("absent cells beside the numbers", REVIEWED + [""] * 9),
    ("text stragglers beside the numbers", REVIEWED + ["n/a "] * 6),
    ("a band with one blocked stratum", BAND),
    ("a ladder with no room for a whole number", FLAT),
)

# The one battery case whose point-free demand is larger than the
# published ends can ever leave room for, and whose remainder therefore
# stands or falls with the draw. Every one of its 39 cells is claimed
# point-free -- 19 by a NAMED `leading_plus` count and 20 by the
# anonymous pool, which contract 7.5.7 writes plainly -- while the
# published `min` of `-4.5` has no point-free spelling at all, so 38 is
# the most any conforming generator can write. The twin writes all 38 on
# most seeds and 29 on the rest, and the reason is a real one rather
# than a placement it could undo: its ladder is FLAT at `18` across a
# quarter of the column, so the stratum sitting on that rung holds `18`
# and the stratum just below it can reach only `17`, which the stratum
# below THAT holds inside its own share on the seeds where its value
# rounds up. What does hold on every seed is the part the description
# NAMES -- `test_every_named_style_count_is_written_exactly` asserts it
# with the rest of the battery -- and the equality
# `test_every_cell_that_can_be_written_point_free_is` states, that every
# cell whose value HAS a point-free spelling is written with one. The
# residue is the anonymous pool, and it is recorded rather than absorbed.
LADDER_LEAVES_NO_ROOM = frozenset({"a ladder with no room for a whole number"})


# The floor this file describes at, stated rather than inherited. Every
# claim below is about the ANONYMOUS POOLED REMAINDER of `numeric_styles`
# -- the `(withheld)` key -- and a style is pooled only when fewer than
# `small_cell_floor` cells wore it. The default floor is now 1 (owner
# ruling A-P4-37), at which nothing is ever pooled and the whole subject
# of this file disappears; 11 is the floor these cases were built for and
# the one at which a pool exists to compete with a named count.
SETTINGS = taxonomy.Settings(small_cell_floor=11)


def _described(
    folder: pathlib.Path,
    values: "list[str]",
    measured: "list[str] | None" = None,
) -> "tuple[dict, contract.Profile]":
    """Write a one-column table, describe it, load the description.

    `measured` is the `--measurement` declaration, which the joined role
    REQUIRES: an undeclared `120/80` column is not that role, by design
    (plan P4-D23), and a fixture that forgets it gets an `identifier`
    and a test that checks nothing.
    """
    path = fixtures.write(
        folder, "table.csv", fixtures.single_column_table("amount", values)
    )
    table = reading.read_table(str(path))
    document = profile.build_document(table, SETTINGS, [], None, measured)
    target = fixtures.write_profile(folder, "table-profile.json", document)
    return document, contract.load_profile(str(target))


def _styles(twin: generation.Twin) -> "dict[str, int]":
    """The form of every numeric cell, read off the contract's ladder."""
    counted: dict[str, int] = {}
    for cell in twin.columns[0]:
        if cell == "" or parsing.classify_number(cell) != parsing.NUMBER:
            continue
        style = parsing.numeric_style(cell)
        counted[style] = counted.get(style, 0) + 1
    return counted


def _target(published: "dict[str, int]") -> "dict[str, int]":
    """The published map with the pooled remainder added to `plain`.

    Contract 7.5.7 fixes that as the form the pooled cells take, and so
    as what the recount from the written CSV is measured against.
    """
    wanted: dict[str, int] = {}
    for name in sorted(published):
        key = "plain" if name == "(withheld)" else name
        wanted[key] = wanted.get(key, 0) + published[name]
    return wanted


def _named(published: "dict[str, int]") -> "dict[str, int]":
    """Only the counts the description NAMES, pool excluded."""
    return {
        name: published[name]
        for name in sorted(published)
        if name != "(withheld)"
    }


def _point_free_number(value: float) -> bool:
    """Whether this number has a spelling with no point and no exponent.

    Stated here from the number rather than read from the generator, so
    the expectation below is not the implementation's own opinion: a
    value can be written in digits alone exactly when it is WHOLE, at
    any width.

    THE SIXTEEN-FIGURE CEILING IS GONE (owner decision 10, 2026-08-13).
    It was the contract's fixed-point window, which governs the
    canonical spelling of a number in the profile DOCUMENT and not the
    spelling of a plain cell in the twin. A plain cell owes two things
    -- it reads back as the same number and it classifies as plain --
    and the full digit expansion of a whole value does both however
    many figures it takes. While the ceiling stood, a column whose
    source wrote very wide whole numbers in figures published them
    `plain` and got `100000000000000000000.0` back, which a reader
    takes for a decimal column.
    """
    return float(value).is_integer()


def _ceiling(document: dict) -> int:
    """The most point-free cells the published ends can leave.

    At least one cell must read back as the published `min` and, once
    the column holds more than one different value, one as the published
    `max`. Both are EXACT-OBSERVABLE, so an end with no point-free
    spelling costs one cell of the point-free demand and no rule can buy
    it back.
    """
    column = document["columns"][0]
    numbers = column["n_numeric"]
    strata = min(numbers, column["n_distinct_folded"])
    blocked = 0
    if numbers >= 1 and not _point_free_number(column["percentiles"]["min"]):
        blocked = blocked + 1
    if strata >= 2 and not _point_free_number(column["percentiles"]["max"]):
        blocked = blocked + 1
    return numbers - blocked


def _cases(folder: pathlib.Path) -> "list[tuple[str, dict, contract.Profile]]":
    """Every battery description, built once through the real producer."""
    built: list[tuple[str, dict, contract.Profile]] = []
    for step, (name, values) in enumerate(BATTERY):
        here = folder / f"case-{step}"
        here.mkdir()
        document, loaded = _described(here, values)
        assert "numeric_styles" in document["columns"][0], (
            f"{name} is not a numeric column and proves nothing here"
        )
        built = built + [(name, document, loaded)]
    return built


# -- 1. the column the review item names -------------------------------


def test_the_reviewed_column_writes_its_published_map_exactly(
    tmp_path: pathlib.Path,
) -> None:
    """Point 1, on the item's own fifty-one cells and every named seed.

    The source's own values are an assignment that meets every
    published fact at once, so there is nothing here for a report to
    say. The twin writes twenty `plain` and thirty-one `decimal`, and
    the deviation ledger holds nothing about this column's styles.
    """
    document, loaded = _described(tmp_path, REVIEWED)
    assert document["columns"][0]["numeric_styles"] == {
        "plain": 20,
        "decimal": 31,
    }
    assert document["columns"][0]["integer_valued"] is False

    for seed in SEEDS:
        twin = generation.generate(loaded, seed)
        assert _styles(twin) == {"plain": 20, "decimal": 31}, seed
        assert [
            note for note in twin.deviations if note.fact == "numeric_styles"
        ] == [], seed


# -- 2 and 3. the general claim, over a producer battery ---------------


def test_every_named_style_count_is_written_exactly(
    tmp_path: pathlib.Path,
) -> None:
    """Point 2: no NAMED published count is missed on these columns.

    A count the description NAMES is written in full on every one of
    these producer descriptions and on every seed; only the anonymous
    pool falls short, and the next test bounds even that. The claim is
    stated over descriptions rather than as a universal, because one
    published shape can still cost a named count and this file names it
    rather than leaving it to be found: a ladder crowding several
    different values inside one unit leaves those strata no whole number
    of their own, so their cells cannot be written point-free at all.
    `test_a_crowded_ladder_costs_a_named_count_and_says_so` holds that
    case to the bound that does apply to it.
    """
    for name, document, loaded in _cases(tmp_path):
        published = document["columns"][0]["numeric_styles"]
        for seed in SEEDS:
            written = _styles(generation.generate(loaded, seed))
            for style, count in _named(published).items():
                assert written.get(style, 0) >= count, (name, seed, style)


def test_the_map_comes_out_whole_or_reaches_the_ends_ceiling(
    tmp_path: pathlib.Path,
) -> None:
    """Point 3: exactly the map, or exactly the most that can be written.

    Either the recounted map IS the published one with the pooled
    remainder added to `plain`, or the point-free demand was larger than
    the published ends leave room for -- and then the twin writes every
    point-free cell those ends leave. The one case with a lower ceiling
    of its own is named in `LADDER_LEAVES_NO_ROOM` together with the
    published fact that lowers it, so an exception has to be argued in
    words rather than absorbed.
    """
    for name, document, loaded in _cases(tmp_path):
        if name in LADDER_LEAVES_NO_ROOM:
            continue
        column = document["columns"][0]
        wanted = _target(column["numeric_styles"])
        demand = sum(
            wanted.get(style, 0)
            for style in ("plain", "leading_zero", "leading_plus")
        )
        room = _ceiling(document)
        for seed in SEEDS:
            written = _styles(generation.generate(loaded, seed))
            if demand <= room:
                assert written == wanted, (name, seed)
                continue
            free = sum(
                written.get(style, 0)
                for style in ("plain", "leading_zero", "leading_plus")
            )
            assert free == room, (name, seed, demand, room)


def test_every_cell_that_can_be_written_point_free_is(
    tmp_path: pathlib.Path,
) -> None:
    """The general form of point 3, and the one that holds everywhere.

    A cell can wear `plain`, `leading_zero` or `leading_plus` exactly
    when the value it holds can be written with no point. So the number
    of cells written that way can never exceed the number of cells whose
    value can be, and a generator that stops short of it has left a
    published count unwritten for no reason its own values give. The two
    are EQUAL here on every battery description and every seed -- except
    where the published map asks for fewer, which is the ordinary case
    and is checked as equality with the map instead.
    """
    for name, document, loaded in _cases(tmp_path):
        wanted = _target(document["columns"][0]["numeric_styles"])
        demand = sum(
            wanted.get(style, 0)
            for style in ("plain", "leading_zero", "leading_plus")
        )
        for seed in SEEDS:
            twin = generation.generate(loaded, seed)
            written = _styles(twin)
            free = sum(
                written.get(style, 0)
                for style in ("plain", "leading_zero", "leading_plus")
            )
            carriers = len(
                [
                    value
                    for value in [
                        parsing.parse_number(cell)
                        for cell in twin.columns[0]
                        if cell != ""
                        and parsing.classify_number(cell) == parsing.NUMBER
                    ]
                    if value is not None and _point_free_number(value)
                ]
            )
            assert free <= carriers, (name, seed, free, carriers)
            assert free == min(demand, carriers), (
                name, seed, free, demand, carriers,
            )


def test_a_pooled_cell_the_ends_cannot_hold_is_spelled_by_its_value(
    tmp_path: pathlib.Path,
) -> None:
    """The open defect of P2-C5-F3, repaired: no miss is left to name.

    Forty named `plain` cells and six pooled ones over forty-six cells,
    while one cell must read back as `0.5` and one as `9.25`. Under the
    withdrawn rule every pooled cell was owed the `plain` form, which
    those two cells have no spelling for, so the twin missed a total it
    could not have met and the report named it. The amended rule of the
    Phase 3 plan (P3-D8.1) spells a pooled cell by its OWN value: the
    four pooled cells with a point-free spelling are written plainly,
    the two without are written in their values' canonical text, and
    NOTHING IS MISSED. The bytes are the same bytes; what changed is
    that the obligation is now one the twin can meet.
    """
    document, loaded = _described(
        tmp_path, ["0.5"] * 3 + ["7"] * 40 + ["9.25"] * 3
    )
    assert document["columns"][0]["numeric_styles"] == {
        "plain": 40,
        "(withheld)": 6,
    }
    twin = generation.generate(loaded, 0)
    assert _styles(twin) == {"plain": 44, "decimal": 2}
    named = [note for note in twin.deviations if note.fact == "numeric_styles"]
    assert named == [], [note.published for note in named]


def test_a_re_spelled_whole_cell_cannot_buy_its_own_spill(
    tmp_path: pathlib.Path,
) -> None:
    """The regression for the circular recount (review item P3-C1-F2).

    THIS IS THE ATTACK THE FIRST REPAIR LET THROUGH, and the reason it
    has a test of its own: the recount counted the cells WRITTEN with a
    point rather than the cells whose VALUE has no point-free spelling,
    so a column that spelled a whole value `7.0` instead of `7` raised
    its own spill by one and the arithmetic balanced against itself.
    Every published count still looked met and the twin was wrong.

    Re-spelling three whole cells as decimals must therefore be named,
    and it must be named on the two clauses it actually breaks: the
    plain total falls short, and the two canonical point-carrying forms
    carry more between them than the published counts and the spill
    allow. Reinstating the old written-style count turns this red,
    which is what the earlier tamper test could not do -- it moved a
    cell to `leading_zero`, which the exact leading-zero count catches
    whichever way the spill is computed.
    """
    _unused, loaded = _described(
        tmp_path, ["0.5"] * 3 + ["7"] * 40 + ["9.25"] * 3
    )
    twin = generation.generate(loaded, 0)
    written = list(twin.columns[0])
    assert generation._style_notes(loaded.columns[0], written) == []

    tampered: list[str] = []
    moved = 0
    for cell in written:
        if cell and "." not in cell and "e" not in cell and moved < 3:
            tampered = tampered + [f"{cell}.0"]
            moved = moved + 1
            continue
        tampered = tampered + [cell]
    assert moved == 3, "the fixture no longer holds three whole cells"
    notes = generation._style_notes(loaded.columns[0], tampered)
    assert notes, "a whole cell re-spelled with a point must be named"
    spoken = " ".join(note.published for note in notes)
    assert "plain form" in spoken, spoken
    assert "decimal point or a lower-case exponent" in spoken, spoken


def test_the_repaired_style_identity_still_names_a_broken_column(
    tmp_path: pathlib.Path,
) -> None:
    """The vacuity floor under the repair above.

    A rule that cannot be broken is not a rule. The same description is
    measured against a column whose cells were re-spelled after the
    fact -- every plain cell given a leading zero, which is a form the
    description publishes zero of -- and the recount must name it. This
    is the clause that stops the amended identity from being satisfied
    by substituting one published form for another.
    """
    document, loaded = _described(
        tmp_path, ["0.5"] * 3 + ["7"] * 40 + ["9.25"] * 3
    )
    assert document["columns"][0]["numeric_styles"] == {
        "plain": 40,
        "(withheld)": 6,
    }
    twin = generation.generate(loaded, 0)
    written = list(twin.columns[0])
    tampered = [
        f"0{cell}" if cell and "." not in cell else cell for cell in written
    ]
    notes = generation._style_notes(loaded.columns[0], tampered)
    assert notes, "a re-spelled column must be named"
    broken = sorted(note.published for note in notes)
    assert any("leading_zero" in line for line in broken), broken
    assert any("plain" in line for line in broken), broken


def test_the_crowded_ladder_of_p2c5f3_writes_its_published_map(
    tmp_path: pathlib.Path,
) -> None:
    """Review item P2-C5-F3, on the 82 cells the reviewer described.

    THIS COLUMN USED TO MISS A NAMED PUBLISHED COUNT, and a test in this
    file used to require the miss. The reviewer's own reading was the
    one that held: its ladder crowds four different values between
    `0.125` and `1`, so the EVEN SPLIT leaves those four strata one
    whole number between them -- but the split is not a published fact,
    the source's own values are an assignment meeting every count at
    once, and `numeric_styles` is EXACT-OBSERVABLE. Seeds 0, 1 and 63
    wrote `20/62` and seeds 17 and 113 wrote `30/52`; the reach step of
    G5.2 now asks the LADDER which strata a whole number is left for and
    moves the cells -- and, where a band's strata all sit on fractions,
    one stratum's window -- until the published counts have cells that
    can wear them.

    What is asserted is the whole of the obligation: the exact map on
    every seed, no `numeric_styles` line in the report, and no OTHER
    exact count bought to pay for it -- the count of different spellings
    is the one that repair could have spent, so it is recounted here
    beside the map.
    """
    values = (
        ["0.125"] * 10
        + ["0.25"] * 10
        + ["0.375"] * 10
        + ["0.625"] * 10
        + ["1"] * 20
        + ["-32"] * 14
        + ["-59.5"] * 4
        + ["52.75"] * 4
    )
    document, loaded = _described(tmp_path, values)
    column = document["columns"][0]
    assert column["numeric_styles"] == {"plain": 34, "decimal": 48}
    for seed in SEEDS + (17, 113):
        twin = generation.generate(loaded, seed)
        assert _styles(twin) == {"plain": 34, "decimal": 48}, seed
        assert [
            note for note in twin.deviations if note.fact == "numeric_styles"
        ] == [], seed
        present = [cell for cell in twin.columns[0] if cell != ""]
        assert len(set(present)) == column["n_distinct"], seed
        assert len({parsing.folded(cell) for cell in present}) == (
            column["n_distinct_folded"]
        ), seed
        # THE ONE THING THIS COLUMN CANNOT CARRY, and it is named
        # rather than silent (plan amendment A-P4-15). Its census
        # publishes thirty cells at three figures after the point and
        # fourteen at two, and its twin's own strata are sized 11, 11,
        # 10, 11, 4 and 1 -- no assignment of whole values reaches
        # either quota, and the walk refuses to split a value across two
        # widths because that would spend the count of different
        # spellings this test recounts one line above. So a width goes
        # unplaced, the report says which, and nothing else moves.
        other = [
            note
            for note in twin.deviations
            if note.fact not in ("fraction_widths", "n_distinct_values")
        ]
        assert other == [], seed
        # AND THE SECOND THING IT CANNOT ALWAYS CARRY, which this
        # column is the clearest demonstration of in the suite (plan
        # P4-D4.9, closing residual R-P4-20). At seeds 3 and 17 the
        # twin writes `-46` AND `-46.0`: two spellings of ONE number.
        # The published count of different SPELLINGS is met exactly --
        # the assertion four lines above proves it -- while the column
        # holds seven numbers where the description publishes eight.
        # Until `n_distinct_values` existed nothing anywhere said so,
        # and a reader grouping these rows by value met seven groups
        # with every check green.
        numbers = len({parsing.exact_of_spelling(cell) for cell in present})
        spoken_values = [
            note
            for note in twin.deviations
            if note.fact == "n_distinct_values"
        ]
        if numbers != column["n_distinct_values"]:
            assert spoken_values, seed
        else:
            assert spoken_values == [], seed
        # ...AND THE WIDTH THAT WENT UNPLACED IS NAMED, which is the
        # half a filter alone does not assert. A test that only
        # subtracts the deviation it expects would stay green if the
        # report fell silent -- and silence is exactly what A-P4-15
        # trades the quota for, so silence is the thing to pin.
        spoken = [
            note for note in twin.deviations if note.fact == "fraction_widths"
        ]
        assert spoken, seed
        for note in spoken:
            assert note.column == "amount", seed
            assert "figure(s) after the point" in note.published, seed
            assert note.achieved.isdigit(), (seed, note.achieved)
            assert note.published != note.achieved, seed


def test_the_reach_step_and_the_chain_together_place_the_crowded_ladder(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mutant 5: put the optimistic count back, and P2-C5-F3 returns.

    `_reach_sizes` is reverted to the identity, which is exactly G5.2's
    carrier step as it stood when the review found this column: the cell
    step counts a stratum as a carrier because the values step MAY take
    it to a whole number, sees enough of them, and moves nothing. The
    reviewer's own 20/62 comes straight back, so this file is proving
    something about that step rather than about the seed.

    THERE ARE NOW TWO WAYS TO THE SAME COUNT, and this test said there
    was one. R-P4-69's repair gave the values step a second, independent
    route -- `_rehomed` asks a stratum HOLDING a whole number for it
    rather than passing over the number, so a stratum the reach step
    miscounted as a carrier is repaired after the fact. Reverting either
    one alone now leaves the published count intact, and the test
    asserting that reverting the reach step ALONE broke it was asserting
    something no longer true. Both are reverted here, and each is also
    measured alone, so the file records which of them is load-bearing:
    on this column, neither is by itself and the pair is.
    """
    values = (
        ["0.125"] * 10
        + ["0.25"] * 10
        + ["0.375"] * 10
        + ["0.625"] * 10
        + ["1"] * 20
        + ["-32"] * 14
        + ["-59.5"] * 4
        + ["52.75"] * 4
    )
    _document, loaded = _described(tmp_path, values)
    assert _styles(generation.generate(loaded, 0)) == {
        "plain": 34, "decimal": 48,
    }

    monkeypatch.setattr(
        generation,
        "_reach_sizes",
        lambda sizes, bands, rungs, whole, numbers, demand, plus: sizes,
    )
    assert _styles(generation.generate(loaded, 0)) == {
        "plain": 34, "decimal": 48,
    }, "the chain alone still covers this column"

    monkeypatch.undo()
    monkeypatch.setattr(generation, "_rehomed", lambda *a, **k: None)
    assert _styles(generation.generate(loaded, 0)) == {
        "plain": 34, "decimal": 48,
    }, "the reach step alone still covers this column"

    monkeypatch.setattr(
        generation,
        "_reach_sizes",
        lambda sizes, bands, rungs, whole, numbers, demand, plus: sizes,
    )
    written = _styles(generation.generate(loaded, 0))
    assert written.get("plain", 0) < 34, written


def test_the_flat_rung_claim_and_the_chain_keep_the_map_seed_free(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mutant 6: let the walk claim a later stratum's only number.

    A stratum sitting just under a flat rung rounds ONTO that rung's
    number, which is the only one the stratum whose share IS that rung
    can ever be given. Without the bar in `_held_later` which of them
    got a form turns on a drawn value, and the count comes apart along
    the seed. The mutant restores that, and the column must part
    company with its own published count on at least one seed.

    THE SHAPE, AND WHY IT REACHES THE BAR, so the next person does not
    have to rediscover it. `_held_later` is consulted only where the
    whole number a stratum wants lies OUTSIDE its own share of the
    ladder -- inside it, the stratum has the older claim and the bar is
    never asked. So the column needs THREE things at once: a stratum
    whose nearest whole number sits just past the top of its share; a
    LATER stratum whose share holds that number and which has no other
    whole number within half a unit of its own share; and a point-free
    demand large enough that the walk reaches both. Twenty-two cells
    over four values do it. The ladder is flat at `6` from the third
    quartile up, which pins `6` on the top stratum and leaves the nine
    cells below it -- share (4.91, 6.0) -- with `5` as their only
    reachable whole number, `4` being more than half a unit under their
    share. The two cells below THAT sit in (4.0, 4.91), and on the
    seeds where the draw puts them above 4.5 -- 101, 104, 106, 108 and
    110 of this file's seeds -- their nearest whole number is that same
    `5`, half a unit outside their own share. Held back, they step to
    `4` inside their share and both strata are written point-free;
    unheld, they take `5`, the nine-cell stratum is left with no
    candidate at all and keeps `5.25`, and eleven published `plain`
    cells come out as nine.

    THE VALUES ARE THE FIXTURE, NOT THE SIZES: nothing publishes the
    stratum sizes, and since method G5.2a the allotment reads them off
    the ladder's plateaus, so the four sizes above are what these four
    values and these four counts produce. That is also why the review
    item's own 54-cell column no longer reaches this bar and this one
    replaces it: under the plateau allotment its two contending strata
    meet AT the number they contend for, which puts the number inside
    both shares, and a number inside a stratum's own share is one the
    bar is never asked about.
    """
    document, loaded = _described(tmp_path, CONTENDED)
    published = _named(document["columns"][0]["numeric_styles"])
    assert published == {"plain": 11, "decimal": 11}
    before = [_styles(generation.generate(loaded, seed)) for seed in SEEDS]
    for step in range(len(SEEDS)):
        for style, count in published.items():
            assert before[step].get(style, 0) >= count, (SEEDS[step], style)

    # AND THE SAME PAIR AS MUTANT 5 (residual R-P4-69). `_rehomed`
    # reaches the stratum the unheld walk strands -- it asks the stratum
    # holding the contended number for it, and the chain repeats -- so
    # withdrawing the bar ALONE no longer parts the column from its
    # count on any seed. The bar is not therefore idle: withdraw both
    # and the seed dependence comes back exactly as recorded.
    monkeypatch.setattr(generation, "_held_later", lambda candidate, later: False)
    unheld = [_styles(generation.generate(loaded, seed)) for seed in SEEDS]
    assert not any(
        one.get(style, 0) < count
        for one in unheld
        for style, count in published.items()
    ), unheld

    monkeypatch.setattr(generation, "_rehomed", lambda *a, **k: None)
    after = [_styles(generation.generate(loaded, seed)) for seed in SEEDS]
    assert any(
        one.get(style, 0) < count
        for one in after
        for style, count in published.items()
    ), after


def test_one_form_per_stratum_is_what_keeps_the_spelling_count(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mutant 7: let the cell walk split a stratum, and a count is spent.

    Two forms inside one stratum write one value two ways, and a column
    with as many strata as it has published spellings has no room for
    that. The repair packs the styles over whole strata there;
    `_style_strata` reverted to the identity puts the cell walk's own
    answer back, and the count of different spellings must then come out
    above the published one on at least one seed -- which is one exact
    count bought with another, the trade this file exists to refuse.
    """
    values = (
        ["0.125"] * 10
        + ["0.25"] * 10
        + ["0.375"] * 10
        + ["0.625"] * 10
        + ["1"] * 20
        + ["-32"] * 14
        + ["-59.5"] * 4
        + ["52.75"] * 4
    )
    document, loaded = _described(tmp_path, values)
    published = document["columns"][0]["n_distinct"]
    for seed in SEEDS:
        twin = generation.generate(loaded, seed)
        present = [cell for cell in twin.columns[0] if cell != ""]
        assert len(set(present)) == published, seed

    monkeypatch.setattr(
        generation,
        "_style_strata",
        lambda quotas, layout, values, whole, wanted, raw, styles: styles,
    )
    spent = []
    for seed in SEEDS:
        twin = generation.generate(loaded, seed)
        present = [cell for cell in twin.columns[0] if cell != ""]
        spent = spent + [len(set(present))]
    assert any(count > published for count in spent), spent


# -- 4. what the repair is not allowed to spend ------------------------


def test_the_counts_the_carrier_step_may_not_spend_are_recounted(
    tmp_path: pathlib.Path,
) -> None:
    """Point 4: sign, zero and both ends survive, and no value is added.

    Moving cells between strata could buy a style with `n_negative`, and
    stepping a stratum onto a free whole number could buy one with an
    end of the ladder or with the count of different values. Every one
    of those is recounted here from the finished cells, on every battery
    case and every seed. The count of different values is checked in the
    direction this repair could move it: a step onto a number some other
    stratum already held would ADD a value the description never
    published, so no run may hold more values than the description
    names.
    """
    for name, document, loaded in _cases(tmp_path):
        column = document["columns"][0]
        for seed in SEEDS:
            twin = generation.generate(loaded, seed)
            values = [
                parsing.parse_number(cell)
                for cell in twin.columns[0]
                if cell != ""
                and parsing.classify_number(cell) == parsing.NUMBER
            ]
            held = [value for value in values if value is not None]
            assert len(held) == column["n_numeric"], (name, seed)
            assert len([one for one in held if one < 0.0]) == (
                column["n_negative"] - column["n_negative_unrepresentable"]
            ), (name, seed)
            assert len([one for one in held if one == 0.0]) == (
                column["n_zero"]
            ), (name, seed)
            assert min(held) == column["percentiles"]["min"], (name, seed)
            assert max(held) == column["percentiles"]["max"], (name, seed)
            assert len(set(held)) <= column["n_distinct_folded"], (name, seed)


# -- 5. the four bounds the R-P4-69 hold-back rests on ------------------
#
# EACH OF THESE IS A BOUND NO COLUMN IN THE BATTERY WITNESSES, and that
# is exactly why they are here. Mutating any one of them left the whole
# suite green: the sign bound is unreachable while the named-`plain`
# bound stands, the two of them cover each other, and the two
# preferences change which strata are chosen without changing any
# published count. A bound whose only witness is another bound is a
# bound that goes when someone simplifies, so each is held to its own
# contract directly.


def _pooled_column(
    folder: pathlib.Path,
) -> "tuple[contract.ColumnBlock, contract.NumericFacts]":
    """The R-P4-69 column: 34 whole numbers and two pooled halves."""
    values = [f"{index % 9 + 1}" for index in range(34)] + ["1.5", "2.5"]
    _document, loaded = _described(folder, values)
    column = loaded.columns[0]
    return column, column.facts


def test_the_held_back_value_never_crosses_zero() -> None:
    """A stratum's share may straddle zero; its value may not.

    The rung above a column's last negative value is a positive number,
    so the share interpolated for the stratum just under zero runs from
    a negative low to a positive high. Halving in from the top of that
    share lands on the positive side. Measured before the bound was
    written, on a column of four `-4.5` cells: the negative stratum was
    handed `2.097` and the twin held ONE negative cell against a
    published four.
    """
    straddling = (-1.0, 3.0)
    below = generation._fraction_inside(
        straddling, {}, generation._BAND_NEGATIVE
    )
    assert below is None or below < 0.0, below
    above = generation._fraction_inside(
        (-3.0, 1.0), {}, generation._BAND_POSITIVE
    )
    assert above is None or above > 0.0, above
    # And the bound is not simply refusing everything: a share wholly
    # inside one band still yields a value.
    inside = generation._fraction_inside(
        (-4.0, -3.0), {}, generation._BAND_NEGATIVE
    )
    assert inside is not None and -4.0 < inside < -3.0, inside
    # A HELD-BACK VALUE IS NEVER ONE THAT WOULD BE WRITTEN POINT-FREE,
    # which is the whole reason it is held back. The middle of this
    # share is `2`, and taking it would leave the cell reading `plain`
    # and the pooled count still unmet.
    whole_in_reach = generation._fraction_inside(
        (1.0, 3.0), {}, generation._BAND_POSITIVE
    )
    assert whole_in_reach == 2.5, whole_in_reach

    # AND A SHARE WHOSE WIDTH IS A POWER OF TWO IS NOT A DEAD END
    # (round 1, item 3). Eight halvings of `(1, 257)` are `129, 65, 33,
    # 17, 9, 5, 3, 2` -- every one of them whole -- and this helper used
    # to answer None and let the stratum be passed over in silence,
    # although `1.5` was there to be had. The middle plus at most half a
    # unit cannot be whole when the middle is, which is what makes the
    # search complete at any width.
    wide = generation._fraction_inside(
        (1.0, 257.0), {}, generation._BAND_POSITIVE
    )
    assert wide is not None and 1.0 < wide < 257.0, wide
    assert wide != int(wide), wide
    # A SHARE THAT STRADDLES ZERO STILL YIELDS ITS OWN SIDE OF IT,
    # rather than nothing: cutting the share back to the band is what
    # makes the sign bound a narrowing and not a refusal.
    straddling = generation._fraction_inside(
        (-1.0, 3.0), {}, generation._BAND_NEGATIVE
    )
    assert straddling is not None and -1.0 < straddling < 0.0, straddling
    # AND IT LOOKS BELOW THE MIDDLE AS WELL AS ABOVE IT (round 2, item
    # 1). Probing one side only exhausts on a share whose upper half is
    # spoken for while its lower half is free: the middle of `(1, 2)`
    # and every step above it held, `1.25` is still there.
    upper: dict[float, int] = {1.5: 1}
    step = (2.0 - 1.5) / 2.0
    for _each in range(20):
        upper[1.5 + step] = 1
        step = step / 2.0
    lower = generation._fraction_inside(
        (1.0, 2.0), upper, generation._BAND_POSITIVE
    )
    assert lower is not None and 1.0 < lower < 1.5, lower


def test_the_hold_back_leaves_a_column_whose_plain_is_not_named_alone(
    tmp_path: pathlib.Path,
) -> None:
    """A pooled cell may be point-free, so the pool is not the count.

    Where `plain` is a named count every cell the twin can write
    point-free it writes plainly, so the cells carrying a point number
    exactly the pool. Where `plain` is NOT named that arithmetic does
    not hold: this column's pool of twenty covers `060` and `11` as
    well as its fractions, and holding back twenty cells would put a
    point in eleven that never had one.
    """
    _document, loaded = _described(tmp_path, FLAT)
    column = loaded.columns[0]
    facts = column.facts
    assert facts.numeric_styles.get("plain", 0) == 0, facts.numeric_styles
    assert generation._style_pool(facts.numeric_styles) == 20
    layout, _notes, _content = generation._numeric_layout(column, facts)
    rungs = generation._merged_rungs(facts)
    values = [-4.5, -4.0, 15.0, 18.0, 25.0, 60.0]
    kept, held, notes = generation._pool_enough(
        column, facts, layout, rungs, list(values)
    )
    assert held == values
    assert kept is layout
    assert notes == []


def test_the_hold_back_takes_the_narrowest_strata(
    tmp_path: pathlib.Path,
) -> None:
    """A held-back form belongs on a rare value, not on a crowded one.

    Nothing publishes the stratum sizes, so which strata keep a value
    with a point in it is the twin's own choice, and the choice is
    made where the real column made it: the forms a description holds
    back are the ones too rare to name, so the twin puts them on the
    cells it has fewest of. Widest-first meets the same census and
    spreads a rare form over a crowded value.
    """
    column, facts = _pooled_column(tmp_path)
    built, _notes, _content = generation._numeric_layout(column, facts)
    rungs = generation._merged_rungs(facts)
    # THE SIZES THIS COLUMN'S LADDER GIVES CANNOT TELL THE TWO ORDERS
    # APART, and a test that cannot tell them apart is not measuring the
    # preference. Its narrowest strata are single cells and its pool is
    # two, so a walk from the widest end passes over every stratum too
    # wide to fit and arrives at the same two. One stratum of exactly
    # the pool's width is what separates them: widest-first takes THAT
    # one and stops, narrowest-first takes the single cell first.
    sizes = (3, 4, 1, 5, 3, 4, 4, 4, 4, 2, 2)
    assert sum(sizes) == column.n_numeric
    starts: list[int] = []
    running = 0
    for size in sizes:
        starts = starts + [running]
        running = running + size
    layout = dataclasses.replace(
        built, sizes=sizes, starts=tuple(starts)
    )
    values = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0]
    assert len(values) == len(layout.sizes)
    _kept, held, _notes = generation._pool_enough(
        column, facts, layout, rungs, list(values)
    )
    moved = [
        place for place in range(len(values)) if held[place] != values[place]
    ]
    narrowest = min(layout.sizes)
    assert moved, held
    for place in moved:
        assert layout.sizes[place] == narrowest, (place, layout.sizes)


def test_the_type_is_owed_a_cell_no_stratum_fits_exactly(
    tmp_path: pathlib.Path,
) -> None:
    """The hold-back may overshoot for the TYPE, and only for the type.

    A stratum wider than the count still wanted is passed over rather
    than overshot, because a cell written with a point the description
    did not pool is a `plain` floor missed. That rule is about a COUNT.
    The column's TYPE is not a count: a twin publishing
    `integer_valued: false` whose every value is whole re-describes as
    `count`, and everything downstream then reads a different kind of
    column. So where no stratum fits, the narrowest one takes the value
    anyway.

    NO COLUMN IN THIS FILE REACHES THAT BRANCH, which is exactly why it
    is asserted here: the census duty or the drawn values give these
    fixtures a cell carrying a point before the question arises, and
    mutating the branch away left the whole suite green (round 1, items
    1 and 5). A layout whose every stratum is wider than the one cell
    owed is what reaches it.
    """
    column, facts = _pooled_column(tmp_path)
    built, _notes, _content = generation._numeric_layout(column, facts)
    rungs = generation._merged_rungs(facts)
    # Every stratum at least two cells wide, so the exact-fit rule above
    # passes over all of them while one cell is still owed.
    sizes = (4, 4, 4, 4, 4, 4, 4, 4, 4)
    assert sum(sizes) == column.n_numeric
    starts: list[int] = []
    running = 0
    for size in sizes:
        starts = starts + [running]
        running = running + size
    layout = dataclasses.replace(
        built,
        sizes=sizes,
        starts=tuple(starts),
        bands=tuple([generation._BAND_POSITIVE] * len(sizes)),
    )
    whole = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]
    narrowed, held, notes = generation._pool_enough(
        column, facts, layout, rungs, list(whole)
    )
    assert any(value != int(value) for value in held), held
    assert notes == [], notes
    # AND IT TAKES ONE CELL, NOT THE STRATUM (round 2, item 2). Taking
    # the stratum whole would meet the type by writing four cells with a
    # point in them where the description pooled one, which is a `plain`
    # floor missed to buy a type that one cell would have bought. The
    # stratum is narrowed to a single cell and its neighbour takes the
    # rest, so the count of different values does not move either.
    moved = [
        place for place in range(len(whole)) if held[place] != whole[place]
    ]
    assert len(moved) == 1, (moved, held)
    assert narrowed.sizes[moved[0]] == 1, (moved, narrowed.sizes)
    assert sum(narrowed.sizes) == sum(layout.sizes), narrowed.sizes
    assert len(narrowed.sizes) == len(layout.sizes), narrowed.sizes


def test_a_stratum_never_hands_its_number_to_a_wider_one(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The chain's trade may not cost cells, which is its whole point.

    `_rehomed` asks a stratum HOLDING a whole number for it, and the
    holder that cannot step elsewhere gives it up only if it is
    NARROWER. Traded the other way the walk would take a number off a
    stratum covering more cells than the one asking, and the count of
    point-free cells -- the count the walk exists to meet -- would fall.

    The walk is watched where it runs, on every column of the battery
    and every seed, because the trade fires only where a stratum finds
    no free whole number left and no fixture reaches that by design.
    """
    seen: list[tuple[int, int]] = []
    traded = [0]
    walked = generation._whole_enough
    homed = generation._rehomed

    def watched(column, facts, layout, rungs, values):
        after = walked(column, facts, layout, rungs, values)
        seen.append(
            (
                _point_free_cells(layout, values),
                _point_free_cells(layout, after),
            )
        )
        return after

    def counted(*arguments, **named):
        moves = homed(*arguments, **named)
        if moves is None:
            return moves
        layout = arguments[2]
        rungs = arguments[3]
        numbers = arguments[4]
        # THE HOLDER IS NARROWER, ASSERTED WHERE THE TRADE HAPPENS.
        # Trading the other way need not show up in the finished
        # column at all: the walk goes on afterwards and, on this
        # column, wins back every cell such a trade would cost. So the
        # bound is asserted on the trade itself rather than read off a
        # total that does not move. A chain gives its fraction to the
        # stratum the DEEPEST asker asked, which is the move after it,
        # not the one that began the chain.
        if not generation._carries_plainly(moves[0][1], False):
            traded[0] = traded[0] + 1
            giving = moves[0][0]
            asked_by = moves[1][0]
            assert layout.sizes[giving] < layout.sizes[asked_by], (
                giving, asked_by, layout.sizes,
            )
        # AND NO MOVE TAKES A NUMBER A LATER STRATUM IS STILL WAITING
        # FOR. The chain asks `_whole_inside` the same question the
        # plain walk asks and passes it the same `_shares_after`, so a
        # stratum reaching OUTSIDE its own share never takes the one
        # number a stratum further on could ever be given.
        for step in range(len(moves)):
            seat = moves[step][0]
            value = moves[step][1]
            if not generation._carries_plainly(value, False):
                continue
            mine = generation._share_of(seat, layout, rungs, numbers)
            if mine is None or mine[0] <= value <= mine[1]:
                continue
            for share in generation._shares_after(
                seat, layout, rungs, numbers
            ):
                assert not share[0] <= value <= share[1], (
                    seat, value, share,
                )
        return moves

    monkeypatch.setattr(generation, "_whole_enough", watched)
    monkeypatch.setattr(generation, "_rehomed", counted)
    # THE BATTERY DOES NOT REACH THIS BRANCH AT ALL -- measured: zero
    # calls to `_rehomed` over every case and every seed of it -- so the
    # column the trade was written for is walked here as well, and the
    # test asserts that the trade FIRED before asserting what it costs.
    # Without that, this reads as a clean pass over a branch never run.
    _document, pooled = _described(
        tmp_path, [f"{index % 9 + 1}" for index in range(34)] + ["1.5", "2.5"]
    )
    for _name, _each, loaded in _cases(tmp_path):
        for seed in SEEDS:
            generation.generate(loaded, seed)
    for seed in SEEDS:
        generation.generate(pooled, seed)
    assert seen
    assert traded[0] > 0, "the trade branch was never reached"
    for before, after in seen:
        assert after >= before, (before, after)


def _point_free_cells(
    layout: "generation._NumericLayout", values: "list[float]"
) -> int:
    """How many CELLS these stratum values write with no point."""
    covered = 0
    for place in range(len(values)):
        if generation._carries_plainly(values[place], False):
            covered = covered + layout.sizes[place]
    return covered


# -- 6. the two roles that carry a numeric grain inside them -----------
#
# AFFIXED CORES AND JOINED POSITIONS TAKE THIS SAME PATH. Both are
# turned into a numeric view and handed to `_numeric_content`, so every
# rule above governs them at a grain no column-shaped test reaches: the
# OUTER role can read back perfectly while the nested `integer_valued`
# has moved and the nested `plain` floor is missed (round 1, item 6).


def _nested_numbers(column: contract.ColumnBlock) -> "list[object]":
    """Every numeric grain inside one column, whatever its role."""
    facts = column.facts
    inner = getattr(facts, "numbers", None)
    if inner is not None:
        return [inner]
    parts = getattr(facts, "parts", None)
    if parts is not None:
        return list(parts)
    return [facts]


def test_a_nested_numeric_grain_keeps_the_type_it_publishes(
    tmp_path: pathlib.Path,
) -> None:
    """`integer_valued: false` inside a role is still a fact about a type.

    An affixed core and a joined position each publish their own
    `integer_valued`, and a consumer routes on it exactly as it routes
    on a plain numeric column's. The outer role surviving proves nothing
    about them: a `$1.50` column whose core came back whole in every
    cell is an affixed column of counts wearing a currency mark.

    Both fixtures publish a pooled pair of fractions in the grain --
    `plain: 34` with a pool of 2 -- which is the shape residual R-P4-69
    was recorded on.
    """
    affixed = [f"${index % 9 + 1}" for index in range(34)] + ["$1.5", "$2.5"]
    joined = [
        f"{index % 9 + 1}/{index % 7 + 1}" for index in range(34)
    ] + ["1.5/2", "2.5/3"]
    for name, values, measured in (
        ("affixed", affixed, None),
        ("joined", joined, ["amount"]),
    ):
        document, loaded = _described(tmp_path, values, measured)
        column = loaded.columns[0]
        grains = _nested_numbers(column)
        # THE FIXTURE REACHES THE GRAIN AT ALL, asserted before anything
        # is asserted about it: a role that came back `identifier` for
        # want of a declaration would make every check below vacuous.
        assert column.role in ("affixed_number", "joined_numbers"), (
            name, column.role
        )
        published = [
            grain for grain in grains if grain.integer_valued is False
        ]
        assert published, (name, [g.integer_valued for g in grains])
        for seed in SEEDS:
            twin = generation.generate(loaded, seed)
            written = [cell for cell in twin.columns[0] if cell != ""]
            held = [
                parsing.parse_number(piece)
                for cell in written
                for piece in _pieces(cell)
            ]
            numbers = [one for one in held if one is not None]
            assert numbers, (name, seed)
            assert any(one != int(one) for one in numbers), (
                name, seed, sorted(set(written))[:6],
            )


def _pieces(cell: str) -> "list[str]":
    """The parts of one cell that might each read as a number."""
    stripped = ""
    for letter in cell:
        if letter in "0123456789.-+eE":
            stripped = stripped + letter
        else:
            stripped = stripped + " "
    return [piece for piece in stripped.split(" ") if piece != ""]


# -- 7. what adversarial round 2 reproduced -----------------------------


def test_a_grain_is_laid_out_by_the_CELL_count_which_is_R_P4_112(
    tmp_path: pathlib.Path,
) -> None:
    """R-P4-112 asserted as a WITNESS, with its root cause pinned.

    `_numeric_layout` divides a column's cells into strata by the count
    of different things it publishes, and for an affixed or joined
    column that count is over CELLS. A 36-row column of `N/M` holds 36
    different pairs while its first position holds 11 different numbers,
    so the position is laid out in 36 strata where a plain column
    carrying the same numeric facts gets 11.

    THAT IS THE ROOT, and adversarial round 2 found it; the residual's
    first diagnosis blamed the pairing step, which cannot cause it --
    each position is finished before pairing runs, and pairing only
    permutes that position's own multiset.

    IT IS ASSERTED RATHER THAN REPAIRED, and the reason is measured.
    Handing the grain its own count closes the style floor -- the first
    position writes 2 cells with a point in them where it wrote 12 to
    15 -- and costs the column's distinct-cell count, which falls from
    34 of 36 to 28, because the pairing walk then has fewer
    combinations to build it from. `distinct.n_distinct` and
    `distinct.n_distinct_folded` are published facts too, and the twin
    of the suite's own joined description stopped meeting them: the
    product's headline claim, that a twin of its own description misses
    nothing, went red. The two counts have to move together, which is
    the landing that retargets the draw.

    This witness fails when the root is repaired, which is when it
    should be rewritten to assert the repair.
    """
    joined = [
        f"{index % 9 + 1}/{index % 7 + 1}" for index in range(34)
    ] + ["1.5/2", "2.5/3"]
    _document, loaded = _described(tmp_path, joined, ["amount"])
    column = loaded.columns[0]
    assert column.role == "joined_numbers", column.role
    part = column.facts.parts[0]
    # THE FIXTURE SEPARATES THE TWO COUNTS, asserted before anything
    # rests on it: where they are equal this test measures nothing.
    assert part.n_distinct_values == 11, part.n_distinct_values
    assert column.n_distinct == 36, column.n_distinct
    view = generation._part_view(column, 0)
    assert view.n_distinct == column.n_distinct, view.n_distinct
    assert view.n_distinct_folded == column.n_distinct_folded


def test_the_joined_position_misses_its_plain_floor_which_is_R_P4_112(
    tmp_path: pathlib.Path,
) -> None:
    """The same residual from the other side, and it is REPORTED.

    The first position publishes `plain: 34` with a pool of 2 and writes
    many more cells with a point in them than the pool covers, because
    of the cardinality above.

    AND THE TWIN'S OWN REPORT DOES NOT NAME IT, while `validate` does.
    Measured: on a seed writing 14 such cells the twin's deviations
    carry `n_distinct` and nothing about the styles, and the quality
    report has `number 1 styles.published.plain` MISSED at 22 against a
    floor of 34. A person who reads the report beside their twin and
    does not run the validator is told the count of different values
    moved and is not told the form census did. That silence is recorded
    in R-P4-112 and is asserted here, so that closing it is noticed.
    """
    joined = [
        f"{index % 9 + 1}/{index % 7 + 1}" for index in range(34)
    ] + ["1.5/2", "2.5/3"]
    _document, loaded = _described(tmp_path, joined, ["amount"])
    column = loaded.columns[0]
    assert column.facts.parts[0].numeric_styles == {
        "plain": 34, contract.WITHHELD: 2,
    }
    over = 0
    for seed in SEEDS:
        twin = generation.generate(loaded, seed)
        written = [cell for cell in twin.columns[0] if cell != ""]
        firsts = [cell.split("/")[0] for cell in written]
        held = [parsing.parse_number(piece) for piece in firsts]
        numbers = [one for one in held if one is not None]
        pointed = len([one for one in numbers if one != int(one)])
        # THE TYPE SURVIVES on every seed even while the count does not,
        # which is the part that must not slip while the residual waits.
        assert pointed >= 1, (seed, sorted(set(firsts))[:8])
        if pointed > 2:
            over = over + 1
    assert over > 0, "the residual this witness records is not reproducing"

    # THE VALIDATOR NAMES IT, and the twin's own report does not.
    twin = generation.generate(loaded, SEEDS[0])
    folder = tmp_path / "joined-witness"
    folder.mkdir(exist_ok=True)
    written = fixtures.write(folder, "twin.csv", rendering.twin_csv(twin))
    outcome = validation.measure(loaded, str(written))
    missed = {
        check.subcheck
        for check in outcome.checks
        if check.verdict == validation.MISSED
    }
    assert "number 1 styles.published.plain" in missed, sorted(missed)
    assert not [
        note for note in twin.deviations if note.fact == "numeric_styles"
    ], twin.deviations


def test_numbers_too_large_to_hold_a_fraction_are_named_not_hidden(
    tmp_path: pathlib.Path,
) -> None:
    """The twin cannot always keep the type, and must never hide it.

    Above about two to the fifty-third the gap between one representable
    number and the next is more than a whole unit — at two to the
    fifty-fifth it is eight — so a share up there holds no value with a
    point in it at all. A column of 995 such numbers beside one `0.5`
    publishes `integer_valued: false` and has nowhere to put the half.
    The twin writes whole numbers throughout and re-describes as a
    column of counts, which is permitted; doing it in SILENCE is not,
    and it did (round 2, item 1).
    """
    values = ["0"] * 5 + ["0.5"] + ["36028797018963968"] * 995
    document, loaded = _described(tmp_path, values)
    assert document["columns"][0]["integer_valued"] is False
    for seed in (0, 1, 2):
        twin = generation.generate(loaded, seed)
        named = [
            note for note in twin.deviations
            if note.fact == "integer_valued"
        ]
        assert named, (seed, twin.deviations)
        assert named[0].published == "no"
        assert named[0].achieved == "yes"


def test_a_narrowed_carrier_keeps_both_the_type_and_the_floor(
    tmp_path: pathlib.Path,
) -> None:
    """Round 2, item 2, end to end: both obligations, not one of them.

    Two `0`, one `0.5` and 197 `2` publish `plain: 199` with a pool of
    one, and the ladder allots strata of 2, 2 and 196. No single-cell
    stratum exists, so keeping the type meant giving the two-cell middle
    stratum a value with a point in it and missing an exactly achievable
    `plain: 199` by one. The source's own `0.5` covers one row, so both
    were always reachable together.
    """
    values = ["0"] * 2 + ["0.5"] + ["2"] * 197
    document, loaded = _described(tmp_path, values)
    published = document["columns"][0]
    assert published["numeric_styles"] == {"plain": 199, "(withheld)": 1}
    for seed in SEEDS:
        twin = generation.generate(loaded, seed)
        written = [cell for cell in twin.columns[0] if cell != ""]
        held = [parsing.parse_number(cell) for cell in written]
        numbers = [one for one in held if one is not None]
        pointed = len([one for one in numbers if one != int(one)])
        assert pointed == 1, (seed, sorted(set(written)))
        assert _styles(twin).get("plain", 0) == 199, (seed, _styles(twin))
        assert list(twin.deviations) == [], (seed, twin.deviations)


def test_no_two_strata_are_given_the_same_whole_number() -> None:
    """Point 4, on the walk itself, where the guard actually lives.

    The share walk is the one rule in this repair that chooses a value
    rather than a form, so it is held to its four bounds directly: the
    nearest whole number first; a number another stratum holds refused;
    a step permitted only INSIDE the stratum's own share of the ladder;
    zero never crossed; and no answer at all rather than a wrong one.
    """
    band = generation._BAND_POSITIVE
    empty: dict[float, int] = {}
    wide = (0.5, 20.0)
    # The nearest, when nothing stands in the way.
    assert generation._whole_inside(
        4.4, band, (1.0, 9.0), wide, 4, empty
    ) == 4.0
    # The nearest is taken: step inside the share.
    assert generation._whole_inside(
        4.4, band, (1.0, 9.0), wide, 4, {4.0: 1}
    ) == 5.0
    assert generation._whole_inside(
        4.4, band, (1.0, 9.0), wide, 4, {4.0: 1, 5.0: 1}
    ) == 3.0
    # The share is too narrow to hold a second whole number.
    assert generation._whole_inside(
        4.4, band, (4.0, 4.2), wide, 4, {4.0: 1}
    ) is None
    # A positive stratum never steps onto or past zero.
    assert generation._whole_inside(
        0.4, band, (-5.0, 5.0), (-9.0, 9.0), 4, {}
    ) == 1.0
    # A negative stratum likewise.
    assert generation._whole_inside(
        -0.4, generation._BAND_NEGATIVE, (-5.0, 5.0), (-9.0, 9.0), 4, {}
    ) == -1.0
    # The published ends bind the NEAREST candidate too: rounding 88.5
    # up would put a value above a published `max` of 88.5.
    assert generation._whole_inside(
        88.5, band, (7.0, 88.5), (1.5, 88.5), 4, {}
    ) == 88.0
    # With no ladder there is no share, so only the nearest is offered.
    assert generation._whole_inside(
        4.4, band, None, None, 4, {4.0: 1}
    ) is None


def test_every_measured_bound_still_holds_over_the_battery(
    tmp_path: pathlib.Path,
) -> None:
    """Point 4's other half: the widened rung window is still met.

    The carrier step spends ladder conformance to buy an exact style
    map, and method G5.6 reads its own `g_max` off the strata the step
    produces -- so the window widens by exactly what was spent and the
    measurement must still land inside it. A window that quietly stopped
    holding would be the same defect in another place.
    """
    for name, _document, loaded in _cases(tmp_path):
        for seed in SEEDS:
            twin = generation.generate(loaded, seed)
            outside = [
                measured
                for measured in twin.approximations
                if not measured.inside
            ]
            assert outside == [], (name, seed, outside)


# -- 5. one mutant per rule the repair rests on ------------------------


def test_the_carrier_step_is_what_places_the_reviewed_map(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mutant 1: put the even split back, and the item's case returns.

    `_carrier_sizes` is reverted to the identity it was before the
    repair, which is exactly method G5.2 without its carrier step. The
    reviewed column must then miss its published map again -- if it does
    not, this file is proving nothing about that step.
    """
    document, loaded = _described(tmp_path, REVIEWED)
    assert _styles(generation.generate(loaded, 0)) == {
        "plain": 20, "decimal": 31,
    }

    monkeypatch.setattr(
        generation,
        "_carrier_sizes",
        lambda sizes, bands, flags, demand, plus_demand: sizes,
    )
    written = _styles(generation.generate(loaded, 0))
    assert written.get("plain", 0) < 20, written
    assert document["columns"][0]["numeric_styles"]["plain"] == 20


def test_the_band_step_is_what_reaches_a_stranded_sign_band(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mutant 2: leave the band share alone, and two NAMED counts fall.

    THE SHAPE, AND WHY IT STILL REACHES THE STEP. The share of strata
    between the two sign bands follows the LADDER'S PLATEAUS now and no
    longer the cells (residual R-P4-49), so a band is stranded only
    where the ladder gives it FEW different values beside the other
    band's many. This column's eleven negative cells hold two -- the
    published `min` of `-20.5` and a run of `-20` -- which the ladder
    reads as THREE plateaus, against EIGHT over the ten positive cells;
    five strata shared in that proportion leave the negative side ONE.
    That one is the pinned `min`, and it carries a point, so no cell of
    the band can be written point-free at all: without the band step all
    eleven come out `-20.5`, and the twin misses BOTH published counts,
    not only the pooled remainder.
    """
    document, loaded = _described(tmp_path, BAND)
    published = document["columns"][0]["numeric_styles"]
    assert published == {"plain": 20, "leading_zero": 12, "(withheld)": 1}
    written = _styles(generation.generate(loaded, 0))
    assert written["leading_zero"] == 12
    assert written["plain"] >= 20

    monkeypatch.setattr(
        generation,
        "_carrier_bands",
        lambda negatives, zeros, positives, low, high, rungs, whole, demand,
        plus_demand: (low, high),
    )
    after = _styles(generation.generate(loaded, 0))
    assert after.get("leading_zero", 0) < 12, after
    assert after.get("plain", 0) < 20, after


def test_the_share_walk_is_what_places_a_flat_ladder(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mutant 2: refuse the step inside the share, and a flat half fails.

    Where a column's commonest value IS one of its published ends, the
    ladder is flat on that side and the interior stratum rounds onto the
    pinned end's own number. The repair steps to the next whole number
    inside that stratum's own share; this mutant gives up instead, which
    is what the code did before, and the published `plain` count goes
    unwritten.

    THE SHAPE, AND WHY IT REACHES THE REPAIR. Twenty-eight cells over
    three different values: a fractional minimum of `1.5`, seven cells
    of `8.5`, and fifteen of `9`, which is both the commonest value and
    the published maximum. Three different values give three strata, and
    the two ends are pinned, so exactly ONE stratum is free -- the
    smallest arrangement in which this walk can be the thing that
    decides. The ladder is flat at `9` from `p50` up, which puts that
    one stratum's share at `7.0` to `9.0` and its own value at `8.5` or
    above. Every such value rounds to `9` by the ties rule of G5.4, and
    `9` is the pinned maximum's number, already taken -- so the NEAREST
    whole number can never answer here and only the walk can. It steps
    one unit down to `8`, which is inside the stratum's own share, and
    the fifteenth point-free cell is written. The mutant, which has the
    walk removed, hands back nothing and the twin writes fourteen.

    A FIXTURE THAT REACHES A REPAIR IS NOT THE SAME AS ONE THAT ONCE
    DID. This test drew on `["4"] * 30 + ["9.5"] * 10 + ["12.5"] * 8`
    until the share-out of a column's cells stopped being an even split
    and began following the runs of the ladder (method G5.2a/G5.2b);
    under the runs, that column's strata carry enough whole numbers on
    their own and `_whole_inside` is called ZERO times on every seed
    here, so the mutant changed nothing and the test asserted nothing.
    """
    values = ["1.5"] * 6 + ["8.5"] * 7 + ["9"] * 15
    _document, loaded = _described(tmp_path, values)
    keep = generation._whole_inside
    seeds = [seed for seed in SEEDS]

    def nearest(value, band, share, ends, reach, taken, later=()):
        """The repair with its share walk removed: the nearest, or none."""
        return keep(value, band, None, ends, 0, taken, later)

    before = [_styles(generation.generate(loaded, seed)) for seed in seeds]
    monkeypatch.setattr(generation, "_whole_inside", nearest)
    after = [_styles(generation.generate(loaded, seed)) for seed in seeds]

    assert all(one.get("plain", 0) == 15 for one in before), before
    assert any(one.get("plain", 0) < 15 for one in after), after


def test_the_pool_gives_way_before_a_named_count(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mutant 3: let the pool compete, and a NAMED count is missed.

    Twenty-five named `leading_zero` cells and a pooled remainder of ten
    over thirty-three point-free cells: something must give. The repair
    gives up the anonymous claim; this mutant hands the pool the same
    standing as the named count, which is what the placement did before,
    and the named twenty-five comes out twenty-four.
    """
    values = ["1.5"] * 5 + ["007"] * 25 + ["88.5"] * 5
    document, loaded = _described(tmp_path, values)
    assert document["columns"][0]["numeric_styles"] == {
        "leading_zero": 25, "(withheld)": 10,
    }
    assert _styles(generation.generate(loaded, 0))["leading_zero"] == 25

    keep = generation._style_places
    monkeypatch.setattr(
        generation,
        "_style_places",
        lambda quotas, holds, whole_column, pool=0: keep(
            quotas, holds, whole_column, 0
        ),
    )
    written = _styles(generation.generate(loaded, 0))
    assert written.get("leading_zero", 0) < 25, written


def test_a_generator_that_stops_choosing_styles_is_caught(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mutant 4: remove the style step, and the recount says so.

    The style-removal mutant of the review item. Every cell is written
    in whatever form its own value falls into, which is what a generator
    with no style rule at all would do. The published map is then missed
    and the report names it -- so the recount is a check that can fail,
    and the passing runs above mean what they say.
    """
    document, loaded = _described(tmp_path, REVIEWED)
    assert [
        note
        for note in generation.generate(loaded, 0).deviations
        if note.fact == "numeric_styles"
    ] == []

    monkeypatch.setattr(
        generation,
        "_style_places",
        lambda quotas, holds, whole_column, pool=0: [
            "plain" if whole_column else "decimal" for _cell in holds
        ],
    )
    twin = generation.generate(loaded, 0)
    assert _styles(twin) == {"decimal": 51}
    named = [note for note in twin.deviations if note.fact == "numeric_styles"]
    assert named, "the map was missed and the report said nothing"
    assert document["columns"][0]["numeric_styles"]["plain"] == 20
