"""Columns of two offsets and of the joint member (landing 3b.7, plan P4-D378).

The battery of the 3b.7 design and its skeptic, kept beside the tests that
read it: clinic and emergency-department moments across both changes of
daylight saving time, two sites at -06:00 and +05:30, an instrument writing
UTC beside a ward at +02:00, three offsets, a -06:00 clinic with one cell in
fifty at +05:30, sixtieth seconds at +05:30, admissions with bare dates
beside moments, every value different, and two columns of the C1 date
battery (seed 77, cases 0 and 551) that missed a withheld count at midnight.
Every cell is made up here; none is a real row. Standard library only.
"""

from __future__ import annotations

import datetime
import random


def _nth_sunday(year: int, month: int, n: int) -> datetime.date:
    day = datetime.date(year, month, 1)
    day += datetime.timedelta(days=(6 - day.weekday()) % 7)
    return day + datetime.timedelta(days=7 * (n - 1))


def _last_sunday(year: int, month: int) -> datetime.date:
    day = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
    return day - datetime.timedelta(days=(day.weekday() - 6) % 7)


def us_central(local: datetime.datetime) -> int:
    """Minutes east of UTC on the US Central clock at this local time."""
    start = _nth_sunday(local.year, 3, 2)
    end = _nth_sunday(local.year, 11, 1)
    return -5 * 60 if start <= local.date() < end else -6 * 60


def eu_central(local: datetime.datetime) -> int:
    """Minutes east of UTC on the central European clock at this local time."""
    start = _last_sunday(local.year, 3)
    end = _last_sunday(local.year, 10)
    return 2 * 60 if start <= local.date() < end else 60


def off_text(minutes: int) -> str:
    sign = "+" if minutes >= 0 else "-"
    whole = abs(minutes)
    return f"{sign}{whole // 60:02d}:{whole % 60:02d}"


HOURS_CLINIC = [0] * 7 + [3, 9, 10, 10, 9, 5, 7, 9, 9, 7, 4, 1] + [0] * 6
HOURS_ED = [3, 2, 2, 1, 1, 1, 2, 3, 5, 6, 7, 7, 7, 7, 6, 6, 6, 6, 6, 5, 5, 4, 4, 3]
HOURS_LAB = [1, 1, 1, 1, 2, 6, 14, 10, 7, 6, 5, 4, 4, 4, 3, 3, 3, 3, 3, 3, 2, 2, 1, 1]
WD_BUSINESS = [10, 10, 10, 10, 10, 0, 0]
WD_ADMIT = [18, 15, 14, 14, 15, 11, 9]
WD_ALL = [1] * 7


def _pick(draw: random.Random, weights: "list[int]") -> int:
    return draw.choices(range(len(weights)), weights=weights)[0]


def _local_moment(
    draw: random.Random,
    start: datetime.date,
    days: int,
    weekdays: "list[int]",
    hours: "list[int]",
    minute_step: int = 1,
    second: bool = True,
) -> datetime.datetime:
    while True:
        day = start + datetime.timedelta(days=draw.randrange(days))
        if draw.random() * max(weekdays) < weekdays[day.weekday()]:
            break
    hour = _pick(draw, hours)
    minute = draw.randrange(0, 60, minute_step)
    seconds = draw.randrange(60) if second else 0
    return datetime.datetime(day.year, day.month, day.day, hour, minute, seconds)


def _stamp(moment: datetime.datetime) -> str:
    return moment.strftime("%Y-%m-%dT%H:%M:%S")


def dst_clinic(n: int, draw: random.Random) -> "list[str]":
    found: "list[str]" = []
    for _ in range(n):
        moment = _local_moment(draw, datetime.date(2023, 1, 2), 364, WD_BUSINESS, HOURS_CLINIC, 5, False)
        found += [_stamp(moment) + off_text(us_central(moment))]
    return found


def dst_ed(n: int, draw: random.Random) -> "list[str]":
    found: "list[str]" = []
    for _ in range(n):
        moment = _local_moment(draw, datetime.date(2023, 1, 2), 364, WD_ALL, HOURS_ED)
        found += [_stamp(moment) + off_text(eu_central(moment))]
    return found


def two_sites(n: int, draw: random.Random) -> "list[str]":
    found: "list[str]" = []
    for _ in range(n):
        moment = _local_moment(draw, datetime.date(2023, 11, 6), 112, WD_ADMIT, HOURS_ED)
        found += [_stamp(moment) + off_text(-6 * 60 if draw.random() < 0.6 else 5 * 60 + 30)]
    return found


def few_off(n: int, draw: random.Random) -> "list[str]":
    found: "list[str]" = []
    for _ in range(n):
        moment = _local_moment(draw, datetime.date(2023, 11, 6), 112, WD_BUSINESS, HOURS_CLINIC, 5, False)
        found += [_stamp(moment) + off_text(5 * 60 + 30 if draw.random() < 0.02 else -6 * 60)]
    return found


def z_plus(n: int, draw: random.Random) -> "list[str]":
    found: "list[str]" = []
    for _ in range(n):
        moment = _local_moment(draw, datetime.date(2023, 5, 1), 140, WD_BUSINESS, HOURS_LAB)
        if draw.random() < 0.7:
            found += [_stamp(moment - datetime.timedelta(hours=2)) + "Z"]
        else:
            found += [_stamp(moment) + "+02:00"]
    return found


def leap_shared(n: int, draw: random.Random) -> "list[str]":
    found: "list[str]" = []
    for _ in range(n - 40):
        moment = _local_moment(draw, datetime.date(2016, 9, 1), 120, WD_ADMIT, HOURS_ED)
        found += [_stamp(moment) + off_text(-6 * 60 if draw.random() < 0.6 else 5 * 60 + 30)]
    found += ["2017-01-01T05:29:60+05:30"] * 40
    draw.shuffle(found)
    return found


def isomix_admit(n: int, draw: random.Random) -> "list[str]":
    found: "list[str]" = []
    for _ in range(n):
        moment = _local_moment(draw, datetime.date(2023, 1, 2), 364, WD_ADMIT, HOURS_ED)
        found += [moment.strftime("%Y-%m-%d") if draw.random() < 0.15 else moment.strftime("%Y-%m-%d %H:%M:%S")]
    return found


def isomix_offsets(n: int, draw: random.Random) -> "list[str]":
    found: "list[str]" = []
    for _ in range(n):
        moment = _local_moment(draw, datetime.date(2023, 1, 2), 364, WD_ADMIT, HOURS_ED)
        if draw.random() < 0.1:
            found += [moment.strftime("%Y-%m-%d")]
        else:
            found += [_stamp(moment) + off_text(eu_central(moment))]
    return found


def clinic_isomix(n: int, draw: random.Random) -> "list[str]":
    found: "list[str]" = []
    for _ in range(n):
        moment = _local_moment(draw, datetime.date(2023, 1, 2), 364, WD_BUSINESS, HOURS_CLINIC, 5, False)
        found += [moment.strftime("%Y-%m-%d") if draw.random() < 0.15 else moment.strftime("%Y-%m-%d %H:%M:%S")]
    return found


def isomix_alldiff_b(n: int, draw: random.Random) -> "list[str]":
    """Item (b) as recorded: a fifth of the rows consecutive ISO dates, the rest ISO stamps over
    the same span, every value different."""
    dates = n // 5
    start = datetime.datetime(2024, 1, 1)
    found = [(start + datetime.timedelta(days=day)).strftime("%Y-%m-%d") for day in range(dates)]
    seconds = draw.sample(range(0, dates * 86400), n - dates)
    found += [(start + datetime.timedelta(seconds=second)).strftime("%Y-%m-%d %H:%M:%S") for second in seconds]
    draw.shuffle(found)
    return found


def isomix_alldiff(n: int, draw: random.Random) -> "list[str]":
    """A fifth of the rows ISO dates over three times as many days, the rest ISO stamps over
    eight years, every value different."""
    dates = n // 5
    start = datetime.date(2015, 1, 1)
    found = [(start + datetime.timedelta(days=day)).isoformat() for day in draw.sample(range(max(3 * dates, 400)), dates)]
    seconds = draw.sample(range(0, 365 * 86400 * 8), n - dates)
    found += [
        (datetime.datetime(2015, 1, 1) + datetime.timedelta(seconds=second)).strftime("%Y-%m-%d %H:%M:%S")
        for second in seconds
    ]
    draw.shuffle(found)
    return found


def consec_hours_off(n: int, draw: random.Random) -> "list[str]":
    """Every value different, one stamp an hour, at +01:00 and +02:00 across a change."""
    start = datetime.datetime(2023, 1, 1)
    found: "list[str]" = []
    for step in range(n):
        moment = start + datetime.timedelta(hours=step)
        found += [_stamp(moment) + off_text(eu_central(moment))]
    draw.shuffle(found)
    return found



# C1's date battery, seed 77, case 0 (naive beside Z and -12:00) and case 551 (+01:00 beside
# +02:00): each value with how many rows wrote it.
C0_CELLS: "tuple[tuple[str, int], ...]" = (
    ("2020-10-29T16:00:00Z", 3),
    ("2020-11-08T20:00:00Z", 16),
    ("2020-10-28T00:45:00Z", 1),
    ("2020-10-25T22:15:00Z", 1),
    ("2020-10-23T12:00:00", 16),
    ("2020-11-09T02:00:00Z", 16),
    ("2020-11-02T14:00:00", 1),
    ("2020-11-14T16:00:00", 16),
    ("2020-10-27T06:00:00Z", 1),
    ("2020-11-01T15:15:00", 2),
    ("2020-10-25T09:45:00Z", 1),
    ("2020-10-24T07:00:00", 1),
    ("2020-10-27T08:15:00Z", 1),
    ("2020-10-27T18:45:00", 2),
    ("2020-10-25T09:45:00-12:00", 3),
    ("2020-10-29T13:00:00-12:00", 2),
    ("2020-11-02T14:00:00-12:00", 2),
    ("2020-10-25T02:30:00Z", 4),
    ("2020-11-01T19:15:00-12:00", 1),
    ("2020-10-29T02:00:00-12:00", 1),
    ("2020-10-29T02:00:00Z", 1),
    ("2020-10-25T04:30:00Z", 2),
    ("2020-10-31T03:45:00", 1),
    ("2020-11-02T14:00:00Z", 1),
    ("2020-10-27T18:45:00-12:00", 1),
    ("2020-10-25T04:30:00-12:00", 2),
    ("2020-10-25T22:15:00", 2),
    ("2020-10-29T13:00:00", 1),
    ("2020-10-26T17:00:00", 2),
    ("2020-10-24T15:00:00", 2),
    ("2020-11-01T03:30:00", 1),
    ("2020-11-02T22:00:00-12:00", 1),
    ("2020-10-28T16:45:00Z", 1),
    ("2020-10-29T02:00:00", 1),
    ("2020-10-24T20:45:00", 1),
    ("2020-11-01T15:15:00-12:00", 1),
    ("2020-11-01T19:15:00Z", 2),
    ("2020-10-30T00:00:00-12:00", 2),
    ("2020-10-26T06:45:00", 1),
    ("2020-10-31T20:00:00Z", 1),
    ("2020-10-31T04:00:00Z", 1),
    ("2020-11-01T15:15:00Z", 1),
    ("2020-10-30T23:15:00", 1),
    ("2020-10-30T00:00:00Z", 2),
    ("2020-11-01T03:30:00Z", 2),
    ("2020-10-30T18:15:00Z", 1),
    ("2020-10-30T18:15:00", 1),
    ("2020-10-26T10:30:00Z", 1),
    ("2020-10-28T16:45:00", 1),
    ("2020-11-02T00:00:00", 1),
    ("2020-10-31T11:45:00Z", 1),
    ("2020-10-25T06:45:00-12:00", 1),
    ("2020-10-27T18:45:00Z", 1),
    ("2020-11-01T02:00:00-12:00", 1),
    ("2020-10-28T16:45:00-12:00", 2),
    ("2020-10-31T03:15:00-12:00", 1),
    ("2020-10-28T00:45:00-12:00", 2),
    ("2020-10-25T22:15:00-12:00", 1),
    ("2020-10-27T08:15:00", 1),
    ("2020-11-01T02:00:00", 1),
    ("2020-10-30T18:15:00-12:00", 1),
    ("2020-10-29T16:00:00-12:00", 1),
    ("2020-10-31T03:15:00Z", 1),
)
C551_CELLS: "tuple[tuple[str, int], ...]" = (
    ("2020-11-06T13:30:00+02:00", 3),
    ("2020-11-07T14:30:00+02:00", 3),
    ("2020-11-05T04:30:00+02:00", 1),
    ("2020-11-04T08:00:00+01:00", 16),
    ("2020-11-21T12:30:00+01:00", 3),
    ("2020-11-20T19:00:00+01:00", 11),
    ("2020-11-05T21:45:00+01:00", 3),
    ("2020-10-28T01:00:00+02:00", 12),
    ("2020-11-06T07:45:00+02:00", 3),
    ("2020-11-08T04:00:00+02:00", 2),
    ("2020-11-07T07:30:00+02:00", 2),
    ("2020-11-06T01:00:00+02:00", 2),
    ("2020-11-05T20:00:00+01:00", 2),
    ("2020-11-06T23:45:00+02:00", 3),
    ("2020-11-05T18:00:00+02:00", 1),
    ("2020-11-06T04:30:00+02:00", 3),
    ("2020-11-08T12:45:00+01:00", 3),
    ("2020-11-05T14:15:00+02:00", 1),
    ("2020-11-08T18:00:00+02:00", 2),
    ("2020-11-05T14:15:00+01:00", 2),
    ("2020-11-07T01:45:00+02:00", 3),
    ("2020-11-08T21:00:00+02:00", 1),
    ("2020-11-06T07:45:00+01:00", 1),
    ("2020-11-07T12:45:00+02:00", 3),
    ("2020-11-05T09:15:00+02:00", 3),
    ("2020-11-07T19:00:00+02:00", 1),
    ("2020-11-14T08:00:00+02:00", 2),
    ("2020-11-07T08:45:00+02:00", 4),
    ("2020-11-08T02:30:00+02:00", 1),
    ("2020-11-07T05:45:00+01:00", 1),
    ("2020-11-08T11:00:00+01:00", 2),
    ("2020-11-08T09:00:00+02:00", 2),
    ("2020-11-05T09:15:00+01:00", 1),
    ("2020-11-06T13:30:00+01:00", 1),
    ("2020-11-06T01:00:00+01:00", 2),
    ("2020-11-08T12:45:00+02:00", 1),
    ("2020-11-05T10:45:00+01:00", 1),
    ("2020-11-05T20:15:00+01:00", 1),
    ("2020-11-05T12:15:00+01:00", 1),
    ("2020-11-08T23:15:00+01:00", 1),
    ("2020-11-07T01:45:00+01:00", 1),
    ("2020-11-08T18:00:00+01:00", 2),
    ("2020-11-06T18:30:00+01:00", 1),
    ("2020-11-06T13:00:00+02:00", 1),
    ("2020-11-06T14:45:00+01:00", 3),
    ("2020-11-07T14:30:00+01:00", 1),
    ("2020-11-05T19:15:00+02:00", 1),
    ("2020-11-08T04:00:00+01:00", 1),
    ("2020-11-07T07:30:00+01:00", 1),
    ("2020-11-07T21:15:00+02:00", 2),
    ("2020-11-07T17:00:00+01:00", 2),
    ("2020-11-08T23:15:00+02:00", 2),
    ("2020-11-08T11:15:00+02:00", 1),
    ("2020-11-05T19:15:00+01:00", 1),
    ("2020-11-06T13:00:00+01:00", 2),
    ("2020-11-05T12:15:00+02:00", 3),
    ("2020-11-07T05:45:00+02:00", 2),
    ("2020-11-06T21:00:00+02:00", 2),
    ("2020-11-05T18:00:00+01:00", 1),
    ("2020-11-07T03:15:00+02:00", 1),
    ("2020-11-06T17:15:00+01:00", 3),
    ("2020-11-05T21:45:00+02:00", 1),
    ("2020-11-07T18:00:00+01:00", 2),
    ("2020-11-08T13:45:00+02:00", 2),
    ("2020-11-07T03:15:00+01:00", 2),
    ("2020-11-07T23:45:00+01:00", 1),
    ("2020-11-05T22:30:00+01:00", 2),
    ("2020-11-07T21:15:00+01:00", 2),
    ("2020-11-07T15:15:00+01:00", 1),
    ("2020-11-07T15:15:00+02:00", 1),
    ("2020-11-05T04:30:00+01:00", 1),
    ("2020-11-05T08:00:00+01:00", 1),
    ("2020-11-05T02:00:00+01:00", 1),
    ("2020-11-08T17:00:00+02:00", 2),
    ("2020-11-07T18:00:00+02:00", 1),
    ("2020-11-08T11:00:00+02:00", 1),
    ("2020-11-07T23:45:00+02:00", 2),
    ("2020-11-05T03:45:00+01:00", 1),
    ("2020-11-07T19:00:00+01:00", 2),
    ("2020-11-08T17:00:00+01:00", 2),
    ("2020-11-08T02:00:00+02:00", 1),
    ("2020-11-05T19:30:00+02:00", 2),
    ("2020-11-06T04:30:00+01:00", 1),
)


def c0(_n: int, _draw: random.Random) -> "list[str]":
    return [value for value, count in C0_CELLS for _ in range(count)]


def c551(_n: int, _draw: random.Random) -> "list[str]":
    return [value for value, count in C551_CELLS for _ in range(count)]


SHAPES = {
    "dst_clinic": dst_clinic,
    "dst_ed": dst_ed,
    "two_sites": two_sites,
    "few_off": few_off,
    "z_plus": z_plus,
    "leap_shared": leap_shared,
    "isomix_admit": isomix_admit,
    "isomix_offsets": isomix_offsets,
    "clinic_isomix": clinic_isomix,
    "isomix_alldiff": isomix_alldiff,
    "isomix_alldiff_b": isomix_alldiff_b,
    "consec_hours_off": consec_hours_off,
    "c0": c0,
    "c551": c551,
}


def build(name: str, n: int) -> "list[str]":
    """The named column at `n` rows, its draw seeded by its name and size."""
    return SHAPES[name](n, random.Random(sum(map(ord, name)) * 7919 + n))
