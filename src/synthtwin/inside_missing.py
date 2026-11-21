"""THE INSIDE RECORD'S MISSING-VALUES ZONE (lane IN-7, plan P4-D501): which columns are empty together, and who is missing.

WHAT IT CARRIES. The relations zone (lane IN-2) fits each column it
models on the modelled columns before it, an empty cell among a
number's states and a label's levels, so the empty cells of the
MODELLED columns already follow the columns they depend on. Every other
column -- a date, a clock, free text, a record number other than the
person's, a constant written on some rows -- is KEPT from the
description's twin, whose empty cells fall on rows chosen with no
regard to the other columns: an end date empty on rows whose stay is
over, a remark written where nothing happened. This zone
carries those. For each kept column that holds at least `MIN_ROWS`
empty cells and as many filled ones, in the table's order, one logistic
response of its emptiness is fitted inside, on the real table, by the
relations zone's own machinery (`inside_relations.select` through
`fit_label`: main blocks, curves, interactions, each past the
chi-square gate at 0.001, at most `inside_relations.PARENT_CAP`
parents) on every modelled column (a number's score and its states, a
label's levels, an empty cell among them) and on the emptiness of the
kept columns before it. So WHICH COLUMNS ARE EMPTY TOGETHER and HOW A
COLUMN'S EMPTINESS DEPENDS ON THE OTHERS are carried as fitted
responses. Where the person column repeats and a column is empty or
filled for all of a person's rows, its emptiness is fitted once a
person, on the person-level columns.

WHAT THE TWIN DOES WITH IT (`draw`). Each carried column's twin rows
take a latent emptiness: the fitted log odds plus a logistic draw (a
person's at the person's first row where the emptiness is one a
person), the draws SplitMix64 streams of the seed and the column's
name, as lane IN-5's are. A date column the dates zone writes takes
the rows whose latent is at most nought as the rows that hold a date
(`present_rows`, handed to `inside_dates.write_dates`), so its empty
cells come at the fitted share where the fit puts them. Every other
carried column keeps the description's twin's own cells, exactly as
many filled and empty cells as that twin holds, the filled ones moved
onto the rows whose latent emptiness is lowest (`dealt`), each group
in its order. A column whose cells a rule binds to another column
(values typed by a key, a computed column) is not moved, nor one whose
cells are held once a person (a person's rows would then differ).

WHAT IT HOLDS AND NEVER HOLDS. Each carried column's emptiness model:
its terms, its coefficients, its count of empty cells, its level; no
row, no cell, no person, no value: its size follows the columns and
their terms, never the rows.

ZONES. The fit runs at describe time, the draw at generate time: the
generator imports this module, so it is zone G, and like the relations
zone it uses Python integers and binary64 `+ - * /` in the order
written, sums by `math.fsum`, the exponential and logarithm written out
in `chain_walk`, and no random source.
"""

import dataclasses
import math
import typing

from synthtwin import chain_walk, inside_relations, parsing

ZONE = "missing"
ZONE_VERSION = 1
# A carried column holds at least this many empty cells and as many filled ones.
MIN_ROWS = inside_relations.MIN_ROWS
# A column block's keys that bind its cells to another column: such a column's cells are never moved.
BOUND_KEYS = ("keyed", "keyed_by", "key_blocks", "computed_from")
# The roles of the columns whose cells a date writer makes (the dates zone's): they take the present rows.
DATE_ROLES = ("datetime", "time_of_day")
# A latent emptiness is the log odds plus a logistic draw; the log odds is capped as the relations zone caps it.
ETA_CAP = 35.0
FILLED = 0
EMPTY = 1
# The relations zone's levels of a column (`inside_relations.level_of`), as plain words the offline audit reads.
ROW = "row"
PATIENT = "patient"
_MASK = 0xFFFFFFFFFFFFFFFF
_GOLDEN = 0x9E3779B97F4A7C15
_TWO_53 = 9007199254740992.0


class MissingError(ValueError):
    """A missing-values zone that cannot be read or drawn from, in plain words naming no value."""


# -- words, read under the offline audit's exact type checks ---------------------------------------


def _text(value: object) -> str:
    if not isinstance(value, str):
        raise MissingError("The inside record's missing-values zone holds a word where it does not.")
    return value


def _int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise MissingError("The inside record's missing-values zone holds a whole number where it does not.")
    return value


def _float(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise MissingError("The inside record's missing-values zone holds a number where it does not.")
    return float(value)


def _list(value: object) -> "list[object]":
    if not isinstance(value, list):
        raise MissingError("The inside record's missing-values zone holds a list where it does not.")
    return value


def _dict(value: object) -> "dict[str, object]":
    if not isinstance(value, dict):
        raise MissingError("The inside record's missing-values zone holds an entry where it does not.")
    return typing.cast("dict[str, object]", value)


def _get(mapping: object, key: str) -> object:
    if not isinstance(mapping, dict) or key not in mapping:
        raise MissingError(f"The inside record's missing-values zone lacks its {key!r} entry; describe the table again.")
    return mapping[key]


def is_empty(cell: object) -> bool:
    """Whether a cell holds no value: a blank, or a spelling the product reads as no value (`parsing.is_missing_text`)."""
    if not isinstance(cell, str):
        raise TypeError("synthtwin reads a table's cells as text only.")
    return not cell.strip() or parsing.is_missing_text(cell)


def frame_name(name: str) -> str:
    """The name a carried column's emptiness goes by among the fits' frames: no column of a table can take it."""
    return "\x00" + _text(name)


# -- which kept columns the zone carries (from the description's own blocks) ------------------------


@dataclasses.dataclass
class Kept:
    """One kept column the zone may carry: its emptiness on the fit's rows, its counts, its levels, and whether its cells may move."""

    name: str
    place: int
    role: str
    codes: "list[int]"
    empty: int
    rows: int
    level: str
    once: bool
    moved: bool


def kept_column(spec: inside_relations.ColumnSpec, block: object, cells: "list[str]", rows: "list[int]",
                persons: "inside_relations.Persons | None") -> "Kept | None":
    """A kept column read for the zone, or None where it is modelled, names the person, or holds too few empty or filled cells.

    `rows` are the fit's rows (`inside_relations.sample_rows`); `persons`
    the table's persons where a person column repeats. The emptiness is
    counted over all rows; its codes are read on the fit's rows.
    """
    if spec.kind or spec.why_kept == inside_relations.NAMES_THE_PERSON:
        return None
    role = block["role"] if isinstance(block, dict) and "role" in block and isinstance(block["role"], str) else ""
    bound = False
    if isinstance(block, dict):
        for key in BOUND_KEYS:
            if key in block and block[key]:
                bound = True
    flags = [EMPTY if is_empty(cell) else FILLED for cell in cells]
    empty = len([flag for flag in flags if flag == EMPTY])
    if empty < MIN_ROWS or len(cells) - empty < MIN_ROWS:
        return None
    marks = ["" if flag == EMPTY else "1" for flag in flags]
    probe = inside_relations.ColumnSpec(spec.name, spec.place, inside_relations.LABEL, 0, (), "")
    level = inside_relations.level_of(probe, marks, persons)
    del marks
    once = inside_relations.level_of(probe, cells, persons) == PATIENT
    codes = [flags[row] for row in rows]
    return Kept(spec.name, spec.place, role, codes, empty, len(cells), level, once, not bound)


def once_of(relations: "dict[str, object]") -> "set[str]":
    """The modelled columns a relations zone holds once a person (their frames are a person's)."""
    found: "set[str]" = set()
    for entry in _list(_get(relations, "columns")):
        mapping = _dict(entry)
        if "level" in mapping and mapping["level"] == PATIENT:
            found = found | set([_text(_get(mapping, "name"))])
    return found


def _first_rows(owners: "list[int] | None", sample: int) -> "list[bool] | None":
    """Each fit row's place as its person's first fit row (None where every row is a person of its own)."""
    if owners is None:
        return None
    seen: "dict[int, bool]" = {}
    first: "list[bool]" = []
    for row in range(sample):
        first += [owners[row] not in seen]
        seen[owners[row]] = True
    return first


def fit_zone(kept: "list[Kept]", frames: "dict[str, inside_relations.Frame]", once: "set[str]", sample: int,
             rows: int, owners: "list[int] | None" = None) -> "dict[str, object]":
    """The missing-values zone: each kept column's emptiness, in the table's order, fitted on the modelled columns and the kept ones before it.

    `frames` are the relations zone's frames on the fit's rows
    (`inside_relations.fit_zone`'s `frames_out`), one a modelled column;
    `once` names those held once a person; `owners` gives each fit row's
    person where a person column repeats. Each fitted emptiness joins the
    frames under `frame_name`, so the kept columns after it read it.
    `frames` gains those entries.
    """
    first = _first_rows(owners, sample)
    person_level = set(once)
    columns: "list[object]" = []
    for column in kept:
        held_once = column.level == PATIENT and first is not None
        candidates: "list[inside_relations.Block]" = []
        for parent in frames:
            if held_once and parent not in person_level:
                continue
            block = inside_relations.main_block(parent, frames[parent])
            if block is not None:
                candidates += [block]
        fitted = [row for row in range(sample) if first is None or not held_once or first[row]]
        target = inside_relations.Target(inside_relations.LABEL, [], fitted, column.codes, 2)
        model = inside_relations.fit_label(target, candidates, frames, sample)
        columns += [{
            "name": column.name, "place": column.place, "role": column.role, "rows": column.rows,
            "empty": column.empty, "level": column.level if held_once else ROW,
            "once": column.once, "moved": column.moved, "presence": model,
        }]
        name = frame_name(column.name)
        frames[name] = inside_relations.Frame(inside_relations.LABEL, [], [], column.codes)
        if held_once:
            person_level = person_level | set([name])
    return {"version": ZONE_VERSION, "rows": rows, "sample_rows": sample, "columns": columns}


# -- the zone read back --------------------------------------------------------------------------------


def zone_of(record: object) -> "dict[str, object] | None":
    """The missing-values zone of a loaded inside record, checked for its version; None where the record has none."""
    zones = _get(record, "zones")
    if not isinstance(zones, dict) or ZONE not in zones:
        return None
    zone = _dict(zones[ZONE])
    if _int(_get(zone, "version")) != ZONE_VERSION:
        raise MissingError("The inside record's missing-values zone is of another version; describe the table again.")
    return zone


def _names_in(term: object) -> "list[str]":
    parts = _list(term)
    head = _text(parts[0])
    if head == "one":
        return []
    if head == "prod":
        return _names_in(parts[1]) + _names_in(parts[2])
    return [_text(parts[1])]


def parents(zone: "dict[str, object] | None") -> "set[str]":
    """The modelled columns whose drawn frames the zone's fits read (never a carried column's own emptiness)."""
    found: "set[str]" = set()
    if zone is None:
        return found
    for entry in _list(_get(zone, "columns")):
        model = _dict(_get(entry, "presence"))
        for term in _list(_get(model, "terms")):
            for name in _names_in(term):
                if name[:1] != "\x00":
                    found = found | set([name])
    return found


def carried(zone: "dict[str, object] | None") -> "list[str]":
    """The columns the zone carries, in its order."""
    if zone is None:
        return []
    return [_text(_get(entry, "name")) for entry in _list(_get(zone, "columns"))]


def entry_of(zone: "dict[str, object]", name: str) -> "dict[str, object]":
    """One carried column's entry."""
    for entry in _list(_get(zone, "columns")):
        if _text(_get(entry, "name")) == name:
            return _dict(entry)
    raise MissingError("The inside record's missing-values zone does not carry that column.")


# -- the draw ------------------------------------------------------------------------------------------


def _mixed(value: int) -> int:
    z = (value + _GOLDEN) & _MASK
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & _MASK
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & _MASK
    return z ^ (z >> 31)


def _stream(seed: int, name: str) -> "list[int]":
    """A column's stream: the seed and the column's name mixed character by character, then the purpose's mark."""
    state = _mixed(seed & _MASK)
    for character in _text(name):
        state = _mixed(state ^ ord(character))
    return [_mixed(state ^ 0x45)]


def _uniform(state: "list[int]") -> float:
    """The stream's next number strictly between nought and one."""
    state[0] = (state[0] + _GOLDEN) & _MASK
    z = state[0]
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & _MASK
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & _MASK
    z = z ^ (z >> 31)
    return ((z >> 11) + 0.5) / _TWO_53


def _log_odds_of(share: float) -> float:
    return chain_walk.natural_log(share / (1.0 - share))


def _predictor(model: "dict[str, object]", frames: "dict[str, inside_relations.Frame]", rows: int) -> "list[float]":
    """The fitted log odds of an empty cell on every twin row, the terms added in their order and capped at `ETA_CAP`."""
    terms = _list(_get(model, "terms"))
    coefficients = _list(_get(model, "coefficients"))
    if len(coefficients) != 2:
        raise MissingError("The inside record's missing-values zone holds an emptiness fit of another shape.")
    beta = [_float(value) for value in _list(coefficients[1])]
    if len(beta) != len(terms):
        raise MissingError("The inside record's missing-values zone holds an emptiness fit of another shape.")
    eta = [0.0 for _row in range(rows)]
    for place in range(len(terms)):
        weight = beta[place]
        if weight == 0.0:
            continue
        values = inside_relations.term_values(terms[place], frames, rows)
        eta = [e + weight * x for e, x in zip(eta, values)]
    return [min(ETA_CAP, max(-ETA_CAP, e)) for e in eta]


def draw(zone: "dict[str, object]", frames: "dict[str, inside_relations.Frame]", rows: int, seed: int,
         persons: "inside_relations.Persons | None" = None) -> "dict[str, list[float]]":
    """Each carried column's latent emptiness on every twin row: empty where it is above nought.

    `frames` holds the drawn frames of every modelled column the zone's
    fits read (`parents`); it gains each carried column's emptiness under
    `frame_name` as it is drawn, so the columns after it read it.
    `persons` names the twin's persons where a person column repeats: a
    column whose emptiness is one a person draws it at each person's
    first row and gives it to every row of the person. Same zone, frames
    and seed, same latents. Raises MissingError where the zone does not
    fit the twin (another number of rows, a parent not drawn).
    """
    if _int(_get(zone, "rows")) != rows:
        raise MissingError("The inside record was written for a table of another size than this twin.")
    out: "dict[str, list[float]]" = {}
    for entry in _list(_get(zone, "columns")):
        name = _text(_get(entry, "name"))
        model = _dict(_get(entry, "presence"))
        try:
            eta = _predictor(model, frames, rows)
        except inside_relations.RelationsError:
            raise MissingError("The inside record's missing-values zone reads a column the twin did not draw.") from None
        state = _stream(seed, name)
        held_once = _text(_get(entry, "level")) == PATIENT and persons is not None and persons.repeats
        latent: "list[float]" = []
        if held_once and persons is not None:
            of_person: "dict[int, float]" = {}
            for row in range(rows):
                owner = persons.person[row]
                if owner not in of_person:
                    of_person[owner] = eta[row] + _log_odds_of(_uniform(state))
                latent += [of_person[owner]]
        else:
            for row in range(rows):
                latent += [eta[row] + _log_odds_of(_uniform(state))]
        out[name] = latent
        frames[frame_name(name)] = inside_relations.Frame(
            inside_relations.LABEL, [], [], [EMPTY if value > 0.0 else FILLED for value in latent])
    return out


def present_rows(latent: "list[float]") -> "list[bool]":
    """The rows that hold a value: those whose latent emptiness is at most nought."""
    return [value <= 0.0 for value in latent]


def dealt(cells: "list[str]", latent: "list[float]", kept: "list[bool] | None" = None) -> "list[str]":
    """A kept column's own cells moved by the latent emptiness: as many filled cells as it holds, on the rows least likely empty.

    The column keeps every cell it holds: its filled cells go, in their
    order, to the rows of lowest latent emptiness (ties by place), its
    empty cells, in their order and spelling, to the rest. The rows `kept`
    marks (the description's twin's all-empty records, lane IN-2b) keep
    their own cells and take no part in the dealing (batch 4x's outside
    review, item 7), so a record the description keeps empty stays empty.
    Guarantees: a fixed function of the lists; the same multiset of cells;
    every kept row's cell as it stands.
    """
    if len(cells) != len(latent) or (kept is not None and len(kept) != len(cells)):
        raise MissingError("The inside record's missing-values zone was drawn for a twin of another size.")
    free = [row for row in range(len(cells)) if kept is None or not kept[row]]
    filled = [cells[row] for row in free if not is_empty(cells[row])]
    empty = [cells[row] for row in free if is_empty(cells[row])]
    ranked = sorted((latent[row], row) for row in free)
    chosen = [False for _row in range(len(cells))]
    for place in range(len(filled)):
        chosen[ranked[place][1]] = True
    out: "list[str]" = [cell for cell in cells]
    taken_filled = 0
    taken_empty = 0
    for row in free:
        if chosen[row]:
            out[row] = filled[taken_filled]
            taken_filled += 1
        else:
            out[row] = empty[taken_empty]
            taken_empty += 1
    return out


def moves(entry: "dict[str, object]") -> bool:
    """Whether a carried column's own cells are moved (`dealt`): no rule binds them and they vary within a person."""
    return _get(entry, "moved") is True and _get(entry, "once") is not True and _text(_get(entry, "role")) not in DATE_ROLES


def frame_names(zone: "dict[str, object] | None") -> "list[str]":
    """The frame names the carried columns' emptiness goes by, in the zone's order."""
    return [frame_name(name) for name in carried(zone)]


def shares(latent: "list[float]") -> float:
    """The share of rows a latent emptiness makes empty (a check for the gate files and the report)."""
    if not latent:
        return 0.0
    return math.fsum([1.0 if value > 0.0 else 0.0 for value in latent]) / len(latent)
