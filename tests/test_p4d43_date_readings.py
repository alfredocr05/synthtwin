"""The widened date readings, and the form census they made necessary.

Plan P4-D4.3, all three widenings: the slashed ISO form of item 1, the
month resolution of item 2, and the joint ISO reading of item 3 with
the `resolution_mix` census that reading forced onto every column of
dates. Amendment A-P4-1's own two widenings are here too -- the
unpadded year-last slashed fields of its item 1, and the two slashed
stamp members of its item 2.

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


def test_the_year_last_slashed_families_take_unpadded_fields() -> None:
    """A table that writes `3/5/2024` writes the same day as `03/05/2024`.

    Amendment A-P4-1 item 1 retired the ten-character rule for the four
    year-last families and for those only. The earlier reader refused
    the first spelling over a leading zero nobody typed, and a whole
    column of them fell through to free text, which publishes nothing.
    """
    for value, day in (
        ("3/5/2024", "2024-03-05"),
        ("1/1/2024", "2024-01-01"),
        ("12/31/2024", "2024-12-31"),
        ("3/13/2024", "2024-03-13"),
    ):
        assert parsing.parse_datetime(value, "month-first-date") == (day, "")
    assert parsing.parse_datetime("5/3/2024", "day-first-date") == (
        "2024-03-05",
        "",
    )


def test_an_unpadded_slashed_column_is_a_column_of_dates() -> None:
    """And the widening is a ROUTING change, not only a parsing one."""
    values = [f"3/{13 + place % 19}/2024" for place in range(120)]
    document, described, _table = _described(values)
    block = document["columns"][0]
    assert block["role"] == "datetime"
    assert block["format"] == "month-first-date"
    assert block["earliest"] == "2024-03-13"
    assert block["latest"] == "2024-03-31"
    assert described.columns[0].facts.n_unparsed == 0


def test_the_unpadded_grammar_refuses_what_it_should() -> None:
    """The year is four figures and still comes last, or nothing reads.

    That is the whole of what keeps the four families apart: the
    year-first slashed member is fully padded, and the compact family
    is eight figures with no delimiter, so no spelling satisfies two of
    the three.
    """
    for value in (
        "003/5/2024",
        "3/5/24",
        "3//2024",
        "3/5/2024/",
        "3/5/20244",
        "/3/5/2024",
        "2/30/2024",
        "3/5/two-thousand",
    ):
        assert parsing.parse_datetime(value, "month-first-date") is None
        assert parsing.parse_datetime(value, "day-first-date") is None
    for value in ("2024/03/05", "20240305"):
        assert parsing.parse_datetime(value, "month-first-date") is None
        assert parsing.parse_datetime(value, "day-first-date") is None


def test_an_unpadded_column_still_carries_the_ambiguity_remark() -> None:
    """The amendment says ambiguity handling is untouched; it is.

    A column whose fields could be read either way is read month-first
    and says so, whether or not its fields are padded.
    """
    padded = [f"0{1 + place % 9}/0{1 + place % 9}/2024" for place in range(120)]
    unpadded = [f"{1 + place % 9}/{1 + place % 9}/2024" for place in range(120)]
    first, _described_one, _one = _described(padded, "padded")
    second, _described_two, _two = _described(unpadded, "unpadded")
    assert first["columns"][0]["format"] == "month-first-date"
    assert second["columns"][0]["format"] == "month-first-date"
    assert first["columns"][0]["remarks"] == second["columns"][0]["remarks"]
    assert first["columns"][0]["remarks"] != []


def test_a_rescued_spelling_is_counted_present() -> None:
    """`--keep-value NA` makes `NA` a value, and the recount must agree.

    The recount now reads cells the way the twin will be read, and it
    reached for the predicate that keeps this run from MAKING UP a
    spelling a reader might call absent, rather than the one that says
    what this column publishes. Forty cells the person rescued were
    then counted absent, and the report carried distinctness
    deviations no file has (review item P4-DATE2-F2).
    """
    values = ["north"] * 40 + ["south"] * 40 + ["NA"] * 40
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder, "r.csv", fixtures.single_column_table("region", values)
    )
    settings = taxonomy.Settings(kept_values=("NA",))
    document = profile.build_document(
        reading.read_table(f"{table}"), settings, []
    )
    written = fixtures.write_profile(folder, "r.json", document)
    described = contract.load_profile(f"{written}")
    twin = generation.generate(described, 3)
    outcome = twin.outcomes[0]
    assert outcome.n_present == 120
    assert outcome.n_missing == 0
    assert outcome.n_distinct == 3
    assert twin.deviations == ()
    # ...and the conservative predicate is still the one that guards an
    # INVENTED spelling, so nothing this run makes up wears a word a
    # reader might call absent.
    assert generation._is_a_hole_spelling("NA", ())
    assert not generation._wears_a_published_hole("NA", ())


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

    `2024-03` beside `2024-03-17` is not read, and now that the month
    resolution IS built the reason is the one the decision gives rather
    than an absence: neither form reaches the parse line alone, and the
    only joint reading there is joins the two ISO instant forms. A
    month is a span and a date is a day, so a joint reading of them
    would have to choose which of the two the column publishes at, and
    the decision declines to choose.
    """
    values = ["2024-03"] * 60 + _dates(60)
    document, _loaded, _table = _described(values)
    assert document["columns"][0]["role"] != "datetime"


# -- item 2: the month resolution -------------------------------------


def test_a_column_of_months_is_read_at_the_month() -> None:
    """`YYYY-MM` is a span, and it is published as one."""
    values = [f"20{20 + place // 12:02d}-{1 + place % 12:02d}" for place in range(120)]
    document, described, _table = _described(values)
    block = document["columns"][0]
    assert block["role"] == "datetime"
    assert block["format"] == "iso-month"
    assert block["resolution"] == "month"
    assert block["time_precision"] == "month"
    assert block["earliest"] == "2020-01"
    assert block["latest"] == "2029-12"
    assert block["resolution_mix"] == {"iso-month": 120}
    assert described.columns[0].facts.n_unparsed == 0


def test_a_month_ladder_is_read_in_months() -> None:
    """Twelve to the year, from the origin the quarter counts from."""
    assert generation._ordinal_of("1970-01", "month") == 0
    assert generation._ordinal_of("1970-12", "month") == 11
    assert generation._ordinal_of("1971-01", "month") == 12
    assert generation._ordinal_of("2024-06", "month") == 12 * 54 + 5
    for ordinal, text in ((0, "1970-01"), (11, "1970-12"), (12, "1971-01")):
        assert generation._cell_of_ordinal(ordinal, "month", "month", 0) == text


def test_a_month_twin_reads_back_as_a_column_of_months() -> None:
    """The whole way through, on the resolution this item added."""
    values = [f"20{20 + place // 12:02d}-{1 + place % 12:02d}" for place in range(120)]
    _document, described, _table = _described(values)
    twin = generation.generate(described, 5)
    folder = pathlib.Path(tempfile.mkdtemp())
    written = fixtures.write(folder, "twin.csv", rendering.twin_csv(twin))
    outcome = validation.measure(described, f"{written}")
    missed = [
        check.subcheck for check in outcome.checks if check.verdict == validation.MISSED
    ]
    assert missed == []
    again = profile.build_document(
        reading.read_table(f"{written}"), taxonomy.Settings(), []
    )
    assert again["columns"][0]["format"] == "iso-month"
    assert again["columns"][0]["resolution"] == "month"


def test_a_month_and_a_quarter_are_not_one_reading() -> None:
    """Both are seven characters with a dash at the fifth, and neither
    reads the other."""
    assert parsing.parse_datetime("2024-03", "year-quarter") is None
    assert parsing.parse_datetime("2024-Q1", "iso-month") is None
    assert parsing.parse_datetime("2024-03-15", "iso-month") is None


def test_no_span_reader_admits_a_year_the_calendar_lacks() -> None:
    """Year zero, which both span readers took (review item P4-DATE3-F4).

    `_valid_date` has always refused it for every reader that names a
    DAY. The two readers that name a span had no such check, so the
    producer itself would publish `0000-01` -- a canonical form the
    contract's own range starts above.
    """
    for value in ("0000-01", "0000-12"):
        assert parsing.parse_datetime(value, "iso-month") is None
    for value in ("0000-Q1", "0000-Q4"):
        assert parsing.parse_datetime(value, "year-quarter") is None
    assert parsing.parse_datetime("0001-01", "iso-month") is not None
    assert parsing.parse_datetime("0001-Q1", "year-quarter") is not None


def test_the_twin_report_does_not_warn_where_nothing_changed() -> None:
    """A column already in the international form keeps its spelling.

    Telling that reader to change an explicit date format would send
    them to fix code that is not broken (review item P4-DATE3-F5).
    """
    values = [f"20{20 + place // 12:02d}-{1 + place % 12:02d}" for place in range(120)]
    _document, described, _table = _described(values)
    twin = generation.generate(described, 6)
    page = rendering.report(described, twin)
    assert "which IS that form" in page
    assert "it is NOT kept" not in page


# -- amendment A-P4-1 item 2: the two slashed stamp members -----------


def test_a_slashed_stamp_column_is_a_column_of_dates_and_times() -> None:
    """A slashed date, one space, and a clock in the role's two forms."""
    values = [
        f"{1 + place % 12}/{1 + place % 28}/2024 {8 + place % 10:02d}:{place % 60:02d}"
        for place in range(120)
    ]
    document, described, _table = _described(values)
    block = document["columns"][0]
    assert block["role"] == "datetime"
    assert block["format"] == "month-first-datetime"
    assert block["resolution"] == "datetime"
    assert block["time_precision"] == "minute"
    assert described.columns[0].facts.n_unparsed == 0


def test_the_slashed_stamp_carries_the_ambiguity_remark() -> None:
    """The date half is as ambiguous as the date member's is."""
    values = [
        f"0{1 + place % 9}/0{1 + place % 9}/2024 {8 + place % 10:02d}:{place % 60:02d}"
        for place in range(120)
    ]
    document, _loaded, _table = _described(values)
    assert document["columns"][0]["format"] == "month-first-datetime"
    assert document["columns"][0]["remarks"] != []


def test_the_stamp_clock_is_the_role_s_two_forms_and_no_wider() -> None:
    """No fractional second, no offset, no unpadded hour."""
    for value in ("3/17/2024 14:05", "3/17/2024 14:05:09", "03/17/2024 14:05"):
        assert parsing.parse_datetime(value, "month-first-datetime") is not None
    for value in (
        "3/17/2024 14:05:09.5",
        "3/17/2024 14:05+02:00",
        "3/17/2024 4:05",
        "3/17/2024  14:05",
        "3/17/2024T14:05",
        "2024/03/17 14:05",
        "3/17/2024",
    ):
        assert parsing.parse_datetime(value, "month-first-datetime") is None


def test_the_stamp_reader_and_the_precision_reader_cannot_part() -> None:
    """One says the cell parsed and the other says how finely it wrote.

    A cell one accepts and the other reads differently is two answers
    to one question, which is the shape every reading defect in this
    module has taken.
    """
    for value in (
        "3/17/2024 14:05",
        "3/17/2024 14:05:09",
        "3/17/2024  14:05",
        "3/17/2024 4:05",
        "3/17/2024",
    ):
        parsed = parsing.parse_datetime(value, "month-first-datetime") is not None
        told = parsing.datetime_precision(value, "month-first-datetime")
        assert parsed == (told in ("minute", "second")), value


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


def test_a_column_read_under_one_format_has_no_census_line() -> None:
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
    # ...and the words are true of a column of MONTHS too, whose census
    # has one key and no time of day in it at all (review item
    # P4-DATE3-F5).
    assert "carried a time of day" not in listed[0].reason
    page = quality.quality_report(described, outcome)
    assert "which written form each of your dates wore" in page


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


# -- what the adversarial read of this work turned up -----------------


def test_the_parse_line_is_the_exact_product(  # P4-DATE-F1
) -> None:
    """A line built by rounding is a line that moves.

    The contract fixes the parse-line count as the smallest whole
    number reaching the EXACT product of the recorded rate and the
    count. A rate recorded as `0.01` is not one hundredth -- the
    nearest binary64 to it is a shade above -- so against a hundred
    values the exact product is a shade above one and the line is two.
    Multiplying in binary64 rounded that product back down to exactly
    one and the line came out at one, which is a line the contract does
    not state.
    """
    assert taxonomy._needed(0.01, 100) == 2
    assert taxonomy._needed(0.01, 200) == 3
    assert taxonomy._needed(0.99, 240) == 238
    assert taxonomy._needed(0.5, 7) == 4
    assert taxonomy._needed(1.0, 240) == 240
    assert taxonomy._needed(0.0, 240) == 0


def test_the_rate_is_carried_as_the_numbers_it_stands_for() -> None:
    """And the pair really is the rate, for every rate in the range."""
    place = 0
    while place < 2000:
        share = place / 2000
        numerator, denominator = taxonomy._exact_ratio(share)
        assert numerator / denominator == share
        assert denominator > 0
        place = place + 1


def test_the_ceiling_counterpart_is_exact_too() -> None:
    """`_at_most` decides roles by the same product and moves the same.

    THE FIRST THREE CASES CANNOT FAIL, AND THAT IS WHY THE REST ARE
    HERE (review item P4-DATE2-F4). At `0.10` against 240, at zero and
    at one, rounding and exactness agree, so an assertion built from
    those alone stays green under the very implementation this repair
    replaced. The cases below are ones where the two part company: the
    binary64 nearest three hundredths sits BELOW it, so the exact
    product with a hundred is a shade under three and the ceiling is
    two, where the rounded product was exactly three. This count routes
    a column to the category rule, so the difference is a role.
    """
    assert taxonomy._at_most(0.10, 240) == 24
    assert taxonomy._at_most(0.0, 240) == 0
    assert taxonomy._at_most(1.0, 13) == 13
    assert taxonomy._at_most(0.03, 100) == 2
    assert taxonomy._at_most(0.03, 200) == 5
    assert taxonomy._at_most(0.06, 50) == 2
    assert taxonomy._at_most(0.15, 20) == 2


def test_the_loader_applies_the_same_line_the_producer_does() -> None:
    """The rule is written twice on purpose, so it is checked twice.

    The loader may not import the describing side, so it carries its
    own copy of the parse line -- and one copy was repaired while the
    other went on rounding, which is a loader admitting a description
    the producer would never write (review item P4-DATE2-F1).
    """
    for share in (0.01, 0.03, 0.07, 0.5, 0.99, 1.0, 0.0):
        for total in (1, 7, 50, 100, 200, 240, 1000):
            assert contract._line_count(share, total) == taxonomy._needed(
                share, total
            )


def test_a_stand_in_number_reaches_its_share_as_a_count() -> None:
    """The last threshold that decided a boundary by a rounded division.

    A candidate is removed only where it is BOTH an outlier and reaches
    `sentinel_minimum_share`. That share was compared against a
    division computed in binary64, and one occurrence in two hundred
    rounds to exactly the recorded rate although the exact share is
    below it -- so a single `-999` was called frequent, removed, and
    the column published a smallest value of 1 where its own table
    holds -999 (review item P4-DATE2-F3).
    """
    values = ["-999"] + [f"{place + 1}" for place in range(199)]
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder, "n.csv", fixtures.single_column_table("score", values)
    )
    document = profile.build_document(
        reading.read_table(f"{table}"), taxonomy.Settings(), []
    )
    block = document["columns"][0]
    assert block["n_present"] == 200
    assert block["n_missing"] == 0
    assert block["percentiles"]["min"] == -999.0
    assert block["sentinel_verdicts"] == []


def _mixed_with_a_declared_hole(
    declared: "tuple[str, ...]",
    holes: "list[str]",
) -> "tuple[dict, contract.Profile, taxonomy.Settings, pathlib.Path]":
    """A joint reading whose midnight endpoint a declaration also spells."""
    folder = pathlib.Path(tempfile.mkdtemp())
    dates = ["2024-01-01"] + [f"2024-04-{1 + place % 28:02d}" for place in range(59)]
    stamps = [
        f"2024-{6 + place % 6:02d}-{1 + place % 28:02d} "
        f"{8 + place % 10:02d}:{place % 60:02d}:{(place * 7) % 60:02d}"
        for place in range(60)
    ]
    table = fixtures.write(
        folder,
        "seen.csv",
        fixtures.single_column_table("seen", dates + stamps + holes),
    )
    settings = taxonomy.Settings(declared_missing_values=declared)
    document = profile.build_document(reading.read_table(f"{table}"), settings, [])
    written = fixtures.write_profile(folder, "seen.json", document)
    return document, contract.load_profile(f"{written}"), settings, folder


def test_an_endpoint_is_not_lost_to_a_declared_spelling(  # P4-DATE-F2
) -> None:
    """The collision is the twin's own doing, so the twin undoes it.

    A real column can hold a present cell at midnight written
    `2024-01-01` and, beside it, cells a declaration made absent as
    `2024-01-01T00:00:00`. Both facts are honest. The twin then writes
    every parsed cell at the finest precision, reaches for the second
    spelling, and hands back a cell its OWN description reads as
    absent -- so an exact end walks out over a separator nobody chose.
    The space form is written instead: the same instant, at the same
    precision, on the same clock.
    """
    document, described, settings, folder = _mixed_with_a_declared_hole(
        ("2024-01-01T00:00:00",), ["2024-01-01T00:00:00"] * 11
    )
    assert document["columns"][0]["format"] == "iso-mixed"
    assert document["columns"][0]["earliest"] == "2024-01-01 00:00:00"
    assert document["columns"][0]["missing_by_source"] == {
        "2024-01-01T00:00:00": 11
    }
    for seed in (1, 2, 3):
        twin = generation.generate(described, seed)
        # THE PRESENT CELLS, and the filter is the version 6 write rule
        # (plan P4-D6.1): the twin now writes each recorded hole
        # spelling at its published count, so the declared spelling
        # appears among the ABSENT cells on purpose. What must not wear
        # it is a cell the twin means as a value.
        holes = set(described.columns[0].missing_by_source)
        cells = [
            cell
            for cell in twin.columns[0]
            if cell and cell not in holes
        ]
        assert "2024-01-01T00:00:00" not in cells
        assert "2024-01-01 00:00:00" in cells
        assert [
            deviation
            for deviation in twin.deviations
            if deviation.fact == "earliest"
        ] == []
        written = fixtures.write(
            folder, f"twin{seed}.csv", rendering.twin_csv(twin)
        )
        again = profile.build_document(
            reading.read_table(f"{written}"), settings, []
        )
        assert again["columns"][0]["n_present"] == 120
        assert again["columns"][0]["earliest"] == "2024-01-01 00:00:00"


def test_where_no_spelling_survives_the_loss_is_named() -> None:
    """And no third spelling is invented to hide it.

    With BOTH separators declared absent there is no cell text left
    that reads as the published end and is not read as a hole. The run
    writes the fixed form and says the end is gone, which is what the
    method's own words promise for a fact it cannot hold.
    """
    _document, described, _settings, _folder = _mixed_with_a_declared_hole(
        ("2024-01-01T00:00:00", "2024-01-01 00:00:00"),
        ["2024-01-01T00:00:00"] * 11 + ["2024-01-01 00:00:00"] * 11,
    )
    twin = generation.generate(described, 1)
    named = [
        deviation for deviation in twin.deviations if deviation.fact == "earliest"
    ]
    assert len(named) == 1
    assert "reads that cell as absent" in named[0].achieved


def test_the_census_recount_does_not_count_an_absent_cell() -> None:
    """The recount is the twin's own reader, or it is not a recount.

    A cell wearing a declared spelling is not a date of any form when
    the twin is described again, and a census line that counted it
    would say the twin wrote a value where its own description finds
    none.
    """
    _document, described, _settings, _folder = _mixed_with_a_declared_hole(
        ("2024-01-01T00:00:00", "2024-01-01 00:00:00"),
        ["2024-01-01T00:00:00"] * 11 + ["2024-01-01 00:00:00"] * 11,
    )
    twin = generation.generate(described, 1)
    named = [
        deviation
        for deviation in twin.deviations
        if deviation.fact == "resolution_mix"
    ]
    assert len(named) == 1
    assert "119 carry a time of day" in named[0].achieved


def test_the_recount_of_present_cells_reads_through_the_declaration() -> None:
    """The same rule, one grain wider: this is every column's count.

    `n_present` is what a person gets by describing the twin again, so
    a cell the twin's own description reads as absent is not present in
    it, whatever the bytes look like.
    """
    holes = ("no value",)
    assert generation._recounted(["a", "b", ""], ()) == (2, 1, 2, 2)
    assert generation._recounted(["a", "no value", ""], holes) == (1, 2, 1, 1)


def test_the_method_names_the_census_among_its_deviations(  # P4-DATE-F3
) -> None:
    """A report line no specification carries is a line nobody owes.

    G12's list is the closed inventory a reviewer checks the report
    against, and a second implementation reading it would have had no
    rule authorizing this line at all.
    """
    method = pathlib.Path(__file__).resolve().parent.parent
    body = (method / "docs" / "spec" / "generation-method-v1.md").read_text(
        encoding="utf-8"
    )
    flat = " ".join(body.split())
    assert "the form census of a column of dates read under the joint" in flat
    assert "`resolution_mix` is REPORT-ONLY" in flat


def test_a_declared_number_is_matched_exactly_by_the_recount() -> None:
    """Two numbers a person can tell apart are never one (P4-DATE3-F2).

    The producer's declaration rule is exact: `-999` and
    `-999.00000000000001` denote two numbers and a declaration naming
    one reaches only its own cells. The recount compared the two after
    rounding them both to binary64, so a column publishing the second
    as a label had those cells counted absent.
    """
    assert generation._wears_a_published_hole("-999.00", ("-999",))
    assert generation._wears_a_published_hole("-999e0", ("-999",))
    assert not generation._wears_a_published_hole(
        "-999.00000000000001", ("-999",)
    )
    assert not generation._wears_a_published_hole("-998", ("-999",))
    # ...and it is the producer's own rule, by its own name, not a
    # second copy of it.
    assert parsing.exact_of_spelling("-999.00") == parsing.exact_of_spelling(
        "-999"
    )
    assert parsing.exact_of_spelling(
        "-999.00000000000001"
    ) != parsing.exact_of_spelling("-999")


def test_a_stand_in_never_wears_a_spelling_the_column_calls_absent() -> None:
    """Every invention site asks, because the speller itself asks.

    A numeric column publishing `missing_by_source {"text-1": 11}` got
    `text-1` invented for its one ordinary-text stand-in, and
    describing the twin again then found twelve absent cells and no
    unparsed one -- an EXACT-OBSERVABLE count gone before any recount
    could name it (review item P4-DATE3-F3).
    """
    used: "dict[str, int]" = {}
    assert generation._text_spelling(1, used, ()) == "text-1"
    assert generation._text_spelling(1, used, ("text-1",)) == "text-2"
    assert generation._text_spelling(1, used, ("text-1", "text-2")) == "text-3"

    values = [f"{place + 1}" for place in range(120)] + ["oddity"]
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder,
        "n.csv",
        fixtures.single_column_table("score", values + ["text-1"] * 11),
    )
    settings = taxonomy.Settings(declared_missing_values=("text-1",))
    document = profile.build_document(
        reading.read_table(f"{table}"), settings, []
    )
    assert document["columns"][0]["missing_by_source"] == {"text-1": 11}
    written = fixtures.write_profile(folder, "n.json", document)
    described = contract.load_profile(f"{written}")
    twin = generation.generate(described, 4)
    # The PRESENT cells again: since P4-D6.1 the twin reproduces
    # `text-1` in the absent cells at its published count, which is
    # what the description records. The stand-in this test is about is
    # a cell the twin means as a value.
    holes = set(described.columns[0].missing_by_source)
    cells = [
        cell for cell in twin.columns[0] if cell and cell not in holes
    ]
    assert "text-1" not in cells
    assert twin.outcomes[0].n_present == 121
