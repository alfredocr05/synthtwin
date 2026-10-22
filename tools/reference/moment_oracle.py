"""The exact route of contract 4.6d.4, decided in whole numbers (lane CHo).

WHAT IT DECIDES. For a region `R` of contract 4.6d.3 under an option
`o`, the joint space `Sigma(R, o)` of 4.6d.4 is a set of POINTS: one
whole number `n(g) >= 0` for each GROUP `g = (lambda, alpha)`, a base
cell and one atom of every region column, meeting a system of
whole-number equations and ranges. The node tables and the `L0` totals
are point condition (2); each column's own facts, read as counts of its
atoms, are (3); every number the option publishes, a sum of whole-number
coefficients (a code, a square, a product, a correlation's `a^i b^j`)
times the counts, is (4). This module decides, in Python integers only,
the witness's three clauses:

- (a) `V-`: each group whose atom vector holds no small atom, and which
  no point lifts to `f` rows;
- (b) whether some point holds 0 rows on every group of `V-`;
- (c) for every small atom `G` and every group `g` holding `G` that SOME
  point makes non-empty, whether some point zero on `V-` puts all of
  `G`'s rows into `g`.

THE ROUTE. One layered dynamic programme over the groups in a fixed
order. A STATE after group `k` is the tuple of partial sums of the
constraints still OPEN there (holding a group at or before `k` and one
after it). The forward pass keeps every state some assignment of the
first groups reaches without leaving any constraint's window; the
backward pass keeps those from which the remaining groups can close
every constraint, and reads off, for every group, the largest value any
point gives it. A claim that NO point exists (that a group lies in
`V-`; that (b) or (c) fails) is then an exhaustive statement about a
finite set of states, made in integer steps, which is what contract
4.6d.4 calls the exact route; a claim that a point EXISTS is a path
through the layers, and `point_through` exhibits one, re-checked against
every constraint in whole numbers.

THE CLASS (`CLASS_NAME`), decided before any search, on published
sizes alone (each group's largest count, each constraint's coefficients
and its published total: published cell counts, codes and published
sums, so inventory class (b)). An instance lies inside where (1) its
groups, counted from the region's sizes before any group is listed,
number at most `GROUPS_MAX`; (2) the bound `class_bounds` reads on the
transitions every pass of `decide` can make together is at most
`NODES_MAX`; (2b) the bound it reads on the whole numbers those passes
write and read (each transition's new state, one entry for each
constraint open after its group, and each state's checks, one for each
constraint reading the next group) is at most `ENTRIES_MAX`, which
bounds the time a transition takes and the memory a state holds, since
both grow with the open constraints; and (3) no node of the region
publishes a slope (point condition (5) is not linear, so the space this
module lists would hold more than `Sigma(R, o)`). Outside, `decide`
returns "outside" without one transition, and the option it would
publish is not eligible (contract 4.6d.3 (ii)). Inside, every pass stays
under both bounds, so the route always finishes within its budget, and
the verdict is the predicate's own value: a function of the published
facts.

WHAT IT NEVER DOES. No float decides anything here: every division is a
floor or a ceiling of whole numbers or an exact fraction, and the
module holds no float literal (the test file scans it). No solver, no
numpy. It reads no table: an instance is built from published facts.

Usage as a library: `build_instance(spec)`, then `decide(instance)`.
"""

import bisect
import fractions
import itertools
import math

F = fractions.Fraction

CLASS_NAME = "cho1"

# The node budget: the largest number of transitions (a state and one
# value of the next group) the class lets every pass of one decision
# make together. A transition's cost grows with the constraints open
# after its group, so the transitions alone bound neither the time nor
# the memory (lane CHo's skeptic, 2026-10-21: 20 binary groups under 30
# open constraints, inside a bound on transitions alone, took 36.65
# seconds and 1.31 GB); ENTRIES_MAX bounds both. The time and the peak
# the two caps admit are MEASURED at the widest instances they admit
# (plan P4-D421, its repair of 2026-10-22).
NODES_MAX = 10_000_000

# The entry budget: the whole numbers every pass of one decision writes
# into new states and reads in its checks, together.
ENTRIES_MAX = 40_000_000

# A first test on sizes alone, before any instance is built: a region
# whose groups (base cells times atom vectors) exceed this count is
# outside the class without being listed.
GROUPS_MAX = 50_000

DEFAULT_FLOOR = 11

# The keys a region's spec may hold (`build_instance`); any other is refused.
SPEC_KEYS = ("floor", "cells", "atoms", "margins", "facts", "sums", "slopes")


class BudgetSpent(Exception):
    """A pass reached its node budget (never inside the class)."""


class Instance:
    """The joint space of one region under one option, as whole numbers.

    `keys` names each group (a base cell and an atom vector), in the
    route's fixed order. `upper[k]` is the largest count group `k` can
    hold (a published count containing it). `constraints` lists
    `(terms, lo, hi)`: `terms` a tuple of `(group, coefficient)` pairs,
    whole numbers, and the constraint reads `lo <= sum <= hi` (an
    equation where they are equal). `small_atoms` lists `(name, groups)`
    for each small atom: the groups holding it. `holds_small` is every
    group whose atom vector holds a small atom (clause (a) leaves them
    out of `V-`).
    """

    def __init__(self, keys, upper, constraints, small_atoms=(), floor=DEFAULT_FLOOR, slopes=(), counted=None):
        self.keys = list(keys)
        # The groups counted from the region's sizes: a region past
        # GROUPS_MAX is built with no group listed (`build_instance`).
        self.counted = len(self.keys) if counted is None else int(counted)
        # The nodes of the region publishing a slope (rule (3)).
        self.slopes = tuple(slopes)
        self.upper = [int(u) for u in upper]
        self.original = []
        for terms, lo, hi in constraints:
            merged = {}
            for group, coefficient in terms:
                merged[group] = merged.get(group, 0) + int(coefficient)
            kept = tuple(sorted((g, c) for g, c in merged.items() if c != 0))
            self.original += [(kept, int(lo), int(hi))]
        self.constraints = presolve(self.original)
        self.small_atoms = [(name, tuple(sorted(groups))) for name, groups in small_atoms]
        holding = set()
        for _, groups in self.small_atoms:
            holding.update(groups)
        self.holds_small = frozenset(holding)
        self.floor = int(floor)
        if len(self.upper) != len(self.keys):
            raise ValueError("one upper bound is owed for each group")


def presolve(constraints):
    """The same point set, written with the smallest coefficients.

    Two exact moves, each keeping every point and adding none. (1) Where
    an EQUATION with every coefficient 1 counts exactly the groups a
    constraint reads (a cell's count beside its code sum), the constraint
    is shifted by its least coefficient times that count, so a sum of
    codes 100 to 105 over 40 rows reads as a sum of codes 0 to 5: every
    point meets one exactly where it meets the other. (2) A constraint
    whose coefficients share a divisor `d` is divided by it, its window
    read on whole multiples of `d`. Terms whose coefficient becomes
    nought are dropped. The class bound and every pass read the result.
    """
    counts = {}
    for terms, lo, hi in constraints:
        if terms and lo == hi and all(c == 1 for _, c in terms):
            counts[frozenset(g for g, _ in terms)] = lo
    out = []
    for terms, lo, hi in constraints:
        key = frozenset(g for g, _ in terms)
        if key in counts and terms and not all(c == 1 for _, c in terms):
            least = min(c for _, c in terms)
            terms = tuple((g, c - least) for g, c in terms)
            lo -= least * counts[key]
            hi -= least * counts[key]
        divisor = 0
        for _, c in terms:
            divisor = math.gcd(divisor, abs(c))
        if divisor > 1:
            terms = tuple((g, c // divisor) for g, c in terms)
            lo = _ceil_div(lo, divisor)
            hi = _floor_div(hi, divisor)
        terms = tuple((g, c) for g, c in terms if c != 0)
        out += [(terms, lo, hi)]
    return out


def _ceil_div(a, b):
    """The least whole number at least a / b, for b above nought."""
    return -((-a) // b)


def _floor_div(a, b):
    """The greatest whole number at most a / b, for b above nought."""
    return a // b


def _layout(instance, upper):
    """The constraints open after each group, and each group's checks.

    Returns `(opened, plans, empty_ok)`: `opened[k]` the sorted list of
    constraints open after group `k`; `plans[k]` the transition plan of
    group `k`; `empty_ok` False where a constraint holding no group asks
    for a total its window does not hold.
    """
    count = len(upper)
    first = []
    last = []
    empty_ok = True
    by_group = [[] for _ in range(count)]
    for index, (terms, lo, hi) in enumerate(instance.constraints):
        if not terms:
            first += [None]
            last += [None]
            if not lo <= 0 <= hi:
                empty_ok = False
            continue
        groups = [g for g, _ in terms]
        first += [min(groups)]
        last += [max(groups)]
        for g, c in terms:
            by_group[g] += [(index, c)]
    # The window a constraint's partial sum must keep after group k:
    # [lo - (most the later groups can add), hi - (least they can add)].
    remaining = {}
    for index, (terms, lo, hi) in enumerate(instance.constraints):
        low_rest = 0
        high_rest = 0
        for g, c in sorted(terms, reverse=True):
            remaining[(index, g)] = (lo - high_rest, hi - low_rest)
            low_rest += min(0, c * upper[g])
            high_rest += max(0, c * upper[g])
    opened = []
    current = set()
    for k in range(count):
        for index, _ in by_group[k]:
            if first[index] == k:
                current.add(index)
        for index, _ in by_group[k]:
            if last[index] == k:
                current.discard(index)
        opened += [sorted(current)]
    plans = []
    before = []
    for k in range(count):
        after = opened[k]
        where_before = {index: at for at, index in enumerate(before)}
        touched = {index: c for index, c in by_group[k]}
        checks = []
        for index, c in by_group[k]:
            low, high = remaining[(index, k)]
            checks += [(where_before.get(index, -1), c, low, high)]
        build = []
        for index in after:
            build += [(where_before.get(index, -1), touched.get(index, 0))]
        plans += [(tuple(checks), tuple(build))]
        before = after
    return opened, plans, empty_ok


def _values(state, checks, top):
    """The values of the next group a state can take, as a range."""
    low = 0
    high = top
    for at, c, window_low, window_high in checks:
        partial = state[at] if at >= 0 else 0
        if c > 0:
            low = max(low, _ceil_div(window_low - partial, c))
            high = min(high, _floor_div(window_high - partial, c))
        else:
            low = max(low, _ceil_div(partial - window_high, -c))
            high = min(high, _floor_div(partial - window_low, -c))
        if high < low:
            return range(0)
    return range(low, high + 1)


def _step(state, build, value):
    out = []
    for at, c in build:
        partial = state[at] if at >= 0 else 0
        out += [partial + c * value]
    return tuple(out)


def _spend(box, transitions, entries):
    box[0] -= transitions
    box[1] -= entries
    if box[0] < 0 or box[1] < 0:
        raise BudgetSpent("the node budget was spent")


def _budget():
    """A fresh budget: transitions left, entries left."""
    return [NODES_MAX, ENTRIES_MAX]


def _forward(instance, upper, box):
    """Every layer of states the first groups reach, or None if a layer empties."""
    opened, plans, empty_ok = _layout(instance, upper)
    if not empty_ok:
        return None, plans
    layers = [{()}]
    for k, (checks, build) in enumerate(plans):
        nxt = set()
        spent = 0
        for state in layers[-1]:
            span = _values(state, checks, upper[k])
            spent += len(span)
            for value in span:
                nxt.add(_step(state, build, value))
        _spend(box, spent, len(layers[-1]) * len(checks) + spent * len(build))
        if not nxt:
            return None, plans
        layers += [nxt]
    return layers, plans


def _solve(instance, upper, box):
    """The largest value each group takes in some point, or None where no point exists."""
    layers, plans = _forward(instance, upper, box)
    if layers is None:
        return None
    good = layers[-1]
    largest = [0] * len(plans)
    for k in range(len(plans) - 1, -1, -1):
        checks, build = plans[k]
        keep = set()
        best = -1
        spent = 0
        for state in layers[k]:
            span = _values(state, checks, upper[k])
            spent += len(span)
            for value in span:
                if _step(state, build, value) in good:
                    keep.add(state)
                    if value > best:
                        best = value
        _spend(box, spent, len(layers[k]) * len(checks) + spent * len(build))
        largest[k] = best
        good = keep
    return largest


def feasible_values(instance, upper=None, box=None):
    """Every value each group takes in some point (a set per group), or None where no point exists.

    The same two passes as `_solve`, keeping each value a transition
    into a completing state uses; the mutants of the test file read it.
    """
    upper = list(instance.upper if upper is None else upper)
    box = box if box is not None else _budget()
    layers, plans = _forward(instance, upper, box)
    if layers is None:
        return None
    good = layers[-1]
    values = [set() for _ in plans]
    for k in range(len(plans) - 1, -1, -1):
        checks, build = plans[k]
        keep = set()
        for state in layers[k]:
            for value in _values(state, checks, upper[k]):
                if _step(state, build, value) in good:
                    keep.add(state)
                    values[k].add(value)
        good = keep
    return values


def _feasible(instance, upper, box):
    layers, _ = _forward(instance, upper, box)
    return layers is not None


def point_through(instance, upper=None, fixed=None, box=None):
    """One point of the instance, as a list of counts, or None.

    `fixed` maps groups to the value they must take. The point is found
    by walking back through the forward layers and re-checked against
    every constraint in whole numbers before it is returned: an
    existence claim stands on the point exhibited.
    """
    upper = list(instance.upper if upper is None else upper)
    for g, value in (fixed or {}).items():
        if value > upper[g]:
            return None
        upper[g] = value
    lower = {g: v for g, v in (fixed or {}).items()}
    box = box if box is not None else _budget()
    layers, plans = _forward(instance, upper, box)
    if layers is None:
        return None
    target = next(iter(layers[-1]))
    point = [0] * len(plans)
    for k in range(len(plans) - 1, -1, -1):
        checks, build = plans[k]
        found = None
        for state in sorted(layers[k]):
            for value in _values(state, checks, upper[k]):
                if value < lower.get(k, 0):
                    continue
                if _step(state, build, value) == target:
                    found = (state, value)
                    break
            if found is not None:
                break
        if found is None:
            return None
        target, point[k] = found
    if not holds_point(instance, point):
        raise AssertionError("a point walked back from the layers broke a constraint")
    return point


def holds_point(instance, point):
    """Whether a list of counts meets every constraint, in whole numbers."""
    if any(v < 0 or v > u for v, u in zip(point, instance.upper)):
        return False
    for terms, lo, hi in instance.original:
        total = 0
        for g, c in terms:
            total += c * point[g]
        if not lo <= total <= hi:
            return False
    return True


def pass_bound(instance, upper=None):
    """An upper bound on the transitions of one pass, from sizes alone (`pass_bounds`' first)."""
    return pass_bounds(instance, upper)[0]


def pass_bounds(instance, upper=None):
    """Upper bounds on one pass's transitions and on the entries it writes and reads, from sizes alone.

    After group `k` the states are tuples of the open constraints'
    partial sums. Each partial sum is a multiple of the gcd of the
    coefficients read so far, inside the window the constraint's total
    and the largest counts leave it, so the states number at most the
    product of those counts; and at most the states before times the
    values group `k` can take (one where `k` closes an equation). The
    pass makes at most the states before each group times its values.
    Each state before group `k` reads one check for each constraint
    reading `k`, and each transition writes one entry for each
    constraint open after `k`: the ENTRIES, bounded the same way.
    Returns `(transitions, entries)`.
    """
    upper = instance.upper if upper is None else upper
    count = len(upper)
    opened, plans, empty_ok = _layout(instance, upper)
    if not empty_ok:
        return 0, 0
    # For each constraint, running sums over its groups in order: the
    # least and most its first terms can add, and the gcd of the
    # coefficients of the terms that can be above nought.
    info = []
    for terms, lo, hi in instance.constraints:
        groups = [g for g, _ in terms]
        lows = [0]
        highs = [0]
        gcds = [0]
        for g, c in terms:
            lows += [lows[-1] + min(0, c * upper[g])]
            highs += [highs[-1] + max(0, c * upper[g])]
            gcds += [math.gcd(gcds[-1], abs(c)) if upper[g] > 0 else gcds[-1]]
        info += [(groups, lows, highs, gcds, lo, hi)]
    total = 0
    entries = 0
    states = 1
    for k in range(count):
        checks, build = plans[k]
        width = upper[k] + 1
        for _, c, window_low, window_high in checks:
            width = min(width, _floor_div(window_high - window_low, abs(c)) + 1)
        width = max(width, 0)
        total += states * width
        entries += states * len(checks) + states * width * len(build)
        product = 1
        for index in opened[k]:
            groups, lows, highs, gcds, lo, hi = info[index]
            j = bisect.bisect_right(groups, k)
            low = max(lows[j], lo - (highs[-1] - highs[j]))
            high = min(highs[j], hi - (lows[-1] - lows[j]))
            if high < low:
                product = 0
                break
            divisor = gcds[j] or 1
            product *= _floor_div(high, divisor) - _ceil_div(low, divisor) + 1
        states = min(product, states * width)
    return total, entries


def class_bound(instance):
    """The transitions every pass of `decide` can make together, bounded from sizes (`class_bounds`' first)."""
    return class_bounds(instance)[0]


def class_bounds(instance):
    """The transitions and the entries every pass of `decide` can make together, bounded from sizes.

    The full pass forward and backward, one pass for clause (b), and one
    for each group holding a small atom (clause (c)). Zeroing groups only
    narrows every window and every value range, so each later pass is
    bounded by the first.
    """
    one, entries = pass_bounds(instance)
    asked = sum(len(groups) for _, groups in instance.small_atoms)
    return one * (3 + asked), entries * (3 + asked)


class Verdict:
    """What `decide` found: the class, the witness and its parts."""

    def __init__(self):
        self.inside = False
        self.why = None
        self.bound = 0
        self.entries = 0
        self.nodes = 0
        self.read = 0
        self.empty = False
        self.largest = None
        self.unreachable = []
        self.zero = None
        self.small = None
        self.holds = False

    def as_dict(self, instance):
        out = {
            "class": CLASS_NAME if self.inside else "outside",
            "bound": self.bound,
            "entries": self.entries,
            "nodes": self.nodes,
        }
        if not self.inside:
            out["why"] = self.why
        if self.inside:
            out["empty"] = self.empty
            out["v_minus"] = [instance.keys[k] for k in self.unreachable]
            out["b"] = self.zero
            out["c"] = self.small
            out["holds"] = self.holds
        return out


def decide(instance, nodes_max=NODES_MAX, entries_max=ENTRIES_MAX):
    """Decide the witness of contract 4.6d.4 on one instance, or say it lies outside.

    Returns a `Verdict`. Outside the class (its groups above
    `GROUPS_MAX`, a slope in the region, its bound above `nodes_max` or
    its entries above `entries_max`; `why` names the first test it
    fails) nothing is searched and `holds` is False: the option is not
    eligible, whatever a search would find. Inside, the verdict is
    exact: `unreachable` is `V-`; `zero` is clause (b); `small` is
    clause (c), read over every point; `holds` is all three.
    """
    verdict = Verdict()
    verdict.why = "groups"
    if instance.counted > GROUPS_MAX:
        verdict.bound = None
        verdict.entries = None
        return verdict
    verdict.why = "slope"
    if instance.slopes:
        verdict.bound = None
        verdict.entries = None
        return verdict
    verdict.bound, verdict.entries = class_bounds(instance)
    verdict.why = "nodes"
    if verdict.bound > nodes_max:
        return verdict
    verdict.why = "entries"
    if verdict.entries > entries_max:
        return verdict
    verdict.why = None
    verdict.inside = True
    box = [verdict.bound, verdict.entries]
    upper = list(instance.upper)
    largest = _solve(instance, upper, box)
    if largest is None:
        verdict.empty = True
        verdict.zero = False
        verdict.small = False
        verdict.nodes = verdict.bound - box[0]
        verdict.read = verdict.entries - box[1]
        return verdict
    verdict.largest = largest
    f = instance.floor
    unreachable = [
        k for k in range(len(upper)) if k not in instance.holds_small and largest[k] < f
    ]
    verdict.unreachable = unreachable
    zeroed = list(upper)
    for k in unreachable:
        zeroed[k] = 0
    verdict.zero = _feasible(instance, zeroed, box)
    small_ok = True
    if verdict.zero:
        for _, groups in instance.small_atoms:
            for g in groups:
                if largest[g] < 1:
                    continue
                asked = list(zeroed)
                for other in groups:
                    if other != g:
                        asked[other] = 0
                if not _feasible(instance, asked, box):
                    small_ok = False
                    break
            if not small_ok:
                break
    else:
        small_ok = False
    verdict.small = small_ok
    verdict.holds = bool(verdict.zero and small_ok)
    verdict.nodes = verdict.bound - box[0]
    verdict.read = verdict.entries - box[1]
    return verdict


# --- building the joint space from a region's published facts -----------


def build_instance(spec):
    """The joint space `Sigma(R, o)` of a region, from its published facts.

    `spec` holds:
    - `floor`: the floor `f`;
    - `cells`: the base cells, in order, each `{"name", "bands"}`, its
      band of every member (a region column at its `L0` band);
    - `atoms`: for each region column, its atoms in reading order, each
      `{"name", "band", "codes", "reading", "small"}`: the `L0` band it
      lies in, its codes by code name (`"L"`, `"S"`), whether it holds a
      reading, and whether it is a small atom;
    - `margins`: each published count over base cells, `{"cells",
      "count"}` (a node's cell, an `L0` total);
    - `facts`: each own fact as a count of atoms, `{"column", "atoms",
      "lo", "hi"}`;
    - `sums`: each published number, `{"columns", "codes", "powers",
      "centres", "cells", "value"}`: the sum over the listed base cells'
      rows holding a reading of every listed column of the product of
      each column's code less its centre, raised to its power;
    - `slopes`: the nodes of the region that publish a slope (contract
      4.6b.6), each named as the spec's reader names it; empty or absent
      where none does. A slope is point condition (5), which is not
      linear, so a region holding one lies outside the class (rule (3)):
      the space listed here, without it, would hold more points than
      `Sigma(R, o)`, and an existence claim read on it could be false.
    A key outside these is refused (ValueError): a published fact the
    route does not read is never left out in silence. The groups are
    counted from these sizes BEFORE any is listed (each base cell's
    product, over the region columns, of the atoms its band holds); a
    region counting more than `GROUPS_MAX` is returned with no group
    listed, and `decide` reads it as outside. Groups are listed cell by
    cell, each cell's atom vectors in the columns' order, every column's
    atoms in reading order.
    """
    unread = sorted(set(spec) - set(SPEC_KEYS))
    if unread:
        raise ValueError("a published fact the route does not read: %s" % ", ".join(unread))
    floor = spec.get("floor", DEFAULT_FLOOR)
    columns = sorted(spec["atoms"])
    slopes = tuple(spec.get("slopes") or ())
    counted = 0
    for cell in spec["cells"]:
        product = 1
        for column in columns:
            band = cell["bands"][column]
            product *= sum(1 for a in spec["atoms"][column] if a["band"] == band)
        counted += product
    if counted > GROUPS_MAX:
        return Instance([], [], [], (), floor, slopes=slopes, counted=counted)
    keys = []
    vectors = []
    of_cell = []
    for at, cell in enumerate(spec["cells"]):
        choices = []
        for column in columns:
            band = cell["bands"][column]
            choices += [[a for a in spec["atoms"][column] if a["band"] == band]]
        for vector in itertools.product(*choices):
            keys += [(cell["name"],) + tuple(a["name"] for a in vector)]
            vectors += [vector]
            of_cell += [at]
    groups_of_cell = {}
    for g, at in enumerate(of_cell):
        groups_of_cell[at] = groups_of_cell.get(at, []) + [g]
    upper = []
    for g, at in enumerate(of_cell):
        top = None
        for margin in spec["margins"]:
            if at in margin["cells"]:
                top = margin["count"] if top is None else min(top, margin["count"])
        for fact in spec.get("facts", ()):
            position = columns.index(fact["column"])
            if vectors[g][position]["name"] in fact["atoms"]:
                top = fact["hi"] if top is None else min(top, fact["hi"])
        if top is None:
            raise ValueError("every base cell lies in some published count")
        upper += [top]
    constraints = []
    for margin in spec["margins"]:
        terms = []
        for at in margin["cells"]:
            terms += [(g, 1) for g in groups_of_cell.get(at, [])]
        constraints += [(terms, margin["count"], margin["count"])]
    for fact in spec.get("facts", ()):
        position = columns.index(fact["column"])
        terms = [(g, 1) for g in range(len(keys)) if vectors[g][position]["name"] in fact["atoms"]]
        constraints += [(terms, fact["lo"], fact["hi"])]
    for total in spec.get("sums", ()):
        terms = []
        wanted = set(total["cells"])
        for g in range(len(keys)):
            if of_cell[g] not in wanted:
                continue
            coefficient = 1
            for column, code, power, centre in zip(
                total["columns"], total["codes"], total["powers"], total["centres"]
            ):
                atom = vectors[g][columns.index(column)]
                if not atom["reading"]:
                    coefficient = 0
                    break
                coefficient *= (atom["codes"][code] - centre) ** power
            if coefficient:
                terms += [(g, coefficient)]
        constraints += [(terms, total["value"], total["value"])]
    small = []
    for position, column in enumerate(columns):
        for atom in spec["atoms"][column]:
            if atom.get("small"):
                groups = [g for g in range(len(keys)) if vectors[g][position]["name"] == atom["name"]]
                small += [((column, atom["name"]), groups)]
    return Instance(keys, upper, constraints, small, floor, slopes=slopes, counted=counted)


def groups_by_sizes(cells_per_member, atoms_per_band):
    """The count of groups a region would list, from published sizes alone.

    `cells_per_member` gives, for each member of the region's nodes that
    is not a region column, its band count at the finest level a node
    holds it; `atoms_per_band` gives, for each region column, its atom
    count in each `L0` band. Every combination is a base cell (a cell
    whose published count is nought is still listed: it costs a group and
    holds no row), so the count is the members' product times, for each
    region column, the sum of its atoms over its bands.
    """
    count = 1
    for bands in cells_per_member:
        count *= bands
    for per_band in atoms_per_band:
        count *= sum(per_band)
    return count


def in_class_by_sizes(cells_per_member, atoms_per_band, slopes=False):
    """The class's tests (1) and (3), on sizes alone, before any instance is built."""
    return groups_by_sizes(cells_per_member, atoms_per_band) <= GROUPS_MAX and not slopes


# --- the closed form CF1 of contract 4.6d.4, for the comparison --------


def cf1_reach(rows, total, low, high, code, floor=DEFAULT_FLOOR):
    """CF1's first claim: code `code` of a cell can hold `f` rows."""
    if rows < floor:
        return False
    return (rows - floor) * low + floor * code <= total <= (rows - floor) * high + floor * code


def cf1_holds(rows, total, low, high, floor=DEFAULT_FLOOR):
    """CF1's second claim: clause (b) on one cell (a run, and the sum inside it)."""
    run = [v for v in range(low, high + 1) if cf1_reach(rows, total, low, high, v, floor)]
    return bool(run) and rows * run[0] <= total <= rows * run[-1]


def one_cell_spec(rows, low, high, total, floor=DEFAULT_FLOOR):
    """One base cell of `rows` rows over the codes `low` to `high`, its code sum published.

    The region of CF1's conditions read on one cell: one column, one
    band, one atom a code (an interior band holding no own-fact group),
    and the cell's code sum the one published number.
    """
    atoms = [
        {"name": v, "band": 0, "codes": {"L": v}, "reading": True, "small": False}
        for v in range(low, high + 1)
    ]
    return {
        "floor": floor,
        "cells": [{"name": "cell", "bands": {"c": 0}}],
        "atoms": {"c": atoms},
        "margins": [{"cells": [0], "count": rows}],
        "facts": [],
        "sums": [
            {"columns": ["c"], "codes": ["L"], "powers": [1], "centres": [0], "cells": [0], "value": total}
        ],
    }


def correlation_allowed(n, s10, s01, s20, s02, s11):
    """Test (i) of contract 4.6d.3 in whole numbers: `400 cov**2 < 361 var_a var_b`."""
    cov = n * s11 - s10 * s01
    var_a = n * s20 - s10 * s10
    var_b = n * s02 - s01 * s01
    return 400 * cov * cov < 361 * var_a * var_b
