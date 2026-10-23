"""The columns lane R1's two date questions are measured on (plan P4-D381).

Seeded, made-up cells and nothing else: every value is drawn from a
`random.Random` seeded by the shape's own name, so the same name gives
the same cells on every platform and every supported Python.

THREE FAMILIES.

* `CLEAN` -- the thirty-seven spellings of the date and time reach audit
  of 2026-10-01 that are read, written back and checked with no gap at
  668f276: SQL Server, REDCap, SAS, SPSS, HL7, FHIR, Excel, R and pandas
  exports, written exactly as the audit's battery wrote them, at the
  audit's own seeds. Thirty-six of them may raise neither question; the
  thirty-seventh, `mdy_ambiguous` -- `mm/dd/yyyy` whose every day is 12
  or less -- is read month first and RIGHT, and is the same cells as a
  day-first column with its two fields swapped, so the day-or-month
  question is put to it and its standing answer keeps it right.
* `DAY_OR_MONTH` -- columns of dates no value of which says whether the
  day or the month comes first, each with the order it is really
  written in.
* `CODES` -- columns of dates or times beside a few repeated codes, each
  with the codes, and `NOT_ASKED` -- the shapes either question must
  leave alone: too few rows, too many codes, too much of the column, too
  few dates, no dates at all.

Each shape carries the `strptime` format the person who owns the table
would read it with, which is what "the twin parses" is measured by.
"""

import dataclasses
import datetime as dt
import random
import zlib

MON = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
MONTH = (
    "January", "February", "March", "April", "May", "June", "July",
    "August", "September", "October", "November", "December",
)
# An emergency department's hours, the audit's own weights.
_HOURS = (
    2.6, 2.2, 1.9, 1.6, 1.4, 1.4, 1.7, 2.5, 3.8, 5.0, 5.9, 6.2,
    6.1, 5.9, 5.7, 5.6, 5.6, 5.6, 5.5, 5.3, 4.9, 4.4, 3.8, 3.2,
)
ROWS = 1000


def _draw(name: str) -> random.Random:
    return random.Random(zlib.crc32(name.encode("utf-8")))


def _date(draw: random.Random) -> dt.datetime:
    day = dt.date(2021, 1, 1) + dt.timedelta(days=draw.randrange(1461))
    return dt.datetime(day.year, day.month, day.day)


def _moment(draw: random.Random) -> dt.datetime:
    day = dt.date(2021, 1, 1) + dt.timedelta(days=draw.randrange(1461))
    hour = draw.choices(range(24), weights=_HOURS)[0]
    return dt.datetime(
        day.year, day.month, day.day, hour, draw.randrange(60),
        draw.randrange(60), draw.randrange(1000000),
    )


def _minute(draw: random.Random) -> dt.datetime:
    return _moment(draw).replace(second=0, microsecond=0)


def _day_twelve_or_less(draw: random.Random) -> dt.datetime:
    while True:
        moment = _date(draw)
        if moment.day <= 12 and moment.day != moment.month:
            return moment


_MAKERS = {
    "date": _date,
    "moment": _moment,
    "minute": _minute,
    "le12": _day_twelve_or_less,
}


@dataclasses.dataclass(frozen=True)
class Shape:
    """One column: how its cells are drawn and written, and how they are read.

    ``fmt`` is the person's own `strptime` format, or empty where none
    reads the spelling (a quarter). ``codes`` are the spellings that
    stand for a missing value: one every ``every`` rows, taking the codes
    in turn, or, where ``share`` is given instead, each row a code with
    that chance -- the audit's own way, kept for its own column.
    ``answer`` is the answer that repairs the column, and ``rows`` how
    many cells it has.
    """

    name: str
    maker: str
    write: "object"
    fmt: str
    codes: "tuple[str, ...]" = ()
    every: int = 0
    answer: str = ""
    rows: int = ROWS
    share: float = 0.0


def cells(shape: Shape) -> "list[str]":
    """The shape's cells, in row order, from its own seed."""
    draw = _draw(shape.name)
    maker = _MAKERS[shape.maker]
    out: "list[str]" = []
    for row in range(shape.rows):
        moment = maker(draw)
        if shape.every and row % shape.every == shape.every - 1:
            out += [shape.codes[(row // shape.every) % len(shape.codes)]]
            continue
        if shape.share and draw.random() < shape.share:
            out += [draw.choice(list(shape.codes))]
            continue
        writer = shape.write
        assert callable(writer)
        out += [f"{writer(moment)}"]
    return out


def _quarter(moment: dt.datetime) -> str:
    return f"{moment.year}-Q{(moment.month - 1) // 3 + 1}"


CLEAN = (
    Shape("ss_datetime_midnight", "date", lambda m: m.strftime("%Y-%m-%d") + " 00:00:00.000", "%Y-%m-%d %H:%M:%S.%f"),
    Shape("ss_date", "date", lambda m: m.strftime("%Y-%m-%d"), "%Y-%m-%d"),
    Shape("ss_time0", "moment", lambda m: m.strftime("%H:%M:%S"), "%H:%M:%S"),
    Shape("cab_datekey", "date", lambda m: m.strftime("%Y%m%d"), "%Y%m%d"),
    Shape("rc_ymd", "date", lambda m: m.strftime("%Y-%m-%d"), "%Y-%m-%d"),
    Shape("rc_mdy_slash", "date", lambda m: m.strftime("%m/%d/%Y"), "%m/%d/%Y"),
    Shape("rc_dmy_slash", "date", lambda m: m.strftime("%d/%m/%Y"), "%d/%m/%Y"),
    Shape("rc_dt_ymd_hm", "minute", lambda m: m.strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M"),
    Shape("rc_dt_ymd_hms", "moment", lambda m: m.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S"),
    Shape("rc_time_hm", "moment", lambda m: m.strftime("%H:%M"), "%H:%M"),
    Shape("rc_time_hms", "moment", lambda m: m.strftime("%H:%M:%S"), "%H:%M:%S"),
    Shape("sas_mmddyy10", "date", lambda m: m.strftime("%m/%d/%Y"), "%m/%d/%Y"),
    Shape("sas_e8601dt", "moment", lambda m: m.strftime("%Y-%m-%dT%H:%M:%S"), "%Y-%m-%dT%H:%M:%S"),
    Shape("spss_date11", "date", lambda m: f"{m.day:02d}-{MON[m.month - 1].upper()}-{m.year}", "%d-%b-%Y"),
    Shape("spss_edate10", "date", lambda m: m.strftime("%d.%m.%Y"), "%d.%m.%Y"),
    Shape("spss_sdate10", "date", lambda m: m.strftime("%Y/%m/%d"), "%Y/%m/%d"),
    Shape("hl7_dt8", "date", lambda m: m.strftime("%Y%m%d"), "%Y%m%d"),
    Shape("iso_z", "moment", lambda m: m.strftime("%Y-%m-%dT%H:%M:%SZ"), "%Y-%m-%dT%H:%M:%SZ"),
    Shape("iso_offset", "moment", lambda m: m.strftime("%Y-%m-%dT%H:%M:%S") + "+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    Shape("iso_t_minutes", "minute", lambda m: m.strftime("%Y-%m-%dT%H:%M"), "%Y-%m-%dT%H:%M"),
    Shape("iso_quarter", "date", _quarter, ""),
    Shape("xl_us_date", "date", lambda m: f"{m.month}/{m.day}/{m.year}", "%m/%d/%Y"),
    Shape("xl_iso_dt", "moment", lambda m: m.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S"),
    Shape("mil_colon", "minute", lambda m: m.strftime("%H:%M"), "%H:%M"),
    Shape("mon_dd_mmm_yyyy", "date", lambda m: f"{m.day:02d}-{MON[m.month - 1]}-{m.year}", "%d-%b-%Y"),
    Shape("mon_mmm_d_yyyy", "date", lambda m: f"{MON[m.month - 1]} {m.day}, {m.year}", "%b %d, %Y"),
    Shape("mon_mmmm_d_yyyy", "date", lambda m: f"{MONTH[m.month - 1]} {m.day}, {m.year}", "%B %d, %Y"),
    Shape("mon_d_mmmm_yyyy", "date", lambda m: f"{m.day} {MONTH[m.month - 1]} {m.year}", "%d %B %Y"),
    Shape("dmy_unpadded", "date", lambda m: f"{m.day}/{m.month}/{m.year}", "%d/%m/%Y"),
    Shape("dmy_padded", "date", lambda m: m.strftime("%d/%m/%Y"), "%d/%m/%Y"),
    Shape("mdy_ambiguous", "le12", lambda m: m.strftime("%m/%d/%Y"), "%m/%d/%Y", answer="month-first"),
    Shape("dmy_dt", "minute", lambda m: m.strftime("%d/%m/%Y %H:%M"), "%d/%m/%Y %H:%M"),
    Shape("yy_mdy", "date", lambda m: f"{m.month}/{m.day}/{m:%y}", "%m/%d/%y"),
    Shape("yy_dmy", "date", lambda m: m.strftime("%d/%m/%y"), "%d/%m/%y"),
    Shape("r_posixct", "moment", lambda m: m.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S"),
    Shape("pd_tz", "moment", lambda m: m.strftime("%Y-%m-%d %H:%M:%S") + "+00:00", "%Y-%m-%d %H:%M:%S%z"),
    Shape("pd_period_month", "date", lambda m: m.strftime("%Y-%m"), "%Y-%m"),
)

# The one clean spelling no value of which says which comes first.
CLEAN_AMBIGUOUS = ("mdy_ambiguous",)


def _month_start(moment: dt.datetime) -> str:
    """The first of the month the moment falls in, written day first."""
    return f"01/{moment.month:02d}/{moment.year}"


DAY_OR_MONTH = (
    Shape("dmy_ambiguous", "le12", lambda m: m.strftime("%d/%m/%Y"), "%d/%m/%Y", answer="day-first"),
    Shape("month_start_dmy", "date", _month_start, "%d/%m/%Y", answer="day-first"),
    Shape("dotted_dmy_ambiguous", "le12", lambda m: m.strftime("%d.%m.%Y"), "%d.%m.%Y", answer="day-first"),
    Shape("yy_dmy_ambiguous", "le12", lambda m: m.strftime("%d/%m/%y"), "%d/%m/%y", answer="day-first"),
    Shape(
        "dmy_dt_ambiguous", "le12",
        lambda m: m.strftime("%d/%m/%Y") + f" {(m.day * 7) % 24:02d}:{(m.month * 13) % 60:02d}",
        "%d/%m/%Y %H:%M", answer="day-first",
    ),
    Shape("mdy_ambiguous", "le12", lambda m: m.strftime("%m/%d/%Y"), "%m/%d/%Y", answer="month-first"),
)

CODES = (
    # A code every 33rd row is 30 of a thousand, 3 in 100.
    Shape("clock_9999", "minute", lambda m: m.strftime("%H:%M"), "%H:%M", ("99:99",), 33, "missing"),
    Shape("clock_unk", "minute", lambda m: m.strftime("%H:%M"), "%H:%M", ("UNK",), 33, "missing"),
    Shape("mdy_zero", "date", lambda m: m.strftime("%m/%d/%Y"), "%m/%d/%Y", ("00/00/0000",), 33, "missing"),
    Shape("mdy_unk", "date", lambda m: m.strftime("%m/%d/%Y"), "%m/%d/%Y", ("UNK",), 33, "missing"),
    # The audit's own Caboodle column, at its own seed: a key of -1 or -2
    # on about 3 rows in 100, -1 twice as often.
    Shape(
        "cab_datekey_sentinels", "date", lambda m: m.strftime("%Y%m%d"), "%Y%m%d",
        ("-1", "-1", "-2"), 0, "missing", share=0.03,
    ),
    Shape("iso_zero_date", "date", lambda m: m.strftime("%Y-%m-%d"), "%Y-%m-%d", ("0000-00-00",), 33, "missing"),
    Shape("iso_unk", "date", lambda m: m.strftime("%Y-%m-%d"), "%Y-%m-%d", ("UNK",), 50, "missing"),
    # ...and one the date rule already reads, its codes under its line:
    # twenty rows of four thousand, a two-hundredth.
    Shape(
        "iso_unk_sparse", "date", lambda m: m.strftime("%Y-%m-%d"), "%Y-%m-%d",
        ("UNK",), 200, "missing", 4000,
    ),
)


def _iso(moment: dt.datetime) -> str:
    return moment.strftime("%Y-%m-%d")


def _two_dates(moment: dt.datetime) -> str:
    return "2021-03-01" if moment.day % 2 else "2021-03-02"


def _notes(moment: dt.datetime) -> str:
    return f"bed {moment.toordinal() % 997} side {moment.day}"


NOT_ASKED = (
    # Five rows of the code: a slip of a keyboard as often as a code.
    Shape("iso_unk_few", "date", _iso, "%Y-%m-%d", ("UNK",), 200),
    # A third of the column: something else, with dates in it.
    Shape("iso_unk_third", "date", _iso, "%Y-%m-%d", ("UNK",), 3),
    # Six different codes, 13 or 14 rows each: more than a few.
    Shape(
        "iso_six_codes", "date", _iso, "%Y-%m-%d",
        ("UNK", "NK", "N/K", "XX", "TBD", "PEND"), 12,
    ),
    # Two dates beside the code: the date rule is not what reads it.
    Shape("two_dates_and_unk", "date", _two_dates, "%Y-%m-%d", ("UNK",), 33),
    # No dates at all: many different notes beside the code, so the one
    # rule that stands between it and the question is the date rule.
    Shape("notes_with_codes", "date", _notes, "", ("UNK",), 33),
)


def by_name(name: str) -> Shape:
    """The shape of that name, from any family."""
    for shape in CLEAN + DAY_OR_MONTH + CODES + NOT_ASKED:
        if shape.name == name:
            return shape
    raise KeyError(name)


def parses(cell: str, fmt: str) -> bool:
    """Whether the person's own format reads one cell."""
    try:
        dt.datetime.strptime(cell, fmt)
    except ValueError:
        return False
    return True
