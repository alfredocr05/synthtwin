"""The plain-language summary of a profile (plan P1-D5, P1-D6).

The same text is printed to the screen and written beside the profile.
It is written for a researcher who has never programmed: no jargon that
is not explained in the sentence that uses it, no statistical notation,
and every number said in words a person can act on.

It has one job beyond being readable. The profile is computed FROM real
data, so it is real-derived material, and the person running the tool
has to be able to see -- before they move the file anywhere -- exactly
which of their real values it carries and which it does not. That is
what the disclosure section is for, and it is printed every run,
whether or not anything was withheld.

The summary is built from the profile document, never from the table.
That is deliberate: the machine-readable record and the words a person
reads are then two views of the same thing and cannot disagree.

Imports here stay within the allowlist (plan D6.2): this module imports
only from this package.
"""

from synthtwin import parsing, taxonomy

_ROLE_WORDS = {
    taxonomy.ROLE_EMPTY: "no values at all",
    taxonomy.ROLE_CONSTANT: "one repeated value",
    # This role is never inferred: it appears only when the person
    # running the tool named the column with --identifier, so the words
    # say who decided (review item P1-R6-F8).
    taxonomy.ROLE_IDENTIFIER: (
        "record numbers or codes (you named this column)"
    ),
    taxonomy.ROLE_BINARY: "two possible values",
    taxonomy.ROLE_DATETIME: "dates or times",
    taxonomy.ROLE_COUNT: "whole numbers that count things",
    taxonomy.ROLE_CONTINUOUS: "measured numbers",
    taxonomy.ROLE_CATEGORICAL: "a set of categories",
    taxonomy.ROLE_TEXT: "free text",
    taxonomy.ROLE_UNREPRESENTABLE: (
        "numbers this file format cannot hold"
    ),
}

# Roles whose real labels can appear in the profile, and roles whose
# values never appear in it at all.
_ROLES_WITH_LABELS = (
    taxonomy.ROLE_CONSTANT,
    taxonomy.ROLE_BINARY,
    taxonomy.ROLE_CATEGORICAL,
    # THE LONG TAIL BELONGS HERE OR THIS PAGE UNDERSTATES ITSELF (plan
    # P4-D5, which requires the summary to list every column whose
    # labels will be visible BEFORE anything is written). It is the one
    # role that CHANGED what a column publishes: such a column was free
    # text and published no value at all, and now names its
    # floor-clearing spellings. A page that left it out would tell a
    # person the fewest columns are the ones that disclose.
    taxonomy.ROLE_LONG_TAIL,
)
_ROLES_WITHOUT_VALUES = (
    taxonomy.ROLE_IDENTIFIER,
    taxonomy.ROLE_TEXT,
    taxonomy.ROLE_UNREPRESENTABLE,
)
_ROLES_WITH_RANGES = (
    taxonomy.ROLE_COUNT,
    taxonomy.ROLE_CONTINUOUS,
    taxonomy.ROLE_DATETIME,
    # THE TWO PHASE 4 RANGE ROLES, and they were in NO list at all
    # until 2026-08-22, so a person reading this page was told nothing
    # about a column of clock times, or about one whose numbers each
    # wear a unit -- two of the kinds of column this phase taught
    # synthtwin to read. Both publish
    # a smallest and a largest value and a ladder between them, which
    # is exactly what this list is for. The affixed role's shared text
    # is disclosed separately below, because it is a spelling and this
    # list is about ranges.
    taxonomy.ROLE_CLOCK,
    taxonomy.ROLE_AFFIXED,
)

# What was decided about a number synthtwin uses as a stand-in for "no
# value", in words. The profile records codes so a program can act on
# them; these are the same decisions for a person to read, and neither
# of these tables holds a value of anybody's table.
_VERDICT_WORDS = {
    taxonomy.VERDICT_MISSING: "counted as 'no value'",
    taxonomy.VERDICT_KEPT: "kept as a number",
}
_REASON_WORDS = {
    taxonomy.REASON_OUTLIER_AND_FREQUENT: (
        "far outside the rest of the column, and in enough rows to be a "
        "convention rather than a reading"
    ),
    taxonomy.REASON_NOT_AN_OUTLIER: (
        "inside the range the rest of the column covers, so it reads as "
        "an ordinary value"
    ),
    taxonomy.REASON_TOO_RARE: (
        "in too few rows to be a convention, and removing it would throw "
        "away a real reading"
    ),
    taxonomy.REASON_TOO_FEW_OTHERS: (
        "there are too few other values in this column to judge it against"
    ),
    taxonomy.REASON_KEPT_BY_USER: "you named it with --keep-value",
}

_RULE = "=" * 66


def _text_of(value: object) -> str:
    """Any value as text, for a message, with display controls shown."""
    return parsing.visible(f"{value}")


def _raw_text_of(value: object) -> str:
    """Any value as text, EXACTLY, for anything that is not a message.

    The display boundary belongs where text meets a screen, and this
    module's own page crosses it once, in `cli`, over the whole text.
    Anything this module ASKS a question about -- is this word one of
    synthtwin's own? -- has to be asked about the text the description
    stores, or the question is put to something the description does not
    hold (review item P3-V9-F3).
    """
    return f"{value}"


def _list_of(value: object) -> list[object]:
    """``value`` when it is a list, an empty list otherwise."""
    if isinstance(value, list):
        return value
    return []


def _map_of(value: object) -> dict[str, object]:
    """``value`` when it is a mapping, an empty mapping otherwise."""
    if isinstance(value, dict):
        return value
    return {}


def _count_of(value: object) -> int:
    """``value`` when it is a whole number, zero otherwise."""
    if isinstance(value, int):
        return value
    return 0


def _listed(items: list[str]) -> str:
    """Join names with commas, without handing a list to a text method."""
    text = ""
    for item in items:
        text = item if not text else f"{text}, {item}"
    return text


def _role_words(role: str) -> str:
    """The plain-language name of a role."""
    if role not in _ROLE_WORDS:
        return role
    return _ROLE_WORDS[role]


def _decision_words(code: str) -> str:
    """What was decided about a stand-in number, in words."""
    if code not in _VERDICT_WORDS:
        return code
    return _VERDICT_WORDS[code]


def _because_words(code: str) -> str:
    """Why that was decided, in words."""
    if code not in _REASON_WORDS:
        return code
    return _REASON_WORDS[code]


def _occurrence_shape(column: dict[str, object]) -> dict[str, object]:
    """The repetition mapping a column block carries, or an empty one.

    Absent on every role but the declared identifier, and absent from
    every profile written before version 3, so its absence is an
    ordinary answer here and not a fault.
    """
    if "n_distinct_by_occurrences" not in column:
        return {}
    return _map_of(column["n_distinct_by_occurrences"])


def _number_in(text: str) -> int:
    """A key written as a base-ten number, read back, or zero.

    The repetition mapping's keys are row counts left-padded with zeros
    so that sorted keys are in numeric order; reading one back is what
    turns a key into the number of rows it names. Anything that is not
    a run of digits is not one of those keys and reads as zero.
    """
    if not isinstance(text, str):
        return 0
    if not parsing.is_digit_text(text):
        return 0
    return int(text)


def _repetition_lines(column: dict[str, object]) -> list[str]:
    """What the column's repetition mapping says, in words.

    The profile carries how many different values cover one row, two
    rows and so on. These lines read TWO facts out of that mapping --
    how many values appear in one row only, and the most rows any one
    value covers -- and then say what the mapping is for. They do not
    claim to be the whole mapping: the machine-readable record holds
    every entry, and a summary that printed one line per entry would
    have no bound on its length.

    Both facts are counts of rows and counts of values. Neither is a
    value of the table, and the mapping they come from holds none
    (review item P1-R8-F4).
    """
    shape = _occurrence_shape(column)
    if not shape:
        return []
    alone = 0
    most = 0
    for key in shape:
        occurrences = _number_in(key)
        if occurrences == 1:
            alone = _count_of(shape[key])
        most = max(most, occurrences)
    return [
        (
            f"    how often values repeat: {alone} of the different values "
            f"appear in one row only, and the most repeated of them "
            f"appears in {most} row(s)."
        ),
        (
            "    synthtwin recorded how OFTEN values repeat here, never "
            "which values"
        ),
        (
            "    repeat, so the twin can invent its own codes and repeat "
            "them the same"
        ),
        "    number of times as yours.",
    ]


def _sentinel_lines(column: dict[str, object]) -> list[str]:
    """What the column decided about numbers that can mean "no value".

    Written from the column block and nothing else, so the words and
    the machine-readable record cannot disagree -- including about the
    value itself. A column whose role publishes values carries the
    candidate's spelling; a column whose role publishes none carries
    `(withheld)` in its place (review item P1-R7-F2). This function
    never decides what may be shown; it shows what the profile holds.

    IT SHOWS IT WITHOUT CALLING A POOLED NAME A NUMBER (review of the
    shipped reports, 2026-08-15). `(withheld)` used to be printed where
    the candidate goes, so the line read "(withheld), in 40 row(s):
    kept as a number" -- a sentence naming a spelling no table wrote.
    Where the profile withholds the candidate the line says the number
    is not named here, which is the fact the profile carries.

    The candidates that appeared in too few rows to be named at all are
    NOT listed here. The column's own remark already says how many
    there were, and a line about them here would have had to say which
    way each one went while the profile deliberately does not record
    that against a candidate it will not name.
    """
    verdicts = _list_of(column["sentinel_verdicts"])
    if not verdicts:
        return []
    lines = [
        "    numbers synthtwin checks as stand-ins for 'no value':",
    ]
    for item in verdicts:
        entry = _map_of(item)
        candidate = _text_of(entry["candidate"])
        if candidate == parsing.MISSING_WITHHELD:
            candidate = "a number not named here"
        lines = lines + [
            (
                f"      {candidate}, in "
                f"{_count_of(entry['n_occurrences'])} row(s): "
                f"{_decision_words(_text_of(entry['verdict']))} "
                f"-- {_because_words(_text_of(entry['reason']))}"
            )
        ]
    return lines


def _missing_spelling_words(
    column: dict[str, object], floor: int
) -> list[str]:
    """The spellings the absent cells wore, and the two counts beside them.

    A POOLED NAME IS NOT A SPELLING (review of the shipped reports,
    2026-08-15). Version 4's `missing_by_source` pooled every spelling
    under the publication floor into the single key `(withheld)`, which
    is synthtwin's word for "not published here". Listed beside the real
    spellings it read as one of them, so a column of eight EMPTY cells
    said `counted as missing: (withheld) (8)` -- telling the person
    their blanks wore a marker they would have to account for, which was
    false of all eight.

    FROM CONTRACT VERSION 5 THE TWO ARE NOT EVEN IN THE SAME FIELD
    (section 5). The map holds spellings the table wrote and nothing
    else; the blank cells and the pooled remainder are two counts of
    their own, and each is said here as what it is.

    AND EVERY SPELLING CROSSES THE DISPLAY BOUNDARY HERE (C5-3). The
    description now stores a key character for character, so this is
    the surface that has to show it safely -- version 4 stored a key
    that had already crossed, and this line printed it as it stood.
    """
    sources = _map_of(column["missing_by_source"])
    spellings: list[str] = []
    blank = _count_of(column["n_missing_blank"])
    if blank:
        spellings = spellings + [
            f"{blank} cell(s) with nothing written in them"
        ]
    for spelling in sorted(sources):
        counted = _count_of(sources[spelling])
        spellings = spellings + [f"{_text_of(spelling)} ({counted})"]
    pooled = _count_of(column["n_missing_withheld"])
    if pooled:
        spellings = spellings + [
            (
                f"{pooled} cell(s) whose spelling is not named "
                f"here, because fewer than {floor} cell(s) were "
                f"written that way"
            )
        ]
    return spellings


def _column_lines(column: dict[str, object], floor: int) -> list[str]:
    """The block of lines describing one column."""
    role = _text_of(column["role"])
    lines = [
        f"  {_text_of(column['name'])}",
        f"    read as: {_role_words(role)}",
        f"    why: {_text_of(column['detection_evidence'])}",
        (
            f"    values present: {_count_of(column['n_present'])};   "
            f"missing: {_count_of(column['n_missing'])}"
        ),
    ]
    spellings = _missing_spelling_words(column, floor)
    if spellings:
        lines = lines + [f"    counted as missing: {_listed(spellings)}"]
    lines = lines + _sentinel_lines(column)
    if role in _ROLES_WITH_LABELS:
        levels = _list_of(column["levels"])
        shown = [
            f"{_text_of(_map_of(level)['label'])} "
            f"({_count_of(_map_of(level)['count'])})"
            for level in levels
        ]
        if shown:
            lines = lines + [f"    values in the profile: {_listed(shown)}"]
        withheld = _count_of(column["suppressed_levels"])
        if withheld:
            lines = lines + [
                (
                    f"    values left out because too few rows share them: "
                    f"{withheld} (covering "
                    f"{_count_of(column['suppressed_rows'])} rows)"
                )
            ]
    if role in (taxonomy.ROLE_COUNT, taxonomy.ROLE_CONTINUOUS):
        ladder = _map_of(column["percentiles"])
        lines = lines + [
            (
                f"    smallest: {_text_of(ladder['min'])};   "
                f"middle: {_text_of(ladder['p50'])};   "
                f"largest: {_text_of(ladder['max'])}"
            ),
            (
                f"    average: {_text_of(column['mean'])};   "
                f"spread (standard deviation): {_text_of(column['std'])}"
            ),
        ]
    if role == taxonomy.ROLE_DATETIME:
        # A column written on two clocks is published on one, and this
        # line has to say which, or a reader compares a UTC time with
        # the wall clock they remember writing down.
        clock = ""
        if _text_of(column["datetimes_read_at"]) == "utc":
            clock = (
                "  (written in more than one time zone, so these are "
                "given at UTC)"
            )
        lines = lines + [
            (
                f"    earliest: {_text_of(column['earliest'])};   "
                f"latest: {_text_of(column['latest'])}{clock}"
            )
        ]
    if role == taxonomy.ROLE_IDENTIFIER:
        # A column is here because the reader of this summary put it
        # here. Saying so keeps the words honest: synthtwin never works
        # this role out for itself (review item P1-R6-F8).
        lines = lines + [
            (
                f"    {_count_of(column['n_distinct'])} different values, "
                f"between {_count_of(column['min_length'])} and "
                f"{_count_of(column['max_length'])} characters long. This "
                f"column publishes no value of the table, so the values "
                f"themselves are not in the profile."
            ),
        ]
        # What the profile records about REPETITION, which is a fact
        # about the column and not a value of it (review item P1-R8-F4).
        # It goes before the sentence about who decided the role so that
        # the two claims about what is and is not recorded read together.
        lines = lines + _repetition_lines(column)
        lines = lines + [
            (
                "    synthtwin never decides this for itself: a column "
                "holds record numbers only when you say so with "
                "--identifier."
            ),
        ]
    if role == taxonomy.ROLE_TEXT:
        length = _map_of(column["length"])
        lines = lines + [
            (
                f"    text between {_count_of(length['min'])} and "
                f"{_count_of(length['max'])} characters long. The text "
                f"itself is not in the profile."
            ),
            # What the role MEANS, in one line: synthtwin ruled readings
            # out and settled on none. The column's own remark carries
            # the option to declare it when its values never repeat, so
            # this line does not repeat that (review item P1-R6-F8).
            (
                "    No value of this column reaches the profile, and "
                "synthtwin makes no claim about what these values mean."
            ),
        ]
    for remark in _list_of(column["remarks"]):
        lines = lines + [f"    worth knowing: {_text_of(remark)}"]
    return lines


def words_of_your_own(
    document: dict[str, object],
) -> "list[tuple[str, str, int]]":
    """The person's OWN spellings this description names, and where.

    Each entry is one spelling, the column that names it, and how many
    of that column's cells wore it. A spelling named by two columns is
    two entries, because a person deciding whether to move this file is
    looking for where their word went and not for how many words there
    were.

    WHAT THIS IS FOR, AND IT IS THE WHOLE OF REVIEW ITEM P3-V9-F1.
    Contract 5 section 3.3.1 fixes the derivation: every key of a
    published `missing_by_source` that is not blank and is not a member
    of synthtwin's own thirteen published words is a spelling somebody
    typed after `--missing-value`. So a version 5 description CARRIES
    the person's own declared word, character for character, wherever
    the floor permits the group to be named and the column publishes
    values at all -- and until this function existed, no page said so.
    The summary told the reader the opposite: that synthtwin would not
    keep a record of any word outside those thirteen, printed four
    screens under `counted as missing: <their word> (12)`.

    A FALSE ASSURANCE ABOUT WITHHOLDING IS WORSE THAN NO ASSURANCE.
    The profile is safer to move than the table because of what it
    holds back; a researcher who reads that their diagnosis code is
    absent, and it is not, shares the file on the strength of the
    sentence.

    Guarantees:

    - Inputs: a profile document as built by `profile.build_document`.
      No table and no file is consulted.
    - Determinism: sorted by column position, then by spelling, so two
      runs over one document produce one list.
    - Errors raised: none for a document this package built.
    - Boundary: the spellings are returned RAW, as the document stores
      them from contract version 5 (C5-3). Every caller prints them
      through the display boundary -- the summary through
      `parsing.visible_lines` over the whole page, the command line
      through its own `_shown` -- which is where a key is made safe to
      show and is the same rule `_missing_spelling_words` follows.

    THE QUESTION IS ASKED OF THE RAW SPELLING, and the answer is the raw
    spelling (review item P3-V9-F3's sweep). The first version of this
    function escaped a key before asking whether it is one of
    synthtwin's own words and returned the escaped text -- which made
    the sentence above false, and put a comparison on the wrong side of
    a boundary that exists for screens. No page moves a byte either way,
    because the whole summary crosses the boundary once in `cli` and
    crossing it twice changes nothing; what would have moved is a
    consumer comparing what this returns with the description's own key.
    """
    found: list[tuple[str, str, int]] = []
    for entry in _list_of(document["columns"]):
        column = _map_of(entry)
        name = _raw_text_of(column["name"])
        sources = _map_of(column["missing_by_source"])
        for spelling in sorted(sources):
            raw = _raw_text_of(spelling)
            if taxonomy.is_published_vocabulary(raw):
                continue
            found = found + [(raw, name, _count_of(sources[spelling]))]
    return found


def words_behind(named: "list[tuple[str, str, int]]") -> int:
    """How many words somebody TYPED the listed spellings came from.

    WHY THIS IS NOT `len(named)` (review item P3-V10-F9; plan amendment
    A-P3-42 clause 5). `words_of_your_own` returns one entry per
    spelling per column, because a person looking for their word wants
    to know every place it went. That is the right list and it is the
    wrong COUNT for a sentence about what the person did: one
    `--missing-value XX` over a table holding eleven `XX` cells and
    eleven `" xx "` cells publishes two spellings, and the screen said
    "Words you typed after --missing-value are written into the
    description" about one word they typed and one spelling their table
    chose. Nothing was hidden and nothing was wrong about the list; the
    attribution was wrong, and a person reading it goes looking for a
    second option they never gave.

    THE GROUPING IS THE PRODUCER'S OWN, not a second rule.
    `settings.declaration_matching` has one permitted value -- the exact
    number where the spelling reads as one, else the trimmed and folded
    spelling -- and it is the rule that decided which cells each
    declaration took. Grouping the published spellings by it therefore
    counts declarations exactly as the producer counted them
    (`n_declared`, contract 5 C5-18 as amended), and the same way the
    validator's own recovery does.

    Guarantees:

    - Inputs: the list `words_of_your_own` returns. Nothing is read.
    - Determinism: a fixed function of that list.
    - Errors raised: none.
    - Boundary: a count leaves this function and no spelling does.
    """
    identities: dict[object, int] = {}
    for spelling, _column, _count in named:
        exact = taxonomy.exact_of_spelling(spelling)
        if exact is None:
            identities[("word", parsing.folded(spelling))] = 1
        else:
            identities[("number", exact)] = 1
    return len(identities)


def _your_own_words_lines(document: dict[str, object]) -> list[str]:
    """Which of the reader's own words this description names, by name.

    THIS PAGE HAS TO SAY IT ON ITS OWN FACE (review item P3-V9-F1). A
    person is handed one of the five files, not the set, and the one
    they can read is this one. The column blocks above already print
    every spelling among `counted as missing:`, but nothing there tells
    the reader which of those spellings is a word THEY typed rather
    than a word their table happened to hold -- and the word they typed
    is the one they chose, so it is the one they can be wrong about.

    Nothing new leaves the machine here. Every spelling listed is
    already printed in its own column's block on this page and stored
    in the description beside it; what this adds is the sentence that
    tells a reader which of them came off their command line.

    IT LISTS SPELLINGS AND COUNTS WORDS (review item P3-V10-F9). A word
    somebody typed can reach the description under several spellings,
    because the cells decide the spellings and the person decides the
    word. So the list below has a line per spelling and the sentence
    over it counts what was typed, and where the two numbers differ the
    page says which side each came from rather than leaving the reader
    to think they gave an option they never gave.
    """
    named = words_of_your_own(document)
    if not named:
        return [
            "    The settings are not the whole description, though, and",
            "    no column of this one names a word of your own. That is",
            "    this run and not a rule: it is what the floor, the roles",
            "    of your columns and your table's own cells came to, and",
            "    another table under the same command could name one.",
            "",
        ]
    words = words_behind(named)
    # The sentence is about the words THIS DESCRIPTION NAMES and not
    # about how many were typed, because those are two numbers and the
    # second is on the line above ("named as 'no value': 2"). A person
    # can name two words and have one of them reach the description,
    # which is the ordinary outcome when the other one's cells fall
    # below the floor.
    if words == 1:
        lines = [
            "    WORDS OF YOUR OWN THAT THIS DESCRIPTION NAMES. The settings",
            "    are not the whole description, and this word of yours is",
            "    written into it -- and printed above -- exactly as your",
            "    table spelled it:",
        ]
    else:
        lines = [
            "    WORDS OF YOUR OWN THAT THIS DESCRIPTION NAMES. The settings",
            f"    are not the whole description, and these {words} words of",
            "    yours are written into it -- and printed above -- exactly",
            "    as your table spelled them:",
        ]
    for spelling, column, count in named:
        lines = lines + [f"      {spelling} -- in {column} ({count} cell(s))"]
    if len(named) > words:
        lines = lines + [
            "    There are more lines there than words you named, because",
            "    your table wrote "
            + ("that word" if words == 1 else "some of those words")
            + " more than one way and",
            "    each way is a line of its own. What you typed decided",
            "    which cells count as missing; your table decided how each",
            "    of them is spelled here.",
        ]
    return lines + [
        "    If one of those spellings is something you would not send in",
        "    an email, neither this description nor this page may go",
        "    anywhere until you have dealt with it.",
        "",
    ]


def _declared_count(settings: dict[str, object], key: str) -> int:
    """How many values were declared under ``key``, or zero.

    Zero is also the answer for a profile written under the older shape,
    where the key held the spellings themselves rather than a count.
    Reading that shape is not this function's job; not falling over on
    it is.
    """
    if key not in settings:
        return 0
    block = _map_of(settings[key])
    if "n_declared" not in block:
        return 0
    return _count_of(block["n_declared"])


def _declaration_lines(document: dict[str, object]) -> list[str]:
    """What the profile records about the values the person named.

    Guarantees:

    - Inputs: a profile document as built by `profile.build_document`.
    - Determinism: the text depends only on the document.
    - Errors raised: none for a document this package built.
    - Boundary: no spelling of the PERSON'S reaches the lines rendered
      from the SETTINGS BLOCK, because none reaches that block (review
      item P1-R7-F2). From contract version 5 the block also names
      which members of synthtwin's own thirteen published words were
      typed; these lines say that it does and print how many, and they
      do not repeat the members -- saying the fact is what the contract
      asks of this page (its section 6.6), and a page that travels says
      no more than it must. The block CLOSES with
      `_your_own_words_lines`, which does print the person's own
      spellings, out of the columns that named them and off this same
      page; the boundary that governs those is the display boundary
      every spelling on this page crosses, not silence.

    WHAT THESE LINES MAY NOT CLAIM. The first version of them told the
    person that a value they typed was in neither file, on the reasoning
    that they typed it because it was a value of their table and it was
    therefore held back like any other. That was false, and provably so:
    a column of 200 readings
    with three cells of `-999`, profiled with `--keep-value -999`,
    prints `smallest: -999.0` four lines above. The publication is
    right -- declaring a value KEPT says it is real data, so it is an
    ordinary number of that column, and every column of numbers
    publishes a real smallest and a real largest; that is what a range
    is. What was wrong was the paragraph, and a person deciding whether
    to move this file has to be able to trust the paragraph exactly.
    Overclaiming safety is worse than claiming less.

    So these lines separate the settings from the columns, and the two
    directions from each other. Each statement below was checked against
    what the code does:

    * the settings record counts and the matching rule; in the settings
      block never a spelling of the person's own, in both directions
      and on every role -- and, from contract version 5, which members
      of synthtwin's own published vocabulary were among them;
    * a value named as 'no value' is counted absent, and its spelling is
      listed by its column as one of the spellings it counted as missing
      -- but only where that column publishes values at all and at least
      `small_cell_floor` rows share it, otherwise it is pooled unnamed;
    * a value named as real data is data from that point on, so it can
      be the smallest or largest number of a column of numbers HOWEVER
      FEW rows hold it (a range is not governed by the floor), and it
      can be one of the labels of a column of categories only when at
      least `small_cell_floor` rows share it;
    * a column that publishes nothing at all -- record numbers, free
      text, numbers no format can hold -- still publishes nothing, in
      either direction, and now in every field of its block rather than
      in the fields somebody remembered. A value named with
      `--keep-value` used to travel out of a declared identifier column
      as the `candidate` of a sentinel verdict, which is the one
      remaining way a spelling could leave a column declared precisely
      to keep its spellings in (review item P1-R7-F2). The decision and
      the rows it accounted for are still published; the spelling reads
      `(withheld)`.

    THE CLOSING SENTENCE WAS RETIRED TWICE, and only the second time
    was it retired for the right reason. It began by telling the person
    to keep a note of their own command line because synthtwin would
    keep no record of which values they had named. Contract version 5
    made that false of synthtwin's own thirteen words, since the
    settings now name which of them were typed -- so the sentence was
    narrowed to the words that are NOT synthtwin's, which carried the
    defect forward whole rather than repairing it.

    IT WAS FALSE OF THE VERY RUN IT WAS WRITTEN FOR (review item
    P3-V9-F1). Sixty numbers and twelve cells reading a declared
    marker, at the ordinary floor, publish that marker in
    `missing_by_source` -- correctly, because contract 5 section 3.2
    way 4 is what makes the description readable back -- and this page
    prints it four screens above as `counted as missing: <the marker>
    (12)`. So the page told a researcher their word was not kept while
    showing them the word it had kept. A person who believed it could
    hand on a description carrying a diagnosis code they had been told
    was absent, and the profile is only safer to move than the table
    because of what it withholds: a false assurance about what it
    withholds is worse than no assurance.

    Both halves now say WHERE they hold. The settings-block half keeps
    the claim contract 5 section 6 actually holds to and names its
    scope; `_your_own_words_lines` closes the block by naming the words
    the columns kept, so the page states the exposure rather than
    denying it.

    AND THE OPENING SENTENCE WAS CORRECTED IN THE SAME FAMILY, one
    stage earlier, because the page contradicted itself on the run that
    matters most (plan amendment A-P3-30). It said "the spellings YOU
    typed are not written into its settings" and then, eight lines
    lower, told the person who typed `n/a` that the description records
    which of synthtwin's own words they named. Both halves were true and
    the pair was not readable: the reader who has to act on this page is
    exactly the reader who typed one of the thirteen. The opening now
    names the exception where it makes the claim.

    Nothing is said on a run where nothing was declared. A sentence
    printed on every ordinary run is a sentence people stop reading, and
    the person who has to see this is the person who typed a value.
    """
    settings = _map_of(document["settings"])
    kept = _declared_count(settings, "kept_values")
    declared_missing = _declared_count(settings, "declared_missing_values")
    if not kept and not declared_missing:
        return []
    floor = _count_of(settings["small_cell_floor"])
    lines = [
        "  Values you named yourself, with --keep-value or",
        "  --missing-value:",
        (
            f"    named as real data: {kept};   named as 'no value': "
            f"{declared_missing}"
        ),
        "    The profile records how many DIFFERENT values you named",
        "    each way, and the rule it used to match them. Naming one",
        "    value twice, or naming it again with other spacing or",
        "    capitals, counts once: synthtwin reads those as one value.",
        "    For a value that is one of synthtwin's own words --",
        "    the ones described lower down -- it also records which of",
        "    those words it was. A word of YOUR OWN is not written",
        "    into its settings. That is a rule about the settings and",
        "    nothing else, so read the next lines before you decide",
        "    this file may travel: naming a value does not hide it",
        "    from the description of the column it is in,",
    ]
    if kept and declared_missing:
        # Both options were used, so the reader is about to be given two
        # rules and has to be told they are not one rule said twice.
        lines = lines + [
            "    and the two directions do not work the same way:",
        ]
    else:
        lines = lines + [
            "    and here is what that means:",
        ]
    if declared_missing:
        lines = lines + [
            "      a value you named as 'no value' is counted as absent,",
            "      and THE WORD ITSELF is then written into that column's",
            "      description and printed on this page, spelled character",
            "      for character as your table spelled it, if at least",
            f"      {floor} rows share that spelling and that column",
            "      publishes any values at all. Below that many rows it is",
            "      counted without being named, and a column that publishes",
            "      no values names no spelling at all;",
        ]
    if kept:
        lines = lines + [
            "      a value you named as real data IS data from then on,",
            "      so it appears wherever that column publishes values:",
            "      as the smallest or largest number of a column of",
            "      numbers, however few rows hold it, or as one of the",
            "      labels of a column of categories if at least",
            f"      {floor} rows share it.",
        ]
    lines = lines + [
        "    A column that publishes nothing -- record numbers, free",
        "    text -- still publishes nothing either way.",
    ]
    return (
        lines
        + _own_words_lines(settings)
        + _your_own_words_lines(document)
    )


# The thirteen words of the published vocabulary, counted rather than
# repeated. The contract fixes the list in its own appendix; this page
# says that the description records WHICH of them were typed, and how
# many, because a person deciding whether to move this file has to know
# what it carries about what they typed (contract 5 section 6.6).
_OWN_WORD_KEYS = ("built_in_texts", "built_in_numbers")


def _own_words_named(settings: dict[str, object], key: str) -> int:
    """How many of synthtwin's own published words one option named."""
    record = _map_of(settings[key])
    found = 0
    for name in _OWN_WORD_KEYS:
        if name in record:
            found = found + len(_list_of(record[name]))
    return found


def _own_words_lines(settings: dict[str, object]) -> list[str]:
    """Which of SYNTHTWIN'S OWN words the settings record you named.

    Two sentences, and which of them is printed depends on the run
    rather than on a rule somebody has to remember: a person who named
    only words of their own is told the settings record none of them,
    and a person who named one of synthtwin's is told they record that.

    THE SCOPE OF EVERY SENTENCE HERE IS THE SETTINGS BLOCK, and saying
    so is the repair of review item P3-V9-F1. These lines used to close
    by sending the person away to their own shell history for a record
    of any word outside the thirteen, on the ground that synthtwin
    would keep none. Read as it stood, that spoke for the whole
    document, and it was false of one from the moment contract version
    5 landed: a word of the person's own reaches its column's
    `missing_by_source` under the ordinary floor, and this same page
    prints it four screens above beside the count of cells that wore
    it. What the settings block does not carry is still worth saying --
    it is the one field a declaration is compared against every column
    through -- but it is said with its scope attached, and
    `_your_own_words_lines` below names the words the columns DID keep.
    """
    kept = _own_words_named(settings, "kept_values")
    absent = _own_words_named(settings, "declared_missing_values")
    named = kept + absent
    # THE THIRTEEN ARE NOT SPELLED OUT HERE, and that is deliberate.
    # Three of them are numbers, and a page that travels printing a
    # number beside a column's own facts is a page a reader can mistake
    # for a statement about that column. The list is synthtwin's own and
    # is published in its description contract; what this page owes is
    # the FACT that the description records which of them were typed.
    lines = [
        "    synthtwin has thirteen words of its own that it already",
        "    reads as 'no value' -- an empty cell, NA, n/a, none, null",
        "    and a few more, and three numbers often used as stand-ins.",
        "    They are listed in synthtwin's description contract, and",
        "    the description records which of them you named.",
    ]
    if named:
        lines = lines + [
            (
                f"    {named} of the values you named "
                + ("is" if named == 1 else "are")
                + " one of those, and the"
            ),
            "    description says which. It has to: without that, a check",
            "    of your own table against its own description would read",
            "    those cells the wrong way and report failures that are",
            "    not real. No other word you typed is in the settings, and",
            "    no count, column or row goes with the ones that are.",
        ]
    else:
        lines = lines + [
            "    You named none of them, so the settings record nothing",
            "    there.",
        ]
    return lines + [""]


def _lowered_floor_lines(floor: int) -> list[str]:
    """Said only where this profile was made under a lowered floor.

    THIS PAGE IS ONE OF THE FOUR THAT MUST SAY IT (owner ruling
    2026-08-14, plan amendment A-P3-11). The owner ruled that
    `--smallest-group` below the default is let through end to end, and
    ruled with it that every artifact made from such a description
    carries the fact on its own face -- because a person is handed one
    of these files, not the set, and the JSON's `small_cell_floor` is a
    number in a document a non-programmer does not open. So this page
    says it, the generation report says it and the quality report says
    it, each without reference to the others.

    IT IS CONDITIONAL, and that is the opposite of the rule the honest
    limits are written under. A limit true of every run is printed on
    every run so that nobody comes to expect its absence. This is not a
    limit of synthtwin; it is a fact about THIS description that is
    false of an ordinary one, and printing it on every run -- "your
    floor was not lowered" -- is how a reader is trained to skip
    the paragraph that matters.

    Guarantees:

    - Inputs: the floor this description was made with.
    - Determinism: a fixed function of that number.
    - Errors raised: none.
    - Boundary: no value of the table reaches it.
    """
    if floor >= taxonomy.Settings().small_cell_floor:
        return []
    usual = taxonomy.Settings().small_cell_floor
    lines = [
        (
            "  THE SMALLEST GROUP SIZE WAS LOWERED FOR THIS PROFILE, TO "
            f"{floor}."
        ),
        "",
        f"  synthtwin normally leaves a value out unless at least {usual}",
        "  rows share it. This profile names values that as few as",
        f"  {floor} row(s) share, and says how many rows that is.",
        "",
    ]
    # "a group of 1 is 1 people" is not English, so at a floor of one the
    # sentence is the one that is true there rather than the general one
    # with a bad number in it.
    if floor < 2:
        lines = lines + [
            "  A named group can be a single row. If one row of your table",
            "  is one person, this profile says out loud that exactly one",
            "  person -- on their own -- has that value.",
            "",
        ]
    else:
        lines = lines + [
            (
                "  If one row of your table is one person, a group of "
                f"{floor} is"
            ),
            f"  {floor} people.",
            "",
        ]
    return lines + [
        "  What that can mean for a person. Somebody who already knows",
        "  one true thing about someone in your table -- that they are in",
        "  it at all -- can find the small group that person must be in",
        "  and read off everything else this profile says about that",
        f"  group. That is what the usual {usual} prevents and what this",
        "  profile does not.",
        "",
        "  It does not stop with this file. The twin is built to hold",
        "  these counts exactly, and the twin's report and the quality",
        "  report quote them back, so all five files of a full run carry",
        "  them.",
        "",
    ]


def _all_labels_held_back(column: dict[str, object]) -> bool:
    """Whether a twin of this label column would invent its every cell.

    Two shapes reach it. The floor held every one of this column's
    levels back; or the floor held back every spelling of the levels it
    did publish, which is reachable with no suppressed level at all. In
    both the generator writes neutral stand-ins for every present cell,
    so plan amendment A-P4-2 calls such a column fully invented however
    its role publishes.

    THIS ARITHMETIC IS WRITTEN TWICE, HERE AND IN `rendering`, and the
    duplication is deliberate rather than tidy: this side reads the
    document the producer is about to write, that side reads the typed
    profile a loader handed back, and neither representation is
    available where the other is. `test_p4d2_loud_decline` holds the
    two to the same answer on one table, so a change to one that is not
    a change to the other turns the suite red.
    """
    present = _count_of(column["n_present"])
    if not present:
        return False
    invented = _count_of(column["suppressed_rows"])
    for entry in _list_of(column["levels"]):
        level = _map_of(entry)
        withheld = _map_of(level["variants_withheld"])
        for key in sorted(withheld):
            rows = _count_of(withheld[key])
            # The keys are row counts written as text, zero-padded so
            # they sort as text; `int` reads one because this side of
            # the format has no loader to ask.
            invented = invented + int(key) * rows
    return invented >= present


def _disclosure_lines(document: dict[str, object]) -> list[str]:
    """What of the real table this profile carries, and what it does not."""
    with_labels: list[str] = []
    without_values: list[str] = []
    with_ranges: list[str] = []
    with_shared_text: list[str] = []
    all_invented: list[str] = []
    for entry in _list_of(document["columns"]):
        column = _map_of(entry)
        name = _text_of(column["name"])
        role = _text_of(column["role"])
        if role in _ROLES_WITH_LABELS and _list_of(column["levels"]):
            with_labels = with_labels + [name]
        if role in _ROLES_WITHOUT_VALUES:
            without_values = without_values + [name]
            all_invented = all_invented + [name]
        if role in _ROLES_WITH_RANGES:
            with_ranges = with_ranges + [name]
        # THE ONE SPELLING A RANGES ROLE PUBLISHES. An affixed column
        # names the piece of text its cells share -- `mg`, `$`, `%` --
        # where enough rows wrote it, and that is text of the table
        # however short it is. It has its own sentence because it is
        # not a label and not a range, and a person deciding what may
        # leave their machine is owed it in the place they read about
        # everything else (plan P4-D4.1).
        if role == taxonomy.ROLE_AFFIXED:
            with_shared_text = with_shared_text + [name]
        # A LABEL COLUMN CAN BE FULLY INVENTED WITHOUT PUBLISHING
        # NOTHING (plan amendment A-P4-2, review item P4-C2-F1). It
        # keeps its place in the disclosure lists above -- a published
        # folded label IS something of the table's, and moving it out
        # of them would misstate what this profile carries -- but the
        # forward sentence below is about what a TWIN of it would hold,
        # which is a different question with a different answer.
        if role in _ROLES_WITH_LABELS and _all_labels_held_back(column):
            all_invented = all_invented + [name]
    floor = _count_of(_map_of(document["settings"])["small_cell_floor"])
    lines = [
        "WHAT THIS PROFILE CARRIES FROM YOUR TABLE",
        "",
        "  The profile was computed from your real data, so your",
        "  institution's rules for real-derived material apply to it.",
        "  It contains no rows of your table, but it is not anonymous",
        "  either. Here is exactly what is in it.",
        "",
        # THE HANDLING RULE COVERS FIVE FILES, NOT ONE (plan P2-D11,
        # widened by P3-D3 and again by amendment A-P3-8). Saying it of
        # the profile alone reads as permission for the others, and it
        # is not: the twin reproduces published counts exactly, the
        # report quotes published facts back, the quality report states
        # measurements taken from the file it checked, and THIS FILE --
        # the one being read right now -- repeats the published labels
        # in words. The person deciding what may leave their machine has
        # to be told about all five in the one place they are reading
        # about it, and the file they are holding is one of the five.
        "  The same is true of the other four files a full run makes,",
        "  this page among them: it repeats in words what the profile",
        "  carries, the real labels listed below included.",
        "  The profile, the plain-language summary beside it, the twin,",
        "  the twin's report and the quality report all carry facts",
        "  computed from your real data, so those rules apply to all",
        "  five of them, not to the profile alone.",
        "",
    ]
    lines = lines + _lowered_floor_lines(floor)
    if with_labels:
        # THE SPELLINGS ARE PART OF THIS CLAIM, and saying only "labels"
        # would now be a promise the profile no longer keeps. A label is
        # published in one settled form -- trimmed, upper and lower case
        # folded together -- and beside it the profile records each
        # exact spelling the file used for that label, held to the same
        # floor (owner decisions 9 and 11). A person deciding whether
        # the profile may leave their machine has to read that here, not
        # discover it in the file.
        lines = lines + [
            "  Real labels you will see in the profile, with how often each",
            f"  appears (only labels shared by at least {floor} rows). Beside",
            "  each label, the exact spellings your file uses for it --",
            f"  capitals and spacing included -- again only where {floor} rows",
            "  or more wrote it that way:",
            f"    {_listed(with_labels)}",
            "",
        ]
    else:
        lines = lines + [
            "  No column has labels visible in the profile.",
            "",
        ]
    if with_ranges:
        lines = lines + [
            "  Real smallest and largest values, and the points in between",
            "  that describe the shape of the column:",
            f"    {_listed(with_ranges)}",
            "",
        ]
    if with_shared_text:
        lines = lines + [
            "  A piece of text your cells share -- the unit or the sign",
            "  written around each number, like mg or $ -- named exactly",
            f"  as your file writes it, and only where at least {floor} rows",
            "  wrote it that way:",
            f"    {_listed(with_shared_text)}",
            "",
        ]
    if without_values:
        # The claim is exact, and it is worth saying why it is worded
        # this way. These columns still carry counts -- how many values
        # there are, how long they are, how many of them are all digits
        # -- and they carry what synthtwin decided about a number that
        # can mean "no value": how many rows it accounted for and which
        # way the decision went, with the number itself replaced by
        # `(withheld)`. The earlier wording said "only how many there
        # are and how long they are" while one of those decisions
        # carried the number's spelling out of a column whose whole
        # purpose was to keep its values in (review item P1-R7-F2). The
        # spelling is gone now; so is the wording that did not cover
        # the rest.
        #
        # EVERY column in this list carries one count more since profile
        # version 4: how many different values cover one row, two rows,
        # and so on. A column declared with --identifier has carried it
        # since review item P1-R8-F4; free text and columns of numbers
        # this format cannot hold carry it now too (plan P2-D4), because
        # they publish no value either and their shape of repetition was
        # otherwise unrecorded. It is a count of rows and a count of
        # values, so "only counts" below still covers it, and the
        # column's own block above says it in words for the person who
        # wants to know what shape of repetition was recorded.
        lines = lines + [
            "  No value at all, in any form -- only counts, lengths, and what",
            "  synthtwin decided about the column:",
            f"    {_listed(without_values)}",
            "",
        ]
    # WHAT THIS MEANS FOR THE TWIN, said where a person meets the
    # withholding rather than only in the twin's own report (plan P4-D2
    # item 4). It is true of the generator this version ships: a column
    # this description carries no writable value of gives the generator
    # nothing but counts and shapes, so every present cell of that
    # column's twin is synthtwin's own. The list is NOT the one above:
    # a label column whose every level or every spelling the floor held
    # back is fully invented too, and saying so only for the three
    # publishing-nothing roles left the person unwarned about it
    # (amendment A-P4-2, review item P4-C2-F1).
    if all_invented:
        # THE REASON HAS TO BE TRUE OF BOTH ROUTES INTO THIS LIST
        # (review item P4-C3-F1). "There is nothing of yours in this
        # description for it to write" is true of a column that
        # publishes no value at all -- and false of a label column
        # whose folded label IS published while every spelling of it
        # sits below the floor. Both end with a twin whose every cell
        # is invented, for two different reasons, so the sentence
        # names both rather than the first one twice.
        lines = lines + [
            "  If you build a twin from this description, every value in",
            "  these columns will be one synthtwin made up. Either the",
            "  column publishes no value at all, or its spellings were",
            "  each worn by too few rows to publish, and either way the",
            "  twin has to invent what it writes --",
            f"    {_listed(all_invented)}",
            "  The twin's own report says so again, column by column.",
            "",
        ]
    lines = lines + _declaration_lines(document)
    notes = _list_of(document["publication_notes"])
    if notes:
        lines = lines + ["  What was left out, column by column:"]
        for entry in notes:
            note = _map_of(entry)
            lines = lines + [
                f"    {_text_of(note['column'])}: {_text_of(note['note'])}"
            ]
        lines = lines + [""]
    return lines


def _first_row_lines(document: dict[str, object]) -> "list[str]":
    """What the summary says about where the column names came from.

    Guarantees:

    - Inputs: a profile document as built by `profile.build_document`.
    - Determinism: the text depends only on the document.
    - Errors raised: none for a document this package built.
    - Boundary: says nothing when the reading was settled by evidence or
      by the person, and speaks only when the names were ASSUMED. An
      assumption the reader is not told about is the defect this exists
      to prevent; saying it on every ordinary run instead would train
      people to skip it.
    """
    source = _map_of(document["source"])
    if "header_by_convention" not in source:
        return []
    if not source["header_by_convention"]:
        return []
    return [
        "",
        "About the first row of your file:",
        "  synthtwin read the first row as the column names because that is",
        "  how a table is normally written, and nothing in your file said",
        "  otherwise. It did not confirm that those values are names.",
        "  If your file has no column names, then what synthtwin is calling",
        "  column names is really your first record -- it is described here",
        "  as names and it is NOT counted among the rows above.",
        "  Run the command again with --first-row data if that is the case,",
        "  and synthtwin will name the columns itself and keep every record.",
    ]


def render(document: dict[str, object], encoding_note: str) -> str:
    """The whole summary, as the text printed and written to disk.

    Guarantees:

    - Inputs: a profile document as built by `profile.build_document`,
      and one sentence describing how the file was read.
    - Determinism: the text depends only on the document and that
      sentence; every list it prints is in the document's own order or
      sorted, and nothing consults a clock or the environment.
    - Errors raised: none for a document this package built.
    - Boundary: no file is opened, and nothing appears here that is not
      already in the document -- which is what keeps the words and the
      machine-readable record from ever disagreeing.
    """
    n_rows = _count_of(document["n_rows"])
    n_columns = _count_of(document["n_columns"])
    lines = [
        _RULE,
        "synthtwin: what your table looks like",
        _RULE,
        "",
        f"Your table has {n_rows} rows and {n_columns} columns.",
        encoding_note,
        "",
    ]
    # When the column names were assumed rather than shown, the person
    # reading this must be told before they read anything below it: if
    # the assumption is wrong, the first row of their table is being
    # described as column names and is missing from every count on this
    # page. It goes here, near the top, and not in the disclosure block
    # at the end, because it changes what every later line means.
    lines = lines + _first_row_lines(document)
    lines = lines + [
        "",
        "This is a description of your table, not a copy of it. Next,",
        "'synthtwin generate' uses this description to build a synthetic",
        "twin: a table with the same columns, the same number of rows, and",
        "each column holding the kinds of values and the counts recorded",
        "below, every cell of it worked out from this description and a",
        "seed. The twin is built from this file alone: your table is not",
        "opened again, and the generator samples or copies no row of it.",
        "Numbers computed on a twin are not research results -- develop your",
        "analysis on the twin, then run the finished analysis on your real",
        "table.",
        "",
        "After that, 'synthtwin validate' measures the twin against this",
        "description and writes the quality report: which of the",
        "obligations recorded below the file meets, which it misses, and",
        "which nothing written in a CSV can evidence either way. Each",
        "command prints the next one for you when it finishes, so you",
        "never have to work out a command line from this page.",
        "",
        # WHAT THE DESCRIPTION DOES NOT DESCRIBE (plan P2-D11, residual
        # R-P2-3). This page is where a person first meets the idea of a
        # twin of their table, and every column below is described on
        # its own -- so a reader who is not told otherwise here will
        # assume the twin keeps what holds BETWEEN their columns. It
        # does not, and the honest place to say so is beside the promise
        # rather than only in the twin's own report.
        "What this description does NOT describe. Every column below is",
        "described on its own, and the twin is built the same way, so it",
        "carries no cross-column structure at all: nothing that links two",
        "of your columns is in it -- not a taller person weighing more,",
        "not a code that only ever appears beside one region, not two",
        "columns left empty in the same rows.",
        "",
        "Every row is built on its own too, and this description",
        "never says what one row of your table is, so if your table holds",
        "several rows per person or per visit, anything that groups rows",
        "behaves differently on the twin than it does on your table.",
        "Cross-column structure arrives in a later version of synthtwin.",
        "",
        # THE QUALIFIED CLAIM, IN THE PLACE A PERSON ACTUALLY READS IT
        # (plan P2-D11). "Built from the description" is a statement
        # about where the twin's values come from. It is not a promise
        # that no twin row can equal a real one, and this summary made
        # exactly that promise until Phase 2, in a flat clause asserting
        # the twin holds none of the reader's rows, which was false.
        # Meeting published counts exactly can force the match, and the
        # eleven-row case is the shortest true example rather than a
        # corner nobody meets: it is what every small single-label
        # column does.
        "One thing that sentence does NOT say. Because the twin has to",
        "match the counts in this description exactly, the arithmetic can",
        "force a twin row to match a real one. If your table had eleven",
        "rows and one column, and all eleven rows shared one label, this",
        "description publishes that label with the count eleven -- so the",
        "twin has to write it in all eleven of its rows, and each of those",
        "rows is the row you have. Nothing was copied; there was no other",
        "answer. synthtwin offers no formal privacy guarantee.",
        "",
        _RULE,
        "COLUMNS, ONE BY ONE",
        _RULE,
        "",
    ]
    floor = _count_of(_map_of(document["settings"])["small_cell_floor"])
    for entry in _list_of(document["columns"]):
        lines = lines + _column_lines(_map_of(entry), floor) + [""]
    lines = lines + [_RULE] + _disclosure_lines(document)
    # The lines are joined by hand: the offline policy accepts a text
    # method only with arguments it has resolved, and a list built at
    # run time is not one (plan D6.2).
    text = ""
    for line in lines:
        text = text + line + "\n"
    return text
