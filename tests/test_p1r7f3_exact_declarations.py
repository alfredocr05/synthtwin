"""P1-R7-F3: a declared value is compared with a cell EXACTLY.

Round 6 settled the right rule -- a declared number matches a cell by
the NUMBER both denote, so `--keep-value -999` covers a file that writes
`-999.00` -- and applied it with the wrong instrument. Both sides were
turned into the binary64 value they round to and those were compared,
and rounding makes one number out of two:

* profiled with `--missing-value 9007199254740992`, a column holding
  twenty of that number and twenty of 9007199254740993 lost all forty
  rows. Twenty values nobody named were removed, the column came back
  empty, and nothing in the profile said so;
* `--keep-value 9007199254740992 --missing-value 9007199254740993`
  names two different numbers and was refused as a contradiction.

The comparison is now on the exact number each spelling denotes, so two
spellings that denote different numbers never match however close the
binary64 values they round to are, and two spellings that denote one
number always match however differently they are written.

Everything here goes through `cli.main` with the words a person would
type, except the unit checks at the end, which pin the canonical form
the comparison is made of.
"""

import fractions
import json
import pathlib

import pytest

import fixtures
from synthtwin import parsing, taxonomy
from synthtwin.cli import main

# The reviewer's pair: two whole numbers one apart, both of which round
# to the same binary64 value because it is the first pair above the
# range where every whole number has its own.
LOWER = "9007199254740992"
UPPER = "9007199254740993"

# Distinct decimal spellings that round to one binary64 value, one pair
# per way of reaching the boundary: whole numbers just above the exactly
# representable range, a short fraction beside the exact decimal value
# of the number it rounds to, and two neighbouring long fractions.
COLLAPSING_PAIRS = [
    (LOWER, UPPER),
    ("0.1", "0.1000000000000000055511151231257827021181583404541015625"),
    ("1.0000000000000002", "1.0000000000000003"),
    ("0.3", "0.29999999999999998889776975374843"),
]

# Spellings that all denote -999, which is the behaviour round 6
# established and which must survive the repair unchanged.
ONE_NUMBER_MANY_SPELLINGS = [
    "-999",
    "-999.0",
    "-999.00",
    " -999 ",
    "-9.99e2",
    "-0.999E3",
    "(999)",
]

READINGS = [f"{index}" for index in range(1, 200)]


def _written(tmp_path: pathlib.Path, name: str, values: list[str]) -> str:
    """One column on disk, and its path as a person would type it."""
    text = fixtures.single_column_table(name, values)
    return f"{fixtures.write(tmp_path, f'{name}.csv', text)}"


def _kept(spelling: str) -> str:
    """`--keep-value` and its value as one word.

    Joined with `=` so that a spelling opening with a minus sign reaches
    the option whatever the command-line parser makes of a leading `-`.
    Both forms are what a person types; this one is the one that carries
    every spelling this item is about. The spaced form is exercised by
    `tests/test_p1r6f9_declared_values.py`.
    """
    return f"--keep-value={spelling}"


def _missing(spelling: str) -> str:
    """`--missing-value` and its value as one word, for the same reason."""
    return f"--missing-value={spelling}"


def _run(
    tmp_path: pathlib.Path,
    name: str,
    values: list[str],
    options: list[str],
    capsys: pytest.CaptureFixture[str],
) -> dict:
    """Profile one column through the command; return the document."""
    table = _written(tmp_path, name, values)
    assert main(["profile", table] + options) == 0
    capsys.readouterr()
    document = json.loads(
        (tmp_path / f"{name}-profile.json").read_text(encoding="utf-8")
    )
    assert isinstance(document, dict)
    return document


def _exactly(triple: "tuple[int, tuple[str, ...], int]") -> fractions.Fraction:
    """The number a canonical triple denotes, computed independently.

    The test's own arithmetic, in a library the product does not use, so
    that the canonical form is checked against something other than
    itself.
    """
    sign, digits, power = triple
    if sign == 0:
        assert digits == () and power == 0, "zero has exactly one form"
        return fractions.Fraction(0)
    whole = 0
    for digit in digits:
        whole = whole * 10 + int(digit)
    return sign * fractions.Fraction(whole) * fractions.Fraction(10) ** power


# -- the item's own reproduction --------------------------------------


def test_the_neighbour_of_a_declared_number_is_not_removed_with_it(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # The reviewer's damaging direction, reproduced exactly: forty rows,
    # twenty of each of two whole numbers one apart, and only one of the
    # two named. Before the repair the column came back with n_present
    # zero and forty rows counted as declared missing.
    values = [LOWER] * 20 + [UPPER] * 20
    document = _run(tmp_path, "reading", values, [_missing(LOWER)], capsys)
    column = document["columns"][0]
    assert column["n_missing"] == 20, (
        "only the twenty rows holding the number that was named may go"
    )
    assert column["n_present"] == 20
    assert column["missing_by_class"]["(declared-missing)"] == 20
    assert column["role"] != taxonomy.ROLE_EMPTY


def test_the_other_neighbour_is_the_one_that_goes(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # The mirror image, so that the check above cannot pass by removing
    # the wrong twenty rows.
    values = [LOWER] * 20 + [UPPER] * 20
    document = _run(tmp_path, "reading", values, [_missing(UPPER)], capsys)
    column = document["columns"][0]
    assert column["n_missing"] == 20
    assert column["n_present"] == 20


@pytest.mark.parametrize(("lower", "upper"), COLLAPSING_PAIRS)
def test_two_numbers_that_round_alike_are_still_two_numbers(
    lower: str,
    upper: str,
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # The class the item names, at three more boundaries. Each pair is
    # two different numbers whose binary64 values are equal, so a
    # comparison of rounded values treats either as the other.
    assert parsing.parse_number(lower) == parsing.parse_number(upper), (
        "this pair is only interesting while both spellings round alike"
    )
    values = [lower] * 20 + [upper] * 20
    document = _run(tmp_path, "reading", values, [_missing(lower)], capsys)
    column = document["columns"][0]
    assert column["n_missing"] == 20
    assert column["n_present"] == 20


@pytest.mark.parametrize(("lower", "upper"), COLLAPSING_PAIRS)
def test_two_numbers_that_round_alike_do_not_contradict_each_other(
    lower: str,
    upper: str,
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # The item's other direction: keeping one and declaring the other
    # missing names two different numbers, and a person who typed them
    # was told they were the same value and refused.
    table = _written(tmp_path, "reading", READINGS + [lower] * 15)
    code = main(["profile", table, _kept(lower), _missing(upper)])
    assert code == 0, capsys.readouterr().err
    capsys.readouterr()
    assert (tmp_path / "reading-profile.json").exists()


@pytest.mark.parametrize(("lower", "upper"), COLLAPSING_PAIRS)
def test_the_library_does_not_call_the_pair_a_contradiction(
    lower: str, upper: str
) -> None:
    assert taxonomy.contradictory_declarations((lower,), (upper,)) == []
    assert taxonomy.contradictory_declarations((upper,), (lower,)) == []


# -- everything round 6 established, re-verified ----------------------


@pytest.mark.parametrize("declared", ONE_NUMBER_MANY_SPELLINGS)
@pytest.mark.parametrize("in_the_file", ONE_NUMBER_MANY_SPELLINGS)
def test_one_number_still_matches_however_either_side_spells_it(
    declared: str,
    in_the_file: str,
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    values = READINGS + [in_the_file] * 15
    document = _run(tmp_path, "reading", values, [_kept(declared)], capsys)
    column = document["columns"][0]
    assert column["n_missing"] == 0, (
        f"{declared!r} and {in_the_file!r} are the same number, "
        "and the person said that number is data"
    )
    assert column["percentiles"]["min"] == -999.0


@pytest.mark.parametrize("declared", ["0", "-0", "0.0", "-0.00", "0e0"])
def test_zero_still_covers_the_zero_written_with_a_minus(
    declared: str,
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Signed zero is one number, and a person who names it names both
    # ways of writing it.
    values = READINGS + ["-0"] * 15
    document = _run(
        tmp_path, "reading", values, [_missing(declared)], capsys
    )
    column = document["columns"][0]
    assert column["n_missing"] == 15
    assert column["missing_by_class"]["(declared-missing)"] == 15


def test_a_declaration_that_names_no_number_still_matches_by_spelling(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    values = ["north"] * 40 + ["south"] * 40 + ["NA"] * 40
    document = _run(tmp_path, "region", values, [_kept(" na ")], capsys)
    column = document["columns"][0]
    assert column["n_missing"] == 0
    assert column["role"] == taxonomy.ROLE_CATEGORICAL


def test_one_number_named_both_ways_is_still_refused(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # Two spellings, one number, opposite instructions: still refused,
    # still said in words, still nothing written.
    table = _written(tmp_path, "reading", READINGS + ["-999"] * 15)
    code = main(["profile", table, _kept("-999"), _missing("-9.99e2")])
    assert code == 2
    told = capsys.readouterr().err
    assert "contradict each other" in told
    assert "Decide which one you meant" in told
    assert not (tmp_path / "reading-profile.json").exists()


def test_the_accounting_form_is_the_negative_number() -> None:
    # `(999)` is minus nine hundred and ninety-nine, so it clashes with
    # -999 and not with 999. Getting this backwards would publish a
    # column of debts as credits.
    assert len(taxonomy.contradictory_declarations(("-999",), ("(999)",))) == 1
    assert taxonomy.contradictory_declarations(("999",), ("(999)",)) == []


def test_a_spelling_this_format_cannot_hold_still_matches_by_spelling() -> None:
    # A number too large to hold denotes no value this tool can compare,
    # so it falls back to the spelling rule -- unchanged from round 6,
    # and stated here because the exact comparison could have been read
    # as an invitation to widen the range.
    assert parsing.classify_number("1e400") == parsing.NUMBER_OUT_OF_RANGE
    assert taxonomy.contradictory_declarations(("1e400",), ("1e400",)) != []
    assert taxonomy.contradictory_declarations(("1e400",), ("1e401",)) == []
    assert taxonomy.contradictory_declarations(("1e400",), ("10e399",)) == []


# -- the canonical form itself ----------------------------------------


NOTATIONS = [
    "0",
    "-0",
    "1",
    "-1",
    "+999",
    "1000",
    "1,000",
    "1,000.00",
    "0.1",
    "0.10",
    "-999.00",
    "-9.99e2",
    "(1,234.50)",
    "1e-320",
    "5e-324",
    "1.7976931348623157e308",
    "0.30000000000000004",
    "0e00000000000000000000000",
    LOWER,
    UPPER,
]


@pytest.mark.parametrize("text", NOTATIONS)
def test_the_exact_form_denotes_what_the_reader_read(text: str) -> None:
    # The repair's own soundness condition: the exact number and the
    # binary64 number must be the same number, one rounded and one not.
    # If these ever part company, the profile's statistics and its
    # declaration matching are describing two different tables.
    assert parsing.classify_number(text) == parsing.NUMBER
    triple = taxonomy._exact_value(text)
    assert triple is not None
    assert float(_exactly(triple)) == parsing.parse_number(text)


@pytest.mark.parametrize(
    "text", ["NA", "", "abc", "1e400", "(-5)", "12mg", "1,23"]
)
def test_a_spelling_that_is_not_a_number_has_no_exact_form(
    text: str,
) -> None:
    assert parsing.classify_number(text) != parsing.NUMBER
    assert taxonomy._exact_value(text) is None


def test_the_exact_form_is_canonical() -> None:
    # Equal numbers give equal triples and different numbers give
    # different ones. That is the whole of the comparison, so it is
    # checked directly and not only through its consequences.
    for text in ONE_NUMBER_MANY_SPELLINGS:
        assert taxonomy._exact_value(text) == taxonomy._exact_value("-999")
    for zero in ["0", "-0", "0.0", "-0.000", "0e00", "(0)"]:
        assert taxonomy._exact_value(zero) == taxonomy._exact_value("0")
    for lower, upper in COLLAPSING_PAIRS:
        assert taxonomy._exact_value(lower) != taxonomy._exact_value(upper)
        assert _exactly(taxonomy._exact_value(lower)) != _exactly(
            taxonomy._exact_value(upper)
        )


@pytest.mark.parametrize(
    "value",
    [-9999.0, -999.0, 9999.0, 0.0, -0.0, 1.0, 0.5, 0.1, 1e22, 5e-324],
)
def test_a_number_already_held_gets_the_same_exact_form(value: float) -> None:
    # The numeric sentinels reach the declaration comparison as numbers
    # rather than as text, so the two ways into the canonical form have
    # to agree about what a number is.
    assert _exactly(taxonomy._exact_number(value)) == fractions.Fraction(value)


def test_a_kept_sentinel_is_recognised_through_the_number_it_is(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # The sentinel rule asks the same question through the same
    # comparison: the candidate arrives as a number, the declaration as
    # text, and the person's word still wins.
    values = READINGS + ["-999"] * 15
    document = _run(
        tmp_path, "reading", values, [_kept("-0.999e3")], capsys
    )
    column = document["columns"][0]
    assert column["n_missing"] == 0
    verdicts = column["sentinel_verdicts"]
    assert [entry["reason"] for entry in verdicts] == ["kept_by_you"]
