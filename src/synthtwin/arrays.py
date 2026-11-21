"""THE AUDITED ARRAY HELPER (plan P4-D466, lane ARR-a; plan P4-D409 part 3 (c) and (e)).

The one module where the offline audit admits numpy's array operations,
one name at a time: `frombuffer`, `zeros`, `argsort` (stable, on whole
numbers), `bincount` (no weights), `cumsum` (whole numbers), `where`,
`flatnonzero`, `concatenate`, `min` and `max` (whole numbers, for the
bound checks), and on an array this module made, `astype` and
`tolist`. WHY: TIME (goal G4; LANE I4m RULINGS 25 and 26). The polish
of method G16.3 runs its row passes as Python loops; the same passes
here run in numpy's compiled loops and give the same bytes.

THE BOUNDARY. No numpy object leaves this module: every public function
takes and returns built-in values only (bytes, bytearray, list, int,
float, None) and writes its results into the bytearrays it is handed
(8 bytes a row, little-endian binary64, for a float column; a packed
store's width, little-endian, as `chain_walk.Packed` holds them, for
whole numbers). Inside a function an array stands only where the
scanner's closure rule lets it stand (tools/offline_scan/scan_imports.py,
plan P4-D466): bound to a local name, an operand of an admitted
operator, an argument of an admitted numpy name, the receiver of
`astype` or `tolist`, indexed, or written through; `tolist()`, `int()`,
`float()` and `len()` are its only exits. So one function never hands
an array to another: the private functions below take and return
built-in values too.

THE BYTES (plan P4-D409 part 2 and part 3 (e); the hard constraint G1).
Only these are computed here, each with the same result on every
computer, Python and numpy version the product supports:
- whole-number arithmetic in int64 under a bound proved in Python
  integers below 2 ** 63 (below 2 ** 53 where a whole number meets a
  float); 1- and 2-byte storage is widened to int64 before any
  operator, and no unsigned 8-byte value meets a signed one;
- STABLE sorts of int64 keys: a stable sort of a total order has one
  result, whatever the algorithm;
- elementwise IEEE `+ - * /` on float64, in the order the plain Python
  writes them (each operation rounds once; two never fuse);
- comparisons, gathers, scatters whose indices are checked unique,
  counts by `bincount` without weights, and int64 `cumsum`.
Never here: a float reduction (sum, mean, dot, a float cumsum), a
transcendental, a float power, an unstable sort, bincount's weights,
float min or max. Every correctly rounded sum over rows is an EXACT SUM
ROUNDED ONCE (`exact_sum`: the value `math.fsum` returns), and every
running float sum stays a Python running sum from 0.0 in row order
(`running_totals`).

THE PLAIN-PYTHON PATH. Each function also holds the loop it replaces,
taken on a big-endian computer (`sys.byteorder`), where a check the
fast path needs does not hold (a repeated scatter index, an
inconsistent group list), and where an input of `score_rows` or
`move_from_means` is 2 ** 500 or more in magnitude (below it no
product or sum of theirs can pass binary64's largest value, so numpy
never meets an overflow and prints nothing; Python's floats print
nothing either, and an overflow there is refused where the score is
written); it gives the same bytes. Every check that a caller's input
is malformed is made BEFORE the path is chosen, on the same values
both paths then read (explicit little-endian views, which read the
same on any computer), so it raises the same ValueError on both paths:
among them (lane ARR-a's repair 2) a count, a width or a start that is
not a whole number, a buffer the scatter writes handed again as
another of its arguments, and a draw whose entries are not single
words; and a list of whole numbers is read once, as whole numbers (a
float equal to one is that number), and both paths read it so read.

ZONES (plan P4-D409 part 3 (a) and (c); the scanner's per-function
table): the whole-number functions are zone D's and callable from zones
D and G; the float functions (`score_rows`, `running_totals`,
`move_from_means`, `order_by_score`) and `hidden_sums`, which reads the
generator's draw, are zone G's alone.

NOTHING CALLS THIS MODULE YET but its own tests (tests/test_arrays.py,
against the frozen as-built loops of tests/arrays_as_built.py); lane
ARR-b adopts it in the polish (P4-D466's second paragraph).
"""

import math
import sys

import numpy

# A whole number held in int64 stays below this, proved in Python
# integers before the operation that could reach it.
_INT64_TOP = 1 << 63
# The 63 low bits of a binary64 value, and its exponent's bits all set
# (an infinity or not a number).
_LOW_BITS = 0x7FFF_FFFF_FFFF_FFFF
_NOT_FINITE = 0x7FF0_0000_0000_0000
# G16.8's hidden score: `(S - 393210) / 65536`, `S` the sum of a row's
# twelve 16-bit pieces (chain_walk.SCORE_CENTRE and SCORE_UNIT).
_SCORE_CENTRE = 393210
_SCORE_UNIT = 65536.0
# `joint_counts` holds at most this many cells of a code pair.
_JOINT_CELLS = 65536
# `order_by_score` sorts each group's slots on their own up to this many
# groups, and all slots at once (two stable sorts) above it.
_FEW_GROUPS = 64
# numpy's path of `score_rows` and `move_from_means` is taken only where
# every float they read is below 2 ** 500 in magnitude (the bits of
# binary64's 2 ** 500 here): a product of two stays below 2 ** 1000 and
# the sums below 2 ** 1017, so none can overflow (LANE ARR RULINGS 4 (3)).
_LARGE = float(1 << 500)
_LARGE_BITS = (1023 + 500) << 52
# ... and where the partners are at most this many (65,536 products
# below 2 ** 1000 sum below 2 ** 1016).
_MANY_PARTNERS = 65536
# A rank code takes two bytes: a table of this many normal scores holds
# every code, so no held code needs the bound check's pass.
_RANK_CODES = 65536


def _fast() -> bool:
    """True where the numpy path is taken: a little-endian computer (the draw's words are viewed in place)."""
    return sys.byteorder == "little"


def _width_for(top: int) -> int:
    """The fewest bytes, one to eight, holding every whole number from nought to `top` (chain_walk.width_for)."""
    width = 1
    while width < 8 and top >= (1 << (8 * width)):
        width = width + 1
    return width


def _store(data: "bytes | bytearray", width: int) -> int:
    """How many whole numbers a little-endian store of `width` bytes each holds; ValueError on a malformed one."""
    if not isinstance(data, (bytes, bytearray)):
        raise ValueError("a store of whole numbers is bytes or a bytearray")
    # Lane ARR-a's repair 2 (LANE ARR RULINGS 5 (4)): a width is a whole
    # number, read before the path is chosen (a float there failed on the
    # two paths with two different messages).
    if not isinstance(width, int) or width < 1 or width > 7:
        raise ValueError("a store holds one to seven bytes a whole number here")
    if len(data) % width:
        raise ValueError("a store's length is a whole number of entries")
    return len(data) // width


def _wide(data: "bytes | bytearray", width: int) -> bytearray:
    """The whole numbers of a little-endian store of `width` bytes each, as int64 bytes.

    Widths 1, 2 and 4 are read through `u1`, `<u2` and `<u4` views and
    widened; 3, 5, 6 and 7 are put together from their bytes by shifts
    of whole bytes. Every value is below 2 ** 56, so no step passes
    2 ** 63.
    """
    count = _store(data, width)
    out = bytearray(8 * count)
    wide = numpy.frombuffer(out, dtype="<i8")
    if width == 1:
        wide[0:count] = numpy.frombuffer(data, dtype="u1").astype("<i8")
        return out
    if width == 2:
        wide[0:count] = numpy.frombuffer(data, dtype="<u2").astype("<i8")
        return out
    if width == 4:
        wide[0:count] = numpy.frombuffer(data, dtype="<u4").astype("<i8")
        return out
    raw = numpy.frombuffer(data, dtype="u1").astype("<i8")
    value = numpy.zeros(count, dtype="<i8")
    for place in range(width - 1, -1, -1):
        value = (value << 8) + raw[place::width]
    wide[0:count] = value
    return out


def _packed(wide: "bytes | bytearray", width: int) -> bytearray:
    """int64 whole numbers, each from nought to below 2 ** (8 width), written `width` bytes each, little-endian."""
    if width < 1 or width > 7 or len(wide) % 8:
        raise ValueError("a packed store holds one to seven bytes a whole number here")
    count = len(wide) // 8
    out = bytearray(width * count)
    if not count:
        return out
    value = numpy.frombuffer(wide, dtype="<i8")
    if int(numpy.min(value)) < 0 or int(numpy.max(value)) >= (1 << (8 * width)):
        raise ValueError("a whole number does not fit the store's width")
    byte = numpy.frombuffer(out, dtype="u1")
    rest = value
    for place in range(width):
        low = rest & 255
        byte[place::width] = low.astype("u1")
        rest = rest >> 8
    return out


def _whole_numbers(values: "list[int]") -> bytearray:
    """A list of whole numbers as int64 bytes; ValueError for anything else.

    numpy refuses a whole number outside int64 (OverflowError, raised
    as it is); reading the bytes back and comparing them with the list
    refuses a float, a text or anything numpy would have converted.
    """
    if not isinstance(values, list):
        raise ValueError("whole numbers come as a list")
    out = bytearray(8 * len(values))
    view = numpy.frombuffer(out, dtype="<i8")
    view[0:len(values)] = values
    back: "list[int]" = view.tolist()
    if back != values:
        raise ValueError("every entry is a whole number")
    return out


def _codes(codes: "bytes | bytearray | list[int]") -> bytearray:
    """Row codes, a byte a row or a list of whole numbers, as int64 bytes; ValueError on a negative code."""
    if isinstance(codes, list):
        out = _whole_numbers(codes)
        if codes and int(numpy.min(numpy.frombuffer(out, dtype="<i8"))) < 0:
            raise ValueError("a code is never negative")
        return out
    return _wide(codes, 1)


def _code_count(codes: "bytes | bytearray | list[int]") -> int:
    """How many rows a code store holds."""
    if isinstance(codes, list):
        return len(codes)
    return _store(codes, 1)


def _floats(values: "list[float]") -> bytearray:
    """A list of finite floats as binary64 bytes, little-endian; ValueError for anything else.

    Each value is copied bit for bit; a whole number is taken only
    where binary64 holds it exactly (it compares equal read back), and
    an infinity or a value that is not a number is refused, read on the
    bits (all eleven exponent bits set), so no arithmetic meets it.
    """
    if not isinstance(values, list):
        raise ValueError("floats come as a list")
    out = bytearray(8 * len(values))
    view = numpy.frombuffer(out, dtype="<f8")
    view[0:len(values)] = values
    bits = numpy.frombuffer(out, dtype="<i8")
    magnitude = bits & _LOW_BITS
    if len(numpy.flatnonzero(magnitude >= _NOT_FINITE)):
        raise ValueError("every entry is finite")
    back: "list[float]" = view.tolist()
    if back != values:
        raise ValueError("every entry is a number binary64 holds exactly")
    return out


def _finite(value: float) -> float:
    """A finite float, as a float; ValueError otherwise."""
    if not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError("a finite number is needed")
    return float(value)


def _mask(mask: "bytes | bytearray | None", rows: int) -> None:
    """ValueError unless `mask` is None or holds a byte a row."""
    if mask is None:
        return
    if not isinstance(mask, (bytes, bytearray)) or len(mask) != rows:
        raise ValueError("a mask holds one byte a row")


def _held(first: "bytes | bytearray | None", second: "bytes | bytearray | None", rows: int) -> bytearray:
    """The rows both masks hold (a byte not nought; None holds every row), rising, as int64 bytes."""
    _mask(first, rows)
    _mask(second, rows)
    both = numpy.zeros(rows, dtype="<i8") + 1
    if first is not None:
        holds = numpy.frombuffer(first, dtype="u1") != 0
        both = both & holds.astype("<i8")
    if second is not None:
        holds = numpy.frombuffer(second, dtype="u1") != 0
        both = both & holds.astype("<i8")
    chosen = numpy.flatnonzero(both).astype("<i8")
    out = bytearray(8 * len(chosen))
    numpy.frombuffer(out, dtype="<i8")[0:len(chosen)] = chosen
    return out


def _plain_held(first: "bytes | bytearray | None", second: "bytes | bytearray | None", rows: int) -> "list[int]":
    """`_held` in plain Python: the rows both masks hold, rising."""
    _mask(first, rows)
    _mask(second, rows)
    return [row for row in range(rows) if (first is None or first[row]) and (second is None or second[row])]


def _plain_codes(codes: "bytes | bytearray | list[int]") -> "list[int]":
    """Row codes as a list of whole numbers: a list read through `_codes`' own check, so both paths read the same codes."""
    if isinstance(codes, list):
        return _listed(_codes(codes))
    _store(codes, 1)
    return list(codes)


def _listed(wide: "bytes | bytearray") -> "list[int]":
    """Whole numbers held as int64 bytes (8 each, little-endian) as a list."""
    listed: "list[int]" = numpy.frombuffer(wide, dtype="<i8").tolist()
    return listed


def _plain_wide(data: "bytes | bytearray", width: int) -> "list[int]":
    """A little-endian store's whole numbers as a list (chain_walk.read_code, every row)."""
    count = _store(data, width)
    out: "list[int]" = []
    for at in range(count):
        value = 0
        for place in range(width):
            value = value | (data[at * width + place] << (8 * place))
        out += [value]
    return out


def _plain_packed(values: "list[int]", width: int) -> bytearray:
    """Whole numbers written `width` bytes each, little-endian (chain_walk.write_code, every row)."""
    out = bytearray(width * len(values))
    for at in range(len(values)):
        value = values[at]
        if value < 0 or value >= (1 << (8 * width)):
            raise ValueError("a whole number does not fit the store's width")
        for place in range(width):
            out[at * width + place] = (value >> (8 * place)) & 255
    return out


# -- counting: zone D and G ---------------------------------------------


def code_counts(
    codes: "bytes | bytearray | list[int]",
    first: "bytes | bytearray | None",
    second: "bytes | bytearray | None",
    bins: int,
) -> "list[int]":
    """How many rows the two masks hold carry each code from 0 to `bins` - 1 (codes at or above `bins` are not counted).

    `codes` holds a byte a row or a whole number a row (a list); each
    mask a byte a row, a row held where its byte is not nought, None
    holding every row. ZONES D and G. CHECKS, before the path is
    chosen: the masks' and codes' lengths agree, every code a whole
    number and none negative, `bins` from 1 to below 2 ** 62;
    `bincount` counts whole numbers below `bins`, so every count is
    exact. PLAIN PATH: one pass over the rows.
    """
    rows = _code_count(codes)
    if not isinstance(bins, int) or bins < 1 or bins >= (1 << 62):
        raise ValueError("bins from one to below 2 ** 62")
    _mask(first, rows)
    _mask(second, rows)
    code_bytes = _codes(codes)
    if not _fast():
        held = _plain_held(first, second, rows)
        listed = _listed(code_bytes)
        counted = [0 for _bin in range(bins)]
        for row in held:
            if listed[row] < bins:
                counted[listed[row]] = counted[listed[row]] + 1
        return counted
    code = numpy.frombuffer(code_bytes, dtype="<i8")
    taken = code[numpy.frombuffer(_held(first, second, rows), dtype="<i8")]
    inside = numpy.flatnonzero(taken < bins)
    counts: "list[int]" = numpy.bincount(taken[inside], minlength=bins).tolist()
    return counts


def joint_counts(
    first_codes: "bytes | bytearray | list[int]",
    second_codes: "bytes | bytearray | list[int]",
    first_bins: int,
    second_bins: int,
    first: "bytes | bytearray | None",
    second: "bytes | bytearray | None",
) -> "list[int]":
    """How many held rows carry each code pair, at `a * second_bins + b`, for `a` below `first_bins` and `b` below `second_bins`.

    At most 65,536 cells (`first_bins * second_bins`). ZONES D and G.
    CHECKS, before the path is chosen: as `code_counts`; the cell `a *
    second_bins + b` is below `first_bins * second_bins`, at most
    65,536, so the joint code is formed in int64 with room to spare.
    PLAIN PATH: one pass over the rows.
    """
    rows = _code_count(first_codes)
    if _code_count(second_codes) != rows:
        raise ValueError("both codes hold one entry a row")
    if (
        not isinstance(first_bins, int)
        or not isinstance(second_bins, int)
        or first_bins < 1
        or second_bins < 1
        or first_bins * second_bins > _JOINT_CELLS
    ):
        raise ValueError("a code pair holds at most 65,536 cells")
    cells = first_bins * second_bins
    _mask(first, rows)
    _mask(second, rows)
    bytes_a = _codes(first_codes)
    bytes_b = _codes(second_codes)
    if not _fast():
        held = _plain_held(first, second, rows)
        listed_a = _listed(bytes_a)
        listed_b = _listed(bytes_b)
        counted = [0 for _cell in range(cells)]
        for row in held:
            if listed_a[row] < first_bins and listed_b[row] < second_bins:
                cell = listed_a[row] * second_bins + listed_b[row]
                counted[cell] = counted[cell] + 1
        return counted
    chosen = numpy.frombuffer(_held(first, second, rows), dtype="<i8")
    code_a = numpy.frombuffer(bytes_a, dtype="<i8")[chosen]
    code_b = numpy.frombuffer(bytes_b, dtype="<i8")[chosen]
    small_a = code_a < first_bins
    small_b = code_b < second_bins
    inside = numpy.flatnonzero(small_a.astype("<i8") & small_b.astype("<i8"))
    joint = code_a[inside] * second_bins + code_b[inside]
    counts: "list[int]" = numpy.bincount(joint, minlength=cells).tolist()
    return counts


def exact_sum(counts: "list[int]", values: "list[float]") -> float:
    """The sum of `values[c]` taken `counts[c]` times, exactly, rounded once: the value `math.fsum` returns for that multiset.

    Each value is `m 2 ** e` by `math.frexp` (`m` a whole number of 53
    bits); the sum is formed in Python integers on the least exponent
    and rounded once by a whole number's true division by a power of
    two, which CPython rounds correctly (to nearest, ties to even, a
    subnormal included). A zero sum is `math.fsum`'s own zero: over the
    contributing zeros where every contributing value is a zero, else
    over one nonzero value and its negation (an exact cancellation).
    ZONES D and G (no numpy: whole numbers alone). CHECKS: equal
    lengths, counts whole numbers from nought, every contributing value
    finite; a sum outside binary64's range raises OverflowError, as
    `math.fsum` does. ONE DIFFERENCE, outside the polish's reach: where
    `math.fsum` raises on an intermediate overflow (terms near binary64's
    largest value whose exact sum is still finite), this returns that
    exact sum rounded once, the oracle's fsum (tools/reference/
    chain_oracle.py); the polish's terms are standardized codes, far
    below it.
    """
    if len(counts) != len(values):
        raise ValueError("one count a value")
    terms: "list[tuple[int, int]]" = []
    zeros: "list[float]" = []
    nonzero = 0.0
    for at in range(len(counts)):
        count = counts[at]
        if not isinstance(count, int) or count < 0:
            raise ValueError("a count is a whole number from nought")
        if count == 0:
            continue
        value = _finite(values[at])
        if value == 0.0:
            zeros += [value]
            continue
        fraction, exponent = math.frexp(value)
        terms += [(count * int(fraction * 9007199254740992.0), exponent - 53)]
        nonzero = value
    if not terms:
        return math.fsum(zeros)
    least = terms[0][1]
    for _mantissa, exponent in terms:
        least = min(least, exponent)
    total = 0
    for mantissa, exponent in terms:
        total = total + (mantissa << (exponent - least))
    if total == 0:
        return math.fsum([nonzero, -nonzero])
    if least >= 0:
        return float(total << least)
    return total / (1 << -least)


# -- the polish's floats: zone G alone ------------------------------------


def score_rows(
    present: "bytes | bytearray",
    partners: "list[tuple[str, float, bytes | bytearray | list[int], bytes | bytearray | list[float]]]",
    normal: "list[float]",
    noise: float,
    sums: "bytes | bytearray",
    out: bytearray,
) -> None:
    """Each row's polish score, written into `out` (8 bytes a row, binary64 little-endian): 0.0 where the column holds no reading.

    Where `present[row]` is not nought: `part = 0.0`, then for each
    partner in order `part = part + weight * value`, and the score is
    `part + noise * ((S - 393210) / 65536)`, `S` the row's hidden sum
    (`sums`, three bytes a row). A partner is `("rank", weight, ranks,
    held)`: its value `normal[k]` for the rank code `k` (`ranks`, two
    bytes a row) where `held[row]` is not nought, else 0.0; or `("band",
    weight, bands, encoding)`: its value `encoding[b]` for the row's band
    `b` (a byte or a whole number a row) where `b` is below
    `len(encoding)`, else 0.0. ZONE G. CHECKS, every one before the path
    is chosen: every length agrees; the weights, the noise, `normal` and
    each encoding (a list) are finite; every band a whole number, none
    negative; a held rank code is below `len(normal)` (a pass over the
    rows only where `normal` holds fewer than 65,536 scores, as only
    then can a two-byte code pass it). Every float operation is one
    elementwise IEEE operation in the order above, so the bytes are the
    plain loop's. numpy's path is taken only where the noise and every
    weight, normal score and encoding entry is below 2 ** 500 in
    magnitude and the partners are at most 65,536, so no product or sum
    can overflow. PLAIN PATH: that loop.
    """
    rows = _store(present, 1)
    if not isinstance(out, bytearray) or len(out) != 8 * rows:
        raise ValueError("the scores take 8 bytes a row")
    if _store(sums, 3) != rows:
        raise ValueError("the hidden sums take three bytes a row")
    noise = _finite(noise)
    table = _floats(normal)
    moderate = abs(noise) < _LARGE and _moderate(table) and len(partners) <= _MANY_PARTNERS
    listed_bands: "list[bytearray]" = []
    for partner in partners:
        if len(partner) != 4 or partner[0] not in ("rank", "band"):
            raise ValueError("a partner is ('rank', weight, ranks, held) or ('band', weight, bands, encoding)")
        kind, weight, codes, more = partner
        weighed = _finite(weight)
        moderate = moderate and abs(weighed) < _LARGE
        if kind == "rank":
            if not isinstance(codes, (bytes, bytearray)) or len(codes) != 2 * rows:
                raise ValueError("rank codes take two bytes a row")
            if not isinstance(more, (bytes, bytearray)) or len(more) != rows:
                raise ValueError("a partner's readings take a byte a row")
            if len(normal) < _RANK_CODES:
                _ranks_below(codes, more, len(normal))
            listed_bands += [bytearray()]
            continue
        if not isinstance(more, list):
            raise ValueError("a band partner's encoding is a list")
        if _code_count(codes) != rows:
            raise ValueError("a band partner's bands take one entry a row")
        encoding_bytes = _floats(more)
        moderate = moderate and _moderate(encoding_bytes)
        listed_bands += [_codes(codes) if isinstance(codes, list) else bytearray()]
    if not _fast() or not moderate:
        _plain_score_rows(present, partners, normal, noise, sums, out)
        return
    part = numpy.zeros(rows, dtype="<f8")
    normals = numpy.frombuffer(table, dtype="<f8")
    for at in range(len(partners)):
        kind, weight, codes, more = partners[at]
        value = numpy.zeros(rows, dtype="<f8")
        if isinstance(more, list):
            if more:
                if isinstance(codes, list):
                    band = numpy.frombuffer(listed_bands[at], dtype="<i8")
                else:
                    band = numpy.frombuffer(_codes(codes), dtype="<i8")
                encoding = numpy.frombuffer(_floats(more), dtype="<f8")
                within = band < len(more)
                inside = within.astype("<i8")
                value = numpy.where(inside, encoding[band * inside], 0.0)
        elif normal and isinstance(codes, (bytes, bytearray)):
            holds = numpy.frombuffer(more, dtype="u1") != 0
            holding = holds.astype("<i8")
            rank = numpy.frombuffer(codes, dtype="<u2").astype("<i8") * holding
            value = numpy.where(holding, normals[rank], 0.0)
        part = part + _finite(weight) * value
    total = numpy.frombuffer(_wide(sums, 3), dtype="<i8")
    centred = total - _SCORE_CENTRE
    hidden = centred.astype("<f8") / _SCORE_UNIT
    holds = numpy.frombuffer(present, dtype="u1") != 0
    held_rows = holds.astype("<i8")
    numpy.frombuffer(out, dtype="<f8")[0:rows] = numpy.where(held_rows, part + noise * hidden, 0.0)


def _ranks_below(codes: "bytes | bytearray", held: "bytes | bytearray", top: int) -> None:
    """ValueError unless every held row's rank code (two bytes a row, little-endian) is below `top`."""
    holds = numpy.frombuffer(held, dtype="u1") != 0
    holding = holds.astype("<i8")
    if not len(numpy.flatnonzero(holding)):
        return
    rank = numpy.frombuffer(codes, dtype="<u2").astype("<i8") * holding
    if int(numpy.max(rank)) >= top:
        raise ValueError("a held row's rank code is below the normal scores' count")


def _moderate(data: "bytes | bytearray") -> bool:
    """True where every binary64 value of `data` (8 bytes each, little-endian) is below 2 ** 500 in magnitude, read on the bits."""
    bits = numpy.frombuffer(data, dtype="<i8")
    magnitude = bits & _LOW_BITS
    return not len(numpy.flatnonzero(magnitude >= _LARGE_BITS))


def _plain_score_rows(
    present: "bytes | bytearray",
    partners: "list[tuple[str, float, bytes | bytearray | list[int], bytes | bytearray | list[float]]]",
    normal: "list[float]",
    noise: float,
    sums: "bytes | bytearray",
    out: bytearray,
) -> None:
    """`score_rows` as the plain loop: one row at a time, the partners in order (their inputs checked by `score_rows`)."""
    rows = len(present)
    hidden = _plain_wide(sums, 3)
    bands_of: "list[bytes | bytearray | list[int]]" = []
    for kind, _weight, codes, _more in partners:
        bands_of += [_plain_codes(codes) if kind == "band" and isinstance(codes, list) else codes]
    score = [0.0 for _row in range(rows)]
    for row in range(rows):
        if not present[row]:
            continue
        part = 0.0
        for at in range(len(partners)):
            kind, weight, codes, more = partners[at]
            value = 0.0
            if kind == "rank":
                if more[row]:
                    value = normal[codes[2 * row] | (codes[2 * row + 1] << 8)]
            else:
                band = bands_of[at][row]
                if band < len(more):
                    value = more[band]
            part = part + _finite(weight) * value
        score[row] = part + noise * ((hidden[row] - _SCORE_CENTRE) / _SCORE_UNIT)
    _plain_floats_into(score, out)


def _float_bits(value: float) -> int:
    """A finite binary64 value's 64 bits as a whole number (sign, exponent, fraction), by exact arithmetic.

    The sign is read from the value's own spelling, which CPython writes
    with a leading minus for every negative value, -0.0 among them.
    """
    if not math.isfinite(value):
        raise ValueError("a finite number is needed")
    sign = 1 if repr(value)[0] == "-" else 0
    magnitude = -value if sign else value
    if magnitude == 0.0:
        return sign << 63
    fraction, exponent = math.frexp(magnitude)
    # magnitude = fraction 2 ** exponent, 0.5 <= fraction < 1.
    if exponent >= -1021:
        mantissa = int(fraction * 9007199254740992.0)
        return (sign << 63) | ((exponent + 1022) << 52) | (mantissa - (1 << 52))
    # A subnormal: magnitude = mantissa 2 ** -1074.
    return (sign << 63) | int(math.ldexp(fraction, exponent + 1074))


def _bits_float(bits: int) -> float:
    """The binary64 value of 64 bits, by exact arithmetic; ValueError for an infinity or a value that is not a number."""
    sign = -1.0 if bits >> 63 else 1.0
    exponent = (bits >> 52) & 2047
    fraction = bits & ((1 << 52) - 1)
    if exponent == 2047:
        raise ValueError("a finite number is needed")
    if exponent == 0:
        return sign * math.ldexp(float(fraction), -1074)
    return sign * math.ldexp(float(fraction + (1 << 52)), exponent - 1075)


def _plain_floats(data: "bytes | bytearray") -> "list[float]":
    """The binary64 values of a little-endian store of 8 bytes each, by exact arithmetic."""
    if not isinstance(data, (bytes, bytearray)) or len(data) % 8:
        raise ValueError("floats take 8 bytes each")
    out: "list[float]" = []
    for at in range(len(data) // 8):
        bits = 0
        for place in range(8):
            bits = bits | (data[8 * at + place] << (8 * place))
        out += [_bits_float(bits)]
    return out


def _plain_floats_into(values: "list[float]", out: bytearray) -> None:
    """Finite floats written into `out`, 8 bytes each, binary64 little-endian, bit for bit (exact arithmetic)."""
    for at in range(len(values)):
        bits = _float_bits(values[at])
        for place in range(8):
            out[8 * at + place] = (bits >> (8 * place)) & 255


def _scores(score: "bytes | bytearray") -> int:
    """How many rows a score store (8 bytes a row) holds; ValueError on a malformed one."""
    if not isinstance(score, (bytes, bytearray)) or len(score) % 8:
        raise ValueError("the scores take 8 bytes a row")
    return len(score) // 8


def _finite_scores(score: "bytes | bytearray") -> bool:
    """ValueError unless every score is finite (no infinity, no value that is not a number); True where every one is also below 2 ** 500 in magnitude.

    One pass over the bits: the scores at or above 2 ** 500 are found,
    and an infinity or a value that is not a number is among them.
    """
    bits = numpy.frombuffer(score, dtype="<i8")
    magnitude = bits & _LOW_BITS
    large = numpy.flatnonzero(magnitude >= _LARGE_BITS)
    if not len(large):
        return True
    if int(numpy.max(magnitude[large])) >= _NOT_FINITE:
        raise ValueError("every score is finite")
    return False


def running_totals(
    score: "bytes | bytearray",
    first: "bytes | bytearray | None",
    second: "bytes | bytearray | None",
    bands: "bytes | bytearray | list[int] | None",
    count: int,
) -> "tuple[list[float], list[int]]":
    """Each band's running sum of the held rows' scores, in row order from 0.0, and its count of rows.

    `score` holds 8 bytes a row (binary64 little-endian); the masks as
    in `code_counts`; `bands` a byte or a whole number a row, None for
    one band holding every held row; a row whose band is at or above
    `count` is left out. The SUM IS PYTHON'S: the held rows' scores are
    gathered once in row order, each band's taken from them (one band at
    a time up to 64 bands, else a stable sort by band) and handed over
    by `tolist()`, and each total is `total = total + value` from 0.0,
    the loop the plain path runs over the rows. ZONE G. CHECKS, before
    the path is chosen: lengths, every band a whole number and none
    negative, every score finite, `count` from 1. PLAIN PATH: one pass
    over the rows.
    """
    rows = _scores(score)
    if not isinstance(count, int) or count < 1 or count >= (1 << 62):
        raise ValueError("count from one to below 2 ** 62")
    if bands is not None and _code_count(bands) != rows:
        raise ValueError("the bands take one entry a row")
    _mask(first, rows)
    _mask(second, rows)
    _finite_scores(score)
    band_bytes = _codes(bands) if bands is not None else bytearray()
    if not _fast():
        held = _plain_held(first, second, rows)
        values = _plain_floats(score)
        listed = _listed(band_bytes)
        totals = [0.0 for _band in range(count)]
        counted = [0 for _band in range(count)]
        for row in held:
            row_band = listed[row] if bands is not None else 0
            if row_band < count:
                totals[row_band] = totals[row_band] + values[row]
                counted[row_band] = counted[row_band] + 1
        return totals, counted
    chosen = numpy.frombuffer(_held(first, second, rows), dtype="<i8")
    if bands is None:
        band = numpy.zeros(len(chosen), dtype="<i8")
    else:
        band = numpy.frombuffer(band_bytes, dtype="<i8")[chosen]
    inside = numpy.flatnonzero(band < count)
    taken = band[inside]
    kept = numpy.frombuffer(score, dtype="<f8")[chosen[inside]]
    sizes: "list[int]" = numpy.bincount(taken, minlength=count).tolist()
    sums: "list[float]" = []
    if count <= _FEW_GROUPS:
        # Each band's rows in row order, one band at a time, from the scores gathered once.
        for each in range(count):
            gathered: "list[float]" = kept[numpy.flatnonzero(taken == each)].tolist()
            total = 0.0
            for value in gathered:
                total = total + value
            sums += [total]
        return sums, sizes
    # Many bands: one stable sort by band keeps each band's rows in row order.
    order = numpy.argsort(taken, kind="stable")
    in_order: "list[float]" = kept[order].tolist()
    at = 0
    for size in sizes:
        total = 0.0
        for value in in_order[at:at + size]:
            total = total + value
        sums += [total]
        at = at + size
    return sums, sizes


def move_from_means(
    score: bytearray,
    first: "bytes | bytearray | None",
    second: "bytes | bytearray | None",
    bands: "bytes | bytearray | list[int] | None",
    means: "list[float]",
    factors: "list[float]",
) -> None:
    """Each held row's score moved from its band's mean by the band's factor: `mean + factor * (score - mean)`, in place.

    A row whose band is at or above `len(means)` keeps its score; bands
    None is one band, every held row. ZONE G. CHECKS, before the path
    is chosen: `score` a bytearray of 8 bytes a row, every score, mean
    and factor finite, one factor a mean, every band a whole number and
    none negative. The three IEEE operations are the plain loop's,
    elementwise, in its order. numpy's path is taken only where every
    score, mean and factor is below 2 ** 500 in magnitude, so no
    product or sum can overflow. PLAIN PATH: that loop.
    """
    if not isinstance(score, bytearray):
        raise ValueError("the scores are moved in a bytearray")
    rows = _scores(score)
    if len(factors) != len(means) or not means:
        raise ValueError("one factor a mean, at least one band")
    if bands is not None and _code_count(bands) != rows:
        raise ValueError("the bands take one entry a row")
    _mask(first, rows)
    _mask(second, rows)
    mean_bytes = _floats(means)
    factor_bytes = _floats(factors)
    moderate = _finite_scores(score) and _moderate(mean_bytes) and _moderate(factor_bytes)
    band_bytes = _codes(bands) if bands is not None else bytearray()
    if not _fast() or not moderate:
        held = _plain_held(first, second, rows)
        plain_scores = _plain_floats(score)
        plain_means = _plain_floats(mean_bytes)
        plain_factors = _plain_floats(factor_bytes)
        listed = _listed(band_bytes)
        for row in held:
            row_band = listed[row] if bands is not None else 0
            if row_band < len(means):
                plain_scores[row] = plain_means[row_band] + plain_factors[row_band] * (plain_scores[row] - plain_means[row_band])
        _plain_floats_into(plain_scores, score)
        return
    chosen = numpy.frombuffer(_held(first, second, rows), dtype="<i8")
    if bands is None:
        band = numpy.zeros(len(chosen), dtype="<i8")
    else:
        band = numpy.frombuffer(band_bytes, dtype="<i8")[chosen]
    inside = numpy.flatnonzero(band < len(means))
    moved = chosen[inside]
    mean = numpy.frombuffer(mean_bytes, dtype="<f8")[band[inside]]
    factor = numpy.frombuffer(factor_bytes, dtype="<f8")[band[inside]]
    values = numpy.frombuffer(score, dtype="<f8")
    values[moved] = mean + factor * (values[moved] - mean)


def order_by_score(
    grouped: "bytes | bytearray",
    width: int,
    starts: "list[int]",
    score: "bytes | bytearray",
) -> bytearray:
    """The rows of each group's slots in the order of their (score, row) pairs, packed `width` bytes a row as `grouped` is.

    `grouped` holds the slots' rows (`rows_by_group`: rising inside
    each group), `starts` where each group's slots start, then the slot
    count; `score` 8 bytes a row over every row. THE KEY: a finite
    binary64 value's bits read as int64 with the 63 low bits negated
    where the sign is set, so both zeros are 0 and the int64 order is
    the order of the values, equal values equal keys; then TWO STABLE
    SORTS, by the key and then by the group, which keep the rising row
    order among equal keys: the order of the plain loop's sorted
    `(score, row)` pairs (up to 64 groups, each group's slots are sorted
    on their own, the same order). ZONE G. CHECKS, before the path is
    chosen: the starts whole numbers rising strictly from 0 to the slot
    count, every score finite, every slot's row inside the scores; the
    rows rise inside each group (else the plain path). PLAIN PATH: one
    sort of whole-number keys a group.
    """
    slots = _store(grouped, width)
    rows = _scores(score)
    start_bytes = _whole_numbers(starts)
    listed_starts = _listed(start_bytes)
    if not listed_starts or listed_starts[0] != 0 or listed_starts[-1] != slots:
        raise ValueError("the starts run from 0 to the slot count")
    for at in range(1, len(listed_starts)):
        if listed_starts[at] <= listed_starts[at - 1]:
            raise ValueError("every group holds a slot")
    _finite_scores(score)
    if not slots:
        return bytearray()
    row = numpy.frombuffer(_wide(grouped, width), dtype="<i8")
    if int(numpy.max(row)) >= rows:
        raise ValueError("a slot names a row the scores hold")
    if not _fast():
        return _plain_order_by_score(grouped, width, listed_starts, score)
    starts_found = numpy.frombuffer(start_bytes, dtype="<i8")
    inner = starts_found[1:-1]
    same_group = numpy.zeros(slots - 1, dtype="<i8") + 1
    same_group[inner - 1] = 0
    rows_fall = row[1:] <= row[:-1]
    if len(numpy.flatnonzero(rows_fall.astype("<i8") & same_group)):
        return _plain_order_by_score(grouped, width, listed_starts, score)
    bits = numpy.frombuffer(score, dtype="<i8")[row]
    magnitude = bits & _LOW_BITS
    negative = bits < 0
    key = numpy.where(negative, -magnitude, magnitude)
    out = bytearray(8 * slots)
    ordered = numpy.frombuffer(out, dtype="<i8")
    if len(listed_starts) - 1 <= _FEW_GROUPS:
        # A stable sort of each group's slots by key: rising rows among equal keys.
        for group in range(len(listed_starts) - 1):
            first = listed_starts[group]
            last = listed_starts[group + 1]
            ordered[first:last] = row[first:last][numpy.argsort(key[first:last], kind="stable")]
    else:
        # Many groups: one stable sort by key, then one by group, which
        # keeps each group's key order (the same order, fewer calls).
        group_of = numpy.cumsum(1 - same_group)
        by_key = numpy.argsort(key, kind="stable")
        by_group = numpy.argsort(numpy.concatenate((numpy.zeros(1, dtype="<i8"), group_of))[by_key], kind="stable")
        ordered[0:slots] = row[by_key[by_group]]
    return _packed(out, width)


def _plain_order_by_score(
    grouped: "bytes | bytearray", width: int, starts: "list[int]", score: "bytes | bytearray"
) -> bytearray:
    """`order_by_score` as the plain loop: each group's (key, row) pairs sorted as whole numbers."""
    rows = _plain_wide(grouped, width)
    values = _plain_floats(score)
    span = 1
    while span <= len(values):
        span = span * 2
    ordered: "list[int]" = []
    for group in range(len(starts) - 1):
        keys = [_score_key(values[row]) * span + row for row in rows[starts[group]:starts[group + 1]]]
        ordered += [key % span for key in sorted(keys)]
    return _plain_packed(ordered, width)


# Above every magnitude `_score_key` builds, so every key is positive.
_SCORE_KEY_OFFSET = 1 << 65


def _score_key(score: float) -> int:
    """A whole number in the order of a finite binary64 value, equal for equal values (-0.0 and 0.0 among them)."""
    if score == 0.0:
        return _SCORE_KEY_OFFSET
    fraction, exponent = math.frexp(score)
    magnitude = (exponent + 1100) * (1 << 53) + int(abs(fraction) * (1 << 53))
    return _SCORE_KEY_OFFSET + magnitude if score > 0.0 else _SCORE_KEY_OFFSET - magnitude


# -- the counting sorts and the write-back: zone D and G -----------------


def rows_by_group(
    groups: "bytes | bytearray",
    group_width: int,
    present: "bytes | bytearray",
) -> "tuple[bytearray, int, list[int], list[int]]":
    """The rows holding a reading, grouped by group in rising group order and rising inside each; where each group starts; the groups met in that order.

    `groups` holds each row's group, `group_width` bytes a row
    (little-endian); `present` a byte a row. Returns the rows packed
    `width_for(max(rows - 1, 0))` bytes a slot (chain_walk's rule),
    that width, the starts (one a group, then the slot count) and the
    groups. ONE STABLE SORT of the held rows' groups: equal groups keep
    their rising rows. ZONES D and G. CHECKS: lengths. PLAIN PATH: the
    two-pass counting sort.
    """
    rows = _store(present, 1)
    if _store(groups, group_width) != rows:
        raise ValueError("the groups take one entry a row")
    width = _width_for(max(rows - 1, 0))
    if width > 7:
        raise ValueError("too many rows for a packed store")
    if not _fast():
        group_of = _plain_wide(groups, group_width)
        sizes: "dict[int, int]" = {}
        for row in range(rows):
            if present[row]:
                sizes[group_of[row]] = sizes[group_of[row]] + 1 if group_of[row] in sizes else 1
        ordered = sorted(sizes)
        starts = [0]
        next_slot: "dict[int, int]" = {}
        for group_key in ordered:
            next_slot[group_key] = starts[-1]
            starts += [starts[-1] + sizes[group_key]]
        placed = [0 for _slot in range(starts[-1])]
        for row in range(rows):
            if present[row]:
                placed[next_slot[group_of[row]]] = row
                next_slot[group_of[row]] = next_slot[group_of[row]] + 1
        return _plain_packed(placed, width), width, starts, ordered
    held = numpy.frombuffer(_held(present, None, rows), dtype="<i8")
    group = numpy.frombuffer(_wide(groups, group_width), dtype="<i8")[held]
    order = numpy.argsort(group, kind="stable")
    sorted_group = group[order]
    out = bytearray(8 * len(held))
    numpy.frombuffer(out, dtype="<i8")[0:len(held)] = held[order]
    if not len(held):
        return _packed(out, width), width, [0], []
    changed = sorted_group[1:] != sorted_group[:-1]
    firsts = numpy.concatenate((numpy.zeros(1, dtype="<i8"), numpy.flatnonzero(changed) + 1))
    starts_found: "list[int]" = firsts.tolist()
    starts_found += [len(held)]
    groups_met: "list[int]" = sorted_group[firsts].tolist()
    return _packed(out, width), width, starts_found, groups_met


def places_by_group(
    groups: "bytes | bytearray",
    group_width: int,
    present: "bytes | bytearray",
    starts: "list[int]",
    ordered: "list[int]",
    index: "bytes | bytearray",
    index_width: int,
    slot_codes: "bytes | bytearray",
    binary: bool,
) -> bytearray:
    """Each group's places, in the slots `rows_by_group` gave its rows: rising (a binary's: level 0, then level 1), packed.

    A place belongs to the group of the held row whose index names it;
    the places of each group are taken in rising order (a binary's
    `(level, place)` order, a level read from `slot_codes`, places of
    other levels left out) and written `width_for(max(places - 1, 0))`
    bytes a slot. TWO STABLE SORTS (by level, then by group). ZONES D
    and G. CHECKS, before the path is chosen: lengths; the starts and
    the groups whole numbers (read as such on both paths); every held
    row's place inside the places. Then the groups the held rows meet are
    `ordered` and each group's places fill exactly its slots, and no two
    held rows name one place -- where either fails, the plain path,
    whose loop writes what it writes. PLAIN PATH: one pass over the
    rows, one over the places a level.
    """
    rows = _store(present, 1)
    places = _store(slot_codes, 1)
    if _store(groups, group_width) != rows or _store(index, index_width) != rows:
        raise ValueError("the groups and the index take one entry a row")
    # Lane ARR-a's repair 2 (LANE ARR RULINGS 5 (4)): the starts and the
    # groups read as whole numbers before the path is chosen (a float
    # equal to one is that number, anything else is refused), and both
    # paths read the lists so read.
    starts = _listed(_whole_numbers(starts))
    ordered = _listed(_whole_numbers(ordered))
    if len(starts) != len(ordered) + 1 or (starts and starts[0] != 0):
        raise ValueError("one start a group, then the slot count")
    width = _width_for(max(places - 1, 0))
    if width > 7:
        raise ValueError("too many places for a packed store")
    held = numpy.frombuffer(_held(present, None, rows), dtype="<i8")
    count = len(held)
    place = numpy.frombuffer(_wide(index, index_width), dtype="<i8")[held]
    if count and int(numpy.max(place)) >= places:
        raise ValueError("an index names a place past the places")
    if not _fast():
        return _plain_places_by_group(groups, group_width, present, starts, ordered, index, index_width, slot_codes, binary)
    group = numpy.frombuffer(_wide(groups, group_width), dtype="<i8")[held]
    if count and int(numpy.max(numpy.bincount(place))) > 1:
        return _plain_places_by_group(groups, group_width, present, starts, ordered, index, index_width, slot_codes, binary)
    order = numpy.argsort(group, kind="stable")
    sorted_group = group[order]
    change = numpy.zeros(count, dtype="<i8")
    if count:
        change[0:1] = 1
        changed = sorted_group[1:] != sorted_group[:-1]
        change[1:] = changed.astype("<i8")
    met: "list[int]" = sorted_group[numpy.flatnonzero(change)].tolist()
    if met != ordered:
        return _plain_places_by_group(groups, group_width, present, starts, ordered, index, index_width, slot_codes, binary)
    position = numpy.zeros(count, dtype="<i8")
    position[order] = numpy.cumsum(change)
    of_place = numpy.zeros(places, dtype="<i8")
    of_place[place] = position
    taken = numpy.flatnonzero(of_place)
    taken_group = of_place[taken]
    if binary:
        level = numpy.frombuffer(_wide(slot_codes, 1), dtype="<i8")[taken]
        at_zero = level == 0
        at_one = level == 1
        kept = numpy.flatnonzero(at_zero.astype("<i8") | at_one.astype("<i8"))
        taken = taken[kept]
        taken_group = taken_group[kept]
        by_level = numpy.argsort(level[kept], kind="stable")
        by_group = numpy.argsort(taken_group[by_level], kind="stable")
        found = taken[by_level[by_group]]
    else:
        found = taken[numpy.argsort(taken_group, kind="stable")]
    sizes: "list[int]" = numpy.bincount(taken_group, minlength=len(ordered) + 1).tolist()
    wanted = [0]
    wanted += [starts[at + 1] - starts[at] for at in range(len(ordered))]
    if sizes != wanted:
        return _plain_places_by_group(groups, group_width, present, starts, ordered, index, index_width, slot_codes, binary)
    out = bytearray(8 * len(found))
    numpy.frombuffer(out, dtype="<i8")[0:len(found)] = found
    return _packed(out, width)


def _plain_places_by_group(
    groups: "bytes | bytearray",
    group_width: int,
    present: "bytes | bytearray",
    starts: "list[int]",
    ordered: "list[int]",
    index: "bytes | bytearray",
    index_width: int,
    slot_codes: "bytes | bytearray",
    binary: bool,
) -> bytearray:
    """`places_by_group` as the plain loop (lane MPg's `_places_by_group`)."""
    rows = len(present)
    count = len(slot_codes)
    group_of = _plain_wide(groups, group_width)
    place_of = _plain_wide(index, index_width)
    position = {ordered[at]: at + 1 for at in range(len(ordered))}
    of_place = [0 for _place in range(count)]
    for row in range(rows):
        if present[row]:
            of_place[place_of[row]] = position[group_of[row]]
    found = [0 for _slot in range(starts[-1])]
    next_slot = [starts[group] for group in range(len(starts) - 1)]
    for level in ((0, 1) if binary else (-1,)):
        for place in range(count):
            group = of_place[place]
            if group and (level < 0 or slot_codes[place] == level):
                found[next_slot[group - 1]] = place
                next_slot[group - 1] = next_slot[group - 1] + 1
    return _plain_packed(found, _width_for(max(count - 1, 0)))


def joint_groups(
    found: bytearray,
    width: int,
    bands: "bytes | bytearray | list[int]",
    count: int,
) -> None:
    """Each row's group so far crossed with its band, renumbered in order of first meeting, written back into `found`.

    The plain loop forms the key `group * count + band` as a Python
    whole number, which may pass 2 ** 63 (a group times a count of 2 **
    32, lane MPg's test hook); this never forms it: TWO STABLE SORTS
    (by band, then by group) put equal pairs together in rising row
    order, each pair's first row is its first meeting, and the pairs are
    numbered in the order of their first rows (a stable sort of the
    first rows, inverted by a second). ZONES D and G. CHECKS, before
    the path is chosen: lengths, every band a whole number and none
    negative, the numbers fit the store; then every band below `count`
    (else two pairs could share a key in the plain loop: the plain
    path). PLAIN PATH: the dictionary of keys in row order.
    """
    if not isinstance(found, bytearray):
        raise ValueError("the groups are renumbered in a bytearray")
    rows = _store(found, width)
    if _code_count(bands) != rows:
        raise ValueError("the bands take one entry a row")
    if not isinstance(count, int) or count < 1:
        raise ValueError("count from one")
    if rows > (1 << (8 * width)):
        raise ValueError("the groups do not fit the store's width")
    band_bytes = _codes(bands)
    if not _fast():
        _plain_joint_groups(found, width, bands, count)
        return
    if not rows:
        return
    band = numpy.frombuffer(band_bytes, dtype="<i8")
    if int(numpy.max(band)) >= count:
        _plain_joint_groups(found, width, bands, count)
        return
    group = numpy.frombuffer(_wide(found, width), dtype="<i8")
    by_band = numpy.argsort(band, kind="stable")
    order = by_band[numpy.argsort(group[by_band], kind="stable")]
    sorted_group = group[order]
    sorted_band = band[order]
    change = numpy.zeros(rows, dtype="<i8")
    group_changed = sorted_group[1:] != sorted_group[:-1]
    band_changed = sorted_band[1:] != sorted_band[:-1]
    change[1:] = group_changed.astype("<i8") | band_changed.astype("<i8")
    pair = numpy.cumsum(change)
    firsts = numpy.concatenate((numpy.zeros(1, dtype="<i8"), numpy.flatnonzero(change)))
    by_meeting = numpy.argsort(order[firsts], kind="stable")
    number = numpy.argsort(by_meeting, kind="stable")
    renumbered = bytearray(8 * rows)
    numpy.frombuffer(renumbered, dtype="<i8")[order] = number[pair]
    found[0:len(found)] = _packed(renumbered, width)


def _plain_joint_groups(found: bytearray, width: int, bands: "bytes | bytearray | list[int]", count: int) -> None:
    """`joint_groups` as the plain loop (lane MPg's `_joint_groups`)."""
    group_of = _plain_wide(found, width)
    listed = _plain_codes(bands)
    seen: "dict[int, int]" = {}
    renumbered: "list[int]" = []
    for row in range(len(group_of)):
        value = group_of[row] * count + listed[row]
        if value not in seen:
            seen[value] = len(seen)
        renumbered += [seen[value]]
    found[0:len(found)] = _plain_packed(renumbered, width)


def scatter_places(
    order: "bytes | bytearray",
    order_width: int,
    places: "bytes | bytearray",
    places_width: int,
    index: bytearray,
    index_width: int,
    own: bytearray,
    slot_codes: "bytes | bytearray",
    ranks: "bytearray | None",
    slot_rank: "bytes | bytearray | None",
) -> None:
    """Each ordered row takes the place of its slot: its index (`index_width` bytes), its code and, where given, its two rank bytes, written back.

    Row `order[k]` takes place `places[k]`: `index[row] = place`,
    `own[row] = slot_codes[place]`, `ranks[2 row], ranks[2 row + 1] =
    slot_rank[2 place], slot_rank[2 place + 1]`. ZONES D and G. CHECKS,
    before the path is chosen: lengths, no buffer written handed again
    as another argument, every row and place inside its
    store; then the rows UNIQUE (a scatter whose indices repeat takes the
    plain path, whose loop lets the last write stand). The index's bytes
    are the place's low bytes, as the plain loop writes them. PLAIN
    PATH: one pass over the slots.
    """
    slots = _store(order, order_width)
    if _store(places, places_width) != slots:
        raise ValueError("one place a slot")
    if not isinstance(index, bytearray) or not isinstance(own, bytearray):
        raise ValueError("the index and the codes are written in bytearrays")
    rows = _store(index, index_width)
    if index_width > 7 or len(own) != rows:
        raise ValueError("the index and the codes hold one entry a row")
    if (ranks is None) != (slot_rank is None):
        raise ValueError("the rank codes and the places' rank codes come together")
    if ranks is not None and (not isinstance(ranks, bytearray) or len(ranks) != 2 * rows):
        raise ValueError("the rank codes take two bytes a row")
    # Lane ARR-a's repair 2 (LANE ARR RULINGS 5 (3)): a buffer written is
    # no other buffer handed in. The plain loop reads `slot_codes` and
    # `slot_rank` between its writes, numpy's path after all of them, so
    # an alias would give two different results: refused on both paths.
    written: "list[bytes | bytearray]" = [index, own] if ranks is None else [index, own, ranks]
    handed = written + [order, places, slot_codes] + ([] if slot_rank is None else [slot_rank])
    for one in range(len(written)):
        for another in range(len(handed)):
            if another != one and written[one] is handed[another]:
                raise ValueError("a buffer written is no other buffer handed in")
    _store(slot_codes, 1)
    if slot_rank is not None and _store(slot_rank, 2) != len(slot_codes):
        raise ValueError("the places' rank codes take two bytes a place")
    if not slots:
        return
    row = numpy.frombuffer(_wide(order, order_width), dtype="<i8")
    place = numpy.frombuffer(_wide(places, places_width), dtype="<i8")
    if int(numpy.max(row)) >= rows or int(numpy.max(place)) >= len(slot_codes):
        raise ValueError("a slot names a row or a place past its store")
    if not _fast() or int(numpy.max(numpy.bincount(row))) > 1:
        _plain_scatter_places(order, order_width, places, places_width, index, index_width, own, slot_codes, ranks, slot_rank)
        return
    index_bytes = numpy.frombuffer(index, dtype="u1")
    at = row * index_width
    rest = place
    for byte in range(index_width):
        low = rest & 255
        index_bytes[at + byte] = low.astype("u1")
        rest = rest >> 8
    numpy.frombuffer(own, dtype="u1")[row] = numpy.frombuffer(slot_codes, dtype="u1")[place]
    if ranks is not None and slot_rank is not None:
        rank_bytes = numpy.frombuffer(ranks, dtype="u1")
        slot_bytes = numpy.frombuffer(slot_rank, dtype="u1")
        rank_bytes[2 * row] = slot_bytes[2 * place]
        rank_bytes[2 * row + 1] = slot_bytes[2 * place + 1]


def _plain_scatter_places(
    order: "bytes | bytearray",
    order_width: int,
    places: "bytes | bytearray",
    places_width: int,
    index: bytearray,
    index_width: int,
    own: bytearray,
    slot_codes: "bytes | bytearray",
    ranks: "bytearray | None",
    slot_rank: "bytes | bytearray | None",
) -> None:
    """`scatter_places` as the plain loop (lane MPg's write-back)."""
    rows = _plain_wide(order, order_width)
    placed = _plain_wide(places, places_width)
    for slot in range(len(rows)):
        row = rows[slot]
        place = placed[slot]
        for byte in range(index_width):
            index[row * index_width + byte] = (place >> (8 * byte)) & 255
        own[row] = slot_codes[place]
        if ranks is not None and slot_rank is not None:
            ranks[2 * row] = slot_rank[2 * place]
            ranks[2 * row + 1] = slot_rank[2 * place + 1]


def take_codes(
    index: "bytes | bytearray",
    index_width: int,
    table: "bytes | bytearray",
    table_width: int,
    mapping: "list[int] | None",
    out: "bytearray | None",
    out_width: int,
) -> "list[int] | None":
    """Each row's code through its place: `mapping[table[index[row]]]` (`table[index[row]]` where `mapping` is None).

    Written `out_width` bytes a row into `out`, or handed back as a list
    where `out` is None. ZONES D and G. CHECKS, before the path is
    chosen: lengths, `out_width` from one to seven bytes, the mapping
    whole numbers; every place inside the table and every code inside
    the mapping; every result fits `out_width` bytes. PLAIN PATH: one
    pass over the rows.
    """
    rows = _store(index, index_width)
    entries = _store(table, table_width)
    if out is not None and (
        not isinstance(out, bytearray)
        or not isinstance(out_width, int)
        or out_width < 1
        or out_width > 7
        or len(out) != out_width * rows
    ):
        raise ValueError("the codes are written out_width bytes a row, one to seven")
    mapping_bytes = _whole_numbers(mapping) if mapping is not None else bytearray()
    if not rows:
        return [] if out is None else None
    place = numpy.frombuffer(_wide(index, index_width), dtype="<i8")
    if int(numpy.max(place)) >= entries:
        raise ValueError("an index names a place past the table")
    code = numpy.frombuffer(_wide(table, table_width), dtype="<i8")[place]
    if mapping is not None and int(numpy.max(code)) >= len(mapping):
        raise ValueError("a code past the mapping")
    if not _fast():
        place_of = _plain_wide(index, index_width)
        code_of = _plain_wide(table, table_width)
        taken = [code_of[place_of[row]] for row in range(rows)]
        if mapping is not None:
            mapped = _listed(mapping_bytes)
            taken = [mapped[code_taken] for code_taken in taken]
        if out is None:
            return taken
        out[0:len(out)] = _plain_packed(taken, out_width)
        return None
    if mapping is not None:
        code = numpy.frombuffer(mapping_bytes, dtype="<i8")[code]
    if out is None:
        listed: "list[int]" = code.tolist()
        return listed
    wide = bytearray(8 * rows)
    numpy.frombuffer(wide, dtype="<i8")[0:rows] = code
    out[0:len(out)] = _packed(wide, out_width)
    return None


# -- the draw: zone G alone -----------------------------------------------


def hidden_sums(draw: "numpy.typing.NDArray[numpy.uint64]", out: bytearray, start: int) -> None:
    """Each row's hidden sum `S` from the draw's three words a row, written three bytes a row into `out` from row `start` (G16.8).

    `S` is the sum of the twelve 16-bit pieces of a row's three 64-bit
    words (chain_walk.hidden_sum): read here through a `<u2` view of the
    words' bytes, widened to int64 and summed in twelve strided
    additions (at most 12 x 65,535, below 2 ** 20); never a uint64
    operation. `draw` is the array the generator's one `integers` call
    returned -- the ONE restricted value the audit lets a first-party
    function be handed (P4-D466) -- whose eight bytes a word are its
    native bytes, so the view is taken on a little-endian computer
    alone. ZONE G. CHECKS, before the path is chosen: eight bytes a
    word, one word an entry, three words a row, the rows inside `out`. PLAIN PATH (any
    other computer): `int()` of each word and the plain sum.
    """
    words = len(draw)
    if words % 3:
        raise ValueError("three words a row")
    rows = words // 3
    if (
        not isinstance(out, bytearray)
        or len(out) % 3
        or not isinstance(start, int)
        or start < 0
        or 3 * (start + rows) > len(out)
    ):
        raise ValueError("the hidden sums take three bytes a row, inside the store")
    if len(numpy.frombuffer(draw, dtype="u1")) != 8 * words:
        raise ValueError("the draw holds eight bytes a word")
    if words:
        # Lane ARR-a's repair 2 (LANE ARR RULINGS 5 (4)): one word an
        # entry. A draw of several dimensions (a size of (3, 1)) passes the
        # byte count above while each entry is an array, which numpy's
        # view reads and the plain path's int() refuses: refused here, on
        # both paths. A word, unlike an array, has no length.
        try:
            len(draw[0])
        except TypeError:
            pass
        else:
            raise ValueError("the draw holds one word an entry")
    if not _fast():
        plain = [int(word) for word in draw]
        summed: "list[int]" = []
        for row in range(rows):
            total = 0
            for word in plain[3 * row:3 * row + 3]:
                total = total + (word & 65535) + ((word >> 16) & 65535) + ((word >> 32) & 65535) + ((word >> 48) & 65535)
            summed += [total]
        out[3 * start:3 * (start + rows)] = _plain_packed(summed, 3)
        return
    piece = numpy.frombuffer(draw, dtype="<u2").astype("<i8")
    row_sums = (
        piece[0::12] + piece[1::12] + piece[2::12] + piece[3::12]
        + piece[4::12] + piece[5::12] + piece[6::12] + piece[7::12]
        + piece[8::12] + piece[9::12] + piece[10::12] + piece[11::12]
    )
    summed_bytes = bytearray(8 * rows)
    numpy.frombuffer(summed_bytes, dtype="<i8")[0:rows] = row_sums
    out[3 * start:3 * (start + rows)] = _packed(summed_bytes, 3)
