"""THE INSIDE RECORD'S LINKS ZONE (lane W5-F14): a table joined to another table of its study by the person column.

WHY IT EXISTS. Two tables of one study -- a cohort of one row a patient,
and the orders, visits or results of those patients -- are joined by the
column that names the person. Each table's twin is made on its own, so a
join of two twins found its keys only where both columns happened to be
written in one layout, and how many rows a person holds in one table
never followed that person's columns in the other: a count of orders by
diabetes, the share of the cohort with an order, a rate per person in a
group. This zone carries how the two real tables join, and the twin of
the second table is written over the persons of the first table's twin.

WHAT IT CARRIES (fitted inside, at `synthtwin profile TABLE --linked-to
OTHER`, on the two real tables): how many of TABLE's persons are found in
OTHER; and how many rows each person of OTHER holds in TABLE as a function
of that person's own columns in OTHER -- a Poisson fit of the count on the
columns that pass a score test at the chi-square quantile of
`inside_relations.GATE_LEVEL` (overdispersion read off the fit's Pearson
statistic), and then, in `BINS` bins of the fit's linear predictor, the
distribution of each person's place among all persons of OTHER ordered by
their rows in TABLE (`POINTS` quantiles). It holds the columns' names,
the label levels the fit uses, the coefficients, the bins' cut points and
the quantiles. No row, no key, no person's values: its size depends on
the columns, the levels and the bins, never on the rows.

THE LINK (`synthtwin generate DESCRIPTION --linked-to OTHER_DESCRIPTION`).
OTHER's twin is built from its own description at the same seed, the twin
`synthtwin generate OTHER_DESCRIPTION --seed K` writes, and each person of
this twin -- a block of rows sharing a key -- is given a person of OTHER's
twin: each person of OTHER's twin draws a place from its bin's quantiles,
and the persons ordered by their places take this twin's blocks ordered by
their rows, the largest first, so a person with more rows here is a person
whose columns in OTHER hold more on the real tables, and as many blocks
are found in OTHER as the real share says; the rest keep keys of their
own that OTHER's twin does not hold. The rows of a block keep every cell
but the key.

NO TWIN KEY IS A REAL ONE, BY CONSTRUCTION. A key this twin takes from
OTHER's twin is a made-up key of OTHER's (never one of OTHER's real keys),
and the link is made only where every key of OTHER's twin is written wider,
merged, than every real key of this table can be (`spill_bound`, read off
this description alone: every real cell's merged key is shorter); a key a
block keeps of its own is this twin's own made-up key or one written in
the same width and checked the same way, AND against OTHER's own bound
(read off OTHER's description), so a key written anew is a real key of
neither table (batch 4y's fix round, Codex's review of the batch, item 4);
where OTHER publishes no bound, no key is written anew. Where the bound cannot be read,
or a key of OTHER's twin is not wide enough, nothing is linked and the
twin is the one its description makes.

ZONES. The fit runs at describe time and reads both tables' cells handed
to it as text; the link runs at generate time on the two twins' cells. Both
are Python integers and binary64 `+ - * /`, `math.sqrt` and `math.fsum`, the
logarithm, exponential and normal quantile of `chain_walk`, and a fixed
whole-number hash of the seed (`inside_relations.mixed`): the same record,
twins and seed give the same keys on every computer. No I/O.
"""

import dataclasses
import math

from synthtwin import chain_walk, inside_relations, parsing

ZONE = "links"
ZONE_VERSION = 1
# The bins of the fit's linear predictor, and the quantiles of a person's place kept in each.
BINS = 20
POINTS = 41
# The persons of the linked table a fit reads: every one up to this many, else a fixed hashed choice of about as many.
FIT_CAP = 50_000
# A column of numbers: at least this share of its present cells read as one number.
READ_SHARE = 0.9
# A label column: its commonest levels kept, each held by at least `MIN_PERSONS` persons, covering at least
# `KEPT_SHARE` of the persons; every other level reads as its commonest.
LEVEL_CAP = 12
MIN_PERSONS = 20
KEPT_SHARE = 0.5
# The blocks a fit takes at most.
SELECT_CAP = 12
# A key of its own for an unlinked block: the tries of a new spelling before the block is linked instead.
OWN_KEY_TRIES = 64
_ITERATIONS = 25
_CHANGE = 1e-8
_ETA_CAP = 30.0
_MASK64 = (1 << 64) - 1

NUMBER = "number"
LABEL = "label"
# A term of the fit: a number's normal score, its square, its empty-or-word indicator; a label level's indicator;
# the normal score of a person's rows in the linked table, where a person holds several there.
SCORE, SQUARE, MISSING, LEVEL, ROWS = "score", "square", "missing", "level", "rows"

# Why a link was not made (`Linked.refused`).
REFUSED_NO_BOUND = "no bound"
REFUSED_NOT_WIDER = "not wider"
REFUSED_NO_KEY = "no key column"
REFUSED_NO_PERSONS = "no persons"


class LinksError(ValueError):
    """The record's links zone cannot be read; the twin is then left as its description makes it."""


def _bare(cell: object) -> str:
    if not isinstance(cell, str):
        raise TypeError("synthtwin reads a table's cells as text only.")
    return cell.strip()


# -- the persons of each table --------------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class Persons:
    """The persons a key column names, in the order each first appears: its key, its first row, its rows."""

    keys: "list[str]"
    first: "list[int]"
    rows: "list[int]"


def persons_in(cells: "list[str]") -> Persons:
    """Each different key of a column (trimmed; an empty cell is no person), its first row and its rows. No I/O."""
    seen: "dict[str, int]" = {}
    keys: "list[str]" = []
    first: "list[int]" = []
    rows: "list[int]" = []
    for row in range(len(cells)):
        key = _bare(cells[row])
        if not key:
            continue
        if key in seen:
            rows[seen[key]] += 1
            continue
        seen[key] = len(keys)
        keys += [key]
        first += [row]
        rows += [1]
    return Persons(keys, first, rows)


# -- the linked table's columns, a person at a time ---------------------------------------------------------------


def _scores(values: "list[float | None]") -> "list[float]":
    """Each present value's normal score among the present values (mid-ranks for ties); 0.0 where none."""
    pairs: "list[tuple[float, int]]" = []
    for at in range(len(values)):
        value = values[at]
        if value is not None:
            pairs += [(value, at)]
    present = sorted(pairs)
    out = [0.0 for _at in range(len(values))]
    count = len(present)
    start = 0
    while start < count:
        end = start
        while end + 1 < count and present[end + 1][0] == present[start][0]:
            end += 1
        score = chain_walk.normal_score((start + end + 1) / (2 * count))
        for at in range(start, end + 1):
            out[present[at][1]] = score
        start = end + 1
    return out


def _numbers(cells: "list[str]") -> "list[float | None]":
    return [inside_relations.number_of(_bare(cell)) for cell in cells]


def _number_kind(cells: "list[str]") -> bool:
    """Whether a column of persons' cells reads as numbers: `READ_SHARE` of its present cells, two values or more."""
    present = 0
    read = 0
    seen: "dict[float, bool]" = {}
    for cell in cells:
        if not _bare(cell):
            continue
        present += 1
        value = inside_relations.number_of(_bare(cell))
        if value is not None:
            read += 1
            seen[value] = True
    return present >= MIN_PERSONS and read >= READ_SHARE * present and len(seen) >= 2


def _levels(cells: "list[str]") -> "list[str]":
    """A label column's kept levels, the commonest first (ties by their spelling), or none where it is no label."""
    counts: "dict[str, int]" = {}
    for cell in cells:
        level = _bare(cell)
        counts[level] = (counts[level] if level in counts else 0) + 1
    ranked = sorted([(-counts[level], level) for level in counts])
    kept = [level for negative, level in ranked[:LEVEL_CAP] if -negative >= MIN_PERSONS]
    covered = 0
    for level in kept:
        covered += counts[level]
    if len(kept) < 2 or covered < KEPT_SHARE * len(cells):
        return []
    return kept


@dataclasses.dataclass(frozen=True)
class Column:
    """One column of the linked table as the fit reads it: its kind, a label's kept levels, a number's empties."""

    name: str
    kind: str
    levels: "tuple[str, ...]"
    missing: bool


def _column_of(name: str, cells: "list[str]") -> "Column | None":
    if _number_kind(cells):
        empty = 0
        for value in _numbers(cells):
            if value is None:
                empty += 1
        return Column(name, NUMBER, (), MIN_PERSONS <= empty <= len(cells) - MIN_PERSONS)
    levels = _levels(cells)
    if levels:
        return Column(name, LABEL, tuple(levels), False)
    return None


def _term_values(term: "tuple[str, str, str]", cells: "list[str]") -> "list[float]":
    """One term's value for each person, from the persons' cells of its column."""
    kind, _name, level = term
    if kind == LEVEL:
        return [1.0 if _bare(cell) == level else 0.0 for cell in cells]
    values = _numbers(cells)
    if kind == MISSING:
        return [1.0 if value is None else 0.0 for value in values]
    scores = _scores(values)
    if kind == SQUARE:
        return [score * score - 1.0 if value is not None else 0.0 for score, value in zip(scores, values)]
    return scores


def _rows_term(persons: Persons) -> "list[float]":
    return _scores([float(held) for held in persons.rows])


def _blocks(columns: "list[Column]", repeats: bool) -> "list[tuple[tuple[str, str, str], ...]]":
    """The candidate blocks of the fit, in the linked table's order: a number's score, square and empties; a label's levels."""
    out: "list[tuple[tuple[str, str, str], ...]]" = []
    if repeats:
        out += [((ROWS, "", ""),)]
    for column in columns:
        if column.kind == NUMBER:
            out += [((SCORE, column.name, ""),), ((SQUARE, column.name, ""),)]
            if column.missing:
                out += [((MISSING, column.name, ""),)]
        else:
            out += [tuple([(LEVEL, column.name, level) for level in column.levels[1:]])]
    return out


# -- the Poisson fit -------------------------------------------------------------------------------------------------


def _poisson_deviance(response: "list[float]", eta: "list[float]") -> float:
    terms: "list[float]" = []
    for y, e in zip(response, eta):
        mean = chain_walk.exponential(min(_ETA_CAP, max(-_ETA_CAP, e)))
        terms += [(y * chain_walk.natural_log(y / mean) if y > 0.0 else 0.0) - (y - mean)]
    return 2.0 * math.fsum(terms)


def poisson(columns: "list[list[float]]", response: "list[float]") -> inside_relations.Fit:
    """A Poisson fit with the log link by iteratively reweighted least squares (the first term the intercept), ridged.

    A step that raises the deviance is halved until it does not. The fit's
    `scale` is its overdispersion, Pearson's statistic over the degrees of
    freedom left and never under one, so a score test of a block reads
    counts more spread than Poisson's as they are (`inside_relations
    .score_statistic` divides by it). Deterministic; raises nothing.
    """
    rows = len(response)
    size = len(columns)
    mean_all = max(math.fsum(response) / max(1, rows), 1e-9)
    beta = [0.0 for _a in range(size)]
    beta[0] = chain_walk.natural_log(mean_all)
    lower: "list[list[float]]" = []
    dropped: "list[bool]" = []
    deviance = _poisson_deviance(response, inside_relations.predictor(columns, beta, rows))
    for _step in range(_ITERATIONS):
        eta = inside_relations.predictor(columns, beta, rows)
        means = [chain_walk.exponential(min(_ETA_CAP, max(-_ETA_CAP, e))) for e in eta]
        weights = [max(m, 1e-10) for m in means]
        working = [e + (y - m) / w for e, y, m, w in zip(eta, response, means, weights)]
        lower, dropped = inside_relations.information(columns, weights)
        weighted = [w * z for w, z in zip(weights, working)]
        moved = inside_relations.solved(
            lower, dropped, [0.0 if dropped[a] else inside_relations.dot(columns[a], weighted) for a in range(size)])
        if not all([math.isfinite(value) for value in moved]):
            break
        reached = _poisson_deviance(response, inside_relations.predictor(columns, moved, rows))
        halved = 0
        while not reached <= deviance + 1e-9 * (1.0 + abs(deviance)) and halved < 60:
            moved = [(a + b) / 2.0 for a, b in zip(moved, beta)]
            reached = _poisson_deviance(response, inside_relations.predictor(columns, moved, rows))
            halved += 1
        change = max([abs(a - b) for a, b in zip(moved, beta)]) if size else 0.0
        beta = moved
        deviance = reached
        if change < _CHANGE:
            break
    eta = inside_relations.predictor(columns, beta, rows)
    means = [chain_walk.exponential(min(_ETA_CAP, max(-_ETA_CAP, e))) for e in eta]
    weights = [max(m, 1e-10) for m in means]
    lower, dropped = inside_relations.information(columns, weights)
    kept = len([flag for flag in dropped if not flag])
    pearson = math.fsum([(y - m) * (y - m) / w for y, m, w in zip(response, means, weights)])
    scale = max(1.0, pearson / max(1, rows - kept))
    return inside_relations.Fit(beta, weights, [y - m for y, m in zip(response, means)], lower, dropped, scale)


def _selected(blocks: "list[tuple[tuple[str, str, str], ...]]", values: "dict[tuple[str, str, str], list[float]]",
              response: "list[float]") -> "tuple[list[tuple[str, str, str]], inside_relations.Fit]":
    """Forward selection by the score test, the block passing its quantile by the most first; a square after its score."""
    rows = len(response)
    terms: "list[tuple[str, str, str]]" = []
    columns = [[1.0 for _row in range(rows)]]
    fit = poisson(columns, response)
    taken: "dict[int, bool]" = {}
    while len(taken) < SELECT_CAP:
        best = -1
        best_ratio = 1.0
        for at in range(len(blocks)):
            block = blocks[at]
            if at in taken or not block:
                continue
            if block[0][0] == SQUARE and (SCORE, block[0][1], "") not in terms:
                continue
            statistic = inside_relations.score_statistic(fit, columns, [values[term] for term in block])
            ratio = statistic / inside_relations.critical(len(block))
            if ratio > best_ratio:
                best, best_ratio = at, ratio
        if best < 0:
            break
        taken[best] = True
        for term in blocks[best]:
            terms += [term]
            columns += [values[term]]
        fit = poisson(columns, response)
    return terms, fit


# -- a bin's places ------------------------------------------------------------------------------------------------


def _places(counts: "list[int]", members: "list[int]") -> "list[float]":
    """The `POINTS` quantiles of the members' places among all persons ordered by their counts, ties spread evenly.

    A person whose count is held by a tie group starting at rank a, of n
    persons, stands anywhere in [a / N, (a + n) / N), N every person; the
    members' places are the mixture of those intervals, whose quantile at
    (k + 1/2) / POINTS is read exactly off it.
    """
    total = len(counts)
    below: "dict[int, int]" = {}
    held: "dict[int, int]" = {}
    for count in counts:
        held[count] = (held[count] if count in held else 0) + 1
    running = 0
    for count in sorted(held):
        below[count] = running
        running += held[count]
    mine: "dict[int, int]" = {}
    for member in members:
        count = counts[member]
        mine[count] = (mine[count] if count in mine else 0) + 1
    groups = sorted(mine)
    weight = len(members)
    out: "list[float]" = []
    at = 0
    passed = 0
    for k in range(POINTS):
        wanted = (k + 0.5) / POINTS * weight
        while at < len(groups) - 1 and passed + mine[groups[at]] < wanted:
            passed += mine[groups[at]]
            at += 1
        group = groups[at]
        inside = (wanted - passed) / mine[group]
        start = below[group] / total
        out += [start + max(0.0, min(1.0, inside)) * held[group] / total]
    return out


def _bin_of(cuts: "list[float]", eta: float) -> int:
    found = 0
    for cut in cuts:
        if cut <= eta:
            found += 1
    return found


# -- the fit ----------------------------------------------------------------------------------------------------------


def fit_sample(total: int) -> "list[int]":
    """The linked table's persons a fit reads, by their place: every one up to `FIT_CAP`, else a fixed hashed choice."""
    if total <= FIT_CAP:
        return [at for at in range(total)]
    bound = (FIT_CAP << 64) // total
    return [at for at in range(total) if inside_relations.mixed(at) < bound]


def fit_zone(key: str, child_keys: "list[str]", parents: Persons, sample: "list[int]",
             first_cells: "dict[str, list[str]]", order: "list[str]", linked_file: str) -> "dict[str, object]":
    """The links zone of a table whose person column ``key`` also names the persons of the linked table.

    ``child_keys`` is this table's key column; ``parents`` the persons of
    the linked table's key column (`persons_in`), ``sample`` the places of
    those the fit reads (`fit_sample`), and ``first_cells`` each other
    column of the linked table by name, one cell a sampled person, from
    its first row, in the sample's order; ``order`` the linked table's
    column names in order; ``linked_file`` its file's name. Each person's
    count is its rows in this table (0 where none), its place read among
    the sampled persons. Raises LinksError where the linked table names
    fewer than two persons; nothing else. Deterministic; no I/O.
    """
    total = len(parents.keys)
    if total < 2 or len(sample) < 2:
        raise LinksError("The linked table names no persons in its person column.")
    mine = persons_in(child_keys)
    index: "dict[str, int]" = {}
    for at in range(total):
        index[parents.keys[at]] = at
    whole_counts = [0 for _at in range(total)]
    found = 0
    for at in range(len(mine.keys)):
        if mine.keys[at] in index:
            whole_counts[index[mine.keys[at]]] = mine.rows[at]
            found += 1
    repeats = any([held > 1 for held in parents.rows])
    counts = [whole_counts[at] for at in sample]
    columns: "list[Column]" = []
    for name in order:
        if name == key or name not in first_cells:
            continue
        found_column = _column_of(name, first_cells[name])
        if found_column is not None:
            columns += [found_column]
    blocks = _blocks(columns, repeats)
    values: "dict[tuple[str, str, str], list[float]]" = {}
    rows_scores = _scores([float(parents.rows[at]) for at in sample])
    for block in blocks:
        for term in block:
            values[term] = rows_scores if term[0] == ROWS else _term_values(term, first_cells[term[1]])
    response = [float(count) for count in counts]
    terms, fit = _selected(blocks, values, response)
    beta = list(fit.beta)
    size = len(sample)
    eta = [beta[0] for _at in range(size)]
    for place in range(len(terms)):
        weight = beta[place + 1]
        eta = [e + weight * x for e, x in zip(eta, values[terms[place]])]
    ordered = sorted(eta)
    cuts = [ordered[min(size - 1, (k * size) // BINS)] for k in range(1, BINS)]
    members: "list[list[int]]" = [[] for _k in range(BINS)]
    for at in range(size):
        members[_bin_of(cuts, eta[at])] += [at]
    everyone = [at for at in range(size)]
    bins = [_places(counts, held if held else everyone) for held in members]
    kinds: "dict[str, object]" = {}
    for column in columns:
        kinds[column.name] = {"kind": column.kind, "levels": list(column.levels)}
    return {
        "version": ZONE_VERSION,
        "key": key,
        "linked": {"file": linked_file, "persons": total, "repeats": repeats},
        "persons": len(mine.keys),
        "found": found,
        "columns": kinds,
        "terms": [list(term) for term in terms],
        "beta": beta,
        "scale": fit.scale,
        "cuts": cuts,
        "bins": bins,
    }


# -- the zone read back ---------------------------------------------------------------------------------------------


def _get(mapping: object, name: str) -> object:
    if not isinstance(mapping, dict) or name not in mapping:
        raise LinksError(f"The inside record's links zone lacks its {name!r} entry; describe the table again.")
    return mapping[name]


def _whole(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise LinksError("The inside record's links zone holds a whole number where it does not.")
    return value


def _real(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise LinksError("The inside record's links zone holds a number where it does not.")
    return float(value)


def _reals(value: object) -> "list[float]":
    if not isinstance(value, list):
        raise LinksError("The inside record's links zone holds a list where it does not.")
    return [_real(each) for each in value]


def _word(value: object) -> str:
    if not isinstance(value, str):
        raise LinksError("The inside record's links zone holds a word where it does not.")
    return value


@dataclasses.dataclass(frozen=True)
class Zone:
    """The links zone, checked: the key, the linked table's file, the persons, the fit and the bins."""

    key: str
    linked_file: str
    repeats: bool
    persons: int
    found: int
    terms: "list[tuple[str, str, str]]"
    beta: "list[float]"
    cuts: "list[float]"
    bins: "list[list[float]]"


def zone_of(record: object) -> "Zone | None":
    """A record's links zone, checked, or None where the record holds none. Raises LinksError where it cannot be read."""
    zones = record["zones"] if isinstance(record, dict) and "zones" in record else None
    if not isinstance(zones, dict) or ZONE not in zones:
        return None
    zone = zones[ZONE]
    if _whole(_get(zone, "version")) != ZONE_VERSION:
        raise LinksError("The inside record's links zone was written by another version of synthtwin; describe the "
                         "table again.")
    linked = _get(zone, "linked")
    terms: "list[tuple[str, str, str]]" = []
    listed = _get(zone, "terms")
    if not isinstance(listed, list):
        raise LinksError("The inside record's links zone holds a list where it does not.")
    for each in listed:
        if not isinstance(each, list) or len(each) != 3:
            raise LinksError("The inside record's links zone holds a term it cannot read.")
        kind = _word(each[0])
        if kind not in (SCORE, SQUARE, MISSING, LEVEL, ROWS):
            raise LinksError("The inside record's links zone holds a term it cannot read.")
        terms += [(kind, _word(each[1]), _word(each[2]))]
    beta = _reals(_get(zone, "beta"))
    cuts = _reals(_get(zone, "cuts"))
    rows = _get(zone, "bins")
    if not isinstance(rows, list) or len(rows) != BINS or len(cuts) != BINS - 1 or len(beta) != len(terms) + 1:
        raise LinksError("The inside record's links zone holds a fit it cannot read.")
    bins = [_reals(each) for each in rows]
    if any([len(each) != POINTS for each in bins]):
        raise LinksError("The inside record's links zone holds a bin it cannot read.")
    repeats = _get(linked, "repeats")
    return Zone(_word(_get(zone, "key")), _word(_get(linked, "file")), repeats is True,
                _whole(_get(zone, "persons")), _whole(_get(zone, "found")), terms, beta, cuts, bins)


def needed_columns(zone: Zone) -> "list[str]":
    """The linked twin's columns the link reads: the key, then each column a term of the fit names, once."""
    out = [zone.key]
    for _kind, name, _level in zone.terms:
        if name and name not in out:
            out += [name]
    return out


# -- the link ---------------------------------------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class Linked:
    """What the link did: this twin's key cells, how many blocks it found in the linked twin and how many it left.

    ``refused`` names why nothing was linked ('' where the link was made);
    ``cells`` are then the cells it was handed.
    """

    cells: "list[str]"
    persons: int
    found: int
    own: int
    refused: str


def _uniform(seed: int, salt: int, at: int) -> float:
    return inside_relations.share_of(inside_relations.mixed((seed * 0x2545F4914F6CDD1D + inside_relations.mixed(
        (at << 4) + salt)) & _MASK64))


def _quantile(points: "list[float]", share: float) -> float:
    spot = share * POINTS - 0.5
    if spot <= 0.0:
        return points[0]
    if spot >= POINTS - 1:
        return points[POINTS - 1]
    low = int(spot)
    return points[low] + (spot - low) * (points[low + 1] - points[low])


def _taken(key: str, spellings: "dict[str, bool]", merged: "dict[str, bool]") -> bool:
    return key in spellings or parsing.merged_key(key) in merged


def _own_key(key: str, bound: int, seed: int, block: int, spellings: "dict[str, bool]",
             merged: "dict[str, bool]", other_bound: int = 0) -> str:
    """A key of its own for an unlinked block: its own where no linked or other key holds it, else one of its width.

    The block's own key is this twin's made-up key, never a real one of
    this table by its description's own construction, and is kept where no
    key taken so far holds it, as written or merged, and, where the linked
    table's description publishes ``other_bound`` (the merged length every
    real key of THAT table falls under), where it is at least that long.
    Else the new key keeps every character of it but its last run of
    figures, which is written again from the seed's hash at the same width
    and kept only where its merged key is at least ``bound`` long AND at
    least ``other_bound`` long (so no real key of either table can be it;
    batch 4y's fix round, Codex's review of the batch, item 4: a rewrite
    checked against this table's bound alone wrote a real key of the
    linked table) and no key taken so far holds it. '' where none is
    found in `OWN_KEY_TRIES` tries, and at once where ``other_bound`` is
    0 (the linked table's real keys then bound no width a new key could
    clear).
    """
    own_clear = other_bound <= 0 or len(parsing.merged_key(key)) >= other_bound
    if not _taken(key, spellings, merged) and own_clear:
        return key
    if other_bound <= 0:
        return ""
    end = len(key)
    while end > 0 and not ("0" <= key[end - 1] <= "9"):
        end -= 1
    start = end
    while start > 0 and "0" <= key[start - 1] <= "9":
        start -= 1
    width = end - start
    if width == 0:
        return ""
    for attempt in range(OWN_KEY_TRIES):
        drawn = int(_uniform(seed, 7, (block << 8) + attempt) * float(10 ** width))
        figures = f"{drawn:0{width}d}"[-width:]
        candidate = key[:start] + figures + key[end:]
        wide = len(parsing.merged_key(candidate))
        if wide >= bound and wide >= other_bound and not _taken(candidate, spellings, merged):
            return candidate
    return ""


def link(zone: Zone, cells: "list[str]", linked: "dict[str, list[str]]", seed: int, bound: int,
         table: str = "", other_bound: int = 0) -> Linked:
    """This twin's key cells written over the linked twin's persons (the module's docstring, THE LINK).

    ``cells`` is this twin's key column, ``linked`` the linked twin's
    columns by name (`needed_columns`), ``bound`` the merged length every
    real key of this table falls under (`spill_bound` of this description;
    0 where it publishes none), ``other_bound`` the same of the linked
    table's key column (`spill_bound` of ITS description; 0 where it
    publishes none): a block left unfound keeps its own key, or takes a
    new one, only where the key clears both, so no key it writes is a real
    key of either table (`_own_key`). Nothing is linked -- the cells come back as
    handed, with the reason -- where the bound is 0, where a key of the
    linked twin is shorter, merged, than the bound, or where either twin
    names no person. ``table`` names this table (its description's file
    name), and its digest is mixed into the seed: two tables linked to one
    twin at one seed draw their persons' places apart, so they meet through
    the linked twin's columns alone, as two tables independent given those
    columns do. Deterministic in its arguments; raises LinksError where the
    linked twin lacks a column the fit reads; no I/O.
    """
    stream = inside_relations.mixed(
        (seed + int(inside_relations.digest_of(bytes(table, "utf-8", "surrogatepass")), 16)) & _MASK64)
    for name in needed_columns(zone):
        if name not in linked:
            if name == zone.key:
                return Linked(list(cells), 0, 0, 0, REFUSED_NO_KEY)
            raise LinksError("The linked table's twin lacks a column the inside record's links zone reads.")
    if bound <= 0:
        return Linked(list(cells), 0, 0, 0, REFUSED_NO_BOUND)
    parents = persons_in(linked[zone.key])
    mine = persons_in(cells)
    if not parents.keys or not mine.keys:
        return Linked(list(cells), len(mine.keys), 0, 0, REFUSED_NO_PERSONS)
    for key in parents.keys:
        if len(parsing.merged_key(key)) < bound:
            return Linked(list(cells), len(mine.keys), 0, 0, REFUSED_NOT_WIDER)
    total = len(parents.keys)
    # Each linked person's predictor from its first row's cells, its bin, and its drawn place.
    eta = [zone.beta[0] for _at in range(total)]
    rows_scores = _rows_term(parents) if any([term[0] == ROWS for term in zone.terms]) else []
    first_cells: "dict[str, list[str]]" = {}
    for place in range(len(zone.terms)):
        term = zone.terms[place]
        if term[0] == ROWS:
            values = rows_scores
        else:
            if term[1] not in first_cells:
                column = linked[term[1]]
                first_cells[term[1]] = [column[row] for row in parents.first]
            values = _term_values(term, first_cells[term[1]])
        weight = zone.beta[place + 1]
        eta = [e + weight * x for e, x in zip(eta, values)]
    places = [_quantile(zone.bins[_bin_of(zone.cuts, eta[at])], _uniform(stream, 1, at)) for at in range(total)]
    # How many of this twin's persons are found there: the real share, at most every linked person.
    blocks = len(mine.keys)
    wanted = min(total, (2 * blocks * zone.found + zone.persons) // (2 * max(1, zone.persons)))
    by_hash = sorted([(inside_relations.mixed((stream << 20) + at), at) for at in range(blocks)])
    left: "dict[int, bool]" = {}
    for _word_at, at in by_hash[: blocks - wanted]:
        left[at] = True
    found_blocks = sorted([(-mine.rows[at], _uniform(stream, 2, at), at) for at in range(blocks) if at not in left])
    takers = sorted([(-places[at], _uniform(stream, 3, at), at) for at in range(total)])
    new_key: "dict[str, str]" = {}
    spellings: "dict[str, bool]" = {}
    merged: "dict[str, bool]" = {}
    for key in parents.keys:
        spellings[key] = True
        merged[parsing.merged_key(key)] = True
    for at in range(len(found_blocks)):
        new_key[mine.keys[found_blocks[at][2]]] = parents.keys[takers[at][2]]
    spare = len(found_blocks)
    own = 0
    for at in range(blocks):
        if at not in left:
            continue
        key = _own_key(mine.keys[at], bound, stream, at, spellings, merged, other_bound)
        if not key and spare < total:
            # No key of its own was found: the block is linked to a person no block has taken, where one is left.
            new_key[mine.keys[at]] = parents.keys[takers[spare][2]]
            spare += 1
            continue
        if not key:
            key = mine.keys[at]
        own += 1
        new_key[mine.keys[at]] = key
        spellings[key] = True
        merged[parsing.merged_key(key)] = True
    out: "list[str]" = []
    for cell in cells:
        bare = _bare(cell)
        out += [new_key[bare] if bare in new_key else cell]
    return Linked(out, blocks, blocks - own, own, "")
