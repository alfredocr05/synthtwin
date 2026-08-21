"""Profile version 4: the five additions, and what each one owes.

The contract is `docs/spec/profile-contract-v4.md`; the decisions behind
it are plan P2-D3 to P2-D5 and owner decisions 9, 10 and 11. Version 4
is version 3 plus five additions and no removals, so every test here
asks one of two questions: is the new fact PRESENT and closed, and does
the floor still govern what may be named.

THESE FIVE ARE STILL VERSION 5'S, and that is why this file stays.
`docs/spec/profile-contract-v5.md` carries version 4 by reference: every
rule it does not supersede is a rule of version 5 at its version 4
wording. None of the five is superseded, so every assertion below is an
assertion about the shipped format. What version 5 ADDS is
`tests/test_profile_version_5.py`.

Each addition exists because two different tables used to produce
identical bytes, and a description that cannot tell them apart cannot
be the only thing a twin is built from. Where that is the reason, the
test builds both tables and asserts they now differ, rather than
asserting only that a key is there.
"""

import json
import pathlib

import fixtures
from synthtwin import canonical, profile, reading, taxonomy

SETTINGS = taxonomy.Settings()
FLOOR = SETTINGS.small_cell_floor


def describe(
    values: "list[str]", declared: bool = False
) -> taxonomy.ColumnProfile:
    """One column, described by the taxonomy exactly as a run would."""
    return taxonomy.profile_column(
        "value", 1, values, len(values), SETTINGS, declared
    )


def document_for(
    tmp_path: pathlib.Path,
    values: "list[str]",
    declared: "list[str] | None" = None,
) -> "dict[str, object]":
    """A whole one-column profile, through the reader and the builder."""
    text = fixtures.single_column_table("value", values)
    table = reading.read_table(str(fixtures.write(tmp_path, "t.csv", text)))
    return profile.build_document(table, SETTINGS, declared or [])


# -- 1. the three axes (plan P2-D3) -----------------------------------


def test_every_role_has_axes_and_they_are_the_documented_ones() -> None:
    """The derivation is TOTAL over the roles, and it is the rule table.

    An axis a column sometimes lacks is an axis nothing can dispatch on,
    so the mapping is checked against the role tuple itself rather than
    against a list somebody kept in step by hand.
    """
    assert sorted(taxonomy.ROLE_AXES) == sorted(taxonomy.ROLES)
    assert taxonomy.axes_of(taxonomy.ROLE_EMPTY, False) == (
        "unknown",
        "empty",
        "data",
    )
    assert taxonomy.axes_of(taxonomy.ROLE_UNREPRESENTABLE, False) == (
        "numeric",
        "unrepresentable",
        "data",
    )
    assert taxonomy.axes_of(taxonomy.ROLE_IDENTIFIER, True) == (
        "code",
        "ok",
        "identifier",
    )
    assert taxonomy.axes_of(taxonomy.ROLE_TEXT, False) == (
        "text",
        "ok",
        "data",
    )
    # The six roles that name their own shape.
    for role in (
        taxonomy.ROLE_CONSTANT,
        taxonomy.ROLE_BINARY,
        taxonomy.ROLE_DATETIME,
        taxonomy.ROLE_COUNT,
        taxonomy.ROLE_CONTINUOUS,
        taxonomy.ROLE_CATEGORICAL,
    ):
        assert taxonomy.axes_of(role, False) == (role, "ok", "data")


def test_every_column_of_every_role_carries_all_three_axes(
    tmp_path: pathlib.Path,
) -> None:
    table = reading.read_table(
        str(fixtures.write(tmp_path, "t.csv", fixtures.every_role_table()))
    )
    document = profile.build_document(table, SETTINGS, [])
    for column in document["columns"]:
        assert column["statistical_type"]
        assert column["quality_state"] in ("ok", "empty", "unrepresentable")
        assert column["structural_role"] in ("data", "identifier")
        assert (
            column["statistical_type"],
            column["quality_state"],
        ) == taxonomy.ROLE_AXES[column["role"]]


def test_a_declared_column_of_nothing_is_still_a_key_column() -> None:
    """The one corner where the role and the declaration disagree.

    A declared column whose cells all mean "no value" is settled as an
    empty column before any other rule runs, so it never reaches the
    identifier role. Reading the role alone would say "an ordinary empty
    column" and lose the fact that its owner said it holds codes --
    which is exactly the fact that decides what its values may be used
    for.
    """
    described = describe([""] * 40, declared=True)
    assert described.role == taxonomy.ROLE_EMPTY
    assert described.structural_role == "identifier"
    assert described.statistical_type == "unknown"
    assert described.quality_state == "empty"


def test_the_axes_agree_with_the_declaration_that_produced_them(
    tmp_path: pathlib.Path,
) -> None:
    document = document_for(
        tmp_path, [f"R{index:04d}" for index in range(30)], ["value"]
    )
    column = document["columns"][0]
    assert column["structural_role"] == "identifier"
    assert document["settings"]["forced_identifiers"] == ["value"]
    plain = document_for(tmp_path, [f"R{index:04d}" for index in range(30)])
    assert plain["columns"][0]["structural_role"] == "data"
    assert plain["settings"]["forced_identifiers"] == []


# -- 2. repetition parity (plan P2-D4) ---------------------------------


def test_free_text_now_records_the_shape_of_its_repetition() -> None:
    """Two free-text columns that used to serialize identically.

    Both hold sixty rows and thirty different values; one holds each
    value twice, the other holds twenty-nine once and one value
    thirty-one times. Nothing else in either block can tell them apart.
    """
    words = fixtures.prose(30)
    twice = describe(words * 2)
    lopsided = describe(words + [words[0]] * 30)
    assert twice.role == taxonomy.ROLE_TEXT
    assert lopsided.role == taxonomy.ROLE_TEXT
    assert twice.n_present == lopsided.n_present == 60
    assert twice.n_distinct == lopsided.n_distinct == 30
    # The keys are padded to the width of the largest key in the SAME
    # mapping, which is what makes the document's sorted key order a
    # numeric one: written bare, "31" would sort before "01".
    assert twice.details["n_distinct_by_occurrences"] == {"2": 30}
    assert lopsided.details["n_distinct_by_occurrences"] == {
        "01": 29,
        "31": 1,
    }


def test_a_column_of_numbers_too_large_to_hold_records_it_too() -> None:
    described = describe(["1e999"] * 20 + ["2e999"] * 10)
    assert described.role == taxonomy.ROLE_UNREPRESENTABLE
    shape = described.details["n_distinct_by_occurrences"]
    assert shape == {"10": 1, "20": 1}
    # M1 and M2, the two sums every one of these mappings closes.
    assert sum(shape.values()) == described.n_distinct
    assert sum(int(key) * shape[key] for key in shape) == described.n_present


def test_the_repetition_mapping_publishes_no_value_of_the_column() -> None:
    """Both roles publish nothing, and this key does not change that."""
    text = canonical.serialize(
        {"a": describe(["1e999"] * 20 + ["2e999"] * 10).details}
    )
    assert "1e999" not in text
    assert "2e999" not in text


# -- 3. the relationship manifest (plan P2-D5) -------------------------


def test_the_manifest_reserves_eight_names_and_claims_none_of_them(
    tmp_path: pathlib.Path,
) -> None:
    document = document_for(tmp_path, [str(index) for index in range(40)])
    related = document["relationships"]
    assert sorted(related) == [
        "deterministic",
        "grain",
        "hierarchy",
        "keys",
        "missing_data_process",
        "statistical",
        "temporal",
        "validation_targets",
    ]
    assert sorted(related) == sorted(profile.RELATIONSHIP_SLOTS)
    for slot in related:
        assert related[slot] is None


# -- 4. label spellings (owner decisions 9 and 11) ---------------------


def test_a_published_label_carries_the_spellings_that_cleared_the_floor() -> None:
    """The contract's worked example, and the sum that closes it."""
    values = (
        ["North"] * 22 + ["north"] * 15 + ["NORTH", " north", "North "]
    )
    described = describe(values)
    assert described.role == taxonomy.ROLE_CONSTANT
    entry = described.details["levels"][0]
    assert entry["label"] == "north"
    assert entry["count"] == 40
    assert entry["variants"] == {"North": 22, "north": 15}
    assert entry["variants_withheld"] == {"1": 3}
    named = sum(entry["variants"].values())
    withheld = sum(
        int(key) * entry["variants_withheld"][key]
        for key in entry["variants_withheld"]
    )
    assert named + withheld == entry["count"]


def test_a_spelling_below_the_floor_is_never_named() -> None:
    values = ["North"] * 22 + ["north"] * 15 + ["NORTH", " north", "North "]
    text = canonical.serialize({"a": describe(values).details})
    assert '"NORTH"' not in text
    assert '" north"' not in text
    assert '"North "' not in text
    assert '"North"' in text


def test_a_withheld_label_carries_no_spellings_at_all() -> None:
    """A label the floor holds back has no entry to hang them on."""
    described = describe(["Alpha"] * 5 + ["beta"] * 30 + ["gamma"] * 30)
    assert described.role == taxonomy.ROLE_CATEGORICAL
    assert described.details["suppressed_levels"] == 1
    labels = [entry["label"] for entry in described.details["levels"]]
    assert "alpha" not in labels
    text = canonical.serialize({"a": described.details})
    assert "Alpha" not in text
    assert "alpha" not in text


def test_the_spellings_are_what_lets_a_folded_column_be_rebuilt() -> None:
    """Two columns that used to be one description (owner decision 9).

    Both publish two labels of thirty rows each. One column was written
    one way throughout; the other was written two ways. Without the
    spellings nothing said so, and anything built from the profile
    would have repeated where the second column never did.
    """
    plain = describe(["yes"] * 30 + ["no"] * 30)
    varied = describe(["yes"] * 15 + ["YES"] * 15 + ["no"] * 30)
    assert plain.details["levels"][0]["count"] == 30
    assert varied.details["levels"][0]["count"] == 30
    assert plain.n_distinct == 2
    assert varied.n_distinct == 3
    assert plain.details["levels"] != varied.details["levels"]


# -- 5. how the numbers were written (owner decision 10) ---------------


def test_the_three_families_no_longer_produce_one_description() -> None:
    """Whole numbers, decimals and exponents, all reading as zero.

    Every other published fact about these three columns is the same:
    three different spellings, thirty-six present values, every one a
    whole number, every one zero. A reader infers a different type from
    each, and the twin can only keep that type if the form is recorded.
    """
    whole = describe(["0"] * 12 + ["00"] * 12 + ["000"] * 12)
    decimals = describe(["0.0"] * 12 + ["00.0"] * 12 + ["000.0"] * 12)
    exponents = describe(["0e0"] * 12 + ["00e0"] * 12 + ["000e0"] * 12)
    for described in (whole, decimals, exponents):
        assert described.role == taxonomy.ROLE_COUNT
        assert described.n_present == 36
        assert described.n_distinct == 3
        assert described.details["integer_valued"] is True
    assert whole.details["numeric_styles"] == {"plain": 12, "leading_zero": 24}
    assert decimals.details["numeric_styles"] == {"decimal": 36}
    assert exponents.details["numeric_styles"] == {"exponent_lower": 36}


def test_a_form_used_by_too_few_cells_is_pooled_and_never_named() -> None:
    described = describe(["5"] * 30 + ["6"] * 30 + ["+7"] * 3)
    assert described.role == taxonomy.ROLE_COUNT
    styles = described.details["numeric_styles"]
    assert styles == {"plain": 60, taxonomy.SUPPRESSED_LABEL: 3}
    assert sum(styles.values()) == described.n_numeric


def test_every_form_is_one_form_and_the_ladder_decides_which() -> None:
    """The order is normative, so it is pinned value by value."""
    assert taxonomy.numeric_style("0") == "plain"
    assert taxonomy.numeric_style("00") == "leading_zero"
    assert taxonomy.numeric_style("-007") == "leading_zero"
    assert taxonomy.numeric_style("+5") == "leading_plus"
    assert taxonomy.numeric_style("0.0") == "decimal"
    # A cell carrying two marks is counted under the one that decides
    # the type a reader infers.
    assert taxonomy.numeric_style("+0.5") == "decimal"
    assert taxonomy.numeric_style("1e5") == "exponent_lower"
    assert taxonomy.numeric_style("1E5") == "exponent_upper"
    assert taxonomy.numeric_style("1.0E5") == "exponent_upper"
    # Brackets and thousands separators are not forms of their own: the
    # digits inside them decide.
    assert taxonomy.numeric_style("(5)") == "plain"
    assert taxonomy.numeric_style("(05)") == "leading_zero"
    assert taxonomy.numeric_style("1,234") == "plain"
    assert taxonomy.numeric_style("  42  ") == "plain"


def test_the_forms_count_the_cells_the_statistics_could_use() -> None:
    """Out-of-range cells have forms these six cannot express.

    A number too large for this format to hold is written by a rule of
    its own, so counting it here would oblige a twin to write a form
    these six cannot say. The counted population is therefore the cells
    that read as numbers this format holds -- one fewer than the cells
    present, in this column.
    """
    described = describe(["1"] * 100 + ["2"] * 99 + ["1e999"])
    assert described.role == taxonomy.ROLE_COUNT
    assert described.n_present == 200
    assert described.n_out_of_range == 1
    assert described.n_numeric == 199
    assert described.details["numeric_styles"] == {"plain": 199}


# -- the document as a whole -------------------------------------------


def test_the_version_number_moved_with_the_additions(
    tmp_path: pathlib.Path,
) -> None:
    document = document_for(tmp_path, [str(index) for index in range(40)])
    # The number moved AGAIN with version 5's three additions, and it is
    # asserted exactly rather than as "at least four": a version number
    # that could drift upward without a test moving is a version number
    # nothing pins. What this test is about is that the five additions
    # above arrived with a number of their own, and they did.
    assert profile.PROFILE_VERSION == 5
    assert document["profile_version"] == 5


def test_the_document_still_serializes_to_the_same_bytes_twice(
    tmp_path: pathlib.Path,
) -> None:
    values = ["North"] * 22 + ["north"] * 15 + ["NORTH", " north", "North "]
    first = canonical.serialize(document_for(tmp_path, values))
    second = canonical.serialize(document_for(tmp_path, values))
    assert first == second
    # And the canonical text is what json.loads reads back unchanged.
    assert canonical.serialize(json.loads(first)) == first
