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

A key block the description holds as identifiers (an answered or an open
question offering `identifier`) is NEVER modelled, whatever its values
repeat across persons (lane IN-4b, batch 4x's outside review, item 1: a
name repeats across the persons a clinician sees): that column's cells at
that level stay the description's twin's made-up ones, while the level's
other columns are modelled. So is a key block the description holds by a
privacy mark of its own (a year cut, an age's words, a withheld count:
batch 4y's fix round), a column whose cells at a level read as dates, and
a column of more than `LABELS_MOST` spellings at a level. A column the
description publishes key by key (`by_key`) is named in `scoped`. A level
or a column the description top-codes at 90 (an age, Safe Harbor) is
written so here too, a copy's own levels among them; a copy any of whose
own key blocks the description holds is not written. The zone's size
follows columns, levels and grids, never rows.

HOW THE TWIN READS IT (lane IN-4b), in two steps of
`generation.generate_inside` (the dates zone, lane IN-5, writes the dates
between them). The zone writes no person and no spelling of its own: the
persons are the description's twin's, never re-cut (item 5), and every
column it deals holds that twin's own cells -- a `scoped` column on each
key level's rows, any other over the rows of the keys it types -- the
zone deciding only which row holds which cell, as the relations zone
does (lane IN-2b). (1) `persons_and_labels`: a `scoped` column moved with
its key where the relations zone moved the key, and each row's label
cells dealt toward its key level's joint table; (2) `numbers_and_rules`,
on the time axis the dates zone wrote: each level's numbers dealt in the
order of a latent score that carries the trend, the person's level and
the lag (a number the deal leaves on the scale of another label's group
written at its row's place on its own scale, in the cell's own written
form, never past a top code: item 2), every flag dealt toward its
intervals, each later clock moved to its level's gap after the anchor
keeping the dates zone's presence, form and month on every row (item 6),
and each copy written by its rule where no level of its source is held.
Every random quantity comes from SplitMix64 words seeded by the twin's
seed; the arithmetic is binary64 `+ - * /` and `sqrt` in the order
written, with the shared module's logarithm and normal quantile, so a
twin is the same on every machine.

NOTHING HERE PRINTS A VALUE. The producer returns the zone, the
generator returns cells; neither writes a line.
"""

import dataclasses
import math
import typing

from synthtwin import chain_walk, inside_dates, inside_trajectories, parsing

ZONE = "keyed"
# Version 2 (lane IN-4b): no census of persons, `scoped` columns, a level's held columns, gaps without a presence
# rule, a copy's top code. Version 3 (batch 4y's fix round): a level's blocks held by a privacy mark of their own,
# and a copy's own holds key by key (its levels top-coded at 90, a copy any of whose blocks is held left unwritten);
# a zone of version 2 lacks them, so it is refused as every zone of another version is, and the twin keeps the
# description's keyed values.
ZONE_VERSION = 3
KEY_LEVELS_LEAST = 3
KEY_LEVELS_MOST = 1000
MODELLED_LEVELS_MOST = 300
KEY_SAMPLE = 20000
# The written cells a key level holds before its reading counts toward the key typing a column (`key_of`).
TYPED_WRITTEN_LEAST = 20
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
# A key block the description holds by a privacy mark of its own (a year cut, an age's words, a withheld count, a
# Safe Harbor top code other than an age's 90): never modelled, its rows keeping the description's twin's cells
# (batch 4y's fix round, Codex's review of the batch, item 3).
KEPT_PRIVACY = "held for privacy"
_SEP = "\x1f"
_ZONE_KEYS = ("anchor", "axis", "content", "copies", "gaps", "key", "levels", "person", "rows", "scoped", "version")


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


def _typed_by(key_cells: "list[str]", cells: "list[str]", written_least: int = 0) -> bool:
    """Whether a key types a column's value: its reading (number or word) or its scale (the logarithm of its number) set by the key.

    A level is read only where it holds ``written_least`` written cells
    or more (nought: every level, as `_moved_by` reads it), and its share
    of numbers only where it holds 20 rows; `key_of` asks
    `TYPED_WRITTEN_LEAST` (lane W5-302), so a level whose cells are all or
    nearly all empty, which says nothing of how the column's values are
    written, never makes a key: neither by a share of nought among no
    written cell nor by the spread of three or four values between a few
    such levels.
    """
    by = _by_level(key_cells, cells)
    shares: "list[float]" = []
    groups: "dict[str, list[float]]" = {}
    numbered = 0
    present = 0
    for level in sorted(by):
        level_cells = by[level]
        values: "list[float]" = []
        written = 0
        for cell in level_cells:
            if _bare(cell):
                written += 1
            value = _leading(cell)
            if value is not None:
                values += [_log_size(value)]
        if written < written_least:
            continue
        if len(level_cells) >= 20:
            shares += [_numeric_share(level_cells)]
        present += written
        numbered += len(values)
        groups[level] = values
    if shares and max(shares) >= NUMERIC_SHARE and min(shares) <= 1.0 - NUMERIC_SHARE:
        return True
    return present > 0 and numbered >= 0.5 * present and _between_share(groups) >= KEYED_SHARE


@dataclasses.dataclass(frozen=True)
class _Read:
    """A column's cells as `_typed_by` reads them, each read once: written, numeric where written, the logarithm of its number."""

    written: "list[bool]"
    numeric: "list[bool]"
    sized: "list[float | None]"


def _read(cells: "list[str]") -> _Read:
    written: "list[bool]" = []
    numeric: "list[bool]" = []
    sized: "list[float | None]" = []
    for cell in cells:
        bare = _bare(cell)
        written += [bool(bare)]
        numeric += [bool(bare) and _position(cell) is not None]
        value = _leading(cell)
        sized += [_log_size(value) if value is not None else None]
    return _Read(written, numeric, sized)


def _places_by_level(key_cells: "list[str]") -> "list[tuple[str, list[int]]]":
    """Each level of a key with its rows in order, the levels sorted (as `_typed_by` walks them)."""
    by: "dict[str, list[int]]" = {}
    for row in range(len(key_cells)):
        level = key_cells[row]
        if level not in by:
            by[level] = []
        by[level] += [row]
    return [(level, by[level]) for level in sorted(by)]


def _typed_by_read(places: "list[tuple[str, list[int]]]", read: _Read, written_least: int = 0) -> bool:
    """`_typed_by` of a key whose levels' rows are `places` (`_places_by_level`) and a column `_read` once: the same answer."""
    shares: "list[float]" = []
    groups: "dict[str, list[float]]" = {}
    numbered = 0
    present = 0
    for level, rows in places:
        values: "list[float]" = []
        written = 0
        numeric = 0
        for row in rows:
            if read.written[row]:
                written += 1
                if read.numeric[row]:
                    numeric += 1
            value = read.sized[row]
            if value is not None:
                values += [value]
        if written < written_least:
            continue
        if len(rows) >= 20:
            shares += [numeric / written if written else 0.0]
        present += written
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
    """The key of a long table: the content label of `KEY_LEVELS_LEAST` to `KEY_LEVELS_MOST` levels, moving within persons, that types a value (`_typed_by`) and moves the most other content columns (`_moved_by`); '' where none does.

    A label types a value only where its levels are written
    (`TYPED_WRITTEN_LEAST` written cells a level, lane W5-302):
    a column empty on most rows -- a test written for a few patients --
    holds levels with no written cell, and those once read as a column
    "typed" by every label beside it, so a wide table without any key
    took a clock or a code for one. A label that types no column is no
    key, and the columns it moves are not counted (the count decides
    only between labels that type one), so a wide table spends one pass
    a label instead of two. Guarantees: a fixed function of the columns'
    cells on `key_sample_rows` and their persons; reads nothing else;
    raises nothing but what its helpers raise on a cell that is not text.
    """
    rows = len(owners)
    sample = _spread_rows(rows, KEY_SAMPLE)
    cut: "dict[str, list[str]]" = {}
    for name in content:
        whole = columns[name]
        cut[name] = [_bare(whole[row]) for row in sample]
    cut_owners = [owners[row] for row in sample]
    # Each column's cells read once (`_Read`), not once a label (lane W5-302): the typing of a column by every label
    # is then a pass over row places.
    readings: "dict[str, _Read]" = {}
    best, best_score = "", 0
    for key in content:
        cells = cut[key]
        levels = _counts(cells)
        if not KEY_LEVELS_LEAST <= len(levels) <= KEY_LEVELS_MOST:
            continue
        if _numeric_share(cells) >= 0.5 or not _varies_within(cells, cut_owners):
            continue
        places = _places_by_level(cells)
        typed = False
        for other in content:
            if other == key:
                continue
            if other not in readings:
                readings[other] = _read(cut[other])
            if _typed_by_read(places, readings[other], TYPED_WRITTEN_LEAST):
                typed = True
                break
        if not typed:
            continue
        score = 0
        for other in content:
            if other != key and _moved_by(cells, cut[other]):
                score += 1
        if score > best_score:
            best, best_score = key, score
    return best


def key_sample_rows(rows: int) -> "list[int]":
    """The rows of a table of ``rows`` rows that `key_of` reads: every row up to `KEY_SAMPLE`, else that many spread evenly."""
    return _spread_rows(rows, KEY_SAMPLE)


def sampled_key(person_cells: "list[str]", sampled: "dict[str, list[str]]", person: str,
                skipped: "tuple[str, ...]" = (), dated: "tuple[str, ...]" = ()) -> str:
    """The key `build_zone` would find, read from the person column whole and each column's cells on `key_sample_rows` alone.

    THE TABLE IS NOT HELD WHOLE TO LEARN IT HOLDS NO KEY (lane W5-302).
    `build_zone` reads every column of the table whole as text, and most
    tables -- a wide export of 302 columns among them, 3.6 GB of text at
    200,000 rows -- hold no key, which `key_of` decides from at most
    `KEY_SAMPLE` rows. ``sampled`` holds each column of the table, in its
    order, at the rows `key_sample_rows(len(person_cells))` names;
    ``skipped`` and ``dated`` are `build_zone`'s. Returns the key
    `build_zone` reads at the same arguments with every column whole, or
    '' where it would return None for want of a person that repeats or of
    a key. Raises TypeError where a sampled column holds another number
    of rows; nothing else.
    """
    if not person or person not in sampled or not _repeats(person_cells):
        return ""
    owners, _persons_counted = _persons(person_cells)
    sample = _spread_rows(len(person_cells), KEY_SAMPLE)
    content = [name for name in sampled if name != person and name not in skipped and name not in dated]
    for name in content:
        if len(sampled[name]) != len(sample):
            raise TypeError("internal check: a sampled column holds another number of rows")
    return key_of(sampled, content, [owners[row] for row in sample])


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
    """The later clocks whose gap from the anchor the key moves: each level's gaps (split by the label that moves them
    most), put in its entry. Their presence is not modelled: the twin keeps the dates zone's (lane IN-4b, item 6)."""
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
            labels: "list[str]" = []
            for label in candidates:
                if 2 <= len(_counts([_bare(columns[label][row]) for row in rows])) <= SCALE_LABELS_MOST:
                    labels += [label]
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
            gaps_entry: "dict[str, object]" = {"grid": _gap_grid(gaps_of[level]), "split_by": split_by, "grids": grids}
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
                              "agreement": _agreement_of(cells),
                              "model": _model(z, times, owners, order),
                              "cap": TOP_CODE if (name in tops or name in level_tops) else 0}
    entry["pairs"] = pair_entries
    return entry


def _held_somewhere(blocks: "dict[str, dict[str, object]]") -> bool:
    """Whether any key block of a column the description publishes key by key is held as identifiers."""
    for level in sorted(blocks):
        block = blocks[level]
        if "identifier" in block and block["identifier"]:
            return True
    return False


def _kept_for_privacy(block: "dict[str, object]") -> bool:
    """Whether a key block as `key_blocks_of` reads it carries a privacy mark of its own (`PRIVACY_KEYS`, or a Safe
    Harbor top code other than an age's 90): such a block is never modelled (batch 4y's fix round)."""
    return "privacy" in block and block["privacy"] is True


def _agreement_of(cells: "list[str]") -> float:
    """The rank agreement of a pair column's two parts over its cells that are pairs (`parsing.rank_agreement`, the
    measure the description publishes as `part_agreements` and validation reads; lane IN-4c)."""
    firsts: "list[float]" = []
    seconds: "list[float]" = []
    for cell in cells:
        found = pair_of(cell)
        if found is None:
            continue
        first = plain_number(found[0])
        second = plain_number(found[1])
        if first is None or second is None:
            continue
        firsts += [first]
        seconds += [second]
    return parsing.rank_agreement(firsts, seconds)


def build_zone(columns: "dict[str, list[str]]", person: str, skipped: "tuple[str, ...]" = (),
               dated: "tuple[str, ...]" = (), tops: "dict[str, int] | None" = None,
               held: "dict[str, dict[str, dict[str, object]]] | None" = None,
               typed: "dict[str, str] | None" = None) -> "dict[str, object] | None":
    """The keyed zone of a long table, or None where the table holds no key (see the module's account).

    `columns` holds every column's cells as text; `person` names the
    column of persons (it must repeat); `skipped` the columns kept whole
    (record numbers, free text); `dated` the date columns (the first read
    on nine rows in ten is the time axis); `tops` the columns top-coded
    at 90; `held` each keyed value column's key blocks as the description
    holds them ({column: {folded level: {"identifier": bool, "top": int,
    "privacy": bool}}}, `key_blocks_of`); `typed` each column the
    description publishes key by key, with its key column (`typed_of`). A
    key block held as identifiers (lane IN-4b, item 1) or by a privacy mark
    of its own (batch 4y's fix round) is never modelled; a column published
    key by key under another key with any block held as identifiers is left
    out of the zone whole; a copy reads its own blocks (its levels' top
    codes, its holds).
    Guarantees: a fixed function of its inputs; no I/O. Raises nothing
    but TypeError on an internal mismatch.
    """
    if not person or person not in columns or not _repeats(columns[person]):
        return None
    rows = len(columns[person])
    owners, persons = _persons(columns[person])
    tops = tops or {}
    held = held or {}
    typed = typed or {}
    content = [name for name in columns if name != person and name not in skipped and name not in dated]
    for name in content:
        if len(columns[name]) != rows:
            raise TypeError("internal check: the columns of one table hold different numbers of rows")
    key = key_of(columns, content, owners)
    if not key:
        return None
    # A column published key by key under ANOTHER key whose blocks the description holds anywhere: its held cells
    # cannot be told apart by this key's levels, so the zone leaves the whole column to the description's twin.
    content = [name for name in content
               if not (name in typed and typed[name] != key and name in held and _held_somewhere(held[name]))]
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
    for rule in copies:
        # THE COPY'S OWN HOLDS, KEY BY KEY (batch 4y's fix round, Codex's review of the batch, item 2): a copy is
        # taken out of the modelled columns before their key blocks are read, so its own blocks are read here: the
        # rows of each key level whose block the description top-codes at 90 take no number past it, and a copy any
        # of whose blocks the description holds (as identifiers or by a privacy mark) is not written at all.
        destination = typing.cast(str, rule["column"])
        rule["cap"] = TOP_CODE if destination in tops else 0
        own = held[destination] if destination in held else {}
        capped = [level for level in sorted(own) if "top" in own[level] and own[level]["top"] == TOP_CODE]
        if capped:
            rule["capped"] = capped
        if _held_somewhere(own) or any([_kept_for_privacy(own[level]) for level in sorted(own)]):
            rule["held"] = True
    copied = [typing.cast(str, rule["column"]) for rule in copies]
    rest = [name for name in taken if name not in copied]
    scoped = [name for name in rest if name in typed and typed[name] == key]
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
        # THE COLUMNS HELD AT THIS LEVEL (lane IN-4b, batch 4x's outside review, item 1): a key block the
        # description holds as identifiers is never modelled, whatever its values repeat across persons (a name
        # repeats across the persons one clinician sees), and a column whose cells read as dates here is not
        # either; each keeps the description's twin's cells on this level's rows, while the level's other
        # columns are modelled.
        set_aside: "list[list[str]]" = []
        for name in rest:
            blocks = held[name] if name in held else {}
            block = blocks[folded] if folded in blocks else {}
            if "top" in block and block["top"] == TOP_CODE:
                level_tops[name] = TOP_CODE
            if "identifier" in block and block["identifier"]:
                set_aside += [[name, KEPT_IDENTIFIER]]
                continue
            # ...and a block held by a privacy mark of its own (a year cut: Codex's review of batch 4y, item 3,
            # birth years before the cut written from the record's marginal) is never modelled either.
            if _kept_for_privacy(block):
                set_aside += [[name, KEPT_PRIVACY]]
                continue
            cells = [_text(columns[name][row]) for row in level_rows]
            if _numeric_share(cells) < NUMERIC_SHARE and inside_dates.reading_of(cells) is not None:
                set_aside += [[name, KEPT_DATES]]
        aside = [pair[0] for pair in set_aside]
        built = _level_entry(columns, level_rows, [name for name in rest if name not in aside], owners, times, tops,
                             level_tops)
        built["level"] = level
        built["held"] = set_aside
        levels += [built]
    keyed_gaps = _keyed_gaps(columns, dated, anchor, by, levels,
                             [name for name in content if name != key and name not in constant])
    return {
        "version": ZONE_VERSION, "key": key, "person": person, "anchor": anchor, "axis": axis,
        "content": rest, "copies": copies, "levels": levels, "rows": rows, "gaps": keyed_gaps, "scoped": scoped,
    }


def key_blocks_of(document: object) -> "tuple[dict[str, int], dict[str, dict[str, dict[str, object]]]]":
    """From a description written: the columns top-coded at 90, and each keyed value column's key blocks' holds and top codes.

    Each key block reads as {"identifier": held as identifiers, "top": its
    top code, "privacy": whether it carries any other privacy mark of its
    own (`PRIVACY_KEYS`: a year cut, an age's words, a withheld count; or
    a top code other than 90)} -- every safety mark a nested block keeps
    reaches the zone (batch 4y's fix round, Codex's review of the batch,
    item 3: a block's year cut was dropped here). Raises nothing.
    """
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
            privacy = top not in (0, TOP_CODE)
            for mark in PRIVACY_KEYS:
                if mark in inner and inner[mark]:
                    privacy = True
            read[fold(each["key"])] = {"identifier": role == "identifier" or structural == "identifier", "top": top,
                                       "privacy": privacy}
        held[name] = read
    return tops, held


def typed_of(document: object) -> "dict[str, str]":
    """From a description written: each column it publishes key by key (`by_key`), with the name of its key column."""
    out: "dict[str, str]" = {}
    columns = document["columns"] if isinstance(document, dict) and "columns" in document else None
    if not isinstance(columns, list):
        return out
    for block in columns:
        if not isinstance(block, dict) or "name" not in block or not isinstance(block["name"], str):
            continue
        by_key = block["by_key"] if "by_key" in block else None
        if isinstance(by_key, dict) and "key" in by_key and isinstance(by_key["key"], str):
            out[block["name"]] = by_key["key"]
    return out


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
#
# THE DESCRIPTION'S TWIN'S OWN CELLS (lane IN-4b, after batch 4x's outside review, items 1, 2, 5 and 6, and the
# landing's validation of the keyed tables): the zone writes no person and no spelling of its own choosing. Each
# column it deals keeps the description's twin's cells for it -- a column the description publishes key by key
# (`scoped`) on each key level's rows, any other over every row whose key is written -- and the zone decides only
# which row holds which (`_dealt`, `_numbers_dealt`), as the relations zone does (lane IN-2b). So every count and
# written form the description publishes for those columns stands, a held block keeps its made-up cells, and the
# persons are the twin's. Two writings are bounded exceptions: a number a deal leaves on the scale of another label's
# group is written at its row's place on its own scale in the cell's own written form, never past a top code
# (`_in_form`); a copy is written by its rule from its source's cells where no level of the source is held.


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


def _scoped(zone: "dict[str, object]") -> "list[str]":
    """The columns the description publishes key by key on this zone's key."""
    return [_text(name) for name in _list(zone["scoped"])]


def _current(out: "dict[str, list[str]]", cells: "dict[str, list[str]]", name: str) -> "list[str]":
    """A column's cells as the zone has them now: its own writing where it wrote it, the twin's otherwise."""
    if name in out:
        return out[name]
    if name in cells:
        return cells[name]
    raise KeyedError("The inside record's keyed zone names a column this twin does not hold.")


def capped_anywhere(zone: "dict[str, object]", name: str) -> bool:
    """Whether a level of the zone writes `name` under a top code (a key block the description top-codes at 90)."""
    for entry in _list(zone["levels"]):
        level = _object(entry)
        for kind in ("numbers", "pairs"):
            entries = _object(level[kind]) if kind in level else {}
            if name in entries and int(_object(entries[name])["cap"]):
                return True
    return False


def held_anywhere(zone: "dict[str, object]", name: str) -> bool:
    """Whether a level of the zone leaves `name` held as identifiers (its block made up in the twin)."""
    for entry in _list(zone["levels"]):
        level = _object(entry)
        for pair in (_list(level["held"]) if "held" in level else []):
            if _text(_list(pair)[0]) == name and _text(_list(pair)[1]) == KEPT_IDENTIFIER:
                return True
    return False


def _realigned(value: "list[str]", original: "list[str]", current: "list[str]") -> "list[str]":
    """A column published key by key, moved with its key (the relations zone deals a key column anew): a row whose key
    spelling did not move keeps its cell, and a row whose spelling moved takes, in row order, the cells of the rows
    that left that spelling, which the description's twin wrote under it. Raises KeyedError where the key's
    spellings are not the same multiset on both sides."""
    if len(value) != len(original) or len(current) != len(original):
        raise KeyedError("The inside record's keyed zone does not fit this twin's rows.")
    leaving: "dict[str, list[int]]" = {}
    for row in range(len(original)):
        if original[row] != current[row]:
            spelling = original[row]
            if spelling not in leaving:
                leaving[spelling] = []
            leaving[spelling] += [row]
    taken: "dict[str, int]" = {}
    out = [cell for cell in value]
    for row in range(len(current)):
        if original[row] == current[row]:
            continue
        spelling = current[row]
        rows = leaving[spelling] if spelling in leaving else []
        at = taken[spelling] if spelling in taken else 0
        if at >= len(rows):
            raise KeyedError("The inside record's keyed zone does not fit this twin's rows.")
        out[row] = value[rows[at]]
        taken[spelling] = at + 1
    return out


def _drawn_rank(key: str, key_cells: "list[str]", seed: int) -> "dict[int, int]":
    """Each row that holds a key, at its place in the order the seed draws (the order every deal serves rows in)."""
    rows = [row for row in range(len(key_cells)) if _bare(key_cells[row])]
    order = _shuffled(rows, inside_trajectories.stream_of(seed, inside_trajectories.name_salt(key + _SEP + "deal")))
    rank: "dict[int, int]" = {}
    for place in range(len(order)):
        rank[order[place]] = place
    return rank


def _in_order(rows: "list[int]", rank: "dict[int, int]") -> "list[int]":
    """Rows in the drawn order (a row the order does not hold after every one it does, in row order)."""
    last = len(rank)
    return [row for _place, row in sorted((rank[row] if row in rank else last + row, row) for row in rows)]


def _unmodelled(rank: "dict[int, int]", by_level: "dict[str, list[int]]") -> "list[int]":
    """The rows that hold a key the zone does not model (past the levels modelled, or a spelling it does not know)."""
    modelled: "dict[int, int]" = {}
    for level_name in by_level:
        for row in by_level[level_name]:
            modelled[row] = 1
    return [row for row in sorted(rank) if row not in modelled]


def _plan(weights: "list[int]", rows: int, state: "list[int]") -> "list[int]":
    """Each of `rows` places' entry of `weights`, in exact shares (largest remainders), in the order the stream draws."""
    if sum(weights) <= 0:
        return [len(weights) - 1 for _row in range(rows)]
    dealt = _largest_remainders(weights, rows)
    plan: "list[int]" = []
    for place in range(len(dealt)):
        plan += [place for _count in range(dealt[place])]
    return _shuffled(plan, state)


def _tuple_wants(zone: "dict[str, object]", by_level: "dict[str, list[int]]",
                 levels: "dict[str, dict[str, typing.Any]]", seed: int) -> "dict[str, dict[int, str]]":
    """Each modelled row's label cells as its key level's joint table deals them (exact shares, in an order the seed draws)."""
    key = _text(zone["key"])
    wanted: "dict[str, dict[int, str]]" = {}
    for level_name in sorted(by_level):
        level = levels[level_name]
        rows_k = by_level[level_name]
        label_names = [_text(name) for name in _list(level["labels"])]
        for name in label_names:
            if name not in wanted:
                wanted[name] = {}
        level_state = inside_trajectories.stream_of(seed, inside_trajectories.name_salt(key + _SEP + level_name))
        if "tuples" in level:
            table = _list(level["tuples"])
            plan = _plan([int(_list(entry)[1]) for entry in table], len(rows_k), level_state)
            for at in range(len(rows_k)):
                chosen = _list(_list(table[plan[at]])[0])
                for k in range(len(label_names)):
                    wanted[label_names[k]][rows_k[at]] = _text(chosen[k])
        else:
            apart = _object(level["apart"])
            for name in label_names:
                table = _list(apart[name])
                plan = _plan([int(_list(entry)[1]) for entry in table], len(rows_k), level_state)
                for at in range(len(rows_k)):
                    wanted[name][rows_k[at]] = _text(_list(table[plan[at]])[0])
    return wanted


def _spellings_at(level: "dict[str, typing.Any]", name: str) -> "list[str]":
    """A label's spellings at a level, commonest first: its joint table's, or its flag rule's labels."""
    counts: "dict[str, int]" = {}
    label_names = [_text(each) for each in _list(level["labels"])] if "labels" in level else []
    if "tuples" in level:
        for k in range(len(label_names)):
            if label_names[k] != name:
                continue
            for entry in _list(level["tuples"]):
                cell = _text(_list(_list(entry)[0])[k])
                counts[cell] = (counts[cell] if cell in counts else 0) + int(_list(entry)[1])
    elif "apart" in level:
        apart = _object(level["apart"])
        if name in apart:
            for pair in _list(apart[name]):
                cell = _text(_list(pair)[0])
                counts[cell] = (counts[cell] if cell in counts else 0) + int(_list(pair)[1])
    intervals = _object(level["intervals"]) if "intervals" in level else {}
    if name in intervals:
        groups = _object(_object(intervals[name])["groups"])
        for joined in sorted(groups):
            bounds = _object(groups[joined])
            named = [_text(_list(cut)[1]) for cut in _list(bounds["cuts"])]
            named += [_text(bounds["last"]), _text(bounds["other"])]
            for cell in named:
                counts[cell] = (counts[cell] if cell in counts else 0) + 1
    return [cell for _count, cell in sorted((-counts[cell], cell) for cell in counts)]


def _dealt(rows: "list[int]", wanted: "dict[int, str]", have: "list[str]", level_of: "dict[int, str]",
           preferred: "dict[str, list[str]]") -> "dict[int, str]":
    """The cells `have` holds on `rows`, dealt anew among those rows (the same cells, each once).

    In the order `rows` comes in, a row takes the cell it is wanted to hold
    while one is left; then a row left takes one equal to it once trimmed
    and folded, else the commonest of its level's own spellings left
    (`preferred`, by the row's level in `level_of`); the rows still left
    take the cells left, commonest first. Raises nothing.
    """
    pool: "dict[str, int]" = {}
    for row in rows:
        cell = have[row]
        pool[cell] = (pool[cell] if cell in pool else 0) + 1
    out: "dict[int, str]" = {}
    left: "list[int]" = []
    for row in rows:
        if row in wanted:
            want = wanted[row]
            if want in pool and pool[want] > 0:
                out[row] = want
                pool[want] -= 1
                continue
        left += [row]
    if not left:
        return out
    by_fold: "dict[str, list[str]]" = {}
    for cell in sorted(pool):
        folded = fold(cell)
        if folded not in by_fold:
            by_fold[folded] = []
        by_fold[folded] += [cell]
    rest: "list[int]" = []
    for row in left:
        found = ""
        taken = False
        if row in wanted:
            folded = fold(wanted[row])
            for cell in (by_fold[folded] if folded in by_fold else []):
                if pool[cell] > 0:
                    found, taken = cell, True
                    break
            if not taken and row in level_of and level_of[row] in preferred:
                for cell in preferred[level_of[row]]:
                    if cell in pool and pool[cell] > 0:
                        found, taken = cell, True
                        break
        if taken:
            out[row] = found
            pool[found] -= 1
        else:
            rest += [row]
    remaining: "list[str]" = []
    for _count, cell in sorted((-pool[cell], cell) for cell in pool):
        for _copy in range(pool[cell]):
            remaining += [cell]
    for at in range(len(rest)):
        out[rest[at]] = remaining[at]
    return out


def _column_dealt(scoped: bool, wanted: "dict[int, str]", have: "list[str]", levels_of_name: "dict[str, list[int]]",
                  rank: "dict[int, int]", leftover: "list[int]", preferred: "dict[str, list[str]]") -> "list[str]":
    """One column dealt from the description's twin's own cells (`_dealt`): on each level's rows apart for a column
    published key by key, else over every listed level's rows at once, the rows of a key the zone does not model
    taking the cells left (so the cells over the keys the zone models are those its joint tables ask for)."""
    written = [cell for cell in have]
    level_of: "dict[int, str]" = {}
    for level_name in levels_of_name:
        for row in levels_of_name[level_name]:
            level_of[row] = level_name
    groups: "list[list[int]]" = []
    if scoped:
        for level_name in sorted(levels_of_name):
            groups += [_in_order(levels_of_name[level_name], rank)]
    else:
        every: "list[int]" = []
        for level_name in sorted(levels_of_name):
            every += levels_of_name[level_name]
        served = _in_order(every, rank)
        served += _in_order(leftover, rank)
        groups += [served]
    for rows in groups:
        dealt = _dealt(rows, wanted, have, level_of, preferred)
        for row in rows:
            written[row] = dealt[row]
    return written


def _flagged(zone: "dict[str, object]") -> "list[str]":
    """The columns some level rules by the intervals of a number: dealt in step two, once the numbers are."""
    out: "list[str]" = []
    for entry in _list(zone["levels"]):
        level = _object(entry)
        intervals = _object(level["intervals"]) if "intervals" in level else {}
        for name in sorted(intervals):
            if name not in out:
                out += [name]
    return out


def persons_and_labels(zone: "dict[str, object]", cells: "dict[str, list[str]]", seed: int,
                       original: "list[str] | None" = None) -> "dict[str, list[str]]":
    """Step one: each modelled row's label cells, dealt from the description's twin's own cells (lane IN-4b).

    The persons are the twin's as they stand: none is re-cut (batch 4x's
    outside review, item 5), so every column the relations zone drew
    against them keeps its sequences and its persons' values. Where the
    relations zone dealt the key column anew (`original` holds it as the
    description's twin wrote it), each column published key by key moves
    with its key first (`_realigned`). Then every label of a level's joint
    table -- but a column some level rules by a number's intervals, dealt in
    step two -- holds the same cells, each row taking the one its level's
    joint table deals it where the cells allow (`_column_dealt`). `cells`
    holds the twin's key column and the columns the zone deals, as written
    so far. Returns every column it wrote. Raises KeyedError where the zone
    does not fit the twin.
    """
    key = _text(zone["key"])
    if key not in cells:
        raise KeyedError("The inside record's keyed zone names a column this twin does not hold.")
    key_cells = cells[key]
    scoped = _scoped(zone)
    out: "dict[str, list[str]]" = {}
    if original is not None:
        if len(original) != len(key_cells):
            raise KeyedError("The inside record's keyed zone does not fit this twin's rows.")
        moved = False
        for row in range(len(key_cells)):
            if original[row] != key_cells[row]:
                moved = True
                break
        if moved:
            for name in scoped:
                if name in cells:
                    out[name] = _realigned(cells[name], original, key_cells)
    by_level = _level_rows(zone, key_cells)
    levels = _levels_by_spelling(zone)
    wanted = _tuple_wants(zone, by_level, levels, seed)
    later = _flagged(zone)
    rank = _drawn_rank(key, key_cells, seed)
    leftover = _unmodelled(rank, by_level)
    for name in sorted(wanted):
        if name in later:
            continue
        levels_of_name: "dict[str, list[int]]" = {}
        preferred: "dict[str, list[str]]" = {}
        for level_name in sorted(by_level):
            level = levels[level_name]
            if name in [_text(each) for each in _list(level["labels"])]:
                levels_of_name[level_name] = by_level[level_name]
                preferred[level_name] = _spellings_at(level, name)
        out[name] = _column_dealt(name in scoped, wanted[name], _current(out, cells, name), levels_of_name, rank,
                                  leftover, preferred)
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


def _place_of(cell: str) -> float:
    place = _position(cell)
    return place if place is not None else 0.0


def _plain_value(drawn: _Drawn, share: float) -> float:
    """The plain part's value at `share` of it (its value table by counts, or its grid read between points)."""
    if drawn.table:
        total = 0
        for _value, spellings in drawn.table:
            total += sum(count for _cell, count in spellings)
        point = share * total
        for value, spellings in drawn.table:
            held = sum(count for _cell, count in spellings)
            if point < held:
                return value
            point -= held
        return drawn.table[len(drawn.table) - 1][0]
    if not drawn.grid:
        return 0.0
    place = min(max(share, 0.0), 1.0) * (len(drawn.grid) - 1)
    low = int(place)
    high = low + 1 if low + 1 < len(drawn.grid) else low
    return drawn.grid[low] + (drawn.grid[high] - drawn.grid[low]) * (place - low)


def _target(drawn: _Drawn, share: float) -> float:
    """The place on its line of the marginal's cell at `share` of it: an atom at its place, a plain value at its own."""
    if drawn.total <= 0:
        return 0.0
    point = share * drawn.total
    for cell, count in drawn.low:
        if point < count:
            return _place_of(cell)
        point -= count
    if point < drawn.plain or not drawn.high:
        return _plain_value(drawn, point / drawn.plain if drawn.plain else 0.0)
    point -= drawn.plain
    for cell, count in drawn.high:
        if point < count:
            return _place_of(cell)
        point -= count
    return _place_of(drawn.high[len(drawn.high) - 1][0])


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


def _in_form(cell: str, value: float, cap: int) -> str:
    """`value` written in `cell`'s own written form, never past `cap` (an age's top code; lane IN-4b, item 2).

    The form is the cell's: its decimals, a sign written or not, a point
    with no figure before it. Where the form cannot carry the value (the
    cell is no plain number, its figures open with a nought that pads them,
    the value has a sign the cell does not, or a point with no figure
    before it would hold a value of 1 or more), the cell itself is
    returned. Raises nothing.
    """
    text = _bare(cell)
    if plain_number(text) is None:
        return cell
    if cap and value > cap:
        value = float(cap)
    sign = text[:1] if text[:1] in "+-" else ""
    body = text[len(sign):]
    whole, _point, _fraction = _point_parts(body)
    if len(whole) > 1 and whole[:1] == "0":
        return cell
    if (sign == "-") != (value < 0.0):
        return cell
    places = decimals_of(body)
    written = _written(abs(value), places)
    if not whole:
        if abs(value) >= 1.0 or written[:2] != "0.":
            return cell
        written = written[1:]
    written = sign + written
    if plain_number(written) is None or decimals_of(written[len(sign):]) != places:
        return cell
    return written


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


@dataclasses.dataclass
class _Want:
    """A row's part in a number's deal: the state (a word or an empty cell) it is dealt, else its place on its scale's
    line by the rank of its latent score; and its group's marginal, at which a plain number cell dealt to it is
    written in its own form (`written`: a number column's, not a pair's)."""

    row: int
    state: "str | None"
    place: float
    latent: float
    drawn: _Drawn
    written: bool
    cap: int
    share: float


def _number_wants(body: "dict[str, typing.Any]", model: "dict[str, typing.Any]", rows_k: "list[int]",
                  scales: "list[str] | None", owners: "list[int]", times: "list[float]", seed: int, salt: str,
                  people: "list[str]", cap: int, written: bool) -> "list[_Want]":
    """Each of a level's rows' part in one number column's deal: its group by the label that sets the number's scale
    (`scales`, that label's cells), the states its group deals in exact shares, and its place on its group's line
    at the rank of its latent score (the trend, the person's level, the lag)."""
    groups = _object(body["groups"])
    groups_of: "dict[str, list[int]]" = {}
    for row in rows_k:
        group = _bare(scales[row]) if scales is not None else ""
        if group not in groups_of:
            groups_of[group] = []
        groups_of[group] += [row]
    state = inside_trajectories.stream_of(seed, inside_trajectories.name_salt(salt))
    latents = _latents(model, rows_k, owners, times, seed, salt, people)
    out: "list[_Want]" = []
    for group in sorted(groups_of):
        named = group if group in groups else _largest_name(groups)
        part = _object(groups[named])
        drawn = _drawn_of(_object(part["marginal"]))
        states = [(_text(_list(pair)[0]), int(_list(pair)[1])) for pair in _list(part["states"])]
        rows_g = groups_of[group]
        plan = _plan([count for _cell, count in states] + [drawn.total], len(rows_g), state)
        stated: "dict[int, str]" = {}
        for at in range(len(rows_g)):
            if plan[at] < len(states):
                stated[rows_g[at]] = states[plan[at]][0]
        ranked = [row for _latent, row in sorted((latents[row], row) for row in rows_g)]
        for place in range(len(ranked)):
            row = ranked[place]
            share = (place + 0.5) / len(ranked)
            out += [_Want(row, stated[row] if row in stated else None, _target(drawn, share), latents[row], drawn,
                          written, cap, share)]
    return out


def _plain_share(drawn: _Drawn, share: float) -> float:
    """A share of a marginal read as a share of its plain part (its censoring atoms set aside)."""
    if drawn.plain <= 0:
        return 0.0
    low = 0
    for _cell, count in drawn.low:
        low += count
    return min(max((share * drawn.total - low) / drawn.plain, 0.0), 1.0)


def _cell_place(cell: str) -> "float | None":
    """A cell's place on its column's line for a number's deal: a number or an atom at itself, a pair at its first part."""
    place = _position(cell)
    if place is not None:
        return place
    found = pair_of(cell)
    return plain_number(found[0]) if found is not None else None


def _numbers_dealt(wants: "list[_Want]", have: "list[str]", rank: "dict[int, int]") -> "dict[int, str]":
    """One number column's cells on the wanted rows (the description's twin's), dealt anew among them.

    A row dealt a state takes it while the cells hold one (in the drawn
    order); the states left go to the rows dealt a state first, then to the
    others; every row left takes the number cells by rank: the row at the
    lowest place the lowest cell, and so on. A plain number cell so dealt is
    written at its row's place on its group's marginal (the record's, on the
    scale the row's label sets) in the cell's own written form (`_in_form`:
    its decimals, its sign, a point with no figure before it; never past a
    top code), so the level's written forms are the description's twin's and
    its values follow the record; an atom, a word, a pair or a cell whose form
    cannot carry the value stays the twin's. Raises KeyedError on an
    internal mismatch.
    """
    numbers: "list[tuple[float, str]]" = []
    states: "dict[str, int]" = {}
    by_row: "dict[int, _Want]" = {}
    for want in wants:
        by_row[want.row] = want
        cell = have[want.row]
        place = _cell_place(cell)
        if place is None:
            states[cell] = (states[cell] if cell in states else 0) + 1
        else:
            numbers += [(place, cell)]
    out: "dict[int, str]" = {}
    need: "list[int]" = []
    for row in _in_order([want.row for want in wants], rank):
        stated = by_row[row].state
        if stated is not None and stated in states and states[stated] > 0:
            out[row] = stated
            states[stated] -= 1
        else:
            need += [row]
    extra: "list[str]" = []
    for _count, cell in sorted((-states[cell], cell) for cell in states):
        for _copy in range(states[cell]):
            extra += [cell]
    first = [row for row in need if by_row[row].state is not None]
    first += [row for row in need if by_row[row].state is None]
    for at in range(len(extra)):
        out[first[at]] = extra[at]
    ranked = [row for _place, _latent, row in sorted(
        (by_row[row].place, by_row[row].latent, row) for row in need if row not in out)]
    numbers = sorted(numbers)
    if len(ranked) != len(numbers):
        raise KeyedError("internal check: a number's deal holds as many cells as rows")
    for at in range(len(ranked)):
        want = by_row[ranked[at]]
        place, cell = numbers[at]
        if want.written:
            cell = _carried(cell, _plain_value(want.drawn, _plain_share(want.drawn, want.share)), want.cap, want.drawn)
        out[want.row] = cell
    return out


def _carried(cell: str, value: float, cap: int, drawn: _Drawn) -> str:
    """`value` in `cell`'s own written form (`_in_form`), or in its level's own commonest form where the cell's form
    cannot carry it (lane STATS-B).

    A cell of a pooled stand-in written in whole numbers dealt to a level of
    thousandths wrote every value of the level as `0` (187 troponin cells of
    the battery's laboratory twin, whose real cells are `.012` and the like):
    where the form writes a value other than nought as nought, or more than
    half of it away, or with a number of decimals the level never writes (a
    whole number on a level written to one place, 119 C-reactive protein
    cells; a glucose's two units' forms crossed, 191), the value is written
    with its level's commonest decimals (`drawn.decimals`) and, where most of
    the level's cells write a point with no figure before it (`drawn.dotted`),
    so; never past `cap`. Raises nothing.
    """
    written = _in_form(cell, value, cap)
    shown = plain_number(written)
    own_places = [places for places, count in drawn.decimals if count > 0]
    foreign = bool(own_places) and shown is not None and decimals_of(f"{written}".strip().lstrip("+-")) not in own_places
    if shown is None or ((value == 0.0 or (shown != 0.0 and abs(shown - value) <= 0.5 * abs(value))) and not foreign):
        return written
    if cap and value > cap:
        value = float(cap)
    places = 0
    best = -1
    for count_places, count in drawn.decimals:
        if count > best:
            best, places = count, count_places
    own = _written(value, places)
    if plain_number(own) in (None, 0.0):
        return written
    if drawn.dotted * 2 > max(1, drawn.plain) and own[:2] == "0.":
        own = own[1:]
    elif drawn.dotted * 2 > max(1, drawn.plain) and own[:3] == "-0.":
        own = "-" + own[2:]
    return own


def _flags_dealt(zone: "dict[str, object]", cells: "dict[str, list[str]]", out: "dict[str, list[str]]",
                 by_level: "dict[str, list[int]]", levels: "dict[str, dict[str, typing.Any]]", seed: int,
                 rank: "dict[int, int]", leftover: "list[int]") -> None:
    """Each column some level rules by a number's intervals, dealt from the description's twin's own cells: a row
    of such a level wanted the label its number's interval names, a row of a level whose joint table holds the
    column wanted the label that table deals it (`_column_dealt`)."""
    later = _flagged(zone)
    if not later:
        return
    tuples = _tuple_wants(zone, by_level, levels, seed)
    scoped = _scoped(zone)
    for name in later:
        wanted: "dict[int, str]" = {}
        if name in tuples:
            for row in tuples[name]:
                wanted[row] = tuples[name][row]
        levels_of_name: "dict[str, list[int]]" = {}
        preferred: "dict[str, list[str]]" = {}
        for level_name in sorted(by_level):
            level = levels[level_name]
            intervals = _object(level["intervals"]) if "intervals" in level else {}
            if name in intervals:
                rule = _object(intervals[name])
                values = _current(out, cells, _text(rule["of"]))
                others = [_current(out, cells, _text(each)) for each in _list(rule["by"])]
                groups = _object(rule["groups"])
                for row in by_level[level_name]:
                    joined = _joined([_bare(other[row]) for other in others])
                    if joined not in groups:
                        continue
                    bounds = _object(groups[joined])
                    value = plain_number(values[row])
                    if value is None:
                        wanted[row] = _text(bounds["other"])
                        continue
                    label = _text(bounds["last"])
                    for cut in _list(bounds["cuts"]):
                        if value < float(_list(cut)[0]):
                            label = _text(_list(cut)[1])
                            break
                    wanted[row] = label
            elif name not in [_text(each) for each in _list(level["labels"])]:
                continue
            levels_of_name[level_name] = by_level[level_name]
            preferred[level_name] = _spellings_at(level, name)
        out[name] = _column_dealt(name in scoped, wanted, _current(out, cells, name), levels_of_name, rank, leftover,
                                  preferred)


def _gap_at(grid: "list[int]", share: float) -> int:
    """A gap in minutes at `share` of a level's gap grid, read between its points (a quantile function: the grid's
    top point, the largest gap seen, weighs no more than the gaps beside it), to the nearest whole minute."""
    place = min(max(share, 0.0), 1.0) * (len(grid) - 1)
    low = int(place)
    high = low + 1 if low + 1 < len(grid) else low
    # Rounded to the nearest minute on BOTH sides of nought (Codex's review of batch 4y, item 11): `int(x + 0.5)`
    # truncates toward nought, so a gap of -60 minutes read -59 and one of -1 read 0 (an event written at its
    # anchor's minute). The floor of `x + 0.5`, taken by `int` and one step down where `int` rounded up, is the
    # same number for every gap at or above nought.
    halfway = grid[low] + (grid[high] - grid[low]) * (place - low) + 0.5
    whole = int(halfway)
    return whole - 1 if whole > halfway else whole


def _month_of(seconds: int) -> "tuple[int, int]":
    year, month, _day = inside_trajectories.civil_from_days(seconds // 86400)
    return year, month


def _gaps_written(zone: "dict[str, object]", cells: "dict[str, list[str]]", out: "dict[str, list[str]]",
                  by_level: "dict[str, list[int]]", levels: "dict[str, dict[str, typing.Any]]", seed: int) -> None:
    """Each modelled row's later clocks moved to its level's gap after the anchor (lane IN-4b, item 6).

    The dates zone's presence stands on every row: an empty cell stays
    empty and a written one stays written. A written cell in the anchor's
    minute form is moved to the anchor's moment plus a gap from its level's
    grid (split by a label where one moves the gap), written in that cell's
    own form, where the new moment stays in the cell's month; any other cell
    keeps the dates zone's writing.
    """
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
        written = [cell for cell in _current(out, cells, name)]
        moved = False
        for level_name in sorted(by_level):
            level = levels[level_name]
            held = _object(level["gaps"]) if "gaps" in level else {}
            if name not in held:
                continue
            entry = _object(held[name])
            pooled = [int(value) for value in _list(entry["grid"])]
            split_by = _text(entry["split_by"]) if "split_by" in entry else ""
            grids = _object(entry["grids"]) if "grids" in entry else {}
            labels = _current(out, cells, split_by) if split_by else None
            state = inside_trajectories.stream_of(seed, inside_trajectories.name_salt(level_name + _SEP + name))
            for row in by_level[level_name]:
                draw = inside_trajectories.next_uniform(state)
                start = anchor_minutes[row]
                old = inside_trajectories.moment_of(written[row])
                if start is None or old is None or old.kind != inside_trajectories.KIND_MINUTE:
                    continue
                if inside_trajectories.moment_text(old.seconds, old.kind, old.joint) != written[row]:
                    continue
                grid = pooled
                if labels is not None and _bare(labels[row]) in grids:
                    grid = [int(value) for value in _list(grids[_bare(labels[row])])]
                if not grid:
                    continue
                seconds = (start + _gap_at(grid, draw)) * 60
                if _month_of(seconds) != _month_of(old.seconds):
                    continue
                written[row] = inside_trajectories.moment_text(seconds, inside_trajectories.KIND_MINUTE, old.joint)
                moved = True
        if moved:
            out[name] = written


def _copies_written(zone: "dict[str, object]", cells: "dict[str, list[str]]", out: "dict[str, list[str]]") -> None:
    """Each copy by its rule: the source's cell where it is a plain number (never past the copy's top code, the
    whole column's or its row's key level's), its sentinel elsewhere; a row whose two cells are both empty stays
    so. A copy whose source a level holds as identifiers is not written (its made-up cells would land in a published
    column), nor one any of whose own key blocks the description holds (batch 4y's fix round), nor one whose
    sentinel the description's twin does not write. A copy whose source a level writes under a top code IS written
    by its rule (lane STATS-B, reversing lane IN-4c's hold): its cells on that level's rows are the source's, so
    never past the source's top code, and a copy is never more than its source shows. Held back, the copy was the
    description's twin's own column, its sentinel on about one row in twelve of every test and its numbers no
    test's, so an analysis reading the copy (a potassium mean, the sentinel filtered out) read 25,927 against the
    real 4.1; written, the copy's own facts the cap moves (its numbers above 90 on the capped levels' rows) are the
    price."""
    for rule_entry in _list(zone["copies"]):
        rule = _object(rule_entry)
        origin = _text(rule["from"])
        copy_name = _text(rule["column"])
        if held_anywhere(zone, origin) or ("held" in rule and rule["held"] is True):
            continue
        source = _current(out, cells, origin)
        current = _current(out, cells, copy_name)
        sentinel = _text(rule["else"])
        cap = int(rule["cap"]) if "cap" in rule else 0
        capped = {_text(level): 1 for level in _list(rule["capped"])} if "capped" in rule else {}
        key_cells = _current(out, cells, _text(zone["key"])) if capped else []
        written_somewhere = not sentinel
        for cell in current:
            if _bare(cell) == sentinel:
                written_somewhere = True
                break
        if not written_somewhere:
            continue
        written = [cell for cell in current]
        for row in range(len(current)):
            if not _bare(source[row]) and not _bare(current[row]):
                continue
            value = plain_number(source[row])
            row_cap = TOP_CODE if capped and fold(key_cells[row]) in capped else cap
            written[row] = sentinel if value is None else _capped(_bare(source[row]), value, row_cap)
        out[copy_name] = written


def numbers_and_rules(zone: "dict[str, object]", cells: "dict[str, list[str]]", seed: int) -> "dict[str, list[str]]":
    """Step two: each modelled row's numbers and pairs, dealt from the description's twin's own cells by the latent
    order; then each flag dealt toward its intervals, each later clock moved to its level's gap, each copy written.

    `cells` holds the twin as written so far (persons, key, label cells,
    and the dates the dates zone wrote). Returns every column the zone
    writes. Raises KeyedError where the zone does not fit.
    """
    person = _text(zone["person"])
    key = _text(zone["key"])
    if person not in cells or key not in cells:
        raise KeyedError("The inside record's keyed zone names a column this twin does not hold.")
    people = [_bare(cell) for cell in cells[person]]
    owners, persons = _persons(people)
    times = _time_axis(zone, cells, owners, persons)
    scoped = _scoped(zone)
    out: "dict[str, list[str]]" = {}
    key_cells = cells[key]
    by_level = _level_rows(zone, key_cells)
    levels = _levels_by_spelling(zone)
    rank = _drawn_rank(key, key_cells, seed)
    wants_of: "dict[str, dict[str, list[_Want]]]" = {}
    for level_name in sorted(by_level):
        level = levels[level_name]
        rows_k = by_level[level_name]
        salt = key + _SEP + level_name
        for kind in ("numbers", "pairs"):
            entries = _object(level[kind]) if kind in level else {}
            for name in sorted(entries):
                entry = _object(entries[name])
                body = entry if kind == "numbers" else _object(entry["first"])
                scale = _text(body["scale"])
                wants = _number_wants(body, _object(entry["model"]), rows_k,
                                      _current(out, cells, scale) if scale else None, owners, times, seed,
                                      salt + _SEP + name, people, int(entry["cap"]), kind == "numbers")
                scope = level_name if name in scoped else ""
                if name not in wants_of:
                    wants_of[name] = {}
                if scope not in wants_of[name]:
                    wants_of[name][scope] = []
                wants_of[name][scope] += wants
    for name in sorted(wants_of):
        have = _current(out, cells, name)
        written = [cell for cell in have]
        for scope in sorted(wants_of[name]):
            dealt = _numbers_dealt(wants_of[name][scope], have, rank)
            for row in dealt:
                written[row] = dealt[row]
        out[name] = written
    # ...each level's pairs joined again at the record's correlation of their parts (lane IN-4c).
    for level_name in sorted(by_level):
        level = levels[level_name]
        entries = _object(level["pairs"]) if "pairs" in level else {}
        for name in sorted(entries):
            if name in out:
                _pairs_rejoined(out[name], by_level[level_name], _object(entries[name]), seed,
                                key + _SEP + level_name + _SEP + name)
    _flags_dealt(zone, cells, out, by_level, levels, seed, rank, _unmodelled(rank, by_level))
    _gaps_written(zone, cells, out, by_level, levels, seed)
    _copies_written(zone, cells, out)
    return out


def _pairs_rejoined(written: "list[str]", rows_k: "list[int]", entry: "dict[str, typing.Any]", seed: int,
                    salt: str) -> None:
    """A level's pair cells, joined again so their two parts move together as the record's do (lane IN-4c).

    The deal keeps each pair cell whole, so the two parts move together
    only as the description's twin paired them: a rank agreement held to
    its published value, but a pairing whose correlation fell short of the
    real one (measured on the battery's charting table: 0.823 against
    0.852). Here the level's first parts stay where the deal put them and
    the second parts -- the same spellings, none made -- are dealt again
    by the rank of a normal score that carries the record's correlation of
    the two parts' normal scores (`corr`): the first part's normal score
    times `corr`, plus a fresh normal draw times the rest. The new pairing
    stands only where it keeps the count of cells whose first part is the
    larger, and its rank agreement lies within half the validator's window
    of the record's (`agreement`); otherwise, and for a pair under a top
    code, a scale label, or a record written before this lane, the cells
    stay as dealt. Changes ``written`` in place. Raises nothing.
    """
    if "agreement" not in entry or int(entry["cap"]) or _text(_object(entry["first"])["scale"]):
        return
    corr = float(entry["corr"])
    target = float(entry["agreement"])
    rows = [row for row in rows_k if pair_of(written[row]) is not None]
    if len(rows) < 3:
        return
    firsts: "dict[int, tuple[float, str]]" = {}
    seconds: "list[tuple[float, str]]" = []
    above_before = 0
    for row in rows:
        found = pair_of(written[row])
        if found is None:
            return
        first = plain_number(found[0])
        second = plain_number(found[1])
        if first is None or second is None:
            return
        firsts[row] = (first, found[0])
        seconds += [(second, found[1])]
        above_before += int(first > second)
    ordered = [row for _first, row in sorted((firsts[row][0], row) for row in rows)]
    state = inside_trajectories.stream_of(seed, inside_trajectories.name_salt(salt + _SEP + "rejoined"))
    rest = math.sqrt(max(0.0, 1.0 - corr * corr))
    scores: "dict[int, float]" = {}
    for place in range(len(ordered)):
        lead = chain_walk.normal_score((place + 0.5) / len(ordered))
        scores[ordered[place]] = corr * lead
    for row in sorted(rows):
        scores[row] = scores[row] + rest * inside_trajectories.next_normal(state)
    seconds = sorted(seconds)
    by_score = [row for _score, row in sorted((scores[row], row) for row in rows)]
    joined: "dict[int, tuple[float, str]]" = {}
    for place in range(len(by_score)):
        joined[by_score[place]] = seconds[place]
    above_after = 0
    for row in rows:
        above_after += int(firsts[row][0] > joined[row][0])
    agreement = parsing.rank_agreement([firsts[row][0] for row in rows], [joined[row][0] for row in rows])
    if above_after != above_before or abs(agreement - target) > parsing.RANK_AGREEMENT_WINDOW / 2.0:
        return
    for row in rows:
        written[row] = firsts[row][1] + "/" + joined[row][1]


def _largest_name(groups: "dict[str, typing.Any]") -> str:
    """The group of a number entry whose plain part holds the most cells (the first on a tie)."""
    best, most = "", -1
    for name in sorted(groups):
        marginal = _object(_object(groups[name])["marginal"])
        if int(marginal["plain"]) > most:
            best, most = name, int(marginal["plain"])
    if most < 0:
        raise KeyedError("The inside record's keyed zone is not a zone synthtwin wrote.")
    return best


def read_columns(zone: "dict[str, object]") -> "list[str]":
    """The columns the zone reads but does not write: the labels that split a later clock's gap."""
    out: "list[str]" = []
    for entry in _list(zone["levels"]):
        level = _object(entry)
        held = _object(level["gaps"]) if "gaps" in level else {}
        for name in sorted(held):
            gap = _object(held[name])
            label = _text(gap["split_by"]) if "split_by" in gap else ""
            if label and label not in out:
                out += [label]
    return out


def copy_columns(zone: "dict[str, object]") -> "list[str]":
    """The columns the zone writes by a copy's rule (their source's cells, not their own)."""
    return [_text(_object(rule)["column"]) for rule in _list(zone["copies"])]


def written_columns(zone: "dict[str, object]") -> "list[str]":
    """Every column the zone may write: the content columns, every copy and every later clock (never the persons)."""
    out: "list[str]" = []
    for name in _list(zone["content"]):
        out += [_text(name)]
    for rule in _list(zone["copies"]):
        out += [_text(_object(rule)["column"])]
    for pair in (_list(zone["gaps"]) if "gaps" in zone else []):
        name = _text(_list(pair)[0])
        if name not in out:
            out += [name]
    return out
