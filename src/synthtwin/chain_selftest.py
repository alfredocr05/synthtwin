"""THE SELF-TEST L2b: a trial twin of the sample, judged at the whole table's precision (contract 4.6b.8; lane ST, plan P4-D458).

NOT IN FORCE, AND ZONE P. Invariant S12 stands: only `synthtwin profile`'s
switched branch reaches this module, through the ONE import site the
offline scanner's table names (`cli._private_report`), and nothing it
computes enters the description, the questions file, the summary, the
twin or the shared report. Its fits use platform floats (lane MDEP's
delegated choice D-L1, contract 4.6d.6): a judged word near its line may
differ between two computers, and no byte anyone else sees depends on it.

WHAT IT DOES, in the order of plan P4-D458:

- THE WORDS: each sampled row's own SplitMix64 stream, seeded by a
  constant and the row's content hash (with its place among equal rows
  of the sample), so the words are a function of the table's content
  alone. Word 0 gives the row's group of sixteen, whose bits 0 to 3 are
  the four fixed half-splits; words `1 + 3 f` to `3 + 3 f` the walk's
  three words for family `f`; the words after them the shuffle.
- THE TRIAL TWIN: each eligible column's own sample cells, dealt into
  rows by the chain's walk through the shared module `chain_walk`
  (G16.9: `hidden_sum`, `order_by_scores`, `target_of`, `deal`), each
  family's target counted on the sample. Held in memory only.
- THE PANEL, from the schema alone: subgroup rates of each two-valued
  column by the `L0` bands of every other column (F1); correlations of
  every pair of fine columns on the code scale and, for a skewed one, on
  its second code (F2); least squares of each fine number (F3), logistic
  models of each two-valued column (F4), Poisson models of each count
  (F5) and a Cox model of each time-and-event pair (F6) on their
  strongest partners, the parameters capped at events / 10; missing
  cells by the bands of every other column (F9); analyses that stop on
  the trial twin and not on the sample (F10). Every fit takes Newton
  steps solved by a Cholesky factor written out in Python floats.
- THE YARDSTICK: each estimate's half-split yardstick `h` (the root mean
  square over the four splits of half 0's value less half 1's), SCALED to
  the whole table, `h * sqrt(n_s / n)` (BC-ARCH 4.2 item 1); supported
  estimates only (every defining cell at least 22 rows on the sample and
  11 in every half, events and non-events alike); RULE W2: a pair is
  judged only where `n * h` reaches the floor.
- THE CONTROLS, in every run: the REPLICATE (split 0's two halves, held to
  `sqrt(2)` times the yardstick of splits 1 to 3) and a column-wise
  SHUFFLE of the sample; a run where the replicate does not land inside
  at about a fresh sample's rate, or the shuffle does, judges nothing and
  says why.
- THE WORDS JUDGED: `carried`, `approximate`, `not carried` or `not
  judged`, for every pair and every family F1 to F10, with THE CEILING:
  a raw-scale analysis of a skewed column, and a log-scale one of a
  skewed column with no second code, read at best `approximate`.

ARITHMETIC. Words, groups, cells and counts are Python integers; the
exponential is the contract's stated exponential (`chain_rules`), so no
library exponential is admitted for this zone. No I/O of any kind.
"""

import dataclasses
import math

from synthtwin import chain, chain_grades, chain_walk
from synthtwin import chain_rules as rules

# -- THE WORDS -------------------------------------------------------------

SELFTEST_CONSTANT = 0x53594E5448545354
GOLDEN = 0x9E3779B97F4A7C15
MASK64 = (1 << 64) - 1

# -- THE JUDGEMENT'S CONSTANTS (decided on measurement, plan P4-D458) -------

# Every defining cell at least this many rows on the sample, and half of it
# in every half (S2 2.1, `analyst_battery.SUPPORT`).
SUPPORT = 22
HALF_SUPPORT = 11
# K-BC-01's family target: a family reads `carried` where its share of
# estimates inside the scaled yardstick stands at most this many points
# under the replicate's.
FAMILY_TARGET = 0.25
# A family with fewer supported estimates is not judged.
FAMILY_MINIMUM = 5
# The line between `approximate` and `not carried`: the median, over the
# estimates the shuffle moves beyond their yardstick, of the twin's gap
# over the shuffle's gap. A CONVENTION, the conservative one (LANE ST
# RULINGS 4 (5)): over the battery's seeds the replicate's median read 0 to
# 1.36 (its 95th percentile 0.59) and the trial twin's 0.26 to 1.03 where
# the product misses and 0.05 to 0.98 where it meets, so the line does not
# separate the controls, and no advice rests on it: `approximate` and `not
# carried` both say develop the code on the twin and run it on the table.
NOT_CARRIED_LINE = 0.5
# THE CEILING's skew: a fine column whose quantile skew of its published
# rungs reaches this in magnitude is skewed.
SKEW_CEILING = 0.2
# THE CONTROLS: the replicate lands inside on at least this share of the
# run's supported estimates, and the shuffle at least this many points
# under it.
REPLICATE_AT_LEAST = 0.5
SHUFFLE_UNDER = 0.25
# An estimate is JOINT where its sample value stands more than this many
# yardsticks from its value were the columns unrelated (about two
# standard errors): the controls are read on the joint estimates, which a
# shuffle must miss.
JOINT_AT = 1.0
# The panel's models: at most this many predictors, and at most this many
# models of each kind (a STATED LIMIT, plan P4-D458: the first twelve
# outcomes of a kind in the schema's order, for the self-test's seconds
# under G4; the private report names the outcomes it modelled).
PREDICTORS = 6
MODELS_A_KIND = 12
# THE TRIAL KEYS (LANE ST RULINGS 3 (2)(a) and 4 (2)(b)): the self-test runs
# under its constant, the constant plus one and plus two, one key after
# another, and every family and pair reads the WORST of the keys' words
# (`not judged` where a key does not judge it).
TRIAL_KEYS = 3
# A family's share inside, and the replicate's, are read on its JOINT
# estimates (the set K-BC-01's family target counts), and on all its
# supported estimates where fewer than this many are joint (LANE ST
# RULINGS 4 (2)(a)).
JOINT_MINIMUM = 5
# F1's part of its own (LANE ST RULINGS 3 (2)(b)): each level of a label
# column holding SUPPORT rows or more on the sample, at most its this many
# largest, read as a 0/1 outcome by the `L0` bands of every other column.
LABEL_LEVELS = 10
# THE TABLE WITHOUT RELATIONSHIPS (LANE ST RULINGS 4 (6), and 6 (1) on the
# repair-1 verify's FIX 1): with the columns unrelated, an estimate stands
# more than its yardstick from its null value on about this share of
# estimates by chance (the yardstick is read from four half-splits, so the
# ratio is Student's t with four degrees of freedom over two: P(|t_4| > 2)
# is 0.116, against 0.046 for a yardstick known exactly; measured 0.103 to
# 0.105 on the null table ST5 at 20,000 rows). A family between columns
# whose share of joint estimates among its supported ones is under twice it
# is not judged, its reason giving the counts. The line is read family by
# family: the share over a whole run read 0.112 to 0.119 on ST4, a table
# with relationships, beside ST5's 0.103 to 0.105, so no line over a run
# tells the two apart. It is the SHARE alone: repair 1 also left a family
# of fewer than `JOINT_MINIMUM` joint estimates unjudged, which hid a model
# with three strong coefficients of eight (3.5 to 8.7 yardsticks from
# nought) and so dropped the fallback of RULINGS 4 (2)(a) at family level.
CHANCE_JOINT = 0.116
NO_RELATIONSHIP_UNDER = 2 * CHANCE_JOINT


def sees_no_relationship(joint: int, supported: int) -> bool:
    """A family between columns too weakly related to judge: its share of joint estimates under twice chance.

    `joint` of its `supported` estimates stand beyond their yardstick from
    their value were the columns unrelated (LANE ST RULINGS 6 (1)(a)).
    """
    return joint < NO_RELATIONSHIP_UNDER * supported


def unrelated_reason(joint: int, supported: int) -> str:
    """Why a family the share rule leaves unjudged is not judged: its counts, never more (LANE ST RULINGS 6 (1)(b))."""
    return (
        f"only {joint} of its {supported} supported estimates stand beyond their yardstick from their value were "
        "the columns unrelated, under twice the share chance gives, so it is not judged"
    )


NEWTON_STEPS = 30
NEWTON_TOLERANCE = 1e-9

CARRIED = "carried"
APPROXIMATE = "approximate"
NOT_CARRIED = "not carried"
NOT_JUDGED = "not judged"
# The reason every word reads where the self-test stopped (LANE ST RULINGS
# 3 (1)(b)): the run, its description and its exit code stand.
STOPPED = "the self-test stopped"
# The reason every word reads where the chain a description publishes is
# its PATIENT LAYER's (lane GRa, plan P4-D449): the self-test reads a chain
# of one row a person on its sample, and `describe` hands it no inputs for
# a patient layer (batch 4q's merge of lane ST beside that layer).
PATIENT_LAYER = (
    "the self-test judges the chain of a table of one row a person, and this description's chain is its "
    "patient layer's, which this version does not judge"
)
# Where none of the run's supported estimates stands beyond its yardstick
# from its value were the columns unrelated, nothing between columns is
# judged (its counts given by `unrelated_reason` where it is a family's).
NONE_JOINT = (
    "none of the panel's supported estimates stands beyond its yardstick from its value were the columns "
    "unrelated, so nothing between columns is judged"
)
# The judged words from the best to the worst: a family with parts reads
# the worst of its parts' words.
_WORST = (CARRIED, APPROXIMATE, NOT_CARRIED)


def _rank(word: str) -> int:
    """A judged word's place from the best to the worst; -1 for `not judged`."""
    for at in range(len(_WORST)):
        if _WORST[at] == word:
            return at
    return -1

# A fine column's rates are also read in sixteen equal bins of its linear
# code, cuts between the published rungs, as an analyst's own bands are.
BINS = 16
# THREE COLUMNS TOGETHER: each two-valued column's rate in the cells of two
# of its strongest partners' `L2` bands, over this many partners.
TRIPLE_PARTNERS = 8

FAMILY_NAMES = (
    ("F1", "subgroup rates and cross-tables"),
    ("F2", "correlations"),
    ("F3", "linear regression"),
    ("F4", "logistic regression"),
    ("F5", "count regression"),
    ("F6", "time to event"),
    ("F7", "several rows per person"),
    ("F8", "trained models"),
    ("F9", "missing data by other columns"),
    ("F10", "code run unchanged"),
)


def splitmix64(state: int) -> int:
    """SplitMix64's output for one state (Steele, Lea and Flood 2014): the mix of `state`."""
    z = state & MASK64
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK64
    return z ^ (z >> 31)


def word(seed: int, position: int) -> int:
    """The `position`-th output (from 0) of SplitMix64 seeded with `seed`: `mix(seed + (position + 1) * golden)`."""
    return splitmix64((seed + (position + 1) * GOLDEN) & MASK64)


def row_seeds(hashes: "tuple[int, ...] | list[int]", constant: int = SELFTEST_CONSTANT) -> "list[int]":
    """Each sampled row's seed: the constant XOR its content hash's first 8 bytes, plus its place among equal rows.

    `constant` is the self-test's (`SELFTEST_CONSTANT`); a measurement
    hands others to draw other trial twins of one sample (plan P4-D458).

    Equal rows of the sample (one content hash) are told apart by their
    place among the sample's rows of that hash, so the seeds are a
    function of the sample's content alone, never of the file's order.
    """
    seen: "dict[int, int]" = {}
    out: "list[int]" = []
    for value in hashes:
        place = seen[value] if value in seen else 0
        seen[value] = place + 1
        out += [((constant ^ value) + place * GOLDEN) & MASK64]
    return out


def groups_of(seeds: "list[int]") -> bytes:
    """Each row's group of sixteen (word 0's low four bits); split `j`'s half is bit `j`."""
    return bytes(word(seed, 0) & 15 for seed in seeds)


def walk_sums(seeds: "list[int]", family: int) -> "list[int]":
    """Each trial row's hidden sum `S` for family `family` (words `1 + 3 f` to `3 + 3 f`, G16.8)."""
    base = 1 + 3 * family
    return [chain_walk.hidden_sum(word(seed, base), word(seed, base + 1), word(seed, base + 2)) for seed in seeds]


def shuffle_order(seeds: "list[int]", families: int, column: int) -> "list[int]":
    """The shuffle's rows for one column: the sample's rows sorted by the row's word `1 + 3 F + c`, ties by row."""
    position = 1 + 3 * families + column
    keyed = sorted((word(seeds[row], position), row) for row in range(len(seeds)))
    return [row for _key, row in keyed]


# -- THE TABLES THE SELF-TEST READS ----------------------------------------


@dataclasses.dataclass
class View:
    """One table the panel reads: each eligible column's codes over its rows.

    `l0[c]` each row's `L0` band code; `value[c]` the number the panel reads
    (a fine column's linear code, a two-valued column's 0 or 1), `None`
    where the row holds none; `log[c]` a skewed fine column's second code;
    `excess[c]` a fine column's RAW SCALE where it parts from the code: for
    each row whose reading lies beyond the clip, the reading less its code,
    in code units (`raw_excess`); the raw scale is the code plus it.
    """

    rows: int
    l0: "dict[str, list[int]]"
    value: "dict[str, list[float | None]]"
    log: "dict[str, list[float | None]]"
    excess: "dict[str, dict[int, float]]" = dataclasses.field(default_factory=dict)


def _value_lists(column: chain.SampleColumn) -> "tuple[list[float | None], list[float | None] | None]":
    """A column's numbers on the sample: the linear code (fine) or 0 and 1 (two-valued), and its second code."""
    rows = len(column.l0)
    if column.linear is not None and column.has is not None:
        linear = column.linear
        has = column.has
        values: "list[float | None]" = [float(linear[row]) if has[row] else None for row in range(rows)]
        second: "list[float | None] | None" = None
        if column.second is not None:
            held = column.second
            second = [float(held[row]) if has[row] else None for row in range(rows)]
        return values, second
    if column.binary is not None:
        zero, one = column.binary
        out: "list[float | None]" = []
        for row in range(rows):
            code = column.l0[row]
            out += [0.0 if code == zero else 1.0 if code == one else None]
        return out, None
    return [None] * rows, None


def raw_excess(column: chain.SampleColumn) -> "dict[int, float]":
    """A fine column's RAW SCALE where it parts from its code: each sample row read beyond the clip, its reading less its code.

    In code units: the reading `v` reads `256 (v - lo) / (hi - lo) - 1/2`
    on the code's own scale (a code's mid-point reads the code itself), so
    the raw scale is the code plus this excess on the rows beyond the clip,
    and the code inside it, within half a code (half of 1/256 of the clip's
    span). LANE ST RULINGS 5 (2), Codex's item 3: the extremes the clip
    folds into its end codes are read where they stand.
    """
    out: "dict[int, float]" = {}
    beyond = column.beyond
    linear = column.linear
    lo = column.lo
    hi = column.hi
    if beyond is None or linear is None or lo is None or hi is None or hi <= lo:
        return out
    scale = 256.0 / (hi - lo)
    for row in sorted(beyond):
        moved = (beyond[row] - lo) * scale - 0.5 - linear[row]
        if moved != 0.0 and math.isfinite(moved):
            out[row] = moved
    return out


def sample_view(inputs: chain.SelftestInputs) -> View:
    """The sample itself, as the panel reads it."""
    l0: "dict[str, list[int]]" = {}
    value: "dict[str, list[float | None]]" = {}
    log: "dict[str, list[float | None]]" = {}
    excess: "dict[str, dict[int, float]]" = {}
    for column in inputs.columns:
        l0[column.name] = list(column.l0)
        values, second = _value_lists(column)
        value[column.name] = values
        if second is not None:
            log[column.name] = second
        moved = raw_excess(column)
        if moved:
            excess[column.name] = moved
    return View(len(inputs.hashes), l0, value, log, excess)


def mapped_view(sample: View, source: "dict[str, list[int]]") -> View:
    """A table whose row `r` of column `c` holds the sample's row `source[c][r]` of that column."""
    l0: "dict[str, list[int]]" = {}
    value: "dict[str, list[float | None]]" = {}
    log: "dict[str, list[float | None]]" = {}
    excess: "dict[str, dict[int, float]]" = {}
    for name in sample.l0:
        rows = source[name]
        held = sample.l0[name]
        l0[name] = [held[row] for row in rows]
        numbers = sample.value[name]
        value[name] = [numbers[row] for row in rows]
        if name in sample.log:
            second = sample.log[name]
            log[name] = [second[row] for row in rows]
        if name in sample.excess:
            moved = sample.excess[name]
            excess[name] = {at: moved[rows[at]] for at in range(len(rows)) if rows[at] in moved}
    return View(sample.rows, l0, value, log, excess)


# -- THE TRIAL TWIN: THE CHAIN'S WALK THROUGH THE SHARED MODULE -------------


def child_bands(column: chain.SampleColumn, level: int) -> "tuple[chain_walk.ChildBands, list[int]]":
    """A column's sample cells at a chain level: the bands' sizes, their read cells, order, and the CELL LIST.

    Inside each band the cells holding a reading of the band's order (a
    value band's) come first, sorted by reading (the linear code, then the
    second code, then the `L0` band, then the sample row), then the rest,
    as G16.2 step 4 reads a column's cell list.
    """
    ladder = column.ladder
    maps = ladder.maps[level]
    count = ladder.counts[level]
    read_cells: "list[list[tuple[int, int, int, int]]]" = [[] for _band in range(count)]
    other_cells: "list[list[int]]" = [[] for _band in range(count)]
    linear = column.linear
    second = column.second
    has = column.has
    for row in range(len(column.l0)):
        code = column.l0[row]
        band = maps[code]
        if ladder.ordered[code]:
            first = linear[row] if linear is not None and has is not None and has[row] else 0
            then = second[row] if second is not None and has is not None and has[row] else 0
            read_cells[band] += [(first, then, code, row)]
        else:
            other_cells[band] += [row]
    sizes: "list[int]" = []
    read: "list[int]" = []
    cells: "list[int]" = []
    for band in range(count):
        ordered_cells = sorted(read_cells[band])
        sizes += [len(ordered_cells) + len(other_cells[band])]
        read += [len(ordered_cells)]
        cells += [entry[3] for entry in ordered_cells] + other_cells[band]
    ordered = [False] * count
    for place in range(len(ladder.l0)):
        if ladder.ordered[place]:
            ordered[maps[place]] = True
    return chain_walk.ChildBands(tuple(sizes), tuple(read), tuple(ordered)), cells


@dataclasses.dataclass(frozen=True)
class Parent:
    """A family's parent as the walk reads it: its dealt band codes at its chain level and its maps."""

    codes: "bytearray | bytes"
    width: int
    maps: "tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]"
    chain_level: int
    level: int
    counts: "tuple[int, int, int]"


def deal_family(
    parents: "list[Parent]",
    bands: chain_walk.ChildBands,
    table: "tuple[tuple[int, ...], ...]",
    sums: "chain_walk.Packed | list[int]",
) -> "tuple[chain_walk.Dealt, chain_walk.Target]":
    """One family dealt as `generation._chain_family` deals it (G16.2 and G16.6), on any rows.

    Each row's parent cell is formed from the parents' dealt band codes,
    each mapped from the parent's chain level to its level here (the
    levels nest), the last parent varying fastest; the target is the
    family's table or its moved table (`chain_walk.target_of`); the rows
    are ordered by their hidden sums and dealt (`chain_walk.deal`).
    """
    rows = chain_walk.size_of(sums)
    cell_count = 1
    for parent in parents:
        cell_count = cell_count * parent.counts[parent.level]
    cells = chain_walk.packed(rows, chain_walk.width_for(cell_count - 1))
    for parent in parents:
        down = [0 for _band in range(parent.counts[parent.chain_level])]
        for place in range(len(parent.maps[0])):
            down[parent.maps[parent.chain_level][place]] = parent.maps[parent.level][place]
        size = parent.counts[parent.level]
        for row in range(rows):
            chain_walk.put(cells, row, chain_walk.item(cells, row) * size + down[chain_walk.read_code(parent.codes, parent.width, row)])
    counts = [0 for _cell in range(cell_count)]
    for row in range(rows):
        cell = chain_walk.item(cells, row)
        counts[cell] = counts[cell] + 1
    aimed = chain_walk.target_of(table, counts, list(bands.sizes))
    order = chain_walk.order_by_scores(sums)
    return chain_walk.deal(cells, cell_count, order, bands, aimed.table), aimed


def _sample_table(inputs: chain.SelftestInputs, family: rules.Family, columns: "dict[str, chain.SampleColumn]") -> "tuple[tuple[int, ...], ...]":
    """The family's table counted on the sample's own rows, at the family's levels: its target in the trial twin."""
    child = columns[family.child]
    count = child.ladder.counts[family.level]
    cell_count = 1
    for name, level in family.parents:
        cell_count = cell_count * columns[name].ladder.counts[level]
    table = [[0] * count for _cell in range(cell_count)]
    for row in range(len(inputs.hashes)):
        cell = 0
        for name, level in family.parents:
            parent = columns[name]
            cell = cell * parent.ladder.counts[level] + parent.ladder.maps[level][parent.l0[row]]
        table[cell][child.ladder.maps[family.level][child.l0[row]]] += 1
    return tuple(tuple(line) for line in table)


def trial_twin(inputs: chain.SelftestInputs, seeds: "list[int]") -> "tuple[dict[str, list[int]], int]":
    """Each eligible column's sample row standing in each trial row, and the families dealt against a moved target.

    The trial twin is the sample's own cells, column by column, dealt into
    rows by the chain's walk: a family's child is dealt against the
    family's table counted on the sample, on the parents' bands as dealt
    before it. A column no family places is dealt alone. Nothing here is
    written anywhere.
    """
    columns = {column.name: column for column in inputs.columns}
    dealt: "dict[str, tuple[bytearray, int, int]]" = {}
    source: "dict[str, list[int]]" = {}
    families = list(inputs.families)
    placed = {family.child for family in families}
    for column in inputs.columns:
        if column.name not in placed:
            families += [rules.Family(column.name, 0, (), None, ())]
    moved = 0
    for place in range(len(families)):
        family = families[place]
        child = columns[family.child]
        bands, cells = child_bands(child, family.level)
        parents: "list[Parent]" = []
        for name, level in family.parents:
            codes, width, chain_level = dealt[name]
            ladder = columns[name].ladder
            parents += [Parent(codes, width, ladder.maps, chain_level, level, ladder.counts)]
        table = _sample_table(inputs, family, columns)
        sums = walk_sums(seeds, place)
        result, aimed = deal_family(parents, bands, table, sums)
        moved += 1 if aimed.moved else 0
        dealt[family.child] = (result.bands, result.band_width, family.level)
        source[family.child] = [cells[chain_walk.read_code(result.index, result.index_width, row)] for row in range(len(seeds))]
    return source, moved


def shuffled(inputs: chain.SelftestInputs, seeds: "list[int]") -> "dict[str, list[int]]":
    """The control without joint structure: each column's sample cells in an order of its own."""
    families = len(inputs.families)
    return {inputs.columns[at].name: shuffle_order(seeds, families, at) for at in range(len(inputs.columns))}


# -- THE ESTIMATES ---------------------------------------------------------


@dataclasses.dataclass
class Estimate:
    """One number of the panel on the sample, the trial twin, the shuffle and the eight halves."""

    key: "tuple[str, ...]"
    family: str
    sample: float
    twin: "float | None"
    shuffle: "float | None"
    halves: "list[float]"
    kind: str = "difference"
    # The estimate's value were the two columns unrelated (a rate's
    # overall rate, a correlation's or coefficient's nought): an estimate
    # whose sample value stands beyond its yardstick from it is JOINT, and
    # the controls are read on the joint estimates.
    null: float = 0.0
    # The PART of its family the estimate belongs to (F1's bands, cuts
    # between them and three columns together; F2's code and second code):
    # a family reads the worst word of its parts.
    part: str = ""


def _halves() -> "tuple[tuple[int, ...], ...]":
    """For split `j` and half `h`, the groups (of sixteen) it holds: index `2 j + h`."""
    out: "list[tuple[int, ...]]" = []
    for split in range(4):
        for half in range(2):
            out += [tuple(group for group in range(16) if (group >> split) & 1 == half)]
    return tuple(out)


HALF_GROUPS = _halves()
ALL_GROUPS = tuple(range(16))


def _sum_groups(per_group: "list[list[float]]", groups: "tuple[int, ...]") -> "list[float]":
    total = [0.0] * len(per_group[0])
    for group in groups:
        held = per_group[group]
        for at in range(len(total)):
            total[at] += held[at]
    return total


def _codes_of(view: View, name: str, binned: bool) -> "list[int]":
    """A column's `L0` band codes, or a fine column's sixteen BINS of its linear code (a seventeenth for no reading)."""
    if not binned:
        return view.l0[name]
    return [BINS if value is None else int(value) // 16 for value in view.value[name]]


def _rate_estimates(
    family: str,
    outcome: str,
    flags: "dict[str, list[float | None]]",
    views: "dict[str, View]",
    groups: bytes,
    others: "list[str]",
    binned: bool = False,
    left: "dict[str, int] | None" = None,
) -> "list[Estimate]":
    """The rate of a 0/1 outcome inside each `L0` band (or, `binned`, each code bin) of every other column (F1, F9)."""
    out: "list[Estimate]" = []
    for other in others:
        cells = {side: _codes_of(views[side], other, binned) for side in views}
        out += _rates_in_cells(family, (family, outcome, other, "bin" if binned else "band"), flags, cells, groups, left)
    return out


LEVEL_PART = "each level of a label column"


def label_levels(column: chain.SampleColumn) -> "list[int]":
    """A label column's levels F1 reads as outcomes: its `L0` codes holding SUPPORT rows on the sample, the largest first.

    At most `LABEL_LEVELS`, ties by code; never the column's empty band.
    """
    counted: "dict[int, int]" = {}
    for code in column.l0:
        counted[code] = counted[code] + 1 if code in counted else 1
    ranked = sorted((-counted[code], code) for code in counted if code != column.missing and counted[code] >= SUPPORT)
    return [code for _count, code in ranked[:LABEL_LEVELS]]


def _label_rate_estimates(
    name: str,
    missing: int,
    levels: "list[int]",
    views: "dict[str, View]",
    groups: bytes,
    others: "dict[str, int]",
    left: "dict[str, int] | None" = None,
) -> "list[Estimate]":
    """EACH LEVEL OF A LABEL COLUMN as a 0/1 outcome, its rate in each `L0` band of every other column (F1's part).

    One pass a side for each other column counts every level at once: the
    rows whose label is present by the other's band, and of them each
    level's. `others` maps each other column to its count of `L0` bands.
    A cell under the support rule yields no estimate (`left`).
    """
    out: "list[Estimate]" = []
    width = len(levels)
    place = {levels[at]: at for at in range(width)}
    sample = views["sample"]
    labels = sample.l0[name]
    for other in others:
        bands = others[other]
        rows_by_group = [[0] * bands for _group in range(16)]
        events_by_group = [[0] * (bands * width) for _group in range(16)]
        codes = sample.l0[other]
        for row in range(sample.rows):
            code = labels[row]
            if code == missing:
                continue
            group = groups[row]
            band = codes[row]
            rows_by_group[group][band] += 1
            if code in place:
                events_by_group[group][band * width + place[code]] += 1
        side_rates: "dict[str, list[float | None]]" = {}
        for side in ("twin", "shuffle"):
            held_labels = views[side].l0[name]
            held_codes = views[side].l0[other]
            counted = [0] * bands
            events = [0] * (bands * width)
            for row in range(views[side].rows):
                code = held_labels[row]
                if code == missing:
                    continue
                band = held_codes[row]
                counted[band] += 1
                if code in place:
                    events[band * width + place[code]] += 1
            side_rates[side] = [
                events[cell] / counted[cell // width] if counted[cell // width] else None for cell in range(bands * width)
            ]
        rows_all = [0] * bands
        events_all = [0] * (bands * width)
        for group in range(16):
            for band in range(bands):
                rows_all[band] += rows_by_group[group][band]
            for cell in range(bands * width):
                events_all[cell] += events_by_group[group][cell]
        present = sum(rows_all)
        if not present:
            continue
        halves_rows = [[sum(rows_by_group[group][band] for group in HALF_GROUPS[at]) for band in range(bands)] for at in range(8)]
        halves_events = [
            [sum(events_by_group[group][cell] for group in HALF_GROUPS[at]) for cell in range(bands * width)] for at in range(8)
        ]
        # Each level's rows over every band, counted ONCE before the band
        # loop (Codex's item 9, G4): the level's rate overall is its null.
        level_totals = [0] * width
        for cell in range(bands * width):
            level_totals[cell % width] += events_all[cell]
        for band in range(bands):
            held_rows = rows_all[band]
            if not held_rows:
                continue
            for at in range(width):
                cell = band * width + at
                held_events = events_all[cell]
                if held_rows < SUPPORT or held_events < SUPPORT or held_rows - held_events < SUPPORT or any(
                    halves_rows[half][band] < HALF_SUPPORT
                    or halves_events[half][cell] < HALF_SUPPORT
                    or halves_rows[half][band] - halves_events[half][cell] < HALF_SUPPORT
                    for half in range(8)
                ):
                    if left is not None:
                        left["rate cells"] = left["rate cells"] + 1 if "rate cells" in left else 1
                    continue
                level_rows = level_totals[at]
                out += [
                    Estimate(
                        ("F1", f"{name}={levels[at]}", other, "level", f"{band}"),
                        "F1",
                        held_events / held_rows,
                        side_rates["twin"][cell],
                        side_rates["shuffle"][cell],
                        [halves_events[half][cell] / halves_rows[half][band] for half in range(8)],
                        "difference",
                        level_rows / present,
                        LEVEL_PART,
                    )
                ]
    return out


_PART_OF = {"band": "at the published bands", "bin": "between the published cuts"}


def _triple_rate_estimates(
    outcome: str,
    flags: "dict[str, list[float | None]]",
    views: "dict[str, View]",
    groups: bytes,
    partners: "tuple[str, ...]",
    coarse: "dict[str, tuple[int, ...]]",
    left: "dict[str, int] | None" = None,
) -> "list[Estimate]":
    """THREE COLUMNS TOGETHER: the outcome's rate in each cell of two partners' `L2` bands (F1; S2's three-way counts).

    A cell under the support rule is counted in `left["rate cells"]` as
    every other rate's is (Codex's item 15).
    """
    out: "list[Estimate]" = []
    for first in range(len(partners)):
        for second in range(first + 1, len(partners)):
            x = partners[first]
            z = partners[second]
            width = 1 + max(coarse[z])
            cells = {
                side: [coarse[x][a] * width + coarse[z][b] for a, b in zip(views[side].l0[x], views[side].l0[z])]
                for side in views
            }
            out += _rates_in_cells("F1", ("F1", outcome, x, z), flags, cells, groups, left)
    return out


def _rates_in_cells(
    family: str,
    key: "tuple[str, ...]",
    flags: "dict[str, list[float | None]]",
    cells: "dict[str, list[int]]",
    groups: bytes,
    left: "dict[str, int] | None" = None,
) -> "list[Estimate]":
    """A 0/1 outcome's rate in each cell of a grouping, on the sample (by group), the trial twin and the shuffle.

    A cell holding rows but under the support rule (22 rows, events and
    non-events on the sample; 11 of each in every half) yields no
    estimate, and is counted in `left["rate cells"]`.
    """
    out: "list[Estimate]" = []
    codes = cells["sample"]
    bands = 1
    for side in cells:
        if cells[side]:
            bands = max(bands, 1 + max(cells[side]))
    rows_by_group = [[0.0] * bands for _group in range(16)]
    events_by_group = [[0.0] * bands for _group in range(16)]
    flag = flags["sample"]
    for row in range(len(codes)):
        value = flag[row]
        if value is None:
            continue
        group = groups[row]
        rows_by_group[group][codes[row]] += 1.0
        events_by_group[group][codes[row]] += value
    rows_all = _sum_groups(rows_by_group, ALL_GROUPS)
    events_all = _sum_groups(events_by_group, ALL_GROUPS)
    overall = sum(events_all) / sum(rows_all) if sum(rows_all) else 0.0
    rows_half = [_sum_groups(rows_by_group, held) for held in HALF_GROUPS]
    events_half = [_sum_groups(events_by_group, held) for held in HALF_GROUPS]
    others_rates: "dict[str, list[float | None]]" = {}
    for side in ("twin", "shuffle"):
        counted = [0.0] * bands
        events = [0.0] * bands
        side_flag = flags[side]
        side_codes = cells[side]
        for row in range(len(side_codes)):
            value = side_flag[row]
            if value is None:
                continue
            counted[side_codes[row]] += 1.0
            events[side_codes[row]] += value
        others_rates[side] = [events[band] / counted[band] if counted[band] else None for band in range(bands)]
    for band in range(bands):
        held_rows = rows_all[band]
        held_events = events_all[band]
        if not held_rows:
            continue
        if held_rows < SUPPORT or held_events < SUPPORT or held_rows - held_events < SUPPORT or any(
            rows_half[at][band] < HALF_SUPPORT
            or events_half[at][band] < HALF_SUPPORT
            or rows_half[at][band] - events_half[at][band] < HALF_SUPPORT
            for at in range(8)
        ):
            if left is not None:
                left["rate cells"] = left["rate cells"] + 1 if "rate cells" in left else 1
            continue
        out += [
            Estimate(
                key + (f"{band}",),
                family,
                held_events / held_rows,
                others_rates["twin"][band],
                others_rates["shuffle"][band],
                [events_half[at][band] / rows_half[at][band] for at in range(8)],
                "difference",
                overall,
                _PART_OF[key[3]] if len(key) == 4 and key[3] in _PART_OF else "three columns together",
            )
        ]
    return out


def _correlation(sums: "list[float]") -> "float | None":
    """Pearson's r from `[n, sx, sy, sxx, syy, sxy]`, None where a spread is nought."""
    n, sx, sy, sxx, syy, sxy = sums
    if n < 3:
        return None
    vx = n * sxx - sx * sx
    vy = n * syy - sy * sy
    if vx <= 0.0 or vy <= 0.0:
        return None
    return (n * sxy - sx * sy) / math.sqrt(vx * vy)


def _pair_sums(left: "list[float | None]", right: "list[float | None]", groups: "bytes | None") -> "list[list[float]]":
    """`[n, sx, sy, sxx, syy, sxy]` over the rows holding both, by group (one list where `groups` is None)."""
    out = [[0.0] * 6 for _group in range(16 if groups is not None else 1)]
    for row in range(len(left)):
        x = left[row]
        y = right[row]
        if x is None or y is None:
            continue
        held = out[groups[row]] if groups is not None else out[0]
        held[0] += 1.0
        held[1] += x
        held[2] += y
        held[3] += x * x
        held[4] += y * y
        held[5] += x * y
    return out


def _numbers(view: View, name: str, read: str) -> "list[float | None]":
    """A column's numbers on a table: its second code where `read` is "log", else its value."""
    return view.log[name] if read == "log" else view.value[name]


def _excess_sums(
    left: "list[float | None]",
    right: "list[float | None]",
    extra_left: "dict[int, float]",
    extra_right: "dict[int, float]",
    groups: "bytes | None",
) -> "list[list[float]]":
    """What the raw scale adds to the code scale's `[n, sx, sy, sxx, syy, sxy]`, by group (one list where `groups` is None).

    Only the rows holding both columns whose reading lies beyond a clip
    (`View.excess`) add anything, so the raw scale costs a pass over those
    few rows and never another pass over the sample.
    """
    out = [[0.0] * 6 for _group in range(16 if groups is not None else 1)]
    for row in sorted(set(extra_left) | set(extra_right)):
        x = left[row]
        y = right[row]
        if x is None or y is None:
            continue
        ex = extra_left[row] if row in extra_left else 0.0
        ey = extra_right[row] if row in extra_right else 0.0
        held = out[groups[row]] if groups is not None else out[0]
        held[1] += ex
        held[2] += ey
        held[3] += (2.0 * x + ex) * ex
        held[4] += (2.0 * y + ey) * ey
        held[5] += x * ey + (y + ey) * ex
    return out


def _with(first: "list[list[float]]", second: "list[list[float]]") -> "list[list[float]]":
    """Two lists of sums by group, added."""
    return [[first[group][at] + second[group][at] for at in range(len(first[group]))] for group in range(len(first))]


RAW_PART = "on the raw scale"


def _raw_correlation(
    views: "dict[str, View]", groups: bytes, a: str, b: str, by_group: "list[list[float]]", sides: "dict[str, list[float]]"
) -> "Estimate | None":
    """Pearson's r of two columns on the RAW SCALE (LANE ST RULINGS 5 (2)): the code scale's sums with the excess added.

    `by_group` the code scale's sums on the sample by group, `sides` the
    trial twin's and the shuffle's; None where neither column reads beyond
    its clip (the raw scale is then the code scale) or a spread is nought.
    """
    sample = views["sample"]
    if a not in sample.excess and b not in sample.excess:
        return None
    found: "dict[str, float | None]" = {}
    for side in ("twin", "shuffle"):
        view = views[side]
        extra = _excess_sums(
            view.value[a], view.value[b], view.excess[a] if a in view.excess else {},
            view.excess[b] if b in view.excess else {}, None,
        )
        found[side] = _correlation(_with([sides[side]], extra)[0])
    raw = _with(by_group, _excess_sums(
        sample.value[a], sample.value[b], sample.excess[a] if a in sample.excess else {},
        sample.excess[b] if b in sample.excess else {}, groups,
    ))
    value = _correlation(_sum_groups(raw, ALL_GROUPS))
    halves = [_correlation(_sum_groups(raw, held)) for held in HALF_GROUPS]
    if value is None or any(held is None for held in halves):
        return None
    return Estimate(("pair", a, b, "raw"), "pair", value, found["twin"], found["shuffle"],
                    [float(held) for held in halves if held is not None], "difference", 0.0, RAW_PART)


def _correlation_estimates(
    views: "dict[str, View]", groups: bytes, fine: "list[str]", skewed: "set[str]"
) -> "tuple[list[Estimate], dict[tuple[str, str], Estimate]]":
    """Pearson's r of every pair of fine columns on the code scale, and on the second code where one is skewed (F2).

    Beside them, each pair's correlation on the RAW SCALE where a column
    reads beyond its clip (`_raw_correlation`), keyed by the pair: a pair's
    word reads it (LANE ST RULINGS 5 (2)); it is not one of F2's estimates.
    """
    out: "list[Estimate]" = []
    raw: "dict[tuple[str, str], Estimate]" = {}
    sample = views["sample"]
    for first in range(len(fine)):
        for second in range(first + 1, len(fine)):
            a = fine[first]
            b = fine[second]
            scales = [("code", "value", "value")]
            if (a in skewed and a in sample.log) or (b in skewed and b in sample.log):
                scales += [("log", "log" if a in sample.log else "value", "log" if b in sample.log else "value")]
            for scale, read_a, read_b in scales:
                by_group = _pair_sums(_numbers(sample, a, read_a), _numbers(sample, b, read_b), groups)
                total = _sum_groups(by_group, ALL_GROUPS)
                if total[0] < SUPPORT:
                    continue
                halves_sums = [_sum_groups(by_group, held) for held in HALF_GROUPS]
                if any(held[0] < HALF_SUPPORT for held in halves_sums):
                    continue
                value = _correlation(total)
                halves = [_correlation(held) for held in halves_sums]
                if value is None or any(held is None for held in halves):
                    continue
                side_sums: "dict[str, list[float]]" = {}
                sides: "dict[str, float | None]" = {}
                for side in ("twin", "shuffle"):
                    view = views[side]
                    side_sums[side] = _pair_sums(_numbers(view, a, read_a), _numbers(view, b, read_b), None)[0]
                    sides[side] = _correlation(side_sums[side])
                out += [
                    Estimate(
                        ("F2", a, b, scale),
                        "F2",
                        value,
                        sides["twin"],
                        sides["shuffle"],
                        [float(held) for held in halves if held is not None],
                        "difference",
                        0.0,
                        "on the code scale" if scale == "code" else "on the second code (the log scale)",
                    )
                ]
                if scale == "code":
                    found = _raw_correlation(views, groups, a, b, by_group, side_sums)
                    if found is not None:
                        raw[(a, b)] = found
    return out, raw


def _counted(first: "list[int]", second: "list[int]", width: int, groups: "bytes | None") -> "list[dict[int, int]]":
    """A pair's `L0` table counted by group (one table where `groups` is None), cells keyed `a * width + b`."""
    out: "list[dict[int, int]]" = [{} for _group in range(16 if groups is not None else 1)]
    for row in range(len(first)):
        held = out[groups[row]] if groups is not None else out[0]
        cell = first[row] * width + second[row]
        held[cell] = held[cell] + 1 if cell in held else 1
    return out


def _at_level(table: "dict[int, int]", width: int, maps: "tuple[tuple[int, ...], tuple[int, ...]]", level_width: int) -> "dict[int, int]":
    """An `L0` table read at a coarser level: each cell's two codes mapped by each column's own ladder."""
    out: "dict[int, int]" = {}
    for cell in table:
        first, second = divmod(cell, width)
        merged = maps[0][first] * level_width + maps[1][second]
        out[merged] = out[merged] + table[cell] if merged in out else table[cell]
    return out


def pair_table(
    views: "dict[str, View]", groups: bytes, a: chain.SampleColumn, b: chain.SampleColumn
) -> "tuple[Estimate | None, int]":
    """A pair's table at the FINEST LEVEL its cells support (LANE ST RULINGS 3 (4)), and that level; (None, -1) where none does.

    The table is read at `L0`, then `L1`, then `L2`, and taken at the first
    level at which every cell holding rows on the sample holds `SUPPORT`
    rows there and `HALF_SUPPORT` in every half; its estimate is the total
    variation distance of the trial twin's (and the shuffle's) table at that
    level from the sample's, and of each split's two halves'. Cells are
    counted in dictionaries keyed by the joint code, so a table of two
    long-tailed label columns holds only its cells that hold rows.
    """
    width = max(1, b.ladder.counts[0])
    by_group = _counted(views["sample"].l0[a.name], views["sample"].l0[b.name], width, groups)
    levels: "list[tuple[dict[int, int], list[dict[int, int]]]]" = []
    for level in range(3):
        maps = (a.ladder.maps[level], b.ladder.maps[level])
        grouped = [_at_level(held, width, maps, b.ladder.counts[level]) for held in by_group]
        levels += [(_joined(grouped, ALL_GROUPS), [_joined(grouped, HALF_GROUPS[at]) for at in range(8)])]
    level = first_supported_level(levels)
    if level < 0:
        return None, -1
    maps = (a.ladder.maps[level], b.ladder.maps[level])
    whole, halves = levels[level]
    distances = [_distance(halves[2 * split], halves[2 * split + 1]) for split in range(4)]
    found = {
        side: _distance(_at_level(_counted(views[side].l0[a.name], views[side].l0[b.name], width, None)[0], width, maps, b.ladder.counts[level]), whole)
        for side in ("twin", "shuffle")
    }
    return Estimate(("pair", a.name, b.name, f"L{level}"), "pair", 0.0, found["twin"], found["shuffle"], distances, "distance"), level


def first_supported_level(levels: "list[tuple[dict[int, int], list[dict[int, int]]]]") -> int:
    """The first level whose every cell holding rows holds `SUPPORT` rows on the sample and `HALF_SUPPORT` in each half; -1 where none does.

    `levels[k]` is a pair's table at level `k`: its cells' counts on the
    whole sample and in each of the eight halves (LANE ST RULINGS 3 (4)).
    """
    for level in range(len(levels)):
        whole, halves = levels[level]
        if all(
            whole[cell] >= SUPPORT and all((half[cell] if cell in half else 0) >= HALF_SUPPORT for half in halves) for cell in whole
        ):
            return level
    return -1


def _ratio_sums(values: "list[float | None]", codes: "list[int]", kept: "dict[int, int]", groups: "bytes | None") -> "list[list[float]]":
    """By group, each kept level's rows, sum and sum of squares of `values`: `[n_0, s_0, q_0, n_1, ...]`."""
    width = len(kept)
    out = [[0.0] * (3 * width) for _group in range(16 if groups is not None else 1)]
    for row in range(len(values)):
        value = values[row]
        code = codes[row]
        if value is None or code not in kept:
            continue
        held = out[groups[row]] if groups is not None else out[0]
        at = 3 * kept[code]
        held[at] += 1.0
        held[at + 1] += value
        held[at + 2] += value * value
    return out


def _ratio(sums: "list[float]") -> "float | None":
    """The correlation ratio (eta) from each level's `[n, sum, sum of squares]`; None where the spread is nought."""
    rows = 0.0
    total = 0.0
    squares = 0.0
    between = 0.0
    for at in range(0, len(sums), 3):
        n = sums[at]
        rows += n
        total += sums[at + 1]
        squares += sums[at + 2]
        if n > 0.0:
            between += sums[at + 1] * sums[at + 1] / n
    if rows < 3.0:
        return None
    spread = squares - total * total / rows
    if spread <= 0.0:
        return None
    share = (between - total * total / rows) / spread
    return math.sqrt(min(1.0, max(0.0, share)))


def _ratio_excess(
    values: "list[float | None]", codes: "list[int]", kept: "dict[int, int]", extra: "dict[int, float]", groups: "bytes | None"
) -> "list[list[float]]":
    """What the raw scale adds to `_ratio_sums`' `[n_0, s_0, q_0, ...]`, by group: the rows read beyond the clip alone."""
    width = len(kept)
    out = [[0.0] * (3 * width) for _group in range(16 if groups is not None else 1)]
    for row in sorted(extra):
        value = values[row]
        code = codes[row]
        if value is None or code not in kept:
            continue
        moved = extra[row]
        held = out[groups[row]] if groups is not None else out[0]
        at = 3 * kept[code]
        held[at + 1] += moved
        held[at + 2] += (2.0 * value + moved) * moved
    return out


def pair_correlations(
    views: "dict[str, View]", groups: bytes, a: chain.SampleColumn, b: chain.SampleColumn, skewed: "set[str]",
    left: "dict[str, int] | None" = None,
) -> "list[Estimate] | None":
    """The CODE-SCALE CORRELATION of a pair holding a fine column (LANE ST RULINGS 4 (1)(a)), on the second code too where one is skewed.

    Pearson's r of the fine column's linear code with the other's (its
    linear code, or 0 and 1 for a two-valued column), or the correlation
    ratio of the fine column's code by a label's levels (each holding
    `SUPPORT` rows on the sample and `HALF_SUPPORT` in every half, counted
    on the COMPLETE cases the ratio reads: rows holding both the label and
    a reading, Codex's item 4). Beside them the same on the RAW SCALE where
    the fine column reads beyond its clip (LANE ST RULINGS 5 (2)). Returns
    [] for a pair holding no fine column, and None where an estimate the
    pair owes is not supported (fewer than 22 rows, 11 in a half, or no
    spread), counted in `left["correlations"]`.
    """
    if a.linear is None and b.linear is not None:
        a, b = b, a
    if a.linear is None:
        return []
    sample = views["sample"]
    log_a = a.name in skewed and a.name in sample.log
    log_b = b.linear is not None and b.name in skewed and b.name in sample.log
    scales = [("code", "value", "value")]
    if log_a or log_b:
        scales += [("log", "log" if log_a else "value", "log" if log_b else "value")]
    label = b.linear is None and b.binary is None
    kept: "dict[int, int]" = {}
    if label:
        for code in label_levels_halved(b, groups, sample.value[a.name]):
            kept[code] = len(kept)
        if len(kept) < 2:
            if left is not None:
                left["correlations"] = left["correlations"] + 1 if "correlations" in left else 1
            return None
        scales = [scale for scale in scales if scale[0] == "code" or log_a]
    out: "list[Estimate]" = []
    for scale, read_a, read_b in scales:
        raw: "Estimate | None" = None
        if label:
            ratio_by_group = _ratio_sums(_numbers(sample, a.name, read_a), sample.l0[b.name], kept, groups)
            value = _ratio(_sum_groups(ratio_by_group, ALL_GROUPS))
            halves = [_ratio(_sum_groups(ratio_by_group, held)) for held in HALF_GROUPS]
            side_ratio: "dict[str, list[float]]" = {
                side: _ratio_sums(_numbers(views[side], a.name, read_a), views[side].l0[b.name], kept, None)[0]
                for side in ("twin", "shuffle")
            }
            sides = {side: _ratio(side_ratio[side]) for side in side_ratio}
            enough = True
            if scale == "code" and a.name in sample.excess:
                raw_by_group = _with(ratio_by_group, _ratio_excess(
                    sample.value[a.name], sample.l0[b.name], kept, sample.excess[a.name], groups))
                raw_value = _ratio(_sum_groups(raw_by_group, ALL_GROUPS))
                raw_halves = [_ratio(_sum_groups(raw_by_group, held)) for held in HALF_GROUPS]
                raw_sides: "dict[str, float | None]" = {}
                for side in ("twin", "shuffle"):
                    view = views[side]
                    extra = view.excess[a.name] if a.name in view.excess else {}
                    raw_sides[side] = _ratio(_with([side_ratio[side]], _ratio_excess(
                        view.value[a.name], view.l0[b.name], kept, extra, None))[0])
                if raw_value is not None and all(held is not None for held in raw_halves):
                    raw = Estimate(("pair", a.name, b.name, "raw"), "pair", raw_value, raw_sides["twin"], raw_sides["shuffle"],
                                   [float(held) for held in raw_halves if held is not None], "difference", 0.0, RAW_PART)
        else:
            pair_by_group = _pair_sums(_numbers(sample, a.name, read_a), _numbers(sample, b.name, read_b), groups)
            total = _sum_groups(pair_by_group, ALL_GROUPS)
            enough = total[0] >= SUPPORT and all(_sum_groups(pair_by_group, held)[0] >= HALF_SUPPORT for held in HALF_GROUPS)
            value = _correlation(total)
            halves = [_correlation(_sum_groups(pair_by_group, held)) for held in HALF_GROUPS]
            side_sums: "dict[str, list[float]]" = {
                side: _pair_sums(_numbers(views[side], a.name, read_a), _numbers(views[side], b.name, read_b), None)[0]
                for side in ("twin", "shuffle")
            }
            sides = {side: _correlation(side_sums[side]) for side in side_sums}
            if scale == "code" and enough:
                raw = _raw_correlation(views, groups, a.name, b.name, pair_by_group, side_sums)
        if not enough or value is None or any(held is None for held in halves):
            if left is not None:
                left["correlations"] = left["correlations"] + 1 if "correlations" in left else 1
            return None
        out += [
            Estimate(
                ("pair", a.name, b.name, scale),
                "pair",
                value,
                sides["twin"],
                sides["shuffle"],
                [float(held) for held in halves if held is not None],
                "difference",
                0.0,
                "on the code scale" if scale == "code" else "on the second code (the log scale)",
            )
        ]
        if raw is not None:
            out += [raw]
    return out


def label_levels_halved(column: chain.SampleColumn, groups: bytes, values: "list[float | None] | None" = None) -> "list[int]":
    """A label's levels holding `SUPPORT` rows on the sample and `HALF_SUPPORT` in every half, in code order.

    Counted on the rows that also hold a reading of `values` where it is
    given: the complete cases the correlation ratio reads (Codex's item 4).
    """
    counted: "list[dict[int, int]]" = [{} for _group in range(16)]
    for row in range(len(column.l0)):
        code = column.l0[row]
        if code == column.missing or (values is not None and values[row] is None):
            continue
        held = counted[groups[row]]
        held[code] = held[code] + 1 if code in held else 1
    whole = _joined(counted, ALL_GROUPS)
    halves = [_joined(counted, HALF_GROUPS[at]) for at in range(8)]
    return sorted(
        code
        for code in whole
        if whole[code] >= SUPPORT and all((halves[at][code] if code in halves[at] else 0) >= HALF_SUPPORT for at in range(8))
    )


def _joined(by_group: "list[dict[int, int]]", groups: "tuple[int, ...]") -> "dict[int, int]":
    """The cells of several groups' tables, added."""
    out: "dict[int, int]" = {}
    for group in groups:
        held = by_group[group]
        for cell in held:
            out[cell] = out[cell] + held[cell] if cell in out else held[cell]
    return out


def _distance(one: "dict[int, int]", other: "dict[int, int]") -> float:
    """The total variation distance between two tables' shares."""
    total_one = 0
    for cell in one:
        total_one += one[cell]
    total_other = 0
    for cell in other:
        total_other += other[cell]
    if not total_one or not total_other:
        return 0.0
    cells = set(one) | set(other)
    gap = 0.0
    for cell in cells:
        gap += abs((one[cell] if cell in one else 0) / total_one - (other[cell] if cell in other else 0) / total_other)
    return 0.5 * gap


# -- THE FITS: NEWTON STEPS SOLVED BY CHOLESKY (zone P) ---------------------


class FitStopped(Exception):
    """A fit that cannot be finished: a singular system, no convergence, a separation."""


def exp(value: float) -> float:
    """`e` to the power `value`, by the contract's stated exponential (4.6b.4): no library exponential."""
    if value <= 0.0:
        return rules.stated_exponential(-value)
    if value > 700.0:
        raise FitStopped("an exponential beyond binary64's range")
    return 1.0 / rules.stated_exponential(value)


def _solve(matrix: "list[list[float]]", vector: "list[float]") -> "list[float]":
    """`matrix^-1 vector` for a symmetric positive-definite matrix, by its Cholesky factor written out in Python floats.

    The factor `L` (`matrix = L L'`) row by row, then `L y = vector` forward
    and `L' x = y` backward: at most seven unknowns (six predictors and an
    intercept). Written out because scipy 1.18, which Python 3.12 and later
    install, refuses a list where scipy 1.17 took one, and zone P builds no
    array (repair 1 of lane ST). A pivot that is not positive, or a value
    that is not finite, is a singular system.
    """
    size = len(vector)
    lower = [[0.0] * size for _row in range(size)]
    for i in range(size):
        for j in range(i + 1):
            total = matrix[i][j]
            for k in range(j):
                total -= lower[i][k] * lower[j][k]
            if i == j:
                if not math.isfinite(total) or total <= 0.0:
                    raise FitStopped("a singular system")
                lower[i][i] = math.sqrt(total)
            else:
                lower[i][j] = total / lower[j][j]
    forward = [0.0] * size
    for i in range(size):
        total = vector[i]
        for k in range(i):
            total -= lower[i][k] * forward[k]
        forward[i] = total / lower[i][i]
    out = [0.0] * size
    for i in range(size - 1, -1, -1):
        total = forward[i]
        for k in range(i + 1, size):
            total -= lower[k][i] * out[k]
        out[i] = total / lower[i][i]
    if not all(math.isfinite(value) for value in out):
        raise FitStopped("a singular system")
    return out


def _filled(matrix: "list[list[float]]") -> "list[list[float]]":
    """A lower triangle made symmetric."""
    for i in range(len(matrix)):
        for j in range(i):
            matrix[j][i] = matrix[i][j]
    return matrix


def moments_by_group(x_rows: "list[list[float]]", y: "list[float]", groups: "list[int] | None") -> "list[tuple[list[list[float]], list[float]]]":
    """Each group's `X'X` (lower triangle) and `X'y`: one group where `groups` is None."""
    size = len(x_rows[0]) if x_rows else 0
    held = [([[0.0] * size for _at in range(size)], [0.0] * size) for _group in range(16 if groups is not None else 1)]
    for row in range(len(x_rows)):
        x = x_rows[row]
        target = y[row]
        matrix, vector = held[groups[row]] if groups is not None else held[0]
        for i in range(size):
            xi = x[i]
            vector[i] += xi * target
            line = matrix[i]
            for j in range(i + 1):
                line[j] += xi * x[j]
    return held


def _added(parts: "list[tuple[list[list[float]], list[float]]]", picked: "tuple[int, ...]") -> "tuple[list[list[float]], list[float]]":
    """Several groups' matrices and vectors, added (the matrix made symmetric)."""
    size = len(parts[0][1])
    matrix = [[0.0] * size for _at in range(size)]
    vector = [0.0] * size
    for group in picked:
        held_matrix, held_vector = parts[group]
        for i in range(size):
            vector[i] += held_vector[i]
            line = matrix[i]
            held_line = held_matrix[i]
            for j in range(i + 1):
                line[j] += held_line[j]
    return _filled(matrix), vector


def least_squares(x_rows: "list[list[float]]", y: "list[float]") -> "list[float]":
    """The least-squares coefficients of `y` on `x_rows` (an intercept among them)."""
    matrix, vector = _added(moments_by_group(x_rows, y, None), (0,))
    return _solve(matrix, vector)


def glm_pass(
    x_rows: "list[list[float]]", y: "list[float]", beta: "list[float]", kind: str, groups: "list[int] | None"
) -> "list[tuple[list[list[float]], list[float]]]":
    """Each group's information `X'WX` (lower triangle) and score `X'(y - mu)` at `beta` (one group where `groups` is None)."""
    size = len(beta)
    held = [([[0.0] * size for _at in range(size)], [0.0] * size) for _group in range(16 if groups is not None else 1)]
    stated = rules.stated_exponential
    logistic = kind == "logistic"
    for row in range(len(x_rows)):
        x = x_rows[row]
        eta = 0.0
        for i in range(size):
            eta += beta[i] * x[i]
        if logistic:
            if eta >= 0.0:
                tail = stated(eta)
                mu = 1.0 / (1.0 + tail)
            else:
                tail = stated(-eta)
                mu = tail / (1.0 + tail)
            weight = mu * (1.0 - mu)
        else:
            if eta > 700.0:
                raise FitStopped("an exponential beyond binary64's range")
            mu = stated(-eta) if eta <= 0.0 else 1.0 / stated(eta)
            weight = mu
        residual = y[row] - mu
        matrix, score = held[groups[row]] if groups is not None else held[0]
        for i in range(size):
            xi = x[i]
            score[i] += xi * residual
            line = matrix[i]
            wx = weight * xi
            for j in range(i + 1):
                line[j] += wx * x[j]
    return held


def glm(x_rows: "list[list[float]]", y: "list[float]", kind: str, start: "list[float] | None") -> "list[float]":
    """A logistic (`kind` "logistic") or Poisson (`kind` "poisson") model's coefficients by Newton steps."""
    size = len(x_rows[0]) if x_rows else 0
    beta = list(start) if start is not None else [0.0] * size
    if start is None and kind == "poisson":
        mean = sum(y) / len(y) if y else 0.0
        if mean <= 0.0:
            raise FitStopped("an outcome of noughts only")
        beta[0] = _log(mean)
    for _step in range(NEWTON_STEPS):
        matrix, score = _added(glm_pass(x_rows, y, beta, kind, None), (0,))
        step = _solve(matrix, score)
        beta = [beta[i] + step[i] for i in range(size)]
        if max(abs(value) for value in beta) > 50.0:
            raise FitStopped("a separation")
        if max(abs(value) for value in step) < NEWTON_TOLERANCE * (1.0 + max(abs(value) for value in beta)):
            return beta
    raise FitStopped("no convergence")


def cox(times: "list[float]", events: "list[float]", x_rows: "list[list[float]]", start: "list[float] | None") -> "list[float]":
    """A Cox model's coefficients by Newton steps on Breslow's partial likelihood (no intercept)."""
    size = len(x_rows[0]) if x_rows else 0
    order = [row for _time, row in sorted((-times[row], row) for row in range(len(times)))]
    beta = list(start) if start is not None else [0.0] * size
    for _step in range(NEWTON_STEPS):
        score = [0.0] * size
        matrix = [[0.0] * size for _at in range(size)]
        s0 = 0.0
        s1 = [0.0] * size
        s2 = [[0.0] * size for _at in range(size)]
        at = 0
        rows = len(order)
        while at < rows:
            moment = times[order[at]]
            tied: "list[int]" = []
            while at < rows and times[order[at]] == moment:
                tied += [order[at]]
                at += 1
            for row in tied:
                x = x_rows[row]
                eta = 0.0
                for i in range(size):
                    eta += beta[i] * x[i]
                risk = exp(eta)
                s0 += risk
                for i in range(size):
                    s1[i] += risk * x[i]
                    line = s2[i]
                    rx = risk * x[i]
                    for j in range(i + 1):
                        line[j] += rx * x[j]
            died = [row for row in tied if events[row] > 0.5]
            if not died or s0 <= 0.0:
                continue
            count = float(len(died))
            for row in died:
                x = x_rows[row]
                for i in range(size):
                    score[i] += x[i]
            for i in range(size):
                mean_i = s1[i] / s0
                score[i] -= count * mean_i
                line = matrix[i]
                for j in range(i + 1):
                    line[j] += count * (s2[i][j] / s0 - mean_i * s1[j] / s0)
        for i in range(size):
            for j in range(i):
                matrix[j][i] = matrix[i][j]
        step = _solve(matrix, score)
        beta = [beta[i] + step[i] for i in range(size)]
        if max(abs(value) for value in beta) > 50.0:
            raise FitStopped("a separation")
        if max(abs(value) for value in step) < NEWTON_TOLERANCE * (1.0 + max(abs(value) for value in beta)):
            return beta
    raise FitStopped("no convergence")


def _log(value: float) -> float:
    """The natural logarithm by `frexp` and a series: only a Poisson model's first step reads it."""
    mantissa, exponent = math.frexp(value)
    ratio = (mantissa - 1.0) / (mantissa + 1.0)
    square = ratio * ratio
    total = 0.0
    power = ratio
    for k in range(40):
        total += power / (2 * k + 1)
        power *= square
    return 2.0 * total + exponent * rules.LN2


# -- THE MODELS OF THE PANEL -----------------------------------------------


@dataclasses.dataclass(frozen=True)
class Model:
    """One model of the panel: its family, outcome, predictors and, for a Cox model, its event column."""

    family: str
    outcome: str
    predictors: "tuple[str, ...]"
    event: str = ""
    clip: "tuple[float, float] | None" = None


@dataclasses.dataclass
class Design:
    """A model's complete cases on one table: the design rows, the outcome, the events, each row's group."""

    x_rows: "list[list[float]]"
    y: "list[float]"
    events: "list[float]"
    groups: "list[int]"


def design_of(view: View, model: Model, centre: "dict[str, tuple[float, float]]", groups: "bytes | None") -> Design:
    """A model's complete cases on a table: the design (standardized predictors, an intercept unless Cox), y, events.

    A count model's outcome is the count read back from its linear code,
    `lo + (code + 1/2) (hi - lo) / 256` (`Model.clip`), so the model reads
    the count's own scale between its clip rungs.
    """
    x_rows: "list[list[float]]" = []
    y: "list[float]" = []
    events: "list[float]" = []
    kept: "list[int]" = []
    outcome = view.value[model.outcome]
    event = view.value[model.event] if model.event else None
    columns = [view.value[name] for name in model.predictors]
    shifts = [centre[name] for name in model.predictors]
    intercept = model.family != "F6"
    for row in range(view.rows):
        target = outcome[row]
        if target is None:
            continue
        if model.clip is not None:
            target = model.clip[0] + (target + 0.5) * (model.clip[1] - model.clip[0]) / 256.0
        flag = 0.0
        if event is not None:
            held = event[row]
            if held is None:
                continue
            flag = held
        line: "list[float]" = [1.0] if intercept else []
        complete = True
        for at in range(len(columns)):
            value = columns[at][row]
            if value is None:
                complete = False
                break
            line += [(value - shifts[at][0]) / shifts[at][1]]
        if not complete:
            continue
        x_rows += [line]
        y += [target]
        events += [flag]
        kept += [groups[row] if groups is not None else 0]
    return Design(x_rows, y, events, kept)


def _fit(model: Model, design: Design, start: "list[float] | None") -> "list[float]":
    if len(design.x_rows) < SUPPORT:
        raise FitStopped("too few rows")
    if model.family == "F3":
        return least_squares(design.x_rows, design.y)
    if model.family == "F4":
        return glm(design.x_rows, design.y, "logistic", start)
    if model.family == "F5":
        return glm(design.x_rows, design.y, "poisson", start)
    return cox(design.y, design.events, design.x_rows, start)


def supported(model: Model, design: Design) -> bool:
    """Every defining cell of the model holds 22 rows on the sample and 11 in every half.

    The cells: the model's rows; a two-valued outcome's (or a Cox model's
    event's) events and non-events; each two-valued predictor's two
    levels, and on a two-valued outcome each level's events and
    non-events (S2 2.1).
    """
    offset = 0 if model.family == "F6" else 1
    flags = design.events if model.family == "F6" else design.y if model.family == "F4" else None
    counted: "list[dict[tuple[int, int, int], int]]" = [{} for _group in range(16)]
    two_valued = [at for at in range(len(model.predictors)) if len({line[offset + at] for line in design.x_rows[:2000]}) <= 2 and len({line[offset + at] for line in design.x_rows}) == 2]
    levels = {at: sorted({line[offset + at] for line in design.x_rows}) for at in two_valued}
    for row in range(len(design.x_rows)):
        held = counted[design.groups[row]]
        flag = 1 if flags is not None and flags[row] > 0.5 else 0
        keys = [(-1, 0, 0), (-1, 0, 1 + flag)]
        for at in two_valued:
            level = 0 if design.x_rows[row][offset + at] == levels[at][0] else 1
            keys += [(at, level, 0), (at, level, 1 + flag)]
        for key in keys:
            held[key] = held[key] + 1 if key in held else 1

    def holds(picked: "tuple[int, ...]", least: int) -> bool:
        total: "dict[tuple[int, int, int], int]" = {}
        for group in picked:
            for key in counted[group]:
                total[key] = total[key] + counted[group][key] if key in total else counted[group][key]
        cells = [(-1, 0)] + [(at, level) for at in two_valued for level in (0, 1)]
        for at, level in cells:
            rows = total[(at, level, 0)] if (at, level, 0) in total else 0
            if rows < least:
                return False
            if flags is not None:
                hits = total[(at, level, 2)] if (at, level, 2) in total else 0
                if hits < least or rows - hits < least:
                    return False
        return True

    return holds(ALL_GROUPS, SUPPORT) and all(holds(picked, HALF_SUPPORT) for picked in HALF_GROUPS)


def _halves_of(model: Model, design: Design, found: "list[float]") -> "list[list[float]]":
    """The model on the eight halves: least squares exactly; a logistic or count model by ONE Newton step from the sample's fit.

    The one-step estimator from the whole sample's coefficients is
    asymptotically the half's own fit (each half's information and score
    at the sample's coefficients, counted by group in one pass); a Cox
    model is fitted on each half, starting from the sample's coefficients.
    """
    if model.family == "F3":
        parts = moments_by_group(design.x_rows, design.y, design.groups)
        out: "list[list[float]]" = []
        for picked in HALF_GROUPS:
            matrix, vector = _added(parts, picked)
            out += [_solve(matrix, vector)]
        return out
    if model.family in ("F4", "F5"):
        parts = glm_pass(design.x_rows, design.y, found, "logistic" if model.family == "F4" else "poisson", design.groups)
        out = []
        for picked in HALF_GROUPS:
            matrix, score_vector = _added(parts, picked)
            step = _solve(matrix, score_vector)
            out += [[found[i] + step[i] for i in range(len(found))]]
        return out
    out = []
    for picked in HALF_GROUPS:
        chosen = set(picked)
        rows = [row for row in range(len(design.x_rows)) if design.groups[row] in chosen]
        part = Design([design.x_rows[row] for row in rows], [design.y[row] for row in rows], [design.events[row] for row in rows], [])
        out += [_fit(model, part, found)]
    return out


def _model_estimates(
    model: Model,
    views: "dict[str, View]",
    groups: bytes,
    centre: "dict[str, tuple[float, float]]",
    stops: "list[str]",
    left: "dict[str, int] | None" = None,
) -> "list[Estimate]":
    """A model's coefficients on the sample, the trial twin, the shuffle and the eight halves; its stop on the twin, named.

    A model whose design the support rule refuses gives no estimate and is
    counted in `left["models"]`.
    """
    design = design_of(views["sample"], model, centre, groups)
    if len(design.x_rows) < SUPPORT or not supported(model, design):
        if left is not None:
            left["models"] = left["models"] + 1 if "models" in left else 1
        return []
    try:
        found = _fit(model, design, None)
        halves = _halves_of(model, design, found)
    except FitStopped:
        return []
    sides: "dict[str, list[float] | None]" = {}
    for side in ("twin", "shuffle"):
        try:
            sides[side] = _fit(model, design_of(views[side], model, centre, None), found)
        except FitStopped as stopped:
            sides[side] = None
            if side == "twin":
                stops += [f"{FAMILY_LABEL[model.family]} of {model.outcome}: {stopped}"]
    offset = 0 if model.family == "F6" else 1
    out: "list[Estimate]" = []
    for at in range(len(model.predictors)):
        twin = sides["twin"]
        shuffle = sides["shuffle"]
        out += [
            Estimate(
                (model.family, model.outcome, model.predictors[at]),
                model.family,
                found[offset + at],
                None if twin is None else twin[offset + at],
                None if shuffle is None else shuffle[offset + at],
                [held[offset + at] for held in halves],
            )
        ]
    return out


FAMILY_LABEL = {
    "F3": "the linear model",
    "F4": "the logistic model",
    "F5": "the count model",
    "F6": "the Cox model",
}


# -- THE JUDGEMENT ---------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class FamilyWord:
    """One analysis family's judged word, with what it was judged on (the private report's line)."""

    family: str
    name: str
    word: str
    why: str
    supported: int
    inside: int
    replicate: "float | None"
    ceiling: "tuple[str, ...]" = ()
    # Each part's word, `(part, word, why, supported, inside, basis,
    # joint)`, where the family has parts (`inside` counted on `basis`
    # estimates, the joint ones where `joint`: Codex's item 14); the
    # family's word is the worst of them.
    parts: "tuple[tuple[str, str, str, int, int, int, bool], ...]" = ()
    # The estimates the share inside was read on: the joint ones, or every
    # supported one where fewer than JOINT_MINIMUM are joint.
    basis: int = 0
    joint: bool = False
    # Each trial key's word, in key order (the private report keeps them).
    keys: "tuple[str, ...]" = ()
    # The family's share of joint estimates among its supported ones (THE
    # TABLE WITHOUT RELATIONSHIPS reads it against twice chance).
    joint_share: "float | None" = None
    # Whether the share rule (or a run with no joint estimate) left it
    # unjudged: K-BC-11 reads these beside the overclaims (LANE ST RULINGS
    # 6 (1)(c)).
    unrelated: bool = False
    # The skewed columns of `ceiling` that hold a second code: the raw scale
    # alone is held at best approximate there (LANE ST RULINGS 6 (3), FIX 6).
    logged: "tuple[str, ...]" = ()
    # Whether the comparisons rule left it unjudged (fewer than
    # FAMILY_MINIMUM estimates the shuffle moves beyond their yardstick, not
    # every one past the line): K-BC-11 reads these beside the share rule's
    # (LANE ST RULINGS 7 (1)).
    few_comparisons: bool = False


@dataclasses.dataclass(frozen=True)
class PairWord:
    """One pair's judged word (the private report's line)."""

    columns: "tuple[str, str]"
    word: str
    why: str
    # The skewed columns of the pair (THE CEILING), and each key's word.
    ceiling: "tuple[str, ...]" = ()
    keys: "tuple[str, ...]" = ()
    # The word of its table alone, and the level its table was read at
    # (-1 where none supports it): what the pair read before its
    # correlation joined it (LANE ST RULINGS 4 (1)(a), the price).
    table: str = ""
    level: int = -1
    # Whether its RAW-SCALE correlation moved beyond its yardstick (the
    # extreme values beyond a clip, LANE ST RULINGS 5 (2)), and the skewed
    # columns of `ceiling` holding a second code (FIX 6).
    extreme: bool = False
    logged: "tuple[str, ...]" = ()


@dataclasses.dataclass(frozen=True)
class Controls:
    """The replicate's and the shuffle's shares inside, and whether the run's judgement stands."""

    replicate: "float | None"
    shuffle: "float | None"
    held: bool
    why: str
    # The share of the supported estimates that are JOINT (LANE ST RULINGS
    # 4 (6): under twice chance, the panel sees no relationship).
    joint: "float | None" = None


@dataclasses.dataclass(frozen=True)
class Judged:
    """The self-test's result: every family's and pair's judged word, the controls, the sample's size."""

    families: "tuple[FamilyWord, ...]"
    pairs: "tuple[PairWord, ...]"
    controls: Controls
    sample: int
    rows: int
    moved: int
    stops: "tuple[str, ...]"
    # The models of the panel, each named by its kind, outcome and partners.
    models: "tuple[str, ...]" = ()
    # What the support rule and RULE W2 left out (LANE ST RULINGS 4 (8)):
    # rate cells, correlations, models and pairs' tables under the support
    # rule, and pairs RULE W2 left `not judged`, under the first key.
    left: "tuple[tuple[str, int], ...]" = ()
    # Each trial key's controls, in key order.
    key_controls: "tuple[Controls, ...]" = ()


def _yardstick(estimate: Estimate) -> "tuple[float, float]":
    """The half-split yardstick `h` over the four splits, and the replicate's own over splits 1 to 3."""
    if estimate.kind == "distance":
        gaps = [estimate.halves[split] for split in range(4)]
    else:
        gaps = [estimate.halves[2 * split] - estimate.halves[2 * split + 1] for split in range(4)]
    whole = math.sqrt(sum(gap * gap for gap in gaps) / 4.0)
    rest = math.sqrt(sum(gap * gap for gap in gaps[1:]) / 3.0)
    return whole, rest


def _gaps(estimate: Estimate) -> "tuple[float | None, float | None, float]":
    """The twin's and the shuffle's gaps from the sample, and the replicate's (split 0's halves)."""
    if estimate.kind == "distance":
        return estimate.twin, estimate.shuffle, estimate.halves[0]
    twin = None if estimate.twin is None else abs(estimate.twin - estimate.sample)
    shuffle = None if estimate.shuffle is None else abs(estimate.shuffle - estimate.sample)
    return twin, shuffle, abs(estimate.halves[0] - estimate.halves[1])


@dataclasses.dataclass(frozen=True)
class Scored:
    """One estimate judged: inside for the twin (scaled), the replicate and the shuffle (unscaled)."""

    estimate: Estimate
    twin_inside: bool
    replicate_inside: bool
    shuffle_inside: bool
    recovery: "float | None"
    judged: bool
    joint: bool
    # The replicate's gap over the shuffle's, where the shuffle moves the
    # estimate beyond its yardstick: what a fresh half keeps (the control).
    replicate_recovery: "float | None" = None


def score(estimate: Estimate, sample: int, rows: int, floor: int) -> Scored:
    """An estimate against its yardstick: the twin's gap within `h * sqrt(n_s / n)`, RULE W2 on pairs."""
    whole, rest = _yardstick(estimate)
    scaled = whole * math.sqrt(sample / rows) if rows > 0 else whole
    twin, shuffle, replicate = _gaps(estimate)
    judged = True
    if estimate.kind == "distance" and rows * scaled < floor:
        judged = False
    twin_inside = twin is not None and twin <= scaled
    replicate_inside = replicate <= math.sqrt(2.0) * rest
    shuffle_inside = shuffle is not None and shuffle <= whole
    recovery: "float | None" = None
    replicate_recovery: "float | None" = None
    if twin is not None and shuffle is not None and shuffle > whole and shuffle > 0.0:
        recovery = twin / shuffle
        replicate_recovery = replicate / shuffle
    joint = estimate.kind != "distance" and abs(estimate.sample - estimate.null) > JOINT_AT * whole
    return Scored(estimate, twin_inside, replicate_inside, shuffle_inside, recovery, judged, joint, replicate_recovery)


def _median(values: "list[float]") -> float:
    ordered = sorted(values)
    middle = len(ordered) // 2
    return ordered[middle] if len(ordered) % 2 else 0.5 * (ordered[middle - 1] + ordered[middle])


def word_of(scored: "list[Scored]") -> "tuple[str, str, int, int, float | None, int, bool, bool]":
    """A family's word from its supported estimates: carried, approximate or not carried, with why.

    The share inside and the replicate's are read on the JOINT estimates
    (K-BC-01's family target counts those), on all supported ones where
    fewer than `JOINT_MINIMUM` are joint (LANE ST RULINGS 4 (2)(a)).
    Returns the word, why, the supported estimates, those inside, the
    replicate's share, the estimates the shares were read on, whether
    they are the joint ones, and whether the comparisons rule left it
    `not judged` (fewer than FAMILY_MINIMUM comparisons, not every one
    past the line: LANE ST RULINGS 7 (1)).
    """
    if len(scored) < FAMILY_MINIMUM:
        return NOT_JUDGED, f"fewer than {FAMILY_MINIMUM} supported estimates ({len(scored)})", len(scored), 0, None, 0, False, False
    joint = [one for one in scored if one.joint]
    basis = joint if len(joint) >= JOINT_MINIMUM else scored
    on_joint = len(joint) >= JOINT_MINIMUM
    inside = sum(1 for one in basis if one.twin_inside)
    replicate = sum(1 for one in basis if one.replicate_inside) / len(basis)
    share = inside / len(basis)
    recovered = [one.recovery for one in scored if one.recovery is not None]
    kept = [one.replicate_recovery for one in scored if one.replicate_recovery is not None]
    found = (len(scored), inside, replicate, len(basis), on_joint)
    near = share >= replicate - FAMILY_TARGET
    if near and len(recovered) < FAMILY_MINIMUM:
        # A COMPARISON SKIPPED IS NO AFFIRMATION (LANE ST RULINGS 5 (3),
        # Codex's item 5): what the twin keeps is set against what a fresh
        # half keeps only over FAMILY_MINIMUM estimates the shuffle moves
        # beyond their yardstick; with fewer, nothing says it keeps them.
        # EVERY COMPARISON PAST THE LINE (LANE ST RULINGS 7 (1), choice (b)):
        # where every comparison present reads `not carried` on its own
        # (`one_word`: outside its scaled yardstick, a relationship shown,
        # the twin's gap at least NOT_CARRIED_LINE of the shuffle's), the
        # family reads `not carried`; otherwise `not judged`. Either way the
        # reason counts the estimates showing a relationship that the trial
        # twin keeps inside, so 'about as often as the replicate' is never
        # the whole of it.
        kept_inside = (f"{sum(1 for one in joint if one.twin_inside)} of its {len(joint)} estimates beyond their "
                       "yardstick from their value were the columns unrelated are inside on the trial twin")
        compared = [one for one in scored if one.recovery is not None]
        if compared and all(one_word(one) == NOT_CARRIED for one in compared):
            return (NOT_CARRIED, "the trial twin keeps less of the relationships than the line between approximate and "
                    f"not carried on every estimate the shuffle moves beyond its yardstick ({len(compared)} of them, "
                    f"under the {FAMILY_MINIMUM} that setting what it keeps against a fresh half needs); "
                    f"{kept_inside}") + found + (False,)
        over = "" if on_joint else f" over all {len(scored)} of its supported estimates"
        return (NOT_JUDGED, f"inside the yardstick about as often as the replicate{over}, but only {len(recovered)} of "
                f"its estimates are moved beyond their yardstick by the shuffle, under the {FAMILY_MINIMUM} that "
                f"setting what it keeps against a fresh half needs; {kept_inside}") + found + (True,)
    keeps_as_a_half = _median(recovered) <= _median(kept) if recovered and kept else False
    if near and keeps_as_a_half:
        return (CARRIED, "inside the yardstick about as often as the replicate, and keeping the relationships as a fresh half does") + found + (False,)
    if near:
        return (APPROXIMATE, "inside the yardstick, but keeping less of the relationships than a fresh half of the sample") + found + (False,)
    if recovered and _median(recovered) >= NOT_CARRIED_LINE:
        return (NOT_CARRIED, "the trial twin keeps less of the relationships than the line between approximate and not carried") + found + (False,)
    return (APPROXIMATE, "outside the yardstick on some estimates") + found + (False,)


def one_word(scored: Scored) -> str:
    """One estimate's word: inside its scaled yardstick carried; at least half the shuffle's gap not carried; else approximate.

    `not carried` says the twin keeps no more of a relationship than a twin
    without any, so a correlation reads it only where the sample shows one
    (it is JOINT); a table's distance reads it where the shuffle moves the
    table beyond its yardstick, which is the relationship shown.
    """
    if scored.twin_inside:
        return CARRIED
    shown = scored.joint or scored.estimate.kind == "distance"
    if shown and scored.recovery is not None and scored.recovery >= NOT_CARRIED_LINE:
        return NOT_CARRIED
    return APPROXIMATE


def pair_word(
    table: "Scored | None", level: int, correlations: "list[Scored] | None", ceiling: "tuple[str, ...]"
) -> "tuple[str, str]":
    """A pair's word: the WORST of its table's word and its correlations' (LANE ST RULINGS 4 (1)(a) and 5 (2)).

    The table is read at the finest level its cells support (`pair_table`);
    a pair holding a fine column also reads its correlation on the code
    scale, on the second code where a column is skewed, and on the RAW
    SCALE where a column reads beyond its clip (key `raw`); THE CEILING
    holds the code-scale and raw-scale correlations of a pair holding a
    skewed column at best `approximate`. Any part left unjudged leaves the
    pair `not judged`.
    """
    if table is None:
        return NOT_JUDGED, "its table holds a cell under 22 rows on the sample, or 11 in a half, at every level (L0, L1 and L2)"
    if not table.judged:
        return NOT_JUDGED, "RULE W2: the yardstick at the whole table's precision is under the floor"
    if correlations is None:
        return NOT_JUDGED, "its correlation holds too few rows, or no spread, on the sample or in a half"
    said = [(one_word(table), f"its table at L{level}")]
    for scored in correlations:
        word = one_word(scored)
        scale = scored.estimate.part
        if ceiling and scored.estimate.key[3] in ("code", "raw") and word == CARRIED:
            word = APPROXIMATE
            scale += f" (at best approximate: {_listed(list(ceiling), ', ')} skewed)"
        said += [(word, f"its correlation {scale}")]
    worst = said[0]
    for one in said[1:]:
        if _rank(one[0]) > _rank(worst[0]):
            worst = one
    return worst[0], _listed([f"{text} {word}" for word, text in said], "; ")


def not_judged(why: str, words: "list[dict[str, object]]", sample: int = 0, rows: int = 0) -> Judged:
    """Every family and pair `not judged`, for one reason (the chain off, the controls failing, the self-test stopped)."""
    families = tuple(FamilyWord(code, name, NOT_JUDGED, why, 0, 0, None) for code, name in FAMILY_NAMES)
    pairs = tuple(PairWord(_pair_names(entry), NOT_JUDGED, why) for entry in words)
    return Judged(families, pairs, Controls(None, None, False, why), sample, rows, 0, ())


def _pair_names(entry: "dict[str, object]") -> "tuple[str, str]":
    names = entry["columns"] if "columns" in entry else []
    if isinstance(names, list) and len(names) == 2:
        return f"{names[0]}", f"{names[1]}"
    return "", ""


def _strongest(outcome: str, candidates: "list[str]", sample: View, cap: int) -> "tuple[str, ...]":
    """The outcome's strongest partners on the sample, by |r| on their numbers, at most `cap`."""
    ranked: "list[tuple[float, str]]" = []
    for name in candidates:
        if name == outcome:
            continue
        r = _correlation(_pair_sums(sample.value[outcome], sample.value[name], None)[0])
        if r is None:
            continue
        ranked += [(-abs(r), name)]
    return tuple(name for _r, name in sorted(ranked)[:cap])


def run(
    inputs: "chain.SelftestInputs | None",
    words: "list[dict[str, object]]",
    floor: int,
    off: str = "",
    constant: int = SELFTEST_CONSTANT,
    keys: int = TRIAL_KEYS,
) -> Judged:
    """The self-test on a description's inputs: every family's and pair's judged word, private only.

    `words` is the description's own `words` (4.6b.8), read for the pairs'
    order; `off` the reason no chain is published, where none is. The
    self-test runs under `keys` trial keys, `constant` plus 0, 1 and 2,
    ONE AFTER ANOTHER (never side by side: the memory of one key is let go
    before the next), and every family and pair reads the worst of the
    keys' words (LANE ST RULINGS 3 (2)(a)). Returns every family and pair
    `not judged` with the reason where the chain is off or a key's
    controls fail. No I/O of any kind; nothing is held past the call.
    """
    if inputs is None:
        return not_judged(off or "no chain is published for this table", words)
    found: "list[Judged]" = []
    for key in range(max(1, keys)):
        found += [judge_one(inputs, words, floor, constant + key)]
    return combined(found)


def combined(found: "list[Judged]") -> Judged:
    """The keys' results as one: each family and pair the worst of the keys' words, `not judged` where a key does not judge it."""
    first = found[0]
    controls = tuple(one.controls for one in found)
    failed = [at for at in range(len(found)) if not found[at].controls.held]
    family_keys = [tuple(one.families[at].word for one in found) for at in range(len(first.families))]
    pair_keys = [tuple(one.pairs[at].word for one in found) for at in range(len(first.pairs))]
    if failed:
        held = found[failed[0]].controls
        why = f"under trial key {failed[0]}, {held.why}" if len(found) > 1 else held.why
        families = tuple(
            dataclasses.replace(first.families[at], word=NOT_JUDGED, why=f"the self-test's controls failed: {why}",
                                supported=0, inside=0, replicate=None, parts=(), keys=family_keys[at], unrelated=False,
                                few_comparisons=False)
            for at in range(len(first.families))
        )
        pairs = tuple(
            PairWord(first.pairs[at].columns, NOT_JUDGED, f"the self-test's controls failed: {why}", first.pairs[at].ceiling, pair_keys[at],
                     logged=first.pairs[at].logged)
            for at in range(len(first.pairs))
        )
        return Judged(families, pairs, Controls(held.replicate, held.shuffle, False, why), first.sample, first.rows,
                      first.moved, first.stops, first.models, first.left, controls)
    families_out: "list[FamilyWord]" = []
    for at in range(len(first.families)):
        ones = [one.families[at] for one in found]
        unjudged = [one for one in ones if one.word == NOT_JUDGED]
        if unjudged:
            why = unjudged[0].why
            if len(unjudged) < len(ones):
                why = f"judged under {len(ones) - len(unjudged)} of the {len(ones)} trial keys only ({why})"
            worst = dataclasses.replace(unjudged[0], why=why)
        else:
            worst = ones[0]
            for one in ones[1:]:
                if _rank(one.word) > _rank(worst.word):
                    worst = one
        parts: "list[tuple[str, str, str, int, int, int, bool]]" = []
        for part in worst.parts:
            chosen_part = part
            for one in ones:
                for other in one.parts:
                    if other[0] == part[0] and chosen_part[1] != NOT_JUDGED and (
                        other[1] == NOT_JUDGED or _rank(other[1]) > _rank(chosen_part[1])
                    ):
                        chosen_part = other
            parts += [chosen_part]
        families_out += [dataclasses.replace(worst, parts=tuple(parts), keys=family_keys[at])]
    pairs_out: "list[PairWord]" = []
    for at in range(len(first.pairs)):
        ones_pairs = [one.pairs[at] for one in found]
        chosen = ones_pairs[0]
        table_word = chosen.table
        for one_pair in ones_pairs[1:]:
            if table_word != NOT_JUDGED and (one_pair.table == NOT_JUDGED or _rank(one_pair.table) > _rank(table_word)):
                table_word = one_pair.table
            if chosen.word == NOT_JUDGED:
                continue
            if one_pair.word == NOT_JUDGED or _rank(one_pair.word) > _rank(chosen.word):
                chosen = one_pair
        pairs_out += [dataclasses.replace(chosen, keys=pair_keys[at], table=table_word)]
    return Judged(tuple(families_out), tuple(pairs_out), first.controls, first.sample, first.rows, first.moved,
                  first.stops, first.models, first.left, controls)


def family_word(
    code: str,
    name: str,
    mine: "list[Scored]",
    ceiling: "tuple[str, ...]" = (),
    logged: "tuple[str, ...]" = (),
    none_joint: bool = False,
) -> FamilyWord:
    """One family between columns judged from its supported estimates: its word, its parts' words and why.

    A family whose share of joint estimates stands under twice chance
    (`sees_no_relationship`, the SHARE alone: LANE ST RULINGS 6 (1)(a)) is
    not judged, its reason giving its counts (`unrelated_reason`), and so
    is every family where no estimate of the run is joint (`none_joint`);
    otherwise its word is `word_of` its estimates and the worst of its
    parts' words.
    """
    joint_count = sum(1 for one in mine if one.joint)
    share = joint_count / len(mine) if mine else None
    if none_joint:
        return FamilyWord(code, name, NOT_JUDGED, NONE_JOINT, len(mine), 0, None, ceiling, joint_share=share,
                          unrelated=True, logged=logged)
    if len(mine) >= FAMILY_MINIMUM and sees_no_relationship(joint_count, len(mine)):
        return FamilyWord(code, name, NOT_JUDGED, unrelated_reason(joint_count, len(mine)), len(mine), 0, None, ceiling,
                          joint_share=share, unrelated=True, logged=logged)
    judged_word, reason, supported, inside, replicate, basis, on_joint, few = word_of(mine)
    part_names = sorted({one.estimate.part for one in mine if one.estimate.part})
    parts: "list[tuple[str, str, str, int, int, int, bool]]" = []
    for part in part_names:
        part_word, part_why, part_supported, part_inside, _replicate, part_basis, part_joint, _few = word_of(
            [one for one in mine if one.estimate.part == part]
        )
        parts += [(part, part_word, part_why, part_supported, part_inside, part_basis, part_joint)]
    worst = _rank(judged_word)
    for held_part in parts:
        if _rank(held_part[1]) > worst:
            worst = _rank(held_part[1])
            judged_word = held_part[1]
            reason = "the worst word of its parts"
    return FamilyWord(code, name, judged_word, reason, supported, inside, replicate, ceiling, tuple(parts), basis, on_joint,
                      (), share, logged=logged, few_comparisons=few and judged_word == NOT_JUDGED)


def judge_one(inputs: chain.SelftestInputs, words: "list[dict[str, object]]", floor: int, constant: int) -> Judged:
    """The self-test under ONE trial key: its trial twin, its shuffle, its splits and every word they give."""
    sample = len(inputs.hashes)
    seeds = row_seeds(inputs.hashes, constant)
    groups = groups_of(seeds)
    sampled = sample_view(inputs)
    source, moved = trial_twin(inputs, seeds)
    views = {"sample": sampled, "twin": mapped_view(sampled, source), "shuffle": mapped_view(sampled, shuffled(inputs, seeds))}
    source = {}
    left: "dict[str, int]" = {}
    names = [column.name for column in inputs.columns]
    by_name = {column.name: column for column in inputs.columns}
    fine = [column.name for column in inputs.columns if column.linear is not None]
    binaries = [column.name for column in inputs.columns if column.binary is not None]
    labels = [
        column.name
        for column in inputs.columns
        if column.linear is None and column.binary is None and column.role in (rules.ROLE_CATEGORICAL, rules.ROLE_LONG_TAIL)
    ]
    skewed = {column.name for column in inputs.columns if column.skew is not None and abs(column.skew) >= SKEW_CEILING}
    centre: "dict[str, tuple[float, float]]" = {}
    for name in fine + binaries:
        values = [value for value in sampled.value[name] if value is not None]
        if len(values) < 2:
            continue
        mean = math.fsum(values) / len(values)
        spread = math.sqrt(math.fsum((value - mean) * (value - mean) for value in values) / (len(values) - 1))
        centre[name] = (mean, spread if spread > 0.0 else 1.0)
    numbers = [name for name in fine + binaries if name in centre]
    coarse = {column.name: column.ladder.maps[2] for column in inputs.columns}
    estimates: "list[Estimate]" = []
    for outcome in binaries:
        outcome_flags = {side: views[side].value[outcome] for side in views}
        estimates += _rate_estimates("F1", outcome, outcome_flags, views, groups, [name for name in names if name != outcome], False, left)
        estimates += _rate_estimates("F1", outcome, outcome_flags, views, groups, [name for name in fine if name != outcome], True, left)
        strongest = _strongest(outcome, [name for name in numbers if name != outcome], sampled, TRIPLE_PARTNERS)
        estimates += _triple_rate_estimates(outcome, outcome_flags, views, groups, strongest, coarse, left)
    for name in labels:
        column = by_name[name]
        levels = label_levels(column)
        if levels:
            others = {other: by_name[other].ladder.counts[0] for other in names if other != name}
            estimates += _label_rate_estimates(name, column.missing, levels, views, groups, others, left)
    for column in inputs.columns:
        name = column.name
        blank_flags: "dict[str, list[float | None]]" = {}
        for side in views:
            view = views[side]
            if column.has is not None:
                blank_flags[side] = [0.0 if value is not None else 1.0 for value in view.value[name]]
            elif column.missing >= 0:
                blank_flags[side] = [1.0 if code == column.missing else 0.0 for code in view.l0[name]]
        if blank_flags:
            estimates += _rate_estimates("F9", name, blank_flags, views, groups, [other for other in names if other != name], False, left)
    correlations_found, raw_known = _correlation_estimates(views, groups, fine, skewed)
    estimates += correlations_found
    roles = {column.name: column.role for column in inputs.columns}
    dated = [column.name for column in inputs.columns if column.role in (rules.ROLE_DATETIME, rules.ROLE_CLOCK)]
    models: "list[Model]" = []
    linear = [name for name in fine if roles[name] in rules.NUMBER_ROLES and roles[name] != rules.ROLE_COUNT]
    counts = [name for name in fine if roles[name] == rules.ROLE_COUNT]
    for family, outcomes in (("F3", linear), ("F4", binaries), ("F5", counts)):
        for outcome in outcomes[:MODELS_A_KIND]:
            if outcome not in centre:
                continue
            values = [value for value in sampled.value[outcome] if value is not None]
            least = len(values)
            if family == "F4":
                hits = sum(1 for value in values if value > 0.5)
                least = min(hits, len(values) - hits)
            cap = min(PREDICTORS, least // 10 - 1)
            if cap < 1:
                continue
            clip: "tuple[float, float] | None" = None
            if family == "F5":
                count_column = by_name[outcome]
                if count_column.lo is None or count_column.hi is None or count_column.lo < 0.0:
                    continue
                clip = (count_column.lo, count_column.hi)
            models += [Model(family, outcome, _strongest(outcome, numbers, sampled, cap), "", clip)]
    for time_name, event in list(inputs.pairs)[:MODELS_A_KIND]:
        if time_name not in fine or event not in centre:
            continue
        flags_held = [value for value in sampled.value[event] if value is not None]
        hits = sum(1 for value in flags_held if value > 0.5)
        cap = min(PREDICTORS, hits // 10)
        partners = [name for name in numbers if name not in (time_name, event)]
        if cap >= 1:
            models += [Model("F6", time_name, _strongest(event, partners, sampled, cap), event)]
    stops: "list[str]" = []
    ran = 0
    named_models: "list[str]" = []
    for model in models:
        if not model.predictors:
            continue
        named_models += [
            f"{FAMILY_LABEL[model.family]} of {model.outcome}"
            + (f" with the event {model.event}" if model.event else "")
            + f" on {_listed(list(model.predictors), ', ')}"
        ]
        fitted = _model_estimates(model, views, groups, centre, stops, left)
        ran += 1 if fitted else 0
        estimates += fitted
    rows = inputs.rows
    scored = [score(one, sample, rows, floor) for one in estimates]
    joint = [one for one in scored if one.joint]
    replicate_share = sum(1 for one in scored if one.replicate_inside) / len(scored) if scored else None
    shuffle_share = sum(1 for one in joint if one.shuffle_inside) / len(joint) if joint else None
    joint_replicate = sum(1 for one in joint if one.replicate_inside) / len(joint) if joint else None
    joint_share = len(joint) / len(scored) if scored else 0.0
    held = True
    unrelated = False
    why = "the replicate lands inside about as often as a fresh sample, and the shuffle misses the relationships the sample shows"
    if replicate_share is None:
        held = False
        why = "the panel found no supported estimate on this table"
    elif replicate_share < REPLICATE_AT_LEAST:
        held = False
        why = f"the replicate landed inside on {replicate_share:.0%} of the estimates, under {REPLICATE_AT_LEAST:.0%}"
    elif shuffle_share is None or joint_replicate is None:
        unrelated = True
        why = NONE_JOINT
    elif shuffle_share > joint_replicate - SHUFFLE_UNDER:
        held = False
        why = "the column-wise shuffle landed inside about as often as the replicate: the panel sees no relationship the chain could carry"
    controls = Controls(replicate_share, shuffle_share, held, why, joint_share if scored else None)
    pair_scored: "dict[tuple[str, str], tuple[Scored | None, int, list[Scored] | None]]" = {}
    known = {(one.key[1], one.key[2], one.key[3]): one for one in estimates if one.family == "F2"}
    for entry in words:
        pair = _pair_names(entry)
        if pair[0] not in by_name or pair[1] not in by_name or pair in pair_scored:
            continue
        a = by_name[pair[0]]
        b = by_name[pair[1]]
        table, level = pair_table(views, groups, a, b)
        if table is None:
            left["pairs' tables"] = left["pairs' tables"] + 1 if "pairs' tables" in left else 1
        correlations: "list[Estimate] | None"
        if a.linear is not None and b.linear is not None:
            logged = (a.name in skewed and a.name in sampled.log) or (b.name in skewed and b.name in sampled.log)
            scales = ["code"] + (["log"] if logged else [])
            correlations = []
            for scale in scales:
                one = known[(a.name, b.name, scale)] if (a.name, b.name, scale) in known else known[(b.name, a.name, scale)] if (b.name, a.name, scale) in known else None
                if one is None:
                    left["correlations"] = left["correlations"] + 1 if "correlations" in left else 1
                    correlations = None
                    break
                correlations += [one]
            # THE RAW SCALE (LANE ST RULINGS 5 (2)), where a column of the
            # pair reads beyond its clip.
            raw_one = raw_known[(a.name, b.name)] if (a.name, b.name) in raw_known else raw_known[(b.name, a.name)] if (b.name, a.name) in raw_known else None
            if correlations is not None and raw_one is not None:
                correlations += [raw_one]
        else:
            correlations = pair_correlations(views, groups, a, b, skewed, left)
        table_scored = score(table, sample, rows, floor) if table is not None else None
        if table_scored is not None and not table_scored.judged:
            left["RULE W2"] = left["RULE W2"] + 1 if "RULE W2" in left else 1
        pair_scored[pair] = (
            table_scored,
            level,
            None if correlations is None else [score(one, sample, rows, floor) for one in correlations],
        )
    pairs: "list[PairWord]" = []
    for entry in words:
        pair = _pair_names(entry)
        pair_ceiling = tuple(name for name in pair if name in skewed and name in fine)
        pair_logged = tuple(name for name in pair_ceiling if name in sampled.log)
        if pair not in pair_scored:
            pairs += [PairWord(pair, NOT_JUDGED, "a column of the pair is not among the self-test's eligible columns", pair_ceiling,
                               logged=pair_logged)]
            continue
        table_scored, level, correlation_scored = pair_scored[pair]
        word, reason = pair_word(table_scored, level, correlation_scored, pair_ceiling)
        table_alone = NOT_JUDGED if table_scored is None or not table_scored.judged else one_word(table_scored)
        # THE RAW SCALE (LANE ST RULINGS 5 (2)): moved beyond its yardstick,
        # the pair reads at best approximate and its ceiling line names the
        # extreme values; a pair holding no number has no raw scale to read.
        extreme = correlation_scored is not None and any(
            one.estimate.key[3] == "raw" and not one.twin_inside for one in correlation_scored
        )
        if word != NOT_JUDGED and correlation_scored == []:
            reason += "; it holds no number, so it has no raw scale to read"
        elif word != NOT_JUDGED and correlation_scored is not None and not any(
            one.estimate.key[3] == "raw" for one in correlation_scored
        ):
            reason += "; on the raw scale as on the code scale, no reading of it lying beyond its clip"
        if unrelated:
            # NO ESTIMATE STANDS BEYOND ITS YARDSTICK: no pair is judged either.
            word, reason = NOT_JUDGED, NONE_JOINT
        pairs += [PairWord(pair, word, reason, pair_ceiling, (), table_alone, level, extreme, pair_logged)]
    left_out = tuple((kind, left[kind]) for kind in ("rate cells", "correlations", "models", "pairs' tables", "RULE W2") if kind in left)
    if not held:
        result = not_judged(f"the self-test's controls failed: {why}", words, sample, rows)
        return Judged(result.families, tuple(dataclasses.replace(one, ceiling=pairs[at].ceiling, logged=pairs[at].logged) for at, one in enumerate(result.pairs)),
                      controls, sample, rows, moved, tuple(stops), tuple(named_models), left_out)
    families: "list[FamilyWord]" = []
    for code, name in FAMILY_NAMES:
        if code == "F7":
            families += [FamilyWord(code, name, NOT_JUDGED, "the chain is published only where each person has one row; several rows a person are the patient layer's", 0, 0, None)]
            continue
        if code == "F8":
            families += [FamilyWord(code, name, NOT_JUDGED, "trained models are not judged in this version: their time is outside the self-test's", 0, 0, None)]
            continue
        if code == "F10":
            if not ran:
                families += [FamilyWord(code, name, NOT_JUDGED, "no model of the panel ran on the sample", 0, 0, None)]
            elif stops:
                families += [FamilyWord(code, name, NOT_CARRIED, f"{len(stops)} of the panel's {ran} models stop on the trial twin and not on the sample", ran, ran - len(stops), None)]
            elif len(dated) >= 2:
                # THE ORDER BETWEEN TWO DATES: no rule is published by this
                # layer (the rule step is lane RO's), so code that reads one
                # date against another (a duration, a follow-up) may stop on
                # the twin; at best approximate (K-BC-10's notion).
                families += [FamilyWord(code, name, APPROXIMATE, f"each of the panel's {ran} models runs on the trial twin, but the order between the dates {_listed(dated, ', ')} is carried only where a rule publishes it, so code reading one date against another may stop", ran, ran, None)]
            else:
                families += [FamilyWord(code, name, CARRIED, f"each of the panel's {ran} models runs on the trial twin as on the sample", ran, ran, None)]
            continue
        ceiling: "tuple[str, ...]" = ()
        if code in ("F2", "F3", "F4", "F5", "F6"):
            ceiling = tuple(sorted(column_name for column_name in skewed if column_name in fine))
        family_logged = tuple(column_name for column_name in ceiling if column_name in sampled.log)
        mine = [one for one in scored if one.estimate.family == code]
        families += [family_word(code, name, mine, ceiling, family_logged, unrelated)]
    return Judged(tuple(families), tuple(pairs), controls, sample, rows, moved, tuple(stops), tuple(named_models), left_out)


# -- THE PRIVATE REPORT (contract 4.6b.8, the owner's R7) ------------------

BEFORE_THE_POLISH = "Judged on the arrangement the walk deals, before the polish."
ACT_ON = (
    "WHICH GRADE TO ACT ON. Act on the judged grade: it was measured on this table. The structural grade is "
    "what the people the twin is shared with see."
)
# WHICH TWIN TO USE, as contract 4.6b.8 amended on 2026-11-05 states it
# (LANE ST RULINGS 4 (1)(b)): the twin's numbers stand in for the table's
# only where a pair or an analysis is JUDGED carried; an exact pair is
# exact at its family's published bands, and no more.
WHICH_TWIN = (
    "WHICH TWIN TO USE. Where a pair or an analysis is judged carried, the twin's numbers can stand in for your "
    "table's. A pair that reads exact is exact at its family's published bands: an analysis at those bands gives "
    "your table's numbers on the twin, and any other analysis of the pair reads as its judged word says. Where a "
    "pair reads implied, or a pair or an analysis is judged approximate, not carried or not judged, develop the "
    "code on the twin and run it unchanged on your real table. In every case the code is developed on the twin "
    "and run unchanged on the real table."
)
EXACT_AT = "exact at its family's published bands"
# On a sample smaller than the table (LANE ST RULINGS 4 (4)): the trial
# twin is dealt at the sample's precision and judged at the table's, so
# pairs read approximate more often than on a larger sample.
SMALLER_SAMPLE = (
    "On a sample smaller than your table, pairs read approximate more often than they would on a larger sample: "
    "that is an underclaim, never an overclaim."
)
# RULE W2's measured scope (LANE ST RULINGS 5 (6), Codex's item 13): `n`
# times the scaled yardstick is `sqrt(n n_s)` times the sample's, at least
# 20,000 times it on a table of 20,000 rows or more.
RULE_W2_SCOPE = (
    "RULE W2 leaves a pair not judged where your table's rows times the pair's yardstick at your table's "
    "precision fall under the floor. At the floor of 11 on a table of 20,000 rows or more, that is a pair whose "
    "yardstick on the sample is under 11 in 20,000, its table reading almost exactly alike in all four "
    "half-splits (a yardstick of nought is left out at any size); a raised floor (--smallest-group) leaves out more."
)
# A pair's word is a property of one description (LANE ST RULINGS 6 (4)):
# the chain is drawn under the description's name and key.
PAIRS_BELONG = (
    "Each pair's words belong to this description: the chain is drawn under its name and key, so the same table "
    "described under another name may place other families and read other words."
)
COMPLETE_FOLLOW_UP = "on a table where every patient has every visit, change over visits is not published in December"
NOT_FLAT = "approximate or unconstrained, NOT flat"
# The private report's file is `<the table's name>-private-report` with the
# text file's ending, in the private folder. It is written by a switched
# profile run alone, so it is not among the files a shipped full run
# leaves behind (tests/test_claim_inventory.py counts those); the landing
# that ships the switch counts it there (lanes CHON and CHc).
REPORT_FILE = "private-report"
FOLDER = "private-reports"
# The letters a table's name keeps in its private report's file name; any
# other becomes `_`, and a digest of the exact name follows (`report_stem`).
NAME_LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_."
# At most this many of the name's letters are kept, so a long name still
# makes a file name every filesystem takes.
NAME_KEPT = 80
# The chain's note where no chain is published (`chain._off`): the reason
# follows it, and the private report reads it with this prefix's own
# length (Codex's item 16 of lane ST's review).
OFF_PREFIX = "no chain is published: "


def report_stem(name: str) -> str:
    """The private report's file stem: the name's letters a file name keeps (any other `_`), a dash, a digest of the EXACT name.

    Two different names never share one report (LANE ST RULINGS 5 (1)(a),
    Codex's item 1): `trial A` and `trial_A`, or two names that differ only
    in case on a filesystem that folds case, each keep a file of their own,
    and the same name always finds its own. The digest is twelve
    hexadecimal figures of SplitMix64 folded over the name's UTF-8 bytes
    and their count, in Python integers: a name, not a secret.
    """
    kept = ""
    for letter in name[:NAME_KEPT]:
        kept += letter if letter in NAME_LETTERS else "_"
    data = bytes(name, "utf-8", "surrogatepass")
    state = SELFTEST_CONSTANT
    for byte in data:
        state = splitmix64(state ^ (byte + 1))
    state = splitmix64(state ^ (len(data) << 8))
    return f"{kept or 'table'}-{state & 0xFFFFFFFFFFFF:012x}"


def _complete_follow_up(census: object) -> bool:
    """Every patient holds one number of rows: one census band holds them all, or the open top band does at `lo` rows each."""
    if not isinstance(census, dict):
        return False
    bands = census["bands"] if "bands" in census else []
    top = census["top"] if "top" in census else None
    lo = census["lo"] if "lo" in census else None
    held = [band for band in bands if isinstance(band, dict) and isinstance(band["patients"] if "patients" in band else None, int) and band["patients"] > 0] if isinstance(bands, list) else []
    top_patients = top["patients"] if isinstance(top, dict) and "patients" in top else 0
    top_rows = top["rows"] if isinstance(top, dict) and "rows" in top else 0
    if not isinstance(top_patients, int) or not isinstance(top_rows, int):
        return False
    if len(held) == 1 and top_patients == 0:
        return True
    return not held and top_patients > 0 and isinstance(lo, int) and top_rows == top_patients * lo


def patient_lines(grain: object, off: "str | None" = None) -> "list[str]":
    """The patient words (contract 4.6c.11), read from `grain` as 4.6c.9 writes it, private only.

    Which groups' trends over visits a published `Q_P` carries, which only
    the generation method's extension implies (approximate or
    unconstrained, NOT flat), and the complete-follow-up sentence where
    every patient holds every visit. `off` is the reason no chain is
    published, None where one is: where it is the table's several rows a
    person (`chain.OFF_PERSON`), the line says so, and that the description
    describes none of them (LANE ST RULINGS 6 (3), FIX 5), never that each
    row is one person's; where it is one of the subject question's holds
    (`chain.OFF_SUBJECT`, `chain.OFF_NO_PERSON`, `chain.OFF_HELD_REPEATS`),
    the line gives that reason, and never that each row is one person's.
    """
    if not isinstance(grain, dict):
        if off == chain.OFF_PERSON:
            return [
                "This table holds several rows a person, and this description describes none of them: no chain "
                "between columns and no patient layer is published for it."
            ]
        if off in (chain.OFF_SUBJECT, chain.OFF_NO_PERSON, chain.OFF_HELD_REPEATS):
            # The subject question's holds (lane GRa, plan P4-D449): nothing
            # published says each row is one person's, so the line says why
            # no chain stands (batch 4q's merge of lane ST).
            return [f"This description carries no patient layer and no chain between columns: {off}."]
        return ["This description carries no patient layer: each row is read as one person's."]
    person = grain["person"] if "person" in grain else ""
    out = [f"The patient layer stands, by {person}."]
    trend = grain["trend"] if "trend" in grain else []
    carried: "dict[str, list[str]]" = {}
    for entry in trend if isinstance(trend, list) else []:
        if not isinstance(entry, dict):
            continue
        column = f"{entry['column']}" if "column" in entry else ""
        cell = entry["cell"] if "cell" in entry else []
        label = _listed([f"{part}" for part in cell], " and ") if isinstance(cell, list) else f"{cell}"
        carried[column] = carried[column] + [label] if column in carried else [label]
    grid = grain["grid"] if "grid" in grain else []
    trending = [f"{entry['column']}" for entry in grid if isinstance(entry, dict) and "column" in entry] if isinstance(grid, list) else []
    for column in sorted(set(trending) | set(carried)):
        groups = carried[column] if column in carried else []
        if groups:
            out += [
                f"Change over visits of {column}: carried by a published trend for the groups {_listed(groups, '; ')}. "
                f"Every other group's trend over visits comes back only as the published trends and the generation "
                f"method's extension imply it: {NOT_FLAT}."
            ]
        else:
            out += [
                f"Change over visits of {column}: no trend is published; it comes back only as the generation "
                f"method's extension implies it: {NOT_FLAT}."
            ]
    if not trending and not carried:
        out += [f"Change over visits: no trend is published; every group's trend comes back as the generation method's extension implies it: {NOT_FLAT}."]
    if _complete_follow_up(grain["census"] if "census" in grain else None):
        out += [COMPLETE_FOLLOW_UP[0].upper() + COMPLETE_FOLLOW_UP[1:] + "."]
    return out


def _percent(share: "float | None") -> str:
    return "none" if share is None else f"{round(100 * share)}%"


def _keys_said(keys: "tuple[str, ...]") -> str:
    """Each trial key's word, in key order: `under the trial keys: carried, carried, approximate`."""
    return "under the trial keys: " + _listed(list(keys), ", ") if keys else ""


def report_text(
    judged: Judged,
    words: "list[dict[str, object]]",
    notes: "tuple[str, ...]",
    counts: "dict[str, int]",
    name: str,
    key_file: str,
    grain: object = None,
    off: "str | None" = None,
    not_dates: "tuple[str, ...]" = (),
) -> str:
    """The private report's text: both grades for every family and pair, which to act on, which twin to use.

    `words` is the description's own `words`; `notes` the chain's private
    notes (why a family was not placed, the refusals, why the chain is
    off); `counts` its counters, read for rule B's moments by kind and
    reason; `key_file` the key file's PATH (never the key); `grain` the
    description's patient layer as 4.6c.9 writes it, or None; `off` the
    reason no chain is published, None where one is; `not_dates` the
    columns of dates whose twin writes record numbers
    (`generation.dates_written_as_record_numbers`, read by
    `cli._dates_not_carried`), inside which code run unchanged reads
    N (Codex's review of batch 4q, item 3). Where no chain is
    published the structural grades are the ones the twin's shared report
    prints for such a description (`chain_grades.off_grades`: `N` for every
    family that needs a chain, `E` only for code run unchanged within one
    column), so the two reports never disagree (LANE ST RULINGS 5 (3),
    Codex's item 7). A fixed function of its arguments; no I/O of any kind.
    """
    rule = "=" * 72
    published = chain_grades.pair_words(words)
    pinned = any(word == "pinned" for _first, _second, word in published)
    lines = [
        rule,
        f"synthtwin: the PRIVATE report on {name}",
        rule,
        "",
        "This report is for you, who ran synthtwin on your own table. It is not part of the description,",
        "the twin, the questions file or the shared report, and it stays with you: it holds what the",
        "self-test measured on your table, which the people the twin is shared with never see.",
        "",
        ACT_ON,
        "",
        WHICH_TWIN,
        "",
    ]
    if judged.sample:
        lines += [
            f"Judged on a sample of {judged.sample} rows of your {judged.rows}-row table, at the precision of your whole table.",
            BEFORE_THE_POLISH,
        ]
        if judged.sample < judged.rows:
            lines += [SMALLER_SAMPLE]
        lines += [
            f"Each word is the worst of {max(1, len(judged.key_controls))} trial keys, run one after another.",
            "",
            "THE CONTROLS",
        ]
        for at in range(len(judged.key_controls)):
            held = judged.key_controls[at]
            lines += [
                f"  Trial key {at}: the replicate (one half of the sample against the other) landed inside on "
                f"{_percent(held.replicate)} of the estimates; a column-wise shuffle on {_percent(held.shuffle)} of "
                "those that show a relationship."
            ]
        if not judged.key_controls:
            lines += [
                f"  The replicate landed inside on {_percent(judged.controls.replicate)} of the estimates; a column-wise "
                f"shuffle on {_percent(judged.controls.shuffle)} of those that show a relationship."
            ]
        lines += [f"  {'The judgement stands' if judged.controls.held else 'Nothing is judged'}: {judged.controls.why}."]
    else:
        lines += [f"The self-test did not run, so nothing is judged: {judged.controls.why}."]
    lines += [
        "",
        "ANALYSIS FAMILIES: the structural grade, then the judged grade",
    ]
    judged_by = {family.family: family for family in judged.families}
    grades = (
        chain_grades.off_grades(not_dates)
        if off is not None
        else chain_grades.family_grades(pinned, isinstance(grain, dict), (), not_dates)
    )
    for code, family_name, grade in grades:
        found = judged_by[code]
        detail = f"{found.why}"
        if found.supported and found.word != NOT_JUDGED:
            if found.basis and found.joint:
                detail += f"; {found.inside} of its {found.basis} joint estimates inside (of {found.supported} supported)"
            else:
                detail += f"; {found.inside} of {found.supported} supported estimates inside"
            if found.replicate is not None:
                detail += f", the replicate {_percent(found.replicate)}"
        if found.keys:
            detail += f"; {_keys_said(found.keys)}"
        lines += [f"  {code} {family_name}: structural {grade}; judged {found.word} ({detail})."]
        for part, part_word, part_why, part_supported, part_inside, part_basis, part_joint in found.parts:
            # Each part's count on its own basis (Codex's item 14): its joint
            # estimates where its shares were read on them.
            if part_word == NOT_JUDGED:
                part_said = part_why
            elif part_joint:
                part_said = f"{part_inside} of its {part_basis} joint estimates inside, of {part_supported} supported"
            else:
                part_said = f"{part_inside} of {part_supported} supported estimates inside"
            lines += [f"      {part}: judged {part_word} ({part_said})."]
        lines += _ceiling_lines(found.ceiling, found.logged)
    lines += ["", "PAIRS OF COLUMNS: the structural word, then the judged word", f"  {PAIRS_BELONG}"]
    judged_pairs = {pair.columns: pair for pair in judged.pairs}
    for first, second, word in published:
        pair = judged_pairs[(first, second)] if (first, second) in judged_pairs else None
        structural = EXACT_AT if word == "exact" else word
        said = f"judged {NOT_JUDGED}"
        if pair is not None:
            reason = pair.why
            if pair.keys and len(set(pair.keys)) > 1:
                reason += f"; {_keys_said(pair.keys)}"
            said = f"judged {pair.word} ({reason})"
        lines += [f"  {first} and {second}: structural {structural}; {said}."]
        if pair is not None:
            lines += _ceiling_lines(pair.ceiling, pair.logged)
            if pair.extreme:
                lines += [f"      On the raw scale of {first} and {second} (extreme values): at best approximate."]
    lines += ["", "THE PANEL'S MODELS"]
    lines += [f"  {model}." for model in judged.models] or ["  None: no outcome of this table gave the panel a model."]
    lines += [
        f"  At most {MODELS_A_KIND} outcomes of each kind are modelled, the first in the table's order, so the "
        "self-test's time stays inside the owner's hours."
    ]
    lines += ["", "WHAT THE SUPPORT RULE AND RULE W2 LEFT OUT (under the first trial key)"]
    left = dict(judged.left)
    held_out = [left[kind] if kind in left else 0 for kind in ("rate cells", "correlations", "models", "pairs' tables", "RULE W2")]
    lines += [
        f"  Under 22 rows on the sample, or 11 in a half, in a defining cell: {held_out[0]} rate cells, "
        f"{held_out[1]} correlations, {held_out[2]} models and {held_out[3]} pairs' tables at every level.",
        f"  Left not judged by RULE W2: {held_out[4]} pairs. {RULE_W2_SCOPE}",
    ]
    lines += ["", "WHAT THE DESCRIPTION LEFT OUT, AND WHY"]
    lines += [f"  {note}" for note in notes] or ["  Nothing was left out by the chain's own rules."]
    if judged.moved:
        lines += [f"  The trial twin dealt {judged.moved} family or families against a moved target."]
    lines += [f"  Stops on the trial twin: {stop}." for stop in judged.stops]
    lines += ["", "MOMENTS BETWEEN COLUMNS (the owner's rule B), by kind and reason"]
    moment_lines = [f"  {key[8:]}: {counts[key]}" for key in sorted(counts) if key[:8] == "moments "]
    lines += moment_lines or ["  None was counted: no moment layer stands in this description."]
    lines += ["", "SEVERAL ROWS A PERSON"]
    lines += [f"  {line}" for line in patient_lines(grain, off)]
    lines += [
        "",
        "THE KEY",
        f"  The installation's private key file is at {key_file}. This report never holds the key.",
        "",
    ]
    return _listed(lines, "\n")


def _ceiling_lines(ceiling: "tuple[str, ...]", logged: "tuple[str, ...]") -> "list[str]":
    """THE CEILING's lines: the raw scale of a skewed column holding a second code, the raw or log scale of one without.

    A skewed column with a second code reads its log scale on that code
    (judged on its own), so only its raw scale is held at best approximate
    (LANE ST RULINGS 6 (3), FIX 6).
    """
    raw_only = [name for name in ceiling if name in logged]
    both = [name for name in ceiling if name not in logged]
    out: "list[str]" = []
    if raw_only:
        out += [f"      On the raw scale of {_listed(raw_only, ', ')} (skewed): at best approximate."]
    if both:
        out += [f"      On the raw or log scale of {_listed(both, ', ')} (skewed): at best approximate."]
    return out


def _listed(parts: "list[str]", between: str) -> str:
    """The parts written one after another with `between` between them."""
    out = ""
    for at in range(len(parts)):
        out += (between if at else "") + f"{parts[at]}"
    return out
