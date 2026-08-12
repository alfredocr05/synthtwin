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

import pathlib

import pytest

import fixtures
from synthtwin import (
    canonical,
    contract,
    generation,
    parsing,
    profile,
    reading,
    taxonomy,
)

# The seeds of the item's own closure check, and the seed of every
# frozen reference-vector case, so the claim is not one seed wide.
SEEDS = (0, 1, 2, 3, 63, 12345) + tuple(range(101, 114))

# The column of review item P2-C4-F3, written out once so that every
# test that needs it is looking at the same fifty-one cells.
REVIEWED = ["1.5"] * 11 + ["100"] * 20 + ["200.5"] * 20

# A column whose negative side holds ten cells and, under the even
# share of G5.2, ONE stratum -- the pinned `min` of `-45.5`, which
# carries a point. Every negative cell is stuck on it until the band
# step of the carrier rule gives that side a second stratum.
BAND = (
    ["023"] * 20
    + ["-044"] * 6
    + ["45"] * 5
    + ["00"] * 15
    + ["-45.5"] * 4
    + ["42"] * 4
    + ["38"] * 4
)

# A 54-cell column on which two neighbouring strata can reach the same
# whole number: the one sitting under the flat rung at `4` rounds onto
# it, and the stratum whose share IS that rung has no other. Which of
# them got it used to turn on a drawn value, so the published `plain`
# count came out 26 on some seeds and 20 on others.
CONTENDED = (
    ["-44.5"] * 2
    + ["-7"] * 9
    + ["3.125"] * 6
    + ["3.25"] * 10
    + ["3.375"] * 7
    + ["4"] * 17
    + ["32.75"] * 3
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


def _described(
    folder: pathlib.Path, values: "list[str]"
) -> "tuple[dict, contract.Profile]":
    """Write a one-column table, describe it, load the description."""
    path = fixtures.write(
        folder, "table.csv", fixtures.single_column_table("amount", values)
    )
    table = reading.read_table(str(path))
    document = profile.build_document(table, taxonomy.Settings(), [])
    target = folder / "table-profile.json"
    target.write_text(
        canonical.serialize(document), encoding="utf-8", newline="\n"
    )
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
    value can be written in digits alone exactly when it is whole and
    its digits are the shortest round trip's, which the contract's
    fixed-point window holds up to `1e+16`.
    """
    return float(value).is_integer() and abs(value) < 1e16


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


def test_a_map_the_ends_cannot_hold_is_named_in_the_report(
    tmp_path: pathlib.Path,
) -> None:
    """The floor under point 3: the ceiling is not a licence to be quiet.

    Forty named `plain` cells and six pooled ones over forty-six cells
    ask for every cell to carry no point, while one must read back as
    `0.5` and one as `9.25`. The twin writes the forty-four it can, and
    the report names each published count beside the achieved one --
    saying which part of the forty-six the description names and which
    part it held back, because forty-six appears nowhere in the profile
    and a reader checking the report against it must be able to.
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
    assert {note.achieved for note in named} == {"44", "2"}
    spoken = sorted(note.published for note in named)
    assert spoken[0] == "0 cell(s) written in the decimal form"
    assert spoken[1].startswith(
        "46 cell(s) written in the plain form -- 40 the description "
        "names and 6 it held back"
    )


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
        assert list(twin.deviations) == [], seed


def test_the_reach_step_is_what_places_the_crowded_ladder(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mutant 5: put the optimistic count back, and P2-C5-F3 returns.

    `_reach_sizes` is reverted to the identity, which is exactly G5.2's
    carrier step as it stood when the review found this column: the cell
    step counts a stratum as a carrier because the values step MAY take
    it to a whole number, sees enough of them, and moves nothing. The
    reviewer's own 20/62 comes straight back, so this file is proving
    something about that step rather than about the seed.
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
    written = _styles(generation.generate(loaded, 0))
    assert written.get("plain", 0) < 34, written


def test_the_flat_rung_claim_is_what_keeps_the_map_seed_free(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mutant 6: let the walk claim a later stratum's only number.

    A stratum sitting just under a flat rung rounds ONTO that rung's
    number, which is the only one the stratum whose share IS that rung
    can ever be given. Without the bar in `_held_later` which of them
    got a form turned on a drawn value, and a 54-cell producer column
    published 26 point-free cells while writing 26 on some seeds and 20
    on others. The mutant restores that, and the column must part
    company with its own published count on at least one seed.
    """
    document, loaded = _described(tmp_path, CONTENDED)
    published = _named(document["columns"][0]["numeric_styles"])
    assert published == {"plain": 26, "decimal": 28}
    before = [_styles(generation.generate(loaded, seed)) for seed in SEEDS]
    for step in range(len(SEEDS)):
        for style, count in published.items():
            assert before[step].get(style, 0) >= count, (SEEDS[step], style)

    monkeypatch.setattr(generation, "_held_later", lambda candidate, later: False)
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
        lambda quotas, layout, values, whole, wanted, styles: styles,
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

    This column's ten negative cells sit under one stratum, because the
    even share of G5.2 gives the negative side one -- and that one is
    the pinned `min` of `-45.5`, which carries a point. Without the band
    step no cell of that band can be written point-free, and the twin
    misses BOTH published counts, not only the pooled remainder.
    """
    document, loaded = _described(tmp_path, BAND)
    published = document["columns"][0]["numeric_styles"]
    assert published == {"plain": 13, "leading_zero": 41, "(withheld)": 4}
    written = _styles(generation.generate(loaded, 0))
    assert written["leading_zero"] == 41
    assert written["plain"] >= 13

    monkeypatch.setattr(
        generation,
        "_carrier_bands",
        lambda negatives, zeros, positives, low, high, rungs, whole, demand,
        plus_demand: (low, high),
    )
    after = _styles(generation.generate(loaded, 0))
    assert after.get("leading_zero", 0) < 41, after
    assert after.get("plain", 0) < 13, after


def test_the_share_walk_is_what_places_a_flat_ladder(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mutant 2: refuse the step inside the share, and a flat half fails.

    Where a column's commonest value IS its published minimum, the
    ladder's lower half is flat and the interior stratum rounds onto the
    pinned end's own number. The repair steps to the next whole number
    inside that stratum's own share; this mutant gives up instead, which
    is what the code did before, and the published `plain` count goes
    unwritten.
    """
    values = ["4"] * 30 + ["9.5"] * 10 + ["12.5"] * 8
    _document, loaded = _described(tmp_path, values)
    keep = generation._whole_inside
    seeds = [seed for seed in SEEDS]

    def nearest(value, band, share, ends, reach, taken, later=()):
        """The repair with its share walk removed: the nearest, or none."""
        return keep(value, band, None, ends, 0, taken, later)

    before = [_styles(generation.generate(loaded, seed)) for seed in seeds]
    monkeypatch.setattr(generation, "_whole_inside", nearest)
    after = [_styles(generation.generate(loaded, seed)) for seed in seeds]

    assert all(one.get("plain", 0) == 30 for one in before), before
    assert any(one.get("plain", 0) < 30 for one in after), after


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
