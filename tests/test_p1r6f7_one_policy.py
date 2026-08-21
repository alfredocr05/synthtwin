"""P1-R6-F7: one taxonomy policy, and the neighbours on both sides of it.

The plan and the code described different products. The owner settled
the policy, and it is the plan's:

* a column is described as numbers -- count or continuous -- only when
  at least 0.99 of its present values read as numbers this format can
  hold, and there is no second, lower line;
* a column is described as a set of categories only when the number of
  different values it holds, after trimming and case folding, is at most
  `min(1000, a tenth of the values present)`, and never below 2;
* nothing is routed by the WIDTH of its text;
* a column that fails both is described as free text, which publishes
  NOTHING, and carries a remark naming the competing readings and how
  far each one got;
* the settings recorded in every profile are exactly the thresholds that
  produced it.

Every threshold here is tested at the value that just fails, the value
that just passes, and where it matters the value in between, because a
policy that is only tested in the middle is a policy nobody can check.
"""

import dataclasses
import json
import pathlib

import pytest

import fixtures
from synthtwin import profile, reading, taxonomy

SETTINGS = taxonomy.Settings()


def describe(
    values: list[str],
    settings: taxonomy.Settings = SETTINGS,
    forced: bool = False,
) -> taxonomy.ColumnProfile:
    """One column, described by the rules under test."""
    return taxonomy.profile_column(
        "column", 1, values, len(values), settings, forced
    )


def whole_block(described: taxonomy.ColumnProfile) -> str:
    """Everything about one column that reaches a file, as one string."""
    return (
        json.dumps(profile._column_block(described), sort_keys=True)
        + " ".join(described.remarks)
        + " ".join(described.publication_notes)
    )


def numeric_column(parsing_count: int, total: int = 100) -> list[str]:
    """``parsing_count`` numbers and enough distinct notes to fill ``total``.

    The notes are all different, so the category rule cannot claim the
    column either: what is being tested is the numeric line alone.
    """
    numbers = [str(index) for index in range(parsing_count)]
    notes = fixtures.prose(total - parsing_count)
    return numbers + notes


_PROSE = fixtures.prose(40)

# The labels these ceiling tests count. They have to be values no rule
# reads on their own: `label0`, `label1` and the rest are a number
# wearing the word `label`, which the affixed-number rule reads -- so a
# column PAST the ceiling would take that role instead of falling to
# free text, and the sentence these tests are about belongs to free
# text. The ceiling is the same ceiling whatever the values are.
_LABELS = fixtures.prose(1100)


def ceiling_of(values: list[str]) -> int:
    """The category ceiling this column is judged against."""
    cells = taxonomy._tally(
        taxonomy._classify_all(values), len(values), SETTINGS
    )
    return taxonomy._categorical_ceiling(cells)


# -- the numeric line: 49, 50, 98 and 99 per cent ---------------------
#
# 50 is where the deleted rule stood, so it is tested from both sides;
# 99 is where the ratified rule stands, so it is too.


@pytest.mark.parametrize("parsing_count", [49, 50, 51, 98])
def test_a_column_below_the_numeric_line_publishes_no_statistic(
    parsing_count: int,
) -> None:
    described = describe(numeric_column(parsing_count))
    assert described.role == taxonomy.ROLE_TEXT, (
        f"{parsing_count} of 100 values reading as numbers is below the "
        f"line, so no statistic of this column may be published"
    )
    for key in ("percentiles", "mean", "std", "skew", "levels"):
        assert key not in described.details
    # The counts are still there, because they are fields of the class
    # rather than of a branch -- but they are counts, not values.
    assert described.n_numeric == parsing_count
    assert described.n_not_numeric == 100 - parsing_count


def test_the_column_at_the_line_is_described_as_numbers() -> None:
    described = describe(numeric_column(99))
    assert described.role == taxonomy.ROLE_COUNT
    assert described.details["n_used_in_statistics"] == 99
    assert described.details["n_left_out_of_statistics"] == 1
    assert described.details["percentiles"]["max"] == 98.0


def test_the_deleted_majority_rule_leaves_no_trace_in_the_settings() -> None:
    # A profile has to say what policy produced it, so a threshold that
    # no longer decides anything must not be recorded as though it did.
    recorded = profile._settings_block(SETTINGS, [])
    for gone in (
        "numeric_majority",
        "categorical_repetition",
        "categorical_numeric_ceiling",
        "code_minimum_width",
    ):
        assert gone not in recorded, (
            f"{gone} names a rule that no longer exists; a profile that "
            f"records it says its columns were routed by it"
        )
    assert recorded["minimum_parse_rate"] == 0.99
    assert recorded["categorical_share"] == 0.10
    assert recorded["categorical_ceiling"] == 1000
    assert recorded["categorical_floor"] == 2


def test_the_reviewers_own_worst_example_publishes_nothing() -> None:
    # Sixty numeric cells and forty two-word notes were published as
    # role `count` with `min: 0`, `max: 59` and `mean: 29.5`, with the
    # forty in no distribution at all.
    values = [str(index) for index in range(60)] + fixtures.prose(40)
    described = describe(values)
    assert described.role == taxonomy.ROLE_TEXT
    block = whole_block(described)
    assert "29.5" not in block
    assert "percentiles" not in described.details


def test_the_declining_column_names_the_readings_and_the_rates() -> None:
    # What the person is owed instead of a bare verdict: what was tried,
    # how far each reading got, and how far it had to get.
    values = [str(index) for index in range(60)] + [
        f"2024-01-{(index % 28) + 1:02d}" for index in range(40)
    ]
    described = describe(values)
    assert described.role == taxonomy.ROLE_TEXT
    said = " ".join(described.remarks)
    assert "60 of the 100 values are written as numbers" in said
    assert "40 read as dates written as 2024-03-17" in said
    assert "at least 99 of them read that way" in said
    # And the same two counts are in the machine-readable evidence, so
    # the words and the record cannot disagree.
    assert "60 of the 100 values are written as numbers" in (
        described.detection_evidence
    )
    assert "40 read as dates" in described.detection_evidence


def test_a_column_written_as_numbers_but_unholdable_is_named_for_it() -> None:
    # The line applies to what can be HELD; a column above it in written
    # numbers and below it in holdable ones is not free text but the
    # role that says exactly what happened.
    described = describe([f"{index}e999" for index in range(1, 101)])
    assert described.role == taxonomy.ROLE_UNREPRESENTABLE
    assert "percentiles" not in described.details


# -- the category ceiling: just under, at, and just over --------------


@pytest.mark.parametrize("distinct", [9, 10])
def test_a_column_at_or_under_the_ceiling_is_a_set_of_categories(
    distinct: int,
) -> None:
    values = [_LABELS[index % distinct] for index in range(100)]
    described = describe(values)
    assert ceiling_of(values) == 10
    assert described.role == taxonomy.ROLE_CATEGORICAL
    assert described.n_distinct_folded == distinct


def test_a_column_one_value_over_the_ceiling_publishes_nothing() -> None:
    values = [_LABELS[index % 11] for index in range(100)]
    described = describe(values)
    assert ceiling_of(values) == 10
    assert described.role == taxonomy.ROLE_TEXT
    assert "levels" not in described.details
    said = " ".join(described.remarks)
    assert "11 different values" in said
    assert "at most 10" in said


def test_the_ceiling_is_a_tenth_of_the_values_present() -> None:
    # Stated as counts on both sides of a value that does not divide by
    # ten: a tenth of 95 is 9.5, and nine is the most a set of
    # categories may hold.
    values = [_LABELS[index % 9] for index in range(95)]
    assert ceiling_of(values) == 9
    assert describe(values).role == taxonomy.ROLE_CATEGORICAL
    over = [_LABELS[index % 10] for index in range(95)]
    assert describe(over).role == taxonomy.ROLE_TEXT


def test_the_thousand_cap_is_a_ceiling_on_the_role() -> None:
    under: list[str] = []
    for index in range(1000):
        under = under + [_LABELS[index]] * 20
    described = describe(under)
    assert ceiling_of(under) == 1000, "a tenth of 20000 is capped at 1000"
    assert described.role == taxonomy.ROLE_CATEGORICAL
    assert len(described.details["levels"]) == 1000

    over: list[str] = []
    for index in range(1001):
        over = over + [_LABELS[index]] * 20
    beyond = describe(over)
    assert beyond.role == taxonomy.ROLE_TEXT
    assert "levels" not in beyond.details
    said = " ".join(beyond.remarks)
    assert "1001 different values" in said
    assert "at most 1000" in said


def test_the_floor_keeps_a_categorical_path_in_a_tiny_table() -> None:
    # A tenth of twelve values is one, and a ceiling of one would say
    # that a column with two different values has too many to describe
    # -- while the two-value role publishes both of them. The floor
    # keeps the ceiling at two, so the two rules cannot contradict each
    # other in a short table.
    tiny = ["north", "south"] * 6
    assert ceiling_of(tiny) == 2
    assert describe(tiny).role == taxonomy.ROLE_BINARY
    assert ceiling_of(["north"] * 3) == 2
    assert ceiling_of([]) == 2


# -- nothing is routed by the width of its text -----------------------


@pytest.mark.parametrize(
    "values",
    [
        ["00501", "02139", "52242"] * 20,
        [" 00501", "02139", "52242"] * 20,
        [f"{index:06d}" for index in range(50)],
        [
            f"{hour:02d}{minute:02d}"
            for hour in range(24)
            for minute in range(0, 60, 10)
        ],
    ],
)
def test_a_formerly_fixed_width_code_lands_where_the_rules_put_it(
    values: list[str],
) -> None:
    # Every one of these was routed by its width and its leading zero.
    # They are all-digit columns, so the ordinary rules read them as
    # numbers -- and the profile says so in its evidence rather than
    # claiming anything about codes.
    described = describe(values)
    assert described.role == taxonomy.ROLE_COUNT
    assert "fixed_width_code" not in described.details
    assert "leading zeros" not in described.detection_evidence
    assert "code" not in described.detection_evidence


def test_the_padded_column_is_still_declarable_and_then_withholds_all(
) -> None:
    values = [f"{index:06d}" for index in range(50)]
    declared = describe(values, forced=True)
    assert declared.role == taxonomy.ROLE_IDENTIFIER
    block = whole_block(declared)
    for value in values:
        assert value not in block


def test_a_width_rule_would_have_to_be_a_setting_and_there_is_none(
) -> None:
    # The deletion is structural: no threshold about widths survives in
    # the settings, so no profile can claim a column was routed by one.
    declared = {
        field.name for field in dataclasses.fields(taxonomy.Settings)
    }
    assert "code_minimum_width" not in declared


# -- end to end, through the profile document -------------------------


def test_the_policy_reaches_the_written_profile(
    tmp_path: pathlib.Path,
) -> None:
    rows = []
    for index in range(100):
        rows.append(
            [
                # 60 numbers and 40 notes: below the numeric line.
                str(index) if index < 60 else _PROSE[index % len(_PROSE)],
                # 11 labels in 100 rows: above the category ceiling.
                # Prose rather than `label0`..`label10`, so the column
                # past the ceiling falls to free text as this test
                # means it to, instead of being read as a number
                # wearing the word `label`.
                _LABELS[index % 11],
                # 9 labels in 100 rows: within it.
                _LABELS[20 + index % 9],
                # A zero-padded code column, read by the ordinary rules.
                f"{index:06d}",
            ]
        )
    table = reading.read_table(
        str(
            fixtures.write(
                tmp_path,
                "policy.csv",
                fixtures.rows_to_csv(
                    ["mixed", "many_labels", "few_labels", "padded"], rows
                ),
            )
        )
    )
    document = profile.build_document(table, SETTINGS, [])
    roles = {column["name"]: column["role"] for column in document["columns"]}
    assert roles == {
        "mixed": taxonomy.ROLE_TEXT,
        "many_labels": taxonomy.ROLE_TEXT,
        "few_labels": taxonomy.ROLE_CATEGORICAL,
        "padded": taxonomy.ROLE_COUNT,
    }
    serialized = profile.serialize(document)
    assert '"minimum_parse_rate": 0.99' in serialized
    assert '"categorical_share": 0.1' in serialized
    # Neither declining column publishes a value of itself.
    for index in range(60):
        assert f'"label{index % 11}"' not in serialized
    assert '"note 61 in words"' not in serialized
