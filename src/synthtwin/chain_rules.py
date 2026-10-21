"""The chain's rules read from published facts alone (contract 4.6b; plans P4-D407 and P4-D418).

WHAT IS HERE. Everything about stage 6's first layer, the CHAIN of floored
family tables, that is a function of the DESCRIPTION: the ladder of each
column (4.6b.2) built from its published rungs and its band totals, the
levels the search offers (RULES W3 and NE, 4.6b.3), a table's score
(`u = X2 - df`, an exact fraction), RULE W1's filter read on the published
tables' zero patterns (4.6b.3, 4.6b.9 (c)), RULE WE's bound (4.6b.3), the
draw's stated exponential and its choice from a word (4.6b.4) and the
structural words (4.6b.8). The loader's invariants S23 to S28 (4.6b.11)
read them in `chain_check`.

WHY ONE MODULE FOR BOTH HALVES. The producer (`chain`, zone D) decides
which options are eligible with these functions, and the loader
(`contract`, zone G) recomputes the same decisions from the description
and refuses one that disagrees (S24: "which options are eligible is a
function of the description, so the loader can check it"). Two copies of
one rule would drift; one copy cannot.

WHAT IS NOT HERE. Nothing reads a row of the real table, nothing reads
the installation's key, and no library float decides anything: counts
are Python integers, the score is a `fractions.Fraction`, and the
draw's exponential is the stated polynomial of 4.6b.4 in correctly
rounded binary64 steps (plan P4-D409 part 2, zone D's rule). The module
is reached by the loader, so it is held to zone G's imports.

NOT IN FORCE. Invariant S12 stands until the landing that ships stage 6:
`synthtwin profile`, `generate` and `validate` never publish or accept a
chain. These functions run only behind the switch the product does not
expose (`chain.ChainSwitch`, `contract.load_profile(..., chain=True)`).
"""

import dataclasses
import fractions
import math

from synthtwin import parsing

LEVELS = ("L0", "L1", "L2")
OTHER = "other"
LABELS = "labels"
MISSING = "missing"
POOL = "held back"
SPREAD = (OTHER, LABELS, MISSING)

ROLE_COUNT = "count"
ROLE_CONTINUOUS = "continuous"
ROLE_AFFIXED = "affixed_number"
ROLE_JOINED = "joined_numbers"
ROLE_COMPOUND = "numbers_with_labels"
ROLE_DATETIME = "datetime"
ROLE_CLOCK = "time_of_day"
ROLE_BINARY = "binary"
ROLE_CONSTANT = "constant"
ROLE_CATEGORICAL = "categorical"
ROLE_LONG_TAIL = "long_tail_labels"

NUMBER_ROLES = (ROLE_COUNT, ROLE_CONTINUOUS, ROLE_AFFIXED, ROLE_JOINED, ROLE_COMPOUND)
ORDERED_ROLES = NUMBER_ROLES + (ROLE_DATETIME, ROLE_CLOCK)
LABEL_ROLES = (ROLE_BINARY, ROLE_CONSTANT, ROLE_CATEGORICAL, ROLE_LONG_TAIL)

# 4.6b.2's table: the rungs each level's edges are cut at.
NUMBER_RUNGS = (
    ("p10", "p20", "p25", "p30", "p40", "p50", "p60", "p70", "p75", "p80", "p90"),
    ("p25", "p50", "p75", "p90"),
    ("p50",),
)
NINE_RUNGS = (
    ("p01", "p05", "p10", "p25", "p50", "p75", "p90", "p95", "p99"),
    ("p25", "p50", "p75", "p90"),
    ("p50",),
)

# The reasons 4.6b.1 lists, and no other.
INELIGIBLE_REASONS = (
    "identifier",
    "free_text",
    "empty",
    "unrepresentable",
    "sequence",
    "held",
    "constant",
    "one_band",
    "computed",
    "position_like",
)

# The settings of 4.6b.14 recorded in `procedure` (4.6b.5).
K_MAX = 3
TAU = fractions.Fraction(2)
W_RULE = fractions.Fraction(1, 20)
W_TE = fractions.Fraction(1)
W_SEED = fractions.Fraction(1, 20)
UNIFORM_SHARE_BITS = 30
L0_CUT = "deciles"
SELFTEST_SMALL = 20000
SELFTEST_LARGE = 200000
SELFTEST_LINE = 1000000

# The stated exponential's constants (4.6b.4): the binary64 values nearest
# 1 / ln 2 and ln 2, written as the decimal literals that read back as
# exactly those values (0x1.71547652b82fep0 and 0x1.62e42fefa39efp-1).
LOG2E = 1.4426950408889634
LN2 = 0.6931471805599453

# A label group that is not one published level of its own (L1's rest, L2's rest).
_REST = 1000000


def _get(mapping: "dict[str, object]", key: str) -> object:
    """A key's value, or None where the mapping does not hold it."""
    if key in mapping:
        return mapping[key]
    return None


def _whole(value: object) -> bool:
    """A whole number that is not a truth value."""
    return isinstance(value, int) and not isinstance(value, bool)


def _taylor() -> "tuple[float, ...]":
    """The fourteen coefficients `ck`, each the binary64 value nearest (-L)^k / k!.

    Each is computed exactly from `L` as a fraction and rounded once
    (4.6b.4): `float()` of a fraction is a correctly rounded division of
    two Python integers.
    """
    exact = fractions.Fraction(LN2)
    out: "list[float]" = []
    term = fractions.Fraction(1)
    for k in range(14):
        if k:
            term = term * (-exact) / k
        out += [float(term)]
    return tuple(out)


TAYLOR = _taylor()


def stated_exponential(y: float) -> float:
    """`E(y)`, the stated exponential of `e` to the power `-y`, for `y >= 0` (4.6b.4).

    Every step is a correctly rounded binary64 operation, an exact floor
    or an exact `ldexp`, so every machine returns the same weight; no
    library exponential is used. `E(y)` is exactly 0.0 where `j` exceeds
    1074.
    """
    if not y >= 0.0:
        raise ValueError("the stated exponential is read for y >= 0 only")
    t = y * LOG2E
    j = int(t)
    if j > 1074:
        return 0.0
    r = t - j
    p = TAYLOR[13]
    for k in range(12, -1, -1):
        p = TAYLOR[k] + r * p
    return math.ldexp(p, -j)


def weights_of(scores: "list[fractions.Fraction]", tau: fractions.Fraction) -> "list[float]":
    """Each eligible option's weight `E((v_max - v_i) / tau)`, in option order (4.6b.4)."""
    if not scores:
        return []
    top = max(scores)
    return [stated_exponential(float((top - one) / tau)) for one in scores]


def big_endian(data: bytes) -> int:
    """A run of bytes read as one big-endian whole number."""
    value = 0
    for byte in data:
        value = value * 256 + byte
    return value


def choose(word: bytes, weights: "list[float]") -> int:
    """The place of the option a step places, from its 16-byte word (4.6b.4).

    `U1` is the word's first 8 bytes and `U2` its last 8, each big-endian.
    Where `U1 >> 34` is 0 (the word's top 30 bits clear) the option at
    `(U2 * m) >> 64` is placed whatever its weight; otherwise the first
    option whose running sum of weights exceeds `(U2 >> 11) * 2**-53 * W`,
    or, where rounding leaves none, the last option of positive weight.
    """
    if len(word) != 16:
        raise ValueError("a step's word is 16 bytes")
    count = len(weights)
    if count == 0:
        raise ValueError("a step has at least one eligible option")
    first = big_endian(word[0:8])
    second = big_endian(word[8:16])
    if first >> (64 - UNIFORM_SHARE_BITS) == 0:
        return (second * count) >> 64
    running: "list[float]" = []
    total = 0.0
    for weight in weights:
        total = total + weight
        running += [total]
    target = math.ldexp(float(second >> 11), -53) * total
    for place in range(count):
        if running[place] > target:
            return place
    for place in range(count - 1, -1, -1):
        if weights[place] > 0.0:
            return place
    return count - 1


def fraction_text(value: fractions.Fraction) -> str:
    """A setting's fraction written as a string ("1/20", "1", "2")."""
    if value.denominator == 1:
        return f"{value.numerator}"
    return f"{value.numerator}/{value.denominator}"


def fraction_of(text: str) -> "fractions.Fraction | None":
    """A setting's string read back as a fraction, or None where it is not one."""
    if not isinstance(text, str):
        raise TypeError("a setting's fraction is text")
    numerator = 0
    denominator = 0
    seen_slash = False
    digits = 0
    for character in text:
        if character == "/":
            if seen_slash or digits == 0:
                return None
            seen_slash = True
            digits = 0
            continue
        if character not in "0123456789":
            return None
        digits += 1
        if seen_slash:
            denominator = denominator * 10 + ord(character) - 48
        else:
            numerator = numerator * 10 + ord(character) - 48
    if digits == 0:
        return None
    if not seen_slash:
        return fractions.Fraction(numerator)
    if denominator == 0:
        return None
    return fractions.Fraction(numerator, denominator)


def selftest_size(tabled: int) -> int:
    """The constant `selftest_sample` of 4.6b.14 at this many tabled rows."""
    return SELFTEST_SMALL if tabled < SELFTEST_LINE else SELFTEST_LARGE


def procedure_record(tabled: int) -> "dict[str, object]":
    """The constants this description ran under (4.6b.5's `procedure`)."""
    return {
        "k_max": K_MAX,
        "l0_cut": L0_CUT,
        "selftest_sample": selftest_size(tabled),
        "tau": fraction_text(TAU),
        "uniform_share_bits": UNIFORM_SHARE_BITS,
        "w_rule": fraction_text(W_RULE),
        "w_seed": fraction_text(W_SEED),
        "w_te": fraction_text(W_TE),
    }


# -- THE LADDER (4.6b.2) -------------------------------------------------


@dataclasses.dataclass(frozen=True)
class Starting:
    """A column's STARTING bands, before the `L0` merge, in band order.

    `names` are the published descriptors: a spread band's word, a range
    `[lower, upper]` named by rung keys (None where open), a published
    level as a one-item list, or the pool's word. `groups[level]` gives
    each starting band the band of that level it falls in before any
    merge (each spread band its own); the merge's union closure turns
    them into the published `l1` and `l2`. `values` holds the edge
    values the value bands are cut at, in the column's own order.
    """

    names: "tuple[object, ...]"
    groups: "tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]"
    value: "tuple[bool, ...]"
    is_label: bool
    values: "tuple[object, ...]"


@dataclasses.dataclass(frozen=True)
class Ladder:
    """One eligible column's published ladder (4.6b.2), with its level maps.

    `maps[level][i]` is the band of `level` holding `L0` band `i`;
    `counts[level]` the band count of that level; `totals` the `L0`
    totals over the tabled rows; `ordered[i]` whether `L0` band `i`
    holds a value band.
    """

    column: str
    l0: "tuple[tuple[object, ...], ...]"
    maps: "tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]"
    counts: "tuple[int, int, int]"
    totals: "tuple[int, ...]"
    ordered: "tuple[bool, ...]"


def totals_at(ladder: Ladder, level: int) -> "list[int]":
    """A ladder's band totals at one level, each the sum of its `L0` totals."""
    out = [0] * ladder.counts[level]
    for place in range(len(ladder.totals)):
        out[ladder.maps[level][place]] += ladder.totals[place]
    return out


def coarsen(ladder: Ladder, finer: int, coarser: int) -> "list[int]":
    """Each band of level `finer` mapped to the band of level `coarser` holding it."""
    out = [0] * ladder.counts[finer]
    for place in range(len(ladder.totals)):
        out[ladder.maps[finer][place]] = ladder.maps[coarser][place]
    return out


def published_ladder(ladder: Ladder) -> "dict[str, object]":
    """The ladder's entry as 4.6b.2 writes it: `{column, l0, l1, l2, totals}`."""
    return {
        "column": ladder.column,
        "l0": [[_written(name) for name in band] for band in ladder.l0],
        "l1": bands_of(ladder.maps[1], ladder.counts[1]),
        "l2": bands_of(ladder.maps[2], ladder.counts[2]),
        "totals": list(ladder.totals),
    }


def _written(name: object) -> object:
    """A starting band's descriptor as JSON writes it (a tuple as a list)."""
    if isinstance(name, tuple):
        return list(name)
    return name


def bands_of(mapping: "tuple[int, ...]", count: int) -> "list[list[int]]":
    """A level's bands, each the list of `L0` band indices it holds."""
    out: "list[list[int]]" = [[] for _place in range(count)]
    for place in range(len(mapping)):
        out[mapping[place]] += [place]
    return out


def rung_ladder(block: "dict[str, object]") -> "dict[str, object] | None":
    """The published rungs a column's value bands are cut at, keyed `p10` and so on."""
    role = _get(block, "role")
    holder: object = None
    if role in (ROLE_COUNT, ROLE_CONTINUOUS, ROLE_AFFIXED):
        holder = block
    elif role == ROLE_JOINED:
        parts = _get(block, "parts")
        if isinstance(parts, list) and parts:
            holder = parts[0]
    elif role == ROLE_COMPOUND:
        holder = _get(block, "numbers")
    elif role == ROLE_DATETIME:
        found = _get(block, "date_percentiles")
        return found if isinstance(found, dict) else None
    elif role == ROLE_CLOCK:
        found = _get(block, "clock_percentiles")
        return found if isinstance(found, dict) else None
    if not isinstance(holder, dict):
        return None
    out: "dict[str, object]" = {}
    for key in ("percentiles", "percentiles_between"):
        part = _get(holder, key)
        if isinstance(part, dict):
            for rung in part:
                out[rung] = part[rung]
    return out


def rung_value(role: str, rung: object, form: object) -> "object | None":
    """A rung's value in the column's own order: a number, a canonical date, a clock ordinal."""
    if rung is None:
        return None
    if role == ROLE_CLOCK:
        if not isinstance(form, str) or not isinstance(rung, str):
            return None
        if form not in parsing.CLOCK_FORMS:
            return None
        return parsing.clock_ordinal(rung, form)
    if role == ROLE_DATETIME:
        return rung if isinstance(rung, str) else None
    if isinstance(rung, bool) or not isinstance(rung, (int, float)):
        return None
    return float(rung)


def below(left: object, right: object) -> bool:
    """Whether `left` stands below `right` in a column's own order."""
    if isinstance(left, str) and isinstance(right, str):
        return left < right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return left < right
    return False


def _equal(left: object, right: object) -> bool:
    if isinstance(left, str) and isinstance(right, str):
        return left == right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return left == right
    return False


def edges_of(block: "dict[str, object]") -> "list[tuple[str, object]] | None":
    """`L0`'s edges before any merge: (rung key, value), strictly increasing.

    A `null` rung is no edge; where several rungs hold one value the edge
    names the one of lowest percent (4.6b.2). None where the role has no
    value rungs, or its rungs fall back.
    """
    role = f"{_get(block, 'role')}"
    rungs = rung_ladder(block)
    if rungs is None:
        return None
    form = _get(block, "clock_form")
    keys = NINE_RUNGS[0] if role in (ROLE_DATETIME, ROLE_CLOCK) else NUMBER_RUNGS[0]
    out: "list[tuple[str, object]]" = []
    for key in keys:
        value = rung_value(role, _get(rungs, key), form)
        if value is None:
            continue
        if out and not below(out[-1][1], value):
            if _equal(out[-1][1], value):
                continue
            return None
        out += [(key, value)]
    return out


def level_edge_values(block: "dict[str, object]", level: int) -> "list[object]":
    """The values of the rungs level `level` cuts at (`L1`: p25 p50 p75 p90; `L2`: p50)."""
    role = f"{_get(block, 'role')}"
    rungs = rung_ladder(block)
    if rungs is None:
        return []
    form = _get(block, "clock_form")
    keys = NINE_RUNGS[level] if role in (ROLE_DATETIME, ROLE_CLOCK) else NUMBER_RUNGS[level]
    out: "list[object]" = []
    for key in keys:
        value = rung_value(role, _get(rungs, key), form)
        if value is not None:
            out += [value]
    return out


def label_levels(block: "dict[str, object]") -> "list[tuple[str, int]]":
    """A label column's published levels, in published order: (label, count)."""
    role = _get(block, "role")
    out: "list[tuple[str, int]]" = []
    if role == ROLE_CONSTANT:
        value = _get(block, "value")
        present = _get(block, "n_present")
        if isinstance(value, str):
            out += [(value, present if isinstance(present, int) and not isinstance(present, bool) else 0)]
        return out
    levels = _get(block, "levels")
    if not isinstance(levels, list):
        return out
    for level in levels:
        if not isinstance(level, dict):
            continue
        label = _get(level, "label")
        count = _get(level, "count")
        if isinstance(label, str):
            out += [(label, count if isinstance(count, int) and not isinstance(count, bool) else 0)]
    return out


def starting_bands(block: "dict[str, object]", spread: "tuple[bool, bool, bool]") -> "Starting | None":
    """A column's starting bands in band order (4.6b.2's table and its band order).

    `spread` says which of `other`, `labels` and `missing` hold cells on
    the tabled rows; a spread band with no cell is no band. On a label
    column `spread[1]` says whether the held-back pool holds a cell. None
    where the role takes no ladder.
    """
    role = f"{_get(block, 'role')}"
    names: "list[object]" = []
    value: "list[bool]" = []
    groups: "list[list[int]]" = [[], [], []]
    if role in ORDERED_ROLES:
        edges = edges_of(block)
        if edges is None:
            return None
        for place in range(3):
            if spread[place]:
                names += [SPREAD[place]]
                value += [False]
                for level in range(3):
                    groups[level] += [-1 - place]
        cuts = [level_edge_values(block, 1), level_edge_values(block, 2)]
        for k in range(len(edges) + 1):
            lower = edges[k - 1][0] if k else None
            upper = edges[k][0] if k < len(edges) else None
            names += [(lower, upper)]
            value += [True]
            groups[0] += [k]
            for level in (1, 2):
                inside = 0
                if k:
                    for cut in cuts[level - 1]:
                        if not below(edges[k - 1][1], cut):
                            inside += 1
                groups[level] += [inside]
        return Starting(
            tuple(names),
            (tuple(groups[0]), tuple(groups[1]), tuple(groups[2])),
            tuple(value),
            False,
            tuple(edge[1] for edge in edges),
        )
    if role not in LABEL_ROLES:
        return None
    levels = label_levels(block)
    if spread[2]:
        names += [MISSING]
        value += [False]
        for level in range(3):
            groups[level] += [-1]
    ranked = sorted((-levels[place][1], place) for place in range(len(levels)))
    top_ten = {pair[1] for pair in ranked[:10]}
    top_one = {pair[1] for pair in ranked[:1]}
    many = role in (ROLE_CATEGORICAL, ROLE_LONG_TAIL)
    for place in range(len(levels)):
        names += [(levels[place][0],)]
        value += [True]
        groups[0] += [place]
        groups[1] += [place if (not many or place in top_ten) else _REST]
        groups[2] += [place if (not many or place in top_one) else _REST]
    if spread[1]:
        names += [POOL]
        value += [True]
        groups[0] += [len(levels)]
        groups[1] += [_REST if many else len(levels)]
        groups[2] += [_REST if many else len(levels)]
    return Starting(
        tuple(names),
        (tuple(groups[0]), tuple(groups[1]), tuple(groups[2])),
        tuple(value),
        True,
        (),
    )


def merge_ladder(column: str, start: Starting, totals: "list[int]", floor: int) -> "Ladder | None":
    """The `L0` merge, then `L1` and `L2` read through it (4.6b.2).

    A band holding no row is dropped (a value band's upper edge stops
    being an edge: it joins the value band above it, or the one below it
    at the top). While some band holds 1 to `floor - 1` rows: on a number,
    date or clock column the EARLIEST such band in band order is joined
    with its neighbour holding fewer rows, ties to the earlier neighbour;
    on a label column the two smallest bands are joined, `missing`
    counting as one, ties to the earlier (the order the page leaves open,
    fixed as built, plan P4-D418). Every printed `L0` total is then 0 or
    at least `floor`. None where no band holds a row.
    """
    bands: "list[list[int]]" = []
    counts: "list[int]" = []
    for place in range(len(start.names)):
        if totals[place] > 0 or (start.value[place] and not start.is_label):
            bands += [[place]]
            counts += [totals[place]]
    if not start.is_label:
        changed = True
        while changed:
            changed = False
            for at in range(len(bands)):
                if counts[at] != 0:
                    continue
                above = at + 1
                below_at = at - 1
                if above < len(bands) and start.value[bands[above][0]]:
                    target = above
                elif below_at >= 0 and start.value[bands[below_at][-1]]:
                    target = below_at
                else:
                    bands = bands[:at] + bands[at + 1 :]
                    counts = counts[:at] + counts[at + 1 :]
                    changed = True
                    break
                low, high = (at, target) if at < target else (target, at)
                bands = bands[:low] + [sorted(bands[low] + bands[high])] + bands[high + 1 :]
                counts = counts[:low] + [counts[low] + counts[high]] + counts[high + 1 :]
                changed = True
                break
    if not bands or sum(counts) == 0:
        return None
    while len(bands) >= 2:
        small = [at for at in range(len(bands)) if 0 < counts[at] < floor]
        if not small:
            break
        if start.is_label:
            ranked = sorted((counts[at], at) for at in range(len(bands)))
            low = min(ranked[0][1], ranked[1][1])
            high = max(ranked[0][1], ranked[1][1])
        else:
            at = small[0]
            if at == 0:
                other = 1
            elif at == len(bands) - 1:
                other = at - 1
            else:
                other = at - 1 if counts[at - 1] <= counts[at + 1] else at + 1
            low, high = (at, other) if at < other else (other, at)
        bands = bands[:low] + [sorted(bands[low] + bands[high])] + bands[high + 1 :]
        counts = counts[:low] + [counts[low] + counts[high]] + counts[high + 1 :]
    first = tuple(range(len(bands)))
    second = union_closure(bands, start.groups[1])
    third = union_closure(bands, start.groups[2])
    ordered = tuple(any(start.value[place] for place in band) for band in bands)
    names = tuple(tuple(start.names[place] for place in band) for band in bands)
    level_counts = (len(bands), max(second) + 1, max(third) + 1)
    return Ladder(column, names, (first, second, third), level_counts, tuple(counts), ordered)


def union_closure(bands: "list[list[int]]", groups: "tuple[int, ...]") -> "tuple[int, ...]":
    """Each `L0` band's band at a coarser level: groups joined wherever one `L0` band spans two."""
    parent = list(range(len(bands)))
    seen: "dict[int, int]" = {}
    for at in range(len(bands)):
        for place in bands[at]:
            group = groups[place]
            if group in seen:
                first = _root(parent, seen[group])
                second = _root(parent, at)
                if first != second:
                    parent[max(first, second)] = min(first, second)
            else:
                seen[group] = at
    out: "list[int]" = []
    names: "dict[int, int]" = {}
    for at in range(len(bands)):
        top = _root(parent, at)
        if top not in names:
            names[top] = len(names)
        out += [names[top]]
    return tuple(out)


def _root(parent: "list[int]", at: int) -> int:
    while parent[at] != at:
        parent[at] = parent[parent[at]]
        at = parent[at]
    return at


# -- OWN-FACT GROUPS (4.6b.3, RULE W1's groups) --------------------------


def band_of_value(edge_values: "tuple[object, ...]", value: object) -> int:
    """The starting value band (0-based among value bands) holding `value`."""
    place = 0
    for edge in edge_values:
        if below(value, edge):
            break
        place += 1
    return place


def _small(count: object, floor: int) -> bool:
    return isinstance(count, int) and not isinstance(count, bool) and 0 < count < floor


def small_group_bands(block: "dict[str, object]", start: Starting, ladder: Ladder, floor: int) -> "set[int]":
    """The `L0` bands of a column holding an OWN-FACT GROUP of 1 to `floor - 1` rows.

    Read from the column's published block (4.6b.3's list, read
    conservatively: a group whose band the facts do not place marks every
    band it may stand in, which refuses more and never passes more):
    one reading's count fixed by `mode_count` or `n_zero`; a published
    heap; a histogram bin of a few rows; a tail's published values or a
    tail of a few rows; the readings of a column of at most six different
    values; a missing spelling, a level's spelling or an unread kind of
    cell counted 1 to `floor - 1`; and every sub-band an `L0` merge took
    in.
    """
    role = f"{_get(block, 'role')}"
    l0_of_start: "dict[int, int]" = {}
    for at in range(len(ladder.l0)):
        for name in ladder.l0[at]:
            for place in range(len(start.names)):
                if start.names[place] == name:
                    l0_of_start[place] = at
    marked: "set[int]" = set()
    value_starts = [place for place in range(len(start.names)) if start.value[place]]
    every_value = {l0_of_start[place] for place in value_starts if place in l0_of_start}
    for at in range(len(ladder.l0)):
        if len(ladder.l0[at]) > 1:
            marked = marked | {at}
    holder: object = block
    if role == ROLE_JOINED:
        parts = _get(block, "parts")
        holder = parts[0] if isinstance(parts, list) and parts else {}
    elif role == ROLE_COMPOUND:
        holder = _get(block, "numbers")
    if not isinstance(holder, dict):
        holder = {}
    spread_at: "dict[str, int]" = {}
    for place in range(len(start.names)):
        name = start.names[place]
        if isinstance(name, str) and place in l0_of_start:
            spread_at[name] = l0_of_start[place]

    def at_value(reading: object) -> "set[int]":
        index = band_of_value(start.values, reading)
        if index < len(value_starts) and value_starts[index] in l0_of_start:
            return {l0_of_start[value_starts[index]]}
        return set()

    if role in NUMBER_ROLES:
        if _small(_get(holder, "n_zero"), floor):
            marked = marked | at_value(0.0)
        mode = _get(holder, "mode")
        if _small(_get(holder, "mode_count"), floor) and isinstance(mode, (int, float)) and not isinstance(mode, bool):
            marked = marked | at_value(float(mode))
        if _get(holder, "heaped") not in (None, {}, []):
            marked = marked | every_value
        histogram = _get(holder, "value_histogram")
        if isinstance(histogram, dict):
            for key in histogram:
                if _small(histogram[key], floor):
                    marked = marked | every_value
        tails = _get(holder, "tails")
        if isinstance(tails, dict):
            for key in tails:
                side = tails[key]
                if not isinstance(side, dict):
                    continue
                values = _get(side, "values")
                if isinstance(values, list):
                    for one in values:
                        if isinstance(one, (int, float)) and not isinstance(one, bool):
                            marked = marked | at_value(float(one))
                if _small(_get(side, "rows"), floor):
                    marked = marked | every_value
        distinct = _get(holder, "n_distinct_values")
        if distinct is None:
            distinct = _get(block, "n_distinct")
        if _whole(distinct) and isinstance(distinct, int) and distinct <= 6:
            marked = marked | every_value
        for key in ("n_out_of_range", "n_contradictory", "n_not_numeric", "n_label_cells"):
            if _small(_get(block, key), floor):
                for word in (OTHER, LABELS):
                    if word in spread_at:
                        marked = marked | {spread_at[word]}
    if role in (ROLE_DATETIME, ROLE_CLOCK):
        for key in ("low_tail", "high_tail"):
            side = _get(block, key)
            if isinstance(side, dict):
                if _get(side, "values") not in (None, []) or _small(_get(side, "rows"), floor):
                    marked = marked | every_value
        if _small(_get(block, "n_unparsed"), floor) and OTHER in spread_at:
            marked = marked | {spread_at[OTHER]}
    for key in ("missing_by_source", "missing_by_class"):
        census = _get(block, key)
        if isinstance(census, dict):
            for spelling in census:
                if _small(census[spelling], floor) and MISSING in spread_at:
                    marked = marked | {spread_at[MISSING]}
    if role in LABEL_ROLES:
        levels = _get(block, "levels")
        if isinstance(levels, list):
            for level in levels:
                if not isinstance(level, dict):
                    continue
                variants = _get(level, "variants")
                if not isinstance(variants, dict):
                    continue
                for spelling in variants:
                    if _small(variants[spelling], floor):
                        for place in range(len(start.names)):
                            if start.names[place] == (_get(level, "label"),) and place in l0_of_start:
                                marked = marked | {l0_of_start[place]}
    return marked


# -- THE FAMILIES (4.6b.5) ------------------------------------------------


@dataclasses.dataclass(frozen=True)
class Family:
    """One placed family: child at `level`, parents at theirs, its complete table.

    `table` is flat, row-major: one row a joint cell of the parents (the
    last parent varying fastest), one column a band of the child.
    """

    child: str
    level: int
    parents: "tuple[tuple[str, int], ...]"
    anchor: "int | None"
    table: "tuple[int, ...]"



def members(family: Family) -> "tuple[tuple[str, int], ...]":
    """A family's child, then its parents, each with its level there."""
    return ((family.child, family.level),) + family.parents


def radices(family: Family, ladders: "dict[str, Ladder]") -> "list[int]":
    """Each member's band count at its level in the family, child first."""
    return [ladders[name].counts[level] for name, level in members(family)]


def cell_parts(index: int, sizes: "list[int]") -> "list[int]":
    """A flat cell index split into each member's band, child first."""
    child = index % sizes[0]
    rest = index // sizes[0]
    parents: "list[int]" = []
    for size in sizes[:0:-1]:
        parents = [rest % size] + parents
        rest //= size
    return [child] + parents


@dataclasses.dataclass(frozen=True)
class ParentCells:
    """A candidate's parents and its anchor, read for RULE NE's margins.

    The parents' joint cell totals at chosen levels are the anchor's
    published table summed to them, or, for a root pair, the parent's own
    band totals. `kept` holds them by levels, since W3 and NE ask the
    same levels of many candidates.
    """

    ladders: "dict[str, Ladder]"
    parents: "tuple[str, ...]"
    anchor: "Family | None"
    kept: "dict[tuple[int, ...], list[int]]"


def parent_cells(ladders: "dict[str, Ladder]", parents: "tuple[str, ...]", anchor: "Family | None") -> ParentCells:
    """A candidate's margins, nothing summed yet."""
    return ParentCells(ladders, parents, anchor, {})


def parent_cells_at(margins: ParentCells, levels: "tuple[int, ...]") -> "list[int]":
    """The parents' joint cell totals at `levels`, the last parent varying fastest."""
    if levels in margins.kept:
        return margins.kept[levels]
    ladders = margins.ladders
    anchor = margins.anchor
    if anchor is None:
        out = totals_at(ladders[margins.parents[0]], levels[0])
        margins.kept[levels] = out
        return out
    held = members(anchor)
    sizes = radices(anchor, ladders)
    places: "list[int]" = []
    maps: "list[list[int]]" = []
    width = 1
    for at_place in range(len(margins.parents)):
        name = margins.parents[at_place]
        for place in range(len(held)):
            if held[place][0] == name:
                places += [place]
                maps += [coarsen(ladders[name], held[place][1], levels[at_place])]
        width *= ladders[name].counts[levels[at_place]]
    out = [0] * width
    table = anchor.table
    for index in range(len(table)):
        count = table[index]
        if not count:
            continue
        parts = cell_parts(index, sizes)
        cell = 0
        for at_place in range(len(places)):
            name = margins.parents[at_place]
            cell = cell * ladders[name].counts[levels[at_place]] + maps[at_place][parts[places[at_place]]]
        out[cell] += count
    margins.kept[levels] = out
    return out


# -- THE OFFERED LEVELS (RULES W3 AND NE, 4.6b.3) ------------------------


def offered_levels(
    ladders_of: "list[Ladder]",
    start: "list[int]",
    order: "list[int]",
    margins: "ParentCells | None",
    tabled: int,
    floor: int,
) -> "list[int] | None":
    """W3 and NE's levels for a candidate, or None where it is not offered.

    `ladders_of[0]` is the child, the rest the parents; `start` their
    starting levels (the child at `L0`, each parent at its level in the
    anchor, a root pair both at `L0`); `order` each member's place in
    schema order (the tie rule). `margins` gives the parents' joint cell
    totals (RULE NE); None for a candidate with no parent.
    """
    levels = list(start)
    count = len(ladders_of)
    while True:
        bands = [ladders_of[at].counts[levels[at]] for at in range(count)]
        failing: "list[int]" = []
        for at in range(count):
            others = 1
            for other in range(count):
                if other != at:
                    others *= bands[other]
            if min(totals_at(ladders_of[at], levels[at])) < floor * others:
                failing += [at]
        if not failing:
            break
        movable = [(min(totals_at(ladders_of[at], levels[at])), order[at], at) for at in failing if levels[at] < 2]
        if not movable:
            return None
        levels[min(movable)[2]] += 1
    if count == 1 or margins is None:
        return levels
    while True:
        child_totals = totals_at(ladders_of[0], levels[0])
        cells = parent_cells_at(margins, tuple(levels[1:]))
        smallest_cell = min(cells)
        smallest_child = min(child_totals)
        if smallest_child * smallest_cell >= (floor + 1) * tabled:
            return levels
        movable = [(min(totals_at(ladders_of[at], levels[at])), order[at], at) for at in range(count) if levels[at] < 2]
        if not movable:
            return None
        levels[min(movable)[2]] += 1


def variants_of(levels: "list[int]") -> "list[tuple[int, ...]]":
    """Every combination in which each member stands at its offered level or coarser."""
    out: "list[tuple[int, ...]]" = [()]
    for level in levels:
        out = [done + (step,) for done in out for step in range(level, 3)]
    return out


# -- THE SCORE (4.6b.3) ---------------------------------------------------


def gcd(a: int, b: int) -> int:
    """Euclid's greatest common divisor of two non-negative whole numbers."""
    while b:
        a, b = b, a % b
    return a


def score(table: "list[int] | tuple[int, ...]", rows: int, columns: int) -> fractions.Fraction:
    """`u = X2 - df` of a table, exactly: Pearson's chi-square less its degrees of freedom.

    `X2` sums `(O - E)^2 / E` over cells whose expected count is not
    nought; `df` is `(r - 1)(c - 1)` over the rows and columns whose
    totals are not nought. Written as `N * sum(O^2 / (R C)) - N` over
    common denominators of Python integers, one fraction at the end.
    """
    row_totals = [0] * rows
    column_totals = [0] * columns
    for r in range(rows):
        for c in range(columns):
            cell = table[r * columns + c]
            row_totals[r] += cell
            column_totals[c] += cell
    total = sum(row_totals)
    live_rows = [r for r in range(rows) if row_totals[r]]
    live_columns = [c for c in range(columns) if column_totals[c]]
    if total == 0:
        return fractions.Fraction(0)
    column_lcm = 1
    for c in live_columns:
        column_lcm = column_lcm * column_totals[c] // gcd(column_lcm, column_totals[c])
    row_lcm = 1
    for r in live_rows:
        row_lcm = row_lcm * row_totals[r] // gcd(row_lcm, row_totals[r])
    numerator = 0
    for r in live_rows:
        inner = 0
        for c in live_columns:
            cell = table[r * columns + c]
            if cell:
                inner += cell * cell * (column_lcm // column_totals[c])
        numerator += inner * (row_lcm // row_totals[r])
    chi = fractions.Fraction(total * numerator, row_lcm * column_lcm) - total
    df = (len(live_rows) - 1) * (len(live_columns) - 1)
    return chi - df


# -- RULE W1 (4.6b.3, 4.6b.9 (c)) ----------------------------------------


@dataclasses.dataclass(frozen=True)
class Support:
    """RULE W1's support: which combinations of chain-level bands the published zeros leave open.

    Exact boolean message passing over the chain's junction tree (each
    family joined to its anchor through its parents, every parent held
    at its anchor's level or coarser), read from the published tables'
    zero patterns alone: 4.6b.3's "passing true and false along the
    chain". `cells[f]` is family `f`'s non-zero cells, each (flat index,
    member bands); `links[f]` reads family `f`'s parents in its anchor's
    cells, each (the anchor member's place, the coarsening to `f`'s
    level).
    """

    families: "tuple[Family, ...]"
    chain_level: "dict[str, int]"
    home: "dict[str, int]"
    children: "tuple[tuple[int, ...], ...]"
    cells: "tuple[tuple[tuple[int, tuple[int, ...]], ...], ...]"
    links: "tuple[tuple[tuple[int, tuple[int, ...]], ...], ...]"


def support_of(families: "list[Family]", ladders: "dict[str, Ladder]") -> Support:
    """The chain's support, read from its families' published tables."""
    chain_level: "dict[str, int]" = {}
    home: "dict[str, int]" = {}
    for at in range(len(families)):
        chain_level[families[at].child] = families[at].level
        home[families[at].child] = at
    children: "list[list[int]]" = [[] for _family in families]
    for at in range(len(families)):
        anchor = families[at].anchor
        if anchor is not None:
            children[anchor] += [at]
    cells: "list[tuple[tuple[int, tuple[int, ...]], ...]]" = []
    links: "list[tuple[tuple[int, tuple[int, ...]], ...]]" = []
    for at in range(len(families)):
        family = families[at]
        sizes = radices(family, ladders)
        live: "list[tuple[int, tuple[int, ...]]]" = []
        for index in range(len(family.table)):
            if family.table[index]:
                live += [(index, tuple(cell_parts(index, sizes)))]
        cells += [tuple(live)]
        link: "list[tuple[int, tuple[int, ...]]]" = []
        if family.anchor is not None:
            anchor_members = members(families[family.anchor])
            for name, level in family.parents:
                for place in range(len(anchor_members)):
                    if anchor_members[place][0] == name:
                        link += [(place, tuple(coarsen(ladders[name], anchor_members[place][1], level)))]
        links += [tuple(link)]
    return Support(
        tuple(families),
        chain_level,
        home,
        tuple(tuple(one) for one in children),
        tuple(cells),
        tuple(links),
    )


def seen_from_anchor(support: Support, at: int, anchor_parts: "tuple[int, ...]") -> "tuple[int, ...]":
    """An anchor cell's bands of family `at`'s parents, coarsened to `at`'s levels."""
    return tuple(mapping[anchor_parts[place]] for place, mapping in support.links[at])


def beliefs(support: Support, clamp: "tuple[str, set[int]] | None" = None) -> "list[list[tuple[int, tuple[int, ...]]]]":
    """Each family's cells some feasible combination reaches, under one clamp.

    A clamp keeps only the cells of a column's own family where it stands
    in a given set of its chain-level bands. Children follow their anchor
    in chain order, so one pass from the last family up and one from the
    first down settle every family exactly (the chain is a junction
    tree: each column's families are joined through it, 4.6b.5).
    """
    count = len(support.families)
    kept: "list[list[tuple[int, tuple[int, ...]]]]" = [[] for _place in range(count)]
    for at in range(count - 1, -1, -1):
        cells = list(support.cells[at])
        if clamp is not None and clamp[0] in support.home and support.home[clamp[0]] == at:
            cells = [cell for cell in cells if cell[1][0] in clamp[1]]
        for child in support.children[at]:
            messages = {cell[1][1:] for cell in kept[child]}
            cells = [cell for cell in cells if seen_from_anchor(support, child, cell[1]) in messages]
        kept[at] = cells
    final: "list[list[tuple[int, tuple[int, ...]]]]" = [[] for _place in range(count)]
    for at in range(count):
        cells = kept[at]
        anchor = support.families[at].anchor
        if anchor is not None:
            reach = {seen_from_anchor(support, at, cell[1]) for cell in final[anchor]}
            cells = [cell for cell in cells if cell[1][1:] in reach]
        final[at] = cells
    return final


def column_bands(support: Support, reached: "list[list[tuple[int, tuple[int, ...]]]]", name: str) -> "set[int]":
    """A column's chain-level bands some feasible combination reaches."""
    return {cell[1][0] for cell in reached[support.home[name]]}


def w1_refusals(
    families: "list[Family]",
    ladders: "dict[str, Ladder]",
    groups: "dict[str, set[int]]",
) -> "list[tuple[str, int, str]]":
    """RULE W1 in full (4.6b.3): every (column, chain-level band, other column) that fails.

    For every placed column `c`, every chain-level band `beta` of `c`
    holding an own-fact group (`groups[c]`, `L0` bands), and every other
    placed column `m`: the support beside `beta` must reach at least two
    bands of `m`'s coarsest level, `L2`. Returns each failing triple in
    chain order, empty where W1 holds.
    """
    support = support_of(families, ladders)
    failing: "list[tuple[str, int, str]]" = []
    for family in families:
        name = family.child
        if name not in groups:
            continue
        level = support.chain_level[name]
        ladder = ladders[name]
        bands = sorted({ladder.maps[level][at] for at in groups[name]})
        for band in bands:
            reached_all = beliefs(support, (name, {band}))
            for other_family in families:
                other = other_family.child
                if other == name:
                    continue
                reached = column_bands(support, reached_all, other)
                coarse = coarsen(ladders[other], support.chain_level[other], 2)
                if len({coarse[at] for at in reached}) < 2:
                    failing += [(name, band, other)]
    return failing


# -- RULE WE (4.6b.3) -----------------------------------------------------


def blank_record_room(document: "dict[str, object]", floor: int) -> int:
    """`Z`: at most how many tabled rows are blank in every column of the table."""
    source = _get(document, "source")
    if not isinstance(source, dict):
        return 0
    line = max(2, floor)
    workbook = _get(source, "workbook")
    if isinstance(workbook, dict):
        return 0 if _get(workbook, "empty_rows_inside") is not None else line - 1
    if floor <= 1:
        return 0
    room = 0
    dialect = _get(source, "dialect")
    if isinstance(dialect, dict):
        empty = _get(dialect, "empty_rows")
        if isinstance(empty, dict):
            for key in ("interior", "leading", "trailing"):
                if _get(empty, key) == 0:
                    room += line - 1
    return room


def records_holding_nothing(document: "dict[str, object]") -> int:
    """`E`: the records holding nothing that a published count places (4.6b.5)."""
    source = _get(document, "source")
    if not isinstance(source, dict):
        return 0
    workbook = _get(source, "workbook")
    if isinstance(workbook, dict):
        inside = _get(workbook, "empty_rows_inside")
        return inside if isinstance(inside, int) and not isinstance(inside, bool) else 0
    total = 0
    dialect = _get(source, "dialect")
    if isinstance(dialect, dict):
        empty = _get(dialect, "empty_rows")
        if isinstance(empty, dict):
            for key in ("interior", "leading", "trailing"):
                count = _get(empty, key)
                if isinstance(count, int) and not isinstance(count, bool):
                    total += count
    return total


def outside_cells(document: "dict[str, object]", eligible: "set[str]") -> int:
    """`P`: the cells that are not blank, over the columns outside the ladder."""
    rows = _get(document, "n_rows")
    whole_rows = rows if isinstance(rows, int) and not isinstance(rows, bool) else 0
    total = 0
    columns = _get(document, "columns")
    if not isinstance(columns, list):
        return 0
    for block in columns:
        if not isinstance(block, dict) or _get(block, "name") in eligible:
            continue
        blank = _get(block, "n_missing_blank")
        if isinstance(blank, int) and not isinstance(blank, bool):
            total += whole_rows - blank
    return total


def blank_cell(ladders: "dict[str, Ladder]", blank_counts: "dict[str, int]") -> "dict[str, int] | None":
    """`x0`: each eligible column's `L0` band holding its blank cells, or None where one holds none."""
    out: "dict[str, int]" = {}
    for name in ladders:
        if name not in blank_counts or blank_counts[name] <= 0:
            return None
        ladder = ladders[name]
        found = -1
        for at in range(len(ladder.l0)):
            if MISSING in ladder.l0[at]:
                found = at
        if found < 0:
            return None
        out[name] = found
    return out


def cell_bound(x0: "dict[str, int]", families: "list[Family]", ladders: "dict[str, Ladder]", tabled: int) -> int:
    """`b(x0)`: the smallest published number counting a set of rows holding `x0` (4.6b.9 (a))."""
    bound = tabled
    for name in x0:
        bound = min(bound, ladders[name].totals[x0[name]])
    for family in families:
        sizes = radices(family, ladders)
        held = members(family)
        if any(name not in x0 for name, _level in held):
            continue
        index = 0
        for place in range(1, len(held)):
            name, level = held[place]
            index = index * sizes[place] + ladders[name].maps[level][x0[name]]
        child, level = held[0]
        bound = min(bound, family.table[index * sizes[0] + ladders[child].maps[level][x0[child]]])
    return bound


# -- WORDS (4.6b.8) -------------------------------------------------------


def words_of(eligible: "list[str]", families: "list[Family]") -> "tuple[list[dict[str, object]], list[list[str]]]":
    """Every candidate pair's structural word, and the pairs reading `implied`."""
    together: "set[tuple[str, str]]" = set()
    for family in families:
        names = [name for name, _level in members(family)]
        for first in names:
            for second in names:
                if first != second:
                    together = together | {(first, second)}
    words: "list[dict[str, object]]" = []
    implied: "list[list[str]]" = []
    for at in range(len(eligible)):
        for other in eligible[at + 1 :]:
            word = "exact" if (eligible[at], other) in together else "implied"
            words += [{"columns": [eligible[at], other], "word": word}]
            if word == "implied":
                implied += [[eligible[at], other]]
    return words, implied
