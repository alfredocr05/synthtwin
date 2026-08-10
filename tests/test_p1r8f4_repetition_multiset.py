"""P1-R8-F4: a declared identifier records the SHAPE of its repetition.

Under profile version 2 a column of six rows holding one code four
times and two codes once each, and a column of six rows holding three
codes twice each, produced byte-identical profiles and byte-identical
summaries. Both recorded `n_present` 6 and `n_distinct` 3 and nothing
about multiplicity, so a generator reading the profile alone had to
pick one repetition pattern for both, and any grouped analysis on the
twin diverged from the real table.

The owner's decision publishes an anonymous count multiset:
`n_distinct_by_occurrences`, how many different values cover one row,
two rows, and so on. The two columns above become `{"1": 2, "4": 1}`
and `{"2": 3}`.

What is checked here:

* the reviewer's two tables now differ, in the document and in the
  summary, and each mapping is the one worked out by hand above;
* the key form -- numeric text, left-padded so that the document's
  sorted-key order is a numeric order and `"10"` cannot sort before
  `"2"`;
* the two arithmetic invariants that tie the mapping to counts the
  profile already published;
* the extremes: every value different, every value the same, one row,
  a column of blanks, and a declared column whose every cell is a
  spelling meaning "no value" (the empty-column rule runs before the
  declaration, so that column has no mapping at all);
* that no source spelling reaches the COMPLETE serialized document or
  the complete summary, in any of those cases.

The mappings asserted here are worked out by hand from the input, so
this file is an oracle for the field and not a recording of what the
code happened to produce.
"""

import json
import pathlib

import fixtures
from synthtwin import profile, reading, summary, taxonomy

SETTINGS = taxonomy.Settings()

KEY = "n_distinct_by_occurrences"

# Three neutral codes of equal length, so that nothing but the pattern
# of repetition can tell the two tables below apart.
FIRST = "AX01"
SECOND = "BY02"
THIRD = "CZ03"

# The reviewer's pair, over the same six rows and the same three codes.
FOUR_ONE_ONE = [FIRST, FIRST, FIRST, FIRST, SECOND, THIRD]
TWO_TWO_TWO = [FIRST, FIRST, SECOND, SECOND, THIRD, THIRD]


def describe(
    values: list[str], settings: taxonomy.Settings = SETTINGS
) -> taxonomy.ColumnProfile:
    """One declared-identifier column, described on its own."""
    return taxonomy.profile_column(
        "code", 1, values, len(values), settings, True
    )


def outputs(
    folder: pathlib.Path,
    values: list[str],
    name: str = "t.csv",
    settings: taxonomy.Settings = SETTINGS,
) -> "tuple[dict, str, str]":
    """Both published artifacts for a table whose first column is declared.

    The second column is ordinary and is there only so the table is an
    unremarkable two-column file; nothing is asserted about it.
    """
    rows = [[value, str(index)] for index, value in enumerate(values)]
    text = fixtures.rows_to_csv(["code", "n"], rows)
    table = reading.read_table(str(fixtures.write(folder, name, text)))
    document = profile.build_document(table, settings, ["code"])
    return (
        document,
        profile.serialize(document),
        summary.render(document, "read as UTF-8."),
    )


def code_block(document: dict) -> dict:
    """The declared column's entry in a document built by `outputs`."""
    for column in document["columns"]:
        if column["name"] == "code":
            return column
    raise AssertionError("the declared column is missing from the document")


# -- the regression the review item names ------------------------------


def test_the_two_reviewer_tables_no_longer_serialize_the_same(
    tmp_path: pathlib.Path,
) -> None:
    _first, first_text, first_summary = outputs(
        tmp_path, FOUR_ONE_ONE, "a.csv"
    )
    _second, second_text, second_summary = outputs(
        tmp_path, TWO_TWO_TWO, "b.csv"
    )
    assert first_text != second_text, (
        "two declared columns with different repetition patterns must "
        "not produce the same profile: a generator reading the profile "
        "alone cannot then reproduce either"
    )
    assert first_summary != second_summary


def test_the_counts_that_used_to_be_the_whole_story_are_still_equal(
    tmp_path: pathlib.Path,
) -> None:
    # The premise of the item: everything ELSE about these two columns
    # agrees, which is why the profiles were identical.
    first = code_block(outputs(tmp_path, FOUR_ONE_ONE, "a.csv")[0])
    second = code_block(outputs(tmp_path, TWO_TWO_TWO, "b.csv")[0])
    for field in (
        "role",
        "n_present",
        "n_missing",
        "n_distinct",
        "n_distinct_folded",
        "min_length",
        "max_length",
    ):
        assert first[field] == second[field], field
    assert first[KEY] != second[KEY]


def test_each_mapping_is_the_one_worked_out_by_hand() -> None:
    # [4, 1, 1]: one code covers four rows, two codes cover one row each.
    assert describe(FOUR_ONE_ONE).details[KEY] == {"1": 2, "4": 1}
    # [2, 2, 2]: three codes cover two rows each.
    assert describe(TWO_TWO_TWO).details[KEY] == {"2": 3}


# -- the key form ------------------------------------------------------


def test_keys_are_numeric_text_read_back_as_row_counts() -> None:
    described = describe(FOUR_ONE_ONE)
    for key in described.details[KEY]:
        assert isinstance(key, str)
        assert int(key) >= 1


def test_ten_does_not_sort_before_two_in_the_written_document(
    tmp_path: pathlib.Path,
) -> None:
    """The trap the key form exists to avoid.

    The document is serialized with sorted keys, and text order puts
    `"10"` before `"2"`. Keys are therefore left-padded to a common
    width, so the order the file shows is the order of the numbers.
    """
    values = [FIRST] * 10 + [SECOND] * 2 + [THIRD] * 2
    document, text, _summary_text = outputs(tmp_path, values)
    shape = code_block(document)[KEY]
    assert shape == {"02": 2, "10": 1}
    # Read back as numbers, the keys of the written file ascend.
    written = json.loads(text)
    for column in written["columns"]:
        if column["name"] != "code":
            continue
        keys = [int(key) for key in column[KEY]]
        assert keys == sorted(keys)
        assert keys == [2, 10]
    block = json.dumps(shape, sort_keys=True)
    assert block.index('"02"') < block.index('"10"')


def test_a_single_width_mapping_is_written_without_padding() -> None:
    # Padding is to the width of the largest key in the SAME mapping, so
    # an ordinary column is written the plain way.
    assert describe([FIRST] * 9 + [SECOND]).details[KEY] == {"1": 1, "9": 1}


# -- the arithmetic the mapping must satisfy ---------------------------


def _entries(shape: dict) -> "tuple[int, int]":
    """How many different values the mapping accounts for, and how many rows."""
    values = 0
    rows = 0
    for key, count in shape.items():
        values = values + count
        rows = rows + int(key) * count
    return values, rows


def test_the_mapping_accounts_for_every_value_and_every_row() -> None:
    cases = [
        FOUR_ONE_ONE,
        TWO_TWO_TWO,
        [FIRST] * 10 + [SECOND] * 2 + [THIRD] * 2,
        [f"C{index:04d}" for index in range(37)],
        [FIRST] * 25,
        [FIRST],
    ]
    for values in cases:
        described = describe(values)
        n_values, n_rows = _entries(described.details[KEY])
        assert n_values == described.n_distinct, values[:3]
        assert n_rows == described.n_present, values[:3]


def test_the_mapping_counts_spellings_the_way_n_distinct_does() -> None:
    # Raw spellings, not case-folded ones. `n_distinct` is the raw count
    # and the two have to agree, or the invariant above cannot be
    # checked by a consumer at all; `n_distinct_folded` answers the
    # other question and is published beside it.
    described = describe(["Ab", "ab", "Ab", "AB"])
    assert described.n_distinct == 3
    assert described.n_distinct_folded == 1
    assert described.details[KEY] == {"1": 2, "2": 1}


def test_the_invariants_hold_for_many_neutral_columns() -> None:
    # Shapes nobody wrote a case for: every mixture of group sizes that
    # a small table can hold.
    for repeat in range(1, 8):
        for singles in range(8):
            values = [FIRST] * repeat + [
                f"S{index:03d}" for index in range(singles)
            ]
            if not values:
                continue
            described = describe(values)
            n_values, n_rows = _entries(described.details[KEY])
            assert n_values == described.n_distinct
            assert n_rows == described.n_present


# -- the extremes ------------------------------------------------------


def test_every_value_different() -> None:
    described = describe([f"D{index:04d}" for index in range(12)])
    assert described.details[KEY] == {"1": 12}
    # Forced by counts the profile has always carried, so this extreme
    # adds nothing that was not already published.
    assert described.n_distinct == described.n_present == 12


def test_every_value_the_same() -> None:
    described = describe([FIRST] * 12)
    assert described.details[KEY] == {"12": 1}
    assert described.n_distinct == 1


def test_a_single_row() -> None:
    described = describe([FIRST])
    assert described.details[KEY] == {"1": 1}
    assert described.n_present == 1


def test_a_column_of_blanks_has_no_mapping_at_all() -> None:
    # The empty-column rule runs before the declaration, so this column
    # is not given the identifier role and carries no details at all. A
    # consumer must treat the field as absent rather than as empty.
    described = describe(["", "", "", ""])
    assert described.role == taxonomy.ROLE_EMPTY
    assert KEY not in described.details


def test_a_declared_column_of_nothing_but_missing_spellings(
    tmp_path: pathlib.Path,
) -> None:
    """The declaration outlives the role it did not get.

    Every cell is a spelling the person named as meaning "no value", so
    the empty-column rule settles the column before any rule runs. It
    has no repetition mapping, and it still publishes no spelling.
    """
    token = "QZ8842"
    settings = taxonomy.Settings(declared_missing_values=(token,))
    document, text, summary_text = outputs(
        tmp_path, [token] * 8, settings=settings
    )
    block = code_block(document)
    assert block["role"] == taxonomy.ROLE_EMPTY
    assert KEY not in block
    assert token not in text
    assert token not in summary_text


# -- nothing of the column leaves, in any of those cases ---------------


def test_no_source_spelling_reaches_either_complete_output(
    tmp_path: pathlib.Path,
) -> None:
    """The whole document and the whole summary, searched for the input.

    Every case above goes through here, including the extremes, and the
    search is over the complete serialized document rather than over
    one block of it.
    """
    cases = {
        "four-one-one": FOUR_ONE_ONE,
        "two-two-two": TWO_TWO_TWO,
        "spanning-ten": [FIRST] * 10 + [SECOND] * 2 + [THIRD] * 2,
        "all-different": [f"E{index:04d}" for index in range(15)],
        "all-the-same": [FIRST] * 15,
        "one-row": [FIRST],
        "blanks": ["", "", "", ""],
    }
    index = 0
    for label in sorted(cases):
        index = index + 1
        values = cases[label]
        _document, text, summary_text = outputs(
            tmp_path, values, f"t{index}.csv"
        )
        for value in values:
            if not value:
                continue
            assert value not in text, f"{label}: {value} reached the profile"
            assert value not in summary_text, (
                f"{label}: {value} reached the summary"
            )


def test_the_mapping_survives_the_whole_block_filter() -> None:
    # The publication class is applied to the whole block, and a key it
    # does not know is replaced by `(withheld)`. This field is published
    # because it is named as carrying no value, not because the branch
    # that built it forgot to filter it.
    assert KEY in taxonomy.KEYS_THAT_CARRY_NO_VALUE
    described = describe(FOUR_ONE_ONE)
    assert described.details[KEY] != taxonomy.SUPPRESSED_LABEL
    for key in described.details:
        assert (
            key in taxonomy.KEYS_THAT_CARRY_NO_VALUE
            or described.details[key] == taxonomy.SUPPRESSED_LABEL
        ), key


def test_relabelling_the_values_does_not_move_the_mapping() -> None:
    # The property the privacy argument rests on: the mapping is a
    # function of the group SIZES alone. Rename every value and reorder
    # every row, and it does not move.
    original = describe(FOUR_ONE_ONE)
    renamed = describe(["ZZ99", "PP11", "ZZ99", "QQ22", "ZZ99", "ZZ99"])
    assert original.details[KEY] == renamed.details[KEY] == {"1": 2, "4": 1}


# -- what the person is told -------------------------------------------


def test_the_summary_says_what_was_and_was_not_recorded(
    tmp_path: pathlib.Path,
) -> None:
    _document, _text, summary_text = outputs(tmp_path, FOUR_ONE_ONE)
    assert "how often values repeat" in summary_text
    assert "recorded how OFTEN values repeat here, never which values" in (
        summary_text
    )
    assert "invent its own codes and repeat them the same" in summary_text
    assert "2 of the different values appear in one row only" in summary_text
    assert "the most repeated of them appears in 4 row(s)" in summary_text


def test_the_summary_and_the_document_cannot_disagree(
    tmp_path: pathlib.Path,
) -> None:
    document, _text, summary_text = outputs(tmp_path, TWO_TWO_TWO)
    assert code_block(document)[KEY] == {"2": 3}
    assert "0 of the different values appear in one row only" in summary_text
    assert "the most repeated of them appears in 2 row(s)" in summary_text


def test_a_column_that_publishes_no_values_says_so_and_means_it(
    tmp_path: pathlib.Path,
) -> None:
    # The publication note covers the WHOLE block, so it has to name the
    # repetition counts too; a note that promises less than the block
    # holds is how the next field slips past.
    document, _text, summary_text = outputs(tmp_path, FOUR_ONE_ONE)
    notes = [
        note["note"]
        for note in document["publication_notes"]
        if note["column"] == "code"
    ]
    assert notes
    assert any("how often they repeat" in note for note in notes)
    assert "how often they repeat" in summary_text


# -- the contract ------------------------------------------------------


def test_the_document_version_moved_with_the_new_key() -> None:
    # A key APPEARED, so a consumer reading a version 2 profile will not
    # find it. That is what this number exists to make explicit.
    assert profile.PROFILE_VERSION == 3


def test_the_same_table_still_produces_the_same_bytes(
    tmp_path: pathlib.Path,
) -> None:
    first = outputs(tmp_path, FOUR_ONE_ONE, "one.csv")[1]
    second = outputs(tmp_path, FOUR_ONE_ONE, "two.csv")[1]
    assert first == second
