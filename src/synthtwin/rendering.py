"""The two files a `generate` run leaves behind (plan P2-D10).

One command writes two artifacts, and they are two different kinds of
thing, so they are rendered by two functions here rather than by one:

* `twin_csv` turns the built twin into the exact bytes of the twin
  table. Its reader is a PROGRAM -- the researcher's own analysis code,
  or the profiler reading the twin back -- so nothing here may alter a
  cell for the sake of a screen. The byte rules are method G2 and are
  written out in `twin_csv`'s own docstring, because "CSV" is not one
  format and a rule left unstated is a rule two programs will disagree
  about.
* `report` turns the same run into the plain-language report. Its reader
  is a PERSON, so every column name, label and spelling in it goes
  through `parsing.visible` before it reaches the text -- a name out of
  somebody's table can carry an escape sequence, and a report is opened
  in a terminal as often as in an editor.

WHY THE REPORT SAYS THE SAME THINGS EVERY RUN. A twin is a file of
values that look like data and are not; whoever picks it up next may not
be the person who built it. So the report states, on every run and
whether or not anything went wrong: which seed built it; that the
columns were built one at a time and carry no structure between them;
that the rows were built one at a time and the description never said
what one row of the real table is; where the twin's values come from and
the one case in which a twin row can nonetheless equal a real one; that
all three files of a full run carry facts computed from real data; and
which cells common spreadsheet software will read as a formula. None of
those is conditional on anything, because a warning that appears only
sometimes is a warning nobody comes to expect.

WHAT IT MEASURES AND WHAT IT DOES NOT. Nothing here recomputes anything:
every number in this report is one the GENERATOR measured on the cells it
had just written, and this module puts words around it. Two kinds of
measurement arrive. A DEVIATION is a published fact the twin could not
meet, with the value achieved beside the value published. An
APPROXIMATION is a fact the contract never obliged the twin to meet
exactly -- an average, an interior rung of a ladder, the count of
different dates -- carrying its published value, the value the twin's own
cells hold, and the two ends of the bound method G12 fixes for it. Both
are printed in full, so no fact is approximate and unchecked.

What is still NOT here is a fidelity verdict: no claim that the twin is
good enough for a purpose, and no measure of anything the description
never published. That is Phase 3's work, and this report says so rather
than implying the silence is a pass.

THE BOUNDARY THIS MODULE UPHOLDS (plan P2-D1). It reads the loaded
description and the built twin, and nothing else. It opens no file,
writes no file, and imports neither the table reader nor pandas, directly
or through anything it imports: `contract` reads one description file,
`generation` reads none at all, and `parsing` imports nothing outside
this package.

Imports here stay within the allowlist (plan D6.2): this module imports
only from this package.
"""

from synthtwin import contract, generation, parsing

# -- the twin's bytes (method G2) -------------------------------------

# The three characters that decide whether a field has to be quoted, and
# the quote character itself. A field holding a comma would otherwise
# read as two fields; a field holding a line feed or a carriage return
# would otherwise read as two rows.
_QUOTE = '"'
_COMMA = ","
_NEWLINE = "\n"
_RETURN = "\r"

# The byte-order mark, written as an escape because a character nobody
# can see has no business sitting in source anybody has to read. A first
# column name beginning with it must be quoted whatever else it holds:
# written plainly it would begin the file with the mark's own bytes, and
# the reader that then opens the twin consumes them -- so the column
# would come back under a different name than the description publishes
# (plan P2-D10, method G2 exception 1).
_MARKER = "\ufeff"

# The characters that make common spreadsheet software read a cell as a
# formula rather than as text (plan P2-D10, residual R-P2-6). The twin
# is never altered to avoid them -- a published label has to be written
# as it was published, or the counts the twin exists to reproduce stop
# holding -- so they are counted and warned about instead.
_FORMULA_LEADERS = ("=", "+", "-", "@", "\t", "\r")

# -- the report's words -----------------------------------------------

_RULE = "=" * 66

# What each column holds, in words, keyed by the axis the generator
# dispatched on rather than by the role name (plan P2-D3). A reader of
# the report and a reader of the code are then looking at the same
# question.
_TYPE_WORDS = {
    "unknown": "no values at all",
    "numeric": "numbers this file format cannot hold",
    "constant": "one repeated value",
    "binary": "two possible values",
    "datetime": "dates or times",
    "count": "whole numbers that count things",
    "continuous": "measured numbers",
    "categorical": "a set of categories",
    "code": "record numbers or codes (you named this column)",
    "text": "free text",
}

# What the description's own words for a stand-in decision mean. The
# codes are the profiler's; these are the same two decisions written for
# a person, and neither table holds a value of anybody's table.
_VERDICT_WORDS = {
    "missing": "counted as 'no value'",
    "kept": "kept as a number",
}


def _shown(value: object) -> str:
    """One value out of a description, safe to put into the report.

    Anything synthtwin did not write itself -- a column name, a label,
    an absent-value spelling, a sentence the profiler recorded -- goes
    through here first. Every character that instructs a display is
    shown as text, the line feed included, so a value cannot forge a
    line that reads as though synthtwin wrote it.
    """
    return parsing.visible(f"{value}")


def _joined(items: "list[str]") -> str:
    """Names in a row, separated by commas, without a text method.

    The offline policy accepts a text method only with arguments it has
    resolved, and a list built while the program runs is not one (plan
    D6.2), so the commas are put in by hand.
    """
    text = ""
    for item in items:
        text = item if not text else f"{text}, {item}"
    return text


def _needs_quoting(cell: str) -> "tuple[bool, bool]":
    """Whether ``cell`` must be quoted, and whether it holds a quote.

    Two answers from one walk of the cell, because the second decides
    whether the more expensive doubling step is needed at all: a field
    is quoted when it holds a comma, a quote character, a carriage
    return or a line feed, and only a field holding a quote character
    has to have anything rewritten inside it.
    """
    special = False
    quoted = False
    for character in cell:
        if character == _QUOTE:
            quoted = True
            special = True
        elif (
            character == _COMMA
            or character == _NEWLINE
            or character == _RETURN
        ):
            special = True
    return (special, quoted)


def _field(cell: str, always: bool) -> str:
    """One cell as it is written in the twin (method G2).

    ``always`` is the canonical exception: the first column name of a
    header row beginning with the byte-order mark is quoted whether or
    not anything else about it needs quoting.
    """
    special, quoted = _needs_quoting(cell)
    if not special and not always:
        return cell
    if not quoted:
        return f"{_QUOTE}{cell}{_QUOTE}"
    body = ""
    for character in cell:
        body = body + character
        if character == _QUOTE:
            body = body + _QUOTE
    return f"{_QUOTE}{body}{_QUOTE}"


def _begins_with_the_marker(cell: str) -> bool:
    """True when ``cell`` starts with the byte-order mark."""
    for character in cell:
        return character == _MARKER
    return False


def _line(cells: "tuple[str, ...]", header: bool) -> str:
    """One whole line of the twin, without its line ending.

    Two canonical exceptions to minimal quoting live here (method G2).
    The first: a header row whose first name begins with the byte-order
    mark has that name quoted. The second: a row of a ONE-column table
    whose only cell is absent is written as two quote characters rather
    than as nothing, because a line with nothing on it is not a row that
    any reader agrees about -- the shipped reader refuses it, since it
    cannot tell a record whose one value is missing from a blank line
    somebody left in the file, and the second reader drops it. Two quote
    characters read back as an empty cell, which is what an absent value
    is. The exception cannot arise with two or more columns: a row of
    absent cells is then written as commas, which is not an empty line.
    """
    if len(cells) == 1:
        one = cells[0]
        if not one:
            return f"{_QUOTE}{_QUOTE}"
    text = ""
    for place in range(len(cells)):
        if place:
            text = text + _COMMA
        always = header and place == 0 and _begins_with_the_marker(cells[place])
        text = text + _field(cells[place], always)
    return text


def twin_csv(twin: generation.Twin) -> str:
    """The twin table's exact text, ready to be written (method G2).

    Guarantees:

    - Inputs: one twin as `generation.generate` built it, and nothing
      else. No path, no file, no description: everything this needs the
      twin already carries.
    - Determinism: a fixed function of the twin. The same twin always
      gives the same text, character for character, on every platform.
    - Errors raised: none. Every cell is text by the time it arrives
      here, and no rule below can fail on any text.
    - Boundary: nothing is read and nothing is written; this hands back
      the text and the caller decides what becomes of it.

    The format, stated in full because "CSV" is not one format:

    * fields are separated by a comma, rows by a line feed, and the last
      row ends with a line feed like every other;
    * a field is quoted when and only when it holds a comma, a quote
      character, a carriage return or a line feed, and a quote character
      inside a quoted field is written twice. There is no escape
      character;
    * TWO canonical exceptions to that rule: a header row whose first
      name begins with the byte-order mark has that name quoted, and the
      one cell of a one-column row that holds nothing is written as two
      quote characters. `_line` says what each of them prevents;
    * the header row is written when the description says the column
      names came from the table's own file, and not written when the
      description says synthtwin made them up;
    * the columns are in the description's own order, which is the order
      of the description's column list.

    The caller writes it as UTF-8 with no byte-order mark of its own;
    the twin's bytes are then the same on every platform (plan D12), and
    a twin built from a table that was read as Western European text is
    written as UTF-8 like every other (residual R-P2-5).
    """
    text = ""
    if twin.write_header:
        text = text + _line(twin.names, True) + _NEWLINE
    for row in twin.rows:
        text = text + _line(row, False) + _NEWLINE
    return text


# -- the report (plan P2-D10, P2-D11) ---------------------------------


def _formula_hazard(twin: generation.Twin) -> "tuple[int, list[str]]":
    """How many cells a spreadsheet reads as a formula, and where.

    The header names are counted too when a header row is written: a
    column name beginning with one of those characters is a cell of the
    file like any other.
    """
    total = 0
    named: list[str] = []
    for place in range(len(twin.columns)):
        hits = 0
        if twin.write_header:
            for leader in _FORMULA_LEADERS:
                if _first_character(twin.names[place]) == leader:
                    hits = hits + 1
        for cell in twin.columns[place]:
            for leader in _FORMULA_LEADERS:
                if _first_character(cell) == leader:
                    hits = hits + 1
        if hits:
            named = named + [f"'{_shown(twin.names[place])}'"]
        total = total + hits
    return (total, named)


def _first_character(cell: str) -> str:
    """The first character of ``cell``, or nothing when it is empty."""
    for character in cell:
        return character
    return ""


def _seed_lines(twin: generation.Twin) -> "list[str]":
    """The seed, and what running the command again does."""
    return [
        f"Seed: {twin.seed}.",
        "Run the command again on the same description, with the same seed",
        "and the same version of synthtwin, and you get this twin again,",
        "byte for byte. A different seed gives a different twin that follows",
        "the description just as closely -- neither of them is the more",
        "correct one.",
    ]


def _header_lines(profile: contract.Profile) -> "list[str]":
    """Which header the twin was given, and what that name is worth.

    The second half is required rather than a nicety (plan P2-D6). The
    profiler can take a first row AS names by convention, because nothing
    in the file settled the question; a report that said only "the names
    were written" would hide a warning the description carries, and the
    person would develop against a twin whose first record is missing.
    """
    source = profile.source
    if source.header_source == "file":
        lines = [
            "The twin's first line holds the column names, because the",
            "description says your table's own file supplied them.",
        ]
    else:
        lines = [
            "The twin has no line of column names, because the description",
            "says your table's file had none and synthtwin made the names up",
            "(column_1, column_2, and so on). The names are in the",
            "description, and the twin's columns are in the same order.",
        ]
    if source.header_by_convention:
        lines = lines + [
            "",
            "Those names were ASSUMED to be names. Nothing in your table",
            "settled the question, so what the twin carries as column names",
            "may in fact be your table's first record -- and if it is, that",
            "record is missing from every count the description holds and",
            "from the twin. The description records the reason in these",
            f"words: {_shown(source.header_evidence)}",
            "If that first row was data, describe the table again with",
            "'--first-row data' and build the twin from the new description.",
        ]
    return lines


def _encoding_lines(profile: contract.Profile) -> "list[str]":
    """How the real file was read, and what the twin is written as."""
    lines = [
        "The twin is UTF-8 text with newline line endings and no",
        "byte-order mark, whatever your own table was written as.",
    ]
    if profile.source.used_fallback_encoding:
        return lines + [
            "The description records that your table was not readable as",
            "UTF-8 and was read as Western European text (Latin-1), so any",
            "accented letter in a published label reached the twin through",
            "that reading.",
        ]
    return lines + [
        (
            f"The description records that your table was read as UTF-8 "
            f"(encoding: {_shown(profile.source.encoding)})."
        ),
    ]


def _independence_lines() -> "list[str]":
    """The two limits that hold for every twin this version builds.

    Both are stated in every report (plan P2-D11, residual R-P2-3). They
    are not failures of this run: they are what this version of synthtwin
    models, and somebody who does not know them can draw a conclusion
    from the twin that the real table would not support.

    The wording is held to the same words the charter, `README.md`,
    `SECURITY.md`, the package docstring, the command's status screen and
    the profiler's summary use -- no cross-column structure at all, rows
    treated as independent, the grain undescribed, and cross-column
    structure arriving in a later phase -- and
    `tests/test_claim_inventory.py` holds every one of those surfaces to
    it (review item P2-C1-F7). A twin that a reader believes carries
    structure between its columns is worse than no twin: the reader gets
    a number, not an error.
    """
    return [
        "1. EVERY COLUMN WAS BUILT ON ITS OWN. This version of synthtwin",
        "   carries no cross-column structure at all -- no fact about how",
        "   two columns move together -- so nothing that links two columns",
        "   of your table is in the twin: not a taller person weighing",
        "   more, not a later date costing more, not a code that only ever",
        "   appears beside one region, not two columns left empty in the",
        "   same rows. Analysis code developed on the twin RUNS; a number",
        "   it computes from two columns of the twin means nothing about",
        "   your table. Cross-column structure arrives in a later version",
        "   of synthtwin.",
        "",
        "2. EVERY ROW WAS BUILT ON ITS OWN, and the description of your",
        "   table never says what one row of it is. If your table holds",
        "   several rows per person, per visit or per site, the twin does",
        "   not: its rows are independent of each other. Anything that",
        "   groups rows -- an average per person, a repeated-measures",
        "   model, a count of visits each -- behaves differently on the",
        "   twin than it will on your table. The twin is faithful one row",
        "   at a time, and a twin of a repeated-measures table",
        "   misdescribes the subject-level truth even where every column",
        "   of it is right on its own.",
        "",
        "3. NUMBERS COMPUTED ON THE TWIN ARE NOT RESEARCH RESULTS. Develop",
        "   your analysis on the twin, then run the finished analysis on",
        "   your real table, inside the environment that holds it.",
    ]


def _invented_columns(profile: contract.Profile) -> "frozenset[str]":
    """The columns whose every value the twin made up (contract 6.10).

    Three roles publish no value of the table anywhere in their block --
    record numbers, free text, and numbers too large to hold -- and so
    does any column declared a record number, whatever its role. A cell
    of one of those columns was invented by synthtwin; a cell of any
    other MAY be a value the description published. The report needs
    the difference because it tells the reader two different things
    about a spreadsheet hazard, and saying the wrong one is a lie about
    where the cell came from.
    """
    made_up: list[str] = []
    for column in profile.columns:
        if column.structural_role == "identifier" or column.role in (
            "free_text",
            "numeric_unrepresentable",
        ):
            made_up = made_up + [column.name]
    return frozenset(made_up)


def _formula_lines(
    profile: contract.Profile, twin: generation.Twin
) -> "list[str]":
    """The spreadsheet warning, which appears whatever the count is.

    The hazard is counted and the columns are named, and the twin is
    NOT altered: a published label has to be written as the description
    publishes it, or the counts the twin exists to reproduce stop
    holding (plan P2-D10, residual R-P2-6). Quoting is not offered as
    protection, because it is not protection: the quoting belongs to the
    file format and the spreadsheet strips it before it decides what the
    cell is.

    AND IT SAYS WHICH KIND OF CELL EACH COLUMN HOLDS (owner decision 9,
    2026-08-13). This paragraph used to tell every reader that a
    hazardous cell was a value their description published, which is
    false for a column that publishes no values at all: there the cell
    was INVENTED, and it opens with a sign because the description's own
    counts leave no other spelling of that width -- which is itself the
    proof that the real column held such values. Both facts are worth a
    sentence, and neither is worth a sentence that says the other.
    """
    total, named = _formula_hazard(twin)
    made_up = _invented_columns(profile)
    # A HAZARDOUS HEADER IS NOT AN INVENTED CELL (review item P3-C5-F8).
    # The count above takes the header row's names beside the data,
    # because a name is a cell of the file like any other -- but a name
    # came from the description, and calling it made-up would be the
    # same class of false sentence this paragraph was rewritten to
    # remove. So the invented list is built from DATA cells only, and a
    # column whose only hazard is its name is left out of it.
    invented: list[str] = []
    for place in range(len(twin.columns)):
        name = twin.names[place]
        if name not in made_up:
            continue
        for cell in twin.columns[place]:
            if _first_character(cell) in _FORMULA_LEADERS:
                invented = invented + [f"'{_shown(name)}'"]
                break
    lines = [
        "Common spreadsheet software reads a cell that begins with  =  +  -",
        "@  a tab or a carriage return as a formula rather than as text,",
        "and works out something of its own instead of showing you the",
        "value. Some spreadsheets can be made to reach other files or other",
        "programs that way.",
        "",
    ]
    if total:
        lines = lines + [
            f"This twin has {total} such cell(s), in these columns:",
            f"  {_joined(named)}",
        ]
        touched = [one for one in named if one in invented]
        if touched:
            lines = lines + [
                "",
                "Some of those cells synthtwin MADE UP, in these columns:",
                f"  {_joined(touched)}",
                "Those columns publish no value of your table, so every",
                "value in them is invented. Your description's own counts",
                "are what leave no other way to spell a value of that",
                "width -- which is also how you know your real column",
                "held values written the same way.",
            ]
    else:
        lines = lines + [
            "No cell of this twin begins with one of those characters, and",
            "no twin is checked for it only when somebody suspects it, so",
            "the count is printed either way.",
        ]
    return lines + [
        "",
        "synthtwin does not change those cells, and there is no spelling",
        "that would make a spreadsheet read them as text. Where the value",
        "is one your description published, it has to be written exactly",
        "as published or the counts the twin exists to reproduce stop",
        "holding. Where synthtwin invented it, every other spelling of",
        "that width would have broken a count your description states.",
        "Quotation marks around a cell are NOT protection: they belong to",
        "the file format, and a spreadsheet removes them before it decides",
        "what the cell is.",
        "",
        "What to do: open the twin with the program that will use it --",
        "your analysis code -- or with a spreadsheet's 'import as text'",
        "route, rather than by double-clicking the file. And if this",
        "matters to your work, it is worth settling in your real table",
        "rather than working around it here: values written that way",
        "behave the same way there, which is why the twin has them at",
        "all.",
    ]


def _deviation_lines(twin: generation.Twin) -> "list[str]":
    """Every published fact the twin could not meet, achieved and published.

    The list is the generator's own measurement, in its own column
    order; nothing is added to it here and nothing is left out of it
    here. Where it is empty, the report says what that does and does not
    mean, because "nothing to report" is a claim in its own right.
    """
    lines = [
        "The description publishes facts about your real table, and the",
        "twin was built to hold every one of them. Where one of them could",
        "not be held exactly, it is named here with the value the twin",
        "actually holds beside the value the description publishes.",
        "",
    ]
    if not twin.deviations:
        lines = lines + [
            "Nothing was given up in this run: every published fact this",
            "method reproduces exactly was reproduced exactly.",
            "",
        ]
    for deviation in twin.deviations:
        lines = lines + [
            f"'{_shown(deviation.column)}' -- {_shown(deviation.fact)}",
            f"  the description says: {_shown(deviation.published)}",
            f"  the twin holds:       {_shown(deviation.achieved)}",
            f"  what that means:      {_shown(deviation.note)}",
            "",
        ]
    return lines + [
        "Some facts are approximate by construction and are not listed",
        "here, because being approximate is not the same as being given",
        "up. A column's average, its spread, the shape of its values, the",
        "nine steps between its smallest and its largest value, and the",
        "middle length of a piece of text are all built to land close to",
        "the description's numbers rather than on them. Every one of them",
        "was measured on this twin and the next section prints it, with",
        "the range it was allowed and whether it landed inside.",
    ]


def _approximation_lines(twin: generation.Twin) -> "list[str]":
    """Every approximated fact, measured, with the range it was allowed.

    The list is the generator's own measurement, in its own column order
    and its own fact order; nothing is computed here. Each entry gets
    its plain-language name, the two values side by side, the two ends
    of the bound and the answer -- because an approximated fact whose
    bound nobody printed is a fact a reader has to take on trust, and
    this repository treats a check whose result is not shown as a check
    that was not made (plan P2-D11, contract section 2.2).
    """
    lines = [
        "A fact in this section is APPROXIMATE by construction: the method",
        "that builds the twin cannot land on it exactly, so instead it",
        "promises a RANGE, worked out from the way the cells are built and",
        "from the size of your column. Every one of them is measured on the",
        "twin's own cells and printed here with the description's value",
        "beside it. 'Inside the range' means the twin did what this method",
        "promises; it does not mean the two numbers are equal, and the two",
        "numbers are both printed so you can see the difference yourself.",
        "",
    ]
    if not twin.approximations:
        return lines + [
            "This twin has no approximated fact at all: no column of",
            "numbers, dates or free text, so nothing here was approximate.",
        ]
    outside = 0
    for found in twin.approximations:
        if not found.inside:
            outside = outside + 1
    lines = lines + [
        (
            f"{len(twin.approximations)} approximated fact(s) were measured "
            f"on this twin."
        ),
    ]
    if outside:
        lines = lines + [
            f"{outside} of them landed OUTSIDE the range this method",
            "promises. Each one that did is also named in the section above,",
            "because a promise this method could not keep is a fact the twin",
            "did not hold.",
            "",
        ]
    else:
        lines = lines + [
            "Every one of them landed inside the range this method promises.",
            "",
        ]
    shown = ""
    for found in twin.approximations:
        if found.column != shown:
            shown = found.column
            lines = lines + [f"'{_shown(found.column)}'"]
        result = "inside the range"
        if not found.inside:
            result = "OUTSIDE the range"
        lines = lines + [
            f"  {_shown(found.note)} ({_shown(found.fact)})",
            (
                f"    the description says {_shown(found.published)}; "
                f"the twin holds {_shown(found.achieved)}"
            ),
            (
                f"    allowed anywhere from {_shown(found.lowest)} to "
                f"{_shown(found.highest)}: {result}"
            ),
        ]
    return lines


def _missing_lines(column: contract.ColumnBlock) -> "list[str]":
    """How the real table wrote its absent cells, which the twin does not.

    Every absent cell of the twin is written as an empty cell, so the
    spellings and the reasons behind them are recorded here and nowhere
    else (residual R-P2-2).
    """
    if not column.n_missing:
        return []
    lines = [
        "  The twin writes every one of them as an empty cell, so how your",
        "  table wrote them is here rather than in the twin:",
    ]
    for spelling in sorted(column.missing_by_source):
        count = column.missing_by_source[spelling]
        lines = lines + [f"    {_shown(spelling)}: {count} cell(s)"]
    classes = column.missing_by_class
    reasons = [
        (classes.blank, "nothing was written there"),
        (classes.declared_missing, "a value you named with --missing-value"),
        (
            classes.numeric_sentinel,
            "a number this column used as a stand-in for 'no value'",
        ),
        (classes.text_code, "a code such as NA that reads as 'no value'"),
        (
            classes.withheld,
            "a spelling held back, because too few rows wrote it that way",
        ),
    ]
    for count, reason in reasons:
        if count:
            lines = lines + [f"    counted absent because {reason}: {count}"]
    return lines


def _sentinel_lines(column: contract.ColumnBlock) -> "list[str]":
    """What was decided about each stand-in number, and one consequence.

    The consequence is worth its line every time (residual R-P2-13): a
    twin value can land on one of those numbers by ordinary arithmetic,
    and describing the twin again would then count it absent -- exactly
    as the real column's own cells were counted.
    """
    if not column.sentinel_verdicts:
        return []
    lines = [
        "  Numbers this column used as stand-ins for 'no value', and what",
        "  synthtwin decided about each. The twin does not reproduce them:",
    ]
    for verdict in column.sentinel_verdicts:
        decision = verdict.verdict
        if decision in _VERDICT_WORDS:
            decision = _VERDICT_WORDS[decision]
        lines = lines + [
            (
                f"    {_shown(verdict.candidate)} in "
                f"{verdict.n_occurrences} row(s): {_shown(decision)}, "
                f"because {_shown(verdict.reason)}"
            )
        ]
    return lines + [
        "  A number the twin worked out can land on one of those spellings",
        "  by arithmetic alone. Describing the twin again would count that",
        "  cell absent, exactly as your own column's cells were counted.",
    ]


def _datetime_lines(column: contract.ColumnBlock) -> "list[str]":
    """The date spelling the twin does not keep (residual R-P2-7)."""
    facts = column.facts
    if not isinstance(facts, contract.DatetimeFacts):
        return []
    return [
        "  The twin writes this column's dates in the international form",
        "  (2024-03-15, or 2024-Q1 for a column of quarters), at the same",
        "  precision your table had and with an offset only where the",
        (
            f"  description records one. Your table's own spelling was read "
            f"as '{_shown(facts.parser_family)}', and it is NOT kept:"
        ),
        "  code that reads dates with an explicit format needs that format",
        "  changed for the twin.",
    ]


def _column_lines(
    column: contract.ColumnBlock,
    outcome: generation.ColumnOutcome,
    notes: "list[str]",
) -> "list[str]":
    """One column's block: what it holds, and what only the description has.

    The two counts on the second line come from the OUTCOME, which the
    generator counted from the cells it had written, beside the two the
    description publishes. Printing the description's numbers alone
    would have been a sentence that cannot be wrong and therefore says
    nothing; printing both means a reader can see that they agree.

    `notes` is what the description says was held back for this column,
    already collected by the caller so that this walks the note list once
    for the whole document rather than once per column.
    """
    words = column.statistical_type
    if words in _TYPE_WORDS:
        words = _TYPE_WORDS[words]
    lines = [
        f"'{_shown(column.name)}' -- {words}",
        (
            f"  The twin holds {outcome.n_present} value(s) and leaves "
            f"{outcome.n_missing} cell(s) empty, counted from its own"
        ),
        (
            f"  cells; the description records {column.n_present} and "
            f"{column.n_missing}."
        ),
    ]
    if column.detection_evidence:
        lines = lines + [
            (
                f"  How synthtwin read this column: "
                f"{_shown(column.detection_evidence)}"
            )
        ]
    for remark in column.remarks:
        lines = lines + [f"  Note from the description: {_shown(remark)}"]
    for note in notes:
        lines = lines + [f"  Held back from the description: {_shown(note)}"]
    lines = lines + _missing_lines(column)
    lines = lines + _sentinel_lines(column)
    lines = lines + _datetime_lines(column)
    if column.n_sentinel_candidates_unpublished:
        lines = lines + [
            (
                f"  {column.n_sentinel_candidates_unpublished} other "
                f"number(s) were looked at as possible stand-ins and are"
            ),
            "  not named in the description, so they are not named here",
            "  either.",
        ]
    return lines + [""]


def _notes_for(profile: contract.Profile, name: str) -> "list[str]":
    """The description's publication notes for one column, in its order."""
    found: list[str] = []
    for note in profile.publication_notes:
        if note.column == name:
            found = found + [note.note]
    return found


def _handling_lines() -> "list[str]":
    """Where the twin's values come from, and how the files are handled.

    The record claim is a PROVENANCE claim and is written as one (plan
    P2-D11). A claim about the RESULT -- that the twin holds nothing of
    the reader's -- would be false: allocating a published count exactly
    can leave the arithmetic no other answer than a row that matches a
    real one. Saying where the values came from is a claim synthtwin can
    keep.

    The load-bearing phrases here are deliberately the same ones the
    charter, `README.md`, `SECURITY.md`, the package docstring, the
    command's status screen and the profiler's summary use, and
    `tests/test_claim_inventory.py` holds all of them to it. One product
    saying this one way is the point; six paraphrases would leave a
    reader wondering which surface to believe.
    """
    return [
        "WHERE THE TWIN'S VALUES CAME FROM. Building the twin read no",
        "table: it samples or copies no row of yours, and every cell was",
        "worked out from the description and the seed. That says where the",
        "values came from, and it is the claim synthtwin makes.",
        "",
        "It does NOT say that no row of the twin can equal a row of your",
        "table. The description publishes counts, and holding a count",
        "exactly can force a twin row to match a real one. A table of 11",
        "rows and one column, whose single label is shared by enough rows",
        "to be published, publishes that label with the count 11 -- so the",
        "twin holds it in all 11 rows, and every row matches. Nothing was",
        "copied; there was nothing else to write. The smaller the table and",
        "the fewer its columns, the more often that happens.",
        "",
        "HOW TO KEEP THESE FILES. All three files of a full run --",
        "the description, this twin and this report -- carry facts computed",
        "from your real data: counts, ranges, published labels and the",
        "spellings named above. Keep all three under the rules your",
        "institution applies to the table itself, and check with whoever",
        "approves data leaving your environment before you move any of them",
        "anywhere. synthtwin offers no formal privacy guarantee: nothing",
        "here bounds, mathematically, what someone could work out from the",
        "twin.",
    ]


def report(profile: contract.Profile, twin: generation.Twin) -> str:
    """The whole plain-language report, as the text printed and written.

    Guarantees:

    - Inputs: the description this run was given, loaded by
      `contract.load_profile`, and the twin `generation.generate` built
      from it. Nothing else: no path, no table, no file, no clock. The
      report names no file path, so the same run writes the same report
      wherever its two files are put.
    - Determinism: a fixed function of those two values. Every list it
      prints is in the description's own order or sorted, and nothing
      consults the environment or a random source.
    - Errors raised: none, for a description the loader accepted and a
      twin the generator built from it.
    - Boundary: no file is opened, and no value appears here that the
      description does not already carry or that the generator did not
      measure while building the twin. The real table is not read, not
      named and not reachable from here.
    - Display: every column name, label, spelling and recorded sentence
      passes through `parsing.visible` before it reaches the text, so a
      value carrying an escape sequence is shown rather than obeyed
      (plan P2-D10). The caller puts the finished text through the
      display boundary once more on its way to the screen and to disk.

    What it always says, whatever the run did: the seed; that columns
    were built independently; that rows were built independently and the
    description never said what one row is; where the twin's values came
    from and the one case in which a twin row can equal a real one; that
    all three artifacts carry facts computed from real data and are kept
    under the institution's rules; which cells a spreadsheet reads as a
    formula; every published fact the twin could not meet, with the
    value achieved beside the value published; and every fact the
    contract calls approximated, with the value achieved beside the
    value published, the two ends of the range this method promises for
    it, and whether the twin landed inside.
    """
    lines = [
        _RULE,
        "synthtwin: your synthetic twin, and what it carries",
        _RULE,
        "",
        "This report describes the twin table written beside it. The twin",
        (
            f"has {twin.n_rows} row(s) and {len(twin.names)} column(s), in "
            f"the description's own"
        ),
        "order. Read this before you use the twin, and keep the two files",
        "together: this is the only place that says which facts the twin",
        "holds exactly, which it holds approximately, and which it does not",
        "hold at all.",
        "",
    ]
    lines = lines + _seed_lines(twin) + [""]
    lines = lines + _header_lines(profile) + [""]
    lines = lines + _encoding_lines(profile)
    lines = lines + [
        "",
        _RULE,
        "THREE THINGS THAT ARE TRUE OF EVERY TWIN THIS VERSION BUILDS",
        _RULE,
        "",
    ]
    lines = lines + _independence_lines()
    lines = lines + [
        "",
        _RULE,
        "BEFORE YOU OPEN THE TWIN IN A SPREADSHEET",
        _RULE,
        "",
    ]
    lines = lines + _formula_lines(profile, twin)
    lines = lines + [
        "",
        _RULE,
        "WHERE THE TWIN DOES NOT MATCH THE DESCRIPTION",
        _RULE,
        "",
    ]
    lines = lines + _deviation_lines(twin)
    lines = lines + [
        "",
        _RULE,
        "HOW CLOSE THE APPROXIMATE FACTS CAME",
        _RULE,
        "",
    ]
    lines = lines + _approximation_lines(twin)
    lines = lines + [
        "",
        _RULE,
        "COLUMN BY COLUMN: WHAT ONLY THE DESCRIPTION HOLDS",
        _RULE,
        "",
        "The twin reproduces the values and the counts. What it cannot",
        "carry -- how your table wrote the cells it left empty, what was",
        "held back as too rare to publish, how synthtwin read each column --",
        "is recorded here, once per column.",
        "",
    ]
    # The description's columns and the twin's outcomes are the same
    # list in the same order -- the schema order the contract fixes and
    # the generator consumes (S3) -- so the two are walked by position.
    for place in range(len(profile.columns)):
        column = profile.columns[place]
        lines = lines + _column_lines(
            column, twin.outcomes[place], _notes_for(profile, column.name)
        )
    lines = lines + [_RULE, ""] + _handling_lines()
    # The lines are joined by hand: the offline policy accepts a text
    # method only with arguments it has resolved, and a list built while
    # the program runs is not one (plan D6.2).
    text = ""
    for line in lines:
        text = text + line + _NEWLINE
    return text
