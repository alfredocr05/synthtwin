"""Writing a twin as a file of the system its table came from (lane FORMATS).

ZONE W, the standard library alone. The twin is drawn as text, column by
column, exactly as a delimited twin is; this module turns each column's
cells back into the values its source stored -- the inverse of the
rendering `native` defines, which reads every text back into the very
value it came from -- and writes them in the source's format:

- PARQUET: one row group, each column chunk a run of uncompressed pages
  in the PLAIN encoding (definition levels run-length encoded), the
  footer in Thrift's compact protocol (`native.thrift_bytes`), and
  pandas' metadata block rebuilt from the published fields alone
  (`native.pandas_block`), so `pandas.read_parquet` restores each
  column's dtype and the index the source named.
- STATA: format 118 (119 past 32,767 columns), little-endian, every
  column in its own storage type, with its display format, label and
  value labels where they are published.
- SPSS: an uncompressed .sav with its dictionary -- formats, labels,
  value labels, missing values, measures, long names -- in UTF-8.
- SAS TRANSPORT: version 5, or version 8 where a name or a label is
  longer than version 5 holds, numbers in IBM's hexadecimal floats.

NOTHING OF THE MOMENT OR THE MACHINE IS WRITTEN: every header's date is
1 January 1980 at midnight, as `sheetwriting` dates a workbook's parts,
and every "written by" field names synthtwin. The same twin is the same
bytes on every computer: the writing is integer arithmetic and the
binary64 bits `math.frexp` hands over exactly (`native.double_bits`).

WHERE A TWIN CELL DOES NOT FIT ITS SOURCE'S STORAGE -- a whole number
past an integer type's range (the tail rule may draw past the real end),
a text longer than its fixed width, a four-byte number past binary32's
range -- the column is stored in the next wider storage and the writer
says so (`Written.widened`): the twin's values are never cut to fit. A
cell no storage of its column can hold (a word in a column of numbers)
is refused (`NativeWriteError`) and nothing is written.

Guarantees: `twin_file` is a fixed function of its arguments; it reads
nothing, opens nothing and writes nothing itself -- the caller writes
the bytes it returns through `writing.write_both_files`.
"""

import dataclasses

from synthtwin import errors, native


class NativeWriteError(ValueError):
    """A twin cell its column's native storage cannot hold; its message is `errors.native_twin_not_writable`'s."""


def _refused(column: str, why: str) -> NativeWriteError:
    """The refusal of a twin column the writer cannot store, in words a person can act on."""
    return NativeWriteError(errors.native_twin_not_writable(column, "native", why))


@dataclasses.dataclass(frozen=True)
class Written:
    """The twin file's bytes, and each column stored wider than its source stored it."""

    data: bytes
    # (column name, the source's storage, the twin's) for each widened column.
    widened: "tuple[tuple[str, str, str], ...]" = ()


# The one moment every header is dated with.
_STATA_STAMP = b"01 Jan 1980 00:00"
_SPSS_DATE = b"01 Jan 80"
_SPSS_TIME = b"00:00:00"
_SAS_STAMP = b"01JAN80:00:00:00"
_CREATED_BY = "synthtwin"


def twin_file(
    form: native.NativeForm,
    names: "tuple[str, ...]",
    columns: "list[list[str]]",
    n_rows: int,
) -> Written:
    """The twin's bytes in the format ``form`` names (`native.twin_format` of the source's).

    ``columns`` holds every column's cells as the twin wrote them, in
    the order of ``names``, each ``n_rows`` long. Raises NativeWriteError
    for a cell its column cannot hold in any storage of its kind, and
    ValueError for columns of unequal length (a caller's slip). No I/O.
    """
    if len(names) != len(form.columns) or len(columns) != len(names):
        raise ValueError("internal check: the twin's columns and its native form disagree")
    for cells in columns:
        if len(cells) != n_rows:
            raise ValueError("internal check: a twin column is not as long as the table")
    target = native.twin_format(form.system)
    if target == native.FORMAT_PARQUET:
        return _parquet(form, names, columns, n_rows)
    if target == native.FORMAT_STATA:
        return _stata(form, names, columns, n_rows)
    if target == native.FORMAT_SPSS:
        return _spss(form, names, columns, n_rows)
    return _xport(form, names, columns, n_rows)


# -- reading a twin cell back into its value ---------------------------


def _whole(text: str, column: str) -> int:
    """A whole number's text, as written by `native.whole_text`."""
    if not isinstance(text, str):
        raise TypeError("internal check: a cell was not text")
    body = text[1:] if text.startswith("-") else text
    if not body or not body.isdigit() or not body.isascii():
        raise _refused(column, "a cell holds something that is not a whole number")
    return int(text)


def _number(text: str, column: str, single: bool) -> float:
    found = native.exact_single(text) if single else native.exact_double(text)
    if found is None:
        raise _refused(column, "a cell holds something that is not a number")
    return found


def _decimal(text: str, scale: int, column: str) -> int:
    """The unscaled whole number of a decimal's text written with ``scale`` figures after its point."""
    if not isinstance(text, str):
        raise TypeError("internal check: a cell was not text")
    negative = text.startswith("-")
    body = text[1:] if negative else text
    point = body.find(".")
    whole_part = body if point < 0 else body[:point]
    fraction = "" if point < 0 else body[point + 1 :]
    if not whole_part or not whole_part.isdigit() or not whole_part.isascii():
        raise _refused(column, "a cell holds something that is not a decimal number")
    if fraction and (not fraction.isdigit() or not fraction.isascii()):
        raise _refused(column, "a cell holds something that is not a decimal number")
    if len(fraction) > scale:
        if fraction[scale:].strip("0"):
            raise _refused(column, "a cell holds more figures after its point than the column keeps")
        fraction = fraction[:scale]
    unscaled = int(whole_part)
    for _ in range(scale):
        unscaled = unscaled * 10
    tail = int(fraction) if fraction else 0
    for _ in range(scale - len(fraction)):
        tail = tail * 10
    unscaled = unscaled + tail
    return -unscaled if negative else unscaled


def _date(text: str, column: str) -> int:
    found = native.date_of_text(text)
    if found is None:
        raise _refused(column, "a cell holds something that is not a date written year-month-day")
    return found


def _stamp_units(text: str, per_second: int, column: str) -> int:
    """A stamp's text as a count of 1/per_second from 1970-01-01, universal time where it says so."""
    found = native.stamp_of_text(text)
    if found is None:
        raise _refused(column, "a cell holds something that is not a date and a time")
    days, seconds, figures, width = found
    units = native.units_of_figures(figures, width, per_second)
    if units is None:
        raise _refused(column, "a cell holds a finer fraction of a second than the column keeps")
    return (days * 86400 + seconds) * per_second + units


def _clock_units(text: str, per_second: int, column: str) -> int:
    found = native.clock_of_text(text)
    if found is None:
        raise _refused(column, "a cell holds something that is not a time of day")
    seconds, figures, width = found
    units = native.units_of_figures(figures, width, per_second)
    if units is None:
        raise _refused(column, "a cell holds a finer fraction of a second than the column keeps")
    return seconds * per_second + units


# -- Parquet -------------------------------------------------------------

_PAGE_ROWS = 65536
_ENCODING_PLAIN = 0
_ENCODING_RLE = 3
_PAGE_DATA = 0
# The logical type's field (7 a time of day, 8 a timestamp) and its
# unit's field (1 milliseconds, 2 microseconds, 3 nanoseconds).
_MOMENT_FIELDS = {
    native.STORE_TIME_MS: (7, 1),
    native.STORE_TIME_US: (7, 2),
    native.STORE_TIME_NS: (7, 3),
    native.STORE_TIMESTAMP_MS: (8, 1),
    native.STORE_TIMESTAMP_US: (8, 2),
    native.STORE_TIMESTAMP_NS: (8, 3),
}
_INTEGER_WIDENING = {
    native.STORE_INT8: native.STORE_INT16,
    native.STORE_INT16: native.STORE_INT32,
    native.STORE_INT32: native.STORE_INT64,
    native.STORE_UINT8: native.STORE_UINT16,
    native.STORE_UINT16: native.STORE_UINT32,
    native.STORE_UINT32: native.STORE_UINT64,
}
_INTEGER_BITS = {
    native.STORE_INT8: (8, True), native.STORE_INT16: (16, True),
    native.STORE_INT32: (32, True), native.STORE_INT64: (64, True),
    native.STORE_UINT8: (8, False), native.STORE_UINT16: (16, False),
    native.STORE_UINT32: (32, False), native.STORE_UINT64: (64, False),
}
_CONVERTED_INTEGER = {
    native.STORE_UINT8: 11, native.STORE_UINT16: 12, native.STORE_UINT32: 13,
    native.STORE_UINT64: 14, native.STORE_INT8: 15, native.STORE_INT16: 16,
    native.STORE_INT32: 17, native.STORE_INT64: 18,
}


@dataclasses.dataclass(frozen=True)
class _ParquetColumn:
    """One Parquet column ready to write: its schema facts and its present values' bytes."""

    name: str
    store: str
    physical: int
    type_length: int
    required: bool
    present: "tuple[bool, ...]"
    values: bytes
    # A categorical's dictionary (each entry its text's bytes) and each
    # present cell's place in it, written as a dictionary page and pages
    # of indices; empty for every other column.
    dictionary: "tuple[bytes, ...]" = ()
    indices: "tuple[int, ...]" = ()


def _rle_levels(present: "tuple[bool, ...]") -> bytes:
    """Definition levels of bit width one, as the run-length half of the hybrid encoding writes them."""
    out = bytearray()
    at = 0
    while at < len(present):
        level = present[at]
        run = 1
        while at + run < len(present) and present[at + run] == level:
            run = run + 1
        out += native.varint_bytes(run << 1)
        out += bytes([1 if level else 0])
        at = at + run
    return bytes(out)


def _parquet_values(cells: "list[str]", column: native.NativeColumn, name: str) -> "tuple[str, tuple[bool, ...], list[object]]":
    """(the storage the column is written in, which cells hold a value, the values) of one twin column."""
    store = column.storage
    present: "list[bool]" = []
    values: "list[object]" = []
    for cell in cells:
        # THE CELL STANDING FOR AN EMPTY TEXT IS WRITTEN AS ONE (lane TOOLS;
        # the outside review of batch 4zz, item 10): "" itself where the
        # source held no missing text, else its run of spaces; the cell ""
        # is then a missing text, as it always was.
        if column.written_as == native.WRITTEN_TEXT and column.empty_text is not None and cell == column.empty_text:
            present += [True]
            values += [""]
            continue
        if cell == "" and column.written_as != native.WRITTEN_TEXT:
            present += [False]
            continue
        if cell == "" and column.written_as == native.WRITTEN_TEXT and not column.required:
            present += [False]
            continue
        present += [True]
        written = column.written_as
        if written == native.WRITTEN_FLAG:
            if cell == native.FLAG_TRUE:
                values += [True]
            elif cell == native.FLAG_FALSE:
                values += [False]
            else:
                raise _refused(name, "a cell holds something that is not True or False")
        elif written == native.WRITTEN_WHOLE:
            values += [_whole(cell, name)]
        elif written == native.WRITTEN_NUMBER:
            values += [_number(cell, name, False)]
        elif written == native.WRITTEN_SINGLE:
            values += [_number(cell, name, True)]
        elif written == native.WRITTEN_DECIMAL:
            values += [_decimal(cell, column.scale if column.scale is not None else 0, name)]
        elif written == native.WRITTEN_DATE:
            values += [_date(cell, name)]
        elif written == native.WRITTEN_STAMP:
            values += [_stamp_units(cell, native.PER_SECOND[store], name)]
        elif written == native.WRITTEN_CLOCK:
            values += [_clock_units(cell, native.PER_SECOND[store], name)]
        else:
            values += [cell]
    if store in _INTEGER_WIDENING or store in (native.STORE_INT64, native.STORE_UINT64):
        while True:
            least, most = native.INTEGER_RANGES[store]
            if all(least <= value <= most for value in values if isinstance(value, int)):
                break
            if store not in _INTEGER_WIDENING:
                raise _refused(name, "a whole number is past the widest whole numbers the column can hold")
            store = _INTEGER_WIDENING[store]
    if store == native.STORE_FLOAT32:
        for value in values:
            if isinstance(value, float) and native.single_bits(value) is None:
                store = native.STORE_FLOAT64
                break
    return (store, tuple(present), values)


def _parquet_column(cells: "list[str]", column: native.NativeColumn, name: str) -> "tuple[_ParquetColumn, str]":
    store, present, values = _parquet_values(cells, column, name)
    out = bytearray()
    physical = native.PHYSICAL_BYTE_ARRAY
    type_length = 0
    if store == native.STORE_BOOLEAN:
        physical = native.PHYSICAL_BOOLEAN
        byte = 0
        filled = 0
        for value in values:
            if value is True:
                byte = byte | (1 << filled)
            filled = filled + 1
            if filled == 8:
                out += bytes([byte])
                byte = 0
                filled = 0
        if filled:
            out += bytes([byte])
    elif store in _INTEGER_BITS:
        bits, _signed = _INTEGER_BITS[store]
        width = 8 if bits == 64 else 4
        physical = native.PHYSICAL_INT64 if bits == 64 else native.PHYSICAL_INT32
        for value in values:
            out += native.little(int(f"{value}"), width)
    elif store == native.STORE_FLOAT32:
        physical = native.PHYSICAL_FLOAT
        for value in values:
            bits32 = native.single_bits(float(f"{value!r}"))
            out += native.little(bits32 if bits32 is not None else 0, 4)
    elif store == native.STORE_FLOAT64:
        physical = native.PHYSICAL_DOUBLE
        for value in values:
            out += native.little(native.double_bits(float(f"{value!r}")), 8)
    elif store == native.STORE_DATE:
        physical = native.PHYSICAL_INT32
        for value in values:
            out += native.little(int(f"{value}"), 4)
    elif store in (native.STORE_TIME_MS,):
        physical = native.PHYSICAL_INT32
        for value in values:
            out += native.little(int(f"{value}"), 4)
    elif store in native.PER_SECOND:
        physical = native.PHYSICAL_INT64
        for value in values:
            out += native.little(int(f"{value}"), 8)
    elif store == native.STORE_DECIMAL:
        physical = native.PHYSICAL_FIXED
        precision = column.precision if column.precision is not None else 38
        type_length = column.width if column.width else _decimal_bytes(precision)
        for value in values:
            number = int(f"{value}")
            if number >= (1 << (8 * type_length - 1)) or number < -(1 << (8 * type_length - 1)):
                raise _refused(name, "a decimal number is past the figures the column keeps")
            out += native.big(number, type_length)
    else:
        for value in values:
            data = bytes(f"{value}", "utf-8")
            out += native.little(len(data), 4) + data
    required = column.required and all(present)
    dictionary: "tuple[bytes, ...]" = ()
    indices: "tuple[int, ...]" = ()
    if store == native.STORE_STRING and column.pandas is not None and column.pandas.pandas_type == "categorical":
        # THE CATEGORIES IN THEIR PUBLISHED ORDER, then every other text the
        # twin holds in the order of its characters, as pandas orders the
        # categories it makes: pyarrow reads a dictionary page's order as
        # the categories' order.
        order: "list[str]" = list(column.categories) if column.categories is not None else []
        seen: "dict[str, int]" = {}
        for text in order:
            seen[text] = len(seen)
        others = sorted(set([f"{value}" for value in values if f"{value}" not in seen]))
        for text in others:
            seen[text] = len(seen)
            order += [text]
        dictionary = tuple([bytes(text, "utf-8") for text in order])
        indices = tuple([seen[f"{value}"] for value in values])
    built = _ParquetColumn(
        name=name, store=store, physical=physical, type_length=type_length,
        required=required, present=present, values=bytes(out),
        dictionary=dictionary, indices=indices,
    )
    return (built, store)


def _decimal_bytes(precision: int) -> int:
    """The fewest bytes a two's complement number of ``precision`` decimal figures fits in."""
    largest = 1
    for _ in range(precision):
        largest = largest * 10
    size = 1
    while (1 << (8 * size - 1)) <= largest:
        size = size + 1
    return size


def _value_widths(column: _ParquetColumn) -> "list[int]":
    """How many bytes each present value takes in the PLAIN encoding (for cutting pages)."""
    if column.physical == native.PHYSICAL_BOOLEAN:
        return []
    fixed = {
        native.PHYSICAL_INT32: 4, native.PHYSICAL_INT64: 8,
        native.PHYSICAL_FLOAT: 4, native.PHYSICAL_DOUBLE: 8,
    }
    count = sum(1 for flag in column.present if flag)
    if column.physical in fixed:
        return [fixed[column.physical]] * count
    if column.physical == native.PHYSICAL_FIXED:
        return [column.type_length] * count
    widths: "list[int]" = []
    at = 0
    data = column.values
    while at < len(data):
        size = native.from_little(data[at : at + 4])
        widths += [4 + size]
        at = at + 4 + size
    return widths


_ENCODING_RLE_DICTIONARY = 8
_PAGE_DICTIONARY = 2


def _bit_width(count: int) -> int:
    """The bits a dictionary index of a dictionary of ``count`` entries takes (one at least)."""
    width = 1
    while (1 << width) < count:
        width = width + 1
    return width


def _rle_indices(indices: "tuple[int, ...]", width: int) -> bytes:
    """Dictionary indices as the run-length half of the hybrid encoding writes them, each run's value in whole bytes."""
    out = bytearray()
    size = (width + 7) // 8
    at = 0
    while at < len(indices):
        value = indices[at]
        run = 1
        while at + run < len(indices) and indices[at + run] == value:
            run = run + 1
        out += native.varint_bytes(run << 1)
        out += native.little(value, size)
        at = at + run
    return bytes(out)


def _dictionary_pages(column: _ParquetColumn) -> "tuple[bytes, int]":
    """A categorical column's chunk: its dictionary page, then pages of indices; and the dictionary page's size."""
    out = bytearray()
    body = bytearray()
    for entry in column.dictionary:
        body += native.little(len(entry), 4)
        body += entry
    header = native.thrift_bytes(
        (
            native.T(1, native.I32, _PAGE_DICTIONARY),
            native.T(2, native.I32, len(body)),
            native.T(3, native.I32, len(body)),
            native.T(7, native.STRUCT, (
                native.T(1, native.I32, len(column.dictionary)),
                native.T(2, native.I32, _ENCODING_PLAIN),
            )),
        )
    )
    out += header
    out += body
    dictionary_size = len(out)
    width = _bit_width(len(column.dictionary))
    rows = len(column.present)
    row = 0
    index_at = 0
    while row < rows:
        end = min(rows, row + _PAGE_ROWS)
        flags = column.present[row:end]
        count = sum(1 for flag in flags if flag)
        page_indices = column.indices[index_at : index_at + count]
        index_at = index_at + count
        data = bytes([width]) + _rle_indices(page_indices, width)
        page = data
        if not column.required:
            levels = _rle_levels(flags)
            page = native.little(len(levels), 4) + levels + data
        header = native.thrift_bytes(
            (
                native.T(1, native.I32, _PAGE_DATA),
                native.T(2, native.I32, len(page)),
                native.T(3, native.I32, len(page)),
                native.T(5, native.STRUCT, (
                    native.T(1, native.I32, end - row),
                    native.T(2, native.I32, _ENCODING_RLE_DICTIONARY),
                    native.T(3, native.I32, _ENCODING_RLE),
                    native.T(4, native.I32, _ENCODING_RLE),
                )),
            )
        )
        out += header
        out += page
        row = end
    return (bytes(out), dictionary_size)


def _parquet_pages(column: _ParquetColumn) -> "tuple[bytes, int]":
    """The column chunk's pages, and its total size."""
    out = bytearray()
    widths = _value_widths(column)
    value_at = 0
    byte_at = 0
    rows = len(column.present)
    row = 0
    while row < rows or (rows == 0 and not out):
        end = min(rows, row + _PAGE_ROWS)
        flags = column.present[row:end]
        count = sum(1 for flag in flags if flag)
        if column.physical == native.PHYSICAL_BOOLEAN:
            # Booleans are bit-packed across the page: re-pack this page's bits.
            bits_out = bytearray()
            byte = 0
            filled = 0
            for index in range(value_at, value_at + count):
                bit = (column.values[index // 8] >> (index % 8)) & 1
                byte = byte | (bit << filled)
                filled = filled + 1
                if filled == 8:
                    bits_out += bytes([byte])
                    byte = 0
                    filled = 0
            if filled:
                bits_out += bytes([byte])
            body_values = bytes(bits_out)
        else:
            size = sum(widths[value_at : value_at + count])
            body_values = column.values[byte_at : byte_at + size]
            byte_at = byte_at + size
        value_at = value_at + count
        body = body_values
        if not column.required:
            levels = _rle_levels(flags)
            body = native.little(len(levels), 4) + levels + body_values
        header = native.thrift_bytes(
            (
                native.T(1, native.I32, _PAGE_DATA),
                native.T(2, native.I32, len(body)),
                native.T(3, native.I32, len(body)),
                native.T(
                    5,
                    native.STRUCT,
                    (
                        native.T(1, native.I32, end - row),
                        native.T(2, native.I32, _ENCODING_PLAIN),
                        native.T(3, native.I32, _ENCODING_RLE),
                        native.T(4, native.I32, _ENCODING_RLE),
                    ),
                ),
            )
        )
        out += header
        out += body
        row = end
        if rows == 0:
            break
    return (bytes(out), len(out))


def _logical_fields(column: _ParquetColumn, native_column: native.NativeColumn) -> "tuple[native.T, ...]":
    """The schema element's converted type, scale, precision and logical type fields."""
    store = column.store
    if store == native.STORE_STRING:
        return (native.T(6, native.I32, 0), native.T(10, native.STRUCT, (native.T(1, native.STRUCT, ()),)))
    if store == native.STORE_DATE:
        return (native.T(6, native.I32, 6), native.T(10, native.STRUCT, (native.T(6, native.STRUCT, ()),)))
    if store == native.STORE_DECIMAL:
        precision = native_column.precision if native_column.precision is not None else 38
        scale = native_column.scale if native_column.scale is not None else 0
        return (
            native.T(6, native.I32, 5),
            native.T(7, native.I32, scale),
            native.T(8, native.I32, precision),
            native.T(10, native.STRUCT, (native.T(5, native.STRUCT, (
                native.T(1, native.I32, scale), native.T(2, native.I32, precision),
            )),)),
        )
    if store in _INTEGER_BITS and store not in (native.STORE_INT32, native.STORE_INT64):
        bits, signed = _INTEGER_BITS[store]
        return (
            native.T(6, native.I32, _CONVERTED_INTEGER[store]),
            native.T(10, native.STRUCT, (native.T(10, native.STRUCT, (
                native.T(1, native.BYTE, bits), native.T(2, native.BOOL, signed),
            )),)),
        )
    if store in _MOMENT_FIELDS:
        slot, unit = _MOMENT_FIELDS[store]
        utc = native_column.utc is True
        return (
            native.T(10, native.STRUCT, (native.T(slot, native.STRUCT, (
                native.T(1, native.BOOL, utc),
                native.T(2, native.STRUCT, (native.T(unit, native.STRUCT, ()),)),
            )),)),
        )
    return ()


def _parquet(
    form: native.NativeForm, names: "tuple[str, ...]", columns: "list[list[str]]", n_rows: int
) -> Written:
    pieces = bytearray(b"PAR1")
    written = 4
    chunks: "list[tuple[native.T, ...]]" = []
    schema: "list[tuple[native.T, ...]]" = [
        (native.T(4, native.BINARY, "schema"), native.T(5, native.I32, len(names)))
    ]
    widened: "list[tuple[str, str, str]]" = []
    stores_written: "list[str]" = []
    nullable: "list[bool]" = []
    total = 0
    for place in range(len(names)):
        native_column = form.columns[place]
        built, store = _parquet_column(columns[place], native_column, names[place])
        stores_written += [store]
        nullable += [not built.required]
        if store != native_column.storage:
            widened += [(names[place], native_column.storage, store)]
        offset = written
        dictionary_size = 0
        if built.dictionary:
            pages, dictionary_size = _dictionary_pages(built)
            size = len(pages)
        else:
            pages, size = _parquet_pages(built)
        pieces += pages
        written = written + size
        total = total + size
        element: "list[native.T]" = [native.T(1, native.I32, built.physical)]
        if built.physical == native.PHYSICAL_FIXED:
            element += [native.T(2, native.I32, built.type_length)]
        element += [
            native.T(3, native.I32, native.REQUIRED if built.required else native.OPTIONAL),
            native.T(4, native.BINARY, names[place]),
        ]
        element += list(_logical_fields(built, native_column))
        schema += [tuple(element)]
        encodings = (_ENCODING_PLAIN, _ENCODING_RLE) + ((_ENCODING_RLE_DICTIONARY,) if built.dictionary else ())
        meta: "list[native.T]" = [
            native.T(1, native.I32, built.physical),
            native.T(2, native.LIST, native.TList(native.I32, encodings)),
            native.T(3, native.LIST, native.TList(native.BINARY, (names[place],))),
            native.T(4, native.I32, 0),
            native.T(5, native.I64, n_rows),
            native.T(6, native.I64, size),
            native.T(7, native.I64, size),
            native.T(9, native.I64, offset + dictionary_size),
        ]
        if built.dictionary:
            meta += [native.T(11, native.I64, offset)]
        chunks += [(native.T(2, native.I64, offset), native.T(3, native.STRUCT, tuple(meta)))]
    group = (
        native.T(1, native.LIST, native.TList(native.STRUCT, tuple(chunks))),
        native.T(2, native.I64, total),
        native.T(3, native.I64, n_rows),
    )
    pairs: "list[tuple[native.T, ...]]" = []
    with_pandas = any(column.pandas is not None for column in form.columns)
    # A zone Arrow alone kept rides in Arrow's record, with no pandas block
    # (lane TOOLS; `native.arrow_schema_text`).
    zoned = any(column.zone is not None and column.utc for column in form.columns)
    if with_pandas or zoned:
        pandas_text = native.pandas_block(form, names, n_rows) if with_pandas else ""
        written_form = native.NativeForm(
            system=form.system,
            version=form.version,
            columns=tuple(
                [
                    dataclasses.replace(form.columns[place], storage=stores_written[place])
                    for place in range(len(names))
                ]
            ),
            table_name=form.table_name,
            index=form.index,
        )
        arrow = native.arrow_schema_text(written_form, names, tuple(nullable), pandas_text)
        if arrow:
            pairs += [(native.T(1, native.BINARY, native.ARROW_KEY), native.T(2, native.BINARY, arrow))]
        if with_pandas:
            pairs += [
                (
                    native.T(1, native.BINARY, native.PANDAS_KEY),
                    native.T(2, native.BINARY, pandas_text),
                )
            ]
    fields: "list[native.T]" = [
        native.T(1, native.I32, 1),
        native.T(2, native.LIST, native.TList(native.STRUCT, tuple(schema))),
        native.T(3, native.I64, n_rows),
        native.T(4, native.LIST, native.TList(native.STRUCT, (group,))),
    ]
    if pairs:
        fields += [native.T(5, native.LIST, native.TList(native.STRUCT, tuple(pairs)))]
    fields += [native.T(6, native.BINARY, _CREATED_BY)]
    footer = native.thrift_bytes(tuple(fields))
    pieces += footer
    pieces += native.little(len(footer), 4)
    pieces += b"PAR1"
    return Written(data=bytes(pieces), widened=tuple(widened))


# -- SAS, Stata and SPSS: one column's values --------------------------

_MISSING = "missing"


@dataclasses.dataclass(frozen=True)
class _StatColumn:
    """One column of a SAS, Stata or SPSS twin: numbers (or a special missing's text) or texts."""

    name: str
    text: bool
    # Each cell: a float, None (missing), or a special missing's text
    # (`.A`, `.a`) for a numeric column; bytes for a text column.
    values: "list[object]"
    width: int


def _stat_values(cells: "list[str]", column: native.NativeColumn, name: str, system: str) -> _StatColumn:
    """A twin column read back into the numbers (in the target system's own units) or texts it stores."""
    if column.storage == native.STORE_TEXT:
        encoded: "list[object]" = []
        longest = 0
        for cell in cells:
            data = bytes(cell, "utf-8")
            encoded += [data]
            if len(data) > longest:
                longest = len(data)
        return _StatColumn(name=name, text=True, values=encoded, width=longest)
    spss = system == native.FORMAT_SPSS
    stata = system == native.FORMAT_STATA
    day_zero = native.SPSS_EPOCH_DAYS if spss else native.DAYS_1960
    out: "list[object]" = []
    for cell in cells:
        if cell == "":
            out += [None]
            continue
        if (stata and cell in native.STATA_EXTENDED) or (not stata and not spss and cell in native.SAS_SPECIAL):
            out += [cell]
            continue
        written = column.written_as
        if written == native.WRITTEN_DATE:
            days = _date(cell, name) - day_zero
            out += [float(days * 86400) if spss else float(days)]
        elif written == native.WRITTEN_STAMP:
            micro = _stamp_units(cell, 1000000, name) - day_zero * 86400 * 1000000
            if stata:
                if micro % 1000:
                    raise _refused(name, "a cell holds a finer fraction of a second than Stata keeps")
                out += [float(micro // 1000)]
            else:
                # Whole numbers divided: Python rounds the exact quotient
                # once, so a stamp past 2 ** 53 microseconds (SPSS counts
                # from 1582) is the double its text names.
                out += [micro / 1000000]
        elif written == native.WRITTEN_CLOCK:
            out += [_clock_units(cell, 1000000, name) / 1000000]
        elif written == native.WRITTEN_WHOLE:
            out += [float(_whole(cell, name))]
        elif written == native.WRITTEN_SINGLE:
            out += [_number(cell, name, True)]
        else:
            out += [_number(cell, name, False)]
    return _StatColumn(name=name, text=False, values=out, width=8)


# -- Stata -----------------------------------------------------------------

_STATA_TYPE_CODES = {
    native.STORE_STATA_DOUBLE: 65526,
    native.STORE_STATA_FLOAT: 65527,
    native.STORE_STATA_LONG: 65528,
    native.STORE_STATA_INT: 65529,
    native.STORE_STATA_BYTE: 65530,
}
_STATA_WIDTHS = {
    native.STORE_STATA_DOUBLE: 8,
    native.STORE_STATA_FLOAT: 4,
    native.STORE_STATA_LONG: 4,
    native.STORE_STATA_INT: 2,
    native.STORE_STATA_BYTE: 1,
}
_STATA_WIDER = {
    native.STORE_STATA_BYTE: native.STORE_STATA_INT,
    native.STORE_STATA_INT: native.STORE_STATA_LONG,
    native.STORE_STATA_LONG: native.STORE_STATA_DOUBLE,
    native.STORE_STATA_FLOAT: native.STORE_STATA_DOUBLE,
}
_STATA_MISSING_BASE = {
    native.STORE_STATA_BYTE: 101,
    native.STORE_STATA_INT: 32741,
    native.STORE_STATA_LONG: 2147483621,
}
_STATA_FORMATS = {
    native.STORE_STATA_DOUBLE: "%10.0g",
    native.STORE_STATA_FLOAT: "%9.0g",
    native.STORE_STATA_LONG: "%12.0g",
    native.STORE_STATA_INT: "%8.0g",
    native.STORE_STATA_BYTE: "%8.0g",
}
_STATA_STRING_MOST = 2045


def _stata_fits(store: str, values: "list[object]") -> bool:
    """Whether every present value of a numeric column fits Stata storage ``store`` exactly."""
    for value in values:
        if not isinstance(value, float):
            continue
        if store == native.STORE_STATA_DOUBLE:
            continue
        if store == native.STORE_STATA_FLOAT:
            if value == value and native.single_bits(value) is None:
                return False
            continue
        if value != value or value != int(value):
            return False
        least, most = native.INTEGER_RANGES[store]
        if not least <= int(value) <= most:
            return False
    return True


def _stata_cell(store: str, value: object) -> bytes:
    """One numeric cell in Stata storage ``store``: its value, Stata's missing `.`, or `.a` to `.z`."""
    letter = 0
    if isinstance(value, str):
        letter = ord(value[1]) - 96
    if store == native.STORE_STATA_DOUBLE:
        if isinstance(value, float):
            return native.little(native.double_bits(value), 8)
        return native.little(0x7FE0000000000000 + letter * 0x0000010000000000, 8)
    if store == native.STORE_STATA_FLOAT:
        if isinstance(value, float):
            bits = native.single_bits(value)
            return native.little(bits if bits is not None else 0, 4)
        return native.little(0x7F000000 + letter * 0x800, 4)
    width = _STATA_WIDTHS[store]
    if isinstance(value, float):
        return native.little(int(value), width)
    return native.little(_STATA_MISSING_BASE[store] + letter, width)


def _padded(text: str, width: int) -> bytes:
    data = bytes(text, "utf-8")[:width]
    return data + bytes(width - len(data))


def _stata(
    form: native.NativeForm, names: "tuple[str, ...]", columns: "list[list[str]]", n_rows: int
) -> Written:
    count = len(names)
    # The source's own release where it is 118 or 119; 118 for an older
    # one (Stata 14's format, which every reader of 117 also reads but
    # Stata 13 does not); 119 past 32,767 columns, which 118 cannot hold.
    release = form.version if form.version in (118, 119) else 118
    if count > 32767:
        release = 119
    stats: "list[_StatColumn]" = []
    stores: "list[str]" = []
    widths: "list[int]" = []
    widened: "list[tuple[str, str, str]]" = []
    for place in range(count):
        column = form.columns[place]
        stat = _stat_values(columns[place], column, names[place], native.FORMAT_STATA)
        stats += [stat]
        if stat.text:
            width = max(1, stat.width, column.width if column.width else 1)
            if width > _STATA_STRING_MOST:
                raise _refused(names[place], "a text is longer than Stata's longest fixed text of 2,045 bytes")
            if column.width and width > column.width:
                widened += [(names[place], f"str{column.width}", f"str{width}")]
            stores += [native.STORE_TEXT]
            widths += [width]
            continue
        store = column.storage if column.storage in _STATA_TYPE_CODES else native.STORE_STATA_DOUBLE
        first = store
        while not _stata_fits(store, stat.values):
            store = _STATA_WIDER[store]
        if store != first:
            widened += [(names[place], first, store)]
        stores += [store]
        widths += [_STATA_WIDTHS[store]]
    head = (
        b"<stata_dta><header><release>" + bytes(f"{release}", "ascii") + b"</release>"
        + b"<byteorder>LSF</byteorder><K>" + native.little(count, 4 if release == 119 else 2)
        + b"</K><N>" + native.little(n_rows, 8) + b"</N><label>" + native.little(0, 2)
        + b"</label><timestamp>" + bytes([len(_STATA_STAMP)]) + _STATA_STAMP + b"</timestamp></header>"
    )
    types = b""
    varnames = b""
    formats = b""
    value_label_names = b""
    variable_labels = b""
    label_sets: "dict[str, list[tuple[int, str]]]" = {}
    set_order: "list[str]" = []
    for place in range(count):
        column = form.columns[place]
        if stores[place] == native.STORE_TEXT:
            types = types + native.little(widths[place], 2)
            shown = column.display if column.display is not None else f"%-{widths[place]}s"
        else:
            types = types + native.little(_STATA_TYPE_CODES[stores[place]], 2)
            if column.display is not None:
                shown = column.display
            elif column.written_as == native.WRITTEN_DATE:
                shown = "%td"
            elif column.written_as == native.WRITTEN_STAMP:
                shown = "%tc"
            else:
                shown = _STATA_FORMATS[stores[place]]
        varnames = varnames + _padded(names[place], 129)
        formats = formats + _padded(shown, 57)
        set_name = ""
        if column.value_labels and stores[place] != native.STORE_TEXT:
            set_name = column.label_set if column.label_set is not None else names[place]
            entries: "list[tuple[int, str]]" = []
            for code, text in column.value_labels:
                number = native.exact_double(code)
                if number is None or number != number or number != int(number):
                    continue
                entries += [(int(number), text)]
            if set_name not in label_sets:
                set_order += [set_name]
                label_sets[set_name] = []
            label_sets[set_name] = label_sets[set_name] + entries
        value_label_names = value_label_names + _padded(set_name, 129)
        variable_labels = variable_labels + _padded(column.label if column.label is not None else "", 321)
    data = bytearray()
    for row in range(n_rows):
        for place in range(count):
            value = stats[place].values[row]
            if stores[place] == native.STORE_TEXT:
                cell = value if isinstance(value, bytes) else b""
                data += cell + bytes(widths[place] - len(cell))
            else:
                data += _stata_cell(stores[place], value)
    labels = b""
    for set_name in set_order:
        chosen: "dict[int, str]" = {}
        for number, words in label_sets[set_name]:
            chosen[number] = words
        numbers = sorted(chosen)
        offsets = b""
        values = b""
        text_bytes = b""
        for number in numbers:
            offsets = offsets + native.little(len(text_bytes), 4)
            values = values + native.little(number, 4)
            text_bytes = text_bytes + bytes(chosen[number], "utf-8") + b"\x00"
        table = native.little(len(numbers), 4) + native.little(len(text_bytes), 4) + offsets + values + text_bytes
        labels = labels + b"<lbl>" + native.little(len(table), 4) + _padded(set_name, 129) + bytes(3) + table + b"</lbl>"
    sections = [
        b"<variable_types>" + types + b"</variable_types>",
        b"<varnames>" + varnames + b"</varnames>",
        b"<sortlist>" + bytes(2 * (count + 1) if release == 118 else 4 * (count + 1)) + b"</sortlist>",
        b"<formats>" + formats + b"</formats>",
        b"<value_label_names>" + value_label_names + b"</value_label_names>",
        b"<variable_labels>" + variable_labels + b"</variable_labels>",
        b"<characteristics></characteristics>",
        b"<data>" + bytes(data) + b"</data>",
        b"<strls></strls>",
        b"<value_labels>" + labels + b"</value_labels>",
    ]
    map_size = len(b"<map>") + 14 * 8 + len(b"</map>")
    offsets_list = [0, len(head)]
    at = len(head) + map_size
    for section in sections:
        offsets_list += [at]
        at = at + len(section)
    offsets_list += [at]
    offsets_list += [at + len(b"</stata_dta>")]
    whole = bytearray(head)
    whole += b"<map>"
    for offset in offsets_list:
        whole += native.little(offset, 8)
    whole += b"</map>"
    for section in sections:
        whole += section
    whole += b"</stata_dta>"
    return Written(data=bytes(whole), widened=tuple(widened))


# -- SPSS --------------------------------------------------------------------

_SPSS_SYSMIS = 0xFFEFFFFFFFFFFFFF
_SPSS_HIGHEST = 0x7FEFFFFFFFFFFFFF
_SPSS_LOWEST = 0xFFEFFFFFFFFFFFFE
_SPSS_FORMAT_CODES = {
    "A": 1, "AHEX": 2, "COMMA": 3, "DOLLAR": 4, "F": 5, "IB": 6, "PIBHEX": 7,
    "P": 8, "PIB": 9, "PK": 10, "RB": 11, "RBHEX": 12, "Z": 15, "N": 16,
    "E": 17, "DATE": 20, "TIME": 21, "DATETIME": 22, "ADATE": 23, "JDATE": 24,
    "DTIME": 25, "WKDAY": 26, "MONTH": 27, "MOYR": 28, "QYR": 29, "WKYR": 30,
    "PCT": 31, "DOT": 32, "CCA": 33, "CCB": 34, "CCC": 35, "CCD": 36,
    "CCE": 37, "EDATE": 38, "SDATE": 39, "MTIME": 40, "YMDHMS": 41,
}
_SPSS_MEASURES = {"nominal": 1, "ordinal": 2, "scale": 3}
_SPSS_STRING_MOST = 255


def _spss_format(code: "str | None", fallback: "tuple[int, int, int]") -> int:
    """A display format as SPSS's packed number: type, width and decimals."""
    if code is None:
        kind, width, decimals = fallback
        return (kind << 16) | (width << 8) | decimals
    return _spss_format_of(code, fallback)


def _spss_format_of(code: str, fallback: "tuple[int, int, int]") -> int:
    if not isinstance(code, str):
        raise TypeError("internal check: a format code was not text")
    cut = len(code)
    while cut > 0 and (48 <= ord(code[cut - 1]) <= 57 or code[cut - 1] == "."):
        cut = cut - 1
    name = code[:cut]
    rest = code[cut:]
    if name not in _SPSS_FORMAT_CODES:
        kind, width, decimals = fallback
        return (kind << 16) | (width << 8) | decimals
    point = rest.find(".")
    width_text = rest if point < 0 else rest[:point]
    decimals_text = "" if point < 0 else rest[point + 1 :]
    width = int(width_text) if width_text else fallback[1]
    decimals = int(decimals_text) if decimals_text else 0
    return (_SPSS_FORMAT_CODES[name] << 16) | ((width & 0xFF) << 8) | (decimals & 0xFF)


def _int32(value: int) -> bytes:
    return native.little(value, 4)


def _short_names(names: "tuple[str, ...]") -> "list[str]":
    """Eight-byte short names, upper case and distinct, for SPSS's dictionary."""
    taken: "dict[str, bool]" = {}
    out: "list[str]" = []
    for place in range(len(names)):
        stem = str(bytes(names[place], "utf-8")[:8], "utf-8", "ignore").upper()
        if not stem or stem in taken or not _spss_name_start(stem):
            stem = f"V{place + 1}"
        while stem in taken:
            stem = f"V{place + 1}X"
        taken[stem] = True
        out += [stem]
    return out


def _spss_name_start(stem: str) -> bool:
    place = ord(stem[0])
    return 65 <= place <= 90 or stem[0] in "@#$"


def _spss(
    form: native.NativeForm, names: "tuple[str, ...]", columns: "list[list[str]]", n_rows: int
) -> Written:
    count = len(names)
    stats: "list[_StatColumn]" = []
    widths: "list[int]" = []
    widened: "list[tuple[str, str, str]]" = []
    for place in range(count):
        column = form.columns[place]
        stat = _stat_values(columns[place], column, names[place], native.FORMAT_SPSS)
        stats += [stat]
        if stat.text:
            width = max(1, stat.width, column.width if column.width else 1)
            if width > _SPSS_STRING_MOST:
                raise _refused(names[place], "a text is longer than the 255 bytes this release writes")
            if column.width and width > column.width:
                widened += [(names[place], f"A{column.width}", f"A{width}")]
            widths += [width]
        else:
            widths += [0]
    slots = 0
    for width in widths:
        slots = slots + (1 if width == 0 else (width + 7) // 8)
    short = _short_names(names)
    out = (
        b"$FL2" + _ascii_padded("@(#) SPSS DATA FILE synthtwin", 60)
        + _int32(2) + _int32(slots) + _int32(0) + _int32(0) + _int32(n_rows)
        + native.little(native.double_bits(100.0), 8)
        + _SPSS_DATE + _SPSS_TIME + bytes(b" " * 64) + bytes(3)
    )
    index_of: "list[int]" = []
    at = 1
    for place in range(count):
        column = form.columns[place]
        width = widths[place]
        index_of += [at]
        if width == 0:
            fallback = (5, 8, 2)
            if column.written_as == native.WRITTEN_DATE:
                fallback = (20, 11, 0)
            elif column.written_as == native.WRITTEN_STAMP:
                fallback = (22, 20 if not column.fraction else 21 + column.fraction, column.fraction)
            elif column.written_as == native.WRITTEN_CLOCK:
                fallback = (21, 8, 0)
            shown = _spss_format(column.display, fallback)
        else:
            shown = (1 << 16) | (width << 8)
        label = column.label
        missing = b""
        missing_count = 0
        if column.missing is not None and width == 0:
            codes = list(column.missing.values)
            if column.missing.low is not None and column.missing.high is not None:
                missing_count = -3 if codes else -2
                low = native.exact_double(column.missing.low)
                high = native.exact_double(column.missing.high)
                missing = missing + native.little(native.double_bits(low if low is not None else 0.0), 8)
                missing = missing + native.little(native.double_bits(high if high is not None else 0.0), 8)
                codes = codes[:1]
            else:
                missing_count = len(codes)
            for code in codes:
                number = native.exact_double(code)
                missing = missing + native.little(native.double_bits(number if number is not None else 0.0), 8)
        elif column.missing is not None and width:
            codes = [code for code in column.missing.values if len(bytes(code, "utf-8")) <= 8]
            missing_count = len(codes)
            for code in codes:
                missing = missing + _ascii_padded(code, 8)
        record = (
            _int32(2) + _int32(width) + _int32(1 if label is not None else 0) + _int32(missing_count)
            + _int32(shown) + _int32(shown) + _ascii_padded(short[place], 8)
        )
        if label is not None:
            text = bytes(label, "utf-8")[:255]
            record = record + _int32(len(text)) + text + b" " * ((4 - len(text) % 4) % 4)
        record = record + missing
        out = out + record
        at = at + 1
        if width:
            for _ in range((width + 7) // 8 - 1):
                out = out + _int32(2) + _int32(-1) + _int32(0) + _int32(0) + _int32(0) + _int32(0) + b"        "
                at = at + 1
    for place in range(count):
        column = form.columns[place]
        if not column.value_labels or widths[place]:
            continue
        entries = b""
        listed = 0
        for code, words in column.value_labels:
            number = native.exact_double(code)
            if number is None:
                continue
            spelled = bytes(words, "utf-8")[:120]
            size = 1 + len(spelled)
            padding = (8 - size % 8) % 8
            entries = entries + native.little(native.double_bits(number), 8) + bytes([len(spelled)]) + spelled + b" " * padding
            listed = listed + 1
        if not listed:
            continue
        out = out + _int32(3) + _int32(listed) + entries
        out = out + _int32(4) + _int32(1) + _int32(index_of[place])
    machine = _int32(20) + _int32(0) + _int32(0) + _int32(-1) + _int32(1) + _int32(1) + _int32(2) + _int32(65001)
    out = out + _int32(7) + _int32(3) + _int32(4) + _int32(8) + machine
    floats = (
        native.little(_SPSS_SYSMIS, 8) + native.little(_SPSS_HIGHEST, 8) + native.little(_SPSS_LOWEST, 8)
    )
    out = out + _int32(7) + _int32(4) + _int32(8) + _int32(3) + floats
    display = b""
    for place in range(count):
        column = form.columns[place]
        # A measure the source left unset is written unset (0), as SPSS
        # and ReadStat read an unknown one.
        measure = _SPSS_MEASURES[column.measure] if column.measure in _SPSS_MEASURES else 0
        display = display + _int32(measure) + _int32(8 if not widths[place] else min(widths[place], 32))
        display = display + _int32(0 if widths[place] else 1)
    out = out + _int32(7) + _int32(11) + _int32(4) + _int32(3 * count) + display
    long_names = bytearray()
    for place in range(count):
        if place:
            long_names += b"\t"
        long_names += bytes(short[place], "utf-8") + b"=" + bytes(names[place], "utf-8")
    out = out + _int32(7) + _int32(13) + _int32(1) + _int32(len(long_names)) + long_names
    encoding = b"UTF-8"
    out = out + _int32(7) + _int32(20) + _int32(1) + _int32(len(encoding)) + encoding
    out = out + _int32(999) + _int32(0)
    data = bytearray()
    for row in range(n_rows):
        for place in range(count):
            value = stats[place].values[row]
            width = widths[place]
            if width:
                cell = value if isinstance(value, bytes) else b""
                padded_width = ((width + 7) // 8) * 8
                data += cell + b" " * (padded_width - len(cell))
            elif isinstance(value, float):
                data += native.little(native.double_bits(value), 8)
            else:
                data += native.little(_SPSS_SYSMIS, 8)
    return Written(data=out + bytes(data), widened=tuple(widened))


# -- SAS transport ----------------------------------------------------------

_XPORT_NUMERIC = 1
_XPORT_TEXT = 2


def _record(text: bytes) -> bytes:
    """One 80-byte card image, padded with blanks."""
    return text[:80] + b" " * (80 - len(text[:80]))


def _ascii_padded(text: str, width: int) -> bytes:
    data = bytes(text, "utf-8")[:width]
    return data + b" " * (width - len(data))


def _big16(value: int) -> bytes:
    return native.big(value, 2)


def _sas_format(code: "str | None", fallback: "tuple[str, int, int]") -> "tuple[str, int, int]":
    """(name, width, decimals) of a SAS format code such as `DATE9.`, `8.2` or `$CHAR20.`."""
    if code is None:
        return fallback
    return _sas_format_of(code)


def _sas_format_of(code: str) -> "tuple[str, int, int]":
    if not isinstance(code, str):
        raise TypeError("internal check: a format code was not text")
    body = code[: len(code) - 1] if code.endswith(".") else code
    cut = len(body)
    while cut > 0 and (48 <= ord(body[cut - 1]) <= 57 or body[cut - 1] == "."):
        cut = cut - 1
    name = body[:cut]
    rest = body[cut:]
    point = rest.find(".")
    width_text = rest if point < 0 else rest[:point]
    decimals_text = "" if point < 0 else rest[point + 1 :]
    width = int(width_text) if width_text else 0
    decimals = int(decimals_text) if decimals_text else 0
    return (name[:8], width, decimals)


def _xport_number(value: object, length: int) -> "bytes | None":
    if value is None:
        return b"." + bytes(length - 1)
    if isinstance(value, str):
        return bytes([ord(value[1])]) + bytes(length - 1)
    if not isinstance(value, float) or value != value:
        return b"." + bytes(length - 1)
    return native.ibm_bits(value, length)


def _xport(
    form: native.NativeForm, names: "tuple[str, ...]", columns: "list[list[str]]", n_rows: int
) -> Written:
    count = len(names)
    stats: "list[_StatColumn]" = []
    lengths: "list[int]" = []
    widened: "list[tuple[str, str, str]]" = []
    for place in range(count):
        column = form.columns[place]
        stat = _stat_values(columns[place], column, names[place], native.FORMAT_SAS_TRANSPORT)
        stats += [stat]
        if stat.text:
            width = max(1, stat.width, column.width if column.width else 1)
            if width > 32767:
                raise _refused(names[place], "a text is longer than SAS keeps in one variable")
            if column.width and width > column.width:
                widened += [(names[place], f"${column.width}", f"${width}")]
            lengths += [width]
            continue
        length = column.width if column.width and 2 <= column.width <= 8 else 8
        first = length
        while length < 8 and any(
            _xport_number(value, length) is None for value in stat.values if isinstance(value, float)
        ):
            length = length + 1
        for value in stat.values:
            if isinstance(value, float) and value == value and native.ibm_bits(value, 8) is None:
                raise _refused(names[place], "a number is past the largest a SAS transport file holds")
        if length != first:
            widened += [(names[place], f"length {first}", f"length {length}")]
        lengths += [length]
    long_form = form.system == native.FORMAT_SAS_TRANSPORT and form.version == 8
    for place in range(count):
        label = form.columns[place].label
        if len(bytes(names[place], "utf-8")) > 8 or (label is not None and len(bytes(label, "utf-8")) > 40):
            long_form = True
    member = form.table_name if form.table_name is not None else "DATA"
    if not long_form:
        member = member[:8]
    out = b""
    if long_form:
        out = out + _record(b"HEADER RECORD*******LIBV8   HEADER RECORD!!!!!!!000000000000000000000000000000")
    else:
        out = out + _record(b"HEADER RECORD*******LIBRARY HEADER RECORD!!!!!!!000000000000000000000000000000")
    out = out + _record(b"SAS     SAS     SASLIB  9.4     X64_7PRO" + b" " * 24 + _SAS_STAMP)
    out = out + _record(_SAS_STAMP)
    if long_form:
        out = out + _record(b"HEADER RECORD*******MEMBV8  HEADER RECORD!!!!!!!000000000000000001600000000140")
        out = out + _record(b"HEADER RECORD*******DSCPTV8 HEADER RECORD!!!!!!!000000000000000000000000000000")
        out = out + _record(b"SAS     " + _ascii_padded(member, 32) + b"SASDATA 9.4     X64_7PRO" + _SAS_STAMP)
    else:
        out = out + _record(b"HEADER RECORD*******MEMBER  HEADER RECORD!!!!!!!000000000000000001600000000140")
        out = out + _record(b"HEADER RECORD*******DSCRPTR HEADER RECORD!!!!!!!000000000000000000000000000000")
        out = out + _record(b"SAS     " + _ascii_padded(member, 8) + b"SASDATA 9.4     X64_7PRO" + b" " * 24 + _SAS_STAMP)
    out = out + _record(_SAS_STAMP + b" " * 16 + b" " * 40 + b" " * 8)
    head = b"HEADER RECORD*******NAMSTV8 HEADER RECORD!!!!!!!000000" if long_form else (
        b"HEADER RECORD*******NAMESTR HEADER RECORD!!!!!!!000000"
    )
    out = out + _record(head + bytes(f"{count:04d}", "ascii") + b"00000000000000000000")
    names_block = b""
    position = 0
    long_labels: "list[int]" = []
    for place in range(count):
        column = form.columns[place]
        text = stats[place].text
        if text:
            fallback = ("", 0, 0)
        elif column.written_as == native.WRITTEN_DATE:
            fallback = ("DATE", 9, 0)
        elif column.written_as == native.WRITTEN_STAMP:
            fallback = ("DATETIME", 20 if not column.fraction else 21 + column.fraction, column.fraction)
        elif column.written_as == native.WRITTEN_CLOCK:
            fallback = ("TIME", 8, 0)
        else:
            fallback = ("", 0, 0)
        shown = _sas_format(column.display, fallback)
        label = column.label if column.label is not None else ""
        name_bytes = bytes(names[place], "utf-8")
        label_bytes = bytes(label, "utf-8")
        entry = (
            _big16(_XPORT_TEXT if text else _XPORT_NUMERIC) + _big16(0) + _big16(lengths[place])
            + _big16(place + 1) + _ascii_padded(names[place], 8) + _ascii_padded(label, 40)
            + _ascii_padded(shown[0], 8) + _big16(shown[1]) + _big16(shown[2]) + _big16(0 if text else 1)
            + bytes(2) + b" " * 8 + _big16(0) + _big16(0) + native.big(position, 4)
        )
        if long_form:
            entry = entry + _ascii_padded(names[place], 32) + _big16(len(label_bytes)) + bytes(18)
            # A long NAME stands in the namestr's own 32 bytes; a label past
            # 40 bytes needs a LABELV8 record of its own.
            if len(label_bytes) > 40:
                long_labels += [place]
        else:
            entry = entry + bytes(52)
        names_block = names_block + entry
        position = position + lengths[place]
    if len(names_block) % 80:
        names_block = names_block + b" " * (80 - len(names_block) % 80)
    out = out + names_block
    if long_form and long_labels:
        out = out + _record(
            b"HEADER RECORD*******LABELV8 HEADER RECORD!!!!!!!" + bytes(f"{len(long_labels):<30d}", "ascii")
        )
        block = b""
        for place in long_labels:
            said = form.columns[place].label
            name_bytes = bytes(names[place], "utf-8")
            label_bytes = bytes(said if said is not None else "", "utf-8")
            block = block + _big16(place + 1) + _big16(len(name_bytes)) + _big16(len(label_bytes)) + name_bytes + label_bytes
        if len(block) % 80:
            block = block + b" " * (80 - len(block) % 80)
        out = out + block
    if long_form:
        # Version 8 names its observations' count in the header.
        out = out + _record(
            b"HEADER RECORD*******OBSV8   HEADER RECORD!!!!!!!" + bytes(f"{n_rows:15d}", "ascii") + b" " * 17
        )
    else:
        out = out + _record(b"HEADER RECORD*******OBS     HEADER RECORD!!!!!!!000000000000000000000000000000")
    data = bytearray()
    for row in range(n_rows):
        for place in range(count):
            value = stats[place].values[row]
            if stats[place].text:
                cell = value if isinstance(value, bytes) else b""
                data += cell + b" " * (lengths[place] - len(cell))
                continue
            encoded = _xport_number(value, lengths[place])
            if encoded is None:
                raise _refused(names[place], "a number does not fit the column's length")
            data += encoded
    if len(data) % 80:
        data += b" " * (80 - len(data) % 80)
    return Written(data=out + bytes(data), widened=tuple(widened))
