"""THE TRAJECTORIES ZONE OF THE INSIDE RECORD: a patient's visits as a model kept on the protected computer (lane IN-3, plan P4-D498).

WHAT IT IS. A table of several rows a patient holds, beside each
patient's fixed columns (an arm, an age, a clinic), the patient's visits:
how many rows each patient has, how far apart its dated rows lie, and how
each repeated number and each repeated yes/no outcome moves within the
patient. The strict description could only publish these as rounded
spreads over bands of at least the floor of patients, so the twin's long
patients were cut short, its visit gaps took no shape, its yes/no outcomes
carried no patient at all and its random effects were normal by
construction. The inside record stays on the computer the real table is
on (`inside`, plan P4-D495), so this zone carries them as a MODEL at full
resolution, never as data:

* `census`: how many patients hold each number of rows (exact; the long
  patients included), never a patient or a row;
* `gaps`: the anchor date column's gaps between a patient's consecutive
  rows as a quantile function of `GAP_GRID` points, the share of a gap's
  normal score a patient keeps (its pace), the gaps' serial correlation,
  and the pace's correlation with the patient's number of rows;
* `numbers`: for each repeated number column, on its scale (standardized
  where its skew is small, else the normal scores of its mid-ranks) and
  its time axis (positions, or years since the patient's first dated row,
  whichever each patient's own line leaves less on), the fixed part by
  least squares with errors robust to the patients, each term but the
  intercept and the time kept where its z reaches `GATE_Z` (time, its
  square, every patient-fixed column, the time and its square by every
  patient-fixed label of at most `BY_LEVELS` levels, the patient's number
  of rows); the random level and slope as DISTRIBUTIONS: their spreads and
  correlation by EM with each patient's line read with the noise its
  rows' times and the AR(1) noise give (maximum likelihood), their shapes
  as quantile functions of `SHAPE_GRID` points of the standardized
  predictions of the patients read reliably; the noise and its lag-one
  coefficient (calibrated for short series on the patients' own times);
  and the correlations between columns within a row and between patients'
  levels;
* `binaries`: for each repeated yes/no column, a LATENT THRESHOLD: a
  probit on the same patient-fixed columns, time and the patient's rows,
  with a term on each repeated number column of the same row, and the
  latent within-patient correlation from the pairs of one patient's rows
  (the bivariate normal by its Hermite series, so a pair's joint chance
  needs no special function);
* `keys`, on a KEYED LONG TABLE (a label of three levels or more moving
  within patients, the one that fixes the most other labels: an item, a
  test): each key level's value column (the first of the row's content
  numeric on nine tenths of the level's cells), the label that sets its
  scale where one does (a unit: groups whose typical values stand
  `SCALE_RATIO` times apart), and the same two-level model read on the
  level's rows alone, on the normal scores within each unit.

A test holds the zone's size to the columns, levels and grid points:
doubling the rows of an invented table moves it by a few per cent.

HOW THE TWIN READS IT (`applied`, after the generator's patient walk made
the patients, their fixed columns and their rows), in two steps, the
second reading the time axis the first leaves (the dates zone, lane IN-5,
may run its own between them at the merge): (1) the long patients: each
twin patient's number of rows is set by rank to the census, rows moving
from a patient of too many to one of too few, inside the same
patient-fixed labels first (the moved rows take the receiving patient's
key and fixed cells); (2) the position column written 1, 2, ... again;
(3) the anchor, a date or a clock, timed again from each patient's first
moment by the gap model, every other date column of the row moved with
it (never in the generate step, `twin_with_zone`, which times no date:
there every date column moves with its rows and the dates zone writes
its own again over the patients the rows form, every day of the month
made up; Codex's review of batch 4w, item 2); then (4) each repeated number column's present cells DEALT to the
rows in the order of their latent scores (so the column's values stand
exactly as the generator wrote them, and only their arrangement carries
the model); (5) each yes/no column's present cells dealt the same way by
the latent threshold, on the twin's own (dealt) numbers; (6) on a keyed
table, each key level's rows' content (the value and every cell standing
with it: its unit, its copy, its flag) dealt by the level's latent
scores inside each unit. Every random quantity comes from SplitMix64
words seeded by the twin's seed; every operation is binary64 `+ - * /`
and `sqrt` in the order written, with the shared module's logarithm,
exponential and normal quantile, so a twin is the same on every machine.

WHY IT NEEDS THE PATIENT LAYER. The zone carries trajectories, not the
skeleton they ride on: the patients, their fixed columns and the order of
their rows are the patient walk's (`patient_walk`), which runs where the
description's `grain` stands. The layer's sub-switch guarded what a SHARED
description publishes in patients; the inside record is never shared, so
nothing the switch guarded applies to it, but without the walk a twin has
no patients to give a trajectory to: `profile` writes the zone only where
the layer stands and `generate` applies it only where `grain` does.

NOTHING HERE PRINTS A VALUE. The producer returns the zone, the generator
returns cells; neither writes a line.
"""

import dataclasses
import math
import typing

from synthtwin import chain_walk

ZONE = "trajectories"
ZONE_VERSION = 1
# The grids: a gap's quantile function, a random effect's shape.
GAP_GRID = 1001
SHAPE_GRID = 101
# A census of rows a patient keeps every number it holds up to this many
# different numbers of rows, else a quantile function of `GAP_GRID` points.
CENSUS_CAP = 1000
# A label column of the patient enters a fixed part as one indicator a level
# but its commonest, where it has at most this many levels; past it, not at all.
LEVELS_AT_MOST = 30
# ...and the time by its levels where it has at most this many.
BY_LEVELS = 4
# A term of a fixed part whose robust z is under this is set to nought, the
# intercept and the time's own term apart.
GATE_Z = 1.96
# A zone stands only where at least this many patients hold two rows or more.
PATIENTS_AT_LEAST = 50
# A label sets a key's scale (a unit) where its groups' typical values stand this many times apart.
SCALE_RATIO = 3.0
# The rounds that set a date anchor's gaps to their shape and its moments to the real calendar in turn.
CALENDAR_ROUNDS = 4
# The fits of a table read at most this many rows, of whole patients.
FIT_ROWS = 200000
# A random effect's shape is read from the patients whose own line holds at least this share of its spread.
RELIABLE = 0.8
# The rows of a patient its yes/no pairs read (the first ones, in order).
PAIR_ROWS = 8
# The Hermite series' terms.
HERMITE_TERMS = 40
# The most a correlation or a lag-one coefficient is held to.
CORR_MOST = 0.95
LAG_MOST = 0.95
LAG_LEAST = -0.5
# A year in seconds (365.25 days).
SECONDS_A_YEAR = 31557600
SECONDS_A_DAY = 86400
# The kinds of a date column's cells.
KIND_DATE = "date"
KIND_MINUTE = "minute"
KIND_SECOND = "second"
KINDS = (KIND_DATE, KIND_MINUTE, KIND_SECOND)
AXIS_POSITION = "position"
AXIS_YEARS = "years"
SCALE_LINEAR = "linear"
SCALE_NORMAL = "normal"
# A number column is read on the linear scale where its skew is under this.
SKEW_CUT = 0.2
# A repeated number whose one commonest value holds at least this share of its present cells (an atom, such as an
# amount that is nought on most rows) is not dealt by the zone (lane W5-PL): read on one scale, its two parts (whether
# a row holds the atom, and how large the rest are) lose what the columns before it in the relations zone carry, an
# arm's effect on a blood loss's amount halved on the battery's visits table (-0.15 against -0.31), so its cells stay
# where the relations zone dealt them.
ATOM_SHARE = 0.3
# Cells read as no value whatever the column.
NO_VALUE = ("", "na", "n/a", "nan", "null", "none", ".", "-")
_MASK = (1 << 64) - 1
_TWO_53 = 9007199254740992.0
_ROOT_TWO_PI = 2.5066282746310002
_ZONE_KEYS = ("binaries", "census", "fixed", "gaps", "numbers", "order", "person", "position", "rows", "version")


# -- text, read under the offline audit's exact type checks ------------------------------------------


def _text(cell: object) -> str:
    if not isinstance(cell, str):
        raise TypeError("synthtwin reads a table's cells as text only.")
    return cell


def _bare(cell: object) -> str:
    if not isinstance(cell, str):
        raise TypeError("synthtwin reads a table's cells as text only.")
    return cell.strip()


def _absent(cell: object) -> bool:
    if not isinstance(cell, str):
        raise TypeError("synthtwin reads a table's cells as text only.")
    return cell.strip().lower() in NO_VALUE


def _digits(text: str) -> bool:
    if not text:
        return False
    for character in text:
        if character < "0" or character > "9":
            return False
    return True


def _number(cell: object) -> "float | None":
    """A cell written as a plain decimal number (a sign, figures, one point, an exponent), else None."""
    if not isinstance(cell, str):
        raise TypeError("synthtwin reads a table's cells as text only.")
    text = cell.strip()
    if not text or text.lower() in ("nan", "inf", "-inf", "+inf", "infinity", "-infinity"):
        return None
    for character in text:
        if character not in "0123456789+-.eE":
            return None
    try:
        value = float(text)
    except ValueError:
        return None
    return value if math.isfinite(value) else None


def floor_of(value: float) -> int:
    """The greatest whole number at or below `value` (`int` cuts toward nought)."""
    whole = int(value)
    return whole - 1 if whole > value else whole


def _whole(value: float) -> bool:
    return value == float(floor_of(value))


# -- the calendar, in whole numbers ------------------------------------------------------------------


def days_from_civil(year: int, month: int, day: int) -> int:
    """Days since 1970-01-01 of a day of the proleptic Gregorian calendar (H. Hinnant's algorithm)."""
    shifted = year - 1 if month <= 2 else year
    era = (shifted if shifted >= 0 else shifted - 399) // 400
    of_era = shifted - era * 400
    of_year = (153 * (month + (-3 if month > 2 else 9)) + 2) // 5 + day - 1
    of_cycle = of_era * 365 + of_era // 4 - of_era // 100 + of_year
    return era * 146097 + of_cycle - 719468


def civil_from_days(days: int) -> "tuple[int, int, int]":
    """The year, month and day of a count of days since 1970-01-01."""
    shifted = days + 719468
    era = (shifted if shifted >= 0 else shifted - 146096) // 146097
    of_era = shifted - era * 146097
    of_cycle = (of_era - of_era // 1460 + of_era // 36524 - of_era // 146096) // 365
    year = of_cycle + era * 400
    of_year = of_era - (365 * of_cycle + of_cycle // 4 - of_cycle // 100)
    point = (5 * of_year + 2) // 153
    day = of_year - (153 * point + 2) // 5 + 1
    month = point + (3 if point < 10 else -9)
    return (year + 1 if month <= 2 else year), month, day


@dataclasses.dataclass(frozen=True)
class Moment:
    """A date cell read: seconds since 1970-01-01, its kind, and the character between its day and its clock."""

    seconds: int
    kind: str
    joint: str


def moment_of(cell: object) -> "Moment | None":
    """A cell written YYYY-MM-DD, optionally a space or a T and HH:MM or HH:MM:SS; else None."""
    text = _bare(cell)
    if len(text) < 10 or text[4] != "-" or text[7] != "-":
        return None
    if not _digits(text[:4]) or not _digits(text[5:7]) or not _digits(text[8:10]):
        return None
    year, month, day = int(text[:4]), int(text[5:7]), int(text[8:10])
    if month < 1 or month > 12 or day < 1 or day > 31:
        return None
    days = days_from_civil(year, month, day)
    if civil_from_days(days) != (year, month, day):
        return None
    rest = text[10:]
    if not rest:
        return Moment(days * SECONDS_A_DAY, KIND_DATE, " ")
    joint = rest[0]
    clock = rest[1:]
    if joint not in (" ", "T") or len(clock) not in (5, 8) or clock[2] != ":":
        return None
    if not _digits(clock[:2]) or not _digits(clock[3:5]):
        return None
    hours, minutes = int(clock[:2]), int(clock[3:5])
    seconds = 0
    kind = KIND_MINUTE
    if len(clock) == 8:
        if clock[5] != ":" or not _digits(clock[6:8]):
            return None
        seconds = int(clock[6:8])
        kind = KIND_SECOND
    if hours > 23 or minutes > 59 or seconds > 59:
        return None
    return Moment(days * SECONDS_A_DAY + hours * 3600 + minutes * 60 + seconds, kind, joint)


def moment_text(seconds: int, kind: str, joint: str) -> str:
    """A moment written back in its column's form."""
    days = seconds // SECONDS_A_DAY
    left = seconds - days * SECONDS_A_DAY
    year, month, day = civil_from_days(days)
    out = f"{year:04d}-{month:02d}-{day:02d}"
    if kind == KIND_DATE:
        return out
    clock = f"{left // 3600:02d}:{(left % 3600) // 60:02d}"
    if kind == KIND_SECOND:
        clock = clock + f":{left % 60:02d}"
    return out + joint + clock


# -- the random stream -----------------------------------------------------------------------------


def _mixed(value: int) -> int:
    mixed = (value + 0x9E3779B97F4A7C15) & _MASK
    mixed = ((mixed ^ (mixed >> 30)) * 0xBF58476D1CE4E5B9) & _MASK
    mixed = ((mixed ^ (mixed >> 27)) * 0x94D049BB133111EB) & _MASK
    return mixed ^ (mixed >> 31)


def name_salt(name: object) -> int:
    """A fixed whole number of a column's name (FNV-1a over its characters' code points), the same on every machine."""
    if not isinstance(name, str):
        raise TypeError("synthtwin reads a column's name as text only.")
    total = 0xCBF29CE484222325
    for character in name:
        total = ((total ^ ord(character)) * 0x100000001B3) & _MASK
    return total


def stream_of(seed: int, salt: int) -> "list[int]":
    """A SplitMix64 stream's state (one word in a list) from a seed and a salt."""
    return [_mixed(((seed & _MASK) * 0x9E3779B97F4A7C15 + (salt & _MASK)) & _MASK)]


def next_word(state: "list[int]") -> int:
    state[0] = (state[0] + 0x9E3779B97F4A7C15) & _MASK
    return _mixed(state[0])


def next_uniform(state: "list[int]") -> float:
    """A share strictly between nought and one from the stream's next word."""
    return ((next_word(state) >> 11) + 0.5) / _TWO_53


def next_normal(state: "list[int]") -> float:
    """A normal score from the stream's next word (the shared module's quantile)."""
    return chain_walk.normal_score(next_uniform(state))


# -- small arithmetic ---------------------------------------------------------------------------------


def _mean(values: "list[float]") -> float:
    total = 0.0
    for value in values:
        total = total + value
    return total / len(values) if values else 0.0


def _spread(values: "list[float]") -> float:
    if len(values) < 2:
        return 0.0
    centre = _mean(values)
    total = 0.0
    for value in values:
        total = total + (value - centre) * (value - centre)
    return math.sqrt(total / (len(values) - 1))


def _skew(values: "list[float]") -> float:
    if len(values) < 3:
        return 0.0
    centre = _mean(values)
    second = 0.0
    third = 0.0
    for value in values:
        d = value - centre
        second = second + d * d
        third = third + d * d * d
    second = second / len(values)
    third = third / len(values)
    if second <= 0.0:
        return 0.0
    return third / (second * math.sqrt(second))


def _corr(first: "list[float]", second: "list[float]") -> float:
    if len(first) < 3:
        return 0.0
    a = _mean(first)
    b = _mean(second)
    sab = 0.0
    saa = 0.0
    sbb = 0.0
    for at in range(len(first)):
        x = first[at] - a
        y = second[at] - b
        sab = sab + x * y
        saa = saa + x * x
        sbb = sbb + y * y
    if saa <= 0.0 or sbb <= 0.0:
        return 0.0
    return sab / math.sqrt(saa * sbb)


def _bounded(value: float, least: float, most: float) -> float:
    return least if value < least else (most if value > most else value)


def _density(z: float) -> float:
    return chain_walk.exponential(-0.5 * z * z) / _ROOT_TWO_PI


def fast_cdf(z: float) -> float:
    """The normal distribution function by Abramowitz and Stegun 26.2.17 (error under 7.5e-8), for the producer's fits."""
    if z < -8.0:
        return 0.0
    if z > 8.0:
        return 1.0
    x = -z if z < 0.0 else z
    t = 1.0 / (1.0 + 0.2316419 * x)
    poly = ((((1.330274429 * t - 1.821255978) * t + 1.781477937) * t - 0.356563782) * t + 0.319381530) * t
    upper = _density(x) * poly
    return upper if z < 0.0 else 1.0 - upper


def _quantile_grid(values: "list[float]", points: int) -> "list[float]":
    """The quantile function on `points` points, each an observed value (the lower order statistic)."""
    ordered = sorted(values)
    last = len(ordered) - 1
    out: "list[float]" = []
    for k in range(points):
        out += [ordered[(k * last) // (points - 1)]]
    return out


def _from_grid(grid: "list[float]", u: float) -> float:
    """A value of a quantile function on an even grid at the share `u`, linear between its points."""
    last = len(grid) - 1
    place = u * last
    below = int(place)
    if below >= last:
        return grid[last]
    if below < 0:
        return grid[0]
    part = place - below
    return grid[below] + (grid[below + 1] - grid[below]) * part


def _share_on_grid(grid: "list[float]", value: float) -> float:
    """The share at which an even quantile grid reaches `value` (the middle of a run of equal points), in (0, 1)."""
    last = len(grid) - 1
    low = 0
    high = last + 1
    while low < high:
        middle = (low + high) // 2
        if grid[middle] < value:
            low = middle + 1
        else:
            high = middle
    first = low
    low = first
    high = last + 1
    while low < high:
        middle = (low + high) // 2
        if grid[middle] <= value:
            low = middle + 1
        else:
            high = middle
    after = low
    if first >= after:
        if first == 0:
            return 0.5 / (last + 1)
        if first > last:
            return 1.0 - 0.5 / (last + 1)
        below = grid[first - 1]
        above = grid[first]
        part = (value - below) / (above - below) if above > below else 0.5
        return _bounded((first - 1 + part) / last, 0.5 / (last + 1), 1.0 - 0.5 / (last + 1))
    middle_point = 0.5 * (first + after - 1)
    return _bounded(middle_point / last, 0.5 / (last + 1), 1.0 - 0.5 / (last + 1))


def mid_scores(values: "list[float]") -> "list[float]":
    """Each value's normal score at its mid-rank (ties share one)."""
    count = len(values)
    order = [at for _value, at in sorted((values[at], at) for at in range(count))]
    out = [0.0 for _value in values]
    start = 0
    while start < count:
        end = start
        while end + 1 < count and values[order[end + 1]] == values[order[start]]:
            end += 1
        score = chain_walk.normal_score((0.5 * (start + end) + 0.5) / count)
        for place in range(start, end + 1):
            out[order[place]] = score
        start = end + 1
    return out


# -- linear algebra, small and exact in its order --------------------------------------------------


def cholesky(matrix: "list[list[float]]", ridge: float = 1e-10) -> "list[list[float]] | None":
    """The lower Cholesky factor of a symmetric matrix (a ridge on the diagonal), None where it is not positive."""
    size = len(matrix)
    lower = [[0.0 for _column in range(size)] for _row in range(size)]
    for row in range(size):
        for column in range(row + 1):
            total = matrix[row][column]
            if row == column:
                total = total + ridge * (1.0 + abs(matrix[row][row]))
            for k in range(column):
                total = total - lower[row][k] * lower[column][k]
            if row == column:
                if not total > 0.0:
                    return None
                lower[row][column] = math.sqrt(total)
            else:
                lower[row][column] = total / lower[column][column]
    return lower


def _solved(lower: "list[list[float]]", right: "list[float]") -> "list[float]":
    size = len(lower)
    forward = [0.0 for _k in range(size)]
    for row in range(size):
        total = right[row]
        for k in range(row):
            total = total - lower[row][k] * forward[k]
        forward[row] = total / lower[row][row]
    back = [0.0 for _k in range(size)]
    for row in range(size - 1, -1, -1):
        total = forward[row]
        for k in range(row + 1, size):
            total = total - lower[k][row] * back[k]
        back[row] = total / lower[row][row]
    return back


def _inverse(lower: "list[list[float]]") -> "list[list[float]]":
    size = len(lower)
    columns: "list[list[float]]" = []
    for k in range(size):
        unit = [1.0 if row == k else 0.0 for row in range(size)]
        columns += [_solved(lower, unit)]
    return [[columns[column][row] for column in range(size)] for row in range(size)]


def positive_correlation(matrix: "list[list[float]]") -> "list[list[float]]":
    """A correlation matrix shrunk toward the identity until it factors (each pass keeps nine tenths of every off-diagonal)."""
    size = len(matrix)
    work = [[matrix[row][column] for column in range(size)] for row in range(size)]
    for _pass in range(60):
        if cholesky(work, 1e-9) is not None:
            return work
        for row in range(size):
            for column in range(size):
                if row != column:
                    work[row][column] = work[row][column] * 0.9
    return [[1.0 if row == column else 0.0 for column in range(size)] for row in range(size)]


# -- the fits ---------------------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class Fit:
    """A fixed part: the terms' names, their coefficients and robust z, and the residuals of the rows it read."""

    terms: "tuple[str, ...]"
    coefficients: "tuple[float, ...]"
    z: "tuple[float, ...]"


def _cross(design: "list[list[float]]", weights: "list[float] | None") -> "list[list[float]]":
    width = len(design[0]) if design else 0
    out = [[0.0 for _column in range(width)] for _row in range(width)]
    for at in range(len(design)):
        row = design[at]
        weight = weights[at] if weights is not None else 1.0
        for a in range(width):
            xa = row[a] * weight
            if xa == 0.0:
                continue
            target = out[a]
            for b in range(a, width):
                target[b] = target[b] + xa * row[b]
    for a in range(width):
        for b in range(a):
            out[a][b] = out[b][a]
    return out


def least_squares(design: "list[list[float]]", response: "list[float]", clusters: "list[int]") -> "tuple[list[float], list[float]] | None":
    """Least squares with standard errors robust to the clusters (each patient one); None where the design is singular."""
    width = len(design[0]) if design else 0
    if width == 0 or len(design) <= width:
        return None
    lower = cholesky(_cross(design, None))
    if lower is None:
        return None
    right = [0.0 for _k in range(width)]
    for at in range(len(design)):
        row = design[at]
        y = response[at]
        for a in range(width):
            right[a] = right[a] + row[a] * y
    beta = _solved(lower, right)
    scores: "dict[int, list[float]]" = {}
    for at in range(len(design)):
        row = design[at]
        fitted = 0.0
        for a in range(width):
            fitted = fitted + row[a] * beta[a]
        residual = response[at] - fitted
        group = clusters[at]
        if group not in scores:
            scores[group] = [0.0 for _k in range(width)]
        held = scores[group]
        for a in range(width):
            held[a] = held[a] + row[a] * residual
    return beta, _robust_errors(lower, scores, width)


def _robust_errors(lower: "list[list[float]]", scores: "dict[int, list[float]]", width: int) -> "list[float]":
    inverse = _inverse(lower)
    meat = [[0.0 for _column in range(width)] for _row in range(width)]
    for group in sorted(scores):
        held = scores[group]
        for a in range(width):
            if held[a] == 0.0:
                continue
            for b in range(width):
                meat[a][b] = meat[a][b] + held[a] * held[b]
    out: "list[float]" = []
    for a in range(width):
        total = 0.0
        for b in range(width):
            for c in range(width):
                total = total + inverse[a][b] * meat[b][c] * inverse[c][a]
        out += [math.sqrt(total) if total > 0.0 else 0.0]
    return out


def probit(design: "list[list[float]]", outcome: "list[int]", clusters: "list[int]") -> "tuple[list[float], list[float]] | None":
    """A marginal probit by Newton's method (iteratively reweighted), standard errors robust to the clusters."""
    width = len(design[0]) if design else 0
    if width == 0 or len(design) <= width:
        return None
    share = _mean([float(y) for y in outcome])
    if share <= 0.0 or share >= 1.0:
        return None
    beta = [0.0 for _k in range(width)]
    beta[0] = chain_walk.normal_score(share)
    lower: "list[list[float]] | None" = None
    for _step in range(30):
        weights: "list[float]" = []
        working: "list[float]" = []
        for at in range(len(design)):
            row = design[at]
            eta = 0.0
            for a in range(width):
                eta = eta + row[a] * beta[a]
            eta = _bounded(eta, -7.0, 7.0)
            p = _bounded(fast_cdf(eta), 1e-10, 1.0 - 1e-10)
            phi = max(_density(eta), 1e-300)
            weights += [phi * phi / (p * (1.0 - p))]
            working += [eta + (outcome[at] - p) / phi]
        lower = cholesky(_cross(design, weights))
        if lower is None:
            return None
        right = [0.0 for _k in range(width)]
        for at in range(len(design)):
            row = design[at]
            wz = weights[at] * working[at]
            for a in range(width):
                right[a] = right[a] + row[a] * wz
        moved = _solved(lower, right)
        change = 0.0
        for a in range(width):
            change = max(change, abs(moved[a] - beta[a]))
        beta = moved
        if change < 1e-9:
            break
    if lower is None:
        return None
    scores: "dict[int, list[float]]" = {}
    for at in range(len(design)):
        row = design[at]
        eta = 0.0
        for a in range(width):
            eta = eta + row[a] * beta[a]
        eta = _bounded(eta, -7.0, 7.0)
        p = _bounded(fast_cdf(eta), 1e-10, 1.0 - 1e-10)
        factor = _density(eta) * (outcome[at] - p) / (p * (1.0 - p))
        group = clusters[at]
        if group not in scores:
            scores[group] = [0.0 for _k in range(width)]
        held = scores[group]
        for a in range(width):
            held[a] = held[a] + row[a] * factor
    return beta, _robust_errors(lower, scores, width)


def hermite_terms(h: float, k: float, terms: int = HERMITE_TERMS) -> "list[float]":
    """`phi(h) phi(k) He_{n-1}(h) He_{n-1}(k) / n!` for n = 1 .. terms: the Hermite series of the bivariate normal's excess over independence."""
    base = _density(h) * _density(k)
    out: "list[float]" = []
    he_h_prev = 0.0
    he_h = 1.0
    he_k_prev = 0.0
    he_k = 1.0
    factorial = 1.0
    for n in range(1, terms + 1):
        factorial = factorial * n
        out += [base * he_h * he_k / factorial]
        next_h = h * he_h - (n - 1) * he_h_prev
        next_k = k * he_k - (n - 1) * he_k_prev
        he_h_prev, he_h = he_h, next_h
        he_k_prev, he_k = he_k, next_k
    return out


def series_value(sums: "list[float]", rho: float) -> float:
    total = 0.0
    power = 1.0
    for term in sums:
        power = power * rho
        total = total + term * power
    return total


def latent_correlation(sums: "list[float]", observed: float) -> float:
    """The latent correlation at which the series' sum meets the observed cross-products (bisection on [0, CORR_MOST])."""
    if observed <= 0.0:
        return 0.0
    if series_value(sums, CORR_MOST) <= observed:
        return CORR_MOST
    low = 0.0
    high = CORR_MOST
    for _step in range(60):
        middle = 0.5 * (low + high)
        if series_value(sums, middle) < observed:
            low = middle
        else:
            high = middle
    return 0.5 * (low + high)


# -- AR(1) arithmetic in one pass --------------------------------------------------------------------


def ar_quadratic(first: "list[float]", second: "list[float]", rho: float) -> float:
    """sum over j, k of first_j second_k rho^|j - k| in one forward and one backward pass."""
    count = len(first)
    total = 0.0
    carried = 0.0
    for j in range(count):
        if j:
            carried = rho * (carried + second[j - 1])
        total = total + first[j] * (second[j] + carried)
    carried = 0.0
    for j in range(count - 2, -1, -1):
        carried = rho * (carried + second[j + 1])
        total = total + first[j] * carried
    return total


def _line(times: "list[float]", values: "list[float]") -> "tuple[float, float, list[float]] | None":
    """Each patient's own least-squares line through (time, value): its level at time 0, its slope and its residuals."""
    count = len(times)
    if count < 3:
        return None
    mt = _mean(times)
    mv = _mean(values)
    sxx = 0.0
    sxy = 0.0
    for at in range(count):
        dt = times[at] - mt
        sxx = sxx + dt * dt
        sxy = sxy + dt * (values[at] - mv)
    if sxx <= 1e-12:
        return None
    slope = sxy / sxx
    level = mv - slope * mt
    residuals = [values[at] - level - slope * times[at] for at in range(count)]
    return level, slope, residuals


def _through(times: "list[float]", values: "list[float]") -> "tuple[float, float] | None":
    """The least-squares line through two points or more: its level at time 0 and its slope; None where the times do not move."""
    count = len(times)
    if count < 2:
        return None
    mt = _mean(times)
    mv = _mean(values)
    sxx = 0.0
    sxy = 0.0
    for at in range(count):
        dt = times[at] - mt
        sxx = sxx + dt * dt
        sxy = sxy + dt * (values[at] - mv)
    if sxx <= 1e-12:
        return None
    slope = sxy / sxx
    return mv - slope * mt, slope


def _line_noise(times: "list[float]", rho: float) -> "tuple[float, float, float]":
    """The noise covariance of a line's (level at 0, slope) per unit noise variance under AR(1) noise of coefficient `rho`."""
    count = len(times)
    ones = [1.0 for _t in times]
    s0 = float(count)
    s1 = 0.0
    s2 = 0.0
    for t in times:
        s1 = s1 + t
        s2 = s2 + t * t
    det = s0 * s2 - s1 * s1
    if det <= 1e-12:
        return 0.0, 0.0, 0.0
    # (X'X)^-1 = [[s2, -s1], [-s1, s0]] / det; X' Omega X by the one-pass sums.
    o00 = ar_quadratic(ones, ones, rho)
    o01 = ar_quadratic(ones, times, rho)
    o11 = ar_quadratic(times, times, rho)
    i00, i01, i11 = s2 / det, -s1 / det, s0 / det
    a00 = i00 * o00 + i01 * o01
    a01 = i00 * o01 + i01 * o11
    a10 = i01 * o00 + i11 * o01
    a11 = i01 * o01 + i11 * o11
    v00 = a00 * i00 + a01 * i01
    v01 = a00 * i01 + a01 * i11
    v11 = a10 * i01 + a11 * i11
    return v00, v01, v11


def _line_trace(times: "list[float]", rho: float) -> float:
    """tr((X'X)^-1 X' Omega X) of a line through (1, time) under AR(1) noise of coefficient `rho`."""
    count = len(times)
    ones = [1.0 for _t in times]
    s1 = 0.0
    s2 = 0.0
    for t in times:
        s1 = s1 + t
        s2 = s2 + t * t
    det = count * s2 - s1 * s1
    if det <= 1e-12:
        return 1.0
    o00 = ar_quadratic(ones, ones, rho)
    o01 = ar_quadratic(ones, times, rho)
    o11 = ar_quadratic(times, times, rho)
    return (s2 * o00 - 2.0 * s1 * o01 + count * o11) / det


@dataclasses.dataclass(frozen=True)
class Seen:
    """One patient's line through its residuals: its level at time 0 and slope (or its level alone) and their noise covariance."""

    patient: int
    level: float
    slope: "float | None"
    v00: float
    v01: float
    v11: float


def random_part(seen: "list[Seen]", steps: int = 400) -> "tuple[float, float, float, dict[int, float], dict[int, float]]":
    """The random level's and slope's variances and covariance by EM with each patient's noise known (maximum likelihood), and each patient's predictions.

    Each patient's (level, slope) is its own line's, read with noise of the
    covariance its rows' times and the AR(1) noise give; a patient of one
    row reads its level alone. The E step takes each patient's posterior
    mean and covariance under the current spread; the M step the mean and
    spread of those. The predictions returned are the last E step's
    posterior means, the shape `_shape` keeps.
    """
    levels = [one.level for one in seen]
    s00 = max(1e-6, 0.5 * _spread(levels) * _spread(levels))
    slopes = [one.slope for one in seen if one.slope is not None]
    s11 = max(1e-8, 0.5 * _spread(slopes) * _spread(slopes)) if len(slopes) >= 2 else 1e-8
    s01 = 0.0
    mu0 = _mean(levels)
    mu1 = _mean(slopes) if slopes else 0.0
    predicted_level: "dict[int, float]" = {}
    predicted_slope: "dict[int, float]" = {}
    for _step in range(steps):
        t00 = 0.0
        t01 = 0.0
        t11 = 0.0
        m0 = 0.0
        m1 = 0.0
        means: "list[tuple[int, float, float, float, float, float]]" = []
        for one in seen:
            if one.slope is None:
                total = s00 + one.v00
                k0 = s00 / total
                k1 = s01 / total
                d0 = one.level - mu0
                p0 = mu0 + k0 * d0
                p1 = mu1 + k1 * d0
                c00 = s00 - s00 * s00 / total
                c01 = s01 - s00 * s01 / total
                c11 = s11 - s01 * s01 / total
            else:
                a00 = s00 + one.v00
                a01 = s01 + one.v01
                a11 = s11 + one.v11
                det = a00 * a11 - a01 * a01
                if det <= 1e-300:
                    continue
                i00, i01, i11 = a11 / det, -a01 / det, a00 / det
                # K = S P^-1
                k00 = s00 * i00 + s01 * i01
                k01 = s00 * i01 + s01 * i11
                k10 = s01 * i00 + s11 * i01
                k11 = s01 * i01 + s11 * i11
                d0 = one.level - mu0
                d1 = one.slope - mu1
                p0 = mu0 + k00 * d0 + k01 * d1
                p1 = mu1 + k10 * d0 + k11 * d1
                # C = S - K S
                c00 = s00 - (k00 * s00 + k01 * s01)
                c01 = s01 - (k00 * s01 + k01 * s11)
                c11 = s11 - (k10 * s01 + k11 * s11)
            means += [(one.patient, p0, p1, c00, c01, c11)]
            m0 = m0 + p0
            m1 = m1 + p1
        if not means:
            break
        count = float(len(means))
        mu0_new = m0 / count
        mu1_new = m1 / count
        for _patient, p0, p1, c00, c01, c11 in means:
            d0 = p0 - mu0_new
            d1 = p1 - mu1_new
            t00 = t00 + d0 * d0 + c00
            t01 = t01 + d0 * d1 + c01
            t11 = t11 + d1 * d1 + c11
        new00 = max(1e-10, t00 / count)
        new11 = max(1e-12, t11 / count)
        new01 = _bounded(t01 / count, -CORR_MOST * math.sqrt(new00 * new11), CORR_MOST * math.sqrt(new00 * new11))
        moved = abs(new00 - s00) + abs(new11 - s11) + abs(new01 - s01) + abs(mu0_new - mu0) + abs(mu1_new - mu1)
        s00, s01, s11, mu0, mu1 = new00, new01, new11, mu0_new, mu1_new
        for patient, p0, p1, _c00, _c01, _c11 in means:
            predicted_level[patient] = p0 - mu0
            predicted_slope[patient] = p1 - mu1
        if moved < 1e-12 * (1.0 + s00):
            break
    return s00, s01, s11, predicted_level, predicted_slope


def _ar_inverse_rows(rows: "list[list[float]]", rho: float) -> "list[list[float]]":
    """Each row of `Omega^-1 X` for a patient's rows `X` in order, Omega the stationary AR(1) correlation (tridiagonal inverse, one pass)."""
    count = len(rows)
    if count == 0:
        return []
    width = len(rows[0])
    if count == 1:
        return [list(rows[0])]
    scale = 1.0 / (1.0 - rho * rho)
    out: "list[list[float]]" = []
    for j in range(count):
        diagonal = 1.0 if j == 0 or j == count - 1 else 1.0 + rho * rho
        line = [diagonal * rows[j][a] for a in range(width)]
        if j > 0:
            for a in range(width):
                line[a] = line[a] - rho * rows[j - 1][a]
        if j < count - 1:
            for a in range(width):
                line[a] = line[a] - rho * rows[j + 1][a]
        out += [[value * scale for value in line]]
    return out


def _small_inverse(matrix: "list[list[float]]") -> "list[list[float]] | None":
    lower = cholesky(matrix, 0.0)
    return _inverse(lower) if lower is not None else None


def gls_fit(design: "list[list[float]]", response: "list[float]", groups: "list[list[int]]", unit_times: "list[float]",
            names: "list[str]", level_var: float, cov01: float, slope_var: float, noise_var: float, lag: float) -> "Fit | None":
    """The fixed part by generalised least squares under the random level and slope and the AR(1) noise, errors robust to the patients, each term but the intercept and the time under `GATE_Z` set aside and the rest fitted again.

    Each patient's covariance is `noise_var Omega + Z S Z'` (Z its rows' (1,
    time), S the random part); its inverse is taken by the push-through
    identity, so S needs no inverse (a slope spread of nought stands).
    """
    keep = list(range(len(names)))
    found: "tuple[list[float], list[float]] | None" = None
    for _pass in range(2):
        found = _gls_once([[row[a] for a in keep] for row in design], response, groups, unit_times, level_var, cov01,
                          slope_var, noise_var, lag)
        if found is None:
            return None
        beta, errors = found
        kept_now = [keep[place] for place in range(len(keep))
                    if names[keep[place]] in ("intercept", "t")
                    or (errors[place] > 0.0 and abs(beta[place] / errors[place]) >= GATE_Z)]
        if kept_now == keep:
            break
        keep = kept_now
        found = None
    if found is None:
        found = _gls_once([[row[a] for a in keep] for row in design], response, groups, unit_times, level_var, cov01,
                          slope_var, noise_var, lag)
        if found is None:
            return None
    beta, errors = found
    coefficients = [0.0 for _name in names]
    zs = [0.0 for _name in names]
    for place in range(len(keep)):
        coefficients[keep[place]] = beta[place]
        zs[keep[place]] = beta[place] / errors[place] if errors[place] > 0.0 else 0.0
    return Fit(tuple(names), tuple(coefficients), tuple(zs))


def _gls_once(design: "list[list[float]]", response: "list[float]", groups: "list[list[int]]", unit_times: "list[float]",
              level_var: float, cov01: float, slope_var: float, noise_var: float, lag: float) -> "tuple[list[float], list[float]] | None":
    width = len(design[0]) if design else 0
    if width == 0:
        return None
    s2 = max(noise_var, 1e-12)
    sigma = [[level_var, cov01], [cov01, slope_var]]
    cross = [[0.0 for _b in range(width)] for _a in range(width)]
    right = [0.0 for _a in range(width)]
    held: "list[tuple[list[int], list[list[float]], list[list[float]], list[list[float]], list[list[float]]]]" = []
    for rows in groups:
        if not rows:
            continue
        x = [design[at] for at in rows]
        z = [[1.0, unit_times[at]] for at in rows]
        w = _ar_inverse_rows(x, lag)
        u = _ar_inverse_rows(z, lag)
        # A = Z' O^-1 Z, B = Z' O^-1 X; H = S (I + A S / s2)^-1.
        a = [[0.0, 0.0], [0.0, 0.0]]
        b = [[0.0 for _k in range(width)] for _r in range(2)]
        for j in range(len(rows)):
            for r in range(2):
                for c in range(2):
                    a[r][c] = a[r][c] + z[j][r] * u[j][c]
                for k in range(width):
                    b[r][k] = b[r][k] + z[j][r] * w[j][k]
        g = [[(1.0 if r == c else 0.0) + (a[r][0] * sigma[0][c] + a[r][1] * sigma[1][c]) / s2 for c in range(2)] for r in range(2)]
        det = g[0][0] * g[1][1] - g[0][1] * g[1][0]
        if abs(det) <= 1e-300:
            return None
        gi = [[g[1][1] / det, -g[0][1] / det], [-g[1][0] / det, g[0][0] / det]]
        h = [[sigma[r][0] * gi[0][c] + sigma[r][1] * gi[1][c] for c in range(2)] for r in range(2)]
        for j in range(len(rows)):
            xj = x[j]
            wj = w[j]
            yj = response[rows[j]]
            for k in range(width):
                if wj[k] == 0.0:
                    continue
                target = cross[k]
                for m in range(width):
                    target[m] = target[m] + wj[k] * xj[m] / s2
                right[k] = right[k] + wj[k] * yj / s2
        # minus B' H B / s2^2 and B' H c / s2^2 (c = Z' O^-1 y).
        zy = [0.0, 0.0]
        for j in range(len(rows)):
            for r in range(2):
                zy[r] = zy[r] + u[j][r] * response[rows[j]]
        hb = [[h[r][0] * b[0][k] + h[r][1] * b[1][k] for k in range(width)] for r in range(2)]
        hc = [h[r][0] * zy[0] + h[r][1] * zy[1] for r in range(2)]
        for k in range(width):
            for m in range(width):
                cross[k][m] = cross[k][m] - (b[0][k] * hb[0][m] + b[1][k] * hb[1][m]) / (s2 * s2)
            right[k] = right[k] - (b[0][k] * hc[0] + b[1][k] * hc[1]) / (s2 * s2)
        held += [(rows, x, z, w, [[h[0][0], h[0][1]], [h[1][0], h[1][1]]])]
    for k in range(width):
        for m in range(k):
            middle = 0.5 * (cross[k][m] + cross[m][k])
            cross[k][m] = middle
            cross[m][k] = middle
    lower = cholesky(cross)
    if lower is None:
        return None
    beta = _solved(lower, right)
    # Robust errors: each patient's score X' V^-1 r.
    scores: "dict[int, list[float]]" = {}
    for place in range(len(held)):
        rows, x, z, w, h = held[place]
        residual = [response[rows[j]] - fitted_value(tuple(beta), x[j]) for j in range(len(rows))]
        omega_r = _ar_inverse_rows([[value] for value in residual], lag)
        xr = [0.0 for _k in range(width)]
        zr = [0.0, 0.0]
        bz = [[0.0 for _k in range(width)] for _r in range(2)]
        for j in range(len(rows)):
            for k in range(width):
                xr[k] = xr[k] + x[j][k] * omega_r[j][0]
                for r in range(2):
                    bz[r][k] = bz[r][k] + z[j][r] * w[j][k]
            for r in range(2):
                zr[r] = zr[r] + z[j][r] * omega_r[j][0]
        hz = [h[r][0] * zr[0] + h[r][1] * zr[1] for r in range(2)]
        scores[place] = [xr[k] / s2 - (bz[0][k] * hz[0] + bz[1][k] * hz[1]) / (s2 * s2) for k in range(width)]
    return beta, _robust_errors(lower, scores, width)


def _reliable(rated: "list[tuple[float, float]]") -> "list[float]":
    """The predictions of the patients read with a reliability of `RELIABLE` or more where `PATIENTS_AT_LEAST` such stand, else of the more reliable half."""
    sure = [value for reliability, value in rated if reliability >= RELIABLE]
    if len(sure) >= PATIENTS_AT_LEAST:
        return sure
    ranked = sorted(rated)
    return [value for _reliability, value in ranked[len(ranked) // 2:]]


def _residual_lag(series: "list[list[float]]") -> float:
    num = 0.0
    den = 0.0
    for values in series:
        for at in range(len(values)):
            den = den + values[at] * values[at]
            if at:
                num = num + values[at] * values[at - 1]
    return num / den if den > 0.0 else 0.0


def calibrated_lag(observed: float, times_sample: "list[list[float]]", detrended: bool) -> float:
    """The AR(1) coefficient whose short detrended series read the observed pooled lag-one correlation (simulated on the patients' own times)."""
    if not times_sample:
        return _bounded(observed, LAG_LEAST, LAG_MOST)
    grid: "list[float]" = []
    seen: "list[float]" = []
    stream = stream_of(12345, 678)
    steps = 30
    for step in range(steps + 1):
        rho = LAG_LEAST + (LAG_MOST - LAG_LEAST) * step / steps
        series: "list[list[float]]" = []
        scale = math.sqrt(max(1e-12, 1.0 - rho * rho))
        for times in times_sample:
            draws: "list[float]" = []
            last = 0.0
            for at in range(len(times)):
                shock = next_normal(stream)
                last = shock if at == 0 else rho * last + scale * shock
                draws += [last]
            if detrended:
                found = _line(times, draws)
                if found is None:
                    continue
                series += [found[2]]
            else:
                centre = _mean(draws)
                series += [[value - centre for value in draws]]
        grid += [rho]
        seen += [_residual_lag(series)]
    # The seen values rise with rho; read the observed one off the curve.
    if observed <= seen[0]:
        return grid[0]
    for at in range(1, len(seen)):
        if observed <= seen[at]:
            below = seen[at - 1]
            above = seen[at]
            part = (observed - below) / (above - below) if above > below else 0.5
            return grid[at - 1] + (grid[at] - grid[at - 1]) * part
    return grid[-1]


# -- reading the table ------------------------------------------------------------------------------


@dataclasses.dataclass
class _Table:
    names: "list[str]"
    rows: int
    person: str
    patient: "list[int]"
    patients: int
    members: "list[list[int]]"


def _patients_of(cells: "list[str]") -> "tuple[list[int], list[list[int]]]":
    """Each row's patient (-1 where the person cell is empty) and each patient's rows in table order."""
    code: "dict[str, int]" = {}
    patient: "list[int]" = []
    members: "list[list[int]]" = []
    for row in range(len(cells)):
        key = _bare(cells[row])
        if not key:
            patient += [-1]
            continue
        if key not in code:
            code[key] = len(members)
            members += [[]]
        at = code[key]
        patient += [at]
        members[at] += [row]
    return patient, members


def _constant_within(cells: "list[str]", members: "list[list[int]]") -> bool:
    """A column every patient of two present cells or more holds one value in (99 per cent of them), with two values or more over the patients."""
    checked = 0
    constant = 0
    seen: "dict[str, int]" = {}
    for rows in members:
        values = [_bare(cells[row]) for row in rows if not _absent(cells[row])]
        if values:
            seen[values[0]] = 1
        if len(values) < 2:
            continue
        checked += 1
        first = values[0]
        if all(value == first for value in values):
            constant += 1
    return checked > 0 and constant >= 0.99 * checked and len(seen) >= 2


def _ordered_rows(members: "list[list[int]]", anchor: "list[int | None] | None", position: "list[float | None] | None") -> "list[list[int]]":
    """Each patient's rows in time order: the anchor's moment, then the position, then the table's order."""
    out: "list[list[int]]" = []
    for rows in members:
        keyed: "list[tuple[int, float, int]]" = []
        for row in rows:
            moment = anchor[row] if anchor is not None else None
            place = position[row] if position is not None else None
            keyed += [(moment if moment is not None else 0, place if place is not None else 0.0, row)]
        out += [[row for _moment, _place, row in sorted(keyed)]]
    return out


def _is_position(values: "list[float | None]", ordered: "list[list[int]]") -> bool:
    """A whole-number column that rises within 95 per cent of the patients of two rows or more, in their time order."""
    checked = 0
    rising = 0
    for rows in ordered:
        if len(rows) < 2:
            continue
        got = [values[row] for row in rows]
        known: "list[float]" = []
        for value in got:
            if value is not None:
                known += [value]
        if len(known) != len(got):
            return False
        checked += 1
        if all(_whole(value) for value in known) and all(known[at] < known[at + 1] for at in range(len(known) - 1)):
            rising += 1
    return checked > 0 and rising >= 0.95 * checked


def _counting_from_one(values: "list[float | None]", ordered: "list[list[int]]") -> bool:
    """Whether the position column reads 1, 2, ... within 99 per cent of the patients."""
    good = 0
    for rows in ordered:
        if all(values[rows[at]] == float(at + 1) for at in range(len(rows))):
            good += 1
    return good >= 0.99 * len(ordered)


def _census(lengths: "list[int]") -> "dict[str, object]":
    counts: "dict[int, int]" = {}
    for length in lengths:
        counts[length] = (counts[length] if length in counts else 0) + 1
    if len(counts) <= CENSUS_CAP:
        return {"counts": [[length, counts[length]] for length in sorted(counts)]}
    return {"quantiles": _quantile_grid([float(length) for length in lengths], GAP_GRID), "patients": len(lengths)}


def census_lengths(census: "dict[str, object]", patients: int) -> "list[int]":
    """`patients` numbers of rows, sorted, read off a census at even shares."""
    listed: "list[int]" = []
    if "counts" in census:
        pairs = census["counts"]
        if isinstance(pairs, list):
            for pair in pairs:
                if isinstance(pair, list) and len(pair) == 2 and isinstance(pair[0], int) and isinstance(pair[1], int):
                    listed += [pair[0] for _k in range(pair[1])]
    elif "quantiles" in census:
        grid = census["quantiles"]
        if isinstance(grid, list):
            values = [float(value) for value in grid if isinstance(value, (int, float))]
            if values:
                listed = [floor_of(_from_grid(values, (k + 0.5) / patients) + 0.5) for k in range(patients)]
    if not listed or patients <= 0:
        return []
    listed = sorted(listed)
    if len(listed) == patients:
        return listed
    return [listed[min(len(listed) - 1, ((2 * k + 1) * len(listed)) // (2 * patients))] for k in range(patients)]


# -- the columns of the patient a fixed part reads --------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class PatientColumn:
    """A patient-fixed column as a fixed part reads it: a label's levels (each but the reference an indicator) or a number's centre and spread."""

    column: str
    kind: str
    levels: "tuple[str, ...]"
    centre: float
    spread: float


def _patient_columns_read(columns: "dict[str, list[str]]", fixed: "list[str]", members: "list[list[int]]") -> "list[PatientColumn]":
    out: "list[PatientColumn]" = []
    for name in fixed:
        cells = columns[name]
        firsts: "list[str]" = []
        for rows in members:
            found = ""
            for row in rows:
                if not _absent(cells[row]):
                    found = _bare(cells[row])
                    break
            firsts += [found]
        present = [cell for cell in firsts if cell]
        numbers = [_number(cell) for cell in present]
        known = [value for value in numbers if value is not None]
        counts: "dict[str, int]" = {}
        for cell in present:
            counts[cell] = (counts[cell] if cell in counts else 0) + 1
        if len(known) >= 0.95 * len(present) and len(counts) > LEVELS_AT_MOST:
            out += [PatientColumn(name, "number", (), _mean(known), max(_spread(known), 1e-9))]
            continue
        if 2 <= len(counts) <= LEVELS_AT_MOST:
            ranked = [level for _many, level in sorted((-counts[level], level) for level in counts)]
            out += [PatientColumn(name, "label", tuple(ranked), 0.0, 1.0)]
    return out


def patient_values(patient_column: PatientColumn, cell: str) -> "list[float]":
    """A patient's fixed column as the design's numbers: a label's indicators (none for its reference), or a number standardized (0 where absent)."""
    text = _bare(cell)
    if patient_column.kind == "number":
        value = _number(text)
        return [0.0 if value is None else (value - patient_column.centre) / patient_column.spread]
    return [1.0 if text == level else 0.0 for level in patient_column.levels[1:]]


def _term_names(patient_columns: "list[PatientColumn]", by_time: bool) -> "list[str]":
    names = ["intercept", "t", "t2", "rows"]
    for patient_column in patient_columns:
        if patient_column.kind == "number":
            names += [f"{patient_column.column}"]
        else:
            names += [f"{patient_column.column}={level}" for level in patient_column.levels[1:]]
    if by_time:
        for patient_column in patient_columns:
            if patient_column.kind == "label" and len(patient_column.levels) <= BY_LEVELS:
                names += [f"t*{patient_column.column}={level}" for level in patient_column.levels[1:]]
                names += [f"t2*{patient_column.column}={level}" for level in patient_column.levels[1:]]
    return names


def design_row(patient_columns: "list[PatientColumn]", patient_cells: "list[str]", t: float, rows_score: float, by_time: bool) -> "list[float]":
    """One row of a fixed part's design: intercept, time, its square, the patient's rows, its fixed columns, the time by small labels."""
    out = [1.0, t, t * t, rows_score]
    labels: "list[tuple[PatientColumn, list[float]]]" = []
    for at in range(len(patient_columns)):
        values = patient_values(patient_columns[at], patient_cells[at])
        out += values
        labels += [(patient_columns[at], values)]
    if by_time:
        for patient_column, values in labels:
            if patient_column.kind == "label" and len(patient_column.levels) <= BY_LEVELS:
                out += [t * value for value in values]
                out += [t * t * value for value in values]
    return out


def gated_fit(design: "list[list[float]]", response: "list[float]", clusters: "list[int]", names: "list[str]", binary: bool) -> "Fit | None":
    """The fixed part: fitted, each term but the intercept and the time under `GATE_Z` set aside, fitted again on the rest."""
    first = probit(design, [int(y) for y in response], clusters) if binary else least_squares(design, response, clusters)
    if first is None:
        return None
    beta, errors = first
    keep: "list[int]" = []
    for a in range(len(names)):
        z = beta[a] / errors[a] if errors[a] > 0.0 else 0.0
        if names[a] in ("intercept", "t") or abs(z) >= GATE_Z:
            keep += [a]
    narrowed = [[row[a] for a in keep] for row in design]
    second = probit(narrowed, [int(y) for y in response], clusters) if binary else least_squares(narrowed, response, clusters)
    if second is None:
        return None
    beta2, errors2 = second
    coefficients = [0.0 for _name in names]
    zs = [0.0 for _name in names]
    for place in range(len(keep)):
        coefficients[keep[place]] = beta2[place]
        zs[keep[place]] = beta2[place] / errors2[place] if errors2[place] > 0.0 else 0.0
    return Fit(tuple(names), tuple(coefficients), tuple(zs))


def fitted_value(coefficients: "tuple[float, ...]", row: "list[float]") -> float:
    total = 0.0
    for a in range(len(row)):
        total = total + coefficients[a] * row[a]
    return total


def _floats(value: object) -> "tuple[float, ...]":
    if not isinstance(value, list):
        raise TypeError("an inside record's numbers are written as a list")
    out: "list[float]" = []
    for one in value:
        if isinstance(one, bool) or not isinstance(one, (int, float)):
            raise TypeError("an inside record's numbers are numbers")
        out += [float(one)]
    return tuple(out)


# -- the producer ----------------------------------------------------------------------------------


def _time_axes(ordered: "list[list[int]]", anchor: "list[int | None] | None") -> "tuple[list[float], list[float] | None]":
    total_rows = max([row for rows in ordered for row in rows] + [-1]) + 1
    positions = [0.0 for _row in range(total_rows)]
    years: "list[float] | None" = [0.0 for _row in range(total_rows)] if anchor is not None else None
    for rows in ordered:
        start: "int | None" = None
        for place in range(len(rows)):
            row = rows[place]
            positions[row] = float(place)
            if years is not None and anchor is not None:
                moment = anchor[row]
                if moment is not None and start is None:
                    start = moment
                years[row] = (moment - start) / SECONDS_A_YEAR if moment is not None and start is not None else 0.0
    return positions, years


def _axis_choice(values: "list[float | None]", ordered: "list[list[int]]", positions: "list[float]", years: "list[float] | None") -> str:
    """Positions or years: the axis on which each patient's own line leaves the smaller pooled share of its spread."""
    if years is None:
        return AXIS_POSITION
    left = {AXIS_POSITION: 0.0, AXIS_YEARS: 0.0}
    for rows in ordered:
        kept = [row for row in rows if values[row] is not None]
        if len(kept) < 3:
            continue
        readings = [typing.cast(float, values[row]) for row in kept]
        for axis, times in ((AXIS_POSITION, positions), (AXIS_YEARS, years)):
            found = _line([times[row] for row in kept], readings)
            if found is None:
                continue
            for residual in found[2]:
                left[axis] = left[axis] + residual * residual
    return AXIS_YEARS if left[AXIS_YEARS] < left[AXIS_POSITION] else AXIS_POSITION


def _scaled(values: "list[float | None]") -> "tuple[list[float | None], str, float, float, list[float]]":
    """A column's readings on its scale, the scale's name, the centre and spread, and its quantile grid."""
    known = [value for value in values if value is not None]
    centre = _mean(known)
    spread = max(_spread(known), 1e-12)
    grid = _quantile_grid(known, SHAPE_GRID)
    out: "list[float | None]" = [None for _value in values]
    if abs(_skew(known)) < SKEW_CUT:
        for row in range(len(values)):
            value = values[row]
            if value is not None:
                out[row] = (value - centre) / spread
        return out, SCALE_LINEAR, centre, spread, grid
    places = [row for row in range(len(values)) if values[row] is not None]
    scores = mid_scores([typing.cast(float, values[row]) for row in places])
    for at in range(len(places)):
        out[places[at]] = scores[at]
    return out, SCALE_NORMAL, centre, spread, grid


def score_of(entry: "dict[str, object]", cell: str) -> "float | None":
    """A cell of a repeated number column on its entry's scale (the twin's own cells read as the real ones were)."""
    value = _number(cell)
    if value is None:
        return None
    scale = entry["scale"]
    centre = typing.cast(float, entry["centre"])
    spread = typing.cast(float, entry["spread"])
    if scale == SCALE_LINEAR:
        return (value - centre) / spread
    grid = list(_floats(entry["grid"]))
    return chain_walk.normal_score(_share_on_grid(grid, value))


def _shape(values: "list[float]") -> "list[float]":
    """The standardized quantile function of a random effect's predictions on `SHAPE_GRID` points."""
    if len(values) < 3:
        return [chain_walk.normal_score((k + 0.5) / SHAPE_GRID) for k in range(SHAPE_GRID)]
    centre = _mean(values)
    spread = _spread(values)
    if spread <= 0.0:
        return [chain_walk.normal_score((k + 0.5) / SHAPE_GRID) for k in range(SHAPE_GRID)]
    standard = [(value - centre) / spread for value in values]
    ordered = sorted(standard)
    out: "list[float]" = []
    for k in range(SHAPE_GRID):
        place = (k + 0.5) / SHAPE_GRID * len(ordered) - 0.5
        below = floor_of(place)
        part = place - below
        low = ordered[max(0, min(len(ordered) - 1, below))]
        high = ordered[max(0, min(len(ordered) - 1, below + 1))]
        out += [low + (high - low) * part]
    return out


def _residuals(design: "list[list[float]]", response: "list[float]", rows_read: "list[int]",
               coefficients: "tuple[float, ...]") -> "dict[int, float]":
    out: "dict[int, float]" = {}
    for at in range(len(rows_read)):
        out[rows_read[at]] = response[at] - fitted_value(coefficients, design[at])
    return out


@dataclasses.dataclass(frozen=True)
class RandomRead:
    """The random part read from a fixed part's residuals: the noise and its lag-one term, the level's and slope's spread and covariance, each patient's predictions."""

    residual: "dict[int, float]"
    seen: "list[Seen]"
    lag: float
    noise_var: float
    level_var: float
    cov01: float
    slope_var: float
    predicted: "dict[int, float]"
    predicted_slopes: "dict[int, float]"


def _random_read(ordered: "list[list[int]]", residual: "dict[int, float]", times: "list[float]", spread_t: float) -> "RandomRead | None":
    """Each patient's own line through its residuals; the noise and its AR(1) term from the lines of three rows or more; the random level and slope by EM with each patient's noise known."""
    lines: "list[tuple[int, float, float, list[float], list[float]]]" = []
    for patient in range(len(ordered)):
        kept = [row for row in ordered[patient] if row in residual]
        if len(kept) < 3:
            continue
        own_times = [times[row] / spread_t for row in kept]
        found = _line(own_times, [residual[row] for row in kept])
        if found is not None:
            lines += [(patient, found[0], found[1], found[2], own_times)]
    if len(lines) < PATIENTS_AT_LEAST:
        return None
    dof = 0.0
    sse = 0.0
    for _patient, _level, _slope, residuals, _times in lines:
        dof = dof + len(residuals) - 2
        for value in residuals:
            sse = sse + value * value
    observed_lag = _residual_lag([residuals for _p, _l, _s, residuals, _t in lines])
    sample = [own_times for _p, _l, _s, _r, own_times in lines[: min(len(lines), 400)]]
    lag = calibrated_lag(observed_lag, sample, True)
    # The noise variance with each line's effective degrees of freedom under AR(1): E sse = s2 sum (n - tr((X'X)^-1 X' Omega X)).
    effective = 0.0
    for _patient, _level, _slope, residuals, own_times in lines:
        effective = effective + max(0.5, len(residuals) - _line_trace(own_times, lag))
    noise_var = sse / max(1.0, effective) if effective > 0.0 else sse / max(1.0, dof)
    seen: "list[Seen]" = []
    for patient in range(len(ordered)):
        kept = [row for row in ordered[patient] if row in residual]
        if not kept:
            continue
        own_times = [times[row] / spread_t for row in kept]
        left = [residual[row] for row in kept]
        if len(kept) >= 2:
            through = _through(own_times, left)
            if through is not None:
                v00, v01, v11 = _line_noise(own_times, lag)
                seen += [Seen(patient, through[0], through[1], v00 * noise_var, v01 * noise_var, v11 * noise_var)]
                continue
        ones = [1.0 for _v in left]
        seen += [Seen(patient, _mean(left), None, noise_var * ar_quadratic(ones, ones, lag) / (len(left) * len(left)), 0.0, 0.0)]
    level_var, cov01, slope_var, predicted, predicted_slopes = random_part(seen)
    return RandomRead(residual, seen, lag, noise_var, level_var, cov01, slope_var, predicted, predicted_slopes)


def _number_entry(
    name: str,
    values: "list[float | None]",
    ordered: "list[list[int]]",
    positions: "list[float]",
    years: "list[float] | None",
    patient_columns: "list[PatientColumn]",
    patient_cells: "list[list[str]]",
    rows_scores: "list[float]",
) -> "tuple[dict[str, object], dict[int, float], dict[int, float]] | None":
    """One repeated number column's entry, with each row's residual and each patient's predicted level (for the cross-column parts)."""
    scaled, scale, centre, spread, grid = _scaled(values)
    axis = _axis_choice(values, ordered, positions, years)
    times = years if axis == AXIS_YEARS and years is not None else positions
    spread_t = _spread([times[row] for rows in ordered for row in rows]) or 1.0
    names = _term_names(patient_columns, True)
    design: "list[list[float]]" = []
    response: "list[float]" = []
    clusters: "list[int]" = []
    rows_read: "list[int]" = []
    for patient in range(len(ordered)):
        for row in ordered[patient]:
            value = scaled[row]
            if value is None:
                continue
            design += [design_row(patient_columns, patient_cells[patient], times[row] / spread_t, rows_scores[patient], True)]
            response += [value]
            clusters += [patient]
            rows_read += [row]
    if len(response) < 3 * len(names):
        return None
    fit = gated_fit(design, response, clusters, names, False)
    if fit is None:
        return None
    unit_times = [times[row] / spread_t for row in rows_read]
    groups: "list[list[int]]" = []
    at = 0
    while at < len(rows_read):
        end = at
        while end < len(rows_read) and clusters[end] == clusters[at]:
            end += 1
        groups += [list(range(at, end))]
        at = end
    # The fixed part by least squares first, then by generalised least squares under the random part read from its
    # residuals (twice): rows of a long patient no longer outweigh the patients, so a trend by group is the
    # patients' own (on an invented visits table the arm's change a visit read -0.61 by rows against -0.81 by a
    # mixed model).
    read = _random_read(ordered, _residuals(design, response, rows_read, fit.coefficients), times, spread_t)
    if read is None:
        return None
    for _round in range(2):
        refit = gls_fit(design, response, groups, unit_times, names, read.level_var, read.cov01, read.slope_var,
                        read.noise_var, read.lag)
        if refit is None:
            break
        again = _random_read(ordered, _residuals(design, response, rows_read, refit.coefficients), times, spread_t)
        if again is None:
            break
        fit = refit
        read = again
    residual = read.residual
    seen = read.seen
    level_var, cov01, slope_var = read.level_var, read.cov01, read.slope_var
    predicted, predicted_slopes = read.predicted, read.predicted_slopes
    noise_var, lag = read.noise_var, read.lag
    corr = 0.0
    if level_var > 1e-9 and slope_var > 1e-11:
        corr = _bounded(cov01 / math.sqrt(level_var * slope_var), -CORR_MOST, CORR_MOST)
    if slope_var <= 1e-11:
        slope_var = 0.0
    # The predictions' standardized shapes, each from the patients whose own line reads it reliably (the share of
    # its spread that is the patient's, not the noise, at least `RELIABLE`; else the more reliable half): a short
    # patient's prediction is shrunk to the centre and carries the noise's normal shape, which would hide the shape.
    level_predictions = _reliable([(level_var / (level_var + one.v00), predicted[one.patient]) for one in seen
                                   if one.slope is not None and one.patient in predicted and level_var + one.v00 > 0.0])
    slope_predictions = _reliable([(slope_var / (slope_var + one.v11), predicted_slopes[one.patient]) for one in seen
                                   if one.slope is not None and one.patient in predicted_slopes
                                   and slope_var + one.v11 > 0.0])
    predicted_levels: "dict[int, float]" = {}
    for patient in sorted(predicted):
        predicted_levels[patient] = predicted[patient]
    entry: "dict[str, object]" = {
        "column": name,
        "scale": scale,
        "centre": centre,
        "spread": spread,
        "grid": grid,
        "axis": axis,
        "time_spread": spread_t,
        "terms": list(fit.terms),
        "coefficients": list(fit.coefficients),
        "level_sd": math.sqrt(level_var),
        "slope_sd": math.sqrt(slope_var),
        "corr": corr,
        "noise_sd": math.sqrt(max(noise_var, 1e-12)),
        "lag1": lag,
        "level_shape": _shape(level_predictions),
        "slope_shape": _shape(slope_predictions),
    }
    return entry, residual, predicted_levels


def _binary_entry(
    name: str,
    cells: "list[str]",
    ordered: "list[list[int]]",
    times: "list[float]",
    time_spread: float,
    patient_columns: "list[PatientColumn]",
    patient_cells: "list[list[str]]",
    rows_scores: "list[float]",
    numbers: "list[tuple[dict[str, object], list[float | None]]]",
) -> "dict[str, object] | None":
    """One repeated yes/no column's latent threshold: the marginal probit and the latent correlation within a patient."""
    counts: "dict[str, int]" = {}
    for cell in cells:
        if not _absent(cell):
            text = _bare(cell)
            counts[text] = (counts[text] if text in counts else 0) + 1
    if len(counts) != 2:
        return None
    pair = sorted(counts)
    yes = _yes_of(pair[0], pair[1], counts)
    names = _term_names(patient_columns, False) + [f"row:{_text(entry['column'])}" for entry, _scores in numbers]
    design: "list[list[float]]" = []
    outcome: "list[float]" = []
    clusters: "list[int]" = []
    rows_read: "list[int]" = []
    for patient in range(len(ordered)):
        for row in ordered[patient]:
            if _absent(cells[row]):
                continue
            line = design_row(patient_columns, patient_cells[patient], times[row] / time_spread, rows_scores[patient], False)
            for _entry, scores in numbers:
                score = scores[row]
                line += [0.0 if score is None else score]
            design += [line]
            outcome += [1.0 if _bare(cells[row]) == yes else 0.0]
            clusters += [patient]
            rows_read += [row]
    if len(outcome) < 5 * len(names):
        return None
    fit = gated_fit(design, outcome, clusters, names, True)
    if fit is None:
        return None
    eta: "dict[int, float]" = {}
    shares: "dict[int, float]" = {}
    seen: "dict[int, float]" = {}
    for at in range(len(rows_read)):
        value = _bounded(fitted_value(fit.coefficients, design[at]), -7.0, 7.0)
        eta[rows_read[at]] = value
        shares[rows_read[at]] = fast_cdf(value)
        seen[rows_read[at]] = outcome[at]
    sums = [0.0 for _k in range(HERMITE_TERMS)]
    observed = 0.0
    pairs = 0
    for rows in ordered:
        kept = [row for row in rows if row in eta][:PAIR_ROWS]
        for a in range(len(kept)):
            for b in range(a + 1, len(kept)):
                first, second = kept[a], kept[b]
                terms = hermite_terms(eta[first], eta[second])
                for k in range(HERMITE_TERMS):
                    sums[k] = sums[k] + terms[k]
                observed = observed + (seen[first] - shares[first]) * (seen[second] - shares[second])
                pairs += 1
    if pairs < PATIENTS_AT_LEAST:
        return None
    rho = latent_correlation(sums, observed)
    return {
        "column": name,
        "yes": yes,
        "no": pair[1] if pair[0] == yes else pair[0],
        "terms": list(fit.terms),
        "coefficients": list(fit.coefficients),
        "latent_corr": rho,
    }


def _yes_of(first: str, second: str, counts: "dict[str, int]") -> str:
    """Which of two spellings is the event: Y, yes, true, 1, positive by name, else the rarer."""
    if not isinstance(first, str):
        raise TypeError("synthtwin reads a table's cells as text only.")
    if not isinstance(second, str):
        raise TypeError("synthtwin reads a table's cells as text only.")
    low_first = first.lower()
    low_second = second.lower()
    for word in ("y", "yes", "true", "1", "positive", "pos", "t"):
        if low_first == word:
            return first
        if low_second == word:
            return second
    return first if counts[first] <= counts[second] else second


def _gap_entry(anchor: "list[int | None]", ordered: "list[list[int]]", lengths: "list[int]") -> "dict[str, object] | None":
    """The anchor's gaps between a patient's consecutive rows: their quantile function, the pace a patient keeps, the serial term, the pace by the rows."""
    gaps: "list[float]" = []
    owner: "list[int]" = []
    for patient in range(len(ordered)):
        moments = [anchor[row] for row in ordered[patient]]
        for place in range(1, len(moments)):
            before = moments[place - 1]
            after = moments[place]
            if before is None or after is None:
                continue
            gaps += [float(after - before)]
            owner += [patient]
    if len(gaps) < 3 * PATIENTS_AT_LEAST:
        return None
    scores = mid_scores(gaps)
    # THE ROWS TERM: a patient of many rows has shorter gaps where a follow-up stops at a fixed length; the gap's score
    # on the patient's rows score by least squares, and the pace read on what is left.
    rows_scores = mid_scores([float(length) for length in lengths])
    sxy = 0.0
    sxx = 0.0
    for at in range(len(gaps)):
        own = rows_scores[owner[at]]
        sxy = sxy + own * scores[at]
        sxx = sxx + own * own
    rows_term = _bounded(sxy / sxx if sxx > 0.0 else 0.0, -CORR_MOST, CORR_MOST)
    scores = [scores[at] - rows_term * rows_scores[owner[at]] for at in range(len(gaps))]
    by_patient: "dict[int, list[float]]" = {}
    for at in range(len(gaps)):
        patient = owner[at]
        if patient not in by_patient:
            by_patient[patient] = []
        by_patient[patient] += [scores[at]]
    # One-way moments: the share of a gap's score a patient keeps. EACH PATIENT'S MEAN IS TAKEN ONCE (Codex's review of
    # batch 4w, item 15) and read again below for the deviations and the paces: a patient of a million rows costs a
    # million steps here, never a million times a million.
    patients = sorted(by_patient)
    within = 0.0
    within_dof = 0.0
    means: "list[float]" = []
    sizes: "list[float]" = []
    for patient in patients:
        values = by_patient[patient]
        centre = _mean(values)
        means += [centre]
        sizes += [float(len(values))]
        for value in values:
            within = within + (value - centre) * (value - centre)
        within_dof = within_dof + len(values) - 1
    within_var = within / within_dof if within_dof > 0.0 else 1.0
    grand = _mean(scores)
    between = 0.0
    weight = 0.0
    weight2 = 0.0
    for at in range(len(means)):
        between = between + sizes[at] * (means[at] - grand) * (means[at] - grand)
        weight = weight + sizes[at]
        weight2 = weight2 + sizes[at] * sizes[at]
    groups = float(len(means))
    n0 = (weight - weight2 / weight) / (groups - 1.0) if groups > 1.0 else 1.0
    between_ms = between / (groups - 1.0) if groups > 1.0 else 0.0
    pace_var = max(0.0, (between_ms - within_var) / n0) if n0 > 0.0 else 0.0
    pace_share = _bounded(pace_var / (pace_var + within_var) if pace_var + within_var > 0.0 else 0.0, 0.0, CORR_MOST)
    deviations = [[value - means[at] for value in by_patient[patients[at]]] for at in range(len(patients))]
    observed_lag = _residual_lag(deviations)
    sample = [[float(k) for k in range(len(by_patient[patient]))] for patient in patients[:400]]
    lag = calibrated_lag(observed_lag, sample, False)
    paces = means
    pace_rows = _corr(paces, [rows_scores[patient] for patient in patients]) if len(paces) >= 3 else 0.0
    return {
        "quantiles": _quantile_grid(gaps, GAP_GRID),
        "pace_share": pace_share,
        "lag1": _bounded(lag, LAG_LEAST, LAG_MOST),
        "pace_rows": _bounded(pace_rows, -CORR_MOST, CORR_MOST),
        "rows_term": rows_term,
    }


def _fit_sample(ordered: "list[list[int]]") -> "list[list[int]]":
    """The patients the fits read: every one where the table holds at most `FIT_ROWS` rows; else whole patients in a fixed order of their places (SplitMix64 of each place) until `FIT_ROWS` rows are read, the others' rows left empty."""
    total = sum(len(rows_of) for rows_of in ordered)
    if total <= FIT_ROWS:
        return ordered
    ranked = [place for _word, place in sorted((_mixed(place), place) for place in range(len(ordered)))]
    chosen = [False for _rows_of in ordered]
    held = 0
    for place in ranked:
        if held + len(ordered[place]) > FIT_ROWS:
            continue
        chosen[place] = True
        held += len(ordered[place])
    return [ordered[place] if chosen[place] else [] for place in range(len(ordered))]


def _cells_of_patients(columns: "dict[str, list[str]]", patient_columns: "list[PatientColumn]", ordered: "list[list[int]]") -> "list[list[str]]":
    out: "list[list[str]]" = []
    for rows_of in ordered:
        line: "list[str]" = []
        for patient_column in patient_columns:
            found = ""
            for row in rows_of:
                if not _absent(columns[patient_column.column][row]):
                    found = _bare(columns[patient_column.column][row])
                    break
            line += [found]
        out += [line]
    return out


def _key_column(columns: "dict[str, list[str]]", candidates: "list[str]") -> str:
    """The key of a keyed long table: the label of 3 to 100 levels that fixes the most other labels (each other label equal to its commonest value within the key's level on 90 per cent of the rows); the first in the table's order on a tie."""
    labels: "list[str]" = []
    level_count: "dict[str, int]" = {}
    for name in candidates:
        seen: "dict[str, int]" = {}
        for cell in columns[name]:
            seen[_bare(cell)] = 1
        level_count[name] = len(seen)
        if 2 <= len(seen) <= 100:
            labels += [name]
    best = ""
    best_fixed = -1
    for key in labels:
        if level_count[key] < 3:
            continue
        keys = [_bare(cell) for cell in columns[key]]
        fixed = 0
        for other in labels:
            if other == key:
                continue
            counts: "dict[tuple[str, str], int]" = {}
            for row in range(len(keys)):
                pair = (keys[row], _bare(columns[other][row]))
                counts[pair] = (counts[pair] if pair in counts else 0) + 1
            commonest: "dict[str, int]" = {}
            for pair in counts:
                if pair[0] not in commonest or counts[pair] > commonest[pair[0]]:
                    commonest[pair[0]] = counts[pair]
            held = 0
            for level in commonest:
                held += commonest[level]
            if held >= 0.9 * len(keys):
                fixed += 1
        if fixed > best_fixed:
            best_fixed = fixed
            best = key
    return best


def _key_entries(
    columns: "dict[str, list[str]]",
    key: str,
    content: "list[str]",
    ordered: "list[list[int]]",
    years: "list[float] | None",
    patient_columns: "list[PatientColumn]",
    patient_cells: "list[list[str]]",
    rows_scores: "list[float]",
) -> "list[dict[str, object]]":
    """Each key level's trajectory: its value column (the first of the row's content numeric on 90 per cent of the level's cells), the label that sets the value's scale (a unit) where one does, and the two-level model on the level's rows alone."""
    keys = [_bare(cell) for cell in columns[key]]
    counts: "dict[str, int]" = {}
    for level in keys:
        counts[level] = (counts[level] if level in counts else 0) + 1
    out: "list[dict[str, object]]" = []
    for _many, level in sorted((-counts[level], level) for level in counts):
        ordered_k = [[row for row in rows_of if keys[row] == level] for rows_of in ordered]
        if sum(1 for rows_of in ordered_k if len(rows_of) >= 2) < PATIENTS_AT_LEAST:
            continue
        rows_k = [row for rows_of in ordered_k for row in rows_of]
        value_name = ""
        for name in content:
            filled = [columns[name][row] for row in rows_k if not _absent(columns[name][row])]
            numeric = [value for value in (_number(cell) for cell in filled) if value is not None]
            distinct: "dict[float, int]" = {}
            for value in numeric:
                distinct[value] = 1
            if filled and len(numeric) >= 0.9 * len(filled) and len(distinct) >= 3:
                value_name = name
                break
        if not value_name:
            continue
        readings = [_number(columns[value_name][row]) for row in rows_k]
        unit = _scale_label(columns, content, value_name, rows_k, readings)
        groups: "dict[str, list[int]]" = {}
        for at in range(len(rows_k)):
            if readings[at] is None:
                continue
            group = _bare(columns[unit][rows_k[at]]) if unit else ""
            if group not in groups:
                groups[group] = []
            groups[group] += [at]
        values: "list[float | None]" = [None for _row in columns[key]]
        for group in sorted(groups):
            places = groups[group]
            scores = mid_scores([typing.cast(float, readings[at]) for at in places])
            for k in range(len(places)):
                values[rows_k[places[k]]] = scores[k]
        positions = [0.0 for _row in columns[key]]
        for rows_of in ordered_k:
            for place in range(len(rows_of)):
                positions[rows_of[place]] = float(place)
        built = _number_entry(value_name, values, ordered_k, positions, years, patient_columns, patient_cells, rows_scores)
        if built is None:
            continue
        entry = built[0]
        entry["key"] = key
        entry["level"] = level
        entry["unit"] = unit
        out += [entry]
    return out


def _scale_label(columns: "dict[str, list[str]]", content: "list[str]", value_name: str, rows_k: "list[int]",
                 readings: "list[float | None]") -> str:
    """The label among the row's content (2 to 10 levels on the key's rows) whose groups' typical values stand `SCALE_RATIO` times apart or more (a unit), else ''; the widest such."""
    best = ""
    best_ratio = SCALE_RATIO
    for name in content:
        if name == value_name:
            continue
        groups: "dict[str, list[float]]" = {}
        for at in range(len(rows_k)):
            value = readings[at]
            if value is None:
                continue
            group = _bare(columns[name][rows_k[at]])
            if group not in groups:
                groups[group] = []
            groups[group] += [abs(value)]
        if not 2 <= len(groups) <= 10:
            continue
        middles: "list[float]" = []
        for group in sorted(groups):
            if len(groups[group]) >= 3:
                ordered = sorted(groups[group])
                middles += [ordered[len(ordered) // 2]]
        if len(middles) < 2 or min(middles) <= 0.0:
            continue
        ratio = max(middles) / min(middles)
        if ratio >= best_ratio:
            best_ratio = ratio
            best = name
    return best


def zone_from_columns(columns: "dict[str, list[str]]", person: str, identifiers: "tuple[str, ...]" = ()) -> "dict[str, object] | None":
    """The trajectories zone of a table of several rows a patient, or None where the table holds no such patients.

    `columns` maps each column's name to its cells as read; `person` names
    the column of the patient's key; `identifiers` the columns read as
    record numbers (never read here). Only the zone's model is returned:
    no row, no patient, no key.
    """
    if person not in columns:
        return None
    names = [name for name in columns]
    rows = len(columns[person])
    patient, members = _patients_of(columns[person])
    several = sum(1 for rows_of in members if len(rows_of) >= 2)
    if several < PATIENTS_AT_LEAST or rows < 2 * len(members) * 0.6:
        return None
    usable = [name for name in names if name != person and name not in identifiers]
    # The anchor: the date column that moves within the most patients.
    anchor_name = ""
    anchor: "list[int | None] | None" = None
    kinds: "dict[str, str]" = {}
    best = 0
    dates: "list[str]" = []
    for name in usable:
        cells = columns[name]
        read = [None if _absent(cell) else moment_of(cell) for cell in cells]
        present = sum(1 for cell in cells if not _absent(cell))
        known = [moment for moment in read if moment is not None]
        if present == 0 or len(known) < 0.95 * present:
            continue
        dates += [name]
        kinds[name] = known[0].kind
        moving = 0
        for rows_of in members:
            seen = {read[row].seconds for row in rows_of if read[row] is not None}  # type: ignore[union-attr]
            if len(seen) >= 2:
                moving += 1
        if moving > best:
            best = moving
            anchor_name = name
            anchor = [moment.seconds if moment is not None else None for moment in read]
    # THE NUMBERS ARE READ ONE COLUMN AT A TIME (lane IN-8, plan P4-D502): which columns are numbers is
    # kept, and a column's readings are made again where they are used, so no list of every number column's
    # readings is held at once.
    numbers_of: "dict[str, bool]" = {}
    for name in usable:
        if name in dates:
            continue
        cells = columns[name]
        filled = sum(1 for cell in cells if not _absent(cell))
        numeric = sum(1 for cell in cells if _number(cell) is not None)
        if filled and numeric >= 0.9 * filled:
            numbers_of[name] = True
    # The position: a whole-number column rising within the patients in the anchor's order.
    first_order = _ordered_rows(members, anchor, None)
    position_name = ""
    position_readings: "list[float | None]" = []
    for name in usable:
        if name in numbers_of:
            readings = [_number(cell) for cell in columns[name]]
            if _is_position(readings, first_order):
                position_name = name
                position_readings = readings
                break
            del readings
    ordered = _ordered_rows(members, anchor, position_readings if position_name else None)
    fixed = [name for name in usable if name not in dates and name != position_name and _constant_within(columns[name], members)]
    # A label of three levels or more that moves within patients makes the table a keyed long table: its
    # per-key trajectories wait for the keyed rows' own zone, so no entry is written for it here.
    keyed = False
    repeated_numbers: "list[str]" = []
    repeated_binaries: "list[str]" = []
    for name in usable:
        if name in dates or name == position_name or name in fixed:
            continue
        cells = columns[name]
        levels: "dict[str, int]" = {}
        for cell in cells:
            if not _absent(cell):
                levels[_bare(cell)] = 1
        if len(levels) == 2:
            repeated_binaries += [name]
        elif name in numbers_of and len(levels) >= 3:
            repeated_numbers += [name]
        elif len(levels) >= 3:
            keyed = True
    lengths = [len(rows_of) for rows_of in members]
    zone: "dict[str, object]" = {
        "version": ZONE_VERSION,
        "person": person,
        "rows": rows,
        "census": _census(lengths),
        "order": {"anchor": anchor_name, "kind": kinds[anchor_name] if anchor_name else "", "dates": dates},
        "position": {"column": position_name,
                     "from_one": bool(position_name) and _counting_from_one(position_readings, ordered)},
        "fixed": fixed,
        "gaps": None,
        "numbers": [],
        "binaries": [],
        "keyed": keyed,
    }
    if anchor is not None:
        gaps = _gap_entry(anchor, ordered, lengths)
        if gaps is not None:
            span = [moment for moment in anchor if moment is not None]
            gaps["first"] = min(span)
            gaps["last"] = max(span)
            # The longest span a patient holds: a follow-up the real table stops at (a study's years) is never passed.
            longest = 0
            for rows_of in ordered:
                held_moments = [anchor[row] for row in rows_of if anchor[row] is not None]
                stamped = [typing.cast(int, moment) for moment in held_moments]
                if len(stamped) >= 2:
                    longest = max(longest, max(stamped) - min(stamped))
            gaps["span_most"] = longest
            # THE PACES: each patient's mean gap (its span over its gaps, patients of two rows or more) as a quantile
            # function, and its normal score's correlation with the patient's rows; a twin patient draws its pace, and
            # its span is its pace times its gaps, so where visits come at a fixed interval every patient keeps it.
            paces: "list[float]" = []
            pace_tie: "list[float]" = []
            rows_by_patient = mid_scores([float(length) for length in lengths])
            for place in range(len(ordered)):
                stamped_span = typing.cast("list[int]", [anchor[row] for row in ordered[place] if anchor[row] is not None])
                if len(stamped_span) >= 2:
                    paces += [float(max(stamped_span) - min(stamped_span)) / (len(stamped_span) - 1)]
                    pace_tie += [rows_by_patient[place]]
            if len(paces) >= PATIENTS_AT_LEAST:
                gaps["paces"] = _quantile_grid(paces, GAP_GRID)
                gaps["pace_tie"] = _bounded(_corr(mid_scores(paces), pace_tie), -CORR_MOST, CORR_MOST)
            # THE FIRST MOMENTS: each patient's first anchor as a quantile function (as the marginals keep a date),
            # and its normal score's correlation with the patient's rows (a late entrant has fewer visits where a
            # table stops on a day), so a date anchor's calendar is the real one once the gaps are drawn.
            firsts: "list[float]" = []
            first_rows: "list[float]" = []
            rows_scored = mid_scores([float(length) for length in lengths])
            for place in range(len(ordered)):
                stamped_first = [anchor[row] for row in ordered[place] if anchor[row] is not None]
                if stamped_first:
                    firsts += [float(min(typing.cast("list[int]", stamped_first)))]
                    first_rows += [rows_scored[place]]
            gaps["starts"] = _quantile_grid(firsts, GAP_GRID)
            gaps["calendar"] = _quantile_grid([float(moment) for moment in anchor if moment is not None], GAP_GRID)
            gaps["start_rows"] = _bounded(_corr(mid_scores(firsts), first_rows), -CORR_MOST, CORR_MOST)
            zone["gaps"] = gaps
    patient_columns = _patient_columns_read(columns, fixed, ordered)
    # THE FITS READ AT MOST `FIT_ROWS` ROWS, OF WHOLE PATIENTS (a fixed choice, the same for the same table): the
    # two-level models of a 2,000,000-row table are read from 200,000 of its rows, as the relations' pair structure
    # is; the census, the first days, the paces and the gaps read every patient.
    fitted = _fit_sample(ordered)
    zone["patient_columns"] = [{"column": c.column, "kind": c.kind, "levels": list(c.levels), "centre": c.centre,
                                "spread": c.spread} for c in patient_columns]
    if keyed:
        # A KEYED LONG TABLE (a label of three levels or more moving within patients: an item, a test): each key's
        # values follow a trajectory of their own, read on the key's rows alone (`_key_entries`); the table's other
        # repeated columns move with the key's value as one row's content, so whatever a row's cells hold together
        # (a unit, a range, a flag, a copy of the value) stays together.
        bundle = [name for name in usable if name not in dates and name != position_name and name not in fixed]
        key = _key_column(columns, bundle)
        if key:
            content = [name for name in bundle if name != key]
            patient_cells_k = _cells_of_patients(columns, patient_columns, ordered)
            rows_scores_k = mid_scores([float(length) for length in lengths])
            positions_all, years_all = _time_axes(ordered, anchor)
            zone["keys"] = _key_entries(columns, key, content, fitted, years_all, patient_columns, patient_cells_k,
                                        rows_scores_k)
            zone["key"] = key
            zone["bundle"] = content
            del positions_all
        return zone
    patient_cells: "list[list[str]]" = []
    for rows_of in ordered:
        line: "list[str]" = []
        for patient_column in patient_columns:
            found = ""
            for row in rows_of:
                if not _absent(columns[patient_column.column][row]):
                    found = _bare(columns[patient_column.column][row])
                    break
            line += [found]
        patient_cells += [line]
    rows_scores = mid_scores([float(length) for length in lengths])
    positions, years = _time_axes(ordered, anchor)
    number_entries: "list[dict[str, object]]" = []
    residuals: "list[dict[int, float]]" = []
    levels_of: "list[dict[int, float]]" = []
    position_readings = []
    for name in repeated_numbers:
        built = _number_entry(name, [_number(cell) for cell in columns[name]], fitted, positions, years, patient_columns,
                              patient_cells, rows_scores)
        if built is None:
            continue
        number_entries += [built[0]]
        residuals += [built[1]]
        levels_of += [built[2]]
    zone["numbers"] = number_entries
    zone["within_corr"] = _cross_correlation(residuals)
    zone["level_corr"] = _cross_correlation(levels_of)
    axis = AXIS_YEARS if any(entry["axis"] == AXIS_YEARS for entry in number_entries) else AXIS_POSITION
    times = years if axis == AXIS_YEARS and years is not None else positions
    time_spread = _spread([times[row] for rows_of in ordered for row in rows_of]) or 1.0
    # A repeated number's scores are read by the yes/no fits on the fitted rows alone, so they are made there
    # (lane IN-8): every other row holds None, a pointer, and no score.
    scored: "list[tuple[dict[str, object], list[float | None]]]" = []
    for entry in number_entries:
        column = _text(entry["column"])
        cells = columns[column]
        at_fitted: "list[float | None]" = [None] * len(cells)
        for rows_of in fitted:
            for row in rows_of:
                at_fitted[row] = score_of(entry, cells[row])
        scored += [(entry, at_fitted)]
        del cells
    binary_entries: "list[dict[str, object]]" = []
    for name in repeated_binaries:
        built_binary = _binary_entry(name, columns[name], fitted, times, time_spread, patient_columns, patient_cells,
                                     rows_scores, scored)
        if built_binary is not None:
            built_binary["axis"] = axis
            built_binary["time_spread"] = time_spread
            binary_entries += [built_binary]
    zone["binaries"] = binary_entries
    return zone


def _cross_correlation(by_row: "list[dict[int, float]]") -> "list[list[float]]":
    """Pairwise correlations of keyed values (rows' residuals, patients' levels) over the keys both hold."""
    size = len(by_row)
    out = [[1.0 if a == b else 0.0 for b in range(size)] for a in range(size)]
    for a in range(size):
        for b in range(a + 1, size):
            shared = [key for key in by_row[a] if key in by_row[b]]
            if len(shared) < PATIENTS_AT_LEAST:
                continue
            value = _bounded(_corr([by_row[a][key] for key in shared], [by_row[b][key] for key in shared]),
                             -CORR_MOST, CORR_MOST)
            out[a][b] = value
            out[b][a] = value
    return out


# -- the zone checked --------------------------------------------------------------------------------


def checked_zone(zone: object) -> "dict[str, object] | None":
    """The zone where it holds the keys and kinds this version writes, else None (a twin is then made without it)."""
    if not isinstance(zone, dict):
        return None
    for key in _ZONE_KEYS:
        if key not in zone:
            return None
    if zone["version"] != ZONE_VERSION or not isinstance(zone["person"], str):
        return None
    if not isinstance(zone["numbers"], list) or not isinstance(zone["binaries"], list):
        return None
    if not isinstance(zone["census"], dict) or not isinstance(zone["order"], dict) or not isinstance(zone["position"], dict):
        return None
    for entry in list(zone["numbers"]) + list(zone["binaries"]):
        if not isinstance(entry, dict) or "column" not in entry or "coefficients" not in entry or "terms" not in entry:
            return None
        try:
            if len(_floats(entry["coefficients"])) != len(typing.cast("list[str]", entry["terms"])):
                return None
        except TypeError:
            return None
    return typing.cast("dict[str, object]", zone)


# -- the generator ---------------------------------------------------------------------------------


@dataclasses.dataclass
class Applied:
    """What `applied` changed: the columns it read, each in the twin's new row order, and that order (None where no row moved)."""

    columns: "dict[str, list[str]]"
    order: "list[int] | None"
    notes: "list[str]"


def needed_columns(zone_given: object) -> "list[str]":
    """The columns of the twin a zone reads and writes: the person's, the fixed ones, the position, the dates, the repeated numbers and yes/no outcomes."""
    zone = checked_zone(zone_given)
    if zone is None:
        return []
    out = [_text(zone["person"])]
    for name in typing.cast("list[object]", zone["fixed"]):
        if isinstance(name, str) and name not in out:
            out += [name]
    position = typing.cast("dict[str, object]", zone["position"])
    order = typing.cast("dict[str, object]", zone["order"])
    listed: "list[object]" = [position["column"]]
    dates = order["dates"]
    if isinstance(dates, list):
        listed += dates
    for entry in list(typing.cast("list[object]", zone["numbers"])) + list(typing.cast("list[object]", zone["binaries"])):
        if isinstance(entry, dict):
            listed += [entry["column"]]
    if "key" in zone and "bundle" in zone:
        listed += [zone["key"]]
        bundle = zone["bundle"]
        if isinstance(bundle, list):
            listed += bundle
    for name in listed:
        if isinstance(name, str) and name and name not in out:
            out += [name]
    return out


def applied(zone_given: object, names: "list[str]", cells_of: "dict[str, list[str]]", seed: int, *,
            timing: bool = True, dealing: bool = True, dates_kept: bool = False,
            kept: "typing.Collection[str]" = (), taken: bool = False) -> Applied:
    """The twin's columns rewritten by a trajectories zone (see the module's text).

    `cells_of` holds at least the columns `needed_columns` names, in the
    twin's row order; `names` are the columns handed; `seed` the twin's
    seed. Every handed column comes back in the new row order, written again
    where the zone writes it; `order` gives, for each new row, the old row
    it came from, so the caller moves every other column the same way. A
    zone this version cannot read, or a twin without the zone's person
    column, comes back untouched (no columns, no order). `timing` and
    `dealing` run the two steps apart (the patients' rows and their timing;
    the values dealt on the time axis the twin then holds), so the dates
    zone's census may run between them at the merge; both, the default,
    are the whole. With `dates_kept` the timing step sets the patients'
    rows and positions only and times no date: every date column keeps its
    cells, moved with their rows (the generate step's setting,
    `twin_with_zone`: the twin's dates are the dates zone's, with the day of
    the month made up, never the real calendar's days this zone holds).
    The dealing step deals no column `kept` names (lane W5-PL): each such
    cell stays on its row, with the row's dates.

    THE CELLS TAKEN (lane W5-2M): with `taken`, each handed column's list
    is taken out of `cells_of` (its name removed from it) and worked on in
    place rather than copied, so a column is held once while the zone
    writes it, never twice; the caller keeps no list it handed. Without
    it, `cells_of` is left as it was. The columns that come back are the
    same either way.
    """
    zone = checked_zone(zone_given)
    if zone is None:
        return Applied({}, None, ["the trajectories zone could not be read, so the twin was made without it"])
    person = _text(zone["person"])
    if person not in cells_of:
        return Applied({}, None, ["the twin has no column of the zone's patients"])
    work: "dict[str, list[str]]" = {}
    for name in names:
        if name not in work:
            work[name] = cells_of[name] if taken else list(cells_of[name])
            if taken:
                del cells_of[name]
    patient, members = _patients_of(work[person])
    if any(code < 0 for code in patient) or not members:
        return Applied({}, None, ["a row of the twin names no patient, so its trajectories were left as made"])
    position = typing.cast("dict[str, object]", zone["position"])
    position_name = _text(position["column"]) if isinstance(position["column"], str) else ""
    order = typing.cast("dict[str, object]", zone["order"])
    anchor_name = _text(order["anchor"]) if isinstance(order["anchor"], str) else ""
    fixed = [name for name in typing.cast("list[str]", zone["fixed"]) if isinstance(name, str) and name in work]
    # THE TWO STEPS (the merge with the dates zone, lane IN-5, may run its own between them): the patients' rows and
    # their timing first, then the values dealt on the time axis the twin then holds.
    layout: "list[int] | None" = None
    if timing:
        # (1) the long patients.
        cut = _recut(zone, work, members, person, fixed)
        if cut is None:
            return Applied({}, None, ["the twin's rows could not be set to the census"])
        members, layout = cut
        # (2) the positions.
        if position_name in work and position["from_one"] is True:
            for rows_of in members:
                for place in range(len(rows_of)):
                    work[position_name][rows_of[place]] = f"{place + 1}"
    # (3) THE ANCHOR TIMED AGAIN FROM ITS GAPS, a date or a clock: each patient keeps its first moment and its later
    # rows stand the real gaps apart, so a patient's span, the hours of a stay and the time since a first visit hold
    # as in the real table; every other date of a row moves with its anchor, so the row's own intervals stand. What a
    # clock says beyond that (rows at night, minutes heaped on five-minute marks, a weekday) is the dates zone's
    # census (lane IN-5).
    gaps = zone["gaps"]
    if timing and not dates_kept and anchor_name in work and isinstance(gaps, dict):
        _dates_again(gaps, typing.cast("list[str]", order["dates"]), anchor_name, work, members, seed)
    if dealing:
        held = frozenset(kept)
        # (4) and (5) the repeated numbers and the yes/no outcomes.
        _numbers_dealt(zone, work, members, fixed, anchor_name, seed, held)
        _binaries_dealt(zone, work, members, anchor_name, seed, held)
        # (6) each key's values, with the content of their rows, on a keyed long table.
        _keys_dealt(zone, work, members, anchor_name, seed, held)
    return Applied(work, layout, [])


def _keys_dealt(zone: "dict[str, object]", work: "dict[str, list[str]]", members: "list[list[int]]", anchor_name: str,
                seed: int, held: "frozenset[str]" = frozenset()) -> None:
    """Each key level's rows: their latent scores under the level's trajectory, and the rows' content (the value and every cell that stands with it) dealt to them in that order, inside each group of the level's scale label.

    A column `held` names stays on its row (lane W5-PL): a date the dates
    zone wrote, or a label its clocks are drawn by (on a charting table, the
    device whose rows are entered as they are charted and on the minute),
    keeps its row's dates; a level whose value column is held is not dealt.
    """
    if "keys" not in zone or "key" not in zone or "bundle" not in zone:
        return
    entries = zone["keys"]
    key = zone["key"]
    bundle = zone["bundle"]
    if not isinstance(entries, list) or not isinstance(key, str) or not isinstance(bundle, list) or key not in work:
        return
    content = [name for name in bundle if isinstance(name, str) and name in work and name not in held]
    patient_columns = _patient_columns_of(zone)
    patient_cells = _patient_cells(patient_columns, work, members)
    rows_scores = mid_scores([float(len(rows_of)) for rows_of in members])
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        level = _text(entry["level"])
        value_name = _text(entry["column"])
        unit = _text(entry["unit"])
        if value_name not in work or (unit and unit not in work) or value_name in held:
            continue
        read = _read_entry(entry)
        pair_lower = cholesky([[1.0, read.corr], [read.corr, 1.0]], 1e-9)
        stream = stream_of(seed, name_salt(f"{key}={level}"))
        latent: "dict[int, float]" = {}
        for p in range(len(members)):
            rows_of = [row for row in members[p] if _bare(work[key][row]) == level]
            if not rows_of:
                continue
            mixed = _times_lower(pair_lower, [next_normal(stream), next_normal(stream)])
            level_draw = _shaped(read.level_shape, mixed[0]) * read.level_sd
            slope_draw = _shaped(read.slope_shape, mixed[1]) * read.slope_sd
            noise = 0.0
            first_moment = _first_moment(work, members[p], anchor_name)
            for place in range(len(rows_of)):
                row = rows_of[place]
                shock = next_normal(stream)
                noise = shock if place == 0 else read.lag * noise + math.sqrt(max(0.0, 1.0 - read.lag * read.lag)) * shock
                if _number(work[value_name][row]) is None:
                    continue
                t = _key_time(entry, work, first_moment, rows_of, place, anchor_name)
                line = design_row(patient_columns, patient_cells[p], t, rows_scores[p], True)
                latent[row] = fitted_value(read.coefficients, line) + level_draw + slope_draw * t + read.noise_sd * noise
        groups: "dict[str, list[int]]" = {}
        for row in sorted(latent):
            group = _bare(work[unit][row]) if unit else ""
            if group not in groups:
                groups[group] = []
            groups[group] += [row]
        moved: "dict[str, list[str]]" = {}
        for name in content:
            moved[name] = list(work[name])
        for group in sorted(groups):
            rows = groups[group]
            sources = [row for _value, row in sorted((typing.cast(float, _number(work[value_name][row])), row) for row in rows)]
            takers = [row for _score, row in sorted((latent[row], row) for row in rows)]
            for rank in range(len(rows)):
                for name in content:
                    moved[name][takers[rank]] = work[name][sources[rank]]
        for name in content:
            work[name] = moved[name]


def _first_moment(work: "dict[str, list[str]]", rows_all: "list[int]", anchor_name: str) -> "int | None":
    """A patient's earliest anchor moment, None where it holds none (or the table has no anchor)."""
    if anchor_name not in work:
        return None
    first: "int | None" = None
    for row in rows_all:
        cell = work[anchor_name][row]
        moment = moment_of(cell) if not _absent(cell) else None
        if moment is not None and (first is None or moment.seconds < first):
            first = moment.seconds
    return first


def _key_time(entry: "dict[str, object]", work: "dict[str, list[str]]", first: "int | None", rows_of: "list[int]",
              place: int, anchor_name: str) -> float:
    """A key's row on its entry's time axis: its place among the patient's rows of the key, or the years since the patient's first dated row."""
    spread = float(typing.cast(float, entry["time_spread"]))
    if entry["axis"] == AXIS_YEARS and anchor_name in work:
        here_cell = work[anchor_name][rows_of[place]]
        here = moment_of(here_cell) if not _absent(here_cell) else None
        if first is None or here is None:
            return 0.0
        return (here.seconds - first) / SECONDS_A_YEAR / spread
    return float(place) / spread


def _row_order(members: "list[list[int]]", rows: int) -> "list[int]":
    out: "list[int]" = []
    for rows_of in members:
        out += rows_of
    if len(out) != rows:
        raise ValueError("the patients' rows do not cover the twin")
    return out


def _recut(zone: "dict[str, object]", work: "dict[str, list[str]]", members: "list[list[int]]", person: str,
           fixed: "list[str]") -> "tuple[list[list[int]], list[int] | None] | None":
    """Each twin patient's number of rows set by rank to the census; rows move to patients of too few, the patient's fixed cells written on them; the rows then laid out patient by patient.

    Returns the patients' rows in the new order and, where a row moved,
    the layout (each new row's old row); None where the census cannot be
    met (the twin is then left as made).
    """
    census = zone["census"]
    if not isinstance(census, dict):
        return members, None
    count = len(members)
    targets = census_lengths(typing.cast("dict[str, object]", census), count)
    rows = len(work[person])
    if len(targets) != count:
        return members, None
    total = sum(targets)
    # The total held to the twin's rows: one row more or fewer on the longest patients.
    place = count - 1
    guard = 0
    while total != rows and guard < 4 * rows + 4 * count:
        step = 1 if total < rows else -1
        if targets[place] + step >= 1:
            targets[place] += step
            total += step
        place = place - 1 if place > 0 else count - 1
        guard += 1
    if total != rows:
        return None
    ranked = [p for _length, p in sorted((len(members[p]), p) for p in range(count))]
    target_of = [0 for _p in range(count)]
    for rank in range(count):
        target_of[ranked[rank]] = targets[rank]
    if all(target_of[p] == len(members[p]) for p in range(count)):
        return members, None

    def cell_of(p: int) -> "tuple[str, ...]":
        first = members[p][0]
        return tuple(work[name][first] for name in fixed)

    spare: "dict[tuple[str, ...], list[int]]" = {}
    for p in range(count):
        extra = len(members[p]) - target_of[p]
        if extra > 0:
            key = cell_of(p)
            if key not in spare:
                spare[key] = []
            spare[key] += members[p][len(members[p]) - extra:]
            members[p] = members[p][: len(members[p]) - extra]
    pool_keys = sorted(spare)
    used: "dict[tuple[str, ...], int]" = {}
    for source in pool_keys:
        used[source] = 0
    # THE DONORS AS ONE QUEUE (Codex's review of batch 4w, item 16): a patient short of rows takes from the donors of
    # its own fixed cells first, then from the pool in the keys' order, starting at the first donor not yet spent; a
    # donor spent is passed once for all, so every patient short of rows reads only the donors it takes from, never
    # the whole pool again (the rows taken, and their order, are those the full walk through the pool took).
    cursor = 0
    for p in range(count):
        need = target_of[p] - len(members[p])
        if need <= 0:
            continue
        key = cell_of(p)
        taken: "list[int]" = []
        if key in spare:
            while need > 0 and used[key] < len(spare[key]):
                taken += [spare[key][len(spare[key]) - 1 - used[key]]]
                used[key] += 1
                need -= 1
        while need > 0 and cursor < len(pool_keys):
            source = pool_keys[cursor]
            while need > 0 and used[source] < len(spare[source]):
                taken += [spare[source][len(spare[source]) - 1 - used[source]]]
                used[source] += 1
                need -= 1
            if used[source] >= len(spare[source]):
                cursor += 1
        first = members[p][0]
        for row in taken:
            work[person][row] = work[person][first]
            for name in fixed:
                work[name][row] = work[name][first]
        members[p] = members[p] + taken
    if any(used[key] < len(spare[key]) for key in spare):
        return None
    # The rows laid out patient by patient, each patient's own rows first.
    layout = _row_order(members, rows)
    for name in work:
        column = work[name]
        work[name] = [column[row] for row in layout]
    out: "list[list[int]]" = []
    at = 0
    for rows_of in members:
        out += [list(range(at, at + len(rows_of)))]
        at += len(rows_of)
    return out, layout


def _dates_again(gaps: "dict[str, object]", dates: "list[str]", anchor_name: str, work: "dict[str, list[str]]",
                 members: "list[list[int]]", seed: int) -> None:
    """Each patient's anchor dates drawn again from its first one by the gap model; the row's other dates moved with it."""
    grid = list(_floats(gaps["quantiles"]))
    pace_share = float(typing.cast(float, gaps["pace_share"]))
    lag = float(typing.cast(float, gaps["lag1"]))
    pace_rows = float(typing.cast(float, gaps["pace_rows"]))
    last_allowed = int(typing.cast(int, gaps["last"]))
    first_allowed = int(typing.cast(int, gaps["first"]))
    span_most = int(typing.cast(int, gaps["span_most"])) if "span_most" in gaps else 0
    stream = stream_of(seed, name_salt(anchor_name) ^ 0x6761707300000000)
    lengths = [float(len(rows_of)) for rows_of in members]
    rows_scores = mid_scores(lengths)
    latent: "list[float]" = []
    owners: "list[tuple[int, int]]" = []
    keep = math.sqrt(max(0.0, 1.0 - pace_share))
    rows_term = float(typing.cast(float, gaps["rows_term"])) if "rows_term" in gaps else 0.0
    for p in range(len(members)):
        mixed = pace_rows * rows_scores[p] + math.sqrt(max(0.0, 1.0 - pace_rows * pace_rows)) * next_normal(stream)
        pace = rows_term * rows_scores[p] + math.sqrt(pace_share) * mixed
        noise = 0.0
        for place in range(1, len(members[p])):
            shock = next_normal(stream)
            noise = shock if place == 1 else lag * noise + math.sqrt(max(0.0, 1.0 - lag * lag)) * shock
            latent += [pace + keep * noise]
            owners += [(p, place)]
    if not latent:
        return
    order = [at for _score, at in sorted((latent[at], at) for at in range(len(latent)))]
    drawn = [0.0 for _at in latent]
    last_point = len(grid) - 1
    for rank in range(len(order)):
        # The nearest point of the gaps' quantile function: every gap drawn is a gap the real table holds.
        drawn[order[rank]] = grid[min(last_point, int((rank + 0.5) / len(order) * last_point + 0.5))]
    gap_of: "dict[tuple[int, int], int]" = {}
    for at in range(len(owners)):
        gap_of[owners[at]] = floor_of(drawn[at] + 0.5)
    span_of = _spans_drawn(gaps, members, rows_scores, seed, anchor_name)
    anchor_cells = work[anchor_name]
    others = [name for name in dates if name != anchor_name and name in work]
    starts = _first_days(gaps, anchor_cells, members, rows_scores, seed, anchor_name)
    firsts: "dict[int, Moment]" = {}
    planned: "dict[int, list[int]]" = {}
    for p in range(len(members)):
        rows_of = members[p]
        found_first = moment_of(anchor_cells[rows_of[0]]) if not _absent(anchor_cells[rows_of[0]]) else None
        if found_first is None:
            continue
        firsts[p] = Moment(starts[p], found_first.kind, found_first.joint) if p in starts else found_first
        steps = [gap_of[(p, place)] for place in range(1, len(rows_of))]
        total = sum(steps)
        if p in span_of and total > 0:
            # The patient's gaps scaled to the pace it drew (its span its pace times its gaps), the gaps' shape within
            # the patient kept.
            target = span_of[p] * len(steps)
            steps = [(step * target) // total for step in steps]
        planned[p] = steps
    # THE GAPS' OWN SHAPE AGAIN: every scaled gap set by its rank among all of them to the real gaps' quantile function
    # (the nearest point), so the gaps hold the real shape exactly while each patient keeps its pace by rank.
    ranked = sorted((planned[p][k], p, k) for p in sorted(planned) for k in range(len(planned[p])))
    for rank in range(len(ranked)):
        _value, p, k = ranked[rank]
        planned[p][k] = floor_of(grid[min(last_point, int((rank + 0.5) / len(ranked) * last_point + 0.5))] + 0.5)
    if span_most > 0:
        _within_spans(planned, span_most)
    moments_of: "dict[int, list[int]]" = {}
    for p in sorted(planned):
        first = firsts[p]
        steps = planned[p]
        total = sum(steps)
        if span_most > 0 and total > span_most:
            # Still past the longest span a real patient holds where no swap could take it in: its gaps drawn closer,
            # in proportion.
            steps = [(step * span_most) // total for step in steps]
        if first.kind == KIND_DATE:
            steps = [floor_of(step / SECONDS_A_DAY + 0.5) * SECONDS_A_DAY for step in steps]
        moments = [first.seconds]
        for step in steps:
            moments += [moments[-1] + step]
        overshoot = moments[-1] - last_allowed
        if overshoot > 0:
            # Past the real table's last date: the whole series moved earlier, never before its first date.
            shift = min(overshoot, max(0, moments[0] - first_allowed))
            if first.kind == KIND_DATE:
                shift = (shift // SECONDS_A_DAY) * SECONDS_A_DAY
            moments = [moment - shift for moment in moments]
        moments_of[p] = moments
    # THE REAL CALENDAR: a date anchor's moments set, by their rank among all of them, to the real moments' quantile
    # function (whole days between its points), so the visits a day, a month and a year are the real ones; within a
    # patient the order stands and a gap moves only by the calendar's local stretch.
    if "calendar" in gaps and all(firsts[p].kind == KIND_DATE for p in moments_of):
        calendar = list(_floats(gaps["calendar"]))
        for round_ in range(CALENDAR_ROUNDS):
            if round_:
                # The gaps the calendar left set back to their exact shape by rank, each patient from its first day.
                _gaps_by_rank(moments_of, grid)
            flat = sorted((moments_of[p][k], p, k) for p in sorted(moments_of) for k in range(len(moments_of[p])))
            for rank in range(len(flat)):
                _moment, p, k = flat[rank]
                value = _from_grid(calendar, (rank + 0.5) / len(flat))
                moments_of[p][k] = floor_of(value / SECONDS_A_DAY + 0.5) * SECONDS_A_DAY
    for p in sorted(moments_of):
        rows_of = members[p]
        first = firsts[p]
        moments = moments_of[p]
        for place in range(len(rows_of)):
            row = rows_of[place]
            old = moment_of(anchor_cells[row]) if not _absent(anchor_cells[row]) else None
            if first.kind == KIND_DATE:
                moments[place] = (moments[place] // SECONDS_A_DAY) * SECONDS_A_DAY
            new_text = moment_text(moments[place], first.kind, first.joint)
            if old is not None:
                moved = moments[place] - old.seconds
                for name in others:
                    cell = work[name][row]
                    other = moment_of(cell) if not _absent(cell) else None
                    if other is not None:
                        work[name][row] = moment_text(other.seconds + moved, other.kind, other.joint)
            anchor_cells[row] = new_text


def _gaps_by_rank(moments_of: "dict[int, list[int]]", grid: "list[float]") -> None:
    """Every patient's gaps set by their rank among all to the real gaps' quantile function (whole days), each patient's moments rebuilt from its first."""
    last_point = len(grid) - 1
    ranked = sorted((moments_of[p][k + 1] - moments_of[p][k], p, k) for p in sorted(moments_of)
                    for k in range(len(moments_of[p]) - 1))
    steps: "dict[int, list[int]]" = {}
    for p in moments_of:
        steps[p] = [0 for _k in range(len(moments_of[p]) - 1)]
    for rank in range(len(ranked)):
        _gap, p, k = ranked[rank]
        value = grid[min(last_point, int((rank + 0.5) / len(ranked) * last_point + 0.5))]
        steps[p][k] = floor_of(value / SECONDS_A_DAY + 0.5) * SECONDS_A_DAY
    for p in moments_of:
        rebuilt = [moments_of[p][0]]
        for step in steps[p]:
            rebuilt += [rebuilt[-1] + step]
        moments_of[p] = rebuilt


def _heap_up(heap: "list[tuple[int, int, int]]", at: int) -> None:
    while at > 0:
        parent = (at - 1) // 2
        if heap[parent] <= heap[at]:
            return
        heap[parent], heap[at] = heap[at], heap[parent]
        at = parent


def _heap_down(heap: "list[tuple[int, int, int]]", size: int) -> None:
    at = 0
    while True:
        left = 2 * at + 1
        right = left + 1
        least = at
        if left < size and heap[left] < heap[least]:
            least = left
        if right < size and heap[right] < heap[least]:
            least = right
        if least == at:
            return
        heap[least], heap[at] = heap[at], heap[least]
        at = least


def _heap_push(heap: "list[tuple[int, int, int]]", size: int, entry: "tuple[int, int, int]") -> int:
    """`entry` put into the heap of `size` entries (the list kept, grown only where it is full); the new size."""
    if size < len(heap):
        heap[size] = entry
    else:
        heap += [entry]
    _heap_up(heap, size)
    return size + 1


def _within_spans(planned: "dict[int, list[int]]", span_most: int) -> None:
    """Each patient past the longest real span gives its largest gap, in turn, for the smallest gap of the patient with the most room that can take it (the smallest place among equal room): the gaps stay the same cells (their shape exact) and the spans come within the real longest.

    The patients with room stand in a binary heap of (minus their room,
    their place, a version), a patient's older entries passed over once
    its room moves, so each swap reads a few entries, not every patient.
    """
    spans: "dict[int, int]" = {}
    smallest: "dict[int, tuple[int, int]]" = {}
    version: "dict[int, int]" = {}
    heap: "list[tuple[int, int, int]]" = []
    size = 0
    for q in planned:
        spans[q] = sum(planned[q])
        version[q] = 0
        if planned[q]:
            smallest[q] = min((planned[q][k], k) for k in range(len(planned[q])))
    for q in sorted(planned):
        if planned[q] and spans[q] < span_most:
            size = _heap_push(heap, size, (spans[q] - span_most, q, 0))

    over = [p for _span, p in sorted((-spans[p], p) for p in planned if spans[p] > span_most)]
    for p in over:
        tries = 0
        while spans[p] > span_most and tries < 4 * len(planned[p]) + 4:
            tries += 1
            large = max((planned[p][k], k) for k in range(len(planned[p])))
            held: "list[tuple[int, int, int]]" = []
            found: "tuple[int, int] | None" = None
            while size > 0:
                top = heap[0]
                size -= 1
                heap[0] = heap[size]
                _heap_down(heap, size)
                _negative, q, seen = top
                if seen != version[q]:
                    continue
                small = smallest[q]
                if q != p and small[0] < large[0] and spans[q] - small[0] + large[0] <= span_most:
                    found = (q, small[1])
                    break
                held += [top]
            for entry in held:
                size = _heap_push(heap, size, entry)
            if found is None:
                break
            q, k = found
            given = planned[p][large[1]]
            taken = planned[q][k]
            planned[p][large[1]] = taken
            planned[q][k] = given
            spans[p] += taken - given
            spans[q] += given - taken
            smallest[q] = min((planned[q][j], j) for j in range(len(planned[q])))
            smallest[p] = min((planned[p][j], j) for j in range(len(planned[p])))
            for moved in (q, p):
                version[moved] += 1
                if planned[moved] and spans[moved] < span_most:
                    size = _heap_push(heap, size, (spans[moved] - span_most, moved, version[moved]))


def _spans_drawn(gaps: "dict[str, object]", members: "list[list[int]]", rows_scores: "list[float]", seed: int,
                 anchor_name: str) -> "dict[int, int]":
    """Each patient of two rows or more's pace (its mean gap): drawn by rank from the real paces, tied to the patient's rows as the real ones are."""
    if "paces" not in gaps or "pace_tie" not in gaps:
        return {}
    grid = list(_floats(gaps["paces"]))
    tie = _bounded(float(typing.cast(float, gaps["pace_tie"])), -CORR_MOST, CORR_MOST)
    stream = stream_of(seed, name_salt(anchor_name) ^ 0x7370616E73000000)
    several = [p for p in range(len(members)) if len(members[p]) >= 2]
    latent = [tie * rows_scores[p] + math.sqrt(max(0.0, 1.0 - tie * tie)) * next_normal(stream) for p in several]
    order = [several[at] for _score, at in sorted((latent[at], at) for at in range(len(several)))]
    out: "dict[int, int]" = {}
    for rank in range(len(order)):
        out[order[rank]] = floor_of(_from_grid(grid, (rank + 0.5) / len(order)) + 0.5)
    return out


def _first_days(gaps: "dict[str, object]", anchor_cells: "list[str]", members: "list[list[int]]",
                rows_scores: "list[float]", seed: int, anchor_name: str) -> "dict[int, int]":
    """Each patient's first day where the anchor is a date of days: drawn by rank from the real first days (between the quantile function's points, whole days), tied to the patient's rows as the real ones are; {} for a clock, whose moments stay the walk's."""
    if "starts" not in gaps or "start_rows" not in gaps:
        return {}
    kinds: "list[str]" = []
    for rows_of in members:
        cell = anchor_cells[rows_of[0]]
        moment = moment_of(cell) if not _absent(cell) else None
        if moment is not None:
            kinds += [moment.kind]
    if not kinds or any(kind != KIND_DATE for kind in kinds):
        return {}
    grid = list(_floats(gaps["starts"]))
    tie = _bounded(float(typing.cast(float, gaps["start_rows"])), -CORR_MOST, CORR_MOST)
    stream = stream_of(seed, name_salt(anchor_name) ^ 0x6669727374730000)
    latent = [tie * rows_scores[p] + math.sqrt(max(0.0, 1.0 - tie * tie)) * next_normal(stream) for p in range(len(members))]
    order = [p for _score, p in sorted((latent[p], p) for p in range(len(members)))]
    out: "dict[int, int]" = {}
    for rank in range(len(order)):
        value = _from_grid(grid, (rank + 0.5) / len(order))
        out[order[rank]] = floor_of(value / SECONDS_A_DAY + 0.5) * SECONDS_A_DAY
    return out


def _times_of(axis: str, time_spread: float, work: "dict[str, list[str]]", members: "list[list[int]]",
              anchor_name: str, rows: int) -> "list[float]":
    times = [0.0 for _row in range(rows)]
    for rows_of in members:
        start: "int | None" = None
        for place in range(len(rows_of)):
            row = rows_of[place]
            if axis == AXIS_YEARS and anchor_name in work:
                cell = work[anchor_name][row]
                moment = moment_of(cell) if not _absent(cell) else None
                if moment is not None and start is None:
                    start = moment.seconds
                value = (moment.seconds - start) / SECONDS_A_YEAR if moment is not None and start is not None else 0.0
            else:
                value = float(place)
            times[row] = value / time_spread
    return times


def _patient_columns_of(zone: "dict[str, object]") -> "list[PatientColumn]":
    out: "list[PatientColumn]" = []
    listed = zone["patient_columns"] if "patient_columns" in zone else []
    if not isinstance(listed, list):
        return out
    for one in listed:
        if not isinstance(one, dict):
            continue
        levels = one["levels"]
        out += [PatientColumn(_text(one["column"]), _text(one["kind"]),
                          tuple(_text(level) for level in (levels if isinstance(levels, list) else [])),
                          float(typing.cast(float, one["centre"])), float(typing.cast(float, one["spread"])))]
    return out


def _patient_cells(patient_columns: "list[PatientColumn]", work: "dict[str, list[str]]", members: "list[list[int]]") -> "list[list[str]]":
    out: "list[list[str]]" = []
    for rows_of in members:
        line: "list[str]" = []
        for patient_column in patient_columns:
            found = ""
            if patient_column.column in work:
                for row in rows_of:
                    if not _absent(work[patient_column.column][row]):
                        found = _bare(work[patient_column.column][row])
                        break
            line += [found]
        out += [line]
    return out


def _shaped(shape: "list[float]", normal: float) -> float:
    """A random effect's standardized value at a normal draw: its shape read at the shares the shape holds its points
    at, `(k + 1/2) / SHAPE_GRID` (`_shape`), and past the shape's two ends its end point plus the draw's distance
    past that end's own normal score (lane STATS-B).

    The shape had been read as an even grid from 0 to 1 (`_from_grid`): every draw then fell between the shape's
    first and last points, the 0.5 per cent tails of the predictions on each side were never drawn and the middle
    was spread over the whole range, so a standard normal shape was drawn with a variance of 0.925, every patient's
    level and slope about 4 per cent short in spread: the clinic visits' twin held an intraclass correlation of
    0.742 to 0.749 against the real 0.756 to 0.761 (K-BC-14, family F11), as a variance short by 7.5 per cent gives.
    """
    count = len(shape)
    if count < 2:
        return shape[0] if shape else normal
    place = chain_walk.normal_cdf(normal) * count - 0.5
    if place <= 0.0:
        return shape[0] + min(0.0, normal - chain_walk.normal_score(0.5 / count))
    if place >= count - 1:
        return shape[count - 1] + max(0.0, normal - chain_walk.normal_score(1.0 - 0.5 / count))
    below = int(place)
    part = place - below
    return shape[below] + (shape[below + 1] - shape[below]) * part


def once_a_value(cells: "list[str]") -> "list[str]":
    """The same cells, each different text held once (lane W5-2M): a list of pointers to one object a value.

    A twin column read back from its held form (`twinstore.column_cells`)
    is a new text object a cell, about fifty bytes beside its characters;
    held this way a column of 2,000,000 rows costs its pointers, eight
    bytes a row, and one object for each different value. Equal cells stay
    equal and every cell reads as it did, so nothing that reads the list by
    value can tell the two apart. A fixed function of the cells; raises
    nothing.
    """
    first: "dict[str, str]" = {}
    out: "list[str]" = []
    for cell in cells:
        if cell not in first:
            first[cell] = cell
        out += [first[cell]]
    return out


@dataclasses.dataclass
class LatentStore:
    """A number column's latent scores, a row each, held as their binary64 bits (lane W5-2M): eight bytes and one a row.

    The repeated numbers are dealt by latent scores drawn for every column
    at once, each patient's levels and each row's shocks correlated across
    the columns, so every column's scores stand together until the last
    is drawn. Held as a dictionary of floats a column (about eighty-five
    bytes a row), the scores of 27 columns at 2,000,000 rows took about
    4.6 GB; held here, about 490 MB. `latent_put` keeps a score exactly
    (its sign, exponent and fraction, by exact arithmetic, -0.0 apart from
    0.0; an infinity or a value that is not a number kept beside, as it
    is); `latent_scores` gives back the dictionary the dealing reads, every
    row that holds one with the very value put, in rising row order.
    """

    bits: bytearray
    present: bytearray
    odd: "dict[int, float]"


def latent_store(rows: int) -> LatentStore:
    """An empty store of ``rows`` rows. Raises nothing for rows of nought or more."""
    return LatentStore(bytearray(8 * rows), bytearray(rows), {})


_FRACTION_BITS = (1 << 52) - 1


def _bits_of(value: float) -> int:
    """A finite binary64 value's 64 bits (sign, exponent, fraction) by exact arithmetic; the sign read off its spelling."""
    sign = 1 if value < 0.0 or (value == 0.0 and repr(value)[0] == "-") else 0
    magnitude = -value if sign else value
    if magnitude == 0.0:
        return sign << 63
    fraction, exponent = math.frexp(magnitude)
    if exponent >= -1021:
        return (sign << 63) | ((exponent + 1022) << 52) | (int(fraction * _TWO_53) - (1 << 52))
    return (sign << 63) | int(math.ldexp(fraction, exponent + 1074))


def _float_of(bits: int) -> float:
    """The finite binary64 value of 64 bits `_bits_of` wrote, by exact arithmetic."""
    sign = -1.0 if bits >> 63 else 1.0
    exponent = (bits >> 52) & 2047
    fraction = bits & _FRACTION_BITS
    if exponent == 0:
        return sign * math.ldexp(float(fraction), -1074)
    return sign * math.ldexp(float(fraction + (1 << 52)), exponent - 1075)


def latent_put(store: LatentStore, row: int, value: float) -> None:
    """Keep ``value`` as row ``row``'s score (a later put replaces an earlier). Raises IndexError for a row outside the store."""
    if not math.isfinite(value):
        store.odd[row] = value
        store.present[row] = 2
        return
    bits = _bits_of(value)
    at = 8 * row
    for place in range(8):
        store.bits[at + place] = (bits >> (8 * place)) & 255
    store.present[row] = 1
    if row in store.odd:
        del store.odd[row]


def latent_scores(store: LatentStore) -> "dict[int, float]":
    """Every row's score that was put, as a dictionary in rising row order, each the value put; the store is emptied."""
    out: "dict[int, float]" = {}
    bits = store.bits
    present = store.present
    for row in range(len(present)):
        if present[row] == 1:
            at = 8 * row
            out[row] = _float_of(bits[at] | (bits[at + 1] << 8) | (bits[at + 2] << 16) | (bits[at + 3] << 24)
                                 | (bits[at + 4] << 32) | (bits[at + 5] << 40) | (bits[at + 6] << 48)
                                 | (bits[at + 7] << 56))
        elif present[row] == 2:
            out[row] = store.odd[row]
    store.bits = bytearray()
    store.present = bytearray()
    store.odd = {}
    return out


def _deal(cells: "list[str]", latent: "dict[int, float]") -> "list[str]":
    """The column's numeric cells dealt to its numeric rows in the order of the rows' latent scores (the cells themselves kept)."""
    rows = sorted(latent)
    values = [row for _value, row in sorted((typing.cast(float, _number(cells[row])), row) for row in rows)]
    takers = [row for _score, row in sorted((latent[row], row) for row in rows)]
    out = list(cells)
    for rank in range(len(rows)):
        out[takers[rank]] = cells[values[rank]]
    return out


def _with_an_atom(cells: "list[str]") -> bool:
    """Whether one value holds at least `ATOM_SHARE` of a number column's present cells (lane W5-PL); a fixed function of the cells."""
    counts: "dict[str, int]" = {}
    present = 0
    for cell in cells:
        if _absent(cell):
            continue
        value = _number(cell)
        text = f"{value}" if value is not None else _bare(cell)
        counts[text] = counts[text] + 1 if text in counts else 1
        present += 1
    if not present:
        return False
    most = 0
    for text in counts:
        most = max(most, counts[text])
    return most >= ATOM_SHARE * present


def _numbers_dealt(zone: "dict[str, object]", work: "dict[str, list[str]]", members: "list[list[int]]",
                   fixed: "list[str]", anchor_name: str, seed: int, held: "frozenset[str]" = frozenset()) -> None:
    entries = [entry for entry in typing.cast("list[dict[str, object]]", zone["numbers"])
               if isinstance(entry, dict) and _text(entry["column"]) in work and _text(entry["column"]) not in held
               and not _with_an_atom(work[_text(entry["column"])])]
    if not entries:
        return
    patient_columns = _patient_columns_of(zone)
    patient_cells = _patient_cells(patient_columns, work, members)
    rows_scores = mid_scores([float(len(rows_of)) for rows_of in members])
    size = len(entries)
    within = typing.cast("list[list[float]]", zone["within_corr"]) if "within_corr" in zone else []
    levels = typing.cast("list[list[float]]", zone["level_corr"]) if "level_corr" in zone else []
    # The patient draws: each column's level and slope, the levels correlated across columns.
    joint = [[0.0 for _b in range(2 * size)] for _a in range(2 * size)]
    for a in range(2 * size):
        joint[a][a] = 1.0
    listed = typing.cast("list[dict[str, object]]", zone["numbers"])
    places = [at for entry in entries for at in range(len(listed)) if listed[at] is entry]
    for a in range(size):
        corr = float(typing.cast(float, entries[a]["corr"]))
        joint[a][size + a] = corr
        joint[size + a][a] = corr
        for b in range(a + 1, size):
            value = levels[places[a]][places[b]] if len(levels) > max(places[a], places[b]) else 0.0
            joint[a][b] = value
            joint[b][a] = value
    joint_lower = cholesky(positive_correlation(joint), 1e-9)
    inner = [[1.0 if a == b else (within[places[a]][places[b]] if len(within) > max(places[a], places[b]) else 0.0)
              for b in range(size)] for a in range(size)]
    inner_lower = cholesky(positive_correlation(inner), 1e-9)
    read = [_read_entry(entry) for entry in entries]
    stream = stream_of(seed, 0x6E756D6265727300)
    # THE SCORES HELD AS BITS (lane W5-2M): every column's scores stand until the last is drawn, each column's in a
    # store of eight bytes a row, given back as the dictionary `_deal` reads one column at a time.
    latent = [latent_store(len(work[entry_read.column])) for entry_read in read]
    # ...AND THE COLUMNS DEALT HELD COMPACTLY WHILE THEY ARE DRAWN (lane W5-2M): the draw reads of a dealt column
    # only which rows hold a number, a byte a row here, so each is held as the twin holds its columns
    # (`twinstore.held_column`) until it is dealt, and read back then, each value once. The anchor, which the draw
    # reads, stays as it is.
    from synthtwin import twinstore

    present: "dict[str, bytearray]" = {}
    packed: "dict[str, twinstore.HeldColumn]" = {}
    for entry_read in read:
        name = entry_read.column
        if name not in present:
            present[name] = bytearray(0 if _number(cell) is None else 1 for cell in work[name])
            if name != anchor_name:
                packed[name] = twinstore.held_column(work[name])
                work[name] = []
    noises = [0.0 for _entry in entries]
    for p in range(len(members)):
        mixed = _times_lower(joint_lower, [next_normal(stream) for _k in range(2 * size)])
        level = [_shaped(read[a].level_shape, mixed[a]) * read[a].level_sd for a in range(size)]
        slope = [_shaped(read[a].slope_shape, mixed[size + a]) * read[a].slope_sd for a in range(size)]
        for place in range(len(members[p])):
            row = members[p][place]
            shocks = _times_lower(inner_lower, [next_normal(stream) for _k in range(size)])
            for a in range(size):
                lag = read[a].lag
                noises[a] = shocks[a] if place == 0 else lag * noises[a] + math.sqrt(max(0.0, 1.0 - lag * lag)) * shocks[a]
            for a in range(size):
                if not present[read[a].column][row]:
                    continue
                t = _entry_time(entries[a], work, members[p], place, anchor_name)
                line = design_row(patient_columns, patient_cells[p], t, rows_scores[p], True)
                total = 0.0
                for k in range(len(line)):
                    total = total + read[a].coefficients[k] * line[k]
                latent_put(latent[a], row, total + level[a] + slope[a] * t + read[a].noise_sd * noises[a])
    for a in range(size):
        name = read[a].column
        if name in packed:
            work[name] = once_a_value(twinstore.column_cells(packed[name]))
            del packed[name]
        work[name] = _deal(work[name], latent_scores(latent[a]))


@dataclasses.dataclass(frozen=True)
class _ReadEntry:
    """A number entry's parts the generator reads on every row, read once."""

    column: str
    coefficients: "tuple[float, ...]"
    level_shape: "list[float]"
    slope_shape: "list[float]"
    level_sd: float
    slope_sd: float
    noise_sd: float
    lag: float
    corr: float


def _read_entry(entry: "dict[str, object]") -> _ReadEntry:
    return _ReadEntry(
            _text(entry["column"]), _floats(entry["coefficients"]), list(_floats(entry["level_shape"])),
            list(_floats(entry["slope_shape"])), float(typing.cast(float, entry["level_sd"])),
            float(typing.cast(float, entry["slope_sd"])), float(typing.cast(float, entry["noise_sd"])),
            _bounded(float(typing.cast(float, entry["lag1"])), LAG_LEAST, LAG_MOST),
            _bounded(float(typing.cast(float, entry["corr"])), -CORR_MOST, CORR_MOST),
        )


def _times_lower(lower: "list[list[float]] | None", draws: "list[float]") -> "list[float]":
    if lower is None:
        return draws
    out: "list[float]" = []
    for row in range(len(lower)):
        total = 0.0
        for k in range(row + 1):
            total = total + lower[row][k] * draws[k]
        out += [total]
    return out


def _entry_time(entry: "dict[str, object]", work: "dict[str, list[str]]", rows_of: "list[int]", place: int, anchor_name: str) -> float:
    spread = float(typing.cast(float, entry["time_spread"]))
    if entry["axis"] == AXIS_YEARS and anchor_name in work:
        first_cell = work[anchor_name][rows_of[0]]
        here_cell = work[anchor_name][rows_of[place]]
        first = moment_of(first_cell) if not _absent(first_cell) else None
        here = moment_of(here_cell) if not _absent(here_cell) else None
        if first is None or here is None:
            return 0.0
        return (here.seconds - first.seconds) / SECONDS_A_YEAR / spread
    return float(place) / spread


def _binaries_dealt(zone: "dict[str, object]", work: "dict[str, list[str]]", members: "list[list[int]]",
                    anchor_name: str, seed: int, held: "frozenset[str]" = frozenset()) -> None:
    entries = [entry for entry in typing.cast("list[dict[str, object]]", zone["binaries"])
               if isinstance(entry, dict) and _text(entry["column"]) in work and _text(entry["column"]) not in held]
    if not entries:
        return
    patient_columns = _patient_columns_of(zone)
    patient_cells = _patient_cells(patient_columns, work, members)
    rows_scores = mid_scores([float(len(rows_of)) for rows_of in members])
    numbers = [entry for entry in typing.cast("list[dict[str, object]]", zone["numbers"]) if isinstance(entry, dict)]
    for entry in entries:
        column = _text(entry["column"])
        yes = _text(entry["yes"])
        rho = _bounded(float(typing.cast(float, entry["latent_corr"])), 0.0, CORR_MOST)
        stream = stream_of(seed, name_salt(column))
        latent: "dict[int, float]" = {}
        terms = typing.cast("list[str]", entry["terms"])
        row_terms = [term[4:] for term in terms if isinstance(term, str) and term[:4] == "row:"]
        number_of = {_text(one["column"]): one for one in numbers}
        coefficients = _floats(entry["coefficients"])
        for p in range(len(members)):
            shared = math.sqrt(rho) * next_normal(stream)
            for place in range(len(members[p])):
                row = members[p][place]
                own = math.sqrt(1.0 - rho) * next_normal(stream)
                if _absent(work[column][row]):
                    continue
                t = _entry_time(entry, work, members[p], place, anchor_name)
                line = design_row(patient_columns, patient_cells[p], t, rows_scores[p], False)
                for name in row_terms:
                    score = score_of(number_of[name], work[name][row]) if name in number_of and name in work else None
                    line += [0.0 if score is None else score]
                latent[row] = fitted_value(coefficients, line) + shared + own
        work[column] = _dealt_binary(work[column], latent, yes)


def _dealt_binary(cells: "list[str]", latent: "dict[int, float]", yes: str) -> "list[str]":
    """The column's yes cells dealt to the rows of the highest latent scores, its other cells to the rest (each cell kept)."""
    rows = sorted(latent)
    ones = [row for row in rows if _bare(cells[row]) == yes]
    others = [row for row in rows if _bare(cells[row]) != yes]
    takers = [row for _score, row in sorted((-latent[row], row) for row in rows)]
    out = list(cells)
    for rank in range(len(takers)):
        source = ones[rank] if rank < len(ones) else others[rank - len(ones)]
        out[takers[rank]] = cells[source]
    return out


# -- the record: the zone written and read where the inside record lives -------------------------------


def write_zone(zone: "dict[str, object]", stem: str, rows: int, columns: "list[str]",
               places: "typing.Any" = None, *, at: "typing.Any" = None,
               description: "dict[str, object] | None" = None) -> "typing.Any":
    """The zone written into the table's inside record (`inside.record_path`), the record's other zones of the same table kept.

    Returns the `inside.Written` record, or None where the inside zone's
    guard refuses the place (a temporary, synchronised, shared or version-
    controlled folder, or any folder but the private one): the description
    is then made exactly as before and nothing is written. A record of
    another table at that name (other columns or rows) is written anew.

    BOUND TO ITS DESCRIPTION (Codex's review of batch 4w, item 14), the way
    the generate step reads it: with `at`, the record's own place (the
    description's, `cli._inside_record_at`, in place of the stem's), and
    `description`, the digest and size of the description's bytes as the
    relations zone's record names them, the zone joins the record written
    beside that very description (the same columns, rows and description)
    and keeps its other zones; where no such record stands there (none, or
    one of another table or of another version of the description), nothing
    is written and None is returned.
    """
    from synthtwin import inside

    here = places if places is not None else inside.default_places()
    path = at if at is not None else inside.record_path(stem, here)
    if inside.place_refusal(path, here):
        return None
    table: "dict[str, object]" = {"rows": rows, "columns": [f"{name}" for name in columns]}
    if description is not None:
        table["description"] = description
    zones: "dict[str, object]" = {}
    try:
        if inside.carries_marker(path):
            existing = inside.load_record(path)
            kept = existing["zones"]
            if existing["table"] == table and isinstance(kept, dict):
                for key in sorted(kept):
                    if key != ZONE:
                        zones[f"{key}"] = kept[key]
            elif description is not None:
                return None
        elif description is not None:
            return None
    except (inside.InsideError, OSError, ValueError):
        if description is not None:
            return None
        zones = {}
    zones[ZONE] = zone
    record: "dict[str, object]" = {"format": inside.FORMAT, "version": inside.VERSION, "mode": inside.MODE,
                                   "table": table, "zones": zones}
    return inside.write_record(record, path, here)


def zone_of_record(stem: str, names: "list[str]", rows: int, places: "typing.Any" = None, *, at: "typing.Any" = None,
                   description: "dict[str, object] | None" = None) -> "dict[str, object] | None":
    """The trajectories zone of the table's inside record where one stands for a table of these columns and rows, else None.

    With `at` and `description` (Codex's review of batch 4w, item 14): the
    record at the description's own place, read only where it names these
    very bytes (the digest and size of the description handed), as the
    relations zone is read; a record of another table of the same columns
    and rows, or of another version of the description, gives None.
    """
    from synthtwin import inside

    here = places if places is not None else inside.default_places()
    try:
        path = at if at is not None else inside.record_path(stem, here)
        if not inside.carries_marker(path):
            return None
        record = inside.load_record(path)
    except (inside.InsideError, OSError, ValueError):
        return None
    table = record["table"]
    zones = record["zones"]
    if not isinstance(table, dict) or not isinstance(zones, dict):
        return None
    if "columns" not in table or "rows" not in table or table["columns"] != list(names) or table["rows"] != rows:
        return None
    if description is not None and ("description" not in table or table["description"] != description):
        return None
    return checked_zone(zones[ZONE] if ZONE in zones else None)


def _dates_labels(found: object) -> "list[str]":
    """Every label column a dates zone's clocks and gaps are drawn by: the texts it holds under a key `by`, once each, in order."""
    out: "list[str]" = []
    queue: "list[object]" = [found]
    at = 0
    while at < len(queue):
        item = queue[at]
        at += 1
        if isinstance(item, dict):
            for key in item:
                value = item[key]
                if key == "by" and isinstance(value, str):
                    if value and value not in out:
                        out += [value]
                else:
                    queue += [value]
        elif isinstance(item, list):
            queue += item
    return sorted(out)


def _dates_written_again(twin: "typing.Any", place_of: "dict[str, int]", first: Applied, dates: "dict[str, object]",
                         rewritten: "list[str]", person: str, seed: int) -> "dict[str, list[str]]":
    """The date columns the dates zone wrote, written by it again over the twin's rows as the timing step laid them out (each patient's rows together, the census met): every day of the month made up, each patient one timeline."""
    from synthtwin import inside_dates, twinstore

    def laid_out(name: str) -> "list[str]":
        if name in first.columns:
            return first.columns[name]
        cells = twinstore.column_cells(twin.held_columns[place_of[name]])
        return cells if first.order is None else [cells[row] for row in first.order]

    people = laid_out(person) if person in place_of else None
    given: "dict[str, list[str]]" = {}
    for label in _dates_labels(dates):
        if label in place_of:
            given[label] = laid_out(label)
    rows = len(people) if people is not None else int(twin.n_rows)
    # Written again with the first writing's cells (lane IN-2b): their dates, blanks and spellings, and their
    # months, are the description's twin's, so they stand over the rows as now laid out.
    months: "dict[str, list[str]]" = {}
    for name in rewritten:
        if name in place_of:
            months[name] = laid_out(name)
    made = inside_dates.write_dates(dates, rows, people, given, None, None,
                                    next_word(stream_of(seed, name_salt(ZONE))), months)
    del months
    out: "dict[str, list[str]]" = {}
    for name in rewritten:
        if name in made:
            out[name] = made[name]
    return out


def twin_with_zone(twin: "typing.Any", profile: "typing.Any", zone: "dict[str, object]", seed: int, *,
                   dates: "dict[str, object] | None" = None, written: "typing.Sequence[str]" = ()) -> "typing.Any":
    """The twin of the patient walk with a trajectories zone applied: the columns the zone writes held again, every other column moved with its rows, each changed column's counts taken again from its cells.

    THE ZONE TIMES NO DATE HERE (Codex's review of batch 4w, item 2): it
    sets each patient's rows and positions and deals the values (`applied`
    with `dates_kept`), and every date column moves with its rows, so no
    twin date is set from the real calendar's or the real first days'
    quantile points this zone holds. Where the dates zone wrote the twin's
    date columns (`written`, by the dates zone `dates`, as
    `generation.generate_inside` does), it writes them again over the
    patients the rows now form, so each patient's dates are one timeline in
    its rows' order with every day of the month made up; the values are
    then dealt on that time axis. Raises what the dates zone's writer
    raises (the caller then keeps the twin as it was).

    THE MEMORY (lane W5-2M): the columns the zone reads are read back
    from the twin's held columns once each, each different text held once
    (`once_a_value`), and handed to `applied` to be worked on in place
    (`taken`), so a column is held once, as pointers, while the zone writes
    it; each is held compactly again as soon as it is written, and a
    column the zone left as it was is told by its cells against the
    twin's own. At 2,000,000 rows the columns had been held three times
    over, each cell its own text object (about 6 GB for a table of 50
    columns before the scores, more than the 8 GB a process is given with
    them). The twin is the same, cell for cell.
    """
    from synthtwin import generation, twinstore

    if twin.held_columns is None:
        return twin
    names = list(twin.names)
    needed = [name for name in needed_columns(zone) if name in names]
    cells_of: "dict[str, list[str]]" = {}
    place_of: "dict[str, int]" = {}
    for at in range(len(names)):
        place_of[names[at]] = at
    for name in needed:
        cells_of[name] = once_a_value(twinstore.column_cells(twin.held_columns[place_of[name]]))
    rewritten = [name for name in written if isinstance(name, str) and name in place_of] if dates is not None else []
    if not rewritten:
        got = applied(zone, needed, cells_of, seed, dates_kept=True, taken=True)
        dated: "dict[str, list[str]]" = {}
    else:
        first = applied(zone, needed, cells_of, seed, dealing=False, dates_kept=True, taken=True)
        if not first.columns:
            return twin
        dated = _dates_written_again(twin, place_of, first, typing.cast("dict[str, object]", dates), rewritten,
                                     _text(zone["person"]), seed)
        middle: "dict[str, list[str]]" = {}
        for name in needed:
            middle[name] = dated[name] if name in dated else first.columns[name]
        first_order = first.order
        # ...the first step's lists are the dealing's now (`taken`): no other name holds them.
        first.columns = {}
        # THE ROW'S DATES AND WHAT THEY ARE DRAWN BY STAY TOGETHER (lane W5-PL): the dealing moves no date column
        # the dates zone wrote, nor any label its clocks and gaps are drawn by, from its row. Dealt with a key's
        # values, a charting table's device flag left the rows it is entered at once and charted on the minute
        # (rows entered at once 1.0 to 0.66, the five-minute difference 0.63 to 0.18 against the real 1.0 and
        # 0.63), and a universal clock left its local one (six hours apart on every row to 52 in 100).
        stay = list(rewritten) + [label for label in _dates_labels(dates) if label in place_of]
        got = Applied(applied(zone, needed, middle, seed, timing=False, kept=stay, taken=True).columns, first_order, [])
    if not got.columns:
        return twin
    every_hole = generation.every_hole_spelling(profile)
    blocks: "dict[str, typing.Any]" = {}
    for column in profile.columns:
        blocks[f"{column.name}"] = column
    held = list(twin.held_columns)
    outcomes = list(twin.outcomes)
    for at in range(len(names)):
        name = names[at]
        if name in got.columns:
            # ...each written column let go once it is held again.
            cells = got.columns[name]
            del got.columns[name]
            if name in dated:
                del dated[name]
            if got.order is None and cells == twinstore.column_cells(twin.held_columns[at]):
                continue
        elif name in dated:
            cells = dated[name]
        elif got.order is not None:
            before = twinstore.column_cells(held[at])
            cells = [before[row] for row in got.order]
        else:
            continue
        held[at] = twinstore.held_column(cells)
        if name in blocks and at < len(outcomes):
            counted = generation.recounted(
                cells, tuple(generation.holes_reserved(blocks[name], every_hole)),
                generation.declared_a_decimal_comma(blocks[name], profile),
            )
            outcomes[at] = dataclasses.replace(outcomes[at], n_present=counted[0], n_missing=counted[1],
                                               n_distinct=counted[2], n_distinct_folded=counted[3])
    return dataclasses.replace(twin, held_columns=tuple(held), outcomes=tuple(outcomes))
