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
# pressure column looks like when nobody has said what it is.
JOINED_ROLES = (
    taxonomy.ROLE_TEXT,
    taxonomy.ROLE_LONG_TAIL,
    taxonomy.ROLE_CATEGORICAL,
)

# The two readings a person is offered, and the third that already had
# an option. The words are the ones the help screen uses.
ANSWER_MEASUREMENT = "measurement"
ANSWER_CODE = "code"
ANSWER_IDENTIFIER = "identifier"
ANSWER_JOINED = "joined"

# Why a column was worth asking about. Each is shown to the person, so
# each says what was SEEN and not what it was taken to mean.
BECAUSE_PADDED = "padded"
BECAUSE_FIXED_WIDTH = "fixed-width"
BECAUSE_JOINED = "two-numbers"

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
      answer, and not true above the default floor.

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
            "an average, a spread, a smallest and a largest, and points "
            "between"
        )
    if answer == ANSWER_JOINED:
        return (
            "each number inside the cell described on its own, with its "
            "own average and ends"
        )
    if answer == ANSWER_CODE:
        if floor > 1:
            return (
                f"every value that at least {floor} rows share, exactly "
                f"as written and with the number of rows that carried "
                f"it; rarer ones counted together and never named, "
                f"because you asked for groups of {floor}"
            )
        return (
            "every value exactly as written, with the number of rows "
            "that carried it, and no average at all"
        )
    # ANSWER_KEEP: whatever the column already is.
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


def _joined_choices(role: str, floor: int) -> "list[Choice]":
    """The answers a column of two-numbers-in-one-cell may take.

    THE FIRST ONE IS WHAT ENTER GIVES YOU, and it is not `joined`
    (review round 1, item 3). Such a column is read as text or as
    labels today; declaring it joined is an affirmative answer that
    CHANGES the reading. Listing the change as the default told a
    person that doing nothing would describe their blood pressures,
    when doing nothing leaves them undescribed.
    """
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
        if name in already:
            position = position + 1
            continue
        if position >= len(table_columns):
            position = position + 1
            continue
        present, _absent = taxonomy.split_missing(
            table_columns[position], settings
        )
        if role not in NUMERIC_ROLES and role not in JOINED_ROLES:
            position = position + 1
            continue
        reason: "str | None"
        if role in JOINED_ROLES:
            reason = why_joined_is_worth_asking(present)
        else:
            reason = why_worth_asking(present)
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
                    _shape_of(reason, present, settings.small_cell_floor),
                    choices,
                    taken,
                )
            ]
        position = position + 1
    return asked


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


def _sayable(count: int, floor: int) -> str:
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
    """
    if count >= floor:
        return f"{count} of them"
    return "some of them"


def _shape_of(reason: str, present: "list[str]", floor: int = 1) -> str:
    """What synthtwin SAW, in words carrying no value of the table.

    THE DISCLOSURE RULE OF THE QUESTIONS FILE, made into a sentence
    (amendment A-P4-58; owner ruling 2026-09-10). The file may name the
    column, the choices, and any spelling the description itself would
    publish -- a separator is one, because the joined role publishes it
    -- and no value of the table. A count of how many cells carry a
    leading zero is a count and not a value; a width is a width.

    Guarantees: accepts a reason and the present cells; returns one
    sentence. Determinism: a fixed function of both. Raises nothing.
    No I/O. **No cell of the column appears in what it returns.**
    """
    if reason == BECAUSE_PADDED:
        padded = 0
        for value in present:
            if len(value) > 1 and value[0] == "0":
                padded = padded + 1
        return (
            f"every value is written in figures alone, and "
            f"{_sayable(padded, floor)} carry a leading zero"
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
    if reason == BECAUSE_JOINED:
        mark = _joining_mark(present)
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
      declared, and the questions already asked so no column appears
      twice.
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
        spoken = spoken + [question.name]
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
            listed = listed + [
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
        elif role in _LABELLED_ROLES and _looks_like_a_code(present):
            listed = listed + [
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
    asked_entries: list[dict[str, object]] = []
    for question in asked:
        asked_entries += [_question_entry(question)]
    listed_entries: list[dict[str, object]] = []
    for question in listed:
        listed_entries += [_question_entry(question)]
    return {
        "what_this_is": (
            "synthtwin could not settle these columns from their values "
            "alone, so it is asking you rather than guessing."
        ),
        "what_this_file_carries": FILE_CARRIES,
        "how_to_answer": HOW_TO_ANSWER,
        "table": table_name,
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
    offered: list[str] = []
    if "answers_you_can_give" in entry:
        choices = entry["answers_you_can_give"]
        if isinstance(choices, list):
            for choice in choices:
                if not isinstance(choice, dict) or "answer" not in choice:
                    continue
                one = choice["answer"]
                if isinstance(one, str) and one:
                    offered += [one]
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
    for entry, place in _entries_of(document, shown):
        read = _entry_answer(entry, place)
        if read is None:
            continue
        name, written, offered = read
        if offered and written not in offered:
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
        elif written != ANSWER_KEEP:
            raise ValueError(
                errors.answers_answer_is_not_offered(
                    shown, name, written, list(offered)
                )
            )
    return Answers(tuple(codes), tuple(identifiers), tuple(measurements))
