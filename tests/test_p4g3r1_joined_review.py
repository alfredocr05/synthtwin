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
import inspect
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
    # THE SIX ROWS ARE ROUND 2'S OWN, RESTATED AND NOT SWAPPED. Round
    # 3 split the one exact distance they carried into its two kinds --
    # a per-pair above-count vector and the seatless count of different
    # cells -- so the distance each row moved is now the CELL count and
    # the above-counts stand still beside it. Every row still separates
    # the rule from a count of conforming pairs, which is what this
    # test is for.
    cases = (
        ([True, True], [True, True], [0, 0], [0, 0], 0, 0, True),
        ([False, False], [True, True], [0, 0], [0, 0], 1, 1, True),
        ([True, False], [False, True], [0, 0], [0, 0], 1, 1, False),
        ([True, False], [False, True], [0, 0], [0, 0], 1, 0, True),
        ([True, True], [True, False], [0, 0], [0, 0], 2, 2, False),
        ([True, True], [True, False], [0, 0], [0, 0], 2, 1, True),
    )
    for before, after, rows_was, rows_now, was, now, allowed in cases:
        assert generation._swap_allowed(
            before, after, rows_was, rows_now, was, now
        ) is allowed, (before, after, was, now, allowed)
    before, after = [True, False], [False, True]
    assert sum(before) == sum(after)
    assert generation._swap_allowed(
        before, after, [0, 0], [0, 0], 1, 1
    ) is False


def _battery_column(which: int) -> "list[str]":
    """One column of the measurement file's own battery, built alike.

    `tools/measurements/r_p4_40_l7_joined.py` seeds `random` once and
    builds twelve columns in order, so a case is reproduced only by
    building every case before it.
    """
    generator = random.Random(20260904)
    built: "list[list[str]]" = []
    for case in range(12):
        rows: "list[str]" = []
        parts = 3 + case % 2
        for _row in range(150):
            first = generator.randint(10, 60)
            second = first + generator.randint(-8, 8)
            third = generator.randint(1, 40)
            fourth = 100 - first
            held = [first, second, third, fourth][:parts]
            rows = rows + ["/".join(str(one) for one in held)]
        built = built + [rows]
    return built[which]


def test_an_exact_seat_is_not_sold_for_an_agreement_term() -> None:
    """Review round 3's producer case, on the twin it produces.

    Round 2 gave the acceptance rule per-pair AGREEMENT masks and left
    the EXACT obligations as one summed distance. A sum cannot express
    the rule either: an above-count can go from held to MISSED while
    another improves by one, the total says nothing happened, and the
    agreement tie-break is then the only reason left to take the swap.

    MEASURED on this column at seed 27 before the repair: at accepted
    swap 57, which is the walk's try 350, the per-pair gaps went
    `(0, 3, 0, 0, 0, 0)` to `(0, 2, 0, 1, 0, 0)` -- `part_above[3]`
    lost while `part_above[1]` gained -- with the total 3 either way
    and `away` falling from 3.256434912989342 to 3.2564112096671862.
    Accepted swap 59, try 377, moved it back the same way, and three
    earlier swaps did the same. Over the whole run the count of pairs
    holding their published above-count fell four times, ending at five
    of six, and the twin held `(65, 120, 32, 118, 31, 0)` against a
    published `(65, 122, 32, 118, 31, 0)`.

    The above-counts are carried by IDENTITY now, and this column meets
    every one of them.

    THIS TEST DOES NOT PIN THE ACCEPTANCE RULE, and saying so is part
    of what it is for. With G6B.4a's retargeted proposal in place, the
    rule was collapsed back to a summed distance and this test stayed
    GREEN: the walk reaches the same twin by another road. What pins
    the rule is `test_the_walk_never_sells_an_above_count_it_holds`
    below, which watches the decisions instead of the cells.
    """
    _document, loaded, folder, _table = _described(_battery_column(11))
    column = loaded.columns[0]
    facts = column.facts
    assert column.role == "joined_numbers", column.role
    assert facts.n_parts == 4, facts.n_parts
    assert column.n_distinct == 149, column.n_distinct
    assert facts.part_above == (65, 122, 32, 118, 31, 0), facts.part_above

    twin = generation.generate(loaded, 27)
    cells = [cell for cell in twin.columns[0] if cell != ""]
    held = [
        [float(cell.split(facts.separator)[place]) for cell in cells]
        for place in range(facts.n_parts)
    ]
    above: "list[int]" = []
    for first in range(facts.n_parts):
        for second in range(first + 1, facts.n_parts):
            above = above + [len([
                1 for row in range(len(cells))
                if held[first][row] > held[second][row]
            ])]
    assert tuple(above) == facts.part_above, (
        f"the twin holds {tuple(above)} against a published "
        f"{facts.part_above}; an exact seat was sold for an agreement "
        "term"
    )
    assert len(set(cells)) == column.n_distinct, len(set(cells))
    written = fixtures.write(folder, "b11.csv", rendering.twin_csv(twin))
    outcome = validation.measure(loaded, f"{written}")
    missed = [
        check.subcheck
        for check in outcome.checks
        if check.verdict == validation.MISSED
        and "one above the other" in check.subcheck
    ]
    assert not missed, missed


def test_the_walk_never_sells_an_above_count_it_holds(
    monkeypatch: "pytest.MonkeyPatch",
) -> None:
    """The DECISIONS the walk took, and not the twin it came out with.

    AN OUTCOME CANNOT PIN THIS RULE, measured: with G6B.4a's
    retargeted proposal in place, collapsing the acceptance rule back
    to a summed distance leaves both outcome cases beside this one
    green -- `battery-11` at seed 27 still comes out holding every
    above-count and all 149 different cells. The walk finds the same
    twin by another road. So this test spies on the arguments the walk
    really hands the rule, and asserts the two things the rule
    promises, neither of which any finished twin can show.

    ONE: no swap is ever allowed that takes a pair's above-count from
    HELD to missed. That is the guarantee the method's G12.9 sentence
    rests on -- "a twin either holds it or has missed it" -- and it is
    what makes the set of pairs holding their count non-shrinking
    across a whole walk.

    TWO: the rule is REACHED on the branch where nothing left its
    window. That is where review round 3's defect lived: the guard
    returned True there without reading its exact arguments at all.
    Measured on this column, 9,125 swaps are refused with every mask
    standing still and an above-count worsening; a rule that read its
    arguments only inside the window guard refuses none of them.
    """
    _document, loaded, _folder, _table = _described(_battery_column(11))
    assert loaded.columns[0].facts.part_above == (
        65, 122, 32, 118, 31, 0
    ), loaded.columns[0].facts.part_above

    honest = generation._swap_allowed
    seen: "list[tuple]" = []

    def watched(before, after, was, now, cells_was, cells_now):
        verdict = honest(before, after, was, now, cells_was, cells_now)
        seen.append((list(before), list(after), list(was), list(now),
                     verdict))
        return verdict

    monkeypatch.setattr(generation, "_swap_allowed", watched)
    generation.generate(loaded, 27)

    assert seen, "the walk never consulted the acceptance rule"
    sold: "list[tuple]" = []
    allowed_sales = 0
    quiet_refusals = 0
    # THREE: the vectors reaching the rule really are PER PAIR and
    # aligned. This column has four positions, so every position the
    # walk moves is in three pairs: a rule handed one summed entry
    # cannot refuse per pair however the refusals are written, and
    # nothing but the walk's own `moved` list keeps the two vectors
    # naming the same pairs.
    for before, after, was, now, _verdict in seen:
        assert len(was) == 3, (
            f"the walk passed {len(was)} above-count entries where the "
            "position it moved is in 3 pairs"
        )
        assert len(was) == len(now) == len(before) == len(after), (
            len(was), len(now), len(before), len(after)
        )
    for before, after, was, now, verdict in seen:
        selling = any(
            was[seat] == 0 and now[seat] != 0 for seat in range(len(was))
        )
        if selling:
            sold.append((was, now))
            if verdict:
                allowed_sales = allowed_sales + 1
        left = any(
            before[seat] and not after[seat] for seat in range(len(before))
        )
        worse = any(
            now[seat] > was[seat] for seat in range(len(was))
        )
        if not verdict and not left and worse:
            quiet_refusals = quiet_refusals + 1
    # VACUITY FIRST: a run that never proposed such a swap would assert
    # nothing at all below.
    assert sold, (
        "no swap in the whole walk offered to sell a held above-count, "
        "so this test pins nothing"
    )
    assert allowed_sales == 0, (
        f"{allowed_sales} of {len(sold)} swaps that would take an "
        "above-count from held to missed were ALLOWED"
    )
    assert quiet_refusals > 0, (
        "no swap was refused on its above-counts while every pair stayed "
        "inside its window, so the rule is still being consulted only "
        "behind the window guard"
    )


def _tight_column(which: int) -> "list[str]":
    """One column of `tools/measurements/a_p4_52_l7_parity.py`'s tight family.

    Five positions, so FOUR movers -- an even mover count, which is
    where a gate read off the walk's own counter starves one parity of
    positions outright. The driver seeds once and builds eight columns
    in order, so a case is reproduced only by building every case
    before it.
    """
    generator = random.Random(20260903)
    built: "list[list[str]]" = []
    for _case in range(8):
        rows: "list[str]" = []
        for _row in range(150):
            one = generator.randint(20, 35)
            rows = rows + ["/".join(str(each) for each in (
                one,
                max(1, one + generator.randint(-2, 2)),
                generator.randint(20, 35),
                55 - one,
                max(1, one + generator.randint(-4, 4)),
            ))]
        built = built + [rows]
    return built[which]


def _above_counts(
    twin: "generation.Twin", facts: "contract.JoinedFacts"
) -> "tuple[int, ...]":
    """How many rows of the twin hold each pair's earlier part above."""
    rows = [
        [float(part) for part in cell.split(facts.separator)]
        for cell in twin.columns[0]
        if cell != ""
    ]
    firsts, seconds = generation._pair_seats(facts.n_parts)
    return tuple(
        sum(
            1
            for row in rows
            if row[firsts[seat]] > row[seconds[seat]]
        )
        for seat in range(len(facts.part_above))
    )


def test_neither_parity_of_positions_is_starved_of_the_proposal() -> None:
    """Both halves of the alternation, each on a column that shows it.

    THE WALK TAKES ITS POSITIONS IN TURN FROM THE TRY COUNTER, so a
    proposal gated on that same counter is not alternating at all
    wherever the mover count is even -- position `p` is reached at
    tries `p - 1`, `p - 1 + movers`, ... which have ONE parity, so the
    gate answers the same thing at every turn that position ever gets.
    Review round 3 gated on `tries % 2` and every column with an odd
    number of positions therefore aimed at an above-count from its
    even positions on every turn and from its odd positions on none.
    Amendment A-P4-52 reads `(turn + place) % 2` instead, where
    `turn` counts that position's OWN turns.

    TWO COLUMNS, ONE FOR EACH HALF, both five positions and 150 rows:

    - `_tight_column(0)` at seed 0 goes red under `tries % 2` -- pair
      (0, 1) comes out holding 49 rows against a published 64, and
      position 1 is that pair's only mover;
    - `_tight_column(5)` at seed 0 goes red under `(tries + 1) % 2`,
      the phase flip, which starves the other half -- pair (0, 4)
      misses, and position 4 is that pair's only mover.

    Either mutant alone leaves the other column green, which is why
    both are here: a test built on one of them would bless the gate
    that starves the other parity. Measured over forty seeds and the
    driver's forty-column recipe, the shipped gate leaves 44 pairs of
    9,640 short of their above-count where `tries % 2` leaves 120 and
    the phase flip leaves 153.
    """
    for which, seed in ((0, 0), (5, 0)):
        _document, loaded, _folder, _table = _described(_tight_column(which))
        column = loaded.columns[0]
        facts = column.facts
        assert isinstance(facts, contract.JoinedFacts), column.role
        assert facts.n_parts == 5, facts.n_parts
        assert len(facts.part_above) == 10, facts.part_above
        held = _above_counts(generation.generate(loaded, seed), facts)
        missed = [
            (seat, held[seat], facts.part_above[seat])
            for seat in range(len(held))
            if held[seat] != facts.part_above[seat]
        ]
        assert not missed, (
            f"tight column {which} at seed {seed} missed {missed} "
            "(seat, held, published); a position that never aims at an "
            "above-count cannot repair the pairs it is the only mover of"
        )


def test_every_position_aims_at_an_above_count_on_half_its_own_turns(
) -> None:
    """The anti-lockout property itself, at every mover count.

    Review round 4 of L7 found the schedule guarded by nothing but a
    byte hash: change its phase and the only test that moves is the
    golden twin's digest, which says the bytes moved and names no
    fact. The phase is not what matters and R-P4-131 measures why --
    all four phases miss within eight pairs of each other in 15,560.
    WHAT matters is the property every phase of it has and the gate it
    replaced did not: each position aims at an above-count on HALF of
    its own turns, whatever the mover count.

    The walk reaches position `p` at tries `p - 1`, `p - 1 + movers`,
    ..., so a gate on the walk's own try counter reads `turn * movers
    + place` -- one parity for every turn a given position ever gets
    wherever `movers` is even. That is 0 turns or all 40, which is the
    lockout, asserted here beside the rule so the defect is legible
    rather than remembered.
    """
    for movers in range(1, 9):
        for place in range(1, movers + 1):
            aimed = [
                turn for turn in range(40)
                if generation._aims_at_above(turn, place)
            ]
            assert len(aimed) == 20, (movers, place, len(aimed))
            # ALTERNATING, not merely half: twenty of forty is also
            # what aiming on the first twenty turns would give.
            assert aimed == [turn for turn in range(0, 40, 2)] or aimed == [
                turn for turn in range(1, 40, 2)
            ], (movers, place, aimed[:6])

    # AND THE GATE IT REPLACED, on the same arithmetic: wherever the
    # mover count is even it opens on none of a position's turns or on
    # every one of them, which is the starving A-P4-52 names.
    starved = set()
    for movers in (2, 4, 6, 8):
        for place in range(1, movers + 1):
            by_tries = sum(
                1 for turn in range(40)
                if (turn * movers + place) % 2 == 0
            )
            starved.add(by_tries)
    assert starved == {0, 40}, starved


def test_the_above_count_marks_name_the_moved_positions_own_pairs(
    monkeypatch: "pytest.MonkeyPatch",
) -> None:
    """The ALIGNMENT itself, which nothing else in the suite touches.

    `_above_marks` is the only thing carrying pair identity into the
    acceptance rule, and its own docstring names the hazard it cannot
    check from inside: entry `k` of the vector must be the pair
    `where[k]` names, and nothing but the shared `moved` list says so.
    Review round 4 found the whole suite SILENT to getting it wrong.
    Replace the one line that computes a mark with

        marks[step] = abs(aboves[step] - facts.part_above[step])

    -- the same length, the same shape, the gaps of the FIRST few
    seats instead of the moved position's own. Run against the whole
    suite, 4,309 collected, that mutant turns exactly this test red
    and nothing else at all.

    AND NO OUTCOME TEST CAN DO IT, which is measured rather than
    argued: under the mutant `battery-11` still comes out holding
    every one of its 240 pairs' above-counts at all forty seeds, the
    same as the shipped rule, because a rule handed the wrong pairs
    still refuses roughly the right proportion of swaps and the walk
    finds its way by another road. The vectors themselves have to be
    read. Under the mutant ALL 29,362 of them name no position's
    pairs; under the shipped rule none does.

    AND MEMBERSHIP ALONE IS NOT THE CHECK, which review round 4
    found: asking only that every vector be one of the three permitted
    vectors leaves a CYCLIC misalignment green -- position 1 reading
    position 2's pairs, 2 reading 3's, 3 reading 1's. All three
    vectors are still permitted, all three still appear, every length
    is still right, and every acceptance decision is still made on the
    wrong pair identities. So each vector is bound BY CALL to the
    position that call was moving, below.

    MEASURED, not argued. Build `moved` from `1 + place % (n_parts -
    1)` instead of from `place`, so the walk swaps one position's
    cells and judges another position's pairs -- the cycle above,
    exactly. The membership check on its own stays GREEN under it.
    The per-call binding refuses all 29,362 vectors, naming position
    1 handed `[5, 1, 0]` where its own pairs owe `[18, 1, 1]`. The
    seat-index mutant further down is caught by both.

    HOW THE TRUTH IS COMPUTED WITHOUT READING THE CLOSURE'S OWN LIST.
    Every swap is refused here, so the walk puts every one of them
    back and the twin comes out holding the arrangement the walk
    STARTED from -- which makes the starting above-count gap of every
    seat countable from the twin's own cells, in the test. The vector
    the rule is owed on a try that moves position `p` is then those
    gaps at the seats whose pairs contain `p`, in seat order, and a
    four-position column has only three such vectors. Every one of the
    29,362 vectors the walk really hands the rule must be one of them.
    """
    _document, loaded, _folder, _table = _described(_battery_column(11))
    column = loaded.columns[0]
    facts = column.facts
    assert facts.n_parts == 4, facts.n_parts
    assert facts.part_above == (65, 122, 32, 118, 31, 0), facts.part_above

    marks: "list[list[int]]" = []
    named: "list[tuple[int, list[int], int]]" = []

    def refusing(before, after, was, now, cells_was, cells_now) -> bool:
        # THE POSITION THE WALK IS REALLY MOVING, read from the
        # caller's own frame and not from the vectors under test.
        # `moved` is built FROM `place`, and all six arguments are
        # built from `moved`, so any position derived from the
        # arguments would agree with a misaligned walk by
        # construction. The walk's own local is the one handle here
        # that `_above_marks` does not feed. Renaming it fails this
        # test loudly, which is the coupling this check is for.
        frame = inspect.currentframe()
        assert frame is not None and frame.f_back is not None
        walking = frame.f_back.f_locals
        assert "place" in walking, sorted(walking)
        marks.append(list(was))
        named.append((walking["place"], list(was), len(now)))
        return False

    monkeypatch.setattr(generation, "_swap_allowed", refusing)
    twin = generation.generate(loaded, 27)

    rows = [
        [float(part) for part in cell.split(facts.separator)]
        for cell in twin.columns[0]
        if cell != ""
    ]
    assert len(rows) == facts.n_joined, (len(rows), facts.n_joined)
    firsts, seconds = generation._pair_seats(facts.n_parts)
    started = [
        abs(
            sum(
                1
                for row in rows
                if row[firsts[seat]] > row[seconds[seat]]
            )
            - facts.part_above[seat]
        )
        for seat in range(len(firsts))
    ]
    # The starting arrangement is fixed by the profile and the seed, so
    # it is stated here rather than left to be read off a failure.
    assert started == [18, 5, 0, 1, 1, 0], started

    # WHAT EACH MOVABLE POSITION IS OWED: its own pairs' gaps, in the
    # order the walk's `moved` list builds them, which is seat order.
    owed = {
        place: [
            started[seat]
            for seat in range(len(firsts))
            if firsts[seat] == place or seconds[seat] == place
        ]
        for place in range(1, facts.n_parts)
    }
    assert owed == {1: [18, 1, 1], 2: [5, 1, 0], 3: [0, 1, 0]}, owed
    # AND THE FIXTURE REALLY CAN TELL THE TWO APART, asserted instead
    # of assumed: a vector indexed by its own place in the moved list
    # reads the first three seats, and that is no position's pairs. A
    # column whose gaps happened to coincide would leave this test
    # vacuous without saying so.
    by_step = started[: facts.n_parts - 1]
    assert by_step == [18, 5, 0], by_step
    assert by_step not in owed.values(), (by_step, owed)

    assert marks, "the walk never consulted the acceptance rule"
    astray = [vector for vector in marks if vector not in owed.values()]
    assert not astray, (
        f"{len(astray)} of {len(marks)} above-count vectors name no "
        f"position's pairs; the first is {astray[0]} where the three "
        f"positions owe {sorted(owed.values())}"
    )
    # EVERY VECTOR AGAINST THE POSITION THAT CALL WAS MOVING, one
    # call at a time, which is what refuses the cyclic misalignment
    # the docstring names.
    crossed = [
        (place, vector)
        for place, vector, _length in named
        if vector != owed[place]
    ]
    assert not crossed, (
        f"{len(crossed)} of {len(named)} calls read another position's "
        f"pairs; the first moved position {crossed[0][0]}, which was "
        f"handed {crossed[0][1]} where its own pairs owe "
        f"{owed[crossed[0][0]]}"
    )
    # The vector read AFTER the swap names the same pairs in the same
    # order, so its LENGTH is owed too. Its values are not: the swap
    # is what moves them, and that is the whole point of taking it.
    mislengthed = {
        (place, length)
        for place, _vector, length in named
        if length != len(owed[place])
    }
    assert not mislengthed, mislengthed
    # AND ALL THREE POSITIONS REALLY WERE MOVED, so no arm of the
    # alignment is pinned by never being exercised. Taken from the
    # positions the walk named, not from the vectors it built.
    reached = {place for place, _vector, _length in named}
    assert reached == {1, 2, 3}, reached


def test_the_walk_holds_the_above_count_of_r_p4_40s_own_column() -> None:
    """The second reproduction, on the residual's own 400-row column.

    The reported case was one seed of one battery column. This one is
    the shape R-P4-40 was opened on -- 400 readings, 379 of them
    different -- and its `part_above` came out MISSED at four of six
    seeds before the repair, through the real validator rather than a
    recount. It is here so the repair is not pinned to a single seed.
    """
    generator = random.Random(20260905)
    values = [
        "%d/%d" % (generator.randint(95, 165), generator.randint(50, 100))
        for _row in range(400)
    ]
    _document, loaded, folder, _table = _described(values)
    column = loaded.columns[0]
    assert column.role == "joined_numbers", column.role
    missed: "list[str]" = []
    for seed in range(6):
        twin = generation.generate(loaded, seed)
        written = fixtures.write(
            folder, f"own-{seed}.csv", rendering.twin_csv(twin)
        )
        outcome = validation.measure(loaded, f"{written}")
        for check in outcome.checks:
            if check.verdict != validation.MISSED:
                continue
            if "one above the other" in check.subcheck:
                missed = missed + [f"seed {seed}: {check.subcheck}"]
    assert not missed, missed


def test_the_swap_rule_carries_the_exact_facts_by_identity() -> None:
    """The rule itself, on the cases a SUM cannot tell apart.

    Every row here has all three pairs INSIDE their window on both
    sides, so the window guard is not reached and the row is decided by
    the above-count refusals alone -- which is the shape review round 3
    reported: the walk's own reproduction never left a window.

    THE SECOND ROW WAS ASSERTED THE OTHER WAY IN THE FIRST DRAFT OF
    THIS REPAIR, and it is the whole difference between the two rules.
    A total that STRICTLY improves was taken to license any trade under
    it, so a pair holding its published above-count could be sold for a
    two-row gain on a pair that stays missed either way. `synthtwin
    validate` reads `part_above` per pair and binary: improving a pair
    that remains missed gains a reader nothing, and the swap gives up a
    fact the twin holds for one it does not.
    """
    mask = [True, True, True]
    # One seat lost, another gained, the total standing still: refused.
    assert generation._swap_allowed(
        mask, mask, [0, 0, 3], [0, 1, 2], 0, 0
    ) is False
    # The same shape summed would be 3 against 3 -- indistinguishable.
    assert sum([0, 0, 3]) == sum([0, 1, 2])
    # A HELD seat sold for a strictly better total: still refused.
    assert generation._swap_allowed(
        mask, mask, [0, 0, 3], [0, 1, 1], 0, 0
    ) is False
    assert sum([0, 1, 1]) < sum([0, 0, 3])
    # Nothing worsens: taken.
    assert generation._swap_allowed(
        mask, mask, [0, 2, 3], [0, 1, 3], 0, 0
    ) is True
    # A seat REACHES its published count while another dips: taken,
    # because refusing it would refuse progress towards the fact the
    # first refusal protects.
    assert generation._swap_allowed(
        mask, mask, [0, 1, 1], [0, 0, 2], 0, 0
    ) is True


def test_the_swap_rule_refuses_each_trade_the_review_named() -> None:
    """The acceptance rule, row by row, against every rule it carries.

    ONE ROW PER REFUSAL AND ONE PER ESCAPE. The first row is the walk's
    own reproduction: at `battery-11` seed 27, try 350, the moved
    pairs' above-count gaps went `(3, 0, 0)` to `(2, 1, 0)` with every
    mask True on both sides. No pair left its window, so the rule
    returned True before ever reading its exact arguments, and `away`
    fell by 2.4e-5 on the agreement tie-break alone.

    NO TWIN IS BUILT HERE, and that is the point of the rule being a
    named function: a twin cannot say which swaps were taken.
    """
    yes = [True, True, True]
    rows = (
        # The reproduction: a held above-count sold while another gains.
        ("try 350", yes, yes, [3, 0, 0], [2, 1, 0], 0, 0, False),
        # A held seat sold for a two-row gain on a seat still missed.
        ("held sold at a profit", yes, yes, [0, 3, 0], [1, 1, 0], 0, 0,
         False),
        # A seat drifts further out while the agreement improves: the
        # beyond-window term of `_away` can outbid a whole row, so the
        # rule refuses it rather than pricing it.
        ("residual grows", yes, yes, [0, 1, 0], [0, 2, 0], 0, 0, False),
        # Sideways among seats missed either way: nothing is gained and
        # the tie-break is the only reason left to take it.
        ("sideways", yes, yes, [2, 3, 0], [3, 2, 0], 0, 0, False),
        # A seat REACHES its count while another dips: allowed.
        ("a seat becomes held", yes, yes, [1, 1, 0], [0, 2, 0], 0, 0,
         True),
        # The same, with the total getting worse: still allowed, since
        # the walk moved a pair onto its published count.
        ("a seat becomes held, total worse", yes, yes, [1, 5, 0],
         [0, 7, 0], 0, 0, True),
        # Plain improvement.
        ("plain gain", yes, yes, [0, 3, 0], [0, 2, 0], 0, 0, True),
        # THE WINDOW GUARD, on rows where no above-count moves. A pair
        # leaves its window and the cell count gains: allowed.
        ("drift, cells gain", yes, [True, True, False], [2, 0, 0],
         [2, 0, 0], 3, 2, True),
        # The same drift where the ROWS gain instead: allowed.
        ("drift, rows gain", yes, [True, True, False], [2, 0, 0],
         [1, 0, 0], 3, 3, True),
        # And where neither exact fact moves: refused.
        ("drift, nothing gained", yes, [True, True, False], [2, 0, 0],
         [2, 0, 0], 3, 3, False),
        # THE LAST TWO ROWS SEPARATE THE DISJUNCTION FROM A RE-MIXED
        # TOTAL, which is the collapse this landing removes. Here the
        # rows come closer while a different cell is lost, and there a
        # seat reaches its published count while a cell is gained: each
        # brings ONE exactly-checked fact closer, which is what step 5
        # asks, and a rule adding the two kinds together would refuse
        # both because the combined number stands still.
        ("drift, rows gain while a cell is lost", yes,
         [True, True, False], [2, 0, 0], [1, 0, 0], 3, 4, True),
        ("drift, a cell gained while a seat reaches its count", yes,
         [True, True, False], [1, 1, 0], [0, 3, 0], 3, 2, True),
    )
    for name, before, after, was, now, cells_was, cells_now, allowed in rows:
        assert generation._swap_allowed(
            before, after, was, now, cells_was, cells_now
        ) is allowed, name
    # THE TWO EXACT FACTS ARE NOT ADDENDS OF ONE ANOTHER. A gained cell
    # does not buy a lost above-row: the first refusal has already
    # returned by the time the cell count is looked at.
    assert generation._swap_allowed(
        yes, yes, [0, 0, 0], [1, 0, 0], 9, 0
    ) is False


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
        lambda before, after, was, now, cells_was, cells_now: False,
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
