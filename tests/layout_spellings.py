"""The date spellings landing R2a reads, as seeded neutral columns (plan P4-D383).

Built at runtime from a seeded generator, as every fixture of this suite
is (plan D13): three calendar years of moments whose hour follows an
emergency-department profile and whose minutes, seconds and fractions are
uniform. Each shape is the cells, the pattern a cell written in the
source's own spelling matches -- padding, case and marks exact -- and the
`strptime` format the code a person runs on their own table would use
(None where Python has no directive for the spelling: seven-figure
fractions, `+HH` and `UTC` offsets, the CLDR month words, an offset some
cells omit).

THE THIRTY-NINE SPELLINGS of the gate and of `K-S3-58`: the thirty-two of
the date half that no named member read before R2a -- twenty-seven of the
reach audit's 116 and five of its skeptic's -- and the seven the R2 design
skeptic added (M2's offset some cells omit, M3's unpadded dotted dates with
a four-figure year, M4's en-GB and en-AU month words).
"""

import datetime
import random
import re

ROWS = 1000

_DAYS = [datetime.date(2021, 1, 1) + datetime.timedelta(days=step) for step in range(3 * 365)]
_HOURS = (
    2.6, 2.2, 1.9, 1.6, 1.4, 1.4, 1.7, 2.5, 3.8, 5.0, 5.9, 6.2,
    6.1, 5.9, 5.7, 5.6, 5.6, 5.6, 5.5, 5.3, 4.9, 4.4, 3.8, 3.2,
)
_MON = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
_GB = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sept", "Oct", "Nov", "Dec")
_AU = ("Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sept", "Oct", "Nov", "Dec")
_MONTH = (
    "January", "February", "March", "April", "May", "June", "July",
    "August", "September", "October", "November", "December",
)
_WEEKDAY = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


def moments(rows: int, seed: int) -> "list[datetime.datetime]":
    """``rows`` seeded moments of 2021 to 2023, to the microsecond."""
    draw = random.Random(seed)
    found: "list[datetime.datetime]" = []
    for _row in range(rows):
        day = draw.choice(_DAYS)
        hour = draw.choices(range(24), weights=_HOURS)[0]
        found += [
            datetime.datetime(
                day.year, day.month, day.day, hour, draw.randrange(60),
                draw.randrange(60), draw.randrange(1000000),
            )
        ]
    return found


def _dst(moment: datetime.datetime) -> bool:
    """Whether a moment falls in the United States' summer time."""
    march = datetime.date(moment.year, 3, 8)
    start = march + datetime.timedelta(days=(6 - march.weekday()) % 7)
    november = datetime.date(moment.year, 11, 1)
    end = november + datetime.timedelta(days=(6 - november.weekday()) % 7)
    return start <= moment.date() < end


_Y4 = r"\d{4}"
_MM = r"(?:0[1-9]|1[0-2])"
_DD = r"(?:0[1-9]|[12]\d|3[01])"
_M = r"(?:[1-9]|1[0-2])"
_D = r"(?:[1-9]|[12]\d|3[01])"
_T = r"(?:[01]\d|2[0-3]):[0-5]\d"
_TS = _T + r":[0-5]\d"


def _words(names: "tuple[str, ...]") -> str:
    return "(?:" + "|".join(names) + ")"


# name: (writer, the source's exact pattern, strptime format or None)
SPELLINGS = {
    # -- twenty-seven of the reach audit's 116 ----------------------------
    "ss_datetimeoffset": (
        lambda m: f"{m:%Y-%m-%d %H:%M:%S}.{m.microsecond:06d}{m.microsecond % 7} +00:00",
        _Y4 + "-" + _MM + "-" + _DD + " " + _TS + r"\.\d{7} \+00:00", None,
    ),
    "ss_datetimeoffset_dst": (
        lambda m: f"{m:%Y-%m-%d %H:%M:%S}.{m.microsecond:06d}{m.microsecond % 7} "
        + ("-04:00" if _dst(m) else "-05:00"),
        _Y4 + "-" + _MM + "-" + _DD + " " + _TS + r"\.\d{7} -0[45]:00", None,
    ),
    "epic_military": (
        lambda m: m.strftime("%m/%d/%Y %H%M"),
        _MM + "/" + _DD + "/" + _Y4 + r" (?:[01]\d|2[0-3])[0-5]\d", "%m/%d/%Y %H%M",
    ),
    "redcap_mdy_hyphen": (lambda m: m.strftime("%m-%d-%Y"), _MM + "-" + _DD + "-" + _Y4, "%m-%d-%Y"),
    "redcap_dmy_hyphen": (lambda m: m.strftime("%d-%m-%Y"), _DD + "-" + _MM + "-" + _Y4, "%d-%m-%Y"),
    "redcap_mdy_hyphen_time": (
        lambda m: m.strftime("%m-%d-%Y %H:%M"), _MM + "-" + _DD + "-" + _Y4 + " " + _T, "%m-%d-%Y %H:%M",
    ),
    "redcap_dmy_hyphen_time": (
        lambda m: m.strftime("%d-%m-%Y %H:%M"), _DD + "-" + _MM + "-" + _Y4 + " " + _T, "%d-%m-%Y %H:%M",
    ),
    "sas_date9": (
        lambda m: f"{m.day:02d}{_MON[m.month - 1].upper()}{m.year}",
        _DD + _words(tuple(name.upper() for name in _MON)) + _Y4, "%d%b%Y",
    ),
    "sas_datetime20": (
        lambda m: f"{m.day:02d}{_MON[m.month - 1].upper()}{m.year}:{m:%H:%M:%S}",
        _DD + _words(tuple(name.upper() for name in _MON)) + _Y4 + ":" + _TS, "%d%b%Y:%H:%M:%S",
    ),
    "sas_datetime16": (
        lambda m: f"{m.day:02d}{_MON[m.month - 1].upper()}{m:%y}:{m:%H:%M:%S}",
        _DD + _words(tuple(name.upper() for name in _MON)) + r"\d\d:" + _TS, "%d%b%y:%H:%M:%S",
    ),
    "stata_td": (
        lambda m: f"{m.day:02d}{_MON[m.month - 1].lower()}{m.year}",
        _DD + _words(tuple(name.lower() for name in _MON)) + _Y4, "%d%b%Y",
    ),
    "stata_tc": (
        lambda m: f"{m.day:02d}{_MON[m.month - 1].lower()}{m.year} {m:%H:%M:%S}",
        _DD + _words(tuple(name.lower() for name in _MON)) + _Y4 + " " + _TS, "%d%b%Y %H:%M:%S",
    ),
    "spss_datetime20": (
        lambda m: f"{m.day:02d}-{_MON[m.month - 1].upper()}-{m.year} {m:%H:%M:%S}",
        _DD + "-" + _words(tuple(name.upper() for name in _MON)) + "-" + _Y4 + " " + _TS,
        "%d-%b-%Y %H:%M:%S",
    ),
    "spss_datetime22": (
        lambda m: f"{m.day:02d}-{_MON[m.month - 1].upper()}-{m.year} {m:%H:%M:%S}.{m.microsecond // 10000:02d}",
        _DD + "-" + _words(tuple(name.upper() for name in _MON)) + "-" + _Y4 + " " + _TS + r"\.\d\d",
        "%d-%b-%Y %H:%M:%S.%f",
    ),
    "hl7_ts14": (lambda m: m.strftime("%Y%m%d%H%M%S"), _Y4 + _MM + _DD + r"(?:[01]\d|2[0-3])[0-5]\d[0-5]\d", "%Y%m%d%H%M%S"),
    "hl7_ts12_offset": (
        lambda m: m.strftime("%Y%m%d%H%M") + ("-0400" if _dst(m) else "-0500"),
        _Y4 + _MM + _DD + r"(?:[01]\d|2[0-3])[0-5]\d-0[45]00", "%Y%m%d%H%M%z",
    ),
    "hl7_ts_fraction_offset": (
        lambda m: m.strftime("%Y%m%d%H%M%S") + f".{m.microsecond // 100:04d}+0000",
        _Y4 + _MM + _DD + r"(?:[01]\d|2[0-3])[0-5]\d[0-5]\d\.\d{4}\+0000", "%Y%m%d%H%M%S.%f%z",
    ),
    "hl7_ts12": (lambda m: m.strftime("%Y%m%d%H%M"), _Y4 + _MM + _DD + r"(?:[01]\d|2[0-3])[0-5]\d", "%Y%m%d%H%M"),
    "iso_offset_without_colon": (
        lambda m: m.strftime("%Y-%m-%dT%H:%M:%S") + "+0100",
        _Y4 + "-" + _MM + "-" + _DD + "T" + _TS + r"\+0100", "%Y-%m-%dT%H:%M:%S%z",
    ),
    "iso_basic_zulu": (
        lambda m: m.strftime("%Y%m%dT%H%M%SZ"),
        _Y4 + _MM + _DD + r"T(?:[01]\d|2[0-3])[0-5]\d[0-5]\dZ", "%Y%m%dT%H%M%SZ",
    ),
    "excel_d_mmm_yy": (
        lambda m: f"{m.day}-{_MON[m.month - 1]}-{m:%y}", _D + "-" + _words(_MON) + r"-\d\d", "%d-%b-%y",
    ),
    "excel_long_date": (
        lambda m: f"{_WEEKDAY[m.weekday()]}, {_MONTH[m.month - 1]} {m.day}, {m.year}",
        _words(_WEEKDAY) + ", " + _words(_MONTH) + " " + _D + ", " + _Y4, "%A, %B %d, %Y",
    ),
    "oracle_dd_mon_rr": (
        lambda m: f"{m.day:02d}-{_MON[m.month - 1].upper()}-{m:%y}",
        _DD + "-" + _words(tuple(name.upper() for name in _MON)) + r"-\d\d", "%d-%b-%y",
    ),
    "dotted_day_first_time": (
        lambda m: m.strftime("%d.%m.%Y %H:%M"), _DD + r"\." + _MM + r"\." + _Y4 + " " + _T, "%d.%m.%Y %H:%M",
    ),
    "year_first_unpadded": (
        lambda m: f"{m.year}-{m.month}-{m.day}", _Y4 + "-" + _M + "-" + _D, "%Y-%m-%d",
    ),
    "db2_timestamp": (
        lambda m: f"{m:%Y-%m-%d-%H.%M.%S}.{m.microsecond:06d}",
        _Y4 + "-" + _MM + "-" + _DD + r"-(?:[01]\d|2[0-3])\.[0-5]\d\.[0-5]\d\.\d{6}", "%Y-%m-%d-%H.%M.%S.%f",
    ),
    "year_first_dotted": (lambda m: m.strftime("%Y.%m.%d"), _Y4 + r"\." + _MM + r"\." + _DD, "%Y.%m.%d"),
    # -- five of the reach audit's skeptic ---------------------------------
    "postgres_utc": (
        lambda m: m.strftime("%Y-%m-%d %H:%M:%S") + "+00",
        _Y4 + "-" + _MM + "-" + _DD + " " + _TS + r"\+00", None,
    ),
    "postgres_new_york": (
        lambda m: m.strftime("%Y-%m-%d %H:%M:%S") + ("-04" if _dst(m) else "-05"),
        _Y4 + "-" + _MM + "-" + _DD + " " + _TS + "-0[45]", None,
    ),
    "r_utc_word": (
        lambda m: m.strftime("%Y-%m-%d %H:%M:%S") + " UTC",
        _Y4 + "-" + _MM + "-" + _DD + " " + _TS + " UTC", "%Y-%m-%d %H:%M:%S UTC",
    ),
    "comma_milliseconds": (
        lambda m: m.strftime("%Y-%m-%d %H:%M:%S") + f",{m.microsecond // 1000:03d}",
        _Y4 + "-" + _MM + "-" + _DD + " " + _TS + r",\d{3}", "%Y-%m-%d %H:%M:%S,%f",
    ),
    "dutch_unpadded": (lambda m: f"{m.day}-{m.month}-{m.year}", _D + "-" + _M + "-" + _Y4, "%d-%m-%Y"),
    # -- seven of the R2 design skeptic ------------------------------------
    "german_unpadded": (lambda m: f"{m.day}.{m.month}.{m.year}", _D + r"\." + _M + r"\." + _Y4, "%d.%m.%Y"),
    "german_unpadded_time": (
        lambda m: f"{m.day}.{m.month}.{m.year} {m:%H:%M}", _D + r"\." + _M + r"\." + _Y4 + " " + _T,
        "%d.%m.%Y %H:%M",
    ),
    "german_locale_string": (
        lambda m: f"{m.day}.{m.month}.{m.year}, {m:%H:%M:%S}", _D + r"\." + _M + r"\." + _Y4 + ", " + _TS,
        "%d.%m.%Y, %H:%M:%S",
    ),
    "british_sept": (
        lambda m: f"{m.day} {_GB[m.month - 1]} {m.year}", _D + " " + _words(_GB) + " " + _Y4, None,
    ),
    "british_sept_time": (
        lambda m: f"{m.day} {_GB[m.month - 1]} {m.year}, {m:%H:%M:%S}",
        _D + " " + _words(_GB) + " " + _Y4 + ", " + _TS, None,
    ),
    "australian_months": (
        lambda m: f"{m.day} {_AU[m.month - 1]} {m.year}", _D + " " + _words(_AU) + " " + _Y4, None,
    ),
    "hl7_offset_some_omit": (
        lambda m: m.strftime("%Y%m%d%H%M%S") + (("-0400" if _dst(m) else "-0500") if m.microsecond % 2 else ""),
        _Y4 + _MM + _DD + r"(?:[01]\d|2[0-3])[0-5]\d[0-5]\d(?:-0[45]00)?", None,
    ),
}

# -- 3b.R2c (P4-D383) ---------------------------------------------------
# THE PARTIAL DATES AND THE DAYS OF THE YEAR landing R2c reads: four
# columns some of whose cells stop short of the layout -- each cell's
# precision drawn from its seeded moment's microsecond, so the shares are
# fixed -- and two written as a year and its day of the year, read only
# under `--date-column` (question Q6). Their strptime formats are given as
# alternatives, `|` between them, one for each precision a cell may have.
_UPPER = tuple(word.upper() for word in _MON)


def _cut(moment: datetime.datetime, whole: str, *shorter: str) -> str:
    """One cell of a partial column: whole on 58 in 100, then each shorter form in turn."""
    share = moment.microsecond % 100
    if share < 58 or not shorter:
        return moment.strftime(whole)
    if share < 85 or len(shorter) == 1:
        return moment.strftime(shorter[0])
    return moment.strftime(shorter[1])


def _medidata(moment: datetime.datetime) -> str:
    """`17 MAR 2023`, `UN MAR 2023` on 7 in 100, `UN UNK 2023` on 4 in 100."""
    share = moment.microsecond % 100
    month = _UPPER[moment.month - 1]
    if share < 89:
        return f"{moment.day:02d} {month} {moment.year}"
    if share < 96:
        return f"UN {month} {moment.year}"
    return f"UN UNK {moment.year}"


PARTIAL_SPELLINGS = {
    "fhir_partial": (
        lambda m: _cut(m, "%Y-%m-%d", "%Y-%m", "%Y"),
        _Y4 + "(?:-" + _MM + "(?:-" + _DD + ")?)?", "%Y-%m-%d|%Y-%m|%Y",
    ),
    "medidata_unknown": (
        _medidata,
        "(?:" + _DD + "|UN) (?:" + _words(_UPPER) + "|UNK) " + _Y4, None,
    ),
    "hl7_mixed_precision": (
        lambda m: _cut(m, "%Y%m%d%H%M%S", "%Y%m%d%H%M", "%Y%m%d%H"),
        _Y4 + _MM + _DD + r"(?:[01]\d|2[0-3])(?:[0-5]\d(?:[0-5]\d)?)?",
        "%Y%m%d%H%M%S|%Y%m%d%H%M|%Y%m%d%H",
    ),
    "oracle_seconds_some_omit": (
        lambda m: f"{m.day:02d}-{_UPPER[m.month - 1]}-{m.year} "
        + m.strftime("%H:%M:%S" if m.microsecond % 100 < 80 else "%H:%M"),
        _DD + "-" + _words(_UPPER) + "-" + _Y4 + " " + _T + "(?::[0-5]\\d)?", None,
    ),
}
DECLARED_SPELLINGS = {
    "iso_ordinal": (lambda m: m.strftime("%Y-%j"), _Y4 + r"-\d{3}", "%Y-%j"),
    "julian_seven": (lambda m: m.strftime("%Y%j"), _Y4 + r"\d{3}", "%Y%j"),
}
EVERY_SPELLING = dict(SPELLINGS)
for _name in PARTIAL_SPELLINGS:
    EVERY_SPELLING[_name] = PARTIAL_SPELLINGS[_name]
for _name in DECLARED_SPELLINGS:
    EVERY_SPELLING[_name] = DECLARED_SPELLINGS[_name]

# THE SPELLINGS WHOSE YEAR IS TWO FIGURES, which question Q5 asks about.
TWO_FIGURE_YEARS = ("excel_d_mmm_yy", "oracle_dd_mon_rr", "sas_datetime16")


def cells(name: str, rows: int = ROWS, seed: int = 50003) -> "list[str]":
    """The cells of one named spelling."""
    writer = EVERY_SPELLING[name][0]
    return [writer(moment) for moment in moments(rows, seed)]


def written_as_the_source(name: str, cell: str) -> bool:
    """Whether one cell is written exactly in the source's own spelling."""
    return re.fullmatch(EVERY_SPELLING[name][1], cell) is not None


def format_of(name: str) -> "str | None":
    """The `strptime` format a person's own code would read the shape with."""
    return EVERY_SPELLING[name][2]


def parses(cell: str, fmt: "str | None") -> bool:
    """Whether a person's own `strptime` reads one cell (True where it has no directive).

    A format of alternatives, `|` between them (landing R2c's partial
    dates), reads a cell where any one of them does.
    """
    if fmt is None:
        return True
    for one in fmt.split("|"):
        try:
            datetime.datetime.strptime(cell, one)
        except ValueError:
            continue
        return True
    return False
