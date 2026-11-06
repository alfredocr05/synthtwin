"""Validator V12 for the chain's families, layer L1 (validation method V12; lane CHv, plan P4-D430).

NOT IN FORCE. Invariant S12 stands until the landing that ships stage 6
whole: `synthtwin validate` never turns this on. It runs only where a
caller hands `cli.main` the chain's switch, which reaches
`validation.measure` as the description's parsed document; every other
run, report and exit code is what it was.

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

from synthtwin import chain, chain_rules, reading, taxonomy, validation

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
    for holder in (document, redescribed):
        settings_block = _get(holder, "settings")
        for key in ("forced_identifiers", "person_columns"):
            listed = _get(settings_block, key)
            if isinstance(listed, list):
                for name in listed:
                    named |= {f"{name}"}
        columns = _get(holder, "columns")
        if isinstance(columns, list):
            for block in columns:
                if isinstance(block, dict) and _get(block, "role") == taxonomy.ROLE_IDENTIFIER:
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
    third = chain_rules.union_closure(bands, start.groups[2])
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
    gate_open = not chain_rules.w1_refusals(families, scales, groups)
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
    counted_lines: "dict[str, int]" = {validation.HELD: 0, validation.MISSED: 0, validation.WITHHELD: 0, "": 0}
    for total in totals:
        counted_lines[total.verdict] += 1
    for line in lines:
        counted_lines[line.verdict] += 1
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
    )


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
