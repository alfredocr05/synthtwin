"""Role detection and the statistics of each role (plan P1-D4).

Type misrouting is the failure this file guards: a column sent down the
wrong path corrupts the twin quietly, with nothing crashing and every
other test still green. Each rule therefore has a case that must take
it AND a neighbouring case that must not.
"""

import pytest

import fixtures
from synthtwin import parsing, taxonomy

# THE SMALLEST GROUP THIS FILE DESCRIBES COLUMNS AT, DECLARED BECAUSE
# IT IS NO LONGER THE DEFAULT. The owner lowered the shipped
# `small_cell_floor` to one (plan amendment A-P4-37), and at a floor of
# one nothing is ever held back: no level is pooled, no spelling is
# withheld, no sentinel candidate goes unpublished (contract invariant
# C5-S13). Several rules of this file are about exactly that holding
# back -- a constant below the floor, labels below the floor, the floor
# under the binary role, a sentinel too rare to name -- and they cannot
# be exercised at all at a floor of one. Eleven is the floor every case
# below was written against, so it is asked for once here rather than
# left to a default that has moved beneath them. The floor of one has a
# file of its own (`tests/test_p3v5f1_floor_one.py`); this one is about
# the roles and their statistics.
SETTINGS = taxonomy.Settings(small_cell_floor=11)


def describe(
    values: list[str],
    n_rows: "int | None" = None,
    settings: taxonomy.Settings = SETTINGS,
    forced: bool = False,
) -> taxonomy.ColumnProfile:
    """Profile a single column of ``values``."""
    return taxonomy.profile_column(
        "column", 1, values, n_rows if n_rows is not None else len(values),
        settings, forced,
    )


# -- the roles, one by one ------------------------------------------


def test_a_column_with_nothing_in_it_is_empty() -> None:
    described = describe(["", "NA", "  ", "null"] * 10)
    assert described.role == taxonomy.ROLE_EMPTY
    assert described.n_present == 0
    assert described.n_missing == 40


def test_one_repeated_value_is_a_constant() -> None:
    described = describe(["same"] * 30)
    assert described.role == taxonomy.ROLE_CONSTANT
    # The published label is the folded identity; `variants` says how
    # the 30 rows that share it wrote it, which here is one way (owner
    # decisions 9 and 11).
    assert described.details["levels"] == [
        {
            "label": "same",
            "count": 30,
            "variants": {"same": 30},
            "variants_withheld": {},
            # Letters alone are one kind, so `same` has no written form
            # and none of its rows wrote it in one (7.4.8, A-P4-47).
            "shape_form_cells": 0,
        }
    ]


def test_a_constant_below_the_floor_is_not_published() -> None:
    described = describe(["rare"] * 4 + [""] * 40)
    assert described.role == taxonomy.ROLE_CONSTANT
    assert described.details["levels"] == []
    assert described.details["suppressed_rows"] == 4
    assert described.publication_notes


def test_unique_words_are_free_text_until_someone_declares_them() -> None:
    """Corrected from `test_unique_words_are_identifiers_...`.

    The old test required 50 unique code words to be INFERRED as record
    numbers. That inference is withdrawn (review item P1-R6-F8): `1mg`
    and `code1` are the same shape of string, so a rule that reads one
    as a record number reads the other as one too, and a dose column
    then loses its distribution for good. Both halves of the old test
    are kept -- the values are still withheld, and the identifier role
    is still exercised -- but the role now comes from the person who
    owns the table rather than from the values.
    """
    values = fixtures.prose(50)
    described = describe(values)
    assert described.role == taxonomy.ROLE_TEXT
    assert described.n_distinct == 50
    assert "levels" not in described.details
    body = f"{described.details}"
    assert "code7" not in body, "no free-text value may appear anywhere"

    declared = describe(values, forced=True)
    assert declared.role == taxonomy.ROLE_IDENTIFIER
    assert "levels" not in declared.details
    assert "code7" not in f"{declared.details}", (
        "no identifier value may appear anywhere"
    )


def test_the_declined_column_says_what_was_not_assumed() -> None:
    # The withdrawal is not silent: the column that would once have been
    # called a record number carries the reason and the way to declare it.
    described = describe(fixtures.prose(50))
    said = " ".join(described.remarks)
    assert "did NOT assume they are record numbers" in said
    assert "--identifier NAME" in said


def test_all_different_numbers_are_numbers_not_identifiers() -> None:
    # In a small table nearly every measurement is all-different.
    # Calling such a column a record number would throw away exactly the
    # distribution the twin exists to reproduce.
    described = describe([str(index) for index in range(50)])
    assert described.role == taxonomy.ROLE_COUNT
    assert "percentiles" in described.details
    assert any("--identifier" in remark for remark in described.remarks)


def test_the_user_can_declare_a_numeric_column_to_be_a_record_number() -> None:
    described = describe([str(index) for index in range(50)], forced=True)
    assert described.role == taxonomy.ROLE_IDENTIFIER
    assert "percentiles" not in described.details
    assert "you told synthtwin" in described.detection_evidence


def test_all_different_sentences_are_free_text_not_identifiers() -> None:
    described = describe(fixtures.prose(50))
    assert described.role == taxonomy.ROLE_TEXT
    assert "length" in described.details
    body = f"{described.details}"
    assert "clinic" not in body, "no free-text value may appear anywhere"


def test_two_values_are_binary_whatever_their_case() -> None:
    described = describe(["yes", "no", "YES", "No"] * 10)
    assert described.role == taxonomy.ROLE_BINARY
    assert any("upper and lower case" in remark for remark in described.remarks)


def test_two_dates_are_described_by_their_two_values() -> None:
    # Fewer values than a distribution needs: recording both values and
    # their counts describes the column exactly, and the remark says so.
    described = describe(["2024-01-02"] * 20 + ["2024-03-04"] * 20)
    assert described.role == taxonomy.ROLE_BINARY
    assert any("also read as numbers or dates" in r for r in described.remarks)


@pytest.mark.parametrize(
    ("values", "expected_format"),
    [
        ([f"2024-01-{day:02d}" for day in range(1, 29)], "iso-date"),
        ([f"2024010{day}" for day in range(1, 10)], "compact-date"),
        ([f"01/{day:02d}/2024" for day in range(1, 29)], "month-first-date"),
        (["2024-Q1", "2024-Q2", "2024-Q3", "2023-Q4"] * 5, "year-quarter"),
        (
            [f"2024-01-02T10:{minute:02d}:00" for minute in range(30)],
            "iso-datetime",
        ),
    ],
)
def test_date_formats_are_detected(
    values: list[str], expected_format: str
) -> None:
    described = describe(values)
    assert described.role == taxonomy.ROLE_DATETIME
    assert described.details["format"] == expected_format


def test_slash_dates_report_the_month_first_reading() -> None:
    described = describe([f"01/{day:02d}/2024" for day in range(1, 29)])
    assert any("month first" in remark for remark in described.remarks)


def test_the_tail_boundaries_are_canonical_and_ordered() -> None:
    """Stage 3: the two tail boundaries stand where the floor puts them.

    A column of thirty different days at a floor of eleven publishes the
    twelfth value from the bottom and the twelfth from the top -- the
    smallest value with eleven cells strictly below it, and the mirror --
    each as canonical text, with the count of cells beyond it. Neither is
    one of the eleven outermost values, and the ladder's own two ends are
    empty, because the ranks they would be read from are inside the two
    tails.
    """
    days = [f"2024-01-{index + 1:02d}" for index in range(30)]
    described = describe(days)
    low = described.details["low_tail"]
    high = described.details["high_tail"]
    assert isinstance(low, dict) and isinstance(high, dict)
    assert low["boundary"] == days[11]
    assert high["boundary"] == days[len(days) - 12]
    assert low["rows"] == 11 and high["rows"] == 11
    assert low["boundary"] < high["boundary"]
    assert low["mean_distance"] == 6.0 and high["mean_distance"] == 6.0
    ladder = described.details["date_percentiles"]
    assert isinstance(ladder, dict)
    assert ladder["min"] is None and ladder["max"] is None
    assert ladder["p50"] == days[14]


def _quarter(step: int) -> str:
    """The `step`th quarter from 1995-Q1, as the column writes it."""
    return f"{1995 + step // 4:04d}-Q{step % 4 + 1}"


def _shared_quarters() -> list[str]:
    """A column of quarters whose low tail holds two values, one of them rare.

    Twelve cells below the boundary `1995-Q3`: two at `1995-Q1`, two
    quarters below it, and ten at `1995-Q2`, one below. Every later
    quarter is held by six cells, so the column's own values come from a
    small fixed set and many rows stand on each.
    """
    cells = [_quarter(0)] * 2 + [_quarter(1)] * 10
    for step in range(2, 42):
        cells += [_quarter(step)] * 6
    return cells


def _all_different_clock() -> list[str]:
    """Nine hundred different minutes of one day, reaching both its ends."""
    cells = []
    for minute in range(1440):
        if minute % 8 != 7:
            cells += [f"{minute // 60:02d}:{minute % 60:02d}"]
    return cells[:900]


def test_the_mean_beside_a_tails_values_is_withheld_where_it_settles_a_count() -> None:
    """Stage 3 (plan P4-D329): values plus a mean can settle a small count.

    A tail that lists its values tells a reader that each of them is held
    at least once. Where it publishes its mean distance beside them the
    counts must ALSO add to `rows` and weight to the whole sum, and over
    two values that is two equations in two unknowns, so both counts
    follow exactly. Here the low tail holds twelve cells, two at
    `1995-Q1` and ten at `1995-Q2`, two quarters and one quarter below
    the boundary: from `rows` and the mean a reader solves the pair and
    reads a count of TWO, below the floor of eleven, which is the count
    the floor exists to keep unsaid. `taxonomy._values_mean_pins` is the
    guard that withholds the mean for that reason, and this is its own
    red case.

    The expectation is derived here, not copied: the test solves the
    same pair the reader would and asserts that it has exactly ONE
    answer, and that the answer holds a count below the floor.

    MUTATION (run on a scratch copy of `src`, the worktree unwritten):
    `_values_mean_pins` returning False before its body publishes
    `mean_distance` 1.1666666666666667 on this tail, and this test is
    the only one in the suite that goes red.
    """
    cells = _shared_quarters()
    described = describe(cells)
    low = described.details["low_tail"]
    assert isinstance(low, dict)
    assert low["boundary"] == _quarter(2)
    assert low["values"] == [_quarter(0), _quarter(1)]
    assert low["rows"] == 12
    # The reader's own back-solve, written from the rule: how many
    # (near, far) pairs of counts meet the two published facts.
    rows = low["rows"]
    total = 2 * 2 + 10 * 1
    solutions = [
        (near, far)
        for near in range(1, rows)
        for far in range(1, rows)
        if near + far == rows and near * 1 + far * 2 == total
    ]
    assert solutions == [(10, 2)], solutions
    assert min(solutions[0]) < SETTINGS.small_cell_floor
    assert low["mean_distance"] is None
    assert low["rms_distance"] is None


def test_a_tail_lists_no_value_that_one_row_holds() -> None:
    """Stage 3 (plan P4-D342): the owner's ruling reaches shared values only.

    The ruling of 2026-09-22 -- "many people will be there and there is
    no big deal in knowing that it's there" -- is about bounded scales
    with few values, and its premise is that many rows stand on each
    listed value. So a tail lists its values only where every value it
    would list is held by at least `TAIL_SHARED_CELLS` of its cells AND
    the column's values come from a small fixed set rather than a fine
    grid, or where every listed value is held by the floor's own number
    of cells, which is a heap. Everywhere else it publishes its shape.

    THE CASE THAT FORCED THE RULE: a column of nine hundred DIFFERENT
    minutes listed the eleven outermost times of each side, its own
    `00:00` and `23:59` among them, each held by exactly one row, with
    `rows` equal to the length of the list so that the count of one
    followed by subtraction.

    MUTATION: with the two halves of the rule made inert the same column
    lists eleven values per side, every one of them held by one cell,
    and this test goes red on the first assertion.
    """
    clock = _all_different_clock()
    described = describe(clock)
    assert described.role == taxonomy.ROLE_CLOCK
    for side in ("low_tail", "high_tail"):
        tail = described.details[side]
        assert isinstance(tail, dict)
        assert tail["values"] is None, side
        assert isinstance(tail["mean_distance"], float)
        assert isinstance(tail["rms_distance"], float)
    published = {
        value
        for value in described.details.values()
        if isinstance(value, str)
    }
    for tail_key in ("low_tail", "high_tail"):
        tail = described.details[tail_key]
        assert isinstance(tail, dict)
        published.add(str(tail["boundary"]))
    ladder = described.details["clock_percentiles"]
    assert isinstance(ladder, dict)
    for rung in ladder.values():
        if rung is not None:
            published.add(str(rung))
    assert min(clock) not in published and max(clock) not in published

    # ...AND THE RULE STILL LETS A BOUNDED SCALE THROUGH, so the guard
    # is not a blanket refusal: every value these tails list is held by
    # more than one row of the column.
    quarters = _shared_quarters()
    held = {}
    for cell in quarters:
        held[cell] = held.get(cell, 0) + 1
    listed = describe(quarters)
    for side in ("low_tail", "high_tail"):
        tail = listed.details[side]
        assert isinstance(tail, dict)
        assert tail["values"] is not None, side
        for value in tail["values"]:
            assert held[value] >= taxonomy.TAIL_SHARED_CELLS, (side, value)


def test_a_floor_sized_heap_lists_its_value_on_any_grid() -> None:
    """Stage 3 (plan P4-D342): a heap is the ruling's own case.

    The column's grid decides whether its values are a bounded scale,
    and a column of moments to the second is a fine grid however many
    rows it has. But where every value a tail would list is held by at
    least the FLOOR's number of cells, "many people are there" is true
    by the project's own measure of many, and the grid says nothing
    against it: the forty cells of `0001-01-01`, the value two common
    systems write for no date at all, are named rather than turned into
    a distance of sixty-three thousand million seconds that means the
    same thing.
    """
    cells = ["0001-01-01 00:00:00"] * 40
    for step in range(360):
        cells += [f"2020-01-01 {step % 24:02d}:{step % 60:02d}:{step % 57:02d}"]
    described = describe(cells)
    low = described.details["low_tail"]
    assert isinstance(low, dict)
    assert low["rows"] == 40
    assert low["values"] == ["0001-01-01 00:00:00"]
    assert cells.count("0001-01-01 00:00:00") >= SETTINGS.small_cell_floor


def test_whole_non_negative_numbers_are_counts() -> None:
    described = describe(fixtures.numbers(1, 60, 0, 9))
    assert described.role == taxonomy.ROLE_COUNT
    assert described.details["integer_valued"] is True


def test_numbers_with_a_fraction_are_continuous() -> None:
    described = describe([f"{index}.5" for index in range(60)])
    assert described.role == taxonomy.ROLE_CONTINUOUS
    assert described.details["integer_valued"] is False


def test_negative_whole_numbers_are_continuous_not_counts() -> None:
    described = describe([str(index - 30) for index in range(60)])
    assert described.role == taxonomy.ROLE_CONTINUOUS
    assert described.details["n_negative"] == 30


def test_a_few_stragglers_do_not_stop_a_column_being_numbers() -> None:
    values = [str(index) for index in range(200)] + ["not a number"]
    described = describe(values)
    assert described.role == taxonomy.ROLE_COUNT
    assert any("are not numbers" in remark for remark in described.remarks)


def test_a_column_that_is_only_mostly_numbers_publishes_nothing() -> None:
    """Corrected from `test_a_column_that_is_mostly_numbers_keeps_...`.

    The old test required ninety numbers beside ten stray words to be
    described as numbers -- the undocumented majority rule. Review item
    P1-R6-F7 settles the policy at one line, the plan's 0.99: a column
    described as numbers on the strength of ninety of its hundred values
    publishes a mean, a smallest and a largest value computed from the
    ninety while the other ten are in no distribution at all, which is a
    column dropped, miscast and approximated at once. The column now
    publishes nothing and says why, and the counts the old test cared
    about are still there, on the free-text role, because they are
    fields of ColumnProfile rather than of a branch.
    """
    values = [str(index) for index in range(90)] + ["word"] * 10
    described = describe(values)
    # SUPERSEDED BY LANDING L8, and this is the supersession the close
    # plan asked for rather than a test edited to suit new code. The
    # objection review item P1-R6-F7 recorded was not "never publish
    # below the line": it was that the old rule published a
    # distribution over ONE population and said nothing about the
    # other. Ninety numbers beside a word on ten rows is a compound
    # column -- both halves described, both counts published, every
    # cell in exactly one of them -- so the objection does not reach
    # it. A column of numbers beside ALL-DIFFERENT prose still
    # publishes nothing, which `tests/test_p1r6f7_one_policy.py` holds
    # unchanged.
    assert described.role == taxonomy.ROLE_COMPOUND
    assert described.n_not_numeric == 10
    assert described.n_numeric == 90
    # AND WHAT MAKES IT A SUPERSESSION RATHER THAN A RELABELLING: both
    # populations are really described, and together they are the
    # whole column.
    assert described.details["n_numeric_cells"] == 90
    assert described.details["n_label_cells"] == 10
    assert "percentiles" in described.details["numbers"]
    # THE LABEL HALF IS DESCRIBED, WHICH IS NOT THE SAME AS NAMED. Its
    # one word covers fewer rows than the publication floor asks, so
    # the floor holds the word back and the half publishes a COUNT of
    # what it holds back instead -- which still accounts for every one
    # of its cells, and is the floor doing its work rather than the
    # description falling short.
    half = described.details["labels"]
    shown = sum(level["count"] for level in half["levels"])
    assert shown + half["suppressed_rows"] == half["n_present"]
    assert half["n_present"] == described.details["n_label_cells"]
    # THE COLUMN'S OWN BLOCK CARRIES NO DISTRIBUTION, and that is still
    # true: the numbers are described inside their own half, where a
    # consumer is told they answer for 90 cells and not for 100. A
    # reader routing on the column's type is not handed a mean.
    assert "percentiles" not in described.details

    # AND THE DECLINE SENTENCE IS GONE, because there is no decline.
    # It read "90 of the 100 values are written as numbers ... only
    # when at least 99 of them read that way", which is what a column
    # was told when the line refused it and nothing was published. The
    # line has not moved -- this column is still not read as NUMBERS --
    # but it is no longer refused, so there is nothing to explain.
    said = " ".join(described.remarks)
    assert "written as numbers" not in said, said


def test_a_small_set_of_labels_is_categorical() -> None:
    described = describe(fixtures.labels(2, 100))
    assert described.role == taxonomy.ROLE_CATEGORICAL
    assert described.n_distinct == 5


def test_labels_below_the_floor_are_pooled_not_published() -> None:
    values = ["common"] * 100 + ["ordinary"] * 40 + ["rare"] * 3
    described = describe(values)
    assert described.role == taxonomy.ROLE_CATEGORICAL
    labels = [level["label"] for level in described.details["levels"]]
    assert labels == ["common", "ordinary"]
    assert described.details["suppressed_levels"] == 1
    assert described.details["suppressed_rows"] == 3
    assert "rare" not in f"{described.details}"


def test_two_labels_are_binary_and_the_floor_still_applies() -> None:
    described = describe(["common"] * 100 + ["rare"] * 3)
    assert described.role == taxonomy.ROLE_BINARY
    labels = [level["label"] for level in described.details["levels"]]
    assert labels == ["common"]
    assert described.details["suppressed_rows"] == 3


def test_levels_are_ordered_by_count_then_label() -> None:
    values = ["b"] * 20 + ["a"] * 20 + ["c"] * 30
    described = describe(values)
    ordered = [level["label"] for level in described.details["levels"]]
    assert ordered == ["c", "a", "b"]


# -- missing values and sentinels ------------------------------------


def test_missing_values_are_counted_by_class() -> None:
    # The exact spellings are no longer published unconditionally: a
    # spelling shared by fewer rows than the small-cell floor is a rare
    # attribute of a few people, so only the CLASS is reported (review
    # items P1-R1-F17, P1-R1-F10). The counts still add up.
    values = ["1"] * 20 + ["", "NA", "n/a", "NULL", ""]
    described = describe(values)
    assert described.n_missing == 5
    assert sum(described.missing_by_class.values()) == 5
    assert "na" not in f"{described.missing_by_class}"


def test_present_and_missing_always_add_up_to_the_row_count() -> None:
    values = ["1", "", "2", "NA", "3"]
    described = describe(values)
    assert described.n_present + described.n_missing == len(values)


def test_an_outlying_sentinel_number_is_read_as_missing() -> None:
    # Frequent enough to be a convention and far outside the rest, so it
    # is read as "no value" -- and the verdict is published, because the
    # count clears the small-cell floor.
    values = [str(index) for index in range(1, 200)] + ["-999"] * 15
    described = describe(values)
    assert described.sentinel_verdicts == [
        {
            "candidate": "-999",
            "verdict": "read_as_missing",
            "reason": "outlier_and_frequent",
            "n_occurrences": 15,
            # WHICH PUBLISHED SPELLING THIS DECISION TOOK OUT (repair
            # pass of landing 2b.6, contract V5). It is the cell's own
            # text, which is what `missing_by_source` keys itself on,
            # and it is what tells a later reader that this key is one
            # column's judgement rather than a word the person named
            # for the whole table.
            "spellings": ["-999"],
        }
    ]
    assert described.missing_by_class["(numeric-sentinel)"] == 15
    assert described.details["percentiles"]["min"] == 1.0


def test_a_sentinel_that_is_not_an_outlier_stays_a_number() -> None:
    # In a column that really ranges over thousands, -999 is data.
    values = [str(value) for value in range(-5000, 5000, 50)] + ["-999"] * 15
    described = describe(values)
    assert described.sentinel_verdicts[0]["verdict"] == "kept_as_a_number"
    assert described.sentinel_verdicts[0]["reason"] == "not_an_outlier"
    assert described.missing_by_class["(numeric-sentinel)"] == 0


def test_a_rare_sentinel_stays_a_number() -> None:
    # An outlier by distance, but far too rare to be a convention: one
    # value in a thousand. Reading it as "no value" would delete a real
    # observation. Its verdict is not named, because naming a value that
    # appears once would disclose it (review item P1-R1-F10).
    values = [str(index % 100 + 1) for index in range(1000)] + ["-999"]
    described = describe(values)
    assert described.missing_by_class["(numeric-sentinel)"] == 0
    assert described.n_sentinel_candidates_unpublished == 1
    assert "-999" not in f"{described.sentinel_verdicts}{described.remarks}"


def test_every_sentinel_candidate_present_gets_a_verdict() -> None:
    values = (
        [str(index) for index in range(1, 200)]
        + ["-999"] * 15
        + ["9999"] * 15
    )
    described = describe(values)
    judged = {entry["candidate"] for entry in described.sentinel_verdicts}
    assert judged == {"-999", "9999"}, (
        "every candidate that appears must be judged, and each judged "
        "against the others' absence so they cannot mask one another"
    )


# -- borderline reporting --------------------------------------------


def test_a_column_one_value_from_a_different_role_says_so() -> None:
    values = [str(index) for index in range(99)] + ["word"]
    described = describe(values)
    assert any("close to the line" in remark for remark in described.remarks)


def test_a_column_far_from_any_threshold_is_quiet() -> None:
    described = describe(fixtures.labels(3, 200))
    assert not any("close to the line" in r for r in described.remarks)


# -- statistics -------------------------------------------------------


def test_percentiles_never_go_down() -> None:
    described = describe(fixtures.numbers(4, 500, 0, 10_000))
    ladder = described.details["percentiles"]
    values = [ladder[label] for label, _num, _den in taxonomy.LADDER]
    assert values == sorted(values)


def test_counts_are_exact_not_rounded() -> None:
    values = ["0"] * 7 + ["-1"] * 3 + ["5"] * 10
    described = describe(values)
    assert described.details["n_zero"] == 7
    assert described.details["n_negative"] == 3
    assert described.details["n_rows"] == 20


def test_statistics_match_a_hand_computation() -> None:
    described = describe(["1", "2", "3", "4"])
    ladder = described.details["percentiles"]
    assert ladder["min"] == 1.0
    assert ladder["p50"] == 2.5
    assert ladder["max"] == 4.0
    assert described.details["mean"] == 2.5
    # Sample standard deviation of 1,2,3,4 is sqrt(5/3).
    assert described.details["std"] == pytest.approx(1.29099444874, rel=1e-9)


def test_spread_and_shape_are_undefined_rather_than_invented() -> None:
    # Checked on the statistics function directly: a column with one or
    # two different values never reaches it, because such a column is
    # described as a constant or as two possible values instead. The
    # guards still belong there, so that the function is correct on its
    # own terms rather than only where it happens to be called.
    single = taxonomy._moments([5.0])
    assert single["std"] is None
    assert single["skew"] is None
    pair = taxonomy._moments([5.0, 7.0])
    assert pair["std"] is not None
    assert pair["skew"] is None
    flat = taxonomy._moments([5.0, 5.0, 5.0])
    assert flat["skew"] is None, "no shape to report when nothing varies"
    assert describe(["5"] * 30).role == taxonomy.ROLE_CONSTANT
    assert describe(["5", "7"] * 15).role == taxonomy.ROLE_BINARY


def test_published_numbers_keep_every_digit_they_earned() -> None:
    # An earlier revision rounded every number to twelve significant
    # digits. On values around 1e15 that collapsed the whole ladder onto
    # one number, so the profile said the range was zero while also
    # reporting a spread (review finding P1-R1-F6). Numbers are now
    # published exactly as computed.
    assert taxonomy.published(1 / 3) == 0.3333333333333333
    assert taxonomy.published(float("inf")) is None
    assert taxonomy.published(-0.0) == 0.0, "row order must not reach the bytes"
    described = describe([str(1000000000000000 + step) for step in range(10)])
    ladder = described.details["percentiles"]
    assert ladder["min"] != ladder["max"], (
        "ten different values must not publish an empty range"
    )
    assert ladder["min"] == 1000000000000000.0
    assert ladder["max"] == 1000000000000009.0


def test_every_present_value_is_counted_once() -> None:
    values = fixtures.labels(5, 300) + [""] * 20
    described = describe(values)
    total = sum(
        level["count"] for level in described.details["levels"]
    ) + described.details["suppressed_rows"]
    assert total == described.n_present


def test_the_taxonomy_never_refuses_a_column() -> None:
    # Charter principle 5: a column is described or safely absorbed as
    # text; "unsupported" is not an outcome.
    nasty = ["", "1", "two", "2024-01-01", "yes", "1,2,3", "  ", "?", "x" * 300]
    described = describe(nasty * 10)
    assert described.role in taxonomy.ROLES


def test_settings_travel_with_the_decision() -> None:
    strict = taxonomy.Settings(small_cell_floor=50)
    values = ["common"] * 100 + ["uncommon"] * 30
    described = describe(values, settings=strict)
    labels = [level["label"] for level in described.details["levels"]]
    assert labels == ["common"], (
        "raising the smallest group size must withhold more, not less"
    )


def test_sentinel_table_is_the_documented_one() -> None:
    assert parsing.NUMERIC_SENTINELS == (-9999.0, -999.0, 9999.0)
