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
    assert "every statistic this profile publishes" in said
    assert "write this column with a decimal point" in said
    # ...AND IT DOES NOT NAME A STATISTIC THE COLUMN MIGHT NOT HAVE,
    # nor promise one is wrong. A symmetric column's mean is unchanged
    # by a factor of a thousand applied to every value, so "any average
    # this profile publishes is wrong" is not universally true. What is
    # true is that every statistic was computed from the wrong numbers.
    assert "are wrong with them" not in said


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
    assert "CONTAINS VALUES WRITTEN WITH A DECIMAL COMMA" in said
    assert "cannot be read with the comma as a thousands separator" in said
    # AND IT DOES NOT SPEAK FOR THE FILE. Two proof cells beside two
    # hundred legitimate thousands-grouped ones do not make the file
    # European, and declaring that it is would be the same false
    # confidence in the other direction.
    assert "THIS FILE" not in said


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


def test_a_comma_suffix_is_left_alone_because_it_cannot_be_told_apart() -> None:
    """WHAT WAS TRIED HERE, AND WHY IT WAS WITHDRAWN.

    `10,5` through `249,5` is European one-decimal data, and the affix
    rule reads it as the number 10 wearing the shared suffix `,5`. The
    cores are comma-free, so nothing sees the comma, and the column
    publishes statistics over 10 to 249 for values running 10.5 to
    249.5.

    A repair was written that declared such a suffix "not an affix" and
    counted every cell wearing it as proof of a decimal comma. The
    third adversarial read killed it, and was right to: `10,5` as a
    revision identifier with a genuine `,5` suffix is OBSERVATIONALLY
    IDENTICAL to `10,5` as a European number. The repair asserted one
    of them and told the person to rewrite their data with a decimal
    point, which on the other reading corrupts every identifier in the
    column. It also gave one column two contradictory remarks, because
    the core scan and the suffix scan disagreed by construction.

    Silence is not good here. It is better than a confident wrong
    answer that instructs somebody to damage their file, which is what
    the repair was. The gap is recorded as residual R-P4-33.
    """
    values = [f"{number},5" for number in range(10, 250)]
    document = _described(values)
    assert document["columns"][0]["role"] == "affixed_number"
    # No remark, and in particular NOT one asserting a decimal comma.
    assert _comma_remark(document) is None



def test_a_genuine_affixed_column_is_warned_too() -> None:
    """A currency column's numeric block is read over its CORES.

    `$1,795` is the same hazard as a bare `1,795`: the affix comes off
    and the core is read as a quantity. The first revision fired the
    remark only from the numeric verdict, so a column of money was
    silently a thousand times out.
    """
    values = [
        f"${number // 1000},{number % 1000:03d}"
        for number in range(1000, 1240)
    ]
    document = _described(values, "amount")
    assert document["columns"][0]["role"] == "affixed_number"
    said = _comma_remark(document)
    assert said is not None, document["columns"][0]["remarks"]
    assert "could be read either way" in said


def test_a_continuous_column_is_warned_too() -> None:
    """The other numeric role, pinned separately from `count`.

    Both are served by one call, but a test that walks only `count`
    lets that call be narrowed to `count` and stay green.
    """
    values = [
        f"{number // 1000},{number % 1000:03d}"
        for number in range(1000, 1240)
    ] + ["0.5"] * 12
    document = _described(values)
    assert document["columns"][0]["role"] == "continuous"
    assert _comma_remark(document) is not None


def test_an_exponent_does_not_hide_the_comma() -> None:
    """`1,001e2` is a spelling the grammar admits.

    Reading the exponent as ordinary characters made the whole cell
    answer "no comma", so a column of them was neither read as numbers
    nor warned about.
    """
    assert parsing.comma_reading("1,001e2") == parsing.COMMA_EITHER
    assert parsing.comma_reading("1,23e2") == parsing.COMMA_DECIMAL
    assert parsing.comma_reading("1,001E+2") == parsing.COMMA_EITHER


def test_only_a_cell_trying_to_be_a_number_may_speak() -> None:
    """THE SHARPEST RISK IN THE SECOND COUNT, closed.

    The proof count is read over EVERY present cell rather than only
    over the numbers, because a cell that settles the question is
    usually not a number this format reads -- `1000,000` is the whole
    reason the count exists. That reach is also its danger: without a
    guard, `Hello.World,Foo` is a point before a comma and was read as
    PROOF of a decimal comma, so a column of names or addresses would
    have been told, in capital letters, that this file writes the
    decimal point as a comma.

    A cell is evidence about how NUMBERS are written only if it is
    trying to be a number. Anything carrying a character that is not a
    figure, a point or a comma says nothing at all.
    """
    for text in (
        "Smith, John",
        "Doe, J., MD",
        "Hello.World,Foo",
        "a,b,c",
        "1,5 mg",
        "Iowa City, IA 52242",
        "2024, March",
    ):
        assert parsing.comma_reading(text) == parsing.COMMA_NONE, text


def test_a_column_of_names_is_never_told_about_decimals() -> None:
    """The same guard, as the column a person would actually hold."""
    names = [f"Family{number}, Given{number % 40}" for number in range(240)]
    assert _comma_remark(_described(names, "patient_name")) is None
    addresses = [
        f"{number} Main St., Apt {number % 40}, Iowa City"
        for number in range(240)
    ]
    assert _comma_remark(_described(addresses, "address")) is None


def test_a_version_string_is_not_a_number_of_any_convention() -> None:
    """A cell of figures, points and commas is not therefore a number.

    `1.2.3,4` carries only the characters a European number carries,
    and its point before the comma read as PROOF of a decimal comma --
    so a column of software versions would have been told in capital
    letters that this file writes decimals with commas. What tells it
    from `1.234.567,89`, which IS a million and a bit written the
    German way, is the grouping: a thousands group is three figures.
    """
    for text in ("1.2.3,4", "2.3.4,5", "1.2.3.4,5", ".,", ","):
        assert parsing.comma_reading(text) == parsing.COMMA_NONE, text
    for text in ("1.234.567,89", "1.234,56", "22.008,28"):
        assert parsing.comma_reading(text) == parsing.COMMA_DECIMAL, text


def test_a_column_of_versions_is_never_told_about_decimals() -> None:
    """The same guard, as a column somebody would actually hold."""
    values = [
        f"{major}.{minor}.{patch},{patch}"
        for major in range(1, 4)
        for minor in range(1, 9)
        for patch in range(1, 11)
    ]
    assert _comma_remark(_described(values, "version")) is None


def test_a_column_carries_the_remark_at_most_once() -> None:
    """One column, one sentence about its commas.

    A repair that scanned both the cores and the affix gave one column
    two NF44 remarks that contradicted each other -- one saying nothing
    settled the question and the other saying the column settled it.
    The counts are built in one place now, and this asserts the
    property rather than trusting that they are.
    """
    for values in (
        [f"{number // 1000},{number % 1000:03d}" for number in
         range(1000, 1240)],
        [f"{number},5" for number in range(10, 250)],
        [f"${number // 1000},{number % 1000:03d}" for number in
         range(1000, 1240)],
    ):
        document = _described(values)
        found = [
            remark for remark in document["columns"][0]["remarks"]
            if "thousands separator" in remark
        ]
        assert len(found) <= 1, found


def test_the_counts_can_never_exceed_the_column() -> None:
    """A sentence saying "241 of this column's values" over 240 rows is
    one a reader stops believing, so the counts are guarded where they
    are built rather than trusted."""
    values = [f"{number // 1000},{number % 1000:03d}" for number in
              range(1000, 1240)]
    document = _described(values)
    block = document["columns"][0]
    said = _comma_remark(document)
    assert said is not None
    assert f"{block['n_present']} of this column's values" in said
