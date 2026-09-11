"""P1-R6-F8, round four: the identifier role is declared, never inferred.

Three repairs were tried and three were defeated by the column next
door. Round 1 read uniqueness plus guards as a record number, and a
column of prices went with it. Round 5 moved the reading to last place,
and zero-padded clock times went with it. Round 6 required a letter --
first, then anywhere in the value -- and `1mg` went with it, because
`1mg` holds the letters m and g and so a amount column became a column of
record numbers and lost its distribution.

The fourth repair is a deletion. `1mg` and `code1` are the same shape of
string; what separates a amount from a label is what the column MEANS, and
no property of the values carries it. So nothing infers the role any
more: `identifier` happens when the person who owns the table writes
`--identifier NAME`, and never otherwise. A column that would once have
been inferred falls to free text, which publishes NO value either -- so
the conservative answer is also the safe one -- and says in plain words
that synthtwin did not assume, and how to declare it if it should be
declared.

The two properties this file exists to pin:

* nothing that only READS values can produce the role. Asserted over a
  battery of shapes rather than over the one column a reviewer sent,
  because "closed on the branch that was demonstrated" is how the defect
  survived three rounds;
* the role is fully alive through the option, end to end, through the
  real CLI, publishing nothing.

Every case is paired: the measurement and the record code with the same
lexical shape, side by side in one table, treated identically until
somebody says which is which.
"""

import json
import pathlib
import random

import pytest

import fixtures
from synthtwin import profile, reading, summary, taxonomy
from synthtwin.cli import main

SETTINGS = taxonomy.Settings()

# The item's own reproduction: an amount with its unit written after the
# number. Round 6 read this as record numbers.
UNIT_AMOUNTS = [f"{index}mg" for index in range(1, 31)]

# A real record-code column of the SAME shape: one token, code alphabet,
# all different, letters and digits mixed. Nothing in the values tells
# these two columns apart, which is the whole argument.
CODE_WORDS = [f"code{index}" for index in range(1, 31)]

# A column that is STILL declined, for the tests about what a decline
# says. `1mg` and `code1` stopped being declined when the
# affixed-number rule was built -- they are read now, which is the
# point of that rule -- so the tests about the language of a DECLINE
# need a column no rule reads: prose, varying in shape, wearing no
# shared text and holding no number to find.
DECLINED_PROSE = [
    f"{opening} {middle} {ending}"
    for opening in ("seen", "review", "pending")
    for middle in ("in clinic", "by phone", "at home")
    for ending in ("no change", "improving", "worse", "unclear")
]

# The shapes the earlier rounds argued over.
CLOCK_TIMES = [
    f"{hour:02d}{minute:02d}"
    for hour in range(24)
    for minute in range(0, 60, 10)
]
PADDED_NUMBERS = [f"{index:06d}" for index in range(50)]
PREFIXED_CODES = [f"R{index:05d}" for index in range(240)]
ACCESSION_CODES = [f"2024-ab-{index:04d}" for index in range(60)]


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
    """Everything about one column that reaches a file, as one string."""
    return (
        json.dumps(profile._column_block(described), sort_keys=True)
        + " ".join(described.remarks)
        + " ".join(described.publication_notes)
    )


# -- nothing infers the role ------------------------------------------


ALL_SHAPES = {
    "unit amounts": UNIT_AMOUNTS,
    "code words": CODE_WORDS,
    "prefixed codes": PREFIXED_CODES,
    "accession codes": ACCESSION_CODES,
    "clock times": CLOCK_TIMES,
    "padded numbers": PADDED_NUMBERS,
    "letters only": [f"zz{first}{second}" for first in "abcde"
                     for second in "abcdef"],
    "letter last": [f"{index}a" for index in range(50)],
    "letter first": [f"a{index}" for index in range(50)],
    "underscored": [f"lot_{index:04d}" for index in range(50)],
    "currency": [f"${index}.50" for index in range(60)],
    "per cent": [f"{index}.5%" for index in range(60)],
    "clock with colon": [f"{hour:02d}:{minute:02d}" for hour in range(10)
                         for minute in range(0, 60, 10)],
    "plain numbers": [str(index) for index in range(50)],
    "decimals": [f"{index}.5" for index in range(50)],
    "dates": [f"2024-01-{day:02d}" for day in range(1, 29)],
    "sentences": [f"a sentence number {index} in words" for index in range(50)],
    "wide digits": [f"{index:08d}" for index in range(50)],
}


@pytest.mark.parametrize("shape", sorted(ALL_SHAPES))
def test_the_rules_never_reach_the_identifier_role(shape: str) -> None:
    described = describe(ALL_SHAPES[shape])
    assert described.role != taxonomy.ROLE_IDENTIFIER, (
        f"{shape} was called record numbers with nobody declaring it"
    )


def test_no_generated_column_of_any_shape_reaches_the_role() -> None:
    # The battery above is a list somebody wrote; this is the same
    # property over columns nobody chose. Every earlier round closed the
    # shapes it had been shown and left the neighbouring shape open, so
    # the claim worth making is about all of them at once: with nothing
    # declared, no column of any shape comes back as record numbers.
    rng = random.Random(20260808)
    alphabets = ("0123456789", "abcdef", "abc123", "0123-_", "xy09-")
    for _run in range(400):
        alphabet = alphabets[rng.randrange(len(alphabets))]
        width = rng.randint(1, 12)
        n_rows = rng.randint(1, 120)
        pool = rng.randint(1, n_rows)
        values = [
            "".join(
                alphabet[rng.randrange(len(alphabet))] for _ in range(width)
            )
            for _index in range(pool)
        ]
        column = [values[rng.randrange(len(values))] for _row in range(n_rows)]
        described = describe(column)
        assert described.role != taxonomy.ROLE_IDENTIFIER, (
            f"a column of {column[:3]}... was called record numbers with "
            f"nobody declaring it"
        )
        assert described.role in taxonomy.ROLES


def test_the_amount_and_the_code_column_are_described_identically() -> None:
    # The pair the item asked for, at the level of the description
    # itself: same role, same published fields. A repair that told them
    # apart would be the fourth defeated guess.
    amount = describe(UNIT_AMOUNTS)
    codes = describe(CODE_WORDS)
    # The role is asserted EQUAL rather than named, because what this
    # item bought is that the two are indistinguishable -- not that
    # they land anywhere in particular. They landed on free text until
    # the affixed-number rule was built, and they land together on it
    # now: `1mg` and `code1` are one shape of string, so a rule that
    # reads one reads the other, and the remark both carry says so.
    assert amount.role == codes.role
    assert sorted(amount.details) == sorted(codes.details)
    # The remarks are compared by FORM rather than by text. They were
    # identical while both columns were declined and published nothing.
    # Now each names its own affix pair, and the sentences differ in
    # more than the spelling: `1mg` wears its text after the number and
    # `code1` before it, so even the clause order differs. That is a
    # fact about the two columns, not a guess synthtwin made about
    # which is which. What this item bought is that synthtwin reaches
    # for the SAME sentences about both, and the forms are what carry
    # that.
    assert [remark.form for remark in amount.remarks] == [
        remark.form for remark in codes.remarks
    ]


@pytest.mark.parametrize("shape", sorted(ALL_SHAPES))
def test_a_declined_column_publishes_none_of_its_values(shape: str) -> None:
    values = ALL_SHAPES[shape]
    described = describe(values)
    if described.role != taxonomy.ROLE_TEXT:
        return
    block = whole_block(described)
    for value in values:
        assert value not in block, (
            f"{value!r} reached the profile from a column that publishes "
            f"nothing"
        )


def test_the_withdrawal_costs_no_ordinary_column_its_distribution() -> None:
    """Corrected where the taxonomy changed (review item P1-R6-F7).

    The property is unchanged: the withdrawal of identifier inference
    must cost no ordinary column its distribution, and quantities, dates
    and repeating labels are all described exactly as before. Two of the
    old cases moved with the ratified taxonomy rather than with this
    withdrawal, and they are the tests below: the padded column, because
    nothing may be routed by the width of its text, and the ten-label
    column, because a set of categories may hold at most a tenth of the
    values present.
    """
    numbers = describe([str(index) for index in range(50)])
    assert numbers.role == taxonomy.ROLE_COUNT
    assert numbers.details["percentiles"]["max"] == 49.0
    measured = describe([f"{index}.5" for index in range(50)])
    assert measured.role == taxonomy.ROLE_CONTINUOUS
    assert measured.details["percentiles"]["min"] == 0.5
    dates = describe([f"2024-01-{day:02d}" for day in range(1, 29)])
    assert dates.role == taxonomy.ROLE_DATETIME
    unpadded = describe(["52242", "10001", "90210"] * 20)
    assert unpadded.role == taxonomy.ROLE_COUNT
    assert unpadded.details["percentiles"]["max"] == 90210.0
    repeating = describe([f"code{index}" for index in range(10)] * 20)
    assert repeating.role == taxonomy.ROLE_CATEGORICAL


def test_the_padded_column_is_read_by_the_ordinary_rules_now() -> None:
    """Corrected from `test_the_padded_column_is_still_kept_away_...`.

    The old test pinned the fixed-width-code rule: `0930` must not fall
    through to the numeric rules and be averaged as nine hundred and
    thirty. Review item P1-R6-F7 deletes that rule -- nothing may be
    routed by the WIDTH of its text -- so `0930` IS read as nine hundred
    and thirty, and that is the ratified answer rather than an accident:
    the identical text is a clock, a padded account number and a postal
    code, and no property of the values says which. What the person is
    owed instead is the option, and every value of the column being
    different is what prompts it.
    """
    described = describe(CLOCK_TIMES)
    assert described.role == taxonomy.ROLE_COUNT
    assert described.details["percentiles"]["max"] == 2350.0
    said = " ".join(described.remarks)
    assert "every value in this column is different" in said
    assert "--identifier NAME" in said
    declared = describe(CLOCK_TIMES, forced=True)
    assert declared.role == taxonomy.ROLE_IDENTIFIER
    assert "percentiles" not in declared.details
    for value in CLOCK_TIMES:
        assert value not in whole_block(declared)


def test_a_ten_label_column_needs_a_hundred_rows_for_the_ceiling() -> None:
    # The category ceiling is a tenth of the values present, so ten
    # different labels are a set of categories in two hundred rows and
    # are not in sixty. The shorter column publishes nothing at all
    # rather than the labels that happen to clear the small-cell floor.
    long = describe([f"code{index}" for index in range(10)] * 20)
    short = describe([f"code{index}" for index in range(10)] * 6)
    assert long.role == taxonomy.ROLE_CATEGORICAL
    # The shorter column is past the ceiling, so the categorical rule
    # declines it -- which is what this test is about, and it is
    # unchanged. What happens AFTER the decline moved: it used to fall
    # to free text and publish nothing, and the affixed-number rule now
    # reads it as a number wearing `code`. Either way it publishes no
    # LEVELS, which is the assertion this test rests on.
    assert short.role != taxonomy.ROLE_CATEGORICAL
    assert "levels" not in short.details


# -- what the declined column SAYS ------------------------------------


@pytest.mark.parametrize(
    "shape",
    # The shapes that still land on free text. Clock times and padded
    # numbers left this list when the fixed-width-code rule was deleted
    # (review item P1-R6-F7): they are described as numbers now, and the
    # remark they carry is the numeric one, checked in the test below.
    ["unit amounts", "code words", "accession codes", "prefixed codes"],
)
def test_the_remark_states_the_withdrawal_in_plain_language(
    shape: str,
) -> None:
    described = describe(ALL_SHAPES[shape])
    # These four shapes are read by the affixed-number rule now, and
    # what the reader is owed moved with them. The WITHDRAWAL is the
    # same and is still stated: no property of the values tells a dose
    # from a code, so `--identifier` is named either way. What may NOT
    # be carried across is the free-text path's account of what was
    # done about it -- "Nothing from this column is published", and the
    # advice to rewrite the values so that "their distribution will be
    # described" -- because this block publishes the distribution. A
    # test that went on asserting those two was asserting that a false
    # sentence is printed.
    assert described.role != taxonomy.ROLE_IDENTIFIER
    spoken = [
        remark for remark in described.remarks if "--identifier" in remark
    ]
    assert spoken, "the withdrawal has to be stated, not silent"
    said = " ".join(spoken)
    assert "every value in this column is different" in said
    assert "--identifier NAME" in said
    assert "which keeps its distribution" in said
    # ...and the direction the earlier rounds got wrong: a measurement
    # must not be pushed into the role either. On this role the
    # sentence that says so is the column's own remark.
    assert "codes rather than measurements" in said
    # THE TWO CLAUSES THAT WOULD BE FALSE HERE.
    assert "Nothing from this column is published" not in said, (
        "a block publishing a full ladder must not tell its reader "
        "that nothing of the column is published"
    )
    assert "write them as plain numbers" not in said, (
        "these values are already described as numbers; telling the "
        "reader to rewrite them to get a distribution they already "
        "have is advice about a column they do not hold"
    )


@pytest.mark.parametrize("shape", ["clock times", "padded numbers"])
def test_a_numeric_column_of_codes_still_carries_the_option(
    shape: str,
) -> None:
    # The other side of deleting the width rule: these columns are
    # described as numbers, so the words they carry are the numeric
    # ones -- the role was not assumed from anything, and --identifier
    # is how a person says the column really holds record numbers.
    described = describe(ALL_SHAPES[shape])
    assert described.role in (
        taxonomy.ROLE_COUNT, taxonomy.ROLE_CONTINUOUS,
    )
    spoken = [
        remark for remark in described.remarks if "--identifier" in remark
    ]
    assert spoken, "the option has to be offered, not assumed away"
    said = spoken[0]
    assert "every value in this column is different" in said
    assert "not treated as evidence of anything" in said
    assert "--identifier NAME" in said


def test_the_remark_is_one_paragraph_of_plain_words() -> None:
    said = next(
        remark
        for remark in describe(UNIT_AMOUNTS).remarks
        if "--identifier" in remark
    )
    assert "\n" not in said, "one paragraph, so any front end can wrap it"
    for jargon in ("free_text", "ROLE_", "taxonomy", "_all_different"):
        assert jargon not in said


# -- the declared path, which is now the only path --------------------


@pytest.mark.parametrize("shape", sorted(ALL_SHAPES))
def test_declaring_the_column_settles_any_shape(shape: str) -> None:
    described = describe(ALL_SHAPES[shape], forced=True)
    assert described.role == taxonomy.ROLE_IDENTIFIER
    assert "you told synthtwin" in described.detection_evidence
    assert "percentiles" not in described.details
    assert "levels" not in described.details


def test_the_declared_column_records_what_it_always_recorded() -> None:
    # The role must still be worth declaring: the profile keeps the
    # counts, the lengths and the whole-number answer that Phase 2 needs
    # in order to invent stand-in record numbers of the right shape.
    described = describe(PREFIXED_CODES, forced=True)
    assert described.details["min_length"] == 6
    assert described.details["max_length"] == 6
    assert described.details["all_whole_numbers"] is False
    assert described.details["n_code_alphabet"] == len(PREFIXED_CODES)
    assert described.n_distinct == len(PREFIXED_CODES)
    assert described.n_present == len(PREFIXED_CODES)
    digits = describe(PADDED_NUMBERS, forced=True)
    assert digits.details["all_whole_numbers"] is True
    assert digits.details["n_all_digits"] == len(PADDED_NUMBERS)


def test_a_declared_column_publishes_none_of_its_values() -> None:
    for values in (CODE_WORDS, UNIT_AMOUNTS, PADDED_NUMBERS, CLOCK_TIMES):
        block = whole_block(describe(values, forced=True))
        for value in values:
            assert value not in block


def test_declaring_beats_every_rule_that_would_have_published() -> None:
    # RULE 0 still outranks the roles that publish values: eleven
    # identical labels are a constant, and a declared column of them
    # publishes nothing.
    described = describe(["amber-id"] * 11, forced=True)
    assert described.role == taxonomy.ROLE_IDENTIFIER
    assert "amber-id" not in whole_block(described)
    numbers = describe([str(index) for index in range(50)], forced=True)
    assert numbers.role == taxonomy.ROLE_IDENTIFIER
    assert "percentiles" not in numbers.details


# -- end to end, through the profile document -------------------------


def test_the_paired_columns_agree_end_to_end(tmp_path: pathlib.Path) -> None:
    # The item's required closure: unit-bearing measurements and true
    # record IDs of the same lexical shape, in one table. Undeclared,
    # both are described the same way and neither publishes a value;
    # declared, one of them -- and only one -- becomes record numbers.
    text = fixtures.rows_to_csv(
        ["amount", "record"],
        [
            [UNIT_AMOUNTS[index], CODE_WORDS[index]]
            for index in range(len(CODE_WORDS))
        ],
    )
    table = reading.read_table(str(fixtures.write(tmp_path, "pair.csv", text)))
    document = profile.build_document(table, SETTINGS, [])
    serialized = profile.serialize(document)
    roles = [column["role"] for column in document["columns"]]
    assert roles[0] == roles[1], "the pair must be read the same way"
    assert taxonomy.ROLE_IDENTIFIER not in roles
    for value in UNIT_AMOUNTS + CODE_WORDS:
        assert value not in serialized

    named = profile.build_document(table, SETTINGS, ["record"])
    named_roles = [column["role"] for column in named["columns"]]
    assert named_roles[0] != taxonomy.ROLE_IDENTIFIER
    assert named_roles[1] == taxonomy.ROLE_IDENTIFIER
    assert named["settings"]["forced_identifiers"] == ["record"]
    for value in UNIT_AMOUNTS + CODE_WORDS:
        assert value not in profile.serialize(named)


def test_the_amount_column_is_never_declared_by_accident(
    tmp_path: pathlib.Path,
) -> None:
    # Declaring the record column must not drag its neighbour with it.
    text = fixtures.rows_to_csv(
        ["amount", "record"],
        [
            [UNIT_AMOUNTS[index], CODE_WORDS[index]]
            for index in range(len(CODE_WORDS))
        ],
    )
    table = reading.read_table(str(fixtures.write(tmp_path, "pair.csv", text)))
    named = profile.build_document(table, SETTINGS, ["record"])
    amount = named["columns"][0]
    assert amount["role"] != taxonomy.ROLE_IDENTIFIER
    assert "--identifier" in " ".join(amount["remarks"])


def test_the_measurement_written_plainly_keeps_its_distribution(
    tmp_path: pathlib.Path,
) -> None:
    # What the remark asks for, and what it buys: the same amounts written
    # as plain numbers with the unit in the column name are described in
    # full.
    text = fixtures.single_column_table(
        "amount_mg", [f"{index}" for index in range(1, 31)]
    )
    table = reading.read_table(str(fixtures.write(tmp_path, "amount.csv", text)))
    column = profile.build_document(table, SETTINGS, [])["columns"][0]
    assert column["role"] == taxonomy.ROLE_COUNT
    assert column["percentiles"]["min"] == 1.0
    assert column["percentiles"]["max"] == 30.0


# -- end to end, through the summary a person reads -------------------


def test_the_summary_names_the_declined_column_in_plain_language(
    tmp_path: pathlib.Path,
) -> None:
    table = reading.read_table(
        str(
            fixtures.write(
                tmp_path,
                "amount.csv",
                fixtures.single_column_table("comment", DECLINED_PROSE),
            )
        )
    )
    text = summary.render(
        profile.build_document(table, SETTINGS, []), "read as UTF-8."
    )
    assert "free text" in text
    assert "free_text" not in text, "the role name must not leak as jargon"
    assert "record numbers or codes" not in text, (
        "nothing may be called a record number that nobody declared"
    )
    assert "did NOT assume they are record numbers" in text
    assert "--identifier NAME" in text
    for value in DECLINED_PROSE:
        assert value not in text


def test_the_summary_names_the_declared_role_in_plain_language(
    tmp_path: pathlib.Path,
) -> None:
    table = reading.read_table(
        str(
            fixtures.write(
                tmp_path,
                "codes.csv",
                fixtures.single_column_table("record", CODE_WORDS),
            )
        )
    )
    text = summary.render(
        profile.build_document(table, SETTINGS, ["record"]), "read as UTF-8."
    )
    assert "record numbers or codes" in text
    assert "read as: identifier" not in text, (
        "the role name must not leak as jargon"
    )
    # The words say WHO decided, because nothing else can decide it.
    assert "you named this column" in text
    assert "synthtwin never decides this for itself" in text
    for value in CODE_WORDS:
        assert value not in text


# -- end to end, through the real command -----------------------------


def test_the_real_command_declines_and_declares(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # An ordinary two-column CSV, profiled by the real CLI exactly as a
    # person would type it -- first with no options at all, then with the
    # record column declared.
    text = fixtures.rows_to_csv(
        ["amount", "record"],
        [
            [UNIT_AMOUNTS[index], CODE_WORDS[index]]
            for index in range(len(CODE_WORDS))
        ],
    )
    table = fixtures.write(tmp_path, "clinic.csv", text)
    assert main(["profile", str(table)]) == 0
    printed = capsys.readouterr().out
    written = (tmp_path / "clinic-profile.txt").read_text(encoding="utf-8")
    document = json.loads(
        (tmp_path / "clinic-profile.json").read_text(encoding="utf-8")
    )
    # Both columns are read the same way, and neither is called record
    # numbers with nobody declaring it. Which role they take is the
    # affixed-number rule's business and is asserted where that rule is
    # tested; what matters HERE is that the command declines to guess.
    roles = [column["role"] for column in document["columns"]]
    assert roles[0] == roles[1]
    assert "identifier" not in roles
    for shown in (printed, written):
        # THE DECLINE IS STATED IN THE WORDS THE ROLE OWNS. Both
        # columns are read by the affixed-number rule, whose own remark
        # names `--identifier` and says the numbers were described as
        # quantities -- so the reader is told the same thing the
        # free-text sentence used to tell them, without the clauses
        # that would be false of a block publishing a distribution.
        assert "--identifier" in shown
        assert "codes rather than measurements" in shown
        assert "Nothing from this column is published" not in shown
        for value in UNIT_AMOUNTS + CODE_WORDS:
            assert value not in shown

    assert main(["profile", str(table), "--identifier", "record"]) == 0
    printed = capsys.readouterr().out
    document = json.loads(
        (tmp_path / "clinic-profile.json").read_text(encoding="utf-8")
    )
    roles = {column["name"]: column["role"] for column in document["columns"]}
    # The declared column takes the identifier role and the undeclared
    # one does not: that is the whole assertion. The undeclared
    # column's own role is the affixed-number rule's business, and
    # pinning it here would make this test fail whenever that rule
    # changes something it has no opinion about.
    assert roles["record"] == "identifier"
    assert roles["amount"] != "identifier"
    assert "record numbers or codes" in printed
    for value in UNIT_AMOUNTS + CODE_WORDS:
        assert value not in printed


def test_the_real_command_still_profiles_a_plain_table(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # Ordinary correct input, through the real command: a table of
    # numbers, labels and dates keeps every statistic it had before.
    rows = [
        [str(index), fixtures.LABELS[index % 5], f"2024-01-{index % 28 + 1:02d}"]
        for index in range(60)
    ]
    table = fixtures.write(
        tmp_path, "plain.csv", fixtures.rows_to_csv(["n", "group", "day"], rows)
    )
    assert main(["profile", str(table)]) == 0
    out = capsys.readouterr().out
    document = json.loads(
        (tmp_path / "plain-profile.json").read_text(encoding="utf-8")
    )
    roles = {column["name"]: column["role"] for column in document["columns"]}
    assert roles == {
        "n": "count", "group": "categorical", "day": "datetime",
    }
    counts = document["columns"][0]
    assert counts["percentiles"]["max"] == 59.0
    assert counts["mean"] is not None
    assert "COLUMNS, ONE BY ONE" in out
    assert "identifier" not in out.replace("--identifier", "")
