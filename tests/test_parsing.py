"""Cell-level parsing rules (plan P1-D4).

These are the rules the whole taxonomy rests on: if "1,23" quietly
became 123, or "nan" became a number, or the 31st of February became a
date, every statistic computed afterwards would be wrong while every
other test stayed green.
"""

import math

import pytest

from synthtwin import parsing


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("0", 0.0),
        ("42", 42.0),
        ("-7", -7.0),
        ("+7", 7.0),
        ("3.5", 3.5),
        (".5", 0.5),
        ("5.", 5.0),
        ("  12  ", 12.0),
        ("1e3", 1000.0),
        ("1E-3", 0.001),
        ("1,234", 1234.0),
        ("1,234,567.5", 1234567.5),
        ("(1,234.50)", -1234.5),
        ("(8)", -8.0),
    ],
)
def test_numbers_that_must_parse(text: str, expected: float) -> None:
    assert parsing.parse_number(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "",
        "   ",
        "abc",
        "1.2.3",
        "1,23",
        "12,3456",
        "1,234,",
        "0x1f",
        "1_000",
        "nan",
        "NaN",
        "inf",
        "-inf",
        "infinity",
        "1e999",
        "١٢٣",
        "12%",
        "$12",
        "- 5",
        "(5",
        "5)",
    ],
)
def test_text_that_must_not_parse_as_a_number(text: str) -> None:
    assert parsing.parse_number(text) is None, (
        f"{text!r} must not be read as a number: reading it as one would "
        "put a value into the statistics that the file does not contain"
    )


def test_not_a_number_words_are_refused_even_though_python_accepts_them() -> None:
    # float("nan") succeeds in Python. If it succeeded here, one such
    # cell would make every mean, spread and percentile of the column
    # not-a-number, and the profile would still look complete.
    assert math.isnan(float("nan"))
    assert parsing.parse_number("nan") is None
    assert parsing.parse_number("inf") is None


@pytest.mark.parametrize(
    ("text", "form", "canonical"),
    [
        ("2024-03-17", "iso-date", "2024-03-17"),
        ("2024-02-29", "iso-date", "2024-02-29"),
        ("20240317", "compact-date", "2024-03-17"),
        ("03/17/2024", "month-first-date", "2024-03-17"),
        ("17/03/2024", "day-first-date", "2024-03-17"),
        ("2024-Q3", "year-quarter", "2024-Q3"),
        ("2024-q3", "year-quarter", "2024-Q3"),
        ("2024-03-17T14:05", "iso-datetime", "2024-03-17 14:05:00"),
        ("2024-03-17 14:05:09", "iso-datetime", "2024-03-17 14:05:09"),
        ("2024-03-17T14:05:09.123456", "iso-datetime", "2024-03-17 14:05:09"),
    ],
)
def test_dates_that_must_parse(text: str, form: str, canonical: str) -> None:
    parsed = parsing.parse_datetime(text, form)
    assert parsed is not None
    assert parsed[0] == canonical


@pytest.mark.parametrize(
    ("text", "form"),
    [
        ("2023-02-29", "iso-date"),
        ("2024-13-01", "iso-date"),
        ("2024-00-10", "iso-date"),
        ("2024-04-31", "iso-date"),
        ("2024-3-17", "iso-date"),
        ("17/03/2024", "month-first-date"),
        ("2024-Q5", "year-quarter"),
        ("2024-Q0", "year-quarter"),
        ("20241332", "compact-date"),
        ("2024-03-17T25:00:00", "iso-datetime"),
        ("2024-03-17T14:61", "iso-datetime"),
    ],
)
def test_dates_that_must_not_parse(text: str, form: str) -> None:
    assert parsing.parse_datetime(text, form) is None


def test_century_leap_year_rule() -> None:
    # 1900 was not a leap year; 2000 was. Getting this wrong would turn
    # one real date a year into an unparseable straggler.
    assert parsing.parse_datetime("1900-02-29", "iso-date") is None
    assert parsing.parse_datetime("2000-02-29", "iso-date") is not None


def test_utc_offsets_are_recorded_not_dropped() -> None:
    parsed = parsing.parse_datetime("2024-03-17T14:05:09+02:00", "iso-datetime")
    assert parsed == ("2024-03-17 14:05:09", "+02:00")
    zulu = parsing.parse_datetime("2024-03-17T14:05:09Z", "iso-datetime")
    assert zulu == ("2024-03-17 14:05:09", "Z")


@pytest.mark.parametrize(
    "text", ["", "   ", "NA", "n/a", "NULL", "None", "nan", ".", "-", "--", "?"]
)
def test_spellings_that_mean_no_value(text: str) -> None:
    assert parsing.is_missing_text(text)


@pytest.mark.parametrize("text", ["0", "-1", "na.", "none of these", "n", "?!"])
def test_text_that_is_a_value_not_a_gap(text: str) -> None:
    assert not parsing.is_missing_text(text)


def test_zero_is_never_treated_as_missing() -> None:
    # A zero count is data. Treating it as missing would move real mass
    # out of the distribution and silently raise every mean.
    assert not parsing.is_missing_text("0")
    assert parsing.parse_number("0") == 0.0


def test_whole_number_test() -> None:
    assert parsing.is_whole_number(5.0)
    assert parsing.is_whole_number(-5.0)
    assert not parsing.is_whole_number(5.5)


def test_token_count() -> None:
    assert parsing.token_count("") == 0
    assert parsing.token_count("one") == 1
    assert parsing.token_count("  two words  ") == 2


def test_parsers_refuse_anything_that_is_not_text() -> None:
    # The readers always hand text over; this is the invariant that says
    # so out loud rather than letting a stray value through.
    for value in (5, None, [], {}):
        with pytest.raises(TypeError):
            parsing.parse_number(value)  # type: ignore[arg-type]
        with pytest.raises(TypeError):
            parsing.is_missing_text(value)  # type: ignore[arg-type]
