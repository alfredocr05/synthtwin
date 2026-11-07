"""The patient layer's profile side: several rows per patient (contract 4.6c; lane GRa, plan P4-D449).

NOT IN FORCE. Invariant S12 stands until the landing that ships stage 6
whole: this module runs only where `chain.describe` is handed the chain's
switch on a table whose settings name a person column, which no shipped
command does. It has ONE call site, in `chain.describe`.

WHAT IT DOES, in contract 4.6c's order:

- THE GATE (4.6c.3): exactly one person column, no tabled row without a
  person value, at least `f` extra rows, and the census draw, whose "off"
  is eligible on every table; patients are the person column's merged
  keys (`parsing.merged_key`, the one rule the product counts people by),
  and the layer stays off where they are not the column's different
  values one for one;
- THE CENSUS OF `r` (4.6c.4): every candidate top edge, each eligible
  only with every band 0 or at least `f` patients and a floored split of
  its open top band found by the bounded deficit search; drawn among the
  eligible ones and "off";
- THE CLASSES (4.6c.5 to 4.6c.7): patient-fixed where at most `T`
  patients hold two different cells, position-like by the KEY test,
  dealt dates, repeated; the position column; a repeated column the KEY
  test reads, or any repeated or dealt date column, kept in rows only
  beside its certificate, else drawn HELD;
- THE PATIENT TABLE AND ITS CHAIN (4.6c's setting, 4.6c.8 (a)): the
  patient-fixed columns at each patient's first position described over
  the patient table by the product's own producer, `r` from the drawn
  census, the derived first-date and own-mean columns (4.6c.2), and
  section 4.6b's search run on it in patients, a family holding `r`
  offered only with every member of every earlier one;
- THE ROW FAMILIES (4.6c.8): each repeated or dealt date column drawn
  under the grain family's members or as the child of no row family,
  each kept beside the certificate the page assigns (PWIT, residual
  PWIT, the floored split on `R*`, with the class witness);
- CHANGE OVER VISITS (4.6c.1): `Q_P` behind SWING and the unpinned
  total's guard, drawn against "no moment";
- the position lists, the row census of a patient-fixed column, and the
  person column's and every other column's block as the layer reads them
  (4.6c.3 (b), (c); 4.6c.5 (b), (c); 4.6c.6 (c)).

WHAT IT DOES NOT DO: generate (lane GRb), moments (lanes MPOL2 and MPp),
or certify complete follow-up (January). Its departures from the page are
plan P4-D449's, each publishing less than the page allows.

ARITHMETIC. Counts are Python integers, grid quantities exact fractions,
scores exact fractions, and the draw's weights the stated exponential of
4.6b.4. No library float decides a published value.
"""

import dataclasses
import fractions

from synthtwin import chain
from synthtwin import chain_moments
from synthtwin import chain_rules
from synthtwin import parsing, profile, reading, taxonomy
from synthtwin import patient_rules

# The modules under the short names this module reads them by.
moments = chain_moments
rules = chain_rules
pr = patient_rules

# The reasons the layer is off although the switch is on, each told in the
# private notes only (4.6c.3 (e); inventory row 15a).
OFF_PERSONS = "the patient layer stands beside exactly one person column"
OFF_HELD = "an open question holds a column whose values repeat"
OFF_BLANK = "a tabled row holds no person value"
OFF_MERGED = "spellings of one person merge, so the patients are not the person column's different values"
OFF_EXTRA = "the extra rows number 1 to f - 1"
OFF_CENSUS = "no candidate census of rows per patient is eligible"
OFF_DRAWN = "the census draw took off"
OFF_RECOUNT = "a column's recount disagreed with its published counts"

# The rule of 4.6c.6 (b): a number column's witness readings at most this many.
POSITION_READINGS = 20
# The own mean's edges are kept to this many more decimal places than the
# column's grid step (departure (5) of P4-D449).
OWN_MEAN_PLACES = 3


def _get(mapping: object, key: str) -> object:
    if isinstance(mapping, dict) and key in mapping:
        return mapping[key]
    return None


def _whole(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


@dataclasses.dataclass(frozen=True)
class Layer:
    """What the patient layer adds to a switched description, or why it is off.

    `statistical` is the patient chain (4.6c.9: never None while the layer
    stands), `grain` the object 4.6c.9 writes, `columns` every column block
    as the layer publishes it. All three are None where the layer is off;
    `notes` then name why, in the private report only.
    """

    statistical: "dict[str, object] | None"
    grain: "dict[str, object] | None"
    columns: "list[dict[str, object]] | None"
    notes: "tuple[str, ...]"
    counts: "dict[str, int]"


def _off(note: str, notes: "list[str]", counts: "dict[str, int]") -> Layer:
    return Layer(None, None, None, tuple(notes + [f"the patient layer is off: {note}"]), counts)


@dataclasses.dataclass(frozen=True)
class _Patients:
    """The table's patients: each tabled row's patient, each patient's rows in position order."""

    tabled: "list[int]"
    of_row: "list[int]"
    rows: "list[list[int]]"
    r: "list[int]"


@dataclasses.dataclass
class _RowColumn:
    """A repeated or dealt date column read in rows: its ladder and its rows' codes at each level."""

    name: str
    place: int
    block: "dict[str, object]"
    ladder: rules.Ladder
    codes: "tuple[list[int], list[int], list[int]]"
    groups: "frozenset[int]"
    texts: "list[str]"
    readings: "list[fractions.Fraction | None]"
    fine: bool
    key_read: bool


# -- THE GATE AND THE PATIENTS (4.6c.3) -----------------------------------


def _tabled_rows(table: reading.Table, filled: bytearray, blank_rows: int) -> "list[int] | None":
    """The tabled rows: every row but the records holding nothing, as `chain.describe` reads them."""
    excluded = bytearray(table.n_rows)
    left = blank_rows
    for row in range(table.n_rows):
        if left and not filled[row]:
            excluded[row] = 1
            left -= 1
    if left:
        return None
    return [row for row in range(table.n_rows) if not excluded[row]]


def _patients_of(values: "list[str]", tabled: "list[int]") -> "tuple[list[str], list[int], list[list[int]]] | None":
    """Each tabled row's patient by its merged key, first-seen order; None where a row holds no person value."""
    index: "dict[str, int]" = {}
    of_row: "list[int]" = []
    rows: "list[list[int]]" = []
    for at in range(len(tabled)):
        text = values[tabled[at]]
        if chain.is_blank(text) or parsing.is_missing_text(text):
            return None
        key = parsing.merged_key(text)
        if key not in index:
            index[key] = len(rows)
            rows += [[]]
        patient = index[key]
        of_row += [patient]
        rows[patient] += [at]
    return list(index), of_row, rows


# -- THE CENSUS AND ITS DRAW (4.6c.4) -------------------------------------


def census_candidates(r_values: "list[int]", floor: int) -> "tuple[list[tuple[pr.Census, int]], int]":
    """Every ELIGIBLE candidate census, in order of `lo`, with its deficit search's steps; and the steps in all.

    At most 12 single values stand below the top band, as a column's `L0`
    holds at most 13 bands (departure (15) of contract 4.6c.12, a rule on
    the candidates alone): a finer census left no row family on the long
    tables this layer exists for.
    """
    counts: "dict[int, int]" = {}
    for one in r_values:
        counts[one] = counts[one] + 1 if one in counts else 1
    largest = max(r_values) if r_values else 0
    found: "list[tuple[pr.Census, int]]" = []
    spent = 0
    for lo in range(1, min(largest + 1, pr.CENSUS_TOP_EDGE_MAX) + 1):
        below = counts[lo - 1] if lo - 1 in counts else 0
        if lo >= 2 and 0 < below < floor:
            # Every later candidate publishes this band on its own: none is eligible.
            break
        census = pr.census_at(lo, counts)
        eligible, steps, _split = pr.census_eligible(census, floor)
        spent += steps
        if eligible:
            found += [(census, steps)]
    return found, spent


def _draw(switch: "chain.ChainSwitch", kind: str, index: object, columns: "list[str]", scores: "list[fractions.Fraction]") -> int:
    """One step of 4.6b.4's draw: the place drawn among the options' scores."""
    word = chain.step_word(switch.key, switch.name, kind, index, columns)
    return rules.choose(word, rules.weights_of(scores, rules.TAU))


# -- READING A COLUMN IN ROWS (the table layer's reader, on the tabled rows) --


def _declared(name: str, codes: "set[str]", measurements: "set[str]", commas: "set[str]") -> "dict[str, bool]":
    return {"code": name in codes, "measurement": name in measurements, "decimal_comma": name in commas}


def _ladder_in(read: "chain._Read", rows: "list[int]", name: str, floor: int) -> "tuple[rules.Ladder | None, list[int]]":
    """A column's ladder over `rows` (4.6b.2's merge), and each of those rows' `L0` band."""
    totals = [0] * len(read.start.names)
    for row in rows:
        totals[read.codes[row]] += 1
    ladder = rules.merge_ladder(name, read.start, totals, floor)
    if ladder is None:
        return None, []
    start_to_l0 = [0] * len(read.start.names)
    for at in range(len(ladder.l0)):
        for place in range(len(read.start.names)):
            if read.start.names[place] in ladder.l0[at]:
                start_to_l0[place] = at
    return ladder, [start_to_l0[read.codes[row]] for row in rows]


def _as_described(
    table: reading.Table,
    place: int,
    block: "dict[str, object]",
    settings: taxonomy.Settings,
    declared: "dict[str, bool]",
    seen: "dict[str, bool]",
    stored_as: str,
    blank_rows: int,
    read: "chain._Read",
) -> "tuple[chain._Read | None, list[str], dict[str, bool]]":
    """A column whose recount agreed, read again on its cells as its description read them (Codex's review of batch 4p, item 1, HIPAA).

    ``read`` is the column read as the file wrote it under the caller's
    ``declared``; ``seen`` the declarations the description read it under
    (`chain.declarations_read`: a comma it inferred among them). Where
    the description changed no cell of it (`chain.described_cells` hands
    the cells back as the file wrote them) under the same declarations,
    the reading comes back as given, byte for byte; otherwise the column
    is read again on the cells the description read -- the age top-code
    and its pool, the placeholders set aside, the dates held, the year
    top-code (`chain.read_as_described`) -- and that recount is the check
    again. Returns the reading, the cells and the declarations they were
    read under. A fixed function of its arguments; no I/O.
    """
    values = reading.column_values(table, place)
    cells = chain.described_cells(table, place, block, settings, seen, stored_as)
    if seen == declared and (cells is values or cells == values):
        return read, values, declared
    again, cells = chain.read_as_described(table, place, block, settings, seen, stored_as, blank_rows)
    return again, cells, seen


def _eligible_ladder(ladder: "rules.Ladder | None", role: object) -> "str | None":
    """4.6b.1's `one_band` and `constant` read on a ladder, as `chain.describe` reads them."""
    if ladder is None:
        return "one_band"
    if role == rules.ROLE_CONSTANT and rules.MISSING not in {one for band in ladder.l0 for one in band}:
        return "constant"
    if len([total for total in rules.totals_at(ladder, 2) if total > 0]) < 2:
        return "one_band"
    return None


def _reading(role: str, value: object, block: "dict[str, object]") -> "fractions.Fraction | None":
    """A cell's reading as an exact number in the column's own order (`pr.reading_of`)."""
    return pr.reading_of(role, value, block)


# -- THE CLASSES (4.6c.5, 4.6c.6) -----------------------------------------


def _threshold(census: pr.Census, floor: int) -> "tuple[int, int | None]":
    """`T = max(f - 1, floor(N2 / 100))` where the census publishes `N2`, else `f - 1` (4.6c.5 (a)); and `N2`."""
    if census.lo >= 2:
        two_or_more = census.patients - census.bands[0]
        return max(floor - 1, two_or_more // 100), two_or_more
    return floor - 1, None


def _two_cells(texts: "list[str]", patients: _Patients) -> int:
    """`V_K`: the patients holding two different cells (two present values, or a present one and an absent one)."""
    held = 0
    for rows in patients.rows:
        if len(rows) < 2:
            continue
        first = _cell(texts[rows[0]])
        for row in rows[1:]:
            if _cell(texts[row]) != first:
                held += 1
                break
    return held


def _cell(text: str) -> str:
    """A cell as the class test compares it: every blank or absent spelling one absent cell."""
    if chain.is_blank(text) or parsing.is_missing_text(text):
        return ""
    return text


def _level_twice(levels: "list[object]", patients: _Patients) -> int:
    """`V`: the patients of two or more rows holding some level of the column on two of their rows."""
    held = 0
    for rows in patients.rows:
        if len(rows) < 2:
            continue
        seen: "set[object]" = set()
        for row in rows:
            level = levels[row]
            if level in seen:
                held += 1
                break
            seen |= {level}
    return held


def _not_a_run(readings: "list[fractions.Fraction | None]", patients: _Patients) -> int:
    """`V` of a FINE number column (departure (16)): the patients of two or more present readings not reading as a run.

    A patient's readings read as a run where its `d` DIFFERENT readings,
    read as their ranks among the column's different readings, span at
    most `d` ranks with a quarter more and one for gaps, and at most a
    quarter of its readings (one where it holds three) repeat another of
    them: a visit number from any start, a week counted in fours, a
    sequence with a visit missed or a visit written twice (a row written
    twice is no broken run: the verify of repair 1, item 2, where a few
    such patients turned a visit number `repeated` and its block named
    the largest `r`). A repeated measurement fails: its readings share
    more or stray over its ranks.
    """
    ranks: "dict[fractions.Fraction, int]" = {}
    for one in sorted({value for value in readings if value is not None}):
        ranks[one] = len(ranks)
    broken = 0
    for rows in patients.rows:
        held = [ranks[value] for value in (readings[k] for k in rows) if value is not None]
        if len(held) < 2:
            continue
        different = len(set(held))
        repeats = len(held) - different
        allowed = max(1, len(held) // 4) if len(held) >= 3 else 0
        if repeats > allowed or max(held) - min(held) + 1 > different + different // 4 + 1:
            broken += 1
    return broken


def _run_list(listed: "list[object]") -> bool:
    """Whether a FINE run's position list stands: every entry a number, strictly rising or strictly falling."""
    numbers: "list[fractions.Fraction]" = []
    for one in listed:
        found = pr.fraction_read(one)
        if found is None:
            return False
        numbers += [found]
    steps = [numbers[at + 1] - numbers[at] for at in range(len(numbers) - 1)]
    return bool(numbers) and (all(step > 0 for step in steps) or all(step < 0 for step in steps))


def _first_positions(patients: _Patients) -> "list[int]":
    """Each patient's first row (its position 1), as an index into the tabled rows."""
    return [rows[0] for rows in patients.rows]


def _codes_three(ladder: rules.Ladder, first: "list[int]") -> "tuple[list[int], list[int], list[int]]":
    return first, [ladder.maps[1][code] for code in first], [ladder.maps[2][code] for code in first]


def _column(name: str, ladder: rules.Ladder, first: "list[int]", groups: "frozenset[int]", blank: int) -> "chain.Column":
    codes = _codes_three(ladder, first)
    return chain.Column(name, ladder, (chain.codes_at(codes[0]), chain.codes_at(codes[1]), chain.codes_at(codes[2])), groups, b"", 1, False, blank, None)


# -- THE PATIENT CHAIN (4.6b in patients, 4.6c.8 (a)) ---------------------


def _holds(family: rules.Family, name: str) -> bool:
    return any(member == name for member, _level in rules.members(family))


def _keyed(names: "set[str]", parents: int, derived: "set[str]") -> bool:
    """A KEYED family: one with parents holding `r` or a derived column (departure (3) of P4-D449)."""
    return parents > 0 and (pr.R_NAME in names or bool(names & derived))


def _keeps_keyed_rule(placed: "list[rules.Family]", option: "chain.Option", derived: "set[str]", r_eligible: bool, scales: "dict[str, rules.Ladder]") -> bool:
    """The rule on a keyed family's options (4.6c.8 (a), widened by departure (3) of P4-D449).

    A keyed family is offered only with every member of every earlier
    keyed family, each at its level there or finer; and, where `r` is
    eligible, a family with parents holding a derived column holds `r`.
    So the grain family `G`, the latest keyed family, holds `r` and every
    derived column placed with parents. A rule on the offered options,
    read on the placed chain (class (b)). Before any derived column is
    drawn, a keyed family whose parents hold `r` takes its child at `L2`,
    so the family a derived column must then hold stays within the floor
    (departure (3) as amended; the statistics skeptic's item 3: the own
    mean, the correlation's route, was otherwise lost on most long runs).
    """
    held = dict(zip((option.child,) + option.parents, option.levels))
    names = set(held)
    if not _keyed(names, len(option.parents), derived):
        return True
    if r_eligible and names & derived and pr.R_NAME not in names:
        return False
    if not derived and pr.R_NAME in option.parents and scales[option.child].counts[option.levels[0]] != scales[option.child].counts[2]:
        return False
    for family in placed:
        if not _keyed({member for member, _level in rules.members(family)}, len(family.parents), derived):
            continue
        for member, level in rules.members(family):
            if member not in held or held[member] > level:
                return False
    return True


def _keeps_r_star(option: "chain.Option", scales: "dict[str, rules.Ladder]", census: pr.Census, floor: int, derived: "set[str]") -> bool:
    """Whether a keyed family's cells leave `R*` a world (4.6c.8 step 4; departure (2) of P4-D449): no keyed family that leaves none is offered.

    The open top band's patients stand in this family's cells, and its
    excess must be shared among those cells with a floored split in each
    (`pr.top_rows_shared`). A family with none certifies no row of any
    column under it, so every column would be held for it: such a family
    is not offered, its parents and "no family" staying eligible. An
    eligibility rule on the option's own table and the census, as the
    floor's rule on that table is (class (a), the column's other options
    and "no family" stand on every table).
    """
    names = (option.child,) + option.parents
    if not census.top_patients or not _keyed(set(names), len(option.parents), derived):
        return True
    sizes = [scales[name].counts[level] for name, level in zip(names, option.levels)]
    place = pr.place_in(names, pr.R_NAME)
    top_band = len(pr.r_band_values(census)) - 1
    cells: "list[int]" = []
    for cell in range(len(option.table)):
        if option.table[cell] and (place < 0 or rules.cell_parts(cell, sizes)[place] == top_band):
            cells += [option.table[cell]]
    return pr.top_rows_shared(cells, census.lo, census.excess, floor) is not None


def _patient_chain(search: "chain._Search", switch: "chain.ChainSwitch", derived: "set[str]", census: pr.Census) -> "tuple[list[rules.Family], list[str]]":
    """Section 4.6b's search on the patient table, each step drawn, with the keyed families' rule.

    The table layer's own steps (`chain.root_options`, `_step_options`,
    `_draw`), each step's options filtered by `_keeps_keyed_rule` and
    `_keeps_r_star` before the draw. RULE WE is not read: the patient table
    holds no record holding nothing, every patient having a person value.
    """
    notes: "list[str]" = []
    r_eligible = pr.R_NAME in search.scales
    roots = [
        option for option in chain.root_options(search, None, 0)
        if _keeps_keyed_rule([], option, derived, r_eligible, search.scales) and _keeps_r_star(option, search.scales, census, search.floor, derived)
    ]
    search.counts["eligible_options"] += len(roots)
    pick = chain.draw_step(search, switch, 0, roots)
    if pick == 0:
        notes += [f"the patient chain's root step drew no family among {len(roots)} eligible options"]
        return [], notes
    root = roots[pick]
    parent = root.parents[0]
    placed: "list[rules.Family]" = [
        rules.Family(parent, root.levels[1], (), None, tuple(rules.totals_at(search.scales[parent], root.levels[1]))),
        rules.Family(root.child, root.levels[0], ((parent, root.levels[1]),), 0, root.table),
    ]
    margins: "dict[tuple[int, tuple[str, ...]], rules.ParentCells]" = {}
    index = 1
    while len(placed) < len(search.eligible):
        need = any(search.columns[name].groups for name in search.eligible if name not in {family.child for family in placed})
        clamps = chain.clamps_of(search, placed, need)
        options = [
            option for option in chain.step_options(search, placed, clamps, margins)
            if _keeps_keyed_rule(placed, option, derived, r_eligible, search.scales) and _keeps_r_star(option, search.scales, census, search.floor, derived)
        ]
        search.counts["eligible_options"] += len(options)
        pick = chain.draw_step(search, switch, index, options)
        placed += [chain.family_of(options[pick])]
        index += 1
    notes += [f"the patient chain placed {len([family for family in placed if family.parents])} families with parents"]
    return placed, notes


def _rules_only(search: "chain._Search") -> "list[rules.Family]":
    """The RULES-ONLY shape in patients: every eligible column a family with no parent at `L0` (4.6c.8 (a))."""
    return [rules.Family(name, 0, (), None, tuple(rules.totals_at(search.scales[name], 0))) for name in search.eligible]


def _cell_of(family: rules.Family, codes_of: "dict[str, tuple[list[int], list[int], list[int]]]", scales: "dict[str, rules.Ladder]", patient: int) -> int:
    """A patient's place in a family's table: its parents' joint cell (the last fastest), then its child's band."""
    cell = 0
    for name, level in family.parents:
        cell = cell * scales[name].counts[level] + codes_of[name][level][patient]
    return cell * scales[family.child].counts[family.level] + codes_of[family.child][family.level][patient]


# -- THE GRAIN FAMILY (4.6c.8 (a)) ----------------------------------------


@dataclasses.dataclass(frozen=True)
class _Grain(pr.Cells):
    """The grain family's cells (`pr.Cells`), with `G`'s place in the chain and each patient's cell."""

    index: "int | None"
    of_patient: "list[int]"


def _grain_of(
    placed: "list[rules.Family]",
    scales: "dict[str, rules.Ladder]",
    codes_of: "dict[str, tuple[list[int], list[int], list[int]]]",
    census: pr.Census,
    r_codes: "list[int]",
    patient_count: int,
    derived: "set[str]",
) -> _Grain:
    """The grain family `G`: the latest keyed family (departure (3)), or `r`'s census itself (`grain_family` null).

    Where `r` is eligible `G` holds it; where it is not (one census band)
    every cell of `G` holds that one band.
    """
    index: "int | None" = None
    for at in range(len(placed)):
        if _keyed({member for member, _level in rules.members(placed[at])}, len(placed[at].parents), derived):
            index = at
    if index is None:
        bands = len(pr.r_band_values(census))
        counted = [0] * bands
        for code in r_codes:
            counted[code] += 1
        members = ((pr.R_NAME, 0),) if pr.R_NAME in scales else ()
        return _Grain(members, (bands,), tuple(counted), tuple(range(bands)), None, list(r_codes))
    family = placed[index]
    held = rules.members(family)
    sizes = tuple(rules.radices(family, scales))
    of_patient = [_cell_of(family, codes_of, scales, patient) for patient in range(patient_count)]
    cells = [0] * len(family.table)
    r_band = [0] * len(family.table)
    names = [name for name, _level in held]
    if pr.R_NAME in names:
        r_place = pr.place_in(names, pr.R_NAME)
        for cell in range(len(family.table)):
            r_band[cell] = rules.cell_parts(cell, list(sizes))[r_place]
    for patient in range(patient_count):
        cells[of_patient[patient]] += 1
    return _Grain(tuple(held), sizes, tuple(cells), tuple(r_band), index, of_patient)


# -- THE ROW FAMILIES' CERTIFICATES (4.6c.8 (a)) --------------------------


@dataclasses.dataclass
class _Ctx:
    """What every row family, one-cell family and trend reads."""

    switch: "chain.ChainSwitch"
    floor: int
    census: pr.Census
    values_r: "list[tuple[int, int | None]]"
    patients: _Patients
    scales: "dict[str, rules.Ladder]"
    codes_of: "dict[str, tuple[list[int], list[int], list[int]]]"
    groups: "dict[str, frozenset[int]]"
    counts: "dict[str, int]"
    threshold: int
    tabled: int
    # R*'S TIE (4.6c.8 step 4; the first skeptic's item 3): one `R*` for the
    # whole description, read at the finest row family's top-band blocks,
    # and every family's certificate as it reads again under a finer one.
    tie: "dict[frozenset[int], int]"
    stars: "list[tuple[tuple[int, int], ...]] | None"
    certified: "list[tuple[list[list[int]], list[int], int, bool, pr.Restriction | None, tuple[int | None, bool]]]"


@dataclasses.dataclass(frozen=True)
class _Derived:
    """A derived column of the patient table: its label, kind, source, the source's level, and its patients' bands."""

    label: str
    kind: str
    source: str
    level: int
    codes: "list[int]"
    edges: "list[fractions.Fraction]"


def _parent_cells(ctx: _Ctx, grain: _Grain, chosen: "tuple[tuple[str, int], ...]") -> "tuple[list[int], int]":
    """Each grain cell's parent cell under parents `chosen` (members of `G` at their level there or coarser)."""
    maps = [rules.coarsen(ctx.scales[name], grain.members[pr.member_place(grain, name)][1], level) for name, level in chosen]
    sizes = [ctx.scales[name].counts[level] for name, level in chosen]
    return pr.parent_cells(grain, chosen, maps, sizes)


def _certificate(ctx: _Ctx, grain: _Grain, members: "list[list[int]]", table: "list[int]", bands: int, stars: "list[tuple[tuple[int, int], ...]] | None", use_pwit: bool, restriction: "pr.Restriction | None", witness: "tuple[int | None, bool]") -> bool:
    return pr.certificate(grain, ctx.values_r, members, table, bands, stars, use_pwit, restriction, witness[0], ctx.floor, ctx.counts, witness[1])


def _w1_rows(ctx: _Ctx, row: _RowColumn, level: int, table: "list[int]", bands: int, chosen: "tuple[tuple[str, int], ...]", width: int) -> bool:
    """RULE W1 read in rows for a row family (4.6c.8 (d)): `pr.w1_in_rows`, the one rule the loader reads too."""
    parents: "list[tuple[rules.Ladder, int, frozenset[int] | set[int]]]" = [(ctx.scales[name], member_level, ctx.groups[name] if name in ctx.groups else frozenset()) for name, member_level in chosen]
    return pr.w1_in_rows(row.ladder, level, row.groups, parents, table, bands, width)


def _parent_options(ctx: _Ctx, grain: _Grain, derived: "_Derived | None") -> "list[tuple[tuple[str, int], ...]]":
    """A row family's parent options (4.6c.8 (a), 4.6c.2 (e)): members of `G`, each at its level there or coarser.

    At most `k_max` parents, every one a member of `G`; a first date's
    source takes the first date at its own level. In a fixed order: more
    parents first, then finer levels first.
    """
    members = list(grain.members)
    out: "list[tuple[tuple[str, int], ...]]" = []
    subsets: "list[list[tuple[str, int]]]" = [[]]
    for member in members:
        subsets += [one + [member] for one in subsets if len(one) < rules.K_MAX]
    for subset in subsets:
        if not subset:
            continue
        if derived is not None and derived.kind == pr.FIRST_DATE and derived.label not in [name for name, _level in subset]:
            continue
        choices: "list[list[tuple[str, int]]]" = [[]]
        for name, level in subset:
            fixed = derived is not None and derived.kind == pr.FIRST_DATE and name == derived.label
            reach = [level] if fixed or name == pr.R_NAME else list(range(level, 3))
            choices = [one + [(name, step)] for one in choices for step in reach]
        for choice in choices:
            out += [tuple(choice)]
    ranked = sorted((-len(out[at]), [level for _name, level in out[at]], at) for at in range(len(out)))
    return [out[entry[2]] for entry in ranked]


def _restriction_of(ctx: _Ctx, grain: _Grain, row: _RowColumn, level: int, derived: "_Derived | None", grid: "pr.Grid | None") -> "pr.Restriction | None":
    """What `row`'s derived column asks of its patterns at `level`, its own mean's edges read at its level in `G`."""
    if derived is None:
        return None
    place = pr.member_place(grain, derived.label)
    edges: "list[fractions.Fraction]" = []
    if derived.kind == pr.OWN_MEAN:
        edges = pr.own_mean_edges(ctx.scales[derived.label], derived.edges, grain.members[place][1])
    return pr.restriction_for(derived.kind, place, row.ladder, row.block, level, grid, edges)


# The most options of one row family that are read, in their fixed order: a
# function of the published grain family alone, so no option's reach depends
# on another option's table (breadth given up, named in the counts).
OPTIONS_READ_MAX = 64


def _row_family(ctx: _Ctx, grain: _Grain, row: _RowColumn, index: int, derived: "_Derived | None", grid: "pr.Grid | None") -> "tuple[int, list[int], int, tuple[tuple[str, int], ...]] | None":
    """A repeated or dealt date column's row family, drawn among its eligible options and "no family" (4.6c.8 (a)).

    The parents are members of the grain family `G` at their level there
    or coarser (`_parent_options`); a column whose derived column is not
    a member of `G` has no option. The child stands at its `L0`, `L1` and
    `L2` (a column the KEY test reads at `L0`, for its class witness; an
    own mean's source at the median, 4.6c.2 (e); a first date's source
    at the first date's level). An option is eligible where its table
    holds 0 or at least `f` rows in every cell, RULE W1 holds in rows, its
    top-band cells are those of every family already placed or coarser or
    finer than them all (R*'s tie), and its certificate and every placed
    family's hold under the one `R*` that then stands. At most
    `OPTIONS_READ_MAX` options are read, in their fixed order. Returns the
    child's level, the table, its band count and the parents, or None for
    "no family".
    """
    if not grain.members:
        return None
    if derived is not None and pr.member_place(grain, derived.label) < 0:
        return None
    levels = [0, 1, 2]
    if row.key_read:
        levels = [0]
    if derived is not None:
        levels = [2] if derived.kind == pr.OWN_MEAN else [derived.level]
    options: "list[tuple[int, list[int], int, tuple[tuple[str, int], ...]]]" = []
    kept: "list[tuple[dict[frozenset[int], int], list[tuple[tuple[int, int], ...]] | None, tuple[list[list[int]], list[int], int, bool, pr.Restriction | None, tuple[int | None, bool]]]]" = []
    scores: "list[fractions.Fraction]" = [fractions.Fraction(0)]
    read = 0
    for chosen in _parent_options(ctx, grain, derived):
        parent_of, width = _parent_cells(ctx, grain, chosen)
        members: "list[list[int]]" = [[] for _cell in range(width)]
        for cell in range(len(grain.patients)):
            if grain.patients[cell]:
                members[parent_of[cell]] += [cell]
        for level in levels:
            read += 1
            if read > OPTIONS_READ_MAX:
                ctx.counts["options_left_unread"] += 1
                continue
            bands = row.ladder.counts[level]
            table = [0] * (width * bands)
            codes = row.codes[level]
            for k in range(len(ctx.patients.tabled)):
                table[parent_of[grain.of_patient[ctx.patients.of_row[k]]] * bands + codes[k]] += 1
            ctx.counts["tables_counted"] += 1
            if any(0 < one < ctx.floor for one in table):
                ctx.counts["floor_refusals"] += 1
                continue
            if not _w1_rows(ctx, row, level, table, bands, chosen, width):
                ctx.counts["w1_refusals"] += 1
                continue
            restriction = _restriction_of(ctx, grain, row, level, derived, grid)
            if restriction is not None and restriction.kind == pr.OWN_MEAN and (bands != 2 or grid is None):
                continue
            parent_rows = [sum(table[at * bands : (at + 1) * bands]) for at in range(width)]
            own_blocks = pr.top_blocks(grain, ctx.values_r, ctx.census.lo, members, parent_rows)
            joined = pr.blocks_joined(ctx.tie, own_blocks) if own_blocks is not None else None
            if joined is None:
                ctx.counts["tie_refusals"] += 1
                continue
            stars = pr.r_star_of(grain, ctx.values_r, ctx.census.lo, joined, ctx.floor)
            if stars is None and ctx.census.top_patients:
                ctx.counts["tie_refusals"] += 1
                continue
            spans = pr.spans_two(row.ladder, row.block, level, grid)
            use_pwit = (row.fine and not row.key_read and derived is None and spans) or (derived is not None and derived.kind == pr.FIRST_DATE)
            witness = pr.class_witness(row.key_read, spans, ctx.threshold + 1)
            if not _certificate(ctx, grain, members, table, bands, stars, use_pwit, restriction, witness):
                continue
            if joined != ctx.tie and not all(_certificate(ctx, grain, one[0], one[1], one[2], stars, one[3], one[4], one[5]) for one in ctx.certified):
                ctx.counts["tie_refusals"] += 1
                continue
            options += [(level, table, bands, chosen)]
            kept += [(joined, stars, (members, table, bands, use_pwit, restriction, witness))]
            scores += [rules.score(table, width, bands)]
    if not options:
        return None
    pick = _draw(ctx.switch, "row", index, [row.name], scores)
    if pick == 0:
        return None
    ctx.tie, ctx.stars, entry = kept[pick - 1]
    ctx.certified += [entry]
    return options[pick - 1]


def _one_cell(ctx: _Ctx, grain: _Grain, row: _RowColumn, grid: "pr.Grid | None") -> bool:
    """A column that is no row family's child: its one-cell family's certificate (4.6c.8 (a); S31).

    The one parent cell is the whole table, its table the column's `L0`
    totals in rows. PWIT where every patient holds one value of `r`; the
    floored split on the description's one `R*` otherwise; a column the
    KEY test reads takes the class witness. Read after every row family is
    placed, so it reads the `R*` that finally stands.
    """
    supplies = list(row.ladder.totals)
    spans = pr.spans_two(row.ladder, row.block, 0, grid)
    witness = pr.class_witness(row.key_read, spans, ctx.threshold + 1)
    census = ctx.census
    constant = census.top_patients == 0 and len([one for one in census.bands if one]) == 1
    if constant and not row.key_read and row.fine and spans:
        return pr.pwit(census.patients, supplies, ctx.floor)
    everyone = [[cell for cell in range(len(grain.patients)) if grain.patients[cell]]]
    return _certificate(ctx, grain, everyone, supplies, len(supplies), ctx.stars, False, None, witness)


# -- CHANGE OVER VISITS (4.6c.1) -------------------------------------------


def _trends(ctx: _Ctx, grain: _Grain, placed: "list[rules.Family]", row: _RowColumn, grid: pr.Grid, row_table: "tuple[int, list[int], int, tuple[tuple[str, int], ...]]", derived: "_Derived | None", derived_labels: "set[str]") -> "list[dict[str, object]]":
    """Change over visits for one FINE column (4.6c.1): each cell's `Q_P` drawn against "no moment" where SWING passes.

    `F_S` is the first family in chain order holding `r` and every
    member of `G` that parents the column's row family and is not
    derived (departure (2): `r` stands at its census bands in every
    family, so the finest level is every such family's). Its cells of
    one `r >= 2` are offered; the unpinned total's guard (4.6c.1 (b) 6)
    refuses every one where the column's exact mean and tails fix its
    code total and no world holds `f` rows outside them in bands of two or
    more codes (`pr.free_rows`).
    """
    if any(value is None for value in row.readings):
        return []
    level, table, bands, chosen = row_table
    if bands != 2 or pr.R_NAME not in {name for name, _level in grain.members}:
        return []
    wanted = {member for member, _level in chosen if member not in derived_labels} | {pr.R_NAME}
    parent_of, width_of_parents = _parent_cells(ctx, grain, chosen)
    f_s: "rules.Family | None" = None
    for family in placed:
        if wanted <= {member for member, _level in rules.members(family)}:
            f_s = family
            break
    if f_s is None:
        return []
    members = rules.members(f_s)
    sizes = rules.radices(f_s, ctx.scales)
    r_place = pr.place_in([member for member, _level in members], pr.R_NAME)
    by_cell = pr.grouped([_cell_of(f_s, ctx.codes_of, ctx.scales, patient) for patient in range(len(ctx.patients.rows))])
    one_r: "list[tuple[int, int]]" = []
    for cell in sorted(by_cell):
        low, high = ctx.values_r[rules.cell_parts(cell, sizes)[r_place]]
        if high is not None and low >= 2:
            one_r += [(cell, low)]
    if not one_r:
        return []
    free = pr.free_rows(grain, ctx.values_r, parent_of, width_of_parents, table, bands, pr.one_code_rows(row.ladder, row.block, level, grid))
    if pr.total_fixed(row.block) and free < ctx.floor:
        ctx.counts["trend_refused_total"] += len(one_r)
        return []
    ranges = [pr.code_range(grid, *pr.band_edges(row.ladder, row.block, level, band)[:2]) for band in range(bands)]
    place = pr.member_place(grain, derived.label) if derived is not None else -1
    edges: "list[fractions.Fraction]" = []
    if derived is not None and derived.kind == pr.OWN_MEAN and place >= 0:
        found = _restriction_of(ctx, grain, row, level, derived, grid)
        edges = list(found.edges) if found is not None else []
    out: "list[dict[str, object]]" = []
    for at in range(len(one_r)):
        cell, rho = one_r[at]
        held = by_cell[cell]
        ctx.counts["trend_cells"] += 1
        total = 0
        for patient in held:
            positions = ctx.patients.rows[patient]
            for j in range(rho):
                reading = row.readings[positions[j]]
                total += pr.grid_code(grid, reading if reading is not None else grid.low) * (2 * (j + 1) - rho - 1)
        q_value = total // 2
        swing = pr.swing_classes(grain, sorted({grain.of_patient[patient] for patient in held}), len(held), rho, table, bands, ranges, grid, list(edges), place, parent_of)
        if swing is None or not pr.swing_passes(q_value, rho, len(held), swing[0], swing[1], grid.codes, ctx.floor):
            ctx.counts["trend_refused_swing"] += 1
            continue
        labels = [f"{members[k][0]}={rho if members[k][0] == pr.R_NAME else part}" for k, part in enumerate(rules.cell_parts(cell, sizes))]
        pick = _draw(ctx.switch, "trend", at, [row.name] + labels, [fractions.Fraction(0), fractions.Fraction(len(held))])
        if pick == 0:
            continue
        out += [{"cell": labels, "column": row.name, "q": q_value}]
        ctx.counts["trend_published"] += 1
    return out


def _fixed_rows(ctx: _Ctx, name: str, placed: "list[rules.Family]", parents_of: "dict[str, tuple[tuple[str, int], ...]]") -> "dict[str, object] | None":
    """A patient-fixed column's row census where it is a function of the description without it (4.6c.5 (c)).

    Clause 1: a family of the patient chain holds the column and `r` (at
    the census's bands, departure (2)) and the top band's patients lie in
    one of the column's bands there. Clause 2: a row family has the
    column as a parent. Either way the census is read on the patient
    table: the sum of `r` over the patients in each band of the column
    at that level.
    """
    level: "int | None" = None
    codes = ctx.codes_of[name]
    r_codes = ctx.codes_of[pr.R_NAME][0] if pr.R_NAME in ctx.codes_of else None
    for family in placed:
        held = dict(rules.members(family))
        if name not in held or pr.R_NAME not in held or r_codes is None:
            continue
        if ctx.census.top_patients == 0:
            level = held[name]
            break
        top = len(ctx.values_r) - 1
        bands = {codes[held[name]][patient] for patient in range(len(ctx.patients.r)) if r_codes[patient] == top}
        if len(bands) == 1:
            level = held[name]
            break
    if level is None:
        for child in parents_of:
            held = dict(parents_of[child])
            if name in held:
                level = held[name]
                break
    if level is None:
        return None
    rows = [0] * ctx.scales[name].counts[level]
    for patient in range(len(ctx.patients.r)):
        rows[codes[level][patient]] += ctx.patients.r[patient]
    return {"column": name, "level": rules.LEVELS[level], "rows": rows}


def _position_list(texts: "list[str]", patients: _Patients, length: int, floor: int) -> "list[object]":
    """A position-like column's modal values at positions 1 to `L` (4.6c.6 (c)), `null` by count, tie or repeated level."""
    out: "list[object]" = []
    used: "set[str]" = set()
    for position in range(length):
        held: "dict[str, int]" = {}
        for rows in patients.rows:
            if position < len(rows):
                text = _cell(texts[rows[position]])
                held[text] = held[text] + 1 if text in held else 1
        if not held:
            out += [None]
            continue
        ranked = sorted((-held[text], text) for text in held)
        top_count = -ranked[0][0]
        tied = len(ranked) > 1 and -ranked[1][0] == top_count
        value = ranked[0][1]
        if top_count < floor or tied or value in used or value == "":
            out += [None]
            continue
        used |= {value}
        out += [value]
    return out


def _one_each(found: object, present: object) -> bool:
    """Whether a multiplicity map is `{1: n_present}`."""
    if not isinstance(found, dict) or len(found) != 1:
        return False
    for key in found:
        return isinstance(key, str) and pr.number_after(key, "") == 1 and found[key] == present
    return False


def _emptied(block: "dict[str, object]") -> "dict[str, object]":
    """A block publishing no key but its name, place and role (S30): every other key null, or `[]` where it was a list."""
    out: "dict[str, object]" = {}
    for key in block:
        value = block[key]
        if key in pr.EMPTIED_KEPT:
            out[key] = value
        elif isinstance(value, list):
            out[key] = []
        else:
            out[key] = None
    return out


# The person column's keys that stay its own in rows (4.6c.3 (b)): its
# presence and absence. Every other key reads the patients, its forms, their
# prefixes and exclusions and its lengths alike (the first skeptic's item 6).
PERSON_KEPT_IN_ROWS = (
    "name", "position", "n_present", "n_missing", "missing_by_class", "missing_by_source",
    "n_missing_blank", "n_missing_withheld",
)
# The person column's counts of its patients by form or alphabet, read over the
# patient table: each stands only at 0 or at least the floor (`_person_counts_floored`).
PERSON_COUNTED_FORMS = ("n_all_digits", "n_code_alphabet")


def _person_counts_floored(block: "dict[str, object]", floor: int) -> "dict[str, object]":
    """The person block's forms with no pool of 1 to `f - 1` patients (the first skeptic's item 6, HIPAA).

    A pool of forms too small to name stands on 1 to `f - 1` patients only
    where the named forms leave it there: the smallest named form joins it
    until it reaches the floor, a form and its prefix and exclusions going
    unnamed together. Publishes no more than the block; a fixed function
    of it.
    """
    forms = _get(block, "layout_forms")
    if not isinstance(forms, dict) or taxonomy.SUPPRESSED_LABEL not in forms:
        return block
    pooled = forms[taxonomy.SUPPRESSED_LABEL]
    named = {key: forms[key] for key in forms if key != taxonomy.SUPPRESSED_LABEL}
    if not isinstance(pooled, int) or pooled >= floor:
        return block
    while pooled < floor and named:
        smallest = min((named[key], key) for key in named)[1]
        pooled += named[smallest]
        del named[smallest]
    out = dict(block)
    named[taxonomy.SUPPRESSED_LABEL] = pooled
    out["layout_forms"] = {key: named[key] for key in sorted(named)}
    for key in ("layout_prefixes", "layout_exclusions"):
        found = _get(block, key)
        if isinstance(found, dict):
            out[key] = {scope: found[scope] for scope in found if scope in named}
    return out


def _blocks_as_published(
    blocks: "list[dict[str, object]]",
    names: "list[str]",
    classes: "dict[str, str]",
    person: str,
    pt_blocks: "dict[str, dict[str, object]]",
    floor: int,
) -> "list[dict[str, object]]":
    """Every column block as the layer publishes it (4.6c.3 (b), (c); 4.6c.5 (b); 4.6c.6 (c)).

    The person column keeps its presence and absence in rows (section
    5.3), its repetition census withheld, every other key read over the
    patient table; a patient-fixed column takes its block over the patient
    table; a position-like or held column publishes no key but its name,
    place and role; every other column's multiplicity map is withheld
    unless each value covers one row.
    """
    out: "list[dict[str, object]]" = []
    for place in range(len(blocks)):
        block = blocks[place]
        name = names[place]
        kind = classes[name]
        if name == person:
            patient_block = _person_counts_floored(pt_blocks[name], floor) if name in pt_blocks else {}
            rewritten: "dict[str, object]" = {}
            for key in block:
                if key in PERSON_KEPT_IN_ROWS or key not in patient_block:
                    rewritten[key] = block[key]
                else:
                    rewritten[key] = patient_block[key]
            rewritten["n_distinct_by_occurrences"] = None
            out += [rewritten]
            continue
        if kind == pr.CLASS_FIXED and name in pt_blocks:
            moved: "dict[str, object]" = {}
            for key in pt_blocks[name]:
                moved[key] = place + 1 if key == "position" else pt_blocks[name][key]
            out += [moved]
            continue
        if kind in (pr.CLASS_POSITION, pr.CLASS_HELD):
            out += [_emptied(block)]
            continue
        found = _get(block, "n_distinct_by_occurrences")
        if found is not None and not _one_each(found, _get(block, "n_present")):
            rewritten = {}
            for key in block:
                rewritten[key] = None if key == "n_distinct_by_occurrences" else block[key]
            out += [rewritten]
            continue
        out += [block]
    return out


# -- THE DERIVED COLUMNS (4.6c.2 (a), (b)) ---------------------------------


def _own_mean(row: _RowColumn, patients: _Patients, grid: pr.Grid, floor: int) -> "tuple[rules.Ladder, list[int], list[fractions.Fraction]] | None":
    """The own mean's ladder over patients (4.6c.2 (a)): deciles with p25 and p75 of the patients' means.

    Each edge is the patients' mean at its rank (nearest rank), kept to
    `u / 1000` (departure (5)); equal edges collapse; the `L0` merge then
    holds every value band at `max(2 f, f + 4)` patients or more. Returns
    the ladder, each patient's `L0` band and the edge of each starting
    band but the first.
    """
    means: "list[fractions.Fraction]" = []
    for rows in patients.rows:
        present = [row.readings[k] for k in rows if row.readings[k] is not None]
        if not present:
            return None
        total = fractions.Fraction(0)
        for value in present:
            if value is not None:
                total += value
        means += [total / len(present)]
    ordered = sorted(means)
    count = len(ordered)
    keep = grid.step / (10 ** OWN_MEAN_PLACES)
    keys = ("p10", "p20", "p25", "p30", "p40", "p50", "p60", "p70", "p75", "p80", "p90")
    percents = (10, 20, 25, 30, 40, 50, 60, 70, 75, 80, 90)
    edges: "list[fractions.Fraction]" = []
    named: "list[str]" = []
    for at in range(len(keys)):
        rank = max(0, min(count - 1, pr.ceil_div(percents[at] * count, 100) - 1))
        kept = (ordered[rank] // keep) * keep
        if edges and kept <= edges[-1]:
            continue
        edges += [kept]
        named += [keys[at]]
    if not edges:
        return None
    quartiles = [edges[at] for at in range(len(edges)) if named[at] in ("p25", "p50", "p75")]
    medians = [edges[at] for at in range(len(edges)) if named[at] == "p50"]
    names: "list[object]" = []
    groups: "list[list[int]]" = [[], [], []]
    for k in range(len(edges) + 1):
        names += [(named[k - 1] if k else None, named[k] if k < len(edges) else None)]
        groups[0] += [k]
        groups[1] += [len([cut for cut in quartiles if k and cut <= edges[k - 1]])]
        groups[2] += [len([cut for cut in medians if k and cut <= edges[k - 1]])]
    start = rules.Starting(tuple(names), (tuple(groups[0]), tuple(groups[1]), tuple(groups[2])), tuple(True for _name in names), False, tuple(edges))
    starting = [_band_of(edges, mean) for mean in means]
    totals = [0] * len(names)
    for band in starting:
        totals[band] += 1
    ladder = rules.merge_ladder(f"(own mean of {row.name})", start, totals, pr.own_mean_floor(floor))
    if ladder is None:
        return None
    to_l0 = [0] * len(names)
    for at in range(len(ladder.l0)):
        for place in range(len(names)):
            if names[place] in ladder.l0[at]:
                to_l0[place] = at
    return ladder, [to_l0[band] for band in starting], edges


def _band_of(edges: "list[fractions.Fraction]", value: fractions.Fraction) -> int:
    """The value band holding `value`: how many edges stand at or below it."""
    low = 0
    high = len(edges)
    while low < high:
        middle = (low + high) // 2
        if edges[middle] <= value:
            low = middle + 1
        else:
            high = middle
    return low


def _edges_at(ladder: rules.Ladder, starting_edges: "list[fractions.Fraction]", level: int) -> "list[fractions.Fraction]":
    """The own mean's edges at a level: the lower edge of each of its bands but the first, in order."""
    out: "list[fractions.Fraction]" = []
    first_place: "dict[int, int]" = {}
    for place in range(len(ladder.l0)):
        band = ladder.maps[level][place]
        if band not in first_place:
            first_place[band] = place
    starts_before = 0
    first_start: "list[int]" = []
    for place in range(len(ladder.l0)):
        first_start += [starts_before]
        starts_before += len(ladder.l0[place])
    for band in sorted(first_place):
        if band == 0:
            continue
        start = first_start[first_place[band]]
        out += [starting_edges[start - 1]]
    return out


def _at_level(ladder: rules.Ladder, level: int, totals: "list[int]", name: str) -> rules.Ladder:
    """A ladder whose `L0` is `ladder`'s level `level`, totals as given, coarser levels read through it."""
    count = ladder.counts[level]
    names: "list[tuple[object, ...]]" = [() for _band in range(count)]
    for place in range(len(ladder.l0)):
        band = ladder.maps[level][place]
        names[band] = names[band] + ladder.l0[place]
    second = _renumbered(tuple(rules.coarsen(ladder, level, max(level, 1))))
    third = _renumbered(tuple(rules.coarsen(ladder, level, 2)))
    ordered = tuple(
        any(ladder.ordered[place] for place in range(len(ladder.l0)) if ladder.maps[level][place] == band)
        for band in range(count)
    )
    return rules.Ladder(name, tuple(names), (tuple(range(count)), second, third), (count, max(second) + 1, max(third) + 1), tuple(totals), ordered)


def _renumbered(mapping: "tuple[int, ...]") -> "tuple[int, ...]":
    """A level map renumbered from 0 in order of first appearance."""
    seen: "dict[int, int]" = {}
    out: "list[int]" = []
    for one in mapping:
        if one not in seen:
            seen[one] = len(seen)
        out += [seen[one]]
    return tuple(out)


def _first_date(row: _RowColumn, patients: _Patients, floor: int) -> "tuple[int, list[int], list[int]] | None":
    """A dealt date column's first date (4.6c.2 (a), (b)): its finest eligible level, patients a band, and their totals.

    A patient's earliest present reading, read at the source's own level
    (a patient with none in the `missing` band its rows stand in); the
    level is eligible where every band holds 0 or at least `f` patients
    and every residual difference (the source's rows in a band less its
    patients there) is 0 or at least `f` rows.
    """
    for level in range(3):
        bands = row.ladder.counts[level]
        totals = [0] * bands
        first_of: "list[int]" = []
        for rows in patients.rows:
            dated = [k for k in rows if row.readings[k] is not None]
            if dated:
                earliest = dated[0]
                for k in dated:
                    here = row.readings[k]
                    best = row.readings[earliest]
                    if here is not None and best is not None and (here, k) < (best, earliest):
                        earliest = k
                band = row.codes[level][earliest]
            else:
                band = row.codes[level][rows[0]]
            first_of += [band]
            totals[band] += 1
        source = rules.totals_at(row.ladder, level)
        if any(0 < total < floor for total in totals):
            continue
        if any(source[at] - totals[at] < 0 or 0 < source[at] - totals[at] < floor for at in range(bands)):
            continue
        if len([total for total in totals if total]) < 2:
            continue
        return level, first_of, totals
    return None


def _first_date_edges(row: _RowColumn, level: int) -> "list[object]":
    """A first date's edges: its source's rungs at the level, as the source publishes them (4.6c.2 (a): no edge of its own).

    Written as the rungs' values, so they read whether or not the source
    column's own block stands (a source drawn HELD publishes none).
    """
    rungs = rules.rung_ladder(row.block)
    out: "list[object]" = []
    seen: "set[int]" = set()
    for place in range(len(row.ladder.l0)):
        band = row.ladder.maps[level][place]
        if band in seen:
            continue
        seen |= {band}
        name = row.ladder.l0[place][0]
        if isinstance(name, tuple) and len(name) == 2 and name[0] is not None and isinstance(rungs, dict):
            out += [_get(rungs, f"{name[0]}")]
    return out


# -- THE WHOLE STEP --------------------------------------------------------


COUNTERS = (
    "census_candidates", "census_steps", "patients", "extra_rows", "patient_fixed", "position_like",
    "dealt_date", "repeated", "held", "row_families", "one_cell_families", "certificate_refusals",
    "witness_refusals", "split_steps", "splits_tried", "splits_failed", "split_bound_hit", "trend_cells",
    "trend_published", "trend_refused_swing", "trend_refused_total", "derived", "fixed_rows",
    "tables_counted", "candidates", "floor_refusals", "w1_refusals", "we_refusals", "eligible_options",
    "options_left_unread", "tie_refusals",
)


def describe(
    table: reading.Table,
    document: "dict[str, object]",
    settings: taxonomy.Settings,
    switch: "chain.ChainSwitch",
    filled: bytearray,
    persons: "list[str]",
    identifiers: "set[str]",
    forced_codes: "list[str]",
    forced_measurements: "list[str]",
    forced_decimal_commas: "list[str]",
    stored_as: "tuple[str, ...]",
) -> Layer:
    """The patient layer of a table whose settings name a person column (contract 4.6c), or why it is off.

    Guarantees: reads the table through `reading.column_values` and the
    description `profile.build_document` wrote of it; returns the patient
    chain, `grain` and the column blocks as the layer publishes them, or
    None for all three with the reason in the notes. The same table,
    name, key, settings and declarations give the same objects byte for
    byte: nothing here reads a clock, an environment or a random source
    but the key's words. Every count it publishes is 0 or at least the
    floor, in patients wherever the object counts patients. Boundary: the
    key enters `chain.step_word` alone. Not in force: only
    `chain.describe`, behind the switch, calls it.
    """
    counts: "dict[str, int]" = {name: 0 for name in COUNTERS}
    notes: "list[str]" = []
    floor = settings.small_cell_floor
    blocks: "list[dict[str, object]]" = []
    published = _get(document, "columns")
    if isinstance(published, list):
        for block in published:
            if isinstance(block, dict):
                blocks += [block]
    names = [f"{_get(block, 'name')}" for block in blocks]
    # -- (a) the gate, items 1 to 3 (4.6c.3 (a)) --
    if len(persons) != 1 or persons[0] not in names:
        return _off(OFF_PERSONS, notes, counts)
    person = persons[0]
    person_place = pr.place_in(names, person)
    for place in range(len(blocks)):
        if names[place] != person and names[place] in switch.held and chain.repeats(reading.column_values(table, place)):
            return _off(OFF_HELD, notes, counts)
    person_block = blocks[person_place]
    blank_rows = rules.records_holding_nothing(document)
    if _get(person_block, "n_missing") != blank_rows:
        return _off(OFF_BLANK, notes, counts)
    tabled = _tabled_rows(table, filled, blank_rows)
    if tabled is None:
        return _off(OFF_RECOUNT, notes, counts)
    grouped = _patients_of(reading.column_values(table, person_place), tabled)
    if grouped is None:
        return _off(OFF_BLANK, notes, counts)
    _keys, of_row, patient_rows = grouped
    patient_count = len(patient_rows)
    if patient_count != _get(person_block, "n_distinct") or patient_count != _get(person_block, "n_distinct_folded"):
        return _off(OFF_MERGED, notes, counts)
    counts["patients"] = patient_count
    counts["extra_rows"] = len(tabled) - patient_count
    if len(tabled) - patient_count < floor:
        return _off(OFF_EXTRA, notes, counts)
    r_values = [len(rows) for rows in patient_rows]
    # -- (b) the census and its draw (4.6c.4; item 4 of the gate) --
    candidates, steps = census_candidates(r_values, floor)
    counts["census_candidates"] = len(candidates)
    counts["census_steps"] = steps
    if not candidates:
        return _off(OFF_CENSUS, notes, counts)
    scores = [fractions.Fraction(0)] + [fractions.Fraction(patient_count * one.lo) for one, _steps in candidates]
    pick = _draw(switch, "census", 0, [person], scores)
    if pick == 0:
        return _off(OFF_DRAWN, notes, counts)
    census = candidates[pick - 1][0]
    notes += [f"the census drew top edge {census.lo} among {len(candidates)} eligible candidates and off"]
    threshold, _two = _threshold(census, floor)
    values_r = pr.r_band_values(census)
    r_code_of: "dict[int, int]" = {}
    for at in range(len(values_r)):
        low, high = values_r[at]
        if high is not None:
            r_code_of[low] = at
    top_code = len(values_r) - 1
    r_codes = [r_code_of[one] if one in r_code_of else top_code for one in r_values]
    # -- (c) every column read in rows, and the classes (4.6c.5 to 4.6c.7) --
    held_by_switch = set(switch.held)
    sequences = chain.sequence_places(document)
    codes_declared = set(forced_codes)
    measurements_declared = set(forced_measurements)
    commas_declared = set(forced_decimal_commas)
    # THE CELLS AS THE ROW DESCRIPTION READ THEM (Codex's review of batch
    # 4p, item 1, HIPAA): every class, reading, band and position list below
    # reads a column's cells as its description read them -- 24,000 rows of
    # ages 80 to 99 under a description top-coded at 90 published a
    # position list of 80 to 92 from the cells as the file wrote them. The
    # recount on those cells stays the gate, as before.
    seen_codes, seen_measurements, seen_commas = chain.declarations_read(
        document, forced_codes, forced_measurements, forced_decimal_commas
    )
    first_patients = _Patients(tabled, of_row, patient_rows, r_values)
    classes: "dict[str, str]" = {}
    row_columns: "dict[str, _RowColumn]" = {}
    fixed_names: "list[str]" = []
    fixed_cells: "dict[str, list[str]]" = {}
    position_like: "list[str]" = []
    fine_runs: "list[str]" = []
    position_texts: "dict[str, list[str]]" = {}
    for place in range(len(blocks)):
        block = blocks[place]
        name = names[place]
        if name == person:
            classes[name] = pr.CLASS_PERSON
            continue
        if chain.ineligible_reason(block, place in sequences, name in held_by_switch, identifiers) is not None:
            classes[name] = pr.CLASS_INELIGIBLE
            continue
        declared = _declared(name, codes_declared, measurements_declared, commas_declared)
        storage = stored_as[place] if place < len(stored_as) else ""
        read = chain.read_column(table, place, block, settings, declared, storage, blank_rows)
        if read is None or not read.agrees:
            notes += [f"the recount of column {name} disagreed with its published counts"]
            return _off(OFF_RECOUNT, notes, counts)
        seen = _declared(name, seen_codes, seen_measurements, seen_commas)
        read, values, declared = _as_described(table, place, block, settings, declared, seen, storage, blank_rows, read)
        if read is None or not read.agrees:
            notes += [f"the recount of column {name} disagreed with its published counts"]
            return _off(OFF_RECOUNT, notes, counts)
        ladder, first = _ladder_in(read, tabled, name, floor)
        texts = [values[row] for row in tabled]
        role = f"{_get(block, 'role')}"
        readings: "list[fractions.Fraction | None]" = []
        # A FINE NUMBER COLUMN IS READ BEFORE ITS LADDER DECIDES ANYTHING: a
        # visit number's block is the census under another name, however few
        # bands it merges to (departure (16) of contract 4.6c.12).
        if role in rules.NUMBER_ROLES and moments.fine(block) and _two_cells(texts, first_patients) > threshold:
            meaning = chain.reading_of(block, values, settings, declared, storage)
            for text in texts:
                kind, value = meaning[text] if text in meaning else ("missing", None)
                readings += [_reading(role, value, block) if kind == "value" else None]
            if _not_a_run(readings, first_patients) <= threshold:
                classes[name] = pr.CLASS_POSITION
                position_like += [name]
                position_texts[name] = texts
                fine_runs += [name]
                continue
        if ladder is None or _eligible_ladder(ladder, _get(block, "role")) is not None:
            classes[name] = pr.CLASS_INELIGIBLE
            continue
        if _two_cells(texts, first_patients) <= threshold:
            classes[name] = pr.CLASS_FIXED
            fixed_names += [name]
            fixed_cells[name] = values
            continue
        if not readings:
            meaning = chain.reading_of(block, values, settings, declared, storage)
            for text in texts:
                kind, value = meaning[text] if text in meaning else ("missing", None)
                readings += [_reading(role, value, block) if kind == "value" else None]
        key_read = pr.key_read(block)
        groups = rules.small_group_bands(block, read.start, ladder, floor) | chain.value_run_bands(block, read.start, ladder, floor, read.readings)
        row_columns[name] = _RowColumn(name, place, block, ladder, _codes_three(ladder, first), frozenset(groups), texts, readings, moments.fine(block), key_read)
        if role == rules.ROLE_DATETIME:
            classes[name] = pr.CLASS_DEALT
            continue
        if key_read:
            levels: "list[object]" = list(texts) if role in rules.ORDERED_ROLES else [read.codes[row] for row in tabled]
            if _level_twice(levels, first_patients) <= threshold:
                classes[name] = pr.CLASS_POSITION
                position_like += [name]
                position_texts[name] = texts
                continue
        classes[name] = pr.CLASS_REPEATED
    # -- (d) the position column (4.6c.7 (a)): the first dealt date column
    # in schema order, a function of published roles and classes (it keeps
    # its place where its own description in rows is later held); each
    # patient's rows in its order, ties and absent dates by row order.
    dealt = [name for name in names if classes[name] == pr.CLASS_DEALT]
    position = dealt[0] if dealt else None
    if position is not None:
        stamps = row_columns[position].readings
        ordered_rows: "list[list[int]]" = []
        for rows in patient_rows:
            present = sorted((stamp, k) for k in rows for stamp in (stamps[k],) if stamp is not None)
            ordered_rows += [[k for _stamp, k in present] + [k for k in rows if stamps[k] is None]]
        patient_rows = ordered_rows
    patients = _Patients(tabled, of_row, patient_rows, r_values)
    # The position lists (4.6c.6 (c)); a number column whose tie world needs
    # more than 20 readings is not position-like (4.6c.6 (b)): it is
    # repeated, a column the KEY test reads, kept by its class witness.
    lists: "dict[str, list[object]]" = {}
    length = census.lo if census.top_patients else len(census.bands)
    beyond = census.lo + pr.tight_cap(census) - length if census.top_patients else 0
    for name in list(position_like):
        listed = _position_list(position_texts[name], patients, length, floor)
        if name in fine_runs:
            # A FINE RUN'S LIST STANDS WHOLE OR NOT AT ALL (departure (16)):
            # its tie world holds every patient on the list, so a list with a
            # `null` or out of order leaves the column HELD, never a block.
            if not _run_list(listed):
                classes[name] = pr.CLASS_HELD
                position_like = [one for one in position_like if one != name]
                continue
            lists[name] = listed
            continue
        if f"{_get(blocks[pr.place_in(names, name)], 'role')}" in rules.ORDERED_ROLES:
            used = len([one for one in listed if one is not None]) + 3 * len([one for one in listed if one is None]) + max(0, beyond)
            if used > POSITION_READINGS:
                classes[name] = pr.CLASS_REPEATED
                position_like = [one for one in position_like if one != name]
                continue
        lists[name] = listed
    # -- (e) the patient table: patient-fixed columns, r, derived columns --
    pt_names = [person] + fixed_names
    pt_cells: "list[list[str]]" = []
    # EACH PATIENT-FIXED COLUMN'S CELLS AS THE ROW DESCRIPTION READ THEM (the
    # sibling sweep of Codex's review of batch 4p, item 1, HIPAA): a fixed
    # year of birth whose rows the description top-coded at 1937 (a stray
    # cell on a patient's later row shaping it) put each patient's first
    # cell on the patient table as the file wrote it, and the patient
    # table's own description, holding no stray, published years of 1925
    # to 1936 in its block and a band of patients below them in its chain.
    # The person column's cells are its keys, as the file wrote them.
    for name in pt_names:
        values = fixed_cells[name] if name in fixed_cells else reading.column_values(table, pr.place_in(names, name))
        pt_cells += [[values[tabled[rows[0]]] for rows in patient_rows]]
    patient_table = reading.Table(
        column_names=pt_names,
        columns=pt_cells,
        n_rows=patient_count,
        encoding=table.encoding,
        used_fallback_encoding=table.used_fallback_encoding,
        header_source=table.header_source,
        header_evidence=table.header_evidence,
    )
    pt_storage = tuple(stored_as[pr.place_in(names, name)] if pr.place_in(names, name) < len(stored_as) else "" for name in pt_names)
    # The patient table holds its own columns only, so the settings it is
    # described under name only them (a date declared as counts or a clock
    # as twelve-hour, on a repeated column, is no fact of this table).
    pt_settings = dataclasses.replace(profile.settings_without_held(settings, [name for name in names if name not in pt_names]), person_columns=())
    # EVERY RULE THE ROW DESCRIPTION APPLIED HOLDS THE PATIENT TABLE (the
    # first skeptic's item 1, HIPAA): the Safe Harbor top-code, its answers,
    # the columns held for a question and the floor-size count of dates, each
    # patient a holder, however few patients a table has.
    pt_document = profile.build_document(
        patient_table,
        pt_settings,
        [person],
        [name for name in pt_names if name in codes_declared],
        [name for name in pt_names if name in measurements_declared],
        [name for name in pt_names if name in commas_declared],
        stored_as=pt_storage,
        unanswered=[name for name in switch.unanswered if name in pt_names],
        top_code=True,
        safe_harbor_no=[name for name in switch.safe_harbor_no if name in pt_names],
        rare_values_released=switch.rare_values_released,
        harbor_year=switch.harbor_year,
        kept_identities=[name for name in switch.kept_identities if name in pt_names],
        long_table_dates=True,
    )
    pt_blocks: "dict[str, dict[str, object]]" = {}
    described = _get(pt_document, "columns")
    if isinstance(described, list):
        for block in described:
            if isinstance(block, dict):
                pt_blocks[f"{_get(block, 'name')}"] = block
    patient_columns: "dict[str, chain.Column]" = {}
    scales: "dict[str, rules.Ladder]" = {}
    codes_of: "dict[str, tuple[list[int], list[int], list[int]]]" = {}
    own_groups: "dict[str, frozenset[int]]" = {}
    pt_eligible: "list[str]" = []
    pt_ineligible: "list[dict[str, object]]" = []
    everyone = list(range(patient_count))
    for at in range(1, len(pt_names)):
        name = pt_names[at]
        block = pt_blocks[name] if name in pt_blocks else {}
        declared = _declared(name, codes_declared, measurements_declared, commas_declared)
        read = chain.read_column(patient_table, at, block, pt_settings, declared, pt_storage[at], 0)
        if read is None or not read.agrees:
            notes += [f"the patient table's recount of column {name} disagreed with its published counts"]
            return _off(OFF_RECOUNT, notes, counts)
        ladder, first = _ladder_in(read, everyone, name, floor)
        reason = _eligible_ladder(ladder, _get(block, "role"))
        if ladder is None or reason is not None:
            pt_ineligible += [{"column": name, "reason": reason or "one_band"}]
            continue
        pt_groups = frozenset(rules.small_group_bands(block, read.start, ladder, floor) | chain.value_run_bands(block, read.start, ladder, floor, read.readings))
        patient_columns[name] = _column(name, ladder, first, pt_groups, sum(read.blanks[k] for k in everyone))
        scales[name] = ladder
        codes_of[name] = _codes_three(ladder, first)
        own_groups[name] = pt_groups
        pt_eligible += [name]
    r_scale = pr.r_ladder(census)
    if r_scale is None:
        pt_ineligible += [{"column": pr.R_NAME, "reason": "one_band"}]
    else:
        patient_columns[pr.R_NAME] = _column(pr.R_NAME, r_scale, r_codes, frozenset(), 0)
        scales[pr.R_NAME] = r_scale
        codes_of[pr.R_NAME] = _codes_three(r_scale, r_codes)
        pt_eligible += [pr.R_NAME]
    # -- (f) the patient chain without its derived columns (4.6b in patients; 4.6c.8 (a)) --
    place_of: "dict[str, int]" = {}
    for at in range(len(pt_eligible)):
        place_of[pt_eligible[at]] = at
    search = chain.Search(patient_columns, scales, tuple(pt_eligible), place_of, patient_count, floor, frozenset(), (), {}, counts, {}, {}, frozenset(), frozenset())
    placed: "list[rules.Family]" = []
    if len(pt_eligible) >= 2:
        placed, step_notes = _patient_chain(search, switch, set(), census)
        notes += step_notes
    if not placed:
        placed = _rules_only(search)
    # -- (f') the derived columns (4.6c.2), drawn after the rest of the chain
    # (departure (3) of P4-D449): a level is eligible where its bands hold
    # the floor and a keyed family can hold the column (r, and every member
    # of every earlier keyed family, at its level or finer); "no derived
    # column" is eligible on every table; a drawn column's family is drawn
    # among those keyed options alone, so it is a member of `G`.
    derived: "dict[str, _Derived]" = {}
    derived_written: "list[dict[str, object]]" = []
    grids: "dict[str, pr.Grid]" = {}
    step = 0
    index = len(placed)
    for name in names:
        if classes[name] not in (pr.CLASS_REPEATED, pr.CLASS_DEALT):
            continue
        row = row_columns[name]
        candidates_of: "list[tuple[int, rules.Ladder, list[int], list[fractions.Fraction]]]" = []
        if classes[name] == pr.CLASS_DEALT:
            label = f"(first date of {name})"
            kind = pr.FIRST_DATE
            found_first = _first_date(row, patients, floor)
            if found_first is not None:
                level, first_of, totals = found_first
                candidates_of += [(level, _at_level(row.ladder, level, totals, label), first_of, [])]
        else:
            label = f"(own mean of {name})"
            kind = pr.OWN_MEAN
            grid = pr.grid_of(row.block) if row.fine else None
            if grid is None or _get(row.block, "n_missing") != blank_rows:
                continue
            grids[name] = grid
            found_mean = _own_mean(row, patients, grid, floor)
            if found_mean is None:
                continue
            whole, bands_of, starting_edges = found_mean
            for level in range(3):
                if whole.counts[level] >= 2:
                    candidates_of += [(level, _at_level(whole, level, rules.totals_at(whole, level), label), [whole.maps[level][band] for band in bands_of], _edges_at(whole, starting_edges, level))]
        eligible_levels: "list[tuple[int, rules.Ladder, list[int], list[fractions.Fraction], list[chain.Option], chain._Search]]" = []
        for level, ladder, first_of, edges in candidates_of:
            trial_columns = dict(patient_columns)
            trial_columns[label] = _column(label, ladder, first_of, frozenset(), 0)
            trial_scales = dict(scales)
            trial_scales[label] = ladder
            trial_eligible = tuple(list(pt_eligible) + [label])
            trial_place = {one: at for at, one in enumerate(trial_eligible)}
            trial = chain.Search(trial_columns, trial_scales, trial_eligible, trial_place, patient_count, floor, frozenset(), (), {}, counts, {}, {}, frozenset(), frozenset())
            keyed_options = [
                option for option in chain.step_options(trial, placed, chain.clamps_of(trial, placed, False), {})
                if option.child == label and option.parents and _keeps_keyed_rule(placed, option, {derived[key].label for key in derived} | {label}, pr.R_NAME in scales, trial_scales)
                and _keeps_r_star(option, trial_scales, census, floor, {derived[key].label for key in derived} | {label})
            ]
            if keyed_options:
                eligible_levels += [(level, ladder, first_of, edges, keyed_options, trial)]
        scores = [fractions.Fraction(0)] + [fractions.Fraction(patient_count * one[1].counts[0]) for one in eligible_levels]
        pick = _draw(switch, "patient_level", step, [name, kind], scores)
        step += 1
        if pick == 0:
            continue
        level, ladder, first_of, edges, keyed_options, trial = eligible_levels[pick - 1]
        chosen_option = keyed_options[chain.draw_step(trial, switch, index, keyed_options)]
        index += 1
        placed += [chain.family_of(chosen_option)]
        derived[name] = _Derived(label, kind, name, level, first_of, edges)
        written_edges: "list[object]" = _first_date_edges(row, level) if kind == pr.FIRST_DATE else [pr.decimal_text(edge) for edge in edges]
        derived_written += [{"edges": written_edges, "kind": kind, "level": rules.LEVELS[level], "name": label, "source": name}]
        patient_columns[label] = _column(label, ladder, first_of, frozenset(), 0)
        scales[label] = ladder
        codes_of[label] = _codes_three(ladder, first_of)
        pt_eligible += [label]
    counts["derived"] = len(derived)
    # -- (g) the grain family (4.6c.8 (a)) --
    grain = _grain_of(placed, scales, codes_of, census, r_codes, patient_count, {derived[key].label for key in derived})
    everyone_cells = [[cell for cell in range(len(grain.patients)) if grain.patients[cell]]]
    base_blocks = pr.top_blocks(grain, values_r, census.lo, everyone_cells, [len(tabled)])
    if base_blocks is None:
        return _off(OFF_RECOUNT, notes, counts)
    ctx = _Ctx(
        switch, floor, census, values_r, patients, scales, codes_of, own_groups, counts, threshold, len(tabled),
        base_blocks, pr.r_star_of(grain, values_r, census.lo, base_blocks, floor), [],
    )
    # -- (h) the row families, and every other column's one-cell family (4.6c.8) --
    rows_written: "list[dict[str, object]]" = []
    row_tables: "dict[str, tuple[int, list[int], int, tuple[tuple[str, int], ...]]]" = {}
    parents_of: "dict[str, tuple[tuple[str, int], ...]]" = {}
    index = 0
    for name in names:
        if classes[name] not in (pr.CLASS_REPEATED, pr.CLASS_DEALT):
            continue
        row = row_columns[name]
        one = derived[name] if name in derived else None
        drawn = _row_family(ctx, grain, row, index, one, grids[name] if name in grids else pr.grid_of(row.block))
        index += 1
        if drawn is not None:
            level, table_counts, bands, chosen = drawn
            row_tables[name] = drawn
            parents_of[name] = chosen
            rows_written += [{
                "child": name,
                "level": rules.LEVELS[level],
                "parents": [{"column": member, "level": rules.LEVELS[member_level]} for member, member_level in chosen],
                "table": [list(table_counts[at * bands : (at + 1) * bands]) for at in range(len(table_counts) // bands)],
            }]
            counts["row_families"] += 1
            continue
        if one is not None:
            # Departure (6): a column whose derived column stands beside no
            # row family of it is HELD.
            classes[name] = pr.CLASS_HELD
    # Every column left without a family reads the `R*` that finally stands.
    for name in names:
        if classes[name] not in (pr.CLASS_REPEATED, pr.CLASS_DEALT) or name in row_tables:
            continue
        row = row_columns[name]
        if _one_cell(ctx, grain, row, grids[name] if name in grids else pr.grid_of(row.block)):
            counts["one_cell_families"] += 1
            continue
        classes[name] = pr.CLASS_HELD
    for name in names:
        key = {
            pr.CLASS_FIXED: "patient_fixed", pr.CLASS_POSITION: "position_like", pr.CLASS_DEALT: "dealt_date",
            pr.CLASS_REPEATED: "repeated", pr.CLASS_HELD: "held",
        }
        if classes[name] in key:
            counts[key[classes[name]]] += 1
    # -- (i) change over visits (4.6c.1) --
    trend: "list[dict[str, object]]" = []
    grid_entries: "list[dict[str, object]]" = []
    derived_labels = {derived[key].label for key in derived}
    for name in names:
        if name not in row_tables or name not in grids or classes[name] != pr.CLASS_REPEATED:
            continue
        found_trend = _trends(ctx, grain, placed, row_columns[name], grids[name], row_tables[name], derived[name] if name in derived else None, derived_labels)
        if found_trend:
            trend += found_trend
            grid_entries += [pr.grid_written(grids[name])]
    # -- (j) the row census of each patient-fixed column (4.6c.5 (c)) --
    fixed_rows: "list[dict[str, object]]" = []
    for name in fixed_names:
        if name in scales:
            found_rows = _fixed_rows(ctx, name, placed, parents_of)
            if found_rows is not None:
                fixed_rows += [found_rows]
    counts["fixed_rows"] = len(fixed_rows)
    # -- (k) the patient chain as 4.6b writes it, in patients, and grain (4.6c.9) --
    words, implied = rules.words_of(pt_eligible, placed)
    chain_entries: "list[dict[str, object]]" = []
    for family in placed:
        sizes = rules.radices(family, scales)
        width = len(family.table) // sizes[0]
        chain_entries += [{
            "anchor": family.anchor,
            "child": family.child,
            "level": rules.LEVELS[family.level],
            "parents": [{"column": member, "level": rules.LEVELS[level]} for member, level in family.parents],
            "slopes": None,
            "table": [list(family.table[at * sizes[0] : (at + 1) * sizes[0]]) for at in range(width)],
        }]
    statistical: "dict[str, object]" = {
        "chain": chain_entries,
        "ineligible": pt_ineligible,
        "ladder": [rules.published_ladder(scales[name]) for name in pt_eligible],
        "moments": None,
        "not_carried": implied,
        "procedure": rules.procedure_record(patient_count),
        "rules": [],
        "withheld": [],
        "words": words,
    }
    grain_written: "dict[str, object]" = {
        "census": pr.census_written(census),
        "classes": [{"class": classes[name], "column": name} for name in names],
        "derived": derived_written,
        "fixed_rows": fixed_rows,
        "grain_family": grain.index,
        "grid": grid_entries,
        "ladder": [rules.published_ladder(row_columns[name].ladder) for name in names if classes[name] in (pr.CLASS_REPEATED, pr.CLASS_DEALT)],
        "person": person,
        "position": position,
        "positions": [{"column": name, "values": lists[name]} for name in names if classes[name] == pr.CLASS_POSITION],
        "rows": rows_written,
        "trend": trend,
    }
    notes += [
        f"the patient layer stands: {patient_count} patients, census top edge {census.lo}, "
        f"{counts['patient_fixed']} patient-fixed, {counts['position_like']} position-like, "
        f"{counts['repeated'] + counts['dealt_date']} described in rows, {counts['held']} held"
    ]
    return Layer(statistical, grain_written, _blocks_as_published(blocks, names, classes, person, pt_blocks, floor), tuple(notes), counts)
