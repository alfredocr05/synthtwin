"""The long tail of labels, end to end and at every edge it names.

Phase 4's third new column type (plan P4-D5). A column past the
categorical ceiling that still holds repeated labels used to be free
text, which publishes nothing at all -- so a twin of it carried neither
the real repeated labels nor a counted tail.

WHAT IS PINNED HERE, and each of it is a rule the decision states
rather than a property somebody noticed:

- the rule fires past the ceiling and only where at least one folded
  level covers the detection line;
- the line is the publication floor or ELEVEN, whichever is larger, and
  the lower bound is what keeps the free-text promise floor-invariant:
  lowering the floor must not make a NEW column publish labels;
- raising the floor raises the line with it;
- the role sits last but one, so every rule that reads a column better
  still claims it first -- a column of clock times with a repeated time
  is a column of clock times;
- it publishes the five shared label keys and NOT `level_ceiling`,
  whose invariant a long tail breaks by definition; the ceiling it
  passed is in its evidence sentence instead;
- the loader refuses a document claiming the role with no level that
  reaches the line (LT1), and one claiming it for a column that is not
  past the categorical ceiling at all (LT2);
- and the twin is the categorical rule verbatim: published labels at
  their counts, invented neutral labels at the exact suppressed sizes.
"""

import copy
import pathlib
import tempfile

import pytest

import fixtures
from synthtwin import (
    contract,
    errors,
    generation,
    profile,
    reading,
    rendering,
    taxonomy,
    validation,
)


def _described(
    values: "list[str]", floor: int = 11
) -> "tuple[dict, contract.Profile, pathlib.Path]":
    """One single-column table, described and read back."""
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder, "thing.csv", fixtures.single_column_table("thing", values)
    )
    document = profile.build_document(
        reading.read_table(f"{table}"),
        taxonomy.Settings(small_cell_floor=floor),
        [],
    )
    written = fixtures.write_profile(folder, "thing.json", document)
    return document, contract.load_profile(f"{written}"), folder


def _tail(shared: "list[tuple[str, int]]", ones: int) -> "list[str]":
    """Repeated labels, then that many one-off sentences."""
    values: list[str] = []
    for label, count in shared:
        values = values + [label] * count
    return values + fixtures.prose(ones)


# -- the rule, and the line it is decided on --------------------------


def test_a_long_tail_is_read_as_labels() -> None:
    """Past the ceiling, with levels worth publishing."""
    document, described, _folder = _described(
        _tail([("common", 40), ("also common", 30)], 230)
    )
    block = document["columns"][0]
    assert block["role"] == "long_tail_labels"
    # IT NAMES ITS OWN SHAPE (contract 14.1, C6-19). The axis table is
    # a bijection -- thirteen roles onto thirteen types -- so a role
    # sharing another's type would break the totality the axes exist
    # for. What it publishes is still the label family's four keys.
    assert block["statistical_type"] == "long_tail_labels"
    assert [level["label"] for level in block["levels"]] == [
        "common",
        "also common",
    ]
    assert block["suppressed_levels"] == 230
    assert block["suppressed_rows"] == 230
    assert isinstance(described.columns[0].facts, contract.LabelFacts)


def test_the_line_is_eleven_and_not_ten() -> None:
    """One row either side of it, and the role turns over."""
    over, _loaded, _folder = _described(_tail([("repeated", 11)], 289))
    assert over["columns"][0]["role"] == "long_tail_labels"
    under, _loaded_two, _folder_two = _described(
        _tail([("repeated", 10)], 290)
    )
    assert under["columns"][0]["role"] == "free_text"


def test_a_lowered_floor_makes_no_new_column_publish_labels() -> None:
    """THE WHOLE REASON THE LINE HAS A LOWER BOUND OF ITS OWN.

    The free-text promise -- publishes no value at all -- has to hold
    at every floor, or a person lowering the floor for one column would
    silently make a column of names start naming them. A ten-row level
    is under the line at floor eleven and stays under it at floor one.
    """
    values = _tail([("repeated", 10)], 290)
    for floor in (1, 2, 5, 10, 11):
        document, _loaded, _folder = _described(values, floor)
        assert document["columns"][0]["role"] == "free_text", floor


def test_a_column_of_names_stays_free_text_at_every_floor() -> None:
    """The case the promise is about: nothing repeats at all."""
    values = fixtures.prose(300)
    for floor in (1, 5, 11, 20):
        document, _loaded, _folder = _described(values, floor)
        assert document["columns"][0]["role"] == "free_text", floor


def test_raising_the_floor_raises_the_line_with_it() -> None:
    """A level nobody may name is not a level this rule can count."""
    values = _tail([("repeated", 15)], 285)
    document, _loaded, _folder = _described(values, 11)
    assert document["columns"][0]["role"] == "long_tail_labels"
    higher, _loaded_two, _folder_two = _described(values, 20)
    assert higher["columns"][0]["role"] == "free_text"


def test_the_published_set_widens_with_a_lowered_floor() -> None:
    """...for a column the line already admits, exactly as a set of
    categories does at floor one today."""
    values = _tail([("repeated", 11), ("rare", 3)], 286)
    document, _loaded, _folder = _described(values, 11)
    assert [level["label"] for level in document["columns"][0]["levels"]] == [
        "repeated"
    ]
    lower, _loaded_two, _folder_two = _described(values, 3)
    published = [level["label"] for level in lower["columns"][0]["levels"]]
    assert "repeated" in published
    assert "rare" in published


# -- where the rule sits --------------------------------------------


def test_a_rule_that_reads_the_column_better_still_claims_it() -> None:
    """It sits LAST BUT ONE, and that is the whole of its safety."""
    clocks = [f"{7 + place % 12:02d}:{place % 60:02d}" for place in range(200)]
    document, _loaded, _folder = _described(clocks + ["09:00"] * 40)
    assert document["columns"][0]["role"] == "time_of_day"

    dates = [
        f"2024-{1 + place % 12:02d}-{1 + place % 28:02d}"
        for place in range(200)
    ]
    later, _loaded_two, _folder_two = _described(dates + ["2024-06-01"] * 40)
    assert later["columns"][0]["role"] == "datetime"

    numbers = [f"{place}" for place in range(200)] + ["7"] * 40
    third, _loaded_three, _folder_three = _described(numbers)
    assert third["columns"][0]["role"] in ("count", "continuous")


def test_a_set_of_categories_is_still_a_set_of_categories() -> None:
    """Under the ceiling the earlier rule claims the column."""
    document, _loaded, _folder = _described(
        ["north"] * 60 + ["south"] * 60 + ["east"] * 60 + ["west"] * 60
    )
    assert document["columns"][0]["role"] == "categorical"
    assert "level_ceiling" in document["columns"][0]


# -- what it publishes, and what it does not -------------------------


def test_it_publishes_the_four_label_keys_and_not_the_ceiling() -> None:
    """`level_ceiling` is categorical's own, and a long tail breaks it.

    The format has no optional keys, so the ceiling this column PASSED
    is recorded in its evidence sentence rather than in a key whose
    invariant it could not keep.
    """
    document, _loaded, _folder = _described(
        _tail([("common", 40), ("also common", 30)], 230)
    )
    block = document["columns"][0]
    for key in (
        "levels",
        "suppressed_levels",
        "suppressed_rows",
        "suppressed_level_counts",
    ):
        assert key in block
    assert "level_ceiling" not in block
    assert "a set of categories may have" in block["detection_evidence"]


def test_the_evidence_names_the_line_and_how_many_cleared_it() -> None:
    """A reader can check the rule fired for the reason it states."""
    document, _loaded, _folder = _described(
        _tail([("common", 40), ("also common", 30)], 230)
    )
    said = document["columns"][0]["detection_evidence"]
    assert "2 level(s) of it are shared by at least 11 rows each" in said


# -- the document: what the loader refuses ---------------------------


def test_a_document_claiming_the_role_without_a_covering_level() -> None:
    """LT1, and it is the rule that makes the role's own line checkable.

    At a lowered floor a column may publish levels of ten, none of
    which reaches the line -- which is a document claiming a role its
    own numbers say the rule would not have given it.
    """
    document, _loaded, folder = _described(
        _tail([("aaa", 10), ("bbb", 10)], 220), 10
    )
    assert document["columns"][0]["role"] == "free_text"
    forged = copy.deepcopy(document)
    block = forged["columns"][0]
    block["role"] = "long_tail_labels"
    block["statistical_type"] = "long_tail_labels"
    block["levels"] = [
        {
            "label": "aaa",
            "count": 10,
            "variants": {"aaa": 10},
            "variants_withheld": {},
        },
        {
            "label": "bbb",
            "count": 10,
            "variants": {"bbb": 10},
            "variants_withheld": {},
        },
    ]
    block["suppressed_levels"] = 220
    block["suppressed_rows"] = 220
    block["suppressed_level_counts"] = [1] * 220
    # The free-text keys go with the role that carried them: the
    # format has no optional keys, so a block claiming this role
    # carries the four label keys and nothing else its role does not
    # add.
    for key in list(block):
        if key in (
            "length",
            "words",
            "n_distinct_by_occurrences",
            "n_all_digits",
            "n_code_alphabet",
            "min_length",
            "max_length",
            "all_whole_numbers",
        ):
            del block[key]
    written = fixtures.write_profile(folder, "forged.json", forged)
    with pytest.raises(errors.ProfileError) as raised:
        contract.load_profile(f"{written}")
    assert "LT1" in f"{raised.value}"


# -- the twin ---------------------------------------------------------


def test_the_twin_carries_the_real_labels_and_a_counted_tail() -> None:
    """The categorical generation rule verbatim (plan P4-D5).

    Against today's filler, which carried neither.
    """
    _document, described, folder = _described(
        _tail([("common", 40), ("also common", 30)], 230)
    )
    twin = generation.generate(described, 3)
    cells = [cell for cell in twin.columns[0] if cell]
    counted: "dict[str, int]" = {}
    for cell in cells:
        counted[cell] = counted.get(cell, 0) + 1
    assert counted["common"] == 40
    assert counted["also common"] == 30
    assert len(counted) == 232

    written = fixtures.write(folder, "twin.csv", rendering.twin_csv(twin))
    outcome = validation.measure(described, f"{written}")
    missed = [
        check.subcheck
        for check in outcome.checks
        if check.verdict == validation.MISSED
    ]
    assert missed == []


def test_the_twin_reads_back_as_the_same_role() -> None:
    """A twin whose own description gives it another role would be a
    twin of a different column."""
    _document, described, folder = _described(
        _tail([("common", 40), ("also common", 30)], 230)
    )
    twin = generation.generate(described, 5)
    written = fixtures.write(folder, "twin.csv", rendering.twin_csv(twin))
    again = profile.build_document(
        reading.read_table(f"{written}"), taxonomy.Settings(), []
    )
    assert again["columns"][0]["role"] == "long_tail_labels"


def test_the_twin_is_a_fixed_function_of_the_description_and_seed() -> None:
    """Label columns draw no content words; the placement is seeded."""
    _document, described, _folder = _described(
        _tail([("common", 40), ("also common", 30)], 230)
    )
    first = generation.generate(described, 7)
    again = generation.generate(described, 7)
    assert first.columns == again.columns
    other = generation.generate(described, 8)
    assert other.columns != first.columns


# -- the disclosure page, which is where a person meets this ----------


def test_every_role_is_classified_by_the_disclosure_page() -> None:
    """A role in none of the three lists appears on the page NOWHERE.

    THIS IS THE CONTROL THAT WAS MISSING, and two shipped roles had
    already fallen through it: `time_of_day` and `affixed_number` were
    in no list at all, so the page a person reads BEFORE anything is
    written said nothing about a column of clock times, or about one
    whose numbers each wear a unit -- two of the three kinds of column
    this phase taught synthtwin to read.

    `empty` is the one role deliberately outside the three: a column
    with no values in it has nothing to disclose, and listing it under
    "no value at all" would put a column that never had one beside the
    columns that have values the profile withholds.
    """
    from synthtwin import summary

    classified = (
        set(summary._ROLES_WITH_LABELS)
        | set(summary._ROLES_WITHOUT_VALUES)
        | set(summary._ROLES_WITH_RANGES)
    )
    missing = sorted(set(taxonomy.ROLES) - classified - {taxonomy.ROLE_EMPTY})
    assert missing == [], (
        f"these roles are in no disclosure list, so the summary page "
        f"says nothing at all about a column of them: {missing}"
    )


def test_the_page_names_a_long_tail_among_the_label_columns() -> None:
    """P4-D5: the summary lists them BEFORE anything is written."""
    from synthtwin import summary

    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder,
        "thing.csv",
        fixtures.single_column_table(
            "thing", _tail([("common", 40), ("also common", 30)], 230)
        ),
    )
    document = profile.build_document(
        reading.read_table(f"{table}"), taxonomy.Settings(), []
    )
    page = summary.render(document, "")
    assert "Real labels you will see in the profile" in page
    at = page.index("Real labels you will see in the profile")
    tail = page[at : at + 400]
    assert "thing" in tail


def test_the_page_names_the_shared_text_of_an_affixed_column() -> None:
    """The one spelling a ranges role publishes, said in its own words."""
    from synthtwin import summary

    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder,
        "dose.csv",
        fixtures.single_column_table(
            "dose", [f"{10 + place % 90} mg" for place in range(120)]
        ),
    )
    document = profile.build_document(
        reading.read_table(f"{table}"), taxonomy.Settings(), []
    )
    assert document["columns"][0]["role"] == "affixed_number"
    page = summary.render(document, "")
    assert "A piece of text your cells share" in page
