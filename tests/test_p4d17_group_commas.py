"""A comma inside a number is a choice, and the column says so.

Plan decision P4-D17, contract NF44.

WHAT WAS WRONG, and it is the one place this tool could be wrong by a
FACTOR rather than by a rounding. A column of laboratory values written
the way most of the world writes them -- `1,795`, `0,814`, `2,706` --
was read as one thousand seven hundred and ninety-five, eight hundred
and fourteen, two thousand seven hundred and six. The description said
`role: count`, `integer_valued: true`, "whole numbers that count
things", and published a mean of 1830 for a column whose real mean is
1.83. The twin held `0814`. The quality report said nothing.

THE COLUMN CANNOT SETTLE IT. A thousands group is exactly three digits,
so `12,5` proves a decimal comma -- but a column written to three
decimals has every group exactly three digits long, and is
indistinguishable from a US column carrying thousands separators.
Evidence does not reach the dangerous case. So the reading stays a
CHOICE, and every column where the choice was made says so.
"""

import pathlib
import tempfile

import fixtures
from synthtwin import parsing, profile, reading, taxonomy


def _described(values: "list[str]", name: str = "value") -> dict:
    folder = pathlib.Path(tempfile.mkdtemp())
    rows = [[value, "x"] for value in values]
    table = fixtures.write(
        folder, "thing.csv", fixtures.rows_to_csv([name, "other"], rows)
    )
    return profile.build_document(
        reading.read_table(f"{table}"), taxonomy.Settings(), []
    )


def _comma_remark(document: dict) -> "str | None":
    for remark in document["columns"][0]["remarks"]:
        if "comma inside the number" in remark:
            return remark
    return None


# -- the reading itself -----------------------------------------------


def test_which_cells_read_as_a_number_only_through_a_comma() -> None:
    """The predicate the remark is counted from."""
    for text in ("1,795", "1,234.56", "0,814", "12,345", "(1,234.50)"):
        assert parsing.carries_a_group_comma(text), text
    # No comma at all, so no choice was made.
    for text in ("814", "1.795", "", "abc"):
        assert not parsing.carries_a_group_comma(text), text
    # A comma the thousands rule REFUSES: the cell is not a number, so
    # no choice was made about it either.
    for text in ("12,5", "1,23", "22.008,28"):
        assert not parsing.carries_a_group_comma(text), text


def test_the_dangerous_column_carries_no_evidence() -> None:
    """WHY THIS IS A REMARK AND NOT A RULE.

    Three decimals is what an INR, a creatinine or a currency amount is
    written to, and every group of a three-decimal European column is
    three digits long -- which is exactly what a thousands group looks
    like. There is nothing in the column to detect.
    """
    european = [f"{number / 1000:.3f}".replace(".", ",") for number in
                range(800, 3000, 9)]
    for cell in european:
        assert parsing.classify_number(cell) == parsing.NUMBER, cell
    # ...whereas one cell written to ONE decimal would have settled it,
    # which is why the finding is about the three-decimal case.
    assert parsing.classify_number("1,8") != parsing.NUMBER


# -- the column says so -----------------------------------------------


def test_a_comma_bearing_column_states_the_choice() -> None:
    """THE CASE THE DECISION IS FOR, end to end."""
    values = [f"{number / 1000:.3f}".replace(".", ",") for number in
              range(800, 3000, 9)]
    document = _described(values)
    block = document["columns"][0]
    assert block["role"] == "count"
    said = _comma_remark(document)
    assert said is not None, block["remarks"]
    assert f"{len(values)} of this column's values" in said


def test_the_sentence_states_the_size_of_the_error() -> None:
    """A hedged sentence is one a reader passes over.

    The error is a factor of a thousand and reaches every statistic the
    column publishes, so the sentence says the factor, says which way
    it went, and says what to do.
    """
    values = [f"{number / 1000:.3f}".replace(".", ",") for number in
              range(800, 3000, 9)]
    said = _comma_remark(_described(values))
    assert said is not None
    assert "thousand times its real size" in said
    assert "average" in said and "spread" in said
    assert "write them with a point instead" in said


def test_it_names_no_value_of_the_table() -> None:
    """A sentence of this format carries counts, never a cell."""
    values = [f"{number / 1000:.3f}".replace(".", ",") for number in
              range(800, 3000, 9)]
    said = _comma_remark(_described(values))
    assert said is not None
    for value in set(values):
        if value == "1,795":          # the form's own illustration
            continue
        assert value not in said, value


# -- and where it stays quiet -----------------------------------------


def test_a_column_with_no_comma_says_nothing() -> None:
    """Most columns. The remark must not become noise."""
    values = [f"{1000 + number}" for number in range(240)]
    assert _comma_remark(_described(values)) is None


def test_a_column_whose_commas_are_not_numbers_says_nothing() -> None:
    """No choice was made, because nothing was read as a number.

    `12,5` is refused by the thousands rule, so such a column is text
    and this sentence would be false of it.
    """
    values = [f"{number},5" for number in range(10, 250)]
    document = _described(values)
    assert document["columns"][0]["role"] != "count"
    assert _comma_remark(document) is None
