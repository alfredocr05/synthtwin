"""The BRUTE FORCE of the weekday census's certificate (landing 3b.1).

It imports nothing from synthtwin. On tiny bodies -- four to seven cells
over seven to ten days, nought to two rungs, both boundaries body days,
the count of different days EXACT (a reader holding listed tails) -- at a
line of three, it enumerates EVERY table meeting the facts and asks EVERY
set of days of the span:

  a CENSUS-CAUSED PIN is a set whose count, shifted by an exact offset
  `a` in 0 .. line (a count a reader could add from days it holds
  exactly), lies inside 1 .. line - 1 over every table meeting the facts
  and the census, while over every table meeting the facts alone -- the
  census's empty weekdays still empty in both -- it does not.

A census the certificate publishes must have no census-caused pin
(`unsound` otherwise); every witness it returns must be one of the
enumerated tables; every class it certifies must have an enumerated
table holding the line on its witness's day. The menu is written here a
second time, from its statement, so the census asked is the one the
floor alone chooses.

Every function is a function of its arguments; nothing is read or
written.
"""

from __future__ import annotations

import datetime
import itertools
import random

LINE = 3
_EPOCH = datetime.date(1970, 1, 1)


def weekday(day: int) -> int:
    """Monday 0 to Sunday 6 of a day counted from 1970-01-01."""
    return (_EPOCH + datetime.timedelta(days=day)).weekday()


def menu(bins: "list[int]", line: int) -> "tuple[list[tuple[int, int, int]], int]":
    """The census the floor alone offers, and its entry; ([], 0) for none."""
    def fits(count: int) -> bool:
        return count == 0 or count >= line

    if all(fits(count) for count in bins):
        groups: "list[tuple[int, int, int]]" = []
        for day in range(7):
            if bins[day] == 0 and groups and groups[-1][2] == 0 and groups[-1][1] == day - 1:
                groups[-1] = (groups[-1][0], day, 0)
            else:
                groups += [(day, day, bins[day])]
        return groups, 1
    weekend = bins[5] + bins[6]
    if all(fits(count) for count in bins[:5]) and fits(weekend) and weekend > 0:
        groups = []
        for day in range(5):
            if bins[day] == 0 and groups and groups[-1][2] == 0 and groups[-1][1] == day - 1:
                groups[-1] = (groups[-1][0], day, 0)
            else:
                groups += [(day, day, bins[day])]
        return groups + [(5, 6, weekend)], 2
    if sum(bins[:5]) >= line and fits(weekend):
        return [(0, 4, sum(bins[:5])), (5, 6, weekend)], 3
    return [], 0


def instance(draw: random.Random, larger: bool = False) -> "dict | None":
    """One tiny body and its menu census, or None where the menu offers none."""
    span = draw.randint(8, 11) if larger else draw.randint(7, 10)
    base = 738000 + draw.randint(0, 6)
    low, high = base, base + span - 1
    body = draw.randint(6, 9) if larger else draw.randint(4, 7)
    inner = [draw.randint(low, high) for _ in range(body - 2)]
    cells = sorted([low, high] + inner)
    rungs = [
        (rank, cells[rank])
        for rank in sorted(draw.sample(range(1, body - 1), draw.randint(0, min(2, body - 2))))
    ]
    bins = [0] * 7
    for day in cells:
        bins[weekday(day)] += 1
    groups, entry = menu(bins, LINE)
    if not groups:
        return None
    return {
        "cells": cells, "low": low, "high": high, "rungs": rungs,
        "different": len(set(cells)), "groups": groups, "entry": entry,
        "body": body, "span": span,
    }


def _meets(inst: dict, table: "tuple[int, ...]", census: bool) -> bool:
    if table[0] != inst["low"] or table[-1] != inst["high"]:
        return False
    for rank, day in inst["rungs"]:
        before = sum(1 for cell in table if cell < day)
        upto = sum(1 for cell in table if cell <= day)
        if before > rank or upto < rank + 1:
            return False
    if len(set(table)) != inst["different"]:
        return False
    bins = [0] * 7
    for day in table:
        bins[weekday(day)] += 1
    empty = {day for first, last, count in inst["groups"] if count == 0 for day in range(first, last + 1)}
    if any(bins[day] for day in empty):
        return False
    if not census:
        return True
    for first, last, count in inst["groups"]:
        if sum(bins[first:last + 1]) != count:
            return False
    if inst["entry"] == 2 and not any(1 <= count <= LINE - 1 for count in bins[5:7]):
        return False
    if inst["entry"] == 3 and not any(1 <= count <= LINE - 1 for count in bins[0:5]):
        return False
    return True


def tables(inst: dict, census: bool) -> "list[tuple[int, ...]]":
    """Every table of the body meeting the facts (and the census, if asked)."""
    days = list(range(inst["low"], inst["high"] + 1))
    return [
        table
        for table in itertools.combinations_with_replacement(days, inst["body"])
        if _meets(inst, table, census)
    ]


def _ranges(inst: dict, found: "list[tuple[int, ...]]") -> "tuple[list[int], list[int]]":
    span = inst["span"]
    least = [10 ** 9] * (1 << span)
    most = [-1] * (1 << span)
    for table in found:
        on = [0] * span
        for day in table:
            on[day - inst["low"]] += 1
        sums = [0] * (1 << span)
        for mask in range(1, 1 << span):
            low_bit = mask & -mask
            sums[mask] = sums[mask ^ low_bit] + on[low_bit.bit_length() - 1]
        for mask in range(1 << span):
            least[mask] = min(least[mask], sums[mask])
            most[mask] = max(most[mask], sums[mask])
    return least, most


def judge(
    inst: dict,
    published: bool,
    witnesses: "list[tuple[int, tuple[tuple[int, int], ...]]]",
) -> dict:
    """The brute force's verdict on one census: counts of each failure.

    `witnesses` are (the witness's day, its table as (day, cells) pairs).
    """
    with_census = tables(inst, True)
    without = tables(inst, False)
    least, most = _ranges(inst, with_census)
    least3, most3 = _ranges(inst, without)
    pins = 0
    for mask in range(1, 1 << inst["span"]):
        for offset in range(LINE + 1):
            inside = 1 <= least[mask] + offset and most[mask] + offset <= LINE - 1
            inside3 = 1 <= least3[mask] + offset and most3[mask] + offset <= LINE - 1
            if inside and not inside3:
                pins += 1
                break
    verdict = {"unsound": 0, "not_a_table": 0, "unfillable": 0, "pins": pins}
    if not published:
        return verdict
    if pins:
        verdict["unsound"] = 1
    known = set(with_census)
    for day, pairs in witnesses:
        flat: "list[int]" = []
        for place, cells in pairs:
            flat += [place] * cells
        if tuple(sorted(flat)) not in known:
            verdict["not_a_table"] += 1
        if not any(sum(1 for cell in table if cell == day) >= LINE for table in with_census):
            verdict["unfillable"] += 1
    return verdict
