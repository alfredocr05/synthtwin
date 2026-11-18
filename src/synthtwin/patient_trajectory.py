"""A PATIENT'S OWN TRAJECTORY: each repeated number column's level, slope and serial correlation over a patient's visits as rounded, floor-gated moments (contract 4.6c.15; lane GRb2-c, plan P4-D491 part c).

NOT IN FORCE ON A SHIPPED RUN: like the rest of the patient layer, this
module is reached only where `grain` stands, which no shipped command
publishes while `cli._PATIENT_LAYER_SHIPPED` is off.

WHY (the owner's priority order of 2026-11-10, and his "I want statistical
reliability!"): the patient layer keeps the people, the rows a person, the
order of the visits and what stays fixed within a person, but a repeated
number column was dealt with no person term wherever its own-mean column
does not pass the floor (most tables of 20,000 rows and 1,000 people), and
with no slope or serial term anywhere: mixed models with a random slope,
trend by group and models of serial correlation read noise on the twin.
The counted objects that would carry them (bands of people's own means,
tables of trend cells) need cells of people at the floor, and the counts
they publish can stand against each other at 1 to 10 (lane GRb2 part a,
withdrawn). Here no count is published at all: rule B (the owner's answer
"B" of 2026-11-02) publishes ROUNDED MOMENTS over at least the floor of
people, and that is all an entry holds.

WHAT AN ENTRY HOLDS (`grain.trajectory`, one entry a column), every number
on the column's own scale (`scale`: LINEAR, its readings standardized, for a
date column and for a number column whose published quantile skew is under
1/5; NORMAL, each present reading's mid-rank among the column's readings
through the shared normal quantile, for a skewed one), over a time axis `t`:
the row's POSITION within its patient (0 for the first row, in the order the
layer reads them), or the YEARS since the patient's first dated row where
the layer's position column is a dealt date and each patient's own line
leaves less about it on the years than on the positions (a date column's
own entry reads positions):

    z = shift(x) + b0 + (trend + trend(x) + b1) t + (curve + curve(x)) t^2 + e

- `trend` and `curve`: the within-patient change a unit of time and its
  bend, for patients in the first band of every grouping column; `by`: for a
  patient-fixed column of the patient chain, at the finest of its published
  levels whose every band holds enough patients, each band's `shift` of the
  level, change of the `trend` and of the `curve` against its first band
  (the trend BY GROUP: an arm, a clinic, an age band);
- `level_sd`, `slope_sd` and `corr`: the spread of a patient's own level
  (at its first position) and own slope beyond the fixed part, and their
  correlation (the random intercept and slope);
- `noise_sd` and `lag1`: what is left within a patient, first-order
  autoregressive from one position to the next (the serial correlation),
  on either axis.

HOW THEY ARE MEASURED (the producer, `measured`): the fixed part by least
squares over every reading; on what is left, the lag-0, lag-1 and lag-2
products of the differences between neighbouring positions within a patient
give the lag-one coefficient `a` free of the levels and slopes (`E d d = s1 +
2 s (1 - a)`, `s1 - s (1 - a)^2`, `s1 - s a (1 - a)^2` at lags 0, 1, 2, `s`
the noise variance, `s1` the slope variance) where their lag-two term is
steady, else the grid of `LAG_GRID` chooses it; at that coefficient the
products of two residuals of one patient among its first `LEVEL_ROWS`
positions, each patient weighing one, give the level and slope variances,
their covariance and the noise variance together; then the fixed part again,
each patient weighing as its own estimates' variance, and the random part
again. Each is a mean of per-person derived numbers over at least
`FLOOR_TIMES` times the floor of patients, a moment of rule B (LANE GRb2
RULINGS 1, D3 and D4), and is rounded half away from nought to its stated
places, far below its sampling error at the table floor; an entry, and each
band of a grouping column, stands only where its patients reach that number;
NO COUNT OF PEOPLE OR ROWS IS PUBLISHED, so no published count can stand
against another.

HOW THE TWIN READS THEM (the generator, `scores`): each patient draws its
own level and slope from two hidden scores (the slope's correlated with the
level as published; the level is the patient's own-mean score where an
own-mean column parents the column's row family, so its band still holds),
and each of its rows an innovation of the serial term; the row's score is
the form above, and the column's cells are dealt to the rows in the order of
their scores (inside the row family's published cells where one stands), so
every published count and the column's own values stand exactly as before.

ARITHMETIC. Readings compare as exact fractions; every other operation is
binary64 `+ - * /` and `sqrt`, each rounded once in the order written, with
the normal quantile the shared module's (`chain_walk.normal_score`), so the
same table gives the same entry byte for byte on every machine. No I/O.
"""

import dataclasses
import fractions
import math

from synthtwin import chain_moments, chain_walk, errors

# The key `grain` holds the entries under, present only where one stands.
TRAJECTORY_KEY = "trajectory"
# The time axes: a row's position within its patient (a dealt date column's own
# entry, and every entry of a table whose position column is no date), and the
# years since the patient's first dated row on the layer's position column.
AXIS_POSITION = "position"
AXIS_YEARS = "years"
ENTRY_KEYS = ("axis", "by", "column", "corr", "curve", "lag1", "level_sd", "noise_sd", "scale", "slope_sd", "trend")
# The scales a column's readings are read on: LINEAR, the readings standardized
# (a date column's, and a number column's whose published quantile skew is
# under 1/5, `chain_moments.SKEW_CUT`), else NORMAL, the normal scores of their
# mid-ranks (a skewed column, whose tail would else outweigh its body).
SCALE_LINEAR = "linear"
SCALE_NORMAL = "normal"
BY_KEYS = ("column", "curve", "level", "shift", "trend")
# A year in seconds (365.25 days), the years axis's unit.
SECONDS_A_YEAR = 31557600
# The roles an entry's column may hold (`chain_rules.NUMBER_ROLES`, and the date
# role of a dealt date column), written here so the loader reads them alone.
NUMBER_ROLES = ("count", "continuous", "affixed_number", "joined_numbers", "numbers_with_labels")
DATE_ROLE = "datetime"
# The levels a grouping column may be read at, finest first: an entry reads
# each grouping column at the finest of its published levels whose every band
# holds enough patients (`FLOOR_TIMES` times the floor with two readings or
# more), so a clinic of twelve values or an age of twelve bands is read whole
# wherever its patients allow.
LEVELS = ("L0", "L1", "L2")
LEVEL_PLACE = {"L0": 0, "L1": 1, "L2": 2}
# The places each published moment is rounded to, half away from nought.
PLACES = {"corr": 3, "curve": 6, "lag1": 3, "level_sd": 3, "noise_sd": 3, "slope_sd": 4, "trend": 4, "shift": 4}
# The bounds a loader holds every moment to (S35).
CORR_MOST = fractions.Fraction(95, 100)
LAG_MOST = fractions.Fraction(95, 100)
LAG_LEAST = fractions.Fraction(-90, 100)
SIZE_MOST = fractions.Fraction(10)
# The first positions of a patient its level and slope moments read, in pairs
# (the work stays linear in the rows).
LEVEL_ROWS = 32
# A patient's noise shares are summed exactly over its positions up to this
# many readings, by their long-run factor beyond.
EXACT_POSITIONS = 64
# An entry, and each band of a grouping column, stands where at least this
# many times the floor of patients hold the rows its moments read.
FLOOR_TIMES = 2
# The words the walk draws for one entry: two hidden scores a patient (three
# words each), one a row.
PATIENT_WORDS = 6
ROW_WORDS = 3


def _broken(where: str, detail: str) -> errors.ProfileError:
    return errors.ProfileError(errors.profile_chain_broken("S35", where, detail))


def rounded_text(value: float, places: int) -> str:
    """`value` rounded half away from nought to `places` decimals, written as a decimal (no exponent, no trailing nought)."""
    exact = fractions.Fraction(value) * (10 ** places)
    whole = abs(exact.numerator) // exact.denominator
    if 2 * (abs(exact.numerator) - whole * exact.denominator) >= exact.denominator:
        whole += 1
    negative = exact < 0 and whole != 0
    integer, rest = divmod(whole, 10 ** places)
    text = f"{'-' if negative else ''}{integer}"
    shown = places
    while rest and rest % 10 == 0:
        rest = rest // 10
        shown -= 1
    if rest:
        text += "." + f"{rest:0{shown}d}"
    return text


def _bounded(value: float, most: fractions.Fraction, least: "fractions.Fraction | None" = None) -> float:
    top = float(most)
    bottom = -top if least is None else float(least)
    return top if value > top else (bottom if value < bottom else value)


# -- the producer --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class Grouping:
    """A patient-fixed column of the patient chain the entry may read: its name, each patient's band at one level, that level's band count, and the level."""

    name: str
    bands: "list[int]"
    count: int
    level: int = 2


def grouping_levels(name: str, codes: "tuple[list[int], list[int], list[int]]", counts: "tuple[int, int, int]") -> "list[Grouping]":
    """A patient-fixed column offered at each of its levels, finest first (`measured` keeps the finest that holds)."""
    return [Grouping(name, list(codes[level]), counts[level], level) for level in range(3)]


def linear_scores(readings: "list[fractions.Fraction | None]") -> "list[float | None]":
    """Each present reading standardized: less the least reading exactly, then less the mean and over the sample spread in binary64 in the order written; all None where fewer than two readings or no spread."""
    present = [k for k in range(len(readings)) if readings[k] is not None]
    out: "list[float | None]" = [None for _k in readings]
    if len(present) < 2:
        return out
    least = readings[present[0]]
    for k in present:
        value = readings[k]
        if value is not None and least is not None and value < least:
            least = value
    values: "list[float]" = []
    for k in present:
        value = readings[k]
        values += [float(value - least) if value is not None and least is not None else 0.0]
    total = 0.0
    for shifted in values:
        total = total + shifted
    mean = total / len(values)
    squares = 0.0
    for shifted in values:
        squares = squares + (shifted - mean) * (shifted - mean)
    spread = math.sqrt(squares / (len(values) - 1))
    if spread <= 0.0:
        return out
    for at in range(len(present)):
        out[present[at]] = (values[at] - mean) / spread
    return out


def normal_scores(readings: "list[fractions.Fraction | None]") -> "list[float | None]":
    """Each present reading's normal score: its mid-rank among the readings, `(rank - 1/2) / n`, through the shared quantile."""
    present = [k for k in range(len(readings)) if readings[k] is not None]
    count = len(present)
    out: "list[float | None]" = [None for _k in readings]
    if count == 0:
        return out
    order = [k for _reading, k in sorted((readings[k], k) for k in present)]
    at = 0
    while at < count:
        end = at
        while end + 1 < count and readings[order[end + 1]] == readings[order[at]]:
            end += 1
        score = chain_walk.normal_score(((at + end) / 2.0 + 0.5) / count)
        for place in range(at, end + 1):
            out[order[place]] = score
        at = end + 1
    return out


def _solved(matrix: "list[list[float]]", right: "list[float]") -> "list[float] | None":
    """The least-squares normal equations solved by Gaussian elimination with partial pivoting, or None where they are singular."""
    size = len(right)
    a = [list(matrix[i]) + [right[i]] for i in range(size)]
    scale = 0.0
    for i in range(size):
        scale = max(scale, abs(a[i][i]))
    if scale <= 0.0:
        return None
    for column in range(size):
        pivot = column
        for row in range(column + 1, size):
            if abs(a[row][column]) > abs(a[pivot][column]):
                pivot = row
        if abs(a[pivot][column]) <= 1e-10 * scale:
            return None
        a[column], a[pivot] = a[pivot], a[column]
        for row in range(column + 1, size):
            factor = a[row][column] / a[column][column]
            if factor != 0.0:
                for k in range(column, size + 1):
                    a[row][k] = a[row][k] - factor * a[column][k]
    out = [0.0 for _i in range(size)]
    for row in range(size - 1, -1, -1):
        total = a[row][size]
        for k in range(row + 1, size):
            total = total - a[row][k] * out[k]
        out[row] = total / a[row][row]
    return out


def _runs(positions: "list[bool]") -> int:
    """The longest run of consecutive present positions."""
    best = 0
    run = 0
    for present in positions:
        run = run + 1 if present else 0
        best = max(best, run)
    return best


def _design(groupings: "list[Grouping]", patient: int) -> "list[float]":
    """A patient's design `w`: 1, then one indicator for each band but the first of each grouping column."""
    out = [1.0]
    for one in groupings:
        for band in range(1, one.count):
            out += [1.0 if one.bands[patient] == band else 0.0]
    return out


def _fixed_part(lines: "list[list[tuple[int, float, float]]]", groupings: "list[Grouping]") -> "list[float] | None":
    """The fixed part's coefficients by least squares: for each element of `w`, its level shift, its change a unit of time and its curve."""
    width = 1 + sum(one.count - 1 for one in groupings)
    size = 3 * width
    matrix = [[0.0 for _b in range(size)] for _a in range(size)]
    right = [0.0 for _a in range(size)]
    for patient in range(len(lines)):
        held = lines[patient]
        if not held:
            continue
        sums = [0.0, 0.0, 0.0, 0.0, 0.0]
        ys = [0.0, 0.0, 0.0]
        for _position, t, score in held:
            square = t * t
            sums[0] = sums[0] + 1.0
            sums[1] = sums[1] + t
            sums[2] = sums[2] + square
            sums[3] = sums[3] + square * t
            sums[4] = sums[4] + square * square
            ys[0] = ys[0] + score
            ys[1] = ys[1] + t * score
            ys[2] = ys[2] + square * score
        w = _design(groupings, patient)
        for a in range(width):
            if w[a] == 0.0:
                continue
            for ta in range(3):
                right[3 * a + ta] = right[3 * a + ta] + ys[ta]
            for b in range(width):
                if w[b] == 0.0:
                    continue
                for ta in range(3):
                    for tb in range(3):
                        matrix[3 * a + ta][3 * b + tb] = matrix[3 * a + ta][3 * b + tb] + sums[ta + tb]
    return _solved(matrix, right)


def _fitted(beta: "list[float]", w: "list[float]", t: float) -> float:
    total = 0.0
    for a in range(len(w)):
        if w[a] != 0.0:
            total = total + beta[3 * a] + beta[3 * a + 1] * t + beta[3 * a + 2] * t * t
    return total


@dataclasses.dataclass(frozen=True)
class Random:
    """The random part as measured: level and slope variances, their covariance, the noise variance and the lag-one coefficient."""

    level: float
    slope: float
    both: float
    noise: float
    lag: float


def _powers(lag: float, count: int) -> "list[float]":
    """`lag ** h` for `h` in `0 .. count - 1`, each the last times `lag`."""
    out = [1.0]
    for _h in range(1, count):
        out += [out[-1] * lag]
    return out


def _random_part(residuals: "list[list[float | None]]", times: "list[list[float]]") -> "Random | None":
    """The lag-one coefficient and the noise variance from the differences, then the level and slope variances and their covariance from the products.

    The differences `d` between neighbouring positions of one patient hold
    no level and, at lags 0, 1 and 2, `E d d = s1 g + 2 s (1 - a)`, `s1 g -
    s (1 - a)^2` and `s1 g - s a (1 - a)^2` (`g` the product of the time
    steps, one a position on the position axis): the first less the second
    and the third less the second read `s (1 - a)(3 - a)` and `s (1 - a)^3`,
    exactly on the position axis and up to the steps' spread on the years
    axis, which give `a` and `s`. The products of two residuals of one patient
    at positions `j <= k` among its first `LEVEL_ROWS` then hold `E r_j r_k =
    s0 + s01 (t_j + t_k) + s1 t_j t_k + s a^(k - j)`: least squares of the
    products less the noise part on `1`, `t_j + t_k` and `t_j t_k`, each pair
    weighing one over its patient's readings there, give `s0`, `s01`, `s1`.
    """
    m0 = m1 = m2 = 0.0
    q1 = q2 = 0.0
    c0 = c1 = c2 = 0
    for line in residuals:
        steps: "list[float | None]" = []
        for j in range(len(line) - 1):
            first, second = line[j], line[j + 1]
            steps += [second - first if first is not None and second is not None else None]
        for j in range(len(steps)):
            d = steps[j]
            if d is None:
                continue
            m0 = m0 + d * d
            c0 += 1
            if j + 1 < len(steps):
                after = steps[j + 1]
                if after is not None:
                    m1 = m1 + d * after
                    q1 = q1 + d * after * d * after
                    c1 += 1
            if j + 2 < len(steps):
                later = steps[j + 2]
                if later is not None:
                    m2 = m2 + d * later
                    q2 = q2 + d * later * d * later
                    c2 += 1
    if c0 == 0 or c1 == 0 or c2 == 0:
        return None
    mean0 = m0 / c0
    mean1 = m1 / c1
    mean2 = m2 / c2
    top = mean0 - mean1
    bottom = mean2 - mean1
    # The lag-two term's own sampling error against its size: where it is
    # small the differences read the lag coefficient, else the products do.
    spread_two = q1 / c1 - mean1 * mean1
    spread_three = q2 / c2 - mean2 * mean2
    error = math.sqrt(max(0.0, spread_two / c1 + spread_three / c2))
    steady = top > 0.0 and bottom > 0.0 and top > bottom and error <= DIFFERENCE_ERROR_MOST * bottom
    if top <= 0.0:
        lag = 0.0
    elif bottom <= 0.0:
        lag = float(LAG_MOST)
    else:
        ratio = top / bottom
        if ratio <= 1.0:
            lag = float(LAG_LEAST)
        else:
            lag = ((2.0 * ratio - 1.0) - math.sqrt(8.0 * ratio + 1.0)) / (2.0 * ratio)
    lag = _bounded(lag, LAG_MOST, LAG_LEAST)
    noise = top / ((1.0 - lag) * (3.0 - lag)) if top > 0.0 else 0.0
    # THE PRODUCTS, gathered by lag: for each lag `h` the weighted sums of 1,
    # `s = t_j + t_k`, `p = t_j t_k`, their products, and of the product `y`
    # of the two residuals with each, so every lag coefficient on the grid
    # reads the same sums.
    sums = [[0.0 for _part in range(10)] for _h in range(LEVEL_ROWS)]
    squares = 0.0
    for patient in range(len(residuals)):
        line = residuals[patient]
        clock = times[patient]
        held: "list[tuple[int, float, float]]" = []
        for j in range(min(len(line), LEVEL_ROWS)):
            value = line[j]
            if value is not None:
                held += [(j, clock[j], value)]
        if not held:
            continue
        weight = 1.0 / len(held)
        for first in range(len(held)):
            j, tj, rj = held[first]
            for second in range(first, len(held)):
                k, tk, rk = held[second]
                y = rj * rk
                both_t = tj + tk
                product = tj * tk
                line_sums = sums[k - j]
                line_sums[0] = line_sums[0] + weight
                line_sums[1] = line_sums[1] + weight * both_t
                line_sums[2] = line_sums[2] + weight * product
                line_sums[3] = line_sums[3] + weight * both_t * both_t
                line_sums[4] = line_sums[4] + weight * both_t * product
                line_sums[5] = line_sums[5] + weight * product * product
                line_sums[6] = line_sums[6] + weight * y
                line_sums[7] = line_sums[7] + weight * y * both_t
                line_sums[8] = line_sums[8] + weight * y * product
                squares = squares + weight * y * y
    found = _on_the_grid(sums, squares, (_rounded_lag(lag),) if steady else LAG_GRID)
    if found is not None:
        return found
    # No point of the grid gives every variance its sign: the lag and the noise
    # stand as the differences read them, and the products give the rest.
    matrix = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
    right = [0.0, 0.0, 0.0]
    powers = _powers(lag, LEVEL_ROWS)
    for h in range(LEVEL_ROWS):
        line_sums = sums[h]
        totals = ((line_sums[0], line_sums[1], line_sums[2]), (line_sums[1], line_sums[3], line_sums[4]), (line_sums[2], line_sums[4], line_sums[5]))
        crossed = (line_sums[6] - noise * powers[h] * line_sums[0], line_sums[7] - noise * powers[h] * line_sums[1], line_sums[8] - noise * powers[h] * line_sums[2])
        for a in range(3):
            right[a] = right[a] + crossed[a]
            for b in range(3):
                matrix[a][b] = matrix[a][b] + totals[a][b]
    solved = _solved(matrix, right)
    if solved is None:
        return None
    return _signed(solved[0], solved[1], solved[2], noise, lag)


# The lag coefficients the products are read at: -0.90 to 0.95 by hundredths.
LAG_GRID = tuple(fractions.Fraction(step, 100) for step in range(-90, 96))
# The differences read the lag coefficient where the lag-two term's sampling
# error is at most this share of its size (moderate lags and noise); else the
# products choose it on the grid (high lags, or a loud noise beside a small
# level), each by its smaller spread on the lane's invented tables.
DIFFERENCE_ERROR_MOST = 0.2


def _rounded_lag(lag: float) -> fractions.Fraction:
    """The differences' lag coefficient at the grid's hundredths, half away from nought."""
    return fractions.Fraction(rounded_text(lag, 2))


def _signed(level: float, both: float, slope: float, noise: float, lag: float) -> Random:
    """The random part with each variance at nought or above and the covariance inside its bound."""
    if slope < 0.0:
        slope = 0.0
    if level < 0.0:
        level = 0.0
    most = float(CORR_MOST) * math.sqrt(level * slope)
    both = most if both > most else (-most if both < -most else both)
    return Random(level, slope, both, noise, lag)


def _on_the_grid(sums: "list[list[float]]", squares: float, grid: "tuple[fractions.Fraction, ...]") -> "Random | None":
    """The products read jointly: at each lag coefficient `a` of `grid`, least squares of `y` on `1`, `s`, `p` and
    `a^h`; the point of least residual sum among those whose noise variance is above nought and whose level and slope
    variances are not below it (the first of equal sums). None where no point qualifies."""
    best: "tuple[float, Random] | None" = None
    for point in grid:
        lag = float(point)
        powers = _powers(lag, LEVEL_ROWS)
        matrix = [[0.0 for _b in range(4)] for _a in range(4)]
        right = [0.0, 0.0, 0.0, 0.0]
        for h in range(LEVEL_ROWS):
            line_sums = sums[h]
            power = powers[h]
            row = (line_sums[0], line_sums[1], line_sums[2], power * line_sums[0])
            totals = (
                (line_sums[0], line_sums[1], line_sums[2], power * line_sums[0]),
                (line_sums[1], line_sums[3], line_sums[4], power * line_sums[1]),
                (line_sums[2], line_sums[4], line_sums[5], power * line_sums[2]),
                (row[3], power * line_sums[1], power * line_sums[2], power * power * line_sums[0]),
            )
            crossed = (line_sums[6], line_sums[7], line_sums[8], power * line_sums[6])
            for a in range(4):
                right[a] = right[a] + crossed[a]
                for b in range(4):
                    matrix[a][b] = matrix[a][b] + totals[a][b]
        solved = _solved(matrix, right)
        if solved is None:
            continue
        level, both, slope, noise = solved
        if noise <= 0.0 or level < 0.0 or slope < 0.0:
            continue
        residual = squares
        for a in range(4):
            residual = residual - solved[a] * right[a]
        if best is None or residual < best[0]:
            best = (residual, _signed(level, both, slope, noise, lag))
    return None if best is None else best[1]


def _spread(held: "list[tuple[int, float]]", centre: float, powers: "list[float]", lag: float) -> "tuple[float, float]":
    """For one patient's readings `(position, time)`: the noise's share in the variance of its least-squares slope on time, and in that of its mean (each times the noise variance).

    Exact sums over every pair of readings up to `EXACT_POSITIONS`
    readings, the long-run factor `(1 + a) / (1 - a)` beyond.
    """
    count = len(held)
    sxx = 0.0
    for _j, t in held:
        sxx = sxx + (t - centre) * (t - centre)
    if count > EXACT_POSITIONS:
        factor = (1.0 + lag) / (1.0 - lag)
        return (factor / sxx if sxx > 0.0 else 0.0), factor / count
    slope_sum = 0.0
    mean_sum = 0.0
    for first, t_first in held:
        for second, t_second in held:
            gap = first - second if first >= second else second - first
            power = powers[gap] if gap < len(powers) else 0.0
            slope_sum = slope_sum + (t_first - centre) * (t_second - centre) * power
            mean_sum = mean_sum + power
    return (slope_sum / (sxx * sxx) if sxx > 0.0 else 0.0), mean_sum / (count * count)


def _weighted_fixed_part(
    lines: "list[list[tuple[int, float, float]]]", groupings: "list[Grouping]", found: Random, curves: "list[float]"
) -> "list[float] | None":
    """The fixed part again, each patient weighing as its own estimates' variance under the random part found.

    The curve stays the first pass's (`curves`, one an element of `w`); the
    changes a unit of time by least squares on each patient's own slope of
    its readings less the curve, weighed one over `s1 + s q`; then the
    levels on each patient's mean less the change times its mean time and
    the curve, weighed one over `s0 + 2 s01 m + s1 m^2 + s u` (`q` and `u`
    the noise's shares, `m` the mean time). Returns the coefficients as
    `_fixed_part` writes them, or None where either system is singular.
    """
    width = 1 + sum(one.count - 1 for one in groupings)
    powers = _powers(found.lag, 2 * EXACT_POSITIONS + 1)
    slopes = [[0.0 for _b in range(width)] for _a in range(width)]
    slope_right = [0.0 for _a in range(width)]
    kept: "list[tuple[list[float], float, float, float]]" = []
    for patient in range(len(lines)):
        held = lines[patient]
        if not held:
            continue
        w = _design(groupings, patient)
        curve = 0.0
        for a in range(width):
            if w[a] != 0.0:
                curve = curve + curves[a]
        count = len(held)
        mean_y = 0.0
        mean_t = 0.0
        for _j, t, value in held:
            mean_y = mean_y + value - curve * t * t
            mean_t = mean_t + t
        mean_y = mean_y / count
        mean_t = mean_t / count
        q, u = _spread([(j, t) for j, t, _value in held], mean_t, powers, found.lag)
        kept += [(w, mean_y, mean_t, u)]
        if count < 2 or q <= 0.0:
            continue
        sxx = 0.0
        sxy = 0.0
        for _j, t, value in held:
            sxx = sxx + (t - mean_t) * (t - mean_t)
            sxy = sxy + (t - mean_t) * (value - curve * t * t - mean_y)
        if sxx <= 0.0:
            continue
        variance = found.slope + found.noise * q
        weight = 1.0 / variance if variance > 0.0 else 0.0
        own = sxy / sxx
        for a in range(width):
            if w[a] == 0.0:
                continue
            slope_right[a] = slope_right[a] + weight * own
            for b in range(width):
                if w[b] != 0.0:
                    slopes[a][b] = slopes[a][b] + weight
    changes = _solved(slopes, slope_right)
    if changes is None:
        return None
    levels = [[0.0 for _b in range(width)] for _a in range(width)]
    level_right = [0.0 for _a in range(width)]
    for w, mean_y, mean_t, u in kept:
        change = 0.0
        for a in range(width):
            if w[a] != 0.0:
                change = change + changes[a]
        variance = found.level + 2.0 * found.both * mean_t + found.slope * mean_t * mean_t + found.noise * u
        weight = 1.0 / variance if variance > 0.0 else 0.0
        target = mean_y - change * mean_t
        for a in range(width):
            if w[a] == 0.0:
                continue
            level_right[a] = level_right[a] + weight * target
            for b in range(width):
                if w[b] != 0.0:
                    levels[a][b] = levels[a][b] + weight
    shifts = _solved(levels, level_right)
    if shifts is None:
        return None
    out: "list[float]" = []
    for a in range(width):
        out += [shifts[a], changes[a], curves[a]]
    return out


def _residuals(lines: "list[list[float | None]]", times: "list[list[float]]", beta: "list[float]", groupings: "list[Grouping]") -> "list[list[float | None]]":
    out: "list[list[float | None]]" = []
    for patient in range(len(lines)):
        w = _design(groupings, patient)
        line = lines[patient]
        clock = times[patient]
        out += [[None if line[j] is None else line[j] - _fitted(beta, w, clock[j]) for j in range(len(line))]]  # type: ignore[operator]
    return out


def measured(
    name: str,
    readings: "list[fractions.Fraction | None]",
    patient_rows: "list[list[int]]",
    groupings: "list[Grouping]",
    floor: int,
    years: "list[float | None] | None" = None,
    linear: bool = False,
) -> "dict[str, object] | None":
    """One repeated number or dealt date column's entry, or None where it does not stand (contract 4.6c.15).

    `readings` are the column's readings on the tabled rows (None where a
    row holds none), `patient_rows` each patient's tabled rows in position
    order, `groupings` the patient-fixed columns of the patient chain, each
    at its levels finest first (`grouping_levels`; the first level of a
    column that holds is kept), `years` each tabled row's years since its
    patient's first dated row on the layer's position column (None on the
    position axis; a row whose time is None reads as holding no reading).
    The entry stands where at least `FLOOR_TIMES` times the floor of
    patients hold four consecutive positions with readings (the lag-two
    products' rows); a grouping column stands where each of its bands holds
    that many patients with two readings or more, else it is left out. Two
    passes: the fixed part by least squares over every reading and the
    random part on what is left; then the fixed part again with each
    patient weighing as its own estimates' variance, and the random part
    again. `linear` reads the readings standardized (`linear_scores`), else
    as normal scores. Guarantees: a fixed function of its arguments;
    publishes no count; raises nothing; no I/O of any kind.
    """
    entry = from_scores(name, linear_scores(readings) if linear else normal_scores(readings), patient_rows, groupings, floor, years)
    if entry is not None:
        entry["scale"] = SCALE_LINEAR if linear else SCALE_NORMAL
    return entry


def line_misfit(scores: "list[float | None]", patient_rows: "list[list[int]]", years: "list[float | None] | None" = None) -> "float | None":
    """The pooled variance left about each patient's own least-squares line on an axis (positions, or `years` where
    given; a row with no time reads as holding no reading), over the patients of three readings or more: what that
    axis leaves of a patient's own change unread. None where no patient qualifies. Raises nothing."""
    squares = 0.0
    freedom = 0
    for rows in patient_rows:
        held: "list[tuple[float, float]]" = []
        for j in range(len(rows)):
            value = scores[rows[j]]
            t = float(j) if years is None else years[rows[j]]
            if value is not None and t is not None:
                held += [(t, value)]
        if len(held) < 3:
            continue
        mean_t = 0.0
        mean_y = 0.0
        for t, value in held:
            mean_t = mean_t + t
            mean_y = mean_y + value
        mean_t = mean_t / len(held)
        mean_y = mean_y / len(held)
        sxx = 0.0
        sxy = 0.0
        syy = 0.0
        for t, value in held:
            sxx = sxx + (t - mean_t) * (t - mean_t)
            sxy = sxy + (t - mean_t) * (value - mean_y)
            syy = syy + (value - mean_y) * (value - mean_y)
        if sxx <= 0.0:
            continue
        squares = squares + (syy - sxy * sxy / sxx)
        freedom = freedom + len(held) - 2
    return squares / freedom if freedom > 0 else None


def chosen(
    on_positions: "dict[str, object] | None",
    in_years: "dict[str, object] | None",
    misfit_positions: "float | None" = None,
    misfit_years: "float | None" = None,
) -> "dict[str, object] | None":
    """The entry a column publishes where both axes are offered: the years where each patient's own line leaves less
    about it on them than on the positions (`line_misfit`; the axis that reads more of a patient's own change), else
    the positions, which a twin's own visits carry exactly (a twin's dates are drawn at their published grain); the
    one that stands where only one does."""
    if in_years is None:
        return on_positions
    if on_positions is None:
        return in_years
    return in_years if misfit_years is not None and (misfit_positions is None or misfit_years < misfit_positions) else on_positions


def measured_on_both(
    name: str,
    readings: "list[fractions.Fraction | None]",
    patient_rows: "list[list[int]]",
    groupings: "list[Grouping]",
    floor: int,
    years: "list[float | None]",
    linear: bool,
) -> "dict[str, object] | None":
    """`measured` on the positions and on the years, the entry `chosen` by each axis's `line_misfit` on the same scores."""
    scored = linear_scores(readings) if linear else normal_scores(readings)
    on_positions = from_scores(name, scored, patient_rows, groupings, floor, None)
    in_years = from_scores(name, scored, patient_rows, groupings, floor, years)
    for entry in (on_positions, in_years):
        if entry is not None:
            entry["scale"] = SCALE_LINEAR if linear else SCALE_NORMAL
    return chosen(on_positions, in_years, line_misfit(scored, patient_rows, None), line_misfit(scored, patient_rows, years))


def _distinct_times(readings: "list[tuple[int, float, float]]") -> int:
    """How many different times a patient's readings are at (the support of a trend is two, of a curve three)."""
    return len({clock for _position, clock, _value in readings})


def from_scores(
    name: str,
    scores: "list[float | None]",
    patient_rows: "list[list[int]]",
    groupings: "list[Grouping]",
    floor: int,
    years: "list[float | None] | None" = None,
) -> "dict[str, object] | None":
    """`measured` on scores already on the normal-score scale (its every rule but the scores; the gate reads the
    moments of invented trajectories through it on their own scale)."""
    least = FLOOR_TIMES * floor
    lines: "list[list[float | None]]" = []
    times: "list[list[float]]" = []
    by_patient: "list[list[tuple[int, float, float]]]" = []
    reaching = 0
    supports_trend: "list[bool]" = []
    supports_curve: "list[bool]" = []
    for rows in patient_rows:
        line: "list[float | None]" = []
        clock: "list[float]" = []
        for j in range(len(rows)):
            k = rows[j]
            t = float(j) if years is None else years[k]
            value = scores[k]
            line += [value if t is not None else None]
            clock += [t if t is not None else 0.0]
        lines += [line]
        times += [clock]
        by_patient += [[(j, clock[j], value) for j, value in enumerate(line) if value is not None]]
        # ...A PATIENT SUPPORTS A TREND ONLY WHERE ITS READINGS SPAN TWO TIMES, A CURVE WHERE THEY SPAN THREE (batch
        # 4v's outside review, item 2): readings all at one date fix no slope, so the person floor is applied to the
        # support of each released coefficient.
        spans = _distinct_times(by_patient[-1])
        supports_trend += [spans >= 2]
        supports_curve += [spans >= 3]
        if _runs([value is not None for value in line]) >= 4 and spans >= 2:
            reaching += 1
    if reaching < least:
        return None
    bent = sum(1 for held in supports_curve if held) >= least
    kept: "list[Grouping]" = []
    bent_by: "dict[str, list[bool]]" = {}
    for one in groupings:
        if one.count < 2 or len(one.bands) != len(patient_rows) or any(other.name == one.name for other in kept):
            continue
        holding = [0 for _band in range(one.count)]
        for patient in range(len(patient_rows)):
            if len(by_patient[patient]) >= 2 and supports_trend[patient]:
                holding[one.bands[patient]] += 1
        if min(holding) >= least:
            kept += [one]
            bending = [0 for _band in range(one.count)]
            for patient in range(len(patient_rows)):
                if supports_curve[patient]:
                    bending[one.bands[patient]] += 1
            bent_by[one.name] = [band_count >= least for band_count in bending]
    beta = _fixed_part(by_patient, kept)
    while beta is None and kept:
        kept = kept[:-1]
        beta = _fixed_part(by_patient, kept)
    if beta is None:
        return None
    found = _random_part(_residuals(lines, times, beta, kept), times)
    if found is None:
        return None
    width = 1 + sum(one.count - 1 for one in kept)
    weighted = _weighted_fixed_part(by_patient, kept, found, [beta[3 * a + 2] for a in range(width)])
    if weighted is not None:
        again = _random_part(_residuals(lines, times, weighted, kept), times)
        if again is not None:
            beta, found = weighted, again
    level_sd = math.sqrt(found.level)
    slope_sd = math.sqrt(found.slope)
    corr = found.both / (level_sd * slope_sd) if level_sd > 0.0 and slope_sd > 0.0 else 0.0
    by: "list[dict[str, object]]" = []
    at = 1
    for one in kept:
        shifts = ["0"]
        trends = ["0"]
        curves = ["0"]
        for band in range(1, one.count):
            shifts += [rounded_text(_bounded(beta[3 * at], SIZE_MOST), PLACES["shift"])]
            trends += [rounded_text(_bounded(beta[3 * at + 1], SIZE_MOST), PLACES["trend"])]
            band_bends = bent_by[one.name][band] if one.name in bent_by else False
            curves += [rounded_text(_bounded(beta[3 * at + 2], SIZE_MOST), PLACES["curve"]) if band_bends else "0"]
            at += 1
        by += [{"column": one.name, "curve": curves, "level": LEVELS[one.level], "shift": shifts, "trend": trends}]
    return {
        "axis": AXIS_POSITION if years is None else AXIS_YEARS,
        "by": by,
        "column": name,
        "corr": rounded_text(_bounded(corr, CORR_MOST), PLACES["corr"]),
        "curve": rounded_text(_bounded(beta[2], SIZE_MOST), PLACES["curve"]) if bent else "0",
        "lag1": rounded_text(found.lag, PLACES["lag1"]),
        "level_sd": rounded_text(_bounded(level_sd, SIZE_MOST), PLACES["level_sd"]),
        "noise_sd": rounded_text(_bounded(math.sqrt(found.noise), SIZE_MOST), PLACES["noise_sd"]),
        "scale": SCALE_NORMAL,
        "slope_sd": rounded_text(_bounded(slope_sd, SIZE_MOST), PLACES["slope_sd"]),
        "trend": rounded_text(_bounded(beta[1], SIZE_MOST), PLACES["trend"]),
    }


# -- the loader (S35) and the entries read back ----------------------------------------------


@dataclasses.dataclass(frozen=True)
class GroupingRead:
    """A grouping column of an entry read back: its name, the level read (0, 1 or 2) and each band's shift and change a position."""

    column: str
    level: int
    shift: "tuple[float, ...]"
    trend: "tuple[float, ...]"
    curve: "tuple[float, ...]" = ()


@dataclasses.dataclass(frozen=True)
class Trajectory:
    """One entry of `grain.trajectory` read back (contract 4.6c.15), every number on the column's normal-score scale."""

    column: str
    level_sd: float
    slope_sd: float
    corr: float
    noise_sd: float
    lag1: float
    trend: float
    by: "tuple[GroupingRead, ...]"
    axis: str = AXIS_POSITION
    curve: float = 0.0


def _decimal(value: object, places: int, where: str) -> fractions.Fraction:
    """A moment's decimal text read exactly: an optional minus, figures, at most one point with figures after it."""
    if not isinstance(value, str):
        raise _broken(where, "every moment is a decimal written as text")
    figures = 0
    points = 0
    for at in range(len(value)):
        character = value[at]
        if "0" <= character <= "9":
            figures += 1
        elif character == "." and points == 0 and figures > 0 and at + 1 < len(value):
            points += 1
        elif not (character == "-" and at == 0):
            raise _broken(where, "every moment is a decimal written as text")
    if figures == 0:
        raise _broken(where, "every moment is a decimal written as text")
    exact = fractions.Fraction(value)
    if (exact * (10 ** places)).denominator != 1:
        raise _broken(where, f"a moment is written to at most {places} places")
    return exact


def checked(grain: "dict[str, object]", classes: "dict[str, str]", roles: "dict[str, str]", bands_at: "dict[str, tuple[int, int, int]]", counted: "set[str]") -> None:
    """S35: refuse a `grain.trajectory` that is not this version's shape and bounds.

    `classes` each column's published class, `roles` each column's role,
    `bands_at` the band count at `L0`, `L1` and `L2` of every patient-fixed
    column of the patient chain's ladder, `counted` the counting process's
    columns. Each entry names a repeated number column or a dealt date
    column once, in schema order, outside the counting process; its moments
    are decimals to their places inside their bounds; each grouping column a
    patient-fixed column of the patient chain once, at one of its levels,
    one shift, one change and one curve a band of that level, the first
    band's 0; an entry reads the years axis only on a repeated column beside
    a dealt date position column; a date column's reads positions on the
    linear scale.
    Raises `errors.ProfileError`; returns where every one holds.
    """
    if TRAJECTORY_KEY not in grain:
        return
    entries = grain[TRAJECTORY_KEY]
    if not isinstance(entries, list) or not entries:
        raise _broken("grain.trajectory", "a list holding one entry or more, written only where one stands")
    place_of: "dict[str, int]" = {}
    for name in classes:
        place_of[name] = len(place_of)
    seen: "list[int]" = []
    position = grain["position"] if "position" in grain else None
    dated = isinstance(position, str) and position in classes and classes[position] == "dealt_date"
    for entry in entries:
        if not isinstance(entry, dict) or sorted(entry) != list(ENTRY_KEYS):
            raise _broken("grain.trajectory", "an entry holds exactly its eleven keys")
        name = entry["column"]
        if not isinstance(name, str) or name not in classes or classes[name] not in ("repeated", "dealt_date") or name in counted:
            raise _broken("grain.trajectory", "an entry names a repeated or dealt date column outside the counting process")
        if name not in roles or (classes[name] == "repeated" and roles[name] not in NUMBER_ROLES) or (
            classes[name] == "dealt_date" and roles[name] != DATE_ROLE
        ):
            raise _broken(name, "an entry names a repeated column of a number role or a dealt date column")
        place = place_of[name]
        if seen and place <= seen[-1]:
            raise _broken(name, "the entries stand once each, in schema order")
        seen += [place]
        allowed = (AXIS_POSITION, AXIS_YEARS) if dated and classes[name] == "repeated" else (AXIS_POSITION,)
        if entry["axis"] not in allowed:
            raise _broken(name, "the time axis is the position, or the years beside a dated position column")
        scales = (SCALE_LINEAR,) if classes[name] == "dealt_date" else (SCALE_LINEAR, SCALE_NORMAL)
        if entry["scale"] not in scales:
            raise _broken(name, "the scale is linear or normal, a date's linear")
        for key in ("level_sd", "slope_sd", "noise_sd"):
            value = _decimal(entry[key], PLACES[key], f"{name}.{key}")
            if value < 0 or value > SIZE_MOST:
                raise _broken(f"{name}.{key}", "a spread lies in 0 to 10")
        if abs(_decimal(entry["corr"], PLACES["corr"], f"{name}.corr")) > CORR_MOST:
            raise _broken(f"{name}.corr", "the level and slope correlation lies in -0.95 to 0.95")
        lag = _decimal(entry["lag1"], PLACES["lag1"], f"{name}.lag1")
        if lag < LAG_LEAST or lag > LAG_MOST:
            raise _broken(f"{name}.lag1", "the lag-one coefficient lies in -0.9 to 0.95")
        if abs(_decimal(entry["trend"], PLACES["trend"], f"{name}.trend")) > SIZE_MOST:
            raise _broken(f"{name}.trend", "a change a unit of time lies in -10 to 10")
        if abs(_decimal(entry["curve"], PLACES["curve"], f"{name}.curve")) > SIZE_MOST:
            raise _broken(f"{name}.curve", "a curve lies in -10 to 10")
        groups = entry["by"]
        if not isinstance(groups, list):
            raise _broken(f"{name}.by", "a list of grouping columns")
        named: "set[str]" = set()
        for group in groups:
            if not isinstance(group, dict) or sorted(group) != list(BY_KEYS):
                raise _broken(f"{name}.by", "a grouping column holds exactly its five keys")
            column = group["column"]
            if not isinstance(column, str) or column in named or column not in bands_at or column not in classes or classes[column] != "patient_fixed":
                raise _broken(f"{name}.by", "a grouping column is a patient-fixed column of the patient chain, once")
            named = named | {column}
            level = group["level"]
            if not isinstance(level, str) or level not in LEVEL_PLACE:
                raise _broken(f"{name}.by", "a grouping column is read at L0, L1 or L2")
            bands = bands_at[column][LEVEL_PLACE[level]]
            for key in ("shift", "trend", "curve"):
                listed = group[key]
                if not isinstance(listed, list) or len(listed) != bands or bands < 2:
                    raise _broken(f"{name}.by.{column}", "one shift, one change and one curve for each band of the level read")
                read = [_decimal(one, PLACES[key], f"{name}.by.{column}") for one in listed]
                if read[0] != 0 or any(abs(one) > SIZE_MOST for one in read):
                    raise _broken(f"{name}.by.{column}", "the first band's are 0 and every one lies in -10 to 10")


def entries_of(grain: "dict[str, object]") -> "tuple[Trajectory, ...]":
    """`grain.trajectory` read back, or () where it does not stand; read only after S35 has held it. Raises nothing."""
    listed = grain[TRAJECTORY_KEY] if TRAJECTORY_KEY in grain else None
    out: "list[Trajectory]" = []
    for entry in listed if isinstance(listed, list) else []:
        if not isinstance(entry, dict):
            continue
        groups: "list[GroupingRead]" = []
        listed_by = entry["by"] if "by" in entry else None
        for group in listed_by if isinstance(listed_by, list) else []:
            if isinstance(group, dict):
                level = group["level"] if "level" in group else "L2"
                groups += [GroupingRead(
                    f"{group['column']}",
                    LEVEL_PLACE[level] if isinstance(level, str) and level in LEVEL_PLACE else 2,
                    tuple(float(fractions.Fraction(one)) for one in group["shift"]),
                    tuple(float(fractions.Fraction(one)) for one in group["trend"]),
                    tuple(float(fractions.Fraction(one)) for one in group["curve"]),
                )]
        out += [Trajectory(
            f"{entry['column']}",
            float(fractions.Fraction(entry["level_sd"])), float(fractions.Fraction(entry["slope_sd"])),
            float(fractions.Fraction(entry["corr"])), float(fractions.Fraction(entry["noise_sd"])),
            float(fractions.Fraction(entry["lag1"])), float(fractions.Fraction(entry["trend"])), tuple(groups),
            f"{entry['axis']}", float(fractions.Fraction(entry["curve"])),
        )]
    return tuple(out)


# -- the generator ------------------------------------------------------------------------


def words_needed(entries: int, patients: int, rows: int) -> int:
    """The walk's words for the entries: `PATIENT_WORDS` a patient and `ROW_WORDS` a row, each entry."""
    return entries * (PATIENT_WORDS * patients + ROW_WORDS * rows)


def scores(
    entry: Trajectory,
    r_values: "list[int]",
    bands: "dict[str, list[int]]",
    words: "chain_walk.Packed",
    first_word: int,
    own: "list[float] | None" = None,
    times: "list[float] | None" = None,
) -> "list[float]":
    """Each tabled row's score under the entry (G16.20), patients in order and each one's rows by position.

    `bands[c]` is each patient's band of grouping column `c` at the level its entry reads; `words`
    the entry's words from `first_word` on (`PATIENT_WORDS` a patient, then
    `ROW_WORDS` a row); `own` each patient's own-mean score where an
    own-mean column parents the column's row family (it stands for the
    level's hidden score); `times` each row's time on the entry's axis (the
    position where None). Guarantees: a fixed function of its arguments;
    raises nothing for words the plan counted; no I/O.
    """
    count = len(r_values)
    rows = sum(r_values)
    row_word = first_word + PATIENT_WORDS * count
    slope_free = math.sqrt(1.0 - entry.corr * entry.corr)
    lag_free = math.sqrt(1.0 - entry.lag1 * entry.lag1)
    out = [0.0 for _row in range(rows)]
    at = 0
    for patient in range(count):
        base = first_word + PATIENT_WORDS * patient
        u0 = chain_walk.hidden_score(chain_walk.hidden_sum(chain_walk.item(words, base), chain_walk.item(words, base + 1), chain_walk.item(words, base + 2)))
        u1 = chain_walk.hidden_score(chain_walk.hidden_sum(chain_walk.item(words, base + 3), chain_walk.item(words, base + 4), chain_walk.item(words, base + 5)))
        if own is not None:
            u0 = own[patient]
        level = entry.level_sd * u0
        slope = entry.trend + entry.slope_sd * (entry.corr * u0 + slope_free * u1)
        curve = entry.curve
        for group in entry.by:
            band = bands[group.column][patient]
            level = level + group.shift[band]
            slope = slope + group.trend[band]
            if group.curve:
                curve = curve + group.curve[band]
        noise = 0.0
        for j in range(r_values[patient]):
            word = row_word + ROW_WORDS * at
            h = chain_walk.hidden_score(chain_walk.hidden_sum(chain_walk.item(words, word), chain_walk.item(words, word + 1), chain_walk.item(words, word + 2)))
            noise = entry.noise_sd * h if j == 0 else entry.lag1 * noise + lag_free * entry.noise_sd * h
            t = float(j) if times is None else times[at]
            out[at] = level + slope * t + curve * t * t + noise
            at += 1
    return out


def date_order(text: str) -> "fractions.Fraction | None":
    """A canonical date, month, quarter or stamp's place in time as an exact number of seconds (a month or quarter at its first day), else None."""
    if not isinstance(text, str):
        return None
    if len(text) >= 7 and text[4:6] == "-Q" and "1" <= text[6] <= "4":
        text = f"{text[0:4]}-{3 * (int(text[6]) - 1) + 1:02d}-01"
    elif len(text) == 7:
        text = text + "-01"
    found = chain_moments.ordinal(DATE_ROLE, text, {})
    if found is None:
        return None
    return found * 86400 if len(text) <= 10 else found


def redealt(cells: "list[str]", values: "list[fractions.Fraction | float | None]", order_scores: "list[float]") -> "list[str]":
    """A column's cells dealt again to its rows in the order of their scores: the rows holding a reading take the readings in rising order, ties by row; every other row keeps its cell.

    The column's cells are the same cells, so every fact of the column on
    its own stands as before. Raises nothing.
    """
    holders = [row for row in range(len(cells)) if values[row] is not None]
    by_value = [row for _value, row in sorted((values[row], row) for row in holders)]
    by_score = [row for _score, row in sorted((order_scores[row], row) for row in holders)]
    out = list(cells)
    for place in range(len(holders)):
        out[by_score[place]] = cells[by_value[place]]
    return out
