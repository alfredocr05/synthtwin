"""THE PATIENT WALK: the twin of a description whose `grain` stands (method G16.13 to G16.17; lane GRb, plan P4-D465).

NOT IN FORCE. Only a description loaded behind the chain's switch can
carry `grain` (contract 4.6c, invariants S29 to S33), and no shipped
command loads one so: `generation.generate_held` reaches this module from
its one branch where `relationships.grain` stands, and every other twin is
made exactly as before (S12; the switch at its default moves no byte).

What runs, in G16.13's order, reading the description only (never the
key's `R*`, never a real row):

1. THE PATIENT TABLE (`patient_table`): its columns -- the person
   column's patient view, the patient-fixed columns (their blocks counted
   in patients), `r` and the derived columns -- made over `N` patient rows
   by G4 and arranged against the patient chain by the EXISTING walk:
   `generation.generate_held` run on the patient table's own description
   (its `_walk_plan` and `_chain_family`, G16.0 to G16.6, the same code).
   `r` and each derived column stand in it as label columns holding each
   published band on its count, so the walk deals their bands; `r`'s cells
   are then written from the census (G16.14), never dealt from a block.
2. PATIENTS INTO ROWS: patient `p` becomes `r_p` consecutive rows in the
   patient table's row order; the person column and every patient-fixed
   column are copied to each of its rows.
3. THE ROW COLUMNS (`row_table`): every other column made by G4 over the
   table's rows from its block, the repeated and dealt date columns with
   their `L0` band totals counted in rows (`grain.ladder`).
4. THE ROW FAMILIES, in `grain.rows` order: each child dealt inside each
   parent cell by G16.2's walk (`chain_walk.deal`) on each row's hidden
   score plus G16.15's patient term.
5. POSITIONS: every dealt date sorted within its patient; each
   position-like column written from its list.
6. THE DERIVED COLUMNS' CLOSE (own means; first dates across bands) and
   THE TREND (G16.15).
7. Computed dates (G16.16): no description this version loads classes a
   column computed in the patient layer (contract 4.6c.12, departure 12).
8. THE OTHER COLUMNS keep G4.2's placement; a withheld multiplicity map
   takes G16.13 step 8's even map (`with_even_map`).

Every word is drawn by `generation.generate_held` (`draw_plan` counts them
from the description) and handed over in `Draws`. The arithmetic is
G16.8's: whole numbers, the walk's words, and binary64 `+ - * /` and
`sqrt` in the order written; the normal quantile, the logarithm and the
normal distribution function are the shared module's.
"""
import dataclasses
import fractions
import math

from synthtwin import chain_rules, chain_walk, contract, dialect, errors, generation, patient_intervals, patient_rules, patient_trajectory, twinstore

# The grid of the patient weight `omega` (G16.15): 0, 0.005, ..., 0.995.
OMEGA_STEPS = 200
OMEGA_STEP = 0.005
# The own-mean score's points a band (G16.15): 24 equal quantile points.
OMEGA_POINTS = 24
# The trend's random improving exchanges: proposals a patient (G16.15).
TREND_PROPOSALS = 30
# The exact close's reach: positions at most this far apart (G16.15).
TREND_REACH = 40
# The derived closes' bound on passes over the patients (G16.15).
CLOSE_PASSES = 4
# The own-mean close's bound on the partner rows one of a patient's rows is
# read against (a run of equal readings may hold thousands of rows): the
# close's time stays linear in the rows (G16.17's memory and time).
CLOSE_PARTNERS = 256
# THE OWN-MEAN CLOSE'S TOTAL-WORK BOUND (repair 2 of lane GRb, LANE GRb
# RULINGS 5 (3), Codex's item 3): in one pass a patient visits at most
# `CLOSE_VISITS` of its own rows for each row it holds (a visit reads at most
# `CLOSE_PARTNERS` partner rows in each of its two searches), and a close
# reads at most `CLOSE_WORK` rows for each row of its column in all (its
# patients' own rows and the partner rows their searches read); a patient
# whose search reaches its own bound stops for that pass, and a close that
# reaches `CLOSE_WORK` ends there; the patients a close leaves outside are
# named in DEVIATIONS on the derived column and on each row family it
# parents, the note saying the search stopped at its total-work bound
# wherever either bound stopped one. Two patients of `n` rows each needing
# `n / 2` exchanges of one step cost the build `n ** 2 / 2` visits.
CLOSE_VISITS = 16
CLOSE_WORK = 1024


def _internal(detail: str) -> errors.ProfileError:
    """An internal check of the patient walk: a mistake in synthtwin, never the description's."""
    return errors.ProfileError(
        f"synthtwin internal check: the patient walk {detail}. This means a "
        "mistake in synthtwin; please report it. Nothing has been written."
    )


def _grain_of(profile: contract.Profile) -> contract.PatientGrain:
    grain = profile.relationships.grain
    if grain is None:
        raise _internal("was asked for a twin of a description with no patient layer")
    return grain


# -- what the walk draws ---------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class DrawPlan:
    """How many words the walk asks of the stream, from the description alone (G16.17).

    `rows` the tabled rows and `patients` the patients the census counts;
    `families` one entry a row family in `grain.rows` order, True where its
    child has an own-mean parent (four words a patient); `trend` one entry a
    trend column in `grain.grid` order: two words a proposal, thirty a
    patient of its published cells; `words` the walk's words in all.
    """

    rows: int
    patients: int
    families: "tuple[bool, ...]"
    trend: "tuple[int, ...]"
    words: int
    # The counting process's words (G16.19; lane GRb2-b, plan P4-D491 part
    # b), drawn after the trend's: none where no interval rule stands.
    intervals: int = 0
    # A patient's own trajectory's words (G16.20; lane GRb2-c, plan P4-D491
    # part c), drawn after the counting process's: none where no entry stands.
    trajectory: int = 0


@dataclasses.dataclass(frozen=True)
class Draws:
    """The walk's words as `generation.generate_held` drew them: each row family's hidden sums (three bytes a row), its patient words, each trend column's proposals, and every word the run drew."""

    row_sums: "tuple[chain_walk.Packed, ...]"
    patient_words: "tuple[chain_walk.Packed, ...]"
    trend_words: "tuple[chain_walk.Packed, ...]"
    words_drawn: int
    interval_words: "chain_walk.Packed | None" = None
    trajectory_words: "chain_walk.Packed | None" = None


def _own_mean_of(grain: contract.PatientGrain, source: str) -> "contract.DerivedColumn | None":
    for derived in grain.derived:
        if derived.source == source and derived.kind == patient_rules.OWN_MEAN:
            return derived
    return None


def draw_plan(profile: contract.Profile) -> DrawPlan:
    """The walk's words, counted on the description (G16.17)."""
    grain = _grain_of(profile)
    rows = grain.top_rows
    for at in range(len(grain.bands)):
        rows += (at + 1) * grain.bands[at]
    patients = contract.patient_total(grain)
    families: "list[bool]" = []
    for family in grain.rows:
        own = _own_mean_of(grain, family.child)
        families += [own is not None and any(name == own.name for name, _level in family.parents)]
    trend: "list[int]" = []
    for name, _u, _low, _top in grain.grid:
        held = 0
        for cell in grain.trend:
            if cell.column == name:
                held += _cell_patients(grain, cell)
        trend += [2 * TREND_PROPOSALS * held]
    intervals = patient_intervals.words_needed(grain, rows, patients)
    trajectory = patient_trajectory.words_needed(len(grain.trajectory), patients, rows)
    words = 3 * rows * len(families) + 4 * patients * len([one for one in families if one]) + sum(trend) + intervals + trajectory
    return DrawPlan(rows, patients, tuple(families), tuple(trend), words, intervals, trajectory)


# -- step 1: the patient table ---------------------------------------------------


@dataclasses.dataclass(frozen=True)
class PatientTable:
    """The patient table's own description, its columns' names in order, and the band labels of `r` and of each derived column."""

    profile: contract.Profile
    names: "tuple[str, ...]"
    labels: "dict[str, tuple[str, ...]]"


def _label_block(name: str, position: int, labels: "tuple[str, ...]", counts: "tuple[int, ...]") -> contract.ColumnBlock:
    """A categorical column holding each label on its count of patients, nothing absent (G8 writes each level at its count)."""
    patients = sum(counts)
    levels: "list[contract.LevelEntry]" = []
    for at in range(len(labels)):
        levels += [contract.LevelEntry(label=labels[at], count=counts[at], variants={labels[at]: counts[at]}, variants_withheld={}, shape_form_cells=0)]
    return contract.ColumnBlock(
        name=name, position=position, role=contract.ROLE_CATEGORICAL, statistical_type="categorical",
        quality_state="ok", structural_role="data", n_present=patients, n_missing=0,
        missing_by_class=contract.MissingByClass(0, 0, 0, 0, 0, 0), missing_by_source={},
        n_missing_blank=0, n_missing_withheld=0, n_distinct=len(labels), n_distinct_folded=len(labels),
        n_numeric=0, n_not_numeric=patients, n_out_of_range=0, n_contradictory=0,
        n_sentinel_candidates_unpublished=0, sentinel_verdicts=(), detection_evidence="", remarks=(),
        facts=contract.CategoricalFacts(
            levels=tuple(levels), suppressed_levels=0, suppressed_rows=0, shape_forms={},
            suppressed_numbers=contract.PooledNumbers(0, None), level_ceiling=max(len(labels), 1),
        ),
    )


def _band_labels(entry: contract.LadderEntry) -> "tuple[str, ...]":
    """`r`'s band labels as published (each band one level), or a derived column's own (`d0`, `d1`, ...)."""
    found: "list[str]" = []
    for band in entry.bands:
        level = [start for start in band if isinstance(start, tuple) and len(start) == 1]
        found += [f"{level[0][0]}" if len(band) == 1 and level else ""]
    if all(found) and len(set(found)) == len(found):
        return tuple(found)
    return tuple(f"d{at}" for at in range(len(entry.bands)))


def with_even_map(column: contract.ColumnBlock) -> contract.ColumnBlock:
    """A column whose multiplicity map the layer withheld (contract 4.6c.3 (c)), given G16.13 step 8's even map.

    Its present cells are written with its published `n_distinct` values,
    each on `floor(n_present / n_distinct)` rows or one more, the first
    `n_present mod n_distinct` values in value order taking one more; every
    other column comes back as it was.
    """
    facts = column.facts
    if not isinstance(facts, (contract.IdentifierFacts, contract.TextFacts, contract.UnrepresentableFacts)):
        return column
    if facts.n_distinct_by_occurrences or column.n_distinct <= 0 or column.n_present <= 0:
        return column
    each, more = divmod(column.n_present, column.n_distinct)
    even: "dict[str, int]" = {}
    if column.n_distinct - more > 0 and each > 0:
        even[f"{each}"] = column.n_distinct - more
    if more > 0:
        even[f"{each + 1}"] = more
    return dataclasses.replace(column, facts=dataclasses.replace(facts, n_distinct_by_occurrences=even))


def patient_table(profile: contract.Profile) -> PatientTable:
    """The patient table as a description of its own, counted in patients (G16.13 step 1)."""
    grain = _grain_of(profile)
    by_name: "dict[str, contract.ColumnBlock]" = {}
    places: "dict[str, int]" = {}
    for at in range(len(profile.columns)):
        by_name[profile.columns[at].name] = profile.columns[at]
        places[profile.columns[at].name] = at
    entries: "dict[str, contract.LadderEntry]" = {}
    for entry in grain.patient_ladder:
        entries[entry.column] = entry
    names: "list[str]" = [grain.person]
    for column in profile.columns:
        if contract.class_in(grain, column.name) == patient_rules.CLASS_FIXED:
            names += [column.name]
    blocks: "list[contract.ColumnBlock]" = []
    forms: "list[dialect.ColumnForm]" = []
    form = profile.source.dialect
    for name in names:
        blocks += [dataclasses.replace(with_even_map(by_name[name]), position=len(blocks) + 1)]
        forms += [form.columns[places[name]] if places[name] < len(form.columns) else dialect.plain_column()]
    labels: "dict[str, tuple[str, ...]]" = {}
    ladder: "list[contract.LadderEntry]" = []
    for name in names:
        if name in entries:
            ladder += [entries[name]]
    synthetic = [patient_rules.R_NAME] + [derived.name for derived in grain.derived]
    for name in synthetic:
        if name not in entries:
            continue
        found = _band_labels(entries[name])
        labels[name] = found
        blocks += [_label_block(name, len(blocks) + 1, found, entries[name].totals)]
        forms += [dialect.plain_column()]
        names += [name]
        ladder += [dataclasses.replace(entries[name], bands=tuple(((label,),) for label in found))]
    order: "dict[str, int]" = {}
    for at in range(len(names)):
        order[names[at]] = at
    plain = dataclasses.replace(
        form,
        empty_rows_leading=0,
        empty_rows_interior=0,
        empty_rows_trailing=0,
        blank_lines=(),
        columns=tuple(forms),
        row_order=dataclasses.replace(form.row_order, column=0),
    )
    chain = tuple(family for family in grain.patient_chain if family.child in order)
    relationships = dataclasses.replace(
        profile.relationships, ladder=tuple(ladder), families=len(chain), chain=chain,
        moments=None, rules=(), words=(), grain=None,
    )
    notes = tuple(note for note in profile.publication_notes if note.column in order)
    table = dataclasses.replace(
        profile,
        n_rows=contract.patient_total(grain),
        n_columns=len(blocks),
        source=dataclasses.replace(profile.source, dialect=plain, workbook=None),
        relationships=relationships,
        publication_notes=notes,
        columns=tuple(blocks),
    )
    return PatientTable(table, tuple(names), labels)


# -- step 3: the row columns -----------------------------------------------------


def row_table(profile: contract.Profile) -> contract.Profile:
    """The description whose run makes every column counted in rows (G16.13 step 3).

    The person column and the patient-fixed columns are written from the
    patient table, so here they are held empty and draw no word, as a
    computed column is. The repeated and dealt date columns are made with
    their `L0` band totals counted in rows (`grain.ladder`). No chain is
    dealt here (the row families are the walk's), no record holding
    nothing is placed and no sort runs: the twin's own form places them
    last.
    """
    grain = _grain_of(profile)
    columns: "list[contract.ColumnBlock]" = []
    for column in profile.columns:
        kind = contract.class_in(grain, column.name)
        if kind in (patient_rules.CLASS_PERSON, patient_rules.CLASS_FIXED):
            columns += [dataclasses.replace(column, computed_from=grain.person)]
        else:
            columns += [with_even_map(column)]
    form = profile.source.dialect
    plain = dataclasses.replace(
        form, empty_rows_leading=0, empty_rows_interior=0, empty_rows_trailing=0,
        row_order=dataclasses.replace(form.row_order, column=0),
    )
    relationships = dataclasses.replace(
        profile.relationships, ladder=grain.ladder, families=max(1, len(grain.rows)), chain=(),
        moments=None, rules=(), words=(), grain=None,
    )
    return dataclasses.replace(
        profile, source=dataclasses.replace(profile.source, dialect=plain),
        relationships=relationships, columns=tuple(columns),
    )


# -- reading a cell's band ---------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class _Reading:
    """A column read into its `L0` bands as the profile's reader reads the twin's text (method G16.0 (h)).

    An absent cell (nothing but spaces, or a spelling the column or the
    table declares absent) stands in the band holding `missing`; a label
    column's cell in its level's band (a withheld level's stand-in in the
    pool); every other present cell by its role's reading into the range
    its published edges cut, `other` (or `labels`) where it holds none,
    each kind no band holds joined as `generation._group_l0_bands` joins it.
    """

    facts: object
    comma: bool
    holes: "frozenset[str]"
    where: "dict[object, int]"
    ranges: "tuple[object, ...]"
    edges: "tuple[object, ...]"
    levels: "dict[str, int]"
    labels: "tuple[str, ...]"
    joined: "dict[object, int]"


def _reading_of(profile: contract.Profile, column: contract.ColumnBlock, entry: contract.LadderEntry) -> _Reading:
    where: "dict[object, int]" = {}
    ranges: "list[object]" = []
    for place in range(len(entry.bands)):
        for start in entry.bands[place]:
            where[start] = place
            if isinstance(start, tuple) and len(start) == 2:
                ranges += [start]
    facts = column.facts
    levels: "dict[str, int]" = {}
    labels: "list[str]" = []
    order: "list[object]" = [chain_rules.OTHER, chain_rules.LABELS, chain_rules.MISSING] + ranges
    if isinstance(facts, contract.LabelFacts):
        for at in range(len(facts.levels)):
            level = facts.levels[at]
            labels += [level.label]
            levels[level.label] = at
            for variant in level.variants:
                if variant not in levels:
                    levels[variant] = at
        order = [chain_rules.MISSING]
        for band in entry.bands:
            for start in band:
                if isinstance(start, tuple):
                    order += [start]
        order += ["held back"]
    joined: "dict[object, int]" = {}
    for kind in (chain_rules.OTHER, chain_rules.LABELS, chain_rules.MISSING, "held back"):
        if kind in where:
            joined[kind] = where[kind]
            continue
        at = len(order)
        for place in range(len(order)):
            if order[place] == kind:
                at = place
        found = -1
        for later in order[at + 1:]:
            if later in where:
                found = where[later]
                break
        if found < 0:
            for earlier in reversed(order[:at]):
                if earlier in where:
                    found = where[earlier]
                    break
        joined[kind] = found
    return _Reading(
        facts,
        generation.declared_a_decimal_comma(column, profile),
        frozenset(generation.holes_reserved(column, generation.every_hole_spelling(profile))),
        where,
        tuple(ranges),
        generation.reader_edges(column, entry) if ranges else (),
        levels,
        tuple(labels),
        joined,
    )


def _absent(reading: _Reading, text: str) -> bool:
    """Whether the cell holds no value of the column."""
    return dialect.holds_nothing(text) or text in reading.holes


def _joined_band(reading: _Reading, kind: object) -> int:
    band = reading.joined[kind] if kind in reading.joined else -1
    if band < 0:
        raise _internal("read a cell that stands in no band of its ladder")
    return band


def _read(reading: _Reading, text: str) -> "tuple[int, float | str | None]":
    """The cell's `L0` band, and its reading of the band's order (a number, a clock's ordinal, a date's canonical text) or None."""
    if _absent(reading, text):
        return _joined_band(reading, chain_rules.MISSING), None
    if isinstance(reading.facts, contract.LabelFacts):
        if text in reading.levels:
            level = reading.levels[text]
            key = (reading.labels[level],)
            if key in reading.where:
                return reading.where[key], float(level)
        return _joined_band(reading, "held back"), None
    kind, value = generation.reader_reading(reading.facts, text, reading.comma)
    if kind == "value" and reading.ranges and isinstance(value, (int, float, str)) and not isinstance(value, bool):
        start = reading.ranges[chain_rules.band_of_value(reading.edges, value)]
        return reading.where[start], value if isinstance(value, str) else float(value)
    return _joined_band(reading, kind if kind in (chain_rules.OTHER, chain_rules.LABELS) else chain_rules.OTHER), None


# -- the patients ------------------------------------------------------------------


@dataclasses.dataclass
class _Patients:
    """The patient table as the walk left it: each patient's cells and `L0` band codes, in patient order."""

    count: int
    cells: "dict[str, list[str]]"
    codes: "dict[str, list[int]]"
    r: "list[int]"
    start: "list[int]"


def _patients_read(table: PatientTable, made: "generation.Twin") -> _Patients:
    """Each patient's cells and its `L0` band in every column of the patient chain."""
    held = made.held_columns if made.held_columns is not None else ()
    count = table.profile.n_rows
    cells: "dict[str, list[str]]" = {}
    codes: "dict[str, list[int]]" = {}
    entries: "dict[str, contract.LadderEntry]" = {}
    for entry in table.profile.relationships.ladder:
        entries[entry.column] = entry
    for at in range(len(table.names)):
        name = table.names[at]
        column = twinstore.column_cells(held[at])
        if len(column) != count:
            raise _internal("made a patient table of another length")
        if name in table.labels:
            place: "dict[str, int]" = {}
            for band in range(len(table.labels[name])):
                place[table.labels[name][band]] = band
            codes[name] = [place[cell] for cell in column]
            continue
        cells[name] = column
        if name in entries:
            reading = _reading_of(table.profile, table.profile.columns[at], entries[name])
            codes[name] = [_read(reading, cell)[0] for cell in column]
    return _Patients(count, cells, codes, [], [])


# -- G16.14: r, and the top band ------------------------------------------------------


def straight_line(q: int, m: int) -> "list[int]":
    """G16.14's excess line: the `i`-th of `m` patients takes `floor(q (2 m - 2 i - 1) / m^2)`, then one unit in turn from the largest until they sum to `q`."""
    if m <= 0:
        return []
    values = [(q * (2 * m - 2 * i - 1)) // (m * m) for i in range(m)]
    total = sum(values)
    at = 0
    while total < q:
        values[at % m] += 1
        total += 1
        at += 1
    at = 0
    while total > q:
        if values[at % m] > 0:
            values[at % m] -= 1
            total -= 1
        at += 1
    return values


def excess_split(targets: "list[fractions.Fraction]", total: int) -> "list[int]":
    """Whole `q_C >= 0` summing to `total`, the least `sum |q_C - t_C|`, and among those the lexicographically least (G16.14).

    `|q - t|` is convex in `q`, so a least sum takes the cheapest units
    first: every unit up to `floor(t_C)` (each lowers the sum by one),
    then the unit up to `ceil(t_C)` (each changes it by `1 - 2 frac`),
    then units anywhere (each raises it by one). Where several cells tie
    for the units left, the LATER cells take them, which leaves each
    earlier `q_C` at its least value over the minimisers.
    """
    floors: "list[int]" = []
    for target in targets:
        floors += [target.numerator // target.denominator if target >= 0 else 0]
    out = [0 for _target in targets]
    left = total
    for at in range(len(targets) - 1, -1, -1):
        take = min(floors[at], left)
        out[at] = take
        left -= take
    if left <= 0:
        return out
    ranked = sorted((floors[at] - targets[at], -at) for at in range(len(targets)) if targets[at] > floors[at])
    for _gain, place in ranked:
        if left <= 0:
            break
        out[-place] += 1
        left -= 1
    if left > 0 and out:
        out[len(out) - 1] += left
    return out


def _level_map(entry: contract.LadderEntry, level: int) -> "list[int]":
    """Each `L0` band's band at `level` (0 the identity)."""
    if level == 0:
        return list(range(len(entry.bands)))
    grouped = entry.l1 if level == 1 else entry.l2
    out = [0 for _band in entry.bands]
    for band in range(len(grouped)):
        for place in grouped[band]:
            out[place] = band
    return out


def _parent_cells(patients: _Patients, parents: "tuple[tuple[str, int], ...]", entries: "dict[str, contract.LadderEntry]") -> "tuple[list[int], int]":
    """Each patient's parent cell of a family whose parents are patient-table columns, and the number of cells (the last parent fastest)."""
    cells = [0 for _patient in range(patients.count)]
    width = 1
    for name, level in parents:
        maps = _level_map(entries[name], level)
        size = max(maps) + 1 if maps else 1
        codes = patients.codes[name]
        for patient in range(patients.count):
            cells[patient] = cells[patient] * size + maps[codes[patient]]
        width = width * size
    return cells, width


def _grouped(keys: "list[int]", members: "list[int]") -> "dict[int, list[int]]":
    """`members` grouped by their key, each group in the members' order."""
    out: "dict[int, list[int]]" = {}
    for member in members:
        key = keys[member]
        if key in out:
            out[key] += [member]
        else:
            out[key] = [member]
    return out


def _r_values(grain: contract.PatientGrain, patients: _Patients, labels: "tuple[str, ...]", entries: "dict[str, contract.LadderEntry]") -> "tuple[list[int], list[str]]":
    """Each patient's `r` from the census (G16.14): a value below `lo` as its band says, the top band's excess by the straight line.

    With no row family, one straight line over the whole top band in
    patient order. Where a row family stands, each grain cell's total
    excess `q_C` meets the finest row family's parent row totals, split by
    `excess_split` inside its parent cells, then the line inside each
    grain cell. The second item names any family whose parent row totals
    the split leaves unmet (a deviation).
    """
    value_of: "list[int]" = []
    for label in labels:
        value_of += [_whole_text(label)]
    bands = patients.codes[patient_rules.R_NAME] if patient_rules.R_NAME in patients.codes else [0 for _p in range(patients.count)]
    r = [0 for _p in range(patients.count)]
    top: "list[int]" = []
    for patient in range(patients.count):
        value = value_of[bands[patient]] if value_of else -1
        if value < 0:
            if grain.top_patients <= 0 and grain.bands:
                value = len(grain.bands)
            else:
                top += [patient]
                value = grain.lo
        r[patient] = value
    missed: "list[str]" = []
    m = len(top)
    q = grain.top_rows - grain.lo * m
    if m == 0:
        return r, missed
    if not grain.rows:
        line = straight_line(q, m)
        for at in range(m):
            r[top[at]] += line[at]
        return r, missed
    family = grain.patient_chain[grain.grain_family] if grain.grain_family is not None and grain.grain_family < len(grain.patient_chain) else None
    members: "list[tuple[str, int]]" = []
    if family is not None:
        for name, level in list(family.parents) + [(family.child, family.level)]:
            if name in patients.codes:
                members += [(name, level)]
    grain_cell = _parent_cells(patients, tuple(members), entries)[0] if members else [0 for _p in range(patients.count)]
    finest_of: "list[int]" = []
    finest_cells = -1
    finest_table: "tuple[tuple[int, ...], ...]" = ()
    finest_child = ""
    for row in grain.rows:
        cells, count = _parent_cells(patients, row.parents, entries)
        if count > finest_cells:
            finest_of, finest_cells, finest_table, finest_child = cells, count, row.table, row.child
    owed = [sum(line) for line in finest_table]
    is_top = [False for _p in range(patients.count)]
    for patient in top:
        is_top[patient] = True
    for patient in range(patients.count):
        cell = finest_of[patient]
        if cell < len(owed):
            owed[cell] -= r[patient]
    top_in = _grouped(finest_of, top)
    for cell in sorted(top_in):
        need = owed[cell] if cell < len(owed) else 0
        if need < 0:
            missed += [finest_child]
            need = 0
        by_grain = _grouped(grain_cell, top_in[cell])
        order = sorted(by_grain)
        targets = [fractions.Fraction(q * len(by_grain[one]), m) for one in order]
        split = excess_split(targets, need)
        for at in range(len(order)):
            here = by_grain[order[at]]
            line = straight_line(split[at], len(here))
            for place in range(len(here)):
                r[here[place]] += line[place]
    for row in grain.rows:
        cells, _count = _parent_cells(patients, row.parents, entries)
        held = [0 for _line in row.table]
        for patient in range(patients.count):
            if cells[patient] < len(held):
                held[cells[patient]] += r[patient]
        if held != [sum(line) for line in row.table]:
            missed += [row.child]
    return r, missed


def _whole_text(text: str) -> int:
    """A label written as a whole number of digits, else -1 (`r`'s single values; its top band reads -1)."""
    if not isinstance(text, str) or not text:
        return -1
    value = 0
    for character in text:
        if character < "0" or character > "9":
            return -1
        value = value * 10 + (ord(character) - ord("0"))
    return value


# -- G16.15: the patient scores and the weight --------------------------------------


def patient_scores(sums: "list[int]", places: "list[int]", bands: "list[int]") -> "list[float]":
    """Each patient's score `z_p` (G16.15): the `N` hidden scores, sorted (stable on patient order), dealt to the patients sorted by band, then word 4, then patient order."""
    count = len(sums)
    ordered = sorted((sums[patient], patient) for patient in range(count))
    takers = sorted((bands[patient], places[patient], patient) for patient in range(count))
    out = [0.0 for _patient in range(count)]
    for rank in range(count):
        out[takers[rank][2]] = chain_walk.hidden_score(ordered[rank][0])
    return out


def omega_of(table: "list[list[int]]", own_shares: "list[int]", steps: int = OMEGA_STEPS, points_a_band: int = OMEGA_POINTS) -> float:
    """The patient weight `omega` (G16.15): the grid point of greatest multinomial likelihood of a published (own-mean band, child band) table.

    `table[a][b]` holds the rows of own-mean band `a` in band `b` of the
    child, pooled over the other parents; `own_shares[a]` the patients of
    own-mean band `a`. The own-mean score is uniform on each band's share
    of patients (24 equal quantile points a band), the child's edges at
    the normal quantiles of its row shares; each reading is `omega z +
    sqrt(1 - omega^2) e`. The grid points are tried in ascending order, a
    tie keeping the smaller. Every quantile, logarithm and normal
    distribution value is the shared module's.
    """
    patients = sum(own_shares)
    bands = len(table[0]) if table else 0
    rows = 0
    for line in table:
        rows += sum(line)
    if patients <= 0 or rows <= 0 or bands < 2 or len(table) < 2:
        return 0.0
    column = [0 for _b in range(bands)]
    for line in table:
        for b in range(bands):
            column[b] += line[b]
    edges: "list[float]" = []
    running = 0
    for b in range(bands - 1):
        running += column[b]
        edges += [chain_walk.normal_score(running / rows) if 0 < running < rows else (-8.0 if running <= 0 else 8.0)]
    points: "list[list[float]]" = []
    below = 0
    for a in range(len(table)):
        share = own_shares[a]
        here: "list[float]" = []
        for k in range(points_a_band):
            p = (below + share * (2 * k + 1) / (2 * points_a_band)) / patients
            here += [chain_walk.normal_score(p) if 0.0 < p < 1.0 else 0.0]
        points += [here]
        below += share
    best = 0.0
    best_value = 0.0
    found = False
    for step in range(steps):
        omega = step * OMEGA_STEP
        noise = math.sqrt(1.0 - omega * omega)
        value = 0.0
        broken = False
        for a in range(len(table)):
            if sum(table[a]) <= 0:
                continue
            chance = [0.0 for _b in range(bands)]
            for z in points[a]:
                last = 0.0
                for b in range(bands - 1):
                    cut = chain_walk.normal_cdf((edges[b] - omega * z) / noise)
                    chance[b] = chance[b] + (cut - last)
                    last = cut
                chance[bands - 1] = chance[bands - 1] + (1.0 - last)
            for b in range(bands):
                if table[a][b] <= 0:
                    continue
                p = chance[b] / points_a_band
                if p <= 0.0:
                    broken = True
                    break
                value = value + table[a][b] * chain_walk.natural_log(p)
            if broken:
                break
        if broken:
            continue
        if not found or value > best_value:
            best_value = value
            best = omega
            found = True
    return best


# -- step 4: the row families -------------------------------------------------------


@dataclasses.dataclass
class _Rows:
    """The tabled rows: each one's patient and position, and each row column's cells in tabled order."""

    patient: "list[int]"
    position: "list[int]"
    # Each row column HELD (`twinstore`): one column is text objects at a
    # time, never the twin whole (G16.17's memory, lane SG's held twin).
    cells: "dict[str, twinstore.HeldColumn]"
    spare: "dict[str, list[str]]"


def _ordered_bands(entry: contract.LadderEntry, maps: "list[int]", bands: int) -> "list[bool]":
    """Whether each band at a level holds a value band (a range, a level or the pool): ORDERED, else SPREAD (contract 4.6b.2)."""
    out = [False for _band in range(bands)]
    for place in range(len(entry.bands)):
        if any(generation.value_start(start) for start in entry.bands[place]):
            out[maps[place]] = True
    return out


def _deal_family(
    child_cells: "list[str]",
    reading: _Reading,
    entry: contract.LadderEntry,
    level: int,
    parent_of_row: "list[int]",
    parent_count: int,
    latent: "list[float]",
    published: "tuple[tuple[int, ...], ...]",
) -> "tuple[list[str], bool]":
    """One row family dealt (G16.2 steps 3 and 4 inside each parent cell): the child's cells in their new rows, and whether the target moved.

    The child's CELL LIST at the family's level: its cells band by band,
    each band's cells holding a reading sorted by it, then the others in
    their order (G16.2 step 4).
    """
    maps = _level_map(entry, level)
    bands = max(maps) + 1 if maps else 1
    banded: "list[list[tuple[float | str, int]]]" = [[] for _band in range(bands)]
    others: "list[list[int]]" = [[] for _band in range(bands)]
    for place in range(len(child_cells)):
        l0, value = _read(reading, child_cells[place])
        band = maps[l0]
        if value is None:
            others[band] += [place]
        else:
            banded[band] += [(value, place)]
    listed: "list[int]" = []
    sizes: "list[int]" = []
    read: "list[int]" = []
    for band in range(bands):
        listed += [place for _value, place in sorted(banded[band])] + others[band]
        sizes += [len(banded[band]) + len(others[band])]
        read += [len(banded[band])]
    counts = [0 for _cell in range(parent_count)]
    for cell in parent_of_row:
        counts[cell] += 1
    target = chain_walk.target_of(published, counts, sizes)
    order = [row for _value, row in sorted((latent[row], row) for row in range(len(latent)))]
    dealt = chain_walk.deal(parent_of_row, parent_count, order, chain_walk.ChildBands(tuple(sizes), tuple(read), tuple(_ordered_bands(entry, maps, bands))), target.table)
    out = ["" for _row in child_cells]
    for row in range(len(child_cells)):
        out[row] = child_cells[listed[chain_walk.read_code(dealt.index, dealt.index_width, row)]]
    return out, target.moved


# -- G16.15: the trend -----------------------------------------------------------------


def _label_parts(label: str) -> "tuple[str, str]":
    """A trend cell's label `name=value` as its two parts."""
    if not isinstance(label, str):
        raise TypeError("a label is text")
    at = len(label) - 1
    while at >= 0 and label[at] != "=":
        at -= 1
    if at < 0:
        return label, ""
    return label[:at], label[at + 1:]


def trend_levels(grain: contract.PatientGrain, names: "list[str]") -> "dict[str, int]":
    """Each member's level in `F_S`, the first family of the patient chain holding `r` and every member a trend cell names (contract 4.6c.1 (a))."""
    for family in grain.patient_chain:
        held: "dict[str, int]" = {}
        for name, level in family.parents:
            held[name] = level
        held[family.child] = family.level
        if all(name in held for name in names):
            return held
    return {}


def _cell_patients(grain: contract.PatientGrain, cell: contract.TrendCell) -> int:
    """A published trend cell's patients, read on the published `F_S` table (G16.17's proposal count)."""
    want: "dict[str, str]" = {}
    for label in cell.cell:
        name, value = _label_parts(label)
        want[name] = value
    names = [name for name in want]
    for family in grain.patient_chain:
        members = list(family.parents) + [(family.child, family.level)]
        held = [name for name, _level in members]
        if not all(name in held for name in names):
            continue
        entries: "dict[str, contract.LadderEntry]" = {}
        for entry in grain.patient_ladder:
            entries[entry.column] = entry
        sizes = [max(_level_map(entries[name], level)) + 1 for name, level in members if name in entries]
        if len(sizes) != len(members):
            return 0
        total = 0
        for line_at in range(len(family.table)):
            for band in range(len(family.table[line_at])):
                parts: "list[int]" = []
                rest = line_at
                for size in reversed(sizes[:len(sizes) - 1]):
                    parts = [rest % size] + parts
                    rest = rest // size
                parts += [band]
                same = True
                for place in range(len(members)):
                    name = members[place][0]
                    if name not in want:
                        continue
                    label = f"{parts[place]}"
                    if name == patient_rules.R_NAME:
                        label = _level_label(entries[name], parts[place])
                    if label != want[name]:
                        same = False
                if same:
                    total += family.table[line_at][band]
        return total
    return 0


def _level_label(entry: contract.LadderEntry, band: int) -> str:
    """The label of a band holding one level (`r`'s bands), "" for any other band."""
    if band >= len(entry.bands) or len(entry.bands[band]) != 1:
        return ""
    start = entry.bands[band][0]
    if isinstance(start, tuple) and len(start) == 1:
        return f"{start[0]}"
    return ""


@dataclasses.dataclass(frozen=True)
class _Grid:
    """A trend column's grid code (contract 4.6c's setting), from its published decimal texts."""

    u: str
    low: str
    top: int


def exact_meaning(profile: contract.Profile, column: contract.ColumnBlock, cells: "list[str]") -> "dict[str, fractions.Fraction | None]":
    """Each distinct spelling of a column read ONCE, exactly, as the profile's reader reads it (repair 1 of lane GRb, the first skeptic's item 1).

    The reader is the deal's (`generation.reader_reading`, contract
    4.6b.2's): a unit word or letter, a declared decimal comma beside a
    thousands mark, a leading plus are read as the profiler reads them,
    and the number it gives is written in its shortest decimal
    (`patient_rules.exact_number`), as the validator's `exact_readings`
    and the producer read a cell (`patient_rules.reading_of`). None for an
    absent cell (nothing but spaces, or a spelling the column or the table
    declares absent) and for one holding no number. Never a character
    filter: the closes read `6.6 mmol` as 6.6, as the deal does.
    """
    comma = generation.declared_a_decimal_comma(column, profile)
    holes = frozenset(generation.holes_reserved(column, generation.every_hole_spelling(profile)))
    facts = column.facts
    out: "dict[str, fractions.Fraction | None]" = {}
    for text in cells:
        if text in out:
            continue
        value: "fractions.Fraction | None" = None
        if not (dialect.holds_nothing(text) or text in holes) and not isinstance(facts, contract.LabelFacts):
            kind, found = generation.reader_reading(facts, text, comma)
            if kind == "value" and isinstance(found, float) and math.isfinite(found):
                value = patient_rules.exact_number(found)
        out[text] = value
    return out


def grid_code(grid: _Grid, value: "fractions.Fraction | None") -> int:
    """A reading's grid code (`patient_rules.grid_code_of`, as the validator codes it); 0 for a cell holding no number."""
    return patient_rules.grid_code_of(grid.u, grid.low, grid.top, value)


def _whole_gcd(first: int, second: int) -> int:
    """The greatest common divisor of two whole numbers (Euclid's)."""
    while second:
        first, second = second, first % second
    return first


@dataclasses.dataclass(frozen=True)
class _Published:
    """One published `Q_P` as the twin's patients hold it: the patients, `q` and `r`."""

    patients: "tuple[int, ...]"
    q: int
    rho: int


def _trend_targets(
    grain: contract.PatientGrain,
    column: str,
    u: float,
    patients: _Patients,
    entries: "dict[str, contract.LadderEntry]",
) -> "tuple[list[float], list[_Published]]":
    """Each patient's target slope `mu_p` in the column's units, and each published cell as the twin's patients hold it (G16.15).

    A patient of a cell of `F_S` carrying `Q_P` takes `(2 Q_P + h) u / (2
    |P| Sxx(r))`; every other patient of two rows or more takes the
    EXTENSION, the pooled slope over the published cells sharing its
    labels but `r`, else its first label, else every published cell; with
    no published cell, 0. A cell's labels name `r` by its value and every
    other member of `F_S` by its band's place at `F_S`'s level of it.
    """
    targets = [0.0 for _patient in range(patients.count)]
    published: "list[_Published]" = []
    cells = [cell for cell in grain.trend if cell.column == column]
    if not cells:
        return targets, published
    names: "list[str]" = []
    for cell in cells:
        for label in cell.cell:
            name = _label_parts(label)[0]
            if name not in names:
                names += [name]
    levels = trend_levels(grain, names)
    keys: "list[tuple[str, ...]]" = []
    rests: "list[tuple[str, ...]]" = []
    for patient in range(patients.count):
        key_parts: "list[str]" = []
        rest_parts: "list[str]" = []
        for name in names:
            if name == patient_rules.R_NAME:
                key_parts += [f"{name}={patients.r[patient]}"]
                continue
            label = f"{name}=?"
            if name in patients.codes and name in entries:
                label = f"{name}={_level_map(entries[name], levels[name] if name in levels else 0)[patients.codes[name][patient]]}"
            key_parts += [label]
            rest_parts += [label]
        keys += [tuple(key_parts)]
        rests += [tuple(rest_parts)]
    members: "dict[tuple[str, ...], list[int]]" = {}
    for patient in range(patients.count):
        if keys[patient] in members:
            members[keys[patient]] += [patient]
        else:
            members[keys[patient]] = [patient]
    pooled_num: "dict[tuple[str, ...], float]" = {}
    pooled_den: "dict[tuple[str, ...], float]" = {}
    every_num = 0.0
    every_den = 0.0
    carried = [False for _patient in range(patients.count)]
    for cell in cells:
        want: "dict[str, str]" = {}
        for label in cell.cell:
            name, value = _label_parts(label)
            want[name] = value
        key = tuple(f"{name}={want[name] if name in want else '?'}" for name in names)
        rest = tuple(f"{name}={want[name] if name in want else '?'}" for name in names if name != patient_rules.R_NAME)
        found = members[key] if key in members else []
        rho = _whole_text(want[patient_rules.R_NAME]) if patient_rules.R_NAME in want else -1
        if not found or rho < 2:
            continue
        h = 0.5 if rho % 2 == 0 else 0.0
        sxx = (rho * rho * rho - rho) / 12.0
        slope = (2 * cell.q + h) * u / (2 * len(found) * sxx)
        for patient in found:
            targets[patient] = slope
            carried[patient] = True
        published += [_Published(tuple(found), cell.q, rho)]
        pooled_num[rest] = (pooled_num[rest] if rest in pooled_num else 0.0) + (2 * cell.q + h) * u
        pooled_den[rest] = (pooled_den[rest] if rest in pooled_den else 0.0) + 2 * len(found) * sxx
        every_num += (2 * cell.q + h) * u
        every_den += 2 * len(found) * sxx
    for patient in range(patients.count):
        if carried[patient] or patients.r[patient] < 2:
            continue
        rest = rests[patient]
        if rest in pooled_den and pooled_den[rest] > 0:
            targets[patient] = pooled_num[rest] / pooled_den[rest]
            continue
        num = 0.0
        den = 0.0
        for other in pooled_den:
            if rest and other and other[0] == rest[0]:
                num += pooled_num[other]
                den += pooled_den[other]
        if den > 0:
            targets[patient] = num / den
        elif every_den > 0:
            targets[patient] = every_num / every_den
    return targets, published


def _slope_of(values: "list[float]") -> float:
    """A patient's least-squares slope of its values on positions 1 .. r."""
    count = len(values)
    if count < 2:
        return 0.0
    middle = (count + 1) / 2.0
    sxx = (count * count * count - count) / 12.0
    total = 0.0
    for j in range(count):
        total += values[j] * (j + 1 - middle)
    return total / sxx


def _s_of(codes: "list[int]") -> int:
    """A patient's `sum_j c_j (2 j - r - 1)` (contract 4.6c.1)."""
    count = len(codes)
    total = 0
    for j in range(count):
        total += codes[j] * (2 * (j + 1) - count - 1)
    return total


def _robust_scale(column: contract.ColumnBlock) -> float:
    """A column's published robust scale: its interquartile range over 1.349, read from its rungs (G16.15), else 0."""
    facts = column.facts
    if not isinstance(facts, contract.NumericFacts):
        return 0.0
    low = generation.rung_by_key(facts, "p25")
    high = generation.rung_by_key(facts, "p75")
    if low is None or high is None:
        return 0.0
    return (high - low) / 1.349


def _with_trend(latent: "list[float]", targets: "list[float]", gamma: float, rows: _Rows, r_values: "list[int]") -> "list[float]":
    """The walk's score plus the trend term `gamma mu_p (j - (r_p + 1) / 2)` (G16.15)."""
    out = list(latent)
    for row in range(len(out)):
        patient = rows.patient[row]
        mu = targets[patient]
        if mu != 0.0:
            out[row] = out[row] + gamma * mu * (rows.position[row] - (r_values[patient] + 1) / 2.0)
    return out


def _response(cells: "list[str]", targets: "list[float]", patients: _Patients, reading: _Reading) -> float:
    """The least-squares slope of each patient's achieved slope on its target slope, over every patient with a target (G16.15's `beta`)."""
    num = 0.0
    den = 0.0
    for patient in range(patients.count):
        mu = targets[patient]
        if mu == 0.0:
            continue
        begin = patients.start[patient]
        values: "list[float]" = []
        for row in range(begin, begin + patients.r[patient]):
            value = _read(reading, cells[row])[1]
            values += [value if isinstance(value, float) else 0.0]
        num += _slope_of(values) * mu
        den += mu * mu
    return num / den if den > 0 else 0.0


def _sorted_within(cells: "list[str]", reading: _Reading, patients: _Patients) -> "list[str]":
    """A dealt date column with each patient's dates sorted ascending (G16.13 step 5), its absent cells after them in row order."""
    out = list(cells)
    for patient in range(patients.count):
        begin = patients.start[patient]
        end = begin + patients.r[patient]
        present: "list[tuple[float | str, int, str]]" = []
        absent: "list[str]" = []
        for row in range(begin, end):
            value = _read(reading, cells[row])[1]
            if value is None:
                absent += [cells[row]]
            else:
                present += [(value, row, cells[row])]
        placed = [cell for _value, _row, cell in sorted(present)] + absent
        for at in range(len(placed)):
            out[begin + at] = placed[at]
    return out


# -- step 6: the derived columns' close ------------------------------------------------


def _scaled(cells: "list[str]", meaning: "dict[str, fractions.Fraction | None]") -> "tuple[list[int | None], int]":
    """Each cell's exact reading (`exact_meaning`) as a whole number of the column's finest step, and that step's scale: the least common multiple of the readings' denominators, so every reading is whole exactly."""
    scale = 1
    for spelling in meaning:
        read = meaning[spelling]
        if read is not None:
            scale = scale * read.denominator // _whole_gcd(scale, read.denominator)
    out: "list[int | None]" = []
    for text in cells:
        value = meaning[text]
        out += [None if value is None else value.numerator * (scale // value.denominator)]
    return out, scale


def _ceiling(value: fractions.Fraction) -> int:
    """The least whole number at or above an exact fraction."""
    return -((-value.numerator) // value.denominator)


@dataclasses.dataclass(frozen=True)
class _MeanClose:
    """What an own-mean close did: the patients left outside their bands, the exchanges of rows in the order made, whether a work bound ended it, and its row reads."""

    left: int
    exchanges: "tuple[tuple[int, int], ...]"
    bounded: bool
    reads: int


def _own_mean_close(
    rows: _Rows,
    profile: contract.Profile,
    column: contract.ColumnBlock,
    derived: contract.DerivedColumn,
    patients: _Patients,
    parent_of_patient: "list[int]",
) -> _MeanClose:
    """G16.15's own-mean close on the twin's rows: the source's cells read once (`exact_meaning`), closed by `mean_close`, each exchange made on the cells."""
    source = column.name
    cells = twinstore.column_cells(rows.cells[source])
    values, scale = _scaled(cells, exact_meaning(profile, column, cells))
    done = mean_close(values, scale, [fractions.Fraction(edge) for edge in derived.edges], patients.codes[derived.name],
                      rows.patient, patients, parent_of_patient)
    for row, other_row in done.exchanges:
        cells[row], cells[other_row] = cells[other_row], cells[row]
    rows.cells[source] = twinstore.held_column(cells)
    return done


def mean_close(
    values: "list[int | None]",
    scale: int,
    edges: "list[fractions.Fraction]",
    wanted: "list[int]",
    owner: "list[int]",
    patients: _Patients,
    parent_of_patient: "list[int]",
) -> _MeanClose:
    """G16.15's own-mean close: exchanges of the source's readings between two patients of one parent cell.

    `values` holds each row's reading as a whole number of the column's
    finest step (`scale` steps a unit; None where the row holds no
    number), `owner` each row's patient, `wanted` each patient's band of
    the published `edges` (the one the patient table's walk dealt it).
    Each patient's own mean is read EXACTLY: patient `p` is inside its band
    while its sum lies in `[low_p, high_p]`, an open end of the lowest or
    the highest band held past every sum the readings can make (repair 2 of
    lane GRb, Codex's item 2: a finite stand-in for it, 2 ** 62, left the
    band empty once the finest step reached `10 ** -19`). In patient order,
    a patient outside proposes its rows, the lowest reading first where its
    sum must rise (the highest where it must fall), against the rows of the
    other patients of its parent cell: the exchange taken is the one of the
    nearest reading that brings its sum into its band (searched from the
    patient's side outward, whether its sum must rise or fall), else the
    one moving it farthest toward it, in either case only where the other
    patient's sum stays inside its band (or moves toward it without
    passing it). Each of the parent cell's (cell, band) counts keeps its
    rows, so every row family's table and every count of one column is
    kept. At most four passes, within the total-work bound
    (`CLOSE_VISITS`, `CLOSE_WORK`); a patient's rows are kept in their
    order as they change, never sorted again a proposal.
    """
    count = patients.count
    sums = [0 for _p in range(count)]
    counts = [0 for _p in range(count)]
    far = 1
    for row in range(len(values)):
        value = values[row]
        if value is not None:
            sums[owner[row]] += value
            counts[owner[row]] += 1
            far += value if value >= 0 else -value
    lows = [0 for _p in range(count)]
    highs = [0 for _p in range(count)]
    for p in range(count):
        band = wanted[p]
        lows[p] = _ceiling(edges[band - 1] * counts[p] * scale) if band > 0 else -far
        highs[p] = _ceiling(edges[band] * counts[p] * scale) - 1 if band < len(edges) else far
    by_cell = _grouped(parent_of_patient, list(range(count)))
    exchanges: "list[tuple[int, int]]" = []
    state = _CloseState(sums, lows, highs, values, {}, [], [], owner, 0, 0, CLOSE_WORK * len(values), 0)
    for _pass in range(CLOSE_PASSES):
        changed = False
        for cell in by_cell:
            members = by_cell[cell]
            outside = [p for p in members if counts[p] > 0 and not lows[p] <= sums[p] <= highs[p]]
            if not outside:
                continue
            pool: "list[int]" = []
            for other in members:
                begin = patients.start[other]
                for row in range(begin, begin + patients.r[other]):
                    if values[row] is not None:
                        pool += [row]
            pool = [row for _value, row in sorted((values[row], row) for row in pool)]
            slot: "dict[int, int]" = {}
            keys: "list[int]" = []
            for at in range(len(pool)):
                slot[pool[at]] = at
                value = values[pool[at]]
                keys += [value if value is not None else 0]
            state.slot, state.pool, state.keys = slot, pool, keys
            for p in outside:
                if not counts[p] or lows[p] <= sums[p] <= highs[p]:
                    continue
                # THE PATIENT'S ROWS IN THEIR ORDER, kept as its readings change
                # (Codex's item 3): sorted once a pass, each exchange moving one row.
                rising = sums[p] < lows[p]
                begin = patients.start[p]
                mine = sorted((value if rising else -value, row) for row in range(begin, begin + patients.r[p]) for value in (values[row],) if value is not None)
                state.visits = 0
                state.allowed = CLOSE_VISITS * patients.r[p]
                while not lows[p] <= sums[p] <= highs[p]:
                    moved = _one_exchange(p, state, mine)
                    if moved is None:
                        break
                    row, other_row = moved
                    exchanges += [moved]
                    changed = True
                    left_value = values[other_row]
                    came = values[row]
                    if left_value is not None and came is not None:
                        del mine[_rows_below(mine, (left_value if rising else -left_value, row))]
                        moving = (came if rising else -came, row)
                        place = _rows_below(mine, moving)
                        mine[place:place] = [moving]
        if not changed or state.bounded == 2:
            break
    left = 0
    for p in range(count):
        if counts[p] > 0 and not lows[p] <= sums[p] <= highs[p]:
            left += 1
    return _MeanClose(left, tuple(exchanges), state.bounded > 0, state.reads)


@dataclasses.dataclass
class _CloseState:
    """The own-mean close's state: the patients' sums and bands, the readings, one parent cell's rows sorted by reading, each row's patient, and the work spent against its bounds.

    `visits` and `allowed` are the patient's own rows visited in this pass
    and its bound; `reads` and `most` the close's row reads and its bound;
    `bounded` is 1 once a patient's bound has stopped a search, 2 once the
    close's has.
    """

    sums: "list[int]"
    lows: "list[int]"
    highs: "list[int]"
    values: "list[int | None]"
    slot: "dict[int, int]"
    pool: "list[int]"
    keys: "list[int]"
    owner: "list[int]"
    visits: int
    allowed: int
    most: int
    reads: int
    bounded: int = 0


def _first_at_or_above(keys: "list[int]", value: int) -> int:
    """How many of the sorted `keys` stand below `value` (a halving search)."""
    low = 0
    high = len(keys)
    while low < high:
        middle = (low + high) // 2
        if keys[middle] < value:
            low = middle + 1
        else:
            high = middle
    return low


def _rows_below(mine: "list[tuple[int, int]]", item: "tuple[int, int]") -> int:
    """How many of the sorted pairs `mine` stand below `item` (the same halving search over a patient's proposal order).

    The halving searches here stand in for the standard library's `bisect`,
    which the offline audit's allowlist (plan D6.2) does not name; an item
    inserted at this place leaves the list as `bisect.insort` leaves it,
    the pairs being whole numbers, so equal pairs are the same pair.
    """
    low = 0
    high = len(mine)
    while low < high:
        middle = (low + high) // 2
        if mine[middle] < item:
            low = middle + 1
        else:
            high = middle
    return low


def _one_exchange(p: int, state: _CloseState, mine: "list[tuple[int, int]]") -> "tuple[int, int] | None":
    """One exchange of the own-mean close for patient `p`, applied to the state; its two rows (the patient's first), or None.

    `mine` is the patient's rows holding a reading in its proposal order
    (the lowest reading first where its sum must rise, the highest where it
    must fall). Each of its rows visited and each partner row read counts
    against the close's bounds; a bound reached ends the search, and the
    best move found before it, if any, is taken.
    """
    sums = state.sums
    rising = sums[p] < state.lows[p]
    need = (state.lows[p] - sums[p]) if rising else (sums[p] - state.highs[p])
    room = (state.highs[p] - sums[p]) if rising else (sums[p] - state.lows[p])
    best_gain = 0
    best: "tuple[int, int] | None" = None
    for _key, row in mine:
        if state.reads >= state.most:
            state.bounded = 2
            break
        if state.visits >= state.allowed:
            state.bounded = max(state.bounded, 1)
            break
        state.visits += 1
        state.reads += 1
        v = state.values[row]
        if v is None:
            continue
        # THE NEAREST READING THAT BRINGS THE SUM INTO ITS BAND, searched from
        # the patient's side outward in both directions (repair 1 of lane
        # GRb, the statistics check's item 1): a rising patient upward from
        # `v + need`, a falling one DOWNWARD from `v - need`, so a falling
        # patient lands at its band's near edge, never its far one.
        read = 0
        if rising:
            at = _first_at_or_above(state.keys, v + need)
            while at < len(state.pool) and state.keys[at] <= v + room and read < CLOSE_PARTNERS:
                orow = state.pool[at]
                other = state.owner[orow]
                if other != p and _affords(other, v - state.keys[at], state):
                    state.reads += read + 1
                    return _applied(row, orow, p, other, state)
                at += 1
                read += 1
        else:
            at = _first_at_or_above(state.keys, v - need + 1) - 1
            while at >= 0 and state.keys[at] >= v - room and read < CLOSE_PARTNERS:
                orow = state.pool[at]
                other = state.owner[orow]
                if other != p and _affords(other, v - state.keys[at], state):
                    state.reads += read + 1
                    return _applied(row, orow, p, other, state)
                at -= 1
                read += 1
        state.reads += read
        read = 0
        if rising:
            at = _first_at_or_above(state.keys, v + need) - 1
            while at >= 0 and state.keys[at] > v and read < CLOSE_PARTNERS:
                orow = state.pool[at]
                other = state.owner[orow]
                read += 1
                if other != p and _affords(other, v - state.keys[at], state):
                    if state.keys[at] - v > best_gain:
                        best_gain = state.keys[at] - v
                        best = (row, orow)
                    break
                at -= 1
        else:
            at = _first_at_or_above(state.keys, v - need + 1)
            while at < len(state.pool) and state.keys[at] < v and read < CLOSE_PARTNERS:
                orow = state.pool[at]
                other = state.owner[orow]
                read += 1
                if other != p and _affords(other, v - state.keys[at], state):
                    if v - state.keys[at] > best_gain:
                        best_gain = v - state.keys[at]
                        best = (row, orow)
                    break
                at += 1
        state.reads += read
    if best is None:
        return None
    return _applied(best[0], best[1], p, state.owner[best[1]], state)


def _affords(other: int, change: int, state: _CloseState) -> bool:
    """Whether another patient's sum may move by `change`: it stays inside its band, or moves toward it without passing it."""
    now = state.sums[other]
    after = now + change
    if state.lows[other] <= now <= state.highs[other]:
        return state.lows[other] <= after <= state.highs[other]
    if now < state.lows[other]:
        return now < after <= state.highs[other]
    return state.lows[other] <= after < now


def _applied(row: int, orow: int, p: int, other: int, state: _CloseState) -> "tuple[int, int]":
    """Exchanges two rows' readings in the close's state; the sorted pool keeps its values, its two slots changing rows."""
    v = state.values[row]
    w = state.values[orow]
    if v is None or w is None:
        return row, orow
    state.sums[p] += w - v
    state.sums[other] += v - w
    state.values[row] = w
    state.values[orow] = v
    first = state.slot[row]
    second = state.slot[orow]
    state.pool[first] = orow
    state.pool[second] = row
    state.slot[row] = second
    state.slot[orow] = first
    return row, orow


def _first_date_close(
    rows: _Rows,
    source: str,
    reading: _Reading,
    entry: contract.LadderEntry,
    derived: contract.DerivedColumn,
    patients: _Patients,
    parent_of_patient: "list[int]",
) -> int:
    """G16.15's first-date close: exchanges of the source's dates ACROSS bands between two patients of one parent cell.

    A patient's first date is its earliest present date; its band is the
    source's band at the derived column's level, and the patient table's
    walk dealt each patient the band it must hold (`b`). A patient whose
    first date lies in another band exchanges one of its dates outside `b`
    (its earliest where that lies below `b`, else its latest) against a
    date of another patient of its parent cell lying in `b` (in `b` or
    above where its first date lies below `b`), the earliest such date
    first; an exchange is kept where it puts the patient's first date in
    `b` or nearer it and leaves the other patient's first date in its own
    band, or nearer it. The dates' (cell, band) counts keep their rows. At
    most four passes. Returns the patients left outside their bands.
    """
    cells = twinstore.column_cells(rows.cells[source])
    maps = _level_map(entry, derived.level)
    band_of = [-1 for _row in cells]
    value_of: "list[float | str | None]" = [None for _row in cells]
    for row in range(len(cells)):
        l0, value = _read(reading, cells[row])
        if value is not None:
            band_of[row] = maps[l0]
            value_of[row] = value
    wanted = patients.codes[derived.name]

    def first_band(patient: int) -> int:
        begin = patients.start[patient]
        dated = [(value_of[row], row) for row in range(begin, begin + patients.r[patient]) if value_of[row] is not None]
        return band_of[sorted(dated)[0][1]] if dated else -1

    by_cell = _grouped(parent_of_patient, list(range(patients.count)))
    for _pass in range(CLOSE_PASSES):
        changed = False
        for cell in by_cell:
            members = by_cell[cell]
            outside = [p for p in members if first_band(p) not in (-1, wanted[p])]
            if not outside:
                continue
            dated: "list[tuple[float | str, int]]" = []
            for other in members:
                begin = patients.start[other]
                for row in range(begin, begin + patients.r[other]):
                    value = value_of[row]
                    if value is not None:
                        dated += [(value, row)]
            pool = [row for _value, row in sorted(dated)]
            for p in outside:
                first = first_band(p)
                band = wanted[p]
                if first == band or first < 0:
                    continue
                begin = patients.start[p]
                mine = [row for _value, row in sorted((value_of[row], row) for row in range(begin, begin + patients.r[p]) if value_of[row] is not None and band_of[row] != band)]
                if first > band:
                    mine = mine[::-1]
                done = False
                for row in mine:
                    for orow in pool:
                        other = rows.patient[orow]
                        if other == p or (band_of[orow] != band and not (first < band and band_of[orow] > band)):
                            continue
                        before = first_band(other)
                        _swap(cells, band_of, value_of, row, orow)
                        after_p = first_band(p)
                        after = first_band(other)
                        better = after_p >= 0 and abs(after_p - band) < abs(first - band)
                        kept = after == wanted[other] or (before != wanted[other] and abs(after - wanted[other]) <= abs(before - wanted[other]))
                        if better and kept:
                            changed = True
                            done = after_p == band
                            first = after_p
                            break
                        _swap(cells, band_of, value_of, row, orow)
                    if done:
                        break
        if not changed:
            break
    rows.cells[source] = twinstore.held_column(cells)
    left = 0
    for p in range(patients.count):
        if first_band(p) not in (-1, wanted[p]):
            left += 1
    return left


def _swap(cells: "list[str]", band_of: "list[int]", value_of: "list[float | str | None]", row: int, orow: int) -> None:
    cells[row], cells[orow] = cells[orow], cells[row]
    band_of[row], band_of[orow] = band_of[orow], band_of[row]
    value_of[row], value_of[orow] = value_of[orow], value_of[row]


# -- G16.15: the trend's close -----------------------------------------------------


def _gap(total: int, low: int, high: int) -> int:
    """How far `total` lies outside `[low, high]`."""
    if total < low:
        return low - total
    if total > high:
        return total - high
    return 0


def _step(codes: "list[int]", begin: int, a: int, b: int) -> int:
    """The change of `S` when positions `a` and `b` (from 0) of one patient exchange their codes: `2 (c_a - c_b) (b - a)`."""
    return 2 * (codes[begin + a] - codes[begin + b]) * (b - a)


def _exchange(cells: "list[str]", codes: "list[int]", first: int, second: int) -> None:
    cells[first], cells[second] = cells[second], cells[first]
    codes[first], codes[second] = codes[second], codes[first]


def _steps_of(codes: "list[int]", begin: int, rho: int, patient: int) -> "dict[int, tuple[int, int, int]]":
    """Each step one exchange of this patient makes, positions at most 40 apart, the lowest positions first: step -> (patient, a, b)."""
    out: "dict[int, tuple[int, int, int]]" = {}
    for reach in range(1, min(TREND_REACH, rho - 1) + 1):
        for a in range(rho - reach):
            b = a + reach
            step = _step(codes, begin, a, b)
            if step != 0 and step not in out:
                out[step] = (patient, a, b)
    return out


def _trend_close(rows: _Rows, profile: contract.Profile, column: contract.ColumnBlock, grid: _Grid, patients: _Patients, published: "list[_Published]", words: chain_walk.Packed) -> int:
    """G16.15's close: exchanges of the column's readings between two rows of ONE patient until each published cell's `S_P` lies in its window.

    First the random improving exchanges: 30 proposals a patient, two of
    the column's drawn words a proposal over the published cells' patients
    in cell order (the words wrap round where a moved patient table holds
    more patients than the published cells), each proposal the positions
    `word mod r` of its two words, kept where it brings `S_P` nearer its
    window. Then, cell by cell, while `S_P` is outside: one exchange whose
    step equals the remaining gap, else TWO on different patients whose
    steps sum to it, else the largest step that fits, each exchange of two
    positions at most 40 apart of one patient; among equal choices the
    lowest patient, then the lowest positions. Each cell's grid code is
    read on its exact reading (`exact_meaning`, the profile's reader, as
    the validator reads it). Returns the cells left outside their windows.
    """
    name = column.name
    cells = twinstore.column_cells(rows.cells[name])
    meaning = exact_meaning(profile, column, cells)
    coded: "dict[str, int]" = {}
    for text in meaning:
        coded[text] = grid_code(grid, meaning[text])
    codes = [coded[cell] for cell in cells]
    available = chain_walk.size_of(words)
    word = 0
    unmet = 0
    for cell in published:
        rho = cell.rho
        low = 2 * cell.q
        high = 2 * cell.q + 1 if rho % 2 == 0 else 2 * cell.q
        total = 0
        for p in cell.patients:
            begin = patients.start[p]
            total += _s_of(codes[begin:begin + rho])
        for p in cell.patients:
            begin = patients.start[p]
            for _proposal in range(TREND_PROPOSALS):
                if available < 2:
                    break
                a = chain_walk.item(words, word % available) % rho
                b = chain_walk.item(words, (word + 1) % available) % rho
                word += 2
                if a == b:
                    continue
                step = _step(codes, begin, a, b)
                if step != 0 and _gap(total + step, low, high) < _gap(total, low, high):
                    _exchange(cells, codes, begin + a, begin + b)
                    total += step
        total = _exact_close(cells, codes, list(cell.patients), patients, rho, total, (low, high))
        if _gap(total, low, high) != 0:
            unmet += 1
    rows.cells[name] = twinstore.held_column(cells)
    return unmet


def _exact_close(cells: "list[str]", codes: "list[int]", found: "list[int]", patients: _Patients, rho: int, total: int, window: "tuple[int, int]") -> int:
    """The close's exact steps on one cell (G16.15): one exchange, else two on different patients, else the largest that fits; returns `S_P`.

    Among equal choices the lowest patient, then its steps in their order
    (positions nearer first, then the lower). The patients holding each
    step are kept as the steps change (`holders`, each step's patients in
    a heap, `_Holding`), so a round reads each distinct step once and the
    least two patients of a step, never a holder set whole (repair 2 of
    lane GRb, Codex's item 4: the build's `min` over every remaining holder
    made `N` patients of one step cost `N ** 2 / 2` reads), and a patient is
    added to or taken from a step's holders in a number of reads that grows
    as the logarithm of their count, never by shifting a list (batch 4u's
    outside review, item 5: an ascending list kept by a halving search
    shifted every later entry, so `N` three-row patients of codes `(0, 0,
    1)` brought to `S_P = 0` cost 2.075 CPU seconds at 200,001 rows and
    157.9 at 2,000,001). THE TOTAL-WORK BOUND: at most `4 |P| + 8` rounds,
    so a column's close makes at most `4 N + 8 C` rounds over its `C`
    published cells of `N` patients, at most two exchanges a round, each
    exchange reading its patient's steps afresh (at most `40 r`
    positions); a cell the bound leaves outside its window is named in the
    twin's deviations (`grain.trend`).
    """
    low, high = window
    steps: "dict[int, dict[int, tuple[int, int, int]]]" = {}
    holders: "dict[int, _Holding]" = {}
    for p in found:
        steps[p] = _steps_of(codes, patients.start[p], rho, p)
        _hold(holders, steps[p], p)
    rounds = 0
    while _gap(total, low, high) > 0 and rounds < 4 * len(found) + 8:
        rounds += 1
        want = (low - total) if total < low else (high - total)
        chosen: "list[tuple[int, int, int]]" = []
        if want in holders:
            chosen = [steps[_least(holders[want])][want]]
        else:
            chosen = _two_held(steps, holders, want)
            if not chosen:
                size = 0
                best = 0
                for step in holders:
                    if ((want > 0 and 0 < step < want) or (want < 0 and want < step < 0)) and abs(step) > size:
                        size = abs(step)
                        best = step
                if size:
                    chosen = [steps[_least(holders[best])][best]]
        if not chosen:
            break
        for p, a, b in chosen:
            begin = patients.start[p]
            total += _step(codes, begin, a, b)
            _exchange(cells, codes, begin + a, begin + b)
            _unhold(holders, steps[p], p)
            steps[p] = _steps_of(codes, begin, rho, p)
            _hold(holders, steps[p], p)
    return total


@dataclasses.dataclass
class _Holding:
    """The patients holding one step of the trend close (batch 4u's outside review, item 5).

    `heap` holds them in a binary heap written out by hand (`heapq` is not
    on the offline allowlist, plan D6.2), its least patient first; `live`
    counts each patient holding the step now. A patient taken away keeps
    its entry until the entry reaches the top, where it is skipped, so a
    patient is added or taken away in a number of reads that grows as the
    logarithm of the entries and no list is ever shifted. The step stands
    in `holders` while `live` holds a patient.
    """

    heap: "list[int]"
    live: "dict[int, int]"


def _heap_up(heap: "list[int]", p: int) -> None:
    """`p` added to the heap, its least entry first."""
    heap += [p]
    at = len(heap) - 1
    while at:
        parent = (at - 1) // 2
        if heap[parent] <= heap[at]:
            break
        heap[parent], heap[at] = heap[at], heap[parent]
        at = parent


def _heap_off(heap: "list[int]") -> None:
    """The heap's least entry taken off."""
    last = heap[len(heap) - 1]
    del heap[len(heap) - 1]
    if not heap:
        return
    heap[0] = last
    at = 0
    size = len(heap)
    while True:
        left = 2 * at + 1
        if left >= size:
            return
        child = left
        if left + 1 < size and heap[left + 1] < heap[left]:
            child = left + 1
        if heap[at] <= heap[child]:
            return
        heap[at], heap[child] = heap[child], heap[at]
        at = child


def _least(holding: _Holding) -> int:
    """The least patient holding the step (entries of patients taken away skipped and dropped as they reach the top)."""
    heap = holding.heap
    while heap[0] not in holding.live:
        _heap_off(heap)
    return heap[0]


def _hold(holders: "dict[int, _Holding]", held: "dict[int, tuple[int, int, int]]", p: int) -> None:
    """Patient `p` added to the holders of each of its steps."""
    for step in held:
        if step not in holders:
            holders[step] = _Holding([p], {p: 1})
            continue
        holding = holders[step]
        if p in holding.live:
            holding.live[p] += 1
        else:
            holding.live[p] = 1
            _heap_up(holding.heap, p)


def _unhold(holders: "dict[int, _Holding]", held: "dict[int, tuple[int, int, int]]", p: int) -> None:
    """Patient `p` taken from the holders of each of its steps; a step no patient holds leaves the table."""
    for step in held:
        if step not in holders or p not in holders[step].live:
            continue
        holding = holders[step]
        if holding.live[p] > 1:
            holding.live[p] -= 1
            continue
        del holding.live[p]
        if not holding.live:
            del holders[step]


def _least_but(holding: _Holding, p: int) -> int:
    """The least patient holding the step other than `p`, else -1 (as an ascending list's first two entries read)."""
    first = _least(holding)
    if first != p:
        return first
    if holding.live[p] > 1:
        return p
    heap = holding.heap
    while heap and (heap[0] == p or heap[0] not in holding.live):
        _heap_off(heap)
    other = heap[0] if heap else -1
    _heap_up(heap, p)
    return other


def _two_held(steps: "dict[int, dict[int, tuple[int, int, int]]]", holders: "dict[int, _Holding]", want: int) -> "list[tuple[int, int, int]]":
    """Two exchanges of DIFFERENT patients whose steps sum to `want`: the lowest first patient, its steps in their order, the lowest second; else none."""
    best_patient = -1
    for step in holders:
        rest = want - step
        if rest not in holders:
            continue
        first = _least(holders[step])
        if _least_but(holders[rest], first) < 0:
            continue
        if best_patient < 0 or first < best_patient:
            best_patient = first
    if best_patient < 0:
        return []
    for step in steps[best_patient]:
        rest = want - step
        if rest not in holders:
            continue
        other = _least_but(holders[rest], best_patient)
        if other >= 0:
            return [steps[best_patient][step], steps[other][rest]]
    return []


# -- the twin --------------------------------------------------------------------------


def _write_positions(rows: _Rows, grain: contract.PatientGrain) -> None:
    """Each position-like column written from its list (G16.13 step 5): the listed value at a listed position, the column's stand-in at a `null` entry and beyond `L`.

    The stand-in is the cell the row columns' run wrote for the column's
    emptied block (contract 4.6c.6 (c); plan P4-D401: no value of the table).
    """
    for name, values in grain.positions:
        if name not in rows.cells:
            continue
        cells = twinstore.column_cells(rows.cells[name])
        stand_in = cells[0] if cells else ""
        run = _whole_run(values)
        out: "list[str]" = []
        for row in range(len(rows.position)):
            j = rows.position[row]
            listed = values[j - 1] if j - 1 < len(values) else None
            if listed is None and run is not None and j > len(values):
                # A WHOLE-NUMBER RUN GOES ON PAST ITS LIST (G16.20; lane GRb2-c,
                # plan P4-D491 part c): a visit number whose list reads 1, 2,
                # ..., L writes L + 1, L + 2, ... at the twin's own later
                # positions, so a patient's later rows keep their order and a
                # time axis an analysis reads (no published fact reads them;
                # V12.7 reads the listed positions alone).
                listed = f"{run[0] + run[1] * (j - len(values))}"
            out += [listed if listed is not None else stand_in]
        rows.cells[name] = twinstore.held_column(out)


def _whole_run(values: "tuple[str | None, ...]") -> "tuple[int, int] | None":
    """A position list's last value and its step where every entry is a whole number written plainly and the steps are equal and not nought, else None."""
    numbers: "list[int]" = []
    for value in values:
        if not isinstance(value, str) or not value:
            return None
        negative = value[0] == "-"
        figures = value[1:] if negative else value
        if not figures or not all("0" <= character <= "9" for character in figures):
            return None
        whole = int(figures)
        if figures != f"{whole}":
            return None
        numbers += [-whole if negative else whole]
    if len(numbers) < 2:
        return None
    step = numbers[1] - numbers[0]
    if step == 0 or any(numbers[at + 1] - numbers[at] != step for at in range(len(numbers) - 1)):
        return None
    return numbers[-1], step


def _deviation(column: str, fact: str, published: str, achieved: str, note: str) -> "generation.Deviation":
    return generation.deviation_of(column, fact, published, achieved, note)


def twin(profile: contract.Profile, seed: int, rows_box: "list[generation.Twin]", patients_made: "generation.Twin", draws: Draws) -> "generation.Twin":
    """The twin of a description whose `grain` stands (G16.13 steps 1 to 8), from the row columns' run, the patient table's run and the walk's words.

    The row columns' run comes in a box of one (`rows_box`), which the walk
    empties of its columns once it has read them, and each row column is
    dropped once its finished column is written (G16.17's memory; LANE GRb
    RULINGS 3 (6)): the row columns are held twice at most, never three
    times. Guarantees: a fixed function of the description and the seed
    (every word is the stream's); every count it writes is a count of twin
    rows or patients; it reads no key, no `R*` and no real row. Raises
    `errors.ProfileError` only as an internal check. No I/O of any kind.
    """
    grain = _grain_of(profile)
    table = patient_table(profile)
    rows_made = rows_box[0]
    drawn = rows_made.words_drawn + patients_made.words_drawn + draws.words_drawn
    deviations: "list[generation.Deviation]" = []
    patients = _patients_read(table, patients_made)
    entries: "dict[str, contract.LadderEntry]" = {}
    for entry in table.profile.relationships.ladder:
        entries[entry.column] = entry
    r_labels = table.labels[patient_rules.R_NAME] if patient_rules.R_NAME in table.labels else ()
    r_values, missed = _r_values(grain, patients, r_labels, entries)
    for name in sorted(set(missed)):
        deviations += [_deviation(
            name, "grain.rows", "every parent cell's published row total", "a parent cell's rows differ",
            "The top band's rows a patient could not meet every row family's parent totals, so this family is dealt against a moved table.",
        )]
    patients.r = r_values
    start = 0
    patient_of_row: "list[int]" = []
    position: "list[int]" = []
    for patient in range(patients.count):
        patients.start += [start]
        for j in range(r_values[patient]):
            patient_of_row += [patient]
            position += [j + 1]
        start += r_values[patient]
    tabled = start
    blank_records = profile.n_rows - tabled
    if blank_records < 0:
        raise _internal("dealt more rows than the table holds")
    held = rows_made.held_columns if rows_made.held_columns is not None else ()
    rows = _Rows(patient_of_row, position, {}, {})
    by_name: "dict[str, contract.ColumnBlock]" = {}
    for at in range(len(profile.columns)):
        column = profile.columns[at]
        by_name[column.name] = column
        if contract.class_in(grain, column.name) in (patient_rules.CLASS_PERSON, patient_rules.CLASS_FIXED):
            continue
        kept: "list[str]" = []
        spare: "list[str]" = []
        for cell in twinstore.column_cells(held[at]):
            if len(spare) < blank_records and dialect.holds_nothing(cell):
                spare += [cell]
            else:
                kept += [cell]
        if len(kept) > tabled:
            spare = spare + kept[tabled:]
            kept = kept[:tabled]
        rows.cells[column.name] = twinstore.held_column(kept)
        rows.spare[column.name] = spare
    # THE ROW RUN'S COLUMNS RELEASED: their cells now live in `rows.cells`
    # alone; the run keeps its outcomes and notes for the twin's report.
    rows_made = dataclasses.replace(rows_made, held_columns=None)
    rows_box[0] = rows_made
    held = ()
    row_entries: "dict[str, contract.LadderEntry]" = {}
    for entry in grain.ladder:
        row_entries[entry.column] = entry
    grids: "dict[str, _Grid]" = {}
    for name, u, low, top in grain.grid:
        grids[name] = _Grid(u, low, _whole_text(top))
    trajectories: "dict[str, tuple[int, patient_trajectory.Trajectory]]" = {}
    for place in range(len(grain.trajectory)):
        trajectories[grain.trajectory[place].column] = (place, grain.trajectory[place])
    # A PATIENT'S OWN TRAJECTORY ON THE YEARS AXIS (G16.20; lane GRb2-c, plan
    # P4-D491 part c): the position column's dates are made first and sorted
    # inside each patient, so every entry read in years reads the twin's own
    # dates. Each family is dealt on its own words, so the order of the deals
    # moves no family's cells but through these times.
    position_name = grain.position
    yearly = position_name is not None and any(entry.axis == patient_trajectory.AXIS_YEARS for entry in grain.trajectory)
    families_dealt = {family.child for family in grain.rows}
    order = list(range(len(grain.rows)))
    times: "list[float] | None" = None
    redealt_first: "set[str]" = set()
    if yearly and position_name is not None:
        order = [at for at in order if grain.rows[at].child == position_name] + [at for at in order if grain.rows[at].child != position_name]
        if position_name not in families_dealt and position_name in rows.cells and position_name in row_entries:
            if position_name in trajectories:
                _redeal(profile, rows, row_entries, by_name, position_name, _trajectory_scores(trajectories[position_name], patients, entries, r_values, draws, None))
                redealt_first = {position_name}
            _one_sorted(profile, rows, row_entries, by_name, patients, position_name)
            times = _times_of(profile, rows, row_entries, by_name, patients, position_name)
    # -- step 4: the row families, in `grain.rows` order (the position column's first where an entry reads years) --
    for at in order:
        family = grain.rows[at]
        child = family.child
        if child not in rows.cells or child not in row_entries:
            continue
        parent_of_patient, parent_count = _parent_cells(patients, family.parents, entries)
        parent_of_row = [parent_of_patient[patient] for patient in patient_of_row]
        sums = draws.row_sums[at]
        latent = [chain_walk.hidden_score(chain_walk.item(sums, row)) for row in range(tabled)]
        own = _own_mean_of(grain, child)
        owned = own is not None and any(name == own.name for name, _level in family.parents)
        reading = _reading_of(profile, by_name[child], row_entries[child])
        child_cells = twinstore.column_cells(rows.cells[child])
        if child in trajectories:
            # A PATIENT'S OWN TRAJECTORY (G16.20; lane GRb2-c, plan P4-D491
            # part c): the rows are dealt in the order of their scores under
            # the column's entry, the own-mean score standing for the level's
            # where an own-mean column parents the family, so every published
            # cell of the family stands as before.
            owned_scores = _own_scores(own, patients, entries, draws.patient_words[at]) if owned and own is not None else None
            latent = _trajectory_scores(trajectories[child], patients, entries, r_values, draws, owned_scores, times)
            dealt, moved = _deal_family(child_cells, reading, row_entries[child], family.level, parent_of_row, parent_count, latent, family.table)
        elif child in grids and any(cell.column == child for cell in grain.trend):
            if owned and own is not None:
                latent = _with_patient_term(family, own, child, latent, patients, entries, row_entries, draws.patient_words[at], patient_of_row)
            targets, _published = _trend_targets(grain, child, float(fractions.Fraction(grids[child].u)), patients, entries)
            spread = _robust_scale(by_name[child])
            gamma = 1.0 / spread if spread > 0 else 1.0
            first, moved = _deal_family(child_cells, reading, row_entries[child], family.level, parent_of_row, parent_count,
                                        _with_trend(latent, targets, gamma, rows, r_values), family.table)
            beta = _response(first, targets, patients, reading)
            if beta > 0.05:
                gamma = gamma / beta
            first = []
            dealt, moved = _deal_family(child_cells, reading, row_entries[child], family.level, parent_of_row, parent_count,
                                        _with_trend(latent, targets, gamma, rows, r_values), family.table)
        else:
            if owned and own is not None:
                latent = _with_patient_term(family, own, child, latent, patients, entries, row_entries, draws.patient_words[at], patient_of_row)
            dealt, moved = _deal_family(child_cells, reading, row_entries[child], family.level, parent_of_row, parent_count, latent, family.table)
        child_cells = []
        latent = []
        rows.cells[child] = twinstore.held_column(dealt)
        dealt = []
        if yearly and child == position_name:
            _one_sorted(profile, rows, row_entries, by_name, patients, child)
            times = _times_of(profile, rows, row_entries, by_name, patients, child)
        if moved:
            deviations += [_deviation(
                child, "grain.rows", "the row family's published table", "a moved table",
                "The twin's counts of this row family's parent cells or of its child's bands differ from the published ones, so the family is dealt against the nearest table those counts allow.",
            )]
    # -- step 4': THE COUNTING PROCESS (G16.19; lane GRb2-b, plan P4-D491 part
    # b): where an interval rule stands, the interval, switch and end columns
    # are written from each patient's intervals (none is a row family's child).
    if grain.intervals and grain.hazard is not None and draws.interval_words is not None:
        column_bands: "list[list[int]]" = []
        for hazard_column in grain.hazard.columns:
            maps = _level_map(entries[hazard_column.column], hazard_column.level)
            column_bands += [[maps[code] for code in patients.codes[hazard_column.column]]]
        written = patient_intervals.write(grain, rows.cells, r_values, patients.start, column_bands, draws.interval_words)
        if written.lengthened:
            deviations += [_deviation(
                grain.intervals[0].stop, "grain.hazard", "every patient's end drawn from the hazard moments",
                f"{written.lengthened} patient(s) lengthened to hold their rows",
                "A patient's follow-up, drawn forward from the origin, that is shorter than its rows (or than its switch time and one unit) can hold is lengthened so.",
            )]
    # -- step 4'': A PATIENT'S OWN TRAJECTORY ON A COLUMN NO ROW FAMILY DEALS
    # (G16.20; lane GRb2-c, plan P4-D491 part c): its cells, the same cells,
    # dealt again to its rows in the order of their scores (no published cell
    # of any family reads which row holds them), before the dates are sorted
    # within each patient, so a date column's entry sets each patient's span.
    for name in trajectories:
        if name in families_dealt or name in redealt_first or name not in rows.cells or name not in row_entries:
            continue
        _redeal(profile, rows, row_entries, by_name, name, _trajectory_scores(trajectories[name], patients, entries, r_values, draws, None, times))
    # -- step 5: dealt dates sorted within each patient; position-like columns from their lists --
    _dates_sorted(profile, grain, rows, row_entries, patients)
    _write_positions(rows, grain)
    # -- step 6: the derived columns' close, the dates sorted again, then the trend's close --
    for derived in grain.derived:
        source = derived.source
        if source not in rows.cells or source not in row_entries or derived.name not in patients.codes:
            # A source the layer holds (contract 4.6c.12, departure 6) is
            # written as a held column: no reading of it stands to close.
            continue
        parent_of_patient = [0 for _p in range(patients.count)]
        for family in grain.rows:
            if family.child == source:
                parent_of_patient = _parent_cells(patients, family.parents, entries)[0]
                break
        bounded = False
        if derived.kind == patient_rules.FIRST_DATE:
            reading = _reading_of(profile, by_name[source], row_entries[source])
            left = _first_date_close(rows, source, reading, row_entries[source], derived, patients, parent_of_patient)
            what = "first date"
        else:
            done = _own_mean_close(rows, profile, by_name[source], derived, patients, parent_of_patient)
            left = done.left
            bounded = done.bounded
            what = "own mean"
        if left:
            # THE NOTE SAYS WHAT WAS SEARCHED (repair 2 of lane GRb, Codex's item
            # 8): the close's search is bounded (its passes, the partner rows a
            # proposal reads, its total work), so a repair beyond its bounds may
            # exist; the note never claims none could.
            reached = " It stopped at its total-work bound." if bounded else ""
            deviations += [_deviation(
                source, "grain.derived", f"every patient's {what} inside its band of {derived.name}",
                f"some patients' {what}s outside their bands",
                f"The bounded search of exchanges inside each patient's parent cell did not find a repair bringing every {what} into its published band, so the derived family is met only approximately.{reached}",
            )]
            # THE FAMILY IT MISSES (G16.15: "named in the twin's DEVIATIONS with
            # the family it misses"; repair 1 of lane GRb, the statistics
            # check's item 5): a patient left outside its band carries its rows
            # into another parent cell of every row family the derived column
            # is a parent of.
            for family in grain.rows:
                if not any(name == derived.name for name, _level in family.parents):
                    continue
                if any(one.column == family.child and one.fact == "grain.rows" for one in deviations):
                    continue
                deviations += [_deviation(
                    family.child, "grain.rows", "the row family's published table", "a parent cell's rows differ",
                    f"Patients left outside their band of {derived.name} carry their rows into another parent cell of this row family, so its table is met only approximately.",
                )]
    _dates_sorted(profile, grain, rows, row_entries, patients)
    for at in range(len(grain.grid)):
        name = grain.grid[at][0]
        if name not in rows.cells or not any(cell.column == name for cell in grain.trend):
            continue
        _targets, published = _trend_targets(grain, name, float(fractions.Fraction(grids[name].u)), patients, entries)
        unmet = _trend_close(rows, profile, by_name[name], grids[name], patients, published, draws.trend_words[at])
        if unmet:
            deviations += [_deviation(
                name, "grain.trend", "every published Q_P met", f"{unmet} cell(s) outside their window",
                "Exchanges of this column's readings within each patient could not bring every published cell's trend moment into its window.",
            )]
    return _assembled(profile, table, patients, rows, (rows_made, patients_made), deviations, drawn, seed)


def _with_patient_term(
    family: contract.RowFamily,
    own: contract.DerivedColumn,
    child: str,
    latent: "list[float]",
    patients: _Patients,
    entries: "dict[str, contract.LadderEntry]",
    row_entries: "dict[str, contract.LadderEntry]",
    words: chain_walk.Packed,
    patient_of_row: "list[int]",
) -> "list[float]":
    """G16.15's patient term: each row's score `omega z_p + sqrt(1 - omega^2) z_pj`.

    `omega` fitted on the published row family's table by (own-mean band
    at the family's level, band of the child), pooled over its other
    parents; `z_p` each patient's score inside its own-mean band at the
    band's PUBLISHED level, from its four words.
    """
    own_level = 0
    names: "list[str]" = []
    sizes: "list[int]" = []
    for name, level in family.parents:
        names += [name]
        sizes += [max(_level_map(entries[name], level)) + 1]
        if name == own.name:
            own_level = level
    own_maps = _level_map(entries[own.name], own_level)
    own_bands = max(own_maps) + 1
    child_bands = max(_level_map(row_entries[child], family.level)) + 1
    pooled = [[0 for _b in range(child_bands)] for _a in range(own_bands)]
    shares = [0 for _a in range(own_bands)]
    for patient in range(patients.count):
        shares[own_maps[patients.codes[own.name][patient]]] += 1
    own_place = 0
    for place in range(len(names)):
        if names[place] == own.name:
            own_place = place
    for line_at in range(len(family.table)):
        parts: "list[int]" = []
        rest = line_at
        for size in reversed(sizes):
            parts = [rest % size] + parts
            rest = rest // size
        for b in range(child_bands):
            pooled[parts[own_place]][b] += family.table[line_at][b]
    omega = omega_of(pooled, shares)
    scores = _own_scores(own, patients, entries, words)
    noise = math.sqrt(1.0 - omega * omega)
    return [omega * scores[patient_of_row[row]] + noise * latent[row] for row in range(len(latent))]


def _own_scores(own: contract.DerivedColumn, patients: _Patients, entries: "dict[str, contract.LadderEntry]", words: chain_walk.Packed) -> "list[float]":
    """Each patient's own-mean score `z_p` (G16.15): inside its own-mean band at the band's PUBLISHED level, from its four words."""
    sums: "list[int]" = []
    places: "list[int]" = []
    for patient in range(patients.count):
        sums += [chain_walk.hidden_sum(chain_walk.item(words, 4 * patient), chain_walk.item(words, 4 * patient + 1), chain_walk.item(words, 4 * patient + 2))]
        places += [chain_walk.item(words, 4 * patient + 3)]
    published_maps = _level_map(entries[own.name], 0)
    return patient_scores(sums, places, [published_maps[code] for code in patients.codes[own.name]])


def _redeal(profile: contract.Profile, rows: _Rows, row_entries: "dict[str, contract.LadderEntry]", by_name: "dict[str, contract.ColumnBlock]", name: str, latent: "list[float]") -> None:
    """A column no row family deals, its cells dealt again in the order of `latent` (G16.20): a number by its reading, a date by its place in time."""
    reading = _reading_of(profile, by_name[name], row_entries[name])
    cells = twinstore.column_cells(rows.cells[name])
    values: "list[fractions.Fraction | float | None]" = []
    for cell in cells:
        value = _read(reading, cell)[1]
        if isinstance(value, str):
            values += [patient_trajectory.date_order(value)]
        else:
            values += [value if isinstance(value, float) else None]
    rows.cells[name] = twinstore.held_column(patient_trajectory.redealt(cells, values, latent))


def _one_sorted(profile: contract.Profile, rows: _Rows, row_entries: "dict[str, contract.LadderEntry]", by_name: "dict[str, contract.ColumnBlock]", patients: _Patients, name: str) -> None:
    """One dealt date column's dates sorted inside each patient (G16.13 step 5, for this column alone and early)."""
    if name in rows.cells and name in row_entries:
        cells = twinstore.column_cells(rows.cells[name])
        rows.cells[name] = twinstore.held_column(_sorted_within(cells, _reading_of(profile, by_name[name], row_entries[name]), patients))


def _times_of(profile: contract.Profile, rows: _Rows, row_entries: "dict[str, contract.LadderEntry]", by_name: "dict[str, contract.ColumnBlock]", patients: _Patients, name: str) -> "list[float]":
    """Each tabled row's years since its patient's first dated row on the position column (G16.20); a row holding no date takes the time of the row before it."""
    reading = _reading_of(profile, by_name[name], row_entries[name])
    cells = twinstore.column_cells(rows.cells[name])
    out: "list[float]" = []
    for patient in range(patients.count):
        first: "fractions.Fraction | None" = None
        last = 0.0
        for j in range(patients.r[patient]):
            value = _read(reading, cells[patients.start[patient] + j])[1]
            moment = patient_trajectory.date_order(value) if isinstance(value, str) else None
            if moment is not None and first is None:
                first = moment
            if moment is not None and first is not None:
                last = float(moment - first) / patient_trajectory.SECONDS_A_YEAR
            out += [last]
    return out


def _trajectory_scores(
    found: "tuple[int, patient_trajectory.Trajectory]",
    patients: _Patients,
    entries: "dict[str, contract.LadderEntry]",
    r_values: "list[int]",
    draws: Draws,
    own: "list[float] | None",
    times: "list[float] | None" = None,
) -> "list[float]":
    """Each tabled row's score under a column's trajectory entry (G16.20): its grouping columns' bands at the levels it reads, off the patient table; its words the entry's; its times the years where it reads them."""
    place, entry = found
    if draws.trajectory_words is None:
        raise _internal("was handed no words for a patient's own trajectory")
    bands: "dict[str, list[int]]" = {}
    for group in entry.by:
        if group.column not in patients.codes or group.column not in entries:
            raise _internal("read a trajectory's grouping column the patient table does not hold")
        maps = _level_map(entries[group.column], group.level)
        bands[group.column] = [maps[code] for code in patients.codes[group.column]]
    first = place * (patient_trajectory.PATIENT_WORDS * patients.count + patient_trajectory.ROW_WORDS * sum(r_values))
    reads_years = entry.axis == patient_trajectory.AXIS_YEARS and times is not None
    return patient_trajectory.scores(entry, r_values, bands, draws.trajectory_words, first, own, times if reads_years else None)


def _dates_sorted(profile: contract.Profile, grain: contract.PatientGrain, rows: _Rows, row_entries: "dict[str, contract.LadderEntry]", patients: _Patients) -> None:
    for column in profile.columns:
        if contract.class_in(grain, column.name) == patient_rules.CLASS_DEALT and column.name in rows.cells and column.name in row_entries:
            sorted_cells = _sorted_within(twinstore.column_cells(rows.cells[column.name]), _reading_of(profile, column, row_entries[column.name]), patients)
            rows.cells[column.name] = twinstore.held_column(sorted_cells)


def _assembled(
    profile: contract.Profile,
    table: PatientTable,
    patients: _Patients,
    rows: _Rows,
    made: "tuple[generation.Twin, generation.Twin]",
    deviations: "list[generation.Deviation]",
    drawn: int,
    seed: int,
) -> "generation.Twin":
    """The twin in schema order: patients' cells on their rows, the records holding nothing on the form's places, then the form's sort.

    THE RECORDS HOLDING NOTHING ARE RESERVED, AND NO CELL LEAVES ITS ROW
    (repair 2 of lane GRb, Codex's item 1): a workbook's stand on its first
    rows, as G4.2a reserves them, and the twin says so (`reserved_rows`), so
    its writer deals each column's classes to them first and moves no cell;
    a text file's stand on the form's places, then last. The arrangement
    gives no record a cell of another row and its sort moves whole rows, so
    every patient's cells stay on its rows. The build placed a workbook's by
    the text file's arithmetic, which gave the records holding nothing
    cells of other rows, and its writer then moved each column's cells
    holding nothing on its own: on 7,909 records of 1,200 patients with 11
    empty records, 11 records held cells but no person and 10 patients'
    readings moved.
    """
    grain = _grain_of(profile)
    rows_made, patients_made = made
    tabled = len(rows.patient)
    arranging = dialect.arranging(profile.source.dialect, profile.n_rows, len(profile.columns))
    workbook = profile.source.workbook is not None
    blank: "list[int]" = []
    taken = [False for _row in range(profile.n_rows)]
    if workbook:
        blank = list(range(profile.n_rows - tabled))
        for row in blank:
            taken[row] = True
    else:
        targets = arranging.targets if arranging.placing else [False for _row in range(profile.n_rows)]
        for row in range(profile.n_rows):
            if targets[row] and len(blank) < profile.n_rows - tabled:
                blank += [row]
        for row in blank:
            taken[row] = True
        extra = profile.n_rows - 1
        while len(blank) < profile.n_rows - tabled:
            if not taken[extra]:
                blank += [extra]
                taken[extra] = True
            extra -= 1
    arranging = dialect.reserved_arranging(arranging, tuple(sorted(blank)), workbook, tuple(False for _column in profile.columns))
    tabled_rows = [row for row in range(profile.n_rows) if not taken[row]]
    finished: "list[twinstore.HeldColumn]" = []
    outcomes: "list[generation.ColumnOutcome]" = []
    level_remarks: "list[generation.Remark]" = []
    patient_place: "dict[str, int]" = {}
    for at in range(len(table.names)):
        patient_place[table.names[at]] = at
    listed = {name for name, _values in grain.positions}
    every_hole = generation.every_hole_spelling(profile)
    for at in range(len(profile.columns)):
        column = profile.columns[at]
        name = column.name
        out = ["" for _row in range(profile.n_rows)]
        if name in patients.cells:
            values = patients.cells[name]
            for k in range(tabled):
                out[tabled_rows[k]] = values[rows.patient[k]]
            first = patients_made.outcomes[patient_place[name]]
            # A FACT COUNTED IN PATIENTS, TOLD FROM THE ROWS (repair 2 of lane
            # GRb, Codex's item 5): the description counts this column in
            # patients, the counts below are the finished rows'.
            said = [generation.Remark(
                name, "the twin's patients holding a value of this column",
                f"{first.n_present} of the twin's {patients.count} patients hold a value, {first.n_distinct} different value(s)",
                "The description publishes this column counted in patients, one row a patient; the twin writes each patient's value on every one of its rows, and the counts above are of those rows.",
            )]
        else:
            values = twinstore.column_cells(rows.cells[name]) if name in rows.cells else ["" for _k in range(tabled)]
            for k in range(tabled):
                out[tabled_rows[k]] = values[k]
            spare = rows.spare[name] if name in rows.spare else []
            for k in range(len(blank)):
                out[blank[k]] = spare[k] if k < len(spare) else ""
            first = rows_made.outcomes[at]
            said = []
            if name in listed:
                said = [generation.Remark(
                    name, "the rows of this position-like column",
                    "each patient's row at a listed position holds the listed value, every other row the column's stand-in",
                    "The description publishes this column only as its list of one value a position; its block holds no count, and the counts above are of the twin's rows written from the list.",
                )]
            # Each row column dropped once its finished column is made (G16.17's memory).
            if name in rows.cells:
                del rows.cells[name]
            if name in rows.spare:
                del rows.spare[name]
            values = []
        # THE FINISHED CELLS RECOUNTED (Codex's item 5): the runs' outcomes were
        # counted before the patients' rows were written and the position
        # lists filled, so `visit` read 0 present on 7,898 filled rows.
        counted = generation.recounted(
            out, tuple(generation.holes_reserved(column, every_hole)), generation.declared_a_decimal_comma(column, profile),
        )
        outcomes += [dataclasses.replace(
            first, position=column.position, n_present=counted[0], n_missing=counted[1], n_distinct=counted[2],
            n_distinct_folded=counted[3], remarks=tuple(first.remarks) + tuple(said),
        )]
        level_remarks += said
        finished += [twinstore.held_column(dialect.placed_column(arranging, out))]
    finished = dialect.arranged_columns(arranging, finished, [])
    # The patient table's `r` and derived columns are no columns of the twin:
    # what its run measured of them is dropped.
    own = table.labels
    return generation.Twin(
        names=tuple(column.name for column in profile.columns),
        write_header=profile.source.header_source == "file",
        n_rows=profile.n_rows,
        columns=(),
        rows=(),
        outcomes=tuple(outcomes),
        deviations=tuple(list(rows_made.deviations) + [one for one in patients_made.deviations if one.column not in own] + deviations),
        approximations=tuple(list(rows_made.approximations) + [one for one in patients_made.approximations if one.column not in own]),
        remarks=tuple(list(rows_made.remarks) + [one for one in patients_made.remarks if one.column not in own] + level_remarks),
        words_drawn=drawn,
        seed=seed,
        form=profile.source.dialect,
        held_columns=tuple(finished),
        # A workbook's records holding nothing stand reserved on its first
        # rows, so its writer deals each column's classes to them first and
        # moves no cell (Codex's item 1); every class is dealt by the writer.
        reserved_rows=len(blank) if workbook else -1,
        sheet_dealt=(),
    )
