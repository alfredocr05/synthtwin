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


def test_an_unscored_pair_is_never_dressed_as_an_approximation() -> None:
    """Goes red if `_agreement_approximations` scores every pair again.

    The approximated pairs are exactly those the walk moves: the ones
    the LAST position is part of. For three positions that is two of
    the three pairs, and the third is not approximated at all.
    """
    _document, loaded, _folder, _table = _described(_three_positions())
    twin = generation.generate(loaded, 9)
    scored = sorted(
        record.fact
        for record in twin.approximations
        if "part_agreements" in record.fact
    )
    assert scored == ["part_agreements[1]", "part_agreements[2]"], (
        "pair 0 is between the first two positions, which the walk "
        f"never moves, and it was approximated anyway: {scored}"
    )


def test_an_unscored_pair_that_misses_is_named_as_a_deviation() -> None:
    """A fact nothing reports is one a reader cannot know was missed.

    Removing it from the approximations must not remove it from the
    report. It becomes what it is -- a published fact the twin did not
    meet -- and the sentence beside it says no closeness was promised,
    so a reader is not left to infer a bound from silence.

    Goes red if `_agreement_notes` is dropped from the deviation chain.
    """
    _document, loaded, _folder, _table = _described(_three_positions())
    twin = generation.generate(loaded, 9)
    named = [
        note for note in twin.deviations if note.fact == "part_agreements[0]"
    ]
    assert len(named) == 1, (
        "the pair the walk never moves came out somewhere other than "
        "published and no line of the report says so"
    )
    assert "not aimed at" in named[0].note


def test_a_two_position_column_has_no_unscored_pair() -> None:
    """The common case is untouched, and that is worth pinning.

    Two positions make one pair and the walk moves one of them, so
    every pair of an ordinary joined column is scored. A change that
    made the ordinary column start reporting deviations here would be
    a regression this catches.
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
    # appear is the UNSCORED-pair note, which would say the walk never
    # aimed at the one pair it spends its whole search on.
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


def test_the_scored_rule_has_one_definition() -> None:
    """Two modules asked which pairs are scored and only one was fixed.

    The generator decides which pairs it approximates; the validator
    decides which it holds to G12.9's window. Written separately, only
    one was corrected in round 1, and the twin's own report then called
    a pair unscored while the quality report handed the same pair the
    window of the section that excludes it.
    """
    assert contract.scored_pairs(2) == (0,)
    assert contract.scored_pairs(3) == (1, 2)
    assert contract.scored_pairs(4) == (2, 4, 5)


def test_both_pages_say_the_same_thing_about_the_same_twin() -> None:
    """The pair the walk never moves is named the same way by both.

    Goes red if either side stops reading `contract.scored_pairs`.
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
    assert approximated == {"part_agreements[1]", "part_agreements[2]"}

    # A SCORED PAIR CARRIES THE ENVELOPE WHERE IT IS WINDOWED, and a
    # pair that hits its published value exactly is HELD and carries
    # none -- the citation travels with the lesser verdict, not with
    # every scored pair. What must never happen is the reverse: an
    # UNSCORED pair carrying G12.9, which is the section that excludes
    # it.
    windowed = {
        check.fact
        for check in outcome.checks
        if "part_agreements" in check.fact
        and check.citation == validation.ENVELOPE_JOINED_AGREEMENT
    }
    assert windowed, "no pair was windowed at all, so this pins nothing"
    assert windowed <= {
        "joined.part_agreements[1]",
        "joined.part_agreements[2]",
    }, (
        "the quality report cites the joined-agreement envelope for a "
        f"pair the pairing walk never moves: {windowed}"
    )

    unscored = [
        check
        for check in outcome.checks
        if check.fact == "joined.part_agreements[0]"
    ]
    assert len(unscored) == 1
    # CHECKED EXACTLY AND NOT EXCUSED. A round of this review made it
    # an AUTHORIZED-DEVIATION and that was withdrawn (item
    # P4-G3-R3-F2): G12.9 withholds the WINDOW, not the obligation, and
    # excusing the miss let a file that is not a twin pass every
    # verdict-bearing check. The twin does miss it, that is residual
    # R-P4-51, and an open residual belongs in the report.
    assert unscored[0].verdict in (validation.HELD, validation.MISSED)
    assert not unscored[0].citation, (
        "no window is promised for this pair, so no envelope may be "
        f"cited beside it: {unscored[0].citation!r}"
    )


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


def test_the_walk_starts_from_the_pairs_it_can_actually_move(
    monkeypatch: "pytest.MonkeyPatch",
) -> None:
    """An unaimed-at fact must not steer a choice it cannot affect (F6).

    The starting arrangement is chosen from the average published
    agreement, and only the LAST position moves -- so a pair between
    two earlier positions cannot be helped by any answer, and letting
    its target into the average lets a fact nothing can reach decide
    the start for the facts that can.

    COMPUTING TWO AVERAGES IN THE TEST PINNED NOTHING, which is what
    the first version did (review item P4-G3-R3-F5): restoring the old
    loop over every published agreement left it green, because it never
    generated a column at all. So this REPLACES the rule the generator
    reads and watches the twin's own cells move. If the generator stops
    consulting `contract.scored_pairs` when it picks a start, the two
    twins come out identical and this goes red.

    Twenty random three-position columns did NOT separate the two rules
    by their verdicts, which is why this pins the CALL rather than
    sampling for an improvement I could not measure.
    """
    # A DESCRIPTION WHOSE TARGETS STRADDLE THE BRANCH, because no
    # ordinary column does. Sixty three-position columns built to lean
    # the right way were measured and NONE of them put the two
    # averaging rules on opposite sides of the walk's own threshold --
    # so the published agreements are set here directly, which is what
    # the generator consumes and is the whole of what this test is
    # about. The rest of the description is a real one.
    document, _loaded, folder, _table = _described(_three_position_column())
    forged = copy.deepcopy(document)
    forged["columns"][0]["part_agreements"] = [-0.68, 0.4, 0.4]
    loaded = contract.load_profile(
        f"{fixtures.write_profile(folder, 'forged.json', forged)}"
    )
    assert loaded.columns[0].facts.part_agreements == (-0.68, 0.4, 0.4)

    honest = generation.generate(loaded, 21)

    # Every seat scored -- the rule the generator used to average over.
    def every_seat(n_parts: int) -> "tuple[int, ...]":
        seats: "list[int]" = []
        place = 0
        for first in range(n_parts):
            for second in range(first + 1, n_parts):
                seats = seats + [place]
                place = place + 1
        return tuple(seats)

    monkeypatch.setattr(contract, "scored_pairs", every_seat)
    widened = generation.generate(loaded, 21)

    assert honest.columns[0] != widened.columns[0], (
        "replacing the rule that says which pairs the walk aims at "
        "left the twin's cells unchanged, so the generator is not "
        "reading it where it chooses a starting arrangement"
    )


def test_the_two_averaging_rules_fall_on_opposite_sides() -> None:
    """The arithmetic the test above depends on, stated once.

    With an early pair at -0.68 and both scored pairs at +0.4,
    averaging the pairs the walk moves gives 0.400 and starts
    rank-for-rank, while averaging all three gives 0.040 and starts
    from a shuffle. If this ever stops holding, the test above is
    watching two runs that were never going to differ.
    """
    published = (-0.68, 0.4, 0.4)
    seats = contract.scored_pairs(3)
    over_scored = sum(published[seat] for seat in seats) / len(seats)
    over_every = sum(published) / len(published)
    assert over_scored >= 0.4 > over_every


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
    # The check itself, over both spellings of the same number.
    for measured in (0.0, -0.0):
        check = validation._unscored_agreement(
            "bp",
            "joined.part_agreements[0]",
            "together.how strongly they move, pair 1",
            0.0,
            measured,
        )
        assert check.verdict == validation.HELD, (
            f"an agreement of {measured!r} against a published 0.0 came "
            f"back {check.verdict}, and the two numbers are equal"
        )


def test_the_method_and_the_code_choose_the_start_the_same_way() -> None:
    """THE REPAIR MUST NOT OUTGROW THE PUBLIC METHOD (F4).

    G6B.4 step 2 said to average EVERY published agreement while the
    code averaged only the scored ones, so two implementations -- one
    written from the specification, one from this repository -- could
    write different twin bytes for the same description and seed. The
    method is amended; this holds the two together by reading the
    method's own words.
    """
    method = (
        pathlib.Path(__file__).resolve().parents[1]
        / "docs"
        / "spec"
        / "generation-method-v1.md"
    ).read_text(encoding="utf-8")
    step = method[method.index("**2. Choose the start.**") :][:2400]
    assert "SCORED" in step, (
        "G6B.4 step 2 no longer says the mean is taken over the scored "
        "entries, so an implementer working from the method would "
        "average every entry and choose a different starting "
        "arrangement from this code"
    )
    assert "-0.68, 0.4, 0.4" in step, (
        "the worked example that separates the two rules has gone from "
        "the method, so a reader cannot check which one is meant"
    )
