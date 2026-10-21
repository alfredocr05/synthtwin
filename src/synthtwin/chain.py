"""The chain's profile side: scales, family tables and the keyed draw (contract 4.6b; lane CHa, plan P4-D418).

NOT IN FORCE. Invariant S12 stands until the landing that ships stage 6
whole (contract 4.6b's opening): no shipped description carries a fact
between two columns. Everything here runs only where a caller hands
`describe` a `ChainSwitch`, which `synthtwin profile` never does; the
switch is a parameter of the profile entry point and of the tools
(`cli._run_profile(..., chain=...)`), so every shipped description,
summary and twin stays byte for byte as it was.

WHAT IT DOES, in 4.6b's order:

- reads every column through `reading.column_values` (lane SR's column
  access, plan P4-D400), each cell to its STARTING band by the
  classifier's own reading of the column (`taxonomy._read_the_column`,
  the same declarations `profile_column` applied), and checks the
  recount against the column's published counts before anything is
  published from it;
- cuts each eligible column's ladder (4.6b.2: `L0` the deciles with p25
  and p75 on a number, the nine interior rungs on a date or clock, each
  published level on a label column; the `L0` merge; `L1` and `L2` read
  through it) and codes every tabled row in one byte a level;
- searches the chain (4.6b.3): RULES W3 and NE fix the levels each
  candidate is offered at, every coarser variant is an option of its
  own, the floor, RULE W1 (read member by member and across the chain,
  checked in full at every step) and RULE WE decide which options are
  eligible, and RULE W5 DRAWS one option a step over every eligible one
  (4.6b.4), keyed by the installation's key, the table's name and the
  step, never greedily;
- raises an option's score, never its eligibility, for a time-and-event
  pair (`w_te`) and for the triple screen's seeds (`w_seed`), the screen
  ranking every triple twice on the content-keyed self-test sample
  (4.6b.8);
- counts every family on ALL tabled rows, and writes the structural
  words and the names (4.6b.8).

WHAT IT DOES NOT DO. It publishes no slope (ruling R12: no publishing
region exists while lane MPOL's gate is closed), no moment and no
patient-layer object; a table whose person column repeats (several rows
per patient) gets no chain, since the table layer's proof is for one row
per patient (lane MG's page owns the rest). Lane MR's rule inference is
not built, so no rule step opens and no column is computed or derived in
a description this module writes (4.6b.7 stands ready in
`chain_derived`). The key never reaches anything this module returns.

ARITHMETIC. Every count is a Python integer; every score an exact
fraction; the draw's weights the stated exponential of 4.6b.4. The
screen's scores are binary64 sums in a fixed order over a triple's cells,
which choose only which options are raised, never a published value
(plan P4-D409 part 2, zone D).
"""

import dataclasses
import fractions
import hashlib
import json
import math

from synthtwin import chain_moments as moments
from synthtwin import chain_rules as rules
from synthtwin import parsing, reading, taxonomy

# The reasons a whole chain is not published although the switch is on,
# each told in the private notes only (inventory rows 4 and 34).
OFF_PERSON = "several rows per person: the patient layer's (lane MG), not the table layer's"
OFF_RECOUNT = "a column's recount disagreed with its published counts"
OFF_FEW = "fewer than two eligible columns"
OFF_ROOT = "the root step drew no family"

FEW_LEVELS = 8
SCREEN_ALL = 10
SCREEN_FEW = 3
SCREEN_ROUNDS = 6


@dataclasses.dataclass(frozen=True)
class ChainSwitch:
    """The switch the product does not expose: the table's name and the installation's key.

    `name` is the person's name for the dataset (`--name`, by default the
    input file's name without its extension; 4.6b.4); `key` the
    installation's 32-byte private key (`installation.key_of`). The key is
    read here and handed to the draw's words alone.
    """

    name: str
    key: bytes
    held: "tuple[str, ...]" = ()


@dataclasses.dataclass(frozen=True)
class Chained:
    """What `describe` returns: the published object and the private notes.

    `statistical` is the object 4.6b writes under `relationships`, or
    None where no chain is published. `notes` are lines for the private
    report only (why a family was not placed, refusals counted, the
    sample's size, the screen's seeds), never published and never
    holding the key. `counts` are the measurement counters a KPI driver
    reads (W1's refusals, eligible options, tables counted).
    """

    statistical: "dict[str, object] | None"
    notes: "tuple[str, ...]"
    counts: "dict[str, int]"
    seeds: "tuple[tuple[str, str, str], ...]"
    chosen: "tuple[tuple[str, tuple[str, ...], tuple[int, ...]], ...]"
    content: str
    moments: "dict[str, object] | None" = None


@dataclasses.dataclass(frozen=True)
class Column:
    """One eligible column read for the chain: its ladder, its codes, its groups."""

    name: str
    ladder: rules.Ladder
    codes: "tuple[bytes | list[int], bytes | list[int], bytes | list[int]]"
    groups: "frozenset[int]"
    screen: bytes
    screen_levels: int
    few: bool
    blank: int
    value_codes: "tuple[bytes, bytes | None, bytearray] | None" = None


@dataclasses.dataclass(frozen=True)
class Option:
    """One option of a step: a family (or `no family`) with its levels and table."""

    child: str
    parents: "tuple[str, ...]"
    levels: "tuple[int, ...]"
    anchor: "int | None"
    table: "tuple[int, ...]"
    score: fractions.Fraction


def _get(mapping: "dict[str, object]", key: str) -> object:
    """A key's value, or None where the mapping does not hold it."""
    if key in mapping:
        return mapping[key]
    return None


def _length_word(count: int) -> bytes:
    """A length as 8 bytes, big-endian (4.6b.8's framing)."""
    return bytes([(count >> shift) & 255 for shift in (56, 48, 40, 32, 24, 16, 8, 0)])


def _hex(data: bytes) -> str:
    """Bytes written as lower-case hexadecimal figures."""
    figures = "0123456789abcdef"
    out = ""
    for byte in data:
        out += figures[byte >> 4] + figures[byte & 15]
    return out


def _is_blank(text: str) -> bool:
    """A cell holding nothing but spaces and tabs holds NOTHING (contract 4.1, `empty_rows`)."""
    for character in text:
        if character not in " \t":
            return False
    return True


# -- THE WORDS OF THE DRAW (4.6b.4) --------------------------------------


def step_word(key: bytes, name: str, kind: str, index: object, columns: "list[str]") -> bytes:
    """A step's 16-byte word: keyed BLAKE2b over `[name, kind, index, columns]`.

    Keyed by the installation's key, `person=b"synthtwin.draw.1"`, over the
    UTF-8 bytes of the JSON array written with `separators=(",", ":")` and
    `ensure_ascii=False`. Never keyed by the table's content.
    """
    text = json.dumps([name, kind, index, columns], separators=(",", ":"), ensure_ascii=False)
    return hashlib.blake2b(
        bytes(text, "utf-8"), key=key, digest_size=16, person=b"synthtwin.draw.1"
    ).digest()


# -- ELIGIBILITY (4.6b.1) -------------------------------------------------


def ineligible_reason(block: "dict[str, object]", sequence: bool, held: bool, identifiers: "set[str]") -> "str | None":
    """4.6b.1's reason a column is ineligible, read before its ladder; None to read on."""
    role = _get(block, "role")
    name = _get(block, "name")
    if role == "identifier" or name in identifiers:
        return "identifier"
    if role == "free_text":
        return "free_text"
    if role == "empty":
        return "empty"
    if role == "numeric_unrepresentable":
        return "unrepresentable"
    if sequence:
        return "sequence"
    if held:
        return "held"
    if role not in rules.ORDERED_ROLES + rules.LABEL_ROLES:
        return "free_text"
    return None


# -- READING A COLUMN TO ITS STARTING BANDS -------------------------------


def _reading_of(
    block: "dict[str, object]",
    values: "list[str]",
    settings: taxonomy.Settings,
    declared: "dict[str, bool]",
    stored_as: str,
) -> "dict[str, tuple[str, object]]":
    """Each distinct cell text read as 4.6b.2's starting bands read it.

    Returns text -> (kind, reading): `missing`; `other` (a present cell
    holding no reading of the value bands); `labels`; `value` with the
    reading in the column's own order (a number, a canonical date, a
    clock ordinal); `level` with the published label; `pool`.
    """
    name = f"{_get(block, 'name')}"
    role = f"{_get(block, 'role')}"
    comma = declared["decimal_comma"]
    spelled = taxonomy.spellings_read(
        values,
        name,
        settings,
        forced_code=declared["code"],
        forced_measurement=declared["measurement"],
        forced_decimal_comma=comma,
        stored_as=stored_as,
    )
    out: "dict[str, tuple[str, object]]" = {}
    present: "list[str]" = []
    for text in spelled:
        if spelled[text][0] == "missing":
            out[text] = ("missing", None)
        else:
            present += [text]
    if role in (rules.ROLE_COUNT, rules.ROLE_CONTINUOUS, rules.ROLE_COMPOUND):
        for text in present:
            kind, number = spelled[text]
            if kind == parsing.NUMBER and number is not None:
                out[text] = ("value", float(number))
            elif role == rules.ROLE_COMPOUND:
                out[text] = ("labels", None)
            else:
                out[text] = ("other", None)
        return out
    if role == rules.ROLE_AFFIXED:
        prefix = _get(block, "affix_prefix")
        suffix = _get(block, "affix_suffix")
        for text in present:
            core = None
            if isinstance(prefix, str) and isinstance(suffix, str):
                core = taxonomy.core_read(text, prefix, suffix, comma)
            if core is not None and core[0] == parsing.NUMBER and core[1] is not None:
                out[text] = ("value", float(core[1]))
            else:
                out[text] = ("other", None)
        return out
    if role == rules.ROLE_JOINED:
        separator = _get(block, "separator")
        for text in present:
            parts = None
            if isinstance(separator, str):
                parts = taxonomy.splits_into_numbers(text, separator)
            first = taxonomy.spelling_read(parts[0], comma) if parts else None
            if first is not None and first[0] == parsing.NUMBER and first[1] is not None:
                out[text] = ("value", float(first[1]))
            else:
                out[text] = ("other", None)
        return out
    if role == rules.ROLE_DATETIME:
        form = _get(block, "format")
        for text in present:
            parsed = parsing.parse_datetime(text, form) if isinstance(form, str) else None
            out[text] = ("other", None) if parsed is None else ("value", parsed[0])
        return out
    if role == rules.ROLE_CLOCK:
        form = _get(block, "clock_form")
        for text in present:
            ordinal = None
            if isinstance(form, str) and form in parsing.CLOCK_FORMS:
                ordinal = parsing.clock_ordinal(text, form)
            out[text] = ("other", None) if ordinal is None else ("value", ordinal)
        return out
    # Label columns: each published spelling to its level, the rest pooled.
    by_spelling: "dict[str, str]" = {}
    by_folded: "dict[str, str]" = {}
    for label, _count in rules.label_levels(block):
        by_folded[parsing.folded(label)] = label
    levels = _get(block, "levels")
    if isinstance(levels, list):
        for level in levels:
            if not isinstance(level, dict):
                continue
            variants = _get(level, "variants")
            level_label = _get(level, "label")
            if isinstance(variants, dict) and isinstance(level_label, str):
                for spelling in variants:
                    by_spelling[spelling] = level_label
    for text in present:
        if text in by_spelling:
            out[text] = ("level", by_spelling[text])
        elif parsing.folded(text) in by_folded:
            out[text] = ("level", by_folded[parsing.folded(text)])
        else:
            out[text] = ("pool", None)
    return out


def _starting_index(start: rules.Starting) -> "dict[object, int]":
    """Each starting band's descriptor to its place."""
    out: "dict[object, int]" = {}
    for place in range(len(start.names)):
        out[start.names[place]] = place
    return out


def _value_places(start: rules.Starting) -> "list[int]":
    return [place for place in range(len(start.names)) if start.value[place]]


def _recount_agrees(block: "dict[str, object]", totals: "dict[str, int]", tabled_missing: int, blank_rows: int) -> bool:
    """Whether the starting totals agree with the column's own published counts.

    `totals` holds the rows of each kind over every row of the table; the
    `missing` band over the tabled rows is `n_missing - E` (4.6b.2), so
    the check reads `n_missing` itself.
    """
    role = f"{_get(block, 'role')}"
    present = _get(block, "n_present")
    missing = _get(block, "n_missing")
    if not isinstance(present, int) or not isinstance(missing, int):
        return False
    if totals["missing"] != missing or totals["missing"] - blank_rows != tabled_missing:
        return False
    readings = totals["value"]
    if role in (rules.ROLE_COUNT, rules.ROLE_CONTINUOUS, rules.ROLE_AFFIXED):
        return readings == _get(block, "n_used_in_statistics")
    if role == rules.ROLE_COMPOUND:
        return readings == _get(block, "n_numeric_cells") and totals["labels"] == _get(block, "n_label_cells")
    if role in (rules.ROLE_DATETIME, rules.ROLE_CLOCK):
        unparsed = _get(block, "n_unparsed")
        unread = unparsed if isinstance(unparsed, int) else 0
        return readings == present - unread
    if role == rules.ROLE_JOINED:
        return readings + totals["other"] == present
    return readings + totals["pool"] == present


@dataclasses.dataclass(frozen=True)
class _Read:
    """One column's starting bands, its rows' starting codes, and the recount."""

    start: rules.Starting
    codes: "list[int]"
    agrees: bool
    blanks: bytearray
    linear: "bytes | None"
    second: "bytes | None"
    has_reading: bytearray


def read_column(
    table: reading.Table,
    place: int,
    block: "dict[str, object]",
    settings: taxonomy.Settings,
    declared: "dict[str, bool]",
    stored_as: str,
    blank_rows: int,
) -> "_Read | None":
    """One column read to its starting bands, row by row, through `reading.column_values`."""
    values = reading.column_values(table, place)
    start = rules.starting_bands(block, (True, True, True))
    if start is None:
        return None
    meaning = _reading_of(block, values, settings, declared, stored_as)
    places = _starting_index(start)
    value_places = _value_places(start)
    role = f"{_get(block, 'role')}"
    code_of: "dict[str, int]" = {}
    kinds: "dict[str, int]" = {"missing": 0, "other": 0, "labels": 0, "value": 0, "pool": 0}
    kind_of: "dict[str, str]" = {}
    for text in meaning:
        kind, value = meaning[text]
        if kind == "missing":
            code = places[rules.MISSING]
            kind_of[text] = "missing"
        elif kind == "other":
            code = places[rules.OTHER]
            kind_of[text] = "other"
        elif kind == "labels":
            code = places[rules.LABELS]
            kind_of[text] = "labels"
        elif kind == "pool":
            code = places[rules.POOL] if rules.POOL in places else -1
            kind_of[text] = "pool"
        elif kind == "level":
            code = places[(value,)] if (value,) in places else -1
            kind_of[text] = "value"
        else:
            index = rules.band_of_value(start.values, value)
            code = value_places[index] if index < len(value_places) else -1
            kind_of[text] = "value"
        code_of[text] = code
    codes: "list[int]" = []
    blanks = bytearray(len(values))
    agrees = True
    for row in range(len(values)):
        text = values[row]
        if text not in code_of:
            agrees = False
            codes += [0]
            continue
        code = code_of[text]
        if code < 0:
            agrees = False
            code = 0
        codes += [code]
        kinds[kind_of[text]] += 1
        if _is_blank(text):
            blanks[row] = 1
    missing = _get(block, "n_missing")
    tabled_missing = (missing if isinstance(missing, int) else 0) - blank_rows
    if role in rules.LABEL_ROLES:
        # A published level's rows are its published count.
        counted: "dict[str, int]" = {}
        for row in range(len(values)):
            text = values[row]
            if text in meaning and meaning[text][0] == "level":
                label = f"{meaning[text][1]}"
                counted[label] = counted[label] + 1 if label in counted else 1
        for label, count in rules.label_levels(block):
            if (counted[label] if label in counted else 0) != count:
                agrees = False
    agrees = agrees and _recount_agrees(block, kinds, tabled_missing, blank_rows)
    # THE MOMENT LAYER'S CODES (contract 4.6d.1), one byte a row, for a FINE
    # column: read here once, for the inputs `chain_moments` computes.
    linear: "bytes | None" = None
    second: "bytes | None" = None
    has_reading = bytearray(len(values))
    found = moments.codes_of(block) if moments.fine(block) else None
    if found is not None:
        by_text: "dict[str, tuple[int, int]]" = {}
        for text in meaning:
            kind, value = meaning[text]
            if kind != "value":
                continue
            exact = moments.ordinal(role, value, block)
            if exact is None:
                continue
            by_text[text] = (moments.linear_code(found, exact), moments.second_code(found, exact))
        first_codes = bytearray(len(values))
        second_codes = bytearray(len(values))
        for row in range(len(values)):
            if values[row] in by_text:
                pair = by_text[values[row]]
                first_codes[row] = pair[0]
                second_codes[row] = pair[1]
                has_reading[row] = 1
        linear = bytes(first_codes)
        second = bytes(second_codes) if found.second is not None else None
    return _Read(start, codes, agrees, blanks, linear, second, has_reading)


# -- THE CONTENT HASH AND THE SELF-TEST SAMPLE (4.6b.8) ------------------


def row_hashes(table: reading.Table) -> "tuple[list[bytes], bytearray]":
    """Each row's CONTENT HASH, and which rows hold nothing in every column.

    The hash is BLAKE2b (`digest_size=32`, `person=b"synthtwin.row.1"`)
    over the row's cells taken in the order of their column names, each
    written as the name's UTF-8 bytes and the cell's text's UTF-8 bytes,
    each of the two preceded by its own length in bytes as 8 bytes
    big-endian (4.6b.8). The cells are the reader's own
    (`reading.column_values`), so a CSV and a workbook of one table give
    one hash. Each row's framed bytes are gathered column by column in
    name order and digested once the last name is read; the price is the
    framed table held at once (`K-S6-15`'s count on a table read in
    groups, plan P4-D418).
    """
    names = list(table.column_names)
    order = sorted((names[place], place) for place in range(len(names)))
    rows = table.n_rows
    framed = [bytearray() for _row in range(rows)]
    filled = bytearray(rows)
    for name, place in order:
        name_bytes = bytes(name, "utf-8")
        head = _length_word(len(name_bytes)) + name_bytes
        values = reading.column_values(table, place)
        for row in range(rows):
            text = values[row]
            cell = bytes(text, "utf-8")
            framed[row] += head + _length_word(len(cell)) + cell
            if not _is_blank(text):
                filled[row] = 1
    hashes: "list[bytes]" = []
    for row in range(rows):
        hashes += [hashlib.blake2b(bytes(framed[row]), digest_size=32, person=b"synthtwin.row.1").digest()]
        framed[row] = bytearray()
    return hashes, filled


def content_hash(hashes: "list[bytes]") -> bytes:
    """The table's content hash: its rows' hashes summed modulo 2**256, written in 32 bytes."""
    total = 0
    for one in hashes:
        total = (total + rules.big_endian(one)) % (1 << 256)
    return bytes([(total >> (8 * (31 - at))) & 255 for at in range(32)])


def sample_rows(hashes: "list[bytes]", tabled: "list[int]", size: int) -> "list[int]":
    """The self-test's sample: the `min(m, n)` tabled rows of smallest SAMPLE KEY, sorted by key.

    Each row's key is BLAKE2b (`digest_size=8`, `person=b"synthtwin.smp.1"`)
    over its content hash and its OCCURRENCE (the count of earlier rows
    of the same hash) as 8 bytes big-endian; equal keys are taken in
    order of content hash and then occurrence (4.6b.8). Returns places in
    `tabled` (indices into the tabled rows).
    """
    seen: "dict[bytes, int]" = {}
    keyed: "list[tuple[bytes, bytes, int, int]]" = []
    for at in range(len(tabled)):
        one = hashes[tabled[at]]
        occurrence = seen[one] if one in seen else 0
        seen[one] = occurrence + 1
        key = hashlib.blake2b(one + _length_word(occurrence), digest_size=8, person=b"synthtwin.smp.1").digest()
        keyed += [(key, one, occurrence, at)]
    keyed = sorted(keyed)
    return [entry[3] for entry in keyed[: min(size, len(keyed))]]


# -- THE TRIPLE SCREEN (4.6b.3, inventory row 12) ------------------------


def _screen_codes(block: "dict[str, object]", read: _Read, ladder: rules.Ladder) -> "tuple[list[int], int, bool]":
    """A column's screen codes by starting band: finer for few-level columns, coarse otherwise.

    A `binary` column or a label column of at most 8 published levels
    reads each published level as its own code (and the pool, and blank
    cells, one more code each); every other column takes the coarse codes:
    a number below its median, up to its 90th percentile and above it, a
    label's two commonest levels and a pool, each with one code for blank
    and unread cells. Returns the starting band -> code map, the code
    count, and whether the column is few-level.
    """
    role = f"{_get(block, 'role')}"
    start = read.start
    out = [0] * len(start.names)
    if role in rules.LABEL_ROLES:
        levels = rules.label_levels(block)
        few = role == rules.ROLE_BINARY or len(levels) <= FEW_LEVELS
        ranked = sorted((-levels[place][1], place) for place in range(len(levels)))
        top_two = [pair[1] for pair in ranked[:2]]
        first_of_two = top_two[0] if top_two else -1
        level_place: "dict[object, int]" = {}
        for place in range(len(levels)):
            level_place[(levels[place][0],)] = place
        if few:
            count = len(levels) + 2
            for place in range(len(start.names)):
                name = start.names[place]
                if name in level_place:
                    out[place] = level_place[name]
                elif name == rules.POOL:
                    out[place] = len(levels)
                else:
                    out[place] = len(levels) + 1
            return out, count, True
        for place in range(len(start.names)):
            name = start.names[place]
            if name in level_place and level_place[name] in top_two:
                out[place] = 0 if level_place[name] == first_of_two else 1
            elif name == rules.MISSING:
                out[place] = 3
            else:
                out[place] = 2
        return out, 4, False
    medians = rules.level_edge_values(block, 2)
    rungs = rules.rung_ladder(block) or {}
    p90 = rules.rung_value(role, _get(rungs, "p90"), _get(block, "clock_form"))
    median = medians[0] if medians else None
    value_places = _value_places(start)
    for place in range(len(start.names)):
        if not start.value[place]:
            out[place] = 3
            continue
        k = 0
        while value_places[k] != place:
            k += 1
        low = start.values[k - 1] if k else None
        if low is None or median is None or rules.below(low, median):
            out[place] = 0
        elif p90 is None or rules.below(low, p90):
            out[place] = 1
        else:
            out[place] = 2
    return out, 4, False


_SHAPES: "dict[tuple[int, int, int], tuple[list[int], list[int], list[int]]]" = {}


def _slots(a: int, b: int, c: int) -> "tuple[list[int], list[int], list[int]]":
    """Each cell's place in the ab, ac and bc margins of an a x b x c table, kept by shape."""
    key = (a, b, c)
    if key not in _SHAPES:
        first: "list[int]" = []
        second: "list[int]" = []
        third: "list[int]" = []
        for i in range(a):
            for j in range(b):
                for k in range(c):
                    first += [i * b + j]
                    second += [i * c + k]
                    third += [j * c + k]
        _SHAPES[key] = (first, second, third)
    return _SHAPES[key]


def _triple_score(table: "list[int]", a: int, b: int, c: int) -> float:
    """A triple's departure from the model of no three-way term, `(X2 - df) / sqrt(2 df)`.

    The fit is the swap candidate's (lanes A0b and A0c): six rounds of
    proportional fitting to the three two-way margins in the order ab, ac,
    bc; `X2` over the fitted cells above 0.5, `df` a quarter of them and
    at least 1. Binary64 in a fixed order over the triple's cells, which
    chooses only which options are raised (plan P4-D409 part 2, zone D).
    """
    size = a * b * c
    places = _slots(a, b, c)
    widths = (a * b, a * c, b * c)
    targets: "list[list[float]]" = []
    for which in range(3):
        target = [0.0] * widths[which]
        slots = places[which]
        for cell in range(size):
            target[slots[cell]] += float(table[cell])
        targets += [target]
    fit = [1.0] * size
    for _round in range(SCREEN_ROUNDS):
        for which in range(3):
            slots = places[which]
            target = targets[which]
            current = [0.0] * widths[which]
            for cell in range(size):
                current[slots[cell]] += fit[cell]
            for cell in range(size):
                slot = slots[cell]
                fit[cell] = fit[cell] * target[slot] / current[slot] if current[slot] > 0.0 else 0.0
    chi = 0.0
    cells = 0
    for cell in range(size):
        expected = fit[cell]
        if expected > 0.5:
            gap = table[cell] - expected
            chi += gap * gap / expected
            cells += 1
    df = max(1, cells // 4)
    return (chi - df) / math.sqrt(2.0 * df)


def screen_seeds(columns: "list[Column]") -> "tuple[tuple[int, int, int], ...]":
    """The screen's seeds: the 10 best triples greedily, then 3 best few-level triples not among them.

    Every triple of eligible columns is counted on the sample and scored
    (`_triple_score`); ranked by score, ties by schema order. List (i) takes
    the 10 best, a pair of columns in at most two seeds; list (ii) the 3
    best of the few-level class (each member `binary` or a label column of
    at most 8 levels) not already in (i), a pair in at most two of them
    (4.6b.3, amended 2026-10-20).
    """
    count = len(columns)
    scored: "list[tuple[float, int, int, int, int]]" = []
    order = 0
    for i in range(count):
        first = columns[i]
        for j in range(i + 1, count):
            second = columns[j]
            pair_codes = [x * second.screen_levels + y for x, y in zip(first.screen, second.screen)]
            width = first.screen_levels * second.screen_levels
            for k in range(j + 1, count):
                third = columns[k]
                levels = third.screen_levels
                table = [0] * (width * levels)
                for x, y in zip(pair_codes, third.screen):
                    table[x * levels + y] += 1
                value = _triple_score(table, first.screen_levels, second.screen_levels, levels)
                scored += [(-value, order, i, j, k)]
                order += 1
    ranked = sorted(scored)
    chosen: "list[tuple[int, int, int]]" = []
    uses: "dict[tuple[int, int], int]" = {}
    for _value, _order, i, j, k in ranked:
        if len(chosen) >= SCREEN_ALL:
            break
        pairs = ((i, j), (i, k), (j, k))
        if any((uses[pair] if pair in uses else 0) >= 2 for pair in pairs):
            continue
        for pair in pairs:
            uses[pair] = (uses[pair] if pair in uses else 0) + 1
        chosen += [(i, j, k)]
    few_chosen: "list[tuple[int, int, int]]" = []
    few_uses: "dict[tuple[int, int], int]" = {}
    for _value, _order, i, j, k in ranked:
        if len(few_chosen) >= SCREEN_FEW:
            break
        if not (columns[i].few and columns[j].few and columns[k].few) or (i, j, k) in chosen:
            continue
        pairs = ((i, j), (i, k), (j, k))
        if any((few_uses[pair] if pair in few_uses else 0) >= 2 for pair in pairs):
            continue
        for pair in pairs:
            few_uses[pair] = (few_uses[pair] if pair in few_uses else 0) + 1
        few_chosen += [(i, j, k)]
    return tuple(chosen + few_chosen)


# -- TIME-AND-EVENT PAIRS (4.6b.3, inventory row 11) ---------------------

EVENT_WORDS = frozenset(
    {
        "event", "status", "died", "death", "dead", "deceased", "censor",
        "censored", "outcome", "relapse", "failure", "mortality", "readmit",
        "readmitted", "recurrence",
    }
)
TIME_WORDS = frozenset(
    {
        "time", "days", "day", "months", "month", "years", "year", "weeks",
        "week", "duration", "followup", "follow", "fu", "survival", "futime",
        "tte", "length", "stay",
    }
)


def _words_of_name(name: str) -> "set[str]":
    """A column name's words: runs of letters and figures, lower case."""
    if not isinstance(name, str):
        raise TypeError("a column name is text")
    out: "set[str]" = set()
    word = ""
    for character in name.lower():
        if "a" <= character <= "z" or "0" <= character <= "9":
            word += character
        else:
            if word:
                out = out | {word}
            word = ""
    if word:
        out = out | {word}
    return out


def time_event_pairs(blocks: "list[dict[str, object]]", eligible: "list[str]") -> "frozenset[tuple[str, str]]":
    """The time-and-event pairs, from published roles and names alone (inventory row 11).

    A follow-up time is an eligible `count` or `continuous` column whose
    name holds a word of time (`days`, `time`, `follow`, `survival`, ...);
    its event flag an eligible `binary` column whose name holds a word of
    an event (`event`, `status`, `died`, `death`, ...). Every such pair is
    one, both ways round. It only raises a weight (`w_te`), so a pair
    named wrongly costs nothing a proof rests on.
    """
    times: "list[str]" = []
    events: "list[str]" = []
    allowed = set(eligible)
    for block in blocks:
        name = _get(block, "name")
        role = _get(block, "role")
        if not isinstance(name, str) or name not in allowed:
            continue
        words = _words_of_name(name)
        if role in (rules.ROLE_COUNT, rules.ROLE_CONTINUOUS) and words & TIME_WORDS:
            times += [name]
        if role == rules.ROLE_BINARY and words & EVENT_WORDS:
            events += [name]
    out: "set[tuple[str, str]]" = set()
    for time_name in times:
        for event_name in events:
            out = out | {(time_name, event_name), (event_name, time_name)}
    return frozenset(out)


# -- COUNTING ON EVERY TABLED ROW -----------------------------------------


def count_table(
    child: "bytes | list[int]",
    parents: "list[bytes | list[int]]",
    child_bands: int,
    parent_bands: "list[int]",
) -> "list[int]":
    """A family's complete table over every tabled row, row-major, the last parent fastest."""
    width = 1
    for bands in parent_bands:
        width *= bands
    counts = [0] * (width * child_bands)
    if not parents:
        for c in child:
            counts[c] += 1
    elif len(parents) == 1:
        for a, c in zip(parents[0], child):
            counts[a * child_bands + c] += 1
    elif len(parents) == 2:
        second = parent_bands[1]
        for a, b, c in zip(parents[0], parents[1], child):
            counts[(a * second + b) * child_bands + c] += 1
    else:
        second = parent_bands[1]
        third = parent_bands[2]
        for a, b, d, c in zip(parents[0], parents[1], parents[2], child):
            counts[((a * second + b) * third + d) * child_bands + c] += 1
    return counts


def aggregate(table: "list[int] | tuple[int, ...]", sizes: "list[int]", coarser: "list[list[int]]", to_sizes: "list[int]") -> "list[int]":
    """A table summed to coarser levels: `coarser[m]` maps member `m`'s bands, child first."""
    width = 1
    for size in to_sizes:
        width *= size
    out = [0] * width
    for index in range(len(table)):
        count = table[index]
        if not count:
            continue
        parts = rules.cell_parts(index, sizes)
        cell = 0
        for place in range(1, len(parts)):
            cell = cell * to_sizes[place] + coarser[place][parts[place]]
        out[cell * to_sizes[0] + coarser[0][parts[0]]] += count
    return out


def _floored(table: "list[int] | tuple[int, ...]", floor: int) -> bool:
    for cell in table:
        if 0 < cell < floor:
            return False
    return True


# -- THE SEARCH (4.6b.3) AND THE DRAW (4.6b.4) ---------------------------


@dataclasses.dataclass(frozen=True)
class _Search:
    """What every step reads: the columns, their scales, the table's size and the weights' raises."""

    columns: "dict[str, Column]"
    scales: "dict[str, rules.Ladder]"
    eligible: "tuple[str, ...]"
    place: "dict[str, int]"
    tabled: int
    floor: int
    pairs: "frozenset[tuple[str, str]]"
    seeds: "tuple[tuple[str, str, str], ...]"
    tables: "dict[tuple[str, tuple[str, ...], tuple[int, ...]], tuple[int, ...]]"
    counts: "dict[str, int]"
    scored: "dict[tuple[str, tuple[str, ...], tuple[int, ...]], tuple[bool, fractions.Fraction]]"


def _table_at(search: _Search, child: str, parents: "tuple[str, ...]", base: "tuple[int, ...]", levels: "tuple[int, ...]") -> "tuple[int, ...]":
    """A candidate's complete table at `levels`, counted once at `base` (W3 and NE's levels) and summed coarser."""
    key = (child, parents, levels)
    if key in search.tables:
        return search.tables[key]
    names = (child,) + parents
    if levels != base:
        finest = _table_at(search, child, parents, base, base)
        sizes = [search.scales[names[at]].counts[base[at]] for at in range(len(names))]
        to_sizes = [search.scales[names[at]].counts[levels[at]] for at in range(len(names))]
        maps = [rules.coarsen(search.scales[names[at]], base[at], levels[at]) for at in range(len(names))]
        table = tuple(aggregate(finest, sizes, maps, to_sizes))
    else:
        child_codes = search.columns[child].codes[levels[0]]
        parent_codes = [search.columns[parents[at]].codes[levels[at + 1]] for at in range(len(parents))]
        bands = [search.scales[parents[at]].counts[levels[at + 1]] for at in range(len(parents))]
        table = tuple(count_table(child_codes, parent_codes, search.scales[child].counts[levels[0]], bands))
        search.counts["tables_counted"] += 1
    search.tables[key] = table
    return table


def _judged(search: _Search, child: str, parents: "tuple[str, ...]", levels: "tuple[int, ...]", table: "tuple[int, ...]") -> "tuple[bool, fractions.Fraction]":
    """Whether a candidate's table passes the floor, and its score with its raises: facts of the table, kept."""
    key = (child, parents, levels)
    if key in search.scored:
        return search.scored[key]
    floored = _floored(table, search.floor)
    value = fractions.Fraction(0)
    if floored:
        columns = search.scales[child].counts[levels[0]]
        value = rules.score(table, len(table) // columns, columns) + _raise_of(search, child, parents)
    search.scored[key] = (floored, value)
    return floored, value


def _raise_of(search: _Search, child: str, parents: "tuple[str, ...]") -> fractions.Fraction:
    """The score's raise for a family (weights only, 4.6b.3): `w_te n` and `w_seed n` a seed's further column."""
    raised = fractions.Fraction(0)
    for parent in parents:
        if (child, parent) in search.pairs:
            raised += rules.W_TE * search.tabled
            break
    for seed in search.seeds:
        if child in seed:
            for parent in parents:
                if parent in seed:
                    raised += rules.W_SEED * search.tabled
    return raised


@dataclasses.dataclass(frozen=True)
class _Clamps:
    """One step's W1 supports: each family's feasible cells under each clamp."""

    support: rules.Support
    groups: "dict[tuple[str, int], list[list[tuple[int, tuple[int, ...]]]]]"
    bands: "dict[tuple[str, int], list[list[tuple[int, tuple[int, ...]]]]]"
    projected: "dict[tuple[str, str, int, int, tuple[str, ...], tuple[int, ...]], frozenset[int]]"
    narrowed: "dict[tuple[str, str, int], frozenset[int]]"


def _clamps_of(search: _Search, placed: "list[rules.Family]", need_bands: bool) -> _Clamps:
    """The supports W1's fast check reads at one step (4.6b.9 (c)).

    `groups` clamps each placed column to each of its chain-level bands
    holding an own-fact group; `bands` clamps each placed column to each
    band of its coarsest level, read only where an unplaced child holds a
    group of its own.
    """
    support = rules.support_of(placed, search.scales)
    groups: "dict[tuple[str, int], list[list[tuple[int, tuple[int, ...]]]]]" = {}
    bands: "dict[tuple[str, int], list[list[tuple[int, tuple[int, ...]]]]]" = {}
    for family in placed:
        name = family.child
        ladder = search.scales[name]
        for group in sorted(search.columns[name].groups):
            band = ladder.maps[family.level][group]
            if (name, band) not in groups:
                groups[(name, band)] = rules.beliefs(support, (name, {band}))
        if need_bands:
            coarse = rules.coarsen(ladder, family.level, 2)
            for wide in range(ladder.counts[2]):
                inside = {band for band in range(len(coarse)) if coarse[band] == wide}
                bands[(name, wide)] = rules.beliefs(support, (name, inside))
    # Which families each clamp NARROWS: where it leaves every non-zero cell of
    # a family feasible, the projection onto any parents is every parent cell
    # the family's table holds, and the option's own table answers alone.
    narrowed: "dict[tuple[str, str, int], frozenset[int]]" = {}
    for which, held in (("group", groups), ("band", bands)):
        for key in held:
            reached = held[key]
            narrowed[(which, key[0], key[1])] = frozenset(
                at for at in range(len(placed)) if len(reached[at]) != len(support.cells[at])
            )
    return _Clamps(support, groups, bands, {}, narrowed)


def _projector(search: _Search, anchor: rules.Family, parents: "tuple[str, ...]", levels: "tuple[int, ...]") -> "list[tuple[int, list[int], int]]":
    """How an anchor cell's bands give a parent cell of a candidate at `levels`: (place, map, size) a parent."""
    held = rules.members(anchor)
    out: "list[tuple[int, list[int], int]]" = []
    for at in range(len(parents)):
        for place in range(len(held)):
            if held[place][0] == parents[at]:
                ladder = search.scales[parents[at]]
                out += [(place, rules.coarsen(ladder, held[place][1], levels[at]), ladder.counts[levels[at]])]
    return out


def _w1_holds(
    search: _Search,
    clamps: "_Clamps | None",
    anchor_at: "int | None",
    anchor: "rules.Family | None",
    child: str,
    parents: "tuple[str, ...]",
    levels: "tuple[int, ...]",
    table: "tuple[int, ...]",
) -> bool:
    """RULE W1 for an option whose child stands in no placed family yet (4.6b.3).

    Adding a family whose child is new never narrows an earlier support:
    its table summed over the child equals the anchor's summed to its
    parents (S25), so every combination the chain allowed extends. So
    only the pairs holding the new child are read, each against the
    support of the whole chain: (a) every placed column's group bands
    beside the child's coarsest level, and (b) the child's own group
    bands beside every placed column's coarsest level. A child that
    already stands in a placed family takes the full check
    (`rules.w1_refusals`).
    """
    ladder = search.scales[child]
    child_bands = ladder.counts[levels[0]]
    to_coarse = rules.coarsen(ladder, levels[0], 2)
    if anchor is None:
        # A root pair: one parent, nothing placed.
        parent = parents[0]
        parent_ladder = search.scales[parent]
        parent_coarse = rules.coarsen(parent_ladder, levels[1], 2)
        rows = parent_ladder.counts[levels[1]]
        for group in search.columns[parent].groups:
            row = parent_ladder.maps[levels[1]][group]
            reached = {to_coarse[c] for c in range(child_bands) if table[row * child_bands + c]}
            if len(reached) < 2:
                return False
        for group in search.columns[child].groups:
            column = ladder.maps[levels[0]][group]
            reached = {parent_coarse[r] for r in range(rows) if table[r * child_bands + column]}
            if len(reached) < 2:
                return False
        return True
    if clamps is None or anchor_at is None:
        return True
    width = len(table) // child_bands
    whole: "set[int]" = set()
    for row in range(width):
        for c in range(child_bands):
            if table[row * child_bands + c]:
                whole = whole | {to_coarse[c]}
    for key in clamps.groups:
        if anchor_at not in clamps.narrowed[("group", key[0], key[1])]:
            if len(whole) < 2:
                return False
            continue
        reachable = _projected(search, clamps, "group", key, anchor_at, anchor, parents, levels[1:])
        reached_bands: "set[int]" = set()
        for row in reachable:
            for c in range(child_bands):
                if table[row * child_bands + c]:
                    reached_bands = reached_bands | {to_coarse[c]}
            if len(reached_bands) >= 2:
                break
        if len(reached_bands) < 2:
            return False
    own = {ladder.maps[levels[0]][group] for group in search.columns[child].groups}
    for band in sorted(own):
        rows_holding: "set[int]" = set()
        for row in range(width):
            if table[row * child_bands + band]:
                rows_holding = rows_holding | {row}
        placed_names = sorted({key[0] for key in clamps.bands})
        for other in placed_names:
            admitted = 0
            for wide in range(search.scales[other].counts[2]):
                if anchor_at not in clamps.narrowed[("band", other, wide)]:
                    admitted += 1 if rows_holding else 0
                    continue
                feasible_rows = _projected(search, clamps, "band", (other, wide), anchor_at, anchor, parents, levels[1:])
                if feasible_rows & rows_holding:
                    admitted += 1
            if admitted < 2:
                return False
    return True


def _projected(
    search: _Search,
    clamps: _Clamps,
    which: str,
    key: "tuple[str, int]",
    anchor_at: int,
    anchor: rules.Family,
    parents: "tuple[str, ...]",
    plevels: "tuple[int, ...]",
) -> "frozenset[int]":
    """The parent cells, at a candidate's parent levels, of the anchor's cells a clamp leaves feasible.

    Kept for the step: options sharing an anchor, parents and levels read
    one projection however many children and child levels they offer.
    """
    slot = (which, key[0], key[1], anchor_at, parents, plevels)
    if slot in clamps.projected:
        return clamps.projected[slot]
    feasible = (clamps.groups if which == "group" else clamps.bands)[key][anchor_at]
    projector = _projector(search, anchor, parents, plevels)
    found = frozenset(_fold(projector, parts) for _index, parts in feasible)
    clamps.projected[slot] = found
    return found


def _fold(projector: "list[tuple[int, list[int], int]]", parts: "tuple[int, ...]") -> int:
    """One anchor cell's parent cell at a candidate's levels."""
    cell = 0
    for place, mapping, size in projector:
        cell = cell * size + mapping[parts[place]]
    return cell


def _listed(names: "tuple[str, ...]") -> str:
    """Names joined by commas, for a note."""
    out = ""
    for name in names:
        out = name if not out else f"{out}, {name}"
    return out


def _family_of(option: Option) -> rules.Family:
    """The family an option places."""
    parents = tuple((option.parents[at], option.levels[at + 1]) for at in range(len(option.parents)))
    return rules.Family(option.child, option.levels[0], parents, option.anchor, option.table)


def _no_family(search: _Search, child: str) -> Option:
    """`no family for d`: the column as a family with no parent at `L0`, scoring 0."""
    return Option(child, (), (0,), None, tuple(search.scales[child].totals), fractions.Fraction(0))


def _subsets(names: "list[str]", k_max: int) -> "list[tuple[str, ...]]":
    """Every set of 1 to `k_max` names, each in the order given."""
    out: "list[tuple[str, ...]]" = [()]
    for name in names:
        out = out + [done + (name,) for done in out if len(done) < k_max]
    return [one for one in out if one]


def _step_options(
    search: _Search,
    placed: "list[rules.Family]",
    clamps: "_Clamps | None",
    margins: "dict[tuple[int, tuple[str, ...]], rules.ParentCells]",
) -> "list[Option]":
    """A step's ELIGIBLE options in option order (4.6b.3, 4.6b.4)."""
    placed_names = {family.child for family in placed}
    earliest: "dict[tuple[str, ...], int]" = {}
    for at in range(len(placed)):
        ordered = sorted((search.place[name], name) for name, _level in rules.members(placed[at]))
        for subset in _subsets([pair[1] for pair in ordered], rules.K_MAX):
            if subset not in earliest:
                earliest[subset] = at
    out: "list[Option]" = []
    for child in search.eligible:
        if child in placed_names:
            continue
        out += [_no_family(search, child)]
        found: "list[tuple[int, tuple[int, ...], tuple[int, ...], int, Option]]" = []
        for subset in sorted(earliest):
            anchor_at = earliest[subset]
            anchor = placed[anchor_at]
            held = dict(rules.members(anchor))
            start = [0] + [held[name] for name in subset]
            order = [search.place[child]] + [search.place[name] for name in subset]
            key = (anchor_at, subset)
            if key not in margins:
                margins[key] = rules.parent_cells(search.scales, subset, anchor)
            scales = [search.scales[child]] + [search.scales[name] for name in subset]
            offered = rules.offered_levels(scales, start, order, margins[key], search.tabled, search.floor)
            search.counts["candidates"] += 1
            if offered is None:
                continue
            base = tuple(offered)
            for levels in rules.variants_of(offered):
                table = _table_at(search, child, subset, base, levels)
                floored, value = _judged(search, child, subset, levels, table)
                if not floored:
                    search.counts["floor_refusals"] += 1
                    continue
                if not _w1_holds(search, clamps, anchor_at, anchor, child, subset, levels, table):
                    search.counts["w1_refusals"] += 1
                    continue
                option = Option(child, subset, levels, anchor_at, table, value)
                found += [(anchor_at, tuple(search.place[name] for name in subset), levels, len(found), option)]
        for _anchor, _places, _levels, _serial, option in sorted(found):
            out += [option]
    return out


def _root_options(search: _Search, x0: "dict[str, int] | None", room: int) -> "list[Option]":
    """The root step's ELIGIBLE options in option order: `no family`, then every pair."""
    out: "list[Option]" = [Option("", (), (), None, (), fractions.Fraction(0))]
    found: "list[tuple[int, int, tuple[int, ...], int, Option]]" = []
    names = list(search.eligible)
    for later in range(len(names)):
        child = names[later]
        for earlier in range(later):
            parent = names[earlier]
            margins = rules.parent_cells(search.scales, (parent,), None)
            offered = rules.offered_levels(
                [search.scales[child], search.scales[parent]],
                [0, 0],
                [later, earlier],
                margins,
                search.tabled,
                search.floor,
            )
            search.counts["candidates"] += 1
            if offered is None:
                continue
            base = tuple(offered)
            for levels in rules.variants_of(offered):
                table = _table_at(search, child, (parent,), base, levels)
                if not _floored(table, search.floor):
                    search.counts["floor_refusals"] += 1
                    continue
                if not _w1_holds(search, None, None, None, child, (parent,), levels, table):
                    search.counts["w1_refusals"] += 1
                    continue
                option = Option(child, (parent,), levels, 0, table, rules.score(table, search.scales[parent].counts[levels[1]], search.scales[child].counts[levels[0]]) + _raise_of(search, child, (parent,)))
                if x0 is not None:
                    roots = [
                        rules.Family(parent, levels[1], (), None, tuple(rules.totals_at(search.scales[parent], levels[1]))),
                        rules.Family(child, levels[0], ((parent, levels[1]),), 0, table),
                    ]
                    if rules.cell_bound(x0, roots, search.scales, search.tabled) > room:
                        search.counts["we_refusals"] += 1
                        continue
                found += [(later, earlier, levels, len(found), option)]
    for _later, _earlier, _levels, _serial, option in sorted(found):
        out += [option]
    return out


def _draw(search: _Search, switch: ChainSwitch, index: int, options: "list[Option]") -> int:
    """RULE W5: the place of the option drawn among a step's eligible options."""
    weights = rules.weights_of([option.score for option in options], rules.TAU)
    word = step_word(switch.key, switch.name, "place", index, list(search.eligible))
    return rules.choose(word, weights)


def search_chain(search: _Search, switch: ChainSwitch, x0: "dict[str, int] | None", room: int) -> "tuple[list[rules.Family], list[str]]":
    """The chain, step by step, each step DRAWN among its eligible options (4.6b.3, 4.6b.4)."""
    notes: "list[str]" = []
    roots = _root_options(search, x0, room)
    search.counts["eligible_options"] += len(roots)
    pick = _draw(search, switch, 0, roots)
    if pick == 0:
        notes += [f"the root step drew no family among {len(roots)} eligible options"]
        return [], notes
    root = roots[pick]
    parent = root.parents[0]
    placed: "list[rules.Family]" = [
        rules.Family(parent, root.levels[1], (), None, tuple(rules.totals_at(search.scales[parent], root.levels[1]))),
        rules.Family(root.child, root.levels[0], ((parent, root.levels[1]),), 0, root.table),
    ]
    notes += [f"step 0 drew {root.child} under {parent} among {len(roots)} eligible options"]
    margins: "dict[tuple[int, tuple[str, ...]], rules.ParentCells]" = {}
    index = 1
    while len(placed) < len(search.eligible):
        need_bands = any(
            search.columns[name].groups
            for name in search.eligible
            if name not in {family.child for family in placed}
        )
        clamps = _clamps_of(search, placed, need_bands)
        options = _step_options(search, placed, clamps, margins)
        search.counts["eligible_options"] += len(options)
        pick = _draw(search, switch, index, options)
        chosen = options[pick]
        placed += [_family_of(chosen)]
        if chosen.parents:
            notes += [f"step {index} drew {chosen.child} under {_listed(chosen.parents)} among {len(options)} eligible options"]
        else:
            notes += [f"step {index} drew no family for {chosen.child} among {len(options)} eligible options"]
        index += 1
    return placed, notes


# -- THE WHOLE STEP: describe (4.6b) --------------------------------------


def _repeats(values: "list[str]") -> bool:
    """Whether some present value stands on two or more rows."""
    seen: "set[str]" = set()
    for text in values:
        if _is_blank(text):
            continue
        if text in seen:
            return True
        seen = seen | {text}
    return False


def _sequence_places(document: "dict[str, object]") -> "set[int]":
    """The row-sequence columns' places (`sequence_start` published, plan P4-D86)."""
    out: "set[int]" = set()
    source = _get(document, "source")
    dialect = _get(source, "dialect") if isinstance(source, dict) else None
    columns = _get(dialect, "columns") if isinstance(dialect, dict) else None
    if isinstance(columns, list):
        for place in range(len(columns)):
            entry = columns[place]
            if isinstance(entry, dict) and _get(entry, "sequence_start") is not None:
                out = out | {place}
    return out


def _codes(values: "list[int]") -> "bytes | list[int]":
    """A level's codes in one byte a row where they fit, else as numbers."""
    if not values or max(values) < 256:
        return bytes(values)
    return values


def moment_inputs(
    placed: "list[rules.Family]",
    scales: "dict[str, rules.Ladder]",
    columns: "dict[str, Column]",
    blocks: "dict[str, dict[str, object]]",
    floor: int,
) -> "dict[str, object]":
    """The moment layer's offers, regions, codes, sums and the witness's inputs (contract 4.6d), never published.

    Lane MPOL's GATE is closed, so `procedure.classes` is empty and the
    description's `moments` stays `null`; these are handed to the caller
    for lane MPp's witness and lane CHo's oracle (4.6d.10's "owed
    elsewhere").
    """
    region_columns = [name for name in blocks if columns[name].value_codes is not None]
    codes: "list[dict[str, object]]" = []
    for name in region_columns:
        found = moments.codes_of(blocks[name])
        if found is not None:
            codes += [{"column": name, "hi": found.hi, "lo": found.lo, "p50": found.p50,
                       "second": None if found.second is None else list(found.second)}]
    offers = moments.offers_of(placed, scales, region_columns, floor)
    regions = moments.regions_of(placed, offers)
    level_codes = {name: columns[name].codes for name in columns}
    value_codes: "dict[str, tuple[bytes, bytes | None, bytearray]]" = {}
    for name in region_columns:
        held = columns[name].value_codes
        if held is not None:
            value_codes[name] = held
    sums = moments.sums_of(placed, scales, level_codes, value_codes, offers)
    cuts: "dict[str, int]" = {}
    for name in region_columns:
        found = moments.codes_of(blocks[name])
        if found is not None:
            cuts[name] = len(moments.cut_points(found, blocks[name], scales[name]))
    return {
        "classes_published": [],
        "codes": codes,
        "cut_points": cuts,
        "offers": [{"class": "mean", "column": name, "family": at} for name, at in offers],
        "regions": [{"columns": list(names), "families": list(nodes)} for names, nodes in regions],
        "sums": sums,
    }


def _off(note: str, counts: "dict[str, int]", notes: "list[str]", content: str) -> Chained:
    return Chained(None, tuple(notes + [f"no chain is published: {note}"]), counts, (), (), content)


def describe(
    table: reading.Table,
    document: "dict[str, object]",
    settings: taxonomy.Settings,
    switch: ChainSwitch,
    forced_codes: "list[str] | None" = None,
    forced_measurements: "list[str] | None" = None,
    forced_decimal_commas: "list[str] | None" = None,
    stored_as: "tuple[str, ...] | None" = None,
) -> Chained:
    """The chain of `document`'s table: its `statistical` object and the private notes (4.6b).

    Guarantees: reads the table through `reading.column_values` and the
    description `profile.build_document` wrote of it, under the same
    settings and declarations; returns the object 4.6b writes under
    `relationships.statistical`, or None where no chain is published,
    with the reason in the notes. The same table, name, key, settings and
    declarations give the same object byte for byte: nothing here reads
    a clock, an environment or a random source but the key's words.
    Boundary: the key enters `step_word` alone; no returned value holds
    it. Not in force: only a caller holding the switch reaches this.
    """
    counts: "dict[str, int]" = {
        "tables_counted": 0,
        "candidates": 0,
        "floor_refusals": 0,
        "w1_refusals": 0,
        "we_refusals": 0,
        "eligible_options": 0,
        "eligible_columns": 0,
        "sample_rows": 0,
    }
    notes: "list[str]" = []
    floor = settings.small_cell_floor
    blocks: "list[dict[str, object]]" = []
    columns_published = _get(document, "columns")
    if isinstance(columns_published, list):
        for block in columns_published:
            if isinstance(block, dict):
                blocks += [block]
    held = set(switch.held)
    settings_block = _get(document, "settings")
    identifiers: "set[str]" = set()
    persons: "list[str]" = []
    if isinstance(settings_block, dict):
        forced = _get(settings_block, "forced_identifiers")
        if isinstance(forced, list):
            identifiers = {f"{name}" for name in forced}
        named = _get(settings_block, "person_columns")
        if isinstance(named, list):
            persons = [f"{name}" for name in named]
    hashes, filled = row_hashes(table)
    content = _hex(content_hash(hashes))
    if persons:
        return _off(OFF_PERSON, counts, notes, content)
    for place in range(len(blocks)):
        named = _get(blocks[place], "name")
        if (named in held or named in identifiers) and _repeats(reading.column_values(table, place)):
            return _off(OFF_PERSON, counts, notes, content)
    blank_rows = rules.records_holding_nothing(document)
    excluded = bytearray(table.n_rows)
    left = blank_rows
    for row in range(table.n_rows):
        if left and not filled[row]:
            excluded[row] = 1
            left -= 1
    if left:
        return _off(OFF_RECOUNT, counts, notes, content)
    tabled_rows = [row for row in range(table.n_rows) if not excluded[row]]
    tabled = len(tabled_rows)
    sample = sample_rows(hashes, tabled_rows, rules.selftest_size(tabled))
    counts["sample_rows"] = len(sample)
    sequences = _sequence_places(document)
    declared_codes = set(forced_codes or [])
    declared_measurements = set(forced_measurements or [])
    declared_commas = set(forced_decimal_commas or [])
    storage = stored_as or ()
    eligible: "list[str]" = []
    ineligible: "list[dict[str, object]]" = []
    columns: "dict[str, Column]" = {}
    moment_blocks: "dict[str, dict[str, object]]" = {}
    scales: "dict[str, rules.Ladder]" = {}
    for place in range(len(blocks)):
        block = blocks[place]
        name = f"{_get(block, 'name')}"
        reason = ineligible_reason(block, place in sequences, name in held, identifiers)
        if reason is not None:
            ineligible += [{"column": name, "reason": reason}]
            continue
        declared = {
            "code": name in declared_codes,
            "measurement": name in declared_measurements,
            "decimal_comma": name in declared_commas,
        }
        read = read_column(
            table,
            place,
            block,
            settings,
            declared,
            storage[place] if place < len(storage) else "",
            blank_rows,
        )
        if read is None or not read.agrees:
            notes += [f"the recount of column {name} disagreed with its published counts"]
            return _off(OFF_RECOUNT, counts, notes, content)
        starting_totals = [0] * len(read.start.names)
        for row in tabled_rows:
            starting_totals[read.codes[row]] += 1
        ladder = rules.merge_ladder(name, read.start, starting_totals, floor)
        role = _get(block, "role")
        if ladder is None:
            ineligible += [{"column": name, "reason": "one_band"}]
            continue
        if role == rules.ROLE_CONSTANT and rules.MISSING not in {
            one for band in ladder.l0 for one in band
        }:
            ineligible += [{"column": name, "reason": "constant"}]
            continue
        coarse_totals = rules.totals_at(ladder, 2)
        if len([total for total in coarse_totals if total > 0]) < 2:
            ineligible += [{"column": name, "reason": "one_band"}]
            continue
        start_to_l0 = [0] * len(read.start.names)
        for at in range(len(ladder.l0)):
            for start_place in range(len(read.start.names)):
                if read.start.names[start_place] in ladder.l0[at]:
                    start_to_l0[start_place] = at
        first = [start_to_l0[read.codes[row]] for row in tabled_rows]
        second = [ladder.maps[1][code] for code in first]
        third = [ladder.maps[2][code] for code in first]
        screen_map, screen_levels, few = _screen_codes(block, read, ladder)
        screen = bytes(screen_map[read.codes[tabled_rows[at]]] for at in sample)
        blank = 0
        for row in tabled_rows:
            blank += read.blanks[row]
        groups = rules.small_group_bands(block, read.start, ladder, floor)
        value_codes: "tuple[bytes, bytes | None, bytearray] | None" = None
        if read.linear is not None:
            linear_rows = read.linear
            second_rows = read.second
            value_codes = (
                bytes(linear_rows[row] for row in tabled_rows),
                None if second_rows is None else bytes(second_rows[row] for row in tabled_rows),
                bytearray(read.has_reading[row] for row in tabled_rows),
            )
            moment_blocks[name] = block
        columns[name] = Column(
            name,
            ladder,
            (_codes(first), _codes(second), _codes(third)),
            frozenset(groups),
            screen,
            screen_levels,
            few,
            blank,
            value_codes,
        )
        scales[name] = ladder
        eligible += [name]
    counts["eligible_columns"] = len(eligible)
    if len(eligible) < 2:
        return _off(OFF_FEW, counts, notes, content)
    pairs = time_event_pairs(blocks, eligible)
    seed_places = screen_seeds([columns[name] for name in eligible])
    seeds = tuple((eligible[i], eligible[j], eligible[k]) for i, j, k in seed_places)
    place_of: "dict[str, int]" = {}
    for at in range(len(eligible)):
        place_of[eligible[at]] = at
    search = _Search(columns, scales, tuple(eligible), place_of, tabled, floor, pairs, seeds, {}, counts, {})
    blank_counts = {name: columns[name].blank for name in eligible}
    x0 = rules.blank_cell(scales, blank_counts)
    room = rules.blank_record_room(document, floor) + rules.outside_cells(document, set(eligible))
    placed, step_notes = search_chain(search, switch, x0, room)
    notes += step_notes
    if not placed:
        return _off(OFF_ROOT, counts, notes, content)
    refused = rules.w1_refusals(placed, scales, {name: set(columns[name].groups) for name in eligible})
    for family in placed:
        if not _floored(family.table, floor):
            refused += [(family.child, -1, "")]
    if refused:
        notes += [f"the chain's own check found {len(refused)} refusals"]
        return _off("the chain's own check failed", counts, notes, content)
    inputs = moment_inputs(placed, scales, columns, moment_blocks, floor)
    for key, name in (("moment_region_columns", "codes"), ("moment_offers", "offers"), ("moment_regions", "regions"), ("moment_sums", "sums")):
        listed = inputs[name]
        counts[key] = len(listed) if isinstance(listed, list) else 0
    words, implied = rules.words_of(eligible, placed)
    chain_entries: "list[dict[str, object]]" = []
    for family in placed:
        sizes = rules.radices(family, scales)
        width = len(family.table) // sizes[0]
        rows_written = [list(family.table[row * sizes[0] : (row + 1) * sizes[0]]) for row in range(width)]
        chain_entries += [
            {
                "anchor": family.anchor,
                "child": family.child,
                "level": rules.LEVELS[family.level],
                "parents": [{"column": name, "level": rules.LEVELS[level]} for name, level in family.parents],
                "slopes": None,
                "table": rows_written,
            }
        ]
    statistical: "dict[str, object]" = {
        "chain": chain_entries,
        "ineligible": ineligible,
        "ladder": [rules.published_ladder(scales[name]) for name in eligible],
        "moments": None,
        "not_carried": implied,
        "procedure": rules.procedure_record(tabled),
        "rules": [],
        "withheld": [],
        "words": words,
    }
    if seeds:
        notes += [f"the screen offered {len(seeds)} seeds as weights"]
    chosen = tuple((family.child, tuple(name for name, _level in family.parents), tuple(level for _name, level in rules.members(family))) for family in placed)
    return Chained(statistical, tuple(notes), counts, seeds, chosen, content, inputs)
