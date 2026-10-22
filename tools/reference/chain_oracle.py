"""The chain's oracle in exact arithmetic (lane CHo): contract 4.6b and method G16, from the page alone.

WHAT THIS IS. An independent reading of `docs/spec/profile-contract-v6.md`
section 4.6b (the chain of floored family tables) and
`docs/spec/generation-method-v1.md` G16 (the walk that deals them),
written from those pages and from nothing else: lane CHa's and lane
CHb's code is not read. It imports neither synthtwin, nor numpy, nor
pandas, nor a solver, and every decision it takes is made in Python
integers or exact fractions.

WHERE THE PAGES ASK FOR BINARY64. Two rules are stated on binary64
arithmetic: RULE W5's stated exponential and running weight sums
(contract 4.6b.4) and the walk's latent order `L` (G16.2 step 2). Each
correctly rounded binary64 operation is EMULATED here: the exact result
is formed as a fraction and rounded to the nearest binary64 value, ties
to the even significand, by `b64`. That is the definition of a correctly
rounded operation, so the emulation gives the bits CPython gives on
every machine, and no Python float is formed (the test file scans this
module for float literals and float calls).

WHAT IS COVERED (the case list of the design's 10.3, plan P4-D421):
each column's ladder and band codes with the `L0` merge (4.6b.2); a pair's table and
its implied table with the dealing spread (V12.2); a family's complete
table (4.6b.5); the score `u = X2 - df` (4.6b.3); RULES W3 and NE and
their variants; the floor; RULE W1 read at the other column's coarsest
level, member by member and across the chain; RULE WE's cell bound; the
draw of RULE W5 for a given key; the walk (G16.2), the moved target
(G16.6) and a carried order rule's computed column (G16.2 step 5).

WHAT IS NOT. Row 9's one test for a carried rule (lane CHa's case),
the patient layer (G16.13), the polish (G17.8) and the triple screen's
seeds (an input here, never computed).
"""

import fractions
import hashlib
import itertools
import json

F = fractions.Fraction

DEFAULT_FLOOR = 11
K_MAX = 3
LEVELS = (0, 1, 2)

# --- binary64, emulated in exact arithmetic -----------------------------

_TWO52 = 1 << 52
_TWO53 = 1 << 53


def _scaled(numerator, denominator, exponent):
    """The fraction numerator / denominator divided by 2 ** exponent."""
    if exponent >= 0:
        return F(numerator, denominator << exponent)
    return F(numerator << -exponent, denominator)


def b64(value):
    """The binary64 value nearest `value`, ties to the even significand, as a fraction.

    Raises OverflowError past the largest finite binary64. Subnormal
    results round on the grid of 2 ** -1074, as IEEE 754 does.
    """
    q = F(value)
    if q == 0:
        return F(0)
    negative = q < 0
    a = -q if negative else q
    n, d = a.numerator, a.denominator
    e = n.bit_length() - d.bit_length() - 53
    m = _scaled(n, d, e)
    while m >= _TWO53:
        e += 1
        m = _scaled(n, d, e)
    while m < _TWO52:
        e -= 1
        m = _scaled(n, d, e)
    if e < -1074:
        e = -1074
        m = _scaled(n, d, e)
    whole = m.numerator // m.denominator
    rest = m - whole
    if rest > F(1, 2) or (rest == F(1, 2) and whole % 2 == 1):
        whole += 1
    if whole == _TWO53:
        whole = _TWO52
        e += 1
    if e > 971:
        raise OverflowError("past the largest finite binary64")
    out = F(whole) * (F(2) ** e)
    return -out if negative else out


def b64_hex(value):
    """The form Python's `float.hex` prints for a binary64 value held as a fraction."""
    x = F(value)
    if b64(x) != x:
        raise ValueError("not a binary64 value")
    if x == 0:
        return "0x0.0p+0"
    sign = "-" if x < 0 else ""
    a = abs(x)
    exponent = (a.numerator.bit_length() - a.denominator.bit_length())
    while F(2) ** exponent > a:
        exponent -= 1
    while F(2) ** (exponent + 1) <= a:
        exponent += 1
    if exponent < -1022:
        fraction = a / (F(2) ** -1022)
        lead = 0
        exponent = -1022
    else:
        fraction = a / (F(2) ** exponent)
        lead = 1
    tail = (fraction - lead) * _TWO52
    if tail.denominator != 1:
        raise ValueError("not a binary64 value")
    return "%s0x%d.%013xp%+d" % (sign, lead, tail.numerator, exponent)


def from_hex(text):
    """The exact value of a C99 hexadecimal floating constant, `0x1.71547652b82fep0`."""
    body = text.lower()
    negative = body.startswith("-")
    body = body.lstrip("+-")
    if not body.startswith("0x"):
        raise ValueError("a hexadecimal constant starts 0x")
    mantissa, _, power = body[2:].partition("p")
    whole, _, digits = mantissa.partition(".")
    value = F(int(whole or "0", 16))
    if digits:
        value += F(int(digits, 16), 16 ** len(digits))
    value *= F(2) ** int(power or "0")
    return -value if negative else value


def b64_add(a, b):
    return b64(F(a) + F(b))


def b64_sub(a, b):
    return b64(F(a) - F(b))


def b64_mul(a, b):
    return b64(F(a) * F(b))


def b64_div(a, b):
    return b64(F(a) / F(b))


def b64_floor(a):
    """`floor` of a binary64 value: an exact whole number."""
    x = F(a)
    return x.numerator // x.denominator


def b64_ldexp(a, power):
    """`ldexp(a, power)`, rounded once as C's ldexp rounds a subnormal result."""
    return b64(F(a) * (F(2) ** power))


# --- RULE W5's stated exponential (contract 4.6b.4) ---------------------

LOG2E = from_hex("0x1.71547652b82fep0")
LN2 = from_hex("0x1.62e42fefa39efp-1")


def _taylor_coefficients():
    out = []
    factorial = 1
    for k in range(14):
        if k:
            factorial *= k
        out += [b64(F((-LN2) ** k) / factorial)]
    return tuple(out)


COEFFICIENTS = _taylor_coefficients()


def stated_exponential(gap):
    """`E(y)` of contract 4.6b.4 for `y = gap` (an exact fraction at least nought).

    `y` is the binary64 nearest the gap; `t = y * LOG2E`; `j = floor(t)`
    and `r = t - j`; `p(r)` by Horner's rule from `c13` down to `c0`;
    `E = ldexp(p(r), -j)`, exactly nought where `j` exceeds 1074. Each
    step is one correctly rounded binary64 operation.
    """
    y = b64(gap)
    if y < 0:
        raise ValueError("the stated exponential reads gaps of at least nought")
    t = b64_mul(y, LOG2E)
    j = b64_floor(t)
    r = b64_sub(t, j)
    acc = COEFFICIENTS[13]
    for k in range(12, -1, -1):
        acc = b64_add(COEFFICIENTS[k], b64_mul(r, acc))
    if j > 1074:
        return F(0)
    return b64_ldexp(acc, -j)


# --- the word and the choice (contract 4.6b.4) ---------------------------

PERSON_DRAW = b"synthtwin.draw.1"
PERSON_FINGERPRINT = b"synthtwin.kfp.1"


def word(key, name, kind, index, columns):
    """Step `index`'s 16-byte word: keyed BLAKE2b over `[name, kind, index, columns]`."""
    payload = json.dumps([name, kind, index, list(columns)], separators=(",", ":"), ensure_ascii=False)
    return hashlib.blake2b(payload.encode("utf-8"), key=key, digest_size=16, person=PERSON_DRAW).digest()


def fingerprint(key):
    """The key's fingerprint: keyed BLAKE2b of `b"key fingerprint"`, 8 bytes, its own domain."""
    return hashlib.blake2b(b"key fingerprint", key=key, digest_size=8, person=PERSON_FINGERPRINT).digest()


def choose(word_bytes, scores, tau):
    """The option RULE W5 places, by its place among the eligible options.

    `scores` are the eligible options' raised scores `v_i` (exact
    fractions) in option order; `tau` the temperature. Returns `(place,
    how, weights)`: `how` is "uniform" where the word's top 30 bits are
    clear, else "weighted"; `weights` the stated exponentials.
    """
    m = len(scores)
    if m == 0:
        raise ValueError("a step always has an eligible option")
    u1 = int.from_bytes(word_bytes[:8], "big")
    u2 = int.from_bytes(word_bytes[8:], "big")
    top = max(scores)
    weights = [stated_exponential((top - v) / F(tau)) for v in scores]
    if u1 >> 34 == 0:
        return (u2 * m) >> 64, "uniform", weights
    running = []
    acc = F(0)
    for w in weights:
        acc = b64_add(acc, w)
        running += [acc]
    total = running[-1]
    threshold = b64_mul(b64_mul(u2 >> 11, F(1, 1 << 53)), total)
    for place, s in enumerate(running):
        if s > threshold:
            return place, "weighted", weights
    for place in range(m - 1, -1, -1):
        if weights[place] > 0:
            return place, "weighted", weights
    return m - 1, "weighted", weights


# --- each column's ladder (contract 4.6b.2) -------------------------------------------

NUMBER_L0 = ("p10", "p20", "p25", "p30", "p40", "p50", "p60", "p70", "p75", "p80", "p90")
NUMBER_L1 = ("p25", "p50", "p75", "p90")
NUMBER_L2 = ("p50",)
SPREAD_ORDER = ("other", "labels", "missing")


class Ladder:
    """One eligible column's three nested levels over the tabled rows.

    `l0` lists the `L0` bands in band order, each a list of the starting
    bands it joins (`"missing"`, `"other"`, `"labels"`, a value range
    `(lower_key, upper_key)` with None where open, or a level name).
    `totals` are the `L0` totals; `l1` and `l2` list each coarser band as
    a list of `L0` band indices; `row_l0` is each row's `L0` band;
    `taken_in` lists the `L0` bands that took in a sub-band of 1 to
    `f - 1` rows (an own-fact group for RULE W1).
    """

    def __init__(self, name, role, l0, totals, l1, l2, row_l0, taken_in, ordered, position=0):
        self.name = name
        self.position = position
        self.role = role
        self.l0 = l0
        self.totals = totals
        self.l1 = l1
        self.l2 = l2
        self.row_l0 = row_l0
        self.taken_in = taken_in
        self.ordered = ordered

    def bands(self, level):
        """The bands of a level, each a list of `L0` band indices."""
        if level == 0:
            return [[i] for i in range(len(self.l0))]
        return self.l1 if level == 1 else self.l2

    def coarsen(self, level):
        """The map from each `L0` band to its band at `level`."""
        out = {}
        for b, members in enumerate(self.bands(level)):
            for i in members:
                out[i] = b
        return out

    def codes(self, level):
        """Each row's band at `level` (its band code, G16.1)."""
        to = self.coarsen(level)
        return [to[i] for i in self.row_l0]

    def band_totals(self, level):
        return [sum(self.totals[i] for i in members) for members in self.bands(level)]

    def as_dict(self):
        return {
            "column": self.name,
            "l0": [[list(s) if isinstance(s, tuple) else s for s in band] for band in self.l0],
            "l1": self.l1,
            "l2": self.l2,
            "totals": self.totals,
            "taken_in": self.taken_in,
        }


def _number_edges(rungs, keys):
    """The rung keys that are edges: published, not null, the lowest percent where tied."""
    out = []
    held = set()
    for key in keys:
        value = rungs.get(key)
        if value is None:
            continue
        value = F(value)
        if value in held:
            continue
        held.add(value)
        out += [(key, value)]
    return out


def _cell_kind(cell):
    return cell[0]


def ladder_of(name, role, cells, rungs=None, levels=None, floor=DEFAULT_FLOOR, position=0):
    """The ladder of one eligible column, from its published facts and its cells.

    `cells` lists, for each tabled row in row order, `("value", x)` (a
    reading, an exact fraction), `("level", name)` (a published level),
    `("held",)` (a level of the held-back pool), `("missing",)`,
    `("other",)` or `("labels",)`. Number, date and clock columns pass
    their published `rungs` (keys `p10` ... `p90`, `p25`, `p75`; a date
    or clock its interior rungs on its own ordinal, read here under the
    same keys); label columns (`binary`, `categorical`,
    `long_tail_labels`, `constant`) pass their published `levels` as
    `(name, count)` in published order. A DERIVED column of a carried
    rule (contract 4.6b.7, role `derived` here) passes the bands of the
    ONE level its family `{D | A}` publishes as its `levels`; that level
    is all three of its levels, so RULE W1 reads it as its coarsest.
    """
    label_role = role in ("binary", "categorical", "long_tail_labels", "constant", "derived")
    starting = []
    if label_role:
        for kind in ("missing",):
            if any(_cell_kind(c) == kind for c in cells):
                starting += [kind]
        for level, _ in levels:
            starting += [("level", level)]
        if any(_cell_kind(c) == "held" for c in cells):
            starting += [("level", "held back")]
    else:
        for kind in SPREAD_ORDER:
            if any(_cell_kind(c) == kind for c in cells):
                starting += [kind]
        edges = _number_edges(rungs, NUMBER_L0)
        bounds = [None] + [k for k, _ in edges] + [None]
        for i in range(len(bounds) - 1):
            starting += [("range", bounds[i], bounds[i + 1])]
        values = {k: v for k, v in edges}

    def start_of(cell):
        kind = cell[0]
        if kind in ("missing", "other", "labels"):
            return starting.index(kind)
        if kind == "level":
            return starting.index(("level", cell[1]))
        if kind == "held":
            return starting.index(("level", "held back"))
        x = F(cell[1])
        for i, s in enumerate(starting):
            if isinstance(s, tuple) and s[0] == "range":
                low = values[s[1]] if s[1] is not None else None
                high = values[s[2]] if s[2] is not None else None
                if (low is None or low <= x) and (high is None or x < high):
                    return i
        raise ValueError("a reading lies in no band")

    row_start = [start_of(c) for c in cells]
    counts = [0] * len(starting)
    for s in row_start:
        counts[s] += 1
    groups = [[i] for i in range(len(starting))]
    # A band holding no row is dropped; a value band so dropped joins the
    # band above it (its upper edge stops being an edge), the top one the
    # band below.
    def size(group):
        return sum(counts[i] for i in group)

    def is_value(i):
        return isinstance(starting[i], tuple)

    changed = True
    while changed:
        changed = False
        for at, group in enumerate(groups):
            if size(group) == 0:
                if label_role or not all(is_value(i) for i in group):
                    groups = groups[:at] + groups[at + 1:]
                else:
                    later = [j for j in range(at + 1, len(groups)) if any(is_value(i) for i in groups[j])]
                    earlier = [j for j in range(at) if any(is_value(i) for i in groups[j])]
                    if later:
                        j = later[0]
                        groups[j] = group + groups[j]
                        groups = groups[:at] + groups[at + 1:]
                    elif earlier:
                        j = earlier[-1]
                        groups[j] = groups[j] + group
                        groups = groups[:at] + groups[at + 1:]
                    else:
                        groups = groups[:at] + groups[at + 1:]
                changed = True
                break
    taken = []
    # The merge: while some band holds 1 to f - 1 rows, it joins a
    # neighbour (a number column: the neighbour in band order holding
    # fewer rows, ties to the earlier; a label column: the two smallest
    # bands, `missing` counting as one, ties to the earlier).
    while True:
        small = [at for at, g in enumerate(groups) if 1 <= size(g) <= floor - 1]
        if not small or len(groups) < 2:
            break
        if label_role:
            order = sorted(range(len(groups)), key=lambda at: (size(groups[at]), at))
            a, b = sorted(order[:2])
            smaller = order[0]
        else:
            a = small[0]
            if a == 0:
                b = 1
            elif a == len(groups) - 1:
                b = a - 1
            else:
                b = a - 1 if size(groups[a - 1]) <= size(groups[a + 1]) else a + 1
            smaller = a
            a, b = min(a, b), max(a, b)
        taken += [(groups[smaller], size(groups[smaller]))]
        groups = groups[:a] + [groups[a] + groups[b]] + groups[a + 1:b] + groups[b + 1:]
    l0 = [[starting[i] for i in sorted(g)] for g in groups]
    where = {}
    for at, g in enumerate(groups):
        for i in g:
            where[i] = at
    row_l0 = [where[s] for s in row_start]
    totals = [0] * len(groups)
    for b in row_l0:
        totals[b] += 1
    taken_in = sorted({where[g[0]] for g, _ in taken})
    ordered = [any(isinstance(s, tuple) for s in band) for band in l0]
    if role in ("binary", "constant", "derived"):
        l1 = [[i] for i in range(len(l0))]
        l2 = [[i] for i in range(len(l0))]
    elif label_role:
        l1, l2 = _label_levels(l0, levels)
    else:
        l1 = _number_level(l0, starting, NUMBER_L1)
        l2 = _number_level(l0, starting, NUMBER_L2)
    return Ladder(name, role, l0, totals, l1, l2, row_l0, taken_in, ordered, position)


def _number_level(l0, starting, keys):
    """A coarser level of a number column, read through `L0`.

    Its edges are the keys that are still edges of `L0` (an edge the
    merge removed is removed here too); each band is the run of `L0`
    bands between two of them. A spread band of `L0` holding no value
    band stays a band of its own.
    """
    still = set()
    for band in l0:
        ranges = [s for s in band if isinstance(s, tuple)]
        if ranges:
            still.add(ranges[0][1])
    edges = [k for k in keys if k in still and k is not None]
    out = []
    spread = [[i] for i, band in enumerate(l0) if not any(isinstance(s, tuple) for s in band)]
    out += spread
    current = []
    for i, band in enumerate(l0):
        ranges = [s for s in band if isinstance(s, tuple)]
        if not ranges:
            continue
        lower = ranges[0][1]
        if current and lower in edges:
            out += [current]
            current = []
        current += [i]
    if current:
        out += [current]
    return out


def _label_levels(l0, levels):
    """`L1` and `L2` of a label column, read through `L0`.

    `L1`: the ten commonest published levels by published count (ties to
    the earlier published) each a band, every other level and the pool
    one band; `L2`: the commonest level, every other level one band. An
    `L0` band holds its levels together, so a band joining a level kept
    apart with one pooled goes to the pool; `missing` stays a band of its
    own unless the merge joined it with a level.
    """
    published = [name for name, _ in levels]
    ranked = sorted(range(len(levels)), key=lambda i: (-levels[i][1], i))

    def level_of(top):
        kept = {published[i] for i in ranked[:top]}
        out = []
        rest = []
        for i, band in enumerate(l0):
            names = [s[1] for s in band if isinstance(s, tuple)]
            if not names:
                out += [[i]]
            elif all(n in kept for n in names):
                out += [[i]]
            else:
                rest += [i]
        if rest:
            out += [rest]
        return out

    return level_of(10), level_of(1)


# --- tables (contract 4.6b.5; validation V12.2) --------------------------


def family_table(child_codes, child_count, parents):
    """A family's COMPLETE table over the tabled rows.

    `parents` is a list of `(codes, count)` in listed order. One row for
    each joint cell of the parents (the last parent's band varying
    fastest; one row where there is none), one column for each band of
    the child, every cell written, zeros included.
    """
    shape = [count for _, count in parents]
    rows = 1
    for s in shape:
        rows *= s
    table = [[0] * child_count for _ in range(rows)]
    for r in range(len(child_codes)):
        cell = 0
        for codes, count in parents:
            cell = cell * count + codes[r]
        table[cell][child_codes[r]] += 1
    return table


def pair_table(a_codes, a_count, b_codes, b_count):
    """A pair's table: `a`'s bands by `b`'s, counted over the tabled rows."""
    return family_table(b_codes, b_count, [(a_codes, a_count)])


def score(table):
    """`u = X2 - df` of contract 4.6b.3, an exact fraction (no logarithm)."""
    rows = [sum(r) for r in table]
    columns = [sum(c) for c in zip(*table)] if table else []
    n = sum(rows)
    if n == 0:
        return F(0)
    x2 = F(0)
    for i, r in enumerate(table):
        for j, observed in enumerate(r):
            if rows[i] == 0 or columns[j] == 0:
                continue
            expected = F(rows[i] * columns[j], n)
            x2 += (observed - expected) ** 2 / expected
    used_rows = sum(1 for t in rows if t)
    used_columns = sum(1 for t in columns if t)
    df = max(0, used_rows - 1) * max(0, used_columns - 1)
    return x2 - df


def floor_holds(table, floor=DEFAULT_FLOOR):
    """The floor of contract 4.6b.3: every cell 0 or at least `f`."""
    return all(c == 0 or c >= floor for r in table for c in r)


def dealing_spread(implied, n):
    """V12.2's dealing spread, `s = 1/2 sum sqrt(p (1 - p) / n)`, held exactly.

    Returns `(radicands, low, high)`: each cell's radicand `p (1 - p) /
    n` as an exact fraction, and a certified enclosure `low <= s <= high`
    of whole multiples of `2 ** -60`, each root bounded by integer
    square roots, so nothing here is rounded unseen.
    """
    total = sum(sum(r) for r in implied)
    radicands = []
    low = F(0)
    high = F(0)
    scale = 1 << 60
    for r in implied:
        for c in r:
            p = F(c) / total
            q = p * (1 - p) / n
            radicands += [q]
            lo_int = _isqrt_floor(q * scale * scale)
            hi_int = lo_int if F(lo_int * lo_int) == q * scale * scale else lo_int + 1
            low += F(lo_int, scale)
            high += F(hi_int, scale)
    return radicands, low / 2, high / 2


def _isqrt_floor(q):
    """The greatest whole number whose square is at most the fraction `q`."""
    whole = q.numerator // q.denominator
    root = _isqrt(whole)
    while (root + 1) * (root + 1) <= q:
        root += 1
    return root


def _isqrt(n):
    if n < 0:
        raise ValueError("no root of a negative number")
    if n == 0:
        return 0
    x = 1 << ((n.bit_length() + 1) // 2)
    while True:
        y = (x + n // x) // 2
        if y >= x:
            return x
        x = y


# --- the chain, its tables and its implied joint --------------------------


class Family:
    """One placed family: its child, its parents and the levels of each."""

    def __init__(self, child, level, parents, anchor, table):
        self.child = child
        self.level = level
        self.parents = list(parents)  # [(column, level)] in schema order
        self.anchor = anchor
        self.table = table

    def members(self):
        return [c for c, _ in self.parents] + [self.child]

    def levels(self):
        return [lv for _, lv in self.parents] + [self.level]

    def as_dict(self):
        return {
            "child": self.child,
            "level": "L%d" % self.level,
            "parents": [{"column": c, "level": "L%d" % lv} for c, lv in self.parents],
            "anchor": self.anchor,
            "table": self.table,
        }


def table_of(lads, child, level, parents):
    """A family's complete table over the tabled rows, from each ladder's band codes."""
    lc = lads[child]
    parent_codes = [(lads[c].codes(lv), len(lads[c].bands(lv))) for c, lv in parents]
    return family_table(lc.codes(level), len(lc.bands(level)), parent_codes)


def chain_level(chain, column):
    """A column's chain level: the level of the family it is the child of."""
    for family in chain:
        if family.child == column:
            return family.level
    raise KeyError(column)


def _allowed(family, lads, levels_at):
    """The member tuples at chain levels that lie in a non-zero cell of the family's table."""
    members = family.members()
    flevels = family.levels()
    maps = []
    domains = []
    for column, lv in zip(members, flevels):
        lad = lads[column]
        chain_bands = lad.bands(levels_at[column])
        to_family = lad.coarsen(lv)
        maps += [[to_family[b[0]] for b in chain_bands]]
        domains += [range(len(chain_bands))]
    sizes = [len(lads[c].bands(lv)) for c, lv in zip(members, flevels)]
    out = set()
    for combo in itertools.product(*domains):
        coarse = [maps[i][x] for i, x in enumerate(combo)]
        row = 0
        for i in range(len(coarse) - 1):
            row = row * sizes[i] + coarse[i]
        if family.table[row][coarse[-1]] > 0:
            out.add(combo)
    return members, out


def tree_edges(chain):
    """The junction tree's edges: each family joined to its anchor, and a family with
    parents and no anchor (a derived family `{D | A}` of a carried rule, placed at its
    rule's step before `A`'s own family, contract 4.6b.7) joined to the family each
    parent is the child of, once that family is placed. Each column's families stay
    connected, so the two passes of `support` are exact."""
    child_of = {}
    for i, family in enumerate(chain):
        child_of.setdefault(family.child, i)
    edges = []
    for i, family in enumerate(chain):
        if family.anchor is not None:
            edges += [(i, family.anchor)]
        else:
            for parent, _ in family.parents:
                j = child_of.get(parent)
                if j is not None and j != i:
                    edges += [(i, j)]
    return edges


def _tree_order(count, edges):
    """Each family's place in a walk of the tree from its component's first family:
    the order, and each family's neighbour toward that first family."""
    neighbours = {i: [] for i in range(count)}
    for a, b in edges:
        neighbours[a] += [b]
        neighbours[b] += [a]
    order = []
    toward = {}
    for start in range(count):
        if start in toward:
            continue
        toward[start] = None
        queue = [start]
        at = 0
        while at < len(queue):
            u = queue[at]
            at += 1
            order += [u]
            for v in sorted(neighbours[u]):
                if v not in toward:
                    toward[v] = u
                    queue += [v]
    return order, toward


def support(chain, lads, fixed=None):
    """The chain-level band combinations no published nought rules out, column by column.

    Families form a junction tree (`tree_edges`: each family joined to
    its anchor, a derived family to its parent's own family), so passing
    true and false up the tree and back down leaves, in each family,
    exactly the member tuples some full assignment extends (contract
    4.6b.3's RULE W1, 4.6b.9 (c)). `fixed` restricts columns to sets of
    chain-level bands. Returns each column's admitted bands.
    """
    fixed = fixed or {}
    levels_at = {f.child: f.level for f in chain}
    allowed = []
    for family in chain:
        members, out = _allowed(family, lads, levels_at)
        out = {t for t in out if all(t[i] in fixed[c] for i, c in enumerate(members) if c in fixed)}
        allowed += [(members, out)]
    order, toward = _tree_order(len(chain), tree_edges(chain))

    def narrowed(target, source):
        tm, tout = allowed[target]
        sm, sout = allowed[source]
        sep = [c for c in tm if c in sm]
        message = {tuple(t[sm.index(c)] for c in sep) for t in sout}
        return (tm, {t for t in tout if tuple(t[tm.index(c)] for c in sep) in message})

    # Upward: each family's allowed tuples narrowed by the messages of the families beyond it.
    for i in reversed(order):
        if toward[i] is not None:
            allowed[toward[i]] = narrowed(toward[i], i)
    # Downward: each family narrowed by the family toward its component's first.
    for i in order:
        if toward[i] is not None:
            allowed[i] = narrowed(i, toward[i])
    roots_empty = any(not out for members, out in allowed)
    admitted = {}
    for members, out in allowed:
        for i, c in enumerate(members):
            seen = {t[i] for t in out}
            admitted[c] = admitted[c] & seen if c in admitted else seen
    if roots_empty:
        return {c: set() for c in admitted}
    return admitted


def w1_holds(chain, lads, groups):
    """RULE W1 checked in full (contract 4.6b.3).

    `groups` lists each placed column's own-fact groups of 1 to `f - 1`
    rows as `(column, L0 band holding it)`. For every such group, and
    every OTHER placed column `m`, the band of the column's chain level
    holding the group must admit at least two bands of `m`'s coarsest
    level. Returns `(holds, failures)`.
    """
    levels_at = {f.child: f.level for f in chain}
    failures = []
    for column, l0_band in groups:
        if column not in levels_at:
            continue
        lad = lads[column]
        beta = lad.coarsen(levels_at[column])[l0_band]
        admitted = support(chain, lads, {column: {beta}})
        for other in sorted(levels_at):
            if other == column:
                continue
            olad = lads[other]
            chain_bands = olad.bands(levels_at[other])
            to_l2 = olad.coarsen(2)
            coarsest = {to_l2[chain_bands[b][0]] for b in admitted.get(other, set())}
            if len(coarsest) < 2:
                failures += [(column, l0_band, other, sorted(coarsest))]
    return not failures, failures


def cell_bound(chain, lads, cell, n):
    """`b(x)` of contract 4.6b.9 (a): the least published count holding the full joint cell `x`.

    `cell` maps each column to its `L0` band. The counts read are every
    family cell whose bands hold `x`'s bands, every `L0` total of `x`'s
    bands, and `n`.
    """
    best = n
    for column, band in cell.items():
        best = min(best, lads[column].totals[band])
    for family in chain:
        members = family.members()
        if not all(c in cell for c in members):
            continue
        coarse = [lads[c].coarsen(lv)[cell[c]] for c, lv in zip(members, family.levels())]
        sizes = [len(lads[c].bands(lv)) for c, lv in zip(members, family.levels())]
        row = 0
        for i in range(len(coarse) - 1):
            row = row * sizes[i] + coarse[i]
        best = min(best, family.table[row][coarse[-1]])
    return best


# --- RULES W3 and NE: which levels are offered (contract 4.6b.3) ----------


def _marginal(table, members, levels, lads, keep, keep_levels):
    """A family's table summed to some of its members, each at a level no finer."""
    sizes = [len(lads[c].bands(lv)) for c, lv in zip(members, levels)]
    to = []
    for c, lv, klv in zip(members, levels, [keep_levels.get(c) for c in members]):
        if c in keep:
            full = lads[c].coarsen(klv)
            here = lads[c].bands(lv)
            to += [[full[b[0]] for b in here]]
        else:
            to += [None]
    out = {}
    parent_sizes = sizes[:-1]
    for row, cells in enumerate(table):
        rest = row
        coords = []
        for s in reversed(parent_sizes):
            coords += [rest % s]
            rest //= s
        coords = list(reversed(coords))
        for j, count in enumerate(cells):
            full_coords = coords + [j]
            key = tuple(to[i][full_coords[i]] for i in range(len(members)) if to[i] is not None)
            out[key] = out.get(key, 0) + count
    return out


def offered_levels(lads, child, parents, anchor_family, n, floor=DEFAULT_FLOOR):
    """The levels RULES W3 and NE end on for a candidate, or None where it is not offered.

    `parents` lists `(column, level in the anchor)`; a root pair passes
    one parent at `L0` and `anchor_family` None. Members are read in
    schema order for ties, the child last among equals only by its own
    place (the caller passes `order`). Returns a dict column -> level.
    """
    members = [c for c, _ in parents] + [child]
    level = {c: lv for c, lv in parents}
    level[child] = 0
    order = sorted(members, key=lambda c: lads[c].position)

    def totals(c):
        return lads[c].band_totals(level[c])

    def count(c):
        return len(lads[c].bands(level[c]))

    def coarsen_one(candidates):
        movable = [c for c in candidates if level[c] < 2]
        if not movable:
            return False
        pick = min(movable, key=lambda c: (min(totals(c)), order.index(c)))
        level[pick] += 1
        return True

    while True:
        failing = []
        for c in members:
            others = 1
            for o in members:
                if o != c:
                    others *= count(o)
            if min(totals(c)) < floor * others:
                failing += [c]
        if not failing:
            break
        if not coarsen_one(failing):
            return None
    while True:
        child_totals = totals(child)
        if anchor_family is None:
            parent_cells = {(b,): t for b, t in enumerate(totals(parents[0][0]))}
        else:
            keep = [c for c, _ in parents]
            parent_cells = _marginal(
                anchor_family.table, anchor_family.members(), anchor_family.levels(), lads, keep, level
            )
        bad = False
        for cell_total in parent_cells.values():
            for t in child_totals:
                if t * cell_total < (floor + 1) * n:
                    bad = True
        if not bad:
            break
        if not coarsen_one(members):
            return None
    return dict(level)


def variants(levels):
    """Every combination with each member at its offered level or coarser."""
    names = sorted(levels)
    out = []
    for combo in itertools.product(*[range(levels[c], 3) for c in names]):
        out += [dict(zip(names, combo))]
    return out


# --- the search: options, eligibility, scores and the draw ---------------


class Setting:
    """What a description's search runs under, all of it published or a constant.

    `own_groups` lists each eligible column's own-fact groups of 1 to
    `f - 1` rows as `(column, L0 band)` (the producer reads them from the
    column's published block: `mode_count`, `n_zero`, a heap, a bin of
    one reading); the sub-bands an `L0` merge took in are added from each
    ladder's `taken_in` at every check. `we` is None or
    `{"blank": {column: L0 band holding its blank cells, or None}, "z":
    Z, "p": P}` (RULE WE). `rule_pairs` and `te_pairs` are column pairs
    (sets); `seeds` the triple screen's seeds, each a tuple of columns.
    """

    def __init__(self, name, key, floor=DEFAULT_FLOOR, k_max=K_MAX, tau=F(2), w_rule=F(1, 20),
                 w_te=F(1), w_seed=F(1, 20), rule_pairs=(), te_pairs=(), seeds=(), own_groups=(), we=None):
        self.name = name
        self.key = key
        self.floor = floor
        self.k_max = k_max
        self.tau = F(tau)
        self.w_rule = F(w_rule)
        self.w_te = F(w_te)
        self.w_seed = F(w_seed)
        self.rule_pairs = [frozenset(p) for p in rule_pairs]
        self.te_pairs = [frozenset(p) for p in te_pairs]
        self.seeds = [tuple(s) for s in seeds]
        self.own_groups = list(own_groups)
        self.we = we


def raise_of(setting, n, child, parents):
    """The weight raises of contract 4.6b.3, on the score's own scale (`n` times a fraction)."""
    up = F(0)
    for p in parents:
        if frozenset((child, p)) in setting.rule_pairs:
            up += setting.w_rule * n
            break
    for p in parents:
        if frozenset((child, p)) in setting.te_pairs:
            up += setting.w_te * n
            break
    for seed in setting.seeds:
        if child not in seed:
            continue
        others = [c for c in seed if c != child]
        if len(seed) == 2:
            if others[0] in parents:
                up += setting.w_seed * n
        else:
            up += setting.w_seed * n * sum(1 for c in others if c in parents)
    return up


def _families_of(option, lads):
    """The families an option places, in chain order (the root pair places two)."""
    kind = option["kind"]
    if kind == "root":
        a, b = option["parent"], option["child"]
        la, lb = option["levels"][a], option["levels"][b]
        first = Family(a, la, [], None, [lads[a].band_totals(la)])
        second = Family(b, lb, [(a, la)], None, table_of(lads, b, lb, [(a, la)]))
        return [first, second]
    if kind == "none_for":
        d = option["child"]
        return [Family(d, 0, [], None, [lads[d].band_totals(0)])]
    if kind == "family":
        d = option["child"]
        parents = [(p, option["levels"][p]) for p in option["parents"]]
        fam = Family(d, option["levels"][d], parents, option["anchor"], table_of(lads, d, option["levels"][d], parents))
        return [fam]
    return []


def _placed(chain, option, lads):
    out = list(chain)
    for fam in _families_of(option, lads):
        if option["kind"] == "root" and fam.parents:
            fam.anchor = len(out) - 1
        out += [fam]
    return out


def we_holds(setting, chain, lads, n):
    """RULE WE with the option placed: `b(x0) <= Z + P`, or no cell `x0`."""
    if setting.we is None:
        return True
    blank = setting.we["blank"]
    if any(blank.get(c) is None for c in lads):
        return True
    x0 = {c: blank[c] for c in lads}
    return cell_bound(chain, lads, x0, n) <= setting.we["z"] + setting.we["p"]


def eligible(setting, chain, option, lads, n, w1=None):
    """Whether an offered option is ELIGIBLE (contract 4.6b.3): the floor, RULE W1, RULE WE.

    `w1` replaces RULE W1 (the mutants pass the vacuous clause or the
    design's own clause). Returns `(eligible, why)`.
    """
    if option["kind"] in ("none", "none_for"):
        return True, "no family is always eligible"
    families = _families_of(option, lads)
    table = families[-1].table
    if not floor_holds(table, setting.floor):
        return False, "floor"
    placed = _placed(chain, option, lads)
    groups = list(setting.own_groups)
    for column in sorted(lads):
        groups += [(column, band) for band in lads[column].taken_in if (column, band) not in groups]
    check = w1 or (lambda ch: w1_holds(ch, lads, groups)[0])
    if not check(placed):
        return False, "W1"
    if not we_holds(setting, placed, lads, n):
        return False, "WE"
    return True, "eligible"


def _level_key(levels, lads):
    return tuple(levels[c] for c in sorted(levels, key=lambda c: lads[c].position))


def root_options(setting, lads, n):
    """The root step's options in option order, with their raised scores."""
    names = sorted(lads, key=lambda c: lads[c].position)
    out = [({"kind": "none"}, F(0))]
    for b in names:
        for a in names:
            if lads[a].position >= lads[b].position:
                continue
            levels = offered_levels(lads, b, [(a, 0)], None, n, setting.floor)
            if levels is None:
                continue
            for variant in sorted(variants(levels), key=lambda v: _level_key(v, lads)):
                option = {"kind": "root", "parent": a, "child": b, "levels": variant}
                table = table_of(lads, b, variant[b], [(a, variant[a])])
                out += [(option, score(table) + raise_of(setting, n, b, [a]))]
    return out


def step_options(setting, lads, chain, n):
    """A later step's options in option order, with their raised scores."""
    names = sorted(lads, key=lambda c: lads[c].position)
    placed_columns = set()
    for fam in chain:
        placed_columns.update(fam.members())
    out = []
    for d in names:
        if d in placed_columns:
            continue
        out += [({"kind": "none_for", "child": d}, F(0))]
        candidates = {}
        for at, fam in enumerate(chain):
            members = sorted(fam.members(), key=lambda c: lads[c].position)
            for size in range(1, setting.k_max + 1):
                for parents in itertools.combinations(members, size):
                    if parents not in candidates:
                        candidates[parents] = at
        for parents, anchor in sorted(candidates.items(), key=lambda kv: (kv[1], [lads[c].position for c in kv[0]])):
            fam = chain[anchor]
            at_anchor = dict(zip(fam.members(), fam.levels()))
            levels = offered_levels(lads, d, [(p, at_anchor[p]) for p in parents], fam, n, setting.floor)
            if levels is None:
                continue
            for variant in sorted(variants(levels), key=lambda v: _level_key(v, lads)):
                if any(variant[p] < at_anchor[p] for p in parents):
                    continue
                option = {"kind": "family", "child": d, "parents": list(parents), "anchor": anchor, "levels": variant}
                pl = [(p, variant[p]) for p in parents]
                table = table_of(lads, d, variant[d], pl)
                out += [(option, score(table) + raise_of(setting, n, d, list(parents)))]
    return out


def search(setting, lads, n, w1=None):
    """The whole search of contract 4.6b.3 and 4.6b.4 for one key: the chain it places.

    Returns `(chain, steps)`: `steps` lists, for each step, its kind, its
    eligible options with their raised scores, the word, how the choice
    fell and the option placed.
    """
    names = sorted(lads, key=lambda c: lads[c].position)
    chain = []
    steps = []
    index = 0
    options = root_options(setting, lads, n)
    while True:
        kept = []
        for option, v in options:
            ok, _ = eligible(setting, chain, option, lads, n, w1)
            if ok:
                kept += [(option, v)]
        w = word(setting.key, setting.name, "place", index, names)
        place, how, weights = choose(w, [v for _, v in kept], setting.tau)
        option = kept[place][0]
        steps += [{"index": index, "eligible": kept, "word": w.hex(), "how": how, "placed": option,
                   "weights": [b64_hex(x) for x in weights]}]
        if option["kind"] == "none":
            return [], steps
        chain = _placed(chain, option, lads)
        placed_columns = set()
        for fam in chain:
            placed_columns.update(fam.members())
        if placed_columns >= set(names):
            return chain, steps
        index += 1
        options = step_options(setting, lads, chain, n)


# --- the walk (method G16.2) -----------------------------------------------


def hidden_score(words3):
    """G16.8's hidden score: the twelve 16-bit pieces of three words summed, `(S - 393210) / 65536`."""
    total = 0
    for w in words3:
        for shift in (0, 16, 32, 48):
            total += (w >> shift) & 0xFFFF
    return F(total - 393210, 65536)


def value_code(x, lo, hi):
    """Contract 4.6b.6's value code: `min(255, max(0, floor(256 (x - lo) / (hi - lo))))`, exact."""
    if lo == hi:
        return 0
    q = F(256) * (F(x) - F(lo)) / (F(hi) - F(lo))
    return min(255, max(0, q.numerator // q.denominator))


def published_decimal(text):
    """The binary64 nearest a number written to four decimals (a published `beta` or `sigma`)."""
    return b64(F(text))


def _spread_positions(g, t):
    """G16.2 step 3: the `q`-th of `t` rows stands at `floor((2 q + 1) g / (2 t))`."""
    return [((2 * q + 1) * g) // (2 * t) for q in range(t)]


def walk_rows(chain, lads, cells, words, slopes=None, codes=None, targets=None,
              sort_by_row=False, spread_after=False, trace=None):
    """Method G16.2 on given words: each arranged row's cell of each eligible column.

    `lads` maps each column to its PUBLISHED ladder (band structure and totals);
    `cells[column]` lists, for each `L0` band in band order, the twin's
    cells of that band as `(text, reading)` in the interface's order
    (`reading` None on a cell holding no reading of the band's order);
    `words[f]` lists three words for each arranged row of family `f`;
    `slopes[f]` is None or `([(parent, beta text)], sigma text)`;
    `codes[column]` is `(lo, hi)` for a FINE column's value code;
    `targets[f]` replaces family `f`'s published table (a moved target).
    The two keyword mutants are G16.12's: rows sorted by row number
    instead of `L`, and the spread bands placed after the ordered ones.
    `trace`, where a dict, receives for each family index its rows'
    latent orders `L` and each slope parent's cell means (exact
    binary64 values as fractions).
    Returns `{column: [cell index of each row]}`, the cell lists, and each
    family's table as dealt.
    """
    slopes = slopes or {}
    codes = codes or {}
    targets = targets or {}
    n = len(words[0])
    band_code = {}
    reading = {}
    index = {}
    cell_list = {}
    dealt = []
    for fi, fam in enumerate(chain):
        child = fam.child
        lad = lads[child]
        level = fam.level
        bands = lad.bands(level)
        sizes = [len(lads[p].bands(lv)) for p, lv in fam.parents]
        to_family = []
        for p, lv in fam.parents:
            chain_to = {b: lads[p].coarsen(lv)[members[0]] for b, members in enumerate(lads[p].bands(_chain_level_of(chain, p)))}
            to_family += [chain_to]
        cell_of = [0] * n
        for r in range(n):
            cell = 0
            for (p, lv), size, mapping in zip(fam.parents, sizes, to_family):
                cell = cell * size + mapping[band_code[p][r]]
            cell_of[r] = cell
        target = targets.get(fi, fam.table)
        z = [hidden_score(words[fi][r]) for r in range(n)]
        latent = list(z)
        means = {}
        if fi in slopes and slopes[fi] is not None and lad.ordered and any(lad.ordered):
            parent_terms, sigma_text = slopes[fi]
            sigma = published_decimal(sigma_text)
            for p, beta_text in parent_terms:
                sums = {}
                for r in range(n):
                    if reading[p][r] is None:
                        continue
                    s, k = sums.get(cell_of[r], (0, 0))
                    sums[cell_of[r]] = (s + value_code(reading[p][r], *codes[p]), k + 1)
                means[p] = {c: b64(F(s, k)) for c, (s, k) in sums.items()}
            for r in range(n):
                acc = None
                for p, beta_text in parent_terms:
                    beta = published_decimal(beta_text)
                    if reading[p][r] is None or cell_of[r] not in means[p]:
                        term = F(0)
                    else:
                        code = value_code(reading[p][r], *codes[p])
                        term = b64_mul(beta, b64_sub(code, means[p][cell_of[r]]))
                    acc = term if acc is None else b64_add(acc, term)
                latent[r] = b64_add(acc, b64_mul(sigma, z[r]))
        if trace is not None:
            trace[fi] = {"latent": latent, "means": means}
        sort_key = (lambda r: r) if sort_by_row else (lambda r: (latent[r], r))
        band_of = [None] * n
        ordered_band = [any(isinstance(s, tuple) for b in members for s in lad.l0[b]) for members in bands]
        if lad.role in ("binary", "categorical", "long_tail_labels", "constant"):
            ordered_band = [not all(s == "missing" for b in members for s in lad.l0[b]) for members in bands]
        for cell in range(len(target)):
            rows = sorted([r for r in range(n) if cell_of[r] == cell], key=sort_key)
            free = list(rows)
            spread = [b for b in range(len(bands)) if not ordered_band[b] and target[cell][b] > 0]
            ordered = [b for b in range(len(bands)) if ordered_band[b]]

            def place_spread(free):
                for b in spread:
                    t = target[cell][b]
                    picked = set(_spread_positions(len(free), t))
                    for at in sorted(picked):
                        band_of[free[at]] = b
                    free = [r for at, r in enumerate(free) if at not in picked]
                return free

            if not spread_after:
                free = place_spread(free)
            at = 0
            for b in ordered:
                t = target[cell][b]
                for r in free[at:at + t]:
                    band_of[r] = b
                at += t
            if spread_after:
                rest = free[at:]
                for b in spread:
                    t = target[cell][b]
                    for r in rest[:t]:
                        band_of[r] = b
                    rest = rest[t:]
        table = [[0] * len(bands) for _ in range(len(target))]
        for r in range(n):
            table[cell_of[r]][band_of[r]] += 1
        dealt += [table]
        # Step 4: the cells inside their bands.
        listing = []
        idx = [None] * n
        read = [None] * n
        for b, members in enumerate(bands):
            rows = sorted([r for r in range(n) if band_of[r] == b], key=sort_key)
            with_reading = []
            without = []
            for l0 in members:
                for text, value in cells[child][l0]:
                    if value is None:
                        without += [(text, value)]
                    else:
                        with_reading += [(text, value)]
            with_reading = [c for _, c in sorted(enumerate(with_reading), key=lambda ic: (ic[1][1], ic[0]))]
            start = len(listing)
            listing += with_reading + without
            g = len(rows)
            a = len(without)
            spread_at = set(_spread_positions(g, a)) if a else set()
            k_read = 0
            k_without = 0
            for pos, r in enumerate(rows):
                if pos in spread_at:
                    idx[r] = start + len(with_reading) + k_without
                    k_without += 1
                else:
                    idx[r] = start + k_read
                    k_read += 1
                read[r] = listing[idx[r]][1]
        band_code[child] = band_of
        reading[child] = read
        index[child] = idx
        cell_list[child] = listing
    return index, cell_list, dealt


def _chain_level_of(chain, column):
    for fam in chain:
        if fam.child == column:
            return fam.level
    raise KeyError(column)


# --- the moved target (method G16.6) -----------------------------------------


def _tables_with(rows, columns):
    """Every table of whole numbers with the given row and column totals."""
    r, c = len(rows), len(columns)

    def fill(i, j, cur, row_left, col_left):
        if i == r:
            if all(x == 0 for x in col_left):
                yield [list(x) for x in cur]
            return
        if j == c - 1:
            v = row_left[i]
            if v <= col_left[j]:
                cur[i][j] = v
                col_left[j] -= v
                yield from fill(i + 1, 0, cur, row_left, col_left)
                col_left[j] += v
            return
        for v in range(min(row_left[i], col_left[j]) + 1):
            cur[i][j] = v
            row_left[i] -= v
            col_left[j] -= v
            yield from fill(i, j + 1, cur, row_left, col_left)
            row_left[i] += v
            col_left[j] += v

    if sum(rows) != sum(columns):
        return []
    return list(fill(0, 0, [[0] * c for _ in range(r)], list(rows), list(columns)))


def moved_target(published, rows, columns):
    """G16.6's moved table, by enumeration: fewest units in published noughts, then the
    smallest total distance, then the smallest sum of squares, then the greatest in
    row-major order. Returns `(table, units_in_noughts)` with each `(row, column, units)`.
    """
    best = None
    best_key = None
    for table in _tables_with(rows, columns):
        noughts = sum(table[i][j] for i in range(len(rows)) for j in range(len(columns)) if published[i][j] == 0)
        distance = sum(abs(table[i][j] - published[i][j]) for i in range(len(rows)) for j in range(len(columns)))
        squares = sum((table[i][j] - published[i][j]) ** 2 for i in range(len(rows)) for j in range(len(columns)))
        flat = [-x for row in table for x in row]
        key = (noughts, distance, squares, flat)
        if best_key is None or key < best_key:
            best, best_key = table, key
    named = [(i, j, best[i][j]) for i in range(len(rows)) for j in range(len(columns)) if published[i][j] == 0 and best[i][j] > 0]
    return best, named


def needs_move(published, parent_counts, child_totals):
    """G16.0's test: a family's target is its published table only where the twin's parent
    cells hold the table's row totals and the child's band totals its column totals."""
    rows = [sum(r) for r in published]
    columns = [sum(c) for c in zip(*published)]
    return rows != list(parent_counts) or columns != list(child_totals)


# --- a carried order rule (method G16.2 step 5) -------------------------------


def computed_column(a_readings, d_readings):
    """`B` written as `A + D` where both hold a reading, absent where either does not."""
    out = []
    for a, d in zip(a_readings, d_readings):
        out += [None if a is None or d is None else F(a) + F(d)]
    return out
