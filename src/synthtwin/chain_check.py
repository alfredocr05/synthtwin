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

import fractions

from synthtwin import chain_moments
from synthtwin import chain_rules
from synthtwin import errors
from synthtwin import patient_rules


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
    """Refuse a description whose chain breaks S23 to S28, or its patient layer S29 to S33; return where every one holds."""
    relationships = _get(document, "relationships")
    statistical = _get(relationships, "statistical") if isinstance(relationships, dict) else None
    grain = _get(relationships, "grain") if isinstance(relationships, dict) else None
    if grain is not None:
        _check_patients(document, statistical, grain)
        return
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
    # A later amendment moves no older description (4.6b.5): a record of
    # the version before RULE ONE_BAND is read by its own `L2`.
    one_band = chain_rules.reads_one_band(statistical["procedure"], tabled)
    if one_band is None:
        raise _broken("S24", "procedure", "the constants are this version's or the earlier version's (contract 4.6b.5, 4.6b.14)")
    if statistical["withheld"] != []:
        raise _broken("S28", "withheld", "this version carries no withheld class")
    computed = _computed_named(statistical["rules"])
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
        if (entry["reason"] == "computed") != (entry["column"] in computed):
            # S28: a column is ineligible as `computed` exactly where one
            # carried rule computes it (Codex's item 9 on repair 1).
            raise _broken("S28", f"{entry['column']}", "a column is ineligible as computed exactly where one carried rule computes it")
        out_of_ladder = out_of_ladder | {f"{entry['column']}"}
    if not computed <= out_of_ladder:
        raise _broken("S28", "rules", "every column a carried rule computes is ineligible as computed")
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
        scale, start = _ladder_of(entry, blocks[name], floor, tabled, blank_rows, one_band)
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
    if all(not family.parents for family in families) and not statistical["rules"]:
        raise _broken("S24", "chain", "a chain of families with no parent stands only beside a carried rule")
    # -- the carried rules (S28 as contract 4.6b.7 amends it; lane RO, plan P4-D459) --
    derived = check_rules(statistical["rules"], document, blocks, schema, eligible, scales, groups, floor, tabled)
    # W3 and NE: each placed family's levels among the variants offered.
    for at in range(len(families)):
        family = families[at]
        if not family.parents:
            continue
        _offered(family, at, families, scales, eligible, floor, tabled)
    # RULE W1, in full (the own-fact groups read above, before the moments),
    # each carried rule's derived family read through its parent (rule 4).
    failing = chain_rules.w1_refusals(families, scales, groups, derived)
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


def _computed_named(listed: object) -> "set[str]":
    """The columns the carried rules compute, as `rules` names them (read before the ladder, S28)."""
    if not isinstance(listed, list):
        raise _broken("S28", "rules", "a list")
    out: "set[str]" = set()
    for entry in listed:
        if isinstance(entry, dict) and isinstance(_get(entry, "computed"), str):
            out = out | {f"{entry['computed']}"}
    return out


def check_rules(
    listed: object,
    document: "dict[str, object]",
    blocks: "dict[str, dict[str, object]]",
    schema: "list[str]",
    eligible: "list[str]",
    scales: "dict[str, chain_rules.Ladder]",
    groups: "dict[str, set[int]]",
    floor: int,
    tabled: int,
) -> "tuple[chain_rules.Derived, ...]":
    """S28 as contract 4.6b.7 amends it (MR.1 to MR.6; lane RO, plan P4-D459): every carried rule.

    Each clause of the derived option's rules 1 to 6; the class `phrase`,
    or a count from `f` to `L(n)` for a derived carrier only, its
    partition passing row 9's one test on the base; a source carrier's
    own block publishing `n_negative` 0, under MR.3's three source
    conditions; the computed column's block key by key; rule identities
    unique; no rule reading a computed column. Returns each derived
    family as RULE W1 reads it (rule 4, beside the chain's families).
    """
    if not isinstance(listed, list):
        raise _broken("S28", "rules", "a list")
    limit = chain_rules.rule_limit(tabled, floor)
    computed: "set[str]" = set()
    read: "set[str]" = set()
    derived: "list[chain_rules.Derived]" = []
    for at in range(len(listed)):
        entry = listed[at]
        where = f"rules[{at}]"
        if not isinstance(entry, dict) or sorted(entry) != list(chain_rules.RULE_ENTRY_KEYS):
            raise _broken("S28", where, "a carried rule holds carrier, class, computed, derived, grain, inputs, kind, op and unit")
        kind = entry["kind"]
        target = entry["computed"]
        inputs = entry["inputs"]
        carrier = entry["carrier"]
        klass = entry["class"]
        if kind != chain_rules.RULE_ORDER:
            raise _broken("S28", where, "this version carries order rules alone (a formula rule is lane RD's)")
        if entry["op"] is not None:
            raise _broken("S28", where, "an order rule names no operation")
        if not isinstance(target, str) or target not in blocks:
            raise _broken("S28", where, "a rule computes a column of this table")
        if not isinstance(inputs, list) or len(inputs) != 1 or not isinstance(inputs[0], str) or inputs[0] not in eligible:
            raise _broken("S28", where, "an order rule reads one eligible column")
        first = inputs[0]
        if target in computed or target in read or first in computed or first == target:
            raise _broken("S28", target, "a column is computed by at most one carried rule, and no carried rule reads a computed column")
        a_block = blocks[first]
        kind_of_pair = chain_rules.kind_of_role(_get(a_block, "role"))
        if kind_of_pair is None or chain_rules.has_exponent(a_block):
            raise _broken("S28", first, "a rule's input has a role of the kind its pair reads and no E-notation")
        b_block = blocks[target]
        _computed_block(target, b_block, a_block, kind, schema)
        if chain_rules.first_style(b_block) in chain_rules.EXPONENT_STYLES:
            raise _broken("S28", target, "a computed column is not first written in E-notation")
        grain = entry["grain"]
        if kind_of_pair == chain_rules.KIND_NUMBER:
            wanted_grain: "str | None" = None
        elif kind_of_pair == chain_rules.KIND_CLOCK:
            wanted_grain = chain_rules.GRAIN_A
        elif chain_rules.every_layout_clocked(a_block) and not chain_rules.first_layout_clocked(b_block):
            wanted_grain = chain_rules.GRAIN_DAY
        else:
            wanted_grain = chain_rules.GRAIN_A
        if grain != wanted_grain:
            raise _broken("S28", where, "the rule's grain is the one its pair's published layouts give")
        step = chain_rules.grain_step(a_block, grain)
        if step is None:
            raise _broken("S28", where, "the input's published layouts give the pair a step")
        seconds = kind_of_pair == chain_rules.KIND_CLOCK or (
            kind_of_pair == chain_rules.KIND_DATE and grain == chain_rules.GRAIN_A and chain_rules.every_layout_clocked(a_block)
        )
        if carrier == chain_rules.CARRIER_DERIVED:
            if entry["unit"] is not None:
                raise _broken("S28", where, "a derived carrier names no unit")
            readings = sum(scales[first].totals[place] for place in range(len(scales[first].totals)) if scales[first].ordered[place])
            if klass == chain_rules.CLASS_PHRASE:
                pass
            elif _whole(klass) and isinstance(klass, int) and floor <= klass <= limit:
                if not chain_rules.partition_passes(readings, floor, limit):
                    raise _broken("S28", where, "a count class stands only where row 9's one test passes its whole partition")
            else:
                raise _broken("S28", where, "the class is the phrase, or a count from the floor to the inference limit")
            derived += [_derived_entry(entry["derived"], where, first, scales[first], groups[first] if first in groups else set(), klass, step, floor)]
        else:
            if klass != chain_rules.CLASS_PHRASE or entry["derived"] is not None:
                raise _broken("S28", where, "a source carrier takes the phrase alone and names no derived column")
            if not isinstance(carrier, str) or carrier not in eligible or carrier in (first, target) or carrier in computed:
                raise _broken("S28", where, "a source carrier is another eligible column")
            d_block = blocks[carrier]
            if _get(d_block, "role") not in chain_rules.NUMBER_PAIR_ROLES or chain_rules.has_exponent(d_block):
                raise _broken("S28", carrier, "a source carrier is a number column with no E-notation")
            if _get(d_block, "n_negative") != 0:
                raise _broken("S28", carrier, "a source carrier's own block publishes n_negative 0")
            refused = chain_rules.source_refusal(entry["unit"], kind_of_pair, seconds, step, d_block, b_block)
            if refused is not None:
                raise _broken("S28", where, f"a source carrier meets MR.3's three source conditions ({refused})")
            read = read | {carrier}
        computed = computed | {target}
        read = read | {first}
    return tuple(derived)


def _computed_block(
    name: str,
    block: "dict[str, object]",
    template: "dict[str, object]",
    kind: str,
    schema: "list[str]",
) -> None:
    """A computed column's block, key by key (contract 4.6b.7, MR.6 (a)): its name, position and the
    rule's role, its own layout words, and every other key `null`, `{}` or `[]`; a number column's own
    affix words beside its rule's role's keys (lane RO's repair 2)."""
    role = chain_rules.computed_role(kind, [f"{_get(template, 'role')}"])
    extra = set(block) - set(template)
    affixed = role in chain_rules.NUMBER_PAIR_ROLES and extra == set(chain_rules.AFFIX_WORDS)
    if not set(template) <= set(block) or (extra and not affixed):
        raise _broken("S28", name, "a computed column's block holds the keys of its rule's role")
    place = 0
    for at in range(len(schema)):
        if schema[at] == name:
            place = at + 1
    if _get(block, "role") != role or _get(block, "position") != place:
        raise _broken("S28", name, "a computed column's block holds its name, its place and its rule's role")
    lists = chain_rules.LAYOUT_LISTS[role] if role in chain_rules.LAYOUT_LISTS else ()
    words = (chain_rules.LAYOUT_WORDS[role] if role in chain_rules.LAYOUT_WORDS else ()) + (chain_rules.AFFIX_WORDS if affixed else ())
    for key in block:
        value = block[key]
        if key in ("name", "position", "role"):
            continue
        if key in lists and isinstance(value, list) and all(isinstance(word, str) for word in value):
            continue
        if key in words and (value is None or isinstance(value, str)):
            continue
        if value is not None and value != {} and value != []:
            raise _broken("S28", name, f"a computed column publishes nothing read from its cells ({key})")


def _derived_entry(
    written: object,
    where: str,
    first: str,
    ladder: "chain_rules.Ladder",
    groups: "set[int]",
    klass: "str | int",
    step: "chain_rules.Exact",
    floor: int,
) -> "chain_rules.Derived":
    """A derived column's entry (S28): one named level, its family `{D | A}` complete, rules 1 to 6."""
    if not isinstance(written, dict) or sorted(written) != list(chain_rules.DERIVED_ENTRY_KEYS):
        raise _broken("S28", where, "a derived carrier names its derived column's edges, level, parent, table and totals")
    names = {name: percents for name, percents in chain_rules.DERIVED_LEVELS}
    level_name = written["name"]
    if not isinstance(level_name, str) or level_name not in names:
        raise _broken("S28", where, "a derived column's level is one of L0, L1, L2 and one")
    percents = names[level_name]
    edges_written = written["edges"]
    edges: "list[chain_rules.Exact]" = []
    for edge in edges_written if isinstance(edges_written, list) else [None]:
        value = chain_rules.decimal_value(edge)
        if value is None or (edges and not edges[-1] < value):
            raise _broken("S28", where, "a derived column's edges are exact decimals, strictly increasing")
        edges += [value]
    if len(edges) > len(percents) or (percents and not edges):
        raise _broken("S28", where, "a derived column's edges are its level's rungs, tied edges taken once")
    parent = written["parent"]
    if not isinstance(parent, dict) or sorted(parent) != ["column", "level"] or parent["column"] != first:
        raise _broken("S28", where, "a derived family's one parent is the rule's input")
    a_level = _level_of(parent["level"], "S28", where)
    totals = written["totals"]
    if not isinstance(totals, list) or len(totals) != len(edges) + 1 or not all(_whole(total) and total >= 0 for total in totals):
        raise _broken("S28", where, "one total for every value band of the derived column")
    table = written["table"]
    rows = ladder.counts[a_level]
    if not isinstance(table, list) or len(table) != rows:
        raise _broken("S28", where, "the derived family's table holds one row for every band of its parent")
    for line in table:
        if not isinstance(line, list) or len(line) != len(edges) + 2 or not all(_whole(cell) and cell >= 0 for cell in line):
            raise _broken("S28", where, "the derived family's table is complete, one count a band of the derived column and its missing band")
    parent_totals = chain_rules.totals_at(ladder, a_level)
    for row in range(rows):
        if sum(table[row]) != parent_totals[row]:
            raise _broken("S28", where, "the derived family's table sums to its parent's totals at its level")
    for band in range(len(edges) + 1):
        if sum(table[row][band] for row in range(rows)) != totals[band]:
            raise _broken("S28", where, "the derived family's table sums to the derived column's totals")
    spread: "set[int]" = set()
    for band in range(rows):
        members = [place for place in range(len(ladder.totals)) if ladder.maps[a_level][place] == band]
        if members and not any(ladder.ordered[place] for place in members):
            spread = spread | {band}
    missing_alone = all(not (chain_rules.MISSING in band and len(band) > 1) for band in ladder.l0)
    group_rows = {ladder.maps[a_level][band] for band in groups}
    level = (level_name, percents, tuple(edges))
    refused = chain_rules.derived_option_refusal(level, list(totals), table, spread, missing_alone, group_rows, klass, step, floor)
    if refused is not None:
        raise _broken("S28", where, f"a derived option meets rules 1 to 6 ({refused})")
    return chain_rules.derived_of(first, a_level, table, not edges)


def _ladder_of(
    entry: "dict[str, object]",
    block: "dict[str, object]",
    floor: int,
    tabled: int,
    blank_rows: int,
    one_band: bool,
) -> "tuple[chain_rules.Ladder, chain_rules.Starting]":
    """One ladder entry read back and checked against its column's own facts (S23).

    `one_band` is False on a description written before RULE ONE_BAND,
    whose `L2` is read at `p50` alone, as it was written.
    """
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
        bands += [places]
        names += [tuple(start.names[place] for place in places)]
    if not start.is_label:
        # A spread band with no cell is no band (4.6b.2), so it stands
        # between no two bands: adjacency is read without it.
        standing = [place for place in range(len(start.names)) if start.value[place] or place in used]
        for places in bands:
            first = 0
            while standing[first] != places[0]:
                first += 1
            if places != standing[first : first + len(places)]:
                raise _broken("S23", name, "a band of a number, date or clock column is a run of adjacent starting bands")
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
    if one_band:
        third = chain_rules.coarsest_level(start, bands, second, third, totals)
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
# -- THE PATIENT LAYER (contract 4.6c.10; lane GRa, plan P4-D449) ---------


def _check_patients(document: "dict[str, object]", statistical: object, grain: object) -> None:
    """Refuse a description whose patient layer breaks S29 to S33, or whose patient chain breaks S23 to S28 in patients.

    `patient_rules.check` reads the layer's shape (its one call site);
    the patient chain is then held to section 4.6b's invariants over the
    patient table, and every row family's certificate, every column's
    one-cell certificate, every trend's SWING and every row census are
    recomputed from published counts alone.
    """
    if not isinstance(grain, dict):
        raise _broken("S29", "relationships.grain", "the patient layer is an object")
    if not isinstance(statistical, dict):
        raise _broken("S29", "relationships.statistical", "the patient chain stands while the layer does")
    expected = ("chain", "ineligible", "ladder", "moments", "not_carried", "procedure", "rules", "withheld", "words")
    if sorted(statistical) != list(expected):
        raise _broken("S24", "relationships.statistical", "the chain holds exactly its nine keys")
    settings = _get(document, "settings")
    floor = _get(settings, "small_cell_floor") if isinstance(settings, dict) else None
    if not isinstance(floor, int) or isinstance(floor, bool):
        raise _broken("S23", "settings", "the floor is a whole number")
    rows = _get(document, "n_rows")
    whole_rows = rows if isinstance(rows, int) and not isinstance(rows, bool) else 0
    blank_rows = chain_rules.records_holding_nothing(document)
    tabled = whole_rows - blank_rows
    found = patient_rules.check(document, grain, tabled, blank_rows, floor)
    census = found["census"]
    classes = found["classes"]
    patients = found["patients"]
    if not isinstance(census, patient_rules.Census) or not isinstance(classes, dict) or not isinstance(patients, int):
        raise _broken("S29", "grain", "the layer's census and classes read back")
    blocks: "dict[str, dict[str, object]]" = {}
    schema: "list[str]" = []
    columns = _get(document, "columns")
    if isinstance(columns, list):
        for block in columns:
            if isinstance(block, dict) and isinstance(_get(block, "name"), str):
                blocks[f"{block['name']}"] = block
                schema += [f"{block['name']}"]
    if statistical["procedure"] != chain_rules.procedure_record(patients):
        raise _broken("S24", "procedure", "the constants are this version's, read over the patients")
    if statistical["moments"] is not None or statistical["rules"] != [] or statistical["withheld"] != []:
        raise _broken("S28", "rules", "this version carries no rule, no moment and no withheld class")
    scales, eligible, derived, groups = _patient_scales(statistical, grain, blocks, schema, classes, census, floor, patients)
    _derived_edges(derived, scales, blocks)
    families = _patient_families(statistical, scales, eligible, floor, patients, derived, groups)
    cells = _cells_of(grain, families, scales, census, _latest_keyed(families, set(derived)))
    row_scales, row_groups = _row_scales(grain, blocks, schema, classes, floor, tabled, blank_rows)
    _recheck_rows(grain, blocks, schema, classes, census, cells, scales, row_scales, derived, floor, tabled, groups, row_groups)
    _recheck_trends(grain, blocks, families, scales, row_scales, cells, census, derived, floor, tabled)
    _recheck_fixed_rows(grain, families, scales, census, row_scales)


def _patient_scales(
    statistical: "dict[str, object]",
    grain: "dict[str, object]",
    blocks: "dict[str, dict[str, object]]",
    schema: "list[str]",
    classes: "dict[str, str]",
    census: patient_rules.Census,
    floor: int,
    patients: int,
) -> "tuple[dict[str, chain_rules.Ladder], list[str], dict[str, dict[str, object]], dict[str, set[int]]]":
    """Each column's ladder on the patient table (S23 in patients): patient-fixed columns, `r`, the derived columns.

    With each column's `L0` bands holding an own-fact group as its
    published block shows them (`chain_rules.small_group_bands`, in
    patients; `r` and the derived columns publish none), which RULE W1
    reads (Codex's review of lane GRa, item 6).
    """
    derived: "dict[str, dict[str, object]]" = {}
    written = grain["derived"]
    if isinstance(written, list):
        for entry in written:
            if isinstance(entry, dict) and isinstance(_get(entry, "name"), str):
                derived[f"{entry['name']}"] = entry
    table_names = [name for name in schema if classes[name] == patient_rules.CLASS_FIXED] + [patient_rules.R_NAME] + list(derived)
    reasons = statistical["ineligible"]
    out_of_ladder: "set[str]" = set()
    if not isinstance(reasons, list):
        raise _broken("S27", "ineligible", "a list")
    for entry in reasons:
        if not isinstance(entry, dict) or sorted(entry) != ["column", "reason"] or entry["column"] not in table_names or entry["reason"] not in chain_rules.INELIGIBLE_REASONS:
            raise _broken("S27", "ineligible", "a reason of contract 4.6b.1 for a column of the patient table")
        out_of_ladder = out_of_ladder | {f"{entry['column']}"}
    eligible = [name for name in table_names if name not in out_of_ladder]
    published = statistical["ladder"]
    if not isinstance(published, list) or len(published) != len(eligible):
        raise _broken("S23", "ladder", "one entry for every eligible column of the patient table, in its order")
    scales: "dict[str, chain_rules.Ladder]" = {}
    groups: "dict[str, set[int]]" = {}
    for at in range(len(eligible)):
        name = eligible[at]
        entry = published[at]
        if not isinstance(entry, dict) or _get(entry, "column") != name:
            raise _broken("S23", name, "the ladder's entries stand in the patient table's order")
        groups[name] = set()
        if name == patient_rules.R_NAME:
            built = patient_rules.r_ladder(census)
            if built is None or entry != chain_rules.published_ladder(built):
                raise _broken("S23", name, "the rows per patient stand at the census's own bands at every level")
            scales[name] = built
        elif name in derived:
            scales[name] = _derived_ladder(entry, derived[name], floor, patients)
        else:
            scale, start = _ladder_of(entry, blocks[name], floor, patients, 0, True)
            scales[name] = scale
            groups[name] = chain_rules.small_group_bands(blocks[name], start, scale, floor)
    return scales, eligible, derived, groups


def _derived_edges(derived: "dict[str, dict[str, object]]", scales: "dict[str, chain_rules.Ladder]", blocks: "dict[str, dict[str, object]]") -> None:
    """S32: each derived column stands in the patient chain, its edges one for each band they open, a first date's its source's rungs (Codex's review of lane GRa, item 9)."""
    for label in derived:
        entry = derived[label]
        if label not in scales:
            raise _broken("S32", label, "a derived column stands in the patient chain")
        kind = f"{entry['kind']}"
        edges = entry["edges"]
        if not isinstance(edges, list) or len(edges) != patient_rules.edges_expected(kind, scales[label]):
            raise _broken("S32", label, "a derived column's edges number one for each band they open")
        if kind != patient_rules.FIRST_DATE:
            continue
        source = f"{entry['source']}"
        rungs = chain_rules.rung_ladder(blocks[source]) if source in blocks else None
        if not isinstance(rungs, dict) or not rungs:
            continue
        expected: "list[object]" = []
        for band in scales[label].l0:
            first = band[0] if band else None
            if isinstance(first, tuple) and len(first) == 2 and first[0] is not None:
                expected += [rungs[f"{first[0]}"] if f"{first[0]}" in rungs else None]
        if edges != expected:
            raise _broken("S32", label, "a first date's edges are its source's rungs at its level")


def _derived_ladder(entry: "dict[str, object]", written: "dict[str, object]", floor: int, patients: int) -> chain_rules.Ladder:
    """A derived column's ladder read back (S32): its bands, its levels, its totals in patients."""
    name = f"{written['name']}"
    if sorted(entry) != ["column", "l0", "l1", "l2", "totals"]:
        raise _broken("S32", name, "a ladder entry holds column, l0, l1, l2 and totals")
    l0 = entry["l0"]
    totals = entry["totals"]
    if not isinstance(l0, list) or not isinstance(totals, list) or len(l0) != len(totals) or len(l0) < 2:
        raise _broken("S32", name, "one total for every band")
    least = patient_rules.own_mean_floor(floor) if written["kind"] == patient_rules.OWN_MEAN else floor
    for total in totals:
        if not isinstance(total, int) or isinstance(total, bool) or 0 < total < least:
            raise _broken("S32", name, "every band of a derived column holds 0 or at least its floor of patients")
    if sum(totals) != patients:
        raise _broken("S32", name, "a derived column's totals sum to the patients")
    names: "list[tuple[object, ...]]" = []
    for band in l0:
        if not isinstance(band, list) or not band:
            raise _broken("S32", name, "each band lists what it joins")
        names += [tuple(_starting_of(one) for one in band)]
    maps: "list[tuple[int, ...]]" = [tuple(range(len(l0)))]
    for key in ("l1", "l2"):
        level = entry[key]
        mapping = [-1] * len(l0)
        if not isinstance(level, list):
            raise _broken("S32", name, "L1 and L2 list the L0 bands they join")
        for at in range(len(level)):
            joined = level[at]
            if not isinstance(joined, list):
                raise _broken("S32", name, "L1 and L2 list the L0 bands they join")
            for place in joined:
                if not isinstance(place, int) or not 0 <= place < len(l0) or mapping[place] >= 0:
                    raise _broken("S32", name, "every L0 band in one band of each coarser level")
                mapping[place] = at
        if min(mapping) < 0:
            raise _broken("S32", name, "every L0 band in one band of each coarser level")
        maps += [tuple(mapping)]
    return chain_rules.Ladder(
        name, tuple(names), (maps[0], maps[1], maps[2]),
        (len(l0), max(maps[1]) + 1, max(maps[2]) + 1), tuple(int(one) for one in totals),
        tuple(True for _band in l0),
    )


def _patient_families(
    statistical: "dict[str, object]",
    scales: "dict[str, chain_rules.Ladder]",
    eligible: "list[str]",
    floor: int,
    patients: int,
    derived: "dict[str, dict[str, object]]",
    groups: "dict[str, set[int]]",
) -> "list[chain_rules.Family]":
    """The patient chain read back (S24, S25 in patients), with the keyed families' rule and the order of its children."""
    chain = statistical["chain"]
    if not isinstance(chain, list):
        raise _broken("S24", "chain", "a chain lists its families")
    families: "list[chain_rules.Family]" = []
    seen: "set[str]" = set()
    for at in range(len(chain)):
        family = _family_of(chain[at], at, families, scales, eligible, floor, patients, chain_rules.K_MAX)
        if family.child in seen:
            raise _broken("S24", family.child, "every eligible column is the child of exactly one family")
        seen = seen | {family.child}
        families += [family]
    if chain and seen != set(eligible):
        raise _broken("S24", "chain", "every eligible column of the patient table is the child of exactly one family")
    for at in range(len(families)):
        if families[at].parents:
            _offered(families[at], at, families, scales, eligible, floor, patients)
    failing = chain_rules.w1_refusals(families, scales, groups)
    if failing:
        raise _broken("S24", failing[0][0], "RULE W1 in patients: a band holding a small group of the column reaches two bands of every other column's coarsest level")
    words, implied = chain_rules.words_of(eligible, families)
    if statistical["words"] != words or statistical["not_carried"] != implied:
        raise _broken("S27", "words", "every candidate pair of the patient table once, with the word the description gives it")
    labels = set(derived)
    r_eligible = patient_rules.R_NAME in scales
    keyed: "list[chain_rules.Family]" = []
    for family in families:
        held = dict(chain_rules.members(family))
        if not family.parents or not (patient_rules.R_NAME in held or set(held) & labels):
            continue
        if r_eligible and set(held) & labels and patient_rules.R_NAME not in held:
            raise _broken("S31", family.child, "a family holding a derived column holds the rows per patient")
        for earlier in keyed:
            for member, level in chain_rules.members(earlier):
                if member not in held or held[member] > level:
                    raise _broken("S31", family.child, "a family holding the rows per patient or a derived column holds every member of every earlier one, at its level or finer")
        if not set(held) & labels and patient_rules.R_NAME in dict(family.parents) and scales[family.child].counts[family.level] != scales[family.child].counts[2]:
            raise _broken("S31", family.child, "before any derived column, a family whose parents hold the rows per patient takes its child at L2")
        keyed += [family]
    return families


def _latest_keyed(families: "list[chain_rules.Family]", labels: "set[str]") -> "int | None":
    """The place of the patient chain's latest KEYED family (departure (3)): parents, and `r` or a derived column among its members; None where none is."""
    found: "int | None" = None
    for at in range(len(families)):
        held = {name for name, _level in chain_rules.members(families[at])}
        if families[at].parents and (patient_rules.R_NAME in held or bool(held & labels)):
            found = at
    return found


def _cells_of(
    grain: "dict[str, object]",
    families: "list[chain_rules.Family]",
    scales: "dict[str, chain_rules.Ladder]",
    census: patient_rules.Census,
    latest: "int | None",
) -> patient_rules.Cells:
    """The grain family's cells as published (4.6c.8 (a)): `G`'s table, or the census's bands.

    `G` is the latest keyed family, which the loader reads off the chain
    itself (`latest`, `_latest_keyed`): a `grain_family` naming another
    family, an earlier one or null beside a keyed family, is refused, so
    every certificate is recomputed on the cells the description's own
    chain fixes (Codex's review of lane GRa, item 2).
    """
    index = grain["grain_family"]
    if index != latest or isinstance(index, bool):
        raise _broken("S31", "grain.grain_family", "the grain family is the patient chain's latest keyed family")
    values = patient_rules.r_band_values(census)
    if index is None:
        counts: "list[int]" = []
        for at in range(len(census.bands)):
            if census.bands[at]:
                counts += [census.bands[at]]
        if census.top_patients:
            counts += [census.top_patients]
        members = ((patient_rules.R_NAME, 0),) if patient_rules.R_NAME in scales else ()
        return patient_rules.Cells(members, (len(values),), tuple(counts), tuple(range(len(values))))
    if not isinstance(index, int) or isinstance(index, bool) or not 0 <= index < len(families):
        raise _broken("S31", "grain.grain_family", "the grain family is a family of the patient chain")
    family = families[index]
    held = chain_rules.members(family)
    sizes = tuple(chain_rules.radices(family, scales))
    names = [name for name, _level in held]
    r_band = [0] * len(family.table)
    if patient_rules.R_NAME in names:
        place = patient_rules.place_in(names, patient_rules.R_NAME)
        for cell in range(len(family.table)):
            r_band[cell] = chain_rules.cell_parts(cell, list(sizes))[place]
    return patient_rules.Cells(tuple(held), sizes, tuple(family.table), tuple(r_band))


def _row_scales(
    grain: "dict[str, object]",
    blocks: "dict[str, dict[str, object]]",
    schema: "list[str]",
    classes: "dict[str, str]",
    floor: int,
    tabled: int,
    blank_rows: int,
) -> "tuple[dict[str, chain_rules.Ladder], dict[str, set[int]]]":
    """`grain.ladder` read back (S23 in rows): one entry for each repeated and dealt date column, in schema order, with each one's own-fact groups in rows."""
    rowed = [name for name in schema if classes[name] in (patient_rules.CLASS_REPEATED, patient_rules.CLASS_DEALT)]
    written = grain["ladder"]
    if not isinstance(written, list) or len(written) != len(rowed):
        raise _broken("S31", "grain.ladder", "one ladder in rows for every repeated and dealt date column")
    out: "dict[str, chain_rules.Ladder]" = {}
    groups: "dict[str, set[int]]" = {}
    for at in range(len(rowed)):
        entry = written[at]
        if not isinstance(entry, dict) or _get(entry, "column") != rowed[at]:
            raise _broken("S31", rowed[at], "each ladder in rows stands in schema order")
        scale, start = _ladder_of(entry, blocks[rowed[at]], floor, tabled, blank_rows, True)
        out[rowed[at]] = scale
        groups[rowed[at]] = chain_rules.small_group_bands(blocks[rowed[at]], start, scale, floor)
    return out, groups


def _derived_of(derived: "dict[str, dict[str, object]]", source: str) -> "dict[str, object] | None":
    for label in derived:
        if derived[label]["source"] == source:
            return derived[label]
    return None


def _restriction(
    derived_entry: "dict[str, object] | None",
    cells: patient_rules.Cells,
    scales: "dict[str, chain_rules.Ladder]",
    child: chain_rules.Ladder,
    block: "dict[str, object]",
    level: int,
    grid: "patient_rules.Grid | None",
) -> "patient_rules.Restriction | None":
    """A derived column's restriction on its source, read on the description (4.6c.2 (c))."""
    if derived_entry is None:
        return None
    label = f"{derived_entry['name']}"
    place = patient_rules.member_place(cells, label)
    if place < 0:
        raise _broken("S31", label, "a derived column whose source is a row family's child is a member of the grain family")
    edges: "list[fractions.Fraction]" = []
    if derived_entry["kind"] == patient_rules.OWN_MEAN:
        written = derived_entry["edges"]
        read = [patient_rules.fraction_read(one) for one in written] if isinstance(written, list) else []
        if any(one is None for one in read):
            raise _broken("S32", label, "an own mean's edges are decimal numbers")
        exact = [one for one in read if one is not None]
        edges = patient_rules.own_mean_edges(scales[label], exact, cells.members[place][1])
    return patient_rules.restriction_for(f"{derived_entry['kind']}", place, child, block, level, grid, edges)


def _recheck_rows(
    grain: "dict[str, object]",
    blocks: "dict[str, dict[str, object]]",
    schema: "list[str]",
    classes: "dict[str, str]",
    census: patient_rules.Census,
    cells: patient_rules.Cells,
    scales: "dict[str, chain_rules.Ladder]",
    row_scales: "dict[str, chain_rules.Ladder]",
    derived: "dict[str, dict[str, object]]",
    floor: int,
    tabled: int,
    groups: "dict[str, set[int]]",
    row_groups: "dict[str, set[int]]",
) -> None:
    """S31 recomputed: every row family's parents, table, RULE W1 in rows and certificate, and every other column's one-cell certificate."""
    values = patient_rules.r_band_values(census)
    witness_at = patient_rules.threshold(census, floor) + 1
    counts: "dict[str, int]" = {}
    children: "set[str]" = set()
    written = grain["rows"]
    # R*'S TIE (4.6c.8 step 4): one `R*` for the description, read at the finest
    # row family's cut of the open top band; a family whose cut crosses another's is refused.
    everyone = [[cell for cell in range(len(cells.patients)) if cells.patients[cell]]]
    tie = patient_rules.top_blocks(cells, values, census.lo, everyone, [census.rows])
    if tie is None:
        raise _broken("S31", "grain.census", "the grain family's patients hold the census's rows")
    reads: "list[tuple[str, list[list[int]], list[int], int, bool, patient_rules.Restriction | None, tuple[int | None, bool]]]" = []
    for entry in written if isinstance(written, list) else []:
        child = f"{entry['child']}"
        if child in children:
            raise _broken("S31", child, "a column is the child of one row family at most")
        children = children | {child}
        ladder = row_scales[child]
        level = _level_of(entry["level"], "S31", child)
        chosen: "list[tuple[str, int]]" = []
        parents = entry["parents"]
        for parent in parents if isinstance(parents, list) else []:
            if not isinstance(parent, dict) or sorted(parent) != ["column", "level"]:
                raise _broken("S31", child, "each parent names a column and a level")
            name = f"{parent['column']}"
            place = patient_rules.member_place(cells, name)
            parent_level = _level_of(parent["level"], "S31", child)
            if place < 0 or parent_level < cells.members[place][1]:
                raise _broken("S31", child, "every parent is a member of the grain family at its level there or coarser")
            chosen += [(name, parent_level)]
        if not chosen or len(chosen) > chain_rules.K_MAX:
            raise _broken("S31", child, "a row family has one to k_max parents")
        maps = [chain_rules.coarsen(scales[name], cells.members[patient_rules.member_place(cells, name)][1], parent_level) for name, parent_level in chosen]
        sizes = [scales[name].counts[parent_level] for name, parent_level in chosen]
        parent_of, width = patient_rules.parent_cells(cells, tuple(chosen), maps, sizes)
        bands = ladder.counts[level]
        table = entry["table"]
        flat: "list[int]" = []
        if not isinstance(table, list) or len(table) != width:
            raise _broken("S31", child, "the table is complete: one row for each parent cell")
        for row in table:
            if not isinstance(row, list) or len(row) != bands:
                raise _broken("S31", child, "the table is complete: one column for each band of the child")
            flat += [int(cell) for cell in row]
        by_child = [0] * bands
        for index in range(len(flat)):
            by_child[index % bands] += flat[index]
        if by_child != chain_rules.totals_at(ladder, level):
            raise _broken("S31", child, "the table's sum over the parents is the child's L0 totals at its level")
        parents_read: "list[tuple[chain_rules.Ladder, int, frozenset[int] | set[int]]]" = [(scales[name], parent_level, groups[name] if name in groups else set()) for name, parent_level in chosen]
        if not patient_rules.w1_in_rows(ladder, level, row_groups[child] if child in row_groups else set(), parents_read, flat, bands, width):
            raise _broken("S31", child, "RULE W1 in rows: a band holding a small group of the child or of a parent reaches two bands of the other's coarsest level")
        inside: "list[list[int]]" = [[] for _cell in range(width)]
        for cell in range(len(cells.patients)):
            if cells.patients[cell]:
                inside[parent_of[cell]] += [cell]
        parent_rows = [sum(flat[at * bands : (at + 1) * bands]) for at in range(width)]
        block = blocks[child]
        grid = patient_rules.grid_of(block)
        one = _derived_of(derived, child)
        restriction = _restriction(one, cells, scales, ladder, block, level, grid)
        if one is not None and one["kind"] == patient_rules.FIRST_DATE and f"{one['name']}" not in [name for name, _level in chosen]:
            raise _broken("S31", child, "a first date's source takes the first date as a parent")
        fine = chain_moments.fine(block)
        read_by_key = patient_rules.key_read(block)
        spans = patient_rules.spans_two(ladder, block, level, grid)
        use_pwit = (fine and not read_by_key and one is None and spans) or (one is not None and one["kind"] == patient_rules.FIRST_DATE)
        own_blocks = patient_rules.top_blocks(cells, values, census.lo, inside, parent_rows)
        joined = patient_rules.blocks_joined(tie, own_blocks) if own_blocks is not None else None
        if joined is None:
            raise _broken("S31", child, "one R* meets every table holding the rows per patient: no family's top-band cells cross another's")
        tie = joined
        reads += [(child, inside, flat, bands, use_pwit, restriction, patient_rules.class_witness(read_by_key, spans, witness_at))]
    stars = patient_rules.r_star_of(cells, values, census.lo, tie, floor)
    if stars is None and census.top_patients:
        raise _broken("S31", "grain.census", "one R* meets every table holding the rows per patient")
    for child, inside, flat, bands, use_pwit, restriction, witness in reads:
        if not patient_rules.certificate(cells, values, inside, flat, bands, stars, use_pwit, restriction, witness[0], floor, counts, witness[1]):
            raise _broken("S31", child, "the row family's certificate holds on its published counts")
    for name in schema:
        if classes[name] not in (patient_rules.CLASS_REPEATED, patient_rules.CLASS_DEALT) or name in children:
            continue
        if _derived_of(derived, name) is not None:
            raise _broken("S31", name, "a column whose derived column stands is a row family's child or held")
        ladder = row_scales[name]
        block = blocks[name]
        grid = patient_rules.grid_of(block)
        read_by_key = patient_rules.key_read(block)
        supplies = list(ladder.totals)
        constant = census.top_patients == 0 and len([one for one in census.bands if one]) == 1
        spans = patient_rules.spans_two(ladder, block, 0, grid)
        if constant and not read_by_key and chain_moments.fine(block) and spans:
            if not patient_rules.pwit(census.patients, supplies, floor):
                raise _broken("S31", name, "the column's one-cell family's certificate holds")
            continue
        one_witness, witness_v = patient_rules.class_witness(read_by_key, spans, witness_at)
        if not patient_rules.certificate(cells, values, everyone, supplies, len(supplies), stars, False, None, one_witness, floor, counts, witness_v):
            raise _broken("S31", name, "the column's one-cell family's certificate holds")
    del tabled


def _recheck_trends(
    grain: "dict[str, object]",
    blocks: "dict[str, dict[str, object]]",
    families: "list[chain_rules.Family]",
    scales: "dict[str, chain_rules.Ladder]",
    row_scales: "dict[str, chain_rules.Ladder]",
    cells: patient_rules.Cells,
    census: patient_rules.Census,
    derived: "dict[str, dict[str, object]]",
    floor: int,
    tabled: int,
) -> None:
    """S33 recomputed: each trend's grid, the unpinned total's guard and SWING, on published facts."""
    trend = grain["trend"]
    grids = grain["grid"]
    rows = grain["rows"]
    by_child: "dict[str, dict[str, object]]" = {}
    for entry in rows if isinstance(rows, list) else []:
        by_child[f"{entry['child']}"] = entry
    gridded: "dict[str, dict[str, object]]" = {}
    for entry in grids if isinstance(grids, list) else []:
        gridded[f"{entry['column']}"] = entry
    for name in gridded:
        grid = patient_rules.grid_of(blocks[name]) if name in blocks else None
        if grid is None or gridded[name] != patient_rules.grid_written(grid):
            raise _broken("S33", name, "the grid's u, L and K agree with the column's block")
    values = patient_rules.r_band_values(census)
    derived_labels = set(derived)
    person = grain["person"]
    person_block = blocks[f"{person}"] if f"{person}" in blocks else {}
    for entry in trend if isinstance(trend, list) else []:
        if not isinstance(entry, dict):
            raise _broken("S33", "grain.trend", "each trend is an object")
        name = f"{entry['column']}"
        block = blocks[name] if name in blocks else {}
        grid = patient_rules.grid_of(block)
        if grid is None or name not in by_child:
            raise _broken("S33", name, "a trend stands on a gridded column that is a row family's child")
        if _get(block, "n_missing") != _get(person_block, "n_missing"):
            raise _broken("S33", name, "a trend's column holds a reading on every tabled row")
        family_entry = by_child[name]
        ladder = row_scales[name]
        level = _level_of(family_entry["level"], "S33", name)
        bands = ladder.counts[level]
        if bands != 2:
            raise _broken("S33", name, "a trend stands on a row family whose child has two bands")
        written_parents = family_entry["parents"]
        chosen = [
            (f"{parent['column']}", _level_of(parent["level"], "S33", name))
            for parent in (written_parents if isinstance(written_parents, list) else [])
            if isinstance(parent, dict)
        ]
        wanted = {member for member, _level in chosen if member not in derived_labels} | {patient_rules.R_NAME}
        f_s = None
        for family in families:
            if wanted <= {member for member, _level in chain_rules.members(family)}:
                f_s = family
                break
        if f_s is None:
            raise _broken("S33", name, "a trend's cell is a cell of the family F_S")
        members = chain_rules.members(f_s)
        sizes = chain_rules.radices(f_s, scales)
        labels = entry["cell"]
        if not isinstance(labels, list) or len(labels) != len(members):
            raise _broken("S33", name, "a trend's cell names every member of F_S")
        parts: "list[int]" = []
        rho = 0
        for place in range(len(members)):
            text = f"{labels[place]}"
            head = f"{members[place][0]}="
            read_number = patient_rules.number_after(text, head)
            if read_number is None:
                raise _broken("S33", name, "a trend's cell names every member of F_S")
            number = read_number
            if members[place][0] == patient_rules.R_NAME:
                rho = number
                found = [band for band in range(len(values)) if values[band] == (number, number)]
                if not found or number < 2:
                    raise _broken("S33", name, "a trend's cell holds one value of the rows per patient, two or more")
                number = found[0]
            parts += [number]
        index = 0
        for place in range(1, len(parts)):
            index = index * sizes[place] + parts[place]
        cell = index * sizes[0] + parts[0]
        held = f_s.table[cell] if 0 <= cell < len(f_s.table) else 0
        if held <= 0:
            raise _broken("S33", name, "a trend's cell holds patients")
        maps = []
        for member, member_level in members:
            place = patient_rules.member_place(cells, member)
            if place < 0:
                raise _broken("S33", name, "F_S's members are members of the grain family")
            maps += [(place, chain_rules.coarsen(scales[member], cells.members[place][1], member_level))]
        held_cells: "list[int]" = []
        for grain_cell in range(len(cells.patients)):
            grain_parts = chain_rules.cell_parts(grain_cell, list(cells.sizes))
            if cells.patients[grain_cell] and all(maps[k][1][grain_parts[maps[k][0]]] == parts[k] for k in range(len(members))):
                held_cells += [grain_cell]
        one = _derived_of(derived, name)
        place = patient_rules.member_place(cells, f"{one['name']}") if one is not None else -1
        edges: "list[fractions.Fraction]" = []
        if one is not None and one["kind"] == patient_rules.OWN_MEAN and place >= 0:
            restriction = _restriction(one, cells, scales, ladder, block, level, grid)
            edges = list(restriction.edges) if restriction is not None else []
        parent_maps = [chain_rules.coarsen(scales[member], cells.members[patient_rules.member_place(cells, member)][1], member_level) for member, member_level in chosen]
        parent_sizes = [scales[member].counts[member_level] for member, member_level in chosen]
        parent_of, parent_count = patient_rules.parent_cells(cells, tuple(chosen), parent_maps, parent_sizes)
        written_table = family_entry["table"]
        flat = [int(one_cell) for row in (written_table if isinstance(written_table, list) else []) for one_cell in row]
        if patient_rules.total_fixed(block) and patient_rules.free_rows(cells, values, parent_of, parent_count, flat, bands, patient_rules.one_code_rows(ladder, block, level, grid)) < floor:
            raise _broken("S33", name, "a trend stands only where the rows outside its cells keep their code total free")
        ranges = [patient_rules.code_range(grid, *patient_rules.band_edges(ladder, block, level, band)[:2]) for band in range(bands)]
        swing = patient_rules.swing_classes(cells, held_cells, held, rho, flat, bands, ranges, grid, edges, place, parent_of)
        q_value = entry["q"]
        if swing is None or not isinstance(q_value, int) or not patient_rules.swing_passes(q_value, rho, held, swing[0], swing[1], grid.codes, floor):
            raise _broken("S33", name, "SWING passes on the trend's published facts")


def _recheck_fixed_rows(
    grain: "dict[str, object]",
    families: "list[chain_rules.Family]",
    scales: "dict[str, chain_rules.Ladder]",
    census: patient_rules.Census,
    row_scales: "dict[str, chain_rules.Ladder]",
) -> None:
    """S30 recomputed: each row census is a function of the rest by either clause of 4.6c.5 (c), and equals it."""
    del row_scales
    values = patient_rules.r_band_values(census)
    rows = grain["rows"]
    for entry in grain["fixed_rows"] if isinstance(grain["fixed_rows"], list) else []:
        name = f"{entry['column']}"
        level = _level_of(entry["level"], "S30", name)
        found: "list[int] | None" = None
        for family in families:
            held = dict(chain_rules.members(family))
            if name not in held or patient_rules.R_NAME not in held or held[name] != level:
                continue
            sizes = chain_rules.radices(family, scales)
            members = [member for member, _level in chain_rules.members(family)]
            name_place = patient_rules.place_in(members, name)
            r_place = patient_rules.place_in(members, patient_rules.R_NAME)
            counted = [0] * scales[name].counts[level]
            top_bands: "set[int]" = set()
            for cell in range(len(family.table)):
                count = family.table[cell]
                if not count:
                    continue
                parts = chain_rules.cell_parts(cell, sizes)
                low, high = values[parts[r_place]]
                if high is None:
                    top_bands = top_bands | {parts[name_place]}
                    continue
                counted[parts[name_place]] += low * count
            if len(top_bands) <= 1:
                for band in top_bands:
                    counted[band] += census.top_rows
                found = counted
                break
        if found is None:
            for row_entry in rows if isinstance(rows, list) else []:
                written_parents = row_entry["parents"]
                parents = [
                    (f"{parent['column']}", _level_of(parent["level"], "S30", name))
                    for parent in (written_parents if isinstance(written_parents, list) else [])
                    if isinstance(parent, dict)
                ]
                if (name, level) not in parents:
                    continue
                place = [at for at in range(len(parents)) if parents[at] == (name, level)][0]
                sizes = [scales[member].counts[member_level] for member, member_level in parents]
                counted = [0] * scales[name].counts[level]
                written_table = row_entry["table"]
                for at, row in enumerate(written_table if isinstance(written_table, list) else []):
                    index = at
                    parts = [0] * len(sizes)
                    for k in range(len(sizes) - 1, -1, -1):
                        parts[k] = index % sizes[k]
                        index //= sizes[k]
                    counted[parts[place]] += sum(int(one) for one in row)
                found = counted
                break
        if found is None or found != entry["rows"]:
            raise _broken("S30", name, "a row census is published only where the rest of the description gives it, and equals it")
