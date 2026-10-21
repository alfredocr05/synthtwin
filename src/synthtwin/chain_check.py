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
rule is carried, no slope is published (ruling R12) and no moment
(lane MPOL's gate), so `rules`, `withheld` and every family's `slopes`
must be empty and `moments` null; a description that fills one was
written by a later landing and is refused as one this version cannot
check.
"""

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
    if statistical["moments"] is not None or statistical["rules"] != [] or statistical["withheld"] != []:
        raise _broken("S28", "rules", "this version carries no rule, no moment and no withheld class")
    # -- ineligible and the ladder (S23) --
    reasons = statistical["ineligible"]
    out_of_ladder: "set[str]" = set()
    if not isinstance(reasons, list):
        raise _broken("S27", "ineligible", "a list")
    for entry in reasons:
        if not isinstance(entry, dict) or sorted(entry) != ["column", "reason"]:
            raise _broken("S27", "ineligible", "each entry names a column and a reason")
        if entry["column"] not in blocks or entry["reason"] not in chain_rules.INELIGIBLE_REASONS:
            raise _broken("S27", f"{entry['column']}", "a reason of contract 4.6b.1 for a column of this table")
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
    # RULE W1, in full.
    groups: "dict[str, set[int]]" = {}
    for name in eligible:
        groups[name] = chain_rules.small_group_bands(blocks[name], starts[name], scales[name], floor)
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
        if start.is_label and len(names[at]) == 1 and isinstance(names[at][0], tuple):
            for label, count in chain_rules.label_levels(block):
                if names[at][0] == (label,) and totals[at] != count:
                    raise _broken("S23", name, "a level's band counts its published count")
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
        if not isinstance(parent, dict) or sorted(parent) != ["column", "level"] or parent["column"] not in scales:
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
        if earliest is None or anchor != earliest:
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
