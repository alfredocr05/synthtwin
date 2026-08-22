"""The widened date readings, and the form census they made necessary.

Plan P4-D4.3. Two of its three widenings are built here: the slashed
ISO form of item 1, and the joint ISO reading of item 3 with the
`resolution_mix` census that reading forced onto every column of dates.
Item 2, the month resolution, is not built and nothing in this file
pretends it is.

WHAT IS PINNED HERE, each of it a rule the decision states rather than
a property somebody noticed:

- the slashed ISO form reads because the YEAR LEADS, so no second
  reading of the same cell exists, and the two-figure slashed forms are
  untouched by it;
- THE SINGLE-FORMAT PASS RUNS FIRST and its verdict stands wherever it
  clears -- ninety-nine ISO dates and one stamp is a column of dates
  with one cell that did not read, exactly as it was before this
  widening, and the joint reading never sees it;
- the joint reading runs ONLY where no single format clears the line,
  and then publishes at the finer of the two forms, because a cell that
  wrote a time of day would otherwise lose it;
- the census has exactly two permitted key sets, and the loader refuses
  every other one (RM1) and every total that is not the parsed count
  (RM2);
- the census is REPORT-ONLY: the twin writes every parsed cell at the
  finest recorded precision, and the twin's own report says so, per
  column, every run, with both sides recounted from the finished cells;
- and the quality report lists the census as an obligation it does not
  check, in words, for a reason that is true of it -- not the reason
  the format fact carries, which would claim a file cannot show this.
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
    parsing,
    profile,
    quality,
    reading,
    rendering,
    taxonomy,
    validation,
)


def _described(
    values: "list[str]",
    name: str = "seen_on",
) -> "tuple[dict, contract.Profile, pathlib.Path]":
    """One single-column table, described and read back."""
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder, f"{name}.csv", fixtures.single_column_table(name, values)
    )
    document = profile.build_document(
        reading.read_table(f"{table}"), taxonomy.Settings(), []
    )
    written = fixtures.write_profile(folder, f"{name}.json", document)
    return document, contract.load_profile(f"{written}"), table


def _dates(count: int) -> "list[str]":
    """Whole ISO dates, all different, spread over one year."""
    return [f"2024-{1 + place % 12:02d}-{1 + place % 28:02d}" for place in range(count)]


def _stamps(count: int) -> "list[str]":
    """ISO datetimes, all different, spread over the same year."""
    return [
        f"2024-{1 + place % 12:02d}-{1 + place % 28:02d} "
        f"{6 + place % 12:02d}:{place % 60:02d}:{(place * 7) % 60:02d}"
        for place in range(count)
    ]


# -- item 1: the slashed ISO form -------------------------------------


def test_a_slashed_iso_column_is_a_column_of_dates() -> None:
    """`2024/03/15` reads, and reads as the day it names.

    The year leads, so there is no second reading of the cell: no
    calendar has a four-figure day or month. That is the whole reason
    this form could join the table while the two-figure slashed forms
    still carry a question.
    """
    values = [value.replace("-", "/") for value in _dates(120)]
    document, described, _table = _described(values)
    block = document["columns"][0]
    assert block["role"] == "datetime"
    assert block["format"] == "slashed-iso-date"
    assert block["resolution"] == "date"
    assert block["earliest"] == "2024-01-01"
    assert block["latest"] == "2024-12-28"
    assert described.columns[0].facts.n_unparsed == 0


def test_the_slashed_iso_form_does_not_read_the_two_figure_forms() -> None:
    """A padded four-figure year is required, and nothing shorter.

    If this form ever accepted `03/05/2024` it would be a second
    reading of a cell the month-first and day-first members already
    read, and the ambiguity the year-leading rule exists to avoid would
    be back inside the one member that has none.
    """
    assert parsing.parse_datetime("2024/03/05", "slashed-iso-date") is not None
    for value in ("03/05/2024", "24/03/05", "2024/3/5", "2024/03/5"):
        assert parsing.parse_datetime(value, "slashed-iso-date") is None


def test_a_slashed_iso_column_makes_a_twin_that_reads_back() -> None:
    """The whole way through, on the form this widening added."""
    values = [value.replace("-", "/") for value in _dates(120)]
    _document, described, _table = _described(values)
    twin = generation.generate(described, 7)
    folder = pathlib.Path(tempfile.mkdtemp())
    written = fixtures.write(folder, "twin.csv", rendering.twin_csv(twin))
    outcome = validation.measure(described, f"{written}")
    missed = [check.subcheck for check in outcome.checks if check.verdict == validation.MISSED]
    assert missed == []


# -- item 3: the single-format pass keeps its verdict -----------------


def test_one_stamp_among_dates_stays_a_column_of_dates() -> None:
    """The case the decision names outright, and it must not move.

    Ninety-nine ISO dates and one datetime cell is a column of dates
    with one cell that did not read -- before this widening and after
    it. A joint reading that claimed this column would change the
    published resolution of columns that read perfectly well today.
    """
    values = _dates(119) + ["2024-06-01 08:30:00"]
    document, described, _table = _described(values)
    block = document["columns"][0]
    assert block["format"] == "iso-date"
    assert block["resolution"] == "date"
    assert block["n_unparsed"] == 1
    assert block["resolution_mix"] == {"iso-date": 119}
    assert described.columns[0].facts.resolution_mix == {"iso-date": 119}


def test_a_single_format_column_publishes_its_own_form_alone() -> None:
    """Every column of dates carries the census, with one name in it.

    The key is REQUIRED on every block, which is what stops a reader
    from having to know whether a mixed column would have published
    one -- and what stops an implementation from publishing the census
    only where it is interesting.
    """
    for values, expected in (
        (_dates(120), "iso-date"),
        (_stamps(120), "iso-datetime"),
        ([value.replace("-", "/") for value in _dates(120)], "slashed-iso-date"),
    ):
        document, _loaded, _table = _described(values)
        block = document["columns"][0]
        assert block["format"] == expected
        assert block["resolution_mix"] == {expected: 120}


# -- item 3: the joint reading ----------------------------------------


def test_a_mixed_iso_column_is_read_jointly() -> None:
    """Neither ISO form clears the line alone; together they do."""
    document, described, _table = _described(_dates(60) + _stamps(60))
    block = document["columns"][0]
    assert block["role"] == "datetime"
    assert block["format"] == "iso-mixed"
    assert block["n_unparsed"] == 0
    assert block["resolution_mix"] == {"iso-date": 60, "iso-datetime": 60}
    assert described.columns[0].facts.parser_family == "iso-mixed"


def test_the_joint_reading_publishes_at_the_finer_form() -> None:
    """A column holding times of day is published at the second.

    Publishing such a column as whole dates would throw away every time
    of day it holds. The cells that carried none are placed at midnight,
    and the census is what says how many of them there were, so nothing
    invites a reader to think they all wrote a time.
    """
    document, described, _table = _described(_dates(60) + _stamps(60))
    block = document["columns"][0]
    assert block["resolution"] == "datetime"
    assert block["time_precision"] == "second"
    facts = described.columns[0].facts
    assert isinstance(facts, contract.DatetimeFacts)
    assert facts.resolution == "datetime"


def test_a_mixed_column_of_two_other_families_is_not_read() -> None:
    """Only the ISO family mixes, and the decision says why.

    A compact date and a month-first date are ambiguous with one
    another, so a joint reading of them would be a guess. The column
    declines instead, which is the outcome it had before this widening.
    """
    values = ["20240315"] * 60 + ["03/15/2024"] * 60
    document, _loaded, _table = _described(values)
    assert document["columns"][0]["role"] != "datetime"


def test_a_month_beside_a_day_stays_unread() -> None:
    """The residual the decision names, asserted as the residual it is.

    `2024-03` beside `2024-03-17` is not read, because the month
    resolution is not built. This test exists so that building it is a
    visible change here rather than a silent one.
    """
    values = ["2024-03"] * 60 + _dates(60)
    document, _loaded, _table = _described(values)
    assert document["columns"][0]["role"] != "datetime"


# -- the census as a document: what the loader refuses ----------------


def _forged(document: dict, mix: object) -> str:
    """Load one document with its census replaced, and refuse it."""
    folder = pathlib.Path(tempfile.mkdtemp())
    changed = copy.deepcopy(document)
    changed["columns"][0]["resolution_mix"] = mix
    written = fixtures.write_profile(folder, "forged.json", changed)
    with pytest.raises(errors.ProfileError) as raised:
        contract.load_profile(f"{written}")
    return f"{raised.value}"


def test_the_census_of_a_single_format_column_names_that_format() -> None:
    """RM1, on the shape a single-format column may not take."""
    document, _loaded, _table = _described(_dates(120))
    for mix in (
        {"iso-datetime": 120},
        {"iso-date": 60, "iso-datetime": 60},
        {},
    ):
        said = _forged(document, mix)
        assert "RM1" in said


def test_the_census_of_a_joint_reading_names_both_members() -> None:
    """RM1 again, from the other side: a joint reading needs both."""
    document, _loaded, _table = _described(_dates(60) + _stamps(60))
    for mix in ({"iso-mixed": 120}, {"iso-datetime": 120}, {"iso-date": 120}):
        said = _forged(document, mix)
        assert "RM1" in said


def test_the_census_counts_the_values_that_parsed() -> None:
    """RM2, in both directions."""
    document, _loaded, _table = _described(_dates(60) + _stamps(60))
    for mix in (
        {"iso-date": 60, "iso-datetime": 59},
        {"iso-date": 61, "iso-datetime": 60},
    ):
        said = _forged(document, mix)
        assert "RM2" in said


def test_a_census_is_refused_before_it_can_be_a_share() -> None:
    """A count, not a share: the census may not carry a fraction.

    The publication guard holds these to whole numbers, so a document
    stating the mix as two halves of one is refused where it is read
    rather than believed and divided by something.
    """
    document, _loaded, _table = _described(_dates(60) + _stamps(60))
    said = _forged(document, {"iso-date": 0.5, "iso-datetime": 0.5})
    assert "resolution_mix" in said


# -- the census as a fact: REPORT-ONLY, and said so -------------------


def test_the_twin_report_names_the_census_as_not_reproduced() -> None:
    """Per column, every run -- and both sides recounted.

    The published side comes from the description and the achieved side
    is counted off the cells this run wrote, so the line can say which
    it was rather than restate a rule.
    """
    _document, described, _table = _described(_dates(60) + _stamps(60))
    for seed in (1, 2, 3):
        twin = generation.generate(described, seed)
        named = [
            deviation
            for deviation in twin.deviations
            if deviation.fact == "resolution_mix"
        ]
        assert len(named) == 1
        assert "60" in named[0].published
        assert "120 carry a time of day" in named[0].achieved


def test_a_single_format_column_earns_no_census_line() -> None:
    """The census restates the format there, and the format is listed.

    Two lines for one loss would tell a reader there were two.
    """
    _document, described, _table = _described(_dates(120))
    twin = generation.generate(described, 4)
    assert [
        deviation
        for deviation in twin.deviations
        if deviation.fact == "resolution_mix"
    ] == []


def test_the_quality_report_lists_the_census_in_its_own_words() -> None:
    """And the words are true of THIS fact.

    The sentence the format fact carries says a written file cannot
    show the fact. Of this one that would be false -- anybody can count
    the two shapes in a CSV -- so the census carries its own reason: the
    description asks no file to match it.
    """
    _document, described, _table = _described(_dates(60) + _stamps(60))
    twin = generation.generate(described, 9)
    folder = pathlib.Path(tempfile.mkdtemp())
    written = fixtures.write(folder, "twin.csv", rendering.twin_csv(twin))
    outcome = validation.measure(described, f"{written}")
    listed = [
        listing
        for listing in outcome.listings
        if listing.fact == "datetime.resolution_mix"
    ]
    assert len(listed) == 1
    assert "asks no file to write them the same way" in listed[0].reason
    assert "cannot show it" not in listed[0].reason
    page = quality.quality_report(described, outcome)
    assert "how many of your dates were written as a whole date" in page


def test_the_census_is_never_a_verdict() -> None:
    """It is a listing, and a listing is not a check that passed.

    A REPORT-ONLY fact counted as a passed check would inflate the one
    number the quality report exists to make honest.
    """
    _document, described, _table = _described(_dates(60) + _stamps(60))
    twin = generation.generate(described, 11)
    folder = pathlib.Path(tempfile.mkdtemp())
    written = fixtures.write(folder, "twin.csv", rendering.twin_csv(twin))
    outcome = validation.measure(described, f"{written}")
    assert [
        check for check in outcome.checks if "resolution_mix" in check.fact
    ] == []


def test_a_twin_of_a_mixed_column_still_meets_every_obligation() -> None:
    """The census is the one thing it does not carry, and it is listed."""
    _document, described, _table = _described(_dates(60) + _stamps(60))
    twin = generation.generate(described, 13)
    folder = pathlib.Path(tempfile.mkdtemp())
    written = fixtures.write(folder, "twin.csv", rendering.twin_csv(twin))
    outcome = validation.measure(described, f"{written}")
    missed = [
        check.subcheck for check in outcome.checks if check.verdict == validation.MISSED
    ]
    assert missed == []
