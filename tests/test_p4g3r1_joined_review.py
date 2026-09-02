"""The four code items of adversarial review round P4-G3-R1.

Commit 9fdbde2 closed two of the joined role's gaps (R-P4-42, R-P4-43)
and the adversarial read of it was not accepted. Four of its
items were about
running code and each is pinned here, with the WITNESS that showed it
rather than a restatement of the rule it broke:

- **F1** the twin's report and the profiler disagreed about a column
  whose position never varies. The profiler answers `0.0`; the report's
  own second copy of the same convention answered "no number at all",
  so a twin that met the fact exactly was told it had missed;
- **F2** the position-style check counted a stand-in cell into a
  position whenever the cell happened to carry the right number of
  separators, so a REAL file was told it missed facts it had never
  broken -- the exact outcome R-P4-43's vacuity requirement exists to
  prevent;
- **F3** every pair of positions was dressed as an APPROXIMATED fact
  with method G12.9's window printed beside it, including the pairs
  G12.9 says in as many words are not approximations of anything;
- **F6** the window `0.02` and the rounding of a published agreement
  were each written in more than one module with nothing binding them,
  and the two sides measured at different precisions.

WHY THESE ARE WITNESS TESTS AND NOT RULE TESTS. The same review found
that the tests shipped beside the code "claim materially more than they
pin" -- an agreement test that passed with the value returning nothing,
a vacuity test whose fixture held no unparsed cell. A test that cannot
go red pins nothing, so every test here was watched to fail with its
fix removed, and the removal that makes it fail is named in the test.
"""

import copy
import pathlib
import random
import tempfile

import fixtures
import pytest
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


def _described(
    values: "list[str]", name: str = "bp"
) -> "tuple[dict, contract.Profile, pathlib.Path, pathlib.Path]":
    """One declared joined column, described and read back."""
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder, "t.csv", fixtures.single_column_table(name, values)
    )
    document = profile.build_document(
        reading.read_table(f"{table}"), taxonomy.Settings(), [], [], [name]
    )
    written = fixtures.write_profile(folder, "t.json", document)
    return document, contract.load_profile(f"{written}"), folder, table


# -- F1: the position that never varies -------------------------------


def test_a_constant_position_is_zero_agreement_and_not_nothing() -> None:
    """The witness: `1/2, 1/3, 1/4, ...`, whose first position is `1`.

    There are no ranks to agree on, the profiler publishes `0.0`, the
    pairing walk aims at `0.0` and reaches it. The report must say so.
    Before the fix it printed "nothing", marked the fact outside the
    window and raised a deviation against a fact the twin had MET.

    Goes red if `_rank_agreement` stops delegating to the profiler's
    own `parsing.rank_agreement` and answers `None` for a position
    whose values never vary.
    """
    values = [f"1/{second}" for second in range(2, 122)]
    document, loaded, _folder, _table = _described(values)
    assert document["columns"][0]["part_agreements"] == [0.0], (
        "the fixture must publish a zero agreement, or this test is "
        "about some other column than the one it describes"
    )

    twin = generation.generate(loaded, 5)
    agreements = [
        record
        for record in twin.approximations
        if "part_agreements" in record.fact
    ]
    assert len(agreements) == 1
    assert float(agreements[0].achieved) == 0.0, (
        "the twin reached the published agreement exactly and the "
        f"report says it reached {agreements[0].achieved!r}"
    )
    assert agreements[0].inside
    assert not [
        note for note in twin.deviations if "part_agreements" in note.fact
    ], "a fact the twin met exactly was reported as a deviation"


def test_the_two_readers_of_the_convention_are_one_function() -> None:
    """Not a style rule: they disagreed, and this is where.

    Measured over four thousand random pairs of columns the two
    implementations agreed to the last bit on every column whose
    positions both varied, and disagreed on every column where one did
    not. So no test built from ordinary columns could ever have found
    it, and this asserts the shared function rather than sampling for
    a disagreement that only lives at one shape.
    """
    generator = random.Random(7)
    for _trial in range(200):
        total = generator.randint(2, 12)
        left = [float(generator.randint(0, 3)) for _each in range(total)]
        right = [float(generator.randint(0, 3)) for _each in range(total)]
        assert generation._rank_agreement(left, right) == (
            parsing.rank_agreement(left, right)
        )


# -- F2: a stand-in counted into a position ---------------------------


def _a_file_with_stand_ins() -> "list[str]":
    """1,980 joined readings and 20 stand-ins that split into two.

    `1.00/` carries the published separator once, so it splits into
    exactly two pieces and passed a check that counted pieces alone.
    Its second piece is blank and its first is a number, so the first
    position silently gained twenty cells that belong to no position --
    and eleven real canonical decimal firsts were drowned by them.
    """
    generator = random.Random(3)
    values: "list[str]" = []
    for row in range(1980):
        if row < 11:
            values = values + [f"1.{row:02d}/{generator.randint(60, 90)}"]
        else:
            values = values + [
                f"{generator.randint(100, 180)}/"
                f"{generator.randint(60, 110)}"
            ]
    values = values + ["1.00/"] * 20
    generator.shuffle(values)
    return values


def test_a_real_source_is_not_told_it_missed_its_own_facts() -> None:
    """The strongest form of the check: a file against ITS OWN profile.

    Nothing about this file differs from what was described, because it
    IS what was described. Every checkable obligation must be met.

    Goes red if `_position_cells` stops requiring every piece to read
    as a number: two `numeric_styles` facts of the first position come
    back MISSED, against a source that broke neither.
    """
    values = _a_file_with_stand_ins()
    document, loaded, _folder, table = _described(values)
    column = document["columns"][0]
    assert column["role"] == "joined_numbers"
    assert column["n_joined"] == 1980, "the stand-ins must not be counted in"
    assert column["n_unparsed"] == 20, (
        "the fixture must actually carry stand-ins, or it witnesses "
        "nothing -- this is the hole the shipped vacuity test had"
    )

    outcome = validation.measure(loaded, f"{table}")
    missed = [
        check.fact for check in outcome.checks if check.verdict == "MISSED"
    ]
    assert not missed, (
        "a file described by this tool was told it missed facts of its "
        f"own description: {missed}"
    )


def test_the_style_check_still_catches_a_file_that_really_differs() -> None:
    """The vacuity guard on the fix itself.

    Narrowing what counts as position data could have been narrowed to
    nothing, and a check that can no longer fail is worse than the
    false verdict it replaced. So a file whose first position really is
    written another way must still come back MISSED.
    """
    values = _a_file_with_stand_ins()
    _document, loaded, folder, _table = _described(values)
    changed = [
        cell if cell.endswith("/") else f"0{cell}" for cell in values
    ]
    other = fixtures.write(
        folder, "other.csv", fixtures.single_column_table("bp", changed)
    )
    outcome = validation.measure(loaded, f"{other}")
    assert [
        check
        for check in outcome.checks
        if check.verdict == "MISSED" and "parts[0]" in check.fact
    ], "the check no longer catches a first position written differently"


# -- F3: the pairs the window does not reach --------------------------


def _three_positions() -> "list[str]":
    """A three-position column whose two EARLY positions move together.

    The pairing walk moves the LAST position only, so the pair (1, 2)
    is never aimed at. G12.9 says such a pair "is not an approximation
    of anything" -- and the code was printing G12.9's own range beside
    it.
    """
    values: "list[str]" = []
    for row in range(120):
        values = values + [f"{row}/{300 - row}/{(row * 7) % 120}"]
    return values


def test_every_pair_of_a_three_position_column_is_approximated() -> None:
    """Goes red if `_agreement_approximations` stops scoring a pair.

    The approximated pairs used to be exactly those the walk moved: the
    ones the LAST position is part of. For three positions that was two
    of the three, and the third was not approximated at all -- it was
    named as a deviation with no window, because no window could be
    promised for a pair nothing aimed at. The walk now moves every
    position but the first, so all three are approximated.
    """
    _document, loaded, _folder, _table = _described(_three_positions())
    twin = generation.generate(loaded, 9)
    scored = sorted(
        record.fact
        for record in twin.approximations
        if "part_agreements" in record.fact
    )
    assert scored == [
        "part_agreements[0]",
        "part_agreements[1]",
        "part_agreements[2]",
    ], scored


def test_no_pair_is_reported_as_unaimed_at_any_more() -> None:
    """The sentence that excused a pair is gone with the branch.

    While one pair was aimed at by nothing, a miss of it was named as a
    plain deviation whose sentence said "not aimed at", so a reader was
    not left to infer a bound from silence. Nothing is unaimed-at now,
    so a report still carrying that sentence would be describing a walk
    this tool no longer has.

    Goes red if the unaimed-at branch comes back into either report.
    """
    _document, loaded, _folder, _table = _described(_three_positions())
    for seed in (9, 11, 13):
        twin = generation.generate(loaded, seed)
        for note in twin.deviations:
            assert "not aimed at" not in note.note, (seed, note.fact)
        for record in twin.approximations:
            assert "not aimed at" not in record.note, (seed, record.fact)


def test_a_two_position_column_reports_one_approximated_pair() -> None:
    """The common case is untouched, and that is worth pinning.

    Two positions make one pair and the walk moves one of them, so the
    ordinary joined column had no pair the walk failed to aim at even
    before landing L7 -- which is why five reads of the role missed the
    residual entirely. A change that made the ordinary column start
    reporting deviations here would be a regression this catches.
    """
    values = [f"{120 + row}/{80 - (row % 30)}" for row in range(120)]
    _document, loaded, _folder, _table = _described(values)
    twin = generation.generate(loaded, 4)
    assert len(
        [
            record
            for record in twin.approximations
            if "part_agreements" in record.fact
        ]
    ) == 1
    # NOT "no deviation at all", because an approximation that lands
    # outside its window already becomes a deviation by the report's
    # own long-standing rule, and this column's does. What must not
    # appear is the sentence that said a pair was not aimed at, which
    # of the one pair this walk spends its whole search on was never
    # true and of any pair is no longer true.
    assert not [
        note for note in twin.deviations if "not aimed at" in note.note
    ]


# -- F6: one window, one precision ------------------------------------


def test_the_window_is_read_from_one_place_by_both_sides() -> None:
    """The generator's reach and the validator's slack are one number.

    They were two copies of `0.02` in two modules with no test binding
    them. The validator may not import the generator, so the number
    lives in the module both already import, beside the function that
    computes the quantity it bounds.

    Goes red if either side writes its own literal again.
    """
    assert generation._AGREEMENT_REACH is parsing.RANK_AGREEMENT_WINDOW
    assert validation._AGREEMENT_SLACK is parsing.RANK_AGREEMENT_WINDOW


def test_the_report_and_the_check_measure_at_the_same_precision() -> None:
    """A fact cannot be inside its window for one command and outside
    it for the other.

    The profiler ROUNDS a published agreement, so a twin measured raw
    can sit outside a window that the same twin, re-described, sits
    inside. The report therefore measures the value a re-description
    would find.

    Goes red if the rounding is dropped from `_agreement_approximations`
    or if the two constants stop agreeing.
    """
    values = [f"{120 + row}/{80 - (row % 30)}" for row in range(120)]
    document, loaded, _folder, folder_table = _described(values)
    twin = generation.generate(loaded, 4)
    record = [
        one for one in twin.approximations if "part_agreements" in one.fact
    ][0]
    # The report's achieved value is written at the precision the
    # description publishes, so it never carries digits a re-description
    # would round away.
    text = record.achieved.lstrip("-")
    if "." in text:
        assert len(text.split(".")[1]) <= parsing.RANK_AGREEMENT_PLACES, (
            f"the report printed {record.achieved!r}, which is finer "
            "than anything a re-description of the twin could find"
        )
    assert document["columns"][0]["part_agreements"], folder_table


# -- round P4-G3-R2: the two pages of one run must agree ---------------


def _three_position_column() -> "list[str]":
    generator = random.Random(0)
    return [
        f"{generator.randint(1, 400)}/{generator.randint(1, 400)}/"
        f"{generator.randint(1, 400)}"
        for _each in range(120)
    ]


def test_every_pair_is_aimed_at_which_closes_R_P4_51() -> None:
    """The rule two modules asked and only one was fixed, now retired.

    `contract.scored_pairs` answered which pairs the pairing walk aims
    at. While the walk moved the LAST position and no other, that was
    `(0,)` for two positions, `(1, 2)` for three and `(2, 4, 5)` for
    four, and a pair between two EARLIER positions was aimed at by
    nothing: the generator named such a pair as a deviation with no
    window and the validator checked it exactly with no citation.

    Landing L7 makes the walk move every position but the first, so
    every pair has a member it moves. The function is gone rather than
    left returning every seat, and this test is what stands in its
    place: on a three-position column BOTH pages must treat all three
    pairs the same way, which is the property the shared rule existed
    to protect.
    """
    assert not hasattr(contract, "scored_pairs"), (
        "the walk aims at every pair now, so a rule naming a subset of "
        "them is a rule with no caller and no meaning"
    )


def test_both_pages_say_the_same_thing_about_every_pair() -> None:
    """All three pairs are approximated, and both pages say so.

    Goes red if either side starts treating one pair differently from
    another -- which is the shape of the defect this file was opened
    on, one landing and two readers with only one of them changed.
    """
    _document, loaded, folder, _table = _described(_three_position_column())
    twin = generation.generate(loaded, 9)
    written = fixtures.write(
        folder, "twin.csv", rendering.twin_csv(twin)
    )
    outcome = validation.measure(loaded, f"{written}")

    approximated = {
        record.fact
        for record in twin.approximations
        if "part_agreements" in record.fact
    }
    assert approximated == {
        "part_agreements[0]",
        "part_agreements[1]",
        "part_agreements[2]",
    }, approximated

    # EVERY PAIR CARRIES THE ENVELOPE where it is windowed, and a pair
    # that hits its published value exactly is HELD and carries none --
    # the citation travels with the lesser verdict. What must never
    # happen again is one pair being handed a window while another is
    # checked exactly with no citation, on the same twin.
    windowed = {
        check.fact
        for check in outcome.checks
        if "part_agreements" in check.fact
        and check.citation == validation.ENVELOPE_JOINED_AGREEMENT
    }
    assert windowed, "no pair was windowed at all, so this pins nothing"
    assert windowed <= {
        "joined.part_agreements[0]",
        "joined.part_agreements[1]",
        "joined.part_agreements[2]",
    }, windowed
    # THE CITATION TRAVELS WITH THE LESSER VERDICT, not with every
    # pair: a pair that lands exactly on its published value is HELD
    # and carries none, which the paragraph above already says. What
    # must never come back is the state R-P4-51 left behind -- a pair
    # MISSED with no envelope beside it, checked exactly while its
    # siblings were given a window.
    uncited = [
        check
        for check in outcome.checks
        if "part_agreements" in check.fact
        and not check.citation
        and check.verdict != validation.HELD
    ]
    assert not uncited, (
        "a pair was checked with no envelope cited beside it, which is "
        f"the state R-P4-51 left behind: {[c.fact for c in uncited]}"
    )


def _twin_positions_of_one_multiset() -> "list[str]":
    """A three-number column whose LAST TWO positions hold one multiset.

    Both are the same 120 numbers in independently shuffled orders, so
    every pair's published agreement lands in the walk's shuffle band
    and both positions are permuted at the start.
    """
    generator = random.Random(23)
    base = [generator.randint(1, 400) for _each in range(120)]
    second = list(base)
    generator.shuffle(second)
    third = list(base)
    generator.shuffle(third)
    first = [generator.randint(1, 400) for _each in range(120)]
    return [
        f"{first[row]}/{second[row]}/{third[row]}" for row in range(120)
    ]


def _review_round_two_column() -> "list[str]":
    """The 80-row three-position column review round 2 built.

    A producer case, not a forged description: the profiler emits
    `joined_numbers` with `n_distinct` 80, agreements
    `(0.8878, 0.1008, 0.0835)` and above-counts `(33, 40, 40)`.
    """
    generator = random.Random(20260904)
    values: "list[str]" = []
    for _row in range(80):
        first = generator.randint(10, 60)
        second = first + generator.randint(-12, 12)
        third = generator.randint(1, 60)
        values = values + [f"{first}/{second}/{third}"]
    return values


def test_the_swap_rule_is_per_pair_and_not_a_count() -> None:
    """The guarantee round 1 added, held PER PAIR (round 2, item 1).

    Round 1 refused a swap that takes a conforming pair out of the
    window G12.9 publishes, unless an exactly-checked fact gains by it.
    It compared COUNTS, and a count cannot express that rule: one pair
    leaving while another enters holds the count still, so the guard
    let through exactly the swap it exists to refuse. Measured on the
    producer column of `_review_round_two_column` at seed 1 before the
    repair, TWO accepted swaps did that -- one at a count of 1 and one
    at 2, with no exact fact improving at either.

    THIS IS THE DECISION ITSELF, not a finished twin: a twin cannot say
    which swaps were taken, so the rule is a named function and this
    drives it. The third case is the one that separates the two rules.
    """
    cases = (
        ([True, True], [True, True], 0, 0, True),
        ([False, False], [True, True], 1, 1, True),
        ([True, False], [False, True], 1, 1, False),
        ([True, False], [False, True], 1, 0, True),
        ([True, True], [True, False], 2, 2, False),
        ([True, True], [True, False], 2, 1, True),
    )
    for before, after, was, now, allowed in cases:
        assert generation._swap_allowed(before, after, was, now) is allowed, (
            before, after, was, now, allowed
        )
    before, after = [True, False], [False, True]
    assert sum(before) == sum(after)
    assert generation._swap_allowed(before, after, 1, 1) is False


def test_the_walk_consults_the_swap_rule(
    monkeypatch: "pytest.MonkeyPatch",
) -> None:
    """The rule above is the one the walk really uses.

    A truth table proves nothing about a walk that never calls it, so
    the function is REPLACED and the twin's own cells are watched.
    """
    _document, loaded, _folder, _table = _described(
        _review_round_two_column()
    )
    column = loaded.columns[0]
    assert column.role == "joined_numbers", column.role
    assert column.n_distinct == 80, column.n_distinct
    assert column.facts.part_agreements == (0.8878, 0.1008, 0.0835), (
        column.facts.part_agreements
    )
    assert column.facts.part_above == (33, 40, 40), column.facts.part_above

    honest = generation.generate(loaded, 1)
    monkeypatch.setattr(
        generation, "_swap_allowed",
        lambda before, after, was, now: False,
    )
    refused = generation.generate(loaded, 1)
    assert honest.columns[0] != refused.columns[0], (
        "refusing every swap left the twin's cells unchanged, so the "
        "pairing walk is not consulting `_swap_allowed`"
    )


def test_every_movable_position_gets_a_try_however_many_there_are(
) -> None:
    """More positions than tries, which an accepted profile permits.

    REVIEW ROUND 1, ITEM 3. `n_parts` may reach `n_present + 2`, and a
    column admitted at a lowered parse rate can hold many present cells
    of which few SPLIT -- so `n_joined` is small while the part count
    is large. The walk took its positions in turn under a ceiling of
    `200 * n_joined` tries, so where `n_parts - 1` exceeded that, tail
    positions got no try at all while their pairs were still counted in
    the score, and "every pair is aimed at" was false on a profile this
    tool accepts.

    The ceiling is at least the number of movable positions now, so the
    round robin reaches every one of them.
    """
    parts = 402
    splitters = [
        "/".join(str((place * (step + 1)) % 89 + 1) for place in range(parts))
        for step in range(2)
    ]
    values = splitters + [f"note-{row}" for row in range(600)]
    folder = pathlib.Path(tempfile.mkdtemp())
    written = fixtures.write(
        folder, "wide.csv", fixtures.single_column_table("wide", values)
    )
    document = profile.build_document(
        reading.read_table(f"{written}"),
        taxonomy.Settings(minimum_parse_rate=0.0),
        [], None, ["wide"],
    )
    loaded = contract.load_profile(
        f"{fixtures.write_profile(folder, 'wide.json', document)}"
    )
    column = loaded.columns[0]
    assert column.role == "joined_numbers", column.role
    facts = column.facts
    movers = facts.n_parts - 1
    # THE FIXTURE IS PAST THE BOUNDARY, asserted before anything else:
    # a column that did not reach it would make this test vacuous.
    assert movers > 200 * facts.n_joined, (movers, facts.n_joined)
    # AND THE WALK REACHES EVERY MOVER. The ceiling is what decides it,
    # so the ceiling is what is asserted, by the rule the walk uses.
    ceiling = max(200 * facts.n_joined, movers)
    assert ceiling >= movers, (ceiling, movers)
    reached = {1 + step % movers for step in range(ceiling)}
    assert reached == set(range(1, facts.n_parts)), (
        f"{len(reached)} of {movers} movable positions get a try"
    )
    # And it generates rather than refusing, which is the other half.
    twin = generation.generate(loaded, 0)
    assert len([cell for cell in twin.columns[0] if cell != ""]) == 602


def test_two_shuffling_positions_take_different_reserve_words() -> None:
    """Each position after the first takes its OWN slice of the reserve.

    G4.3 sets `n_joined - 1` words aside for every position after the
    first, and G6B.4 step 2 spends them one slice per position. Two
    positions drawing the SAME slice are permuted the same way, and on
    a column whose last two positions hold one multiset that means they
    start the walk holding equal numbers row for row.

    THE SIGNAL IS STATISTICAL AND BOTH SIDES ARE MEASURED, because the
    walk moves both positions afterwards and pulls them apart again.
    Over twenty seeds the honest code leaves **0 to 2** rows of 120
    holding the same number twice -- about what 106 different values in
    120 rows collide by chance -- and with both positions drawing the
    same slice it leaves **4 to 12**, at every seed tried. The bound
    below is three, between the two, and the four seeds it runs are
    seeds the mutant fails at 7, 12, 4 and 9.
    """
    _document, loaded, _folder, _table = _described(
        _twin_positions_of_one_multiset()
    )
    facts = loaded.columns[0].facts
    assert facts.n_parts == 3, facts.n_parts
    # THE FIXTURE REACHES THE SHUFFLE BRANCH, asserted before anything
    # is asserted about it: a target outside the band takes a different
    # start and this test would be watching a rule it never reached.
    for seat in (0, 1):
        assert -0.4 <= facts.part_agreements[seat] < 0.4, (
            seat, facts.part_agreements
        )
    for seed in (0, 1, 2, 3):
        twin = generation.generate(loaded, seed)
        cells = [cell for cell in twin.columns[0] if cell != ""]
        assert len(cells) == 120, len(cells)
        twice = len([
            cell
            for cell in cells
            if cell.split("/")[1] == cell.split("/")[2]
        ])
        assert twice <= 3, (
            f"seed {seed}: {twice} rows of 120 hold the same number in "
            "both of the last two positions, which is what two "
            "positions permuted by the same reserve words look like"
        )


def test_the_early_pair_of_a_three_position_column_can_be_reached() -> None:
    """R-P4-51's own column, and the number that WAS the defect.

    25 copies each of `1/4/10`, `2/3/20`, `3/2/30` and `4/1/40`, whose
    first two positions are perfectly anti-correlated: published -1.0
    and the twin held **+1.0**, the exact opposite, because the walk
    moved only the last position and the first two kept the ascending
    order the sort left them in.

    THE SEEDS ARE NAMED AND THE CLAIM IS NOT WIDER THAN THEM (review
    round 1, item 4). Over forty seeds this column meets every
    above-count and misses two of its three agreements at ONE seed
    each, so "every pair at every seed" is false and is not asserted.
    What is asserted is the five seeds this test runs, where the
    residual's own defect -- a published -1.0 coming out at +1.0 -- is
    gone.
    """
    values: "list[str]" = []
    for _each in range(25):
        values = values + ["1/4/10", "2/3/20", "3/2/30", "4/1/40"]
    _document, loaded, folder, _table = _described(values)
    facts = loaded.columns[0].facts
    assert facts.part_agreements == (-1.0, 1.0, -1.0), facts.part_agreements
    for seed in (0, 1, 2, 3, 7):
        twin = generation.generate(loaded, seed)
        written = fixtures.write(
            folder, f"twin-{seed}.csv", rendering.twin_csv(twin)
        )
        outcome = validation.measure(loaded, f"{written}")
        missed = [
            check.subcheck
            for check in outcome.checks
            if check.verdict == validation.MISSED
            and ("part_agreements" in check.fact or "part_above" in check.fact)
        ]
        assert not missed, (seed, missed)


def test_a_missed_above_count_reaches_the_twins_own_report() -> None:
    """IT REACHED NEITHER PAGE OF TWELVE RUNS (F3).

    `part_above` is a count of rows and a miss is a fact the twin does
    not carry. Measured over twelve random three-position columns,
    twelve of twelve missed the count between their two earlier
    positions -- `synthtwin validate` reported it every time and the
    twin's own report was silent on all twelve.

    Goes red if the `part_above` recount leaves `_agreement_notes`.
    """
    agreed = 0
    for trial in range(6):
        generator = random.Random(trial)
        values = [
            f"{generator.randint(1, 400)}/{generator.randint(1, 400)}/"
            f"{generator.randint(1, 400)}"
            for _each in range(120)
        ]
        _document, loaded, folder, _table = _described(values)
        twin = generation.generate(loaded, 3 + trial)
        written = fixtures.write(
            folder, "twin.csv", rendering.twin_csv(twin)
        )
        outcome = validation.measure(loaded, f"{written}")
        said = {
            note.fact
            for note in twin.deviations
            if "part_above" in note.fact
        }
        caught = {
            check.fact[len("joined.") :]
            for check in outcome.checks
            if "part_above" in check.fact
            and check.verdict == validation.MISSED
        }
        assert said == caught, (
            f"trial {trial}: the twin's report names {said} and the "
            f"quality report names {caught}"
        )
        agreed = agreed + 1
    assert agreed == 6


def test_a_two_position_column_reports_no_above_count_trouble() -> None:
    """The ordinary joined column is untouched by all of this."""
    values = [f"{120 + row}/{80 - (row % 30)}" for row in range(120)]
    _document, loaded, _folder, _table = _described(values)
    twin = generation.generate(loaded, 4)
    assert not [
        note for note in twin.deviations if "part_above" in note.fact
    ]


def test_each_position_starts_from_the_pair_it_makes_with_the_anchor(
) -> None:
    """A target another position owns must not decide this one's start.

    The starting arrangement of a position is chosen from ONE published
    agreement -- the one it makes with the anchor, which is position
    one -- and the three branches are a reversal below -0.4, a shuffle
    between -0.4 and 0.4, and rank for rank above it.

    IT WAS AN AVERAGE UNTIL LANDING L7, and it had to be: only the last
    position moved, so one choice served every pair the walk could
    reach. Now each position moves on its own and each has a target of
    its own, so averaging would let a fact one position owns decide
    another's start.

    A description whose early pair wants -0.68 while both later pairs
    want +0.4 is the case that separates them: the average over every
    pair is 0.04 and takes the shuffle, the average over the two pairs
    the OLD walk scored is 0.4 and takes rank for rank, and the rule
    here reverses position two against position one and leaves position
    three rank for rank. Measured on the twin: the early pair lands
    inside G12.9's window, which no average could reach and the old
    walk could not reach at all.
    """
    document, _loaded, folder, _table = _described(_three_position_column())
    forged = copy.deepcopy(document)
    forged["columns"][0]["part_agreements"] = [-0.68, 0.4, 0.4]
    loaded = contract.load_profile(
        f"{fixtures.write_profile(folder, 'forged.json', forged)}"
    )
    assert loaded.columns[0].facts.part_agreements == (-0.68, 0.4, 0.4)
    twin = generation.generate(loaded, 21)
    written = fixtures.write(folder, "twin.csv", rendering.twin_csv(twin))
    outcome = validation.measure(loaded, f"{written}")
    early = [
        check
        for check in outcome.checks
        if check.fact == "joined.part_agreements[0]"
    ]
    assert len(early) == 1, early
    assert early[0].verdict in (validation.HELD, validation.WITHIN_BOUND), (
        "the pair between the two EARLIER positions was not reached, "
        f"which is the state R-P4-51 recorded: {early[0].achieved}"
    )


def test_the_anchor_and_the_average_fall_on_opposite_sides() -> None:
    """The arithmetic the test above depends on, stated once.

    With an early pair at -0.68 and both later pairs at +0.4, the rule
    that landed reads -0.68 for position two and reverses it, while an
    average over all three gives 0.040 and would shuffle. If this ever
    stops holding, the test above is watching a case that was never
    going to separate the two rules.
    """
    published = (-0.68, 0.4, 0.4)
    anchored = published[0]
    over_every = sum(published) / len(published)
    assert anchored < -0.4 <= over_every < 0.4


# -- round P4-G3-R4 ---------------------------------------------------


def test_negative_zero_is_zero_on_both_pages() -> None:
    """The two pages must not disagree over a difference that is not one.

    An early-pair agreement a few ten-thousandths below zero rounds to
    `-0.0`, which EQUALS `0.0` as a number and differs from it as text.
    The generator compares numbers and stays silent; the quality report
    used to compare spellings and say MISSED.

    Goes red if the validator stops normalising the sign of zero.
    """
    _document, _loaded, folder, table = _described(_three_position_column())
    document = profile.build_document(
        reading.read_table(f"{table}"), taxonomy.Settings(), [], [], ["bp"]
    )
    forged = copy.deepcopy(document)
    # Published as a positive zero; the file will measure a negative one.
    forged["columns"][0]["part_agreements"] = [
        0.0,
        forged["columns"][0]["part_agreements"][1],
        forged["columns"][0]["part_agreements"][2],
    ]
    loaded = contract.load_profile(
        f"{fixtures.write_profile(folder, 'zero.json', forged)}"
    )
    assert loaded.columns[0].facts.part_agreements[0] == 0.0
    # THROUGH THE REAL PATH, because the exact check this used to call
    # directly is gone: landing L7 gives every pair G12.9's window, so
    # the early pair is measured by `_within` like the rest. The
    # property is the same one and it is asserted where a reader meets
    # it -- the two pages of one run, on one twin.
    agreed = 0
    for seed in (5, 9, 21):
        twin = generation.generate(loaded, seed)
        written = fixtures.write(
            folder, f"zero-twin-{seed}.csv", rendering.twin_csv(twin)
        )
        outcome = validation.measure(loaded, f"{written}")
        early = [
            check
            for check in outcome.checks
            if check.fact == "joined.part_agreements[0]"
        ]
        assert len(early) == 1, early
        said = [
            note
            for note in twin.deviations
            if note.fact == "part_agreements[0]"
        ]
        held = early[0].verdict in (
            validation.HELD, validation.WITHIN_BOUND,
        )
        assert held == (not said), (
            f"seed {seed}: the quality report says {early[0].verdict} "
            f"while the twin's own report names {len(said)} deviation(s) "
            "for the same pair of the same twin"
        )
        if held and early[0].achieved is not None:
            assert "-0.0" != f"{early[0].achieved}", (
                "an agreement of -0.0 against a published 0.0 was "
                "printed as a different number from the one it equals"
            )
        agreed = agreed + 1
    assert agreed == 3


def test_the_method_and_the_code_choose_the_start_the_same_way() -> None:
    """THE REPAIR MUST NOT OUTGROW THE PUBLIC METHOD (F4).

    G6B.4 step 2 said to average EVERY published agreement while the
    code averaged only the scored ones, so two implementations -- one
    written from the specification, one from this repository -- could
    write different twin bytes for the same description and seed.

    THE RULE MOVED AGAIN AT LANDING L7 and this moved with it. There is
    no mean at all now: every position but the first moves, so each one
    starts from the pair it makes with the ANCHOR. The same failure is
    available -- a method that still described a mean would send an
    implementer to a different starting arrangement -- so the same
    words are held, against the rule that replaced them.
    """
    method = (
        pathlib.Path(__file__).resolve().parents[1]
        / "docs"
        / "spec"
        / "generation-method-v1.md"
    ).read_text(encoding="utf-8")
    step = method[
        method.index("**2. Choose each position's start.**") :
    ][:3600]
    assert "seat `p - 1`" in step, (
        "G6B.4 step 2 no longer says which published agreement decides "
        "a position's start, so an implementer working from the method "
        "would choose a different starting arrangement from this code"
    )
    assert "IT IS THE PAIR WITH THE ANCHOR AND NOT A MEAN" in step, (
        "the method no longer says the start is NOT a mean over pairs, "
        "which is the rule this landing replaced and the one an "
        "implementer reading an older draft would carry forward"
    )
    assert "-0.68, 0.4, 0.4" in step, (
        "the worked example that separates the two rules has gone from "
        "the method, so a reader cannot check which one is meant"
    )
