"""The column-analysis redesign: one case per rule, one neighbour per rule.

Every test here is red against the pre-redesign taxonomy and green after
it. Each names the review item it closes.
"""

import json

import pytest

from synthtwin import parsing, profile, taxonomy

SETTINGS = taxonomy.Settings()


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


def whole_block(described: taxonomy.ColumnProfile) -> str:
    """Everything about a column that reaches a file, as one string."""
    return (
        json.dumps(profile._column_block(described), sort_keys=True)
        + " ".join(described.remarks)
        + " ".join(described.publication_notes)
    )


# -- ROLE ORDER (P1-R1-F8) -------------------------------------------


def test_a_mostly_numeric_column_keeps_its_distribution() -> None:
    # 0..97 plus the word "trace": 98 of 99 values are numbers, one short
    # of the "essentially all" line. It used to be called an identifier
    # and lose its distribution entirely.
    described = describe([str(index) for index in range(98)] + ["trace"])
    assert described.role == taxonomy.ROLE_COUNT
    assert described.details["percentiles"]["max"] == 97.0
    assert described.details["n_used_in_statistics"] == 98
    assert described.details["n_left_out_of_statistics"] == 1


def test_a_minority_numeric_column_is_not_described_as_numbers() -> None:
    # The neighbour on the other side of the majority line.
    values = [str(index) for index in range(40)] + [
        f"note {index} in words" for index in range(60)
    ]
    described = describe(values)
    assert described.role not in (taxonomy.ROLE_COUNT, taxonomy.ROLE_CONTINUOUS)


@pytest.mark.parametrize(
    "values",
    [
        [f"${index}.50" for index in range(60)],
        [f"{index}.5%" for index in range(60)],
        [f"{hour:02d}:{minute:02d}" for hour in range(10)
         for minute in range(0, 60, 10)],
    ],
)
def test_unsupported_measurement_syntax_is_not_called_an_identifier(
    values: list[str],
) -> None:
    # Currency, percentages and times of day are all-different single
    # words that synthtwin cannot parse. Calling them record numbers was
    # a false claim about their meaning.
    described = describe(values)
    assert described.role == taxonomy.ROLE_TEXT
    assert any("--identifier" in remark for remark in described.remarks)


def test_a_two_row_column_of_two_values_is_binary_not_an_identifier() -> None:
    described = describe(["T", "F"])
    assert described.role == taxonomy.ROLE_BINARY


def test_all_different_code_words_are_declined_and_declarable() -> None:
    """Corrected from `test_all_different_code_words_are_still_identifiers`.

    The old test pinned the inference that single words in the code
    alphabet, all different, ARE record numbers. `1mg` through `30mg` is
    that same shape, so the inference read a dose column as record
    numbers and destroyed its distribution; it is withdrawn rather than
    narrowed again (review item P1-R6-F8). What the old test really
    protected -- that such a column publishes nothing -- is unchanged,
    and the identifier role is exercised through the declared path.
    """
    values = [f"code{index}" for index in range(50)]
    described = describe(values)
    assert described.role == taxonomy.ROLE_TEXT
    assert described.n_distinct == 50
    assert "code7" not in whole_block(described)

    declared = describe(values, forced=True)
    assert declared.role == taxonomy.ROLE_IDENTIFIER
    assert "code7" not in whole_block(declared)


# -- FIXED-WIDTH CODES (P1-R1-F8) ------------------------------------


def test_zero_padded_codes_keep_their_padding_and_stay_discrete() -> None:
    described = describe(["00501", "02139", "52242"] * 20)
    assert described.role == taxonomy.ROLE_CATEGORICAL
    assert described.details["fixed_width_code"] is True
    labels = [level["label"] for level in described.details["levels"]]
    assert labels == ["00501", "02139", "52242"]
    assert "percentiles" not in described.details


def test_eight_digit_dates_are_not_mistaken_for_codes() -> None:
    described = describe([f"2024010{day}" for day in range(1, 10)] * 3)
    assert described.role == taxonomy.ROLE_DATETIME


def test_unpadded_same_width_digits_stay_a_quantity() -> None:
    # The stated limit: without a leading zero there is nothing in the
    # text that says the width is meaningful.
    described = describe(["52242", "10001", "90210"] * 20)
    assert described.role == taxonomy.ROLE_COUNT


# -- THE CATEGORICAL CEILING (P1-R1-F8) ------------------------------


def test_the_role_does_not_change_when_the_table_is_subsampled() -> None:
    labels = [f"label{index}" for index in range(9)]
    short = describe((labels * 6)[:50])
    long = describe((labels * 12)[:100])
    assert short.role == long.role == taxonomy.ROLE_CATEGORICAL
    assert short.n_distinct == long.n_distinct == 9


def test_more_labels_than_the_cap_keep_their_distribution() -> None:
    values: list[str] = []
    for index in range(1001):
        values = values + [f"label{index:04d}"] * 20
    described = describe(values)
    assert described.role == taxonomy.ROLE_CATEGORICAL
    assert described.n_distinct == 1001
    assert len(described.details["levels"]) == 1000
    assert described.details["levels_beyond_cap"] == 1
    assert described.details["rows_beyond_cap"] == 20


def test_values_that_hardly_repeat_are_not_a_set_of_categories() -> None:
    described = describe([f"note {index}" for index in range(50)])
    assert described.role != taxonomy.ROLE_CATEGORICAL


# -- NO-REPRESENTABLE ROUTING (P1-R3-F3, P1-R4-F2, P1-R5-F2) ---------


def test_numbers_no_format_can_hold_get_their_own_outcome() -> None:
    described = describe([f"{index}e999" for index in range(1, 101)])
    assert described.role == taxonomy.ROLE_UNREPRESENTABLE
    assert described.n_out_of_range == 100
    assert described.details["n_whole"] == 100
    assert "length" not in described.details


def test_repeated_unrepresentable_spellings_are_never_published() -> None:
    described = describe(["1e999", "2e999", "3e999"] * 20)
    assert described.role == taxonomy.ROLE_UNREPRESENTABLE
    assert "1e999" not in whole_block(described)


def test_repeated_contradictory_spellings_are_never_published() -> None:
    described = describe(["(-5)"] * 100)
    assert described.role == taxonomy.ROLE_UNREPRESENTABLE
    assert described.n_contradictory == 100
    assert "(-5)" not in whole_block(described)


# -- SENTINELS (P1-R1-F7, P1-R4-F2, P1-R5-F2) ------------------------


def test_two_sentinel_conventions_do_not_mask_each_other() -> None:
    described = describe(["0"] * 60 + ["-999"] * 20 + ["9999"] * 20)
    assert described.role == taxonomy.ROLE_CONSTANT
    assert described.n_missing == 40
    verdicts = [entry["verdict"] for entry in described.sentinel_verdicts]
    assert verdicts == [taxonomy.VERDICT_MISSING, taxonomy.VERDICT_MISSING]


def test_a_candidate_is_judged_even_when_some_values_are_words() -> None:
    # 90 numbers, 10 words and one candidate. The old gate needed 99% of
    # the values to be representable numbers, so no verdict was reached
    # at all.
    values = [str(index) for index in range(1, 91)] + ["word"] * 10 + ["-999"]
    described = describe(values)
    assert described.n_missing == 1
    assert described.details["percentiles"]["min"] == 1.0


def test_unrepresentable_values_do_not_stop_a_sentinel_being_judged() -> None:
    # P1-R5-F2 scenario 1: three values no format can hold used to push
    # the representable count below the gate, so -999 survived and was
    # published as the column's minimum.
    values = (
        [str(index) for index in range(1, 197)]
        + ["-999", "1e999", "2e999", "3e999"]
    )
    described = describe(values)
    assert described.details["percentiles"]["min"] == 1.0
    assert described.n_missing == 1


def test_a_legitimate_text_code_can_be_kept(  ) -> None:
    values = ["north"] * 40 + ["south"] * 40 + ["NA"] * 40
    assert describe(values).role == taxonomy.ROLE_BINARY
    kept = describe(values, settings=taxonomy.Settings(kept_values=("NA",)))
    assert kept.role == taxonomy.ROLE_CATEGORICAL
    assert kept.n_present == 120
    assert kept.n_missing == 0


def test_a_spelling_can_be_declared_missing() -> None:
    values = ["north"] * 40 + ["south"] * 40 + ["unknown"] * 40
    declared = describe(
        values,
        settings=taxonomy.Settings(declared_missing_values=("unknown",)),
    )
    assert declared.n_missing == 40
    assert declared.missing_by_class[parsing.MISSING_DECLARED] == 40


def test_a_visible_sign_rules_out_a_column_of_counts() -> None:
    # P1-R5-F2 scenario 2: the accounting form of a negative number that
    # no format can hold.
    described = describe([str(index) for index in range(1, 100)] + ["(1e999)"])
    assert described.role == taxonomy.ROLE_CONTINUOUS
    assert described.details["n_negative"] == 1
    assert described.details["n_negative_unrepresentable"] == 1


def test_a_value_too_small_to_hold_is_not_a_whole_number() -> None:
    # P1-R5-F2 scenario 3.
    described = describe([str(index) for index in range(1, 100)] + ["1e-999"])
    assert described.role == taxonomy.ROLE_CONTINUOUS
    assert described.details["integer_valued"] is False


# -- SUPPRESSION (P1-R1-F10) -----------------------------------------


def test_a_forced_identifier_beats_every_automatic_role() -> None:
    described = describe(["amber-id"] * 11, forced=True)
    assert described.role == taxonomy.ROLE_IDENTIFIER
    assert "amber-id" not in whole_block(described)


def test_a_withheld_sentinel_is_not_named_in_the_output() -> None:
    described = describe(["0"] * 200 + ["-999"])
    assert described.role == taxonomy.ROLE_BINARY
    assert described.sentinel_verdicts == []
    assert described.n_sentinel_candidates_unpublished == 1
    assert "-999" not in whole_block(described)


def test_a_withholding_role_publishes_no_missing_spelling() -> None:
    values = (
        [f"a sentence number {index} in words" for index in range(50)]
        + ["-9.99e2"]
    )
    described = describe(
        values, settings=taxonomy.Settings(declared_missing_values=("-9.99e2",))
    )
    assert described.role == taxonomy.ROLE_TEXT
    assert described.missing_by_source == {}
    assert described.missing_by_class[parsing.MISSING_WITHHELD] == 1
    assert "-9.99e2" not in whole_block(described)


def test_a_binary_column_publishes_exactly_two_labels() -> None:
    described = describe(["yes"] * 60 + ["no"] * 59 + ["YES"] * 11)
    assert described.role == taxonomy.ROLE_BINARY
    assert len(described.details["levels"]) == 2
    assert described.details["levels"] == [
        {"label": "yes", "count": 71},
        {"label": "no", "count": 59},
    ]
    assert described.n_distinct == 3
    assert described.n_distinct_folded == 2


def test_a_lone_differently_cased_row_is_not_a_level_of_its_own() -> None:
    described = describe(["yes"] * 60 + ["no"] * 60 + ["YES"])
    assert described.details["suppressed_levels"] == 0
    assert "YES" not in whole_block(described)


# -- CONTRACT SUFFICIENCY (P1-R1-F9) ---------------------------------


def test_two_date_columns_with_opposite_shapes_differ_in_the_profile() -> None:
    early = ["2020-01-01"] * 49 + ["2020-06-15"] * 2 + ["2020-12-31"] * 49
    middle = ["2020-01-01"] + ["2020-06-15"] * 98 + ["2020-12-31"]
    first, second = describe(early), describe(middle)
    assert first.details["earliest"] == second.details["earliest"]
    assert first.details["latest"] == second.details["latest"]
    assert first.details["date_percentiles"] != second.details["date_percentiles"]


def test_two_suppressed_binary_splits_differ_in_the_profile() -> None:
    lopsided = describe(["a"] + ["b"] * 9)
    even = describe(["a"] * 5 + ["b"] * 5)
    assert lopsided.details["levels"] == even.details["levels"] == []
    assert lopsided.details["suppressed_level_counts"] == [1, 9]
    assert even.details["suppressed_level_counts"] == [5, 5]


def test_sub_second_precision_is_recorded() -> None:
    described = describe(
        [f"2024-01-02T10:00:0{index % 10}.{index:03d}" for index in range(30)]
    )
    assert described.details["time_precision"] == parsing.PRECISION_SUBSECOND
    assert described.details["subsecond_digits"] == 3


def test_whole_minute_datetimes_say_so() -> None:
    described = describe(
        [f"2024-01-02T10:{minute:02d}" for minute in range(30)]
    )
    assert described.details["time_precision"] == parsing.PRECISION_MINUTE


def test_offsets_are_counted_not_reduced_to_one_word() -> None:
    values = (
        [f"2024-01-02T10:{minute:02d}:00+05:30" for minute in range(20)]
        + [f"2024-01-02T11:{minute:02d}:00Z" for minute in range(20)]
    )
    described = describe(values)
    assert described.role == taxonomy.ROLE_DATETIME
    assert described.details["utc_offsets"] == {"+05:30": 20, "Z": 20}


def test_datetimes_are_ordered_by_the_instant_they_name() -> None:
    # The review's own example: `+14:00` at half past midnight on the 1st
    # happened BEFORE `-12:00` at a quarter to midnight on the 31st,
    # although the local text sorts the other way. Sorting the text put
    # them in the wrong order.
    values = (
        [f"2024-01-01T00:{minute:02d}:00+14:00" for minute in range(20)]
        + [f"2023-12-31T23:{minute + 40:02d}:00-12:00" for minute in range(19)]
    )
    described = describe(values)
    assert described.role == taxonomy.ROLE_DATETIME
    # Two clocks wrote this column, so the profile publishes it on one.
    # Ordering by the instant and then writing out the LOCAL text made
    # `earliest` read later than `latest`, which is what a generator
    # comparing them as text would have to act on.
    assert described.details["datetimes_read_at"] == "utc"
    assert described.details["earliest"] == "2023-12-31 10:00:00"
    assert described.details["latest"] == "2024-01-01 11:58:00"
    assert described.details["earliest"] < described.details["latest"]
    assert described.details["earliest_utc_offset"] == "+14:00"
    assert described.details["latest_utc_offset"] == "-12:00"
    rungs = list(described.details["date_percentiles"].values())
    assert rungs == sorted(rungs)


@pytest.mark.parametrize("offset", ["+99:99", "+24:60", "-15:00"])
def test_an_impossible_utc_offset_is_not_a_datetime(offset: str) -> None:
    assert parsing.parse_datetime(
        f"2024-01-02T10:00:00{offset}", "iso-datetime"
    ) is None


def test_a_real_utc_offset_still_parses() -> None:
    assert parsing.parse_datetime(
        "2024-01-02T10:00:00+05:30", "iso-datetime"
    ) == ("2024-01-02 10:00:00", "+05:30")


def test_the_count_left_out_of_the_statistics_is_a_number_not_prose() -> None:
    described = describe([str(index) for index in range(200)] + ["word"])
    assert described.details["n_used_in_statistics"] == 200
    assert described.details["n_left_out_of_statistics"] == 1
    assert described.n_not_numeric == 1


# -- COUNTS PRESENT ON EVERY ROLE ------------------------------------


EVERY_ROLE = {
    taxonomy.ROLE_EMPTY: ["", "NA"] * 20,
    taxonomy.ROLE_UNREPRESENTABLE: [f"{index}e999" for index in range(1, 51)],
    taxonomy.ROLE_CONSTANT: ["same"] * 30,
    taxonomy.ROLE_BINARY: ["yes", "no"] * 20,
    taxonomy.ROLE_DATETIME: [f"2024-01-{day:02d}" for day in range(1, 29)],
    taxonomy.ROLE_COUNT: [str(index) for index in range(60)],
    taxonomy.ROLE_CONTINUOUS: [f"{index}.5" for index in range(60)],
    taxonomy.ROLE_CATEGORICAL: ["a"] * 40 + ["b"] * 40 + ["c"] * 40,
    taxonomy.ROLE_IDENTIFIER: [f"code{index}" for index in range(50)],
    taxonomy.ROLE_TEXT: [f"a sentence number {i} here" for i in range(50)],
}

# The one role no column reaches by itself. Its fixture is profiled with
# the column DECLARED, because that is the only way the role happens at
# all since review item P1-R6-F8 -- and it must still carry every
# universal count, which is what this battery is for.
DECLARED_ROLES = (taxonomy.ROLE_IDENTIFIER,)


def described_as(role: str) -> taxonomy.ColumnProfile:
    """The fixture for ``role``, profiled the way that role is reached."""
    return describe(EVERY_ROLE[role], forced=role in DECLARED_ROLES)


@pytest.mark.parametrize("role", sorted(EVERY_ROLE))
def test_every_universal_count_is_present_on_every_role(role: str) -> None:
    described = described_as(role)
    assert described.role == role, "the fixture must exercise the named role"
    block = profile._column_block(described)
    for key in (
        "missing_by_class",
        "missing_by_source",
        "n_numeric",
        "n_out_of_range",
        "n_contradictory",
        "n_not_numeric",
        "n_distinct",
        "n_distinct_folded",
        "sentinel_verdicts",
        "n_sentinel_candidates_unpublished",
    ):
        assert key in block, f"{key} is missing from role {role}"


@pytest.mark.parametrize("role", sorted(EVERY_ROLE))
def test_the_counts_reconcile_on_every_role(role: str) -> None:
    described = described_as(role)
    assert (
        described.n_numeric
        + described.n_out_of_range
        + described.n_contradictory
        + described.n_not_numeric
        == described.n_present
    )
    assert sum(described.missing_by_class.values()) == described.n_missing
    assert (
        described.n_present + described.n_missing
        == len(EVERY_ROLE[role])
    )


@pytest.mark.parametrize("role", sorted(EVERY_ROLE))
def test_every_role_belongs_to_exactly_one_publication_class(
    role: str,
) -> None:
    classes = [
        role in taxonomy.ROLES_PUBLISHING_LABELS,
        role in taxonomy.ROLES_PUBLISHING_RANGES,
        role in taxonomy.ROLES_PUBLISHING_NOTHING,
        role == taxonomy.ROLE_EMPTY,
    ]
    assert len([found for found in classes if found]) == 1
