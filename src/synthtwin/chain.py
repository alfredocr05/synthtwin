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
patient-layer object itself: a table whose settings name a person
column is handed to the patient layer (`patient_layer`, contract 4.6c,
lane GRa), and a table whose subject question is open gets no chain,
since the table layer's proof is for one row per patient. Lane MR's rule inference is
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
import typing

from synthtwin import chain_moments as moments
from synthtwin import chain_order
from synthtwin import chain_rules as rules
from synthtwin import calendar_rules, date_counts, parsing, reading, taxonomy

# The reasons a whole chain is not published although the switch is on,
# each told in the private notes only (inventory rows 4 and 34).
OFF_PERSON = "a declared person column: the patient layer's (lane MG), not the table layer's"
OFF_HELD_REPEATS = (
    "a column held or declared as an identifier repeats a value and nothing published says each row "
    "is another person: the table may hold several rows per person"
)
# THE SUBJECT QUESTION'S HOLD (lane GRa, plan P4-D449; plan P4-D418 limit
# (3)): while the question whether one person may stand on several rows is
# open, or answered with no column naming the person, no chain is drawn.
OFF_SUBJECT = "the question whether one person may stand on several rows is open"
OFF_NO_PERSON = "one person may stand on several rows and no column names the person"

# What a switched run knows of who each row is about (`ChainSwitch.rows_per_person`).
ROWS_UNASKED = ""
ROWS_OPEN = "open"
ROWS_ONE = "one row each"
ROWS_UNNAMED = "several rows, no column names the person"
ROWS_PERSON = "the settings' person column identifies the person"
OFF_RECOUNT = "a column's recount disagreed with its published counts"
OFF_FEW = "fewer than two eligible columns"
OFF_ROOT = "the root step drew no family"

FEW_LEVELS = 8
SCREEN_ALL = 10
SCREEN_FEW = 3
SCREEN_ROUNDS = 6
# THE SCREEN'S BOUND (4.6b.3, amended 2026-11-01, lane CHa2): the triples it
# counts, every one up to 50 eligible columns (`C(50, 3)`), and past them a
# list read from positions and published classes alone; half of the budget
# goes first to the few-level class.
SCREEN_TRIPLES = 19600
SCREEN_FEW_TRIPLES = 9800

# THE STAGE PROBE (lane CHs, plan P4-D462): `describe` calls `_probed` by
# its written-out name at the end of each of its stages, with the stage's
# name and its work counters. Here it does nothing; a measurement driver
# puts its own reading of the clocks and the memory counters in its place
# (`tools/measurements/kpi_chain_describe_scale.py`, K-S6-15). Nothing
# returned or published reads it.


def _probed(stage: str, counts: "dict[str, int]") -> None:
    """The end of a stage of `describe`: nothing, unless a measurement driver stands here."""


@dataclasses.dataclass(frozen=True)
class ChainSwitch:
    """The switch the product does not expose: the table's name and the installation's key.

    `name` is the person's name for the dataset (`--name`, by default the
    input file's name without its extension; 4.6b.4); `key` the
    installation's 32-byte private key (`installation.key_of`). The key is
    read here and handed to the draw's words alone. `add` and `drop` are
    the pairs the questions file asked for (its `between_columns` entry,
    repair 2 of lane CHa, Codex's item 6): a pair to add is offered to
    the draw with the rule weight's raise (`w_rule`, a weight only, never
    forced); a pair to drop shares no family table (no option places one
    of its columns as a parent of the other).
    """

    name: str
    key: bytes = dataclasses.field(repr=False)
    held: "tuple[str, ...]" = ()
    add: "tuple[tuple[str, str], ...]" = ()
    drop: "tuple[tuple[str, str], ...]" = ()
    # THE SUBJECT QUESTION (lane GRa, plan P4-D449): `ROWS_OPEN`, the
    # default, while nothing has said who each row is about, and
    # `ROWS_UNNAMED` where an answer says no column names the person (no
    # chain and no patient layer either way); `ROWS_ONE` where it says each
    # row is a different person; `ROWS_PERSON` where the settings' person
    # column is said to identify the person; and `ROWS_UNASKED` only where a
    # caller states in its own line that it measures the walk beside a
    # repeating column (the chain's drivers: no command reaches it).
    rows_per_person: str = ROWS_OPEN
    # The columns the person question's open answer holds (`held` holds
    # them too): under `ROWS_ONE` every other repeating held column stays
    # held and ineligible, and these still hold the chain back.
    held_by_person: "tuple[str, ...]" = ()
    # WHAT THE ROW DESCRIPTION WAS TOLD, for the patient table's: every
    # rule it applied holds the patient-fixed columns too (`profile.build_document`).
    safe_harbor_no: "tuple[str, ...]" = ()
    unanswered: "tuple[str, ...]" = ()
    rare_values_released: bool = True
    # Lane SH2's reference year (years showing an age over 89 pooled, plan
    # P4-D434) and lane UN-1b's columns answered `keep` (plan P4-D443), as
    # the row description was told them.
    harbor_year: int = 0
    kept_identities: "tuple[str, ...]" = ()
    # THE RULE STEPS (contract 4.6b.7; lane RO, plan P4-D459), behind the
    # switch and off unless a caller asks: a description carrying a rule
    # writes its computed columns' blocks in `columns` (`with_rules`), which
    # every writer of a switched description must do before it is read;
    # lane CHON turns the rule steps on with the chain.
    rules: bool = False


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
    # THE PATIENT LAYER (contract 4.6c; lane GRa, plan P4-D449): `grain`
    # where it stands, and every column block as it then publishes them.
    grain: "dict[str, object] | None" = None
    columns: "list[dict[str, object]] | None" = None
    # A carried rule's computed column's block (contract 4.6b.7, MR.6 (a)),
    # by name: the caller writes it in the column's place in `columns`
    # (`with_rules`). Empty where no rule is carried.
    computed: "tuple[tuple[str, dict[str, object]], ...]" = ()
    # THE SELF-TEST'S INPUTS (lane ST, plan P4-D458): what the self-test
    # L2b reads, never published and never written (`SelftestInputs`);
    # None where no chain is published.
    selftest: "SelftestInputs | None" = None


# The page's names (contract 4.6b.7, MR.12): lanes RD and RZ call these.
infer_rules = chain_order.infer_rules
computed_block = chain_order.computed_block


@dataclasses.dataclass(frozen=True)
class SampleColumn:
    """One eligible column on the self-test's sample rows (lane ST, plan P4-D458), never published.

    `l0` is each sampled row's `L0` band code, in sample order; `linear`,
    `second` and `has` a FINE column's value codes and reading map on the
    same rows (4.6d.1), None elsewhere (`second` None where the column is
    not skewed); `binary` a binary's two `L0` value bands (read 0 and 1,
    `chain_moments.binary_levels`); `missing` the `L0` band holding the
    column's empty cells, -1 where none does; `skew` the quantile skew
    `(p90 + p10 - 2 p50) / (p90 - p10)` read from the published rungs
    (BC-ARCH inventory row 23), None where they do not give one; `lo` and
    `hi` the linear code's clip values (4.6d.1); `beyond` the sample rows
    (places in sample order) whose reading lies beyond the clip, each with
    its reading, from which the self-test reads its RAW SCALE (LANE ST
    RULINGS 5 (2)): inside the clip a reading is read at its code's
    mid-point, within half of 1/256 of the clip's span.
    """

    name: str
    role: str
    ladder: rules.Ladder
    l0: "bytes | list[int]"
    linear: "bytes | None"
    second: "bytes | None"
    has: "bytes | None"
    binary: "tuple[int, int] | None"
    missing: int
    skew: "float | None"
    lo: "float | None"
    hi: "float | None"
    beyond: "dict[int, float] | None" = None


@dataclasses.dataclass(frozen=True)
class SelftestInputs:
    """What the self-test L2b reads (contract 4.6b.8; lane ST, plan P4-D458), never published.

    `rows` is the table's tabled rows `n`; `hashes` each sampled row's
    content hash read as a whole number from its first 8 bytes, in sample
    order (the SplitMix64 words are keyed by them); `columns` each
    eligible column on the sample rows, in schema order; `families` the
    placed families in chain order (their tables counted on every tabled
    row, as published); `pairs` the time-and-event pairs, each as
    `(time, event)`. Held in memory only: nothing here is written to a
    file, a log or the description.
    """

    rows: int
    hashes: "tuple[int, ...]"
    columns: "tuple[SampleColumn, ...]"
    families: "tuple[rules.Family, ...]"
    pairs: "tuple[tuple[str, str], ...]"


@dataclasses.dataclass(frozen=True)
class Column:
    """One eligible column read for the chain: its ladder, its codes, its groups."""

    name: str
    ladder: rules.Ladder
    # `L0`'s codes, one byte a row; `L1` and `L2` read from them through the
    # ladder's maps where None (`_level_codes`; lane CHs, plan P4-D462).
    codes: "tuple[bytes | list[int], bytes | list[int] | None, bytes | list[int] | None]"
    groups: "frozenset[int]"
    screen: bytes
    screen_levels: int
    few: bool
    blank: int
    value_codes: "tuple[bytes, bytes | None, bytearray] | None" = None
    # The self-test's sample rows (places in sample order) whose reading
    # lies beyond the clip, each with its reading (lane ST, plan P4-D458):
    # never published.
    beyond: "dict[int, float] | None" = None


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
    kept: "list[tuple[list[str], dict[str, tuple[str, float | None, str]]]] | None" = None,
    spellings_kept: "taxonomy.KeptSpellings | None" = None,
) -> "dict[str, tuple[str, object]]":
    """Each distinct cell text read as 4.6b.2's starting bands read it.

    Returns text -> (kind, reading): `missing`; `other` (a present cell
    holding no reading of the value bands); `labels`; `value` with the
    reading in the column's own order (a number, a canonical date, a
    clock ordinal); `level` with the published label; `pool`.

    `kept`, where given, receives the cells and the spellings read (lane
    RO); `spellings_kept` is the description's own reading of the column
    (`taxonomy.KeptSpellings`, lane CHs, plan P4-D462), which
    `taxonomy.spellings_read` takes only where it was read under every
    argument it reads under here. The two lanes each named theirs `kept`;
    batch 4q's merge renamed lane CHs's.
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
        kept=spellings_kept,
    )
    if kept is not None:
        kept += [(values, spelled)]
    out: "dict[str, tuple[str, object]]" = {}
    present: "list[str]" = []
    for text in spelled:
        if spelled[text][0] == "missing":
            out[text] = ("missing", None)
        else:
            present += [text]
    if role in (rules.ROLE_COUNT, rules.ROLE_CONTINUOUS, rules.ROLE_COMPOUND):
        for text in present:
            kind, number, _text = spelled[text]
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
            parsed = parsing.parse_datetime(spelled[text][2], form) if isinstance(form, str) else None
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


# -- THE CELLS AS THE DESCRIPTION READ THEM (batch 4p's fix round) -------
#
# The command describes many columns from cells it has CHANGED: the Safe
# Harbor age top-code with its placeholders set aside and a small top
# category pooled, the year top-code, dates in disguise held, a column
# counted absent; and it reads a comma it inferred as the decimal point.
# The published counts are those of the changed cells, made by the HIPAA
# rules. `described_cells` reads a column's cells as the description read
# them, by the same taxonomy functions in `profile.build_document`'s
# order, from the marks the published block carries and the document's
# own settings -- as the validator reads a checked file
# (`validation._top_coded_table` and its neighbours). The patient layer
# reads through it every column whose recount agrees, so no class,
# reading, band or position list it publishes reads a value the
# description held (Codex's review of batch 4p, item 1: a position list
# read the cells as the file wrote them and published ages of 91 and 92
# beside a description top-coded at 90). The row chain's own reader
# still reads the cells as the file wrote them, its recount the check:
# lane BT3a moves it onto these cells.


def declarations_read(
    document: "dict[str, object]",
    forced_codes: "list[str] | None",
    forced_measurements: "list[str] | None",
    forced_decimal_commas: "list[str] | None",
) -> "tuple[set[str], set[str], set[str]]":
    """The columns read as codes, as measurements and with a decimal comma: the caller's beside the description's own.

    The description publishes in its settings (`forced_codes`,
    `forced_measurements`, `forced_decimal_commas`) every column it read
    so -- among the commas, one it INFERRED from the cells (lane UN-1b,
    plan P4-D443), which no person declared and the command does not hand
    over -- and `_reading_of` reads a column under exactly these three
    (`stored_as`, the fourth thing it reads, is the reader's, never a
    declaration). Guarantees: a fixed function of the four; reads no
    cell. Raises nothing. No I/O.
    """
    settings_block = _get(document, "settings")
    found: "list[set[str]]" = []
    for key, given in (
        ("forced_codes", forced_codes),
        ("forced_measurements", forced_measurements),
        ("forced_decimal_commas", forced_decimal_commas),
    ):
        named = {f"{name}" for name in given or []}
        published = _get(settings_block, key) if isinstance(settings_block, dict) else None
        if isinstance(published, list):
            named |= {f"{name}" for name in published}
        found += [named]
    return found[0], found[1], found[2]


def _whole_mark(value: object) -> int:
    """A published mark (`top_coded`, `top_coded_year`, `top_category_pooled`) as a whole number, -1 where none is written."""
    return value if isinstance(value, int) and not isinstance(value, bool) else -1


def _plainly_absent(spellings: "list[str]", settings: taxonomy.Settings) -> "frozenset[str]":
    """The spellings every reading counts absent: blank, the package's vocabulary of nothing, a declared one (as the validator reads them)."""
    declared: "dict[str, bool]" = {}
    for spelling in settings.declared_missing_values:
        declared[parsing.trimmed(spelling)] = True
    return frozenset(
        one for one in spellings
        if not parsing.trimmed(one) or parsing.is_missing_text(one) or parsing.trimmed(one) in declared
    )


def described_cells(
    table: reading.Table,
    place: int,
    block: "dict[str, object]",
    settings: taxonomy.Settings,
    declared: "dict[str, bool]",
    stored_as: str,
    exact: bool = False,
) -> "list[str]":
    """One column's cells as its published block says the description read them (4.6b.2; 4.6c's reading in rows).

    In `profile.build_document`'s order, each step by the taxonomy
    function that made the description: (1) DATES IN DISGUISE HELD, where
    the block carries the remark `REMARK_DATED_VALUES_HELD`
    (`date_counts.dated_values_blanked`, ages kept up to 125 years in the
    unit of the column's mark: its `top_coded`, else its name's, else 90,
    as the validator reads it); (2) A COLUMN COUNTED ABSENT
    (`present_count_withheld`: every present cell blank); (3) THE AGE
    TOP-CODE, where the block carries `top_coded`: every value from the
    mark written as it (`taxonomy.top_coded_cells`, or
    `top_coded_cells_before_sh3` where the block records no pooling
    rule), the placeholders past 125 written blank
    (`age_placeholders_set_aside`), and a top category fewer than
    `top_category_pooled` rows -- or people of each column of
    `top_category_people`, read as `profile.subject_keys` reads them --
    hold written as the value below it (`top_category_pooled`); (4) THE
    YEAR TOP-CODE, where it carries `top_coded_year`
    (`year_top_coded_cells`). Each step skips the spellings the column's
    own reading counts absent and reads the comma of ``declared``
    (`declarations_read`: the description's own beside the caller's).

    ONCE A SPELLING. Each step is a function of a cell given inputs read
    off the column's different spellings, so the steps run once a
    different spelling and the cells are written through the map they
    make; the pool alone counts rows, read off each spelling's rows held
    at the floor (`top_category_pooled` decides on fewer than the floor),
    or off every row where it counts people. Where no step writes a cell
    blank or pools, the absent spellings are the ones every reading
    counts absent (`_plainly_absent`), and a recount that disagrees is
    read again (`read_as_described`); otherwise, and with ``exact``, the
    ones the column's own reading counts absent (`taxonomy.spellings_read`,
    as `build_document` reads them, after the dates are held again).

    Guarantees: a column whose block carries none of these marks is
    returned as `reading.column_values` gives it, the same list, so it is
    read byte for byte as before, as is one the steps leave whole;
    otherwise a new list of the same length, a fixed function of the
    arguments and the table's subject columns. Raises what `taxonomy`
    raises on a cell that is not text. No I/O.
    """
    values = reading.column_values(table, place)
    remarks = _get(block, "remarks")
    dated = isinstance(remarks, list) and taxonomy.rendered(taxonomy.REMARK_DATED_VALUES_HELD, ()) in remarks
    counted_absent = _get(block, "present_count_withheld") is True
    mark = max(_whole_mark(_get(block, "top_coded")), 0)
    year = max(_whole_mark(_get(block, "top_coded_year")), 0)
    if not (dated or counted_absent or mark or year):
        return values
    name = f"{_get(block, 'name')}"
    comma = declared["decimal_comma"]
    rows_of: "dict[str, int]" = {}
    for cell in values:
        rows_of[cell] = rows_of[cell] + 1 if cell in rows_of else 1
    spellings = [one for one in rows_of]
    if exact:
        spelled = taxonomy.spellings_read(
            values, name, settings, forced_code=declared["code"], forced_measurement=declared["measurement"],
            forced_decimal_comma=comma, stored_as=stored_as,
        )
        absent = frozenset(text for text in spelled if spelled[text][0] == "missing")
    else:
        absent = _plainly_absent(spellings, settings)
    image = spellings
    blanked = False
    if dated:
        unit_mark = mark if mark else (taxonomy.age_mark_named(name) or taxonomy.TOP_CODE)
        held = date_counts.dated_values_blanked(
            image, absent, taxonomy.TOP_CODE_REACH_CEILING * unit_mark / taxonomy.TOP_CODE
        )
        if held is not None:
            image = held
            blanked = True
            if exact:
                # ...and the steps below read the column as the description
                # read it again after its dates were held (`described_from`).
                dated_map = dict(zip(spellings, image))
                spelled = taxonomy.spellings_read(
                    [dated_map[cell] for cell in values], name, settings, forced_code=declared["code"],
                    forced_measurement=declared["measurement"], forced_decimal_comma=comma, stored_as=stored_as,
                )
                absent = frozenset(text for text in spelled if spelled[text][0] == "missing")
    if counted_absent:
        image = ["" if parsing.folded(one) and one not in absent else one for one in image]
        blanked = True
    pooled_here = False
    if mark:
        pooled = _whole_mark(_get(block, "top_category_pooled"))
        if pooled < 0:
            # A description written before lane SH3's repair records no
            # pooling rule and is read as it was made (P4-D454).
            coded = taxonomy.top_coded_cells_before_sh3(image, comma, absent)
        else:
            coded = taxonomy.top_coded_cells(image, comma, absent, mark)
        aside = taxonomy.age_placeholders_set_aside(coded, comma, absent, settings.small_cell_floor, mark)
        blanked = blanked or aside != coded
        coded = aside
        if pooled > 0:
            coded = _pooled(table, values, spellings, rows_of, coded, block, settings, comma, absent, pooled, mark)
            pooled_here = coded != aside
        image = coded
    if year:
        image = taxonomy.year_top_coded_cells(image, comma, absent, year)
    if not exact and (blanked or pooled_here):
        return described_cells(table, place, block, settings, declared, stored_as, True)
    if image == spellings:
        return values
    written = dict(zip(spellings, image))
    return [written[cell] for cell in values]


def _pooled(
    table: reading.Table,
    values: "list[str]",
    spellings: "list[str]",
    rows_of: "dict[str, int]",
    coded: "list[str]",
    block: "dict[str, object]",
    settings: taxonomy.Settings,
    comma: bool,
    absent: "frozenset[str]",
    pooled: int,
    mark: int,
) -> "list[str]":
    """`described_cells`'s third step's pool, each spelling's image beside ``spellings``.

    In rows: `taxonomy.top_category_pooled`, asked of each spelling once
    with a floor past the column's rows, writes every spelling of the top
    category as it would pool it (the largest value below the mark, first
    met, or the mark less one), and the category is pooled where the rows
    those spellings stand on are fewer than the floor (``pooled``), as the
    function decides on every row. In the people of each column of
    `top_category_people`, read as `profile.subject_keys` reads them, it
    is asked of every row.
    """
    people = _get(block, "top_category_people")
    holders: "list[list[str]]" = []
    for subject in people if isinstance(people, list) else []:
        for spot, column_name in enumerate(table.column_names):
            if column_name == subject:
                from synthtwin import profile

                holders += [profile.subject_keys(reading.column_values(table, spot), settings.declared_missing_values)]
                break
    if holders:
        image = dict(zip(spellings, coded))
        cells = [image[cell] for cell in values]
        found = taxonomy.top_category_pooled(cells, comma, absent, pooled, mark, holders)
        by_cell = dict(zip(values, found))
        return [by_cell[one] for one in spellings]
    found = taxonomy.top_category_pooled(coded, comma, absent, len(values) + 1, mark, None)
    top_rows = 0
    for at in range(len(spellings)):
        if found[at] != coded[at]:
            top_rows += rows_of[spellings[at]]
    return found if top_rows < pooled else coded


def read_as_described(
    table: reading.Table,
    place: int,
    block: "dict[str, object]",
    settings: taxonomy.Settings,
    declared: "dict[str, bool]",
    stored_as: str,
    blank_rows: int,
) -> "tuple[_Read | None, list[str]]":
    """A column read to its starting bands on its cells as its description read them (`described_cells`), and those cells.

    A recount that disagrees on the cells read with the plain absent
    spellings is read once more with the column's own (``exact``).
    """
    cells = described_cells(table, place, block, settings, declared, stored_as)
    found = read_column(table, place, block, settings, declared, stored_as, blank_rows, cells)
    if found is not None and found.agrees:
        return found, cells
    again = described_cells(table, place, block, settings, declared, stored_as, True)
    if again == cells:
        return found, cells
    return read_column(table, place, block, settings, declared, stored_as, blank_rows, again), again


@dataclasses.dataclass(frozen=True)
class _Read:
    """One column's starting bands, its rows' starting codes, and the recount."""

    start: rules.Starting
    codes: "bytearray | list[int]"
    agrees: bool
    blanks: bytearray
    linear: "bytes | None"
    second: "bytes | None"
    has_reading: bytearray
    readings: "tuple[tuple[object, int], ...]" = ()
    # A FINE column's rows whose reading lies beyond its clip (4.6d.1), each
    # with its reading as a float: what the self-test reads its raw scale
    # from (lane ST, plan P4-D458; LANE ST RULINGS 5 (2)). None elsewhere.
    beyond: "dict[int, float] | None" = None


def read_column(
    table: reading.Table,
    place: int,
    block: "dict[str, object]",
    settings: taxonomy.Settings,
    declared: "dict[str, bool]",
    stored_as: str,
    blank_rows: int,
    cells: "list[str] | None" = None,
    kept: "list[tuple[list[str], dict[str, tuple[str, float | None, str]]]] | None" = None,
    spellings_kept: "taxonomy.KeptSpellings | None" = None,
) -> "_Read | None":
    """One column read to its starting bands, row by row, through `reading.column_values`.

    ``cells``, where given, are the column's cells as its description
    read them (`described_cells`), read in place of the cells as the file
    wrote them.

    `kept`, where a caller passes it, receives the column's cells and its
    own reader's decision on each spelling, so the rule steps read the
    column from what this read (lane RO, plan P4-D459): nothing is read
    twice.

    `spellings_kept` is the description's own reading of the column,
    kept as the chain reads it (`taxonomy.KeptSpellings`; lane CHs, plan
    P4-D462): taken where it was read under every argument this reading
    reads under, so the column's spellings are what they would be read
    as here; never where `cells` stand in for the file's cells.
    """
    values = reading.column_values(table, place) if cells is None else cells
    start = rules.starting_bands(block, (True, True, True))
    if start is None:
        return None
    meaning = _reading_of(block, values, settings, declared, stored_as, kept, spellings_kept if cells is None else None)
    places = _starting_index(start)
    value_places = _value_places(start)
    role = f"{_get(block, 'role')}"
    # ONE BYTE A ROW (lane CHs, plan P4-D462): the rows of each distinct
    # text counted first, then each text's starting band and kind read once
    # and its kind counted by its rows, and each row's band looked up by its
    # text into one byte a row (a number a row where a column has more than
    # 256 starting bands); the blank cells are marked where a blank text
    # stands. The recount reads the same counts the first build's walk did.
    rows_of: "dict[str, int]" = {}
    for text in values:
        rows_of[text] = rows_of[text] + 1 if text in rows_of else 1
    code_of: "dict[str, int]" = {}
    kinds: "dict[str, int]" = {"missing": 0, "other": 0, "labels": 0, "value": 0, "pool": 0}
    agrees = True
    for text in meaning:
        kind, value = meaning[text]
        if kind == "missing":
            code = places[rules.MISSING]
            counted_as = "missing"
        elif kind == "other":
            code = places[rules.OTHER]
            counted_as = "other"
        elif kind == "labels":
            code = places[rules.LABELS]
            counted_as = "labels"
        elif kind == "pool":
            code = places[rules.POOL] if rules.POOL in places else -1
            counted_as = "pool"
        elif kind == "level":
            code = places[(value,)] if (value,) in places else -1
            counted_as = "value"
        else:
            index = rules.band_of_value(start.values, value)
            code = value_places[index] if index < len(value_places) else -1
            counted_as = "value"
        kinds[counted_as] += rows_of[text] if text in rows_of else 0
        if code < 0:
            agrees = False
            code = 0
        code_of[text] = code
    # A text the reading left without a band reads band 0 and counts in
    # nothing, and the recount disagrees, as the first build's walk did.
    unknown = [text for text in rows_of if text not in code_of]
    for text in unknown:
        agrees = False
        code_of[text] = 0
        del rows_of[text]
    codes: "bytearray | list[int]"
    if len(start.names) <= 256:
        codes = bytearray(code_of[text] for text in values)
    else:
        codes = [code_of[text] for text in values]
    blank_texts = {text for text in rows_of if _is_blank(text)}
    blanks = bytearray(1 if text in blank_texts else 0 for text in values) if blank_texts else bytearray(len(values))
    missing = _get(block, "n_missing")
    tabled_missing = (missing if isinstance(missing, int) else 0) - blank_rows
    if role in rules.LABEL_ROLES:
        # A published level's rows are its published count.
        counted: "dict[str, int]" = {}
        for text in rows_of:
            if meaning[text][0] == "level":
                label = f"{meaning[text][1]}"
                counted[label] = counted[label] + rows_of[text] if label in counted else rows_of[text]
        for label, count in rules.label_levels(block):
            if (counted[label] if label in counted else 0) != count:
                agrees = False
    agrees = agrees and _recount_agrees(block, kinds, tabled_missing, blank_rows)
    # THE MOMENT LAYER'S CODES (contract 4.6d.1), one byte a row, for a FINE
    # column: read here once, for the inputs `chain_moments` computes.
    linear: "bytes | None" = None
    second: "bytes | None" = None
    beyond: "dict[int, float] | None" = None
    has_reading = bytearray(len(values))
    found = moments.codes_of(block) if moments.fine(block) else None
    if found is not None:
        by_text: "dict[str, tuple[int, int]]" = {}
        # The readings beyond the clip, each as a float (the self-test's
        # raw scale, lane ST): a few rows a column, read in this one pass.
        beyond_text: "dict[str, float]" = {}
        for text in meaning:
            kind, value = meaning[text]
            if kind != "value":
                continue
            exact = moments.ordinal(role, value, block)
            if exact is None:
                continue
            by_text[text] = (moments.linear_code(found, exact), moments.second_code(found, exact))
            if exact < found.lo_value or exact > found.hi_value:
                beyond_text[text] = float(exact)
        first_codes = bytearray(len(values))
        second_codes = bytearray(len(values))
        beyond = {}
        for row in range(len(values)):
            if values[row] in by_text:
                pair = by_text[values[row]]
                first_codes[row] = pair[0]
                second_codes[row] = pair[1]
                has_reading[row] = 1
                if values[row] in beyond_text:
                    beyond[row] = beyond_text[values[row]]
        linear = bytes(first_codes)
        second = bytes(second_codes) if found.second is not None else None
    # Each value with its rows, ascending: what `value_run_bands` reads.
    by_value: "dict[object, int]" = {}
    for text in rows_of:
        kind, value = meaning[text]
        if kind == "value" and value is not None:
            by_value[value] = by_value[value] + rows_of[text] if value in by_value else rows_of[text]
    ordered: "list[object]" = sorted(by_value)  # type: ignore[type-var]
    readings = tuple((value, by_value[value]) for value in ordered)
    return _Read(start, codes, agrees, blanks, linear, second, has_reading, readings, beyond)


# -- OWN-FACT GROUPS READ ON THE COLUMN'S OWN VALUES (4.6b.3, amended by repair 1) --


# The most single values a run is read less of, one subset at a time; a run
# holding more is marked whole (it refuses more and never passes more).
RUN_POINTS_AT_MOST = 10

# The periodic censuses of a date, moment or clock column, and how many
# places one turn of each holds.
PERIODIC = (
    ("weekday_census", 7),
    ("day_of_month_census", 34),
    ("hour_census", 24),
    ("minute_census", 60),
    ("second_census", 60),
)

# How a census's bin is read off a reading (`_bin_of`).
BIN_HISTOGRAM = "histogram"
BIN_CLOCK = "clock"


def _first_index(keys: "list[object]", value: object, side: int) -> int:
    """How many readings stand below `value` (side 0) or at or below it (side 1)."""
    low = 0
    high = len(keys)
    while low < high:
        middle = (low + high) // 2
        one = keys[middle]
        before = rules.below(one, value) or (side == 1 and not rules.below(value, one))
        if before:
            low = middle + 1
        else:
            high = middle
    return low


def _bin_of(reading: object, kind: str, lowest: float, highest: float, step: int) -> int:
    """A reading's bin: C6-31f's division of `[lowest, highest]`, or a clock's bin of `step` units."""
    if kind == BIN_HISTOGRAM:
        number = _number(reading)
        return parsing.histogram_bin(number if number is not None else lowest, lowest, highest)
    if isinstance(reading, int) and not isinstance(reading, bool):
        return reading // step
    return 0


def _first_bin_at_least(keys: "list[object]", low: int, high: int, at: int, kind: str, lowest: float, highest: float, step: int) -> int:
    """The first place in `keys[low:high]` whose bin is `at` or above (bins never fall), else `high`."""
    while low < high:
        middle = (low + high) // 2
        if _bin_of(keys[middle], kind, lowest, highest, step) >= at:
            high = middle
        else:
            low = middle + 1
    return low


def _first_day_after(keys: "list[object]", day: str, strict: bool) -> int:
    """The first reading written on `day` or later (on a later day where `strict`)."""
    low = 0
    high = len(keys)
    while low < high:
        middle = (low + high) // 2
        written = f"{keys[middle]}"[:10]
        if written > day or (not strict and written == day):
            high = middle
        else:
            low = middle + 1
    return low


def _number(value: object) -> "float | None":
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _number_holder(block: "dict[str, object]") -> "dict[str, object]":
    role = _get(block, "role")
    holder: object = block
    if role == rules.ROLE_JOINED:
        parts = _get(block, "parts")
        holder = parts[0] if isinstance(parts, list) and parts else {}
    elif role == rules.ROLE_COMPOUND:
        holder = _get(block, "numbers")
    return holder if isinstance(holder, dict) else {}


def _run_of(keys: "list[object]", value: object) -> "tuple[int, int] | None":
    """The readings equal to `value`, as a run of places, or None where none is."""
    if value is None:
        return None
    low = _first_index(keys, value, 0)
    high = _first_index(keys, value, 1)
    return (low, high) if low < high else None


@dataclasses.dataclass(frozen=True)
class _Places:
    """Where a column's readings stand among its `L0` bands."""

    keys: "list[object]"
    values: "tuple[object, ...]"
    value_starts: "list[int]"
    l0_of_start: "dict[int, int]"


def _band_at(places: _Places, index: int) -> "set[int]":
    """The `L0` band holding the reading at `index`."""
    found = rules.band_of_value(places.values, places.keys[index])
    if found < len(places.value_starts) and places.value_starts[found] in places.l0_of_start:
        return {places.l0_of_start[places.value_starts[found]]}
    return set()


def _bands_between(places: _Places, low: int, high: int) -> "set[int]":
    """Every `L0` band holding a reading of `keys[low:high]`."""
    if low >= high:
        return set()
    out = _band_at(places, low)
    for edge in places.values:
        at = _first_index(places.keys, edge, 0)
        if low < at < high:
            out = out | _band_at(places, at)
    return out


def _periodic_place(key: str, reading: object, role: str, seconds: bool) -> "int | None":
    """A reading's place in one turn of a periodic census, or None where it has none."""
    if role == rules.ROLE_CLOCK:
        if not isinstance(reading, int) or isinstance(reading, bool):
            return None
        minutes = reading // 60 if seconds else reading
        if key == "minute_census":
            return minutes % 60
        if key == "second_census":
            return reading % 60 if seconds else None
        return None
    if not isinstance(reading, str) or len(reading) < 10:
        return None
    try:
        if key == "weekday_census":
            return calendar_rules.weekday_of(calendar_rules.written_day(reading))
        if key == "day_of_month_census":
            year, month, day = int(reading[0:4]), int(reading[5:7]), int(reading[8:10])
            return calendar_rules.month_bin_of(day, calendar_rules.month_length(year, month)) - 1
        if len(reading) < 13:
            return None
        if key == "hour_census":
            return int(reading[11:13])
        if key == "minute_census" and len(reading) >= 16:
            return int(reading[14:16])
        if key == "second_census" and len(reading) >= 19:
            return int(reading[17:19])
    except ValueError:
        return None
    return None


def _turn_groups(census: "list[object]", places: int, from_one: bool) -> "tuple[list[int], list[int]] | None":
    """Each place's group in one turn (a group may wrap), and each group's count; None where unread."""
    where = [-1] * places
    counts: "list[int]" = []
    for index in range(len(census)):
        group = census[index]
        if not isinstance(group, dict):
            return None
        first = _get(group, "first")
        last = _get(group, "last")
        count = _get(group, "count")
        if not isinstance(first, int) or not isinstance(last, int) or not isinstance(count, int):
            return None
        at = first - (1 if from_one else 0)
        end = last - (1 if from_one else 0)
        steps = 0
        while 0 <= at < places and steps <= places:
            where[at] = index
            if at == end:
                break
            at = (at + 1) % places
            steps += 1
        counts += [count]
    return where, counts


def _census_cuts(
    keys: "list[object]",
    groups: "list[object]",
    span: "tuple[int, int]",
    kind: str,
    lowest: float,
    highest: float,
    step: int,
) -> "set[int] | None":
    """Where a census of value ranges changes group inside `span`; None where its groups are unread."""
    out: "set[int]" = set()
    for at in range(1, len(groups)):
        group = groups[at]
        first = _get(group, "first") if isinstance(group, dict) else None
        if not isinstance(first, int) or isinstance(first, bool):
            return None
        out = out | {_first_bin_at_least(keys, span[0], span[1], first, kind, lowest, highest, step)}
    return out


def _named_points(block: "dict[str, object]", role: str, form: object, keys: "list[object]") -> "list[tuple[int, int]]":
    """The runs of readings a published count names one value (or one day) of, each once.

    The named values are the mode, nought, a number tail's listed values,
    a clock heap, a date or clock tail's listed values, and a heavy date
    (the whole day). `value_run_bands` reads a run less any of them, a
    named value of few rows, and whether every other reading is single.
    """
    singles: "list[object]" = []
    if role in rules.NUMBER_ROLES:
        holder = _number_holder(block)
        mode_count = _get(holder, "mode_count")
        if isinstance(mode_count, int) and not isinstance(mode_count, bool) and mode_count > 0:
            singles += [_number(_get(holder, "mode"))]
        n_zero = _get(holder, "n_zero")
        if isinstance(n_zero, int) and not isinstance(n_zero, bool) and n_zero > 0:
            singles += [0.0]
        tails = _get(holder, "tails")
        if isinstance(tails, dict):
            for name in ("low", "high"):
                tail_side = _get(tails, name)
                listed = _get(tail_side, "values") if isinstance(tail_side, dict) else None
                if isinstance(listed, list):
                    for one in listed:
                        singles += [_number(one)]
    if role == rules.ROLE_CLOCK:
        heaps = _get(block, "clock_heaps")
        if isinstance(heaps, list):
            for heap in heaps:
                text = _get(heap, "value") if isinstance(heap, dict) else None
                if isinstance(text, str):
                    singles += [rules.rung_value(role, text, form)]
    if role in (rules.ROLE_DATETIME, rules.ROLE_CLOCK):
        for name in ("low_tail", "high_tail"):
            tail = _get(block, name)
            listed = _get(tail, "values") if isinstance(tail, dict) else None
            if isinstance(listed, list):
                for one in listed:
                    singles += [rules.rung_value(role, one, form) if isinstance(one, str) else one]
    points: "list[tuple[int, int]]" = []
    for single in singles:
        run = _run_of(keys, single)
        if run is not None and run not in points:
            points += [run]
    if role == rules.ROLE_DATETIME:
        heavy = _get(block, "heavy_dates")
        if isinstance(heavy, list):
            for entry in heavy:
                day = _get(entry, "date") if isinstance(entry, dict) else None
                if isinstance(day, str) and len(day) == 10:
                    run = (_first_day_after(keys, day, False), _first_day_after(keys, day, True))
                    if run[0] < run[1] and run not in points:
                        points += [run]
    return points


def value_run_bands(
    block: "dict[str, object]",
    start: rules.Starting,
    ladder: rules.Ladder,
    floor: int,
    readings: "tuple[tuple[object, int], ...]",
) -> "set[int]":
    """The `L0` bands holding an own-fact group the published facts draw through the column's own values.

    Every published fact of one ordered column that splits its values is
    a CUT: each published rung, each `L0` edge, a date or clock tail's
    boundary, and each edge where a census of value ranges changes group
    (`bin_groups` by the tail block's division, `value_histogram` by the
    published ends, `clock_census` by its ten-minute bins). The readings
    between two neighbouring cuts form a RUN, and a run's count is a
    difference of two counts a reader can put together, so a run holding
    1 to `floor - 1` rows is an own-fact group; so is a run less any of
    the single values a published count names inside it (the mode, nought,
    a clock heap, a heavy date, a tail's listed value), and so is such a
    value counted 1 to `floor - 1` itself. A periodic census (days of the
    week or month, hours, minutes, seconds) marks the body's bands outside
    a run of neighbouring bands that holds all but 1 to `floor - 1` rows
    of the groups it reaches (those rows lie there), and marks a run's
    bands where the groups lying wholly inside it leave 1 to `floor - 1`
    of its rows. The counts are
    read on the column's own values (`readings`, each reading with its
    rows, ascending; repair 1 of lane CHa, skeptic 1's item 1). A rung
    draws a cut where the published facts fix the rank it stands at: a
    rung no row stands on (the rank its percent sets), and a rung exactly
    one row stands on where every reading other than the single values a
    published count names holds one row (the distinct count then tells a
    reader every other value is single, so the rung's row has a rank the
    reader holds; it cuts on both sides of that row; repair 2, the
    verify's item 1, measured: a 501-row column all different but a mode
    of 12, or eleven noughts, published five-row percent slices confined
    to one gender on 8 of 8 keys before it). A rung tied rows stand on
    whose tie count no published fact names is no cut: the rows below it
    and through it are open to a reader, and reading it as a cut refused
    the registry's censor date beside its event date at 5,000 rows on a
    run whose count no published fact fixes. Cutting at every one-row
    rung instead cost lane E0b's ST3 37.06 % of its score at 20,000 rows
    (the verify's variant) and is not done.
    """
    role = f"{_get(block, 'role')}"
    if role not in rules.ORDERED_ROLES or not readings or not start.values:
        return set()
    keys = [one[0] for one in readings]
    sums = [0]
    for one in readings:
        sums += [sums[-1] + one[1]]
    total = len(keys)
    l0_of_start: "dict[int, int]" = {}
    for at in range(len(ladder.l0)):
        for name in ladder.l0[at]:
            for place in range(len(start.names)):
                if start.names[place] == name:
                    l0_of_start[place] = at
    value_starts = [place for place in range(len(start.names)) if start.value[place]]
    every_value = {l0_of_start[place] for place in value_starts if place in l0_of_start}
    places = _Places(keys, start.values, value_starts, l0_of_start)
    form = _get(block, "clock_form")
    seconds = isinstance(form, str) and "-mm-ss" in form
    cuts: "set[int]" = {0, total}
    for edge in start.values:
        cuts = cuts | {_first_index(keys, edge, 0)}
    rungs = rules.rung_ladder(block)
    points = _named_points(block, role, form, keys)
    # Every reading other than the single values a published count names
    # holds one row: the column's distinct count then tells a reader that
    # every other value is single (n_distinct_values = rows - mode_count + 1,
    # or the like for nought, a tail's listed values, a clock heap or a
    # heavy date), so a rung one row stands on has a rank the reader holds.
    covered: "set[int]" = set()
    for pair in points:
        covered |= set(range(pair[0], pair[1]))
    rest_single = all(readings[at][1] == 1 for at in range(total) if at not in covered)
    if isinstance(rungs, dict):
        for name in rungs:
            value = rules.rung_value(role, _get(rungs, name), form)
            if value is None:
                continue
            # A rung no row stands on reads the rank its percent sets, so the
            # rows below it are a count a reader holds. Where every reading
            # but the named single values holds one row, a rung one row
            # stands on holds that row's rank too (its own value printed),
            # so it cuts on both sides of that row. Where rows may tie
            # unnamed, a rung a row stands on leaves both counts open: no cut.
            below = _first_index(keys, value, 0)
            through = _first_index(keys, value, 1)
            held_at = sums[through] - sums[below]
            if held_at == 0:
                cuts = cuts | {below}
            elif held_at == 1 and rest_single:
                cuts = cuts | {below, through}
    marked: "set[int]" = set()
    body = (0, total)
    if role in (rules.ROLE_DATETIME, rules.ROLE_CLOCK):
        ends: "list[int]" = []
        for name, side in (("low_tail", 0), ("high_tail", 1)):
            tail = _get(block, name)
            boundary = _get(tail, "boundary") if isinstance(tail, dict) else None
            value = rules.rung_value(role, boundary, form) if isinstance(boundary, str) else None
            if value is not None:
                ends += [_first_index(keys, value, side)]
                cuts = cuts | {ends[-1]}
        if len(ends) == 2:
            body = (ends[0], ends[1])
    if role in rules.NUMBER_ROLES:
        holder = _number_holder(block)
        groups = _get(holder, "bin_groups")
        tails = _get(holder, "tails")
        if isinstance(groups, list) and groups:
            ends_read: "tuple[float, float] | None" = None
            if isinstance(tails, dict) and isinstance(rungs, dict):
                low_side = _get(tails, "low")
                high_side = _get(tails, "high")
                if isinstance(low_side, dict) and isinstance(high_side, dict):
                    low_percent = _get(low_side, "percent")
                    high_percent = _get(high_side, "percent")
                    if isinstance(low_percent, int) and isinstance(high_percent, int):
                        lowest = _number(_get(rungs, f"p{low_percent:02d}"))
                        highest = _number(_get(rungs, f"p{high_percent:02d}"))
                        if lowest is not None and highest is not None and highest > lowest:
                            ends_read = (lowest, highest)
            found = None
            if ends_read is not None:
                span = (_first_index(keys, ends_read[0], 0), _first_index(keys, ends_read[1], 1))
                cuts = cuts | set(span)
                found = _census_cuts(keys, groups, span, BIN_HISTOGRAM, ends_read[0], ends_read[1], 1)
            if found is None:
                marked = marked | every_value
            else:
                cuts = cuts | found
        histogram = _get(holder, "value_histogram")
        if isinstance(histogram, dict) and histogram:
            low_end = _number(_get(rungs, "min")) if isinstance(rungs, dict) else None
            high_end = _number(_get(rungs, "max")) if isinstance(rungs, dict) else None
            if low_end is None or high_end is None or not high_end > low_end:
                marked = marked | every_value
            else:
                span = (_first_index(keys, low_end, 0), _first_index(keys, high_end, 1))
                cuts = cuts | set(span)
                every_bin: "list[object]" = [{"first": at} for at in range(parsing.HISTOGRAM_BINS)]
                found = _census_cuts(keys, every_bin, span, BIN_HISTOGRAM, low_end, high_end, 1)
                cuts = cuts | (found or set())
    if role == rules.ROLE_CLOCK:
        census = _get(block, "clock_census")
        if isinstance(census, list) and census:
            found = _census_cuts(keys, census, body, BIN_CLOCK, 0.0, 0.0, 600 if seconds else 10)
            if found is None:
                marked = marked | every_value
            else:
                cuts = cuts | found
    ordered_cuts = sorted(cuts)
    for at in range(len(ordered_cuts) - 1):
        low = ordered_cuts[at]
        high = ordered_cuts[at + 1]
        rows = sums[high] - sums[low]
        if rows <= 0:
            continue
        inside = [pair for pair in points if low <= pair[0] and pair[1] <= high]
        if 0 < rows < floor or len(inside) > RUN_POINTS_AT_MOST:
            marked = marked | _band_at(places, low)
            continue
        sizes = [sums[pair[1]] - sums[pair[0]] for pair in inside]
        for chosen in range(1, 1 << len(sizes)):
            left = rows
            for place in range(len(sizes)):
                if chosen >> place & 1:
                    left -= sizes[place]
            if 0 < left < floor:
                marked = marked | _band_at(places, low)
                break
    for pair in points:
        size = sums[pair[1]] - sums[pair[0]]
        if 0 < size < floor:
            marked = marked | _bands_between(places, pair[0], pair[1])
    if role in (rules.ROLE_DATETIME, rules.ROLE_CLOCK):
        marked = marked | _periodic_marks(block, role, seconds, places, readings, body, floor, every_value)
    return marked


def _periodic_marks(
    block: "dict[str, object]",
    role: str,
    seconds: bool,
    places: _Places,
    readings: "tuple[tuple[object, int], ...]",
    body: "tuple[int, int]",
    floor: int,
    every_value: "set[int]",
) -> "set[int]":
    """The bands a periodic census marks beside the value bands (`value_run_bands`)."""
    marked: "set[int]" = set()
    for heaps in ("minute_heaps", "second_heaps"):
        if _get(block, heaps) not in (None, []):
            return set(every_value)
    keys = places.keys
    edges = [_first_index(keys, edge, 0) for edge in places.values]
    starts = [body[0]] + [min(max(at, body[0]), body[1]) for at in edges] + [body[1]]
    for key, turn in PERIODIC:
        census = _get(block, key)
        if not isinstance(census, list) or not census:
            continue
        read = _turn_groups(census, turn, key == "day_of_month_census")
        if read is None:
            return set(every_value)
        where, counts = read
        bands = len(starts) - 1
        rows_in = [0] * bands
        reach: "list[set[int]]" = [set() for _band in range(bands)]
        lowest = [bands] * len(counts)
        highest = [-1] * len(counts)
        seen = [0] * len(counts)
        for band in range(bands):
            for index in range(starts[band], starts[band + 1]):
                place = _periodic_place(key, keys[index], role, seconds)
                if place is None or not 0 <= place < turn or where[place] < 0:
                    return set(every_value)
                group = where[place]
                rows_in[band] += readings[index][1]
                seen[group] += readings[index][1]
                reach[band] = reach[band] | {group}
                lowest[group] = min(lowest[group], band)
                highest[group] = max(highest[group], band)
        if seen != counts:
            return set(every_value)
        for first in range(bands):
            reached: "set[int]" = set()
            rows = 0
            for last in range(first, bands):
                reached = reached | reach[last]
                rows += rows_in[last]
                # The reached groups' rows outside the run lie in the body's
                # other bands: those bands hold the group the count fixes.
                outside = sum(counts[group] for group in reached) - rows
                if 0 < outside < floor:
                    marked = marked | _bands_between(places, starts[0], starts[first]) | _bands_between(places, starts[last + 1], starts[bands])
                held = sum(counts[group] for group in range(len(counts)) if counts[group] and first <= lowest[group] and highest[group] <= last)
                if 0 < rows - held < floor:
                    marked = marked | _bands_between(places, starts[first], starts[last + 1])
    return marked


# -- THE CONTENT HASH AND THE SELF-TEST SAMPLE (4.6b.8) ------------------


def row_hash_buffer(table: reading.Table) -> "tuple[bytearray, bytearray]":
    """Each row's CONTENT HASH, 32 bytes a row in ONE buffer, and which rows hold nothing in every column.

    THE CELL-BY-CELL FORM (4.6b.8 as amended by lane CHa's repair 2,
    Codex's item 4). Each cell is written as the column name's UTF-8
    bytes and the cell's text's UTF-8 bytes, each of the two preceded by
    its own length in bytes as 8 bytes big-endian (the length framing of
    4.6b.8), and hashed alone: BLAKE2b (`digest_size=32`,
    `person=b"synthtwin.cel.1"`). A row's cell hashes, read as big-endian
    whole numbers, are summed modulo `2**256`, and the sum's 32 bytes are
    hashed once more: BLAKE2b (`digest_size=32`,
    `person=b"synthtwin.row.2"`). The sum is free of column order, as
    the name order of the first form was. A cell holding nothing (spaces
    and tabs alone, `_is_blank`) is framed as the empty text, as 4.6b.8
    states; the first build framed it as written, so a blank cell given a
    space made a second table of the ledger's one (lane CHb's second
    repair, Codex's item 4). The cells are the reader's own
    (`reading.column_values`), so a CSV and a workbook of one table give
    one hash, and the walk takes the table's columns group by group
    (`reading.column_groups`), each group read once, holding one whole
    number a row: the first form held a table read in groups as its
    framed rows at once (about 1.25 kB a row at 50 columns, MEASURED;
    3.2 GB of payload at 2,000,000 x 50 by Codex's count, over the
    2.5 GB watchdog by itself). The finished hashes stand in one buffer,
    row `r`'s at bytes `32 r` to `32 r + 32` (lane CHs, plan P4-D462: a
    list of hashes held a Python object of about 80 bytes a row).
    """
    names = list(table.column_names)
    rows = table.n_rows
    filled = bytearray(rows)
    sums = [0] * rows
    for first, last in reading.column_groups(table):
        for place in range(first, last):
            name_bytes = bytes(names[place], "utf-8")
            head = _length_word(len(name_bytes)) + name_bytes
            values = reading.column_values(table, place)
            for row in range(rows):
                text = values[row]
                blank = _is_blank(text)
                # A CELL HOLDING NOTHING IS THE EMPTY TEXT (4.6b.8): `""` and
                # `" \t"` frame alike (lane CHb's second repair, Codex's item 4).
                cell = b"" if blank else bytes(text, "utf-8")
                digest = hashlib.blake2b(head + _length_word(len(cell)) + cell, digest_size=32, person=b"synthtwin.cel.1").hexdigest()
                sums[row] += int(digest, 16)
                if not filled[row] and not blank:
                    filled[row] = 1
    held = bytearray(32 * rows)
    for row in range(rows):
        total = _bytes32(sums[row] % (1 << 256))
        sums[row] = 0
        held[32 * row : 32 * row + 32] = hashlib.blake2b(total, digest_size=32, person=b"synthtwin.row.2").digest()
    return held, filled


def row_hashes(table: reading.Table) -> "tuple[list[bytes], bytearray]":
    """Each row's content hash as its own 32 bytes (`row_hash_buffer`'s, row by row), and which rows hold nothing."""
    held, filled = row_hash_buffer(table)
    return [bytes(held[32 * row : 32 * row + 32]) for row in range(table.n_rows)], filled


def _bytes32(value: int) -> bytes:
    """A whole number below `2**256` written in 32 bytes, big-endian."""
    return bytes([(value >> (8 * (31 - at))) & 255 for at in range(32)])


def content_hash(hashes: "list[bytes] | bytearray", filled: "bytearray | None" = None) -> bytes:
    """The table's content hash: its rows' hashes summed modulo 2**256, written in 32 bytes.

    A row blank in every column is left out where `filled` marks it
    (4.6b.8 as amended by repair 1: a record holding nothing adds no
    content, so one more empty record does not make a second table of a
    table the ledger knows).
    """
    total = 0
    for row in range(_hash_count(hashes)):
        if filled is not None and not filled[row]:
            continue
        total = (total + rules.big_endian(_hash_at(hashes, row))) % (1 << 256)
    return _bytes32(total)


def _hash_count(hashes: "list[bytes] | bytearray") -> int:
    """How many rows' hashes `hashes` holds: a list of them, or one buffer of 32 bytes a row."""
    return len(hashes) if isinstance(hashes, list) else len(hashes) // 32


def _hash_at(hashes: "list[bytes] | bytearray", row: int) -> bytes:
    """Row `row`'s 32-byte content hash, from a list of them or from one buffer of 32 bytes a row."""
    if isinstance(hashes, list):
        return hashes[row]
    return bytes(hashes[32 * row : 32 * row + 32])


def _rows_of(rows: int, excluded: "list[int]") -> "typing.Iterator[int]":
    """The tabled rows of a table of `rows` rows in row order: every row but the ones `excluded` lists (ascending).

    Nothing is held a row (lane CHs, plan P4-D462: the first build held a
    list of the tabled rows' places, a Python number each).
    """
    start = 0
    for row in excluded:
        yield from range(start, row)
        start = row + 1
    yield from range(start, rows)


def _rows_at(places: "list[int]", excluded: "list[int]") -> "list[int]":
    """The row of each tabled place in `places`, in their order: a table's rows but the ones `excluded` lists (ascending).

    One number a place, never one a row: what lane ST's self-test reads of
    its sample (plan P4-D458) beside lane CHs's tabled rows, which list
    only the rows set aside (plan P4-D462; batch 4q's merge). `places`
    are distinct places in the tabled rows (the sample's).
    """
    if not excluded:
        return list(places)
    rows = [0] * len(places)
    skipped = 0
    for place, at in sorted((places[at], at) for at in range(len(places))):
        while skipped < len(excluded) and excluded[skipped] <= place + skipped:
            skipped += 1
        rows[at] = place + skipped
    return rows


def _tabled_texts(texts: "list[str]", excluded: "list[int]") -> "list[str]":
    """A column's cells on the tabled rows alone, in row order: the cells themselves where no row is set aside.

    What lane RO's rule steps read the tabled rows from (plan P4-D459),
    beside lane CHs's tabled rows (plan P4-D462; batch 4q's merge): a
    list of the cells, made only where a record holding nothing is set
    aside, one column at a time.
    """
    if not excluded:
        return texts
    return [texts[row] for row in _rows_of(len(texts), excluded)]


def sample_rows(hashes: "list[bytes] | bytearray", tabled: "typing.Sequence[int]", size: int) -> "list[int]":
    """The self-test's sample: the `min(m, n)` tabled rows of smallest SAMPLE KEY, sorted by key.

    Each row's key is BLAKE2b (`digest_size=8`, `person=b"synthtwin.smp.1"`)
    over its content hash and its OCCURRENCE (the count of earlier rows
    of the same hash) as 8 bytes big-endian; equal keys are taken in
    order of content hash and then occurrence (4.6b.8). Returns places in
    `tabled` (indices into the tabled rows).

    MEMORY (lane CHs, plan P4-D462, beside lane ST's bounded heap of
    P4-D458). At most `min(m, n)` keyed entries are held, in a heap whose
    top is the largest entry kept: a row whose entry is not below the top
    is never held. Every entry is distinct (its place in `tabled` is its
    last part), so the `m` smallest are one set, and sorted they are the
    first build's rows in the first build's order. The occurrences are
    read without a dictionary over every row: a first walk marks each
    row's first 25 bits in one bit a mark, and a mark met twice in a
    second; a row whose mark no other row holds is the only row of its
    hash (occurrence 0), and only the rows of marks met twice are counted
    in a dictionary of their hashes, in row order, which gives each its
    occurrence exactly.
    """
    return _selection(hashes, tabled, tabled, min(size, len(tabled)))


def _selection(
    hashes: "list[bytes] | bytearray",
    first: "typing.Iterable[int]",
    second: "typing.Iterable[int]",
    wanted: int,
) -> "list[int]":
    """`sample_rows`'s selection over the tabled rows, walked twice (`first`, then `second`, the same rows)."""
    if wanted <= 0:
        return []
    once = bytearray(1 << 22)
    twice = bytearray(1 << 22)
    for row in first:
        one = _hash_at(hashes, row)
        mark = (one[0] << 17) | (one[1] << 9) | (one[2] << 1) | (one[3] >> 7)
        bit = 1 << (mark & 7)
        if once[mark >> 3] & bit:
            twice[mark >> 3] |= bit
        else:
            once[mark >> 3] |= bit
    del once
    seen: "dict[bytes, int]" = {}
    heap: "list[tuple[bytes, bytes, int, int]]" = []
    for at, row in enumerate(second):
        one = _hash_at(hashes, row)
        mark = (one[0] << 17) | (one[1] << 9) | (one[2] << 1) | (one[3] >> 7)
        occurrence = 0
        if twice[mark >> 3] & (1 << (mark & 7)):
            occurrence = seen[one] if one in seen else 0
            seen[one] = occurrence + 1
        key = hashlib.blake2b(one + _length_word(occurrence), digest_size=8, person=b"synthtwin.smp.1").digest()
        entry = (key, one, occurrence, at)
        if len(heap) < wanted:
            _heap_add(heap, entry)
        elif entry < heap[0]:
            _heap_replace_top(heap, entry)
    return [entry[3] for entry in sorted(heap)]


def _heap_add(heap: "list[tuple[bytes, bytes, int, int]]", entry: "tuple[bytes, bytes, int, int]") -> None:
    """Add an entry to a heap whose top (place 0) is its LARGEST entry (lane ST's, plan P4-D458)."""
    heap += [entry]
    at = len(heap) - 1
    while at > 0:
        up = (at - 1) // 2
        if heap[up] >= entry:
            break
        heap[at] = heap[up]
        at = up
    heap[at] = entry


def _heap_replace_top(heap: "list[tuple[bytes, bytes, int, int]]", entry: "tuple[bytes, bytes, int, int]") -> None:
    """Put `entry` in place of a heap's largest entry and sift it down (lane ST's, plan P4-D458)."""
    size = len(heap)
    at = 0
    while True:
        child = 2 * at + 1
        if child >= size:
            break
        if child + 1 < size and heap[child + 1] > heap[child]:
            child = child + 1
        if heap[child] <= entry:
            break
        heap[at] = heap[child]
        at = child
    heap[at] = entry


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


def _triples_by_span(places: "list[int]", budget: int, kept: "set[tuple[int, int, int]]") -> None:
    """Grow `kept` to `budget` triples of `places`, the narrowest first (span in the list, then its order)."""
    count = len(places)
    for span in range(2, count):
        for first in range(count - span):
            for middle in range(first + 1, first + span):
                if len(kept) >= budget:
                    return
                kept |= {(places[first], places[middle], places[first + span])}


def screen_triples(few: "list[bool]") -> "list[tuple[int, int, int]]":
    """The triples the screen counts, in schema order: a function of the columns' places and classes alone.

    `few[i]` says whether eligible column `i` is of the few-level class, a
    published fact. Up to `SCREEN_TRIPLES` triples exist (50 columns):
    every one. Past that the list is by construction no longer than
    `SCREEN_TRIPLES`, whatever the column count: up to
    `SCREEN_FEW_TRIPLES` of the few-level class, the narrowest in that
    class's own order first, then every triple of all the columns, the
    narrowest first (4.6b.3, amended 2026-11-01). It reads no cell, no
    count and no key, so it adds nothing to the draw's inputs.
    """
    count = len(few)
    if count * (count - 1) * (count - 2) // 6 <= SCREEN_TRIPLES:
        return [(i, j, k) for i in range(count) for j in range(i + 1, count) for k in range(j + 1, count)]
    kept: "set[tuple[int, int, int]]" = set()
    _triples_by_span([place for place in range(count) if few[place]], SCREEN_FEW_TRIPLES, kept)
    _triples_by_span(list(range(count)), SCREEN_TRIPLES, kept)
    return sorted(kept)


def screen_seeds(columns: "list[Column]") -> "tuple[tuple[int, int, int], ...]":
    """The screen's seeds: the 10 best triples greedily, then 3 best few-level triples not among them.

    The triples of `screen_triples` are counted on the sample and scored
    (`_triple_score`); ranked by score, ties by schema order. List (i) takes
    the 10 best, a pair of columns in at most two seeds; list (ii) the 3
    best of the few-level class (each member `binary` or a label column of
    at most 8 levels) not already in (i), a pair in at most two of them
    (4.6b.3, amended 2026-10-20).
    """
    scored: "list[tuple[float, int, int, int, int]]" = []
    order = 0
    held_pair = (-1, -1)
    pair_codes: "list[int]" = []
    width = 0
    for i, j, k in screen_triples([column.few for column in columns]):
        first = columns[i]
        second = columns[j]
        if (i, j) != held_pair:
            pair_codes = [x * second.screen_levels + y for x, y in zip(first.screen, second.screen)]
            width = first.screen_levels * second.screen_levels
            held_pair = (i, j)
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
    refused: "dict[tuple[str, tuple[str, ...], tuple[int, ...]], bool]"
    # The questions file's pairs, each in both orders (`ChainSwitch`).
    asked: "frozenset[tuple[str, str]]" = frozenset()
    dropped: "frozenset[tuple[str, str]]" = frozenset()
    # The carried rules' derived families `{D | A}`, placed at their rule
    # steps before the chain (RULE W1 reads `D` through `A`, rule 4).
    derived: "tuple[rules.Derived, ...]" = ()
    # Each count above 256 the cached tables hold, as one number object the
    # search shares among them (`_interned`; lane CHs, plan P4-D462).
    shared: "dict[int, int]" = dataclasses.field(default_factory=dict)


# The most cells a family's table may hold at every member's `L0` for the
# walk over the rows to count it there and sum it to the levels it is
# asked at (lane CHs, plan P4-D462); a wider one is counted at those
# levels, each member read through its own ladder's map.
L0_TABLE_CELLS = 4096


def _interned(search: _Search, table: "list[int] | tuple[int, ...]") -> "tuple[int, ...]":
    """A table's counts, each count above 256 the one number object the search holds for that count.

    THE TABLES CACHE, A POINTER A CELL (lane CHs, plan P4-D462). Python
    shares the numbers up to 256, so a cached table's cell cost 8 bytes
    while its counts were small and 36 once they passed 256: the cache
    grew with the rows, +453 MB of the switched describe's peak at
    200,000 rows of 50 numbers (MEASURED). Each count above 256 now
    stands once, shared by every cell holding it: the same numbers, and
    a cell costs a pointer however many rows the table counts.
    """
    shared = search.shared
    for count in table:
        if count > 256 and count not in shared:
            shared[count] = count
    return tuple(shared[count] if count > 256 else count for count in table)


def _level_codes(column: Column, level: int) -> "bytes | list[int]":
    """A column's codes at `level`: held, or read from its `L0` codes through the ladder's map (the same codes)."""
    held = column.codes[level]
    if held is not None:
        return held
    return moments.at_level(column.codes[0], column.ladder.maps[level])


def _table_at(search: _Search, child: str, parents: "tuple[str, ...]", base: "tuple[int, ...]", levels: "tuple[int, ...]") -> "tuple[int, ...]":
    """A candidate's complete table at `levels`, counted once at `base` (W3 and NE's levels) and summed coarser.

    THE WALK OVER THE ROWS READS `L0` (lane CHs, plan P4-D462), where only
    `L0`'s codes are held: a table asked at every member's `L0` is counted
    there; another, where the table at every member's `L0` holds at most
    `L0_TABLE_CELLS` cells, is counted there and summed to `base`, the
    same whole numbers a count at `base` gives; a wider one is counted at
    `base`, each member's codes read through its own ladder's map. Either
    way each `base` table is one walk over the rows.
    """
    key = (child, parents, levels)
    if key in search.tables:
        return search.tables[key]
    names = (child,) + parents
    if levels != base:
        finest = _table_at(search, child, parents, base, base)
        sizes = [search.scales[names[at]].counts[base[at]] for at in range(len(names))]
        to_sizes = [search.scales[names[at]].counts[levels[at]] for at in range(len(names))]
        maps = [rules.coarsen(search.scales[names[at]], base[at], levels[at]) for at in range(len(names))]
        table = _interned(search, aggregate(finest, sizes, maps, to_sizes))
    else:
        l0_sizes = [search.scales[names[at]].counts[0] for at in range(len(names))]
        cells = 1
        for size in l0_sizes:
            cells *= size
        if any(levels) and cells <= L0_TABLE_CELLS:
            counted = count_table(
                search.columns[child].codes[0],
                [search.columns[parent].codes[0] for parent in parents],
                l0_sizes[0],
                l0_sizes[1:],
            )
            sized = [search.scales[names[at]].counts[levels[at]] for at in range(len(names))]
            mapped = [rules.coarsen(search.scales[names[at]], 0, levels[at]) for at in range(len(names))]
            table = _interned(search, aggregate(counted, l0_sizes, mapped, sized))
        else:
            child_codes = _level_codes(search.columns[child], levels[0])
            parent_codes = [_level_codes(search.columns[parents[at]], levels[at + 1]) for at in range(len(parents))]
            bands = [search.scales[parents[at]].counts[levels[at + 1]] for at in range(len(parents))]
            table = _interned(search, count_table(child_codes, parent_codes, search.scales[child].counts[levels[0]], bands))
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
    for parent in parents:
        if (child, parent) in search.asked:
            raised += rules.W_RULE * search.tabled
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
    # Each derived family's parent `A` clamped to each of its chain-level
    # bands (RULE W1 reads `D` through `A`, contract 4.6b.7 rule 4).
    derived: "dict[tuple[str, int], list[list[tuple[int, tuple[int, ...]]]]]" = dataclasses.field(default_factory=dict)
    # The carried rules' derived families themselves.
    families: "tuple[rules.Derived, ...]" = ()


def _clamps_of(
    search: _Search,
    placed: "list[rules.Family]",
    need_bands: bool,
    derived_families: "tuple[rules.Derived, ...]" = (),
) -> _Clamps:
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
    derived: "dict[tuple[str, int], list[list[tuple[int, tuple[int, ...]]]]]" = {}
    homes = {family.child: family.level for family in placed}
    for one in derived_families:
        if one.parent not in homes:
            continue
        for band in range(search.scales[one.parent].counts[homes[one.parent]]):
            if (one.parent, band) not in derived:
                derived[(one.parent, band)] = rules.beliefs(support, (one.parent, {band}))
    narrowed: "dict[tuple[str, str, int], frozenset[int]]" = {}
    for which, held in (("group", groups), ("band", bands), ("derived", derived)):
        for key in held:
            reached = held[key]
            narrowed[(which, key[0], key[1])] = frozenset(
                at for at in range(len(placed)) if len(reached[at]) != len(support.cells[at])
            )
    return _Clamps(support, groups, bands, {}, narrowed, derived, derived_families)


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
    if not _derived_w1(search, clamps, anchor_at, anchor, child, parents, levels, table, clamps.families):
        return False
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


def _derived_w1(
    search: _Search,
    clamps: "_Clamps | None",
    anchor_at: "int | None",
    anchor: "rules.Family | None",
    child: str,
    parents: "tuple[str, ...]",
    levels: "tuple[int, ...]",
    table: "tuple[int, ...]",
    derived: "tuple[rules.Derived, ...]",
) -> bool:
    """RULE W1 for a carried rule's derived column `D`, read through `A` (contract 4.6b.7, rule 4).

    `{D | A}` is placed at its rule's step, before the chain, so `D` joins
    the support through `A` once `A`'s own family is placed (the oracle's
    `tree_edges`). An option whose child is `A` reads `D` beside every
    group already placed; an option whose child is new and stands beside
    a placed `A` reads `D` beside the child's own groups; `A`'s own groups
    were read by rule 4 at the rule's step. Each reach takes `D`'s bands
    over `A`'s `L0` bands inside its admitted bands (`rules.derived_reach`).
    """
    if not derived:
        return True
    child_bands = search.scales[child].counts[levels[0]]
    width = len(table) // child_bands
    for one in derived:
        a_ladder = search.scales[one.parent]
        if anchor is None:
            parent = parents[0]
            if child == one.parent:
                for group in search.columns[parent].groups:
                    row = search.scales[parent].maps[levels[1]][group]
                    feasible = {c for c in range(child_bands) if table[row * child_bands + c]}
                    if not rules.derived_reach_holds(rules.derived_reach(a_ladder, levels[0], feasible, one), one, False):
                        return False
            elif parent == one.parent:
                for group in search.columns[child].groups:
                    column = search.scales[child].maps[levels[0]][group]
                    feasible = {r for r in range(width) if table[r * child_bands + column]}
                    if not rules.derived_reach_holds(rules.derived_reach(a_ladder, levels[1], feasible, one), one, False):
                        return False
            continue
        if clamps is None or anchor_at is None:
            continue
        if child == one.parent:
            for key in clamps.groups:
                if anchor_at in clamps.narrowed[("group", key[0], key[1])]:
                    reachable = _projected(search, clamps, "group", key, anchor_at, anchor, parents, levels[1:])
                else:
                    reachable = frozenset(range(width))
                feasible = {c for c in range(child_bands) if any(table[row * child_bands + c] for row in reachable)}
                if not rules.derived_reach_holds(rules.derived_reach(a_ladder, levels[0], feasible, one), one, False):
                    return False
            continue
        if one.parent not in clamps.support.home:
            continue
        a_level = clamps.support.chain_level[one.parent]
        own = {search.scales[child].maps[levels[0]][group] for group in search.columns[child].groups}
        for band in sorted(own):
            holding = {row for row in range(width) if table[row * child_bands + band]}
            feasible_bands: "set[int]" = set()
            for a_band in range(a_ladder.counts[a_level]):
                key = (one.parent, a_band)
                if key not in clamps.derived:
                    continue
                if anchor_at in clamps.narrowed[("derived", key[0], key[1])]:
                    reachable = _projected(search, clamps, "derived", key, anchor_at, anchor, parents, levels[1:])
                else:
                    reachable = frozenset(range(width)) if clamps.derived[key][anchor_at] else frozenset()
                if reachable & holding:
                    feasible_bands = feasible_bands | {a_band}
            if not rules.derived_reach_holds(rules.derived_reach(a_ladder, a_level, feasible_bands, one), one, False):
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
    held = clamps.groups if which == "group" else (clamps.bands if which == "band" else clamps.derived)
    feasible = held[key][anchor_at]
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
        held = len(out)
        out += [out[at] + (name,) for at in range(held) if len(out[at]) < k_max]
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
            if any((child, name) in search.dropped for name in subset):
                continue
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
                    search.refused[(child, subset, levels)] = True
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
            if (child, parent) in search.dropped:
                continue
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
                if not _w1_holds(search, None, None, None, child, (parent,), levels, table) or (
                    search.derived and not _derived_w1(search, None, None, None, child, (parent,), levels, table, search.derived)
                ):
                    search.counts["w1_refusals"] += 1
                    search.refused[(child, (parent,), levels)] = True
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


def _release(search: _Search, child: str) -> None:
    """Let go of the cached tables and scores of a column just placed: no later step offers it as a child (lane CHs, plan P4-D462)."""
    for key in [key for key in search.tables if key[0] == child]:
        del search.tables[key]
    for key in [key for key in search.scored if key[0] == child]:
        del search.scored[key]


def search_chain(search: _Search, switch: ChainSwitch, x0: "dict[str, int] | None", room: int) -> "tuple[list[rules.Family], list[str]]":
    """The chain, step by step, each step DRAWN among its eligible options (4.6b.3, 4.6b.4)."""
    notes: "list[str]" = []
    roots = _root_options(search, x0, room)
    search.counts["eligible_options"] += len(roots)
    _probed("search step", search.counts)
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
    _release(search, parent)
    _release(search, root.child)
    margins: "dict[tuple[int, tuple[str, ...]], rules.ParentCells]" = {}
    index = 1
    while len(placed) < len(search.eligible):
        need_bands = any(
            search.columns[name].groups
            for name in search.eligible
            if name not in {family.child for family in placed}
        )
        clamps = _clamps_of(search, placed, need_bands, search.derived)
        options = _step_options(search, placed, clamps, margins)
        search.counts["eligible_options"] += len(options)
        _probed("search step", search.counts)
        pick = _draw(search, switch, index, options)
        chosen = options[pick]
        placed += [_family_of(chosen)]
        _release(search, chosen.child)
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
        # Grown in place: a copy a value made the walk quadratic on a
        # column of unique keys (Codex's item 3 on repair 1).
        seen |= {text}
    return False


def _requested(pairs: "tuple[tuple[str, str], ...]", eligible: "list[str]") -> "frozenset[tuple[str, str]]":
    """The questions file's pairs of two different eligible columns, each in both orders."""
    out: "set[tuple[str, str]]" = set()
    for one, other in pairs:
        if one != other and one in eligible and other in eligible:
            out |= {(one, other), (other, one)}
    return frozenset(out)


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


def _tabled(data: "bytes | bytearray | list[int]", excluded: "list[int]") -> "bytes | bytearray | list[int]":
    """One entry a row read on the tabled rows alone: the rows `excluded` lists (ascending) left out.

    Nothing is copied where no row is left out; otherwise the runs between
    the rows left out are joined, bytes as bytes and numbers as numbers.
    """
    if not excluded:
        return data
    start = 0
    if isinstance(data, list):
        numbers: "list[int]" = []
        for row in excluded:
            numbers += data[start:row]
            start = row + 1
        numbers += data[start:]
        return numbers
    out = bytearray()
    for row in excluded:
        out += data[start:row]
        start = row + 1
    out += data[start:]
    return out


def _mapped(codes: "bytes | bytearray | list[int]", mapping: "list[int] | tuple[int, ...]") -> "bytes | list[int]":
    """Each code read through `mapping`, one byte a row where every result fits one, else a number a row."""
    if not mapping or max(mapping) < 256:
        return bytes(mapping[code] for code in codes)
    return _codes([mapping[code] for code in codes])


def _count_codes(codes: "bytes | bytearray | list[int]", size: int) -> "list[int]":
    """How many rows stand at each of `size` codes."""
    out = [0] * size
    for code in codes:
        out[code] += 1
    return out


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


def released_moments(
    eligible: "list[str]",
    blocks: "dict[str, dict[str, object]]",
    columns: "dict[str, Column]",
    scales: "dict[str, rules.Ladder]",
    floor: int,
) -> "tuple[dict[str, object] | None, dict[str, int]]":
    """Rule B's `moments` object (contract 4.6d.0, plan P4-D455) from the codes the chain read.

    The moment columns are the eligible FINE columns of a number role, on
    their linear code, and the binaries of `binary_levels`, on 0 and 1;
    every eligible column groups on its `L1` bands. A held, identifier,
    sequence or free-text column is ineligible (4.6b.1), so no moment
    reads it; dates and clocks take no moment. The chain is reached only
    on a table of one row a person (`OFF_PERSON`), so every count here
    is a count of people.
    """
    picked: "list[moments.Released]" = []
    groupings: "list[moments.Grouping]" = []
    for name in eligible:
        column = columns[name]
        role = _get(blocks[name], "role")
        ladder = scales[name]
        groupings += [
            moments.Grouping(
                name,
                b"",
                tuple(rules.totals_at(ladder, 1)),
                frozenset(ladder.maps[1][band] for band in column.groups),
                tuple(rules.coarsen(ladder, 1, 2)),
                column.codes[0],
                ladder.maps[1],
            )
        ]
        if role in rules.NUMBER_ROLES and column.value_codes is not None:
            linear, _second, has = column.value_codes
            picked += [moments.Released(name, moments.KIND_NUMBER, linear, has)]
            continue
        if role != rules.ROLE_BINARY:
            continue
        levels = moments.binary_levels(ladder)
        if levels is None:
            continue
        level_zero = column.codes[0]
        values = bytes(1 if level_zero[row] == levels[1] else 0 for row in range(len(level_zero)))
        present = bytearray(1 if level_zero[row] in levels else 0 for row in range(len(level_zero)))
        picked += [moments.Released(name, moments.KIND_BINARY, values, present)]
    return moments.released(picked, groupings, floor)


def _quantile_skew(block: "dict[str, object]") -> "float | None":
    """The quantile skew `(p90 + p10 - 2 p50) / (p90 - p10)` of a column's published rungs, or None."""
    rungs = rules.rung_ladder(block)
    if rungs is None:
        return None
    role = f"{_get(block, 'role')}"
    p10 = moments.ordinal(role, _get(rungs, "p10"), block)
    p50 = moments.ordinal(role, _get(rungs, "p50"), block)
    p90 = moments.ordinal(role, _get(rungs, "p90"), block)
    if p10 is None or p50 is None or p90 is None or p10 == p90:
        return None
    return float((p90 + p10 - 2 * p50) / (p90 - p10))


def selftest_inputs(
    sample: "list[int]",
    tabled: int,
    sample_hashes: "tuple[int, ...]",
    eligible: "list[str]",
    columns: "dict[str, Column]",
    blocks: "dict[str, dict[str, object]]",
    placed: "list[rules.Family]",
    pairs: "frozenset[tuple[str, str]]",
) -> SelftestInputs:
    """The self-test's inputs (lane ST, plan P4-D458): each eligible column's codes on the sample rows.

    Reads only what `describe` already holds at its return, one pass over
    the sample a column: nothing here grows with the table's rows.
    `tabled` is the count of tabled rows and `sample_hashes` each sampled
    row's content hash's first eight bytes as a number, in sample order,
    read where the sample is drawn (batch 4q's merge of lane CHs, whose
    describe lets the row hashes go there and holds no list of the
    tabled rows).
    """
    picked: "list[SampleColumn]" = []
    for name in eligible:
        column = columns[name]
        block = blocks[name]
        role = f"{_get(block, 'role')}"
        ladder = column.ladder
        level_zero = column.codes[0]
        l0 = _codes([level_zero[at] for at in sample])
        linear: "bytes | None" = None
        second: "bytes | None" = None
        has: "bytes | None" = None
        lo: "float | None" = None
        hi: "float | None" = None
        if column.value_codes is not None:
            held_linear, held_second, held_has = column.value_codes
            linear = bytes(held_linear[at] for at in sample)
            second = None if held_second is None else bytes(held_second[at] for at in sample)
            has = bytes(held_has[at] for at in sample)
            found = moments.codes_of(block)
            if found is not None:
                lo = float(found.lo_value)
                hi = float(found.hi_value)
        missing = -1
        for at in range(len(ladder.l0)):
            if rules.MISSING in ladder.l0[at]:
                missing = at
        binary = moments.binary_levels(ladder) if role == rules.ROLE_BINARY else None
        picked += [
            SampleColumn(
                name, role, ladder, l0, linear, second, has, binary, missing, _quantile_skew(block), lo, hi, column.beyond
            )
        ]
    oriented = tuple((first, other) for first, other in sorted(pairs) if _get(blocks[first], "role") != rules.ROLE_BINARY)
    return SelftestInputs(
        tabled,
        sample_hashes,
        tuple(picked),
        tuple(placed),
        oriented,
    )


def _off(note: str, counts: "dict[str, int]", notes: "list[str]", content: str) -> Chained:
    return Chained(None, tuple(notes + [f"no chain is published: {note}"]), counts, (), (), content)


def too_few_columns(chained: Chained) -> bool:
    """Whether a table drew no chain for want of two eligible columns, so that the subject question would decide nothing."""
    return bool(chained.notes) and chained.notes[-1] == f"no chain is published: {OFF_FEW}"


def person_question_holds(chained: Chained) -> bool:
    """Whether the open person question holds a repeating column, so that the subject question would decide nothing this round."""
    return "person_question_holds" in chained.counts


def describe(
    table: reading.Table,
    document: "dict[str, object]",
    settings: taxonomy.Settings,
    switch: ChainSwitch,
    forced_codes: "list[str] | None" = None,
    forced_measurements: "list[str] | None" = None,
    forced_decimal_commas: "list[str] | None" = None,
    stored_as: "tuple[str, ...] | None" = None,
    kept: "dict[int, taxonomy.KeptSpellings] | None" = None,
) -> Chained:
    """The chain of `document`'s table: its `statistical` object and the private notes (4.6b).

    `kept` holds the description's own readings, kept column by column by
    `profile.build_document` (lane CHs, plan P4-D462): each is taken by
    `read_column` where it was read under the chain's own arguments, and
    let go as its column is read.

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
    _probed("start", counts)
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
    hashes, filled = row_hash_buffer(table)
    content = _hex(content_hash(hashes, filled))
    _probed("row hashes", counts)
    if persons:
        # THE PERSON AND THE RECORD (lane GRa, RULINGS 1 (1)): a repeating key
        # nothing reads as the person holds the layer back, so no count of
        # encounters is ever published as a count of patients; an answer
        # `one row each` beside it contradicts itself, and draws nothing.
        if switch.rows_per_person == ROWS_OPEN:
            return _off(OFF_SUBJECT, counts, notes, content)
        if switch.rows_per_person == ROWS_UNNAMED:
            return _off(OFF_NO_PERSON, counts, notes, content)
        if switch.rows_per_person == ROWS_ONE:
            return _off(OFF_PERSON, counts, notes, content)
        # THE KEPT READINGS ARE THE TABLE LAYER'S (lane CHs, plan P4-D462):
        # the patient layer reads none of them, so they are let go before it
        # runs (batch 4q's merge of lane CHs beside lane GRa's layer).
        if kept is not None:
            for place in [place for place in kept]:
                del kept[place]
        # THE PATIENT LAYER (contract 4.6c; lane GRa, plan P4-D449), its one
        # call site: a table whose settings name a person column is described
        # in patients where 4.6c.3's gate holds, else no chain is drawn.
        from synthtwin import patient_layer

        layer = patient_layer.describe(
            table, document, settings, switch, filled, persons, identifiers,
            list(forced_codes or []), list(forced_measurements or []),
            list(forced_decimal_commas or []), stored_as or (),
        )
        for key in layer.counts:
            counts[key] = layer.counts[key]
        if layer.statistical is None:
            return _off(OFF_PERSON, counts, notes + list(layer.notes), content)
        return Chained(layer.statistical, tuple(notes + list(layer.notes)), counts, (), (), content, None, layer.grain, layer.columns)
    # A REPEATING COLUMN HELD OR DECLARED, BESIDE NO PERSON COLUMN. A caller
    # that measures the walk is told at once. Otherwise the check is read
    # after the eligible columns are counted (the subject question's reach),
    # and under `one row each` only a key answered `identifier` or a column
    # the person question still holds keeps it: a column held for another
    # question (Safe Harbor, a ZIP) stays held and ineligible, and the person
    # has said its repeats are no person's (the statistics skeptic's item 7).
    named_key = False
    for place in range(len(blocks)):
        named = _get(blocks[place], "name")
        if (named in held or named in identifiers) and _repeats(reading.column_values(table, place)):
            if switch.rows_per_person == ROWS_UNASKED:
                return _off(OFF_HELD_REPEATS, counts, notes, content)
            # The open person question holds a repeating column: the subject
            # question cannot settle this table until that one is answered.
            if named in switch.held_by_person:
                counts["person_question_holds"] = 1
            # (The description lists every held column among its declared
            # ones, so "answered" reads the declared ones no question holds.)
            if switch.rows_per_person == ROWS_ONE and named not in switch.held_by_person and (named in held or named in switch.unanswered or named not in identifiers):
                continue
            named_key = True
    # THE PERSON COLUMN'S STATE FOR THE RULE STEPS (contract 4.6b.7, MR.3;
    # lane RO, plan P4-D459), as lane GRa's subject question leaves it (plan
    # P4-D449): a person column has gone to the patient layer above, and a
    # repeating key no answer excuses holds the layer back below
    # (OFF_HELD_REPEATS); a column the answer `one row each` excuses is no
    # person's, so the rule steps read no person there.
    person_state = named_key
    blank_rows = rules.records_holding_nothing(document)
    # THE TABLED ROWS (lane CHs, plan P4-D462): the rows set aside, a record
    # holding nothing each, listed (E of them); every row reads on the
    # tabled rows through `_tabled`, so nothing is held a row for them.
    excluded: "list[int]" = []
    left = blank_rows
    for row in range(table.n_rows):
        if left and not filled[row]:
            excluded += [row]
            left -= 1
    if left:
        return _off(OFF_RECOUNT, counts, notes, content)
    tabled = table.n_rows - len(excluded)
    sample = _selection(
        hashes, _rows_of(table.n_rows, excluded), _rows_of(table.n_rows, excluded), min(rules.selftest_size(tabled), tabled)
    )
    # THE SAMPLE'S ROWS AND THEIR HASHES (lane ST's self-test, plan P4-D458,
    # beside lane CHs's tabled rows, P4-D462; batch 4q's merge): the row of
    # each sampled place, and the first eight bytes of its content hash read
    # as a number, read before the hashes are let go; the self-test's inputs
    # and its readings beyond the clip read them, a number a sampled row.
    sampled_rows = _rows_at(sample, excluded)
    sample_hashes = tuple(rules.big_endian(_hash_at(hashes, row)[:8]) for row in sampled_rows)
    del hashes
    counts["sample_rows"] = len(sample)
    _probed("sample", counts)
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
    # THE RULE STEPS' READINGS (lane RO, plan P4-D459; G4): each column's
    # readings under the kinds the inference reads, taken in the loop below
    # from the cells it reads, held compactly, and let go after the inference.
    gathered = chain_order.gathered_for(tabled) if switch.rules else None
    for place in range(len(blocks)):
        block = blocks[place]
        name = f"{_get(block, 'name')}"
        declared = {
            "code": name in declared_codes,
            "measurement": name in declared_measurements,
            "decimal_comma": name in declared_commas,
        }
        reason = ineligible_reason(block, place in sequences, name in held, identifiers)
        takes = gathered is not None and chain_order.takes_part(block, reason is None, held, identifiers)
        if reason is not None:
            # An ineligible column's kept reading is let go here, before the
            # search, which never reads it (lane CHs, plan P4-D462).
            if kept is not None and place in kept:
                del kept[place]
            ineligible += [{"column": name, "reason": reason}]
            if takes and gathered is not None:
                # A candidate `B` the families never read: read once, here, in its place.
                texts = reading.column_values(table, place)
                spelled = taxonomy.spellings_read(
                    texts,
                    name,
                    settings,
                    forced_code=declared["code"],
                    forced_measurement=declared["measurement"],
                    forced_decimal_comma=declared["decimal_comma"],
                    stored_as=storage[place] if place < len(storage) else "",
                )
                chain_order.gather(gathered, name, block, _tabled_texts(texts, excluded), spelled, declared, range(tabled))
            continue
        cells_kept: "list[tuple[list[str], dict[str, tuple[str, float | None, str]]]] | None" = [] if takes else None
        handed: "taxonomy.KeptSpellings | None" = None
        if kept is not None and place in kept:
            handed = kept[place]
            del kept[place]
        read = read_column(
            table,
            place,
            block,
            settings,
            declared,
            storage[place] if place < len(storage) else "",
            blank_rows,
            kept=cells_kept,
            spellings_kept=handed,
        )
        if cells_kept and gathered is not None:
            # The rule steps read the tabled rows alone (lane RO): the cells on
            # them, row by row, in place of a list of their places, which lane
            # CHs no longer holds (batch 4q's merge; the same readings).
            chain_order.gather(gathered, name, block, _tabled_texts(cells_kept[0][0], excluded), cells_kept[0][1], declared, range(tabled))
        cells_kept = None
        del handed
        _probed("read column", counts)
        if read is None or not read.agrees:
            notes += [f"the recount of column {name} disagreed with its published counts"]
            return _off(OFF_RECOUNT, counts, notes, content)
        start_codes = _tabled(read.codes, excluded)
        starting_totals = _count_codes(start_codes, len(read.start.names))
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
        # `L0`'s codes through the starting bands' map, one byte a row; `L1`
        # and `L2` are read from them where they are asked for
        # (`_level_codes`): the same codes the first build held.
        first = _mapped(start_codes, start_to_l0)
        screen_map, screen_levels, few = _screen_codes(block, read, ladder)
        screen = bytes(screen_map[start_codes[at]] for at in sample)
        del start_codes
        blank = sum(read.blanks) - sum(read.blanks[row] for row in excluded)
        groups = rules.small_group_bands(block, read.start, ladder, floor) | value_run_bands(
            block, read.start, ladder, floor, read.readings
        )
        value_codes: "tuple[bytes, bytes | None, bytearray] | None" = None
        if read.linear is not None:
            second_rows = read.second
            value_codes = (
                bytes(_tabled(read.linear, excluded)),
                None if second_rows is None else bytes(_tabled(second_rows, excluded)),
                bytearray(_tabled(read.has_reading, excluded)),
            )
            moment_blocks[name] = block
        # THE SELF-TEST'S RAW SCALE (lane ST, plan P4-D458): the sample's
        # rows whose reading lies beyond the clip, read from this pass.
        beyond: "dict[int, float] | None" = None
        if read.beyond is not None:
            held_beyond = read.beyond
            beyond = {}
            for at in range(len(sample)):
                if sampled_rows[at] in held_beyond:
                    beyond[at] = held_beyond[sampled_rows[at]]
        columns[name] = Column(
            name,
            ladder,
            (first, None, None),
            frozenset(groups),
            screen,
            screen_levels,
            few,
            blank,
            value_codes,
            beyond,
        )
        scales[name] = ladder
        eligible += [name]
        _probed("ladder and codes", counts)
    # THE RULE STEPS (contract 4.6b.7, MR.3 and MR.7; lane RO, plan P4-D459):
    # every rule whose step opens, one step a rule, all before the chain,
    # each DRAWN among "not carried" and its eligible carried options. A
    # carried rule's computed column leaves the eligible columns.
    inference = chain_order.Inference((), (), (), 0)
    if gathered is not None:
        for name in list(gathered.present):
            if name not in scales and chain_order.computed_refused(block_of_name(blocks, name), held, identifiers):
                # Neither a `B` OPEN1 admits nor an eligible column: its readings are not read.
                chain_order.let_go(gathered, name)
        inference = chain_order.infer_rules(
            gathered,
            blocks,
            settings,
            dict(scales),
            {name: columns[name].groups for name in eligible},
            {name: columns[name].codes[0] for name in eligible},
            tabled,
            held,
            identifiers,
            _requested(switch.drop, [f"{_get(block, 'name')}" for block in blocks]),
            person_state,
        )
        gathered = None
    carried, rule_notes, rule_pairs = _rule_steps(inference, switch, [f"{_get(block, 'name')}" for block in blocks])
    notes += rule_notes
    counts["rules_opened"] = len(inference.rules)
    counts["rules_carried"] = len(carried)
    computed_names = {rule.computed for rule, _option in carried}
    if computed_names:
        eligible = [name for name in eligible if name not in computed_names]
        for name in computed_names:
            if name in columns:
                del columns[name]
                del scales[name]
            if name in moment_blocks:
                del moment_blocks[name]
        place_in_schema = {f"{_get(blocks[at], 'name')}": at for at in range(len(blocks))}
        # (`ineligible_entries`, not `kept`: since lane CHs, `kept` names the description's kept readings.)
        ineligible_entries = [entry for entry in ineligible if entry["column"] not in computed_names]
        ineligible_entries += [{"column": name, "reason": "computed"} for name in computed_names]
        ranked = sorted((place_in_schema[f"{ineligible_entries[at]['column']}"], at) for at in range(len(ineligible_entries)))
        ineligible = [ineligible_entries[at] for _place, at in ranked]
    derived_families = tuple(
        rules.derived_of(rule.inputs[0], option.a_level, option.table, not option.level[2])
        for rule, option in carried
        if option.carrier == rules.CARRIER_DERIVED and option.a_level is not None and option.level is not None
    )
    counts["eligible_columns"] = len(eligible)
    if len(eligible) < 2 and not carried:
        return _off(OFF_FEW, counts, notes, content)
    # THE SUBJECT QUESTION'S HOLD: read here, where only the question stands
    # between this table and a chain (a table with fewer than two eligible
    # columns draws none, whatever the answer, and is not asked).
    if switch.rows_per_person == ROWS_OPEN:
        return _off(OFF_SUBJECT, counts, notes, content)
    if switch.rows_per_person == ROWS_UNNAMED:
        return _off(OFF_NO_PERSON, counts, notes, content)
    if named_key:
        return _off(OFF_HELD_REPEATS, counts, notes, content)
    pairs = time_event_pairs(blocks, eligible)
    seed_places = screen_seeds([columns[name] for name in eligible])
    seeds = tuple((eligible[i], eligible[j], eligible[k]) for i, j, k in seed_places)
    _probed("screen", counts)
    place_of: "dict[str, int]" = {}
    for at in range(len(eligible)):
        place_of[eligible[at]] = at
    asked = _requested(switch.add, eligible)
    dropped = _requested(switch.drop, eligible)
    if asked or dropped:
        notes += [f"the questions file asked to add {len(asked) // 2} and drop {len(dropped) // 2} pairs of eligible columns"]
    # W5's raise for every opened rule step (contract 4.6b.7, MR.12): the pair
    # `{A, B}`, or `{D, A}` where a source carries it, read beside the
    # questions file's pairs, one raise a family (as the oracle's `rule_pairs`).
    raised = asked | frozenset(pair for pair in rule_pairs if pair[0] in place_of and pair[1] in place_of)
    search = _Search(
        columns, scales, tuple(eligible), place_of, tabled, floor, pairs, seeds, {}, counts, {}, {}, raised, dropped,
        derived_families,
    )
    blank_counts = {name: columns[name].blank for name in eligible}
    x0 = rules.blank_cell(scales, blank_counts)
    room = rules.blank_record_room(document, floor) + rules.outside_cells(document, set(eligible))
    placed: "list[rules.Family]" = []
    if len(eligible) >= 2:
        placed, step_notes = search_chain(search, switch, x0, room)
        notes += step_notes
    counts["w1_refused_options"] = len(search.refused)
    if not placed:
        if not carried:
            return _off(OFF_ROOT, counts, notes, content)
        # A RULES-ONLY description (4.6b.3): every eligible column at `L0`, in schema order, beside the carried rules.
        placed = [rules.Family(name, 0, (), None, tuple(scales[name].totals)) for name in eligible]
        notes += ["the chain is rules only: every eligible column at L0 beside the carried rules"]
    refused = rules.w1_refusals(placed, scales, {name: set(columns[name].groups) for name in eligible}, derived_families)
    for family in placed:
        if not _floored(family.table, floor):
            refused += [(family.child, -1, "")]
    _probed("chain check", counts)
    if refused:
        notes += [f"the chain's own check found {len(refused)} refusals"]
        return _off("the chain's own check failed", counts, notes, content)
    inputs = moment_inputs(placed, scales, columns, moment_blocks, floor)
    _probed("moment inputs", counts)
    for key, name in (("moment_region_columns", "codes"), ("moment_offers", "offers"), ("moment_regions", "regions"), ("moment_sums", "sums")):
        listed = inputs[name]
        counts[key] = len(listed) if isinstance(listed, list) else 0
    block_of: "dict[str, dict[str, object]]" = {f"{_get(block, 'name')}": block for block in blocks}
    released, released_counts = released_moments(eligible, block_of, columns, scales, floor)
    _probed("released moments", counts)
    for key in released_counts:
        counts[f"moments {key}"] = released_counts[key]
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
        "moments": released,
        "not_carried": implied,
        "procedure": rules.procedure_record(tabled),
        "rules": [_rule_entry(rule, option) for rule, option in carried],
        "withheld": [],
        "words": words,
    }
    if seeds:
        notes += [f"the screen offered {len(seeds)} seeds as weights"]
    chosen = tuple((family.child, tuple(name for name, _level in family.parents), tuple(level for _name, level in rules.members(family))) for family in placed)
    computed: "list[tuple[str, dict[str, object]]]" = []
    for rule, _option in carried:
        own = block_of[rule.computed]
        template = block_of[rule.inputs[0]]
        role = rules.computed_role(rule.kind, [f"{_get(block_of[name], 'role')}" for name in rule.inputs])
        computed += [(rule.computed, chain_order.computed_block(own, template, role, floor))]
    selftest = selftest_inputs(sample, tabled, sample_hashes, eligible, columns, block_of, placed, pairs)
    _probed("statistical object", counts)
    return Chained(
        statistical,
        tuple(notes),
        counts,
        seeds,
        chosen,
        content,
        inputs,
        computed=tuple(computed),
        selftest=selftest,
    )


# THE PATIENT LAYER'S READ OF THIS MODULE (lane GRa, plan P4-D449): the steps
# of 4.6b it runs over the patient table, under names another module may read.
Search = _Search
draw_step = _draw
root_options = _root_options
step_options = _step_options
clamps_of = _clamps_of
family_of = _family_of
is_blank = _is_blank
repeats = _repeats
reading_of = _reading_of
sequence_places = _sequence_places
codes_at = _codes


def block_of_name(blocks: "list[dict[str, object]]", name: str) -> "dict[str, object]":
    """The published block of the column named `name` (an empty block where none is)."""
    for block in blocks:
        if _get(block, "name") == name:
            return block
    return {}


def _rule_steps(
    inference: chain_order.Inference,
    switch: ChainSwitch,
    names: "list[str]",
) -> "tuple[list[tuple[chain_order.Inferred, chain_order.Option]], list[str], frozenset[tuple[str, str]]]":
    """Each rule's step DRAWN among "not carried" and its eligible carried options (4.6b.7, MR.7).

    In step order; a rule whose computed column a rule carried before it
    computes or reads, or one of whose inputs it computes, has "not
    carried" alone, and a source option whose carrier a rule carried
    before it computes is not offered (no carried rule reads a computed
    column; lane RO's repair 2, the outside review's item 7). The word is
    keyed by the rule's IDENTITY, `[kind,
    computed, inputs]`, beside the table's column names in schema order
    (a fact every table of the preimage shares before any step: the
    eligible columns move with the steps' outcomes), never by its place.
    Returns the carried rules with their options, private notes (no
    count) and W5's raise: every opened rule's pair `{A, B}`, or `{D, A}`
    where a source carries it, each in both orders, where the rule's
    antecedent (both columns reading) holds at least `f` rows (4.6b.7's
    opening paragraph; a weight, which the draw masks): a step whose
    computed column never reads under its input's kind raises nothing.
    """
    carried: "list[tuple[chain_order.Inferred, chain_order.Option]]" = []
    computed: "set[str]" = set()
    read: "set[str]" = set()
    raised: "set[tuple[str, str]]" = set()
    notes: "list[str]" = []
    for rule in inference.rules:
        first = rule.inputs[0]
        blocked = rule.computed in computed or rule.computed in read or any(name in computed for name in rule.inputs)
        options = [] if blocked else [option for option in rule.options if option.carrier == rules.CARRIER_DERIVED or option.carrier not in computed]
        scores = [fractions.Fraction(0)] + [option.score for option in options]
        word = step_word(switch.key, switch.name, rules.STEP_RULE, rules.rule_key(rule.kind, rule.computed, list(rule.inputs)), names)
        pick = rules.choose(word, rules.weights_of(scores, rules.TAU))
        if pick == 0:
            if rule.antecedent:
                raised |= {(first, rule.computed), (rule.computed, first)}
            why = "blocked by a rule carried before it" if blocked else (rule.why or "drawn")
            notes += [f"the rule {rule.computed} on or after {first} was not carried among {len(options) + 1} eligible options ({why})"]
            continue
        option = options[pick - 1]
        carried += [(rule, option)]
        computed |= {rule.computed}
        read |= set(rule.inputs)
        if option.carrier == rules.CARRIER_DERIVED:
            raised |= {(first, rule.computed), (rule.computed, first)}
            notes += [f"the rule {rule.computed} on or after {first} is carried by a derived difference among {len(options) + 1} eligible options"]
        else:
            read |= {option.carrier}
            raised |= {(option.carrier, first), (first, option.carrier)}
            notes += [f"the rule {rule.computed} on or after {first} is carried by the source column {option.carrier} among {len(options) + 1} eligible options"]
    return carried, notes, frozenset(raised)


def _rule_entry(rule: chain_order.Inferred, option: chain_order.Option) -> "dict[str, object]":
    """A carried rule's entry of `rules` (4.6b.5 as amended by MR.2 and MR.8)."""
    derived: "dict[str, object] | None" = None
    if option.carrier == rules.CARRIER_DERIVED and option.level is not None and option.a_level is not None:
        derived = {
            "edges": [rules.decimal_text(edge) for edge in option.level[2]],
            "name": option.level[0],
            "parent": {"column": rule.inputs[0], "level": rules.LEVELS[option.a_level]},
            "table": [list(line) for line in option.table],
            "totals": list(option.totals),
        }
    return {
        "carrier": option.carrier,
        "class": option.klass,
        "computed": rule.computed,
        "derived": derived,
        "grain": rule.grain,
        "inputs": list(rule.inputs),
        "kind": rule.kind,
        "op": None,
        "unit": option.unit,
    }


def with_rules(document: "dict[str, object]", chained: Chained) -> "dict[str, object]":
    """The description with its chain in `relationships.statistical` and each computed column's block
    in the column's place (contract 4.6b.7): what a caller of the switch writes."""
    written: "dict[str, object]" = {}
    for key in document:
        written[key] = document[key]
    computed = dict(chained.computed)
    columns = _get(document, "columns")
    if computed and isinstance(columns, list):
        replaced: "list[object]" = []
        for block in columns:
            name = _get(block, "name") if isinstance(block, dict) else None
            replaced += [computed[name] if isinstance(name, str) and name in computed else block]
        written["columns"] = replaced
    relationships = _get(document, "relationships")
    if isinstance(relationships, dict):
        block_out: "dict[str, object]" = {}
        for key in relationships:
            block_out[key] = relationships[key]
        block_out["statistical"] = chained.statistical
        written["relationships"] = block_out
    return written
