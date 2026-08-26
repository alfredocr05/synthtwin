"""What synthtwin cannot know, and how it asks.

THE ONE THING THE VALUES CANNOT SETTLE (plan P4-D19). A column of
`213`, `08`, `141` is a column of vaccine codes or a column of counts,
and the two are written identically. Read as counts it publishes an
average, a smallest and a largest -- all three meaningless for a code,
and all three REAL CODES besides -- and its twin loses the leading
zeros, so `08` comes back as `8` and a reader that splits on width
breaks. Read as codes it keeps every spelling exactly and publishes how
many rows carried each, which is what the column is for.

`taxonomy._decide`'s RULE 5 has said since review item P1-R6-F7 that
this cannot be settled from the values: it deleted a rule that guessed
codes from their width, recorded that "nothing may be routed by the
WIDTH of its text", and named the owner of the table as the only one
who knows. This module is the other half of that sentence. It does not
decide anything. It works out which columns are worth ASKING about,
and the person answers.

THE DIFFERENCE BETWEEN ROUTING AND ASKING, because the deleted rule
looked at exactly the same evidence this module looks at. A rule that
ROUTES on padding is wrong because it is a guess presented as a fact,
and a wrong guess is silent. Choosing which QUESTION to put to a person
is not a guess: the person answers, the answer is recorded in the
profile's `forced_codes`, and a wrong signal here costs one skipped
question rather than a wrong description. That is why the evidence the
deleted rule used is admissible here and inadmissible there.

WHAT IS NOT ASKED ABOUT, stated so nobody reads silence as clearance.
Only the roles that publish numeric statistics over the cells are
reached -- `count`, `continuous` and `numeric_unrepresentable`. A
column of `HCC19` lands on `affixed_number`, which publishes
percentiles over the numeric CORE and is as wrong for a code as the
numeric roles are; it is not asked about because `$1,200` and `45%`
land there too and are genuine measurements, so there is no signal that
separates them. `--code` is accepted for such a column and does the
right thing with it; it is the asking that stops short, not the fix.
"""

import dataclasses

from . import taxonomy

# The roles that publish a ladder of real values. A column here that is
# really a coding system publishes real codes as its endpoints.
NUMERIC_ROLES = (
    taxonomy.ROLE_COUNT,
    taxonomy.ROLE_CONTINUOUS,
    taxonomy.ROLE_UNREPRESENTABLE,
)

# The two readings a person is offered, and the third that already had
# an option. The words are the ones the help screen uses.
ANSWER_MEASUREMENT = "measurement"
ANSWER_CODE = "code"
ANSWER_IDENTIFIER = "identifier"

# Why a column was worth asking about. Each is shown to the person, so
# each says what was SEEN and not what it was taken to mean.
BECAUSE_PADDED = "padded"
BECAUSE_FIXED_WIDTH = "fixed-width"

# A fixed-width all-digit column is asked about from three digits up.
# Below that the shape is too common to mean anything: a column of `1`
# to `9` is one digit wide and is almost always a count, and asking
# about every such column is the noise that makes a person stop reading
# the questions.
_NARROWEST_FIXED_WIDTH = 3


def _is_plain_whole_number(text: str) -> bool:
    """True where the text is digits and nothing else.

    No sign, no point, no exponent, no space. Those are how a
    MEASUREMENT is written; a code is bare digits. The test is on
    fixed ASCII rather than `str.isdigit`, for the reason
    `parsing._is_a_digit` gives: the five supported Pythons carry five
    Unicode databases, and `str.isdigit` is true of characters this
    project must not read as figures.
    """
    if not text:
        return False
    for character in text:
        if not ("0" <= character <= "9"):
            return False
    return True


def why_worth_asking(values: "list[str]") -> "str | None":
    """The reason to ask about this column, or None to stay quiet.

    Guarantees:

    - Inputs: every present cell of one column, as text.
    - Determinism: a fixed function of those cells.
    - Errors raised: none.
    - Boundary: returns a REASON, never a value. Nothing a cell holds
      leaves this function.

    Two signals, and a column showing either is asked about:

    - a leading zero on a cell more than one character long. A
      measurement is not padded -- nobody writes an age as `08` -- so
      padding is the strongest thing a column of digits can show.
    - every cell exactly the same number of digits, at least three of
      them. Fixed width is what a code has and a measurement does not:
      real quantities spread across widths.
    """
    if not values:
        return None
    for value in values:
        if not _is_plain_whole_number(value):
            return None
    for value in values:
        if len(value) > 1 and value[0] == "0":
            return BECAUSE_PADDED
    widths = {len(value) for value in values}
    if len(widths) == 1:
        only = sorted(widths)[0]
        if only >= _NARROWEST_FIXED_WIDTH:
            return BECAUSE_FIXED_WIDTH
    return None


@dataclasses.dataclass(frozen=True)
class Question:
    """One column synthtwin cannot read on its own, ready to be put.

    It carries the column's name, the role it landed on, the reason it
    is being asked about, and a few of its values to show the person.
    The values are shown because the question is unanswerable without
    them: nobody can say whether a column is codes from its name.

    A dataclass rather than a written constructor, for the reason
    `taxonomy.Settings` gives: the offline policy accepts no
    double-underscore name in this source (plan D6.2).
    """

    name: str
    role: str
    reason: str
    examples: "list[str]"


def _examples(values: "list[str]", most: int = 4) -> "list[str]":
    """A few different values of the column, in the order they appear.

    Different ones, because four copies of the same value show a person
    nothing. In file order, because that is reproducible and because
    the first rows are what they would see opening the file.
    """
    shown: list[str] = []
    for value in values:
        if value not in shown:
            shown = shown + [value]
        if len(shown) == most:
            return shown
    return shown


def questions_for(
    document: "dict[str, object]",
    table_columns: "list[list[str]]",
    settings: taxonomy.Settings,
    already: "list[str]",
) -> "list[Question]":
    """Every column worth asking about, in the table's own order.

    Guarantees:

    - Inputs: a profile document, the table's columns as text in the
      same order, the settings that produced it, and every column name
      already declared with `--code` or `--identifier`.
    - Determinism: a fixed function of the arguments.
    - Errors raised: none.
    - Boundary: opens no file and prints nothing. It decides what would
      be asked; whether anything is asked is the caller's.

    A column already declared is never asked about: the person has
    answered, and asking again would say their answer had not been
    heard.
    """
    blocks = document["columns"]
    if not isinstance(blocks, list):
        return []
    asked: list[Question] = []
    position = 0
    for block in blocks:
        if not isinstance(block, dict):
            position = position + 1
            continue
        name = f"{block['name']}"
        role = f"{block['role']}"
        if role not in NUMERIC_ROLES or name in already:
            position = position + 1
            continue
        if position >= len(table_columns):
            position = position + 1
            continue
        present, _absent = taxonomy.split_missing(
            table_columns[position], settings
        )
        reason = why_worth_asking(present)
        if reason is not None:
            asked = asked + [
                Question(name, role, reason, _examples(present))
            ]
        position = position + 1
    return asked
