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


def plain_book(n_rows: int = 30) -> bytes:
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


def typed_book() -> bytes:
    """Every cell class the study says a description MUST carry.

    Columns: a text of digits that must stay text, NA-like text, an
    empty-string cell beside an absent one, a boolean, an error, a
    formula with a cached value and one without, an integral number
    beside a fractional one, and a number wearing a format code.
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
    body += [
        (
            2,
            [
                cell("A2", "8", "s"),
                cell("B2", "9", "s"),
                cell("C2", "10", "s"),
                cell("D2", "1", "b"),
                cell("E2", "#N/A", "e"),
                cell("F2", "40", "", 0, "A2*10", True),
                cell("G2", "12.5"),
                cell("H2", "123", "", 7),
            ],
        ),
        (
            3,
            [
                cell("A3", "11", "s"),
                cell("B3", "12", "s"),
                cell("D3", "0", "b"),
                cell("E3", "#DIV/0!", "e"),
                cell("F3", "", "", 0, "A3*10", False),
                cell("G3", "3"),
                cell("H3", "4501", "", 7),
            ],
        ),
    ]
    return package(
        [
            ("[Content_Types].xml", _content_types(1, True, False, False)),
            ("_rels/.rels", _root_rels()),
            ("xl/workbook.xml", _workbook([("Data", "")])),
            ("xl/_rels/workbook.xml.rels", _workbook_rels(1, True)),
            ("xl/styles.xml", _styles()),
            ("xl/sharedStrings.xml", _shared_strings(strings)),
            ("xl/worksheets/sheet1.xml", sheet(body, dimension="A1:H3")),
        ]
    )


def titled_book(n_rows: int = 12) -> bytes:
    """Blank rows, a title row and a merged header cell above the names.

    An all-empty row stands inside the data as well, which both readers
    keep as a record of nothing.
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
    for place in range(n_rows):
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


def hidden_first_book(n_rows: int = 20) -> bytes:
    """A hidden sheet first, so the chosen sheet is the second one."""
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
    notes = sheet([(1, [cell("A1", "0", "s")])], dimension="A1:A1")
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


def epoch_book(n_rows: int = 10) -> bytes:
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


def inline_book(n_rows: int = 20) -> bytes:
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


def macro_book(n_rows: int = 10) -> bytes:
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
