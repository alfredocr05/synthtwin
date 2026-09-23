"""Seeded neutral WORKBOOK builders for the landing 2b.10 tests (plan D13).

No data-format file is ever committed, and a workbook is a data-format
file, so every workbook a test reads is assembled here from code, by the
standard library alone, with fixed zip timestamps and a fixed member
order. The same call produces the same bytes on every machine.

WHY THE PARTS ARE WRITTEN OUT RATHER THAN DRIVEN OUT OF A LIBRARY. The
measured study behind this landing found that both Python writers
corrupt what a test most needs to pin: openpyxl turns any text starting
with `=` into a formula and stores no cached value, and xlsxwriter turns
such text into a formula with a cached 0 and turns `http://...` text
into a hyperlink. A fixture built by either could not hold the cells
this landing exists to read correctly. So the XML is written here, in
the shapes the study measured Excel, pandas, openpyxl and R actually
emitting, and the round-trip tests read the result back with openpyxl
and pandas as INDEPENDENT ORACLES to show the fixture is a real
workbook rather than one only synthtwin can read.

The vocabulary is deliberately neutral and made up on the spot.
"""

import zipfile

from synthtwin import parsing

# A fixed moment for every member, so the bytes do not carry the clock.
_WHEN = (1980, 1, 1, 0, 0, 0)

_DECLARATION = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
_RELS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def _escaped(text: str) -> str:
    """One piece of text as XML content."""
    out = text
    out = out.replace("&", "&amp;")
    out = out.replace("<", "&lt;")
    out = out.replace(">", "&gt;")
    out = out.replace('"', "&quot;")
    return out


def package(members: "list[tuple[str, bytes]]") -> bytes:
    """A zip package of these members, in this order, at a fixed moment."""
    import io

    buffer = io.BytesIO()
    bundle = zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED)
    try:
        for name, data in members:
            entry = zipfile.ZipInfo(name, _WHEN)
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o600 << 16
            bundle.writestr(entry, data)
    finally:
        bundle.close()
    return buffer.getvalue()


def _content_types(sheets: int, shared: bool, table: bool, macro: bool) -> bytes:
    kind = "application/vnd.ms-excel.sheet.macroEnabled.main+xml"
    if not macro:
        kind = (
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet.main+xml"
        )
    parts = [
        _DECLARATION,
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/'
        'content-types">',
        '<Default Extension="rels" ContentType="application/vnd.'
        'openxmlformats-package.relationships+xml"/>',
        '<Default Extension="xml" ContentType="application/xml"/>',
        '<Default Extension="bin" ContentType="application/vnd.ms-office.'
        'vbaProject"/>',
        f'<Override PartName="/xl/workbook.xml" ContentType="{kind}"/>',
    ]
    for number in range(1, sheets + 1):
        parts += [
            f'<Override PartName="/xl/worksheets/sheet{number}.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.'
            'spreadsheetml.worksheet+xml"/>'
        ]
    parts += [
        '<Override PartName="/xl/styles.xml" ContentType="application/vnd.'
        'openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
    ]
    if shared:
        parts += [
            '<Override PartName="/xl/sharedStrings.xml" ContentType='
            '"application/vnd.openxmlformats-officedocument.spreadsheetml.'
            'sharedStrings+xml"/>'
        ]
    if table:
        parts += [
            '<Override PartName="/xl/tables/table1.xml" ContentType='
            '"application/vnd.openxmlformats-officedocument.spreadsheetml.'
            'table+xml"/>'
        ]
    parts += ["</Types>"]
    return "".join(parts).encode("utf-8")


def _root_rels() -> bytes:
    return (
        _DECLARATION
        + '<Relationships xmlns="http://schemas.openxmlformats.org/package/'
        '2006/relationships"><Relationship Id="rId1" Type="'
        + _RELS
        + '/officeDocument" Target="xl/workbook.xml"/></Relationships>'
    ).encode("utf-8")


def _workbook_rels(sheets: int, shared: bool) -> bytes:
    parts = [
        _DECLARATION,
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/'
        '2006/relationships">',
    ]
    for number in range(1, sheets + 1):
        parts += [
            f'<Relationship Id="rId{number}" Type="{_RELS}/worksheet" '
            f'Target="worksheets/sheet{number}.xml"/>'
        ]
    following = sheets + 1
    parts += [
        f'<Relationship Id="rId{following}" Type="{_RELS}/styles" '
        'Target="styles.xml"/>'
    ]
    if shared:
        parts += [
            f'<Relationship Id="rId{following + 1}" Type="{_RELS}/'
            'sharedStrings" Target="sharedStrings.xml"/>'
        ]
    parts += ["</Relationships>"]
    return "".join(parts).encode("utf-8")


def _workbook(
    names: "list[tuple[str, str]]",
    epoch_1904: bool = False,
    defined: "list[tuple[str, str]]" = [],
) -> bytes:
    """`names` is (sheet name, state) per sheet, in workbook order."""
    parts = [
        _DECLARATION,
        f'<workbook xmlns="{_MAIN}" xmlns:r="{_RELS}">',
    ]
    if epoch_1904:
        parts += ['<workbookPr date1904="1"/>']
    parts += ["<sheets>"]
    for place in range(len(names)):
        name, state = names[place]
        shown = "" if not state else f' state="{state}"'
        parts += [
            f'<sheet name="{_escaped(name)}" sheetId="{place + 1}"'
            f'{shown} r:id="rId{place + 1}"/>'
        ]
    parts += ["</sheets>"]
    if defined:
        parts += ["<definedNames>"]
        for label, where in defined:
            parts += [
                f'<definedName name="{_escaped(label)}">'
                f"{_escaped(where)}</definedName>"
            ]
        parts += ["</definedNames>"]
    parts += ["</workbook>"]
    return "".join(parts).encode("utf-8")


def _shared_strings(items: "list[str]") -> bytes:
    parts = [
        _DECLARATION,
        f'<sst xmlns="{_MAIN}" count="{len(items)}" '
        f'uniqueCount="{len(items)}">',
    ]
    for item in items:
        if item != item.strip():
            parts += [f'<si><t xml:space="preserve">{_escaped(item)}</t></si>']
        else:
            parts += [f"<si><t>{_escaped(item)}</t></si>"]
    parts += ["</sst>"]
    return "".join(parts).encode("utf-8")


# The number format codes the study measured, in the order the styles
# below give them. Index 0 is the general format.
FORMAT_CODES = (
    "General",
    "yyyy\\-mm\\-dd",
    "yyyy\\-mm\\-dd\\ hh:mm:ss",
    "h:mm",
    "[h]:mm:ss",
    "0.00%",
    '"$"#,##0.00',
    "000000",
    "@",
    "#,##0",
    # A MOMENT TO THE MILLISECOND, appended so every style number above
    # keeps its place. Excel writes the subsecond figures in the format
    # code and the serial carries them as a fraction of a day.
    "yyyy\\-mm\\-dd\\ hh:mm:ss.000",
)


def _styles() -> bytes:
    parts = [
        _DECLARATION,
        f'<styleSheet xmlns="{_MAIN}">',
        f'<numFmts count="{len(FORMAT_CODES) - 1}">',
    ]
    for place in range(1, len(FORMAT_CODES)):
        parts += [
            f'<numFmt numFmtId="{163 + place}" '
            f'formatCode="{_escaped(FORMAT_CODES[place])}"/>'
        ]
    parts += [
        "</numFmts>",
        '<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font>'
        '<font><b/><sz val="11"/><name val="Calibri"/></font></fonts>',
        '<fills count="2"><fill><patternFill patternType="none"/></fill>'
        '<fill><patternFill patternType="gray125"/></fill></fills>',
        '<borders count="1"><border><left/><right/><top/><bottom/>'
        "<diagonal/></border></borders>",
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" '
        'borderId="0"/></cellStyleXfs>',
        f'<cellXfs count="{len(FORMAT_CODES) + 1}">',
        '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>',
    ]
    for place in range(1, len(FORMAT_CODES)):
        parts += [
            f'<xf numFmtId="{163 + place}" fontId="0" fillId="0" '
            'borderId="0" xfId="0" applyNumberFormat="1"/>'
        ]
    # One more: the bold header style, carrying the general format.
    parts += [
        '<xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" '
        'applyFont="1"/>',
        "</cellXfs>",
        '<cellStyles count="1"><cellStyle name="Normal" xfId="0" '
        'builtinId="0"/></cellStyles>',
        "</styleSheet>",
    ]
    return "".join(parts).encode("utf-8")


HEADER_STYLE = len(FORMAT_CODES)


def cell(reference: str, value: str = "", kind: str = "", style: int = 0,
         formula: str = "", cached: bool = True) -> str:
    """One `<c>` element, written the way the study measured Excel writing it."""
    marks = f' r="{reference}"'
    if kind:
        marks = marks + f' t="{kind}"'
    if style:
        marks = marks + f' s="{style}"'
    if formula:
        inner = f"<f>{_escaped(formula)}</f>"
        if cached:
            inner = inner + f"<v>{_escaped(value)}</v>"
        return f"<c{marks}>{inner}</c>"
    if not value and kind != "inlineStr":
        # A styled cell holding nothing: present in the sheet, with no
        # value at all. This is Excel's formatted blank.
        return f"<c{marks}/>"
    if kind == "inlineStr":
        return f"<c{marks}><is><t>{_escaped(value)}</t></is></c>"
    return f"<c{marks}><v>{_escaped(value)}</v></c>"


def sheet(
    rows: "list[tuple[int, list[str]]]",
    dimension: str = "",
    frozen: int = 0,
    autofilter: str = "",
    widths: "list[tuple[int, int, float, bool]]" = [],
    merged: "list[str]" = [],
    table: bool = False,
) -> bytes:
    """One worksheet part from already-written `<c>` elements."""
    parts = [_DECLARATION, f'<worksheet xmlns="{_MAIN}" xmlns:r="{_RELS}">']
    if dimension:
        parts += [f'<dimension ref="{dimension}"/>']
    if frozen:
        parts += [
            '<sheetViews><sheetView workbookViewId="0">'
            f'<pane ySplit="{frozen}" topLeftCell="A{frozen + 1}" '
            'activePane="bottomLeft" state="frozen"/>'
            "</sheetView></sheetViews>"
        ]
    else:
        parts += [
            '<sheetViews><sheetView workbookViewId="0"/></sheetViews>'
        ]
    # `<sheetFormatPr>` carries no attribute here. Excel writes a
    # default row measurement on it and a workbook is perfectly valid
    # without one -- both oracle readers accept these books unchanged --
    # and the word for that measurement is one the decontamination
    # manifest denies. The scanner walks the tracked tree, markup and
    # all, so the fixture says less rather than the manifest saying
    # different.
    parts += ["<sheetFormatPr/>"]
    if widths:
        parts += ["<cols>"]
        for first, last, width, hidden in widths:
            mark = ' hidden="1"' if hidden else ""
            parts += [
                f'<col min="{first}" max="{last}" width="{width}" '
                f'customWidth="1"{mark}/>'
            ]
        parts += ["</cols>"]
    parts += ["<sheetData>"]
    for number, cells in rows:
        if not cells:
            parts += [f'<row r="{number}"/>']
            continue
        parts += [f'<row r="{number}">' + "".join(cells) + "</row>"]
    parts += ["</sheetData>"]
    if autofilter:
        parts += [f'<autoFilter ref="{autofilter}"/>']
    if merged:
        parts += [f'<mergeCells count="{len(merged)}">']
        for span in merged:
            parts += [f'<mergeCell ref="{span}"/>']
        parts += ["</mergeCells>"]
    if table:
        parts += ['<tableParts count="1"><tablePart r:id="rId1"/></tableParts>']
    parts += ["</worksheet>"]
    return "".join(parts).encode("utf-8")


# -- the named shapes the tests read ----------------------------------
#
# Each is a workbook a real exporter writes, in the shapes the study
# measured. `chosen` names the sheet synthtwin should settle on.

SITES = ("North", "South", "East", "West")

# HOW MANY RECORDS THE ORDINARY SHAPES HOLD (plan P4-D341). `synthtwin
# profile` describes no table under `parsing.POPULATION_FLOOR` and
# writes nothing, and none of these shapes is a shape of a ROW COUNT --
# each is about a sheet's furniture, its storage types, its date system
# or its macro project. So each builder writes the floor by default and
# every caller that needs a different length still says so.
BOOK_ROWS = parsing.POPULATION_FLOOR


def _rows_of(n_rows: int, first: int = 2) -> "list[tuple[int, list[str]]]":
    """`n_rows` ordinary records of four columns, starting at row `first`."""
    out: "list[tuple[int, list[str]]]" = []
    for place in range(n_rows):
        number = first + place
        out += [
            (
                number,
                [
                    cell(f"A{number}", f"{place + 1}"),
                    cell(f"B{number}", f"{place % 4}", "s"),
                    cell(f"C{number}", f"{12.5 + place}"),
                    cell(f"D{number}", f"{45296 + place}", "", 1),
                ],
            )
        ]
    return out


def plain_book(n_rows: int = BOOK_ROWS) -> bytes:
    """One visible sheet, a header row, ordinary typed records."""
    strings = ["reading", "site", "amount", "recorded_on"] + list(SITES)
    head = [
        cell("A1", "0", "s"),
        cell("B1", "1", "s"),
        cell("C1", "2", "s"),
        cell("D1", "3", "s"),
    ]
    body: "list[tuple[int, list[str]]]" = [(1, head)]
    for place in range(n_rows):
        number = 2 + place
        body += [
            (
                number,
                [
                    cell(f"A{number}", f"{place + 1}"),
                    cell(f"B{number}", f"{4 + (place % 4)}", "s"),
                    cell(f"C{number}", f"{12.5 + place}"),
                    cell(f"D{number}", f"{45296 + place}", "", 1),
                ],
            )
        ]
    return package(
        [
            ("[Content_Types].xml", _content_types(1, True, False, False)),
            ("_rels/.rels", _root_rels()),
            ("xl/workbook.xml", _workbook([("Data", "")])),
            ("xl/_rels/workbook.xml.rels", _workbook_rels(1, True)),
            ("xl/styles.xml", _styles()),
            ("xl/sharedStrings.xml", _shared_strings(strings)),
            (
                "xl/worksheets/sheet1.xml",
                sheet(body, dimension=f"A1:D{n_rows + 1}"),
            ),
        ]
    )


def typed_book(n_rows: int = BOOK_ROWS) -> bytes:
    """Every cell class the study says a description MUST carry.

    Columns: a text of digits that must stay text, NA-like text, an
    empty-string cell beside an absent one, a boolean, an error, a
    formula with a cached value and one without, an integral number
    beside a fractional one, and a number wearing a format code.

    THE TWO RECORDS THE STUDY WROTE ARE REPEATED to ``n_rows`` (plan
    P4-D341), so the shape -- every cell class, on the rows the study
    put it on -- is unchanged and the table reaches the population
    floor the command describes at.
    """
    strings = [
        "code",
        "note",
        "blank_or_absent",
        "flag",
        "trouble",
        "computed",
        "amount",
        "padded",
        "00123",
        "NA",
        "",
        "007",
        "n/a",
    ]
    head: "list[str]" = []
    for place in range(8):
        head += [cell(f"{chr(65 + place)}1", f"{place}", "s")]
    body: "list[tuple[int, list[str]]]" = [(1, head)]
    for place in range(n_rows):
        number = 2 + place
        if place % 2 == 0:
            body += [
                (
                    number,
                    [
                        cell(f"A{number}", "8", "s"),
                        cell(f"B{number}", "9", "s"),
                        cell(f"C{number}", "10", "s"),
                        cell(f"D{number}", "1", "b"),
                        cell(f"E{number}", "#N/A", "e"),
                        cell(f"F{number}", "40", "", 0, f"A{number}*10", True),
                        cell(f"G{number}", "12.5"),
                        cell(f"H{number}", "123", "", 7),
                    ],
                )
            ]
            continue
        body += [
            (
                number,
                [
                    cell(f"A{number}", "11", "s"),
                    cell(f"B{number}", "12", "s"),
                    cell(f"D{number}", "0", "b"),
                    cell(f"E{number}", "#DIV/0!", "e"),
                    cell(f"F{number}", "", "", 0, f"A{number}*10", False),
                    cell(f"G{number}", "3"),
                    cell(f"H{number}", "4501", "", 7),
                ],
            )
        ]
    return package(
        [
            ("[Content_Types].xml", _content_types(1, True, False, False)),
            ("_rels/.rels", _root_rels()),
            ("xl/workbook.xml", _workbook([("Data", "")])),
            ("xl/_rels/workbook.xml.rels", _workbook_rels(1, True)),
            ("xl/styles.xml", _styles()),
            ("xl/sharedStrings.xml", _shared_strings(strings)),
            (
                "xl/worksheets/sheet1.xml",
                sheet(body, dimension=f"A1:H{n_rows + 1}"),
            ),
        ]
    )


def titled_book(n_rows: int = BOOK_ROWS) -> bytes:
    """Blank rows, a title row and a merged header cell above the names.

    An all-empty row stands inside the data as well, which both readers
    keep as a record of nothing.

    SO IT WRITES ONE ROW MORE THAN IT IS ASKED FOR (repair of landing
    3.2). `n_rows` is how many records HOLD A VALUE, which is what the
    population floor counts and what `BOOK_ROWS` promises; the record
    of nothing stands on top of them, because counting it would be the
    defect that repair closed.
    """
    strings = ["Cohort extract", "reading", "site", "amount", "recorded_on"]
    body: "list[tuple[int, list[str]]]" = [
        (2, [cell("A2", "0", "s")]),
        (
            4,
            [
                cell("A4", "1", "s"),
                cell("B4", "2", "s"),
                cell("C4", "3", "s"),
                cell("D4", "4", "s"),
            ],
        ),
    ]
    for place in range(n_rows + 1):
        number = 5 + place
        if place == 4:
            body += [(number, [])]
            continue
        body += [
            (
                number,
                [
                    cell(f"A{number}", f"{place + 1}"),
                    cell(f"B{number}", f"{12.5 + place}"),
                    cell(f"C{number}", f"{place}"),
                    cell(f"D{number}", f"{45296 + place}", "", 1),
                ],
            )
        ]
    return package(
        [
            ("[Content_Types].xml", _content_types(1, True, False, False)),
            ("_rels/.rels", _root_rels()),
            ("xl/workbook.xml", _workbook([("Data", "")])),
            ("xl/_rels/workbook.xml.rels", _workbook_rels(1, True)),
            ("xl/styles.xml", _styles()),
            ("xl/sharedStrings.xml", _shared_strings(strings)),
            (
                "xl/worksheets/sheet1.xml",
                sheet(
                    body,
                    dimension=f"A1:D{n_rows + 4}",
                    merged=["A2:D2"],
                    frozen=4,
                ),
            ),
        ]
    )


def hidden_first_book(n_rows: int = BOOK_ROWS, notes_cells: int = 1) -> bytes:
    """A hidden sheet first, so the chosen sheet is the second one.

    ``notes_cells`` is how many cells the notes page holds: one by
    default, which is the shape the study measured, and none for the
    control that a twin writing that sheet EMPTY is reported MISSED
    rather than passing (plan P4-D82).
    """
    strings = ["reading", "site", "amount", "recorded_on"] + list(SITES)
    head = [
        cell("A1", "0", "s"),
        cell("B1", "1", "s"),
        cell("C1", "2", "s"),
        cell("D1", "3", "s"),
    ]
    body: "list[tuple[int, list[str]]]" = [(1, head)]
    for place in range(n_rows):
        number = 2 + place
        body += [
            (
                number,
                [
                    cell(f"A{number}", f"{place + 1}"),
                    cell(f"B{number}", f"{4 + (place % 4)}", "s"),
                    cell(f"C{number}", f"{12.5 + place}"),
                    cell(f"D{number}", f"{45296 + place}", "", 1),
                ],
            )
        ]
    held = [(1, [cell("A1", "0", "s")])] if notes_cells else []
    notes = sheet(held, dimension="A1:A1")
    return package(
        [
            ("[Content_Types].xml", _content_types(2, True, False, False)),
            ("_rels/.rels", _root_rels()),
            (
                "xl/workbook.xml",
                _workbook([("Notes", "hidden"), ("Data", "")]),
            ),
            ("xl/_rels/workbook.xml.rels", _workbook_rels(2, True)),
            ("xl/styles.xml", _styles()),
            ("xl/sharedStrings.xml", _shared_strings(strings)),
            ("xl/worksheets/sheet1.xml", notes),
            (
                "xl/worksheets/sheet2.xml",
                sheet(body, dimension=f"A1:D{n_rows + 1}"),
            ),
        ]
    )


def withheld_name_book(n_rows: int = BOOK_ROWS) -> bytes:
    """A workbook whose chosen sheet's name may not be published.

    'Cohort extract' is not one of the generic names this version can
    rebuild from its own vocabulary, so it is WITHHELD -- which is what
    most real research workbooks look like, and the shape whose twin
    failed its own description until the repair of landing 2b.10.
    """
    strings = ["reading", "site", "amount"] + list(SITES)
    head = [cell("A1", "0", "s"), cell("B1", "1", "s"), cell("C1", "2", "s")]
    body: "list[tuple[int, list[str]]]" = [(1, head)]
    for place in range(n_rows):
        number = 2 + place
        body += [
            (
                number,
                [
                    cell(f"A{number}", f"{place + 1}"),
                    cell(f"B{number}", f"{3 + (place % 4)}", "s"),
                    cell(f"C{number}", f"{12.5 + place}"),
                ],
            )
        ]
    other = sheet([(1, [cell("A1", "0", "s")])], dimension="A1:A1")
    return package(
        [
            ("[Content_Types].xml", _content_types(2, True, False, False)),
            ("_rels/.rels", _root_rels()),
            (
                "xl/workbook.xml",
                _workbook([("Cohort extract", ""), ("Sheet2", "")]),
            ),
            ("xl/_rels/workbook.xml.rels", _workbook_rels(2, True)),
            ("xl/styles.xml", _styles()),
            ("xl/sharedStrings.xml", _shared_strings(strings)),
            (
                "xl/worksheets/sheet1.xml",
                sheet(body, dimension=f"A1:C{n_rows + 1}"),
            ),
            ("xl/worksheets/sheet2.xml", other),
        ]
    )


def second_sheet_book(n_rows: int = BOOK_ROWS) -> bytes:
    """Two VISIBLE sheets, the table on the second one.

    Nothing about the file says which sheet holds the table, so reading
    it without `--sheet` lands on the notes page. It is the shape that
    proves `--sheet` is honoured rather than accepted and dropped.
    """
    strings = ["note", "reading", "site", "amount"] + list(SITES)
    notes = sheet([(1, [cell("A1", "0", "s")])], dimension="A1:A1")
    head = [cell("A1", "1", "s"), cell("B1", "2", "s"), cell("C1", "3", "s")]
    body: "list[tuple[int, list[str]]]" = [(1, head)]
    for place in range(n_rows):
        number = 2 + place
        body += [
            (
                number,
                [
                    cell(f"A{number}", f"{place + 1}"),
                    cell(f"B{number}", f"{4 + (place % 4)}", "s"),
                    cell(f"C{number}", f"{12.5 + place}"),
                ],
            )
        ]
    return package(
        [
            ("[Content_Types].xml", _content_types(2, True, False, False)),
            ("_rels/.rels", _root_rels()),
            ("xl/workbook.xml", _workbook([("Notes", ""), ("Data", "")])),
            ("xl/_rels/workbook.xml.rels", _workbook_rels(2, True)),
            ("xl/styles.xml", _styles()),
            ("xl/sharedStrings.xml", _shared_strings(strings)),
            ("xl/worksheets/sheet1.xml", notes),
            (
                "xl/worksheets/sheet2.xml",
                sheet(body, dimension=f"A1:C{n_rows + 1}"),
            ),
        ]
    )


def epoch_book(n_rows: int = BOOK_ROWS) -> bytes:
    """The 1904 date system, which shifts every date by 1,462 days."""
    strings = ["reading", "recorded_on"]
    body: "list[tuple[int, list[str]]]" = [
        (1, [cell("A1", "0", "s"), cell("B1", "1", "s")])
    ]
    for place in range(n_rows):
        number = 2 + place
        body += [
            (
                number,
                [
                    cell(f"A{number}", f"{place + 1}"),
                    cell(f"B{number}", f"{43834 + place}", "", 1),
                ],
            )
        ]
    return package(
        [
            ("[Content_Types].xml", _content_types(1, True, False, False)),
            ("_rels/.rels", _root_rels()),
            ("xl/workbook.xml", _workbook([("Data", "")], epoch_1904=True)),
            ("xl/_rels/workbook.xml.rels", _workbook_rels(1, True)),
            ("xl/styles.xml", _styles()),
            ("xl/sharedStrings.xml", _shared_strings(strings)),
            (
                "xl/worksheets/sheet1.xml",
                sheet(body, dimension=f"A1:B{n_rows + 1}"),
            ),
        ]
    )


def subsecond_book(n_rows: int = 240, figures: bool = True) -> bytes:
    """Moments stored as serials and formatted to the millisecond.

    The shape of the extra review's item 9: a workbook column whose cells
    are numbers, whose format code shows three figures after the second,
    and whose serials carry a thousandth of a second.

    ``figures`` false wears `yyyy-mm-dd hh:mm:ss` instead -- the code
    pandas writes by default -- over the SAME serials, which is the
    other half of that item (plan P4-D259.1): the fraction is stored and
    no figure of the format shows it.
    """
    strings = ["recorded_at"]
    style = len(FORMAT_CODES) - 1 if figures else 2
    body: "list[tuple[int, list[str]]]" = [(1, [cell("A1", "0", "s")])]
    for place in range(n_rows):
        number = 2 + place
        serial = 45300 + place + 0.5 + 0.001 / 86400
        body += [
            (number, [cell(f"A{number}", repr(serial), "", style)])
        ]
    return package(
        [
            ("[Content_Types].xml", _content_types(1, True, False, False)),
            ("_rels/.rels", _root_rels()),
            ("xl/workbook.xml", _workbook([("Data", "")])),
            ("xl/_rels/workbook.xml.rels", _workbook_rels(1, True)),
            ("xl/styles.xml", _styles()),
            ("xl/sharedStrings.xml", _shared_strings(strings)),
            (
                "xl/worksheets/sheet1.xml",
                sheet(body, dimension=f"A1:A{n_rows + 1}"),
            ),
        ]
    )


def inline_book(n_rows: int = BOOK_ROWS) -> bytes:
    """Cells written inline, as pandas with openpyxl writes them."""
    names = ["reading", "site", "amount"]
    head: "list[str]" = []
    for place in range(len(names)):
        head += [cell(f"{chr(65 + place)}1", names[place], "inlineStr")]
    body: "list[tuple[int, list[str]]]" = [(1, head)]
    for place in range(n_rows):
        number = 2 + place
        body += [
            (
                number,
                [
                    cell(f"A{number}", f"{place + 1}"),
                    cell(
                        f"B{number}", SITES[place % 4], "inlineStr"
                    ),
                    cell(f"C{number}", f"{12.5 + place}"),
                ],
            )
        ]
    return package(
        [
            ("[Content_Types].xml", _content_types(1, False, False, False)),
            ("_rels/.rels", _root_rels()),
            ("xl/workbook.xml", _workbook([("Sheet1", "")])),
            ("xl/_rels/workbook.xml.rels", _workbook_rels(1, False)),
            ("xl/styles.xml", _styles()),
            (
                "xl/worksheets/sheet1.xml",
                sheet(body, dimension=f"A1:C{n_rows + 1}"),
            ),
        ]
    )


# -- the hostile shapes -----------------------------------------------
#
# Built here for the same reason the ordinary ones are: the study's own
# hostile files are local evidence and no data-format file is ever
# committed. Each one is the smallest file that exercises exactly one
# refusal, so a test that passes says which cap held.


def doctype_book() -> bytes:
    """A workbook whose stored text carries a document type declaration.

    This is the shape both the entity-expansion and the external-entity
    attacks take, so one refusal answers both. The declaration below
    defines an entity that names a file; nothing must fetch it.
    """
    body = (
        _DECLARATION
        + '<!DOCTYPE sst [<!ENTITY outside SYSTEM "file:///etc/hostname">]>'
        + f'<sst xmlns="{_MAIN}" count="1" uniqueCount="1">'
        + "<si><t>&outside;</t></si></sst>"
    )
    return package(
        [
            ("[Content_Types].xml", _content_types(1, True, False, False)),
            ("_rels/.rels", _root_rels()),
            ("xl/workbook.xml", _workbook([("Data", "")])),
            ("xl/_rels/workbook.xml.rels", _workbook_rels(1, True)),
            ("xl/styles.xml", _styles()),
            ("xl/sharedStrings.xml", body.encode("utf-8")),
            (
                "xl/worksheets/sheet1.xml",
                sheet([(1, [cell("A1", "0", "s")])], dimension="A1:A1"),
            ),
        ]
    )


def far_cell_book() -> bytes:
    """A sheet holding one cell past the last row a spreadsheet has."""
    number = 1_048_577
    body = [(number, [cell(f"A{number}", "1")])]
    return package(
        [
            ("[Content_Types].xml", _content_types(1, False, False, False)),
            ("_rels/.rels", _root_rels()),
            ("xl/workbook.xml", _workbook([("Data", "")])),
            ("xl/_rels/workbook.xml.rels", _workbook_rels(1, False)),
            ("xl/styles.xml", _styles()),
            ("xl/worksheets/sheet1.xml", sheet(body)),
        ]
    )


def wide_cell_book() -> bytes:
    """A sheet holding one cell past the last column a spreadsheet has."""
    body = [(1, [cell("XFE1", "1")])]
    return package(
        [
            ("[Content_Types].xml", _content_types(1, False, False, False)),
            ("_rels/.rels", _root_rels()),
            ("xl/workbook.xml", _workbook([("Data", "")])),
            ("xl/_rels/workbook.xml.rels", _workbook_rels(1, False)),
            ("xl/styles.xml", _styles()),
            ("xl/worksheets/sheet1.xml", sheet(body)),
        ]
    )


def ratio_bomb_book(ratio: int = 4_000) -> bytes:
    """A workbook holding one part that expands far past its packed size."""
    filler = ("<r/>" * 400_000).encode("utf-8")
    body = (
        _DECLARATION
        + f'<worksheet xmlns="{_MAIN}"><sheetData>'
        + "<row r=\"1\"><c r=\"A1\"><v>1</v></c></row>"
        + "</sheetData></worksheet>"
    ).encode("utf-8")
    return package(
        [
            ("[Content_Types].xml", _content_types(1, False, False, False)),
            ("_rels/.rels", _root_rels()),
            ("xl/workbook.xml", _workbook([("Data", "")])),
            ("xl/_rels/workbook.xml.rels", _workbook_rels(1, False)),
            ("xl/styles.xml", _styles()),
            ("xl/worksheets/sheet1.xml", body),
            ("xl/padding.xml", filler),
        ]
    )


def traversal_book() -> bytes:
    """A workbook holding a part named as though it sat outside the file."""
    return package(
        [
            ("[Content_Types].xml", _content_types(1, False, False, False)),
            ("_rels/.rels", _root_rels()),
            ("xl/workbook.xml", _workbook([("Data", "")])),
            ("xl/_rels/workbook.xml.rels", _workbook_rels(1, False)),
            ("xl/styles.xml", _styles()),
            (
                "xl/worksheets/sheet1.xml",
                sheet([(1, [cell("A1", "1")])], dimension="A1:A1"),
            ),
            ("../outside.txt", b"x"),
        ]
    )


def macro_book(n_rows: int = BOOK_ROWS) -> bytes:
    """A macro-enabled workbook: an ordinary table beside a code project."""
    strings = ["reading", "site"] + list(SITES)
    body: "list[tuple[int, list[str]]]" = [
        (1, [cell("A1", "0", "s"), cell("B1", "1", "s")])
    ]
    for place in range(n_rows):
        number = 2 + place
        body += [
            (
                number,
                [
                    cell(f"A{number}", f"{place + 1}"),
                    cell(f"B{number}", f"{2 + (place % 4)}", "s"),
                ],
            )
        ]
    return package(
        [
            ("[Content_Types].xml", _content_types(1, True, False, True)),
            ("_rels/.rels", _root_rels()),
            ("xl/workbook.xml", _workbook([("Data", "")])),
            ("xl/_rels/workbook.xml.rels", _workbook_rels(1, True)),
            ("xl/styles.xml", _styles()),
            ("xl/sharedStrings.xml", _shared_strings(strings)),
            (
                "xl/worksheets/sheet1.xml",
                sheet(body, dimension=f"A1:B{n_rows + 1}"),
            ),
            ("xl/vbaProject.bin", b"\xd0\xcf\x11\xe0" + b"\x00" * 508),
        ]
    )


def all_hidden_book() -> bytes:
    """A workbook whose only sheet is hidden, so none can be chosen."""
    return package(
        [
            ("[Content_Types].xml", _content_types(1, False, False, False)),
            ("_rels/.rels", _root_rels()),
            ("xl/workbook.xml", _workbook([("Notes", "hidden")])),
            ("xl/_rels/workbook.xml.rels", _workbook_rels(1, False)),
            ("xl/styles.xml", _styles()),
            (
                "xl/worksheets/sheet1.xml",
                sheet([(1, [cell("A1", "1")])], dimension="A1:A1"),
            ),
        ]
    )


def two_table_book(n_rows: int = BOOK_ROWS, keep: str = "", third: str = "") -> bytes:
    """Two sheets, each holding a TABLE, which synthtwin cannot twin.

    synthtwin describes ONE table, and the twin writes every other sheet
    with none of the person's cells in it -- so a reader opening the
    second sheet of the twin would meet a frame of withheld cells where
    a table stood. The workbook is refused instead, naming the sheet
    (plan P4-D82).

    ``keep`` names one of the two sheets, `Data` or `Codebook`, and builds
    the COPY the refusal asks for instead: that sheet alone, under its own
    name (owner ruling of 2026-09-17, item 3, plan P4-D203).

    ``third`` names a THIRD sheet holding the same table, between the two
    (repair pass of 2026-09-17): the refusal stops at the first other
    sheet it meets, so its sentence may not speak of "the two sheets".
    """
    strings = ["reading", "site", "amount", "recorded_on"] + list(SITES)
    head = [
        cell("A1", "0", "s"),
        cell("B1", "1", "s"),
        cell("C1", "2", "s"),
        cell("D1", "3", "s"),
    ]
    body: "list[tuple[int, list[str]]]" = [(1, head)] + _rows_of(n_rows)
    page = sheet(body, dimension=f"A1:D{n_rows + 1}")
    if keep:
        return package(
            [
                ("[Content_Types].xml", _content_types(1, True, False, False)),
                ("_rels/.rels", _root_rels()),
                ("xl/workbook.xml", _workbook([(keep, "")])),
                ("xl/_rels/workbook.xml.rels", _workbook_rels(1, True)),
                ("xl/styles.xml", _styles()),
                ("xl/sharedStrings.xml", _shared_strings(strings)),
                ("xl/worksheets/sheet1.xml", page),
            ]
        )
    names = [("Data", ""), ("Codebook", "")]
    if third:
        names = [("Data", ""), (third, ""), ("Codebook", "")]
    return package(
        [
            ("[Content_Types].xml", _content_types(len(names), True, False, False)),
            ("_rels/.rels", _root_rels()),
            ("xl/workbook.xml", _workbook(names)),
            ("xl/_rels/workbook.xml.rels", _workbook_rels(len(names), True)),
            ("xl/styles.xml", _styles()),
            ("xl/sharedStrings.xml", _shared_strings(strings)),
        ]
        + [
            (f"xl/worksheets/sheet{number}.xml", page)
            for number in range(1, len(names) + 1)
        ]
    )


def wide_number_book(n_rows: int = 300) -> bytes:
    """Whole numbers past 2**53, which binary64 cannot hold exactly.

    THE SHAPE OF LANDING 2b.10'S NAMED LIMIT. A register of long
    identifiers or amounts written as NUMBER cells, every one of them
    past the last whole number this format holds exactly, so that the
    value a reader hands back is not the number the person wrote:
    `9007199254740993` reads back as 9007199254740992.0. The limit was
    that such a real workbook failed its own description, and the same
    values as delimited text failed it the same way, so the fixture is
    built here and the delimited control is built beside the test.
    """
    strings = ["record_id", "amount"]
    head = [cell("A1", "0", "s"), cell("B1", "1", "s")]
    body: "list[tuple[int, list[str]]]" = [(1, head)]
    for place in range(n_rows):
        number = 2 + place
        body += [
            (
                number,
                [
                    cell(f"A{number}", f"{place + 1}"),
                    cell(f"B{number}", f"{9007199254740993 + (place % 7)}"),
                ],
            )
        ]
    return package(
        [
            ("[Content_Types].xml", _content_types(1, True, False, False)),
            ("_rels/.rels", _root_rels()),
            ("xl/workbook.xml", _workbook([("Data", "")])),
            ("xl/_rels/workbook.xml.rels", _workbook_rels(1, True)),
            ("xl/styles.xml", _styles()),
            ("xl/sharedStrings.xml", _shared_strings(strings)),
            (
                "xl/worksheets/sheet1.xml",
                sheet(body, dimension=f"A1:B{n_rows + 1}"),
            ),
        ]
    )


def noisy_number_book(n_rows: int = 400, figures: int = 16) -> bytes:
    """One-decimal measurements stored at ``figures`` significant figures.

    THE SHAPE OF THE STAGE-2b INTEGRATION'S BLOCKER. openpyxl and
    pandas store the double 79.1 as `79.09999999999999` (`%.16g`) and
    Excel stores it as `79.099999999999994` (`%.17g`); every reader hands
    both back as 79.1. The values are a seeded walk of one-decimal
    numbers in a plausible range, so a good share of them carry binary
    noise at sixteen figures and most do at seventeen.
    """
    import random

    draw = random.Random(12)
    strings = ["measure"]
    body: "list[tuple[int, list[str]]]" = [(1, [cell("A1", "0", "s")])]
    for place in range(n_rows):
        number = 2 + place
        value = round(max(35.0, draw.gauss(78, 16)), 1)
        body += [(number, [cell(f"A{number}", "%.*g" % (figures, value))])]
    return package(
        [
            ("[Content_Types].xml", _content_types(1, True, False, False)),
            ("_rels/.rels", _root_rels()),
            ("xl/workbook.xml", _workbook([("Data", "")])),
            ("xl/_rels/workbook.xml.rels", _workbook_rels(1, True)),
            ("xl/styles.xml", _styles()),
            ("xl/sharedStrings.xml", _shared_strings(strings)),
            (
                "xl/worksheets/sheet1.xml",
                sheet(body, dimension=f"A1:A{n_rows + 1}"),
            ),
        ]
    )


def compound_file() -> bytes:
    """The opening bytes of a legacy .xls or an encrypted workbook."""
    return b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + bytes(504)


def markup_named_xls() -> bytes:
    """An HTML table exported under a spreadsheet's name, as many are."""
    return (
        "<html><head><meta charset=\"utf-8\"></head><body><table>"
        "<tr><th>reading</th><th>site</th></tr>"
        "<tr><td>1</td><td>North</td></tr>"
        "</table></body></html>"
    ).encode("utf-8")


# -- the study's own shapes, at the sizes a real table comes in --------
#
# Plan P4-D79's gate needs workbooks that are REALISTIC rather than
# minimal: every cell class the study measured, every kind of number
# format it found deciding a reader's type, at the row counts a
# research table actually has, written the three ways the study watched
# them being written. These build them from a seed, so no data-format
# file is ever committed.


def _words(seed: int, count: int) -> "list[int]":
    """`count` whole numbers from a seed, by a written-out recurrence.

    A recurrence of this file's own rather than a library's, so a
    fixture is the same on every machine and in every Python.
    """
    out: "list[int]" = []
    state = (seed * 6364136223846793005 + 1442695040888963407) % (2**64)
    for _place in range(count):
        state = (state * 6364136223846793005 + 1442695040888963407) % (2**64)
        out += [state >> 11]
    return out


# The columns the study says a description MUST carry, with the style
# each wears. The style numbers are indexes into FORMAT_CODES above.
STUDY_COLUMNS = (
    ("record_code", 0),
    ("site", 0),
    ("note", 0),
    ("spare", 0),
    ("flag", 0),
    ("trouble", 0),
    ("reading", 0),
    ("amount", 0),
    ("recorded_on", 1),
    ("stamp", 2),
    ("clock", 3),
    ("elapsed", 4),
    ("share", 5),
    ("cost", 6),
    ("padded", 7),
    ("grouped", 9),
)

_NA_TEXTS = ("NA", "n/a", "NULL", "nan")


def study_book(
    n_rows: int = 200,
    seed: int = 0,
    shape: str = "excel",
    sheets: int = 1,
    titled: bool = False,
    table: bool = False,
    epoch_1904: bool = False,
) -> bytes:
    """A realistic workbook of sixteen typed columns (plan P4-D79).

    ``shape`` is which writer's output this imitates:

    * `excel` -- shared strings and styles, as Excel's own save writes;
    * `pandas` -- a written row index whose header corner is empty,
      which is what `to_excel` produces by default;
    * `writexl` -- inline strings, which is how R's writexl writes text.

    Every column is one the study named: a text code with leading zeros
    that must not become a number, NA-like text that must not become a
    missing value, empty-string cells beside absent ones, a boolean with
    blanks, error cells, dates in the workbook's own epoch, a time, an
    elapsed duration, a percentage, a currency, a padded number and a
    grouped one.
    """
    inline = shape == "writexl"
    indexed = shape == "pandas"
    figures = _words(seed, n_rows * 4)
    names: "list[str]" = []
    for name, _style in STUDY_COLUMNS:
        names += [name]
    texts: "list[str]" = []
    if indexed:
        texts += [""]
    for name in names:
        texts += [name]
    for site in SITES:
        texts += [site]
    for spelling in _NA_TEXTS:
        texts += [spelling]
    codes: "list[str]" = []
    for place in range(n_rows):
        codes += ["%06d" % (place + 1)]
    for code in codes:
        texts += [code]
    texts += [""]
    where: "dict[str, int]" = {}
    for place in range(len(texts)):
        if texts[place] not in where:
            where[texts[place]] = place

    def _shared(value: str) -> int:
        return where[value]

    def _text_cell(reference: str, value: str, style: int = 0) -> str:
        if inline:
            return cell(reference, value, "inlineStr", style)
        return cell(reference, f"{_shared(value)}", "s", style)

    first = 1
    body: "list[tuple[int, list[str]]]" = []
    if titled:
        # A title above the table, then a blank row, as a person types.
        body += [(1, [_text_cell("A1", "Cohort extract")])]
        body += [(2, [])]
        first = 3
    head: "list[str]" = []
    offset = 1 if indexed else 0
    for place in range(len(names)):
        reference = f"{_column(place + 1 + offset)}{first}"
        head += [_text_cell(reference, names[place], HEADER_STYLE)]
    body += [(first, head)]

    for place in range(n_rows):
        number = first + 1 + place
        word = figures[place * 4]
        second = figures[place * 4 + 1]
        line: "list[str]" = []
        if indexed:
            line += [cell(f"A{number}", f"{place}")]
        at = offset
        for index in range(len(STUDY_COLUMNS)):
            name, style = STUDY_COLUMNS[index]
            reference = f"{_column(index + 1 + at)}{number}"
            if name == "record_code":
                line += [_text_cell(reference, codes[place])]
            elif name == "site":
                line += [_text_cell(reference, SITES[word % 4])]
            elif name == "note":
                # NA-like text every few rows, ordinary text otherwise.
                if second % 5 == 0:
                    line += [_text_cell(reference, _NA_TEXTS[word % 4])]
                else:
                    line += [_text_cell(reference, SITES[second % 4])]
            elif name == "spare":
                # An empty-string cell, a styled blank, or nothing at all.
                if word % 3 == 0:
                    line += [_text_cell(reference, "")]
                elif word % 3 == 1:
                    line += [cell(reference, "", "", 8)]
            elif name == "flag":
                if word % 7 == 0:
                    line += [cell(reference, "", "", 8)]
                else:
                    line += [cell(reference, f"{word % 2}", "b")]
            elif name == "trouble":
                if second % 11 == 0:
                    kind = "#N/A" if word % 2 else "#DIV/0!"
                    line += [cell(reference, kind, "e")]
                else:
                    line += [cell(reference, f"{word % 50}")]
            elif name == "reading":
                line += [cell(reference, f"{word % 500}")]
            elif name == "amount":
                line += [cell(reference, f"{(word % 10000) / 100}")]
            elif name == "recorded_on":
                line += [cell(reference, f"{43834 + place % 900}", "", style)]
            elif name == "stamp":
                line += [
                    cell(reference, f"{43834 + place % 900}.5", "", style)
                ]
            elif name == "clock":
                line += [cell(reference, f"0.{word % 899999:06d}", "", style)]
            elif name == "elapsed":
                line += [cell(reference, f"{word % 400}.25", "", style)]
            elif name == "share":
                line += [cell(reference, f"0.{word % 99:02d}", "", style)]
            elif name == "cost":
                line += [cell(reference, f"{word % 90000 / 100}", "", style)]
            elif name == "padded":
                line += [cell(reference, f"{word % 999999}", "", style)]
            else:
                line += [cell(reference, f"{word % 900000}", "", style)]
        body += [(number, line)]

    last = first + n_rows
    width = len(STUDY_COLUMNS) + offset
    span = f"A{first}:{_column(width)}{last}"
    pages: "list[tuple[str, str]]" = [("Data", "")]
    for extra in range(sheets - 1):
        pages += [(f"Sheet{extra + 2}", "")]
    members: "list[tuple[str, bytes]]" = [
        ("[Content_Types].xml", _content_types(len(pages), not inline, table, False)),
        ("_rels/.rels", _root_rels()),
        ("xl/workbook.xml", _workbook(pages, epoch_1904=epoch_1904)),
        ("xl/_rels/workbook.xml.rels", _workbook_rels(len(pages), not inline)),
        ("xl/styles.xml", _styles()),
    ]
    if not inline:
        members += [("xl/sharedStrings.xml", _shared_strings(texts))]
    members += [
        (
            "xl/worksheets/sheet1.xml",
            sheet(
                body,
                dimension=f"A1:{_column(width)}{last}",
                frozen=first,
                autofilter=span if table else "",
                table=table,
            ),
        )
    ]
    for extra in range(sheets - 1):
        members += [
            (
                f"xl/worksheets/sheet{extra + 2}.xml",
                sheet([(1, [])], dimension="A1"),
            )
        ]
    if table:
        members += [
            (
                "xl/worksheets/_rels/sheet1.xml.rels",
                (
                    _DECLARATION
                    + '<Relationships xmlns="http://schemas.openxmlformats.'
                    'org/package/2006/relationships"><Relationship Id="rId1" '
                    f'Type="{_RELS}/table" Target="../tables/table1.xml"/>'
                    "</Relationships>"
                ).encode("utf-8"),
            ),
            ("xl/tables/table1.xml", _table(names, span, offset)),
        ]
    return package(members)


def _column(number: int) -> str:
    """The letters naming a column, counting from one."""
    letters = ""
    left = number
    while left > 0:
        left = left - 1
        letters = chr(65 + left % 26) + letters
        left = left // 26
    return letters


def _table(names: "list[str]", span: str, offset: int) -> bytes:
    """A defined table over the header and the records below it."""
    parts = [
        _DECLARATION,
        f'<table xmlns="{_MAIN}" id="1" name="tblStudy" '
        f'displayName="tblStudy" ref="{span}" totalsRowShown="0">',
        f'<tableColumns count="{len(names) + offset}">',
    ]
    number = 0
    if offset:
        number = number + 1
        parts += [f'<tableColumn id="{number}" name="index"/>']
    for name in names:
        number = number + 1
        parts += [f'<tableColumn id="{number}" name="{_escaped(name)}"/>']
    parts += ["</tableColumns></table>"]
    return "".join(parts).encode("utf-8")
