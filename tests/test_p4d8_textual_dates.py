"""Dates written with a month NAME are read as dates.

Plan decision P4-D8, first of its three families.

WHAT WAS WRONG. `17 Mar 2024`, `17-Mar-2024`, `Mar 17, 2024` and
`March 17, 2024` are four of the commonest ways a date is written into
a spreadsheet, and this tool read every one of them as free text. A
free-text column publishes no earliest, no latest, no ladder and no
distribution over time, so its twin holds invented strings and NOTHING
a person writes against a date runs on it -- not a difference in days,
not a window, not a sort, not a resample. The column was neither
handled by an appropriate type path nor declined with an explanation,
which is the whole of what principle 5 asks.

WHAT THIS DOES NOT DO, and the tests say so as plainly as the ones that
do. The twin still writes ISO. That is owner decision 5 of the Phase 2
plan, `format` is REPORT-ONLY because of it, and residual R-P2-7
records the loss: a person parsing with an explicit format argument
still has to change that argument. What they gain here is the column's
whole behaviour AS A DATE, which they had none of before.
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


def _described(
    values: "list[str]",
) -> "tuple[dict, contract.Profile, pathlib.Path]":
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder, "thing.csv", fixtures.single_column_table("thing", values)
    )
    document = profile.build_document(
        reading.read_table(f"{table}"), taxonomy.Settings(), []
    )
    written = fixtures.write_profile(folder, "thing.json", document)
    return document, contract.load_profile(f"{written}"), folder


# -- the reading itself -----------------------------------------------


MONTHS = (
    ("jan", "january"), ("feb", "february"), ("mar", "march"),
    ("apr", "april"), ("may", "may"), ("jun", "june"),
    ("jul", "july"), ("aug", "august"), ("sep", "september"),
    ("oct", "october"), ("nov", "november"), ("dec", "december"),
)


def test_the_month_name_vocabulary_is_read_either_way_it_is_written() -> None:
    """THE WHOLE CLOSED LIST, not a sample of it (contract C6-D8N).

    An earlier version of this test walked eight names, so removing
    `february` or `april` from the vocabulary left it green -- a test
    that names a closed list and checks part of it is a test that lets
    the list quietly shrink.
    """
    place = 0
    for short, whole in MONTHS:
        place = place + 1
        month = f"0{place}" if place < 10 else f"{place}"
        for spelling in (
            short, whole, short.upper(), whole.upper(), short.capitalize(),
        ):
            assert parsing.month_of_name(spelling) == month, spelling
    for word in ("", "Ja", "Janu", "Smarch", "13", "Mar.", "Sept"):
        assert parsing.month_of_name(word) is None, word


def test_the_month_name_is_CASE_FOLDED_and_not_merely_lowercased() -> None:
    """The package has one folding operation and this reads it.

    An earlier revision reached for `.lower()`, which is a different
    rule: Unicode case folding maps the long s to `s`, so `ſep` folds
    to `sep` while lower-casing leaves it alone. The contract says case
    folding, `parsing.folded` is what the rest of the package means by
    it, and a second spelling of one rule living in one function is how
    an exception comes apart from the rule it excepts.
    """
    assert "\u017Fep".lower() != "sep"
    assert parsing.folded("\u017Fep") == "sep"
    assert parsing.month_of_name("\u017Fep") == "09"
    assert parsing.parse_datetime(
        "17 \u017Fep 2024", "textual-day-first-date"
    ) == ("2024-09-17", "")


def test_each_written_shape_reads_as_the_day_it_names() -> None:
    """The four shapes, each under the member that owns it."""
    for text, member in (
        ("17 Mar 2024", "textual-day-first-date"),
        ("17-Mar-2024", "textual-day-first-date"),
        ("17 March 2024", "textual-day-first-date"),
        ("7 Mar 2024", "textual-day-first-date"),
        ("Mar 17, 2024", "textual-month-first-date"),
        ("March 17, 2024", "textual-month-first-date"),
        ("Mar-17-2024", "textual-month-first-date"),
        ("Mar 7, 2024", "textual-month-first-date"),
    ):
        assert parsing.parse_datetime(text, member) == (
            "2024-03-17" if "17" in text else "2024-03-07", ""
        ), text


def test_the_two_members_do_not_reach_each_other_s_spellings() -> None:
    """The position of the NAME decides it, and nothing else has to."""
    assert parsing.parse_datetime(
        "Mar 17, 2024", "textual-day-first-date"
    ) is None
    assert parsing.parse_datetime(
        "17 Mar 2024", "textual-month-first-date"
    ) is None


def test_a_day_the_calendar_does_not_have_is_not_a_date() -> None:
    """The same rule every other member keeps."""
    for text in ("32 Mar 2024", "30 Feb 2024", "17 Foo 2024", "0 Mar 2024"):
        assert parsing.parse_datetime(
            text, "textual-day-first-date"
        ) is None, text


def test_a_mixed_separator_is_not_this_grammar() -> None:
    """`17 Mar-2024` is not a shape anybody writes."""
    for text in ("17 Mar-2024", "17-Mar 2024"):
        assert parsing.parse_datetime(
            text, "textual-day-first-date"
        ) is None, text


# -- the column, end to end -------------------------------------------


def test_a_textual_column_is_a_date_column_now() -> None:
    """THE CASE THE DECISION IS FOR, and the whole of what it buys.

    Before this landing every assertion below was false: the role was
    `free_text`, and a free-text block publishes no endpoint at all.
    """
    for pattern, member in (
        ("%d %b %Y", "textual-day-first-date"),
        ("%d-%b-%Y", "textual-day-first-date"),
        ("%d %B %Y", "textual-day-first-date"),
        ("%b %d, %Y", "textual-month-first-date"),
        ("%B %d, %Y", "textual-month-first-date"),
    ):
        document, _loaded, _folder = _described(
            [day.strftime(pattern) for day in DAYS]
        )
        block = document["columns"][0]
        assert block["role"] == "datetime", pattern
        assert block["format"] == member, pattern
        assert block["resolution"] == "date", pattern
        assert block["earliest"] == "2024-01-01", pattern
        assert block["latest"] == "2024-08-27", pattern
        assert block["n_unparsed"] == 0, pattern
        assert block["resolution_mix"] == {member: 240}, pattern


def test_the_twin_of_a_textual_column_carries_the_dates() -> None:
    """Every published obligation met, on a column that had none.

    THE ROLE IS ASSERTED HERE AND NOT ONLY THE VERDICT, which is the
    correction the second adversarial read asked for. A quality report
    is a statement about a description and the file beside it, so a
    twin of a FREE-TEXT column also reports nothing missed -- and this
    test, which exists to show the textual reading works, passed just
    as happily with the reading removed entirely. It now says what kind
    of column it is looking at before it says the column is met.
    """
    document, described, folder = _described(
        [day.strftime("%d %b %Y") for day in DAYS]
    )
    assert document["columns"][0]["role"] == "datetime"
    assert described.columns[0].role == "datetime"
    twin = generation.generate(described, 3)
    cells = [cell for cell in twin.columns[0] if cell]
    assert cells, "a twin of this column must hold cells"
    for cell in cells:
        assert parsing.parse_datetime(cell, "iso-date") is not None, cell
    written = fixtures.write(folder, "twin.csv", rendering.twin_csv(twin))
    outcome = validation.measure(described, f"{written}")
    assert outcome.census.missed == 0


def test_the_twin_writes_iso_and_that_is_the_ratified_choice() -> None:
    """OWNER DECISION 5, ASSERTED RATHER THAN ASSUMED.

    This landing adds READING. The twin's date syntax is ISO at the
    recorded precision, `format` is REPORT-ONLY because of it, and
    residual R-P2-7 records what a person still owes: the format
    argument in their own parsing call. A test that let the twin
    quietly start writing the source's spelling would be a test that
    let this repository start claiming something it has not built.
    """
    _document, described, _folder = _described(
        [day.strftime("%d %b %Y") for day in DAYS]
    )
    twin = generation.generate(described, 3)
    for cell in twin.columns[0]:
        if not cell:
            continue
        assert parsing.parse_datetime(cell, "iso-date") is not None, cell


def test_a_column_of_month_names_alone_is_not_a_date_column() -> None:
    """The criterion that keeps ordinary words out is unweakened."""
    document, _loaded, _folder = _described(
        ["Jan", "Feb", "Mar", "Apr"] * 60
    )
    assert document["columns"][0]["role"] != "datetime"


def test_a_comma_after_the_month_name_is_not_this_grammar() -> None:
    """What the adversarial read found: the comma belongs to one shape.

    `Mar 17, 2024` is written with a comma because the comma follows a
    DAY. `17 Mar, 2024` puts one after a month name, which no writer
    does and no member of the contract owns -- and the shared splitter
    stripped it before either member was consulted, so the day-first
    member accepted a spelling nobody had written down.
    """
    for text in ("17 Mar, 2024", "17-Mar,-2024", "17 March, 2024"):
        assert parsing.parse_datetime(
            text, "textual-day-first-date"
        ) is None, text
    # The shape that does own a comma still reads, and so does the
    # day-first shape without one.
    assert parsing.parse_datetime(
        "Mar 17, 2024", "textual-month-first-date"
    ) == ("2024-03-17", "")
    assert parsing.parse_datetime(
        "17 Mar 2024", "textual-day-first-date"
    ) == ("2024-03-17", "")


def test_no_field_carries_space_of_its_own() -> None:
    """The separator rule, made true rather than nearly true.

    `month_of_name` trims before it matches, so a middle field of
    ` Mar` answered `03` and `17- Mar-2024` was read as a date under a
    grammar that permits no such spelling: the contract asks for ONE
    separator character, the same one both times. The day and year
    fields were never exposed to this -- both ask for ASCII digits and
    a space is not one -- so the guard is written over all three
    rather than the one that happened to need it.
    """
    for text in (
        "17- Mar-2024",
        "17-Mar -2024",
        "17-\tMar-2024",
        "17 Mar-2024",
        "17-Mar 2024",
    ):
        for member in (
            "textual-day-first-date", "textual-month-first-date"
        ):
            assert parsing.parse_datetime(text, member) is None, text


def test_the_month_vocabulary_is_closed_where_the_contract_closes_it() -> None:
    """C6-D8N, and the cost of closing it, both asserted.

    `Sept` is a real abbreviation people write and this package does
    NOT read it. That is the contract's choice and the test states it,
    so that a later widening is a decision somebody makes rather than
    something that drifts in: a vocabulary left open is one two
    implementations spell differently.
    """
    assert parsing.month_of_name("Sept") is None
    assert parsing.month_of_name("Sep") == "09"
    assert parsing.month_of_name("September") == "09"
    assert parsing.parse_datetime(
        "17 Sept 2024", "textual-day-first-date"
    ) is None
