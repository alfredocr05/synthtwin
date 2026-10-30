"""The written clocks landing T1 reads, as seeded neutral columns (plan P4-D370).

Built at runtime from a seeded generator, as every fixture of this suite
is (plan D13): one calendar year of moments whose hour follows an
emergency-department profile and whose minutes and seconds are uniform.
Each shape is the cells, the `strptime` format the code a person runs on
their own table would use (None where Python has no directive for the
spelling, the dotted markers), and its kind: `stamp` for a date and a
clock in one cell, `clock` for a time of day alone.

THE TWENTY SPELLINGS of the gate and of `K-S3-52`: eleven stamps (Excel's
unpadded hour with and without seconds, padded dates beside an unpadded
hour, the day-first and year-first stamps, and six 12-hour clocks -- two
figures and one, upper and lower case, dotted, with no space, and .NET's
seconds), seven clocks alone, and the two all-midnight exports the T1
design skeptic added (.NET's `12:00:00 AM` and Excel's `0:00`). Two
controls that read before T1, and the shapes the skeptic attacked with
(a mixed hour width, a mixed face, a 12-hour face with no marker, a
24-hour morning, every day 12 or less), stand beside them.
"""

import datetime
import random

ROWS = 1000

_YEAR = [datetime.date(2023, 1, 1) + datetime.timedelta(days=step) for step in range(365)]
_HOURS = (
    2.6, 2.2, 1.9, 1.6, 1.4, 1.4, 1.7, 2.5, 3.8, 5.0, 5.9, 6.2,
    6.1, 5.9, 5.7, 5.6, 5.6, 5.6, 5.5, 5.3, 4.9, 4.4, 3.8, 3.2,
)


def moments(rows: int, seed: int) -> "list[datetime.datetime]":
    """``rows`` seeded moments of 2023."""
    draw = random.Random(seed)
    found: "list[datetime.datetime]" = []
    for _row in range(rows):
        day = draw.choice(_YEAR)
        hour = draw.choices(range(24), weights=_HOURS)[0]
        found += [
            datetime.datetime(
                day.year, day.month, day.day, hour, draw.randrange(60), draw.randrange(60)
            )
        ]
    return found


def _twelve(moment: datetime.datetime) -> int:
    return moment.hour % 12 or 12


def _marker(moment: datetime.datetime, style: str) -> str:
    morning = moment.hour < 12
    return {
        "AM": "AM" if morning else "PM",
        "am": "am" if morning else "pm",
        "a.m.": "a.m." if morning else "p.m.",
    }[style]


# name: (writer, strptime format or None, kind)
SPELLINGS = {
    "excel_us": (lambda m: f"{m.month}/{m.day}/{m.year} {m.hour}:{m.minute:02d}", "%m/%d/%Y %H:%M", "stamp"),
    "excel_us_seconds": (lambda m: f"{m.month}/{m.day}/{m.year} {m.hour}:{m.minute:02d}:{m.second:02d}", "%m/%d/%Y %H:%M:%S", "stamp"),
    "padded_date_one_figure_hour": (lambda m: f"{m.month:02d}/{m.day:02d}/{m.year} {m.hour}:{m.minute:02d}", "%m/%d/%Y %H:%M", "stamp"),
    "day_first_one_figure_hour": (lambda m: f"{m.day}/{m.month}/{m.year} {m.hour}:{m.minute:02d}", "%d/%m/%Y %H:%M", "stamp"),
    "year_first_one_figure_hour": (lambda m: f"{m.year}/{m.month:02d}/{m.day:02d} {m.hour}:{m.minute:02d}", "%Y/%m/%d %H:%M", "stamp"),
    "padded_twelve_hour": (lambda m: f"{m.month:02d}/{m.day:02d}/{m.year} {_twelve(m):02d}:{m.minute:02d} {_marker(m, 'AM')}", "%m/%d/%Y %I:%M %p", "stamp"),
    "excel_twelve_hour": (lambda m: f"{m.month}/{m.day}/{m.year} {_twelve(m)}:{m.minute:02d} {_marker(m, 'AM')}", "%m/%d/%Y %I:%M %p", "stamp"),
    "dotnet_twelve_hour_seconds": (lambda m: f"{m.month}/{m.day}/{m.year} {_twelve(m)}:{m.minute:02d}:{m.second:02d} {_marker(m, 'AM')}", "%m/%d/%Y %I:%M:%S %p", "stamp"),
    "lower_case_twelve_hour": (lambda m: f"{m.month:02d}/{m.day:02d}/{m.year} {_twelve(m):02d}:{m.minute:02d} {_marker(m, 'am')}", "%m/%d/%Y %I:%M %p", "stamp"),
    "dotted_twelve_hour": (lambda m: f"{m.month:02d}/{m.day:02d}/{m.year} {_twelve(m)}:{m.minute:02d} {_marker(m, 'a.m.')}", None, "stamp"),
    "unspaced_twelve_hour": (lambda m: f"{m.month}/{m.day}/{m.year} {_twelve(m)}:{m.minute:02d}{_marker(m, 'AM')}", "%m/%d/%Y %I:%M%p", "stamp"),
    "clock_one_figure_hour": (lambda m: f"{m.hour}:{m.minute:02d}", "%H:%M", "clock"),
    "clock_one_figure_hour_seconds": (lambda m: f"{m.hour}:{m.minute:02d}:{m.second:02d}", "%H:%M:%S", "clock"),
    "clock_padded_twelve_hour": (lambda m: f"{_twelve(m):02d}:{m.minute:02d} {_marker(m, 'AM')}", "%I:%M %p", "clock"),
    "clock_twelve_hour": (lambda m: f"{_twelve(m)}:{m.minute:02d} {_marker(m, 'AM')}", "%I:%M %p", "clock"),
    "clock_twelve_hour_seconds": (lambda m: f"{_twelve(m)}:{m.minute:02d}:{m.second:02d} {_marker(m, 'AM')}", "%I:%M:%S %p", "clock"),
    "clock_lower_case_twelve_hour": (lambda m: f"{_twelve(m)}:{m.minute:02d} {_marker(m, 'am')}", "%I:%M %p", "clock"),
    "clock_dotted_twelve_hour": (lambda m: f"{_twelve(m)}:{m.minute:02d} {_marker(m, 'a.m.')}", None, "clock"),
    "dotnet_date_only": (lambda m: f"{m.month}/{m.day}/{m.year} 12:00:00 AM", "%m/%d/%Y %I:%M:%S %p", "stamp"),
    "excel_date_only": (lambda m: f"{m.month}/{m.day}/{m.year} 0:00", "%m/%d/%Y %H:%M", "stamp"),
}

# Two spellings every reader before T1 read, which must keep their bytes.
CONTROLS = {
    "control_stamp": (lambda m: f"{m.month:02d}/{m.day:02d}/{m.year} {m.hour:02d}:{m.minute:02d}", "%m/%d/%Y %H:%M", "stamp"),
    "control_clock": (lambda m: f"{m.hour:02d}:{m.minute:02d}", "%H:%M", "clock"),
}

# The 12-hour face with no marker (hours 1 to 12), which only a person
# can tell from a 24-hour morning.
UNMARKED = {
    "unmarked_twelve_hour_stamp": (lambda m: f"{m.month}/{m.day}/{m.year} {_twelve(m)}:{m.minute:02d}", "%m/%d/%Y %I:%M", "stamp"),
    "unmarked_twelve_hour_clock": (lambda m: f"{_twelve(m)}:{m.minute:02d}", "%I:%M", "clock"),
}


def cells(name: str, rows: int = ROWS, seed: int = 40001) -> "list[str]":
    """The cells of one named shape."""
    for table in (SPELLINGS, CONTROLS, UNMARKED):
        if name in table:
            writer = table[name][0]
            return [writer(moment) for moment in moments(rows, seed)]
    raise KeyError(name)


def format_of(name: str) -> "str | None":
    """The `strptime` format a person's own code would read the shape with."""
    for table in (SPELLINGS, CONTROLS, UNMARKED):
        if name in table:
            return table[name][1]
    raise KeyError(name)


def kind_of(name: str) -> str:
    """`stamp` or `clock`."""
    for table in (SPELLINGS, CONTROLS, UNMARKED):
        if name in table:
            return table[name][2]
    raise KeyError(name)


def mixed(first: str, second: str, share: float, rows: int = ROWS, seed: int = 777) -> "list[str]":
    """A column writing ``first``'s way on a share of its rows and ``second``'s on the rest."""
    draw = random.Random(seed)
    one = cells(first, rows)
    other = cells(second, rows)
    return [one[place] if draw.random() < share else other[place] for place in range(rows)]


def parses(cell: str, fmt: "str | None") -> bool:
    """Whether a person's own `strptime` reads one cell."""
    if fmt is None:
        return False
    try:
        datetime.datetime.strptime(cell, fmt)
    except ValueError:
        return False
    return True
