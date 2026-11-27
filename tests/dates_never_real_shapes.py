"""The invented tables of plan P4-D488's measures (lane ID-ROOM3): dates written as counts and as text, the census-withheld shapes, the placeholder table.

Shared by tools/measurements/kpi_dates_never_real.py (K-HZ-38) and tools/measurements/kpi_identifier_room.py
(K-HZ-06's census-withheld leg). Every date is invented: 1,000 patients born 1928 to 2005 at a random time of
day, twenty visits a patient from 2016 on, seed 206; the shapes of the verify of lane ID-ROOM2's repair 2 rebuilt
from their rule. Nothing here reads or writes a file.
"""

import datetime
import random

from synthtwin import date_counts

ROWS, PEOPLE = 20_000, 1_000
VISITS = ROWS // PEOPLE
EPOCHS = {
    "excel-1900": datetime.datetime(1899, 12, 30), "excel-1904": datetime.datetime(1904, 1, 1),
    "seconds-since-1970": datetime.datetime(1970, 1, 1), "milliseconds-since-1970": datetime.datetime(1970, 1, 1),
    "days-since-1960": datetime.datetime(1960, 1, 1), "seconds-since-1960": datetime.datetime(1960, 1, 1),
    "days-since-1970": datetime.datetime(1970, 1, 1), "days-since-1840": datetime.datetime(1840, 12, 31),
}
COUNTED = (
    ("x1900d", "excel-1900", "day"), ("x1900f", "excel-1900", "frac"), ("x1904d", "excel-1904", "day"),
    ("u1970s", "seconds-since-1970", "sec"), ("u1970ms", "milliseconds-since-1970", "ms"),
    ("sas_d", "days-since-1960", "day"), ("sas_dt", "seconds-since-1960", "sec"),
    ("r1970d", "days-since-1970", "day"), ("m1840d", "days-since-1840", "day"),
)
TEXT = (
    ("iso", "%Y-%m-%d"), ("jul7", "%Y%j"), ("jul5", "%y%j"), ("sasdt4", "%d%b%Y:%H:%M:%S"),
    ("sasdt2", "%d%b%y:%H:%M:%S"), ("doyclk", "%Y%j%H%M%S"), ("ph9", "%Y-%m-%d"), ("mixlay", "%Y-%m-%d"),
)
MODES = ("U", "A", "N", "H")


def counted_cell(moment: datetime.datetime, member: str, how: str) -> str:
    delta = moment - EPOCHS[member]
    if how == "day":
        return f"{delta.days}"
    if how == "frac":
        return f"{delta.total_seconds() / 86400:.5f}"
    if how == "ms":
        return f"{int(delta.total_seconds()) * 1000}"
    return f"{int(delta.total_seconds())}"


def counted_day(cell: str, member: str) -> "datetime.date | None":
    written = date_counts.counted(member, cell.strip(), date_counts.POINT)
    if written is None:
        return None
    numerator, denominator = date_counts.exact_value(written)
    moment = date_counts.moment_of(member, numerator, denominator, date_counts.SECOND)
    if moment is None:
        return None
    return datetime.date(1970, 1, 1) + datetime.timedelta(seconds=moment)


def text_days(cell: str, form: str) -> "set[datetime.date]":
    """The days a text names in its form, the census-withheld layout too; a two-figure year in both centuries."""
    core = cell.strip()
    found: "set[datetime.date]" = set()
    forms = [form, "%d-%b-%Y"] if form == "%Y-%m-%d" else [form]
    for one in forms:
        try:
            read = datetime.datetime.strptime(core.title() if "%b" in one else core, one).date()
        except ValueError:
            continue
        found.add(read)
        if "%y" in one:
            for century in (1900, 2000):
                try:
                    found.add(read.replace(year=century + read.year % 100))
                except ValueError:
                    continue
    return found


def people(how_many: int = PEOPLE, visits_each: int = VISITS) -> "tuple[dict, dict, list]":
    """``how_many`` patients' births and ``visits_each`` visits each, and the rows' shuffled order (seed 206)."""
    draw = random.Random(206)
    births: "dict[str, datetime.datetime]" = {}
    visits: "dict[str, list[datetime.datetime]]" = {}
    for person in range(how_many):
        name = f"P{person + 1:05d}"
        day = datetime.date(1928, 1, 1) + datetime.timedelta(days=draw.randrange(78 * 365))
        births[name] = datetime.datetime.combine(
            day, datetime.time(draw.randrange(24), draw.randrange(60), draw.randrange(60)))
        start = datetime.date(2016, 1, 1) + datetime.timedelta(days=draw.randrange(6 * 365))
        seen: "list[datetime.datetime]" = []
        day = start
        for _visit in range(visits_each):
            if day.weekday() == 5 and draw.random() < 0.8:
                day += datetime.timedelta(days=2)
            elif day.weekday() == 6 and draw.random() < 0.9:
                day += datetime.timedelta(days=1)
            if day.month in (7, 8) and draw.random() < 0.3:
                day += datetime.timedelta(days=14)
            seen += [datetime.datetime.combine(
                day, datetime.time(7 + draw.randrange(11), draw.randrange(60), draw.randrange(60)))]
            day += datetime.timedelta(days=1 + int(draw.expovariate(1 / 40)))
        visits[name] = seen
    order = [(name, index) for name in births for index in range(visits_each)]
    draw.shuffle(order)
    return births, visits, order


MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _day(draw: random.Random, low: int, high: int, top: int = 31) -> datetime.date:
    while True:
        found = datetime.date.fromordinal(draw.randint(datetime.date(low, 1, 1).toordinal(),
                                                       datetime.date(high, 12, 31).toordinal()))
        if found.day <= top:
            return found


def _wmy(day: datetime.date, four: bool = True) -> str:
    return f"{day.day:02d}-{MONTHS[day.month - 1]}-{day.year if four else f'{day.year % 100:02d}'}"


def shape_table(name: str) -> "tuple[list[str], list[list[str]], list[str], list[str]]":
    """(header, rows, typed arguments, the persons of the rows) of a census-withheld shape or the placeholder table."""
    draw = random.Random(11)
    if name in ("F3u", "F2u", "F3cu"):
        low, high = {"F3u": (1980, 1985), "F2u": (1928, 1937), "F3cu": (1905, 1925)}[name]
        few: "list[str]" = []
        for _k in range(4):
            day = _day(draw, low, high, 28)
            few += [f"{day.day:02d}-{MONTHS[day.month - 1]}-{day.year}"]
            day = _day(draw, low, high, 9)
            few += [f"{day.day}-{MONTHS[day.month - 1]}-{day.year}"]
            day = _day(draw, low, high, 28)
            few += [f"{day.day:02d} {MONTHS[day.month - 1]} {day.year}"]
        cells = [_wmy(_day(draw, 2000, 2025), False) for _one in range(ROWS - 12)] + few
        draw.shuffle(cells)
        companions = random.Random(3)
        rows = []
        for place, cell in enumerate(cells):
            if name == "F3u":
                rows += [[f"Q{700000 + place}", cell, companions.choice("MF"), f"{100 + companions.randrange(60)}"]]
            else:
                rows += [[f"Q{700000 + place}", cell, "MF"[place % 2], f"{100 + place % 60}"]]
        return ["patient_ref", "dob", "group", "value"], rows, [], [row[0] for row in rows]
    if name in ("P3", "P2"):
        low, high = (1980, 1985) if name == "P3" else (1928, 1937)
        draw = random.Random(5)
        born: "dict[int, str]" = {}
        for person in range(2000):
            if person < 1998:
                born[person] = _wmy(_day(draw, 2000, 2025), False)
            else:
                day = _day(draw, low, high, 9)
                born[person] = (f"{day.day}-{MONTHS[day.month - 1]}-{day.year}" if person == 1998
                                else f"{day.day:02d} {MONTHS[day.month - 1]} {day.year}")
        pairs = [(person, born[person], "MF"[person % 2]) for person in range(2000) for _k in range(10)]
        draw.shuffle(pairs)
        rows = [[f"M{500000 + person * 7}", cell, group, f"V{900000 + place}"]
                for place, (person, cell, group) in enumerate(pairs)]
        return ["person", "dob", "group", "visit_no"], rows, [], [row[0] for row in rows]
    draw = random.Random(7)
    cells = [_day(draw, 1930, 1999).isoformat() for _one in range(ROWS)]
    for place in (5, 5000, 15000):
        cells[place] = "99999"
    rows = [[f"R{300000 + place}", cell, f"{draw.randint(1, 9)}"] for place, cell in enumerate(cells)]
    typed = ["--identifier", "dob"] if name == "PHi" else []
    return ["row_id", "dob", "grade"], rows, typed, [row[0] for row in rows]




# THE REPAIR'S TABLES (lane ID-ROOM3's repair 1): skeptic 1's young births, the statistics check's stray word, the
# forms that find no room, and ordinary record numbers beside them.
ZONED = (("zmon", "%d-%b-%Y %H:%M:%S"), ("zyy", "%m/%d/%y %H:%M"), ("zfrac", "%Y-%m-%d %H:%M:%S.%f"))
NO_ROOM = (("jul7", "%Y%j"), ("sasdt4", "%d%b%Y:%H:%M:%S"), ("sasdt2", "%d%b%y:%H:%M:%S"))


def young_table() -> "tuple[list[str], list[list[str]], list[str]]":
    """(header, rows, persons): births of 1973-04 to 2001-08 written as seconds from 1970, every one nine figures and
    positive, and as seconds with a comma before three figures (skeptic 1's table Z), beside an ordinary column."""
    births, _visits, order = people()
    first = datetime.datetime(1973, 4, 1)
    span = int((datetime.datetime(2001, 8, 31) - first).total_seconds())
    draw = random.Random(19)
    young = {person: first + datetime.timedelta(seconds=draw.randrange(span)) for person in births}
    rows: "list[list[str]]" = []
    for person, _index in order:
        seconds = int((young[person] - EPOCHS["seconds-since-1970"]).total_seconds())
        rows += [[person, f"{seconds}", f"{seconds},{(seconds * 7919) % 1000:03d}", f"{draw.randint(1, 9)}"]]
    return ["person_ref", "birth_ys", "birth_yc", "grade"], rows, [row[0] for row in rows]


def stray_word_table(word: str = "UNK") -> "tuple[list[str], list[list[str]], list[str], list[str]]":
    """(header, rows, the `--date-count` arguments, persons): the nine counting systems' births, one patient's twenty
    cells of each the word (the statistics check's item 1), beside an ordinary column."""
    births, _visits, order = people()
    stray = order[0][0]
    header = ["person_ref"] + [f"birth_{family}" for family, _member, _how in COUNTED] + ["grade"]
    typed: "list[str]" = []
    for family, member, _how in COUNTED:
        typed += ["--date-count", f"birth_{family}", member]
    draw = random.Random(23)
    rows: "list[list[str]]" = []
    for person, _index in order:
        cells = [word if person == stray else counted_cell(births[person], member, how)
                 for _family, member, how in COUNTED]
        rows += [[person] + cells + [f"{draw.randint(1, 9)}"]]
    return header, rows, typed, [row[0] for row in rows]


def zoned_cell(moment: datetime.datetime, form: str) -> str:
    return f"{moment.strftime(form).upper()} {'EDT' if 4 <= moment.month <= 10 else 'EST'}"


def no_room_table() -> "tuple[list[str], list[list[str]], list[str]]":
    """(header, rows, persons): births written in the three forms with a zone word that find no room (a month's word,
    a two-figure year and a six-figure fraction, each with EST or EDT) and in a day of the year and SAS's DATETIME
    of both year widths, beside an ordinary column."""
    births, _visits, order = people()
    draw = random.Random(29)
    rows: "list[list[str]]" = []
    for person, _index in order:
        born = births[person].replace(microsecond=(int(person[1:]) * 7919) % 1_000_000)
        cells = [zoned_cell(born, form) for _family, form in ZONED]
        cells += [born.strftime(form).upper() for _family, form in NO_ROOM]
        rows += [[person] + cells + [f"{draw.randint(1, 9)}"]]
    header = ["person_ref"] + [f"birth_{family}" for family, _form in ZONED + NO_ROOM] + ["grade"]
    return header, rows, [row[0] for row in rows]


def record_number_table() -> "tuple[list[str], list[list[str]], list[str]]":
    """(header, rows, persons): ordinary record numbers no question about dates concerns, each on a patient's rows: a
    member number of seven figures, a case number of twelve to eighteen, a claim number of sixteen; and an encounter
    key a row, numbered one after another from 700000000."""
    births, _visits, order = people()
    draw = random.Random(31)
    member = {person: f"{draw.randrange(1_000_000, 9_999_999)}" for person in births}
    case = {person: f"{draw.randrange(10 ** (width - 1), 10 ** width)}"
            for person, width in zip(births, [12, 13, 14, 16, 17, 18] * len(births))}
    claim = {person: f"{draw.randrange(10 ** 15, 10 ** 16)}" for person in births}
    rows = [[person, member[person], case[person], claim[person], f"{700_000_000 + place}", f"{draw.randint(1, 9)}"]
            for place, (person, _index) in enumerate(order)]
    return ["person_ref", "member_no", "case_no", "claim_no", "encounter_key", "grade"], rows, [row[0] for row in rows]


def stray_figure_table() -> "tuple[list[str], list[list[str]], list[str], list[str]]":
    """(header, rows, the `--date-count` arguments, persons): lane ID-ROOM3's repair 2 (the verify of repair 1, items 1
    and 3): births written as seconds from 1970 beside eleven `00000000`, beside one patient's twenty rows written as
    ISO dates and as the count zero-padded to ten figures; as milliseconds beside one patient's ISO rows; as SAS
    datetimes beside one patient's rows written month first; and as seconds beside two patients' words (`UNK`,
    `UNKNOWN`) and beside three patients' `UNK`; beside an ordinary column."""
    births, _visits, order = people()
    seen: "list[str]" = []
    for person, _index in order:
        if person not in seen:
            seen += [person]
        if len(seen) == 4:
            break
    zeros = {7 + 1811 * one for one in range(11)}
    columns = (
        ("birth_z8", "seconds-since-1970"), ("birth_iso", "seconds-since-1970"), ("birth_pad", "seconds-since-1970"),
        ("birth_msiso", "milliseconds-since-1970"), ("birth_sdtmdy", "seconds-since-1960"),
        ("birth_two", "seconds-since-1970"), ("birth_three", "seconds-since-1970"),
    )
    typed: "list[str]" = []
    for name, member in columns:
        typed += ["--date-count", name, member]
    draw = random.Random(37)
    rows: "list[list[str]]" = []
    for place, (person, _index) in enumerate(order):
        born = births[person]
        seconds = counted_cell(born, "seconds-since-1970", "sec")
        cells = [
            "00000000" if place in zeros else seconds,
            born.date().isoformat() if person == seen[0] else seconds,
            f"{int(seconds):010d}" if person == seen[0] and int(seconds) >= 0 else seconds,
            born.date().isoformat() if person == seen[1] else counted_cell(born, "milliseconds-since-1970", "ms"),
            born.strftime("%m/%d/%Y") if person == seen[2] else counted_cell(born, "seconds-since-1960", "sec"),
            {seen[1]: "UNK", seen[3]: "UNKNOWN"}.get(person, seconds),
            "UNK" if person in seen[:3] else seconds,
        ]
        rows += [[person] + cells + [f"{draw.randint(1, 9)}"]]
    header = ["person_ref"] + [name for name, _member in columns] + ["grade"]
    return header, rows, typed, [row[0] for row in rows]


def epoch_cohort_table() -> "tuple[list[str], list[list[str]], list[str]]":
    """(header, rows, persons): lane ID-ROOM3's repair 2 (the verify of repair 1, item 2): births of one calendar year,
    one a patient -- 1970 written as seconds and as milliseconds from 1970, 1960 as SAS datetimes (the first year of
    their epochs), 1971, 1999 and 2001 as seconds (common years), 2000 as seconds (a leap year) -- beside an ordinary
    column."""
    births, _visits, order = people()
    draw = random.Random(41)
    cohorts = (("birth_1970s", 1970, "seconds-since-1970", "sec"), ("birth_1970ms", 1970, "milliseconds-since-1970", "ms"),
               ("birth_1960sdt", 1960, "seconds-since-1960", "sec"), ("birth_1971s", 1971, "seconds-since-1970", "sec"),
               ("birth_1999s", 1999, "seconds-since-1970", "sec"), ("birth_2001s", 2001, "seconds-since-1970", "sec"),
               ("birth_2000s", 2000, "seconds-since-1970", "sec"))
    born: "dict[str, dict[str, str]]" = {}
    for name, year, member, how in cohorts:
        first = datetime.datetime(year, 1, 1)
        span = int((datetime.datetime(year + 1, 1, 1) - first).total_seconds())
        born[name] = {person: counted_cell(first + datetime.timedelta(seconds=draw.randrange(span)), member, how)
                      for person in births}
    rows = [[person] + [born[name][person] for name, _year, _member, _how in cohorts] + [f"{draw.randint(1, 9)}"]
            for person, _index in order]
    header = ["person_ref"] + [name for name, _year, _member, _how in cohorts] + ["grade"]
    return header, rows, [row[0] for row in rows]


EPOCH_COHORTS = (("birth_1970s", "seconds-since-1970"), ("birth_1970ms", "milliseconds-since-1970"),
                 ("birth_1960sdt", "seconds-since-1960"), ("birth_1971s", "seconds-since-1970"),
                 ("birth_1999s", "seconds-since-1970"), ("birth_2001s", "seconds-since-1970"),
                 ("birth_2000s", "seconds-since-1970"))
STRAY_FIGURES = (("birth_z8", "seconds-since-1970", ""), ("birth_iso", "seconds-since-1970", "%Y-%m-%d"),
                 ("birth_pad", "seconds-since-1970", ""), ("birth_msiso", "milliseconds-since-1970", "%Y-%m-%d"),
                 ("birth_sdtmdy", "seconds-since-1960", "%m/%d/%Y"), ("birth_two", "seconds-since-1970", ""),
                 ("birth_three", "seconds-since-1970", ""))


def fraction_table() -> "tuple[list[str], list[list[str]], list[str]]":
    """(header, rows, persons): lane ID-ROOM3's repair 2 (the verify of repair 1, item 4): births written as seconds
    from 1970 with five and with ten figures after the point and as milliseconds with three, one a patient, beside an
    ordinary column."""
    births, _visits, order = people()
    draw = random.Random(43)
    after = {person: f"{draw.randrange(10 ** 10):010d}" for person in births}
    rows: "list[list[str]]" = []
    for person, _index in order:
        seconds = counted_cell(births[person], "seconds-since-1970", "sec")
        figures = after[person]
        millis = counted_cell(births[person], "milliseconds-since-1970", "ms")
        rows += [[person, f"{seconds}.{figures[:5]}", f"{seconds}.{figures}", f"{millis}.{figures[:3]}",
                  f"{draw.randint(1, 9)}"]]
    return ["person_ref", "birth_sf5", "birth_sf10", "birth_msf3", "grade"], rows, [row[0] for row in rows]


FRACTIONS = (("birth_sf5", "seconds-since-1970"), ("birth_sf10", "seconds-since-1970"),
             ("birth_msf3", "milliseconds-since-1970"))
