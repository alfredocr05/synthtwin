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

from synthtwin import chain_rules as rules

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


def sums_of(
    families: "list[rules.Family]",
    scales: "dict[str, rules.Ladder]",
    level_codes: "dict[str, tuple[bytes | list[int], bytes | list[int], bytes | list[int]]]",
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
        streams = [level_codes[member][level] for member, level in held]
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
