"""Dotted dates and two-figure years are read as dates.

Plan decision P4-D8, its second and third families.

`17.03.2024` and `03/17/24` are two more shapes a spreadsheet writes
constantly, and this tool read both as free text -- so the column lost
its ends, its ladder and every distribution over time, and its twin held
invented strings that no date code could run against.

BOTH FAMILIES CARRY THE SAME AMBIGUITY THE SLASHED PAIR DOES, and they
are read by the same machinery rather than a rule of their own: the
column's own evidence first, then `--day-first`, then the ratified
default. What is new is the CENTURY: a two-figure year does not say
which hundred years it belongs to, so the pivot is fixed, stated, and
carried in the column's remarks wherever it is used.

The twin still writes ISO. That is owner decision 5 and residual
R-P2-7, unchanged here.
"""

import datetime
import pathlib
import tempfile

import fixtures
from synthtwin import (
    contract,
    generation,
    parsing,
    profile,
    reading,
    rendering,
    taxonomy,
    validation,
)

DAYS = [
    datetime.date(2024, 1, 1) + datetime.timedelta(days=step)
    for step in range(240)
]

# Every field at or below twelve, so BOTH readings parse every cell and
# the column settles nothing on its own.
AMBIGUOUS = [(month, day) for month in range(1, 13) for day in range(1, 13)]


def _described(
    values: "list[str]", settings: "taxonomy.Settings | None" = None
) -> "tuple[dict, contract.Profile, pathlib.Path]":
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder, "thing.csv", fixtures.single_column_table("thing", values)
    )
    document = profile.build_document(
        reading.read_table(f"{table}"), settings or taxonomy.Settings(), []
    )
    written = fixtures.write_profile(folder, "thing.json", document)
    return document, contract.load_profile(f"{written}"), folder


# -- the readings -----------------------------------------------------


def test_each_shape_reads_under_the_member_that_owns_it() -> None:
    """The dotted pair is PADDED and the two-figure pair is not.

    That asymmetry is deliberate and is the subject of
    `test_a_version_identifier_is_not_a_dotted_date` below: a version
    identifier is written `1.2.2024` and never `01.02.2024`, so the
    padding is what tells a dotted date from a version. Nothing writes
    a version with slashes and a two-figure year, so the two-figure
    pair keeps the unpadded fields C6-22 gives the slashed families.
    """
    for text, member in (
        ("17.03.2024", "dotted-day-first-date"),
        ("03.17.2024", "dotted-month-first-date"),
        ("07.03.2024", "dotted-day-first-date"),
        ("03/17/24", "two-digit-month-first-date"),
        ("17/03/24", "two-digit-day-first-date"),
        ("3/7/24", "two-digit-month-first-date"),
    ):
        assert parsing.parse_datetime(text, member) is not None, text


def test_the_families_do_not_reach_each_other_s_spellings() -> None:
    """The delimiter and the width of the year keep them apart."""
    assert parsing.parse_datetime(
        "03/17/2024", "two-digit-month-first-date"
    ) is None
    assert parsing.parse_datetime(
        "03/17/24", "month-first-date"
    ) is None
    assert parsing.parse_datetime(
        "17.03.24", "dotted-day-first-date"
    ) is None


def test_a_decimal_number_is_not_a_dotted_date() -> None:
    """One dot is a number; two are not.

    A column of prices must not become a column of dates, which is the
    whole reason the dotted grammar asks for two delimiters and a
    four-figure year rather than any text with a dot in it.
    """
    for text in ("17.03", "1.5", "17.03.", ".03.2024"):
        assert parsing.parse_datetime(
            text, "dotted-day-first-date"
        ) is None, text


# -- the century ------------------------------------------------------


def test_the_pivot_is_the_one_the_contract_fixes() -> None:
    """C6-D8P, at both sides of the line and at both ends."""
    assert parsing.TWO_DIGIT_YEAR_PIVOT == 68
    assert parsing.year_of_two_figures("00") == "2000"
    assert parsing.year_of_two_figures("68") == "2068"
    assert parsing.year_of_two_figures("69") == "1969"
    assert parsing.year_of_two_figures("99") == "1999"


def test_a_two_figure_year_reads_at_the_pivot_end_to_end() -> None:
    read = parsing.parse_datetime("03/17/69", "two-digit-month-first-date")
    assert read == ("1969-03-17", "")
    read = parsing.parse_datetime("03/17/68", "two-digit-month-first-date")
    assert read == ("2068-03-17", "")


def test_the_century_guess_is_always_said_out_loud() -> None:
    """WHICHEVER WAY THE MONTH AND DAY WERE SETTLED.

    The century is a guess even on a column whose own values settle the
    month and day beyond doubt, so the remark stands outside that
    chain. A column that said nothing here would be a column whose
    dates are a hundred years out with no warning at all.
    """
    # This column carries days above twelve, so its month-and-day
    # reading is EVIDENCE and not a guess -- and it still says so about
    # the century.
    document, _loaded, _folder = _described(
        [day.strftime("%m/%d/%y") for day in DAYS]
    )
    block = document["columns"][0]
    assert block["format"] == "two-digit-month-first-date"
    remarks = block["remarks"]
    assert any("two figures" in remark for remark in remarks), remarks
    assert any("1969" in remark for remark in remarks), remarks


def test_a_four_figure_year_says_nothing_about_a_century() -> None:
    """The remark belongs to the family that needs it and no other."""
    document, _loaded, _folder = _described(
        [day.strftime("%d.%m.%Y") for day in DAYS]
    )
    for remark in document["columns"][0]["remarks"]:
        assert "two figures" not in remark, remark


# -- the ambiguity, on the machinery that already existed -------------


def test_an_ambiguous_dotted_column_says_it_guessed() -> None:
    """The standing warning reaches the dotted pair now.

    Before this landing the sentence named slashes, so a person holding
    a dotted column read a true sentence as one about another column --
    and their own column, guessed at in exactly the same way, said
    nothing.
    """
    values = [f"{month:02d}.{day:02d}.2024" for month, day in AMBIGUOUS] * 2
    document, _loaded, _folder = _described(values)
    block = document["columns"][0]
    assert block["format"] == "dotted-month-first-date"
    assert any(
        "read month first" in remark for remark in block["remarks"]
    ), block["remarks"]


def test_the_declaration_turns_the_new_families_round() -> None:
    """`--day-first` reaches them, because they are in the pair list."""
    for pattern, month_first, day_first in (
        ("{month:02d}.{day:02d}.2024",
         "dotted-month-first-date", "dotted-day-first-date"),
        ("{month:02d}/{day:02d}/24",
         "two-digit-month-first-date", "two-digit-day-first-date"),
    ):
        values = [
            pattern.format(month=month, day=day) for month, day in AMBIGUOUS
        ] * 2
        plain, _loaded, _folder = _described(values)
        assert plain["columns"][0]["format"] == month_first, pattern
        turned, _also, _more = _described(
            values, taxonomy.Settings(day_first=True)
        )
        assert turned["columns"][0]["format"] == day_first, pattern


def test_the_columns_evidence_still_beats_the_declaration() -> None:
    """P4-D4.6's rule, unchanged, reaching two more families.

    A column holding a field above twelve has said which way it reads,
    and a declaration does not overrule what the values themselves
    settle.
    """
    values = [day.strftime("%m.%d.%Y") for day in DAYS]
    turned, _loaded, _folder = _described(
        values, taxonomy.Settings(day_first=True)
    )
    assert turned["columns"][0]["format"] == "dotted-month-first-date"


# -- the column, end to end -------------------------------------------


def test_both_families_become_date_columns() -> None:
    """THE CASE THE DECISION IS FOR. Every assertion was false before."""
    for pattern, member in (
        ("%d.%m.%Y", "dotted-day-first-date"),
        ("%m/%d/%y", "two-digit-month-first-date"),
    ):
        document, described, folder = _described(
            [day.strftime(pattern) for day in DAYS]
        )
        block = document["columns"][0]
        assert block["role"] == "datetime", pattern
        assert block["format"] == member, pattern
        assert block["earliest"] == "2024-01-01", pattern
        assert block["latest"] == "2024-08-27", pattern
        assert block["n_unparsed"] == 0, pattern

        twin = generation.generate(described, 3)
        written = fixtures.write(
            folder, "twin.csv", rendering.twin_csv(twin)
        )
        outcome = validation.measure(described, f"{written}")
        assert outcome.census.missed == 0, pattern


# -- what the adversarial read found ----------------------------------


def test_a_version_identifier_is_not_a_dotted_date() -> None:
    """THE DEFECT THE FIRST READ FOUND, and the reason the dotted pair
    is the one padded family.

    `1.2.2024` is how a version identifier is written and, character
    for character, how an unpadded dotted date would be written. With
    the unpadded grammar a `version` column of `1.1.2024` through
    `1.12.2024` cleared the date parse line, became a `datetime`
    column, published endpoints and a ladder over version numbers, and
    handed back a twin of ISO days. Nothing in the cell settles which
    it is; the PADDING does, well enough to be worth a rule.
    """
    for text in ("1.2.2024", "1.12.2024", "2.0.2024", "7.3.2024"):
        for member in ("dotted-day-first-date", "dotted-month-first-date"):
            assert parsing.parse_datetime(text, member) is None, text
    # ...and the padded shape, which is what the places that write
    # dotted dates actually write, still reads.
    assert parsing.parse_datetime(
        "17.03.2024", "dotted-day-first-date"
    ) == ("2024-03-17", "")


def test_a_column_of_versions_stays_a_column_of_versions() -> None:
    """The same finding, as the column a person would actually hold."""
    values = [
        f"{major}.{minor}.2024"
        for major in range(1, 4)
        for minor in range(1, 13)
    ] * 3
    document, _loaded, _folder = _described(values)
    assert document["columns"][0]["role"] != "datetime"


def test_the_pivot_remark_states_a_range_and_not_a_distance() -> None:
    """The consequence clause the first read corrected.

    An earlier wording said such a table is read forward "by a hundred
    years". That holds only for the century either side of the pivot:
    `68` meaning 1868 is read as 2068 and is two hundred years out, and
    `75` meaning 2075 is read as 1975 -- out in the other direction,
    which that wording did not warn about at all.
    """
    document, _loaded, _folder = _described(
        [day.strftime("%m/%d/%y") for day in DAYS]
    )
    remarks = document["columns"][0]["remarks"]
    said = [remark for remark in remarks if "two figures" in remark]
    assert len(said) == 1
    assert "1969 to 2068" in said[0]
    assert "hundred years" not in said[0]
