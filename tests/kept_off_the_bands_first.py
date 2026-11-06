"""Method G7.15 as lane CZ-H's first repair wrote it (160ea30f), kept for the differential test of its second repair.

Codex's review of the first repair, item 4: each cell was read again for
every escape of every moved value, and again each time the search for a
free place reached farther. The second repair reads each cell once; the
orchestrator's LANE CZ-H RULINGS 5 (2) asks that it write the same cells,
measured against this copy on 2,000 seeded random columns
(`tests/test_zoo_dates_in_disguise.py`). Only the test reads it.
"""

from __future__ import annotations

from synthtwin import date_counts as dc


def first_moving_value(cell: str, number: bool, absent: "frozenset[str]") -> "dc._Value | None":
    """A cell's value where method G7.15 moves it: written by the numeric machinery, no missing value, a count of a date in disguise."""
    _lead, body, _trail = dc._around(cell)
    if not body or not number or cell in absent or body in absent:
        return None
    pieces = dc._number_pieces(body)
    if pieces is None or len(f"{int(pieces[1])}") not in dc._WINDOWS or not dc.counted_figures(body):
        return None
    return pieces[0], int(pieces[1]), pieces[5]


def first_kept_off_the_bands(
    cells: "list[str]", numbers: "list[bool]", absent: "frozenset[str]" = frozenset()
) -> "list[str]":
    """A twin column's cells with no number its numeric machinery wrote inside a band of a date in disguise (method G7.15).

    ``numbers`` says, cell by cell, which the numeric machinery wrote;
    every other cell, a cell spelled as one of ``absent`` (the column's
    missing values) and a cell that is no count of a date in disguise
    (`dc.counted_figures`) is kept as it is. Guarantees: a fixed function of
    the three, the cells in their order; the column keeps its count of
    different values and how many cells hold each; no cell it moves reads
    as a date in disguise (`date_in_disguise`, by `_free_place`). Memory:
    the different values it moves and the cells' values near the places
    they move to, never one entry a cell. Raises TypeError for a cell that
    is not text. No I/O.
    """
    # 1. The different values to move.
    moving: "dict[dc._Value, bool]" = {}
    for place, cell in enumerate(cells):
        found = first_moving_value(cell, numbers[place], absent)
        if found is not None:
            moving[found] = True
    # 2. Where each side escapes to.
    escapes: "dict[tuple[int, int, str, bool], int]" = {}
    for sign, whole, kept in moving:
        for downward in (True, False):
            out = dc._escaped(sign, whole, kept, downward)
            if out is not None:
                escapes[(sign, whole, kept, downward)] = out
    # A value can meet a moved one only at the same sign and figures after
    # the point, and only near an escape of theirs; the cells' values are
    # read that near, and read again four times as far where a place met
    # lies farther out, so the column's other values are never all held.
    in_class: "dict[tuple[int, str], int]" = {}
    for sign, _whole, kept in moving:
        one = (sign, kept)
        in_class[one] = (in_class[one] if one in in_class else 0) + 1
    near: "dict[tuple[int, str], list[int]]" = {}
    for escape_key in escapes:
        one = (escape_key[0], escape_key[2])
        if one not in near:
            near[one] = []
        near[one] += [escapes[escape_key]]
    target: "dict[dc._Value, int]" = {}
    widen = 1
    while moving:
        reach: "dict[tuple[int, str], int]" = {}
        for one in in_class:
            reach[one] = widen * (2 * in_class[one] + 2 * dc._ESCAPE_STEPS_AT_MOST)
        taken = first_taken_near(cells, numbers, absent, moving, near, reach)
        target, farthest = first_placed(moving, escapes, taken)
        inside = True
        for one in farthest:
            if farthest[one] > reach[one]:
                inside = False
        if inside:
            break
        widen = 4 * widen
    # 3. The cells, each moved value in its own spelling.
    written: "list[str]" = []
    for place, cell in enumerate(cells):
        found = first_moving_value(cell, numbers[place], absent) if target else None
        if found is None or found not in target:
            written += [cell]
            continue
        lead, body, trail = dc._around(cell)
        pieces = dc._number_pieces(body)
        if pieces is None:
            written += [cell]
            continue
        figures = f"{target[found]}"
        sign_text = body[:1] if body[:1] in ("-", "+") else ""
        written += [
            lead + sign_text + (dc._grouped(figures) if pieces[2] else figures)
            + (dc.POINT + pieces[3] if pieces[3] else "") + pieces[4] + trail
        ]
    return written


def first_taken_near(
    cells: "list[str]", numbers: "list[bool]", absent: "frozenset[str]", moving: "dict[dc._Value, bool]",
    near: "dict[tuple[int, str], list[int]]", reach: "dict[tuple[int, str], int]",
) -> "dict[dc._Value, bool]":
    """The values of the cells that stay, within a class's reach of one of its escapes: those a moved value must not meet."""
    taken: "dict[dc._Value, bool]" = {}
    for place, cell in enumerate(cells):
        _lead, body, _trail = dc._around(cell)
        if not body:
            continue
        pieces = dc._number_pieces(body)
        if pieces is None:
            continue
        key = (pieces[0], int(pieces[1]), pieces[5])
        if key in moving and first_moving_value(cell, numbers[place], absent) is not None:
            continue
        one = (key[0], key[2])
        if one not in near:
            continue
        for escape in near[one]:
            if abs(key[1] - escape) <= reach[one]:
                taken[key] = True
    return taken


def first_placed(
    moving: "dict[dc._Value, bool]", escapes: "dict[tuple[int, int, str, bool], int]", taken: "dict[dc._Value, bool]",
) -> "tuple[dict[dc._Value, int], dict[tuple[int, str], int]]":
    """Each value, in order of size, at the nearer side's next free place; and how far from its escape each class placed one."""
    following: "dict[tuple[int, str, bool, int], int]" = {}
    target: "dict[dc._Value, int]" = {}
    farthest: "dict[tuple[int, str], int]" = {}
    ordered: "list[tuple[tuple[int, int, str], dc._Value]]" = []
    for key in moving:
        ordered += [(first_ordering(key), key)]
    for _rank, key in sorted(ordered):
        sign, whole, kept = key
        offered: "list[tuple[int, bool, int]]" = []
        for downward in (True, False):
            if (sign, whole, kept, downward) not in escapes:
                continue
            escape = escapes[(sign, whole, kept, downward)]
            side = (sign, kept, downward, escape)
            at = first_free_place(sign, following[side] if side in following else escape, kept, downward, taken)
            if at is not None:
                offered += [(abs(at - whole), not downward, at)]
                following[side] = at
        if not offered:
            continue
        _distance, upward, chosen = min(offered)
        target[key] = chosen
        taken[(sign, chosen, kept)] = True
        escape = escapes[(sign, whole, kept, not upward)]
        following[(sign, kept, not upward, escape)] = chosen + (1 if upward else -1)
        one = (sign, kept)
        farthest[one] = max(farthest[one] if one in farthest else 0, abs(chosen - escape))
    return target, farthest


def first_free_place(sign: int, at: "int | None", kept: str, downward: bool, taken: "dict[dc._Value, bool]") -> "int | None":
    """From a side's next place, the first whole part outward that no cell holds and no band reads, or None.

    No date reading takes it: a plain number outside the bands reads as a
    date only as a stamp of eight, twelve or fourteen figures, and the
    places a value moves to write four, five, eight (`99,999,999` and
    below, never under `31,122,050`, the last stamp of eight figures, as
    a side's next place moves on by one), ten, eleven or thirteen.
    """
    step = -1 if downward else 1
    for _step in range(dc._ESCAPE_STEPS_AT_MOST * 1000):
        if at is None or at < 0:
            return None
        if dc._band_holding(sign, at, kept) is not None:
            at = dc._escaped(sign, at, kept, downward)
            continue
        if (sign, at, kept) not in taken:
            return at
        at = at + step
    return None


def first_ordering(key: "dc._Value") -> "tuple[int, int, str]":
    """A value's place in order of size: the signed whole part, then the figures after the point, read the sign's way."""
    sign, whole, kept = key
    padded = kept + "0" * (dc.VALUE_FIGURES - len(kept))
    if sign > 0:
        return sign * whole, sign, padded
    flipped = ""
    for figure in padded:
        flipped = flipped + f"{9 - int(figure)}"
    return sign * whole, sign, flipped
