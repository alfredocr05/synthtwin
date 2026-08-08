"""Red against the proposed redesign, green after the corrections.

Each test names the defect it pins. Put this file at
tests/test_column_analysis_review.py, or fold the tests into
tests/test_column_analysis.py.
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


@pytest.mark.parametrize("stragglers", [1, 2, 3, 5, 20])
def test_a_repeating_numeric_column_keeps_its_distribution(
    stragglers: int,
) -> None:
    """RULE 8 sits between the two numeric rules.

    One hundred ages that REPEAT, plus a few cells that do not read as
    numbers. RULE 7 wants 99 per cent, so more than one straggler drops
    the column past it; without a guard RULE 8 then claims it, every one
    of its 23 levels falls below the small-cell floor, and the profile
    carries no percentile, no mean, no minimum and no label at all.
    """
    ages = [str(20 + (index % 21)) for index in range(100)]
    described = describe(ages + [f"refused{n}" for n in range(stragglers)])
    assert described.role == taxonomy.ROLE_COUNT
    assert described.details["percentiles"]["min"] == 20.0
    assert described.details["percentiles"]["max"] == 40.0
    assert described.details["n_used_in_statistics"] == 100
    assert described.details["n_left_out_of_statistics"] == stragglers


def test_a_small_set_of_numeric_codes_is_still_a_set_of_categories() -> None:
    """The neighbour on the other side of the new guard."""
    described = describe(["1", "2", "3"] * 30 + ["unknown"] * 5)
    assert described.role == taxonomy.ROLE_CATEGORICAL
    assert [level["label"] for level in described.details["levels"]] == [
        "1", "2", "3",
    ]


def test_the_numeric_category_guard_reads_the_column_not_the_table() -> None:
    """The guard must not reintroduce the subsample flip."""
    codes = [str(index) for index in range(6)]
    short = describe((codes * 10)[:50] + ["unknown"] * 2)
    long = describe((codes * 20)[:100] + ["unknown"] * 4)
    assert short.role == long.role == taxonomy.ROLE_CATEGORICAL


# -- F2: a percentile ladder must rest on the cells it is computed from


def test_a_ladder_is_never_built_from_a_handful_of_cells() -> None:
    """`numeric_looking` counts cells that contribute nothing to a rung.

    Fifty cells no format can hold, ONE real number and forty-nine
    notes clears the majority gate, so the column was described as a
    count whose eleven rungs were all one row's exact value.
    """
    values = (
        ["1e999"] * 50 + ["7"] + [f"note {index} here" for index in range(49)]
    )
    described = describe(values)
    assert described.role == taxonomy.ROLE_UNREPRESENTABLE
    assert "percentiles" not in described.details
    assert "7" not in whole_block(described).replace('"7"', "")


def test_the_unrepresentable_evidence_states_what_the_column_shows() -> None:
    values = ["1e999"] * 50 + [f"a note number {i} written out" for i in range(50)]
    described = describe(values)
    assert described.role == taxonomy.ROLE_UNREPRESENTABLE
    # "all 50 of the 100 values are written as numbers" was false.
    assert "all 50 of the 100" not in described.detection_evidence
    assert "50 of the 100 values are written as numbers" in (
        described.detection_evidence
    )


def test_a_majority_numeric_column_still_keeps_its_distribution() -> None:
    """The neighbour: enough representable numbers to describe."""
    described = describe(
        [str(index) for index in range(60)]
        + [f"note {index} here" for index in range(40)]
    )
    assert described.role == taxonomy.ROLE_COUNT
    assert described.details["n_used_in_statistics"] == 60


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


# -- F4: the fixed-width rule must read one text ----------------------


def test_one_stray_space_does_not_undo_the_fixed_width_rule() -> None:
    """Two predicates read the trimmed cell, one read the raw one."""
    described = describe([" 00501", "02139", "52242"] * 20)
    assert described.role == taxonomy.ROLE_CATEGORICAL
    assert described.details["fixed_width_code"] is True
    assert [level["label"] for level in described.details["levels"]] == [
        "00501", "02139", "52242",
    ]
    assert "percentiles" not in described.details


# -- F5: the free-text remark must not misdirect a measurement --------


@pytest.mark.parametrize("values", [
    [f"${index}.50" for index in range(60)],
    [f"{index}.5%" for index in range(60)],
])
def test_the_free_text_remark_names_both_readings(
    values: list[str],
) -> None:
    """Naming only --identifier tells a price column to withhold itself."""
    described = describe(values)
    assert described.role == taxonomy.ROLE_TEXT
    remark = " ".join(described.remarks)
    assert "--identifier" in remark
    assert "measurement" in remark
    assert "plain numbers" in remark
