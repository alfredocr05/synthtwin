"""Order rules between columns, carried through their difference `D` (contract 4.6b.7; lane RO, plan P4-D459).

NOT IN FORCE. Invariant S12 stands until the landing that ships stage 6:
only a caller holding the chain's switch reaches this module, through
`chain.describe`, which calls `infer_rules` once, before the chain is
searched. Every shipped description, summary and twin stays byte for
byte as it was.

WHAT IT DOES. Lane MR's page (contract 4.6b.7, MR.1 to MR.13) exactly:

- THE INFERENCE (MR.3). A rule's step OPENS on a table where, and only
  where, OPEN1 to OPEN3 hold, and a builder may add no condition: OPEN1
  reads the columns' names, roles, answers, holds, top-codes, year
  pooling and published number styles (and `B`'s first published form);
  OPEN2 reads `v`, the rows where both columns hold a reading and `B`
  lies below `A` under MR.2's reading of the pair, against `L(n)`;
  OPEN3 reads the base's readings against the floor. A pair in the
  switch's drop list opens no step. A pair stops at its first `L + 1`
  failing rows.
- THE READINGS (MR.2), each column through its own reader: numbers
  exactly (a cell's number through its shortest decimal text, so `003.50`
  reads 3.5 and a workbook number reads as its shortest text), dates in
  whole calendar days, stamps in seconds (across UTC offsets where both
  hold one), a date beside a stamp in calendar days with grain `day`,
  clocks in seconds within the day with no wrap. `D` has one unit for
  the pair, and is exact: a whole number of days or seconds, or a
  number scaled to a common count of places.
- THE OPTIONS OF AN OPEN STEP: "not carried"; a DERIVED option for each
  pair of a level of `D` and a level of `A` eligible under rules 1 to 6
  (`chain_rules.derived_option_refusal`), row 9's one test on the base
  (`chain_rules.partition_passes`) and the class the real `v` falls in;
  a SOURCE option for every number column and unit whose own failing
  rows number at most `f - 1`, under MR.3's three source conditions and
  `n_negative` 0.
- THE SCORE (MR.7), which reads the real table freely because the draw
  masks it: `w_rule n` plus the family's `u`, a source option the step's
  largest derived score plus `w_rule n`, and `-w_rule n` for an option
  NOT WORTH carrying by MR.7's list, every item as written and nothing
  more.

WHAT IT DOES NOT DO. No formula rule (lane RD), no zero's inference
(lane RZ), no chain of events and no carrier `{D | A, X}` (lane RO2),
no rule counted in people (lane GR): on a table where a person column
is declared, answered or open, the phrase class only and no derived
option. It writes nothing, reads no key, and holds no count it hands
back but through the options it offers; the private notes it returns
carry a reason and never a count of 1 to `f - 1` rows.

ARITHMETIC. Python integers and exact fractions decide every failing
row, band, class and option. A number column's readings are held as
whole numbers at its own count of places; a pair is read at the larger
of its two. The rows are read in blocks of `BLOCK_ROWS`, each pair once
until it passes its limit, so the inference is linear in the rows
(limit 15's time bar, measured in plan P4-D459).
"""

import dataclasses
import fractions

from synthtwin import chain_rules as rules
from synthtwin import parsing, reading, taxonomy

KIND_NUMBER = rules.KIND_NUMBER
KIND_DATE = rules.KIND_DATE
KIND_CLOCK = rules.KIND_CLOCK
NUMBER_PAIR_ROLES = rules.NUMBER_PAIR_ROLES
# The rows read at once: a pair's readings are decoded and its gaps read one block of rows at a time, so
# what a pair holds beside the columns' compact readings is a function of the block, not of the rows.
BLOCK_ROWS = 16384
# MR.7's lines, read on the real table and never published (JUDGEMENT; lane RO's measurement in P4-D459).
SHARE_LINE = fractions.Fraction(1, 100)
HEAP_LINE = fractions.Fraction(99, 100)
READ_LINE = fractions.Fraction(99, 100)
ASSOCIATION_LINE = fractions.Fraction(1, 20)
# MR.10's NEAR-RULE reading (private): a pair over the limit whose failing share is under a fifth of BREAK.
NEAR_SHARE = fractions.Fraction(1, 5)
# MR.7's presence item (AMENDED 2026-11-05, LANE RO RULINGS 3 (5)): B's presence follows another column.
PRESENCE_LINE = fractions.Fraction(1, 20)
# MR.7's items that read whole columns (BREAK, the association) read at most this many rows, evenly
# strided: a score may read anything, a sample too, because the draw masks it (MR.3, MR.7).
SCORE_SAMPLE_ROWS = 20000
# The last clock value a layout writes, in seconds within the day.
_DAY_END = {1: 86399, 60: 86340}
# A column holding at most this many different readings keeps a palette of them and one byte a row.
_PALETTE_AT_MOST = 255


def _get(mapping: "dict[str, object]", key: str) -> object:
    if key in mapping:
        return mapping[key]
    return None


# -- ONE COLUMN READ UNDER ONE KIND (MR.2), HELD COMPACTLY (G4) --------------


@dataclasses.dataclass(frozen=True)
class Readings:
    """One column read under one kind over the tabled rows, held in bytes (lane RO's repair 1, G4).

    A reading is a number scaled by `10 ** places`, a day number, or
    seconds (a stamp's local seconds, a clock's seconds within the day).
    It is held one of three ways: a PALETTE of the column's different
    readings (`palette[0]` is None, no reading) and one byte a row naming
    its place in it; or WIDE, two to four bytes a row, low byte first, of
    the reading less `base` plus 1 (0 where the row holds none); or, past
    four bytes, a plain list (`plain`). A column holding no reading of
    the kind holds nothing a row at all. `clocked` is one byte a row
    where the column mixes date cells holding a time of day and cells
    holding none; elsewhere `clock_all` says which. A stamp's UTC offset
    in seconds is held as a palette too (`offsets`, one byte a row, and a
    second byte a row in `offset_high` where the column writes more than
    255 different offsets), or not at all where no cell holds one.
    `present` counts the cells holding something (not absent), `reads`
    the readings. `objects` is the bytes the readings of a `plain` list
    hold beside its slots (each a whole number of the interpreter's own).
    """

    kind: str
    rows: int
    places: int
    present: int
    reads: int
    palette: "tuple[int | None, ...] | None" = None
    planes: "tuple[bytearray, ...]" = ()
    base: int = 0
    plain: "list[int | None] | None" = None
    clocked: "bytearray | None" = None
    clock_all: bool = False
    offset_palette: "tuple[int | None, ...] | None" = None
    offset_codes: "bytearray | None" = None
    offset_high: "bytearray | None" = None
    objects: int = 0


def block_of(readings: Readings, start: int, stop: int) -> "list[int | None]":
    """The readings of rows `start` to `stop`, None where a row holds none."""
    if not readings.reads:
        return [None] * (stop - start)
    plain = readings.plain
    if plain is not None:
        return plain[start:stop]
    planes = readings.planes
    palette = readings.palette
    if palette is not None:
        return [palette[code] for code in planes[0][start:stop]]
    less = readings.base - 1
    stored: "list[int]" = []
    if len(planes) == 2:
        stored = [low | high << 8 for low, high in zip(planes[0][start:stop], planes[1][start:stop])]
    elif len(planes) == 3:
        stored = [low | middle << 8 | high << 16 for low, middle, high in zip(planes[0][start:stop], planes[1][start:stop], planes[2][start:stop])]
    else:
        stored = [
            low | second << 8 | third << 16 | high << 24
            for low, second, third, high in zip(planes[0][start:stop], planes[1][start:stop], planes[2][start:stop], planes[3][start:stop])
        ]
    return [code + less if code else None for code in stored]


def reading_at(readings: Readings, row: int) -> "int | None":
    """One row's reading, or None."""
    if not readings.reads:
        return None
    plain = readings.plain
    if plain is not None:
        return plain[row]
    palette = readings.palette
    if palette is not None:
        return palette[readings.planes[0][row]]
    code = 0
    for shift in range(len(readings.planes)):
        code |= readings.planes[shift][row] << (8 * shift)
    return code + readings.base - 1 if code else None


def clock_at(readings: Readings, row: int) -> bool:
    """Whether a date row's reading holds a time of day (its reading then in seconds, else in days)."""
    clocked = readings.clocked
    if clocked is not None:
        return bool(clocked[row])
    return readings.clock_all


def offset_at(readings: Readings, row: int) -> "int | None":
    """A stamp row's UTC offset in seconds east of UTC, or None where it holds none."""
    palette = readings.offset_palette
    codes = readings.offset_codes
    if palette is None or codes is None:
        return None
    high = readings.offset_high
    return palette[codes[row] | (high[row] << 8 if high is not None else 0)]


def offsets_in(readings: Readings, start: int, stop: int) -> "list[int | None]":
    """The UTC offsets of rows `start` to `stop` in seconds east of UTC, None where a row holds none."""
    palette = readings.offset_palette
    codes = readings.offset_codes
    if palette is None or codes is None:
        return [None] * (stop - start)
    high = readings.offset_high
    if high is None:
        return [palette[code] for code in codes[start:stop]]
    return [palette[low | top << 8] for low, top in zip(codes[start:stop], high[start:stop])]


def strided(readings: Readings, stride: int) -> Readings:
    """The readings of every `stride`-th row from the first (MR.7's sample)."""
    if stride == 1:
        return readings
    rows = len(range(0, readings.rows, stride))
    plain = readings.plain
    clocked = readings.clocked
    offset_codes = readings.offset_codes
    offset_high = readings.offset_high
    return dataclasses.replace(
        readings,
        rows=rows,
        planes=tuple(plane[0 : readings.rows : stride] for plane in readings.planes),
        plain=None if plain is None else plain[0 : readings.rows : stride],
        clocked=None if clocked is None else clocked[0 : readings.rows : stride],
        offset_codes=None if offset_codes is None else offset_codes[0 : readings.rows : stride],
        offset_high=None if offset_high is None else offset_high[0 : readings.rows : stride],
    )


def held_bytes(readings: Readings) -> int:
    """The bytes a column's readings hold over its rows (the inference's own, G4): its byte planes, and a
    `plain` list's slots of 8 bytes a row with the whole numbers they hold (lane RO's repair 2, the outside
    review's item 10: a reading whose scaled span reaches 2 to the 32 is held as a whole number of the
    interpreter's own, about 32 to 36 bytes beside its slot, not 8)."""
    held = 0
    for plane in readings.planes:
        held += len(plane)
    held += 0 if readings.clocked is None else len(readings.clocked)
    held += 0 if readings.offset_codes is None else len(readings.offset_codes)
    held += 0 if readings.offset_high is None else len(readings.offset_high)
    held += 0 if readings.plain is None else 8 * len(readings.plain) + readings.objects
    return held


def _object_bytes(value: int) -> int:
    """The bytes the interpreter holds a whole number in beside its slot: 24 and 4 a 30-bit digit, one at least."""
    digits = 1
    rest = (value if value >= 0 else -value) >> 30
    while rest:
        digits += 1
        rest >>= 30
    return 24 + 4 * digits


def _nonzero(codes: "bytes | bytearray") -> int:
    """The bytes of `codes` that are not 0."""
    return sum(map(bool, codes))


def _none_in(values: "list[int | None]") -> int:
    """The entries of `values` that are None."""
    return sum(1 for value in values if value is None)


def _empty(kind: str, rows: int, present: int) -> Readings:
    """A column holding no reading of `kind`: nothing held a row."""
    return Readings(kind, rows, 0, present, 0)


def _coded(texts: "list[str]", tabled_rows: "list[int] | range", code_of: "dict[str, int]") -> bytearray:
    """One byte a row: each tabled row's text's code, 0 where its text has none."""
    return bytearray(code_of[texts[row]] if texts[row] in code_of else 0 for row in tabled_rows)


def _held(
    kind: str,
    texts: "list[str]",
    tabled_rows: "list[int] | range",
    meaning: "dict[str, int]",
    present: int,
    places: int,
    clock_of: "dict[str, bool] | None" = None,
    offset_of: "dict[str, int | None] | None" = None,
) -> Readings:
    """A column's readings held compactly: `meaning` gives each text's reading, read once a text."""
    rows = len(tabled_rows)
    if not meaning:
        return _empty(kind, rows, present)
    readings = {meaning[text] for text in meaning}
    clocked: "bytearray | None" = None
    clock_all = False
    if clock_of is not None:
        clocks = {clock_of[text] for text in meaning}
        if len(clocks) == 1:
            clock_all = clocks == {True}
        else:
            clocked = _coded(texts, tabled_rows, {text: 1 for text in meaning if clock_of[text]})
    offset_palette: "tuple[int | None, ...] | None" = None
    offset_codes: "bytearray | None" = None
    offset_high: "bytearray | None" = None
    if offset_of is not None:
        written: "set[int]" = set()
        for text in meaning:
            offset = offset_of[text]
            if offset is not None:
                written |= {offset}
        offsets = sorted(written)
        if offsets:
            offset_palette = (None,) + tuple(offsets)
            place_of = {offsets[at]: at + 1 for at in range(len(offsets))}
            held_offset: "dict[str, int]" = {}
            for text in meaning:
                offset = offset_of[text]
                if offset is not None:
                    held_offset[text] = place_of[offset]
            # A column writing more than 255 different offsets names each by two bytes a row (lane RO's
            # repair 2, the outside review's item 11: the 256th raised in one byte).
            offset_codes = _coded(texts, tabled_rows, {text: held_offset[text] & 255 for text in held_offset})
            if len(offsets) > 255:
                offset_high = _coded(texts, tabled_rows, {text: held_offset[text] >> 8 for text in held_offset})
    if len(readings) <= _PALETTE_AT_MOST:
        ordered = sorted(readings)
        palette: "tuple[int | None, ...]" = (None,) + tuple(ordered)
        place_in = {ordered[at]: at + 1 for at in range(len(ordered))}
        codes = _coded(texts, tabled_rows, {text: place_in[meaning[text]] for text in meaning})
        reads = _nonzero(codes)
        return Readings(kind, rows, places, present, reads, palette, (codes,), 0, None, clocked, clock_all, offset_palette, offset_codes, offset_high)
    low = min(readings)
    span = max(readings) - low + 1
    width = 2 if span < 1 << 16 else (3 if span < 1 << 24 else (4 if span < 1 << 32 else 0))
    stored = {text: meaning[text] - low + 1 for text in meaning}
    if not width:
        plain = [meaning[texts[row]] if texts[row] in meaning else None for row in tabled_rows]
        reads = rows - _none_in(plain)
        objects = sum(_object_bytes(meaning[text]) for text in meaning)
        return Readings(kind, rows, places, present, reads, None, (), 0, plain, clocked, clock_all, offset_palette, offset_codes, offset_high, objects)
    parts: "list[bytearray]" = [bytearray() for _plane in range(width)]
    reads = 0
    for start in range(0, rows, BLOCK_ROWS):
        block = [stored[texts[row]] if texts[row] in stored else 0 for row in tabled_rows[start : start + BLOCK_ROWS]]
        reads += sum(map(bool, block))
        for shift in range(width):
            parts[shift] += bytearray((code >> (8 * shift)) & 255 for code in block)
    return Readings(kind, rows, places, present, reads, None, tuple(parts), low, None, clocked, clock_all, offset_palette, offset_codes, offset_high)


def _exact_number(number: float) -> "tuple[int, int] | None":
    """A number through its shortest decimal text: `(whole figures, places)` exactly (a workbook number)."""
    text = repr(number)
    if text in ("nan", "inf", "-inf"):
        return None
    value = fractions.Fraction(text)
    return _figures_and_places(value)


def _figures_and_places(value: fractions.Fraction) -> "tuple[int, int] | None":
    """An exact terminating decimal as `(whole figures, places)`; None where it does not terminate."""
    denominator = value.denominator
    twos = 0
    fives = 0
    while denominator % 2 == 0:
        denominator //= 2
        twos += 1
    while denominator % 5 == 0:
        denominator //= 5
        fives += 1
    if denominator != 1:
        return None
    places = max(twos, fives)
    return value.numerator * 10**places // value.denominator, places


def exact_cell(text: str, number: float, prefix: str, suffix: str, comma: bool) -> "tuple[int, int] | None":
    """A number cell read EXACTLY from its written figures (MR.2: binary64 never decides a failing row).

    The cell's core (inside an affixed column's prefix and suffix, '' and
    '' on a column that writes none), read with a declared decimal comma
    as the point, through the reader of record's exact triple
    (`parsing.exact_of_spelling`), so a cell of 17 or more figures keeps
    them all; where that reading does not round to the number the
    column's own reader gave, the number's shortest text is read instead
    (the reader of record decides what a cell is).
    """
    if not isinstance(text, str):
        raise TypeError("a cell is text")
    if not isinstance(prefix, str):
        raise TypeError("an affix is text")
    if not isinstance(suffix, str):
        raise TypeError("an affix is text")
    core = text.strip()
    before = prefix.strip()
    after = suffix.strip()
    if before or after:
        if not (core.startswith(before) and core.endswith(after)):
            return _exact_number(number)
        core = core[len(before) : len(core) - len(after)].strip()
    if comma:
        core = core.replace(".", "").replace(" ", "").replace(",", ".")
    triple = parsing.exact_of_spelling(core) if core else None
    if triple is None:
        return _exact_number(number)
    sign, digits, power = triple
    figures = ""
    for figure in digits:
        figures += f"{figure}"
    whole = sign * (rules.figures_of(figures) or 0)
    value = fractions.Fraction(whole) * fractions.Fraction(10) ** power
    if float(value) != number:
        return _exact_number(number)
    return _figures_and_places(value)


def _offset_seconds(offset: str) -> "int | None":
    """A written UTC offset (`Z`, `+05:30`, `-0800`) in seconds east of UTC; None where none is written."""
    if not offset:
        return None
    if offset in ("Z", "z"):
        return 0
    sign = -1 if offset[0] == "-" else 1
    figures = ""
    for letter in offset[1:]:
        if "0" <= letter <= "9":
            figures += letter
    read = rules.figures_of(figures)
    if read is None:
        return None
    if len(figures) == 2:
        return sign * read * 3600
    if len(figures) == 4:
        return sign * ((read // 100) * 3600 + (read % 100) * 60)
    return None


def _canonical_moment(canonical: str) -> "tuple[int, int | None]":
    """A canonical date (`YYYY-MM-DD`) or stamp (`YYYY-MM-DD HH:MM:SS`): (day number, seconds or None)."""
    day = parsing.days_from_civil(int(canonical[0:4]), int(canonical[5:7]), int(canonical[8:10]))
    if len(canonical) >= 19:
        seconds = int(canonical[11:13]) * 3600 + int(canonical[14:16]) * 60 + int(canonical[17:19])
        return day, day * rules.DAY_SECONDS + seconds
    return day, None


def readings_of(
    texts: "list[str]",
    spelled: "dict[str, tuple[str, float | None, str]]",
    block: "dict[str, object]",
    kind: str,
    declared: "dict[str, bool]",
    tabled_rows: "list[int] | range",
) -> Readings:
    """Column cells read under `kind` by the column's OWN reader (MR.2): its layout read from its own cells.

    `texts` are the column's cells in row order and `spelled` its own
    reader's decision on each spelling (`taxonomy.spellings_read`), as
    the chain's describe already holds them, so nothing is read again.
    """
    role = f"{_get(block, 'role')}"
    rows = len(tabled_rows)
    if (kind == KIND_DATE and role != rules.ROLE_DATETIME) or (kind == KIND_CLOCK and role != rules.ROLE_CLOCK):
        # No cell of a column of another role reads as a date or a clock: its present cells
        # are its published present count, and it holds no reading.
        present_cells = _get(block, "n_present")
        count = present_cells if isinstance(present_cells, int) and not isinstance(present_cells, bool) else 0
        return _empty(kind, rows, count)
    present_texts = {text for text in spelled if spelled[text][0] != "missing"}
    present = sum(1 for row in tabled_rows if texts[row] in present_texts)
    meaning: "dict[str, int]" = {}
    if kind == KIND_NUMBER and role not in (rules.ROLE_JOINED, rules.ROLE_COMPOUND):
        prefix = _get(block, "affix_prefix")
        suffix = _get(block, "affix_suffix")
        affixed = role == rules.ROLE_AFFIXED and isinstance(prefix, str) and isinstance(suffix, str)
        exact: "dict[str, tuple[int, int]]" = {}
        places = 0
        for text in present_texts:
            cell_kind, number, _text = spelled[text]
            if affixed:
                assert isinstance(prefix, str) and isinstance(suffix, str)
                core = taxonomy.core_read(text, prefix, suffix, declared["decimal_comma"])
                if core is None or core[0] != parsing.NUMBER or core[1] is None:
                    continue
                number = core[1]
            elif cell_kind != parsing.NUMBER or number is None:
                continue
            found = exact_cell(
                text,
                float(number),
                prefix if affixed and isinstance(prefix, str) else "",
                suffix if affixed and isinstance(suffix, str) else "",
                declared["decimal_comma"],
            )
            if found is not None:
                exact[text] = found
                places = max(places, found[1])
        for text in exact:
            whole, own = exact[text]
            meaning[text] = whole * 10 ** (places - own)
        return _held(kind, texts, tabled_rows, meaning, present, places)
    if kind == KIND_DATE:
        form = _get(block, "format")
        clock_of: "dict[str, bool]" = {}
        offset_of: "dict[str, int | None]" = {}
        if isinstance(form, str):
            for text in present_texts:
                parsed = parsing.parse_datetime(spelled[text][2], form)
                # A partial date (a month, a quarter) holds no reading: it opens no step (MR.2; lane RO's
                # repair 2, the sibling check of the verify's item 1: a month column beside a date raised).
                if parsed is None or len(parsed[0]) < 10:
                    continue
                day, seconds = _canonical_moment(parsed[0])
                meaning[text] = day if seconds is None else seconds
                clock_of[text] = seconds is not None
                offset_of[text] = _offset_seconds(parsed[1])
        return _held(kind, texts, tabled_rows, meaning, present, 0, clock_of, offset_of)
    if kind == KIND_CLOCK:
        form = _get(block, "clock_form")
        if isinstance(form, str) and form in parsing.CLOCK_FORMS:
            step = parsing.clock_step(form)
            for text in present_texts:
                ordinal = parsing.clock_ordinal(text, form)
                if ordinal is not None:
                    meaning[text] = ordinal * step
        return _held(kind, texts, tabled_rows, meaning, present, 0)
    return _held(kind, texts, tabled_rows, meaning, present, 0)


def kinds_held(block: "dict[str, object]") -> "tuple[str, ...]":
    """The kinds a column is read under: numbers always, and dates or clocks by its role."""
    role = _get(block, "role")
    if role == rules.ROLE_DATETIME:
        return (KIND_NUMBER, KIND_DATE)
    if role == rules.ROLE_CLOCK:
        return (KIND_NUMBER, KIND_CLOCK)
    return (KIND_NUMBER,)


def read_under(
    table: reading.Table,
    place: int,
    block: "dict[str, object]",
    kind: str,
    settings: taxonomy.Settings,
    declared: "dict[str, bool]",
    stored_as: str,
    tabled_rows: "list[int]",
) -> Readings:
    """Column `place` of a table read under `kind` by its OWN reader (MR.2), reading the column itself.

    The validator's route (V12): the inference itself never calls it,
    and takes its readings from the cells the chain's describe reads
    (`Gathered`).
    """
    role = f"{_get(block, 'role')}"
    if (kind == KIND_DATE and role != rules.ROLE_DATETIME) or (kind == KIND_CLOCK and role != rules.ROLE_CLOCK):
        return readings_of([], {}, block, kind, declared, tabled_rows)
    texts = reading.column_values(table, place)
    spelled = taxonomy.spellings_read(
        texts,
        f"{_get(block, 'name')}",
        settings,
        forced_code=declared["code"],
        forced_measurement=declared["measurement"],
        forced_decimal_comma=declared["decimal_comma"],
        stored_as=stored_as,
    )
    return readings_of(texts, spelled, block, kind, declared, tabled_rows)


@dataclasses.dataclass(frozen=True)
class Gathered:
    """Every column's readings the inference reads, taken kind by kind from the cells the describe reads.

    `chain.describe` hands each column's cells and its reader's decision
    to `gather` as it reads them in schema order, so the inference reads no
    column of the file again (G4: a column the describe does not read
    for its own families, a candidate `B`, is read once, in its place).
    A column with no reading of a kind holds nothing a row for it.
    """

    rows: int
    held: "dict[tuple[str, str], Readings]"
    present: "dict[str, int]"


def gathered_for(rows: int) -> Gathered:
    """An empty store for a table of `rows` tabled rows."""
    return Gathered(rows, {}, {})


def gather(
    gathered: Gathered,
    name: str,
    block: "dict[str, object]",
    texts: "list[str]",
    spelled: "dict[str, tuple[str, float | None, str]]",
    declared: "dict[str, bool]",
    tabled_rows: "list[int] | range",
) -> None:
    """Read one column under each kind it is read under (`kinds_held`) and keep what it holds."""
    for kind in kinds_held(block):
        gathered.held[(name, kind)] = readings_of(texts, spelled, block, kind, declared, tabled_rows)
    present_cells = _get(block, "n_present")
    gathered.present[name] = present_cells if isinstance(present_cells, int) and not isinstance(present_cells, bool) else 0


def let_go(gathered: Gathered, name: str) -> None:
    """Let a column's readings go."""
    for kind in (KIND_NUMBER, KIND_DATE, KIND_CLOCK):
        if (name, kind) in gathered.held:
            del gathered.held[(name, kind)]


def readings_for(gathered: Gathered, name: str, kind: str) -> Readings:
    """A column's readings under `kind`: what it holds, or nothing where it holds no reading of the kind."""
    if (name, kind) in gathered.held:
        return gathered.held[(name, kind)]
    return _empty(kind, gathered.rows, gathered.present[name] if name in gathered.present else 0)


def gathered_bytes(gathered: Gathered) -> int:
    """The bytes held a row, over every column and kind (the inference's own memory, G4)."""
    return sum(held_bytes(gathered.held[key]) for key in gathered.held)


def computed_refused(block: "dict[str, object]", held: "set[str]", identifiers: "set[str]") -> bool:
    """OPEN1 on `B`: named `identifier` by the person, held, top-coded, year-pooled, or first written in E-notation.

    A Safe Harbor question put on `B` and still open holds it (it is in
    the switch's held columns); one answered `no` leaves none of these.
    """
    name = f"{_get(block, 'name')}"
    if name in identifiers or name in held or _get(block, "held") is True:
        return True
    if _get(block, "role") == "identifier" or _get(block, "structural_role") == "identifier":
        return True
    top = _get(block, "top_coded")
    year = _get(block, "top_coded_year")
    if (top is not None and top != 0) or (year is not None and year != 0):
        return True
    return rules.first_style(block) in ("exponent_lower", "exponent_upper")


def takes_part(block: "dict[str, object]", eligible_so_far: bool, held: "set[str]", identifiers: "set[str]") -> bool:
    """Whether a column's readings are gathered: a `B` OPEN1 admits, or a column that may be `A` or a source."""
    if not computed_refused(block, held, identifiers):
        return True
    return eligible_so_far and rules.kind_of_role(_get(block, "role")) is not None and not rules.has_exponent(block)


# -- A PAIR READ ROW BY ROW (MR.2) --------------------------------------------


@dataclasses.dataclass(frozen=True)
class PairReading:
    """How a pair reads `D`: its grain, `D`'s unit in seconds (dates and clocks) and the scale of a number pair."""

    kind: str
    grain: "str | None"
    seconds: bool
    scale_a: int
    scale_b: int
    # Whether MR.7's BREAK reads each stamp at its instant, as `gap_of` reads a row: a pair read in
    # seconds whose two columns both write UTC offsets (lane RO's repair 2, the outside review's item 8).
    instants: bool = False


def pair_reading(kind: str, a_block: "dict[str, object]", b_block: "dict[str, object]", a: Readings, b: Readings) -> PairReading:
    """The pair's reading: grain `day` where every `A` layout holds a clock and `B` is written as dates."""
    if kind == KIND_NUMBER:
        places = max(a.places, b.places)
        return PairReading(kind, None, False, 10 ** (places - a.places), 10 ** (places - b.places))
    if kind == KIND_CLOCK:
        return PairReading(kind, rules.GRAIN_A, True, 1, 1)
    clocked = rules.every_layout_clocked(a_block)
    if clocked and _get(b_block, "role") == rules.ROLE_DATETIME and not rules.first_layout_clocked(b_block):
        return PairReading(kind, rules.GRAIN_DAY, False, 1, 1)
    return PairReading(kind, rules.GRAIN_A, clocked, 1, 1, clocked and a.offset_palette is not None and b.offset_palette is not None)


def _day_of(value: int, clocked: bool) -> int:
    return value // rules.DAY_SECONDS if clocked else value


def gap_of(pair: PairReading, a: Readings, b: Readings, row: int) -> "tuple[int | None, bool]":
    """One row's `D` in the pair's unit and whether the row FAILS (MR.1, MR.2).

    Returns (None, False) where either column holds no reading. A row
    fails where `D` is below 0, and, in a date pair, where `B`'s cell
    holds a clock under grain `day` or none beside `A`'s clock under grain
    `A` read in seconds (such a row has no reading of `D`).
    """
    first = reading_at(a, row)
    second = reading_at(b, row)
    if first is None or second is None:
        return None, False
    if pair.kind == KIND_NUMBER:
        gap = second * pair.scale_b - first * pair.scale_a
        return gap, gap < 0
    if pair.kind == KIND_CLOCK:
        gap = second - first
        return gap, gap < 0
    a_clock = clock_at(a, row)
    b_clock = clock_at(b, row)
    if pair.grain == rules.GRAIN_DAY:
        if b_clock:
            return None, True
        gap = _day_of(second, b_clock) - _day_of(first, a_clock)
        return gap, gap < 0
    if pair.seconds:
        if not b_clock:
            return None, True
        a_offset = offset_at(a, row)
        b_offset = offset_at(b, row)
        if a_offset is not None and b_offset is not None:
            gap = (second - b_offset) - (first - a_offset)
        else:
            gap = second - first
        return gap, gap < 0
    gap = _day_of(second, b_clock) - _day_of(first, a_clock)
    return gap, gap < 0


def pair_gaps(pair: PairReading, a: Readings, b: Readings, start: int = 0, end: "int | None" = None) -> "tuple[list[int | None], int]":
    """Each row's `D` from `start` to `end` (None where either reads nothing), and the rows that fail with
    no reading of `D` (a date cell of the wrong resolution under the pair's grain): `gap_of`, row by row,
    in one pass over the rows' readings, decoded a block at a time."""
    stop = a.rows if end is None else end
    firsts = block_of(a, start, stop)
    seconds = block_of(b, start, stop)
    if pair.kind == KIND_NUMBER:
        if pair.scale_a == 1 and pair.scale_b == 1:
            return [None if x is None or y is None else y - x for x, y in zip(firsts, seconds)], 0
        scale_a = pair.scale_a
        scale_b = pair.scale_b
        return [None if x is None or y is None else y * scale_b - x * scale_a for x, y in zip(firsts, seconds)], 0
    if pair.kind == KIND_CLOCK:
        return [None if x is None or y is None else y - x for x, y in zip(firsts, seconds)], 0
    day = rules.DAY_SECONDS
    if a.clocked is None and b.clocked is None and (a.offset_codes is None or b.offset_codes is None or not pair.seconds):
        # Each column's readings are all in seconds or all in days.
        a_all = a.clock_all
        b_all = b.clock_all
        if pair.grain == rules.GRAIN_DAY:
            if b_all:
                held = [None if x is None or y is None else 0 for x, y in zip(firsts, seconds)]
                return [None] * len(held), len(held) - _none_in(held)
            if a_all:
                return [None if x is None or y is None else y - x // day for x, y in zip(firsts, seconds)], 0
            return [None if x is None or y is None else y - x for x, y in zip(firsts, seconds)], 0
        if pair.seconds:
            if not b_all:
                held = [None if x is None or y is None else 0 for x, y in zip(firsts, seconds)]
                return [None] * len(held), len(held) - _none_in(held)
            return [None if x is None or y is None else y - x for x, y in zip(firsts, seconds)], 0
        if a_all and b_all:
            return [None if x is None or y is None else y // day - x // day for x, y in zip(firsts, seconds)], 0
        if a_all:
            return [None if x is None or y is None else y - x // day for x, y in zip(firsts, seconds)], 0
        if b_all:
            return [None if x is None or y is None else y // day - x for x, y in zip(firsts, seconds)], 0
        return [None if x is None or y is None else y - x for x, y in zip(firsts, seconds)], 0
    gaps: "list[int | None]" = []
    odd_rows = 0
    for row in range(start, stop):
        gap, fails = gap_of(pair, a, b, row)
        gaps += [gap]
        if gap is None and fails:
            odd_rows += 1
    return gaps, odd_rows


def spans(rows: int) -> "list[tuple[int, int]]":
    """The blocks a pass reads its rows in: 256 rows, then twice as many each time up to `BLOCK_ROWS`, so a
    pass that stops at its first few failing rows decodes few rows."""
    out: "list[tuple[int, int]]" = []
    start = 0
    size = 256
    while start < rows:
        stop = min(rows, start + size)
        out += [(start, stop)]
        start = stop
        size = min(BLOCK_ROWS, size * 2)
    return out


def failing_rows(pair: PairReading, a: Readings, b: Readings, limit: int) -> int:
    """`v`, read in blocks of rows and stopped at its first `limit + 1` failing rows (MR.3)."""
    rows = a.rows
    count = 0
    for start, stop in spans(rows):
        gaps, odd = pair_gaps(pair, a, b, start, stop)
        count += odd + sum(1 for gap in gaps if gap is not None and gap < 0)
        if count > limit:
            return count
    return count


@dataclasses.dataclass(frozen=True)
class _Passed:
    """One pair read through its rows once (MR.3): `v` (stopped past `limit`), and where it stopped not,
    the joint of `A`'s `L0` band and `D` with its rows, the rows where both read, those where `D` is 0,
    and those where `B` reads and `A` does not."""

    v: int
    joint: "dict[tuple[int, int | None], int]"
    both: int
    zero: int
    b_without_a: int


def _pair_pass(pair: PairReading, a: Readings, b: Readings, limit: int, codes: "bytes | bytearray | list[int]") -> _Passed:
    """`v` and, below the limit, the joint `(A's L0 band, D)`: one pass over the rows, a block at a time."""
    rows = a.rows
    v = 0
    joint: "dict[tuple[int, int | None], int]" = {}
    both = 0
    zero = 0
    b_without_a = 0
    for start, stop in spans(rows):
        gaps, odd = pair_gaps(pair, a, b, start, stop)
        v += odd + sum(1 for gap in gaps if gap is not None and gap < 0)
        if v > limit:
            return _Passed(v, {}, 0, 0, 0)
        for key in zip(codes[start:stop], gaps):
            joint[key] = joint[key] + 1 if key in joint else 1
        both += len(gaps) - _none_in(gaps)
        zero += sum(1 for gap in gaps if gap == 0)
        if a.reads < rows and b.reads:
            b_without_a += sum(1 for x, y in zip(block_of(a, start, stop), block_of(b, start, stop)) if x is None and y is not None)
    return _Passed(v, joint, both, zero, b_without_a)


# -- AN OPEN STEP'S OPTIONS ----------------------------------------------------


@dataclasses.dataclass(frozen=True)
class Option:
    """One CARRIED option of a rule's step (4.6b.7).

    A derived option names `D`'s `level` (name, percents, edges in `D`'s
    unit), `A`'s `a_level` and the family `{D | A}`'s `table` (one row a
    band of `A` at that level, one count a value band of `D`, the last
    `D`'s `missing` band) and `totals`; a source option names its
    `carrier` column and `unit`. `klass` is the class it publishes,
    `score` its score (MR.7), `worth` whether MR.7's list leaves it worth
    carrying (private).
    """

    carrier: str
    unit: "str | None"
    level: "tuple[str, tuple[int, ...], tuple[fractions.Fraction, ...]] | None"
    a_level: "int | None"
    totals: "tuple[int, ...]"
    table: "tuple[tuple[int, ...], ...]"
    klass: "str | int"
    score: fractions.Fraction
    worth: bool


@dataclasses.dataclass(frozen=True)
class Inferred:
    """One inferred rule whose step OPENED (MR.3), with its eligible carried options in option order.

    `step` is the grain `g` in `D`'s unit (a day is 1 where `D` reads
    whole days); `seconds` whether `D` reads seconds. `why` is the
    private reason MR.7 leaves it not worth carrying, '' where it is
    worth it.
    """

    kind: str
    computed: str
    inputs: "tuple[str, ...]"
    pair: str
    grain: "str | None"
    seconds: bool
    step: "fractions.Fraction | None"
    options: "tuple[Option, ...]"
    why: str
    # Whether the rule's ANTECEDENT, the rows where both columns hold a
    # reading, numbers at least `f` (4.6b.7's opening paragraph): only such
    # a rule RAISES the chain's weights (W5's raise, a weight the draw masks).
    antecedent: bool = False


@dataclasses.dataclass(frozen=True)
class Inference:
    """What `infer_rules` hands back: the open steps in step order, the pairs over the limit (each `(A, B)`;
    MR.10's NEAR-RULE reading of them is owed, lane RO2), the private notes and the pairs read."""

    rules: "tuple[Inferred, ...]"
    near: "tuple[tuple[str, str], ...]"
    notes: "tuple[str, ...]"
    pairs_read: int


def _histogram(joint: "dict[tuple[int, int | None], int]") -> "list[tuple[int, int]]":
    """`D`'s readings with their rows, ascending."""
    counts: "dict[int, int]" = {}
    for key in joint:
        gap = key[1]
        if gap is None:
            continue
        counts[gap] = counts[gap] + joint[key] if gap in counts else joint[key]
    return sorted((gap, counts[gap]) for gap in counts)


def _family_table(
    joint: "dict[tuple[int, int | None], int]",
    ladder: rules.Ladder,
    a_level: int,
    edges: "tuple[fractions.Fraction, ...]",
    unit: fractions.Fraction,
    band_of_gap: "dict[int, int] | None" = None,
) -> "list[list[int]]":
    """The family `{D | A}` at `A`'s level: one row a band of `A`, one count a value band of `D` and its `missing` band.

    `band_of_gap`, where given, holds each reading's value band at these
    edges (`_bands_of_gaps`), shared by `A`'s three levels.
    """
    values = len(edges) + 1
    table = [[0] * (values + 1) for _band in range(ladder.counts[a_level])]
    bands = band_of_gap if band_of_gap is not None else _bands_of_gaps(joint, edges, unit)
    to_row = ladder.maps[a_level]
    for key in joint:
        band, gap = key
        rows = joint[key]
        row = to_row[band]
        if gap is None:
            table[row][values] += rows
            continue
        table[row][bands[gap]] += rows
    return table


def _bands_of_gaps(
    joint: "dict[tuple[int, int | None], int]",
    edges: "tuple[fractions.Fraction, ...]",
    unit: fractions.Fraction,
) -> "dict[int, int]":
    """Each reading's value band of `D` at `edges`, bands closed on the RIGHT, read in whole numbers: a reading
    `x` (`D` is `x` times `unit`) lies above an edge `e` exactly where `x` exceeds the floor of `e / unit`."""
    thresholds: "list[int]" = []
    for edge in edges:
        ratio = edge / unit
        thresholds += [ratio.numerator // ratio.denominator]
    out: "dict[int, int]" = {}
    for key in joint:
        gap = key[1]
        if gap is None or gap in out:
            continue
        band = 0
        for threshold in thresholds:
            if threshold < gap:
                band += 1
        out[gap] = band
    return out


def _missing_alone(ladder: rules.Ladder) -> bool:
    """Rule 2: `A`'s `missing` band is an `L0` band of its own (or `A` has none)."""
    for band in ladder.l0:
        if rules.MISSING in band and len(band) > 1:
            return False
    return True


def _spread_rows(ladder: rules.Ladder, a_level: int) -> "set[int]":
    """The bands of `A` at a level that hold no reading of `A` (its spread bands alone)."""
    out: "set[int]" = set()
    for band in range(ladder.counts[a_level]):
        members = [place for place in range(len(ladder.totals)) if ladder.maps[a_level][place] == band]
        if members and not any(ladder.ordered[place] for place in members):
            out = out | {band}
    return out


def a_readings_total(ladder: rules.Ladder) -> int:
    """`R`, the rows where `A` holds a reading, read from its published `L0` totals (Proposition T)."""
    return sum(ladder.totals[place] for place in range(len(ladder.totals)) if ladder.ordered[place])


def derived_options(
    joint: "dict[tuple[int, int | None], int]",
    ladder: rules.Ladder,
    groups: "frozenset[int]",
    v: int,
    step: fractions.Fraction,
    unit: fractions.Fraction,
    f: int,
    limit: int,
    phrase_only: bool,
    tabled: int,
) -> "tuple[list[Option], dict[str, int]]":
    """Every pair of a level of `D` and a level of `A` eligible under rules 1 to 6, the one test and the class.

    `unit` turns a reading into `D`'s unit (1, or `10 ** -places` on a
    number pair). Returns the options in option order (`D`'s levels from
    the finest, then `A`'s) and the refusals by reason (private).
    """
    refusals: "dict[str, int]" = {}
    histogram = [(fractions.Fraction(pair[0]) * unit, pair[1]) for pair in _histogram(joint)]
    if not histogram:
        return [], {"no reading of D": 1}
    klass = rules.class_of(v, a_readings_total(ladder), f, limit, phrase_only)
    missing_alone = _missing_alone(ladder)
    out: "list[Option]" = []
    for level in rules.derived_levels(histogram):
        totals = rules.derived_totals(level[2], histogram)
        band_of_gap = _bands_of_gaps(joint, level[2], unit)
        for a_level in range(3):
            table = _family_table(joint, ladder, a_level, level[2], unit, band_of_gap)
            group_rows = {ladder.maps[a_level][band] for band in groups}
            refused = rules.derived_option_refusal(
                level, totals, table, _spread_rows(ladder, a_level), missing_alone, group_rows,
                klass, step, f,
            )
            if refused is not None:
                refusals[refused] = refusals[refused] + 1 if refused in refusals else 1
                continue
            assert klass is not None
            flat = [cell for line in table for cell in line]
            score = rules.W_RULE * tabled + rules.score(flat, len(table), len(table[0]))
            out += [Option(rules.CARRIER_DERIVED, None, level, a_level, tuple(totals), tuple(tuple(line) for line in table), klass, score, True)]
    return out, refusals


def source_failing(
    pair: PairReading,
    a: Readings,
    b: Readings,
    d: Readings,
    unit_seconds: int,
    b_end: "int | None",
    f: int,
) -> int:
    """A source option's failing rows (MR.1), stopped at `f`: the order's own, the rows where `B` differs
    from `A + D x unit` held at the last value `B`'s layout writes (REPAIR 2), and a reading on one side
    only (`A + D` read and `B` not, or `B` read and `A + D` not)."""
    count = 0
    places = max(a.places, b.places)
    scale = 10**d.places
    rows = a.rows
    for start, stop in spans(rows):
        firsts = block_of(a, start, stop)
        seconds = block_of(b, start, stop)
        lengths = block_of(d, start, stop)
        gaps = pair_gaps(pair, a, b, start, stop)[0]
        for at in range(stop - start):
            first = firsts[at]
            length = lengths[at]
            second = seconds[at]
            summed = first is not None and length is not None
            gap = gaps[at]
            if second is None or not summed:
                if (second is not None) != summed:
                    count += 1
            elif gap is None or gap < 0 or first is None or length is None:
                # A date cell of the wrong resolution under the grain fails with no reading of `D`.
                count += 1
            elif pair.kind == KIND_NUMBER:
                # B - A, at 10 ** -places, against D at 10 ** -d.places, times the unit 1.
                if gap * scale != length * 10**places:
                    count += 1
            elif pair.seconds or pair.kind == KIND_CLOCK:
                # Seconds: `A + D x unit`, exactly, held at the last value B's layout writes.
                if (length * unit_seconds) % scale:
                    count += 1
                else:
                    want = length * unit_seconds // scale
                    if b_end is not None and first + want > b_end:
                        want = b_end - first
                    if gap != want:
                        count += 1
            elif gap * rules.DAY_SECONDS * scale != length * unit_seconds:
                # Whole days: the gap in seconds against `D x unit`, exactly.
                count += 1
            if count >= f:
                return count
    return count


def source_options(
    pair: PairReading,
    a: Readings,
    b: Readings,
    a_block: "dict[str, object]",
    b_block: "dict[str, object]",
    sources: "list[tuple[str, dict[str, object], Readings]]",
    step: fractions.Fraction,
    f: int,
) -> "tuple[list[Option], list[str]]":
    """Every source column and unit whose failing rows number at most `f - 1`, under MR.3's three
    source conditions and `n_negative` 0, ordered by column, then by unit, largest first."""
    out: "list[Option]" = []
    refused: "list[str]" = []
    units: "tuple[tuple[str, int], ...]" = ((rules.UNIT_ONE, 1),) if pair.kind == KIND_NUMBER else rules.TIME_UNITS
    for name, block, d in sources:
        if d.reads == 0:
            continue
        for unit_word, _unit_seconds in units:
            why = rules.source_refusal(unit_word, pair.kind, pair.seconds or pair.kind == KIND_CLOCK, step, block, b_block)
            if why is not None:
                refused += [f"{name} by the {unit_word}: {why}"]
                continue
            negative = _get(block, "n_negative")
            if negative != 0:
                refused += [f"{name}: its own block publishes negative readings"]
                continue
            b_step = rules.first_step(b_block, pair.kind)
            b_end = None
            if pair.kind == KIND_CLOCK and b_step is not None:
                b_end = _DAY_END[1] if b_step == 1 else _DAY_END[60]
            failing = source_failing(pair, a, b, d, dict(rules.TIME_UNITS)[unit_word] if unit_word in dict(rules.TIME_UNITS) else 1, b_end, f)
            if failing <= f - 1:
                out += [Option(name, unit_word, None, None, (), (), rules.CLASS_PHRASE, fractions.Fraction(0), True)]
    return out, refused


# -- MR.7: WHAT MAY READ THE REAL TABLE -------------------------------------------


def _stride(rows: int) -> int:
    """The stride of the rows MR.7's whole-column items read: every row, or an even `SCORE_SAMPLE_ROWS`."""
    return max(1, -(-rows // SCORE_SAMPLE_ROWS))


def _sampled(rows: int) -> "range":
    """The rows MR.7's whole-column items read: every row, or an even stride of `SCORE_SAMPLE_ROWS`."""
    return range(0, rows, _stride(rows))


def _in_unit(readings: Readings, pair: PairReading, scale: int) -> "list[int | None]":
    """A column's readings at every row in the pair's unit: a number at the pair's places, days on a
    date pair whose `D` reads days (a clocked cell's day), seconds otherwise, at the instant (the local
    seconds less the row's offset) where the pair reads instants."""
    values = block_of(readings, 0, readings.rows)
    if pair.instants:
        offsets = offsets_in(readings, 0, readings.rows)
        return [None if value is None else value - (offset if offset is not None else 0) for value, offset in zip(values, offsets)]
    if pair.kind == KIND_DATE and not pair.seconds:
        if readings.clocked is not None:
            return [None if value is None else _day_of(value, bool(clocked)) for value, clocked in zip(values, readings.clocked)]
        if readings.clock_all:
            return [None if value is None else value // rules.DAY_SECONDS for value in values]
        return values
    if scale != 1:
        return [None if value is None else value * scale for value in values]
    return values


def _sorted_sample(readings: Readings, pair: PairReading, scale: int) -> "list[int]":
    """A column's sampled readings in the pair's unit, ascending (BREAK's side)."""
    return sorted(value for value in _in_unit(strided(readings, _stride(readings.rows)), pair, scale) if value is not None)


def _break_share(a: Readings, b: Readings, pair: PairReading, firsts: "list[int] | None" = None) -> fractions.Fraction:
    """BREAK: the exact share of pairs (a reading of `A`, a reading of `B`) with `B` below `A`, at the pair's
    unit, over the sampled rows' readings. `firsts`, where given, is `A`'s side already read
    (`_sorted_sample`)."""
    stride = _stride(a.rows)
    if firsts is None:
        firsts = _sorted_sample(a, pair, pair.scale_a)
    seconds = sorted(value for value in _in_unit(strided(b, stride), pair, pair.scale_b) if value is not None)
    if not firsts or not seconds:
        return fractions.Fraction(0)
    above = 0
    at = 0
    # For each B reading, the A readings strictly above it.
    for value in seconds:
        while at < len(firsts) and firsts[at] <= value:
            at += 1
        above += len(firsts) - at
    return fractions.Fraction(above, len(firsts) * len(seconds))


@dataclasses.dataclass
class _Candidate:
    """A pair under study: its reading, `v`, its derived options, and the facts MR.7's list reads (private)."""

    a: str
    b: str
    kind: str
    reading: PairReading
    v: int
    both: int
    b_without_a: int
    median: fractions.Fraction
    unit: fractions.Fraction
    step: "fractions.Fraction | None"
    gap_zero: int
    derived: "tuple[Option, ...]"
    # The mean of |D| over the rows where both read (the tighter-rule item's tie, MR.7 as amended).
    mean_size: fractions.Fraction = fractions.Fraction(0)


def _median(histogram: "list[tuple[fractions.Fraction, int]]") -> fractions.Fraction:
    total = sum(rows for _value, rows in histogram)
    if not total:
        return fractions.Fraction(0)
    half = (total - 1) // 2
    seen = 0
    for value, rows in histogram:
        seen += rows
        if seen > half:
            return value
    return histogram[-1][0]


def derived_option_worth(edges: "tuple[fractions.Fraction, ...] | list[fractions.Fraction]", gap_zero: int, both: int) -> bool:
    """MR.7's item on ONE derived option (REPAIR 2, AMENDED 2026-11-05 by the orchestrator's ruling, lane RO's
    repair 1): a level of `D` with no edge writes `B` as `A`, so it is NOT WORTH carrying unless the real
    gap is 0 on at least 99 of 100 of the rows where both read (a heap at 0, limit 19); a level with an
    edge is not judged here."""
    if edges:
        return True
    return both > 0 and fractions.Fraction(gap_zero, both) >= HEAP_LINE


def option_score(worth: bool, u: fractions.Fraction, tabled: int) -> fractions.Fraction:
    """A carried derived option's score (MR.7): `w_rule n` plus its family's `u`, or `-w_rule n` NOT WORTH."""
    return rules.W_RULE * tabled + u if worth else -rules.W_RULE * tabled


def infer_rules(
    gathered: Gathered,
    blocks: "list[dict[str, object]]",
    settings: taxonomy.Settings,
    eligible: "dict[str, rules.Ladder]",
    groups: "dict[str, frozenset[int]]",
    codes: "dict[str, bytes | list[int]]",
    tabled: int,
    held: "set[str]",
    identifiers: "set[str]",
    dropped: "frozenset[tuple[str, str]]",
    person: bool,
) -> Inference:
    """MR.3 exactly: every rule whose step opens on the table, with its eligible options and scores.

    `gathered` holds every column's readings, taken from the cells the
    describe read; `eligible` maps each eligible column to its ladder,
    `groups` to its own-fact groups (`L0` bands) and `codes` to its `L0`
    band on each tabled row, as `chain.describe` read them; `held` and
    `identifiers` the columns held or named `identifier`; `dropped` the
    questions file's pairs to drop, each in both orders; `person` whether
    a person column is declared, answered or open on a table of several
    rows a person (the phrase only, and no derived option). Returns the
    open steps in step order (the computed column's schema order,
    `formula` before `order`, then the inputs). Each pair is read once a
    block of rows at a time; its joint with `A`'s bands is let go as soon
    as its options are read, so what the inference holds beside the
    columns' compact readings is one pair's.
    """
    floor = settings.small_cell_floor
    limit = rules.rule_limit(tabled, floor)
    position: "dict[str, int]" = {}
    by_name: "dict[str, dict[str, object]]" = {}
    for place in range(len(blocks)):
        name = f"{_get(blocks[place], 'name')}"
        position[name] = place
        by_name[name] = blocks[place]
    notes: "list[str]" = []
    near: "list[tuple[str, str]]" = []
    candidates: "list[_Candidate]" = []
    pairs_read = 0
    for a_name in eligible:
        a_block = by_name[a_name]
        kind = rules.kind_of_role(_get(a_block, "role"))
        if kind is None or rules.has_exponent(a_block):
            continue
        a = readings_for(gathered, a_name, kind)
        # OPEN3: the base's rows where every base column holds a reading number at least f.
        if a.reads < floor:
            continue
        for b_name in position:
            if b_name == a_name or (a_name, b_name) in dropped:
                continue
            b_block = by_name[b_name]
            # OPEN1 on B.
            if computed_refused(b_block, held, identifiers):
                continue
            b = readings_for(gathered, b_name, kind)
            reading_ = pair_reading(kind, a_block, b_block, a, b)
            pairs_read += 1
            passed = _pair_pass(reading_, a, b, limit, codes[a_name]) if b.reads else _Passed(0, {}, 0, 0, 0)
            if passed.v > limit:
                # Over the limit: no step (MR.10's private NEAR-RULE reading stays owed, lane RO2).
                near += [(a_name, b_name)]
                continue
            unit = fractions.Fraction(1, 10 ** max(a.places, b.places)) if kind == KIND_NUMBER else fractions.Fraction(1)
            step = rules.grain_step(a_block, reading_.grain)
            if kind == KIND_DATE and reading_.seconds is False:
                step = fractions.Fraction(1)
            histogram = [(fractions.Fraction(pair[0]) * unit, pair[1]) for pair in _histogram(passed.joint)]
            derived: "list[Option]" = []
            if passed.both and step is not None:
                found_options, _refusals = derived_options(
                    passed.joint, eligible[a_name], groups[a_name], passed.v, step, unit, floor, limit, person, tabled,
                )
                if not person:
                    derived = found_options
            size = fractions.Fraction(sum(abs(value) * rows for value, rows in histogram))
            candidates += [
                _Candidate(
                    a_name, b_name, kind, reading_, passed.v, passed.both, passed.b_without_a, _median(histogram),
                    unit, step, passed.zero, tuple(derived), size / passed.both if passed.both else fractions.Fraction(0),
                )
            ]
    # The rules each source column names (MR.7's item: the column is a source difference another rule names).
    sources_named: "dict[tuple[str, str], list[Option]]" = {}
    source_columns = [
        name for name in eligible
        if _get(by_name[name], "role") in NUMBER_PAIR_ROLES and not rules.has_exponent(by_name[name])
    ]
    for candidate in candidates:
        if not candidate.both or candidate.v > floor - 1:
            continue
        a = readings_for(gathered, candidate.a, candidate.kind)
        b = readings_for(gathered, candidate.b, candidate.kind)
        sources: "list[tuple[str, dict[str, object], Readings]]" = []
        for name in source_columns:
            if name in (candidate.a, candidate.b):
                continue
            sources += [(name, by_name[name], readings_for(gathered, name, KIND_NUMBER))]
        step = candidate.step if candidate.step is not None else fractions.Fraction(1)
        found, _refused = source_options(candidate.reading, a, b, by_name[candidate.a], by_name[candidate.b], sources, step, floor)
        if found:
            sources_named[(candidate.a, candidate.b)] = found
    named_sources = {option.carrier for key in sources_named for option in sources_named[key]}
    opened = {(candidate.a, candidate.b) for candidate in candidates}
    out: "list[tuple[tuple[int, int, tuple[int, ...]], Inferred]]" = []
    worth_rule: "dict[tuple[str, str], bool]" = {}
    why_of: "dict[tuple[str, str], str]" = {}
    stride = _stride(tabled)
    sampled_codes = {name: codes[name][0:tabled:stride] for name in eligible}
    for candidate in candidates:
        a = readings_for(gathered, candidate.a, candidate.kind)
        b = readings_for(gathered, candidate.b, candidate.kind)
        carriers = {option.carrier for option in sources_named[(candidate.a, candidate.b)]} if (candidate.a, candidate.b) in sources_named else set()
        copies = [name for name in source_columns if name not in (candidate.a, candidate.b)]
        offered = bool(candidate.derived) or (candidate.a, candidate.b) in sources_named
        why = _not_worth_first(candidate, a, b, by_name, eligible, sampled_codes, opened, position, named_sources, carriers, copies, gathered, offered)
        why_of[(candidate.a, candidate.b)] = why
        worth_rule[(candidate.a, candidate.b)] = not why
    # A column a rule worth carrying computes is no input "not computed" (MR.7's tighter-rule item).
    computed_by_worth = {candidate.b for candidate in candidates if worth_rule[(candidate.a, candidate.b)]}
    for candidate in candidates:
        key = (candidate.a, candidate.b)
        why = why_of[key]
        if not why:
            why = tighter_rule(candidate, candidates, worth_rule, computed_by_worth)
        options = list(candidate.derived)
        # The candidate's options move into its rule: nothing else holds them (G4).
        candidate.derived = ()
        derived_scores = [option.score for option in options]
        top = max(derived_scores) if derived_scores else rules.W_RULE * tabled
        for option in sources_named[key] if key in sources_named else []:
            options += [dataclasses.replace(option, score=top + rules.W_RULE * tabled)]
        if why:
            options = [dataclasses.replace(option, score=-rules.W_RULE * tabled, worth=False) for option in options]
        else:
            # Per derived option: a level with no edge writes `B` as `A`, NOT WORTH unless the gap is 0 on 99 of
            # 100 rows (MR.7, REPAIR 2, as amended by the orchestrator's ruling of 2026-11-05).
            reshaped: "list[Option]" = []
            for option in options:
                if option.carrier == rules.CARRIER_DERIVED and option.level is not None and not derived_option_worth(option.level[2], candidate.gap_zero, candidate.both):
                    reshaped += [dataclasses.replace(option, score=option_score(False, fractions.Fraction(0), tabled), worth=False)]
                else:
                    reshaped += [option]
            options = reshaped
        rule = Inferred(
            rules.RULE_ORDER, candidate.b, (candidate.a,), candidate.kind, candidate.reading.grain,
            candidate.reading.seconds, candidate.step, tuple(options), why, candidate.both >= floor,
        )
        out += [(rules.step_order(position, rules.RULE_ORDER, candidate.b, [candidate.a]), rule)]
    ordered = sorted((out[at][0], at) for at in range(len(out)))
    return Inference(tuple(out[at][1] for _key, at in ordered), tuple(near), tuple(notes), pairs_read)


def tighter_rule(
    candidate: _Candidate,
    candidates: "list[_Candidate]",
    worth_rule: "dict[tuple[str, str], bool]",
    computed_by_worth: "set[str]",
) -> str:
    """MR.7's tighter-rule item: another rule worth carrying by every other item computes the same column
    from an input NOT computed by such a rule, by a smaller median gap, at equal medians by a smaller mean
    gap ('' where none does). A rule from an input another worth rule computes would be blocked at its step,
    and `B` dealt apart from both."""
    for other in candidates:
        if other.b != candidate.b or other.a == candidate.a or not worth_rule[(other.a, other.b)]:
            continue
        if other.a in computed_by_worth:
            continue
        if tighter_than(abs(other.median), other.mean_size, abs(candidate.median), candidate.mean_size):
            return "another worth rule computes this column from an input not computed by a smaller median gap"
    return ""


def tighter_than(median: fractions.Fraction, mean: fractions.Fraction, against: fractions.Fraction, against_mean: fractions.Fraction) -> bool:
    """MR.7's tighter-rule order (AMENDED 2026-11-05, LANE RO RULINGS 3 (3)): a smaller median |D|, and at
    equal medians a smaller mean |D|."""
    return median < against or (median == against and mean < against_mean)


def association_lost_share(lost: fractions.Fraction, kept: fractions.Fraction) -> fractions.Fraction:
    """The share MR.7's association item reads for one other column: what computing `B` loses (`D`'s share
    between its bands), but no more than `B` dealt apart would keep (`B`'s own share)."""
    return min(lost, kept)


def _not_worth_first(
    candidate: _Candidate,
    a: Readings,
    b: Readings,
    by_name: "dict[str, dict[str, object]]",
    eligible: "dict[str, rules.Ladder]",
    sampled_codes: "dict[str, bytes | list[int]]",
    opened: "set[tuple[str, str]]",
    position: "dict[str, int]",
    named_sources: "set[str]",
    carriers: "set[str]",
    copies: "list[str]",
    gathered: Gathered,
    offered: bool,
) -> str:
    """MR.7's NOT WORTH items read on the real table, but the tighter-rule item: '' where none holds.

    `carriers` are the source columns this rule's options name: computing
    `B` from one of them keeps `B`'s association with it, so the
    association item reads every other column.
    """
    b_block = by_name[candidate.b]
    a_block = by_name[candidate.a]
    if _get(b_block, "role") in rules.LABEL_ROLES:
        return "B's own role is a label"
    if b.present and fractions.Fraction(b.reads, b.present) < READ_LINE:
        return "fewer than 99 of 100 of B's present cells read under A's kind"
    if b.present and fractions.Fraction(candidate.b_without_a, b.present) > SHARE_LINE:
        return "B reads on more than 1/100 of its present cells where A holds none"
    if candidate.kind == KIND_DATE:
        a_dates = not rules.every_layout_clocked(a_block)
        if a_dates and _get(b_block, "role") == rules.ROLE_DATETIME and rules.first_layout_clocked(b_block):
            return "B is finer than A: a clock beside A's dates"
    if candidate.kind == KIND_NUMBER and b.places > a.places:
        return "B is finer than A: more places than A"
    if candidate.kind == KIND_DATE:
        b_figures = _figures_after_the_second(b_block)
        a_figures = _figures_after_the_second(a_block)
        if b_figures > a_figures:
            # A stamp's places after the second, as its block publishes them: computing `B` writes `A`'s
            # (lane RO's repair 2, the sibling check of the verify's item 1: a fraction beside a stamp to the
            # second was written to the second, and code parsing the real column's fraction failed on it).
            return "B is finer than A: more places than A"
        if b_figures and b_figures != a_figures:
            # Read both ways where `B` writes a fraction (LANE RO RULINGS 7 (2): a stamp to the millisecond
            # beside one to the microsecond was written with six figures on every cell, against three on
            # every real cell).
            return "B writes fewer figures after the second than A: computing it would write A's"
    if candidate.kind == KIND_DATE and _get(b_block, "role") == rules.ROLE_DATETIME:
        if candidate.reading.seconds != rules.first_layout_clocked(b_block) and candidate.reading.grain != rules.GRAIN_DAY:
            return "the option's grain is other than B's own"
    if candidate.reading.instants and candidate.both and offsets_other(a, b):
        # Computing `B` writes `A`'s offset on every row (MR.2), so a `B` written in another zone took `A`'s
        # on every cell (LANE RO RULINGS 7 (1): `+03:00` beside `-05:00`, its local clock eight hours back).
        return "B's UTC offset is other than A's: computing it would erase it"
    if candidate.both:
        share = _break_share(a, b, candidate.reading)
        if share < SHARE_LINE:
            return "BREAK under 1/100: a pair the twin keeps dealt apart"
        failing_share = fractions.Fraction(candidate.v, candidate.both)
        if failing_share > SHARE_LINE:
            return "v above 1/100 of the rows where both read"
        if failing_share * 2 >= share:
            return "v at least half of BREAK"
    if (candidate.b, candidate.a) in opened and position[candidate.b] < position[candidate.a]:
        return "it holds both ways, and computes the earlier column"
    if candidate.b in named_sources:
        return "the column is a source difference another rule names"
    if candidate.both and offered:
        association = _association_lost(candidate, a, b, eligible, sampled_codes, carriers, copies, gathered)
        if association >= ASSOCIATION_LINE:
            return "B's strongest association with another column would be lost"
        if presence_follows(candidate, b, eligible, sampled_codes, carriers) >= PRESENCE_LINE:
            return "B's presence follows another column"
    return ""


def offsets_other(a: Readings, b: Readings) -> bool:
    """MR.7's offset item (ADDED 2026-11-06, LANE RO RULINGS 7 (1)): whether the UTC offsets `B` holds on the
    rows both columns read are other than those `A` holds there.

    Computing `B` writes `A`'s offset on each row (MR.2), so a `B` written in
    another zone than `A` would take `A`'s offset on every row. Two columns
    of one zone hold the same offsets, and a row across that zone's clock
    change, `A` before it and `B` after, keeps the rule (the zoo's
    encounters, LANE RO RULINGS 3 (4)). The rows are read in blocks
    through `offsets_in` on both, as held, and the pass stops at the first
    block holding an offset the other column holds on no row.
    """
    a_written = set(a.offset_palette or ())
    b_written = set(b.offset_palette or ())
    a_held: "set[int | None]" = set()
    b_held: "set[int | None]" = set()
    for start, stop in spans(a.rows):
        firsts = block_of(a, start, stop)
        seconds = block_of(b, start, stop)
        both = [at for at in range(stop - start) if firsts[at] is not None and seconds[at] is not None]
        if not both:
            continue
        a_offsets = offsets_in(a, start, stop)
        b_offsets = offsets_in(b, start, stop)
        a_held |= {a_offsets[at] for at in both}
        b_held |= {b_offsets[at] for at in both}
        if a_held - b_written or b_held - a_written:
            return True
    return a_held != b_held


def _figures_after_the_second(block: "dict[str, object]") -> int:
    """The figures a stamp column writes after the second, as its block publishes them (0 below `subsecond`)."""
    digits = _get(block, "subsecond_digits")
    if _get(block, "time_precision") != "subsecond" or not isinstance(digits, int) or isinstance(digits, bool):
        return 0
    return digits


def presence_follows(
    candidate: _Candidate,
    b: Readings,
    eligible: "dict[str, rules.Ladder]",
    sampled_codes: "dict[str, bytes | list[int]]",
    carriers: "set[str]",
) -> fractions.Fraction:
    """MR.7's presence item (AMENDED 2026-11-05, LANE RO RULINGS 3 (5), the statistics review's item 4): the
    largest share of variance of `B`'s presence (1 where `B` reads under `A`'s kind, else 0) between another
    eligible column's `L0` bands, over the sampled rows, exactly; `A`, `B` and the rule's named sources set
    aside. A computed `B` is present where `D` reads, and `{D | A}` deals `D`'s `missing` band by `A` alone, so
    a presence another column sets is lost by computing it."""
    sampled = strided(b, _stride(b.rows))
    indicator: "list[int | None]" = [0 if value is None else 1 for value in block_of(sampled, 0, sampled.rows)]
    best = fractions.Fraction(0)
    if not _spread_of(indicator):
        return best
    for name in eligible:
        if name in (candidate.a, candidate.b) or name in carriers:
            continue
        best = max(best, _share_between(indicator, sampled_codes[name], len(eligible[name].totals)))
    return best


def _spread_of(values: "list[int | None]") -> bool:
    """Whether the readings take two values or more (a share of variance between bands exists)."""
    first: "int | None" = None
    for value in values:
        if value is None:
            continue
        if first is None:
            first = value
        elif value != first:
            return True
    return False


def _share_between(values: "list[int | None]", groups: "bytes | list[int]", bands: int) -> fractions.Fraction:
    """A reading's exact share of variance between a column's `L0` bands (eta squared), over the rows it reads."""
    count = 0
    total = 0
    squares = 0
    sums = [0] * bands
    rows_of = [0] * bands
    for group, value in zip(groups, values):
        if value is not None:
            count += 1
            total += value
            squares += value * value
            sums[group] += value
            rows_of[group] += 1
    if count < 2:
        return fractions.Fraction(0)
    spread = fractions.Fraction(squares) - fractions.Fraction(total * total, count)
    if spread <= 0:
        return fractions.Fraction(0)
    between = sum(fractions.Fraction(sums[group] * sums[group], rows_of[group]) for group in range(bands) if rows_of[group])
    between -= fractions.Fraction(total * total, count)
    return between / spread


def _association_lost(
    candidate: _Candidate,
    a: Readings,
    b: Readings,
    eligible: "dict[str, rules.Ladder]",
    sampled_codes: "dict[str, bytes | list[int]]",
    carriers: "set[str]",
    copies: "list[str]",
    gathered: Gathered,
) -> fractions.Fraction:
    """MR.7's association item: `B`'s association with another eligible column `C` LOST by computing it,
    exactly (the real table's, never published), over the sampled rows alone.

    Computing `B` deals `D` by `A` alone, so what is lost on `C` is `D`'s
    share of variance between `C`'s `L0` bands; but a `B` dealt apart
    from `A`, the rule not carried, keeps of it no more than `B`'s own
    share between those bands (`B` read under `A`'s kind in the pair's
    unit): the item reads, for each `C`, the smaller of the two, and
    takes the largest over the columns (AMENDED 2026-11-05, lane RO's
    repair 1, the statistics review's item 2: `D`'s share alone refused a
    stay's discharge whose own dates hold no association to keep). Not
    read: `A`, `B`, a source column this rule names (computing `B` from it
    keeps it), and a number column that copies `D` (equal to it in one
    unit on 99 of 100 of the rows both read: another reading of the same
    difference, which carries no rule from `f` failing rows on, the price
    limit 18 states).
    """
    stride = _stride(a.rows)
    a_sampled = strided(a, stride)
    b_sampled = strided(b, stride)
    gaps = pair_gaps(candidate.reading, a_sampled, b_sampled)[0]
    own = _in_unit(b_sampled, candidate.reading, candidate.reading.scale_b)
    best = fractions.Fraction(0)
    if not _spread_of(gaps) or not _spread_of(own):
        # A `D` or a `B` that does not vary holds no share of variance to lose or to keep.
        return best
    for name in eligible:
        if name in (candidate.a, candidate.b) or name in carriers:
            continue
        power = 10 ** max(a.places, b.places) if candidate.kind == KIND_NUMBER else 1
        if name in copies and _copies_the_gap(gaps, strided(readings_for(gathered, name, KIND_NUMBER), stride), candidate.kind, candidate.reading.seconds, power):
            continue
        bands = len(eligible[name].totals)
        lost = _share_between(gaps, sampled_codes[name], bands)
        if lost <= best:
            continue
        kept = _share_between(own, sampled_codes[name], bands)
        best = max(best, association_lost_share(lost, kept))
    return best


def _copies_the_gap(gaps: "list[int | None]", other: Readings, kind: str, seconds: bool, power: int = 1) -> bool:
    """Whether a number column copies `D`: on at least 99 of 100 of the rows where both read, `D` equals
    the column's reading times one unit (1 on a number pair; a day, an hour, a minute or a second on a
    date or clock pair), in whole numbers. `power` is `10 ** p` of a number pair read at `p` places
    (`D`'s readings are scaled by it; lane RO's repair 2, the outside review's item 5)."""
    if not other.reads:
        return False
    units = [1] if kind == KIND_NUMBER else [86400, 3600, 60, 1]
    # D's own unit in seconds: a whole day where D reads days, a second elsewhere (1 on a number pair).
    own = 1 if (kind == KIND_NUMBER or seconds or kind == KIND_CLOCK) else rules.DAY_SECONDS
    scale = 10**other.places
    values = block_of(other, 0, other.rows)
    for unit in units:
        both = 0
        equal = 0
        for gap, value in zip(gaps, values):
            if gap is None or value is None:
                continue
            both += 1
            equal += 1 if gap * own * scale == value * unit * power else 0
        if both and 100 * equal >= 99 * both:
            return True
    return False


# -- A COMPUTED COLUMN'S BLOCK (MR.6 (a)) ---------------------------------------


def _emptied(value: object) -> object:
    """A withheld key's value: `{}` for an object, `[]` for a list, `null` otherwise (4.6b.7's list)."""
    if isinstance(value, dict):
        return {}
    if isinstance(value, list):
        return []
    return None


def computed_block(own: "dict[str, object]", template: "dict[str, object]", role: str, floor: int) -> "dict[str, object]":
    """A computed column's block (MR.6 (a)): its name, position and the RULE's role, its own layout
    words each held by at least `f` rows most rows first and without counts, and every other key
    `null`, `{}` or `[]`.

    `own` is the column's block described on its own; `template` a block
    of the rule's role (the input's), whose keys the computed block holds,
    so section 5.1 and the role's keys of section 6.11 are all present. A
    number column keeps its OWN affix whatever the rule's role (an affixed
    `B` beside a bare `A`: the two affix words beside the role's keys;
    lane RO's repair 2, the outside review's item 1).
    """
    out: "dict[str, object]" = {}
    lists = rules.LAYOUT_LISTS[role] if role in rules.LAYOUT_LISTS else ()
    words = rules.LAYOUT_WORDS[role] if role in rules.LAYOUT_WORDS else ()
    for key in template:
        if key == "name":
            out[key] = _get(own, "name")
        elif key == "position":
            out[key] = _get(own, "position")
        elif key == "role":
            out[key] = role
        elif key in lists:
            census = _get(own, key)
            kept: "list[str]" = []
            if isinstance(census, dict):
                for word in rules.ranked_words(census):
                    count = census[word]
                    if isinstance(count, int) and count >= floor:
                        kept += [word]
            out[key] = kept
        elif key in words and key in own and isinstance(_get(own, key), str):
            out[key] = _get(own, key)
        else:
            out[key] = _emptied(template[key])
    affixes = [_get(own, name) for name in rules.AFFIX_WORDS]
    if role in rules.NUMBER_PAIR_ROLES and _get(own, "role") == rules.ROLE_AFFIXED and all(isinstance(affix, str) for affix in affixes):
        for name, affix in zip(rules.AFFIX_WORDS, affixes):
            out[name] = affix
    return out
