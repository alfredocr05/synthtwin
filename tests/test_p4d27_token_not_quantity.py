"""P4-D27: a number wrapped in text is not always a quantity (R-P4-39).

A column of `user12345@example.org` was claimed by the affixed-number
role and published a ladder, a mean and a spread over its cores. On 400
rows the mean was 53,574.055 -- the average of the real identifiers --
and the smallest and largest were two of them exactly. That is the
failure this project puts ahead of every ordinary bug: a number that
looks entirely plausible and is meaningless.

WHAT IS PINNED HERE, and why each case is in the file:

- the shape that DECLINES, with its real spelling;
- **the shapes that must NOT decline, which is most of this file**,
  because the first version of this rule declined several of them and
  was refused by the suite;
- and the half of R-P4-39 that CANNOT be closed by reading values,
  pinned as a test so nobody re-opens it as a bug.

**TWO EARLIER VERSIONS OF THIS RULE WERE WRONG, and their cases are
kept below as tests rather than as a story.**

The first declined on all-whole, all-different cores inside a
letter-bearing prefix. That reads `code1` as a token and `1mg` as a
quantity, which review item P1-R6-F8 deleted for the fourth time;
seventeen tests refused it.

The second declined on `@` anywhere in the pair, over a claim that no
unit uses that character. **The claim was false**: `100 ms @ ambient`
and `$100@close` are ordinary quantities. Both would have lost their
distribution.

What survives makes a POSITIVE identification -- the suffix IS an
electronic address, `@` then a host then a dot then a letter label --
rather than a negative claim that no quantity looks like something.
"""

import csv
import pathlib
import random

from synthtwin import taxonomy


def _cells(values: "list[str]", settings: "taxonomy.Settings | None" = None):
    """One column's tally, built the way the profiler builds it."""
    used = settings if settings is not None else taxonomy.Settings()
    return taxonomy._tally(taxonomy._classify_all(values), len(values), used)


def _reads_as_affixed(values: "list[str]", declared: bool = False) -> bool:
    """Whether the affixed rule claims this column."""
    return taxonomy._affixed_reading(_cells(values), declared) is not None


def _identifiers(count: int = 400, seed: int = 11) -> "list[int]":
    """Distinct whole numbers, as a record-number column holds them."""
    return random.Random(seed).sample(range(10000, 99999), count)


def test_an_address_column_no_longer_reads_as_a_quantity() -> None:
    """The shape R-P4-39 was opened for."""
    values = [f"user{number}@example.org" for number in _identifiers()]
    assert not _reads_as_affixed(values)


def test_a_prefixed_record_number_STILL_reads_as_a_quantity() -> None:
    """THE HALF THAT CANNOT BE CLOSED BY READING VALUES.

    `ACC00012345` is a record code and reads as a quantity, which is
    wrong. It stays wrong on purpose: it cannot be told from `USD100`
    by any property of the values, and four rules that tried were each
    defeated by the column next door (P1-R6-F8). The answer is a
    declaration -- `--identifier` or `--code`.

    This is a test so that nobody re-opens it as a bug, finds it easy,
    and writes the fifth defeated rule.
    """
    values = [f"ACC{number:08d}" for number in _identifiers()]
    assert _reads_as_affixed(values)


def test_a_measurement_with_a_unit_still_reads() -> None:
    """The reading this rule must not take away.

    A weight column carries fractions, which is the first test, and
    repeats, which is the second. Either alone would keep it.
    """
    rng = random.Random(3)
    values = [f"{rng.uniform(45, 120):.1f} kg" for _each in range(400)]
    assert _reads_as_affixed(values)


def test_a_whole_repeating_dose_still_reads() -> None:
    """Whole numbers alone are not enough to decline.

    `450 mg` is whole in every cell, so only the all-different test
    keeps this column -- which is why that test is in the rule.
    """
    rng = random.Random(4)
    values = [f"{rng.choice([250, 500, 750, 1000])} mg" for _each in range(400)]
    assert _reads_as_affixed(values)


def test_a_currency_column_of_all_different_whole_amounts_still_reads() -> None:
    """A salary column keeps its distribution."""
    values = [f"${number}" for number in _identifiers()]
    assert _reads_as_affixed(values)


def test_a_quantity_measured_at_a_condition_still_reads() -> None:
    """`100 ms @ ambient`. THE SECOND VERSION OF THIS RULE LOST IT.

    `@` means "at" as often as it introduces a host, and a rule that
    declined on the character alone took this column's distribution
    away. Kept as a test because the claim that no quantity uses `@`
    was made in a docstring and refuted the same day.
    """
    values = [f"{number} ms @ ambient" for number in range(100, 500)]
    assert _reads_as_affixed(values)


def test_a_price_at_a_market_close_still_reads() -> None:
    """`$100@close`, the second counterexample, for the same reason."""
    values = [f"${number}@close" for number in range(100, 500)]
    assert _reads_as_affixed(values)


def test_the_declaration_silences_the_rule() -> None:
    """THE PERSON WHO OWNS THE TABLE HAS THE LAST WORD.

    An address-shaped column the person calls a measurement is read as
    numbers. This regression exists because the guard was DELETED by an
    edit that narrowed the rule, and nothing caught it until review:
    the parameter was still accepted, still passed, and no longer
    consulted.
    """
    values = [f"user{number}@example.org" for number in _identifiers()]
    assert not _reads_as_affixed(values)
    assert _reads_as_affixed(values, declared=True)


def test_the_two_columns_no_value_can_separate_are_treated_alike() -> None:
    """P1-R6-F8's own pairing, re-asserted from this rule's side.

    `1mg` and `code1` are one shape of string. Any rule here that
    treats them differently is the defect that review deleted, and
    this test is where such a rule meets it first.
    """
    amounts = [f"{index}mg" for index in range(1, 31)]
    codes = [f"code{index}" for index in range(1, 31)]
    assert _reads_as_affixed(amounts) == _reads_as_affixed(codes)


def test_a_letter_prefixed_currency_still_reads() -> None:
    """`USD100`, all different and whole, is a quantity.

    The withdrawn rule declined this. It is the column that proves the
    letter test was arbitrary: nothing separates it from `ACC00012345`.
    """
    values = [f"USD{number}" for number in _identifiers()]
    assert _reads_as_affixed(values)


def test_a_letter_prefixed_amount_still_reads() -> None:
    """`Rs52000` keeps its distribution.

    The withdrawn rule declined this too, which is what a rule reading
    values costs: a real salary column, silently no longer described.
    """
    values = [f"Rs{number}" for number in _identifiers()]
    assert _reads_as_affixed(values)


def test_the_declining_column_is_not_silent(tmp_path: pathlib.Path) -> None:
    """A column that stops being described must say something.

    It falls to free text, whose remarks tell the person that nothing
    was assumed and that `--identifier` exists. **They do not yet name
    `--measurement`**, which is recorded in P4-D27 and rides with the
    advisory-remarks landing; this test pins what IS said so that the
    day it changes, it changes on purpose.
    """
    from synthtwin import profile, reading

    table = tmp_path / "addresses.csv"
    with table.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["email"])
        for number in _identifiers():
            writer.writerow([f"user{number}@example.org"])
    read = reading.read_table(f"{table}")
    document = profile.build_document(read, taxonomy.Settings(), [])
    column = document["columns"][0]
    assert column["role"] == taxonomy.ROLE_TEXT
    said = " ".join(column["remarks"])
    assert "--identifier" in said
    assert "did NOT assume" in said
