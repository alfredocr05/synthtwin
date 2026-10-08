"""What synthtwin cannot know, and how it asks.

THE ONE THING THE VALUES CANNOT SETTLE (plan P4-D19). A column of
`213`, `08`, `141` is a column of vaccine codes or a column of counts,
and the two are written identically. Read as counts it publishes an
average, a spread and points along a range -- all of them meaningless
for a code, and the boundary each of its tails is measured from IS a
REAL CODE besides -- and its twin loses the leading zeros, so `08`
comes back as `8` and a reader that splits on width
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

AND THE RULING TO ROUTE ON PADDING WAS MEASURED AND WITHDRAWN
(A-P4-59 clause 3; amendment A-P4-60, 2026-09-10). It said an
unanswered column of figures should be read as CODES. Built, it was
run against the suite, and three things came back that no argument
survives:

* **The owner has already settled this, the other way.** Review item
  P1-R6-F7 deleted a rule that routed on width AND ON THE LEADING
  ZERO, and the owner settled the policy that replaced it. The test
  that records it -- `tests/test_p1r6f7_one_policy.py` -- names
  `00501` and `000000`..`000049` among the columns that must land
  where the ordinary rules put them. A leading zero is not a signal
  outside that finding; it is half of what the finding is about.
* **The harm it was meant to prevent is already prevented, and better.**
  Plan decision P4-D14 publishes the FIELD WIDTH of a padded column, so
  the twin of `00100` is written `00100` and a length check, a
  fixed-width slice or a join on the code runs on the real table. The
  argument for routing was that the twin loses the padding. It does
  not, and has not since P4-D14.
* **Routing would have cost the distribution.** The column would have
  become labels, so the average, the spread and the ends of a genuine
  padded measurement would have gone -- against the tool's second goal,
  to keep results close to the real ones.

What is left of the ruling is what this module was already for: the
column IS asked about, its shape is described, `code` is one of the
answers offered, and since amendment A-P4-58 the question can be
answered without anybody at the keyboard by filling in the questions
file and handing it back with `--answers`. Asking was always the
owner's own first principle here -- "it's better to ask the user than
make wrong guesses" -- and the answer path is what was missing, not a
rule.

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

from synthtwin import dialect
from synthtwin import errors
from synthtwin import parsing
from synthtwin import taxonomy

# The roles that publish a ladder of real values. A column here that is
# really a coding system publishes real codes as its endpoints.
NUMERIC_ROLES = (
    taxonomy.ROLE_COUNT,
    taxonomy.ROLE_CONTINUOUS,
    taxonomy.ROLE_UNREPRESENTABLE,
)

# THE ROLES A COLUMN OF JOINED NUMBERS LANDS ON UNDECLARED (plan
# P4-D21). `120/80` is not a number, not a date and not a clock time,
# so it falls to free text -- or, where few enough readings repeat, to
# a label role. Both are asked about, because both are what a blood
# pressure column looks like when nobody has said what it is. AND THE
# JOINED ROLE ITSELF (plan P4-D40): a pair of plain whole numbers joined
# by a slash is read as joined numbers from its values, and a coding
# system can be written that way too, so the question is still put and
# `code` and `identifier` are still offered.
JOINED_ROLES = (
    taxonomy.ROLE_TEXT,
    taxonomy.ROLE_LONG_TAIL,
    taxonomy.ROLE_CATEGORICAL,
    taxonomy.ROLE_JOINED,
)

# The two readings a person is offered, and the third that already had
# an option. The words are the ones the help screen uses.
ANSWER_MEASUREMENT = "measurement"
ANSWER_CODE = "code"
ANSWER_IDENTIFIER = "identifier"
ANSWER_JOINED = "joined"
# ...and the fourth declaration a question can stand for (landing 2b.2):
# the column writes a point between its thousands and a comma for its
# decimals, which is `--decimal-comma`.
ANSWER_DECIMAL_COMMA = "decimal_comma"
# ...and the seventh (landing T1, plan P4-D370): the column is a 12-hour
# clock written without AM or PM, which is `--twelve-hour`. Nothing in
# `8:34` or `12:15` says which clock wrote it, so where every hour of a
# column lies in 1 to 12 the run asks (the owner's ruling of 2026-10-01:
# "If we can't guess and we need more informations, there is no big deal
# to ask for what we need").
ANSWER_TWELVE_HOUR = "twelve-hour"
BECAUSE_TWELVE_HOUR = "hours-from-one-to-twelve-and-no-am-or-pm"
# ...and the tenth (landing 3b.5, plan P4-D373): a column of clock times
# holding few enough different values for a set of labels -- the shift
# starts `07:00`, `15:00` and `23:00` -- is read as clock times since that
# landing, and a list of labels is written exactly alike, so the run asks.
# Enter keeps the times; `code` is `--code`, which reads it as labels.
BECAUSE_FEW_CLOCK_TIMES = "few-times-of-day-each-shared-by-many-rows"

# THE FIFTH DECLARATION, AND THE FIRST THAT IS NOT ABOUT A COLUMN (plan
# P4-D81). Some survey exports write two rows UNDER the column names
# that describe those columns rather than holding anybody's record.
# synthtwin used to recognise that shape and act on it, which meant a
# file it recognised WRONGLY had two of its records taken out of the
# table and published whole as schema text (review item CODEX-2). So
# the shape is a question now, and these are its two answers: the rows
# are records of the table (the reading that stands where nobody
# answers), or they describe the columns.
ANSWER_DATA = "data"
ANSWER_METADATA_ROWS = "metadata-rows"

# How many rows the answer declares. The shape synthtwin recognises is
# exactly two, and two is what the description can carry (contract FD9).
METADATA_ROWS_DECLARED = 2

# What the question is ABOUT, where a column question names its column.
# It names no value and no cell: it is a fact about the file's shape.
METADATA_SUBJECT = "the rows under your column names"

BECAUSE_EXPORT_SHAPE = "export-metadata-shape"
# ...and the same question asked from the other side: the person
# DECLARED such rows on a file that does not wear that shape, so the
# rows stayed in the table and the question is put in the file where
# they can answer it after reading what it costs (review of landing
# 2b.17, MAJOR; the CODEX-2 ruling read the other way round).
BECAUSE_DECLARED_UNSEEN = "declared-metadata-rows-not-seen"

# THE SIXTH DECLARATION, AND THE SECOND ABOUT THE FILE (plan P4-D110,
# review item CODEX-4): which character separates the columns, asked
# only where the file reads equally well under more than one. Each
# answer is a word a person can type in a JSON file, which a tab is not.
DELIMITER_SUBJECT = "the character between your columns"
BECAUSE_DELIMITER_TIE = "reads-equally-well-with-two-delimiters"
ANSWER_DELIMITERS = {
    "comma": ",",
    "semicolon": ";",
    "tab": "\t",
    "vertical-bar": "|",
}

# THE SEVENTH DECLARATION, AND THE THIRD ABOUT THE FILE (the owner's
# ruling of 2026-09-17, item 8; plan P4-D232): which row the column
# names are in, asked wherever the first row could not be told from a
# record of the table. The reading that stands where nobody answers is
# that the row is a RECORD -- the columns are named `column_1`,
# `column_2` and so on and every row is kept -- because that reading
# publishes no text of a row that may be somebody's data, and the other
# publishes all of it.
FIRST_ROW_SUBJECT = "which row your column names are in"
BECAUSE_FIRST_ROW_UNTOLD = "first-row-not-told-from-a-record"
ANSWER_FIRST_ROW_NAMES = "names"
ANSWER_FIRST_ROW_DATA = "first-record"

# THE EIGHTH DECLARATION, AND THE FOURTH ABOUT THE FILE (lane R1 of
# stage 3b, plan P4-D381; the owner's ruling of 2026-10-01: "If we can't
# guess and we need more informations, there is no big deal to ask"):
# whether the day or the month comes first, asked where a column of
# dates reads every cell both ways, so nothing in its values can say.
# The answer `day-first` is `--day-first`, which reaches every such
# column of the file. Landing T1 asked the same question in the same
# words; merged, the two are this one question.
DAY_FIRST_SUBJECT = "the order of the day and the month in your dates"
BECAUSE_DAY_AND_MONTH = "day-and-month-read-either-way"
ANSWER_MONTH_FIRST = "month-first"
ANSWER_DAY_FIRST = "day-first"

# THE NINTH, AND IT IS ABOUT A COLUMN AGAIN (lane R1, plan P4-D381): a
# column of dates or times that writes a few repeated codes where it has
# none -- `UNK`, `00/00/0000`, `0000-00-00`, a Caboodle `-1`, `99:99` --
# misses the date rule's line by them and is read as labels or numbers,
# and its twin then holds strings no date reader takes. The answer
# `missing` is `--missing-value` naming each code; `real-value` is
# `--keep-value` naming each, which keeps the reading and stops the
# question; Enter keeps the reading the column has.
BECAUSE_DATE_CODES = "dates-or-times-beside-a-few-repeated-codes"
ANSWER_NO_DATE = "missing"
ANSWER_REAL_VALUE = "real-value"

# Why a column was worth asking about. Each is shown to the person, so
# each says what was SEEN and not what it was taken to mean.
BECAUSE_PADDED = "padded"
BECAUSE_FIXED_WIDTH = "fixed-width"
BECAUSE_JOINED = "two-numbers"
# ...and the two a number grouped between its thousands raises (landing
# 2b.2). A column of `123 456 789` reads as numbers since that landing,
# and every value the same number of figures is what an identifier looks
# like whatever mark groups it. A column of `12.345` reads as decimals,
# and three figures after every point is what a point between thousands
# looks like.
BECAUSE_GROUPED_FIXED_WIDTH = "grouped-fixed-width"
BECAUSE_POINT_THOUSANDS = "three-figures-after-the-point"
# ...AND THE ONE QUESTION ABOUT WHO THE ROWS ARE (plan P4-D340, and
# the repair of landing 3.2). Asked of a column whose values REPEAT
# and are either MANY or written as CODES, and only where nothing at
# all was declared as holding record numbers: that shape is how a
# table with several rows per subject is written, and nothing else in
# this tool can reach it. The uniqueness pointer cannot -- it fires
# only where almost every value differs, which is the opposite shape --
# so a table of 12 subjects over 1,196 rows was described with every
# subject's identifier published beside its visit count and nothing
# said about it. ONE REASON COVERS BOTH ROUTES on purpose: what the
# person is being asked is the same question with the same two
# answers, and `_shape_of` renders what was actually seen -- how many
# different values over how many cells -- rather than restating the
# route that found it. `asking._names_people` holds both routes.
BECAUSE_REPEATS_AND_MANY = "repeats-and-many-different-values"

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


def _grouped_figures(text: str) -> "str | None":
    """The figures of a cell written as figures grouped in threes, or None.

    A cell qualifies where `parsing.thousands_mark` finds one mark
    grouping its figures and nothing but figures and that mark stands in
    it -- no sign, no point, no exponent -- which is how an identifier
    grouped for reading is written: `123 456 789`.
    """
    mark = parsing.thousands_mark(text)
    if not mark:
        return None
    figures = ""
    for character in text:
        if character == mark:
            continue
        if not ("0" <= character <= "9"):
            return None
        figures = figures + character
    return figures


def _without_sign_or_padding(text: str) -> str:
    """A cell with its outer spaces and its sign notation taken off.

    The notations the reader accepts on a number (landing 2b.2): a
    leading `+` or `-`, the minus sign U+2212, brackets around the
    figures, and a trailing minus. The shape questions below ask about
    the figures and the point, and a sign or a padded cell says nothing
    about whether the point groups thousands (integration repair: one
    `+1.500`, or one ` 1.500 `, among 599 plain cells silenced the
    question, and a column counted in thousands published a mean of
    1.4995 with nothing asked).
    """
    body = parsing.trimmed(text)
    if len(body) >= 2 and body[:1] == "(" and body[len(body) - 1 :] == ")":
        body = body[1 : len(body) - 1]
    elif len(body) >= 2 and body[len(body) - 1 :] == "-" and body[:1] != "-":
        body = body[: len(body) - 1]
    elif body[:1] in ("+", "-", parsing.MINUS_SIGN):
        body = body[1:]
    return body


def _point_between_thousands(text: str) -> bool:
    """Whether a cell could be a whole number with a point between thousands.

    One to three figures, not led by a zero, then a point, then exactly
    three figures, after an optional minus: `12.345`, `-1.500`. A
    thousands group never begins `0.`, so a column of proportions
    written `0.125` is not asked about.
    """
    if not isinstance(text, str):
        raise TypeError("a cell to ask about must be text")
    body = text
    if body[:1] == "-":
        body = body[1:]
    point = -1
    for place in range(len(body)):
        if body[place] == "." and point < 0:
            point = place
    if point < 1 or point > 3:
        return False
    head = body[:point]
    tail = body[point + 1 :]
    if head[:1] == "0" or len(tail) != 3:
        return False
    return _is_plain_whole_number(head) and _is_plain_whole_number(tail)


def _written_below_a_thousand(text: str) -> bool:
    """Whether a cell is a whole number below a thousand, written plainly.

    One to three figures, not led by a zero unless it is `0` itself,
    after an optional minus: `523`, `-7`, `0`. Written with a point
    between its thousands, a number below a thousand has no point at all,
    so these are the cells a column of `12.345` holds beside them.
    """
    if not isinstance(text, str):
        raise TypeError("a cell to ask about must be text")
    body = text
    if body[:1] == "-":
        body = body[1:]
    if len(body) < 1 or len(body) > 3:
        return False
    if body[:1] == "0" and body != "0":
        return False
    return _is_plain_whole_number(body)


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

    AND TWO THAT A GROUPED NUMBER RAISES (landing 2b.2):

    - every cell figures alone or figures grouped in threes by one mark,
      at least one of them grouped, and every cell the same number of
      FIGURES. `123 456 789` is read as a number since that landing,
      and a register of nine-figure identifiers grouped for reading
      would otherwise publish real identifiers of its own -- the
      boundary each tail is measured from, and a rung a group of rows
      shares -- with nothing asked.
    - at least one cell one to three figures, a point and exactly three
      figures, and every other cell a whole number below a thousand
      written plainly. Read undeclared, `12.345` is twelve and a bit;
      written with a point between thousands it is twelve thousand, and
      only the person holding the table knows which. The reading is not
      changed: the question offers `--decimal-comma` as an answer.

    THE SMALL NUMBERS DO NOT SILENCE IT (the verification of landing
    2b.2). The first rule asked only where EVERY cell had a point, and a
    count written the German way writes `523` for five hundred and
    twenty-three: a column of 900 such counts, a third of them below a
    thousand, published a mean of 184 for a true mean in the thousands
    with nothing asked, on three seeds of three. A cell below a thousand
    is what that column must hold, and one written any other way -- a
    point with one or two figures after it, a fourth figure before it --
    still settles the reading, so the column stays unasked.
    """
    if not values:
        return None
    grouped = False
    figures_of: "list[str]" = []
    for value in values:
        if _is_plain_whole_number(value):
            figures_of += [value]
            continue
        figures = _grouped_figures(value)
        if figures is None:
            pointed = False
            for cell in values:
                body = _without_sign_or_padding(cell)
                if _point_between_thousands(body):
                    pointed = True
                elif not _written_below_a_thousand(body):
                    return None
            if pointed:
                return BECAUSE_POINT_THOUSANDS
            return None
        grouped = True
        figures_of += [figures]
    if grouped:
        counted = {len(figures) for figures in figures_of}
        if len(counted) == 1:
            if sorted(counted)[0] >= _NARROWEST_FIXED_WIDTH:
                return BECAUSE_GROUPED_FIXED_WIDTH
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


def why_joined_is_worth_asking(values: "list[str]") -> "str | None":
    """The reason to ask whether a column holds joined numbers.

    Every present cell splits, on ONE separator, into the same number
    of NUMBERS -- two or more, each of which may carry one decimal
    point, which is what a ventilator ratio of `1:1.5` needs. This
    docstring said "whole numbers" until 2026-08-26 while the function
    it describes returned its reason for `1:1.5`. That is what a blood
    pressure looks like, and it is also exactly what a laboratory code
    looks like, which is why this raises a QUESTION and decides
    nothing.
    """
    if not values:
        return None
    for separator in taxonomy.JOINED_SEPARATORS:
        parts = 0
        for value in values:
            split = taxonomy.splits_into_numbers(value, separator)
            if split is None:
                parts = 0
                break
            if parts and len(split) != parts:
                parts = 0
                break
            parts = len(split)
        if parts >= 2:
            return BECAUSE_JOINED
    return None


def reads_each_number(role: str) -> bool:
    """Whether a column on this role is described one number at a time.

    The joined role (plan P4-D21, and P4-D40 for the shape read from the
    values) describes each position of a cell as a quantity and
    publishes no whole cell; neither sentence written for a label role
    or a text role says that.

    Guarantees: accepts a role name; returns whether it is the joined
    role. Determinism: a function of the name. Raises nothing. No I/O.
    """
    return role == taxonomy.ROLE_JOINED


def publishes_its_values(role: str) -> bool:
    """Whether a column on this role publishes the values themselves.

    WHAT A SCREEN MAY SAY ABOUT A COLUMN IT IS ASKING ABOUT (review
    round 1 of landing L16, item 2). The joined question reaches three
    roles and they do not agree on this: a column of few enough
    different pairs publishes every one of them with the rows that
    carried it, and a column of three hundred different pairs reaches
    free text and publishes NONE of them. One sentence covering both
    told the second kind that its values were kept as written, which
    is the opposite of the profile written beside it.

    It asks `taxonomy.ROLES_PUBLISHING_NOTHING`, which is the closed
    enumeration that already answers this question for every role, so
    a role added later cannot be missed here.

    Guarantees: accepts a role name; returns whether that role
    publishes any value of the column. Determinism: a function of the
    name against a closed tuple. Raises nothing. No I/O of any kind.
    """
    return role not in taxonomy.ROLES_PUBLISHING_NOTHING


@dataclasses.dataclass(frozen=True)
class Choice:
    """One answer a person may give, and what taking it would publish.

    A CHOICE IS DATA, NOT PROSE AT A CALL SITE (plan amendment
    A-P4-58). The questions file and the terminal prompt are the same
    question asked in two places, and Phase 7 will ask it in a third.
    Where each of them writes its own words they drift, and a person
    answering one is answering a different question from the person
    answering another. So the words live here, once, and every surface
    renders them.

    `publishes` is the half a person actually decides on. "Codes" and
    "measurements" are labels for a choice whose real content is what
    the description will carry: an average over the values, or every
    value kept with the rows that held it.
    """

    answer: str
    means: str
    publishes: str


@dataclasses.dataclass(frozen=True)
class Question:
    """One column synthtwin cannot read on its own, ready to be put.

    THE SHAPE IS DESCRIBED, NOT SHOWN (owner ruling 2026-09-10, on the
    disclosure rule amendment A-P4-58 fixes for the questions file).
    This carried four of the column's real values until then, because a
    question about a column seemed unanswerable without them. It is
    not: what a person needs is what synthtwin SAW, and the shape says
    that without carrying a cell off the machine -- "every value is
    written in figures alone, all five characters wide" answers the
    question that four copies of `99213` answers, and travels where
    they may not.

    That matters because the file travels and the screen does not. A
    person hands the file to a colleague, keeps it beside the profile,
    or opens it on another machine; the plan's rule for it is that it
    may name the column, the choices and any spelling the description
    itself would publish, and no value of the table. Showing values on
    the screen while withholding them in the file would make one
    question into two, which is the thing that rule exists to stop.

    A dataclass rather than a written constructor, for the reason
    `taxonomy.Settings` gives: the offline policy accepts no
    double-underscore name in this source (plan D6.2).
    """

    name: str
    role: str
    reason: str
    shape: str
    choices: "list[Choice]"
    taken: str


# THE READING THAT STANDS WHERE NOBODY ANSWERS, as an answer of its
# own (review round 1 of landing L17a, item 3). A joined-looking column
# of three hundred different pairs lands on `free_text`, and this
# recorded `joined` as the reading taken -- so the prompt told a person
# that pressing Enter kept a reading Enter does not give them, and the
# file would have said so in writing. The standing reading is not one
# of the three declarations; it is what the column already is.
ANSWER_KEEP = "keep"


def _clock_publishes(floor: int, role: str = taxonomy.ROLE_CLOCK) -> str:
    """What a column of clock times or of moments publishes, as a choice says it."""
    along = "along the day"
    if role == taxonomy.ROLE_DATETIME:
        along = "along its range of dates and times"
    said = (
        f"points {along} and the two tails beyond them, but neither end: "
        f"each end is published only where at least {floor} rows share "
        f"the value"
    )
    if role == taxonomy.ROLE_CLOCK:
        # ...AND THE CENSUS OF A CLOCK (landing 3b.5, plan P4-D373).
        said = (
            f"{said}; and every time at least {floor} rows share that "
            f"stands out from the times beside it, with how many rows "
            f"share it, and how many of the others fall in each stretch "
            f"of the day, each such count at least {floor}"
        )
    return said


def _publishes_under(answer: str, role: str, floor: int) -> str:
    """What the description carries if this answer is taken.

    DERIVED FROM THE ROLE AND THE FLOOR, never a constant (review round
    1 of landing L17a, item 4). Two measured sentences were false:

    * a column of 400-figure integers takes `numeric_unrepresentable`,
      which publishes NO numeric statistic at all, and the measurement
      choice promised it an average, a spread and ends;
    * at a smallest-group size of eleven a categorical column withholds
      its rare levels, and the code choice promised that every value is
      kept exactly as written -- which is the whole point of that
      answer, and not true above a floor of one.

    AND IT DOES NOT SAY WHO CHOSE THE FLOOR (plan P4-D316). It read
    "because you asked for groups of 11", which was true while the
    default was 1 and every floor above it had been typed. The default
    is 11 since 2026-09-22, so most runs at that floor asked for nothing,
    and the sentence now names the rule rather than a request.

    AND NO CHOICE PROMISES AN END STAGE 3 WITHHELD (review of
    2026-09-23, finding 7). The measurement, joined-number and
    decimal-comma choices each read "a smallest and a largest", and a
    description written after stage 3 publishes an end only where at
    least the floor's rows share it. Measured on 100 readings 0.125 to
    99.125: `min`, `max` and six of the nine interior rungs are withheld,
    so the person answering was deciding on a promise of two values the
    answer cannot deliver. Each of the three now names the tail instead,
    with the floor the end would have to clear.

    A choice that overstates what it buys is worse than no choice: the
    person is deciding on this sentence, and it is the only part of the
    question they cannot check for themselves.

    Guarantees: accepts an answer word, the role the column holds now,
    and the publication floor; returns one sentence. Determinism: a
    function of the three. Raises nothing. No I/O, and no value of any
    table is reachable from here.
    """
    if answer == ANSWER_IDENTIFIER:
        return "no value of the column at all"
    if answer == ANSWER_MEASUREMENT:
        if role == taxonomy.ROLE_UNREPRESENTABLE:
            return (
                "how its numbers are WRITTEN -- how many figures, how "
                "many carry a sign -- and no average, smallest or "
                "largest, because numbers this large are past what this "
                "file format can hold"
            )
        return (
            f"an average, a spread and points along its range, but "
            f"neither end: each end is published only where at least "
            f"{floor} rows share the value, and otherwise the "
            f"description carries a boundary, how many rows lie beyond "
            f"it and, where its tail rule lets it, how far beyond they "
            f"lie"
        )
    if answer == ANSWER_JOINED or (
        answer == ANSWER_KEEP and role == taxonomy.ROLE_JOINED
    ):
        return (
            f"each number inside the cell described on its own, with its "
            f"own average, spread and points along its range, and its "
            f"own two ends published only where at least {floor} rows "
            f"share them"
        )
    if answer == ANSWER_DECIMAL_COMMA:
        return (
            f"an average, a spread and points along its range, but "
            f"neither end unless at least {floor} rows share it, with "
            f"every point read as a mark between thousands and every "
            f"comma as the decimal point"
        )
    if answer == ANSWER_CODE:
        if floor > 1:
            return (
                f"every value that at least {floor} rows share, exactly "
                f"as written and with the number of rows that carried "
                f"it; rarer ones counted together and never named, "
                f"because no group of fewer than {floor} rows is named"
            )
        return (
            "every value exactly as written, with the number of rows "
            "that carried it, and no average at all"
        )
    if answer == ANSWER_TWELVE_HOUR:
        return (
            f"{_clock_publishes(floor, role)}, read on a 12-hour clock: 12 "
            f"is the hour after midnight, and the twin writes hours 1 to 12 "
            f"only, as your table does"
        )
    # ANSWER_KEEP: whatever the column already is.
    if role == taxonomy.ROLE_CLOCK or role == taxonomy.ROLE_DATETIME:
        return f"what it publishes now: {_clock_publishes(floor, role)}"
    if not publishes_its_values(role):
        return "no value of the column at all, which is what it does now"
    if floor > 1:
        return (
            f"what it publishes now: every value that at least {floor} "
            f"rows share, with its count, and the rarer ones counted "
            f"together"
        )
    return (
        "what it publishes now: every value as written, with the number "
        "of rows that carried it"
    )


def _numeric_choices(
    taken: str, role: str, floor: int
) -> "list[Choice]":
    """The three answers a column of figures may take.

    `taken` names the reading that stands where nobody answers, and it
    is put FIRST: a person reads the first of three as the default
    whatever the words underneath say, so the order has to agree with
    the behaviour or the list itself misleads.
    """
    every = [
        Choice(
            ANSWER_MEASUREMENT,
            "measurements -- quantities somebody counted or measured",
            _publishes_under(ANSWER_MEASUREMENT, role, floor),
        ),
        Choice(
            ANSWER_CODE,
            "codes -- a coding system, where the value stands for a "
            "thing rather than counting one",
            _publishes_under(ANSWER_CODE, role, floor),
        ),
        Choice(
            ANSWER_IDENTIFIER,
            "record numbers -- a key nothing should publish",
            _publishes_under(ANSWER_IDENTIFIER, role, floor),
        ),
    ]
    first: list[Choice] = []
    rest: list[Choice] = []
    for choice in every:
        if choice.answer == taken:
            first += [choice]
        else:
            rest += [choice]
    return first + rest


def _point_choices(role: str, floor: int) -> "list[Choice]":
    """The answers a column of `12.345`-shaped figures may take (landing 2b.2).

    The reading taken first, because Enter gives it: the point is a
    decimal point. The second is the declaration that reads it the other
    way, and the last two are the ones every column of figures is
    offered.
    """
    return [
        Choice(
            ANSWER_MEASUREMENT,
            "measurements written with a decimal point -- `12.345` is "
            "twelve and a bit",
            _publishes_under(ANSWER_MEASUREMENT, role, floor),
        ),
        Choice(
            ANSWER_DECIMAL_COMMA,
            "measurements written with a point between thousands and a "
            "comma for decimals -- `12.345` is twelve thousand three "
            "hundred and forty-five",
            _publishes_under(ANSWER_DECIMAL_COMMA, role, floor),
        ),
        Choice(
            ANSWER_CODE,
            "codes -- a coding system, where the value stands for a "
            "thing rather than counting one",
            _publishes_under(ANSWER_CODE, role, floor),
        ),
        Choice(
            ANSWER_IDENTIFIER,
            "record numbers -- a key nothing should publish",
            _publishes_under(ANSWER_IDENTIFIER, role, floor),
        ),
    ]


def _joined_choices(role: str, floor: int) -> "list[Choice]":
    """The answers a column of two-numbers-in-one-cell may take.

    THE FIRST ONE IS WHAT ENTER GIVES YOU, and it is not `joined`
    (review round 1, item 3). Such a column is read as text or as
    labels today; declaring it joined is an affirmative answer that
    CHANGES the reading. Listing the change as the default told a
    person that doing nothing would describe their blood pressures,
    when doing nothing leaves them undescribed.

    A column already read as joined numbers from its values (plan
    P4-D40) keeps that reading on Enter, and is not offered `joined`
    again: the answer would change nothing.
    """
    if role == taxonomy.ROLE_CLOCK:
        # A CLOCK READ FROM ITS VALUES (landing T1). `8:34` is a time of
        # day and also two numbers joined by a colon -- a duration in
        # minutes and seconds is written so -- and the reader takes the
        # clock, so Enter keeps it and the other readings are offered.
        return [
            Choice(
                ANSWER_KEEP,
                "leave it as it is -- synthtwin reads these cells as times "
                "of day",
                _publishes_under(ANSWER_KEEP, role, floor),
            ),
            Choice(
                ANSWER_JOINED,
                "measurements written as two numbers in one cell, such as "
                "a duration in minutes and seconds",
                _publishes_under(ANSWER_JOINED, role, floor),
            ),
            Choice(
                ANSWER_CODE,
                "codes -- a coding system that writes its codes in parts",
                _publishes_under(ANSWER_CODE, role, floor),
            ),
            Choice(
                ANSWER_IDENTIFIER,
                "record numbers -- a key nothing should publish",
                _publishes_under(ANSWER_IDENTIFIER, role, floor),
            ),
        ]
    if role == taxonomy.ROLE_JOINED:
        return [
            Choice(
                ANSWER_KEEP,
                "leave it as it is -- synthtwin reads each number in "
                "these cells on its own",
                _publishes_under(ANSWER_KEEP, role, floor),
            ),
            Choice(
                ANSWER_CODE,
                "codes -- a coding system that writes its codes in parts",
                _publishes_under(ANSWER_CODE, role, floor),
            ),
            Choice(
                ANSWER_IDENTIFIER,
                "record numbers -- a key nothing should publish",
                _publishes_under(ANSWER_IDENTIFIER, role, floor),
            ),
        ]
    return [
        Choice(
            ANSWER_KEEP,
            "leave it as it is -- synthtwin reads these cells as text",
            _publishes_under(ANSWER_KEEP, role, floor),
        ),
        Choice(
            ANSWER_JOINED,
            "measurements written as two numbers in one cell, such as "
            "a blood pressure",
            _publishes_under(ANSWER_JOINED, role, floor),
        ),
        Choice(
            ANSWER_CODE,
            "codes -- a coding system that writes its codes in parts",
            _publishes_under(ANSWER_CODE, role, floor),
        ),
        Choice(
            ANSWER_IDENTIFIER,
            "record numbers -- a key nothing should publish",
            _publishes_under(ANSWER_IDENTIFIER, role, floor),
        ),
    ]


@dataclasses.dataclass(frozen=True, eq=False)
class SplitColumns:
    """The present cells `questions_for` split out of the columns it read.

    Handed to `person_questions`, which asks `taxonomy.split_missing` the
    same question of the same columns under the same settings, so each
    column is split once. ``cells[place]`` is the column object the list
    ``present[place]`` was split from, and `person_questions` takes a
    list only where the table's column at that place IS that object and
    the settings are equal to ``settings``; anything else it splits
    itself.
    """

    settings: taxonomy.Settings
    cells: "dict[int, list[str]]"
    present: "dict[int, list[str]]"


def questions_for(
    document: "dict[str, object]",
    table_columns: "list[list[str]]",
    settings: taxonomy.Settings,
    already: "list[str]",
    decimal_commas: "tuple[str, ...]" = (),
) -> "list[Question]":
    """Every column worth asking about, in the table's own order.

    `questions_and_splits_for` without the present cells it split, for
    a caller that asks nothing after it.
    """
    return questions_and_splits_for(
        document, table_columns, settings, already, decimal_commas
    )[0]


def _clock_hours(
    present: "list[str]", stamps: bool
) -> "tuple[bool, bool, bool]":
    """What the clocks of a column show about their face (landing T1).

    Whether every clock it reads writes no marker, whether every such
    hour lies in 1 to 12 -- which a 24-hour clock and a 12-hour clock
    written without AM or PM both write -- and whether some hour is
    written in one figure. Counts nothing that is published.
    """
    seen = False
    unmarked = True
    within = True
    one_figure = False
    for value in present:
        parts = parsing.clock_parts(
            parsing.stamp_halves(value)[1] if stamps else value
        )
        if parts is None:
            continue
        seen = True
        if parts[5]:
            unmarked = False
            continue
        if parts[0] < 1 or parts[0] > 12:
            within = False
        if parts[4] == 1:
            one_figure = True
    return seen and unmarked, seen and unmarked and within, one_figure


def _clock_question(
    block: "dict[str, object]",
    present: "list[str]",
    floor: int,
    twelve_hours: "tuple[str, ...]",
) -> "Question | None":
    """The question a column of unmarked clocks may raise (landing T1).

    TWO THINGS ITS VALUES CANNOT SETTLE. A column of clock times whose
    hours are written in one figure is also two numbers joined by a
    colon, which is how a duration in minutes and seconds is written --
    the question it was asked as free text before it was read, kept (the
    T1 design skeptic, item 3). And where every hour lies in 1 to 12 and
    no cell writes AM or PM, a 24-hour clock and a 12-hour clock are
    written alike (item 1); the answer `twelve-hour` is `--twelve-hour`,
    and Enter keeps the 24-hour reading. A column declared a 12-hour
    clock, a column writing a marker, and a column of two-figure hours
    some of which pass twelve raise nothing.
    """
    name = f"{block['name']}"
    role = f"{block['role']}"
    stamps = (
        role == taxonomy.ROLE_DATETIME
        and "format" in block
        and f"{block['format']}" in parsing.SLASHED_STAMPS
    )
    if role != taxonomy.ROLE_CLOCK and not stamps:
        return None
    if name in twelve_hours:
        return None
    unmarked, within, one_figure = _clock_hours(present, stamps)
    if not unmarked:
        return None
    # THE CELLS THE COLUMN DID NOT READ, as its description counts them,
    # so the 12-hour question does not say "every value" of a column
    # holding some that are no clock it reads (the T1 review's item 10).
    unread = block["n_unparsed"] if "n_unparsed" in block else 0
    remainder = unread if isinstance(unread, int) else 0
    choices: "list[Choice]" = []
    if role == taxonomy.ROLE_CLOCK and one_figure:
        choices = _joined_choices(role, floor)
    if within:
        twelve = Choice(
            ANSWER_TWELVE_HOUR,
            "a 12-hour clock written without AM or PM -- 12:15 is a "
            "quarter past midnight",
            _publishes_under(ANSWER_TWELVE_HOUR, role, floor),
        )
        if not choices:
            choices = [
                Choice(
                    ANSWER_KEEP,
                    "leave it as it is -- a 24-hour clock, 12:15 is a "
                    "quarter past noon",
                    _publishes_under(ANSWER_KEEP, role, floor),
                )
            ]
        choices = [choices[0], twelve] + choices[1:]
        return Question(
            name, role, BECAUSE_TWELVE_HOUR,
            _shape_of(BECAUSE_TWELVE_HOUR, present, floor, "", remainder),
            choices, ANSWER_KEEP,
        )
    if choices:
        # ...AND THE COLON QUESTION COUNTS THE CELLS ITS SENTENCE SAYS ARE
        # NOT numbers joined by a colon, which is not the cells the column
        # left unread: a clock of the other precision, `1:00:00` among
        # minutes, is unread and is such numbers all the same.
        apart = 0
        for value in present:
            split = taxonomy.splits_into_numbers(value, ":")
            if split is None or len(split) < 2:
                apart = apart + 1
        return Question(
            name, role, BECAUSE_JOINED,
            _shape_of(BECAUSE_JOINED, present, floor, ":", apart),
            choices, ANSWER_KEEP,
        )
    return None


def asks_about_a_clock(question: Question) -> bool:
    """Whether a question is `_clock_question`'s, about a column read as times of day.

    The 12-hour question, on a clock or a slashed stamp, and the colon
    question a clock whose hours show one figure keeps (landing T1), and
    the clock-or-labels question of a column of few shared times (landing
    3b.5, plan P4-D373; at its merge into T1's tree a scripted run put
    that column under "read as measurements"). A caller saying what such
    a column is read as must not take it for text or for figures (the T1
    review's item 8). Guarantees: a function of the question; raises
    nothing; opens nothing.
    """
    if question.reason == BECAUSE_TWELVE_HOUR or question.reason == BECAUSE_FEW_CLOCK_TIMES:
        return True
    return question.reason == BECAUSE_JOINED and question.role == taxonomy.ROLE_CLOCK


# What the clock-or-labels question's `code` means (landing 3b.5, plan
# P4-D373): the answer that reads a column of few shared times as labels.
# `offers_labels_written_as_times` finds it among a question's choices,
# wherever `_with_the_labels_answer` carried it.
_LABELS_WRITTEN_AS_TIMES = (
    "labels that happen to be written as times -- each value names a group, "
    "not a moment"
)


def offers_labels_written_as_times(question: Question) -> bool:
    """Whether a question offers the clock-or-labels question's `code` (P4-D373).

    The clock-or-labels question offers it, and so does a 12-hour
    question the labels answer joined (`_with_the_labels_answer`); the
    colon question's own `code`, codes written in parts, is another
    answer. A caller offering `--code` for labels written as times asks
    this (the merge of landing 3b.5 beside landing T1). Guarantees: a
    function of the question; raises nothing; opens nothing.
    """
    for choice in question.choices:
        if choice.answer == ANSWER_CODE and choice.means == _LABELS_WRITTEN_AS_TIMES:
            return True
    return False


def _clock_or_labels_question(
    block: "dict[str, object]",
    present: "list[str]",
    settings: taxonomy.Settings,
    n_rows: int,
) -> "Question | None":
    """The question a column of few clock times raises (landing 3b.5).

    WHAT THE VALUES CANNOT SETTLE. Since plan P4-D373 a column of clock
    times is read as clock times however few different values it holds,
    where it used to be a set of labels once it held no more than the
    categories line (`taxonomy.categories_ceiling`). Both readings fit
    such a column: as times its shared values are published as heaps with
    their counts and the rest as counts of ten-minute stretches, and the
    twin writes times of day; as labels every value at least the floor's
    rows share is published with its count and the rest counted together.
    Enter keeps the times; `code` is `--code` on this column.

    ASKED WHERE THE DATA DOES NOT SETTLE IT: where the column holds few
    enough different values for a set of labels and EVERY TIME inside its
    range -- between the two tail boundaries, both included, or every
    time of a column with no tails -- is written by at least the census
    line's rows, as every value of a list of labels the floor publishes
    is (`_times_each_shared`). Three shift starts are such a column, and
    so are twelve neighbouring minutes written twenty rows each: they
    stand out from nothing, so they publish a census and no heap, and the
    repair round asked only where heaps held the body -- but that the
    values sit side by side does not say they are times (the landing's
    review, item 3: the seed-0 twin of those 240 rows wrote `14:01` 39
    times and `14:08` 10 where each label had 20). Walk-ins at 10,000
    rows, 713 different times most of them on a few rows, are times, and
    nobody is asked.

    Guarantees: accepts the column's block, its present cells, the
    settings and the table's rows; returns the question or None. No cell
    of the column appears in it. Determinism: a function of the four.
    Raises nothing. No I/O.
    """
    if f"{block['role']}" != taxonomy.ROLE_CLOCK:
        return None
    different = block["n_distinct_folded"] if "n_distinct_folded" in block else None
    if not isinstance(different, int):
        return None
    if different > taxonomy.categories_ceiling(n_rows, settings):
        return None
    floor = settings.small_cell_floor
    if not _times_each_shared(block, present, parsing.census_floor(floor)):
        return None
    role = taxonomy.ROLE_CLOCK
    return Question(
        f"{block['name']}",
        role,
        BECAUSE_FEW_CLOCK_TIMES,
        _shape_of(BECAUSE_FEW_CLOCK_TIMES, present, floor),
        [
            Choice(
                ANSWER_KEEP,
                "leave it as it is -- times of day, such as when a shift "
                "starts",
                _publishes_under(ANSWER_KEEP, role, floor),
            ),
            Choice(
                ANSWER_CODE,
                _LABELS_WRITTEN_AS_TIMES,
                _publishes_under(ANSWER_CODE, role, floor),
            ),
        ],
        ANSWER_KEEP,
    )


def _times_each_shared(
    block: "dict[str, object]", present: "list[str]", line: int
) -> bool:
    """Whether every time inside a clock column's range is written by at
    least `line` rows (P4-D373; the landing's review, item 3).

    Inside its range: between the two tail boundaries, both included, or
    anywhere on a column with no tails, so a few stray times beyond the
    boundaries do not settle it. Each spelling is read once, in the
    column's form, and its rows added to the time it reads as; a cell the
    form leaves unread is no time and is not asked about.

    Guarantees: accepts the column's block, its present cells and the
    line; returns False where the block cannot be read or no time is
    inside. Determinism: a function of the three. Raises nothing. No I/O.
    """
    form = block["clock_form"] if "clock_form" in block else None
    if not isinstance(form, str) or form not in parsing.CLOCK_FORMS:
        return False
    lowest: "int | None" = None
    highest: "int | None" = None
    low = block["low_tail"] if "low_tail" in block else None
    high = block["high_tail"] if "high_tail" in block else None
    if isinstance(low, dict) and isinstance(high, dict):
        lowest = parsing.clock_ordinal(f"{low['boundary']}", form)
        highest = parsing.clock_ordinal(f"{high['boundary']}", form)
        if lowest is None or highest is None:
            return False
    spelled: "dict[str, int]" = {}
    for value in present:
        spelled[value] = (spelled[value] if value in spelled else 0) + 1
    rows_at: "dict[int, int]" = {}
    for spelling in spelled:
        at = parsing.clock_ordinal(spelling, form)
        if at is None:
            continue
        if lowest is not None and highest is not None and not lowest <= at <= highest:
            continue
        rows_at[at] = (rows_at[at] if at in rows_at else 0) + spelled[spelling]
    if not rows_at:
        return False
    for at in rows_at:
        if rows_at[at] < line:
            return False
    return True


def _with_the_labels_answer(question: Question, labels: Question) -> Question:
    """A clock column's question offering the labels answer too (P4-D373).

    THE LANDING'S REVIEW, ITEM 2: where the 12-hour question, or the colon
    question a clock in one figure raises, and the clock-or-labels
    question both fit one column, the first was asked alone and the second
    never was -- 100 rows each of `07:00`, `08:00` and `09:00` were
    offered `keep` and `twelve-hour`, so a person whose values name groups
    could not answer `code` in the questions file. One question per
    column, so the first is asked with every answer either offers: `code`
    joins it where it does not offer it already, and what was seen says
    why labels fit too.

    Guarantees: a function of the two questions; raises nothing; no I/O.
    """
    choices: "list[Choice]" = []
    offered = False
    for choice in question.choices:
        choices += [choice]
        if choice.answer == ANSWER_CODE:
            offered = True
    for choice in labels.choices:
        if choice.answer == ANSWER_CODE and not offered:
            choices += [choice]
    return Question(
        question.name,
        question.role,
        question.reason,
        f"{question.shape}; and {labels.shape}",
        choices,
        question.taken,
    )


def questions_and_splits_for(
    document: "dict[str, object]",
    table_columns: "list[list[str]]",
    settings: taxonomy.Settings,
    already: "list[str]",
    decimal_commas: "tuple[str, ...]" = (),
) -> "tuple[list[Question], SplitColumns]":
    """Every column worth asking about, in the table's own order.

    Returned with the present cells split out of every column read on
    the way (`SplitColumns`), which `person_questions` takes rather than
    splitting the same columns again.

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
    heard. ``decimal_commas`` names the columns declared with
    `--decimal-comma`, which have answered the point question and only
    that one (the verification of landing 2b.2: a declared column of
    `2.433` beside `771` was still asked whether its point was a mark
    between thousands).
    """
    split_cells: "dict[int, list[str]]" = {}
    split_present: "dict[int, list[str]]" = {}
    blocks = document["columns"]
    if not isinstance(blocks, list):
        return [], SplitColumns(settings, split_cells, split_present)
    asked: list[Question] = []
    position = 0
    for block in blocks:
        if not isinstance(block, dict):
            position = position + 1
            continue
        name = f"{block['name']}"
        role = f"{block['role']}"
        if name in already:
            position = position + 1
            continue
        if position >= len(table_columns):
            position = position + 1
            continue
        present, _absent = taxonomy.split_missing(
            table_columns[position], settings
        )
        split_cells[position] = table_columns[position]
        split_present[position] = present
        clock = _clock_question(
            block, present, settings.small_cell_floor,
            settings.forced_twelve_hour_clocks,
        )
        # ...or, where both readings fit, whether the times are labels
        # (landing 3b.5, plan P4-D373) -- and where both questions fit, the
        # first asked with every answer either offers (the review, item 2).
        labels = _clock_or_labels_question(
            block, present, settings, len(table_columns[position])
        )
        if clock is None:
            clock = labels
        elif labels is not None:
            clock = _with_the_labels_answer(clock, labels)
        if clock is not None:
            asked += [clock]
            position = position + 1
            continue
        if role not in NUMERIC_ROLES and role not in JOINED_ROLES:
            position = position + 1
            continue
        reason: "str | None"
        mark = ""
        remainder = 0
        if role == taxonomy.ROLE_JOINED:
            # THE PUBLISHED READING IS THE EVIDENCE (integration repair of
            # landing 2b.5). Rule 9c reads a pair spaced `1234 / 5`, and a
            # column with a cell that is not a pair, as joined numbers,
            # and the recogniser below re-parses on bare marks with every
            # cell a pair -- so both published an average of each number
            # with nothing asked, while the bare column was asked. A
            # column declared a measurement is in ``already`` above.
            reason = BECAUSE_JOINED
            mark = f"{block['separator']}" if "separator" in block else ""
            unparsed = block["n_unparsed"] if "n_unparsed" in block else 0
            remainder = unparsed if isinstance(unparsed, int) else 0
        elif role in JOINED_ROLES:
            reason = why_joined_is_worth_asking(present)
        else:
            reason = why_worth_asking(present)
        if reason == BECAUSE_POINT_THOUSANDS and name in decimal_commas:
            reason = None
        if reason is not None:
            # THE READING RECORDED HERE IS THE ONE THE TOOL TAKES, and
            # never the one it ought to take. A questions file that
            # named a reading the run does not take would be the one
            # thing this file may never be, so both branches follow
            # `taxonomy.profile_column` exactly -- which is why the
            # padded column below says `measurement`, and why the
            # docstring records the ruling that would have made it say
            # `code` and the measurement that withdrew it.
            if reason == BECAUSE_JOINED:
                # ENTER KEEPS THE READING THE COLUMN ALREADY HAS, which
                # for a joined-looking column is text or labels and is
                # never `joined`: declaring it joined CHANGES the
                # reading (review round 1, item 3).
                choices = _joined_choices(role, settings.small_cell_floor)
                taken = ANSWER_KEEP
            elif reason == BECAUSE_POINT_THOUSANDS:
                choices = _point_choices(role, settings.small_cell_floor)
                taken = ANSWER_MEASUREMENT
            else:
                choices = _numeric_choices(
                    ANSWER_MEASUREMENT, role, settings.small_cell_floor
                )
                taken = ANSWER_MEASUREMENT
            asked += [
                Question(
                    name,
                    role,
                    reason,
                    _shape_of(
                        reason, present, settings.small_cell_floor, mark,
                        remainder,
                    ),
                    choices,
                    taken,
                )
            ]
        position = position + 1
    return asked, SplitColumns(settings, split_cells, split_present)


def file_questions(
    metadata_shape: bool,
    declared_unseen: int = 0,
    tied_delimiters: "tuple[str, ...]" = (),
    first_row_seen: str = "",
    day_or_month: "tuple[DayOrMonth, ...]" = (),
) -> "list[Question]":
    """The questions about the FILE rather than about a column.

    Four subjects: which row the column names are in
    (`_first_row_questions`, the owner's ruling of 2026-09-17 item 8,
    plan P4-D232), the rows under the column names
    (`_metadata_questions`), where the file reads equally well under
    more than one delimiter, which one it is written with
    (`_delimiter_questions`, plan P4-D110), and where no value of a
    column of dates can say, whether the day or the month comes first
    (`_day_first_questions`, plan P4-D381). In that order, which is the
    order a file is read in: which row the names are in is settled
    before anything under it can be described, and the cells are split
    before any of them is read as a date.

    Guarantees: a fixed function of the arguments; opens nothing; and
    carries no value of the table.
    """
    return (
        _first_row_questions(first_row_seen)
        + _metadata_questions(metadata_shape, declared_unseen)
        + _delimiter_questions(tied_delimiters)
        + _day_first_questions(day_or_month)
    )


@dataclasses.dataclass(frozen=True)
class DayOrMonth:
    """One column of dates no value of which can say which comes first.

    `months` is how many different months of the year its dates fall in
    when read month first, and `days` how many different days of a
    month; read day first the two change places. Both are counts of
    calendar positions -- at most twelve each, since every day and
    month here is twelve or less -- and never of rows.
    """

    name: str
    months: int
    days: int


def day_or_month_seen(
    present: "list[str]", format_name: str
) -> "DayOrMonth | None":
    """Whether a column's dates read every cell both ways, and what each way gives.

    THE QUESTION A COLUMN OF DATES CANNOT ANSWER (lane R1 of stage 3b,
    plan P4-D381). `03/04/2024` is the 4th of March or the 3rd of April,
    and where every cell of a column has its day and its month both
    twelve or less, both readings parse every cell: the column is read
    month first by the ratified default, and nothing in it can say
    whether that is right. Measured on 668f276 over the columns of
    `tests/date_question_shapes.py`: a day-first column whose days all
    lie in 1 to 12 is read month first and its twin parses 453 of 1,000
    cells under the person's own `%d/%m/%Y`, and month starts written
    `01/03/2023`, every date of which that reading puts in January, 741.
    `--day-first` repairs both to 1,000.

    Asked only of the reading a column TOOK, and only where that is the
    month-first member of one of the classifier's slashed pairs
    (`taxonomy.SLASHED_PAIRS`: slashed, dotted and two-figure-year
    dates, and slashed dates with a clock). A column whose own values
    settle the order -- one cell only one reading parses -- reads the
    way they say and is not asked about, and neither is a column read
    day first, which a declaration or its own evidence chose.

    Each DIFFERENT spelling is parsed once, under both readings, so a
    column of a million cells over a few thousand dates costs a few
    thousand parses; the walk stops at the first cell one reading alone
    parses.

    Guarantees: accepts the present cells and the format member the
    column took; returns the column's two calendar counts, under the
    name the caller gives it, or None. Determinism: a function of the
    two. Raises TypeError if a cell is not text. No I/O, and no cell
    reaches what it returns.
    """
    pair: "tuple[str, str] | None" = None
    for candidate in taxonomy.SLASHED_PAIRS:
        if candidate[0] == format_name:
            pair = candidate
    if pair is None or not present:
        return None
    seen: "dict[str, int]" = {}
    months: "dict[str, int]" = {}
    days: "dict[str, int]" = {}
    for value in present:
        if value in seen:
            continue
        seen[value] = 1
        month_first = parsing.parse_datetime(value, pair[0])
        day_first = parsing.parse_datetime(value, pair[1])
        if (month_first is None) != (day_first is None):
            return None
        if month_first is None:
            continue
        canonical = month_first[0]
        months[canonical[5:7]] = 1
        days[canonical[8:10]] = 1
    if not months:
        return None
    return DayOrMonth("", len(months), len(days))


def day_or_month_columns(
    document: "dict[str, object]",
    table_columns: "list[list[str]]",
    settings: taxonomy.Settings,
    split: "SplitColumns | None" = None,
    also: "tuple[DayOrMonth, ...]" = (),
) -> "tuple[DayOrMonth, ...]":
    """Every column of dates no value of which can say which comes first.

    Asked only of a column read under the month-first member of a
    slashed pair, so nothing is asked where `--day-first` was given, in
    either way it can be given: under it a column whose cells read both
    ways is read day first, which is the reading the person asked for,
    and a column still read month first is one whose own cells said so.
    That test is the block's format, made before any cell is split, so
    a column of dates read any other way costs nothing here. Each
    column's present cells are taken from ``split`` where `questions_
    and_splits_for` split that very column under these settings, and
    split here otherwise.

    ``also`` holds the columns of dates beside a few codes whose other
    cells read both ways (`date_codes_seen`): such a column is read
    as labels until the codes are answered, so its block names no
    format, and it is put in the same question rather than in the file
    the answering run writes. Each stands in the table's own place.

    Guarantees: a fixed function of the arguments, in the table's own
    column order; opens nothing; and no cell of any column appears in
    what it returns.
    """
    blocks = document["columns"]
    if not isinstance(blocks, list):
        return also
    found: "list[DayOrMonth]" = []
    # Each column of ``also`` by its name, once (the Codex review of lane
    # R1, item 9): it was walked once per column of the table.
    also_of: "dict[str, DayOrMonth]" = {}
    for one in also:
        if one.name not in also_of:
            also_of[one.name] = one
    position = 0
    for block in blocks:
        position = position + 1
        if not isinstance(block, dict) or position > len(table_columns):
            continue
        if f"{block['name']}" in also_of:
            # Once: a column of dates read whole but for its codes is
            # also a block with a format, and it is asked once.
            found += [also_of[f"{block['name']}"]]
            continue
        if f"{block['role']}" != taxonomy.ROLE_DATETIME:
            continue
        if "format" not in block:
            continue
        if f"{block['format']}" not in _MONTH_FIRST_MEMBERS:
            continue
        if (
            split is not None
            and position - 1 in split.present
            and split.cells[position - 1] is table_columns[position - 1]
            and split.settings == settings
        ):
            present = split.present[position - 1]
        else:
            present, _absent = taxonomy.split_missing(
                table_columns[position - 1], settings
            )
        seen = day_or_month_seen(present, f"{block['format']}")
        if seen is not None:
            found += [DayOrMonth(f"{block['name']}", seen.months, seen.days)]
    return tuple(found)


# The month-first member of each of the classifier's slashed pairs: the
# only readings the day-or-month question is asked of.
_MONTH_FIRST_MEMBERS = tuple(pair[0] for pair in taxonomy.SLASHED_PAIRS)


def _day_first_questions(
    found: "tuple[DayOrMonth, ...]",
) -> "list[Question]":
    """Which comes first, the day or the month, where no value can say.

    ONE QUESTION FOR THE FILE, because the answer is `--day-first` and
    that reaches every such column at once: a file written by one tool
    writes its dates one way. What it says was SEEN is the shape the
    columns share and, where one reading puts every date of a column on
    one calendar position and the other does not, that too -- read
    month first, month starts written `01/03/2023` all fall in January,
    which is the evidence a person needs to answer, and counts of
    calendar positions rather than of rows or cells.

    The reading that stands where nobody answers is month first, the
    ratified default, and it is the first choice because it is what
    Enter gives.
    """
    if not found:
        return []
    named = ""
    for one in found:
        quoted = f"'{one.name}'"
        named = quoted if not named else f"{named}, {quoted}"
    seen = (
        f"in {named}, every date's day and month are both 12 or less, so "
        f"each date reads as a real day with either one first, and nothing "
        f"in the values can say which your file writes first"
    )
    for one in found:
        if one.months == 1 and one.days > 1:
            seen = (
                f"{seen}; read month first, every date in '{one.name}' falls "
                f"in one month of the year, and read day first, every one "
                f"falls on one day of a month"
            )
        elif one.days == 1 and one.months > 1:
            seen = (
                f"{seen}; read month first, every date in '{one.name}' falls "
                f"on one day of a month, and read day first, every one falls "
                f"in one month of the year"
            )
    return [
        Question(
            DAY_FIRST_SUBJECT,
            "",
            BECAUSE_DAY_AND_MONTH,
            seen,
            [
                Choice(
                    ANSWER_MONTH_FIRST,
                    "the month comes first -- 03/04/2024 is the 4th of March",
                    (
                        "these columns as they are read now, month first, "
                        "and the twin writes their dates the same way"
                    ),
                ),
                Choice(
                    ANSWER_DAY_FIRST,
                    "the day comes first -- 03/04/2024 is the 3rd of April",
                    (
                        "every column of your file whose dates read either "
                        "way, read day first -- which is --day-first -- and "
                        "the twin writes their dates the same way; a column "
                        "whose own values say which comes first keeps that "
                        "order"
                    ),
                ),
            ],
            ANSWER_MONTH_FIRST,
        )
    ]


def _first_row_questions(seen: str) -> "list[Question]":
    """Which row the column names are in, where the file cannot say.

    THE QUESTION A FILE CANNOT ANSWER (the owner's ruling of 2026-09-17,
    item 8; plan P4-D232). A row of text above a table is the column
    names as often as it is the first record, and where the values below
    it mark it as a record -- or where a title stands above it, so that
    a headerless table and a headed one are the same bytes up to that
    row -- nothing in the file settles which. synthtwin takes the
    reading that publishes nothing of it: the columns are named
    `column_1`, `column_2` and so on and every row is kept, including
    that one. The other reading is a declaration, and this is where it
    is offered.

    WHAT IT SAYS WAS SEEN IS A FACT ABOUT THE FILE'S SHAPE, never a
    cell: a value in that row reads as a number, a value in it belongs
    among the values below it, or a line that is not a record stands
    above it. The row's own text is exactly what the standing reading
    withholds, so quoting it to ask about it would publish it.

    Guarantees: accepts what the file showed, in words, or the empty
    string where the reading was settled; returns at most one question;
    opens nothing; and carries no value of the table.
    """
    if not seen:
        return []
    return [
        Question(
            FIRST_ROW_SUBJECT,
            "",
            BECAUSE_FIRST_ROW_UNTOLD,
            seen,
            [
                Choice(
                    ANSWER_FIRST_ROW_DATA,
                    "the first row of the file is a record of the table",
                    (
                        "the columns are named column_1, column_2 and so "
                        "on, every row of the file is described, and no "
                        "text of the first row is published anywhere"
                    ),
                ),
                Choice(
                    ANSWER_FIRST_ROW_NAMES,
                    "the first row of the file holds the column names",
                    (
                        "the columns are named as that row names them, "
                        "which publishes its text in the description, in "
                        "the summary, in the twin and in the quality "
                        "report, and the table is described without it"
                    ),
                ),
            ],
            ANSWER_FIRST_ROW_DATA,
        )
    ]


def _delimiter_questions(tied: "tuple[str, ...]") -> "list[Question]":
    """Which delimiter a file that reads equally well two ways is written with.

    THE QUESTION THE CELLS CANNOT ANSWER (review item CODEX-4). A file
    written `id,pair|code` over rows such as `1,2|3` is two columns
    under the comma and two different columns under the vertical bar,
    and a count of the cells that read as numbers took the bar where an
    earlier version read the comma. Neither reading is wrong about the
    bytes, so the reading taken stands -- a file this tool twinned
    before may not be refused now -- and the person is asked. What the
    question names is the delimiters, never a cell.

    AND WHAT THE ANSWER COSTS IS SAID IN THE ANSWER (plan P4-D297, the
    merge-close of 2026-09-18). The merge skeptic measured the residue
    this question leaves: on `id,measure|low|high` over 120 rows of
    `i,{100+i%4}|90|110` the vertical bar wins and the comma is recorded,
    but the source's first column holds `0`, `1`, `2` beside its comma
    while the twin's holds `100|90|110`, so a comma reader finds two
    fields per row on the source and one on the twin. Both files
    validate at nought against the description, because no published
    fact is about the losing reading. Holding the twin's cells to the
    losing delimiter's field count as well would bind every made-up cell
    of every column to a second shape, against the length and form
    censuses those cells already owe; so the cost is stated here, where
    the person is choosing, rather than paid there.
    """
    if len(tied) < 2:
        return []
    word_of = {ANSWER_DELIMITERS[word]: word for word in ANSWER_DELIMITERS}
    choices: list[Choice] = []
    for one in tied:
        choices += [
            Choice(
                word_of[one],
                f"the columns are separated by {dialect.DELIMITER_WORDS[one]}",
                (
                    f"the file is read with {dialect.DELIMITER_WORDS[one]}, "
                    f"which decides every column name and every column's "
                    f"values, and the twin is written with it -- the "
                    f"twin's own cells are made up under this reading "
                    f"alone, so a reader that splits the twin by the "
                    f"other character need not find the rows your file "
                    f"gives it"
                ),
            )
        ]
    return [
        Question(
            DELIMITER_SUBJECT,
            "",
            BECAUSE_DELIMITER_TIE,
            (
                f"every record of your file splits cleanly, into one "
                f"steady number of columns, under {len(tied)} different "
                f"delimiters -- which need not be the same number of "
                f"columns under each -- so nothing in the values can "
                f"say which one your file uses"
            ),
            choices,
            word_of[tied[0]],
        )
    ]


def _metadata_questions(
    metadata_shape: bool, declared_unseen: int = 0
) -> "list[Question]":
    """The question about the rows under the column names.

    One subject, asked from either side: whether the rows under the
    column names describe those columns (plan P4-D81).

    WHERE THE SHAPE WAS SEEN it is asked because synthtwin will not act
    on a resemblance -- two records as wide as the header, the second
    every cell an ImportId object -- and NOTHING is done about it
    unless the person answers, because acting on the shape unasked is
    how a person's own record became schema text (review item
    CODEX-2).

    WHERE THE PERSON DECLARED SUCH ROWS AND THE SHAPE IS NOT THERE it
    is asked for the mirror-image reason (review of landing 2b.17,
    MAJOR). `--metadata-rows 2` on an ordinary table used to take two
    records out of it and publish them verbatim as the columns'
    description -- two people's rows, exempt from the smallest group,
    written into the twin, and gone from every count -- on the
    strength of a declaration the file plainly did not bear out. The
    rows now stay in the table and the person is asked here, where the
    answer says what it will cost before it is acted on. Answering
    `metadata-rows` in this file is what makes the declaration act,
    and it is a deliberate second step rather than a typing slip.

    Guarantees: a fixed function of the arguments; opens nothing; and
    carries no value of the table -- the shape it reports is a count of
    rows and the name of a marker synthtwin itself looks for.
    """
    if declared_unseen and not metadata_shape:
        return [
            Question(
                METADATA_SUBJECT,
                "",
                BECAUSE_DECLARED_UNSEEN,
                (
                    f"you said the {declared_unseen} row(s) under your "
                    f"column names describe those columns, and what "
                    f"synthtwin looked for and did not see is the shape "
                    f"such a file usually has: rows as wide as your "
                    f"table whose second holds a marker in every cell"
                ),
                [
                    Choice(
                        ANSWER_DATA,
                        "they are records of your table, like any other row",
                        (
                            "they stay in the table, counted and described "
                            "as data, which is what this run did"
                        ),
                    ),
                    Choice(
                        ANSWER_METADATA_ROWS,
                        (
                            "they describe the columns; they are not "
                            "anybody's record"
                        ),
                        (
                            "they are taken out of the table and published "
                            "as written, like the column names, and the "
                            "twin writes them back unchanged"
                        ),
                    ),
                ],
                ANSWER_DATA,
            )
        ]
    if not metadata_shape:
        return []
    return [
        Question(
            METADATA_SUBJECT,
            "",
            BECAUSE_EXPORT_SHAPE,
            (
                "the two rows under your column names are each as wide as "
                "the table, and every cell of the second is an ImportId "
                "marker -- the shape some survey tools write to describe "
                "their columns"
            ),
            [
                Choice(
                    ANSWER_DATA,
                    "they are records of your table, like any other row",
                    (
                        "both rows are counted and described as data, and "
                        "the twin holds a made-up row in each one's place"
                    ),
                ),
                Choice(
                    ANSWER_METADATA_ROWS,
                    "they describe the columns; they are not anybody's record",
                    (
                        "both rows are taken out of the table and published "
                        "as written, like the column names, and the twin "
                        "writes them back unchanged"
                    ),
                ),
            ],
            ANSWER_DATA,
        )
    ]


def _joining_mark(values: "list[str]") -> str:
    """The one mark every cell of a joined-looking column splits on."""
    for separator in taxonomy.JOINED_SEPARATORS:
        parts = 0
        for value in values:
            split = taxonomy.splits_into_numbers(value, separator)
            if split is None:
                parts = 0
                break
            if parts and len(split) != parts:
                parts = 0
                break
            parts = len(split)
        if parts >= 2:
            return separator
    return ""


def _sayable(count: int, population: int, floor: int) -> str:
    """A count of cells, or the word for one the floor will not name.

    THE DISCLOSURE FLOOR REACHES THE SHAPE TOO (review round 1 of
    landing L17a, item 2). At a smallest-group size of eleven, a column
    of one `001` beside 299 ordinary numbers said "1 of them carry a
    leading zero" -- a count of one, on a surface the plan holds to
    naming no count below the floor, reaching the prompt and, once the
    file lands, a document that travels.

    "Some" is not a count. That a column carries padding at all is a
    fact about how it was written, which is what the question is about;
    HOW MANY carry it is a count of a group, and a group smaller than
    the floor is not named here any more than anywhere else.

    AND THE COMPLEMENT IS A GROUP TOO -- the whole of the shared rule
    `parsing.census_nameable`, asked here as every other surface asks it
    (plan P4-D273, the repair of the extra review round of 2026-09-18).
    The floor alone reads the count and not what is left beside it, and
    the description that stands next to this file absorbs a spelling
    below the line into the column's commonest (ruling 6 of 2026-09-17).
    **Measured** at a floor of eleven, on 399 values `00001` to `00399`
    and one `12345`: the description published `numeric_styles
    {"leading_zero": 400}`, which says every value is padded, while this
    file recounted the cells for itself and said "399 of them carry a
    leading zero" -- and 400 present cells less 399 is the one unpadded
    record, restored on the surface beside the one that hid it. The
    count is now spoken only where it AND what it leaves over reach the
    line, so the file says "some of them" and the pair says nothing.

    Guarantees: accepts the count, the cells it was counted over and the
    settings floor; returns words carrying no value of the table.
    Determinism: a fixed function of the three. Raises nothing. No I/O.
    """
    if parsing.census_nameable([count], [population], floor):
        return f"{count} of them"
    return "some of them"


def _shape_of(
    reason: str,
    present: "list[str]",
    floor: int,
    mark: str = "",
    remainder: int = 0,
) -> str:
    """What synthtwin SAW, in words carrying no value of the table.

    THE DISCLOSURE RULE OF THE QUESTIONS FILE, made into a sentence
    (amendment A-P4-58; owner ruling 2026-09-10). The file may name the
    column, the choices, and any spelling the description itself would
    publish -- a separator is one, because the joined role publishes it
    -- and no value of the table. A count of how many cells carry a
    leading zero is a count and not a value; a width is a width.

    THE FLOOR HAS NO DEFAULT (plan P4-D317). It was 1, so a caller that
    left it out would have counted at a floor of one whatever the person
    asked for; the one caller passes the settings floor.

    Guarantees: accepts a reason, the present cells and the settings
    floor; returns one sentence. Determinism: a fixed function of those.
    Raises nothing. No I/O. **No cell of the column appears in what it
    returns.**
    """
    if reason == BECAUSE_REPEATS_AND_MANY:
        # THE TWO COUNTS THE RULE WAS MEASURED ON, and nothing else: how
        # many different values the column holds and how many cells
        # they stand on. Both are counts a description publishes about
        # every column anyway (`n_distinct_folded` and `n_present`), so
        # the file carries nothing here it does not carry there -- and
        # no cell of the column reaches this sentence.
        different: "dict[str, int]" = {}
        for value in present:
            different[parsing.folded(value)] = 1
        # ON AVERAGE, AND THE WORD IS LOAD-BEARING (review of stage 3,
        # floor item 4). This said "so each one stands on more than
        # one row", which was true of route two while route two demanded
        # it of every value -- and one subject with a single visit
        # silenced the whole question for exactly that reason. The rule
        # is now the average on both routes, so a register of twelve
        # subjects one of whom has one visit IS asked about, and the
        # sentence that says what was seen may not claim of that column
        # something the column does not do.
        return (
            f"{len(different)} different value(s) over {len(present)} "
            f"cell(s), so they stand on more than one row each on average"
        )
    if reason == BECAUSE_PADDED:
        padded = 0
        for value in present:
            if len(value) > 1 and value[0] == "0":
                padded = padded + 1
        return (
            f"every value is written in figures alone, and "
            f"{_sayable(padded, len(present), floor)} carry a leading zero"
        )
    if reason == BECAUSE_FIXED_WIDTH:
        # A COMPREHENSION RATHER THAN `add` (plan D6.2). The offline
        # audit reads the source and accepts no method call on a
        # value it cannot trace to an allowlisted API, which a local
        # set is not; `why_worth_asking` builds its widths the same
        # way one screen above.
        widths = {len(value) for value in present}
        only = 0
        for width in sorted(widths):
            only = width
        return (
            f"every value is written in figures alone, all {only} "
            f"characters wide"
        )
    if reason == BECAUSE_GROUPED_FIXED_WIDTH:
        # THE WIDTH IN FIGURES, NOT IN CHARACTERS: the mark between the
        # groups is not a figure, and "eleven characters" would name a
        # width no identifier has.
        counted: "list[int]" = []
        for value in present:
            figures = _grouped_figures(value)
            counted += [len(value) if figures is None else len(figures)]
        only = 0
        for width in sorted(counted):
            only = width
        return (
            f"every value is written in figures, grouped in threes, all "
            f"{only} figures long"
        )
    if reason == BECAUSE_TWELVE_HOUR:
        # WHAT BOTH CLOCKS WRITE, and no count: the shape alone is why.
        # ``remainder`` is the column's count of cells it did not read,
        # named under the floor as every count here is; where there are
        # some, the sentence is about the cells it read and not "every
        # value" (the T1 review's item 10).
        if remainder > 0:
            return (
                f"every time of day it reads has its hour from 1 to 12, "
                f"with no AM or PM, which a 24-hour clock and a 12-hour "
                f"clock both write, and "
                f"{_sayable(remainder, len(present), floor)} write no time "
                f"of day it reads"
            )
        return (
            "every value writes a time of day whose hour is from 1 to 12, "
            "with no AM or PM, which a 24-hour clock and a 12-hour clock "
            "both write"
        )
    if reason == BECAUSE_FEW_CLOCK_TIMES:
        # HOW MANY DIFFERENT TIMES, which the description publishes as
        # `n_distinct_folded`, and the line every time inside the range
        # reaches (`_times_each_shared`), a setting; nothing else.
        times: "dict[str, int]" = {}
        for value in present:
            times[parsing.folded(value)] = 1
        return (
            f"its values are times of day, every one inside its range written "
            f"by at least {parsing.census_floor(floor)} rows, and the column "
            f"holds only {len(times)} different value(s) over {len(present)} "
            f"cell(s), which a list of labels written as times also holds"
        )
    if reason == BECAUSE_POINT_THOUSANDS:
        return (
            "every value with a point has exactly three figures after it, "
            "and every value without one is below a thousand, which is "
            "also how numbers are written with a point between their "
            "thousands"
        )
    if reason == BECAUSE_JOINED:
        # ``mark`` is the separator a joined column publishes, spaces and
        # all; ``remainder`` its count of cells that are not such a pair,
        # named under the floor as every count here is.
        if not mark:
            mark = _joining_mark(present)
        if remainder > 0:
            return (
                f"values are two or more numbers with '{mark}' between "
                f"them, and {_sayable(remainder, len(present), floor)} "
                f"are not"
            )
        return (
            f"every value is two or more numbers with '{mark}' between "
            f"them"
        )
    return "this column could be read more than one way"


# A COLUMN NAMED ON THE CHECKLIST RATHER THAN ASKED ABOUT (owner
# ruling 2026-09-10, decision D14 of the close plan). Nothing in its
# values raised a question -- an unpadded, variable-width column of
# figures is written exactly as a count is -- so no rule can find it
# and no remark can honestly single it out. What reaches it is a
# person reading one list of every column that was read as a number.
BECAUSE_LISTED = "listed"
# ...and its sibling: a column already read as codes, listed so the
# person can see the whole register in one place and correct it if the
# reading is wrong.
BECAUSE_LISTED_AS_CODES = "listed-as-codes"

# The roles whose description carries statistics over the cells. A
# column here that is really a coding system publishes an average over
# its codes, which is the hazard the checklist exists to reach.
_MEASURED_ROLES = (
    taxonomy.ROLE_COUNT,
    taxonomy.ROLE_CONTINUOUS,
    taxonomy.ROLE_UNREPRESENTABLE,
    taxonomy.ROLE_AFFIXED,
    taxonomy.ROLE_COMPOUND,
)
# The roles that publish the values themselves. A code column that
# reached one of these is already described the way its owner wants,
# and is listed only so they can say if it is not.
_LABELLED_ROLES = (
    taxonomy.ROLE_CATEGORICAL,
    taxonomy.ROLE_LONG_TAIL,
)


def _looks_like_a_code(present: "list[str]") -> bool:
    """Whether these cells are written the way a coding system writes.

    Figures with a letter, a dot or a dash among them, no spaces, and
    short. This decides NOTHING -- it chooses which columns a person is
    shown on one list, and being shown costs a line of reading where
    being missed costs the column's description.
    """
    if not present:
        return False
    for value in present:
        if not value or len(value) > 20:
            return False
        figures = False
        for mark in value:
            if "0" <= mark <= "9":
                figures = True
            elif mark not in ".-_/" and not (
                "a" <= mark <= "z" or "A" <= mark <= "Z"
            ):
                return False
        if not figures:
            return False
    return True


def checklist_for(
    document: "dict[str, object]",
    table_columns: "list[list[str]]",
    settings: taxonomy.Settings,
    already: "list[str]",
    asked: "list[Question]",
    answered: "tuple[Question, ...]" = (),
) -> "list[Question]":
    """Every column read as a number, listed once for one question.

    THE SHAPES NO RULE CAN SEE (owner ruling 2026-09-10, decision D14).
    A register of drug concept identifiers six and seven figures wide,
    a column of month codes 1 to 12, a set of case-mix codes 5, 470 and
    871 -- each is written exactly as a count is written, each is
    published with an average over its codes, and NOTHING in the values
    can tell them apart from a quantity. The rule that would find them
    was deleted in review item P1-R6-F7 for guessing, and every
    replacement measured wrong.

    So they are not guessed at and not remarked at either: they are
    LISTED, once, under one question. A person who holds the table
    reads one list and names the ones that are codes. That is the
    cheapest true thing this tool can do about a class of column no
    amount of cleverness will reach.

    ONE QUESTION AND NOT N, which is what keeps it from being a burden
    (amendment A-P4-56, point 1). Asking is for what a count cannot
    settle; it is not a way to move work onto the person. A list of
    twelve columns with one question over it is a minute's reading. A
    separate question per column is a form nobody finishes.

    Guarantees:

    - Inputs: the profile document, the table's columns as text in the
      same order, the settings that produced it, the names already
      declared, the questions already asked so no column appears
      twice, and the columns whose date codes were answered kept
      (`DateCodesSeen.answered`). Those are not listed as already read
      as codes -- the answer settled what their values are -- but one
      the answer leaves read as a measurement IS listed, because its
      description still carries statistics over its values (second
      review of lane R1, item 3: a DateKey column answered
      `real-value` had lost its line).
    - Determinism: a fixed function of the arguments.
    - Errors raised: none.
    - Boundary: opens no file, prints nothing, and no cell of any
      column appears in what it returns.
    """
    blocks = document["columns"]
    if not isinstance(blocks, list):
        return []
    spoken: list[str] = []
    for question in asked:
        spoken += [question.name]
    settled: list[str] = []
    for question in answered:
        settled += [question.name]
    listed: list[Question] = []
    position = 0
    for block in blocks:
        if not isinstance(block, dict):
            position = position + 1
            continue
        name = f"{block['name']}"
        role = f"{block['role']}"
        if name in already or name in spoken:
            position = position + 1
            continue
        if position >= len(table_columns):
            position = position + 1
            continue
        present, _absent = taxonomy.split_missing(
            table_columns[position], settings
        )
        if role in _MEASURED_ROLES:
            listed += [
                Question(
                    name,
                    role,
                    BECAUSE_LISTED,
                    "read as a measurement, so its description carries "
                    "statistics over these values",
                    _numeric_choices(
                        ANSWER_MEASUREMENT,
                        role,
                        settings.small_cell_floor,
                    ),
                    ANSWER_MEASUREMENT,
                )
            ]
        elif (
            role in _LABELLED_ROLES
            and name not in settled
            and _looks_like_a_code(present)
        ):
            listed += [
                Question(
                    name,
                    role,
                    BECAUSE_LISTED_AS_CODES,
                    "already read as codes: "
                    + _publishes_under(
                        ANSWER_KEEP, role, settings.small_cell_floor
                    ),
                    _numeric_choices(
                        ANSWER_CODE, role, settings.small_cell_floor
                    ),
                    ANSWER_CODE,
                )
            ]
        position = position + 1
    return listed


# THE ROLES A COLUMN THAT NAMES PEOPLE CAN HOLD (plan P4-D340): every
# role EXCEPT the ones whose description is a distribution over the
# numbers themselves, the calendar and clock roles, and the empty one.
# A subject number is written `P00017`, `SUBJ0004` or `A-1000` and is
# read as numbers wearing an affix, or as text, or as labels; a column
# read as plain numbers, as a date or as a clock time is reached by the
# checklist question instead, which lists every column read as a
# number so that a register of codes can be named there.
#
# WHY THE NUMERIC ROLES ARE OUT, measured rather than assumed. On the
# subject design's tables a `score` of whole numbers 0 to 100 repeats
# 3 to 28 times per value and a `weight` repeats 1.6 to 5.1 times, both
# with more different values than a set of categories may hold -- so
# every bounded scale the owner named on 2026-09-22 -- a pain score of
# 0 to 10, a risk grade, a rating item, a coma scale, ages in whole
# years -- would be asked about on this rule if the role did not
# exclude it.
_PERSON_ROLES_EXCLUDED = (
    taxonomy.ROLE_EMPTY,
    taxonomy.ROLE_COUNT,
    taxonomy.ROLE_CONTINUOUS,
    taxonomy.ROLE_UNREPRESENTABLE,
    taxonomy.ROLE_COMPOUND,
    taxonomy.ROLE_JOINED,
    taxonomy.ROLE_DATETIME,
    taxonomy.ROLE_CLOCK,
)

# HOW OFTEN A VALUE HAS TO STAND ON A ROW before the column can be
# naming people: two rows per different value on average. One is a key
# with a row each, which names nobody.
PERSON_ROWS_PER_VALUE = 2


def _names_people(
    present: "list[str]", role: str, n_rows: int, settings: taxonomy.Settings
) -> bool:
    """Whether this column looks like it names the people the rows are about.

    TWO ROUTES, EITHER OF WHICH ASKS. The first was the whole rule when
    landing 3.2 was written and could not reach the case the plan cites
    as its reason for existing; the second is the repair.

    ROUTE ONE -- MANY VALUES, REPEATING (plan P4-D340).

    * Its present values REPEAT: at least `PERSON_ROWS_PER_VALUE` rows
      per different folded value, on average. A value on one row each
      names a row, not a person.
    * It holds MORE DIFFERENT VALUES THAN A SET OF CATEGORIES COULD
      HAVE HAD in a table of this many rows -- `taxonomy.
      categories_ceiling`, the line `categorical_share` and
      `categorical_ceiling` already record in every description. That
      is the line, asked rather than restated.

    ROUTE TWO -- A REGISTER OF CODES (repair of landing 3.2). Route
    one's second condition is the exact COMPLEMENT of the rule that
    makes a column `categorical` (`_categorical_ceiling` over the same
    row count), so route one can only ever fire on a column that
    publishes NO levels -- and the column the plan was written about
    publishes every one of them. 12 subjects over 1,196 rows read as
    `categorical`, and `subject_id` came back with all twelve
    identifiers beside their visit counts and no question asked. So a
    column also clears the rule when

    * its present values REPEAT, which is route one's FIRST condition
      unchanged: at least `PERSON_ROWS_PER_VALUE` rows per different
      folded value, on average; and
    * every present cell is WRITTEN AS A CODE: inside the code alphabet
      (`parsing.is_code_text`, which is the positive evidence the
      identifier rule itself asks for) and carrying both a letter and a
      figure. The letter is what keeps a bare-figure column out -- a
      binary 0/1, a group coded 1/2/3, an ordinal 0 to 10 -- and the
      figure is what keeps a column of words out, `site`, `arm`,
      `North`, `yes`/`no`. Measured: with the figure alone required, a
      0/1 column clears the rule; with both required, no column of the
      battery that is not a code does.

    ROUTE TWO'S FIRST CONDITION WAS "EVERY VALUE ON TWO ROWS OR MORE",
    AND ONE SINGLE-VISIT SUBJECT SILENCED IT (review of stage 3, floor
    finding 4). The stricter form was recorded as a measured limit and
    left standing; the review reproduced what the limit costs, which is
    the whole question going unasked on a register of twelve subjects
    where ONE of them has one visit -- a register of people, published
    identifier by identifier, that one row decides. ONE ROW MAY NOT
    SETTLE WHO THE TABLE IS ABOUT, so the condition is now route one's
    average, counted and never divided. What it still keeps out is what
    the stricter form was for: a per-row key holds as many different
    values as it has cells, so `len(present) >= 2 x len(different)` is
    false of `record`, `subject` and `visit_id` by a factor of two,
    whether or not one value of them repeats.

    WHAT ROUTE TWO ALSO REACHES, AND IS ACCEPTED (ledger K-S3-02). A
    `ward-12`-shaped label column and a register of diagnosis-like
    codes are written exactly as a subject register is written, and
    nothing in the values tells them apart. They are asked about. The
    cost of a false positive here is ONE question whose standing answer
    is `keep`, and the cost of the miss it replaces was a description
    that published twelve people's identifiers; the trade is taken
    deliberately and the count is held at its measured value in the
    ledger. Route one already asked about a 60-ward column over 500
    rows and about a repeating free-text remarks column before this
    repair, which is why the docstring that said `ward` could not
    clear this rule was wrong when it was written.

    MEASURED ON THE BATTERIES THE RULE WAS CHOSEN ON. Over the four
    realistic families of `tests/kpi_shapes.py` (twelve columns, run
    with the declarations they ship and with every declaration removed)
    and five tables of the subject design -- fixed 100x5, fixed 150x3,
    geometric 1,000, and 1 to 8 visits over 40 and over 22 subjects --
    the rule is true of the five `subject_id` columns and of nothing
    else: `dose`
    (40 different values over 400 cells) and `note` (9 over 400) are
    sets of categories, fall at route one's second condition and are
    not written as codes; `record`, `subject` and `visit_id` are
    different on every row and fall at the first condition both routes
    now share; `score`, `weight`, `amount` and both date columns are
    excluded by role.

    Guarantees: accepts the present cells, the role the column holds,
    the table's rows and the settings; returns a truth value. A fixed
    function of those. Raises nothing. No I/O, and no cell reaches
    anything it returns.
    """
    if role in _PERSON_ROLES_EXCLUDED:
        return False
    if not present:
        return False
    different: "dict[str, int]" = {}
    for value in present:
        key = parsing.folded(value)
        if key in different:
            different[key] = different[key] + 1
        else:
            different[key] = 1
    # COUNTED, never divided: `len(present) / len(different) >= 2` is
    # the same question as this one and asks a float to decide a
    # question about rows.
    #
    # AND IT IS THE CONDITION BOTH ROUTES SHARE (review of stage 3,
    # floor item 4). Route two asked "every different value on two
    # rows or more" until then, which one subject with a single visit
    # made false -- so one row silenced the question on a register of
    # twelve people. The two routes now differ in their SECOND condition
    # alone: many values, or every cell a code.
    if len(present) < PERSON_ROWS_PER_VALUE * len(different):
        return False
    if len(different) > taxonomy.categories_ceiling(n_rows, settings):
        return True
    return _a_register_of_codes(present)


def _a_register_of_codes(present: "list[str]") -> bool:
    """Route two's second condition: every cell is written as a code.

    Split out so that each half of the rule can be mutated on its own
    and so that the loop over the cells stops at the first cell that is
    not a code rather than folding the whole column first. The half that
    asks how often a value repeats is the caller's, because both routes
    ask it and one question belongs in one place.

    Guarantees: accepts the present cells; returns a truth value. A
    fixed function of them. Raises nothing. No I/O, and no cell reaches
    anything it returns.
    """
    if not present:
        return False
    for value in present:
        if not parsing.is_code_text(value):
            return False
        figure = False
        letter = False
        for character in value:
            if "0" <= character <= "9":
                figure = True
            elif ("a" <= character <= "z") or ("A" <= character <= "Z"):
                letter = True
        if not figure or not letter:
            return False
    return True


def person_questions(
    document: "dict[str, object]",
    table_columns: "list[list[str]]",
    settings: taxonomy.Settings,
    already: "list[str]",
    asked: "list[Question]",
    split: "SplitColumns | None" = None,
) -> "list[Question]":
    """The question about who the rows are, where nobody has said.

    ASKED ONLY WHERE THE POPULATION IS COUNTED IN PEOPLE ALREADY, which
    is `settings.person_columns` -- the declared identifiers that REPEAT
    -- and NOT where any identifier at all is declared (review of stage
    3, floor item 4). A DECLARATION IS NOT AN ANSWER TO THIS
    QUESTION unless it settles who the rows are about, and one that is
    different on every row settles nothing: it names a ROW.
    `taxonomy.repeating_identifiers` says at length what that
    distinction cost when it was measured, and the same distinction is
    what this rule reads. Measured on the tree before this repair: 1,196
    visits over twelve people with a unique-per-row `visit_id` declared
    and nothing else left `person_columns` correctly EMPTY -- the
    population was counted in rows -- while the declaration silenced the
    question, so the run published the twelve subject codes, asked
    nothing, and printed neither the population notice nor the notice
    that it had counted rows. Declaring the subject column refuses the
    same table as twelve people.

    ASKING IS PART OF THE PRODUCT (amendments A-P4-56 and A-P4-58), and
    this is the column class nothing else reaches. Until it existed a
    table of 12 subjects over 1,196 rows passed the population floor on
    its rows with no notice, and `subject_id` was described as a set of
    categories with every subject's identifier published beside its
    visit count. THAT EXACT CASE was still unreachable when landing 3.2
    was written -- the rule's second condition was the complement of
    the one that makes a column `categorical`, so it could fire only on
    a column publishing no levels -- and route two of
    `_names_people` is what reaches it.

    Guarantees:

    - Inputs: the profile document, the table's columns as text in the
      same order, the settings that produced it -- whose
      `person_columns` is what says whether anybody has settled who the
      rows are about -- the names already declared any way at all, the
      questions already asked so no column is asked twice, and what
      `questions_and_splits_for` split out of the same columns, taken
      where it was split from the same column under the same settings
      so no column is split twice (none means every column is split
      here).
    - Determinism: a fixed function of the arguments, in the table's
      own column order.
    - Errors raised: none.
    - Boundary: opens no file, prints nothing, and no cell of any
      column appears in what it returns.
    """
    if settings.person_columns:
        return []
    blocks = document["columns"]
    if not isinstance(blocks, list):
        return []
    spoken: "list[str]" = []
    for question in asked:
        spoken += [question.name]
    rows = document["n_rows"]
    if not isinstance(rows, int):
        return []
    found: "list[Question]" = []
    position = 0
    for block in blocks:
        if not isinstance(block, dict):
            position = position + 1
            continue
        name = f"{block['name']}"
        role = f"{block['role']}"
        if name in already or name in spoken:
            position = position + 1
            continue
        if position >= len(table_columns):
            position = position + 1
            continue
        if (
            split is not None
            and position in split.present
            and split.cells[position] is table_columns[position]
            and split.settings == settings
        ):
            present = split.present[position]
        else:
            present, _absent = taxonomy.split_missing(
                table_columns[position], settings
            )
        if _names_people(present, role, rows, settings):
            found += [
                Question(
                    name,
                    role,
                    BECAUSE_REPEATS_AND_MANY,
                    _shape_of(
                        BECAUSE_REPEATS_AND_MANY,
                        present,
                        settings.small_cell_floor,
                    ),
                    _person_choices(role, settings.small_cell_floor),
                    ANSWER_KEEP,
                )
            ]
        position = position + 1
    return found


def _person_choices(role: str, floor: int) -> "list[Choice]":
    """The two answers the person question may take.

    `keep` is first because it is what standing still gives: nobody
    declared this column, so the reading in force is the one it already
    has, and a list whose first entry is not the standing reading
    misleads whatever the words underneath say.
    """
    return [
        Choice(
            ANSWER_KEEP,
            "not a person -- it repeats for some other reason, and the "
            "reading it has now is right",
            _publishes_under(ANSWER_KEEP, role, floor),
        ),
        Choice(
            ANSWER_IDENTIFIER,
            "the people the rows are about -- rows sharing a value of "
            "it are one person, and it is a key nothing should publish",
            _publishes_under(ANSWER_IDENTIFIER, role, floor),
        ),
    ]


# HOW FEW, HOW OFTEN AND HOW MUCH (lane R1, plan P4-D381). A column is
# asked about where at most five different spellings read as no date or
# time, each on at least eleven rows -- the default smallest group, and
# never fewer than the run's own -- which together hold at most a tenth
# of its present cells, beside at least three different dates or times.
# Fewer rows is a slip of a keyboard as often as a code, and a spelling
# on fewer rows than the floor is one the description would not name;
# more spellings, or more of the column, is a column of something else
# with some dates in it, which is a different question (the reach
# audit's Q6, not asked here).
_DATE_CODES_MOST = 5
_DATE_CODES_LINE = 11
_DATE_CODES_SHARE = 10
_DATE_CODES_VARIETY = 3


@dataclasses.dataclass(frozen=True)
class DateCodes:
    """A column of dates or times beside a few repeated codes, as seen.

    `reading` is the date member or clock form the rest of the column
    reads under at the date rule's own line, and `n_read` how many of
    its `n_present` cells that reading parses -- in a question that is
    put, the reading the classifier gives the column once the codes are
    declared missing, and every present cell that is neither a code nor
    one that run leaves unread, a stand-in date it sets aside counted
    read (`_as_the_classifier_reads`). `codes` holds each code
    once -- one spelling for each declaration a person could type, the
    one most of its cells wore -- with the rows that wore it.

    The spellings are kept HERE, inside one run, and go no further than
    the declaration they become: the question that is put names how many
    codes there are, how each is written and how many rows hold it, and
    no code itself (amendment A-P4-58: the questions file carries no
    value of the table).
    """

    reading: str
    codes: "tuple[tuple[str, int], ...]"
    n_read: int
    n_present: int


def _declared_identity(
    spelling: str, decimal_comma: bool = False
) -> "tuple[str, object]":
    """What a declaration naming this spelling would match, as a key.

    The rule `taxonomy.Settings.declaration_matching` records, asked
    here of a code rather than of a declaration: a spelling that reads
    as a number this format can hold is that EXACT number, and any other
    is its trimmed, case-folded text. Two spellings with one key are one
    `--missing-value` -- `UNK` and `unk`, `-1` and `-1.0`.

    ``decimal_comma`` asks it of a column declared `--decimal-comma`,
    whose number is read from the swapped spelling, as
    `taxonomy._declarations` reads a declaration and `taxonomy._classify`
    a cell there: in such a column `-1,0` is the number -1, which a
    declaration naming `-1` takes.
    """
    read = spelling
    if decimal_comma:
        read = parsing.written_with_a_decimal_comma(spelling)
    exact = parsing.exact_of_spelling(read)
    if exact is not None:
        return ("number", exact)
    return ("text", parsing.folded(spelling))


def declared_identity(spelling: str) -> "tuple[str, object]":
    """What a declaration naming this spelling would match, as a key.

    `_declared_identity`, for the run that turns answers into
    declarations: two spellings with one key are one declaration, and
    are named once.

    Guarantees: accepts one spelling; returns its key. Determinism: a
    function of the text. Raises TypeError if it is not text. No I/O.
    """
    return _declared_identity(spelling)


def _a_date_or_a_time(spelling: str, last: str) -> str:
    """The member or clock form one spelling reads under, or nothing.

    ``last`` is the member the previous date of the column read under,
    tried first, so a column of dates costs about one parse a spelling.
    """
    if last and last in parsing.DATE_FORMATS:
        if parsing.parse_datetime(spelling, last) is not None:
            return last
    for format_name in parsing.DATE_FORMATS:
        if parsing.parse_datetime(spelling, format_name) is not None:
            return format_name
    form = parsing.clock_form(spelling)
    if form is not None:
        return form
    return ""


def date_codes_of(
    present: "list[str]",
    settings: taxonomy.Settings,
    n_rows: "int | None" = None,
    counting_kept: bool = False,
) -> "DateCodes | None":
    """The few repeated codes a column of dates or times writes, or None.

    THE COLUMN THE DATE RULE MISSES BY A FEW SPELLINGS (lane R1 of stage
    3b, plan P4-D381; the reach audit's Q2). The date rule reads a
    column whose cells parse at its line, 99 in 100, and a column of
    dates that writes `UNK` on 3 in 100 does not: it is read as labels,
    and its twin holds strings no date reader takes. Measured on
    668f276, a thousand cells each: `00/00/0000`, `UNK` beside
    `03/17/2023`, `0000-00-00`, `UNK` beside ISO dates, Caboodle's `-1`
    and `-2` beside `20221206`, and `99:99` and `UNK` beside `14:05` --
    the twins parse 0 to 59 in 100 under the person's own format, and
    every one parses all of them once the codes are named with
    `--missing-value`, which also writes them back where they were
    counted.

    What is asked of the column, in order, each step cheaper than the
    next:

    1. the spellings standing on at least the line's rows (eleven, or
       the run's floor where that is higher) that read as no date member
       and no clock form are its CODES, grouped as one declaration would
       match them; a spelling the person declared kept with
       `--keep-value` is no code, because that is their answer --
       unless ``counting_kept`` asks for the codes as they stand
       whatever was kept, which is how a column whose codes were
       answered `real-value` is still known for one asked about them
       (an answer of `missing` reaches a code typed kept through
       `date_codes_answered`, which takes that typed word out); and
       each code's rows are every cell its declaration would take, any
       spelling under the line it matches counted in, while a
       declaration that would also take a cell some date member or
       clock form reads is no code (the Codex review of lane R1, item 2);
    2. there are one to five of them;
    3. together they hold at most a tenth of the present cells;
    4. at least three different spellings are left; and
    5. what is left clears the date rule's own line
       (`taxonomy.reading_of_the_rest`, over the table's ``n_rows``,
       which the clock half's categories line is a share of).

    A spelling on fewer rows stays among what is left and counts against
    the line there, as it does in the column itself.

    Guarantees: accepts the present cells, in row order, the settings
    they were split under and the table's rows (the present cells'
    count where none is given); returns what was seen or None.
    Determinism: a function of the arguments. Raises TypeError if a cell is
    not text. No I/O of any kind.
    """
    found = _codes_and_rest(
        _spellings_counted(present),
        len(present),
        settings,
        len(present) if n_rows is None else n_rows,
        counting_kept,
    )
    return None if found is None else found[0]


def _spellings_counted(present: "list[str]") -> "dict[str, int]":
    """Each different spelling of a column once, with the rows that wore it."""
    counted: "dict[str, int]" = {}
    for value in present:
        if value in counted:
            counted[value] = counted[value] + 1
        else:
            counted[value] = 1
    return counted


def _codes_and_rest(
    counted: "dict[str, int]",
    n_present: int,
    settings: taxonomy.Settings,
    n_rows: int,
    counting_kept: bool,
) -> "tuple[DateCodes, dict[str, int]] | None":
    """`date_codes_of` over a column's counted spellings, with what is left.

    The second half is each different spelling of what is left with
    the rows that wore it, which is what the day-or-month question asks
    of the same column (`date_codes_seen`) without counting it again;
    and the count is taken once by the caller, so asking a column twice
    -- once as it stands and once whatever was kept -- counts it once.
    """
    if not counted:
        return None
    line = max(_DATE_CODES_LINE, parsing.census_floor(settings.small_cell_floor))
    kept: "list[tuple[str, object]]" = []
    if not counting_kept:
        for spelling in settings.kept_values:
            kept += [_declared_identity(spelling)]
    keys: "list[tuple[str, object]]" = []
    spelled: "list[str]" = []
    rows: "list[int]" = []
    taken: "dict[str, int]" = {}
    last = ""
    for spelling in counted:
        if counted[spelling] < line:
            continue
        reading = _a_date_or_a_time(spelling, last)
        if reading:
            last = reading
            continue
        key = _declared_identity(spelling)
        if key in kept:
            continue
        taken[spelling] = 1
        place = -1
        for index in range(len(keys)):
            if keys[index] == key:
                place = index
        if place < 0:
            keys += [key]
            spelled += [spelling]
            rows += [counted[spelling]]
            if len(keys) > _DATE_CODES_MOST:
                return None
            continue
        # One declaration, several spellings: the rows add up, and the
        # spelling named is the one most of them wore, the first on a tie.
        if counted[spelling] > counted[spelled[place]]:
            spelled[place] = spelling
        rows[place] = rows[place] + counted[spelling]
    if not keys:
        return None
    # THE WHOLE REACH OF EACH DECLARATION IN THIS COLUMN (the Codex review
    # of lane R1, item 2). `--missing-value` takes every cell it matches,
    # not only the spellings that stood on the line: measured before
    # this, 20 `UNK` beside 5 `unk` were said to be a code on 20 rows and
    # the answer took 25, and 20 cells of `20,230,101` -- the number
    # 20230101 -- were said to be a code on 20 rows while the answer also
    # took the 80 cells of `20230101`, every one a real first of January.
    # So every other spelling a declaration would match is counted in --
    # and a declaration that would take a cell some date member or clock
    # form reads is no code at all, since answering it would take real
    # dates out of the column with it.
    place_of: "dict[tuple[str, object], int]" = {}
    for index in range(len(keys)):
        place_of[keys[index]] = index
    reach: "dict[str, int]" = {}
    poisoned: "dict[int, int]" = {}
    for spelling in counted:
        if spelling in taken:
            continue
        key = _declared_identity(spelling)
        if key not in place_of:
            continue
        if _a_date_or_a_time(spelling, ""):
            poisoned[place_of[key]] = 1
            continue
        reach[spelling] = place_of[key]
    for spelling in reach:
        index = reach[spelling]
        taken[spelling] = 1
        if counted[spelling] > counted[spelled[index]]:
            spelled[index] = spelling
        rows[index] = rows[index] + counted[spelling]
    if poisoned:
        kept_keys: "list[tuple[str, object]]" = []
        kept_spelled: "list[str]" = []
        kept_rows: "list[int]" = []
        for index in range(len(keys)):
            if index not in poisoned:
                kept_keys += [keys[index]]
                kept_spelled += [spelled[index]]
                kept_rows += [rows[index]]
        still: "dict[str, int]" = {}
        for spelling in taken:
            if _declared_identity(spelling) in kept_keys:
                still[spelling] = 1
        taken = still
        keys = kept_keys
        spelled = kept_spelled
        rows = kept_rows
        if not keys:
            return None
    coded = 0
    for held in rows:
        coded = coded + held
    if coded * _DATE_CODES_SHARE > n_present:
        return None
    rest: "dict[str, int]" = {}
    for spelling in counted:
        if spelling not in taken:
            rest[spelling] = counted[spelling]
    if len(rest) < _DATE_CODES_VARIETY:
        return None
    reading_of = taxonomy.reading_of_the_rest(rest, settings, n_rows)
    if reading_of is None:
        return None
    codes: "list[tuple[str, int]]" = []
    for index in range(len(keys)):
        codes += [(spelled[index], rows[index])]
    return (
        DateCodes(reading_of[0], tuple(codes), reading_of[1], n_present),
        rest,
    )


def _code_written(spelling: str) -> str:
    """How one code is written, in words that name no character of it.

    Its length and the kinds of character it holds -- letters, figures,
    a leading minus sign, other marks -- and nothing else, which is what
    the questions file may say of a cell (amendment A-P4-58).
    """
    body = parsing.trimmed(spelling)
    letters = 0
    figures = 0
    marks = 0
    for character in body:
        if "0" <= character <= "9":
            figures = figures + 1
        elif ("a" <= character <= "z") or ("A" <= character <= "Z"):
            letters = letters + 1
        else:
            marks = marks + 1
    if letters and not figures and not marks:
        return f"{letters} letter(s)"
    if figures and not letters and not marks:
        return f"{figures} figure(s)"
    if figures and not letters and marks == 1 and body[:1] == "-":
        return f"a minus sign and {figures} figure(s)"
    if figures and not letters:
        return f"{figures} figure(s) with {marks} mark(s) among them"
    if letters and figures:
        return f"{len(body)} characters, letters and figures among them"
    return f"{len(body)} character(s)"


# The made-up instant every clock form is shown by in a sentence, beside
# `parsing.format_example` for the date members: 14:05:30, written in the
# form itself (`14:05`, `2:05 PM`, `02:05:30pm`), so each of T1's forty
# forms has its example (the Codex review of lane R1, item 4).
_CLOCK_EXAMPLE_SECOND = 14 * 3600 + 5 * 60 + 30


def _reads_as_a_clock(reading: str) -> bool:
    """Whether a reading is a clock form rather than a date member."""
    return reading in parsing.CLOCK_FORMS


def date_codes_reading(found: DateCodes) -> str:
    """What the rest of a column reads as, in the words a person meets.

    Guarantees: accepts what `date_codes_of` saw; returns a phrase that
    names the reading by a made-up example of its own (`03/17/2024`,
    `14:05`, `2:05 PM`) and no cell of the column. Determinism: a
    function of the reading. Raises nothing. No I/O.
    """
    if _reads_as_a_clock(found.reading):
        example = parsing.written_clock(
            _CLOCK_EXAMPLE_SECOND,
            parsing.clock_step(found.reading) == 1,
            parsing.clock_style_of(found.reading),
        )
        return f"times of day written as {example}"
    return f"dates written as {parsing.format_example(found.reading)}"


def _date_codes_shape(
    found: DateCodes, floor: int, elsewhere: "tuple[Elsewhere, ...]" = ()
) -> str:
    """What synthtwin saw in a column of dates beside a few codes.

    EVERY COUNT HERE IS ONE THE DISCLOSURE RULE LETS THROUGH, and by
    construction rather than by a test made here: each code stands on at
    least the line's rows, which is never under `parsing.census_floor`,
    and together they hold at most a tenth of the column, so what each
    leaves over -- and what the date reading leaves over, which holds
    every code -- reaches the line too. A branch that printed words in
    place of these numbers could never be taken, and is not written.
    The counts of OTHER columns are not held to that construction, and
    `_elsewhere_words` asks the rule of each.
    """
    read = f"{found.n_read} of the {found.n_present} values"
    which = date_codes_reading(found)
    also = ""
    if elsewhere:
        also = (
            f". The same spellings stand in other columns of your table: "
            f"{_elsewhere_words(elsewhere, floor)}"
        )
    # THE CELLS THAT ARE NEITHER, SAID (the Codex review of lane R1, item
    # 6). The date rule's line leaves room for one cell in a hundred to
    # read as nothing, so "every other value is" one of the codes was
    # false wherever some did: 975 dates, 20 `UNK` and five `ODD` were
    # said to be dates and one code, and the answer left five cells
    # unread. Their count is said where the disclosure rule lets it
    # through, and "a few" where not.
    others = "every other value"
    unread = _date_codes_unread(found)
    if unread:
        others = f"every other value but {_unread_words(found, floor)}"
    lead = f"{read} read as {which}, and {others} is {_codes_said(found)}"
    if unread:
        lead = (
            f"{lead}; those left read as none of these and as no "
            f"{_read_kind(found)}, and stay unread whatever the answer"
        )
    return f"{lead}{also}"


def _codes_said(found: DateCodes) -> str:
    """The words a question says its codes in: how many, how each is written, on how many rows.

    One sentence's middle, which `_date_codes_shape` puts in the question
    and `date_codes_answered` looks for in a question handed back: the
    same words for the same codes, and different words wherever the
    count of codes, the way one is written or the rows of one differ.
    """
    named = ""
    for spelling, held in found.codes:
        one = f"written in {_code_written(spelling)}, on {held} rows"
        if len(found.codes) > 1:
            one = f"one {one}"
        named = one if not named else f"{named}; {one}"
    if len(found.codes) == 1:
        return (
            f"one spelling, repeated on many rows, that reads as no date "
            f"or time: {named}"
        )
    return (
        f"one of {len(found.codes)} spellings, each repeated on many rows, "
        f"that read as no date or time: {named}"
    )


def _said_in(found: DateCodes, said: str) -> bool:
    """Whether a question's words describe these codes.

    The codes' words (`_codes_said`) stand in it whole: at its end, or
    before the `;` or `.` that follow them in `_date_codes_shape`, so
    "on 30 rows" is not found in "on 300 rows".
    """
    words = _codes_said(found)
    # A slice and `in`, which are operators: no method of the handed-back
    # words is called, for the offline audit's reason (`_joined`).
    return (
        said[len(said) - len(words):] == words
        or f"{words};" in said
        or f"{words}." in said
    )


def date_codes_answered(
    cells: "list[str]",
    settings: taxonomy.Settings,
    said: str,
    missing: bool,
) -> "tuple[DateCodes | None, tuple[str, ...]]":
    """The codes an answered question was about, found again in its column.

    THE CODES THE QUESTION DESCRIBED, AND NO OTHERS (the Codex review of
    lane R1, item 5, and the regression its first repair brought). The
    questions file names the column and never its codes, so the run that
    reads the answer finds them again -- and a word typed after
    `--missing-value` or `--keep-value` decides what it finds. Found
    under the typed declarations, `--missing-value UNK` typed beside an
    answer of `real-value` about `UNK` and `PENDING` kept `PENDING` alone
    and left the thirty `UNK` cells missing without a word; found under
    none, a word typed on BOTH runs, which the question never counted,
    was taken by the answer too: `--missing-value NOTE` beside `UNK`
    answered `real-value` kept NOTE's twenty cells, and an `XX` under
    the line typed missing was put back among the dates, so the column
    read as labels and the answer declared nothing.

    So the codes are found once under the typed declarations, as the
    question is worked out under them, and that reading is taken where
    ``said`` -- the question's own words, handed back in the file --
    describes its codes (`_said_in`): the run that wrote the file was
    typed the same way. Where it does not, they are found once more with
    every typed word a code of this column would match taken out -- a
    spelling on the codes' line of rows that reads as no date or time --
    and that reading is taken where ``said`` describes it, or where the
    first found nothing: the answer then replaces the typed words it
    contradicts, as the newer statement. Where neither is described, the
    table or the options changed since the file was written; the typed
    declarations stand, and the typed words the answer contradicts that
    a code would match are handed back, for the person to be told that
    the answer left them as typed.

    Guarantees: accepts every cell of the column in row order, the
    settings of the run as typed, the question's words (empty where the
    file carries none) and whether the answer was `missing`; returns the
    codes or None, and the typed words left as typed -- each a
    `--keep-value` where ``missing``, a `--missing-value` where not.
    Determinism: a function of the arguments. Raises TypeError if a cell
    is not text. No I/O.
    """
    n_rows = len(cells)
    present, _absent = taxonomy.split_missing(cells, settings)
    typed = date_codes_of(present, settings, n_rows)
    if typed is not None and _said_in(typed, said):
        return typed, ()
    line = max(_DATE_CODES_LINE, parsing.census_floor(settings.small_cell_floor))
    counted = _spellings_counted(cells)
    could: "dict[tuple[str, object], int]" = {}
    for spelling in counted:
        if counted[spelling] >= line and not _a_date_or_a_time(spelling, ""):
            could[_declared_identity(spelling)] = 1
    kept = tuple(
        one for one in settings.kept_values if _declared_identity(one) not in could
    )
    absent = tuple(
        one
        for one in settings.declared_missing_values
        if _declared_identity(one) not in could
    )
    if kept == settings.kept_values and absent == settings.declared_missing_values:
        return typed, ()
    untyped_settings = dataclasses.replace(
        settings, kept_values=kept, declared_missing_values=absent
    )
    present, _absent = taxonomy.split_missing(cells, untyped_settings)
    untyped = date_codes_of(present, untyped_settings, n_rows)
    if untyped is not None and (typed is None or _said_in(untyped, said)):
        return untyped, ()
    contrary = settings.kept_values if missing else settings.declared_missing_values
    left = tuple(one for one in contrary if _declared_identity(one) in could)
    return typed, left


def _date_codes_unread(found: DateCodes) -> int:
    """The present cells that are neither read nor one of the codes."""
    coded = 0
    for _spelling, held in found.codes:
        coded = coded + held
    return max(0, found.n_present - found.n_read - coded)


def _unread_count(found: DateCodes, floor: int) -> str:
    """How many cells read as neither, as the disclosure rule lets it be said.

    The count where it and what it leaves over reach the line
    (`parsing.census_nameable`), and "a few" where not.
    """
    unread = _date_codes_unread(found)
    if parsing.census_nameable([unread], [found.n_present], floor):
        return f"{unread}"
    return "a few"


def _unread_words(found: DateCodes, floor: int) -> str:
    """`_unread_count`, as a part of the column's other values."""
    return f"{_unread_count(found, floor)} of them"


def _read_kind(found: DateCodes) -> str:
    """`date` or `time of day`, as the reading of the column is."""
    return "time of day" if _reads_as_a_clock(found.reading) else "date"


@dataclasses.dataclass(frozen=True)
class Elsewhere:
    """Another column holding a code of a column asked about, as counted.

    `rows` is how many of its cells a declaration naming the codes would
    take, and `n_present` how many cells it holds that are not missing:
    the two the disclosure rule asks before the count is said.
    """

    name: str
    rows: int
    n_present: int


def _elsewhere_words(elsewhere: "tuple[Elsewhere, ...]", floor: int) -> str:
    """Where else a column's codes stand, in words the disclosure rule allows.

    A count is said only where it AND what it leaves over reach the line
    (`parsing.census_nameable`); otherwise the column is named with
    "some rows", which says the answer reaches it without saying how
    few of its rows that is.
    """
    words = ""
    for other in elsewhere:
        rows = (
            f"{other.rows} rows"
            if parsing.census_nameable([other.rows], [other.n_present], floor)
            else "some rows"
        )
        one = f"on {rows} of '{other.name}'"
        words = one if not words else f"{words}, {one}"
    return words


def codes_elsewhere(
    document: "dict[str, object]",
    table_columns: "list[list[str]]",
    asked: "list[tuple[int, DateCodes]]",
    settings: taxonomy.Settings,
    decimal_commas: "tuple[str, ...]" = (),
) -> "dict[int, tuple[Elsewhere, ...]]":
    """Every other column a declaration naming each asked column's codes would reach.

    WHAT AN ANSWER OF `missing` DOES TO THE REST OF THE TABLE (review of
    lane R1, item 1). `--missing-value` reaches every column, and the
    file names no code, so a person answering about a column of dates
    cannot see that `-1` is also a real score of change in another one.
    Measured before this count: a table of 2,000 rows whose DateKey
    column wrote `-1` and `-2` on 4.5 in 100 rows, beside a column of
    scores holding -1 and -2 legitimately, was asked with neither named;
    answered `missing`, the scores lost 552 rows (27.6 in 100) to
    "missing" and their published mean moved from -0.032 to +0.477.

    A PRESENT cell is counted where the declaration would take it, under
    the rule that declaration applies to ITS column
    (`_declared_identity`, the rule `--missing-value` matches by): `-1.0`
    beside a code `-1`, `unk` beside `UNK`, and -- in a column declared
    `--decimal-comma` -- `-1,0`, which that column reads as -1 (second
    review of lane R1, item 1: a column of volumes lost 112 rows to an
    answer whose question said no other column held its codes).

    ONE PASS OVER THE TABLE FOR EVERY QUESTION (second review, item 2):
    each column's spellings are counted once and each different one
    judged once, and every question's count is summed from that, so
    thirty DateKey columns cost one pass and not thirty. Columns
    described as empty are passed over.

    Guarantees: accepts the description, the table's columns, each
    asked column's 0-based place with what was seen in it, the settings
    and the columns declared `--decimal-comma`; returns, for each asked
    place, each other column holding at least one such cell, in the
    table's own column order, with how many and how many cells it holds
    that are not missing. Determinism: a function of the arguments.
    Raises nothing for text. No I/O.
    """
    blocks = document["columns"]
    found: "dict[int, list[Elsewhere]]" = {}
    if not asked or not isinstance(blocks, list):
        return {}
    # Each question's codes as the identities a declaration would match,
    # once as an ordinary column reads them and once as a column
    # declared `--decimal-comma` does -- and each identity with the
    # questions holding it, so a column is matched against the codes it
    # holds and never walked against every question (the Codex review of
    # lane R1, item 9: thirty columns each with a code of its own paid
    # thirty times thirty comparisons for an empty answer).
    holders_of: "dict[bool, dict[tuple[str, object], list[int]]]" = {}
    for comma in (False, True):
        holders: "dict[tuple[str, object], list[int]]" = {}
        for index in range(len(asked)):
            for spelling, _rows in asked[index][1].codes:
                identity = _declared_identity(spelling, comma)
                if identity not in holders:
                    holders[identity] = [index]
                elif holders[identity][len(holders[identity]) - 1] != index:
                    holders[identity] += [index]
        holders_of[comma] = holders
    place_of: "dict[int, int]" = {}
    for index in range(len(asked)):
        place_of[index] = asked[index][0]
    only = place_of[0] if len(asked) == 1 else -1
    place = -1
    for block in blocks:
        place = place + 1
        if place >= len(table_columns) or not isinstance(block, dict):
            continue
        if f"{block['role']}" == taxonomy.ROLE_EMPTY:
            continue
        # A column asked alone is "elsewhere" for no question, and is
        # not counted at all.
        if place == only:
            continue
        name = f"{block['name']}"
        comma = name in decimal_commas
        holders = holders_of[comma]
        counted = _spellings_counted(table_columns[place])
        # Each different spelling judged once; only those a declaration
        # would match are then asked whether they are present at all.
        matched: "list[str]" = []
        identity_of: "dict[str, tuple[str, object]]" = {}
        for spelling in counted:
            identity = _declared_identity(spelling, comma)
            if identity in holders:
                matched += [spelling]
                identity_of[spelling] = identity
        if not matched:
            continue
        present, _absent = taxonomy.split_missing(matched, settings, comma)
        rows_of: "dict[tuple[str, object], int]" = {}
        for spelling in present:
            identity = identity_of[spelling]
            held = rows_of[identity] if identity in rows_of else 0
            rows_of[identity] = held + counted[spelling]
        # The rows each OTHER question's declaration takes here, found
        # from the identities this column holds.
        rows_for: "dict[int, int]" = {}
        for identity in rows_of:
            for index in holders[identity]:
                if place_of[index] == place:
                    continue
                before = rows_for[index] if index in rows_for else 0
                rows_for[index] = before + rows_of[identity]
        if not rows_for:
            continue
        n_present = block["n_present"] if "n_present" in block else None
        if not isinstance(n_present, int):
            every, _gone = taxonomy.split_missing(list(counted), settings, comma)
            n_present = 0
            for spelling in every:
                n_present = n_present + counted[spelling]
        for index in sorted(rows_for):
            position = place_of[index]
            one = Elsewhere(name, rows_for[index], n_present)
            if position in found:
                found[position] += [one]
            else:
                found[position] = [one]
    return {position: tuple(found[position]) for position in found}


def _now_publishes(role: str, floor: int, found: DateCodes) -> str:
    """What a column of dates beside codes publishes while nobody answers."""
    dates = "times of day" if _reads_as_a_clock(found.reading) else "dates"
    if role == taxonomy.ROLE_CLOCK:
        # A CODE IS WRITTEN BACK (landing 3b.5, plan P4-D373): each such
        # spelling at least the floor's rows wrote is published with its
        # count, and the twin writes it as the table does.
        return (
            f"what it publishes now: points along its range and the tails "
            f"beyond them, with the rows holding those spellings counted as "
            f"values that are not {dates}; each spelling at least {floor} "
            f"rows share is written back in the twin as your table writes "
            f"it, and the rarer ones as made-up text"
        )
    if role == taxonomy.ROLE_DATETIME:
        return (
            f"what it publishes now: points along its range and the tails "
            f"beyond them, with the rows holding those spellings counted as "
            f"values that are not {dates}, which the twin writes as made-up "
            f"text"
        )
    if role in _MEASURED_ROLES:
        return (
            f"what it publishes now: an average, a spread and points along "
            f"its range, worked out over these values as plain numbers with "
            f"those spellings among them, so many of the twin's cells will "
            f"not read as {dates}"
        )
    return (
        f"{_publishes_under(ANSWER_KEEP, role, floor)}, so many of the "
        f"twin's cells will not read as {dates}"
    )


def _date_code_choices(
    role: str,
    floor: int,
    found: DateCodes,
    elsewhere: "tuple[Elsewhere, ...]" = (),
) -> "list[Choice]":
    """The three answers a column of dates beside a few codes may take.

    `keep` first, because Enter gives it: nobody said what the codes
    mean, so the column keeps the reading it has. `missing` is the one
    that repairs it, and says that `--missing-value` reaches every
    column of the table, which is how that option works -- naming each
    other column that holds the same spellings, and how many of its
    rows, or that none does (`codes_elsewhere`); `real-value` keeps the
    reading and records the answer, so the question is not put again,
    and says the same of the other columns.
    """
    reading = date_codes_reading(found)
    now = _now_publishes(role, floor, found)
    unread_too = ""
    if _date_codes_unread(found):
        many = _unread_count(found, floor)
        many = "few" if many == "a few" else many
        unread_too = f", the {many} cells that read as neither counted unread"
    if elsewhere:
        where = _elsewhere_words(elsewhere, floor)
        missing_too = (
            f": the same spellings stand {where}, which this answer reads "
            f"as missing there too"
        )
        kept_too = (
            f": the same spellings stand {where}, which this answer keeps "
            f"as values there too"
        )
    else:
        missing_too = ", and no other column of your table holds them"
        kept_too = missing_too
    return [
        Choice(
            ANSWER_KEEP,
            "leave it as it is -- synthtwin reads this column the way it "
            "does now",
            now,
        ),
        Choice(
            ANSWER_NO_DATE,
            "those spellings stand for a date or time nobody wrote down -- "
            "unknown, not recorded or not applicable",
            (
                f"the column read as {reading}: points along its range and "
                f"the tails beyond them, but neither end unless at least "
                f"{floor} rows share it, with the rows holding those "
                f"spellings counted as missing{unread_too} and each spelling "
                f"at least {floor} rows share written back in the twin as "
                f"your table writes it. This is --missing-value naming each "
                f"of those spellings, and it reaches every column of your "
                f"table{missing_too}"
            ),
        ),
        Choice(
            ANSWER_REAL_VALUE,
            "those spellings are values of their own, not a missing date "
            "or time",
            (
                f"{now}; and this question is not asked again. This is "
                f"--keep-value naming each of those spellings, which "
                f"reaches every column of your table{kept_too}"
            ),
        ),
    ]


def _a_spelling_can_reach_the_line(
    block: "dict[str, object]",
    present: "list[str]",
    settings: taxonomy.Settings,
) -> bool:
    """Whether some spelling of a column could stand on the codes' line of rows.

    A COLUMN OF A MILLION DIFFERENT VALUES IS NOT COUNTED TO LEARN THAT
    NONE OF THEM REPEATS. The commonest spelling of `n` present cells
    over `d` different ones stands on at most `n - d + 1` rows, and the
    column's block publishes both -- so where that is under the line no
    code can be there, and the column of free text, record numbers or
    all-different moments is passed over without a dictionary of its
    cells. The bound is used only where the block counted the same cells
    this run split, and the column is counted otherwise.

    Guarantees: accepts the column's block, its present cells and the
    settings; returns False only where no spelling can reach the line.
    Determinism: a function of the three. Raises nothing. No I/O.
    """
    held = block["n_present"] if "n_present" in block else None
    different = block["n_distinct"] if "n_distinct" in block else None
    if not isinstance(held, int) or not isinstance(different, int):
        return True
    if held != len(present) or different < 1:
        return True
    line = max(_DATE_CODES_LINE, parsing.census_floor(settings.small_cell_floor))
    return held - different + 1 >= line


@dataclasses.dataclass(frozen=True)
class DateCodesSeen:
    """What one pass over a table's columns found about dates beside codes.

    `questions` are the codes questions to put. `answered` are the
    columns whose codes stand only because the person declared them
    kept -- an answer of `real-value`, or `--keep-value` typed -- each
    as the question it would have been: such a column is asked no
    question of what kind its values are, and gets no checklist line
    calling it codes, as while the question stood (review of lane R1,
    item 2) -- but a column the answer leaves read as a measurement keeps
    its checklist line, owner decision D14's (second review, item 3).
    `day_or_month` are the columns asked about whose other
    cells read both ways under a slashed pair (item 4), for the file's
    day-or-month question.
    """

    questions: "tuple[Question, ...]" = ()
    answered: "tuple[Question, ...]" = ()
    day_or_month: "tuple[DayOrMonth, ...]" = ()


def date_code_questions(
    document: "dict[str, object]",
    table_columns: "list[list[str]]",
    settings: taxonomy.Settings,
    already: "list[str]",
    split: "SplitColumns | None" = None,
    decimal_commas: "tuple[str, ...]" = (),
    stored_as: "tuple[str, ...]" = (),
) -> "list[Question]":
    """The codes questions `date_codes_seen` finds, as a list."""
    return list(
        date_codes_seen(
            document,
            table_columns,
            settings,
            already,
            split,
            decimal_commas,
            stored_as,
        ).questions
    )


def _as_the_classifier_reads(
    name: str,
    values: "list[str]",
    settings: taxonomy.Settings,
    found: DateCodes,
    decimal_comma: bool,
    stored_as: str,
) -> "DateCodes | None":
    """What was seen, as the classifier reads the column once its codes are missing.

    The question promises a reading -- "read as dates written as ..." --
    and the classifier is asked for it (`taxonomy.role_read`), with each
    code declared missing and any word declared kept that one of them
    would match taken out, which is what the answer `missing` does: the
    question is put only where that run reads the column as dates or
    times, and says the member or clock form that run reads it under
    and the cells that run leaves unread (the Codex review of lane R1,
    item 3, and of landing T1, item 5). None where the answer would give
    any other role.

    THE CELLS LEFT UNREAD ARE THAT RUN'S OWN COUNT OF THEM (the
    verification of the repairs of the Codex review of lane R1, its
    open item 1). The cells that run reads are counted among the cells
    it still holds, and a cell it sets aside as a stand-in date --
    `1900-01-01` beside real days -- is held no more, though the reading
    parses it. Taken as the cells read, that count said of 950 ISO
    dates, thirty `1900-01-01` and twenty `UNK` that 950 of the 1000
    read as dates and that 30 cells besides the code read as neither
    and would "stay unread whatever the answer" -- while the answer
    `missing` left none unread and counted the thirty missing, by their
    spelling. So the cells left unread are those that run holds and does
    not read, and every other present cell that is no code is one the
    reading reads: 980 of the 1000, and every other value is the code,
    as 110cb46 said.
    """
    named: "list[str]" = []
    identities: "list[tuple[str, object]]" = []
    for spelling, _rows in found.codes:
        named += [spelling]
        identities += [_declared_identity(spelling)]
    kept = [
        one
        for one in settings.kept_values
        if _declared_identity(one) not in identities
    ]
    answered = dataclasses.replace(
        settings,
        kept_values=tuple(kept),
        declared_missing_values=settings.declared_missing_values
        + tuple(named),
    )
    try:
        role, reading, n_read, held = taxonomy.role_read(
            name, values, answered, decimal_comma, stored_as
        )
    except ValueError:
        return None
    if role != taxonomy.ROLE_DATETIME and role != taxonomy.ROLE_CLOCK:
        return None
    if not reading:
        return None
    coded = 0
    for _spelling, rows in found.codes:
        coded = coded + rows
    unread = held - n_read
    return DateCodes(
        reading, found.codes, found.n_present - coded - unread, found.n_present
    )


def date_codes_seen(
    document: "dict[str, object]",
    table_columns: "list[list[str]]",
    settings: taxonomy.Settings,
    already: "list[str]",
    split: "SplitColumns | None" = None,
    decimal_commas: "tuple[str, ...]" = (),
    stored_as: "tuple[str, ...]" = (),
) -> DateCodesSeen:
    """Every column of dates or times that writes a few repeated codes.

    Asked of every column nobody declared, whatever it was read as --
    labels, free text, numbers, or dates and times with cells left
    unread -- because the codes are what moved it there; a column of
    dates or times every cell of which its reading parses has no code to
    ask about and is passed over without its cells being read. Each
    column's present cells are taken from ``split`` where
    `questions_and_splits_for` split that very column under these
    settings, and each is counted once.

    A COLUMN ASKED ABOUT HERE IS ASKED NOTHING ELSE: `00/00/0000` beside
    `03/17/2023` is two numbers joined by a mark on every row, and the
    joined question that shape raises would offer a blood pressure
    reading of a column of dates. The caller takes these columns out of
    the others (`without_columns_of`) -- and the `answered` ones too,
    whose codes the person declared kept: the joined question is no
    more the column's after that answer than before it.

    Each question names the other columns its answer would reach
    (`codes_elsewhere`, one pass over the table for every question,
    reading each column declared in ``decimal_commas`` as the
    declaration does), and a column whose dates read either way once
    its codes are out is put in the day-or-month question as well, so
    one file asks both and one answering run reads the column right.

    Guarantees: a fixed function of the arguments, in the table's own
    column order; opens nothing; prints nothing; and no cell of any
    column appears in what it returns.
    """
    blocks = document["columns"]
    if not isinstance(blocks, list):
        return DateCodesSeen()
    found: "list[Question]" = []
    answered: "list[Question]" = []
    order: "list[DayOrMonth]" = []
    pending: "list[tuple[str, str, int, DateCodes]]" = []
    position = 0
    for block in blocks:
        position = position + 1
        if not isinstance(block, dict) or position > len(table_columns):
            continue
        name = f"{block['name']}"
        role = f"{block['role']}"
        if name in already or role == taxonomy.ROLE_EMPTY:
            continue
        if role == taxonomy.ROLE_DATETIME or role == taxonomy.ROLE_CLOCK:
            unread = block["n_unparsed"] if "n_unparsed" in block else 0
            if not isinstance(unread, int) or unread < 1:
                continue
        if (
            split is not None
            and position - 1 in split.present
            and split.cells[position - 1] is table_columns[position - 1]
            and split.settings == settings
        ):
            present = split.present[position - 1]
        else:
            present, _absent = taxonomy.split_missing(
                table_columns[position - 1], settings
            )
        if not _a_spelling_can_reach_the_line(block, present, settings):
            continue
        counted = _spellings_counted(present)
        n_rows = len(table_columns[position - 1])
        comma = name in decimal_commas
        storage = (
            stored_as[position - 1] if position - 1 < len(stored_as) else ""
        )
        seen = _codes_and_rest(counted, len(present), settings, n_rows, False)
        if seen is None:
            if not settings.kept_values:
                continue
            # WHAT WAS DECLARED KEPT, COUNTED AS IT STANDS: where the
            # codes are back once nothing is kept, the person kept them,
            # and the column is one asked about and answered -- where the
            # question would have been put, which the classifier says.
            stood = _codes_and_rest(counted, len(present), settings, n_rows, True)
            if stood is not None and _as_the_classifier_reads(
                name,
                table_columns[position - 1],
                settings,
                stood[0],
                comma,
                storage,
            ) is not None:
                answered += [
                    Question(
                        name, role, BECAUSE_DATE_CODES, "", [], ANSWER_REAL_VALUE
                    )
                ]
            continue
        rest = seen[1]
        confirmed = _as_the_classifier_reads(
            name, table_columns[position - 1], settings, seen[0], comma, storage
        )
        if confirmed is None:
            continue
        codes = confirmed
        pending += [(name, role, position - 1, codes)]
        if codes.reading in _MONTH_FIRST_MEMBERS:
            either = day_or_month_seen(list(rest), codes.reading)
            if either is not None:
                order += [DayOrMonth(name, either.months, either.days)]
    # Where else each column's codes stand, for every question at once.
    elsewhere_of = codes_elsewhere(
        document,
        table_columns,
        [(place, codes) for _name, _role, place, codes in pending],
        settings,
        decimal_commas,
    )
    for name, role, place, codes in pending:
        elsewhere = elsewhere_of[place] if place in elsewhere_of else ()
        found += [
            Question(
                name,
                role,
                BECAUSE_DATE_CODES,
                _date_codes_shape(codes, settings.small_cell_floor, elsewhere),
                _date_code_choices(
                    role, settings.small_cell_floor, codes, elsewhere
                ),
                ANSWER_KEEP,
            )
        ]
    return DateCodesSeen(tuple(found), tuple(answered), tuple(order))


# THE QUESTIONS A COLUMN OF DATES BESIDE CODES IS NOT ASKED (plan
# P4-D381): the ones about what KIND of value its cells hold -- numbers
# joined by a mark, a code register written in figures, a point between
# thousands -- which the codes question answers in their place. A
# question of another kind about the same column, such as which clock
# its hours are written on, still stands beside it.
_ANSWERED_BY_THE_CODES_QUESTION = (
    BECAUSE_JOINED,
    BECAUSE_PADDED,
    BECAUSE_FIXED_WIDTH,
    BECAUSE_GROUPED_FIXED_WIDTH,
    BECAUSE_POINT_THOUSANDS,
)


def without_columns_of(
    questions: "list[Question]", asked: "list[Question]"
) -> "list[Question]":
    """``questions`` less those about what kind of values a column ``asked`` names holds.

    Guarantees: accepts two lists of questions; returns the first's in
    its own order, less each one whose column the second names and
    whose reason is one the codes question answers in its place
    (`_ANSWERED_BY_THE_CODES_QUESTION`). Determinism: a function of the
    two. Raises nothing. No I/O.
    """
    named: "list[str]" = []
    for question in asked:
        named += [question.name]
    return [
        question
        for question in questions
        if question.name not in named
        or question.reason not in _ANSWERED_BY_THE_CODES_QUESTION
    ]


# The one question the checklist puts, in the words every surface uses.
CHECKLIST_QUESTION = (
    "Which of these columns hold codes or record numbers rather than "
    "measurements?"
)
# The same question as a screen heading. Written out rather than
# upper-cased at the call site: the offline audit reads a single
# named attribute of a module and no deeper, so `CHECKLIST_QUESTION
# .upper()` is two steps past `asking` and is refused (plan D6.2).
CHECKLIST_HEADING = (
    "WHICH OF THESE COLUMNS HOLD CODES OR RECORD NUMBERS RATHER "
    "THAN MEASUREMENTS?"
)
# What the file is, said on its own face. It is real-derived material
# like the other five files a full run leaves behind: it names columns,
# it counts cells, and it says what each column's shape is. It carries
# no value of the table, and that is a narrower promise than being
# anonymous (amendment A-P4-58).
FILE_CARRIES = (
    "This file was written from your real table. It names your columns, "
    "counts their cells and describes the shape of what they hold. It "
    "carries no value of your table. Keep it under the same rules your "
    "institution applies to the table itself."
)
HOW_TO_ANSWER = (
    "Write one of the answers offered beside 'your_answer' for any "
    "column you want to correct, save the file, and run synthtwin "
    "profile again on the same table naming this file after --answers. "
    "Columns you leave blank keep the reading named in 'read_as_now'."
)


def _question_entry(question: Question) -> "dict[str, object]":
    """One question as the plain data both the file and a screen show."""
    offered: list[dict[str, str]] = []
    for choice in question.choices:
        offered += [
            {
                "answer": choice.answer,
                "means": choice.means,
                "then_the_description_publishes": choice.publishes,
            }
        ]
    return {
        "column": question.name,
        "what_synthtwin_saw": question.shape,
        "read_as_now": question.taken,
        "answers_you_can_give": offered,
        "your_answer": "",
    }


def questions_document(
    table_name: str,
    asked: "list[Question]",
    listed: "list[Question]",
    about_file: "list[Question] | None" = None,
    about_table: "list[str] | None" = None,
) -> "dict[str, object]":
    """The questions file's whole content, as plain data.

    TWO SECTIONS, AND THE ORDER IS THE POINT (amendment A-P4-58; owner
    ruling 2026-09-10). `asked` holds the columns synthtwin could read
    more than one way and did not guess about -- a real question, one
    per column, each with what was seen and what each answer would
    publish. `checklist` holds every column read as a number that
    raised no question at all, under ONE question, because nothing in
    their values can single them out: a register of concept
    identifiers, a set of month codes and a column of ages are written
    identically, and the rule that tried to tell them apart was deleted
    for guessing.

    The asked section comes first because it is the shorter one and the
    one with a real question in it. The checklist is longer and is read
    the way a person reads a list of their own columns.

    Guarantees:

    - Inputs: the table's name and the two lists of questions.
    - Determinism: a fixed function of the arguments, in the table's
      own column order.
    - Errors raised: none.
    - Boundary: **no value of the table appears anywhere in the
      result.** Every question carries a shape, which is a count, a
      width or a separator, and never a cell.
    """
    file_entries: list[dict[str, object]] = []
    for question in about_file if about_file else []:
        file_entries += [_question_entry(question)]
    asked_entries: list[dict[str, object]] = []
    for question in asked:
        asked_entries += [_question_entry(question)]
    listed_entries: list[dict[str, object]] = []
    for question in listed:
        listed_entries += [_question_entry(question)]
    said: list[str] = []
    for sentence in about_table if about_table else []:
        said += [f"{sentence}"]
    return {
        "what_this_is": (
            "synthtwin could not settle these columns from their values "
            "alone, so it is asking you rather than guessing."
        ),
        # WHAT THIS RUN SAID ABOUT THE TABLE AS A WHOLE, not about any
        # column (plan P4-D341). Empty on almost every table: it holds
        # the population notice, which the description carries as a
        # note of its own and every page of the run repeats. It is
        # HERE as well because this file travels on its own -- a person
        # hands it to a colleague or opens it on another machine -- and
        # a page that names the columns of a small table without saying
        # it is a small table says less than the other four do.
        "about_your_table": said,
        "what_this_file_carries": FILE_CARRIES,
        "how_to_answer": HOW_TO_ANSWER,
        "table": table_name,
        # QUESTIONS ABOUT THE FILE ITSELF, not about one column (plan
        # P4-D81). Empty for almost every table: it is filled only
        # where synthtwin saw a shape it must not act on unasked.
        "about_your_file": file_entries,
        "asked": asked_entries,
        "checklist": {
            "question": CHECKLIST_QUESTION,
            "why": (
                "Nothing in these columns' values can tell a coding "
                "system from a measurement -- a code register and a "
                "column of counts are written identically -- so they "
                "raised no question of their own. Only you know which "
                "is which."
            ),
            "columns": listed_entries,
        },
    }


@dataclasses.dataclass(frozen=True)
class Answers:
    """What a person wrote in a questions file, as three lists of names.

    THE SAME THREE LISTS THE INTERVIEW PRODUCES (amendment A-P4-58).
    Answering on the screen and answering in the file are the same act,
    so they end in the same shape and the command cannot tell them
    apart afterwards -- which is what stops the two paths drifting into
    two behaviours.
    """

    codes: "tuple[str, ...]"
    identifiers: "tuple[str, ...]"
    measurements: "tuple[str, ...]"
    # ...and the fourth list (landing 2b.2): the columns answered as
    # writing a point between thousands, which is `--decimal-comma`.
    decimal_commas: "tuple[str, ...]" = ()
    # ...and the fifth answer, which is not a list of columns at all
    # (plan P4-D81): how many rows under the column names the person
    # said describe those columns. Nought where they did not answer,
    # which leaves those rows in the table.
    metadata_rows: int = 0
    # ...and the sixth (plan P4-D110): the delimiter the person said
    # their file is written with, as the character, or empty.
    delimiter: str = ""
    # WHETHER THE FIFTH WAS ANSWERED AT ALL (plan P4-D172). `data` is an
    # answer of nought rows, and nought is also what an unanswered file
    # carries -- so the command line could not tell "leave these rows in
    # my table" from silence, dropped the answer, and let a typed
    # `--metadata-rows 2` take a person's record out of the table and
    # publish it. This says which it was.
    metadata_rows_answered: bool = False
    # ...and the seventh (the owner's ruling of 2026-09-17, item 8;
    # plan P4-D232): which row the person says their column names are
    # in, as the word they answered, or empty where they did not
    # answer. `names` is `--first-row names`; `first-record` is the
    # reading that already stands and changes nothing, and it is
    # carried all the same, because an answer that is dropped is an
    # answer a person was told had been heard.
    first_row: str = ""
    # ...and the columns answered `twelve-hour` (landing T1), which is
    # `--twelve-hour`.
    twelve_hours: "tuple[str, ...]" = ()
    # ...and the eighth (plan P4-D381): whether the person said the day
    # comes first in their file's dates, which is `--day-first`. False
    # where they said the month does, which is the reading that stands,
    # and where they said nothing.
    day_first: bool = False
    # WHETHER THEY SAID THE MONTH DOES. It declares nothing -- month
    # first is the reading that stands, and no option records it -- but
    # it is an answer, and the questions file the same run writes again
    # may not put the question back to a person who has just answered
    # it.
    month_first: bool = False
    # ...and the ninth (plan P4-D381): the columns whose few repeated
    # codes the person said stand for a missing date or time, and those
    # whose codes they said are values of their own. NAMES, not codes:
    # the questions file carries no value of the table, so the run that
    # reads the answer finds each column's codes again in the table it
    # opens and declares those (`date_codes_of`).
    missing_date_columns: "tuple[str, ...]" = ()
    real_value_columns: "tuple[str, ...]" = ()
    # ...and what each of those questions said it saw, as the file holds
    # it, column by column: the words that tell the run reading the
    # answer which codes it was about (`date_codes_answered`). Empty
    # words where an edited file carries none.
    date_code_shapes: "tuple[tuple[str, str], ...]" = ()


def _entry_answer(
    entry: object, place: str
) -> "tuple[str, str, tuple[str, ...]] | None":
    """One entry read back: its column, the answer given, what was offered.

    None where the entry carries no answer at all, which is what a
    blank `your_answer` means and is the commonest case by far: a
    person answers two columns of forty and leaves the rest alone.

    Raises ValueError, with a message written for a person, where the
    entry is not shaped like one this module wrote.
    """
    if not isinstance(entry, dict):
        raise ValueError(errors.answers_entry_is_not_a_question(place))
    # READ BY INDEX AND NEVER BY `.get`, which is the offline policy
    # and not a style (plan D6.2): a method call on a value this
    # module did not build is a call the audit cannot trace, and this
    # value came out of a file somebody edited. Membership is asked
    # with `in`, which is an operator, and the key is then indexed.
    if "column" not in entry:
        raise ValueError(errors.answers_entry_names_no_column(place))
    name = entry["column"]
    if not isinstance(name, str) or not name:
        raise ValueError(errors.answers_entry_names_no_column(place))
    given: object = ""
    if "your_answer" in entry:
        given = entry["your_answer"]
    if not isinstance(given, str):
        raise ValueError(errors.answers_entry_is_not_a_question(place))
    written = parsing.trimmed(given)
    if not written:
        return None
    # A MALFORMED CHOICE LIST MAY NOT TURN THE CHECK OFF (review item
    # L17b-R1-5). This gathered what it could and handed back whatever
    # it found, and the caller checked membership only when the tuple
    # was non-empty -- so an entry whose `answers_you_can_give` was a
    # mapping, or an empty list, or a list of the wrong shape, accepted
    # ANY word as an answer. A question that offers nothing cannot be
    # answered, and the person is told that rather than obeyed.
    offered: list[str] = []
    if "answers_you_can_give" not in entry:
        raise ValueError(errors.answers_entry_offers_nothing(place, name))
    choices = entry["answers_you_can_give"]
    if not isinstance(choices, list):
        raise ValueError(errors.answers_entry_offers_nothing(place, name))
    for choice in choices:
        if not isinstance(choice, dict) or "answer" not in choice:
            raise ValueError(
                errors.answers_entry_offers_nothing(place, name)
            )
        one = choice["answer"]
        if not isinstance(one, str) or not one:
            raise ValueError(
                errors.answers_entry_offers_nothing(place, name)
            )
        offered += [one]
    if not offered:
        raise ValueError(errors.answers_entry_offers_nothing(place, name))
    return name, written, tuple(offered)


def _entries_of(document: object, shown: str) -> "list[tuple[object, str]]":
    """Every entry of a questions file, each with the place to name it by.

    Both sections, in the order the file writes them, because a person
    may answer in either: the checklist is where a code register that
    raised no question of its own is corrected, and it is the longer
    of the two.
    """
    if not isinstance(document, dict):
        raise ValueError(errors.answers_file_is_not_one(shown))
    if "asked" not in document or "checklist" not in document:
        raise ValueError(errors.answers_file_is_not_one(shown))
    asked = document["asked"]
    checklist = document["checklist"]
    if not isinstance(asked, list) or not isinstance(checklist, dict):
        raise ValueError(errors.answers_file_is_not_one(shown))
    if "columns" not in checklist:
        raise ValueError(errors.answers_file_is_not_one(shown))
    listed = checklist["columns"]
    if not isinstance(listed, list):
        raise ValueError(errors.answers_file_is_not_one(shown))
    found: list[tuple[object, str]] = []
    # THE FILE'S OWN SECTION FIRST, and tolerated absent: a questions
    # file written before plan P4-D81 carries no such section, and
    # refusing a person's older file for a question it could not have
    # been asked would be this tool telling them their answers were
    # wrong when they were only early.
    if "about_your_file" in document:
        about = document["about_your_file"]
        if not isinstance(about, list):
            raise ValueError(errors.answers_file_is_not_one(shown))
        place = 0
        for entry in about:
            place += 1
            found += [(entry, f"about_your_file[{place}]")]
    place = 0
    for entry in asked:
        place += 1
        found += [(entry, f"asked[{place}]")]
    place = 0
    for entry in listed:
        place += 1
        found += [(entry, f"checklist[{place}]")]
    return found


def answers_in(document: object, shown: str) -> Answers:
    """Read a questions file back as the declarations it stands for.

    Guarantees:

    - Inputs: the parsed content of a questions file, and the path to
      name in a refusal.
    - Determinism: a fixed function of the two. The names come back in
      the file's own order, which is the table's.
    - Errors raised: ValueError, carrying one plain-language message,
      where the file is not a questions file, where an entry is not
      shaped like a question, or where an answer is not one of the
      answers that entry offered.
    - Boundary: opens nothing, prints nothing, and reads no table. It
      turns text into three lists of column names and does not check
      that any of them is a column: naming a column that is not in the
      table is refused later, by the same check that covers `--code`
      typed on the command line, so a person meets one message for
      that mistake and not two.

    AN ANSWER THAT IS NOT OFFERED IS REFUSED, never ignored. A person
    who writes `codes` where the file offers `code`, or who answers a
    column in a language of their own, has said something; taking the
    file, dropping that word and describing their table the old way
    would tell them their answer had been heard when it had not.

    `keep` and `measurement` on a column already read as a measurement
    add no declaration, because there is nothing to change. Every other
    answer becomes the declaration that makes it true.
    """
    codes: list[str] = []
    identifiers: list[str] = []
    measurements: list[str] = []
    decimal_commas: list[str] = []
    metadata_rows = 0
    metadata_rows_answered = False
    delimiter = ""
    first_row = ""
    twelve_hours: list[str] = []
    day_first = False
    month_first = False
    missing_dates: "list[str]" = []
    real_values: "list[str]" = []
    code_shapes: "list[tuple[str, str]]" = []
    for entry, place in _entries_of(document, shown):
        read = _entry_answer(entry, place)
        if read is None:
            continue
        name, written, offered = read
        # UNCONDITIONALLY (review item L17b-R1-5). `_entry_answer`
        # refuses an entry that offers nothing, so `offered` is a
        # non-empty tuple by the time it arrives here and this check
        # can no longer be skipped by editing the choices away.
        if written not in offered:
            raise ValueError(
                errors.answers_answer_is_not_offered(
                    shown, name, written, list(offered)
                )
            )
        if written == ANSWER_CODE:
            codes += [name]
        elif written == ANSWER_IDENTIFIER:
            identifiers += [name]
        elif written == ANSWER_MEASUREMENT or written == ANSWER_JOINED:
            measurements += [name]
        elif written == ANSWER_DECIMAL_COMMA:
            decimal_commas += [name]
        elif written == ANSWER_METADATA_ROWS:
            # The one answer that names no column (plan P4-D81).
            metadata_rows = METADATA_ROWS_DECLARED
            metadata_rows_answered = True
        elif written == ANSWER_DATA:
            # The reading that already stands: the rows are records. It
            # is an ANSWER all the same, and it overrides a typed
            # declaration (plan P4-D172).
            metadata_rows = 0
            metadata_rows_answered = True
        elif written == ANSWER_TWELVE_HOUR:
            twelve_hours += [name]
        elif written == ANSWER_FIRST_ROW_NAMES:
            first_row = ANSWER_FIRST_ROW_NAMES
        elif written == ANSWER_FIRST_ROW_DATA:
            first_row = ANSWER_FIRST_ROW_DATA
        elif written == ANSWER_DAY_FIRST:
            # The one answer about the dates of the whole file (plan
            # P4-D381), which is `--day-first`.
            day_first = True
        elif written == ANSWER_MONTH_FIRST:
            # The reading that already stands; nothing to declare, and
            # the answer is carried so that it is not asked again.
            month_first = True
        elif written == ANSWER_NO_DATE or written == ANSWER_REAL_VALUE:
            if written == ANSWER_NO_DATE:
                missing_dates += [name]
            else:
                real_values += [name]
            # Read by index, for the offline policy above.
            saw = (
                entry["what_synthtwin_saw"]
                if isinstance(entry, dict) and "what_synthtwin_saw" in entry
                else ""
            )
            code_shapes += [(name, saw if isinstance(saw, str) else "")]
        elif written in ANSWER_DELIMITERS:
            # The one answer that decides how the file is SPLIT (plan
            # P4-D110), which is `--delimiter`.
            delimiter = ANSWER_DELIMITERS[written]
        elif written != ANSWER_KEEP:
            # Offered by the file but not a word this module acts on,
            # which a questions file synthtwin wrote cannot contain and
            # an edited one can.
            raise ValueError(
                errors.answers_answer_is_not_offered(
                    shown, name, written, list(offered)
                )
            )
    # ONE COLUMN'S CODES ANSWERED BOTH WAYS IS REFUSED (the Codex review
    # of lane R1, item 8). An edited file can hold two entries for one
    # column; both answers were kept, and the run read the column under
    # `missing` alone without a word about the other.
    kept_columns = {name: 1 for name in real_values}
    for name in missing_dates:
        if name in kept_columns:
            raise ValueError(errors.one_column_answered_both_ways(shown, name))
    return Answers(
        tuple(codes),
        tuple(identifiers),
        tuple(measurements),
        tuple(decimal_commas),
        metadata_rows,
        delimiter,
        metadata_rows_answered,
        first_row,
        tuple(twelve_hours),
        day_first=day_first,
        month_first=month_first,
        missing_date_columns=tuple(missing_dates),
        real_value_columns=tuple(real_values),
        date_code_shapes=tuple(code_shapes),
    )
