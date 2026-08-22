"""Independent reference vectors for synthtwin's generation transform.

This script NEVER imports synthtwin, numpy, or pandas.  It implements
`docs/spec/generation-method-v1.md` (revision 1) from that document
alone and computes, for each case, the twin cells a conforming
generator must write.

**The vectors are a pure function of GIVEN uint64 words.**  The words
are inputs: they are written out in the file itself and this tool draws
none of them.  It therefore contains no generator, no seed handling and
no library random operation of any kind.  What the vectors freeze is
the transform from words to bytes; the word stream a seed produces is
bound separately, by the golden twin hash CI computes against the
locked numpy (method section G14.1, G14.4).

**Why numpy may not be imported here**, stated because it is the
constraint that shapes the whole design: the data-provenance guard runs
every fixture generator under `tools/provenance/guard_runner.py`, whose
audit hook refuses an import of `ctypes`, and numpy imports `ctypes`.
A generator that imported numpy would be stopped before it wrote a
byte.  So every uniform, every bounded range, every arrangement and
every downstream value is derived from the given words in exact
standard-library integer arithmetic.

Every binary64 this file publishes is *proved* correctly rounded, not
merely computed.  The proof is a separate pass over the finished
document rather than a step inside the construction: once every number
is in place, each one is looked up together with the exact rational it
stands for and re-derived from its two binary64 neighbours, ties to the
even significand.  A number that reaches the document with no exact
value recorded beside it stops the run, so the claim "every published
float is proved" cannot quietly stop being true when a field is added.
That walk visits every value the file writes as a number, whole ones
included, at any depth and inside every container the JSON encoder
turns into an object or an array -- a Python tuple is an array there
exactly as a list is (review item P1-R8-F3's blind spot) -- and a node
whose shape the walk has no rule for stops the run instead of being
passed over.  Before anything is serialized the run also drives a
full-generator mutant through the same proof layer and refuses to
continue unless the mutant is caught.

The two shapes of proof, and where each is used:

* `nearest` -- the published float is the binary64 nearest an exact
  rational, ties to the even significand, checked by comparing that
  rational against the two exact midpoints bracketing the float.  Used
  for every published profile input (which is stated in this file as
  exact decimal text, so the float beside it is a claim to be proved
  rather than a transcription) and for each of the three IEEE-754
  operations of the convex form in method section G5.3 that can round:
  `u * L[j]`, `t * L[j+1]` and their sum;
* `exact` -- the published float IS the recorded rational, with nothing
  rounded.  Used for the segment position `t`, which is a whole number
  of units in the last place scaled by a power of two, for `1 - t`,
  which the format holds exactly, and for the finished cell value,
  which the clamp and the integer rule reach by exact comparison.

Two boundaries a numeric comparison alone cannot see are checked by
hand in both shapes, exactly as the Phase 1 vector tool checks them:
the point where binary64 rounds to an infinity (past the largest finite
float there is no upper neighbour to compare with), and the sign of a
zero (+0.0 == -0.0, so `< 0` and `> 0` say nothing about which of the
two a routine produced).

One departure from the profile's own wire shape is made deliberately
and is stated here so no reader has to discover it: **a published
binary64 inside a case's `column` block is written inside a `float64`
wrapper** carrying the exact decimal it was read from, that decimal as
an exact rational, and the proof shape.  The wire value is the
wrapper's `float64` field.  Writing those numbers bare would put a
number in the file that nothing proved, which is the one thing this
document may not do.

Usage:  python3 make_generation_reference_vectors.py --seed 0 --out <path>
        (the command line the data-provenance guard uses; the seed is
        accepted and ignored, because these vectors are a fixed
        transform of given words rather than a random sample).
"""

import argparse
import datetime
import fractions
import json
import math
import struct
import sys

F = fractions.Fraction

# The one draw width of method section G3.2, as an exact scale.
TWO64 = 1 << 64

# The ladder probabilities, in hundredths, held as whole numbers exactly
# as the method holds them (G5.1): 0.99 has no exact binary spelling and
# the nearest one moves a rung onto the wrong pair of neighbours.
PCT = (0, 1, 5, 10, 25, 50, 75, 90, 95, 99, 100)
LADDER_KEYS = (
    "min", "p01", "p05", "p10", "p25", "p50", "p75", "p90", "p95", "p99", "max",
)

# binary64 shape, as integers.
SIGNIFICAND_BITS = 53
MIN_EXPONENT = -1074   # exponent of the last place of a subnormal
MAX_EXPONENT = 971     # exponent of the last place of the largest finite

# Where the finite range stops, as exact rationals.  The largest finite
# binary64 is (2**53 - 1) * 2**971; the next value the format would
# carry if its exponent range went one binade further is 2**1024, which
# it cannot hold.  Round-to-nearest sends everything from the midpoint
# between those two upwards to an infinity -- the midpoint included,
# because the tie goes to the even significand and 2**1024 is the even
# one -- so an oracle asked about a value at or above it must refuse
# rather than publish the largest finite float as though it were the
# answer.
LARGEST_FINITE = F(((1 << SIGNIFICAND_BITS) - 1) << MAX_EXPONENT)
FIRST_VALUE_PAST_THE_RANGE = F(1 << 1024)
OVERFLOW_MIDPOINT = (LARGEST_FINITE + FIRST_VALUE_PAST_THE_RANGE) / 2


# ---------------------------------------------------------------- floats


def float_bits(x):
    """The IEEE-754 binary64 bit pattern of ``x``, as an integer."""
    return struct.unpack("<Q", struct.pack("<d", x))[0]


def float_from_bits(bits):
    """The binary64 value with bit pattern ``bits``."""
    return struct.unpack("<d", struct.pack("<Q", bits))[0]


def next_up(x):
    """The next binary64 above ``x`` (finite ``x``)."""
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
    """The next binary64 below ``x`` (finite ``x``)."""
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

    This is the parity IEEE-754 round-to-nearest-ties-to-even uses.  For
    a non-negative binary64 the bit pattern is a monotone whole number
    whose last bit IS the last bit of the significand, and it stays that
    way across the subnormal/normal boundary, so one test covers every
    magnitude.
    """
    return float_bits(abs(x)) % 2 == 0


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


def _power_of_two(exponent):
    """The exact Fraction 2**exponent, for any sign of exponent."""
    if exponent >= 0:
        return F(1 << exponent, 1)
    return F(1, 1 << -exponent)


def _divide_half_even(numerator, denominator):
    """``numerator / denominator`` rounded to a whole number, ties to even.

    Both arguments are non-negative whole numbers with a positive
    divisor.  The tie is decided by comparing twice the remainder
    against the divisor, which is exact.
    """
    whole, rest = divmod(numerator, denominator)
    twice = rest * 2
    if twice > denominator:
        return whole + 1
    if twice < denominator:
        return whole
    return whole if whole % 2 == 0 else whole + 1


def _last_place_exponent(size):
    """The exponent of the last place of the binary64 nearest ``size`` > 0.

    That is ``max(-1074, floor(log2(size)) - 52)``, with the logarithm
    taken by comparison against exact powers of two so that no
    floating-point estimate can be off by one at a binade edge.
    """
    guess = size.numerator.bit_length() - size.denominator.bit_length()
    while _compare(size, _power_of_two(guess)) < 0:
        guess -= 1
    while _compare(size, _power_of_two(guess + 1)) >= 0:
        guess += 1
    exponent = guess - (SIGNIFICAND_BITS - 1)
    return max(exponent, MIN_EXPONENT)


def round_rational_to_float(value):
    """The binary64 nearest ``value`` (an exact Fraction), ties to even.

    Built by whole-number arithmetic alone: the significand is an exact
    quotient and the tie is decided by comparing twice the remainder
    against the divisor.  Overflow is refused rather than turned into an
    infinity, because an oracle that publishes an infinity has stopped
    being an oracle.
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
    """Raise unless ``result`` is the binary64 nearest ``value``, ties even.

    Re-derived from the neighbours rather than from the construction
    above: ``result`` must sit between the two exact midpoints that
    bracket it, and a value landing exactly on a midpoint must have gone
    to the even significand.  Every comparison is between exact
    rationals, so nothing here can round.

    Two boundaries are checked by hand because the bracketing comparison
    on its own is blind to them: at the largest finite float there is no
    upper neighbour to take a midpoint with, so the upper boundary is
    taken against ``OVERFLOW_MIDPOINT`` and a value at or above it is
    refused; and the sign of a zero is read from the sign bit, because
    ``+0.0 == -0.0`` makes a numeric sign test blind to it.
    """
    if math.isnan(result) or math.isinf(result):
        raise AssertionError(
            f"a published value is not a finite number: {result!r}. Only "
            "finite numbers may be published; the value that produced this "
            "one has to be recomputed or refused."
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
                f"it and {result!r} must not be published for it. Refuse the "
                "value instead of reporting the most negative finite float."
            )
    else:
        low = _compare(value, (exact + F(below)) / 2)
    if high > 0 or low < 0:
        raise AssertionError(f"{result!r} is not the binary64 nearest {value}")
    if (high == 0 or low == 0) and not significand_is_even(result):
        raise AssertionError(
            f"{result!r} is an exact midpoint of {value} and its significand "
            "is odd; ties must go to the even significand"
        )


def prove_exact_float(value, result):
    """Raise unless ``result`` IS ``value``, with nothing rounded away.

    The stronger of the two claims, and the one the transform's exact
    steps may make.  ``t`` is a whole number of units in the last place
    scaled by a power of two; ``1 - t`` is a difference the format holds
    exactly; the finished cell value is reached from the interpolation by
    exact comparison and by the whole-number rule of method section G5.4.  Each of those is either exactly the rational
    recorded beside it or a defect, so the weaker "nearest" claim would
    let a wrong value through whenever the wrong value happened to be
    the nearest float to itself.

    The sign of a zero is read from the sign bit here as well: the two
    zeros compare equal, so equality alone would accept +0.0 where the
    exact value is a negative zero.
    """
    if math.isnan(result) or math.isinf(result):
        raise AssertionError(
            f"a published value is not a finite number: {result!r}. Only "
            "finite numbers may be published."
        )
    if F(result) != value:
        raise AssertionError(
            f"{result!r} is not exactly {value}. This field claims an exact "
            "value, so the number published for it must carry no rounding "
            "at all; publish it as a 'nearest' field if it is a rounding."
        )
    if sign_bit_is_set(result) and value >= 0:
        raise AssertionError(
            f"{result!r} carries a negative zero where the exact value is "
            f"{value}. The two zeros compare equal, so only the sign bit "
            "tells them apart."
        )


# Every published number is proved by one of these two routines, named
# in the record of exact values that travels beside the document.
NEAREST = "nearest"
EXACT = "exact"

# The key that wraps every proved number.  It is a promise about the
# type as well as a place to hang the exact value on: what sits under it
# must be a Python float, which is a binary64 value and the only thing
# the neighbour comparison can be applied to.
FLOAT64 = "float64"

# The one place in the file where `float64` names the wrapper instead of
# sitting above a value: the document's own glossary says in words what
# a `float64` field means.  It is text about the wrapper, not a number
# under one, so it is exempt from the proof -- and held to being text,
# so the exemption cannot become a place to put an unproved number.
DOCUMENT_TEXT_FIELDS = frozenset({("definitions", FLOAT64)})

# The other place the name is used for something that is not a wrapper:
# the method specification calls a case's chain of interior values its
# `float64` section (G14.2), and that section is an array of records.
# The walk DESCENDS into an enumerated section path instead of handing
# it over as a value, so every number inside one is still reached and
# still has to be proved -- the exemption changes which node the walk
# treats as a wrapper, never whether the numbers under it are visited.
# It is a list of exact paths for the same reason the glossary exemption
# is: a rule about the word would exempt the next field somebody named
# `float64` as well.


# What the walk over the finished document may meet, sorted by what the
# JSON encoder does with it.  These are not the shapes the walk knows
# about beside a default of passing everything else over: they are the
# whole of what it accepts, and a node matching none of them stops the
# run.  The encoder writes a tuple as an array exactly as it writes a
# list, so a number inside a tuple reaches the file; refusing an
# unrecognised shape makes the next shape nobody thought of a failure
# here rather than a hole found later (review item P1-R8-F3).
JSON_OBJECT_TYPES = (dict,)
JSON_ARRAY_TYPES = (list, tuple)
# Written by the encoder as something other than a number: text, the
# `true`/`false` literals, and `null`.  `bool` has to be tested before
# `int`, because `True` and `False` are Python ints by inheritance.
JSON_NON_NUMBER_TYPES = (str, bool, type(None))
JSON_NUMBER_TYPES = (int, float)

OBJECT = "object"
ARRAY = "array"
NUMBER = "number"
NOT_A_NUMBER = "not a number"


def _where(path):
    """A readable name for one place in the document."""
    if not path:
        return "the top level of the document"
    return ".".join(str(step) for step in path)


def _named(fields):
    """The listed field paths as one readable phrase."""
    if not fields:
        return "none at all"
    return ", ".join(sorted(_where(field) for field in fields))


def _json_shape(node, path):
    """Name which of the four shapes above ``node`` is.

    The refusal at the end is the point of the function: a node matching
    none of the four is a shape nobody accounted for, and a shape nobody
    accounted for is exactly where a published number goes unproved. It
    stops the run instead of being passed over.
    """
    if isinstance(node, JSON_OBJECT_TYPES):
        return OBJECT
    if isinstance(node, JSON_ARRAY_TYPES):
        return ARRAY
    if isinstance(node, JSON_NON_NUMBER_TYPES):
        return NOT_A_NUMBER
    if isinstance(node, JSON_NUMBER_TYPES):
        return NUMBER
    raise AssertionError(
        f"{_where(path)} carries a {type(node).__name__}, which this walk "
        f"has no rule for, so it cannot say whether a number is inside it: "
        f"{node!r}. Every value this document publishes has to be an object, "
        "an array, text, a true/false, a null, or a number. Give the walk a "
        "rule for this shape -- and a proof for whatever numbers it holds -- "
        "or do not publish it."
    )


def _keys_in_order(node, path):
    """``node``'s keys, sorted, refusing one that is not text.

    JSON names every field with text, so the encoder would rewrite a key
    that is not a string as the text of its own spelling.  A number put
    in a key position would reach the file that way with nothing able to
    prove it, so it stops the run here.
    """
    not_text = [key for key in node if not isinstance(key, str)]
    if not_text:
        raise AssertionError(
            f"{_where(path)} is written with {not_text[0]!r} as one of its "
            "keys, which is not text. JSON names every field with text, so "
            "the encoder would rewrite that key as the text of its own "
            "spelling and this walk would have no number there to prove. "
            "Use a text key."
        )
    return sorted(node)


def _published_numbers(node, path=(), section_fields=frozenset()):
    """Every value ``node`` publishes as a number, with the path to it.

    Walks the finished document rather than the code that built it, so a
    number added by a new field is found whether or not anyone
    remembered to prove it.  Two kinds of value come back, and between
    them they leave no number in the document unvisited:

    * whatever sits under a ``"float64"`` key, of whatever type at all.
      The wrapper is a promise about the type, so a value there is
      handed over even when it is not a number -- a whole number, a
      piece of text or a nested object under that key is a broken
      promise to be refused, not something to walk past;
    * every other value written as a JSON number, whole or fractional
      alike, at any depth and inside any container the encoder turns
      into an object or an array.

    ``True`` and ``False`` are Python ints by inheritance, but JSON
    writes them as ``true`` and ``false`` rather than as numbers, so
    they are not numbers here -- except under a ``float64`` key, where
    nothing at all is skipped.

    The walk is closed rather than open: every node it reaches has to be
    one of the shapes named above this function, and one that is not
    stops the run.
    """
    shape = _json_shape(node, path)
    if shape == OBJECT:
        for key in _keys_in_order(node, path):
            child = node[key]
            if key == FLOAT64 and path + (key,) not in section_fields:
                yield path + (key,), child
            else:
                yield from _published_numbers(
                    child, path + (key,), section_fields
                )
    elif shape == ARRAY:
        for index, item in enumerate(node):
            yield from _published_numbers(item, path + (index,), section_fields)
    elif shape == NUMBER:
        yield path, node
    # NOT_A_NUMBER is text, a true/false or a null: the encoder writes
    # it as something other than a number, so there is nothing here for
    # a proof to reach.


def prove_every_published_float(
    published,
    exact_values,
    whole_number_fields=frozenset(),
    text_fields=frozenset(),
    section_fields=frozenset(),
):
    """Prove every number in ``published`` against the exact value it stands for.

    This is what makes the file's claim true.  The construction is not
    trusted at all here: each number is looked up with the exact
    rational it was built from and re-derived from its two binary64
    neighbours.  Four things stop the run rather than being published
    unproved:

    * a node of a shape the walk has no rule for, which is refused by
      the walk itself rather than passed over, so a number inside a
      container nobody accounted for cannot reach the file quietly;
    * a number with no exact value recorded for it -- a field somebody
      added without saying what it means;
    * a value under a ``"float64"`` key that is not a binary64 value.
      JSON has one kind of number, so a Python int is published as a
      number exactly as a float is, and a proof that asked only whether
      a value was a float would walk straight past ``{"float64": 7}``;
    * a whole number anywhere the document has not said in advance that
      it publishes one, named in ``whole_number_fields``.

    ``text_fields`` names the paths where ``"float64"`` is the subject
    being written about rather than a wrapper above a value -- the
    document's own glossary entry for the wrapper.  Each one must hold
    text, so an unproved number cannot be parked there either.

    ``section_fields`` names the paths where ``"float64"`` is a section
    of the document rather than a wrapper.  The walk descends into one
    instead of handing it over, so every number inside is still visited
    and still has to be proved.

    ``exact_values`` maps the path of a published number, without its
    trailing ``"float64"`` key, to one of

      ``(NEAREST, exact)``  the binary64 nearest an exact rational,
      ``(EXACT, exact)``    exactly that rational, nothing rounded.

    The match is one-to-one in both directions: every ``float64`` field
    needs a claim, and every claim must have been spent on a field.  A
    claim left over is how a skipped field hides, because the count of
    proved numbers alone cannot tell the two apart.

    Returns how many numbers were proved.
    """
    proved = 0
    proved_fields = set()
    for path, value in _published_numbers(published, (), section_fields):
        if path and path[-1] == FLOAT64:
            if path in text_fields:
                if not isinstance(value, str):
                    raise AssertionError(
                        f"{_where(path)} is the document's own account of "
                        "what a 'float64' field means, so it has to be text. "
                        f"It carries {value!r} instead. Publish that number "
                        "as a 'float64' field of its own with the exact "
                        "value it stands for recorded beside it, or put the "
                        "wording back."
                    )
                continue
            if not isinstance(value, float):
                raise AssertionError(
                    f"{_where(path)} publishes {value!r}, which is not a "
                    "binary64 value. A 'float64' field is a promise about "
                    "the type: the proof re-derives a float from its two "
                    "neighbouring binary64 values and has nothing to work "
                    "with otherwise. Publish a Python float there, or move "
                    "the value out of the 'float64' field."
                )
            field = path[:-1]
            claim = exact_values.get(field)
            if claim is None:
                raise AssertionError(
                    f"{_where(path)} publishes {value!r} with no exact value "
                    "recorded to check it against. Record the exact value "
                    "for this field so it can be proved, or do not publish "
                    "it."
                )
            if claim[0] == NEAREST:
                prove_nearest_float(claim[1], value)
            elif claim[0] == EXACT:
                prove_exact_float(claim[1], value)
            else:
                raise AssertionError(
                    f"{_where(path)} records {claim[0]!r} as the way to prove "
                    f"{value!r}, which is not one of {NEAREST!r} or {EXACT!r}."
                )
            proved_fields.add(field)
            proved += 1
        elif isinstance(value, float):
            raise AssertionError(
                f"{_where(path)} carries the number {value!r} outside a "
                "'float64' field, so nothing proved it. Publish every number "
                "as a 'float64' field and record the exact value it stands "
                "for beside it."
            )
        elif path not in whole_number_fields:
            raise AssertionError(
                f"{_where(path)} publishes the whole number {value!r}, and "
                "this document names no whole-number field there. A number "
                "nobody proved must not be published: publish it as a "
                "'float64' field with the exact value it stands for recorded "
                "beside it, or, if it is a count rather than a measurement, "
                "name it among the whole-number fields in this generator."
            )
    unspent = [field for field in exact_values if field not in proved_fields]
    if unspent:
        raise AssertionError(
            f"an exact value is recorded for {_named(unspent)}, but the "
            "document publishes no 'float64' field there, so that claim "
            "proved nothing. A claim left over is how a skipped field "
            "hides: publish the field, or remove the claim."
        )
    return proved


# ------------------------------------------------------- exact decimals


def decimal_to_fraction(text):
    """The exact rational value of a decimal literal, refusing anything else.

    Published numbers enter this file as decimal TEXT so that the
    binary64 beside each one is a claim the proof layer re-derives
    rather than a transcription of whatever a Python literal happened to
    produce.  The grammar is the one this file writes: an optional sign,
    digits, an optional fraction, an optional ``e`` exponent.
    """
    body = text
    sign = 1
    if body.startswith("-"):
        sign, body = -1, body[1:]
    elif body.startswith("+"):
        body = body[1:]
    exponent = 0
    if "e" in body:
        body, _, power = body.partition("e")
        exponent = int(power)
    if "." in body:
        whole, _, fraction = body.partition(".")
    else:
        whole, fraction = body, ""
    digits = whole + fraction
    if not digits or not digits.isdigit():
        raise ValueError(f"{text!r} is not a decimal literal this file writes")
    exponent -= len(fraction)
    value = F(sign * int(digits))
    if exponent >= 0:
        return value * F(10**exponent)
    return value / F(10 ** (-exponent))


def rational_text(value):
    """An exact rational written as ``p/q``, or ``p`` when ``q`` is 1."""
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _proved_nearest(value):
    """The nearest binary64, constructed and then proved from neighbours.

    The proof is repeated for every published number by
    ``prove_every_published_float`` once the document is complete; this
    one stops a wrong number at the place it was built, where the error
    message can name the field.
    """
    result = round_rational_to_float(value)
    prove_nearest_float(value, result)
    return result


def nearest_field(text):
    """A published input: exact decimal text, its rational, its binary64."""
    exact = decimal_to_fraction(text)
    return {
        "decimal": text,
        "exact": rational_text(exact),
        FLOAT64: _proved_nearest(exact),
        "proof": NEAREST,
    }, (NEAREST, exact)


def exact_field(value):
    """A published float that IS the exact rational recorded beside it."""
    exact = F(value)
    prove_exact_float(exact, value)
    return {
        "exact": rational_text(exact),
        FLOAT64: value,
        "proof": EXACT,
    }, (EXACT, exact)


def nearest_result_field(exact, value):
    """A published float that is the binary64 nearest a computed rational."""
    prove_nearest_float(exact, value)
    return {
        "exact": rational_text(exact),
        FLOAT64: value,
        "proof": NEAREST,
    }, (NEAREST, exact)


# ------------------------------------------- the transform, section by section


def bounded(word, size):
    """``(word * size) >> 64`` -- method section G3.4(b).

    The multiply-high rule: the whole part of ``unit(word) * size``, a
    value in ``0 .. size - 1``, consuming exactly one word every time it
    is called so that a run's word count is a fixed function of the
    published facts.
    """
    if size < 1:
        raise ValueError("a bounded range needs a size of at least one")
    return (word * size) >> 64


def permutation(count, words):
    """The arrangement of ``0 .. count - 1`` of method section G3.4(c).

    Consumes exactly ``max(count - 1, 0)`` words.  The loop runs
    downward, the drawn index is inclusive of ``i`` itself, and the swap
    happens even when ``j == i``; all three change the bytes, so all
    three are written out.
    """
    needed = max(count - 1, 0)
    if len(words) != needed:
        raise AssertionError(
            f"an arrangement of {count} entries consumes {needed} words and "
            f"{len(words)} were supplied"
        )
    order = list(range(count))
    supply = list(words)
    for position in range(count - 1, 0, -1):
        index = bounded(supply.pop(0), position + 1)
        order[position], order[index] = order[index], order[position]
    return order


def ladder_segment(numerator, denominator):
    """The unique ``j`` in ``0 .. 9`` with ``PCT[j]*D <= 100*N < PCT[j+1]*D``.

    Scanned upward from zero and stopped at the first that holds, as
    method sections G5.3 and G7.3 fix.  The probabilities are strictly
    increasing, so the segment is unique.
    """
    scaled = 100 * numerator
    for index in range(10):
        if PCT[index] * denominator <= scaled < PCT[index + 1] * denominator:
            return index
    raise AssertionError(
        f"{numerator}/{denominator} falls in no ladder segment; the position "
        "of a stratum or a rank is always below one by construction"
    )


REACHABLE = (("zero", "positive"), ("negative", "zero", "positive"))


def band_sizes(negatives, zeros, positives, negative_strata, positive_strata):
    """The even split of method section G5.2, band by band."""
    sizes = []
    bands = []
    for count, strata, band in (
        (negatives, negative_strata, "negative"),
        (zeros, 1 if zeros > 0 else 0, "zero"),
        (positives, positive_strata, "positive"),
    ):
        for index in range(strata):
            sizes.append(
                (index + 1) * count // strata - index * count // strata
            )
            bands.append(band)
    return sizes, bands


def band_strata(negatives, zeros, positives, values):
    """How the different values divide between the bands -- G5.2.

    Returns ``(M_neg, M_pos)``.  The share is proportional to the cells
    on each side, rounded with ties upward and computed exactly in whole
    numbers, then clamped so that a band holding cells keeps a stratum.
    """
    rest = values - (1 if zeros > 0 else 0)
    if rest < 0:
        raise AssertionError(
            "fewer different values are permitted than the zero stratum alone "
            "requires; this document would be refused by the feasibility stage"
        )
    if negatives > 0 and positives > 0:
        share = negatives + positives
        negative_strata = (2 * rest * negatives + share) // (2 * share)
        negative_strata = max(1, min(rest - 1, negative_strata))
        return negative_strata, rest - negative_strata
    if negatives > 0:
        return rest, 0
    if positives > 0:
        return 0, rest
    return 0, 0


def stratum_layout(numeric, negatives, zeros, positives, values, pair=None):
    """The strata of method section G5.2: sizes and starting positions.

    Returns ``(sizes, starts, bands)`` in the fixed order negatives
    ascending, then the zero stratum, then positives ascending -- which
    is the sorted order of the column's own values, and the order the
    ladder is a statement about.  ``bands`` names each stratum
    ``negative``, ``zero`` or ``positive``, which is what the sign
    repair of G5.5 reads.  ``pair`` overrides the band share, which is
    what the carrier step's band half of G5.2 hands back.
    """
    if pair is None:
        pair = band_strata(negatives, zeros, positives, values)
    sizes, bands = band_sizes(negatives, zeros, positives, pair[0], pair[1])
    # ``starts[s]`` is the number of cells in all strata before ``s``.
    starts = []
    running = 0
    for size in sizes:
        starts.append(running)
        running += size
    if running != numeric:
        raise AssertionError(
            f"the strata hold {running} cells and the column publishes "
            f"{numeric} numeric cells"
        )
    return sizes, starts, bands


def can_carry_point_free(index, sizes, bands, ladder, integer_valued):
    """Whether stratum ``index`` can hold a point-free value -- G5.2.

    The zero stratum holds exactly ``0``; a pinned end holds a published
    rung, so it can carry only where that rung has a point-free
    spelling; and any other stratum can, because the values step of
    G6.4 may take it to a whole number.
    """
    total = len(sizes)
    if bands[index] == "zero":
        return True
    if not (index == 0 or (index == total - 1 and total >= 2)):
        return True
    end = ladder[0] if index == 0 else ladder[10]
    return point_free_spelling(end, integer_valued) is not None


def carrier_room(sizes, bands, flags, reachable):
    """The most cells the strata that can carry could ever cover -- G5.2.

    A band with no stratum that can carry offers nothing, because cells
    never cross a sign band; a band that has one offers every cell it
    holds except the one each of its other strata must keep.
    ``reachable`` is which bands the demand can be written in: every one
    for ``W``, and the two that are not negative for ``W_plus``.
    """
    room = 0
    for band in reachable:
        holds = [index for index in range(len(sizes)) if bands[index] == band]
        if not any(flags[index] for index in holds):
            continue
        for index in holds:
            room += sizes[index] if flags[index] else sizes[index] - 1
    return room


def carrier_bands(
    negatives, zeros, positives, pair, ladder, integer_valued, demand, plus_demand
):
    """The BAND half of G5.2's carrier step (review item P2-C4-F3).

    How the different values divide between the negative and the
    positive side is no more published than how many cells each holds.
    A band left with one stratum, where that stratum is a pinned end
    whose rung carries a point, can carry no point-free cell at all and
    every cell of that band is stuck on it.  So one stratum moves into
    such a band from the other divided band -- ``W_plus`` before ``W``,
    the negative side before the positive -- where the other band keeps
    at least one and the move raises ``carrier_room``.

    ``S``, the zero stratum, the sign counts and the draw budget of G4.3
    are all unchanged: both bands keep a stratum, so the zero stratum
    keeps its place in the order, and G4.3 counts strata, not cells.
    """
    for wanted, reachable in ((plus_demand, REACHABLE[0]), (demand, REACHABLE[1])):
        for step in range(2):
            sizes, bands = band_sizes(
                negatives, zeros, positives, pair[0], pair[1]
            )
            flags = [
                can_carry_point_free(index, sizes, bands, ladder, integer_valued)
                for index in range(len(sizes))
            ]
            room = carrier_room(sizes, bands, flags, reachable)
            if room >= wanted:
                break
            moved = pair
            if step == 0 and negatives > 0 and pair[1] >= 2:
                moved = (pair[0] + 1, pair[1] - 1)
            if step == 1 and positives > 0 and pair[0] >= 2:
                moved = (pair[0] - 1, pair[1] + 1)
            if moved == pair:
                continue
            other, other_bands = band_sizes(
                negatives, zeros, positives, moved[0], moved[1]
            )
            other_flags = [
                can_carry_point_free(
                    index, other, other_bands, ladder, integer_valued
                )
                for index in range(len(other))
            ]
            if carrier_room(other, other_bands, other_flags, reachable) > room:
                pair = moved
    return pair


def carrier_split(sizes, bands, ladder, integer_valued, published, zeros, positives):
    """The carrier step of method section G5.2 (review item P2-C4-F3).

    Three of the six styles can be worn only by a cell whose value has a
    point-free spelling, so how many such cells a column HAS is settled
    by the split, before any style is chosen.  Where the strata that can
    carry cover fewer cells than the published map asks to be written
    that way, cells move into them: the leading-plus share first and
    only over the bands that are not negative, always within one sign
    band so ``G``, ``Z`` and ``P`` are untouched, never emptying a
    stratum so ``S`` is untouched, and the fewest the demand needs.

    A numeric block publishes no multiplicity map, so the even split is
    the method's own default rather than a published fact, while
    ``numeric_styles`` is published and EXACT-OBSERVABLE.  Plan P2-D6's
    feasibility rule 4 fixes which of the two gives way.
    """
    remaining = _effective_style_map(published)
    cells = sum(sizes)
    demand = min(sum(remaining[style] for style in POINT_FREE_STYLES), cells)
    if demand < 1:
        return list(sizes)
    moved = list(sizes)
    flags = [
        can_carry_point_free(index, sizes, bands, ladder, integer_valued)
        for index in range(len(sizes))
    ]
    plus_demand = min(remaining["leading_plus"], zeros + positives)
    for wanted, reachable in (
        (plus_demand, REACHABLE[0]),
        (demand, REACHABLE[1]),
    ):
        room = sum(
            size
            for size, flag, band in zip(moved, flags, bands)
            if flag and band in reachable
        )
        short = wanted - room
        for band in reachable:
            if short <= 0:
                break
            takers = [
                index
                for index in range(len(moved))
                if flags[index] and bands[index] == band
            ]
            givers = [
                index
                for index in range(len(moved))
                if not flags[index] and bands[index] == band
            ]
            if not takers or not givers:
                continue
            take = min(short, sum(moved[index] - 1 for index in givers))
            if take <= 0:
                continue
            short -= take
            left = take
            for index in givers:
                step = min(moved[index] - 1, left)
                moved[index] -= step
                left -= step
            for step, index in enumerate(takers):
                moved[index] += (step + 1) * take // len(takers) - (
                    step * take // len(takers)
                )
    if sum(moved) != cells or any(size < 1 for size in moved):
        raise AssertionError(
            "the carrier step must move cells between strata of one band "
            "without emptying a stratum or changing the column's cell count"
        )
    return moved


def restarted(sizes):
    """``starts[s]``: the number of cells in all strata before ``s``."""
    starts = []
    running = 0
    for size in sizes:
        starts.append(running)
        running += size
    return starts


def ladder_at(ladder, position, denominator):
    """The published ladder read at one exact place (method G5.6).

    The same segment rule and the same convex form G5.3 builds values
    with, so a share of the distribution is read by the construction's
    own arithmetic rather than by a second reading of it.
    """
    segment = ladder_segment(position, denominator)
    return convex_interpolation(
        position, denominator, ladder[segment], ladder[segment + 1]
    )["clamped"]


def convex_interpolation(position, denominator, low, high):
    """The stratified inverse transform of method section G5.3.

    ``position / denominator`` is the exact place inside the
    distribution.  The segment is located by whole-number comparison,
    the offset inside it is turned into ``t``, a whole number of units
    in the last place scaled by a power of two, and the value is the
    convex form in exactly the four IEEE-754 binary64 operations the
    method names and no others, followed by the clamp.

    Returns a record of every step with the exact rational each one
    stands for, so the file can publish the whole chain rather than only
    its answer: the difference form the method rejects and the convex
    form it requires part company at exactly these intermediates.
    """
    segment = ladder_segment(position, denominator)
    above = 100 * position - PCT[segment] * denominator
    width = (PCT[segment + 1] - PCT[segment]) * denominator
    scaled = (above << SIGNIFICAND_BITS) // width
    if not 0 <= scaled <= (1 << SIGNIFICAND_BITS) - 1:
        raise AssertionError(
            "the segment position left the half-open unit interval, which "
            "the method's own bound on A and B forbids"
        )
    t = math.ldexp(float(scaled), -SIGNIFICAND_BITS)
    left = low
    right = high
    # The four operations, in this order, and no others.
    u = 1.0 - t
    x1 = u * left
    x2 = t * right
    total = x1 + x2
    # ... then the clamp, in this order: the lower bound first and the
    # upper bound second, which is the order the method writes and the
    # order that decides a value when the two rungs are equal.
    clamped = max(total, left)
    clamped = min(clamped, right)
    return {
        "segment": segment,
        "t": t,
        "t_exact": F(scaled, 1 << SIGNIFICAND_BITS),
        "u": u,
        "u_exact": F(1) - F(t),
        "x1": x1,
        "x1_exact": F(u) * F(left),
        "x2": x2,
        "x2_exact": F(t) * F(right),
        "interpolated": total,
        "interpolated_exact": F(x1) + F(x2),
        "clamped": clamped,
    }


def integer_rule(value):
    """To nearest, ties toward positive infinity -- method section G5.4.

    Not banker's rounding and not toward zero: two implementations that
    disagree here disagree on bytes, and half-even would make a twin's
    rounding depend on the parity of a neighbour.  Both subtractions are
    exact -- for a magnitude at or above 2**52 the value is already
    whole, and below that the truncation is exactly representable.
    """
    whole = int(value)
    rest = value - float(whole)
    if rest > 0.5:
        return float(whole + 1)
    if rest == 0.5:
        return float(whole + 1)
    if rest < -0.5:
        return float(whole - 1)
    if rest == -0.5:
        return float(whole)
    return float(whole)


def class_repair(value, band, low, high):
    """The sign repair of method section G5.5.

    Where the ladder and the sign counts disagree, the counts win: a
    stratum in the negative band whose value is at or above zero takes
    the larger of ``min`` and ``-1``, and a stratum in the positive band
    whose value is at or below zero takes the smaller of ``max`` and
    ``1``.  The zero stratum needs no repair, because it was never
    drawn.  Both fallbacks are inside ``[min, max]`` whenever they are
    reachable, and both are whole numbers when the column's values are.
    """
    if band == "negative" and value >= 0:
        return max(low, -1.0), True
    if band == "positive" and value <= 0:
        return min(high, 1.0), True
    return value, False


# ------------------------------------------------------- numeric spelling


def shortest_round_trip(value):
    """``(digits, decpt)`` with ``value == 0.digits * 10**decpt``.

    The shortest decimal digit string that reads back as exactly
    ``value``, shortest first and then nearest with ties to the even
    significand -- method section G6.2.  Found by exact rational
    arithmetic: for each digit count in turn the correctly rounded
    decimal of that width is formed by whole-number division, and the
    first width whose decimal rounds back to ``value`` wins.  Nothing
    here calls the platform's own formatter, so the answer is this
    file's and not the interpreter's.
    """
    if value == 0.0:
        return "0", 1
    exact = F(abs(value))
    # The decimal exponent, located by comparison against exact powers of
    # ten so no logarithm estimate can be off by one at a decade edge.
    decpt = 0
    while exact >= F(10) ** decpt:
        decpt += 1
    while exact < F(10) ** (decpt - 1):
        decpt -= 1
    for width in range(1, 18):
        scale = decpt - width
        if scale >= 0:
            numerator, denominator = exact.numerator, exact.denominator * 10**scale
        else:
            numerator, denominator = exact.numerator * 10 ** (-scale), exact.denominator
        digits = _divide_half_even(numerator, denominator)
        carried = decpt
        if digits >= 10**width:
            digits //= 10
            carried += 1
        candidate = F(digits) * (F(10) ** (carried - width))
        try:
            reads_back = round_rational_to_float(candidate)
        except ValueError:
            # A short decimal near the top of the range can round to a
            # value binary64 cannot hold; it is therefore not a spelling
            # of this value, and the next width is tried.
            continue
        if reads_back == abs(value):
            # Trailing zeros of the digit string do not change the value
            # and are not part of the shortest spelling, so decpt is
            # unchanged when they go.
            return str(digits).rstrip("0") or "0", carried
    raise AssertionError(
        f"no decimal of at most seventeen digits reads back as {value!r}, "
        "which binary64 makes impossible"
    )


def _fixed_point(digits, decpt):
    """``0.digits * 10**decpt`` in fixed-point notation, with ``.0`` when whole."""
    if decpt <= 0:
        return "0." + "0" * (-decpt) + digits
    if decpt >= len(digits):
        return digits + "0" * (decpt - len(digits)) + ".0"
    return digits[:decpt] + "." + digits[decpt:]


def _exponent_form(digits, decpt, marker):
    """``d[.ddd]e±XX``: sign always written, exponent at least two digits."""
    body = digits[0] + ("." + digits[1:] if len(digits) > 1 else "")
    power = decpt - 1
    return f"{body}{marker}{'-' if power < 0 else '+'}{abs(power):02d}"


def canonical_spelling(value, integer_valued):
    """The canonical spelling of method section G6.2.

    A whole-number column writes the base-ten digits of the value and
    nothing else; every other column writes the shortest round-trip
    digits, in fixed-point notation when ``-4 < decpt <= 16`` and in
    exponent notation otherwise.  ``0`` is written ``0``, never ``-0``.
    """
    if integer_valued:
        whole = int(value)
        return str(whole)
    if value == 0.0:
        return "0.0"
    digits, decpt = shortest_round_trip(value)
    sign = "-" if value < 0 else ""
    if -4 < decpt <= 16:
        return sign + _fixed_point(digits, decpt)
    return sign + _exponent_form(digits, decpt, "e")


STYLE_ORDER = (
    "plain",
    "leading_zero",
    "leading_plus",
    "decimal",
    "exponent_lower",
    "exponent_upper",
)

# The three styles whose text carries neither a decimal point nor an
# exponent, which is what the contract's first-match ladder counts them
# by (contract 7.5.4, method G6.2).  A cell can wear one of these only
# where its value has a point-free spelling at all.
POINT_FREE_STYLES = ("plain", "leading_zero", "leading_plus")


def point_free_spelling(value, integer_valued):
    """The point-free spelling of method section G6.2, or ``None``.

    ``plain``, ``leading_zero`` and ``leading_plus`` write a text
    carrying neither a decimal point nor an exponent, so on a column
    publishing ``integer_valued: false`` the canonical spelling will not
    serve: the canonical spelling of the whole value 100 is ``100.0``,
    which the contract's ladder counts as ``decimal``.  The point-free
    spelling is therefore defined for its own sake.

    Where the column publishes ``integer_valued: true`` the canonical
    spelling is already the base-ten digits of the value and nothing
    else (G6.2's first clause), so it IS the point-free spelling and is
    returned unchanged.  Otherwise, with ``D`` and ``decpt`` the
    shortest round-trip digits and decimal point: where
    ``decpt >= len(D)`` -- a whole value -- the spelling is the sign,
    ``D`` and ``decpt - len(D)`` trailing zeros, and zero is written
    ``0`` and never ``-0``.  Where that does not hold the value has no
    point-free spelling at all: ``12.5`` has none, because inserting
    zeros in front of it leaves the point exactly where it was.

    THERE IS NO WIDTH CEILING (owner decision 10, 2026-08-13).  An
    earlier revision stopped at ``decpt <= 16``, the fixed-point window
    of the contract's CANONICAL spelling -- which governs the numbers
    inside a profile document and not the spelling of a cell in the
    twin.  A plain cell owes that it reads back as the same number and
    that it classifies as plain, and the full digit expansion of a whole
    value does both however many figures it takes.  While the ceiling
    stood, a column whose source wrote ``100000000000000000000`` in
    figures was published ``plain`` and written back with a point.
    """
    if integer_valued:
        return canonical_spelling(value, True)
    digits, decpt = shortest_round_trip(value)
    if decpt < len(digits):
        return None
    sign = "-" if value < 0 else ""
    return sign + digits + "0" * (decpt - len(digits))


def styled_spelling(style, value, integer_valued, order):
    """One numeric cell in one of the six styles of method section G6.1.

    ``order`` is the leading-zero order the family of G6.3 carries
    INSIDE the style: order zero is the style's own base spelling and
    each step writes one more zero straight after the sign, which leaves
    the contract's ladder where it was -- a point keeps a cell
    ``decimal``, an ``e`` or an ``E`` keeps it in its exponent case, a
    leading plus keeps it ``leading_plus``.  ``plain`` is the one style
    with no family, because a zero in front of a plain spelling is what
    makes it ``leading_zero``; ``leading_zero``'s own base spelling is
    the single zero, so its order counts from there.

    The three point-free styles are written from the point-free spelling
    of G6.2.  Where the value has none the canonical spelling stands in
    its place: G6.4 offers those styles to such a cell only once every
    other quota is spent, and the finished text then classifies as
    whatever the ladder makes of it, which G12 names as a miss.

    A thousands separator is never written -- the comma breaks the CSV
    row itself -- and accounting parentheses never appear, because they
    are the contradictory-notation stand-in of G10.3 and would change a
    cell's class.
    """
    if style not in STYLE_ORDER:
        raise AssertionError(f"{style!r} is not one of the six permitted styles")
    if style in POINT_FREE_STYLES:
        text = point_free_spelling(value, integer_valued)
        if text is None:
            text = canonical_spelling(value, integer_valued)
    else:
        digits, decpt = shortest_round_trip(value)
        sign = "-" if value < 0 else ""
        if style == "decimal":
            text = sign + _fixed_point(digits, decpt)
        else:
            marker = "e" if style == "exponent_lower" else "E"
            text = sign + _exponent_form(digits, decpt, marker)
    if style == "plain":
        if order:
            raise AssertionError("the plain style carries no leading-zero family")
        return text
    sign = "-" if text.startswith("-") else ""
    body = text[len(sign):]
    if style == "leading_zero":
        return sign + "0" * (order + 1) + body
    if style == "leading_plus":
        if sign:
            raise AssertionError(
                "there is no leading-plus spelling of a negative value"
            )
        return "+" + "0" * order + body
    return sign + "0" * order + body


def _effective_style_map(published):
    """The published map with the withheld remainder added to ``plain``.

    That is what the recount from the written CSV is measured against
    (method G6.4, contract 7.5.7): every style but ``plain`` matches its
    own published count exactly, and ``plain`` matches its published
    count plus the remainder, because the pooled cells are written in
    the style that changes nothing a reader infers.
    """
    remaining = {style: 0 for style in STYLE_ORDER}
    for style, count in published.items():
        if style == "(withheld)":
            remaining["plain"] += count
        elif style in remaining:
            remaining[style] += count
        else:
            raise AssertionError(f"{style!r} is not one of the six styles")
    return remaining


def whole_inside(value, band, share, ends, reach, taken):
    """The whole number one stratum may take -- method section G6.4.

    The nearest first, which is the half unit G12.2's window already
    owes.  Where that one is another stratum's already -- which is what
    a FLAT ladder produces, so a column whose commonest value is its own
    published ``min`` reaches it -- the walk steps one unit at a time,
    ``+1``, ``-1``, ``+2``, ``-2``, and takes the first that lies inside
    the stratum's own share of the ladder (review item P2-C4-F3).  A
    value inside its own share costs G5.6's window nothing, because that
    window already carries the width of the stratum covering a rank.

    Three bounds hold for every candidate, the nearest included: zero is
    never crossed, no number another stratum holds is taken, and the
    published ``min`` and ``max`` are never left -- that last one
    because G5.4 rounds a tie toward positive infinity, so a value of
    ``88.5`` rounds to ``89`` and would carry a column whose published
    ``max`` IS ``88.5`` above its own end.
    """
    want = integer_rule(value)
    for step in range(reach + 1):
        for candidate in ([want] if step == 0 else [want + step, want - step]):
            if any(candidate == other for other in taken):
                continue
            if point_free_spelling(candidate, False) is None:
                continue
            if band == "negative" and not candidate < 0:
                continue
            if band == "positive" and not candidate > 0:
                continue
            if ends is not None and not ends[0] <= candidate <= ends[1]:
                continue
            if step > 0 and (
                share is None or not share[0] <= candidate <= share[1]
            ):
                continue
            return candidate
    return None


def whole_number_values(
    published, values, sizes, starts, bands, ladder, numeric, integer_valued
):
    """The VALUES step of method section G6.4, taken before the styles.

    The map and the values are one question: a ``plain`` quota needs
    cells whose values are whole, and on a column publishing
    ``integer_valued: false`` the ladder hands back values that mostly
    are not.  So, before styles are assigned, ``W`` is the sum of
    ``plain``, ``leading_zero`` and ``leading_plus`` in the effective
    map, capped at the numeric cell count -- the same number G5.2's
    carrier step made the split serve, and ``W_plus`` likewise.

    The walk is taken twice, in the order the carrier step uses and for
    the same reason: first over the strata that are not negative until
    the cells they cover reach ``W_plus``, because a plus needs a value
    that is not negative as well as one with no point, and then over
    every stratum until they reach ``W``.  Each pass walks the strata in
    ascending order and takes the fewest of them the shortfall needs to
    a whole number by ``whole_inside``.

    Two strata are never taken: the two pinned ends, which hold the
    published ends of the ladder.

    Returns the values, moved where the shortfall asked for it.
    """
    total = len(values)
    remaining = _effective_style_map(published)
    cells = sum(sizes)
    wanted = min(sum(remaining[style] for style in POINT_FREE_STYLES), cells)
    values = list(values)
    if integer_valued or wanted < 1:
        return values
    free = sum(size for size, band in zip(sizes, bands) if band != "negative")

    def carried(reachable):
        return sum(
            size
            for size, value, band in zip(sizes, values, bands)
            if band in reachable
            and point_free_spelling(value, integer_valued) is not None
        )

    taken = list(values)
    for demand, reachable in (
        (min(remaining["leading_plus"], free), REACHABLE[0]),
        (wanted, REACHABLE[1]),
    ):
        for index in range(total):
            if carried(reachable) >= demand:
                break
            if index == 0 or (index == total - 1 and total >= 2):
                continue
            if bands[index] not in reachable or bands[index] == "zero":
                continue
            if point_free_spelling(values[index], integer_valued) is not None:
                continue
            share = None
            ends = None
            if ladder is not None:
                share = (
                    ladder_at(ladder, starts[index], numeric),
                    ladder_at(ladder, starts[index] + sizes[index], numeric),
                )
                ends = (ladder[0], ladder[10])
            moved = whole_inside(
                values[index], bands[index], share, ends, total + 1, taken
            )
            if moved is None:
                continue
            taken.append(moved)
            values[index] = moved
    return values


def style_allocation(published, values, integer_valued):
    """Which cell gets which style -- method section G6.4.

    Largest-remaining-quota over the numeric cells in stratum order and,
    inside a stratum, in ascending cell index, with ties broken by the
    enumeration order of G6.1 and the withheld remainder added to
    ``plain``.  Largest-remaining rather than a block per style, because
    a block assignment would put every exponent-styled cell at one end
    of the distribution and a reader of the twin would find style
    correlated with magnitude where the real column had none.

    A cell's style is what the contract's ladder makes of the text the
    twin finally writes, never a label kept beside the cell, so a style
    is offered to a cell only where the finished text would classify
    back as that style: ``leading_plus`` needs a value that is not
    negative, and the three point-free styles need a value that has a
    point-free spelling.

    The LOOK-AHEAD is part of the rule and not an optimisation.
    ``carriers[i]`` is how many cells from ``i`` onward can wear a
    point-free style and ``plus_carriers[i]`` how many of those are not
    negative; a choice is admissible only where it leaves the point-free
    quotas still inside the carriers that come after it.  Without that,
    largest-remaining spends a cell that could have worn a point-free
    style on a form any cell could have worn, and the quota arrives at
    the end of the column with nothing left to carry it.

    THE ANONYMOUS POOL GIVES WAY BEFORE A NAMED COUNT DOES (review item
    P2-C4-F3).  The withheld remainder standing inside the ``plain``
    quota says how many cells were pooled and never which of the six
    forms they took, so where the point-free cells cannot carry every
    quota it is the anonymous claim that yields.  That gives the
    look-ahead four answers, tried in order: the choice that keeps
    every quota placeable, the pool included; the choice that keeps
    every NAMED quota placeable; a point-free style on every cell that
    can wear one, since being this far means the point-free counts
    cannot all be placed however the rest of the column goes and a
    carrier spent on a form any cell could have worn makes the shortfall
    one worse than the column's own values force; and the largest
    remaining count this cell can wear at all.

    Returns ``(chosen, missed)``, where ``missed`` counts by style the
    quotas the column's own facts left no cell for.  Naming a miss is
    not a licence to leave a quota unplaced: where a quota's own cells
    exist the look-ahead puts them there, and ``missed`` is empty.
    """
    remaining = _effective_style_map(published)
    pool = min(published.get("(withheld)", 0), remaining["plain"])
    total = len(values)
    point_free = [
        point_free_spelling(value, integer_valued) is not None for value in values
    ]
    carriers = [0] * (total + 1)
    plus_carriers = [0] * (total + 1)
    for index in range(total - 1, -1, -1):
        carries = 1 if point_free[index] else 0
        carriers[index] = carriers[index + 1] + carries
        plus_carriers[index] = plus_carriers[index + 1] + (
            carries if not values[index] < 0 else 0
        )

    def largest(pool):
        return min(pool, key=lambda name: (-remaining[name], STYLE_ORDER.index(name)))

    def wearable(style, index):
        if style == "leading_plus" and values[index] < 0:
            return False
        if point_free[index] or style not in POINT_FREE_STYLES:
            return True
        # THE POOL IS OFFERED TO A CELL THAT CANNOT BE WRITTEN PLAINLY,
        # where it is spelled canonically instead (Phase 3 plan
        # P3-D8.1).  Contract 7.5.7 used to write every pooled cell
        # `plain`, which a column whose published `min` or `max` carries
        # a point can never do, so the remainder came out short by that
        # cell.  A pooled cell has no published form, so nothing is owed
        # by writing it in its own value's canonical text.  The offer
        # opens only while the pool is still standing AND the point-free
        # claims outnumber the carriers left, which is what keeps every
        # other column placed exactly as before.
        if style != "plain" or pool <= 0:
            return False
        demand = sum(remaining[name] for name in POINT_FREE_STYLES)
        return demand > carriers[index + 1]

    chosen = []
    missed = {}
    for index in range(total):
        offered = [style for style in STYLE_ORDER if remaining[style] > 0]
        can_wear = [style for style in offered if wearable(style, index)]
        admissible = []
        saved = []
        for style in can_wear:
            owed = sum(remaining[name] for name in POINT_FREE_STYLES) - (
                1 if style in POINT_FREE_STYLES else 0
            )
            spent = 1 if style == "plain" and pool > 0 else 0
            plus_owed = remaining["leading_plus"] - (
                1 if style == "leading_plus" else 0
            )
            if plus_owed > plus_carriers[index + 1]:
                continue
            if owed - (pool - spent) <= carriers[index + 1]:
                saved.append(style)
            if owed <= carriers[index + 1]:
                admissible.append(style)
        # Where no choice keeps every quota placeable, the pool is what
        # gives; where not even the named quotas fit, every cell that
        # can wear a point-free style takes one, because the shortfall
        # is then one cell worse for each carrier spent elsewhere; where
        # the cell can wear nothing left at all the largest remaining
        # quota is spent on it and the text it does classify as is what
        # gets written.
        carriers_left = [
            style for style in can_wear if style in POINT_FREE_STYLES
        ]
        style = largest(admissible or saved or carriers_left or can_wear or offered)
        remaining[style] -= 1
        if style == "plain" and pool > 0:
            pool -= 1
        if style not in can_wear:
            missed[style] = missed.get(style, 0) + 1
        chosen.append(style)
    return chosen, missed


# ------------------------------------------------------ datetime ordinals


def days_from_civil(year, month, day):
    """Days from 1970-01-01, proleptic Gregorian -- method section G7.1.

    The leap rule is the one the method names: a year divisible by four
    is a leap year, except a century not divisible by four hundred.
    """
    shifted = year - (1 if month <= 2 else 0)
    era = (shifted if shifted >= 0 else shifted - 399) // 400
    year_of_era = shifted - era * 400
    day_of_year = (153 * (month + (-3 if month > 2 else 9)) + 2) // 5 + day - 1
    day_of_era = (
        year_of_era * 365 + year_of_era // 4 - year_of_era // 100 + day_of_year
    )
    return era * 146097 + day_of_era - 719468


def civil_from_days(days):
    """The inverse of ``days_from_civil``."""
    shifted = days + 719468
    era = (shifted if shifted >= 0 else shifted - 146096) // 146097
    day_of_era = shifted - era * 146097
    year_of_era = (
        day_of_era
        - day_of_era // 1460
        + day_of_era // 36524
        - day_of_era // 146096
    ) // 365
    year = year_of_era + era * 400
    day_of_year = day_of_era - (
        365 * year_of_era + year_of_era // 4 - year_of_era // 100
    )
    shifted_month = (5 * day_of_year + 2) // 153
    day = day_of_year - (153 * shifted_month + 2) // 5 + 1
    month = shifted_month + (3 if shifted_month < 10 else -9)
    return year + (1 if month <= 2 else 0), month, day


def ordinal_of(text, resolution):
    """The ordinal of a canonical published instant -- method section G7.1."""
    if resolution == "quarter":
        year, quarter = text.split("-Q")
        return 4 * (int(year) - 1970) + (int(quarter) - 1)
    if resolution == "month":
        # G7.1's month row: twelve to the year, from the same origin
        # the quarter counts from.  A month names a SPAN, so it has a
        # space of its own and no day is consulted.
        return 12 * (int(text[0:4]) - 1970) + (int(text[5:7]) - 1)
    date_text = text[:10]
    year, month, day = (int(part) for part in date_text.split("-"))
    days = days_from_civil(year, month, day)
    if resolution == "date":
        return days
    clock = text[11:]
    hours, minutes, seconds = (int(part) for part in clock.split(":"))
    return 86400 * days + 3600 * hours + 60 * minutes + seconds


def precision_form(ordinal, resolution, time_precision, subsecond_digits):
    """The cell text of method section G7.5, before the offset suffix."""
    if resolution == "quarter":
        year = 1970 + ordinal // 4
        quarter = ordinal % 4 + 1
        return f"{year:04d}-Q{quarter}"
    if resolution == "month":
        year = 1970 + ordinal // 12
        return f"{year:04d}-{ordinal % 12 + 1:02d}"
    if resolution == "date":
        year, month, day = civil_from_days(ordinal)
        return f"{year:04d}-{month:02d}-{day:02d}"
    days, rest = divmod(ordinal, 86400)
    year, month, day = civil_from_days(days)
    hours, rest = divmod(rest, 3600)
    minutes, seconds = divmod(rest, 60)
    stem = f"{year:04d}-{month:02d}-{day:02d}T{hours:02d}:{minutes:02d}"
    if time_precision == "minute":
        return stem
    stem = f"{stem}:{seconds:02d}"
    if time_precision == "second":
        return stem
    # The fractional digits are zeros: the profile publishes how MANY
    # digits the finest cell carried and nothing about their values, so
    # any other digits would be an invented fact.
    return stem + "." + "0" * subsecond_digits


def interpolated_ordinal(position, denominator, rungs):
    """One interior rank's ordinal -- the transform of method section G7.3.

    The floor division is the stated rounding direction: toward the
    EARLIER instant, always, before the epoch included.  Python's ``//``
    floors toward negative infinity, and that is the intended behaviour
    -- a rule that truncated toward zero would round in opposite
    directions on either side of 1970.
    """
    segment = ladder_segment(position, denominator)
    above = 100 * position - PCT[segment] * denominator
    width = (PCT[segment + 1] - PCT[segment]) * denominator
    return rungs[segment] + (
        above * (rungs[segment + 1] - rungs[segment])
    ) // width


def endpoint_cell(text, resolution, time_precision, subsecond_digits, shift):
    """An endpoint cell, from the endpoint's OWN fields -- method section G7.5.

    The two endpoint cells do not travel through the ordinal space of
    G7.1 (P2-C2-F5).  That space has one place for ``HH:MM:59`` and the
    next for ``HH:MM+1:00`` and none for the ``SS`` of ``60`` the
    profile contract's canonical form admits, so an endpoint carrying
    one would come back as the following minute -- an exact published
    end turned into a neighbouring instant.

    So: read the published endpoint as its four fields, take the date
    with ``HH:MM`` and ``SS`` of ``00``, move THAT by ``shift`` (nought
    on the local clock, the cell's own offset in seconds on the shared
    one), cut the result to the recorded ``time_precision``, and write
    the published seconds field back unchanged.  Every offset is a whole
    number of minutes, so the move never touches the seconds field and a
    ``60`` survives it.  For every ``SS`` of ``00`` through ``59`` this
    produces exactly the bytes the ordinal route produces, which is why
    it moves no other frozen case.
    """
    if resolution != "datetime":
        # A whole date and a quarter are already the cell text G7.5's
        # table asks for, and neither has a time of day to move.
        return text
    year, month, day = (int(part) for part in text[:10].split("-"))
    hours, minutes, seconds = (int(part) for part in text[11:].split(":"))
    minute = (
        86400 * days_from_civil(year, month, day) + 3600 * hours + 60 * minutes
    )
    written = precision_form(
        minute + shift, resolution, time_precision, subsecond_digits
    )
    if time_precision == "minute":
        # The one precision with no seconds field at all, which contract
        # invariant D10 admits only where both ends carry `SS` of `00`.
        return written
    # YYYY-MM-DDTHH:MM:SS -- the seconds field is the two characters at
    # 17 and 18, and anything after them is the fraction.
    return written[:17] + f"{seconds:02d}" + written[19:]


def offset_form(offset):
    """The offset suffix, and the seconds it shifts a wall clock by.

    ``(none)`` and ``(withheld)`` are written with no offset at all --
    the second of those is a loss, named as one, because the profile
    does not say which offsets those cells carried.
    """
    if offset in ("(none)", "(withheld)"):
        return "", 0
    if offset == "Z":
        return "Z", 0
    sign = -1 if offset.startswith("-") else 1
    hours, minutes = (int(part) for part in offset[1:].split(":"))
    return offset, sign * (3600 * hours + 60 * minutes)


# --------------------------------------------------- invented spellings


DIGITS = tuple("0123456789")
CODE = tuple(
    "-"
    + "0123456789"
    + "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    + "_"
    + "abcdefghijklmnopqrstuvwxyz"
)
WIDE = tuple(chr(point) for point in range(0x20, 0x7F))

# Positional constraints of method section G9.1, applied to every
# invented spelling: no space at either end, so trimming cannot change a
# value and none reads as blank; and no leading character a spreadsheet
# reads as a formula, so no invented value creates a hazard the report
# would have to count.
FORMULA_LEADERS = ("=", "+", "-", "@")

CODE_CHARACTERS = frozenset(CODE)
DIGIT_CHARACTERS = frozenset(DIGITS)

# The three alphabet BANDS of method section G9.5 step 4, in the order
# the contract names the two counts that fix them: the figures answer
# for `n_all_digits`, the code alphabet for the further
# `n_code_alphabet - n_all_digits`, and the wide alphabet for whatever
# is left.  A declared identifier packs its groups over exactly these
# three and over nothing else (G9.6).
FIGURES = "figures"
CODE_BAND = "code"
WIDE_BAND = "wide"
IDENTIFIER_BANDS = (FIGURES, CODE_BAND, WIDE_BAND)


def _not_a_digit(character):
    """A code-alphabet cell's leftmost character, so it is not all-digits."""
    return character not in DIGIT_CHARACTERS


def _outside_the_code_alphabet(character):
    """A wide cell's leftmost character, so it is not code-alphabet."""
    return character not in CODE_CHARACTERS


def _not_a_leading_zero(character):
    """The figures band's leading character when the cells are whole numbers."""
    return character in DIGIT_CHARACTERS and character != "0"


def _permitted(character, first, last, leading_extra):
    if first and character in FORMULA_LEADERS:
        return False
    if (first or last) and character == " ":
        return False
    return not (
        first and leading_extra is not None and not leading_extra(character)
    )


def enumerated_spelling(alphabet, length, index, leading_extra=None):
    """Plain base-|A| counting -- method section G9.2.

    ``A[0]`` is the zero digit and the leftmost character is the most
    significant, so index ``k`` maps to the string whose character at
    position ``i`` from the RIGHT is ``A[(k // |A|**i) mod |A|]``.  Where
    a positional constraint rejects a character, the first character of
    the same alphabet meeting that constraint takes its place, in the
    alphabet's own order.  There is no rejection loop anywhere: the
    n-th spelling is a mixed-radix decomposition in a fixed number of
    steps.
    """
    size = len(alphabet)
    characters = []
    for place in range(length - 1, -1, -1):
        characters.append(alphabet[(index // size**place) % size])
    for position, character in enumerate(characters):
        first = position == 0
        last = position == length - 1
        if not _permitted(character, first, last, leading_extra):
            for candidate in alphabet:
                if _permitted(candidate, first, last, leading_extra):
                    characters[position] = candidate
                    break
            else:
                raise AssertionError(
                    "no character of this alphabet meets the positional "
                    "constraint, so the domain is empty at this length"
                )
    return "".join(characters)


def case_flip(spelling, counter):
    """The case-flip family of method sections G8.2 and G9.3.

    ``counter`` is written in binary and the case of the alphabetic
    position named by every set bit is flipped, with bit 0 the LEFTMOST
    alphabetic position.  A spelling with ``L`` letters supplies
    ``2**L - 1`` partners.
    """
    places = [index for index, char in enumerate(spelling) if char.isalpha()]
    if counter >= 1 << len(places):
        return None
    characters = list(spelling)
    for bit, place in enumerate(places):
        if counter >> bit & 1:
            character = characters[place]
            characters[place] = (
                character.lower() if character.isupper() else character.upper()
            )
    return "".join(characters)


def folded(text):
    """Trim, then Unicode case-fold -- the shipped ``parsing.folded`` rule."""
    return text.strip().casefold()


def partner_family(parent, longest):
    """Every fold-collision partner of one parent -- method section G9.3.

    **The fold the partners have to come down onto is the SHIPPED fold,
    and the shipped fold trims before it turns the case over**
    (P2-C2-F6).  A partner is therefore a case flip, edge spacing, or
    both, and the family is enumerated in one fixed order so that two
    implementations build the same partners:

    * the edge spacing is taken by ascending TOTAL number of spaces,
      and within one total the LEADING share ascends -- the spaces go
      to the end first, then are moved leftward one at a time -- so a
      total of ``t`` supplies ``t + 1`` placements;
    * within one placement the case flips are taken in ascending
      binary-counter order, bit 0 the leftmost alphabetic position,
      with ``k = 0`` the parent's own case;
    * the parent itself -- no spacing and ``k = 0`` -- is not one of its
      own partners and is stepped over.

    Case flips of the unspaced parent are therefore the first
    ``2**L - 1`` partners, in exactly the order the case-flip-only
    construction gave them, so a column whose collisions case alone can
    carry writes what it wrote before.  A parent written in figures
    alone has no case at all: its family begins at one space, which is
    the whole point -- that column's collisions cannot be built by case
    changes and were named as a loss until this construction existed.

    The walk stops when the spacing would carry the partner past
    ``longest``, the longest length the column publishes, because no
    slot of that column may take a longer value.
    """
    letters = sum(1 for character in parent if character.isalpha())
    total = 0
    while len(parent) + total <= longest:
        for leading in range(total + 1):
            placed = " " * leading + parent + " " * (total - leading)
            for counter in range(1 << letters):
                if total == 0 and counter == 0:
                    continue
                yield case_flip(placed, counter)
        total += 1


def invented_variants(parent, used, wanted):
    """The invented variant spellings of method section G8.2.

    Case flips first, in binary-counter order, skipping any candidate
    equal to a spelling already used in this column; then trailing
    spaces, one more each time, which the fold trims away and the reader
    preserves, and whose supply has no end.  A parent with no letters
    exhausts the case flips immediately and goes straight to the spaces.
    """
    produced = []
    seen = set(used)
    counter = 1
    while len(produced) < wanted:
        candidate = case_flip(parent, counter)
        if candidate is None:
            break
        counter += 1
        if candidate in seen:
            continue
        produced.append(candidate)
        seen.add(candidate)
    spaces = 1
    while len(produced) < wanted:
        candidate = parent + " " * spaces
        spaces += 1
        if candidate in seen:
            continue
        produced.append(candidate)
        seen.add(candidate)
    return produced


def invented_levels(used, sizes):
    """The neutral stand-in labels of method section G8.3.

    ``group-1``, ``group-2``, … in order, each candidate skipped and the
    number advanced when it collides, raw or folded, with any spelling
    already used in the column.  They carry no fragment of any real
    value, are not one of the spellings that mean "no value", do not
    read as a number or a date, need no quoting, and do not begin with a
    character a spreadsheet reads as a formula.
    """
    seen = set(used)
    folds = {folded(text) for text in used}
    produced = []
    counter = 1
    for size in sizes:
        while True:
            candidate = f"group-{counter}"
            counter += 1
            if candidate in seen or folded(candidate) in folds:
                continue
            seen.add(candidate)
            folds.add(folded(candidate))
            produced.append((candidate, size))
            break
    return produced


# ------------------------------------------------------------ the writer


NO_VALUE_SPELLINGS = frozenset(
    {"", "-", "--", ".", "?", "n/a", "na", "nan", "none", "null"}
)


def text_stand_ins(used, wanted):
    """``text-1``, ``text-2``, … -- method sections G10.3 and G10.4.

    Each is checked against the spellings that mean "no value" and
    against every spelling already used in the column, and ``k`` is
    advanced on a collision.  Each parses as no number and as no date,
    so it stays in its own class.
    """
    seen = set(used)
    produced = []
    counter = 1
    while len(produced) < wanted:
        candidate = f"text-{counter}"
        counter += 1
        if candidate in seen or folded(candidate) in NO_VALUE_SPELLINGS:
            continue
        seen.add(candidate)
        produced.append(candidate)
    return produced


def csv_field(text, one_column, absent):
    """One CSV field, under the byte rules of method section G2.

    Minimal quoting: a field is quoted when and only when it holds a
    comma, a quote character, a carriage return or a line feed -- plus
    the canonical exception for a row that would otherwise be empty.  A
    one-column table's absent cell is written as two quote characters
    rather than as nothing, because an empty line is what the shipped
    reader refuses and the second reader drops.
    """
    if absent and one_column:
        return '""'
    if any(mark in text for mark in (",", '"', "\r", "\n")):
        return '"' + text.replace('"', '""') + '"'
    return text


def place(content, missing, rows, words):
    """Extend with the absent cells, then arrange -- method section G4.2.

    The absent cells are placed by the same arrangement that places
    everything else, which is what makes their positions seeded-random
    without a second mechanism and without a second draw budget.
    """
    extended = list(content) + [""] * missing
    if len(extended) != rows:
        raise AssertionError(
            f"the column holds {len(extended)} cells and the table has {rows} "
            "rows"
        )
    order = permutation(rows, words)
    return [extended[order[index]] for index in range(rows)]


# ------------------------------------------------------- the four builders


def _label_content(column):
    """The content list of a label column -- method sections G8.1 and G8.4."""
    content = []
    used = []
    for level in column["levels"]:
        for spelling in sorted(level["variants"]):
            content.extend([spelling] * level["variants"][spelling])
            used.append(spelling)
        withheld = level["variants_withheld"]
        wanted = sum(withheld.values())
        if not level["variants"] and not withheld:
            content.extend([level["label"]] * level["count"])
            used.append(level["label"])
            continue
        invented = invented_variants(level["label"], used, wanted)
        supply = iter(invented)
        for key in sorted(withheld, key=int):
            for _ in range(withheld[key]):
                spelling = next(supply)
                content.extend([spelling] * int(key))
                used.append(spelling)
    for spelling, size in invented_levels(used, column["suppressed_level_counts"]):
        content.extend([spelling] * size)
        used.append(spelling)
    return content


def _datetime_content(column):
    """The content list of a datetime column -- method sections G7.2 to G7.5.

    The parsed cells come first, in ascending rank, and the unparsed
    stand-ins follow.  The method fixes the ranks and fixes the
    stand-ins but does not say in which order the two groups enter
    ``content``; this file takes the order every other role uses -- the
    reproduced values first, the counted stand-ins after -- and says so,
    because a reader has to know which reading was taken.
    """
    resolution = column["resolution"]
    parsed = column["n_present"] - column["n_unparsed"]
    rungs = [
        ordinal_of(column["date_percentiles"][key], resolution)
        for key in LADDER_KEYS
    ]
    offsets = _offset_allocation(column, parsed)
    words = iter(column["_content_words"])
    content = []
    for rank in range(parsed):
        # Ranks 0 and P-1 are the two published ends, and they are built
        # from the endpoint's own fields rather than from an ordinal
        # (G7.5): the ordinal space has no place for an `SS` of `60`.
        endpoint = None
        ordinal = None
        if rank == 0:
            endpoint = column["earliest"]
        elif rank == parsed - 1 and parsed >= 2:
            endpoint = column["latest"]
        else:
            ordinal = interpolated_ordinal(
                rank * TWO64 + next(words), parsed * TWO64, rungs
            )
        suffix, shift = offset_form(offsets[rank])
        moved = shift if (
            column["datetimes_read_at"] == "utc" and resolution == "datetime"
        ) else 0
        if endpoint is not None:
            text = endpoint_cell(
                endpoint,
                resolution,
                column["time_precision"],
                column["subsecond_digits"],
                moved,
            )
        else:
            text = precision_form(
                ordinal + moved,
                resolution,
                column["time_precision"],
                column["subsecond_digits"],
            )
        content.append(text + suffix)
    content.extend(text_stand_ins(content, column["n_unparsed"]))
    return content


def _offset_allocation(column, parsed):
    """Which offset each rank carries -- method section G7.4."""
    remaining = dict(column["utc_offsets"])
    allocated = [None] * parsed
    for rank, field in ((0, "earliest_utc_offset"), (parsed - 1, "latest_utc_offset")):
        named = column[field]
        if named not in ("(none)", "(withheld)") and remaining.get(named, 0) > 0:
            allocated[rank] = named
            remaining[named] -= 1
    def key(name):
        return (name in ("(none)", "(withheld)"), name)
    for rank in range(parsed):
        if allocated[rank] is not None:
            continue
        for name in sorted(remaining, key=key):
            if remaining[name] > 0:
                allocated[rank] = name
                remaining[name] -= 1
                break
        else:
            raise AssertionError(
                "the published offset counts do not cover every parsed cell"
            )
    return allocated


def slot_lengths(slot, low, high):
    """The lengths one slot of an invented column may take.

    G9.2 pins the two extreme lengths -- the FIRST spelling of a column
    has the shortest published length and the SECOND has the longest --
    which is what makes ``min_length`` and ``max_length``
    EXACT-OBSERVABLE at no cost in words.  G9.3 step 3 reads the same
    two pins as the window a partner taking that slot may hold, and
    every other slot may take any length in the published range.
    """
    if slot == 0:
        return (low,)
    if slot == 1 and high > low:
        return (high,)
    return tuple(range(low, high + 1))


def identifier_family(band, whole_numbers, length):
    """One band's family at one length -- method sections G9.5 step 4, G9.6.

    Returns the alphabet the block is enumerated over, how many
    characters that block holds, the rule its leftmost character obeys,
    and the text written after it; ``None`` where the band has no
    spelling at this length at all.

    Where the column publishes ``all_whole_numbers`` FALSE the three
    bands are the three alphabets themselves: the figures write digits
    and nothing else; a code-alphabet cell carries a non-digit at its
    leftmost position so it does not count as all-digits; and a wide
    cell carries a character outside the code alphabet at its leftmost
    permitted position so it does not count as code-alphabet.

    Where it publishes ``all_whole_numbers`` TRUE, G9.6 fixes one
    whole-number spelling per band and the bands still come from the two
    published alphabet counts and from nothing else.  The figures write
    the digits themselves with a non-zero leading digit, so the
    spelling's length is its digit count; the code band writes
    ``<digits>e0``, which reads back as a whole number and holds a
    character the figures do not; and outside the code alphabet the cell
    is written ``<digits>.``, which reads back as a whole number and
    holds a character the code alphabet does not.  Each of those two
    templates spends characters on its marker, so a published length
    below three in the code band, or below two in the wide band, leaves
    the band no whole-number spelling at that length -- the corner G9.6
    names.  Where the whole published RANGE leaves a band no such
    spelling the description's facts cannot all hold and a shipped run
    refuses generation for it (G12); where some other length in the
    range does carry one, the ordinary walk takes the value and
    ``all_whole_numbers`` is recounted from the finished cells and named
    in the report, which is the open defect review item P2-C5-F4 leaves
    standing.
    """
    if whole_numbers:
        if band == FIGURES:
            return DIGITS, length, _not_a_leading_zero, ""
        if band == CODE_BAND:
            return (DIGITS, length - 2, None, "e0") if length >= 3 else None
        return (DIGITS, length - 1, None, ".") if length >= 2 else None
    if band == FIGURES:
        return DIGITS, length, None, ""
    if band == CODE_BAND:
        return CODE, length, _not_a_digit, ""
    return WIDE, length, _outside_the_code_alphabet, ""


def _cell_fills(sizes, available, room, owed):
    """Every way one cell of the packing grid can be filled, in G9.5's order.

    "Within a cell the different group SIZES are offered in ascending
    order and each size offers as many copies as the cell can still
    hold, falling back to fewer."  The order is what two implementations
    have to share; the completeness is what makes the quota exact.

    ``room`` is the most cells this one can take -- the smallest amount
    any of its own margins still owes -- and ``owed`` is the exact total
    it must take when it is the LAST cell that can answer for one of
    those counts, or ``None`` when it may take any total up to ``room``.
    Over one margin every count sits in exactly one cell, so every cell
    is the last for its own count and ``owed`` is always that quota:
    the single-axis rule of G9.5 is this walk with one margin, not a
    second rule.
    """

    def walk(position, left, taken):
        if position == len(sizes):
            total = room - left
            if owed is None or total == owed:
                yield taken
            return
        size = sizes[position]
        for count in range(min(available[size], left // size), -1, -1):
            yield from walk(
                position + 1, left - count * size, {**taken, size: count}
            )

    return walk(0, room, {})


def _grid_cells(margins):
    """The cells of a packing grid, in the order G9.5 fills them.

    "Each margin ranks its own counts in ascending order of their
    published values, ties by the order the contract states them in; a
    cell then carries one rank per margin and the cells are filled in
    ascending order of those ranks read margin by margin, ties by the
    cell's own number."  Each margin arrives here in the contract's own
    order, so a stable sort by published value IS the tie rule and
    nothing else is needed.

    Over two margins this is exactly row-major order over ranked rows
    and ranked columns; over one it is the ranked counts themselves;
    over three it is the same statement again, which is what lets one
    walk govern the alphabet packing of a declared identifier (G9.6),
    the class-and-alphabet packing of free text (G9.5) and the
    class-and-whole-and-sign packing of an unrepresentable column
    (G10.5).
    """
    ranks = []
    for margin in margins:
        places = sorted(range(len(margin)), key=lambda index, m=margin: m[index][1])
        ranks.append({margin[at][0]: place for place, at in enumerate(places)})
    cells = [()]
    for margin in margins:
        cells = [cell + (name,) for cell in cells for name, _count in margin]
    cells.sort(
        key=lambda cell: tuple(ranks[index][name] for index, name in enumerate(cell))
    )
    return cells


def _packed_grid(groups, margins, demanded=True):
    """Which cell of the grid each group answers for -- method section G9.5.

    ``groups`` is one entry per group, in group order, as
    ``(size, permitted cells)``; ``margins`` is one entry per published
    family of counts, each a tuple of ``(count name, published value)``
    in the contract's own order.  The answer is one cell per group, in
    group order.

    ``demanded`` is False where the caller is asking whether ONE
    candidate shape packs and has other shapes to try (G9.5's shape
    rule, P2-C4-F2); the answer is then None instead of a refusal, and
    the caller refuses only after every shape has been asked.

    **Every quota of every margin is met exactly whenever such an
    assignment exists.**  That is the whole of the rule, and it is why
    this walk backtracks rather than choosing greedily: a fill that
    leaves a later cell unable to finish is undone and the next is
    tried.  Nothing counts the work and nothing stops the walk early
    (P2-C3-F1): the only end is the finite set of cells and groups the
    description itself fixes.

    A cell is the LAST of one of its counts exactly when no later cell
    carrying that count can be answered for by a group that is still
    unplaced, and then it takes what that count still owes rather than
    choosing.  Two counts that force two different totals leave the cell
    with no fill at all, which is a branch that held no answer.
    """
    cells = _grid_cells(margins)

    def last_for(index, place, name, unplaced):
        for later in cells[index + 1:]:
            if later[place] != name:
                continue
            if any(later in groups[position][1] for position in unplaced):
                return False
        return True

    def walk(index, owed, unplaced):
        if index == len(cells):
            if unplaced:
                return None
            # No fill can take more than the smallest amount one of its
            # own counts still owes, so no count can go below nought and
            # a margin whose counts sum to the cells is settled the
            # moment every group is placed. A margin whose counts sum to
            # something else is a description no loader accepts, and it
            # is refused here rather than answered.
            if any(count for margin in owed for count in margin.values()):
                return None
            return {}
        cell = cells[index]
        room = min(owed[place][name] for place, name in enumerate(cell))
        forced = set()
        for place, name in enumerate(cell):
            if last_for(index, place, name, unplaced):
                forced.add(owed[place][name])
        if len(forced) > 1:
            return None
        exact = forced.pop() if forced else None
        pool = {}
        for position in unplaced:
            size, permitted = groups[position]
            if cell in permitted:
                pool.setdefault(size, []).append(position)
        sizes = sorted(pool)
        available = {size: len(pool[size]) for size in sizes}
        for fill in _cell_fills(sizes, available, room, exact):
            chosen = []
            for size in sizes:
                chosen.extend(pool[size][: fill.get(size, 0)])
            taken = sum(groups[position][0] for position in chosen)
            after = tuple(
                {name: count - (taken if name == cell[place] else 0)
                 for name, count in margin.items()}
                for place, margin in enumerate(owed)
            )
            spent = set(chosen)
            left = tuple(position for position in unplaced if position not in spent)
            rest = walk(index + 1, after, left)
            if rest is not None:
                rest[cell] = tuple(sorted(chosen))
                return rest
        return None

    start = tuple({name: count for name, count in margin} for margin in margins)
    chosen = walk(0, start, tuple(range(len(groups))))
    if chosen is None and not demanded:
        return None
    if chosen is None:
        raise AssertionError(
            "no assignment of whole groups meets every quota of every margin "
            f"{[dict(margin) for margin in margins]} over the group sizes "
            f"{[size for size, _cells in groups]}, so this column's own facts "
            "cannot all hold at once. The packing is complete, so this is a "
            "statement about the description and never about the search"
        )
    answer = [None] * len(groups)
    for cell, members in chosen.items():
        for position in members:
            answer[position] = cell
    return answer


def _band_quotas(column):
    """How many CELLS each band answers for -- method section G9.5 step 4.

    ``n_all_digits`` cells are written from the figures; a further
    ``n_code_alphabet - n_all_digits`` from the code alphabet; the rest
    from the wide alphabet.  The figures are a subset of the code
    alphabet, which is why an all-digit cell counts toward
    ``n_code_alphabet`` as well (G9.1) and why the code band's own quota
    is the difference.
    """
    figures = column["n_all_digits"]
    code = column["n_code_alphabet"] - figures
    wide = column["n_present"] - column["n_code_alphabet"]
    quotas = {FIGURES: figures, CODE_BAND: code, WIDE_BAND: wide}
    for band, quota in quotas.items():
        if quota < 0:
            raise AssertionError(
                f"the {band} band is asked for {quota} cells, so this "
                "column's two published alphabet counts cannot both hold"
            )
    return quotas


# The four classes the contract's own parser sorts a cell into, in the
# order section 9.2 states them.  A declared identifier publishes all
# four, and G9.6 packs them WITH the two alphabet counts.
IDENTIFIER_CLASSES = ("number", "out_of_range", "contradictory", "not_numeric")


def _class_quotas(column):
    """How many CELLS each parser class answers for -- G9.6, contract 9.2."""
    return {
        "number": column["n_numeric"],
        "out_of_range": column["n_out_of_range"],
        "contradictory": column["n_contradictory"],
        "not_numeric": column["n_not_numeric"],
    }


def _packed_bands(groups, column, quotas, whole_numbers, low, high):
    """Which class AND which band each group answers for -- G9.6.

    Every published count is a count of CELLS and every group covers a
    whole number of cells, so meeting a count means choosing which
    GROUPS answer for it, and every quota of BOTH margins must be met
    exactly whenever an assignment exists.

    **The classes are packed with the alphabets, not read off them**
    (review item P2-C5-F2).  A group written from an alphabet reads back
    as whatever the contract's own parser makes of it, so packing the
    alphabets alone certifies a class count instead of meeting it.  And
    which pairs a group may stand in depends on the lengths its slot may
    take -- one character cannot be a number and stand outside the
    figures at the same time -- so the slot's own window narrows the
    grid here, where the single-margin form of this walk had nothing to
    narrow.

    THIS ORACLE FREEZES ONLY THE CLASSES IT HAS A FAMILY FOR.  The two
    families a declared identifier's required cases need are ordinary
    text and ordinary numbers; a case publishing a cell too large to
    hold, or one whose notation conflicts with itself, is refused here
    rather than built from a family this file does not state.
    """
    for name in ("out_of_range", "contradictory"):
        if quotas[name]:
            raise AssertionError(
                f"this case publishes {quotas[name]} cell(s) of the {name} "
                "class, and this oracle states no identifier family for it: "
                "the required cases of G14.3 publish none, so freezing one "
                "would mean freezing a construction this file does not write"
            )
    bands = _band_quotas(column)
    class_margin = tuple((name, quotas[name]) for name in IDENTIFIER_CLASSES)
    band_margin = tuple((band, bands[band]) for band in IDENTIFIER_BANDS)
    permitted = []
    for slot, size in enumerate(groups):
        cells = set()
        for name in IDENTIFIER_CLASSES:
            for band in IDENTIFIER_BANDS:
                for length in slot_lengths(slot, low, high):
                    if _identifier_pair(name, band, whole_numbers, length):
                        cells.add((name, band))
                        break
        permitted.append((size, frozenset(cells)))
    packed = _packed_grid(permitted, (class_margin, band_margin))
    return [cell[0] for cell in packed], [cell[1] for cell in packed]


def _identifier_pair(name, band, whole_numbers, length):
    """Whether one class can be written in one band at one exact length.

    A cell of ordinary text is never written in the figures alone,
    because figures alone read back as a number; a cell that reads as a
    number is written by ``identifier_family`` and exists wherever that
    family does.  Both readings are the method's, and the recount below
    holds the finished cells to them.
    """
    if name == "not_numeric":
        return band != FIGURES
    if name != "number":
        return False
    family = identifier_family(band, whole_numbers, length)
    return family is not None and family[1] >= 1


def _identifier_recount(column, content):
    """The published identifier facts, recounted from the finished cells.

    Method section G9.6 makes ``min_length``, ``max_length``,
    ``all_whole_numbers``, ``n_all_digits`` and ``n_code_alphabet``
    EXACT-OBSERVABLE in every case, and outside owner decision 6's
    infeasible corner the three distinctness facts are exact too.  A
    reference vector that published cells missing one of them would be
    an oracle certifying the very thing the method forbids, so the
    recount is applied to the oracle's own answer before it can reach
    the file.  It is the check that would have refused revision 1's
    withdrawn rule, which wrote every cell from the figures alone
    whenever ``all_whole_numbers`` was true (review items P2-C1-F1,
    P2-C2-F7).
    """
    trimmed = [cell.strip() for cell in content]
    measured = {
        "n_present": len(content),
        "min_length": min(len(cell) for cell in content),
        "max_length": max(len(cell) for cell in content),
        "n_all_digits": sum(
            1 for cell in trimmed if cell and set(cell) <= DIGIT_CHARACTERS
        ),
        "n_code_alphabet": sum(
            1 for cell in trimmed if cell and set(cell) <= CODE_CHARACTERS
        ),
        "all_whole_numbers": bool(content)
        and all(_is_a_whole_number(cell) for cell in trimmed),
        "n_distinct": len(set(content)),
        "n_distinct_folded": len({folded(cell) for cell in content}),
        # THE FOUR PARSER CLASSES, RECOUNTED (review item P2-C5-F2).
        # P2-D6 makes them EXACT-OBSERVABLE by class-preserving
        # construction on every role, and nothing here was measuring
        # them: a vector whose cells missed one would be an oracle
        # certifying the very thing the plan forbids. This oracle builds
        # only the two classes it states a family for, so the other two
        # are recounted as nought and a case publishing either is
        # refused before the packing begins.
        "n_numeric": sum(1 for cell in trimmed if _is_a_number(cell)),
        "n_not_numeric": sum(1 for cell in trimmed if not _is_a_number(cell)),
        "n_out_of_range": 0,
        "n_contradictory": 0,
    }
    occurrences = {}
    for cell in set(content):
        key = content.count(cell)
        occurrences[key] = occurrences.get(key, 0) + 1
    width = max(len(str(key)) for key in occurrences) if occurrences else 1
    measured["n_distinct_by_occurrences"] = {
        str(key).rjust(width, "0"): occurrences[key] for key in sorted(occurrences)
    }
    for name, value in sorted(measured.items()):
        if column[name] != value:
            raise AssertionError(
                f"the cells this oracle built recount {name} as {value!r} and "
                f"the case publishes {column[name]!r}. The method requires the "
                "published value, so the construction above is wrong; do not "
                "move the published fact to meet it."
            )


def _is_a_number(text):
    """Whether one finished cell reads back as an ordinary number.

    The decimal grammar this file writes its published inputs in is the
    reading a person takes, and a cell outside it -- text, an accounting
    parenthesis, a spelling that means "no value" -- is not a number.
    A number this grammar accepts but binary64 cannot hold would be the
    out-of-range class instead, and no required case publishes one.
    """
    try:
        decimal_to_fraction(text)
    except ValueError:
        return False
    return True


def _is_a_whole_number(text):
    """Whether one finished cell reads back as a whole number.

    ``all_whole_numbers`` is true when every present cell is a whole
    number (contract section 6.8), so the recount needs the same reading
    of a cell that a reader takes.  The decimal grammar this file
    already writes its published inputs in is that reading, and anything
    outside it -- text, an accounting parenthesis, a spelling that means
    "no value" -- is not a number at all.
    """
    try:
        value = decimal_to_fraction(text)
    except ValueError:
        return False
    return value.denominator == 1


def _identifier_content(column):
    """The content list of an identifier column -- method sections G9.2, G9.3, G9.6.

    The multiplicity map fixes the groups; the two published alphabet
    counts fix which band each group answers for; the enumeration fixes
    the spellings, with the two extreme lengths pinned so ``min_length``
    and ``max_length`` are met exactly and cost no word.  Where the
    profile publishes fewer folded identities than raw spellings, the
    first of the identities are drawn from the letter-bearing part of
    the domain so each can carry a case-flip partner.

    **The bands come from the two published alphabet counts and from
    nothing else.**  Revision 1 said that a column publishing
    ``all_whole_numbers`` true writes every group from the figures; the
    method withdrew that as false (G9.6, review item P2-C1-F1), since a
    column of ``+1`` and ``+2`` publishes ``all_whole_numbers`` true
    with ``n_all_digits`` and ``n_code_alphabet`` both nought.  What
    ``all_whole_numbers`` decides is what each band WRITES, which is
    ``identifier_family`` above.

    The method fixes which spellings exist and which identity carries
    which partner, but not the order in which identities and partners
    are laid into the groups; this file lays the identities down first,
    in enumeration order, and then the partners in ascending identity
    order, and says so.  That divergence is older than this note and is
    recorded in the Phase 3 plan; it is repeated here so the next reader
    meets it as a known item.

    **AND THIS ORACLE DOES NOT MODEL G9.3 STEP 5** (plan amendment
    A-P3-12), which lays a column out again where a collision it owes
    could not be built.  It does not have to, and that is a statement
    about reach rather than an excuse: step 5 is reachable only on a
    description whose first layout leaves a partner unbuilt, and this
    oracle raises rather than stating cells for exactly that
    description -- see the two AssertionErrors below, one for a partner
    the identities cannot carry and one for a slot the packing put in
    another band.  So no case it can freeze reaches the step, no frozen
    case does today, and a case that did would need this oracle widened
    -- its naive tail replaced by G9.6's choice rule, and step 5 built
    on top of that -- BEFORE the case could be added.
    """
    occurrences = column["n_distinct_by_occurrences"]
    groups = []
    for key in sorted(occurrences, key=int):
        groups.extend([int(key)] * occurrences[key])
    distinct = column["n_distinct"]
    if len(groups) != distinct or sum(groups) != column["n_present"]:
        raise AssertionError(
            f"the multiplicity map describes {len(groups)} values covering "
            f"{sum(groups)} rows, and the column publishes {distinct} values "
            f"covering {column['n_present']} rows"
        )
    whole_numbers = column["all_whole_numbers"]
    low, high = column["min_length"], column["max_length"]
    _classes, bands = _packed_bands(
        groups, column, _class_quotas(column), whole_numbers, low, high
    )
    partners_wanted = distinct - column["n_distinct_folded"]
    identities_wanted = column["n_distinct_folded"]
    used = set()

    def take(band, lengths, letters_needed):
        """The first unused spelling of this band at the first length that has one.

        The walk over one family visits that family's indices in order
        and stops at the family's own size, which G9.4 computes before
        the walk begins, so it ends whether or not it produces a value.

        The fold-collision ask of G9.3 is an ASK (G9.2): a pass that
        insists on a letter-bearing candidate and finds none puts the
        walk back exactly where that pass began and takes it again
        without the ask, so the ask can never spend a family the
        ordinary rule could still have used.  A pass that finds nothing
        adds nothing to ``used``, which is what makes the rewind exact.
        """
        families = []
        for length in lengths:
            family = identifier_family(band, whole_numbers, length)
            if family is not None and family[1] >= 1:
                families.append(family)
        if not families:
            raise AssertionError(
                f"the published length range holds no whole-number spelling "
                f"of the {band} band, which is the corner method section G9.6 "
                "names: the published facts cannot all hold, so a shipped run "
                "refuses generation for that description before any cell is "
                "built (G12, review item P2-C5-F4). This oracle freezes no "
                "case for that corner and states no expected cells for it"
            )
        for ask in (True, False) if letters_needed else (False,):
            for alphabet, block, leading, suffix in families:
                for index in range(len(alphabet) ** block):
                    candidate = (
                        enumerated_spelling(alphabet, block, index, leading) + suffix
                    )
                    if candidate in used:
                        continue
                    if ask and not any(char.isalpha() for char in candidate):
                        continue
                    used.add(candidate)
                    return candidate
        raise AssertionError(
            f"the {band} band's domain is exhausted, which is owner decision "
            "6's infeasible corner: G9.4 says a declared identifier repeats "
            "there rather than refusing, and three distinctness facts become "
            "REPORT-ONLY. This oracle freezes no case for that corner and "
            "states no expected cells for it"
        )

    identities = []
    for position in range(identities_wanted):
        letters_needed = position < partners_wanted
        identities.append(
            take(
                bands[position],
                slot_lengths(position, low, high),
                letters_needed,
            )
        )

    partners = []
    # Partners are assigned to identities in ascending identity order,
    # one each, then a second each, so that the collisions are spread
    # rather than piled on one identity (G9.3 step 4). Each one is the
    # first member of its own identity's family (G9.3 step 2) that this
    # column has not written and whose LENGTH the taking slot may hold
    # (step 3): the two slots carrying the published length ends may
    # take only that one length, and every other slot may take any
    # length in the published range. The family is walked from its start
    # for EVERY slot and a member one slot's window turns down is not
    # spent, because a wider slot later on may still take it; and the
    # count of partners a parent has already supplied decides which
    # parent comes next, never which member is taken. Both sentences are
    # G9.3 step 2's own rule since review item P2-C4-F4 -- an ordinal
    # taken from the slot would step over a member nothing has written
    # and no window has turned down.
    for taking in range(partners_wanted):
        slot = identities_wanted + taking
        window = slot_lengths(slot, low, high)
        position = taking % identities_wanted
        partner = None
        for candidate in partner_family(identities[position], high):
            if candidate in used or len(candidate) not in window:
                continue
            partner = candidate
            break
        if partner is None:
            raise AssertionError(
                f"the identities carry {len(partners)} partners and the profile "
                f"asks for {partners_wanted}, which is owner decision 6's "
                "infeasible corner. This oracle freezes no case for that corner "
                "and states no expected cells for it"
            )
        if bands[slot] != bands[position]:
            raise AssertionError(
                "a partner stays in its identity's own band, and the packing "
                f"puts the group taking this one in the {bands[slot]} band "
                f"while its identity is in the {bands[position]} band. This "
                "oracle freezes no case for that shape and states no expected "
                "cells for it"
            )
        used.add(partner)
        partners.append(partner)
    spellings = identities + partners
    if len(spellings) != distinct:
        raise AssertionError(
            f"the construction produced {len(spellings)} spellings and the "
            f"profile publishes {distinct}"
        )
    content = []
    for group, spelling in zip(groups, spellings):
        content.extend([spelling] * group)
    _identifier_recount(column, content)
    return content


# ------------------------------------- what a finished cell reads back as


# Where binary64 stops at the small end. ``float()`` rounds to nearest
# with ties to the even significand, so a magnitude at or below half the
# smallest subnormal reads back as a zero -- an underflow the shipped
# parser refuses as a number it cannot hold, exactly as it refuses an
# overflow at the other end (``OVERFLOW_MIDPOINT`` above).
UNDERFLOW_MIDPOINT = F(1, 1 << 1075)

NOTATION_NUMBER = "n_numeric"
NOTATION_TEXT = "n_not_numeric"
NOTATION_OUT_OF_RANGE = "n_out_of_range"
NOTATION_CONTRADICTORY = "n_contradictory"

WHOLE_YES = "n_whole"
WHOLE_NO = "n_fraction"
WHOLE_UNSETTLED = "n_whole_unknown"

SIGN_POSITIVE = "n_positive"
SIGN_NEGATIVE = "n_negative"
SIGN_UNSETTLED = "n_sign_unknown"


def notation_reading(text):
    """What one finished cell's notation settles -- the tie of G10.2 and G10.5.

    Returns the three answers the recounts of this document ask of every
    cell: which notation class it belongs to, whether its notation
    settles that the value is a whole number, and which sign it settles.
    The reading is this file's own, taken from the contract's own
    definitions (sections 5.1 and 6.2) rather than from the shipped
    parser, and it is exact: the value is held as a rational and
    compared against the two points where binary64 stops, so a 400-digit
    whole number is out of range and a fraction below the smallest
    subnormal is out of range as well, each with its sign and its
    whole-number status still visible in the text.

    A sign inside accounting parentheses is the notation that conflicts
    with itself, and it settles neither the sign nor the whole-number
    status -- the shipped parser answers "unknown" for both and never
    guesses.  Ordinary text settles neither either.

    Two spellings stop the run rather than being read: a grouped one,
    because this file writes no thousands separator and states no rule
    for reading one, and anything else the decimal grammar of this file
    cannot settle.  A reading nobody can state is not a reading.
    """
    body = text.strip()
    if "," in body:
        raise AssertionError(
            f"{text!r} carries a thousands separator, and this file writes "
            "none and states no rule for reading one back. It freezes no case "
            "whose cells carry one"
        )
    if body[:1] == "(" and body[-1:] == ")":
        inside = body[1:-1].strip()
        if inside[:1] in ("+", "-"):
            try:
                decimal_to_fraction(inside[1:])
            except ValueError:
                return NOTATION_TEXT, WHOLE_UNSETTLED, SIGN_UNSETTLED
            return NOTATION_CONTRADICTORY, WHOLE_UNSETTLED, SIGN_UNSETTLED
        return NOTATION_TEXT, WHOLE_UNSETTLED, SIGN_UNSETTLED
    try:
        value = decimal_to_fraction(body)
    except ValueError:
        return NOTATION_TEXT, WHOLE_UNSETTLED, SIGN_UNSETTLED
    size = -value if value < 0 else value
    if size >= OVERFLOW_MIDPOINT or (value != 0 and size <= UNDERFLOW_MIDPOINT):
        notation = NOTATION_OUT_OF_RANGE
    else:
        notation = NOTATION_NUMBER
    whole = WHOLE_YES if value.denominator == 1 else WHOLE_NO
    if value < 0:
        return notation, whole, SIGN_NEGATIVE
    if value > 0:
        return notation, whole, SIGN_POSITIVE
    return notation, whole, SIGN_UNSETTLED


# ------------------------------------------ the unrepresentable column


# The canonical invented width of method section G10.5: a 400-digit
# whole number is far outside binary64's range, and a fraction written
# as `0.` followed by 399 zeros and one non-zero digit is far below the
# smallest subnormal. The width is invented, it is the same for every
# such column, and the report says so in those words (residual R-P2-1).
CANONICAL_WIDTH = 400

# The six shapes a wide cell may take and what each one answers for --
# method section G10.5 step 1's own table. The sign column names the
# answers the shape can give, which is the permission the packing
# carries rather than a choice an implementation may take: notation that
# conflicts with itself and ordinary text settle neither the sign nor
# the whole-number status.
UNREPRESENTABLE_SHAPES = (
    ("contradictory", NOTATION_CONTRADICTORY, WHOLE_UNSETTLED, (SIGN_UNSETTLED,)),
    ("too_large", NOTATION_OUT_OF_RANGE, WHOLE_YES, (SIGN_POSITIVE, SIGN_NEGATIVE)),
    ("too_small", NOTATION_OUT_OF_RANGE, WHOLE_NO, (SIGN_POSITIVE, SIGN_NEGATIVE)),
    ("whole_in_range", NOTATION_NUMBER, WHOLE_YES, (SIGN_POSITIVE, SIGN_NEGATIVE)),
    ("fraction_in_range", NOTATION_NUMBER, WHOLE_NO, (SIGN_POSITIVE, SIGN_NEGATIVE)),
    ("ordinary_text", NOTATION_TEXT, WHOLE_UNSETTLED, (SIGN_UNSETTLED,)),
)

# The three published families, each in the contract's own order
# (sections 5.1 and 6.2), which is the tie rule the grid of G9.5 uses
# when two counts of one margin are equal.
NOTATION_ORDER = (
    NOTATION_NUMBER, NOTATION_TEXT, NOTATION_OUT_OF_RANGE, NOTATION_CONTRADICTORY,
)
WHOLE_ORDER = (WHOLE_YES, WHOLE_NO, WHOLE_UNSETTLED)
SIGN_ORDER = (SIGN_POSITIVE, SIGN_NEGATIVE, SIGN_UNSETTLED)


def _unrepresentable_spelling(shape, sign, order):
    """The ``order``-th spelling of one shape -- method section G10.5 step 4.

    In-range cells are written as ``1``, ``-1``, ``0.5``, ``-0.5`` and
    their distinct variants from the leading-zero family, since no
    ladder and no statistic is published for this role.  The two
    out-of-range shapes are written at the canonical width, and the
    contradictory shape is the construction of G10.3.
    """
    lead = "-" if sign == SIGN_NEGATIVE else ""
    if shape == "contradictory":
        return f"(-{order + 1})"
    if shape == "whole_in_range":
        return lead + "0" * order + "1"
    if shape == "fraction_in_range":
        return lead + "0" * order + "0.5"
    if shape == "too_large":
        return lead + enumerated_spelling(
            DIGITS, CANONICAL_WIDTH, order, _not_a_leading_zero
        )
    if shape == "too_small":
        if order >= 9:
            raise AssertionError(
                "the ninth too-small spelling at the canonical width is the "
                "last one this file states, and the method fixes no further "
                "one. It freezes no case that asks for more"
            )
        return lead + "0." + "0" * (CANONICAL_WIDTH - 1) + str(order + 1)
    raise AssertionError(f"{shape!r} is not one of the six shapes of G10.5")


def _unrepresentable_recount(column, content):
    """The published unrepresentable facts, recounted from the finished cells.

    Method section G10.5 step 6 recounts every one of ``n_whole``,
    ``n_fraction``, ``n_whole_unknown``, ``n_positive``, ``n_negative``
    and ``n_sign_unknown`` from the finished cells, asking the same
    three questions of each cell that the profiler asks of a real one,
    and the four notation counts are recounted the same way on every
    role (G10.2).  A reference vector publishing cells that miss one of
    them would be an oracle certifying the very thing the method calls a
    defect rather than a deviation, so the recount runs on the oracle's
    own answer before it can reach the file.
    """
    measured = {name: 0 for name in NOTATION_ORDER + WHOLE_ORDER + SIGN_ORDER}
    for cell in content:
        for answer in notation_reading(cell):
            measured[answer] += 1
    measured["n_present"] = len(content)
    measured["n_distinct"] = len(set(content))
    measured["n_distinct_folded"] = len({folded(cell) for cell in content})
    occurrences = {}
    for cell in set(content):
        key = content.count(cell)
        occurrences[key] = occurrences.get(key, 0) + 1
    width = max(len(str(key)) for key in occurrences) if occurrences else 1
    measured["n_distinct_by_occurrences"] = {
        str(key).rjust(width, "0"): occurrences[key] for key in sorted(occurrences)
    }
    for name, value in sorted(measured.items()):
        if column[name] != value:
            raise AssertionError(
                f"the cells this oracle built recount {name} as {value!r} and "
                f"the case publishes {column[name]!r}. Every one of these is "
                "EXACT-OBSERVABLE, so the construction above is wrong; do not "
                "move the published fact to meet it."
            )


def _unrepresentable_content(column):
    """The content list of an unrepresentable column -- method section G10.5.

    **The three published families are THREE MARGINS over one set of
    cells, and no cross-tabulation of them is assumed** (P2-C3-F1). The
    description says how the cells divide by notation class, how they
    divide by whole-number status and how they divide by sign, and says
    NOTHING about how those three divisions cross -- in particular, how
    ``n_out_of_range`` divides between whole numbers and fractions is
    not a published fact.  An implementation that fixes that division by
    a rule of its own has invented a description, and may then find no
    packing where the real column had one.

    So the three margins are packed together by the grid rule of G9.5,
    over the six shapes of step 1 and the permissions their own
    notation carries, and the walk chooses among every cross-tabulation
    the three margins permit.  The groups come from
    ``n_distinct_by_occurrences``, one spelling each, exactly as they do
    for free text.
    """
    occurrences = column["n_distinct_by_occurrences"]
    groups = []
    for key in sorted(occurrences, key=int):
        groups.extend([int(key)] * occurrences[key])
    if len(groups) != column["n_distinct"] or sum(groups) != column["n_present"]:
        raise AssertionError(
            f"the multiplicity map describes {len(groups)} values covering "
            f"{sum(groups)} rows, and the column publishes "
            f"{column['n_distinct']} values covering {column['n_present']} rows"
        )
    permitted = frozenset(
        (notation, whole, sign)
        for _shape, notation, whole, signs in UNREPRESENTABLE_SHAPES
        for sign in signs
    )
    margins = (
        tuple((name, column[name]) for name in NOTATION_ORDER),
        tuple((name, column[name]) for name in WHOLE_ORDER),
        tuple((name, column[name]) for name in SIGN_ORDER),
    )
    cells = _packed_grid([(size, permitted) for size in groups], margins)
    shapes = {
        (notation, whole): shape
        for shape, notation, whole, _signs in UNREPRESENTABLE_SHAPES
    }
    content = []
    spent = {}
    used = []
    for size, cell in zip(groups, cells):
        notation, whole, sign = cell
        shape = shapes[(notation, whole)]
        if shape == "ordinary_text":
            spelling = text_stand_ins(used, 1)[0]
        else:
            spelling = _unrepresentable_spelling(shape, sign, spent.get(shape, 0))
            spent[shape] = spent.get(shape, 0) + 1
        used.append(spelling)
        content.extend([spelling] * size)
    _unrepresentable_recount(column, content)
    return content


# ----------------------------------------------------------- free text


# Each band's alphabet and the rule its leftmost character obeys --
# method section G9.5 step 4. The figures write digits and nothing else;
# a code-alphabet cell carries a non-digit at its leftmost position so
# it does not count as all-digits; a wide cell carries a character
# outside the code alphabet at its leftmost permitted position so it
# does not count as code-alphabet.
FREE_TEXT_BANDS = {
    FIGURES: (DIGITS, None),
    CODE_BAND: (CODE, _not_a_digit),
    WIDE_BAND: (WIDE, _outside_the_code_alphabet),
}

# The longest word this file will freeze a free-text case for. Rule 4 of
# G9.2 rejects a candidate that reads as a date under the shipped date
# formats, and the shortest spelling any of those formats can match is
# longer than this, so no candidate of this file's own cases can reach
# the rule. A longer word would need the rule answered rather than
# reasoned away, and this file states no reading of it.
LONGEST_FROZEN_WORD = 3


def _free_text_permits(notation, band, length):
    """Whether one class can be written in one band at one length -- G9.5 step 4.

    **The bands a group may take depend on the class it took**, and the
    dependency is part of the rule rather than something an
    implementation may leave to chance (P2-C1-F1): a cell of ordinary
    text cannot be written in figures alone, because figures alone read
    as a number. Outside the code alphabet a leading point is both
    outside it and the start of a number, so the wide band can answer
    for either class once it has two characters to spend.

    A number CAN be written in the code band, and saying it could not
    lost published counts a real table reaches (P2-C4-F2): a leading
    minus sign is a character the figures do not hold and what follows
    it is still read as a number, so `-3` is a two-character
    code-alphabet number. One character is genuinely too few -- a single
    character that reads as a number is a figure, and a figure is
    all-digits.
    """
    if notation == NOTATION_NUMBER:
        if band == FIGURES:
            return length >= 1
        return length >= 2
    if notation == NOTATION_TEXT:
        return band != FIGURES
    return False


def _free_text_spelling(notation, band, length, used):
    """One free-text word -- the enumeration of G9.2 with its rejections.

    The walk visits the family's indices in order and stops at the
    family's own size.  A candidate is rejected where this column has
    already written it, where it reads back as some other numeric class
    than the one its group has to answer for, or where it means "no
    value"; the date rule is not reasoned away but kept out of reach by
    ``LONGEST_FROZEN_WORD``.
    """
    alphabet, leading = FREE_TEXT_BANDS[band]
    for index in range(len(alphabet) ** length):
        candidate = enumerated_spelling(alphabet, length, index, leading)
        if candidate in used:
            continue
        if folded(candidate) in NO_VALUE_SPELLINGS:
            continue
        if notation_reading(candidate)[0] != notation:
            continue
        return candidate
    raise AssertionError(
        f"the {band} band at length {length} holds no further spelling that "
        f"reads back as {notation}, which is the generation-domain-too-small "
        "refusal of G9.4. This oracle freezes no case for that corner and "
        "states no expected cells for it"
    )


def _nearest_whole(exact):
    """The whole number nearest an exact rational, ties upward."""
    return (2 * exact.numerator + exact.denominator) // (2 * exact.denominator)


def wire_value(node):
    """The wire value of a published field, whatever wrapper it arrived in.

    Every published binary64 in a case's column block is written inside
    a ``float64`` wrapper carrying the exact rational it stands for, so
    that nothing in this file is a number nobody proved.  A rule that
    reads such a field reads the wire value under the wrapper; a field
    that is a whole number carries no wrapper and is itself.
    """
    if isinstance(node, dict) and isinstance(node.get(FLOAT64), float):
        return node[FLOAT64]
    return node


def _free_text_shapes(total):
    """Every pair of groups that may carry the two published ends -- G9.5.

    WHICH group carries an end is not a fact the description publishes,
    so it is part of the packing's answer and not part of its question
    (P2-C4-F2).  The pairs are offered in ascending order of the pair
    itself -- the group taking the shortest length first, then the group
    taking the longest -- so the description's own first two groups are
    tried first.  A column with one group has nothing to pair.
    """
    if total < 2:
        return [(0, 0)]
    return [
        (low, high)
        for low in range(total)
        for high in range(total)
        if high != low
    ]


def _free_text_lengths(column, groups, carriers):
    """One length per group -- method section G9.5 step 5.

    ``length.min`` and ``length.max`` are EXACT-OBSERVABLE and are
    pinned onto the two groups ``carriers`` names -- whichever pair the
    shape rule of G9.5 is asking about, which for the first shape asked
    is the description's own first two groups.  The rest start at the
    published ``length.p50`` rounded by the rule of G5.4 and clamped
    into the published range, and the residual against the whole target
    ``round(length.mean * n_present)`` is spent one character at a time,
    largest occurrence count first, ties by group order.
    """
    low = column["length"]["min"]
    high = column["length"]["max"]
    base = min(
        max(int(integer_rule(wire_value(column["length"]["p50"]))), low), high
    )
    lengths = [base] * len(groups)
    lengths[carriers[0]] = low
    if len(groups) > 1:
        lengths[carriers[1]] = high
    target = _nearest_whole(
        F(wire_value(column["length"]["mean"])) * column["n_present"]
    )
    residual = target - sum(
        size * length for size, length in zip(groups, lengths)
    )
    free = [place for place in range(len(groups)) if place not in carriers]
    while residual:
        step = 1 if residual > 0 else -1
        movable = [
            index
            for index in free
            if (lengths[index] < high if step > 0 else lengths[index] > low)
        ]
        if not movable:
            break
        index = max(movable, key=lambda place: (groups[place], -place))
        lengths[index] += step
        after = residual - step * groups[index]
        if (after > 0) != (residual > 0) and after != 0:
            break
        residual = after
    return lengths


def _free_text_words(column, groups, lengths, carriers):
    """One word count per group -- method section G9.5 step 6.

    ``words.min`` and ``words.max`` are EXACT-OBSERVABLE and pinned onto
    the same two groups the lengths pinned, which ``carriers`` names;
    ``words.mean`` is APPROXIMATED and is approached by the same
    residual walk, with no published middle rung to start the free
    groups at -- this file reads ``words.mean`` as standing where
    ``length.p50`` stands for the lengths, and says so.  Each count is
    then clamped to the ``(L + 1) // 2`` words a cell of that length can
    hold, and lengths and word counts are paired by ascending order, so
    the longest cells take the most words.
    """
    low = column["words"]["min"]
    high = column["words"]["max"]
    base = min(
        max(int(integer_rule(wire_value(column["words"]["mean"]))), low), high
    )
    counts = [base] * len(groups)
    counts[carriers[0]] = low
    if len(groups) > 1:
        counts[carriers[1]] = high
    target = _nearest_whole(
        F(wire_value(column["words"]["mean"])) * column["n_present"]
    )
    residual = target - sum(size * count for size, count in zip(groups, counts))
    free = [place for place in range(len(groups)) if place not in carriers]
    while residual:
        step = 1 if residual > 0 else -1
        movable = [
            index
            for index in free
            if (counts[index] < high if step > 0 else counts[index] > low)
        ]
        if not movable:
            break
        index = max(movable, key=lambda place: (groups[place], -place))
        counts[index] += step
        after = residual - step * groups[index]
        if (after > 0) != (residual > 0) and after != 0:
            break
        residual = after
    paired = sorted(counts)
    order = sorted(range(len(groups)), key=lambda place: (lengths[place], place))
    settled = [0] * len(groups)
    for place, index in enumerate(order):
        settled[index] = min(paired[place], max(1, (lengths[index] + 1) // 2))
    return settled


def _free_text_recount(column, content):
    """The published free-text facts, recounted from the finished cells."""
    trimmed = [cell.strip() for cell in content]
    lengths = sorted(len(cell) for cell in content)
    measured = {
        "n_present": len(content),
        "n_distinct": len(set(content)),
        "n_distinct_folded": len({folded(cell) for cell in content}),
        "n_all_digits": sum(
            1 for cell in trimmed if cell and set(cell) <= DIGIT_CHARACTERS
        ),
        "n_code_alphabet": sum(
            1 for cell in trimmed if cell and set(cell) <= CODE_CHARACTERS
        ),
    }
    for name in NOTATION_ORDER:
        measured[name] = sum(
            1 for cell in content if notation_reading(cell)[0] == name
        )
    occurrences = {}
    for cell in set(content):
        key = content.count(cell)
        occurrences[key] = occurrences.get(key, 0) + 1
    width = max(len(str(key)) for key in occurrences) if occurrences else 1
    measured["n_distinct_by_occurrences"] = {
        str(key).rjust(width, "0"): occurrences[key] for key in sorted(occurrences)
    }
    for name, value in sorted(measured.items()):
        if column[name] != value:
            raise AssertionError(
                f"the cells this oracle built recount {name} as {value!r} and "
                f"the case publishes {column[name]!r}. The method requires the "
                "published value, so the construction above is wrong; do not "
                "move the published fact to meet it."
            )
    words = [len(cell.split()) for cell in content]
    exact = {
        ("length", "min"): F(lengths[0]),
        ("length", "max"): F(lengths[-1]),
        ("length", "mean"): F(sum(lengths), len(lengths)),
        ("length", "p50"): _quantile(lengths, F(1, 2)),
        ("words", "min"): F(min(words)),
        ("words", "max"): F(max(words)),
        ("words", "mean"): F(sum(words), len(words)),
    }
    for (block, name), value in sorted(exact.items()):
        if F(wire_value(column[block][name])) != value:
            raise AssertionError(
                f"the cells this oracle built recount {block}.{name} as "
                f"{value} and the case publishes "
                f"{wire_value(column[block][name])!r}. The "
                "two ends are EXACT-OBSERVABLE, and this file freezes an "
                "average only where the walk of G9.5 lands on the published "
                "one exactly, so that no case pins a deviation nobody derived."
            )


def _quantile(sorted_values, share):
    """The profiler's own interpolated quantile, in exact rationals.

    The rung at ``share`` of a sorted sample is taken at position
    ``(n - 1) * share`` and interpolated between its two neighbours,
    which is what ``taxonomy._quantile`` computes and what the
    free-text ``length.p50`` is measured by.
    """
    place = (len(sorted_values) - 1) * share
    below = int(place)
    above = min(below + 1, len(sorted_values) - 1)
    return F(sorted_values[below]) + (place - below) * (
        F(sorted_values[above]) - F(sorted_values[below])
    )


def _free_text_content(column):
    """The content list of a free-text column -- method section G9.5.

    **Steps 3 and 4 are ONE packing, not two** (P2-C1-F1, P2-C2-F1).
    Every group answers for one class count and one alphabet count at
    the same time, and which PAIRS it may stand in depends on its own
    length, so deciding the classes in one walk and the alphabets in a
    second throws away joint assignments that exist.  The two margins
    are therefore packed together by the grid rule, with each group's
    permitted cells taken from its own length.

    **And the SHAPE is part of that same answer** (P2-C4-F2).  The
    description publishes that some group carries each end, never which
    one, so a shape fixed before the packing narrows the packing with a
    fact the profile never carried.  The shapes are offered in the fixed
    order of `_free_text_shapes`, and under each first the reading that
    holds every free group to the length step 5's walk gave it and then
    the reading that lets a free group be written at any published
    length; the first shape whose grid packs every quota exactly is the
    one taken.  So a description the first shape already answers is
    answered identically, and no published count is lost to a pinning
    the profile never asked for.
    """
    for name in (NOTATION_OUT_OF_RANGE, NOTATION_CONTRADICTORY):
        if column[name]:
            raise AssertionError(
                f"{name} is published above nought, and this file states no "
                "free-text construction for that class. It freezes no case for "
                "one"
            )
    occurrences = column["n_distinct_by_occurrences"]
    groups = []
    for key in sorted(occurrences, key=int):
        groups.extend([int(key)] * occurrences[key])
    if len(groups) != column["n_distinct"] or sum(groups) != column["n_present"]:
        raise AssertionError(
            f"the multiplicity map describes {len(groups)} values covering "
            f"{sum(groups)} rows, and the column publishes "
            f"{column['n_distinct']} values covering {column['n_present']} rows"
        )
    quotas = _band_quotas(column)
    margins = (
        tuple((name, column[name]) for name in NOTATION_ORDER),
        tuple((band, quotas[band]) for band in IDENTIFIER_BANDS),
    )
    longest = column["length"]["max"]
    settled = None
    for reach in (False, True):
        # Two groups of the same size are the same question: no
        # published count tells them apart, so a pair whose two sizes an
        # earlier pair already offered can only fail the same way.
        sized = set()
        for carriers in _free_text_shapes(len(groups)):
            if (groups[carriers[0]], groups[carriers[1]]) in sized:
                continue
            sized.add((groups[carriers[0]], groups[carriers[1]]))
            lengths = _free_text_lengths(column, groups, carriers)
            counts = _free_text_words(column, groups, lengths, carriers)
            offered = []
            for place, size in enumerate(groups):
                spans = [lengths[place]]
                if reach and place not in carriers:
                    spans = list(range(lengths[place], longest + 1))
                offered.append((
                    size,
                    frozenset(
                        (notation, band)
                        for notation in NOTATION_ORDER
                        for band in IDENTIFIER_BANDS
                        if any(
                            _free_text_permits(notation, band, length)
                            for length in spans
                        )
                    ),
                ))
            packed = _packed_grid(offered, margins, demanded=False)
            if packed is None:
                continue
            if reach:
                lengths = [
                    lengths[place]
                    if place in carriers
                    else next(
                        length
                        for length in range(lengths[place], longest + 1)
                        if _free_text_permits(*packed[place], length)
                    )
                    for place in range(len(groups))
                ]
            settled = (carriers, lengths, counts, packed)
            break
        if settled is not None:
            break
    if settled is None:
        # Every shape has been asked and none packs, so the refusal is a
        # statement about the description. The first shape raises it.
        carriers = _free_text_shapes(len(groups))[0]
        lengths = _free_text_lengths(column, groups, carriers)
        counts = _free_text_words(column, groups, lengths, carriers)
        _packed_grid(
            [
                (
                    size,
                    frozenset(
                        (notation, band)
                        for notation in NOTATION_ORDER
                        for band in IDENTIFIER_BANDS
                        if _free_text_permits(notation, band, length)
                    ),
                )
                for size, length in zip(groups, lengths)
            ],
            margins,
        )
    carriers, lengths, counts, packed = settled
    if set(counts) != {1}:
        raise AssertionError(
            "every group of a frozen case holds exactly one word: G9.5 step 7 "
            "fixes how several words share a length, but which of them the "
            "rejection rules of G9.2 are asked about is not stated, and this "
            "file freezes no case that turns on a reading it cannot take from "
            "the method"
        )
    if max(lengths) > LONGEST_FROZEN_WORD:
        raise AssertionError(
            f"a word of more than {LONGEST_FROZEN_WORD} characters can reach "
            "the date rule of G9.2, which this file states no reading of. It "
            "freezes no case that long"
        )
    content = []
    used = set()
    for size, length, (notation, band) in zip(groups, lengths, packed):
        spelling = _free_text_spelling(notation, band, length, used)
        used.add(spelling)
        content.extend([spelling] * size)
    _free_text_recount(column, content)
    return content


def numbers_class_budget(column, published):
    """The numbers class's share of one distinctness count -- method G6.5.

    The four classes take the budget in the fixed order numbers,
    out_of_range, contradictory, not_numeric.  Every non-empty class
    receives one spelling; the remainder is then offered to the classes
    in that order, each taking as much as it can use and never more than
    its own cell count, until the remainder is spent.  Only the first
    class's share is returned, because that is the one the values and
    the spellings of G5.2 and G6.5 are built against.
    """
    counts = (
        column["n_numeric"],
        column["n_out_of_range"],
        column["n_contradictory"],
        column["n_not_numeric"],
    )
    shares = [1 if count else 0 for count in counts]
    remainder = max(0, published - sum(shares))
    for index, count in enumerate(counts):
        if not count:
            continue
        take = min(remainder, count - shares[index])
        shares[index] += take
        remainder -= take
    return shares[0]


def _numeric_content(column):
    """The content list of a numeric column, and the chain behind each value.

    Method sections G5.2 to G5.5 for the values, G6.1 to G6.5 for the
    spellings, and G10.3 for the stragglers.
    """
    numeric = column["n_numeric"]
    negatives = column["n_negative"] - column["n_negative_unrepresentable"]
    zeros = column["n_zero"]
    positives = numeric - negatives - zeros
    if positives < 0:
        raise AssertionError(
            "n_zero and n_negative together exceed n_numeric, which no "
            "ordering of values can satisfy: this is generation-counts-"
            "contradict, refused before any cell is generated"
        )
    folded_budget = numbers_class_budget(column, column["n_distinct_folded"])
    values_wanted = min(numeric, folded_budget)
    ladder = [column["_rungs"][key] for key in LADDER_KEYS]
    integer_valued = column["integer_valued"]
    effective = _effective_style_map(column["numeric_styles"])
    demand = min(
        sum(effective[style] for style in POINT_FREE_STYLES), numeric
    )
    pair = band_strata(negatives, zeros, positives, values_wanted)
    if demand > 0:
        # G5.2's carrier step, band half: a band whose only stratum is a
        # pinned end that carries a point can carry no point-free cell,
        # and every cell of that band is stuck on it.
        pair = carrier_bands(
            negatives,
            zeros,
            positives,
            pair,
            ladder,
            integer_valued,
            demand,
            min(effective["leading_plus"], zeros + positives),
        )
    sizes, starts, bands = stratum_layout(
        numeric, negatives, zeros, positives, values_wanted, pair
    )
    # G5.2's carrier step, cell half: the cells a published point-free
    # count needs, put where they can be written.  It moves cells
    # between strata of one sign band, so it changes neither the number
    # of strata nor their bands, and G4.3's budget is untouched.
    sizes = carrier_split(
        sizes,
        bands,
        ladder,
        integer_valued,
        column["numeric_styles"],
        zeros,
        positives,
    )
    starts = restarted(sizes)
    words = iter(column["_content_words"])
    values = []
    chain = []
    total = len(sizes)
    for index, size in enumerate(sizes):
        if index == 0:
            values.append(ladder[0])
            continue
        if index == total - 1 and total >= 2:
            values.append(ladder[10])
            continue
        if bands[index] == "zero":
            values.append(0.0)
            continue
        position = starts[index] * TWO64 + size * next(words)
        denominator = numeric * TWO64
        segment = ladder_segment(position, denominator)
        record = convex_interpolation(
            position, denominator, ladder[segment], ladder[segment + 1]
        )
        value = record["clamped"]
        if integer_valued:
            value = integer_rule(value)
        value, repaired = class_repair(value, bands[index], ladder[0], ladder[10])
        record["stratum"] = index
        record["value"] = value
        record["repaired"] = repaired
        chain.append(record)
        values.append(value)
    # Both fallbacks apply to every stratum after the integer rule,
    # including the pinned ones (G5.5).
    for index in range(total):
        if index == 0 or (index == total - 1 and total >= 2):
            values[index], _ = class_repair(
                values[index], bands[index], ladder[0], ladder[10]
            )
    # The VALUES step of G6.4 is taken before the styles, because the map
    # and the values are one question: a point-free quota needs cells
    # whose values are whole.
    values = whole_number_values(
        column["numeric_styles"],
        values,
        sizes,
        starts,
        bands,
        ladder,
        numeric,
        integer_valued,
    )
    cell_values = []
    for index, size in enumerate(sizes):
        cell_values.extend([values[index]] * size)
    styles, missed = style_allocation(
        column["numeric_styles"], cell_values, integer_valued
    )
    content = [
        styled_spelling(style, value, integer_valued, 0)
        for style, value in zip(styles, cell_values)
    ]
    # G6.5: how many zeros are spent is decided over the WHOLE column
    # first.  Count the identities the base spellings already hold; the
    # shortfall against the folded budget is how many cells raise their
    # order, and no more, because spending a zero that was not needed
    # carries the count PAST the published one.  Cells are visited in the
    # order of G6.4 and each that raises its order takes the lowest order
    # whose folded identity is new.  A cell can raise only inside a style
    # that carries the family, which is every style but ``plain``.
    held = set()
    repeats = []
    for index, text in enumerate(content):
        identity = folded(text)
        if identity in held:
            repeats.append(index)
        else:
            held.add(identity)
    shortfall = max(0, folded_budget - len(held))
    for index in repeats:
        if not shortfall:
            break
        if styles[index] == "plain":
            continue
        order = 1
        while True:
            raised = styled_spelling(
                styles[index], cell_values[index], integer_valued, order
            )
            if folded(raised) not in held:
                break
            order += 1
        content[index] = raised
        held.add(folded(raised))
        shortfall -= 1
    content.extend(_straggler_cells(column, content))
    return content, chain, missed


def _straggler_cells(column, used):
    """The out-of-range, contradictory and ordinary-text cells of G10.3."""
    cells = []
    for index in range(column["n_out_of_range"]):
        negative = index < column["n_negative_unrepresentable"]
        cells.append(("-" if negative else "") + f"{index + 1}e999")
    for index in range(column["n_contradictory"]):
        cells.append(f"(-{index + 1})")
    cells.extend(text_stand_ins(list(used) + cells, column["n_not_numeric"]))
    return cells


# ------------------------------------------------------------- the cases


def _ladder_fields(texts):
    """A published ladder as eleven proved binary64 fields."""
    published = {}
    claims = {}
    rungs = {}
    for key in LADDER_KEYS:
        field, claim = nearest_field(texts[key])
        published[key] = field
        claims[(key,)] = claim
        rungs[key] = field[FLOAT64]
    return published, claims, rungs


def _universal(name, role, statistical_type, structural_role, quality_state, **facts):
    block = {
        "name": name,
        "position": 1,
        "role": role,
        "statistical_type": statistical_type,
        "quality_state": quality_state,
        "structural_role": structural_role,
        "missing_by_class": {
            "(blank)": 0,
            "(declared-missing)": 0,
            "(numeric-sentinel)": 0,
            "(text-code)": 0,
            "(withheld)": 0,
        },
        "missing_by_source": {},
        # The two counts contract version 5 moved out of the map above,
        # so that its keys are the table's own text and nothing else
        # (that contract's section 5).  Neither is read by any
        # generation rule; they are here because every column block
        # carries them and the loader would refuse a block that did not.
        "n_missing_blank": 0,
        "n_missing_withheld": 0,
        "n_sentinel_candidates_unpublished": 0,
        "sentinel_verdicts": [],
        "detection_evidence": "written by hand in this method specification's "
        "own neutral vocabulary; no value here comes from any table.",
        "remarks": [],
    }
    block.update(facts)
    # The census of fraction widths (contract C6-27 to C6-30), on the
    # three roles that carry a forms map and on no other: a block that
    # publishes no forms map has no decimal cells to take a census of,
    # and a loader refuses a key its role does not carry.  A block that
    # names no `decimal` cells publishes an empty census, which is what
    # every case here but two does.
    if "numeric_styles" in block and "fraction_widths" not in block:
        block["fraction_widths"] = {}
    # The census of which form each parsed date wore (contract C6-25),
    # on every column of dates and on no other role.  A column read
    # under one format wore that format in every cell that parsed, so
    # its census is that one name beside that one count; the joint ISO
    # reading is the only shape with two names in it, and no case in
    # this file takes that reading.  The census is REPORT-ONLY and
    # steers no rule of the method: it is written because every block
    # of dates carries it and a loader refuses a block that does not.
    if role == "datetime":
        parsed = block["n_present"] - block["n_unparsed"]
        block["resolution_mix"] = {block["format"]: parsed}
    if block["n_missing"]:
        block["missing_by_class"] = dict(block["missing_by_class"])
        block["missing_by_class"]["(withheld)"] = block["n_missing"]
        if role not in ("identifier", "free_text", "numeric_unrepresentable"):
            block["n_missing_withheld"] = block["n_missing"]
    return block


def _date_only():
    column = _universal(
        "column_1", "datetime", "datetime", "data", "ok",
        n_present=12, n_missing=0, n_distinct=12, n_distinct_folded=12,
        n_numeric=0, n_not_numeric=12, n_out_of_range=0, n_contradictory=0,
        format="iso-date", resolution="date", time_precision="date",
        subsecond_digits=0, datetimes_read_at="local",
        earliest="2020-01-01", latest="2020-12-31",
        earliest_utc_offset="(none)", latest_utc_offset="(none)",
        date_percentiles={
            "min": "2020-01-01", "p01": "2020-01-05", "p05": "2020-01-20",
            "p10": "2020-02-10", "p25": "2020-03-15", "p50": "2020-06-30",
            "p75": "2020-09-01", "p90": "2020-11-15", "p95": "2020-12-01",
            "p99": "2020-12-20", "max": "2020-12-31",
        },
        n_unparsed=0, utc_offsets={"(none)": 12},
    )
    return {
        "why": "the date form of G7.5, both endpoints exact, and the floor "
        "rounding of the ordinal transform: ten interior ranks each take one "
        "word and land on a whole day, never between two.",
        "column": column,
        "rows": 12,
        "identifier_declared": False,
    }


def _quarter():
    column = _universal(
        "column_1", "datetime", "datetime", "data", "ok",
        n_present=12, n_missing=0, n_distinct=12, n_distinct_folded=12,
        n_numeric=0, n_not_numeric=12, n_out_of_range=0, n_contradictory=0,
        format="year-quarter", resolution="quarter", time_precision="quarter",
        subsecond_digits=0, datetimes_read_at="local",
        earliest="2018-Q1", latest="2024-Q4",
        earliest_utc_offset="(none)", latest_utc_offset="(none)",
        date_percentiles={
            "min": "2018-Q1", "p01": "2018-Q2", "p05": "2018-Q4",
            "p10": "2019-Q2", "p25": "2020-Q1", "p50": "2021-Q3",
            "p75": "2022-Q4", "p90": "2023-Q3", "p95": "2024-Q1",
            "p99": "2024-Q3", "max": "2024-Q4",
        },
        n_unparsed=0, utc_offsets={"(none)": 12},
    )
    return {
        "why": "the quarter form of G7.5 and the quarter ordinal, where one "
        "unit is three months and no clock exists to shift.",
        "column": column,
        "rows": 12,
        "identifier_declared": False,
    }


def _month_span():
    """The second SPAN resolution, added with the month (P4-D4.3).

    Twelve months of one year, so the ordinal walk crosses no year
    boundary and a reader can check every cell by counting.  The two
    ends are pinned by G7.3 and, because a month IS its own canonical
    text, the fields route and the ordinal route of G7.5 write the same
    characters -- which is the property this case exists to freeze.
    """
    column = _universal(
        "column_1", "datetime", "datetime", "data", "ok",
        n_present=12, n_missing=0, n_distinct=12, n_distinct_folded=12,
        n_numeric=0, n_not_numeric=12, n_out_of_range=0, n_contradictory=0,
        format="iso-month", resolution="month", time_precision="month",
        subsecond_digits=0, datetimes_read_at="local",
        earliest="2024-01", latest="2024-12",
        earliest_utc_offset="(none)", latest_utc_offset="(none)",
        date_percentiles={
            "min": "2024-01", "p01": "2024-01", "p05": "2024-02",
            "p10": "2024-02", "p25": "2024-04", "p50": "2024-06",
            "p75": "2024-09", "p90": "2024-11", "p95": "2024-12",
            "p99": "2024-12", "max": "2024-12",
        },
        n_unparsed=0, utc_offsets={"(none)": 12},
    )
    return {
        "why": "the month form of G7.5 and the month ordinal of G7.1, "
        "where one unit is one month, no clock exists to shift, and the "
        "cell text is the canonical form itself.",
        "column": column,
        "rows": 12,
        "identifier_declared": False,
    }


def _offset_bearing():
    column = _universal(
        "column_1", "datetime", "datetime", "data", "ok",
        n_present=24, n_missing=0, n_distinct=24, n_distinct_folded=24,
        n_numeric=0, n_not_numeric=24, n_out_of_range=0, n_contradictory=0,
        format="iso-datetime", resolution="datetime", time_precision="second",
        subsecond_digits=0, datetimes_read_at="utc",
        earliest="2021-03-01 00:00:00", latest="2021-03-02 12:00:00",
        earliest_utc_offset="Z", latest_utc_offset="+02:00",
        date_percentiles={
            "min": "2021-03-01 00:00:00", "p01": "2021-03-01 00:30:00",
            "p05": "2021-03-01 02:00:00", "p10": "2021-03-01 04:00:00",
            "p25": "2021-03-01 06:00:00", "p50": "2021-03-01 12:00:00",
            "p75": "2021-03-01 18:00:00", "p90": "2021-03-02 02:00:00",
            "p95": "2021-03-02 06:00:00", "p99": "2021-03-02 09:00:00",
            "max": "2021-03-02 12:00:00",
        },
        n_unparsed=0, utc_offsets={"+02:00": 11, "Z": 13},
    )
    return {
        "why": "the offset allocation of G7.4 with both endpoint offsets "
        "pinned, and the utc clock conversion: a published instant written "
        "on the wall clock of the offset its own cell carries.",
        "column": column,
        "rows": 24,
        "identifier_declared": False,
    }


def _leap_second_endpoint():
    column = _universal(
        "column_1", "datetime", "datetime", "data", "ok",
        n_present=12, n_missing=0, n_distinct=12, n_distinct_folded=12,
        n_numeric=0, n_not_numeric=12, n_out_of_range=0, n_contradictory=0,
        format="iso-datetime", resolution="datetime", time_precision="second",
        subsecond_digits=0, datetimes_read_at="local",
        earliest="2016-12-31 23:00:00", latest="2016-12-31 23:59:60",
        earliest_utc_offset="(none)", latest_utc_offset="(none)",
        date_percentiles={
            "min": "2016-12-31 23:00:00", "p01": "2016-12-31 23:05:00",
            "p05": "2016-12-31 23:10:00", "p10": "2016-12-31 23:15:00",
            "p25": "2016-12-31 23:20:00", "p50": "2016-12-31 23:30:00",
            "p75": "2016-12-31 23:40:00", "p90": "2016-12-31 23:50:00",
            "p95": "2016-12-31 23:55:00", "p99": "2016-12-31 23:58:00",
            "max": "2016-12-31 23:59:60",
        },
        n_unparsed=0, utc_offsets={"(none)": 12},
    )
    return {
        "why": "the endpoint route of G7.5, on the one published end the "
        "ordinal space of G7.1 cannot hold. The latest cell carries a seconds "
        "field of 60, which the profile contract's canonical form admits "
        "because the shipped reader accepts one; the whole-second space has "
        "one place for 23:59:59 and the next for the following midnight and "
        "none for it. So the two ends are built from the published "
        "endpoint's own four fields -- the date with HH:MM and a seconds "
        "field of 00, moved to this cell's clock, then the published seconds "
        "field written back unchanged -- and the space below is left to the "
        "ten interior ranks it is exact for. The clock here is the local one, "
        "which is the only clock the contract's D10 lets this end stand on: "
        "on the shared clock every cell is written on its own offset's wall "
        "clock, so D10 refuses that pair in the description instead. An "
        "implementation that sent these two cells through the ordinal route "
        "writes the following minute for the second of them and every other "
        "byte of this case unchanged, which is exactly the regression this "
        "case is frozen to stop.",
        "column": column,
        "rows": 12,
        "identifier_declared": False,
    }


def _mixed_parsed_unparsed():
    column = _universal(
        "column_1", "datetime", "datetime", "data", "ok",
        n_present=14, n_missing=2, n_distinct=14, n_distinct_folded=14,
        n_numeric=0, n_not_numeric=14, n_out_of_range=0, n_contradictory=0,
        format="iso-date", resolution="date", time_precision="date",
        subsecond_digits=0, datetimes_read_at="local",
        earliest="2019-05-04", latest="2019-08-19",
        earliest_utc_offset="(none)", latest_utc_offset="(none)",
        date_percentiles={
            "min": "2019-05-04", "p01": "2019-05-06", "p05": "2019-05-11",
            "p10": "2019-05-18", "p25": "2019-06-02", "p50": "2019-06-21",
            "p75": "2019-07-10", "p90": "2019-07-28", "p95": "2019-08-05",
            "p99": "2019-08-14", "max": "2019-08-19",
        },
        n_unparsed=3, utc_offsets={"(none)": 11},
    )
    return {
        "why": "counted neutral stand-ins beside parsed cells, and the "
        "absent cells of a one-column table, which the canonical quoting "
        "exception writes as two quote characters rather than as nothing.",
        "column": column,
        "rows": 16,
        "identifier_declared": False,
    }


def _numeric_integer():
    ladder, ladder_claims, rungs = _ladder_fields({
        "min": "-8", "p01": "-7.75", "p05": "-7", "p10": "-6.5",
        "p25": "-3.25", "p50": "2.5", "p75": "2.5", "p90": "16.25",
        "p95": "21.5", "p99": "29.75", "max": "34",
    })
    claims = {
        ("column", "percentiles") + key: value
        for key, value in ladder_claims.items()
    }
    moments = {}
    for name, text in (("mean", "4.25"), ("std", "14.5"), ("skew", "0.5"),
                       ("numeric_share", "1")):
        field, claim = nearest_field(text)
        moments[name] = field
        claims[("column", name)] = claim
    column = _universal(
        "column_1", "continuous", "continuous", "data", "ok",
        n_present=20, n_missing=2, n_distinct=12, n_distinct_folded=12,
        n_numeric=20, n_not_numeric=0, n_out_of_range=0, n_contradictory=0,
        percentiles=ladder, std_unrepresentable=False,
        n_zero=4, n_negative=6, n_negative_unrepresentable=0,
        n_used_in_statistics=20, n_left_out_of_statistics=0,
        integer_valued=True, n_rows=22, numeric_styles={"plain": 20},
        **moments,
    )
    return {
        "why": "the stratified inverse transform with integer_valued true. "
        "The p50 and p75 rungs are the same half-integer, so four interior "
        "strata land on exactly 2.5 and the rounding direction is what "
        "decides their bytes: to nearest, ties toward positive infinity, so "
        "each writes 3 and neither 2 nor a parity-dependent answer. Both "
        "endpoints are pinned and cost no word; the zero stratum costs none "
        "either.",
        "column": column,
        "rows": 22,
        "identifier_declared": False,
        "rungs": rungs,
        "claims": claims,
    }


def _numeric_pooled_spelling():
    """The two branches owner decisions 9 to 11 left without a witness.

    THIS CASE EXISTS BECAUSE A REVIEW FOUND THE ORACLE AND THE SHIPPED
    CODE DISAGREEING WHERE NOTHING LOOKED (review item P3-C4-F2, owner
    decision 11). The pooled-spelling rule changed and no frozen case
    reached it, so both files stayed green while the independent check
    they exist to be was, on that branch, checking nothing. Two branches
    meet in this one column:

    - **a pooled cell with no point-free spelling.** The published
      smallest value carries a decimal point, so the cell that must read
      back as it cannot be written plainly -- and the map's held-back
      remainder used to be owed exactly that. A pooled cell names no
      form, so it is written in its own value's canonical text, and the
      recount identity of contract 7.5.7 is what the twin owes instead.
    - **a whole value wider than the fixed-point window.** The published
      largest value is ten to the twentieth, whole, and published
      `plain` because a source that wrote it wrote its digits. Owner
      decision 10 lifted the sixteen-figure ceiling that used to send it
      back with a decimal point, so it is written in figures here.
    """
    ladder, ladder_claims, rungs = _ladder_fields({
        "min": "0.5", "p01": "4", "p05": "4", "p10": "4",
        "p25": "4", "p50": "4", "p75": "4",
        "p90": "4", "p95": "4", "p99": "4",
        "max": "1e+20",
    })
    claims = {
        ("column", "percentiles") + key: value
        for key, value in ladder_claims.items()
    }
    moments = {}
    for name, text in (("mean", "1e+19"), ("std", "3e+19"),
                       ("skew", "3"), ("numeric_share", "1")):
        field, claim = nearest_field(text)
        moments[name] = field
        claims[("column", name)] = claim
    column = _universal(
        "column_1", "continuous", "continuous", "data", "ok",
        n_present=12, n_missing=0, n_distinct=3, n_distinct_folded=3,
        n_numeric=12, n_not_numeric=0, n_out_of_range=0, n_contradictory=0,
        percentiles=ladder, std_unrepresentable=False,
        n_zero=0, n_negative=0, n_negative_unrepresentable=0,
        n_used_in_statistics=12, n_left_out_of_statistics=0,
        integer_valued=False, n_rows=12,
        numeric_styles={"plain": 11, "(withheld)": 1},
        # THE POOLED SIDE OF THE CENSUS. The one cell that carries a
        # point is the one the floor held back, so no width is named at
        # all and the census carries the pooled remainder alone -- the
        # census's own shape for a column whose decimal cells the floor
        # pooled (contract C6-30's case P5.c). The cell is unsnapped and
        # written at its own value's spelling, which is the pooled
        # remainder's rule of G6.4 unchanged.
        fraction_widths={"(withheld)": 1},
        **moments,
    )
    return {
        "why": "the pooled remainder written by its own value, and a whole "
        "value wider than the fixed-point window written in figures. Eleven "
        "cells are published plain and one is held back below the smallest "
        "group size; the cell that must read back as the published smallest "
        "value carries a decimal point and can wear no point-free form at "
        "all, so the held-back cell is the one that lands there and is "
        "written canonically. The published largest value is whole and wider "
        "than the window the canonical spelling switches at, and is written "
        "in its digits rather than with a point. Neither branch had a frozen "
        "case until owner decision 11 asked for one.",
        "column": column,
        "rows": 12,
        "identifier_declared": False,
        "rungs": rungs,
        "claims": claims,
    }


def _numeric_decimal_styles():
    ladder, ladder_claims, rungs = _ladder_fields({
        "min": "1e-05", "p01": "0.0001", "p05": "0.001", "p10": "0.01",
        "p25": "1", "p50": "5", "p75": "1000000000000000",
        "p90": "1000000000000000", "p95": "1000000000000000",
        "p99": "1000000000000000", "max": "1e+16",
    })
    claims = {
        ("column", "percentiles") + key: value
        for key, value in ladder_claims.items()
    }
    moments = {}
    for name, text in (("mean", "1000000000000"), ("std", "3000000000000"),
                       ("skew", "4.5"), ("numeric_share", "1")):
        field, claim = nearest_field(text)
        moments[name] = field
        claims[("column", name)] = claim
    column = _universal(
        "column_1", "continuous", "continuous", "data", "ok",
        n_present=25, n_missing=0, n_distinct=24, n_distinct_folded=23,
        n_numeric=25, n_not_numeric=0, n_out_of_range=0, n_contradictory=0,
        percentiles=ladder, std_unrepresentable=False,
        n_zero=0, n_negative=0, n_negative_unrepresentable=0,
        n_used_in_statistics=25, n_left_out_of_statistics=0,
        integer_valued=False, n_rows=25,
        numeric_styles={"(withheld)": 3, "exponent_lower": 11,
                        "exponent_upper": 11},
        **moments,
    )
    return {
        "why": "the shortest round-trip digits at both boundaries of the "
        "fixed-point window, and an exact style map on a column whose values "
        "mostly cannot wear a point-free form. The pinned smallest value "
        "writes 1e-05, one place below the window, and the pinned largest "
        "writes 1e+16, one place above it; at those two decimal exponents "
        "the exponent style and the canonical spelling are the same text, "
        "which is itself worth freezing. The published map asks for three "
        "plain cells, and a plain cell carries neither a point nor an "
        "exponent, so only a value the window holds whole can wear one: the "
        "four cells on the flat top of the ladder are this column's only "
        "carriers and they all hold 1000000000000000, whose point-free "
        "spelling is the digits alone and not the canonical "
        "1000000000000000.0. The look-ahead of G6.4 is what keeps the quota "
        "for them, since largest-remaining on its own would have spent every "
        "one of them on an exponent form and left the quota at the end of "
        "the column with nothing to carry it; the two exponent quotas "
        "alternate from the first cell until then. Distinctness is met "
        "inside that map: the base spellings hold twenty-one folded "
        "identities against a published twenty-three, so exactly two cells "
        "raise their leading-zero order, each inside the style G6.4 gave it, "
        "and neither is a plain cell, because plain is the one style with no "
        "such family. The cost is the one G6.5's precedence decides: three "
        "plain cells on a single value are a single raw spelling, so this "
        "column's own supply is twenty-three raw spellings against a "
        "published twenty-four, and G12.8's envelope prints that range.",
        "column": column,
        "rows": 25,
        "identifier_declared": False,
        "rungs": rungs,
        "claims": claims,
    }


def _label_variants():
    column = _universal(
        "column_1", "categorical", "categorical", "data", "ok",
        n_present=48, n_missing=2, n_distinct=13, n_distinct_folded=5,
        n_numeric=0, n_not_numeric=48, n_out_of_range=0, n_contradictory=0,
        levels=[
            {
                "label": "north", "count": 13,
                "variants": {"North": 11}, "variants_withheld": {"1": 2},
            },
            {
                "label": "south", "count": 13,
                "variants": {}, "variants_withheld": {"1": 3, "5": 2},
            },
            {
                "label": "7-11", "count": 12,
                "variants": {}, "variants_withheld": {"4": 3},
            },
        ],
        suppressed_levels=2, suppressed_rows=10,
        suppressed_level_counts=[3, 7], level_ceiling=20,
    )
    return {
        "why": "the variant allocation of G8.1, the case flips of G8.2 with "
        "a candidate skipped because a published variant already spells it, "
        "the trailing-space family a parent with no letters falls straight "
        "through to, and the neutral stand-in labels of G8.3 at their "
        "published sizes. A label column consumes no content word, so every "
        "byte here is fixed by published counts.",
        "column": column,
        "rows": 50,
        "identifier_declared": False,
    }


def _identifier_fold_collisions():
    column = _universal(
        "column_1", "identifier", "code", "identifier", "ok",
        n_present=14, n_missing=0, n_distinct=14, n_distinct_folded=12,
        n_numeric=0, n_not_numeric=14, n_out_of_range=0, n_contradictory=0,
        min_length=2, max_length=4, all_whole_numbers=False,
        n_all_digits=0, n_code_alphabet=14,
        n_distinct_by_occurrences={"1": 14},
    )
    return {
        "why": "two published folded identities fewer than raw spellings, so "
        "two of the invented values must fold onto a partner: the first "
        "identities are drawn from the letter-bearing part of the domain and "
        "each carries one case flip. The length pins of G9.2 are visible in "
        "the first two spellings, which take the shortest and the longest "
        "published length and cost no word.",
        "column": column,
        "rows": 14,
        "identifier_declared": True,
    }


def _identifier_whole_numbers():
    column = _universal(
        "column_1", "identifier", "code", "identifier", "ok",
        n_present=12, n_missing=0, n_distinct=8, n_distinct_folded=8,
        n_numeric=12, n_not_numeric=0, n_out_of_range=0, n_contradictory=0,
        min_length=3, max_length=5, all_whole_numbers=True,
        n_all_digits=4, n_code_alphabet=8,
        n_distinct_by_occurrences={"1": 4, "2": 4},
    )
    return {
        "why": "a declared identifier publishing all_whole_numbers true "
        "across all three alphabet bands, which is the branch review item "
        "P2-C2-F7 found this oracle carrying a withdrawn rule for. Revision "
        "1 said that all_whole_numbers true meant every group was written "
        "from the figures alone; G9.6 withdrew that, and the bands here come "
        "from the two published alphabet counts and from nothing else: four "
        "cells in the figures, four more in the code alphabet, four outside "
        "it. What all_whole_numbers decides is what each band WRITES -- the "
        "figures write digits with a non-zero leading one, the code band "
        "writes <digits>e0, and outside the code alphabet the cell is "
        "written <digits>., whose one character outside that alphabet is the "
        "last rather than the leftmost, because a whole number cannot begin "
        "with it. Both alphabet counts are counts of CELLS answered for by "
        "whole GROUPS, so the four singletons answer for the figures and two "
        "doubled groups answer for each of the other two bands; and the "
        "length pins of G9.2 sit on the first two spellings, which cost no "
        "word.",
        "column": column,
        "rows": 12,
        "identifier_declared": True,
    }


def _numeric_point_free_styles():
    ladder, ladder_claims, rungs = _ladder_fields({key: "5" for key in LADDER_KEYS})
    claims = {
        ("column", "percentiles") + key: value
        for key, value in ladder_claims.items()
    }
    moments = {}
    for name, text in (("mean", "5"), ("std", "0"), ("numeric_share", "1")):
        field, claim = nearest_field(text)
        moments[name] = field
        claims[("column", name)] = claim
    column = _universal(
        "column_1", "count", "count", "data", "ok",
        n_present=33, n_missing=0, n_distinct=3, n_distinct_folded=3,
        n_numeric=33, n_not_numeric=0, n_out_of_range=0, n_contradictory=0,
        percentiles=ladder, std_unrepresentable=False, skew=None,
        n_zero=0, n_negative=0, n_negative_unrepresentable=0,
        n_used_in_statistics=33, n_left_out_of_statistics=0,
        integer_valued=True, n_rows=33,
        numeric_styles={"decimal": 11, "leading_plus": 11, "leading_zero": 11},
        # THE ONE CASE HERE WITH `decimal` CELLS, so the one that
        # publishes a width for them.  Every decimal cell of this column
        # writes the point-free spelling of a whole number with one
        # figure after the point, so the census names ONE width and its
        # cells already fit it -- no cell is snapped and the committed
        # bytes are the bytes this case has always carried.
        fraction_widths={"1": 11},
        **moments,
    )
    return {
        "why": "the three styles no other case places a cell in: the literal "
        "decimal, leading-zero and leading-plus forms of G6.1, each written "
        "from the point-free spelling of G6.2 and each recounted by the "
        "contract's own first-match ladder as the style it was given. The "
        "floor governs a style like any published fact, so a map naming three "
        "of them needs eleven cells each and thirty-three in all. Every rung "
        "of the ladder is the same whole number, which is what keeps the case "
        "small enough to read by hand and makes two further things visible: "
        "the clamp of G5.3 is not decoration, because the four IEEE-754 "
        "operations of the convex form can leave the sum one unit in the last "
        "place away from a value both rungs agree on, and the clamp is what "
        "brings it back; and the tie rule of G6.4 decides every cell here, "
        "since all three quotas stand equal at each step, so the styles are "
        "taken in the enumeration order plain, leading_zero, leading_plus, "
        "decimal and the column cycles through the three it publishes. Three "
        "spellings of one value are three raw identities and three folded "
        "ones, which is what the column publishes, so no cell raises its "
        "leading-zero order.",
        "column": column,
        "rows": 33,
        "identifier_declared": False,
        "rungs": rungs,
        "claims": claims,
    }


def _unrepresentable_joint():
    column = _universal(
        "column_1", "numeric_unrepresentable", "numeric", "data",
        "unrepresentable",
        n_present=6, n_missing=0, n_distinct=4, n_distinct_folded=4,
        n_numeric=2, n_not_numeric=0, n_out_of_range=1, n_contradictory=3,
        n_whole=2, n_fraction=1, n_whole_unknown=3,
        n_positive=0, n_negative=3, n_sign_unknown=3,
        n_distinct_by_occurrences={"1": 2, "2": 2},
    )
    return {
        "why": "the six-row column of G10.5 step 2, whose three published "
        "families have a joint answer that no two of them settle. The "
        "contradictory cells are the only ones that can answer for the three "
        "whole-unknown and the three sign-unknown counts, so they take the "
        "groups of two and one; the remaining three cells are all negative "
        "and divide two whole against one fraction. Sending the one "
        "out-of-range cell to the whole count asks for cell quotas no packing "
        "of groups 2, 2, 1 and 1 meets; sending it to the fraction count -- "
        "equally consistent with every published count, because how "
        "n_out_of_range divides between whole numbers and fractions is not a "
        "published fact -- is met exactly. The walk chooses among every "
        "cross-tabulation the three margins permit, and the recount of step 6 "
        "reads all twelve counts back off the finished cells.",
        "column": column,
        "rows": 6,
        "identifier_declared": False,
    }


def _free_text_joint():
    length, length_claims = {}, {}
    for name, text in (("mean", "1.75"), ("p50", "2")):
        field, claim = nearest_field(text)
        length[name] = field
        length_claims[("column", "length", name)] = claim
    length["min"] = 1
    length["max"] = 2
    words, words_claims = {"min": 1, "max": 1}, {}
    field, claim = nearest_field("1")
    words["mean"] = field
    words_claims[("column", "words", "mean")] = claim
    column = _universal(
        "column_1", "free_text", "text", "data", "ok",
        n_present=4, n_missing=0, n_distinct=3, n_distinct_folded=3,
        n_numeric=2, n_not_numeric=2, n_out_of_range=0, n_contradictory=0,
        length=length, words=words,
        n_all_digits=2, n_code_alphabet=3,
        n_distinct_by_occurrences={"1": 2, "2": 1},
    )
    return {
        "why": "the joint class-and-alphabet packing of G9.5 steps 3 and 4 on "
        "a column where two separate walks cannot both land. The class counts "
        "alone permit the doubled group to answer for either class; the "
        "alphabet counts alone permit either split of the singletons. A walk "
        "that settled the classes first would take the two singletons for the "
        "two numeric cells -- the smallest sizes for the count that is "
        "reached first -- and leave the doubled group owing one "
        "code-alphabet cell and one wide cell, which one group covering two "
        "cells cannot do. The joint packing gives the doubled group the "
        "figures and the two singletons the other two bands, which meets "
        "every quota of both margins exactly. The permissions are the rule's "
        "own: a cell of ordinary text cannot be written in figures alone "
        "because figures alone read as a number, and a cell whose leftmost "
        "character is a non-digit of the code alphabet is not a number at "
        "all.",
        "column": column,
        "rows": 4,
        "identifier_declared": False,
        "claims": {**length_claims, **words_claims},
    }


def _identifier_edge_spacing():
    column = _universal(
        "column_1", "identifier", "code", "identifier", "ok",
        n_present=4, n_missing=0, n_distinct=4, n_distinct_folded=1,
        n_numeric=4, n_not_numeric=0, n_out_of_range=0, n_contradictory=0,
        min_length=1, max_length=3, all_whole_numbers=True,
        n_all_digits=4, n_code_alphabet=4,
        n_distinct_by_occurrences={"1": 4},
    )
    return {
        "why": "a fold collision no case change can build. The column is "
        "written in figures alone, so its one identity holds no character "
        "with a case and the case-flip half of G9.3's partner family is empty "
        "from the start; the three partners the published counts ask for can "
        "come only from the edge spacing, which the fold trims away. The "
        "family's order is visible in all three: the total number of spaces "
        "ascends, and within one total the leading share ascends, so the "
        "spaces go to the end first and are then moved leftward one at a "
        "time. The second slot carries the longest published length, which a "
        "partner may hold only because spacing lengthens -- the whole point "
        "of the second slot being open to a partner when the column comes "
        "down to one identity. WHICH member each slot takes is G9.3 step 2's "
        "own rule since review item P2-C4-F4: every slot walks the family "
        "from that family's own start and takes the first member the column "
        "has not written whose length its own window admits, so the slot "
        "pinned to the longest length takes the first two-space placement "
        "and the two open slots after it take the two one-space placements "
        "in the family's order. A walk that began at an ordinal of the "
        "slot's own would step over a member nothing has written and no "
        "window has turned down, which is how two implementations came to "
        "write different bytes for this column. Every other published fact "
        "survives the "
        "spacing: the alphabet counts and the whole-number fact are read "
        "after trimming, the writer quotes a field for a comma, a quote "
        "character or a line ending and for nothing else, and the reader "
        "gives the spaces back unchanged.",
        "column": column,
        "rows": 4,
        "identifier_declared": True,
    }


# The nine cases method section G14.3 names, which are the first
# committed file, and the five it adds for the branches those nine leave
# unexercised (review items P2-C3-F3 and P2-C4-C3), which are the
# second. The two sets are one oracle: the same transform, the same
# proof layer, the same words-as-inputs rule. They are two FILES because
# a committed fixture must stay under the manifest's 100000-byte cap,
# and the nine already spend most of it.
NAMED_PART = "named"
BRANCH_PART = "branches"

NAMED_CASE_BUILDERS = {
    "date_only": _date_only,
    "identifier_fold_collisions": _identifier_fold_collisions,
    "identifier_whole_numbers": _identifier_whole_numbers,
    "label_variants": _label_variants,
    "mixed_parsed_unparsed": _mixed_parsed_unparsed,
    "numeric_decimal_styles": _numeric_decimal_styles,
    "numeric_integer": _numeric_integer,
    "offset_bearing": _offset_bearing,
    "quarter": _quarter,
}

BRANCH_CASE_BUILDERS = {
    "free_text_joint": _free_text_joint,
    "numeric_pooled_spelling": _numeric_pooled_spelling,
    "identifier_edge_spacing": _identifier_edge_spacing,
    "leap_second_endpoint": _leap_second_endpoint,
    "month_span": _month_span,
    "numeric_point_free_styles": _numeric_point_free_styles,
    "unrepresentable_joint": _unrepresentable_joint,
}

CASE_SETS = {
    NAMED_PART: NAMED_CASE_BUILDERS,
    BRANCH_PART: BRANCH_CASE_BUILDERS,
}

CASE_BUILDERS = {**NAMED_CASE_BUILDERS, **BRANCH_CASE_BUILDERS}

# What each file says about itself, so that neither can be read as the
# whole of the oracle and neither hides the other.
CASE_SET_ACCOUNTS = {
    NAMED_PART: "The nine cases method section G14.3 names, committed as "
    "tests/reference/generation-reference-vectors.json. The seven cases that "
    "reach the branches these nine leave unexercised (review items P2-C3-F3 "
    "and P2-C4-C3, owner decision 11, and the month resolution of plan "
    "P4-D4.3) are the same oracle's second file, "
    "tests/reference/generation-branch-vectors.json: one transform, one proof "
    "layer, two files, because a committed fixture must stay under the "
    "provenance manifest's byte cap and these nine already spend most of it.",
    BRANCH_PART: "The seven cases method section G14.3 adds for the branches "
    "its first nine leave unexercised (review items P2-C3-F3 and P2-C4-C3, "
    "owner decision 11, and plan P4-D4.3): "
    "the joint class-and-sign packing of an unrepresentable column, the joint "
    "class-and-alphabet packing of free text, a fold collision no case change "
    "can build, the literal decimal, leading-zero and leading-plus style "
    "placements, the published end whose seconds field is 60, which the "
    "ordinal space cannot hold and the endpoint-fields route writes exactly, "
    "the pooled remainder written by its own value beside a whole number "
    "wider than the fixed-point window, and the month, which is the second "
    "resolution naming a SPAN rather than an instant. "
    "They are computed by the same oracle and the same proof "
    "layer as tests/reference/generation-reference-vectors.json, and live in "
    "their own file only because a committed fixture must stay under the "
    "provenance manifest's byte cap.",
}

# The chain of interior values a case publishes lives under the key the
# method names for it, which is the same word the value wrapper uses; the
# walk is told about each of these paths so it descends rather than
# treating the section as a value.
SECTION_FIELDS = frozenset(("cases", name, FLOAT64) for name in CASE_BUILDERS)

# The words each case is GIVEN, in consumption order.  They are inputs:
# nothing here draws them, and this file holds no generator and no seed.
# The stream a seed produces is bound by the golden twin hash CI computes
# against the locked numpy, not by this file (method section G14.4).
GIVEN_WORDS = {
    "date_only": (
        17405102656223811442, 6630147816760228827, 14477104582272359118,
        10907157359294391350, 5429403641982895397, 17021284587681472559,
        16036336519888171172, 6717168357184625225, 17951943638000877096,
        4141742867391886884, 14858776128100620215, 12560318519191079629,
        8689532878278713804, 568260631324672868, 16506113449883541490,
        10581652359165407223, 7199916538783650088, 6542673427813023417,
        12026779432949751174, 6401544535132643203, 9363196662584741243,
    ),
    "identifier_fold_collisions": (
        15790298876938276606, 11663417973422657062, 2174973634102678219,
        6468031425780904311, 4429227251541079064, 1398918272586881189,
        8789375813863383005, 16487705707051843465, 8139873547394760287,
        11404387512573117166, 9826873545502997855, 10233833751414870731,
        7563852239047881160,
    ),
    "identifier_whole_numbers": (
        10030274107849547999, 15521253635765011071, 13836461403225338975,
        6117593865009646518, 11054268929625209901, 3587914545536121365,
        2793628182718251330, 9295060879584016278, 10009843322027634450,
        18435849063748089958, 18148993397754231745,
    ),
    "label_variants": (
        11963376127784481471, 8811798785216892889, 9273867820551118783,
        13554370282884725440, 9060547780293923212, 1411783948479155249,
        7666529744640113064, 18254477183346180252, 3084421031199700831,
        15063200609615600966, 4230815638602937026, 4076406646768261274,
        765929995082621236, 1978656067210153435, 13158816643724607965,
        18028253954223023117, 5164776794570387654, 5807853018807556082,
        1855828987004747402, 16976035838679037573, 5337167761819413389,
        17094048286831685378, 9674771367788047423, 4457276250860306191,
        13320454777781917740, 16357963768041601936, 16285172591989972951,
        2013287018539706433, 5377445686737864308, 10629050919875048420,
        2365084283309719593, 8321559233565288351, 2689868915047693894,
        1022557403213150778, 6239415321289908665, 10962266920683331171,
        18387766627622840498, 8008958887467463717, 3352561267809570791,
        2527308457471687039, 12159246088705695820, 3355888160917775940,
        5286037579214665404, 8551260477731462453, 8122623374493414700,
        6433478580196713009, 4534578588385673979, 12350521707959121959,
        9283696747916472363,
    ),
    "mixed_parsed_unparsed": (
        15468790482999093277, 12767879758820553273, 3986135311488018723,
        2313441185114737656, 6918807186959069744, 13906788553970883755,
        13561824172940846821, 7616466615151289132, 11896883917442988457,
        15203904226939018011, 1222699267172346040, 9929831366226458468,
        13943388631391938479, 15224560754684281973, 4041919053268054581,
        8926944878616040259, 6753681669668235960, 4894827040233008342,
        14726592479066544356, 10333078532235126804, 10370370648584336126,
        4904921341357146097, 12874998094852978492, 1115272402486917155,
    ),
    "numeric_decimal_styles": (
        18122226285733997623, 745251280968031284, 2265014642969230085,
        8564186180574590976, 17790820182404252692, 2560395418245524351,
        6006355448536362631, 3536383705070940149, 5933272102958222522,
        1019141037504069393, 11730558448425329608, 1265090817159327158,
        17987427395615227841, 2790094521200593362, 5445314763428947640,
        955394625722831381, 13153659650187502672, 7365485450781542734,
        9567025444509976164, 12744960014427948290, 806937940243059194,
        4804218408820866901, 7727943645550869855, 1714489202306818105,
        1520229949718584579, 83083277045611386, 12865410532545056808,
        7854065325545113299, 16337924459546691455, 2599083258829215049,
        7212223952302396495, 18081592058026531404, 3610000432696877458,
        5971099600468076975, 18329783686676331769, 16396278361322735980,
        16318951378032944714, 4589929018872600007, 16664587370514787775,
        4977703725571114289, 9946834984199833014, 12604538961719754543,
        14043947692871599059, 2864893112624124495, 15982129525091029551,
    ),
    "numeric_integer": (
        11772625987983383310, 18289204737680302691, 1784343509013158634,
        9347045313664117555, 7313007878855836523, 3800328781381396623,
        16295278607414762533, 9970149361428565735, 11293179004703751843,
        5263992174777769659, 10257478491244533986, 13533929204537971183,
        3668598122693968034, 4884033769700471139, 6003686507303868290,
        9487660973591609688, 8409348134138937769, 9120532227540731730,
        11095733292861077991, 14510376374364777935, 13560177484143940994,
        11173923279816319277, 14794590252439445687, 7011644228590637169,
        6486586343555636615, 4048370230160771086, 13353600119125463639,
        6954318356567724678, 6952775705301372451, 11786355788230889783,
    ),
    "offset_bearing": (
        5767987570180376785, 4137940843852105099, 3357486873081111151,
        15867495332932156262, 15818866815484724309, 1910389707909542319,
        5332766239925695447, 12203844558430543301, 12936623471645322750,
        8092217747800504980, 8880384414625044392, 13650279682525226351,
        8097458334581197121, 17706528596577841216, 5708511762091391385,
        2062486542870504659, 4671442185228173103, 1030638457095904017,
        17010039991443910733, 11968978306597155092, 3621312926436956588,
        678001638936691630, 15621394269280345601, 6844949931885213773,
        3861112309963881180, 7500036688811799097, 3004537903871046789,
        1319293843099693824, 402133304777179008, 157650257388527877,
        11402520411093986989, 6085542217269792998, 4734660979387692243,
        8473303461638027804, 11630077187634147208, 4458374147249290524,
        2369030762614924813, 12369823957925092664, 5166522099601314915,
        15616721581626287654, 9429884691979953109, 18127486393963791964,
        3344364491090853863, 2323706709912995473, 2923796674797395481,
    ),
    "free_text_joint": (
        2148289608029031280, 15571884919775399509, 14732924256990173560,
    ),
    "identifier_edge_spacing": (
        1301936263764534004, 2783040907285617897, 2670401546021029124,
    ),
    "leap_second_endpoint": (
        13427168714134208824, 2622372851408911490, 7994527897440520627,
        12988577211988740715, 11221240180743911529, 11903615472945588819,
        8022945971884194589, 9470686378554496101, 16464846541937923496,
        2015723726740522778, 2953194388775208825, 186460714444600446,
        10286796248990847147, 3073121396252394582, 5850044163583767416,
        18384416552906420653, 15259945026574340491, 1508198782665164068,
        17439788078174870154, 7339215063107649377, 9204310222248724882,
    ),
    # The twelve words of the pooled-spelling case (owner decision
    # 11): one content word and eleven placement words, drawn in
    # the one form G3.2 permits so the shipped generator reaches
    # the same cells from the same stream.
    "numeric_pooled_spelling": (
        12955849785445258386, 11136466736298123742, 10038147400135452611,
        15147492697428057229, 14236867650031288, 2173290989802069806,
        11540999283663690755, 7558342730909420832, 4008536478337168684,
        7977734629748327352, 2774262970987807365, 3332551472928899385,
    ),
    "numeric_point_free_styles": (
        17164562756356967436, 9452808604124318311, 13143735524693854369,
        9264394462213188003, 4424453555071538545, 16165890503801172771,
        1269149005679939117, 12961166868588685495, 1805945305664177376,
        8221329215693956576, 9678221350114918390, 4883968381507460964,
        1186568609038911133, 11742150723573194681, 9039212224933945618,
        11807987216793257899, 8078543970593484256, 13148862654883819303,
        12952826994547832336, 7089260808419439423, 15347290669249134533,
        15555194800501135327, 8642828883554635416, 15125560542937574112,
        7032404254710712784, 11529033739087927467, 10460607393191814099,
        14397204600971004711, 13236913917897978945, 17589778316560365163,
        6002837667684665038, 4039038238430453467, 936435099686866448,
    ),
    "unrepresentable_joint": (
        2834551707271871843, 3123094663624302558, 9333394219979397357,
        12140150428679393766, 14159367994340888644,
    ),
    "month_span": (
        3179660957074219929, 16176357821278490312, 17656820539994292342,
        17540219834124380146, 9365132703411629466, 11037237009629682836,
        5537033287795020884, 10091697982931758559, 5772994017682272647,
        9256936461562489083, 5846245697595079916, 3288170915282709302,
        17570781254895321736, 17342232991728644533, 424412772268271036,
        5101176902256472994, 17483310722792023123, 11776508763375653527,
        11238713790439917190, 2349096050734119258, 14187853255911556467,
    ),
    "quarter": (
        2951315705954145492, 10808750059907510011, 15197106187201647244,
        5483483510807493621, 12634166190170755924, 8557152385012124240,
        16442642387055436547, 10420072498744423129, 18321158485267126211,
        4473733150874107093, 2016160144537938125, 6374270959940166065,
        14373970446143769944, 9954831754992850354, 17049503755859162412,
        18342807586139153977, 17012409700022442331, 2994083137851607544,
        10884890814974754874, 13385752094565004958, 16951936404647227201,
    ),
}


def word_budget(column, rows):
    """The draw budget of method section G4.3, as a function of the facts."""
    role = column["role"]
    placement = max(rows - 1, 0)
    if role == "datetime":
        parsed = column["n_present"] - column["n_unparsed"]
        return max(parsed - 2, 0), placement
    if role in ("count", "continuous"):
        numeric = column["n_numeric"]
        negatives = column["n_negative"] - column["n_negative_unrepresentable"]
        zeros = column["n_zero"]
        positives = numeric - negatives - zeros
        values = min(
            numeric, numbers_class_budget(column, column["n_distinct_folded"])
        )
        # G5.2's carrier step moves cells between strata of one band and
        # changes neither how many strata there are nor which band each
        # is in, so the budget is a function of the even split alone.
        sizes, _starts, bands = stratum_layout(
            numeric, negatives, zeros, positives, values
        )
        strata = len(sizes)
        pinned = 2 if strata >= 2 else (1 if strata == 1 else 0)
        zeroed = 0
        if zeros > 0:
            index = bands.index("zero")
            if index != 0 and not (index == strata - 1 and strata >= 2):
                zeroed = 1
        return strata - pinned - zeroed, placement
    return 0, placement


# Leaf keys of a column block whose value is a whole number, and the
# objects and arrays whose members are.  A number at any other place in
# a column block stops the run: the point of naming them is that a field
# added later cannot arrive as an unproved number without being noticed.
INTEGER_COLUMN_KEYS = frozenset({
    "position", "n_present", "n_missing", "n_missing_blank",
    "n_missing_withheld", "n_distinct", "n_distinct_folded",
    "n_numeric", "n_not_numeric", "n_out_of_range", "n_contradictory",
    "n_sentinel_candidates_unpublished", "n_zero", "n_negative",
    "n_negative_unrepresentable", "n_used_in_statistics",
    "n_left_out_of_statistics", "n_rows", "suppressed_levels",
    "suppressed_rows", "level_ceiling", "subsecond_digits", "n_unparsed",
    "min_length", "max_length", "n_all_digits", "n_code_alphabet", "count",
    "n_occurrences", "n_whole", "n_fraction", "n_whole_unknown",
    "n_positive", "n_sign_unknown",
})
INTEGER_COLUMN_MAPS = frozenset({
    "missing_by_class", "missing_by_source", "numeric_styles", "utc_offsets",
    "variants", "variants_withheld", "n_distinct_by_occurrences",
    "fraction_widths", "resolution_mix",
})
INTEGER_COLUMN_ARRAYS = frozenset({"suppressed_level_counts"})
# The two blocks of a free-text column whose own two ends are whole
# numbers while the statistics beside them are proved binary64 values.
INTEGER_COLUMN_ENDS = frozenset({"length", "words"})


def whole_number_fields(document):
    """Exactly the paths in ``document`` that may carry a whole number.

    Built by walking the finished document and holding every whole
    number it finds up to the rule above: a count under one of the named
    leaf keys, a value inside one of the named maps, a member of one of
    the named arrays, a word budget, the stratum and segment a chain
    record names, or the method revision.  Anything else stops the run
    here rather than reaching the proof layer as a number nobody
    accounted for.
    """
    allowed = set()
    for path, value in _published_numbers(document, (), SECTION_FIELDS):
        if path and path[-1] == FLOAT64:
            continue
        if not isinstance(value, int) or isinstance(value, bool):
            continue
        if path == ("method_revision",):
            allowed.add(path)
            continue
        if len(path) >= 4 and path[0] == "cases" and path[2] == "word_budget":
            allowed.add(path)
            continue
        if (
            len(path) == 5
            and path[0] == "cases"
            and path[2] == FLOAT64
            and path[4] in ("stratum", "segment")
        ):
            allowed.add(path)
            continue
        if len(path) >= 4 and path[0] == "cases" and path[2] == "column":
            inside = path[3:]
            if len(inside) == 1 and inside[0] in INTEGER_COLUMN_KEYS:
                allowed.add(path)
                continue
            if len(inside) == 2 and inside[0] in INTEGER_COLUMN_MAPS:
                allowed.add(path)
                continue
            if len(inside) == 2 and inside[0] in INTEGER_COLUMN_ARRAYS:
                allowed.add(path)
                continue
            if (
                len(inside) == 2
                and inside[0] in INTEGER_COLUMN_ENDS
                and inside[1] in ("min", "max")
            ):
                allowed.add(path)
                continue
            if (
                len(inside) >= 3
                and inside[0] == "levels"
                and (
                    inside[2] in INTEGER_COLUMN_KEYS
                    or (len(inside) == 4 and inside[2] in INTEGER_COLUMN_MAPS)
                )
            ):
                allowed.add(path)
                continue
            if (
                len(inside) == 3
                and inside[0] == "sentinel_verdicts"
                and inside[2] in INTEGER_COLUMN_KEYS
            ):
                allowed.add(path)
                continue
        raise AssertionError(
            f"{_where(path)} publishes the whole number {value!r} at a place "
            "this document has no rule for. Name the field among the "
            "whole-number keys of this generator, or publish it as a "
            "'float64' field with the exact value it stands for beside it."
        )
    return frozenset(allowed)


# --------------------------------------------------------- assembling it


def build_case(name):
    """One finished case, and the exact value recorded for every number in it.

    Nothing is written here.  The document and the record of exact
    values go together to ``prove_every_published_float``, which is what
    makes the file's claim true, and separating them is what lets a test
    hold the committed bytes up to the same records the writer uses.
    """
    spec = CASE_BUILDERS[name]()
    column = spec["column"]
    rows = spec["rows"]
    words = list(GIVEN_WORDS[name])
    content_words, placement_words = word_budget(column, rows)
    if len(words) != content_words + placement_words:
        raise AssertionError(
            f"{name} is given {len(words)} words and the draw budget of "
            f"G4.3 asks for {content_words} content words and "
            f"{placement_words} placement words"
        )
    working = dict(column)
    working["_content_words"] = words[:content_words]
    working["_rungs"] = spec.get("rungs")
    chain = []
    if column["role"] == "datetime":
        content = _datetime_content(working)
    elif column["role"] in ("count", "continuous"):
        content, chain, _missed = _numeric_content(working)
    elif column["role"] == "identifier":
        content = _identifier_content(working)
    elif column["role"] == "free_text":
        content = _free_text_content(working)
    elif column["role"] == "numeric_unrepresentable":
        content = _unrepresentable_content(working)
    else:
        content = _label_content(working)
    if len(content) != column["n_present"]:
        raise AssertionError(
            f"{name} built {len(content)} present cells and the column "
            f"publishes {column['n_present']}"
        )
    cells = place(content, column["n_missing"], rows, words[content_words:])
    one_column = True
    csv_bytes = "".join(
        csv_field(cell, one_column, cell == "") + "\n" for cell in cells
    )
    claims = dict(spec.get("claims", {}))
    published_chain = []
    for index, record in enumerate(chain):
        entry = {"stratum": record["stratum"], "segment": record["segment"]}
        for key, exact_key, shape in (
            ("t", "t_exact", EXACT),
            ("u", "u_exact", EXACT),
            ("x1", "x1_exact", NEAREST),
            ("x2", "x2_exact", NEAREST),
            ("interpolated", "interpolated_exact", NEAREST),
        ):
            if shape == EXACT:
                field, claim = exact_field(record[key])
                if F(record[key]) != record[exact_key]:
                    raise AssertionError(
                        f"{name} stratum {record['stratum']} claims {key} is "
                        f"exactly {record[exact_key]} and it is not"
                    )
            else:
                field, claim = nearest_result_field(record[exact_key], record[key])
            entry[key] = field
            claims[(FLOAT64, index, key)] = claim
        field, claim = exact_field(record["value"])
        entry["value"] = field
        entry["repaired_onto_a_sign_fallback"] = record["repaired"]
        claims[(FLOAT64, index, "value")] = claim
        published_chain.append(entry)
    case = {
        "why": spec["why"],
        "column": column,
        "words": [str(word) for word in words],
        "word_budget": {"content": content_words, "placement": placement_words},
        "content": content,
        "cells": cells,
        "csv_bytes": csv_bytes,
        FLOAT64: published_chain,
    }
    return case, {("cases", name) + key: value for key, value in claims.items()}


DEFINITIONS = {
    "bounded": "bounded(w, m) = (w * m) >> 64, the whole part of "
    "(w / 2**64) * m and a value in 0..m-1. One word every call, so a "
    "run's word count is a fixed function of the published facts (G3.4b).",
    "permutation": "a = [0..n-1]; for i from n-1 down to 1, j = "
    "bounded(next word, i+1) and a[i] and a[j] are swapped, the swap "
    "happening even when j == i. Consumes max(n-1, 0) words (G3.4c).",
    "stratum_layout": "negatives ascending, then the zero stratum, then "
    "positives ascending. M = min(K, F_num) different values; M_neg is the "
    "nearest whole number to M_rest*G/(G+P) with ties upward, computed as "
    "(2*M_rest*G + (G+P)) // (2*(G+P)) and clamped into [1, M_rest-1]; each "
    "band is divided by the even split floor((i+1)*n/m) - floor(i*n/m) "
    "(G5.2).",
    "ladder_segment": "the unique j in 0..9 with PCT[j]*D <= 100*N < "
    "PCT[j+1]*D, scanned upward from zero and stopped at the first that "
    "holds. PCT is (0,1,5,10,25,50,75,90,95,99,100) held as whole numbers "
    "(G5.1, G5.3, G7.3).",
    "convex_interpolation": "T = (A << 53) // B and t = ldexp(T, -53); then "
    "u = 1 - t, x1 = u * L[j], x2 = t * L[j+1], v = x1 + x2 -- four IEEE-754 "
    "binary64 operations in that order and no others -- then the clamp, "
    "v = L[j] when below and v = L[j+1] when above. The difference form "
    "L[j] + t*(L[j+1]-L[j]) is not used: it overflows to an infinity when "
    "the rungs sit at opposite ends of the range and loses the "
    "interpolation between neighbouring subnormals (G5.3).",
    "integer_rule": "b = int(v) truncated toward zero; r = v - float(b); to "
    "nearest with ties toward POSITIVE INFINITY -- r > 0.5 or r == 0.5 "
    "gives b+1, r < -0.5 gives b-1, r == -0.5 gives b. Not banker's "
    "rounding and not toward zero. Applied by the published "
    "integer_valued fact and never by the role name, and never to a pinned "
    "stratum (G5.4).",
    "class_repair": "a stratum in the negative band whose value is at or "
    "above zero takes max(min, -1); a stratum in the positive band whose "
    "value is at or below zero takes min(max, 1); the zero stratum needs "
    "none. Where the ladder and the sign counts disagree, the counts win "
    "(G5.5).",
    "canonical_spelling": "a whole-number column writes the base-ten digits "
    "of the value, 0 never -0. Otherwise the shortest digit string that "
    "reads back as exactly the value (shortest first, then nearest, ties to "
    "the even significand), in fixed-point notation when -4 < decpt <= 16 "
    "with .0 appended where no fractional digit would otherwise be written, "
    "and in d[.ddd]e+/-XX otherwise with the sign always written and the "
    "exponent at least two digits. Beside it, and not always the same text, "
    "the POINT-FREE spelling the three styles carrying neither a point nor "
    "an exponent are written from: where decpt >= len(D) -- that is, where "
    "the value is whole, at any width -- it is the sign, D and "
    "decpt - len(D) trailing zeros, and where it is not whole the value has "
    "no point-free spelling at all (G6.2, as owner decision 10 amended it; "
    "the -4 < decpt <= 16 window this sentence used to carry belongs to the "
    "canonical spelling above and not to this one).",
    "style_allocation": "the VALUES step first: W is the point-free quota of "
    "the effective map, and while fewer cells than that hold a value with a "
    "point-free spelling the strata are walked in ascending order and the "
    "fewest the shortfall needs are taken to the nearest whole number, never "
    "the two pinned ends, never one that would cross zero and never one "
    "whose rounded value is already another stratum's. Then "
    "largest-remaining-quota over the numeric cells in stratum order and, "
    "inside a stratum, in ascending cell index, with ties going to the "
    "enumeration order plain, leading_zero, leading_plus, decimal, "
    "exponent_lower, exponent_upper and the withheld remainder added to "
    "plain. A style is offered to a cell only where the finished text would "
    "classify back as that style: leading_plus needs a value that is not "
    "negative, and plain, leading_zero and leading_plus need a value with a "
    "point-free spelling. The look-ahead is part of the rule: a choice is "
    "admissible only where it leaves the point-free quotas inside the count "
    "of cells after it that can carry them. Zeros are then spent over the "
    "WHOLE column at once -- the shortfall of the base spellings' identities "
    "against the folded budget is how many cells raise their order, each "
    "taking the lowest order whose folded identity is new, inside whatever "
    "style it was given, since every style but plain carries the family "
    "(G6.3, G6.4, G6.5).",
    "ordinal_transform": "N_r = r * 2**64 + w over D = P * 2**64; the "
    "segment is located as above and ordinal = Lo[j] + (A * (Lo[j+1] - "
    "Lo[j])) // B. The floor division rounds toward the EARLIER instant "
    "always, before the epoch included, which is why it floors toward "
    "negative infinity rather than truncating toward zero (G7.3).",
    "precision_form": "quarter writes YYYY-Qn, date writes YYYY-MM-DD, and "
    "datetime writes YYYY-MM-DDTHH:MM, ...:SS or ...:SS.ddd by the "
    "published time_precision, with T as the separator and the fractional "
    "digits all zeros because the profile publishes how many digits the "
    "finest cell carried and nothing about their values (G7.5).",
    "endpoint_fields": "the two endpoint cells are built from the published "
    "endpoint's OWN four fields and never from an ordinal: take the date "
    "with HH:MM and a seconds field of 00, move THAT to the clock this cell "
    "is allocated -- unchanged on the local clock, shifted by "
    "offset_in_seconds on the shared one -- cut the result to the recorded "
    "time_precision, and write the published seconds field back unchanged. "
    "Every offset is a whole number of minutes, so the move never touches "
    "the seconds field and a seconds field of 60 survives it; for every "
    "other seconds field this produces the bytes the ordinal route produces "
    "(G7.5).",
    "grid_packing": "the published families of counts over one set of cells "
    "are MARGINS of one packing, never one walk after another: every group "
    "takes one cell of the grid out of the set its own facts permit, and "
    "every quota of every margin is met exactly whenever such an assignment "
    "exists. Each margin ranks its counts in ascending order of their "
    "published values, ties by the contract's own order; a cell carries one "
    "rank per margin and the cells are filled in ascending order of those "
    "ranks read margin by margin. Within a cell the group SIZES are offered "
    "in ascending order and each size offers as many copies as the cell can "
    "still hold, falling back to fewer; a fill that leaves a later cell "
    "unable to finish is undone and the next is tried; groups are handed to "
    "their cells in group order. A cell that is the last which can answer for "
    "one of its counts takes what that count still owes rather than choosing. "
    "Nothing counts the work and nothing stops the walk early (G9.5, G9.6, "
    "G10.5).",
    "partner_family": "a fold-collision partner is a case flip, edge spacing, "
    "or both, because the shipped fold trims before it turns the case over. "
    "One parent's partners are enumerated by ascending TOTAL number of "
    "spaces, and within one total the LEADING share ascends, so the spaces go "
    "to the end first and are then moved leftward one at a time; within one "
    "placement the case flips are taken in ascending binary-counter order "
    "with bit 0 the leftmost alphabetic position and k = 0 the placement's "
    "own case; the parent itself is stepped over. The case flips of the "
    "unspaced parent are therefore the first 2**L - 1 partners. A partner may "
    "take only a length its own slot may take (G9.3).",
    "notation_reading": "what one finished cell's notation settles, asked of "
    "every cell by the recounts: a sign inside accounting parentheses is the "
    "contradictory class and settles neither the sign nor the whole-number "
    "status, ordinary text settles neither either, and a well-formed number "
    "is out of range exactly when its magnitude reaches the point where "
    "binary64 rounds to an infinity or falls to or below half the smallest "
    "subnormal -- so a 400-digit whole number is out of range and whole, and "
    "a fraction below that point is out of range and a fraction (G10.2, "
    "G10.5).",
    "offset_form": "rank 0 takes earliest_utc_offset and rank P-1 takes "
    "latest_utc_offset where each names a real offset; the rest are spent "
    "over the remaining ranks in ascending rank, taking the keys in the "
    "profile's own sorted order with (none) and (withheld) last. A cell "
    "allocated either of those is written with no offset. Under the utc "
    "clock a datetime cell is written on its own offset's wall clock, "
    "local_ordinal = ordinal + offset_in_seconds (G7.4).",
    FLOAT64: "the binary64 value published for the exact rational recorded "
    "beside it. 'proof' says which claim is being made: 'nearest' means the "
    "value is the correctly rounded (round-half-even) binary64 of that "
    "rational, and 'exact' means it IS that rational with nothing rounded "
    "away. Both are re-derived from the value's two binary64 neighbours in "
    "a separate pass over the finished document.",
}


def build_document(part=None):
    """One whole file, and the exact value recorded for every number in it.

    ``part`` names which set of cases this file carries: the nine
    method section G14.3 names, or the four it adds for the branches
    those nine leave unexercised.  The two sets share this one oracle
    and are two files only because a committed fixture must stay under
    the manifest's byte cap.
    """
    if part is None:
        part = NAMED_PART
    if part not in CASE_SETS:
        raise AssertionError(
            f"{part!r} is not one of the case sets this oracle writes: "
            f"{', '.join(sorted(CASE_SETS))}"
        )
    builders = CASE_SETS[part]
    document = {
        "what": "Independent reference vectors for synthtwin's generation "
        "transform: the twin cells a conforming generator must write, "
        "computed from the method specification alone.",
        "generated_by": "tools/reference/make_generation_reference_vectors.py",
        "case_set": CASE_SET_ACCOUNTS[part],
        "never_imports": ["synthtwin", "numpy", "pandas"],
        "method": "docs/spec/generation-method-v1.md",
        "method_revision": 1,
        "word_source": "The words below are INPUTS. This oracle draws none "
        "of them: it holds no generator, no seed handling and no library "
        "random operation of any kind, because the data-provenance guard "
        "refuses an import of ctypes and numpy imports ctypes. What these "
        "vectors freeze is the transform from words to bytes; the word "
        "stream a seed produces is bound separately, by the golden twin "
        "hash computed in CI against the locked numpy.",
        "column_shape": "Each case's 'column' is one column block in the "
        "profile's own wire shape, with one departure stated rather than "
        "left to be discovered: every published binary64 in it is written "
        "inside a 'float64' wrapper carrying the exact decimal it was read "
        "from, that decimal as an exact rational, and the proof shape. The "
        "wire value is the wrapper's 'float64' field. Writing those numbers "
        "bare would put a number in this file that nothing proved.",
        "readings_taken": "Seven places where the method fixes the parts but "
        "not their order are read here as follows, so a reader knows which "
        "reading these vectors freeze. (1) A datetime column's content list "
        "holds the parsed cells first, in ascending rank, and the counted "
        "stand-ins after. (2) An identifier column's spellings are laid into "
        "the groups as the identities in enumeration order followed by the "
        "partners in ascending identity order. (3) G9.5 fills the "
        "packing grid's margins in ascending order of their own published "
        "counts, ties by the contract's own order; for the three alphabet "
        "bands of a declared identifier that order is read as the figures "
        "first, then the code alphabet, then the rest, which is the order "
        "G9.5 step 4 itself names them in. (4) G9.6 fixes a non-zero leading "
        "digit for the figures band of a whole-number identifier, and gives "
        "the other two bands the templates <digits>e0 and <digits>. ; the "
        "digit block of those two templates is read as the ordinary figures "
        "enumeration of G9.2, with the non-zero rule applied where G9.6 "
        "states it and nowhere else. (5) A grid of more than two margins is "
        "read margin by margin in the order the section that publishes them "
        "names: the notation counts, then the whole-number counts, then the "
        "sign counts for an unrepresentable column (G10.5 step 3), and the "
        "class counts before the alphabet counts for free text (G9.5 steps 3 "
        "and 4). (6) Free text publishes no "
        "middle rung for its word counts, so the groups that are not pinned "
        "start at the whole number nearest words.mean, which is where "
        "length.p50 stands for the lengths. (7) The content list of a free-"
        "text or unrepresentable column is built group by group in group "
        "order, the order the multiplicity map itself states. What was "
        "reading (6) here is no longer a reading: which member of a fold-"
        "collision family a slot takes was worked out two ways by two "
        "implementations, and G9.3 now states the rule -- every slot walks "
        "its parent's family from that family's own start and takes the "
        "first member the column has not written whose length its own window "
        "admits, and the count of partners a parent has supplied decides "
        "which parent comes next and never which member is taken (review "
        "item P2-C4-F4).",
        "definitions": DEFINITIONS,
        "cases": {},
    }
    claims = {}
    for name in sorted(builders):
        case, case_claims = build_case(name)
        document["cases"][name] = case
        claims.update(case_claims)
    return document, claims


def _self_check_mutant(document, claims, fields):
    """A full-generator mutant, driven before anything is serialized.

    The review item this carries forward (P1-R8-F3) is a number the walk
    never reaches: Python's JSON encoder writes a tuple as an array, so a
    tuple-valued field added to every case reached the file while the
    tool reported that every published number had been proved. Checking
    the committed fixture afterwards would not have caught it, because
    the fixture holds no tuple. So the mutant is driven through the whole
    proof layer here, on the document about to be written, and a run in
    which it is NOT caught stops instead of writing a byte.
    """
    mutants = (
        ("a number inside a tuple", (7.0,), "nothing proved it"),
        ("a whole number inside a tuple", (7,), "publishes the whole number"),
        ("an unclaimed wrapper", ({FLOAT64: 7.0},), "no exact value"),
        ("a wrapper holding a whole number", ({FLOAT64: 7},), "binary64"),
        ("a shape the walk has no rule for", {7.0}, "no rule for"),
    )
    for described, added, refusal_says in mutants:
        mutated = dict(document)
        mutated["cases"] = {
            name: dict(case, added_later=added)
            for name, case in document["cases"].items()
        }
        try:
            prove_every_published_float(
                mutated, claims, fields, DOCUMENT_TEXT_FIELDS, SECTION_FIELDS
            )
        except AssertionError as refusal:
            if refusal_says in str(refusal):
                continue
            raise AssertionError(
                f"the mutant that adds {described} to every case was refused, "
                f"but for the wrong reason: {refusal}"
            ) from refusal
        raise AssertionError(
            f"the mutant that adds {described} to every case was certified "
            "by the proof layer. Every number this file publishes is "
            "supposed to be proved, and a layer that passes this mutant "
            "cannot make that true. Nothing was written."
        )


def _self_check_arithmetic():
    """The transform's own foundations, checked before any case is built.

    Two of them cannot be checked by any case: the civil-date arithmetic
    is a transcription that a wrong leap rule would leave self-consistent
    across a round trip, so it is held up against the standard library's
    own proleptic Gregorian calendar rather than against itself; and the
    shortest round-trip digits are this file's own and not the
    interpreter's, so they are held up against the interpreter's rather
    than assumed to agree with it.
    """
    epoch = datetime.date(1970, 1, 1).toordinal()
    for days in range(-700000, 2900000, 9973):
        civil = datetime.date.fromordinal(days + epoch)
        mine = days_from_civil(civil.year, civil.month, civil.day)
        if mine != days:
            raise AssertionError(
                f"days_from_civil({civil.year}, {civil.month}, {civil.day}) "
                f"is {mine} and the proleptic Gregorian answer is {days}"
            )
        if civil_from_days(days) != (civil.year, civil.month, civil.day):
            raise AssertionError(
                f"civil_from_days({days}) is {civil_from_days(days)} and the "
                f"proleptic Gregorian answer is "
                f"{(civil.year, civil.month, civil.day)}"
            )
    for days in (-1, 0, 1, 11017, 18321, 59, 60, -25567):
        if days_from_civil(*civil_from_days(days)) != days:
            raise AssertionError(f"the civil-date round trip fails at {days}")
    for value in (
        1e16, 1e15, 1e-05, 1e-04, 5.0, -2.5, 0.1, 3.25, 2.5, 1234.5,
        float(2**53), 5e-324, 1.7976931348623157e308,
    ):
        digits, decpt = shortest_round_trip(value)
        sign = "-" if value < 0 else ""
        if -4 < decpt <= 16:
            mine = sign + _fixed_point(digits, decpt)
        else:
            mine = sign + _exponent_form(digits, decpt, "e")
        if mine != repr(value):
            raise AssertionError(
                f"this file spells {value!r} as {mine!r} and the shortest "
                f"round-trip rule spells it {repr(value)!r}"
            )


def _counts_published(document, section_fields=frozenset()):
    """How many whole numbers the document publishes outside a wrapper.

    Reported beside the count of proved numbers so that both halves of
    what the walk accounted for are stated, rather than only the half
    that carries a proof.
    """
    return sum(
        1
        for path, _value in _published_numbers(document, (), section_fields)
        if not path or path[-1] != FLOAT64
    )


def main(argv=None, part=None):
    """Write the vectors to the path given by --out.

    The data-provenance guard (plan D13) runs every committed fixture's
    generator with `--seed <seed> --out <path>`, so this script takes
    that exact command line. The seed is accepted and ignored: these
    vectors are a fixed transform of given words, not a random sample,
    and this tool holds no generator to give a seed to.

    ``part`` names which set of cases to write, and it is not a command
    line argument for the same reason: the manifest's convention is that
    exact command line and nothing else. The nine cases method section
    G14.3 names are the default, and the branch cases are asked for by
    the second entry point beside this one, which names this file's own
    ``BRANCH_PART`` rather than repeating a word.

    Nothing is written until every number the file would carry has been
    proved, the proof layer has refused a full-generator mutant, and the
    proof has been applied twice: once to the assembled document, and
    once to the tree parsed back out of the exact bytes about to be
    written. The second walk is over what the JSON encoder really
    produced rather than over what this file believes it produces.
    """
    parser = argparse.ArgumentParser(
        prog="make_generation_reference_vectors",
        description=(
            "Compute the twin cells synthtwin's generation method requires, "
            "from the method specification alone, importing none of the code "
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

    _self_check_arithmetic()
    document, claims = build_document(part)
    fields = whole_number_fields(document)
    proved = prove_every_published_float(
        document, claims, fields, DOCUMENT_TEXT_FIELDS, SECTION_FIELDS
    )
    counts = _counts_published(document, SECTION_FIELDS)
    _self_check_mutant(document, claims, fields)

    text = json.dumps(document, indent=2, sort_keys=True, allow_nan=False)
    # The same walk over the bytes themselves. A number that reached the
    # file through a container the walk above modelled wrongly is refused
    # here, where the container has become whatever the encoder made of
    # it; anything else the two walks disagree about is refused just
    # below.
    written = json.loads(text)
    proved_in_the_bytes = prove_every_published_float(
        written, claims, fields, DOCUMENT_TEXT_FIELDS, SECTION_FIELDS
    )
    counts_in_the_bytes = _counts_published(written, SECTION_FIELDS)
    if (proved_in_the_bytes, counts_in_the_bytes) != (proved, counts):
        raise AssertionError(
            f"the walk over the document accounted for {proved} proved "
            f"numbers and {counts} named counts, and the walk over the bytes "
            f"about to be written accounted for {proved_in_the_bytes} and "
            f"{counts_in_the_bytes}. The two must agree: a difference means "
            "the file carries a number the walk over the document did not "
            "visit."
        )

    print(
        f"proved {proved} published numbers across "
        f"{len(document['cases'])} cases, beside {counts} named whole-number "
        "counts; every number this file publishes is one of them",
        file=sys.stderr,
    )
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text + "\n")
    print(f"wrote {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
