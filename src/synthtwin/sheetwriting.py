"""The twin written as a spreadsheet workbook (plan P4-D79).

WHY THIS MODULE EXISTS AND WHY IT IS OURS. The owner's ruling of
2026-09-15 is that the twin is written the way its source file was, and
a workbook's twin is a workbook. Neither Python writer in common use
can be handed the job: the study behind this landing measured openpyxl
turning any text beginning with `=` into a formula with no cached
value, and xlsxwriter turning the same text into a formula with a
cached 0 and any `http://...` text into a hyperlink. Those are exactly
the cells a twin of a research table has to carry unchanged, so the
writer is written here, out of the standard library, and admits no
third runtime dependency into the offline guarantee.

WHAT THIS MODULE MAY TOUCH. It builds bytes and hands them back. It
opens nothing, reads nothing and writes nothing: the one write stays in
`writing`, where every other output of this package is written, and the
zip package is assembled in memory. It parses NO markup -- the reader's
parser is not reachable from here -- which is what keeps the generator's
import graph free of anything that opens or parses a table, the rule
`tests/test_cli_generate.py` now guards in a fresh interpreter.

WHAT IT NEVER WRITES, stated as a list because each one is a way a
spreadsheet file can act on the person who opens it: no formula, ever,
whatever a cell's text begins with; no macro project; no external link,
no hyperlink and no connection; and no cache of any kind -- no
calcChain, no pivot or chart cache, no cached value of a formula that
is not there. A twin is a file of values.

THE BYTES ARE A FUNCTION OF THE DESCRIPTION AND THE SEED. Every member
of the package carries one fixed moment rather than the clock, the
members are written in one fixed order, and every number this module
writes it writes itself. So the same description and the same seed give
the same bytes on one platform (plan D12). Across platforms the deflate
stream itself may differ between zlib builds, which the landing states
as a limit rather than claiming past it.
"""

from synthtwin import contract, dialect, generation

# THE ONE MOMENT EVERY MEMBER CARRIES. A zip member ordinarily records
# when it was written, which would make the same twin different bytes on
# every run. This is the same fixed moment the seeded test builder uses
# and the earliest a zip can store.
_MOMENT = (1980, 1, 1, 0, 0, 0)

_DECLARATION = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
_RELS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
_PACKAGE = "http://schemas.openxmlformats.org/package/2006/relationships"
_TYPES = "http://schemas.openxmlformats.org/package/2006/content-types"
_SHEET_TYPE = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"
)

# The neutral name the twin's defined table carries. A defined table's
# own name is text somebody typed, so it is never published and never
# written back; what IS written back is that a table is there, resized
# to the twin's own rows, because that is what structured references and
# Power Query read.
_TABLE_NAME = "Table1"


def _escaped(text: str) -> str:
    """One piece of text as XML content.

    A CARRIAGE RETURN IS WRITTEN AS ITS CHARACTER REFERENCE (plan
    P4-D167). Every XML reader turns a literal carriage return into a
    line feed before the text reaches it, so a header `line&#13;name`
    that the reader had read as `line\rname` came back from the twin as
    `line\nname`: the real workbook validated and its twin missed the
    header's presence, its names, the column order and every column's
    position. `&#13;` is the one spelling that survives the reading.
    """
    if not isinstance(text, str):
        raise TypeError("internal check: a cell's text was not text")
    out = text
    out = out.replace("&", "&amp;")
    out = out.replace("<", "&lt;")
    out = out.replace(">", "&gt;")
    out = out.replace('"', "&quot;")
    out = out.replace("\r", "&#13;")
    return out


def _attribute(text: str) -> str:
    """One piece of text as an XML ATTRIBUTE's value.

    An attribute's tab and line feed are turned into spaces by every
    reader as well, so all three are written as references here.
    """
    if not isinstance(text, str):
        raise TypeError("internal check: an attribute's text was not text")
    out = text
    out = out.replace("&", "&amp;")
    out = out.replace("<", "&lt;")
    out = out.replace(">", "&gt;")
    out = out.replace('"', "&quot;")
    out = out.replace("\r", "&#13;")
    out = out.replace("\n", "&#10;")
    out = out.replace("\t", "&#9;")
    return out


def _cleaned(text: str) -> str:
    """The text with the characters XML cannot carry taken out.

    A workbook cell cannot hold most control characters at all, and a
    twin that carried one would be a file no reader opens. Every value
    here came from the description, so reaching this is rare; it is a
    guard rather than a transformation.
    """
    if not isinstance(text, str):
        raise TypeError("internal check: a cell's text was not text")
    out = ""
    for character in text:
        place = ord(character)
        if place in (9, 10, 13) or place >= 32:
            out = out + character
    return out


def column_reference(number: int) -> str:
    """The letters naming a column, counting from one: 1 is A, 28 is AB."""
    if not isinstance(number, int):
        raise TypeError("internal check: a column number was not a number")
    if number < 1:
        raise ValueError("internal check: a column number was below one")
    letters = ""
    left = number
    while left > 0:
        left = left - 1
        letters = chr(65 + left % 26) + letters
        left = left // 26
    return letters


def number_spelling(text: str) -> str:
    """The text as a workbook stores a number, or "" where it is not one.

    WHAT IS DELIBERATELY REFUSED HERE. A number a workbook stores is a
    plain spelling: an optional sign, figures, an optional point and
    figures, an optional exponent. A grouped number (`1,234`), a
    decimal comma (`0,5`), a bracketed negative, a percent sign or a
    currency mark is NOT one -- in a workbook those are a FORMAT worn by
    a plain number, never the stored value -- so a cell whose text is
    written that way is written as text and keeps its characters. That
    is what stops the twin from turning one of the person's published
    spellings into a different number.

    The rule is `dialect.sheet_number_spelling`, which the reader asks
    too when it refuses a column mixing numbers with texts spelled as
    numbers (plan P4-D166); one writing of it keeps the two in step.
    """
    return dialect.sheet_number_spelling(text)


def boolean_spelling(text: str) -> str:
    """`1` or `0` where the text is a boolean's spelling, else nothing."""
    if not isinstance(text, str):
        raise TypeError("internal check: a cell's text was not text")
    folded = text.casefold()
    if folded in ("true", "1"):
        return "1"
    if folded in ("false", "0"):
        return "0"
    return ""


# WHICH ERROR A CELL CARRIES IS PUBLISHED, and the twin writes it.
# Measured rather than assumed: an error cell reaches the column
# machinery as an ABSENT cell whose source spelling is the error's own
# kind, so `missing_by_source` already publishes how many cells said
# `#N/A` and how many said `#DIV/0!`, and the generator writes those
# spellings into the cells it makes. An earlier writing of this module
# put a canonical `#N/A` in every error cell instead, and the validator
# caught it at once: two obligations MISSED on a twin whose own
# description named both kinds. The cell's own text is what is written.

_NOTHING_CLASSES = (
    dialect.SHEET_CELL_ABSENT,
    dialect.SHEET_CELL_BLANK,
    dialect.SHEET_CELL_EMPTY,
)
_VALUE_CLASSES = dialect.SHEET_VALUE_CLASSES


def _wanted(census: "dict[str, int | None]", kind: str) -> int:
    """How many cells of this class the description asks for.

    A count the smallest group held back (`null`) is not a licence to
    write none: it means the number was not published, and the class it
    stands for is then filled by the column's leading class rather than
    being invented here.
    """
    if kind in census:
        found = census[kind]
        if isinstance(found, int):
            return found
    return 0


def _denied(census: "dict[str, int | None]", kind: str) -> bool:
    """Whether the census says outright that no cell has this class.

    A published `0` is a FACT about the column; a `null` is the floor
    holding a number back and says nothing at all. The two must not be
    read the same way, which is the whole of the defect below.
    """
    if kind not in census:
        return False
    found = census[kind]
    if isinstance(found, bool) or not isinstance(found, int):
        return False
    return found == 0


def _leading(census: "dict[str, int | None]", among: "tuple[str, ...]") -> str:
    """Which of these classes the column holds most of.

    Ties are broken by the order of the tuple, which is fixed, so this
    is a function of the description and not of a dictionary's order.

    A CLASS THE CENSUS PUBLISHES AS NOUGHT IS NEVER THE LEADING ONE, and
    that is a defect this was measured into (repair of landing 2b.10).
    Where the smallest group held every count of a column back, every
    count read as nought here, the tie fell to the FIRST class in the
    tuple, and the remainder was written in it -- so a column whose
    census publishes `boolean 0` got a twin full of booleans, and the
    quality report missed `workbook.cell-classes` on eight columns at a
    floor of eleven while the real file passed. A withheld count is not
    a licence to write none, and a published nought is not a count to
    fall back on: the remainder goes to a class whose number was not
    published rather than to one the description denies.
    """
    best = among[len(among) - 1]
    seen = -1
    best_denied = True
    for kind in among:
        count = _wanted(census, kind)
        denied = _denied(census, kind)
        if count > seen:
            seen = count
            best = kind
            best_denied = denied
            continue
        if count == seen and best_denied and not denied:
            best = kind
            best_denied = denied
    return best


def _left(census: "dict[str, int | None]", kind: str) -> "int | None":
    """How many cells of this class the census still asks for.

    None where the count was withheld: the census asks for some number
    of them nobody was told, which is not a licence for none.
    """
    if kind not in census:
        return None
    found = census[kind]
    if isinstance(found, bool) or not isinstance(found, int):
        return None
    return found


# The classes a cell holding a value can be told apart by its spelling
# (plan P4-D166), in the order a census is handed out in.
_TOLD_BY_SPELLING = (
    dialect.SHEET_CELL_ERROR,
    dialect.SHEET_CELL_BOOLEAN,
    dialect.SHEET_CELL_DATE,
    dialect.SHEET_CELL_NUMBER,
)


def cell_classes(
    census: "dict[str, int | None]",
    cells: "tuple[str, ...]",
    value_class: "str | None" = None,
) -> "tuple[str, ...]":
    """Which class each generated cell of one column is written as.

    THE GENERATOR STAYS TABLE-BLIND, AND THIS IS THE SEAM THAT LETS IT.
    `generation.generate` produces the column's cells as text, knowing
    nothing about workbooks; this decides what each of those cells IS in
    the file, from the census the description publishes and from the
    text itself. So the rule that a column of text which all looks
    numeric stays TEXT is kept here, once, for every column: the class
    comes from what the source held, never from what the twin's
    characters could be read as.

    A cell holding no text takes one of the three classes that hold
    nothing -- absent, a styled blank, or a cell holding the empty
    string -- and a cell holding text takes one of the classes that hold
    a value. Within each group the published counts are handed out in
    row order, so a column whose census is entirely one class is written
    entirely that way and a census that does not add up cannot leave a
    cell classless.

    A CLASS GOES ONLY TO A CELL SPELLED THE WAY THAT CLASS IS WRITTEN
    (plan P4-D166). The first writing handed the error, boolean and text
    counts out to the cells in row order whatever they held, so a column
    of forty `#N/A` errors, forty `North` and forty `South` got a twin
    marking twenty-six ordinary labels as errors: pandas read 27, 27 and
    66 missing from the twin against 40, 40 and 40 from the source, and
    validation missed nothing. An error goes to an error's spelling, a
    boolean to `TRUE` or `FALSE`, a date to ISO text and a number to a
    plain number (`dialect.sheet_class_fits`), and text takes what is
    left -- first the cells no class still wanted could hold.

    WHERE THE CENSUS WITHHELD A COUNT, ``value_class`` DECIDES (plan
    P4-D164). A cell no published count claims goes to the column's
    named commonest class where its spelling fits one, then to a
    withheld class it fits, then to text -- so a column of digit texts
    whose every count was withheld is still written as text, and a
    column of numbers still as numbers.
    """
    empty_order: "list[int]" = []
    full_order: "list[int]" = []
    for index in range(len(cells)):
        if cells[index] == "":
            empty_order += [index]
            continue
        full_order += [index]

    out: "list[str]" = []
    for _index in range(len(cells)):
        out += [""]

    leading_nothing = _leading(census, _NOTHING_CLASSES)
    at = 0
    for kind in _NOTHING_CLASSES:
        left = _wanted(census, kind)
        while left > 0 and at < len(empty_order):
            out[empty_order[at]] = kind
            at = at + 1
            left = left - 1
    withheld_nothing = ""
    for kind in _NOTHING_CLASSES:
        if not withheld_nothing and _left(census, kind) is None:
            withheld_nothing = kind
    while at < len(empty_order):
        out[empty_order[at]] = (
            withheld_nothing if withheld_nothing else leading_nothing
        )
        at = at + 1

    remaining: "dict[str, int | None]" = {}
    for kind in _VALUE_CLASSES:
        remaining[kind] = _left(census, kind)
    taken: "dict[int, bool]" = {}
    for kind in _TOLD_BY_SPELLING:
        wanted = remaining[kind]
        if wanted is None:
            continue
        fitting: "list[int]" = []
        for index in full_order:
            if index not in taken and dialect.sheet_class_fits(kind, cells[index]):
                fitting += [index]
        for index in _spread_over(fitting, wanted):
            out[index] = kind
            taken[index] = True
        remaining[kind] = wanted - min(wanted, len(fitting))

    text_left = remaining[dialect.SHEET_CELL_TEXT]
    if text_left is not None and text_left > 0:
        for tier in (0, 1):
            for index in full_order:
                if text_left <= 0:
                    break
                if index in taken:
                    continue
                if tier == 0 and _still_wanted(remaining, cells[index]):
                    continue
                out[index] = dialect.SHEET_CELL_TEXT
                taken[index] = True
                text_left = text_left - 1
        remaining[dialect.SHEET_CELL_TEXT] = text_left

    leading_value = _leading(census, _VALUE_CLASSES)
    for index in full_order:
        if index in taken:
            continue
        out[index] = _unclaimed_class(
            remaining, cells[index], value_class, leading_value
        )
    return tuple(out)


def _spread_over(fitting: "list[int]", wanted: int) -> "list[int]":
    """Which of the cells a class fits it takes: all, or an even spread.

    WHERE MORE CELLS FIT A CLASS THAN ITS COUNT NAMES, THE COUNT IS
    SPREAD OVER THEM (plan P4-D187). A column holding numbers some of
    which were stored as text publishes both counts and one
    distribution of values, so every one of its cells fits `number`.
    Handed out in row order, the numbers took the first rows and the
    text the last: measured, the thirty text cells of a three-hundred-row
    column stood in its last thirty rows. The smooth rotation -- each
    fitting cell adds the count to a credit and is taken where the credit
    reaches the number of fitting cells, which is then taken back --
    takes exactly the count, evenly over the rows. Where no more cells
    fit than the count names, every one is taken, in row order, as
    before.
    """
    if wanted <= 0:
        return []
    if len(fitting) <= wanted:
        return fitting
    chosen: "list[int]" = []
    credit = 0
    for index in fitting:
        credit = credit + wanted
        if credit >= len(fitting):
            credit = credit - len(fitting)
            chosen += [index]
    return chosen


def _still_wanted(remaining: "dict[str, int | None]", text: str) -> bool:
    """Whether a class other than text that could hold this cell wants more."""
    for kind in _TOLD_BY_SPELLING:
        wanted = remaining[kind]
        if wanted is not None and wanted <= 0:
            continue
        if dialect.sheet_class_fits(kind, text):
            return True
    return False


def _unclaimed_class(
    remaining: "dict[str, int | None]",
    text: str,
    value_class: "str | None",
    leading: str,
) -> str:
    """The class a cell no published count claimed is written as."""
    order: "list[str]" = []
    if value_class is not None and value_class in remaining:
        order += [value_class]
    for kind in _VALUE_CLASSES:
        order += [kind]
    for kind in order:
        if remaining[kind] is None and dialect.sheet_class_fits(kind, text):
            return kind
    if dialect.sheet_class_fits(leading, text):
        return leading
    return dialect.SHEET_CELL_TEXT


def _place_of(
    items: "list[str]", places: "dict[str, int]", text: str
) -> int:
    """Where this text sits in the shared-string table, adding it if new.

    Excel writes every piece of text once and points at it, and its own
    save turns an inline string into a shared one, so the twin is
    written the way Excel writes it. The table is two plain containers
    rather than an object with methods: the offline audit refuses a
    method call on a value it cannot trace, and a list and a mapping are
    values it can.
    """
    if not isinstance(text, str):
        raise TypeError("internal check: a cell's text was not text")
    if text in places:
        found = places[text]
        if isinstance(found, int):
            return found
    place = len(items)
    items += [text]
    places[text] = place
    return place


def _styles_part(codes: "tuple[str, ...]") -> str:
    """The style table: one style per published format code, plus the header.

    Every code here came from the description, and every one of them is
    one `dialect.sheet_format_code_publishable` admits: Excel's own
    published vocabulary, synthtwin's canonical codes, or a code of the
    format language's own tokens alone written as the source wrote it
    (plan P4-D189). A code carrying anybody's words is never written,
    because one is never published.
    """
    customs: "list[str]" = []
    for code in codes:
        if code not in dialect.SHEET_BUILT_IN_FORMAT_IDS and code not in customs:
            customs += [code]
    text = _DECLARATION + f'<styleSheet xmlns="{_MAIN}">'
    if customs:
        text = text + f'<numFmts count="{len(customs)}">'
        for index in range(len(customs)):
            text = text + (
                f'<numFmt numFmtId="{164 + index}" '
                f'formatCode="{_attribute(customs[index])}"/>'
            )
        text = text + "</numFmts>"
    text = text + (
        '<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font>'
        '<font><b/><sz val="11"/><name val="Calibri"/></font></fonts>'
        '<fills count="2"><fill><patternFill patternType="none"/></fill>'
        '<fill><patternFill patternType="gray125"/></fill></fills>'
        '<borders count="1"><border><left/><right/><top/><bottom/>'
        "<diagonal/></border></borders>"
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" '
        'borderId="0"/></cellStyleXfs>'
    )
    text = text + f'<cellXfs count="{len(codes) + 1}">'
    for code in codes:
        number = 0
        if code in dialect.SHEET_BUILT_IN_FORMAT_IDS:
            found = dialect.SHEET_BUILT_IN_FORMAT_IDS[code]
            if isinstance(found, int):
                number = found
        else:
            for index in range(len(customs)):
                if customs[index] == code:
                    number = 164 + index
        text = text + (
            f'<xf numFmtId="{number}" fontId="0" fillId="0" borderId="0" '
            'xfId="0" applyNumberFormat="1"/>'
        )
    # The last style is the header's: bold, with the general format.
    text = text + (
        '<xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" '
        'applyFont="1"/>'
    )
    text = text + "</cellXfs>"
    text = text + (
        '<cellStyles count="1"><cellStyle name="Normal" xfId="0" '
        'builtinId="0"/></cellStyles></styleSheet>'
    )
    return text


def _wears_edge_space(text: str) -> bool:
    """Whether the text begins or ends with space a reader would trim."""
    if not isinstance(text, str):
        raise TypeError("internal check: a cell's text was not text")
    return text != text.strip()


def _shared_strings_part(items: "list[str]") -> str:
    """The shared-string table, preserving every space a cell's text has."""
    text = _DECLARATION + (
        f'<sst xmlns="{_MAIN}" count="{len(items)}" '
        f'uniqueCount="{len(items)}">'
    )
    for item in items:
        shown = _escaped(item)
        if _wears_edge_space(item):
            text = text + f'<si><t xml:space="preserve">{shown}</t></si>'
            continue
        text = text + f"<si><t>{shown}</t></si>"
    text = text + "</sst>"
    return text


def _cell(reference: str, kind: str, value: str, style: int) -> str:
    """One `<c>` element. It never carries a formula, whatever it holds."""
    marks = f' r="{reference}"'
    if kind:
        marks = marks + f' t="{kind}"'
    if style:
        marks = marks + f' s="{style}"'
    if not value:
        return f"<c{marks}/>"
    return f"<c{marks}><v>{_escaped(value)}</v></c>"


def _core_part() -> str:
    """Document properties, written NEUTRAL.

    The study found openxlsx recording the operating-system user name as
    the file's creator and Excel writing the signed-in user's name into
    `lastModifiedBy`. Both name a person, so the twin carries neither,
    and neither is read from the source or published.
    """
    text = (
        _DECLARATION
        + '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/'
        'package/2006/metadata/core-properties" xmlns:dc="http://purl.org/'
        'dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        "<dc:title></dc:title><dc:subject></dc:subject>"
        "<dc:creator></dc:creator><cp:lastModifiedBy></cp:lastModifiedBy>"
        "</cp:coreProperties>"
    )
    return text


def _app_part() -> str:
    """The other half of the document properties, equally neutral."""
    text = (
        _DECLARATION
        + '<Properties xmlns="http://schemas.openxmlformats.org/'
        'officeDocument/2006/extended-properties">'
        "<Application>synthtwin</Application><Company></Company>"
        "</Properties>"
    )
    return text


# -- where the twin's rows sit on the sheet ----------------------------


def _placeholder_rows(above: int, n_columns: int) -> int:
    """How many rows the twin writes above its header.

    The COUNT is published and the TEXT never is: a title or a banner
    above a table is free text somebody typed, and the disclosure rule
    names it outright. So the twin writes as many rows as the source had
    and puts NOTHING of the person's in them -- each is one cell holding
    the empty string, which is content to every reader (so the count
    comes back when the twin is described again) and carries no
    character of anybody's table.

    A ONE-COLUMN TABLE CANNOT CARRY THEM, and this is the limit rather
    than a defect hidden behind a rule: the header is found as the first
    row reaching the table's width, so on a table one column wide a
    one-cell row above the header IS the width and would be read back as
    the header. There the twin writes no rows above and the landing
    states the loss.
    """
    if n_columns <= 1:
        return 0
    return above


def _empty_row_places(
    classes: "list[tuple[str, ...]]", n_rows: int, wanted: int
) -> "dict[int, bool]":
    """Which generated rows are written as records holding nothing.

    A record holding nothing is a row where EVERY column's cell holds
    nothing, so the twin can only place one where the generated cells
    already leave one: the published counts of each column are met
    first, and a row is then blank only if every column's allocation
    made it blank. The rows that qualify are taken in order until the
    published count is met; where fewer qualify than the source had, the
    twin writes fewer and the shortfall is a stated limit of the landing
    rather than a cell quietly thrown away.
    """
    places: "dict[int, bool]" = {}
    if wanted <= 0:
        return places
    left = wanted
    for row in range(n_rows):
        if left <= 0:
            break
        holding = False
        for column in classes:
            if row < len(column) and column[row] not in _NOTHING_CLASSES:
                holding = True
                break
        if not holding:
            places[row] = True
            left = left - 1
    return places


def cell_format_kinds(
    census: "dict[str, int | None]",
    classes: "tuple[str, ...]",
    format_code: str = "General",
    dated: "tuple[str, ...] | None" = None,
) -> "tuple[str, ...]":
    """Which kind of format each cell of one column wears.

    A MIXTURE IS REPRODUCED AS ITS COUNTS, NOT COLLAPSED TO THE MAJORITY.
    An earlier writing of this module gave every cell of a column the
    column's one published code, and the validator caught it at once: a
    column whose blanks wear a text format and whose values wear none
    published `plain 133, text 67` and its twin came back `plain 200,
    text 0`. The census publishes a count per kind, so the twin owes a
    cell per count.

    AN ABSENT CELL IS ALWAYS PLAIN, and that is not a choice: nothing is
    written for it, so every reader sees the general format there. The
    kinds that are not plain are therefore handed out among the cells
    that ARE written, in row order, a text format first to the cells
    holding text and a date or time format first to the cells holding a
    number, and plain takes the rest.

    A DATE FORMAT GOES TO A DATE FIRST (repair of the stage-2b
    integration). ``dated`` names, per cell, the kind of date its text
    was written from (`date`, `datetime`, or "" for none), and a date
    or datetime format is handed first to the cells holding a date of
    that kind, then to the cells holding a date of the other, and only
    then by the order above. A date wearing the general format is read
    back as a bare day count, so where the census names as many date
    formats as there are dates, every date keeps its format.

    A WITHHELD COUNT IS NOT A LICENCE FOR PLAIN (plan P4-D166). Where
    the census held the counts back, the cells no published count claims
    used to be written plain -- including in a column whose census
    PUBLISHED plain as nought: twenty dates at a floor of eleven came
    back `plain 20` and missed `workbook.format-kinds`. So a date no
    count claimed keeps its own kind where that kind's count was
    withheld (measured on the titled book at a floor of eleven: the date
    column read back as numbers and missed its role); and any other such
    cell takes the kind of the column's published code where that kind
    was withheld, then a withheld kind, and plain only where plain was
    not denied. A PUBLISHED count is never exceeded by either rule.

    (Both repairs rewrote this step, the integration's for dates and the
    files review's for withheld counts and cell classes; at their merge
    the two orders were composed into this one: a date's own kind first,
    then the class tiers.)
    """
    written: "list[int]" = []
    absent = 0
    for index in range(len(classes)):
        if classes[index] != dialect.SHEET_CELL_ABSENT:
            written += [index]
            continue
        absent = absent + 1
    out: "list[str]" = []
    for _index in range(len(classes)):
        out += [dialect.SHEET_FORMAT_PLAIN]
    taken: "dict[int, bool]" = {}
    for kind in dialect.SHEET_FORMAT_KINDS:
        if kind == dialect.SHEET_FORMAT_PLAIN:
            continue
        left = _wanted(census, kind)
        order: "list[int]" = []
        if dated is not None and kind in (
            dialect.SHEET_FORMAT_DATE, dialect.SHEET_FORMAT_DATETIME
        ):
            for index in written:
                if dated[index] == kind:
                    order += [index]
            for index in written:
                if dated[index] and dated[index] != kind:
                    order += [index]
        for tier in (0, 1, 2):
            for index in written:
                if _format_tier(kind, classes[index]) == tier:
                    order += [index]
        for index in order:
            if left <= 0:
                break
            if index in taken:
                continue
            out[index] = kind
            taken[index] = True
            left = left - 1
    if dated is not None:
        for index in written:
            if index in taken or not dated[index]:
                continue
            if _left(census, dated[index]) is not None:
                continue
            out[index] = dated[index]
            taken[index] = True
    plain_left = _left(census, dialect.SHEET_FORMAT_PLAIN)
    if plain_left is not None:
        plain_left = plain_left - absent
    leading = dialect.sheet_format_kind(format_code)
    for index in written:
        if index in taken:
            continue
        if plain_left is not None and plain_left > 0:
            plain_left = plain_left - 1
            continue
        if plain_left is None and leading == dialect.SHEET_FORMAT_PLAIN:
            continue
        out[index] = _unclaimed_kind(census, leading, plain_left is None)
    return tuple(out)


def _format_tier(kind: str, cell_class: str) -> int:
    """How well a cell of this class suits a format of this kind: 0 best."""
    if kind == dialect.SHEET_FORMAT_TEXT:
        if cell_class in (dialect.SHEET_CELL_TEXT, dialect.SHEET_CELL_EMPTY):
            return 0
    elif cell_class in (dialect.SHEET_CELL_NUMBER, dialect.SHEET_CELL_DATE):
        return 0
    if cell_class == dialect.SHEET_CELL_BLANK:
        return 1
    return 2


def _unclaimed_kind(
    census: "dict[str, int | None]", leading: str, plain_withheld: bool
) -> str:
    """The kind a written cell no published count claimed wears."""
    if _left(census, leading) is None:
        return leading
    if plain_withheld:
        return dialect.SHEET_FORMAT_PLAIN
    for kind in dialect.SHEET_FORMAT_KINDS:
        if _left(census, kind) is None:
            return kind
    return dialect.SHEET_FORMAT_PLAIN


def _code_for_kind(kind: str, published: str) -> str:
    """The code a cell of this kind is written with.

    The column's own published code is used for the kind it IS, so a
    column whose dates were written `mm-dd-yy` keeps that spelling; a
    kind the published code is not gets the canonical code of its own
    kind, which is how a mixture is written back at all.
    """
    # ASKED OF THE RULE AND NOT OF A CLOSED MAP (plan P4-D189): a code
    # published as the source wrote it is in no list, and is the code
    # its own kind's cells wear.
    if dialect.sheet_format_kind(published) == kind:
        return published
    canonical = dialect.SHEET_CANONICAL_FORMAT_CODES[kind]
    if isinstance(canonical, str):
        return canonical
    return "General"


def _aligned_for_empty_records(
    classes: "list[tuple[str, ...]]",
    cells: "list[tuple[str, ...]]",
    n_rows: int,
    wanted: int,
    tags: "list[tuple[str, ...]] | None" = None,
) -> "tuple[list[tuple[str, ...]], list[tuple[str, ...]], list[tuple[str, ...]]]":
    """Move each column's empty cells onto shared rows, keeping every value.

    A RECORD HOLDING NOTHING IS A FACT ABOUT THE WHOLE ROW, and the
    generator cannot produce one: it fills each column's missing cells
    independently, so on a table of any width no row is empty in every
    column at once and a source that had such records got a twin with
    none. Measured on the study's titled book: `empty_rows_inside` went
    from 1 to 0.

    What this does is a PERMUTATION WITHIN EACH COLUMN and nothing else.
    A column's cells are swapped among its own rows so that the cells
    holding nothing come to rest on the same rows in every column; no
    cell is added, removed or changed, so each column keeps its exact
    multiset of values and every published fact about that column still
    holds. Where a column has fewer empty cells than the record count
    asks for, fewer records are emptied and the shortfall is a stated
    limit rather than a value quietly thrown away.

    ``tags`` is one more per-cell list carried through the same
    exchanges, so a fact about a cell travels with the cell; it comes
    back as the third item, all "" where none was given.
    """
    carried: "list[tuple[str, ...]]" = []
    for index in range(len(cells)):
        if tags is not None and index < len(tags):
            carried += [tags[index]]
            continue
        row_tags: "list[str]" = []
        for _value in cells[index]:
            row_tags += [""]
        carried += [tuple(row_tags)]
    if wanted <= 0 or not classes:
        return (classes, cells, carried)
    room = n_rows
    for column in classes:
        spare = 0
        for kind in column:
            if kind in _NOTHING_CLASSES:
                spare = spare + 1
        if spare < room:
            room = spare
    if room < wanted:
        wanted = room
    if wanted <= 0:
        return (classes, cells, carried)

    targets: "dict[int, bool]" = {}
    for row in range(wanted):
        targets[row] = True

    out_classes: "list[tuple[str, ...]]" = []
    out_cells: "list[tuple[str, ...]]" = []
    out_tags: "list[tuple[str, ...]]" = []
    for index in range(len(classes)):
        kinds: "list[str]" = []
        for kind in classes[index]:
            kinds += [kind]
        values: "list[str]" = []
        for value in cells[index]:
            values += [value]
        marks: "list[str]" = []
        for mark in carried[index]:
            marks += [mark]
        spare_rows: "list[int]" = []
        for row in range(len(kinds)):
            if row not in targets and kinds[row] in _NOTHING_CLASSES:
                spare_rows += [row]
        at = 0
        for row in range(wanted):
            if row < len(kinds) and kinds[row] in _NOTHING_CLASSES:
                continue
            if at >= len(spare_rows):
                break
            other = spare_rows[at]
            at = at + 1
            held_kind = kinds[row]
            held_value = values[row]
            held_mark = marks[row]
            kinds[row] = kinds[other]
            values[row] = values[other]
            marks[row] = marks[other]
            kinds[other] = held_kind
            values[other] = held_value
            marks[other] = held_mark
        out_classes += [tuple(kinds)]
        out_cells += [tuple(values)]
        out_tags += [tuple(marks)]
    return (out_classes, out_cells, out_tags)


def _sheet_part(
    names: "tuple[str, ...]",
    cells: "list[tuple[str, ...]]",
    classes: "list[tuple[str, ...]]",
    styles: "list[tuple[int, ...]]",
    n_rows: int,
    write_header: bool,
    header_style: int,
    rows_above: int,
    empty_places: "dict[int, bool]",
    trailing_rows: int,
    trailing_columns: int,
    frozen_rows: int,
    autofilter: bool,
    table: bool,
    items: "list[str]",
    places: "dict[str, int]",
) -> str:
    """The worksheet: the rows above, the header, the records, the blanks."""
    width = len(names)
    empty_place = _place_of(items, places, "")
    text = _DECLARATION + f'<worksheet xmlns="{_MAIN}" xmlns:r="{_RELS}">'
    last_row = rows_above + (1 if write_header else 0) + n_rows
    if trailing_rows:
        last_row = last_row + trailing_rows
    last_column = width + trailing_columns
    if last_row < 1:
        last_row = 1
    if last_column < 1:
        last_column = 1
    text = text + (
        f'<dimension ref="A1:{column_reference(last_column)}{last_row}"/>'
    )
    if frozen_rows:
        text = text + (
            '<sheetViews><sheetView workbookViewId="0">'
            f'<pane ySplit="{frozen_rows}" topLeftCell="A{frozen_rows + 1}" '
            'activePane="bottomLeft" state="frozen"/>'
            "</sheetView></sheetViews>"
        )
    else:
        text = text + '<sheetViews><sheetView workbookViewId="0"/></sheetViews>'
    text = text + "<sheetFormatPr/><sheetData>"

    number = 0
    # The rows above the header: one empty-string cell apiece, no more.
    for _above in range(rows_above):
        number = number + 1
        text = text + f'<row r="{number}">'
        text = text + _cell(f"A{number}", "s", f"{empty_place}", 0)
        text = text + "</row>"

    if write_header:
        number = number + 1
        text = text + f'<row r="{number}">'
        for index in range(width):
            reference = column_reference(index + 1) + f"{number}"
            # A HEADER CELL THE SOURCE LEFT BLANK IS WRITTEN BLANK (plan
            # P4-D165). Its column is named `Unnamed: N` for its place,
            # which is what every reader names it and what the reader
            # names it again from a blank cell -- so writing the words
            # into the twin's header would hand a reader of cells a name
            # the source never had. Nothing is written in its place.
            if names[index] == dialect.unnamed_column(index):
                continue
            place = _place_of(items, places, _cleaned(names[index]))
            text = text + _cell(reference, "s", f"{place}", header_style)
        # The formatted blanks BEYOND the table stand on the header row.
        for extra in range(trailing_columns):
            reference = column_reference(width + extra + 1) + f"{number}"
            text = text + _cell(reference, "", "", 0)
        text = text + "</row>"

    for row in range(n_rows):
        number = number + 1
        if row in empty_places:
            # A record holding nothing: the row is written with no cells
            # at all, which is what every reader reads as an empty record.
            text = text + f'<row r="{number}"/>'
            continue
        line = ""
        for index in range(width):
            kind = classes[index][row]
            if kind == dialect.SHEET_CELL_ABSENT:
                continue
            reference = column_reference(index + 1) + f"{number}"
            style = styles[index][row]
            if kind == dialect.SHEET_CELL_BLANK:
                line = line + _cell(reference, "", "", style)
                continue
            if kind == dialect.SHEET_CELL_EMPTY:
                line = line + _cell(reference, "s", f"{empty_place}", style)
                continue
            value = _cleaned(cells[index][row])
            if kind == dialect.SHEET_CELL_ERROR:
                line = line + _cell(reference, "e", value, style)
                continue
            if kind == dialect.SHEET_CELL_DATE and dialect.sheet_date_is_real(
                value
            ):
                # A date stored as its ISO text is written back as one
                # (plan P4-D168), never as a string a reader hands back
                # as text -- and never where the text wears a date's
                # shape without naming a day of the calendar, which is
                # a cell no reader but this one can read (plan P4-D291).
                line = line + _cell(reference, "d", value, style)
                continue
            if kind == dialect.SHEET_CELL_BOOLEAN:
                spelled = boolean_spelling(value)
                if spelled:
                    line = line + _cell(reference, "b", spelled, style)
                    continue
                place = _place_of(items, places, value)
                line = line + _cell(reference, "s", f"{place}", style)
                continue
            if kind == dialect.SHEET_CELL_NUMBER:
                spelled = number_spelling(value)
                if spelled:
                    line = line + _cell(reference, "", spelled, style)
                    continue
                place = _place_of(items, places, value)
                line = line + _cell(reference, "s", f"{place}", style)
                continue
            place = _place_of(items, places, value)
            line = line + _cell(reference, "s", f"{place}", style)
        if not line:
            text = text + f'<row r="{number}"/>'
            continue
        text = text + f'<row r="{number}">' + line + "</row>"

    # The formatted blanks BELOW the table.
    for _below in range(trailing_rows):
        number = number + 1
        text = text + f'<row r="{number}">'
        text = text + _cell(f"A{number}", "", "", 0)
        text = text + "</row>"

    text = text + "</sheetData>"
    if autofilter and write_header and width:
        first = rows_above + 1
        text = text + (
            f'<autoFilter ref="A{first}:{column_reference(width)}{last_row}"/>'
        )
    if table:
        text = text + '<tableParts count="1"><tablePart r:id="rId1"/></tableParts>'
    text = text + "</worksheet>"
    return text


def _other_sheet_part(
    extent: "tuple[int, int] | None",
    items: "list[str]",
    places: "dict[str, int]",
) -> str:
    """A sheet that is not the table's: its shape, and none of its cells.

    WHY THIS IS NOT AN EMPTY SHEET (plan P4-D82). It was one, and a
    reader then saw a different workbook: measured with pandas, the
    default sheet of a book whose first sheet is a notes page reads back
    as one column and no rows on the real file and as nothing whatever
    on the twin. Writing the person's own text is what the disclosure
    rule forbids, and writing cells that hold the empty string changes
    nothing at all, because every reader folds those into a missing
    value and trims the frame away again -- measured, the same nothing.

    So the sheet is written with as many cells as it held, each carrying
    one word of synthtwin's own. A reader meets a sheet of the same
    shape holding no character of anybody's table. A sheet that held
    nothing is written holding nothing, and a sheet holding a TABLE
    never reaches here: the reader refuses that workbook and asks which
    sheet the table is on.
    """
    rows = 0
    columns = 0
    if extent is not None:
        rows = extent[0]
        columns = extent[1]
    text = _DECLARATION + (
        f'<worksheet xmlns="{_MAIN}" xmlns:r="{_RELS}">'
    )
    if rows and columns:
        last = column_reference(columns) + f"{rows}"
        text = text + f'<dimension ref="A1:{last}"/>'
    else:
        text = text + '<dimension ref="A1"/>'
    text = text + (
        '<sheetViews><sheetView workbookViewId="0"/></sheetViews>'
        "<sheetFormatPr/>"
    )
    if not rows or not columns:
        return text + "<sheetData/></worksheet>"
    place = _place_of(items, places, dialect.SHEET_WITHHELD_CELL)
    text = text + "<sheetData>"
    for row in range(rows):
        number = row + 1
        text = text + f'<row r="{number}">'
        for column in range(columns):
            reference = column_reference(column + 1) + f"{number}"
            text = text + _cell(reference, "s", f"{place}", 0)
        text = text + "</row>"
    return text + "</sheetData></worksheet>"


def _table_part(
    names: "tuple[str, ...]", first_row: int, last_row: int, autofilter: bool
) -> str:
    """A defined table over the twin's OWN rows, under a neutral name.

    The source's table name is never published and never written: a
    table's name is text somebody typed. What is written is that a
    table is there and that it covers the twin's rows, because that is
    what a structured reference and a query read.
    """
    width = len(names)
    span = f"A{first_row}:{column_reference(width)}{last_row}"
    text = _DECLARATION + (
        f'<table xmlns="{_MAIN}" id="1" name="{_TABLE_NAME}" '
        f'displayName="{_TABLE_NAME}" ref="{span}" totalsRowShown="0">'
    )
    if autofilter:
        text = text + f'<autoFilter ref="{span}"/>'
    text = text + f'<tableColumns count="{width}">'
    for index in range(width):
        shown = _attribute(_cleaned(names[index]))
        text = text + f'<tableColumn id="{index + 1}" name="{shown}"/>'
    text = text + "</tableColumns>"
    text = text + (
        '<tableStyleInfo name="TableStyleMedium2" showFirstColumn="0" '
        'showLastColumn="0" showRowStripes="1" showColumnStripes="0"/>'
    )
    text = text + "</table>"
    return text


def _hidden_states(
    sheets: int, chosen: int, chosen_hidden: bool
) -> "list[bool]":
    """Which of the twin's sheets are hidden, so the table can be found.

    THE TWIN WAS UNREADABLE BY SYNTHTWIN ITSELF WITHOUT THIS (repair of
    landing 2b.10). A workbook is read at the sheet the person named or
    else at the FIRST VISIBLE SHEET, and the writer wrote every sheet
    visible -- so a table that sat on sheet 2 behind a hidden notes page
    got a twin whose sheet 1 was an empty placeholder, and `profile` and
    `validate` both refused it: "the sheet 'Notes' holds no cells at all".
    Measured on the landing's own hidden-first fixture, and on a
    three-sheet book of the same shape.

    The rule is the reading rule read backwards. Every sheet BEFORE the
    chosen one is hidden, so the chosen sheet is the first visible one
    and the twin's own reader lands on the table. The chosen sheet keeps
    the hidden state the description publishes. Sheets after it stay
    visible, so that a workbook whose chosen sheet is itself hidden
    still has one.

    THE ONE PLACE THIS CANNOT BE HONOURED, stated rather than hidden: a
    workbook whose every sheet is hidden cannot be opened by a
    spreadsheet application and is refused by synthtwin's own reader, so
    a lone sheet that was hidden is written VISIBLE. The validator
    withholds `workbook.sheet-hidden` in exactly that case.
    """
    states: "list[bool]" = []
    for index in range(sheets):
        number = index + 1
        if number < chosen:
            states += [True]
            continue
        if number == chosen:
            states += [chosen_hidden]
            continue
        states += [False]
    showing = False
    for state in states:
        if not state:
            showing = True
    if not showing and states:
        # Nothing would be visible: show a sheet that is not the table's
        # where there is one, and the table's own where there is not.
        last = len(states) - 1
        if last == chosen - 1 and last > 0:
            last = last - 1
        states[last] = False
    return states


def _workbook_part(
    sheet_names: "list[str]", hidden: "list[bool]", epoch_1904: bool
) -> str:
    """The workbook: every sheet in its place, its state, and the epoch."""
    text = _DECLARATION + f'<workbook xmlns="{_MAIN}" xmlns:r="{_RELS}">'
    if epoch_1904:
        text = text + '<workbookPr date1904="1"/>'
    text = text + "<sheets>"
    for index in range(len(sheet_names)):
        shown = _attribute(sheet_names[index])
        state = ""
        if index < len(hidden) and hidden[index]:
            state = ' state="hidden"'
        text = text + (
            f'<sheet name="{shown}" sheetId="{index + 1}"{state} '
            f'r:id="rId{index + 1}"/>'
        )
    text = text + "</sheets></workbook>"
    return text


def _workbook_rels_part(sheets: int) -> str:
    """What the workbook points at: its sheets, its styles, its strings."""
    text = _DECLARATION + f'<Relationships xmlns="{_PACKAGE}">'
    for number in range(1, sheets + 1):
        text = text + (
            f'<Relationship Id="rId{number}" Type="{_RELS}/worksheet" '
            f'Target="worksheets/sheet{number}.xml"/>'
        )
    following = sheets + 1
    text = text + (
        f'<Relationship Id="rId{following}" Type="{_RELS}/styles" '
        'Target="styles.xml"/>'
        f'<Relationship Id="rId{following + 1}" Type="{_RELS}/sharedStrings" '
        'Target="sharedStrings.xml"/>'
    )
    text = text + "</Relationships>"
    return text


def _root_rels_part() -> str:
    """What the package points at: the workbook and the two property parts."""
    text = _DECLARATION + (
        f'<Relationships xmlns="{_PACKAGE}">'
        f'<Relationship Id="rId1" Type="{_RELS}/officeDocument" '
        'Target="xl/workbook.xml"/>'
        f'<Relationship Id="rId2" Type="{_PACKAGE}/metadata/core-properties" '
        'Target="docProps/core.xml"/>'
        f'<Relationship Id="rId3" Type="{_RELS}/extended-properties" '
        'Target="docProps/app.xml"/>'
        "</Relationships>"
    )
    return text


def _content_types_part(sheets: int, table: bool) -> str:
    """What each part of the package is. No macro type is ever written."""
    text = _DECLARATION + f'<Types xmlns="{_TYPES}">'
    text = text + (
        '<Default Extension="rels" ContentType="application/vnd.'
        'openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        f'<Override PartName="/xl/workbook.xml" ContentType="{_SHEET_TYPE}"/>'
    )
    for number in range(1, sheets + 1):
        text = text + (
            f'<Override PartName="/xl/worksheets/sheet{number}.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.'
            'spreadsheetml.worksheet+xml"/>'
        )
    text = text + (
        '<Override PartName="/xl/styles.xml" ContentType="application/vnd.'
        'openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        '<Override PartName="/xl/sharedStrings.xml" ContentType='
        '"application/vnd.openxmlformats-officedocument.spreadsheetml.'
        'sharedStrings+xml"/>'
    )
    if table:
        text = text + (
            '<Override PartName="/xl/tables/table1.xml" ContentType='
            '"application/vnd.openxmlformats-officedocument.spreadsheetml.'
            'table+xml"/>'
        )
    text = text + (
        '<Override PartName="/docProps/core.xml" ContentType="application/'
        'vnd.openxmlformats-package.core-properties+xml"/>'
        '<Override PartName="/docProps/app.xml" ContentType="application/'
        'vnd.openxmlformats-officedocument.extended-properties+xml"/>'
    )
    text = text + "</Types>"
    return text


def _sheet_rels_part() -> str:
    """What a sheet carrying a defined table points at."""
    text = _DECLARATION + (
        f'<Relationships xmlns="{_PACKAGE}">'
        f'<Relationship Id="rId1" Type="{_RELS}/table" '
        'Target="../tables/table1.xml"/>'
        "</Relationships>"
    )
    return text


def _stores_dates(column: "contract.WorkbookColumn") -> bool:
    """Whether the description says this column stores dates as ISO text.

    The one question `_dates_as_day_counts` needs answered before it
    trusts an allocation (plan P4-D284): a published count of `date`
    cells above nought, or a value class of `date` where the counts were
    withheld. A census that merely does not DENY date storage is not it,
    because a withheld census lets any spelling that fits take the class.

    Guarantees: accepts one column's published workbook block; returns a
    bool. Determinism: a fixed function of it. Raises nothing. No I/O.
    """
    counted = column.cell_classes[dialect.SHEET_CELL_DATE]
    if isinstance(counted, int):
        return counted > 0
    return column.value_class == dialect.SHEET_CELL_DATE


def _onto_the_calendar(own: "tuple[str, ...]") -> "tuple[str, ...]":
    """A date-storing column's cells brought onto the calendar (P4-D291).

    `dialect.sheet_date_on_the_calendar` per cell: a cell that is not a
    date's shape, and one that already names a day, come back exactly as
    they came.
    """
    out: "list[str]" = []
    for text in own:
        out += [dialect.sheet_date_on_the_calendar(text)]
    return tuple(out)


def _dates_as_day_counts(
    column: "contract.WorkbookColumn",
    own: "tuple[str, ...]",
    epoch_1904: bool,
    stored: "tuple[str, ...]" = (),
) -> "tuple[tuple[str, ...], tuple[str, ...]]":
    """A column's dates written back as the day counts a workbook stores.

    THE OTHER HALF OF READING A DATE CELL AS ITS DATE (repair of the
    stage-2b integration; `dialect.sheet_serial_moment`). The reader
    hands the column machinery `2024-03-01` for a day count wearing a
    date format, so the generator writes dates; a workbook stores a day
    count, and a date written as TEXT would read back as text in every
    reader. Where the description publishes date or datetime formats
    for this column, each cell holding the reader's own spelling of a
    date is written as its day count, and the kind of date it was is
    handed back beside it so the right format can be put on it. A column
    publishing no date format is returned exactly as it came.

    A CELL THE CENSUS STORES AS A DATE IS NOT CONVERTED (plan P4-D284,
    the repair of review item 5 of the files review of 2026-09-18).
    ``stored`` is the storage class each cell has already been allocated
    (`cell_classes`), and the day count is a NUMBER's spelling: it is
    written only where the cell is to be stored as a number. A workbook
    that stores its dates as ISO text (`t="d"`, class `date`, plan
    P4-D168) publishes a census of date cells, and converting those
    first left the ISO spelling nowhere to be found -- so no cell fitted
    the date class, the whole column fell through to text, and every
    reader handed back strings such as `"45315"`. MEASURED at a floor of
    five on 120 `t="d"` cells wearing `yyyy-mm-dd`: the source came back
    as dates and the twin as those strings, describing the twin again
    turned the column's role from `datetime` into `count`, and the twin
    missed its storage class, its value class, its role, its statistical
    type and its numeric counts while the source missed nothing. Left
    empty, every cell is offered for conversion, which is what a column
    stored as day counts wants.

    AND THE CENSUS HAS TO SAY SO, NOT MERELY FAIL TO DENY IT. The caller
    passes the allocation only where the column PUBLISHES date storage
    (`_stores_dates`). Where the census withheld its counts, a cell no
    count claims is allocated the first withheld class its spelling
    fits, and the twin's own spelling of a date fits `date` -- so a
    column of ordinary day counts wearing a date format, whose census
    the floor held back, was allocated date storage it never had and
    kept the ISO text. Measured on the study's titled book at a floor of
    eleven: 59 of the twin's date cells changed from `<v>45343</v>` to
    `t="d"` holding `2024-02-21`, and the twin missed
    `workbook.value-class`.
    """
    wants_dates = False
    for kind in (dialect.SHEET_FORMAT_DATE, dialect.SHEET_FORMAT_DATETIME):
        if _wanted(column.format_kinds, kind) > 0:
            wants_dates = True
    if dialect.sheet_format_kind(column.format_code) in (
        dialect.SHEET_FORMAT_DATE, dialect.SHEET_FORMAT_DATETIME
    ):
        wants_dates = True
    out: "list[str]" = []
    dated: "list[str]" = []
    for index in range(len(own)):
        text = own[index]
        kept = (
            index < len(stored)
            and stored[index] == dialect.SHEET_CELL_DATE
        )
        if not wants_dates or not text or kept:
            out += [text]
            dated += [""]
            continue
        serial = dialect.sheet_moment_serial(text, epoch_1904)
        if not serial:
            out += [text]
            dated += [""]
            continue
        out += [serial]
        dated += [dialect.sheet_moment_kind(text)]
    return tuple(out), tuple(dated)


def _members(
    profile: "contract.Profile", twin: "generation.Twin"
) -> "list[tuple[str, str]]":
    """Every part of the twin's package, in the one fixed order.

    THE ORDER IS PART OF THE DETERMINISM. The members are written in
    this order and each is given one fixed moment rather than the clock,
    so the same description and the same seed give the same bytes.
    """
    form = profile.source.workbook
    if form is None:
        raise TypeError(
            "internal check: a workbook twin was asked of a description "
            "that records no workbook"
        )
    names = twin.names
    n_rows = twin.n_rows
    write_header = twin.write_header
    width = len(names)

    # One style per distinct published format code, with the general
    # format standing first so that an unstyled cell is still right.
    codes: "list[str]" = ["General"]
    style_of: "dict[str, int]" = {"General": 0}
    classes: "list[tuple[str, ...]]" = []
    cells: "list[tuple[str, ...]]" = []
    dates: "list[tuple[str, ...]]" = []
    epoch_1904 = form.date_system == dialect.SHEET_DATE_SYSTEM_1904
    # THE STORAGE CLASS IS ALLOCATED BEFORE THE CONVERSION, AND SETTLED
    # AFTER IT (plan P4-D284). The first pass asks the census which
    # cells are stored as ISO date text, because only their own
    # spelling can answer that; those cells keep it, every other date
    # becomes the day count a workbook stores, and the second pass
    # settles the classes over the cells as they will be written.
    for index in range(width):
        column = form.columns[index]
        written = tuple(twin.columns[index])
        stores_dates = _stores_dates(column)
        if stores_dates:
            written = _onto_the_calendar(written)
        held = cell_classes(
            column.cell_classes, written, column.value_class
        )
        own, dated = _dates_as_day_counts(
            column, written, epoch_1904, held if stores_dates else (),
        )
        cells += [own]
        dates += [dated]
        classes += [
            cell_classes(column.cell_classes, own, column.value_class)
        ]

    items: "list[str]" = []
    places: "dict[str, int]" = {}
    rows_above = _placeholder_rows(form.rows_above_header, width)
    # NOTHING WHERE THE FLOOR HELD THE COUNT BACK. `empty_rows_inside`
    # counts records of the table, so the smallest group holds it like
    # every other count of rows, and a description that publishes none
    # asks the twin for none rather than for zero of them.
    wanted_empty = 0
    if form.empty_rows_inside is not None:
        wanted_empty = form.empty_rows_inside
    classes, cells, dates = _aligned_for_empty_records(
        classes, cells, n_rows, wanted_empty, dates
    )
    empty_places = _empty_row_places(classes, n_rows, wanted_empty)

    # ONE STYLE PER CELL, worked out after the cells have settled: a
    # column may hold a mixture of format kinds and the census publishes
    # a count for each, so the style is a fact about the cell and not
    # about the column.
    styles: "list[tuple[int, ...]]" = []
    for index in range(width):
        column = form.columns[index]
        kinds = cell_format_kinds(
            column.format_kinds, classes[index], column.format_code,
            dates[index],
        )
        row_styles: "list[int]" = []
        for row in range(len(kinds)):
            code = _code_for_kind(kinds[row], column.format_code)
            if code not in style_of:
                style_of[code] = len(codes)
                codes += [code]
            found = style_of[code]
            if not isinstance(found, int):
                raise TypeError("internal check: a style was not a number")
            row_styles += [found]
        styles += [tuple(row_styles)]
    table = form.defined_table

    published_names: "list[str | None]" = []
    for index in range(form.sheet_count):
        published: "str | None" = None
        if index < len(form.sheet_names):
            published = form.sheet_names[index]
        published_names += [published]
    # ONE ALLOCATION, SHARED WITH THE VALIDATOR (`dialect.twin_sheet_names`;
    # repair of landing 2b.10). The writer used to hand out neutral names
    # in sheet order and add an underscore on a collision, which renamed
    # a sheet whose name the description PUBLISHES -- ('Cohort extract',
    # 'Sheet1') came back as 'Sheet1' and 'Sheet1_' -- and the validator
    # had no way to know what name a conforming twin should carry, so it
    # reported every withheld name MISSED.
    sheet_names: "list[str]" = []
    for name in dialect.twin_sheet_names(tuple(published_names)):
        sheet_names += [name]

    chosen = form.sheet_position
    if chosen < 1 or chosen > len(sheet_names):
        chosen = 1
    hidden = _hidden_states(len(sheet_names), chosen, form.sheet_hidden)

    parts: "list[tuple[str, str]]" = []
    for index in range(len(sheet_names)):
        number = index + 1
        if number != chosen:
            extent: "tuple[int, int] | None" = None
            if index < len(form.sheet_extents):
                extent = form.sheet_extents[index]
            parts += [
                (
                    f"xl/worksheets/sheet{number}.xml",
                    _other_sheet_part(extent, items, places),
                )
            ]
            continue
        parts += [
            (
                f"xl/worksheets/sheet{number}.xml",
                _sheet_part(
                    names,
                    cells,
                    classes,
                    styles,
                    n_rows,
                    write_header,
                    len(codes),
                    rows_above,
                    empty_places,
                    form.trailing_blank_rows,
                    form.trailing_blank_columns,
                    form.frozen_rows,
                    form.autofilter,
                    table,
                    items,
                    places,
                ),
            )
        ]

    first_row = rows_above + 1
    last_row = rows_above + (1 if write_header else 0) + n_rows
    members: "list[tuple[str, str]]" = [
        ("[Content_Types].xml", _content_types_part(len(sheet_names), table)),
        ("_rels/.rels", _root_rels_part()),
        ("docProps/app.xml", _app_part()),
        ("docProps/core.xml", _core_part()),
        (
            "xl/workbook.xml",
            _workbook_part(
                sheet_names,
                hidden,
                form.date_system == dialect.SHEET_DATE_SYSTEM_1904,
            ),
        ),
        ("xl/_rels/workbook.xml.rels", _workbook_rels_part(len(sheet_names))),
        ("xl/styles.xml", _styles_part(tuple(codes))),
        ("xl/sharedStrings.xml", _shared_strings_part(items)),
    ]
    for name, data in parts:
        members += [(name, data)]
    if table:
        members += [
            (
                f"xl/worksheets/_rels/sheet{chosen}.xml.rels",
                _sheet_rels_part(),
            ),
            (
                "xl/tables/table1.xml",
                _table_part(names, first_row, last_row, form.autofilter),
            ),
        ]
    return members


def workbook_members(
    profile: "contract.Profile", twin: "generation.Twin"
) -> "list[tuple[str, str]]":
    """The twin as the parts of a spreadsheet package (plan P4-D79).

    Guarantees:

    - Inputs: one description loaded by `contract.load_profile` whose
      `source.workbook` is not None, and the twin `generation.generate`
      built from it. Nothing else: no path, no file, no table.
    - Determinism: a fixed function of those two, on every platform.
      Nothing here reads a clock or a random source.
    - Errors raised: TypeError where the description records no
      workbook, which is a defect in the caller.
    - Boundary: nothing is opened, read or written. The parts are handed
      back and `writing.write_workbook_file` puts them on disk, which is
      what keeps every write this package makes in one module.

    WHAT DECIDES EACH CELL. The generator is table-blind and produced
    this column's cells as text. `cell_classes` decides what each of
    those cells IS in the file, from the census the description
    publishes -- so a column whose cells were all TEXT is written as
    text even where every one of them looks like a number, and a column
    whose cells were numbers wearing a date format is written as numbers
    wearing that format. That is what makes a reader return the same
    column types on the twin as on the source.
    """
    return _members(profile, twin)
