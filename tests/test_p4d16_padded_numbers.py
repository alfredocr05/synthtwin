"""A number written with a leading zero says it may be a code.

Plan decision P4-D16, contract NF43.

WHAT WAS WRONG. A code column whose values are all digits is described
as arithmetic: its average, its spread and its ends go into the
profile, and the twin is invented numbers drawn from that ladder. That
is not a defect in any rule -- the numeric path does what it is
specified to do, and `--identifier` is the escape. What was missing is
anybody telling the person the escape was there.

TWO POINTERS ALREADY EXISTED AND NEITHER REACHED A CODE COLUMN. NF32
fires where every value differs, which a code column is not, because
codes repeat. NF35 fires where the cells wear an affix, which reaches
`D0120` and not `00100`. Between them a procedure code, a vaccine code
and a zip code fell through.

WHAT IS PINNED HERE: the remark fires where a numeric column holds a
padded cell; it stays silent on a column of plain measurements; it
names a COUNT and not a value; and it says in as many words that
nothing was assumed from it -- because the README's ratified rule is
that no rule may DECIDE the identifier role from a column's values, and
this one proposes rather than decides.
"""

import pathlib
import tempfile

import fixtures
from synthtwin import profile, reading, taxonomy


def _described(values: "list[str]", name: str = "code") -> dict:
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder, "thing.csv", fixtures.single_column_table(name, values)
    )
    return profile.build_document(
        reading.read_table(f"{table}"), taxonomy.Settings(), []
    )


def _remarks(document: dict) -> "list[str]":
    return document["columns"][0]["remarks"]


def _padded_remark(document: dict) -> "str | None":
    for remark in _remarks(document):
        if "written with a leading zero" in remark:
            return remark
    return None


CODES = (
    "00100", "00140", "01402", "11042", "20610", "36415", "43239",
    "45378", "64483", "66984", "70450", "71046", "80053", "81002",
    "85025", "90471", "93000", "96372", "99213", "99214", "99215",
)
WEIGHTS = (4, 3, 5, 6, 9, 40, 7, 6, 4, 3, 8, 12, 15, 11, 14, 10, 13, 9, 35, 28, 12)


def _code_column() -> "list[str]":
    values: list[str] = []
    for code, count in zip(CODES, WEIGHTS):
        values = values + [code] * count
    return values


# -- the case the decision is for -------------------------------------


def test_a_padded_code_column_is_told_about_identifier() -> None:
    """THE WHOLE OF WHAT THIS BUYS, on the column it was raised for."""
    document = _described(_code_column())
    block = document["columns"][0]
    assert block["role"] == "count"
    said = _padded_remark(document)
    assert said is not None, _remarks(document)
    assert "--identifier" in said
    assert "no value of this column will be published at all" in said


def test_the_remark_names_a_count_and_no_value() -> None:
    """A sentence of this format carries counts, never a cell.

    THE FIXTURE AVOIDS THE FORM'S OWN ILLUSTRATION on purpose. The
    sentence shows `00100` as an example of a padded number, exactly as
    NF26 shows `03/04/2024` and NF35 shows an affix shape -- it is part
    of the form's fixed text and not an argument, so a column that
    happens to hold that code would see it either way. Testing against
    a column that contains it proves nothing; testing against one that
    does not proves the sentence carries no cell of the table.
    """
    values = [f"0{700 + number % 90}" for number in range(120)] + [
        f"{4000 + number % 60}" for number in range(130)
    ]
    padded = len([value for value in values if value[0] == "0"])
    said = _padded_remark(_described(values))
    assert said is not None
    assert f"{padded} of this column's values" in said
    for value in set(values):
        if value == "00100":
            continue
        assert value not in said, value


def test_it_decides_nothing_and_says_so() -> None:
    """The README's ratified rule, kept in the sentence itself.

    No rule may DECIDE the identifier role from a column's values. This
    one proposes: the column is described as numbers either way, which
    is what keeps its distribution, and the role is unchanged.
    """
    document = _described(_code_column())
    assert document["columns"][0]["role"] == "count"
    said = _padded_remark(document)
    assert said is not None
    assert "nothing is assumed from that" in said
    assert "described as numbers either way" in said


# -- and where it must stay quiet --------------------------------------


def test_a_column_of_plain_measurements_says_nothing() -> None:
    """A count of visits is not a code and must not be nagged about."""
    values = [f"{1 + number % 9}" for number in range(250)]
    assert _padded_remark(_described(values, "visits")) is None


def test_a_column_of_decimals_says_nothing() -> None:
    """A leading zero before a POINT is how a fraction is written.

    `0.5` is not a padded code and never was: what makes a cell padded
    is a redundant zero in front of the figures of a whole number.
    """
    values = [f"0.{number % 90 + 10}" for number in range(250)]
    assert _padded_remark(_described(values, "rate")) is None


def test_one_padded_cell_is_enough_to_say_it() -> None:
    """Because one is enough for the column to be a code column.

    The floor governs what is PUBLISHED about a group, not whether a
    person is told how their own column was written -- and a column
    whose padding was too rare to name is still a column whose padding
    they should hear about.
    """
    values = ["00100"] + [f"{1000 + number}" for number in range(249)]
    said = _padded_remark(_described(values))
    assert said is not None
    assert "1 of this column's values" in said
