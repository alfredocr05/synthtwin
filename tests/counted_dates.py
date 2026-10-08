"""The columns landing R4's numbers that are dates are measured on (plan P4-D384).

Seeded, made-up cells and nothing else: every value is drawn from a
`random.Random` seeded by the shape's own name and the seed, so the same
name gives the same cells on every platform and every supported Python.

SIX FAMILIES.

* `SHAPES` -- the fourteen columns of the R4 design's battery, each a
  counting system, the dates its counts name and the way an export spells
  them: Excel serial dates and date-times (`%.15g` clinic slots, six
  figures at the second), the 1904 system, SAS days and seconds, Stata
  milliseconds, Unix seconds and milliseconds, Epic day numbers and
  `*_DATE_REAL` with its contact number, and birth dates as Excel serials,
  signed SAS days and Unix seconds at midnight UTC.
* `RANGES` -- the same writers over events from 1985 to 2025 and births
  from 1920 to 2005 (the R4 design review, item 2).
* `SCENARIOS` -- the same columns carrying what real columns carry: one
  cell keyed a century late or early, two and five keyed a century out
  either way (the review of landing R4, item 6), and one in a hundred
  written `0`, `-1`, or the system's own count for 9999-12-31 or
  1900-01-01 (item 1); `heaped`, a share of one placeholder large
  enough that the ladder publishes it as the column's end (the review of
  landing R4, item 1); and `heaped_pair`, two placeholders heaped at one
  end (its second review, item 3).
* `ORDINARY` -- the chance battery: forty-eight generators of
  measurements and thirteen of codes written as numbers, each drawn with
  its location and scale jittered, and six more the review added -- two
  variable-width identifiers, two clocks counted in seconds and two more
  wide numbers (items 5 and 7) -- and eight the review of landing R4
  added (its item 7): five money and dose columns written to one or two
  figures in Excel's five-figure band, and two lengths of time kept as
  whole days of seconds and milliseconds. A question one of them raises
  that the fixed-width question did not raise already is a NEW question.
* `COARSE` -- dates written as counts with figures no unit of time keeps
  whole: one or two figures of a day, tenths and hundredths of a second,
  and four figures of a day of moments off the minute (the review of
  landing R4, item 2), beside two whose figures a unit does keep.
* `WRITERS` -- the shapes an exporter writes beside the battery's: pandas'
  `45000.0` and `repr`, Python's `repr` of a timestamp taken to the
  microsecond, and an Epic day exported to seventeen significant figures
  (the review of landing R4, items 2, 3 and 5).

What a person reads a column with is `decode`, the counting system's own
rule, written here with `datetime` alone.
"""

import dataclasses
import datetime as dt
import math
import random
import zlib

ROWS = 1000

# THE SYSTEMS, as the person who owns the table would read them: the day
# the count of nought names and how many seconds one count holds.
EPOCHS = {
    "excel-1900": dt.datetime(1899, 12, 30),
    "excel-1904": dt.datetime(1904, 1, 1),
    "days-since-1960": dt.datetime(1960, 1, 1),
    "seconds-since-1960": dt.datetime(1960, 1, 1),
    "milliseconds-since-1960": dt.datetime(1960, 1, 1),
    "seconds-since-1970": dt.datetime(1970, 1, 1),
    "milliseconds-since-1970": dt.datetime(1970, 1, 1),
    "days-since-1840": dt.datetime(1840, 12, 31),
}
UNIT_SECONDS = {
    "excel-1900": 86400,
    "excel-1904": 86400,
    "days-since-1960": 86400,
    "seconds-since-1960": 1,
    "milliseconds-since-1960": 0.001,
    "seconds-since-1970": 1,
    "milliseconds-since-1970": 0.001,
    "days-since-1840": 86400,
}
DAY_SYSTEMS = ("excel-1900", "excel-1904", "days-since-1960", "days-since-1840")

# An emergency department's hours and a clinic's weekdays, Monday first.
_ED_HOURS = (
    2.6, 2.2, 1.9, 1.6, 1.4, 1.4, 1.7, 2.5, 3.8, 5.0, 5.9, 6.2,
    6.1, 5.9, 5.7, 5.6, 5.6, 5.6, 5.5, 5.3, 4.9, 4.4, 3.8, 3.2,
)
_CLINIC = (1.2, 1.15, 1.1, 1.1, 1.0, 0.45, 0.4)


def _weighted_day(draw: random.Random, first: dt.date, last: dt.date, weights: "tuple[float, ...]") -> dt.date:
    span = (last - first).days
    while True:
        day = first + dt.timedelta(days=draw.randrange(span))
        if draw.random() * max(weights) < weights[day.weekday()]:
            return day


def encounter(draw: random.Random, first: dt.date = dt.date(2016, 1, 1), last: dt.date = dt.date(2026, 1, 1)) -> dt.datetime:
    """A clinic's encounter day, its weekdays weighted."""
    return dt.datetime.combine(_weighted_day(draw, first, last, _CLINIC), dt.time())


def birth(draw: random.Random, first: dt.date = dt.date(1930, 1, 1), last: dt.date = dt.date(2005, 1, 1)) -> dt.datetime:
    """A birth date, uniform over the span."""
    return dt.datetime.combine(first + dt.timedelta(days=draw.randrange((last - first).days)), dt.time())


def arrival(draw: random.Random, first: dt.date = dt.date(2016, 1, 1), last: dt.date = dt.date(2026, 1, 1), milliseconds: bool = False) -> dt.datetime:
    """An emergency arrival at a whole second (or millisecond), its hours weighted."""
    day = first + dt.timedelta(days=draw.randrange((last - first).days))
    hour = draw.choices(range(24), weights=_ED_HOURS)[0]
    micro = draw.randrange(1000) * 1000 if milliseconds else 0
    return dt.datetime(day.year, day.month, day.day, hour, draw.randrange(60), draw.randrange(60), micro)


def slot(draw: random.Random, first: dt.date = dt.date(2016, 1, 1), last: dt.date = dt.date(2026, 1, 1)) -> dt.datetime:
    """A clinic slot on a fifteen-minute grid, weekdays only, 08:00 to 17:00."""
    day = _weighted_day(draw, first, last, (1, 1, 1, 1, 1, 0.001, 0.001))
    quarter = draw.randrange(8 * 4, 17 * 4)
    return dt.datetime(day.year, day.month, day.day, quarter // 4, (quarter % 4) * 15)


def count_of(system: str, moment: dt.datetime) -> float:
    """The count a system writes for a moment, as a binary64 (an exporter's own arithmetic)."""
    delta = moment - EPOCHS[system]
    micro = delta.days * 86400 * 10**6 + delta.seconds * 10**6 + delta.microseconds
    if system in DAY_SYSTEMS:
        return micro / (86400 * 10**6)
    if system.startswith("seconds"):
        return micro / 10**6
    return micro / 10**3


def whole(system: str) -> "callable":
    return lambda moment: str(int(round(count_of(system, moment))))


def g15(system: str) -> "callable":
    return lambda moment: "%.15g" % count_of(system, moment)


def six_stripped(system: str) -> "callable":
    return lambda moment: f"{count_of(system, moment):.6f}".rstrip("0").rstrip(".")


@dataclasses.dataclass(frozen=True)
class Shape:
    """One column of the battery: its system, its dates and how they are written."""

    name: str
    system: str
    kind: str
    truth: "callable"
    write: "callable"
    note: str


SHAPES = (
    Shape("xl_date", "excel-1900", "date", encounter, whole("excel-1900"),
          "Excel 1900 serial dates, encounters with a weekday pattern"),
    Shape("xl_dt15g", "excel-1900", "datetime", slot, g15("excel-1900"),
          "Excel 1900 serial date-times, clinic slots on a 15-minute grid, %.15g"),
    Shape("xl_dt6", "excel-1900", "datetime", arrival, six_stripped("excel-1900"),
          "Excel 1900 serial date-times, arrivals at whole seconds, six figures trimmed"),
    Shape("xl1904_date", "excel-1904", "date", encounter, whole("excel-1904"),
          "Excel 1904 serial dates, encounters"),
    Shape("sas_days", "days-since-1960", "date", encounter, whole("days-since-1960"),
          "SAS and Stata days since 1960, encounters"),
    Shape("sas_secs", "seconds-since-1960", "datetime", arrival, whole("seconds-since-1960"),
          "SAS date-time seconds since 1960, arrivals"),
    Shape("stata_ms", "milliseconds-since-1960", "datetime", arrival, whole("milliseconds-since-1960"),
          "Stata %tc milliseconds since 1960, arrivals at whole seconds"),
    Shape("unix_s", "seconds-since-1970", "datetime", arrival, whole("seconds-since-1970"),
          "Unix seconds, arrivals"),
    Shape("unix_ms", "milliseconds-since-1970", "datetime",
          lambda draw: arrival(draw, milliseconds=True), whole("milliseconds-since-1970"),
          "Unix milliseconds, arrivals, the thousandths kept"),
    Shape("epic_dte", "days-since-1840", "date", encounter, whole("days-since-1840"),
          "Epic day numbers, contact dates"),
    Shape("epic_real", "days-since-1840", "date", encounter, whole("days-since-1840"),
          "Epic *_DATE_REAL: a day and a contact number after the point"),
    Shape("xl_birth", "excel-1900", "date", birth, whole("excel-1900"),
          "Excel 1900 serial birth dates, 1930 to 2005"),
    Shape("sas_birth", "days-since-1960", "date", birth, whole("days-since-1960"),
          "SAS days, birth dates 1930 to 2005, signed"),
    Shape("unix_s_birth", "seconds-since-1970", "date", birth, whole("seconds-since-1970"),
          "Unix seconds at midnight UTC, birth dates 1930 to 2005, signed"),
)
BY_NAME = {shape.name: shape for shape in SHAPES}
# The one shape question Q3 does not reach: signed SAS days of birth,
# written with a varying number of figures -- reached by `--date-count`.
NOT_ASKED = ("sas_birth",)


def _draw(name: str, seed: int) -> random.Random:
    return random.Random(zlib.crc32(name.encode("utf-8")) + seed)


def _epic_contacts(seed: int) -> "callable":
    contact = random.Random(7 + seed)
    return lambda: contact.choices((0, 1, 2), weights=(85, 12, 3))[0]


def cells(shape: Shape, rows: int = ROWS, seed: int = 0) -> "tuple[list[str], list[dt.datetime]]":
    """A shape's cells as the export writes them, and the moments they name."""
    draw = _draw(shape.name, seed)
    truth = [shape.truth(draw) for _ in range(rows)]
    if shape.name == "epic_real":
        pick = _epic_contacts(seed)
        written = []
        for moment in truth:
            day = int(count_of(shape.system, moment))
            contact = pick()
            written += [f"{day}" if contact == 0 else f"{day}.{contact:02d}".rstrip("0")]
        return written, truth
    return [shape.write(moment) for moment in truth], truth


# THE TWO RANGES THE REVIEW ADDED: events from 1985 and births from 1920.
RANGES = {
    "events_1985": (dt.date(1985, 1, 1), dt.date(2025, 12, 31)),
    "births_1920": (dt.date(1920, 1, 1), dt.date(2005, 12, 31)),
}


def ranged(shape: Shape, name: str, rows: int = ROWS, seed: int = 0) -> "list[str]":
    """The shape's writer over one of `RANGES`, at a clock where the shape carries one."""
    first, last = RANGES[name]
    draw = _draw(f"{shape.name}:{name}", seed)
    moments: "list[dt.datetime]" = []
    for _ in range(rows):
        day = first + dt.timedelta(days=draw.randrange((last - first).days))
        if shape.kind == "datetime":
            moments += [dt.datetime(day.year, day.month, day.day, draw.randrange(24), draw.randrange(60), draw.randrange(60))]
        else:
            moments += [dt.datetime(day.year, day.month, day.day)]
    if shape.name == "epic_real":
        return [str(int(count_of(shape.system, moment))) for moment in moments]
    return [shape.write(moment) for moment in moments]


SCENARIOS = (
    "clean",
    "typo_future_1",
    "typo_past_1",
    "zero_1pct",
    "hi_sentinel_1pct",
    "lo_sentinel_1pct",
    "minus1_1pct",
    "typos_2",
    "typos_5",
)

# THE PLACEHOLDERS A HEAP IS MADE OF (`heaped`), each a cell a system writes
# where no date was given.
PLACEHOLDERS = ("zero", "minus1", "hi_sentinel", "lo_sentinel")


def _shifted(moment: dt.datetime, years: int) -> dt.datetime:
    try:
        return moment.replace(year=moment.year + years)
    except ValueError:
        return moment.replace(year=moment.year + years, day=28)


def dirty(shape: Shape, written: "list[str]", truth: "list[dt.datetime]", scenario: str, seed: int = 0) -> "list[str]":
    """The shape's cells carrying one scenario's stray values."""
    out = list(written)
    draw = random.Random(seed * 7 + 3)

    def spelled(moment: dt.datetime) -> str:
        if shape.name == "epic_real":
            return str(int(count_of(shape.system, moment)))
        return shape.write(moment)

    if scenario == "typo_future_1":
        place = draw.randrange(len(out))
        out[place] = spelled(_shifted(truth[place], 100))
    elif scenario == "typo_past_1":
        place = draw.randrange(len(out))
        out[place] = spelled(_shifted(truth[place], -100))
    elif scenario in ("typos_2", "typos_5"):
        for place in draw.sample(range(len(out)), int(scenario[-1])):
            out[place] = spelled(_shifted(truth[place], 100 if draw.random() < 0.5 else -100))
    elif scenario != "clean":
        for place in draw.sample(range(len(out)), max(1, len(out) // 100)):
            if scenario == "zero_1pct":
                out[place] = "0"
            elif scenario == "minus1_1pct":
                out[place] = "-1"
            elif scenario == "hi_sentinel_1pct":
                out[place] = spelled(dt.datetime(9999, 12, 31))
            elif scenario == "lo_sentinel_1pct":
                out[place] = spelled(dt.datetime(1900, 1, 1))
    return out


def placeholder(shape: Shape, kind: str) -> str:
    """The cell a shape's system writes for one of `PLACEHOLDERS`."""
    if kind == "zero":
        return "0"
    if kind == "minus1":
        return "-1"
    moment = dt.datetime(9999, 12, 31) if kind == "hi_sentinel" else dt.datetime(1900, 1, 1)
    if shape.name == "epic_real":
        return str(int(count_of(shape.system, moment)))
    return shape.write(moment)


def heaped(shape: Shape, written: "list[str]", kind: str, share: float, seed: int = 0) -> "list[str]":
    """The shape's cells with ``share`` of them one placeholder: a heap the ladder publishes as an end."""
    out = list(written)
    draw = random.Random(2000 + seed)
    for place in draw.sample(range(len(out)), int(round(len(out) * share))):
        out[place] = placeholder(shape, kind)
    return out


# TWO PLACEHOLDERS HEAPED AT ONE END (the second review of landing R4, item
# 3): `0` beside the system's count for 1900-01-01, `-1` beside it, and `0`
# beside `-1`.
PLACEHOLDER_PAIRS = (("zero", "lo_sentinel"), ("minus1", "lo_sentinel"), ("zero", "minus1"))


def heaped_pair(
    shape: Shape, written: "list[str]", kinds: "tuple[str, str]", share: float, seed: int = 0
) -> "list[str]":
    """The shape's cells with ``share`` of them each of two placeholders: two heaps at one end."""
    out = list(written)
    draw = random.Random(3000 + seed)
    many = int(round(len(out) * share))
    places = draw.sample(range(len(out)), 2 * many)
    for place in places[:many]:
        out[place] = placeholder(shape, kinds[0])
    for place in places[many:]:
        out[place] = placeholder(shape, kinds[1])
    return out


# -- the chance battery ------------------------------------------------


def _lognormal(draw: random.Random, median: float, sigma: float) -> float:
    return math.exp(math.log(median) + sigma * draw.gauss(0, 1))


def _clip(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


# name: (kind, maker(draw, jitter) -> one value, figures after the point)
ORDINARY = {
    "age_years": ("measure", lambda r, j: _clip(r.gauss(55 * j, 18), 0, 105), 0),
    "age_months_peds": ("measure", lambda r, j: r.uniform(0, 216 * j), 0),
    "age_days_peds": ("measure", lambda r, j: r.uniform(0, 6570 * j), 0),
    "gest_age_days": ("measure", lambda r, j: r.gauss(273, 14), 0),
    "stay_days": ("measure", lambda r, j: _lognormal(r, 4 * j, 0.8), 0),
    "stay_hours": ("measure", lambda r, j: _lognormal(r, 60 * j, 0.8), 0),
    "ed_stay_minutes": ("measure", lambda r, j: _lognormal(r, 240 * j, 0.6), 0),
    "followup_days": ("measure", lambda r, j: r.uniform(0, 3650 * j), 0),
    "survival_days": ("measure", lambda r, j: _lognormal(r, 900 * j, 1.0), 0),
    "glucose_mgdl": ("measure", lambda r, j: _lognormal(r, 110 * j, 0.35), 0),
    "sodium": ("measure", lambda r, j: r.gauss(139, 3), 0),
    "potassium": ("measure", lambda r, j: r.gauss(4.2, 0.5), 1),
    "creatinine_umol": ("measure", lambda r, j: _lognormal(r, 90 * j, 0.5), 0),
    "hemoglobin_gl": ("measure", lambda r, j: r.gauss(130 * j, 20), 0),
    "platelets_e9": ("measure", lambda r, j: _lognormal(r, 250 * j, 0.35), 0),
    "platelets_per_ul": ("measure", lambda r, j: _lognormal(r, 250000 * j, 0.35), 0),
    "wbc_per_ul": ("measure", lambda r, j: _lognormal(r, 7500 * j, 0.35), 0),
    "cd4_per_ul": ("measure", lambda r, j: _lognormal(r, 500 * j, 0.5), 0),
    "troponin_ngl": ("measure", lambda r, j: _lognormal(r, 10 * j, 1.5), 0),
    "ntprobnp": ("measure", lambda r, j: _lognormal(r, 300 * j, 1.3), 0),
    "crp": ("measure", lambda r, j: _lognormal(r, 5 * j, 1.2), 1),
    "ferritin": ("measure", lambda r, j: _lognormal(r, 150 * j, 0.9), 0),
    "ldh": ("measure", lambda r, j: _lognormal(r, 220 * j, 0.4), 0),
    "alt": ("measure", lambda r, j: _lognormal(r, 25 * j, 0.6), 0),
    "viral_load": ("measure", lambda r, j: _lognormal(r, 20000 * j, 2.0), 0),
    "urine_ml_day": ("measure", lambda r, j: _lognormal(r, 1500 * j, 0.4), 0),
    "cholesterol": ("measure", lambda r, j: r.gauss(190 * j, 40), 0),
    "inr": ("measure", lambda r, j: _lognormal(r, 1.1, 0.3), 2),
    "heart_rate": ("measure", lambda r, j: r.gauss(80, 15), 0),
    "sbp": ("measure", lambda r, j: r.gauss(128, 18), 0),
    "body_mass_kg": ("measure", lambda r, j: _lognormal(r, 78 * j, 0.22), 1),
    "weight_g_adult": ("measure", lambda r, j: _lognormal(r, 78000 * j, 0.22), 0),
    "birth_weight_g": ("measure", lambda r, j: r.gauss(3300 * j, 550), 0),
    "stature_mm": ("measure", lambda r, j: r.gauss(1700 * j, 90), 0),
    "steps_day": ("measure", lambda r, j: _lognormal(r, 7000 * j, 0.5), 0),
    "visits": ("measure", lambda r, j: _lognormal(r, 3 * j, 0.9), 0),
    "beds_occupied": ("measure", lambda r, j: r.gauss(400 * j, 40), 0),
    "monthly_admissions": ("measure", lambda r, j: r.gauss(2500 * j, 300), 0),
    "ward_census_minutes": ("measure", lambda r, j: r.gauss(43200 * j, 3000), 0),
    "annual_ed_visits_site": ("measure", lambda r, j: r.gauss(45000 * j, 6000), 0),
    "dose_units": ("measure", lambda r, j: _lognormal(r, 5000 * j, 0.7), 0),
    "charges_usd": ("measure", lambda r, j: _lognormal(r, 25000 * j, 0.9), 2),
    "costs_usd": ("measure", lambda r, j: _lognormal(r, 12000 * j, 0.8), 2),
    "payments_usd": ("measure", lambda r, j: _lognormal(r, 8000 * j, 1.0), 0),
    "income_usd": ("measure", lambda r, j: _lognormal(r, 55000 * j, 0.6), 0),
    "drg_charges_narrow": ("measure", lambda r, j: _lognormal(r, 45000 * j, 0.15), 2),
    "nurse_salary_narrow": ("measure", lambda r, j: r.gauss(48000 * j, 4000), 0),
    "cost_cents": ("measure", lambda r, j: _lognormal(r, 1200000 * j, 0.8), 0),
    "zip_ohio": ("code", lambda r, j: r.randrange(43001, 46000), 0),
    "zip_georgia": ("code", lambda r, j: r.randrange(30002, 32000), 0),
    "zip_illinois": ("code", lambda r, j: r.randrange(60001, 63000), 0),
    "zip_pennsylvania": ("code", lambda r, j: r.randrange(15001, 19641), 0),
    "zip_california": ("code", lambda r, j: r.randrange(90001, 96163), 0),
    "npi": ("code", lambda r, j: r.randrange(1000000000, 2000000000), 0),
    "csn_10": ("code", lambda r, j: r.randrange(1000000000, 1400000000), 0),
    "record_no_8": ("code", lambda r, j: r.randrange(10000000, 99999999), 0),
    "phone_us": ("code", lambda r, j: r.randrange(2000000000, 9999999999), 0),
    "year": ("code", lambda r, j: r.randrange(1990, 2026), 0),
    "yyyymm": ("code", lambda r, j: 201601 + 100 * r.randrange(10) + r.randrange(12), 0),
    "procedure_code_5": ("code", lambda r, j: r.randrange(10021, 99499), 0),
    "hhmm": ("code", lambda r, j: 100 * r.randrange(24) + r.randrange(60), 0),
    # ...and the six the review added (items 5 and 7): two identifiers of
    # nine and ten figures, two clocks counted in seconds, and two more
    # wide numbers.
    "csn_9to10": ("code", lambda r, j: r.randrange(700_000_000, 1_300_000_000), 0),
    "order_id_9to10": ("code", lambda r, j: r.randrange(900_000_000, 1_100_000_000), 0),
    "sas_time_clinic_s": ("measure", lambda r, j: 34200 + 900 * r.randrange(22), 0),
    "sas_time_or_start_s": ("measure", lambda r, j: r.randrange(7 * 3600, 16 * 3600), 0),
    "accession_10to11": ("code", lambda r, j: r.randrange(2_000_000_000, 12_000_000_000), 0),
    "epoch_like_counter": ("measure", lambda r, j: int(r.gauss(1.2e9 * j, 1e8)), 0),
    # ...and the eight the review of landing R4 added (its item 7): money in
    # cents and a drug's total to one figure inside Excel's five-figure band, and
    # lengths of time kept as whole days of seconds and of milliseconds.
    "salary_cents_45k": ("measure", lambda r, j: r.gauss(45000, 2500), 2),
    "payment_cents_20k": ("measure", lambda r, j: r.gauss(20000, 2000), 2),
    "room_charge_cents_62k": ("measure", lambda r, j: r.gauss(62000, 3000), 2),
    "glucose_area_1dp": ("measure", lambda r, j: r.gauss(16000, 1500), 1),
    "dose_total_1dp": ("measure", lambda r, j: r.gauss(42000, 3000), 1),
    "stay_seconds_whole_days": ("measure", lambda r, j: 86400 * r.randrange(1, 60), 0),
    "gap_milliseconds_whole_days": ("measure", lambda r, j: 86400000 * r.randrange(1, 30), 0),
    "followup_seconds_whole_days": ("measure", lambda r, j: 86400 * r.randrange(1, 300), 0),
}


def jitter(draw: random.Random) -> float:
    return math.exp(draw.uniform(-0.35, 0.35))


def ordinary(name: str, rows: int, draw_number: int) -> "list[str]":
    """One draw of an ordinary column, its location and scale jittered."""
    kind, maker, places = ORDINARY[name]
    draw = random.Random(zlib.crc32(f"{name}:{rows}:{draw_number}".encode("utf-8")))
    scale = jitter(draw)
    out: "list[str]" = []
    for _ in range(rows):
        value = maker(draw, scale)
        out += [str(int(round(value))) if places == 0 else f"{value:.{places}f}"]
    return out


# -- figures no unit keeps, and other writers ---------------------------


def _fraction(draw: random.Random) -> float:
    """An Excel serial of 2023 to 2031 with any time of day."""
    return 45000 + draw.randrange(3000) + draw.random()


COARSE = {
    # name: (system, the cell written for each row, whether a unit keeps
    # every figure). The first five are the review's (item 2).
    "excel_1dp": ("excel-1900", lambda r: f"{_fraction(r):.1f}", False),
    "excel_2dp": ("excel-1900", lambda r: f"{_fraction(r):.2f}", False),
    "unix_s_1dp": ("seconds-since-1970", lambda r: f"{1600000000 + r.randrange(200000000) + r.randrange(10) / 10:.1f}", False),
    "unix_s_2dp": ("seconds-since-1970", lambda r: f"{1600000000 + r.randrange(200000000) + r.randrange(100) / 100:.2f}", False),
    "excel_4dp_off_minute": ("excel-1900", lambda r: f"{_fraction(r):.4f}", False),
    # ...and two a unit keeps: four figures of a day at whole minutes, and
    # five at whole seconds.
    "excel_4dp_minutes": ("excel-1900", lambda r: f"{45000 + r.randrange(3000) + r.randrange(1440) / 1440:.4f}", True),
    "excel_5dp_seconds": ("excel-1900", lambda r: f"{45000 + r.randrange(3000) + r.randrange(86400) / 86400:.5f}", True),
}


def coarse(name: str, rows: int = ROWS, seed: int = 0) -> "list[str]":
    """One `COARSE` column's cells."""
    _system, write, _kept = COARSE[name]
    draw = random.Random(zlib.crc32(f"coarse:{name}".encode("utf-8")) + seed)
    return [write(draw) for _ in range(rows)]


def written_by(writer: str, shape: Shape, rows: int = ROWS, seed: int = 0) -> "list[str]":
    """A shape's moments as another exporter writes them (`WRITERS`).

    `repr_microseconds` is Python's own writing of a timestamp it took to
    the microsecond -- the shape's whole count and a seeded number of
    microseconds -- whose figures are finer than fifteen carry (the
    second pass of the review of landing R4, item 2).
    """
    _cells, truth = cells(shape, rows, seed)
    micro = random.Random(zlib.crc32(f"micro:{shape.name}".encode("utf-8")) + seed)
    out: "list[str]" = []
    for moment in truth:
        exact = count_of(shape.system, moment)
        if writer == "pandas_point_zero":
            out += [f"{int(round(exact))}.0"]
        elif writer == "repr":
            out += [repr(exact)]
        elif writer == "repr_microseconds":
            out += [repr(int(round(exact)) + micro.randrange(10**6) / 10**6)]
        else:
            day = int(exact)
            out += [f"{day + 0.01:.17g}" if moment.day % 7 == 0 else f"{day}"]
    return out


WRITERS = ("pandas_point_zero", "repr", "repr_microseconds", "seventeen_significant")


def decode(system: str, text: str) -> "dt.datetime | None":
    """A cell read the way its owner reads it: the system's epoch plus the count."""
    try:
        value = float(text.replace(",", "."))
    except ValueError:
        return None
    if system == "days-since-1840":
        value = float(int(value))
    if system == "excel-1900" and value < 61:
        return None
    try:
        return EPOCHS[system] + dt.timedelta(seconds=round(value * UNIT_SECONDS[system], 3))
    except OverflowError:
        return None


def weekday_shares(moments: "list[dt.datetime]") -> "list[float]":
    """The share of the moments on each weekday, Monday first."""
    counts = [0] * 7
    for moment in moments:
        counts[moment.weekday()] += 1
    total = max(1, len(moments))
    return [count / total for count in counts]


def tvd(left: "list[float]", right: "list[float]") -> float:
    """The total variation distance between two distributions over the same bins."""
    return sum(abs(a - b) for a, b in zip(left, right)) / 2
