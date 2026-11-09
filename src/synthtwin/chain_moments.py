"""The moment layer's inputs beside the chain: codes, offers, regions, sums and the witness's inputs (contract 4.6d; lane CHa, plan P4-D418).

NOT PUBLISHED. Contract 4.6d.10 names, for lane CHa, "the offers, regions,
codes, sums and the draw, and the witness's yield in refusals", and for
lane MPp the joint-space witness's INPUTS, never its decision. Lane
MPOL's GATE stays closed (4.6d.5 (h)): `procedure.classes` is empty, so
`moments` is `null` in every description and nothing here reaches one.
What is computed is handed back to the caller (`chain.describe`'s private
counts and the tools), for lane MPp's witness and lane CHo's oracle to
read.

WHAT IS HERE, by 4.6d's own sections:
- REGION COLUMNS (4.6d.1): eligible, FINE (4.6b.6: more than 20 different
  readings and at least 10 whose counts the column's own facts do not
  fix), and no derived, computed or rule column;
- THE CODES (4.6d.1, 4.6b.6): the linear code `floor(256 (x - lo) / (hi -
  lo))` clipped to 0..255, `lo` and `hi` the outermost published rung pair
  whose tails hold at least `f` readings (p01/p99 from 1,100 readings,
  else p05/p95, else p10/p90); a column SKEWED where its quantile skew
  `(p90 + p10 - 2 p50) / (p90 - p10)` is at least `skew_cut` (1/5) in
  magnitude takes the second code on the rungs' probability scale; all in
  exact fractions on the reading's own value;
- THE OFFERS (4.6d.1): `mean` in each HOME family (a family holding the
  column) where every cell whose band of the column holds no spread cell
  holds 0 or at least `2 f` rows (rule M3, all cells or none);
- THE REGIONS (4.6d.3): joined until nothing changes, each region column
  bringing every node holding it (its families and its `L0` totals);
- THE SUMS (4.6d.2): every whole number an option would publish, exact
  integers: each offered mean's code sum in each cell of its home family,
  and each `L0` band's code sum, on the linear code and, where the column
  is skewed, the second;
- THE WITNESS'S INPUTS (4.6d.4): each region's base members and, for each
  of its columns, the cut points of its reading line (`L0` edges, the
  ladder's other rungs, both codes' interval boundaries) and its own-fact
  readings, from which lane MPp builds the atoms and the joint space.

ARITHMETIC. Codes and cut points are exact fractions; sums are Python
integers. Nothing here is a library float.
"""

import dataclasses
import fractions

from synthtwin import chain_rules

# The chain's rules under the short name this module reads them by.
rules = chain_rules

SKEW_CUT = fractions.Fraction(1, 5)
CLASSES_OFFERED = ("mean",)
FINE_READINGS = 20
FREE_READINGS = 10
BIG_TAILS = 1100
PERCENT = {
    "p01": fractions.Fraction(1, 100), "p05": fractions.Fraction(5, 100), "p10": fractions.Fraction(10, 100),
    "p25": fractions.Fraction(25, 100), "p50": fractions.Fraction(50, 100), "p75": fractions.Fraction(75, 100),
    "p90": fractions.Fraction(90, 100), "p95": fractions.Fraction(95, 100), "p99": fractions.Fraction(99, 100),
}
LADDER_KEYS = ("p01", "p05", "p10", "p25", "p50", "p75", "p90", "p95", "p99")


def _get(mapping: "dict[str, object]", key: str) -> object:
    if key in mapping:
        return mapping[key]
    return None


def ordinal(role: str, value: object, block: "dict[str, object]") -> "fractions.Fraction | None":
    """A reading or a rung as an exact number in the column's own order (dates and clocks on their ordinal)."""
    if value is None:
        return None
    if role == rules.ROLE_DATETIME:
        if not isinstance(value, str):
            return None
        return _date_ordinal(value)
    if role == rules.ROLE_CLOCK:
        if isinstance(value, int) and not isinstance(value, bool):
            return fractions.Fraction(value)
        found = rules.rung_value(role, value, _get(block, "clock_form"))
        return fractions.Fraction(found) if isinstance(found, int) else None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return fractions.Fraction(value)


def _date_ordinal(text: str) -> "fractions.Fraction | None":
    """A canonical date, month, quarter or stamp as a whole number in its own unit, exactly."""
    if not isinstance(text, str):
        raise TypeError("a canonical date is text")
    figures = [character for character in text if "0" <= character <= "9"]
    if len(text) >= 7 and text[4:6] == "-Q":
        return fractions.Fraction(4 * int(text[0:4]) + int(text[6]) - 1)
    if len(figures) < 6:
        return None
    year = int(text[0:4])
    month = int(text[5:7])
    if len(text) == 7:
        return fractions.Fraction(12 * year + month - 1)
    days = _days(year, month, int(text[8:10]))
    if len(text) <= 10:
        return fractions.Fraction(days)
    return fractions.Fraction(86400 * days + 3600 * int(text[11:13]) + 60 * int(text[14:16]) + int(text[17:19]))


def _days(year: int, month: int, day: int) -> int:
    """Days from the civil epoch (Howard Hinnant's algorithm), exact."""
    shifted = year - 1 if month <= 2 else year
    era = shifted // 400
    year_of_era = shifted - era * 400
    day_of_year = (153 * (month + (-3 if month > 2 else 9)) + 2) // 5 + day - 1
    day_of_era = year_of_era * 365 + year_of_era // 4 - year_of_era // 100 + day_of_year
    return era * 146097 + day_of_era - 719468


@dataclasses.dataclass(frozen=True)
class Codes:
    """A region column's codes (4.6d.2's `codes` entry, with the values it reads)."""

    column: str
    lo: str
    hi: str
    p50: str
    second: "tuple[str, ...] | None"
    lo_value: fractions.Fraction
    hi_value: fractions.Fraction
    rungs: "tuple[tuple[fractions.Fraction, fractions.Fraction, fractions.Fraction], ...]"


def readings_of(block: "dict[str, object]") -> int:
    """The readings a number, date or clock column lays out (`K`)."""
    role = f"{_get(block, 'role')}"
    present = _get(block, "n_present")
    present_count = present if isinstance(present, int) else 0
    if role in (rules.ROLE_COUNT, rules.ROLE_CONTINUOUS, rules.ROLE_AFFIXED):
        used = _get(block, "n_used_in_statistics")
        return used if isinstance(used, int) else 0
    if role == rules.ROLE_COMPOUND:
        numbers = _get(block, "n_numeric_cells")
        return numbers if isinstance(numbers, int) else 0
    unparsed = _get(block, "n_unparsed")
    return present_count - (unparsed if isinstance(unparsed, int) else 0)


def fine(block: "dict[str, object]") -> bool:
    """FINE (4.6b.6, rule M1): more than 20 different readings, at least 10 whose counts its own facts do not fix."""
    role = f"{_get(block, 'role')}"
    if role not in rules.ORDERED_ROLES:
        return False
    distinct = _get(block, "n_distinct_values")
    if not isinstance(distinct, int):
        distinct = _get(block, "n_distinct")
    if not isinstance(distinct, int) or distinct <= FINE_READINGS:
        return False
    fixed = 0
    named_rows = 0
    mode_count = _get(block, "mode_count")
    mode = _get(block, "mode")
    if isinstance(mode_count, int) and not isinstance(mode_count, bool) and mode is not None:
        fixed += 1
        named_rows += mode_count
    n_zero = _get(block, "n_zero")
    if isinstance(n_zero, int) and not isinstance(n_zero, bool) and n_zero != 0:
        fixed += 1
        if mode != 0:
            named_rows += n_zero
        elif isinstance(mode_count, int) and mode_count == n_zero:
            fixed -= 1
    # Where the readings left beside the named ones number exactly the
    # values left, each of those values holds one row: its count is fixed
    # (Codex's item 7 on repair 1: 600 readings of 600 different values
    # were read as fine).
    if readings_of(block) - named_rows == distinct - fixed:
        return False
    tails = _get(block, "tails")
    if isinstance(tails, dict):
        for key in tails:
            side = tails[key]
            if isinstance(side, dict):
                values = _get(side, "values")
                fixed += len(values) if isinstance(values, list) else 0
    heaped = _get(block, "heaped")
    if isinstance(heaped, list):
        fixed += len(heaped)
    return distinct - fixed >= FREE_READINGS


def codes_of(block: "dict[str, object]") -> "Codes | None":
    """A FINE column's codes: its clip, its median and, where it is skewed, the second code's rungs."""
    role = f"{_get(block, 'role')}"
    rungs = rules.rung_ladder(block)
    if rungs is None:
        return None
    readings = readings_of(block)
    pairs = (("p01", "p99"), ("p05", "p95"), ("p10", "p90"))
    start = 0 if readings >= BIG_TAILS else 1
    chosen = None
    for low, high in pairs[start:]:
        low_value = ordinal(role, _get(rungs, low), block)
        high_value = ordinal(role, _get(rungs, high), block)
        if low_value is not None and high_value is not None:
            chosen = (low, high, low_value, high_value)
            break
    median = ordinal(role, _get(rungs, "p50"), block)
    if chosen is None or median is None:
        return None
    low, high, low_value, high_value = chosen
    p10 = ordinal(role, _get(rungs, "p10"), block)
    p90 = ordinal(role, _get(rungs, "p90"), block)
    second: "tuple[str, ...] | None" = None
    steps: "list[tuple[fractions.Fraction, fractions.Fraction, fractions.Fraction]]" = []
    if p10 is not None and p90 is not None and p10 != p90:
        skew = (p90 + p10 - 2 * median) / (p90 - p10)
        if abs(skew) >= SKEW_CUT:
            keys = [key for key in _rung_keys(rungs) if PERCENT[low] <= _percent(key) <= PERCENT[high]]
            second_keys: "list[str]" = []
            for key in keys:
                value = ordinal(role, _get(rungs, key), block)
                if value is None:
                    continue
                if steps and steps[-1][0] == value:
                    held = steps[-1]
                    steps[-1] = (held[0], held[1], _percent(key))
                else:
                    steps += [(value, _percent(key), _percent(key))]
                second_keys += [key]
            second = tuple(second_keys)
    return Codes(f"{_get(block, 'name')}", low, high, "p50", second, low_value, high_value, tuple(steps))


def code_clip(block: "dict[str, object]") -> "tuple[float, float] | None":
    """A FINE column's code clip `(lo, hi)` as binary64 values, for the generator's polish (lane MPg).

    The values `codes_of` reads from the published rungs, each the exact
    value of a published binary64 number, so the conversion is exact and
    `chain_walk.value_code` gives the code `linear_code` gives. None where
    the column takes no code.
    """
    found = codes_of(block) if fine(block) else None
    if found is None:
        return None
    low = found.lo_value
    high = found.hi_value
    return low.numerator / low.denominator, high.numerator / high.denominator


def _percent(key: str) -> fractions.Fraction:
    """A rung key's probability: `p05` is 5/100."""
    if not isinstance(key, str):
        raise TypeError("a rung key is text")
    return fractions.Fraction(int(key[1:]), 100)


def _rung_keys(rungs: "dict[str, object]") -> "list[str]":
    """Every published rung key `p01` to `p99`, in increasing percent."""
    keys: "list[tuple[int, str]]" = []
    for key in rungs:
        text = f"{key}"
        if len(text) == 3 and text[0] == "p" and "0" <= text[1] <= "9" and "0" <= text[2] <= "9":
            keys += [(int(text[1:]), text)]
    return [pair[1] for pair in sorted(keys)]


def linear_code(codes: Codes, value: fractions.Fraction) -> int:
    """`min(255, max(0, floor(256 (x - lo) / (hi - lo))))`, 0 where `lo` equals `hi`."""
    if codes.hi_value == codes.lo_value:
        return 0
    scaled = 256 * (value - codes.lo_value) / (codes.hi_value - codes.lo_value)
    return min(255, max(0, scaled.numerator // scaled.denominator))


def position(codes: Codes, value: fractions.Fraction) -> fractions.Fraction:
    """A reading's place on the rungs' probability scale (4.6d.1): a heap at the middle of its rungs."""
    steps = codes.rungs
    if value <= steps[0][0]:
        return (steps[0][1] + steps[0][2]) / 2
    if value >= steps[-1][0]:
        return (steps[-1][1] + steps[-1][2]) / 2
    for at in range(len(steps)):
        if value == steps[at][0]:
            return (steps[at][1] + steps[at][2]) / 2
        if at + 1 < len(steps) and steps[at][0] < value < steps[at + 1][0]:
            span = steps[at + 1][0] - steps[at][0]
            return steps[at][2] + (value - steps[at][0]) / span * (steps[at + 1][1] - steps[at][2])
    return (steps[-1][1] + steps[-1][2]) / 2


def second_code(codes: Codes, value: fractions.Fraction) -> int:
    """The second code: `floor(256 (pos - P_lo) / (P_hi - P_lo))` clipped to 0..255."""
    if codes.second is None or not codes.rungs:
        return 0
    low = PERCENT[codes.lo]
    high = PERCENT[codes.hi]
    scaled = 256 * (position(codes, value) - low) / (high - low)
    return min(255, max(0, scaled.numerator // scaled.denominator))


# -- OFFERS, REGIONS AND SUMS ------------------------------------------------


def pure_bands(scale: rules.Ladder, level: int) -> "set[int]":
    """The bands of a level holding no spread cell (every `L0` band inside it a value band without spread)."""
    spread_l0 = {
        at for at in range(len(scale.l0)) if any(not isinstance(name, tuple) or len(name) != 2 for name in scale.l0[at])
    }
    out: "set[int]" = set(range(scale.counts[level]))
    for at in spread_l0:
        out = out - {scale.maps[level][at]}
    return out


def offers_of(
    families: "list[rules.Family]",
    scales: "dict[str, rules.Ladder]",
    region_columns: "list[str]",
    floor: int,
) -> "list[tuple[str, int]]":
    """Every offered `mean`: (column, home family index), where rule M3 holds in that family."""
    out: "list[tuple[str, int]]" = []
    for name in region_columns:
        for at in range(len(families)):
            family = families[at]
            held = rules.members(family)
            place = -1
            for member in range(len(held)):
                if held[member][0] == name:
                    place = member
            if place < 0:
                continue
            level = held[place][1]
            pure = pure_bands(scales[name], level)
            sizes = rules.radices(family, scales)
            fits = True
            for index in range(len(family.table)):
                parts = rules.cell_parts(index, sizes)
                if parts[place] in pure and 0 < family.table[index] < 2 * floor:
                    fits = False
                    break
            if fits:
                out += [(name, at)]
    return out


def regions_of(
    families: "list[rules.Family]",
    offers: "list[tuple[str, int]]",
) -> "list[tuple[tuple[str, ...], tuple[int, ...]]]":
    """The regions (4.6d.3): each column with an offered class brings every node holding it; joined till nothing changes.

    Each region is (its columns in the order offered, its family indices in
    chain order); a column's `L0` totals node is implied by the column.
    """
    groups: "list[tuple[set[str], set[int]]]" = []
    for name, _at in offers:
        nodes = {at for at in range(len(families)) if name in {one for one, _level in rules.members(families[at])}}
        groups += [({name}, nodes)]
    changed = True
    while changed:
        changed = False
        for first in range(len(groups)):
            for second in range(first + 1, len(groups)):
                if groups[first][0] & groups[second][0] or groups[first][1] & groups[second][1]:
                    merged = (groups[first][0] | groups[second][0], groups[first][1] | groups[second][1])
                    groups = groups[:first] + [merged] + groups[first + 1 : second] + groups[second + 1 :]
                    changed = True
                    break
            if changed:
                break
    return [(tuple(sorted(columns)), tuple(sorted(nodes))) for columns, nodes in groups]


def at_level(codes: "bytes | list[int]", mapping: "tuple[int, ...] | list[int]") -> "bytes | list[int]":
    """Each `L0` code read through a ladder's map to a coarser level: one byte a row where every result fits one (lane CHs, plan P4-D462)."""
    if not mapping or max(mapping) < 256:
        return bytes(mapping[code] for code in codes)
    return [mapping[code] for code in codes]


def _level_of(
    held: "tuple[bytes | list[int], bytes | list[int] | None, bytes | list[int] | None]",
    scale: rules.Ladder,
    level: int,
) -> "bytes | list[int]":
    """A column's codes at `level`: held, or read from its `L0` codes through the ladder's map (the same codes)."""
    found = held[level]
    if found is not None:
        return found
    return at_level(held[0], scale.maps[level])


def sums_of(
    families: "list[rules.Family]",
    scales: "dict[str, rules.Ladder]",
    level_codes: "dict[str, tuple[bytes | list[int], bytes | list[int] | None, bytes | list[int] | None]]",
    value_codes: "dict[str, tuple[bytes, bytes | None, bytearray]]",
    offers: "list[tuple[str, int]]",
) -> "list[dict[str, object]]":
    """Every whole number the offered options would publish: cell sums of each offered mean, and band sums.

    `value_codes[column]` holds each tabled row's linear code, its second
    code (or None), and a flag a row a reading. Each sum names its class,
    column, code, family, cell and band (4.6d.2's fields).
    """
    out: "list[dict[str, object]]" = []
    for name, at in offers:
        family = families[at]
        held = rules.members(family)
        sizes = rules.radices(family, scales)
        place = 0
        for member in range(len(held)):
            if held[member][0] == name:
                place = member
        pure = pure_bands(scales[name], held[place][1])
        streams = [_level_of(level_codes[member], scales[member], level) for member, level in held]
        linear, second, has = value_codes[name]
        for which, codes in (("L", linear), ("S", second)):
            if codes is None:
                continue
            totals = [0] * len(family.table)
            for row in range(len(has)):
                if not has[row]:
                    continue
                parts = [streams[member][row] for member in range(len(held))]
                if parts[place] not in pure:
                    continue
                cell = 0
                for member in range(1, len(held)):
                    cell = cell * sizes[member] + parts[member]
                totals[cell * sizes[0] + parts[0]] += codes[row]
            for index in range(len(totals)):
                parts_of = rules.cell_parts(index, sizes)
                if parts_of[place] in pure and family.table[index]:
                    out += [{"band": None, "cell": index, "class": "mean", "codes": [which], "columns": [name],
                             "family": at, "powers": [1], "value": totals[index]}]
    for name in sorted({name for name, _at in offers}):
        linear, second, has = value_codes[name]
        scale = scales[name]
        for which, codes in (("L", linear), ("S", second)):
            if codes is None:
                continue
            totals = [0] * len(scale.totals)
            first_level = level_codes[name][0]
            for row in range(len(has)):
                if has[row]:
                    totals[first_level[row]] += codes[row]
            for band in range(len(totals)):
                out += [{"band": band, "cell": None, "class": "band", "codes": [which], "columns": [name],
                         "family": None, "powers": [1], "value": totals[band]}]
    return out


def cut_points(codes: Codes, block: "dict[str, object]", scale: rules.Ladder) -> "list[fractions.Fraction]":
    """The witness's input for one column: every boundary a published fact draws on its reading line (4.6d.1's atoms).

    The `L0` edges, the ladder's published rungs, each code's interval
    boundaries (both codes), in increasing order, each once. With the
    column's `L0` bands and its own-fact readings, lane MPp cuts the
    atoms from these.
    """
    role = f"{_get(block, 'role')}"
    rungs = rules.rung_ladder(block) or {}
    out: "set[fractions.Fraction]" = set()
    for key in rungs:
        value = ordinal(role, rungs[key], block)
        if value is not None:
            out = out | {value}
    span = codes.hi_value - codes.lo_value
    if span:
        for k in range(1, 256):
            out = out | {codes.lo_value + span * k / 256}
    if codes.second is not None and len(codes.rungs) >= 2:
        low = PERCENT[codes.lo]
        high = PERCENT[codes.hi]
        for k in range(1, 256):
            target = low + (high - low) * k / 256
            found = _inverse(codes, target)
            if found is not None:
                out = out | {found}
    return sorted(out)


def _inverse(codes: Codes, target: fractions.Fraction) -> "fractions.Fraction | None":
    """The reading whose position is `target`, on the open stretch between two rungs, or None at a rung."""
    steps = codes.rungs
    for at in range(len(steps) - 1):
        low = steps[at][2]
        high = steps[at + 1][1]
        if low < target < high:
            return steps[at][0] + (target - low) / (high - low) * (steps[at + 1][0] - steps[at][0])
    return None


def own_readings(block: "dict[str, object]") -> "list[object]":
    """The readings whose counts the column's own facts fix: the mode, zero, heaps and tail values."""
    out: "list[object]" = []
    if isinstance(_get(block, "mode_count"), int) and _get(block, "mode") is not None:
        out += [_get(block, "mode")]
    if isinstance(_get(block, "n_zero"), int) and _get(block, "n_zero") != 0:
        out += [0.0]
    tails = _get(block, "tails")
    if isinstance(tails, dict):
        for key in tails:
            side = tails[key]
            if isinstance(side, dict) and isinstance(_get(side, "values"), list):
                values = _get(side, "values")
                if isinstance(values, list):
                    out += values
    return out


# -- RULE B: THE MOMENTS RELEASED (contract 4.6d.0, plan P4-D455) ------------
#
# The owner's rule B of 2026-11-02 (bc-design ruling R13): a moment between
# columns is published where it is computed over at least `f` people and
# every count it implies DIRECTLY is 0 or at least `f`, rounded to the
# stated units below; no proof beyond that. What is computed here, in
# Python integers only, from each tabled row's code:
# - a NUMBER is an eligible FINE column of a number role, read on its
#   linear code (4.6d.1: clipped to the outermost published rungs whose
#   tails hold at least `f` readings, so no tail value enters a moment);
# - a BINARY is an eligible column of the binary role whose `L0` holds
#   exactly two value bands, each one published level, read 0 and 1 in
#   that order;
# - a GROUPING column is any eligible column, read on its `L1` bands, or,
#   where every `L1` band cannot pass, on its published `L2` bands.
# Published: each number's and binary's own moments (`columns`); the
# correlation of every pair of numbers, on its grid of Fisher's z, with
# the pair's own two spreads over the rows holding both where those rows
# are fewer than either column's readings (`correlations`); and the
# mean and spread of a number, or the share of a binary's second level,
# within every band of a grouping column, for the PARTNERS grouping
# columns with the largest share of the column's spread between those
# bands (`within`), all bands or none. Slopes are derived from these and
# never published apart (4.6d.0 (1)).
#
# THE UNITS (4.6d.0 (3)): tenths of a code for a mean and for a band's
# spread, thousandths of a code for a column's own spread and a pair's
# spreads (they feed a slope, `r * sd_y / sd_x`, whose rounding grows as
# 1 / (1 - r * r) near a tie), and ten-thousandths for a share, each made
# one decimal place finer for every 100-fold, or part of one, that the
# moment's own count exceeds the table floor's 20,000 rows (`unit`), so
# the rounding stays the same part of the sampling error at every size. A correlation is rounded on Fisher's z, in
# ten-thousandths of z at 20,000 rows or fewer and finer by the same rule,
# and published as the hyperbolic tangent of that grid point, printed to 12
# decimals: z's sampling error is about 1 / sqrt(n) at every r, where r's
# is (1 - r * r) / sqrt(n), so a fixed step of r near |r| = 1 would be
# several standard errors, and a step of z is the same part of one at
# every r. The step is a tenth of the first one built (LANE MPp RULINGS 7):
# a regression on two nearly collinear predictors amplifies r's rounding,
# and in thousandths of z a coefficient at a predictor correlation of 0.999
# moved by 2.6 to 2.9 of its own standard error. Every step is decided
# exactly in whole numbers (the logarithm and the exponential by their
# series in fixed point, the digits growing until the rounding is decided
# beyond the series' error), and the loader compares a published r with
# its grid point exactly, on the grid integer (`on_the_grid`).
#
# ONE PASS, NO LIST OF ROWS (4.6d.0 (5)): a column's band sums are read in
# one pass over the grouping's band codes, grouping by grouping, so the
# layer holds one column's sums at a time and no list of row numbers.

RULE_B = "B"
SCALE_MEAN = 10
SCALE_SPREAD = 10
SCALE_COLUMN_SPREAD = 1000
SCALE_SHARE = 10000
SCALE_FISHER_Z = 10000
SCALE_CORRELATION = 1000000000000
CORRELATION_TOP = 999999000000
UNIT_ROWS = 20000
PARTNERS = 24
KIND_NUMBER = "number"
KIND_BINARY = "binary"
LEVEL_BANDS = 1
LEVEL_COARSE = 2
_ABSENT = 256
_CELLS = 257


@dataclasses.dataclass(frozen=True)
class Released:
    """One number or binary column read for rule B: one value and one flag a tabled row (a row without a reading holds 0)."""

    name: str
    kind: str
    values: bytes
    present: bytearray


@dataclasses.dataclass(frozen=True)
class Grouping:
    """One eligible column read on its `L1` bands: a band a tabled row, the published totals, W1's marks.

    `small` holds the `L1` bands holding an own-fact group of 1 to `f - 1`
    rows (4.6b.3's list, as `chain.describe` reads it); `coarsest[g]` is
    the `L2` band holding `L1` band `g`.
    """

    name: str
    bands: "bytes | list[int]"
    totals: "tuple[int, ...]"
    small: "frozenset[int]"
    coarsest: "tuple[int, ...]"
    # Lane CHs (plan P4-D462): a grouping may hand its `L0` codes and the
    # `L0` to `L1` map instead of its bands; `released` then reads its
    # bands one grouping at a time (the same bands), so the groupings'
    # bands are never held all at once.
    l0: "bytes | list[int] | None" = None
    to_bands: "tuple[int, ...]" = ()


def binary_levels(ladder: rules.Ladder) -> "tuple[int, int] | None":
    """A binary's two `L0` value bands, each one published level, in band order; None where it has others.

    Rule B reads such a column 0 and 1 (contract 4.6d.0); a binary whose
    `L0` also holds a pool, an `other` or a `labels` band, or whose two
    levels the merge joined, is no binary there.
    """
    found: "list[int]" = []
    for at in range(len(ladder.l0)):
        band = ladder.l0[at]
        if len(band) == 1 and band[0] == rules.MISSING:
            continue
        if len(band) != 1 or not isinstance(band[0], tuple) or len(band[0]) != 1:
            return None
        found += [at]
    if len(found) != 2:
        return None
    return found[0], found[1]


def unit(scale: int, n: int) -> int:
    """`scale`, one decimal place finer for each 100-fold, or part of one, that the count `n` exceeds 20,000 (contract 4.6d.0 (3))."""
    out = scale
    reach = UNIT_ROWS
    while n > reach:
        out *= 10
        reach *= 100
    return out


def _isqrt(value: int) -> int:
    """The largest whole number whose square is at most `value` (Newton's method in integers)."""
    if value < 0:
        raise ValueError("a square root of a negative number")
    if value < 2:
        return value
    bits = 0
    rest = value
    while rest:
        rest >>= 1
        bits += 1
    guess = 1 << ((bits + 1) // 2)
    while True:
        better = (guess + value // guess) // 2
        if better >= guess:
            return guess
        guess = better


def rounded_ratio(numerator: int, denominator: int, scale: int) -> int:
    """`numerator / denominator` in units of `1 / scale`, half away from nought, exactly."""
    if denominator <= 0:
        raise ValueError("a ratio over a positive count")
    sign = -1 if numerator < 0 else 1
    size = abs(numerator)
    return sign * ((2 * scale * size + denominator) // (2 * denominator))


def rounded_root(numerator: int, denominator: int, scale: int) -> int:
    """`sqrt(numerator / denominator)` in units of `1 / scale`, half up, exactly."""
    if denominator <= 0 or numerator < 0:
        raise ValueError("a root of a non-negative ratio")
    doubled = _isqrt((4 * scale * scale * numerator) // denominator)
    return (doubled + 1) // 2


def spread_top(n: int, scale: int) -> int:
    """The largest sample spread (divisor `n - 1`) `n` codes of 0 to 255 can hold, rounded as a spread is, in units of `1 / scale`.

    Half the readings at 0 and half at 255 (`n // 2` and `n - n // 2`):
    the squared deviations total `(n // 2) * (n - n // 2) * 255 ** 2 / n`,
    so the spread is `127.5 * sqrt(n / (n - 1))` for an even count, more
    than half the code's range (Codex's band of twelve, six readings at 0
    and six at 255: 133.17). Rounding is monotone, so no published spread
    of `n` codes exceeds this.
    """
    if n < 2:
        raise ValueError("a spread needs two readings")
    low = n // 2
    return rounded_root(low * (n - low) * 255 * 255, n * (n - 1), scale)


def _halvings(top: int, bottom: int) -> int:
    """The largest `k` with `bottom * 2 ** k <= top`, for whole numbers `top >= bottom > 0` (a power of two that fits)."""
    shift = 0
    while (bottom << (shift + 1)) <= top:
        shift += 1
    return shift


def _atanh_fixed(numerator: int, denominator: int, one: int) -> int:
    """`atanh(numerator / denominator)` times `one`, for a ratio in 0 to 1/3, within two units a term of its series."""
    power = numerator * one // denominator
    square_top = numerator * numerator
    square_bottom = denominator * denominator
    total = 0
    term = 1
    while power:
        total += power // term
        power = power * square_top // square_bottom
        term += 2
    return total


def _half_log_units(top: int, bottom: int, scale: int, nearest: bool) -> int:
    """`ln(top / bottom) / 2` times `scale`, for whole numbers `top >= bottom > 0`, rounded half up (`nearest`) or down, exactly."""
    digits = 60
    while True:
        one = int(10**digits)
        shift = _halvings(top, bottom)
        rest = bottom << shift
        doubled = shift * 2 * _atanh_fixed(1, 3, one) + 2 * _atanh_fixed(top - rest, top + rest, one)
        value = doubled * scale + (one if nearest else 0)
        units = value // (2 * one)
        edge = value - 2 * one * units
        if min(edge, 2 * one - edge) > ((4 + 4 * shift) * (digits + 6) + 8) * scale:
            return units
        digits += 40


def _exp_fixed(top: int, bottom: int, one: int) -> "tuple[int, int]":
    """`exp(top / bottom)` times `one` for `top / bottom >= 0`, below the true value by at most the second number returned."""
    term = one
    total = one
    step = 1
    while term:
        term = term * top // (bottom * step)
        total += term
        step += 1
    return total, (step + 2) * (total // one + 2)


def tanh_units(units: int, scale: int) -> int:
    """`tanh(units / scale)` in units of `1 / SCALE_CORRELATION` (12 decimals), half away from nought, exactly."""
    sign = -1 if units < 0 else 1
    size = abs(units)
    if size == 0:
        return 0
    digits = 60
    while True:
        one = int(10**digits)
        grown, error = _exp_fixed(2 * size, scale, one)
        top = (grown - one) * SCALE_CORRELATION
        bottom = grown + one
        value = 2 * top + bottom
        printed = value // (2 * bottom)
        edge = value - 2 * bottom * printed
        if min(edge, 2 * bottom - edge) * one > (error + 1) * SCALE_CORRELATION * bottom:
            return sign * printed
        digits += 40


def fisher_z_units(cross: int, first: int, second: int, scale: int) -> int:
    """Fisher's z of `r = cross / sqrt(first * second)`, `atanh(r)`, in units of `1 / scale`, half away from nought, exactly.

    Whole-number arithmetic only: with `S = sqrt(first * second)` and
    `c = |cross|`, `2 z = ln((S + c) ** 2 / (S ** 2 - c ** 2))`, its
    logarithm taken by halving to [1, 2) and the series of `atanh` in fixed
    point; the digits grow until the rounding is decided beyond the
    series' error. An exact linear tie (`c * c = S * S`) gives the grid's
    top (`correlation_top_units`).
    """
    if first <= 0 or second <= 0:
        raise ValueError("a correlation needs a spread in both columns")
    sign = -1 if cross < 0 else 1
    size = abs(cross)
    product = first * second
    top = correlation_top_units(scale)
    if size == 0:
        return 0
    if size * size >= product:
        return sign * top
    digits = 60
    while True:
        one = int(10**digits)
        upper = _isqrt(product * one * one) + size * one
        rest = (product - size * size) * one * one
        shift = _halvings(upper * upper, rest)
        bottom = rest << shift
        doubled = shift * 2 * _atanh_fixed(1, 3, one) + 2 * _atanh_fixed(upper * upper - bottom, upper * upper + bottom, one)
        value = doubled * scale
        units = (value + one) // (2 * one)
        slack = ((4 + 4 * shift) * (digits + 6) + 8) * scale
        if min(value + one - 2 * one * units, 2 * one * (units + 1) - value - one) > slack:
            return sign * min(units, top)
        digits += 40


def correlation_top_units(scale: int) -> int:
    """The largest grid point of z, in units of `1 / scale`, whose tanh is at most 0.999999 (`CORRELATION_TOP`)."""
    return _half_log_units(SCALE_CORRELATION + CORRELATION_TOP, SCALE_CORRELATION - CORRELATION_TOP, scale, False)


def rounded_correlation(cross: int, first: int, second: int, n: int) -> int:
    """A pair's published r: Fisher's z rounded to its grid at `n` rows (`unit(SCALE_FISHER_Z, n)`), then tanh, in 12 decimals."""
    scale = unit(SCALE_FISHER_Z, n)
    return tanh_units(fisher_z_units(cross, first, second, scale), scale)


def on_the_grid(printed: int, n: int) -> bool:
    """A published r lies on its count's grid of z: it IS the tanh of a grid point printed to 12 decimals, compared on the grid integer.

    The grid point nearest the printed r's own z (`atanh(|r|)` in units of
    `1 / s`, half up, at most the grid's top) is printed again with
    `tanh_units` and must equal `|r|` exactly; where two neighbouring grid
    points print alike or the nearest one prints past `|r|` (only where the
    step is finer than the print near |r| = 0.999999, past 200,000,000
    rows), the walk goes on to the neighbour on `|r|`'s side, so every r the
    product writes loads and nothing else does. No tolerance (LANE MPp
    RULINGS 7 (2)): neighbouring grid points stand `(1 - r ** 2)` times the
    step apart in r, 2e-10 at the floor's ten-thousandths of z near
    |r| = 0.999999, so a tolerance of 1e-9 accepted values between them.
    A point of the first grid built, thousandths of z, is a point of this
    one (ten of its steps), so an r on that grid loads where it lies on
    this one and nowhere else.
    """
    size = abs(printed)
    if size > CORRELATION_TOP:
        return False
    scale = unit(SCALE_FISHER_Z, n)
    top = correlation_top_units(scale)
    point = min(_half_log_units(SCALE_CORRELATION + size, SCALE_CORRELATION - size, scale, True), top)
    found = tanh_units(point, scale)
    while found < size and point < top:
        point += 1
        found = tanh_units(point, scale)
    while found > size and point > 0:
        point -= 1
        found = tanh_units(point, scale)
    return found == size


def passes(count: int, floor: int) -> bool:
    """A count a moment implies directly may be published: 0, or at least the floor."""
    return count == 0 or count >= floor


def _spread(n: int, total: int, squares: int) -> int:
    """`n` times the sum of squared deviations: `n * squares - total ** 2`."""
    return n * squares - total * total


def column_sums(column: Released) -> "tuple[int, int, int]":
    """A column's readings, the total of their codes and of the codes' squares, in one pass."""
    found = band_sums(column, bytes(len(column.values)), 1)
    return found[0]


def band_sums(column: Released, bands: "bytes | list[int]", count: int) -> "list[tuple[int, int, int]]":
    """Each band's readings, code total and total of squared codes, from one pass over the rows (no list of rows kept)."""
    cells = [0] * (_CELLS * count)
    for band, value, has in zip(bands, column.values, column.present):
        cells[_CELLS * band + (value if has else _ABSENT)] += 1
    out: "list[tuple[int, int, int]]" = []
    for band in range(count):
        base = _CELLS * band
        n = total = squares = 0
        for value in range(_ABSENT):
            seen = cells[base + value]
            if seen:
                n += seen
                total += value * seen
                squares += value * value * seen
        out += [(n, total, squares)]
    return out


def column_moments(column: Released, floor: int, sums: "tuple[int, int, int] | None" = None) -> "tuple[dict[str, object] | None, str]":
    """A number's count, mean and spread on its code, or a binary's count and share; None with the reason refused."""
    n, total, squares = column_sums(column) if sums is None else sums
    if n < floor or n < 2:
        return None, "fewer than the floor"
    if column.kind == KIND_BINARY:
        if not (passes(total, floor) and passes(n - total, floor)):
            return None, "a level count of 1 to f - 1"
        return {"column": column.name, "kind": KIND_BINARY, "n": n, "share": rounded_ratio(total, n, unit(SCALE_SHARE, n))}, ""
    return {
        "column": column.name,
        "kind": KIND_NUMBER,
        "mean": rounded_ratio(total, n, unit(SCALE_MEAN, n)),
        "n": n,
        "sd": rounded_root(_spread(n, total, squares), n * (n - 1), unit(SCALE_COLUMN_SPREAD, n)),
    }, ""


def pair_moments(
    first: Released,
    second: Released,
    floor: int,
    first_sums: "tuple[int, int, int] | None" = None,
    second_sums: "tuple[int, int, int] | None" = None,
) -> "tuple[list[object] | None, str]":
    """The correlation of two numbers over the rows holding both: `[r, n]`, r on its count's grid of z, or None with the reason refused.

    Where those `n` rows are fewer than either column's readings, the
    entry also holds the pair's own two spreads over them, `[r, n, [sd of
    first, sd of second]]`, in the unit of `n` (`SCALE_COLUMN_SPREAD`), so
    a complete-case slope reads `r` times the pair's spread of one over
    the pair's spread of the other; where the pair holds every reading of
    both, the columns' own spreads are the pair's and nothing is added
    (contract 4.6d.0 (1)). A spread is a sum of squares: it implies no
    count. Counts implied directly, the four cells of the pair's presence table
    over the `T` tabled rows: `n` (both), each column's readings outside
    it (`n_x - n`, `n_y - n`) and the rows holding neither (`T - n_x - n_y
    + n`), each 0 or at least `f`. Where one column holds a reading on
    every tabled row, the other's readings outside the pair are 0 and its
    own rows outside them are its own unread count, which its own column
    entry already gives (`T - n`; a count a column publishes about itself,
    contract 4.6d.0 (2) reading R1 with P4-D363), so that count stands.
    """
    tabled = len(first.present)
    nx, sx_all, sxx_all = column_sums(first) if first_sums is None else first_sums
    ny, sy_all, syy_all = column_sums(second) if second_sums is None else second_sums
    if nx == tabled and ny == tabled:
        n, sx, sy, sxx, syy = tabled, sx_all, sy_all, sxx_all, syy_all
    elif ny == tabled:
        n, sx, sxx = nx, sx_all, sxx_all
        sy = sum(b for b, a in zip(second.values, first.present) if a)
        syy = sum(b * b for b, a in zip(second.values, first.present) if a)
    elif nx == tabled:
        n, sy, syy = ny, sy_all, syy_all
        sx = sum(a for a, b in zip(first.values, second.present) if b)
        sxx = sum(a * a for a, b in zip(first.values, second.present) if b)
    else:
        n = sum(a * b for a, b in zip(first.present, second.present))
        sx = sum(a for a, b in zip(first.values, second.present) if b)
        sy = sum(b for b, a in zip(second.values, first.present) if a)
        sxx = sum(a * a for a, b in zip(first.values, second.present) if b)
        syy = sum(b * b for b, a in zip(second.values, first.present) if a)
    if n < floor:
        return None, "fewer than the floor"
    if not ((passes(nx - n, floor) or nx == tabled) and (passes(ny - n, floor) or ny == tabled)):
        return None, "a count of 1 to f - 1"
    if not passes(tabled - nx - ny + n, floor):
        return None, "rows holding neither, 1 to f - 1"
    sxy = sum(a * b for a, b in zip(first.values, second.values))
    dx = _spread(n, sx, sxx)
    dy = _spread(n, sy, syy)
    if dx <= 0 or dy <= 0:
        return None, "no spread"
    found: "list[object]" = [rounded_correlation(n * sxy - sx * sy, dx, dy, n), n]
    if n < nx or n < ny:
        scale = unit(SCALE_COLUMN_SPREAD, n)
        found += [[rounded_root(dx, n * (n - 1), scale), rounded_root(dy, n * (n - 1), scale)]]
    return found, ""


def _interval(value: int, scale: int) -> "tuple[fractions.Fraction, fractions.Fraction]":
    """The values a non-negative published `value` in units of `1 / scale` was rounded from (half up): `value / scale` give or take half a unit."""
    half = fractions.Fraction(1, 2 * scale)
    centre = fractions.Fraction(value, scale)
    return max(centre - half, fractions.Fraction(0)), centre + half


def spreads_agree(groups: "list[list[int]]", n: int, spread: int) -> bool:
    """A number's published spread and its bands' counts, means and spreads satisfy the total-variance identity within the rounding.

    `(n - 1) * s ** 2 = sum((n_g - 1) * s_g ** 2) + sum(n_g * (m_g - m) ** 2)`,
    `m` the readings' mean, `sum(n_g * m_g) / n`, over the bands holding
    the column's `n` readings (`[n_g, mean, sd]`, a band of none `[0]`).
    Each published value stands for half a unit either side: the bands'
    within part takes the bounds of their spreads, the between part the
    bounds of each band's distance from the mean (a band's mean off by at
    most its half unit, `m` by at most the largest), the column's part the
    bounds of its spread (`SCALE_COLUMN_SPREAD`); False where the two sides
    cannot meet (Codex's item 5 on repair 1: a spread of 751 written 0
    beside bands at 745 to 756). Exact, in fractions.
    """
    held = [group for group in groups if group[0]]
    if not held:
        return True
    within_low = within_high = fractions.Fraction(0)
    centres: "list[tuple[int, fractions.Fraction, fractions.Fraction]]" = []
    widest = fractions.Fraction(0)
    weighted = fractions.Fraction(0)
    for group in held:
        count = group[0]
        low, high = _interval(group[2], unit(SCALE_SPREAD, count))
        within_low += (count - 1) * low * low
        within_high += (count - 1) * high * high
        scale = unit(SCALE_MEAN, count)
        half = fractions.Fraction(1, 2 * scale)
        centre = fractions.Fraction(group[1], scale)
        centres += [(count, centre, half)]
        widest = max(widest, half)
        weighted += count * centre
    middle = weighted / n
    between_low = between_high = fractions.Fraction(0)
    for count, centre, half in centres:
        distance = abs(centre - middle)
        reach = half + widest
        near = max(distance - reach, fractions.Fraction(0))
        far = distance + reach
        between_low += count * near * near
        between_high += count * far * far
    low, high = _interval(spread, unit(SCALE_COLUMN_SPREAD, n))
    return within_high + between_high >= (n - 1) * low * low and within_low + between_low <= (n - 1) * high * high


def _bands_refused(kind: str, found: "list[tuple[int, int, int]]", totals: "list[int]", small: "frozenset[int]", floor: int) -> str:
    """Why a column's bands cannot all be published (contract 4.6d.0 (2)), or '' where they can."""
    for band in range(len(found)):
        n, total, _squares = found[band]
        if not (passes(n, floor) and passes(totals[band] - n, floor)):
            return "a count of 1 to f - 1"
        if kind == KIND_BINARY and not (passes(total, floor) and passes(n - total, floor)):
            return "a count of 1 to f - 1"
    if kind == KIND_BINARY:
        for band in sorted(small):
            n, total, _squares = found[band]
            if len([part for part in (total, n - total, totals[band] - n) if part]) < 2:
                return "RULE W1"
    return ""


def _band_groups(kind: str, found: "list[tuple[int, int, int]]") -> "tuple[list[list[int]], fractions.Fraction]":
    """The published groups of a column's bands, each in the unit of its own count, and the share of the spread between them."""
    groups: "list[list[int]]" = []
    n_all = total_all = squares_all = 0
    between = fractions.Fraction(0)
    for n, total, squares in found:
        n_all += n
        total_all += total
        squares_all += squares
        if n == 0:
            groups += [[0]]
            continue
        between += fractions.Fraction(total * total, n)
        if kind == KIND_BINARY:
            groups += [[n, rounded_ratio(total, n, unit(SCALE_SHARE, n))]]
        else:
            groups += [[n, rounded_ratio(total, n, unit(SCALE_MEAN, n)), rounded_root(_spread(n, total, squares), n * (n - 1), unit(SCALE_SPREAD, n))]]
    if not n_all:
        return groups, fractions.Fraction(0)
    between -= fractions.Fraction(total_all * total_all, n_all)
    whole = fractions.Fraction(_spread(n_all, total_all, squares_all), n_all)
    return groups, (between / whole if whole > 0 else fractions.Fraction(0))


def within_moments(
    column: Released,
    grouping: Grouping,
    floor: int,
) -> "tuple[list[list[int]] | None, fractions.Fraction, str, int]":
    """A column's moments in every band of a grouping column, all bands or none: its `L1` bands, else its `L2` bands.

    Returns the groups (`[n, mean, sd]` for a number, `[n, share]` for a
    binary, `[0]` for a band holding none of its readings), the share of
    the column's spread between the bands (the partners' rank), the reason
    the `L1` bands were refused ('' where they stand), and the level read. Counts implied directly, each 0 or
    at least `f`: every band's readings `n_g` and its rows without one
    `T_g - n_g`; for a binary also each level's rows in each band. RULE W1
    (4.6b.3) for a binary: a band holding an own-fact group of the
    grouping column holds two of the binary's levels or its absence.
    Where the `L1` bands cannot all pass, the published `L2` bands
    (`coarsest`) are read under the same rule (a rare level or a rare
    blank spread over many narrow bands; contract 4.6d.0 (2)).
    """
    found = band_sums(column, grouping.bands, len(grouping.totals))
    why = _bands_refused(column.kind, found, list(grouping.totals), grouping.small, floor)
    if not why:
        groups, share = _band_groups(column.kind, found)
        return groups, share, "", LEVEL_BANDS
    count = max(grouping.coarsest) + 1 if grouping.coarsest else 0
    if len(set(grouping.coarsest)) >= len(found):
        return None, fractions.Fraction(0), why, LEVEL_BANDS
    folded = [[0, 0, 0] for _band in range(count)]
    totals = [0] * count
    for band in range(len(found)):
        at = grouping.coarsest[band]
        for part in range(3):
            folded[at][part] += found[band][part]
        totals[at] += grouping.totals[band]
    coarse = [(n, total, squares) for n, total, squares in folded]
    small = frozenset(grouping.coarsest[band] for band in grouping.small)
    if _bands_refused(column.kind, coarse, totals, small, floor):
        return None, fractions.Fraction(0), why, LEVEL_BANDS
    groups, share = _band_groups(column.kind, coarse)
    return groups, share, why, LEVEL_COARSE


def released(
    columns: "list[Released]",
    groupings: "list[Grouping]",
    floor: int,
) -> "tuple[dict[str, object] | None, dict[str, int]]":
    """The `moments` object rule B publishes (contract 4.6d.0), and the refusals counted by kind and reason.

    `columns` and `groupings` stand in schema order. None where nothing
    is published. The `within` entries are read grouping by grouping, one
    pass over the rows for each column, and ranked afterwards.
    """
    counts: "dict[str, int]" = {}

    def count(key: str) -> None:
        counts[key] = counts[key] + 1 if key in counts else 1

    entries: "list[dict[str, object]]" = []
    kept: "list[Released]" = []
    sums: "dict[str, tuple[int, int, int]]" = {}
    for column in columns:
        own = column_sums(column)
        entry, why = column_moments(column, floor, own)
        if entry is None:
            count(f"refused column: {why}")
            continue
        count(f"published column: {column.kind}")
        entries += [entry]
        kept += [column]
        sums[column.name] = own
    numbers = [column for column in kept if column.kind == KIND_NUMBER]
    triangle: "list[list[list[object] | None]]" = []
    for at in range(len(numbers)):
        line: "list[list[object] | None]" = []
        for other in range(at):
            first, second = numbers[at], numbers[other]
            pair, why = pair_moments(first, second, floor, sums[first.name], sums[second.name])
            count("published correlation" if pair is not None else f"refused correlation: {why}")
            line += [pair]
        triangle += [line]
    ranked: "dict[str, list[tuple[fractions.Fraction, int, dict[str, object]]]]" = {column.name: [] for column in kept}
    for place in range(len(groupings)):
        grouping = groupings[place]
        if grouping.l0 is not None:
            grouping = dataclasses.replace(grouping, bands=at_level(grouping.l0, grouping.to_bands), l0=None)
        for column in kept:
            if grouping.name == column.name:
                continue
            groups, share, why, level = within_moments(column, grouping, floor)
            if groups is None:
                count(f"refused within: {why}")
                continue
            if level == LEVEL_COARSE:
                count(f"within on the L2 bands: {column.kind}")
                count(f"L1 bands refused, L2 published: {why}")
            placed: "dict[str, object]" = {"by": grouping.name, "column": column.name, "groups": groups}
            if level == LEVEL_COARSE:
                placed["level"] = LEVEL_COARSE
            ranked[column.name] += [(-share, place, placed)]
    within: "list[dict[str, object]]" = []
    for column in kept:
        # Each grouping column stands once in a column's list, so the
        # ranking never compares two entries past their places.
        held = sorted(ranked[column.name])
        for _dropped in held[PARTNERS:]:
            count("not among the partners")
        for _place, chosen in sorted((place, chosen) for _share, place, chosen in held[:PARTNERS]):
            count(f"published within: {column.kind}")
            within += [chosen]
    if not entries:
        return None, counts
    return {
        "columns": entries,
        "correlations": triangle,
        "partners": PARTNERS,
        "rule": RULE_B,
        "scales": {
            "column_sd": SCALE_COLUMN_SPREAD,
            "correlation": SCALE_CORRELATION,
            "fisher_z": SCALE_FISHER_Z,
            "mean": SCALE_MEAN,
            "sd": SCALE_SPREAD,
            "share": SCALE_SHARE,
        },
        "within": within,
    }, counts
