"""THE INSIDE RECORD'S RELATIONS ZONE (lane IN-2, plan P4-D496): fitted responses, and the twin drawn from them.

WHAT IT CARRIES. The joint structure of a real table at fine resolution,
as FITTED RESPONSES: each modelled column, in the table's own order, is a
response fitted on the real table inside the protected computer to the
modelled columns before it. A number is fitted on its normal score (its
rank among the column's numbers, read through the normal quantile) by
least squares, with a residual shape of `RESIDUAL_POINTS` quantiles; a
label, and a number's presence (a number, an empty cell, another word),
by one logistic fit a level against the commonest level (baseline-category
log odds fitted level by level). The terms a fit may use are each earlier
column's main block (a number's score and its presence states; a label's
levels), a CURVE block (a restricted cubic spline of a number's score,
knots at `KNOTS`) and INTERACTION blocks (a label's levels times a
number's score or another label's levels; two numbers' scores), so an
interaction such as one yes/no column changing another's effect, a curved
effect, and a step at a class's cut point are carried as they stand, not
folded into inflated main effects as a Gaussian copula folds them. A block
enters only where its score statistic passes the chi-square quantile of
`GATE_LEVEL` (at most `PARENT_CAP` parents a response, then at most
`EXTRA_CAP` curve or interaction blocks), so the twin adds no relation the
table does not show.

WHAT IT HOLDS AND WHAT IT NEVER HOLDS. Each modelled number's quantile
function on `GRID` points over ALL its rows (its exact shape), its written
decimals, its censoring atoms (`<x`, `>x`) and its Safe Harbor top code;
each modelled label's published spellings and their counts over all rows;
and each fit's terms and coefficients, fitted on at most `SAMPLE_CAP` rows.
No row, no person's values, no record number: its size depends on the
columns, the levels and the grids, never on the rows.

WHICH COLUMNS. A number (`count`, `continuous`, `affixed_number`,
`numbers_with_labels`) or a label (`binary`, `categorical`,
`long_tail_labels`) that the description reads as data, top-coded at 90 or
not at all, typed by no key and computed by no rule. Every other column --
identifiers, dates, clocks, free text, joined numbers, keyed values, the
rarer Safe Harbor codes -- is KEPT: its cells are the description's own
twin's, made by every rule that twin keeps (made-up identifiers never
equal to a real one, held columns, dates and the rest). So are a label's
cells outside its published spellings and a number column's words: they
are drawn from the same column of the description's twin, never from the
record.

ZONES. The fit runs at describe time, the draw at generate time; both are
Python integers and binary64 `+ - * /` and `math.sqrt` in the order
written, sums by `math.fsum`, the exponential, logarithm and normal
quantile written out in `chain_walk`, and the one seeded stream: the
generator imports this module, so it is zone G, and the same record and
seed give the same twin on every computer.
"""

import dataclasses
import math
import typing

import numpy.random

from synthtwin import chain_walk, contract, twinstore

ZONE = "relations"
ZONE_VERSION = 1
# The fit's rows: every row up to this many, else a fixed hashed choice of about this many.
SAMPLE_CAP = 200_000
# A number's quantile function: points over all its rows.
GRID = 1001
# A response's residual shape: standardised residual quantiles at shares (k + 1/2) / RESIDUAL_POINTS.
RESIDUAL_POINTS = 41
# Restricted cubic spline knots on a normal score: its 5th, 30th, 70th and 95th percentiles.
KNOTS = (-1.644854, -0.524401, 0.524401, 1.644854)
# The level a block's score statistic must pass: chi-square quantiles at 0.999, degrees of freedom 1 to 40.
GATE_LEVEL = 0.001
_CHI_SQUARE_999 = (
    10.8276, 13.8155, 16.2662, 18.4668, 20.515, 22.4577, 24.3219, 26.1245, 27.8772, 29.5883,
    31.2641, 32.9095, 34.5282, 36.1233, 37.6973, 39.2524, 40.7902, 42.3124, 43.8202, 45.3147,
    46.797, 48.2679, 49.7282, 51.1786, 52.6197, 54.052, 55.476, 56.8923, 58.3012, 59.7031,
    61.0983, 62.4872, 63.8701, 65.2472, 66.6188, 67.9852, 69.3465, 70.7029, 72.0547, 73.402,
)
# The normal quantile at 0.999, for the Wilson-Hilferty form past 40 degrees of freedom.
_Z_999 = 3.090232
PARENT_CAP = 12
EXTRA_CAP = 4
# The candidates `select`'s conditional pass reads exactly, the strongest by their residuals' plain score (lane STATS-B).
CONDITIONAL_EXACT = 6
# A label's modelled spellings, its commonest published ones; and the rows a level, state or term needs.
LEVEL_CAP = 30
MIN_ROWS = 20
# A carried label's rest spellings kept with their counts (lane IN-7), the marginals zone's own cap.
OTHERS_CAP = 1000
# A label parent's indicator terms at most; an interaction's degrees of freedom at most.
INDICATOR_CAP = 24
INTERACTION_DF_CAP = 8
# A label response fits its levels' interactions only up to this many levels.
EXTRA_LEVELS_CAP = 6
_PIVOT = 1e-9
_RIDGE = 1e-8
_ITERATIONS = 30
_CHANGE = 1e-7
_ETA_CAP = 35.0
_WORD_CEILING = 18446744073709551615
_TWO_53 = 9007199254740992.0
_MASK64 = (1 << 64) - 1
_INFINITY = float("inf")

NUMBER = "number"
LABEL = "label"
NUMBER_ROLES = (contract.ROLE_COUNT, contract.ROLE_CONTINUOUS, contract.ROLE_AFFIXED, contract.ROLE_COMPOUND)
LABEL_ROLES = (contract.ROLE_BINARY, contract.ROLE_CATEGORICAL, contract.ROLE_LONG_TAIL)
# A number's presence states: a number, an empty cell, another word, and its lowest or highest value where
# that one value holds at least `SPIKE_SHARE` of the numbers (a zero most rows hold, a floor or a ceiling):
# a SPIKE is a state of its own, so a two-part relation (whether, then how much) is fitted as one.
PRESENT, EMPTY, WORD, LOW, HIGH = 0, 1, 2, 3, 4
STATES = 5
NUMBER_STATES = (PRESENT, LOW, HIGH)
SPIKE_SHARE = 0.05
# A column block's keys that keep a column on the description's twin whatever its role. An age's ends and
# bands pooled in people (`top_coded_ends`, `top_coded_bands`) are the floor's, not Safe Harbor's: the 90 of
# `top_coded` is kept on every drawn age.
KEPT_KEYS = (
    "keyed", "keyed_by", "key_blocks", "computed_from", "top_coded_year", "top_coded_words",
    "present_count_withheld", "withheld_words_from",
)


class RelationsError(ValueError):
    """A relations zone that cannot be read or drawn from, in plain words naming no value."""


# -- words, read under the offline audit's exact type checks ---------------------------------------


def _bare(cell: object) -> str:
    if not isinstance(cell, str):
        raise TypeError("synthtwin reads a table's cells as text only.")
    return cell.strip()


def _starts(text: object, prefix: str) -> bool:
    if not isinstance(text, str):
        raise TypeError("synthtwin reads a table's cells as text only.")
    return text[: len(prefix)] == prefix


def _number(text: object) -> "float | None":
    """A cell's number where the whole cell is one (finite), else None."""
    bare = _bare(text)
    if not bare:
        return None
    try:
        value = float(bare)
    except ValueError:
        return None
    return value if math.isfinite(value) else None


def _decimals(text: object) -> int:
    """The places after the point a number cell needs written in fixed point: its own, or its exponent's scale.

    `1.234e-6` needs nine (its mantissa's three, moved six places by its
    exponent), `1.5e2` none: an exponent's spelling read as nought places
    wrote a column of millionths as zeroes.
    """
    if not isinstance(text, str):
        raise TypeError("synthtwin reads a table's cells as text only.")
    bare = text.strip()
    if "e" in bare or "E" in bare:
        form = _exponent_form(bare)
        if form is not None:
            return max(0, form[0] - form[4])
    pieces = bare.split(".")
    return len(pieces[1]) if len(pieces) == 2 else 0


def _exponent_form(text: object) -> "tuple[int, str, bool, int, int] | None":
    """How a number cell writes an exponent: its mantissa's places, its mark, a plus shown, the power's figures and the power.

    `1.234e-6` is (3, "e", False, 1, -6) and `-2.50E+03` (2, "E", True, 2,
    3); None for a cell written in fixed point (or that is no number).
    """
    if not isinstance(text, str):
        raise TypeError("synthtwin reads a table's cells as text only.")
    bare = text.strip()
    # A number holds one mark at most: found from its lower or its upper case, with no loop over the cell.
    at = bare.find("e")
    if at < 0:
        at = bare.find("E")
    if at < 1 or _number(bare) is None:
        return None
    mantissa = bare[:at]
    power = bare[at + 1:]
    plus = _starts(power, "+")
    figures = power[1:] if (plus or _starts(power, "-")) else power
    if not figures or figures.strip("0123456789"):
        return None
    pieces = mantissa.split(".")
    places = len(pieces[1]) if len(pieces) == 2 else 0
    return places, bare[at], plus, len(figures), int(power)


def _atom(text: object) -> "tuple[float, str] | None":
    """A censoring atom `<x`, `<=x`, `>x`, `>=x`: its place just below or above `x`, and its text; else None."""
    bare = _bare(text)
    for mark, below in (("<=", True), (">=", False), ("<", True), (">", False)):
        if _starts(bare, mark):
            value = _number(bare[len(mark):])
            if value is None:
                return None
            step = abs(value) * 1e-9 + 1e-12
            return (value - step if below else value + step), bare
    return None


def _fnv(data: bytes) -> str:
    """The 64-bit FNV-1a digest of `data`, as 16 hex figures (whole numbers only)."""
    value = 14695981039346656037
    for byte in data:
        value = ((value ^ byte) * 1099511628211) & _MASK64
    return f"{value:016x}"


def digest_of(data: bytes) -> str:
    """The digest that binds a record to the description it was written beside (FNV-1a, 64 bits)."""
    if not isinstance(data, bytes):
        raise TypeError("synthtwin digests bytes only.")
    return _fnv(data)


def _mix(value: int) -> int:
    """SplitMix64's finaliser: a fixed whole-number hash of a row's place."""
    z = (value + 0x9E3779B97F4A7C15) & _MASK64
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & _MASK64
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & _MASK64
    return z ^ (z >> 31)


@dataclasses.dataclass(frozen=True)
class Persons:
    """Who each row is about, where a person column names several rows a person: each row's person and its place among them."""

    person: "list[int]"
    first: "list[bool]"
    sequence: "list[int]"
    repeats: bool
    rows_of: "list[int]" = dataclasses.field(default_factory=list)


def persons_of(cells: "list[str]") -> Persons:
    """Each row's person (its key as written, trimmed; a blank key a person of its own), first rows and places in row order."""
    seen: "dict[str, int]" = {}
    person: "list[int]" = []
    first: "list[bool]" = []
    sequence: "list[int]" = []
    held: "list[int]" = []
    for row in range(len(cells)):
        key = _bare(cells[row])
        if not key:
            key = "\x00" + f"{row}"
        if key in seen:
            index = seen[key]
            held[index] += 1
            first += [False]
        else:
            index = len(held)
            seen[key] = index
            held += [1]
            first += [True]
        person += [index]
        sequence += [held[index]]
    return Persons(person, first, sequence, len(held) < len(cells), held)


# A column is held once a person where at least this share of the persons with two rows or more hold one value
# (a patient's arm, an age at entry); a number counts a person's rows (1, 2, 3 in row order) where this share of
# its rows do.
PATIENT_SHARE = 0.95
ROW, PATIENT, SEQUENCE = "row", "patient", "sequence"
# The level of a number counting each person's rows, as a name other modules read (lane STATS-B).
SEQUENCE_LEVEL = SEQUENCE


def level_of(spec: "ColumnSpec", cells: "list[str]", persons: "Persons | None") -> str:
    """Whether a column varies by row, is held once a person, or counts each person's rows in row order."""
    if persons is None or not persons.repeats:
        return ROW
    if spec.kind == NUMBER:
        hits = 0
        for row in range(len(cells)):
            value = _number(cells[row])
            if value is not None and value == float(persons.sequence[row]):
                hits += 1
        if hits >= PATIENT_SHARE * len(cells):
            return SEQUENCE
    value_of: "dict[int, str]" = {}
    mixed: "dict[int, bool]" = {}
    for row in range(len(cells)):
        owner = persons.person[row]
        if owner in value_of:
            if value_of[owner] != cells[row]:
                mixed[owner] = True
        else:
            value_of[owner] = cells[row]
    several = len([held for held in persons.rows_of if held >= 2])
    constant = several - len(mixed)
    return PATIENT if several >= MIN_ROWS and constant >= PATIENT_SHARE * several else ROW


def sample_rows(rows: int, cap: int = SAMPLE_CAP, persons: "Persons | None" = None) -> "list[int]":
    """The rows a fit reads: every row up to `cap`, else the rows (by person, where persons repeat) whose fixed hash falls under `cap / rows`."""
    if rows <= cap:
        return [row for row in range(rows)]
    bound = (cap << 64) // rows
    if persons is not None and persons.repeats:
        return [row for row in range(rows) if _mix(persons.person[row]) < bound]
    return [row for row in range(rows) if _mix(row) < bound]


# -- the record read back, its values never quoted ---------------------------------------------------


def _get(mapping: object, key: str) -> object:
    if not isinstance(mapping, dict) or key not in mapping:
        raise RelationsError(f"The inside record's relations zone lacks its {key!r} entry; describe the table again.")
    return mapping[key]


def _list(value: object) -> "list[object]":
    if not isinstance(value, list):
        raise RelationsError("The inside record's relations zone holds a list where it does not; describe the table again.")
    return value


def _int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise RelationsError("The inside record's relations zone holds a whole number where it does not.")
    return value


def _float(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise RelationsError("The inside record's relations zone holds a number where it does not.")
    return float(value)


def _text(value: object) -> str:
    if not isinstance(value, str):
        raise RelationsError("The inside record's relations zone holds a word where it does not.")
    return value


def _floats(value: object) -> "list[float]":
    return [_float(each) for each in _list(value)]


def _dict(value: object) -> "dict[str, object]":
    if not isinstance(value, dict):
        raise RelationsError("The inside record's relations zone holds an entry where it does not; describe the table again.")
    return typing.cast("dict[str, object]", value)


# -- which columns are modelled (from the description's own blocks) ---------------------------------


# Why a column is kept: it names the person, or it is an identifier (both record numbers, of which the
# marginals zone keeps no value).
NAMES_THE_PERSON = "names the person"
AN_IDENTIFIER = "an identifier"
RECORD_NUMBERS = (NAMES_THE_PERSON, AN_IDENTIFIER)


@dataclasses.dataclass(frozen=True)
class ColumnSpec:
    """One column as the relations zone reads it: its kind (`number`, `label` or '' kept), its top code, its spellings."""

    name: str
    place: int
    kind: str
    top: int
    spellings: "tuple[str, ...]"
    why_kept: str
    # Lane IN-7 (`inside_holds.carried_spec`): the spellings are the column's real ones the readers let through,
    # each written as it is, the rest drawn from their real counts.
    carried: bool = False


def number_of(text: object) -> "float | None":
    """A cell's number where the whole cell is one (finite), else None."""
    return _number(text)


def _block_spellings(block: "dict[str, object]") -> "tuple[str, ...]":
    """A label block's published spellings: every level's variants (the cells as written)."""
    levels = block["levels"] if "levels" in block else None
    out: "list[str]" = []
    if not isinstance(levels, list):
        return ()
    for level in levels:
        if not isinstance(level, dict):
            continue
        variants = level["variants"] if "variants" in level else None
        if isinstance(variants, dict):
            for spelling in variants:
                if isinstance(spelling, str):
                    out += [spelling]
    return tuple(out)


def column_spec(block: object, place: int, persons: "tuple[str, ...]") -> ColumnSpec:
    """How the relations zone reads one column block of a description written (a dict as `profile.serialize` holds it)."""
    if not isinstance(block, dict):
        return ColumnSpec("", place, "", 0, (), "not a column block")
    name = block["name"] if "name" in block and isinstance(block["name"], str) else ""
    role = block["role"] if "role" in block and isinstance(block["role"], str) else ""
    structural = block["structural_role"] if "structural_role" in block else ""
    top = block["top_coded"] if "top_coded" in block and isinstance(block["top_coded"], int) else 0
    why = ""
    if name in persons:
        why = NAMES_THE_PERSON
    elif structural == "identifier":
        why = AN_IDENTIFIER
    elif top not in (0, 90):
        why = "a Safe Harbor top code other than an age's"
    else:
        for key in KEPT_KEYS:
            if key in block and block[key]:
                why = f"carries {key}"
                break
    if not why and role in NUMBER_ROLES:
        return ColumnSpec(name, place, NUMBER, top, (), "")
    if not why and role in LABEL_ROLES:
        return ColumnSpec(name, place, LABEL, 0, _block_spellings(block), "")
    return ColumnSpec(name, place, "", top, (), why or f"its kind ({role}) is drawn by the description")


def record_document(document: object, rows_described: object) -> object:
    """The description the inside record reads its columns' holds from: `document`, each column the patient layer
    holds read as the rows' description wrote it (batch 4y's fix round, Codex's review of the batch, item 1).

    The patient layer empties the block of a repeated column no row family
    carries (contract 4.6c.5, S30: no key but its name, place and role), so
    its age top code, its year cut, its identifier reading and every other
    hold were lost to the record, and the twin's writer drew it from the
    record's model uncapped (981 ages past 90 on a table of ages fixed but
    once a person). `rows_described` is the description of the same run
    before the layer (its `columns` blocks, one a column, the rows' own);
    each column `document`'s `grain` classes `held` takes that block, so
    the record keeps it as the rows' description held it. A document with
    no `grain`, or no `rows_described`, comes back as it is. Raises
    nothing; reads the documents alone; no I/O.
    """
    if not isinstance(document, dict) or not isinstance(rows_described, dict):
        return document
    relationships = document["relationships"] if "relationships" in document else None
    grain = relationships["grain"] if isinstance(relationships, dict) and "grain" in relationships else None
    classes = grain["classes"] if isinstance(grain, dict) and "classes" in grain else None
    held: "set[str]" = set()
    if isinstance(classes, list):
        for entry in classes:
            if not isinstance(entry, dict) or "class" not in entry or "column" not in entry:
                continue
            if entry["class"] == "held" and isinstance(entry["column"], str):
                held = held | {entry["column"]}
    columns = document["columns"] if "columns" in document else None
    rows_columns = rows_described["columns"] if "columns" in rows_described else None
    if not held or not isinstance(columns, list) or not isinstance(rows_columns, list):
        return document
    by_name: "dict[str, object]" = {}
    for block in rows_columns:
        if isinstance(block, dict) and "name" in block and isinstance(block["name"], str):
            by_name[block["name"]] = block
    read: "list[object]" = []
    for block in columns:
        name = block["name"] if isinstance(block, dict) and "name" in block else None
        read += [by_name[name] if isinstance(name, str) and name in held and name in by_name else block]
    out: "dict[str, object]" = {}
    for key in document:
        out[key] = read if key == "columns" else document[key]
    return out


def specs_of(document: object) -> "list[ColumnSpec]":
    """Every column of a description written, read by `column_spec`, with the persons its settings name."""
    columns = document["columns"] if isinstance(document, dict) and "columns" in document else None
    settings = document["settings"] if isinstance(document, dict) and "settings" in document else None
    persons: "list[str]" = []
    named = settings["person_columns"] if isinstance(settings, dict) and "person_columns" in settings else None
    if isinstance(named, list):
        for each in named:
            if isinstance(each, str):
                persons += [each]
    out: "list[ColumnSpec]" = []
    if isinstance(columns, list):
        for place in range(len(columns)):
            out += [column_spec(columns[place], place, tuple(persons))]
    return out


# -- one column encoded: its marginal over all rows, its sample's values ----------------------------


@dataclasses.dataclass
class Encoded:
    """One modelled column: its zone entry (marginal over all rows) and its values on the fit's rows."""

    entry: "dict[str, object]"
    states: "list[int]"
    positions: "list[float]"
    codes: "list[int]"


def _grid_of(ordered: "list[float]") -> "list[float]":
    last = len(ordered) - 1
    return [ordered[(k * last) // (GRID - 1)] for k in range(GRID)]


def _place_of(cell: str) -> "float | None":
    """A cell's place on the number line: its number, or a censoring atom's place; None for anything else."""
    value = _number(cell)
    if value is not None:
        return value
    atom = _atom(cell)
    return atom[0] if atom is not None else None


# A number written inside a wrapper (`72.5 kg`, `$12.00`, `45 years`) is read as its number where at least this
# share of a column's cells that are not bare numbers wear one wrapper (lane IN-7: the column is modelled, its
# number drawn and written back inside the wrapper; a cell wearing another wrapper is a word of the column).
WRAPPER_SHARE = 0.95
_FIGURES = "0123456789"


def wrapped(text: object) -> "tuple[str, str, str] | None":
    """A cell written as one number inside a wrapper: its prefix, its number as written, its suffix; None for any other cell.

    The number is the first run of figures with at most one point (a
    point just before the run joins it, a minus sign at the cell's start
    too); a wrapper holds no figure, and a bare number has none.
    """
    bare = _bare(text)
    start = -1
    for place in range(len(bare)):
        if bare[place] in _FIGURES:
            start = place
            break
    if start < 0:
        return None
    if start > 0 and bare[start - 1] == ".":
        start -= 1
    if start == 1 and bare[0] == "-":
        start = 0
    end = start + 1 if bare[start] in "-." else start
    pointed = bare[start] == "."
    while end < len(bare) and (bare[end] in _FIGURES or (bare[end] == "." and not pointed)):
        if bare[end] == ".":
            pointed = True
        end += 1
    prefix, core, suffix = bare[:start], bare[start:end], bare[end:]
    if not prefix and not suffix:
        return None
    for character in prefix + suffix:
        if character in _FIGURES:
            return None
    if _number(core) is None:
        return None
    return prefix, core, suffix


def common_wrapper(cells: "list[str]") -> "tuple[str, str] | None":
    """The one wrapper a number column's cells wear, where `WRAPPER_SHARE` of its cells that are not bare numbers wear it."""
    tallies: "dict[tuple[str, str], int]" = {}
    others = 0
    for cell in cells:
        bare = _bare(cell)
        if not bare or _number(bare) is not None or _atom(bare) is not None:
            continue
        others += 1
        found = wrapped(bare)
        if found is not None:
            key = (found[0], found[2])
            tallies[key] = (tallies[key] if key in tallies else 0) + 1
    ranked = sorted((-tallies[key], key) for key in tallies)
    if not ranked or -ranked[0][0] < MIN_ROWS or -ranked[0][0] < WRAPPER_SHARE * others:
        return None
    return ranked[0][1]


def _place_in(cell: str, wrapper: "tuple[str, str] | None") -> "float | None":
    """A cell's place on the number line, a number inside the column's wrapper read as its number."""
    if wrapper is not None:
        found = wrapped(cell)
        if found is not None and (found[0], found[2]) == wrapper:
            return _number(found[1])
    return _place_of(cell)


def _spike_text(cells: "list[str]", place: float, wrapper: "tuple[str, str] | None" = None) -> str:
    """The commonest spelling of the cells at one place (a spike's text)."""
    spellings: "dict[str, int]" = {}
    for cell in cells:
        bare = _bare(cell)
        if bare and _place_in(bare, wrapper) == place:
            spellings[bare] = (spellings[bare] if bare in spellings else 0) + 1
    ranked = sorted((-spellings[text], text) for text in spellings)
    return ranked[0][1] if ranked else ""


def encode_number(spec: ColumnSpec, cells: "list[str]", rows: "list[int]") -> "Encoded | None":
    """A number column's entry (grid over all rows, decimals, atoms, spikes, states) and its fit rows' states and places."""
    positions: "list[float]" = []
    decimals: "dict[int, int]" = {}
    atoms: "dict[str, tuple[float, int]]" = {}
    counts = [0 for _state in range(STATES)]
    # How the numbers are written: in fixed point, or with an exponent (each exponent's form counted).
    fixed_cells = 0
    exponent_cells = 0
    forms: "dict[tuple[int, str, bool, int], int]" = {}
    wrapper = common_wrapper(cells)
    for cell in cells:
        bare = _bare(cell)
        if not bare:
            counts[EMPTY] += 1
            continue
        value = _number(bare)
        if value is not None:
            positions += [value]
            places = _decimals(bare)
            decimals[places] = (decimals[places] if places in decimals else 0) + 1
            written = _exponent_form(bare) if ("e" in bare or "E" in bare) else None
            if written is None:
                fixed_cells += 1
            else:
                exponent_cells += 1
                key = (written[0], written[1], written[2], written[3])
                forms[key] = (forms[key] if key in forms else 0) + 1
            continue
        atom = _atom(bare)
        if atom is not None:
            positions += [atom[0]]
            atoms[atom[1]] = (atom[0], (atoms[atom[1]][1] if atom[1] in atoms else 0) + 1)
            continue
        found = wrapped(bare) if wrapper is not None else None
        if found is not None and (found[0], found[2]) == wrapper:
            inner = _number(found[1])
            if inner is not None:
                positions += [inner]
                places = _decimals(found[1])
                decimals[places] = (decimals[places] if places in decimals else 0) + 1
                continue
        counts[WORD] += 1
    if len(positions) < MIN_ROWS or len(set(positions)) < 3:
        return None
    ordered = sorted(positions)
    del positions
    spikes: "list[object]" = [None, None]
    low_end, high_end = ordered[0], ordered[len(ordered) - 1]
    at_low = len([place for place in ordered if place == low_end])
    at_high = len([place for place in ordered if place == high_end])
    rest = len(ordered)
    for side, place, held in ((0, low_end, at_low), (1, high_end, at_high)):
        if held >= MIN_ROWS and held >= SPIKE_SHARE * len(ordered) and rest - held >= MIN_ROWS:
            spikes[side] = [place, _spike_text(cells, place, wrapper)]
            rest = rest - held
    lowest = spikes[0][0] if isinstance(spikes[0], list) else None
    highest = spikes[1][0] if isinstance(spikes[1], list) else None
    middle = [place for place in ordered if place != lowest and place != highest]
    del ordered
    counts[LOW] = at_low if lowest is not None else 0
    counts[HIGH] = at_high if highest is not None else 0
    counts[PRESENT] = len(middle)
    if len(set(middle)) < 3:
        return None
    kept_atoms: "list[list[object]]" = []
    for text in sorted(atoms):
        if atoms[text][1] >= MIN_ROWS:
            kept_atoms += [[atoms[text][0], text]]
    places_mode = 0
    best = -1
    for places in sorted(decimals):
        if decimals[places] > best:
            best, places_mode = decimals[places], places
    entry: "dict[str, object]" = {
        "name": spec.name, "place": spec.place, "kind": NUMBER, "grid": _grid_of(middle),
        "decimals": places_mode, "atoms": kept_atoms, "spikes": spikes, "top": spec.top, "states": counts,
    }
    if exponent_cells > fixed_cells:
        # A column most of whose numbers are written with an exponent writes its twin so: its commonest form
        # (the mantissa's places, the mark, a plus shown, the power's figures), so `1.234e-6` stays `1.234e-6`.
        ranked = sorted((-forms[key], key) for key in forms)
        chosen = ranked[0][1]
        entry["exponent"] = [chosen[0], chosen[1], chosen[2], chosen[3]]
    if wrapper is not None:
        entry["wrapper"] = [wrapper[0], wrapper[1]]
    del middle
    states: "list[int]" = []
    places_of: "list[float]" = []
    for row in rows:
        bare = _bare(cells[row])
        spot = _place_in(bare, wrapper) if bare else None
        if not bare:
            states += [EMPTY]
            places_of += [0.0]
        elif spot is None:
            states += [WORD]
            places_of += [0.0]
        else:
            states += [LOW if spot == lowest else (HIGH if spot == highest else PRESENT)]
            places_of += [spot]
    return Encoded(entry, states, places_of, [])


def encode_label(spec: ColumnSpec, cells: "list[str]", rows: "list[int]") -> "Encoded | None":
    """A label column's entry (its modelled published spellings and their counts over all rows) and its fit rows' codes."""
    allowed = set(spec.spellings)
    counts: "dict[str, int]" = {}
    for cell in cells:
        if not isinstance(cell, str):
            raise TypeError("synthtwin reads a table's cells as text only.")
        counts[cell] = (counts[cell] if cell in counts else 0) + 1
    ranked = sorted((-counts[cell], cell) for cell in counts if (cell in allowed or not _bare(cell)))
    levels: "list[str]" = []
    level_counts: "list[int]" = []
    for negative, cell in ranked:
        if len(levels) < LEVEL_CAP and -negative >= MIN_ROWS:
            levels += [cell]
            level_counts += [-negative]
    if len(levels) < 1:
        return None
    rest_rows = len(cells) - sum(level_counts)
    if len(levels) + (1 if rest_rows > 0 else 0) < 2:
        return None
    code_of: "dict[str, int]" = {}
    for code in range(len(levels)):
        code_of[levels[code]] = code
    rest_code = len(levels)
    codes = [code_of[cells[row]] if cells[row] in code_of else rest_code for row in rows]
    entry: "dict[str, object]" = {
        "name": spec.name, "place": spec.place, "kind": LABEL, "levels": levels, "counts": level_counts,
        "rest": rest_rows,
    }
    if spec.carried:
        # The rest's own spellings with their real counts (lane IN-7): a rest row of the twin is drawn among them,
        # the rows of a spelling the readers hold filled from the description's twin as before.
        others = sorted((-counts[cell], cell) for cell in counts if cell in allowed and cell not in code_of
                        and _bare(cell))
        entry["carried"] = True
        entry["others"] = [[cell, -negative] for negative, cell in others[:OTHERS_CAP]]
    return Encoded(entry, [], [], codes)


def encode(spec: ColumnSpec, cells: "list[str]", rows: "list[int]", persons: "Persons | None" = None) -> "Encoded | None":
    """One column encoded for the zone, or None where it is kept on the description's twin.

    Where a person column repeats (`persons`), a column held once a person
    is described over each person's first row (its shape a person, not a
    row), and a number counting each person's rows in row order is a
    sequence the twin writes as its own rows' places, with no fit.
    """
    if spec.kind not in (NUMBER, LABEL):
        return None
    level = level_of(spec, cells, persons)
    if level == SEQUENCE:
        states: "list[int]" = []
        places: "list[float]" = []
        for row in rows:
            value = _number(cells[row])
            states += [PRESENT if value is not None else EMPTY]
            places += [value if value is not None else 0.0]
        entry: "dict[str, object]" = {"name": spec.name, "place": spec.place, "kind": NUMBER, "level": SEQUENCE}
        return Encoded(entry, states, places, [])
    if level == PATIENT and persons is not None:
        described = [cells[row] for row in range(len(cells)) if persons.first[row]]
        mapped = [0 for _row in range(len(cells))]
        firsts: "dict[int, int]" = {}
        for row in range(len(cells)):
            if persons.first[row]:
                firsts[persons.person[row]] = len(firsts)
        for row in range(len(cells)):
            mapped[row] = firsts[persons.person[row]]
        found = (encode_number(spec, described, [mapped[row] for row in rows]) if spec.kind == NUMBER
                 else encode_label(spec, described, [mapped[row] for row in rows]))
    else:
        found = encode_number(spec, cells, rows) if spec.kind == NUMBER else encode_label(spec, cells, rows)
    if found is not None:
        found.entry["level"] = level
    return found


# -- normal scores and terms -------------------------------------------------------------------------


def normal_scores(states: "list[int]", positions: "list[float]",
                  counted: "tuple[int, ...]" = NUMBER_STATES) -> "list[float]":
    """Each row's normal score among the rows whose state is `counted` (mid-ranks for ties); 0.0 on every other row."""
    present = sorted((positions[row], row) for row in range(len(states)) if states[row] in counted)
    out = [0.0 for _row in range(len(states))]
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


def _cube(value: float) -> float:
    return value * value * value if value > 0.0 else 0.0


def spline(score: float, which: int) -> float:
    """Restricted cubic spline term `which` (0 or 1) of a normal score, knots `KNOTS`, scaled by the outer knots' span squared."""
    knot = KNOTS[which]
    inner, outer = KNOTS[2], KNOTS[3]
    value = (_cube(score - knot) - _cube(score - inner) * (outer - knot) / (outer - inner)
             + _cube(score - outer) * (inner - knot) / (outer - inner))
    span = KNOTS[3] - KNOTS[0]
    return value / (span * span)


@dataclasses.dataclass(frozen=True)
class HeldFrame:
    """A drawn column's frame held compactly while later columns read it (lane IN-8, plan P4-D502).

    A number's scores as each row's place in `table`, its different scores
    in the order first met (`places`, the fewest bytes a row that hold the
    count), and its states a byte a row; a label's codes the fewest bytes a
    row. `frame_rows` gives a block of rows back as the lists a term reads,
    each value the one held: a score of -0.0 is held apart from 0.0.
    """

    rows: int
    table: "list[float]"
    places: chain_walk.Packed
    states: bytes
    codes: chain_walk.Packed


@dataclasses.dataclass
class Frame:
    """The values a term reads: for a number its scores and states, for a label its codes.

    A frame of the draw that a later column reads is held compactly
    (`held_frame`): its lists are then empty and `held` holds them.
    """

    kind: str
    scores: "list[float]"
    states: "list[int]"
    codes: "list[int]"
    held: "HeldFrame | None" = None


def held_frame(frame: Frame, rows: int) -> Frame:
    """The frame of `rows` rows held compactly (`HeldFrame`), its values unchanged."""
    if frame.held is not None:
        return frame
    table: "list[float]" = []
    index: "dict[object, int]" = {}
    places: "list[int]" = []
    for score in frame.scores:
        # A zero is keyed by its spelling, so -0.0 is held apart from 0.0 (equal as numbers, not as signs).
        key: object = score if score != 0.0 else f"{score}"
        if key not in index:
            index[key] = len(table)
            table += [score]
        places += [index[key]]
    packed_places = chain_walk.packed(len(places), chain_walk.width_for(max(0, len(table) - 1)))
    for row in range(len(places)):
        chain_walk.put(packed_places, row, places[row])
    del places
    states = bytes([state for state in frame.states])
    top = 0
    for code in frame.codes:
        if code > top:
            top = code
    codes = chain_walk.packed(len(frame.codes), chain_walk.width_for(top))
    for row in range(len(frame.codes)):
        chain_walk.put(codes, row, frame.codes[row])
    return Frame(frame.kind, [], [], [], HeldFrame(rows, table, packed_places, states, codes))


def frame_rows(frame: Frame, start: int, stop: int) -> Frame:
    """Rows `start` to `stop` of a frame, as the lists a term reads (a held frame's values given back)."""
    held = frame.held
    if held is None:
        return Frame(frame.kind, frame.scores[start:stop], frame.states[start:stop], frame.codes[start:stop])
    scores: "list[float]" = []
    states: "list[int]" = []
    codes: "list[int]" = []
    if held.table:
        table = held.table
        data, width = held.places.data, held.places.width
        scores = [table[chain_walk.read_code(data, width, row)] for row in range(start, min(stop, held.rows))]
    if held.states:
        states = [state for state in held.states[start:stop]]
    if chain_walk.size_of(held.codes):
        data, width = held.codes.data, held.codes.width
        codes = [chain_walk.read_code(data, width, row) for row in range(start, min(stop, held.rows))]
    return Frame(frame.kind, scores, states, codes)


def term_values(term: object, frames: "dict[str, Frame]", rows: int) -> "list[float]":
    """One term's value on every row of `frames` (the fit's rows or the twin's)."""
    parts = _list(term)
    head = _text(parts[0])
    if head == "one":
        return [1.0 for _row in range(rows)]
    if head == "prod":
        first = term_values(parts[1], frames, rows)
        second = term_values(parts[2], frames, rows)
        return [a * b for a, b in zip(first, second)]
    name = _text(parts[1])
    if name not in frames:
        raise RelationsError("The inside record's relations zone names a parent it does not model.")
    frame = frames[name]
    if head == "z":
        return [each for each in frame.scores]
    if head == "s":
        which = _int(parts[2])
        return [spline(score, which) if state in NUMBER_STATES else 0.0 for score, state in zip(frame.scores, frame.states)]
    if head == "state":
        wanted = _int(parts[2])
        return [1.0 if state == wanted else 0.0 for state in frame.states]
    if head == "level":
        wanted = _int(parts[2])
        return [1.0 if code == wanted else 0.0 for code in frame.codes]
    raise RelationsError("The inside record's relations zone names a term of a kind it does not draw.")


# -- linear algebra in the order written ------------------------------------------------------------


def _dot(first: "list[float]", second: "list[float]") -> float:
    return math.fsum([a * b for a, b in zip(first, second)])


_NOUGHT_AND_ONE = frozenset([0.0, 1.0])


def _finite(values: "list[float]") -> bool:
    """Whether every value is finite: their exact sum is (an infinity or a value that is not a number carries through)."""
    try:
        return math.isfinite(math.fsum(values))
    except (OverflowError, ValueError):
        return False


@dataclasses.dataclass(frozen=True)
class DesignFacts:
    """What a Gram matrix's sums may skip (lane SPEED-2M): each column's rows holding a one where it holds noughts and
    ones alone (None for any other), and whether each column is finite."""

    ones: "tuple[list[int] | None, ...]"
    finite: "tuple[bool, ...]"


def design_facts(columns: "list[list[float]]") -> DesignFacts:
    """The facts `_gram` reads of a design's columns, read once for the fits that share the columns."""
    ones: "list[list[int] | None]" = []
    finite: "list[bool]" = []
    for column in columns:
        if set(column) <= _NOUGHT_AND_ONE:
            ones += [[row for row, value in enumerate(column) if value == 1.0]]
            finite += [True]
        else:
            ones += [None]
            finite += [_finite(column)]
    return DesignFacts(tuple(ones), tuple(finite))


def _gram(columns: "list[list[float]]", weights: "list[float] | None",
          facts: "DesignFacts | None" = None) -> "list[list[float]]":
    """The (weighted) Gram matrix: each entry `math.fsum` of a weighted column's products with a column, in row order.

    THE SAME SUMS, OVER THE ROWS THAT ADD (lane SPEED-2M). Where the
    column ``b`` holds noughts and ones alone, its product with a finite
    value is that value on a one and a nought on a nought, and
    `math.fsum` gives the same correctly rounded sum without the noughts
    (and +0.0 for a sum of noughts alone): the sum over the rows holding
    a one. Where the weighted column ``a`` comes of such a column with
    finite weights of at most one in size, it is a nought off its ones
    and its products are summed over them. Only finite values are so
    read (`DesignFacts.finite`, and the weights read here); any other
    entry is summed over every row as written.
    """
    size = len(columns)
    weighted = columns if weights is None else [[x * w for x, w in zip(column, weights)] for column in columns]
    known = facts if facts is not None else design_facts(columns)
    bounded = weights is None or (_finite(weights) and (not weights or (max(weights) <= 1.0 and min(weights) >= -1.0)))
    out = [[0.0 for _b in range(size)] for _a in range(size)]
    for a in range(size):
        # ...a weighted column is finite where its column is and the weights are finite and bounded by one.
        finite_a = bounded and known.finite[a]
        for b in range(a + 1):
            value = _summed(weighted[a], columns[b], known.ones[a] if bounded else None, known.ones[b], finite_a,
                            known.finite[b])
            out[a][b] = value
            out[b][a] = value
    return out


def _summed(first: "list[float]", second: "list[float]", first_ones: "list[int] | None",
            second_ones: "list[int] | None", first_finite: bool, second_finite: bool) -> float:
    """`_dot(first, second)`, the same bits, summed over the rows that add where one side is noughts off a list of rows.

    ``second_ones``, where given, are the rows on which ``second`` is one,
    and it is nought on every other: with ``first`` finite, each product is
    ``first``'s value on those rows and a nought elsewhere. ``first_ones``,
    where given, are rows off which ``first`` is nought: with ``second``
    finite, every product off them is a nought. `math.fsum` passes over a
    nought (+0.0 for a sum of noughts alone), so the sum over those rows is
    the sum over all. Anything else is `_dot` as written.
    """
    if second_ones is not None and first_finite:
        return math.fsum([first[row] for row in second_ones])
    if first_ones is not None and second_finite:
        return math.fsum([first[row] * second[row] for row in first_ones])
    return _dot(first, second)


def _cholesky(matrix: "list[list[float]]") -> "tuple[list[list[float]], list[bool]]":
    """The lower factor; a term whose pivot falls under `_PIVOT` of its diagonal is dropped (a unit row)."""
    size = len(matrix)
    lower = [[0.0 for _b in range(size)] for _a in range(size)]
    dropped = [False for _a in range(size)]
    for j in range(size):
        diagonal = matrix[j][j]
        total = diagonal - math.fsum([lower[j][k] * lower[j][k] for k in range(j)])
        if not diagonal > 0.0 or total <= _PIVOT * diagonal:
            dropped[j] = True
            lower[j][j] = 1.0
            continue
        root = math.sqrt(total)
        lower[j][j] = root
        for i in range(j + 1, size):
            lower[i][j] = (matrix[i][j] - math.fsum([lower[i][k] * lower[j][k] for k in range(j)])) / root
    return lower, dropped


def _solve(lower: "list[list[float]]", dropped: "list[bool]", rhs: "list[float]") -> "list[float]":
    size = len(rhs)
    middle = [0.0 for _a in range(size)]
    for j in range(size):
        if dropped[j]:
            continue
        middle[j] = (rhs[j] - math.fsum([lower[j][k] * middle[k] for k in range(j)])) / lower[j][j]
    out = [0.0 for _a in range(size)]
    for j in range(size - 1, -1, -1):
        if dropped[j]:
            continue
        out[j] = (middle[j] - math.fsum([lower[i][j] * out[i] for i in range(j + 1, size)])) / lower[j][j]
    return out


def _ridged(matrix: "list[list[float]]") -> "list[list[float]]":
    for j in range(len(matrix)):
        matrix[j][j] = matrix[j][j] * (1.0 + _RIDGE)
    return matrix


def _predictor(columns: "list[list[float]]", beta: "list[float]", rows: int) -> "list[float]":
    """The linear predictor, the terms added in their order."""
    eta = [0.0 for _row in range(rows)]
    for place in range(len(columns)):
        weight = beta[place]
        if weight == 0.0:
            continue
        eta = [e + weight * x for e, x in zip(eta, columns[place])]
    return eta


def expit(eta: float) -> float:
    """The logistic function, written out (`chain_walk.exponential`), its argument capped at `_ETA_CAP`."""
    capped = min(_ETA_CAP, max(-_ETA_CAP, eta))
    if capped >= 0.0:
        return 1.0 / (1.0 + chain_walk.exponential(-capped))
    lifted = chain_walk.exponential(capped)
    return lifted / (1.0 + lifted)


def _log_odds(share: float) -> float:
    bounded = min(1.0 - 1e-9, max(1e-9, share))
    return chain_walk.natural_log(bounded / (1.0 - bounded))


@dataclasses.dataclass
class Fit:
    """A fitted response: coefficients, the working weights and residuals, and the information's factor."""

    beta: "list[float]"
    weights: "list[float]"
    residuals: "list[float]"
    lower: "list[list[float]]"
    dropped: "list[bool]"
    scale: float


def least_squares(columns: "list[list[float]]", response: "list[float]") -> Fit:
    """Ordinary least squares in the order written; `scale` is the residual variance."""
    rows = len(response)
    lower, dropped = _cholesky(_ridged(_gram(columns, None)))
    beta = _solve(lower, dropped, [0.0 if dropped[a] else _dot(columns[a], response) for a in range(len(columns))])
    eta = _predictor(columns, beta, rows)
    residuals = [y - e for y, e in zip(response, eta)]
    kept = len([flag for flag in dropped if not flag])
    scale = math.fsum([r * r for r in residuals]) / max(1, rows - kept)
    return Fit(beta, [1.0 for _row in range(rows)], residuals, lower, dropped, max(scale, 1e-12))


def _deviance(response: "list[float]", eta: "list[float]") -> float:
    """A logistic fit's deviance at a linear predictor (its probabilities kept off nought and one)."""
    return _scored(response, eta)[0]


# A predictor holding at most this share of different values a row has its logistic function and logarithms read
# once a value (lane SPEED-2M): a fit on labels alone holds one a combination of their levels.
_FEW_VALUES_SHARE = 0.25


def _expits(eta: "list[float]") -> "list[float]":
    """`expit` of each row's predictor, each different value worked out once where few are (the same values).

    `expit` is a fixed function of its argument's value, and of nought
    and minus nought alike (both give one half), so a table of the
    different values gives every row the value its own call gives.
    """
    different = set(eta)
    if len(different) > _FEW_VALUES_SHARE * len(eta):
        return [expit(e) for e in eta]
    table = {e: expit(e) for e in different}
    return [table[e] for e in eta]


def _scored(response: "list[float]", eta: "list[float]") -> "tuple[float, list[float]]":
    """The deviance at a predictor and each row's `expit` of it (lane SPEED-2M: the next step reads them, made once).

    THE SAME DEVIANCE, ONE LOGARITHM A ROW. A row's term is
    `y ln(m) + (1 - y) ln(1 - m)`, its mean `m` kept within 1e-15 of
    nought and one, so both logarithms are negative: where `y` is one
    the term is `ln(m) + 0 ln(1 - m)`, `ln(m)` plus a minus nought, which
    is `ln(m)` exactly; where `y` is nought it is `ln(1 - m)` exactly. So
    such a row's term is its one logarithm, the value written out gives;
    any other `y` is worked out as written. Each different predictor's
    terms are worked out once where few are (`_FEW_VALUES_SHARE`). The
    terms are summed by `math.fsum` in row order as before.
    """
    means = _expits(eta)
    high = 1.0 - 1e-15
    if len(set(eta)) <= _FEW_VALUES_SHARE * len(eta):
        hits: "dict[float, float]" = {}
        misses: "dict[float, float]" = {}
        terms: "list[float]" = []
        for y, e, m in zip(response, eta, means):
            if y == 1.0:
                if e not in hits:
                    hits[e] = chain_walk.natural_log(min(high, max(1e-15, m)))
                terms += [hits[e]]
            elif y == 0.0:
                if e not in misses:
                    misses[e] = chain_walk.natural_log(1.0 - min(high, max(1e-15, m)))
                terms += [misses[e]]
            else:
                mean = min(high, max(1e-15, m))
                terms += [y * chain_walk.natural_log(mean) + (1.0 - y) * chain_walk.natural_log(1.0 - mean)]
        return -2.0 * math.fsum(terms), means
    clamped = [min(high, max(1e-15, m)) for m in means]
    return -2.0 * math.fsum([chain_walk.natural_log(mean) if y == 1.0 else (
        chain_walk.natural_log(1.0 - mean) if y == 0.0 else
        y * chain_walk.natural_log(mean) + (1.0 - y) * chain_walk.natural_log(1.0 - mean))
        for y, mean in zip(response, clamped)]), means


# A Newton step that raises a logistic fit's deviance is halved up to this many times (lane IN-7: a fit near
# separation, a label level no row of some parent's level holds, took a step to coefficients of 1e9 and drew its
# label at a share far from the table's; a step that lowers the deviance is taken whole, so a fit that settles
# as before keeps every byte).
_HALVINGS = 60


def logistic(columns: "list[list[float]]", response: "list[float]") -> Fit:
    """A logistic fit by iteratively reweighted least squares (the first term the intercept), ridged; its predictor capped at the draw.

    A step that raises the deviance is halved until it does not (at most
    `_HALVINGS` times), so a fit near separation walks its coefficients
    out slowly instead of jumping to a meaningless point.
    """
    rows = len(response)
    size = len(columns)
    share = math.fsum(response) / max(1, rows)
    beta = [0.0 for _a in range(size)]
    beta[0] = _log_odds(share)
    lower: "list[list[float]]" = []
    dropped: "list[bool]" = []
    weights: "list[float]" = []
    means: "list[float]" = []
    # THE PREDICTOR AND ITS MEANS MADE ONCE A STEP (lane SPEED-2M): the deviance of the coefficients taken reads the
    # predictor and each row's mean the next step reads, so the step takes them (the same lists) instead of making
    # them again.
    eta_now = _predictor(columns, beta, rows)
    deviance, means_now = _scored(response, eta_now)
    facts = design_facts(columns)
    for _step in range(_ITERATIONS):
        eta = eta_now
        means = means_now
        weights = [max(m * (1.0 - m), 1e-10) for m in means]
        working = [e + (y - m) / w for e, y, m, w in zip(eta, response, means, weights)]
        lower, dropped = _cholesky(_ridged(_gram(columns, weights, facts)))
        weighted = [w * z for w, z in zip(weights, working)]
        finite_weighted = _finite(weighted)
        moved = _solve(lower, dropped, [0.0 if dropped[a] else _summed(columns[a], weighted, facts.ones[a], None,
                                                                         facts.finite[a], finite_weighted)
                                        for a in range(size)])
        if not all([math.isfinite(value) for value in moved]):
            beta = moved
            break
        eta_moved = _predictor(columns, moved, rows)
        reached, means_moved = _scored(response, eta_moved)
        halved = 0
        while not reached <= deviance + 1e-9 * (1.0 + abs(deviance)) and halved < _HALVINGS:
            moved = [(a + b) / 2.0 for a, b in zip(moved, beta)]
            eta_moved = _predictor(columns, moved, rows)
            reached, means_moved = _scored(response, eta_moved)
            halved += 1
        change = max([abs(a - b) for a, b in zip(moved, beta)]) if size else 0.0
        beta = moved
        deviance = reached
        eta_now = eta_moved
        means_now = means_moved
        if change < _CHANGE:
            break
    if not all([math.isfinite(value) for value in beta]):
        # A fit that leaves the numbers binary64 holds draws the level at its share alone.
        beta = [0.0 for _a in range(size)]
        beta[0] = _log_odds(share)
        eta_now = _predictor(columns, beta, rows)
        means_now = _expits(eta_now)
    means = means_now
    weights = [max(m * (1.0 - m), 1e-10) for m in means]
    lower, dropped = _cholesky(_ridged(_gram(columns, weights, facts)))
    return Fit(beta, weights, [y - m for y, m in zip(response, means)], lower, dropped, 1.0)


def critical(freedom: int) -> float:
    """The chi-square quantile at 1 - `GATE_LEVEL`: written to 40 degrees of freedom, Wilson-Hilferty past them."""
    if freedom <= 0:
        return _INFINITY
    if freedom <= len(_CHI_SQUARE_999):
        return _CHI_SQUARE_999[freedom - 1]
    ninth = 2.0 / (9.0 * freedom)
    root = 1.0 - ninth + _Z_999 * math.sqrt(ninth)
    return freedom * root * root * root


def score_statistic(fit: Fit, columns: "list[list[float]]", block: "list[list[float]]") -> float:
    """The score statistic for adding `block` to `fit` (the variance of a least-squares fit read from `scale`)."""
    size = len(columns)
    width = len(block)
    if width == 0:
        return 0.0
    weighted_block = [[b * w for b, w in zip(term, fit.weights)] for term in block]
    score = [_dot(term, fit.residuals) for term in block]
    cross = [[0.0 if fit.dropped[a] else _dot(weighted_block[k], columns[a]) for a in range(size)] for k in range(width)]
    solved = [_solve(fit.lower, fit.dropped, cross[k]) for k in range(width)]
    variance = [[0.0 for _b in range(width)] for _a in range(width)]
    for k in range(width):
        for m in range(k + 1):
            value = _dot(weighted_block[k], block[m]) - _dot(cross[k], solved[m])
            variance[k][m] = value
            variance[m][k] = value
    lower, dropped = _cholesky(variance)
    if all(dropped):
        return 0.0
    solved_score = _solve(lower, dropped, [0.0 if dropped[k] else score[k] for k in range(width)])
    statistic = _dot(score, solved_score) / fit.scale
    return statistic if statistic > 0.0 else 0.0


# -- one response: blocks, selection and the final fit ----------------------------------------------


@dataclasses.dataclass(frozen=True)
class Block:
    """A named group of terms that enters a fit together."""

    terms: "tuple[object, ...]"
    parent: str
    kind: str


def _main_block(name: str, frame: Frame) -> "Block | None":
    terms: "list[object]" = []
    if frame.kind == NUMBER:
        terms += [["z", name]]
        for state in (EMPTY, WORD, LOW, HIGH):
            if len([s for s in frame.states if s == state]) >= MIN_ROWS:
                terms += [["state", name, state]]
    else:
        tallies: "dict[int, int]" = {}
        for code in frame.codes:
            tallies[code] = (tallies[code] if code in tallies else 0) + 1
        ranked = sorted((-tallies[code], code) for code in tallies)
        for negative, code in ranked[1: 1 + INDICATOR_CAP]:
            if -negative >= MIN_ROWS:
                terms += [["level", name, code]]
    return Block(tuple(terms), name, "main") if terms else None


def main_block(name: str, frame: Frame) -> "Block | None":
    """A parent's main block: a number's score and its states held by `MIN_ROWS` rows, a label's levels but the commonest (lane IN-7 reads it too)."""
    return _main_block(name, frame)


def _curve_block(name: str, frame: Frame) -> "Block | None":
    if frame.kind != NUMBER or len(set(frame.scores)) < 10:
        return None
    return Block((["s", name, 0], ["s", name, 1]), name, "curve")


def _interactions(first: Block, second: Block, frames: "dict[str, Frame]") -> "Block | None":
    """The interaction of two main blocks: label indicators times a number's score or another label's indicators."""
    left = [term for term in first.terms if _text(_list(term)[0]) in ("z", "level")]
    right = [term for term in second.terms if _text(_list(term)[0]) in ("z", "level")]
    if not left or not right or len(left) * len(right) > INTERACTION_DF_CAP:
        return None
    terms: "list[object]" = []
    for a in left:
        for b in right:
            terms += [["prod", a, b]]
    return Block(tuple(terms), first.parent + "\x00" + second.parent, "interaction")


def _evaluated(block: Block, frames: "dict[str, Frame]", rows: int, keep: "list[int] | None") -> "list[list[float]]":
    out: "list[list[float]]" = []
    for term in block.terms:
        values = term_values(term, frames, rows)
        out += [values if keep is None else [values[row] for row in keep]]
    return out


@dataclasses.dataclass
class Target:
    """A response as the fits read it: a number's score on its present rows, or a label's codes."""

    kind: str
    response: "list[float]"
    rows: "list[int]"
    codes: "list[int]"
    levels: int


def _fits(target: Target, columns_of: "list[list[list[float]]]") -> "list[Fit | None]":
    """The fits of a target: one least-squares fit, or one logistic fit a non-reference level (None where too few rows)."""
    if target.kind == NUMBER:
        return [least_squares(columns_of[0], target.response)]
    out: "list[Fit | None]" = []
    for level in range(1, target.levels):
        columns = columns_of[level]
        if not columns or len(columns[0]) == 0:
            out += [None]
            continue
        response = [1.0 if target.codes[row] == level else 0.0 for row in _label_rows(target, level)]
        if len([y for y in response if y > 0.5]) < MIN_ROWS or len([y for y in response if y < 0.5]) < MIN_ROWS:
            out += [None]
            continue
        out += [logistic(columns, response)]
    return out


def _label_rows(target: Target, level: int) -> "list[int]":
    """The rows of a baseline-category fit of `level`: those holding it or the reference level (code 0)."""
    return [row for row in target.rows if target.codes[row] == level or target.codes[row] == 0]


def _design(target: Target, blocks: "list[Block]", frames: "dict[str, Frame]", rows: int) -> "list[list[list[float]]]":
    """The design of each fit of a target: the intercept and every block's terms, on that fit's rows."""
    whole: "list[list[float]]" = [[1.0 for _row in range(rows)]]
    for block in blocks:
        whole += _evaluated(block, frames, rows, None)
    if target.kind == NUMBER:
        return [[[column[row] for row in target.rows] for column in whole]]
    out: "list[list[list[float]]]" = [[]]
    for level in range(1, target.levels):
        keep = _label_rows(target, level)
        out += [[[column[row] for row in keep] for column in whole]]
    return out


def _indicators_of(block: Block, frames: "dict[str, Frame]", rows: int) -> "tuple[list[int], list[int]] | None":
    """Where every term of `block` is a level of one label parent, each level once: the parent's codes and each term's level."""
    parent = ""
    wanted: "list[int]" = []
    for term in block.terms:
        parts = _list(term)
        if _text(parts[0]) != "level":
            return None
        name = _text(parts[1])
        if parent and name != parent:
            return None
        parent = name
        wanted += [_int(parts[2])]
    if not parent or parent not in frames or len(set(wanted)) != len(wanted):
        return None
    codes = frames[parent].codes
    if frames[parent].kind != LABEL or len(codes) != rows:
        return None
    return codes, wanted


def indicator_statistic(fit: Fit, codes: "list[int]", wanted: "list[int]", used: "list[int]") -> float:
    """`score_statistic` of the fit of the intercept alone and a block of level indicators, read from sums a level.

    THE SAME NUMBER, MADE IN ONE PASS (lane W5-302). The block's terms
    are a label parent's levels `wanted` (each once) on the fit's rows
    `used` (row `used[i]` holds `codes[used[i]]`), and the fit's design
    is its intercept alone, as every screen of `select` reads a parent.
    Each product `score_statistic` sums is then a weight or a residual
    of a row at one level, or a zero, and `math.fsum` gives the same
    correctly rounded sum without the zeros (it returns +0.0 for any sum
    of zeros): the score of a level is the sum of its rows' residuals,
    the cross product with the intercept and the diagonal of the block's
    information the sum of its rows' weights, two levels' product
    nought. So the statistic is the one `score_statistic` returns, bit
    for bit, in one pass over the rows in place of one a pair of levels
    (24 levels: 348 sums over every row, now 48 over a row each). A
    fixed function of its arguments; raises nothing.
    """
    width = len(wanted)
    place: "dict[int, int]" = {}
    for k in range(width):
        place[wanted[k]] = k
    weights_at: "list[list[float]]" = [[] for _k in range(width)]
    residuals_at: "list[list[float]]" = [[] for _k in range(width)]
    for i in range(len(used)):
        code = codes[used[i]]
        if code in place:
            k = place[code]
            weights_at[k] += [fit.weights[i]]
            residuals_at[k] += [fit.residuals[i]]
    score = [math.fsum(residuals_at[k]) for k in range(width)]
    weight_sums = [math.fsum(weights_at[k]) for k in range(width)]
    cross = [[0.0 if fit.dropped[0] else weight_sums[k]] for k in range(width)]
    solved = [_solve(fit.lower, fit.dropped, cross[k]) for k in range(width)]
    variance = [[0.0 for _b in range(width)] for _a in range(width)]
    for k in range(width):
        for m in range(k + 1):
            value = (weight_sums[k] if k == m else 0.0) - _dot(cross[k], solved[m])
            variance[k][m] = value
            variance[m][k] = value
    lower, dropped = _cholesky(variance)
    if all(dropped):
        return 0.0
    solved_score = _solve(lower, dropped, [0.0 if dropped[k] else score[k] for k in range(width)])
    statistic = _dot(score, solved_score) / fit.scale
    return statistic if statistic > 0.0 else 0.0


def _block_statistic(target: Target, fits: "list[Fit | None]", design: "list[list[list[float]]]",
                     block: Block, frames: "dict[str, Frame]", rows: int) -> "tuple[float, int]":
    """The summed score statistic of a block over a target's fits, and its degrees of freedom.

    A label parent's levels screened against a fit of the intercept alone
    are read from sums a level (`indicator_statistic`, lane W5-302): the
    same statistic, in one pass over the rows.
    """
    indicators = _indicators_of(block, frames, rows)
    if indicators is not None:
        codes, wanted = indicators
        if target.kind == NUMBER:
            fit = fits[0]
            if fit is None:
                return 0.0, 0
            if len(design[0]) == 1:
                return indicator_statistic(fit, codes, wanted, target.rows), len(wanted)
        elif all(len(design[level]) == 1 for level in range(1, target.levels) if fits[level - 1] is not None):
            total = 0.0
            freedom = 0
            for level in range(1, target.levels):
                fit = fits[level - 1]
                if fit is None:
                    continue
                total += indicator_statistic(fit, codes, wanted, _label_rows(target, level))
                freedom += len(wanted)
            return total, freedom
    values = _evaluated(block, frames, rows, None)
    total = 0.0
    freedom = 0
    if target.kind == NUMBER:
        fit = fits[0]
        if fit is None:
            return 0.0, 0
        return score_statistic(fit, design[0], [[column[row] for row in target.rows] for column in values]), len(values)
    for level in range(1, target.levels):
        fit = fits[level - 1]
        if fit is None:
            continue
        keep = _label_rows(target, level)
        total += score_statistic(fit, design[level], [[column[row] for row in keep] for column in values])
        freedom += len(values)
    return total, freedom


def _residual_score(target: Target, fits: "list[Fit | None]", block: Block, frames: "dict[str, Frame]",
                    rows: int) -> float:
    """A block's plain score against a target's fits: for each of its terms and each fit, the squared sum of the
    term times the fit's residuals over the sum of the term squared times the fit's weights, summed (lane STATS-B).

    The exact statistic (`_block_statistic`) projects the block on the fit's
    own design first, which only lowers the information it divides by, so
    this never reads more than the exact one does for a single term; it
    orders the candidates of `select`'s conditional pass. A fixed function
    of its arguments; raises nothing.
    """
    values = _evaluated(block, frames, rows, None)
    total = 0.0
    for level in range(len(fits)):
        fit = fits[level]
        if fit is None or fit.scale <= 0.0:
            continue
        keep = target.rows if target.kind == NUMBER else _label_rows(target, level + 1)
        for column in values:
            term = [column[row] for row in keep]
            if len(term) != len(fit.residuals):
                continue
            information = math.fsum([x * x * w for x, w in zip(term, fit.weights)])
            if information <= 0.0:
                continue
            score = math.fsum([x * r for x, r in zip(term, fit.residuals)])
            total += score * score / (information * fit.scale)
    return total


def _standardised(statistic: float, freedom: int) -> float:
    """How far a statistic stands past its gate, comparable across degrees of freedom."""
    if freedom <= 0:
        return -_INFINITY
    return (statistic - critical(freedom)) / math.sqrt(2.0 * freedom)


def select(target: Target, candidates: "list[Block]", frames: "dict[str, Frame]",
           rows: int) -> "tuple[list[Block], list[Fit | None]]":
    """Parents by their score statistics against the intercept alone, then those the chosen ones mask, then curves and
    interactions given them.

    A number parent is screened on its main block and its curve block
    together, so a relation with no straight part (a U shape) still
    brings its parent in; the curve then enters as an extra by its own
    statistic given the main blocks. Each parent the screen leaves out is
    read again given the chosen ones (lane STATS-B), so a relation that
    confounding hides from the screen enters too. The three steps are
    `_screen`, `_conditional` and `_refine` (lane SPEED-2M: the fits kept
    between rounds read each apart); this is the three in their order.
    """
    chosen, design, fits = _screen(target, candidates, frames, rows, None, "", {})
    chosen, design, fits = _conditional(target, candidates, chosen, frames, rows, design, fits, None, "", {})
    return _refine(target, chosen, frames, rows, design, fits)


def _conditional(target: Target, candidates: "list[Block]", chosen: "list[Block]", frames: "dict[str, Frame]",
                 rows: int, design: "list[list[list[float]]] | None", fits: "list[Fit | None] | None",
                 kept: "KeptFits | None", target_key: str,
                 keys: "dict[str, str]") -> "tuple[list[Block], list[list[list[float]]] | None, list[Fit | None] | None]":
    """`select`'s second step: the parents ``chosen`` by the screen, and after them those the chosen ones mask.

    THE CONDITIONAL PASS (lane STATS-B): a parent whose relation the chosen
    ones mask -- a treatment given to the older and sicker, which lowers
    the outcome's odds while its own patients' odds stand near the
    others' -- reads as nothing against the intercept alone, so the screen
    leaves it out and the twin lost the treatment's effect (the battery's
    methods table: -0.56 real, -0.06 twin, and with it the effect's change
    with age, the matched difference and the Cox model's). Each candidate
    the screen left out is read again given the chosen parents, by the
    same gate, and the strongest enter up to `PARENT_CAP` in all.

    ``design`` and ``fits`` are the intercept alone's (None where the
    screen made none); the design and fits returned are those of the
    parents returned where this step made them, the intercept alone's
    where no parent was chosen, and None otherwise (`_refine` then makes
    them). With ``kept`` (lane SPEED-2M), the parents this step adds are
    held under a digest of ``target_key`` and every candidate's key in
    ``keys`` in their order -- everything the step reads, since the
    screen's choice is itself a fixed function of them -- and taken where
    held; they are not counted among the statistics and models taken or
    made. A fixed function of its arguments; raises what `_fits` raises.
    """
    chosen = [block for block in chosen]
    if not chosen:
        return chosen, design, fits
    if len(chosen) >= PARENT_CAP:
        return chosen, None, None
    taken = [any(candidates[place] is block for block in chosen) for place in range(len(candidates))]
    key = _key_of(["conditional", target_key] + [keys[block.parent] for block in candidates]) if kept is not None else ""
    if kept is not None:
        held = _kept_added(kept, key, taken, PARENT_CAP - len(chosen))
        if held is not None:
            return chosen + [candidates[place] for place in held], None, None
    design = _design(target, chosen, frames, rows)
    fits = _fits(target, design)
    again: "list[tuple[float, int]]" = []
    # ...each read first by its residuals' plain score (one pass over the rows, no projection on the chosen
    # parents, so it never reads more than the exact statistic does), and the exact statistic made only for the
    # strongest `CONDITIONAL_EXACT` of them: a table of hundreds of columns reads each candidate once, cheaply.
    cheap: "list[tuple[float, int]]" = []
    for place in range(len(candidates)):
        if not taken[place]:
            cheap += [(-_residual_score(target, fits, candidates[place], frames, rows), place)]
    for _negative, place in sorted(cheap)[:CONDITIONAL_EXACT]:
        statistic, freedom = _block_statistic(target, fits, design, candidates[place], frames, rows)
        if freedom > 0 and statistic >= critical(freedom):
            again += [(-_standardised(statistic, freedom), place)]
    added = [place for _negative, place in sorted(again)[:PARENT_CAP - len(chosen)]]
    if kept is not None:
        kept.made_models[key] = {"added": [place for place in added]}
    if added:
        chosen += [candidates[place] for place in added]
        design = _design(target, chosen, frames, rows)
        fits = _fits(target, design)
    return chosen, design, fits


def _kept_added(kept: "KeptFits", key: str, taken: "list[bool]", room: int) -> "list[int] | None":
    """The places `_conditional` added under ``key`` (this round's first, then the last round's), kept again for the
    file; None where none is held or what is held could not be this step's answer (a place out of range, taken by
    the screen, repeated, or more than ``room``)."""
    found = kept.made_models[key] if key in kept.made_models else (
        kept.held_models[key] if key in kept.held_models else None)
    if not isinstance(found, dict) or sorted(found) != ["added"] or not isinstance(found["added"], list):
        return None
    places: "list[int]" = []
    for place in found["added"]:
        if not isinstance(place, int) or isinstance(place, bool) or not 0 <= place < len(taken):
            return None
        if taken[place] or place in places:
            return None
        places += [place]
    if len(places) > room:
        return None
    kept.made_models[key] = {"added": [place for place in places]}
    return places


def _screen(target: Target, candidates: "list[Block]", frames: "dict[str, Frame]", rows: int,
            kept: "KeptFits | None", target_key: str,
            keys: "dict[str, str]") -> "tuple[list[Block], list[list[list[float]]] | None, list[Fit | None] | None]":
    """`select`'s first half: the parents a target takes, by each one's score statistic against the intercept alone.

    Returns the parents chosen, in their rank, and the design and fits of
    the intercept alone the screen made (None where every statistic was
    taken from ``kept``, the fits kept from the last description of this
    table, so none was made). With ``kept``, each parent's statistic is
    looked up by `_stat_key` of ``target_key`` and the parent's
    own key in ``keys`` and made only where it is not held: the same
    statistic, for it is a fixed function of the target and the parent's
    frame, both of which the two keys digest. A fixed function of its
    arguments; raises what `_fits` raises.
    """
    design: "list[list[list[float]]] | None" = None
    fits: "list[Fit | None] | None" = None
    if kept is None:
        design = _design(target, [], frames, rows)
        fits = _fits(target, design)
    ranked: "list[tuple[float, int]]" = []
    for place in range(len(candidates)):
        screened = candidates[place]
        key = _stat_key(target_key, keys[screened.parent]) if kept is not None else ""
        held = _kept_stat(kept, key) if kept is not None else None
        if held is not None:
            statistic, freedom = held
        else:
            if design is None or fits is None:
                design = _design(target, [], frames, rows)
                fits = _fits(target, design)
            curve = _curve_block(screened.parent, frames[screened.parent])
            if curve is not None:
                screened = Block(screened.terms + curve.terms, screened.parent, "screen")
            statistic, freedom = _block_statistic(target, fits, design, screened, frames, rows)
            if kept is not None:
                _keep_stat(kept, key, statistic, freedom)
        if freedom > 0 and statistic >= critical(freedom):
            ranked += [(-_standardised(statistic, freedom), place)]
    chosen: "list[Block]" = []
    for _negative, place in sorted(ranked)[:PARENT_CAP]:
        chosen += [candidates[place]]
    return chosen, design, fits


# THE EXTRAS OF A NUMBER GROWN, NOT REMADE (lane SPEED-2M). A number's
# response is fitted by least squares, whose weights are one on every row,
# and each step of `_refine` adds a block's columns at the end of its
# design: every column of the design before stays as it was, and so does
# every sum of products of it with an extra's terms, with the response, or
# with another column of the design. A step reads those sums from the step
# before (`Grown`) and makes the new ones alone; the Cholesky factor's
# leading part reads the same matrix, so the fit and every statistic are
# the as-built ones, bit for bit. Each sum is made by `_summed` (the rows
# that add, where a side is noughts off a list of rows).


@dataclasses.dataclass
class Grown:
    """The sums of one number target's steps (lane SPEED-2M), each made once: keyed by the design's column places."""

    design: "list[list[float]]"
    facts: "list[tuple[list[int] | None, bool, list[int] | None]]"
    gram: "dict[tuple[int, int], float]" = dataclasses.field(default_factory=dict)
    rhs: "dict[int, float]" = dataclasses.field(default_factory=dict)
    values: "dict[int, list[list[float]]]" = dataclasses.field(default_factory=dict)
    value_facts: "dict[int, list[tuple[list[int] | None, bool, list[int] | None]]]" = dataclasses.field(
        default_factory=dict)
    crossed: "dict[tuple[int, int, int], float]" = dataclasses.field(default_factory=dict)
    selves: "dict[tuple[int, int, int], float]" = dataclasses.field(default_factory=dict)
    # Whether the last fit's residuals are finite, read once a fit.
    residuals_finite: bool = True
    # How many values `values` holds (kept to `_GROWN_CELLS_MOST`).
    cells: int = 0


# A column is summed over its nonzero rows where these are at most this share of its rows.
_SPARSE_SHARE = 0.5
# The extras' values a target's steps keep at most (about 32 bytes a value as a list of floats: 256 MB); an extra
# past it is worked out again at each step, as before, its sums with the design still made once.
_GROWN_CELLS_MOST = 8_000_000


def _facts_of(column: "list[float]") -> "tuple[list[int] | None, bool, list[int] | None]":
    """A column's nonzero rows (None where more than `_SPARSE_SHARE` of its rows are), whether it is finite, and its
    rows holding a one where every other holds a nought (None for any other column); read once a column."""
    if not _finite(column):
        return None, False, None
    nonzero = [row for row, value in enumerate(column) if value != 0.0]
    ones = nonzero if all([column[row] == 1.0 for row in nonzero]) else None
    return (nonzero if len(nonzero) <= _SPARSE_SHARE * len(column) else None), True, ones


def _grown_sum(first: "list[float]", first_facts: "tuple[list[int] | None, bool, list[int] | None]", second: "list[float]", second_facts: "tuple[list[int] | None, bool, list[int] | None]") -> float:
    """`_dot(first, second)`, the same bits, summed over the rows that add.

    Each product is one rounding of the exact product, whichever side
    comes first; a product of a finite value with a nought is a nought,
    with a one the value itself; and `math.fsum` passes over a nought
    (+0.0 for a sum of noughts alone). So, both sides finite, the sum over
    one side's ones is that sum of the other side's values, and the sum
    over one side's nonzero rows is the sum over every row. Anything else
    is `_dot` as written.
    """
    first_rows, first_finite, first_ones = first_facts
    second_rows, second_finite, second_ones = second_facts
    if not first_finite or not second_finite:
        return _dot(first, second)
    if second_ones is not None and (first_ones is None or len(second_ones) <= len(first_ones)):
        return math.fsum([first[row] for row in second_ones])
    if first_ones is not None:
        return math.fsum([second[row] for row in first_ones])
    if first_rows is not None and (second_rows is None or len(first_rows) <= len(second_rows)):
        return math.fsum([first[row] * second[row] for row in first_rows])
    if second_rows is not None:
        return math.fsum([first[row] * second[row] for row in second_rows])
    return _dot(first, second)


def _grown_least_squares(grown: Grown, response: "list[float]") -> Fit:
    """`least_squares(grown.design, response)`, the same bits, each sum of a column pair and with the response made once."""
    columns = grown.design
    size = len(columns)
    rows = len(response)
    response_facts: "tuple[list[int] | None, bool, list[int] | None]" = (None, _finite(response), None)
    matrix = [[0.0 for _b in range(size)] for _a in range(size)]
    for a in range(size):
        for b in range(a + 1):
            if (a, b) not in grown.gram:
                grown.gram[(a, b)] = _grown_sum(columns[a], grown.facts[a], columns[b], grown.facts[b])
            value = grown.gram[(a, b)]
            matrix[a][b] = value
            matrix[b][a] = value
    lower, dropped = _cholesky(_ridged(matrix))
    for a in range(size):
        if not dropped[a] and a not in grown.rhs:
            grown.rhs[a] = _grown_sum(columns[a], grown.facts[a], response, response_facts)
    beta = _solve(lower, dropped, [0.0 if dropped[a] else grown.rhs[a] for a in range(size)])
    eta = _predictor(columns, beta, rows)
    residuals = [y - e for y, e in zip(response, eta)]
    kept = len([flag for flag in dropped if not flag])
    scale = math.fsum([r * r for r in residuals]) / max(1, rows - kept)
    grown.residuals_finite = _finite(residuals)
    return Fit(beta, [1.0 for _row in range(rows)], residuals, lower, dropped, max(scale, 1e-12))


def _grown_values(grown: Grown, target: Target, key: int, block: Block, frames: "dict[str, Frame]", rows: int
                  ) -> "tuple[list[list[float]], list[tuple[list[int] | None, bool, list[int] | None]]]":
    """A block's terms on the target's rows and their facts (`_evaluated` restricted as `_block_statistic` and
    `_design` do), kept for the next step while `_GROWN_CELLS_MOST` allows.

    ``key`` is the block's place among the target's extras, which the steps keep.
    """
    if key in grown.values:
        return grown.values[key], grown.value_facts[key]
    values = _evaluated(block, frames, rows, None)
    restricted = [[column[row] for row in target.rows] for column in values]
    facts = [_facts_of(column) for column in restricted]
    size = len(restricted) * len(target.rows)
    if grown.cells + size <= _GROWN_CELLS_MOST:
        grown.values[key] = restricted
        grown.value_facts[key] = facts
        grown.cells += size
    return restricted, facts


def _grown_statistic(grown: Grown, fit: Fit, target: Target, key: int, block: Block, frames: "dict[str, Frame]",
                     rows: int) -> "tuple[float, int]":
    """`_block_statistic` of a number target's extra block (`score_statistic` on its rows), the same bits.

    The fit is a least-squares fit, its weights one on every row, so the
    weighted block is the block (a value times one is that value) and its
    sums with a design column and with itself are the same at every step:
    each is made once.
    """
    block_values, facts = _grown_values(grown, target, key, block, frames, rows)
    width = len(block_values)
    if width == 0:
        return 0.0, 0
    columns = grown.design
    size = len(columns)
    residual_facts: "tuple[list[int] | None, bool, list[int] | None]" = (None, grown.residuals_finite, None)
    score = [_grown_sum(term, term_facts, fit.residuals, residual_facts) for term, term_facts in zip(block_values, facts)]
    cross: "list[list[float]]" = []
    for k in range(width):
        row_of: "list[float]" = []
        for a in range(size):
            if fit.dropped[a]:
                row_of += [0.0]
                continue
            if (key, k, a) not in grown.crossed:
                grown.crossed[(key, k, a)] = _grown_sum(block_values[k], facts[k], columns[a], grown.facts[a])
            row_of += [grown.crossed[(key, k, a)]]
        cross += [row_of]
    solved = [_solve(fit.lower, fit.dropped, cross[k]) for k in range(width)]
    variance = [[0.0 for _b in range(width)] for _a in range(width)]
    for k in range(width):
        for m in range(k + 1):
            if (key, k, m) not in grown.selves:
                grown.selves[(key, k, m)] = _grown_sum(block_values[k], facts[k], block_values[m], facts[m])
            value = grown.selves[(key, k, m)] - _dot(cross[k], solved[m])
            variance[k][m] = value
            variance[m][k] = value
    lower, dropped = _cholesky(variance)
    if all(dropped):
        return 0.0, width
    solved_score = _solve(lower, dropped, [0.0 if dropped[k] else score[k] for k in range(width)])
    statistic = _dot(score, solved_score) / fit.scale
    return (statistic if statistic > 0.0 else 0.0), width


def _refine_number(target: Target, chosen: "list[Block]", frames: "dict[str, Frame]",
                   rows: int) -> "tuple[list[Block], list[Fit | None]]":
    """`_refine` of a number target, the same blocks and fit bit for bit, its sums grown step by step (`Grown`)."""
    chosen = [block for block in chosen]
    grown = Grown([], [])
    for column in _design(target, chosen, frames, rows)[0]:
        grown.design += [column]
        grown.facts += [_facts_of(column)]
    fit = _grown_least_squares(grown, target.response)
    extras: "list[Block]" = []
    for block in chosen:
        curve = _curve_block(block.parent, frames[block.parent])
        if curve is not None:
            extras += [curve]
    for a in range(len(chosen)):
        for b in range(a + 1, len(chosen)):
            first, second = chosen[a], chosen[b]
            if frames[first.parent].kind == NUMBER and frames[second.parent].kind == LABEL:
                first, second = second, first
            joined = _interactions(first, second, frames)
            if joined is not None:
                extras += [joined]
    # Each extra's place among them as first made: the key of its sums while the steps go on.
    numbers = [place for place in range(len(extras))]
    for _step in range(EXTRA_CAP):
        best = -_INFINITY
        best_place = -1
        for place in range(len(extras)):
            statistic, freedom = _grown_statistic(grown, fit, target, numbers[place], extras[place], frames, rows)
            if freedom > 0 and statistic >= critical(freedom) and _standardised(statistic, freedom) > best:
                best = _standardised(statistic, freedom)
                best_place = place
        if best_place < 0:
            break
        taken = extras[best_place]
        number = numbers[best_place]
        chosen += [taken]
        extras = [extras[place] for place in range(len(extras)) if place != best_place]
        numbers = [numbers[place] for place in range(len(numbers)) if place != best_place]
        # ...the design grows by the block's columns at its end, as `_design` writes them.
        added, added_facts = _grown_values(grown, target, number, taken, frames, rows)
        for k in range(len(added)):
            grown.design += [added[k]]
            grown.facts += [added_facts[k]]
        fit = _grown_least_squares(grown, target.response)
    return chosen, [fit]


def _refine(target: Target, chosen: "list[Block]", frames: "dict[str, Frame]", rows: int,
            design: "list[list[list[float]]] | None",
            fits: "list[Fit | None] | None") -> "tuple[list[Block], list[Fit | None]]":
    """`select`'s last step: the fits on the parents ``chosen``, then the curves and interactions given them.

    ``design`` and ``fits`` are those of ``chosen`` where `_conditional`
    made them (None where it did not: they are then made here, the same
    values). A fixed function of the target and the chosen parents'
    frames; raises what `_fits` raises.
    """
    if target.kind == NUMBER:
        return _refine_number(target, chosen, frames, rows)
    chosen = [block for block in chosen]
    if design is None or fits is None:
        design = _design(target, chosen, frames, rows)
        fits = _fits(target, design)
    extras: "list[Block]" = []
    for block in chosen:
        curve = _curve_block(block.parent, frames[block.parent])
        if curve is not None:
            extras += [curve]
    if target.kind == LABEL and target.levels > EXTRA_LEVELS_CAP:
        return chosen, fits
    for a in range(len(chosen)):
        for b in range(a + 1, len(chosen)):
            first, second = chosen[a], chosen[b]
            if frames[first.parent].kind == NUMBER and frames[second.parent].kind == LABEL:
                first, second = second, first
            joined = _interactions(first, second, frames)
            if joined is not None:
                extras += [joined]
    for _step in range(EXTRA_CAP):
        best = -_INFINITY
        best_place = -1
        for place in range(len(extras)):
            statistic, freedom = _block_statistic(target, fits, design, extras[place], frames, rows)
            if freedom > 0 and statistic >= critical(freedom) and _standardised(statistic, freedom) > best:
                best = _standardised(statistic, freedom)
                best_place = place
        if best_place < 0:
            break
        chosen += [extras[best_place]]
        extras = [extras[place] for place in range(len(extras)) if place != best_place]
        design = _design(target, chosen, frames, rows)
        fits = _fits(target, design)
    return chosen, fits


def _residual_shape(fit: Fit) -> "list[float]":
    spread = math.sqrt(fit.scale)
    ordered = sorted(r / spread for r in fit.residuals)
    count = len(ordered)
    if count == 0:
        return [0.0 for _k in range(RESIDUAL_POINTS)]
    out: "list[float]" = []
    for k in range(RESIDUAL_POINTS):
        at = (2 * k + 1) * count / (2 * RESIDUAL_POINTS) - 0.5
        low = int(at) if at > 0.0 else 0
        high = min(count - 1, low + 1)
        frac = at - low if at > 0.0 else 0.0
        out += [ordered[low] + frac * (ordered[high] - ordered[low])]
    return out


def _terms_of(blocks: "list[Block]") -> "list[object]":
    terms: "list[object]" = [["one"]]
    for block in blocks:
        for term in block.terms:
            terms += [term]
    return terms


def _intercepts_only(codes: "list[int]", levels: int) -> "list[list[float] | None]":
    tallies = [0 for _level in range(levels)]
    for code in codes:
        tallies[code] += 1
    reference = max(1, tallies[0])
    out: "list[list[float] | None]" = [None]
    for level in range(1, levels):
        out += [[chain_walk.natural_log(tallies[level] / reference)] if tallies[level] > 0 else [-_ETA_CAP]]
    return out


def fit_label(target: Target, candidates: "list[Block]", frames: "dict[str, Frame]", rows: int,
              kept: "KeptFits | None" = None, target_key: str = "",
              keys: "dict[str, str] | None" = None) -> "dict[str, object]":
    """A label response's model: its terms and, for each non-reference level, its coefficients (intercept only where too rare).

    With ``kept`` (lane SPEED-2M), the screen's statistics and the model
    are taken where the fits kept from the last description of this table
    hold them under the same keys (``target_key`` the target's, ``keys``
    each candidate parent's), and made otherwise: the same model either way.
    """
    if kept is None or keys is None:
        chosen, fits = select(target, candidates, frames, rows)
        return _label_model(target, chosen, fits)
    picked, design, screen_fits = _screen(target, candidates, frames, rows, kept, target_key, keys)
    picked, design, screen_fits = _conditional(target, candidates, picked, frames, rows, design, screen_fits, kept,
                                               target_key, keys)
    key = _model_key(target_key, [keys[block.parent] for block in picked])
    held = _kept_model(kept, key)
    if held is not None:
        return held
    chosen, fits = _refine(target, picked, frames, rows, design, screen_fits)
    model = _label_model(target, chosen, fits)
    _keep_model(kept, key, model)
    return model


def _label_model(target: Target, chosen: "list[Block]", fits: "list[Fit | None]") -> "dict[str, object]":
    """A label response's model from its chosen blocks and its fits (`fit_label`'s last step)."""
    terms = _terms_of(chosen)
    fallback = _intercepts_only([target.codes[row] for row in target.rows], target.levels)
    coefficients: "list[object]" = [None]
    for level in range(1, target.levels):
        fit = fits[level - 1] if level - 1 < len(fits) else None
        if fit is None:
            only = fallback[level]
            coefficients += [[(only[0] if only is not None else -_ETA_CAP)] + [0.0 for _t in range(len(terms) - 1)]]
        else:
            coefficients += [[value for value in fit.beta]]
    return {"terms": terms, "coefficients": coefficients}


def person_split(residuals: "list[float]", owners: "list[int]") -> "tuple[float, float]":
    """The residual variance split into a person's share and a row's (one-way moments): the two spreads.

    Between persons `(MSB - MSW) / n0`, nought where negative; within,
    `MSW`; `n0 = (N - sum n_i ** 2 / N) / (k - 1)`. Where fewer than two
    persons or no person holds two rows, everything is within.
    """
    totals: "dict[int, list[float]]" = {}
    for residual, owner in zip(residuals, owners):
        if owner in totals:
            totals[owner] += [residual]
        else:
            totals[owner] = [residual]
    count = len(residuals)
    groups = len(totals)
    if groups < 2 or groups >= count:
        spread = math.sqrt(math.fsum([r * r for r in residuals]) / max(1, count))
        return 0.0, spread
    grand = math.fsum(residuals) / count
    means: "dict[int, float]" = {}
    for owner in totals:
        means[owner] = math.fsum(totals[owner]) / len(totals[owner])
    within = math.fsum([(r - means[owner]) * (r - means[owner]) for r, owner in zip(residuals, owners)]) / (count - groups)
    between = math.fsum([len(totals[owner]) * (means[owner] - grand) * (means[owner] - grand) for owner in totals]) / (groups - 1)
    squares = math.fsum([float(len(totals[owner]) * len(totals[owner])) for owner in totals])
    typical = (count - squares / count) / (groups - 1)
    share = (between - within) / typical if typical > 0.0 else 0.0
    return (math.sqrt(share) if share > 0.0 else 0.0), math.sqrt(max(within, 1e-12))


def fit_number(target: Target, candidates: "list[Block]", frames: "dict[str, Frame]", rows: int,
               owners: "list[int] | None" = None, kept: "KeptFits | None" = None, target_key: str = "",
               keys: "dict[str, str] | None" = None) -> "dict[str, object]":
    """A number response's model: its terms, coefficients, residual spread and residual shape.

    With `owners` (each fit row's person, where a person column repeats),
    the residual is split into a person's share and a row's
    (`person_split`), which the draw gives each twin person and each row.
    With ``kept`` (lane SPEED-2M), as `fit_label`: ``target_key`` names the
    target and whether `owners` is read, so a model made with them is never
    taken for one made without.
    """
    if kept is None or keys is None:
        chosen, fits = select(target, candidates, frames, rows)
        return _number_model(target, chosen, fits, owners)
    picked, design, screen_fits = _screen(target, candidates, frames, rows, kept, target_key, keys)
    picked, design, screen_fits = _conditional(target, candidates, picked, frames, rows, design, screen_fits, kept,
                                               target_key, keys)
    key = _model_key(target_key, [keys[block.parent] for block in picked])
    held = _kept_model(kept, key)
    if held is not None:
        return held
    chosen, fits = _refine(target, picked, frames, rows, design, screen_fits)
    model = _number_model(target, chosen, fits, owners)
    _keep_model(kept, key, model)
    return model


def _number_model(target: Target, chosen: "list[Block]", fits: "list[Fit | None]",
                  owners: "list[int] | None") -> "dict[str, object]":
    """A number response's model from its chosen blocks and its fit (`fit_number`'s last step)."""
    fit = fits[0]
    if fit is None:
        raise RelationsError("synthtwin internal check: a number's fit was not made.")
    model: "dict[str, object]" = {"terms": _terms_of(chosen), "coefficients": [value for value in fit.beta],
                                  "spread": math.sqrt(fit.scale), "residuals": _residual_shape(fit)}
    if owners is not None:
        between, within = person_split(fit.residuals, [owners[row] for row in target.rows])
        model["person_spread"] = between
        model["row_spread"] = within
    return model


# THE FITS KEPT BETWEEN ROUNDS (lane SPEED-2M). A person who answers the
# questions file describes the table again, and every round refitted the
# whole relations zone: about an hour a round at the fit's 200,000 rows,
# 2,300 seconds at 20,000 rows of 302 columns. Each round's screen
# statistics and models are now kept beside the record (`KeptFits`, written
# by the command in the private folder, never in the description), each
# under a digest of everything it was made from: a statistic under its
# target's key and its parent's, a model under its target's key and the
# keys of the parents its screen and the conditional pass chose, and the
# parents the conditional pass adds (lane STATS-B's, merged in batch 4zz)
# under its target's key and every candidate's, since it reads them all.
# A column's key digests its entry and its values on the fit's rows; a
# target's adds which fit it is, the fit's rows and persons
# (`_fits_base`). So a later round takes a fit only where every input is
# the same and makes the rest: the zone is the same bytes as a round that
# kept nothing. The keys are FNV-1a digests of the inputs' exact
# spellings (`repr` of each float, which reads back to the same
# binary64). Version 2: the conditional pass entered every model.
FITS_VERSION = 2


@dataclasses.dataclass
class KeptFits:
    """The fits of the last description of a table (``held_*``) and of this one (``made_*``), by their keys (lane SPEED-2M).

    ``taken`` counts the statistics and models found held, ``fitted`` those
    made. Plain values only: a statistic is ``[statistic, freedom]``, a
    model the dict a zone entry holds.
    """

    held_stats: "dict[str, list[object]]" = dataclasses.field(default_factory=dict)
    held_models: "dict[str, dict[str, object]]" = dataclasses.field(default_factory=dict)
    made_stats: "dict[str, list[object]]" = dataclasses.field(default_factory=dict)
    made_models: "dict[str, dict[str, object]]" = dataclasses.field(default_factory=dict)
    taken: int = 0
    fitted: int = 0


def _fnv_more(value: int, data: bytes) -> int:
    """FNV-1a's state after `data`, from the state `value` (whole numbers only)."""
    for byte in data:
        value = ((value ^ byte) * 1099511628211) & _MASK64
    return value


def _key_of_bytes(parts: "list[bytes]") -> str:
    """The FNV-1a digest of the parts, each after its length (so no two lists of parts read alike), as 16 hex figures."""
    value = 14695981039346656037
    for part in parts:
        if not isinstance(part, bytes):
            raise TypeError("synthtwin digests bytes only.")
        value = _fnv_more(value, bytes(f"{len(part)}:", "ascii"))
        value = _fnv_more(value, part)
    return f"{value:016x}"


def _key_of(parts: "list[str]") -> str:
    """`_key_of_bytes` of the parts' exact spellings."""
    return _key_of_bytes([bytes(f"{part}", "utf-8", "surrogatepass") for part in parts])


def _stat_key(target_key: str, parent_key: str) -> str:
    return _key_of(["stat", target_key, parent_key])


def _model_key(target_key: str, parent_keys: "list[str]") -> str:
    return _key_of(["model", target_key] + parent_keys)


def _kept_stat(kept: KeptFits, key: str) -> "tuple[float, int] | None":
    """A statistic held under ``key`` (this round's first, then the last round's), counted as taken; None where none is."""
    found = kept.made_stats[key] if key in kept.made_stats else (kept.held_stats[key] if key in kept.held_stats else None)
    if not isinstance(found, list) or len(found) != 2:
        return None
    statistic, freedom = found[0], found[1]
    if not isinstance(statistic, float) or not isinstance(freedom, int) or isinstance(freedom, bool):
        return None
    kept.made_stats[key] = [statistic, freedom]
    kept.taken += 1
    return statistic, freedom


def _keep_stat(kept: KeptFits, key: str, statistic: float, freedom: int) -> None:
    kept.made_stats[key] = [float(statistic), int(freedom)]
    kept.fitted += 1


def _kept_model(kept: KeptFits, key: str) -> "dict[str, object] | None":
    """A model held under ``key``, counted as taken; None where none is."""
    found = kept.made_models[key] if key in kept.made_models else (
        kept.held_models[key] if key in kept.held_models else None)
    if not isinstance(found, dict):
        return None
    kept.made_models[key] = found
    kept.taken += 1
    return found


def _keep_model(kept: KeptFits, key: str, model: "dict[str, object]") -> None:
    kept.made_models[key] = model
    kept.fitted += 1


def _fits_base(sample: int, owners: "list[int] | None") -> str:
    """The part of every key a fit shares: the versions, the fit's rows and each row's person."""
    return _key_of([f"{FITS_VERSION}", f"{ZONE_VERSION}", f"{sample}", repr(owners) if owners is not None else "-"])


def _column_key(base: str, column: Encoded) -> str:
    """A modelled column's key: its entry as encoded (before its fit) and its values on the fit's rows."""
    entry = column.entry
    listed = [(key, entry[key]) for key in sorted(entry)]
    top = 0
    for code in column.codes:
        if code > top:
            top = code
    codes = (b"b" + bytes(column.codes)) if top < 256 else (b"r" + bytes(repr(column.codes), "ascii"))
    return _key_of_bytes([bytes(base, "ascii"), bytes(repr(listed), "utf-8", "surrogatepass"), bytes(column.states),
                          bytes(repr(column.positions), "ascii"), codes])


def fit_zone(encoded: "list[Encoded]", sample: int, rows: int, owners: "list[int] | None" = None,
             person: str = "", frames_out: "dict[str, Frame] | None" = None,
             kept: "KeptFits | None" = None) -> "dict[str, object]":
    """The relations zone: each encoded column, in order, fitted on the columns before it (`sample` rows read).

    `owners` gives each fit row's person (None where every row is a
    person of its own; the fit rows hold each person's rows whole) and
    `person` names the person column: a column held once a person is
    fitted on each person's first row alone, on the columns before it
    that are held once a person too; a number varying by row splits its
    residual into a person's share and a row's; a sequence is fitted on
    nothing and read by the columns after it. Each number column's
    `positions` are emptied once its frame holds their scores (lane
    W5-302): `encoded` is the fit's own. `frames_out`, where given,
    gains every modelled column's frame on the fit's rows (the
    missing-values zone of lane IN-7 fits on them); the zone's bytes do
    not depend on it. ``kept`` (lane SPEED-2M), where given, holds the
    fits of the last description of this table and gains this one's: each
    statistic and model is taken from it where its key is held (the same
    value, for the key digests every input of it) and made otherwise, so
    the zone's bytes do not depend on it either.
    """
    first: "list[bool] | None" = None
    if owners is not None:
        seen: "dict[int, bool]" = {}
        first = []
        for owner in owners:
            first += [owner not in seen]
            seen[owner] = True
    frames: "dict[str, Frame]" = {}
    once: "set[str]" = set()
    columns: "list[object]" = []
    # Each parent's main block, made once as its frame is made (lane W5-302): a frame never changes once made, so
    # the block every later response screens is the one `_main_block` gives it, read once and not once a response.
    main_of: "dict[str, Block | None]" = {}
    # Each modelled column's key (lane SPEED-2M), made before its fit reads it: its frame is a fixed function of it.
    base = _fits_base(sample, owners) if kept is not None else ""
    keys: "dict[str, str]" = {}
    for column in encoded:
        entry = column.entry
        name = _text(entry["name"])
        level = _text(entry["level"]) if "level" in entry else ROW
        own = _column_key(base, column) if kept is not None else ""
        keys[name] = own
        if level == SEQUENCE:
            frames[name] = Frame(NUMBER, normal_scores(column.states, column.positions), column.states, [])
            main_of[name] = _main_block(name, frames[name])
            column.positions = []
            columns += [entry]
            continue
        held_once = level == PATIENT and first is not None
        candidates: "list[Block]" = []
        for parent in frames:
            if held_once and parent not in once:
                continue
            block = main_of[parent]
            if block is not None:
                candidates += [block]
        fitted = [row for row in range(sample) if first is None or not held_once or first[row]]
        # ...each target's key: its column's, which fit it is, and whether its rows are each person's first alone.
        held_word = "once" if held_once else "rows"
        kept_keys = keys if kept is not None else None
        if _text(entry["kind"]) == NUMBER:
            states = column.states
            presence = Target(LABEL, [], fitted, states, STATES)
            entry["presence"] = (fit_label(presence, candidates, frames, sample, kept,
                                           _key_of(["presence", held_word, own]), kept_keys)
                                 if len([row for row in fitted if states[row] != PRESENT]) >= MIN_ROWS else None)
            keep = [False for _row in range(sample)]
            for row in fitted:
                keep[row] = True
            masked = [states[row] if keep[row] else EMPTY for row in range(sample)]
            middle = normal_scores(masked, column.positions, (PRESENT,))
            present = [row for row in fitted if states[row] == PRESENT]
            value = Target(NUMBER, [middle[row] for row in present], present, [], 0)
            entry["value"] = fit_number(value, candidates, frames, sample, None if held_once else owners, kept,
                                        _key_of(["value", held_word, own]), kept_keys)
            frames[name] = Frame(NUMBER, normal_scores(states, column.positions), states, [])
            # ...and the column's numbers let go once its frame holds their scores (lane W5-302): nothing reads them
            # again, and a wide table held them all through its whole fit (8 bytes a row and a float each).
            column.positions = []
        else:
            levels = len(_list(entry["levels"])) + (1 if _int(entry["rest"]) > 0 else 0)
            target = Target(LABEL, [], fitted, column.codes, levels)
            entry["value"] = fit_label(target, candidates, frames, sample, kept, _key_of(["label", held_word, own]),
                                       kept_keys)
            frames[name] = Frame(LABEL, [], [], column.codes)
        main_of[name] = _main_block(name, frames[name])
        if held_once:
            once = once | set([name])
        columns += [entry]
    if frames_out is not None:
        for name in frames:
            frames_out[name] = frames[name]
    return {"version": ZONE_VERSION, "rows": rows, "sample_rows": sample, "person": person, "columns": columns}


# -- the twin drawn from the zone -------------------------------------------------------------------


def _uniform(word: int) -> float:
    """A share strictly between nought and one from a 64-bit word (its top 53 bits and a half)."""
    return ((word >> 11) + 0.5) / _TWO_53


def _residual(shape: "list[float]", share: float) -> float:
    at = share * RESIDUAL_POINTS - 0.5
    if at <= 0.0:
        return shape[0]
    if at >= RESIDUAL_POINTS - 1:
        return shape[RESIDUAL_POINTS - 1]
    low = int(at)
    return shape[low] + (at - low) * (shape[low + 1] - shape[low])


def _grid_value(grid: "list[float]", share: float) -> float:
    at = share * (GRID - 1)
    low = int(at)
    if low >= GRID - 1:
        return grid[GRID - 1]
    return grid[low] + (at - low) * (grid[low + 1] - grid[low])


def _written(value: float, places: int, top: int, form: "list[object] | None" = None) -> str:
    """A drawn number as the column writes it: its decimals (or its exponent's form), and above 89 the top code where one stands."""
    if top > 0 and value > top - 1:
        value = float(top)
    text = _with_exponent(value, form) if form is not None else f"{value:.{places}f}"
    if _starts(text, "-") and _number(text) == 0.0:
        text = text[1:]
    return text


def _exponent_of(entry: "dict[str, object]") -> "list[object] | None":
    """A number entry's exponent form (`encode_number`), checked, or None where the column writes fixed point."""
    found = entry["exponent"] if "exponent" in entry else None
    if found is None:
        return None
    form = _list(found)
    if (len(form) != 4 or not isinstance(form[0], int) or isinstance(form[0], bool) or form[1] not in ("e", "E")
            or not isinstance(form[2], bool) or not isinstance(form[3], int) or isinstance(form[3], bool)):
        raise RelationsError("The inside record's relations zone writes a number's exponent another way; describe the "
                             "table again.")
    return form


def _with_exponent(value: float, form: "list[object]") -> str:
    """A number in a column's exponent form: `1.234e-6` for its mantissa's three places, mark `e`, no plus, one figure."""
    places = _int(form[0])
    mark = _text(form[1])
    plus = form[2] is True
    width = _int(form[3])
    text = f"{value:.{places}e}"
    at = len(text) - 1
    while at > 0 and text[at] != "e":
        at -= 1
    power = int(text[at + 1:])
    figures = f"{abs(power)}"
    if len(figures) < width:
        figures = "0" * (width - len(figures)) + figures
    sign = "-" if power < 0 else ("+" if plus else "")
    return f"{text[:at]}{mark}{sign}{figures}"


def _censored_age(text: str, top: int) -> str:
    """A censoring spelling of a top-coded age column as the twin writes it (Safe Harbor binds the twin).

    One that names only ages past the top category (`>95`, `>=97`, `> 120`)
    is written as that category in the column's censored form, `>89`, as
    the description writes it; every other one stands (`>89`, `>=90` are
    the category itself, `<95` names no age past it).
    """
    for mark, last in ((">=", top), (">", top - 1)):
        if _starts(text, mark):
            value = _number(text[len(mark):])
            return f">{top - 1}" if value is not None and value > last else text
    return text


def _aged(text: str, places: int, top: int) -> str:
    """A drawn atom's or spike's cell under the column's top code: a number above 89 written as the top code, a censoring
    spelling past the top category written as it (`_censored_age`); every cell as it stands where no top code does."""
    if top <= 0:
        return text
    value = _number(text)
    if value is not None:
        return _written(value, places, top) if value > top - 1 else text
    return _censored_age(text, top) if _atom(text) is not None else text


# THE DRAW'S BLOCK OF ROWS (lane IN-8, plan P4-D502): a term's values and a
# predictor are made for this many rows at a time, from the parents' frames
# read back a block at a time (`frame_rows`), so what a column's draw holds
# beside its own cells is one block of its terms, not the table. Each row's
# arithmetic is the same in the same order, so the twin is the same bytes
# whatever the block (a gate case draws one twin with blocks of 7 rows).
DRAW_BLOCK = 65_536


def _block_frames(frames: "dict[str, Frame]", terms: "list[object]", start: int, stop: int) -> "dict[str, Frame]":
    """The frames the terms read, rows `start` to `stop`, as lists; RelationsError where a term reads no frame."""
    out: "dict[str, Frame]" = {}
    for term in terms:
        for name in _names_in(term):
            if name not in frames:
                raise RelationsError("The inside record's relations zone names a parent it does not model.")
            if name not in out:
                out[name] = frame_rows(frames[name], start, stop)
    return out


# A COLUMN'S DRAW WORDS (lane W5-2M): each column draws its `2 n` or `3 n` words at once; held as a list they
# were whole numbers of the interpreter's own and a pointer each, about 44 bytes a word (about 260 MB for one
# number column of 2,000,000 rows of several rows a person), and `draw_columns` now holds them as eight bytes
# each, little-endian, in one bytearray. Every reader takes a word through `_word`, which reads either form
# as the number drawn.
def _word(words: "list[int] | bytearray", at: int) -> int:
    """The ``at``-th word of a column's draw, held as a list or as eight bytes a word."""
    if isinstance(words, bytearray):
        place = 8 * at
        return (words[place] | (words[place + 1] << 8) | (words[place + 2] << 16) | (words[place + 3] << 24)
                | (words[place + 4] << 32) | (words[place + 5] << 40) | (words[place + 6] << 48)
                | (words[place + 7] << 56))
    return words[at]


def _word_count(words: "list[int] | bytearray") -> int:
    """How many words a column's draw holds."""
    return len(words) // 8 if isinstance(words, bytearray) else len(words)


def _draw_label(model: "dict[str, object]", frames: "dict[str, Frame]", rows: int, words: "list[int] | bytearray",
                levels: int, residuals: "list[float] | None" = None) -> "list[int]":
    """Each row's level by its fitted log odds; `residuals`, where given, gains each row's place inside its level's share (0 to 1)."""
    terms = _list(_get(model, "terms"))
    coefficients = _list(_get(model, "coefficients"))
    _block_frames(frames, terms, 0, 0)
    block = max(1, DRAW_BLOCK)
    codes: "list[int]" = []
    for start in range(0, rows, block):
        stop = min(rows, start + block)
        held = _block_frames(frames, terms, start, stop)
        columns = [term_values(term, held, stop - start) for term in terms]
        etas: "list[list[float]]" = [[0.0 for _row in range(stop - start)]]
        for level in range(1, levels):
            etas += [_predictor(columns, _floats(coefficients[level]), stop - start)]
        del columns
        for at in range(stop - start):
            top = max([etas[level][at] for level in range(levels)])
            lifted = [chain_walk.exponential(max(-700.0, etas[level][at] - top)) for level in range(levels)]
            total = math.fsum(lifted)
            share = _uniform(_word(words, start + at)) * total
            running = 0.0
            code = levels - 1
            for level in range(levels):
                running += lifted[level]
                if share < running:
                    code = level
                    break
            codes += [code]
            if residuals is not None:
                width = lifted[code]
                inside = (share - (running - width)) / width if width > 0.0 else 0.5
                residuals += [min(1.0 - 1e-12, max(0.0, inside))]
    return codes


def _etas(model: "dict[str, object]", frames: "dict[str, Frame]", rows: int, levels: int) -> "list[list[float]]":
    """Each level's fitted log odds against the first on every row (the first level's are nought).

    Made `DRAW_BLOCK` rows at a time from the parents' frames read back a
    block at a time (lane IN-8): each row's arithmetic is the same in the
    same order, so the log odds are the same whatever the block.
    """
    terms = _list(_get(model, "terms"))
    coefficients = _list(_get(model, "coefficients"))
    _block_frames(frames, terms, 0, 0)
    block = max(1, DRAW_BLOCK)
    etas: "list[list[float]]" = [[0.0 for _row in range(rows)]]
    for _level in range(1, levels):
        etas += [[]]
    for start in range(0, rows, block):
        stop = min(rows, start + block)
        held = _block_frames(frames, terms, start, stop)
        columns = [term_values(term, held, stop - start) for term in terms]
        for level in range(1, levels):
            etas[level] += _predictor(columns, _floats(coefficients[level]), stop - start)
        del columns
    return etas


def _codes_of(etas: "list[list[float]]", rows: int, words: "list[int] | bytearray") -> "list[int]":
    """Each row's level drawn by its log odds (`etas`) from its own word."""
    levels = len(etas)
    codes: "list[int]" = []
    for row in range(rows):
        top = max([etas[level][row] for level in range(levels)])
        lifted = [chain_walk.exponential(max(-700.0, etas[level][row] - top)) for level in range(levels)]
        total = math.fsum(lifted)
        share = _uniform(_word(words, row)) * total
        running = 0.0
        code = levels - 1
        for level in range(levels):
            running += lifted[level]
            if share < running:
                code = level
                break
        codes += [code]
    return codes


def _scores_drawn(model: "dict[str, object]", frames: "dict[str, Frame]", rows: int, present: "list[int]",
                  words: "list[int] | bytearray", owners: "list[int] | None" = None,
                  person_words: "list[int] | bytearray | None" = None, word_at: int = 0,
                  person_at: int = 0) -> "list[float]":
    """Each present row's drawn score: its fitted predictor and a residual, a person's share added where one was fitted.

    `present` is in rising order; the predictor is made a block of rows at a
    time. A row's residual word is `words[word_at + row]` and a person's
    share's `person_words[person_at + first row]`: the column's one list of
    words is read in place, never copied into slices (lane IN-8).
    """
    terms = _list(_get(model, "terms"))
    beta = _floats(_get(model, "coefficients"))
    spread = _float(_get(model, "spread"))
    shape = _floats(_get(model, "residuals"))
    _block_frames(frames, terms, 0, 0)
    block = max(1, DRAW_BLOCK)
    split = "person_spread" in model and owners is not None and person_words is not None
    between, scale = 0.0, 0.0
    if split:
        between = _float(model["person_spread"])
        within = _float(_get(model, "row_spread"))
        scale = within / spread if spread > 0.0 else 0.0
    out: "list[float]" = []
    at = 0
    for start in range(0, rows, block):
        stop = min(rows, start + block)
        end = at
        while end < len(present) and present[end] < stop:
            end += 1
        if end == at:
            continue
        held = _block_frames(frames, terms, start, stop)
        columns = [term_values(term, held, stop - start) for term in terms]
        eta = _predictor(columns, beta, stop - start)
        del columns
        if split and owners is not None and person_words is not None:
            out += [eta[row - start] + between * chain_walk.normal_score(_uniform(_word(person_words, person_at + owners[row])))
                    + scale * spread * _residual(shape, _uniform(_word(words, word_at + row))) for row in present[at:end]]
        else:
            out += [eta[row - start] + spread * _residual(shape, _uniform(_word(words, word_at + row))) for row in present[at:end]]
        at = end
    return out


@dataclasses.dataclass
class Drawn:
    """One modelled column of the twin: its cells (None where a cell is filled from the description's twin) and its frame."""

    cells: "list[str | None]"
    frame: Frame


def _owners(persons: "Persons | None", rows: int) -> "list[int]":
    """Each row's person's first row (each row its own where no person column repeats)."""
    if persons is None:
        return [row for row in range(rows)]
    first_of: "dict[int, int]" = {}
    for row in range(rows):
        if persons.first[row]:
            first_of[persons.person[row]] = row
    return [first_of[persons.person[row]] for row in range(rows)]


def draw_sequence(persons: "Persons | None", rows: int) -> Drawn:
    """A sequence column: each row's place among its person's rows, in row order (1, 2, 3...)."""
    places = [float(persons.sequence[row]) if persons is not None else 1.0 for row in range(rows)]
    states = [PRESENT for _row in range(rows)]
    cells: "list[str | None]" = [f"{int(place)}" for place in places]
    return Drawn(cells, Frame(NUMBER, normal_scores(states, places), states, []))


def draw_number(entry: "dict[str, object]", frames: "dict[str, Frame]", rows: int, words: "list[int] | bytearray",
                owners: "list[int] | None" = None, persons_of_rows: "list[int] | None" = None) -> Drawn:
    """A number column: its presence states (spikes among them), then its present rows' scores, mapped by rank onto its grid.

    `owners` (each row's person's first row) draws a column held once a
    person: each person's first row is drawn and its cell written on every
    row of the person.
    """
    presence = entry["presence"] if "presence" in entry else None
    counts = [_int(each) for each in _list(_get(entry, "states"))]
    if len(counts) != STATES:
        raise RelationsError("The inside record's relations zone counts a number's states another way; describe the table again.")
    if isinstance(presence, dict):
        states = _draw_label(_dict(presence), frames, rows, words, STATES)
    else:
        total = max(1, sum(counts))
        states = []
        for row in range(rows):
            share = _uniform(_word(words, row)) * total
            running = 0
            state = PRESENT
            for each in range(STATES):
                running += counts[each]
                if share < running:
                    state = each
                    break
            states += [state]
    if owners is not None:
        states = [states[owners[row]] for row in range(rows)]
    spikes = _list(_get(entry, "spikes"))
    if len(spikes) != 2:
        raise RelationsError("The inside record's relations zone holds a number's spikes another way; describe the table again.")
    present = [row for row in range(rows) if states[row] == PRESENT and (owners is None or owners[row] == row)]
    drawn = _scores_drawn(_dict(_get(entry, "value")), frames, rows, present, words,
                          persons_of_rows, words if _word_count(words) >= 3 * rows else None, rows, 2 * rows)
    order = sorted((drawn[k], present[k]) for k in range(len(present)))
    # What is dead is let go at once (lane IN-8): the scores and rows once in order, the order once mapped.
    del drawn, present
    grid = _floats(_get(entry, "grid"))
    places = _int(_get(entry, "decimals"))
    top = _int(_get(entry, "top"))
    form = _exponent_of(entry)
    atoms: "dict[float, str]" = {}
    for pair in _list(_get(entry, "atoms")):
        atoms[_float(_list(pair)[0])] = _text(_list(pair)[1])
    # A number written inside a wrapper is written back inside it (lane IN-7); a column without one keeps its bytes.
    worn = _list(entry["wrapper"]) if "wrapper" in entry else ["", ""]
    prefix, suffix = _text(worn[0]), _text(worn[1])
    cells: "list[str | None]" = [None for _row in range(rows)]
    positions = [0.0 for _row in range(rows)]
    count = len(order)
    for rank in range(count):
        row = order[rank][1]
        place = _grid_value(grid, (rank + 0.5) / count)
        if place in atoms:
            # A censoring atom keeps its spelling, under the age rule where the column is top-coded (`>95` is `>89`).
            cells[row] = _aged(atoms[place], places, top)
            positions[row] = place
            continue
        text = _written(place, places, top, form)
        cells[row] = prefix + text + suffix if prefix or suffix else text
        value = _number(text)
        positions[row] = value if value is not None else place
    del order
    for row in range(rows):
        if states[row] == EMPTY:
            cells[row] = ""
        elif states[row] in (LOW, HIGH):
            spike = spikes[0] if states[row] == LOW else spikes[1]
            # A spike the zone does not hold (its count nought, its odds e ** -35) writes its grid's end.
            end = grid[0] if states[row] == LOW else grid[GRID - 1]
            place = _float(_list(spike)[0]) if isinstance(spike, list) else end
            positions[row] = place
            spelled = (_text(_list(spike)[1]) if isinstance(spike, list)
                       else prefix + _written(end, places, top, form) + suffix)
            # ...a number above 89 written as the top code, a censoring spelling past the top category as it, and a
            # number inside the column's wrapper capped inside it (lane IN-7).
            inner = wrapped(spelled) if prefix or suffix else None
            if inner is not None:
                cells[row] = inner[0] + _aged(inner[1], places, top) + inner[2]
            else:
                cells[row] = _aged(spelled, places, top)
    if owners is not None:
        cells = [cells[owners[row]] for row in range(rows)]
        positions = [positions[owners[row]] for row in range(rows)]
    return Drawn(cells, Frame(NUMBER, normal_scores(states, positions), states, []))


def draw_label(entry: "dict[str, object]", frames: "dict[str, Frame]", rows: int, words: "list[int] | bytearray",
               allowed: "set[str]", owners: "list[int] | None" = None) -> Drawn:
    """A label column: each row's level by its fitted log odds; a level the description does not publish, and the rest, filled later.

    `owners` draws a column held once a person, as `draw_number` does.
    """
    levels = _list(_get(entry, "levels"))
    rest = _int(_get(entry, "rest"))
    count = len(levels) + (1 if rest > 0 else 0)
    # A carried label (lane IN-7) writes every modelled level as it is, and draws a rest row among the rest's real
    # spellings by their counts (the rows of the spellings it does not list are filled as before).
    carried = "carried" in entry and entry["carried"] is True
    others: "list[tuple[str, int]]" = []
    if carried and "others" in entry:
        for pair in _list(entry["others"]):
            others += [(_text(_list(pair)[0]), _int(_list(pair)[1]))]
    places: "list[float] | None" = [] if others else None
    codes = _draw_label(_dict(_get(entry, "value")), frames, rows, words, count, places)
    if owners is not None:
        codes = [codes[owners[row]] for row in range(rows)]
        if places is not None:
            places = [places[owners[row]] for row in range(rows)]
    cells: "list[str | None]" = []
    for row in range(len(codes)):
        code = codes[row]
        if code < len(levels):
            text = _text(levels[code])
            cells += [text if (carried or text in allowed or not _bare(text)) else None]
        elif places is not None:
            cells += [_other_of(others, rest, places[row])]
        else:
            cells += [None]
    return Drawn(cells, Frame(LABEL, [], [], codes))


def _other_of(others: "list[tuple[str, int]]", rest: int, share: float) -> "str | None":
    """A rest row's spelling: the listed spelling its place among the rest's rows falls on; None past them (filled as before)."""
    at = share * max(1, rest)
    running = 0
    for text, held in others:
        running += held
        if at < running:
            return text
    return None


def _filled(cells: "list[str | None]", pool: "list[str]") -> "list[str]":
    """The drawn cells with each unfilled one taken, in turn, from `pool` (the description's twin's own cells)."""
    out: "list[str]" = []
    taken = 0
    for cell in cells:
        if cell is not None:
            out += [cell]
            continue
        out += [pool[taken % len(pool)] if pool else ""]
        taken += 1
    return out


# -- THE DESCRIPTION'S WRITTEN FORMS KEPT (lane IN-2b): a drawn column dealt inside its own twin's cells ----------
#
# A drawn column is written with the description's twin's own cells for that column: every spelling, decimal
# place, sign, affix, missing-value spelling, label spelling and exact count the description publishes stands as
# that twin writes it, and the draw decides only WHICH ROW holds WHICH cell. The classes of cells (a number, its
# low or high spike, an empty cell, another word; a label's modelled spellings and the rest) are drawn with
# exactly the counts that twin holds (the draw's own result, the fewest rows moved where it holds other counts),
# a number's cells are dealt by the rank of the drawn scores, and a column held once a person deals whole
# persons' cells among persons of the same number of rows, so every count over rows stands too.

_FAR = -700.0
_LANE_RELEASE, _LANE_ORDER, _LANE_PICK, _LANE_TIE = 0, 1, 2, 3


def _salted(salt: int, row: int, lane: int) -> float:
    """A share strictly between nought and one: a fixed hash of a column's salt, a row's place and a lane."""
    return _uniform(_mix((salt + _mix((row << 3) + lane)) & _MASK64))


def _share_at(etas: "list[list[float]] | None", constant: "list[float]", row: int, kind: int) -> float:
    """A class's log odds at a row against the row's first class: its fitted predictor, or its constant share's log."""
    if etas is not None:
        return etas[kind][row] if kind < len(etas) else _FAR
    return constant[kind] if kind < len(constant) else _FAR


def _constant_shares(counts: "list[int]") -> "list[float]":
    """Each class's share, as a logarithm (a class the counts never hold weighs half a row)."""
    total = float(max(1, sum(counts)))
    return [chain_walk.natural_log(max(float(count), 0.5) / total) for count in counts]


def _settled(codes: "list[int]", members: "list[int]", targets: "list[int]", etas: "list[list[float]] | None",
             constant: "list[float]", salt: int) -> int:
    """Move the fewest of `members`' codes so each class holds exactly its target; the number of rows moved.

    A class holding more members than its target releases its surplus,
    drawn without replacement, each member weighted by how much likelier
    the under-filled classes are than its own at its row (Efraimidis and
    Spirakis' keys, in logarithms); each released member then takes an
    under-filled class with room, drawn by those classes' shares at its
    row. `targets` add up to the members. A fixed function of its inputs:
    the draws are hashes of `salt` and the row, no word of the stream.
    """
    classes = len(targets)
    by_class: "list[list[int]]" = [[] for _class in range(classes)]
    for row in members:
        by_class[codes[row]] += [row]
    surplus = [len(by_class[kind]) - targets[kind] for kind in range(classes)]
    under = [kind for kind in range(classes) if surplus[kind] < 0]
    if not under:
        return 0
    released: "list[int]" = []
    for kind in range(classes):
        if surplus[kind] <= 0:
            continue
        keyed: "list[tuple[float, int]]" = []
        for row in by_class[kind]:
            ups = [_share_at(etas, constant, row, other) for other in under]
            top = max(ups)
            gain = top + chain_walk.natural_log(math.fsum([chain_walk.exponential(max(_FAR, up - top)) for up in ups]))
            weight = min(-_FAR, max(_FAR, gain - _share_at(etas, constant, row, kind)))
            keyed += [(chain_walk.natural_log(_salted(salt, row, _LANE_RELEASE)) * chain_walk.exponential(-weight), row)]
        ranked = sorted(keyed, reverse=True)
        released += [row for _key, row in ranked[:surplus[kind]]]
    room = [-surplus[kind] if surplus[kind] < 0 else 0 for kind in range(classes)]
    for _share, row in sorted((_salted(salt, row, _LANE_ORDER), row) for row in released):
        open_classes = [kind for kind in under if room[kind] > 0]
        ups = [_share_at(etas, constant, row, kind) for kind in open_classes]
        top = max(ups)
        lifted = [chain_walk.exponential(max(_FAR, up - top)) for up in ups]
        pick = _salted(salt, row, _LANE_PICK) * math.fsum(lifted)
        chosen = open_classes[len(open_classes) - 1]
        running = 0.0
        for at in range(len(open_classes)):
            running += lifted[at]
            if pick < running:
                chosen = open_classes[at]
                break
        codes[row] = chosen
        room[chosen] -= 1
    return len(released)


def _number_class(cell: str, low: "float | None", high: "float | None",
                  wrapper: "tuple[str, str] | None" = None) -> "tuple[int, float]":
    """A number column's cell as the draw's states read it: its class (a number, a spike, empty, a word) and place.

    A number worn inside the column's wrapper (lane IN-7, `common_wrapper`) is read as its number.
    """
    bare = _bare(cell)
    if not bare:
        return EMPTY, 0.0
    place = _place_in(bare, wrapper)
    if place is None:
        return WORD, 0.0
    if low is not None and place == low:
        return LOW, place
    if high is not None and place == high:
        return HIGH, place
    return PRESENT, place


@dataclasses.dataclass
class Dealing:
    """How a drawn column's cells are dealt: row by row (`rows_of` None), or person by person where the column is held
    once a person (`rows_of` lists each person's rows in row order).

    `kept` names rows left as the description's twin holds them (its
    all-empty records).
    """

    rows: int
    kept: "list[bool] | None" = None
    rows_of: "list[list[int]] | None" = None


def _free_rows(dealing: Dealing) -> "list[int]":
    """The rows a row-by-row dealing deals: every row not kept."""
    kept = dealing.kept
    return [row for row in range(dealing.rows) if kept is None or not kept[row]]


def _free_persons(dealing: Dealing) -> "list[int]":
    """The persons a person-by-person dealing deals: every person whose first row is not kept."""
    kept = dealing.kept
    rows_of = dealing.rows_of if dealing.rows_of is not None else []
    return [person for person in range(len(rows_of)) if kept is None or not kept[rows_of[person][0]]]


def _hashed(units: "list[int]", lead: "list[int]", salt: int, lane: int) -> "list[int]":
    """Units in a fixed hashed order (each read at its row in `lead`)."""
    return [unit for _key, unit in sorted((_salted(salt, lead[at], lane), units[at]) for at in range(len(units)))]


def _put(bucket: "dict[int, list[int]]", size: int, person: int) -> None:
    """A person put on top of its size's pile."""
    if size in bucket:
        bucket[size] += [person]
    else:
        bucket[size] = [person]


def _taken(bucket: "dict[int, list[int]]", size: int) -> int:
    """The person on top of a size's pile, taken off it."""
    pile = bucket[size]
    person = pile[len(pile) - 1]
    del pile[len(pile) - 1]
    return person


def _persons_dealt_settled(codes: "list[int]", rows_of: "list[list[int]]", persons: "list[int]", kinds: "list[int]",
                           classes: int, etas: "list[list[float]] | None", constant: "list[float]", salt: int) -> None:
    """The person-by-person settle: where the description's twin holds the column one value a person, each number of
    rows keeps that twin's count of persons of each class (`_settled` on the persons of each size), so the counts
    over persons and over rows stand at once; elsewhere the counts over rows, by moving whole persons
    (`_person_settled`). `kinds` is each row's class in that twin; `codes` is read and written at first rows."""
    one_a_person = True
    for person in persons:
        rows = rows_of[person]
        first = kinds[rows[0]]
        for row in rows:
            if kinds[row] != first:
                one_a_person = False
                break
        if not one_a_person:
            break
    if not one_a_person:
        targets = [0 for _class in range(classes)]
        for person in persons:
            for row in rows_of[person]:
                targets[kinds[row]] += 1
        _person_settled(codes, rows_of, persons, targets, salt)
        return
    by_size: "dict[int, list[int]]" = {}
    for person in persons:
        size = len(rows_of[person])
        if size in by_size:
            by_size[size] += [person]
        else:
            by_size[size] = [person]
    for size in sorted(by_size):
        group = by_size[size]
        targets = [0 for _class in range(classes)]
        for person in group:
            targets[kinds[rows_of[person][0]]] += 1
        _settled(codes, [rows_of[person][0] for person in group], targets, etas, constant, salt)


def _person_settled(codes: "list[int]", rows_of: "list[list[int]]", persons: "list[int]", targets: "list[int]",
                    salt: int) -> int:
    """Move the fewest whole persons between classes so each class holds exactly `targets` rows; the persons moved.

    `codes` is read and written at each person's first row. Persons move
    in a fixed hashed order, the largest gap between a class of too many
    and one of too few first: the largest person that does not overshoot
    the gap, else an exchange of two persons whose sizes differ by it; a
    pair no move closes gives way to the next. Where no move closes any
    gap the rest is left (a table whose persons cannot make the count; the
    count is then off by under the largest person's rows).
    """
    classes = len(targets)
    held = [0 for _class in range(classes)]
    buckets: "list[dict[int, list[int]]]" = [{} for _class in range(classes)]
    for person in _hashed(persons, [rows_of[person][0] for person in persons], salt, _LANE_RELEASE):
        kind = codes[rows_of[person][0]]
        size = len(rows_of[person])
        held[kind] += size
        _put(buckets[kind], size, person)
    surplus = [held[kind] - targets[kind] for kind in range(classes)]
    moved = 0
    while True:
        over = sorted((-surplus[kind], kind) for kind in range(classes) if surplus[kind] > 0)
        under = sorted((surplus[kind], kind) for kind in range(classes) if surplus[kind] < 0)
        if not over or not under:
            return moved
        step = None
        # The largest gap first; a pair no move closes gives way to the next, so one class whose gap no person fits
        # leaves the others' gaps to close.
        for _over, fullest in over:
            for _under, emptiest in under:
                need = min(surplus[fullest], -surplus[emptiest])
                fits = [size for size in buckets[fullest] if size <= need and buckets[fullest][size]]
                if fits:
                    step = (fullest, emptiest, max(fits), 0)
                    break
                for size in sorted(buckets[fullest]):
                    back = size - need
                    if size > need and buckets[fullest][size] and back in buckets[emptiest] and buckets[emptiest][back]:
                        step = (fullest, emptiest, size, back)
                        break
                if step is not None:
                    break
            if step is not None:
                break
        if step is None:
            return moved
        fullest, emptiest, size, back = step
        going = _taken(buckets[fullest], size)
        _put(buckets[emptiest], size, going)
        codes[rows_of[going][0]] = emptiest
        surplus[fullest] -= size
        surplus[emptiest] += size
        moved += 1
        if back:
            coming = _taken(buckets[emptiest], back)
            _put(buckets[fullest], back, coming)
            codes[rows_of[coming][0]] = fullest
            surplus[fullest] += back
            surplus[emptiest] -= back
            moved += 1


def _persons_valued(entry: "dict[str, object]", cells: "list[str | None]", rows_of: "list[list[int]]",
                    persons: "list[int]", pool: "list[str]", wrapper: "tuple[str, str] | None" = None) -> None:
    """Each person drawn as a number, in the order of its drawn score, writes on all its rows the description's twin's
    cell in the middle of the block of that twin's sorted numbers (`pool`) its rows cover in turn: a quantile over
    persons WEIGHTED BY THEIR ROWS (batch 4x's outside review, item 4), so a person holds one value and the rows
    follow that twin's numbers -- its distribution over rows, its mean among them, stands as nearly as one value a
    person allows, however the persons' sizes go with their values -- and every value written is one of that twin's
    cells, its spelling, places and unit wrapper with it (item 3: a number worn inside the column's wrapper keeps it).
    A column written with an exponent writes that cell's number in its own exponent form, inside the wrapper where
    it wears one. Where that twin holds no number for the column, the zone's quantile function over persons is read
    as before (a censoring atom keeps its spelling, the top code holds)."""
    grid = _floats(_get(entry, "grid"))
    places = _int(_get(entry, "decimals"))
    top = _int(_get(entry, "top"))
    form = _exponent_of(entry)
    prefix, suffix = wrapper if wrapper is not None else ("", "")
    atoms: "dict[float, str]" = {}
    for pair in _list(_get(entry, "atoms")):
        atoms[_float(_list(pair)[0])] = _text(_list(pair)[1])
    count = len(persons)
    taken = 0
    for rank in range(count):
        person = persons[rank]
        size = len(rows_of[person])
        if pool:
            block = pool[min(len(pool) - 1, taken + (size - 1) // 2)]
            text = block
            value = _place_in(_bare(block), wrapper) if form is not None and _atom(block) is None else None
            if value is not None:
                text = prefix + _written(value, places, top, form) + suffix
        else:
            place = _grid_value(grid, (rank + 0.5) / count)
            if place in atoms:
                text = _aged(atoms[place], places, top)
            else:
                text = prefix + _written(place, places, top, form) + suffix
        for row in rows_of[person]:
            cells[row] = text
        taken += size


def _rows_valued(entry: "dict[str, object]", cells: "list[str | None]", rows: "list[int]") -> None:
    """Each row drawn as a number, in the order given (its drawn score's), takes its value from the zone's quantile
    function and writes it as `draw_number` does (a censoring atom keeps its spelling, the top code holds, an
    exponent column writes its own exponent form)."""
    grid = _floats(_get(entry, "grid"))
    places = _int(_get(entry, "decimals"))
    top = _int(_get(entry, "top"))
    form = _exponent_of(entry)
    atoms: "dict[float, str]" = {}
    for pair in _list(_get(entry, "atoms")):
        atoms[_float(_list(pair)[0])] = _text(_list(pair)[1])
    count = len(rows)
    for rank in range(count):
        place = _grid_value(grid, (rank + 0.5) / count)
        cells[rows[rank]] = _aged(atoms[place], places, top) if place in atoms else _written(place, places, top, form)


def _spellings_dealt(cells: "list[str | None]", rows_of: "list[list[int]]", persons: "list[int]",
                     pool: "list[str]", salt: int) -> None:
    """The persons of one class, each writing one spelling of that class on all its rows: first the cell at the head of
    the block of `pool` (that class's cells in the description's twin, in a fixed hashed order) its rows cover in
    turn, then the spellings' counts over rows settled by moving whole persons between them (`_person_settled`), so
    a class holding several spellings (the rest of a label, a number's words) keeps each spelling's count as nearly
    as whole persons allow."""
    if not persons or not pool:
        return
    spellings = sorted(set(pool))
    index: "dict[str, int]" = {}
    for at in range(len(spellings)):
        index[spellings[at]] = at
    targets = [0 for _spelling in spellings]
    for cell in pool:
        targets[index[cell]] += 1
    marks: "dict[int, int]" = {}
    taken = 0
    for person in persons:
        marks[rows_of[person][0]] = index[pool[min(len(pool) - 1, taken)]]
        taken += len(rows_of[person])
    if len(spellings) > 1:
        codes = [0 for _row in range(max(marks) + 1)]
        for row in marks:
            codes[row] = marks[row]
        _person_settled(codes, rows_of, persons, targets, salt)
        for row in marks:
            marks[row] = codes[row]
    for person in persons:
        text = spellings[marks[rows_of[person][0]]]
        for row in rows_of[person]:
            cells[row] = text


def _capped(text: str, places: int, top: int, wrapper: "tuple[str, str] | None" = None) -> str:
    """A cell of a top-coded column as the twin may write it: a number past the top code written as it, a censoring
    spelling past the top category written as that category (`_censored_age`); every other cell as it stands. A
    number worn inside the column's wrapper (lane IN-7) is capped inside it."""
    if top <= 0 or not _bare(text):
        return text
    if wrapper is not None:
        found = wrapped(text)
        if found is not None and (found[0], found[2]) == wrapper:
            inner = _capped(found[1], places, top)
            return text if inner == found[1] else found[0] + inner + found[2]
    value = _number(text)
    if value is not None:
        return _written(float(top), places, top) if value > top else text
    return _censored_age(text, top) if _atom(text) is not None else text


def _number_states(entry: "dict[str, object]", frames: "dict[str, Frame]", rows: int,
                   words: "list[int] | bytearray") -> "tuple[list[int], list[list[float]] | None, list[float]]":
    """A number column's presence states drawn as `draw_number` draws them, and the log odds they were drawn by."""
    counts = [_int(each) for each in _list(_get(entry, "states"))]
    if len(counts) != STATES:
        raise RelationsError("The inside record's relations zone counts a number's states another way; describe the table again.")
    presence = entry["presence"] if "presence" in entry else None
    if isinstance(presence, dict):
        etas = _etas(_dict(presence), frames, rows, STATES)
        return _codes_of(etas, rows, words), etas, []
    total = max(1, sum(counts))
    states: "list[int]" = []
    for row in range(rows):
        share = _uniform(_word(words, row)) * total
        running = 0
        state = PRESENT
        for each in range(STATES):
            running += counts[each]
            if share < running:
                state = each
                break
        states += [state]
    return states, None, _constant_shares(counts)


def redeal_number(entry: "dict[str, object]", frames: "dict[str, Frame]", words: "list[int] | bytearray", strict: "list[str]",
                  dealing: Dealing, persons_of_rows: "list[int] | None" = None) -> Drawn:
    """A number column drawn from the zone and written with the description's twin's own cells for it.

    ROW BY ROW: the presence states (a number, the low or high spike, an
    empty cell, a word) are drawn as `draw_number` draws them, then
    settled on the counts of those classes among the description's twin's
    cells (`_settled`); the rows drawn as numbers take that twin's numbers
    in the order of their drawn scores, every other row a cell of its
    class in a fixed hashed order: the column's cells ARE that twin's.
    PERSON BY PERSON (a column held once a person): the states are drawn
    at each person's first row and settled on those counts over rows by
    moving whole persons (`_person_settled`); the persons drawn as numbers
    take, in the order of their scores, the middle cell of the block of
    that twin's sorted numbers their rows cover, so each person holds one
    value and the rows follow that twin's numbers. A top-coded column
    keeps its top code on every cell.
    """
    rows = dealing.rows
    top = _int(_get(entry, "top"))
    places = _int(_get(entry, "decimals"))
    spikes = _list(_get(entry, "spikes"))
    if len(spikes) != 2:
        raise RelationsError("The inside record's relations zone holds a number's spikes another way; describe the table again.")
    if len(strict) != rows:
        raise RelationsError("The description's twin holds another number of rows than the inside record draws.")
    low = _float(_list(spikes[0])[0]) if isinstance(spikes[0], list) else None
    high = _float(_list(spikes[1])[0]) if isinstance(spikes[1], list) else None
    # A number column worn inside one common wrapper (lane IN-7) is read and capped inside it, so its numbers are
    # dealt by their drawn scores as a bare column's are.
    worn = _list(entry["wrapper"]) if "wrapper" in entry else None
    wrapper = (_text(worn[0]), _text(worn[1])) if worn is not None and len(worn) == 2 else None
    kinds: "list[int]" = []
    spots: "list[float]" = []
    for cell in strict:
        kind, spot = _number_class(_capped(cell, places, top, wrapper), low, high, wrapper)
        kinds += [kind]
        spots += [spot]
    states, etas, constant = _number_states(entry, frames, rows, words)
    salt = _word(words, 0) if _word_count(words) else 0
    cells: "list[str | None]" = [None for _row in range(rows)]
    rows_of = dealing.rows_of
    if rows_of is None:
        free = _free_rows(dealing)
        targets = [0 for _class in range(STATES)]
        for row in free:
            targets[kinds[row]] += 1
        _settled(states, free, targets, etas, constant, salt)
        etas = None
        lead = [row for row in free if states[row] == PRESENT]
    else:
        free = _free_persons(dealing)
        _persons_dealt_settled(states, rows_of, free, kinds, STATES, etas, constant, salt)
        etas = None
        lead = [rows_of[person][0] for person in free if states[rows_of[person][0]] == PRESENT]
    drawn = _scores_drawn(_dict(_get(entry, "value")), frames, rows, lead, words,
                          persons_of_rows, words if _word_count(words) >= 3 * rows else None, rows, 2 * rows)
    order = [row for _score, row in sorted((drawn[at], lead[at]) for at in range(len(lead)))]
    del drawn, lead
    if rows_of is None:
        givers: "list[list[int]]" = [[] for _class in range(STATES)]
        takers: "list[list[int]]" = [[] for _class in range(STATES)]
        for row in free:
            givers[kinds[row]] += [row]
            takers[states[row]] += [row]
        takers[PRESENT] = order
        for kind in range(STATES):
            if kind == PRESENT and _exponent_of(entry) is not None:
                # A column written with an exponent: the description's twin does not write that form, so its numbers
                # are the zone's, in the column's own exponent form (the classes' counts stand as dealt).
                _rows_valued(entry, cells, takers[kind])
                continue
            if kind == PRESENT:
                ranked = [row for _spot, _tie, row in sorted((spots[row], _salted(salt, row, _LANE_TIE), row)
                                                             for row in givers[kind])]
            else:
                ranked = _hashed(givers[kind], givers[kind], salt, _LANE_TIE + 1 + kind)
            for at in range(len(takers[kind])):
                cells[takers[kind][at]] = strict[ranked[at]]
    else:
        pools: "list[list[int]]" = [[] for _class in range(STATES)]
        for person in free:
            for row in rows_of[person]:
                pools[kinds[row]] += [row]
        by_state: "list[list[int]]" = [[] for _class in range(STATES)]
        for person in free:
            by_state[states[rows_of[person][0]]] += [person]
        firsts: "dict[int, int]" = {}
        for person in free:
            firsts[rows_of[person][0]] = person
        by_state[PRESENT] = [firsts[row] for row in order]
        for kind in range(STATES):
            if kind == PRESENT:
                pool = [strict[row] for _spot, _tie, row in sorted((spots[row], _salted(salt, row, _LANE_TIE), row)
                                                                   for row in pools[kind])]
                _persons_valued(entry, cells, rows_of, by_state[kind], pool, wrapper)
            else:
                pool = [strict[row] for row in _hashed(pools[kind], pools[kind], salt, _LANE_TIE + 1 + kind)]
                persons = by_state[kind]
                _spellings_dealt(cells, rows_of, _hashed(persons, [rows_of[person][0] for person in persons], salt,
                                                         _LANE_ORDER), pool, salt)
    del order, kinds, spots, states
    written = [_capped(cell if cell is not None else strict[row], places, top, wrapper) for row, cell in enumerate(cells)]
    del cells
    final: "list[int]" = []
    positions: "list[float]" = []
    for text in written:
        kind, spot = _number_class(text, low, high, wrapper)
        final += [kind]
        positions += [spot]
    return Drawn([text for text in written], Frame(NUMBER, normal_scores(final, positions), final, []))


def redeal_label(entry: "dict[str, object]", frames: "dict[str, Frame]", words: "list[int] | bytearray", strict: "list[str]",
                 dealing: Dealing) -> Drawn:
    """A label column drawn from the zone and written with the description's twin's own cells for it.

    Each row's level is drawn by its fitted log odds as `draw_label` draws
    it, then the levels are settled on the counts of the zone's modelled
    spellings and of the rest among the description's twin's cells
    (`_settled`), and each row takes a cell of its class in a fixed hashed
    order: the column's cells ARE that twin's. A column held once a person
    draws at each person's first row and settles by moving whole persons
    (`_person_settled`); a person of a modelled spelling writes it on all
    its rows, one of the rest a cell of the rest, so the modelled
    spellings' counts over rows stand exactly.
    """
    rows = dealing.rows
    if len(strict) != rows:
        raise RelationsError("The description's twin holds another number of rows than the inside record draws.")
    levels = [_text(each) for each in _list(_get(entry, "levels"))]
    modelled = len(levels) + (1 if _int(_get(entry, "rest")) > 0 else 0)
    rest = len(levels)
    code_of: "dict[str, int]" = {}
    for code in range(len(levels)):
        code_of[levels[code]] = code
    kinds = [code_of[cell] if cell in code_of else rest for cell in strict]
    etas = _etas(_dict(_get(entry, "value")), frames, rows, modelled)
    codes = _codes_of(etas, rows, words)
    salt = _word(words, 0) if _word_count(words) else 0
    cells: "list[str | None]" = [None for _row in range(rows)]
    rows_of = dealing.rows_of
    targets = [0 for _class in range(rest + 1)]
    if rows_of is None:
        free = _free_rows(dealing)
        for row in free:
            targets[kinds[row]] += 1
        _settled(codes, free, targets, etas, [], salt)
        del etas
        givers: "list[list[int]]" = [[] for _class in range(rest + 1)]
        takers: "list[list[int]]" = [[] for _class in range(rest + 1)]
        for row in free:
            givers[kinds[row]] += [row]
            takers[codes[row]] += [row]
        for kind in range(rest + 1):
            ranked = _hashed(givers[kind], givers[kind], salt, _LANE_TIE)
            for at in range(len(takers[kind])):
                cells[takers[kind][at]] = strict[ranked[at]]
    else:
        free = _free_persons(dealing)
        pools: "list[list[int]]" = [[] for _class in range(rest + 1)]
        for person in free:
            for row in rows_of[person]:
                pools[kinds[row]] += [row]
        _persons_dealt_settled(codes, rows_of, free, kinds, rest + 1, etas, [], salt)
        del etas
        by_code: "list[list[int]]" = [[] for _class in range(rest + 1)]
        for person in _hashed(free, [rows_of[person][0] for person in free], salt, _LANE_ORDER):
            by_code[codes[rows_of[person][0]]] += [person]
        for kind in range(rest + 1):
            pool = [strict[row] for row in _hashed(pools[kind], pools[kind], salt, _LANE_TIE)]
            _spellings_dealt(cells, rows_of, by_code[kind], pool, salt)
    del codes, kinds
    written = [cell if cell is not None else strict[row] for row, cell in enumerate(cells)]
    del cells
    final = [code_of[cell] if cell in code_of else rest for cell in written]
    return Drawn([text for text in written], Frame(LABEL, [], [], final))


def zone_of(record: object) -> "dict[str, object]":
    """The relations zone of a loaded inside record, checked for its version."""
    zone = _dict(_get(_get(record, "zones"), ZONE))
    if _int(_get(zone, "version")) != ZONE_VERSION:
        raise RelationsError("The inside record's relations zone is of another version; describe the table again.")
    return zone


def modelled_names(zone: "dict[str, object]") -> "list[str]":
    """The columns a zone draws, in its order."""
    return [_text(_get(entry, "name")) for entry in _list(_get(zone, "columns"))]


def person_of(zone: "dict[str, object]") -> str:
    """The person column a zone reads the twin's persons from ('' where every row is a person of its own)."""
    return _text(zone["person"]) if "person" in zone else ""


def published_spellings(column: contract.ColumnBlock) -> "set[str]":
    """Every spelling a loaded description publishes for a label column: its levels' variants."""
    facts = column.facts
    found: "list[str]" = []
    if isinstance(facts, contract.LabelFacts):
        for level in facts.levels:
            for spelling in level.variants:
                found += [spelling]
    return set(found)


def _names_in(term: object) -> "list[str]":
    """The columns a term reads."""
    parts = _list(term)
    head = _text(parts[0])
    if head == "one":
        return []
    if head == "prod":
        return _names_in(parts[1]) + _names_in(parts[2])
    return [_text(parts[1])]


def _last_reads(columns: "list[object]") -> "dict[str, int]":
    """For each column a later fit reads, the place of the last column whose fit reads it."""
    last: "dict[str, int]" = {}
    for place in range(len(columns)):
        entry = _dict(columns[place])
        for key in ("value", "presence"):
            model = entry[key] if key in entry else None
            if isinstance(model, dict) and "terms" in model:
                for term in _list(model["terms"]):
                    for name in _names_in(term):
                        last[name] = place
    return last


def draw_columns(zone: "dict[str, object]", profile: contract.Profile, held: "dict[str, twinstore.HeldColumn]",
                 seed: int, keep: "frozenset[str] | set[str]" = frozenset(),
                 frames_out: "dict[str, Frame] | None" = None,
                 kept: "list[bool] | None" = None) -> "dict[str, twinstore.HeldColumn]":
    """Every modelled column of a twin of `profile.n_rows` rows, drawn from the zone and the seed, each held at once.

    Guarantees: a fixed function of the zone, the description, the
    description's twin's held columns of the modelled columns and of the
    person column the zone names (`held`: each drawn column is WRITTEN WITH
    ITS OWN CELLS there, `redeal_number` and `redeal_label`, and the person
    column names the twin's persons), the rows `kept` as that twin holds
    them (its all-empty records) and the seed. Each column draws exactly
    `2 n` words (a number: its presence, then its scores; `3 n` where
    persons repeat and it varies by row: a person's share read at each
    person's first row), `n` (a label) or none (a sequence), in the zone's
    order. A column held once a person is drawn on each twin person's
    first row and deals whole persons' cells among persons of one number of
    rows; a sequence is each row's place among its person's rows. So every
    cell of a drawn column is a cell of the same column of the description's
    twin, and every spelling and count over rows that twin holds stands
    (a sequence aside). THE MEMORY: one column of the description's twin is
    read back at a time, each drawn column is held compactly
    (`twinstore.held_column`) as soon as it is drawn, a column's terms and
    predictors are made `DRAW_BLOCK` rows at a time (lane IN-8), and a
    column's scores, states or codes are held compactly (`held_frame`:
    bytes a row, not Python objects) until the last fit that reads them,
    then let go, except the columns `keep` names (the missing-values zone's
    parents, lane IN-7), whose frames `frames_out` gains once every column
    is drawn. Raises RelationsError
    where the zone does not fit the description (another number of rows,
    a column it does not hold).
    """
    rows = profile.n_rows
    if _int(_get(zone, "rows")) != rows:
        raise RelationsError("The inside record was written for a table of another size than this description's.")
    blocks: "dict[str, contract.ColumnBlock]" = {}
    for column in profile.columns:
        blocks[column.name] = column
    person = _text(_get(zone, "person")) if "person" in zone else ""
    persons: "Persons | None" = None
    if person:
        if person not in held:
            raise RelationsError("The inside record's relations zone names a person column this description does not hold.")
        persons = persons_of(twinstore.column_cells(held[person]))
    owners = _owners(persons, rows)
    # THE DEALING (lane IN-2b): every drawn column is written with the description's twin's own cells for it; a
    # column held once a person deals whole persons among persons of one number of rows; the twin's all-empty
    # records (`kept`) stay as that twin holds them.
    by_row = Dealing(rows, kept)
    by_person = by_row
    if persons is not None and persons.repeats:
        rows_of: "list[list[int]]" = [[] for _person in range(len(persons.rows_of))]
        for row in range(rows):
            rows_of[persons.person[row]] += [row]
        by_person = Dealing(rows, kept, rows_of)
    entries = _list(_get(zone, "columns"))
    last = _last_reads(entries)
    frames: "dict[str, Frame]" = {}
    out: "dict[str, twinstore.HeldColumn]" = {}
    generator = numpy.random.default_rng(seed)
    for place in range(len(entries)):
        entry = _dict(entries[place])
        name = _text(_get(entry, "name"))
        if name not in blocks or name not in held:
            raise RelationsError("The inside record's relations zone names a column this description does not hold.")
        kind = _text(_get(entry, "kind"))
        level = _text(entry["level"]) if "level" in entry else ROW
        if level == SEQUENCE:
            drawn = draw_sequence(persons, rows)
            out[name] = twinstore.held_column(_filled(drawn.cells, []))
        else:
            held_once = level == PATIENT and persons is not None
            split = persons is not None and not held_once and kind == NUMBER
            need = (3 * rows if split else 2 * rows) if kind == NUMBER else rows
            words = bytearray(8 * need) if need > 0 else bytearray()
            if need > 0:
                byte_at = 0
                for word in generator.integers(0, _WORD_CEILING, size=int(need), dtype="uint64", endpoint=True):
                    value = int(word)
                    for shift in range(0, 64, 8):
                        words[byte_at] = (value >> shift) & 255
                        byte_at += 1
            # ...and the description's twin's cells for the column read back each value once (lane W5-2M): a
            # pointer a row, not a text object a row, while the column is drawn.
            strict = _cells_once(twinstore.column_cells(held[name]))
            dealing = by_person if held_once else by_row
            if not _holds_a_cell(strict):
                # A COLUMN THE DESCRIPTION PUBLISHES NOTHING OF (lane W5-PL): the patient layer empties the block of a
                # repeated column no row family carries (contract 4.6c.5, S30), so the description's twin writes it
                # blank on every row and there is no written form to keep; the zone's own writer draws it from the
                # record's model, every modelled level written as the record holds it, rather than a blank column
                # (two of the battery's orders table's eight columns, every analysis of a dose or an action stopped).
                if kind == NUMBER:
                    drawn = draw_number(entry, frames, rows, words, owners if held_once else None,
                                        owners if split else None)
                else:
                    allowed: "set[str]" = set()
                    for modelled in _list(_get(entry, "levels")):
                        allowed = allowed | {_text(modelled)}
                    drawn = draw_label(entry, frames, rows, words, allowed, owners if held_once else None)
            elif kind == NUMBER:
                drawn = redeal_number(entry, frames, words, strict, dealing, owners if split else None)
            else:
                drawn = redeal_label(entry, frames, words, strict, dealing)
            del strict
            del words
            out[name] = twinstore.held_column(_filled(drawn.cells, []))
            drawn.cells = []
        if (name in last and last[name] > place) or name in keep:
            # A frame later columns read is held compactly until its last reader (lane IN-8, plan P4-D502); the
            # missing-values zone's parents (lane IN-7) are held to the end.
            frames[name] = held_frame(drawn.frame, rows)
        for gone in [each for each in frames if each not in keep and last[each] <= place]:
            del frames[gone]
    if frames_out is not None:
        for name in frames:
            if name in keep:
                # Given back as the lists a term reads (`term_values` reads no held frame).
                frames_out[name] = frame_rows(frames[name], 0, rows)
    return out


def _cells_once(cells: "list[str]") -> "list[str]":
    """The same cells, each different text one object (lane W5-2M). A fixed function of the cells."""
    first: "dict[str, str]" = {}
    out: "list[str]" = []
    for cell in cells:
        if cell not in first:
            first[cell] = cell
        out += [first[cell]]
    return out


def _holds_a_cell(cells: "list[str]") -> bool:
    """Whether any cell holds more than blanks (lane W5-PL). Raises nothing."""
    for cell in cells:
        if _bare(cell):
            return True
    return False


def held_cells(column: twinstore.HeldColumn) -> "list[str]":
    """A held column's cells (the description's twin), as a list."""
    return twinstore.column_cells(column)


# -- the fitting helpers another zone fits with (lane W5-F14's links zone) -------------------------------------------


def predictor(columns: "list[list[float]]", beta: "list[float]", rows: int) -> "list[float]":
    """The linear predictor of ``columns`` at ``beta`` over ``rows`` rows, the terms added in their order."""
    return _predictor(columns, beta, rows)


def information(columns: "list[list[float]]", weights: "list[float]") -> "tuple[list[list[float]], list[bool]]":
    """The ridged weighted information's lower factor and its dropped terms (a pivot under `_PIVOT` of its diagonal)."""
    return _cholesky(_ridged(_gram(columns, weights)))


def solved(lower: "list[list[float]]", dropped: "list[bool]", rhs: "list[float]") -> "list[float]":
    """The system of a lower factor solved for ``rhs``, a dropped term at nought."""
    return _solve(lower, dropped, rhs)


def dot(first: "list[float]", second: "list[float]") -> float:
    """The sum of the products, by `math.fsum`."""
    return _dot(first, second)


def mixed(value: int) -> int:
    """SplitMix64's finaliser of a whole number (`_mix`)."""
    return _mix(value)


def share_of(word: int) -> float:
    """A share strictly between nought and one from a 64-bit word (`_uniform`)."""
    return _uniform(word)


# -- THE IDENTITIES (lane STATS-B): one record-number column equal to another on the rows of some levels -------------
#
# WHAT IT CARRIES. Two columns the description holds as record numbers (made up in the twin, never a real one) can
# be one number on some rows of the real table: a policy's subscriber IS the patient exactly where the relationship
# is `Self`. Made up apart, the twin's two columns never met (the battery's accounts table: `self_subscriber_is_the_
# patient` 1.0 real, 0.0 twin, 0 of 9 runs). An IDENTITY is that rule as a model: the column, the one it equals,
# and the levels of one label column on whose rows it does -- every one of them on the fit's rows, and none of the
# other levels' rows -- or, where it holds on every row both hold a number, no label at all. No value: column names
# and the label's level spellings (the relations zone's own). HOW THE TWIN READS IT (`identities_held`, after every
# zone): on those rows the column is written as the other column's twin cell, a made-up number already, so the
# twin's cells stay made up and its two columns meet exactly where the real table's do.

IDENTITIES = "identities"
IDENTITY_LEAST_ROWS = 50
IDENTITY_LEVELS_MOST = 30


def identities_of(numbers: "dict[str, list[str]]", labels: "dict[str, list[str]]",
                  kept: "tuple[str, ...]" = ()) -> "list[dict[str, object]]":
    """The identities between the record-number columns `numbers` (their cells on the fit's rows, in the table's
    order), each by the label column of `labels` (cells on the same rows) whose levels part its rows exactly.

    A pair is an identity where its two cells are one text (both written) on at least `IDENTITY_LEAST_ROWS` rows,
    and either on every row where both are written (no label) or, for one label of at most
    `IDENTITY_LEVELS_MOST` levels, on every row of some of its levels and on none of the others'. The column the
    twin writes is the later of the two, unless it is one of `kept` (the column naming the person, which the twin
    never writes from another): then the earlier, and a pair of two kept columns is none. Each column equals at most
    one other. Deterministic. Raises nothing of its own.
    """
    names = [name for name in numbers]
    out: "list[dict[str, object]]" = []
    taken: "set[str]" = set()
    pairs: "list[tuple[str, str]]" = []
    for later in range(len(names)):
        for earlier in range(later):
            first, second = names[earlier], names[later]
            if second not in kept:
                pairs += [(second, first)]
            elif first not in kept:
                pairs += [(first, second)]
    for column, other in pairs:
        if column in taken or other in taken:
            continue
        own, theirs = numbers[column], numbers[other]
        both: "list[int]" = []
        equal: "list[bool]" = []
        for row in range(min(len(own), len(theirs))):
            if _bare(own[row]) and _bare(theirs[row]):
                both += [row]
                equal += [_bare(own[row]) == _bare(theirs[row])]
        met = sum(1 for each in equal if each)
        if met < IDENTITY_LEAST_ROWS:
            continue
        if met == len(both):
            out += [{"column": column, "equals": other, "by": "", "levels": []}]
            taken = taken | {column}
            continue
        found: "dict[str, object] | None" = None
        for label in labels:
            if label in (column, other):
                continue
            cells = labels[label]
            seen: "dict[str, list[int]]" = {}
            for at in range(len(both)):
                level = _bare(cells[both[at]]) if both[at] < len(cells) else ""
                if level not in seen:
                    seen[level] = [0, 0]
                seen[level][0] += 1
                seen[level][1] += 1 if equal[at] else 0
            if len(seen) > IDENTITY_LEVELS_MOST or len(seen) < 2:
                continue
            if all(seen[level][1] == 0 or seen[level][1] == seen[level][0] for level in seen):
                levels = sorted(level for level in seen if seen[level][1] > 0)
                if levels:
                    found = {"column": column, "equals": other, "by": label, "levels": levels}
                    break
        if found is not None:
            out += [found]
            taken = taken | {column}
    return out


def identities_held(rules: object, cells: "dict[str, list[str]]") -> "dict[str, list[str]]":
    """Each identity's column written as its other column's cell on the rows of its levels (every row both are
    written, where it names no label); only the columns that change. A rule naming a column `cells` does not hold is
    left out. Same rules and cells, same columns. Raises RelationsError on a damaged rule."""
    out: "dict[str, list[str]]" = {}
    for rule in _list(rules):
        entry = _dict(rule)
        column, other, label = _text(entry["column"]), _text(entry["equals"]), _text(entry["by"])
        levels = {_text(level) for level in _list(entry["levels"])}
        if column not in cells or other not in cells or (label and label not in cells):
            continue
        own = out[column] if column in out else cells[column]
        theirs = out[other] if other in out else cells[other]
        written = list(own)
        changed = False
        for row in range(min(len(own), len(theirs))):
            if label:
                if _bare(cells[label][row]) not in levels or not _bare(theirs[row]):
                    continue
            elif not (_bare(own[row]) and _bare(theirs[row])):
                continue
            if written[row] != theirs[row]:
                written[row] = theirs[row]
                changed = True
        if changed:
            out[column] = written
    return out
