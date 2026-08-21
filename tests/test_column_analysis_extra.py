"""Red against the proposed redesign, green after the corrections.

Each test names the defect it pins. Put this file at
tests/test_column_analysis_review.py, or fold the tests into
tests/test_column_analysis.py.
"""

import json

import pytest

import fixtures
from synthtwin import parsing, profile, taxonomy

SETTINGS = taxonomy.Settings()


def describe(
    values: list[str],
    n_rows: "int | None" = None,
    settings: taxonomy.Settings = SETTINGS,
    forced: bool = False,
) -> taxonomy.ColumnProfile:
    return taxonomy.profile_column(
        "column", 1, values, n_rows if n_rows is not None else len(values),
        settings, forced,
    )


def whole_block(described: taxonomy.ColumnProfile) -> str:
    return (
        json.dumps(profile._column_block(described), sort_keys=True)
        + " ".join(described.remarks)
        + " ".join(described.publication_notes)
    )


# -- F1: the category rule must not steal a column of measurements ----


@pytest.mark.parametrize("stragglers", [0, 1])
def test_a_repeating_numeric_column_keeps_its_distribution(
    stragglers: int,
) -> None:
    """Corrected for the one numeric line (review item P1-R6-F7).

    The original case is unchanged where it still holds: one hundred
    ages that REPEAT, plus a cell or two that do not read as numbers,
    must be described as numbers rather than swallowed by the category
    rule -- which under the deleted rule made all 23 levels fall below
    the small-cell floor and left the profile with no percentile, no
    mean, no minimum and no label at all.

    What changed is where "a few" stops. The old parametrization ran to
    twenty stragglers and required a published distribution for all of
    them, which only the deleted majority rule gave: at twenty of a
    hundred and twenty, a published mean would be computed from five
    sixths of the column with the rest in no distribution at all. One
    straggler in a hundred and one is inside the plan's line and two in
    a hundred and two are not, so the cases inside it are kept here and
    the ones outside it are the test below.
    """
    ages = [str(20 + (index % 21)) for index in range(100)]
    described = describe(ages + [f"refused{n}" for n in range(stragglers)])
    assert described.role == taxonomy.ROLE_COUNT
    assert described.details["percentiles"]["min"] == 20.0
    assert described.details["percentiles"]["max"] == 40.0
    assert described.details["n_used_in_statistics"] == 100
    assert described.details["n_left_out_of_statistics"] == stragglers


@pytest.mark.parametrize("stragglers", [2, 3, 5, 20])
def test_too_many_stragglers_publish_nothing_and_say_why(
    stragglers: int,
) -> None:
    # Past the line the column is not described as numbers, and the
    # remark carries both readings and the count each one reached, so
    # the person can see the arithmetic that declined it.
    ages = [str(20 + (index % 21)) for index in range(100)]
    described = describe(ages + [f"refused{n}" for n in range(stragglers)])
    assert described.role == taxonomy.ROLE_TEXT
    assert "percentiles" not in described.details
    said = " ".join(described.remarks)
    assert f"100 of the {100 + stragglers} values are written as numbers" in said
    assert "read that way" in said


def test_a_small_set_of_numeric_codes_is_still_a_set_of_categories() -> None:
    """A column of labels that happen to be digits, below the line."""
    described = describe(["1", "2", "3"] * 30 + ["unknown"] * 5)
    assert described.role == taxonomy.ROLE_CATEGORICAL
    assert [level["label"] for level in described.details["levels"]] == [
        "1", "2", "3",
    ]


def test_the_category_ceiling_is_a_share_of_the_values_present() -> None:
    """Corrected from `test_the_numeric_category_guard_reads_the_...`.

    The guard this pinned -- a cap of twelve on mostly numeric columns,
    between two numeric rules -- is deleted with the second numeric rule
    (review item P1-R6-F7). The ceiling that decides the role now is the
    plan's: a tenth of the values present, never more than 1000 and
    never fewer than 2. Seven different values are a set of categories
    in a hundred and four rows and are not in fifty-two, and the shorter
    column publishes nothing rather than a part of itself.
    """
    codes = [str(index) for index in range(6)]
    short = describe((codes * 10)[:50] + ["unknown"] * 2)
    long = describe((codes * 20)[:100] + ["unknown"] * 4)
    assert long.role == taxonomy.ROLE_CATEGORICAL
    assert short.role == taxonomy.ROLE_TEXT
    assert "levels" not in short.details


# -- F2: a percentile ladder must rest on the cells it is computed from


def _leaves_equal_to(node: object, number: float, text: str) -> list[str]:
    """Every leaf of a block that holds this value, by either spelling."""
    found: list[str] = []
    if isinstance(node, dict):
        for key in node:
            if key == text:
                found = found + [f"key {key!r}"]
            found = found + _leaves_equal_to(node[key], number, text)
    elif isinstance(node, list):
        for item in node:
            found = found + _leaves_equal_to(item, number, text)
    elif isinstance(node, bool):
        pass
    elif isinstance(node, (int, float)) and float(node) == number:
        found = found + [f"value {node!r}"]
    elif isinstance(node, str) and node == text:
        found = found + [f"value {node!r}"]
    return found


def test_a_ladder_is_never_built_from_a_handful_of_cells() -> None:
    """A ladder must rest on the cells it is computed from.

    Fifty cells no format can hold, ONE real number and forty-nine notes
    cleared the deleted majority rule, so the column was described as a
    count whose eleven rungs were all one row's exact value. With one
    line at 0.99 (review item P1-R6-F7) the column is not written as
    numbers often enough to be named for them either, so it lands on
    free text -- which publishes no value and no ladder. The property
    the test exists for is unchanged: no rung of any ladder is ever that
    one row's value.
    """
    values = (
        ["1e999"] * 50 + ["7"] + fixtures.prose(49)
    )
    described = describe(values)
    assert described.role == taxonomy.ROLE_TEXT
    assert "percentiles" not in described.details
    # The one real number must not be published as a VALUE. Searching
    # the block for the character `7` cannot say that -- it matches the
    # 7 inside a count of 47 or a length of 27 -- so the check is on
    # what the block actually holds: no leaf equal to that value, by
    # either spelling.
    assert not _leaves_equal_to(described.details, 7.0, "7")


def test_the_unrepresentable_evidence_states_what_the_column_shows() -> None:
    """Fixture corrected for the one line (review item P1-R6-F7).

    The sentence under test is unchanged and so is the defect it closes:
    "all 50 of the 100 values are written as numbers" was false whenever
    fewer than all of them were. The fixture is now a column that
    reaches the numeric-unrepresentable role under the ratified rule --
    written as numbers at the parse rate, holdable at nothing like it.
    """
    values = ["1e999"] * 99 + ["a note written out in words"]
    described = describe(values)
    assert described.role == taxonomy.ROLE_UNREPRESENTABLE
    assert "all 99 of the 100" not in described.detection_evidence
    assert "99 of the 100 values are written as numbers" in (
        described.detection_evidence
    )


def test_a_majority_numeric_column_publishes_nothing_and_says_why() -> None:
    """Corrected from `test_a_majority_numeric_column_still_keeps_...`.

    This is the reviewer's own worst example in review item P1-R6-F7:
    sixty numbers beside forty two-word notes were published with role
    `count`, `min: 0`, `max: 59` and `mean: 29.5`, with forty cells left
    out of the distribution and named nowhere in the profile. The old
    test required exactly that. The column now publishes nothing, and
    the remark names both readings and how far each one got.
    """
    described = describe(
        [str(index) for index in range(60)]
        + fixtures.prose(40)
    )
    assert described.role == taxonomy.ROLE_TEXT
    assert "percentiles" not in described.details
    assert "mean" not in described.details
    assert described.n_numeric == 60
    said = " ".join(described.remarks)
    assert "60 of the 100 values are written as numbers" in said
    assert "none of them reads as a date" in said
    assert "at least 99 of them read that way" in said


# -- F3: one UTC offset, one floor ------------------------------------


def test_a_below_floor_utc_offset_is_named_nowhere() -> None:
    """`utc_offsets` pooled the lone zone away; the endpoint published it."""
    values = [f"2024-03-{day:02d}T09:00:00+00:00" for day in range(1, 29)]
    values = values + ["2024-04-01T09:00:00+05:45"]
    described = describe(values)
    assert described.role == taxonomy.ROLE_DATETIME
    assert described.details["utc_offsets"] == {
        "+00:00": 28, parsing.MISSING_WITHHELD: 1,
    }
    assert described.details["latest_utc_offset"] == parsing.MISSING_WITHHELD
    assert "+05:45" not in whole_block(described)


def test_an_offset_above_the_floor_is_still_named() -> None:
    values = [f"2024-03-{day:02d}T09:00:00+05:45" for day in range(1, 29)]
    described = describe(values)
    assert described.details["earliest_utc_offset"] == "+05:45"
    assert described.details["latest_utc_offset"] == "+05:45"


# -- F4: nothing is routed by the width of its text -------------------


def test_a_stray_space_changes_nothing_now_the_width_rule_is_gone() -> None:
    """Corrected from `test_one_stray_space_does_not_undo_the_fixed_...`.

    The old test pinned a repair to the fixed-width-code rule: two of
    its predicates read the trimmed cell and one read the raw one, so a
    single stray space handed the column to the numeric rule with its
    padding gone. Review item P1-R6-F7 deletes the rule outright --
    nothing may be routed by the WIDTH of its text -- so the defect it
    repaired cannot happen. What is worth keeping is the other half:
    surrounding whitespace changes nothing about how a column is read,
    which is what the plan (P1-D4) requires of every numeric shape.
    """
    padded = describe([" 00501", "02139", "52242"] * 20)
    plain = describe(["00501", "02139", "52242"] * 20)
    assert padded.role == plain.role == taxonomy.ROLE_COUNT
    assert padded.details["percentiles"] == plain.details["percentiles"]
    assert "fixed_width_code" not in padded.details


# -- F5: the free-text remark must not misdirect a measurement --------


@pytest.mark.parametrize("values", [
    [f"${index}.50" for index in range(60)],
    [f"{index}.5%" for index in range(60)],
])
def test_the_free_text_remark_names_both_readings(
    values: list[str],
) -> None:
    """Naming only --identifier tells a price column to withhold itself.

    Both fixtures are read by the affixed-number rule now -- a price and
    a percentage ARE numbers wearing shared text -- so the column gets
    its distribution instead of being declined. The sentence this test
    is about survived the move: it still names `--identifier`, and it
    still says "measurement", because the reason for saying both is the
    same one. A column of codes must be able to recognize itself.
    """
    described = describe(values)
    assert described.role != taxonomy.ROLE_IDENTIFIER
    remark = " ".join(described.remarks)
    assert "--identifier" in remark
    assert "measurement" in remark
    # AND NOT THE FREE-TEXT PATH'S ADVICE. "Write them as plain
    # numbers" is what a reader is told when nothing of their column
    # was published; these two columns publish a full distribution, so
    # the same sentence would send them to rewrite a table to obtain
    # what they already have.
    assert "write them as plain numbers" not in remark
    assert "Nothing from this column is published" not in remark
