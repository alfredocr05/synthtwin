"""Validator V12 for the chain's families, layer L1 (validation method V12; lane CHv, plan P4-D430).

IN FORCE SINCE PLAN P4-D464 (lane CHON): `synthtwin validate` reads every
description through `contract.load_profile_document` and runs these lines
wherever it carries a chain (validation method V12 as amended
2026-11-09); a description carrying none is measured, reported and
exited exactly as before.

WHAT IT CHECKS (V12.2), against the PUBLISHED choices and none of its
own (V12.1): each eligible column of the measured file is cut at its
published ladder, every cell read by the profiler's own reading of the
column under the description's settings and declarations
(`chain.read_column`), and every published family is counted at its
published levels over the file's tabled rows (the file's own records
holding nothing set aside, contract 4.6b.5). The lines:

- an `L0` band-total line a column, EXACT-OBSERVABLE, HELD or MISSED: the
  file's count of each band equals the published total, and no cell
  stands outside every published band;
- a family's line, EXACT-OBSERVABLE: the measured table equals the
  published table cell for cell, its published noughts included. Its
  verdict stands only where every band-total line of its members reads
  HELD (otherwise V12.3's fixed words "not judged: ...") and where the
  published tables are eligible beside the file's OWN facts (V12.3: RULE
  W1 read with the file's own-fact groups, RULE WE with the file's own
  records holding nothing; otherwise V5.3's fixed sentence). Both tests
  read the description, the lines already printed and the file's own
  description, never the measured table, so whether a line is withheld
  tells nothing of the table;
- every candidate pair's line: the word the description publishes, and
  for a pair reading `implied` the table the chain IMPLIES at the two
  columns' chain levels (the junction-tree product of the published
  families, exact fractions in `+ - * /`) beside V12.2's dealing spread:
  REPORT-ONLY, never a check and never beside anything measured;
- the description itself is the loader's: invariants S23 to S28
  (`chain_check`, which `contract.load_profile_document` runs before any
  byte of the file is read).

WHAT IT NEVER HOLDS (V12.3). No measured cell, total, difference or
count of moved rows reaches a line: each line holds its verdict and what
the description publishes. A column the file lacks, or reads under
another role, is NOT CHECKABLE (V3.3), and so is every family holding it.

ARITHMETIC. Counts are Python integers; an implied share is a pair of
integers in lowest terms; the dealing spread is bounded by integer
square roots (Newton's method on whole numbers) and written to four decimals. No float
decides anything here, and no library logarithm, exponential or sine is
called.
"""

import dataclasses

from synthtwin import chain, chain_order, chain_rules, reading, taxonomy, validation

# V12.3's fixed words where a total line of a family's member reads MISSED.
NOT_JUDGED = "not judged: the file's band totals differ from the published ones"
# V5.3's fixed sentence, where the published tables are not eligible beside the file's own facts.
GATE_CLOSED = validation.CHAIN_GATE_CLOSED
# V3.3's reasons a line is NOT CHECKABLE.
NO_SUCH_COLUMN = "the checked file has no column of this name, so its bands cannot be counted"
ANOTHER_ROLE = "the checked file reads this column under another role, so its published bands do not apply"
A_MEMBER_NOT_CHECKABLE = "a column of this family is not checkable in the checked file"
COUNTED_IN_PEOPLE = (
    "the checked file repeats a value of a column the descriptions read as record numbers, so its own "
    "description counts every value in people and publishes no family, and no band published here applies to it"
)

# The scale an implied share's root is bounded at (as the oracle's `dealing_spread`).
_ROOT_SCALE = 1 << 60


def _get(mapping: object, key: str) -> object:
    if isinstance(mapping, dict) and key in mapping:
        return mapping[key]
    return None


def _whole(value: object) -> int:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    return 0


# -- RATIONALS AS PAIRS OF INTEGERS ----------------------------------------


def _gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a


def _isqrt(n: int) -> int:
    """The greatest whole number whose square is at most `n` (Newton's method on integers)."""
    if n <= 0:
        return 0
    x = 1
    while x * x <= n:
        x = x * 2
    while True:
        y = (x + n // x) // 2
        if y >= x:
            return x
        x = y


def _reduced(numerator: int, denominator: int) -> "tuple[int, int]":
    if numerator == 0:
        return (0, 1)
    common = _gcd(numerator, denominator)
    return (numerator // common, denominator // common)


def _sum(left: "tuple[int, int]", right: "tuple[int, int]") -> "tuple[int, int]":
    return _reduced(left[0] * right[1] + right[0] * left[1], left[1] * right[1])


def _product(left: "tuple[int, int]", numerator: int, denominator: int) -> "tuple[int, int]":
    return _reduced(left[0] * numerator, left[1] * denominator)


# -- THE FILE READ AT EACH PUBLISHED LADDER ---------------------------------

# HELD COMPACTLY (skeptic 1 of lane CHv, item 10; Codex's item 5 on the
# build): each eligible column's `L0` code a tabled row is held in ONE BYTE
# where its ladder has at most `_BYTE_BANDS` bands (V12.6's one byte a row
# and column), as a list of whole numbers otherwise (a label column of
# more than 254 published levels; the offline policy admits no `array`);
# a stored code is the band
# plus one, 0 standing for a cell outside every published band. A
# column's readings are read for its own-fact groups the moment it is
# read and let go before the next column is, so no column's readings
# outlive it. Measured before: a Python list of codes a column (8 bytes a
# row) and every column's readings held to the end, about 800 MB of codes
# alone at 2,000,000 rows by 50 eligible columns.
_BYTE_BANDS = 254

def _code_store(bands: int, rows: int) -> "bytearray | list[int]":
    """A column's stored codes over `rows` tabled rows, all 0: one byte a row where `bands` allows it."""
    if bands <= _BYTE_BANDS:
        return bytearray(rows)
    return [0] * rows


@dataclasses.dataclass(frozen=True)
class _Column:
    """One eligible column of the file: each tabled row's stored `L0` code, and what its own facts mark."""

    codes: "bytearray | list[int]"
    blank: int
    groups: "set[int]"


def _l0_of_start(scale: chain_rules.Ladder, start: chain_rules.Starting) -> "list[int]":
    """Each starting band's `L0` band in the published ladder, -1 where no `L0` band joins it."""
    out = [-1] * len(start.names)
    for at in range(len(scale.l0)):
        for name in scale.l0[at]:
            for place in range(len(start.names)):
                if start.names[place] == name:
                    out[place] = at
    return out


def _holds_nothing(text: str) -> bool:
    """A cell of nothing but spaces and tabs holds NOTHING (contract 4.1, `empty_rows`; the chain's own test)."""
    for character in text:
        if character not in " \t":
            return False
    return True


def _file_column(
    table: reading.Table,
    place: int,
    blocks: "tuple[dict[str, object], dict[str, object]]",
    settings: taxonomy.Settings,
    declared: "dict[str, bool]",
    stored_as: str,
    scale: chain_rules.Ladder,
    holding_nothing: int,
    tabled: "tuple[bytearray, int]",
    floor: int,
) -> "_Column | None":
    """The file's column read by the profiler's own reading for the chain (`chain.read_column`), at the PUBLISHED bands.

    `blocks` is the column's published block and the file's own block.
    `chain.read_column` cuts each cell at the published block's starting
    bands (every spread band and the held-back pool among them, so every
    cell has a starting band); a starting band that no published `L0`
    band joins held no row when the description was written, and a cell
    standing there is outside every band (stored 0). The column's
    own-fact groups (V12.3: `chain_rules.small_group_bands` on the file's
    own block, `chain.value_run_bands` on its own values) are read here,
    while its readings are in hand, and the readings are not kept.
    """
    published, own = blocks
    found = chain.read_column(table, place, published, settings, declared, stored_as, holding_nothing)
    if found is None:
        return None
    to_l0 = _l0_of_start(scale, found.start)
    mask, count = tabled
    codes = _code_store(len(scale.l0), count)
    blank = 0
    at = 0
    for row in range(len(mask)):
        if mask[row]:
            codes[at] = to_l0[found.codes[row]] + 1
            blank += found.blanks[row]
            at += 1
    groups = chain_rules.small_group_bands(own, found.start, scale, floor) | chain.value_run_bands(
        own, found.start, scale, floor, found.readings
    )
    return _Column(codes, blank, groups)


def _tabled_rows(table: reading.Table, holding_nothing: int) -> "tuple[bytearray, int]":
    """The file's tabled rows as a mask a row (1: tabled), and their count (4.6b.5).

    Every row is tabled but the first `holding_nothing` rows blank in
    every column: the rows `chain.describe` sets aside, `E` being the
    file's own count of records holding nothing.
    """
    filled = bytearray(table.n_rows)
    for place in range(len(table.column_names)):
        values = reading.column_values(table, place)
        for row in range(len(values)):
            if not filled[row] and not _holds_nothing(values[row]):
                filled[row] = 1
    left = holding_nothing
    mask = bytearray(table.n_rows)
    count = 0
    for row in range(table.n_rows):
        if left and not filled[row]:
            left -= 1
            continue
        mask[row] = 1
        count += 1
    return mask, count


def _repeats(values: "list[str]") -> bool:
    """Whether some present value of a column stands on two or more rows."""
    seen: "set[str]" = set()
    for text in values:
        if _holds_nothing(text):
            continue
        if text in seen:
            return True
        seen |= {text}
    return False


def _repeats_as_published(block: "dict[str, object]") -> bool:
    """Whether a column's published counts say one of its values stands on two or more rows."""
    distinct = _get(block, "n_distinct")
    present = _get(block, "n_present")
    return isinstance(distinct, int) and isinstance(present, int) and distinct < present


def _counted_in_people(
    table: reading.Table,
    document: "dict[str, object]",
    redescribed: "dict[str, object]",
) -> bool:
    """Whether the file's own description counts its values in PEOPLE (Codex's item 2 on the build).

    A column the description declares as record numbers or as the
    person column (`settings.forced_identifiers`, `person_columns`), or
    that the description or the file's own description reads as record
    numbers (role `identifier`), names a PERSON on the file where one of
    its values stands on two or more rows (`taxonomy.repeating_identifiers`'
    reading): `synthtwin profile` run on that file counts every value in
    those people (plan P4-D406) and publishes no family at all (the
    chain's `OFF_PERSON`), so no published band applies to the file.
    """
    named: "set[str]" = set()
    # A COLUMN THE CHAIN STANDS BESIDE (lane GRa, the statistics skeptic's item
    # 7): a column the chain holds ineligible that repeats on the description's
    # own table repeated when the person said each row is a different person,
    # so where the chain stands its repeats name nobody; every other column
    # is read as before.
    statistical = _get(_get(document, "relationships"), "statistical")
    released: "set[str]" = set()
    listed_out = _get(statistical, "ineligible") if isinstance(statistical, dict) else None
    published = _get(document, "columns")
    if isinstance(listed_out, list) and isinstance(published, list):
        out_of_chain = {f"{_get(entry, 'column')}" for entry in listed_out if _get(entry, "reason") in ("held", "identifier")}
        for block in published:
            if isinstance(block, dict) and f"{_get(block, 'name')}" in out_of_chain and _repeats_as_published(block):
                released |= {f"{_get(block, 'name')}"}
    for holder in (document, redescribed):
        settings_block = _get(holder, "settings")
        for key in ("forced_identifiers", "person_columns"):
            listed = _get(settings_block, key)
            if isinstance(listed, list):
                for name in listed:
                    if f"{name}" not in released:
                        named |= {f"{name}"}
        columns = _get(holder, "columns")
        if isinstance(columns, list):
            for block in columns:
                if isinstance(block, dict) and _get(block, "role") == taxonomy.ROLE_IDENTIFIER and f"{_get(block, 'name')}" not in released:
                    named |= {f"{_get(block, 'name')}"}
    for place in range(len(table.column_names)):
        if table.column_names[place] in named and _repeats(reading.column_values(table, place)):
            return True
    return False


# -- THE COUNTS -----------------------------------------------------------


def _band_totals(codes: "bytearray | list[int]", count: int) -> "tuple[list[int], bool]":
    """Each `L0` band's rows, and whether every row stands in a published band."""
    out = [0] * (count + 1)
    for code in codes:
        out[code] += 1
    return out[1:], out[0] == 0


def _measured_table(
    family: chain_rules.Family,
    scales: "dict[str, chain_rules.Ladder]",
    codes: "dict[str, bytearray | list[int]]",
    rows: int,
) -> "list[int]":
    """A family's table over the file's tabled rows, laid out as the published one (4.6b.5)."""
    held = chain_rules.members(family)
    sizes = chain_rules.radices(family, scales)
    width = 1
    for size in sizes:
        width *= size
    out = [0] * width
    # A stored code is the band plus one; every one is inside here (the
    # family is counted only where its members' totals hold).
    maps = [(0,) + scales[name].maps[level] for name, level in held]
    columns = [codes[name] for name, _level in held]
    for row in range(rows):
        index = 0
        for place in range(1, len(held)):
            index = index * sizes[place] + maps[place][columns[place][row]]
        out[index * sizes[0] + maps[0][columns[0][row]]] += 1
    return out


# -- WHAT THE CHAIN IMPLIES (REPORT-ONLY) -----------------------------------


def _chain_levels(families: "list[chain_rules.Family]") -> "dict[str, int]":
    out: "dict[str, int]" = {}
    for family in families:
        out[family.child] = family.level
    return out


# BOUNDED (Codex's item 4 on the build). An implied table is a product of
# published tables, independent of the rows, but its size is the product
# of the two columns' band counts: two label columns of 50,000 published
# levels make 2,500,000,000 cells. So this report works out an implied
# table only where it has at most `IMPLIED_CELLS_AT_MOST` cells (decided
# from the two band counts before any work), holding at most
# `IMPLIED_HELD_AT_MOST` joint cells at any step of the product, and
# spending at most `IMPLIED_WORK_AT_MOST` products over the whole section;
# a pair past any of them prints its word and why its table is not
# worked out, and nothing else. Every one is a function of the
# description alone.
IMPLIED_CELLS_AT_MOST = 1024
IMPLIED_HELD_AT_MOST = 65536
IMPLIED_WORK_AT_MOST = 4000000

TOO_MANY_CELLS = (
    f"not worked out: its table at these levels would hold more than {IMPLIED_CELLS_AT_MOST} cells, "
    "more than this report prints, so neither its shares nor its spread are printed"
)
TOO_MUCH_WORK = (
    "not worked out: the product of the published tables that gives it is larger than this report "
    "works through, so neither its shares nor its spread are printed"
)


@dataclasses.dataclass
class _Work:
    """What is left of the section's work on implied tables (`IMPLIED_WORK_AT_MOST`)."""

    left: int


def implied_tables(
    families: "list[chain_rules.Family]",
    scales: "dict[str, chain_rules.Ladder]",
    wanted: "list[tuple[str, str]]",
    work: "_Work | None" = None,
) -> "dict[tuple[str, str], list[list[tuple[int, int]]] | None]":
    """The table the chain implies for each wanted pair, at the two columns' chain levels, as exact shares of the tabled rows.

    The junction-tree product of the published families (4.6b.9 (a)):
    each family is a clique of the chain's junction tree (its child at
    its chain level, its parents at its levels), joined to its anchor
    through its parents, and its published table IS the clique's joint
    count over the tabled rows (the margins tie, S25). For a pair `(X,
    Y)` the joint of `X` with each clique is carried from `X`'s own
    family outward along the tree, through each separator `S` (the
    parents a family reads): `P(X, C) = P(X, S) P(C) / P(S)`, `X` and the
    rest of `C` independent given `S`; `Y`'s family then gives `P(X,
    Y)`. Columns in two trees of the forest are independent. One walk of
    `X`'s tree gives every pair `X` leads, so the work grows with the
    published tables, never with a product of all the columns. Rows are
    `first`'s bands. Integers and `+ - * /` only. A pair is None where
    its table would pass one of the bounds above (`work` holds the
    section's own).
    """
    budget = work if work is not None else _Work(IMPLIED_WORK_AT_MOST)
    levels = _chain_levels(families)
    home: "dict[str, int]" = {}
    for at in range(len(families)):
        home[families[at].child] = at
    out: "dict[tuple[str, str], list[list[tuple[int, int]]] | None]" = {}
    led: "dict[str, list[str]]" = {}
    for first, second in wanted:
        out[(first, second)] = None
        if scales[first].counts[levels[first]] * scales[second].counts[levels[second]] > IMPLIED_CELLS_AT_MOST:
            continue
        if first in led:
            led[first] += [second]
        else:
            led[first] = [second]
    if not led:
        return out
    support = chain_rules.support_of(families, scales)
    # Each clique's cells holding rows: (rows, member bands, child first).
    cells: "list[list[tuple[int, tuple[int, ...]]]]" = []
    totals: "list[int]" = []
    for at in range(len(families)):
        sizes = chain_rules.radices(families[at], scales)
        found: "list[tuple[int, tuple[int, ...]]]" = []
        whole = 0
        for index in range(len(families[at].table)):
            count = families[at].table[index]
            if count:
                found += [(count, tuple(chain_rules.cell_parts(index, sizes)))]
                whole += count
        cells += [found]
        totals += [whole]
    # The tree's edges: each family to its anchor and to the families anchored on it.
    edges: "list[list[int]]" = [[] for _family in families]
    for at in range(len(families)):
        anchor = families[at].anchor
        if anchor is not None:
            edges[at] += [anchor]
            edges[anchor] += [at]

    def separator(here: int, there: int, parts: "tuple[int, ...]") -> "tuple[int, ...]":
        """A cell of clique `here` read at the separator toward `there` (the parents the child family reads)."""
        if families[here].anchor == there:
            return parts[1:]
        return chain_rules.seen_from_anchor(support, there, parts)

    for first in led:
        start = home[first]
        rows = scales[first].counts[levels[first]]
        wanted_here: "dict[int, list[str]]" = {}
        for second in led[first]:
            if home[second] in wanted_here:
                wanted_here[home[second]] += [second]
            else:
                wanted_here[home[second]] = [second]
        # P(X, C) on X's own family: its table over the tabled rows.
        held: "dict[int, dict[int, tuple[int, int]]]" = {}
        for place in range(len(cells[start])):
            count, parts = cells[start][place]
            held[place] = {parts[0]: _reduced(count, totals[start])}
        carried: "dict[int, dict[int, dict[int, tuple[int, int]]]]" = {start: held}
        holding = len(cells[start])
        queue = [start]
        reached = {start}
        next_at = 0
        while next_at < len(queue):
            here = queue[next_at]
            next_at += 1
            for there in edges[here]:
                if there in reached:
                    continue
                joint: "dict[tuple[int, ...], dict[int, tuple[int, int]]]" = {}
                for place in carried[here]:
                    key = separator(here, there, cells[here][place][1])
                    if key not in joint:
                        joint[key] = {}
                    into = joint[key]
                    given_here = carried[here][place]
                    for band in given_here:
                        into[band] = _sum(into[band], given_here[band]) if band in into else given_here[band]
                margin: "dict[tuple[int, ...], int]" = {}
                for count, parts in cells[there]:
                    key = separator(there, here, parts)
                    margin[key] = margin[key] + count if key in margin else count
                spread: "dict[int, dict[int, tuple[int, int]]]" = {}
                for place in range(len(cells[there])):
                    count, parts = cells[there][place]
                    key = separator(there, here, parts)
                    if key not in joint:
                        continue
                    given: "dict[int, tuple[int, int]]" = {}
                    for band in joint[key]:
                        if budget.left <= 0:
                            return out
                        budget.left -= 1
                        given[band] = _product(joint[key][band], count, margin[key])
                    spread[place] = given
                    holding += len(given)
                if holding > IMPLIED_HELD_AT_MOST:
                    return out
                carried[there] = spread
                reached |= {there}
                queue += [there]
                if there in wanted_here:
                    for second in wanted_here[there]:
                        columns = scales[second].counts[levels[second]]
                        table = [[(0, 1)] * columns for _row in range(rows)]
                        for place in spread:
                            band = cells[there][place][1][0]
                            for row in spread[place]:
                                table[row][band] = _sum(table[row][band], spread[place][row])
                        out[(first, second)] = table
            for place in carried[here]:
                holding -= len(carried[here][place])
            del carried[here]
        # Two trees of the forest: the two columns are independent.
        for there in wanted_here:
            if there in reached:
                continue
            for second in wanted_here[there]:
                columns = scales[second].counts[levels[second]]
                own = [0] * rows
                for count, parts in cells[start]:
                    own[parts[0]] += count
                other = [0] * columns
                for count, parts in cells[there]:
                    other[parts[0]] += count
                table = [[(0, 1)] * columns for _row in range(rows)]
                for row in range(rows):
                    for column in range(columns):
                        table[row][column] = _reduced(own[row] * other[column], totals[start] * totals[there])
                out[(first, second)] = table
    return out


def implied_shares(
    families: "list[chain_rules.Family]",
    scales: "dict[str, chain_rules.Ladder]",
    first: str,
    second: str,
    work: "_Work | None" = None,
) -> "list[list[tuple[int, int]]] | None":
    """The table the chain implies for one pair (`implied_tables` for that pair alone)."""
    return implied_tables(families, scales, [(first, second)], work)[(first, second)]


def dealing_spread(shares: "list[list[tuple[int, int]]]", tabled: int) -> "tuple[int, int]":
    """V12.2's dealing spread `s = 1/2 sum sqrt(p (1 - p) / n')`, bounded in whole multiples of 2 ** -61.

    Returns `(low, high)` with `low / 2 ** 61 <= s <= high / 2 ** 61`,
    each cell's root bounded by an integer square root, as the oracle's
    `dealing_spread` bounds it.
    """
    low = 0
    high = 0
    square = _ROOT_SCALE * _ROOT_SCALE
    for row in shares:
        for numerator, denominator in row:
            top = numerator * (denominator - numerator) * square
            bottom = denominator * denominator * tabled
            root = _isqrt(top // bottom) if bottom else 0
            low += root
            high += root if root * root * bottom == top else root + 1
    return low, high


def spread_text(low: int) -> str:
    """The spread to four decimals, rounded half up from its lower bound (`dealing_spread`'s bounds lie within 2 ** -40 of each other)."""
    units = (low * 10000 + _ROOT_SCALE) // (2 * _ROOT_SCALE)
    whole = units // 10000
    rest = units % 10000
    return f"{whole}.{rest:04d}"


# -- THE LINES -------------------------------------------------------------


def _band_word(name: object) -> str:
    """One starting band in the description's words."""
    if isinstance(name, (list, tuple)) and len(name) == 2 and not isinstance(name[0], (list, tuple)):
        lower = name[0]
        upper = name[1]
        if lower is None and upper is None:
            return "every value"
        if lower is None:
            return f"below {upper}"
        if upper is None:
            return f"{lower} and above"
        return f"{lower} to below {upper}"
    if isinstance(name, (list, tuple)) and len(name) == 1:
        return f"{name[0]}"
    return f"{name}"


def _starting_of(name: object) -> object:
    """A published starting-band descriptor in the form `chain_rules` builds it (a list read as a tuple)."""
    if isinstance(name, list):
        return tuple(name)
    return name


def _published_scale(
    entry: "dict[str, object]", block: "dict[str, object]"
) -> "tuple[chain_rules.Ladder, chain_rules.Starting] | None":
    """One published ladder entry read back as the loader reads it (S23 already holds on it)."""
    start = chain_rules.starting_bands(block, (True, True, True))
    l0 = entry["l0"]
    totals = entry["totals"]
    if start is None or not isinstance(l0, list) or not isinstance(totals, list):
        return None
    bands: "list[list[int]]" = []
    names: "list[tuple[object, ...]]" = []
    for band in l0:
        places: "list[int]" = []
        if isinstance(band, list):
            for one in band:
                for place in range(len(start.names)):
                    if start.names[place] == _starting_of(one):
                        places += [place]
        bands += [places]
        names += [tuple(start.names[place] for place in places)]
    second = chain_rules.union_closure(bands, start.groups[1])
    # `L2` as published: S23 held it to the cut its own `procedure` names
    # (RULE ONE_BAND, or `p50` alone on a description written before it).
    third = _published_level(entry["l2"], len(bands))
    if third is None:
        return None
    ordered = tuple(any(start.value[place] for place in band) for band in bands)
    scale = chain_rules.Ladder(
        f"{entry['column']}",
        tuple(names),
        (tuple(range(len(bands))), second, third),
        (len(bands), max(second) + 1, max(third) + 1),
        tuple(_whole(total) for total in totals),
        ordered,
    )
    return scale, start


def _published_level(written: object, count: int) -> "tuple[int, ...] | None":
    """Each `L0` band's band at a published level, `l1` or `l2` (the inverse of `chain_rules.bands_of`)."""
    if not isinstance(written, list):
        return None
    out = [-1] * count
    for at in range(len(written)):
        band = written[at]
        if not isinstance(band, list):
            return None
        for one in band:
            if not isinstance(one, int) or isinstance(one, bool) or not 0 <= one < count:
                return None
            out[one] = at
    if -1 in out:
        return None
    return tuple(out)


def _level_of(written: object) -> int:
    for place in range(3):
        if written == chain_rules.LEVELS[place]:
            return place
    return 0


def _published_family(written: object) -> chain_rules.Family:
    """One published chain entry read back as the loader reads it (S24 and S25 already hold on it)."""
    parents: "list[tuple[str, int]]" = []
    written_parents = _get(written, "parents")
    if isinstance(written_parents, list):
        for parent in written_parents:
            parents += [(f"{_get(parent, 'column')}", _level_of(_get(parent, "level")))]
    flat: "list[int]" = []
    table = _get(written, "table")
    if isinstance(table, list):
        for row in table:
            if isinstance(row, list):
                for cell in row:
                    flat += [_whole(cell)]
    anchor = _get(written, "anchor")
    return chain_rules.Family(
        f"{_get(written, 'child')}",
        _level_of(_get(written, "level")),
        tuple(parents),
        anchor if isinstance(anchor, int) and not isinstance(anchor, bool) else None,
        tuple(flat),
    )


def _legend(entry: "dict[str, object]") -> validation.ChainLegend:
    bands: "list[str]" = []
    l0 = entry["l0"]
    if isinstance(l0, list):
        for band in l0:
            words = ""
            if isinstance(band, list):
                for one in band:
                    words = (words + " + " if words else "") + _band_word(one)
            bands += [words]
    coarser: "list[tuple[tuple[int, ...], ...]]" = []
    for key in ("l1", "l2"):
        found: "list[tuple[int, ...]]" = []
        written = entry[key]
        if isinstance(written, list):
            for band in written:
                if isinstance(band, list):
                    found += [tuple(_whole(one) for one in band)]
        coarser += [tuple(found)]
    return validation.ChainLegend(f"{entry['column']}", tuple(bands), coarser[0], coarser[1])


def reads_a_calendar(document: "dict[str, object]") -> bool:
    """Whether the description's chain holds a column of dates or times (its own facts then need the calendar censuses)."""
    statistical = _get(_get(document, "relationships"), "statistical")
    ladder = _get(statistical, "ladder")
    if not isinstance(ladder, list):
        return False
    eligible: "set[str]" = set()
    for entry in ladder:
        eligible |= {f"{_get(entry, 'column')}"}
    columns = _get(document, "columns")
    if isinstance(columns, list):
        for block in columns:
            if f"{_get(block, 'name')}" in eligible and _get(block, "role") in (taxonomy.ROLE_DATETIME, taxonomy.ROLE_CLOCK):
                return True
    return False


def lines_of(
    document: "dict[str, object]",
    table: reading.Table,
    redescribed: "dict[str, object]",
    settings: taxonomy.Settings,
    declared_codes: "list[str]",
    declared_measured: "list[str]",
    declared_commas: "list[str]",
    stored_as: "tuple[str, ...]",
) -> "validation.ChainLines | None":
    """Every V12 line of the measured file against the description's chain; None where it carries none.

    Guarantees: `document` is a description the loader accepted with the
    chain's switch (S23 to S28 hold on it); `table` the measured file as
    `validation.measure` read it, and `redescribed` the file's own
    description (V2.1). Determinism: a function of the three and the
    settings. Boundary: no field of the result holds a string read from
    the measured file, a measured count or a measured cell: only
    verdicts, the description's own words and numbers, and fixed words.
    Raises nothing for a description the loader accepted.
    """
    statistical = _get(_get(document, "relationships"), "statistical")
    if not isinstance(statistical, dict):
        return None
    # THE PATIENT LAYER (V12.7; lane GRb, plan P4-D465): where `grain`
    # stands, `statistical` is the patient chain, counted in patients, and
    # the file is read in patients and in rows by the patient lines.
    if isinstance(_get(_get(document, "relationships"), "grain"), dict):
        return patient_lines(document, table, redescribed, settings, declared_codes, declared_measured, declared_commas, stored_as)
    floor = _whole(_get(_get(document, "settings"), "small_cell_floor"))
    published_blocks: "dict[str, dict[str, object]]" = {}
    columns_written = _get(document, "columns")
    if isinstance(columns_written, list):
        for block in columns_written:
            if isinstance(block, dict):
                published_blocks[f"{block['name']}"] = block
    file_blocks: "dict[str, dict[str, object]]" = {}
    file_columns = _get(redescribed, "columns")
    if isinstance(file_columns, list):
        for block in file_columns:
            if isinstance(block, dict):
                file_blocks[f"{block['name']}"] = block
    holding_nothing = chain_rules.records_holding_nothing(document)
    tabled = _whole(_get(document, "n_rows")) - holding_nothing
    ladder = statistical["ladder"]
    entries: "list[dict[str, object]]" = []
    if isinstance(ladder, list):
        for entry in ladder:
            if isinstance(entry, dict):
                entries += [entry]
    eligible = [f"{entry['column']}" for entry in entries]
    scales: "dict[str, chain_rules.Ladder]" = {}
    starts: "dict[str, chain_rules.Starting]" = {}
    for entry in entries:
        name = f"{entry['column']}"
        found = _published_scale(entry, published_blocks[name])
        if found is None:
            return None
        scales[name] = found[0]
        starts[name] = found[1]
    families: "list[chain_rules.Family]" = []
    written_chain = statistical["chain"]
    if isinstance(written_chain, list):
        for written in written_chain:
            families += [_published_family(written)]
    # -- the file at each published ladder --
    file_place: "dict[str, int]" = {}
    for place in range(len(table.column_names)):
        file_place[table.column_names[place]] = place
    file_nothing = chain_rules.records_holding_nothing(redescribed)
    tabled_mask = _tabled_rows(table, file_nothing)
    codes: "dict[str, bytearray | list[int]]" = {}
    groups: "dict[str, set[int]]" = {}
    blank_counts: "dict[str, int]" = {}
    unchecked: "dict[str, str]" = {}
    people = _counted_in_people(table, document, redescribed)
    for name in eligible:
        if people:
            unchecked[name] = COUNTED_IN_PEOPLE
            continue
        if name not in file_place or name not in file_blocks:
            unchecked[name] = NO_SUCH_COLUMN
            continue
        if _get(file_blocks[name], "role") != _get(published_blocks[name], "role"):
            unchecked[name] = ANOTHER_ROLE
            continue
        declared = {
            "code": name in declared_codes,
            "measurement": name in declared_measured,
            "decimal_comma": name in declared_commas,
        }
        place = file_place[name]
        column = _file_column(
            table,
            place,
            (published_blocks[name], file_blocks[name]),
            settings,
            declared,
            stored_as[place] if place < len(stored_as) else "",
            scales[name],
            file_nothing,
            tabled_mask,
            floor,
        )
        if column is None:
            unchecked[name] = ANOTHER_ROLE
            continue
        codes[name] = column.codes
        groups[name] = column.groups
        blank_counts[name] = column.blank
    totals: "list[validation.ChainTotal]" = []
    held_totals: "set[str]" = set()
    for name in eligible:
        published = scales[name].totals
        if name in unchecked:
            totals += [validation.ChainTotal(name, "", published, unchecked[name])]
            continue
        counted, inside = _band_totals(codes[name], len(published))
        if inside and tuple(counted) == published:
            totals += [validation.ChainTotal(name, validation.HELD, published)]
            held_totals = held_totals | {name}
        else:
            totals += [validation.ChainTotal(name, validation.MISSED, published)]
    # -- whether the published tables stand beside the file's own facts (V12.3) --
    # A column that is not checkable is read as holding a group in every
    # band and its published blank cells: that refuses more, never less.
    for name in eligible:
        if name in unchecked:
            groups[name] = set(range(len(scales[name].l0)))
            blank_counts[name] = _whole(_get(published_blocks[name], "n_missing_blank")) - holding_nothing
    # Each carried rule's derived family `{D | A}`, read through its parent as the loader reads it (rule
    # 4), stands beside the file's own facts too (lane RO's repair 2, the outside review's item 6).
    gate_open = not chain_rules.w1_refusals(families, scales, groups, _derived_families(statistical["rules"], scales))
    x0 = chain_rules.blank_cell(scales, blank_counts)
    room = chain_rules.blank_record_room(redescribed, floor) + chain_rules.outside_cells(redescribed, set(eligible))
    if x0 is not None and chain_rules.cell_bound(x0, families, scales, tabled) > room:
        gate_open = False
    lines: "list[validation.ChainFamily]" = []
    not_judged = 0
    for at in range(len(families)):
        family = families[at]
        sizes = chain_rules.radices(family, scales)
        width = len(family.table) // sizes[0]
        written_rows = tuple(tuple(family.table[row * sizes[0] : (row + 1) * sizes[0]]) for row in range(width))
        names = [name for name, _level in chain_rules.members(family)]
        if any(name in unchecked for name in names):
            lines += [validation.ChainFamily(at, family.child, family.level, family.parents, written_rows, "", A_MEMBER_NOT_CHECKABLE)]
            continue
        if any(name not in held_totals for name in names):
            lines += [validation.ChainFamily(at, family.child, family.level, family.parents, written_rows, validation.WITHHELD, NOT_JUDGED)]
            not_judged += 1
            continue
        if not gate_open:
            lines += [validation.ChainFamily(at, family.child, family.level, family.parents, written_rows, validation.WITHHELD, GATE_CLOSED)]
            continue
        measured = _measured_table(family, scales, codes, tabled_mask[1])
        verdict = validation.HELD if tuple(measured) == family.table else validation.MISSED
        lines += [validation.ChainFamily(at, family.child, family.level, family.parents, written_rows, verdict)]
    # -- every candidate pair, its word as published --
    levels = _chain_levels(families)
    pairs: "list[validation.ChainPair]" = []
    words = statistical["words"]
    wanted: "list[tuple[str, str]]" = []
    if isinstance(words, list):
        for entry in words:
            pair = _get(entry, "columns")
            if isinstance(pair, list) and len(pair) == 2 and f"{_get(entry, 'word')}" == "implied":
                wanted += [(f"{pair[0]}", f"{pair[1]}")]
    tables = implied_tables(families, scales, wanted, _Work(IMPLIED_WORK_AT_MOST))
    if isinstance(words, list):
        for entry in words:
            pair = _get(entry, "columns")
            word = f"{_get(entry, 'word')}"
            if not isinstance(pair, list) or len(pair) != 2:
                continue
            first = f"{pair[0]}"
            second = f"{pair[1]}"
            holding: "int | None" = None
            for at in range(len(families)):
                held = [name for name, _level in chain_rules.members(families[at])]
                if holding is None and first in held and second in held:
                    holding = at
            shares: "tuple[tuple[tuple[int, int], ...], ...]" = ()
            spread = ""
            why = ""
            if word == "implied":
                implied = tables[(first, second)]
                if implied is None:
                    cells = scales[first].counts[levels[first]] * scales[second].counts[levels[second]]
                    why = TOO_MANY_CELLS if cells > IMPLIED_CELLS_AT_MOST else TOO_MUCH_WORK
                else:
                    shares = tuple(tuple(row) for row in implied)
                    low, _high = dealing_spread(implied, tabled)
                    spread = spread_text(low)
            pairs += [validation.ChainPair((first, second), word, holding, (levels[first], levels[second]), shares, spread, why)]
    # -- the carried rules (V12.2's two rows; contract 4.6b.7; lane RO, plan P4-D459) --
    rule_lines = _rule_lines(
        statistical["rules"], published_blocks, file_blocks, file_place, table, settings,
        (declared_codes, declared_measured, declared_commas), stored_as, held_totals, unchecked,
        gate_open, tabled_mask, scales, codes, floor,
    )
    counted_lines: "dict[str, int]" = {validation.HELD: 0, validation.MISSED: 0, validation.WITHHELD: 0, "": 0}
    for total in totals:
        counted_lines[total.verdict] += 1
    for line in lines:
        counted_lines[line.verdict] += 1
    for rule_line in rule_lines:
        counted_lines[rule_line.verdict] += 1
        # A rule's line WITHHELD because a column it reads missed its band totals is counted with the
        # family lines withheld for that reason, never given the disclosure rule as its cause (lane RO's
        # repair 2, the outside review's item 14).
        if rule_line.verdict == validation.WITHHELD and rule_line.reason == NOT_JUDGED:
            not_judged += 1
    return validation.ChainLines(
        tuple(_legend(entry) for entry in entries),
        tuple(totals),
        tuple(lines),
        tuple(pairs),
        counted_lines[validation.HELD],
        counted_lines[validation.MISSED],
        counted_lines[validation.WITHHELD],
        counted_lines[""],
        not_judged,
        tuple(rule_lines),
    )


def _derived_families(listed: object, scales: "dict[str, chain_rules.Ladder]") -> "tuple[chain_rules.Derived, ...]":
    """Each published derived family `{D | A}` as RULE W1 reads it (rule 4): `A`'s level, the bands of `D`
    each band of `A` holds rows in, and whether `D`'s level has no edge."""
    out: "list[chain_rules.Derived]" = []
    if not isinstance(listed, list):
        return ()
    levels = {"L0": 0, "L1": 1, "L2": 2}
    for entry in listed:
        written = _get(entry, "derived") if isinstance(entry, dict) else None
        if not isinstance(written, dict) or _get(entry, "carrier") != chain_rules.CARRIER_DERIVED:
            continue
        parent = written["parent"]
        table = written["table"]
        first = f"{_get(parent, 'column')}"
        if not isinstance(parent, dict) or not isinstance(table, list) or first not in scales:
            continue
        out += [chain_rules.derived_of(first, levels[f"{parent['level']}"] if f"{parent['level']}" in levels else 0, table, not written["edges"])]
    return tuple(out)


def _rule_lines(
    listed: object,
    published_blocks: "dict[str, dict[str, object]]",
    file_blocks: "dict[str, dict[str, object]]",
    file_place: "dict[str, int]",
    table: reading.Table,
    settings: taxonomy.Settings,
    declarations: "tuple[list[str], list[str], list[str]]",
    stored_as: "tuple[str, ...]",
    held_totals: "set[str]",
    unchecked: "dict[str, str]",
    gate_open: bool,
    tabled_mask: "tuple[bytearray, int]",
    scales: "dict[str, chain_rules.Ladder]",
    codes: "dict[str, bytearray | list[int]]",
    floor: int,
) -> "list[validation.ChainRule]":
    """V12.2's two rows for every carried rule: its failing rows inside its class, and a derived column's
    family recomputed on the file as `B - A` (contract 4.6b.7). Each prints its verdict alone (V12.3):
    no count of the computed column's rows and no count of failing rows."""
    out: "list[validation.ChainRule]" = []
    if not isinstance(listed, list):
        return out
    mask, _count = tabled_mask
    tabled_rows = [row for row in range(len(mask)) if mask[row]]
    codes_d, measured, commas = declarations
    for at in range(len(listed)):
        entry = listed[at]
        if not isinstance(entry, dict):
            continue
        first = f"{entry['inputs'][0]}" if isinstance(entry["inputs"], list) and entry["inputs"] else ""
        target = f"{entry['computed']}"
        carrier = f"{entry['carrier']}"
        klass = f"{entry['class']}"
        base = [first] + ([] if carrier == chain_rules.CARRIER_DERIVED else [carrier])
        kinds = ["rule"] + (["derived family"] if carrier == chain_rules.CARRIER_DERIVED else [])

        def line(kind: str, verdict: str, reason: str = "") -> validation.ChainRule:
            return validation.ChainRule(at, target, (first,), carrier, klass, kind, verdict, reason)

        missing = [name for name in base if name in unchecked]
        if missing or target not in file_place or target not in file_blocks:
            reason = unchecked[missing[0]] if missing else NO_SUCH_COLUMN
            out += [line(kind, "", reason) for kind in kinds]
            continue
        if any(name not in held_totals for name in base):
            out += [line(kind, validation.WITHHELD, NOT_JUDGED) for kind in kinds]
            continue
        if not gate_open:
            out += [line(kind, validation.WITHHELD, GATE_CLOSED) for kind in kinds]
            continue
        a_block = published_blocks[first]
        kind_of_pair = chain_rules.kind_of_role(_get(a_block, "role"))
        if kind_of_pair is None:
            out += [line(kind, "", ANOTHER_ROLE) for kind in kinds]
            continue

        def read(name: str, block: "dict[str, object]", kind: str) -> chain_order.Readings:
            place = file_place[name]
            declared = {"code": name in codes_d, "measurement": name in measured, "decimal_comma": name in commas}
            return chain_order.read_under(
                table, place, block, kind, settings, declared, stored_as[place] if place < len(stored_as) else "", tabled_rows,
            )

        a = read(first, a_block, kind_of_pair)
        b = read(target, file_blocks[target], kind_of_pair)
        pair = chain_order.pair_reading(kind_of_pair, a_block, published_blocks[target], a, b)
        if carrier == chain_rules.CARRIER_DERIVED:
            failing = chain_order.failing_rows(pair, a, b, len(tabled_rows))
            held = failing <= floor - 1 if klass == chain_rules.CLASS_PHRASE else f"{failing}" == klass
            out += [line("rule", validation.HELD if held else validation.MISSED)]
            out += [line("derived family", _derived_verdict(entry["derived"], pair, a, b, scales[first], codes[first]))]
            continue
        d = read(carrier, published_blocks[carrier], chain_rules.KIND_NUMBER)
        unit = f"{entry['unit']}"
        seconds = kind_of_pair == chain_rules.KIND_CLOCK or pair.seconds
        units = dict(chain_rules.TIME_UNITS)
        b_step = chain_rules.first_step(published_blocks[target], kind_of_pair)
        b_end = None
        if kind_of_pair == chain_rules.KIND_CLOCK and b_step is not None:
            b_end = 86399 if b_step == 1 else 86340
        failing = chain_order.source_failing(pair, a, b, d, units[unit] if unit in units else 1, b_end, floor)
        held_source = failing <= floor - 1 and (not seconds or unit in units)
        out += [line("rule", validation.HELD if held_source else validation.MISSED)]
    return out


def _derived_verdict(
    written: object,
    pair: chain_order.PairReading,
    a: chain_order.Readings,
    b: chain_order.Readings,
    ladder: chain_rules.Ladder,
    a_codes: "bytearray | list[int]",
) -> str:
    """A derived column's family recomputed on the file: `B - A` banded at its published edges, `A` at its
    published level, against the published table cell for cell (V12.2)."""
    if not isinstance(written, dict):
        return validation.MISSED
    edges = [chain_rules.decimal_value(edge) for edge in written["edges"]]
    if any(edge is None for edge in edges):
        return validation.MISSED
    exact = [edge for edge in edges if edge is not None]
    parent = written["parent"]
    level = {"L0": 0, "L1": 1, "L2": 2}[f"{parent['level']}"] if isinstance(parent, dict) else 0
    unit = chain_rules.Exact(1, 10 ** max(a.places, b.places)) if pair.kind == chain_rules.KIND_NUMBER else chain_rules.Exact(1)
    width = len(exact) + 2
    counted = [[0] * width for _band in range(ladder.counts[level])]
    for row in range(a.rows):
        code = a_codes[row]
        if not code:
            return validation.MISSED
        band = ladder.maps[level][code - 1]
        gap, _fails = chain_order.gap_of(pair, a, b, row)
        column = width - 1 if gap is None else chain_rules.derived_band_of(exact, chain_rules.Exact(gap) * unit)
        counted[band][column] += 1
    published = written["table"]
    return validation.HELD if counted == published else validation.MISSED


def with_lines(outcome: validation.Outcome, lines: validation.ChainLines) -> validation.Outcome:
    """The outcome with the chain's lines, their verdicts counted in its census."""
    census = outcome.census
    counted = validation.Census(
        held=census.held + lines.held,
        within_bound=census.within_bound,
        authorized_deviation=census.authorized_deviation,
        withheld=census.withheld + lines.withheld,
        missed=census.missed + lines.missed,
        not_checkable=census.not_checkable + lines.not_checkable,
    )
    return dataclasses.replace(outcome, census=counted, chain=lines)


# -- THE PATIENT LAYER'S LINES (V12.7; lane GRb, plan P4-D465) ---------------------

R_NAME = "(rows per patient)"
PATIENT_GATE = (
    "not judged: the file's own counts of this object hold a count of 1 to f - 1, "
    "so describing this file on its own would not publish it"
)
CENSUS_DIFFERS = "not judged: the file's census of rows per patient differs from the published one"


def _patient_codes(
    table: reading.Table,
    place: int,
    block: "dict[str, object]",
    entry: "dict[str, object]",
    settings: taxonomy.Settings,
    declared: "dict[str, bool]",
    stored_as: str,
    holding_nothing: int,
) -> "tuple[list[int], chain_rules.Ladder] | None":
    """Each file row's `L0` band of one column at its published ladder (0-based; -1 outside every band), and the ladder."""
    found = _published_scale(entry, block)
    if found is None:
        return None
    scale, _start = found
    read = chain.read_column(table, place, block, settings, declared, stored_as, holding_nothing)
    if read is None:
        return None
    to_l0 = _l0_of_start(scale, read.start)
    return [to_l0[read.codes[row]] for row in range(table.n_rows)], scale


def patients_first_rows(
    table: reading.Table,
    redescribed: "dict[str, object]",
    person: str,
    positions: "list[object] | None" = None,
) -> "list[int] | None":
    """Each patient's first position in a file, in the order the patients first stand (batch 4u's merge of lane GRb).

    The patients are read as `patient_lines` reads them: the tabled rows
    (every row but the file's own records holding nothing, ``redescribed``
    being the file's own description) that share one value of the person
    column, a cell of nothing but spaces and tabs naming no patient. None
    where the file holds no column of that name. ``positions`` is each
    row's reading of the published position column (`position_readings`),
    None where none stands: each patient's rows are then put in its order,
    ties and absent readings by row order, as the producer put them
    (`patient_layer`'s position column), and the first of them is the
    patient's row (batch 4u's outside review, item 3: read on the stored
    first row, a table whose visits stand newest first missed its own
    patient-fixed counts). The validator checks the blocks the loader
    reads counted in patients (`contract.patient_counted`) on these rows.
    A function of the four; raises nothing.
    """
    place_of = {table.column_names[at]: at for at in range(len(table.column_names))}
    if person not in place_of:
        return None
    mask, _count = _tabled_rows(table, chain_rules.records_holding_nothing(redescribed))
    keys = reading.column_values(table, place_of[person])
    rows_of: "dict[str, list[int]]" = {}
    order: "list[str]" = []
    for row in range(table.n_rows):
        if not mask[row] or _holds_nothing(keys[row]):
            continue
        if keys[row] not in rows_of:
            rows_of[keys[row]] = []
            order += [keys[row]]
        rows_of[keys[row]] += [row]
    if positions is not None:
        _in_position_order(rows_of, order, positions)
    return [rows_of[key][0] for key in order]


def _exact_readings(
    table: reading.Table,
    place: int,
    block: "dict[str, object]",
    settings: taxonomy.Settings,
    declared: "dict[str, bool]",
    stored_as: str,
) -> "list[object]":
    """Each row's exact reading of one column, as V12.7 reads it (`patient_rules.reading_of`); None where its cell holds none."""
    from synthtwin import patient_rules

    values = reading.column_values(table, place)
    meaning = chain.reading_of(block, values, settings, declared, stored_as)
    role = f"{_get(block, 'role')}"
    out: "list[object]" = []
    for text in values:
        kind, value = meaning[text] if text in meaning else ("missing", None)
        out += [patient_rules.reading_of(role, value, block) if kind == "value" else None]
    return out


def position_readings(
    document: "dict[str, object]",
    table: reading.Table,
    redescribed: "dict[str, object]",
    settings: taxonomy.Settings,
    declared_codes: "list[str]",
    declared_measured: "list[str]",
    declared_commas: "list[str]",
    stored_as: "tuple[str, ...]",
) -> "list[object] | None":
    """Each row's reading of the published position column (`grain.position`), as the producer read it; None where none stands.

    The producer put each patient's rows in the order of the position
    column's own readings, read before the description held that column
    (`patient_layer`: the first dealt date column keeps its place where its
    own description in rows is later held, as Safe Harbor dates are held
    by default). So the column is read with its published block where that
    block reads a value of the file, as `patient_lines` reads it, and else
    with the file's own description of it (``redescribed``, V2.1), which
    reads the file's cells as `synthtwin profile` does (batch 4u's outside
    review, item 3). None where `grain` names no position, or the file or
    the description holds no column of that name. Nothing read here
    reaches a report: only which row stands first. A function of its
    arguments; raises nothing for a description the loader accepted.
    """
    position = _get(_get(_get(document, "relationships"), "grain"), "position")
    if not isinstance(position, str):
        return None
    place_of = {table.column_names[at]: at for at in range(len(table.column_names))}
    if position not in place_of:
        return None
    place = place_of[position]
    declared = {"code": position in declared_codes, "measurement": position in declared_measured, "decimal_comma": position in declared_commas}
    storage = stored_as[place] if place < len(stored_as) else ""
    readings: "list[object] | None" = None
    for source in (document, redescribed):
        written = _get(source, "columns")
        for one in written if isinstance(written, list) else []:
            if not isinstance(one, dict) or f"{one['name']}" != position:
                continue
            read = _exact_readings(table, place, one, settings, declared, storage)
            if any(stamp is not None for stamp in read):
                return read
            readings = read if readings is None else readings
    return readings


def _in_position_order(rows_of: "dict[str, list[int]]", order: "list[str]", stamps: "list[object]") -> None:
    """Each patient's rows put in its readings' order, in place: ties and absent readings by row order (V12.7)."""
    for key in order:
        present = sorted((stamp, row) for row in rows_of[key] for stamp in (stamps[row],) if stamp is not None)
        rows_of[key] = [row for _stamp, row in present] + [row for row in rows_of[key] if stamps[row] is None]


def patient_lines(
    document: "dict[str, object]",
    table: reading.Table,
    redescribed: "dict[str, object]",
    settings: taxonomy.Settings,
    declared_codes: "list[str]",
    declared_measured: "list[str]",
    declared_commas: "list[str]",
    stored_as: "tuple[str, ...]",
) -> "validation.ChainLines | None":
    """V12.7's lines of a file against a description whose `grain` stands: verdicts alone, no measured number.

    The file's patients are read by the published person column (its
    tabled rows sharing one value), their positions by the published
    position column (each patient's rows by its reading, ties and absent
    readings by row order), every column at its published ladder. THE
    CENSUS LINE IS JUDGED FIRST, AND ALWAYS. Every other line is judged
    where the census and the `L0` totals it reads hold, and, V12.3's gate
    as built here, where the file's own counts of the object hold no
    count of 1 to `f - 1` (patients for a family of the patient chain,
    rows for a row family, patients for a trend cell); otherwise its
    fixed words stand. The validator draws nothing, chooses nothing and
    never reads the key. Raises nothing for a description the loader
    accepted.
    """
    from synthtwin import patient_rules

    relationships = _get(document, "relationships")
    grain = _get(relationships, "grain")
    statistical = _get(relationships, "statistical")
    if not isinstance(grain, dict) or not isinstance(statistical, dict):
        return None
    floor = _whole(_get(_get(document, "settings"), "small_cell_floor"))
    blocks: "dict[str, dict[str, object]]" = {}
    written = _get(document, "columns")
    for block in written if isinstance(written, list) else []:
        if isinstance(block, dict):
            blocks[f"{block['name']}"] = block
    place_of = {table.column_names[at]: at for at in range(len(table.column_names))}
    person = f"{_get(grain, 'person')}"
    if person not in place_of:
        return None
    file_nothing = chain_rules.records_holding_nothing(redescribed)
    mask, _count = _tabled_rows(table, file_nothing)
    keys = reading.column_values(table, place_of[person])
    rows_of: "dict[str, list[int]]" = {}
    order: "list[str]" = []
    for row in range(table.n_rows):
        if not mask[row] or _holds_nothing(keys[row]):
            continue
        if keys[row] not in rows_of:
            rows_of[keys[row]] = []
            order += [keys[row]]
        rows_of[keys[row]] += [row]

    def declared_of(name: str) -> "dict[str, bool]":
        return {"code": name in declared_codes, "measurement": name in declared_measured, "decimal_comma": name in declared_commas}

    def exact_readings(name: str) -> "list[object]":
        return _exact_readings(
            table, place_of[name], blocks[name], settings, declared_of(name), stored_as[place_of[name]] if place_of[name] < len(stored_as) else ""
        )

    position = _get(grain, "position")
    if isinstance(position, str) and position in place_of and position in blocks:
        _in_position_order(rows_of, order, exact_readings(position))
    r_of = {key: len(rows_of[key]) for key in order}
    # -- the census line, judged first and always --
    census = _get(grain, "census")
    lo = _whole(_get(census, "lo"))
    bands_written = _get(census, "bands")
    published_bands = [_whole(_get(entry, "patients")) for entry in bands_written] if isinstance(bands_written, list) else []
    top = _get(census, "top")
    counted = [0 for _band in published_bands]
    top_patients = 0
    top_rows = 0
    for key in order:
        rho = r_of[key]
        if rho >= lo:
            top_patients += 1
            top_rows += rho
        elif 1 <= rho <= len(counted):
            counted[rho - 1] += 1
    census_held = counted == published_bands and top_patients == _whole(_get(top, "patients")) and top_rows == _whole(_get(top, "rows"))
    totals: "list[validation.ChainTotal]" = [
        validation.ChainTotal(R_NAME, validation.HELD if census_held else validation.MISSED, tuple(published_bands) + (_whole(_get(top, "patients")),))
    ]
    # -- each patient-chain column's band, a patient each --
    ladder = statistical["ladder"] if isinstance(statistical["ladder"], list) else []
    entries = {f"{entry['column']}": entry for entry in ladder if isinstance(entry, dict)}
    scales: "dict[str, chain_rules.Ladder]" = {}
    band_of_patient: "dict[str, list[int]]" = {}
    derived = {f"{entry['name']}": entry for entry in grain["derived"] if isinstance(entry, dict)} if isinstance(_get(grain, "derived"), list) else {}
    row_ladder = {f"{entry['column']}": entry for entry in grain["ladder"] if isinstance(entry, dict)} if isinstance(_get(grain, "ladder"), list) else {}
    row_codes: "dict[str, list[int]]" = {}
    row_scales: "dict[str, chain_rules.Ladder]" = {}

    def row_read(name: str) -> bool:
        if name in row_codes:
            return True
        if name not in place_of or name not in blocks or name not in row_ladder:
            return False
        found = _patient_codes(table, place_of[name], blocks[name], row_ladder[name], settings, declared_of(name),
                               stored_as[place_of[name]] if place_of[name] < len(stored_as) else "", file_nothing)
        if found is None:
            return False
        row_codes[name], row_scales[name] = found
        return True

    for name in entries:
        entry = entries[name]
        if name == R_NAME:
            names = [band[0][0] if isinstance(band, list) and band and isinstance(band[0], list) else "" for band in entry["l0"]]
            codes = []
            for key in order:
                rho = r_of[key]
                label = f"{rho}" if rho < lo else ""
                code = len(names) - 1
                for place in range(len(names)):
                    if names[place] == label:
                        code = place
                codes += [code]
            band_of_patient[name] = codes
            scales[name] = chain_rules.Ladder(name, tuple((one,) for one in names), (tuple(range(len(names))),) * 3, (len(names),) * 3, tuple(_whole(one) for one in entry["totals"]), tuple(True for _one in names))
            continue
        if name in derived:
            spec = derived[name]
            source = f"{spec['source']}"
            if source not in place_of or source not in blocks:
                continue
            kind = f"{spec['kind']}"
            codes = []
            if kind == "own_mean":
                values = exact_readings(source)
                edges = list(spec["edges"]) if isinstance(spec["edges"], list) else []
                for key in order:
                    codes += [patient_rules.own_mean_band([values[row] for row in rows_of[key]], edges)]
            else:
                if not row_read(source):
                    continue
                level = _LEVEL_OF[f"{spec['level']}"] if f"{spec['level']}" in _LEVEL_OF else 0
                values = exact_readings(source)
                for key in order:
                    dated = [row for row in rows_of[key] if values[row] is not None]
                    if not dated:
                        codes += [-1]
                        continue
                    first = sorted((values[row], row) for row in dated)[0][1]
                    l0 = row_codes[source][first]
                    codes += [row_scales[source].maps[level][l0] if l0 >= 0 else -1]
            band_of_patient[name] = codes
            found_scale = _derived_scale(entry)
            if found_scale is not None:
                scales[name] = found_scale
            continue
        if name not in place_of or name not in blocks:
            continue
        found = _patient_codes(table, place_of[name], blocks[name], entry, settings, declared_of(name),
                               stored_as[place_of[name]] if place_of[name] < len(stored_as) else "", file_nothing)
        if found is None:
            continue
        codes_rows, scale = found
        scales[name] = scale
        band_of_patient[name] = [codes_rows[rows_of[key][0]] for key in order]
    held_totals: "set[str]" = set()
    for name in entries:
        entry = entries[name]
        if name == R_NAME:
            if census_held:
                held_totals |= {name}
            continue
        published = tuple(_whole(one) for one in entry["totals"])
        if name not in band_of_patient or name not in scales:
            totals += [validation.ChainTotal(name, "", published, NO_SUCH_COLUMN)]
            continue
        counts = [0 for _one in published]
        inside = True
        for code in band_of_patient[name]:
            if 0 <= code < len(counts):
                counts[code] += 1
            else:
                inside = False
        verdict = validation.HELD if inside and tuple(counts) == published else validation.MISSED
        if verdict == validation.HELD:
            held_totals |= {name}
        totals += [validation.ChainTotal(name, verdict, published)]

    def cell_of(parents: "list[tuple[str, int]]", patient: int) -> int:
        cell = 0
        for name, level in parents:
            maps = scales[name].maps[level]
            code = band_of_patient[name][patient]
            if code < 0:
                return -1
            cell = cell * scales[name].counts[level] + maps[code]
        return cell

    lines: "list[validation.ChainFamily]" = []
    not_judged = 0
    chain_written = statistical["chain"] if isinstance(statistical["chain"], list) else []
    for at, written_family in enumerate(chain_written):
        family = _published_family(written_family)
        sizes = chain_rules.radices(family, scales) if all(name in scales for name, _level in chain_rules.members(family)) else [1]
        width = len(family.table) // sizes[0] if sizes[0] else 0
        rows_written = tuple(tuple(family.table[row * sizes[0]:(row + 1) * sizes[0]]) for row in range(width))
        names = [name for name, _level in chain_rules.members(family)]
        if any(name not in scales or name not in band_of_patient for name in names):
            lines += [validation.ChainFamily(at, family.child, family.level, family.parents, rows_written, "", A_MEMBER_NOT_CHECKABLE)]
            continue
        # The gate reads the L0 totals of the file's own columns and of `r`,
        # NEVER a derived column's: its patient totals are what its own line
        # judges, so a family holding it reads MISSED there, not "not judged"
        # (V12.7; repair 1 of lane GRb, the first skeptic's item 2).
        if not census_held or any(name not in held_totals for name in names if name not in derived):
            lines += [validation.ChainFamily(at, family.child, family.level, family.parents, rows_written, validation.WITHHELD, CENSUS_DIFFERS if not census_held else NOT_JUDGED)]
            not_judged += 1
            continue
        measured = [0 for _cell in family.table]
        for patient_at in range(len(order)):
            cell = cell_of(list(family.parents), patient_at)
            child_band = band_of_patient[family.child][patient_at]
            if cell < 0 or child_band < 0:
                continue
            measured[cell * sizes[0] + scales[family.child].maps[family.level][child_band]] += 1
        if any(0 < one < floor for one in measured):
            lines += [validation.ChainFamily(at, family.child, family.level, family.parents, rows_written, validation.WITHHELD, PATIENT_GATE)]
            continue
        verdict = validation.HELD if tuple(measured) == family.table else validation.MISSED
        lines += [validation.ChainFamily(at, family.child, family.level, family.parents, rows_written, verdict)]
    # -- the row families, counted in rows --
    rows_written_grain = grain["rows"] if isinstance(_get(grain, "rows"), list) else []
    for at, written_family in enumerate(rows_written_grain):
        child = f"{written_family['child']}"
        level = _LEVEL_OF[f"{written_family['level']}"] if f"{written_family['level']}" in _LEVEL_OF else 0
        parents = [(f"{one['column']}", _LEVEL_OF[f"{one['level']}"] if f"{one['level']}" in _LEVEL_OF else 0) for one in written_family["parents"]]
        table_written = tuple(tuple(_whole(cell) for cell in line) for line in written_family["table"])
        index = len(chain_written) + at
        if not row_read(child) or any(name not in scales or name not in band_of_patient for name, _level in parents):
            lines += [validation.ChainFamily(index, child, level, tuple(parents), table_written, "", A_MEMBER_NOT_CHECKABLE)]
            continue
        # THE CHILD'S OWN `L0` TOTALS, counted in rows over the tabled rows, hold
        # before its family is judged, as V12.7's dated line of 2026-11-10 says of
        # every non-derived member (repair 2 of lane GRb, Codex's item 7: the build
        # read the parents' alone, so a reading moved to another `L0` band inside
        # its family's band left the family HELD).
        published_child = row_ladder[child]["totals"] if isinstance(_get(row_ladder[child], "totals"), list) else []
        counted_child = [0 for _band in published_child]
        child_inside = True
        for key in order:
            for row in rows_of[key]:
                code = row_codes[child][row]
                if 0 <= code < len(counted_child):
                    counted_child[code] += 1
                else:
                    child_inside = False
        child_held = child_inside and counted_child == [_whole(one) for one in published_child]
        if not census_held or not child_held or any(name not in held_totals for name, _level in parents if name not in derived):
            lines += [validation.ChainFamily(index, child, level, tuple(parents), table_written, validation.WITHHELD, CENSUS_DIFFERS if not census_held else NOT_JUDGED)]
            not_judged += 1
            continue
        child_scale = row_scales[child]
        bands = child_scale.counts[level]
        measured_rows = [[0 for _band in range(bands)] for _line in table_written]
        for patient_at, key in enumerate(order):
            cell = cell_of(parents, patient_at)
            if cell < 0 or cell >= len(measured_rows):
                continue
            for row in rows_of[key]:
                code = row_codes[child][row]
                if code >= 0:
                    measured_rows[cell][child_scale.maps[level][code]] += 1
        if any(0 < one < floor for line in measured_rows for one in line):
            lines += [validation.ChainFamily(index, child, level, tuple(parents), table_written, validation.WITHHELD, PATIENT_GATE)]
            continue
        verdict = validation.HELD if tuple(tuple(line) for line in measured_rows) == table_written else validation.MISSED
        lines += [validation.ChainFamily(index, child, level, tuple(parents), table_written, verdict)]
    # -- each published Q_P, the position lists and the patient-fixed row censuses --
    extra: "list[validation.PatientLine]" = []
    grids = {f"{entry['column']}": entry for entry in grain["grid"] if isinstance(entry, dict)} if isinstance(_get(grain, "grid"), list) else {}
    trend = grain["trend"] if isinstance(_get(grain, "trend"), list) else []
    for cell_written in trend:
        column = f"{cell_written['column']}"
        labels = [f"{label}" for label in cell_written["cell"]]
        subject = f"{column} in the cell"
        for label in labels:
            subject = subject + f" {label}"
        if not census_held:
            extra += [validation.PatientLine("trend", subject, validation.WITHHELD, CENSUS_DIFFERS)]
            continue
        if column not in grids or column not in place_of or column not in blocks:
            extra += [validation.PatientLine("trend", subject, "", NO_SUCH_COLUMN)]
            continue
        grid = grids[column]
        top_code = _whole_text(f"{grid['K']}")
        want: "dict[str, str]" = {}
        for label in labels:
            name_part, value_part = _label_parts(label)
            want[name_part] = value_part
        held_levels: "dict[str, int]" = {}
        for written_family in chain_written:
            family = _published_family(written_family)
            members = dict(family.parents)
            members[family.child] = family.level
            if all(name in members for name in want):
                held_levels = members
                break
        values = exact_readings(column)
        total = 0
        members_count = 0
        rho = _whole_text(want[R_NAME]) if R_NAME in want else 0
        for patient_at, key in enumerate(order):
            if r_of[key] != rho:
                continue
            same = True
            for name in want:
                label = want[name]
                if name == R_NAME:
                    continue
                if name not in band_of_patient or name not in scales:
                    same = False
                    break
                code = band_of_patient[name][patient_at]
                level = held_levels[name] if name in held_levels else 0
                if code < 0 or f"{scales[name].maps[level][code]}" != label:
                    same = False
            if not same:
                continue
            members_count += 1
            for j, row in enumerate(rows_of[key]):
                code = patient_rules.grid_code_of(grid["u"], grid["L"], top_code, values[row])
                total += code * (2 * (j + 1) - rho - 1)
        if 0 < members_count < floor:
            extra += [validation.PatientLine("trend", subject, validation.WITHHELD, PATIENT_GATE)]
            continue
        q = _whole(cell_written["q"])
        window_high = 2 * q + 1 if rho % 2 == 0 else 2 * q
        extra += [validation.PatientLine("trend", subject, validation.HELD if 2 * q <= total <= window_high else validation.MISSED)]
    positions = grain["positions"] if isinstance(_get(grain, "positions"), list) else []
    for entry in positions:
        column = f"{entry['column']}"
        listed = entry["values"] if isinstance(entry["values"], list) else []
        if not any(value is not None for value in listed):
            continue
        if column not in place_of:
            extra += [validation.PatientLine("positions", column, "", NO_SUCH_COLUMN)]
            continue
        # THE CELLS AS THE DESCRIPTION READ THEM (repair 2 of lane GRb, Codex's
        # item 6): the list was read through the marks its block keeps (the age
        # top-code and its pool, the year cut, dates in disguise held), so the
        # file's cells are read through them too; a column carrying none is
        # read as written.
        cells = chain.described_cells(
            table, place_of[column], blocks[column] if column in blocks else {}, settings, declared_of(column),
            stored_as[place_of[column]] if place_of[column] < len(stored_as) else "",
        )
        list_held = True
        for j, value in enumerate(listed):
            if value is None:
                continue
            seen: "dict[str, int]" = {}
            for key in order:
                if j < len(rows_of[key]):
                    text = cells[rows_of[key][j]]
                    seen[text] = seen[text] + 1 if text in seen else 1
            most = 0
            for text in seen:
                most = max(most, seen[text])
            modal = sorted(text for text in seen if seen[text] == most)
            if modal != [f"{value}"]:
                list_held = False
        extra += [validation.PatientLine("positions", column, validation.HELD if list_held else validation.MISSED)]
    fixed_rows = grain["fixed_rows"] if isinstance(_get(grain, "fixed_rows"), list) else []
    for entry in fixed_rows:
        column = f"{entry['column']}"
        if not census_held or column not in band_of_patient or column not in scales:
            extra += [validation.PatientLine("fixed rows", column, validation.WITHHELD, CENSUS_DIFFERS if not census_held else NO_SUCH_COLUMN)]
            continue
        level = _LEVEL_OF[f"{entry['level']}"] if f"{entry['level']}" in _LEVEL_OF else 0
        published_rows = [_whole(one) for one in entry["rows"]]
        summed = [0 for _one in published_rows]
        for patient_at, key in enumerate(order):
            code = band_of_patient[column][patient_at]
            if code >= 0 and scales[column].maps[level][code] < len(summed):
                summed[scales[column].maps[level][code]] += r_of[key]
        extra += [validation.PatientLine("fixed rows", column, validation.HELD if summed == published_rows else validation.MISSED)]
    # -- V12.11: THE COUNTING PROCESS (contract 4.6c.14; lane GRb2-b, plan P4-D491 part b) --
    intervals = _get(grain, "intervals")
    if isinstance(intervals, list) and intervals and isinstance(intervals[0], dict):
        from synthtwin import patient_intervals

        start_name = f"{intervals[0]['start']}"
        stop_name = f"{intervals[0]['stop']}"
        if start_name in place_of and stop_name in place_of and start_name in blocks and stop_name in blocks:
            texts: "dict[str, list[str]]" = {}
            for key in ("switches", "end_events"):
                entries_of = grain[key] if isinstance(_get(grain, key), list) else []
                for entry in entries_of:
                    if isinstance(entry, dict) and f"{entry['column']}" in place_of:
                        texts[f"{entry['column']}"] = reading.column_values(table, place_of[f"{entry['column']}"])
            hazard_bands: "dict[str, list[int]]" = {}
            hazard_columns = _get(_get(grain, "hazard"), "columns")
            for entry in hazard_columns if isinstance(hazard_columns, list) else []:
                name = f"{entry['column']}" if isinstance(entry, dict) else ""
                if name in band_of_patient and name in scales and f"{entry['level']}" in _LEVEL_OF:
                    level = _LEVEL_OF[f"{entry['level']}"]
                    hazard_bands[name] = [scales[name].maps[level][code] if code >= 0 else -1 for code in band_of_patient[name]]
            for kind, subject, verdict, reason in patient_intervals.lines(
                grain, [rows_of[key] for key in order], exact_readings(start_name), exact_readings(stop_name), texts, hazard_bands, floor,
            ):
                extra += [validation.PatientLine(kind, subject, verdict, reason)]
        else:
            extra += [validation.PatientLine("intervals", f"{start_name} to {stop_name}", "", NO_SUCH_COLUMN)]
    counted_lines: "dict[str, int]" = {validation.HELD: 0, validation.MISSED: 0, validation.WITHHELD: 0, "": 0}
    for total_line in totals:
        counted_lines[total_line.verdict] += 1
    for line in lines:
        counted_lines[line.verdict] += 1
    for one in extra:
        counted_lines[one.verdict] += 1
    return validation.ChainLines(
        (),
        tuple(totals),
        tuple(lines),
        (),
        counted_lines[validation.HELD],
        counted_lines[validation.MISSED],
        counted_lines[validation.WITHHELD],
        counted_lines[""],
        not_judged,
        (),
        tuple(extra),
    )


def _derived_scale(entry: "dict[str, object]") -> "chain_rules.Ladder | None":
    """A derived column's published ladder: one band an `L0` band, its coarser levels as published."""
    l0 = entry["l0"] if "l0" in entry else None
    totals = entry["totals"] if "totals" in entry else None
    if not isinstance(l0, list) or not isinstance(totals, list):
        return None
    count = len(l0)
    second = _published_level(entry["l1"] if "l1" in entry else None, count)
    third = _published_level(entry["l2"] if "l2" in entry else None, count)
    if second is None or third is None:
        return None
    return chain_rules.Ladder(
        f"{entry['column']}",
        tuple((f"band {at}",) for at in range(count)),
        (tuple(range(count)), second, third),
        (count, max(second) + 1 if second else 1, max(third) + 1 if third else 1),
        tuple(_whole(one) for one in totals),
        tuple(True for _one in range(count)),
    )


_LEVEL_OF = {"L0": 0, "L1": 1, "L2": 2}


def _label_parts(label: str) -> "tuple[str, str]":
    """A trend cell's label `name=value` as its two parts (the last `=` divides them)."""
    if not isinstance(label, str):
        raise TypeError("a label is text")
    at = len(label) - 1
    while at >= 0 and label[at] != "=":
        at -= 1
    if at < 0:
        return label, ""
    return label[:at], label[at + 1:]


def _whole_text(text: str) -> int:
    """A text of digits read as a whole number, else 0."""
    if not isinstance(text, str) or not text:
        return 0
    value = 0
    for character in text:
        if character < "0" or character > "9":
            return 0
        value = value * 10 + (ord(character) - ord("0"))
    return value
