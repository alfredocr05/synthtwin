"""The workbook writer as it stood before plan P4-D411, frozen as text, and its cases.

Plan P4-D411 writes the workbook twin's sheet as a stream: rows made
one at a time and handed to the zip member as they come, where the
writer of b075342a grew ONE text a row at a time (`text = text + ...`,
a copy of the whole sheet per row) and handed the zip writer whole
texts (`writestr`). The new writer must give the SAME BYTES wherever
the old one finishes. The old one is kept here as fixed text, the
manner of `tests/stage4_as_built.py`, so nothing reads the product's
source to build it and a change of meaning made to the product cannot
reach the reference too:

- `SHEET_PART` is `sheetwriting._sheet_part` exactly as b075342a shipped it;
- `MEMBERS` is `sheetwriting._members` exactly as b075342a shipped it,
  the function that put the parts in order and called it;
- `as_built_file` is the zip loop of b075342a's
  `writing.write_workbook_file`, every part written by `writestr`.

Both texts are compiled into a COPY of `sheetwriting`'s own names, so
the helpers they call (`_cell`, `_place_of`, `_shared_strings_part`,
`_other_sheet_part` and the rest, which this landing does not change)
are today's.

THE CASES are the ones K-S4-22 names: the five workbook goldens of
`tests/reference/generation-document-vectors.json` (method G2.2, the
oracle's parts), the workbook battery of `tests/workbooks.py` and
`tests/kpi_shapes.py`, lane E0a's zoo workbook (`surveys.xlsx`) and a
seeded wide table, each described by the real producer and generated
by the real generator.
"""

import io
import pathlib
import random
import struct
import typing
import zipfile
import zlib

import fixtures
import health_zoo
import kpi_shapes
import workbooks
from synthtwin import (
    contract,
    dialect,
    generation,
    profile,
    reading,
    sheetwriting,
    taxonomy,
    writing,
)

SHEET_PART = '''
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
'''

MEMBERS = '''
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
            told: "frozenset[str]" = frozenset()
            if index < len(profile.columns):
                told = _published_spellings(profile.columns[index])
            written = _onto_the_calendar(written, told)
        held = cell_classes(
            column.cell_classes, written, column.value_class
        )
        own, dated = _dates_as_day_counts(
            column, written, epoch_1904, held if stores_dates else (),
        )
        own = _clocks_as_day_fractions(column, own)
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
'''

# The fixed moment b075342a gave every member.
_MOMENT = (1980, 1, 1, 0, 0, 0)


def _as_built_namespace() -> dict:
    """`sheetwriting`'s names with the two frozen functions compiled over them."""
    names = dict(vars(sheetwriting))
    exec(compile(SHEET_PART, "<as built _sheet_part>", "exec"), names)  # noqa: S102
    exec(compile(MEMBERS, "<as built _members>", "exec"), names)  # noqa: S102
    return names


AS_BUILT = _as_built_namespace()


def as_built_members(described: contract.Profile, twin: generation.Twin) -> list:
    """The package's parts as whole texts, as b075342a made them."""
    return AS_BUILT["_members"](described, twin)


def as_built_file(target: pathlib.Path, members: list) -> bytes:
    """The file b075342a's `write_workbook_file` wrote for ``members``; its bytes."""
    bundle = zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED)
    try:
        for name, data in members:
            entry = zipfile.ZipInfo(name, _MOMENT)
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o600 << 16
            bundle.writestr(entry, data)
    finally:
        bundle.close()
    return target.read_bytes()


def streamed_file(
    target: pathlib.Path, described: contract.Profile, twin: generation.Twin
) -> bytes:
    """The file today's writer writes, the sheet streamed (plan P4-D411); its bytes."""
    writing.write_workbook_file(target, sheetwriting.workbook_stream(described, twin))
    return target.read_bytes()


def both_files(
    folder: pathlib.Path, described: contract.Profile, twin: generation.Twin
) -> "tuple[bytes, bytes]":
    """(b075342a's bytes, today's bytes) for one twin."""
    folder.mkdir(parents=True, exist_ok=True)
    old = as_built_file(folder / "as-built.xlsx", as_built_members(described, twin))
    new = streamed_file(folder / "streamed.xlsx", described, twin)
    return old, new


# -- what "the same file" means on each zlib ------------------------------

# ZLIB-NG WRITES ANOTHER STREAM FOR THE SAME TEXT CUT ELSEWHERE (skeptic 1
# of lane XW, item 3). madler's zlib (1.2.12 on every Python here)
# writes the same deflate stream however its input is cut, measured;
# zlib-ng's medium strategy, the default level, need
# not, and CPython 3.14 on Windows (a CI cell) links zlib-ng, which no
# Python here does. So on zlib-ng the file is compared member by member
# and every header field but the compressed size and the offsets the
# zip64 field carries must agree, with every text; everywhere else the
# files must also be the same bytes.
ZLIB_NG = (
    getattr(zlib, "ZLIBNG_VERSION", None) is not None
    or "zlib-ng" in zlib.ZLIB_VERSION.lower()
    or "zlib-ng" in zlib.ZLIB_RUNTIME_VERSION.lower()
)

# The fields of a member that do not depend on how deflate cut its
# stream, read off zipfile's own record of the central directory.
_MEMBER_FIELDS = (
    "filename",
    "date_time",
    "compress_type",
    "comment",
    "create_system",
    "flag_bits",
    "volume",
    "internal_attr",
    "external_attr",
    "CRC",
    "file_size",
)


# zipfile's version number for a record that carries a zip64 field.
_ZIP64_VERSION = 45


def _stream_free_extra(extra: bytes) -> "tuple[bytes, bool]":
    """``extra`` with what the deflate stream moves taken out of its zip64 field.

    The zip64 field (header id 1) carries, in this order, the member's
    uncompressed size and compressed size when zipfile chose zip64 for the
    sizes, then its header's offset when that lies past zipfile's line.
    The compressed size and the offset move with the deflate stream (on
    zlib-ng, skeptic 2 of lane XW and Codex's item 2), the uncompressed
    size does not. So the field is kept as its id and the uncompressed
    size, and a field that carries the offset alone is dropped. Every
    other field is kept as it is. The second value is True when a zip64
    field carried the offset alone.
    """
    out = b""
    offset_alone = False
    at = 0
    while at + 4 <= len(extra):
        kind, length = struct.unpack("<HH", extra[at : at + 4])
        body = extra[at + 4 : at + 4 + length]
        if kind != 1:
            out += extra[at : at + 4] + body
        elif length >= 16:
            out += b"\x01\x00zip64 size" + body[:8]
        else:
            offset_alone = True
        at += 4 + length
    return out + extra[at:], offset_alone


def _central_record(one: zipfile.ZipInfo, other: zipfile.ZipInfo) -> "list[str]":
    """The central directory's extra and version numbers of a member, compared.

    Read through `_stream_free_extra`. A zip64 field that carries only
    the offset raises the two version numbers to zipfile's zip64 version
    and no further, so where either side has one the numbers are compared
    as raised to it on both sides.
    """
    out: "list[str]" = []
    one_extra, one_alone = _stream_free_extra(one.extra)
    other_extra, other_alone = _stream_free_extra(other.extra)
    if one_extra != other_extra:
        out += [f"{one.filename}: extra"]
    floor = _ZIP64_VERSION if one_alone or other_alone else 0
    for field in ("create_version", "extract_version"):
        if max(getattr(one, field), floor) != max(getattr(other, field), floor):
            out += [f"{one.filename}: {field}"]
    return out


def _local_header(data: bytes, offset: int) -> "tuple[object, ...]":
    """A member's LOCAL header: every field but the compressed size, and its
    extra with the compressed size taken out of its zip64 field."""
    if data[offset : offset + 4] != b"PK\x03\x04":
        return ("no local header at", offset)
    fields = struct.unpack("<HHHHHIIIHH", data[offset + 4 : offset + 30])
    start = offset + 30 + fields[8]
    extra = data[start : start + fields[9]]
    # (version, flags, method, time, date, crc, -, size, name length, -)
    return fields[:6] + fields[7:9] + (_stream_free_extra(extra)[0],)


def member_differences(old: bytes, new: bytes) -> "list[str]":
    """What two packages differ in, member by member, on any zlib.

    The names in order, the archive comment, every field of
    `_MEMBER_FIELDS`, the central directory's extra and version numbers
    (`_central_record`), every local header field but the compressed
    size, and each member's text: every header field but the compressed
    size and the offsets the zip64 field carries.
    """
    out: "list[str]" = []
    with zipfile.ZipFile(io.BytesIO(old)) as first, zipfile.ZipFile(io.BytesIO(new)) as second:
        if first.comment != second.comment:
            out += ["the archive comment"]
        names = [entry.filename for entry in first.infolist()]
        if names != [entry.filename for entry in second.infolist()]:
            return out + ["the members or their order"]
        for one, other in zip(first.infolist(), second.infolist()):
            for field in _MEMBER_FIELDS:
                if getattr(one, field) != getattr(other, field):
                    out += [f"{one.filename}: {field}"]
            out += _central_record(one, other)
            if _local_header(old, one.header_offset) != _local_header(new, other.header_offset):
                out += [f"{one.filename}: the local header"]
            if first.read(one) != second.read(other):
                out += [f"{one.filename}: the text"]
    return out


def package_differences(old: bytes, new: bytes) -> "list[str]":
    """What two packages differ in: the bytes themselves too, except on zlib-ng."""
    out: "list[str]" = []
    if old != new and not ZLIB_NG:
        out += ["the bytes"]
    return out + member_differences(old, new)


# -- the cases ------------------------------------------------------------


def describe_book(
    folder: pathlib.Path, stem: str, data: bytes, sheet: str = ""
) -> contract.Profile:
    """Write ``data`` as a workbook and describe it with the real producer."""
    folder.mkdir(parents=True, exist_ok=True)
    book = folder / f"{stem}.xlsx"
    book.write_bytes(data)
    settings = taxonomy.Settings()
    document = profile.build_document(
        reading.read_table(
            str(book), sheet=sheet, small_cell_floor=settings.small_cell_floor
        ),
        settings,
        [],
        [],
        [],
    )
    written = fixtures.write_profile(folder, f"{stem}-profile.json", document)
    return contract.load_profile(str(written))


def wide_book(n_rows: int, n_columns: int = 50, seed: int = 20261019) -> bytes:
    """A seeded workbook of ``n_columns`` typed columns, Excel's own way.

    Ten kinds of column in turn: a code with leading zeros, a category,
    free text with a character to escape, a whole number, a decimal, a
    date, a date and time, a boolean, a number stored as text, and a
    column half blank.
    """
    draw = random.Random(seed)
    names = [f"col_{index:02d}" for index in range(n_columns)]
    items: "list[str]" = []
    places: "dict[str, int]" = {}

    def shared(text: str) -> str:
        if text not in places:
            places[text] = len(items)
            items[len(items):] = [text]
        return f"{places[text]}"

    rows = [
        (1, [workbooks.cell(sheetwriting.column_reference(i + 1) + "1", shared(names[i]), "s")
             for i in range(n_columns)])
    ]
    for row in range(n_rows):
        number = row + 2
        cells = []
        for index in range(n_columns):
            reference = sheetwriting.column_reference(index + 1) + f"{number}"
            kind = index % 10
            if kind == 0:
                cells += [workbooks.cell(reference, shared(f"{draw.randrange(10 ** 6):07d}"), "s")]
            elif kind == 1:
                cells += [workbooks.cell(reference, shared(draw.choice(("low", "mid", "high", "unknown"))), "s")]
            elif kind == 2:
                cells += [workbooks.cell(reference, shared(f"note {draw.randrange(400)} & more"), "s")]
            elif kind == 3:
                cells += [workbooks.cell(reference, f"{draw.randrange(-50, 5000)}")]
            elif kind == 4:
                cells += [workbooks.cell(reference, f"{draw.gauss(80, 12):.2f}")]
            elif kind == 5:
                cells += [workbooks.cell(reference, f"{draw.randrange(36000, 46000)}", style=1)]
            elif kind == 6:
                cells += [workbooks.cell(reference, f"{draw.randrange(36000, 46000) + draw.random():.6f}", style=2)]
            elif kind == 7:
                cells += [workbooks.cell(reference, draw.choice(("0", "1")), "b")]
            elif kind == 8:
                cells += [workbooks.cell(reference, shared(f"{draw.randrange(100, 999)}"), "s")]
            elif draw.random() < 0.5:
                cells += [workbooks.cell(reference, f"{draw.randrange(1, 9)}")]
        rows += [(number, cells)]
    last = sheetwriting.column_reference(n_columns) + f"{n_rows + 1}"
    return workbooks.package([
        ("[Content_Types].xml", workbooks._content_types(1, True, False, False)),
        ("_rels/.rels", workbooks._root_rels()),
        ("xl/workbook.xml", workbooks._workbook([("Data", "")])),
        ("xl/_rels/workbook.xml.rels", workbooks._workbook_rels(1, True)),
        ("xl/styles.xml", workbooks._styles()),
        ("xl/sharedStrings.xml", workbooks._shared_strings(items)),
        ("xl/worksheets/sheet1.xml", workbooks.sheet(rows, dimension=f"A1:{last}")),
    ])


# The battery: every workbook of `tests/workbooks.py` and `tests/kpi_shapes.py`
# that the reader describes, by name: (how it is built, the sheet named).
BATTERY: "dict[str, tuple[typing.Callable[[], bytes], str]]" = {
    "plain": (workbooks.plain_book, ""),
    "typed": (workbooks.typed_book, ""),
    "titled": (workbooks.titled_book, ""),
    "hidden_first": (workbooks.hidden_first_book, ""),
    "withheld_name": (workbooks.withheld_name_book, ""),
    "second_sheet": (workbooks.second_sheet_book, "Data"),
    "epoch": (workbooks.epoch_book, ""),
    "subsecond": (workbooks.subsecond_book, ""),
    "inline": (workbooks.inline_book, ""),
    "kept_copy": (lambda: workbooks.two_table_book(keep="Data"), ""),
    "wide_number": (workbooks.wide_number_book, ""),
    "noisy_number": (workbooks.noisy_number_book, ""),
    "study_excel": (lambda: workbooks.study_book(600, 5, "excel"), ""),
    "study_pandas": (lambda: workbooks.study_book(600, 5, "pandas"), ""),
    "study_writexl": (lambda: workbooks.study_book(600, 5, "writexl"), ""),
    "study_table": (lambda: workbooks.study_book(600, 3, "excel", table=True), ""),
    "study_titled_two_sheets": (
        lambda: workbooks.study_book(600, 3, "writexl", sheets=2, titled=True),
        "",
    ),
    "study_1904": (lambda: workbooks.study_book(600, 7, "excel", epoch_1904=True), ""),
    "autofilter": (lambda: kpi_shapes.autofilter_book(True), ""),
    "no_autofilter": (lambda: kpi_shapes.autofilter_book(False), ""),
    "zoo_surveys": (lambda: health_zoo.survey_book(*health_zoo.surveys(400, 3)), ""),
    "wide": (lambda: wide_book(600), ""),
}


# The five workbook goldens of method G2.2: each case's description and
# the twin built by hand from the case's own cells, as
# `tests/test_generation_reference.py::_package_matches` builds them.
GOLDENS = (
    "workbook_sheet",
    "workbook_classes_by_spelling",
    "workbook_as_written",
    "workbook_made_up_dates",
    "workbook_typed_clocks",
)


def golden(name: str, folder: pathlib.Path) -> "tuple[contract.Profile, generation.Twin]":
    """One workbook golden's description and twin."""
    import test_generation_reference as reference

    folder.mkdir(parents=True, exist_ok=True)
    case = reference._document_case(name)
    described = reference._workbook_profile(case, folder)
    columns = tuple(tuple(column) for column in case["cells"])
    rows = tuple(
        tuple(columns[place][row] for place in range(len(columns)))
        for row in range(case["n_rows"])
    )
    twin = generation.Twin(
        names=tuple(case["names"]),
        write_header=case["write_header"],
        n_rows=case["n_rows"],
        columns=columns,
        rows=rows,
        outcomes=(),
        deviations=(),
        approximations=(),
        remarks=(),
        words_drawn=0,
        seed=0,
    )
    return described, twin


def stretched(twin: generation.Twin, n_rows: int) -> generation.Twin:
    """``twin`` with its records repeated in turn to ``n_rows`` rows.

    The large twins of K-S4-22 and the memory bound: describing a
    workbook of 100,000 rows of fifty columns is the reader's work and
    lane XL's, not the writer's, so the writer is handed a twin of the
    size it is measured at, its cells those of a real twin of a seeded
    wide table repeated row by row. Nothing in the writer reads the
    description's row count against the twin's.
    """
    columns = tuple(
        tuple(column[row % twin.n_rows] for row in range(n_rows))
        for column in twin.columns
    )
    return generation.Twin(
        names=twin.names,
        write_header=twin.write_header,
        n_rows=n_rows,
        columns=columns,
        rows=(),
        outcomes=(),
        deviations=(),
        approximations=(),
        remarks=(),
        words_drawn=0,
        seed=twin.seed,
    )


# One pool of cells a kind, so the twin's own cells are a few objects
# repeated and what tracemalloc sees is the writer's.
_POOLS: "tuple[tuple[str, tuple[str, ...]], ...]" = (
    (dialect.SHEET_CELL_TEXT, ("alpha", "beta & co", "gamma", " spaced ", "delta")),
    (dialect.SHEET_CELL_NUMBER, ("12", "3.25", "-7", "1000000", "0.5")),
    (dialect.SHEET_CELL_DATE, ("2024-01-05", "2023-12-31", "2025-06-30")),
    (dialect.SHEET_CELL_BOOLEAN, ("TRUE", "FALSE")),
    (dialect.SHEET_CELL_NUMBER, ("45291", "45292.5", "45300.25")),
    (dialect.SHEET_CELL_TEXT, ("00123", "00456", "07789", "A-1", "B-2", "C-3")),
    (dialect.SHEET_CELL_BLANK, ("",)),
    (dialect.SHEET_CELL_EMPTY, ("",)),
    (dialect.SHEET_CELL_ERROR, ("#N/A",)),
    (dialect.SHEET_CELL_NUMBER, ("1", "2", "3", "4", "5", "6", "7", "8", "9")),
)


def sheet_arguments(n_rows: int, width: int = 50) -> tuple:
    """`_sheet_pieces`'s arguments for a sheet of ``n_rows`` rows of ``width`` columns.

    The columns are held as `_sheet_pieces` reads them since plan P4-D415
    (`sheetwriting.held_sheet_columns`): the cells by `twinstore`, the
    classes and the styles a byte a cell.
    """
    names = tuple(f"column_{index:02d}" for index in range(width))
    cells: "list[tuple[str, ...]]" = []
    classes: "list[tuple[str, ...]]" = []
    styles: "list[tuple[int, ...]]" = []
    for index in range(width):
        kind, pool = _POOLS[index % len(_POOLS)]
        cells += [tuple(pool[(row * 7 + index) % len(pool)] for row in range(n_rows))]
        classes += [(kind,) * n_rows]
        styles += [((index % 3),) * n_rows]
    held_cells, held_classes, held_styles = sheetwriting.held_sheet_columns(
        cells, classes, styles
    )
    items: "list[str]" = []
    places: "dict[str, int]" = {}
    return (
        names, held_cells, held_classes, held_styles, n_rows, True, 3, 0, {}, 0, 0, 1,
        True, False, items, places,
    )
