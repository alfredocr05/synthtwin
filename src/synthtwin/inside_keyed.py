"""THE KEYED ZONE OF THE INSIDE RECORD: a long table whose rows are typed by a key, as a model kept on the protected computer (lane IN-4, plan P4-D499).

WHAT IT IS. A long table -- bedside charting, laboratory results,
medication orders, a question-and-answer export -- writes one measurement
a row, and a KEY column (an item, a test, a drug) says what the row's
value means: its scale, its unit, its words, the range printed beside it.
The strict description published such a value column key block by key
block, rounded, floored and held where a block looked like ages or record
numbers, and the twin wrote each row's value apart from its patient, its
time and the other cells of its row. The inside record stays on the
computer the real table is on (`inside`, plan P4-D495), so this zone
carries the table's keyed structure as a MODEL, never as data:

* `key`: the column that types the others (a label of `KEY_LEVELS_LEAST`
  to `KEY_LEVELS_MOST` levels moving within a person, the one that fixes
  or types the most other columns of the row; the first in the table's
  order on a tie);
* `census`: how many persons hold each number of rows (exact, never a
  person);
* `copies`: the rules between two columns of a row that need no key: a
  column equal to another wherever that one is a number, and one fixed
  spelling elsewhere (a numeric copy of a text result and its sentinel);
* for each key level (`levels`, at most `MODELLED_LEVELS_MOST` of them,
  the commonest), THE RULES INSIDE A ROW: the joint table of the row's
  label cells at that level (a unit, a device flag, a printed range: so
  each follows the key, and each other); every number column's MARGINAL
  at that level and, where a label sets the number's scale (a unit whose
  groups stand apart), in each of that label's groups: a value table of
  its written spellings, or a quantile function of `GRID` points with its
  written decimals, its censoring atoms (`<x`, `>x`) and its words as
  states; a pair of numbers written `a/b` as two marginals and the
  correlation of their normal scores; a flag that is a function of
  intervals of a number (a value outside its printed range) as its cut
  points; and THE LEVEL'S TRAJECTORY on the normal scores of its numbers:
  a trend over each person's own time, a person's share of the variance,
  and the lag-one correlation of a person's successive readings
  (moments, unbalanced and corrected for the lag, read on at most
  `FIT_ROWS` rows of whole persons).

A key level the description holds as possible record numbers whose values
do not repeat across persons, a level whose values read as dates, and a
column of more than `LABELS_MOST` spellings at a level are NOT modelled:
their rows keep the description's twin's cells. A level or a column the
description top-codes at 90 (an age, Safe Harbor) is written so here too.
The zone's size follows columns, levels and grids, never rows.

HOW THE TWIN READS IT, in two steps of `generation.generate_inside`
(the dates zone, lane IN-5, writes the dates between them): (1)
`persons_and_labels`: the twin's persons (the description's own made-up
keys) take the census's numbers of rows, each person's rows together, and
each row's label cells come from its key level's joint table (exact
shares, in an order the seed draws); (2) `numbers_and_rules`, on the time
axis the dates zone wrote: each row's numbers from its level's marginal,
in the order of a latent score that carries the trend, the person's level
and the lag, every pair and flag and copy by its rule. Every random
quantity comes from SplitMix64 words seeded by the twin's seed; the
arithmetic is binary64 `+ - * /` and `sqrt` in the order written, with the
shared module's logarithm and normal quantile, so a twin is the same on
every machine.

NOTHING HERE PRINTS A VALUE. The producer returns the zone, the
generator returns cells; neither writes a line.
"""

import dataclasses
import math
import typing

from synthtwin import chain_walk, inside_dates, inside_trajectories

ZONE = "keyed"
ZONE_VERSION = 1
KEY_LEVELS_LEAST = 3
KEY_LEVELS_MOST = 1000
MODELLED_LEVELS_MOST = 300
KEY_SAMPLE = 20000
FIXED_SHARE = 0.9
KEYED_SHARE = 0.5
MOVED_SHARE = 0.1
CONSTANT_SHARE = 0.95
NUMERIC_SHARE = 0.9
PAIR_SHARE = 0.95
LABELS_MOST = 200
TUPLES_MOST = 500
TABLE_MOST = 50
GRID = 1001
SCALE_LABELS_MOST = 10
SCALE_SHARE = 0.8
RULE_SHARE = 0.995
CUTS_MOST = 4
FIT_ROWS = 200000
FIT_ROWS_LEAST = 40
FIT_PERSONS_LEAST = 10
GATE_Z = 3.29
LAG_MOST = 0.95
LAG_LEAST = -0.5
TOP_CODE = 90
SECONDS_A_DAY = 86400.0
GAP_GRID = 201
GAP_MOVED = 0.1
GAP_LEAST = 20
AXIS_DAYS = "days"
AXIS_POSITION = "position"
KEPT_IDENTIFIER = "possible record numbers"
KEPT_DATES = "dates"
KEPT_RARE = "past the levels modelled"
_SEP = "\x1f"
_ZONE_KEYS = ("anchor", "axis", "census", "content", "copies", "key", "levels", "person", "rows", "version")


class KeyedError(ValueError):
    """The keyed zone cannot be read or applied (its record does not fit the twin it is asked to shape)."""


# -- cells ------------------------------------------------------------------------------------------------


def _text(cell: object) -> str:
    return cell if isinstance(cell, str) else ""


def _bare(cell: object) -> str:
    if not isinstance(cell, str):
        raise TypeError("synthtwin reads a table's cells as text only.")
    return cell.strip()


def _point_parts(body: object) -> "tuple[str, str, str]":
    """A number's written figures split at its point: before, the point, after."""
    if not isinstance(body, str):
        raise TypeError("synthtwin reads a table's cells as text only.")
    at = body.find(".")
    if at < 0:
        return body, "", ""
    return body[:at], ".", body[at + 1:]


def _slash_parts(text: object) -> "tuple[str, str, str]":
    if not isinstance(text, str):
        raise TypeError("synthtwin reads a table's cells as text only.")
    at = text.find("/")
    if at < 0:
        return text, "", ""
    return text[:at], "/", text[at + 1:]


def _joined(parts: "list[str]") -> str:
    """The parts written one after another with `_SEP` between them."""
    out = ""
    for at in range(len(parts)):
        out += (_SEP if at else "") + parts[at]
    return out


def _digits(text: str) -> bool:
    if not text:
        return False
    for character in text:
        if character < "0" or character > "9":
            return False
    return True


def plain_number(cell: object) -> "float | None":
    """A cell written as a plain decimal number (a sign, figures, a point; no exponent, no affix), else None."""
    text = _bare(cell)
    if not text:
        return None
    body = text[1:] if text[0] in "+-" else text
    if not body:
        return None
    whole, point, fraction = _point_parts(body)
    if point and not whole and not fraction:
        return None
    if whole and not _digits(whole):
        return None
    if fraction and not _digits(fraction):
        return None
    if not whole and not fraction:
        return None
    return float(text)


def atom_of(cell: object) -> "tuple[str, float] | None":
    """A censoring atom: `<x` or `>x` (a space allowed after the sign) with x a plain number, as ('<' or '>', x)."""
    text = _bare(cell)
    if len(text) < 2 or text[0] not in "<>":
        return None
    value = plain_number(text[1:])
    return None if value is None else (text[0], value)


def pair_of(cell: object) -> "tuple[str, str] | None":
    """A pair of plain numbers written `a/b`, as its two written parts, else None."""
    first, slash, second = _slash_parts(_bare(cell))
    if not slash or plain_number(first) is None or plain_number(second) is None:
        return None
    return first, second


def decimals_of(text: object) -> int:
    _whole, point, fraction = _point_parts(text)
    return len(fraction) if point else 0


def _position(cell: object) -> "float | None":
    """A number cell's place on its column's line: a plain number at itself, `<x` just below x, `>x` just above."""
    value = plain_number(cell)
    if value is not None:
        return value
    atom = atom_of(cell)
    if atom is None:
        return None
    step = abs(atom[1]) * 1e-9 + 1e-12
    return atom[1] - step if atom[0] == "<" else atom[1] + step


def _log_size(value: float) -> float:
    return chain_walk.natural_log(1.0 + abs(value))


def fold(level: object) -> str:
    """A key level as the description's key blocks name it: trimmed and lower-cased."""
    if not isinstance(level, str):
        raise TypeError("synthtwin reads a key level as text only.")
    return level.strip().lower()


# -- small statistics -------------------------------------------------------------------------------------


def _counts(cells: "list[str]") -> "dict[str, int]":
    out: "dict[str, int]" = {}
    for cell in cells:
        out[cell] = (out[cell] if cell in out else 0) + 1
    return out


def _commonest(counts: "dict[str, int]") -> "tuple[str, int]":
    best, most = "", -1
    for cell in sorted(counts):
        if counts[cell] > most:
            best, most = cell, counts[cell]
    return best, most


def _between_share(groups: "dict[str, list[float]]") -> float:
    """The share of the variance of the values that lies between the groups (groups of fewer than 3 values set aside)."""
    values: "list[float]" = []
    for name in sorted(groups):
        if len(groups[name]) >= 3:
            values += groups[name]
    if len(values) < 6:
        return 0.0
    mean = math.fsum(values) / len(values)
    total = math.fsum([(value - mean) * (value - mean) for value in values])
    if total <= 0.0:
        return 0.0
    between = 0.0
    for name in sorted(groups):
        group = groups[name]
        if len(group) >= 3:
            middle = math.fsum(group) / len(group)
            between += len(group) * (middle - mean) * (middle - mean)
    return between / total


def _spread_rows(rows: int, most: int) -> "list[int]":
    if rows <= most:
        return list(range(rows))
    return [(k * rows) // most for k in range(most)]


def _largest_remainders(weights: "list[int]", total: int) -> "list[int]":
    """Whole counts summing to `total` in the proportions of `weights` (largest remainders, ties to the first)."""
    whole = sum(weights)
    if whole <= 0 or total <= 0:
        return [0 for _weight in weights]
    counts = [(weight * total) // whole for weight in weights]
    left = total - sum(counts)
    order = [at for _rest, at in sorted((-((weights[at] * total) % whole), at) for at in range(len(weights)))]
    for place in range(left):
        counts[order[place % len(order)]] += 1
    return counts


def _shuffled(items: "list[typing.Any]", state: "list[int]") -> "list[typing.Any]":
    out = [item for item in items]
    for at in range(len(out) - 1, 0, -1):
        other = inside_trajectories.next_word(state) % (at + 1)
        out[at], out[other] = out[other], out[at]
    return out


# -- the producer -----------------------------------------------------------------------------------------


def _persons(cells: "list[str]") -> "tuple[list[int], int]":
    """Each row's person number (-1 for an empty cell) and the number of persons."""
    seen: "dict[str, int]" = {}
    out: "list[int]" = []
    for cell in cells:
        text = _bare(cell)
        if not text:
            out += [-1]
            continue
        if text not in seen:
            seen[text] = len(seen)
        out += [seen[text]]
    return out, len(seen)


def _repeats(cells: "list[str]") -> bool:
    """Whether a person's column could hold several rows of one person: some person number written twice."""
    seen: "dict[str, int]" = {}
    for cell in cells:
        text = _bare(cell)
        if text in seen:
            return True
        if text:
            seen[text] = 1
    return False


def _numeric_share(cells: "list[str]") -> float:
    present = 0
    numeric = 0
    for cell in cells:
        if not _bare(cell):
            continue
        present += 1
        if _position(cell) is not None:
            numeric += 1
    return numeric / present if present else 0.0


def _varies_within(keys: "list[str]", owners: "list[int]") -> bool:
    first: "dict[int, str]" = {}
    several: "dict[int, int]" = {}
    moved: "dict[int, int]" = {}
    for row in range(len(keys)):
        owner = owners[row]
        if owner < 0:
            continue
        if owner not in first:
            first[owner] = keys[row]
            continue
        several[owner] = 1
        if keys[row] != first[owner]:
            moved[owner] = 1
    return bool(several) and len(moved) >= 0.5 * len(several)


def _leading(cell: object) -> "float | None":
    """A cell's number: a plain number, a censoring atom's, or the number before a space and a word (`650 mg`)."""
    if not isinstance(cell, str):
        raise TypeError("synthtwin reads a table's cells as text only.")
    place = _position(cell)
    if place is not None:
        return place
    at = cell.strip().find(" ")
    return plain_number(cell.strip()[:at]) if at > 0 else None


def _by_level(key_cells: "list[str]", cells: "list[str]") -> "dict[str, list[str]]":
    by: "dict[str, list[str]]" = {}
    for row in range(len(cells)):
        level = key_cells[row]
        if level not in by:
            by[level] = []
        by[level] += [cells[row]]
    return by


def _typed_by(key_cells: "list[str]", cells: "list[str]") -> bool:
    """Whether a key types a column's value: its reading (number or word) or its scale (the logarithm of its number) set by the key."""
    by = _by_level(key_cells, cells)
    shares: "list[float]" = []
    groups: "dict[str, list[float]]" = {}
    numbered = 0
    present = 0
    for level in sorted(by):
        level_cells = by[level]
        if len(level_cells) >= 20:
            shares += [_numeric_share(level_cells)]
        values: "list[float]" = []
        for cell in level_cells:
            if _bare(cell):
                present += 1
            value = _leading(cell)
            if value is not None:
                values += [_log_size(value)]
        numbered += len(values)
        groups[level] = values
    if shares and max(shares) >= NUMERIC_SHARE and min(shares) <= 1.0 - NUMERIC_SHARE:
        return True
    return present > 0 and numbered >= 0.5 * present and _between_share(groups) >= KEYED_SHARE


def _moved_by(key_cells: "list[str]", cells: "list[str]") -> bool:
    """Whether a key moves a column: fixed by it, typed by it, or its spellings spread apart by it (weighted total variation)."""
    rows = len(cells)
    if rows == 0:
        return False
    by = _by_level(key_cells, cells)
    overall = _counts(cells)
    if _commonest(overall)[1] < FIXED_SHARE * rows:
        fixed = 0
        for level in sorted(by):
            fixed += _commonest(_counts(by[level]))[1]
        if fixed >= FIXED_SHARE * rows:
            return True
    if _typed_by(key_cells, cells):
        return True
    if len(overall) > LABELS_MOST:
        groups: "dict[str, list[float]]" = {}
        for level in sorted(by):
            groups[level] = [_log_size(value) for value in (_leading(cell) for cell in by[level]) if value is not None]
        return _between_share(groups) >= MOVED_SHARE
    weighted = 0.0
    counted = 0
    for level in sorted(by):
        level_cells = by[level]
        if len(level_cells) < 20:
            continue
        own = _counts(level_cells)
        distance = 0.0
        for cell in overall:
            share = (own[cell] if cell in own else 0) / len(level_cells)
            distance += abs(share - overall[cell] / rows)
        weighted += 0.5 * distance * len(level_cells)
        counted += len(level_cells)
    return counted > 0 and weighted / counted >= MOVED_SHARE


def _constant_within(cells: "list[str]", owners: "list[int]") -> bool:
    """Whether a column holds one value a person on `CONSTANT_SHARE` of the persons of two rows or more."""
    first: "dict[int, str]" = {}
    several: "dict[int, int]" = {}
    broken: "dict[int, int]" = {}
    for row in range(len(cells)):
        owner = owners[row]
        if owner < 0:
            continue
        if owner not in first:
            first[owner] = cells[row]
            continue
        several[owner] = 1
        if cells[row] != first[owner]:
            broken[owner] = 1
    return bool(several) and len(several) - len(broken) >= CONSTANT_SHARE * len(several)


def key_of(columns: "dict[str, list[str]]", content: "list[str]", owners: "list[int]") -> str:
    """The key of a long table: the content label of `KEY_LEVELS_LEAST` to `KEY_LEVELS_MOST` levels, moving within persons, that types a value (`_typed_by`) and moves the most other content columns (`_moved_by`); '' where none does."""
    rows = len(owners)
    sample = _spread_rows(rows, KEY_SAMPLE)
    cut: "dict[str, list[str]]" = {}
    for name in content:
        whole = columns[name]
        cut[name] = [_bare(whole[row]) for row in sample]
    cut_owners = [owners[row] for row in sample]
    best, best_score = "", 0
    for key in content:
        cells = cut[key]
        levels = _counts(cells)
        if not KEY_LEVELS_LEAST <= len(levels) <= KEY_LEVELS_MOST:
            continue
        if _numeric_share(cells) >= 0.5 or not _varies_within(cells, cut_owners):
            continue
        score = 0
        typed = False
        for other in content:
            if other == key:
                continue
            if _typed_by(cells, cut[other]):
                typed = True
            if _moved_by(cells, cut[other]):
                score += 1
        if typed and score > best_score:
            best, best_score = key, score
    return best


def _copies(columns: "dict[str, list[str]]", content: "list[str]", rows: int) -> "list[dict[str, object]]":
    """Columns equal to another wherever that one is a plain number, one fixed spelling elsewhere (`RULE_SHARE` of rows)."""
    sample = _spread_rows(rows, KEY_SAMPLE)
    out: "list[dict[str, object]]" = []
    taken: "dict[str, int]" = {}
    for copy in content:
        copy_cells = [_bare(columns[copy][row]) for row in sample]
        if _numeric_share(copy_cells) < 0.95:
            continue
        for source in content:
            if source == copy or source in taken or copy in taken:
                continue
            source_cells = [_bare(columns[source][row]) for row in sample]
            numbers = 0
            same = 0
            others: "dict[str, int]" = {}
            for at in range(len(sample)):
                if plain_number(source_cells[at]) is not None:
                    numbers += 1
                    if copy_cells[at] == source_cells[at]:
                        same += 1
                else:
                    others[copy_cells[at]] = (others[copy_cells[at]] if copy_cells[at] in others else 0) + 1
            if numbers < 0.5 * len(sample) or same < RULE_SHARE * numbers:
                continue
            rest = len(sample) - numbers
            sentinel, held = _commonest(others) if others else ("", 0)
            if rest and held < RULE_SHARE * rest:
                continue
            out += [{"column": copy, "from": source, "else": sentinel}]
            taken[copy] = 1
            break
    return out


def _census(owners: "list[int]", persons: int) -> "list[list[int]]":
    held = [0 for _person in range(persons)]
    for owner in owners:
        if owner >= 0:
            held[owner] += 1
    counts = _counts([str(count) for count in held])
    return [[int(count), counts[count]] for _number, count in sorted((int(count), count) for count in counts)]


def _times(columns: "dict[str, list[str]]", dated: "tuple[str, ...]", owners: "list[int]",
           persons: int) -> "tuple[str, str, list[float]]":
    """The anchor date column, the axis ('days' or 'position') and each row's time since its person's first row."""
    rows = len(owners)
    for name in dated:
        if name not in columns:
            continue
        cells = columns[name]
        reading = inside_dates.reading_of([_text(cell) for cell in cells])
        if reading is None:
            continue
        moments: "list[float | None]" = []
        present = 0
        for cell in cells:
            found = inside_dates.moment_of(cell, reading)
            if found is None:
                moments += [None]
                continue
            present += 1
            second = found[1] if found[1] >= 0 else 0
            moments += [found[0] + second / SECONDS_A_DAY]
        if present < 0.9 * rows:
            continue
        return name, AXIS_DAYS, _since_first(moments, owners, persons)
    positions: "list[float | None]" = []
    seen = [0 for _person in range(persons)]
    for owner in owners:
        if owner < 0:
            positions += [None]
            continue
        positions += [float(seen[owner])]
        seen[owner] += 1
    return "", AXIS_POSITION, _since_first(positions, owners, persons)


def _since_first(moments: "list[float | None]", owners: "list[int]", persons: int) -> "list[float]":
    first: "list[float | None]" = [None for _person in range(persons)]
    for row in range(len(owners)):
        owner = owners[row]
        moment = moments[row]
        if owner < 0 or moment is None:
            continue
        known = first[owner]
        if known is None or moment < known:
            first[owner] = moment
    out: "list[float]" = []
    for row in range(len(owners)):
        owner = owners[row]
        moment = moments[row]
        known = first[owner] if owner >= 0 else None
        out += [moment - known if moment is not None and known is not None else 0.0]
    return out


def _minute_stamps(cells: "list[str]") -> "tuple[list[int | None], str] | None":
    """A column of minute stamps (`YYYY-MM-DD HH:MM`, one joint) as minutes, or None where it is not one."""
    out: "list[int | None]" = []
    joints: "dict[str, int]" = {}
    present = 0
    for cell in cells:
        found = inside_trajectories.moment_of(cell)
        if found is None:
            out += [None]
            if _bare(cell):
                return None
            continue
        if found.kind != inside_trajectories.KIND_MINUTE:
            return None
        present += 1
        joints[found.joint] = 1
        out += [found.seconds // 60]
    if present == 0 or len(joints) != 1:
        return None
    return out, _commonest(joints)[0]


def _moved(gaps_of: "dict[str, list[int]]") -> float:
    """The weighted Kolmogorov distance of each level's gaps from the pooled gaps (levels of fewer than `GAP_LEAST` set aside)."""
    pooled: "list[int]" = []
    for level in sorted(gaps_of):
        if len(gaps_of[level]) >= GAP_LEAST:
            pooled += gaps_of[level]
    if not pooled:
        return 0.0
    pooled = sorted(pooled)
    total = 0.0
    for level in sorted(gaps_of):
        own = sorted(gaps_of[level])
        if len(own) < GAP_LEAST:
            continue
        most = 0.0
        at_own = 0
        at_pooled = 0
        for value in own:
            while at_own < len(own) and own[at_own] <= value:
                at_own += 1
            while at_pooled < len(pooled) and pooled[at_pooled] <= value:
                at_pooled += 1
            most = max(most, abs(at_own / len(own) - at_pooled / len(pooled)))
        total += most * len(own) / len(pooled)
    return total


def _gap_grid(gaps: "list[int]") -> "list[int]":
    ordered = sorted(gaps)
    return [ordered[(k * (len(ordered) - 1)) // (GAP_GRID - 1)] for k in range(GAP_GRID)]


def _keyed_gaps(columns: "dict[str, list[str]]", dated: "tuple[str, ...]", anchor: str, by: "dict[str, list[int]]",
                levels: "list[dict[str, object]]", candidates: "list[str]") -> "list[list[str]]":
    """The later clocks whose gap from the anchor the key moves: each level's gaps and presence, put in its entry."""
    if not anchor:
        return []
    read = _minute_stamps(columns[anchor])
    if read is None:
        return []
    anchor_minutes = read[0]
    out: "list[list[str]]" = []
    for name in dated:
        if name == anchor or name not in columns:
            continue
        found = _minute_stamps(columns[name])
        if found is None:
            continue
        minutes, joint = found
        gaps_of: "dict[str, list[int]]" = {}
        for level in sorted(by):
            gaps: "list[int]" = []
            for row in by[level]:
                first, second = anchor_minutes[row], minutes[row]
                if first is not None and second is not None:
                    gaps += [second - first]
            gaps_of[level] = gaps
        if _moved(gaps_of) < GAP_MOVED:
            continue
        for entry in levels:
            level = _text(entry["level"])
            if _text(entry["kept"]) or level not in gaps_of or not gaps_of[level]:
                continue
            rows = by[level]
            present = [minutes[row] is not None for row in rows]
            rule = ""
            shares: "dict[str, list[int]]" = {}
            labels: "list[str]" = []
            for label in candidates:
                if 2 <= len(_counts([_bare(columns[label][row]) for row in rows])) <= SCALE_LABELS_MOST:
                    labels += [label]
            for label in labels:
                split: "dict[str, list[int]]" = {}
                for at in range(len(rows)):
                    cell = _bare(columns[label][rows[at]])
                    if cell not in split:
                        split[cell] = [0, 0]
                    split[cell][0] += 1 if present[at] else 0
                    split[cell][1] += 1
                pure = True
                absent_somewhere = False
                for cell in split:
                    share = split[cell][0] / split[cell][1]
                    if RULE_SHARE > share > 1.0 - RULE_SHARE:
                        pure = False
                    if share <= 1.0 - RULE_SHARE:
                        absent_somewhere = True
                if pure and absent_somewhere and len(split) >= 2:
                    rule, shares = label, split
                    break
            split_by, grids = "", {}
            best = GAP_MOVED
            for label in labels:
                parts: "dict[str, list[int]]" = {}
                for at in range(len(rows)):
                    first, second = anchor_minutes[rows[at]], minutes[rows[at]]
                    if first is None or second is None:
                        continue
                    cell = _bare(columns[label][rows[at]])
                    if cell not in parts:
                        parts[cell] = []
                    parts[cell] += [second - first]
                if not 2 <= len(parts) <= SCALE_LABELS_MOST:
                    continue
                moved = _moved(parts)
                if moved >= best:
                    best = moved
                    split_by = label
                    grids = {cell: _gap_grid(parts[cell]) for cell in sorted(parts)}
            gaps_entry: "dict[str, object]" = {"present": [sum(1 for each in present if each), len(rows)],
                                               "grid": _gap_grid(gaps_of[level]), "by": rule,
                                               "present_by": shares, "split_by": split_by, "grids": grids}
            held = typing.cast("dict[str, object]", entry["gaps"]) if "gaps" in entry else {}
            held[name] = gaps_entry
            entry["gaps"] = held
        out += [[name, joint]]
    return out


def _grid(values: "list[float]") -> "list[float]":
    ordered = sorted(values)
    count = len(ordered)
    out: "list[float]" = []
    for k in range(GRID):
        place = k * (count - 1) / (GRID - 1)
        low = int(place)
        high = low + 1 if low + 1 < count else low
        part = place - low
        out += [ordered[low] + (ordered[high] - ordered[low]) * part]
    return out


def _marginal(cells: "list[str]") -> "dict[str, object]":
    """A number column's marginal over its cells: atoms, and plain numbers as a value table or a quantile function with their form."""
    low: "dict[str, int]" = {}
    high: "dict[str, int]" = {}
    plain: "dict[str, int]" = {}
    values: "list[float]" = []
    for cell in cells:
        text = _bare(cell)
        value = plain_number(text)
        if value is not None:
            plain[text] = (plain[text] if text in plain else 0) + 1
            values += [value]
            continue
        atom = atom_of(text)
        if atom is not None:
            side = low if atom[0] == "<" else high
            side[text] = (side[text] if text in side else 0) + 1
    entry: "dict[str, object]" = {
        "low": [[cell, low[cell]] for _place, cell in sorted((_position(cell), cell) for cell in low)],
        "high": [[cell, high[cell]] for _place, cell in sorted((_position(cell), cell) for cell in high)],
        "plain": len(values),
    }
    places: "dict[float, list[list[object]]]" = {}
    for cell in sorted(plain):
        value = plain_number(cell)
        if value is None:
            continue
        if value not in places:
            places[value] = []
        places[value] += [[cell, plain[cell]]]
    if len(places) <= TABLE_MOST:
        entry["table"] = [[value, places[value]] for value in sorted(places)]
        return entry
    figures = 0
    for cell in plain:
        figures = max(figures, decimals_of(cell))
    entry["grid"] = [float(f"{value:.{figures + 3}f}") for value in _grid(values)]
    decimals: "dict[str, int]" = {}
    small = 0
    dotted = 0
    for cell in plain:
        places_key = str(decimals_of(cell))
        decimals[places_key] = (decimals[places_key] if places_key in decimals else 0) + plain[cell]
        bare = cell[1:] if cell[:1] in ("+", "-") else cell
        value = plain_number(cell)
        if value is not None and abs(value) < 1.0 and value != 0.0:
            small += plain[cell]
            if bare[:1] == ".":
                dotted += plain[cell]
    entry["decimals"] = [[int(places_), decimals[places_]] for _n, places_ in sorted((int(d), d) for d in decimals)]
    entry["dotted"] = (dotted * 1000000) // small if small else 0
    return entry


def _model(z: "dict[int, float]", times: "list[float]", owners: "list[int]", order: "list[int]") -> "dict[str, float]":
    """The trajectory of a level's number on its normal scores: trend over the person's time, person share, lag one, noise."""
    rows_of: "dict[int, list[int]]" = {}
    for row in order:
        if row in z and owners[row] >= 0:
            owner = owners[row]
            if owner not in rows_of:
                rows_of[owner] = []
            rows_of[owner] += [row]
    flat = {"slope": 0.0, "person": 0.0, "noise": 1.0, "lag": 0.0}
    several = [owner for owner in sorted(rows_of) if len(rows_of[owner]) >= 2]
    if len(z) < FIT_ROWS_LEAST or len(several) < FIT_PERSONS_LEAST:
        return flat
    kept: "list[int]" = []
    total = 0
    for owner in sorted(rows_of):
        if total + len(rows_of[owner]) > FIT_ROWS:
            break
        kept += [owner]
        total += len(rows_of[owner])
    sxx = 0.0
    sxy = 0.0
    for owner in kept:
        rows = rows_of[owner]
        if len(rows) < 2:
            continue
        mean_t = math.fsum([times[row] for row in rows]) / len(rows)
        mean_z = math.fsum([z[row] for row in rows]) / len(rows)
        for row in rows:
            sxx += (times[row] - mean_t) * (times[row] - mean_t)
            sxy += (times[row] - mean_t) * (z[row] - mean_z)
    slope = sxy / sxx if sxx > 0.0 else 0.0
    residual: "dict[int, float]" = {}
    for owner in kept:
        for row in rows_of[owner]:
            residual[row] = z[row] - slope * times[row]
    within = 0.0
    lag_sum = 0.0
    lag_null = 0.0
    lag_pairs = 0
    count = 0
    groups = 0
    squares = 0
    means: "list[tuple[float, int]]" = []
    for owner in kept:
        rows = rows_of[owner]
        size = len(rows)
        mean_r = math.fsum([residual[row] for row in rows]) / size
        means += [(mean_r, size)]
        count += size
        groups += 1
        squares += size * size
        deviations = [residual[row] - mean_r for row in rows]
        within += math.fsum([d * d for d in deviations])
        if size >= 2:
            for at in range(size - 1):
                lag_sum += deviations[at] * deviations[at + 1]
            lag_pairs += size - 1
            lag_null += (size - 1) / size
    if count <= groups or groups < 2 or within <= 0.0:
        return flat
    within_pairs = within / (count - groups)
    se_slope = math.sqrt(within_pairs / sxx) if sxx > 0.0 else 0.0
    if se_slope <= 0.0 or abs(slope) < GATE_Z * se_slope:
        slope = 0.0
    lag = 0.0
    if lag_pairs > 0:
        lengths: "dict[int, int]" = {}
        for owner in kept:
            size = len(rows_of[owner])
            lengths[size] = (lengths[size] if size in lengths else 0) + 1
        observed = lag_sum / within
        if abs(observed - _expected_ratio(lengths, 0.0)) * math.sqrt(lag_pairs) >= GATE_Z:
            lag = _lag_solved(lengths, observed)
    factor = 0.0
    spread = 0.0
    for owner in kept:
        size = len(rows_of[owner])
        within_sum = _series_sum(size, lag)
        factor += size - within_sum / size
        spread += (within_sum / size) * (1.0 - size / count)
    noise = within / factor if factor > 0.0 else within_pairs
    grand = math.fsum([mean * size for mean, size in means]) / count
    between = math.fsum([size * (mean - grand) * (mean - grand) for mean, size in means]) / (groups - 1)
    n0 = (count - squares / count) / (groups - 1)
    person = (between - noise * spread / (groups - 1)) / n0 if n0 > 0.0 else 0.0
    return {"slope": slope, "person": max(0.0, person), "noise": max(noise, 1e-9), "lag": lag}


def _expected_ratio(lengths: "dict[int, int]", lag: float) -> float:
    """The expected ratio of a person's lag-one cross products to its sum of squares about its own mean, AR(1) noise.

    For a series of n places, deviations d about the series' mean, S the
    sum of the correlations over every pair of places and r the sum over
    one end's: E[sum d_j d_j+1] = (n-1) lag - (2 S - 2 r) / n + (n-1) S / n^2
    and E[sum d_j^2] = n - S / n, in units of the noise's variance; the
    person's own level cancels in both.
    """
    top = 0.0
    bottom = 0.0
    for size in sorted(lengths):
        if size < 2:
            continue
        total = _series_sum(size, lag)
        end = 0.0
        power = 1.0
        for _step in range(size):
            end += power
            power = power * lag
        count = lengths[size]
        top += count * ((size - 1) * lag - (2.0 * total - 2.0 * end) / size + (size - 1) * total / (size * size))
        bottom += count * (size - total / size)
    return top / bottom if bottom > 0.0 else 0.0


def _lag_solved(lengths: "dict[int, int]", observed: float) -> float:
    """The lag whose expected ratio (`_expected_ratio`) is the observed one, by bisection inside the lag's bounds."""
    low, high = LAG_LEAST, LAG_MOST
    if observed <= _expected_ratio(lengths, low):
        return low
    if observed >= _expected_ratio(lengths, high):
        return high
    for _step in range(40):
        middle = (low + high) / 2.0
        if _expected_ratio(lengths, middle) < observed:
            low = middle
        else:
            high = middle
    return (low + high) / 2.0


def _series_sum(size: int, lag: float) -> float:
    """The sum of an AR(1) series' correlations over every pair of its `size` places (the places themselves included)."""
    total = float(size)
    power = 1.0
    for step in range(1, size):
        power = power * lag
        if power == 0.0:
            break
        total += 2.0 * (size - step) * power
    return total


def _scale_label(labels: "dict[str, list[str]]", cells: "list[str]") -> str:
    """The label (2 to `SCALE_LABELS_MOST` spellings at the level) whose groups hold `SCALE_SHARE` of the number's spread on its logarithm."""
    best, best_share = "", SCALE_SHARE
    for name in sorted(labels):
        level_cells = labels[name]
        spellings = _counts(level_cells)
        if not 2 <= len(spellings) <= SCALE_LABELS_MOST:
            continue
        groups: "dict[str, list[float]]" = {}
        for at in range(len(cells)):
            value = _position(cells[at])
            if value is None:
                continue
            group = level_cells[at]
            if group not in groups:
                groups[group] = []
            groups[group] += [_log_size(value)]
        share = _between_share(groups)
        if share >= best_share:
            best, best_share = name, share
    return best


def _normal_scores(cells: "list[str]", groups: "list[str]") -> "dict[int, float]":
    """Each number cell's normal score at its mid-rank inside its group (atoms at their places)."""
    by: "dict[str, list[int]]" = {}
    for at in range(len(cells)):
        if _position(cells[at]) is None:
            continue
        if groups[at] not in by:
            by[groups[at]] = []
        by[groups[at]] += [at]
    out: "dict[int, float]" = {}
    for group in sorted(by):
        places = by[group]
        scores = inside_trajectories.mid_scores([typing.cast(float, _position(cells[at])) for at in places])
        for k in range(len(places)):
            out[places[k]] = scores[k]
    return out


def _number_entry(cells: "list[str]", groups: "list[str]", scale: str) -> "dict[str, object]":
    by: "dict[str, list[str]]" = {}
    states: "dict[str, dict[str, int]]" = {}
    for at in range(len(cells)):
        group = groups[at]
        if group not in by:
            by[group] = []
            states[group] = {}
        if _position(cells[at]) is not None:
            by[group] += [cells[at]]
        else:
            states[group][cells[at]] = (states[group][cells[at]] if cells[at] in states[group] else 0) + 1
    out: "dict[str, object]" = {}
    for group in sorted(by):
        out[group] = {"marginal": _marginal(by[group]),
                      "states": [[cell, states[group][cell]] for cell in sorted(states[group])]}
    return {"scale": scale, "groups": out}


def _interval_rule(flag: "list[str]", values: "list[float | None]", tuple_keys: "list[str]") -> "dict[str, object] | None":
    """A flag that is a function of intervals of a number inside each group of the row's other labels, as its cuts; None where it is not."""
    by: "dict[str, list[int]]" = {}
    for at in range(len(flag)):
        if tuple_keys[at] not in by:
            by[tuple_keys[at]] = []
        by[tuple_keys[at]] += [at]
    groups: "dict[str, object]" = {}
    covered = 0
    cut_count = 0
    for key in sorted(by):
        places = by[key]
        numbered = [(typing.cast(float, values[at]), flag[at]) for at in places if values[at] is not None]
        others = _counts([flag[at] for at in places if values[at] is None])
        numbered = sorted(numbered)
        cuts: "list[list[object]]" = []
        for at in range(1, len(numbered)):
            if numbered[at][1] != numbered[at - 1][1]:
                if numbered[at][0] == numbered[at - 1][0]:
                    return None
                cuts += [[(numbered[at][0] + numbered[at - 1][0]) / 2.0, numbered[at - 1][1]]]
        if len(cuts) > CUTS_MOST:
            return None
        covered += len(numbered)
        cut_count += len(cuts)
        groups[key] = {"cuts": cuts, "last": numbered[len(numbered) - 1][1] if numbered else "",
                       "other": _commonest(others)[0] if others else ""}
    if covered == 0 or cut_count == 0:
        return None
    return groups


def _level_entry(columns: "dict[str, list[str]]", rows: "list[int]", content: "list[str]", owners: "list[int]",
                 times: "list[float]", tops: "dict[str, int]", level_tops: "dict[str, int]") -> "dict[str, object]":
    """One key level's rules inside a row, marginals and trajectories (see the module's account)."""
    labels: "dict[str, list[str]]" = {}
    numbers: "dict[str, list[str]]" = {}
    pairs: "dict[str, list[str]]" = {}
    kept_columns: "list[str]" = []
    for name in content:
        cells = [_bare(columns[name][row]) for row in rows]
        present = [cell for cell in cells if cell]
        paired = 0
        numeric = 0
        distinct: "dict[float, int]" = {}
        for cell in present:
            if pair_of(cell) is not None:
                paired += 1
            place = _position(cell)
            if place is not None:
                numeric += 1
                distinct[place] = 1
        if present and paired >= PAIR_SHARE * len(present):
            pairs[name] = cells
        elif present and numeric >= NUMERIC_SHARE * len(present) and len(distinct) >= 3:
            numbers[name] = cells
        elif len(_counts(cells)) <= LABELS_MOST:
            labels[name] = cells
        else:
            kept_columns += [name]
    entry: "dict[str, object]" = {"rows": len(rows), "kept": "", "kept_columns": kept_columns}
    intervals: "dict[str, object]" = {}
    for flag_name in sorted(labels):
        flag = labels[flag_name]
        if not 2 <= len(_counts(flag)) <= 3:
            continue
        others = [name for name in sorted(labels) if name != flag_name and name not in intervals]
        tuple_keys = [_joined([labels[name][at] for name in others]) for at in range(len(rows))]
        for number_name in sorted(numbers):
            if _scale_label({flag_name: flag}, numbers[number_name]):
                continue
            values = [plain_number(cell) for cell in numbers[number_name]]
            rule = _interval_rule(flag, values, tuple_keys)
            if rule is not None:
                intervals[flag_name] = {"of": number_name, "by": others, "groups": rule}
                break
    tuple_names = [name for name in sorted(labels) if name not in intervals]
    parts_of: "dict[str, list[str]]" = {}
    joined_rows: "list[str]" = []
    for at in range(len(rows)):
        parts = [labels[name][at] for name in tuple_names]
        joined = _joined(parts)
        parts_of[joined] = parts
        joined_rows += [joined]
    tuples = _counts(joined_rows)
    entry["labels"] = tuple_names
    if len(tuples) <= TUPLES_MOST:
        entry["tuples"] = [[parts_of[joined], tuples[joined]] for joined in sorted(tuples)]
    else:
        apart: "dict[str, object]" = {}
        for name in tuple_names:
            counted = _counts(labels[name])
            apart[name] = [[cell, counted[cell]] for cell in sorted(counted)]
        entry["apart"] = apart
    entry["intervals"] = intervals
    number_entries: "dict[str, object]" = {}
    order = [row for _time, row in sorted((times[rows[at]], rows[at]) for at in range(len(rows)))]
    for name in sorted(numbers):
        cells = numbers[name]
        scale = _scale_label(labels, cells)
        groups = labels[scale] if scale else ["" for _cell in cells]
        built = _number_entry(cells, groups, scale)
        scores = _normal_scores(cells, groups)
        z = {rows[at]: scores[at] for at in scores}
        built["model"] = _model(z, times, owners, order)
        built["cap"] = TOP_CODE if (name in tops or name in level_tops) else 0
        number_entries[name] = built
    entry["numbers"] = number_entries
    pair_entries: "dict[str, object]" = {}
    for name in sorted(pairs):
        cells = pairs[name]
        firsts: "list[str]" = []
        seconds: "list[str]" = []
        for cell in cells:
            found = pair_of(cell)
            firsts += [found[0] if found is not None else cell]
            seconds += [found[1] if found is not None else ""]
        scale = _scale_label(labels, firsts)
        groups = labels[scale] if scale else ["" for _cell in cells]
        first_entry = _number_entry(firsts, groups, scale)
        second_entry = _number_entry(seconds, groups, scale)
        first_scores = _normal_scores(firsts, groups)
        second_scores = _normal_scores(seconds, groups)
        shared = [at for at in sorted(first_scores) if at in second_scores]
        corr = 0.0
        if len(shared) >= 3:
            a = [first_scores[at] for at in shared]
            b = [second_scores[at] for at in shared]
            mean_a = math.fsum(a) / len(a)
            mean_b = math.fsum(b) / len(b)
            sab = math.fsum([(a[k] - mean_a) * (b[k] - mean_b) for k in range(len(a))])
            saa = math.fsum([(x - mean_a) * (x - mean_a) for x in a])
            sbb = math.fsum([(x - mean_b) * (x - mean_b) for x in b])
            corr = sab / math.sqrt(saa * sbb) if saa > 0.0 and sbb > 0.0 else 0.0
        z = {rows[at]: first_scores[at] for at in first_scores}
        pair_entries[name] = {"first": first_entry, "second": second_entry, "corr": max(-0.999, min(0.999, corr)),
                              "model": _model(z, times, owners, order),
                              "cap": TOP_CODE if (name in tops or name in level_tops) else 0}
    entry["pairs"] = pair_entries
    return entry


def _distinct_repeat(cells: "list[str]", owners: "list[int]") -> bool:
    """Whether a level's values repeat across persons as measurements do: half its cells hold a value two persons or more hold."""
    holders: "dict[str, dict[int, int]]" = {}
    present = 0
    for at in range(len(cells)):
        parts: "list[str]" = []
        found = pair_of(cells[at])
        if found is not None:
            parts = [found[0], found[1]]
        elif _bare(cells[at]):
            parts = [_bare(cells[at])]
        for part in parts:
            present += 1
            if part not in holders:
                holders[part] = {}
            holders[part][owners[at]] = 1
    if present == 0:
        return True
    shared = 0
    for part in holders:
        if len(holders[part]) >= 2:
            shared += 1
    repeated = 0
    for at in range(len(cells)):
        found = pair_of(cells[at])
        parts = [found[0], found[1]] if found is not None else ([_bare(cells[at])] if _bare(cells[at]) else [])
        for part in parts:
            if len(holders[part]) >= 2:
                repeated += 1
    return repeated >= 0.5 * present and len(holders) <= 0.5 * present


def build_zone(columns: "dict[str, list[str]]", person: str, skipped: "tuple[str, ...]" = (),
               dated: "tuple[str, ...]" = (), tops: "dict[str, int] | None" = None,
               held: "dict[str, dict[str, dict[str, object]]] | None" = None) -> "dict[str, object] | None":
    """The keyed zone of a long table, or None where the table holds no key (see the module's account).

    `columns` holds every column's cells as text; `person` names the
    column of persons (it must repeat); `skipped` the columns kept whole
    (record numbers, free text); `dated` the date columns (the first read
    on nine rows in ten is the time axis); `tops` the columns top-coded
    at 90; `held` each keyed value column's key blocks as the description
    holds them ({column: {folded level: {"identifier": bool, "top": int}}}).
    Guarantees: a fixed function of its inputs; no I/O. Raises nothing
    but TypeError on an internal mismatch.
    """
    if not person or person not in columns or not _repeats(columns[person]):
        return None
    rows = len(columns[person])
    owners, persons = _persons(columns[person])
    content = [name for name in columns if name != person and name not in skipped and name not in dated]
    for name in content:
        if len(columns[name]) != rows:
            raise TypeError("internal check: the columns of one table hold different numbers of rows")
    key = key_of(columns, content, owners)
    if not key:
        return None
    tops = tops or {}
    held = held or {}
    sample = _spread_rows(rows, KEY_SAMPLE)
    key_sample = [_bare(columns[key][row]) for row in sample]
    owner_sample = [owners[row] for row in sample]
    constant: "list[str]" = []
    taken: "list[str]" = []
    for name in content:
        if name == key:
            continue
        cut = [_bare(columns[name][row]) for row in sample]
        if _constant_within(cut, owner_sample):
            constant += [name]
        elif _moved_by(key_sample, cut):
            taken += [name]
    copies = [rule for rule in _copies(columns, [name for name in content if name != key and name not in constant], rows)
              if rule["from"] in taken]
    copied = [typing.cast(str, rule["column"]) for rule in copies]
    rest = [name for name in taken if name not in copied]
    anchor, axis, times = _times(columns, dated, owners, persons)
    by: "dict[str, list[int]]" = {}
    for row in range(rows):
        level = _bare(columns[key][row])
        if level not in by:
            by[level] = []
        by[level] += [row]
    levels: "list[dict[str, object]]" = []
    ranked = [level for _count, level in sorted((-len(by[level]), level) for level in by)]
    for place in range(len(ranked)):
        level = ranked[place]
        level_rows = by[level]
        if place >= MODELLED_LEVELS_MOST:
            levels += [{"level": level, "rows": len(level_rows), "kept": KEPT_RARE}]
            continue
        folded = fold(level)
        level_tops: "dict[str, int]" = {}
        why = ""
        for name in rest:
            blocks = held[name] if name in held else {}
            block = blocks[folded] if folded in blocks else {}
            if "top" in block and block["top"] == TOP_CODE:
                level_tops[name] = TOP_CODE
            cells = [_text(columns[name][row]) for row in level_rows]
            if "identifier" in block and block["identifier"] and not _distinct_repeat(
                    cells, [owners[row] for row in level_rows]):
                why = KEPT_IDENTIFIER
            if not why and _numeric_share(cells) < NUMERIC_SHARE and inside_dates.reading_of(cells) is not None:
                why = KEPT_DATES
        if why:
            levels += [{"level": level, "rows": len(level_rows), "kept": why}]
            continue
        built = _level_entry(columns, level_rows, rest, owners, times, tops, level_tops)
        built["level"] = level
        levels += [built]
    keyed_gaps = _keyed_gaps(columns, dated, anchor, by, levels,
                             [name for name in content if name != key and name not in constant])
    return {
        "version": ZONE_VERSION, "key": key, "person": person, "anchor": anchor, "axis": axis,
        "census": _census(owners, persons), "content": rest, "copies": copies, "levels": levels, "rows": rows,
        "gaps": keyed_gaps, "constant": constant,
    }


def key_blocks_of(document: object) -> "tuple[dict[str, int], dict[str, dict[str, dict[str, object]]]]":
    """From a description written: the columns top-coded at 90, and each keyed value column's key blocks' holds and top codes."""
    tops: "dict[str, int]" = {}
    held: "dict[str, dict[str, dict[str, object]]]" = {}
    columns = document["columns"] if isinstance(document, dict) and "columns" in document else None
    if not isinstance(columns, list):
        return tops, held
    for block in columns:
        if not isinstance(block, dict) or "name" not in block or not isinstance(block["name"], str):
            continue
        name = block["name"]
        if "top_coded" in block and block["top_coded"] == TOP_CODE:
            tops[name] = TOP_CODE
        by_key = block["by_key"] if "by_key" in block else None
        blocks = by_key["key_blocks"] if isinstance(by_key, dict) and "key_blocks" in by_key else None
        if not isinstance(blocks, list):
            continue
        read: "dict[str, dict[str, object]]" = {}
        for each in blocks:
            if not isinstance(each, dict) or "key" not in each or not isinstance(each["key"], str):
                continue
            inner = each["block"] if "block" in each and isinstance(each["block"], dict) else {}
            role = inner["role"] if "role" in inner else ""
            structural = inner["structural_role"] if "structural_role" in inner else ""
            top = inner["top_coded"] if "top_coded" in inner and isinstance(inner["top_coded"], int) else 0
            read[fold(each["key"])] = {"identifier": role == "identifier" or structural == "identifier", "top": top}
        held[name] = read
    return tops, held


# A column block's keys that keep a column out of the keyed zone, whatever the key does to it: holds the
# description makes for privacy (a withheld count, words withheld, a year or word top code) and a column it
# computes from others by a rule of its own.
PRIVACY_KEYS = ("computed_from", "top_coded_year", "top_coded_words", "present_count_withheld", "withheld_words_from")
KEPT_ROLES = ("identifier", "free_text")


def kept_by_description(document: object) -> "tuple[str, ...]":
    """The columns of a description written that the keyed zone never draws: identifiers, free text, a Safe Harbor top code other than an age's 90, and every column a privacy hold or a computing rule keeps (`PRIVACY_KEYS`)."""
    columns = document["columns"] if isinstance(document, dict) and "columns" in document else None
    out: "list[str]" = []
    if not isinstance(columns, list):
        return ()
    for block in columns:
        if not isinstance(block, dict) or "name" not in block or not isinstance(block["name"], str):
            continue
        role = block["role"] if "role" in block else ""
        structural = block["structural_role"] if "structural_role" in block else ""
        top = block["top_coded"] if "top_coded" in block and isinstance(block["top_coded"], int) else 0
        kept = role in KEPT_ROLES or structural == "identifier" or top not in (0, TOP_CODE)
        for key in PRIVACY_KEYS:
            if key in block and block[key]:
                kept = True
        if kept:
            out += [block["name"]]
    return tuple(out)


def zone_of_record(record: object) -> "dict[str, object] | None":
    """The keyed zone of an inside record, checked, or None where the record holds none."""
    zones = record["zones"] if isinstance(record, dict) and "zones" in record else None
    zone = zones[ZONE] if isinstance(zones, dict) and ZONE in zones else None
    if zone is None:
        return None
    if not isinstance(zone, dict):
        raise KeyedError("The inside record's keyed zone is not a zone synthtwin wrote.")
    for name in _ZONE_KEYS:
        if name not in zone:
            raise KeyedError("The inside record's keyed zone is not a zone synthtwin wrote.")
    if zone["version"] != ZONE_VERSION:
        raise KeyedError("The inside record's keyed zone was written by another version of synthtwin.")
    return zone


# -- the generator ----------------------------------------------------------------------------------------


def _object(value: object) -> "dict[str, typing.Any]":
    if not isinstance(value, dict):
        raise KeyedError("The inside record's keyed zone is not a zone synthtwin wrote.")
    return value


def _list(value: object) -> "list[typing.Any]":
    if not isinstance(value, list):
        raise KeyedError("The inside record's keyed zone is not a zone synthtwin wrote.")
    return value


def _levels_by_spelling(zone: "dict[str, object]") -> "dict[str, dict[str, typing.Any]]":
    out: "dict[str, dict[str, typing.Any]]" = {}
    folded: "dict[str, dict[str, typing.Any]]" = {}
    for entry in _list(zone["levels"]):
        level = _object(entry)
        spelling = _text(level["level"])
        out[spelling] = level
        if fold(spelling) not in folded:
            folded[fold(spelling)] = level
    for spelling in folded:
        if spelling not in out:
            out[spelling] = folded[spelling]
    return out


def _level_rows(zone: "dict[str, object]", key_cells: "list[str]") -> "dict[str, list[int]]":
    """The twin's rows of each modelled key level (a key cell the zone does not model is left to the description's twin)."""
    known = _levels_by_spelling(zone)
    out: "dict[str, list[int]]" = {}
    for row in range(len(key_cells)):
        cell = _bare(key_cells[row])
        level = known[cell] if cell in known else (known[fold(cell)] if fold(cell) in known else None)
        if level is None or _text(level["kept"]):
            continue
        name = _text(level["level"])
        if name not in out:
            out[name] = []
        out[name] += [row]
    return out


def persons_and_labels(zone: "dict[str, object]", cells: "dict[str, list[str]]", seed: int) -> "dict[str, list[str]]":
    """Step one: the twin's persons take the census's numbers of rows, and each modelled row its level's label cells.

    `cells` holds the twin's person column, key column and content columns
    as written so far. Returns the person column and every label column
    the zone writes (other cells of a row the zone does not model stay).
    Raises KeyedError where the zone does not fit the twin.
    """
    person = _text(zone["person"])
    key = _text(zone["key"])
    if person not in cells or key not in cells:
        raise KeyedError("The inside record's keyed zone names a column this twin does not hold.")
    people = cells[person]
    rows = len(people)
    out: "dict[str, list[str]]" = {}
    names: "list[str]" = []
    seen: "dict[str, int]" = {}
    filled: "list[int]" = []
    for row in range(rows):
        text = _bare(people[row])
        if not text:
            continue
        filled += [row]
        if text not in seen:
            seen[text] = 1
            names += [text]
    census: "list[int]" = []
    for pair in _list(zone["census"]):
        count, persons = int(_list(pair)[0]), int(_list(pair)[1])
        census += [count for _person in range(persons)]
    state = inside_trajectories.stream_of(seed, inside_trajectories.name_salt(person + _SEP + "persons"))
    census = _shuffled(census, state)
    if len(census) > len(names):
        kept = sorted(census, reverse=True)[: len(names)]
        census = _shuffled(kept, state)
    counts = _largest_remainders(census, len(filled)) if census else []
    written = [cell for cell in people]
    at = 0
    for place in range(len(counts)):
        for _row in range(counts[place]):
            written[filled[at]] = names[place]
            at += 1
    out[person] = written
    for name in (_list(zone["constant"]) if "constant" in zone else []):
        column_name = _text(name)
        if column_name not in cells:
            continue
        first_cell: "dict[str, str]" = {}
        again = [cell for cell in cells[column_name]]
        for row in filled:
            owner = written[row]
            if owner not in first_cell:
                first_cell[owner] = again[row]
            again[row] = first_cell[owner]
        out[column_name] = again
    by_level = _level_rows(zone, cells[key])
    levels = _levels_by_spelling(zone)
    for level_name in sorted(by_level):
        level = levels[level_name]
        rows_k = by_level[level_name]
        label_names = [_text(name) for name in _list(level["labels"])]
        for name in label_names:
            if name not in out:
                if name not in cells:
                    raise KeyedError("The inside record's keyed zone names a column this twin does not hold.")
                out[name] = [cell for cell in cells[name]]
        level_state = inside_trajectories.stream_of(seed, inside_trajectories.name_salt(key + _SEP + level_name))
        if "tuples" in level:
            table = _list(level["tuples"])
            dealt = _largest_remainders([int(_list(entry)[1]) for entry in table], len(rows_k))
            plan: "list[int]" = []
            for place in range(len(dealt)):
                plan += [place for _count in range(dealt[place])]
            plan = _shuffled(plan, level_state)
            for at in range(len(rows_k)):
                chosen = _list(_list(table[plan[at]])[0])
                for k in range(len(label_names)):
                    out[label_names[k]][rows_k[at]] = _text(chosen[k])
        else:
            apart = _object(level["apart"])
            for name in label_names:
                table = _list(apart[name])
                dealt = _largest_remainders([int(_list(entry)[1]) for entry in table], len(rows_k))
                plan = []
                for place in range(len(dealt)):
                    plan += [place for _count in range(dealt[place])]
                plan = _shuffled(plan, level_state)
                for at in range(len(rows_k)):
                    out[name][rows_k[at]] = _text(_list(table[plan[at]])[0])
    return out


@dataclasses.dataclass
class _Drawn:
    """A marginal read for drawing: its atoms, its plain part (a value table or a grid with its form) and their counts."""

    low: "list[tuple[str, int]]"
    high: "list[tuple[str, int]]"
    plain: int
    table: "list[tuple[float, list[tuple[str, int]]]]"
    grid: "list[float]"
    decimals: "list[tuple[int, int]]"
    dotted: int
    total: int


def _drawn_of(entry: "dict[str, typing.Any]") -> _Drawn:
    low = [(_text(_list(pair)[0]), int(_list(pair)[1])) for pair in _list(entry["low"])]
    high = [(_text(_list(pair)[0]), int(_list(pair)[1])) for pair in _list(entry["high"])]
    plain = int(entry["plain"])
    table: "list[tuple[float, list[tuple[str, int]]]]" = []
    grid: "list[float]" = []
    decimals: "list[tuple[int, int]]" = []
    dotted = 0
    if "table" in entry:
        for place in _list(entry["table"]):
            spellings = [(_text(_list(each)[0]), int(_list(each)[1])) for each in _list(_list(place)[1])]
            table += [(float(_list(place)[0]), spellings)]
    else:
        grid = [float(value) for value in _list(entry["grid"])]
        decimals = [(int(_list(pair)[0]), int(_list(pair)[1])) for pair in _list(entry["decimals"])]
        dotted = int(entry["dotted"])
    total = sum(count for _cell, count in low) + plain + sum(count for _cell, count in high)
    return _Drawn(low, high, plain, table, grid, decimals, dotted, total)


def _drawn_cell(drawn: _Drawn, u: float, state: "list[int]", cap: int) -> str:
    """The spelling at share `u` of the marginal (an atom, a value of the table, or a value of the grid written in its form)."""
    if drawn.total <= 0:
        return ""
    point = u * drawn.total
    for cell, count in drawn.low:
        if point < count:
            return cell
        point -= count
    if point < drawn.plain or not drawn.high:
        share = min(max(point / drawn.plain, 0.0), 1.0) if drawn.plain else 0.0
        return _plain_cell(drawn, share, state, cap)
    point -= drawn.plain
    for cell, count in drawn.high:
        if point < count:
            return cell
        point -= count
    return drawn.high[len(drawn.high) - 1][0]


def _plain_cell(drawn: _Drawn, share: float, state: "list[int]", cap: int) -> str:
    if drawn.table:
        total = 0
        for _value, spellings in drawn.table:
            total += sum(count for _cell, count in spellings)
        point = share * total
        last = drawn.table[len(drawn.table) - 1][0]
        for value, spellings in drawn.table:
            held = sum(count for _cell, count in spellings)
            if point < held or value == last:
                return _capped(_pick(spellings, state), value, cap)
            point -= held
    place = share * (len(drawn.grid) - 1)
    low = int(place)
    high = low + 1 if low + 1 < len(drawn.grid) else low
    value = drawn.grid[low] + (drawn.grid[high] - drawn.grid[low]) * (place - low)
    written = _written(value, _places_drawn(drawn, state))
    if drawn.dotted and abs(value) < 1.0 and inside_trajectories.next_uniform(state) * 1000000 < drawn.dotted:
        if written[:2] == "0.":
            written = written[1:]
        elif written[:3] == "-0.":
            written = "-" + written[2:]
    return _capped(written, value, cap)


def _places_drawn(drawn: _Drawn, state: "list[int]") -> int:
    total = sum(count for _places, count in drawn.decimals)
    if total <= 0:
        return 0
    point = inside_trajectories.next_uniform(state) * total
    for places, count in drawn.decimals:
        if point < count:
            return places
        point -= count
    return drawn.decimals[len(drawn.decimals) - 1][0]


def _pick(spellings: "list[tuple[str, int]]", state: "list[int]") -> str:
    if len(spellings) == 1:
        return spellings[0][0]
    total = sum(count for _cell, count in spellings)
    point = inside_trajectories.next_uniform(state) * total
    for cell, count in spellings:
        if point < count:
            return cell
        point -= count
    return spellings[len(spellings) - 1][0]


def _written(value: float, places: int) -> str:
    """A number written with `places` decimals (rounding half away from nought on the written figures)."""
    scale = 1
    for _place in range(places):
        scale = scale * 10
    whole = int(abs(value) * scale + 0.5)
    sign = "-" if value < 0.0 and whole != 0 else ""
    figures = str(whole)
    if places == 0:
        return sign + figures
    figures = "0" * (places + 1 - len(figures)) + figures if len(figures) <= places else figures
    return sign + figures[: len(figures) - places] + "." + figures[len(figures) - places:]


def _capped(cell: str, value: float, cap: int) -> str:
    if cap and value > cap:
        return str(cap)
    return cell


def _time_axis(zone: "dict[str, object]", cells: "dict[str, list[str]]", owners: "list[int]",
               persons: int) -> "list[float]":
    anchor = _text(zone["anchor"])
    if anchor and anchor in cells:
        reading = inside_dates.reading_of([_text(cell) for cell in cells[anchor]])
        if reading is not None:
            moments: "list[float | None]" = []
            for cell in cells[anchor]:
                found = inside_dates.moment_of(cell, reading)
                if found is None:
                    moments += [None]
                    continue
                second = found[1] if found[1] >= 0 else 0
                moments += [found[0] + second / SECONDS_A_DAY]
            return _since_first(moments, owners, persons)
    positions: "list[float | None]" = []
    seen = [0 for _person in range(persons)]
    for owner in owners:
        if owner < 0:
            positions += [None]
            continue
        positions += [float(seen[owner])]
        seen[owner] += 1
    return _since_first(positions, owners, persons)


def _latents(model: "dict[str, typing.Any]", rows_k: "list[int]", owners: "list[int]", times: "list[float]",
             seed: int, salt: str, people: "list[str]") -> "dict[int, float]":
    """Each row's latent score: the trend over its person's time, its person's level, a lag-one series over its person's rows."""
    slope = float(model["slope"])
    person_var = float(model["person"])
    noise_var = float(model["noise"])
    lag = float(model["lag"])
    person_sd = math.sqrt(person_var) if person_var > 0.0 else 0.0
    noise_sd = math.sqrt(noise_var) if noise_var > 0.0 else 0.0
    innovation = math.sqrt(max(0.0, 1.0 - lag * lag))
    by: "dict[int, list[tuple[float, int]]]" = {}
    for row in rows_k:
        owner = owners[row]
        if owner not in by:
            by[owner] = []
        by[owner] += [(times[row], row)]
    out: "dict[int, float]" = {}
    for owner in sorted(by):
        series = sorted(by[owner])
        name = people[series[0][1]]
        state = inside_trajectories.stream_of(seed, inside_trajectories.name_salt(salt + _SEP + name))
        level = person_sd * inside_trajectories.next_normal(state)
        noise = 0.0
        for at in range(len(series)):
            fresh = inside_trajectories.next_normal(state)
            noise = fresh if at == 0 else lag * noise + innovation * fresh
            time, row = series[at]
            out[row] = slope * time + level + noise_sd * noise
    return out


def _states_dealt(groups_of: "dict[str, list[int]]", entry: "dict[str, typing.Any]", state: "list[int]",
                  written: "list[str]") -> "dict[str, list[int]]":
    """Each group's rows that hold a word or an empty cell (exact shares), written; the rest returned for numbers."""
    numbered: "dict[str, list[int]]" = {}
    groups = _object(entry["groups"])
    for group in sorted(groups_of):
        rows_g = groups_of[group]
        if group not in groups:
            numbered[group] = rows_g
            continue
        part = _object(groups[group])
        marginal = _object(part["marginal"])
        states = [(_text(_list(pair)[0]), int(_list(pair)[1])) for pair in _list(part["states"])]
        weights = [count for _cell, count in states] + [int(marginal["plain"]) + sum(
            int(_list(pair)[1]) for pair in _list(marginal["low"])) + sum(int(_list(pair)[1]) for pair in _list(marginal["high"]))]
        dealt = _largest_remainders(weights, len(rows_g))
        plan: "list[int]" = []
        for place in range(len(dealt)):
            plan += [place for _count in range(dealt[place])]
        plan = _shuffled(plan, state)
        numbered[group] = []
        for at in range(len(rows_g)):
            if plan[at] < len(states):
                written[rows_g[at]] = states[plan[at]][0]
            else:
                numbered[group] += [rows_g[at]]
    return numbered


def _ranked_cells(rows_g: "list[int]", latents: "dict[int, float]", drawn: _Drawn, state: "list[int]",
                  cap: int) -> "dict[int, str]":
    order = [row for _latent, row in sorted((latents[row], row) for row in rows_g)]
    out: "dict[int, str]" = {}
    count = len(order)
    for rank in range(count):
        out[order[rank]] = _drawn_cell(drawn, (rank + 0.5) / count, state, cap)
    return out


def numbers_and_rules(zone: "dict[str, object]", cells: "dict[str, list[str]]", seed: int) -> "dict[str, list[str]]":
    """Step two: each modelled row's numbers and pairs from its level's marginal by the latent order, then every flag and copy by its rule.

    `cells` holds the twin as written so far (persons, key, label cells,
    and the anchor's dates written by the dates zone). Returns every
    column the zone writes. Raises KeyedError where the zone does not fit.
    """
    person = _text(zone["person"])
    key = _text(zone["key"])
    if person not in cells or key not in cells:
        raise KeyedError("The inside record's keyed zone names a column this twin does not hold.")
    people = [_bare(cell) for cell in cells[person]]
    owners, persons = _persons(people)
    times = _time_axis(zone, cells, owners, persons)
    out: "dict[str, list[str]]" = {}
    by_level = _level_rows(zone, cells[key])
    levels = _levels_by_spelling(zone)

    for level_name in sorted(by_level):
        level = levels[level_name]
        rows_k = by_level[level_name]
        salt = key + _SEP + level_name
        numbers = _object(level["numbers"])
        for name in sorted(numbers):
            entry = _object(numbers[name])
            written = _column(out, cells, name)
            scale = _text(entry["scale"])
            groups_of: "dict[str, list[int]]" = {}
            for row in rows_k:
                group = _bare(_column(out, cells, scale)[row]) if scale else ""
                if group not in groups_of:
                    groups_of[group] = []
                groups_of[group] += [row]
            state = inside_trajectories.stream_of(seed, inside_trajectories.name_salt(salt + _SEP + name))
            numbered = _states_dealt(groups_of, entry, state, written)
            latents = _latents(_object(entry["model"]), rows_k, owners, times, seed, salt + _SEP + name, people)
            groups = _object(entry["groups"])
            for group in sorted(numbered):
                part = groups[group] if group in groups else _largest_group(groups)
                drawn = _drawn_of(_object(_object(part)["marginal"]))
                ranked = _ranked_cells(numbered[group], latents, drawn, state, int(entry["cap"]))
                for row in ranked:
                    written[row] = ranked[row]
        pairs = _object(level["pairs"])
        for name in sorted(pairs):
            entry = _object(pairs[name])
            written = _column(out, cells, name)
            first = _object(entry["first"])
            second = _object(entry["second"])
            scale = _text(first["scale"])
            groups_of = {}
            for row in rows_k:
                group = _bare(_column(out, cells, scale)[row]) if scale else ""
                if group not in groups_of:
                    groups_of[group] = []
                groups_of[group] += [row]
            state = inside_trajectories.stream_of(seed, inside_trajectories.name_salt(salt + _SEP + name))
            numbered = _states_dealt(groups_of, first, state, written)
            latents = _latents(_object(entry["model"]), rows_k, owners, times, seed, salt + _SEP + name, people)
            corr = float(entry["corr"])
            rest = math.sqrt(max(0.0, 1.0 - corr * corr))
            spread = _spread_of([latents[row] for row in rows_k])
            cap = int(entry["cap"])
            for group in sorted(numbered):
                rows_g = numbered[group]
                firsts = _object(first["groups"])
                seconds = _object(second["groups"])
                part_one = firsts[group] if group in firsts else _largest_group(firsts)
                part_two = seconds[group] if group in seconds else _largest_group(seconds)
                one = _ranked_cells(rows_g, latents, _drawn_of(_object(_object(part_one)["marginal"])), state, cap)
                second_latents: "dict[int, float]" = {}
                for row in rows_g:
                    second_latents[row] = corr * latents[row] / spread + rest * inside_trajectories.next_normal(state)
                two = _ranked_cells(rows_g, second_latents, _drawn_of(_object(_object(part_two)["marginal"])), state,
                                    cap)
                for row in rows_g:
                    written[row] = one[row] + "/" + two[row]
        intervals = _object(level["intervals"]) if "intervals" in level else {}
        for flag_name in sorted(intervals):
            rule = _object(intervals[flag_name])
            values = _column(out, cells, _text(rule["of"]))
            others = [_text(name) for name in _list(rule["by"])]
            groups = _object(rule["groups"])
            written = _column(out, cells, flag_name)
            for row in rows_k:
                joined = _joined([_bare(_column(out, cells, name)[row]) for name in others])
                if joined not in groups:
                    continue
                bounds = _object(groups[joined])
                value = plain_number(values[row])
                if value is None:
                    written[row] = _text(bounds["other"])
                    continue
                label = _text(bounds["last"])
                for cut in _list(bounds["cuts"]):
                    if value < float(_list(cut)[0]):
                        label = _text(_list(cut)[1])
                        break
                written[row] = label
    _gaps_written(zone, cells, out, by_level, levels, seed)
    for rule_entry in _list(zone["copies"]):
        rule = _object(rule_entry)
        source = _column(out, cells, _text(rule["from"]))
        copy = _column(out, cells, _text(rule["column"]))
        sentinel = _text(rule["else"])
        modelled = by_level
        for level_name in sorted(modelled):
            for row in modelled[level_name]:
                copy[row] = _bare(source[row]) if plain_number(source[row]) is not None else sentinel
    return out


def _gaps_written(zone: "dict[str, object]", cells: "dict[str, list[str]]", out: "dict[str, list[str]]",
                  by_level: "dict[str, list[int]]", levels: "dict[str, dict[str, typing.Any]]", seed: int) -> None:
    """Each modelled row's later clocks: its level's gap after the anchor, present where its level (or a label) says so."""
    anchor = _text(zone["anchor"])
    chained = _list(zone["gaps"]) if "gaps" in zone else []
    if not anchor or not chained or anchor not in cells:
        return
    read = _minute_stamps(cells[anchor])
    if read is None:
        return
    anchor_minutes = read[0]
    for pair in chained:
        name = _text(_list(pair)[0])
        joint = _text(_list(pair)[1])
        written = _column(out, cells, name)
        for level_name in sorted(by_level):
            level = levels[level_name]
            held = _object(level["gaps"]) if "gaps" in level else {}
            if name not in held:
                continue
            entry = _object(held[name])
            pooled = [int(value) for value in _list(entry["grid"])]
            split_by = _text(entry["split_by"]) if "split_by" in entry else ""
            grids = _object(entry["grids"]) if "grids" in entry else {}
            present, rows_seen = int(_list(entry["present"])[0]), int(_list(entry["present"])[1])
            rule = _text(entry["by"])
            shares = _object(entry["present_by"])
            state = inside_trajectories.stream_of(seed, inside_trajectories.name_salt(level_name + _SEP + name))
            for row in by_level[level_name]:
                start = anchor_minutes[row]
                u = inside_trajectories.next_uniform(state)
                if rule:
                    cell = _bare(_column(out, cells, rule)[row])
                    split = _list(shares[cell]) if cell in shares else [present, rows_seen]
                    shown = int(split[0]) * 2 >= int(split[1])
                else:
                    shown = u * rows_seen < present
                if start is None or not shown:
                    written[row] = ""
                    continue
                grid = pooled
                if split_by:
                    cell = _bare(_column(out, cells, split_by)[row])
                    if cell in grids:
                        grid = [int(value) for value in _list(grids[cell])]
                gap = grid[min(len(grid) - 1, int(inside_trajectories.next_uniform(state) * len(grid)))]
                written[row] = inside_trajectories.moment_text((start + gap) * 60, inside_trajectories.KIND_MINUTE,
                                                               joint)


def _column(out: "dict[str, list[str]]", cells: "dict[str, list[str]]", name: str) -> "list[str]":
    """The cells of a column the zone writes: its copy in `out`, made from the twin's cells at first use."""
    if name not in out:
        if name not in cells:
            raise KeyedError("The inside record's keyed zone names a column this twin does not hold.")
        out[name] = [cell for cell in cells[name]]
    return out[name]


def _largest_group(groups: "dict[str, typing.Any]") -> object:
    best, most = None, -1
    for name in sorted(groups):
        marginal = _object(_object(groups[name])["marginal"])
        if int(marginal["plain"]) > most:
            best, most = groups[name], int(marginal["plain"])
    return best


def _spread_of(values: "list[float]") -> float:
    if len(values) < 2:
        return 1.0
    mean = math.fsum(values) / len(values)
    spread = math.sqrt(math.fsum([(value - mean) * (value - mean) for value in values]) / len(values))
    return spread if spread > 0.0 else 1.0


def read_columns(zone: "dict[str, object]") -> "list[str]":
    """The columns the zone reads but does not write: the labels that decide a later clock's presence or split its gap."""
    out: "list[str]" = []
    for entry in _list(zone["levels"]):
        level = _object(entry)
        held = _object(level["gaps"]) if "gaps" in level else {}
        for name in sorted(held):
            gap = _object(held[name])
            for label in (_text(gap["by"]), _text(gap["split_by"]) if "split_by" in gap else ""):
                if label and label not in out:
                    out += [label]
    return out


def written_columns(zone: "dict[str, object]") -> "list[str]":
    """Every column the zone may write: the person column, the content columns and every copy."""
    out = [_text(zone["person"])]
    for name in _list(zone["content"]):
        out += [_text(name)]
    for rule in _list(zone["copies"]):
        out += [_text(_object(rule)["column"])]
    for pair in (_list(zone["gaps"]) if "gaps" in zone else []):
        out += [_text(_list(pair)[0])]
    for name in (_list(zone["constant"]) if "constant" in zone else []):
        out += [_text(name)]
    return out
