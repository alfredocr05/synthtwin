"""The numba vector job: a whole polish schedule, compiled and plain, byte for byte.

Plan P4-D409 part 4 (the owner's "Yes, gated" for numba, 2026-10-19) and
plan P4-D416 (lane DEP-2), which builds the job: CI's `numba-vectors`
runs this file on Ubuntu, Windows and macOS arm64 under Python 3.11 to
3.14 with numba installed from the development lock and
SYNTHTWIN_REQUIRE_NUMBA set, so numba's absence there is a failure and
not a skip; one differing byte fails the gate, and lane MPn's kernel is
not adopted while any does.

WHAT RUNS TODAY. Lane MPn has not written `synthtwin.polish_kernel`.
Until it does, the job runs a STAND-IN schedule written here: the
studies' simpler polish (P4-D409 part 1's numba row), a seeded swap
walk over several columns that accepts a swap when it brings the
column's pair counts nearer their targets, every pass over every
proposal, its integers below the bounds part 4 (vii) states and its
floats made of + - * / alone. The same function runs compiled by
`numba.njit(fastmath=False, parallel=False, cache=False)` -- the one
decorator the offline scanner admits -- and as plain Python on Python
integers, and the two results must be the same bytes, which must also
be the bytes recorded below on every system and Python.

THE BOUNDS (part 4 (vii)). numba's integers wrap and its true division
of two integers above 2^53 rounds where Python's is exact; the
measured cases are pinned here as differences, so the job shows WHY a
kernel checks its bounds in Python integers before each call, and the
guard below shows a case past each bound taking the plain-Python path
with the same bytes.

WHEN THE KERNEL ARRIVES. A `synthtwin.polish_kernel` with no case in
KERNEL_CASES fails this file: lane MPn enters, in the same commit as the
kernel, its whole-schedule reference cases (every pass, every column of
the polish reference table, plain-Python polish as the oracle).
"""

import hashlib
import importlib.util
import os
import struct

import pytest

if os.environ.get("SYNTHTWIN_REQUIRE_NUMBA") == "1":
    import numba
    import numpy
else:
    numba = pytest.importorskip("numba")
    numpy = pytest.importorskip("numpy")

# Lane MPn's whole-schedule cases for synthtwin.polish_kernel, each a
# (name, compiled callable, plain-Python callable, arguments) entry; empty
# until the kernel exists.
KERNEL_CASES: "list[tuple[str, object, object, tuple[object, ...]]]" = []

_MODULUS = 2147483647  # the MINSTD generator: every state below 2^31
_MULTIPLIER = 48271


def polish_schedule(codes, other, target, cells, passes, seed):
    """The stand-in polish: a seeded swap walk, every pass, every proposal.

    `codes` and `other` are two columns of whole numbers below `cells`;
    `target` holds the wanted count of each (code, other) pair, row-major.
    Each proposal draws two rows from the generator and swaps their codes
    when that does not take the pair counts further from their targets
    (a tie is taken on an even draw). Returns the codes, the swaps made,
    the final distance and a float trace of + - * / alone.
    """
    rows = len(codes)
    counts = [0] * (cells * cells)
    for row in range(rows):
        counts[codes[row] * cells + other[row]] += 1
    state = seed
    swaps = 0
    trace = 0.0
    for _ in range(passes):
        for _ in range(rows):
            state = (state * _MULTIPLIER) % _MODULUS
            first = state % rows
            state = (state * _MULTIPLIER) % _MODULUS
            second = state % rows
            a = codes[first]
            b = codes[second]
            if a == b:
                continue
            x = other[first]
            y = other[second]
            if x == y:
                continue
            ax = a * cells + x
            by = b * cells + y
            ay = a * cells + y
            bx = b * cells + x
            before = (
                (counts[ax] - target[ax]) * (counts[ax] - target[ax])
                + (counts[by] - target[by]) * (counts[by] - target[by])
                + (counts[ay] - target[ay]) * (counts[ay] - target[ay])
                + (counts[bx] - target[bx]) * (counts[bx] - target[bx])
            )
            after = (
                (counts[ax] - 1 - target[ax]) * (counts[ax] - 1 - target[ax])
                + (counts[by] - 1 - target[by]) * (counts[by] - 1 - target[by])
                + (counts[ay] + 1 - target[ay]) * (counts[ay] + 1 - target[ay])
                + (counts[bx] + 1 - target[bx]) * (counts[bx] + 1 - target[bx])
            )
            delta = after - before
            if delta < 0 or (delta == 0 and state % 2 == 0):
                counts[ax] -= 1
                counts[by] -= 1
                counts[ay] += 1
                counts[bx] += 1
                codes[first] = b
                codes[second] = a
                swaps += 1
                trace = trace + delta / (3.0 + swaps)
    distance = 0
    for cell in range(cells * cells):
        distance += (counts[cell] - target[cell]) * (counts[cell] - target[cell])
    return codes, swaps, distance, trace


_COMPILED = numba.njit(fastmath=False, parallel=False, cache=False)(polish_schedule)


def _columns(rows: int, cells: int, seed: int) -> "tuple[list[int], list[int], list[int]]":
    """A column pair and its targets, drawn by the same MINSTD generator."""
    state = seed
    codes, other = [], []
    for _ in range(rows):
        state = (state * _MULTIPLIER) % _MODULUS
        codes += [state % cells]
        state = (state * _MULTIPLIER) % _MODULUS
        other += [(state // 7) % cells]
    target = [0] * (cells * cells)
    for row in range(rows):
        target[codes[row] * cells + (codes[row] + row) % cells] += 1
    return codes, other, target


# Three columns of the stand-in reference table: rows, cells, seed.
SCHEDULE = ((3000, 5, 11), (2000, 9, 23), (1500, 3, 37))
PASSES = 4

# The schedule's bytes as plain Python writes them on any system; numba's
# must be these too.
RECORDED_DIGEST = "9a37e207f4bbe1a743710512e4fd13dbc53abef9e8df748c4c8e948b2b7615e0"


def _bytes_of(result) -> bytes:
    codes, swaps, distance, trace = result
    return (
        b"".join(struct.pack("<q", int(code)) for code in codes)
        + struct.pack("<qq", int(swaps), int(distance))
        + struct.pack("<d", float(trace))
    )


def _whole_schedule(compiled: bool) -> bytes:
    out = b""
    for rows, cells, seed in SCHEDULE:
        codes, other, target = _columns(rows, cells, seed)
        if compiled:
            result = _COMPILED(
                numpy.array(codes, dtype=numpy.int64),
                numpy.array(other, dtype=numpy.int64),
                numpy.array(target, dtype=numpy.int64),
                cells,
                PASSES,
                seed,
            )
        else:
            result = polish_schedule(codes, other, target, cells, PASSES, seed)
        out += _bytes_of(result)
    return out


def test_the_whole_schedule_is_the_same_bytes_compiled_and_plain() -> None:
    plain = _whole_schedule(compiled=False)
    compiled = _whole_schedule(compiled=True)
    assert compiled == plain, "numba's polish differs from plain Python's"
    assert len(plain) == 8 * sum(rows for rows, _, _ in SCHEDULE) + 24 * len(SCHEDULE)


def test_the_recorded_bytes() -> None:
    """Plain Python's schedule is the same bytes on every system and Python."""
    digest = hashlib.sha256(_whole_schedule(compiled=False)).hexdigest()
    assert digest == RECORDED_DIGEST, digest


def test_a_fused_or_reordered_float_would_be_seen() -> None:
    """Mutation: the trace with one operation reordered differs, so the bytes would."""
    plain = _whole_schedule(compiled=False)
    codes, other, target = _columns(*SCHEDULE[0][:2], SCHEDULE[0][2])
    altered = list(polish_schedule(codes, other, target, SCHEDULE[0][1], PASSES, SCHEDULE[0][2]))
    altered[3] = altered[3] + 2.0**-40
    assert _bytes_of(altered) not in plain


# -- the bounds of part 4 (vii) --------------------------------------------------


def _wide_sum(values):
    total = 0
    for value in values:
        total += value
    return total


def _true_division(top, bottom):
    return top / bottom


_WIDE_SUM = numba.njit(fastmath=False, parallel=False, cache=False)(_wide_sum)
_TRUE_DIVISION = numba.njit(fastmath=False, parallel=False, cache=False)(_true_division)

_LIMIT_INTEGER = 2**63
_LIMIT_FLOAT_MEETS_INTEGER = 2**53


def guarded_wide_sum(values: "list[int]") -> "tuple[int, str]":
    """The bound checked in Python integers first; past it, plain Python."""
    if sum(abs(value) for value in values) < _LIMIT_INTEGER:
        return int(_WIDE_SUM(numpy.array(values, dtype=numpy.int64))), "numba"
    return _wide_sum(values), "plain"


def guarded_true_division(top: int, bottom: int) -> "tuple[float, str]":
    if abs(top) < _LIMIT_FLOAT_MEETS_INTEGER and abs(bottom) < _LIMIT_FLOAT_MEETS_INTEGER:
        return float(_TRUE_DIVISION(top, bottom)), "numba"
    return _true_division(top, bottom), "plain"


def test_numba_wraps_where_python_does_not() -> None:
    """Part 4 (vii), measured: an integer sum past 2^63 wraps under numba."""
    values = [2**62, 2**62]
    wrapped = int(_WIDE_SUM(numpy.array(values, dtype=numpy.int64)))
    assert wrapped == -(2**63) and _wide_sum(values) == 2**63
    assert guarded_wide_sum(values) == (2**63, "plain")
    small = [2**40, 3, -(2**41)]
    assert guarded_wide_sum(small) == (_wide_sum(small), "numba")


def test_numba_rounds_a_wide_division_where_python_is_exact() -> None:
    """Part 4 (vii), measured: a true division of integers above 2^53."""
    top, bottom = 2**53 + 1, 3
    assert float(_TRUE_DIVISION(top, bottom)) == 3002399751580330.5
    assert _true_division(top, bottom) == 3002399751580331.0
    assert guarded_true_division(top, bottom) == (3002399751580331.0, "plain")
    assert guarded_true_division(7, 2) == (3.5, "numba")


def test_a_kernel_arrives_with_its_cases() -> None:
    """Lane MPn's kernel without whole-schedule cases fails the job."""
    if importlib.util.find_spec("synthtwin") is None:
        pytest.skip("synthtwin is not importable here")
    present = importlib.util.find_spec("synthtwin.polish_kernel") is not None
    if present:
        assert KERNEL_CASES, (
            "synthtwin.polish_kernel exists, so lane MPn enters its whole-schedule "
            "reference cases in KERNEL_CASES (plan P4-D409 part 4 (i))"
        )
    for name, compiled, plain, arguments in KERNEL_CASES:
        assert callable(compiled) and callable(plain), name
        assert compiled(*arguments) == plain(*arguments), name
