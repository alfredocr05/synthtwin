"""Files from other systems: Parquet, SAS, Stata and SPSS (lane FORMATS).

The owner's ruling of 2026-11-23: synthtwin opens a table saved by
another system -- a Parquet file out of a warehouse, a SAS dataset or
transport file, a Stata `.dta`, an SPSS `.sav` -- describes it, and
writes the twin back in the same kind of file, so the code that loads
the real file loads the twin unchanged.

THIS MODULE OPENS NOTHING. It is the vocabulary the reader, the
description's loader and the twin's writer share, and it sits where the
loader may reach it: the loader is in the generator's import graph, and
the module that opens a table never is (plan P2-D1). What it holds:

1. WHICH KIND OF FILE a table's opening bytes begin (`kind_of`), decided
   by the bytes and never by the name, as `workbook.kind_of` decides a
   workbook.
2. HOW A STORED VALUE IS WRITTEN AS TEXT, and back (`whole_text`,
   `double_text`, `single_text`, `date_text`, `stamp_text` and their
   readers). The description is built from text, exactly as from a CSV
   file, so a native file's cells are rendered into the text a CSV
   export of the same table holds, by one documented rule a column, and
   every rendering is EXACT: the twin writer reads each text back into
   the very value it came from (`exact_double`, `exact_single`). A
   column of numbers is written with one count of decimal places
   (`places_needed`), the fewest that writes each value exactly, since a
   number stored in binary has no spelling of its own.
3. THE BITS OF A NUMBER, made with Python integers and the two exact
   `math` names the offline policy admits (`frexp`, `ldexp`): IEEE
   binary64 and binary32, and the IBM hexadecimal floats of a SAS
   transport file. No `struct`: the writer is zone W, which writes with
   the standard library's admitted names alone.
4. THRIFT'S COMPACT PROTOCOL, which a Parquet file's own description
   (its footer) is written in, read and written (`thrift_struct`,
   `thrift_bytes`), and the footer's facts (`parquet_footer`).
5. THE DESCRIPTION'S NATIVE BLOCK (`source.native`): what it may publish
   and the rules a published label, format, name or code is held to
   (`label_published`, `format_published`, `name_published`).

WHAT THE NATIVE BLOCK MAY CARRY, AND WHY (the third requirement of the
ruling: nothing of a file's own metadata may carry a real value or a
private name further than the same table in CSV would). A CSV file holds
column names and cells and nothing else, so everything a native file says
about itself is weighed here one field at a time:

- NEVER CARRIED: the file's own label and notes (SPSS documents, Stata
  notes and characteristics), who or what wrote it and when (creator,
  host, release, timestamps), file paths (a Parquet column chunk may
  name another file; such a file is refused), and every key-value pair a
  Parquet file carries except the pandas block, which is rebuilt from
  the fields this module names (`pandas_block`) rather than copied.
- CARRIED, BECAUSE THE CODE NEEDS THEM, each through a rule: the storage
  type of every column (a schema fact, no value), its display format
  where it is one of the format language's own words
  (`format_published`), a column's label where `label_published` admits
  its text, a value label where its code is held by at least the
  smallest group of cells AND its text is admitted, SPSS's missing-value
  codes (numbers the analyst chose, or a text the column's own cells
  publish), and a SAS transport file's member name where
  `name_published` admits it -- SAS code names the member to read it.
- `column_label_published` refuses a text holding a run of five figures
  or more (an identifier, a telephone number, a date written as digits),
  an at sign or a web address, a control character, or more than 256
  characters: a column's label is the same kind of text as its name.
  `label_published`, for a VALUE label, refuses those and every text the
  twin checks read as an identifier or a person's name (C4). A value
  label is a cell of the CSV the same file exports with its labels
  applied, so it is held to the same floor a published value is, and a
  column's labels are dropped whole where the description holds its
  values back (an identifier, a column held for Safe Harbor).

Guarantees of the whole module: pure functions of their arguments; no
clock, no environment, no random source; no I/O of any kind.
"""

import dataclasses
import json
import math

# -- 1. which kind of file -------------------------------------------

FORMAT_PARQUET = "parquet"
FORMAT_STATA = "stata"
FORMAT_SPSS = "spss"
FORMAT_SAS_TRANSPORT = "sas-transport"
FORMAT_SAS_DATASET = "sas-dataset"
FORMATS = (
    FORMAT_PARQUET,
    FORMAT_SAS_DATASET,
    FORMAT_SAS_TRANSPORT,
    FORMAT_SPSS,
    FORMAT_STATA,
)
# Recognised and refused with words of their own: no reader is admitted.
KIND_ARROW = "arrow"
KIND_ORC = "orc"
KIND_SPSS_PORTABLE = "spss-portable"
KIND_NONE = ""

# How many opening bytes `kind_of` reads: the longest mark is a SAS
# transport file's first record.
OPENING_BYTES = 80

_PARQUET_MARK = b"PAR1"
_STATA_MARK = b"<stata_dta>"
_SPSS_MARKS = (b"$FL2", b"$FL3")
_XPORT_V5_MARK = b"HEADER RECORD*******LIBRARY HEADER RECORD!!!!!!!"
_XPORT_V8_MARK = b"HEADER RECORD*******LIBV8   HEADER RECORD!!!!!!!"
# A SAS dataset's 32-byte magic number (the format's reverse-engineered
# description, and every reader's first check).
_SAS_DATASET_MARK = bytes(
    [0] * 12
    + [0xC2, 0xEA, 0x81, 0x60, 0xB3, 0x14, 0x11, 0xCF, 0xBD, 0x92, 0x08, 0x00]
    + [0x09, 0xC7, 0x31, 0x8C, 0x18, 0x1F, 0x10, 0x11]
)
_ARROW_MARK = b"ARROW1"
_ORC_MARK = b"ORC"
# Stata's releases before 117 open with the release number as one byte,
# then the byte order (1 high first, 2 low first), then 1 and 0.
_OLD_STATA_RELEASES = (113, 114, 115)

# The twin's file ending for each format. A SAS dataset's twin is a SAS
# transport file: no writer of the dataset format is admitted (see
# `twin_format`). TWIN_ENDINGS lists the four, each once.
TWIN_SUFFIXES = {
    FORMAT_PARQUET: "-twin.parquet",
    FORMAT_SAS_DATASET: "-twin.xpt",
    FORMAT_SAS_TRANSPORT: "-twin.xpt",
    FORMAT_SPSS: "-twin.sav",
    FORMAT_STATA: "-twin.dta",
}
TWIN_ENDINGS = ("-twin.dta", "-twin.parquet", "-twin.sav", "-twin.xpt")


def kind_of(opening: bytes) -> str:
    """Which native format these opening bytes begin, or KIND_NONE.

    Guarantees: a fixed function of the bytes (at most `OPENING_BYTES`
    of them are looked at); the name of the file is never consulted.
    Returns one of `FORMATS`, KIND_ARROW, KIND_ORC, KIND_SPSS_PORTABLE
    or KIND_NONE. Raises TypeError for anything but bytes. No I/O.
    """
    if not isinstance(opening, bytes):
        raise TypeError("internal check: a file's opening bytes were not bytes")
    # A Parquet file's mark is followed by its first page's header, a
    # Thrift structure whose first field is a whole number: the byte 0x15.
    # A delimited file whose first name begins `PAR1` is not one.
    if opening[:4] == _PARQUET_MARK and opening[4:5] == b"\x15":
        return FORMAT_PARQUET
    if opening[: len(_STATA_MARK)] == _STATA_MARK:
        return FORMAT_STATA
    if len(opening) >= 4 and opening[0] in _OLD_STATA_RELEASES and opening[1] in (1, 2):
        if opening[2] == 1 and opening[3] == 0:
            return FORMAT_STATA
    if opening[:4] in _SPSS_MARKS:
        return FORMAT_SPSS
    if opening[: len(_XPORT_V5_MARK)] in (_XPORT_V5_MARK, _XPORT_V8_MARK):
        return FORMAT_SAS_TRANSPORT
    if opening[: len(_SAS_DATASET_MARK)] == _SAS_DATASET_MARK:
        return FORMAT_SAS_DATASET
    if opening[: len(_ARROW_MARK)] == _ARROW_MARK:
        return KIND_ARROW
    if opening[:3] == _ORC_MARK:
        return KIND_ORC
    if b"SPSS PORT FILE" in opening[:80] or opening[:8] == b"ASCII SP":
        return KIND_SPSS_PORTABLE
    return KIND_NONE


def twin_format(source_format: str) -> str:
    """The format the twin of a table in ``source_format`` is written in.

    Every format writes its own, save a SAS dataset (.sas7bdat), whose
    twin is a SAS transport file (.xpt): its layout is not published by
    SAS, no admitted library writes it, and a dataset SAS cannot read
    would be worse than a transport file every SAS release, pandas
    (`read_sas`), R (`haven::read_xpt`) and pyreadstat read. This is a
    stated departure from writing the twin as the source; the code that
    reads the real dataset reads the twin by its own file's name.
    """
    if source_format == FORMAT_SAS_DATASET:
        return FORMAT_SAS_TRANSPORT
    return source_format


# -- 2. dates and times as whole numbers ------------------------------

# Days from 1970-01-01 to each system's day 0.
DAYS_1960 = -3653
# SPSS counts SECONDS from the start of 14 October 1582.
SPSS_EPOCH_DAYS = -141428
_SECONDS_A_DAY = 86400


def days_from_civil(year: int, month: int, day: int) -> int:
    """Days from 1970-01-01 to this day of the proleptic Gregorian calendar.

    Howard Hinnant's algorithm, in Python integers: exact for every
    year. Guarantees: a fixed function of the three numbers. Raises
    nothing; the caller checks the month and the day.
    """
    shifted = year - 1 if month <= 2 else year
    era = shifted // 400
    year_of_era = shifted - era * 400
    month_index = month - 3 if month > 2 else month + 9
    year_day = (153 * month_index + 2) // 5 + day - 1
    day_of_era = year_of_era * 365 + year_of_era // 4 - year_of_era // 100 + year_day
    return era * 146097 + day_of_era - 719468


def civil_from_days(days: int) -> "tuple[int, int, int]":
    """The (year, month, day) that many days after 1970-01-01; exact."""
    shifted = days + 719468
    era = shifted // 146097
    day_of_era = shifted - era * 146097
    year_of_era = (
        day_of_era - day_of_era // 1460 + day_of_era // 36524 - day_of_era // 146096
    ) // 365
    year = year_of_era + era * 400
    year_day = day_of_era - (365 * year_of_era + year_of_era // 4 - year_of_era // 100)
    month_index = (5 * year_day + 2) // 153
    day = year_day - (153 * month_index + 2) // 5 + 1
    month = month_index + 3 if month_index < 10 else month_index - 9
    if month <= 2:
        year = year + 1
    return (year, month, day)


def _days_in_month(year: int, month: int) -> int:
    if month == 2:
        leap = (year % 4 == 0 and year % 100 != 0) or year % 400 == 0
        return 29 if leap else 28
    if month in (4, 6, 9, 11):
        return 30
    return 31


def _figures_only(text: str) -> bool:
    """Whether ``text`` is one or more ASCII figures and nothing else."""
    if not isinstance(text, str):
        raise TypeError("internal check: figures were not text")
    if not text:
        return False
    for character in text:
        place = ord(character)
        if place < 48 or place > 57:
            return False
    return True


def _letter(character: str) -> bool:
    """Whether ``character`` is one ASCII letter."""
    if not isinstance(character, str):
        raise TypeError("internal check: a character was not text")
    if len(character) != 1:
        return False
    place = ord(character)
    return 65 <= place <= 90 or 97 <= place <= 122


def date_text(days: int) -> str:
    """The ISO date ``days`` after 1970-01-01: `YYYY-MM-DD`, the year four figures or more.

    A year below 1 is written with its sign (`-0001-12-31`), which no
    CSV writer of the four systems writes and no twin cell needs: the
    reader refuses a column holding one (`dates_in_range`).
    """
    year, month, day = civil_from_days(days)
    sign = "-" if year < 0 else ""
    return f"{sign}{abs(year):04d}-{month:02d}-{day:02d}"


def date_of_text(text: str) -> "int | None":
    """The days after 1970-01-01 an ISO date names, or None where it names none."""
    if not isinstance(text, str):
        raise TypeError("internal check: a date was not text")
    if len(text) < 10 or text[len(text) - 6] != "-" or text[len(text) - 3] != "-":
        return None
    year_text = text[: len(text) - 6]
    month_text = text[len(text) - 5 : len(text) - 3]
    day_text = text[len(text) - 2 :]
    if not (_figures_only(year_text) and _figures_only(month_text) and _figures_only(day_text)):
        return None
    year = int(year_text)
    month = int(month_text)
    day = int(day_text)
    if len(year_text) < 4 or month < 1 or month > 12:
        return None
    if day < 1 or day > _days_in_month(year, month):
        return None
    return days_from_civil(year, month, day)


# A column's fraction of a second is written with one of these numbers
# of figures, the fewest that holds every value of the column exactly.
FRACTION_WIDTHS = (0, 3, 6, 9)


def clock_text(seconds: int, fraction: int, width: int) -> str:
    """`HH:MM:SS`, then `.` and ``width`` figures of ``fraction`` where width is not 0.

    ``seconds`` is the whole seconds into the day, from 0 to 86399, and
    ``fraction`` the part of a second in units of 10 ** -width.
    """
    hours = seconds // 3600
    minutes = (seconds // 60) % 60
    rest = seconds % 60
    text = f"{hours:02d}:{minutes:02d}:{rest:02d}"
    if width:
        text = f"{text}.{fraction:0{width}d}"
    return text


def clock_of_text(text: str) -> "tuple[int, int, int] | None":
    """(seconds into the day, the fraction's figures as a number, its width) of `HH:MM:SS[.f]`."""
    if not isinstance(text, str):
        raise TypeError("internal check: a clock time was not text")
    if len(text) < 8 or text[2] != ":" or text[5] != ":":
        return None
    hours_text = text[0:2]
    minutes_text = text[3:5]
    seconds_text = text[6:8]
    if not (_figures_only(hours_text) and _figures_only(minutes_text) and _figures_only(seconds_text)):
        return None
    hours = int(hours_text)
    minutes = int(minutes_text)
    seconds = int(seconds_text)
    if hours > 23 or minutes > 59 or seconds > 59:
        return None
    rest = text[8:]
    if not rest:
        return (hours * 3600 + minutes * 60 + seconds, 0, 0)
    if rest[0] != "." or len(rest) < 2:
        return None
    figures = rest[1:]
    if not _figures_only(figures) or len(figures) > 9:
        return None
    return (hours * 3600 + minutes * 60 + seconds, int(figures), len(figures))


def stamp_text(days: int, seconds: int, fraction: int, width: int) -> str:
    """`YYYY-MM-DD HH:MM:SS[.f]`: `date_text` and `clock_text` with one space between."""
    return date_text(days) + " " + clock_text(seconds, fraction, width)


def stamp_of_text(text: str) -> "tuple[int, int, int, int] | None":
    """(days, seconds into the day, fraction, width) of a `stamp_text`, else None.

    A trailing `+00:00` (a stamp written in universal time) is read and
    dropped; any other offset is not this module's rendering and reads
    as None.
    """
    if not isinstance(text, str):
        raise TypeError("internal check: a stamp was not text")
    if len(text) > 6 and text[len(text) - 6 :] == "+00:00":
        text = text[: len(text) - 6]
    cut = text.find(" ")
    if cut < 0:
        return None
    days = date_of_text(text[:cut])
    clock = clock_of_text(text[cut + 1 :])
    if days is None or clock is None:
        return None
    return (days, clock[0], clock[1], clock[2])


def split_units(value: int, per_second: int) -> "tuple[int, int, int]":
    """(days, seconds into the day, units into the second) of a count of 1/per_second units from day 0."""
    per_day = _SECONDS_A_DAY * per_second
    days = value // per_day
    rest = value - days * per_day
    return (days, rest // per_second, rest % per_second)


def fraction_width(units: "list[int]", per_second: int) -> "int | None":
    """The fewest `FRACTION_WIDTHS` figures every part of a second in ``units`` is written in exactly.

    ``units`` are parts of a second counted in 1/per_second, and
    ``per_second`` is a power of ten up to 10 ** 9. None where no width
    holds them (a finer unit than nine figures).
    """
    for width in FRACTION_WIDTHS:
        step = 1
        scale = 1
        for _ in range(width):
            scale = scale * 10
        if scale > per_second:
            return None
        step = per_second // scale
        if scale * step != per_second:
            return None
        if all(unit % step == 0 for unit in units):
            return width
    return None


def units_text(units: int, per_second: int, width: int) -> int:
    """``units`` (1/per_second of a second) as the number written in ``width`` figures."""
    scale = 1
    for _ in range(width):
        scale = scale * 10
    return units // (per_second // scale) if scale <= per_second else units * (scale // per_second)


def units_of_figures(figures: int, width: int, per_second: int) -> "int | None":
    """The 1/per_second units ``figures`` written in ``width`` figures stand for, or None where they are finer."""
    scale = 1
    for _ in range(width):
        scale = scale * 10
    if scale <= per_second:
        return figures * (per_second // scale)
    step = scale // per_second
    if figures % step:
        return None
    return figures // step


# -- 3. the bits of a number ------------------------------------------

_SIGN64 = 1 << 63
_MANTISSA64 = (1 << 52) - 1
_SIGN32 = 1 << 31


def _negative(value: float) -> bool:
    """Whether ``value`` carries the minus sign, -0.0 included."""
    if value < 0:
        return True
    if value > 0:
        return False
    return f"{value}"[0] == "-"


def double_bits(value: float) -> int:
    """The 64 bits of ``value`` as IEEE 754 binary64, an unsigned whole number.

    Exact: `math.frexp` splits a double into a mantissa and a power of
    two without rounding, and `math.ldexp` by a power of two is exact,
    so the mantissa's 53 bits are read as a whole number. A NaN is the
    one quiet NaN 0x7FF8000000000000, as every writer here writes it.
    """
    if value != value:
        return 0x7FF8000000000000
    sign = _SIGN64 if _negative(value) else 0
    if value == 0:
        return sign
    magnitude = -value if value < 0 else value
    if not math.isfinite(magnitude):
        return sign | 0x7FF0000000000000
    mantissa, exponent = math.frexp(magnitude)
    # magnitude = mantissa * 2 ** exponent, 0.5 <= mantissa < 1.
    biased = exponent + 1022
    if biased >= 1:
        whole = int(math.ldexp(mantissa, 53))
        return sign | (biased << 52) | (whole & _MANTISSA64)
    # A subnormal: the mantissa scaled to the smallest exponent.
    whole = int(math.ldexp(magnitude, 1074))
    return sign | whole


def double_of_bits(bits: int) -> float:
    """The binary64 value these 64 bits hold; exact (the inverse of `double_bits`)."""
    sign = -1.0 if bits & _SIGN64 else 1.0
    biased = (bits >> 52) & 0x7FF
    whole = bits & _MANTISSA64
    if biased == 0x7FF:
        if whole:
            return float("nan")
        return sign * float("inf")
    if biased == 0:
        return sign * math.ldexp(float(whole), -1074)
    return sign * math.ldexp(float(whole | (1 << 52)), biased - 1075)


def single_bits(value: float) -> "int | None":
    """The 32 bits of ``value`` as IEEE 754 binary32, or None where binary32 does not hold it exactly.

    A value the writer stores in four bytes is one read OUT of four bytes
    (the reader renders it with `single_text`, whose text `exact_single`
    reads back to this very double), so it is exact or it is not stored
    that way: no rounding is done here, and None tells the writer to
    store the column wider.
    """
    if value != value:
        return 0x7FC00000
    sign = _SIGN32 if _negative(value) else 0
    if value == 0:
        return sign
    magnitude = -value if value < 0 else value
    if not math.isfinite(magnitude):
        return sign | 0x7F800000
    mantissa, exponent = math.frexp(magnitude)
    biased = exponent + 126
    if biased >= 255:
        return None
    if biased >= 1:
        scaled = math.ldexp(mantissa, 24)
        whole = int(scaled)
        if whole != scaled:
            return None
        return sign | (biased << 23) | (whole & 0x7FFFFF)
    scaled = math.ldexp(magnitude, 149)
    whole = int(scaled)
    if whole != scaled or whole >= (1 << 23):
        return None
    return sign | whole


def single_of_bits(bits: int) -> float:
    """The binary32 value these 32 bits hold, as a double; exact."""
    sign = -1.0 if bits & _SIGN32 else 1.0
    biased = (bits >> 23) & 0xFF
    whole = bits & 0x7FFFFF
    if biased == 0xFF:
        if whole:
            return float("nan")
        return sign * float("inf")
    if biased == 0:
        return sign * math.ldexp(float(whole), -149)
    return sign * math.ldexp(float(whole | (1 << 23)), biased - 150)


def nearest_single(value: float) -> float:
    """``value`` rounded to the nearest binary32, ties to even, as a double.

    Used where a text must be read the way a four-byte store reads it:
    the double the text names, then binary32's nearest, which is how
    every reader of the four systems stores a decimal into four bytes.
    Exact arithmetic on the double's bits; overflow gives an infinity.
    """
    if value != value or value == 0 or not math.isfinite(value):
        return value
    negative = _negative(value)
    magnitude = -value if negative else value
    mantissa, exponent = math.frexp(magnitude)
    # Keep 24 significant bits (fewer for a subnormal binary32).
    keep = 24
    if exponent + 126 < 1:
        keep = 24 + (exponent + 126) - 1
    if keep < 0:
        return -0.0 if negative else 0.0
    scaled = math.ldexp(mantissa, 53)
    whole = int(scaled)
    drop = 53 - keep
    head = whole >> drop
    rest = whole - (head << drop)
    half = 1 << (drop - 1)
    if rest > half or (rest == half and head & 1):
        head = head + 1
    rounded = math.ldexp(float(head), exponent - keep)
    if rounded > 3.4028234663852886e38:
        rounded = float("inf")
    return -rounded if negative else rounded


def ibm_bits(value: float, width: int) -> "bytes | None":
    """``value`` as an IBM hexadecimal float of ``width`` bytes (2 to 8), big-endian, or None where it does not fit.

    The number form of a SAS transport file. IBM's mantissa is a
    fraction of 56 bits under a power of SIXTEEN, so a double's 53 bits
    always fit eight bytes after the shift to a hexadecimal exponent;
    fewer bytes keep fewer bits, and a value that would lose a bit is
    None, not rounded. A magnitude past 16 ** 63 is None as well.
    """
    if value == 0:
        return bytes(width)
    negative = _negative(value)
    magnitude = -value if negative else value
    mantissa, exponent = math.frexp(magnitude)
    whole = int(math.ldexp(mantissa, 53))
    # magnitude = whole * 2 ** (exponent - 53); write it as
    # fraction * 16 ** hex_exponent with 1/16 <= fraction < 1.
    power = exponent
    shift = (-power) % 4
    power = power + shift
    hex_exponent = power // 4
    # fraction = whole * 2 ** (exponent - 53 - 4 * hex_exponent), in 56 bits:
    bits = 56 + exponent - 53 - 4 * hex_exponent
    if bits >= 0:
        fraction = whole << bits
    else:
        fraction = whole >> (-bits)
        if (fraction << (-bits)) != whole:
            return None
    biased = hex_exponent + 64
    if biased < 0 or biased > 127:
        return None
    keep = 8 * (width - 1)
    if fraction & ((1 << (56 - keep)) - 1):
        return None
    fraction = fraction >> (56 - keep)
    head = biased | (0x80 if negative else 0)
    out = [head]
    for place in range(width - 2, -1, -1):
        out += [(fraction >> (8 * place)) & 0xFF]
    return bytes(out)


def ibm_value(data: bytes) -> float:
    """The value an IBM hexadecimal float of 2 to 8 bytes holds (the inverse of `ibm_bits` where it is exact)."""
    head = data[0]
    fraction = 0
    for byte in data[1:]:
        fraction = (fraction << 8) | byte
    if fraction == 0:
        return 0.0
    keep = 8 * (len(data) - 1)
    exponent = (head & 0x7F) - 64
    value = math.ldexp(float(fraction), 4 * exponent - keep)
    return -value if head & 0x80 else value


def little(value: int, width: int) -> bytes:
    """``value`` as ``width`` bytes, least significant first (two's complement for a negative number)."""
    if value < 0:
        value = value + (1 << (8 * width))
    return bytes([(value >> (8 * place)) & 0xFF for place in range(width)])


def big(value: int, width: int) -> bytes:
    """``value`` as ``width`` bytes, most significant first (two's complement for a negative number)."""
    if value < 0:
        value = value + (1 << (8 * width))
    return bytes([(value >> (8 * place)) & 0xFF for place in range(width - 1, -1, -1)])


def from_little(data: bytes, signed: bool = False) -> int:
    """The whole number ``data`` holds, least significant byte first."""
    value = 0
    for place in range(len(data) - 1, -1, -1):
        value = (value << 8) | data[place]
    if signed and data and data[len(data) - 1] & 0x80:
        value = value - (1 << (8 * len(data)))
    return value


# -- 2 (cont.): numbers as text ---------------------------------------

# A number a column cannot hold (Inf, NaN) is written with these words,
# which the package's own vocabulary of number spellings reads.
NAN_TEXT = "NaN"
INFINITY_TEXT = "inf"
NEGATIVE_INFINITY_TEXT = "-inf"


def whole_text(value: int) -> str:
    """A whole number's figures, a minus sign before a negative one."""
    return f"{value}"


def double_text(value: float) -> str:
    """How a double is written: its figures where it is whole, else Python's shortest round-trip text.

    THE RULE (one for every format): a whole value below 2 ** 53 in
    magnitude is written as its whole figures (`45`, not `45.0`), as a
    SAS, Stata, SPSS or R export of a numeric column writes it; -0.0 is
    `-0.0`, so its sign is kept; anything else is `repr`, the shortest
    text that reads back to the same double (`12.5`, `1e-05`,
    `1.7976931348623157e+308`); NaN and the infinities are `NaN`, `inf`
    and `-inf`. `exact_double` reads every one of them back to the very
    double it came from.
    """
    if value != value:
        return NAN_TEXT
    if not math.isfinite(value):
        return INFINITY_TEXT if value > 0 else NEGATIVE_INFINITY_TEXT
    if value == 0:
        return "-0.0" if _negative(value) else "0"
    if -9007199254740992.0 < value < 9007199254740992.0 and value == int(value):
        return f"{int(value)}"
    return f"{value!r}"


def exact_double(text: str) -> "float | None":
    """The double a `double_text` (or any decimal) names, or None where the text names none."""
    if not isinstance(text, str) or not text:
        return None
    if text == NAN_TEXT:
        return float("nan")
    if text == INFINITY_TEXT:
        return float("inf")
    if text == NEGATIVE_INFINITY_TEXT:
        return float("-inf")
    for character in text:
        if character not in "0123456789+-.eE":
            return None
    try:
        return float(text)
    except ValueError:
        return None


def number_spelled(text: str) -> bool:
    """Whether a text is spelled as `exact_double` reads a number, read off its characters alone, never as a number.

    A sign, figures with at most one point between or around them (one
    figure at least), and an exponent of `e` or `E`, a sign and figures;
    or `NAN_TEXT`, `INFINITY_TEXT`, `NEGATIVE_INFINITY_TEXT`. What the
    description's guard asks of a published code (batch 4zz's merge: a
    key of a published mapping is never handed to a binary64 reader,
    review item P3-V8-F5's guard). A fixed function of the text; raises
    nothing.
    """
    if not isinstance(text, str) or not text:
        return False
    if text in (NAN_TEXT, INFINITY_TEXT, NEGATIVE_INFINITY_TEXT):
        return True
    at = 0
    if text[at] in "+-":
        at = at + 1
    figures = 0
    points = 0
    while at < len(text) and (text[at] in "0123456789" or text[at] == "."):
        if text[at] == ".":
            points = points + 1
        else:
            figures = figures + 1
        at = at + 1
    if figures == 0 or points > 1:
        return False
    if at == len(text):
        return True
    if text[at] not in "eE":
        return False
    at = at + 1
    if at < len(text) and text[at] in "+-":
        at = at + 1
    if at == len(text):
        return False
    while at < len(text):
        if text[at] not in "0123456789":
            return False
        at = at + 1
    return True


def single_text(value: float) -> str:
    """How a value read out of four bytes is written: the shortest text binary32 reads back to it.

    A Stata `float` or a Parquet `float` column holds binary32 values;
    read as doubles they are long (`98.5999984741211`), and an export
    writes the short form (`98.6`). This writes the fewest significant
    figures whose binary32 nearest is the value (`nearest_single`, the
    reading `exact_single` does), whole values as their figures.
    """
    if value != value or not math.isfinite(value) or value == 0:
        return double_text(value)
    if -16777216.0 <= value <= 16777216.0 and value == int(value):
        return f"{int(value)}"
    for figures in range(1, 10):
        text = f"{value:.{figures}g}"
        candidate = float(text)
        if nearest_single(candidate) == value:
            shortest = f"{candidate!r}"
            if nearest_single(float(shortest)) == value:
                return shortest
            return text
    return f"{value!r}"


# The most decimal places a column of numbers is written with in fixed
# form; past them a column is written in `double_text`'s shortest form.
PLACES_MOST = 20


def places_needed(values: "list[float]", single: bool) -> "int | None":
    """The fewest decimal places, 0 to `PLACES_MOST`, that write every finite value of a column exactly.

    A NUMBER STORED IN BINARY HAS NO SPELLING, so its column is written
    in ONE fixed form: every value with the same number of decimal places
    (`fixed_text`), the fewest for which every value reads back to the
    very double (or binary32, ``single``) it is. A column of whole values
    is written with none (`45`), a column of tenths with one throughout
    (`125.0`, `130.4`), as a SAS, SPSS or Stata display format writes
    it. The twin's cells are written the same way, so a twin read back
    is spelled as it was drawn. None where no count up to `PLACES_MOST`
    holds every value (a column of very small or very precise numbers),
    which is then written in `double_text`'s shortest form, value by value.
    """
    for places in range(PLACES_MOST + 1):
        held = True
        for value in values:
            if value != value or not math.isfinite(value):
                continue
            back = exact_single(fixed_text(value, places)) if single else exact_double(fixed_text(value, places))
            if back is None or double_bits(back) != double_bits(value):
                held = False
                break
        if held:
            return places
    return None


def fixed_text(value: float, places: int) -> str:
    """``value`` with ``places`` decimal places (Python's correctly rounded fixed form); NaN and the infinities as words."""
    if value != value:
        return NAN_TEXT
    if not math.isfinite(value):
        return INFINITY_TEXT if value > 0 else NEGATIVE_INFINITY_TEXT
    return f"{value:.{places}f}"


def number_text(value: float, places: "int | None", single: bool) -> str:
    """A number of a column written at ``places`` (`fixed_text`), or its shortest form where ``places`` is None."""
    if places is None:
        return single_text(value) if single else double_text(value)
    return fixed_text(value, places)


def exact_single(text: str) -> "float | None":
    """The binary32 value a `single_text` names, as a double, or None where the text names no number."""
    found = exact_double(text)
    if found is None:
        return None
    return nearest_single(found)


# The special missing values of SAS (`.A` to `.Z` and `._`) and of
# Stata (`.a` to `.z`), written as the systems print them.
SAS_SPECIAL = tuple(["._"] + ["." + chr(code) for code in range(65, 91)])
STATA_EXTENDED = tuple(["." + chr(code) for code in range(97, 123)])


def special_missing_text(letter: str, stata: bool) -> "str | None":
    """The text of a special missing value pyreadstat reports as a letter (`A` or `a`), or None."""
    if not isinstance(letter, str) or len(letter) != 1:
        return None
    place = ord(letter)
    if stata:
        return STATA_EXTENDED[place - 97] if 97 <= place <= 122 else None
    if place == 95:
        return SAS_SPECIAL[0]
    if 97 <= place <= 122:
        place = place - 32
    return SAS_SPECIAL[place - 64] if 65 <= place <= 90 else None


# -- 4. Thrift's compact protocol --------------------------------------
#
# A Parquet file's footer (its own description of itself) and the header
# of every page are Thrift structures in the compact protocol. A
# structure is read into a dictionary from field number to value: a
# whole number, a truth value, bytes, a list, or a nested dictionary.

_CT_STOP = 0
_CT_TRUE = 1
_CT_FALSE = 2
_CT_BYTE = 3
_CT_I16 = 4
_CT_I32 = 5
_CT_I64 = 6
_CT_DOUBLE = 7
_CT_BINARY = 8
_CT_LIST = 9
_CT_SET = 10
_CT_MAP = 11
_CT_STRUCT = 12

# How deep a footer may nest structures: Parquet's own is five levels.
_THRIFT_DEPTH = 16


class ThriftError(ValueError):
    """The bytes are not a Thrift compact structure this reader reads."""


def _varint(data: bytes, at: int) -> "tuple[int, int]":
    value = 0
    shift = 0
    while True:
        if at >= len(data):
            raise ThriftError("a number runs past the end of the footer")
        byte = data[at]
        at = at + 1
        value = value | ((byte & 0x7F) << shift)
        if not byte & 0x80:
            return (value, at)
        shift = shift + 7
        if shift > 70:
            raise ThriftError("a number is longer than ten bytes")


def _zigzag(value: int) -> int:
    return (value >> 1) ^ -(value & 1)


def _thrift_value(data: bytes, at: int, kind: int, depth: int) -> "tuple[object, int]":
    if depth > _THRIFT_DEPTH:
        raise ThriftError("structures nest too deep")
    if kind == _CT_TRUE:
        return (True, at)
    if kind == _CT_FALSE:
        return (False, at)
    if kind == _CT_BYTE:
        if at >= len(data):
            raise ThriftError("a byte runs past the end of the footer")
        byte = data[at]
        return (byte - 256 if byte > 127 else byte, at + 1)
    if kind in (_CT_I16, _CT_I32, _CT_I64):
        raw, at = _varint(data, at)
        return (_zigzag(raw), at)
    if kind == _CT_DOUBLE:
        if at + 8 > len(data):
            raise ThriftError("a number runs past the end of the footer")
        return (double_of_bits(from_little(data[at : at + 8])), at + 8)
    if kind == _CT_BINARY:
        size, at = _varint(data, at)
        if at + size > len(data):
            raise ThriftError("a text runs past the end of the footer")
        return (data[at : at + size], at + size)
    if kind in (_CT_LIST, _CT_SET):
        if at >= len(data):
            raise ThriftError("a list runs past the end of the footer")
        head = data[at]
        at = at + 1
        size = head >> 4
        element = head & 0x0F
        if size == 15:
            size, at = _varint(data, at)
        items: "list[object]" = []
        for _ in range(size):
            if element in (_CT_TRUE, _CT_FALSE):
                if at >= len(data):
                    raise ThriftError("a list runs past the end of the footer")
                items += [data[at] == _CT_TRUE]
                at = at + 1
                continue
            item, at = _thrift_value(data, at, element, depth + 1)
            items += [item]
        return (items, at)
    if kind == _CT_MAP:
        size, at = _varint(data, at)
        if size:
            at = at + 1
        raise ThriftError("a map stands where Parquet's footer writes none")
    if kind == _CT_STRUCT:
        return _thrift_fields(data, at, depth + 1)
    raise ThriftError("a field of an unknown kind")


def _thrift_fields(data: bytes, at: int, depth: int) -> "tuple[dict[int, object], int]":
    fields: "dict[int, object]" = {}
    last = 0
    while True:
        if at >= len(data):
            raise ThriftError("a structure runs past the end of the footer")
        head = data[at]
        at = at + 1
        if head == _CT_STOP:
            return (fields, at)
        kind = head & 0x0F
        delta = head >> 4
        if delta:
            number = last + delta
        else:
            raw, at = _varint(data, at)
            number = _zigzag(raw)
        value, at = _thrift_value(data, at, kind, depth)
        fields[number] = value
        last = number


def thrift_struct(data: bytes, at: int = 0) -> "tuple[dict[int, object], int]":
    """One compact-protocol structure read from ``data`` at ``at``: (its fields, where it ended).

    Guarantees: a fixed function of the bytes. Raises ThriftError for
    bytes that end early, nest past sixteen levels, or hold a kind of
    field Parquet's footer never writes. No I/O.
    """
    if not isinstance(data, bytes):
        raise TypeError("internal check: a footer was not bytes")
    return _thrift_fields(data, at, 0)


def _put_varint(value: int) -> bytes:
    out: "list[int]" = []
    while True:
        byte = value & 0x7F
        value = value >> 7
        if value:
            out += [byte | 0x80]
        else:
            out += [byte]
            return bytes(out)


def varint_bytes(value: int) -> bytes:
    """A whole number of nought or more as the protocol's variable-length bytes (Parquet's levels use it too)."""
    return _put_varint(value)


def _put_zigzag(value: int) -> bytes:
    return _put_varint((value << 1) ^ (value >> 63) if value < 0 else value << 1)


@dataclasses.dataclass(frozen=True)
class T:
    """One field to write: its number, its compact kind and its value (a T list for a structure)."""

    number: int
    kind: int
    value: object


I32 = _CT_I32
I64 = _CT_I64
I16 = _CT_I16
BINARY = _CT_BINARY
LIST = _CT_LIST
STRUCT = _CT_STRUCT
BOOL = _CT_TRUE
BYTE = _CT_BYTE


@dataclasses.dataclass(frozen=True)
class TList:
    """A list to write: the kind of its elements and the elements."""

    kind: int
    items: "tuple[object, ...]"


def _put_value(kind: int, value: object) -> bytes:
    if kind in (_CT_I16, _CT_I32, _CT_I64):
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError("internal check: a Thrift whole number was not one")
        return _put_zigzag(value)
    if kind == _CT_BYTE:
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError("internal check: a Thrift byte was not one")
        return bytes([value & 0xFF])
    if kind == _CT_BINARY:
        if isinstance(value, str):
            value = bytes(value, "utf-8")
        if not isinstance(value, bytes):
            raise TypeError("internal check: a Thrift text was not one")
        return _put_varint(len(value)) + value
    if kind == _CT_STRUCT:
        if not isinstance(value, (list, tuple)):
            raise TypeError("internal check: a Thrift structure was not a list of fields")
        return thrift_bytes(tuple(value))
    if kind == _CT_LIST:
        if not isinstance(value, (TList,)):
            raise TypeError("internal check: a Thrift list was not one")
        size = len(value.items)
        element = value.kind
        if element == _CT_TRUE:
            element = _CT_TRUE
        head = bytes([(size << 4) | element]) if size < 15 else bytes([0xF0 | element]) + _put_varint(size)
        body = b""
        for item in value.items:
            if value.kind == _CT_TRUE:
                body = body + bytes([_CT_TRUE if item else _CT_FALSE])
                continue
            body = body + _put_value(value.kind, item)
        return head + body
    raise TypeError("internal check: a Thrift kind this writer does not write")


def thrift_bytes(fields: "tuple[T, ...]") -> bytes:
    """A compact-protocol structure holding ``fields``, in the order given (ascending numbers).

    Guarantees: the bytes `thrift_struct` reads back to the same fields;
    a truth value is written in its field's head, as the protocol does.
    Raises TypeError for a field whose value is not of its kind and
    ValueError for numbers that do not ascend. No I/O.
    """
    out = b""
    last = 0
    for field in fields:
        if field.number <= last:
            raise ValueError("internal check: Thrift fields are written in ascending order")
        kind = field.kind
        if kind == _CT_TRUE:
            kind = _CT_TRUE if field.value else _CT_FALSE
        delta = field.number - last
        if 0 < delta <= 15:
            out = out + bytes([(delta << 4) | kind])
        else:
            out = out + bytes([kind]) + _put_zigzag(field.number)
        if kind not in (_CT_TRUE, _CT_FALSE):
            out = out + _put_value(kind, field.value)
        last = field.number
    return out + bytes([_CT_STOP])


# -- 4 (cont.): a Parquet file's footer -------------------------------

# Parquet's physical types (parquet.thrift `Type`).
PHYSICAL_BOOLEAN = 0
PHYSICAL_INT32 = 1
PHYSICAL_INT64 = 2
PHYSICAL_INT96 = 3
PHYSICAL_FLOAT = 4
PHYSICAL_DOUBLE = 5
PHYSICAL_BYTE_ARRAY = 6
PHYSICAL_FIXED = 7

# Repetition (parquet.thrift `FieldRepetitionType`).
REQUIRED = 0
OPTIONAL = 1
REPEATED = 2

# The converted types the footer may name (parquet.thrift `ConvertedType`).
_CONVERTED_UTF8 = 0
_CONVERTED_DECIMAL = 5
_CONVERTED_DATE = 6
_CONVERTED_TIME_MILLIS = 7
_CONVERTED_TIME_MICROS = 8
_CONVERTED_TIMESTAMP_MILLIS = 9
_CONVERTED_TIMESTAMP_MICROS = 10
_CONVERTED_INTEGERS = {
    11: (8, False), 12: (16, False), 13: (32, False), 14: (64, False),
    15: (8, True), 16: (16, True), 17: (32, True), 18: (64, True),
}

# The column storages a Parquet column is read as (the native block's
# `storage` word). Every one is flat: a list, a map or a structure is
# refused by the reader.
STORE_BOOLEAN = "boolean"
STORE_INT8 = "int8"
STORE_INT16 = "int16"
STORE_INT32 = "int32"
STORE_INT64 = "int64"
STORE_UINT8 = "uint8"
STORE_UINT16 = "uint16"
STORE_UINT32 = "uint32"
STORE_UINT64 = "uint64"
STORE_FLOAT32 = "float32"
STORE_FLOAT64 = "float64"
STORE_STRING = "string"
STORE_DATE = "date"
STORE_TIMESTAMP_MS = "timestamp-ms"
STORE_TIMESTAMP_US = "timestamp-us"
STORE_TIMESTAMP_NS = "timestamp-ns"
STORE_TIME_MS = "time-ms"
STORE_TIME_US = "time-us"
STORE_TIME_NS = "time-ns"
STORE_DECIMAL = "decimal"
# The storages of SAS, Stata and SPSS files. Stata's five numeric types
# are its own words; SAS and SPSS store every number as a double.
STORE_NUMBER = "number"
STORE_TEXT = "text"
STORE_STATA_BYTE = "byte"
STORE_STATA_INT = "int"
STORE_STATA_LONG = "long"
STORE_STATA_FLOAT = "float"
STORE_STATA_DOUBLE = "double"
PARQUET_STORES = (
    STORE_BOOLEAN, STORE_DATE, STORE_DECIMAL, STORE_FLOAT32, STORE_FLOAT64,
    STORE_INT16, STORE_INT32, STORE_INT64, STORE_INT8, STORE_STRING,
    STORE_TIME_MS, STORE_TIME_NS, STORE_TIME_US, STORE_TIMESTAMP_MS,
    STORE_TIMESTAMP_NS, STORE_TIMESTAMP_US, STORE_UINT16, STORE_UINT32,
    STORE_UINT64, STORE_UINT8,
)
STAT_STORES = (
    STORE_NUMBER, STORE_STATA_BYTE, STORE_STATA_DOUBLE, STORE_STATA_FLOAT,
    STORE_STATA_INT, STORE_STATA_LONG, STORE_TEXT,
)
STORES = tuple(sorted(set(PARQUET_STORES + STAT_STORES)))

# How a column's cells are written as text (the native block's
# `written_as` word), each a rule of section 2.
WRITTEN_NUMBER = "number"
WRITTEN_SINGLE = "single"
WRITTEN_WHOLE = "whole"
WRITTEN_TEXT = "text"
WRITTEN_FLAG = "flag"
WRITTEN_DATE = "date"
WRITTEN_STAMP = "stamp"
WRITTEN_CLOCK = "clock"
WRITTEN_DECIMAL = "decimal"
WRITTEN = (
    WRITTEN_CLOCK, WRITTEN_DATE, WRITTEN_DECIMAL, WRITTEN_FLAG,
    WRITTEN_NUMBER, WRITTEN_SINGLE, WRITTEN_STAMP, WRITTEN_TEXT, WRITTEN_WHOLE,
)
FLAG_TRUE = "True"
FLAG_FALSE = "False"

# Units a second is cut into, by storage.
PER_SECOND = {
    STORE_TIMESTAMP_MS: 1000,
    STORE_TIMESTAMP_US: 1000000,
    STORE_TIMESTAMP_NS: 1000000000,
    STORE_TIME_MS: 1000,
    STORE_TIME_US: 1000000,
    STORE_TIME_NS: 1000000000,
}

# The widest whole number each integer storage holds, (least, most).
INTEGER_RANGES = {
    STORE_INT8: (-128, 127),
    STORE_INT16: (-32768, 32767),
    STORE_INT32: (-2147483648, 2147483647),
    STORE_INT64: (-9223372036854775808, 9223372036854775807),
    STORE_UINT8: (0, 255),
    STORE_UINT16: (0, 65535),
    STORE_UINT32: (0, 4294967295),
    STORE_UINT64: (0, 18446744073709551615),
    # Stata keeps the top of each range for its missing values.
    STORE_STATA_BYTE: (-127, 100),
    STORE_STATA_INT: (-32767, 32740),
    STORE_STATA_LONG: (-2147483647, 2147483620),
}


@dataclasses.dataclass(frozen=True)
class ParquetLeaf:
    """One column of a Parquet file, as its footer describes it."""

    name: str
    physical: int
    repetition: int
    store: str
    type_length: int
    precision: int
    scale: int
    utc: bool


@dataclasses.dataclass(frozen=True)
class ParquetFooter:
    """What a Parquet file's footer says, in the terms the reader needs."""

    rows: int
    leaves: "tuple[ParquetLeaf, ...]"
    # The key-value pairs, as text, in the footer's order.
    pairs: "tuple[tuple[str, str], ...]"
    # Why the file cannot be described ('' where it can): a nested
    # column, a column chunk kept in another file, an unknown type.
    refused: str = ""
    refused_column: str = ""


PARQUET_NESTED = "nested"
PARQUET_ELSEWHERE = "elsewhere"
PARQUET_UNKNOWN_TYPE = "unknown-type"
PARQUET_BROKEN = "broken"


def _logical_store(leaf: "dict[int, object]") -> "tuple[str, bool, int, int]":
    """(storage, utc, precision, scale) of a schema element's logical or converted type, '' where none."""
    physical = leaf[1] if 1 in leaf else -1
    logical = leaf[10] if 10 in leaf else None
    converted = leaf[6] if 6 in leaf else None
    precision = leaf[8] if 8 in leaf and isinstance(leaf[8], int) else 0
    scale = leaf[7] if 7 in leaf and isinstance(leaf[7], int) else 0
    if isinstance(logical, dict):
        if 1 in logical:
            return (STORE_STRING, False, 0, 0)
        if 5 in logical:
            inner = logical[5]
            if isinstance(inner, dict):
                scale = inner[1] if 1 in inner and isinstance(inner[1], int) else scale
                precision = inner[2] if 2 in inner and isinstance(inner[2], int) else precision
            return (STORE_DECIMAL, False, precision, scale)
        if 6 in logical:
            return (STORE_DATE, False, 0, 0)
        for slot, stores in (
            (7, (STORE_TIME_MS, STORE_TIME_US, STORE_TIME_NS)),
            (8, (STORE_TIMESTAMP_MS, STORE_TIMESTAMP_US, STORE_TIMESTAMP_NS)),
        ):
            if slot in logical:
                inner = logical[slot]
                if not isinstance(inner, dict):
                    return ("", False, 0, 0)
                utc = inner[1] is True if 1 in inner else False
                unit = inner[2] if 2 in inner else None
                if isinstance(unit, dict):
                    for number in (1, 2, 3):
                        if number in unit:
                            return (stores[number - 1], utc, 0, 0)
                return ("", False, 0, 0)
        if 10 in logical:
            inner = logical[10]
            if isinstance(inner, dict) and 1 in inner and 2 in inner:
                bits = inner[1]
                signed = inner[2] is True
                named = {
                    (8, True): STORE_INT8, (16, True): STORE_INT16,
                    (32, True): STORE_INT32, (64, True): STORE_INT64,
                    (8, False): STORE_UINT8, (16, False): STORE_UINT16,
                    (32, False): STORE_UINT32, (64, False): STORE_UINT64,
                }
                if isinstance(bits, int) and (bits, signed) in named:
                    return (named[(bits, signed)], False, 0, 0)
            return ("", False, 0, 0)
        return ("", False, 0, 0)
    if isinstance(converted, int):
        if converted == _CONVERTED_UTF8:
            return (STORE_STRING, False, 0, 0)
        if converted == _CONVERTED_DECIMAL:
            return (STORE_DECIMAL, False, precision, scale)
        if converted == _CONVERTED_DATE:
            return (STORE_DATE, False, 0, 0)
        if converted == _CONVERTED_TIME_MILLIS:
            return (STORE_TIME_MS, True, 0, 0)
        if converted == _CONVERTED_TIME_MICROS:
            return (STORE_TIME_US, True, 0, 0)
        if converted == _CONVERTED_TIMESTAMP_MILLIS:
            return (STORE_TIMESTAMP_MS, True, 0, 0)
        if converted == _CONVERTED_TIMESTAMP_MICROS:
            return (STORE_TIMESTAMP_US, True, 0, 0)
        if converted in _CONVERTED_INTEGERS:
            bits, signed = _CONVERTED_INTEGERS[converted]
            named = {
                (8, True): STORE_INT8, (16, True): STORE_INT16,
                (32, True): STORE_INT32, (64, True): STORE_INT64,
                (8, False): STORE_UINT8, (16, False): STORE_UINT16,
                (32, False): STORE_UINT32, (64, False): STORE_UINT64,
            }
            return (named[(bits, signed)], False, 0, 0)
        return ("", False, 0, 0)
    plain = {
        PHYSICAL_BOOLEAN: STORE_BOOLEAN,
        PHYSICAL_INT32: STORE_INT32,
        PHYSICAL_INT64: STORE_INT64,
        PHYSICAL_INT96: STORE_TIMESTAMP_NS,
        PHYSICAL_FLOAT: STORE_FLOAT32,
        PHYSICAL_DOUBLE: STORE_FLOAT64,
    }
    if isinstance(physical, int) and physical in plain:
        return (plain[physical], False, 0, 0)
    return ("", False, 0, 0)


def _text_of(value: object) -> str:
    if isinstance(value, bytes):
        return str(value, "utf-8", "replace")
    return ""


def parquet_footer(footer: bytes) -> ParquetFooter:
    """The facts of a Parquet footer (the Thrift `FileMetaData` alone, without its length and mark).

    Guarantees: a fixed function of the bytes. A file this cannot
    describe is returned with ``refused`` set rather than raised, so the
    reader can name the column in its own words: a column that is a
    list, a map or a structure (`PARQUET_NESTED`), a column chunk kept in
    another file (`PARQUET_ELSEWHERE`; nothing here would ever follow
    the path it names), a type this module has no storage for
    (`PARQUET_UNKNOWN_TYPE`), and bytes that are no footer
    (`PARQUET_BROKEN`). No I/O.
    """
    try:
        meta, _end = thrift_struct(footer)
    except ThriftError:
        return ParquetFooter(rows=0, leaves=(), pairs=(), refused=PARQUET_BROKEN)
    rows = meta[3] if 3 in meta and isinstance(meta[3], int) else -1
    schema = meta[2] if 2 in meta and isinstance(meta[2], list) else []
    if rows < 0 or not schema or not isinstance(schema[0], dict):
        return ParquetFooter(rows=0, leaves=(), pairs=(), refused=PARQUET_BROKEN)
    root = schema[0]
    children = root[5] if 5 in root and isinstance(root[5], int) else 0
    leaves: "list[ParquetLeaf]" = []
    for element in schema[1:]:
        if not isinstance(element, dict) or 4 not in element:
            return ParquetFooter(rows=0, leaves=(), pairs=(), refused=PARQUET_BROKEN)
        name = _text_of(element[4])
        if 5 in element and element[5]:
            return ParquetFooter(rows, (), (), PARQUET_NESTED, name)
        repetition = element[3] if 3 in element and isinstance(element[3], int) else OPTIONAL
        if repetition == REPEATED:
            return ParquetFooter(rows, (), (), PARQUET_NESTED, name)
        store, utc, precision, scale = _logical_store(element)
        physical = element[1] if 1 in element and isinstance(element[1], int) else -1
        if not store:
            return ParquetFooter(rows, (), (), PARQUET_UNKNOWN_TYPE, name)
        if physical == PHYSICAL_BYTE_ARRAY and store != STORE_STRING and store != STORE_DECIMAL:
            return ParquetFooter(rows, (), (), PARQUET_UNKNOWN_TYPE, name)
        leaves += [
            ParquetLeaf(
                name=name,
                physical=physical,
                repetition=repetition,
                store=store,
                type_length=element[2] if 2 in element and isinstance(element[2], int) else 0,
                precision=precision,
                scale=scale,
                utc=utc,
            )
        ]
    if children != len(leaves):
        return ParquetFooter(rows, (), (), PARQUET_NESTED, "")
    groups = meta[4] if 4 in meta and isinstance(meta[4], list) else []
    for group in groups:
        if not isinstance(group, dict):
            continue
        chunks = group[1] if 1 in group and isinstance(group[1], list) else []
        for chunk in chunks:
            if isinstance(chunk, dict) and 1 in chunk and chunk[1]:
                return ParquetFooter(rows, (), (), PARQUET_ELSEWHERE, "")
    pairs: "list[tuple[str, str]]" = []
    listed = meta[5] if 5 in meta and isinstance(meta[5], list) else []
    for pair in listed:
        if isinstance(pair, dict) and 1 in pair:
            pairs += [(_text_of(pair[1]), _text_of(pair[2]) if 2 in pair else "")]
    return ParquetFooter(rows=rows, leaves=tuple(leaves), pairs=tuple(pairs))


# -- 5. the description's native block ----------------------------------

# The fields of the block and of each column's entry, in the order the
# document writes them (the loader requires exactly these).
NATIVE_KEYS = ("columns", "format", "index", "table_name", "version")
COLUMN_KEYS = (
    "categories",
    "display",
    "fraction",
    "label",
    "label_set",
    "measure",
    "missing",
    "pandas",
    "places",
    "precision",
    "required",
    "scale",
    "storage",
    "utc",
    "value_labels",
    "width",
    "written_as",
    "zone",
)
# ...and the one key an entry carries only where it says something (lane
# TOOLS): the cell standing for an empty text (`NativeColumn.empty_text`).
OPTIONAL_COLUMN_KEY = "empty_text"
MISSING_KEYS = ("high", "low", "values")
PANDAS_KEYS = ("numpy_type", "ordered", "pandas_type")
INDEX_KEYS = ("columns", "start", "step")

# SPSS's three measures.
MEASURES = ("nominal", "ordinal", "scale")

# pandas' own words for a column's type, which its metadata block names
# (pyarrow's `pandas_compat`); the twin's block names nothing else.
PANDAS_TYPES = (
    "bool", "bytes", "categorical", "date", "datetime", "datetimetz",
    "decimal", "empty", "float16", "float32", "float64", "int16", "int32",
    "int64", "int8", "mixed", "object", "string", "time", "uint16",
    "uint32", "uint64", "uint8", "unicode",
)
NUMPY_TYPES = (
    "Float32", "Float64", "Int16", "Int32", "Int64", "Int8", "UInt16",
    "UInt32", "UInt64", "UInt8", "bool", "boolean", "category",
    "datetime64[ms]", "datetime64[ns]", "datetime64[s]", "datetime64[us]",
    "float16", "float32", "float64", "int16", "int32", "int64", "int8",
    "object", "str", "string", "timedelta64[ns]", "uint16", "uint32",
    "uint64", "uint8",
)

# The cap on a published label's length, in characters.
LABEL_MOST = 256
# A run of this many figures in a label is a number somebody typed.
LABEL_FIGURES_MOST = 4


def column_label_published(text: object) -> bool:
    """Whether a COLUMN's label may be published as written.

    A column's label is the analyst's own words about a column, the same
    kind of text as the column's name, which the CSV route publishes as
    the file writes it; so it is held to the identifier rules alone: 1
    to `LABEL_MOST` characters, none of them a control character, no run
    of more than `LABEL_FIGURES_MOST` figures (an identifier, a telephone
    number, a date of birth written as digits), no at sign and no web
    address -- AND, since batch 4zz's fix round (the outside review's item
    1: `2024-03-05`, `312-555-0199` and `10.1.2.3` reached a Stata twin's
    bytes), none of the identifier forms the twin checks read in a cell
    (`_an_identifier_form`: a telephone number, a title before a name, a
    social security number, a network address, a device's or a serial
    number) and no date finer than a year (`date_counts.date_in_disguise`).
    A bare person's name is not read here (the persons'-name reading
    withholds `Systolic BP` and `Heart Rate`), as a column's name is not.
    Everything else is withheld: the twin's column then carries no label.
    Guarantees: a fixed function of the text; raises nothing.
    """
    if not isinstance(text, str):
        return False
    return _label_text_published(text) and not _an_identifier_form(text)


def label_published(text: object) -> bool:
    """Whether a VALUE label (the words a code stands for) may be published as written.

    A value label is a cell of the CSV the same file exports with its
    labels applied, so beside `column_label_published`'s rules it is held
    to the readings the twin checks apply to a published cell
    (`twin_checks`, C4): no text the package reads as an identifier's
    words, a social security number, a network address, a device's or a
    serial number, and no text read as a person's name whose words are
    none of a role, a service, a source or a flag of the product's closed
    lists (`taxonomy.a_persons_name` with `an_ordinary_family_name`):
    `Maria Garcia` is withheld, `Intensive Care` and `Home Health` are
    published; and, since batch 4zz's fix round, no date finer than a year
    (the outside review's item 1). Guarantees: a fixed function of the
    text; raises nothing.
    """
    if not isinstance(text, str):
        return False
    return _label_text_published(text) and not _an_identifier_or_a_name(text)


def _label_text_published(text: str) -> bool:
    """`label_published` of a text."""
    if not isinstance(text, str):
        raise TypeError("internal check: a label was not text")
    if not text or len(text) > LABEL_MOST:
        return False
    run = 0
    for character in text:
        place = ord(character)
        if place < 32 or place == 127 or 128 <= place < 160:
            return False
        if 48 <= place <= 57:
            run = run + 1
            if run > LABEL_FIGURES_MOST:
                return False
        else:
            run = 0
        if character == "@":
            return False
    lowered = text.casefold()
    if lowered.find("://") >= 0 or lowered.find("www.") >= 0:
        return False
    return True


def _an_identifier_form(text: str) -> bool:
    """The twin checks' reading of a published cell as an identifier (C4), and a date finer than a year.

    `taxonomy` is imported here: it imports the loader, which imports
    this module.
    """
    from synthtwin import taxonomy

    return bool(
        taxonomy.identifier_words_form(text, False)
        or taxonomy.social_security_form(text)
        or taxonomy.a_network_address(text)
        or taxonomy.a_device_identifier(text)
        or taxonomy.a_serial_number(text)
        or _a_date_in(text)
    )


def _a_date_in(text: str) -> bool:
    """Whether a date stands anywhere in a label (`date_counts.date_in_disguise`): read whole, then from each word's
    start (a date heading the rest)."""
    from synthtwin import date_counts

    if date_counts.date_in_disguise(text):
        return True
    for place in range(1, len(text)):
        if text[place - 1] == " " and text[place] != " " and date_counts.date_in_disguise(text[place:]):
            return True
    return False


def _an_identifier_or_a_name(text: str) -> bool:
    """`_an_identifier_form`, or the twin checks' reading of a published cell as a person's name (C4)."""
    from synthtwin import taxonomy

    return _an_identifier_form(text) or bool(taxonomy.a_persons_name(text) and taxonomy.an_ordinary_family_name(text))


def _a_persons_name(text: str) -> bool:
    """`taxonomy.a_persons_name`, imported here for the reason `_an_identifier_or_a_name` says."""
    from synthtwin import taxonomy

    return taxonomy.a_persons_name(text) and taxonomy.an_ordinary_family_name(text)


def name_published(text: object, most: int) -> bool:
    """Whether a member name, a label set's name or a time zone's name may be published.

    Admitted: 1 to ``most`` characters, each an ASCII letter, a figure,
    an underscore, or (for a zone's name) one of `/+-`, beginning with a
    letter or an underscore, holding no run of three figures or more,
    that `taxonomy.a_persons_name` does not read as a person's name.
    """
    if not isinstance(text, str):
        return False
    return _name_text_published(text, most)


def _name_text_published(text: str, most: int) -> bool:
    """`name_published` of a text."""
    if not isinstance(text, str):
        raise TypeError("internal check: a name was not text")
    if not text or len(text) > most:
        return False
    first = text[0]
    if not (_letter(first) or first == "_"):
        return False
    run = 0
    for character in text:
        place = ord(character)
        if 48 <= place <= 57:
            run = run + 1
            if run > 2:
                return False
            continue
        run = 0
        if not (_letter(character) or character in "_/+-"):
            return False
    return not _a_persons_name(text.replace("_", " ").replace("/", " "))


# The areas the time zone database names its zones under; a zone's name
# is one of them, a slash, and a place, or one of the plain names below.
_ZONE_AREAS = (
    "Africa", "America", "Antarctica", "Arctic", "Asia", "Atlantic",
    "Australia", "Brazil", "Canada", "Chile", "Etc", "Europe", "Indian",
    "Mexico", "Pacific", "US",
)
_ZONE_PLAIN = ("GMT", "UTC", "Z", "Zulu", "Universal")


def zone_published(text: object) -> bool:
    """Whether a time zone's name may be published: the time zone database's shape, or a plain offset.

    A zone covers millions of people and is named after a large city by
    the database's own convention (`America/Chicago`), so it is held to
    that shape and not to the reading of persons' names a cell meets:
    `UTC`, an offset `+05:30`, or an area of `_ZONE_AREAS`, then one or
    two places of ASCII letters, underscores and hyphens, at most 64
    characters in all.
    """
    if not isinstance(text, str):
        return False
    return _zone_text_published(text)


# The longest run of spaces that stands for an empty text.
EMPTY_TEXT_MOST = 64


def empty_text_published(text: object) -> bool:
    """Whether a cell standing for an empty text may be published: "" or a run of spaces, at most `EMPTY_TEXT_MOST`.

    Spaces alone carry no value of the table: the run is chosen as the
    shortest one no cell of the column holds (`empty_text_for`).
    """
    return isinstance(text, str) and len(text) <= EMPTY_TEXT_MOST and all(character == " " for character in text)


def empty_text_for(values: "list[object]") -> "str | None":
    """The cell that stands for an empty text in a Parquet text column of these values (`NativeColumn.empty_text`).

    None where no value is an empty text; "" where none is missing (None),
    so every blank cell is an empty text; else the shortest run of spaces
    that no value of the column is, so the two kinds of nothing stay
    apart. None, too, where every run up to `EMPTY_TEXT_MOST` is taken: the
    empty texts are then read as missing, as before. A fixed function of
    the values; raises nothing.
    """
    seen_empty = False
    seen_missing = False
    spaces: "set[int]" = set()
    for value in values:
        if value is None:
            seen_missing = True
        elif value == "":
            seen_empty = True
        elif isinstance(value, str) and len(value) <= EMPTY_TEXT_MOST and all(character == " " for character in value):
            spaces = spaces | {len(value)}
    if not seen_empty:
        return None
    if not seen_missing:
        return ""
    for length in range(1, EMPTY_TEXT_MOST + 1):
        if length not in spaces:
            return " " * length
    return None


def _empty_text_or_refused(value: object, where: str) -> str:
    if not empty_text_published(value):
        raise NativeFormError(f"{where} names a cell for an empty text that is not a run of spaces")
    return f"{value}"


def _zone_text_published(text: str) -> bool:
    if not isinstance(text, str):
        raise TypeError("internal check: a zone's name was not text")
    if not text or len(text) > 64:
        return False
    if text in _ZONE_PLAIN:
        return True
    if len(text) == 6 and text[0] in "+-" and text[3] == ":":
        return _figures_only(text[1:3]) and _figures_only(text[4:6])
    parts = text.split("/")
    if len(parts) < 2 or len(parts) > 3 or parts[0] not in _ZONE_AREAS:
        return False
    for part in parts[1:]:
        if not part:
            return False
        for character in part:
            if not (_letter(character) or character in "_-"):
                return False
    return True


# The words of each system's display formats that may be published: the
# format languages' own, never a user-defined SAS format's name (which a
# person chose and SAS keeps in a catalogue this package does not read).
_SAS_FORMATS = (
    "BEST", "COMMA", "COMMAX", "DATE", "DATEAMPM", "DATETIME", "DDMMYY",
    "DDMMYYB", "DDMMYYC", "DDMMYYD", "DDMMYYN", "DDMMYYP", "DDMMYYS",
    "DOLLAR", "DOLLARX", "DTDATE", "E", "E8601DA", "E8601DN", "E8601DT",
    "E8601TM", "F", "FRACT", "HHMM", "HOUR", "IS8601DA", "IS8601DN",
    "IS8601DT", "IS8601TM", "JULDAY", "JULIAN", "MMDDYY", "MMDDYYB",
    "MMDDYYC", "MMDDYYD", "MMDDYYN", "MMDDYYP", "MMDDYYS", "MMSS",
    "MMYY", "MONNAME", "MONTH", "MONYY", "NLDATE", "NUMX", "PERCENT",
    "PERCENTN", "QTR", "TIME", "TIMEAMPM", "TOD", "WEEKDATE", "WEEKDAY",
    "WORDDATE", "WORDDATX", "YEAR", "YYMM", "YYMMDD", "YYMMDDB",
    "YYMMDDC", "YYMMDDD", "YYMMDDN", "YYMMDDP", "YYMMDDS", "YYMON",
    "YYQ", "Z", "$", "$CHAR", "$ASCII", "$UPCASE", "$QUOTE",
)
_SPSS_FORMATS = (
    "A", "ADATE", "AHEX", "CCA", "CCB", "CCC", "CCD", "CCE", "COMMA",
    "DATE", "DATETIME", "DOLLAR", "DOT", "DTIME", "E", "EDATE", "F", "IB",
    "JDATE", "MONTH", "MOYR", "MTIME", "N", "P", "PCT", "PIB", "PIBHEX",
    "PK", "QYR", "RB", "RBHEX", "SDATE", "TIME", "WKDAY", "WKYR",
    "YMDHMS", "Z",
)


def _format_word(code: str) -> "tuple[str, str] | None":
    """(the format's name, its width and decimals) of a SAS or SPSS format code."""
    if not isinstance(code, str):
        raise TypeError("internal check: a format code was not text")
    cut = len(code)
    while cut > 0 and (48 <= ord(code[cut - 1]) <= 57 or code[cut - 1] == "."):
        cut = cut - 1
    name = code[:cut]
    rest = code[cut:]
    if rest.count(".") > 1:
        return None
    return (name, rest)


def format_published(code: object, source_format: str) -> bool:
    """Whether a column's display format may be published (and so worn by the twin).

    Stata: the format language's grammar (`%` then an optional `-` or
    `0`, figures and `.`, then one of `g f e s td tc tC tw tm tq th ty`
    or a `%t` date format's own letters, and a comma for figures in
    groups), at most 48 characters. SAS and SPSS: one of the languages'
    own format names, upper case, with its width and decimals in figures.
    Everything else -- above all a user-defined SAS format, whose name a
    person chose -- is withheld, and the twin wears the plain format of
    its storage. Guarantees: a fixed function of the two texts.
    """
    if not isinstance(code, str):
        return False
    return _format_text_published(code, source_format)


def _format_text_published(code: str, source_format: str) -> bool:
    """`format_published` of a text."""
    if not isinstance(code, str):
        raise TypeError("internal check: a format code was not text")
    if not code or len(code) > 48:
        return False
    if source_format == FORMAT_STATA:
        if code[0] != "%":
            return False
        for character in code[1:]:
            place = ord(character)
            if not (_letter(character) or 48 <= place <= 57 or character in "-.,:_/ "):
                return False
        tail = code[1:].lstrip("-0123456789.,")
        if tail[:1] in ("g", "f", "e", "s"):
            return len(tail) <= 2
        if tail[:2] == "-t" or tail[:1] == "t":
            return True
        return False
    if source_format not in (FORMAT_SPSS, FORMAT_SAS_DATASET, FORMAT_SAS_TRANSPORT):
        return False
    words = _SPSS_FORMATS if source_format == FORMAT_SPSS else _SAS_FORMATS
    split = _format_word(code)
    if split is None:
        return False
    name, _rest = split
    return name in words or name == ""


@dataclasses.dataclass(frozen=True)
class NativeMissing:
    """SPSS's missing values of one column: up to three codes, or a range and one code."""

    values: "tuple[str, ...]"
    low: "str | None"
    high: "str | None"


@dataclasses.dataclass(frozen=True)
class PandasColumn:
    """The fields of pandas' metadata block one column may carry."""

    pandas_type: str
    numpy_type: str
    ordered: "bool | None"


@dataclasses.dataclass(frozen=True)
class NativeColumn:
    """How one column is stored in the native file (one entry of `source.native.columns`)."""

    storage: str
    written_as: str
    width: "int | None" = None
    precision: "int | None" = None
    scale: "int | None" = None
    fraction: int = 0
    utc: "bool | None" = None
    zone: "str | None" = None
    required: bool = False
    display: "str | None" = None
    label: "str | None" = None
    label_set: "str | None" = None
    value_labels: "tuple[tuple[str, str], ...] | None" = None
    missing: "NativeMissing | None" = None
    measure: "str | None" = None
    pandas: "PandasColumn | None" = None
    # The decimal places every number of the column is written with
    # (`places_needed`), or None where it is written in its shortest form
    # or holds no numbers.
    places: "int | None" = None
    # A categorical column's categories in the order its file keeps them
    # (pandas' order), each one a value the description publishes; None
    # for every other column.
    categories: "tuple[str, ...] | None" = None
    # THE CELL THAT STANDS FOR AN EMPTY TEXT (lane TOOLS; the outside
    # review of batch 4zz, item 10). A Parquet text column holds two kinds
    # of nothing, a missing value and an empty text, and a cell holds one
    # spelling for both: "" for the missing value. Where the column holds
    # empty texts, this is the cell that stands for one -- "" itself where
    # it holds no missing value, else the shortest run of spaces no cell of
    # the column holds (`empty_text_for`) -- so the description counts the
    # two apart and the twin's writer writes each back as its own kind.
    # None where the column holds no empty text, and for every column of
    # every other system (an empty text IS Stata's and SPSS's missing text).
    empty_text: "str | None" = None


@dataclasses.dataclass(frozen=True)
class NativeIndex:
    """pandas' index, as the Parquet file's pandas block named it."""

    columns: "tuple[str, ...]"
    start: "int | None"
    step: "int | None"


@dataclasses.dataclass(frozen=True)
class NativeForm:
    """What a native file said about itself that the description publishes (contract 4.3c)."""

    system: str
    version: int
    columns: "tuple[NativeColumn, ...]"
    table_name: "str | None" = None
    index: "NativeIndex | None" = None


# The versions each format's twin may be written in.
VERSIONS = {
    FORMAT_PARQUET: (1, 2),
    FORMAT_STATA: (113, 114, 115, 117, 118, 119),
    FORMAT_SPSS: (2, 3),
    FORMAT_SAS_TRANSPORT: (5, 8),
    FORMAT_SAS_DATASET: (0,),
}


class NativeFormError(ValueError):
    """A native block that breaks one of the rules this module states; the words say which."""


def document_of(form: NativeForm) -> "dict[str, object]":
    """The native block as the description writes it (keys in `NATIVE_KEYS` order).

    Guarantees: `form_of` reads the result back to an equal NativeForm.
    """
    columns: "list[dict[str, object]]" = []
    for column in form.columns:
        missing: "dict[str, object] | None" = None
        if column.missing is not None:
            missing = {
                "high": column.missing.high,
                "low": column.missing.low,
                "values": list(column.missing.values),
            }
        pandas: "dict[str, object] | None" = None
        if column.pandas is not None:
            pandas = {
                "numpy_type": column.pandas.numpy_type,
                "ordered": column.pandas.ordered,
                "pandas_type": column.pandas.pandas_type,
            }
        labels: "dict[str, str] | None" = None
        if column.value_labels is not None:
            labels = {}
            for code, text in column.value_labels:
                labels[code] = text
        columns += [
            {
                "categories": list(column.categories) if column.categories is not None else None,
                "display": column.display,
                "fraction": column.fraction,
                "label": column.label,
                "label_set": column.label_set,
                "measure": column.measure,
                "missing": missing,
                "pandas": pandas,
                "places": column.places,
                "precision": column.precision,
                "required": column.required,
                "scale": column.scale,
                "storage": column.storage,
                "utc": column.utc,
                "value_labels": labels,
                "width": column.width,
                "written_as": column.written_as,
                "zone": column.zone,
            }
        ]
        # Written only where it says something (lane TOOLS), so every
        # description without an empty text keeps its keys and bytes.
        if column.empty_text is not None:
            columns[len(columns) - 1]["empty_text"] = column.empty_text
    index: "dict[str, object] | None" = None
    if form.index is not None:
        index = {
            "columns": list(form.index.columns),
            "start": form.index.start,
            "step": form.index.step,
        }
    return {
        "columns": columns,
        "format": form.system,
        "index": index,
        "table_name": form.table_name,
        "version": form.version,
    }


def _exact_keys(mapping: object, keys: "tuple[str, ...]", where: str) -> "dict[str, object]":
    if not isinstance(mapping, dict):
        raise NativeFormError(f"{where} is not a block of named fields")
    for key in sorted([f"{name}" for name in mapping]):
        if key not in keys:
            raise NativeFormError(f"{where} carries a field this version does not know, '{key}'")
    for key in keys:
        if key not in mapping:
            raise NativeFormError(f"{where} lacks its field '{key}'")
    return mapping


def _whole_or_none(value: object, where: str, least: int, most: int) -> "int | None":
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < least or value > most:
        raise NativeFormError(f"{where} is not a whole number from {least} to {most}")
    return value


def _flag_or_none(value: object, where: str) -> "bool | None":
    if value is None:
        return None
    if not isinstance(value, bool):
        raise NativeFormError(f"{where} is not true or false")
    return value


def _number_code(value: object, where: str) -> str:
    if not isinstance(value, str) or exact_double(value) is None or value in (
        NAN_TEXT, INFINITY_TEXT, NEGATIVE_INFINITY_TEXT,
    ):
        raise NativeFormError(f"{where} is not a number written as text")
    return value


def form_of(value: object, width: int) -> "NativeForm | None":
    """The native block, typed, or None where the description has none.

    ``width`` is the description's column count; the block must describe
    exactly that many columns. Every published text is held to the rule
    that admitted it -- a label to `label_published`, a format to
    `format_published`, a name to `name_published`, a word to its list --
    so a hand-made description can put nothing into a twin that this
    package would not have published itself. Raises NativeFormError,
    naming the field, for anything else. No I/O.
    """
    if value is None:
        return None
    block = _exact_keys(value, NATIVE_KEYS, "the native file's block")
    fmt = block["format"]
    if fmt not in FORMATS:
        raise NativeFormError("the native file's block names a format this version does not write")
    version = block["version"]
    if isinstance(version, bool) or not isinstance(version, int) or version not in VERSIONS[f"{fmt}"]:
        raise NativeFormError("the native file's block names a version of its format this version does not write")
    name = block["table_name"]
    if name is not None and not name_published(name, 32):
        raise NativeFormError("the native file's block names its table with a name this version would not publish")
    raw_columns = block["columns"]
    if not isinstance(raw_columns, list) or (width >= 0 and len(raw_columns) != width):
        raise NativeFormError("the native file's block does not describe every column exactly once")
    stores = PARQUET_STORES if fmt == FORMAT_PARQUET else STAT_STORES
    columns: "list[NativeColumn]" = []
    for place in range(len(raw_columns)):
        where = f"column {place + 1} of the native file's block"
        raw_entry = raw_columns[place]
        empty_text: "str | None" = None
        if isinstance(raw_entry, dict) and OPTIONAL_COLUMN_KEY in raw_entry:
            empty_text = _empty_text_or_refused(raw_entry[OPTIONAL_COLUMN_KEY], where)
            raw_entry = {key: raw_entry[key] for key in sorted(raw_entry) if key != OPTIONAL_COLUMN_KEY}
        entry = _exact_keys(raw_entry, COLUMN_KEYS, where)
        storage = entry["storage"]
        if storage not in stores:
            raise NativeFormError(f"{where} names a storage its format has no word for")
        written = entry["written_as"]
        if written not in WRITTEN:
            raise NativeFormError(f"{where} names a way of writing its cells this version does not know")
        display = entry["display"]
        if display is not None and not format_published(display, f"{fmt}"):
            raise NativeFormError(f"{where} wears a display format this version would not publish")
        label = entry["label"]
        if label is not None and not column_label_published(label):
            raise NativeFormError(f"{where} carries a label this version would not publish")
        label_set = entry["label_set"]
        if label_set is not None and not name_published(label_set, 32):
            raise NativeFormError(f"{where} names its value labels with a name this version would not publish")
        labels_raw = entry["value_labels"]
        labels: "tuple[tuple[str, str], ...] | None" = None
        if labels_raw is not None:
            if not isinstance(labels_raw, dict):
                raise NativeFormError(f"{where} carries value labels that are not a block of codes")
            pairs: "list[tuple[str, str]]" = []
            for _order, code in sorted([(_code_order(f"{key}"), f"{key}") for key in labels_raw]):
                text = labels_raw[code]
                if storage != STORE_TEXT:
                    _number_code(code, f"{where}'s value label code")
                if not label_published(text):
                    raise NativeFormError(f"{where} carries a value label this version would not publish")
                pairs += [(code, f"{text}")]
            labels = tuple(pairs)
        missing_raw = entry["missing"]
        missing: "NativeMissing | None" = None
        if missing_raw is not None:
            miss = _exact_keys(missing_raw, MISSING_KEYS, f"{where}'s missing values")
            values_raw = miss["values"]
            if not isinstance(values_raw, list) or len(values_raw) > 3:
                raise NativeFormError(f"{where} lists more missing values than SPSS keeps")
            codes: "list[str]" = []
            for item in values_raw:
                if storage == STORE_TEXT:
                    if not isinstance(item, str) or not label_published(item) or len(bytes(item, "utf-8")) > 8:
                        raise NativeFormError(f"{where} lists a missing value this version would not publish")
                    codes += [item]
                else:
                    codes += [_number_code(item, f"{where}'s missing value")]
            low = miss["low"]
            high = miss["high"]
            if (low is None) != (high is None):
                raise NativeFormError(f"{where} gives one end of a missing range without the other")
            if low is not None:
                _number_code(low, f"{where}'s missing range")
                _number_code(high, f"{where}'s missing range")
                if len(codes) > 1:
                    raise NativeFormError(f"{where} lists more missing values beside a range than SPSS keeps")
            missing = NativeMissing(values=tuple(codes), low=low if isinstance(low, str) else None,
                                    high=high if isinstance(high, str) else None)
        measure = entry["measure"]
        if measure is not None and measure not in MEASURES:
            raise NativeFormError(f"{where} names a measure SPSS does not know")
        pandas_raw = entry["pandas"]
        pandas: "PandasColumn | None" = None
        if pandas_raw is not None:
            panda = _exact_keys(pandas_raw, PANDAS_KEYS, f"{where}'s pandas fields")
            if panda["pandas_type"] not in PANDAS_TYPES or panda["numpy_type"] not in NUMPY_TYPES:
                raise NativeFormError(f"{where}'s pandas fields name a type pandas does not write")
            pandas = PandasColumn(
                pandas_type=f"{panda['pandas_type']}",
                numpy_type=f"{panda['numpy_type']}",
                ordered=_flag_or_none(panda["ordered"], f"{where}'s pandas order"),
            )
        zone = entry["zone"]
        if zone is not None and not zone_published(zone):
            raise NativeFormError(f"{where} names a time zone this version would not publish")
        fraction = entry["fraction"]
        if fraction not in FRACTION_WIDTHS:
            raise NativeFormError(f"{where} writes its fractions of a second in a width this version does not")
        required = entry["required"]
        if not isinstance(required, bool):
            raise NativeFormError(f"{where} does not say whether every cell holds a value")
        listed_raw = entry["categories"]
        categories: "tuple[str, ...] | None" = None
        if listed_raw is not None:
            if not isinstance(listed_raw, list):
                raise NativeFormError(f"{where} lists its categories as something that is not a list")
            listed: "list[str]" = []
            for item in listed_raw:
                if not isinstance(item, str) or not label_published(item) or item in listed:
                    raise NativeFormError(f"{where} lists a category this version would not publish")
                listed += [item]
            categories = tuple(listed)
        columns += [
            NativeColumn(
                storage=f"{storage}",
                written_as=f"{written}",
                width=_whole_or_none(entry["width"], f"{where}'s width", 0, 2147483647),
                precision=_whole_or_none(entry["precision"], f"{where}'s precision", 1, 76),
                scale=_whole_or_none(entry["scale"], f"{where}'s scale", 0, 76),
                fraction=int(f"{fraction}"),
                utc=_flag_or_none(entry["utc"], f"{where}'s universal time"),
                zone=zone if isinstance(zone, str) else None,
                required=required,
                display=display if isinstance(display, str) else None,
                label=label if isinstance(label, str) else None,
                label_set=label_set if isinstance(label_set, str) else None,
                value_labels=labels,
                missing=missing,
                measure=measure if isinstance(measure, str) else None,
                pandas=pandas,
                places=_whole_or_none(entry["places"], f"{where}'s decimal places", 0, PLACES_MOST),
                categories=categories,
                empty_text=empty_text,
            )
        ]
    index_raw = block["index"]
    index: "NativeIndex | None" = None
    if index_raw is not None:
        entry = _exact_keys(index_raw, INDEX_KEYS, "the native file's index")
        index_columns = entry["columns"]
        if not isinstance(index_columns, list):
            raise NativeFormError("the native file's index does not list its columns")
        index = NativeIndex(
            columns=tuple([f"{item}" for item in index_columns]),
            start=_whole_or_none(entry["start"], "the index's start", 0, 1),
            step=_whole_or_none(entry["step"], "the index's step", 1, 1),
        )
    return NativeForm(
        system=f"{fmt}",
        version=version,
        columns=tuple(columns),
        table_name=name if isinstance(name, str) else None,
        index=index,
    )


def _code_order(code: str) -> "tuple[int, float, str]":
    """Value labels in the order of their codes: numbers by value, then texts."""
    found = exact_double(code)
    if found is None or found != found:
        return (1, 0.0, code)
    return (0, found, code)


# -- pandas' metadata block of a Parquet file ---------------------------

PANDAS_KEY = "pandas"


def pandas_fields(text: str) -> "tuple[dict[str, PandasColumn], NativeIndex | None, dict[str, str]]":
    """What pandas' metadata block says, by column name: the types, the index, the time zones.

    Only the fields this module names are read; everything else in the
    block (its creator, versions, attributes, the index's name and
    anything a writer added) is left where it is and never published.
    A block that is not pandas' JSON gives nothing. A RangeIndex is kept
    only where it starts at 0 or 1 and steps by 1: its end is the row
    count, which the description publishes anyway.
    """
    try:
        block = json.loads(text)
    except ValueError:
        return ({}, None, {})
    if not isinstance(block, dict):
        return ({}, None, {})
    found: "dict[str, PandasColumn]" = {}
    zones: "dict[str, str]" = {}
    listed = block["columns"] if "columns" in block else []
    if isinstance(listed, list):
        for item in listed:
            if not isinstance(item, dict) or "field_name" not in item:
                continue
            name = item["field_name"]
            kind = item["pandas_type"] if "pandas_type" in item else None
            numpy_kind = item["numpy_type"] if "numpy_type" in item else None
            if not isinstance(name, str) or kind not in PANDAS_TYPES or numpy_kind not in NUMPY_TYPES:
                continue
            ordered: "bool | None" = None
            extra = item["metadata"] if "metadata" in item else None
            if isinstance(extra, dict):
                if kind == "categorical" and "ordered" in extra and isinstance(extra["ordered"], bool):
                    ordered = extra["ordered"]
                if "timezone" in extra and isinstance(extra["timezone"], str):
                    zones[name] = extra["timezone"]
            found[name] = PandasColumn(pandas_type=f"{kind}", numpy_type=f"{numpy_kind}", ordered=ordered)
    index: "NativeIndex | None" = None
    marks = block["index_columns"] if "index_columns" in block else None
    if isinstance(marks, list):
        named: "list[str]" = []
        start: "int | None" = None
        step: "int | None" = None
        for mark in marks:
            if isinstance(mark, str):
                named += [mark]
            elif isinstance(mark, dict) and "kind" in mark and mark["kind"] == "range":
                first = mark["start"] if "start" in mark else None
                stride = mark["step"] if "step" in mark else None
                if first in (0, 1) and stride == 1 and not isinstance(first, bool):
                    start = int(f"{first}")
                    step = 1
        if named or start is not None:
            index = NativeIndex(columns=tuple(named), start=start, step=step)
    return (found, index, zones)


def pandas_block(form: NativeForm, names: "tuple[str, ...]", rows: int) -> str:
    """pandas' metadata block for a twin, rebuilt from the published fields alone (no copied text).

    Guarantees: JSON pandas' reader (pyarrow's `pandas_compat`) reads;
    names only the columns, their published types, the published index,
    and a creator naming synthtwin. Determinism: a fixed function of the
    form, the names and the row count.
    """
    columns: "list[dict[str, object]]" = []
    for place in range(len(form.columns)):
        column = form.columns[place]
        if column.pandas is None:
            continue
        extra: "dict[str, object] | None" = None
        if column.pandas.pandas_type == "categorical":
            extra = {"num_categories": None, "ordered": column.pandas.ordered is True}
        if column.pandas.pandas_type == "datetimetz":
            extra = {"timezone": column.zone if column.zone is not None else "UTC"}
        columns += [
            {
                "name": names[place],
                "field_name": names[place],
                "pandas_type": column.pandas.pandas_type,
                "numpy_type": column.pandas.numpy_type,
                "metadata": extra,
            }
        ]
    marks: "list[object]" = []
    if form.index is not None:
        for name in form.index.columns:
            marks += [name]
        if form.index.start is not None:
            start = form.index.start
            marks += [{"kind": "range", "name": None, "start": start, "stop": start + rows, "step": 1}]
    block = {
        "index_columns": marks,
        "column_indexes": [
            {"name": None, "field_name": None, "pandas_type": "unicode", "numpy_type": "object",
             "metadata": {"encoding": "UTF-8"}}
        ],
        "columns": columns,
        "creator": {"library": "synthtwin", "version": "1"},
        "pandas_version": "2.0.0",
    }
    return json.dumps(block, sort_keys=False, separators=(", ", ": "))


# -- Arrow's own schema, for a Parquet twin pandas wrote the source of ----
#
# pyarrow keeps each column's Arrow type in a Parquet file's key-value
# pairs under `ARROW:schema`: an Arrow IPC schema message (FlatBuffers),
# encoded in base64. pandas reads a categorical back as a categorical, and
# a time zone in its own unit, only where that record stands; pandas'
# own block restores the rest. The record is REBUILT here from the
# published fields alone -- the storage, pandas' type words, the order
# flag and the zone's name -- and never copied out of the source.

ARROW_KEY = "ARROW:schema"
_FB_INT = 2
_FB_FLOAT = 3
_FB_UTF8 = 5
_FB_BOOL = 6
_FB_DECIMAL = 7
_FB_DATE = 8
_FB_TIME = 9
_FB_TIMESTAMP = 10
_FB_LARGE_UTF8 = 20
_FB_UNITS = {"ms": 1, "us": 2, "ns": 3}


@dataclasses.dataclass(frozen=True)
class _FbTable:
    """A FlatBuffers table to write: (slot, kind, value) fields, kind one of b h i q B o."""

    fields: "tuple[tuple[int, str, object], ...]"


@dataclasses.dataclass(frozen=True)
class _FbVector:
    """A FlatBuffers vector of tables."""

    items: "tuple[_FbTable, ...]"


_FB_SIZES = {"b": 1, "B": 1, "h": 2, "i": 4, "q": 8, "o": 4}


def _fb_align(out: bytearray, size: int) -> None:
    while len(out) % size:
        out += b"\x00"


def _fb_place(out: bytearray, value: object) -> int:
    """Write ``value`` (a table, a vector of tables or a text) at the end of ``out``; where it starts."""
    if isinstance(value, str):
        _fb_align(out, 4)
        at = len(out)
        data = bytes(value, "utf-8")
        out += little(len(data), 4)
        out += data
        out += b"\x00"
        return at
    if isinstance(value, (_FbVector,)):
        _fb_align(out, 4)
        at = len(out)
        out += little(len(value.items), 4)
        slots: "list[int]" = []
        for _ in value.items:
            slots += [len(out)]
            out += bytes(4)
        for index in range(len(value.items)):
            target = _fb_place(out, value.items[index])
            out[slots[index] : slots[index] + 4] = little(target - slots[index], 4)
        return at
    if not isinstance(value, (_FbTable,)):
        raise TypeError("internal check: a FlatBuffers value of no known kind")
    fields = value.fields
    width = 0
    for slot, _kind, _held in fields:
        if slot + 1 > width:
            width = slot + 1
    # The table's own layout: its vtable offset, then each field aligned
    # to its size, the widest first.
    layout: "list[tuple[int, str, object, int]]" = []
    cursor = 4
    for size in (8, 4, 2, 1):
        for slot, kind, held in fields:
            if _FB_SIZES[kind] != size:
                continue
            while cursor % size:
                cursor = cursor + 1
            layout += [(slot, kind, held, cursor)]
            cursor = cursor + size
    table_size = cursor
    vtable = little(4 + 2 * width, 2) + little(table_size, 2)
    places = [0] * width
    for slot, _kind, _held, offset in layout:
        places[slot] = offset
    for offset in places:
        vtable = vtable + little(offset, 2)
    _fb_align(out, 2)
    vtable_at = len(out)
    out += vtable
    _fb_align(out, 8)
    table_at = len(out)
    out += little(table_at - vtable_at, 4)
    out += bytes(table_size - 4)
    pending: "list[tuple[int, object]]" = []
    for _slot, kind, held, offset in layout:
        at = table_at + offset
        if kind == "o":
            pending += [(at, held)]
            continue
        size = _FB_SIZES[kind]
        number = 1 if held is True else 0 if held is False else int(f"{held}")
        out[at : at + size] = little(number, size)
    for at, held in pending:
        target = _fb_place(out, held)
        out[at : at + 4] = little(target - at, 4)
    return table_at


def _fb_buffer(root: _FbTable) -> bytes:
    out = bytearray(8)
    target = _fb_place(out, root)
    out[0:4] = little(target, 4)
    _fb_align(out, 8)
    return bytes(out)


def _arrow_type(column: NativeColumn) -> "tuple[int, _FbTable] | None":
    """The Arrow type of a published column, as (the union's tag, its table), or None where no record is written."""
    store = column.storage
    bits = {
        STORE_INT8: (8, True), STORE_INT16: (16, True), STORE_INT32: (32, True), STORE_INT64: (64, True),
        STORE_UINT8: (8, False), STORE_UINT16: (16, False), STORE_UINT32: (32, False), STORE_UINT64: (64, False),
    }
    if store in bits:
        width, signed = bits[store]
        return (_FB_INT, _FbTable(fields=((0, "i", width), (1, "B", signed))))
    if store == STORE_FLOAT32:
        return (_FB_FLOAT, _FbTable(fields=((0, "h", 1),)))
    if store == STORE_FLOAT64:
        return (_FB_FLOAT, _FbTable(fields=((0, "h", 2),)))
    if store == STORE_BOOLEAN:
        return (_FB_BOOL, _FbTable(fields=()))
    if store == STORE_STRING:
        large = (
            column.pandas is not None
            and column.pandas.numpy_type in ("str", "string")
            and column.pandas.pandas_type != "categorical"
        )
        return (_FB_LARGE_UTF8 if large else _FB_UTF8, _FbTable(fields=()))
    if store == STORE_DATE:
        return (_FB_DATE, _FbTable(fields=((0, "h", 0),)))
    if store == STORE_DECIMAL:
        precision = column.precision if column.precision is not None else 38
        scale = column.scale if column.scale is not None else 0
        return (_FB_DECIMAL, _FbTable(fields=((0, "i", precision), (1, "i", scale), (2, "i", 128))))
    moments = {
        STORE_TIMESTAMP_MS: "ms", STORE_TIMESTAMP_US: "us", STORE_TIMESTAMP_NS: "ns",
        STORE_TIME_MS: "ms", STORE_TIME_US: "us", STORE_TIME_NS: "ns",
    }
    if store in moments:
        unit = _FB_UNITS[moments[store]]
        if store in (STORE_TIME_MS, STORE_TIME_US, STORE_TIME_NS):
            return (_FB_TIME, _FbTable(fields=((0, "h", unit), (1, "i", 32 if store == STORE_TIME_MS else 64))))
        if column.utc:
            zone = column.zone if column.zone is not None else "UTC"
            return (_FB_TIMESTAMP, _FbTable(fields=((0, "h", unit), (1, "o", zone))))
        return (_FB_TIMESTAMP, _FbTable(fields=((0, "h", unit),)))
    return None


_BASE64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"


def _base64(data: bytes) -> str:
    """Standard base64 with padding, written out (no module of the standard library is admitted for it)."""
    alphabet = bytes(_BASE64, "ascii")
    out = bytearray()
    for at in range(0, len(data) - len(data) % 3, 3):
        word = (data[at] << 16) | (data[at + 1] << 8) | data[at + 2]
        out += bytes([alphabet[word >> 18], alphabet[(word >> 12) & 63], alphabet[(word >> 6) & 63], alphabet[word & 63]])
    rest = len(data) % 3
    if rest == 1:
        word = data[len(data) - 1] << 16
        out += bytes([alphabet[word >> 18], alphabet[(word >> 12) & 63]]) + b"=="
    elif rest == 2:
        word = (data[len(data) - 2] << 16) | (data[len(data) - 1] << 8)
        out += bytes([alphabet[word >> 18], alphabet[(word >> 12) & 63], alphabet[(word >> 6) & 63]]) + b"="
    return str(bytes(out), "ascii")


def arrow_schema_text(form: NativeForm, names: "tuple[str, ...]", nullable: "tuple[bool, ...]", pandas_text: str) -> str:
    """The `ARROW:schema` record of a Parquet twin, or '' where the source carried pandas' block for no column.

    Guarantees: base64 of an Arrow IPC schema message (the continuation
    mark, its length, the FlatBuffers `Message` holding a `Schema`),
    which pyarrow reads back to the published types: a categorical
    pandas named is a dictionary of texts (the indices as narrow as
    pandas makes them, the order flag published), a zone's name stands
    on its timestamps, and pandas' block rides in the schema's own pairs
    as pyarrow writes it. Determinism: a fixed function of its arguments.
    """
    # A ZONE STANDS ON ITS TIMESTAMPS ONLY IN THIS RECORD (lane TOOLS; the
    # outside review of batch 4zz, item 11): a file Arrow wrote with no
    # pandas block keeps a timestamp's zone here alone, so the record is
    # written for it too -- every type rebuilt from the published fields,
    # and no pandas block among its pairs.
    with_pandas = any(column.pandas is not None for column in form.columns)
    zoned = any(column.zone is not None and column.utc for column in form.columns)
    if not with_pandas and not zoned:
        return ""
    fields: "list[_FbTable]" = []
    for place in range(len(form.columns)):
        column = form.columns[place]
        typed = _arrow_type(column)
        if typed is None:
            return ""
        tag, table = typed
        parts: "list[tuple[int, str, object]]" = [
            (0, "o", names[place]),
            (1, "B", nullable[place]),
            (2, "B", tag),
            (3, "o", table),
            (5, "o", _FbVector(items=())),
        ]
        if column.pandas is not None and column.pandas.pandas_type == "categorical":
            index_width = 8
            if column.pandas.numpy_type == "int16":
                index_width = 16
            elif column.pandas.numpy_type == "int32":
                index_width = 32
            elif column.pandas.numpy_type == "int64":
                index_width = 64
            parts += [
                (4, "o", _FbTable(fields=(
                    (0, "q", place),
                    (1, "o", _FbTable(fields=((0, "i", index_width), (1, "B", True)))),
                    (2, "B", column.pandas.ordered is True),
                ))),
            ]
        fields += [_FbTable(fields=tuple(parts))]
    if with_pandas:
        pairs = _FbVector(items=(_FbTable(fields=((0, "o", PANDAS_KEY), (1, "o", pandas_text))),))
        schema = _FbTable(fields=((1, "o", _FbVector(items=tuple(fields))), (2, "o", pairs)))
    else:
        schema = _FbTable(fields=((1, "o", _FbVector(items=tuple(fields))),))
    message = _FbTable(fields=((0, "h", 4), (1, "B", 1), (2, "o", schema), (3, "q", 0)))
    body = _fb_buffer(message)
    framed = b"\xff\xff\xff\xff" + little(len(body), 4) + body
    return _base64(framed)



# -- Arrow's own schema, read back for the zone of each timestamp ----------
#
# The other half of the record above (lane TOOLS; the outside review of
# batch 4zz, item 11): a file Arrow wrote without pandas' block names a
# timestamp's zone only in its `ARROW:schema` record, so the reader reads
# that one string per timestamp out of it -- the FlatBuffers `Message`, its
# `Schema`, each `Field`'s name and, where its type is a `Timestamp`, the
# type's `timezone` -- with the standard library alone, every offset held
# inside the record's bytes.

_BASE64_VALUES = {_BASE64[at]: at for at in range(len(_BASE64))}


def _unbase64(text: str) -> "bytes | None":
    """Standard base64 read back (the padding optional), or None where a character is not base64's."""
    out = bytearray()
    word = 0
    held = 0
    for character in text:
        if character == "=":
            break
        if character in "\r\n":
            continue
        if character not in _BASE64_VALUES:
            return None
        word = (word << 6) | _BASE64_VALUES[character]
        held = held + 6
        if held >= 8:
            held = held - 8
            out += bytes([(word >> held) & 255])
    return bytes(out)


def _fb_word(data: bytes, at: int, width: int, signed: bool = False) -> "int | None":
    """A little-endian whole number of ``width`` bytes at ``at``, or None past the end."""
    if at < 0 or at + width > len(data):
        return None
    value = 0
    for step in range(width):
        value = value | (data[at + step] << (8 * step))
    if signed and value >= 1 << (8 * width - 1):
        value = value - (1 << (8 * width))
    return value


def _fb_field(data: bytes, table: int, slot: int) -> "int | None":
    """Where a table's field ``slot`` stands, or None where the table does not carry it."""
    back = _fb_word(data, table, 4, True)
    if back is None:
        return None
    vtable = table - back
    size = _fb_word(data, vtable, 2)
    if size is None or 4 + 2 * slot + 2 > size:
        return None
    offset = _fb_word(data, vtable + 4 + 2 * slot, 2)
    if not offset:
        return None
    return table + offset


def _fb_target(data: bytes, at: "int | None") -> "int | None":
    """Where the offset stored at ``at`` leads."""
    if at is None:
        return None
    step = _fb_word(data, at, 4)
    return None if step is None else at + step


def _fb_text(data: bytes, at: "int | None") -> "str | None":
    """The string the offset at ``at`` leads to, or None."""
    start = _fb_target(data, at)
    if start is None:
        return None
    length = _fb_word(data, start, 4)
    if length is None or start + 4 + length > len(data):
        return None
    try:
        return str(data[start + 4 : start + 4 + length], "utf-8")
    except UnicodeDecodeError:
        return None


def arrow_zones(text: str) -> "dict[str, str]":
    """Each timestamp column's zone name in an `ARROW:schema` record, by the column's name; {} where none is read.

    Guarantees: reads the record's bytes alone and never raises: a record
    that is not base64, not a schema message, or whose offsets lead
    outside its bytes gives {} or the zones read before the fault. A
    fixed function of the text.
    """
    data = _unbase64(text) if isinstance(text, str) else None
    if data is None or len(data) < 8:
        return {}
    start = 0
    if _fb_word(data, 0, 4) == 0xFFFFFFFF:
        start = 8
    elif _fb_word(data, 0, 4) is not None:
        start = 4
    body = data[start:]
    root = _fb_target(body, 0)
    if root is None:
        return {}
    kind = _fb_field(body, root, 1)
    if kind is None or kind >= len(body) or body[kind] != 1:
        return {}
    schema = _fb_target(body, _fb_field(body, root, 2))
    if schema is None:
        return {}
    fields = _fb_target(body, _fb_field(body, schema, 1))
    count = _fb_word(body, fields, 4) if fields is not None else None
    if fields is None or count is None:
        return {}
    zones: "dict[str, str]" = {}
    for place in range(count):
        field = _fb_target(body, fields + 4 + 4 * place)
        if field is None:
            return zones
        name = _fb_text(body, _fb_field(body, field, 0))
        tag_at = _fb_field(body, field, 2)
        if name is None or tag_at is None or tag_at >= len(body) or body[tag_at] != _FB_TIMESTAMP:
            continue
        typed = _fb_target(body, _fb_field(body, field, 3))
        zone = _fb_text(body, _fb_field(body, typed, 1)) if typed is not None else None
        if zone:
            zones[name] = zone
    return zones