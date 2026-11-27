"""THE COUNTING PROCESS: start-stop rows, a treatment that starts during follow-up, an end on the last row (contract 4.6c.14; method G16.19; validation V12.11; lane GRb2-b, plan P4-D491 part b).

NOT IN FORCE, as the whole patient layer: only `patient_layer.describe`
(behind the chain's switch) calls `found_on` and `published`, only
`patient_walk.twin` calls `write`, and only `chain_validation.patient_lines`
calls `lines`. A table where no interval rule holds publishes and writes
exactly what it did before.

THE THREE RULES (contract 4.6c.14 (a) to (c)), read on the patients' rows
and published only where EVERY patient keeps them; a rule one patient
breaks is not published and no count of the patients who break it is
ever written (ruling D8):
- THE INTERVAL RULE (B1): two repeated number columns `(A, B)`, every
  tabled row holding a plain decimal reading of each (one fixed number of
  places), `A` below `B` on every row, and inside every patient, its rows
  sorted by `A`, the first `A` at 0 and each next `A` the previous `B`;
- THE SWITCH RULE (B3): a repeated column of exactly two spellings, held
  on every row, that in `A` order changes at most once a patient, every
  change from the same first spelling to the same second; the patient's
  SWITCH TIME `S` is the `A` of its first row at the second spelling,
  "never" where it holds none;
- THE END-EVENT RULE (B4): a repeated column held on every row whose rows
  but each patient's last hold one spelling, the NONE spelling; the
  patient's END VALUE is its last row's spelling.
The switch and end-event rules are read in the interval rule's `A` order
and published only beside it.

THE PUBLISHED FACTS, each in people under the owner's rule B (contract
4.6c.14 (d) to (f)): the switch time's bands in people (cut at `A`'s own
published rungs, the patients who never switch a band of their own, each
band 0 or at least the floor, the top band's mean as a rounded moment);
and THE HAZARD MOMENTS (B5): for each end value, the patients who end
with it, and the person-time, in each band of time from the origin (cut
at `B`'s own published rungs and merged until every count is 0 or at least
the floor), in each state of the switch, and in each band of each
patient-fixed column of the patient chain (main effects only: no cell of
two patient-level columns). The end of follow-up `T` (B2) and the end
value (B4) are published by these margins in people: the ends in each
band of time are `T`'s bands, the ends of each value are the end value's
levels. No date, no real reading of a row and no person's own interval
is published.

THE WRITER (method G16.19). Each twin patient's history is drawn
forward from the origin: in the first state its ends compete with its
switch (a patient of two rows or more may switch, at a rate a band of the
switch time); after a switch its end is drawn in the second state. The
ends' rates by band of time, state and band of each patient-fixed column,
and the switch's rates, are calibrated on the twin's own patients so the
switches in each band and each margin's rate of ends are the published
ones. A patient's `r - 1` cuts are its switch time where it falls inside
its follow-up and the rest drawn evenly over it; its rows are written as
the consecutive intervals `[0, c1), [c1, c2), ..., [ck, T)`, the switch
column at its second spelling from the switch time on, the end column at
its none spelling but on the last row. So the three rules hold on every
twin patient by construction. Every word is the stream's; the arithmetic
is G16.8's (binary64 in the order written; the logarithm the shared
module's).
"""

import dataclasses
import fractions
import math

from synthtwin import chain_rules, chain_walk, contract, dialect, errors, patient_rules, twinstore

rules = chain_rules
pr = patient_rules

# The origin of the interval rule's `A` (contract 4.6c.14 (a)): numbers from 0.
ORIGIN_ZERO = "zero"
# The far end of the last piece of time (no edge stands beyond it).
_FAR = float("inf")
# The digits of a plain decimal reading, as the interval rule reads `A` and `B` (and the writer writes them).
_DIGITS = "0123456789"
# The places the interval rule reads at most (contract 4.6c.14 (a)).
PLACES_MAX = 6
# Person-time is published to this many significant figures (contract 4.6c.14 (f)).
PERSON_TIME_FIGURES = 3
# The calibration (method G16.19): the patients it reads at most, its outer
# draws and its inner passes of iterative proportional fitting.
CAL_PERSONS = 20000
CAL_ROUNDS = 6
CAL_PASSES = 8
# Four words a patient (the first event or the origin, its choice, the end after a switch, its value), one an extra row.
WORDS_A_PATIENT = 4
# The least share a scaled word may read (a share is strictly inside (0, 1)).
_LEAST_SHARE = 2.0 ** -54


def _get(mapping: object, key: str) -> object:
    if isinstance(mapping, dict) and key in mapping:
        return mapping[key]
    return None


def _whole(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _internal(detail: str) -> errors.ProfileError:
    return errors.ProfileError(
        f"synthtwin internal check: the counting process {detail}. This means a "
        "mistake in synthtwin; please report it. Nothing has been written."
    )


# -- THE RULES, READ ON THE PATIENTS' ROWS (contract 4.6c.14 (a) to (c)) ---------------------


@dataclasses.dataclass(frozen=True)
class HeldCells:
    """A column's cells as described and their exact readings, a tabled row each, held as places in a palette (lane W5-2M).

    The palette holds each different cell with its reading once, in the
    order the rows first hold them (`texts[k]` read as `readings[k]`);
    each row is its pair's place, `width` bytes, little-endian, in
    `places`. A repeated column of 2,000,000 rows was two lists of
    pointers, sixteen bytes a row; held here, one to four. `text_at`,
    `reading_at`, `texts_of` and `readings_of` give back each row's very
    cell and reading. A palette of more than `WHOLE_FROM` pairs whose
    readings are all whole numbers within 64 bits (a date's or a stamp's
    ordinal, a different one nearly every row) holds them in `whole`, nine
    bytes each (a byte that says whether there is one, then the number),
    in place of an exact number object each (about ninety bytes); read
    back, each is the exact number it was (`palette_reading`), and
    `readings` is then empty.
    """

    places: bytes
    width: int
    texts: "tuple[str, ...]"
    readings: "tuple[fractions.Fraction | None, ...]"
    rows: int
    whole: bytes = b""


# A palette of more pairs than this, every reading a whole number, holds its readings as numbers in bytes.
WHOLE_FROM = 4096
_WHOLE_LEAST = -(1 << 63)
_WHOLE_MOST = (1 << 63) - 1


def _put_unsigned(data: bytearray, at: int, width: int, value: int) -> None:
    """Writes the whole number ``value`` (0 to 256 ** width - 1) as ``width`` bytes, low byte first, at ``at``."""
    for place in range(width):
        data[at + place] = (value >> (8 * place)) & 255


def _get_unsigned(data: "bytes | bytearray", at: int, width: int) -> int:
    """The whole number of ``width`` bytes, low byte first, at ``at``."""
    value = 0
    for place in range(width):
        value = value | (data[at + place] << (8 * place))
    return value


def _whole_readings(readings: "list[fractions.Fraction | None]") -> "bytes | None":
    """The readings as nine bytes each where every one is None or a whole exact number within 64 bits, else None.

    Each is a byte that says whether there is one (1) or not (0), then the
    number as its 64-bit two's complement, low byte first.
    """
    out = bytearray(9 * len(readings))
    for at in range(len(readings)):
        value = readings[at]
        if value is None:
            continue
        if not isinstance(value, fractions.Fraction) or value.denominator != 1:
            return None
        if not _WHOLE_LEAST <= value.numerator <= _WHOLE_MOST:
            return None
        out[9 * at] = 1
        _put_unsigned(out, 9 * at + 1, 8, value.numerator & ((1 << 64) - 1))
    return bytes(out)


def palette_reading(cells: "HeldCells", at: int) -> "fractions.Fraction | None":
    """The reading of the palette's ``at``-th pair."""
    if not cells.whole:
        return cells.readings[at]
    if not cells.whole[9 * at]:
        return None
    value = _get_unsigned(cells.whole, 9 * at + 1, 8)
    return fractions.Fraction(value - (1 << 64) if value >> 63 else value)


def palette_readings(cells: "HeldCells") -> "list[fractions.Fraction | None]":
    """Every pair's reading, in the palette's order."""
    return [palette_reading(cells, at) for at in range(len(cells.texts))]


def held_cells(texts: "list[str]", readings: "list[fractions.Fraction | None]") -> HeldCells:
    """The rows' cells and readings (one each a row, the same number of both) held as places in a palette of their pairs."""
    if len(texts) != len(readings):
        raise ValueError("a reading for every cell")
    place_of: "dict[tuple[str, fractions.Fraction | None], int]" = {}
    palette_texts: "list[str]" = []
    palette_readings: "list[fractions.Fraction | None]" = []
    places: "list[int]" = []
    for row in range(len(texts)):
        pair = (texts[row], readings[row])
        if pair not in place_of:
            place_of[pair] = len(palette_texts)
            palette_texts += [texts[row]]
            palette_readings += [readings[row]]
        places += [place_of[pair]]
    width = 1
    while len(palette_texts) > 1 << (8 * width):
        width += 1
    if width == 1:
        packed = bytes(places)
    else:
        wide = bytearray(width * len(places))
        for row in range(len(places)):
            _put_unsigned(wide, width * row, width, places[row])
        packed = bytes(wide)
    whole = _whole_readings(palette_readings) if len(palette_texts) > WHOLE_FROM else None
    if whole is not None:
        return HeldCells(packed, width, tuple(palette_texts), (), len(texts), whole)
    return HeldCells(packed, width, tuple(palette_texts), tuple(palette_readings), len(texts))


def place_at(cells: HeldCells, row: int) -> int:
    """Row ``row``'s place in the palette."""
    if cells.width == 1:
        return cells.places[row]
    return _get_unsigned(cells.places, cells.width * row, cells.width)


def text_at(cells: HeldCells, row: int) -> str:
    """Row ``row``'s cell as described."""
    return cells.texts[place_at(cells, row)]


def reading_at(cells: HeldCells, row: int) -> "fractions.Fraction | None":
    """Row ``row``'s exact reading (None for a cell holding none)."""
    return palette_reading(cells, place_at(cells, row))


def texts_of(cells: HeldCells) -> "list[str]":
    """Every row's cell, in row order."""
    return [cells.texts[place_at(cells, row)] for row in range(cells.rows)]


def readings_of(cells: HeldCells) -> "list[fractions.Fraction | None]":
    """Every row's reading, in row order: each pair's read once, and each row given its pair's."""
    readings = palette_readings(cells)
    return [readings[place_at(cells, row)] for row in range(cells.rows)]


@dataclasses.dataclass(frozen=True)
class RowColumn:
    """What the rules read of one column: its class, role, cells as described and exact readings, a tabled row each (`HeldCells`)."""

    name: str
    kind: str
    role: str
    cells: HeldCells


def row_column(name: str, kind: str, role: str, texts: "list[str]",
               readings: "list[fractions.Fraction | None]") -> RowColumn:
    """A `RowColumn` of the rows' cells and readings (`held_cells`)."""
    return RowColumn(name, kind, role, held_cells(texts, readings))


@dataclasses.dataclass(frozen=True)
class Found:
    """The rules every patient keeps, and each patient's follow-up, switch time and end value (in patient order).

    `start` and `stop` name `A` and `B`, `places` the decimals they are
    written to; `switch` is `(column, first, second)` or None; `end` is
    `(column, none, values)` or None; `follow` each patient's last `B`,
    `switched` its switch time (None for never), `ended` its end value
    ("" where no end rule stands); `order` each patient's rows in `A`
    order (tabled rows).
    """

    start: str
    stop: str
    places: int
    switch: "tuple[str, str, str] | None"
    end: "tuple[str, str, tuple[str, ...]] | None"
    follow: "list[fractions.Fraction]"
    switched: "list[fractions.Fraction | None]"
    ended: "list[str]"
    order: "list[list[int]]"


def _places_of(column: RowColumn) -> "int | None":
    """The one number of places every cell of a number column is written to, or None (contract 4.6c.14 (a))."""
    places: "int | None" = None
    # Read over the palette's pairs, in the order the rows first hold them: every row's pair is one of them, so the
    # rule reads the same (lane W5-2M).
    for at in range(len(column.cells.texts)):
        text = f"{column.cells.texts[at]}"
        value = palette_reading(column.cells, at)
        found = _plain_places(text)
        if value is None or found is None:
            return None
        if places is None:
            places = found
        elif found != places:
            return None
        if places > PLACES_MAX or written(value, places) != text:
            return None
    return places


def _plain_places(text: str) -> "int | None":
    """The places of a plain decimal `-?digits[.digits]`, or None for any other spelling."""
    body = text[1:] if text[:1] == "-" else text
    point = -1
    for at in range(len(body)):
        if body[at] == "." and point < 0:
            point = at
        elif body[at] not in _DIGITS:
            return None
    if not body or point == 0 or point == len(body) - 1:
        return None
    return 0 if point < 0 else len(body) - point - 1


def written(value: fractions.Fraction, places: int) -> str:
    """An exact multiple of `10 ** -places` written as the interval rule reads it: plain decimals, `places` of them."""
    units = value * (10 ** places)
    if units.denominator != 1:
        raise ValueError("a value off the column's grid")
    return units_text(units.numerator, places)


def units_text(units: int, places: int) -> str:
    """A whole number of `10 ** -places` written with `places` decimals (no thousands mark, a point)."""
    sign = "-" if units < 0 else ""
    digits = f"{abs(units):0{places + 1}d}"
    if places == 0:
        return f"{sign}{digits}"
    return f"{sign}{digits[:-places]}.{digits[-places:]}"


def _interval_pair(columns: "list[RowColumn]", patients: "list[list[int]]") -> "tuple[RowColumn, RowColumn, int, list[list[int]]] | None":
    """The first pair `(A, B)` in schema order that every patient keeps as consecutive intervals from 0."""
    numbers: "list[tuple[RowColumn, int]]" = []
    for column in columns:
        if column.kind != pr.CLASS_REPEATED or column.role not in rules.NUMBER_ROLES:
            continue
        places = _places_of(column)
        if places is not None:
            numbers += [(column, places)]
    for first, first_places in numbers:
        first_readings = readings_of(first.cells)
        if any(min(first_readings[row] for row in rows) != 0 for rows in patients if rows):  # type: ignore[type-var]
            continue
        ordered = [_in_start_order(rows, first_readings) for rows in patients]
        del first_readings
        for second, second_places in numbers:
            if second.name == first.name or second_places != first_places:
                continue
            if _keeps_intervals(first, second, ordered):
                return first, second, first_places, ordered
    return None


def _in_start_order(rows: "list[int]", starts: "list[fractions.Fraction | None]") -> "list[int]":
    """A patient's rows sorted by their start (ties by row order); a row with no start reading last, in row order."""
    present: "list[tuple[fractions.Fraction, int]]" = []
    absent: "list[int]" = []
    for row in rows:
        start = starts[row]
        if isinstance(start, fractions.Fraction):
            present += [(start, row)]
        else:
            absent += [row]
    return [row for _start, row in sorted(present)] + absent


def _keeps_intervals(first: RowColumn, second: RowColumn, ordered: "list[list[int]]") -> bool:
    for rows in ordered:
        previous: "fractions.Fraction | None" = None
        for row in rows:
            a = reading_at(first.cells, row)
            b = reading_at(second.cells, row)
            if a is None or b is None or not a < b:
                return False
            if (previous is None and a != 0) or (previous is not None and a != previous):
                return False
            previous = b
    return True


def _two_spellings(column: RowColumn) -> "list[str] | None":
    seen: "list[str]" = []
    # Read over the palette, in the order the rows first hold its cells (lane W5-2M): the same spellings, first
    # met in the same order.
    for cell in column.cells.texts:
        text = f"{cell}"
        if dialect.holds_nothing(text):
            return None
        if text not in seen:
            seen += [text]
            if len(seen) > 2:
                return None
    return seen if len(seen) == 2 else None


def _switch_of(column: RowColumn, ordered: "list[list[int]]", start: RowColumn, floor: int) -> "tuple[str, str, list[fractions.Fraction | None]] | None":
    """A switch rule every patient keeps (B3), its first and second spellings, each patient's switch time."""
    spellings = _two_spellings(column)
    if spellings is None:
        return None
    texts = texts_of(column.cells)
    direction: "tuple[str, str] | None" = None
    changers = 0
    for rows in ordered:
        changes = 0
        for at in range(1, len(rows)):
            before, after = texts[rows[at - 1]], texts[rows[at]]
            if before == after:
                continue
            changes += 1
            if direction is None:
                direction = (before, after)
            elif direction != (before, after):
                return None
        if changes > 1:
            return None
        changers += changes
    if direction is None or changers < floor:
        return None
    first, second = direction
    times: "list[fractions.Fraction | None]" = []
    for rows in ordered:
        at_second = [row for row in rows if texts[row] == second]
        times += [reading_at(start.cells, at_second[0]) if at_second else None]
    holders = {spelling: 0 for spelling in spellings}
    for rows in ordered:
        for spelling in {texts[row] for row in rows}:
            holders[spelling] += 1
    for spelling in holders:
        if holders[spelling] < floor:
            return None
    return first, second, times


def _end_of(column: RowColumn, ordered: "list[list[int]]", floor: int) -> "tuple[str, tuple[str, ...], list[str]] | None":
    """An end-event rule every patient keeps (B4): its none spelling, its end values, each patient's end value."""
    none: "str | None" = None
    texts = texts_of(column.cells)
    for rows in ordered:
        for row in rows[:-1]:
            text = f"{texts[row]}"
            if dialect.holds_nothing(text):
                return None
            if none is None:
                none = text
            elif text != none:
                return None
    if none is None:
        return None
    ended: "list[str]" = []
    held: "dict[str, int]" = {}
    for rows in ordered:
        text = f"{texts[rows[-1]]}"
        if dialect.holds_nothing(text):
            return None
        ended += [text]
        held[text] = held[text] + 1 if text in held else 1
    if len(held) < 2 or any(held[text] < floor for text in held):
        return None
    if sum(1 for rows in ordered if any(texts[row] == none for row in rows)) < floor:
        return None
    return none, tuple(sorted(held)), ended


def found_on(columns: "list[RowColumn]", patients: "list[list[int]]", floor: int) -> "Found | None":
    """The interval rule every patient keeps, with the switch and end-event rules beside it, or None (contract 4.6c.14 (a) to (c)).

    Reads the cells as the row description read them (`columns`, schema
    order) and each patient's tabled rows; publishes nothing itself. A
    fixed function of its arguments; raises nothing.
    """
    pair = _interval_pair(columns, patients)
    if pair is None:
        return None
    first, second, places, ordered = pair
    follow = [reading_at(second.cells, rows[-1]) for rows in ordered]
    if any(value is None for value in follow):
        return None
    switch: "tuple[str, str, str] | None" = None
    switched: "list[fractions.Fraction | None]" = [None for _rows in ordered]
    end: "tuple[str, str, tuple[str, ...]] | None" = None
    ended: "list[str]" = ["" for _rows in ordered]
    roles = roles_of(columns, ordered, first, {first.name, second.name}, floor)
    if roles.switch is not None:
        switch = (roles.switch[0], roles.switch[1][0], roles.switch[1][1])
        switched = roles.switch[1][2]
    if roles.end is not None:
        end = (roles.end[0], roles.end[1][0], roles.end[1][1])
        ended = roles.end[1][2]
    return Found(first.name, second.name, places, switch, end, [value for value in follow if value is not None], switched, ended, ordered)


@dataclasses.dataclass(frozen=True)
class Roles:
    """The switch and end columns chosen for the whole table (each `(name, facts)` or None) and the assignments that tied for it."""

    switch: "tuple[str, tuple[str, str, list[fractions.Fraction | None]]] | None"
    end: "tuple[str, tuple[str, tuple[str, ...], list[str]]] | None"
    tied: int


def roles_of(
    columns: "list[RowColumn]", ordered: "list[list[int]]", start: RowColumn, taken: "set[str]", floor: int,
) -> Roles:
    """THE ROLES ASSIGNED JOINTLY (contract 4.6c.14 (b), (c); repair 2, Codex's item 1), never by column order.

    Every repeated column, and every column the layer leaves ineligible for
    one band alone (an end column at its none value on nearly every row of
    a person-period file; repair 1, item 4), is read by both rules. Of the
    assignments `(switch, end)` of two different columns (either may be
    none), the one with an end and a switch wins, then one with an end
    alone, then a switch alone; among those, the end with more end values;
    a tie is broken by the end column's name, then the switch column's, in
    code-point order, so the choice is a fixed function of the columns'
    names and cells, whatever their order. `tied` counts the assignments
    of the winning rank (1 where it is unique).
    """
    switches: "dict[str, tuple[str, str, list[fractions.Fraction | None]]]" = {}
    ends: "dict[str, tuple[str, tuple[str, ...], list[str]]]" = {}
    for column in columns:
        if column.kind not in (pr.CLASS_REPEATED, pr.CLASS_INELIGIBLE) or column.name in taken:
            continue
        found = _switch_of(column, ordered, start, floor)
        if found is not None:
            switches[column.name] = found
        closing = _end_of(column, ordered, floor)
        if closing is not None:
            ends[column.name] = closing
    best: "tuple[tuple[bool, bool, int], str | None, str | None] | None" = None
    tied = 0
    for end_name in [None, *sorted(ends)]:
        for switch_name in [None, *sorted(switches)]:
            if end_name is not None and end_name == switch_name:
                continue
            if end_name is None and switch_name is None:
                continue
            rank = (end_name is not None, switch_name is not None, len(ends[end_name][1]) if end_name is not None else 0)
            if best is None or rank > best[0]:
                best = (rank, end_name, switch_name)
                tied = 1
            elif rank == best[0]:
                tied += 1
    if best is None:
        return Roles(None, None, 0)
    _rank, end_name, switch_name = best
    return Roles(
        (switch_name, switches[switch_name]) if switch_name is not None else None,
        (end_name, ends[end_name]) if end_name is not None else None,
        tied,
    )


# -- THE PUBLISHED FACTS (contract 4.6c.14 (d) to (f)) ----------------------------------------


def significant(value: fractions.Fraction, figures: int = PERSON_TIME_FIGURES) -> fractions.Fraction:
    """`value` rounded to `figures` significant decimal figures, half to even, exactly (contract 4.6c.14 (f))."""
    if value == 0:
        return fractions.Fraction(0)
    magnitude = 0
    probe = abs(value)
    while probe >= 10:
        probe /= 10
        magnitude += 1
    while probe < 1:
        probe *= 10
        magnitude -= 1
    scale = fractions.Fraction(10) ** (magnitude - figures + 1)
    return round(value / scale) * scale


def _rungs_above_nought(block: "dict[str, object]", ladder: rules.Ladder) -> "list[tuple[fractions.Fraction, object]]":
    """A number column's `L0` band edges above 0, each its published rung (value and as published), rising and distinct."""
    rungs = rules.rung_ladder(block)
    out: "list[tuple[fractions.Fraction, object]]" = []
    if not isinstance(rungs, dict):
        return out
    for band in ladder.l0:
        name = band[0] if band else None
        if not (isinstance(name, tuple) and len(name) == 2 and name[0] is not None):
            continue
        shown = _get(rungs, f"{name[0]}")
        exact = pr.rung_of(block, name[0])
        if exact is None or exact <= 0 or any(exact == known for known, _shown in out):
            continue
        out += [(exact, shown)]
    order = sorted((out[at][0], at) for at in range(len(out)))
    return [out[at] for _exact, at in order]


def _band_of(edges: "list[fractions.Fraction]", value: fractions.Fraction) -> int:
    band = 0
    while band < len(edges) and value >= edges[band]:
        band += 1
    return band


def _merged(counts: "list[list[int]]", floor: int) -> "list[int]":
    """The band edges kept (indices into the candidate edges) so every merged band's counts are 0 or at least the floor, and its total at least the floor.

    `counts[b]` holds one count a value in candidate band `b`. Bands are
    merged from the first upward, a merged band closing once it passes;
    a last band that does not pass joins the merged bands before it, one
    group at a time, until the joined band passes.
    """
    kept: "list[int]" = []
    running: "list[int]" = [0 for _value in counts[0]] if counts else []

    def passes(cells: "list[int]") -> bool:
        return sum(cells) >= floor and all(cell == 0 or cell >= floor for cell in cells)

    for band in range(len(counts)):
        running = [running[at] + counts[band][at] for at in range(len(running))]
        if band + 1 < len(counts) and passes(running):
            kept += [band]
            running = [0 for _value in running]
    # A last band that does not pass joins the bands before it, group by
    # group, until the joined band passes (or one band is left).
    while kept and not passes(running):
        last = kept[-1]
        kept = kept[:-1]
        first = kept[-1] + 1 if kept else 0
        for band in range(first, last + 1):
            running = [running[at] + counts[band][at] for at in range(len(running))]
    return kept


def _switch_entry(
    found: Found, blocks: "dict[str, dict[str, object]]", scales: "dict[str, rules.Ladder]", floor: int,
    late: "tuple[list[fractions.Fraction], list[int], list[int] | None, int | None] | None" = None,
) -> "list[dict[str, object]]":
    """`grain.switches` (contract 4.6c.14 (d)): the switch time's bands in patients, cut at `A`'s rungs, or none where the floor stops them.

    The patients who never switch are a band of their own; every band is
    0 or at least the floor; the top band's mean is a rule-B moment over
    its patients, rounded to one place more than the column's. `late`
    holds the bands of time's edges, the patients ending at or after each,
    where the switch margin publishes ends after the switch of one value
    alone those of them ending with it, and the census's patients of two
    rows or more (None where it publishes no such total): each switch edge
    stands only where `_late_held` lets it (the micro-step, item 1).
    """
    if found.switch is None:
        return []
    candidates = _rungs_above_nought(blocks[found.start], scales[found.start])
    edges = [exact for exact, _shown in candidates]
    counts = [[0] for _band in range(len(edges) + 1)]
    never = 0
    for time in found.switched:
        if time is None:
            never += 1
        else:
            counts[_band_of(edges, time)][0] += 1
    if 0 < never < floor:
        return []
    kept = _merged(counts, floor)
    if late is not None:
        # A dropped edge's band joins the one below; each edge's differences
        # read that edge alone, so one pass is the check repeated to its end.
        kept = [at for at in kept if _late_held(found, candidates[at][0], late, floor)]
    kept_edges = [candidates[at] for at in kept]
    cut = [exact for exact, _shown in kept_edges]
    totals = [0 for _band in range(len(cut) + 1)]
    top_sum = fractions.Fraction(0)
    for time in found.switched:
        if time is not None:
            band = _band_of(cut, time)
            totals[band] += 1
            if band == len(cut):
                top_sum += time
    if any(0 < total < floor for total in totals) or totals[-1] < floor:
        return []
    top_mean = top_sum / totals[-1]
    places = found.places + 1
    entry: "dict[str, object]" = {
        "column": found.switch[0],
        "edges": [shown for _exact, shown in kept_edges],
        "from": found.switch[1],
        "never": never,
        "patients": totals,
        "to": found.switch[2],
        "top_mean": pr.decimal_text(fractions.Fraction(round(top_mean * 10 ** places), 10 ** places)),
    }
    origin = _origin_of(found, never, totals[0], floor)
    if origin is not None:
        entry["origin"] = origin
    return [entry]


def _late_held(found: Found, edge: fractions.Fraction, late: "tuple[list[fractions.Fraction], list[int], list[int] | None, int | None]", floor: int) -> bool:
    """Whether a switch edge may stand beside the bands of time (contract 4.6c.14 (e); the micro-step, item 1, LANE GRb2 RULINGS 15 (1)).

    A switch time is the start of a row, a unit of the grid at least below
    its patient's end, so the patients switching at or after the edge are
    among those ending at or after every time edge at or below it, or
    within one unit above it, and the difference of the two published
    totals, D, is a count of patients; where the switch margin publishes
    ends after the switch of one value alone, every switched patient ends
    with it, and the difference D_v from those ending with it is one too.
    And a switch after the origin needs a row before it, so they are among
    the census's patients of two rows or more. The edge stands only where
    every such difference is 0 or at least the floor. A fixed function of
    its arguments.
    """
    cut, from_edge, from_edge_one, two_rows = late
    unit = fractions.Fraction(1, 10 ** found.places)
    turned = sum(1 for time in found.switched if time is not None and time >= edge)
    if two_rows is not None and (two_rows < turned or 0 < two_rows - turned < floor):
        return False
    for at in range(len(cut)):
        if cut[at] > edge + unit:
            continue
        implied = [from_edge[at] - turned] + ([from_edge_one[at] - turned] if from_edge_one is not None else [])
        if any(count < 0 or 0 < count < floor for count in implied):
            return False
    return True


def _rows_held(found: Found, edge: fractions.Fraction, census_top: int, floor: int) -> bool:
    """Whether a time edge may stand beside the census (contract 4.6c.14 (e); the micro-step, item 1's sibling, LANE GRb2 RULINGS 15 (1)).

    Each row lasts a unit of the grid at least, so a patient of `r` rows
    is followed `r` units at least, and the census's patients of `R` rows
    or more (published for every `R` up to its top edge) are among those
    ending at or after every time edge at or below `R` units: the
    difference of the two published totals is a count of patients. The
    edge stands only where every such difference is 0 or at least the
    floor. A fixed function of its arguments.
    """
    unit = fractions.Fraction(1, 10 ** found.places)
    ending = sum(1 for end in found.follow if end >= edge)
    rows = [len(one) for one in found.order]
    for least in range(2, census_top + 1):
        if edge > least * unit:
            continue
        count = ending - sum(1 for one in rows if one >= least)
        if count < 0 or 0 < count < floor:
            return False
    return True


def _origin_of(found: Found, never: int, first_band: int, floor: int) -> "list[int] | None":
    """`origin` (contract 4.6c.14 (d); repair 2, Codex's item 2): the patients treated FROM THE ORIGIN (switch time 0), of one row and of two rows or more.

    A patient of one row that switches is treated from the origin by the
    rule (its one row starts at 0), and it can be treated no other way.
    Published only where some patient is treated from the origin and
    every count the two imply directly is 0 or at least the floor: the
    two, the one-row patients who never switch (the census publishes the
    one-row patients), the others who never switch, the first band's
    switches from after the origin, every switch from after the origin;
    else left out, those patients standing in the first band as before (a
    stated limit). A fixed function of its arguments.
    """
    one = more = single = 0
    for patient in range(len(found.switched)):
        rows = len(found.order[patient]) if patient < len(found.order) else 0
        single += 1 if rows == 1 else 0
        if found.switched[patient] == 0:
            if rows == 1:
                one += 1
            else:
                more += 1
    if one + more == 0:
        return None
    switched = len(found.switched) - never
    implied = [one, more, single - one, never - (single - one), first_band - one - more, switched - one - more]
    if any(count < 0 or 0 < count < floor for count in implied):
        return None
    return [one, more]


def columns_of(counting: "dict[str, object]") -> "set[str]":
    """The columns the counting process writes: `A`, `B`, the switch column where its rule is published, the end column."""
    out: "set[str]" = set()
    for key, fields in (("intervals", ("start", "stop")), ("switches", ("column",)), ("end_events", ("column",))):
        entries = counting[key] if key in counting else []
        for entry in entries if isinstance(entries, list) else []:
            for field in fields:
                if isinstance(entry, dict) and isinstance(_get(entry, field), str):
                    out |= {f"{entry[field]}"}
    return out


def published(
    found: Found,
    blocks: "dict[str, dict[str, object]]",
    scales: "dict[str, rules.Ladder]",
    hazard_columns: "list[tuple[str, rules.Ladder, tuple[list[int], list[int], list[int]]]]",
    floor: int,
    census_top: int = 0,
) -> "dict[str, object] | None":
    """The four objects of contract 4.6c.14 a description writes into `grain`, or None where the floor stops any of them.

    `scales` holds the row ladder of `A` and of `B`; `hazard_columns` each
    patient-fixed column of the patient chain with its ladder and its
    patients' codes at `L0`, `L1` and `L2`; `census_top` the top edge of
    the census published beside it (0 for none). Every count written is 0
    or at least `floor`, in patients; every person-time is a sum over at
    least `floor` patients, rounded to three significant figures; every
    edge is a rung `A` or `B` already publishes. A fixed function of its
    arguments; raises nothing.
    """
    if found.end is None:
        return None
    patients = len(found.follow)
    values = list(found.end[2])
    value_at = {value: at for at, value in enumerate(values)}
    ends = [value_at[value] for value in found.ended]
    switch_object: "dict[str, object] | None" = None
    # -- the bands of time, cut at `B`'s rungs and merged to the floor, and
    # the switch margin's zeros, BEFORE the switch's bands (the micro-step,
    # item 1: each switch edge is held against them) --
    candidates = _rungs_above_nought(blocks[found.stop], scales[found.stop])
    edges = [exact for exact, _shown in candidates]
    counts = [[0 for _value in values] for _band in range(len(edges) + 1)]
    for patient in range(patients):
        counts[_band_of(edges, found.follow[patient])][ends[patient]] += 1
    kept = _merged(counts, floor)
    if census_top >= 2:
        # A dropped edge's band joins the one below (the micro-step, item 1's sibling).
        kept = [at for at in kept if _rows_held(found, candidates[at][0], census_top, floor)]
    time_edges = [candidates[at] for at in kept]
    cut = [exact for exact, _shown in time_edges]
    bands = len(cut) + 1
    events = [[0 for _band in range(bands)] for _value in values]
    person_time = [fractions.Fraction(0) for _band in range(bands)]
    lows = [fractions.Fraction(0)] + cut
    for patient in range(patients):
        ends_at = found.follow[patient]
        events[ends[patient]][_band_of(cut, ends_at)] += 1
        for band in range(bands):
            high = cut[band] if band < len(cut) else None
            if ends_at <= lows[band]:
                break
            person_time[band] += (ends_at if high is None or ends_at < high else high) - lows[band]
    if any(0 < cell < floor for line in events for cell in line):
        return None
    hazard: "dict[str, object]" = {
        "edges": [shown for _exact, shown in time_edges],
        "events": events,
        "person_time": [pr.decimal_text(significant(one)) for one in person_time],
    }
    margin_object: "dict[str, object] | None" = None
    after = [0 for _value in values]
    if found.switch is not None:
        before = [0 for _value in values]
        time_before = fractions.Fraction(0)
        time_after = fractions.Fraction(0)
        for patient in range(patients):
            ends_at = found.follow[patient]
            time = found.switched[patient]
            if time is not None and time < ends_at:
                after[ends[patient]] += 1
                time_before += time
                time_after += ends_at - time
            else:
                before[ends[patient]] += 1
                time_before += ends_at
        state_counts = before + after
        if all(cell == 0 or cell >= floor for cell in state_counts) and sum(after) >= floor:
            margin_object = {
                "events": [[before[at], after[at]] for at in range(len(values))],
                "person_time": [pr.decimal_text(significant(time_before)), pr.decimal_text(significant(time_after))],
            }
    # Each band of time's patients ending at or after its lower edge, and,
    # where the margin publishes ends after the switch of one value alone,
    # those of them ending with it (the micro-step, item 1).
    alone = [at for at in range(len(values)) if after[at] > 0]
    one_value = alone[0] if margin_object is not None and len(alone) == 1 else None
    from_edge = [sum(events[at][band] for at in range(len(values)) for band in range(edge + 1, bands)) for edge in range(len(cut))]
    from_edge_one = [sum(events[one_value][band] for band in range(edge + 1, bands)) for edge in range(len(cut))] if one_value is not None else None
    two_rows = sum(1 for one in found.order if len(one) >= 2) if census_top >= 2 else None
    switch_entry = _switch_entry(found, blocks, scales, floor, (cut, from_edge, from_edge_one, two_rows))
    if switch_entry:
        switch_object = margin_object
    hazard["switch"] = switch_object
    columns_written: "list[dict[str, object]]" = []
    for name, ladder, codes in hazard_columns:
        for level in range(3):
            width = ladder.counts[level]
            cells = [[0 for _band in range(width)] for _value in values]
            times = [fractions.Fraction(0) for _band in range(width)]
            for patient in range(patients):
                band = codes[level][patient]
                cells[ends[patient]][band] += 1
                times[band] += found.follow[patient]
            people = [sum(cells[at][band] for at in range(len(values))) for band in range(width)]
            if all(cell == 0 or cell >= floor for line in cells for cell in line) and all(one == 0 or one >= floor for one in people):
                entry_written: "dict[str, object]" = {
                    "column": name,
                    "events": cells,
                    "level": rules.LEVELS[level],
                    "person_time": [pr.decimal_text(significant(one)) for one in times],
                }
                # THE SWITCHES IN EACH BAND OF THE COLUMN (contract 4.6c.14
                # (f); repair 1, the statistics check's item 1): where the
                # switch's bands stand, the patients whose switch time stands
                # in each band, published only where every count they imply
                # directly is 0 or at least the floor (`patient_rules.switches_held`: each
                # band's complement, and where the switch margin's zeros make
                # it exact, each band's ends less a state's patients; repair
                # 2); so the writer's switch reads the patient's own bands (a
                # treatment given by indication).
                if switch_entry:
                    turned = [0 for _band in range(width)]
                    for patient in range(patients):
                        if found.switched[patient] is not None:
                            turned[codes[level][patient]] += 1
                    margin = switch_object["events"] if switch_object is not None else None
                    if pr.switches_held(turned, cells, margin if isinstance(margin, list) else None, floor):
                        entry_written["switches"] = turned
                columns_written += [entry_written]
                break
    hazard["columns"] = columns_written
    return {
        "end_events": [{"column": found.end[0], "none": found.end[1], "values": values}],
        "hazard": hazard,
        "intervals": [{"origin": ORIGIN_ZERO, "places": found.places, "start": found.start, "stop": found.stop}],
        "switches": switch_entry,
    }


# -- THE LOADER'S VIEW (contract `PatientGrain`) ------------------------------------------------


def _exact(value: object) -> "fractions.Fraction | None":
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return fractions.Fraction(value)
    if isinstance(value, float):
        return fractions.Fraction(repr(value)) if math.isfinite(value) else None
    if isinstance(value, str):
        return pr.fraction_read(value)
    return None


def exact_edges(edges: "tuple[object, ...] | list[object]") -> "list[fractions.Fraction]":
    """Published edges as exact numbers (a rung as published: a JSON number or a decimal text)."""
    out: "list[fractions.Fraction]" = []
    for edge in edges:
        found = _exact(edge)
        if found is not None:
            out += [found]
    return out


# -- THE WRITER (method G16.19) ------------------------------------------------------------------


def words_needed(grain: contract.PatientGrain, rows: int, patients: int) -> int:
    """The writer's words (G16.19): four a patient and one an extra row where an interval rule stands, else none."""
    if not grain.intervals or grain.hazard is None:
        return 0
    return WORDS_A_PATIENT * patients + max(0, rows - patients)


def _uniform(word: int) -> float:
    """A word read as a share strictly inside (0, 1): its top 53 bits and a half, over 2 ** 53 (exact in binary64)."""
    return ((word >> 11) + 0.5) / 9007199254740992.0


@dataclasses.dataclass
class _Model:
    """Each end value's rates by band of time, its multiplier in each state of the switch and each column band's, and the switch's rate in each of its bands."""

    rate: "list[list[float]]"
    state: "list[list[float]]"
    column: "list[list[list[float]]]"
    switch: "list[float]"
    # The switch's multiplier in each band of each column that publishes its
    # switches (empty for a column that does not; repair 1).
    switch_column: "list[list[float]]" = dataclasses.field(default_factory=list)


@dataclasses.dataclass(frozen=True)
class _Cuts:
    """Where a patient's pieces of time are cut: the hazard's band edges, the switch's band edges, and where switching ends."""

    hazard: "list[float]"
    switch: "list[float]"
    switch_end: float


def _person_factor(model: _Model, value: int, bands: "list[int]") -> float:
    factor = 1.0
    for at in range(len(bands)):
        factor = factor * model.column[value][at][bands[at]]
    return factor


def _switch_factor(model: _Model, bands: "list[int]") -> float:
    """The switch's multiplier of a patient's own column bands: the product over each column that publishes its switches."""
    factor = 1.0
    for at in range(len(model.switch_column)):
        if model.switch_column[at]:
            factor = factor * model.switch_column[at][bands[at]]
    return factor


def _factors(model: _Model, bands: "list[int]") -> "list[float]":
    """A patient's multipliers: each end value's over its column bands, then its switch's."""
    return [_person_factor(model, value, bands) for value in range(len(model.rate))] + [_switch_factor(model, bands)]


def _pieces(cuts: _Cuts, start: float) -> "list[tuple[float, float, int, int]]":
    """The pieces `[a, b)` of time from `start` on, cut at every edge: each with its band of time and its band of the switch (-1 past the switch's end); the last open."""
    edges = sorted({edge for edge in cuts.hazard + cuts.switch + [cuts.switch_end] if start < edge < _FAR})
    out: "list[tuple[float, float, int, int]]" = []
    low = start
    for high in edges + [_FAR]:
        band = 0
        while band < len(cuts.hazard) and low >= cuts.hazard[band]:
            band += 1
        switch_band = -1
        if low < cuts.switch_end:
            switch_band = 0
            while switch_band < len(cuts.switch) and low >= cuts.switch[switch_band]:
                switch_band += 1
        out += [(low, high, band, switch_band)]
        low = high
    return out


def _rates(model: _Model, piece: "tuple[float, float, int, int]", factors: "list[float]", state: int, eligible: bool) -> "list[float]":
    """Each end value's rate in a piece, then the switch's (0 in the second state, for a patient who cannot switch, and past the switch's end).

    `factors` holds each end value's multiplier, then the switch's (1
    where it is not given).
    """
    values = len(model.rate)
    out = [model.rate[value][piece[2]] * model.state[value][state] * factors[value] for value in range(values)]
    switching = model.switch[piece[3]] if state == 0 and eligible and piece[3] >= 0 and model.switch else 0.0
    if switching and len(factors) > values:
        switching = switching * factors[values]
    return out + [switching]


def _next(model: _Model, cuts: _Cuts, factors: "list[float]", state: int, eligible: bool, start: float, share: float) -> "tuple[float, list[float]]":
    """The first event from `start` in a state: the time where the total rate's integral reaches `-ln(share)` (exact inside its piece), and the rates there."""
    target = -chain_walk.natural_log(share)
    held = 0.0
    last: "list[float]" = []
    for piece in _pieces(cuts, start):
        rates = _rates(model, piece, factors, state, eligible)
        total = 0.0
        for rate in rates:
            total = total + rate
        length = piece[1] - piece[0]
        last = rates
        if total > 0.0 and (piece[1] == _FAR or held + total * length >= target):
            return piece[0] + (target - held) / total, rates
        if piece[1] != _FAR:
            held = held + total * length
    return start, last


def _chosen(rates: "list[float]", share: float) -> int:
    """The event a share picks among the rates (each end value, then the switch), in proportion to them."""
    whole = 0.0
    for rate in rates:
        whole = whole + rate
    if whole <= 0.0:
        return 0
    point = share * whole
    running = 0.0
    for at in range(len(rates)):
        running = running + rates[at]
        if point < running:
            return at
    return len(rates) - 1


def _drawn(
    model: _Model, cuts: _Cuts, factors: "list[float]", eligible: bool, shares: "tuple[float, float, float, float]", origin: float = 0.0,
) -> "tuple[float | None, float, int]":
    """One patient's switch time (None where it does not switch), end time and end value, forward from the origin (G16.19).

    TREATED FROM THE ORIGIN (repair 2, Codex's item 2): where the first
    share falls below `origin`, the patient's chance of it, the patient
    switches at time 0 and its end is drawn in the second state from 0
    with the third and fourth shares; else the first share, scaled back to
    (0, 1) over the rest, draws the first state. In the first state the
    patient's ends compete with its switch (where it can switch, its rate
    the switch band's); the first event is drawn by inversion with that
    share and chosen with the second; after a switch, its end is drawn
    from the switch time in the second state with the third and fourth.
    With `origin` 0 every draw is the one it was. Returns `(S, T, value)`.
    """
    values = len(model.rate)
    share = shares[0]
    if origin > 0.0:
        if share < origin:
            end, after = _next(model, cuts, factors, 1, eligible, 0.0, shares[2])
            return 0.0, end, _chosen(after[:values], shares[3])
        share = max((share - origin) / (1.0 - origin), _LEAST_SHARE)
    first, rates = _next(model, cuts, factors, 0, eligible, 0.0, share)
    picked = _chosen(rates, shares[1])
    if picked < values:
        return None, first, picked
    end, after = _next(model, cuts, factors, 1, eligible, first, shares[2])
    return first, end, _chosen(after[:values], shares[3])


def _normalised(model: _Model, value: int) -> None:
    """The fitted multipliers of one end value rescaled, the largest of each set to 1 and the scale moved into its rates (the products unchanged)."""
    moved = 1.0
    for at in range(len(model.column[value])):
        largest = max(model.column[value][at]) if model.column[value][at] else 0.0
        if largest > 0.0:
            model.column[value][at] = [one / largest for one in model.column[value][at]]
            moved = moved * largest
    largest = max(model.state[value])
    if largest > 0.0:
        model.state[value] = [one / largest for one in model.state[value]]
        moved = moved * largest
    model.rate[value] = [one * moved for one in model.rate[value]]


def origin_shares(switch: "contract.SwitchRule | None", r_values: "list[int]") -> "list[float]":
    """Each twin patient's chance of being treated from the origin (G16.19; repair 2, Codex's item 2).

    The published patients of its kind (one row, or two rows or more)
    over the twin's patients of that kind, at most 1; 0 for every patient
    where `origin` is not published (every draw then the one it was).
    """
    if switch is None or len(switch.origin) != 2:
        return [0.0 for _rows in r_values]
    single = sum(1 for rows in r_values if rows == 1)
    several = len(r_values) - single
    one = min(1.0, switch.origin[0] / single) if single else 0.0
    more = min(1.0, switch.origin[1] / several) if several else 0.0
    return [one if rows == 1 else more for rows in r_values]


def time_of(text: object, what: str) -> float:
    """A published time or person-time read as binary64 (G16.19), or the ordinary profile error where it is no decimal number from 0 to 2 ** 53.

    S34 refuses such a description at load (repair 2, Codex's item 8);
    the writer reads every time through here so that no text the loader
    let pass can overflow or poison its arithmetic.
    """
    value = pr.fraction_read(text) if isinstance(text, str) else _exact(text)
    if value is None or value < 0 or value > pr.TIME_MOST:
        raise errors.ProfileError(
            f"synthtwin cannot use this profile: the counting process's {what} reads {text!r}, which is no decimal "
            "number from 0 to 2 ** 53, so its twin cannot be drawn. Describe the table again with synthtwin profile."
        )
    return float(value)


def calibrated(
    hazard: contract.HazardMoments,
    switch_rule: "contract.SwitchRule | None",
    cuts: _Cuts,
    patients: int,
    column_bands: "list[list[int]]",
    eligible: "list[bool]",
    shares: "list[tuple[float, float, float, float]]",
    origin: "list[float] | None" = None,
) -> _Model:
    """The rates, calibrated on the twin's own patients until their expected events meet the published ones (G16.19).

    The patients read are all of them up to `CAL_PERSONS`, else every
    `patients / CAL_PERSONS`-th, the published counts scaled to them. Each
    round draws their histories forward with the round's rates (the same
    words every round) and adds up each piece's time at risk: for the
    ends, by band of time, state and column bands; for the switch, the
    first state's time of the patients who can switch, by band of the
    switch and column bands. The switch's rate in each band is then its
    published switches over that time; where columns publish their
    switches in each band (a treatment given by indication), the switch's
    rates by band and its multipliers by each such column's band are
    fitted by iterative proportional fitting (`CAL_PASSES` passes, each
    multiplier set rescaled so its largest is 1) to the published switches
    of every margin, scaled; the ends' rates are fitted by iterative proportional
    fitting on their exposures (`CAL_PASSES` passes over the bands of
    time, the states and each column in turn, the multipliers of each set
    rescaled so the largest is 1 after each pass) to each margin cell's
    PUBLISHED RATE on the twin's time at risk there (its published ends
    times that time over its published person-time): every patient ends
    once, so a margin's ends alone fix only its end values' shares, never
    its level. After `CAL_ROUNDS` rounds the rates stand. A fixed function
    of the description and the words.
    """
    values = len(hazard.events)
    bands = len(hazard.events[0]) if values else 0
    times = [time_of(one, "person-time") for one in hazard.person_time]
    chance = origin if origin is not None else [0.0 for _patient in range(patients)]
    switch_counts = list(switch_rule.patients) if switch_rule is not None else []
    model = _Model(
        [[(hazard.events[value][band] / times[band]) if times[band] > 0 else 0.0 for band in range(bands)] for value in range(values)],
        [[1.0, 1.0] for _value in range(values)],
        [[[1.0 for _band in range(len(column.events[0]))] for column in hazard.columns] for _value in range(values)],
        [0.0 for _band in switch_counts],
        [[1.0 for _band in column.switches] if column.switches and switch_counts else [] for column in hazard.columns],
    )
    if patients <= 0 or values == 0:
        return model
    lows = [0.0] + cuts.switch
    able = max(1, sum(1 for one in eligible if one))
    for band in range(len(switch_counts)):
        high = lows[band + 1] if band + 1 < len(lows) else cuts.switch_end
        width = high - lows[band] if high > lows[band] else 1.0
        model.switch[band] = switch_counts[band] / (able * width)
    if patients <= CAL_PERSONS:
        read = list(range(patients))
    else:
        read = [(at * patients) // CAL_PERSONS for at in range(CAL_PERSONS)]
    scale = len(read) / patients
    state_times = [time_of(one, "person-time") for one in hazard.switch_time]
    column_times = [[time_of(one, "person-time") for one in column.person_time] for column in hazard.columns]
    target_switch = [count * scale for count in switch_counts]
    target_switch_column = [[count * scale for count in column.switches] if column.switches else [] for column in hazard.columns]
    # THE ORIGIN'S SWITCHES (repair 2, Codex's item 2): the patients treated
    # from the origin stand in the first band's count and in their column
    # bands' switches, so the switch's rates are fitted to the rest.
    if target_switch and any(chance[patient] > 0.0 for patient in read):
        target_switch[0] = max(0.0, target_switch[0] - sum(chance[patient] for patient in read))
        for at in range(len(hazard.columns)):
            if target_switch_column[at]:
                for patient in read:
                    target_switch_column[at][column_bands[at][patient]] = target_switch_column[at][column_bands[at][patient]] - chance[patient]
                target_switch_column[at] = [max(0.0, one) for one in target_switch_column[at]]

    def at_rate(events: int, published: float, exposure: float) -> float:
        """A margin cell's target: the published rate (ends over person-time) on the twin's own time at risk there."""
        return events * exposure / published if published > 0.0 else 0.0
    for _round in range(CAL_ROUNDS):
        keys: "dict[tuple[int, ...], int]" = {}
        key_bands: "list[tuple[int, ...]]" = []
        cell_of: "dict[tuple[int, int, int], int]" = {}
        cell_key: "list[int]" = []
        cell_band: "list[int]" = []
        cell_state: "list[int]" = []
        cell_length: "list[float]" = []
        switch_time = [0.0 for _band in switch_counts]
        switch_cell: "dict[tuple[int, int], float]" = {}
        for patient in read:
            own = tuple(column_bands[at][patient] for at in range(len(hazard.columns)))
            factors = _factors(model, list(own))
            switched, end, _value = _drawn(model, cuts, factors, eligible[patient], shares[patient], chance[patient])
            if own not in keys:
                keys[own] = len(key_bands)
                key_bands += [own]
            key = keys[own]
            turn = switched if switched is not None else end
            for low, high, band, switch_band in _pieces(cuts, 0.0):
                if low >= end:
                    break
                state = 0 if low < turn else 1
                length = min(high, end, turn if state == 0 else _FAR) - low
                if state == 0 and eligible[patient] and switch_band >= 0:
                    switch_time[switch_band] = switch_time[switch_band] + length
                    switch_cell[(switch_band, key)] = (switch_cell[(switch_band, key)] if (switch_band, key) in switch_cell else 0.0) + length
                for one_state, one_length in ((state, length), (1, min(high, end) - turn if state == 0 and turn < min(high, end) else 0.0)):
                    if one_length <= 0.0:
                        continue
                    place = (key, band, one_state)
                    if place not in cell_of:
                        cell_of[place] = len(cell_key)
                        cell_key += [key]
                        cell_band += [band]
                        cell_state += [one_state]
                        cell_length += [0.0]
                    cell_length[cell_of[place]] = cell_length[cell_of[place]] + one_length
        if not any(model.switch_column):
            for band in range(len(switch_counts)):
                if target_switch[band] == 0.0:
                    model.switch[band] = 0.0
                elif switch_time[band] > 0.0:
                    model.switch[band] = target_switch[band] / switch_time[band]
        else:
            _switch_fitted(model, [(place, switch_cell[place]) for place in sorted(switch_cell)], key_bands, target_switch, target_switch_column)
        cells = len(cell_key)
        exposure_band = [0.0 for _band in range(bands)]
        exposure_state = [0.0, 0.0]
        exposure_column = [[0.0 for _band in range(len(column.events[0]))] for column in hazard.columns]
        for cell in range(cells):
            exposure_band[cell_band[cell]] = exposure_band[cell_band[cell]] + cell_length[cell]
            exposure_state[cell_state[cell]] = exposure_state[cell_state[cell]] + cell_length[cell]
            for at in range(len(hazard.columns)):
                exposure_column[at][key_bands[cell_key[cell]][at]] = exposure_column[at][key_bands[cell_key[cell]][at]] + cell_length[cell]
        # EACH MARGIN AT ITS PUBLISHED RATE: every patient ends once, so a
        # margin's ends alone fix only its end values' shares, never its
        # level (all switched patients end in the second state, every patient
        # of a column band in that band); its target is the published ends
        # times the twin's time at risk there over the published person-time.
        target_band = [[at_rate(hazard.events[value][band], times[band], exposure_band[band]) for band in range(bands)] for value in range(values)]
        target_state = [[at_rate(hazard.switch_events[value][state], state_times[state], exposure_state[state]) for state in range(2)] for value in range(values)] if hazard.switch_events and len(state_times) == 2 else []
        target_column = [[[at_rate(hazard.columns[at].events[value][band], column_times[at][band], exposure_column[at][band]) for band in range(len(exposure_column[at]))] for at in range(len(hazard.columns))] for value in range(values)]
        for value in range(values):
            factor_of = [_person_factor(model, value, list(key_bands[key])) for key in range(len(key_bands))]
            for _pass in range(CAL_PASSES):
                expected = [0.0 for _band in range(bands)]
                for cell in range(cells):
                    expected[cell_band[cell]] = expected[cell_band[cell]] + model.state[value][cell_state[cell]] * factor_of[cell_key[cell]] * cell_length[cell]
                for band in range(bands):
                    if target_band[value][band] == 0.0:
                        model.rate[value][band] = 0.0
                    elif expected[band] > 0.0:
                        model.rate[value][band] = target_band[value][band] / expected[band]
                if target_state:
                    in_state = [0.0, 0.0]
                    for cell in range(cells):
                        in_state[cell_state[cell]] = in_state[cell_state[cell]] + model.rate[value][cell_band[cell]] * factor_of[cell_key[cell]] * cell_length[cell]
                    for state in range(2):
                        wanted = target_state[value][state]
                        if wanted == 0.0:
                            model.state[value][state] = 0.0
                        elif in_state[state] > 0.0:
                            model.state[value][state] = wanted / in_state[state]
                base = [0.0 for _key in range(len(key_bands))]
                for cell in range(cells):
                    base[cell_key[cell]] = base[cell_key[cell]] + model.rate[value][cell_band[cell]] * model.state[value][cell_state[cell]] * cell_length[cell]
                for at in range(len(hazard.columns)):
                    width = len(model.column[value][at])
                    within = [0.0 for _band in range(width)]
                    for key in range(len(key_bands)):
                        within[key_bands[key][at]] = within[key_bands[key][at]] + factor_of[key] * base[key]
                    moved = [1.0 for _band in range(width)]
                    for band in range(width):
                        wanted = target_column[value][at][band]
                        if wanted == 0.0:
                            moved[band] = 0.0
                        elif within[band] > 0.0:
                            moved[band] = wanted / within[band]
                    for band in range(width):
                        model.column[value][at][band] = model.column[value][at][band] * moved[band]
                    for key in range(len(key_bands)):
                        factor_of[key] = factor_of[key] * moved[key_bands[key][at]]
                _normalised(model, value)
                factor_of = [_person_factor(model, value, list(key_bands[key])) for key in range(len(key_bands))]
    return model


def _switch_fitted(
    model: _Model,
    places: "list[tuple[tuple[int, int], float]]",
    key_bands: "list[tuple[int, ...]]",
    target: "list[float]",
    target_column: "list[list[float]]",
) -> None:
    """The switch's rates by band and multipliers by column band, fitted in place to the scaled published switches of each margin (G16.19).

    `places` holds the first state's time at risk of the patients who can
    switch, by band of the switch and by column bands (a key into
    `key_bands`); `CAL_PASSES` passes of iterative proportional fitting,
    each multiplier set rescaled so its largest is 1, the scale moved into
    the rates.
    """
    for _pass in range(CAL_PASSES):
        factor_key = [_switch_factor(model, list(bands)) for bands in key_bands]
        expected = [0.0 for _band in target]
        for (band, key), length in places:
            expected[band] = expected[band] + factor_key[key] * length
        for band in range(len(target)):
            if target[band] == 0.0:
                model.switch[band] = 0.0
            elif expected[band] > 0.0:
                model.switch[band] = target[band] / expected[band]
        for at in range(len(model.switch_column)):
            if not model.switch_column[at]:
                continue
            factor_key = [_switch_factor(model, list(bands)) for bands in key_bands]
            within = [0.0 for _band in model.switch_column[at]]
            for (band, key), length in places:
                within[key_bands[key][at]] = within[key_bands[key][at]] + model.switch[band] * factor_key[key] * length
            for one in range(len(within)):
                if target_column[at][one] == 0.0:
                    model.switch_column[at][one] = 0.0
                elif within[one] > 0.0:
                    model.switch_column[at][one] = model.switch_column[at][one] * target_column[at][one] / within[one]
            largest = max(model.switch_column[at])
            if largest > 0.0:
                model.switch_column[at] = [one / largest for one in model.switch_column[at]]
                model.switch = [one * largest for one in model.switch]


@dataclasses.dataclass(frozen=True)
class Written:
    """What the writer did: the patients whose follow-up, drawn forward from the origin, it lengthened to hold their rows (or their switch time and one unit)."""

    lengthened: int


def _grid(value: float, unit: float) -> int:
    """A time on the column's grid, in whole units, the nearest (a half up)."""
    return int(value / unit + 0.5)


def cuts_of(grain: contract.PatientGrain) -> _Cuts:
    """Where every patient's pieces of time are cut: the hazard's and the switch's published edges, and where switching ends (the top band's end, twice its mean less its start)."""
    hazard = grain.hazard
    edges = [time_of(one, "band edge") for one in hazard.edges] if hazard is not None else []
    switch = grain.switches[0] if grain.switches else None
    if switch is None:
        return _Cuts(edges, [], 0.0)
    lows = [time_of(one, "switch band edge") for one in switch.edges]
    top_mean = time_of(switch.top_mean, "top band's mean switch time")
    low = lows[-1] if lows else 0.0
    end = 2.0 * top_mean - low if top_mean > low else low + 1.0
    return _Cuts(edges, lows, end)


def placed_cuts(follow: int, switched: "int | None", rho: int, words: chain_walk.Packed, cut_at: int) -> "list[int]":
    """A patient's `rho - 1` interior cuts on its grid, rising (G16.19): its switch time where it falls inside its follow-up, the rest a uniform sample of the free points.

    THE OTHER CUTS (repair 2, Codex's item 6): Floyd's sample of `k` of the
    `n` points 1 to `T - 1` left free by the switch's cut, one word each
    from `cut_at` on and no search (for `j` from `n - k + 1` to `n`, a word
    picks `t` in 1 to `j`; `j` is taken where `t` already is), so a patient
    costs its rows whatever its follow-up, a dense history included; the
    `c`-th free point is `c` below the switch's cut and `c + 1` from it on.
    Needs `T >= rho` (and `T > S`). A fixed function of its arguments.
    """
    item = chain_walk.item
    cuts_made: "list[int]" = [switched] if switched is not None and switched > 0 else []
    free = follow - 1 - len(cuts_made)
    wanted = rho - 1 - len(cuts_made)
    skipped = cuts_made[0] if cuts_made else follow
    chosen: "set[int]" = set()
    for top in range(free - wanted + 1, free + 1):
        share = _uniform(item(words, cut_at))
        cut_at += 1
        pick = 1 + min(top - 1, int(share * top))
        chosen |= {top if pick in chosen else pick}
    cuts_made += [pick if pick < skipped else pick + 1 for pick in sorted(chosen)]
    return sorted(cuts_made)


def write(
    grain: contract.PatientGrain,
    cells: "dict[str, twinstore.HeldColumn]",
    r_values: "list[int]",
    starts: "list[int]",
    column_bands: "list[list[int]]",
    words: chain_walk.Packed,
) -> Written:
    """Write the interval, switch and end columns of every twin patient (G16.19), in place.

    `r_values` and `starts` each patient's rows and its first row;
    `column_bands` each hazard column's band of each patient at its
    published level. Raises `errors.ProfileError` only as an internal
    check. No I/O of any kind.
    """
    rule = grain.intervals[0]
    hazard = grain.hazard
    if hazard is None or not grain.end_events:
        raise _internal("was asked to write intervals with no hazard moments")
    end = grain.end_events[0]
    switch = grain.switches[0] if grain.switches else None
    patients = len(r_values)
    places = rule.places
    unit = 1.0 / (10 ** places)
    item = chain_walk.item
    shares = [
        (_uniform(item(words, WORDS_A_PATIENT * patient)), _uniform(item(words, WORDS_A_PATIENT * patient + 1)),
         _uniform(item(words, WORDS_A_PATIENT * patient + 2)), _uniform(item(words, WORDS_A_PATIENT * patient + 3)))
        for patient in range(patients)
    ]
    # A switch inside the follow-up cuts it, so a patient of one row cannot
    # switch after the origin; any patient may be treated FROM the origin
    # where `origin` stands (repair 2, Codex's item 2).
    eligible = [switch is not None and r_values[patient] >= 2 for patient in range(patients)]
    chance = origin_shares(switch, r_values)
    cuts = cuts_of(grain)
    model = calibrated(hazard, switch, cuts, patients, column_bands, eligible, shares, chance)
    start_cells: "list[str]" = []
    stop_cells: "list[str]" = []
    switch_cells: "list[str]" = []
    end_cells: "list[str]" = []
    lengthened = 0
    for patient in range(patients):
        # Patient `p`'s words for its cuts: one an extra row, after every patient's four (G16.19).
        cut_at = WORDS_A_PATIENT * patients + starts[patient] - patient
        rho = r_values[patient]
        own = [column_bands[at][patient] for at in range(len(hazard.columns))]
        factors = _factors(model, own)
        switch_time, time, value = _drawn(model, cuts, factors, eligible[patient], shares[patient], chance[patient])
        follow = max(1, _grid(time, unit))
        # A switch drawn after the origin is written one unit from it at
        # least; only the origin's draw writes 0 (the micro-step, item 8: a
        # rounding to 0 treated the patient from its first row).
        switched = None if switch_time is None else max(1, _grid(switch_time, unit)) if switch_time > 0.0 else 0
        least = max(rho, switched + 1 if switched is not None else 0)
        if follow < least:
            follow = least
            lengthened += 1
        bounds = [0] + placed_cuts(follow, switched, rho, words, cut_at) + [follow]
        for at in range(rho):
            begin = bounds[at]
            start_cells += [units_text(begin, places)]
            stop_cells += [units_text(bounds[at + 1], places)]
            if switch is not None:
                switch_cells += [switch.second if switched is not None and begin >= switched else switch.first]
            end_cells += [end.values[value] if at == rho - 1 else end.none]
    rows = sum(r_values)
    if len(start_cells) != rows:
        raise _internal("wrote another number of rows than the census holds")
    cells[rule.start] = twinstore.held_column(start_cells)
    cells[rule.stop] = twinstore.held_column(stop_cells)
    if switch is not None:
        cells[switch.column] = twinstore.held_column(switch_cells)
    cells[end.column] = twinstore.held_column(end_cells)
    return Written(lengthened)


# -- THE LINES (validation V12.11) ----------------------------------------------------------------


def _starts_read(start: "list[object]") -> "list[fractions.Fraction | None]":
    """The start readings normalised ONCE for every patient (repair 2, Codex's item 5: rebuilding them for each patient was quadratic)."""
    return [one if isinstance(one, fractions.Fraction) else None for one in start]


def broken_by(
    rows_of: "list[list[int]]",
    start: "list[object]",
    stop: "list[object]",
    switch_texts: "list[str] | None",
    switch_pair: "tuple[str, str] | None",
    end_texts: "list[str] | None",
    end_none: str,
) -> "tuple[int, int, int]":
    """The patients of a file breaking the interval rule, the switch rule and the end-event rule (V12.11), each read in `A` order; linear in the rows."""
    interval = switch = ended = 0
    starts = _starts_read(start)
    for rows in rows_of:
        readable = all(isinstance(start[row], fractions.Fraction) and isinstance(stop[row], fractions.Fraction) for row in rows)
        if not readable:
            interval += 1
            ordered = list(rows)
        else:
            ordered = _in_start_order(rows, starts)
            previous: "object" = None
            bad = False
            for row in ordered:
                a, b = start[row], stop[row]
                if not a < b or (previous is None and a != 0) or (previous is not None and a != previous):  # type: ignore[operator]
                    bad = True
                previous = b
            interval += 1 if bad else 0
        if switch_texts is not None and switch_pair is not None:
            changes = 0
            bad = False
            for at in range(1, len(ordered)):
                before, after = switch_texts[ordered[at - 1]], switch_texts[ordered[at]]
                if before != after:
                    changes += 1
                    if (before, after) != switch_pair:
                        bad = True
            if bad or changes > 1 or any(switch_texts[row] not in switch_pair for row in ordered):
                switch += 1
        if end_texts is not None:
            if any(end_texts[row] != end_none for row in ordered[:-1]):
                ended += 1
    return interval, switch, ended


def _within(found: int, published_count: int) -> bool:
    """A file's count of ends against the published one: within three times the published count's square root, and one (V12.11)."""
    gap = found - published_count
    return gap * gap <= 9 * max(published_count, 1) + 6 * _whole_root(max(published_count, 1)) + 1


def _whole_root(n: int) -> int:
    """The greatest whole number whose square is at most `n` (Newton's method on whole numbers)."""
    if n <= 0:
        return 0
    x = 1
    while x * x <= n:
        x = x * 2
    while True:
        y = (x + n // x) // 2
        if y >= x:
            return x
        x = y


# The share a cell's rate may move on a twin and stand (V12.11; repair 2): the
# main effects the writer fits (G16.19) leave a cell's rate up to about a
# fifth off where the real hazard has a joint effect (the registry at 20,000
# rows: 18 per cent in one band of the entry date), so a quarter is allowed.
RATE_ALLOWANCE = fractions.Fraction(1, 4)


def rate_held(found: int, exposure: fractions.Fraction, published_count: int, published_time: fractions.Fraction) -> bool:
    """A file's ends in a cell against the published RATE on the file's own person-time there (V12.11; repair 2, Codex's item 3).

    The expected ends are the published ends times the file's person-time
    over the published person-time. The cell stands where the file's ends
    lie within three times the expected ends' square root, and one, of
    them, or within `RATE_ALLOWANCE` of them (the file's rate within a
    quarter of the published rate), each widened by the published
    person-time's rounding (half a unit of its third figure, as a share of
    it). A published person-time of 0 expects no end. Exact.
    """
    if published_time <= 0:
        expected = fractions.Fraction(0)
        slack = fractions.Fraction(0)
    else:
        expected = published_count * exposure / published_time
        slack = expected * pr.half_unit(published_time) / published_time
    gap = abs(found - expected) - slack
    if gap <= 1 or gap <= expected * RATE_ALLOWANCE:
        return True
    return (gap - 1) * (gap - 1) <= 9 * max(expected, fractions.Fraction(1))


def lines(
    grain: "dict[str, object]",
    rows_of: "list[list[int]]",
    start: "list[object]",
    stop: "list[object]",
    texts: "dict[str, list[str]]",
    bands: "dict[str, list[int]]",
    floor: int,
) -> "list[tuple[str, str, str, str]]":
    """V12.11's lines of a file against a description whose counting process stands: `(kind, subject, verdict, reason)`, verdicts alone.

    `rows_of` each file patient's rows in position order; `start` and
    `stop` the exact readings of `A` and `B` a file row each; `texts` the
    switch and end columns' cells; `bands` each hazard column's band of
    each file patient at its published level (-1 where none). The three
    rules are HELD where every file patient keeps them. THE SWITCH TIME'S
    BANDS (repair 2, Codex's item 4) are HELD where each band's patients,
    the patients who never switch and those treated from the origin lie
    within three times the published count's square root (and one) of it
    and the top band's mean switch time within three times its spread
    over the root of its patients, and one unit, of the published mean
    (the spread read as (top mean - lower edge) over the root of three,
    a uniform band's). Each margin of the hazard moments is HELD where
    every count of ends lies within that bound AND every cell's ends lie
    within `rate_held` of the published RATE on the file's own
    person-time there (repair 2, Codex's item 3: a margin whose
    person-time moved is MISSED, the moved cell named); WITHHELD where the
    file's own counts hold one of 1 to `f - 1` (V12.3's gate). The
    validator draws nothing and reads no key. Linear in the rows. Raises
    nothing for a description the loader accepted.
    """
    out: "list[tuple[str, str, str, str]]" = []
    rule = _get(grain, "intervals")
    switches = _get(grain, "switches")
    ends = _get(grain, "end_events")
    hazard = _get(grain, "hazard")
    if not isinstance(rule, list) or not rule or not isinstance(ends, list) or not ends or not isinstance(hazard, dict):
        return out
    names = rule[0]
    end = ends[0]
    switch = switches[0] if isinstance(switches, list) and switches else None
    switch_texts = texts[f"{switch['column']}"] if isinstance(switch, dict) and f"{switch['column']}" in texts else None
    switch_pair = (f"{switch['from']}", f"{switch['to']}") if isinstance(switch, dict) else None
    end_texts = texts[f"{end['column']}"] if f"{end['column']}" in texts else None
    interval, switched, ended = broken_by(rows_of, start, stop, switch_texts, switch_pair, end_texts, f"{end['none']}")
    out += [("intervals", f"{names['start']} to {names['stop']}", "HELD" if interval == 0 else "MISSED", "")]
    if isinstance(switch, dict):
        out += [("switches", f"{switch['column']}", "HELD" if switched == 0 and switch_texts is not None else "MISSED", "")]
    out += [("end events", f"{end['column']}", "HELD" if ended == 0 and end_texts is not None else "MISSED", "")]
    if interval or end_texts is None:
        return out
    values = [f"{one}" for one in end["values"]] if isinstance(end["values"], list) else []
    value_at = {value: at for at, value in enumerate(values)}
    edges = exact_edges(hazard["edges"]) if isinstance(hazard["edges"], list) else []
    count = len(edges) + 1
    lows = [fractions.Fraction(0)] + edges
    found_bands = [[0 for _band in range(count)] for _value in values]
    found_time = [fractions.Fraction(0) for _band in range(count)]
    found_states = [[0, 0] for _value in values]
    state_time = [fractions.Fraction(0), fractions.Fraction(0)]
    found_columns: "dict[str, list[list[int]]]" = {}
    column_time: "dict[str, list[fractions.Fraction]]" = {}
    columns = hazard["columns"] if isinstance(hazard["columns"], list) else []
    found_switches: "dict[str, list[int]]" = {}
    for entry in columns:
        if isinstance(entry, dict) and isinstance(entry["events"], list) and entry["events"]:
            found_columns[f"{entry['column']}"] = [[0 for _band in range(len(entry["events"][0]))] for _value in values]
            column_time[f"{entry['column']}"] = [fractions.Fraction(0) for _band in range(len(entry["events"][0]))]
            if isinstance(_get(entry, "switches"), list) and switch_texts is not None:
                found_switches[f"{entry['column']}"] = [0 for _band in range(len(entry["events"][0]))]
    switch_edges = exact_edges(switch["edges"]) if isinstance(switch, dict) and isinstance(switch["edges"], list) else []
    census = [0 for _band in range(len(switch_edges) + 1)]
    census_never = 0
    census_origin = [0, 0]
    top_sum = fractions.Fraction(0)
    starts = _starts_read(start)
    unread = 0
    for patient, rows in enumerate(rows_of):
        ordered = _in_start_order(rows, starts)
        last = ordered[-1]
        value = end_texts[last]
        follow = stop[last]
        if value not in value_at or not isinstance(follow, fractions.Fraction):
            unread += 1
            continue
        at = value_at[value]
        found_bands[at][_band_of(edges, follow)] += 1
        for band in range(count):
            if follow <= lows[band]:
                break
            found_time[band] += (follow if band + 1 >= count or follow < lows[band + 1] else lows[band + 1]) - lows[band]
        later: "list[int]" = []
        begun: "fractions.Fraction | None" = None
        if switch_texts is not None and switch_pair is not None:
            later = [row for row in ordered if switch_texts[row] == switch_pair[1]]
            first_start = starts[later[0]] if later else None
            begun = first_start if isinstance(first_start, fractions.Fraction) else None
            after = begun is not None and begun < follow
            found_states[at][1 if after else 0] += 1
            state_time[0] += begun if after and begun is not None else follow
            state_time[1] += follow - begun if after and begun is not None else 0
            if begun is None:
                census_never += 1
            else:
                place = _band_of(switch_edges, begun)
                census[place] += 1
                if place == len(switch_edges):
                    top_sum += begun
                if begun == 0:
                    census_origin[0 if len(rows) == 1 else 1] += 1
        for name in found_columns:
            band = bands[name][patient] if name in bands and patient < len(bands[name]) else -1
            if 0 <= band < len(found_columns[name][at]):
                found_columns[name][at][band] += 1
                column_time[name][band] += follow
                if later and name in found_switches:
                    found_switches[name][band] += 1

    def verdict(found: "list[list[int]]", published_lines: object) -> "tuple[str, str]":
        if not isinstance(published_lines, list) or len(published_lines) != len(found):
            return "MISSED", ""
        if any(0 < cell < floor for line in found for cell in line):
            return "WITHHELD", "not judged: the file's own counts of this object hold a count of 1 to f - 1, so describing this file on its own would not publish it"
        held = unread == 0
        for at in range(len(found)):
            line = published_lines[at]
            if not isinstance(line, list) or len(line) != len(found[at]):
                return "MISSED", ""
            for band in range(len(found[at])):
                if not _within(found[at][band], int(line[band]) if _whole(line[band]) else 0):
                    held = False
        return ("HELD" if held else "MISSED"), ""

    def rated(found: "list[list[int]]", exposure: "list[fractions.Fraction]", published_lines: object, published_times: object, where: str) -> "tuple[str, str]":
        shown, reason = verdict(found, published_lines)
        if shown != "HELD" or not isinstance(published_lines, list) or not isinstance(published_times, list) or len(published_times) != len(exposure):
            return shown, reason
        for band in range(len(exposure)):
            published_time = pr.fraction_read(published_times[band]) if isinstance(published_times[band], str) else None
            if published_time is None:
                return "MISSED", f"the published person-time of {where} band {band + 1} is not read"
            for at in range(len(found)):
                published_count = int(published_lines[at][band]) if _whole(published_lines[at][band]) else 0
                if not rate_held(found[at][band], exposure[band], published_count, published_time):
                    return "MISSED", (
                        f"the rate of ends of {values[at]} in {where} band {band + 1} moved: the file's ends over its own person-time "
                        "there lie beyond the sampling bound and a quarter of the published rate"
                    )
        return "HELD", ""

    shown, reason = rated(found_bands, found_time, hazard["events"], hazard["person_time"], "the time's")
    out += [("hazard", "the ends in each band of time", shown, reason)]
    if isinstance(switch, dict) and switch_texts is not None:
        shown, reason = _census_verdict(switch, census, census_never, census_origin, top_sum, floor, unread, int(names["places"]) if _whole(names["places"]) else 0)
        out += [("switches", f"the switch time's bands of {switch['column']}", shown, reason)]
    margin = hazard["switch"]
    if isinstance(margin, dict) and switch_texts is not None:
        shown, reason = rated(found_states, state_time, margin["events"], margin["person_time"], "the switch's state")
        out += [("hazard", f"the ends in each state of {switch['column'] if isinstance(switch, dict) else ''}", shown, reason)]
    for entry in columns:
        if isinstance(entry, dict) and f"{entry['column']}" in found_columns:
            name = f"{entry['column']}"
            shown, reason = rated(found_columns[name], column_time[name], entry["events"], entry["person_time"], f"{name}'s")
            out += [("hazard", f"the ends in each band of {name}", shown, reason)]
            if name in found_switches:
                shown, reason = verdict([found_switches[name]], [entry["switches"]])
                out += [("hazard", f"the switches in each band of {name}", shown, reason)]
    return out


def _census_verdict(
    switch: "dict[str, object]", census: "list[int]", never: int, origin: "list[int]", top_sum: fractions.Fraction, floor: int, unread: int, places: int,
) -> "tuple[str, str]":
    """The switch time's bands of a file against the published ones (V12.11; repair 2, Codex's item 4): each band, never and the origin within `_within`, the top band's mean within three spreads over the root of its patients and one unit of the column's grid."""
    published = switch["patients"] if isinstance(switch["patients"], list) else []
    counts = census + [never] + (origin if isinstance(_get(switch, "origin"), list) else [])
    if any(0 < one < floor for one in counts):
        return "WITHHELD", "not judged: the file's own counts of this object hold a count of 1 to f - 1, so describing this file on its own would not publish it"
    if len(published) != len(census) or unread:
        return "MISSED", "the file's switch time's bands do not stand beside the published ones"
    never_published = switch["never"]
    wanted = [int(one) if _whole(one) else 0 for one in published] + [never_published if isinstance(never_published, int) and _whole(never_published) else 0]
    named = [f"band {band + 1}" for band in range(len(census))] + ["never"]
    published_origin = _get(switch, "origin")
    if isinstance(published_origin, list) and len(published_origin) == 2:
        wanted += [int(one) if _whole(one) else 0 for one in published_origin]
        named += ["treated from the origin, one row", "treated from the origin, two rows or more"]
    for at in range(len(wanted)):
        if not _within(counts[at], wanted[at]):
            return "MISSED", f"the patients of {named[at]} moved beyond the sampling bound of the published count"
    top = census[-1]
    top_mean = pr.fraction_read(switch["top_mean"]) if isinstance(switch["top_mean"], str) else None
    edges = exact_edges(switch["edges"]) if isinstance(switch["edges"], list) else []
    low = edges[-1] if edges else fractions.Fraction(0)
    if top and top_mean is not None:
        mean = top_sum / top
        spread_squared = (top_mean - low) * (top_mean - low) / 3
        slack = abs(mean - top_mean)
        unit = fractions.Fraction(1, 10 ** places)
        if slack > unit and (slack - unit) * (slack - unit) * top > 9 * spread_squared:
            return "MISSED", "the top band's mean switch time moved beyond three spreads over the root of its patients, and one unit"
    return "HELD", ""
