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
    """The comma remark in either of its two wordings.

    The form renders one sentence where the column settled nothing and
    another where it settled the question itself, so a filter matching
    only the first would miss exactly the case that matters most.
    """
    for remark in document["columns"][0]["remarks"]:
        if "comma inside the number" in remark:
            return remark
        if "thousands separator" in remark:
            return remark
    return None


# -- the reading itself -----------------------------------------------


def test_what_one_cell_settles_about_its_own_comma() -> None:
    """THE THREE ANSWERS, and the first read had only two.

    An earlier revision said flatly that no cell could settle the
    question, which was wrong in both directions and is the finding
    that rebuilt this rule. A point AFTER the comma settles it as a
    thousands separator, and so does a second comma -- so a US column
    was being told it might be a thousand times out when it was not. A
    group that is not three figures settles it the other way, and so
    does a first group longer than three, so `1000,000` proves a
    decimal comma and a European column that reaches a thousand
    carries its own proof.
    """
    for text in ("1,795", "0,814", "-1,795", "+1,795"):
        assert parsing.comma_reading(text) == parsing.COMMA_EITHER, text
        assert parsing.carries_a_group_comma(text), text
    for text in ("1,234.56", "1,234,567", "(1,234.50)"):
        assert parsing.comma_reading(text) == parsing.COMMA_GROUPED, text
        assert not parsing.carries_a_group_comma(text), text
    for text in ("12,5", "1,23", "1000,000", "22.008,28", "1,7955"):
        assert parsing.comma_reading(text) == parsing.COMMA_DECIMAL, text
        assert not parsing.carries_a_group_comma(text), text
    for text in ("814", "1.795", "", "abc"):
        assert parsing.comma_reading(text) == parsing.COMMA_NONE, text
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
    assert "write this column with a decimal point" in said


def test_a_column_that_settles_it_is_told_so_outright() -> None:
    """THE SHARPEST CASE, and the first revision was silent on it.

    A European column whose values reach a thousand carries its own
    proof: `1000,000` cannot be thousands-grouped, because a thousands
    group is exactly three figures. Such a column DECLINES to free text
    -- those cells are not numbers -- so the person was told "synthtwin
    could not settle what this column holds" with no mention of the
    reason sitting in every cell. The sentence now stops saying
    "nothing settles it" and says the file has settled it.
    """
    values = [f"{number / 1000:.3f}".replace(".", ",") for number in
              range(800, 3000, 9)]
    values = values + [f"{number}.000".replace(".", ",") for number in
                       range(1000, 1010)]
    document = _described(values)
    said = _comma_remark(document)
    assert said is not None, document["columns"][0]["remarks"]
    assert "THIS FILE WRITES THE DECIMAL POINT AS A COMMA" in said
    assert "cannot be read with the comma as a thousands separator" in said


def test_a_settled_thousands_column_is_not_warned() -> None:
    """The other half of the same correction.

    `1,234.56` is not ambiguous: the point settles the comma's role.
    Warning such a column that it might be a thousand times out is a
    false alarm, and a false alarm on a common shape is how a true one
    stops being read.
    """
    values = [
        f"{number // 1000},{number % 1000:03d}.50"
        for number in range(1000, 1240)
    ]
    document = _described(values)
    assert document["columns"][0]["role"] in ("count", "continuous")
    assert _comma_remark(document) is None


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
