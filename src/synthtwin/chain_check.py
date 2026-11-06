"""The invariants a loader checks on the chain, S23 to S28 (contract 4.6b.11; lane CHa, plan P4-D418).

NOT IN FORCE. `contract.load_profile` reads `relationships.statistical`
only when it is asked to with `chain=True`, which no shipped command
does: `synthtwin generate` and `synthtwin validate` keep invariant S12
word for word and refuse any description that fills the slot.

Each check reads the description alone. A description failing one is
refused, naming the family or the column and the invariant, in words a
person can act on (`errors.profile_chain_broken`). Which options were
eligible is a function of the description (inventory rows 3 to 5a), so
the loader recomputes RULES W3, NE, W1 and WE from the published totals
and tables and finds every placed family eligible. In this landing no
rule is carried and no slope is published apart, so `rules`, `withheld`
and every family's `slopes` must be empty; `moments`, null or rule B's
object (lane MPp, plan P4-D455), is held to S39 to S43 (`check_moments`).
A description that fills another slot was written by a later landing and
is refused as one this version cannot check.
"""


from synthtwin import chain_moments
from synthtwin import chain_rules
from synthtwin import errors


def _get(mapping: "dict[str, object]", key: str) -> object:
    if key in mapping:
        return mapping[key]
    return None


def _broken(invariant: str, where: str, detail: str) -> errors.ProfileError:
    return errors.ProfileError(errors.profile_chain_broken(invariant, where, detail))


def _whole(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _level_of(value: object, invariant: str, where: str) -> int:
    for place in range(3):
        if value == chain_rules.LEVELS[place]:
            return place
    raise _broken(invariant, where, "a level is one of L0, L1 and L2")


def _starting_of(name: object) -> object:
    """A published starting-band descriptor in the form `chain_rules` builds it."""
    if isinstance(name, list):
        return tuple(name)
    return name


def check(document: "dict[str, object]") -> None:
    """Refuse a description whose chain breaks S23 to S28; return where every one holds."""
    relationships = _get(document, "relationships")
    statistical = _get(relationships, "statistical") if isinstance(relationships, dict) else None
    if statistical is None:
        return
    if not isinstance(statistical, dict):
        raise _broken("S24", "relationships.statistical", "the chain is an object")
    expected = ("chain", "ineligible", "ladder", "moments", "not_carried", "procedure", "rules", "withheld", "words")
    if sorted(statistical) != list(expected):
        raise _broken("S24", "relationships.statistical", "the chain holds exactly its nine keys")
    settings = _get(document, "settings")
    floor = _get(settings, "small_cell_floor") if isinstance(settings, dict) else None
    if not _whole(floor) or not isinstance(floor, int):
        raise _broken("S23", "settings", "the floor is a whole number")
    columns = _get(document, "columns")
    blocks: "dict[str, dict[str, object]]" = {}
    schema: "list[str]" = []
    if isinstance(columns, list):
        for block in columns:
            if isinstance(block, dict) and isinstance(_get(block, "name"), str):
                blocks[f"{block['name']}"] = block
                schema += [f"{block['name']}"]
    rows = _get(document, "n_rows")
    whole_rows = rows if isinstance(rows, int) and not isinstance(rows, bool) else 0
    blank_rows = chain_rules.records_holding_nothing(document)
    tabled = whole_rows - blank_rows
    procedure = statistical["procedure"]
    if procedure != chain_rules.procedure_record(tabled):
        raise _broken("S24", "procedure", "the constants are this version's (contract 4.6b.14)")
    if statistical["rules"] != [] or statistical["withheld"] != []:
        raise _broken("S28", "rules", "this version carries no rule and no withheld class")
    # -- ineligible and the ladder (S23) --
    reasons = statistical["ineligible"]
    out_of_ladder: "set[str]" = set()
    if not isinstance(reasons, list):
        raise _broken("S27", "ineligible", "a list")
    for entry in reasons:
        if not isinstance(entry, dict) or sorted(entry) != ["column", "reason"]:
            raise _broken("S27", "ineligible", "each entry names a column and a reason")
        if not isinstance(entry["column"], str) or not isinstance(entry["reason"], str):
            raise _broken("S27", "ineligible", "each entry names a column and a reason in words")
        if entry["column"] not in blocks or entry["reason"] not in chain_rules.INELIGIBLE_REASONS:
            raise _broken("S27", f"{entry['column']}", "a reason of contract 4.6b.1 for a column of this table")
        if entry["reason"] == "computed":
            # S28: a `computed` column is named by exactly one carried rule,
            # and this version carries none (Codex's item 9 on repair 1).
            raise _broken("S28", f"{entry['column']}", "a column ineligible as computed is named by a carried rule, and this version carries none")
        out_of_ladder = out_of_ladder | {f"{entry['column']}"}
    eligible = [name for name in schema if name not in out_of_ladder]
    published = statistical["ladder"]
    if not isinstance(published, list) or len(published) != len(eligible):
        raise _broken("S23", "ladder", "one entry for every eligible column, in schema order")
    scales: "dict[str, chain_rules.Ladder]" = {}
    starts: "dict[str, chain_rules.Starting]" = {}
    for at in range(len(eligible)):
        name = eligible[at]
        entry = published[at]
        if not isinstance(entry, dict) or _get(entry, "column") != name:
            raise _broken("S23", name, "the ladder's entries stand in schema order")
        scale, start = _ladder_of(entry, blocks[name], floor, tabled, blank_rows)
        scales[name] = scale
        starts[name] = start
    # -- the moments rule B releases (S39 to S43, contract 4.6d.0) --
    groups: "dict[str, set[int]]" = {}
    for name in eligible:
        groups[name] = chain_rules.small_group_bands(blocks[name], starts[name], scales[name], floor)
    if statistical["moments"] is not None:
        check_moments(statistical["moments"], blocks, eligible, scales, floor, tabled, groups)
    # -- the chain (S24, S25) --
    chain = statistical["chain"]
    if not isinstance(chain, list) or not chain:
        raise _broken("S24", "chain", "a chain lists its families")
    families: "list[chain_rules.Family]" = []
    seen_children: "set[str]" = set()
    k_max = chain_rules.K_MAX
    for at in range(len(chain)):
        family = _family_of(chain[at], at, families, scales, eligible, floor, tabled, k_max)
        if family.child in seen_children:
            raise _broken("S24", family.child, "every eligible column is the child of exactly one family")
        seen_children = seen_children | {family.child}
        families += [family]
    if seen_children != set(eligible):
        raise _broken("S24", "chain", "every eligible column is the child of exactly one family")
    if all(not family.parents for family in families):
        raise _broken("S24", "chain", "a chain of families with no parent stands only beside a carried rule")
    # W3 and NE: each placed family's levels among the variants offered.
    for at in range(len(families)):
        family = families[at]
        if not family.parents:
            continue
        _offered(family, at, families, scales, eligible, floor, tabled)
    # RULE W1, in full (the own-fact groups read above, before the moments).
    failing = chain_rules.w1_refusals(families, scales, groups)
    if failing:
        raise _broken("S24", failing[0][0], "RULE W1: a band holding a small group of the column reaches two bands of every other column's coarsest level")
    # RULE WE.
    blank_counts: "dict[str, int]" = {}
    for name in eligible:
        blank = _get(blocks[name], "n_missing_blank")
        blank_counts[name] = (blank if isinstance(blank, int) else 0) - blank_rows
    x0 = chain_rules.blank_cell(scales, blank_counts)
    room = chain_rules.blank_record_room(document, floor) + chain_rules.outside_cells(document, set(eligible))
    if x0 is not None and chain_rules.cell_bound(x0, families, scales, tabled) > room:
        raise _broken("S24", "chain", "RULE WE: the rows blank in every eligible column fit the records holding nothing")
    # -- words and names (S27) --
    words, implied = chain_rules.words_of(eligible, families)
    if statistical["words"] != words:
        raise _broken("S27", "words", "every candidate pair once, in schema order, with the word the description gives it")
    if statistical["not_carried"] != implied:
        raise _broken("S27", "not_carried", "exactly the pairs reading implied")


def _ladder_of(
    entry: "dict[str, object]",
    block: "dict[str, object]",
    floor: int,
    tabled: int,
    blank_rows: int,
) -> "tuple[chain_rules.Ladder, chain_rules.Starting]":
    """One ladder entry read back and checked against its column's own facts (S23)."""
    name = f"{_get(block, 'name')}"
    if sorted(entry) != ["column", "l0", "l1", "l2", "totals"]:
        raise _broken("S23", name, "a ladder entry holds column, l0, l1, l2 and totals")
    start = chain_rules.starting_bands(block, (True, True, True))
    if start is None:
        raise _broken("S23", name, "a column whose role takes no ladder")
    l0 = entry["l0"]
    totals = entry["totals"]
    if not isinstance(l0, list) or not isinstance(totals, list) or len(l0) != len(totals) or not l0:
        raise _broken("S23", name, "one total for every L0 band")
    used: "set[int]" = set()
    bands: "list[list[int]]" = []
    names: "list[tuple[object, ...]]" = []
    for band in l0:
        if not isinstance(band, list) or not band:
            raise _broken("S23", name, "each L0 band lists the starting bands it joins")
        places: "list[int]" = []
        for one in band:
            found = -1
            for place in range(len(start.names)):
                if start.names[place] == _starting_of(one):
                    found = place
            if found < 0 or found in used:
                raise _broken("S23", name, "every edge names a rung the column publishes, and each band covers its cells once")
            used = used | {found}
            places += [found]
        if places != sorted(places):
            raise _broken("S23", name, "a band lists its starting bands in band order")
        if not start.is_label and places != list(range(places[0], places[0] + len(places))):
            raise _broken("S23", name, "a band of a number, date or clock column is a run of adjacent starting bands")
        bands += [places]
        names += [tuple(start.names[place] for place in places)]
    for total in totals:
        if not isinstance(total, int) or isinstance(total, bool) or total < 0 or 0 < total < floor:
            raise _broken("S23", name, "every L0 total is 0 or at least the floor")
    if sum(totals) != tabled:
        raise _broken("S23", name, "the L0 totals sum to the tabled rows")
    for at in range(len(bands)):
        if names[at] == (chain_rules.MISSING,):
            missing = _get(block, "n_missing")
            if not isinstance(missing, int) or totals[at] != missing - blank_rows:
                raise _broken("S23", name, "the missing band counts the column's absent cells less the records holding nothing")
    # Every starting band is in one L0 band, or holds no row by the column's
    # own counts; on a label column every band totals its members' counts
    # (Codex's item 2 on repair 1: a level left out, and a merged band
    # printing more than its labels count, were accepted).
    known = _starting_counts(block, start, blank_rows)
    for place in range(len(start.names)):
        if place in used:
            continue
        if (start.value[place] and not start.is_label) or (start.is_label and known[place] is None) or known[place] not in (None, 0):
            raise _broken("S23", name, "every starting band holding a row stands in one L0 band")
    if start.is_label:
        for at in range(len(bands)):
            counted = 0
            for place in bands[at]:
                one = known[place]
                if one is None:
                    raise _broken("S23", name, "a label column's band counts are its published counts")
                counted += one
            if totals[at] != counted:
                raise _broken("S23", name, "a band of a label column counts the published counts of what it joins")
    second = chain_rules.union_closure(bands, start.groups[1])
    third = chain_rules.union_closure(bands, start.groups[2])
    if entry["l1"] != chain_rules.bands_of(second, max(second) + 1) or entry["l2"] != chain_rules.bands_of(third, max(third) + 1):
        raise _broken("S23", name, "L1 and L2 are read through L0, so the levels nest")
    ordered = tuple(any(start.value[place] for place in band) for band in bands)
    scale = chain_rules.Ladder(
        name,
        tuple(names),
        (tuple(range(len(bands))), second, third),
        (len(bands), max(second) + 1, max(third) + 1),
        tuple(totals),
        ordered,
    )
    return scale, start


def _starting_counts(block: "dict[str, object]", start: "chain_rules.Starting", blank_rows: int) -> "list[int | None]":
    """Each starting band's rows on the tabled rows where the column's own counts fix them, else None."""
    out: "list[int | None]" = [None] * len(start.names)
    missing = _get(block, "n_missing")
    present = _get(block, "n_present")
    levels = chain_rules.label_levels(block)
    for place in range(len(start.names)):
        band = start.names[place]
        if band == chain_rules.MISSING:
            out[place] = missing - blank_rows if _whole(missing) and isinstance(missing, int) else None
        elif not start.is_label and band in (chain_rules.OTHER, chain_rules.LABELS):
            out[place] = _spread_count(block, band)
        elif start.is_label and band == chain_rules.POOL:
            if _whole(present) and isinstance(present, int):
                out[place] = present - sum(count for _label, count in levels)
        elif start.is_label and isinstance(band, tuple) and len(band) == 1:
            for label, count in levels:
                if band == (label,):
                    out[place] = count
    return out


def _spread_count(block: "dict[str, object]", band: object) -> "int | None":
    """An ordered column's `other` or `labels` band's rows where its own counts fix them, else None."""
    role = f"{_get(block, 'role')}"
    present = _get(block, "n_present")
    if not _whole(present) or not isinstance(present, int):
        return None
    if role in (chain_rules.ROLE_COUNT, chain_rules.ROLE_CONTINUOUS, chain_rules.ROLE_AFFIXED):
        used = _get(block, "n_used_in_statistics")
        if band == chain_rules.LABELS:
            return 0
        return present - used if _whole(used) and isinstance(used, int) else None
    if role == chain_rules.ROLE_COMPOUND:
        numbers = _get(block, "n_numeric_cells")
        labelled = _get(block, "n_label_cells")
        if not _whole(numbers) or not _whole(labelled) or not isinstance(numbers, int) or not isinstance(labelled, int):
            return None
        return labelled if band == chain_rules.LABELS else present - numbers - labelled
    if role in (chain_rules.ROLE_DATETIME, chain_rules.ROLE_CLOCK):
        unparsed = _get(block, "n_unparsed")
        if band == chain_rules.LABELS:
            return 0
        return unparsed if _whole(unparsed) and isinstance(unparsed, int) else 0
    return None


def _family_of(
    entry: object,
    at: int,
    families: "list[chain_rules.Family]",
    scales: "dict[str, chain_rules.Ladder]",
    eligible: "list[str]",
    floor: int,
    tabled: int,
    k_max: int,
) -> chain_rules.Family:
    """One chain entry read back and checked (S24, S25)."""
    where = f"chain[{at}]"
    if not isinstance(entry, dict) or sorted(entry) != ["anchor", "child", "level", "parents", "slopes", "table"]:
        raise _broken("S24", where, "a family holds anchor, child, level, parents, slopes and table")
    child = entry["child"]
    if not isinstance(child, str) or child not in scales:
        raise _broken("S24", where, "the child is an eligible column")
    if entry["slopes"] is not None:
        raise _broken("S26", child, "no slope is published while no publishing region stands (ruling R12)")
    level = _level_of(entry["level"], "S24", child)
    parents_written = entry["parents"]
    if not isinstance(parents_written, list) or len(parents_written) > k_max:
        raise _broken("S24", child, "a family's parents number at most k_max")
    parents: "list[tuple[str, int]]" = []
    for parent in parents_written:
        if not isinstance(parent, dict) or sorted(parent) != ["column", "level"] or not isinstance(parent["column"], str) or parent["column"] not in scales:
            raise _broken("S24", child, "each parent is an eligible column with a level")
        parents += [(f"{parent['column']}", _level_of(parent["level"], "S24", child))]
    place_of: "dict[str, int]" = {}
    for place in range(len(eligible)):
        place_of[eligible[place]] = place
    order = [place_of[name] for name, _level in parents]
    if order != sorted(order) or len(set(order)) != len(order):
        raise _broken("S24", child, "the parents stand in schema order, each once")
    anchor = entry["anchor"]
    if not parents:
        if anchor is not None:
            raise _broken("S24", child, "a family with no parent has no anchor")
    else:
        earliest = None
        for place in range(len(families)):
            held = {name for name, _level in chain_rules.members(families[place])}
            if all(name in held for name, _level in parents):
                earliest = place
                break
        # A whole number, never `false` or `0.0` (Codex's item 1 on repair 1:
        # either compared equal to 0 and the margins went unchecked).
        if earliest is None or not _whole(anchor) or anchor != earliest:
            raise _broken("S24", child, "the anchor is the earliest family holding every parent")
        held_levels = dict(chain_rules.members(families[earliest]))
        for name, parent_level in parents:
            if parent_level < held_levels[name]:
                raise _broken("S24", child, "each parent stands at its level in the anchor or coarser")
    table = entry["table"]
    sizes = [scales[child].counts[level]] + [scales[name].counts[parent_level] for name, parent_level in parents]
    width = 1
    for size in sizes[1:]:
        width *= size
    if not isinstance(table, list) or len(table) != width:
        raise _broken("S25", child, "the table is complete: one row for each joint cell of the parents")
    flat: "list[int]" = []
    for row in table:
        if not isinstance(row, list) or len(row) != sizes[0]:
            raise _broken("S25", child, "the table is complete: one column for each band of the child")
        for cell in row:
            if not isinstance(cell, int) or isinstance(cell, bool) or cell < 0 or 0 < cell < floor:
                raise _broken("S25", child, "every cell is 0 or at least the floor")
            flat += [cell]
    if sum(flat) != tabled:
        raise _broken("S25", child, "the table sums to the tabled rows")
    family = chain_rules.Family(child, level, tuple(parents), anchor if isinstance(anchor, int) and not isinstance(anchor, bool) else None, tuple(flat))
    # Its sum over the parents is the child's L0 totals at its level.
    by_child = [0] * sizes[0]
    for index in range(len(flat)):
        by_child[index % sizes[0]] += flat[index]
    if by_child != chain_rules.totals_at(scales[child], level):
        raise _broken("S25", child, "the table's sum over the parents is the child's L0 totals at its level")
    if parents and family.anchor is not None:
        by_parents = [0] * width
        for index in range(len(flat)):
            by_parents[index // sizes[0]] += flat[index]
        margins = chain_rules.parent_cells(scales, tuple(name for name, _level in parents), families[family.anchor])
        if by_parents != chain_rules.parent_cells_at(margins, tuple(parent_level for _name, parent_level in parents)):
            raise _broken("S25", child, "the table's sum over the child is its anchor's table summed to its parents")
    elif not parents and flat != list(chain_rules.totals_at(scales[child], level)):
        raise _broken("S25", child, "a family with no parent is the child's totals at its level")
    return family


def _offered(
    family: chain_rules.Family,
    at: int,
    families: "list[chain_rules.Family]",
    scales: "dict[str, chain_rules.Ladder]",
    eligible: "list[str]",
    floor: int,
    tabled: int,
) -> None:
    """W3 and NE recomputed: the family's levels are among the variants they offer (S24)."""
    names = [family.child] + [name for name, _level in family.parents]
    if family.anchor is None:
        return
    anchor = families[family.anchor]
    if at == 1 and not anchor.parents and family.anchor == 0:
        start = [0, 0]
        margins = chain_rules.parent_cells(scales, (names[1],), None)
    else:
        held = dict(chain_rules.members(anchor))
        start = [0] + [held[name] for name in names[1:]]
        margins = chain_rules.parent_cells(scales, tuple(names[1:]), anchor)
    place_of: "dict[str, int]" = {}
    for place in range(len(eligible)):
        place_of[eligible[place]] = place
    order = [place_of[name] for name in names]
    offered = chain_rules.offered_levels([scales[name] for name in names], start, order, margins, tabled, floor)
    placed = [family.level] + [level for _name, level in family.parents]
    if offered is None or any(placed[place] < offered[place] for place in range(len(placed))):
        raise _broken("S24", family.child, "RULES W3 and NE offer the family's levels")


# -- RULE B's MOMENTS (contract 4.6d.0, plan P4-D455): S39 to S43 ----------


def share_counts(share: int, n: int, scale: int = chain_moments.SCALE_SHARE) -> "tuple[int, int]":
    """The counts `c` of `0..n` whose share `c / n` rounds to `share` units of `1 / scale`: `(lowest, highest)`, empty where lowest > highest."""
    low = -((n - 2 * n * share) // (2 * scale))
    high = -((-(2 * n * share + n)) // (2 * scale)) - 1
    return max(low, 0), min(high, n)


def _pins_small(low: int, high: int, floor: int) -> bool:
    """Every count from `low` to `high` lies inside 1 to `floor - 1`: a small count the description fixes or bounds."""
    return low <= high and low >= 1 and high <= floor - 1


def _moment_column(
    entry: object,
    blocks: "dict[str, dict[str, object]]",
    eligible: "list[str]",
    scales: "dict[str, chain_rules.Ladder]",
    floor: int,
    tabled: int,
) -> "tuple[str, str, int, int, int]":
    """One `columns` entry read back (S40, S41, S42): its column, kind, count, its value in units of `1 / unit(n)` (a number's mean, a binary's ones) and a number's spread (0 for a binary)."""
    if not isinstance(entry, dict) or not isinstance(_get(entry, "column"), str):
        raise _broken("S40", "moments.columns", "each entry names a column")
    name = f"{entry['column']}"
    kind = _get(entry, "kind")
    if name not in eligible:
        raise _broken("S40", name, "a moment reads an eligible column only, never a held, identifier, sequence or free-text one")
    block = blocks[name]
    role = _get(block, "role")
    n = _get(entry, "n")
    if not _whole(n) or not isinstance(n, int) or n < floor or n < 2 or n > tabled:
        raise _broken("S41", name, "a column's moments stand over at least the floor's people")
    if kind == chain_moments.KIND_NUMBER:
        if sorted(entry) != ["column", "kind", "mean", "n", "sd"]:
            raise _broken("S40", name, "a number's entry holds column, kind, mean, n and sd")
        if role not in chain_rules.NUMBER_ROLES or not chain_moments.fine(block) or chain_moments.codes_of(block) is None:
            raise _broken("S40", name, "a number is a FINE column of a number role, read on its linear code")
        # Its count is the readings its block lays out (Codex's item 4 on
        # repair 1), as a binary's is its two levels' published totals.
        if n != chain_moments.readings_of(block):
            raise _broken("S41", name, "a number's count is the readings its column block lays out")
        mean_top = 255 * chain_moments.unit(chain_moments.SCALE_MEAN, n)
        sd_top = chain_moments.spread_top(n, chain_moments.unit(chain_moments.SCALE_COLUMN_SPREAD, n))
        for key, top in (("mean", mean_top), ("sd", sd_top)):
            value = entry[key]
            if not _whole(value) or not isinstance(value, int) or value < 0 or value > top:
                raise _broken("S42", name, f"the {key} is a whole number of the units its count states, on the code")
        return name, kind, n, int(entry["mean"]), int(entry["sd"])
    if kind != chain_moments.KIND_BINARY:
        raise _broken("S40", name, "a moment column is a number or a binary")
    if sorted(entry) != ["column", "kind", "n", "share"]:
        raise _broken("S40", name, "a binary's entry holds column, kind, n and share")
    levels = chain_moments.binary_levels(scales[name]) if role == chain_rules.ROLE_BINARY else None
    if levels is None:
        raise _broken("S40", name, "a binary holds exactly two L0 bands, each one published level")
    totals = scales[name].totals
    if n != totals[levels[0]] + totals[levels[1]]:
        raise _broken("S41", name, "a binary's count is its two levels' published totals")
    if entry["share"] != chain_moments.rounded_ratio(totals[levels[1]], n, chain_moments.unit(chain_moments.SCALE_SHARE, n)):
        raise _broken("S42", name, "a binary's share is its second level's published total over its count, in the units its count states")
    return name, kind, n, totals[levels[1]], 0


def _pair_counts(where: str, n: int, first: int, second: int, floor: int, tabled: int) -> None:
    """S41 for one correlation: the four cells of the pair's presence table over the tabled rows (contract 4.6d.0 (2))."""
    if n < floor or n > min(first, second):
        raise _broken("S41", where, "a correlation stands over at least the floor's rows holding both")
    if (first == tabled and n != second) or (second == tabled and n != first):
        raise _broken("S41", where, "beside a column read on every tabled row, the pair's rows are the other column's readings")
    # A column read on every tabled row has, outside the pair, the other
    # column's unread rows: a count the other column publishes about
    # itself, which stands (contract 4.6d.0 (2)). The waiver reads the
    # completeness of the column whose outside count is checked (Codex's
    # item 1 and the verify's item 1 on repair 1), in either order.
    for own in (first, second):
        if not chain_moments.passes(own - n, floor) and own != tabled:
            raise _broken("S41", where, "a column's readings outside the pair are 0 or at least the floor")
    if not chain_moments.passes(tabled - first - second + n, floor):
        raise _broken("S41", where, "the rows holding neither column are 0 or at least the floor")


def _pair_spreads(where: str, pair: "list[object]", n: int, counts: "tuple[int, int]", spreads: "tuple[int, int]") -> None:
    """S42 for one correlation's spreads: `[r, n]` where the pair holds every reading of both columns, else `[r, n, [sd, sd]]`.

    The pair's own two spreads over its rows, in the unit of `n`, each on
    the code's range at `n`; a column whose readings all lie in the pair
    has the pair's spread equal to its own (the same rows, the same unit).
    """
    incomplete = n < counts[0] or n < counts[1]
    if len(pair) != (3 if incomplete else 2):
        raise _broken("S42", where, "a pair publishes its own two spreads exactly where it holds fewer rows than either column's readings")
    if not incomplete:
        return
    found = pair[2]
    if not isinstance(found, list) or len(found) != 2 or not all(_whole(part) and isinstance(part, int) for part in found):
        raise _broken("S42", where, "a pair's spreads are two whole numbers")
    top = chain_moments.spread_top(n, chain_moments.unit(chain_moments.SCALE_COLUMN_SPREAD, n))
    for at in range(2):
        value = found[at]
        if not isinstance(value, int) or value < 0 or value > top:
            raise _broken("S42", where, "a pair's spread lies on the code's range, in the units its count states")
        if counts[at] == n and value != spreads[at]:
            raise _broken("S42", where, "a column whose readings all lie in the pair has the pair's spread equal to its own")


def _bands_agree(where: str, kind: str, groups: "list[list[int]]", n: int, value: int) -> None:
    """S42: the bands' published values, each in its own count's units, agree with the column's own within the rounding."""
    if kind == chain_moments.KIND_BINARY:
        low = high = 0
        for group in groups:
            if group[0] == 0:
                continue
            found = share_counts(group[1], group[0], chain_moments.unit(chain_moments.SCALE_SHARE, group[0]))
            low += found[0]
            high += found[1]
        if not low <= value <= high:
            raise _broken("S42", where, "the bands' shares, in the units their counts state, hold the column's own level total")
        return
    scale = chain_moments.unit(chain_moments.SCALE_MEAN, n)
    finest = scale
    for group in groups:
        if group[0]:
            finest = max(finest, chain_moments.unit(chain_moments.SCALE_MEAN, group[0]))
    # Every unit is a power of ten times the first, so each divides the
    # finest: the sums below are whole numbers of 1 / (2 * finest).
    total = 0
    gap = n * (finest // scale)
    for group in groups:
        if group[0] == 0:
            continue
        times = finest // chain_moments.unit(chain_moments.SCALE_MEAN, group[0])
        total += 2 * group[0] * group[1] * times
        gap += group[0] * times
    if abs(total - 2 * n * value * (finest // scale)) > gap:
        raise _broken("S42", where, "the bands' means, in the units their counts state, add up to the column's mean within the rounding")


def _spreads_agree(where: str, groups: "list[list[int]]", n: int, spread: int) -> None:
    """S42: a number's spread and its bands' counts, means and spreads satisfy the total-variance identity within the rounding (`chain_moments.spreads_agree`)."""
    if not chain_moments.spreads_agree(groups, n, spread):
        raise _broken("S42", where, "the bands' counts, means and spreads hold the column's spread within the rounding (the total-variance identity)")


def check_moments(
    moments: object,
    blocks: "dict[str, dict[str, object]]",
    eligible: "list[str]",
    scales: "dict[str, chain_rules.Ladder]",
    floor: int,
    tabled: int,
    small: "dict[str, set[int]]",
) -> None:
    """Refuse a `moments` object that breaks rule B's invariants S39 to S43 (contract 4.6d.0 (6)).

    S39 its shape and this version's scales; S40 every moment reads an
    eligible number or binary column, never a held one; S41 every count
    it publishes, and every count one subtraction from a published total
    gives (a pair's four presence cells included), is 0 or at least the
    floor, no published share pins a count inside 1 to `f - 1`, and RULE
    W1 where the published facts settle it (`small`: each eligible
    column's `L0` bands holding an own-fact group, as the column's block
    lists them, a subset of what the producer reads on the rows), and a
    number's count the readings its block lays out; S42 every value a
    whole number of the units its own count states, inside its range (a
    spread at most `spread_top` at its count, the `n - 1` divisor), a
    correlation on its count's grid of Fisher's z with the pair's own
    spreads exactly where it holds fewer rows than a column's readings, a
    binary's share its levels' published totals, and the bands agreeing
    with the column within the rounding (their means and shares, and a
    number's spread by the total-variance identity); S43 the pairs: every correlation's pair
    once, every `within` entry's pair once at a published level, at most
    `partners` a column.
    """
    expected = ["columns", "correlations", "partners", "rule", "scales", "within"]
    if not isinstance(moments, dict) or sorted(moments) != expected:
        raise _broken("S39", "moments", "rule B's moments hold columns, correlations, partners, rule, scales and within")
    scales_written = {
        "column_sd": chain_moments.SCALE_COLUMN_SPREAD,
        "correlation": chain_moments.SCALE_CORRELATION,
        "fisher_z": chain_moments.SCALE_FISHER_Z,
        "mean": chain_moments.SCALE_MEAN,
        "sd": chain_moments.SCALE_SPREAD,
        "share": chain_moments.SCALE_SHARE,
    }
    if moments["rule"] != chain_moments.RULE_B or moments["scales"] != scales_written or moments["partners"] != chain_moments.PARTNERS:
        raise _broken("S39", "moments", "the rule, the scales and the partners are this version's (contract 4.6d.0)")
    entries = moments["columns"]
    if not isinstance(entries, list) or not entries:
        raise _broken("S39", "moments.columns", "a list of the moment columns")
    place_of: "dict[str, int]" = {}
    for at in range(len(eligible)):
        place_of[eligible[at]] = at
    read: "list[tuple[str, str, int, int, int]]" = []
    for entry in entries:
        read += [_moment_column(entry, blocks, eligible, scales, floor, tabled)]
    order = [place_of[name] for name, _kind, _n, _value, _sd in read]
    if order != sorted(set(order)):
        raise _broken("S40", "moments.columns", "each column once, in schema order")
    counts = {name: n for name, _kind, n, _value, _sd in read}
    kinds = {name: kind for name, kind, _n, _value, _sd in read}
    values = {name: value for name, _kind, _n, value, _sd in read}
    spreads = {name: sd for name, _kind, _n, _value, sd in read}
    numbers = [name for name, kind, _n, _value, _sd in read if kind == chain_moments.KIND_NUMBER]
    triangle = moments["correlations"]
    if not isinstance(triangle, list) or len(triangle) != len(numbers):
        raise _broken("S43", "moments.correlations", "one row for every number, in the columns' order")
    for at in range(len(numbers)):
        row = triangle[at]
        if not isinstance(row, list) or len(row) != at:
            raise _broken("S43", numbers[at], "row i of the correlations holds the i pairs before it")
        for other in range(at):
            pair = row[other]
            if pair is None:
                continue
            where = f"{numbers[at]} and {numbers[other]}"
            if not isinstance(pair, list) or len(pair) not in (2, 3) or not all(_whole(part) and isinstance(part, int) for part in pair[:2]):
                raise _broken("S42", where, "a correlation is [r, n] in whole numbers, and the pair's two spreads where it holds fewer rows")
            r = int(pair[0])
            n = int(pair[1])
            _pair_counts(where, n, counts[numbers[at]], counts[numbers[other]], floor, tabled)
            if not chain_moments.on_the_grid(r, n):
                raise _broken("S42", where, "r is the tanh of a grid point of Fisher's z at its count, exactly as printed to 12 decimals, and at most 0.999999")
            _pair_spreads(
                where,
                pair,
                n,
                (counts[numbers[at]], counts[numbers[other]]),
                (spreads[numbers[at]], spreads[numbers[other]]),
            )
    within = moments["within"]
    if not isinstance(within, list):
        raise _broken("S43", "moments.within", "a list")
    seen: "list[tuple[int, int]]" = []
    per_column: "dict[str, int]" = {}
    for entry in within:
        if not isinstance(entry, dict) or sorted(entry) not in (["by", "column", "groups"], ["by", "column", "groups", "level"]):
            raise _broken("S43", "moments.within", "each entry holds by, column and groups, and level where it reads the L2 bands")
        name = entry["column"]
        by = entry["by"]
        if not isinstance(name, str) or not isinstance(by, str) or name not in kinds or by not in place_of or by == name:
            raise _broken("S40", "moments.within", "a moment column within the bands of another eligible column")
        where = f"{name} within {by}"
        level = entry["level"] if "level" in entry else chain_moments.LEVEL_BANDS
        if "level" in entry and (level != chain_moments.LEVEL_COARSE or isinstance(level, bool)):
            raise _broken("S43", where, "a grouping read on its L2 bands names level 2; its L1 bands name none")
        seen += [(place_of[name], place_of[by])]
        per_column[name] = per_column[name] + 1 if name in per_column else 1
        totals = chain_rules.totals_at(scales[by], int(level))
        marked = {scales[by].maps[int(level)][band] for band in small[by]} if kinds[name] == chain_moments.KIND_BINARY else set()
        groups = entry["groups"]
        if not isinstance(groups, list) or len(groups) != len(totals):
            raise _broken("S43", where, "one group for every band of the grouping column at its level")
        held = 0
        for band in range(len(groups)):
            group = groups[band]
            if not isinstance(group, list) or not group or not all(_whole(part) for part in group):
                raise _broken("S42", where, "a group is a list of whole numbers")
            n = group[0]
            if n == 0 and len(group) == 1:
                if not chain_moments.passes(totals[band], floor):
                    raise _broken("S41", where, "a band's rows without a reading are 0 or at least the floor")
                if band in marked and totals[band]:
                    raise _broken("S41", where, "RULE W1: a band holding a small group of the grouping column shows two of the binary's levels or its absence")
                continue
            width = 3 if kinds[name] == chain_moments.KIND_NUMBER else 2
            if len(group) != width:
                raise _broken("S42", where, "a number's group is [n, mean, sd], a binary's [n, share]")
            if n < floor or n > totals[band] or not chain_moments.passes(totals[band] - n, floor):
                raise _broken("S41", where, "a band's readings, and its rows without one, are 0 or at least the floor")
            held += n
            if kinds[name] == chain_moments.KIND_NUMBER:
                mean_top = 255 * chain_moments.unit(chain_moments.SCALE_MEAN, n)
                sd_top = chain_moments.spread_top(n, chain_moments.unit(chain_moments.SCALE_SPREAD, n))
                if group[1] < 0 or group[1] > mean_top or group[2] < 0 or group[2] > sd_top:
                    raise _broken("S42", where, "a band's mean and sd lie on the code's range, in the units its count states")
                continue
            scale = chain_moments.unit(chain_moments.SCALE_SHARE, n)
            if group[1] < 0 or group[1] > scale:
                raise _broken("S42", where, "a band's share lies in 0 to 1")
            low, high = share_counts(group[1], n, scale)
            if low > high:
                raise _broken("S42", where, "a band's share is one some count of its readings rounds to")
            if _pins_small(low, high, floor) or _pins_small(n - high, n - low, floor):
                raise _broken("S41", where, "no share fixes or bounds a level's rows inside 1 to f - 1")
            if band in marked and totals[band] == n and (high == 0 or low == n):
                raise _broken("S41", where, "RULE W1: a band holding a small group of the grouping column shows two of the binary's levels or its absence")
        if held != counts[name]:
            raise _broken("S41", where, "the bands' readings add up to the column's")
        _bands_agree(where, f"{kinds[name]}", groups, counts[name], values[name])
        if kinds[name] == chain_moments.KIND_NUMBER:
            _spreads_agree(where, groups, counts[name], spreads[name])
    if seen != sorted(set(seen)):
        raise _broken("S43", "moments.within", "each pair once, by the column's place and then the grouping column's")
    for name in per_column:
        if per_column[name] > chain_moments.PARTNERS:
            raise _broken("S43", name, "at most the stated partners a column")
