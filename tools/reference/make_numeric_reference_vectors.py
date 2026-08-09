"""Independent reference vectors for synthtwin's numeric machinery.

This script NEVER imports synthtwin, numpy, or pandas.  It computes the
mean, the sample standard deviation, the moment skewness and the
eleven-point linear (Hyndman-Fan type 7) quantile ladder from the exact
rational values of the float64 inputs, using `fractions.Fraction` and
exact integer arithmetic for everything, including the square roots.

Every float64 answer it reports is *proved* correctly rounded, not
merely computed at high precision.  The proof is a separate pass over
the finished document rather than a step inside the construction: once
every number is in place, each one is looked up together with the exact
rational it stands for and re-derived from its two float64 neighbours.
A number that reaches the document with no exact value recorded beside
it stops the run, so the claim "every published float is proved" cannot
quietly stop being true when a field is added.

The three shapes of proof:

* rational statistics (the mean, every quantile ladder rung) must lie
  between the two exact midpoints that bracket the published float,
  with an exact tie going to the even significand;
* the two irrational statistics are square roots of exact rationals
  (sd = sqrt(S) with S = m2n/(n-1) exact, and
  skew = sign(m3) * sqrt(m3**2 / m2**3) exact), so the same midpoint
  comparison is made on the squares -- an all-integer comparison with
  no rounding anywhere;
* two boundaries that a numeric comparison alone cannot see are checked
  by hand: the point where binary64 rounds to an infinity (past the
  largest finite float there is no upper neighbour to compare with),
  and the sign of a zero (+0.0 == -0.0, so `< 0` and `> 0` say nothing
  about which of the two a routine produced).

Definitions, stated so the vectors are checkable by hand:

  mean     = (1/n) * sum x_i
  sd       = sqrt( (1/(n-1)) * sum (x_i - mean)**2 )        [n >= 2]
  skew     = ( (1/n) * sum (x_i - mean)**3 )
             / ( (1/n) * sum (x_i - mean)**2 ) ** 1.5       [n >= 3, sd > 0]
  quantile(p): h = (n - 1) * p  computed EXACTLY as a rational;
               k = floor(h); g = h - k;
               q = x_(k)  if g == 0 else x_(k) + g * (x_(k+1) - x_(k))
               over the ascending sorted sample, 0-based.

Note that `mean` above is the exact mean of the exact float64 inputs.
The implementation under test computes it in floating point, so the
vectors carry the exact value and the correctly rounded float64; a test
asserts the implementation is within a stated number of units in the
last place of the correctly rounded value.

Usage:  python3 make_numeric_reference_vectors.py --seed 0 --out <path>
        (the command line the data-provenance guard uses; the seed is
        accepted and ignored, because these vectors are fixed
        mathematics rather than a random sample).
"""

import argparse
import fractions
import json
import math
import struct
import sys

# Every published value is built from exact integers and proved correct
# by exact integer comparison. Nothing here rounds except the single
# publication step, and that step is all-integer, so the decimal module
# is no longer imported at all: a high-precision decimal seed was how a
# square root came out negative (review item P1-R2-F5).
F = fractions.Fraction

# binary64 shape, as integers.
SIGNIFICAND_BITS = 53
MIN_EXPONENT = -1074   # exponent of the last place of a subnormal
MAX_EXPONENT = 971     # exponent of the last place of the largest finite

# Where the finite range stops, as exact rationals.
#
# The largest finite float64 is (2**53 - 1) * 2**971.  The next value the
# format would carry if its exponent range went one binade further is
# 2**1024, which it cannot hold.  Round-to-nearest therefore sends
# everything from the midpoint between those two upwards to an infinity
# -- the midpoint itself included, because the tie goes to the even
# significand and 2**1024 is the even one.  So the largest finite float
# is the nearest float64 only for values STRICTLY BELOW that midpoint,
# and an oracle asked about a value at or above it must refuse rather
# than publish the largest finite float as though it were the answer.
LARGEST_FINITE = F(((1 << SIGNIFICAND_BITS) - 1) << MAX_EXPONENT)
FIRST_VALUE_PAST_THE_RANGE = F(1 << 1024)
OVERFLOW_MIDPOINT = (LARGEST_FINITE + FIRST_VALUE_PAST_THE_RANGE) / 2

LADDER = (
    ("min", fractions.Fraction(0)),
    ("p01", fractions.Fraction(1, 100)),
    ("p05", fractions.Fraction(5, 100)),
    ("p10", fractions.Fraction(10, 100)),
    ("p25", fractions.Fraction(25, 100)),
    ("p50", fractions.Fraction(50, 100)),
    ("p75", fractions.Fraction(75, 100)),
    ("p90", fractions.Fraction(90, 100)),
    ("p95", fractions.Fraction(95, 100)),
    ("p99", fractions.Fraction(99, 100)),
    ("max", fractions.Fraction(1)),
)

# The ladder probabilities as the profiler will spell them in source.
# They are binary64 literals there, so the "as written" ladder differs
# from the exact decimal ladder above in the last bits.  Both are
# reported: `ladder_exact_p` uses the exact decimal probability,
# `ladder_binary_p` uses float64(p).  A profiler that writes 0.01 in
# Python is bound by the second.
LADDER_BINARY = tuple(
    (name, fractions.Fraction(float(fractions.Fraction(p))))
    for name, p in LADDER
)


# ---------------------------------------------------------------- floats











def float_bits(x):
    """The IEEE-754 binary64 bit pattern of ``x``, as an integer."""
    return struct.unpack("<Q", struct.pack("<d", x))[0]


def float_from_bits(bits):
    """The binary64 value with bit pattern ``bits``."""
    return struct.unpack("<d", struct.pack("<Q", bits))[0]


def next_up(x):
    """The next float64 above x (finite x)."""
    if math.isnan(x):
        raise ValueError("not a number has no neighbour")
    if x == math.inf:
        return x
    if x == 0.0:
        return float_from_bits(1)
    bits = float_bits(x)
    if x > 0:
        bits += 1
    else:
        bits -= 1
    return float_from_bits(bits)


def next_down(x):
    """The next float64 below x (finite x)."""
    if x == 0.0:
        return -float_from_bits(1)
    return -next_up(-x)


def sign_bit_is_set(x):
    """True when the binary64 sign bit of ``x`` is set, ``-0.0`` included.

    This is the only test that tells -0.0 from +0.0.  The two compare
    equal as numbers, so ``x < 0`` and ``x > 0`` are both false for each
    of them and neither test says anything about the sign a routine
    actually produced.
    """
    return float_bits(x) >> 63 == 1


def significand_is_even(x):
    """True when the stored significand of ``x`` ends in a zero bit.

    This is the parity that IEEE-754 round-to-nearest-ties-to-even uses.
    For a non-negative float64 the bit pattern is a monotone integer
    whose last bit IS the last bit of the significand, and it stays that
    way across the subnormal/normal boundary, so one test covers every
    magnitude.
    """
    return float_bits(abs(x)) % 2 == 0


def round_rational_to_float(value):
    """The float64 nearest ``value`` (an exact Fraction), ties to even.

    Built by integer arithmetic alone: the significand is an exact
    integer quotient and the tie is decided by comparing twice the
    remainder against the divisor.  Overflow is refused rather than
    turned into an infinity, because an oracle that publishes an
    infinity has stopped being an oracle.
    """
    if value == 0:
        return 0.0
    negative = value < 0
    size = -value if negative else value
    exponent = _last_place_exponent(size)
    numerator, denominator = _shift(size, -exponent)
    significand = _divide_half_even(numerator, denominator)
    if significand == 1 << SIGNIFICAND_BITS:
        significand >>= 1
        exponent += 1
    if exponent > MAX_EXPONENT:
        raise ValueError("the exact value overflows binary64")
    result = math.ldexp(float(significand), exponent)
    return -result if negative else result


def prove_nearest_float(value, result):
    """Raise unless ``result`` is the float64 nearest ``value``, ties even.

    Re-derived from the neighbours rather than from the construction
    above: ``result`` must sit between the two exact midpoints that
    bracket it, and a value landing exactly on a midpoint must have gone
    to the even significand.  Every comparison is between exact
    rationals, so nothing here can round.

    Two boundaries are checked by hand because the bracketing comparison
    on its own is blind to them.

    * At the largest finite float there is no upper neighbour to take a
      midpoint with -- ``next_up`` returns an infinity.  An earlier
      revision let the upper comparison pass unconditionally there, so
      it accepted the largest finite float as the answer for a value far
      past the point where binary64 rounds to an infinity.  The upper
      boundary is instead taken against ``OVERFLOW_MIDPOINT``, and a
      value at or above it is refused.  The lower end is the mirror.
    * The sign of a zero is read from the sign bit.  ``+0.0 == -0.0``, so
      a numeric sign test accepted +0.0 as the rounding of a small
      negative value, which is wrong: rounding never changes a sign.
    """
    if math.isnan(result) or math.isinf(result):
        raise AssertionError(
            f"a published value is not a finite number: {result!r}. Only "
            "finite numbers may be published; the statistic that produced "
            "this one has to be recomputed or refused."
        )
    if sign_bit_is_set(result) != (value < 0):
        raise AssertionError(
            f"the sign of {result!r} is not the sign of {value}. Rounding "
            "never changes a sign, and that includes the sign of a zero: a "
            "value below zero must round to -0.0, and zero or anything "
            "above it to 0.0."
        )
    above = next_up(result)
    below = next_down(result)
    exact = F(result)
    if math.isinf(above):
        high = _compare(value, OVERFLOW_MIDPOINT)
        if high >= 0:
            raise AssertionError(
                f"{value} is at or above the point where binary64 rounds up "
                f"to an infinity, so no finite float is nearest it and "
                f"{result!r} must not be published for it. Refuse the value "
                "instead of reporting the largest finite float."
            )
    else:
        high = _compare(value, (exact + F(above)) / 2)
    if math.isinf(below):
        low = _compare(value, -OVERFLOW_MIDPOINT)
        if low <= 0:
            raise AssertionError(
                f"{value} is at or below the point where binary64 rounds "
                f"down to a negative infinity, so no finite float is nearest "
                f"it and "
                f"{result!r} must not be published for it. Refuse the value "
                "instead of reporting the most negative finite float."
            )
    else:
        low = _compare(value, (exact + F(below)) / 2)
    if high > 0 or low < 0:
        raise AssertionError(f"{result!r} is not the float64 nearest {value}")
    if (high == 0 or low == 0) and not significand_is_even(result):
        raise AssertionError(
            f"{result!r} is an exact midpoint of {value} and its significand "
            "is odd; ties must go to the even significand"
        )


def _compare(left, right):
    """-1, 0 or 1 as the exact Fraction ``left`` is <, == or > ``right``."""
    if left < right:
        return -1
    if left > right:
        return 1
    return 0


def _shift(value, bits):
    """(numerator, denominator) of ``value * 2**bits``, as exact integers."""
    numerator = value.numerator
    denominator = value.denominator
    if bits >= 0:
        return numerator << bits, denominator
    return numerator, denominator << -bits


def _divide_half_even(numerator, denominator):
    """``numerator / denominator`` rounded to a whole number, ties to even.

    Both arguments are non-negative integers with a positive divisor.
    The tie is decided by comparing twice the remainder against the
    divisor, which is exact.
    """
    whole, rest = divmod(numerator, denominator)
    twice = rest * 2
    if twice > denominator:
        return whole + 1
    if twice < denominator:
        return whole
    return whole if whole % 2 == 0 else whole + 1


def _last_place_exponent(size):
    """The exponent of the last place of the float64 nearest ``size`` > 0.

    That is ``max(-1074, floor(log2(size)) - 52)``, with the logarithm
    taken by integer comparison against exact powers of two so that no
    floating-point estimate can be off by one at a binade edge.
    """
    guess = size.numerator.bit_length() - size.denominator.bit_length()
    while _compare(size, _power_of_two(guess)) < 0:
        guess -= 1
    while _compare(size, _power_of_two(guess + 1)) >= 0:
        guess += 1
    exponent = guess - (SIGNIFICAND_BITS - 1)
    return max(exponent, MIN_EXPONENT)


def _power_of_two(exponent):
    """The exact Fraction 2**exponent, for any sign of exponent."""
    if exponent >= 0:
        return F(1 << exponent, 1)
    return F(1, 1 << -exponent)



def compare_root(value, other):
    """-1, 0 or 1 as sqrt(``value``) is <, == or > ``other``.

    Both arguments are non-negative exact Fractions.  Squaring is
    monotone on the non-negatives, so sqrt(p/q) versus a/b has the sign
    of p*b*b - q*a*a: one integer comparison, no root taken anywhere.
    """
    left = value.numerator * other.denominator * other.denominator
    right = value.denominator * other.numerator * other.numerator
    return _compare(F(left), F(right))


def correctly_rounded_sqrt(value):
    """The float64 nearest sqrt(``value``), ties to even, by integers only.

    ``value`` is a non-negative exact Fraction.  The answer is never
    negative and is +0.0 exactly when the true root is at or below half
    the smallest subnormal -- the boundary a previous revision walked
    past, returning -4 * 2**-1074 for a sample whose spread is zero.

    Construction, all exact:

    1. find the binade, the unique g with 2**g <= sqrt(value) < 2**(g+1),
       by integer comparison;
    2. the exponent of the last place is max(-1074, g - 52);
    3. the significand is floor(sqrt(value) / 2**exponent), which equals
       ``isqrt`` of the floor of value / 4**exponent, because
       floor(sqrt(x)) == isqrt(floor(x)) for every real x >= 0;
    4. round by comparing sqrt(value) against the exact midpoint
       (2*significand + 1) * 2**(exponent - 1), sending an exact tie to
       the even significand;
    5. carry a significand that reached 2**53 into the next binade.
    """
    if value < 0:
        raise ValueError("the square root of a negative rational is not real")
    if value == 0:
        return 0.0

    guess = (value.numerator.bit_length() - value.denominator.bit_length()) // 2
    while compare_root(value, _power_of_two(guess)) < 0:
        guess -= 1
    while compare_root(value, _power_of_two(guess + 1)) >= 0:
        guess += 1

    exponent = max(guess - (SIGNIFICAND_BITS - 1), MIN_EXPONENT)

    numerator, denominator = _shift(value, -2 * exponent)
    significand = math.isqrt(numerator // denominator)

    midpoint = F(2 * significand + 1) * _power_of_two(exponent - 1)
    side = compare_root(value, midpoint)
    if side > 0 or (side == 0 and significand % 2 == 1):
        significand += 1

    if significand == 1 << SIGNIFICAND_BITS:
        significand >>= 1
        exponent += 1
    if exponent > MAX_EXPONENT:
        raise ValueError("the square root overflows binary64")
    return math.ldexp(float(significand), exponent)


def prove_correctly_rounded_sqrt(value, result):
    """Raise unless ``result`` is the float64 nearest sqrt(``value``).

    Independent of the construction: it works from the neighbours of
    ``result`` and compares their exact midpoints, squared, against
    ``value``.

    The same two boundaries ``prove_nearest_float`` checks by hand are
    checked here.  A root at or above ``OVERFLOW_MIDPOINT`` rounds to an
    infinity and is refused instead of being reported as the largest
    finite float, and the refusal of a negative answer reads the sign
    bit, so a root published as -0.0 is refused too: ``-0.0 < 0.0`` is
    false, which is how an earlier revision let one through.
    """
    if math.isnan(result) or math.isinf(result):
        raise AssertionError(
            f"a published square root is not a finite number: {result!r}. "
            "Only finite numbers may be published; recompute or refuse the "
            "spread that produced this one."
        )
    if sign_bit_is_set(result):
        raise AssertionError(
            f"a square root came out negative: {result!r}. The square root "
            "of a value that is not negative is never negative, and that "
            "includes the sign of a zero: it must be published as 0.0, not "
            "as -0.0."
        )
    above = next_up(result)
    below = next_down(result)
    # Nothing below zero can be nearer to a non-negative root, so the
    # lower midpoint for +0.0 is +0.0 itself.
    below = max(below, 0.0)
    exact = F(result)
    if math.isinf(above):
        high = compare_root(value, OVERFLOW_MIDPOINT)
        if high >= 0:
            raise AssertionError(
                f"the square root of {value} is at or above the point where "
                f"binary64 rounds up to an infinity, so no finite float is "
                f"nearest it and {result!r} must not be published for it. "
                "Refuse the value instead of reporting the largest finite "
                "float."
            )
    else:
        high = compare_root(value, (exact + F(above)) / 2)
    low = compare_root(value, (exact + F(below)) / 2)
    if high > 0 or low < 0:
        raise AssertionError(
            f"{result!r} is not the float64 nearest the square root of {value}"
        )
    if (high == 0 or low == 0) and not significand_is_even(result):
        raise AssertionError(
            f"{result!r} is an exact midpoint of the square root of {value} "
            "and its significand is odd; ties must go to the even significand"
        )


def prove_correctly_rounded_signed_sqrt(value, negative, result):
    """Raise unless ``result`` is the float64 nearest the signed root.

    The skewness is the sign of the third central moment times the
    square root of an exact non-negative rational, and the sign is
    applied after the rounding.  That is exact -- ties to the even
    significand is symmetric about zero -- so the magnitude is proved on
    its own here and the sign is checked by its bit, which is the only
    way to tell a published -0.0 from a published 0.0.
    """
    if math.isnan(result) or math.isinf(result):
        raise AssertionError(
            f"a published value is not a finite number: {result!r}. Only "
            "finite numbers may be published; recompute or refuse the shape "
            "that produced this one."
        )
    if sign_bit_is_set(result) != negative:
        raise AssertionError(
            f"{result!r} does not carry the sign of the exact value it "
            f"stands for, which is {'below' if negative else 'at or above'} "
            "zero. The sign is applied after rounding and must survive it, "
            "the sign of a zero included."
        )
    prove_correctly_rounded_sqrt(value, math.fabs(result))


# Every published number is proved by one of these three routines, named
# in the record of exact values that travels beside the document.
NEAREST = "nearest"
ROOT = "root"
SIGNED_ROOT = "signed_root"


def _published_floats(node, path=()):
    """Every float in ``node``, with the path of keys that reaches it.

    Walks the finished document rather than the code that built it, so
    a number added by a new field is found whether or not anyone
    remembered to prove it.
    """
    if isinstance(node, dict):
        for key in sorted(node):
            yield from _published_floats(node[key], path + (key,))
    elif isinstance(node, list):
        for index, item in enumerate(node):
            yield from _published_floats(item, path + (index,))
    elif isinstance(node, float):
        yield path, node


def _where(path):
    """A readable name for one place in the document."""
    return ".".join(str(step) for step in path)


def prove_every_published_float(published, exact_values):
    """Prove each float in ``published`` against the exact value it stands for.

    This is what makes the file's claim true.  The construction is not
    trusted at all here: each number is looked up with the exact
    rational it was built from and re-derived from its two float64
    neighbours.  A number with no exact value recorded for it -- a field
    somebody added without saying what it means -- stops the run rather
    than being published unproved.

    ``exact_values`` maps the path of a published number, without its
    trailing ``"float64"`` key, to one of

      ``(NEAREST, exact)``            an exact rational,
      ``(ROOT, radicand)``            the square root of an exact
                                      non-negative rational,
      ``(SIGNED_ROOT, radicand, negative)``  the same, with a sign
                                      applied after the rounding.

    Returns how many numbers were proved.
    """
    proved = 0
    for path, value in _published_floats(published):
        if not path or path[-1] != "float64":
            raise AssertionError(
                f"{_where(path)} carries the number {value!r} outside a "
                "'float64' field, so nothing proved it. Publish every number "
                "as a 'float64' field and record the exact value it stands "
                "for beside it."
            )
        claim = exact_values.get(path[:-1])
        if claim is None:
            raise AssertionError(
                f"{_where(path)} publishes {value!r} with no exact value "
                "recorded to check it against. Record the exact value for "
                "this field so it can be proved, or do not publish it."
            )
        if claim[0] == NEAREST:
            prove_nearest_float(claim[1], value)
        elif claim[0] == ROOT:
            prove_correctly_rounded_sqrt(claim[1], value)
        elif claim[0] == SIGNED_ROOT:
            prove_correctly_rounded_signed_sqrt(claim[1], claim[2], value)
        else:
            raise AssertionError(
                f"{_where(path)} records {claim[0]!r} as the way to prove "
                f"{value!r}, which is not one of {NEAREST!r}, {ROOT!r} or "
                f"{SIGNED_ROOT!r}."
            )
        proved += 1
    return proved


def exact_square_root(value):
    """The exact square root as a Fraction, or None when it is irrational.

    A reduced p/q has a rational square root exactly when p and q are
    both perfect squares, which ``math.isqrt`` settles exactly.
    """
    if value == 0:
        return F(0)
    root_numerator = math.isqrt(value.numerator)
    if root_numerator * root_numerator != value.numerator:
        return None
    root_denominator = math.isqrt(value.denominator)
    if root_denominator * root_denominator != value.denominator:
        return None
    return F(root_numerator, root_denominator)


DECIMAL_DIGITS = 40


def _proved_nearest(value):
    """The nearest float64, constructed and then proved from neighbours.

    The proof is repeated for every published number by
    ``prove_every_published_float`` once the document is complete; this
    one stops a wrong number at the place it was built, where the error
    message can name the statistic.
    """
    result = round_rational_to_float(value)
    prove_nearest_float(value, result)
    return result


def sd_float_as_fraction(value):
    """The exact rational value of a float, for rendering an irrational."""
    return F(value)


def _decimal_text(value):
    """Just the rendered text of an exact Fraction."""
    return exact_decimal(value)[0]


def _decimal_needed(value):
    """How many significant digits the complete expansion needs, or None."""
    return exact_decimal(value)[2]


def _terminating_digits(value):
    """(digits, exponent) with value == digits * 10**exponent, or None.

    None when the decimal expansion does not terminate. ``digits``
    carries no trailing zero, so its length is exactly the number of
    significant digits the complete expansion needs.
    """
    denominator = value.denominator
    twos = 0
    while denominator % 2 == 0:
        denominator //= 2
        twos += 1
    fives = 0
    while denominator % 5 == 0:
        denominator //= 5
        fives += 1
    if denominator != 1:
        return None
    exponent = -max(twos, fives)
    digits = value.numerator * 2 ** (max(twos, fives) - twos)
    digits = digits * 5 ** (max(twos, fives) - fives)
    while digits and digits % 10 == 0:
        digits //= 10
        exponent += 1
    return digits, exponent


def _render(digits, exponent):
    """Plain decimal text for ``digits * 10**exponent`` (exact)."""
    sign = "-" if digits < 0 else ""
    body = str(abs(digits))
    if exponent >= 0:
        return sign + body + "0" * exponent
    point = len(body) + exponent
    if point > 0:
        return sign + body[:point] + "." + body[point:]
    return sign + "0." + "0" * (-point) + body


def exact_decimal(value, digits=DECIMAL_DIGITS):
    """A decimal rendering of an exact Fraction, plus whether it is exact.

    Returns (text, is_exact, digits_needed).

    ``is_exact`` is true ONLY when the expansion terminates AND the whole
    of it fitted in ``digits`` significant digits. An earlier revision
    decided exactness from the denominator alone and truncated the text
    at 200 digits, so 63 published renderings claimed to be exact values
    they were not (review item P1-R2-F5). ``digits_needed`` states the
    true requirement, or None when the expansion never terminates.
    """
    if value == 0:
        return "0", True, 1
    terminating = _terminating_digits(value)
    if terminating is not None:
        whole, exponent = terminating
        needed = len(str(abs(whole)))
        if needed <= digits:
            return _render(whole, exponent), True, needed
    else:
        needed = None
    # Round half-even to `digits` significant digits, by integers.
    negative = value < 0
    size = -value if negative else value
    place = 0
    while size >= 10**digits:
        size /= 10
        place += 1
    while size < 10 ** (digits - 1):
        size *= 10
        place -= 1
    whole, remainder = divmod(size.numerator, size.denominator)
    twice = 2 * remainder
    if twice > size.denominator or (twice == size.denominator and whole % 2 == 1):
        whole += 1
    if whole >= 10**digits:
        whole //= 10
        place += 1
    return _render(-whole if negative else whole, place), False, needed


# ------------------------------------------------------------ statistics


def stats(sample):
    """Exact statistics of a list of float64 values.

    Every number in the returned document is proved before it is
    returned: ``exact_values`` records, for each published number, the
    exact rational it stands for and the shape of proof it needs, and
    ``prove_every_published_float`` walks the finished document and
    re-derives each one from its two float64 neighbours.
    """
    n = len(sample)
    xs = [fractions.Fraction(x) for x in sample]
    ordered = sorted(xs)

    total = sum(xs, fractions.Fraction(0))
    mean = total / n

    m2n = sum(((x - mean) * (x - mean) for x in xs), fractions.Fraction(0))
    m3n = sum(
        ((x - mean) * (x - mean) * (x - mean) for x in xs), fractions.Fraction(0)
    )

    exact_values = {("mean",): (NEAREST, mean)}
    out = {
        "n": n,
        "mean": {
            "decimal": _decimal_text(mean),
            "decimal_is_exact": exact_decimal(mean)[1],
            "float64": _proved_nearest(mean),
        },
    }

    if n >= 2:
        var = m2n / (n - 1)
        sd_float = correctly_rounded_sqrt(var)
        prove_correctly_rounded_sqrt(var, sd_float)
        # The square root is rational only when the variance is a perfect
        # square of one; otherwise the rendering is a rounding and says so.
        sd_exact = exact_square_root(var)
        if sd_exact is None:
            sd_text, sd_is_exact, sd_needed = exact_decimal(sd_float_as_fraction(sd_float))
            sd_is_exact = False
        else:
            sd_text, sd_is_exact, sd_needed = exact_decimal(sd_exact)
        variance_text, variance_is_exact, _variance_needed = exact_decimal(var)
        exact_values[("std",)] = (ROOT, var)
        out["std"] = {
            "decimal": sd_text,
            "decimal_is_exact": sd_is_exact,
            "decimal_digits_needed": sd_needed,
            "float64": sd_float,
            "variance_decimal": variance_text,
            "variance_is_exact": variance_is_exact,
        }
    else:
        out["std"] = None

    if n >= 3 and m2n != 0:
        m2 = m2n / n
        m3 = m3n / n
        if m3 == 0:
            skew_float, skew_text, skew_is_exact = 0.0, "0", True
            exact_values[("skew",)] = (NEAREST, F(0))
        else:
            square = (m3 * m3) / (m2 * m2 * m2)
            magnitude = correctly_rounded_sqrt(square)
            prove_correctly_rounded_sqrt(square, magnitude)
            root = exact_square_root(square)
            if root is None:
                text, _fitted, _needed = exact_decimal(
                    sd_float_as_fraction(magnitude)
                )
                is_exact = False
            else:
                text, is_exact, _needed = exact_decimal(root)
            # Negating after rounding is exact: ties to even is symmetric
            # about zero, so the sign may be applied last.
            if m3 < 0:
                skew_float, skew_text = -magnitude, "-" + text
            else:
                skew_float, skew_text = magnitude, text
            skew_is_exact = is_exact
            exact_values[("skew",)] = (SIGNED_ROOT, square, m3 < 0)
        out["skew"] = {
            "decimal": skew_text,
            "decimal_is_exact": skew_is_exact,
            "float64": skew_float,
        }
    else:
        out["skew"] = None

    # ladder_binary_p records only the rungs where locating by floating
    # point differs from the whole-number rule; the agreeing rungs said
    # nothing and cost a quarter of the file.
    for key, table in (("ladder_exact_p", LADDER), ("ladder_binary_p", LADDER_BINARY)):
        rung = {}
        for name, p in table:
            h = (n - 1) * p
            k = int(h)  # h >= 0 so int() is floor
            if k >= n - 1:
                q = ordered[n - 1]
            else:
                g = h - k
                q = ordered[k] if g == 0 else ordered[k] + g * (ordered[k + 1] - ordered[k])
            text, is_exact, _needed = exact_decimal(q)
            # Proved here as well as in the sweep below.  An earlier
            # revision sent every rung straight through the construction
            # and never compared it against its neighbours at all, so
            # the file's claim that every published float was proved
            # covered the mean, the spread and the shape only.
            exact_values[(key, name)] = (NEAREST, q)
            rung[name] = {
                "decimal": text,
                "decimal_is_exact": is_exact,
                "float64": _proved_nearest(q),
            }
        out[key] = rung

    same = [
        name
        for name in out["ladder_binary_p"]
        if out["ladder_binary_p"][name] == out["ladder_exact_p"][name]
    ]
    for name in same:
        del out["ladder_binary_p"][name]
        del exact_values[("ladder_binary_p", name)]

    prove_every_published_float(out, exact_values)
    return out


# --------------------------------------------------------------- samples


def build_samples():
    cases = {}

    # 1. the ten 1e15 integers from the review finding
    big = [float(1000000000000000 + i) for i in range(10)]
    cases["integers_1e15"] = {
        "why": "P1-R1-F6(a): exactly representable 16-digit integers; "
        "rounding to 12 significant digits flattens the whole ladder, and float64 "
        "reductions invent a skew.",
        "values": big,
    }

    # 2. a fixed base sample, then a translation, a scaling, a permutation
    base = [
        -3.25, 0.5, 7.75, 2.0, 11.5, -0.125, 4.0, 9.0, 1.25, 6.5,
        -2.5, 8.25, 3.75, 0.0, 5.125,
    ]
    cases["base_15"] = {
        "why": "the reference sample the translated/scaled/permuted "
        "copies are derived from; every value is a dyadic rational so "
        "the transforms below are exact in float64.",
        "values": list(base),
    }
    cases["base_15_translated"] = {
        "why": "base_15 + 1024 exactly.  mean must shift by 1024; sd and "
        "skew must be unchanged bit for bit if the reduction is "
        "translation-stable.",
        "values": [x + 1024.0 for x in base],
    }
    cases["base_15_scaled"] = {
        "why": "base_15 * 2**60 exactly (a power of two, so no rounding). "
        "mean and sd must scale by 2**60; skew must be unchanged bit "
        "for bit.",
        "values": [math.ldexp(x, 60) for x in base],
    }
    cases["base_15_permuted"] = {
        "why": "a fixed permutation of base_15.  Every published number "
        "must be bit-identical to base_15.",
        "values": [base[i] for i in
                   (7, 0, 14, 3, 11, 5, 9, 1, 13, 4, 8, 2, 12, 6, 10)],
    }

    # 3. near underflow
    cases["near_underflow"] = {
        "why": "P1-R1-F6(c): values near 1e-300 whose squared deviations "
        "underflow to zero in a naive variance, publishing sd = 0 beside "
        "a nonzero range.",
        "values": [1e-300 * (1.0 + i * 1e-3) for i in range(10)],
    }
    cases["subnormal"] = {
        "why": "values in the subnormal range; a scaled reduction must "
        "still produce a nonzero sd.",
        "values": [float(i) * 5e-324 for i in range(1, 11)],
    }

    # 4. near overflow
    cases["near_overflow"] = {
        "why": "P1-R1-F6(d): sum overflows binary64 although the mean, sd "
        "and skew are all comfortably representable.",
        "values": [1.0e308, 1.1e308, 1.2e308, 1.3e308, 1.4e308, 1.5e308],
    }
    cases["cancelling_extremes"] = {
        "why": "P1-R1-F6(b): the same multiset in two orders; the exact "
        "mean is 1/3 and must not depend on the order.",
        "values": [1e16, 1.0, -1e16],
    }
    cases["cancelling_extremes_permuted"] = {
        "why": "the identical multiset, reordered; every published number "
        "must equal cancelling_extremes bit for bit.",
        "values": [1e16, -1e16, 1.0],
    }

    # 5. tiny samples
    cases["two_values"] = {
        "why": "n = 2: sd is defined, skew is not.",
        "values": [1.0, 2.0],
    }
    cases["three_values"] = {
        "why": "n = 3: the smallest sample with a defined skew.",
        "values": [1.0, 2.0, 6.0],
    }
    cases["three_identical"] = {
        "why": "zero spread: sd is 0 and skew is undefined (0/0).",
        "values": [5.0, 5.0, 5.0],
    }

    # 6. one ordinary sample of 101 values, built by a fixed integer
    #    recurrence so anyone can regenerate it without this file.
    #    x_k = ((k * 7919) % 1000) / 8  for k = 0 .. 100  (dyadic: exact)
    ordinary = [((k * 7919) % 1000) / 8.0 for k in range(101)]
    cases["ordinary_101"] = {
        "why": "101 values from the closed form ((k*7919) mod 1000)/8 for "
        "k = 0..100.  n-1 = 100 makes every ladder rung land on an exact "
        "index for p = 0.01, 0.05, ... so the ladder tests index choice "
        "as well as interpolation.",
        "values": ordinary,
    }
    # A sample whose last value is enormous, so the rungs just below the
    # top are bracketed by neighbours many orders of magnitude apart.
    # This is the case that exercises the ladder's error bound, which is
    # stated in terms of the BRACKETING order statistics rather than of
    # the rung's own value.
    cliff = [float(k) for k in range(100)] + [1.0e18]
    cases["cliff_101"] = {
        "why": "101 values, the last one enormous.  The rungs near the "
        "top sit between neighbours that differ by sixteen orders of "
        "magnitude, which is what the ladder's bracket-relative error "
        "bound is written for.",
        "values": cliff,
    }
    ordinary_odd = [((k * 7919) % 1000) / 8.0 for k in range(100)]
    cases["ordinary_100"] = {
        "why": "the same recurrence truncated to 100 values, so n-1 = 99 "
        "and every interior rung interpolates.",
        "values": ordinary_odd,
    }

    return cases


def main(argv=None):
    """Write the vectors to the path given by --out.

    The data-provenance guard (plan D13) runs every committed fixture's
    generator with `--seed <seed> --out <path>` and byte-compares the
    result, so this script takes that exact command line. The seed is
    accepted and ignored: these vectors are fixed mathematics, not a
    random sample, and a seed that changed them would defeat their
    purpose.
    """
    parser = argparse.ArgumentParser(
        prog="make_numeric_reference_vectors",
        description=(
            "Compute reference values for synthtwin's numeric summary "
            "by exact rational arithmetic, importing none of the code "
            "they are used to check."
        ),
    )
    parser.add_argument("--out", required=True, help="file to write")
    parser.add_argument(
        "--seed",
        type=int,
        default=0,
        help="accepted for the fixture-manifest convention; ignored",
    )
    args = parser.parse_args(argv)
    cases = build_samples()
    document = {
        "what": "Independent high-precision reference vectors for the "
        "synthtwin numeric summary (finding P1-R1-F6).",
        "generated_by": "tools/reference/make_numeric_reference_vectors.py",
        "never_imports": ["synthtwin", "numpy", "pandas"],
        "precision": "exact rational and integer arithmetic throughout. "
        "Every published float64 -- every mean, spread, shape and ladder "
        "rung, with no exception -- is constructed by integer division "
        "or integer square root and then PROVED correct in a separate "
        "pass over the finished document: each number is re-derived from "
        "the exact rational it stands for by comparing that rational "
        "against the exact midpoints to its two neighbouring float64 "
        "values, ties to the even significand. Two boundaries the "
        "midpoint comparison cannot see on its own are checked by hand: "
        "a value at or above the point where binary64 rounds up to an "
        "infinity is refused rather than reported as the largest finite "
        "float, and the sign of a zero is read from the sign bit, "
        "because +0.0 and -0.0 compare equal. A number that reaches the "
        "document with no exact value recorded for it stops the run. No "
        "decimal approximation is used anywhere: a high-precision "
        "decimal seed is how an earlier revision published a negative "
        "standard deviation (review item P1-R2-F5).",
        "definitions": {
            "mean": "(1/n) * sum x_i, over the exact values of the float64 inputs",
            "std": "sqrt( sum (x_i - mean)^2 / (n-1) ), null for n < 2",
            "skew": "[ (1/n) sum (x_i-mean)^3 ] / [ (1/n) sum (x_i-mean)^2 ]^(3/2), "
            "null for n < 3 or zero spread",
            "quantile": "Hyndman-Fan type 7: h = (n-1)*p, k = floor(h), "
            "g = h-k, q = x_(k) + g*(x_(k+1)-x_(k)) on the ascending sample",
            "ladder_exact_p": "quantiles with p as the exact decimal 0.01, "
            "0.05, ...  This is what an implementation gets when it locates "
            "the rung with integer arithmetic -- steps = (n-1)*num, "
            "lo = steps // den, rest = steps - lo*den for the ladder written "
            "as num/den with den = 100.  THIS IS THE ORACLE.",
            "ladder_binary_p": "quantiles with p as the float64 nearest to "
            "those decimals, i.e. what an implementation gets if it writes "
            "h = (n-1) * 0.99 in float.  Reported only to show that the two "
            "differ: for n = 101 the float route puts p99 between the 99th "
            "and 100th order statistics instead of exactly on the 100th.  An "
            "implementation must NOT use this route.",
            "float64": "the correctly rounded (round-half-even) binary64 value "
            "of the exact result; a conforming implementation must publish "
            "exactly this number or one of its two immediate neighbours in "
            "binary64, as the accuracy contract below states",
        },
        "accuracy_contract": {
            "note": "correctly rounded or an immediate neighbour, for every "
            "statistic these vectors cover.  The numeric summary under test "
            "writes each value as one shared power of two and one "
            "whole-number significand, accumulates the power sums as "
            "arbitrary-precision whole numbers -- which cancel without error "
            "because whole numbers do not round -- and rounds once, at the "
            "end.  Nothing is approximated on the way in, so the contract is "
            "stated in representable numbers rather than as a measured error "
            "budget.  This replaces the error budget of revision 1, which "
            "was measured for a two-pass floating-point reduction (sorted "
            "values, power-of-two rescaling, math.fsum, math.sqrt) that the "
            "implementation no longer uses, and which accepted answers two "
            "or more representable numbers away.  eps = 2**-52.",
            "how_two_numbers_are_compared": "by their place in the ordered "
            "list of every binary64 value: consecutive representable numbers "
            "are one apart at every magnitude, across the boundary between "
            "the subnormal and the normal range included, so 'an immediate "
            "neighbour' means exactly one representable number away and "
            "nothing looser.  The two spellings of zero name the same number "
            "and sit in the same place.  A relative comparison against "
            "|expected| * eps is NOT this: it collapses at zero, where it "
            "would accept 1e-100 as a neighbour of 0.0 although about 2e252 "
            "representable numbers lie between them.",
            "mean": "the correctly rounded exact mean, or one of its two "
            "immediate neighbours",
            "std": "the correctly rounded exact sample standard deviation, "
            "or one of its two immediate neighbours",
            "skew": "the correctly rounded exact moment skewness, or one of "
            "its two immediate neighbours.  Revision 1 allowed an absolute "
            "8 * eps * (1 + |skew|) here, which accepted 0.0 for the exact "
            "-1.224744871391589e-16 of {1e16, 1, -1e16}; whole-number "
            "accumulation removes the cancellation that bound excused.",
            "ladder": "the correctly rounded exact rung, or one of its two "
            "immediate neighbours.  A separately stated outer bound of "
            "4 * eps * max(|x_(k)|, |x_(k+1)|) remains recorded because an "
            "interpolated rung is defined by its two BRACKETING order "
            "statistics rather than by its own size, so a rung landing near "
            "zero between two large neighbours is bounded by them.",
        },
        "cases": {},
    }
    for name in sorted(cases):
        case = cases[name]
        values = case["values"]
        entry = {
            "why": case["why"],
            "n": len(values),
            "values_float64_repr": [repr(v) for v in values],
        }
        entry.update(stats(values))
        document["cases"][name] = entry

    text = json.dumps(document, indent=2, sort_keys=True, allow_nan=False)
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text + "\n")
    print(f"wrote {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
