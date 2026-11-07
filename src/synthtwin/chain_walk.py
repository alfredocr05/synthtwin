"""THE CHAIN'S ARRANGEMENT: the shared module of method G16 (G16.9; lane CHb, plan P4-D435).

BUILT BEHIND THE CHAIN'S SWITCH. `generation.generate_held` calls it only
for a description loaded with `contract.load_profile(..., chain=True)`
whose chain places a family with a parent; no shipped command loads one
(invariant S12), so every twin a person makes is byte for byte what it
was.

What lives here, each as the method writes it:

- G16.8's HIDDEN SCORE: the twelve 16-bit pieces of a row's three words
  summed as a whole number `S`, the score `z = (S - 393210) / 65536`;
- G16.1's VALUE CODE (contract 4.6b.6), in exact integer arithmetic on
  binary64 values, and G16.2 step 2's latent order `L` where a family
  publishes slopes;
- G16.2 steps 3 and 4: the bands inside each parent cell, then the cells
  inside their bands, each row's band code and CELL INDEX;
- G16.0's TARGET of a family, and G16.6's MOVED TABLE, exactly: the
  fewest units in published noughts, then the least summed distance,
  then the least sum of squares, then the greatest table read in
  row-major order;
- G16.2 step 5's order rule carried by its difference: `B = A + D` on
  decimal text, the larger number of places of the two.

THE BOUNDARY (G16.9). The module imports the standard library only:
neither the reader, nor pandas, nor numpy, nor the generation module's
random stream. Every function takes its words, its rows and its counts
as arguments and hands values back, so the profiler's self-test (lane
ST) can call it on SplitMix64 words of its sample, and the generator on
words of its one stream. Every decision is made in Python integers, or
in binary64 `+ - * /` each in the order written, which CPython rounds
correctly on every machine. Raises ValueError where an argument breaks
a stated precondition (a mistake of the caller). No I/O of any kind.
"""

import dataclasses
import math

# G16.8: `S` lies in 0 .. 12 * 65535; the score is centred on 6 * 65535.
SCORE_CENTRE = 393210
SCORE_STEPS = 786421
SCORE_UNIT = 65536
# G16.8: one call of the stream for each block of this many arranged rows.
BLOCK_ROWS = 65536
# G16.11: a row's `S` (at most 12 x 65,535) is held in three bytes.
SUM_WIDTH = 3
# G16.2 step 4 and G16.10: a cell index takes 3 bytes a row, 4 above this.
THREE_BYTES = 16_777_215

_MASK16 = 65535


def hidden_sum(first: int, second: int, third: int) -> int:
    """`S`, the sum of the twelve 16-bit pieces of a row's three words (G16.8)."""
    total = 0
    for word in (first, second, third):
        total = total + (word & _MASK16) + ((word >> 16) & _MASK16)
        total = total + ((word >> 32) & _MASK16) + ((word >> 48) & _MASK16)
    return total


def hidden_sums(words: "list[int]") -> "list[int]":
    """Each row's `S` from its three words, `3 k`, `3 k + 1` and `3 k + 2` (G16.8)."""
    if len(words) % 3:
        raise ValueError("three words a row")
    return [
        hidden_sum(words[3 * row], words[3 * row + 1], words[3 * row + 2])
        for row in range(len(words) // 3)
    ]


def hidden_score(total: int) -> float:
    """The hidden score `z = (S - 393210) / 65536`, exact in binary64 (G16.8)."""
    return (total - SCORE_CENTRE) / SCORE_UNIT


def _exact(value: float) -> "tuple[int, int]":
    """A binary64 value as `m * 2 ** e`, `m` a whole number, exactly."""
    mantissa, exponent = math.frexp(value)
    return int(mantissa * 9007199254740992.0), exponent - 53


def value_code(x: float, lo: float, hi: float) -> int:
    """Contract 4.6b.6's value code `min(255, max(0, floor(256 (x - lo) / (hi - lo))))`, exact.

    `x`, `lo` and `hi` are binary64 values (a reading, and the outermost
    published rung pair); the quotient is formed in whole numbers, so no
    rounding decides a code. Every code is 0 where `lo` equals `hi`.
    """
    if lo == hi:
        return 0
    parts = [_exact(x), _exact(lo), _exact(hi)]
    least = min(exponent for _mantissa, exponent in parts)
    scaled = [mantissa << (exponent - least) for mantissa, exponent in parts]
    numerator = 256 * (scaled[0] - scaled[1])
    denominator = scaled[2] - scaled[1]
    if denominator < 0:
        numerator = -numerator
        denominator = -denominator
    return min(255, max(0, numerator // denominator))


def spread_positions(rows: int, taken: int) -> "list[int]":
    """G16.2 steps 3 and 4: the `q`-th of `taken` rows stands at `floor((2 q + 1) rows / (2 taken))`."""
    if taken <= 0:
        return []
    return [((2 * q + 1) * rows) // (2 * taken) for q in range(taken)]


def order_by_scores(totals: "Packed | list[int]") -> "Packed":
    """The arranged rows sorted by `L = z`, ties to the lower row number (G16.2 steps 3 and 4).

    `z` is a strictly increasing function of `S`, so the order of `S` is
    the order of `z`. Two stable passes of a counting sort, on the low and
    then the high ten bits of `S` (which lies below 2 ** 20), starting
    from the rows in row order: equal scores keep row order, so ties go to
    the lower row number, the order the composite key `S n + r` gave.
    Handed back packed, `width_for(n - 1)` bytes a row (G16.11's memory
    clause; repair 1 of lane CHb, item 4). Raises ValueError where a
    total is not a hidden sum.
    """
    count = size_of(totals)
    width = width_for(count - 1)
    first = packed(count, width)
    _counting_pass(totals, None, count, 0, first)
    second = packed(count, width)
    _counting_pass(totals, first, count, _PASS_BITS, second)
    return second


_PASS_BITS = 10
_PASS_MASK = (1 << _PASS_BITS) - 1


def _counting_pass(
    totals: "Packed | list[int]", rows_in: "Packed | None", count: int, shift: int, out: "Packed"
) -> None:
    """One stable pass of `order_by_scores`: the rows (in `rows_in`'s order, else row order) by ten bits of `S`."""
    starts = [0 for _bucket in range((1 << _PASS_BITS) + 1)]
    for at in range(count):
        row = at if rows_in is None else item(rows_in, at)
        total = item(totals, row)
        if total < 0 or total >= (1 << (2 * _PASS_BITS)):
            raise ValueError("a total is not a hidden sum")
        bucket = (total >> shift) & _PASS_MASK
        starts[bucket + 1] = starts[bucket + 1] + 1
    for bucket in range(1 << _PASS_BITS):
        starts[bucket + 1] = starts[bucket + 1] + starts[bucket]
    for at in range(count):
        row = at if rows_in is None else item(rows_in, at)
        bucket = (item(totals, row) >> shift) & _PASS_MASK
        put(out, starts[bucket], row)
        starts[bucket] = starts[bucket] + 1


def order_by_latent(latent: "list[float]") -> "list[int]":
    """The arranged rows sorted by a binary64 latent order `L`, ties to the lower row number."""
    return [row for _value, row in sorted([(latent[row], row) for row in range(len(latent))])]


def order_by_latent_packed(latent: "list[float]") -> "Packed":
    """`order_by_latent`, handed back packed `width_for(n - 1)` bytes a row (G16.11's memory clause).

    The rows sorted on the pairs `(L, row)`, so equal values keep row
    order: ties go to the lower row number, as `order_by_latent`.
    """
    count = len(latent)
    out = packed(count, width_for(count - 1))
    at = 0
    for _value, row in sorted([(latent[row], row) for row in range(count)]):
        put(out, at, row)
        at += 1
    return out


# -- G16.2 step 2's IMPLIED SLOPE (lane MPg, plan P4-D456) -------------------
#
# Where a family publishes no slope, its child is a column of value ranges
# and it has a parent, the walk orders its rows by a slope IMPLIED by what
# the description already publishes: a weighted least-squares line of the
# child's band scores on its ranged parents' band scores over the family's
# published cells, plus each cell's mean band score. Nothing new is
# published, and every number is formed in binary64 `+ - * /` and `sqrt`,
# each in the order written (zone G), from published counts and the walk's
# own ranks. `natural_log` and `normal_score` are written out for that
# reason: no library function decides a byte.

_LN2 = 0.6931471805599453
_ROOT_HALF = 0.7071067811865476
# The odd reciprocals 1, 1/3, ..., 1/25 of the series `ln m = 2 atanh y`.
_ODD = tuple(1.0 / (2 * k + 1) for k in range(13))
# P. J. Acklam's rational approximation of the normal quantile (relative
# error below 1.15e-9): its centre and its tails.
_CENTRE_TOP = (
    -39.69683028665376,
    220.9460984245205,
    -275.9285104469687,
    138.3577518672690,
    -30.66479806614716,
    2.506628277459239,
)
_CENTRE_BOTTOM = (
    -54.47609879822406,
    161.5858368580409,
    -155.6989798598866,
    66.80131188771972,
    -13.28068155288572,
)
_TAIL_TOP = (
    -0.007784894002430293,
    -0.3223964580411365,
    -2.400758277161838,
    -2.549732539343734,
    4.374664141464968,
    2.938163982698783,
)
_TAIL_BOTTOM = (
    0.007784695709041462,
    0.3224671290700398,
    2.445134137142996,
    3.754408661907416,
)
_TAIL_EDGE = 0.02425
# The normal equations' ridge, and the least spread a child keeps.
_RIDGE = 1e-9
_LEAST_SPREAD = 0.1


def natural_log(x: float) -> float:
    """`ln x` for a binary64 `x` above nought, in `+ - * /` written in order (G16.2 step 2).

    `x = m 2 ** e` by `math.frexp` (exact), `m` moved into `[sqrt(1/2),
    sqrt(2))`; then `ln m = 2 y (1 + y**2 / 3 + ... + y**24 / 25)`, `y = (m
    - 1) / (m + 1)`, summed by Horner's rule from the last term, and `e
    ln 2` added. Raises ValueError at or below nought.
    """
    if not x > 0.0:
        raise ValueError("a logarithm of a number above nought")
    mantissa, exponent = math.frexp(x)
    if mantissa < _ROOT_HALF:
        mantissa = mantissa * 2.0
        exponent = exponent - 1
    y = (mantissa - 1.0) / (mantissa + 1.0)
    square = y * y
    total = _ODD[12]
    for k in range(11, -1, -1):
        total = total * square + _ODD[k]
    return 2.0 * y * total + exponent * _LN2


def normal_score(p: float) -> float:
    """The standard normal quantile of `p` (0 < p < 1) by Acklam's approximation, in binary64.

    The centre `|p - 1/2| <= 1/2 - 0.02425` a ratio of polynomials in `(p
    - 1/2) ** 2`; each tail one in `q = sqrt(-2 ln p)` (`ln` by
    `natural_log`), the upper tail on `1 - p` with its sign changed. Each
    polynomial by Horner's rule, each operation rounded once in the order
    written. Raises ValueError outside `(0, 1)`.
    """
    if not 0.0 < p < 1.0:
        raise ValueError("a share strictly between nought and one")
    if p < _TAIL_EDGE or p > 1.0 - _TAIL_EDGE:
        tail = p if p < _TAIL_EDGE else 1.0 - p
        q = math.sqrt(-2.0 * natural_log(tail))
        top = _TAIL_TOP[0]
        for k in range(1, 6):
            top = top * q + _TAIL_TOP[k]
        bottom = _TAIL_BOTTOM[0]
        for k in range(1, 4):
            bottom = bottom * q + _TAIL_BOTTOM[k]
        bottom = bottom * q + 1.0
        value = top / bottom
        return value if p < _TAIL_EDGE else -value
    q = p - 0.5
    r = q * q
    top = _CENTRE_TOP[0]
    for k in range(1, 6):
        top = top * r + _CENTRE_TOP[k]
    bottom = _CENTRE_BOTTOM[0]
    for k in range(1, 5):
        bottom = bottom * r + _CENTRE_BOTTOM[k]
    bottom = bottom * r + 1.0
    return top * q / bottom


def band_scores(totals: "list[int]", valued: "list[bool]") -> "list[float | None]":
    """Each band's NORMAL SCORE at one level, from its published totals (G16.2 step 2, implied slope).

    `totals[b]` is band `b`'s published total at the level (its `L0`
    totals summed), `valued[b]` whether it holds a value band. Over the
    value bands holding a row, `n` their rows in all and `C_b` the rows of
    those before `b`: `normal_score((2 C_b + t_b) / (2 n))`, the mid-point
    of the band's share. A spread band, or one holding no row, scores None.
    """
    count = 0
    for band in range(len(totals)):
        if valued[band] and totals[band] > 0:
            count = count + totals[band]
    out: "list[float | None]" = []
    below = 0
    for band in range(len(totals)):
        if not valued[band] or totals[band] <= 0 or count <= 0:
            out += [None]
            continue
        out += [normal_score((2 * below + totals[band]) / (2 * count))]
        below = below + totals[band]
    return out


@dataclasses.dataclass(frozen=True)
class ImpliedSlope:
    """A family's implied slope (G16.2 step 2): each ranged parent's coefficient, the spread, the cell means.

    `beta[j]` belongs to the `j`-th parent of `used` (places in the
    family's parent list), `sigma` multiplies the hidden score, and
    `means[c]` is parent cell `c`'s mean band score of the child (None
    where the published row holds no row of a scored band).
    """

    used: "tuple[int, ...]"
    beta: "tuple[float, ...]"
    sigma: float
    means: "tuple[float | None, ...]"


def implied_slope(
    table: "tuple[tuple[int, ...], ...]",
    sizes: "list[int]",
    parent_scores: "list[list[float | None]]",
    used: "list[int]",
    child_scores: "list[float | None]",
) -> ImpliedSlope:
    """G16.2 step 2's implied slope of one family, from its PUBLISHED table and band scores alone.

    `table` is the family's published table (one row a parent cell, the
    last parent varying fastest; `sizes` each parent's bands at the
    family's level), `parent_scores[j]` parent `j`'s band scores there,
    `used` the ranged parents (in order), `child_scores` the child's band
    scores at its level. For each cell: `w` its rows in scored bands of the
    child, `y` their mean score (summed in band order, divided once); a
    cell whose used parents all score enters the fit with weight `w` and
    `x` their scores. The fit centres `x` and `y` on their weighted means,
    forms the normal equations `A beta = v` (ridge 1e-9 on `A`'s diagonal),
    solves them by Gauss-Jordan elimination in order without exchanges,
    and sets `sigma = max(0.1, sqrt(max(0, 1 - beta . v)))`. Where no
    parent is used or no cell enters, `beta` is empty and `sigma` 1.
    Every sum is taken in cell order, each operation rounded once.
    """
    cells = len(table)
    means: "list[float | None]" = []
    weights: "list[int]" = []
    xs: "list[list[float]]" = []
    ys: "list[float]" = []
    for cell in range(cells):
        parts = [0 for _parent in sizes]
        rest = cell
        for place in range(len(sizes) - 1, -1, -1):
            parts[place] = rest % sizes[place]
            rest = rest // sizes[place]
        weight = 0
        total = 0.0
        row = table[cell]
        for band in range(len(row)):
            score = child_scores[band] if band < len(child_scores) else None
            if row[band] and score is not None:
                weight = weight + row[band]
                total = total + row[band] * score
        if not weight:
            means += [None]
            continue
        mean = total / weight
        means += [mean]
        x: "list[float]" = []
        whole = True
        for parent in used:
            value = parent_scores[parent][parts[parent]]
            if value is None:
                whole = False
                break
            x += [value]
        if whole:
            weights += [weight]
            xs += [x]
            ys += [mean]
    width = len(used)
    if not width or not weights:
        return ImpliedSlope(tuple(used), (), 1.0, tuple(means))
    summed = 0
    for weight in weights:
        summed = summed + weight
    centre = [0.0 for _a in range(width)]
    centre_y = 0.0
    for at in range(len(weights)):
        for a in range(width):
            centre[a] = centre[a] + weights[at] * xs[at][a]
        centre_y = centre_y + weights[at] * ys[at]
    for a in range(width):
        centre[a] = centre[a] / summed
    centre_y = centre_y / summed
    matrix = [[_RIDGE if a == c else 0.0 for c in range(width)] + [0.0] for a in range(width)]
    for at in range(len(weights)):
        dy = ys[at] - centre_y
        for a in range(width):
            da = xs[at][a] - centre[a]
            for c in range(width):
                matrix[a][c] = matrix[a][c] + weights[at] * da * (xs[at][c] - centre[c]) / summed
            matrix[a][width] = matrix[a][width] + weights[at] * da * dy / summed
    moment = [matrix[a][width] for a in range(width)]
    for a in range(width):
        pivot = matrix[a][a]
        for c in range(a, width + 1):
            matrix[a][c] = matrix[a][c] / pivot
        for other in range(width):
            if other == a:
                continue
            factor = matrix[other][a]
            for c in range(a, width + 1):
                matrix[other][c] = matrix[other][c] - factor * matrix[a][c]
    beta = tuple(matrix[a][width] for a in range(width))
    explained = 0.0
    for a in range(width):
        explained = explained + beta[a] * moment[a]
    left = 1.0 - explained
    sigma = math.sqrt(left if left > 0.0 else 0.0)
    return ImpliedSlope(tuple(used), beta, sigma if sigma > _LEAST_SPREAD else _LEAST_SPREAD, tuple(means))


def reading_ranks(index: "bytes | bytearray", width: int, child: "ChildBands") -> "tuple[Packed, int]":
    """Each arranged row's RANK among the column's readings, from its cell index (G16.2 step 2).

    The cell list holds band by band the cells holding a reading, sorted,
    then the others (G16.2 step 4), so a row whose index lies in the first
    `read[b]` places of an ORDERED band `b` holds the reading of rank
    `C_b + offset`, `C_b` the readings of the bands before it. Every other
    row takes the rank `K`, the count of readings (no reading). Handed
    back packed, with `K`.
    """
    starts: "list[int]" = []
    before: "list[int]" = []
    start = 0
    readings = 0
    for band in range(len(child.sizes)):
        starts += [start]
        before += [readings]
        start = start + child.sizes[band]
        if child.ordered[band]:
            readings = readings + child.read[band]
    count = len(index) // width
    ranks = packed(count, width_for(readings))
    band_of = [0 for _place in range(start)]
    band = 0
    for place in range(start):
        while band + 1 < len(starts) and place >= starts[band + 1]:
            band = band + 1
        band_of[place] = band
    for row in range(count):
        place = read_code(index, width, row)
        band = band_of[place]
        offset = place - starts[band]
        if child.ordered[band] and offset < child.read[band]:
            put(ranks, row, before[band] + offset)
        else:
            put(ranks, row, readings)
    return ranks, readings


def implied_latent(
    cells: "Packed | list[int]",
    slope: ImpliedSlope,
    ranks: "list[tuple[Packed, int]]",
    totals: "Packed | list[int]",
) -> "list[float]":
    """G16.2 step 2's latent order under an implied slope: `L = (sum_j beta_j (s_j - m_j) + sigma z) + mu_c`.

    `cells[r]` is row `r`'s parent cell, `ranks[j]` the `j`-th used
    parent's ranks and readings count (`reading_ranks`), `totals` the
    rows' hidden sums. `s_j = normal_score((2 rank + 1) / (2 K))` where
    the row holds a reading of parent `j`, its term nought otherwise;
    `m_j` the mean of `s_j` over the rows of the row's cell holding one,
    summed in row order and divided once (nought where none does); `mu_c`
    the cell's mean band score, nought where it has none. Summed in that
    order in binary64.
    """
    count = size_of(totals)
    latent = [0.0 for _row in range(count)]
    for at in range(len(slope.beta)):
        held, readings = ranks[at]
        beta = slope.beta[at]
        scores: "list[float | None]" = [None for _row in range(count)]
        sums: "dict[int, float]" = {}
        many: "dict[int, int]" = {}
        for row in range(count):
            rank = item(held, row)
            if rank >= readings:
                continue
            score = normal_score((2 * rank + 1) / (2 * readings))
            scores[row] = score
            cell = item(cells, row)
            sums[cell] = (sums[cell] if cell in sums else 0.0) + score
            many[cell] = (many[cell] if cell in many else 0) + 1
        mean = {cell: sums[cell] / many[cell] for cell in sums}
        for row in range(count):
            held_score = scores[row]
            if held_score is not None:
                latent[row] = latent[row] + beta * (held_score - mean[item(cells, row)])
        scores = []
    for row in range(count):
        cell = item(cells, row)
        centre = slope.means[cell] if cell < len(slope.means) else None
        value = latent[row] + slope.sigma * hidden_score(item(totals, row))
        latent[row] = value + (centre if centre is not None else 0.0)
    return latent


@dataclasses.dataclass(frozen=True)
class Slope:
    """One slope parent of a family (contract 4.6b.6), as G16.2 step 2 reads it.

    `codes` are its value codes on the arranged rows, `mapped` its
    reading map (1 where the row's cell holds a reading of its order),
    `beta` its published coefficient as the nearest binary64 value.
    """

    codes: "bytes | bytearray"
    mapped: "bytes | bytearray"
    beta: float


def slope_latent(cells: "list[int]", slopes: "list[Slope]", sigma: float, totals: "list[int]") -> "list[float]":
    """G16.2 step 2 where a family publishes slopes: `L = beta_1 (s_1 - m_1) + ... + sigma z`.

    Summed in that order in binary64. `m_p` is the mean of parent `p`'s
    codes over the rows of the row's parent cell whose reading map is
    set, an exact whole-number sum divided once; a row whose map is clear
    takes nought for that term, and so does every row of a cell where no
    row's map is set.
    """
    count = len(cells)
    means: "list[dict[int, float]]" = []
    for slope in slopes:
        sums: "dict[int, int]" = {}
        held: "dict[int, int]" = {}
        for row in range(count):
            if not slope.mapped[row]:
                continue
            cell = cells[row]
            sums[cell] = (sums[cell] if cell in sums else 0) + slope.codes[row]
            held[cell] = (held[cell] if cell in held else 0) + 1
        means += [{cell: sums[cell] / held[cell] for cell in sums}]
    latent: "list[float]" = [0.0 for _row in range(count)]
    for row in range(count):
        acc = 0.0
        first = True
        for at in range(len(slopes)):
            slope = slopes[at]
            cell = cells[row]
            term = 0.0
            if slope.mapped[row] and cell in means[at]:
                term = slope.beta * (slope.codes[row] - means[at][cell])
            acc = term if first else acc + term
            first = False
        latent[row] = acc + sigma * hidden_score(totals[row])
    return latent


@dataclasses.dataclass(frozen=True)
class ChildBands:
    """A family's child at its chain level, as the interface handed its cells (G16.0, G16.2 step 4).

    `sizes[b]` is the number of the column's cells band `b` holds (its
    band total in the twin), `read[b]` how many of them hold a reading of
    the band's order (listed first in the band's part of the CELL LIST,
    sorted by reading), and `ordered[b]` whether the band is ORDERED (it
    holds a value band) or SPREAD (contract 4.6b.2).
    """

    sizes: "tuple[int, ...]"
    read: "tuple[int, ...]"
    ordered: "tuple[bool, ...]"


@dataclasses.dataclass(frozen=True)
class Dealt:
    """One family dealt (G16.2 steps 3 and 4).

    `bands` holds each arranged row's band code at the child's chain
    level (`band_width` bytes a row, little-endian), `index` each row's
    cell index (`index_width` bytes a row, little-endian), and `table`
    the family's table as dealt, one row a parent cell.
    """

    bands: bytearray
    band_width: int
    index: bytearray
    index_width: int
    table: "tuple[tuple[int, ...], ...]"


def band_width(bands: int) -> int:
    """Bytes a row's band code takes (G16.1): the fewest holding the level's count of bands.

    One up to 255 bands, two up to 65,535, three up to 16,777,215, and so
    on, so every band code a level holds is written whole. The first
    build wrote two bytes above 255 bands whatever their count, and band
    65,536 of a level holding 65,537 (a long-tail label column of 65,537
    levels of 11 rows each, 720,907 rows) was written as band 0 (lane
    CHb's second repair, Codex's item 2).
    """
    return width_for(bands)


def index_width(cells: int) -> int:
    """Bytes a row's cell index takes (G16.2 step 4): three, or four above 16,777,215 cells."""
    return 4 if cells > THREE_BYTES else 3


@dataclasses.dataclass(frozen=True)
class Packed:
    """Whole numbers held `width` bytes each, little-endian, in one `bytearray` (G16.11's memory clause).

    What the walk keeps a row -- a hidden sum, a parent cell, an arranged
    row, a place in an order -- held as its bytes alone rather than as a
    Python whole number and a pointer to it (about forty bytes a row;
    repair 1 of lane CHb, item 4). `size_of`, `item` and `put` read and
    write one; every function here that takes rows takes a list too.
    """

    data: bytearray
    width: int


def width_for(top: int) -> int:
    """The fewest bytes, one to eight, holding every whole number from nought to ``top``."""
    width = 1
    while width < 8 and top >= (1 << (8 * width)):
        width = width + 1
    return width


def packed(count: int, width: int) -> Packed:
    """``count`` noughts of ``width`` bytes each."""
    return Packed(bytearray(count * width), width)


def size_of(numbers: "Packed | list[int]") -> int:
    """How many whole numbers a packed store or a list holds."""
    if isinstance(numbers, list):
        return len(numbers)
    return len(numbers.data) // numbers.width


def item(numbers: "Packed | list[int]", at: int) -> int:
    """The ``at``-th whole number of a packed store or a list."""
    if isinstance(numbers, list):
        return numbers[at]
    return read_code(numbers.data, numbers.width, at)


def put(numbers: Packed, at: int, value: int) -> None:
    """Writes ``value`` as the ``at``-th whole number of a packed store."""
    _write_code(numbers.data, numbers.width, at, value)


def read_code(data: "bytes | bytearray", width: int, row: int) -> int:
    """A row's whole number from a little-endian store of `width` bytes a row.

    The widths the walk uses are read in one expression each (the loop
    below gives the same number), since the walk reads a store several
    times a row for every family (repair 1 of lane CHb, item 4).
    """
    at = row * width
    if width == 1:
        return data[at]
    if width == 2:
        return data[at] | (data[at + 1] << 8)
    if width == 3:
        return data[at] | (data[at + 1] << 8) | (data[at + 2] << 16)
    value = 0
    for place in range(width):
        value = value | (data[at + place] << (8 * place))
    return value


def write_code(data: bytearray, width: int, row: int, value: int) -> None:
    """Writes `value` as a row's whole number in a little-endian store of `width` bytes a row (`read_code`'s inverse)."""
    _write_code(data, width, row, value)


def _write_code(data: bytearray, width: int, row: int, value: int) -> None:
    at = row * width
    if width == 1:
        data[at] = value & 255
        return
    if width == 3:
        data[at] = value & 255
        data[at + 1] = (value >> 8) & 255
        data[at + 2] = (value >> 16) & 255
        return
    for place in range(width):
        data[at + place] = (value >> (8 * place)) & 255


def _mark_spread(mask: bytearray, rows: int, taken: int) -> None:
    """Sets the bytes `spread_positions(rows, taken)` names, without holding the list."""
    for q in range(max(0, taken)):
        mask[((2 * q + 1) * rows) // (2 * taken)] = 1


def _grouped(
    order: "Packed | list[int]", codes: "Packed | list[int]", groups: int, width: int
) -> "tuple[Packed, list[int]]":
    """The rows of `order` grouped by `codes[row]`, each group in `order`'s order, and each group's start.

    A counting sort into a packed store of ``width`` bytes a row (G16.11's
    memory clause; repair 1 of lane CHb, item 4): group `g`'s rows are the
    places `starts[g]` up to `starts[g + 1]`.
    """
    count = size_of(order)
    starts = [0 for _group in range(groups + 1)]
    for at in range(count):
        code = item(codes, item(order, at))
        starts[code + 1] = starts[code + 1] + 1
    for group in range(groups):
        starts[group + 1] = starts[group + 1] + starts[group]
    filling = [starts[group] for group in range(groups)]
    rows = packed(count, width)
    for at in range(count):
        row = item(order, at)
        code = item(codes, row)
        put(rows, filling[code], row)
        filling[code] = filling[code] + 1
    return rows, starts


def _part(rows: Packed, start: int, end: int) -> Packed:
    """Places ``start`` up to ``end`` of a packed store, as a store of their own."""
    return Packed(rows.data[start * rows.width:end * rows.width], rows.width)


def deal(
    cells: "Packed | list[int]",
    cell_count: int,
    order: "Packed | list[int]",
    child: ChildBands,
    target: "tuple[tuple[int, ...], ...]",
) -> Dealt:
    """G16.2 steps 3 and 4 of one family, on the rows' parent cells and latent order.

    `cells[r]` is arranged row `r`'s parent cell (0 for a family with no
    parent), `order` the arranged rows sorted by `L` ascending, ties to
    the lower row number, and `target[c][b]` the rows parent cell `c`
    deals into band `b`. Step 3: inside each parent cell, each SPREAD band
    with a target above nought, in band order, takes its rows spread over
    the cell's rows not yet taken; the rest, in order, take the ORDERED
    bands in band order. Step 4: each band's rows over every cell, in
    order, take its cells: the cells holding no reading spread over them,
    the others the band's sorted cells in turn. Raises ValueError where a
    cell's targets do not sum to its rows or a band's rows to its cells
    (the target is not the family's, or the cells are not the child's).
    The rows of each parent cell and of each band are counting-sorted into
    packed stores, and every spread is a byte a row (G16.11; repair 1 of
    lane CHb, item 4); `cells` and `order` are packed stores or lists.
    """
    count = size_of(cells)
    bands = len(child.sizes)
    if size_of(order) != count or len(target) != cell_count:
        raise ValueError("one parent cell a row, one target row a cell")
    row_width = width_for(count - 1)
    by_cell, cell_starts = _grouped(order, cells, cell_count, row_width)
    code_width = band_width(bands)
    band_of = bytearray(count * code_width)
    dealt = [[0 for _band in range(bands)] for _cell in range(cell_count)]
    for cell in range(cell_count):
        wanted = target[cell]
        if len(wanted) != bands or sum(wanted) != cell_starts[cell + 1] - cell_starts[cell]:
            raise ValueError("a parent cell's targets do not sum to its rows")
        free = _part(by_cell, cell_starts[cell], cell_starts[cell + 1])
        for band in range(bands):
            taken = wanted[band]
            if child.ordered[band] or taken <= 0:
                continue
            held = size_of(free)
            chosen = bytearray(held)
            _mark_spread(chosen, held, taken)
            kept = packed(held - taken, row_width)
            at = 0
            for place in range(held):
                row = item(free, place)
                if chosen[place]:
                    _write_code(band_of, code_width, row, band)
                else:
                    put(kept, at, row)
                    at = at + 1
            free = kept
            dealt[cell][band] = taken
        at = 0
        for band in range(bands):
            if not child.ordered[band]:
                continue
            for place in range(at, at + wanted[band]):
                _write_code(band_of, code_width, item(free, place), band)
            at = at + wanted[band]
            dealt[cell][band] = wanted[band]
    by_cell = packed(0, row_width)
    by_band, band_starts = _grouped(order, Packed(band_of, code_width), bands, row_width)
    cell_total = sum(child.sizes)
    width = index_width(cell_total)
    index = bytearray(count * width)
    start = 0
    for band in range(bands):
        rows = _part(by_band, band_starts[band], band_starts[band + 1])
        held = size_of(rows)
        if held != child.sizes[band]:
            raise ValueError("a band's rows are not its cells")
        without = child.sizes[band] - child.read[band]
        spread = bytearray(held)
        _mark_spread(spread, held, without)
        took_read = 0
        took_without = 0
        for at in range(held):
            if spread[at]:
                _write_code(index, width, item(rows, at), start + child.read[band] + took_without)
                took_without = took_without + 1
            else:
                _write_code(index, width, item(rows, at), start + took_read)
                took_read = took_read + 1
        start = start + child.sizes[band]
    return Dealt(
        band_of,
        code_width,
        index,
        width,
        tuple(tuple(row) for row in dealt),
    )


def margins(table: "tuple[tuple[int, ...], ...] | list[list[int]]") -> "tuple[list[int], list[int]]":
    """A table's row totals and column totals."""
    rows = [sum(row) for row in table]
    columns = [sum(table[place][band] for place in range(len(table))) for band in range(len(table[0]) if table else 0)]
    return rows, columns


def needs_move(
    published: "tuple[tuple[int, ...], ...]", parent_counts: "list[int]", child_totals: "list[int]"
) -> bool:
    """G16.0's test: the published table is the target only where the twin's parent cells hold
    its row totals and the child's band totals its column totals."""
    rows, columns = margins(published)
    return rows != list(parent_counts) or columns != list(child_totals)


@dataclasses.dataclass(frozen=True)
class Target:
    """A family's target (G16.0): the published table, or its MOVED TABLE (G16.6).

    `moved` says which; `noughts` names each cell `(row, column)` of the
    moved table holding units where the published table holds nought.
    """

    table: "tuple[tuple[int, ...], ...]"
    moved: bool
    noughts: "tuple[tuple[int, int], ...]"


def target_of(
    published: "tuple[tuple[int, ...], ...]", parent_counts: "list[int]", child_totals: "list[int]"
) -> Target:
    """G16.0's target of a family: its published table, or else its moved table (G16.6)."""
    if not needs_move(published, parent_counts, child_totals):
        return Target(published, False, ())
    table = moved_table(published, parent_counts, child_totals)
    noughts = tuple(
        (place, band)
        for place in range(len(table))
        for band in range(len(table[place]))
        if published[place][band] == 0 and table[place][band] > 0
    )
    return Target(table, True, noughts)


def _cost(nought: int, distance_weight: int, published: int, value: int) -> int:
    """One cell's combined cost: units in a published nought, then distance, then square."""
    gap = value - published
    return nought * value + distance_weight * (gap if gap >= 0 else -gap) + gap * gap


def _heap_push(heap: "list[tuple[int, int]]", item: "tuple[int, int]") -> None:
    heap += [item]
    at = len(heap) - 1
    while at:
        parent = (at - 1) // 2
        if heap[parent] <= heap[at]:
            break
        heap[parent], heap[at] = heap[at], heap[parent]
        at = parent


def _heap_pop(heap: "list[tuple[int, int]]") -> "tuple[int, int]":
    top = heap[0]
    last = heap[len(heap) - 1]
    del heap[len(heap) - 1]
    if heap:
        heap[0] = last
        at = 0
        size = len(heap)
        while True:
            left = 2 * at + 1
            if left >= size:
                break
            child = left
            if left + 1 < size and heap[left + 1] < heap[left]:
                child = left + 1
            if heap[at] <= heap[child]:
                break
            heap[at], heap[child] = heap[child], heap[at]
            at = child
    return top


def moved_table(
    published: "tuple[tuple[int, ...], ...]", rows: "list[int]", columns: "list[int]"
) -> "tuple[tuple[int, ...], ...]":
    """G16.6's MOVED TABLE, exactly.

    Among the tables of whole numbers with row totals `rows` and column
    totals `columns`, the one that makes smallest, in this order: the
    units in cells the published table holds as nought; the summed
    distance to the published counts; the sum of the squared differences;
    and, last, among tables equal on the three, the greatest read in
    row-major order at the first place two differ.

    HOW. The three sums are one cost per cell, convex in the cell's
    count, so they are folded into one whole number with weights that
    keep their order (a unit in a nought outweighs any distance and any
    square; a unit of distance any square) and the table is a minimum
    cost flow from the published table, solved by successive shortest
    paths, one unit at a time, with Dijkstra's search on reduced costs.
    The final potentials then fix each cell to an interval of at most two
    counts (a cell's cost rises by at least 2 a unit more than it did a
    unit before, so no third count can tie), every optimal table lies in
    those intervals, and the greatest in row-major order is reached by
    raising each free cell in turn along an alternating cycle of later
    free cells, where one exists. Raises ValueError where the two totals
    differ in sum or a total is below nought.
    """
    depth = len(rows)
    width = len(columns)
    if sum(rows) != sum(columns) or any(total < 0 for total in rows) or any(total < 0 for total in columns):
        raise ValueError("the row and column totals of a moved table differ")
    if len(published) != depth or any(len(row) != width for row in published):
        raise ValueError("the published table and its totals differ in shape")
    if not depth or not width:
        return tuple(tuple(0 for _band in range(width)) for _row in range(depth))
    scale = sum(rows) + sum(sum(row) for row in published) + 1
    distance_weight = scale * scale + 1
    nought_weight = distance_weight * (scale + 1) + 1
    weight = [[nought_weight if published[i][j] == 0 else 0 for j in range(width)] for i in range(depth)]
    x = [[published[i][j] for j in range(width)] for i in range(depth)]

    def up(i: int, j: int) -> int:
        return _cost(weight[i][j], distance_weight, published[i][j], x[i][j] + 1) - _cost(
            weight[i][j], distance_weight, published[i][j], x[i][j]
        )

    def down(i: int, j: int) -> int:
        return _cost(weight[i][j], distance_weight, published[i][j], x[i][j]) - _cost(
            weight[i][j], distance_weight, published[i][j], x[i][j] - 1
        )

    # Nodes: rows 0 .. depth - 1, columns depth .. depth + width - 1.
    nodes = depth + width
    supply = [0 for _node in range(nodes)]
    for i in range(depth):
        supply[i] = rows[i] - sum(x[i])
    for j in range(width):
        supply[depth + j] = sum(x[i][j] for i in range(depth)) - columns[j]
    # A row node with supply above nought sends units out on forward arcs;
    # a column node above nought sends them back on backward arcs; each
    # below nought takes them in.
    potential = [0 for _node in range(nodes)]
    while any(left > 0 for left in supply):
        unseen = -1
        distance = [unseen for _node in range(nodes)]
        before = [-1 for _node in range(nodes)]
        done = [False for _node in range(nodes)]
        heap: "list[tuple[int, int]]" = []
        for node in range(nodes):
            if supply[node] > 0:
                distance[node] = 0
                _heap_push(heap, (0, node))
        while heap:
            reached, node = _heap_pop(heap)
            if done[node] or reached != distance[node]:
                continue
            done[node] = True
            if node < depth:
                for j in range(width):
                    step = up(node, j) + potential[node] - potential[depth + j]
                    if step < 0:
                        raise ValueError("internal: a reduced cost below nought")
                    found = reached + step
                    target = depth + j
                    if distance[target] == unseen or found < distance[target]:
                        distance[target] = found
                        before[target] = node
                        _heap_push(heap, (found, target))
            else:
                j = node - depth
                for i in range(depth):
                    if x[i][j] <= 0:
                        continue
                    step = -down(i, j) + potential[node] - potential[i]
                    if step < 0:
                        raise ValueError("internal: a reduced cost below nought")
                    found = reached + step
                    if distance[i] == unseen or found < distance[i]:
                        distance[i] = found
                        before[i] = node
                        _heap_push(heap, (found, i))
        sink = -1
        for node in range(nodes):
            if supply[node] < 0 and done[node] and (sink < 0 or distance[node] < distance[sink]):
                sink = node
        if sink < 0:
            raise ValueError("internal: no unit can reach a node that takes it")
        reach = distance[sink]
        for node in range(nodes):
            potential[node] = potential[node] + (distance[node] if done[node] and distance[node] < reach else reach)
        node = sink
        while before[node] >= 0:
            came = before[node]
            if came < depth:
                x[came][node - depth] = x[came][node - depth] + 1
            else:
                x[node][came - depth] = x[node][came - depth] - 1
            node = came
        supply[node] = supply[node] - 1
        supply[sink] = supply[sink] + 1
    # Every optimal table: each cell inside the interval its potentials
    # allow (at most two counts), the margins met.
    low = [[0 for _j in range(width)] for _i in range(depth)]
    high = [[0 for _j in range(width)] for _i in range(depth)]
    for i in range(depth):
        for j in range(width):
            slope = potential[depth + j] - potential[i]
            low[i][j] = x[i][j]
            high[i][j] = x[i][j]
            if x[i][j] > 0 and down(i, j) == slope:
                low[i][j] = x[i][j] - 1
            if up(i, j) == slope:
                high[i][j] = x[i][j] + 1
    fixed = [[low[i][j] == high[i][j] for j in range(width)] for i in range(depth)]
    for i in range(depth):
        for j in range(width):
            if fixed[i][j]:
                continue
            fixed[i][j] = True
            if x[i][j] == high[i][j]:
                continue
            path = _raising_cycle(x, low, high, fixed, i, j)
            if path:
                x[i][j] = x[i][j] + 1
                for at in range(len(path)):
                    row, band = path[at]
                    x[row][band] = x[row][band] + (-1 if at % 2 == 0 else 1)
    return tuple(tuple(row) for row in x)


def _raising_cycle(
    x: "list[list[int]]",
    low: "list[list[int]]",
    high: "list[list[int]]",
    fixed: "list[list[bool]]",
    row: int,
    band: int,
) -> "list[tuple[int, int]]":
    """The cells an alternating cycle through `(row, band)` lowers and raises, or [] where none.

    From column `band`, a free cell of that column at its high count is
    lowered, then a free cell of that cell's row at its low count raised,
    and so on, until a lowered cell lies in `row`; only cells not yet
    fixed take part, so no earlier cell of row-major order moves. Found
    by a breadth-first search in fixed order. The list alternates lowered
    and raised cells, a lowered one first and last.
    """
    depth = len(x)
    seen_rows = [False for _i in range(depth)]
    queue: "list[tuple[int, list[tuple[int, int]]]]" = [(band, [])]
    head = 0
    seen_columns = {band: True}
    while head < len(queue):
        column, path = queue[head]
        head = head + 1
        for i in range(depth):
            if seen_rows[i] or fixed[i][column] or x[i][column] <= low[i][column]:
                continue
            seen_rows[i] = True
            lowered = path + [(i, column)]
            if i == row:
                return lowered
            for j in range(len(x[i])):
                if j in seen_columns or fixed[i][j] or x[i][j] >= high[i][j]:
                    continue
                seen_columns[j] = True
                queue += [(j, lowered + [(i, j)])]
    return []


def _decimal_parts(text: str) -> "tuple[int, int] | None":
    """A plain decimal text as `(value scaled to whole figures, places)`, or None."""
    if not isinstance(text, str):
        raise ValueError("a decimal text")
    negative = text.startswith("-")
    body = text[1:] if negative else text
    pieces = body.split(".")
    if len(pieces) > 2:
        return None
    whole = pieces[0]
    fraction = pieces[1] if len(pieces) == 2 else ""
    if not _figures(whole) or (len(pieces) == 2 and not _figures(fraction)):
        return None
    value = int(whole + fraction)
    return (-value if negative else value), len(fraction)


def _figures(text: str) -> bool:
    """Whether a text is one or more of the figures 0 to 9."""
    if not isinstance(text, str):
        raise ValueError("a text")
    return bool(text) and all("0" <= letter <= "9" for letter in text)


def added_decimal(first: str, second: str) -> "str | None":
    """`A + D` on two plain decimal texts, exactly, with the larger number of places (G16.2 step 5).

    A text is an optional `-`, figures, and optionally a point and
    figures. None where either is not one (another layout is lane MR's).
    """
    left = _decimal_parts(first)
    right = _decimal_parts(second)
    if left is None or right is None:
        return None
    places = max(left[1], right[1])
    total = left[0] * 10 ** (places - left[1]) + right[0] * 10 ** (places - right[1])
    sign = "-" if total < 0 else ""
    figures = str(-total if total < 0 else total)
    if not places:
        return sign + figures
    figures = "0" * max(0, places + 1 - len(figures)) + figures
    return sign + figures[: len(figures) - places] + "." + figures[len(figures) - places:]
