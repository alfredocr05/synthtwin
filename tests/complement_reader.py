"""The readers and the seeded columns plan P4-D353 is measured on.

A READER holds one published numeric block and nothing else: never the
table. Five are here, each the arithmetic a review of the tail rule ran
against this producer, lifted so the suite and the ledger ask the same
questions the design measured:

* `named_directly` -- a published pair read by the producer's own
  lattice (`taxonomy._Lattice`) from the published facts alone: the rows,
  the whole sums of the tail's parts counted from its grid home, the cap
  the sign counts give, and the column's own "every value different". A
  cell is NAMED where no admissible multiset holds its distance a
  different number of times (ledger entry `K-S3-18`).
* `by_subtraction` -- the COMPLEMENT: one side's pair published and the
  other withheld; the interior read from the rungs (every rung pins the
  pair of ranks it reads up to its grid ambiguity, every unread segment
  enumerated); the withheld side's sums by subtraction from the column's
  EXACT mean and spread; its cells where ONE multiset fits across every
  interior configuration (ledger entry `K-S3-21`). It reads nothing of a
  block that withholds BOTH pairs, which is why `K-S3-19` counts the
  closures that stand and no values.
* `beside_a_list` -- the same subtraction where the other side LISTS its
  values, on a column whose values may repeat: the listed tail's sums
  from its own published pair (TL5), the interior from the rungs and
  order alone (ledger entry `K-S3-23`).
* `union` -- both pairs published and the interior rung-chained: every
  pair of tails fitting both pairs AND the column's exact skew and
  kurtosis (ledger entry `K-S3-17`, the limit the owner accepted).
* `whole_description` -- NO pair at all: every sorted column the rungs,
  the count of different values, the mode and its count, the sign
  counts and the exact mean and spread admit (ledger entry `K-S3-24`,
  the limit the owner accepted on 2026-09-26).

Each reader works on whole-number columns and gives up -- answers that it
read nothing -- where its enumeration exceeds its caps; a stronger reader
might not, which is why every count it gives is a floor on what comes
back and the entries that hold them say so.

Every column is built at test time from a fixed seed string; no
data-format file enters the repository (plan D13).
"""

from __future__ import annotations

import collections
import datetime
import fractions
import itertools
import math
import random

from synthtwin import parsing, taxonomy

# -- the seeded columns ----------------------------------------------------

KINDS = ("whole_uniform", "whole_normal", "two_place_normal", "two_place_lognormal", "ages")
SIZES = (150, 400, 1500)
DISTINCT_KINDS = (
    "whole_uniform_distinct",
    "two_place_lognormal_distinct",
    "two_place_normal_distinct",
)


def _one_ordinary(kind: str, draw: random.Random) -> str:
    if kind == "whole_uniform":
        return str(draw.randint(0, 99999))
    if kind == "whole_normal":
        return str(int(round(draw.gauss(500, 100))))
    if kind == "two_place_normal":
        return f"{draw.gauss(50, 10):.2f}"
    if kind == "two_place_lognormal":
        return f"{draw.lognormvariate(5, 1):.2f}"
    if kind == "ages":
        return str(max(18, min(99, int(draw.gauss(58, 17)))))
    raise KeyError(kind)


def ordinary(kind: str, rows: int) -> "list[str]":
    """One of the fifteen ordinary shapes (or, with `_distinct`, nine all-different ones)."""
    draw = random.Random(f"design-A/{kind}/{rows}")
    if not kind.endswith("_distinct"):
        return [_one_ordinary(kind, draw) for _ in range(rows)]
    base = kind[: -len("_distinct")]
    seen: "set[str]" = set()
    out: "list[str]" = []
    while len(out) < rows:
        one = _one_ordinary(base, draw)
        if one not in seen:
            seen.add(one)
            out += [one]
    return out


def _distinct_draw(draw: random.Random, rows: int, one) -> "list[str]":
    seen: "set[str]" = set()
    out: "list[str]" = []
    while len(out) < rows:
        text = one(draw)
        if text in seen:
            continue
        seen.add(text)
        out += [text]
    return out


def engineering_distinct(kind: str, rows: int, tag: str) -> "list[str]":
    """The engineering review's all-different draws (`skA` to `skF`)."""
    draw = random.Random(f"{tag}/{kind}-distinct/{rows}")
    if kind == "whole_uniform":
        return _distinct_draw(draw, rows, lambda r: str(r.randint(0, 99999)))
    if kind == "two_place_normal":
        return _distinct_draw(draw, rows, lambda r: f"{r.gauss(50, 10):.2f}")
    if kind == "two_place_lognormal":
        return _distinct_draw(draw, rows, lambda r: f"{r.lognormvariate(5, 1):.2f}")
    raise KeyError(kind)


def pareto(rows: int, seed: int) -> "list[str]":
    """All-different whole-number Pareto(2.5) readings, times a hundred."""
    draw = random.Random(f"skfail/pareto0/{rows}/{seed}")
    return _distinct_draw(draw, rows, lambda r: str(int(100 * r.paretovariate(2.5))))


def _geometry(n: int, floor: int) -> "tuple[int, int, int]":
    units = parsing.tail_units(floor)
    percent = parsing.tail_percent(n, units)
    low_rows = parsing.tail_rows(n, percent, "low")
    high_rows = parsing.tail_rows(n, 100 - percent, "high")
    return percent, low_rows, high_rows


def rung_chained(n: int, floor: int, seed: int) -> "tuple[list[int], list[str]]":
    """A gappy low tail, an interior the rungs chain, a consecutive high run (review attack A1)."""
    _percent, low_rows, high_rows = _geometry(n, floor)
    low_last = low_rows - 1
    high_first = n - high_rows
    draw = random.Random(f"skA/a1/{n}/{floor}/{seed}")
    middle = [500]
    for _ in range(high_first - low_last):
        middle += [middle[-1] + draw.randint(1, 20)]
    low = sorted(draw.sample(range(1, 500), low_last))
    top = middle[-1]
    high = [top + step for step in range(1, n - high_first)]
    values = low + middle + high
    cells = [str(value) for value in values]
    draw.shuffle(cells)
    return values, cells


def one_jump(n: int, floor: int, seed: int, jump: int) -> "tuple[list[int], list[str]]":
    """A gappy low tail, a consecutive interior with one jump, a consecutive high run (attack A2)."""
    _percent, low_rows, high_rows = _geometry(n, floor)
    low_last = low_rows - 1
    high_first = n - high_rows
    draw = random.Random(f"skA/a2/{n}/{floor}/{seed}/{jump}")
    count = high_first - low_last + 1
    jump_at = draw.randint(1, count - 1)
    middle = [5000]
    for place in range(1, count):
        middle += [middle[-1] + (jump if place == jump_at else 1)]
    low = sorted(draw.sample(range(1, 5000), low_last))
    top = middle[-1]
    high = [top + step for step in range(1, n - high_first)]
    values = low + middle + high
    cells = [str(value) for value in values]
    draw.shuffle(cells)
    return values, cells


def both_dense(width: int, floor: int, seed: int, n: int = 102) -> "tuple[list[int], list[str]]":
    """Both tails dense and gappy, the interior rung-chained (the skew and kurtosis shape)."""
    _percent, low_rows, high_rows = _geometry(n, floor)
    low_last = low_rows - 1
    high_first = n - high_rows
    draw = random.Random(f"v2/both/{width}/{floor}/{seed}/{n}")
    middle = [width]
    for _ in range(high_first - low_last):
        middle += [middle[-1] + draw.randint(1, 20)]
    low = sorted(draw.sample(range(1, width), low_last))
    top = middle[-1]
    high = sorted(top + value for value in draw.sample(range(1, width), n - high_first - 1))
    values = low + middle + high
    cells = [str(value) for value in values]
    draw.shuffle(cells)
    return values, cells


def dense_low(width: int, floor: int, seed: int, n: int = 102) -> "tuple[list[int], list[str]]":
    """A dense low tail, a rung-chained interior and a consecutive high run (attack A3)."""
    _percent, low_rows, high_rows = _geometry(n, floor)
    low_last = low_rows - 1
    high_first = n - high_rows
    draw = random.Random(f"skA/a3/{width}/{floor}/{seed}")
    middle = [width]
    for _ in range(high_first - low_last):
        middle += [middle[-1] + draw.randint(1, 20)]
    low = sorted(draw.sample(range(1, width), low_last))
    top = middle[-1]
    high = [top + step for step in range(1, n - high_first)]
    values = low + middle + high
    cells = [str(value) for value in values]
    draw.shuffle(cells)
    return values, cells


def attack_columns(floor: int) -> "list[tuple[str, list[int], list[str]]]":
    """The review's rung-chained and one-jump columns at a floor of 11 or 36, seed for seed."""
    found: "list[tuple[str, list[int], list[str]]]" = []
    if floor == 11:
        chained = range(2, 7)
        jumps = ((400, 6, 100),)
    else:
        chained = range(1, 7)
        jumps = ((400, 2, 100), (400, 3, 300), (400, 4, 65), (1500, 5, 100), (150, 7, 100))
    for seed in chained:
        values, cells = rung_chained(102, floor, seed)
        found += [(f"a1_n102_s{seed}", values, cells)]
    for n, seed, jump in jumps:
        values, cells = one_jump(n, floor, seed, jump)
        found += [(f"a2_n{n}_s{seed}_J{jump}", values, cells)]
    return found


def attack_battery(floor: int) -> "list[tuple[str, list[int], list[str]]]":
    """`attack_columns` and the columns whose two pairs both publish or neither does.

    At a floor of 11 the five both-dense columns of 102 rows (the skew and
    kurtosis shape); at 36 one dense-low and one both-dense column.
    """
    found = attack_columns(floor)
    if floor == 11:
        for seed in range(1, 6):
            values, cells = both_dense(40, floor, seed)
            found += [(f"both_W40_s{seed}", values, cells)]
    else:
        values, cells = dense_low(53, floor, 1)
        found += [("a3_W53_s1", values, cells)]
        values, cells = both_dense(53, floor, 1)
        found += [("both_W53_s1", values, cells)]
    return found


def far_low(far: int, rows: int) -> "list[str]":
    """One far negative value beside a consecutive run from 500."""
    return [str(-far)] + [str(500 + index) for index in range(rows - 1)]


LISTED_SCALES = (
    "likert_far_150",
    "likert_farlow_150",
    "likert_far_400",
    "ages_far_400",
    "pain_far_high_400",
    "scale_far_low_400",
)


def listed_scale(name: str) -> "list[str]":
    """A scale of few values beside ONE far cell: the shape whose near tail LISTS its values.

    Seeded as the review of plan P4-D353 drew them, so its counts can be
    re-derived here.
    """
    draw = random.Random(f"skeptic-A1/list_{name}")
    if name in ("likert_far_150", "likert_far_400"):
        rows, far = (149, "19") if name == "likert_far_150" else (399, "23")
        return [str(draw.choice([1, 1, 2, 2, 3, 3, 3, 4, 4, 5])) for _ in range(rows)] + [far]
    if name == "likert_farlow_150":
        return [str(draw.choice([1, 2, 2, 3, 3, 3, 4, 4, 5, 5])) for _ in range(149)] + ["-9"]
    if name == "ages_far_400":
        return [str(draw.choice(range(18, 30))) for _ in range(399)] + ["97"]
    cells: "list[str]" = []
    for _ in range(399):
        u = draw.random()
        if name == "pain_far_high_400":
            cells += [str(0 if u < 0.2 else 1 if u < 0.35 else min(10, 2 + int(draw.expovariate(0.5))))]
        else:
            cells += [str(10 if u < 0.2 else 9 if u < 0.35 else max(0, 8 - int(draw.expovariate(0.5))))]
    return cells + (["37"] if name == "pain_far_high_400" else ["-25"])


def shape(kind: str, n: int, seed: int) -> "list[str]":
    """The tail review's own seeded shapes, by the names it measured them under."""
    draw = random.Random(f"skA3/{kind}/{n}/{seed}")
    if kind == "par20d":
        return _distinct_draw(draw, n, lambda r: str(int(100 * r.paretovariate(2.0))))
    if kind == "exp3d":
        return _distinct_draw(draw, n, lambda r: f"{r.expovariate(0.01):.3f}")
    if kind == "bigint_d":
        return [str(value) for value in draw.sample(range(1, 10 ** 6), n)]
    if kind.startswith("cfh"):
        far = int(kind[3:])
        return [str(1000 + index) for index in range(n - 1)] + [str(far)]
    if kind.startswith("pad"):
        far = int(kind[3:])
        return [f"{value:05}" for value in range(1, n)] + [f"{far:05}"]
    raise KeyError(kind)


def small_distinct(n: int) -> "list[str]":
    """All-different two-place lognormal readings, few enough to publish moments only at 36."""
    draw = random.Random(f"skA3/small/{n}")
    return _distinct_draw(draw, n, lambda r: f"{r.lognormvariate(5, 1.2):.2f}")


def consecutive_dates(count: int, start: str = "2020-01-01") -> "list[str]":
    first = datetime.date.fromisoformat(start)
    return [(first + datetime.timedelta(days=step)).isoformat() for step in range(count)]


# -- what a reader holds -----------------------------------------------------


def state(tail: "dict") -> str:
    """`list`, `pair` or `withheld`: what one published tail says."""
    if tail.get("values"):
        return "list"
    return "withheld" if tail.get("mean_distance") is None else "pair"


def rung_of(block: "dict", percent: int) -> float:
    where, name = taxonomy._rung_name(percent)
    return block[where][name]


def whole_sum(mean: float, n: int, spread: int = 4) -> "list[int]":
    """Every whole sum whose producer mean is the published one."""
    guess = round(fractions.Fraction(mean) * n)
    return [t for t in range(guess - spread, guess + spread + 1) if taxonomy._rounded_ratio(t, n) == mean]


def whole_squares(std: float, n: int, first: int, spread: int = 64) -> "list[int]":
    """Every whole sum of squares whose producer spread is the published one."""
    variance = fractions.Fraction(std) ** 2
    guess = round((variance * n * (n - 1) + first * first) / n)
    found: "list[int]" = []
    for second in range(guess - spread, guess + spread + 1):
        room = n * second - first * first
        if room > 0 and taxonomy._rounded_root(room, n * (n - 1)) == std:
            found += [second]
    return found


def _skew_of(n: int, first: int, second: int, third: int) -> float:
    spread = n * second - first * first
    shape = n * n * third - 3 * n * first * second + 2 * first ** 3
    size = taxonomy._rounded_root(shape * shape, spread * spread * spread)
    return -size if shape < 0 else size


def whole_cubes(skew: float, n: int, first: int, second: int) -> "tuple[int, int] | None":
    """The interval of whole sums of cubes whose producer skew is the published one."""
    low, high = -(1 << 200), 1 << 200
    a, b = low, high
    while b - a > 1:
        middle = (a + b) // 2
        if _skew_of(n, first, second, middle) >= skew:
            b = middle
        else:
            a = middle
    least = b
    a, b = low, high
    while b - a > 1:
        middle = (a + b) // 2
        if _skew_of(n, first, second, middle) > skew:
            b = middle
        else:
            a = middle
    most = a
    return None if least > most else (least, most)


def _kurtosis_of(n: int, first: int, second: int, third: int, fourth: int) -> float:
    spread = n * second - first * first
    weight = n ** 3 * fourth - 4 * n * n * first * third + 6 * n * first * first * second - 3 * first ** 4
    return taxonomy._rounded_ratio(weight, spread * spread)


def whole_fourths(kurtosis: float, n: int, first: int, second: int, third: int) -> "tuple[int, int] | None":
    """The interval of whole sums of fourth powers whose producer kurtosis is the published one."""
    low, high = -(1 << 260), 1 << 260
    a, b = low, high
    while b - a > 1:
        middle = (a + b) // 2
        if _kurtosis_of(n, first, second, third, middle) >= kurtosis:
            b = middle
        else:
            a = middle
    least = b
    a, b = low, high
    while b - a > 1:
        middle = (a + b) // 2
        if _kurtosis_of(n, first, second, third, middle) > kurtosis:
            b = middle
        else:
            a = middle
    most = a
    return None if least > most else (least, most)


def rung_equations(block: "dict", n: int, low_percent: int, high_percent: int) -> "list[tuple[int, int, int, int]]":
    """[(lower, rest, N, percent)] with (100 - rest) * x[lower] + rest * x[lower + 1] == N."""
    found: "list[tuple[int, int, int, int]]" = []
    for percent in range(low_percent, high_percent + 1):
        value = rung_of(block, percent)
        if value is None:
            continue
        lower, rest = divmod((n - 1) * percent, 100)
        exact = fractions.Fraction(value) * 100
        whole = round(exact)
        assert abs(exact - whole) < fractions.Fraction(1, 10 ** 6), (percent, value)
        found += [(lower, rest, whole, percent)]
    return found


def solve_chain(equations: "list[tuple[int, int, int, int]]", anchors: range) -> "list[dict[int, int]]":
    """Every strictly increasing whole assignment of the ranks the rungs read."""
    equations = sorted(equations)
    first = equations[0][0]
    found: "list[dict[int, int]]" = []
    for anchor in anchors:
        values = {first: anchor}
        good = True
        for lower, rest, whole, _percent in equations:
            if rest == 0:
                if (lower in values and values[lower] * 100 != whole) or whole % 100:
                    good = False
                    break
                values[lower] = whole // 100
                continue
            if lower not in values:
                good = False
                break
            left = whole - (100 - rest) * values[lower]
            if left % rest:
                good = False
                break
            upper = left // rest
            if upper <= values[lower] or (lower + 1 in values and values[lower + 1] != upper):
                good = False
                break
            values[lower + 1] = upper
        if good:
            ranks = sorted(values)
            good = all(values[a] < values[b] for a, b in zip(ranks, ranks[1:]))
        if good:
            found += [values]
    return found


def tail_sums(tail: "dict", boundary: float, side: str) -> "list[tuple[int, int]]":
    """Every (sum, sum of squares) of a whole-number tail whose published pair is this one."""
    rows = tail["rows"]
    mean = tail["mean_distance"]
    root = tail["rms_distance"]
    b = fractions.Fraction(boundary)
    sign = -1 if side == "low" else 1
    guess = round(rows * b + sign * fractions.Fraction(mean) * rows)
    found: "list[tuple[int, int]]" = []
    for first in range(guess - 3, guess + 4):
        distance = sign * (first - rows * b)
        if distance < 0:
            continue
        ratio = distance / rows
        if taxonomy._rounded_ratio(ratio.numerator, ratio.denominator) != mean:
            continue
        squared = fractions.Fraction(root) ** 2 * rows
        second_guess = round(squared + 2 * b * first - rows * b * b)
        for second in range(second_guess - 200, second_guess + 201):
            room = second - 2 * b * first + rows * b * b
            if room < 0:
                continue
            share = room / rows
            if taxonomy._rounded_root(share.numerator, share.denominator) == root:
                found += [(first, second)]
    return found


def different_multisets(
    count: int, total: int, squares: int, lo: int, hi: int, cap: int = 4, budget: int = 5_000_000
) -> "tuple[list[list[int]], bool]":
    """Up to `cap` sets of `count` DIFFERENT whole numbers in [lo, hi] with this sum and sum of squares.

    Returns (sets, finished): finished False means the budget ran out.
    """
    found: "list[list[int]]" = []
    steps = [0]

    def walk(k: int, left: int, left_squares: int, top: int, taken: "list[int]") -> None:
        nonlocal found
        steps[0] += 1
        if steps[0] > budget or len(found) >= cap:
            return
        if k == 0:
            if left == 0 and left_squares == 0:
                found += [list(taken)]
            return
        if top < lo + k - 1:
            return
        if left < k * lo + k * (k - 1) // 2 or left > k * top - k * (k - 1) // 2:
            return
        even, spare = divmod(left, k)
        if left_squares < (k - spare) * even * even + spare * (even + 1) * (even + 1):
            return
        room = left_squares - sum((lo + i) ** 2 for i in range(k - 1))
        if room < 0:
            return
        biggest = min(top, math.isqrt(room))
        smallest = -(-left // k)
        for value in range(biggest, smallest - 1, -1):
            walk(k - 1, left - value, left_squares - value * value, value - 1, taken + [value])
            if steps[0] > budget or len(found) >= cap:
                return

    walk(count, total, squares, hi, [])
    return found, steps[0] <= budget


# -- the three readers -------------------------------------------------------

GAP_MOST = 5000
SOLUTION_CAP = 200
SEGMENT_CAP = 20000
CONFIG_CAP = 200000


def _rung_assignments(equations, cap: int) -> "list[dict[int, int]]":
    """Every assignment of the ranks the rungs read, each rung's pair located up to its grid."""
    choices: "list[tuple[int, int, list[tuple[int, int | None]]]]" = []
    for lower, rest, whole, _percent in equations:
        if rest == 0:
            choices += [(lower, rest, [(whole // 100, None)] if whole % 100 == 0 else [])]
            continue
        here: "list[tuple[int, int | None]]" = []
        for gap in range(1, GAP_MOST + 1):
            bottom = whole - rest * gap
            if bottom % 100 == 0:
                here += [(bottom // 100, bottom // 100 + gap)]
        choices += [(lower, rest, here)]
    found: "list[dict[int, int]]" = []

    def fits(assign: "dict[int, int]") -> bool:
        ranks = sorted(assign)
        return all(assign[b] - assign[a] >= b - a for a, b in zip(ranks, ranks[1:]))

    def walk(index: int, assign: "dict[int, int]") -> None:
        nonlocal found
        if len(found) > cap:
            return
        if index == len(choices):
            found += [dict(assign)]
            return
        lower, rest, here = choices[index]
        for pair in here:
            trial = dict(assign)
            if rest == 0:
                if lower in trial and trial[lower] != pair[0]:
                    continue
                trial[lower] = pair[0]
            else:
                clash = False
                for rank, value in ((lower, pair[0]), (lower + 1, pair[1])):
                    if rank in trial and trial[rank] != value:
                        clash = True
                    trial[rank] = value
                if clash:
                    continue
            if fits(trial):
                walk(index + 1, trial)

    walk(0, {})
    return found


def by_subtraction(block: "dict", values: "list[int]") -> "dict":
    """The COMPLEMENT: what one published pair and the exact moments give back of the other tail.

    Returns `sides` (each tail's state), `values_rebuilt` (the withheld
    tail's cells named exactly, 0 where the reader names nothing), and
    `complement`: `n/a` where the block does not publish exactly one pair
    beside one withheld tail, `open` where the withheld tail comes back,
    `closed-by-ambiguity` where more than one fits, or why the reader gave
    up. `values` are the column's own sorted values, used only to say
    whether what came back IS the tail.
    """
    tails = block["tails"]
    sides = {side: state(tails[side]) for side in ("low", "high")}
    out: "dict" = {"sides": sides, "values_rebuilt": 0}
    if sorted(sides.values()) != ["pair", "withheld"]:
        out["complement"] = "n/a"
        return out
    if block.get("integer_valued") is not True or block.get("n_distinct_values") != block.get("n_used_in_statistics"):
        out["complement"] = "not a whole-number all-different column"
        return out
    n = block["n_used_in_statistics"]
    low_percent, high_percent = tails["low"]["percent"], tails["high"]["percent"]
    low_rows = parsing.tail_rows(n, low_percent, "low")
    high_rows = parsing.tail_rows(n, high_percent, "high")
    low_last = low_rows - 1
    high_first = n - high_rows
    shown = "low" if sides["low"] == "pair" else "high"
    hidden = "high" if shown == "low" else "low"
    first = whole_sum(block["mean"], n)[0]
    second = whole_squares(block["std"], n, first)[0]
    sums = tail_sums(tails[shown], rung_of(block, tails[shown]["percent"]), shown)
    if len(sums) != 1:
        out["complement"] = f"the published pair gives {len(sums)} sums"
        return out
    shown_first, shown_second = sums[0]
    assignments = _rung_assignments(rung_equations(block, n, low_percent, high_percent), SOLUTION_CAP)
    if len(assignments) > SOLUTION_CAP:
        out["complement"] = "interior-too-free (rung assignments)"
        return out
    found: "set[tuple[int, ...]]" = set()
    for assign in assignments:
        ranks = sorted(assign)
        segments = [(a, b) for a, b in zip(ranks, ranks[1:]) if b - a > 1]
        base_first = sum(assign[r] for r in ranks if low_last < r < high_first)
        base_second = sum(assign[r] ** 2 for r in ranks if low_last < r < high_first)
        options: "list[list[tuple[int, int]]] | None" = []
        for a, b in segments:
            if not (low_last <= a and b <= high_first):
                continue
            k = b - a - 1
            lo_value, hi_value = assign[a] + 1, assign[b] - 1
            width = hi_value - lo_value + 1
            if width < k:
                options = None
                break
            span = range(lo_value, hi_value + 1)
            if width == k:
                options += [[(sum(span), sum(v * v for v in span))]]
                continue
            if math.comb(width, k) > SEGMENT_CAP:
                out["complement"] = "interior-too-free (an unread segment)"
                return out
            here: "dict[tuple[int, int], bool]" = {}
            for chosen in itertools.combinations(span, k):
                here[(sum(chosen), sum(v * v for v in chosen))] = True
            options += [list(here)]
        if options is None:
            continue
        total = 1
        for option in options:
            total *= len(option)
        if total > CONFIG_CAP:
            out["complement"] = f"interior-too-free ({total} configurations)"
            return out
        fixed_rank = high_first if hidden == "high" else low_last
        rows = high_rows if hidden == "high" else low_rows
        fixed = assign.get(fixed_rank)
        for picks in itertools.product(*options):
            hidden_first = first - shown_first - base_first - sum(q[0] for q in picks)
            hidden_second = second - shown_second - base_second - sum(q[1] for q in picks)
            need = rows
            if fixed is not None:
                hidden_first -= fixed
                hidden_second -= fixed * fixed
                need = rows - 1
            if hidden == "high":
                start = (fixed if fixed is not None else assign[max(r for r in ranks if r < high_first)]) + 1
                sets, _finished = different_multisets(need, hidden_first, hidden_second, start, 10 ** 7, cap=2, budget=200000)
            else:
                end = (fixed if fixed is not None else assign[min(r for r in ranks if r > low_last)]) - 1
                least = 1 if block.get("n_zero", 0) == 0 and block.get("n_negative", 0) == 0 else -10 ** 7
                sets, _finished = different_multisets(need, hidden_first, hidden_second, max(least, 0), end, cap=2, budget=200000)
            for one in sets:
                found.add(tuple(sorted(one + ([fixed] if fixed is not None else []))))
                if len(found) > 2:
                    break
            if len(found) > 2:
                break
    out["withheld_tails_consistent"] = len(found)
    truth = values[:low_rows] if hidden == "low" else values[high_first:]
    if len(found) == 1 and list(next(iter(found))) == sorted(truth):
        out["values_rebuilt"] = len(truth)
    out["complement"] = "open" if out["values_rebuilt"] else "closed-by-ambiguity"
    return out


# -- the complement beside a LISTED tail --------------------------------------

_UNBOUNDED = 10 ** 15
RANK_WIDTH_CAP = 400
OUTCOME_CAP = 50000


def _rung_pair_options(
    lower: int, rest: int, whole: int, least: "list[int]", most: "list[int]", step: int
) -> "list[tuple[int, int]] | None":
    """The (x[lower], x[lower + 1]) one rung admits inside the ranks' bounds, or None while unbounded."""
    found: "list[tuple[int, int]]" = []
    top = min(most[lower], whole // 100)
    if top - least[lower] <= RANK_WIDTH_CAP:
        for a in range(least[lower], top + 1):
            b, left = divmod(whole - (100 - rest) * a, rest)
            if not left and least[lower + 1] <= b <= most[lower + 1] and b >= a + step:
                found += [(a, b)]
        return found
    bottom = max(least[lower + 1], -(-whole // 100))
    if most[lower + 1] - bottom <= RANK_WIDTH_CAP:
        for b in range(bottom, most[lower + 1] + 1):
            a, left = divmod(whole - rest * b, 100 - rest)
            if not left and least[lower] <= a <= most[lower] and b >= a + step:
                found += [(a, b)]
        return found
    return None


def _rank_bounds(
    n: int, equations: "list[tuple[int, int, int, int]]", fixed: "dict[int, tuple[int, int]]", step: int
) -> "tuple[list[int], list[int]] | str":
    """Each rank's least and most value from the rungs, the fixed ranks and order alone, or why not."""
    least = [-_UNBOUNDED] * n
    most = [_UNBOUNDED] * n
    for rank in fixed:
        least[rank] = max(least[rank], fixed[rank][0])
        most[rank] = min(most[rank], fixed[rank][1])
    for lower, rest, whole, _percent in equations:
        if rest == 0:
            if whole % 100:
                return "a rung on one rank reads between two whole numbers"
            least[lower] = max(least[lower], whole // 100)
            most[lower] = min(most[lower], whole // 100)
        else:
            most[lower] = min(most[lower], whole // 100)
            least[lower + 1] = max(least[lower + 1], -(-whole // 100))
    for _round in range(64):
        before = (list(least), list(most))
        for rank in range(1, n):
            least[rank] = max(least[rank], least[rank - 1] + step)
        for rank in range(n - 2, -1, -1):
            most[rank] = min(most[rank], most[rank + 1] - step)
        for lower, rest, whole, _percent in equations:
            if rest == 0:
                continue
            options = _rung_pair_options(lower, rest, whole, least, most, step)
            if options is None:
                continue
            if not options:
                return "no pair of whole numbers fits a rung"
            least[lower] = min(a for a, _b in options)
            most[lower] = max(a for a, _b in options)
            least[lower + 1] = min(b for _a, b in options)
            most[lower + 1] = max(b for _a, b in options)
        if any(least[rank] > most[rank] for rank in range(n)):
            return "the rungs contradict each other"
        if (least, most) == before:
            return least, most
    return "the bounds do not settle"


def _most_squares(k: int, total: int, bottom: int, top: int) -> int:
    """The largest sum of squares `k` whole numbers in [bottom, top] summing to `total` can have.

    A convex sum is largest at a vertex: every number at an end but one.
    """
    if top <= bottom:
        return k * bottom * bottom
    full, spare = divmod(total - k * bottom, top - bottom)
    if full >= k:
        return k * top * top
    return full * top * top + (bottom + spare) ** 2 + (k - full - 1) * bottom * bottom


def _tail_multisets(
    count: int, total: int, squares: int, least: int, most: int, step: int, cap: int = 3, budget: int = 2_000_000
) -> "tuple[list[list[int]], bool]":
    """Up to `cap` multisets of `count` whole numbers in [least, most], `step` apart at least, with this sum and sum of squares."""
    found: "list[list[int]]" = []
    steps = [0]

    def walk(k: int, left: int, left_squares: int, top: int, taken: "list[int]") -> None:
        nonlocal found
        steps[0] += 1
        if steps[0] > budget or len(found) >= cap:
            return
        if k == 0:
            if left == 0 and left_squares == 0:
                found += [sorted(taken)]
            return
        if left_squares < 0 or k * left_squares < left * left:
            return
        reach = math.isqrt(left_squares)
        bottom = max(least, -reach)
        top = min(top, reach)
        if left < k * bottom + step * k * (k - 1) // 2 or left > k * top - step * k * (k - 1) // 2:
            return
        if left_squares > _most_squares(k, left, bottom, top):
            return
        for value in range(top, -(-left // k) - 1, -1):
            walk(k - 1, left - value, left_squares - value * value, value - step, taken + [value])
            if steps[0] > budget or len(found) >= cap:
                return

    walk(count, total, squares, most, [])
    return found, steps[0] <= budget


def beside_a_list(block: "dict", values: "list[int]") -> "dict":
    """The COMPLEMENT beside a LISTED tail: what the exact moments give back of the withheld side.

    A listed tail publishes both distances (TL5), so its sums follow from
    its own pair; the interior ranks are bounded by every published rung
    (a rung's pair of whole numbers enumerated inside its neighbours'
    bounds), the published ends and order alone -- the column's values
    may repeat, and repeat they do on the scales this is asked of; the
    withheld side's sums follow by subtraction from the column's EXACT
    mean and spread, and its cells are named where ONE multiset fits
    across every interior the rungs admit. Returns `values_rebuilt`,
    `withheld_tails_consistent` and `complement`: `n/a` where the block
    does not list one side beside one withheld side, `open` where the
    withheld tail comes back, `closed-by-ambiguity` where more than one
    fits, or why the reader gave up. `values` are the column's own sorted
    values, used only to say whether what came back IS the tail.
    """
    tails = block["tails"]
    sides = {side: state(tails[side]) for side in ("low", "high")}
    out: "dict" = {"sides": sides, "values_rebuilt": 0}
    if sorted(sides.values()) != ["list", "withheld"]:
        out["complement"] = "n/a"
        return out
    if block.get("integer_valued") is not True:
        out["complement"] = "not a whole-number column"
        return out
    n = block["n_used_in_statistics"]
    step = 1 if block.get("n_distinct_values") == n else 0
    shown = "low" if sides["low"] == "list" else "high"
    hidden = "high" if shown == "low" else "low"
    low_rows, high_rows = tails["low"]["rows"], tails["high"]["rows"]
    inside_first, inside_last = low_rows, n - high_rows - 1
    equations = rung_equations(block, n, tails["low"]["percent"], tails["high"]["percent"])
    totals = whole_sum(block["mean"], n)
    if len(totals) != 1:
        out["complement"] = f"the mean gives {len(totals)} sums"
        return out
    squares = whole_squares(block["std"], n, totals[0])
    if len(squares) != 1:
        out["complement"] = f"the spread gives {len(squares)} sums of squares"
        return out
    # The producer measures a tail's distances from its published rung.
    listed = tail_sums(tails[shown], rung_of(block, tails[shown]["percent"]), shown)
    if len(listed) != 1:
        out["complement"] = f"the listed tail's pair gives {len(listed)} sums"
        return out
    listed_values = [int(value) for value in tails[shown]["values"]]
    fixed: "dict[int, tuple[int, int]]" = {}
    listed_ranks = range(0, low_rows) if shown == "low" else range(n - high_rows, n)
    for rank in listed_ranks:
        fixed[rank] = (min(listed_values), max(listed_values))
    for end, rank in (("min", 0), ("max", n - 1)):
        if block["percentiles"].get(end) is not None:
            fixed[rank] = (int(block["percentiles"][end]), int(block["percentiles"][end]))
    bounds = _rank_bounds(n, equations, fixed, step)
    if isinstance(bounds, str):
        out["complement"] = bounds
        return out
    least, most = bounds
    # THE RANKS WALKED: the interior, the listed side's innermost rank (a
    # boundary rung may read it beside the first interior rank; its value
    # is one of the list and its sum is the pair's), and the withheld
    # side's innermost rank where the rungs bound it.
    first = inside_first - 1 if shown == "low" else inside_first
    last = inside_last + 1 if shown == "high" else inside_last
    edge = inside_last + 1 if hidden == "high" else inside_first - 1
    if most[edge] - least[edge] <= RANK_WIDTH_CAP:
        first, last = min(first, edge), max(last, edge)
    for rank in range(first, last + 1):
        if most[rank] - least[rank] > RANK_WIDTH_CAP:
            out["complement"] = "interior-too-free (an unbounded rank)"
            return out
    ties = {lower + 1: (lower, rest, whole) for lower, rest, whole, _percent in equations if rest}
    # Walked from the last rank down: for each value of a rank, every
    # (sum, sum of squares, value of the outermost walked rank) of the ranks
    # above it, the interior's alone summed.
    after: "dict[int, set[tuple[int, int, int]]]" = {}
    for rank in range(last, first - 1, -1):
        here: "dict[int, set[tuple[int, int, int]]]" = {}
        counted = inside_first <= rank <= inside_last
        for value in range(least[rank], most[rank] + 1):
            if rank in listed_ranks and value not in listed_values:
                continue
            add = (value, value * value) if counted else (0, 0)
            found: "set[tuple[int, int, int]]" = set()
            if rank == last:
                found.add((add[0], add[1], value))
            for above, outcomes in after.items():
                if above < value + step:
                    continue
                if rank + 1 in ties:
                    lower, rest, whole = ties[rank + 1]
                    if (100 - rest) * value + rest * above != whole:
                        continue
                for total, square, outer in outcomes:
                    found.add((total + add[0], square + add[1], outer))
            if found:
                here[value] = found
            if len(found) > OUTCOME_CAP:
                out["complement"] = "interior-too-free (configurations)"
                return out
        after = here
    rows = high_rows if hidden == "high" else low_rows
    tails_found: "set[tuple[int, ...]]" = set()
    finished = True
    for start, outcomes in after.items():
        for total, square, outer in outcomes:
            near = outer if hidden == "high" else start
            left = totals[0] - listed[0][0] - total
            left_squares = squares[0] - listed[0][1] - square
            need, known = rows, []
            if edge in (first, last):
                need, known = rows - 1, [near]
                left, left_squares = left - near, left_squares - near * near
            if hidden == "high":
                end = most[n - 1] if most[n - 1] < _UNBOUNDED else _UNBOUNDED
                sets, done = _tail_multisets(need, left, left_squares, near + step, end, step)
            else:
                end = -least[0] if least[0] > -_UNBOUNDED else _UNBOUNDED
                mirrored, done = _tail_multisets(need, -left, left_squares, -(near - step), end, step)
                sets = [sorted(-one for one in each) for each in mirrored]
            finished = finished and done
            for one in sets:
                tails_found.add(tuple(sorted(one + known)))
            if len(tails_found) > 2:
                break
        if len(tails_found) > 2:
            break
    out["withheld_tails_consistent"] = len(tails_found)
    truth = values[:low_rows] if hidden == "low" else values[n - high_rows :]
    if len(tails_found) == 1 and list(next(iter(tails_found))) == sorted(truth):
        out["values_rebuilt"] = len(truth)
    if out["values_rebuilt"]:
        out["complement"] = "open"
    elif not tails_found and not finished:
        out["complement"] = "a tail search ran out of budget"
    else:
        out["complement"] = "closed-by-ambiguity"
    return out


def union(block: "dict", values: "list[int]", budget: int = 50_000_000) -> "dict":
    """Both pairs published and the interior rung-chained: what the exact skew and kurtosis add.

    Every pair of tails fitting both published pairs, the column's exact
    mean and spread AND its exact third and fourth moments is enumerated.
    Returns `values_rebuilt` (every withheld cell where one pair of tails
    fits, else the cells every fit shares), `minimum_named` and
    `maximum_named` (whether every fit holds the column's own outermost
    values).
    """
    tails = block["tails"]
    sides = {side: state(tails[side]) for side in ("low", "high")}
    out: "dict" = {"sides": sides, "values_rebuilt": 0, "minimum_named": False, "maximum_named": False}
    if not (sides["low"] == "pair" and sides["high"] == "pair"):
        out["union"] = "not both published"
        return out
    if block.get("skew") is None or block.get("kurtosis") is None:
        out["union"] = "no exact third and fourth moments"
        return out
    n = block["n_used_in_statistics"]
    low_percent, high_percent = tails["low"]["percent"], tails["high"]["percent"]
    low_rows = parsing.tail_rows(n, low_percent, "low")
    high_rows = parsing.tail_rows(n, high_percent, "high")
    low_last = low_rows - 1
    high_first = n - high_rows
    truth_low = values[:low_rows]
    truth_high = values[high_first:]
    low_boundary = rung_of(block, low_percent)
    high_boundary = rung_of(block, high_percent)
    chains = solve_chain(
        rung_equations(block, n, low_percent, high_percent),
        range(int(low_boundary) - 5000, int(low_boundary) + 1),
    )
    out["chains"] = len(chains)
    if len(chains) != 1:
        return out
    chain = chains[0]
    first = whole_sum(block["mean"], n)[0]
    second = whole_squares(block["std"], n, first)[0]
    third = whole_cubes(block["skew"], n, first, second)
    assert third is not None and third[0] == third[1]
    third_sum = third[0]
    fourth = whole_fourths(block["kurtosis"], n, first, second, third_sum)
    assert fourth is not None
    interior = [chain[r] for r in range(low_last + 1, high_first)]
    fixed_low, fixed_high = chain[low_last], chain[high_first]
    lows = tail_sums(tails["low"], low_boundary, "low")
    highs = tail_sums(tails["high"], high_boundary, "high")
    assert len(lows) == 1 and len(highs) == 1
    least = 1 if block["n_zero"] == 0 and block["n_negative"] == 0 else 0
    low_sets, _low_done = different_multisets(
        low_rows - 1, lows[0][0] - fixed_low, lows[0][1] - fixed_low ** 2,
        least, fixed_low - 1, cap=10 ** 7, budget=budget,
    )
    high_sets, _high_done = different_multisets(
        high_rows - 1, highs[0][0] - fixed_high, highs[0][1] - fixed_high ** 2,
        fixed_high + 1, fixed_high + 10 ** 6, cap=10 ** 7, budget=budget,
    )
    rest_third = sum(v ** 3 for v in interior) + fixed_low ** 3 + fixed_high ** 3
    rest_fourth = sum(v ** 4 for v in interior) + fixed_low ** 4 + fixed_high ** 4
    by_third: "dict[int, list[list[int]]]" = collections.defaultdict(list)
    for one in high_sets:
        by_third[sum(v ** 3 for v in one)] += [one]
    fits: "list[tuple[list[int], list[int]]]" = []
    for low in low_sets:
        need = third_sum - rest_third - sum(v ** 3 for v in low)
        for high in by_third.get(need, []):
            total = rest_fourth + sum(v ** 4 for v in low) + sum(v ** 4 for v in high)
            if fourth[0] <= total <= fourth[1]:
                fits += [(sorted(low), sorted(high))]
    out["fits"] = len(fits)
    if fits:
        common_low = set(fits[0][0]).intersection(*[set(f[0]) for f in fits])
        common_high = set(fits[0][1]).intersection(*[set(f[1]) for f in fits])
        out["minimum_named"] = all(min(f[0]) == min(truth_low[:-1]) for f in fits)
        out["maximum_named"] = all(max(f[1]) == max(truth_high[1:]) for f in fits)
        if len(fits) == 1:
            out["values_rebuilt"] = len(truth_low) - 1 + len(truth_high) - 1
        else:
            out["values_rebuilt"] = len(common_low) + len(common_high)
    return out


def _grid(block: "dict") -> "int | None":
    if block.get("integer_valued") is True:
        return 0
    census = block.get("fraction_widths")
    styles = block.get("numeric_styles")
    if not isinstance(census, dict) or len(census) != 1 or not isinstance(styles, dict):
        return None
    free = sum(styles.get(key, 0) for key in ("plain", "leading_zero", "leading_plus"))
    for width in census:
        if not width.isdigit() or int(width) <= 0:
            return None
        if census[width] + free != block.get("n_used_in_statistics"):
            return None
        return int(width)
    return None


def _home_sums(block: "dict", side: str):
    """(rows, sum, sum of squares, home, scale) of a published tail's parts, or why not."""
    tail = block["tails"][side]
    if tail.get("values"):
        return "listed"
    if tail.get("mean_distance") is None:
        return "withheld"
    figures = _grid(block)
    if figures is None:
        return "no-grid"
    scale = 10 ** figures
    boundary = fractions.Fraction(rung_of(block, tail["percent"])) * scale
    home = math.floor(boundary) if side == "low" else math.ceil(boundary)
    offset = (boundary - home) if side == "low" else (home - boundary)
    rows = tail["rows"]
    mean = fractions.Fraction(tail["mean_distance"]) * scale
    root = fractions.Fraction(tail["rms_distance"]) * scale
    first = mean * rows - offset * rows
    second = root * root * rows - 2 * offset * first - rows * offset * offset
    whole_first, whole_second = round(first), round(second)
    if abs(first - whole_first) > fractions.Fraction(1, 64):
        return "not-whole"
    if abs(second - whole_second) > max(fractions.Fraction(1, 4), abs(whole_second) * fractions.Fraction(1, 10 ** 12)):
        return "not-whole"
    return rows, int(whole_first), int(whole_second), home, scale


def _cap(block: "dict", side: str, home: int, squares: int) -> int:
    negatives = block.get("n_negative", 0) - block.get("n_negative_unrepresentable", 0)
    used = block.get("n_used_in_statistics")
    positives = used - negatives - block.get("n_zero", 0) if isinstance(used, int) else None
    edge = math.isqrt(max(0, squares))
    if side == "low" and negatives <= 0 and home >= 0:
        edge = min(edge, home)
    if side == "high" and positives is not None and positives <= 0:
        edge = min(edge, max(-home, 0))
    return edge


def named_directly(block: "dict", side: str, values: "list[float]", budget: int = 1 << 22) -> "dict":
    """How many of a published tail's cells the producer's own lattice names, from the block alone.

    `values` (the column's sorted values) are used for one thing: to know
    which distances to ask about, as a reader may ask about any. A
    distance is NAMED where no multiset the published facts admit holds
    it a different number of times. A spent walk names nothing.
    """
    read = _home_sums(block, side)
    if isinstance(read, str):
        return {"status": read, "values": 0}
    rows, first, second, home, scale = read
    tail = values[:rows] if side == "low" else values[len(values) - rows:]
    parts = [home - round(v * scale) if side == "low" else round(v * scale) - home for v in tail]
    if sum(parts) != first or sum(p * p for p in parts) != second:
        return {"status": "reader-sums-disagree", "values": 0}
    edge = _cap(block, side, home, second)
    used = block.get("n_used_in_statistics")
    apart = isinstance(used, int) and used > 0 and block.get("n_distinct_values") == used
    held_budget = taxonomy.TAIL_LATTICE_STEPS
    taxonomy.TAIL_LATTICE_STEPS = budget
    try:
        lattice = taxonomy._Lattice(rows, first, second, max(edge, 1), apart, least=0)
        counts = collections.Counter(parts)
        # THE OUTERMOST DISTANCE IS ASKED FIRST, as the review's reader
        # asked it: a walk that spends its budget there names nothing.
        top = max(parts)
        for candidate in range(min(max(edge, 1), math.isqrt(second)), max(0, -(-first // rows)) - 1, -1):
            if candidate == top:
                continue
            if taxonomy._lattice_with_top(lattice, candidate) is not None:
                break
            if lattice.spent:
                return {"status": "unsearched", "values": 0}
        named = 0
        for distance in sorted(counts):
            held = counts[distance]
            fixed = True
            for other in sorted(range(0, rows + 1), key=lambda c: (abs(c - held), c)):
                if other == held:
                    continue
                if apart and other > 1:
                    break
                if taxonomy._lattice_with_count(lattice, distance, other) is not None:
                    fixed = False
                    break
                if lattice.spent:
                    return {"status": "unsearched", "values": 0}
            if fixed:
                named += held
        return {"status": "unique" if named == rows else ("partial" if named else "open"), "values": named}
    finally:
        taxonomy.TAIL_LATTICE_STEPS = held_budget


# -- the whole description, with no pair at all (ledger entry K-S3-24) -------

# The column family the review of plan P4-D353 measured this reader on
# (skeptic A2, 2026-09-26), beside the gate's own reconstruction attacks:
# one far value above a consecutive run, and a run whose top is a heap.
WHOLE_DESCRIPTION_FAMILY = (
    ("heap12_far_1101", [str(v) for v in range(1, 1089)] + ["1089"] * 12 + ["1250"]),
    ("heap_low_far_1501", ["0"] * 16 + [str(v) for v in range(1, 1484)] + ["1600", "1484"]),
    ("run_far_401", [str(v) for v in range(400)] + ["460"]),
    ("run_far_near_1101", [str(v) for v in range(1, 1100)] + ["1100", "1113"]),
    (
        "gappy_far_1501",
        [str(v) for v in sorted(random.Random("skA2/gappy_far_1501").sample(range(1, 30000), 1500))]
        + ["40000"],
    ),
)

WHOLE_COMBO_CAP = 300_000
WHOLE_STATE_CAP = 3_000_000
WHOLE_TAIL_CAP = 3


def _whole_segment(k: int, low: int, high: int, low_in: bool, mode: "int | None") -> "dict | None":
    """Every way `k` ranks between two pinned values can be filled, by what it adds.

    The values stand in `[low, high]`, each end admitted only where `low_in`
    says so (a low tail may reach its own least value) or as the mode; they
    are all different except the mode, which may repeat. Keyed by (sum, sum
    of squares, mode copies, zeros, negatives) -> [ways, one example, copies].
    None where the enumeration passes its cap.
    """
    free = [u for u in range(low, high + 1) if u != mode and (low_in or u != low) and u != high]
    inside = mode is not None and low <= mode <= high
    options: "dict" = {}
    for copies in range(0, k + 1) if inside else (0,):
        rest = k - copies
        if rest > len(free):
            continue
        if math.comb(len(free), rest) > WHOLE_COMBO_CAP:
            return None
        for chosen in itertools.combinations(free, rest):
            held = mode if copies else 0
            key = (
                sum(chosen) + copies * held,
                sum(u * u for u in chosen) + copies * held * held,
                copies,
                sum(1 for u in chosen if u == 0) + (copies if mode == 0 else 0),
                sum(1 for u in chosen if u < 0) + (copies if mode is not None and mode < 0 else 0),
            )
            if key not in options:
                options[key] = [0, chosen, copies]
            options[key][0] += 1
    return options


def _different_sets(count: int, total: int, squares: int, least: int, avoid: "int | None") -> "list[list[int]]":
    """Up to `WHOLE_TAIL_CAP` sets of `count` different whole numbers at or above `least`.

    Their sum is `total` and their sum of squares `squares`; `avoid` is never
    one of them (the mode, whose copies are counted apart).
    """
    found: "list[list[int]]" = []

    def walk(left: int, first: int, second: int, bottom: int, taken: "list[int]") -> None:
        nonlocal found
        if len(found) >= WHOLE_TAIL_CAP:
            return
        if left == 0:
            if first == 0 and second == 0:
                found += [list(taken)]
            return
        if first < left * bottom + left * (left - 1) // 2:
            return
        if left == 1:
            if first >= bottom and first * first == second and first != avoid:
                found += [taken + [first]]
            return
        top = (first - left * (left - 1) // 2) // left
        for value in range(bottom, top + 1):
            if value == avoid:
                continue
            rest_first = first - value
            rest_second = second - value * value
            others = left - 1
            if rest_second < sum((value + 1 + i) ** 2 for i in range(others)):
                break
            low_part = sum(value + 1 + i for i in range(others - 1))
            peak = rest_first - low_part
            most = sum((value + 1 + i) ** 2 for i in range(others - 1)) + peak * peak
            if rest_second > most:
                continue
            walk(others, rest_first, rest_second, value + 1, taken + [value])

    walk(count, total, squares, least, [])
    return found


def whole_description(block: "dict", values: "list[int]") -> "dict":
    """Every column the WHOLE published block admits, with no tail pair used at all.

    The channel the owner accepted on 2026-09-26 (ruling 8b, ledger entry
    `K-S3-24`): where `n_distinct_values`, the mode and its count, the sign
    counts and the rungs pin a column, its exact mean and spread give its
    values back although both tails withhold their pairs. Skeptic A2's
    reader, lifted: it reads `n_used_in_statistics`, `mean`, `std`, the
    hundred and one rungs, `integer_valued`, `n_distinct_values`, `mode`,
    `mode_count`, `n_zero`, `n_negative` and a listed low tail's values --
    never a mean or root-mean-square distance, never the skew or kurtosis.
    It enumerates every sorted column those admit, exactly: each run of
    ranks between two rungs, the low tail where no value is negative, and
    the high tail by what the mean and spread leave.

    It reads only a whole-number column whose rungs stand on whole ranks
    (`n - 1` a multiple of a hundred), whose one repeated value is the
    mode, and whose low side is bounded by the sign counts; anywhere else,
    or past its caps, it says why and names nothing -- so every count it
    gives is a floor on what comes back.

    Returns `read` (`whole` where one column fits, `high tail` where only
    the high tail is settled, else the reason), `values_rebuilt` (ranks
    whose value comes back exactly AND equals the column's own) and
    `maximum_named` (the settled high tail's largest value is the column's).
    `values` are the column's own sorted values, used only for that check.
    """
    out: "dict" = {"read": "n/a", "values_rebuilt": 0, "maximum_named": False}
    if "tails" not in block or not isinstance(block.get("tails"), dict):
        return out
    n = block["n_used_in_statistics"]
    if block.get("integer_valued") is not True:
        out["read"] = "not a whole-number column"
        return out
    if (n - 1) % 100:
        out["read"] = "rungs off whole ranks"
        return out
    distinct = block["n_distinct_values"]
    copies_of_mode = block["mode_count"]
    mode = block["mode"]
    if distinct == n:
        copies_of_mode, mode = 0, None
    elif not isinstance(copies_of_mode, int) or mode is None or n - distinct != copies_of_mode - 1:
        out["read"] = "a value other than the mode repeats"
        return out
    mode = int(mode) if mode is not None else None
    totals = whole_sum(block["mean"], n)
    if len(totals) != 1:
        out["read"] = "the mean admits no one whole sum"
        return out
    total = totals[0]
    squares_found = whole_squares(block["std"], n, total)
    if len(squares_found) != 1:
        out["read"] = "the spread admits no one whole sum of squares"
        return out
    squares = squares_found[0]
    zeros, negatives = block["n_zero"], block["n_negative"]
    pins: "dict[int, int]" = {}
    for percent in range(101):
        rung = rung_of(block, percent)
        if rung is not None:
            pins[(n - 1) * percent // 100] = int(rung)
    ranks = sorted(pins)
    fixed = (
        sum(pins.values()),
        sum(v * v for v in pins.values()),
        sum(1 for v in pins.values() if v == mode),
        sum(1 for v in pins.values() if v == 0),
        sum(1 for v in pins.values() if v < 0),
    )
    pieces: "list[dict]" = []
    for below, above in zip(ranks, ranks[1:]):
        if above - below > 1:
            found = _whole_segment(above - below - 1, pins[below], pins[above], False, mode)
            if found is None or not found:
                out["read"] = "a run between two rungs is too free" if found is None else "no run fits"
                return out
            pieces += [found]
    first, last = ranks[0], ranks[len(ranks) - 1]
    if first:
        if negatives != 0:
            out["read"] = "both sides unbounded"
            return out
        found = _whole_segment(first, 0 if zeros > 0 else 1, pins[first], True, mode)
        listed = block["tails"]["low"].get("values") or []
        if found is not None and listed:
            allowed = {int(v) for v in listed} | {pins[first]}
            found = {
                key: option for key, option in found.items()
                if set(option[1]) | ({mode} if option[2] else set()) <= allowed
            }
        if found is None or not found:
            out["read"] = "the low tail is too free" if found is None else "no low tail fits"
            return out
        pieces += [found]
    states = {fixed: 1}
    for found in pieces:
        after: "dict" = {}
        for (s1, s2, m, z, g), ways in states.items():
            for (t1, t2, tm, tz, tg), option in found.items():
                key = (s1 + t1, s2 + t2, m + tm, z + tz, g + tg)
                if key[2] > copies_of_mode or key[3] > zeros or key[4] > negatives:
                    continue
                after[key] = (after[key] if key in after else 0) + ways * option[0]
        states = after
        if len(states) > WHOLE_STATE_CAP:
            out["read"] = "too many interiors"
            return out
    high_rows = n - 1 - last
    edge = pins[last]
    settled: "list[tuple[int, list[int]]]" = []
    for (s1, s2, m, z, g), ways in states.items():
        extra = copies_of_mode - m
        if extra < 0 or extra > high_rows or (extra and (mode is None or mode < edge)):
            continue
        if negatives - g != 0 and edge >= 0:
            continue
        held = mode if extra else 0
        for tail in _different_sets(
            high_rows - extra, total - s1 - extra * held, squares - s2 - extra * held * held, edge + 1, mode
        ):
            if sum(1 for u in tail if u == 0) == zeros - z:
                settled += [(ways, sorted([held] * extra + tail))]
        if len(settled) > WHOLE_TAIL_CAP:
            break
    truth = sorted(values)
    if len(settled) != 1:
        out["read"] = "no column fits" if not settled else "more than one high tail fits"
        return out
    ways, high = settled[0]
    right = [a == b for a, b in zip(high, truth[n - high_rows:])]
    out["maximum_named"] = bool(high) and high[len(high) - 1] == truth[n - 1]
    if ways == 1 and all(right):
        out["read"] = "whole"
        out["values_rebuilt"] = n
        return out
    out["read"] = "high tail"
    out["values_rebuilt"] = sum(1 for one in right if one)
    return out
