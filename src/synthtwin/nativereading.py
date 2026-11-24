"""Reading a file from another system: Parquet, SAS, Stata, SPSS (lane FORMATS).

ZONE R. This module opens the person's table, as `reading` does, and is
reached from `reading.read_table` alone; nothing on the generation path
imports it. It hands back the table as TEXT -- one list of cells a
column, every cell the text `native` writes for the value stored there
-- beside the file's own form (`native.NativeForm`), whose labels and
names are still the file's own: what may be published of them is
decided by the profile (`profile._published_native`), which knows the
floor and each column's role.

THE LIBRARIES, AND WHAT EACH IS HANDED. A Parquet file's VALUES are read
by pyarrow's Parquet reader (`pyarrow.parquet.read_table`) on one thread;
its footer -- the names, the types, the row count, the pairs of text it
carries -- is read here with the standard library (`native.parquet_footer`)
from the file's last bytes, and the two readings are held to each other:
the same number of columns and of rows, or a refusal. A SAS, Stata or
SPSS file is read by pyreadstat (`read_sas7bdat`, `read_xport`, `read_dta`,
`read_sav`) with `output_format="dict"`, which hands back plain Python
lists, and `disable_datetime_conversion=True`, which hands back each date
as the number the file stores, so the date arithmetic is this package's
own, in whole numbers. Both readers are fenced as `pandas.read_csv` is:
the path they are handed has passed `validate_local_path` in the same
function, which refuses a URL before any file is opened.

THE FILE IS READ ONCE, BY ONE LIBRARY, as a workbook is read once by the
standard library (`reading._read_workbook_table`): no second reader of
these formats is admitted, and what stands in for one is the round trip
the tests run -- an invented table written by the libraries, read here,
described, its twin written by `nativewriting` and read back by the
libraries and by pandas -- and the footer check above.

WHAT IS HELD. Every column's cells, as text, a spelling held once a
column (`_Spellings`): the table is held whole, as a workbook's is, not
a group of columns at a time as a delimited file read in groups is
(lane SR). A native file's values are typed and compact on disk, so the
cells cost more in memory than the file does; the measured price is in
the lane's report.

Guarantees: `read_native` returns a `NativeReading` or raises
`errors.ProfileError` with a plain sentence; it never writes, never
consults a clock, an environment variable or a random source; the same
file gives the same reading.
"""

import dataclasses
import pathlib

import pyarrow.parquet
import pyreadstat

from synthtwin import errors, native
from synthtwin.paths import validate_local_path

# The systems' names, as a refusal says them.
SYSTEM_WORDS = {
    native.FORMAT_PARQUET: "Parquet",
    native.FORMAT_SAS_DATASET: "SAS dataset (.sas7bdat)",
    native.FORMAT_SAS_TRANSPORT: "SAS transport (.xpt)",
    native.FORMAT_SPSS: "SPSS (.sav)",
    native.FORMAT_STATA: "Stata (.dta)",
    native.KIND_ARROW: "Arrow (Feather)",
    native.KIND_ORC: "ORC",
    native.KIND_SPSS_PORTABLE: "SPSS portable (.por)",
}

# The most bytes of a Parquet file's end held to find its footer.
_FOOTER_MOST = 64 * 1024 * 1024


@dataclasses.dataclass(frozen=True)
class NativeReading:
    """One native file read as text, with its own form (labels not yet held to any rule)."""

    system: str
    version: int
    names: "tuple[str, ...]"
    columns: "list[list[str]]"
    n_rows: int
    form: native.NativeForm


@dataclasses.dataclass
class _Spellings:
    """The texts a column holds once (each repeated spelling one object)."""

    held: "dict[str, str]"


def _once(memo: _Spellings, text: str) -> str:
    if text in memo.held:
        return memo.held[text]
    memo.held[text] = text
    return text


def read_native(
    raw_path: str, system: str, opening: bytes, published: "native.NativeForm | None" = None
) -> NativeReading:
    """The table in a native file at ``raw_path``, as text, with its form.

    ``system`` is `native.kind_of` of the file's opening bytes and
    ``opening`` those bytes (a format's version is read off them).
    ``published`` is the native block of the description a checked file
    is held to (`synthtwin validate`): each column's numbers are written
    with the decimal places, and its stamps with the fraction of a
    second, that block publishes wherever they write every value exactly,
    so a twin is read back spelled as it was drawn. Without it, each
    width is the fewest that writes every value of the column exactly.
    Guarantees: the path passes the locality gate here, again, before any
    reader is handed it. Raises ProfileError, in words a person can act
    on, for a file its reader cannot open, a kind no reader is admitted
    for, a nested Parquet column, a column kept in another file, a type
    with no reading, and a date outside the years 1 to 9999.
    """
    validated = validate_local_path(raw_path, purpose="input")
    shown = f"{pathlib.Path(validated)}"
    if system not in native.FORMATS:
        raise errors.ProfileError(
            errors.native_without_a_reader(shown, SYSTEM_WORDS[system] if system in SYSTEM_WORDS else system)
        )
    if system == native.FORMAT_PARQUET:
        return _read_parquet(raw_path, shown, published)
    return _read_stat(raw_path, shown, system, opening, published)


def _given(published: "native.NativeForm | None", place: int) -> "native.NativeColumn | None":
    """The published entry of column ``place``, where a description gives one."""
    if published is None or place >= len(published.columns):
        return None
    return published.columns[place]


def _places_for(numbers: "list[float | None]", single: bool, given: "native.NativeColumn | None") -> "int | None":
    """The decimal places a column of numbers is written with: the published count where it is exact, else the fewest."""
    present = [number for number in numbers if number is not None]
    if given is not None and given.places is not None:
        exact = True
        for number in present:
            text = native.fixed_text(number, given.places)
            back = native.exact_single(text) if single else native.exact_double(text)
            if back is None or native.double_bits(back) != native.double_bits(number):
                exact = False
                break
        if exact:
            return given.places
    return native.places_needed(present, single)


# -- Parquet ----------------------------------------------------------


def _file_tail(raw_path: str, most: int) -> bytes:
    """The file's last bytes, at most ``most`` of them, read a line at a time and never held whole.

    Read as Latin-1, whose characters are the file's bytes one for one,
    as `reading._opening_of` reads a file's first bytes; the path is
    validated again here, immediately before it is opened.
    """
    validated = validate_local_path(raw_path, purpose="input")
    file_path = pathlib.Path(validated)
    pieces: "list[bytes]" = []
    first = 0
    held = 0
    with file_path.open("r", encoding="latin-1", newline="") as handle:
        for line in handle:
            data = bytes(line, "latin-1")
            pieces += [data]
            held = held + len(data)
            while len(pieces) - first > 1 and held - len(pieces[first]) >= most:
                held = held - len(pieces[first])
                pieces[first] = b""
                first = first + 1
            if first > 4096:
                pieces = pieces[first:]
                first = 0
    tail = bytearray()
    for data in pieces[first:]:
        tail += data
    if len(tail) > most:
        return bytes(tail[len(tail) - most :])
    return bytes(tail)


def _parquet_footer(raw_path: str, shown: str) -> native.ParquetFooter:
    try:
        tail = _file_tail(raw_path, _FOOTER_MOST)
    except OSError as error:
        raise errors.ProfileError(errors.file_unreadable(shown, f"{error}")) from error
    words = SYSTEM_WORDS[native.FORMAT_PARQUET]
    if len(tail) < 12 or tail[len(tail) - 4 :] != b"PAR1":
        raise errors.ProfileError(errors.native_unreadable(shown, words))
    size = native.from_little(tail[len(tail) - 8 : len(tail) - 4])
    if size <= 0 or size + 8 > len(tail):
        raise errors.ProfileError(errors.native_unreadable(shown, words))
    footer = native.parquet_footer(tail[len(tail) - 8 - size : len(tail) - 8])
    if footer.refused == native.PARQUET_NESTED:
        raise errors.ProfileError(errors.native_column_nested(shown, footer.refused_column))
    if footer.refused == native.PARQUET_ELSEWHERE:
        raise errors.ProfileError(errors.native_column_elsewhere(shown))
    if footer.refused == native.PARQUET_UNKNOWN_TYPE:
        raise errors.ProfileError(errors.native_column_type_unknown(shown, footer.refused_column))
    if footer.refused:
        raise errors.ProfileError(errors.native_unreadable(shown, words))
    return footer


def _read_parquet(raw_path: str, shown: str, published: "native.NativeForm | None") -> NativeReading:
    validated = validate_local_path(raw_path, purpose="input")
    footer = _parquet_footer(raw_path, shown)
    words = SYSTEM_WORDS[native.FORMAT_PARQUET]
    try:
        table = pyarrow.parquet.read_table(validated, use_threads=False)
    except OSError as error:
        raise errors.ProfileError(errors.native_unreadable(shown, words)) from error
    except ValueError as error:
        raise errors.ProfileError(errors.native_unreadable(shown, words)) from error
    rows = int(table.num_rows)
    if rows != footer.rows or int(table.num_columns) != len(footer.leaves):
        raise errors.ProfileError(errors.native_unreadable(shown, words))
    typed: "dict[str, native.PandasColumn]" = {}
    index: "native.NativeIndex | None" = None
    zones: "dict[str, str]" = {}
    for key, text in footer.pairs:
        if key == native.PANDAS_KEY:
            typed, index, zones = native.pandas_fields(text)
    names: "list[str]" = []
    columns: "list[list[str]]" = []
    forms: "list[native.NativeColumn]" = []
    for place in range(len(footer.leaves)):
        leaf = footer.leaves[place]
        values: "list[object]" = []
        categorical = leaf.name in typed and typed[leaf.name].pandas_type == "categorical"
        categories: "list[str]" = []
        column = table.column(place)
        for piece in range(int(column.num_chunks)):
            piece_array = column.chunk(piece)
            chunk = piece_array.to_pylist()
            if not isinstance(chunk, list):
                raise errors.ProfileError(errors.native_unreadable(shown, words))
            values += chunk
            if categorical:
                # A categorical's categories, in the order its file keeps
                # them: the dictionary of each piece, read where pyarrow
                # read the column as one (its own schema says so).
                try:
                    kept = piece_array.dictionary.to_pylist()
                except AttributeError:
                    kept = []
                if isinstance(kept, list):
                    for item in kept:
                        if isinstance(item, str) and item not in categories:
                            categories += [item]
        if len(values) != rows:
            raise errors.ProfileError(errors.native_unreadable(shown, words))
        cells, written, fraction, places = _parquet_cells(values, leaf, shown, _given(published, place))
        names += [leaf.name]
        columns += [cells]
        forms += [
            native.NativeColumn(
                storage=leaf.store,
                written_as=written,
                width=leaf.type_length if leaf.physical == native.PHYSICAL_FIXED else None,
                precision=leaf.precision if leaf.store == native.STORE_DECIMAL else None,
                scale=leaf.scale if leaf.store == native.STORE_DECIMAL else None,
                fraction=fraction,
                utc=leaf.utc if leaf.store in native.PER_SECOND else None,
                zone=zones[leaf.name] if leaf.name in zones else None,
                required=leaf.repetition == native.REQUIRED,
                pandas=typed[leaf.name] if leaf.name in typed else None,
                places=places,
                categories=tuple(categories) if categorical and categories else None,
            )
        ]
    form = native.NativeForm(
        system=native.FORMAT_PARQUET,
        version=1,
        columns=tuple(forms),
        index=index,
    )
    return NativeReading(
        system=native.FORMAT_PARQUET,
        version=1,
        names=tuple(names),
        columns=columns,
        n_rows=rows,
        form=form,
    )


def _parquet_cells(
    values: "list[object]", leaf: native.ParquetLeaf, shown: str, given: "native.NativeColumn | None"
) -> "tuple[list[str], str, int, int | None]":
    """A Parquet column's values as text: (cells, how they are written, the fraction's width, the decimal places)."""
    memo = _Spellings(held={})
    store = leaf.store
    cells: "list[str]" = []
    if store == native.STORE_BOOLEAN:
        for value in values:
            if value is None:
                cells += [""]
            else:
                cells += [native.FLAG_TRUE if value is True else native.FLAG_FALSE]
        return (cells, native.WRITTEN_FLAG, 0, None)
    if store in native.INTEGER_RANGES:
        for value in values:
            cells += ["" if value is None else _once(memo, native.whole_text(int(f"{value}")))]
        return (cells, native.WRITTEN_WHOLE, 0, None)
    if store in (native.STORE_FLOAT32, native.STORE_FLOAT64):
        single = store == native.STORE_FLOAT32
        numbers: "list[float | None]" = [None if value is None else float(f"{value!r}") for value in values]
        places = _places_for(numbers, single, given)
        for number in numbers:
            cells += ["" if number is None else _once(memo, native.number_text(number, places, single))]
        return (cells, native.WRITTEN_SINGLE if single else native.WRITTEN_NUMBER, 0, places)
    if store == native.STORE_STRING:
        for value in values:
            if value is None:
                cells += [""]
            elif isinstance(value, str):
                cells += [_once(memo, value)]
            else:
                raise errors.ProfileError(errors.native_column_type_unknown(shown, leaf.name))
        return (cells, native.WRITTEN_TEXT, 0, None)
    if store == native.STORE_DECIMAL:
        for value in values:
            cells += ["" if value is None else _once(memo, f"{value:f}")]
        return (cells, native.WRITTEN_DECIMAL, 0, None)
    if store == native.STORE_DATE:
        for value in values:
            if value is None:
                cells += [""]
                continue
            text = f"{value}"
            if native.date_of_text(text) is None:
                raise errors.ProfileError(errors.native_dates_out_of_range(shown, leaf.name))
            cells += [_once(memo, text)]
        return (cells, native.WRITTEN_DATE, 0, None)
    if store in native.PER_SECOND:
        moments, written, width = _parquet_moments(values, leaf, shown, given)
        return (moments, written, width, None)
    raise errors.ProfileError(errors.native_column_type_unknown(shown, leaf.name))


def _moment_parts(text: str) -> "tuple[int, int, int, int, int] | None":
    """(days, seconds into the day, the fraction's figures, its width, the offset in seconds) of a library's stamp or clock text."""
    if not isinstance(text, str):
        raise TypeError("internal check: a stamp was not text")
    offset = 0
    body = text
    if len(text) >= 6 and text[len(text) - 6] in "+-" and text[len(text) - 3] == ":":
        sign = -1 if text[len(text) - 6] == "-" else 1
        hours = text[len(text) - 5 : len(text) - 3]
        minutes = text[len(text) - 2 :]
        clock = native.clock_of_text(f"{hours}:{minutes}:00")
        if clock is None:
            return None
        offset = sign * clock[0]
        body = text[: len(text) - 6]
    cut = body.find(" ")
    if cut < 0:
        clock = native.clock_of_text(body)
        if clock is None:
            return None
        return (0, clock[0], clock[1], clock[2], offset)
    days = native.date_of_text(body[:cut])
    clock = native.clock_of_text(body[cut + 1 :])
    if days is None or clock is None:
        return None
    return (days, clock[0], clock[1], clock[2], offset)


def _fraction_for(found: int, given: "native.NativeColumn | None") -> int:
    """The fraction of a second's width: the published one where it holds every value (it is no narrower), else the fewest."""
    if given is not None and given.fraction >= found:
        return given.fraction
    return found


def _parquet_moments(
    values: "list[object]", leaf: native.ParquetLeaf, shown: str, given: "native.NativeColumn | None"
) -> "tuple[list[str], str, int]":
    """A timestamp or time-of-day column as text, at one fraction width, universal time where it is kept so."""
    per_second = native.PER_SECOND[leaf.store]
    clock_only = leaf.store in (native.STORE_TIME_MS, native.STORE_TIME_US, native.STORE_TIME_NS)
    totals: "list[int | None]" = []
    fractions: "list[int]" = []
    for value in values:
        if value is None:
            totals += [None]
            continue
        parts = _moment_parts(f"{value}")
        if parts is None:
            raise errors.ProfileError(errors.native_dates_out_of_range(shown, leaf.name))
        days, seconds, figures, written_width, offset = parts
        units = native.units_of_figures(figures, written_width, per_second)
        if units is None:
            raise errors.ProfileError(errors.native_column_type_unknown(shown, leaf.name))
        total = (days * 86400 + seconds - offset) * per_second + units
        totals += [total]
        fractions += [units]
    found_width = native.fraction_width(fractions, per_second)
    if found_width is None:
        raise errors.ProfileError(errors.native_column_type_unknown(shown, leaf.name))
    width = _fraction_for(found_width, given)
    memo = _Spellings(held={})
    cells: "list[str]" = []
    for counted in totals:
        if counted is None:
            cells += [""]
            continue
        days, seconds, units = native.split_units(counted, per_second)
        figures = native.units_text(units, per_second, width)
        if clock_only:
            cells += [_once(memo, native.clock_text(seconds, figures, width))]
            continue
        text = native.stamp_text(days, seconds, figures, width)
        if leaf.utc:
            text = f"{text}+00:00"
        cells += [_once(memo, text)]
    return (cells, native.WRITTEN_CLOCK if clock_only else native.WRITTEN_STAMP, width)


# -- SAS, Stata and SPSS -----------------------------------------------

# The display formats whose numbers are days, seconds or clock times,
# by the name before the width (the systems' own words).
_SAS_DAY_FORMATS = (
    "DATE", "DAY", "DDMMYY", "DDMMYYB", "DDMMYYC", "DDMMYYD", "DDMMYYN",
    "DDMMYYP", "DDMMYYS", "DOWNAME", "E8601DA", "IS8601DA", "JULDATE",
    "JULIAN", "MMDDYY", "MMDDYYB", "MMDDYYC", "MMDDYYD", "MMDDYYN",
    "MMDDYYP", "MMDDYYS", "MMYY", "MONNAME", "MONTH", "MONYY", "NLDATE",
    "QTR", "WEEKDATE", "WEEKDATX", "WEEKDAY", "WORDDATE", "WORDDATX",
    "YEAR", "YYMM", "YYMMDD", "YYMMDDB", "YYMMDDC", "YYMMDDD", "YYMMDDN",
    "YYMMDDP", "YYMMDDS", "YYMON", "YYQ",
)
_SAS_SECOND_FORMATS = ("DATEAMPM", "DATETIME", "DTDATE", "E8601DN", "E8601DT", "IS8601DN", "IS8601DT")
_SAS_CLOCK_FORMATS = ("E8601TM", "HHMM", "HOUR", "IS8601TM", "MMSS", "TIME", "TIMEAMPM", "TOD")
_SPSS_DAY_FORMATS = ("ADATE", "DATE", "EDATE", "JDATE", "MOYR", "QYR", "SDATE", "WKYR")
_SPSS_SECOND_FORMATS = ("DATETIME", "YMDHMS")
_SPSS_CLOCK_FORMATS = ("MTIME", "TIME")

_PER_MICROSECOND = 1000000
_DAYS = "days"
_SECONDS = "seconds"
_MILLISECONDS = "milliseconds"
_CLOCK = "clock"
_PLAIN = ""

_STATA_STORES = {
    "int8": native.STORE_STATA_BYTE,
    "int16": native.STORE_STATA_INT,
    "int32": native.STORE_STATA_LONG,
    "float": native.STORE_STATA_FLOAT,
    "double": native.STORE_STATA_DOUBLE,
    "string": native.STORE_TEXT,
}


def _format_name(code: str) -> str:
    """A SAS or SPSS format code's name: the letters before its width."""
    if not isinstance(code, str):
        raise TypeError("internal check: a format code was not text")
    cut = len(code)
    while cut > 0 and (48 <= ord(code[cut - 1]) <= 57 or code[cut - 1] == "."):
        cut = cut - 1
    return code[:cut].upper()


def _time_kind(system: str, code: object) -> str:
    """Which numbers a column's display format says it holds: days, seconds, milliseconds, a clock, or plain numbers."""
    if not isinstance(code, str) or not code:
        return _PLAIN
    return _time_kind_of(system, code)


def _time_kind_of(system: str, code: str) -> str:
    if not isinstance(code, str):
        raise TypeError("internal check: a format code was not text")
    if system == native.FORMAT_STATA:
        tail = code[1:].lstrip("-0")
        if tail.startswith("td") or tail.startswith("d"):
            return _DAYS
        if tail.startswith("tc") or tail.startswith("tC"):
            return _MILLISECONDS
        return _PLAIN
    name = _format_name(code)
    if system == native.FORMAT_SPSS:
        if name in _SPSS_DAY_FORMATS:
            return _DAYS
        if name in _SPSS_SECOND_FORMATS:
            return _SECONDS
        if name in _SPSS_CLOCK_FORMATS:
            return _CLOCK
        return _PLAIN
    if name in _SAS_DAY_FORMATS:
        return _DAYS
    if name in _SAS_SECOND_FORMATS:
        return _SECONDS
    if name in _SAS_CLOCK_FORMATS:
        return _CLOCK
    return _PLAIN


def _version_of(system: str, opening: bytes) -> int:
    """The format's own version, read off the opening bytes."""
    if system == native.FORMAT_STATA:
        if opening[:11] == b"<stata_dta>":
            release = opening[28:31]
            if release in (b"117", b"118", b"119"):
                return int(str(release, "ascii"))
            return 118
        return opening[0]
    if system == native.FORMAT_SPSS:
        return 3 if opening[:4] == b"$FL3" else 2
    if system == native.FORMAT_SAS_TRANSPORT:
        return 8 if opening[20:25] == b"LIBV8" else 5
    return 0


def _read_stat(
    raw_path: str, shown: str, system: str, opening: bytes, published: "native.NativeForm | None"
) -> NativeReading:
    validated = validate_local_path(raw_path, purpose="input")
    words = SYSTEM_WORDS[system]
    try:
        if system == native.FORMAT_STATA:
            found = pyreadstat.read_dta(
                validated, output_format="dict", disable_datetime_conversion=True, user_missing=True
            )
        elif system == native.FORMAT_SPSS:
            found = pyreadstat.read_sav(
                validated, output_format="dict", disable_datetime_conversion=True, user_missing=True
            )
        elif system == native.FORMAT_SAS_DATASET:
            found = pyreadstat.read_sas7bdat(
                validated, output_format="dict", disable_datetime_conversion=True, user_missing=True
            )
        else:
            found = pyreadstat.read_xport(
                validated, output_format="dict", disable_datetime_conversion=True
            )
    except pyreadstat.ReadstatError as error:
        raise errors.ProfileError(errors.native_unreadable(shown, words)) from error
    except pyreadstat.PyreadstatError as error:
        raise errors.ProfileError(errors.native_unreadable(shown, words)) from error
    except OSError as error:
        raise errors.ProfileError(errors.native_unreadable(shown, words)) from error
    # Everything below is plain Python: each list and mapping is copied
    # out of what the library handed back, and checked to be one. The
    # read hands back the data and the metadata as one pair.
    data = found[0]
    meta = found[1]
    names_found = meta.column_names.copy()
    labels_found = meta.column_labels.copy()
    kinds_found = meta.readstat_variable_types.copy()
    formats_found = meta.original_variable_types.copy()
    widths_found = meta.variable_storage_width.copy()
    value_labels_found = meta.variable_value_labels.copy()
    label_sets_found = meta.variable_to_label.copy()
    ranges_found = meta.missing_ranges.copy()
    measures_found = meta.variable_measure.copy()
    table_found = meta.table_name
    for held in (names_found, labels_found):
        if not isinstance(held, list):
            raise errors.ProfileError(errors.native_unreadable(shown, words))
    for mapping in (kinds_found, formats_found, widths_found, value_labels_found, label_sets_found,
                    ranges_found, measures_found):
        if not isinstance(mapping, dict):
            raise errors.ProfileError(errors.native_unreadable(shown, words))
    names: "list[str]" = []
    for name in names_found:
        if not isinstance(name, str):
            raise errors.ProfileError(errors.native_unreadable(shown, words))
        names += [name]
    rows = -1
    columns: "list[list[str]]" = []
    forms: "list[native.NativeColumn]" = []
    for place in range(len(names)):
        name = names[place]
        values = data[name].copy()
        if not isinstance(values, list):
            raise errors.ProfileError(errors.native_unreadable(shown, words))
        if rows < 0:
            rows = len(values)
        if len(values) != rows:
            raise errors.ProfileError(errors.native_unreadable(shown, words))
        kind = kinds_found[name] if name in kinds_found else "double"
        code = formats_found[name] if name in formats_found else None
        if system == native.FORMAT_STATA:
            storage = _STATA_STORES[kind] if kind in _STATA_STORES else native.STORE_STATA_DOUBLE
        else:
            storage = native.STORE_TEXT if kind == "string" else native.STORE_NUMBER
        cells, written, fraction, places = _stat_cells(
            values, storage, _time_kind(system, code), system, name, shown, _given(published, place)
        )
        width = _text_width(
            system, storage, widths_found[name] if name in widths_found else None, code
        )
        label = labels_found[place] if place < len(labels_found) else None
        coded = value_labels_found[name] if name in value_labels_found else None
        pairs: "list[tuple[str, str]]" = []
        if isinstance(coded, dict):
            for key in coded:
                text = coded[key]
                if not isinstance(text, str):
                    continue
                if isinstance(key, str):
                    pairs += [(key, text)]
                elif isinstance(key, (int, float)) and not isinstance(key, bool):
                    pairs += [(native.double_text(float(key)), text)]
        missing = _spss_missing(ranges_found[name] if name in ranges_found else None, storage)
        measure = measures_found[name] if name in measures_found else None
        columns += [cells]
        forms += [
            native.NativeColumn(
                storage=storage,
                written_as=written,
                width=width if isinstance(width, int) and not isinstance(width, bool) else None,
                fraction=fraction,
                display=code if isinstance(code, str) and code else None,
                label=label if isinstance(label, str) and label else None,
                label_set=(
                    label_sets_found[name]
                    if name in label_sets_found and isinstance(label_sets_found[name], str)
                    else None
                ),
                value_labels=tuple(pairs) if pairs else None,
                missing=missing,
                measure=measure if measure in native.MEASURES else None,
                places=places,
            )
        ]
    if rows < 0:
        rows = 0
    version = _version_of(system, opening)
    form = native.NativeForm(
        system=system,
        version=version if version in native.VERSIONS[system] else native.VERSIONS[system][0],
        columns=tuple(forms),
        table_name=table_found if isinstance(table_found, str) and table_found else None,
    )
    return NativeReading(
        system=system,
        version=form.version,
        names=tuple(names),
        columns=columns,
        n_rows=rows,
        form=form,
    )


def _text_width(system: str, storage: str, stored: object, code: object) -> "int | None":
    """A column's width as its system declares it: a text's bytes, a SAS number's length, or None.

    pyreadstat reports each system's own storage: Stata a text's bytes
    and one more (its terminating byte), SPSS a text's eight-byte slots
    (its `A` format holds the width itself), SAS the declared length of
    a text or of a number (3 to 8 bytes).
    """
    if isinstance(stored, bool) or not isinstance(stored, int):
        return None
    if system == native.FORMAT_STATA:
        if storage != native.STORE_TEXT:
            return None
        return stored - 1 if stored > 1 else stored
    if system == native.FORMAT_SPSS:
        if storage != native.STORE_TEXT:
            return None
        if isinstance(code, str):
            declared = _format_width(code)
            if declared is not None:
                return declared
        return stored
    return stored


def _format_width(code: str) -> "int | None":
    """The width an SPSS text format `A<width>` declares, or None."""
    if not isinstance(code, str):
        raise TypeError("internal check: a format code was not text")
    if len(code) < 2 or code[0] != "A":
        return None
    figures = code[1:]
    for character in figures:
        if not 48 <= ord(character) <= 57:
            return None
    return int(figures)


def _spss_missing(found: object, storage: str) -> "native.NativeMissing | None":
    """SPSS's user-missing values of one column, as pyreadstat reports them, written as text."""
    if not isinstance(found, list) or not found:
        return None
    values: "list[str]" = []
    low: "str | None" = None
    high: "str | None" = None
    for entry in found:
        if not isinstance(entry, dict) or "lo" not in entry or "hi" not in entry:
            continue
        lo = entry["lo"]
        hi = entry["hi"]
        if storage == native.STORE_TEXT:
            if isinstance(lo, str):
                values += [lo]
            continue
        if isinstance(lo, bool) or isinstance(hi, bool):
            continue
        if not isinstance(lo, (int, float)) or not isinstance(hi, (int, float)):
            continue
        if lo == hi:
            values += [native.double_text(float(lo))]
        else:
            low = native.double_text(float(lo))
            high = native.double_text(float(hi))
    if not values and low is None:
        return None
    return native.NativeMissing(values=tuple(values[:3]), low=low, high=high)


def _exact_units(value: float, per: int) -> "int | None":
    """``value`` times ``per`` as a whole number, where that product is one exactly (no rounding)."""
    if value != value or value in (float("inf"), float("-inf")):
        return None
    scaled = value * per
    whole = int(scaled)
    if whole != scaled:
        return None
    # The product of a double and a whole number is rounded: it is exact
    # only where dividing back gives the same double.
    if float(whole) / per != value:
        return None
    return whole


def _stat_cells(
    values: "list[object]", storage: str, time_kind: str, system: str, name: str, shown: str,
    given: "native.NativeColumn | None",
) -> "tuple[list[str], str, int, int | None]":
    """A SAS, Stata or SPSS column as text: (cells, how written, the fraction's width, the decimal places)."""
    memo = _Spellings(held={})
    cells: "list[str]" = []
    stata = system == native.FORMAT_STATA
    if storage == native.STORE_TEXT:
        for value in values:
            cells += ["" if value is None else _once(memo, f"{value}")]
        return (cells, native.WRITTEN_TEXT, 0, None)
    if time_kind:
        dated = _dated_cells(values, time_kind, system, stata, given)
        if dated is not None:
            return (dated[0], dated[1], dated[2], None)
    single = storage == native.STORE_STATA_FLOAT
    whole = storage in (native.STORE_STATA_BYTE, native.STORE_STATA_INT, native.STORE_STATA_LONG)
    numbers: "list[float | None]" = []
    specials: "list[str]" = []
    for value in values:
        if value is None:
            numbers += [None]
            specials += [""]
        elif isinstance(value, str):
            special = native.special_missing_text(value, stata)
            numbers += [None]
            specials += [special if special is not None else ""]
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            numbers += [float(value)]
            specials += [""]
        else:
            raise errors.ProfileError(errors.native_column_type_unknown(shown, name))
    places: "int | None" = None
    if whole:
        places = 0
    else:
        places = _places_for(numbers, single, given)
    for place in range(len(numbers)):
        number = numbers[place]
        if number is None:
            cells += [_once(memo, specials[place]) if specials[place] else ""]
        else:
            cells += [_once(memo, native.number_text(number, places, single))]
    if single:
        return (cells, native.WRITTEN_SINGLE, 0, places)
    return (cells, native.WRITTEN_WHOLE if whole else native.WRITTEN_NUMBER, 0, None if whole else places)


def _dated_cells(
    values: "list[object]", time_kind: str, system: str, stata: bool, given: "native.NativeColumn | None"
) -> "tuple[list[str], str, int] | None":
    """A column of dates, stamps or clock times as text, or None where some value is not one exactly.

    Every present value must be written exactly -- a day count a whole
    number of days, a Stata stamp a whole number of milliseconds, a SAS
    or SPSS stamp or clock a number of seconds whose microseconds are
    whole -- or the column is written as plain numbers instead, its
    display format kept, and nothing is rounded. A year outside 1 to
    9999 does the same.
    """
    day_zero = native.SPSS_EPOCH_DAYS if system == native.FORMAT_SPSS else native.DAYS_1960
    counts: "list[int | None]" = []
    specials: "list[str | None]" = []
    for value in values:
        if value is None:
            counts += [None]
            specials += [None]
            continue
        if isinstance(value, str):
            counts += [None]
            specials += [native.special_missing_text(value, stata)]
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return None
        number = float(value)
        if time_kind == _DAYS:
            counted = _exact_units(number, 1)
            if counted is None:
                return None
            if system == native.FORMAT_SPSS:
                if counted % 86400:
                    return None
                counted = counted // 86400
        elif time_kind == _MILLISECONDS:
            counted = _exact_units(number, 1)
            if counted is None:
                return None
            counted = counted * 1000
        else:
            # The smallest unit that holds the value exactly, whole seconds
            # first: SPSS counts seconds from 1582, so its stamps' counts in
            # microseconds pass 2 ** 53, where a double holds a whole number
            # exactly only every other step.
            counted = None
            for per in (1, 1000, _PER_MICROSECOND):
                exact = _exact_units(number, per)
                if exact is not None:
                    counted = exact * (_PER_MICROSECOND // per)
                    break
            if counted is None:
                return None
        counts += [counted]
        specials += [None]
    memo = _Spellings(held={})
    cells: "list[str]" = []
    if time_kind == _DAYS:
        for place in range(len(counts)):
            count = counts[place]
            if count is None:
                special = specials[place]
                cells += [_once(memo, special) if special is not None else ""]
                continue
            days = count + day_zero
            year = native.civil_from_days(days)[0]
            if year < 1 or year > 9999:
                return None
            cells += [_once(memo, native.date_text(days))]
        return (cells, native.WRITTEN_DATE, 0)
    fractions = [count % _PER_MICROSECOND for count in counts if count is not None]
    found_width = native.fraction_width(fractions, _PER_MICROSECOND)
    if found_width is None:
        return None
    width = _fraction_for(found_width, given)
    for place in range(len(counts)):
        count = counts[place]
        if count is None:
            special = specials[place]
            cells += [_once(memo, special) if special is not None else ""]
            continue
        if time_kind == _CLOCK:
            if count < 0 or count >= 86400 * _PER_MICROSECOND:
                return None
            figures = native.units_text(count % _PER_MICROSECOND, _PER_MICROSECOND, width)
            cells += [_once(memo, native.clock_text(count // _PER_MICROSECOND, figures, width))]
            continue
        days, seconds, part = native.split_units(count, _PER_MICROSECOND)
        days = days + day_zero
        year = native.civil_from_days(days)[0]
        if year < 1 or year > 9999:
            return None
        figures = native.units_text(part, _PER_MICROSECOND, width)
        cells += [_once(memo, native.stamp_text(days, seconds, figures, width))]
    return (cells, native.WRITTEN_CLOCK if time_kind == _CLOCK else native.WRITTEN_STAMP, width)
