"""The patient layer's arithmetic, shared by its producer and its loader (contract 4.6c; lane GRa, plan P4-D449).

NOT IN FORCE. Like `chain_rules`, this module is read by the loader
(`chain_check`, invariants S29 to S33) as well as by the producer
(`patient_layer`), so it imports neither the reader nor the describing
side: everything here reads PUBLISHED counts only, which is what makes
every certificate it decides a function of the description (contract
4.6c.10's inventory, class (a) and (b)).

WHAT IS HERE, by 4.6c's own sections:

- the census of `r` (4.6c.4): a candidate's bands and its open top band,
  its eligibility, and the bounded DEFICIT SEARCH for the top band's
  floored split at the tight cap, which gives up after `TRIES_MAX` steps;
- PWIT in closed form (4.6c.8 step 3) for a parent cell of one `r`;
- the FLOORED SPLIT (4.6c.2 (d), 4.6c.8 (a)): a deterministic, bounded
  search that deals each band's rows to blocks of at least `f` patients,
  band by band, each step a deficit search; what it exhibits is checked
  again in Python integers before it is relied on, and a search that
  finds nothing means "not eligible" (breadth given up, never a leak);
- `R*` (4.6c.8 step 4) on a grain cell holding one census band;
- the class witness's counts `V` and `V_K` read from a split's patterns
  (4.6c.5 (e));
- the trend's certificate SWING (4.6c.1 (b)) and the unpinned total's
  guard (item (b) 6), on published facts and `Q_P` alone;
- the loader's invariants S29 to S33 (4.6c.10), `check`.

ARITHMETIC. Every count is a Python integer and every grid quantity an
exact fraction; no library float decides anything here (plan P4-D409,
zone D).
"""

import dataclasses
import fractions

from synthtwin import chain_moments
from synthtwin import chain_rules
from synthtwin import errors

# The chain's two modules under the short names this module reads them by.
moments = chain_moments
rules = chain_rules

# The searches' bounds (contract 4.6c's setting; PROVISIONAL until lane
# CHa's count of their refusals, which this lane's measurements report).
TRIES_MAX = 1000000
PATTERNS_MAX = 4096
NODES_MAX = 10000
# ONE CERTIFICATE'S FLOORED SPLITS, EVERY TRIAL COUNTED, KEPT OR NOT (the
# statistics skeptic's item 8), so a table's layer has a stated ceiling: at most
# this many steps for each of `OPTIONS_READ_MAX` options of each column. Its
# give-up is named `SPLIT_BOUND` in the counts; a fixed function of one option's
# own table, so the loader reaches the producer's outcome.
SPLIT_TRIES_MAX = 200000
SPLIT_BOUND = "SPLIT_TRIES_MAX"
# The blocks that may trade a whole multiple of their patients, largest first.
TRADING_BLOCKS = 8

# The largest top edge a census offers: at most 12 single values below its top
# band, as a column's `L0` holds at most 13 bands (departure (15) of 4.6c.12).
CENSUS_TOP_EDGE_MAX = 13

# The patient table's made column (4.6c.9: "`r` under the name").
R_NAME = "(rows per patient)"

# The classes of 4.6c's setting, as `grain.classes` writes them.
CLASS_PERSON = "person"
CLASS_FIXED = "patient_fixed"
CLASS_POSITION = "position_like"
CLASS_DEALT = "dealt_date"
CLASS_COMPUTED = "computed"
CLASS_REPEATED = "repeated"
CLASS_HELD = "held"
CLASS_INELIGIBLE = "ineligible"
CLASSES = (
    CLASS_PERSON, CLASS_FIXED, CLASS_POSITION, CLASS_DEALT,
    CLASS_COMPUTED, CLASS_REPEATED, CLASS_HELD, CLASS_INELIGIBLE,
)

# The derived columns' kinds (4.6c.2 (a)).
FIRST_DATE = "first_date"
OWN_MEAN = "own_mean"

# The keys of `grain` (4.6c.9), the departure of 4.6c.9 (a) included.
GRAIN_KEYS = (
    "census", "classes", "derived", "fixed_rows", "grain_family", "grid",
    "ladder", "person", "position", "positions", "rows", "trend",
)

# The keys a block the layer empties keeps (S30).
EMPTIED_KEPT = ("name", "position", "role")


def ceil_div(numerator: int, denominator: int) -> int:
    """`ceil(numerator / denominator)` in whole numbers, the denominator positive."""
    return -((-numerator) // denominator)


def own_mean_floor(floor: int) -> int:
    """The own mean's value-band floor, `max(2 f, f + 4)` patients (4.6c.2 (a))."""
    return max(2 * floor, floor + 4)


def _get(mapping: object, key: str) -> object:
    if isinstance(mapping, dict) and key in mapping:
        return mapping[key]
    return None


def _whole(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


# -- THE DEFICIT SEARCH (4.6c.4 (b)) -------------------------------------


@dataclasses.dataclass(frozen=True)
class Split:
    """A floored split found by the deficit search: each value's patients, and the steps it took."""

    values: "tuple[tuple[int, int], ...]"
    steps: int


def _least_in_class(residue: int, modulus: int, floor: int) -> int:
    """The least whole number at least `floor` that is `residue` modulo `modulus`."""
    if residue >= floor:
        return residue
    return residue + modulus * ceil_div(floor - residue, modulus)


def _inverse_modulo(value: int, modulus: int) -> int:
    """The inverse of `value` modulo `modulus`, the two coprime (the extended Euclid algorithm)."""
    old_r, r = value, modulus
    old_s, s = 1, 0
    while r:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
    return old_s % modulus


def deficit_split(patients: int, excess: int, floor: int) -> "tuple[Split | None, int]":
    """The top band's FLOORED SPLIT at the tight cap, by the bounded deficit search (4.6c.4 (b)).

    `patients` (`m`) patients whose excesses (`r - lo`) sum to `excess`
    (`q`). Returns a split, each value `0 .. t` held by 0 or at least
    `floor` patients, summing to `m` patients and `q` excess, with `t =
    ceil(q / m)` its largest value, and the steps the search took; None
    where none is found within `TRIES_MAX` steps (breadth given up).
    The search tries, in this order: every patient at `t`; one block
    below `t`; two blocks at neighbouring distances; two blocks at any
    two distances. Every split it finds has at most three values.
    Guarantees: a fixed function of its three arguments; reads nothing
    else; raises nothing.
    """
    if patients <= 0:
        return (Split((), 0), 0) if excess == 0 else (None, 0)
    if excess < 0 or patients < floor:
        return None, 0
    top = ceil_div(excess, patients)
    deficit = patients * top - excess
    steps = 1
    if deficit == 0:
        return Split(((top, patients),), steps), steps
    reach = min(top, deficit // floor)
    for distance in range(1, reach + 1):
        steps += 1
        if deficit % distance == 0:
            moved = deficit // distance
            if floor <= moved <= patients - floor:
                return Split(((top - distance, moved), (top, patients - moved)), steps), steps
    for distance in range(1, min(top - 1, deficit // floor) + 1):
        steps += 1
        if steps > TRIES_MAX:
            return None, steps
        least = max(2 * floor, ceil_div(deficit + floor, distance + 1))
        most = min(patients - floor, (deficit - floor) // distance)
        if least <= most:
            further = deficit - least * distance
            nearer = least - further
            if nearer >= floor and further >= floor:
                return Split(
                    ((top - distance - 1, further), (top - distance, nearer), (top, patients - least)), steps
                ), steps
    for near in range(1, reach + 1):
        for far in range(near + 2, reach + 1):
            steps += 1
            if steps > TRIES_MAX:
                return None, steps
            common = rules.gcd(near, far)
            if deficit % common:
                continue
            step_far = near // common
            reduced = deficit // common
            if step_far == 1:
                count_far = floor
            else:
                inverse = _inverse_modulo((far // common) % step_far, step_far)
                count_far = _least_in_class((reduced * inverse) % step_far, step_far, floor)
            while True:
                steps += 1
                if steps > TRIES_MAX:
                    return None, steps
                rest = deficit - count_far * far
                if rest < floor * near:
                    break
                count_near = rest // near
                if count_near * near == rest and count_near + count_far <= patients - floor:
                    return Split(
                        ((top - far, count_far), (top - near, count_near), (top, patients - count_near - count_far)),
                        steps,
                    ), steps
                count_far += step_far
    return None, steps


def split_checked(split: Split, patients: int, excess: int, floor: int) -> bool:
    """A split re-checked in Python integers: floored, `m` patients, `q` excess, values `0 .. t`."""
    top = ceil_div(excess, patients) if patients else 0
    held = 0
    total = 0
    for value, count in split.values:
        if count < floor or value < 0 or value > top:
            return False
        held += count
        total += value * count
    return held == patients and total == excess


# -- THE CENSUS OF `r` (4.6c.4) ------------------------------------------


@dataclasses.dataclass(frozen=True)
class Census:
    """A candidate census: `c_rho` for `rho` below `lo`, and the open top band "`r` at least `lo`"."""

    lo: int
    bands: "tuple[int, ...]"
    top_patients: int
    top_rows: int

    @property
    def excess(self) -> int:
        """The top band's excess `q = n_top - lo m`."""
        return self.top_rows - self.lo * self.top_patients

    @property
    def patients(self) -> int:
        return sum(self.bands) + self.top_patients

    @property
    def rows(self) -> int:
        return sum((at + 1) * self.bands[at] for at in range(len(self.bands))) + self.top_rows


def census_at(lo: int, counts: "dict[int, int]") -> Census:
    """The candidate with top edge `lo`, read off a table's patients by `r` (`counts[r]` patients)."""
    bands = tuple(counts[rho] if rho in counts else 0 for rho in range(1, lo))
    top_patients = 0
    top_rows = 0
    for rho in counts:
        if rho >= lo:
            top_patients += counts[rho]
            top_rows += rho * counts[rho]
    return Census(lo, bands, top_patients, top_rows)


def census_eligible(census: Census, floor: int) -> "tuple[bool, int, Split | None]":
    """Whether a candidate is ELIGIBLE (4.6c.4 (b)), with the deficit search's steps and its split.

    Items 1 and 2 read `c_rho`, `m` and `q` alone, so the loader repeats
    the same decision on the published census.
    """
    for count in census.bands:
        if 0 < count < floor:
            return False, 0, None
    if 0 < census.top_patients < floor:
        return False, 0, None
    if census.top_patients == 0:
        return census.top_rows == 0, 0, None
    split, steps = deficit_split(census.top_patients, census.excess, floor)
    if split is None or not split_checked(split, census.top_patients, census.excess, floor):
        return False, steps, None
    return True, steps, split


def tight_cap(census: Census) -> int:
    """The top band's tight cap `t = ceil(q / m)`, 0 where the band is empty."""
    if census.top_patients == 0:
        return 0
    return ceil_div(census.excess, census.top_patients)


def census_written(census: Census) -> "dict[str, object]":
    """`grain.census` as 4.6c.9 writes it."""
    return {
        "bands": [{"patients": census.bands[at], "r": at + 1} for at in range(len(census.bands))],
        "lo": census.lo,
        "top": {"patients": census.top_patients, "rows": census.top_rows},
    }


def census_read(value: object) -> "Census | None":
    """`grain.census` read back, or None where it is not the shape 4.6c.9 writes."""
    if not isinstance(value, dict) or sorted(value) != ["bands", "lo", "top"]:
        return None
    lo = value["lo"]
    bands = value["bands"]
    top = value["top"]
    if not _whole(lo) or not isinstance(lo, int) or lo < 1 or not isinstance(bands, list) or len(bands) != lo - 1:
        return None
    counts: "list[int]" = []
    for at in range(len(bands)):
        entry = bands[at]
        if not isinstance(entry, dict) or sorted(entry) != ["patients", "r"] or entry["r"] != at + 1:
            return None
        count = entry["patients"]
        if not _whole(count) or not isinstance(count, int) or count < 0:
            return None
        counts += [count]
    if not isinstance(top, dict) or sorted(top) != ["patients", "rows"]:
        return None
    patients = top["patients"]
    rows = top["rows"]
    if not _whole(patients) or not _whole(rows) or not isinstance(patients, int) or not isinstance(rows, int):
        return None
    if patients < 0 or rows < lo * patients:
        return None
    return Census(lo, tuple(counts), patients, rows)


def r_band_names(census: Census) -> "list[tuple[str, ...]]":
    """`r`'s `L0` band descriptors: each value below `lo` on its own, then the open top band (4.6c.4 (d))."""
    names: "list[tuple[str, ...]]" = []
    for at in range(len(census.bands)):
        if census.bands[at]:
            names += [(f"{at + 1}",)]
    if census.top_patients:
        names += [(f"{census.lo} or more",)]
    return names


def r_ladder(census: Census) -> "rules.Ladder | None":
    """`r` as a column of the patient table: its census's nonempty bands at every level (departure (2) of P4-D449).

    `L1` and `L2` equal `L0`, so every family holding `r` holds it at the
    census's own bands, and a grain cell holds ONE census band: the tie
    of `R*` then reads one band a cell. None where fewer than two bands
    hold patients (`r` is then `one_band`, 4.6c.8 (a)).
    """
    names = r_band_names(census)
    totals: "list[int]" = []
    for at in range(len(census.bands)):
        if census.bands[at]:
            totals += [census.bands[at]]
    if census.top_patients:
        totals += [census.top_patients]
    if len(names) < 2:
        return None
    identity = tuple(range(len(names)))
    return rules.Ladder(R_NAME, tuple((name,) for name in names), (identity, identity, identity), (len(names), len(names), len(names)), tuple(totals), tuple(True for _name in names))


def r_band_values(census: Census) -> "list[tuple[int, int | None]]":
    """Each nonempty band's values of `r`: `(rho, rho)` below `lo`, `(lo, None)` for the open top band."""
    out: "list[tuple[int, int | None]]" = []
    for at in range(len(census.bands)):
        if census.bands[at]:
            out += [(at + 1, at + 1)]
    if census.top_patients:
        out += [(census.lo, None)]
    return out


# -- PWIT (4.6c.8 step 3) -------------------------------------------------


def pwit(patients: int, supplies: "list[int] | tuple[int, ...]", floor: int) -> bool:
    """PWIT in a parent cell of one `r`: `s_x <= |P| floor(s_x / f)` for every band `x`."""
    if patients <= 0:
        return all(supply == 0 for supply in supplies)
    for supply in supplies:
        if supply > patients * (supply // floor):
            return False
    return True


# -- THE FLOORED SPLIT (4.6c.2 (d), 4.6c.8 (a)) ---------------------------


@dataclasses.dataclass(frozen=True)
class Klass:
    """A class `(C, rho)` of a parent cell: its patients, its rows a patient, and its allowed rows per band.

    `low[beta]` and `high[beta]` bound how many of a patient's rows may
    stand in band `beta` (an own mean's allowed patterns on a two-band
    child, 4.6c.2 (c); `0` and `rho` where nothing restricts them).
    """

    patients: int
    rho: int
    low: "tuple[int, ...]"
    high: "tuple[int, ...]"


@dataclasses.dataclass(frozen=True)
class Block:
    """Patients of one class sharing one pattern: `count` of them, `pattern[beta]` rows in band `beta`."""

    klass: int
    count: int
    pattern: "tuple[int, ...]"


@dataclasses.dataclass(frozen=True)
class Found:
    """A floored split's blocks, the steps it took, and whether a bound was reached."""

    blocks: "tuple[Block, ...]"
    steps: int
    bound: str


def _deal_band(
    pending: "list[tuple[int, int, tuple[int, ...], int, int]]",
    supply: int,
    floor: int,
    budget: "dict[object, object]",
) -> "list[tuple[int, int, tuple[int, ...]]] | None":
    """One band's rows dealt to the blocks: each block's share, then each share split into blocks of at least `floor`.

    `pending` holds (class, patients, pattern so far, least rows a
    patient takes here, most rows a patient takes here). Each block's
    share of the band's rows above its least is first set in proportion
    to its room, in whole multiples of its patients (every patient alike,
    a split of one value); what is left goes to one block, or one block
    gives up a whole multiple to another, each trial split by the deficit
    search; an exact bounded subset sum decides the rest (`_shares_exact`).
    Returns the blocks with this band's rows added to their patterns, or
    None where no share is found within the budget (`SPLIT_TRIES_MAX`).
    """
    least_total = 0
    widths: "list[int]" = []
    for entry in pending:
        least_total += entry[1] * entry[3]
        widths += [entry[1] * (entry[4] - entry[3])]
    wanted = supply - least_total
    room = sum(widths)
    if wanted < 0 or wanted > room:
        return None
    shares: "list[int]" = []
    for at in range(len(pending)):
        patients = pending[at][1]
        ideal = (wanted * widths[at]) // room if room else 0
        shares += [patients * (ideal // patients)]
    left = wanted - sum(shares)
    for at in range(len(pending)):
        patients = pending[at][1]
        while left >= patients and shares[at] + patients <= widths[at]:
            shares[at] += patients
            left -= patients
    order = [pair[1] for pair in sorted((-pending[at][1], at) for at in range(len(pending)))]
    if left == 0:
        dealt = _dealt(pending, shares, floor, budget)
        if dealt is not None:
            return dealt
    for at in order:
        if shares[at] + left <= widths[at]:
            trial = list(shares)
            trial[at] += left
            dealt = _dealt(pending, trial, floor, budget)
            if dealt is not None:
                return dealt
            if _spent(budget) > SPLIT_TRIES_MAX:
                return None
    for at in order[:TRADING_BLOCKS]:
        patients = pending[at][1]
        if shares[at] < patients:
            continue
        for other in order[:TRADING_BLOCKS]:
            if other != at and shares[other] + left + patients <= widths[other]:
                trial = list(shares)
                trial[at] -= patients
                trial[other] += left + patients
                dealt = _dealt(pending, trial, floor, budget)
                if dealt is not None:
                    return dealt
                if _spent(budget) > SPLIT_TRIES_MAX:
                    return None
    shares_found = _shares_exact(pending, widths, wanted, floor, budget)
    if shares_found is None:
        return None
    return _dealt(pending, shares_found, floor, budget)


def _or_shifts(mask: int, low: int, high: int) -> int:
    """The union of `mask` shifted by every whole number from `low` to `high` (a bitset), by doubling."""
    if high < low:
        return 0
    span = high - low + 1
    out = 0
    block = mask
    size = 1
    place = 0
    while span:
        if span & 1:
            out |= block << place
            place += size
        block |= block << size
        size *= 2
        span >>= 1
    return out << low


def _valid_share(patients: int, share: int, floor: int) -> bool:
    """Whether a share is one the dealing takes: a whole multiple of the block, or a remainder of `f` to `m - f`."""
    rest = share % patients
    return rest == 0 or (patients >= 2 * floor and floor <= rest <= patients - floor)


def _shares_exact(
    pending: "list[tuple[int, int, tuple[int, ...], int, int]]",
    widths: "list[int]",
    wanted: int,
    floor: int,
    budget: "dict[object, object]",
) -> "list[int] | None":
    """Each block's share, found exactly where one exists among the valid shares (a bounded subset sum).

    A share is valid where every patient of the block takes one value
    (a whole multiple of its patients) or two neighbouring values each on
    at least `f` patients (a remainder of `f` to `m - f`). The reachable
    totals are held as one bitset a block; the shares are read back from
    the last block to the first, each the valid share nearest its block's
    proportional one. Every shift counts one step against `SPLIT_TRIES_MAX`.
    """
    limit = (1 << (wanted + 1)) - 1
    masks = [1]
    for at in range(len(pending)):
        patients = pending[at][1]
        reach = masks[-1]
        grown = 0
        for times in range(widths[at] // patients + 1):
            base = times * patients
            if base > wanted:
                break
            grown |= reach << base
            budget["spent"] = _spent(budget) + 1
            if patients >= 2 * floor:
                low = base + floor
                high = min(base + patients - floor, widths[at], wanted)
                grown |= _or_shifts(reach, low, high)
                budget["spent"] = _spent(budget) + 1
        masks += [grown & limit]
        if _spent(budget) > SPLIT_TRIES_MAX:
            return None
    if not (masks[-1] >> wanted) & 1:
        return None
    room = sum(widths)
    shares = [0] * len(pending)
    left = wanted
    for at in range(len(pending) - 1, -1, -1):
        patients = pending[at][1]
        ideal = (wanted * widths[at]) // room if room else 0
        before = masks[at]
        chosen = -1
        for distance in range(0, min(widths[at], left) + 1):
            for share in (ideal - distance, ideal + distance):
                if 0 <= share <= min(widths[at], left) and _valid_share(patients, share, floor) and (before >> (left - share)) & 1:
                    chosen = share
                    break
            if chosen >= 0:
                break
            budget["spent"] = _spent(budget) + 1
        if chosen < 0:
            return None
        shares[at] = chosen
        left -= chosen
    return shares if left == 0 else None


def _spent(budget: "dict[object, object]") -> int:
    found = budget["spent"] if "spent" in budget else 0
    return found if isinstance(found, int) else 0


def _split_kept(patients: int, excess: int, floor: int, budget: "dict[object, object]") -> "Split | None":
    """The deficit search's split, kept by its arguments for one search; every call one step, a search's own steps once."""
    key = (patients, excess)
    budget["spent"] = _spent(budget) + 1
    if key in budget:
        kept = budget[key]
        return kept if isinstance(kept, (Split,)) else None
    split, steps = deficit_split(patients, excess, floor)
    budget["spent"] = _spent(budget) + steps
    if split is not None and not split_checked(split, patients, excess, floor):
        split = None
    budget[key] = split
    return split


def _dealt(
    pending: "list[tuple[int, int, tuple[int, ...], int, int]]",
    shares: "list[int]",
    floor: int,
    budget: "dict[object, object]",
) -> "list[tuple[int, int, tuple[int, ...]]] | None":
    """Each block's share split into floored blocks by the deficit search, or None where one has none."""
    out: "list[tuple[int, int, tuple[int, ...]]]" = []
    for at in range(len(pending)):
        klass, patients, pattern, least, _most = pending[at]
        split = _split_kept(patients, shares[at], floor, budget)
        if split is None:
            return None
        for value, count in split.values:
            out += [(klass, count, pattern + (least + value,))]
    return out


def floored_split(classes: "list[Klass]", supplies: "list[int]", floor: int, budget: "dict[object, object] | None" = None) -> Found:
    """A FLOORED SPLIT of a parent cell (4.6c.2 (d)), found band by band, re-checked in integers.

    Every class's patients are dealt into blocks of at least `floor`
    patients sharing one pattern, each pattern within the class's allowed
    rows a band, the patterns' rows in each band summing to `supplies`.
    The search is deterministic and bounded (`SPLIT_TRIES_MAX` steps in
    all, the one `budget` a certificate hands every parent cell): each band's rows are shared among the blocks
    (`_deal_band`), each share split by the deficit search; the last
    band takes what is left. Returns the blocks, or none with the bound
    or the reason named. Guarantees: a fixed function of the arguments,
    which are published counts only; raises nothing.
    """
    bands = len(supplies)
    if budget is None:
        budget = {"spent": 0}
    for klass in classes:
        if klass.patients and klass.patients < floor:
            return Found((), 0, "a class of 1 to f - 1 patients")
    if sum(klass.patients * klass.rho for klass in classes) != sum(supplies):
        return Found((), 0, "the classes' rows are not the cell's rows")
    blocks: "list[tuple[int, int, tuple[int, ...]]]" = []
    for at in range(len(classes)):
        if classes[at].patients:
            blocks += [(at, classes[at].patients, ())]
    if not blocks:
        return Found((), 0, "") if sum(supplies) == 0 else Found((), 0, "rows without patients")
    for beta in range(bands - 1):
        pending: "list[tuple[int, int, tuple[int, ...], int, int]]" = []
        for klass_at, count, pattern in blocks:
            klass = classes[klass_at]
            left = klass.rho - sum(pattern)
            later_low = sum(klass.low[beta + 1 :])
            later_high = sum(klass.high[beta + 1 :])
            least = max(klass.low[beta], left - later_high)
            most = min(klass.high[beta], left - later_low)
            if least > most:
                return Found((), _spent(budget), "no allowed pattern")
            pending += [(klass_at, count, pattern, least, most)]
        dealt = _deal_band(pending, supplies[beta], floor, budget)
        if dealt is None:
            bound = SPLIT_BOUND if _spent(budget) > SPLIT_TRIES_MAX else "no share split"
            return Found((), _spent(budget), bound)
        blocks = dealt
    found: "list[Block]" = []
    for klass_at, count, pattern in blocks:
        klass = classes[klass_at]
        left = klass.rho - sum(pattern)
        if not klass.low[bands - 1] <= left <= klass.high[bands - 1]:
            return Found((), _spent(budget), "no allowed pattern")
        found += [Block(klass_at, count, pattern + (left,))]
    if not split_holds(found, classes, supplies, floor):
        return Found((), _spent(budget), "the exhibited split failed its check")
    return Found(tuple(_merged(found)), _spent(budget), "")


def _merged(blocks: "list[Block]") -> "list[Block]":
    """Blocks of one class and one pattern joined, in a fixed order."""
    joined: "dict[tuple[int, tuple[int, ...]], int]" = {}
    for block in blocks:
        key = (block.klass, block.pattern)
        joined[key] = joined[key] + block.count if key in joined else block.count
    return [Block(key[0], joined[key], key[1]) for key in sorted(joined)]


def split_holds(blocks: "list[Block]", classes: "list[Klass]", supplies: "list[int]", floor: int) -> bool:
    """A split re-checked in Python integers: floored blocks, allowed patterns, class sizes and band supplies."""
    held = [0] * len(classes)
    rows = [0] * len(supplies)
    for block in blocks:
        klass = classes[block.klass]
        if block.count < floor or len(block.pattern) != len(supplies) or sum(block.pattern) != klass.rho:
            return False
        for beta in range(len(supplies)):
            if not klass.low[beta] <= block.pattern[beta] <= klass.high[beta]:
                return False
            rows[beta] += block.count * block.pattern[beta]
        held[block.klass] += block.count
    return held == [klass.patients for klass in classes] and rows == list(supplies)


def witness_counts(blocks: "tuple[Block, ...] | list[Block]") -> "tuple[int, int]":
    """`V` and `V_K` read from a split's patterns (4.6c.5 (e)): patients holding a level twice, and two levels."""
    repeats = 0
    mixed = 0
    for block in blocks:
        if any(rows >= 2 for rows in block.pattern):
            repeats += block.count
        if len([rows for rows in block.pattern if rows]) >= 2:
            mixed += block.count
    return repeats, mixed


def swung(blocks: "tuple[Block, ...]", classes: "list[Klass]", floor: int, wanted: int) -> "tuple[Block, ...]":
    """A split's blocks swung until `V` reaches `wanted`, every band's rows kept (the class witness, 4.6c.5 (e)).

    A block of `2 g` patients (`g >= floor`) whose pattern holds rows in
    two bands `a` and `b` becomes `g` patients with one row moved from `b`
    to `a` and `g` with one moved from `a` to `b`: the band sums and the
    class sizes stay, and each new pattern holds a band twice wherever
    the old one held it once or more. Blocks are swung in a fixed order.
    """
    out = list(blocks)
    at = 0
    while witness_counts(out)[0] < wanted and at < len(out):
        block = out[at]
        klass = classes[block.klass]
        bands = [beta for beta in range(len(block.pattern)) if block.pattern[beta]]
        if block.count % 2 == 0 and block.count >= 2 * floor:
            half = block.count // 2
        else:
            half = (block.count - floor) // 2
        rest = block.count - 2 * half
        if len(bands) >= 2 and half >= floor and (rest == 0 or rest >= floor):
            a, b = bands[0], bands[1]
            up = list(block.pattern)
            down = list(block.pattern)
            up[a] += 1
            up[b] -= 1
            down[a] -= 1
            down[b] += 1
            if klass.low[a] <= down[a] and up[a] <= klass.high[a] and klass.low[b] <= up[b] and down[b] <= klass.high[b]:
                kept = [Block(block.klass, rest, block.pattern)] if rest else []
                out = out[:at] + [Block(block.klass, half, tuple(up)), Block(block.klass, half, tuple(down))] + kept + out[at + 1 :]
                at += 2 + len(kept)
                continue
        at += 1
    return tuple(_merged(out))


# -- R* ON A GRAIN CELL OF ONE CENSUS BAND (4.6c.8 step 4) ---------------

def r_star(patients: int, rows: int, band: "tuple[int, int | None]", floor: int) -> "tuple[tuple[int, int], ...] | None":
    """`R*_C` for a grain cell of `patients` patients and `rows` rows holding one census band (departure (2)).

    A band of one value `rho` gives every patient `rho` (the cell's rows
    must then be `rho |C|`); the open top band takes the deficit search's
    split of the cell's own excess at its own tight cap, so `R*`'s world
    is a table under every cap a reader may know (the cap lemma: every
    table of the description gives this cell a largest excess at least
    its tight cap). None where none is found.
    """
    low, high = band
    if patients == 0:
        return () if rows == 0 else None
    if patients < floor:
        return None
    if high is not None:
        return ((low, patients),) if rows == low * patients else None
    split, _steps = deficit_split(patients, rows - low * patients, floor)
    if split is None or not split_checked(split, patients, rows - low * patients, floor):
        return None
    return tuple((low + value, count) for value, count in split.values)


def _has_split(patients: int, share: int, floor: int, seen: "dict[tuple[int, int], bool]") -> bool:
    """Whether `patients` patients holding `share` excess rows have a floored split, each pair searched once."""
    key = (patients, share)
    if key not in seen:
        seen[key] = deficit_split(patients, share, floor)[0] is not None
    return seen[key]


def top_rows_shared(cells: "list[int]", lo: int, excess: int, floor: int) -> "list[int] | None":
    """The top band's excess shared among its grain cells so each has a floored split (a one-cell family's `R*`).

    `cells` are the top band's patients in each grain cell of one block (a
    parent cell's cut of the open top band), `excess` the block's published
    extra rows. No cell's share passes the block's own tight cap, `ceil(q /
    m)` rows a patient over `lo`: by the cap lemma every table of the
    description gives the block a largest excess at least that, so `R*`
    stays a world under every cap a reader may know (Codex's review of lane
    GRa, item 1: a block of 37 patients and 22 extra rows, cap 1, gave 11
    patients 2 each, a world no table holds, and certified it). Each cell
    takes a share in proportion to its patients, whole multiples first, the
    remainder moved to the first cell whose deficit search then succeeds;
    returns each cell's rows, or None. Each cell's search is asked at most
    twice, whatever the number of cells (Codex's item 5: a recheck of every
    earlier cell for each trial grew with the square of the cells).
    """
    total = sum(cells)
    if total == 0:
        return [] if excess == 0 else None
    if excess < 0:
        return None
    cap = ceil_div(excess, total)
    shares = [(excess * count) // total for count in cells]
    shares = [count * (shares[at] // count) if count else 0 for at, count in enumerate(cells)]
    left = excess - sum(shares)
    for at in range(len(cells)):
        while cells[at] and left >= cells[at] and shares[at] + cells[at] <= cap * cells[at]:
            shares[at] += cells[at]
            left -= cells[at]
    seen: "dict[tuple[int, int], bool]" = {}
    failing = [k for k in range(len(cells)) if cells[k] and not _has_split(cells[k], shares[k], floor, seen)]
    if left == 0 or len(failing) > 1:
        return None if failing else [lo * cells[k] + shares[k] for k in range(len(cells))]
    # One cell takes the remainder: the failing cell where there is one,
    # else the first that can (every other cell's search already passed).
    for at in failing if failing else range(len(cells)):
        if not cells[at] or shares[at] + left > cap * cells[at]:
            continue
        if _has_split(cells[at], shares[at] + left, floor, seen):
            trial = list(shares)
            trial[at] += left
            return [lo * cells[k] + trial[k] for k in range(len(cells))]
    return None


# -- THE TREND: THE GRID CODE AND SWING (4.6c.1) -------------------------


@dataclasses.dataclass(frozen=True)
class Grid:
    """A FINE column's grid code `c(v) = min(K, max(0, round((v - L) / u)))` (4.6c's setting)."""

    column: str
    step: fractions.Fraction
    low: fractions.Fraction
    codes: int


def grid_code(grid: Grid, value: fractions.Fraction) -> int:
    """A reading's grid code, exactly; halves rounded to even as Python's `round` does."""
    raw = round((value - grid.low) / grid.step)
    return min(grid.codes, max(0, int(raw)))


def decimal_text(value: fractions.Fraction) -> str:
    """An exact fraction written as a decimal string where it has one, else as `p/q`."""
    if value.denominator == 1:
        return f"{value.numerator}"
    denominator = value.denominator
    twos = 0
    fives = 0
    while denominator % 2 == 0:
        denominator //= 2
        twos += 1
    while denominator % 5 == 0:
        denominator //= 5
        fives += 1
    if denominator != 1:
        return f"{value.numerator}/{value.denominator}"
    places = max(twos, fives)
    scaled = value * (10 ** places)
    whole = int(abs(scaled))
    sign = "-" if value < 0 else ""
    digits = f"{whole:0{places + 1}d}"
    return f"{sign}{digits[:-places]}.{digits[-places:]}"


def fraction_read(text: object) -> "fractions.Fraction | None":
    """A decimal string or `p/q` written by `decimal_text`, read back exactly, else None."""
    if not isinstance(text, str) or not text:
        return None
    try:
        return fractions.Fraction(text)
    except (ValueError, ZeroDivisionError):
        return None


def grid_written(grid: Grid) -> "dict[str, object]":
    """A `grain.grid` entry: `{column, u, L, K}`, the numbers as decimal strings (4.6c.9)."""
    return {"K": f"{grid.codes}", "L": decimal_text(grid.low), "column": grid.column, "u": decimal_text(grid.step)}


def weight_sxx(rows: int) -> int:
    """`Sxx(r) = (r^3 - r) / 12`, a whole number for every `r >= 1`."""
    return (rows * rows * rows - rows) // 12


@dataclasses.dataclass(frozen=True)
class TrendClass:
    """One class `(b, k)` of SWING: its greedy pair `a_c`, `b_c` and its bound `u_c` (4.6c.1 (b))."""

    least: int
    most: int
    bound: int


def greedy_pair(ranges: "list[tuple[int, int]]", total: int) -> "tuple[int, int] | None":
    """The greedy maximum and minimum of `S` for code ranges sorted by band over positions `1 .. r` at code sum `total`.

    `ranges[j]` is position `j + 1`'s code range. Units are placed into
    the highest weights first (maximum) or the lowest (minimum), each
    position inside its range. The rigid rule of 4.6c.1 (b) 2 as repaired:
    where a position whose range holds ONE code has a wider range before
    it AND after it, the minimum is read as the maximum. None where the
    total does not fit.
    """
    count = len(ranges)
    floor_sum = sum(low for low, _high in ranges)
    ceiling_sum = sum(high for _low, high in ranges)
    if not floor_sum <= total <= ceiling_sum:
        return None
    weights = [2 * (j + 1) - count - 1 for j in range(count)]

    def placed(order: "list[int]") -> int:
        codes = [low for low, _high in ranges]
        left = total - floor_sum
        for j in order:
            room = ranges[j][1] - ranges[j][0]
            take = min(room, left)
            codes[j] += take
            left -= take
        return sum(codes[j] * weights[j] for j in range(count))

    most = placed(list(range(count - 1, -1, -1)))
    least = placed(list(range(count)))
    wide = [ranges[j][1] > ranges[j][0] for j in range(count)]
    for j in range(count):
        if ranges[j][1] == ranges[j][0] and any(wide[:j]) and any(wide[j + 1 :]):
            least = most
            break
    return most, least


def swing_passes(
    q_value: int,
    rows: int,
    patients: int,
    classes: "list[TrendClass]",
    band_caps: "list[tuple[int, list[int]]]",
    codes: int,
    floor: int,
) -> bool:
    """SWING on published facts (4.6c.1 (b) 4 and 5), for one cell of `|P|` patients of one `r >= 2`.

    `classes` are the classes with `u_c > 0`; `band_caps` the per-band
    caps on patients (`n_b`) with the classes each holds (indices into
    `classes`). The two capacities are the least `sum n_c b_c` and `sum
    n_c (b_c - a_c)` over whole `0 <= n_c <= u_c` summing to `|P|` and
    at most `n_b` a band, each by the greedy fill, cheapest classes first.
    """
    if not classes or rows < 2:
        return False
    cap_b = _least_fill([one.most for one in classes], classes, band_caps, patients)
    cap_g = _least_fill([one.most - one.least for one in classes], classes, band_caps, patients)
    if cap_b is None or cap_g is None:
        return False
    widest = rows * rows // 4
    if rows % 2 == 0:
        reach = max(abs(2 * q_value), abs(2 * q_value + 1))
    else:
        reach = abs(2 * q_value)
    top_b = max(one.most for one in classes)
    top_gap = max(one.most - one.least for one in classes)
    if reach > cap_b - floor * (top_b + codes * widest):
        return False
    return max(one.least + one.most for one in classes) <= cap_g - floor * top_gap + 2


def _least_fill(costs: "list[int]", classes: "list[TrendClass]", band_caps: "list[tuple[int, list[int]]]", patients: int) -> "int | None":
    """The least `sum n_c cost_c` with `0 <= n_c <= u_c`, `sum n_c = |P|` and each band's `n_c` within its cap."""
    left = patients
    used = [0] * len(classes)
    band_left = {at: cap for at, (cap, _members) in enumerate(band_caps)}
    band_of: "dict[int, int]" = {}
    for at, (_cap, members) in enumerate(band_caps):
        for member in members:
            band_of[member] = at
    total = 0
    for cost, place in sorted((costs[at], at) for at in range(len(classes))):
        if left == 0:
            break
        band = band_of[place] if place in band_of else -1
        room = classes[place].bound - used[place]
        if band >= 0:
            room = min(room, band_left[band])
        take = min(room, left)
        if take <= 0:
            continue
        used[place] += take
        left -= take
        if band >= 0:
            band_left[band] -= take
        total += take * cost
    return total if left == 0 else None


def one_code_rows(child: rules.Ladder, block: "dict[str, object]", level: int, grid: Grid) -> "list[int]":
    """The rows of each band of a row family's child at `level` that stand in `L0` bands of ONE code (`n_one`, by band)."""
    out = [0] * child.counts[level]
    for band in range(child.counts[0]):
        low_edge, high_edge, valued = band_edges(child, block, 0, band)
        first, last = code_range(grid, low_edge, high_edge)
        if valued and first == last:
            out[child.maps[level][band]] += child.totals[band]
    return out


def free_rows(cells: "Cells", values: "list[tuple[int, int | None]]", parent_of: "list[int]", width: int, table: "list[int]", bands: int, one_code: "list[int]") -> int:
    """`O_free` (4.6c.1 (b) 6, as amended by departure (17)), read on published counts.

    `O` rows lie outside the cells of `F_S` holding one `r >= 2`. A band of
    one code fixes its rows' code, so what keeps the outside total free is
    a WORLD holding at least `f` outside rows in bands of two or more codes,
    not the worst case of every one-code row outside: the reader cannot fix
    the total while such a world stands. Each parent cell's outside rows
    are its rows less its one-`r` cells', and each stands in a band of the
    row family's child only where that cell has rows in the band; so the
    outside rows are placed on the bands' rows of two or more codes,
    parent cell by parent cell, each band's fewest first. Returns how many
    so place. A lower bound on the most any world holds, so `O_free >= f`
    exhibits one; a fixed function of published counts.
    """
    inside = [0] * width
    for cell in range(len(cells.patients)):
        low, high = values[cells.r_band[cell]]
        if high is not None and low >= 2:
            inside[parent_of[cell]] += low * cells.patients[cell]
    room = [sum(table[at * bands + band] for at in range(width)) - one_code[band] for band in range(bands)]
    free = 0
    for at in range(width):
        outside = sum(table[at * bands : (at + 1) * bands]) - inside[at]
        for _room, band in sorted((room[one], one) for one in range(bands)):
            take = min(outside, table[at * bands + band], room[band])
            if take > 0:
                free += take
                outside -= take
                room[band] -= take
    return free


# -- THE LOADER'S INVARIANTS S29 TO S33 (4.6c.10) -------------------------


def broken(invariant: str, where: str, detail: str) -> errors.ProfileError:
    """A refusal naming the invariant, in the chain's words (`errors.profile_chain_broken`)."""
    return errors.ProfileError(errors.profile_chain_broken(invariant, where, detail))


def emptied(block: "dict[str, object]") -> bool:
    """Whether a column block holds no key but `name`, `position` and `role` (S30)."""
    for key in block:
        if key in EMPTIED_KEPT:
            continue
        if block[key] not in (None, {}, []):
            return False
    return True


def check(document: "dict[str, object]", grain: "dict[str, object]", tabled: int, blank_rows: int, floor: int) -> "dict[str, object]":
    """Refuse a description whose patient layer breaks S29 to S33; return what the patient chain's check reads.

    Reads the description alone. Returns the census, the classes, the
    person column and the patient count for `chain_check` to hold the
    patient chain to S23 to S28 over the patient table.
    """
    if sorted(grain) != sorted(GRAIN_KEYS):
        raise broken("S29", "grain", "the patient layer holds exactly its twelve keys")
    columns = _get(document, "columns")
    blocks: "dict[str, dict[str, object]]" = {}
    schema: "list[str]" = []
    if isinstance(columns, list):
        for block in columns:
            if isinstance(block, dict) and isinstance(_get(block, "name"), str):
                blocks[f"{block['name']}"] = block
                schema += [f"{block['name']}"]
    settings = _get(document, "settings")
    persons = _get(settings, "person_columns")
    person = grain["person"]
    # -- S29: the gate --
    if not isinstance(persons, list) or len(persons) != 1 or persons[0] != person or person not in blocks:
        raise broken("S29", "grain.person", "the layer stands only beside exactly one person column")
    person_block = blocks[f"{person}"]
    if _get(person_block, "n_missing") != blank_rows:
        raise broken("S29", f"{person}", "no tabled row lacks a person value")
    census = census_read(grain["census"])
    if census is None:
        raise broken("S29", "grain.census", "the census of r holds lo, its bands and its open top band")
    if census.lo > CENSUS_TOP_EDGE_MAX:
        raise broken("S29", "grain.census", "a census offers at most 12 single values below its top band")
    patients = census.patients
    if _get(person_block, "n_distinct") != patients:
        raise broken("S29", "grain.census", "the census's patients are the person column's different values")
    if census.rows != tabled or _get(person_block, "n_present") != tabled:
        raise broken("S29", "grain.census", "the census's rows are the tabled rows")
    if tabled - patients < floor:
        raise broken("S29", "grain.census", "the extra rows are at least the floor")
    eligible, _steps, _split = census_eligible(census, floor)
    if not eligible:
        raise broken("S29", "grain.census", "the census is eligible: every band 0 or at least the floor, and a floored split of its top band")
    if _get(person_block, "n_distinct_by_occurrences") is not None:
        raise broken("S29", f"{person}", "the person column's repetition census is withheld while the layer stands")
    for name in schema:
        if name == person:
            continue
        found = _get(blocks[name], "n_distinct_by_occurrences")
        if found is not None and not _one_row_each(found, _get(blocks[name], "n_present")):
            raise broken("S29", name, "a multiplicity map is withheld while the layer stands, unless each value covers one row")
    # -- S30: classes, positions, the patient table --
    classes = _classes_read(grain["classes"], schema, f"{person}")
    positions = grain["positions"]
    if not isinstance(positions, list):
        raise broken("S30", "grain.positions", "a list")
    listed: "dict[str, list[object]]" = {}
    for entry in positions:
        if not isinstance(entry, dict) or sorted(entry) != ["column", "values"] or not isinstance(entry["values"], list):
            raise broken("S30", "grain.positions", "each entry names a column and its values")
        listed[f"{entry['column']}"] = entry["values"]
    length = census.lo if census.top_patients else len(census.bands)
    for name in schema:
        kind = classes[name]
        if kind in (CLASS_POSITION, CLASS_HELD) and not emptied(blocks[name]):
            raise broken("S30", name, "a position-like or held column publishes no block of its own")
        if kind == CLASS_POSITION:
            if name not in listed or len(listed[name]) != length:
                raise broken("S30", name, "a position-like column lists one modal value for each position up to L")
            shown = [one for one in listed[name] if one is not None]
            if len(set(f"{one}" for one in shown)) != len(shown):
                raise broken("S30", name, "the listed values stand in pairwise different levels")
        elif name in listed:
            raise broken("S30", name, "only a position-like column has a positions entry")
    position = grain["position"]
    dealt = [
        name for name in schema
        if classes[name] == CLASS_DEALT or (classes[name] == CLASS_HELD and _get(blocks[name], "role") == rules.ROLE_DATETIME)
    ]
    if position != (dealt[0] if dealt else None):
        raise broken("S30", "grain.position", "the position column is the first dealt date column, kept where it is held")
    _fixed_rows_read(grain["fixed_rows"], classes, census)
    # -- S31: row families --
    rows = grain["rows"]
    if not isinstance(rows, list):
        raise broken("S31", "grain.rows", "a list")
    for at in range(len(rows)):
        entry = rows[at]
        if not isinstance(entry, dict) or sorted(entry) != ["child", "level", "parents", "table"]:
            raise broken("S31", f"grain.rows[{at}]", "a row family holds child, level, parents and table")
        child = entry["child"]
        if child not in classes or classes[f"{child}"] not in (CLASS_REPEATED, CLASS_DEALT):
            raise broken("S31", f"grain.rows[{at}]", "the child is a repeated or dealt date column")
        table = entry["table"]
        if not isinstance(table, list):
            raise broken("S31", f"{child}", "the table is complete")
        total = 0
        for row in table:
            if not isinstance(row, list):
                raise broken("S31", f"{child}", "the table is complete")
            for cell in row:
                if not _whole(cell) or not isinstance(cell, int) or cell < 0 or 0 < cell < floor:
                    raise broken("S31", f"{child}", "every cell is 0 or at least the floor, in rows")
                total += cell
        if total != tabled:
            raise broken("S31", f"{child}", "the table sums to the tabled rows")
    # -- S32: derived columns --
    derived = grain["derived"]
    if not isinstance(derived, list):
        raise broken("S32", "grain.derived", "a list")
    for entry in derived:
        if not isinstance(entry, dict) or sorted(entry) != ["edges", "kind", "level", "name", "source"]:
            raise broken("S32", "grain.derived", "each derived column names its name, kind, source, level and edges")
        if entry["kind"] not in (FIRST_DATE, OWN_MEAN) or entry["source"] not in classes:
            raise broken("S32", f"{entry['name']}", "a first date or an own mean of a column of this table")
        # Codex's review of lane GRa, item 9: a level that is no level, or
        # edges that do not rise, define no bands.
        if entry["level"] not in rules.LEVELS:
            raise broken("S32", f"{entry['name']}", "a derived column's level is L0, L1 or L2")
        if not edges_rise(entry["edges"], f"{entry['kind']}"):
            raise broken("S32", f"{entry['name']}", "a derived column's edges rise strictly: decimal numbers for an own mean, one kind of date text or number for a first date")
    # -- S33: trends --
    trend = grain["trend"]
    grid = grain["grid"]
    if not isinstance(trend, list) or not isinstance(grid, list):
        raise broken("S33", "grain.trend", "lists")
    gridded = {f"{entry['column']}" for entry in grid if isinstance(entry, dict) and "column" in entry}
    for entry in trend:
        if not isinstance(entry, dict) or sorted(entry) != ["cell", "column", "q"] or entry["column"] not in gridded:
            raise broken("S33", "grain.trend", "each trend names a gridded column, its cell and its q")
        if not _whole(entry["q"]):
            raise broken("S33", f"{entry['column']}", "q is a whole number")
    return {"census": census, "classes": classes, "person": person, "patients": patients}


def edges_rise(edges: object, kind: str) -> bool:
    """Whether a derived column's written edges rise strictly (S32): decimal numbers for an own mean; date texts, or numbers, for a first date."""
    if not isinstance(edges, list):
        return False
    if kind == OWN_MEAN:
        read = [fraction_read(one) for one in edges]
        exact = [one for one in read if one is not None]
        return len(exact) == len(edges) and all(exact[at] < exact[at + 1] for at in range(len(exact) - 1))
    if all(isinstance(one, str) for one in edges):
        texts = [f"{one}" for one in edges]
        return all(texts[at] < texts[at + 1] for at in range(len(texts) - 1))
    if all(isinstance(one, (int, float)) and not isinstance(one, bool) for one in edges):
        numbers = [fractions.Fraction(one) for one in edges if isinstance(one, (int, float))]
        return all(numbers[at] < numbers[at + 1] for at in range(len(numbers) - 1))
    return False


def edges_expected(kind: str, ladder: rules.Ladder) -> int:
    """How many edges a derived column writes beside its ladder (S32): an own mean, one a band but the first; a first date, one a band whose first starting band opens at a rung."""
    if kind == OWN_MEAN:
        return ladder.counts[0] - 1
    count = 0
    for band in ladder.l0:
        first = band[0] if band else None
        if isinstance(first, tuple) and len(first) == 2 and first[0] is not None:
            count += 1
    return count


def _one_row_each(found: object, present: object) -> bool:
    """Whether a multiplicity map is `{1: n_present}` (S29: `{1: n_present}` stays)."""
    if not isinstance(found, dict) or len(found) != 1:
        return False
    for key in found:
        return isinstance(key, str) and number_after(key, "") == 1 and found[key] == present
    return False


def _classes_read(value: object, schema: "list[str]", person: str) -> "dict[str, str]":
    """`grain.classes` read back: one class for every column, in schema order (S30)."""
    if not isinstance(value, list) or len(value) != len(schema):
        raise broken("S30", "grain.classes", "one class for every column, in schema order")
    out: "dict[str, str]" = {}
    for at in range(len(schema)):
        entry = value[at]
        if not isinstance(entry, dict) or sorted(entry) != ["class", "column"] or entry["column"] != schema[at]:
            raise broken("S30", "grain.classes", "one class for every column, in schema order")
        kind = entry["class"]
        if kind not in CLASSES:
            raise broken("S30", schema[at], "a class of contract 4.6c's setting")
        if (kind == CLASS_PERSON) != (schema[at] == person):
            raise broken("S30", schema[at], "the person column, and it alone, is classed person")
        out[schema[at]] = f"{kind}"
    return out


def _fixed_rows_read(value: object, classes: "dict[str, str]", census: Census) -> None:
    """`grain.fixed_rows`: each entry a patient-fixed column's row census, summing to the tabled rows (S30)."""
    if not isinstance(value, list):
        raise broken("S30", "grain.fixed_rows", "a list")
    for entry in value:
        if not isinstance(entry, dict) or sorted(entry) != ["column", "level", "rows"]:
            raise broken("S30", "grain.fixed_rows", "each entry names a column, its level and its rows")
        named = f"{entry['column']}"
        if named not in classes or classes[named] != CLASS_FIXED:
            raise broken("S30", f"{entry['column']}", "a row census belongs to a patient-fixed column")
        counted = entry["rows"]
        if not isinstance(counted, list) or not all(_whole(one) for one in counted):
            raise broken("S30", f"{entry['column']}", "a row census is a list of whole numbers")
        if sum(one for one in counted if isinstance(one, int)) != census.rows:
            raise broken("S30", f"{entry['column']}", "a row census sums to the tabled rows")


# -- THE GRAIN FAMILY'S CELLS AND THE ROW FAMILIES' CERTIFICATES ----------
# (4.6c.8 (a)), read on published counts, by the producer and the loader alike.


@dataclasses.dataclass(frozen=True)
class Cells:
    """The grain family's cells as published: its members, their band counts, each cell's patients and band of `r`.

    A cell is a place in `G`'s table (`rules.cell_parts` over `sizes`,
    child first); `r_band[cell]` indexes the census's nonempty bands
    (`r_band_values`).
    """

    members: "tuple[tuple[str, int], ...]"
    sizes: "tuple[int, ...]"
    patients: "tuple[int, ...]"
    r_band: "tuple[int, ...]"


def parent_parts(cell: int, sizes: "list[int]") -> "list[int]":
    """A parent cell's band of each parent, the last parent varying fastest."""
    out = [0] * len(sizes)
    for at in range(len(sizes) - 1, -1, -1):
        out[at] = cell % sizes[at]
        cell //= sizes[at]
    return out


def w1_in_rows(
    child: chain_rules.Ladder,
    level: int,
    child_groups: "frozenset[int] | set[int]",
    parents: "list[tuple[chain_rules.Ladder, int, frozenset[int] | set[int]]]",
    table: "list[int]",
    bands: int,
    width: int,
) -> bool:
    """RULE W1 read in rows for a row family (4.6c.8 (d)), as the table layer reads a root pair, parent by parent.

    The producer's and the loader's one rule (amendment 11 of 4.6c.12;
    Codex's review of lane GRa, item 6: the loader read none). `child` is
    the row column's ladder in rows at `level`, `child_groups` its `L0`
    bands holding an own-fact group (in rows); each parent is its ladder
    on the patient table, its level and its own-fact groups (in
    patients); `table` the family's cells, `bands` of the child in each
    of `width` parent cells. (a) Each band of the child holding an
    own-fact group reaches two bands of every parent's coarsest level;
    (b) each band of a parent holding an own-fact group reaches two
    bands of the child's coarsest level.
    """
    to_coarse = chain_rules.coarsen(child, level, 2)
    sizes = [ladder.counts[member_level] for ladder, member_level, _groups in parents]
    parts_of = [parent_parts(cell, sizes) for cell in range(width)]
    own = {child.maps[level][group] for group in child_groups}
    for band in sorted(own):
        for place in range(len(parents)):
            ladder, member_level, _groups = parents[place]
            to_parent = chain_rules.coarsen(ladder, member_level, 2)
            reached = {to_parent[parts_of[cell][place]] for cell in range(width) if table[cell * bands + band]}
            if len(reached) < 2:
                return False
    for place in range(len(parents)):
        ladder, member_level, groups = parents[place]
        for group in sorted(groups):
            band = ladder.maps[member_level][group]
            reached_bands: "set[int]" = set()
            for cell in range(width):
                if parts_of[cell][place] != band:
                    continue
                for child_band in range(bands):
                    if table[cell * bands + child_band]:
                        reached_bands |= {to_coarse[child_band]}
            if len(reached_bands) < 2:
                return False
    return True


def grouped(keys: "list[int]") -> "dict[int, list[int]]":
    """Each key's places in `keys`, in rising order; every list grown in place, so the work is linear in the places (Codex's review of lane GRa, item 5)."""
    out: "dict[int, list[int]]" = {}
    for place in range(len(keys)):
        key = keys[place]
        if key not in out:
            out[key] = []
        out[key] += [place]
    return out


def cell_part(cells: Cells, cell: int, place: int) -> int:
    """A cell's band of the member at `place`."""
    return rules.cell_parts(cell, list(cells.sizes))[place]


def member_place(cells: Cells, name: str) -> int:
    """A member's place among the grain family's members, or -1."""
    for at in range(len(cells.members)):
        if cells.members[at][0] == name:
            return at
    return -1


def number_after(text: str, head: str) -> "int | None":
    """The whole number written after `head` in `text`, or None where `text` is not so written."""
    if not isinstance(text, str):
        raise TypeError("a label is text")
    if not isinstance(head, str):
        raise TypeError("a label's head is text")
    if not text.startswith(head):
        return None
    return int(text[len(head):]) if text[len(head):].isdigit() else None


def place_in(names: "list[str] | tuple[str, ...]", name: str) -> int:
    """A name's place in a list of names, or -1."""
    for at in range(len(names)):
        if names[at] == name:
            return at
    return -1


def parent_cells(cells: Cells, chosen: "tuple[tuple[str, int], ...]", maps: "list[list[int]]", sizes: "list[int]") -> "tuple[list[int], int]":
    """Each grain cell's parent cell under parents `chosen`, given each parent's map from its level in `G` to its level here.

    The parent cell is the parents' joint band, the last parent varying
    fastest, as a row family's table reads it. Returns the map and the
    count of parent cells.
    """
    places = [member_place(cells, name) for name, _level in chosen]
    width = 1
    for size in sizes:
        width *= size
    out: "list[int]" = []
    for cell in range(len(cells.patients)):
        parts = rules.cell_parts(cell, list(cells.sizes))
        index = 0
        for at in range(len(chosen)):
            index = index * sizes[at] + maps[at][parts[places[at]]]
        out += [index]
    return out, width


def top_blocks(cells: Cells, values: "list[tuple[int, int | None]]", lo: int, members: "list[list[int]]", rows: "list[int]") -> "dict[frozenset[int], int] | None":
    """A family's cut of the open top band: each parent cell's top grain cells, with the excess its published rows leave them.

    None where a parent cell's rows cannot be its patients' rows. A grain
    cell holds one census band (departure (2)), so a parent cell's rows
    less its one-value cells' are its top cells' rows.
    """
    out: "dict[frozenset[int], int]" = {}
    for at in range(len(members)):
        top: "list[int]" = []
        fixed = 0
        for cell in members[at]:
            low, high = values[cells.r_band[cell]]
            if high is None:
                if cells.patients[cell]:
                    top += [cell]
            else:
                fixed += low * cells.patients[cell]
        if not top:
            if fixed != rows[at]:
                return None
            continue
        excess = rows[at] - fixed - lo * sum(cells.patients[cell] for cell in top)
        if excess < 0:
            return None
        out[frozenset(top)] = excess
    return out


def blocks_joined(first: "dict[frozenset[int], int]", second: "dict[frozenset[int], int]") -> "dict[frozenset[int], int] | None":
    """The finer of two families' cuts of the top band, or None where neither refines the other (R*'S TIE).

    4.6c.8 step 4 asks ONE `R*` meeting every table holding `r`. Where
    each family's cut refines or coarsens every other's, reading `R*` at
    the finest meets them all, provided their rows agree. Two cuts that
    cross would need an integer solve over both margins, and the first
    skeptic's table shows such margins may leave no floored world at all
    (each family passing on its own): they are refused, breadth given up.
    """
    for fine, coarse in ((first, second), (second, first)):
        totals: "dict[frozenset[int], int]" = {}
        refines = True
        for block in fine:
            holder = [one for one in coarse if block <= one]
            if len(holder) != 1:
                refines = False
                break
            totals[holder[0]] = (totals[holder[0]] if holder[0] in totals else 0) + fine[block]
        if refines and set(totals) == set(coarse):
            if any(totals[one] != coarse[one] for one in coarse):
                return None
            return fine
    return None


def r_star_of(cells: Cells, values: "list[tuple[int, int | None]]", lo: int, blocks: "dict[frozenset[int], int]", floor: int) -> "list[tuple[tuple[int, int], ...]] | None":
    """The description's one `R*` (4.6c.8 step 4): every grain cell's vector, read at the finest cut of the top band.

    A band of one value gives every patient that value; each block of top
    cells shares its excess among its cells (`top_rows_shared`) under the
    block's own tight cap, each then split by the deficit search at its own
    tight cap, which is no larger. None where no such `R*` is found. A
    fixed function of published counts.
    """
    rows = [0] * len(cells.patients)
    for at in range(len(cells.patients)):
        low, high = values[cells.r_band[at]]
        if high is not None:
            rows[at] = low * cells.patients[at]
    for block in sorted(blocks, key=sorted):
        top = sorted(block)
        shared = top_rows_shared([cells.patients[cell] for cell in top], lo, blocks[block], floor)
        if shared is None:
            return None
        for place in range(len(top)):
            rows[top[place]] = shared[place]
    out: "list[tuple[tuple[int, int], ...]]" = []
    for cell in range(len(cells.patients)):
        found = r_star(cells.patients[cell], rows[cell], values[cells.r_band[cell]], floor)
        if found is None:
            return None
        out += [found]
    return out


def code_range(grid: Grid, low: "fractions.Fraction | None", high: "fractions.Fraction | None") -> "tuple[int, int]":
    """A band `[low, high)`'s grid codes, open ends at the end codes."""
    first = 0
    if low is not None:
        scaled = (low - grid.low) / grid.step
        first = max(0, min(grid.codes, ceil_div(scaled.numerator, scaled.denominator)))
    last = grid.codes
    if high is not None:
        scaled = (high - grid.low) / grid.step
        last = max(0, min(grid.codes, ceil_div(scaled.numerator, scaled.denominator) - 1))
    return first, max(first, last)


def sum_interval(grid: Grid, rho: int, low_edge: "fractions.Fraction | None", high_edge: "fractions.Fraction | None") -> "tuple[int, int]":
    """The code sums `s` with `L + s u / rho` inside an own-mean band `[low_edge, high_edge)` (4.6c.1 (b) 1)."""
    first = 0
    last = rho * grid.codes
    if low_edge is not None:
        scaled = rho * (low_edge - grid.low) / grid.step
        first = max(first, ceil_div(scaled.numerator, scaled.denominator))
    if high_edge is not None:
        scaled = rho * (high_edge - grid.low) / grid.step
        last = min(last, ceil_div(scaled.numerator, scaled.denominator) - 1)
    return first, last


def allowed_interval(ranges: "list[tuple[int, int]]", sums: "tuple[int, int]", rho: int) -> "tuple[int, int] | None":
    """The rows `a` above the median a patient of `rho` readings may hold, its own mean's code sums `sums` (4.6c.2 (c)).

    A pattern of `rho - a` rows below the median and `a` above is ALLOWED
    where `[(rho - a) lo_0 + a lo_1, (rho - a) hi_0 + a hi_1]` meets the
    own-mean band's code-sum interval; both ends rise with `a`, so the
    allowed `a` form one interval. None where none is allowed.
    """
    (lo0, hi0), (lo1, hi1) = ranges
    first, last = sums
    allowed = [a for a in range(rho + 1) if (rho - a) * hi0 + a * hi1 >= first and (rho - a) * lo0 + a * lo1 <= last]
    if not allowed:
        return None
    return allowed[0], allowed[-1]


@dataclasses.dataclass(frozen=True)
class Restriction:
    """What a derived column asks of its source's patterns in each grain cell (4.6c.2 (c)).

    `place` is the derived column's place among `G`'s members; an own
    mean carries the child's bands' grid codes (`ranges`), its edges at
    its level in `G` and the grid; a first date which of the child's
    bands are value bands.
    """

    kind: str
    place: int
    ranges: "tuple[tuple[int, int], ...]"
    edges: "tuple[fractions.Fraction, ...]"
    grid: "Grid | None"
    value_bands: "tuple[bool, ...]"


def klass(restriction: "Restriction | None", cells: Cells, cell: int, rho: int, patients: int, bands: int) -> "Klass | None":
    """A class `(C, rho)` with its allowed rows a band; None where no pattern is allowed."""
    if restriction is None:
        return Klass(patients, rho, tuple(0 for _beta in range(bands)), tuple(rho for _beta in range(bands)))
    band = cell_part(cells, cell, restriction.place)
    if restriction.kind == FIRST_DATE:
        # One row in the first-date band, the other `rho - 1` at or above
        # it or in a spread band (`missing` read apart); a patient with no
        # present date holds every row in its own band.
        rest = rho - 1
        if not restriction.value_bands[band]:
            high = tuple(rest if beta == band else 0 for beta in range(bands))
        else:
            high = tuple(rest if (beta >= band or not restriction.value_bands[beta]) else 0 for beta in range(bands))
        return Klass(patients, rest, tuple(0 for _beta in range(bands)), high)
    grid = restriction.grid
    if grid is None or len(restriction.ranges) != 2:
        return None
    low_edge = restriction.edges[band - 1] if band >= 1 else None
    high_edge = restriction.edges[band] if band < len(restriction.edges) else None
    found = allowed_interval(list(restriction.ranges), sum_interval(grid, rho, low_edge, high_edge), rho)
    if found is None:
        return None
    least, most = found
    return Klass(patients, rho, (rho - most, least), (rho - least, most))


def _count_up(counts: "dict[str, int]", key: str, by: int) -> None:
    """A private counter raised (the counters no description reads)."""
    counts[key] = (counts[key] if key in counts else 0) + by


def certificate(
    cells: Cells,
    values: "list[tuple[int, int | None]]",
    members: "list[list[int]]",
    table: "list[int]",
    bands: int,
    stars: "list[tuple[tuple[int, int], ...]] | None",
    use_pwit: bool,
    restriction: "Restriction | None",
    witness: "int | None",
    floor: int,
    counts: "dict[str, int]",
    witness_v: bool = True,
) -> bool:
    """A row family's certificate on its published counts (4.6c.8 (a)); True where it holds in every parent cell.

    PWIT in a parent cell that is one grain cell of one `r` where
    `use_pwit` (residual PWIT under a first date); otherwise the floored
    split on `R*`, its classes `(C, rho)` each with its allowed rows a
    band; with the class witness, `V_K` and, where `witness_v`, `V`
    summed over the parent cells must reach `witness` (`T + 1`;
    `class_witness`). Counts its refusals in `counts`.
    """
    repeats = 0
    mixed = 0
    budget: "dict[object, object]" = {"spent": 0}
    for at in range(len(members)):
        supplies = list(table[at * bands : (at + 1) * bands])
        inside = members[at]
        if restriction is not None and restriction.kind == FIRST_DATE:
            for cell in inside:
                supplies[cell_part(cells, cell, restriction.place)] -= cells.patients[cell]
            if any(supply < 0 or 0 < supply < floor for supply in supplies):
                _count_up(counts, "certificate_refusals", 1)
                return False
        one_r = len(inside) == 1 and values[cells.r_band[inside[0]]][1] is not None
        if one_r and use_pwit and witness is None:
            if not pwit(cells.patients[inside[0]], supplies, floor):
                _count_up(counts, "certificate_refusals", 1)
                return False
            continue
        if stars is None:
            _count_up(counts, "certificate_refusals", 1)
            return False
        classes: "list[Klass]" = []
        for cell in inside:
            for rho, patients in stars[cell]:
                one = klass(restriction, cells, cell, rho, patients, bands)
                if one is None:
                    _count_up(counts, "certificate_refusals", 1)
                    return False
                classes += [one]
        spent_before = _spent(budget)
        found = floored_split(classes, supplies, floor, budget)
        _count_up(counts, "split_steps", found.steps - spent_before)
        _count_up(counts, "splits_tried", 1)
        if not found.blocks and sum(supplies) > 0:
            _count_up(counts, "certificate_refusals", 1)
            _count_up(counts, "splits_failed", 1)
            if found.bound == SPLIT_BOUND:
                _count_up(counts, "split_bound_hit", 1)
            return False
        if witness is not None:
            # The swing raises `V` and spends `V_K`: a witness of `V_K` alone
            # reads the split's patterns as the deficit search spread them.
            blocks = swung(found.blocks, classes, floor, witness) if witness_v else found.blocks
            one_count, two_count = witness_counts(blocks)
            repeats += one_count
            mixed += two_count
    if witness is not None and ((witness_v and repeats < witness) or mixed < witness):
        _count_up(counts, "witness_refusals", 1)
        return False
    return True


def total_fixed(block: "dict[str, object]") -> bool:
    """Whether the exact mean and both tails' pairs or listed values fix the code total (4.6c.1 (b) 6)."""
    if _get(block, "mean") is None:
        return False
    tails = _get(block, "tails")
    if not isinstance(tails, dict):
        return False
    for side in ("low", "high"):
        tail = _get(tails, side)
        if not isinstance(tail, dict):
            return False
        pair = _get(tail, "mean_distance") is not None and _get(tail, "rms_distance") is not None
        listed = isinstance(_get(tail, "values"), list) and bool(_get(tail, "values"))
        if not pair and not listed:
            return False
    return True


def swing_classes(
    cells: Cells,
    held_cells: "list[int]",
    held: int,
    rho: int,
    table: "list[int]",
    bands: int,
    ranges: "list[tuple[int, int]]",
    grid: Grid,
    edges: "list[fractions.Fraction]",
    place: int,
    parent_of: "list[int]",
) -> "tuple[list[TrendClass], list[tuple[int, list[int]]]] | None":
    """SWING's classes for one cell of `held` patients (4.6c.1 (b) 1 to 3), read on published counts.

    The cell's patients lie in the grain cells `held_cells`; each gives an
    own-mean band `b` (one band where `G` holds none) and the row family's
    published cells holding them (their rows summed: a looser bound, never
    a tighter one). A class is a pattern whose every band those cells
    leave non-zero, at the code sum of `b`'s interval whose greedy maximum
    is largest; its bound the least of `|P|`, the band's patients and each
    band's rows over the pattern's rows there.
    """
    by_band: "dict[int, list[int]]" = {}
    for cell in held_cells:
        band = cell_part(cells, cell, place) if place >= 0 else 0
        if band not in by_band:
            by_band[band] = []
        by_band[band] += [cell]
    classes: "list[TrendClass]" = []
    caps: "list[tuple[int, list[int]]]" = []
    weights = [2 * (j + 1) - rho - 1 for j in range(rho)]
    for band in sorted(by_band):
        supplies = [0] * bands
        patients = 0
        for cell in by_band[band]:
            patients += cells.patients[cell]
        for parent in sorted({parent_of[cell] for cell in by_band[band]}):
            for child in range(bands):
                supplies[child] += table[parent * bands + child]
        low_edge = edges[band - 1] if place >= 0 and 1 <= band <= len(edges) else None
        high_edge = edges[band] if place >= 0 and band < len(edges) else None
        first_sum, last_sum = sum_interval(grid, rho, low_edge, high_edge)
        members: "list[int]" = []
        for above in range(rho + 1):
            pattern = (rho - above, above)
            if any(pattern[beta] and not supplies[beta] for beta in range(bands)):
                continue
            arrangement = [ranges[0]] * pattern[0] + [ranges[1]] * pattern[1]
            least_sum = sum(low for low, _high in arrangement)
            most_sum = sum(high for _low, high in arrangement)
            first = max(first_sum, least_sum)
            last = min(last_sum, most_sum)
            if first > last:
                continue
            peak = least_sum + sum(arrangement[j][1] - arrangement[j][0] for j in range(rho) if weights[j] > 0)
            pair = greedy_pair(arrangement, min(last, max(first, peak)))
            if pair is None:
                continue
            bound = min(held, patients)
            for beta in range(bands):
                if pattern[beta]:
                    bound = min(bound, supplies[beta] // pattern[beta])
            if bound <= 0:
                continue
            members += [len(classes)]
            classes += [TrendClass(pair[1], pair[0], bound)]
        caps += [(patients, members)]
    if not classes:
        return None
    return classes, caps


# -- PUBLISHED FACTS OF ONE COLUMN THE CERTIFICATES READ -------------------


def exact_number(value: object) -> "fractions.Fraction | None":
    """A published number read exactly as the decimal it is written as (`repr` of a float), else None."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    if isinstance(value, float):
        return fractions.Fraction(repr(value))
    return fractions.Fraction(value)


def reading_of(role: str, value: object, block: "dict[str, object]") -> "fractions.Fraction | None":
    """A reading or a rung as an exact number in the column's own order: a number as its decimal, a date on its ordinal."""
    if role in rules.NUMBER_ROLES:
        return exact_number(value)
    return moments.ordinal(role, value, block)


def rung_of(block: "dict[str, object]", key: object) -> "fractions.Fraction | None":
    """A published rung, by its key, as an exact number in the column's own order."""
    if key is None:
        return None
    rungs = rules.rung_ladder(block)
    if not isinstance(rungs, dict):
        return None
    return reading_of(f"{_get(block, 'role')}", _get(rungs, f"{key}"), block)


def grid_of(block: "dict[str, object]") -> "Grid | None":
    """A FINE column's grid code read on its tail boundary rungs (4.6c's setting), or None where it has none.

    None too where the block is top-coded. `L` and `H` are the rungs at the tails' percents; `u` the column's
    published step (`1` where every reading is whole, `10^-w` where every
    reading is written to `w` decimal places, else `(H - L) / 4095`); `K`
    is `(H - L) / u` rounded. None where `tails` or either side is null,
    or `K < 1`.
    """
    # A TOP-CODED READING TAKES NO GRID (the first skeptic's item 2, HIPAA;
    # 45 CFR 164.514(b)(2)(i)(C)): the cells a mean or a code would read hold
    # the ages the block pools at 90, so no own mean, no edge and no `Q_P`.
    if _get(block, "top_coded"):
        return None
    tails = _get(block, "tails")
    rungs = rules.rung_ladder(block)
    if not isinstance(tails, dict) or not isinstance(rungs, dict):
        return None
    low_side = _get(tails, "low")
    high_side = _get(tails, "high")
    if not isinstance(low_side, dict) or not isinstance(high_side, dict):
        return None
    low_percent = _get(low_side, "percent")
    high_percent = _get(high_side, "percent")
    if not _whole(low_percent) or not _whole(high_percent):
        return None
    low = exact_number(_get(rungs, f"p{low_percent:02d}"))
    high = exact_number(_get(rungs, f"p{high_percent:02d}"))
    if low is None or high is None or high <= low:
        return None
    widths = _get(block, "fraction_widths")
    step: "fractions.Fraction | None" = None
    if _get(block, "integer_valued") is True:
        step = fractions.Fraction(1)
    elif isinstance(widths, dict) and len(widths) == 1:
        for key in widths:
            places = number_after(key, "") if isinstance(key, str) else None
            if places is not None:
                step = fractions.Fraction(1, 10 ** places)
    if step is None:
        step = (high - low) / 4095
    codes = round((high - low) / step)
    if codes < 1:
        return None
    return Grid(f"{_get(block, 'name')}", step, low, int(codes))


def band_edges(ladder: rules.Ladder, block: "dict[str, object]", level: int, band: int) -> "tuple[fractions.Fraction | None, fractions.Fraction | None, bool]":
    """A band's published lower and upper edge at `level` (None where open), and whether it is a value band."""
    names: "list[object]" = []
    for place in range(len(ladder.l0)):
        if ladder.maps[level][place] == band:
            names += list(ladder.l0[place])
    if not names or not all(isinstance(name, tuple) and len(name) == 2 for name in names):
        return None, None, False
    first = names[0]
    last = names[-1]
    low = rung_of(block, first[0]) if isinstance(first, tuple) else None
    high = rung_of(block, last[1]) if isinstance(last, tuple) else None
    return low, high, True


def spans_two(ladder: rules.Ladder, block: "dict[str, object]", level: int, grid: "Grid | None") -> bool:
    """Every band at `level` spans two or more published readings (4.6c.5 (e) item 2).

    A band `[low, high)` holds the readings from `low` up to and not
    including `high`, so it spans two only where its edges stand MORE than
    one grid step apart: `[7, 8)` at a step of 1 holds 7 alone (Codex's
    review of lane GRa, item 7).
    """
    step = grid.step if grid is not None else fractions.Fraction(1)
    for band in range(ladder.counts[level]):
        low, high, valued = band_edges(ladder, block, level, band)
        if not valued:
            return False
        if low is not None and high is not None and high - low <= step:
            return False
    return True


def class_witness(key_read: bool, spans: bool, threshold_plus_one: int) -> "tuple[int | None, bool]":
    """The class witness a row family's child asks (4.6c.5 (e)): what `V` and `V_K` must reach, and whether `V` is read.

    Item 1: a column the KEY test reads keeps `V` and `V_K` at least
    `T + 1`. Item 2: a FINE number or date column keeps `V_K` alone, which
    every world gives where every band spans two readings (`spans`); where
    one does not, the floored split's patterns must give it (Codex's
    review of lane GRa, item 7: that fallback read no witness). None where
    no witness is asked.
    """
    if key_read:
        return threshold_plus_one, True
    if not spans:
        return threshold_plus_one, False
    return None, False


def key_read(block: "dict[str, object]") -> bool:
    """Whether the KEY test reads a column (4.6c.6 (a)): a label or binary column, or a number column that is not FINE."""
    role = _get(block, "role")
    if role in rules.LABEL_ROLES:
        return True
    return role in rules.ORDERED_ROLES and role != rules.ROLE_DATETIME and not moments.fine(block)


def threshold(census: Census, floor: int) -> int:
    """`T = max(f - 1, floor(N2 / 100))` where the census publishes `N2`, else `f - 1` (4.6c.5 (a))."""
    if census.lo >= 2:
        return max(floor - 1, (census.patients - census.bands[0]) // 100)
    return floor - 1


def own_mean_edges(derived_ladder: rules.Ladder, edges: "list[fractions.Fraction]", level: int) -> "list[fractions.Fraction]":
    """An own mean's edges at its level `level` in `G`: the lower edge of each of its bands there but the first."""
    out: "list[fractions.Fraction]" = []
    seen: "set[int]" = set()
    for band in range(derived_ladder.counts[0]):
        coarse = derived_ladder.maps[level][band]
        if coarse in seen:
            continue
        seen |= {coarse}
        if band and band - 1 < len(edges):
            out += [edges[band - 1]]
    return out


def restriction_for(
    kind: str,
    place: int,
    child: rules.Ladder,
    block: "dict[str, object]",
    level: int,
    grid: "Grid | None",
    edges: "list[fractions.Fraction]",
) -> Restriction:
    """What a derived column asks of its source's patterns at the child's `level` (4.6c.2 (c)), from published facts."""
    value_bands = tuple(band_edges(child, block, level, band)[2] for band in range(child.counts[level]))
    if kind == FIRST_DATE:
        return Restriction(FIRST_DATE, place, (), (), None, value_bands)
    ranges: "list[tuple[int, int]]" = []
    if grid is not None:
        for band in range(child.counts[level]):
            low, high, _valued = band_edges(child, block, level, band)
            ranges += [code_range(grid, low, high)]
    return Restriction(OWN_MEAN, place, tuple(ranges), tuple(edges), grid, value_bands)
