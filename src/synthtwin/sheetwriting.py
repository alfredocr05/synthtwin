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
    """One piece of text as XML content."""
    if not isinstance(text, str):
        raise TypeError("internal check: a cell's text was not text")
    out = text
    out = out.replace("&", "&amp;")
    out = out.replace("<", "&lt;")
    out = out.replace(">", "&gt;")
    out = out.replace('"', "&quot;")
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


def _all_figures(text: str) -> bool:
    """Whether every character is an ASCII digit, and there is one."""
    if not text:
        return False
    for character in text:
        place = ord(character)
        if place < 48 or place > 57:
            return False
    return True


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
    """
    if not isinstance(text, str):
        raise TypeError("internal check: a cell's text was not text")
    if not text:
        return ""
    body = text
    if body[:1] in ("-", "+"):
        body = body[1:]
    mantissa = body
    exponent = ""
    place = mantissa.find("e")
    if place < 0:
        place = mantissa.find("E")
    if place >= 0:
        exponent = mantissa[place + 1 :]
        mantissa = mantissa[:place]
    if exponent:
        if exponent[:1] in ("-", "+"):
            exponent = exponent[1:]
        if not _all_figures(exponent):
            return ""
    point = mantissa.find(".")
    if point >= 0:
        whole = mantissa[:point]
        fraction = mantissa[point + 1 :]
        if whole and not _all_figures(whole):
            return ""
        if fraction and not _all_figures(fraction):
            return ""
        if not whole and not fraction:
            return ""
        return text
    if not _all_figures(mantissa):
        return ""
    return text


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
_VALUE_CLASSES = (
    dialect.SHEET_CELL_ERROR,
    dialect.SHEET_CELL_BOOLEAN,
    dialect.SHEET_CELL_NUMBER,
    dialect.SHEET_CELL_TEXT,
)


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


def _leading(census: "dict[str, int | None]", among: "tuple[str, ...]") -> str:
    """Which of these classes the column holds most of.

    Ties are broken by the order of the tuple, which is fixed, so this
    is a function of the description and not of a dictionary's order.
    """
    best = among[len(among) - 1]
    seen = -1
    for kind in among:
        count = _wanted(census, kind)
        if count > seen:
            seen = count
            best = kind
    return best


def cell_classes(
    census: "dict[str, int | None]", cells: "tuple[str, ...]"
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
    string -- and a cell holding text takes one of the four that hold a
    value. Within each group the published counts are handed out in row
    order and the column's leading class takes the remainder, so a
    column whose census is entirely one class is written entirely that
    way and a census that does not add up cannot leave a cell classless.

    The number class is handed out to the cells that CAN be written as a
    number first (`number_spelling`), so a mixed column does not spend
    its number cells on text that would have to fall back.
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
    while at < len(empty_order):
        out[empty_order[at]] = leading_nothing
        at = at + 1

    # The number class first, and only to cells that can carry it.
    numeric: "list[int]" = []
    other: "list[int]" = []
    for index in full_order:
        if number_spelling(cells[index]):
            numeric += [index]
            continue
        other += [index]
    taken: "dict[int, bool]" = {}
    left = _wanted(census, dialect.SHEET_CELL_NUMBER)
    for index in numeric:
        if left <= 0:
            break
        out[index] = dialect.SHEET_CELL_NUMBER
        taken[index] = True
        left = left - 1

    leading_value = _leading(census, _VALUE_CLASSES)
    waiting: "list[int]" = []
    for index in full_order:
        if index not in taken:
            waiting += [index]
    at = 0
    for kind in _VALUE_CLASSES:
        if kind == dialect.SHEET_CELL_NUMBER:
            continue
        left = _wanted(census, kind)
        while left > 0 and at < len(waiting):
            out[waiting[at]] = kind
            at = at + 1
            left = left - 1
    while at < len(waiting):
        out[waiting[at]] = leading_value
        at = at + 1
    return tuple(out)


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

    Every code here came from the description and every one of them is
    one of `dialect.SHEET_FORMAT_CODES`, which is Excel's own published
    vocabulary and synthtwin's own. A code of the person's is never
    written, because one is never published.
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
                f'formatCode="{_escaped(customs[index])}"/>'
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
    census: "dict[str, int | None]", classes: "tuple[str, ...]"
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
    that ARE written, in row order, and plain takes the rest.
    """
    written: "list[int]" = []
    for index in range(len(classes)):
        if classes[index] != dialect.SHEET_CELL_ABSENT:
            written += [index]
    out: "list[str]" = []
    for _index in range(len(classes)):
        out += [dialect.SHEET_FORMAT_PLAIN]
    at = 0
    for kind in dialect.SHEET_FORMAT_KINDS:
        if kind == dialect.SHEET_FORMAT_PLAIN:
            continue
        left = _wanted(census, kind)
        while left > 0 and at < len(written):
            out[written[at]] = kind
            at = at + 1
            left = left - 1
    return tuple(out)


def _code_for_kind(kind: str, published: str) -> str:
    """The code a cell of this kind is written with.

    The column's own published code is used for the kind it IS, so a
    column whose dates were written `mm-dd-yy` keeps that spelling; a
    kind the published code is not gets the canonical code of its own
    kind, which is how a mixture is written back at all.
    """
    if kind in dialect.SHEET_FORMAT_CODE_KINDS:
        pass
    if published in dialect.SHEET_FORMAT_CODE_KINDS:
        found = dialect.SHEET_FORMAT_CODE_KINDS[published]
        if isinstance(found, str) and found == kind:
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
) -> "tuple[list[tuple[str, ...]], list[tuple[str, ...]]]":
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
    """
    if wanted <= 0 or not classes:
        return (classes, cells)
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
        return (classes, cells)

    targets: "dict[int, bool]" = {}
    for row in range(wanted):
        targets[row] = True

    out_classes: "list[tuple[str, ...]]" = []
    out_cells: "list[tuple[str, ...]]" = []
    for index in range(len(classes)):
        kinds: "list[str]" = []
        for kind in classes[index]:
            kinds += [kind]
        values: "list[str]" = []
        for value in cells[index]:
            values += [value]
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
            kinds[row] = kinds[other]
            values[row] = values[other]
            kinds[other] = held_kind
            values[other] = held_value
        out_classes += [tuple(kinds)]
        out_cells += [tuple(values)]
    return (out_classes, out_cells)


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
        shown = _escaped(_cleaned(names[index]))
        text = text + f'<tableColumn id="{index + 1}" name="{shown}"/>'
    text = text + "</tableColumns>"
    text = text + (
        '<tableStyleInfo name="TableStyleMedium2" showFirstColumn="0" '
        'showLastColumn="0" showRowStripes="1" showColumnStripes="0"/>'
    )
    text = text + "</table>"
    return text


def _workbook_part(
    sheet_names: "list[str]", epoch_1904: bool
) -> str:
    """The workbook: every sheet in its place, and the date system."""
    text = _DECLARATION + f'<workbook xmlns="{_MAIN}" xmlns:r="{_RELS}">'
    if epoch_1904:
        text = text + '<workbookPr date1904="1"/>'
    text = text + "<sheets>"
    for index in range(len(sheet_names)):
        shown = _escaped(sheet_names[index])
        text = text + (
            f'<sheet name="{shown}" sheetId="{index + 1}" '
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
    for index in range(width):
        column = form.columns[index]
        own = tuple(twin.columns[index])
        cells += [own]
        classes += [cell_classes(column.cell_classes, own)]

    items: "list[str]" = []
    places: "dict[str, int]" = {}
    rows_above = _placeholder_rows(form.rows_above_header, width)
    classes, cells = _aligned_for_empty_records(
        classes, cells, n_rows, form.empty_rows_inside
    )
    empty_places = _empty_row_places(classes, n_rows, form.empty_rows_inside)

    # ONE STYLE PER CELL, worked out after the cells have settled: a
    # column may hold a mixture of format kinds and the census publishes
    # a count for each, so the style is a fact about the cell and not
    # about the column.
    styles: "list[tuple[int, ...]]" = []
    for index in range(width):
        column = form.columns[index]
        kinds = cell_format_kinds(column.format_kinds, classes[index])
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

    sheet_names: "list[str]" = []
    taken: "dict[str, bool]" = {}
    for index in range(form.sheet_count):
        published: "str | None" = None
        if index < len(form.sheet_names):
            published = form.sheet_names[index]
        name = published if published else dialect.neutral_sheet_name(index + 1)
        while name in taken:
            name = name + "_"
        taken[name] = True
        sheet_names += [name]

    chosen = form.sheet_position
    if chosen < 1 or chosen > len(sheet_names):
        chosen = 1

    parts: "list[tuple[str, str]]" = []
    for index in range(len(sheet_names)):
        number = index + 1
        if number != chosen:
            # A sheet that is not the table's is written EMPTY. Its name
            # is kept where the name may be published, because code that
            # names a sheet has to find it; nothing of what it held is.
            empty = _DECLARATION + (
                f'<worksheet xmlns="{_MAIN}" xmlns:r="{_RELS}">'
                '<dimension ref="A1"/>'
                '<sheetViews><sheetView workbookViewId="0"/></sheetViews>'
                "<sheetFormatPr/><sheetData/></worksheet>"
            )
            parts += [
                (f"xl/worksheets/sheet{number}.xml", empty)
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
                sheet_names, form.date_system == dialect.SHEET_DATE_SYSTEM_1904
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
