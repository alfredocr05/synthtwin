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
    candidate's spelling and it is printed; a column whose role
    publishes none carries `(withheld)` in its place and that is
    printed instead, exactly as the withheld missing spellings above
    are printed (review item P1-R7-F2). This function never decides
    what may be shown; it shows what the profile holds.

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
        lines = lines + [
            (
                f"      {_text_of(entry['candidate'])}, in "
                f"{_count_of(entry['n_occurrences'])} row(s): "
                f"{_decision_words(_text_of(entry['verdict']))} "
                f"-- {_because_words(_text_of(entry['reason']))}"
            )
        ]
    return lines


def _column_lines(column: dict[str, object]) -> list[str]:
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
    sources = _map_of(column["missing_by_source"])
    if sources:
        spellings = [
            f"{spelling} ({_count_of(sources[spelling])})"
            for spelling in sorted(sources)
        ]
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
                f"{_count_of(column['max_length'])} characters long. The "
                f"values themselves are not in the profile."
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
    - Boundary: counts only. No spelling reaches these lines, because
      none reaches the settings block they are rendered from (review
      item P1-R7-F2).

    WHAT THESE LINES MAY NOT CLAIM. The first version of them told the
    person "the values themselves are NOT written into the profile or
    into this summary ... a value you typed is a value of your table --
    that is why you typed it -- so it is held back like every other
    value." That was false, and provably so: a column of 200 readings
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

    * the settings record counts and the matching rule, never a
      spelling, in both directions and on every role;
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
        "    The profile records how many values you named each way and",
        "    the rule it used to match them. The spellings you typed are",
        "    not written into its settings, and they are not written",
        "    here. Naming a value does not hide it from the description",
    ]
    if kept and declared_missing:
        # Both options were used, so the reader is about to be given two
        # rules and has to be told they are not one rule said twice.
        lines = lines + [
            "    of the column it is in, though, and the two directions",
            "    do not work the same way:",
        ]
    else:
        lines = lines + ["    of the column it is in, though:"]
    if declared_missing:
        lines = lines + [
            "      a value you named as 'no value' is counted as absent.",
            "      Its column lists it among the spellings it counted as",
            f"      missing, if at least {floor} rows share that spelling",
            "      and that column publishes any values at all;",
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
    return lines + [
        "    A column that publishes nothing -- record numbers, free",
        "    text -- still publishes nothing either way. If you need a",
        "    record of which values you named, keep a note of the",
        "    command you ran; synthtwin will not keep one for you.",
        "",
    ]


def _disclosure_lines(document: dict[str, object]) -> list[str]:
    """What of the real table this profile carries, and what it does not."""
    with_labels: list[str] = []
    without_values: list[str] = []
    with_ranges: list[str] = []
    for entry in _list_of(document["columns"]):
        column = _map_of(entry)
        name = _text_of(column["name"])
        role = _text_of(column["role"])
        if role in _ROLES_WITH_LABELS and _list_of(column["levels"]):
            with_labels = with_labels + [name]
        if role in _ROLES_WITHOUT_VALUES:
            without_values = without_values + [name]
        if role in _ROLES_WITH_RANGES:
            with_ranges = with_ranges + [name]
    floor = _count_of(_map_of(document["settings"])["small_cell_floor"])
    lines = [
        "WHAT THIS PROFILE CARRIES FROM YOUR TABLE",
        "",
        "  The profile was computed from your real data, so your",
        "  institution's rules for real-derived material apply to it.",
        "  It contains no rows of your table, but it is not anonymous",
        "  either. Here is exactly what is in it.",
        "",
        # THE HANDLING RULE COVERS FOUR FILES, NOT ONE (plan P2-D11,
        # widened by P3-D3). Saying it of the profile alone reads as
        # permission for the others, and it is not: the twin reproduces
        # published counts exactly, the report quotes published facts
        # back, and the quality report states measurements taken from the
        # file it checked, so all three are real-derived as well. The
        # person deciding what may leave their machine has to be told
        # about all four in the one place they are reading about it.
        "  The same is true of the other three files a full run makes.",
        # The four artifacts are named in ONE line rather than wrapped
        # across two, because the claim inventory reads this file as
        # text and a phrase split between two string literals is a
        # phrase no reader of the source can grep for.
        "  The profile, the twin, the twin's report and the quality report",
        "  all carry facts computed from your real data, so those rules",
        "  apply to all four of them, not to the profile alone.",
        "",
    ]
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
    for entry in _list_of(document["columns"]):
        lines = lines + _column_lines(_map_of(entry)) + [""]
    lines = lines + [_RULE] + _disclosure_lines(document)
    # The lines are joined by hand: the offline policy accepts a text
    # method only with arguments it has resolved, and a list built at
    # run time is not one (plan D6.2).
    text = ""
    for line in lines:
        text = text + line + "\n"
    return text
