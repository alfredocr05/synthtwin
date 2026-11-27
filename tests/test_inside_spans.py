"""Gate file of lane STATS-D: a person's span of dates in the inside record's dates zone.

THE CLASS. A clinic table whose visits stop six years after a person's first (the model-utility battery's clinic
visits, ST7) holds no person past 6.0 years, but the dates zone's writer drew each person's gaps against the
calendar's span alone (twelve years there): the twins held persons followed 9.9 to 10.8 years, and the tenth followed
longest 6.0 to 6.1 years against 5.7 to 5.8. `inside_dates._longest_spans` keeps, in the inside record, the longest
span of each band of the persons' numbers of dates, and the writer shrinks a person's gap positions by the largest share
that fits within it (found by halving), as it now does for the calendar's span.

A cap alone drew the persons it held too short (lane STATS-D's final run): a person's gaps are drawn one by one from
its band's, so its span is a sum of independent gaps, spread wider than the real persons' (who share one window of
follow-up); capped at the longest, the persons of ten visits or more spanned 4.7 years at the median against 5.33,
the eighth visit came at 3.2 years against 3.5, and the mixed model's spread of the persons' slopes per year read 8
per cent high (the clinic visits' family F11 inside 0.66 to 0.77 of its estimates against 0.79 to 0.88 before the
cap). `inside_dates._span_grids` keeps each band's quantile function of its persons' spans (days, or seconds on a
timeline of minutes), and the writer stretches a person's gap positions (`_stretched`, `_fitted_dates`) so it spans
what the band's real persons span at the place its own sum of gaps takes among a reference of its band's sums drawn
on a stream of their own; the persons' own draws stay the writer's (a first form that drew every person again in two
passes moved the visits table's twin past the five checks' distance check, C2).

WHAT IT HOLDS, each red on its mutant (lane STATS-D's report):

* No twin person spans longer than the longest real person of its band (every person's where the band keeps none),
  where before the cap 134 of 1,400 did and the longest was followed 3,820 days against 2,191; and the tenth of
  persons followed longest are followed within a tenth of the real table's (mutant: the spans not read by the writer).
* The persons of ten visits or more span within 3 per cent of the real ones at the median, and the eighth visit comes
  within 3 per cent of the real one on average (mutant: no person's span matched to its band's, the cap alone).
* On a timeline of minutes (medication orders inside five days) the persons span within 5 per cent of the real ones
  at the median (mutant: a span read in whole days there).
* A stretched person keeps the weekday of every date its draws gave it on a timeline of days (the cases table, whose
  starts fall on a weekend 3 per cent of the time) and the time of day of every moment on a timeline of minutes (the
  orders): every row's weekday, and every row's time of day, is the one the same draws give with no span matched
  (mutant: the stretched gaps kept as they fall; the stretch alone moved the cases' starts onto weekends, 4.4 per cent
  of the later ones, and put the orders' share at night out on 8 of 9 twins).

Every table here is drawn by the standard library's `random` from a seed, at run time; nothing is committed.
"""

from __future__ import annotations

import csv
import io

import reliability_tables as T
import utility_tables as U
from synthtwin import inside_dates


def _columns(text: str) -> "dict[str, list[str]]":
    rows = list(csv.reader(io.StringIO(text)))
    return {name: [row[i] for row in rows[1:]] for i, name in enumerate(rows[0])}


def _spans(columns: "dict[str, list[str]]", zone: "dict[str, object]") -> "dict[str, tuple[int, int]]":
    """Each person's number of dates and span of days."""
    entry = zone["columns"]["visit_date"]  # type: ignore[index]
    reading = inside_dates.Reading(entry["reading"]["kind"], entry["reading"]["member"])
    by: "dict[str, list[int]]" = {}
    for person, cell in zip(columns["subject"], columns["visit_date"]):
        moment = inside_dates.moment_of(cell, reading)
        if moment is not None:
            by.setdefault(person, []).append(moment[0])
    return {person: (len(days), max(days) - min(days)) for person, days in by.items()}


def test_no_person_of_the_twin_is_followed_longer_than_the_real_ones() -> None:
    columns = _columns(U.text("ST7", 12000, 2))
    zone = inside_dates.build_zone(columns, "subject")
    real = _spans(columns, zone)
    longest = max(span for _count, span in real.values())
    twin = inside_dates.write_dates(zone, len(columns["subject"]), people=columns["subject"], given=columns, seed=3)
    mine = _spans({"subject": columns["subject"], "visit_date": twin["visit_date"]}, zone)
    assert max(span for _count, span in mine.values()) <= longest, (max(s for _c, s in mine.values()), longest)
    real_sorted = sorted(span for _count, span in real.values())
    mine_sorted = sorted(span for _count, span in mine.values())
    tenth = len(real_sorted) * 9 // 10
    assert abs(mine_sorted[tenth] - real_sorted[tenth]) <= 0.1 * real_sorted[tenth], (
        mine_sorted[tenth], real_sorted[tenth])


def _person_moments(people: "list[str]", cells: "list[str]", reading: "inside_dates.Reading") -> "dict[str, list[int]]":
    """Each person's moments in seconds, in order."""
    by: "dict[str, list[int]]" = {}
    for person, cell in zip(people, cells):
        moment = inside_dates.moment_of(cell, reading)
        if moment is not None:
            by.setdefault(person, []).append(moment[0] * 86400 + max(0, moment[1]) // inside_dates.TICKS)
    return {person: sorted(seconds) for person, seconds in by.items()}


def _median(values: "list[float]") -> float:
    ordered = sorted(values)
    return ordered[len(ordered) // 2]


def test_a_person_spans_what_the_real_persons_of_its_band_span() -> None:
    columns = _columns(U.text("ST7", 20000, 1))
    zone = inside_dates.build_zone(columns, "subject")
    entry = zone["columns"]["visit_date"]  # type: ignore[index]
    reading = inside_dates.Reading(entry["reading"]["kind"], entry["reading"]["member"])
    real = _person_moments(columns["subject"], columns["visit_date"], reading)
    twin_cells = inside_dates.write_dates(zone, len(columns["subject"]), people=columns["subject"], given=columns,
                                          seed=0)["visit_date"]
    twin = _person_moments(columns["subject"], twin_cells, reading)
    many_real = _median([(m[-1] - m[0]) / 86400 for m in real.values() if len(m) >= 10])
    many_twin = _median([(m[-1] - m[0]) / 86400 for m in twin.values() if len(m) >= 10])
    assert abs(many_twin - many_real) <= 0.03 * many_real, (many_twin, many_real)
    eighth_real = [(m[7] - m[0]) / 86400 for m in real.values() if len(m) >= 8]
    eighth_twin = [(m[7] - m[0]) / 86400 for m in twin.values() if len(m) >= 8]
    mean_real, mean_twin = sum(eighth_real) / len(eighth_real), sum(eighth_twin) / len(eighth_twin)
    assert abs(mean_twin - mean_real) <= 0.03 * mean_real, (mean_twin, mean_real)


def test_on_a_timeline_of_minutes_a_person_s_span_is_read_in_seconds() -> None:
    columns = _columns(T.text("T5", 20000, 1))
    person = T.PERSON["T5"]
    zone = inside_dates.build_zone(columns, person)
    name = "ordered_at"
    entry = zone["columns"][name]  # type: ignore[index]
    reading = inside_dates.Reading(entry["reading"]["kind"], entry["reading"]["member"])
    assert zone["timeline"]["scale"] == "minute"  # type: ignore[index]
    real = _person_moments(columns[person], columns[name], reading)
    twin_cells = inside_dates.write_dates(zone, len(columns[person]), people=columns[person], given=columns,
                                          seed=0)[name]
    twin = _person_moments(columns[person], twin_cells, reading)
    real_median = _median([m[-1] - m[0] for m in real.values() if len(m) >= 2])
    twin_median = _median([m[-1] - m[0] for m in twin.values() if len(m) >= 2])
    assert abs(twin_median - real_median) <= 0.05 * real_median, (twin_median / 86400, real_median / 86400)


def _drawn_twice(name: str, column: str) -> "tuple[list[str], list[str], inside_dates.Reading]":
    """A table's timeline drawn by the zone with its persons' spans matched, and by the same draws with none."""
    columns = _columns(T.text(name, 20000, 1))
    person = T.PERSON[name]
    zone = inside_dates.build_zone(columns, person)
    entry = zone["columns"][column]  # type: ignore[index]
    reading = inside_dates.Reading(entry["reading"]["kind"], entry["reading"]["member"])
    matched = inside_dates.write_dates(zone, len(columns[person]), people=columns[person], given=columns, seed=0)
    assert zone["timeline"]["span_grids"]  # type: ignore[index]
    zone["timeline"]["span_grids"] = {}  # type: ignore[index]
    plain = inside_dates.write_dates(zone, len(columns[person]), people=columns[person], given=columns, seed=0)
    return matched[column], plain[column], reading


def test_a_stretched_person_keeps_its_weekdays_and_times_of_day() -> None:
    matched, plain, reading = _drawn_twice("T4", "sched_start")
    moved = [(a, b) for a, b in zip(matched, plain) if a != b]
    assert len(moved) > 1000, len(moved)  # the persons' spans were matched...
    for one, other in moved:  # ...and every date kept its weekday
        day_one, day_other = inside_dates.moment_of(one, reading), inside_dates.moment_of(other, reading)
        assert day_one is not None and day_other is not None
        assert (day_one[0] - day_other[0]) % 7 == 0, (one, other)
    matched, plain, reading = _drawn_twice("T5", "ordered_at")
    moved = [(a, b) for a, b in zip(matched, plain) if a != b]
    assert len(moved) > 100, len(moved)
    for one, other in moved:
        at_one, at_other = inside_dates.moment_of(one, reading), inside_dates.moment_of(other, reading)
        assert at_one is not None and at_other is not None
        assert at_one[1] == at_other[1], (one, other)
