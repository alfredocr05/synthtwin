"""Reading a spreadsheet workbook with the standard library alone.

WHAT THIS MODULE IS FOR. A researcher's table very often arrives as a
workbook rather than as delimited text, and until this module synthtwin
refused every one of them. Reading one is not like reading a CSV file:
a CSV file's cells ARE their characters, while a workbook's cells are
typed, and what a reader shows a person is worked out from the type,
the stored number and a format code that lives somewhere else entirely.
The measured study behind plan P4-D77 read the same probe workbooks
four ways and found the readers disagreeing about nearly every one of
those answers -- a text cell of digits comes back as an integer from
pandas and as its characters from openpyxl, a date is a number wearing
a format, and an empty-string cell and an absent cell are one thing to
one reader and two to another. So this module records what the cell
HOLDS, never what some reader would make of it, and the description
publishes the spelling rule beside it.

WHY THE STANDARD LIBRARY ALONE. synthtwin's offline guarantee is a
property of its import graph (plan D6), and every workbook library
would have to enter that graph as a third runtime dependency. The two
Python writers also corrupt exactly the cells this landing exists to
carry. So the package reads a workbook with `zipfile` and
`xml.parsers.expat` and nothing else; openpyxl is a DEVELOPMENT
dependency that the tests use as an independent oracle and that
`src/synthtwin` never imports.

WHAT THIS MODULE REFUSES, AND WHY EVERY CAP IS NAMED. A workbook is a
zip package of XML, and both halves of that sentence are an attack
surface on a file synthtwin was pointed at by somebody who did not
write it. The study measured each of these rather than assuming it:

* A document type declaration is refused outright, before any content
  is parsed. It is how both the entity-expansion and the external-entity
  attacks are written, and no workbook a spreadsheet writes has one.
* The total expanded size, the expansion ratio of any one member, the
  row and column counts, the shared-string count and the length of one
  cell's text are each capped, and each cap is its own refusal naming
  what was too big and what to do. A zip bomb of 5.2 MB expanding to
  46 MB cost the two libraries 20 seconds and 445 MB with no limit
  applied by either.
* Nothing is ever extracted to a path, so a member named with `..`
  reaches no filesystem; it is refused by name all the same, because a
  package holding one is not a workbook a spreadsheet wrote.
* A formula is never evaluated and an external link is never followed.
  What a formula cell carries into the description is its CACHED value
  and whether a cache existed at all -- which is what every reader but
  a spreadsheet application sees.
* A macro project is never read and never copied, and the report names
  the workbook as carrying one.

THE BOUNDARY, AND WHY THE PACKAGE IS OPENED SOMEWHERE ELSE. This module
OPENS NOTHING. It is reached by the loader and by the description
producer -- `contract` reads a workbook block against the vocabulary
below -- and `contract` is in the GENERATOR's import graph, so a module
that opened a file could not live here: the generator never reads a
table, and the rule is that the module which opens one is not in its
graph at any instant (plan P2-D1). The split is the same one `dialect`
already has. Everything here works on bytes and records already in
hand; `reading.opened_workbook` is what turns a path into those bytes,
and it lives beside the only other code in this package that opens the
user's table.
"""

import dataclasses
import xml.parsers.expat

from synthtwin import dialect, errors

# -- what a workbook is, decided by its opening bytes ------------------
#
# NEVER BY THE FILE'S NAME. The study found that many exports named
# `.xls` are really HTML or 2003 XML, that an encrypted workbook is a
# compound file whatever it is called, and that a `.xlsm` is an ordinary
# zip package. A reader that trusts the extension mis-routes all three
# and reports the wrong trouble to the person.

KIND_PACKAGE = "package"
KIND_COMPOUND = "compound"
KIND_MARKUP = "markup"
KIND_OTHER = "other"

_ZIP_MARK = b"PK\x03\x04"
_EMPTY_ZIP_MARK = b"PK\x05\x06"
_COMPOUND_MARK = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"

# The caps. Each is a named refusal of its own; none of them is a
# guess, and the numbers Excel itself enforces are used where they
# exist rather than numbers of this package's own invention.
MAXIMUM_ROWS = 1_048_576
MAXIMUM_COLUMNS = 16_384
MAXIMUM_EXPANDED_BYTES = 128_000_000
MAXIMUM_MEMBER_RATIO = 200
MAXIMUM_SHARED_STRINGS = 1_000_000
MAXIMUM_CELL_CHARACTERS = 32_767
MAXIMUM_MEMBERS = 4_096
# THE CAP THAT BOUNDS THE WORK ITSELF, AND THE MEASUREMENT IT IS SET
# FROM (repair of landing 2b.10).
#
# The measured zip bomb passes every SIZE cap honestly -- 5.2 megabytes
# packing to 46, a ratio of under nine, its million rows sitting at
# exactly Excel's own maximum -- and spends it all on one sheet of a
# million styled cells. Nothing about its size is unusual; what is
# unusual is how many cells that size buys, so the cell count is what
# has to be capped.
#
# THE FIRST WRITING OF THIS CAP WAS A GUESS AND THE GUESS WAS WRONG. It
# stood at four million cells, and a review measured what that costs: a
# legal 13-megabyte package of three million cells took 172 seconds and
# 1.78 gigabytes of peak resident memory, so a file sitting at the cap
# would have cost something like 2.4 gigabytes and four minutes. A cap
# that admits that is not a bound on anything.
#
# What a cell actually costs was then measured rather than reasoned
# about: 1,048,708 cells read in 4.3 seconds at 632 megabytes of
# maximum resident set size, which is about 600 bytes a cell (the cell
# itself, its place in the sheet's index, and its column's four
# per-cell lists). One million cells is therefore about 600 megabytes
# and a few seconds, and that is where the cap sits. A table of fifty
# thousand rows by twenty columns clears it; the study's bomb does NOT,
# and is refused by this cap rather than read -- which is what the
# earlier report of this landing claimed and had not measured.
MAXIMUM_CELLS = 1_000_000


def kind_of(data: bytes) -> str:
    """Which kind of file these opening bytes begin.

    Guarantees:

    - Inputs: the first bytes of a file, however few.
    - Determinism: a fixed function of the bytes. Nothing is opened and
      the file's name is never consulted.
    - Errors raised: none. A file this cannot place is KIND_OTHER, and
      the caller decides what to say about it.
    """
    if not isinstance(data, bytes):
        raise TypeError("internal check: a file's opening bytes were not bytes")
    if data[:4] == _ZIP_MARK or data[:4] == _EMPTY_ZIP_MARK:
        return KIND_PACKAGE
    if data[:8] == _COMPOUND_MARK:
        return KIND_COMPOUND
    lead = 0
    while lead < len(data) and data[lead : lead + 1] in (
        b" ",
        b"\t",
        b"\r",
        b"\n",
        b"\xef",
        b"\xbb",
        b"\xbf",
    ):
        lead = lead + 1
    if data[lead : lead + 1] == b"<" and _opens_markup(data[lead + 1 :]):
        return KIND_MARKUP
    return KIND_OTHER


# WHAT MARKUP OPENS WITH, AND WHY A LESS-THAN SIGN ALONE IS NOT IT (plan
# P4-D168). The first writing called any file whose first character was
# `<` markup, and a delimited table whose first header cell was
# `<5 ng/mL` -- a detection limit, written the way a laboratory writes
# one -- was refused as a web page and told to save itself from Excel,
# where the same bytes had been read correctly before. What an HTML or
# XML export opens with is a declaration, a comment or one of a few
# element names, followed by the end of that name.
_MARKUP_OPENINGS = (
    b"?xml",
    b"!doctype",
    b"!--",
    b"html",
    b"head",
    b"body",
    b"meta",
    b"table",
    b"style",
    b"workbook",
    b"?mso-application",
)


def _opens_markup(after: bytes) -> bool:
    """Whether the bytes after a `<` begin a declaration or a known element.

    Letters are compared without their case, byte by byte, and an element
    name has to END there -- a space, a line break, `>` or `/` -- so
    `<tablespoon` is not `<table`. A comment needs no ending.

    AND AN ELEMENT'S NAME ENDING IN A SPACE IS NOT ENOUGH (plan P4-D170).
    A header cell `<body temp` or `<table 2` ends the name in a space too,
    and such a table was refused as a web page. What follows a space in
    markup is the tag's end or an attribute -- a name and `=` -- so an
    element name is markup where it is followed by `>` or `/`, or by
    spaces and then one of those or an attribute. A declaration (`<?xml`,
    `<!doctype`) keeps the plain rule: nothing a table writes opens so.
    """
    for opening in _MARKUP_OPENINGS:
        if len(after) < len(opening):
            continue
        same = True
        for index in range(len(opening)):
            held = after[index]
            if 65 <= held <= 90:
                held = held + 32
            if held != opening[index]:
                same = False
                break
        if not same:
            continue
        if opening == b"!--":
            return True
        if len(after) == len(opening):
            return True
        if opening[0] in (63, 33):
            if after[len(opening)] in (32, 9, 10, 13, 62, 47):
                return True
            continue
        if _tag_goes_on(after[len(opening) :]):
            return True
    return False


def _tag_goes_on(rest: bytes) -> bool:
    """Whether the bytes after an element's name read as the rest of a tag.

    `>` or `/` straight away; or spaces, and then `>`, `/`, the next
    tag's `<`, the end of the bytes read, or an attribute -- a name of
    letters, figures, `_`, `:`, `.` or `-` beginning with a letter, `_`
    or `:`, then spaces and `=`.
    """
    at = 0
    if at < len(rest) and rest[at] in (62, 47):
        return True
    spaced = False
    while at < len(rest) and rest[at] in (32, 9, 10, 13):
        at = at + 1
        spaced = True
    if not spaced:
        return False
    if at >= len(rest) or rest[at] in (62, 47, 60):
        return True
    first = rest[at]
    if not (_is_letter(first) or first in (95, 58)):
        return False
    while at < len(rest) and (
        _is_letter(rest[at]) or 48 <= rest[at] <= 57 or rest[at] in (95, 58, 46, 45)
    ):
        at = at + 1
    while at < len(rest) and rest[at] in (32, 9, 10, 13):
        at = at + 1
    return at < len(rest) and rest[at] == 61


def _is_letter(held: int) -> bool:
    """Whether one byte is an ASCII letter."""
    return 65 <= held <= 90 or 97 <= held <= 122


# -- the package, opened under every cap -------------------------------
#
# THE STRING CHECKS BELOW ARE NOT DECORATION. The offline audit accepts a
# method call only on a value it can trace to an allowlisted API or has
# been shown to be a string (plan D6.2). A zip member's name and an
# element's name both arrive from outside this module's sight -- one
# from the package's own directory, one from the parser -- so each one
# passes an exact type gate before any text method touches it.


def _after_colon(name: str) -> str:
    """The local part of an element name, after any namespace prefix."""
    if not isinstance(name, str):
        raise TypeError("internal check: an element name was not text")
    return name.split(":")[-1]


def names_a_place_outside(name: str) -> bool:
    """Whether a member name reaches outside the package it is in."""
    if not isinstance(name, str):
        raise TypeError("internal check: a part's name was not text")
    if name.startswith("/") or name.startswith("\\"):
        return True
    return ".." in name.split("/")


def names_a_folder(name: str) -> bool:
    """Whether a member name is a folder rather than a part."""
    if not isinstance(name, str):
        raise TypeError("internal check: a part's name was not text")
    return name.endswith("/")


# -- the XML, parsed with no document type declaration accepted --------


@dataclasses.dataclass
class _Walk:
    """What one parse accumulates.

    The handlers below grow these lists with `+=` on an ATTRIBUTE rather
    than on a name of their own. That is not a style choice: a name
    rebound inside a nested function would be a local of that function,
    and the one keyword that would fix it -- `nonlocal` -- is refused
    outright by the offline audit, as is `.append`. An attribute keeps
    one object and never rebinds a name.
    """

    depth: "list[str]"
    open_names: "list[str]"
    open_marks: "list[dict[str, str]]"
    text: "list[str]"
    found: "list[tuple[str, dict[str, str], str]]"
    stopped: "list[str]"


@dataclasses.dataclass
class _StringWalk:
    """What the walk over the stored text accumulates."""

    items: "list[str]"
    pending: str
    inside: bool
    stopped: int
    # How deep the walk stands inside a PHONETIC run (`rPh`), whose text
    # is a reading aid shown above the cell and never the cell's value.
    phonetic: int


@dataclasses.dataclass
class _CellWalk:
    """What the walk over one sheet accumulates, cell by cell.

    NOTHING HERE HOLDS THE DOCUMENT. The first writing of this module
    collected every element of a part and then read the cells out of
    that list, which is fine for a workbook of a few hundred cells and
    was measured costing 920 megabytes on a sheet of a million -- about
    876 bytes for every cell, nearly all of it the element records
    rather than the cells. A sheet is the one part of a workbook that
    has no bound a person would notice, so it is walked as it parses and
    only the cells are kept.
    """

    cells: "list[Cell]"
    strings: "tuple[str, ...]"
    formats: "tuple[str, ...]"
    reference: str
    marked_kind: str
    style: int
    value: str
    inline: str
    in_value: bool
    in_inline: bool
    formula: bool
    cached: bool
    last_row: int
    last_column: int
    frozen: int
    filtered: str
    tabled: bool
    stopped: int
    # Inside an inline string, whether the walk stands in one of its text
    # runs, and how deep inside a phonetic run (plan P4-D163).
    in_text: bool
    phonetic: int


def elements(
    data: bytes, shown: str, wanted: "tuple[str, ...]"
) -> "list[tuple[str, dict[str, str], str]]":
    """Every element of `wanted`, with its marks and its own text.

    Guarantees:

    - Inputs: one member's bytes, the path for a refusal, and the local
      element names to collect. Namespaces are not resolved: every
      writer the study measured puts the spreadsheet vocabulary in the
      default namespace, so the name after any colon identifies an
      element.
    - Order: a document type declaration stops the parse BEFORE any
      content is seen, whatever the declaration says. That one rule is
      what closes both the entity-expansion and the external-entity
      families at once: no entity is ever defined, so no entity can be
      external, and nothing is ever fetched.
    - Determinism: a fixed function of the bytes.
    - Errors raised: ProfileError for a declaration, for markup this
      cannot read, and for a cell's text past its cap.
    - Boundary: nothing is opened and nothing is fetched.
    """
    walk = _Walk([], [], [], [], [], [])

    def declared(
        name: str, system: "str | None", public: "str | None", internal: int
    ) -> None:
        walk.stopped += ["declaration"]
        raise ValueError("a document type declaration is not read")

    def started(name: str, marks: "dict[str, str]") -> None:
        local = _after_colon(name)
        walk.depth += [local]
        if local in wanted:
            walk.open_names += [local]
            walk.open_marks += [marks]
            walk.text += [""]

    def ended(name: str) -> None:
        local = _after_colon(name)
        if walk.depth:
            del walk.depth[-1]
        if local in wanted and walk.open_names:
            walk.found += [
                (walk.open_names[-1], walk.open_marks[-1], walk.text[-1])
            ]
            del walk.open_names[-1]
            del walk.open_marks[-1]
            del walk.text[-1]

    def texted(piece: str) -> None:
        if not walk.text:
            return
        grown = walk.text[-1] + piece
        if len(grown) > MAXIMUM_CELL_CHARACTERS:
            walk.stopped += ["length"]
            raise ValueError("a cell's text is past its cap")
        walk.text[-1] = grown

    parser = xml.parsers.expat.ParserCreate()
    parser.StartDoctypeDeclHandler = declared
    parser.StartElementHandler = started
    parser.EndElementHandler = ended
    parser.CharacterDataHandler = texted
    parser.buffer_text = True
    try:
        parser.Parse(data, True)
    except ValueError as error:
        if walk.stopped and walk.stopped[0] == "declaration":
            raise errors.ProfileError(
                errors.workbook_declares_a_document_type(shown)
            ) from error
        raise errors.ProfileError(
            errors.workbook_cell_too_long(shown, MAXIMUM_CELL_CHARACTERS)
        ) from error
    except xml.parsers.expat.ExpatError as error:
        raise errors.ProfileError(
            errors.workbook_part_unreadable(shown)
        ) from error
    return walk.found


# -- what a cell holds -------------------------------------------------
#
# THESE CLASSES ARE THE CELL'S OWN, NOT A READER'S. The study's first
# finding is that every reader derives something different from the same
# cell: a text cell of digits is an integer to pandas and its characters
# to openpyxl; an empty-string cell, an absent cell and a styled blank
# are three things in the file and one thing (a missing value) to
# pandas. A description that recorded what a reader made of a cell could
# not be written back, so what is recorded here is what the file holds.

CELL_ABSENT = dialect.SHEET_CELL_ABSENT
CELL_BLANK = dialect.SHEET_CELL_BLANK
CELL_EMPTY = dialect.SHEET_CELL_EMPTY
CELL_TEXT = dialect.SHEET_CELL_TEXT
CELL_NUMBER = dialect.SHEET_CELL_NUMBER
CELL_BOOLEAN = dialect.SHEET_CELL_BOOLEAN
CELL_ERROR = dialect.SHEET_CELL_ERROR
CELL_DATE = dialect.SHEET_CELL_DATE
CELL_CLASSES = dialect.SHEET_CELL_CLASSES

# The error cells a spreadsheet writes, by kind. A kind outside this
# list is carried as its own characters and counted as an error all the
# same. The list lives in `dialect`, where the twin's writer reads it.
ERROR_KINDS = dialect.SHEET_ERROR_KINDS

BOOLEAN_TRUE = dialect.SHEET_BOOLEAN_TRUE
BOOLEAN_FALSE = dialect.SHEET_BOOLEAN_FALSE

# Excel's built-in number formats, by id. The study found that Excel
# RENUMBERS custom ids when it saves and drops unused ones, so a
# description that published an id would describe a different format
# after an ordinary re-save. The code is published instead, and these
# are the codes the ids below stand for.
BUILT_IN_FORMATS = {
    0: "General",
    1: "0",
    2: "0.00",
    3: "#,##0",
    4: "#,##0.00",
    9: "0%",
    10: "0.00%",
    11: "0.00E+00",
    12: "# ?/?",
    13: "# ??/??",
    14: "mm-dd-yy",
    15: "d-mmm-yy",
    16: "d-mmm",
    17: "mmm-yy",
    18: "h:mm AM/PM",
    19: "h:mm:ss AM/PM",
    20: "h:mm",
    21: "h:mm:ss",
    22: "m/d/yy h:mm",
    37: "#,##0 ;(#,##0)",
    38: "#,##0 ;[Red](#,##0)",
    39: "#,##0.00;(#,##0.00)",
    40: "#,##0.00;[Red](#,##0.00)",
    45: "mm:ss",
    46: "[h]:mm:ss",
    47: "mmss.0",
    48: "##0.0E+0",
    49: "@",
}

GENERAL_FORMAT = "General"

# What a format code MEANS, which is what decides a cell's type in every
# reader the study measured. A date is a number wearing a format, so the
# kind of format is the only thing that says so.
FORMAT_PLAIN = dialect.SHEET_FORMAT_PLAIN
FORMAT_DATE = dialect.SHEET_FORMAT_DATE
FORMAT_DATETIME = dialect.SHEET_FORMAT_DATETIME
FORMAT_TIME = dialect.SHEET_FORMAT_TIME
FORMAT_ELAPSED = dialect.SHEET_FORMAT_ELAPSED
FORMAT_TEXT = dialect.SHEET_FORMAT_TEXT
FORMAT_KINDS = dialect.SHEET_FORMAT_KINDS


@dataclasses.dataclass(frozen=True, slots=True)
class Cell:
    """One cell, exactly as the file holds it.

    WHY THIS ONE CARRIES SLOTS AND THE OTHERS DO NOT (repair of landing
    2b.10). A sheet holds one of these per cell and nothing else in this
    package is allocated a million times, so the per-instance dictionary
    an ordinary object carries is the whole of the reader's memory cost
    at the caps. Removing it is what let the cell cap be set from a
    measurement rather than from hope; the figures are in the caps'
    own comment above.

    ``text`` is the cell's own characters for text, the stored number's
    own spelling for a number, the kind for an error and the word for a
    boolean. ``formula`` says the cell carries one, and ``cached`` says
    whether a value was stored beside it -- the pair the study found the
    readers disagreeing about, since a formula with no cache reads as a
    missing value everywhere but in a spreadsheet application.
    """

    row: int
    column: int
    kind: str
    text: str
    number_format: str
    formula: bool
    cached: bool


# THE NOISE A WRITER LEAVES IN A STORED NUMBER (plan P4-D170). A workbook
# stores a number as the text of a binary64, and the writers do not agree
# on how many figures that text carries: openpyxl writes sixteen
# significant figures and Excel seventeen, so the value typed as 73.1 is
# stored `73.09999999999999` or `73.099999999999994` -- the SAME binary64
# as `73.1`, which is what every reader hands back. The column machinery
# read those figures as the cell's spelling, published a fraction width
# of fourteen beside a width of one, and the person's own unchanged
# workbook then failed `styles.spelled` against its own description.
# Such a text is read as the shortest spelling of the same value, in the
# same notation. Nothing a person could mean is moved: the shorter text
# is the very number stored, and a text of fewer than sixteen figures,
# or with no shorter spelling of its value, is kept as the file holds it.
NOISY_FIGURES = 16


def stored_number(text: str) -> str:
    """A stored number's text, read as the shortest spelling of its value.

    Guarantees: a fixed function of the text; raises nothing but the
    type check. Returns the text unchanged unless it holds a point or an
    exponent, carries at least `NOISY_FIGURES` significant figures, and
    a shorter text in the same notation reads back as exactly the same
    binary64. A whole number with no point is never rewritten: every
    reader reads it as a whole number, whatever its length.
    """
    if not isinstance(text, str):
        raise TypeError("internal check: a stored number was not text")
    body = text
    if body[:1] in ("-", "+"):
        body = body[1:]
    mantissa = body
    mark = ""
    exponent = ""
    place = mantissa.find("e")
    if place < 0:
        place = mantissa.find("E")
    if place >= 0:
        mark = mantissa[place]
        exponent = mantissa[place + 1 :]
        mantissa = mantissa[:place]
    point = mantissa.find(".")
    if point < 0 and not mark:
        return text
    figures = mantissa
    if point >= 0:
        figures = mantissa[:point] + mantissa[point + 1 :]
    if not figures or not _all_figures(figures):
        return text
    # A TRAILING NOUGHT IS PADDING, NEVER NOISE: a writer's sixteen or
    # seventeen figures are the shortest-of-that-many spelling, which
    # never ends in a nought after the point, while a fraction padded to
    # a width -- synthtwin's own twin writes `45353.39257371100` for a
    # published width of eleven -- does, and is kept.
    if point >= 0 and mantissa[len(mantissa) - 1 :] == "0":
        return text
    leading = 0
    while leading < len(figures) and figures[leading] == "0":
        leading = leading + 1
    if len(figures) - leading < NOISY_FIGURES:
        return text
    try:
        value = float(text)
    except ValueError:
        return text
    if value != value or value in (float("inf"), float("-inf")):
        return text
    shortest = ""
    if not mark:
        for precision in range(1, 18):
            candidate = f"{value:.{precision}g}"
            if float(candidate) == value:
                shortest = candidate
                break
        if not shortest or "e" in shortest:
            return text
    else:
        for precision in range(0, 17):
            candidate = f"{value:.{precision}e}"
            if float(candidate) == value:
                shortest = _in_the_exponent_of(candidate, mark, exponent)
                break
    if not shortest or len(shortest) >= len(text) or float(shortest) != value:
        return text
    if text[:1] == "+" and shortest[:1] != "-":
        shortest = "+" + shortest
    return shortest


def _in_the_exponent_of(candidate: str, mark: str, exponent: str) -> str:
    """A `1.5e-05` spelling rewritten with the source's exponent letter and width."""
    if not isinstance(candidate, str):
        raise TypeError("internal check: an exponent spelling was not text")
    if not isinstance(exponent, str):
        raise TypeError("internal check: an exponent spelling was not text")
    place = candidate.find("e")
    if place < 0:
        return ""
    head = candidate[:place]
    power = candidate[place + 1 :]
    negative = power[:1] == "-"
    if power[:1] in ("-", "+"):
        power = power[1:]
    while len(power) > 1 and power[:1] == "0":
        power = power[1:]
    width = exponent
    if width[:1] in ("-", "+"):
        width = width[1:]
    while len(power) < len(width):
        power = "0" + power
    sign = "-" if negative else ("+" if exponent[:1] == "+" else "")
    return f"{head}{mark}{sign}{power}"


def _marked(marks: "dict[str, str]", key: str, fallback: str) -> str:
    """One attribute of an element, or ``fallback`` where it has none.

    The offline audit refuses `.get` on a value it cannot trace, and an
    element's marks come from the parser, so the lookup is written out.
    """
    if key in marks:
        found = marks[key]
        if isinstance(found, str):
            return found
    return fallback


def _all_figures(text: str) -> bool:
    """Whether every character is an ASCII digit, and there is one.

    Written with ordinals rather than `isdigit`: the offline audit
    traces a method call on a gated parameter and not on text this
    module built character by character, and `isdigit` is true of
    figures in other writing systems that `int` then refuses.
    """
    if not isinstance(text, str):
        raise TypeError("internal check: a number's spelling was not text")
    if not text:
        return False
    for character in text:
        place = ord(character)
        if place < 48 or place > 57:
            return False
    return True


def _whole_number(text: str, fallback: int) -> int:
    """A whole number written in figures, or ``fallback``."""
    if not isinstance(text, str):
        raise TypeError("internal check: a number's spelling was not text")
    if not text:
        return fallback
    figures = text
    if text[:1] == "-":
        figures = text[1:]
    if not _all_figures(figures):
        return fallback
    return int(text)


def reference_column(reference: str) -> int:
    """The column a cell reference names, counting from one.

    `A1` is column 1 and `AB7` is column 28. A reference this cannot
    read yields 0, and the caller places the cell by its order instead.
    """
    if not isinstance(reference, str):
        raise TypeError("internal check: a cell reference was not text")
    number = 0
    for character in reference:
        place = ord(character)
        if 65 <= place <= 90:
            number = number * 26 + (place - 64)
            continue
        if 97 <= place <= 122:
            number = number * 26 + (place - 96)
            continue
        break
    return number


def reference_row(reference: str) -> int:
    """The row a cell reference names, counting from one, or 0."""
    if not isinstance(reference, str):
        raise TypeError("internal check: a cell reference was not text")
    figures = ""
    for character in reference:
        place = ord(character)
        if 48 <= place <= 57:
            figures = figures + character
    return _whole_number(figures, 0)


def _is_elapsed_token(inside: str) -> bool:
    """Whether a bracket's text is an elapsed count: `h`, `mm`, `ss`...

    One letter of hours, minutes or seconds, repeated, in either case.
    Compared character by character, so no text method is called on
    text this module built.
    """
    if not inside:
        return False
    first = inside[0]
    if first not in ("h", "H", "m", "M", "s", "S"):
        return False
    for character in inside:
        if character != first:
            return False
    return True


def format_kind(code: str) -> str:
    """Which kind of thing a number wearing this format code is.

    Guarantees: a fixed function of the code. The rule is the one every
    reader the study measured uses -- the format decides the type -- and
    it reads the code outside its quoted runs, so a currency symbol
    spelling `"d"` inside quotation marks never makes a column of money
    into a column of dates.
    """
    if not isinstance(code, str):
        raise TypeError("internal check: a format code was not text")
    if code == GENERAL_FORMAT or not code:
        return FORMAT_PLAIN
    if code == "@":
        return FORMAT_TEXT
    # The first section only: a format may spell positives, negatives
    # and zeros differently, and the first section is the one a positive
    # number wears.
    body = code.split(";")[0]
    plain = ""
    quoted = False
    skip = False
    # WHAT A BRACKET HOLDS IS NOT READ AS A DATE (plan P4-D165). A colour
    # (`[Red]`), a currency and locale (`[$USD-409]`) and a condition
    # (`[>=100]`) each sit in square brackets, and the letters inside
    # them are not day, month or hour tokens: sixty values `101.25` to
    # `160.25` formatted `[Red]0.00` were classed as DATES by the `d` of
    # `Red`, and the twin came back as datetimes while pandas read floats
    # from the source. The one bracket that IS a token is an elapsed
    # count -- `[h]`, `[mm]`, `[ss]` -- which is kept, as its letters.
    # The character after `_` (a space as wide as it) and after `*` (a
    # fill) is layout, never a token, and is skipped the same way.
    bracket = ""
    in_bracket = False
    elapsed = False
    for character in body:
        if skip:
            skip = False
            continue
        if in_bracket:
            if character == "]":
                in_bracket = False
                if _is_elapsed_token(bracket):
                    elapsed = True
                continue
            bracket = bracket + character
            continue
        if character == "\\" or character == "_" or character == "*":
            skip = True
            continue
        if character == '"':
            quoted = not quoted
            continue
        if quoted:
            continue
        if character == "[":
            in_bracket = True
            bracket = ""
            continue
        plain = plain + character
    # Both cases are tested rather than folding the text: the offline
    # audit traces a method call on a gated parameter and not on text
    # this function built character by character.
    day = "d" in plain or "D" in plain or "y" in plain or "Y" in plain
    # `m` is minutes next to an hour or a second, and months otherwise.
    month = "m" in plain or "M" in plain
    clock = "h" in plain or "H" in plain or "s" in plain or "S" in plain
    if elapsed:
        return FORMAT_ELAPSED
    if day and clock:
        return FORMAT_DATETIME
    if day or (month and not clock):
        return FORMAT_DATE
    if clock:
        return FORMAT_TIME
    return FORMAT_PLAIN


# -- the parts of a workbook -------------------------------------------


@dataclasses.dataclass(frozen=True)
class SheetEntry:
    """One sheet the workbook declares, in workbook order."""

    name: str
    state: str
    part: str


@dataclasses.dataclass(frozen=True)
class Reading:
    """One sheet of one workbook, read.

    ``cells`` holds every cell the sheet carries, in row-major order.
    ``sheets`` names every sheet the workbook declares so the person can
    be told what was chosen and what else was there.
    """

    cells: "tuple[Cell, ...]"
    sheets: "tuple[SheetEntry, ...]"
    # ONE ENTRY PER SHEET, in workbook order: the block of cells a sheet
    # that is NOT the table's holds, as (rows, columns) counted from A1,
    # and None for the sheet the table was read from, whose own facts
    # describe it (plan P4-D82). A sheet holding nothing is (0, 0).
    sheet_extents: "tuple[tuple[int, int] | None, ...]"
    chosen: str
    chosen_hidden: bool
    epoch_1904: bool
    has_macro_project: bool
    frozen_rows: int
    autofilter: str
    table_names: "tuple[str, ...]"
    defined_names: int
    last_row: int
    last_column: int


def _extent_of(cells: "tuple[Cell, ...]") -> "tuple[int, int]":
    """The block of cells a sheet holds: how many rows and columns, from A1.

    Counted over the cells that HOLD something, because that is what a
    reader's frame spans: a styled blank and an absent cell are nothing
    to every reader the study measured, and a sheet of them reads back
    as no table at all.
    """
    rows = 0
    columns = 0
    for cell in cells:
        if cell.kind in (CELL_ABSENT, CELL_BLANK):
            continue
        if cell.row > rows:
            rows = cell.row
        if cell.column > columns:
            columns = cell.column
    return (rows, columns)


def _is_table_part(name: str) -> bool:
    """Whether a member name is one of the workbook's defined tables."""
    if not isinstance(name, str):
        raise TypeError("internal check: a part's name was not text")
    return name.startswith("xl/tables/")


def _part_named(parts: "dict[str, bytes]", name: str) -> bytes:
    """One member's bytes, or nothing where the package has no such part."""
    if name in parts:
        return parts[name]
    return b""


def shared_strings(parts: "dict[str, bytes]", shown: str) -> "tuple[str, ...]":
    """The workbook's table of stored text, in its own order.

    A shared string may be split into runs by its formatting -- the
    study's rich-text case -- and every reader joins the runs and drops
    the formatting, so the runs are joined here and the formatting is
    not carried: it marks part of one cell's text, which is a fact about
    one row and not about the table.

    A PHONETIC RUN IS NOT PART OF THE VALUE (plan P4-D163). A string may
    carry `<rPh>` runs -- the reading of its characters, which a
    spreadsheet shows above them -- and each holds a `<t>` of its own.
    The first writing collected every `<t>`, so a cell whose visible
    text is `alpha` and whose reading is `READING` was read as
    `alphaREADING`, which is not what pandas or openpyxl hand back, and
    the twin carried the joined word. Text inside a phonetic run is
    passed over.
    """
    data = _part_named(parts, "xl/sharedStrings.xml")
    if not data:
        return ()
    walk = _StringWalk([], "", False, 0, 0)

    def declared(
        name: str, system: "str | None", public: "str | None", internal: int
    ) -> None:
        walk.stopped = 1
        raise ValueError("a document type declaration is not read")

    def started(name: str, marks: "dict[str, str]") -> None:
        local = _after_colon(name)
        if local == "si":
            walk.pending = ""
        if local == "rPh":
            walk.phonetic = walk.phonetic + 1
        if local == "t" and not walk.phonetic:
            walk.inside = True

    def ended(name: str) -> None:
        local = _after_colon(name)
        if local == "t":
            walk.inside = False
            return
        if local == "rPh":
            if walk.phonetic:
                walk.phonetic = walk.phonetic - 1
            return
        if local == "si":
            walk.items += [walk.pending]
            walk.pending = ""
            if len(walk.items) > MAXIMUM_SHARED_STRINGS:
                walk.stopped = 2
                raise ValueError("the stored text is past its cap")

    def texted(piece: str) -> None:
        if not walk.inside:
            return
        grown = walk.pending + piece
        if len(grown) > MAXIMUM_CELL_CHARACTERS:
            walk.stopped = 3
            raise ValueError("a cell's text is past its cap")
        walk.pending = grown

    parser = xml.parsers.expat.ParserCreate()
    parser.StartDoctypeDeclHandler = declared
    parser.StartElementHandler = started
    parser.EndElementHandler = ended
    parser.CharacterDataHandler = texted
    parser.buffer_text = True
    try:
        parser.Parse(data, True)
    except ValueError as error:
        if walk.stopped == 1:
            raise errors.ProfileError(
                errors.workbook_declares_a_document_type(shown)
            ) from error
        if walk.stopped == 2:
            raise errors.ProfileError(
                errors.workbook_too_many_shared_strings(
                    shown, MAXIMUM_SHARED_STRINGS
                )
            ) from error
        raise errors.ProfileError(
            errors.workbook_cell_too_long(shown, MAXIMUM_CELL_CHARACTERS)
        ) from error
    except xml.parsers.expat.ExpatError as error:
        raise errors.ProfileError(
            errors.workbook_part_unreadable(shown)
        ) from error
    return tuple(walk.items)


def number_formats(parts: "dict[str, bytes]", shown: str) -> "tuple[str, ...]":
    """The format code of each cell style, by its place in the style table.

    The code and never the id, for the reason the study measured: Excel
    renumbers custom ids on every save and drops the unused ones, so two
    saves of one workbook name the same format by different numbers.
    """
    data = _part_named(parts, "xl/styles.xml")
    if not data:
        return ()
    found = elements(
        data, shown, ("numFmt", "cellStyleXfs", "cellXfs", "xf")
    )
    codes: "dict[int, str]" = {}
    styles: "list[str]" = []
    inside = False
    # A CELL'S STYLE NUMBER COUNTS INSIDE `cellXfs` ALONE, and a styles
    # part holds a second run of the same element: `cellStyleXfs`, the
    # NAMED styles, which a cell never points at. The parse hands each
    # element back as it CLOSES, so `cellStyleXfs` arrives once its own
    # children have -- and how many have arrived by then is exactly how
    # many belong to it. Counting them is what keeps `s="3"` meaning the
    # fourth cell style rather than the fourth element of the part; with
    # the two runs run together every format code on a workbook written
    # by Excel comes out shifted.
    named = 0
    for name, marks, _piece in found:
        if name == "numFmt":
            number = _whole_number(_marked(marks, "numFmtId", ""), -1)
            if number >= 0:
                codes[number] = _marked(marks, "formatCode", GENERAL_FORMAT)
            continue
        if name == "cellStyleXfs":
            named = len(styles)
            continue
        if name == "cellXfs":
            inside = True
            continue
        if name == "xf":
            styles += [_marked(marks, "numFmtId", "0")]
    if not inside:
        return ()
    styles = styles[named:]
    out: "list[str]" = []
    for held in styles:
        number = _whole_number(held, 0)
        if number in codes:
            out += [codes[number]]
            continue
        if number in BUILT_IN_FORMATS:
            out += [BUILT_IN_FORMATS[number]]
            continue
        out += [GENERAL_FORMAT]
    return tuple(out)


def _relationship_targets(
    parts: "dict[str, bytes]", shown: str
) -> "dict[str, str]":
    """Which part each of the workbook's relationships points at."""
    data = _part_named(parts, "xl/_rels/workbook.xml.rels")
    out: "dict[str, str]" = {}
    if not data:
        return out
    for _name, marks, _piece in elements(data, shown, ("Relationship",)):
        out[_marked(marks, "Id", "")] = _marked(marks, "Target", "")
    return out


def _inside_xl(target: str) -> str:
    """A relationship target as a member name of the package."""
    if not isinstance(target, str):
        raise TypeError("internal check: a part's target was not text")
    if target.startswith("/"):
        return target[1:]
    if target.startswith("xl/"):
        return target
    return "xl/" + target


def workbook_parts(
    parts: "dict[str, bytes]", shown: str
) -> "tuple[tuple[SheetEntry, ...], bool, int]":
    """The sheets the workbook declares, its date system and its names."""
    data = _part_named(parts, "xl/workbook.xml")
    if not data:
        raise errors.ProfileError(errors.workbook_unreadable(shown))
    found = elements(data, shown, ("sheet", "workbookPr", "definedName"))
    targets = _relationship_targets(parts, shown)
    sheets: "list[SheetEntry]" = []
    epoch = False
    names = 0
    for name, marks, _piece in found:
        if name == "workbookPr":
            epoch = _marked(marks, "date1904", "0") in ("1", "true")
            continue
        if name == "definedName":
            names = names + 1
            continue
        relation = _marked(marks, "r:id", _marked(marks, "id", ""))
        part = ""
        if relation in targets:
            part = _inside_xl(targets[relation])
        sheets += [
            SheetEntry(
                name=_marked(marks, "name", ""),
                state=_marked(marks, "state", "visible"),
                part=part,
            )
        ]
    return (tuple(sheets), epoch, names)


def chosen_sheet(
    sheets: "tuple[SheetEntry, ...]",
    wanted: str,
    shown: str,
    positions: bool = False,
) -> SheetEntry:
    """Which sheet the table is on: the one named, else the first visible.

    THE FIRST VISIBLE SHEET, WHICH IS NOT WHAT THE READERS DO, and the
    difference is deliberate and published. pandas and readxl both take
    the first sheet in workbook order even when it is hidden; the study
    measured a workbook whose hidden first sheet made pandas read a
    one-column table of nothing. A hidden sheet is one the person put
    out of the way, so synthtwin passes over it and SAYS which sheet it
    settled on.
    """
    if wanted:
        for entry in sheets:
            if entry.name == wanted:
                return entry
        if positions:
            raise errors.ProfileError(
                errors.checked_workbook_sheet_not_found(shown, len(sheets))
            )
        known: "list[str]" = []
        for entry in sheets:
            known += [entry.name]
        raise errors.ProfileError(
            errors.workbook_sheet_not_found(shown, wanted, known)
        )
    for entry in sheets:
        if entry.state == "visible" and entry.part:
            return entry
    raise errors.ProfileError(errors.workbook_has_no_sheet(shown))


def refuse_by_kind(kind: str, shown: str) -> None:
    """Refuse a file whose opening bytes are not a workbook package.

    The two kinds a person actually meets, told apart because the
    remedy differs: a compound file is a legacy or password-protected
    workbook, and markup is the HTML many systems export under a
    spreadsheet's name. Neither is read.
    """
    if kind == KIND_COMPOUND:
        raise errors.ProfileError(errors.workbook_is_a_compound_file(shown))
    if kind == KIND_MARKUP:
        raise errors.ProfileError(errors.workbook_is_markup(shown))


def sheet_cells(
    data: bytes, shown: str, strings: "tuple[str, ...]",
    formats: "tuple[str, ...]",
) -> "tuple[tuple[Cell, ...], int, int, int, str, bool]":
    """Every cell of one sheet, with the sheet's own cheap facts.

    Returns the cells, the last row and column any cell stands in, how
    many rows are frozen at the top, the autofilter's range, and whether
    the sheet carries a defined table.

    Guarantees:

    - Determinism: a fixed function of the part's bytes, the stored text
      and the style table.
    - Memory: bounded by the CELLS the sheet holds and not by its size.
      The walk keeps no element of the document, which is what lets a
      sheet of a million rows be read without holding the million
      element records that the first writing of this module kept.
    - Errors raised: ProfileError for a document type declaration, for
      markup this cannot read, for a cell's text past its cap, and for
      each of the row, column and cell caps by name.
    - Boundary: nothing is opened, nothing is fetched, no formula is
      evaluated. A formula cell yields its CACHED value and the record
      that a cache existed; the formula's own text is never carried,
      because it is cross-column structure this version does not model
      and it can hold constants out of other rows.
    """
    walk = _CellWalk(
        [], strings, formats, "", "", 0, "", "", False, False, False,
        False, 0, 0, 0, "", False, 0, False, 0,
    )

    def declared(
        name: str, system: "str | None", public: "str | None", internal: int
    ) -> None:
        walk.stopped = 1
        raise ValueError("a document type declaration is not read")

    def started(name: str, marks: "dict[str, str]") -> None:
        local = _after_colon(name)
        if local == "c":
            walk.reference = _marked(marks, "r", "")
            walk.marked_kind = _marked(marks, "t", "n")
            walk.style = _whole_number(_marked(marks, "s", "0"), 0)
            walk.value = ""
            walk.inline = ""
            walk.formula = False
            walk.cached = False
            return
        if local == "v":
            walk.in_value = True
            walk.value = ""
            return
        if local == "f":
            walk.formula = True
            return
        if local == "is":
            walk.in_inline = True
            walk.inline = ""
            return
        if local == "rPh" and walk.in_inline:
            walk.phonetic = walk.phonetic + 1
            return
        if local == "t" and walk.in_inline:
            walk.in_text = not walk.phonetic
            return
        if local == "row":
            number = _whole_number(_marked(marks, "r", "0"), 0)
            if number > MAXIMUM_ROWS:
                walk.stopped = 4
                raise ValueError("a row past the last a spreadsheet has")
            if number > walk.last_row:
                walk.last_row = number
            return
        if local == "pane":
            # A SPLIT IS NOT A FREEZE (plan P4-D165). `ySplit` counts ROWS
            # only on a frozen pane; on a split pane it is a distance in
            # twentieths of a point, and a split at `3000` was published as
            # three thousand frozen rows -- which the loader then refused
            # as an edited description, so a real workbook's own
            # description would not load.
            state = _marked(marks, "state", "split")
            if state in ("frozen", "frozenSplit"):
                walk.frozen = _whole_number(_marked(marks, "ySplit", "0"), 0)
            return
        if local == "autoFilter":
            walk.filtered = _marked(marks, "ref", "")
            return
        if local == "tablePart":
            walk.tabled = True

    def texted(piece: str) -> None:
        if walk.in_value:
            grown = walk.value + piece
            if len(grown) > MAXIMUM_CELL_CHARACTERS:
                walk.stopped = 3
                raise ValueError("a cell's text is past its cap")
            walk.value = grown
            return
        # ONLY THE TEXT RUNS OF AN INLINE STRING ARE ITS VALUE (plan
        # P4-D163). The first writing took every character inside `<is>`,
        # so the indentation a writer puts between elements -- `<is>\n
        # <t>North</t>\n </is>` -- became part of the cell, and so did a
        # phonetic run's reading.
        if walk.in_inline and walk.in_text:
            grown = walk.inline + piece
            if len(grown) > MAXIMUM_CELL_CHARACTERS:
                walk.stopped = 3
                raise ValueError("a cell's text is past its cap")
            walk.inline = grown

    def ended(name: str) -> None:
        local = _after_colon(name)
        if local == "v":
            walk.in_value = False
            walk.cached = True
            return
        if local == "is":
            walk.in_inline = False
            walk.in_text = False
            walk.phonetic = 0
            return
        if local == "t" and walk.in_inline:
            walk.in_text = False
            return
        if local == "rPh" and walk.in_inline:
            if walk.phonetic:
                walk.phonetic = walk.phonetic - 1
            return
        if local != "c":
            return
        column = reference_column(walk.reference)
        row = reference_row(walk.reference)
        if column > MAXIMUM_COLUMNS:
            walk.stopped = 5
            raise ValueError("a column past the last a spreadsheet has")
        if row > MAXIMUM_ROWS:
            walk.stopped = 4
            raise ValueError("a row past the last a spreadsheet has")
        code = GENERAL_FORMAT
        if 0 <= walk.style < len(walk.formats):
            code = walk.formats[walk.style]
        kind = CELL_NUMBER
        held = stored_number(walk.value)
        if walk.marked_kind == "s":
            kind = CELL_TEXT
            place = _whole_number(walk.value, -1)
            held = ""
            if 0 <= place < len(walk.strings):
                held = walk.strings[place]
        elif walk.marked_kind == "inlineStr":
            kind = CELL_TEXT
            held = walk.inline
        elif walk.marked_kind == "str":
            kind = CELL_TEXT
            held = walk.value
        elif walk.marked_kind == "b":
            kind = CELL_BOOLEAN
            held = BOOLEAN_TRUE if walk.value == "1" else BOOLEAN_FALSE
        elif walk.marked_kind == "e":
            kind = CELL_ERROR
            held = walk.value
        elif walk.marked_kind == "d":
            # A DATE STORED AS ITS ISO TEXT (plan P4-D164). It is its own
            # class, spelled as the text the file holds, so the column
            # machinery reads a column of dates and the twin writes the
            # cell back the way the file did. It used to fall through to
            # the number class here.
            kind = CELL_DATE
            held = walk.value
        # A CELL PRESENT WITH NO VALUE AT ALL IS NOT AN EMPTY STRING.
        # Excel writes a styled blank as `<c r="A6" s="9"/>`, and the
        # study found every reader folding that, the empty-string cell
        # and the absent cell into one missing value. They are three
        # different things in the file and the twin has to write back
        # the one it was given.
        if not walk.cached and not walk.in_inline and not walk.inline:
            if kind in (CELL_NUMBER, CELL_TEXT, CELL_DATE):
                kind = CELL_BLANK
                held = ""
        elif kind == CELL_TEXT and not held:
            kind = CELL_EMPTY
        if row > walk.last_row:
            walk.last_row = row
        if column > walk.last_column:
            walk.last_column = column
        walk.cells += [
            Cell(
                row=row,
                column=column,
                kind=kind,
                text=held,
                number_format=code,
                formula=walk.formula,
                cached=walk.cached,
            )
        ]
        if len(walk.cells) > MAXIMUM_CELLS:
            walk.stopped = 6
            raise ValueError("more cells than the walk will read")
        walk.value = ""
        walk.inline = ""
        walk.formula = False
        walk.cached = False

    parser = xml.parsers.expat.ParserCreate()
    parser.StartDoctypeDeclHandler = declared
    parser.StartElementHandler = started
    parser.EndElementHandler = ended
    parser.CharacterDataHandler = texted
    parser.buffer_text = True
    try:
        parser.Parse(data, True)
    except ValueError as error:
        if walk.stopped == 1:
            raise errors.ProfileError(
                errors.workbook_declares_a_document_type(shown)
            ) from error
        if walk.stopped == 4:
            raise errors.ProfileError(
                errors.workbook_too_many_rows(shown, MAXIMUM_ROWS)
            ) from error
        if walk.stopped == 5:
            raise errors.ProfileError(
                errors.workbook_too_many_columns(shown, MAXIMUM_COLUMNS)
            ) from error
        if walk.stopped == 6:
            raise errors.ProfileError(
                errors.workbook_holds_too_many_cells(shown, MAXIMUM_CELLS)
            ) from error
        raise errors.ProfileError(
            errors.workbook_cell_too_long(shown, MAXIMUM_CELL_CHARACTERS)
        ) from error
    except xml.parsers.expat.ExpatError as error:
        raise errors.ProfileError(
            errors.workbook_part_unreadable(shown)
        ) from error
    return (
        tuple(walk.cells), walk.last_row, walk.last_column, walk.frozen,
        walk.filtered, walk.tabled,
    )


def _refuse_empty_sheet(
    shown: str, name: str, position: int, positions: bool
) -> None:
    """Refuse a chosen sheet holding nothing, by name or by position."""
    if positions:
        raise errors.ProfileError(
            errors.checked_workbook_sheet_is_empty(shown, position)
        )
    raise errors.ProfileError(errors.workbook_sheet_is_empty(shown, name))


def read_parts(
    parts: "dict[str, bytes]",
    shown: str,
    wanted: str = "",
    positions: bool = False,
) -> Reading:
    """Read one sheet of a workbook: its cells and the facts about it.

    Guarantees:

    - Inputs: the package's members already expanded (`reading.
      opened_workbook` does that, under every cap), the path as the
      person wrote it, and the sheet they named with `--sheet`, or
      nothing to settle it by the rule in `chosen_sheet`.
    - Determinism: a fixed function of those members and the name.
    - Errors raised: ProfileError for every refusal this module names.
    - Boundary: opens nothing, writes nothing, never evaluates a
      formula, never follows a link, and never reads a macro project.
    - Refusals: where ``positions`` is set -- the validate path, which
      measures a file nobody promised was the reader's own (V9) -- every
      refusal here names a sheet by its POSITION and never by its name,
      because a sheet's name is text out of that file (plan P4-D166).
    """
    has_macro = False
    for name in sorted(parts):
        if name == "xl/vbaProject.bin":
            has_macro = True
    strings = shared_strings(parts, shown)
    formats = number_formats(parts, shown)
    sheets, epoch, names = workbook_parts(parts, shown)
    entry = chosen_sheet(sheets, wanted, shown, positions)
    chosen_position = 0
    for index in range(len(sheets)):
        if sheets[index] is entry:
            chosen_position = index + 1
    data = _part_named(parts, entry.part)
    if not data:
        _refuse_empty_sheet(shown, entry.name, chosen_position, positions)
    cells, last_row, last_column, frozen, filtered, tabled = sheet_cells(
        data, shown, strings, formats
    )
    if not cells:
        _refuse_empty_sheet(shown, entry.name, chosen_position, positions)
    # WHAT EVERY OTHER SHEET HOLDS, AND THE ONE SHAPE THAT IS REFUSED
    # (plan P4-D82). A workbook's other sheets used to be written EMPTY,
    # so a reader met a different workbook: measured with pandas, the
    # default sheet of a hidden-first book reads as one column and no
    # rows on the real file and as nothing at all on the twin. The block
    # of cells each such sheet holds is published and written back with
    # synthtwin's own word in every cell, which is the most a twin may
    # carry of a sheet this description does not describe.
    #
    # A sheet holding a TABLE cannot be carried that way at all, and is
    # refused rather than quietly emptied: its values are somebody's
    # rows, so the twin would hand a reader a frame of withheld cells
    # where a table stood, and statistics taken from it would be false
    # while the file still opened. The person is asked which sheet is
    # the table instead.
    #
    # A TABLE ONE COLUMN WIDE IS A TABLE (plan P4-D166). The first
    # writing refused a block only where it reached two rows AND two
    # columns, so a sheet holding a header `site` over thirty values was
    # accepted and every one of its cells written back as the withheld
    # word, while validation missed nothing -- a worse outcome than the
    # refusal a wider table met. Any block of two rows or more is
    # records, whatever its width, and is refused the same way; a block
    # of one row -- a title, a note -- is still carried by its shape.
    extents: "list[tuple[int, int] | None]" = []
    for index in range(len(sheets)):
        other = sheets[index]
        if other is entry:
            extents += [None]
            continue
        page = _part_named(parts, other.part)
        if not page:
            extents += [(0, 0)]
            continue
        other_cells = sheet_cells(page, shown, strings, formats)[0]
        rows, columns = _extent_of(other_cells)
        if rows >= 2:
            if positions:
                raise errors.ProfileError(
                    errors.checked_workbook_other_sheet_holds_a_table(
                        shown, index + 1, chosen_position
                    )
                )
            raise errors.ProfileError(
                errors.workbook_other_sheet_holds_a_table(
                    shown, other.name, entry.name
                )
            )
        extents += [(rows, columns)]
    tables: "list[str]" = []
    if tabled:
        for name in sorted(parts):
            if _is_table_part(name):
                for held, marks, _piece in elements(
                    parts[name], shown, ("table", "autoFilter")
                ):
                    if held == "autoFilter":
                        # A defined table keeps its filter in its own
                        # part rather than in the sheet, which is where
                        # the study's Excel-shaped book puts it.
                        if not filtered:
                            filtered = _marked(marks, "ref", "")
                        continue
                    tables += [_marked(marks, "displayName",
                                       _marked(marks, "name", ""))]
    return Reading(
        cells=cells,
        sheets=sheets,
        sheet_extents=tuple(extents),
        chosen=entry.name,
        chosen_hidden=entry.state != "visible",
        epoch_1904=epoch,
        has_macro_project=has_macro,
        frozen_rows=frozen,
        autofilter=filtered,
        table_names=tuple(tables),
        defined_names=names,
        last_row=last_row,
        last_column=last_column,
    )


# -- from cells to a table --------------------------------------------
#
# THE SPELLING RULE IS THE SEAM. Every column path in this package reads
# TEXT, because a delimited file's cells are text and nothing else. A
# workbook's cells are not, so each class is written as one piece of
# text here, once, and the description publishes which class each cell
# came from beside the count. That is what lets the existing column
# machinery read a workbook column without knowing it is one, and what
# lets the twin write back the class it was given rather than whatever
# a reader would have made of the text.


def spelled(kind: str, text: str) -> str:
    """One cell as the column machinery reads it.

    A cell holding nothing -- absent, or present with no value at all --
    spells as the empty text, which is what an absent cell is in a
    delimited file. The two are told apart by the published census and
    not by the spelling, because no spelling could tell them apart and
    still be read back as the same value.
    """
    if not isinstance(kind, str) or not isinstance(text, str):
        raise TypeError("internal check: a cell's class or text was not text")
    if kind in (CELL_ABSENT, CELL_BLANK):
        return ""
    return text


@dataclasses.dataclass(frozen=True)
class Sheet:
    """One sheet read as a table, with the facts about how it sits.

    ``columns`` and ``classes`` hold one list per column, column-major
    and the same length, so a column's cells and what each cell WAS are
    read together.
    """

    names: "tuple[str, ...]"
    header_cells: "tuple[str, ...]"
    columns: "list[list[str]]"
    classes: "list[list[str]]"
    formats: "list[list[str]]"
    formulas: "list[list[bool]]"
    n_rows: int
    header_row: int
    rows_above: int
    empty_rows_inside: int
    trailing_blank_rows: int
    trailing_blank_columns: int
    # WHICH ROW HOLDS THE NAMES IS NOT SETTLED (plan P4-D170): the header
    # rule stepped over rows of one cell that nothing in the sheet marks
    # as furniture, so those rows may be the names themselves. The
    # profile path asks; see `_header_unsettled`.
    header_unsettled: bool = False


def _table_width(widths: "list[int]") -> int:
    """How wide the table is: the widest row of content it holds.

    THE WIDEST AND NOT THE COMMONEST, and the difference is a defect
    this rule was measured into. A data row may leave cells out -- an
    absent value, a formatted blank -- so the width most rows share can
    be NARROWER than the table; the study's Excel-shaped book has a
    28-cell header over data rows of 27, where the commonest width is
    27 and picking it stepped over the header and named the columns out
    of a record. No row can be WIDER than the set of columns the table
    has, so the widest row is the table's width, and a row above the
    table -- a title, a banner -- is narrower and is passed over.
    """
    widest = 0
    for width in widths:
        if width > widest:
            widest = width
    return widest


def _header_row_of(
    held: "dict[int, dict[int, Cell]]",
    content_rows: "list[int]",
    widths: "list[int]",
    wanted: int,
    first_column: int,
) -> int:
    """Which row of content holds the names (plan P4-D161).

    THE FIRST ROW HOLDING TWO CELLS OR MORE, AND NOT THE FIRST ROW
    REACHING THE WIDEST. The first writing took the first row as wide as
    the widest row, which is right for a title of one cell above a table
    of four -- and wrong for a header that leaves one of its own cells
    blank. Measured: a header `record_key`, blank, `arm` over thirty-one
    records is two cells wide against records of three, so the header
    was stepped over, the FIRST RECORD became the column names --
    `CASE-ZEBRA-471`, `37`, `amber`, one person's whole row published as
    names -- and the table lost that record. A title, a banner or a note
    above a table is ONE cell; a header of a table two or more columns
    wide is two or more, whichever of its cells are blank. So the header
    is the first row of content holding two cells, or the first reaching
    the table's width where the table is one column wide, or the written
    row index -- a header one narrower than the table whose missing cell
    is the first -- where the table is two wide.
    """
    for index in range(len(content_rows)):
        number = content_rows[index]
        if widths[index] >= 2 or widths[index] == wanted:
            return number
        missing_corner = (
            widths[index] == wanted - 1
            and (
                first_column not in held[number]
                or held[number][first_column].kind == CELL_BLANK
            )
        )
        if missing_corner:
            return number
    return content_rows[0]


def _first_row_of(reference: str) -> int:
    """The first row a range such as `A4:D200` names, or 0."""
    if not isinstance(reference, str):
        raise TypeError("internal check: a range was not text")
    place = reference.find(":")
    return reference_row(reference if place < 0 else reference[:place])


def _header_unsettled(
    reading: Reading, content_rows: "list[int]", header_row: int
) -> bool:
    """Whether the rows the header rule stepped over may be the names.

    THE HEADER RULE CANNOT TELL A TITLE FROM A HEADER OF ONE NAME (plan
    P4-D170). A title above a table is one cell; so is a header that
    names one column and leaves the others blank. Measured: `subject` in
    `A1`, `B1` and `C1` blank, over forty-one records of three texts --
    the rule stepped over row 1, the first RECORD became the names and
    was published whole, while pandas named the source's columns
    `subject`, `Unnamed: 1`, `Unnamed: 2`. Nothing in the values can
    settle it: a record of three texts looks like names. What CAN is
    what the sheet says of itself, each a thing a person does to a
    header and never to a record: the rows frozen at the top end at that
    row, or the autofilter -- a defined table's included -- begins at it.

    ONLY WHAT A TWIN CARRIES COUNTS. A merged banner says the same, and
    was measured as evidence and taken out again: the twin writes the
    rows above its header as cells holding nothing and merges nothing,
    so the twin of a book settled by its banner was not settled by
    anything and could not be described again. The frozen rows and the
    autofilter are published and written back.

    Where neither holds, the rows stepped over are not settled.
    Guarantees: a fixed function of the arguments; raises nothing.
    """
    stepped: "list[int]" = []
    for number in content_rows:
        if number < header_row:
            stepped += [number]
    if not stepped:
        return False
    if reading.frozen_rows == header_row:
        return False
    if reading.autofilter and _first_row_of(reading.autofilter) == header_row:
        return False
    return True


def table_of(
    reading: Reading,
    shown: str = "",
    records_from_the_top: bool = False,
    names_on_top: bool = False,
    published_header: int = 0,
) -> Sheet:
    """The table a sheet holds: its names, its cells and where it sits.

    THE HEADER IS FOUND BY WIDTH, and the rule is `_header_row_of`'s:
    rows a person puts above a table -- a title, a merged banner, a note
    -- hold one cell where a header of the table holds two or more.

    ``records_from_the_top`` is the person's `--first-row data` (plan
    P4-D161): no row holds names, every row from the sheet's first is a
    record, and the columns are named by the caller. The workbook branch
    of the reader used to drop that declaration, so a person who said
    their first row was a record still had it published as names.

    WHERE THE HEADER IS NOT SETTLED (`_header_unsettled`, plan P4-D170),
    ``names_on_top`` is the person's `--first-row names`: the first row
    of content holds the names, as every reader takes it. The validator
    passes ``published_header`` instead -- the row the description's
    `rows_above_header` puts the names on -- and it settles the reading
    where it is one of the two. Otherwise the header rule's row stands
    and the sheet says it is unsettled.

    THE COLUMNS START AT THE SHEET'S FIRST COLUMN (plan P4-D161). A table
    whose header begins in `C1` is three columns wide to every reader --
    pandas reads the two columns before it as columns holding nothing --
    and the first writing started the table at its first column of
    content, so its twin moved the table to `A1` and code that reached a
    column by its position reached a different one. The columns before
    the table's first content are columns of the table, holding nothing,
    as they are to the readers.

    Rows holding nothing INSIDE the table stay: every reader keeps them
    as a record of nothing, so the rows between the header and the last
    row of content are all counted whether the file writes them or not.
    Rows and columns of formatted blanks BELOW and BEYOND the table are
    not the table: the readers trim them, the sheet's own last row and
    column count them, and they are published as a fact of their own.

    Errors raised: ProfileError where the table's rectangle -- every
    place from its first row and column to its last, stored or not --
    passes `MAXIMUM_CELLS`. That is measured BEFORE any column is built,
    because a sheet storing two cells far apart used to pass the cap on
    stored cells and then build a table of a million.
    """
    held: "dict[int, dict[int, Cell]]" = {}
    for cell in reading.cells:
        if cell.row not in held:
            held[cell.row] = {}
        held[cell.row][cell.column] = cell
    content_rows: "list[int]" = []
    content_columns: "dict[int, bool]" = {}
    for number in sorted(held):
        filled = False
        for place in sorted(held[number]):
            if held[number][place].kind != CELL_BLANK:
                filled = True
                content_columns[place] = True
        if filled:
            content_rows += [number]
    if not content_rows or not content_columns:
        return Sheet((), (), [], [], [], [], 0, 0, 0, 0, 0, 0)
    places = sorted(content_columns)
    first_column = places[0] if places[0] < 1 else 1
    last_column = places[len(places) - 1]
    last_row = content_rows[len(content_rows) - 1]
    # Counted over the cells each row STORES, never over the span, so the
    # work here is bounded by the cells already read.
    widths: "list[int]" = []
    for number in content_rows:
        width = 0
        for place in held[number]:
            if place < first_column or place > last_column:
                continue
            if held[number][place].kind != CELL_BLANK:
                width = width + 1
        widths += [width]
    wanted = _table_width(widths)
    header_row = 0
    unsettled = False
    top = content_rows[0] if content_rows[0] < 1 else 1
    if not records_from_the_top:
        header_row = _header_row_of(
            held, content_rows, widths, wanted, first_column
        )
        unsettled = _header_unsettled(reading, content_rows, header_row)
        if unsettled and (
            names_on_top or published_header == content_rows[0]
        ):
            header_row = content_rows[0]
            unsettled = False
        elif unsettled and published_header == header_row:
            unsettled = False
        top = header_row + 1
    span = (last_row - top + 1) * (last_column - first_column + 1)
    if span > MAXIMUM_CELLS:
        raise errors.ProfileError(
            errors.workbook_table_spans_too_many_cells(shown, MAXIMUM_CELLS)
        )
    # EVERY ROW ABOVE THE HEADER, AND NOT ONLY THE ROWS OF CONTENT
    # (repair of landing 2b.10). The count published here is what the
    # twin writes above its own header, so a row the source had and
    # this count leaves out is a row the twin does not have. A blank row
    # between a title and the header is not content, and the twin came up
    # short by exactly those rows until the count was read off the
    # header's own row number: measured on the study's titled book,
    # pandas read 15 rows from the source and 13 from its twin. Where
    # every row is a record there is no header and nothing stands above.
    rows_above = header_row - 1 if header_row else 0
    header_cells: "list[str]" = []
    if header_row:
        for place in range(first_column, last_column + 1):
            if place in held[header_row]:
                entry = held[header_row][place]
                header_cells += [spelled(entry.kind, entry.text)]
                continue
            header_cells += [""]
    names = dialect.named_columns(tuple(header_cells))
    columns: "list[list[str]]" = []
    classes: "list[list[str]]" = []
    formats: "list[list[str]]" = []
    formulas: "list[list[bool]]" = []
    for _place in range(first_column, last_column + 1):
        columns += [[]]
        classes += [[]]
        formats += [[]]
        formulas += [[]]
    n_rows = 0
    empty_inside = 0
    for number in range(top, last_row + 1):
        n_rows = n_rows + 1
        holding = False
        for place in range(first_column, last_column + 1):
            index = place - first_column
            standing: "Cell | None" = None
            if number in held and place in held[number]:
                standing = held[number][place]
            if standing is None:
                columns[index] += [""]
                classes[index] += [CELL_ABSENT]
                formats[index] += [GENERAL_FORMAT]
                formulas[index] += [False]
                continue
            columns[index] += [spelled(standing.kind, standing.text)]
            classes[index] += [standing.kind]
            formats[index] += [standing.number_format]
            formulas[index] += [standing.formula]
            if standing.kind not in (CELL_ABSENT, CELL_BLANK):
                holding = True
        if not holding:
            empty_inside = empty_inside + 1
    trailing_rows = 0
    for number in sorted(held):
        if number > last_row:
            trailing_rows = trailing_rows + 1
    trailing_columns = 0
    counted: "dict[int, bool]" = {}
    for number in sorted(held):
        for place in sorted(held[number]):
            if place > last_column:
                counted[place] = True
    trailing_columns = len(counted)
    return Sheet(
        names=names,
        header_cells=tuple(header_cells),
        columns=columns,
        classes=classes,
        formats=formats,
        formulas=formulas,
        n_rows=n_rows,
        header_row=header_row,
        rows_above=rows_above,
        empty_rows_inside=empty_inside,
        trailing_blank_rows=trailing_rows,
        trailing_blank_columns=trailing_columns,
        header_unsettled=unsettled,
    )


# -- what the description publishes about a workbook -------------------
#
# WHAT IS NOT HERE IS THE POINT. The disclosure rule names the facts of
# a workbook that measure or name one person, and none of them is in
# this block: not the sheet's NAME (a sheet or a title can be somebody's
# name), not a column width (an autofit width measures the longest value
# in the column, so it is a measurement of one cell), not a comment or
# its author, not a hidden row, not per-row styling, not a hyperlink's
# target, not the document's author or company, and not any cache of
# real values. The sheet is published by its POSITION and the person is
# told on their own screen which sheet was read.
#
# WHICH COUNTS ARE HELD TO THE SMALLEST GROUP, AND WHICH ARE NOT, said
# exactly rather than in general (repair of landing 2b.10; the comment
# here read "every count" while five of them were published raw, a count
# of one among them).
#
# HELD, through `dialect.sheet_census` and `dialect.sheet_count`: every
# per-column census, each column's formulas and `empty_rows_inside`.
# What these count is ROWS OF THE TABLE -- a row per person, in most
# tables anyone brings here -- so a count of one names the row that holds
# it, a count one short of the whole names the row that does not, and a
# count withheld beside published ones names it again by subtraction
# (plan P4-D160). The rules are written once, in `dialect`, and contract
# WB3 is their executable form on the loader's side.
#
# NOT HELD, and each for the same stated reason: `rows_above_header`,
# `trailing_blank_rows`, `trailing_blank_columns`, `frozen_rows`,
# `defined_names`, `sheet_count` and `sheet_position` count the SHEET'S
# FURNITURE and not the table's records. One title row above a header,
# one frozen row, one column of formatted blanks beyond the last column
# and one defined name are facts about how somebody laid a sheet out;
# none of them is a row of data, so no person is named or counted by
# publishing one of them, and the twin cannot be written without them.
# A count of these is not a count of anybody.
#
# `sheet_names` is neither: a name is published only when it is one this
# version would write itself, which the publication guard settles, and
# withheld otherwise.

WORKBOOK_KEYS = dialect.SHEET_KEYS

WORKBOOK_COLUMN_KEYS = dialect.SHEET_COLUMN_KEYS

DATE_SYSTEM_1900 = dialect.SHEET_DATE_SYSTEM_1900
DATE_SYSTEM_1904 = dialect.SHEET_DATE_SYSTEM_1904
DATE_SYSTEMS = dialect.SHEET_DATE_SYSTEMS


def _counted(kinds: "list[str]", every: "tuple[str, ...]") -> "dict[str, int]":
    """How many of these entries are each key of a closed key space."""
    counts: "dict[str, int]" = {}
    for key in every:
        counts[key] = 0
    for kind in kinds:
        if kind in counts:
            counts[kind] = counts[kind] + 1
    return counts


def _census(
    kinds: "list[str]", every: "tuple[str, ...]", total: int, floor: int
) -> "dict[str, object]":
    """One census over a closed key space, under `dialect.sheet_census`."""
    published = dialect.sheet_census(_counted(kinds, every), every, total, floor)
    out: "dict[str, object]" = {}
    for key in every:
        out[key] = published[key]
    return out


def _format_census(
    codes: "list[str]", total: int, floor: int
) -> "dict[str, object]":
    """What KIND of thing each cell's format makes it, counted.

    THE KIND AND NOT THE CODE, and the reason is a disclosure one rather
    than a convenience. A format code is text out of the file -- a
    custom one may spell a currency, a unit or a label somebody typed --
    and every published sentence in this package is a form it can
    rebuild from its own vocabulary. A census keyed by codes would
    publish that text as a KEY. The kind is what the readers actually
    act on (the study's finding: a date is a number wearing a format,
    and the kind of format decides the type), it is one of six words of
    synthtwin's own, and it is what the twin needs to write the column
    back. The code itself is read, and decides the kind; it is not
    published. That is a stated limit of this landing: a twin cannot
    reproduce a custom format code it was never told.
    """
    kinds: "list[str]" = []
    for code in codes:
        kinds += [format_kind(code)]
    return _census(kinds, FORMAT_KINDS, total, floor)


def _value_codes(classes: "list[str]", codes: "list[str]") -> "list[str]":
    """The format codes the cells HOLDING a value wear, in row order.

    A cell holding nothing wears a format nobody reads it through -- an
    absent cell wears none at all -- so a column two thirds empty used
    to publish the general format for its dates.
    """
    out: "list[str]" = []
    for index in range(len(codes)):
        if index < len(classes) and classes[index] in dialect.SHEET_VALUE_CLASSES:
            out += [codes[index]]
    return out


def _leading_code(
    classes: "list[str]",
    codes: "list[str]",
    kinds: "dict[str, object]",
    floor: int,
) -> str:
    """The format code this column may publish, from its commonest one.

    THE CODE IS PUBLISHED NOW, AND ONLY EVER ONE OF OURS (plan P4-D79).
    Part 1 of this landing published the KIND alone and withheld the
    code, on the ground that a custom code is text out of the person's
    file. That reasoning stands and is unchanged -- what changed is that
    a twin of a workbook has to be WRITTEN, and a date column written
    with no format code comes back from every reader as a column of
    five-digit numbers. So the column's commonest code is published when
    it is one of Excel's own built-in codes, which are the standard's
    vocabulary and nobody's text, and otherwise the CANONICAL code of
    its kind is published in its place. A code somebody typed is never
    published and never written: the twin wears the standard spelling of
    a date rather than theirs, which is the landing's stated limit.

    IT IS THE COMMONEST AMONG THE CELLS HOLDING A VALUE, AND ONLY WHERE
    IT IS WORN BY THE LINE (plan P4-D160). The code a column publishes
    tells a reader which kind of cell is commonest without a count, and
    it is also what the twin writes a cell with where the census held
    every count back -- so it stands where it is a group's and never
    where it is one cell's: a code worn by fewer cells than the line
    gives way to the canonical code of the commonest KIND that reaches
    it, and to the general format where none does. A kind the census
    publishes as nought is never the one chosen.
    """
    line = dialect.sheet_line(floor)
    held = _value_codes(classes, codes)
    counts: "dict[str, int]" = {}
    kind_counts: "dict[str, int]" = {}
    for code in held:
        counts[code] = (counts[code] if code in counts else 0) + 1
        kind = format_kind(code)
        kind_counts[kind] = (kind_counts[kind] if kind in kind_counts else 0) + 1
    best = ""
    seen = 0
    for code in sorted(counts):
        if counts[code] > seen:
            seen = counts[code]
            best = code
    chosen = GENERAL_FORMAT
    if best and seen >= line and not _denied_kind(kinds, format_kind(best)):
        chosen = best
        if best not in dialect.SHEET_BUILT_IN_FORMAT_IDS:
            chosen = _canonical_code(format_kind(best))
        return chosen
    widest = ""
    many = 0
    for kind in FORMAT_KINDS:
        if kind in kind_counts and kind_counts[kind] > many:
            many = kind_counts[kind]
            widest = kind
    if widest and many >= line and not _denied_kind(kinds, widest):
        return _canonical_code(widest)
    if not _denied_kind(kinds, FORMAT_PLAIN):
        return GENERAL_FORMAT
    # Every cell wears a kind other than plain, and no value-holding cell
    # wears one by the line: the kind the census counts most is written.
    most = FORMAT_PLAIN
    largest = 0
    for kind in FORMAT_KINDS:
        found = kinds[kind] if kind in kinds else None
        if isinstance(found, int) and found > largest:
            largest = found
            most = kind
    return _canonical_code(most)


def _denied_kind(kinds: "dict[str, object]", kind: str) -> bool:
    """Whether the published census says no cell wears this kind."""
    if kind not in kinds:
        return False
    found = kinds[kind]
    return isinstance(found, int) and not isinstance(found, bool) and found == 0


def _canonical_code(kind: str) -> str:
    """The canonical code of one kind of format."""
    canonical = dialect.SHEET_CANONICAL_FORMAT_CODES[kind]
    if isinstance(canonical, str):
        return canonical
    return GENERAL_FORMAT


def _value_class(classes: "list[str]", floor: int) -> "str | None":
    """Which class most of the column's value-holding cells are (P4-D160).

    THE ONE FACT A WITHHELD CENSUS STILL OWES THE TWIN. Where one cell of
    a column is unlike the rest -- one absent cell among two hundred
    texts of digits -- the census may publish no count at all, because
    any count it published would let a reader subtract the odd cell's.
    The twin then has nothing to tell a text of digits from a number by,
    and `00123` would be written as the number 123. So the commonest
    value class is published by NAME, without a count, where it is held
    by the line; a class held by fewer is not published.
    """
    counts = _counted(classes, dialect.SHEET_VALUE_CLASSES)
    best = ""
    seen = 0
    for kind in dialect.SHEET_VALUE_CLASSES:
        if counts[kind] > seen:
            seen = counts[kind]
            best = kind
    if best and seen >= dialect.sheet_line(floor):
        return best
    return None


def mixed_storage(sheet: Sheet) -> "tuple[int, str] | None":
    """The first column whose cells mix how they are stored, or nothing.

    THE TWO MIXES A TWIN CANNOT CARRY (review item 6 of the files
    review, plan P4-D162). The description publishes how many cells of a
    column are of each class and wear each kind of format, and the
    column's values as ONE distribution -- nothing that says which
    values the numbers were and which the texts. The writer can keep a
    class with its values only where the values say which class they
    are: a label is never a number, `TRUE` is never an error. Where they
    do not, the association is lost silently. Measured: thirty numeric
    cells of 10 beside thirty text cells of 1000 gave a twin whose
    numeric cells summed to 15150 against 300, with every published fact
    held. So the column is refused where

    * two value classes stand in it and some cell of one is spelled the
      way a cell of the other is written (`dialect.sheet_class_fits`); or
    * its NUMBER cells wear more than one kind of format -- some dates
      and some plain -- because the dates and the plain numbers are one
      distribution in the description too.

    Returns the column's index and which of `errors.MIXED_TYPES` and
    `errors.MIXED_FORMATS` it is. Guarantees: a fixed function of the
    sheet; raises nothing.
    """
    for index in range(len(sheet.classes)):
        classes = sheet.classes[index]
        texts = sheet.columns[index]
        present: "dict[str, bool]" = {}
        for kind in classes:
            if kind in dialect.SHEET_VALUE_CLASSES:
                present[kind] = True
        if len(present) >= 2:
            for row in range(len(classes)):
                own = classes[row]
                if own not in present:
                    continue
                for other in present:
                    if other == own or other == dialect.SHEET_CELL_TEXT:
                        continue
                    if dialect.sheet_class_fits(other, texts[row]):
                        return (index, errors.MIXED_TYPES)
        worn: "dict[str, bool]" = {}
        codes = sheet.formats[index]
        for row in range(len(classes)):
            if classes[row] == dialect.SHEET_CELL_NUMBER and row < len(codes):
                worn[format_kind(codes[row])] = True
        if len(worn) >= 2:
            return (index, errors.MIXED_FORMATS)
    return None


def _published_sheet_names(reading: Reading) -> "list[object]":
    """Each sheet's name where it may be published, else nothing.

    A sheet name is free text somebody typed and can hold a person's
    name, so it is published only when it is one synthtwin can rebuild
    from its own vocabulary (`dialect.sheet_name_published`) and is
    withheld otherwise. The twin writes a withheld sheet under a neutral
    name and the report says which were withheld, so nothing is lost
    silently.
    """
    out: "list[object]" = []
    for entry in reading.sheets:
        out += [dialect.sheet_name_published(entry.name)]
    return out


def _published_extents(reading: Reading) -> "list[object]":
    """Each sheet's block of cells as the description publishes it."""
    out: "list[object]" = []
    for held in reading.sheet_extents:
        if held is None:
            out += [None]
            continue
        out += [{"columns": held[1], "rows": held[0]}]
    return out


def as_the_twin_writes(
    classes: "list[str]", texts: "list[str]", emptied: "tuple[str, ...]"
) -> "list[str]":
    """A column's cell classes, with each cell the twin writes empty absent.

    ``emptied`` holds the spellings of absent cells whose spelling the
    column does not reproduce (plan P4-D170): a cell holding a value that
    reads as one of them is written holding nothing, so it is counted as
    a cell holding nothing -- absent -- and every other cell keeps its
    class. Guarantees: a fixed function of the arguments; raises nothing.
    """
    wanted: "dict[str, bool]" = {}
    for spelling in emptied:
        wanted[spelling] = True
    out: "list[str]" = []
    for index in range(len(classes)):
        kind = classes[index]
        if (
            kind in dialect.SHEET_VALUE_CLASSES
            and index < len(texts)
            and texts[index] in wanted
        ):
            kind = CELL_ABSENT
        out += [kind]
    return out


def document_of(
    reading: Reading,
    sheet: Sheet,
    floor: int,
    emptied: "tuple[tuple[str, ...], ...]" = (),
) -> "dict[str, object]":
    """The workbook as the description publishes it (contract 4.3b).

    Every key is always present, so the loader can require exactly this
    key set; a fact the workbook does not carry, or one the disclosure
    rule of `dialect.sheet_census` holds back, is `null` or nought.
    ``emptied`` is, per column, the absent spellings the twin writes
    empty (`as_the_twin_writes`); left out, no cell is moved.
    """
    position = 0
    for index in range(len(reading.sheets)):
        if reading.sheets[index].name == reading.chosen:
            position = index + 1
    columns: "list[object]" = []
    # One census per COLUMN, and not per name: a table read with
    # `--first-row data` has no names of its own (plan P4-D161).
    for index in range(len(sheet.columns)):
        total = sheet.n_rows
        formulas = 0
        if index < len(sheet.formulas):
            for carried in sheet.formulas[index]:
                if carried:
                    formulas = formulas + 1
        kinds = _format_census(sheet.formats[index], total, floor)
        classes = sheet.classes[index]
        if index < len(emptied):
            classes = as_the_twin_writes(
                classes, sheet.columns[index], emptied[index]
            )
        columns += [
            {
                "cell_classes": _census(classes, CELL_CLASSES, total, floor),
                "format_kinds": kinds,
                "format_code": _leading_code(
                    classes, sheet.formats[index], kinds, floor
                ),
                "formulas": dialect.sheet_count(formulas, total, floor),
                "value_class": _value_class(classes, floor),
            }
        ]
    return {
        "autofilter": bool(reading.autofilter),
        "columns": columns,
        "date_system": (
            DATE_SYSTEM_1904 if reading.epoch_1904 else DATE_SYSTEM_1900
        ),
        "defined_names": reading.defined_names,
        "defined_table": bool(reading.table_names),
        # HELD TO THE SMALLEST GROUP LIKE EVERY OTHER COUNT OF RECORDS
        # (repair of landing 2b.10, plan P4-D160). This one counts ROWS OF
        # THE TABLE: "exactly one record here holds nothing" names that
        # record, and "all but one" names the record that does not, which
        # is what the twin's third clause forbids. The layout counts below
        # are exempt and say why in the comment above WORKBOOK_KEYS.
        "empty_rows_inside": dialect.sheet_count(
            sheet.empty_rows_inside, sheet.n_rows, floor
        ),
        "frozen_rows": reading.frozen_rows,
        "macro_project": reading.has_macro_project,
        "rows_above_header": sheet.rows_above,
        "sheet_count": len(reading.sheets),
        # THE BLOCK OF CELLS EVERY OTHER SHEET HOLDS (plan P4-D82), so
        # that the twin can carry a sheet of the same shape and a reader
        # meets the same workbook. Nothing of what those cells HELD is
        # published: this is how much room they take and nothing else,
        # which is furniture in the same sense as the rows above a header
        # -- and the sheet the table was read from publishes none,
        # because the table's own facts describe it.
        "sheet_extents": _published_extents(reading),
        "sheet_hidden": reading.chosen_hidden,
        "sheet_names": _published_sheet_names(reading),
        "sheet_position": position,
        "trailing_blank_columns": sheet.trailing_blank_columns,
        "trailing_blank_rows": sheet.trailing_blank_rows,
    }
