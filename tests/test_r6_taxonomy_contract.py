"""Round 6 repairs to the column-analysis contract (P1-R6-F3, F8, F10).

Three separate promises are checked here, each with the exact example
the reviewer supplied:

* F3 -- a spread larger than this file format can hold must be reported
  as out of range, not published as the largest finite number. The
  reviewer's column rounds DOWN onto that number, so the test also
  proves that the rounded answer would have looked ordinary;
* F8 -- NO rule decides the identifier role. It is reached only when the
  person who owns the table names the column with `--identifier`. Three
  inferences were tried and each was defeated by the column next door,
  the last of them by `1mg`, which is the same shape of string as
  `code1`: what separates a dose from a label is what the column MEANS,
  and the values do not carry it. A column no rule claims is described
  as free text, which publishes no value either, and says so;
* F10 -- every present cell is classified exactly once, and the work of
  describing a column grows in proportion to its length rather than as
  the square of it.

The exact statistics themselves are checked against the independent
reference vectors in `test_numeric_reference.py`; nothing here is an
oracle for them.
"""

import fractions
import json
import pathlib
import sys
import time
import typing

import pytest

import fixtures
from synthtwin import cli, parsing, profile, reading, taxonomy

# THE SMALLEST GROUP EVERY CASE HERE IS DESCRIBED AT, DECLARED BECAUSE
# IT IS NO LONGER THE DEFAULT. The owner lowered the shipped
# `small_cell_floor` to one (plan amendment A-P4-37), and the floor is
# not only about what a description withholds: the affixed-number rule
# claims a column only when at least `small_cell_floor` of its cells
# are affixed, so at a floor of one a column of FIVE cells is claimed
# by it. The short-column case below is written about a column NO rule
# claims -- which is the whole of item F8 -- and at a floor of one there
# is no such column to write about. Eleven is the floor this file's
# examples were sized against, so it is asked for once here rather than
# left to a default that has moved beneath them. The floor of one is
# the subject of `tests/test_p3v5f1_floor_one.py`.
SETTINGS = taxonomy.Settings(small_cell_floor=11)

# The reviewer's column: three distinct values whose exact sample
# standard deviation is larger than the largest finite binary64 number
# and smaller than the point at which rounding overflows.
SATURATING_SPREAD = [
    "-1.5568479229996504e+308",
    "1.5568479229996504e+308",
    "1.5568479229996502e+308",
]

# A column of amounts written with a unit after the number, and a column
# of true record codes. One word each, every character in the code
# alphabet, all different, in a table big enough for "all different" to
# mean something -- and structurally indistinguishable from each other,
# which is the whole reason the inference is gone.
UNIT_AMOUNTS = [f"{index}mg" for index in range(1, 31)]
RECORD_CODES = [f"code{index}" for index in range(1, 31)]

# Values made of letters and nothing else.
ALL_LETTERS = [
    f"zz{first}{second}"
    for first in "abcde"
    for second in "abcdef"
]
# Zero-padded clock times: four digits, one width, `0000` carrying the
# leading zero, none repeating. Every clause the first inference tested,
# and a clock is not a record number.
CLOCK_TIMES = [
    f"{hour:02d}{minute:02d}"
    for hour in range(24)
    for minute in range(0, 60, 10)
]
# The same text, meant as a padded account number. Nothing in either
# column says which is which, which is the point of the pair.
PADDED_COUNTS = [f"{index:06d}" for index in range(50)]
# A letter first, a letter last, a letter buried among digits and
# hyphens. Round 6 read all three as record numbers; `1mg` has a letter
# in exactly the same place as `1a`.
LETTER_FIRST = [f"a{index}" for index in range(50)]
LETTER_LAST = [f"{index}a" for index in range(50)]
LETTER_INSIDE = [f"00{index:04d}-x" for index in range(50)]
MIXED_SHAPES = RECORD_CODES[:29] + ["000042"]


def describe(
    values: list[str],
    settings: taxonomy.Settings = SETTINGS,
    forced: bool = False,
) -> taxonomy.ColumnProfile:
    """One column, described by the rules under test."""
    return taxonomy.profile_column(
        "column", 1, values, len(values), settings, forced
    )


def whole_block(described: taxonomy.ColumnProfile) -> str:
    """Everything the profile would carry for one column, as one string."""
    return json.dumps(profile._column_block(described), sort_keys=True)


def exact_sample_variance(values: list[str]) -> fractions.Fraction:
    """The exact sample variance, computed here rather than by the code.

    Written with `fractions`, which does not round, so this is an
    independent statement of what the column's spread really is.
    """
    numbers = [fractions.Fraction(float(text)) for text in values]
    count = len(numbers)
    mean = sum(numbers, fractions.Fraction(0)) / count
    squares = [(number - mean) * (number - mean) for number in numbers]
    return sum(squares, fractions.Fraction(0)) / (count - 1)


# -- P1-R6-F3: an exact out-of-range spread --------------------------


def test_the_reviewers_spread_really_is_out_of_range_and_rounds_down() -> None:
    """The premise, stated independently of the code under test.

    Exact rational arithmetic, no float64 anywhere in the comparison:
    the exact standard deviation of this column is larger than the
    largest finite number this format holds, and smaller than the
    midpoint above it -- which is exactly why rounding it produces that
    largest finite number and raises nothing.
    """
    largest = fractions.Fraction(sys.float_info.max)
    step = fractions.Fraction(2) ** 970
    variance = exact_sample_variance(SATURATING_SPREAD)
    assert variance > largest * largest
    assert variance < (largest + step) * (largest + step)


def test_an_exact_out_of_range_spread_is_null_and_flagged() -> None:
    described = describe(SATURATING_SPREAD)
    assert described.role == taxonomy.ROLE_CONTINUOUS
    assert described.details["std"] is None, (
        "a spread this format cannot hold must not be published as a "
        "number at all"
    )
    assert described.details["std_unrepresentable"] is True, (
        "null on its own means 'undefined', which is a different fact"
    )
    # The rest of the description is unaffected: only the spread was out
    # of range.
    assert described.details["mean"] is not None
    assert described.details["skew"] is not None
    assert described.details["percentiles"]["max"] is not None


def test_the_out_of_range_spread_is_not_published_as_a_finite_maximum() -> None:
    # The defect this closes: the exact spread rounds DOWN onto the
    # largest finite number, so the rounding step raises nothing and the
    # profile published 1.7976931348623157e+308 as an ordinary standard
    # deviation. Publishing that number here again is the regression.
    described = describe(SATURATING_SPREAD)
    assert described.details["std"] != sys.float_info.max
    assert str(sys.float_info.max) not in whole_block(described)


def test_the_decision_is_made_on_the_exact_value_not_the_rounded_one() -> None:
    # Proof that the check runs BEFORE rounding: rounding the very same
    # exact fraction yields a perfectly ordinary finite number.
    variance = exact_sample_variance(SATURATING_SPREAD)
    rounded = taxonomy._rounded_root(
        variance.numerator, variance.denominator
    )
    assert rounded == sys.float_info.max, (
        "the premise of the item: the rounded answer looks ordinary"
    )
    assert taxonomy._root_beyond_binary64(
        variance.numerator, variance.denominator
    ), "and the exact answer is out of range"


def test_the_out_of_range_boundary_is_exact_on_both_sides() -> None:
    largest = taxonomy.LARGEST_FINITE_SIGNIFICAND << (
        taxonomy.LARGEST_FINITE_EXPONENT
    )
    assert largest == int(sys.float_info.max)
    # A spread of exactly the largest finite number is representable and
    # must be published.
    assert not taxonomy._root_beyond_binary64(largest * largest, 1)
    # One unit beyond it, in the exact whole numbers, is not.
    assert taxonomy._root_beyond_binary64(largest * largest + 1, 1)


def test_an_ordinary_spread_says_so_rather_than_saying_nothing() -> None:
    # The flag is on every numeric column, not only the ones that
    # tripped it: a reader who has to infer "false" from a key that is
    # not there is a reader guessing.
    described = describe([str(index) for index in range(60)])
    assert described.details["std"] is not None
    assert described.details["std_unrepresentable"] is False


def test_a_spread_that_is_undefined_is_not_an_out_of_range_spread() -> None:
    # The two facts a generator must tell apart, in the one place they
    # can be confused: a single value has no sample spread at all.
    single = taxonomy._moments([5.0])
    assert single["std"] is None
    assert single["std_unrepresentable"] is False
    saturated = taxonomy._moments(
        [float(text) for text in SATURATING_SPREAD]
    )
    assert saturated["std"] is None
    assert saturated["std_unrepresentable"] is True


def test_the_out_of_range_spread_is_said_in_words() -> None:
    described = describe(SATURATING_SPREAD)
    spoken = [
        remark for remark in described.remarks if "spread" in remark
    ]
    assert spoken, "a null where a number belongs has to be explained"
    said = spoken[0]
    assert "too large for this file format to hold" in said
    assert "larger units" in said, "the remark must say what to do next"


def test_the_out_of_range_spread_reaches_the_profile_file(
    tmp_path: pathlib.Path,
) -> None:
    table = reading.read_table(
        str(
            fixtures.write(
                tmp_path,
                "spread.csv",
                fixtures.single_column_table("reading", SATURATING_SPREAD),
            )
        )
    )
    document = profile.build_document(table, SETTINGS, [])
    text = profile.serialize(document)
    column = document["columns"][0]
    assert column["std"] is None
    assert column["std_unrepresentable"] is True
    assert '"std": null' in text
    assert '"std_unrepresentable": true' in text


def test_the_out_of_range_spread_survives_the_command_line(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    table = fixtures.write(
        tmp_path,
        "spread.csv",
        fixtures.single_column_table("reading", SATURATING_SPREAD),
    )
    assert cli.main(["profile", str(table)]) == 0
    printed = capsys.readouterr().out
    document = json.loads(
        (tmp_path / "spread-profile.json").read_text(encoding="utf-8")
    )
    column = document["columns"][0]
    assert column["std"] is None
    assert column["std_unrepresentable"] is True
    assert "too large for this file format to hold" in printed


# -- P1-R6-F8: nothing infers the identifier role --------------------
#
# The contract, in one sentence: `profile_column` returns `identifier`
# when, and only when, it is told to. Three inferences stood here and
# each was defeated by an ordinary column of the same shape, the last by
# `1mg`; the tests below take the withdrawal from both sides -- no shape
# reaches the role by itself, and every shape reaches it when declared.


# Every shape the three defeated inferences argued about, plus the
# ordinary columns they were meant to spare. The battery is the test:
# a repair that closes one shape and leaves the next one open is what
# happened three times.
SHAPE_BATTERY = {
    "code words": RECORD_CODES,
    "letters only": ALL_LETTERS,
    "letter first": LETTER_FIRST,
    "letter last": LETTER_LAST,
    "letter inside": LETTER_INSIDE,
    "unit amounts": UNIT_AMOUNTS,
    "clock times": CLOCK_TIMES,
    "padded counts": PADDED_COUNTS,
    "mixed shapes": MIXED_SHAPES,
    "prefixed codes": [f"R{index:05d}" for index in range(240)],
    "hyphenated": [f"pa-{index:04d}" for index in range(50)],
    "currency": [f"${index}.50" for index in range(60)],
    "per cent": [f"{index}.5%" for index in range(60)],
    "clock with colon": [
        f"{hour:02d}:{minute:02d}"
        for hour in range(10)
        for minute in range(0, 60, 10)
    ],
    "sentences": [f"a sentence number {index} in words" for index in range(50)],
    "plain numbers": [str(index) for index in range(50)],
    "decimals": [f"{index}.5" for index in range(50)],
    "dates": [f"2024-01-{day:02d}" for day in range(1, 29)],
    "wide digits": [f"{index:08d}" for index in range(50)],
}


@pytest.mark.parametrize("shape", sorted(SHAPE_BATTERY))
def test_no_column_shape_reaches_the_identifier_role_by_itself(
    shape: str,
) -> None:
    # The whole of the repair, stated once over every shape the three
    # defeated inferences disagreed about. Uniqueness, a fixed width, a
    # leading zero, one token, the code alphabet, a letter first, a
    # letter anywhere: not one of them, alone or together, produces the
    # role.
    described = describe(SHAPE_BATTERY[shape])
    assert described.role != taxonomy.ROLE_IDENTIFIER, (
        f"{shape} was read as record numbers with nobody declaring it; "
        f"the values of a column cannot say what the column means"
    )


@pytest.mark.parametrize("shape", sorted(SHAPE_BATTERY))
def test_every_shape_reaches_the_role_when_it_is_declared(
    shape: str,
) -> None:
    # The other side: the option is the way in, for every shape, and it
    # publishes nothing whichever shape it was given.
    described = describe(SHAPE_BATTERY[shape], forced=True)
    assert described.role == taxonomy.ROLE_IDENTIFIER
    assert "you told synthtwin" in described.detection_evidence
    block = whole_block(described)
    for value in SHAPE_BATTERY[shape]:
        # A one- or two-character value is a substring of the counts
        # themselves ("0" is in "n_missing": 0), so searching for it
        # says nothing either way. The columns with values that short
        # are covered by the length and count assertions below.
        if len(value) < 4:
            continue
        assert value not in block


def test_the_two_columns_the_repair_could_not_tell_apart_agree() -> None:
    # `1mg` and `code1` are one token, all in the code alphabet, all
    # different, and each holds a letter. Round 6 read the second as
    # record numbers and therefore read the first as record numbers too.
    # Neither is read that way now, and both publish nothing.
    amounts = describe(UNIT_AMOUNTS)
    codes = describe(RECORD_CODES)
    # Asserted EQUAL rather than named: what the repair bought is that
    # the two are indistinguishable, not that they land anywhere in
    # particular. Both were free text until the affixed-number rule was
    # built and both are read by it now, together.
    assert amounts.role == codes.role
    assert amounts.details.keys() == codes.details.keys()
    for described, values in ((amounts, UNIT_AMOUNTS), (codes, RECORD_CODES)):
        block = whole_block(described)
        for value in values:
            assert value not in block


def test_a_declined_column_publishes_none_of_its_values() -> None:
    """The list is the columns that are still DECLINED.

    Clock times and padded counts left it when the fixed-width-code rule
    was deleted (review item P1-R6-F7): they are described as numbers
    now, and a numeric column publishes real minima and maxima by
    design (plan P1-D6), so asserting that none of their values appears
    would be asserting the opposite of the ratified taxonomy. Both
    shapes are covered on the declared path below, where nothing of them
    is published at all.
    """
    for values in (MIXED_SHAPES, ALL_LETTERS):
        described = describe(values)
        assert described.role == taxonomy.ROLE_TEXT
        block = whole_block(described)
        for value in values:
            assert value not in block, (
                f"{value!r} reached the profile from a column that "
                f"publishes nothing"
            )


def test_the_padded_column_is_read_by_the_ordinary_rules() -> None:
    """Corrected from `test_the_declined_column_is_still_kept_from_...`.

    The old test pinned the deleted rule: the padding was why `0930` was
    kept away from the numeric rules. Nothing may be routed by the WIDTH
    of its text (review item P1-R6-F7), so `0930` is read as nine
    hundred and thirty, and the person who knows the column holds codes
    declares it -- which withholds every value of it.
    """
    for values in (CLOCK_TIMES, PADDED_COUNTS):
        described = describe(values)
        assert described.role == taxonomy.ROLE_COUNT
        assert "percentiles" in described.details
        assert "leading zeros" not in described.detection_evidence
        declared = describe(values, forced=True)
        assert declared.role == taxonomy.ROLE_IDENTIFIER
        block = whole_block(declared)
        for value in values:
            assert value not in block


def test_the_ordinary_columns_are_untouched_by_the_withdrawal() -> None:
    # The repair that matters most is the one that changes nothing about
    # ordinary correct input. A withdrawal that swept real quantities,
    # dates or categories into a role publishing nothing would be worse
    # than the defect it closed.
    assert describe([str(index) for index in range(50)]).role == (
        taxonomy.ROLE_COUNT
    )
    assert describe(["52242", "10001", "90210"] * 20).role == (
        taxonomy.ROLE_COUNT
    )
    assert describe([f"{index}.5" for index in range(50)]).role == (
        taxonomy.ROLE_CONTINUOUS
    )
    assert describe([f"2024-01-{day:02d}" for day in range(1, 29)]).role == (
        taxonomy.ROLE_DATETIME
    )
    # Two cases moved with the ratified taxonomy rather than with this
    # withdrawal (review item P1-R6-F7): a zero-padded column is read by
    # the ordinary rules, because nothing may be routed by the width of
    # its text, and ten different labels are a set of categories only in
    # a column of a hundred values or more.
    padded = describe(["00501", "02139", "52242"] * 20)
    assert padded.role == taxonomy.ROLE_COUNT
    assert "fixed_width_code" not in padded.details
    assert describe([f"code{index}" for index in range(10)] * 20).role == (
        taxonomy.ROLE_CATEGORICAL
    )


def test_the_declined_column_says_what_was_not_assumed() -> None:
    # The withdrawal is stated, not silent. Every column that lands on
    # free text with all-different values carries one remark saying so.
    # Clock times and padded counts are not on this list any more: they
    # are described as numbers since the width rule was deleted (review
    # item P1-R6-F7), and the words a numeric column carries are checked
    # in tests/test_p1r6f8_identifier_evidence.py.
    for values in (UNIT_AMOUNTS, RECORD_CODES, ALL_LETTERS):
        described = describe(values)
        # THE WITHDRAWAL IS WHAT THIS TEST IS ABOUT, and it is stated
        # on every one of these shapes. What each shape's sentence says
        # about the CONSEQUENCE is its own role's business: two of the
        # three are affixed numbers now and publish a distribution, so
        # the free-text account of publishing nothing is false of them
        # and is asserted against rather than for.
        assert described.role != taxonomy.ROLE_IDENTIFIER
        spoken = [
            remark for remark in described.remarks if "--identifier" in remark
        ]
        assert spoken, "the withdrawal has to be stated, not silent"
        said = " ".join(spoken)
        assert "every value in this column is different" in said
        assert "--identifier NAME" in said
        assert "measurement" in said
        if described.role == taxonomy.ROLE_TEXT:
            assert "did NOT assume they are record numbers" in said
            assert "cannot tell" in said, "synthtwin must not claim to know"
            assert "Nothing from this column is published" in said
            assert "write them as plain numbers" in said
            continue
        assert "which keeps its distribution" in said
        assert "Nothing from this column is published" not in said
        assert "write them as plain numbers" not in said


def test_a_short_column_is_not_lectured_about_uniqueness() -> None:
    # Below `identifier_minimum_rows` "every value is different" says
    # nothing -- in a short column almost everything is -- so nothing is
    # said about it and the reader is not told to consider an option
    # they do not need.
    described = describe([f"code{index}" for index in range(5)])
    assert described.role == taxonomy.ROLE_TEXT
    assert not [
        remark for remark in described.remarks if "--identifier" in remark
    ]


def test_a_declared_column_states_who_decided() -> None:
    described = describe(RECORD_CODES, forced=True)
    assert described.detection_evidence == (
        "you told synthtwin that this column holds record numbers "
        "rather than measurements"
    )
    assert described.details["min_length"] == 5
    assert described.details["max_length"] == 6
    assert described.details["all_whole_numbers"] is False
    assert "levels" not in described.details
    assert "percentiles" not in described.details


def test_a_declared_column_of_digits_records_that_they_are_whole() -> None:
    # The identifier block still publishes what it always published:
    # counts and lengths, and whether every value is a whole number.
    described = describe(PADDED_COUNTS, forced=True)
    assert described.details["all_whole_numbers"] is True
    assert described.details["n_all_digits"] == len(PADDED_COUNTS)
    assert described.n_distinct == len(PADDED_COUNTS)


def test_a_measurement_column_keeps_its_distribution_end_to_end(
    tmp_path: pathlib.Path,
) -> None:
    # What the blocker cost: the whole distribution. Written as plain
    # numbers, with the unit in the column name, the same column is
    # described in full -- and the remark above is what tells the person
    # running the tool to do that.
    plain = [f"{index}" for index in range(1, 31)]
    table = reading.read_table(
        str(
            fixtures.write(
                tmp_path,
                "amount.csv",
                fixtures.single_column_table("amount_mg", plain),
            )
        )
    )
    document = profile.build_document(table, SETTINGS, [])
    column = document["columns"][0]
    assert column["role"] == taxonomy.ROLE_COUNT
    assert column["percentiles"]["p50"] is not None


def test_the_dose_and_the_record_column_agree_end_to_end(
    tmp_path: pathlib.Path,
) -> None:
    # The paired end-to-end case the item asked for: a dose column and a
    # true record column of the same lexical shape, side by side. Both
    # are described the same way, neither publishes a value, and naming
    # one settles that one alone.
    text = fixtures.rows_to_csv(
        ["dose", "record"],
        [
            [UNIT_AMOUNTS[index], RECORD_CODES[index]]
            for index in range(len(RECORD_CODES))
        ],
    )
    table = reading.read_table(str(fixtures.write(tmp_path, "pair.csv", text)))
    document = profile.build_document(table, SETTINGS, [])
    serialized = profile.serialize(document)
    roles = [column["role"] for column in document["columns"]]
    assert roles[0] == roles[1], "the pair must be read the same way"
    assert taxonomy.ROLE_IDENTIFIER not in roles
    for value in UNIT_AMOUNTS + RECORD_CODES:
        assert value not in serialized
    named = profile.build_document(table, SETTINGS, ["record"])
    named_roles = [column["role"] for column in named["columns"]]
    assert named_roles[0] != taxonomy.ROLE_IDENTIFIER
    assert named_roles[1] == taxonomy.ROLE_IDENTIFIER
    for value in UNIT_AMOUNTS + RECORD_CODES:
        assert value not in profile.serialize(named)


def test_the_two_padded_shapes_agree_end_to_end(
    tmp_path: pathlib.Path,
) -> None:
    """A clock column beside a padded record column of identical text.

    The property this file is about is unchanged and is the point of the
    pair: nothing in the VALUES tells the two apart, so they must be
    described identically until somebody says which is which. What
    changed with the deletion of the fixed-width-code rule (review item
    P1-R6-F7) is which description they share -- both are read by the
    ordinary rules now, and both publish their values -- and that
    declaring one of them still settles that one alone.
    """
    text = fixtures.rows_to_csv(
        ["at_time", "record"],
        [
            [CLOCK_TIMES[index], PADDED_COUNTS[index]]
            for index in range(len(PADDED_COUNTS))
        ],
    )
    table = reading.read_table(str(fixtures.write(tmp_path, "pair.csv", text)))
    document = profile.build_document(table, SETTINGS, [])
    roles = [column["role"] for column in document["columns"]]
    assert roles == [taxonomy.ROLE_COUNT, taxonomy.ROLE_COUNT]
    named = profile.build_document(table, SETTINGS, ["record"])
    named_roles = [column["role"] for column in named["columns"]]
    assert named_roles == [taxonomy.ROLE_COUNT, taxonomy.ROLE_IDENTIFIER]
    serialized = profile.serialize(named)
    for value in PADDED_COUNTS:
        assert value not in serialized, (
            "a declared column publishes none of its values"
        )


# -- P1-R6-F10: one classification per cell --------------------------


class _Counter:
    """Counts calls to one function without changing its answer."""

    def __init__(self, wrapped: typing.Any) -> None:
        self.wrapped = wrapped
        self.calls: list[str] = []

    def __call__(self, text: str, *rest: object) -> typing.Any:
        self.calls.append(text)
        return self.wrapped(text, *rest)


def _counted(
    monkeypatch: pytest.MonkeyPatch, name: str
) -> _Counter:
    counter = _Counter(getattr(parsing, name))
    monkeypatch.setattr(parsing, name, counter)
    return counter


def test_every_present_cell_is_classified_exactly_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    values = (
        [str(index) for index in range(40)]
        + ["(12)", "1e999", "(-3)", "1e-999", "not a number"]
        + ["", "NA"]
    )
    present = 45
    _counted(monkeypatch, "classify_number")
    record = _Counter(taxonomy._classify)
    monkeypatch.setattr(taxonomy, "_classify", record)
    described = describe(values)
    assert described.n_present == present
    # ONE RECORD PER PRESENT CELL, built once and read by every rule.
    # This is the control, and it is the one that carries the defect
    # the item was about: sentinel removal used to read the column a
    # second time, so every cell was classified twice and the two
    # were only trusted to agree.
    #
    # The raw count of parser calls used to stand beside it as a
    # coarser net. It cannot any more, and the reason is worth stating
    # rather than softening in silence: the affixed-number rule
    # searches a cell's SUBSTRINGS for the longest one that parses, to
    # find where the number inside `$1,200` begins. Those are not
    # re-readings of a cell -- a substring is a different string, and
    # no rule compares its answer with the cell's -- but for a
    # one-character cell the substring IS the cell, so no count can
    # tell the two apart. The record count can, and does.
    #
    # What replaces the coarse net is the test below, which pins the
    # search to the columns that need it.
    assert len(record.calls) == present, (
        "and one record per present cell, built once and read by all"
    )
    assert sorted(record.calls) == sorted(
        [value for value in values if value.strip() and value != "NA"]
    )


def test_the_substring_search_runs_only_where_earlier_rules_declined(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The affixed rule's search costs nothing on a column it never sees.

    It is rule 8, so every earlier rule gets the column first, and a
    column any of them claims must never pay for a search that cannot
    change its role. This is what the raw parser count used to protect
    and now protects deliberately: on a plain column of numbers the
    parser is asked exactly once per cell and not once more.
    """
    numbers = [str(index) for index in range(1, 61)]
    classify = _counted(monkeypatch, "classify_number")
    described = describe(numbers)
    assert described.role == taxonomy.ROLE_COUNT
    assert len(classify.calls) == len(numbers), (
        "a column the numeric rule claims must not pay for the affixed "
        "rule's substring search"
    )


def test_dropping_a_sentinel_does_not_classify_anything_twice(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Sentinel removal used to read the whole column a second time, so
    # every cell was classified twice and the two readings were only
    # trusted to agree.
    values = [str(index) for index in range(1, 61)] + ["-999"] * 20
    classify = _counted(monkeypatch, "classify_number")
    parse = _counted(monkeypatch, "parse_number")
    described = describe(values)
    assert described.missing_by_class[parsing.MISSING_NUMERIC_SENTINEL] == 20
    assert len(classify.calls) == 80, "80 present cells, 80 answers"
    # At most two readings of the number per cell: the one the parser
    # takes inside its own classification, which is parsing's business,
    # and the one this module takes to keep the value. The code this
    # replaces took five per numeric cell before the sentinel pass and
    # five more after it.
    assert len(parse.calls) <= 2 * 80


NOTATIONS = [
    "42",
    "-42",
    "+42",
    "0",
    "-0",
    "0.0",
    "(0)",
    "3.5",
    "-3.5",
    "(1,234.50)",
    "1,234,567.89",
    "  7  ",
    "1e5",
    "0e5",
    "1e999",
    "-1e999",
    "(1e999)",
    "1e-999",
    "-1e-999",
    "(-5)",
    "(+5)",
    "(-a)",
    "abc",
    "",
    "12mg",
]


@pytest.mark.parametrize("text", NOTATIONS)
def test_the_one_record_agrees_with_the_parser_on_every_notation(
    text: str,
) -> None:
    # The record derives the sign and the whole-number answer from the
    # one classification instead of asking again. This is the test that
    # keeps that derivation honest: it must say exactly what asking
    # again would have said, on every notation the reader accepts.
    cell = taxonomy._classify(text)
    assert cell.kind == parsing.classify_number(text)
    assert cell.sign == parsing.numeric_sign(text)
    assert cell.whole == parsing.numeric_whole(text)
    if cell.kind == parsing.NUMBER:
        assert cell.value == parsing.parse_number(text)
    else:
        assert cell.value is None


def _seconds(values: list[str]) -> float:
    """How long describing one column of ``values`` takes."""
    started = time.perf_counter()
    taxonomy.profile_column(
        "column", 1, values, len(values), SETTINGS, False
    )
    return time.perf_counter() - started


def test_a_large_numeric_column_is_not_built_quadratically() -> None:
    # Each numeric value used to be added with `numbers = numbers +
    # [parsed]`, copying every value accumulated so far: doubling the
    # column quadrupled the work, and 80,000 numbers took seconds of
    # pure copying. Growth is measured rather than a wall-clock ceiling
    # asserted, so the test means the same thing on a slow machine.
    small = [str(index) for index in range(20000)]
    large = [str(index) for index in range(80000)]
    _seconds(small[:2000])  # warm up: first-call costs are not growth
    short = _seconds(small)
    long = _seconds(large)
    assert short > 0.0
    ratio = long / short
    assert ratio < 8.0, (
        f"four times the values took {ratio:.1f} times the work; "
        f"proportional growth is about 4 and quadratic growth is about 16"
    )


def test_a_column_of_twenty_thousand_values_completes() -> None:
    values = [f"{index}.5" for index in range(20000)]
    described = describe(values)
    assert described.role == taxonomy.ROLE_CONTINUOUS
    assert described.n_present == 20000
    assert described.details["percentiles"]["max"] == 19999.5


def test_a_large_date_column_is_not_built_quadratically() -> None:
    def dates(count: int) -> list[str]:
        return [
            f"2024-{(index % 12) + 1:02d}-{(index % 28) + 1:02d}"
            for index in range(count)
        ]

    _seconds(dates(2000))
    short = _seconds(dates(10000))
    long = _seconds(dates(40000))
    assert short > 0.0
    assert long / short < 8.0


def test_the_counts_still_reconcile_after_the_one_record_change() -> None:
    values = (
        [str(index) for index in range(30)]
        + ["1e999", "1e-999", "(-3)", "word", "  "]
    )
    described = describe(values)
    assert (
        described.n_numeric
        + described.n_out_of_range
        + described.n_contradictory
        + described.n_not_numeric
        == described.n_present
    )
    assert described.n_present + described.n_missing == len(values)
