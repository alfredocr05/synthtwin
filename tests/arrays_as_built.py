"""FROZEN AS-BUILT REFERENCES of the polish's row passes (lane ARR-a, plan P4-D466; tests only).

Lane MPg's polish (method G16.3, plan P4-D456) is not on the line lane
ARR-a builds on, so its loops are copied here as they stand in
`src/synthtwin/generation.py` and `src/synthtwin/chain_walk.py` at lane
MPg's head aea59493, each written as a pure function of plain values
(the state's dictionaries and the target objects unpacked into their
fields; nothing else changed: the same loops, the same order of every
float operation, the same `math.fsum` calls). tests/test_arrays.py
holds the audited array helper (`synthtwin.arrays`) to these, byte for
byte. They are FROZEN: a change here is a change of the reference, which
only a plan decision makes (A-P4-59 governs the method; the helper
changes no method and no order).

Where each comes from (aea59493):
- `read_code`, `write_code`, `width_for`, `hidden_sum(s)`,
  `hidden_score`: chain_walk.py, verbatim;
- `row_bands`: generation._row_bands;
- `feature_rank`, `feature_band`: generation._feature's two branches;
- `scores`: the score build of generation._polish_column;
- `pair_move`, `within_move`: its two spread moves;
- `rows_by_group`, `places_by_group`, `joint_groups`, `score_key`:
  generation._rows_by_group, _places_by_group, _joint_groups and
  _score_key;
- `ordered_rows` and `write_back`: the sort inside each frame group and
  the write-back of _polish_column;
- `pair_sums`, `by_sums`, `grouping_sums`, `pair_spread_sums`,
  `within_spread_sums`: the sums its adjust step forms.
"""

import math

SCORE_CENTRE = 393210
SCORE_UNIT = 65536
_MASK16 = 65535


def read_code(data, width, row):
    at = row * width
    value = 0
    for place in range(width):
        value = value | (data[at + place] << (8 * place))
    return value


def write_code(data, width, row, value):
    at = row * width
    for place in range(width):
        data[at + place] = (value >> (8 * place)) & 255


def width_for(top):
    width = 1
    while width < 8 and top >= (1 << (8 * width)):
        width = width + 1
    return width


def packed_values(data, width):
    """Every whole number of a little-endian store, as a list."""
    return [read_code(data, width, row) for row in range(len(data) // width)]


def packed_store(values, width):
    """A list of whole numbers as a little-endian store."""
    out = bytearray(width * len(values))
    for row in range(len(values)):
        write_code(out, width, row, values[row])
    return out


def hidden_sum(first, second, third):
    total = 0
    for word in (first, second, third):
        total = total + (word & _MASK16) + ((word >> 16) & _MASK16)
        total = total + ((word >> 32) & _MASK16) + ((word >> 48) & _MASK16)
    return total


def hidden_sums(words):
    if len(words) % 3:
        raise ValueError("three words a row")
    return [
        hidden_sum(words[3 * row], words[3 * row + 1], words[3 * row + 2])
        for row in range(len(words) // 3)
    ]


def hidden_score(total):
    return (total - SCORE_CENTRE) / SCORE_UNIT


def row_bands(index, index_width, slot_l0, l0_width, to_level, rows):
    """generation._row_bands, its read: each row's band through its place."""
    return [
        to_level[read_code(slot_l0, l0_width, read_code(index, index_width, row))]
        for row in range(rows)
    ]


def feature_rank(normal, ranks, present, held):
    """generation._feature, a partner number's rank score (0 where it holds none)."""
    return [normal[ranks[2 * row] | (ranks[2 * row + 1] << 8)] if present[row] else 0.0 for row in held]


def feature_band(encoding, of_row, held):
    """generation._feature, the encoding of a band."""
    return [encoding[of_row[row]] if of_row[row] < len(encoding) else 0.0 for row in held]


def scores(present, partners, normal, noise, sums, chunk=65536):
    """The score build of generation._polish_column: a chunk of rows at a time, 0.0 on a row holding no reading.

    `partners` is the helper's form: ("rank", weight, ranks, has) or
    ("band", weight, bands, encoding); `sums` each row's hidden sum.
    """
    rows = len(present)
    score = [0.0 for _row in range(rows)]
    for start in range(0, rows, chunk):
        members = [row for row in range(start, min(rows, start + chunk)) if present[row]]
        part = [0.0 for _row in members]
        for kind, weight, codes, more in partners:
            if kind == "rank":
                values = feature_rank(normal, codes, more, members)
            else:
                values = feature_band(more, codes, members)
            part = [total + weight * value for total, value in zip(part, values)]
            values = []
        for at in range(len(members)):
            row = members[at]
            score[row] = part[at] + noise * hidden_score(sums[row])
        members = []
        part = []
    return score


def pair_move(score, present, both, factor):
    """A pair's own spread: the rows whose partner holds a reading, moved from their mean by the pair's factor."""
    rows = len(present)
    pair_total = 0.0
    pair_rows = 0
    for row in range(rows):
        if present[row] and both[row]:
            pair_total = pair_total + score[row]
            pair_rows = pair_rows + 1
    if pair_rows:
        pair_middle = pair_total / pair_rows
        for row in range(rows):
            if present[row] and both[row]:
                score[row] = pair_middle + factor * (score[row] - pair_middle)
    return pair_total, pair_rows


def within_move(score, present, of_row, scales):
    """A grouping target's band spreads: each row moved from its band's mean by the band's factor."""
    rows = len(present)
    bands = len(scales)
    totals = [0.0 for _band in range(bands)]
    counts = [0 for _band in range(bands)]
    for row in range(rows):
        if present[row] and of_row[row] < bands:
            totals[of_row[row]] = totals[of_row[row]] + score[row]
            counts[of_row[row]] = counts[of_row[row]] + 1
    means = [totals[band] / counts[band] if counts[band] else 0.0 for band in range(bands)]
    factors = scales
    for row in range(rows):
        if present[row] and of_row[row] < bands:
            band = of_row[row]
            score[row] = means[band] + factors[band] * (score[row] - means[band])
    return totals, counts, means


def joint_groups(found, bands, count, rows, width=4):
    """generation._joint_groups (`found` a store of `width` bytes a row, renumbered in place)."""
    seen = {}
    for row in range(rows):
        value = read_code(found, width, row) * count + bands[row]
        if value not in seen:
            seen[value] = len(seen)
        write_code(found, width, row, seen[value])


def rows_by_group(groups, present, count, width=4):
    """generation._rows_by_group: the rows packed, the starts, the groups met."""
    rows = len(present)
    sizes = {}
    for row in range(rows):
        if present[row]:
            group = read_code(groups, width, row)
            sizes[group] = sizes[group] + 1 if group in sizes else 1
    ordered = sorted(sizes)
    starts = [0]
    next_slot = {}
    for group in ordered:
        next_slot[group] = starts[-1]
        starts += [starts[-1] + sizes[group]]
    grouped_width = width_for(max(rows - 1, 0))
    grouped = bytearray(count * grouped_width)
    for row in range(rows):
        if present[row]:
            group = read_code(groups, width, row)
            write_code(grouped, grouped_width, next_slot[group], row)
            next_slot[group] = next_slot[group] + 1
    return grouped, grouped_width, starts, ordered


def places_by_group(groups, present, starts, ordered, index, index_width, slot_codes, binary, width=4):
    """generation._places_by_group: each frame group's places in its slots."""
    rows = len(present)
    count = len(slot_codes)
    position = {ordered[at]: at + 1 for at in range(len(ordered))}
    of_place = bytearray(4 * count)
    for row in range(rows):
        if present[row]:
            write_code(of_place, 4, read_code(index, index_width, row), position[read_code(groups, width, row)])
    position = {}
    found_width = width_for(max(count - 1, 0))
    found = bytearray(starts[-1] * found_width)
    next_slot = [starts[group] for group in range(len(starts) - 1)]
    for level in ((0, 1) if binary else (-1,)):
        for place in range(count):
            group = read_code(of_place, 4, place)
            if group and (level < 0 or slot_codes[place] == level):
                write_code(found, found_width, next_slot[group - 1], place)
                next_slot[group - 1] = next_slot[group - 1] + 1
    return found


_SCORE_KEY_OFFSET = 1 << 65


def score_key(score):
    if score == 0.0:
        return _SCORE_KEY_OFFSET
    fraction, exponent = math.frexp(score)
    magnitude = (exponent + 1100) * (1 << 53) + int(abs(fraction) * (1 << 53))
    return _SCORE_KEY_OFFSET + magnitude if score > 0.0 else _SCORE_KEY_OFFSET - magnitude


def ordered_rows(grouped, grouped_width, starts, score):
    """The sort inside each frame group: each slot's row after `sorted(key * span + row)` (ties to the lower row)."""
    rows = len(score)
    span = 1
    while span <= rows:
        span = span * 2
    out = []
    for group in range(len(starts) - 1):
        start = starts[group]
        ranked = sorted(
            score_key(score[row]) * span + row
            for row in (read_code(grouped, grouped_width, slot) for slot in range(start, starts[group + 1]))
        )
        out += [key % span for key in ranked]
    return out


def write_back(ordered, places, places_width, index, index_width, own, slot_codes, ranks, slot_rank):
    """The write-back of each slot's row: its index, its code and its rank code."""
    for k in range(len(ordered)):
        row = ordered[k]
        place = read_code(places, places_width, k)
        write_code(index, index_width, row, place)
        own[row] = slot_codes[place]
        if ranks is not None and slot_rank is not None:
            ranks[2 * row] = slot_rank[2 * place]
            ranks[2 * row + 1] = slot_rank[2 * place + 1]


def pair_sums(own, present, partner, both, table, other):
    """The adjust step's pair sums: n, sx, sxx, sy, syy, sxy over the rows holding both readings."""
    rows = len(own)
    n = 0
    for row in range(rows):
        if present[row] and both[row]:
            n = n + 1
    sx = math.fsum(table[own[row]] for row in range(rows) if present[row] and both[row])
    sxx = math.fsum(table[own[row]] * table[own[row]] for row in range(rows) if present[row] and both[row])
    sy = math.fsum(other[partner[row]] for row in range(rows) if present[row] and both[row])
    syy = math.fsum(other[partner[row]] * other[partner[row]] for row in range(rows) if present[row] and both[row])
    sxy = math.fsum(table[own[row]] * other[partner[row]] for row in range(rows) if present[row] and both[row])
    return n, sx, sxx, sy, syy, sxy


def by_sums(number_codes, holding, number, of_row, encoding):
    """The adjust step's 'by' sums: m, sx, sy, sxy over the number's rows."""
    rows = len(number_codes)
    m = 0
    for row in range(rows):
        if holding[row]:
            m = m + 1
    sx = math.fsum(number[number_codes[row]] for row in range(rows) if holding[row])
    sy = math.fsum(encoding[of_row[row]] for row in range(rows) if holding[row] and of_row[row] < len(encoding))
    sxy = math.fsum(
        number[number_codes[row]] * encoding[of_row[row]] for row in range(rows) if holding[row] and of_row[row] < len(encoding)
    )
    return m, sx, sy, sxy


def grouping_sums(own, present, table, of_row, encoding):
    """The adjust step's whole_x and a grouping target's sy and sxy."""
    rows = len(own)
    whole_x = math.fsum(table[own[row]] for row in range(rows) if present[row])
    sy = math.fsum(encoding[of_row[row]] for row in range(rows) if present[row] and of_row[row] < len(encoding))
    sxy = math.fsum(
        table[own[row]] * encoding[of_row[row]] for row in range(rows) if present[row] and of_row[row] < len(encoding)
    )
    return whole_x, sy, sxy


def pair_spread_sums(own, present, both):
    """A pair's spread factor's whole numbers: held, total and squares of the codes."""
    held_pair = 0
    total_pair = 0
    squares_pair = 0
    for row in range(len(own)):
        if present[row] and both[row]:
            code = own[row]
            held_pair = held_pair + 1
            total_pair = total_pair + code
            squares_pair = squares_pair + code * code
    return held_pair, total_pair, squares_pair


def within_spread_sums(own, present, of_row, bands):
    """A grouping target's spread factors' whole numbers a band."""
    held = [0 for _band in range(bands)]
    totals = [0 for _band in range(bands)]
    squares = [0 for _band in range(bands)]
    for row in range(len(own)):
        if present[row] and of_row[row] < bands:
            band = of_row[row]
            code = own[row]
            held[band] = held[band] + 1
            totals[band] = totals[band] + code
            squares[band] = squares[band] + code * code
    return held, totals, squares
