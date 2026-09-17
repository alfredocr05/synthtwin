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

# The hundred and one percents a column of NUMBERS interpolates over
# (method G5.3 at revision 2, plan P4-D4.10).  A date or clock ladder
# keeps the eleven above: each of those is a selection ladder over
# values that cannot be averaged, and the finer one is a numeric fact.
PCT_FINE = tuple(range(101))
PERCENTS_BY_LENGTH = {len(PCT): PCT, len(PCT_FINE): PCT_FINE}


def percents_of(ladder):
    """Which percents a ladder of this many rungs stands at."""
    if len(ladder) not in PERCENTS_BY_LENGTH:
        raise AssertionError(
            f"a ladder of {len(ladder)} rungs stands at no percents this "
            "method knows: it is eleven rungs or a hundred and one"
        )
    return PERCENTS_BY_LENGTH[len(ladder)]
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

# THE WINDOW A JOINED COLUMN'S RANK AGREEMENT IS APPROXIMATED INSIDE
# (method G12.9), and how far the pairing walk of G6B.4 looks for a row
# worth swapping (G6B.4a).  Both are written out here rather than
# imported, because this file implements the method and imports nothing
# from `src/`.
RANK_AGREEMENT_WINDOW = 0.02
PROPOSAL_REACH = 16
# Half a unit at the precision an agreement is published to, which is
# four decimal places (G6B.4 steps 4 and 5).
AGREEMENT_ROUNDING = 0.00005

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


def ladder_segment(numerator, denominator, percents=PCT):
    """The unique ``j`` in ``0 .. 9`` with ``PCT[j]*D <= 100*N < PCT[j+1]*D``.

    Scanned upward from zero and stopped at the first that holds, as
    method sections G5.3 and G7.3 fix.  The probabilities are strictly
    increasing, so the segment is unique.
    """
    scaled = 100 * numerator
    for index in range(len(percents) - 1):
        if (
            percents[index] * denominator
            <= scaled
            < percents[index + 1] * denominator
        ):
            return index
    raise AssertionError(
        f"{numerator}/{denominator} falls in no ladder segment; the position "
        "of a stratum or a rank is always below one by construction"
    )


REACHABLE = (("zero", "positive"), ("negative", "zero", "positive"))


def even_split(count, strata):
    """``floor((i+1)*C/M) - floor(i*C/M)`` -- G5.2a's FALLBACK.

    It was the rule for every column until 2026-08-28, and residual
    R-P4-49 is what it cost: an even split gives every value the same
    number of cells, so a column of 230 cells holding 27 numbers --
    five of them about forty cells each, the other twenty-two about one
    -- came out 27 strata of eight or nine, a shape that can represent
    neither.  It is now reached only where there is no ladder to follow
    or where the band has no more cells than strata.
    """
    return [
        (index + 1) * count // strata - index * count // strata
        for index in range(strata)
    ]


def ladder_runs(ladder, low, count, numeric, integer_valued, figures=-1):
    """Steps 1 and 2 of method section G5.2a: the ladder's own plateaus.

    **Step 1, read the ladder at every rank of the band.**  For
    ``i = 0 .. C - 1`` the value at rank ``lo + i`` is
    ``Interpolate(Ladder, (lo + i) * 2**53, K * 2**53)`` by the convex
    form of G5.3, with the whole-number rule of G5.4 applied to it
    where ``integer_valued`` is published true -- the same value the
    twin would hold at that rank.  Nothing rounds here that does not
    round there, because the scale and the segment rule are G5.3's own.

    **Step 2, take the runs.**  A RUN is a maximal block of consecutive
    ranks whose values are equal, compared as binary64 numbers.  A run
    is a PLATEAU of the ladder: the cells that hold one value.

    Returns ``(lengths, heights)`` in rank order.
    """
    scale = 1 << SIGNIFICAND_BITS
    denominator = numeric * scale
    lengths = []
    heights = []
    for index in range(count):
        value = ladder_at(ladder, (low + index) * scale, denominator)
        if integer_valued:
            value = integer_rule(value)
        elif figures > 0:
            # ON A COLUMN WRITTEN AT ONE FRACTION WIDTH the value at a rank
            # is the grid value the writer would write there (G5.2a step
            # 1), so a run is a run of one WRITTEN number.
            value = float(grid_text(value, figures))
        if lengths and heights[-1] == value:
            lengths[-1] = lengths[-1] + 1
        else:
            lengths.append(1)
            heights.append(value)
    return lengths, heights


def join_key(lengths, heights, index):
    """The key G5.2a step 3 joins the SMALLEST of, and the leftmost wins.

    ``(min(L[j], L[j+1]), 0 if Whole(H[j]) == Whole(H[j+1]) else 1,
    Gap(j))`` with ``Gap(j) = |H[j+1] - H[j]| / (|H[j+1]| + |H[j]|)``
    and zero where that denominator is.  All three parts earn their
    place:

    - **the smaller side smallest** -- absorb the least.  A transition
      is one rank wide and a plateau is many, so this takes the
      artifact into the real value beside it and never the reverse.
    - **both whole or both fractional next** -- which cells can be
      written without a point is ``numeric_styles``, an
      EXACT-OBSERVABLE fact, and a whole value's nearest neighbour is
      very often the fraction just below it: ``4`` and ``3.875`` are
      closer than ``4`` and ``5``.
    - **nearest in value last**, measured RELATIVELY against the
      pair's own size, so a column of thousands and a column of
      thousandths are judged the same way.

    The gap is taken in binary64, DIVIDED BEFORE IT IS SUBTRACTED, and
    rescaled by the larger magnitude where the span is not finite: G5.2a
    step 3 states that order, for the overflow reason G5.3 gives, so this
    file states it too rather than taking an exact ratio the text does
    not ask for (integration repair: the two arithmetics chose different
    pairs on a common one-decimal ladder).
    """
    left = heights[index]
    right = heights[index + 1]
    # THE GAP IS TAKEN IN BINARY64 AND DIVIDED BEFORE IT IS SUBTRACTED,
    # which is what G5.2a step 3 states, with the rescale that step gives
    # for a span that is not finite (integration repair). Taken as an
    # exact rational instead, this file and the generator chose different
    # pairs on a common one-decimal ladder -- 501 cells over eleven
    # values gave [56, 40, 4, 17, 50, ...] here and [56, 40, 4, 18, 49,
    # ...] there -- and the method fixes one order for both.
    span = abs(left) + abs(right)
    gap = 0.0
    if not math.isfinite(span):
        scale = max(abs(left), abs(right))
        if math.isfinite(scale) and scale > 0.0:
            near = left / scale
            far = right / scale
            span = abs(far) + abs(near)
            if span > 0.0:
                gap = abs(far / span - near / span)
    elif span > 0.0:
        gap = abs(right / span - left / span)
    return (
        min(lengths[index], lengths[index + 1]),
        0 if left.is_integer() == right.is_integer() else 1,
        gap,
    )


def overshoot(lengths, index, cap):
    """How far joining runs ``index`` and ``index + 1`` would stand above the cap.

    The FIRST part of G5.2a step 3's key: a join that keeps both runs at
    or under the cap costs nothing here and is chosen by the three parts
    that follow, and where every join overshoots, the one that overshoots
    least is taken.  A cap of nought bounds nothing.
    """
    if cap <= 0:
        return 0
    return max(0, lengths[index] + lengths[index + 1] - cap)


def levelled(lengths, cap):
    """G5.2a step 4: no stratum above the cap.

    Strata are visited in ascending order.  While one holds more cells
    than the cap, the NEAREST other stratum still under the cap -- the
    lower one where two are equally near -- takes as many of its cells
    as it has room for and the overflow still owes.  The stratum count
    and the band's total are unchanged.  Nothing moves where the cap is
    nought or where the strata could not hold the band under it.
    """
    sizes = list(lengths)
    if cap <= 0 or not sizes or sum(sizes) > cap * len(sizes):
        return sizes
    for index in range(len(sizes)):
        while sizes[index] > cap:
            roomy = [other for other in range(len(sizes)) if sizes[other] < cap]
            if not roomy:
                break
            target = min(roomy, key=lambda other: (abs(other - index), other))
            moved = min(sizes[index] - cap, cap - sizes[target])
            sizes[index] -= moved
            sizes[target] += moved
    return sizes


# THE FLOOR EVERY CASE IS DESCRIBED UNDER.  tests/test_generation_reference.py
# builds each case's document with `small_cell_floor: 11`, and G5.2a's cap
# reads that floor where a case's mode pair is withheld; the test holds the
# two equal.
CASE_SMALL_CELL_FLOOR = 11


def stratum_cap(column, ladder, numeric, floor):
    """The most cells one stratum may hold -- G5.2a.

    The published ``mode_count`` where the mode pair is published: no
    number of the column was held by more cells than that.  Where the pair
    is withheld, the smaller of ``K - n_distinct_values + 1`` -- every other
    number holds a cell -- and the most cells one value can hold without
    the hundred-and-one-rung ladder showing more equal rungs than it does: a value held by ``c`` cells
    puts at least ``floor((c - 2) * 100 / (K - 1))`` rungs on itself, so
    with ``r`` the longest run of equal rungs ``c`` is at most
    ``floor((r + 1) * (K - 1) / 100) + 2``.

    And a withheld pair under a publication ``floor`` of 3 or more proves no
    number was held by ``floor`` cells, so the cap is at most ``floor - 1``
    -- wherever the description does not itself prove a number held by that
    many: ``ceil(K / n_distinct_values)`` cells, or the
    ``floor((r - 1) * (K - 1) / 100)`` a run of ``r`` equal rungs forces onto
    one number.  A floor under 3 proves only that every number is
    different, which the count already says.
    """
    if column.get("mode") is not None and column.get("mode_count", 0) > 0:
        return column["mode_count"]
    # Every other number holds a cell, so one holds at most what is left.
    # A placeholder count of nought (a case whose count is taken off its
    # finished cells) proves nothing here.
    distinct = column.get("n_distinct_values", 0)
    counted = max(1, numeric - distinct + 1) if distinct > 0 else 0
    if ladder is None or numeric < 2:
        return floored_cap(counted, floor, numeric, distinct, 0)
    longest = 1
    run = 1
    for index in range(1, len(ladder)):
        if ladder[index] == ladder[index - 1]:
            run += 1
            longest = max(longest, run)
        else:
            run = 1
    ladder_bound = ((longest + 1) * (numeric - 1)) // 100 + 2
    bound = min(counted, ladder_bound) if counted > 0 else ladder_bound
    return floored_cap(bound, floor, numeric, distinct, longest)


def floored_cap(bound, floor, numeric, distinct, longest):
    """``bound`` lowered to ``floor - 1`` where a floor of 3 or more binds.

    It binds unless the description proves a number held by ``floor`` cells:
    ``ceil(numeric / distinct)``, or ``floor((longest - 1) * (numeric - 1) /
    100)`` for a run of ``longest`` equal rungs.  Nought still means no bound.
    """
    if floor < 3:
        return bound
    proven = 0
    if distinct > 0:
        proven = max(proven, -(-numeric // distinct))
    if proven >= floor:
        return bound
    held = floor - 1
    return held if bound <= 0 else min(bound, held)


def band_allotment(
    count, strata, ladder, low, numeric, integer_valued, figures=-1, cap=0
):
    """How a band's cells divide between its strata -- method G5.2a.

    THE EVEN SPLIT IS THE FALLBACK AND NO LONGER THE RULE.  Where there
    is no ladder, or where the band has no more cells than strata, the
    cells divide evenly.  Otherwise the sizes follow the LADDER'S OWN
    SHAPE, which is what the hundred-and-one-rung ladder of G5.1 knows
    and the eleven named rungs do not: a value standing at seventeen of
    the rungs stands at seventeen per cent of the column, because the
    rungs stand at the percentiles.

    Interpolating a ladder over a column's ranks puts a one-rank
    TRANSITION between each pair of real plateaus -- a value the column
    does not hold, standing between two it does -- so the run count is
    usually larger than the stratum count and never exactly it by
    accident.  Runs are therefore joined down, or divided up, until
    there are exactly ``strata`` of them, and the sizes are the run
    lengths in rank order.  Each is at least one and they sum to
    ``count``, because every run is at least one rank long and neither
    the joins nor the divisions change the total.
    """
    if strata <= 0:
        return []
    if strata > count:
        # A QUESTION THIS ORACLE REFUSES TO ANSWER BY GUESSING.  G5.2
        # caps `M_rest` at `G + P` so that no stratum is empty -- "a
        # stratum with no cell in it is not a value" (P2-C1-F5) -- and
        # the cell share it capped for could never give one band more
        # strata than it has cells.  The RUN share of G5.2b can: it is
        # clamped only into [1, M_rest - 1], and nothing holds `M_neg`
        # at or below `G` or `M_pos` at or below `P`.  The even split
        # would then hand back a stratum of nought cells, which G5.2
        # forbids by name, so the answer is asked for rather than
        # invented.
        raise AssertionError(
            f"a band of {count} cells was given {strata} strata: G5.2b's run "
            "share can exceed a band's own cell count and the method states "
            "no clamp that stops it, while G5.2 forbids a stratum with no "
            "cell in it. The specification does not say which of the two "
            "gives way"
        )
    if ladder is None or strata >= count:
        return even_split(count, strata)
    if cap > 0:
        # A band with too few strata to fit under the cap is held to the
        # even split's own largest share instead.
        cap = max(cap, -(-count // strata))
    lengths, heights = ladder_runs(
        ladder, low, count, numeric, integer_valued, figures
    )
    # ``min`` and ``max`` both hold the FIRST extremal item, which is
    # the leftmost-wins-a-tie both halves of step 3 ask for.
    while len(lengths) > strata:
        at = min(
            range(len(lengths) - 1),
            key=lambda index: (overshoot(lengths, index, cap),)
            + join_key(lengths, heights, index),
        )
        lengths[at] = lengths[at] + lengths[at + 1]
        del lengths[at + 1]
        del heights[at + 1]
    while len(lengths) < strata:
        at = max(range(len(lengths)), key=lambda index: lengths[index])
        whole = lengths[at]
        lengths[at] = whole // 2
        lengths.insert(at + 1, whole - whole // 2)
        # The two strata then hold the same value, and the leading-zero
        # family of G6.5 is what gives the second of them a spelling.
        heights.insert(at + 1, heights[at])
    lengths = levelled(lengths, cap)
    if sum(lengths) != count or any(size < 1 for size in lengths):
        raise AssertionError(
            "a band's allotment must cover its own cells with a stratum of "
            "at least one cell each, which the joins and the divisions of "
            "G5.2a step 3 preserve"
        )
    return lengths


def band_sizes(
    negatives,
    zeros,
    positives,
    negative_strata,
    positive_strata,
    ladder=None,
    numeric=None,
    integer_valued=False,
    figures=-1,
    cap=0,
):
    """The split of method section G5.2a, band by band.

    The zero stratum, when it exists, has size ``Z``.  Each of the
    other two bands divides its own cells among its own strata by
    ``band_allotment``, reading the ladder from the rank its first cell
    stands at in the sorted column -- ``0`` for the negatives and
    ``G + Z`` for the positives.  Where no ladder is handed in, every
    band takes the even split, which is what a caller that reads only
    the SHAPE of the layout wants.
    """
    sizes = []
    bands = []
    for count, strata, band, low in (
        (negatives, negative_strata, "negative", 0),
        (zeros, 1 if zeros > 0 else 0, "zero", negatives),
        (positives, positive_strata, "positive", negatives + zeros),
    ):
        if band == "zero":
            for _index in range(strata):
                sizes.append(count)
                bands.append(band)
            continue
        for size in band_allotment(
            count, strata, ladder, low, numeric, integer_valued, figures, cap
        ):
            sizes.append(size)
            bands.append(band)
    return sizes, bands


def band_strata(
    negatives,
    zeros,
    positives,
    values,
    ladder=None,
    numeric=None,
    integer_valued=False,
    figures=-1,
    cap=0,
):
    """How many strata each band gets -- method section G5.2b.

    Returns ``(M_neg, M_pos)``.  The share follows the LADDER rather
    than the cells wherever there is one: ``A_neg`` and ``A_pos`` are
    how many RUNS step 2 of G5.2a finds in each band -- how many
    different values the ladder gives it -- and they replace the cell
    counts in the formula.  Cells are the wrong thing to follow here,
    and this clause followed them until 2026-08-28: two bands holding
    the same number of cells need not hold the same number of values,
    and a stratum count is about values.  The share falls back to ``G``
    and ``P`` where there is no ladder or where ``A_neg + A_pos`` is
    zero.

    The rounding is to the nearest whole number with ties upward,
    computed exactly in whole numbers, then clamped so that a band
    holding cells keeps a stratum.

    THEN THE CAP'S FLOOR (landing 2b.1, part 2).  Every number of a band
    holds at most ``cap`` cells, so the band holds at least
    ``ceil(cells / cap)`` numbers; where ``M_rest`` can give both bands
    that many, ``M_neg`` is clamped into
    ``[ceil(G / cap), M_rest - ceil(P / cap)]``.
    """
    rest = values - (1 if zeros > 0 else 0)
    if rest < 0:
        raise AssertionError(
            "fewer different values are permitted than the zero stratum alone "
            "requires; this document would be refused by the feasibility stage"
        )
    if negatives > 0 and positives > 0:
        share_negative = negatives
        share_positive = positives
        if ladder is not None:
            runs_negative = len(
                ladder_runs(
                    ladder, 0, negatives, numeric, integer_valued, figures
                )[0]
            )
            runs_positive = len(
                ladder_runs(
                    ladder,
                    negatives + zeros,
                    positives,
                    numeric,
                    integer_valued,
                    figures,
                )[0]
            )
            if runs_negative + runs_positive > 0:
                share_negative = runs_negative
                share_positive = runs_positive
        share = share_negative + share_positive
        negative_strata = (2 * rest * share_negative + share) // (2 * share)
        negative_strata = max(1, min(rest - 1, negative_strata))
        if cap > 0:
            need_negative = -(-negatives // cap)
            need_positive = -(-positives // cap)
            if need_negative + need_positive <= rest:
                negative_strata = max(negative_strata, need_negative)
                negative_strata = min(negative_strata, rest - need_positive)
        return negative_strata, rest - negative_strata
    if negatives > 0:
        return rest, 0
    if positives > 0:
        return 0, rest
    return 0, 0


def stratum_layout(
    numeric,
    negatives,
    zeros,
    positives,
    values,
    pair=None,
    ladder=None,
    integer_valued=False,
    figures=-1,
    cap=0,
):
    """The strata of method section G5.2: sizes and starting positions.

    Returns ``(sizes, starts, bands)`` in the fixed order negatives
    ascending, then the zero stratum, then positives ascending -- which
    is the sorted order of the column's own values, and the order the
    ladder is a statement about.  ``bands`` names each stratum
    ``negative``, ``zero`` or ``positive``, which is what the sign
    repair of G5.5 reads.  ``pair`` overrides the band share, which is
    what the carrier step's band half of G5.2b hands back.  ``ladder``
    is what G5.2a's allotment and G5.2b's share follow; a caller that
    reads only the SHAPE of the layout -- how many strata there are and
    which band each is in, which is all G4.3's budget needs -- may
    leave it out, because neither the total nor the bands depend on it.
    """
    if pair is None:
        pair = band_strata(
            negatives,
            zeros,
            positives,
            values,
            ladder,
            numeric,
            integer_valued,
            figures,
            cap,
        )
    sizes, bands = band_sizes(
        negatives,
        zeros,
        positives,
        pair[0],
        pair[1],
        ladder,
        numeric,
        integer_valued,
        figures,
        cap,
    )
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
    end = ladder[0] if index == 0 else ladder[-1]
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
    negatives,
    zeros,
    positives,
    pair,
    ladder,
    integer_valued,
    demand,
    plus_demand,
    numeric=None,
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
                negatives,
                zeros,
                positives,
                pair[0],
                pair[1],
                ladder,
                numeric,
                integer_valued,
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
                negatives,
                zeros,
                positives,
                moved[0],
                moved[1],
                ladder,
                numeric,
                integer_valued,
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


def carrier_split(
    sizes, bands, ladder, integer_valued, published, zeros, positives, fractional=-1
):
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
            if fractional > 0:
                # ON A COLUMN ON A WRITTEN GRID each taker takes its even
                # share from the NEAREST givers, the lower of two equally
                # near, each giver keeping one cell (G5.2, landing 2b.1):
                # taking from the lowest strata upward slid every boundary
                # between them and the takers off the grid G5.2a lined up.
                count = len(takers)
                for step, taker in enumerate(takers):
                    owed = (step + 1) * take // count - step * take // count
                    while owed > 0:
                        spare = [index for index in givers if moved[index] > 1]
                        if not spare:
                            break
                        index = min(
                            spare, key=lambda other: (abs(other - taker), other)
                        )
                        given = min(moved[index] - 1, owed)
                        moved[index] -= given
                        moved[taker] += given
                        owed -= given
                continue
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
    percents = percents_of(ladder)
    segment = ladder_segment(position, denominator, percents)
    return convex_interpolation(
        position, denominator, ladder[segment], ladder[segment + 1], percents
    )["clamped"]


def convex_interpolation(
    position, denominator, low, high, percents=PCT
):
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
    segment = ladder_segment(position, denominator, percents)
    above = 100 * position - percents[segment] * denominator
    width = (percents[segment + 1] - percents[segment]) * denominator
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


def grid_step_of_sign(band, ladder, figures, held, total):
    """G5.5's fallback on a column written at one width (landing 2b.1).

    The nearest grid point on the band's side of zero that no other
    stratum holds, never past that side's published end; the first step
    where every step within reach is held.  A plain ``-1.0`` there made
    two strata one number and was written shorter than the width.
    """
    negative = band == "negative"
    first = None
    for step in range(1, total + 2):
        candidate = float(fractions.Fraction(-step if negative else step, 10 ** figures))
        if negative and candidate < ladder[0]:
            break
        if not negative and candidate > ladder[-1]:
            break
        if first is None:
            first = candidate
        if candidate not in held:
            return candidate
    if first is not None:
        return first
    return -1.0 if negative else 1.0


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


def _group_thousands(text, mark):
    """``text`` with ``mark`` between each group of three whole figures.

    The THIRD writing of this rule, and deliberately unlike the other
    two. The generator counts the first group from the left and the
    validator walks from the right; this reverses the whole figures,
    cuts them in threes and reverses back, so a defect shared by any two
    of them would show as a disagreement with the third.  It imports
    nothing, as this oracle imports nothing it checks.

    Only a whole part of four or more figures is grouped; a sign, the
    point and every figure after it are left exactly where they stood.
    """
    if not mark:
        return text
    sign = text[0] if text and text[0] in "+-" else ""
    body = text[len(sign):]
    whole, point, rest = body.partition(".")
    if len(whole) < 4 or not whole.isdigit():
        return text
    backwards = whole[::-1]
    chunks = [backwards[at:at + 3][::-1] for at in range(0, len(backwards), 3)]
    return sign + mark.join(reversed(chunks)) + point + rest


# THE MARKS A COLUMN MAY PUBLISH BETWEEN THOUSANDS (landing 2b.2), as the
# contract lists them: none, a comma, a point under a declared decimal
# comma, a space, an apostrophe, the right single quotation mark, a
# no-break space, a narrow no-break space and a thin space.
PUBLISHED_MARKS = ("", ",", ".", " ", "'", "\u2019", "\u00a0", "\u202f", "\u2009")

# HOW A NEGATIVE IS WRITTEN (landing 2b.2): the notation names, and the
# text each writes in place of the hyphen-minus in front of the figures.
NEGATIVE_NOTATIONS = {
    "minus": ("-", ""),
    "brackets": ("(", ")"),
    "minus_sign": ("\u2212", ""),
    "trailing_minus": ("", "-"),
}


def grouping_mark_of(column):
    """The mark the cells are grouped with before any exchange (G6.1).

    A published comma, and a published point on a column that writes its
    decimals with a comma, are both written as a comma first -- the point
    arrives with the exchange of `decimal_comma_spelled`.  Every other
    mark is neither decimal mark, no exchange touches it, and the cells
    carry it as published.
    """
    published = column.get("group_separator", "")
    if published not in PUBLISHED_MARKS:
        raise AssertionError(f"{published!r} is not a mark a column may publish")
    return "," if published in (",", ".") else published


def negative_spelled(text, notation):
    """A finished cell with its minus written in the column's notation.

    Only a text that begins with the hyphen-minus is negative here; every
    other text comes back as it is.  The figures between the two halves
    of the notation are the ones the style wrote -- zeros, mark and all --
    and no sign stands inside them, so brackets can never read as the
    contradictory stand-in `(-5)`.
    """
    before, after = NEGATIVE_NOTATIONS[notation]
    if not text.startswith("-"):
        return text
    # A trailing minus is read only after figures carrying a decimal
    # point -- a thousands mark alone is a fact of a value's size, not of
    # the column's form -- so on a field with no point the hyphen-minus
    # stays in front, where the cell still reads as a number.
    if notation == "trailing_minus" and "." not in text[1:]:
        return text
    return before + text[1:] + after


def plus_style_exchange(count, styles, values, integer_valued):
    """Styles exchanged so a signed decimal has cells to stand on (G6.4).

    Only where ``count`` -- the named ``decimal_plus`` -- exceeds the cells
    allocated ``decimal`` whose value is not below zero.  The cells
    allocated ``plain`` whose value is not below zero are listed from the
    first cell upward, and the cells allocated ``decimal`` whose value is
    below zero and has a point-free spelling from the last cell downward;
    the i-th of the first list takes ``decimal`` and the i-th of the
    second takes ``plain``, for as many pairs as the shortfall and both
    lists allow.  Each exchange leaves every form count where it was.
    """
    if count <= 0:
        return styles
    have = sum(
        1
        for style, value in zip(styles, values)
        if style == "decimal" and not value < 0
    )
    if have >= count:
        return styles
    givers = [
        index
        for index, (style, value) in enumerate(zip(styles, values))
        if style in ("plain", "leading_zero") and not value < 0
    ]
    takers = [
        index
        for index in reversed(range(len(values)))
        if styles[index] == "decimal"
        and values[index] < 0
        and point_free_spelling(values[index], integer_valued) is not None
    ]

    def figures(value):
        return len(point_free_spelling(value, integer_valued).lstrip("-"))

    # A padded giver (integration repair of landing 2b.2) takes the first
    # free partner needing no more figures than it does.
    exchanged = list(styles)
    used = set()
    short = count - have
    for giver in givers:
        if short <= 0:
            break
        for taker in takers:
            if taker in used:
                continue
            if exchanged[giver] == "leading_zero" and figures(values[taker]) > figures(values[giver]):
                continue
            used.add(taker)
            exchanged[giver], exchanged[taker] = "decimal", exchanged[giver]
            short -= 1
            break
    return exchanged


# -- the two mixture censuses (landing 2b.7) --------------------------

NEGATIVE_NOTATION_ORDER = ("minus", "brackets", "minus_sign", "trailing_minus")
GROUP_MARK_ORDER = ("", ",", ".", " ", "'", "’", " ", " ", " ")


def mark_written(published):
    """The mark a cell is grouped with before any exchange (G6.1).

    `grouping_mark_of` asks this of the column's one published mark; a
    census of marks asks it of each mark it names, and the rule is the
    same one.
    """
    return "," if published in (",", ".") else published


def named_conventions(census, order):
    """The conventions a mixture census NAMES, in the enumeration's order.

    The pooled remainder and the unavailable state name no convention, so
    neither reaches a cell: what they cover is written in the column's
    published majority, as a pooled style count is written plainly.
    """
    return [
        (name, census[name])
        for name in order
        if name in census and census[name] > 0
    ]


def notation_places(census, default, styles, values):
    """Which notation each negative cell wears (landing 2b.7, G6.1).

    Each named notation takes its count in turn from the cells holding a
    negative value that no earlier notation took, spread across them by
    ``plus_cells_by_value`` in order (plan P4-D149) -- whole runs of one
    value by the spread rule, a split run's share on its first cells --
    and not from the first of them upward; what no named count covers
    wears the column's published ``negative_form``.  A trailing minus is
    offered only to a ``decimal`` cell, because `negative_spelled` writes
    one only where the figures carry a point.
    """
    worn = [default] * len(values)
    named = named_conventions(census, NEGATIVE_NOTATION_ORDER)
    if not named:
        return worn
    taken = set()
    for notation, wanted in named:
        eligible = [
            index
            for index in range(len(values))
            if index not in taken
            and values[index] < 0
            and (notation != "trailing_minus" or styles[index] == "decimal")
        ]
        placed = min(wanted, len(eligible))
        for index in plus_cells_by_value(eligible, values, placed, True):
            taken.add(index)
            worn[index] = notation
    return worn


# The marks a pooled remainder may be written with, in the order one is
# offered (G6.1, plan P4-D142): neither decimal mark, and never one the
# census names.
POOL_MARK_ORDER = (" ", "'", "\u2019", "\u00a0", "\u202f", "\u2009")


def pad_need(value, integer_valued):
    """How many figures a value's own point-free spelling writes, sign aside."""
    text = point_free_spelling(value, integer_valued)
    if text is None:
        text = canonical_spelling(value, integer_valued)
    return len(text) - 1 if text.startswith("-") else len(text)


def pad_places(census, styles, values, integer_valued, forms=None):
    """Which field width each padded cell is written at, or -1 -- G6.3.

    Every width the census NAMES is a quota.  The cells are served in two
    tiers (plan P4-D145): first those styled ``leading_zero``, then those
    styled ``leading_plus`` whose value is whole and not negative, each
    tier from what the widths still owe -- and the second tier pads no
    more cells in all than the census counts past the published
    ``leading_zero`` count (or, where that form is not named, past the
    cells styled ``leading_zero``), which is how many plus-signed padded
    cells the census holds.  Inside a tier the cells are
    grouped by the value they hold, in first-seen order; widths are served
    narrowest first; a value may take a width only where its own figures
    are FEWER than the width, so at least one zero is written; the groups
    are ranked by how many of their cells still wait, most first, then by
    value; whole groups that fit what the width owes are taken first, and
    only then is one group divided cell by cell.  Afterwards a
    ``leading_zero`` cell still unplaced takes the narrowest named width
    its value can wear, over that width's count.
    """
    quotas = {
        int(key): count for key, count in census.items() if key != "(withheld)"
    }
    places = [-1] * len(styles)
    if not quotas:
        return places
    left = dict(quotas)
    plus_budget = sum(census.values())
    if forms is not None and "leading_zero" in forms:
        plus_budget -= forms["leading_zero"]
    else:
        plus_budget -= sum(1 for style in styles if style == "leading_zero")
    for tier in ("leading_zero", "leading_plus"):
        groups = {}
        seen = []
        for index, style in enumerate(styles):
            if style != tier:
                continue
            value = values[index]
            if tier == "leading_plus" and (
                value < 0 or not float(value).is_integer()
            ):
                continue
            if value in groups:
                groups[value].append(index)
                continue
            groups[value] = [index]
            seen.append(value)
        for width in sorted(quotas):
            owing = left[width]
            if tier == "leading_plus":
                owing = min(owing, max(0, plus_budget))
            asked = owing
            ranked = []
            for value in seen:
                waiting = sum(1 for index in groups[value] if places[index] < 0)
                if waiting < 1 or pad_need(value, integer_valued) >= width:
                    continue
                ranked.append((-waiting, value))
            for _size, value in sorted(ranked):
                if owing < 1:
                    break
                unplaced = [index for index in groups[value] if places[index] < 0]
                if len(unplaced) > owing:
                    continue
                for index in unplaced:
                    places[index] = width
                owing -= len(unplaced)
            for _size, value in sorted(ranked):
                if owing < 1:
                    break
                for index in groups[value]:
                    if owing < 1:
                        break
                    if places[index] >= 0:
                        continue
                    places[index] = width
                    owing -= 1
            left[width] -= asked - owing
            if tier == "leading_plus":
                plus_budget -= asked - owing
    for index, style in enumerate(styles):
        if style != "leading_zero" or places[index] >= 0:
            continue
        need = pad_need(values[index], integer_valued)
        for width in sorted(quotas):
            if need >= width:
                continue
            places[index] = width
            break
    return places


def candidate_mark(census, published):
    """The mark a cell is asked whether it can wear (G6.1, plan P4-D142).

    The published mark as written before any exchange, and where the
    column publishes none, the first mark its census names, written the
    same way; nothing where it names none either.
    """
    if published:
        return published
    named = named_conventions(census, GROUP_MARK_ORDER)
    if named:
        return mark_written(named[0][0])
    return ""


def mark_places(
    census, published, groupable, floor=CASE_SMALL_CELL_FLOOR, values=None
):
    """Which mark each grouped cell wears (landing 2b.7, G6.1).

    ``groupable`` says, per cell, whether writing it with a mark actually
    put a mark in it -- asked of the writer rather than restated from the
    rules about forms, orders and four whole figures.  Where the census
    names no mark every cell wears the column's published mark.  Where it
    names one or more (plan P4-D142), each named mark takes its count of
    the groupable cells not yet taken; a ``(withheld)`` remainder takes its
    count next, with the first mark of ``POOL_MARK_ORDER`` the census does
    not name; and the groupable cells still left are written with no mark
    where they number at least the census floor -- two, or ``floor`` where
    that is larger -- and with the published mark otherwise.

    Each count is taken by the spread rule of ``plus_cells_by_value``
    over the cells still untaken, in cell order, and not from the first
    of them upward (plan P4-D149): taking from the first would put every
    bare cell on the largest values.  Where ``values`` is not given every
    cell is its own run.
    """
    if values is None:
        values = [float(index) for index in range(len(groupable))]
    worn = [published] * len(groupable)
    named = named_conventions(census, GROUP_MARK_ORDER)
    if not named:
        return worn
    spending = [(mark_written(mark), wanted) for mark, wanted in named]
    pool = census.get("(withheld)", 0)
    if pool > 0:
        unnamed = [mark for mark in POOL_MARK_ORDER if mark not in census]
        spending.append((unnamed[0], pool))
    taken = set()
    for mark, wanted in spending:
        eligible = [
            index
            for index in range(len(groupable))
            if groupable[index] and index not in taken
        ]
        placed = min(wanted, len(eligible))
        for index in plus_cells_by_value(eligible, values, placed, True):
            taken.add(index)
            worn[index] = mark
    left = [
        index
        for index in range(len(groupable))
        if groupable[index] and index not in taken
    ]
    if len(left) >= max(2, floor):
        for index in left:
            worn[index] = ""
    return worn


def padded_sign_exchange(
    styles, values, integer_valued, pads, marks, notations, plussed, content,
    owed,
):
    """Padded cells trade the plus so a value is written both ways (G6.5).

    Plan P4-D145.  A cell may trade when it is styled ``leading_plus`` or
    ``leading_zero``, sits at a named field width, wears no mark and no
    signed-decimal plus, and holds a whole value that is not negative.  At
    one width a value's tradeable cells are counted by form, and a trade
    turns one ``leading_plus`` cell into ``leading_zero`` and one
    ``leading_zero`` cell into ``leading_plus``.  Three walks, each over the
    widths ascending and, within a width, the values in the order of their
    first cell; in each trade the value's first cell (in cell order) of
    the form it gives up changes:

    1. while at least two identities are owed, the k-th value with no
       ``leading_zero`` cell and at least two ``leading_plus`` cells trades
       with the k-th value with no ``leading_plus`` cell and at least two
       ``leading_zero`` cells (the lists taken before the walk);
    2. while at least one is owed, each value with no ``leading_zero``
       cell and at least two ``leading_plus`` cells, in order, trades with
       the first value, in order, that has at least one ``leading_plus``
       cell and still has at least two ``leading_zero`` cells, from a list
       taken before the walk -- a value that no longer has two is passed
       over for good;
    3. the same with the two forms the other way round.

    Nothing is done where no identity is owed.
    """
    if owed < 1:
        return styles, content, owed
    styles = list(styles)
    content = list(content)
    other = {"leading_plus": "leading_zero", "leading_zero": "leading_plus"}
    groups = {}
    for index, style in enumerate(styles):
        value = values[index]
        if style not in other or pads[index] < 0:
            continue
        if marks[index] or plussed[index]:
            continue
        if value < 0 or not float(value).is_integer():
            continue
        width_groups = groups.setdefault(pads[index], {})
        width_groups.setdefault(
            value, {"leading_plus": [], "leading_zero": []}
        )[style].append(index)

    def trade(group, form):
        cell = min(group[form])
        group[form].remove(cell)
        group[other[form]].append(cell)
        styles[cell] = other[form]
        content[cell] = styled_spelling(
            other[form], values[cell], integer_valued, 0, marks[cell],
            notations[cell], plussed[cell], pads[cell],
        )

    for width in sorted(groups):
        ordered = list(groups[width].values())
        only_plus = [g for g in ordered if not g["leading_zero"] and len(g["leading_plus"]) >= 2]
        only_zero = [g for g in ordered if not g["leading_plus"] and len(g["leading_zero"]) >= 2]
        for taker, donor in zip(only_plus, only_zero):
            if owed < 2:
                break
            trade(taker, "leading_plus")
            trade(donor, "leading_zero")
            owed -= 2
    for giving in ("leading_plus", "leading_zero"):
        spare = other[giving]
        for width in sorted(groups):
            ordered = list(groups[width].values())
            takers = [g for g in ordered if not g[spare] and len(g[giving]) >= 2]
            donors = [g for g in ordered if g[giving] and len(g[spare]) >= 2]
            place = 0
            for taker in takers:
                while place < len(donors) and len(donors[place][spare]) < 2:
                    place += 1
                if owed < 1 or place >= len(donors):
                    break
                trade(taker, giving)
                trade(donors[place], spare)
                owed -= 1
    return styles, content, owed


def plus_places(count, styles, values):
    """Which cells carry a plus in front of a decimal spelling (G6.1).

    The cells that may are the ones allocated ``decimal`` whose value is
    not below zero, taken in cell order.  ``count`` of them carry one --
    all of them where fewer exist -- and they are spread, not packed: of
    E such cells the k-th, counting from 0, carries a plus exactly when
    the whole part of (k+1)*count/E exceeds the whole part of k*count/E.
    Taking them from the first cell upward would put every plus on the
    smallest values.
    """
    eligible = [
        index
        for index, (style, value) in enumerate(zip(styles, values))
        if style == "decimal" and not value < 0
    ]
    placed = min(count, len(eligible))
    carries = [False] * len(values)
    for index in plus_cells_by_value(eligible, values, placed):
        carries[index] = True
    return carries


def plus_cells_by_value(eligible, values, placed, in_order=False):
    """The spread rule rounded to whole values (integration repair of 2b.2).

    Runs of one value in cell order are each offered the pluses the
    cell-by-cell spread gives them, and take a plus on every cell where
    that is at least half the run.  The total is made exactly ``placed``:
    over, the taken run with the smallest offered share no larger than the
    excess is given up; under, the untaken run with the largest share that
    fits is taken, earlier first on a tie; what whole runs cannot meet goes
    on the first cells of the first untaken run long enough to hold it.
    """
    total = len(eligible)
    if placed <= 0 or not total:
        return []
    starts = [k for k in range(total) if k == 0 or values[eligible[k]] != values[eligible[k - 1]]]
    ends = starts[1:] + [total]
    sizes = [end - start for start, end in zip(starts, ends)]
    offered = [end * placed // total - start * placed // total for start, end in zip(starts, ends)]
    taken = [2 * share >= size for share, size in zip(offered, sizes)]
    carried = sum(size for size, flag in zip(sizes, taken) if flag)
    runs = range(len(sizes))
    while carried > placed:
        fits = [r for r in runs if taken[r] and sizes[r] <= carried - placed]
        if not fits:
            break
        best = fits[0]
        for r in fits[1:]:
            if fractions.Fraction(offered[r], sizes[r]) < fractions.Fraction(offered[best], sizes[best]):
                best = r
        taken[best] = False
        carried -= sizes[best]
    while carried < placed:
        fits = [r for r in runs if not taken[r] and sizes[r] <= placed - carried]
        if not fits:
            break
        best = fits[0]
        for r in fits[1:]:
            if fractions.Fraction(offered[r], sizes[r]) > fractions.Fraction(offered[best], sizes[best]):
                best = r
        taken[best] = True
        carried += sizes[best]
    # A run that must be split keeps the spread rule inside itself.
    share = [size if flag else 0 for size, flag in zip(sizes, taken)]
    if carried > placed:
        last = max(r for r in runs if taken[r])
        share[last] = sizes[last] - (carried - placed)
    elif carried < placed:
        for r in runs:
            if not taken[r] and sizes[r] >= placed - carried:
                share[r] = placed - carried
                break
    # In order (plan P4-D149, the censuses of conventions): a split run
    # keeps its share on its first cells.
    if in_order:
        return [
            eligible[starts[r] + j]
            for r in runs
            for j in range(sizes[r])
            if j < share[r]
        ]
    return [
        eligible[starts[r] + j]
        for r in runs
        for j in range(sizes[r])
        if (j + 1) * share[r] // sizes[r] > j * share[r] // sizes[r]
    ]


def decimal_comma_spelled(content):
    """A declared column's cells with every point and comma exchanged (P4-D26).

    Applied to the numbers the numeric rules wrote and to nothing else;
    an absent cell is written empty and has no mark to exchange.
    """
    table = {".": ",", ",": "."}
    return ["".join(table.get(letter, letter) for letter in cell) for cell in content]


def styled_spelling(
    style, value, integer_valued, order, mark="", negative="minus", plus=False,
    pad=-1,
):
    """One numeric cell in its style, with the column's sign spellings.

    The style's own text comes from `_style_text`.  A ``decimal`` cell
    chosen by `plus_places` then takes a plus in front, ahead of any
    zeros it spent, and a negative is written in the column's notation
    by `negative_spelled` (landing 2b.2).
    """
    text = _style_text(style, value, integer_valued, order, mark, pad)
    if plus and style == "decimal" and text[:1] not in ("-", "+"):
        text = "+" + text
    return negative_spelled(text, negative)


def _style_text(style, value, integer_valued, order, mark="", pad=-1):
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

    ``mark`` is the column's published thousands separator, written into
    the ``plain``, ``leading_plus`` and ``decimal`` styles at order zero
    and into nothing else: not ``leading_zero`` and not either exponent
    form, and not a cell whose leading-zero family is spent, because
    grouping the zeros would write a padded field wearing a separator.
    This docstring once said a separator is never written because the
    comma breaks the CSV row itself.  That was FALSE -- a comma-bearing
    cell is quoted and read back unchanged -- and the method was amended
    on 2026-09-14.  Accounting parentheses still never appear, because
    they are the contradictory-notation stand-in of G10.3 and would
    change a cell's class.
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
        return _group_thousands(text, mark)
    sign = "-" if text.startswith("-") else ""
    body = text[len(sign):]
    if style == "leading_zero":
        # A NAMED FIELD WIDTH (G6.3): as many zeros as make the field that
        # width, and never fewer than the order asks for.
        if pad >= 0:
            return sign + "0" * max(order + 1, pad - len(body)) + body
        return sign + "0" * (order + 1) + body
    if style == "leading_plus":
        if sign:
            raise AssertionError(
                "there is no leading-plus spelling of a negative value"
            )
        # ...AND ON A PLUS, whose zeros go after it and which then wears
        # no mark (plan P4-D145).
        if pad >= 0:
            return "+" + "0" * max(order, pad - len(body)) + body
        if order == 0:
            return "+" + _group_thousands(body, mark)
        return "+" + "0" * order + body
    if style == "decimal" and order == 0:
        return sign + _group_thousands(body, mark)
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
    published, values, sizes, starts, bands, ladder, numeric, integer_valued,
    signed=0,
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

    Where ``signed``, the named count of ``decimal_plus``, is above
    nought, a walk over the negative strata alone comes between the two:
    at most ``free - signed`` cells that are not negative may be
    point-free, since that many must stay in the form written with a
    point, so the negative strata are taken until they carry
    ``W - max(0, free - signed)`` cells (the verification of landing
    2b.2).

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
    below = max(0, wanted - max(0, free - signed)) if signed > 0 else 0
    for demand, reachable in (
        (min(remaining["leading_plus"], free), REACHABLE[0]),
        (below, ("negative",)),
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
                ends = (ladder[0], ladder[-1])
            moved = whole_inside(
                values[index], bands[index], share, ends, total + 1, taken
            )
            if moved is None:
                continue
            taken.append(moved)
            values[index] = moved
    return values


def named_point_free(published):
    """The point-free cells a styles map NAMES, the withheld share excluded.

    ``_effective_style_map`` beside this one adds the withheld remainder
    to ``plain``, because that is the style G6.4 writes it in.  The GRID
    test may not read it that way: a pooled count names no form, so those
    cells are not proved point-free (Codex review of landing 2b.1, item
    4).
    """
    owed = 0
    for style in POINT_FREE_STYLES:
        if style in published:
            owed += published[style]
    return owed


def written_grid(fraction_widths, integer_valued, numeric, point_free):
    """The grid G5.2a step 1 and G5.3 read the ladder on, or -1 (landing 2b.1).

    ``grid_of``'s one width where it covers every numeric cell, and ALSO the
    one width ``f > 0`` of a column whose other numeric cells are all written
    with no point: a census naming that width alone, whose count and the
    NAMED point-free style count (``point_free``, the withheld share
    EXCLUDED -- an anonymous pool names no form) add up to every numeric
    cell.  A point-free cell is the
    grid point whose last ``f`` figures are zero, so such a column -- ``37``
    beside ``37.4``, ``0`` beside ``2.5`` -- is on the grid ``f`` too.  A
    whole-valued column answers -1: G5.4 already reads it on the integers.
    """
    if integer_valued:
        return -1
    figures = grid_of(fraction_widths, integer_valued, numeric)
    if figures > 0:
        return figures
    if len(fraction_widths) != 1:
        return commonest_width_grid(fraction_widths, numeric, point_free)
    for width in fraction_widths:
        try:
            figures = int(width)
        except (TypeError, ValueError):
            return -1
        if figures <= 0 or fraction_widths[width] + point_free != numeric:
            return -1
        return figures
    return -1


def commonest_width_grid(fraction_widths, numeric, point_free):
    """G5.2a step 1 on a census naming several widths: the commonest.

    The width the most cells are written at, ties to the wider, where
    every named width is positive and the named widths and the NAMED
    point-free style count together cover every numeric cell; -1
    otherwise, and -1 for a census that pools a width at all, since the
    pool may hold a width finer than the grid.
    """
    covered = point_free
    best = -1
    most = -1
    for width in sorted(fraction_widths):
        count = fraction_widths[width]
        covered += count
        if width == "(withheld)":
            return -1
        try:
            figures = int(width)
        except (TypeError, ValueError):
            return -1
        if figures <= 0:
            return -1
        if count > most or (count == most and figures > best):
            most = count
            best = figures
    if best <= 0 or covered != numeric:
        return -1
    return best


def grouped_enough(column, values, sizes, bands, integer_valued, numeric, floor):
    """As many cells at a thousand or more as the marks census counts -- G6.1.

    Plan P4-D185, written from the rule statement.  Only on a column whose
    every numeric cell is on one grid, naming no field width and no form
    but ``decimal`` and ``plain``.  ``C`` is the census's cells, named and
    pooled; ``K`` the cells whose values reach a thousand in size.  Where
    ``K < C``, the run of strata just below a thousand, from the highest
    down while their cells do not pass ``C - K``, takes the lowest free
    grid points of a thousand or more, in order, each below the value of
    the stratum above the run; where ``C < K < C + line``, the run from a
    thousand up, from the lowest while their cells do not pass ``K - C``,
    takes the highest free grid points below a thousand, in order, each
    above the value of the stratum below it.  A stratum moves only where
    its text is its own, is in the positive band, is never the first or
    the last, and the run moves whole or not at all.  Free points are
    looked for at most sixty-four past the run's own length, and a point
    whose text does not survive being read and written again is passed
    over.  Plan P4-D194: where the column holds a negative value, the count
    is taken again after that, and the same rule is asked of the negative
    strata by size
    -- a thousand read as minus a thousand, above read as below -- and
    written here that way rather than by turning the column over.
    """
    census = column.get("thousands_marks") or {}
    total = len(values)
    if total < 3 or not census:
        return values
    owed = sum(census.values())
    figures = grid_of(column.get("fraction_widths", {}), integer_valued, numeric)
    if figures < 0 or column.get("pad_widths"):
        return values
    if any(
        style not in ("decimal", "plain", "(withheld)")
        for style in column["numeric_styles"]
    ):
        return values
    reached = sum(
        sizes[place] for place in range(total) if abs(values[place]) >= 1000.0
    )
    texts = [grid_text(value, figures) for value in values]
    held = {}
    for text in texts:
        held[text] = held.get(text, 0) + 1
    unit = fractions.Fraction(1, 10 ** figures)
    thousand = fractions.Fraction(1000)

    def free_points(start, stride, count):
        found = []
        point = start
        looked = 0
        while len(found) < count and looked < count + 64:
            looked += 1
            spelt = _fraction_text(point, figures)
            point += stride
            if spelt in held or grid_text(float(spelt), figures) != spelt:
                continue
            found.append(float(spelt))
        return found if len(found) == count else None

    def side(sign, band):
        # ``sign`` 1 reads the positive side as written; -1 reads the
        # negative side by size, so "below a thousand" is "above minus a
        # thousand" and the run walks the other way through the strata.
        def size_of(place):
            return sign * values[place]

        def movable(place):
            return (
                0 < place < total - 1
                and held[texts[place]] == 1
                and bands[place] == band
            )

        order = list(range(total)) if sign > 0 else list(reversed(range(total)))
        run = []
        if reached < owed:
            wanted = owed - reached
            under = [p for p in order if size_of(p) < 1000.0]
            place_index = order.index(under[-1]) if under else -1
            while (
                wanted > 0
                and 0 <= place_index < total
                and movable(order[place_index])
                and sizes[order[place_index]] <= wanted
            ):
                run.insert(0, order[place_index])
                wanted -= sizes[order[place_index]]
                place_index -= 1
            if not run:
                return None
            points = free_points(sign * thousand, sign * unit, len(run))
            if points is None:
                return None
            beyond = order.index(run[-1]) + 1
            if beyond < total and sign * points[-1] >= size_of(order[beyond]):
                return None
        elif owed < reached < owed + max(floor, 2):
            wanted = reached - owed
            over = [p for p in order if size_of(p) >= 1000.0]
            if not over:
                return None
            place_index = order.index(over[0])
            while (
                wanted > 0
                and 0 <= place_index < total
                and movable(order[place_index])
                and sizes[order[place_index]] <= wanted
            ):
                run.append(order[place_index])
                wanted -= sizes[order[place_index]]
                place_index += 1
            if not run:
                return None
            points = free_points(
                sign * (thousand - unit), -sign * unit, len(run)
            )
            if points is None:
                return None
            points = list(reversed(points))
            before = order.index(run[0]) - 1
            if sign * points[0] <= size_of(order[before]):
                return None
        else:
            return None
        moved = list(values)
        for step, place in enumerate(run):
            moved[place] = points[step]
        return moved

    moved = side(1, "positive")
    if moved is None:
        moved = values
    if column.get("n_negative", 0) == 0:
        return moved
    values = moved
    reached = sum(
        sizes[place] for place in range(total) if abs(values[place]) >= 1000.0
    )
    texts = [grid_text(value, figures) for value in values]
    held = {}
    for text in texts:
        held[text] = held.get(text, 0) + 1
    turned = side(-1, "negative")
    return values if turned is None else turned


def separation_reaches():
    """The reaches of G6.5a's walks, in the order each round takes them.

    Plan P4-D183: every stratum inside its own share (0), then every
    stratum on its neighbours' ground (1), then every stratum by the
    distance its share is wide (2).  A function of its own so the frozen
    case's registered mutant can put back the order it replaced -- one
    walk reaching as far as it may, stratum by stratum -- and move cells.
    """
    return (0, 1, 2)


def finest_grid(fraction_widths):
    """The finest width a census names, or -1 -- G6.5a, amendment A-P4-55.

    Where the census names several widths, or one that does not cover
    every numeric cell, the separation walks the grid of the most figures
    any cell is written with: two values that read alike there ARE one
    number.  -1 for an empty census, or one holding a key that is not a
    run of figures.
    """
    if not fraction_widths:
        return -1
    finest = -1
    for width in fraction_widths:
        if not width or not all(letter in "0123456789" for letter in width):
            return -1
        finest = max(finest, int(width))
    return finest


def grid_of(fraction_widths, integer_valued, numeric):
    """Which grid every numeric cell of this column is written on -- G6.5a.

    The count of figures after the point, or -1 where the column is not
    on one grid and this pass may not act.  A census naming exactly one
    width AND COVERING EVERY NUMERIC CELL is that width; a census whose
    one width covers only some of them is not a whole-column grid, and
    which cell gets which is settled after the styles by G6.6.  An EMPTY
    census on a whole-valued column is the INTEGER grid: no cell carries
    a figure after the point, so there is no width to count, and reading
    that as "no grid" turns the pass off for every whole-valued
    column.

    ``numeric`` is the column's own count of numeric cells and is what
    the coverage test needs.  Review round 1 of this landing found this
    function without it, accepting any one-key census -- so a case whose
    one width covered 11 of 33 cells would have been called a grid here
    and refused by the implementation.

    A WHOLE-VALUED COLUMN IS ON THE INTEGER GRID WHATEVER ITS CENSUS
    SAYS (landing 2b.7, plan P4-D66.3).  ``integer_valued`` says every
    VALUE is whole and ``fraction_widths`` says how many figures each
    cell WRITES after its point, and a column exported as ``44.0``
    publishes both.  Reading the census here put such a column on the
    grid of TENTHS and the separation walk moved a stratum onto
    ``25.6``.  This read the census first and answered the integers
    only for an EMPTY one, which is the same defect the implementation
    carried at ``_pinned_fraction``.
    """
    if integer_valued:
        return 0
    if len(fraction_widths) != 1:
        return -1
    for width in fraction_widths:
        try:
            figures = int(width)
        except (TypeError, ValueError):
            return -1
        if fraction_widths[width] != numeric:
            return -1
        return figures
    return -1


def at_width(sign, figures, place, width):
    """The figures written with EXACTLY ``width`` of them after the point.

    Short of the width the value is padded, which costs nothing; past it
    the value is ROUNDED, and TIES GO TO EVEN (plan P4-D4.5), which is
    not the tie rule the rest of this method uses.

    WHAT IS ROUNDED is the value's shortest round-trip decimal figures
    and not the binary64 itself -- the method states this where it
    states the tie, and the two differ: `2.675` is held as a double a
    shade below two and sixty-seven and a half hundredths, so rounding
    the double gives `2.67` while rounding the figures `2675` gives the
    tie, and the tie goes to even, so `2.68`.

    COMPUTED AS AN EXACT RATIONAL, on purpose. The shipped generator
    walks the digit string and carries by hand; doing the same here
    would agree with it for the reason a transcription agrees, which is
    no reason at all. This takes the figures as a fraction, scales by
    ten to the width, and compares the remainder against one half in
    exact arithmetic -- a different route to the same stated rule, which
    is what makes agreement evidence. Review round 2 of the
    integer-grid landing asked for exactly that.
    """
    whole = fractions.Fraction(int(figures or "0"), 1)
    exact = whole * fractions.Fraction(10) ** (place - len(figures))
    scaled = exact * fractions.Fraction(10) ** width
    below = scaled.numerator // scaled.denominator
    rest = scaled - below
    half = fractions.Fraction(1, 2)
    if rest > half:
        carried = below + 1
    elif rest < half:
        carried = below
    elif below % 2 == 0:
        carried = below
    else:
        carried = below + 1
    body = str(carried)
    if width == 0:
        return "%s%s." % (sign, body)
    body = body.rjust(width + 1, "0")
    cut = len(body) - width
    return "%s%s.%s" % (sign, body[:cut], body[cut:])


def grid_text(value, figures):
    """The text the writer will write this value at, on the grid -- G6.6.

    THE WRITER'S OWN RULE AND NOT A SECOND ONE.  A function that
    predicts what another will write, by writing it a second way, is the
    shape this landing's first review round found here.
    """
    digits, decpt = shortest_round_trip(value)
    sign = "-" if value < 0 or (value == 0 and math.copysign(1.0, value) < 0) else ""
    return at_width(sign, digits, decpt, figures)


def _snapped_fraction(exact, figures):
    """An exact decimal value snapped to the grid, ties to even."""
    scaled = exact * fractions.Fraction(10) ** figures
    below = scaled.numerator // scaled.denominator
    rest = scaled - below
    half = fractions.Fraction(1, 2)
    if rest > half:
        below = below + 1
    elif rest == half and below % 2:
        below = below + 1
    return fractions.Fraction(below, 10 ** figures)


def _fraction_text(point, figures):
    """A grid point, held exactly, written at ``figures``."""
    units = point * fractions.Fraction(10) ** figures
    whole = units.numerator // units.denominator
    sign = "-" if whole < 0 else ""
    body = str(abs(whole))
    if figures == 0:
        return "%s%s." % (sign, body)
    body = body.rjust(figures + 1, "0")
    cut = len(body) - figures
    return "%s%s.%s" % (sign, body[:cut], body[cut:])


def apart_inside(value, figures, band, share, ends, written, reach=64, whole=None):
    """The nearest free point of the grid inside this share -- G6.5a.

    Outward one grid step at a time from the value's own grid TEXT read
    back -- not from the value -- the LOWER of two equally distant
    candidates first so that two implementations reading the method
    choose the same point, and at most sixty-four steps out. None means
    no candidate within those sixty-four survived the refusals, which
    is not the same as the share holding no free point.  Refused where the text is already written, where it
    leaves the share, where it leaves the published ends, or where it
    would cross into another sign band.
    """
    # THE STEPS ARE COUNTED ON THE GRID, and this is computed as an
    # exact rational rather than by walking a digit string: the anchor
    # as a fraction, plus `step` times one unit of the last place. The
    # shipped generator counts in whole grid units on the text; taking
    # a different route to the same stated rule is what keeps this file
    # a reading of the method rather than a copy of the code. Adding
    # `10 ** -figures` to a double instead accumulates, and at eleven
    # figures a candidate the method bounds at sixty-four units came
    # back seventy out.
    # THE GRID STEP MUST BE A FINITE DOUBLE GREATER THAN NOUGHT, which
    # the method states and which exact arithmetic cannot notice on its
    # own: at 324 figures `10 ** -figures` UNDERFLOWS to zero as a
    # double, so a column described that finely has no grid a twin can
    # walk. A fraction never underflows, so this file sailed past the
    # rule and answered where the method requires nothing (review round
    # 5 of the integer-grid landing). The rule is about the step a
    # program can hold, so it is asked of the double.
    step_as_double = 10.0 ** -figures if figures else 1.0
    if step_as_double <= 0.0 or not math.isfinite(step_as_double):
        return None
    unit = fractions.Fraction(1, 10 ** figures)
    digits, decpt = shortest_round_trip(value)
    seated = fractions.Fraction(int(digits or "0"), 1)
    seated = seated * fractions.Fraction(10) ** (decpt - len(digits))
    if value < 0:
        seated = -seated
    placed = _snapped_fraction(seated, figures)
    limit = reach
    reach = 1
    while reach <= limit:
        for step in (-reach, reach):
            point = placed + step * unit
            spelt = _fraction_text(point, figures)
            try:
                candidate = float(spelt)
            except ValueError:
                continue
            if not math.isfinite(candidate):
                continue
            if grid_text(candidate, figures) != spelt:
                continue
            if spelt in written:
                continue
            # THE STRATUM'S OWN KIND, where the column writes some cells
            # with no point (amendment A-P4-55): a whole value moves only
            # onto a whole number and a fractional one only off them.
            if whole is not None and float(candidate).is_integer() != whole:
                continue
            if band == "negative" and candidate >= 0.0:
                continue
            if band == "positive" and candidate <= 0.0:
                continue
            if band == "zero":
                return None
            if share is not None:
                low = min(share[0], share[1])
                high = max(share[0], share[1])
                if candidate < low or candidate > high:
                    continue
            if ends is not None and (candidate < ends[0] or candidate > ends[1]):
                continue
            return candidate
        reach = reach + 1
    return None


def _exact_decimal(value):
    """A double's shortest round-trip decimal, held exactly."""
    digits, decpt = shortest_round_trip(value)
    exact = fractions.Fraction(int(digits or "0"), 1)
    exact = exact * fractions.Fraction(10) ** (decpt - len(digits))
    return -exact if value < 0 else exact


def _on_grid(value, figures):
    """Whether a double's grid text at ``figures`` reads back as itself."""
    text = grid_text(value, figures)
    try:
        return float(text) == value
    except ValueError:
        return False


def _band_holds(band, value):
    return (
        (band != "zero" or value == 0)
        and (band != "negative" or value < 0)
        and (band != "positive" or value > 0)
    )


def saturated_grid(wanted, figures, total, bands, ladder):
    """The points of a grid with no spare one, in order, or None -- G6.5a.

    Plan P4-D147 on the integers, and plan P4-D176 on every written grid:
    where the strata number ``wanted``, both published ends are points of
    the grid and the points from one to the other number ``wanted``, the
    strata take those points in ascending order, unless a sign band would
    not hold its point.  The points are counted as exact decimals, so no
    step drifts.
    """
    if ladder is None or wanted is None or total != wanted or total < 2:
        return None
    if figures == 0:
        if not (float(ladder[0]).is_integer() and float(ladder[-1]).is_integer()):
            return None
        if ladder[-1] - ladder[0] + 1 != wanted:
            return None
        filled = [float(ladder[0] + place) for place in range(total)]
    else:
        if not (_on_grid(ladder[0], figures) and _on_grid(ladder[-1], figures)):
            return None
        unit = fractions.Fraction(1, 10 ** figures)
        low = _exact_decimal(ladder[0])
        high = _exact_decimal(ladder[-1])
        if (high - low) / unit + 1 != wanted:
            return None
        filled = [
            float(_fraction_text(low + place * unit, figures))
            for place in range(total)
        ]
    if all(_band_holds(bands[place], filled[place]) for place in range(total)):
        return filled
    return None


def saturated_levels(
    wanted, figures, values, bands, ladder, mode, point_free, integer_valued
):
    """The published levels themselves, in order, or None -- G6.5a.

    Plan P4-D178.  The different numbers the hundred and one rungs and the
    mode name, or, where those are more than ``wanted``, the numbers two
    rungs or more name with the two ends and the mode; where that set
    holds exactly ``wanted`` numbers, every one a point of the grid, the
    strata take them in ascending order -- unless a sign band would not
    hold its number, a stratum not in the zero band would take nought, or,
    on a column writing some cell point-free, a stratum would change
    whether its number has a point-free spelling.
    """
    total = len(values)
    if ladder is None or wanted is None or total != wanted or total < 2:
        return None
    named = {}
    for rung in ladder:
        named[rung] = named.get(rung, 0) + 1
    levels = set(named)
    if mode is not None:
        levels.add(mode)
    if len(levels) != wanted:
        levels = {rung for rung in named if named[rung] >= 2}
        levels.update((ladder[0], ladder[-1]))
        if mode is not None:
            levels.add(mode)
        if len(levels) != wanted:
            return None
    given = sorted(levels)
    for place, value in enumerate(given):
        if figures == 0 and not float(value).is_integer():
            return None
        if figures > 0 and not _on_grid(value, figures):
            return None
        if not _band_holds(bands[place], value):
            return None
        if bands[place] != "zero" and value == 0:
            return None
        if point_free and (
            (point_free_spelling(value, integer_valued) is None)
            != (point_free_spelling(values[place], integer_valued) is None)
        ):
            return None
    return [float(value) for value in given]


def twice_written(column, values, sizes, bands, ladder, integer_valued, numeric, demand):
    """A whole number written two ways is held by two strata -- G6.5a, plan P4-D193.

    Read from the method: on a column at ONE fraction width of a figure or
    more beside point-free cells, in the ``decimal`` and ``plain`` forms
    only, with no field width, no mark between thousands and no second
    negative notation, whose strata are its spellings and no fewer than its
    numbers, and whose grid texts are not already settled (as many texts
    as numbers, a text held twice naming a whole number, none three
    times): first the FILL, where the grid points from ``min`` to ``max``
    outside every published empty pair number exactly the count of
    numbers -- the strata take them in order, ``S`` whole points each
    taken by two neighbours, the assignment moving the strata fewest grid
    units in all, the lower point at the first stratum where two differ,
    kept only where the strata with point-free spellings hold the
    point-free demand; then the MERGE, where the texts still outnumber the
    count -- a stratum holding a number that is not whole beside a
    stratum holding a whole number, both texts their holders' own, takes
    the whole number, nearest pairs first, lower pair first, lower mover
    first, no stratum twice, never the ends, the sign band kept.
    """
    wanted = column.get("n_distinct_values")
    total = len(values)
    widths = column.get("fraction_widths", {})
    if integer_valued or wanted is None or ladder is None or total < 2:
        return values
    if column.get("n_distinct") != total or total < wanted:
        return values
    if len(widths) != 1 or column.get("pad_widths") or column.get("thousands_marks"):
        return values
    if any(count > 0 for count in column.get("negative_notations", {}).values()):
        return values
    if any(
        count > 0 and style not in ("decimal", "plain")
        for style, count in column["numeric_styles"].items()
    ):
        return values
    if sum(widths.values()) >= numeric:
        return values
    key = next(iter(widths))
    if not (key.isdigit() and int(key) >= 1):
        return values
    figures = int(key)
    texts = [grid_text(value, figures) for value in values]

    def settled(spelt):
        counts = {}
        for text in spelt:
            counts[text] = counts.get(text, 0) + 1
        if len(counts) != wanted:
            return False
        return all(
            n == 1 or (n == 2 and float(text).is_integer())
            for text, n in counts.items()
        )

    if settled(texts):
        return values
    surplus = total - wanted
    unit = fractions.Fraction(1, 10 ** figures)
    moved = list(values)
    if _on_grid(ladder[0], figures) and _on_grid(ladder[-1], figures):
        low = _exact_decimal(ladder[0])
        high = _exact_decimal(ladder[-1])
        exact_points = []
        point = low
        while point <= high and len(exact_points) <= wanted:
            number = float(_fraction_text(point, figures))
            if not any(
                pair[0] < number < pair[1] for pair in column.get("empty_edges", [])
            ):
                exact_points.append(point)
            point = point + unit
        if len(exact_points) == wanted:
            points = [float(_fraction_text(p, figures)) for p in exact_points]
            anchors = [
                _snapped_fraction(_exact_decimal(float(t)), figures) for t in texts
            ]
            memo = {}

            def least(place, spot, twice):
                # The fewest grid units the strata from ``place`` on move,
                # this stratum on ``points[spot]``; None where none fits.
                if (place, spot, twice) in memo:
                    return memo[(place, spot, twice)]
                answer = None
                if _band_holds(bands[place], points[spot]):
                    here = abs(exact_points[spot] - anchors[place]) / unit
                    if place == total - 1:
                        if spot == wanted - 1:
                            answer = here
                    else:
                        ways = []
                        if not twice and float(points[spot]).is_integer() and place - spot < surplus:
                            nxt = least(place + 1, spot, True)
                            if nxt is not None:
                                ways.append(nxt)
                        if spot + 1 < wanted:
                            nxt = least(place + 1, spot + 1, False)
                            if nxt is not None:
                                ways.append(nxt)
                        if ways:
                            answer = here + min(ways)
                memo[(place, spot, twice)] = answer
                return answer

            import sys as _sys

            _sys.setrecursionlimit(max(_sys.getrecursionlimit(), 10 * total + 1000))
            if least(0, 0, False) is not None:
                given = [points[0]]
                spot = 0
                twice = False
                for place in range(total - 1):
                    same = None
                    if not twice and float(points[spot]).is_integer() and place - spot < surplus:
                        same = least(place + 1, spot, True)
                    step = least(place + 1, spot + 1, False) if spot + 1 < wanted else None
                    if same is not None and (step is None or same <= step):
                        twice = True
                    else:
                        spot = spot + 1
                        twice = False
                    given.append(points[spot])
                carried = sum(
                    sizes[place]
                    for place in range(total)
                    if point_free_spelling(given[place], integer_valued) is not None
                )
                if carried >= demand:
                    moved = given
    texts = [grid_text(value, figures) for value in moved]
    counts = {}
    for text in texts:
        counts[text] = counts.get(text, 0) + 1
    owed = len(counts) - wanted
    if owed <= 0 or total < 3:
        return moved
    pairs = []
    for place in range(total - 1):
        for mover, keeper in ((place, place + 1), (place + 1, place)):
            if mover in (0, total - 1):
                continue
            if not float(moved[keeper]).is_integer() or float(moved[mover]).is_integer():
                continue
            if counts[texts[keeper]] != 1 or counts[texts[mover]] != 1:
                continue
            if not _band_holds(bands[mover], moved[keeper]):
                continue
            apart = abs(
                _snapped_fraction(_exact_decimal(float(texts[keeper])), figures)
                - _snapped_fraction(_exact_decimal(float(texts[mover])), figures)
            ) / unit
            pairs.append((apart, place, mover, keeper))
    merged = list(moved)
    taken = set()
    for apart, place, mover, keeper in sorted(pairs):
        if owed <= 0:
            break
        if mover in taken or keeper in taken:
            continue
        merged[mover] = moved[keeper]
        taken.update((mover, keeper))
        owed -= 1
    return merged


def apart_values(
    wanted, figures, values, sizes, starts, bands, ladder, numeric,
    mode=None, point_free=False, integer_valued=False, keep_whole=False,
):
    """Two strata are two cells, so they are written two ways -- G6.5a.

    Runs after G6.4's point-free carrier walk, which can itself land two
    strata on one text, and before the held-back pool.  Only a stratum
    whose text another stratum also holds may move; never the pinned
    ends, whose values are the published ``min`` and ``max``; never the
    zero stratum.  It stops as soon as the count of different texts
    reaches the published ``n_distinct_values``.

    A GRID WITH NO SPARE POINT IS FILLED, NOT WALKED (plans P4-D147 and
    P4-D176, `saturated_grid`), and A COLUMN WHOSE PUBLISHED LEVELS ARE
    ITS STRATA TAKES THEM (plan P4-D178, `saturated_levels`); where
    neither answers, the walk runs.
    """
    if figures < 0:
        return values
    total = len(values)
    if total < 2:
        return values
    filled = saturated_grid(wanted, figures, total, bands, ladder)
    if filled is not None:
        return filled
    filled = saturated_levels(
        wanted, figures, values, bands, ladder, mode, point_free,
        integer_valued,
    )
    if filled is not None:
        return filled
    moved = list(values)
    texts = [grid_text(value, figures) for value in moved]
    held = {}
    for text in texts:
        held[text] = held.get(text, 0) + 1
    # The size of the map IS the count of different texts: a stratum
    # moves only while its own text has two or more holders, so no key
    # falls to nought. A tally beside it would believe an addition
    # rather than the column.
    ends = None if ladder is None else (ladder[0], ladder[-1])

    def walk(reach):
        for place in range(total):
            if wanted is not None and len(held) >= wanted:
                return
            text = texts[place]
            if held[text] <= 1:
                continue
            if place == 0 or (place == total - 1 and total >= 2):
                continue
            if bands[place] == "zero":
                continue
            share = None
            if ladder is not None:
                share = (
                    ladder_at(ladder, starts[place], numeric),
                    ladder_at(ladder, starts[place] + sizes[place], numeric),
                )
            kind = float(moved[place]).is_integer() if keep_whole else None
            want = apart_inside(
                moved[place], figures, bands[place], share, ends, held,
                64, kind,
            )
            if want is None and share is not None and reach >= 1:
                # The neighbours' ground: the share widened by its own
                # width on either side (amendment A-P4-55).
                width = abs(share[1] - share[0])
                want = apart_inside(
                    moved[place], figures, bands[place],
                    (share[0] - width, share[1] + width), ends, held, 64, kind,
                )
            if want is None and share is not None and reach >= 2:
                # And by distance: as many grid steps as the share is wide,
                # at most sixty-four, anywhere between the published ends.
                width = abs(share[1] - share[0])
                unit = 1.0
                for _each in range(figures):
                    unit = unit / 10.0
                steps = int(width / unit) + 1 if unit > 0.0 else 1
                want = apart_inside(
                    moved[place], figures, bands[place], None, ends, held,
                    min(steps, 64), kind,
                )
            if want is None:
                continue
            fresh = grid_text(want, figures)
            held[text] = held[text] - 1
            held[fresh] = held.get(fresh, 0) + 1
            texts[place] = fresh
            moved[place] = want

    # THREE ROUNDS, AND IN EACH ROUND EVERY STRATUM INSIDE ITS OWN SHARE
    # FIRST (amendment A-P4-55, plan P4-D183): the share walk, then the
    # neighbours' ground, then the distance walk, the count asked after
    # each; a round that moves nothing ends it.
    for _round in range(3):
        before_round = len(held)
        for reach in separation_reaches():
            walk(reach)
            if wanted is not None and len(held) >= wanted:
                break
        if wanted is not None and len(held) >= wanted:
            break
        if len(held) == before_round:
            break
    return moved


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


# -- how a date is WRITTEN (method G7.5, landing 2b.6) ----------------
#
# The owner reversed decision 5 on 2026-09-15: a twin datetime cell is
# written in the MEMBER that read the real column rather than in ISO.
# What follows is that rule, written from the method's own per-member
# table and from nothing else -- this file imports none of the code it
# checks, so the writing rule exists here twice on purpose.

MONTH_NAMES = (
    ("jan", "january"), ("feb", "february"), ("mar", "march"),
    ("apr", "april"), ("may", "may"), ("jun", "june"),
    ("jul", "july"), ("aug", "august"), ("sep", "september"),
    ("oct", "october"), ("nov", "november"), ("dec", "december"),
)

TEXTUAL_MEMBERS = ("textual-day-first-date", "textual-month-first-date")
VARIABLE_WIDTH_MEMBERS = (
    "month-first-date", "day-first-date",
    "two-digit-month-first-date", "two-digit-day-first-date",
    "month-first-datetime", "day-first-datetime",
)
TWO_FIGURE_MEMBERS = (
    "two-digit-month-first-date", "two-digit-day-first-date",
    "dotted-two-digit-month-first-date", "dotted-two-digit-day-first-date",
)
DOTTED_MEMBERS = (
    "dotted-month-first-date", "dotted-day-first-date",
    "dotted-two-digit-month-first-date", "dotted-two-digit-day-first-date",
)
MONTH_FIRST_MEMBERS = (
    "month-first-date", "dotted-month-first-date",
    "two-digit-month-first-date", "dotted-two-digit-month-first-date",
    "month-first-datetime", "textual-month-first-date",
)
DAY_FIRST_MEMBERS = (
    "day-first-date", "dotted-day-first-date",
    "two-digit-day-first-date", "dotted-two-digit-day-first-date",
    "day-first-datetime", "textual-day-first-date",
)
DEFAULT_WIDTH = "padded"
DEFAULT_NAME_STYLE = "title-abbreviated-space-no-comma"


def month_spelling(month, length, case):
    """One month written as a NAME: the inverse of the reader's own."""
    short, whole = MONTH_NAMES[month - 1]
    name = whole if length == "full" else short
    if case == "upper":
        return name.upper()
    if case == "lower":
        return name.lower()
    return name[:1].upper() + name[1:].lower()


def field_text(value, padded):
    """One numeric field at the width its style asks for."""
    if padded or value >= 10:
        return f"{value:02d}"
    return f"{value}"


def pair_widths(width):
    """One width word as a padding decision per field (G7.5, P4-D132).

    A joint word decides both fields; a one-field word decides its own
    field and leaves the other padded.
    """
    if width == "unpadded":
        return False, False
    if width == "first-padded":
        return True, False
    if width == "second-padded":
        return False, True
    if width == "first-field-unpadded":
        return False, True
    if width == "second-field-unpadded":
        return True, False
    return True, True


def name_parts(style):
    """One joint month-name style word, taken back apart."""
    parts = style.split("-")
    comma = "no-comma" if parts[3] == "no" else "comma"
    return parts[0], parts[1], parts[2], comma


def written_date(year, month, day, member, width=DEFAULT_WIDTH,
                 name_style=DEFAULT_NAME_STYLE):
    """One day written the way its member's own source wrote it (G7.5)."""
    if member == "compact-date":
        return f"{year:04d}{month:02d}{day:02d}"
    if member in ("slashed-iso-date", "slashed-iso-datetime"):
        return f"{year:04d}/{month:02d}/{day:02d}"
    if member in TEXTUAL_MEMBERS:
        case, length, mark, comma = name_parts(name_style)
        name = month_spelling(month, length, case)
        between = " " if mark == "space" else "-"
        day_text = field_text(day, width != "unpadded")
        if member == "textual-day-first-date":
            return f"{day_text}{between}{name}{between}{year:04d}"
        tail = "," if comma == "comma" else ""
        return f"{name}{between}{day_text}{tail}{between}{year:04d}"
    if member not in MONTH_FIRST_MEMBERS and member not in DAY_FIRST_MEMBERS:
        return f"{year:04d}-{month:02d}-{day:02d}"
    dotted = member in DOTTED_MEMBERS
    between = "." if dotted else "/"
    first_padded, second_padded = pair_widths(width)
    if dotted:
        # Contract C6-22: the dotted families are read padded and only
        # padded, because `1.2.2024` is a version identifier.
        first_padded = True
        second_padded = True
    first_value, second_value = (month, day)
    if member in DAY_FIRST_MEMBERS:
        first_value, second_value = (day, month)
    year_text = f"{year:04d}"
    if member in TWO_FIGURE_MEMBERS:
        year_text = f"{year % 100:02d}"
    return (
        f"{field_text(first_value, first_padded)}{between}"
        f"{field_text(second_value, second_padded)}{between}{year_text}"
    )


def precision_form(ordinal, resolution, time_precision, subsecond_digits,
                   mark="T", member="iso-datetime", width=DEFAULT_WIDTH,
                   name_style=DEFAULT_NAME_STYLE, marker="upper"):
    """The cell text of method section G7.5, before the offset suffix.

    ``mark`` is the character between the day and the clock that the
    column's separator census gives this rank (plan P4-D39); ``T`` where
    the census names none, which is every case frozen before it existed.
    ``member``, ``width``, ``name_style`` and ``marker`` are the
    reversal of owner decision 5 (landing 2b.6): the date half is
    written in the member that read the real column, at the conventions
    that rank was allocated. Their defaults are the ISO member's own
    spelling, which is what every case frozen before the reversal used.
    """
    if resolution == "quarter":
        year = 1970 + ordinal // 4
        quarter = ordinal % 4 + 1
        letter = "q" if marker == "lower" else "Q"
        return f"{year:04d}-{letter}{quarter}"
    if resolution == "month":
        year = 1970 + ordinal // 12
        return f"{year:04d}-{ordinal % 12 + 1:02d}"
    if resolution == "date":
        year, month, day = civil_from_days(ordinal)
        return written_date(year, month, day, member, width, name_style)
    days, rest = divmod(ordinal, 86400)
    year, month, day = civil_from_days(days)
    hours, rest = divmod(rest, 3600)
    minutes, seconds = divmod(rest, 60)
    half = written_date(year, month, day, member, width, name_style)
    stem = f"{half}{mark}{hours:02d}:{minutes:02d}"
    if time_precision == "minute":
        return stem
    stem = f"{stem}:{seconds:02d}"
    if time_precision == "second":
        return stem
    # The fractional digits are zeros: the profile publishes how MANY
    # digits the finest cell carried and nothing about their values, so
    # any other digits would be an invented fact.
    return stem + "." + "0" * subsecond_digits


CLOCK_STEP = {"hh-mm": 60, "hh-mm-ss": 1}
CLOCK_CAPACITY = {"hh-mm": 24 * 60, "hh-mm-ss": 24 * 60 * 60}


def clock_ordinal_of(text, form):
    """One clock cell as its place in its form's own unit (G7A.1).

    Minutes of day for `hh-mm`, seconds of day for `hh-mm-ss`.  The
    reader is deliberately exact and NOTHING is trimmed first: what this
    role publishes are the cells themselves, character for character.
    """
    if form not in CLOCK_STEP:
        raise AssertionError(f"{form!r} is not one of the two clock forms")
    wanted = 8 if form == "hh-mm-ss" else 5
    if len(text) != wanted:
        raise AssertionError(f"{text!r} is not a cell of form {form}")
    fields = text.split(":")
    if len(fields) != (3 if form == "hh-mm-ss" else 2):
        raise AssertionError(f"{text!r} is not a cell of form {form}")
    numbers = []
    for field in fields:
        if len(field) != 2 or not field.isdigit():
            raise AssertionError(f"{text!r} is not a cell of form {form}")
        numbers.append(int(field))
    if numbers[0] > 23:
        raise AssertionError(f"{text!r} has an hour above 23")
    for rest in numbers[1:]:
        if rest > 59:
            raise AssertionError(f"{text!r} has a field above 59")
    if form == "hh-mm":
        return numbers[0] * 60 + numbers[1]
    return numbers[0] * 3600 + numbers[1] * 60 + numbers[2]


def clock_spelling_of(ordinal, form):
    """The one spelling of one ordinal in one form (G7A.1).

    The inverse of `clock_ordinal_of`, zero-padded to two digits a
    field, so a producer and a generator cannot spell one time two ways.
    """
    if form not in CLOCK_STEP:
        raise AssertionError(f"{form!r} is not one of the two clock forms")
    if ordinal < 0 or ordinal >= CLOCK_CAPACITY[form]:
        raise AssertionError(f"{ordinal} is outside the space of {form}")
    if form == "hh-mm":
        return "%02d:%02d" % (ordinal // 60, ordinal % 60)
    rest = ordinal % 3600
    return "%02d:%02d:%02d" % (ordinal // 3600, rest // 60, rest % 60)


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


def census_weights(census, permitted):
    """How many ranks each written form is owed (method G7.5, P4-D131).

    Every form of ``permitted`` the census names, at its published count.
    A census of written forms names no pool, so nothing is split.
    """
    return {name: census[name] for name in permitted if name in census}


def rotated(weights, count):
    """One form per place, spent by the smooth weighted rotation (G7.5).

    At each place every name's weight is added to its running credit,
    the name with the most credit is taken -- the earliest in sorted
    order on a tie -- and the total is taken back from it.  No word is
    drawn.
    """
    names = sorted(weights)
    if not names or count <= 0:
        return []
    owed = dict(weights)
    total = sum(owed.values())
    if total < count:
        top = max(names, key=lambda name: (owed[name], [-ord(c) for c in name]))
        owed[top] = owed[top] + (count - total)
        total = count
    credit = {name: 0 for name in names}
    spread = []
    for _place in range(count):
        for name in names:
            credit[name] = credit[name] + owed[name]
        best = names[0]
        for name in names:
            if credit[name] > credit[best]:
                best = name
        credit[best] = credit[best] - total
        spread.append(best)
    return spread


def commonest_of(census, default):
    """The form most of a column's cells wrote, or a default (G7.5)."""
    best = ""
    for name in sorted(census):
        if name == "(withheld)":
            continue
        if not best or census[name] > census[best]:
            best = name
    return best or default


FIELD_WIDTH_BOTH = ("padded", "unpadded", "first-padded", "second-padded")
FIELD_WIDTH_FIRST = ("first-field-padded", "first-field-unpadded")
FIELD_WIDTH_SECOND = ("second-field-padded", "second-field-unpadded")
FIELD_WIDTH_STYLES_ONE_FIELD = ("padded", "unpadded")
QUARTER_MARKER_CASES = ("upper", "lower")
ZULU_CASES = ("upper", "lower")


def month_name_styles_of(member, length_words=("abbreviated", "full")):
    """The joint month-name styles one member's cells can show, at the
    given lengths: ``("either",)`` for a cell of May (P4-D133)."""
    built = []
    for case in ("upper", "title", "lower"):
        for length in length_words:
            for mark in ("space", "hyphen"):
                for comma in ("comma", "no-comma"):
                    if member == "textual-day-first-date" and comma == "comma":
                        continue
                    built.append(f"{case}-{length}-{mark}-{comma}")
    return tuple(built)


def reserved(weights, count, floor):
    """One form per place, every named form given its published least
    (method G7.5, P4-D132).

    The rotation alone where it gives every form with a positive weight at
    least min(weight, line), line being the floor and never below two.
    Otherwise, unless those leasts come to more than the places: reserve
    the leasts, share the places left by the rotation over what each form
    is owed beyond its least (over the leasts where nobody is owed more),
    and spread the finished counts by the rotation.
    """
    spread = rotated(weights, count)
    line = max(floor, 2)
    least = {name: min(weight, line) for name, weight in weights.items() if weight > 0}
    if all(spread.count(name) >= need for name, need in least.items()):
        return spread
    if sum(least.values()) > count:
        return spread
    beyond = {name: weights[name] - need for name, need in least.items() if weights[name] > need}
    for name in rotated(beyond or dict(least), count - sum(least.values())):
        least[name] += 1
    return rotated(least, count)


def joint_width_of(census):
    """The commonest joint word; else the joint word of the commonest
    first-field and second-field words, a field with none padded (P4-D132)."""
    joint = commonest_of(census_weights(census, FIELD_WIDTH_BOTH), "")
    if joint:
        return joint
    first = commonest_of(census_weights(census, FIELD_WIDTH_FIRST), "first-field-padded")
    second = commonest_of(census_weights(census, FIELD_WIDTH_SECOND), "second-field-padded")
    pads = (first == "first-field-padded", second == "second-field-padded")
    return {(True, True): "padded", (True, False): "first-padded",
            (False, True): "second-padded", (False, False): "unpadded"}[pads]


def field_weights(census, which):
    """A one-field class's weights: its own two words where the census counts
    them, else the joint words' padding of that field, summed (P4-D132)."""
    words = FIELD_WIDTH_FIRST if which == 1 else FIELD_WIDTH_SECOND
    owed = census_weights(census, words)
    if owed:
        return owed
    for name in FIELD_WIDTH_BOTH:
        if name in census:
            padded = pair_widths(name)[which - 1]
            word = words[0] if padded else words[1]
            owed[word] = owed.get(word, 0) + census[name]
    return owed


def written_fields(column, ordinals, offsets, parsed, space, resolution):
    """The month and day every rank will WRITE (method G7.5, 2b.6).

    Asked of the cell about to be written and not of the ordinal alone:
    the two ends are written from their own published fields, and a rank
    of a column on the shared clock is written on its own offset's wall
    clock, which can carry it into another day.
    """
    fields = []
    for rank in range(parsed):
        if resolution in ("quarter", "month"):
            fields.append((1, 1))
            continue
        end = None
        if rank == 0:
            end = column["earliest"]
        elif rank == parsed - 1 and parsed >= 2:
            end = column["latest"]
        if end is not None and len(end) >= 10:
            fields.append((int(end[5:7]), int(end[8:10])))
            continue
        local = ordinals[rank]
        if (
            column["datetimes_read_at"] == "utc"
            and resolution == "datetime"
            and space != "date"
        ):
            local = local + offset_form(offsets[rank])[1]
        day_number = local if space == "date" or resolution != "datetime" else local // 86400
        _year, month, day = civil_from_days(day_number)
        fields.append((month, day))
    return fields


def written_styles(column, fields, parsed, resolution, offsets, floor=CASE_SMALL_CELL_FLOOR):
    """The four written forms every rank takes (method G7.5, 2b.6).

    WIDTHS (P4-D132): a rank whose two numeric fields are both below ten
    takes a joint word; one whose first field alone is, a first-field word
    written as ``padded`` or ``unpadded``; one whose second alone is, a
    second-field word likewise -- first and second in the member's own
    field order.  A textual member's day is its one field.  A class with no
    count of its own takes ``field_weights``; a rank showing nothing takes
    ``joint_width_of``.  NAMES (P4-D133): a rank of May takes the census's
    ``either`` words and every other rank its words naming a length; a
    class with none takes the other's words, an ``either`` word at the
    abbreviated length or a named length as ``either``.  Every class is
    spent by ``reserved``.  Markers over every quarter rank and zulu cases
    over the ranks carrying ``Z``, by ``reserved`` too.
    """
    member = column["format"]
    widths_census = column.get("date_field_widths", {})
    names_census = column.get("month_name_styles", {})
    marker_census = column.get("quarter_marker_case", {})
    zulu_census = column.get("zulu_case", {})
    width_fallback = joint_width_of(widths_census)
    name_fallback = commonest_of(names_census, DEFAULT_NAME_STYLE)
    widths = [width_fallback] * parsed
    if widths_census:
        both, first, second = [], [], []
        for rank, (month, day) in enumerate(fields):
            if member in TEXTUAL_MEMBERS:
                if day < 10:
                    first.append(rank)
                continue
            low = (month < 10, day < 10)
            if member in DAY_FIRST_MEMBERS:
                low = (day < 10, month < 10)
            if low == (True, True):
                both.append(rank)
            elif low[0]:
                first.append(rank)
            elif low[1]:
                second.append(rank)
        if member in TEXTUAL_MEMBERS:
            weights = census_weights(widths_census, FIELD_WIDTH_STYLES_ONE_FIELD) or {width_fallback: 1}
            for rank, form in zip(first, reserved(weights, len(first), floor)):
                widths[rank] = form
        else:
            weights = census_weights(widths_census, FIELD_WIDTH_BOTH) or {width_fallback: 1}
            for rank, form in zip(both, reserved(weights, len(both), floor)):
                widths[rank] = form
            for which, ranks in ((1, first), (2, second)):
                words = FIELD_WIDTH_FIRST if which == 1 else FIELD_WIDTH_SECOND
                owed = field_weights(widths_census, which) or {words[0]: 1}
                for rank, form in zip(ranks, reserved(owed, len(ranks), floor)):
                    widths[rank] = "unpadded" if form.endswith("-unpadded") else "padded"
    names = [name_fallback] * parsed
    if names_census:
        resolved = month_name_styles_of(member)
        either = month_name_styles_of(member, ("either",))
        may = [rank for rank, (month, _day) in enumerate(fields) if month == 5]
        rest = [rank for rank, (month, _day) in enumerate(fields) if month != 5]
        for places, words, others, length in (
            (rest, resolved, either, "abbreviated"),
            (may, either, resolved, "either"),
        ):
            owed = census_weights(names_census, words)
            if not owed:
                for name in others:
                    if name in names_census:
                        case, _length, mark, comma = name_parts(name)
                        moved = f"{case}-{length}-{mark}-{comma}"
                        owed[moved] = owed.get(moved, 0) + names_census[name]
            if not owed:
                continue
            for rank, form in zip(places, reserved(owed, len(places), floor)):
                names[rank] = form
    markers = [commonest_of(marker_census, "upper")] * parsed
    weights = census_weights(marker_census, QUARTER_MARKER_CASES)
    if weights and resolution == "quarter":
        for rank, form in enumerate(reserved(weights, parsed, floor)):
            markers[rank] = form
    zulus = [commonest_of(zulu_census, "upper")] * parsed
    weights = census_weights(zulu_census, ZULU_CASES)
    places = [rank for rank in range(parsed) if offsets[rank] == "Z"]
    if weights and places:
        for rank, form in zip(places, reserved(weights, len(places), floor)):
            zulus[rank] = form
    return list(zip(widths, names, markers, zulus))


def endpoint_cell(text, resolution, time_precision, subsecond_digits, shift, mark="T",
                  member="iso-datetime", width=DEFAULT_WIDTH,
                  name_style=DEFAULT_NAME_STYLE, marker="upper"):
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
    if resolution == "quarter":
        # Since landing 2b.6 the marker's case is the column's own.
        letter = "q" if marker == "lower" else "Q"
        return f"{text[:4]}-{letter}{text[6]}"
    if resolution == "month":
        return text
    if resolution == "date":
        # THE END IS STILL BUILT FROM ITS OWN PUBLISHED FIELDS (G7.5,
        # review item P2-C2-F5); since landing 2b.6 those fields are
        # written through the member that read the real column, so a
        # month-first column's end is `03/17/2024` and not `2024-03-17`.
        return written_date(
            int(text[:4]), int(text[5:7]), int(text[8:10]),
            member, width, name_style,
        )
    year, month, day = (int(part) for part in text[:10].split("-"))
    hours, minutes, seconds = (int(part) for part in text[11:].split(":"))
    minute = (
        86400 * days_from_civil(year, month, day) + 3600 * hours + 60 * minutes
    )
    written = precision_form(
        minute + shift, resolution, time_precision, subsecond_digits, mark,
        member=member, width=width, name_style=name_style, marker=marker,
    )
    if time_precision == "minute":
        # The one precision with no seconds field at all, which contract
        # invariant D10 admits only where both ends carry `SS` of `00`.
        return written
    # YYYY-MM-DD?HH:MM:SS, the ? being the allocated mark -- one
    # character at 10 whichever it is, so the seconds field is still the
    # two characters at 17 and 18, and anything after them is the
    # fraction.
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
# The one-figure whole numbers in the order method G9.6 walks them: 1 to
# 9, then the lone 0 (plan P4-D162).
ONE_FIGURE_ORDER = tuple("1234567890")
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


def invented_variant(parent, used, target):
    """One invented variant spelling -- method sections G8.2 and G8.2a.

    Case flips first, in binary-counter order, skipping any candidate
    equal to a spelling already used in this column; then trailing
    spaces, one more each time, which the fold trims away and the reader
    preserves, and whose supply has no end.  A parent with no letters
    exhausts the case flips immediately and goes straight to the spaces.

    ``target`` is the written form the spelling must wear, "" for none
    (G8.2a): a candidate wearing another form is stepped past, exactly
    as one already used is.  Where the case flips run out with a form
    still wanted, the trailing space is written and the level falls
    short of its published ``shape_form_cells``, which the twin's own
    report names.
    """
    seen = set(used)
    counter = 1
    while True:
        candidate = case_flip(parent, counter)
        if candidate is None:
            break
        counter += 1
        if candidate in seen or written_form(candidate) != target:
            continue
        return candidate
    spaces = 1
    while True:
        candidate = parent + " " * spaces
        spaces += 1
        if candidate not in seen:
            return candidate


SHAPE_FORM_LIMIT = 24
WITHHELD = "(withheld)"
# The two placeholders and the closed mark list, held here so this
# file's own reading of a form is written out rather than imported --
# which is the whole point of an oracle.
SHAPE_DIGIT = "%"
SHAPE_LETTER = "@"
# The lower-case letter of a census key (contract C6-31a, landing 2b.18
# part 2): a key the census names for the cells of one form whose every
# letter was lower case, and never a mark `written_form` writes.
SHAPE_LOWER = "&"
SHAPE_MARKS = "-./_:#*()[]+,"


def usable_stand_in(candidate):
    """The four properties the neutral spelling had by construction.

    `group-N` had them for free; a spelling built to look like one of
    the column's own values does not, so each is asked.  This file
    answers them WITHOUT the shipped reader, which is the whole point
    of it -- and it must answer them the same way the reader does on
    every candidate its own cases produce, or the two write different
    bytes for a reason that is about this file and not about the
    method.

    So the range it reasons about is bounded and the bound is
    ENFORCED: a form carrying a figure could produce a candidate that
    reads back as a number or as a date, and this file states no
    reading of either.  A case reaching one raises here rather than
    quietly disagreeing.
    """
    if not candidate:
        return False
    if folded(candidate) in NO_VALUE_SPELLINGS:
        return False
    for character in candidate:
        if character == "," or character == '"':
            return False
        if character.isdigit():
            raise AssertionError(
                "this file reasons only about stand-ins with no figure "
                f"in them, and {candidate!r} has one: a candidate that "
                "could read back as a number or a date needs the "
                "number and date rules answered here, not reasoned "
                "away"
            )
    return candidate[0] not in "=+-@"


def written_form(text):
    """The written form of one cell -- contract C6-31a.

    Every ASCII digit becomes ``9``, every ASCII letter ``A``, and every
    other character stands as itself.  A cell that is empty or longer
    than the limit has no form at all.
    """
    if not text or len(text) > SHAPE_FORM_LIMIT:
        return ""
    built = ""
    figures = letters = marks = 0
    for character in text:
        if character in (SHAPE_DIGIT, SHAPE_LETTER):
            return ""
        if character.isdigit():
            built += SHAPE_DIGIT
            figures = 1
        elif character.isalpha():
            built += SHAPE_LETTER
            letters = 1
        elif character in SHAPE_MARKS:
            built += character
            marks = 1
        else:
            return ""
    if figures + letters + marks < 2:
        return ""
    return built


def form_room(form):
    """How many different spellings one form holds."""
    room = 1
    for character in form:
        if character == SHAPE_DIGIT:
            room *= 10
        elif character in (SHAPE_LETTER, SHAPE_LOWER):
            room *= 26
    return room


def all_letters_lower(text):
    """Whether a cell holds an ASCII letter and no upper-case one."""
    lower = any("a" <= character <= "z" for character in text)
    upper = any("A" <= character <= "Z" for character in text)
    return lower and not upper


def census_form(text, census):
    """The census key one cell is counted under -- contract C6-31a.

    Its written form, blind to case; or, where every letter of the cell
    is lower case and the census names the form with `&` in every letter
    place, that key.
    """
    form = written_form(text)
    if not form or SHAPE_LETTER not in form or not all_letters_lower(text):
        return form
    lower = form.replace(SHAPE_LETTER, SHAPE_LOWER)
    return lower if lower in census else form


def shares_a_factor(one, other):
    left, right = one, other
    while right:
        left, right = right, left % right
    return left != 1


def stepped_around(step, room):
    """``step`` moved around ``room`` so every position varies.

    A stride sharing no factor with the room is a one-to-one map onto
    it, so no two steps below the room collide and consecutive steps
    land far apart.  Taken in counting order instead, every position
    but the lowest stays at zero for the first few hundred values and
    every cell of the column ends alike.
    """
    if room < 4:
        return step % max(room, 1)
    stride = max(room * 61803 // 100000, 1)
    while shares_a_factor(stride, room):
        stride += 1
    return (step * stride) % room


def filled_form(form, step):
    """One spelling of one form -- contract 7.9.1."""
    figures = "0123456789"
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    built = ""
    place = stepped_around(step, form_room(form))
    for character in form:
        if character == SHAPE_DIGIT:
            built += figures[place % 10]
            place //= 10
        elif character == SHAPE_LETTER:
            built += letters[place % 26]
            place //= 26
        elif character == SHAPE_LOWER:
            # A lower-case key is filled in lower case, at the same
            # positions and by the same arithmetic (landing 2b.18 part 2).
            built += letters[place % 26].lower()
            place //= 26
        else:
            built += character
    return built


def forms_owed(census, written):
    """Cells each published form still owes after what is written."""
    owing = {}
    for form in sorted(census):
        if form == WITHHELD:
            continue
        owing[form] = census[form]
    for cell in written:
        form = census_form(cell, census)
        if form in owing and owing[form] > 0:
            owing[form] -= 1
    return owing


def neediest_form(owing):
    """The published form owing the most cells, ties by its spelling."""
    ordered = sorted(
        (-owing[form], form) for form in sorted(owing) if owing[form] > 0
    )
    return ordered[0][1] if ordered else ""


def within_the_published_ends(candidate, ladder):
    """Whether a made-up number lies between the published numbers' ends.

    Method G8.3a step 2's bound on the form's OWN walk (P4-D92).  Step 3
    steps from the published numbers, so what it writes sits in or beside
    the span the column holds; the form's own walk fills figure places by
    counting and lands wherever the counting lands.  Unbounded it wrote
    `9.6E6` for a column holding 1.1e6 to 1.3e6 -- meeting the census and
    taking the twin's mean to 2,450,000 against 1,173,077, with validate
    falling from 3 to 0.  So the VALUE is asked too.

    THE ENDS ARE VALUES AND NOT RUNGS (P4-D100).  Asking the LADDER for
    them left a column whose every published number wears an exponent or
    a leading plus with no ends at all, so every spelling of its form was
    refused and four cells of a twenty-six census went unpaid.  Such a
    column does publish numbers; what it lacks is a rung to step from,
    which bears on the walk of step 3 and not on how large a made-up
    number may be.  So the span of the published VALUES bounds it, and
    only a column publishing no number at all has no ends.
    """
    if not ladder["anchored"]:
        if not ladder["spanned"]:
            return False
        return ladder["least"] <= float(candidate) <= ladder["greatest"]
    scale = float(10 ** ladder["places"])
    return (
        ladder["lowest"] / scale <= float(candidate) <= ladder["highest"] / scale
    )


def usable_room(form, wanted, seen, folds, reads=None, ladder=None):
    """How many spellings of one form a stand-in could still wear, up to
    ``wanted`` -- method section G8.3's supply rule.

    A spelling already written, raw or folded, is not supply, and nor is
    one the neutrality tests refuse.  ``reads`` is the numeric class the
    spelling must read as (G8.3a); None is ordinary text.  ``ladder``,
    where given, holds the count to the published ends (P4-D92), so the
    supply is counted under the bound the walk spends under.
    """
    room = min(form_room(form), STAND_IN_STEPS)
    usable = 0
    for step in range(room):
        if usable >= wanted:
            return usable
        candidate = filled_form(form, step)
        if candidate in seen or folded(candidate) in folds:
            continue
        if reads is None:
            if not usable_stand_in(candidate):
                continue
        elif not usable_of_class(candidate, reads):
            continue
        if ladder is not None and not within_the_published_ends(candidate, ladder):
            continue
        usable += 1
    return usable


# How many held-back levels the arrangement search walks at all, and how
# many assignments it looks at -- method section G8.3.
SHARE_OUT_PLACES = 256
SHARE_OUT_NODES = 20000
STAND_IN_STEPS = 4096

# How many different exact class arrangements G8.3a step 1 tries before
# the first one stands (landing 2b.13).  Each pass forbids one more of
# the places the refused arrangement spent, so the passes reach
# genuinely different subsets.
CLASS_RETRIES = 8


def subset_making(spare, total, most):
    """Which slots of ``spare`` sum to ``total`` in at most ``most`` parts.

    Reachable sums, each size offered against the sums reached WITHOUT
    it, and a sum once reached never rewritten -- the two rules that make
    the chain read back strictly decreasing in slot.

    The places a refused arrangement spent are forbidden by the CALLER:
    `settled_by_sums` drops them from ``spare`` before asking this, so
    the retry of G8.3a step 1 reaches a different subset by being handed
    different sizes.
    """
    if total < 1:
        return []
    if most < 1:
        return None
    made = {}
    reached = {0: 0}
    for slot, size in enumerate(spare):
        for sum_so_far, parts in list(reached.items()):
            step = sum_so_far + size
            if step > total or step in reached or parts + 1 > most:
                continue
            reached[step] = parts + 1
            made[step] = (slot, sum_so_far)
    if total not in made:
        return None
    picked = []
    at = total
    while at:
        slot, before = made[at]
        picked.append(slot)
        at = before
    return picked


def settled_by_sums(sizes, places, owing, names, supply, biggest_first, avoid=()):
    """Every debt settled by an exact subset in turn, or None -- G8.3.

    ``avoid`` names places this pass may not give to any debt, which is
    how class_split reaches a different exact arrangement than the one
    whose form debts it could not settle (G8.3a step 1, landing 2b.13).
    """
    spare = [sizes[place] for place in places if place not in avoid]
    where = [place for place in places if place not in avoid]
    taken = {}
    if biggest_first:
        ordered = sorted((-owing[name], name) for name in names)
    else:
        ordered = sorted((owing[name], name) for name in names)
    for _debt, name in ordered:
        picked = subset_making(spare, owing[name], supply[name])
        if picked is None:
            return None
        for slot in sorted(picked, reverse=True):
            taken[where[slot]] = name
            del spare[slot]
            del where[slot]
    return [taken.get(place, "") for place in range(len(sizes))]


def settles(places, sizes, left, names, chosen, budget, supply):
    """The bounded arrangement search of G8.3, walked with its own stack.

    Each place offers the debts in descending order of what they still
    owe, ties by name, and the neutral choice last; a debt is offered
    only where it owes at least the place's size and has supply left.
    """
    depth = 0
    tried = [0 for _ in places]
    while True:
        if depth >= len(places):
            if all(left[name] == 0 for name in names):
                return True
            depth -= 1
            if depth < 0:
                return False
            given_back(left, supply, sizes, chosen, places[depth])
            continue
        budget[0] -= 1
        if budget[0] < 0:
            return False
        place = places[depth]
        size = sizes[place]
        offers = sorted((-left[name], name) for name in names)
        taken = False
        for step in range(tried[depth], len(offers) + 1):
            if step == len(offers):
                tried[depth] = step + 1
                chosen[place] = ""
                taken = True
                break
            name = offers[step][1]
            if left[name] < size or supply[name] < 1:
                continue
            tried[depth] = step + 1
            left[name] -= size
            supply[name] -= 1
            chosen[place] = name
            taken = True
            break
        if taken:
            depth += 1
            if depth < len(places):
                tried[depth] = 0
            continue
        tried[depth] = 0
        depth -= 1
        if depth < 0:
            return False
        given_back(left, supply, sizes, chosen, places[depth])


def given_back(left, supply, sizes, chosen, place):
    name = chosen[place]
    if name:
        left[name] += sizes[place]
        supply[name] += 1
    del chosen[place]


def greedily(sizes, places, owing, seen, folds, supplied=None):
    """G8.3's one-pass arrangement: the neediest debt that still has supply."""
    every = [name for name in sorted(owing) if owing[name] > 0]
    left = {name: owing[name] for name in every}
    spare = {
        name: usable_room(name, len(sizes), seen, folds)
        if supplied is None else supplied[name]
        for name in every
    }
    taken = ["" for _ in sizes]
    for place in places:
        name = neediest_form(
            {form: left[form] for form in sorted(left) if spare[form] > 0}
        )
        if not name:
            break
        taken[place] = name
        left[name] = max(0, left[name] - sizes[place])
        spare[name] -= 1
    return taken


def shared_out(sizes, owing, seen, folds, supplied=None):
    """Which published form each held-back size is written in -- G8.3.

    The sizes are taken LARGEST FIRST; every debt is settled by an exact
    subset of them, the larger debt first and then the smaller first;
    where neither settles every debt, the bounded search runs, and where
    that finds nothing the one-pass arrangement stands.
    """
    names = [name for name in sorted(owing) if owing[name] > 0]
    if not names:
        return ["" for _ in sizes]
    places = [pair[1] for pair in sorted((-size, place) for place, size in enumerate(sizes))]
    supply = {
        name: usable_room(name, len(sizes), seen, folds)
        if supplied is None else supplied[name]
        for name in names
    }
    if len(places) > SHARE_OUT_PLACES:
        return greedily(sizes, places, owing, seen, folds, supplied)
    for biggest_first in (True, False):
        settled = settled_by_sums(
            sizes, places, owing, names, dict(supply), biggest_first
        )
        if settled is not None:
            return settled
    left = {name: owing[name] for name in names}
    chosen = {}
    if settles(places, sizes, left, names, chosen, [SHARE_OUT_NODES], dict(supply)):
        return [chosen.get(place, "") for place in range(len(sizes))]
    return greedily(sizes, places, owing, seen, folds, supplied)


def invented_levels(
    used, sizes, census=None, written=(), placed=None, level_shape=""
):
    """The stand-in labels of method sections G8.3 and G8.3a.

    WHICH SIZE TAKES WHICH FORM IS SETTLED FIRST, by `shared_out`, over
    the debts the census still owes after the cells ALREADY WRITTEN.
    Each stand-in is then walked in the list's own order: a size given a
    form takes that form's next spelling -- each form carrying a cursor
    of its own across the column -- that no cell has written, raw or
    folded, and that the four neutrality tests accept; a size given none,
    or whose form has no such spelling left, takes ``group-N``, whose
    counter is its own and advances past every collision.

    ``placed``, where given, holds the sizes G8.3a already wrote as
    numbers: those keep their spellings, every form a number can wear is
    taken out of the debt, and the words are settled over the rest.
    """
    seen = set(used)
    folds = {folded(text) for text in used}
    owing = forms_owed(census or {}, written)
    wordy = list(range(len(sizes)))
    if placed is not None:
        for spelling in placed.values():
            seen.add(spelling)
            folds.add(folded(spelling))
        for form in sorted(owing):
            if form_reading(form) != NOTATION_TEXT:
                owing[form] = 0
        wordy = [place for place in range(len(sizes)) if place not in placed]
    settled = shared_out([sizes[place] for place in wordy], owing, seen, folds)
    shared = ["" for _ in sizes]
    for step, place in enumerate(wordy):
        shared[place] = settled[step]
    covered = set()
    if level_shape:
        shared, covered = level_shape_spent(
            sizes, shared, level_shape, placed or {}, seen, folds
        )
    produced = []
    walked = {}
    number = 0
    for place, size in enumerate(sizes):
        if placed is not None and place in placed:
            produced.append((placed[place], size))
            continue
        form = shared[place]
        if not form and place in covered:
            form = level_shape
        candidate = None
        if form:
            room = min(form_room(form), STAND_IN_STEPS)
            walked.setdefault(form, 0)
            while walked[form] < room:
                trial = filled_form(form, walked[form])
                walked[form] += 1
                if trial in seen or folded(trial) in folds:
                    continue
                if not usable_stand_in(trial):
                    continue
                candidate = trial
                break
        if candidate is None:
            while True:
                number += 1
                trial = f"group-{number}"
                if trial in seen or folded(trial) in folds:
                    continue
                if not usable_stand_in(trial):
                    continue
                candidate = trial
                break
        seen.add(candidate)
        folds.add(folded(candidate))
        produced.append((candidate, size))
    return produced


# ------------------------------------- the classes a label column owes


# THE THREE NUMERIC CLASSES A HELD-BACK GROUP CAN OWE (method G8.3a),
# keyed with a leading space because no written form holds one.
OWED_NUMBER = " number"
OWED_OUT_OF_RANGE = " out_of_range"
OWED_CONTRADICTORY = " contradictory"
OWED_CLASSES = (OWED_NUMBER, OWED_OUT_OF_RANGE, OWED_CONTRADICTORY)


def owed_reading(name):
    """The notation class a cell paying one class debt reads as."""
    return {
        OWED_NUMBER: NOTATION_NUMBER,
        OWED_OUT_OF_RANGE: NOTATION_OUT_OF_RANGE,
        OWED_CONTRADICTORY: NOTATION_CONTRADICTORY,
    }[name]

LADDER_STEPS = 1 << 14

# The settings every frozen case is described at: the reference test
# builds each case's description with a smallest group size of eleven and
# a long-tail line of eleven, and the rules below that read them read
# these.
SMALL_CELL_FLOOR = 11
LONG_TAIL_LINE = 11
CLASS_SUM_WORK = 1 << 24
NUMERIC_SENTINELS = (F(-9999), F(-999), F(9999))

# The longest made-up number this file freezes a case for.  No shipped
# date format reads a plain decimal -- an optional minus, figures and at
# most one point -- of fewer than eight characters: the compact date is
# eight figures and every other format carries a mark a plain decimal
# does not.  A longer one would need the date rule answered, and this
# file states no reading of it.
LONGEST_FROZEN_NUMBER = 7


def form_reading(form):
    """The class one published form's spellings read as -- G8.3a step 2.

    THE FIRST FILLING IS NOT THE ONLY ONE.  filled_form puts `A` in the
    first letter place, so `%.%@%` -- the form of `1.1e6` -- fills to
    `0.0A0`, which reads as TEXT, and the form was offered to the word
    debt and never to the number debt.  Where the first filling reads as
    no numeric class, the EXPONENT filling is asked as well: a letter
    place holding `E` is what makes a form of figures and one letter a
    number, and the form's own walk reaches such a spelling.  Only
    NUMBER is answered this way; the other two classes are constructed
    outright by G10.3.
    """
    reading = notation_reading(filled_form(form, 0))[0]
    if reading != NOTATION_TEXT:
        return reading
    exponent = exponent_filling(form)
    if exponent and notation_reading(exponent)[0] == NOTATION_NUMBER:
        return NOTATION_NUMBER
    return reading


def exponent_filling(form):
    """One filling of a form wearing `E` in every letter place, or "".

    Every figure mark takes `0`, every letter mark takes `E`, and every
    other character stands as itself.  Empty where the form holds no
    letter mark, which is the ordinary case.  A form whose letter places
    would have to DIFFER is answered exactly as before, which is the
    stated limit of the rule.
    """
    if SHAPE_LETTER not in form and SHAPE_LOWER not in form:
        return ""
    built = ""
    for character in form:
        if character == SHAPE_DIGIT:
            built += "0"
        elif character == SHAPE_LETTER:
            built += "E"
        elif character == SHAPE_LOWER:
            built += "e"
        else:
            built += character
    return built


def usable_of_class(candidate, reads):
    """The neutrality tests of G8.3a, for a stand-in of a numeric class.

    It must read as its class; the three sentinel numbers are refused;
    so are a spelling meaning "no value", a quote, a comma and a leading
    `=`, `+` or `@` -- a minus is how a negative number is written.
    """
    if not candidate or folded(candidate) in NO_VALUE_SPELLINGS:
        return False
    reading = notation_reading(candidate)[0]
    if reading != reads:
        return False
    if reads == NOTATION_NUMBER:
        if decimal_to_fraction(candidate) in NUMERIC_SENTINELS:
            return False
        body = candidate[1:] if candidate[:1] == "-" else candidate
        if len(candidate) > LONGEST_FROZEN_NUMBER or body.count(".") > 1 or not all(
            character.isdigit() or character == "." for character in body
        ):
            raise AssertionError(
                f"{candidate!r} is not a plain decimal of at most "
                f"{LONGEST_FROZEN_NUMBER} characters, so the date rule could "
                "reach it, and this file states no reading of that rule"
            )
    if '"' in candidate or "," in candidate:
        return False
    return candidate[0] not in "=+@"


def classes_owed(column, written):
    """What each numeric class still owes after the cells already written."""
    counted = {name: 0 for name in OWED_CLASSES}
    for cell in written:
        reading = notation_reading(cell)[0]
        for name in OWED_CLASSES:
            if owed_reading(name) == reading:
                counted[name] += 1
    return {
        OWED_NUMBER: column["n_numeric"] - counted[OWED_NUMBER],
        OWED_OUT_OF_RANGE: column["n_out_of_range"] - counted[OWED_OUT_OF_RANGE],
        OWED_CONTRADICTORY: column["n_contradictory"]
        - counted[OWED_CONTRADICTORY],
    }


def plain_units(text):
    """``-12.50`` as (-1250, 2); None for anything but a plain decimal."""
    body = text.strip()
    negative = body[:1] == "-"
    if negative:
        body = body[1:]
    whole, point, fraction = body.partition(".")
    if not whole or not whole.isdigit() or (point and not fraction.isdigit()):
        return None
    value = int(whole + fraction)
    return (-value if negative else value), len(fraction)


def form_places(form):
    """Figures a form writes after its point; nought where it has none."""
    if "." not in form:
        return 0
    return form.rsplit(".", 1)[1].count(SHAPE_DIGIT)


def number_ladder(written, forms):
    """The published numbers a label column steps its made-up ones from."""
    parsed = []
    # EVERY PUBLISHED NUMBER'S VALUE, stepped from or not (P4-D100).  The
    # exact reader above already settles each cell's class, and its value
    # is the same reading; `plain_units` answers for the SPELLINGS the
    # walk of step 3 can step from, which is the narrower question.
    span = []
    for cell in dict.fromkeys(written):
        if notation_reading(cell)[0] != NOTATION_NUMBER:
            continue
        span.append(float(decimal_to_fraction(cell.strip())))
        units = plain_units(cell)
        if units is not None:
            parsed.append(units)
    ends = {"least": min(span) if span else 0.0,
            "greatest": max(span) if span else 0.0,
            "spanned": bool(span)}
    if not parsed:
        places = max([form_places(form) for form in forms] + [0])
        # A NUMBER WEARING NO NAMED FORM takes those places and then whole
        # numbers, which wear no form at all (landing 2b.4, repair).
        tiers = (places, 0) if places > 0 else (0,)
        return {"lowest": 0, "highest": 0, "places": places,
                "signs": {"positive"}, "anchored": False, "published": set(),
                "tiers": tiers, **ends}
    places = max(pair[1] for pair in parsed)
    values = [value * 10 ** (places - own) for value, own in parsed]
    signs = set()
    for value in values:
        signs.add("negative" if value < 0 else "zero" if value == 0 else "positive")
    # EVERY COUNT OF PLACES A PUBLISHED NUMBER WAS WRITTEN WITH, finest
    # first: a number wearing no named form walks them in turn.
    tiers = tuple(sorted({own for _value, own in parsed}, reverse=True))
    return {"lowest": min(values), "highest": max(values), "places": places,
            "signs": signs, "anchored": True, "published": set(values),
            "tiers": tiers, **ends}


def sign_held(value, signs):
    """G8.3a's sign rule: no made-up number takes a sign the column lacks."""
    if value < 0:
        return "negative" in signs
    if value == 0:
        return "zero" in signs or ("negative" in signs and "positive" in signs)
    return "positive" in signs or ("zero" in signs and "negative" not in signs)


def rescaled(value, source, target, upward):
    if target >= source:
        return value * 10 ** (target - source)
    factor = 10 ** (source - target)
    return -((-value) // factor) if upward else value // factor


def outward_at(ladder, places, position, low_ended=False, high_ended=False):
    """One position of G8.3a's walk: (state, value, side).

    The state is "here", "skip" or "end"; the side is "gap", "low" or
    "high". The GAPS come first -- values strictly between the smallest
    and the largest published number that no published number holds,
    nearest an end first and the low end first at each distance -- and
    then the OUTWARD steps, below the smallest and above the largest in
    turn. A side the caller has ended is held as a side whose sign the
    column lacks.
    """
    floor = rescaled(ladder["lowest"], ladder["places"], places, False)
    ceiling = rescaled(ladder["highest"], ladder["places"], places, True)
    if not ladder["anchored"]:
        ceiling = floor
    gaps = ceiling - floor - 1
    half = (gaps + 1) // 2 if gaps > 0 else 0
    if position < 2 * half:
        depth = position // 2 + 1
        value = floor + depth
        if position % 2 == 1:
            if depth > gaps // 2:
                return ("skip", None, "gap")
            value = ceiling - depth
        if places >= ladder["places"]:
            factor = 10 ** (places - ladder["places"])
            published = value % factor == 0 and value // factor in ladder["published"]
        else:
            published = value * 10 ** (ladder["places"] - places) in ladder["published"]
        if published or not sign_held(value, ladder["signs"]):
            return ("skip", None, "gap")
        return ("here", value, "gap")
    step = (position - 2 * half) // 2 + 1
    low = rescaled(ladder["lowest"], ladder["places"], places, True) - step
    high = rescaled(ladder["highest"], ladder["places"], places, False) + step
    if not ladder["anchored"]:
        low, high = -step, step
    low_held = not low_ended and sign_held(low, ladder["signs"])
    high_held = not high_ended and sign_held(high, ladder["signs"])
    if not low_held and not high_held:
        return ("end", None, None)
    if (position - 2 * half) % 2 == 0:
        return ("here", low, "low") if low_held else ("skip", None, "low")
    return ("here", high, "high") if high_held else ("skip", None, "high")


def whole_figures(units, places):
    """Figures before the decimal mark of a number of ``places`` places."""
    return len(str(abs(units) // 10 ** places))


def form_whole_figures(form):
    """Figures a plain decimal form writes before its point; -1 otherwise."""
    body = form[1:] if form[:1] == "-" else form
    whole, _point, fraction = body.partition(".")
    if not whole or any(mark != SHAPE_DIGIT for mark in whole + fraction):
        return -1
    return len(whole)


def units_spelled(units, places):
    """A whole number of last places written plainly, no zero invented."""
    lead = "-" if units < 0 else ""
    size = -units if units < 0 else units
    whole, part = divmod(size, 10 ** places)
    if places == 0:
        return f"{lead}{whole}"
    return f"{lead}{whole}.{part:0{places}d}"


def next_on_ladder(ladder, name, cursor, named, seen, folds, needed=0, pool=None,
                   bounded=False):
    """The next made-up number one debt may take, or "" -- G8.3a.

    A number wearing no named form walks the ladder's tiers, finest count
    of places first. Where ``pool`` is given -- the cells the census
    pooled -- it must wear a form the census could hold: a form with room
    for at least ``needed`` cells that the census does not name is written
    only where the pool holds a cell, and where it is refused on a side
    whose steps only widen, that side has ended. A form's own walk ends a
    side once its steps are wider than the form.
    """
    tiers = ladder["tiers"]
    reach = 0
    if name != OWED_NUMBER:
        tiers = (form_places(name),)
        reach = form_whole_figures(name)
    # THE NARROW WALK (integration repair): the widest number the column
    # published, or the widest plain form the census names, bounds a
    # counted form the census does not name, pool or no pool.
    widest = -1
    if bounded:
        widest = max(
            [whole_figures(ladder["lowest"], ladder["places"]),
             whole_figures(ladder["highest"], ladder["places"])]
            if ladder["anchored"] else [0]
        )
        widest = max([widest] + [form_whole_figures(form) for form in named])
    for places in tiers:
        key = f"{name}/{places}"
        low, high = f"{key}/low", f"{key}/high"
        cursor.setdefault(key, 0)
        while cursor[key] < 2 * LADDER_STEPS:
            state, units, side = outward_at(
                ladder, places, cursor[key], low in cursor, high in cursor
            )
            if state == "end":
                cursor[key] = 2 * LADDER_STEPS
                break
            cursor[key] += 1
            if state == "skip":
                continue
            candidate = units_spelled(units, places)
            form = census_form(candidate, named)
            if name == OWED_NUMBER:
                if form in named:
                    continue
                if pool is not None and form and form_room(form) >= needed and (
                    pool < 1 or (widest >= 0 and whole_figures(units, places) > widest)
                ):
                    if side == "high" and units > 0:
                        cursor[high] = 1
                    if side == "low" and units < 0:
                        cursor[low] = 1
                    continue
            elif form != name:
                wider = whole_figures(units, places) > reach
                if side == "high" and units > 0 and wider:
                    cursor[high] = 1
                if side == "low" and units < 0 and wider:
                    cursor[low] = 1
                continue
            if candidate in seen or folded(candidate) in folds:
                continue
            if not usable_of_class(candidate, NOTATION_NUMBER):
                continue
            return candidate
    return ""


def ladder_room(ladder, name, wanted, named, seen, folds, needed=0, pool=None,
                bounded=False):
    cursor = {}
    usable = 0
    while usable < wanted and next_on_ladder(
        ladder, name, cursor, named, seen, folds, needed, pool, bounded
    ):
        usable += 1
    return usable


def forms_within_the_unasked_supply(
    ladder, sub, mine_forms, room, forms_of, named, seen, folds, needed, pool,
    bounded=False,
):
    """G8.3a step 2's second settlement, where the levels given no form starve.

    Taken only where it settles every form exactly and leaves no more levels
    without a form than a number wearing no named form can supply.
    """
    spare = ladder_room(
        ladder, OWED_NUMBER, len(sub), named, seen, folds, needed, pool, bounded
    )
    unasked = sum(1 for form in forms_of if not form)
    rest = sum(sub) - sum(mine_forms.values())
    if unasked <= spare or rest < 1:
        return forms_of
    refit = shared_out(
        sub, {**mine_forms, OWED_NUMBER: rest}, seen, folds,
        {**room, OWED_NUMBER: spare},
    )
    answer = ["" if form == OWED_NUMBER else form for form in refit]
    if sum(1 for form in answer if not form) > spare:
        return forms_of
    for form in mine_forms:
        if sum(size for size, worn in zip(sub, answer) if worn == form) != mine_forms[form]:
            return forms_of
    return answer


def settles_its_forms(taken, sizes, owing):
    """Whether each class's own form debts can still be settled exactly.

    THE SPLIT SETTLES CELLS AND THE FORMS ARE SETTLED INSIDE IT, so an
    arrangement paying every class exactly can still make a form debt
    impossible (G8.3a step 1, landing 2b.13).  Readings `5.1` and `5.3`
    on eleven rows each, `5.2` on four and `8` on one: five cells must
    be numbers and four of them must wear `%.%`, and the sizes 3+2 make
    five exactly and four not at all, while the source's own 4+1 meets
    both.

    A form owing more cells than the whole class covers is unpayable
    under every split, so it is not asked: an arrangement is not refused
    for failing to do the impossible.  Each form's supply is taken as
    the number of sizes, because this asks whether the ARITHMETIC
    exists and the walk still reports whatever the supply refuses.
    """
    for name in OWED_CLASSES:
        reads = owed_reading(name)
        mine = [place for place in range(len(sizes)) if taken.get(place) == name]
        if not mine:
            continue
        sub = [sizes[place] for place in mine]
        covered = sum(sub)
        wanted = {
            form: owing[form] for form in sorted(owing)
            if 0 < owing[form] <= covered and form_reading(form) == reads
        }
        if not wanted:
            continue
        spots = [pair[1] for pair in sorted((-sub[step], step) for step in range(len(sub)))]
        room = {form: len(sub) for form in sorted(wanted)}
        names = sorted(wanted)
        settled = None
        for biggest_first in (True, False):
            settled = settled_by_sums(sub, spots, wanted, names, room, biggest_first)
            if settled is not None:
                break
        if settled is None:
            return False
    return True


def class_split(sizes, debts, supply, owing=None):
    """Which held-back sizes pay which class debt -- G8.3a step 1.

    ``owing`` is the census's remaining form debt.  Given, an
    arrangement is accepted only where settles_its_forms says each class
    can still settle the forms reading as it; otherwise another exact
    arrangement is tried, up to CLASS_RETRIES, each pass forbidding one
    more of the places the refused arrangement spent.  The FIRST exact
    arrangement stands where none of them can, so a column whose forms
    no arrangement settles is written exactly as it was before the rule.
    """
    names = [name for name in OWED_CLASSES if debts[name] > 0]
    if not names:
        return {}
    places = [pair[1] for pair in sorted((-size, place) for place, size in enumerate(sizes))]
    first = None
    if len(places) * max(debts[name] for name in names) <= CLASS_SUM_WORK:
        for biggest_first in (True, False):
            avoid = ()
            for _again in range(CLASS_RETRIES):
                settled = settled_by_sums(
                    sizes, places, debts, names, dict(supply), biggest_first, avoid
                )
                if settled is None:
                    break
                taken_now = {place: name for place, name in enumerate(settled) if name}
                if first is None:
                    first = taken_now
                if owing is None or settles_its_forms(taken_now, sizes, owing):
                    return taken_now
                spent = [
                    place for place in range(len(sizes))
                    if settled[place] and place not in avoid
                ]
                if not spent:
                    break
                avoid = avoid + (spent[0],)
    if first is not None:
        return first
    left = {name: debts[name] for name in names}
    spare = {name: supply[name] for name in names}
    taken = {}
    for place in places:
        best = ""
        for name in names:
            if left[name] < sizes[place] or spare[name] < 1:
                continue
            if not best or left[name] > left[best]:
                best = name
        if best:
            taken[place] = best
            left[best] -= sizes[place]
            spare[best] -= 1
    return taken


def class_stand_ins(column, written, used, sizes, census):
    """The held-back sizes G8.3a writes as numbers or stragglers.

    THE NARROW WALK FIRST (integration repair): every made-up number is
    first held to the widest number the column shows, and that answer
    stands where every paying size found a spelling; only otherwise may
    the census pool buy a wider number.
    """
    bounded = True
    placed, debts, classes = class_stand_ins_walked(
        column, written, used, sizes, census, True
    )
    if len(placed) != len(classes):
        bounded = False
        placed, debts, classes = class_stand_ins_walked(
            column, written, used, sizes, census, False
        )
    # AND A THIRD WALK WHERE THE NUMBER DEBT IS STILL UNPAID (landing
    # 2b.8).  The shortfall shows at WRITE time and not at the split: the
    # split gives the number class sizes that make its debt exactly, and
    # only then does the census rule refuse every candidate of the one
    # tier the published places offer, so those sizes fall back to words
    # with the class count missed.  The walk is taken again with a
    # whole-number tier after the published places, and kept only where
    # it covers more of the debt.
    if debts[OWED_NUMBER] > 0:
        paid = numbers_paid(sizes, classes, placed)
        if paid < debts[OWED_NUMBER]:
            wider, wider_debts, wider_classes = class_stand_ins_walked(
                column, written, used, sizes, census, bounded, True
            )
            if numbers_paid(sizes, wider_classes, wider) > paid:
                return wider, wider_debts
    return placed, debts


def numbers_paid(sizes, classes, placed):
    """How many cells of the number debt a finished walk actually paid.

    The sizes the split gave the number class AND the walk then found a
    spelling for.  A size left without one takes G8.3's neutral label,
    so its cells pay nothing however the split counted them.
    """
    return sum(
        sizes[place] for place in classes
        if classes[place] == OWED_NUMBER and place in placed
    )


def class_stand_ins_walked(
    column, written, used, sizes, census, bounded, whole_tier=False
):
    """One walk of class_stand_ins, narrow where ``bounded`` says."""
    seen = set(used)
    folds = {folded(text) for text in used}
    named = {form for form in (census or {}) if form != WITHHELD}
    # What the census could hold beside what it names (contract 7.9).
    needed = column["n_distinct"] + SMALL_CELL_FLOOR
    pool = (census or {}).get(WITHHELD, 0)
    owing = forms_owed(census or {}, written)
    debts = classes_owed(column, written)
    number_forms = [
        form for form in sorted(owing)
        if owing[form] > 0 and form_reading(form) == NOTATION_NUMBER
    ]
    ladder = number_ladder(written, number_forms)
    # A WHOLE-NUMBER TIER, WHERE THE CALLER ASKED FOR ONE (landing 2b.8).
    # Where every published number carried a decimal AND the census names
    # the form those places write, every candidate of that tier is
    # stepped past for wearing a named form, so the tier is empty and a
    # class debt goes unpaid.  A whole number wears no form at all, so it
    # can never overpay the census.  It is the LAST tier, and a tier is
    # taken up only once the one before it has ended.
    if whole_tier and ladder["anchored"] and 0 not in ladder["tiers"]:
        ladder = dict(ladder, tiers=ladder["tiers"] + (0,))
    supply = {name: len(sizes) for name in OWED_CLASSES}
    if debts[OWED_NUMBER] > 0:
        supply[OWED_NUMBER] = ladder_room(
            ladder, OWED_NUMBER, len(sizes), set(), seen, folds
        )
    classes = class_split(sizes, debts, supply, owing)
    placed = {}
    cursor = {}
    counters = {}
    walked = {}
    for name in OWED_CLASSES:
        reads = owed_reading(name)
        mine = [place for place in range(len(sizes)) if classes.get(place) == name]
        if not mine:
            continue
        mine_forms = {
            form: owing[form] for form in sorted(owing)
            if owing[form] > 0 and form_reading(form) == reads
        }
        sub = [sizes[place] for place in mine]
        room = {}
        for form in sorted(mine_forms):
            if name == OWED_NUMBER:
                # A NUMBER FORM HAS TWO SUPPLIES (landing 2b.13).  The
                # ladder spells a PLAIN decimal, so a form the ladder
                # cannot spell -- `%.%@%`, whose spellings carry an
                # exponent -- has ladder room nought and shared_out
                # settles it over no level at all.  Its own filling is
                # the other supply, and the walk below takes it where
                # the ladder has nothing.
                room[form] = max(
                    ladder_room(ladder, form, len(sub), named, seen, folds),
                    usable_room(form, len(sub), seen, folds, reads, ladder),
                )
            else:
                room[form] = usable_room(form, len(sub), seen, folds, reads)
        forms_of = ["" for _ in sub]
        if mine_forms:
            forms_of = shared_out(sub, mine_forms, seen, folds, room)
        if name == OWED_NUMBER and mine_forms:
            forms_of = forms_within_the_unasked_supply(
                ladder, sub, mine_forms, room, forms_of, named, seen, folds,
                needed, pool, bounded,
            )
        for _size, place, step in sorted((-sub[step], mine[step], step) for step in range(len(sub))):
            form = forms_of[step]
            found = ""
            if name == OWED_NUMBER:
                if form:
                    found = next_on_ladder(ladder, form, cursor, named, seen, folds)
                    if not found:
                        # THE FORM'S OWN FILLING, WHERE THE LADDER
                        # CANNOT SPELL IT (landing 2b.13).  units_spelled
                        # writes a plain decimal, whose form is `%.%` and
                        # never `%.%@%`, so a number level owing an
                        # exponent form was stepped past every candidate
                        # and fell through to the unformed walk, which
                        # wrote `1`.  The form's own walk writes a spelling
                        # that wears the form AND reads as a number -- and,
                        # since P4-D92, one lying between the published
                        # numbers' own ends, so a census count is never
                        # bought with a magnitude the column is not known
                        # to hold.  Where no plain number was published
                        # there are no ends and the debt simply stands.
                        room_left = min(form_room(form), STAND_IN_STEPS)
                        walked.setdefault(form, 0)
                        while walked[form] < room_left:
                            trial = filled_form(form, walked[form])
                            walked[form] += 1
                            if trial in seen or folded(trial) in folds:
                                continue
                            if usable_of_class(trial, reads) and (
                                within_the_published_ends(trial, ladder)
                            ):
                                found = trial
                                break
                if not found:
                    found = next_on_ladder(
                        ladder, OWED_NUMBER, cursor, named, seen, folds, needed, pool,
                        bounded,
                    )
            else:
                if form:
                    room_left = min(form_room(form), STAND_IN_STEPS)
                    walked.setdefault(form, 0)
                    while walked[form] < room_left:
                        trial = filled_form(form, walked[form])
                        walked[form] += 1
                        if trial in seen or folded(trial) in folds:
                            continue
                        if usable_of_class(trial, reads):
                            found = trial
                            break
                if not found:
                    counters.setdefault(name, 0)
                    while counters[name] < STAND_IN_STEPS:
                        counters[name] += 1
                        if name == OWED_OUT_OF_RANGE:
                            trial = f"{counters[name]}e999"
                        else:
                            trial = f"(-{counters[name]})"
                        if census_form(trial, named) in named:
                            continue
                        if trial in seen or folded(trial) in folds:
                            continue
                        if usable_of_class(trial, reads):
                            found = trial
                            break
            if found:
                seen.add(found)
                folds.add(folded(found))
                placed[place] = found
    return placed, debts, classes


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


# How much arithmetic G8.1a's step 4 will do before step 3's own
# partial answer stands.  The method states the bound as a product of
# the debt and the number of different group sizes.
FORM_DEBT_NODES = 250000


def form_keeping_groups(level):
    """Which held-back groups keep the label's form -- method G8.1a.

    Step 1 adds up the published spellings that already have a form,
    step 2 takes the debt from ``shape_form_cells``, step 3 walks the
    sizes largest first taking as many of each as fit, and step 4
    settles a remainder by reaching every total up to the debt.  The
    answer maps a ``variants_withheld`` key to how many of its groups
    keep the form.
    """
    covered = 0
    for spelling in sorted(level["variants"]):
        if written_form(spelling):
            covered += level["variants"][spelling]
    debt = level["shape_form_cells"] - covered
    keeping = {}
    if debt <= 0:
        return keeping
    withheld = level["variants_withheld"]
    largest_first = sorted(withheld, key=int, reverse=True)
    owed = debt
    for key in largest_first:
        take = min(withheld[key], owed // int(key))
        if take:
            keeping[key] = take
            owed -= take * int(key)
    if owed == 0:
        return keeping
    exact = debt_reached(withheld, largest_first, debt)
    return keeping if exact is None else exact


def debt_reached(withheld, largest_first, debt):
    """A sub-multiset of the held-back sizes summing to ``debt`` -- G8.1a.

    Step 4.  ``reached[total]`` records the first size that closes that
    total, the sizes offered largest first, and ``spent`` keeps one
    chain from using a size more often than the entry holds groups of
    it.  None says the debt is out of reach, or that the walk would
    cost more than ``FORM_DEBT_NODES`` steps.
    """
    if not largest_first or len(largest_first) * (debt + 1) > FORM_DEBT_NODES:
        return None
    reached = [0] * (debt + 1)
    reached[0] = -1
    for key in largest_first:
        size = int(key)
        spent = [0] * (debt + 1)
        for total in range(size, debt + 1):
            if reached[total] or not reached[total - size]:
                continue
            if spent[total - size] >= withheld[key]:
                continue
            reached[total] = size
            spent[total] = spent[total - size] + 1
    if not reached[debt]:
        return None
    keeping = {}
    total = debt
    while total > 0:
        size = reached[total]
        for candidate in largest_first:
            if int(candidate) == size:
                keeping[candidate] = keeping.get(candidate, 0) + 1
                break
        total -= size
    return keeping


def spare_label_group(level, keeping):
    """Which held-back group takes the label's own spelling -- G8.1 step 2.

    The label's own spelling is one more spelling that folds onto the
    label, and the only further one that KEEPS ITS WRITTEN FORM: a case
    flip may already be published and a trailing space changes the
    form.  It is available only where the published and held-back
    spellings already cover the level's count, since otherwise step 3
    writes the label itself and that spelling is spoken for.  It goes
    to the LARGEST group whose target form it wears -- the largest
    form-keeping group where the label has a form, and the largest
    group of all where it has none.  "" says it is not spent.
    """
    covered = sum(level["variants"].values())
    for key in level["variants_withheld"]:
        covered += int(key) * level["variants_withheld"][key]
    if covered < level["count"]:
        return ""
    formless = not written_form(level["label"])
    best = ""
    for key in level["variants_withheld"]:
        if not formless and not keeping.get(key):
            continue
        if not best or int(key) > int(best):
            best = key
    return best


def level_key(spelling):
    """The shape one published spelling wears, its case kept.

    Its written form, with `&` in every letter place where every letter
    of the spelling is lower case; "" where it has no form.
    """
    form = written_form(spelling)
    if form and SHAPE_LETTER in form and all_letters_lower(spelling):
        return form.replace(SHAPE_LETTER, SHAPE_LOWER)
    return form


def published_level_shape(column):
    """The shape a held-back label owed no named form is written in.

    Method G8.3b (landing 2b.18 part 2).  The shapes the published
    spellings wear -- a level's variants, or its label where it has none
    -- are tallied by the rows that wrote them; a shape reading as a
    number is passed over, and so is any shape the census names blind to
    case or in lower case; the one covering the most rows is taken, ties
    to its own spelling ascending.  "" where none is left.
    """
    census = column.get("shape_forms") or {}
    rows = {}
    for level in column["levels"]:
        spellings = level["variants"] or {level["label"]: level["count"]}
        for spelling in sorted(spellings):
            key = level_key(spelling)
            if key:
                rows[key] = rows.get(key, 0) + spellings[spelling]
    best = ""
    for key in sorted(rows):
        if form_reading(key) != NOTATION_TEXT:
            continue
        blind = written_form(filled_form(key, 0))
        if (
            key in census
            or blind in census
            or blind.replace(SHAPE_LETTER, SHAPE_LOWER) in census
        ):
            continue
        if not best or rows[key] > rows[best]:
            best = key
    return best


# The held-back sizes and the named form's debt of the frozen case
# `level_shape_stand_ins`: five groups of four rows and forty single rows,
# of which the census owes thirty-four to `@@@@-@@`. Since the owner's
# ruling of 2026-09-17 (plan P4-D201) the column publishes only their
# number and their pooled sixty rows, so the twin writes them at the sizes
# G8.3 reads off the pool and its debts: thirty-seven single rows, four of
# two, two of three, one of four and one of five.
LEVEL_SHAPE_SIZES = (1,) * 40 + (4,) * 5
LEVEL_SHAPE_DEBT = 34
LEVEL_SHAPE_ROWS = 11 + sum(LEVEL_SHAPE_SIZES)

# How many place-visits the trade pass may spend -- method G8.3b.
LEVEL_SHAPE_WORK = 1 << 22


def rows_past(ranked, sizes, supply):
    """The rows of the places ranked past a shape's supply."""
    return sum(sizes[place] for _size, place in ranked[supply:])


def level_shape_spent(sizes, shared, level_shape, fixed, seen, folds):
    """Where the published labels' shape is spent -- method G8.3b.

    The shape's supply is counted as usable_room counts any form's.  The
    places owed no form, ranked largest first and then by place, are
    covered up to that supply, and the rows past it are the rows missed.
    Each place paying a named form is offered once, largest first and
    then by place, while any row is missed and while the work budget
    lasts (each offer costs twice the number of places): for an offer of
    ``k`` rows, two or more, places owed no form are taken from the END
    of that ranking, each smaller than ``k`` and no larger than what is
    left to match, until they sum to ``k`` exactly with two or more of
    them; the trade stands where the named form has the spellings for
    the extra places and the rows missed then fall.
    """
    arranged = list(shared)
    free = [
        place for place in range(len(sizes))
        if place not in fixed and not arranged[place]
    ]
    supply = usable_room(level_shape, len(free), seen, folds)
    if supply < 1 or not free:
        return arranged, set()
    taken = {}
    for place in range(len(sizes)):
        if place in fixed or not arranged[place]:
            continue
        taken[arranged[place]] = taken.get(arranged[place], 0) + 1
    rooms = {}
    offered = sorted(
        (-sizes[place], place) for place in range(len(sizes))
        if place not in fixed and arranged[place]
    )
    work = LEVEL_SHAPE_WORK
    for _negative, place in offered:
        size = sizes[place]
        if size < 2:
            continue
        work -= 2 * len(sizes)
        if work < 0:
            break
        owed = sorted(
            (-sizes[other], other) for other in range(len(sizes))
            if other not in fixed and not arranged[other]
        )
        before = rows_past(owed, sizes, supply)
        if before == 0:
            break
        chosen = []
        left = size
        for _other_size, other in reversed(owed):
            if sizes[other] <= left and sizes[other] < size:
                chosen.append(other)
                left -= sizes[other]
                if left == 0:
                    break
        if left != 0 or len(chosen) < 2:
            continue
        name = arranged[place]
        if name not in rooms:
            rooms[name] = usable_room(name, len(sizes), seen, folds)
        if taken[name] - 1 + len(chosen) > rooms[name]:
            continue
        trial = list(arranged)
        trial[place] = ""
        for other in chosen:
            trial[other] = name
        after = rows_past(
            sorted(
                (-sizes[other], other) for other in range(len(sizes))
                if other not in fixed and not trial[other]
            ),
            sizes,
            supply,
        )
        if after >= before:
            continue
        arranged = trial
        taken[name] = taken[name] - 1 + len(chosen)
    owed = sorted(
        (-sizes[other], other) for other in range(len(sizes))
        if other not in fixed and not arranged[other]
    )
    return arranged, {place for _size, place in owed[:supply]}


def held_back_debts(column, written, census):
    """What the held-back cells owe, as method G8.3 orders it (P4-D201).

    Two lists.  The first: for each numeric class in G8.3a's order, what
    each census form reading as that class still owes, by the form's
    spelling and never past the class's own debt, then what the class
    owes beyond its forms.  The second: what each census form reading as
    text still owes, by spelling, then every cell left over.
    """
    classes = classes_owed(column, written)
    owing = forms_owed(census or {}, written)
    numbers, words = [], []
    spent = 0
    for name in OWED_CLASSES:
        if classes[name] <= 0:
            continue
        left = classes[name]
        for form in sorted(owing):
            if owing[form] > 0 and left > 0 and form_reading(form) == owed_reading(name):
                part = min(owing[form], left)
                numbers.append(part)
                left -= part
        if left > 0:
            numbers.append(left)
        spent += classes[name]
    for form in sorted(owing):
        if owing[form] > 0 and form_reading(form) == NOTATION_TEXT:
            words.append(owing[form])
            spent += owing[form]
    words.append(column["suppressed_rows"] - spent)
    return numbers, words


def rising_share(cells, count, top):
    """``cells`` over ``count`` labels, one row each and the rest by the
    square of each label's place (largest remainders first, the later
    place on a tie), any label past ``top`` passing its excess down."""
    spare = cells - count
    weights = [(place + 1) ** 2 for place in range(count)]
    whole = sum(weights)
    shares = [1 + spare * weight // whole for weight in weights]
    order = sorted(
        range(count), key=lambda place: (-(spare * weights[place] % whole), -place)
    )
    for place in order[: cells - sum(shares)]:
        shares[place] += 1
    for place in range(count - 1, 0, -1):
        if shares[place] > top:
            shares[place - 1] += shares[place] - top
            shares[place] = top
    return shares


def held_back_sizes(held_back, rows, numbers, words, floor=CASE_SMALL_CELL_FLOOR):
    """The rows of each invented held-back label -- method G8.3's sizes.

    Written from the rule's statement (owner ruling of 2026-09-17, item 2,
    option A; plan P4-D201), not from the product.  Each debt first takes
    the fewest labels that pay it below the floor (a pool whose debts do
    not come to its rows, or need more labels than it holds, is one
    debt); the labels left over go one by one to the debt then largest
    on average, the earlier on a tie -- a number debt while its average
    exceeds a third of the way from one to the floor, then a text form's
    debt up to a label a cell, then the cells owing no form (the last
    word debt) likewise, then any debt up to a label a cell; and each
    debt's cells are shared by ``rising_share``.
    """
    if held_back == 0:
        return []
    top = max(floor - 1, 1)
    debts = [debt for debt in numbers if debt > 0] + [debt for debt in words if debt > 0]
    count_numbers = len([debt for debt in numbers if debt > 0])
    labels = [math.ceil(fractions.Fraction(debt, top)) for debt in debts]
    unformed = len(debts) - 1 if words and words[-1] > 0 else None
    if sum(debts) != rows or sum(labels) > held_back or not debts:
        debts = [rows]
        labels = [math.ceil(fractions.Fraction(rows, top))]
        count_numbers = 0
        unformed = 0

    def hand_out(limits):
        while sum(labels) < held_back:
            open_debts = [place for place in range(len(debts)) if labels[place] < limits[place]]
            if not open_debts:
                return
            best = open_debts[0]
            for place in open_debts[1:]:
                if fractions.Fraction(debts[place], labels[place]) > fractions.Fraction(debts[best], labels[best]):
                    best = place
            labels[best] += 1

    limits = list(labels)
    for place in range(count_numbers):
        limits[place] = math.ceil(fractions.Fraction(3 * debts[place], top + 2))
    hand_out(limits)
    for place in range(count_numbers, len(debts)):
        if place != unformed:
            limits[place] = debts[place]
    hand_out(limits)
    if unformed is not None:
        limits[unformed] = debts[unformed]
    hand_out(limits)
    hand_out(debts)
    sizes = []
    for place in range(len(debts)):
        sizes += rising_share(debts[place], labels[place], top)
    if len(sizes) != held_back or sum(sizes) != rows or max(sizes) > top:
        raise AssertionError(
            f"a pool of {rows} rows cannot be written as {held_back} labels "
            f"below a floor of {floor}"
        )
    return sorted(sizes)


def _label_content(column):
    """The content list of a label column -- method sections G8.1 and G8.4."""
    content = []
    used = []
    for level in column["levels"]:
        for spelling in sorted(level["variants"]):
            content.extend([spelling] * level["variants"][spelling])
            used.append(spelling)
        withheld = level["variants_withheld"]
        if not level["variants"] and not withheld:
            content.extend([level["label"]] * level["count"])
            used.append(level["label"])
            continue
        keeping = form_keeping_groups(level)
        spare = spare_label_group(level, keeping)
        if level["label"] in used:
            spare = ""
        own = written_form(level["label"])
        left = dict(keeping)
        for key in sorted(withheld, key=int):
            for _ in range(withheld[key]):
                target = ""
                if left.get(key):
                    target = own
                    left[key] -= 1
                if spare and key == spare:
                    spelling = level["label"]
                    spare = ""
                else:
                    spelling = invented_variant(level["label"], used, target)
                content.extend([spelling] * int(key))
                used.append(spelling)
    census = column.get("shape_forms")
    numbers_owed, words_owed = held_back_debts(column, content, census)
    sizes = held_back_sizes(
        column["suppressed_levels"], column["suppressed_rows"], numbers_owed, words_owed
    )
    # THE CLASSES THE HELD-BACK LEVELS OWE (method G8.3a) are settled
    # before any word is: where the published spellings leave a numeric
    # class count unpaid, those levels are written as numbers first.
    placed = None
    if sizes and max(classes_owed(column, content).values()) > 0:
        placed, _debts = class_stand_ins(column, content, used, sizes, census)
    # THE SHAPE A STAND-IN OWED NO NAMED FORM TAKES (landing 2b.18 part 2).
    level_shape = published_level_shape(column)
    if placed is None:
        stand_ins = invented_levels(
            used, sizes, census, content, level_shape=level_shape
        )
    else:
        stand_ins = invented_levels(
            used, sizes, census, content, placed=placed,
            level_shape=level_shape,
        )
    for spelling, size in stand_ins:
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
    space = ordinal_space(column)
    # Decided by the space, so that withdrawing the day-unit rule (the
    # `midnight_days` mutant) withdraws the midnight writing with it.
    midnight = space == "date" and resolution == "datetime"
    parsed = column["n_present"] - column["n_unparsed"]
    rungs = [
        ordinal_of(column["date_percentiles"][key], space)
        for key in LADDER_KEYS
    ]
    # A column mixing bare dates with moments whose every value stands at
    # midnight writes its bare-date ranks as bare dates (landing 2b.3);
    # the census of marks is spent over the ranks that write a clock.
    whole = form_allocation(column, parsed)
    words = iter(column["_content_words"])
    # Every rank's instant first, one word per interior rank exactly as
    # before (landing 2b.3); the tail's ranks take their PUBLISHED values
    # and every other rank is drawn inside its own gap (landing 2b.6).
    ordinals = spread_ordinals(rungs, parsed, words)
    gap_lows, gap_highs = pin_bounds(rungs, parsed)
    snapping = snaps_to_midnight(column)
    offset_pins = {}
    if snapping:
        for rank, (seconds, _keys) in sorted(rung_pins(column, parsed).items()):
            ordinals[rank] = seconds
        # ...on a column only partly at midnight too (integration repair
        # of landing 2b.3).
        for rank, keys in instant_offsets(column, parsed).items():
            if 0 < rank < parsed - 1 and keys:
                offset_pins[rank] = keys
    offsets = _offset_allocation(column, parsed, whole, offset_pins)
    clock_marks = iter(_separator_allocation(column, whole.count(False)))
    marks = ["T" if flag else next(clock_marks) for flag in whole]
    if snapping:
        shifts = [
            offset_form(offsets[rank])[1] if column["datetimes_read_at"] == "utc" else 0
            for rank in range(parsed)
        ]
        ordinals = snapped_to_midnight(column, ordinals, shifts)
    # A withheld count at midnight kept on its side (plan P4-D191), and
    # the counts of different values and of widths reached (P4-D192).
    ordinals = kept_off_midnight(column, ordinals, parsed, whole, gap_lows, gap_highs, offsets=offsets)
    ordinals = units_settled(column, ordinals, parsed, whole, gap_lows, gap_highs)
    holes = set(column.get("missing_by_source", {}))
    # HOW EVERY RANK IS SPELLED (method G7.5, landing 2b.6). Allocated
    # after the instants and the offsets, because which conventions a
    # cell can show depends on the day it writes and the clock it writes
    # it on.
    spellings = written_styles(
        column,
        written_fields(column, ordinals, offsets, parsed, space, resolution),
        parsed,
        resolution,
        offsets,
    )
    content = []
    for rank in range(parsed):
        # Ranks 0 and P-1 are the two published ends, and they are built
        # from the endpoint's own fields rather than from an ordinal
        # (G7.5): the ordinal space has no place for an `SS` of `60`.
        endpoint = None
        ordinal = ordinals[rank]
        if rank == 0:
            endpoint = column["earliest"]
        elif rank == parsed - 1 and parsed >= 2:
            endpoint = column["latest"]
        suffix, shift = offset_form(offsets[rank])
        moved = shift if (
            column["datetimes_read_at"] == "utc"
            and resolution == "datetime"
            and not midnight
        ) else 0
        named = sorted(mark_weights(column))
        width, name_style, marker, zulu = spellings[rank]
        member = column["format"]
        if suffix == "Z" and zulu == "lower":
            # The offset spelled as the source spelled it (landing 2b.6):
            # the reading folds `z` onto `Z`, and the census says which.
            suffix = "z"
        if endpoint is not None:
            if whole[rank]:
                text = endpoint[:10]
            else:
                text = endpoint_cell(
                    endpoint,
                    resolution,
                    column["time_precision"],
                    column["subsecond_digits"],
                    moved,
                    mark=marks[rank],
                    member=member,
                    width=width,
                    name_style=name_style,
                    marker=marker,
                )
            content.append(kept_cell(text + suffix, holes, named, member))
            continue

        def spell(unit, mark=marks[rank], suffix=suffix, moved=moved, bare=whole[rank],
                  member=member, width=width, name_style=name_style, marker=marker):
            if bare:
                # A bare date: the day alone, with no mark, clock or offset.
                # Counted in seconds, the rank already stands at a midnight
                # of its own wall clock (landing 2b.3).
                day = unit if space == "date" else (unit + moved) // 86400
                body = precision_form(
                    day, "date", "date", 0, mark=mark, member=member,
                    width=width, name_style=name_style, marker=marker,
                )
            elif midnight:
                # A whole day, written with a midnight clock at the
                # published precision (plan P4-D39), and since landing
                # 2b.6 with its date half in the column's own member.
                body = precision_form(
                    unit * 86400,
                    "datetime",
                    column["time_precision"],
                    column["subsecond_digits"],
                    mark=mark,
                    member=member,
                    width=width,
                    name_style=name_style,
                    marker=marker,
                )
            else:
                body = precision_form(
                    unit + moved,
                    resolution,
                    column["time_precision"],
                    column["subsecond_digits"],
                    mark=mark,
                    member=member,
                    width=width,
                    name_style=name_style,
                    marker=marker,
                )
            return kept_cell(body + suffix, holes, named, member)

        written = spell(ordinal)
        folded = {hole.strip().lower() for hole in holes}
        if space != "datetime" and written.strip().lower() in folded:
            # G7.5's step off a unit that wears only absent spellings: the
            # nearest unit, earlier before later, first inside this rank's
            # own window and then inside the published range.
            first = ordinal_of(column["earliest"], space)
            last = ordinal_of(column["latest"], space)
            # The window is the rank's own GAP (landing 2b.6): the rank
            # was drawn between the two pinned ranks either side of it.
            window = (max(first, gap_lows[rank]), min(last, gap_highs[rank]))
            for low, high in (window, (first, last)):
                chosen = None
                for away in range(1, len(holes) + 2):
                    for other in (ordinal - away, ordinal + away):
                        if low <= other <= high:
                            candidate = spell(other)
                            if candidate.strip().lower() not in folded:
                                chosen = candidate
                                break
                    if chosen is not None:
                        break
                if chosen is not None:
                    written = chosen
                    break
        content.append(written)
    content = rebalance_marks(marks, content, holes, column["format"])
    content.extend(text_stand_ins(content, column["n_unparsed"]))
    return content


MARK_OF = {"lower_t": "t", "space": " ", "upper_t": "T"}


def ordinal_space(column):
    """The resolution a column's ordinals are counted in (plan P4-D39).

    A column of moments that all stand at midnight ON ITS OWN CLOCK is
    counted in whole days, as a column of dates is; every other column,
    one wholly at local midnight on the shared clock included, in its own
    resolution (landing 2b.3).
    """
    if column.get("all_at_midnight", False) and column.get("datetimes_read_at") == "local":
        return "date"
    return column["resolution"]


def snaps_to_midnight(column):
    """Whether a column's ranks are moved onto a midnight (landing 2b.3).

    A column of moments counted in seconds that publishes a positive
    n_at_midnight: partly at midnight on either clock, or wholly at local
    values at midnight on the shared clock.
    """
    return (
        column["resolution"] == "datetime"
        and ordinal_space(column) == "datetime"
        and (column.get("n_at_midnight") or 0) > 0
    )


def rung_rank(percent, parsed):
    """The rank a published rung is read off: floor((P - 1) * c / 100)."""
    return min(parsed - 1, ((parsed - 1) * percent) // 100)


def ordinal_pins(rungs, parsed):
    """Every rank the published tail PINS, with its published ordinal
    (method G7.3, landing 2b.6).

    The two ends, which the contract's D11 makes the ladder's own ends,
    and each of the nine interior rungs at the rank it is selected from.
    Two rungs selecting off one rank keep the LOWER rung's value, so the
    pins stay in rank order whatever ladder a description carries.
    """
    pins = {}
    if parsed <= 0:
        return pins
    pins[0] = rungs[0]
    if parsed >= 2:
        pins[parsed - 1] = rungs[len(PCT) - 1]
    for place in range(1, len(PCT) - 1):
        rank = rung_rank(PCT[place], parsed)
        if 0 < rank < parsed - 1 and rank not in pins:
            pins[rank] = rungs[place]
    return pins


def pin_bounds(rungs, parsed):
    """The pinned value below and above every rank -- the rank's GAP.

    Read by the construction below and by the step off a unit whose
    every spelling is absent, so the two cannot disagree about the room
    a rank has.  A pinned rank's two bounds are its own value.
    """
    lows = [0] * parsed
    highs = [0] * parsed
    if parsed <= 0:
        return lows, highs
    pins = ordinal_pins(rungs, parsed)
    below = pins[0]
    for rank in range(parsed):
        if rank in pins:
            below = pins[rank]
        lows[rank] = below
    above = pins[max(pins)]
    for rank in reversed(range(parsed)):
        if rank in pins:
            above = pins[rank]
        highs[rank] = above
    return lows, highs


PIN_STEPS = 2 ** 20
PIN_PASSES = 128


def pin_places(pins):
    """Where inside its own unit each pinned rank stands (method G7.3, P4-D130, P4-D138).

    Written from the rule statement.  A unit of the ordinal space is a
    stretch, split into ``PIN_STEPS`` steps.  Two sets of places are
    built, and in both the first pin stands at the first step of its unit
    and the last pin at the step one past its unit's end.

    THE MIDDLES: every other pin at its unit's middle step.

    THE STRAIGHTEST: a heap -- two or more pins sharing a unit that holds
    neither the first pin nor the last -- stands at its unit's middle step
    and never moves; every other pin starts at its unit's middle step and
    then, ``PIN_PASSES`` times, in rank order, moves to the step on the
    straight line between its two neighbours' current steps at its own
    rank -- floor division -- kept between its unit's first and last step.

    With fewer than three pins the straightest is taken.  Otherwise each
    set is scored by ``bend_of_places`` and the middles are taken only
    where they score strictly less.  Returns rank -> step.
    """
    ranks = sorted(pins)
    if not ranks:
        return {}
    middles = {rank: pins[rank] * PIN_STEPS + PIN_STEPS // 2 for rank in ranks}
    middles[ranks[0]] = pins[ranks[0]] * PIN_STEPS
    middles[ranks[-1]] = pins[ranks[-1]] * PIN_STEPS + PIN_STEPS
    end_units = {pins[ranks[0]], pins[ranks[-1]]}
    on_unit = {}
    for rank in ranks:
        on_unit[pins[rank]] = on_unit.get(pins[rank], 0) + 1
    heap = {
        rank: pins[rank] not in end_units and on_unit[pins[rank]] >= 2
        for rank in ranks
    }
    straightest = dict(middles)
    for _pass in range(PIN_PASSES):
        for index in range(1, len(ranks) - 1):
            here = ranks[index]
            if heap[here]:
                continue
            before, after = ranks[index - 1], ranks[index + 1]
            line = straightest[before] + (
                (here - before) * (straightest[after] - straightest[before])
            ) // (after - before)
            first = pins[here] * PIN_STEPS
            straightest[here] = min(max(line, first), first + PIN_STEPS - 1)
    if len(ranks) < 3:
        return straightest
    if bend_of_places(pins, middles) < bend_of_places(pins, straightest):
        return middles
    return straightest


COUNT_SCALE = 2 ** 32


def unit_count(pins, at, unit):
    """How many ranks a set of places spreads onto one unit, in COUNT_SCALE parts.

    One for each pin on the unit.  The ranks strictly between two
    neighbouring pins all count on the first pin's unit where the two
    share a unit or their stretch is empty; otherwise each unit takes
    ``between * overlap * COUNT_SCALE // stretch`` of them, with
    ``overlap`` the steps of the stretch inside the unit.
    """
    ranks = sorted(pins)
    low, high = unit * PIN_STEPS, unit * PIN_STEPS + PIN_STEPS
    total = COUNT_SCALE * sum(1 for rank in ranks if pins[rank] == unit)
    for below, above in zip(ranks, ranks[1:]):
        between = above - below - 1
        if between <= 0:
            continue
        start, stop = at[below], at[above]
        if pins[below] == pins[above] or stop <= start:
            if pins[below] == unit:
                total += between * COUNT_SCALE
            continue
        overlap = min(stop, high) - max(start, low)
        if overlap > 0:
            total += (between * overlap * COUNT_SCALE) // (stop - start)
    return total


def bend_of_places(pins, at):
    """The proportional bend of a set of places' unit counts (P4-D138).

    Over each unit strictly between the first pin's unit and the last
    pin's unit that is a pinned unit or next to one, with ``c`` a unit's
    count plus one whole rank, the sum of the squares of
    ``c(u-1) * c(u+1) * COUNT_SCALE // c(u)**2 - COUNT_SCALE``.
    """
    ranks = sorted(pins)
    first, last = pins[ranks[0]], pins[ranks[-1]]
    units = sorted(
        {unit for rank in ranks for unit in (pins[rank] - 1, pins[rank], pins[rank] + 1)
         if first < unit < last}
    )
    bend = 0
    for unit in units:
        before = unit_count(pins, at, unit - 1) + COUNT_SCALE
        here = unit_count(pins, at, unit) + COUNT_SCALE
        after = unit_count(pins, at, unit + 1) + COUNT_SCALE
        ratio = (before * after * COUNT_SCALE) // (here * here)
        bend += (ratio - COUNT_SCALE) ** 2
    return bend


def spread_ordinals(rungs, parsed, words):
    """Every rank's instant -- method G7.3 as landing 2b.6 rewrites it.

    The published tail pins the two ends and the nine interior rungs to
    their published values.  Every OTHER rank takes an INDEPENDENT draw
    inside the gap between the two pinned ranks either side of it, across
    the stretch between the two pins' places (``pin_places``, P4-D130), in
    the column's own ordinal space, and the draws inside one gap are
    sorted, so the ranks stay ascending.

    ONE WORD PER UNPINNED RANK, AND NONE FOR A PINNED ONE, taken in
    rank order.  The budget is unchanged -- the column is handed `P - 2`
    content words and the pins leave up to nine of them unread -- so
    the shared stream stays in step and no column after a column of
    dates moves.  (The repair pass of landing 2b.6 amended this
    paragraph, which had said that a pinned rank draws its word and
    discards it; the shipped construction reads 389 words of a 400-row
    column's 398, and this mirror follows the method's amended rule.)

    What it replaces: one cell per rank inside its own `1 / P` stratum,
    which gave each day almost exactly its expected count -- a
    below-Poisson spread, where a real table's per-day counts vary at
    least Poisson.
    """
    ordinals = [0] * parsed
    if parsed <= 0:
        return ordinals
    pins = ordinal_pins(rungs, parsed)
    for rank, value in pins.items():
        ordinals[rank] = value
    places = sorted(pins)
    steps = pin_places(pins)
    for step in range(len(places) - 1):
        below = places[step]
        above = places[step + 1]
        low = ordinals[below]
        high = ordinals[above]
        start = steps[below]
        stop = steps[above]
        drawn = []
        for _rank in range(below + 1, above):
            word = next(words)
            place = start + (word * (stop - start)) // TWO64 if stop > start else start
            drawn.append(min(max(place // PIN_STEPS, low), high))
        drawn.sort()
        for place, value in enumerate(drawn):
            ordinals[below + 1 + place] = value
    return ordinals


def ranks_the_tail_pins(parsed):
    """The ranks the published tail pins: the two ends and each rung's rank."""
    flags = [False] * parsed
    if parsed:
        flags[0] = True
        flags[parsed - 1] = True
        for percent in PCT[1:-1]:
            flags[rung_rank(percent, parsed)] = True
    return flags


def midnight_offsets(seconds, column):
    """Every published offset -- real offsets sorted, then (none) -- under
    whose wall clock this instant reads 00:00:00, in that order."""
    found = [
        key
        for key in sorted(column["utc_offsets"])
        if key not in ("(none)", "(withheld)") and (seconds + offset_form(key)[1]) % 86400 == 0
    ]
    if "(none)" in column["utc_offsets"] and seconds % 86400 == 0:
        found.append("(none)")
    return tuple(found)


def rung_pins(column, parsed):
    """Each interior rung's rank, with the rung's own instant and every
    offset it stands at a local midnight under (none where it stands at none)."""
    pins = {}
    for place in range(1, len(PCT) - 1):
        rank = rung_rank(PCT[place], parsed)
        if rank <= 0 or rank >= parsed - 1 or rank in pins:
            continue
        seconds = ordinal_of(column["date_percentiles"][LADDER_KEYS[place]], "datetime")
        pins[rank] = (seconds, midnight_offsets(seconds, column))
    return pins


def instant_offsets(column, parsed):
    """The ranks whose instant the published tail fixes, with their offsets
    (repair pass of landing 2b.3), written from the statement.

    The two ends, each with its published offset.  On a column moved onto
    a midnight, also each rung rank and each rank strictly between two
    pinned ranks -- the ends and the rung ranks -- that stand on one
    instant, each with every offset that instant is a midnight under.
    """
    fixed = {}
    if parsed == 0:
        return fixed
    fixed[0] = (column["earliest_utc_offset"],)
    if parsed >= 2:
        fixed[parsed - 1] = (column["latest_utc_offset"],)
    if not snaps_to_midnight(column):
        return fixed
    instants = {0: ordinal_of(column["earliest"], "datetime")}
    if parsed >= 2:
        instants[parsed - 1] = ordinal_of(column["latest"], "datetime")
    for rank, (seconds, keys) in rung_pins(column, parsed).items():
        instants[rank] = seconds
        fixed[rank] = keys
    ranks = sorted(instants)
    for low, high in zip(ranks, ranks[1:]):
        if instants[low] == instants[high]:
            for rank in range(low + 1, high):
                fixed[rank] = midnight_offsets(instants[low], column)
    return fixed


def written_at_midnight(ordinal, shift, step):
    """Whether the cell written from this instant, on its own wall clock and
    cut to the precision's step, reads as midnight."""
    local = ordinal + shift
    return (local - local % step) % 86400 == 0


def nearest_midnight(ordinal, shift, lowest, highest):
    """The instant of the nearest local midnight (the earlier on a tie),
    brought inside [lowest, highest]; None where none lies inside."""
    local = ordinal + shift
    day = local - local % 86400
    if local - day > day + 86400 - local:
        day += 86400
    first = -((-(lowest + shift)) // 86400) * 86400
    last = ((highest + shift) // 86400) * 86400
    if first > last:
        return None
    return min(max(day, first), last) - shift


def snapped_to_midnight(column, ordinals, shifts):
    """The move onto a midnight (landing 2b.3), written from its statement.

    Pinned ranks never move; every other rank is first brought inside the
    pinned values either side of it.  A pinned rank, or one between two
    pinned ranks of one value, that stands at midnight counts toward
    n_at_midnight.  What is still owed is spread over the other ranks by
    the smooth rotation (credit += owed; chosen where credit reaches the
    number of those ranks, which is taken back).  A chosen rank moves to
    its nearest local midnight inside its bounds; an unchosen rank written
    at midnight moves one precision step later, or earlier where later
    would pass its upper bound; then a second pass over the unchosen ranks,
    in rank order, takes what is still owed.
    """
    parsed = len(ordinals)
    moved = list(ordinals)
    if parsed == 0:
        return moved
    step = 60 if column["time_precision"] == "minute" else 1
    pinned = ranks_the_tail_pins(parsed)
    lows = [0] * parsed
    highs = [0] * parsed
    below = moved[0]
    for rank in range(parsed):
        if pinned[rank]:
            below = moved[rank]
        lows[rank] = below
    above = moved[parsed - 1]
    for rank in reversed(range(parsed)):
        if pinned[rank]:
            above = moved[rank]
        highs[rank] = above
    for rank in range(parsed):
        if not pinned[rank]:
            moved[rank] = min(max(moved[rank], lows[rank]), highs[rank])
    owed = column["n_at_midnight"] or 0
    free = []
    for rank in range(parsed):
        if pinned[rank] or lows[rank] == highs[rank]:
            if written_at_midnight(moved[rank], shifts[rank], step):
                owed -= 1
        else:
            free.append(rank)
    wanted = max(0, min(owed, len(free)))
    chosen = set()
    credit = 0
    for rank in free:
        credit += wanted
        if credit >= len(free):
            credit -= len(free)
            chosen.add(rank)
    reached = 0
    for rank in free:
        if rank in chosen:
            found = nearest_midnight(moved[rank], shifts[rank], lows[rank], highs[rank])
            if found is not None:
                moved[rank] = found
                reached += 1
            continue
        if written_at_midnight(moved[rank], shifts[rank], step):
            if moved[rank] + step <= highs[rank]:
                moved[rank] += step
            elif moved[rank] - step >= lows[rank]:
                moved[rank] -= step
    for rank in free:
        if reached >= wanted:
            break
        if rank in chosen or written_at_midnight(moved[rank], shifts[rank], step):
            continue
        found = nearest_midnight(moved[rank], shifts[rank], lows[rank], highs[rank])
        if found is not None:
            moved[rank] = found
            reached += 1
    return moved


SLASHED_STAMPS = ("month-first-datetime", "day-first-datetime", "slashed-iso-datetime")
MARKS_BY_COMMONNESS = ("upper_t", "space", "lower_t")


def midnight_withheld_for_its_size(column):
    """Whether n_at_midnight is withheld because one side was too small
    (plan P4-D191): a column of moments, not wholly at midnight, and not
    read on the shared clock with its offsets pooled."""
    return (
        column["resolution"] == "datetime"
        and column.get("n_at_midnight") is None
        and not column.get("all_at_midnight", False)
        and not (
            column["datetimes_read_at"] != "local"
            and WITHHELD in column.get("utc_offsets", {})
        )
    )


def kept_off_midnight(column, ordinals, parsed, whole, lows, highs, floor=CASE_SMALL_CELL_FLOOR, offsets=None):
    """Method G7.3's midnight rule for a withheld count (plan P4-D191).

    Fewer than the line -- two, or the floor -- may stand at midnight, or
    fewer than the line off it, each rank asked on its own wall clock. On
    a column counted in seconds, the side is the one most of the published instants
    (the ends and the nine rungs) stand on: off midnight, the unpinned
    ranks written at midnight step one precision unit later, or earlier
    where later leaves the gap, in rank order until fewer than the line
    stand there; at midnight, the unpinned ranks off it take the nearest
    midnight inside their gap, in rank order, until fewer than the line
    stand off it, never all of them.
    """
    ordinals = list(ordinals)
    if parsed < 3 or not midnight_withheld_for_its_size(column):
        return ordinals
    if ordinal_space(column) != "datetime":
        return ordinals
    step = 60 if column["time_precision"] == "minute" else 1
    line = max(2, floor)
    pinned = ranks_the_tail_pins(parsed)
    shifts = [
        offset_form(offsets[rank])[1]
        if column["datetimes_read_at"] == "utc" and offsets is not None else 0
        for rank in range(parsed)
    ]
    at = sum(1 for rank in range(parsed) if written_at_midnight(ordinals[rank], shifts[rank], step))
    pins = sum(1 for flag in pinned if flag)
    pins_at = sum(
        1 for rank in range(parsed)
        if pinned[rank] and written_at_midnight(ordinals[rank], shifts[rank], step)
    )
    if at < line or parsed - at < line:
        return ordinals
    if 2 * pins_at <= pins:
        for rank in range(parsed):
            if at < line:
                break
            if pinned[rank] or whole[rank] or not written_at_midnight(ordinals[rank], shifts[rank], step):
                continue
            if ordinals[rank] + step <= highs[rank]:
                ordinals[rank] += step
            elif ordinals[rank] - step >= lows[rank]:
                ordinals[rank] -= step
            else:
                continue
            at -= 1
        return ordinals
    for rank in range(parsed):
        if parsed - at < line or parsed - at <= 1:
            break
        if pinned[rank] or whole[rank] or written_at_midnight(ordinals[rank], shifts[rank], step):
            continue
        found = nearest_midnight(ordinals[rank], shifts[rank], lows[rank], highs[rank])
        if found is None:
            continue
        ordinals[rank] = found
        at += 1
    return ordinals


def date_counts_reachable(column):
    """Where method G7.3's count pass reaches the count of different values
    (plan P4-D192): read on the column's own clock, at date or datetime
    resolution, carrying no offset and pooling none, writing at most one
    mark between day and clock and pooling none, each census of written
    forms naming at most one form, no bare date beside moments, and the
    same count published folded as raw."""
    if column["datetimes_read_at"] != "local" or column["resolution"] not in ("date", "datetime"):
        return False
    if any(key != "(none)" for key in column.get("utc_offsets", {})):
        return False
    marks = column.get("datetime_separators", {})
    if WITHHELD in marks or len(marks) > 1:
        return False
    for key in ("date_field_widths", "month_name_styles", "quarter_marker_case", "zulu_case"):
        if len(column.get(key, {})) > 1:
            return False
    if column["format"] == "iso-mixed" and column.get("resolution_mix", {}).get("iso-date", 0) > 0:
        return False
    return column["n_distinct"] == column["n_distinct_folded"]


def shows_a_width(column, day_number):
    """A written date shows a field's width where a numeric field is below
    ten; a textual member's month is a name, so only its day can."""
    _year, month, day = civil_from_days(day_number)
    if column["format"] in TEXTUAL_MEMBERS:
        return day < 10
    return month < 10 or day < 10


def units_settled(column, ordinals, parsed, whole, lows, highs):
    """Method G7.3's two count passes (plan P4-D192).

    On a column read on its own clock, writing no bare date, counted in
    days or in seconds: (1) where the member shows widths and the census
    names one convention, ranks the tail does not pin move whole days to
    the nearest day of the other kind inside their gap until as many show
    a width as the convention counts -- nearest move first, ties to the
    lower rank, the earlier day first at one distance; (2) where one
    instant is written one way and the two published counts agree, ranks
    move until the different written units -- days, or the precision's
    minutes or seconds -- number `n_distinct` less the stand-ins: too
    many, with each unpinned run sorted, a run of ranks on one unit
    holding no pinned rank moves whole onto the instant of the rank just
    below or above it, inside its gap, of the same width kind and midnight
    standing, nearest first, then the shorter run, then the lower rank;
    too few, a rank sharing its unit moves to the nearest free
    unit inside its gap keeping both; nearest first, ties to the lower
    rank. The two passes run in that order, again while either moved, at
    most four times; then each run of unpinned ranks is sorted.
    """
    ordinals = list(ordinals)
    if parsed < 3 or column["datetimes_read_at"] != "local" or any(whole):
        return ordinals
    space = ordinal_space(column)
    if space not in ("date", "datetime"):
        return ordinals
    day = 1 if space == "date" else 86400
    step = 60 if space == "datetime" and column["time_precision"] == "minute" else 1
    pinned = [
        flag or lows[rank] >= highs[rank]
        for rank, flag in enumerate(ranks_the_tail_pins(parsed))
    ]
    census = column.get("date_field_widths", {})
    widths = None
    if len(census) == 1 and (
        column["format"] in VARIABLE_WIDTH_MEMBERS or column["format"] in TEXTUAL_MEMBERS
    ):
        widths = next(iter(census.values()))
    distinct = None
    if date_counts_reachable(column):
        distinct = column["n_distinct"] - column["n_unparsed"]
    if widths is None and distinct is None:
        return ordinals

    for _round in range(4):
        changed = False
        if distinct is not None:
            changed = distinct_pass(
                column, ordinals, pinned, lows, highs, day, step, distinct, widths is not None
            ) or changed
        if widths is not None:
            changed = widths_pass(
                column, ordinals, pinned, lows, highs, day, widths, step, distinct is not None
            ) or changed
        if not changed:
            break
    sort_unpinned_runs(ordinals, pinned)
    return ordinals


def sort_unpinned_runs(ordinals, pinned):
    """Sort, in place, each run of ranks the published tail does not pin."""
    start = 0
    while start < len(ordinals):
        if pinned[start]:
            start += 1
            continue
        end = start
        while end < len(ordinals) and not pinned[end]:
            end += 1
        ordinals[start:end] = sorted(ordinals[start:end])
        start = end


def nearest_fitting(value, low, high, fits, by):
    """The nearest instant a whole number of ``by`` away, inside
    [low, high], for which ``fits`` holds; the earlier first at one
    distance; None where none lies inside."""
    away = 1
    while True:
        earlier, later = value - away * by, value + away * by
        if earlier < low and later > high:
            return None
        for candidate in (earlier, later):
            if low <= candidate <= high and fits(candidate):
                return candidate
        away += 1


def widths_pass(column, ordinals, pinned, lows, highs, day, widths, step=1, distinct=False):
    """Pass 1 of `units_settled` (plan P4-D192): the widths count.

    Each rank of the kind in surplus is offered the nearest instant a whole
    number of days away inside its gap whose day is of the other kind --
    where the count of different units is held too, the nearest such
    instant on a unit no rank holds, and the nearest on any unit only where
    none is free, asked again when the rank's turn comes -- and the offers
    are taken nearest first, ties to the lower rank.
    """
    parsed = len(ordinals)
    unit = step if day == 86400 else 1
    held = {}
    for value in ordinals:
        held[value // unit] = held.get(value // unit, 0) + 1
    showing = sum(1 for value in ordinals if shows_a_width(column, value // day))
    if showing == widths:
        return False
    fewer = showing > widths

    def offer(value, low, high):
        def kind(candidate):
            return shows_a_width(column, candidate // day) != fewer

        if not distinct:
            return nearest_fitting(value, low, high, kind, day)
        free = nearest_fitting(
            value, low, high,
            lambda candidate: kind(candidate) and held.get(candidate // unit, 0) <= 0,
            day,
        )
        return free if free is not None else nearest_fitting(value, low, high, kind, day)

    options, bare = [], set()
    for rank in range(parsed):
        if pinned[rank] or shows_a_width(column, ordinals[rank] // day) != fewer:
            continue
        if (lows[rank], highs[rank]) in bare:
            continue
        found = offer(ordinals[rank], lows[rank], highs[rank])
        if found is None:
            if day == 1 and not distinct:
                bare.add((lows[rank], highs[rank]))
            continue
        options.append((abs(found - ordinals[rank]), rank, found))
    changed = False
    for _distance, rank, found in sorted(options):
        if showing == widths:
            break
        if distinct:
            found = offer(ordinals[rank], lows[rank], highs[rank])
            if found is None:
                continue
            held[ordinals[rank] // unit] -= 1
            held[found // unit] = held.get(found // unit, 0) + 1
        ordinals[rank] = found
        showing += -1 if fewer else 1
        changed = True
    return changed


def distinct_pass(column, ordinals, pinned, lows, highs, day, step, distinct, widths):
    """Pass 2 of `units_settled` (plan P4-D192): the count of different units."""
    parsed = len(ordinals)
    unit = step if day == 86400 else 1

    def standing(value, target):
        if widths and shows_a_width(column, value // day) != shows_a_width(column, target // day):
            return False
        return day != 86400 or written_at_midnight(value, 0, step) == written_at_midnight(target, 0, step)

    held = {}
    for value in ordinals:
        held[value // unit] = held.get(value // unit, 0) + 1
    count = len(held)
    changed = False
    if count > distinct:
        sort_unpinned_runs(ordinals, pinned)
        options = []
        first = 0
        while first < parsed:
            last = first
            while last + 1 < parsed and ordinals[last + 1] // unit == ordinals[first] // unit:
                last += 1
            if not any(pinned[first:last + 1]):
                for other in (first - 1, last + 1):
                    if not 0 <= other < parsed:
                        continue
                    target = ordinals[other]
                    if lows[first] <= target <= highs[first] and standing(ordinals[first], target):
                        options.append((abs(target - ordinals[first]), last - first + 1, first, other))
            first = last + 1
        for _distance, size, first, other in sorted(options):
            if count == distinct:
                break
            own = ordinals[first] // unit
            target = ordinals[other]
            if target // unit == own or held[own] != size or held.get(target // unit, 0) <= 0:
                continue
            if not lows[first] <= target <= highs[first]:
                continue
            if any(value // unit != own for value in ordinals[first:first + size]):
                continue
            if not standing(ordinals[first], target):
                continue
            ordinals[first:first + size] = [target] * size
            held[own] = 0
            held[target // unit] += size
            count -= 1
            changed = True
    elif count < distinct:
        options, full = [], set()
        for rank in range(parsed):
            if pinned[rank] or held[ordinals[rank] // unit] < 2:
                continue
            if (lows[rank], highs[rank]) in full:
                continue
            value = ordinals[rank]
            found = nearest_fitting(
                value, lows[rank], highs[rank],
                lambda candidate, value=value: held.get(candidate // unit, 0) == 0 and standing(value, candidate),
                unit,
            )
            if found is None:
                if not widths and day == 1:
                    full.add((lows[rank], highs[rank]))
                continue
            options.append((abs(found - value), rank, found))
        for _distance, rank, found in sorted(options):
            if count == distinct:
                break
            own = ordinals[rank] // unit
            if held[own] < 2:
                continue
            if held.get(found // unit, 0) > 0:
                value = ordinals[rank]
                found = nearest_fitting(
                    value, lows[rank], highs[rank],
                    lambda candidate, value=value: held.get(candidate // unit, 0) == 0 and standing(value, candidate),
                    unit,
                )
                if found is None:
                    continue
            held[own] -= 1
            held[found // unit] = 1
            ordinals[rank] = found
            count += 1
            changed = True
    if count < distinct:
        changed = standing_swaps(
            column, ordinals, pinned, lows, highs, day, step, unit, held, widths, distinct - count
        ) or changed
    return changed


def standing_of(column, value, day, step, widths):
    """A unit's width kind (where widths are held) and whether it stands at
    midnight (on a column counted in seconds)."""
    return (
        bool(widths) and shows_a_width(column, value // day),
        day == 86400 and written_at_midnight(value, 0, step),
    )


def nearest_free_where(column, value, low, high, day, step, unit, held, widths, standing, same):
    """The nearest free unit inside [low, high] of (``same``) or not of a
    standing; a unit at a midnight is sought one day at a time, from the
    one starting the value's own day outward, and every other among the
    units ``unit`` apart from the value, outward; earlier first."""
    by, base, away = unit, value, 1
    if same and standing[1]:
        by, base, away = 86400, value - value % 86400, 0
    while True:
        earlier, later = base - away * by, base + away * by
        if earlier < low and later > high:
            return None
        for candidate in (earlier, later):
            if not low <= candidate <= high or held.get(candidate // unit, 0) > 0:
                continue
            if (standing_of(column, candidate, day, step, widths) == standing) == same:
                return candidate
        away += 1


def standing_swaps(column, ordinals, pinned, lows, highs, day, step, unit, held, widths, owed):
    """The trade of plan P4-D192: in rank order, an unpinned rank sharing
    its unit takes the nearest free unit of another standing inside its gap,
    where the first unpinned rank of that standing alone on its unit can take
    the nearest free unit of the first rank's standing inside its own gap;
    both move, every standing's count holds, and one more unit is held."""
    changed = False
    for rank in range(len(ordinals)):
        if owed <= 0:
            break
        if pinned[rank] or held[ordinals[rank] // unit] < 2:
            continue
        own = standing_of(column, ordinals[rank], day, step, widths)
        off = nearest_free_where(column, ordinals[rank], lows[rank], highs[rank], day, step, unit, held, widths, own, False)
        if off is None:
            continue
        wanted = standing_of(column, off, day, step, widths)
        for other in range(len(ordinals)):
            if other == rank or pinned[other]:
                continue
            value = ordinals[other]
            if held[value // unit] != 1 or standing_of(column, value, day, step, widths) != wanted:
                continue
            onto = nearest_free_where(column, value, lows[other], highs[other], day, step, unit, held, widths, own, True)
            if onto is None or onto // unit == off // unit:
                continue
            held[ordinals[rank] // unit] -= 1
            held[off // unit] = 1
            held[value // unit] = 0
            held[onto // unit] = 1
            ordinals[rank], ordinals[other] = off, onto
            owed -= 1
            changed = True
            break
    return changed


def permitted_marks(column):
    """The marks a column's own reader accepts, commonest first (contract D12).

    All three on an ISO reading; a space alone on a slashed stamp.
    """
    if column["format"] in SLASHED_STAMPS:
        return ("space",)
    return MARKS_BY_COMMONNESS


def mark_weights(column):
    """How many values each mark is written on (plan P4-D39, landing 2b.3).

    Written from the statement: every named count as published, and a
    withheld pool split EVENLY over the permitted marks the census leaves
    unnamed, a remainder going one each to those marks in the order
    upper_t, space, lower_t; a mark given no value is left out.  Where
    the census leaves no permitted mark unnamed the pool is not split.
    """
    census = column.get("datetime_separators", {})
    weights = {name: count for name, count in census.items() if name != "(withheld)"}
    if "(withheld)" not in census:
        return weights
    unnamed = [name for name in permitted_marks(column) if name not in census]
    if not unnamed:
        return weights
    share, rest = divmod(census["(withheld)"], len(unnamed))
    for place, name in enumerate(unnamed):
        given = share + (1 if place < rest else 0)
        if given > 0:
            weights[name] = given
    return weights


def _separator_allocation(column, parsed):
    """Which mark each rank carries between day and clock (plan P4-D39).

    A smooth weighted rotation, written here from its statement rather
    than from the implementation: every rank adds each mark's weight to
    that mark's credit, the mark holding the most credit is chosen --
    the first in sorted order among equals -- and the weights' total is
    taken back from it.  The weights are ``mark_weights``: the named
    counts, and a withheld pool spent on the unnamed permitted marks
    (landing 2b.3).  Ranks those weights leave over are added to the
    commonest named mark's weight, or where nothing is named to the first
    permitted mark in the order upper_t, space, lower_t.  No rank is
    pinned, and no word is drawn.
    """
    if column["resolution"] != "datetime" or parsed == 0:
        return ["T"] * parsed
    census = column.get("datetime_separators", {})
    named = {name: count for name, count in census.items() if name != "(withheld)"}
    if not named and "(withheld)" not in census:
        return ["T"] * parsed
    weights = mark_weights(column)
    if named:
        order = sorted(named)
        top = max(order, key=lambda name: (named[name], -order.index(name)))
    else:
        top = permitted_marks(column)[0]
    left = parsed - sum(weights.values())
    if left > 0:
        weights[top] = weights.get(top, 0) + left
    order = sorted(weights)
    total = sum(weights.values())
    credit = dict.fromkeys(order, 0)
    marks = []
    for _rank in range(parsed):
        for name in order:
            credit[name] += weights[name]
        chosen = max(order, key=lambda name: (credit[name], -order.index(name)))
        credit[chosen] -= total
        marks.append(MARK_OF[chosen])
    return marks


ALTERNATE_MARK = {"T": " ", "t": " ", " ": "T"}


def kept_cell(text, holes, named=(), member="iso-datetime"):
    """G7.5's absent-spelling exception, written from its statement.

    A cell whose text is a declared absent spelling is offered, in turn,
    each mark the column's census names (in the census's sorted order)
    and then the other common form -- a space for `T` or `t`, a `T` for a
    space -- and takes the first whose text is not absent; it keeps its
    own text where every offer is absent.  An absent spelling is matched
    whatever the case of its letters, as the reading of a file matches
    it: a `t` stamp is absent where its `T` form is declared.
    """
    folded = {hole.strip().lower() for hole in holes}
    if text.strip().lower() not in folded or len(text) < 11:
        return text
    if member not in ("iso-datetime", "iso-mixed"):
        # NO OTHER MEMBER PUTS ITS MARK AT CHARACTER ELEVEN (landing
        # 2b.6): `3/17/2024 14:05` has a `4` there and `17-MAR-2024` a
        # `2`, so the splice below would rewrite a digit of the date.
        # These members also have exactly one permitted mark, a space,
        # so there is no other mark to offer and nothing is lost.
        return text
    if text[10] not in ALTERNATE_MARK:
        return text
    offers = [MARK_OF[name] for name in sorted(named) if MARK_OF[name] != text[10]]
    if ALTERNATE_MARK[text[10]] not in offers:
        offers.append(ALTERNATE_MARK[text[10]])
    for mark in offers:
        other = text[:10] + mark + text[11:]
        if other.strip().lower() not in folded:
            return other
    return text


def rebalance_marks(wanted, cells, holes, member="iso-datetime"):
    """G7.5's repair of the census after that exception (plan P4-D39).

    Each cell whose mark the exception changed hands the mark it owed to
    the first rank, in rank order, that was allocated the mark the
    changed cell now wears, still wears it, was not touched before, and
    whose new text is not absent.  A repeated text is allowed.  No rank
    is touched twice.
    """
    cells = list(cells)
    if member not in ("iso-datetime", "iso-mixed"):
        # The swap this repairs never happens on these members (landing
        # 2b.6): `kept_cell` declines to respell them, because character
        # eleven of their cells is a digit of the date rather than the
        # mark, and reading it as a mark here counted a `4` as a
        # spelling on every unpadded slashed stamp.
        return cells
    touched = set()
    folded = {hole.strip().lower() for hole in holes}
    for rank, cell in enumerate(cells):
        if rank in touched or len(cell) < 11 or cell[10] == wanted[rank]:
            continue
        owed, spare = wanted[rank], cell[10]
        for other, candidate in enumerate(cells):
            if other in touched or len(candidate) < 11:
                continue
            if wanted[other] != spare or candidate[10] != spare:
                continue
            changed = candidate[:10] + owed + candidate[11:]
            if changed.strip().lower() in folded:
                continue
            # A repair never leaves the column one spelling fewer.
            if cells.count(candidate) < 2 and changed in cells:
                continue
            # ...nor one value fewer once case is ignored, which is what
            # the reading that names a column's kind counts.
            was, becomes = candidate.strip().casefold(), changed.strip().casefold()
            if was != becomes and sum(
                1 for cell in cells if cell.strip().casefold() == was
            ) < 2 and any(cell.strip().casefold() == becomes for cell in cells):
                continue
            cells[other] = changed
            touched.add(other)
            break
    return cells


def form_allocation(column, parsed):
    """Which ranks are written as bare dates (landing 2b.3, plan P4-D39).

    Written from the statement: only on an iso-mixed column whose every
    value stands at midnight.  The ranks whose instant is published are
    settled first, in rank order -- the ranks ``instant_offsets`` names,
    with the offsets it gives them.  One with offsets, none of
    them a marker key, is a moment; on the shared clock, one that may
    carry (none) or (withheld) is a bare date while iso-date has a count
    left (repair pass of landing 2b.3).  Each takes one from its form's
    count.  The other ranks, in order, take the two forms by the smooth
    weighted rotation -- both counts added to their credits, the form with
    more credit taken (iso-date on a tie), the total given back.
    """
    whole = [False] * parsed
    if column["format"] != "iso-mixed" or parsed == 0:
        return whole
    if not column.get("all_at_midnight", False):
        return whole
    published = instant_offsets(column, parsed)
    dates = column["resolution_mix"]["iso-date"]
    moments = column["resolution_mix"].get("iso-datetime", 0)
    pinned = set()
    for rank in sorted(published):
        keys = published[rank]
        if not keys:
            continue
        if all(key not in ("(none)", "(withheld)") for key in keys):
            pinned.add(rank)
            moments = max(0, moments - 1)
        elif column["datetimes_read_at"] == "utc" and dates > 0:
            pinned.add(rank)
            whole[rank] = True
            dates -= 1
    weights = {"iso-date": dates, "iso-datetime": moments}
    order = sorted(weights)
    total = sum(weights.values())
    credit = dict.fromkeys(order, 0)
    for rank in range(parsed):
        if rank in pinned:
            continue
        for name in order:
            credit[name] += weights[name]
        chosen = max(order, key=lambda name: (credit[name], -order.index(name)))
        credit[chosen] -= total
        whole[rank] = chosen == "iso-date"
    return whole


def _offset_allocation(column, parsed, whole=None, pins=None):
    """Which offset each rank carries -- method section G7.4.

    A rank written as a bare date carries no offset: it is settled first,
    taking one from (none), or from (withheld) where (none) is spent
    (landing 2b.3).  An END takes the key published for it, a marker key
    included, which then writes no offset.  A rung rank of a column wholly
    at local midnight on the shared clock takes, after the ends, the first
    offset in ``pins`` that has a count left.
    """
    remaining = dict(column["utc_offsets"])
    allocated = [None] * parsed
    for rank, bare in enumerate(whole or []):
        if not bare:
            continue
        for key in ("(none)", "(withheld)"):
            if remaining.get(key, 0) > 0:
                remaining[key] -= 1
                break
        allocated[rank] = "(none)"
    for rank, field in ((0, "earliest_utc_offset"), (parsed - 1, "latest_utc_offset")):
        named = column[field]
        if allocated[rank] is not None:
            continue
        if remaining.get(named, 0) > 0:
            allocated[rank] = named
            remaining[named] -= 1
    for rank, keys in sorted((pins or {}).items()):
        for key in keys:
            if allocated[rank] is None and remaining.get(key, 0) > 0:
                allocated[rank] = key
                remaining[key] -= 1
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
    the digits themselves with a non-zero leading digit wherever there
    is more than one, so the spelling's length is its digit count and
    the lone figure 0 is one of the ten one-figure spellings; the code band writes
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
        if band == FIGURES and length == 1:
            # The lone figure 0 is a whole number one figure long, and
            # its length is its count of figures (plan P4-D155); it is
            # the LAST one-figure number, after 1 to 9 (plan P4-D162).
            return ONE_FIGURE_ORDER, length, None, ""
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


# ---------------------------------------- the LAYOUT of a record number
#
# Contract section 7.12, written from that section alone.  A layout is
# one mark per character saying what KIND of character stood there and
# never which one, so the census of layouts is also the census of
# LENGTHS -- a fact `min_length` and `max_length` cannot carry, since
# they give only the two ends.

LAYOUT_MARKS = "-./_:#*()[]+,{}"
LAYOUT_DIGIT = "%"
LAYOUT_UPPER = "@"
LAYOUT_LOWER = "&"
LAYOUT_LOWER_HEX = "~"
LAYOUT_UPPER_HEX = "^"
LAYOUT_LEADING_ZERO = "!"
LAYOUT_PLACEHOLDERS = "%@&~^!"
LAYOUT_FORM_LIMIT = 64
LAYOUT_PLAIN = "plain"
LAYOUT_HEX_LOWER = "lower-hexadecimal"
LAYOUT_HEX_UPPER = "upper-hexadecimal"


def _ascii_digit(character):
    return "0" <= character <= "9"


def _ascii_letter(character):
    return ("a" <= character <= "z") or ("A" <= character <= "Z")


def _described_by_a_layout(text):
    """Whether this census describes one cell at all (C6-127).

    A cell carrying a PLACEHOLDER is refused and a cell of marks ALONE
    is refused, and between them they are what makes "no cell that has
    a layout can be spelled the same as any layout" true.  A SPACE may
    stand between two other characters, one at a time, and nowhere else
    (plan P4-D127).
    """
    if not text or len(text) > LAYOUT_FORM_LIMIT:
        return False
    content = 0
    before = ""
    for character in text:
        if character in LAYOUT_PLACEHOLDERS:
            return False
        if _ascii_digit(character) or _ascii_letter(character):
            content += 1
        elif character in LAYOUT_MARKS:
            pass
        elif character == " " and before not in ("", " "):
            pass
        else:
            return False
        before = character
    return content >= 1 and before != " "


def layout_convention(values):
    """Which alphabet convention a whole COLUMN is written in (C6-128).

    Hexadecimal where every letter of every described cell is one of
    a to f in either case and there is at least one letter; its case is
    the case more of those letters wear, lower on a tie (plan P4-D125).
    Decided for the column, which is that clause's whole point: decided
    per character a figure is ambiguous between the two cases, and a
    column of braced GUIDs shatters into one layout per cell.

    And only where some position, among the described cells of one
    length, holds a letter in one cell and a figure in another (plan
    P4-D154): letters a to f that never trade places with a figure are
    letters, and `A1000000` beside `F1000005` is a letter and seven
    figures, not eight hexadecimal characters.
    """
    lower = upper = 0
    kinds_at = {}
    for value in values:
        if not _described_by_a_layout(value):
            continue
        for place, character in enumerate(value):
            if _ascii_digit(character):
                kinds_at.setdefault((len(value), place), set()).add("figure")
                continue
            if not _ascii_letter(character):
                continue
            kinds_at.setdefault((len(value), place), set()).add("letter")
            if character in "abcdef":
                lower += 1
                continue
            if character in "ABCDEF":
                upper += 1
                continue
            return LAYOUT_PLAIN
    if lower + upper < 1:
        return LAYOUT_PLAIN
    if not any(len(kinds) == 2 for kinds in kinds_at.values()):
        return LAYOUT_PLAIN
    return LAYOUT_HEX_UPPER if upper > lower else LAYOUT_HEX_LOWER


def _layout_mark(character, convention, filling):
    if _ascii_digit(character):
        if filling:
            return LAYOUT_LEADING_ZERO
        if convention == LAYOUT_HEX_LOWER:
            return LAYOUT_LOWER_HEX
        if convention == LAYOUT_HEX_UPPER:
            return LAYOUT_UPPER_HEX
        return LAYOUT_DIGIT
    if _ascii_letter(character):
        if convention == LAYOUT_HEX_LOWER:
            return LAYOUT_LOWER_HEX
        if convention == LAYOUT_HEX_UPPER:
            return LAYOUT_UPPER_HEX
        return LAYOUT_LOWER if "a" <= character <= "z" else LAYOUT_UPPER
    return character


def layout_of(text, convention):
    """The layout of one cell (C6-127), or "" where there is none."""
    if not _described_by_a_layout(text):
        return ""
    # THE ZERO FILL (plan P4-D126): in a plain column, every nought of a
    # cell of figures alone that stands before its first other figure,
    # the last character excepted.
    fill = 0
    if convention == LAYOUT_PLAIN and all(_ascii_digit(c) for c in text):
        while fill < len(text) - 1 and text[fill] == "0":
            fill += 1
    built = ""
    for place, character in enumerate(text):
        built += _layout_mark(character, convention, place < fill)
    return built


def layout_room(name):
    """How many different cells could have worn one layout (C6-130)."""
    room = 1
    for character in name:
        if character == LAYOUT_DIGIT:
            room *= 10
        elif character in (LAYOUT_UPPER, LAYOUT_LOWER):
            room *= 26
        elif character in (LAYOUT_LOWER_HEX, LAYOUT_UPPER_HEX):
            room *= 16
    return room


def _shares_a_factor(one, other):
    left, right = one, other
    while right:
        left, right = right, left % right
    return left != 1


def _stepped_around(step, room):
    """``step`` moved around ``room`` so that every position varies.

    Method G9.6 fills a layout by the arithmetic G8.3 fills a written
    form by: a stride coprime to the room is a bijection on it, taken
    near the golden section of the room and walked up to the first
    value sharing no factor with it.
    """
    if room < 4:
        return step % max(room, 1)
    stride = max(room * 61803 // 100000, 1)
    while _shares_a_factor(stride, room):
        stride += 1
    return (step * stride) % room


def layout_stepped(step, room):
    """``step`` moved around a layout's room (method G9.6, plan P4-D128).

    A stride coprime to the room is a bijection on it.  The stride is the
    golden section of the room taken EXACTLY in whole numbers -- the whole
    part of the room times the square root of five, less the room, halved
    -- and walked up to the first value sharing no factor with the room.
    """
    if room < 4:
        return step % max(room, 1)
    stride = max((math.isqrt(5 * room * room) - room) // 2, 1)
    while _shares_a_factor(stride, room):
        stride += 1
    return (step * stride) % room


def filled_layout(layout, step):
    """One spelling of one layout, stepped (method G9.6).

    LEFTMOST FIRST, so consecutive steps differ in the leading
    characters rather than the trailing ones -- which is what stops a
    column of record numbers coming out as a near-consecutive walk.
    `!` takes the figure nought and spends no step, because that is
    exactly what the mark says; the figure after a fill must not be a
    nought, and `_fits_its_slot` steps over a filling where it is,
    because that cell recounts one nought deeper.
    """
    figures = "0123456789"
    upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    lower = "abcdefghijklmnopqrstuvwxyz"
    lower_hex = "0123456789abcdef"
    upper_hex = "0123456789ABCDEF"
    place = layout_stepped(step, layout_room(layout))
    spelling = ""
    for character in layout:
        if character == LAYOUT_DIGIT:
            spelling += figures[place % 10]
            place //= 10
        elif character == LAYOUT_UPPER:
            spelling += upper[place % 26]
            place //= 26
        elif character == LAYOUT_LOWER:
            spelling += lower[place % 26]
            place //= 26
        elif character == LAYOUT_LOWER_HEX:
            spelling += lower_hex[place % 16]
            place //= 16
        elif character == LAYOUT_UPPER_HEX:
            spelling += upper_hex[place % 16]
            place //= 16
        elif character == LAYOUT_LEADING_ZERO:
            spelling += "0"
        else:
            spelling += character
    return spelling


def layout_offer(column):
    """The layouts a column publishes, in the order they are offered.

    Sorted, and without the pooled key, which names no layout. It is a
    function of its own so that the frozen case's registered mutant can
    take it away: with nothing offered every cell falls back to the
    band enumeration and the committed cells move.
    """
    census = column.get("layout_forms") or {}
    return [name for name in sorted(census) if name != WITHHELD]


# ------------------------- the literal PREFIX of a record number (7.12a)
#
# Owner ruling of 2026-09-17, item 1, and method G9.6a, written from the
# rule statement.  `layout_prefixes` maps `(column)` to the text every
# present cell opens with, or a named layout to the text its own cells
# open with.  A prefixed layout is written as its TEMPLATE: the layout
# with its opening marks replaced by the prefix, filled as a layout is
# filled -- a placeholder from the step, every other character standing
# as itself.

PREFIX_OF_THE_COLUMN = "(column)"


def prefix_layout(text):
    """The layout of a prefix or a template: each letter marked by its case."""
    built = ""
    for character in text:
        if "a" <= character <= "z":
            built += LAYOUT_LOWER
        elif "A" <= character <= "Z":
            built += LAYOUT_UPPER
        else:
            built += character
    return built


def templated_census(column):
    """The census keyed by TEMPLATE (method G9.6a).

    A function of its own so the frozen cases' registered mutant can take
    it away: with the layouts left as they were published, the opening
    letters are filled from the step, and the committed cells move.
    """
    census = column.get("layout_forms") or {}
    prefixes = column.get("layout_prefixes") or {}
    whole = prefixes.get(PREFIX_OF_THE_COLUMN, "")
    templated = {}
    for name in sorted(census):
        prefix = prefixes.get(name, whole)
        if name == WITHHELD or not prefix:
            templated[name] = census[name]
        else:
            templated[prefix + name[len(prefix):]] = census[name]
    return templated


def wears_template(candidate, template, convention):
    """The cell recounts into the template's layout and holds its letters."""
    if layout_of(candidate, convention) != prefix_layout(template):
        return False
    return all(
        candidate[place] == mark
        for place, mark in enumerate(template)
        if _ascii_letter(mark)
    )


def worn_template(candidate, convention, keys):
    """The key of ``keys`` a cell is counted under, or its own layout."""
    for template in sorted(keys):
        if wears_template(candidate, template, convention):
            return template
    return layout_of(candidate, convention)


def breaks_a_prefix(candidate, convention, prefixes):
    """Whether a cell does not open with a published prefix it owes (G9.6a)."""
    if PREFIX_OF_THE_COLUMN in prefixes:
        prefix = prefixes[PREFIX_OF_THE_COLUMN]
    else:
        prefix = prefixes.get(layout_of(candidate, convention), "")
    return bool(prefix) and not candidate.startswith(prefix)


# Contract section 14.4's vocabulary of "no value", written from that
# section: seventeen spellings matched after trimming and case folding,
# and one matched byte for byte.
ABSENT_FOLDED = (
    "", "-", "--", ".", "?", "n/a", "na", "nan", "none", "null",
    "#DIV/0!", "#N/A", "#NAME?", "#NULL!", "#NUM!", "#REF!", "#VALUE!",
)
ABSENT_EXACT = ("NaT",)


def reads_as_absent(text, holes=()):
    """Whether a reader of the description reads this spelling as absent.

    Method G9.6 (plan P4-D158): a record number is never written in a
    spelling of contract section 14.4's vocabulary, nor in one the
    document publishes as the spelling of an absent cell, matched after
    trimming and case folding.  A function of its own so the frozen
    case's registered mutant can take it away: with nothing read as
    absent the layout fills `NA`, and the committed cells move.
    """
    if text in ABSENT_EXACT:
        return True
    body = folded(text)
    if any(body == folded(word) for word in ABSENT_FOLDED):
        return True
    return any(body == folded(hole) for hole in holes)


def _fits_its_slot(candidate, layout, convention, band, whole_numbers, holes=()):
    """Whether one filling of a layout may stand in a slot, freeness aside.

    Every guard method G9.6 states but the one about what the column has
    already written: the cell recounts into the band it was made for,
    reads as a number exactly where that band says it must, is no
    spelling a reader reads as absent, and RECOUNTS INTO THE LAYOUT IT
    WAS WRITTEN TO -- `%%%%` filled at a step whose leading figure is
    nought spells `0123`, whose layout is `!%%%`.
    """
    if not wears_template(candidate, layout, convention):
        return False
    if reads_as_absent(candidate, holes):
        return False
    bare = candidate.strip()
    digits = bool(bare) and set(bare) <= DIGIT_CHARACTERS
    coded = bool(bare) and set(bare) <= CODE_CHARACTERS
    if band == FIGURES and not digits:
        return False
    if band == CODE_BAND and (digits or not coded):
        return False
    if band not in (FIGURES, CODE_BAND) and (digits or coded):
        return False
    if whole_numbers and not _is_a_whole_number(candidate):
        return False
    if not whole_numbers and _is_a_number(candidate) != (band == FIGURES):
        return False
    return True


FORMULA_OPENINGS = ("=", "+", "-", "@", " ")


def _a_signed_number(layout):
    """A sign, then figures with at most one point among them (P4-D156).

    Such a layout is worn only by a signed number, so the census proves
    the table held sign-leading numbers and the opening is not refused;
    every other layout opening with a formula character still is.
    """
    body = layout[1:]
    return (
        layout[:1] in ("-", "+")
        and body.count("%") >= 1
        and body.count(".") <= 1
        and set(body) <= {"%", "."}
    )
LAYOUT_STEPS = 4096
LAYOUT_ADMISSION_STEPS = 64


def _layout_spelling(layout, convention, steps, used, band, whole_numbers, holes=()):
    """The next free spelling of one layout that keeps its slot's band.

    At most 4,096 fillings are read, counted on from wherever this
    layout's own walk stopped last; the opening character is never one
    a spreadsheet reads as the start of a formula, and every other guard
    is `_fits_its_slot`.
    """
    room = layout_room(layout)
    ceiling = min(room, LAYOUT_STEPS)
    tried = 0
    while tried < ceiling:
        candidate = filled_layout(layout, steps[layout])
        steps[layout] += 1
        tried += 1
        if candidate[:1] in FORMULA_OPENINGS and not _a_signed_number(layout):
            return None
        if candidate in used:
            continue
        if _fits_its_slot(
            candidate, layout, convention, band, whole_numbers, holes
        ):
            return candidate
    return None


def _layout_admits(layout, convention, band, whole_numbers):
    """Whether a slot of one band can wear one layout at all (G9.6).

    Read off the layout's own first 64 fillings (or all of them, where
    it has fewer), with every guard of `_fits_its_slot` and nothing
    about what the column has written.
    """
    for step in range(min(layout_room(layout), LAYOUT_ADMISSION_STEPS)):
        candidate = filled_layout(layout, step)
        if candidate[:1] in FORMULA_OPENINGS and not _a_signed_number(layout):
            return False
        if _fits_its_slot(candidate, layout, convention, band, whole_numbers):
            return True
    return False


def _convention_of_the_keys(offered):
    """Which alphabet convention a column's PUBLISHED KEYS were built in.

    Read off the keys and off nothing else, because that is all a
    generator has: a hexadecimal mark appears in a column's layouts
    exactly when the producer decided the whole column was hexadecimal
    (C6-128), so one such mark anywhere settles it.
    """
    for layout in sorted(offered):
        for character in layout:
            if character == LAYOUT_LOWER_HEX:
                return LAYOUT_HEX_LOWER
            if character == LAYOUT_UPPER_HEX:
                return LAYOUT_HEX_UPPER
    return LAYOUT_PLAIN


def layout_preferences(
    column, groups, families, bands, windows, pinned, demands=None,
):
    """Which published layout each identity is offered FIRST (method G9.6).

    Written from the rule statement.  The identities are visited with
    the ones carrying a published length END first, then by the number
    of cells they cover, largest first, then in position order.  Each
    visit takes, among the published layouts with at least that many
    cells left, a length the slot's window holds, and a filling the
    slot's band can wear (`_layout_admits`), the one the SMOOTH
    WEIGHTED ROTATION names: every layout that family can wear has its
    published count times the group's size added to its credit, the
    candidate with the most credit is taken -- the earliest in sorted
    order on a tie -- and the family's total times the group's size is
    taken back from it.  Credit is kept per family.  ``""`` is no
    preference.

    AN IDENTITY CARRIES ITS PARTNERS' CELLS (plan P4-D157).  ``demands``
    maps an identity's position to the cell counts of the partners G9.3
    hands it, first partner first.  Where any partner of any published
    layout wears a published layout (`partner_layouts`), an identity
    owing partners is visited after the end carriers and before every
    identity owing none, and a layout is a candidate for it only where
    its own remaining count covers the identity and each published
    layout its partners wear has their cells left -- the layout itself
    counting both where they coincide; all of them are debited together.
    A partner wearing no published layout is debited from the cells the
    census names no layout for (plan P4-D196).

    A function of its own so the frozen case's registered mutant can
    take it away: with no preference every group is offered the layouts
    in sorted order, the singletons that come first take the first
    layout, and the committed cells move.
    """
    offered = layout_offer(column)
    census = column.get("layout_forms") or {}
    convention = _convention_of_the_keys(offered)
    remaining = {name: census[name] for name in offered}
    # The cells the census names no layout for are a quota too, under the
    # empty name a partner wearing no published layout is predicted under
    # (plan P4-D196).
    remaining[""] = max(
        0, column["n_present"] - sum(census[name] for name in offered)
    )
    whole_numbers = column["all_whole_numbers"]
    preferred = [""] * len(groups)
    wearable = {}
    credits = {}
    demands = demands or {}
    paired = partners_wear_published_layouts(column, convention, demands)
    visits = sorted(
        (
            0 if position in pinned else 1,
            -1 if paired and demands.get(position) else 0,
            -groups[position],
            position,
        )
        for position in range(len(groups))
    )
    for _pinned, _owes, _size, position in visits:
        family = families[position]
        if family not in wearable:
            wearable[family] = [
                name for name in offered
                if _layout_admits(name, convention, bands[position], whole_numbers)
            ]
            credits[family] = {name: 0 for name in wearable[family]}
        covering = groups[position]
        weight = sum(census[name] for name in wearable[family])
        best = ""
        best_credit = 0
        best_needs = {}
        for name in wearable[family]:
            if demands.get(position) and _a_signed_number(name):
                # A signed layout is not given to an identity owed a
                # partner (plan P4-D156): its partner could only be
                # edge-spaced, a second cell opening with the sign.
                continue
            needs = {name: covering}
            if paired and demands.get(position):
                owed = demands[position]
                worn = partner_layouts(
                    name, convention, len(owed), column, offered
                )
                for order, cells in enumerate(owed):
                    if worn[order] in remaining:
                        needs[worn[order]] = needs.get(worn[order], 0) + cells
            if any(remaining[key] < needs[key] for key in needs):
                continue
            if len(name) not in windows[position]:
                continue
            credit = credits[family][name] + census[name] * covering
            if best == "" or credit > best_credit:
                best, best_credit, best_needs = name, credit, needs
        if best == "":
            continue
        for name in wearable[family]:
            credits[family][name] += census[name] * covering
        credits[family][best] -= weight * covering
        for key, cells in best_needs.items():
            remaining[key] -= cells
        preferred[position] = best
    return preferred


PARTNER_LAYOUT_STEPS = 64


def partner_layouts(layout, convention, count, column, offered):
    """The published layouts the first ``count`` partners of a layout wear.

    Method G9.6 (plan P4-D157), written from the rule statement.  The
    layout's first filling is walked through its partner family in
    G9.3's order, at most 64 members, inside the published length range;
    the members wearing a PUBLISHED layout are taken in that order, one
    per partner, and a partner past them wears "".
    """
    worn = []
    family = partner_family(filled_layout(layout, 0), column["max_length"])
    for step, member in enumerate(family):
        if step >= PARTNER_LAYOUT_STEPS or len(worn) >= count:
            break
        if len(member) < column["min_length"]:
            continue
        if worn_template(member, convention, offered) in offered:
            worn.append(worn_template(member, convention, offered))
    return worn + [""] * (count - len(worn))


def partners_wear_published_layouts(column, convention, demands):
    """Whether any partner of any published layout wears a published layout."""
    most = max((len(owed) for owed in demands.values()), default=0)
    if most < 1:
        return False
    offered = layout_offer(column)
    return any(
        worn
        for name in offered
        for worn in partner_layouts(name, convention, most, column, offered)
    )


def _offer_a_layout(
    quotas, steps, lengths, convention, used, band, whole_numbers,
    covering, letters_needed, preferred, holes=(), owes=False, only=False,
):
    """The layout this slot takes, spelled (G9.6), or None.

    The preferred layout is offered first and then every other published
    layout in sorted order, each only where it has at least ``covering``
    cells left and a length the slot may hold.  ``letters_needed`` is
    the fold-collision ask of G9.3 step 1 and stays an ASK: a layout
    guaranteeing a character with a case is offered first, and where
    none fits the ordinary offer is taken rather than the slot being
    spent.

    ``only`` says the packing settled this slot's layout (plan P4-D182):
    the slot is offered ``preferred`` alone, and nothing where that is
    empty, because every other layout's count is spoken for.
    """
    offered = ([preferred] if preferred else []) + [
        name for name in sorted(quotas) if name != preferred and not only
    ]
    for asking in ((True, False) if letters_needed else (False,)):
        for layout in offered:
            if quotas[layout] < covering:
                continue
            if len(layout) not in lengths:
                continue
            if asking and not any(
                character in (LAYOUT_UPPER, LAYOUT_LOWER)
                for character in layout
            ):
                continue
            if owes and _a_signed_number(layout):
                continue
            found = _layout_spelling(
                layout, convention, steps, used, band, whole_numbers, holes
            )
            if found is None:
                continue
            quotas[layout] -= covering
            return found
    return None


LAYOUT_STAND_IN_TRIES = 16


def layout_stand_in_bases(column):
    """The named layouts a stand-in may be mixed from (method G9.6).

    Written from the rule statement.  The KINDS are the placeholders
    `%`, `@` and `&` the published layouts use between them, in that
    order; with fewer than two, or on a hexadecimal census, there is
    nothing to mix and nothing is offered.  A base is a named layout with
    no zero fill.

    A function of its own so the frozen case's registered mutant can take
    it away: with no base every group the census does not serve falls to
    the band enumeration, and the committed cells move.
    """
    offered = layout_offer(column)
    kinds = "".join(
        kind
        for kind in (LAYOUT_DIGIT, LAYOUT_UPPER, LAYOUT_LOWER)
        if any(kind in name for name in offered)
    )
    if len(kinds) < 2 or _convention_of_the_keys(offered) != LAYOUT_PLAIN:
        return []
    return [(name, kinds) for name in offered if LAYOUT_LEADING_ZERO not in name]


def layout_mix(base, kinds, step):
    """The ``step``-th mix of ``kinds`` over a base's figure and letter places.

    The step is spread by `layout_stepped` over the number of mixes, and
    taken apart place by place, leftmost first; every other character of
    the base stands as itself.
    """
    places = sum(1 for character in base if character in kinds)
    code = layout_stepped(step, len(kinds) ** places)
    built = ""
    for character in base:
        if character in kinds:
            built += kinds[code % len(kinds)]
            code //= len(kinds)
        else:
            built += character
    return built


def layout_stand_in(
    bases, census, mixed, steps, lengths, convention, used, band, whole_numbers,
    holes=(),
):
    """A group no named layout serves, written to a mix of its kinds (G9.6).

    The bases are read in sorted order, each only where the slot may hold
    its length, and sixteen mixes are read in all, each base's reading
    counted on from where it stopped: a mix the census names is stepped
    over, a mix no slot of this band can wear (`_layout_admits`) is
    stepped over, and the first mix with a free filling that recounts
    into it is taken, its own walk starting at the step after every walk
    already started.  None where no mix serves.
    """
    tried = 0
    named = {prefix_layout(name) for name in census}
    for base, kinds in bases:
        if len(base) not in lengths:
            continue
        mixed.setdefault(base, 0)
        while tried < LAYOUT_STAND_IN_TRIES:
            mix = layout_mix(base, kinds, mixed[base])
            mixed[base] += 1
            tried += 1
            if mix in census or prefix_layout(mix) in named:
                continue
            if not _layout_admits(mix, convention, band, whole_numbers):
                continue
            if mix not in steps:
                steps[mix] = 1 + len(steps) * LAYOUT_STEPS
            found = _layout_spelling(
                mix, convention, steps, used, band, whole_numbers, holes
            )
            if found is not None:
                return found
    return None


def packed_layouts(groups, column, quotas, whole_numbers, low, high):
    """Class, band AND named layout for every group, or None -- G9.6.

    Plan P4-D182, written from the rule statement.  The census of
    layouts is packed as a THIRD MARGIN of the grid `_packed_bands`
    packs: a cell is a class, a band and either one named layout or no
    named layout, the named layouts' quotas are their published counts in
    sorted order and the last quota is the present cells the census names
    no layout for.  A group may take a named layout only where it covers
    no more cells than that layout counts, the layout's length is one its
    slot may hold, and a slot of that class and band can wear it; no
    named layout is open to every class and band the group may stand in.

    The grid is packed FIRST WITH NO END PINNED, and the two groups that
    carry the published ends are read off the answer: the first group
    that can be written at the shortest length -- packed to a named
    layout of that length, or packed to none in a class and band with a
    spelling that long -- and the first other group that can be written
    at the longest.  Only where that finds nothing are the ends pinned
    onto the first two groups, as `_packed_bands` pins them.  This oracle
    lays a column out with its ends on the first two groups, so a case
    whose answer carries them elsewhere is refused rather than frozen.
    None where no assignment of whole groups meets all three margins.
    """
    offered = layout_offer(column)
    census = column.get("layout_forms") or {}
    convention = _convention_of_the_keys(offered)
    bands_owed = _band_quotas(column)
    class_margin = tuple((name, quotas[name]) for name in IDENTIFIER_CLASSES)
    band_margin = tuple((band, bands_owed[band]) for band in IDENTIFIER_BANDS)
    unnamed = column["n_present"] - sum(census[name] for name in offered)
    if unnamed < 0:
        return None
    layout_margin = tuple(
        [(name, census[name]) for name in offered] + [("", unnamed)]
    )
    margins = (class_margin, band_margin, layout_margin)

    def permitted_for(lengths_of):
        permitted = []
        for slot, size in enumerate(groups):
            cells = set()
            lengths = lengths_of(slot)
            for name in IDENTIFIER_CLASSES:
                for band in IDENTIFIER_BANDS:
                    if not any(
                        _identifier_pair(name, band, whole_numbers, length)
                        for length in lengths
                    ):
                        continue
                    cells.add((name, band, ""))
                    for layout in offered:
                        if size > census[layout] or len(layout) not in lengths:
                            continue
                        if _layout_admits_class(
                            layout, convention, name, band, whole_numbers
                        ):
                            cells.add((name, band, layout))
            permitted.append((size, frozenset(cells)))
        return permitted

    everywhere = tuple(range(low, high + 1))
    packed = _packed_grid(
        permitted_for(lambda slot: everywhere), margins, demanded=False
    )
    if packed is not None:
        carriers = []
        for end in ((low,) if high <= low else (low, high)):
            for slot, (name, band, layout) in enumerate(packed):
                if slot in carriers:
                    continue
                if layout:
                    fits = len(layout) == end
                else:
                    fits = _identifier_pair(name, band, whole_numbers, end)
                if fits:
                    carriers.append(slot)
                    break
        if high <= low or len(carriers) == 2:
            if high > low and carriers != [0, 1]:
                raise AssertionError(
                    "the layout packing carries the published ends on groups "
                    f"{carriers}, and this oracle lays a column out with its "
                    "ends on the first two groups: it freezes no case for "
                    "that shape and states no expected cells for it"
                )
            return (
                [cell[0] for cell in packed],
                [cell[1] for cell in packed],
                [cell[2] for cell in packed],
            )
    packed = _packed_grid(
        permitted_for(lambda slot: slot_lengths(slot, low, high)),
        margins,
        demanded=False,
    )
    if packed is None:
        return None
    return (
        [cell[0] for cell in packed],
        [cell[1] for cell in packed],
        [cell[2] for cell in packed],
    )


def _layout_admits_class(layout, convention, name, band, whole_numbers):
    """`_layout_admits`, and the filling reads as the slot's own class."""
    for step in range(min(layout_room(layout), LAYOUT_ADMISSION_STEPS)):
        candidate = filled_layout(layout, step)
        if candidate[:1] in FORMULA_OPENINGS and not _a_signed_number(layout):
            return False
        if _is_a_number(candidate.strip()) != (name == "number"):
            continue
        if _fits_its_slot(candidate, layout, convention, band, whole_numbers):
            return True
    return False


def layouts_short(column, content):
    """Whether a named layout of the census is worn fewer or more times.

    The check of contract 7.12 that `_identifier_recount` makes, asked as
    a question rather than a refusal, so the packing of plan P4-D182 can
    be offered where the first packing's cells miss it.
    """
    census = column.get("layout_forms") or {}
    named = {name: count for name, count in census.items() if name != WITHHELD}
    if not named:
        return False
    convention = layout_convention(list(content))
    worn = {}
    for cell in content:
        layout = layout_of(cell, convention)
        if layout:
            worn[layout] = worn.get(layout, 0) + 1
    return any(worn.get(name, 0) != named[name] for name in named)


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
    holes = tuple(sorted(column.get("missing_by_source") or {}))
    measured = {
        # PRESENCE IS RECOUNTED AS A READER COUNTS IT (plan P4-D158): a
        # cell spelled `NA` is written, and read back as absent, so a
        # construction that wrote one is refused here rather than
        # certified as a present value.
        "n_present": sum(
            1 for cell in content if not reads_as_absent(cell, holes)
        ),
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
    # THE CENSUS OF LAYOUTS, RECOUNTED (contract section 7.12).  That
    # section makes it EXACT-OBSERVABLE, so a vector publishing cells
    # that miss it would be an oracle certifying the very thing the
    # contract forbids.  The POOLED key bounds rather than binds and is
    # not recounted; a NAMED layout is.
    census = column.get("layout_forms") or {}
    named = {
        name: count for name, count in census.items() if name != WITHHELD
    }
    if named:
        convention = layout_convention(list(content))
        worn = {}
        for cell in content:
            layout = layout_of(cell, convention)
            if layout:
                worn[layout] = worn.get(layout, 0) + 1
        for layout in sorted(named):
            if worn.get(layout, 0) != named[layout]:
                raise AssertionError(
                    f"the cells this oracle built wear the layout "
                    f"{layout!r} {worn.get(layout, 0)} times and the case "
                    f"publishes {named[layout]}. Contract section 7.12 "
                    "makes the census EXACT-OBSERVABLE, so the construction "
                    "above is wrong; do not move the published fact to meet "
                    "it."
                )
    # THE PUBLISHED PREFIXES, RECOUNTED (contract section 7.12a): no cell
    # a prefix governs opens otherwise.
    prefixes = column.get("layout_prefixes") or {}
    if prefixes:
        convention = layout_convention(list(content))
        broken = sum(
            1 for cell in content if breaks_a_prefix(cell, convention, prefixes)
        )
        if broken:
            raise AssertionError(
                f"{broken} cells this oracle built do not open with a prefix "
                "the case publishes for them. Contract section 7.12a makes "
                "the prefix EXACT-OBSERVABLE, so the construction above is "
                "wrong; do not move the published fact to meet it."
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


def opened_with_prefix(
    spelling, prefixes, convention, used, band, whole_numbers, holes, offered,
):
    """A cell of the band walk given the prefix it owes (method G9.6a).

    Written from the rule statement.  Where the column publishes a prefix
    for the whole column, or for the layout the spelling wears, the
    spelling's opening is overwritten with it; the result is taken only
    where it is unwritten, reads as absent to no reader, keeps the slot's
    band and its reading as a number, and wears no named layout the
    spelling did not.  Otherwise the spelling stands.
    """
    if not prefixes:
        return spelling
    own = layout_of(spelling, convention)
    prefix = prefixes.get(PREFIX_OF_THE_COLUMN, prefixes.get(own, ""))
    if PREFIX_OF_THE_COLUMN not in prefixes and own not in prefixes:
        prefix = ""
    if not prefix or len(spelling) <= len(prefix) or spelling.startswith(prefix):
        return spelling
    candidate = prefix + spelling[len(prefix):]
    if candidate in used or reads_as_absent(candidate, holes):
        return spelling
    moved = layout_of(candidate, convention)
    if moved != own and moved in {prefix_layout(name) for name in offered}:
        return spelling
    bare, before = candidate.strip(), spelling.strip()
    digits = bool(bare) and set(bare) <= DIGIT_CHARACTERS
    coded = bool(bare) and set(bare) <= CODE_CHARACTERS
    if band == FIGURES and not digits:
        return spelling
    if band == CODE_BAND and (digits or not coded):
        return spelling
    if band not in (FIGURES, CODE_BAND) and (digits or coded):
        return spelling
    if _is_a_number(bare) != _is_a_number(before):
        return spelling
    if whole_numbers and not _is_a_whole_number(bare):
        return spelling
    return candidate


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
    on top of that -- BEFORE the case could be added.  The same holds for
    the step's layout trigger (plan P4-D163), which looks further only
    where the first layout leaves a named layout short -- with ONE
    exception, which this oracle does model: where no group owes a
    partner, the census is first packed as a third margin (plan P4-D182,
    `packed_layouts`), and only where that too leaves a layout short does
    this oracle stop at the check of 7.12.
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
    # THE CONSTRUCTION READS THE CENSUS BY TEMPLATE (method G9.6a): every
    # prefixed layout is written with its prefix standing in it.  The
    # recounts below read the column as published.
    view = dict(column)
    view["layout_forms"] = templated_census(column)
    prefixes = column.get("layout_prefixes") or {}
    _classes, bands = _packed_bands(
        groups, column, _class_quotas(column), whole_numbers, low, high
    )

    def lay(_classes, bands, assigned=None):
        """Every present cell, from one packing (and its layouts, plan P4-D182)."""
        partners_wanted = distinct - column["n_distinct_folded"]
        identities_wanted = column["n_distinct_folded"]
        used = set()
        # The spellings a reader reads as absent: contract section 14.4's
        # vocabulary, and the column's own published hole spellings, which on
        # a one-column document are every spelling the document declares
        # absent (plan P4-D158).
        holes = tuple(sorted(column.get("missing_by_source") or {}))

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
            # THE LONE 0 IS TAKEN LATE (plan P4-D162): after every number
            # shorter than the shortest named layout of figures alone two or
            # more figures long, or after every published length where none
            # is named, where the slot may hold one figure and that length --
            # so a column of 1 to 800 is not written holding 0.
            late = 0
            if whole_numbers and band == FIGURES and low == 1 and high >= 2:
                late = high
                for layout in sorted(column.get("layout_forms") or {}):
                    if (
                        layout != "(withheld)"
                        and len(layout) >= 2
                        and set(layout) == {"%"}
                    ):
                        late = min(late, len(layout) - 1)
                if late < 2 or 1 not in lengths or late not in lengths:
                    late = 0
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
                    # Walked lazily: a family of six code-alphabet places holds
                    # tens of billions of spellings, and the walk stops at the
                    # first one it takes.
                    def spellings(alphabet=alphabet, block=block, leading=leading,
                                  suffix=suffix):
                        for index in range(len(alphabet) ** block):
                            one = enumerated_spelling(alphabet, block, index, leading)
                            if late and block == 1 and one + suffix == "0":
                                continue
                            yield one + suffix
                        if late and block == late:
                            yield "0"

                    for candidate in spellings():
                        if candidate in used:
                            continue
                        if reads_as_absent(candidate, holes):
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

        # THE PUBLISHED LAYOUT IS OFFERED FIRST (contract 7.12, method
        # G9.6).  The census counts CELLS and this walk spends GROUPS, and
        # every cell of a group carries the same spelling, so a group takes
        # the first published layout, in sorted order, whose remaining count
        # is at least the number of cells that group covers and whose length
        # its own slot may hold.  Where nothing is offered -- which is every
        # case frozen before landing 2b.18, each publishing the empty census
        # a floored census gives a column whose layouts are all held back --
        # the band enumeration below is reached unchanged, which is why
        # those cases keep their committed cells.
        offered = layout_offer(view)
        census = view.get("layout_forms") or {}
        quotas = {name: census[name] for name in offered}
        # Each layout's walk starts at its own step (plan P4-D128): the k-th
        # layout in sorted order at 1 + k * 4096, and a mix, when first read,
        # at the next such step after every walk already started.
        steps = {name: 1 + k * LAYOUT_STEPS for k, name in enumerate(offered)}
        convention = _convention_of_the_keys(offered)
        bases = layout_stand_in_bases(view)
        mixed = {}
        preferred = [""] * identities_wanted
        # WHICH PARTNERS EACH IDENTITY IS HANDED (G9.3 step 4): the k-th
        # partner goes to the (k mod identities)-th identity.
        demands = {}
        for taking in range(partners_wanted):
            demands.setdefault(taking % identities_wanted, []).append(
                groups[identities_wanted + taking]
            )
        paired = bool(offered) and partners_wear_published_layouts(
            view, convention, demands
        )
        predicted = {}
        if offered:
            preferred = layout_preferences(
                view,
                groups[:identities_wanted],
                [f"{_classes[p]}/{bands[p]}" for p in range(identities_wanted)],
                bands,
                [slot_lengths(p, low, high) for p in range(identities_wanted)],
                {0, 1} if high > low else {0},
                demands,
            )
        if assigned is not None:
            preferred = list(assigned)

        identities = []
        for position in range(identities_wanted):
            letters_needed = position < partners_wanted
            laid = None
            if offered:
                laid = _offer_a_layout(
                    quotas,
                    steps,
                    slot_lengths(position, low, high),
                    convention,
                    used,
                    bands[position],
                    whole_numbers,
                    groups[position],
                    letters_needed,
                    preferred[position],
                    holes,
                    bool(demands.get(position)),
                    assigned is not None,
                )
            if laid is None and bases:
                laid = layout_stand_in(
                    bases,
                    census,
                    mixed,
                    steps,
                    slot_lengths(position, low, high),
                    convention,
                    used,
                    bands[position],
                    whole_numbers,
                    holes,
                )
            if laid is not None:
                used.add(laid)
                identities.append(laid)
                # Its partners' cells are debited with it, off the layout it
                # took, and remembered by partner (plan P4-D157).
                if paired and demands.get(position):
                    owed = demands[position]
                    worn = partner_layouts(
                        worn_template(laid, convention, quotas), convention,
                        len(owed), view, offered,
                    )
                    slots = [
                        taking for taking in range(partners_wanted)
                        if taking % identities_wanted == position
                    ]
                    for order, taking in enumerate(slots):
                        predicted[taking] = worn[order]
                        if worn[order] in quotas:
                            quotas[worn[order]] -= owed[order]
                continue
            walked = take(
                bands[position],
                slot_lengths(position, low, high),
                letters_needed,
            )
            opened = opened_with_prefix(
                walked, prefixes, convention, used, bands[position],
                whole_numbers, holes, offered,
            )
            if opened != walked:
                used.discard(walked)
                used.add(opened)
            identities.append(opened)

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
            size = groups[slot]
            if paired and predicted.get(taking) in quotas:
                quotas[predicted[taking]] += size
            unnamed = first = unopened = None
            for candidate in partner_family(identities[position], high):
                if candidate in used or len(candidate) not in window:
                    continue
                if reads_as_absent(candidate, holes):
                    continue
                # A MEMBER NOT OPENING WITH A PREFIX IT OWES is taken only
                # where no member keeps it (method G9.6a).
                if prefixes and breaks_a_prefix(candidate, convention, prefixes):
                    unopened = unopened or candidate
                    continue
                if not paired:
                    partner = candidate
                    break
                # THE MEMBER A PARTNER TAKES ON A PAIRED COLUMN (plan
                # P4-D157): the first wearing a published layout with its
                # cells left, else the first wearing none, else the first.
                first = first or candidate
                worn = worn_template(candidate, convention, quotas)
                if worn in quotas:
                    if quotas[worn] >= size:
                        partner = candidate
                        break
                    continue
                unnamed = unnamed or candidate
            if paired and partner is None:
                partner = unnamed or first
            if partner is None:
                partner = unopened
            if paired and partner is not None:
                if worn_template(partner, convention, quotas) in quotas:
                    quotas[worn_template(partner, convention, quotas)] -= size
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
        return content

    content = lay(_classes, bands)
    partners_owed = distinct - column["n_distinct_folded"]
    # A NAMED LAYOUT THE FIRST PACKING LEAVES SHORT IS PACKED WITH THE
    # FAMILIES (plan P4-D182, method G9.6): the census becomes a third
    # margin of the same grid, every group is offered its packed layout
    # alone, and the cells are built again.  Only where no group owes a
    # fold-collision partner, whose layout its parent's spelling decides.
    if layouts_short(column, content) and partners_owed == 0:
        repacked = packed_layouts(
            groups, view, _class_quotas(column), whole_numbers, low, high
        )
        if repacked is not None:
            content = lay(repacked[0], repacked[1], repacked[2])
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


# The two shape floors of method section G10.5, revision 4. A whole
# number leaves binary64's range past about 1.8e308 and a fraction
# falls below its smallest subnormal past about 5e-324, so a value
# written narrower than these stops being unholdable at all -- which
# would make the twin a different kind of column from the one the
# description publishes. Where a group's asked width is below the floor
# of the shape it takes, the floor wins and the report names it.
#
# THE CANONICAL INVENTED WIDTH OF REVISIONS 1 TO 3 IS GONE (residual
# R-P2-1, closed). The role now publishes `min_length` and
# `max_length`, so there is a width to write at and no width to invent.
# Both are counts of the ROOM a value has AFTER its sign, because a
# minus sign buys no magnitude: 309 figures is the first whole number
# past the largest binary64 and 326 characters is the first
# `0.`-and-zeros fraction below the smallest subnormal, and each floor
# carries one character past that measured edge.
OVERFLOW_FIGURES = 310
UNDERFLOW_PLACES = 327

# The zero run is no longer a constant at all: it grows until the value
# underflows, which is the only rule two implementations can agree on
# without sharing a magic number, and the only one that does not write
# some bodies wider than the description asks.

# THE EXPONENT SPELLING FAMILY AND ITS OWN TWO FLOORS -- method section
# G10.5 revision 5, closing residuals R-P4-48 and R-P4-68. The two
# floors above are the DIGIT-STRING family's, and until revision 5 that
# was the only family either out-of-range shape had, so a column of
# `1e400` -- five characters -- could only be written three hundred and
# ten characters wide.  A mantissa, the letter `e` and a signed exponent
# says the same magnitude in five characters (`1e400`) or six
# (`1e-400`), because an exponent certain to leave binary64's range
# needs three figures and the too-small one needs its sign as well.
# Both are counts of the ROOM after the value's own sign, exactly as
# the two floors above are, and the floor that binds a shape is the
# NARROWER of its families' floors.
EXPONENT_LARGE_ROOM = 5
EXPONENT_SMALL_ROOM = 6

# THE EXPONENT IS A THREE-FIGURE FIELD AND IT MOVES.  The walk spends
# the MANTISSA first at one exponent and then steps the exponent
# OUTWARD from 400 -- up to 999, then down from 399 -- so the family's
# capacity is the SHAPE's own rather than one exponent's: at five
# characters a fixed exponent supplies nine spellings and a real column
# holds thousands, and the generator that fixed it refused to build a
# sixteen-value column a profiler had just described.  Where the walk
# stops is not a number written here: it is where the reading of this
# file stops answering "out of range" for the shape being written.
EXPONENT_HOME = 400
EXPONENT_CEILING = 999
EXPONENT_FLOOR = 100

# The two families, in the order a shape is asked for them: the digit
# string first wherever it can write at the asked width, then the
# exponent.  Asking in that order is what keeps every column revision 4
# wrote byte-identical.
SPELLING_PLAIN = "plain"
SPELLING_EXPONENT = "exponent"

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


def _shape_floor(shape):
    """The narrowest width one shape may be written at -- G10.5.

    Four of the six shapes have no floor at all: contradictory
    notation, ordinary text and the two in-range shapes say nothing
    about magnitude, so nothing about their width decides what they
    are.

    THE FLOOR IS THE NARROWER OF THE SHAPE'S TWO FAMILIES (revision 5).
    It read 310 and 327 here while the digit string was the only
    spelling either out-of-range shape had; the exponent family says
    the same magnitudes in five and six characters, so those are the
    floors, and a column publishing widths of five and six carries both
    its ends instead of neither.
    """
    if shape == "too_large":
        return EXPONENT_LARGE_ROOM
    if shape == "too_small":
        return EXPONENT_SMALL_ROOM
    return 1


def _spelling_families(shape, asked, sign=None):
    """The spelling families one shape may use at one asked width -- G10.5.

    Method section G10.5 revision 5.  The digit-string family is asked
    first wherever it can write at all, which is at or above its OWN
    magnitude floor -- 310 characters of room for a value too large to
    hold, 327 for one too small.  The exponent family follows from five
    and six.  The four shapes carrying no magnitude have one family and
    no floor.
    """
    room = _unrepresentable_width(shape, asked, sign)
    if sign == SIGN_NEGATIVE:
        room = room - 1
    if shape == "too_large":
        families = []
        if room >= OVERFLOW_FIGURES:
            families.append(SPELLING_PLAIN)
        if room >= EXPONENT_LARGE_ROOM:
            families.append(SPELLING_EXPONENT)
        return families
    if shape == "too_small":
        families = []
        if room >= UNDERFLOW_PLACES:
            families.append(SPELLING_PLAIN)
        if room >= EXPONENT_SMALL_ROOM:
            families.append(SPELLING_EXPONENT)
        return families
    return [SPELLING_PLAIN]


def _exponent_power(step):
    """The ``step``-th exponent of the walk, counting outward from 400.

    Up to 999, then down from 399, so the family's first spelling is
    `1e400` and the field stays three figures wide the whole way.  None
    says the walk would leave that field, which is a change of width
    rather than another spelling of the same one.  Where it stops in
    practice is earlier and is asked of the reading rather than written
    here, which is why no 309 and no 325 appears in this function.
    """
    up = EXPONENT_CEILING - EXPONENT_HOME
    if step <= up:
        return EXPONENT_HOME + step
    power = EXPONENT_CEILING - step
    if power < EXPONENT_FLOOR:
        return None
    return power


def _exponent_spelling(shape, lead, room, order):
    """The ``order``-th exponent spelling of one out-of-range shape -- G10.5.

    ONE CONSTRUCTION FOR BOTH SHAPES (revision 5): the value's sign, a
    mantissa of decimal figures, the letter `e`, and a three-figure
    exponent carrying a minus for the too-small shape.  The mantissa
    fills whatever the exponent field leaves of the asked width, and
    what separates one spelling from the next is the mantissa read as a
    NUMBER -- 1, 2, 3 and so on -- written at the right of that room
    behind a run of leading zeros.  That is step 4's own rule, which
    keeps the width fixed while the value moves.

    THE MANTISSA IS SPENT BEFORE THE EXPONENT MOVES, and both move, so
    the family's capacity is the shape's own count of spellings at that
    width.  None where the room holds no mantissa at all, or where the
    walk has left the three-figure exponent field.

    This is the ``order``-th CANDIDATE, which is not the same thing as
    the ``order``-th spelling: some candidates the reading turns down.
    `_exponent_accepted` is the one that counts only the accepted ones.
    """
    places = _exponent_places(shape, room)
    if places < 1:
        return None
    power_sign = "-"
    if shape == "too_large":
        power_sign = ""
    span = 10 ** places - 1
    power = _exponent_power(order // span)
    if power is None:
        return None
    body = str(order % span + 1)
    return (
        lead + "0" * (places - len(body)) + body + "e" + power_sign + str(power)
    )


def _exponent_places(shape, room):
    """How many figures the mantissa gets at one room -- G10.5.

    The exponent field is four characters wide for the too-large shape
    and five for the too-small one, whatever exponent it holds, and the
    mantissa fills what that leaves.
    """
    if shape == "too_large":
        return room - 4
    return room - 5


def _exponent_accepted(shape, lead, room, order):
    """The ``order``-th exponent spelling the READING accepts -- G10.5.

    A candidate the reading turns down is STEPPED PAST and the walk
    carries on, because the refusals inside one exponent are contiguous
    at one end -- a suffix for the too-small shape and a PREFIX for the
    too-large one, whose `1e308` is a number this format holds while
    `2e308` through `9e308` are not.  A rule that stopped at the first
    refusal was therefore right for one shape and wrong for the other,
    and this oracle certified the wrong boundary along with the
    generator and the method (review item P4-A2-R3, item 1).

    What ENDS the walk is one whole exponent turned down: the exponent
    moves monotonically away from the shape once it leaves 999, so an
    exponent none of whose mantissas is accepted is one past which
    nothing ever is again.  None says the family is spent at this room.

    Written as "the ``order``-th accepted candidate" rather than as an
    advancing cursor, so this file's answer is a function of ``order``
    alone and shares no state with the walk it checks.
    """
    index = 0
    seen = 0
    turned_down = 0
    span = max(10 ** _exponent_places(shape, room) - 1, 0)
    while True:
        candidate = _exponent_spelling(shape, lead, room, index)
        if candidate is None:
            return None
        index = index + 1
        if not _reads_back_as(shape, candidate):
            turned_down = turned_down + 1
            if turned_down > span:
                return None
            continue
        turned_down = 0
        if seen == order:
            return candidate
        seen = seen + 1


def _reads_back_as(shape, candidate):
    """Whether the parser reads one spelling back as its shape -- G10.5.

    THE QUESTION ITSELF, ASKED OF EACH CANDIDATE (revision 5), which is
    the same pair of questions step 6's recount asks of the finished
    cell: what the notation classifies as, and whether the value is
    whole.  A spelling this refuses is one the recount would file under
    another class.
    """
    answers = notation_reading(candidate)
    if NOTATION_OUT_OF_RANGE not in answers:
        return False
    if shape == "too_large":
        return WHOLE_YES in answers
    return WHOLE_NO in answers


def _unrepresentable_width(shape, asked, sign=None):
    """The width one shape is actually written at -- G10.5.

    The width the group was ASKED for, or the shape's own floor where
    the asked width falls below it.  A negative value spends one
    character on its sign, and the floors are counts of the room AFTER
    that sign, so a negative cell's floor is one character wider.
    """
    floor = _shape_floor(shape)
    if floor <= 1:
        return asked
    if sign == SIGN_NEGATIVE:
        floor = floor + 1
    return max(asked, floor)


def _unrepresentable_widths(column, shapes_taken, signs_taken):
    """The width EVERY group of the column is asked for -- G10.5.

    Both published ends are carried where the column's shapes can carry
    them: every group is asked for ``max_length``, and the FIRST group
    whose shape can be written at ``min_length`` is asked for that
    instead.  The floor carrier is chosen by SHAPE and not by position,
    so a column whose one narrow-capable group comes first still
    carries the floor.
    """
    ceiling = max(column["max_length"], 1)
    floor = max(column["min_length"], 1)
    asked = [ceiling] * len(shapes_taken)
    if len(shapes_taken) < 2 or floor == ceiling:
        return asked
    # The floor is only assigned if something ELSE can still carry the
    # ceiling.  Contradictory notation and ordinary text write at a
    # width of their own whatever they are asked for, so a column with
    # exactly one carrying shape must spend it on the ceiling: the
    # other shapes land where they land, and that is the floor.
    for index, shape in enumerate(shapes_taken):
        if not _carries_a_width(shape, floor, signs_taken[index]):
            continue
        for other, another in enumerate(shapes_taken):
            if other == index:
                continue
            if _carries_a_width(another, ceiling, signs_taken[other]):
                asked[index] = floor
                return asked
    return asked


def _carries_a_width(shape, width, sign=None):
    """Whether one shape can be written at exactly ``width`` -- G10.5.

    Contradictory notation is the fixed construction of G10.3 and
    ordinary text is a stand-in drawn by the text rule; both are
    settled by rules that know nothing about the published widths, so
    neither may be chosen to carry one.  Of the four that may, the two
    out-of-range shapes can carry only a width at or above their floor.
    """
    if shape in ("contradictory", "ordinary_text"):
        return False
    if width < SHAPE_NARROWEST[shape] + (1 if sign == SIGN_NEGATIVE else 0):
        return False
    return _unrepresentable_width(shape, width, sign) == width


# The narrowest cell each carrying shape can write, before its sign.
# The in-range fraction needs three characters (`1.5`) whatever it is
# asked for, so a rule that only checked magnitude floors named it the
# carrier for widths it then missed.
SHAPE_NARROWEST = {
    "too_large": 1,
    "too_small": 1,
    "whole_in_range": 1,
    "fraction_in_range": 2,
}


def _unrepresentable_spelling(shape, sign, order, asked, family=SPELLING_PLAIN):
    """The ``order``-th spelling of one shape -- method section G10.5 step 4.

    In-range cells come from the leading-zero family padded to the
    width the group was asked for, since no ladder and no statistic is
    published for this role.  **What separates one spelling from the
    next is its VALUE and not its width** -- the whole shape counts up
    ``1``, ``2``, ``3`` behind the zeros and the fraction shape counts
    up ``1.5``, ``2.5``, ``3.5`` -- because adding a zero for
    distinctness instead makes every group after the first one
    character wider than the width it was asked for.

    THE ASKED WIDTH IS THE WIDTH OF THE WHOLE CELL.  The minus sign,
    the leading ``0.`` and the trailing figure are all spent inside it.

    ``family`` names which of the two spelling families of revision 5
    writes the cell.  None says that family cannot supply this order at
    this width, which is when the caller asks the next one.
    """
    lead = "-" if sign == SIGN_NEGATIVE else ""
    width = _unrepresentable_width(shape, asked, sign)
    room = width - len(lead)
    if family == SPELLING_EXPONENT:
        return _exponent_accepted(shape, lead, room, order)
    if shape == "contradictory":
        return f"(-{order + 1})"
    if shape == "whole_in_range":
        body = str(order + 1)
        return lead + "0" * max(room - len(body), 0) + body
    if shape == "fraction_in_range":
        # The leading zero is optional to the parser, so `.5` is a
        # holdable TWO-character fraction and the narrowest this shape
        # can write; nine of them exist at that width.
        if room == 2:
            return lead + "." + str((order % 9) + 1)
        body = f"{order + 1}.5"
        return lead + "0" * max(room - len(body), 0) + body
    if shape == "too_large":
        return lead + enumerated_spelling(
            DIGITS, room, order, _not_a_leading_zero
        )
    if shape == "too_small":
        # THE NINTH-SPELLING LIMIT IS GONE, and removing it is the whole
        # point of the rule below (review item P4-G3-R7-F3).  It was
        # written when the zero run was whatever the width left over, so
        # a tenth spelling -- the first whose figure body is two
        # characters -- had no stated answer and this oracle refused
        # rather than guess.  The run now grows until the value
        # underflows, which answers every order, so refusing at nine
        # would make this oracle disagree with a conforming generator on
        # the first column that asks for ten.
        figures = str(order + 1)
        zeros = max(room - 2 - len(figures), 1)
        candidate = lead + "0." + "0" * zeros + figures
        # The zero run grows until the value actually underflows.  A
        # single floor cannot answer this: behind 323 zeros the body
        # `10` underflows and the body `9` does not, and a six-figure
        # body needs only 319, so a floor high enough for the worst body
        # writes every better one wider than the description asks.
        while float(candidate) != 0.0:
            zeros = zeros + 1
            candidate = lead + "0." + "0" * zeros + figures
        # AND WHERE THE GROWN RUN NO LONGER FITS, THIS FAMILY SAYS NO
        # (revision 5, residual R-P4-48).  It used to write the wider
        # cell and let the recount name the width miss, which held a
        # published count by breaking a published width; the exponent
        # family writes that group at the asked width instead.  At 327
        # characters this family runs out at twenty-four spellings.
        if len(candidate) - len(lead) > room:
            return None
        return candidate
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
    # AND THE TWO PUBLISHED WIDTHS, which this postcondition did not
    # cover when they were added (review item P4-G3-R5-F4). An oracle
    # that recounts nine facts and not the two the landing is ABOUT
    # certifies a carrier failure as correct: the two-cell case whose
    # only carrying shape was spent on the wrong end passed here
    # unchallenged. The population is the numeric-looking cells, which
    # is every shape but ordinary text, matching the producer.
    numeric_looking = [
        cell
        for cell in content
        if NOTATION_TEXT not in notation_reading(cell)
    ]
    if numeric_looking:
        widths = [len(cell) for cell in numeric_looking]
        for name, value in (
            ("min_length", min(widths)),
            ("max_length", max(widths)),
        ):
            if column[name] != value:
                raise AssertionError(
                    f"the cells this oracle built recount {name} as {value!r} "
                    f"and the case publishes {column[name]!r}. The two widths "
                    "are EXACT-OBSERVABLE, so either the width rule above is "
                    "wrong or this case publishes a width no real column of "
                    "these cells could; do not move the published fact to "
                    "meet the construction."
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
    # THE SHAPE EVERY GROUP TAKES IS SETTLED BEFORE ANY WIDTH IS
    # CHOSEN, because which group carries the published floor depends on
    # what shape it took (G10.5 revision 4).
    shapes_taken = [shapes[(cell[0], cell[1])] for cell in cells]
    signs_taken = [cell[2] for cell in cells]
    asked = _unrepresentable_widths(column, shapes_taken, signs_taken)
    content = []
    spent = {}
    used = []
    for index, (size, cell) in enumerate(zip(groups, cells)):
        notation, whole, sign = cell
        shape = shapes[(notation, whole)]
        if shape == "ordinary_text":
            spelling = text_stand_ins(used, 1)[0]
        else:
            # EACH SHAPE-AND-SIGN PAIR WALKS EACH FAMILY FROM THAT
            # FAMILY'S OWN START (G10.5 step 4, stated in revision 5).
            # The counter was per SHAPE here and per shape-and-sign in
            # the shipped generator, which agreed on every case frozen
            # so far because no case carried a positive and a negative
            # group of one shape -- and would have disagreed on the
            # first one that did.  The method now says which, and this
            # is that rule.
            spelling = None
            for family in _spelling_families(shape, asked[index], sign):
                key = (shape, sign, family)
                spelling = _unrepresentable_spelling(
                    shape, sign, spent.get(key, 0), asked[index], family
                )
                spent[key] = spent.get(key, 0) + 1
                if spelling is not None:
                    break
            if spelling is None:
                raise AssertionError(
                    f"no spelling family of {shape!r} can supply another "
                    f"distinct value at a width of {asked[index]}"
                )
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
# reasoned away, and this file states no reading of it. RAISED FROM THREE
# TO FIVE at plan P4-D198: the shortest date the formats of the method's
# G7 read is six characters, `1/1/24` and `1.1.24` among them, so no
# word of five or fewer reaches the rule.
LONGEST_FROZEN_WORD = 5


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


def invents_a_leading_zero(text):
    """Whether a number opens with a zero standing before another figure."""
    body = text[1:] if text[:1] == "-" else text
    return len(body) >= 2 and body[0] == "0" and body[1].isdigit()


# The shortest length G9.5 step 3a writes a number of each band at: one
# figure; a minus sign and a figure; a figure, a point and a figure.
NUMBER_SHORTEST = {FIGURES: 1, CODE_BAND: 2, WIDE_BAND: 3}


def plain_number_room(band, length):
    """How many numbers of one band and length need no leading zero."""
    if band == FIGURES:
        return 10 if length <= 1 else 9 * 10 ** (length - 1)
    if length < 2:
        return 0
    if length == 2:
        return 10
    if band == CODE_BAND:
        # Only the numbers whose exponent is nought (landing 2b.4, repair):
        # a number of the code band grows by its length, not by a power of
        # ten.
        return 10 if length == 3 else 9 * 10 ** (length - 3)
    return 100 if length == 3 else 90 * 10 ** (length - 3)


def numbers_out_of_the_code_band(groups, lengths, packed, carriers):
    """G9.5 step 3b's exchange of code-band numbers for wide-band text.

    A text group of the wide band that may stand in the code band at its
    length trades places with number groups of the code band whose sizes
    make its size exactly, read off the reachable sums, smallest text
    group first, while any number stands in the code band. This file
    freezes no case whose census names a form, so no code-band form owes
    cells here.
    """
    moved = list(packed)
    spare = sum(
        size for size, pair in zip(groups, moved)
        if pair == (NOTATION_NUMBER, CODE_BAND)
    )
    if spare < 1:
        return moved
    texts = sorted(
        (groups[place], place) for place in range(len(groups))
        if place not in carriers
        and moved[place] == (NOTATION_TEXT, WIDE_BAND)
        and _free_text_permits(NOTATION_TEXT, CODE_BAND, lengths[place])
    )
    numbers = [
        place for _size, place in sorted(
            (groups[place], place) for place in range(len(groups))
            if place not in carriers
            and moved[place] == (NOTATION_NUMBER, CODE_BAND)
            and _free_text_permits(NOTATION_NUMBER, WIDE_BAND, lengths[place])
        )
    ]
    for size, place in texts:
        if size > spare:
            continue
        picked = subset_making([groups[other] for other in numbers], size, len(numbers))
        if picked is None:
            continue
        moved[place] = (NOTATION_TEXT, CODE_BAND)
        for slot in sorted(picked, reverse=True):
            moved[numbers[slot]] = (NOTATION_NUMBER, WIDE_BAND)
            del numbers[slot]
        spare -= size
        if spare < 1:
            break
    return moved


def singletons_kept_as_text(groups, lengths, packed, carriers, line=LONG_TAIL_LINE):
    """G9.5 step 3c: the text keeps a tenth of its cells in values written once.

    Where the numbers could clear the long-tail line in cells and in
    groups and fewer than a tenth of the text's cells are values written
    once, a text group of several cells trades places with as many
    single-cell number groups of its own band, smallest text group
    first, each standing in the other's notation at its length.
    """
    moved = list(packed)
    numbered = sum(size for size, pair in zip(groups, moved) if pair[0] == NOTATION_NUMBER)
    numbers = sum(1 for pair in moved if pair[0] == NOTATION_NUMBER)
    written = sum(size for size, pair in zip(groups, moved) if pair[0] == NOTATION_TEXT)
    once = sum(1 for size, pair in zip(groups, moved) if pair[0] == NOTATION_TEXT and size == 1)
    if numbered < line or numbers < line or once * 10 >= written:
        return moved
    texts = sorted(
        (groups[place], place) for place in range(len(groups))
        if place not in carriers
        and moved[place][0] == NOTATION_TEXT
        and groups[place] > 1
        and _free_text_permits(NOTATION_NUMBER, moved[place][1], lengths[place])
    )
    for size, place in texts:
        if once * 10 >= written:
            break
        band = moved[place][1]
        singles = [
            other for other in range(len(groups))
            if other not in carriers
            and moved[other] == (NOTATION_NUMBER, band)
            and groups[other] == 1
            and _free_text_permits(NOTATION_TEXT, band, lengths[other])
        ]
        if len(singles) < size:
            continue
        moved[place] = (NOTATION_NUMBER, band)
        for other in singles[:size]:
            moved[other] = (NOTATION_TEXT, band)
        once += size
    return moved


def number_at_form(band, length, census=()):
    """The written form every number of one band and length wears.

    One band and one length write ONE form, which is read off the
    spelling families of G9.5 step 3 rather than off any one spelling:
    in the figures a run of digits, which carries ONE kind and so has no
    form at all; in the code band a minus and a figure at two characters
    and `L - 2` figures, an `e` and a figure above it; outside it a
    figure and a point at two characters and `L - 2` figures, a point
    and a figure above it.
    """
    if band == FIGURES or length < NUMBER_SHORTEST[band]:
        return ""
    if band == CODE_BAND:
        built = "-1" if length == 2 else "1" * (length - 2) + "e1"
    else:
        built = "1." if length == 2 else "1" * (length - 2) + ".1"
    return census_form(built, census)


def number_lengths(column, groups, packed, carriers, lengths=None):
    """G9.5 step 3a: every number carrying no published end at its own length.

    Largest group first, ties by group order, each takes the shortest
    length at or above its band's shortest, and inside the published
    ends, at which its band still has a number with no leading zero to
    give -- AND WHOSE FORM THE CENSUS DOES NOT NAME (landing 2b.8).

    The second clause is the rule the review of landing 2b.4 asked for.
    A named form is settled over the number groups EXACTLY, so its cells
    are spoken for; but the length rule knew nothing of the census, and
    every number of the wide band four characters long is written `99.9`.
    A column publishing `99.9` on 199 cells had those 199 settled and
    then gave forty-eight groups the census owed nothing a length of
    four, so the twin wore that form on 247 cells and failed its own
    description.  Where no length inside the published ends escapes the
    named forms the first length with room stands, the census is missed
    and the report names it, which is what G9.5 step 3b already states.

    This file freezes no case whose census names a form, so no case here
    reaches the second clause; it is written from the rule statement
    all the same, because an oracle that carries only the rules its own
    cases reach cannot answer the next case.
    """
    low = column["length"]["min"]
    high = column["length"]["max"]
    named = {
        form for form in (column.get("shape_forms") or {})
        if form != WITHHELD
    }
    taken = {}
    fixed = {}
    # A number carrying an end spends a spelling of its own length too.
    for place in sorted(set(carriers)):
        if lengths is not None and place < len(groups) and packed[place][0] == NOTATION_NUMBER:
            key = (packed[place][1], lengths[place])
            taken[key] = taken.get(key, 0) + 1
    for place in sorted(range(len(groups)), key=lambda place: (-groups[place], place)):
        notation, band = packed[place]
        if place in carriers or notation != NOTATION_NUMBER:
            continue
        length = max(NUMBER_SHORTEST[band], low)
        spare = 0
        found = 0
        while length < high:
            if taken.get((band, length), 0) < plain_number_room(band, length):
                if not spare:
                    spare = length
                if number_at_form(band, length, named) not in named:
                    found = length
                    break
            length += 1
        if not found:
            # The walk's own answer where every length with room wears a
            # form the census names: the first length with room, or the
            # published longest where none had any.
            found = spare or min(length, high)
        length = found
        taken[(band, length)] = taken.get((band, length), 0) + 1
        fixed[place] = length
    return fixed


def numbers_walked(column, groups, lengths, packed, carriers, fixed):
    """G9.5 step 5's walk of the numbers' own lengths (plan P4-D190).

    Where the residual against the published total is not zero and no
    group the ordinary walk may move -- carrying no end and holding no
    length of its own -- can move toward it, the number groups carrying
    no end whose length's form the census does not name are walked the
    same way: largest group first, ties by group order, one character at
    a time, a group growing below `length.max` and shrinking above its
    band's shortest and `length.min`, and only to a length at which its
    band still has a number with no leading zero to give and whose form
    the census does not name. The walk stops when the residual reaches
    zero, changes sign, or no number can move.
    """
    lengths = list(lengths)
    low = column["length"]["min"]
    high = column["length"]["max"]
    target = _nearest_whole(
        F(wire_value(column["length"]["mean"])) * column["n_present"]
    )
    residual = target - sum(size * length for size, length in zip(groups, lengths))
    if not residual or len(groups) < 3:
        return lengths
    step = 1 if residual > 0 else -1
    for place in range(len(groups)):
        if place in carriers or place in fixed:
            continue
        if (lengths[place] < high) if step > 0 else (lengths[place] > low):
            return lengths
    named = {
        form for form in (column.get("shape_forms") or {})
        if form != WITHHELD
    }
    taken = {}
    walkable = []
    for place in range(len(groups)):
        notation, band = packed[place]
        if notation != NOTATION_NUMBER:
            continue
        taken[(band, lengths[place])] = taken.get((band, lengths[place]), 0) + 1
        if place in carriers or place not in fixed:
            continue
        if number_at_form(band, lengths[place], named) in named:
            continue
        walkable.append(place)
    walkable.sort(key=lambda place: (-groups[place], place))
    while residual:
        moved = None
        for place in walkable:
            band = packed[place][1]
            length = lengths[place] + step
            if length > high or length < max(low, NUMBER_SHORTEST[band]):
                continue
            if taken.get((band, length), 0) >= plain_number_room(band, length):
                continue
            if number_at_form(band, length, named) in named:
                continue
            moved = place
            break
        if moved is None:
            break
        band = packed[moved][1]
        taken[(band, lengths[moved])] -= 1
        lengths[moved] += step
        taken[(band, lengths[moved])] = taken.get((band, lengths[moved]), 0) + 1
        after = residual - step * groups[moved]
        if after and (after > 0) != (residual > 0):
            break
        residual = after
    return lengths


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
    # A NUMBER IS OFFERED ITS SPELLINGS WITH NO INVENTED LEADING ZERO
    # FIRST (G9.5 step 3), and those opening with a zero before another
    # figure only once they are spent; ordinary text has one pass.
    passes = (True, False) if notation == NOTATION_NUMBER else (False,)
    for clean in passes:
        for index in range(len(alphabet) ** length):
            candidate = enumerated_spelling(alphabet, length, index, leading)
            if candidate in used:
                continue
            if folded(candidate) in NO_VALUE_SPELLINGS:
                continue
            if notation_reading(candidate)[0] != notation:
                continue
            if clean and invents_a_leading_zero(candidate):
                continue
            if not clean and notation == NOTATION_NUMBER and not invents_a_leading_zero(candidate):
                continue
            # A NUMBER OF THE CODE BAND IS ITS e0 SPELLINGS (integration
            # repair of landing 2b.4): an exponent whose figure varies
            # multiplies the number by a power of ten.
            if (
                notation == NOTATION_NUMBER
                and band == CODE_BAND
                and "e" in candidate.lower()
                and not candidate.lower().endswith("e0")
            ):
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


def _free_text_lengths(column, groups, carriers, fixed=None):
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
    # A NUMBER'S OWN LENGTH (G9.5 step 3a) is held where it is, and the
    # other groups carry the average between them.
    fixed = fixed or {}
    for place in sorted(fixed):
        if place not in carriers:
            lengths[place] = fixed[place]
    target = _nearest_whole(
        F(wire_value(column["length"]["mean"])) * column["n_present"]
    )
    residual = target - sum(
        size * length for size, length in zip(groups, lengths)
    )
    free = [
        place for place in range(len(groups))
        if place not in carriers and place not in fixed
    ]
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


def _free_text_words(column, groups, lengths, carriers, fixed=None):
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
    fixed = fixed or {}
    for place in sorted(fixed):
        if place not in carriers:
            counts[place] = 1
    target = _nearest_whole(
        F(wire_value(column["words"]["mean"])) * column["n_present"]
    )
    residual = target - sum(size * count for size, count in zip(groups, counts))
    free = [
        place for place in range(len(groups))
        if place not in carriers and place not in fixed
    ]
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
    kept = [place for place in range(len(groups)) if place not in fixed]
    paired = sorted(counts[place] for place in kept)
    order = sorted(kept, key=lambda place: (lengths[place], place))
    settled = [1] * len(groups)
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
    if any(form != WITHHELD for form in column.get("shape_forms", {})):
        raise AssertionError(
            "the census names a written form, and this file states no reading "
            "of G9.5 step 7's forms, step 3a's form lengths or step 3b's band "
            "exchange. It freezes no free-text case whose census names one"
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
    # THE TRUTH VALUES A WORKBOOK CENSUS COUNTS (plan P4-D198), handed to
    # this column under a private key by the case, which carries the
    # census in its own workbook block.
    truths = column.get("_truths", 0)
    settled = None
    first_packed = None
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
            if truths > 0:
                # A shape is taken only where groups can be spelled as the
                # census's truth values; the first packing is kept otherwise.
                trial = numbers_out_of_the_code_band(groups, lengths, packed, carriers)
                trial = singletons_kept_as_text(groups, lengths, trial, carriers)
                held = number_lengths(column, groups, trial, carriers, lengths)
                if not truth_words(
                    groups, trial, carriers, held, truths, lengths, counts
                ):
                    if first_packed is None:
                        first_packed = (carriers, lengths, counts, packed)
                    continue
            settled = (carriers, lengths, counts, packed)
            break
        if settled is not None:
            break
    if settled is None and first_packed is not None:
        settled = first_packed
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
    # G9.5 STEP 3b's exchange out of the code band, then step 3c's
    # values written once kept as text (landing 2b.4, repair).
    packed = numbers_out_of_the_code_band(groups, lengths, packed, carriers)
    packed = singletons_kept_as_text(groups, lengths, packed, carriers)
    # G9.5 STEP 3a: A NUMBER'S LENGTH IS ITS OWN, and the other groups
    # carry the published average between them.
    fixed = number_lengths(column, groups, packed, carriers, lengths)
    chosen = truth_words(groups, packed, carriers, fixed, truths, lengths, counts)
    for place in sorted(chosen):
        fixed[place] = len(chosen[place])
    if fixed:
        lengths = _free_text_lengths(column, groups, carriers, fixed)
        counts = _free_text_words(column, groups, lengths, carriers, fixed)
        # ...AND WHAT THE WALK COULD NOT SPEND GOES TO THE NUMBERS (plan
        # P4-D190).
        lengths = numbers_walked(column, groups, lengths, packed, carriers, fixed)
    if set(counts) != {1}:
        raise AssertionError(
            "every group of a frozen case holds exactly one word: G9.5 step 7 "
            "fixes how several words share a length, but which of them the "
            "rejection rules of G9.2 are asked about is not stated, and this "
            "file freezes no case that turns on a reading it cannot take from "
            "the method"
        )
    # A TRUTH VALUE IS SPELLED, NOT MADE UP, so the date rule never meets it.
    if max(
        length for place, length in enumerate(lengths) if place not in chosen
    ) > LONGEST_FROZEN_WORD:
        raise AssertionError(
            f"a word of more than {LONGEST_FROZEN_WORD} characters can reach "
            "the date rule of G9.2, which this file states no reading of. It "
            "freezes no case that long"
        )
    content = []
    used = set()
    for place, (size, length, (notation, band)) in enumerate(
        zip(groups, lengths, packed)
    ):
        if place in chosen and chosen[place] not in used:
            spelling = chosen[place]
        else:
            spelling = _free_text_spelling(notation, band, length, used)
        used.add(spelling)
        content.extend([spelling] * size)
    _free_text_recount(column, content)
    return content


def truth_words(groups, packed, carriers, fixed, truths, lengths, counts):
    """Which groups are spelled `TRUE` and `FALSE` -- G9.5, plan P4-D198.

    Written from the rule statement.  Among the groups packed as text in
    the code alphabet and held to no length by a number, in group order:
    the first covering exactly ``truths`` cells is `TRUE`; else the first
    two, in order, covering them between them are `TRUE` and `FALSE`; else
    none.  A group carrying a published end is taken only where its pinned
    length is the spelling's and its pinned word count is one.
    """
    if truths < 1:
        return {}

    def fits(place, word):
        return place not in carriers or (
            lengths[place] == len(word) and counts[place] == 1
        )

    open_places = [
        place
        for place in range(len(groups))
        if place not in fixed and packed[place] == (NOTATION_TEXT, CODE_BAND)
    ]
    for place in open_places:
        if groups[place] == truths and fits(place, "TRUE"):
            return {place: "TRUE"}
    for first, one in enumerate(open_places):
        for other in open_places[first + 1:]:
            if (
                groups[one] + groups[other] == truths
                and fits(one, "TRUE")
                and fits(other, "FALSE")
            ):
                return {one: "TRUE", other: "FALSE"}
    return {}


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

    A count column publishing a census of spellings (method G6.8,
    contract 7.13) is written as that census and nothing else: each
    spelling as many times as it counts, in the order of the number it
    spells and then of the spelling, and no chain of drawn values.
    """
    census = column.get("number_spellings") or {}
    if census:
        content = spelled_census(census)
        content.extend(_straggler_cells(column, content))
        return content, [], []
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
    # G5.2's grain rule: a grain inside a role divides by its own count
    # of different NUMBERS, while the spelling budgets above keep the
    # counts the block arrived with.
    divided = column.get("_grain_values")
    values_wanted = min(
        numeric, folded_budget if divided is None else divided
    )
    # THE HUNDRED AND ONE RUNGS IN PERCENT ORDER (method G5.3 at
    # revision 2, plan P4-D4.10). The named eleven and the ninety
    # between them are one ladder, and a column of numbers interpolates
    # over the whole of it: an eleven-rung ladder says nothing about
    # how many cells lie inside a gap, which is what made a twin put
    # too few values where the real column crowded them.
    ladder = [column["_rungs"][key] for key in ALL_LADDER_KEYS]
    integer_valued = column["integer_valued"]
    effective = _effective_style_map(column["numeric_styles"])
    demand = min(
        sum(effective[style] for style in POINT_FREE_STYLES), numeric
    )
    # G5.2b: the share between the bands follows how many different
    # values the LADDER gives each of them, not how many cells each
    # holds.  Two bands holding the same number of cells need not hold
    # the same number of values, and a stratum count is about values.
    # THE GRID AND THE CAP OF G5.2a.  A column written at ONE fraction
    # width reads its ladder on that grid; a whole-valued one already
    # reads it on the integers through G5.4.  The cap is read off the
    # mode pair, the count of different numbers and the ladder.
    fractional = written_grid(
        column.get("fraction_widths", {}),
        integer_valued,
        numeric,
        named_point_free(column["numeric_styles"]),
    )
    cap = stratum_cap(column, ladder, numeric, CASE_SMALL_CELL_FLOOR)
    pair = band_strata(
        negatives, zeros, positives, values_wanted, ladder, numeric,
        integer_valued, fractional, cap,
    )
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
            numeric,
        )
    # G5.2a: the cells of a band divide between its strata by the
    # ladder's own plateaus, and evenly only where there is no ladder
    # to follow or the band has no more cells than strata.
    sizes, starts, bands = stratum_layout(
        numeric,
        negatives,
        zeros,
        positives,
        values_wanted,
        pair,
        ladder,
        integer_valued,
        fractional,
        cap,
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
        fractional,
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
            values.append(ladder[-1])
            continue
        if bands[index] == "zero":
            values.append(0.0)
            continue
        word = next(words)
        position = starts[index] * TWO64 + size * word
        if fractional > 0:
            # G5.3 ON A COLUMN WRITTEN AT ONE FRACTION WIDTH: the word
            # picks one of the stratum's own ranks, ``bounded(w, g)``, and
            # the stratum holds the grid value of the ladder at that rank.
            position = (starts[index] + ((size * word) >> 64)) * TWO64
        denominator = numeric * TWO64
        percents = percents_of(ladder)
        segment = ladder_segment(position, denominator, percents)
        record = convex_interpolation(
            position,
            denominator,
            ladder[segment],
            ladder[segment + 1],
            percents,
        )
        value = record["clamped"]
        if integer_valued:
            value = integer_rule(value)
        elif fractional > 0:
            value = float(grid_text(value, fractional))
        repaired = False
        if fractional <= 0:
            value, repaired = class_repair(value, bands[index], ladder[0], ladder[-1])
        record["stratum"] = index
        record["value"] = value
        record["repaired"] = repaired
        chain.append(record)
        values.append(value)
    # Both fallbacks apply to every stratum after the integer rule,
    # including the pinned ones (G5.5). ON A GRID the others are repaired
    # here, in stratum order, onto the nearest free grid step of their
    # sign (integration repair of landing 2b.1).
    for index in range(total):
        if index == 0 or (index == total - 1 and total >= 2):
            values[index], _ = class_repair(
                values[index], bands[index], ladder[0], ladder[-1]
            )
        elif fractional > 0 and bands[index] != "zero":
            value = values[index]
            wrong = (bands[index] == "negative" and value >= 0) or (
                bands[index] == "positive" and value <= 0
            )
            if wrong:
                values[index] = grid_step_of_sign(
                    bands[index], ladder, fractional,
                    {values[other] for other in range(total) if other != index},
                    total,
                )
                for record in chain:
                    if record["stratum"] == index:
                        record["value"] = values[index]
                        record["repaired"] = True
    # The VALUES step of G6.4 is taken before the styles, because the map
    # and the values are one question: a point-free quota needs cells
    # whose values are whole.
    signed = column.get("decimal_plus", {}).get("+", 0)
    values = whole_number_values(
        column["numeric_styles"],
        values,
        sizes,
        starts,
        bands,
        ladder,
        numeric,
        integer_valued,
        signed,
    )
    # AND TWO STRATA ARE NOT WRITTEN AS ONE CELL (G6.5a), after the
    # carrier walk because that walk moves values onto whole numbers
    # and can itself land two strata on one text.
    widths = column.get("fraction_widths", {})
    # THE PUBLISHED MODE IS A PROVED FIELD in a case's column, and the
    # levels fill reads the number it holds.
    mode = column.get("mode")
    if isinstance(mode, dict):
        mode = mode[FLOAT64]
    separated_on = grid_of(widths, integer_valued, numeric)
    if separated_on < 0:
        separated_on = finest_grid(widths)
    values = apart_values(
        column.get("n_distinct_values"),
        separated_on,
        values,
        sizes,
        starts,
        bands,
        ladder,
        numeric,
        mode,
        demand > 0,
        integer_valued,
        sum(widths.values()) < numeric,
    )
    # AND A WHOLE NUMBER WRITTEN TWO WAYS IS HELD BY TWO STRATA (plan
    # P4-D193), straight after the walk.
    values = twice_written(
        column, values, sizes, bands, ladder, integer_valued, numeric, demand
    )
    # AND AS MANY CELLS REACH A THOUSAND AS THE CENSUS OF MARKS COUNTS
    # (plan P4-D185), last of the value passes.
    values = grouped_enough(
        column, values, sizes, bands, integer_valued, numeric,
        CASE_SMALL_CELL_FLOOR,
    )
    cell_values = []
    for index, size in enumerate(sizes):
        cell_values.extend([values[index]] * size)
    styles, missed = style_allocation(
        column["numeric_styles"], cell_values, integer_valued
    )
    styles = plus_style_exchange(signed, styles, cell_values, integer_valued)
    # THE NAMED FIELD WIDTHS (G6.3), placed once the styles are settled.
    pads = pad_places(
        column.get("pad_widths", {}), styles, cell_values, integer_valued,
        column["numeric_styles"],
    )
    mark = grouping_mark_of(column)
    negative = column.get("negative_form", "minus")
    # The named count of the census; a pooled count names no form.
    plussed = plus_places(signed, styles, cell_values)
    # THE TWO MIXED CONVENTIONS, SPENT CELL BY CELL (landing 2b.7).  A cell is
    # groupable exactly where writing it with the published mark puts a
    # mark in it, which is asked of the writer rather than restated from
    # the rules about forms, orders and four whole figures.
    notations = notation_places(
        column.get("negative_notations", {}), negative, styles, cell_values
    )
    # ...asked with a mark that writes one (plan P4-D142).
    candidate = candidate_mark(column.get("thousands_marks", {}), mark)
    groupable = [
        styled_spelling(
            style, value, integer_valued, 0, candidate, notations[index],
            plussed[index], pads[index],
        )
        != styled_spelling(
            style, value, integer_valued, 0, "", notations[index],
            plussed[index], pads[index],
        )
        for index, (style, value) in enumerate(zip(styles, cell_values))
    ]
    marks = mark_places(
        column.get("thousands_marks", {}), mark, groupable,
        CASE_SMALL_CELL_FLOOR, cell_values,
    )
    content = [
        styled_spelling(
            style, value, integer_valued, 0, marks[index], notations[index],
            plussed[index], pads[index],
        )
        for index, (style, value) in enumerate(zip(styles, cell_values))
    ]
    # G6.5's padded sign exchange (plan P4-D145) comes before any zero is
    # spent: a cell at a named width cannot spend one.
    owed = max(0, folded_budget - len({folded(text) for text in content}))
    styles, content, _owed = padded_sign_exchange(
        styles, cell_values, integer_valued, pads, marks, notations, plussed,
        content, owed,
    )
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
        # A cell at a NAMED field width has spent its family (G6.3): every
        # further order writes one more figure, so it is not raised.
        if pads[index] >= 0:
            continue
        order = 1
        while True:
            raised = styled_spelling(
                styles[index],
                cell_values[index],
                integer_valued,
                order,
                marks[index],
                notations[index],
                plussed[index],
            )
            if folded(raised) not in held:
                break
            order += 1
        content[index] = raised
        held.add(folded(raised))
        shortfall -= 1
    content.extend(_straggler_cells(column, content))
    return content, chain, missed


def spelled_census(census):
    """Every spelling of a count census, as often as it was written -- G6.8."""
    content = []
    for spelling in sorted(census, key=lambda text: (int(text), text)):
        content.extend([spelling] * census[spelling])
    return content


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
    """A published ladder, both halves, as proved binary64 fields.

    Returns the eleven NAMED rungs, the claims for all hundred and one,
    the hundred and one rung VALUES keyed by name, and the ninety finer
    rungs as their own published block (plan P4-D4.10).  The two halves
    are built together because they are one ladder: a case that got its
    named rungs from here and its finer ones from somewhere else could
    publish a pair that goes down between them, which is exactly what
    the loader's Q19 refuses.
    """
    published = {}
    claims = {}
    rungs = {}
    for key in LADDER_KEYS:
        field, claim = nearest_field(texts[key])
        published[key] = field
        claims[("percentiles", key)] = claim
        rungs[key] = field[FLOAT64]
    finer, finer_claims, finer_rungs = _finer_ladder_fields(texts)
    for key in FINER_LADDER_KEYS:
        claims[("percentiles_between", key)] = finer_claims[(key,)]
        rungs[key] = finer_rungs[key]
    return published, claims, rungs, finer


FINER_LADDER_KEYS = tuple(
    f"p{percent:02d}"
    for percent in range(1, 100)
    if percent not in (1, 5, 10, 25, 50, 75, 90, 95, 99)
)


# The hundred and one rung names in PERCENT ORDER, which is the order
# a ladder is walked in and the order `PCT_FINE` stands in.
_NAME_AT_PERCENT = {
    0: "min", 1: "p01", 5: "p05", 10: "p10", 25: "p25", 50: "p50",
    75: "p75", 90: "p90", 95: "p95", 99: "p99", 100: "max",
}
ALL_LADDER_KEYS = tuple(
    _NAME_AT_PERCENT[percent]
    if percent in _NAME_AT_PERCENT
    else f"p{percent:02d}"
    for percent in range(101)
)


def _finer_ladder_fields(texts):
    """The ninety rungs the named ladder does not carry (plan P4-D4.10).

    THEY ARE PUT ON THE STRAIGHT LINE BETWEEN THE NAMED RUNGS, and that
    choice is the point rather than a convenience.  A case exists to
    pin the TRANSFORM, and the transform is what the generator does
    with whatever ladder it is handed.  Placing the finer rungs where
    the eleven-rung ladder already implied they were says: this column
    carries no information the coarse ladder did not, so any difference
    in the committed cells is the arithmetic of interpolating a longer
    list and nothing else.

    WHAT THAT MEANS THIS FILE DOES NOT YET PIN, said plainly because an
    earlier draft of this docstring named a `numeric_bent_ladder` case
    that does not exist.  Every finer ladder frozen here lies on the
    straight line, so reverting the whole mechanism from a hundred and
    one rungs to eleven moves the cells of exactly ONE case.  These
    vectors therefore check that the length dispatch is consistent
    between the two implementations; they do NOT check the fidelity
    mechanism on a ladder that bends, which is where the fact is worth
    its cost.  A bent case is owed.

    Each value is written to SIX DECIMAL PLACES, rounded DOWN, and
    both halves of that are needed.  Six places because the point on
    the line is not always a finite decimal -- the gaps between named
    percents are 1, 4, 5, 15 and 25 wide, and a fifteenth is a
    repeating decimal -- so a rung has to be written to some number of
    places to be published and proved at all.  Down rather than to
    nearest because flooring is MONOTONE: a non-decreasing sequence
    stays non-decreasing through it, so the hundred and one rungs
    cannot come out of order and fail the loader's own Q19.
    """
    named = {
        0: "min", 1: "p01", 5: "p05", 10: "p10", 25: "p25", 50: "p50",
        75: "p75", 90: "p90", 95: "p95", 99: "p99", 100: "max",
    }
    points = sorted(named)
    published = {}
    claims = {}
    rungs = {}
    for key in FINER_LADDER_KEYS:
        percent = int(key[1:])
        under = max(point for point in points if point < percent)
        over = min(point for point in points if point > percent)
        low = decimal_to_fraction(texts[named[under]])
        high = decimal_to_fraction(texts[named[over]])
        share = fractions.Fraction(percent - under, over - under)
        exact = low + share * (high - low)
        text = _floored_decimal_text(exact, 6)
        field, claim = nearest_field(text)
        published[key] = field
        claims[(key,)] = claim
        rungs[key] = field[FLOAT64]
    return published, claims, rungs


def _floored_decimal_text(value, places):
    """One rational written to ``places`` decimals, rounded DOWN.

    Python's ``//`` floors toward negative infinity for a negative
    numerator as well, which is what makes this monotone over the whole
    line and not only over its positive half.
    """
    scale = 10 ** places
    scaled = (value.numerator * scale) // value.denominator
    sign = "-" if scaled < 0 else ""
    digits = f"{abs(scaled)}".rjust(places + 1, "0")
    return f"{sign}{digits[:-places]}.{digits[-places:]}"


def exact_triple(text):
    """The exact number one spelling denotes, as `(sign, digits, power)`.

    THE CONTRACT'S OWN FORM, implemented here from that statement and
    never imported: a decimal spelling denotes `sign * digits * 10 **
    power`, and writing the digits stripped of BOTH leading and
    trailing zeros makes the triple canonical -- two spellings denote
    the same number exactly when their triples are equal.  Zero has one
    triple, `(0, (), 0)`, which is what makes `0` and `-0` one number.

    Returns None for a spelling that is not a plain decimal number,
    which is every cell of a role that does not carry a ladder.
    """
    body = text.strip()
    if not body:
        return None
    sign = 1
    if body[:1] == "+":
        body = body[1:]
    elif body[:1] == "-":
        sign = -1
        body = body[1:]
    power = 0
    for marker in ("e", "E"):
        if marker in body:
            body, _, exponent = body.partition(marker)
            if not exponent:
                return None
            try:
                power = int(exponent)
            except ValueError:
                return None
            break
    if "." in body:
        whole, _, part = body.partition(".")
        if "." in part:
            return None
        power = power - len(part)
        body = whole + part
    if not body:
        return None
    for character in body:
        if character not in "0123456789":
            return None
    # Strip the trailing zeros into the power, then the leading ones,
    # which is what makes two spellings of one number one triple.
    while body and body[-1:] == "0":
        body = body[:-1]
        power = power + 1
    while body and body[:1] == "0":
        body = body[1:]
    if not body:
        return (0, (), 0)
    return (sign, tuple(body), power)


def _distinct_numbers_of(content, prefix="", suffix=""):
    """How many different NUMBERS a list of finished cells holds.

    The exact number a spelling denotes, by the same canonical triple
    the contract states -- `sign * digits * 10 ** power`, the digits
    stripped of leading and trailing zeros -- so two spellings that
    round to one binary64 value but denote different numbers count as
    two, and two spellings of one number count as one.  Implemented
    here from that statement and not imported, like everything else in
    this file.
    """
    seen = set()
    for cell in content:
        body = cell
        if prefix or suffix:
            # ON THE AFFIXED ROLE THE NUMBERS ARE THE CORES, so the
            # pair comes off before the cell is read.  A cell that does
            # not wear the pair is a straggler and is not one of this
            # column's numbers at all.
            if not body.startswith(prefix):
                continue
            if not body.endswith(suffix):
                continue
            body = body[len(prefix): len(body) - len(suffix)] if suffix \
                else body[len(prefix):]
        found = exact_triple(body)
        if found is None:
            continue
        seen.add(found)
    return len(seen)


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
            "(date-sentinel)": 0,
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
    # The census of LAYOUTS (contract 7.12), REQUIRED on the identifier
    # role and forbidden everywhere else, so a case that states none
    # publishes the empty census a floored census gives a column whose
    # layouts are all held back -- and the walk below is then the walk
    # this oracle always had, which is why the three identifier cases
    # frozen before landing 2b.18 keep their committed cells.
    if role == "identifier" and "layout_forms" not in block:
        block["layout_forms"] = {}
    # ...and the literal prefixes (contract 7.12a, owner ruling of
    # 2026-09-17, item 1), REQUIRED on the identifier role and empty on
    # every case frozen before that ruling.
    if role == "identifier" and "layout_prefixes" not in block:
        block["layout_prefixes"] = {}
    # The census of SPELLINGS (contract 7.13), REQUIRED on the count role
    # and forbidden everywhere else, and EMPTY on every count case frozen
    # before landing 2b.18's second part: none of their source columns
    # wrote one number more than one way.
    if role == "count" and "number_spellings" not in block:
        block["number_spellings"] = {}
    # ...and the mark between thousands (contract numeric block, stage 2),
    # EMPTY for every case here: no source column these cases describe
    # was written with a grouped convention, so a case publishes no mark
    # and its frozen cells are the ones it froze before the key existed.
    if "numeric_styles" in block and "group_separator" not in block:
        block["group_separator"] = ""
    # ...and the notation of a negative and the count of signed decimals
    # (landing 2b.2), the minus in front and none for every case that
    # does not state its own: no source column those cases describe wrote
    # either, and their frozen cells are the ones they froze before.
    if "numeric_styles" in block and "negative_form" not in block:
        block["negative_form"] = "minus"
    if "numeric_styles" in block and "decimal_plus" not in block:
        block["decimal_plus"] = {}
    # ...and the wide-run fact (landing 2b.13), `none` for every case
    # that does not state its own: no source column these cases describe
    # wrote a point-free cell at or past 2**53 -- the widest whole
    # number any of them holds is far under it -- so the word is the one
    # a column with no such run publishes, and their frozen cells do not
    # move.
    if "numeric_styles" in block and "wide_runs" not in block:
        block["wide_runs"] = "none"
    # ...and the two MIXTURE censuses (landing 2b.7), EMPTY for every
    # case that does not state its own: no source column these cases
    # describe mixed two notations or two marks, so each census names
    # nothing and the generator writes the column's published majority
    # for every cell -- which is exactly what these cases froze before
    # the keys existed, so their frozen cells do not move.
    if "numeric_styles" in block and "negative_notations" not in block:
        block["negative_notations"] = {}
    if "numeric_styles" in block and "thousands_marks" not in block:
        block["thousands_marks"] = {}
    # ...and the same for the census of field widths (P4-D14), which is
    # that map's sibling and empty for every case here but one: a block
    # naming no padded cells takes a census of none.
    if "numeric_styles" in block and "pad_widths" not in block:
        block["pad_widths"] = {}
    # ...and the four censuses of HOW a column's dates were written
    # (landing 2b.6, contract C6-25d to C6-25g), on the datetime block
    # and no other.  EMPTY for every case that does not state its own:
    # each of these cases describes a source column read under a member
    # whose fields are of fixed width, which writes no month NAME, and
    # which names no zulu offset, so each census is empty and the cells
    # they froze before the censuses existed do not move.
    if "format" in block:
        for census in (
            "date_field_widths",
            "month_name_styles",
            "quarter_marker_case",
            "zulu_case",
        ):
            if census not in block:
                block[census] = {}
    # ...and the census of WHOLE-NUMBER field widths (P4-D30) is NOT
    # defaulted, which is deliberate.  The two above are empty for
    # almost every case here because almost no case has a decimal or a
    # padded cell.  This one covers `plain`, `leading_plus` and
    # `leading_zero` together, so a block naming any of those has cells
    # in it and an empty census would be a false statement about the
    # column rather than a quiet default.  Each case states its own,
    # from the source column it describes, and a case that forgets
    # stops the run here rather than being given a census nobody chose.
    if "numeric_styles" in block and "field_widths" not in block:
        raise SystemExit(
            "a numeric block states no `field_widths`: contract 7.10 "
            "requires the census on every block carrying a forms map, "
            "and it may not be defaulted (P4-D30)"
        )
    # The value histogram (contract C6-31, plan P4-D4.7), on the three
    # roles that carry a ladder.  It is REPORT-ONLY: the twin is not
    # held to it, so the cells this oracle freezes do not depend on it,
    # and every case here publishes the EMPTY census -- which is what a
    # column publishes when its bins cannot all clear the floor, and
    # what these hand-authored cases would publish if they had a source
    # column too thin to fill thirty-two bins.  A case that wanted the
    # census would have to state a shape a real column of its own
    # values could have, and none of these cases is about the shape.
    if "percentiles" in block and "value_histogram" not in block:
        block["value_histogram"] = {}
    # ...and the bins that hold NOTHING (contract 7.11, plan P4-D32),
    # on those same three roles.  It defaults to the EMPTY list, and
    # the empty list is the honest default here for a reason the two
    # censuses above do not share: an empty census means "held back"
    # while an empty list here means "no stretch of this column's range
    # is empty", and every case in this file states so few values that
    # the ladder it publishes is the whole of what is claimed about
    # where they lie.  A case that wanted a named stretch would have to
    # state a shape a real column of its own values could have, and
    # none of these cases is about the shape.  It is REPORT-ONLY and,
    # with no stretch named, method G6.7 does nothing and no cell here
    # depends on it.
    if "percentiles" in block and "empty_bins" not in block:
        block["empty_bins"] = []
    # ...and the two values each of those stretches lies between
    # (contract 7.11a, residual R-P4-138).  One pair per run of empty
    # bins, so with no stretch named this is empty too, and contract
    # Q21 -- as many pairs as there are runs -- is met by nought and
    # nought.
    if "percentiles" in block and "empty_edges" not in block:
        block["empty_edges"] = []
    # ...and how many different NUMBERS the block holds (contract Q17,
    # plan P4-D4.9), on those same three roles.  The figure is a
    # placeholder here and is replaced by a count of the FINISHED cells
    # once they exist, because it is a fact about them.
    if "percentiles" in block and "n_distinct_values" not in block:
        block["n_distinct_values"] = 0
    # ...and the MODE PAIR beside it (contract Q18, plan P4-D4.11), on
    # the same three roles.  Both keys are always present on a block
    # that carries a ladder; a withheld mode is `null` beside a count
    # of nought, which is what a column with no dominant value
    # publishes and what every case in this file publishes.  It is
    # REPORT-ONLY and costs no word, and since landing 2b.1 it steers ONE
    # rule: G5.2a's cap reads it, and a withheld pair hands that cap to
    # the count of different numbers and the ladder instead.
    if "percentiles" in block and "mode" not in block:
        block["mode"] = None
        block["mode_count"] = 0
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
        # A case reading its column jointly states its own form census
        # (landing 2b.3); every other case publishes its one form.
        if "resolution_mix" not in block:
            block["resolution_mix"] = {block["format"]: parsed}
        # ...and the census of marks between day and clock, and the
        # midnight statement (plan P4-D39), defaulted to what every cell
        # frozen before them already wears: a `T` on each parsed cell of a
        # column that writes a clock, none on one that writes no clock,
        # and no column standing wholly at midnight.  A case that states
        # its own keeps it.
        if "datetime_separators" not in block:
            block["datetime_separators"] = (
                {"upper_t": parsed} if block["resolution"] == "datetime" else {}
            )
        if "all_at_midnight" not in block:
            block["all_at_midnight"] = False
        # ...and the count of values at midnight (landing 2b.3), which a
        # case states only where its column is partly at midnight.
        if "n_at_midnight" not in block:
            block["n_at_midnight"] = parsed if block["all_at_midnight"] else None
    if block["n_missing"]:
        block["missing_by_class"] = dict(block["missing_by_class"])
        block["missing_by_class"]["(withheld)"] = block["n_missing"]
        if role not in ("identifier", "free_text", "numeric_unrepresentable"):
            block["n_missing_withheld"] = block["n_missing"]
    return block


def clock_repair(ordinal, last, ceiling):
    """G7A.4's all-different repair: step up, THEN clamp.

    The order is the rule and not an accident.  Stepping up is what
    makes two ranks that interpolated onto one time different -- the
    later one takes the next ordinal, which is what the source column
    itself did -- and the clamp is what keeps that step inside the
    published `latest`.  Clamping first and stepping after would carry
    a rank past the published end.
    """
    if ordinal <= last:
        ordinal = last + 1
    if ordinal > ceiling:
        ordinal = ceiling
    return ordinal


def _field_value(published):
    """The binary64 a published field stands for.

    Every float this file publishes is written as a field -- its exact
    decimal, its rational, and the binary64 it rounds to -- so that the
    proof layer can show the rounding. Arithmetic takes the binary64,
    because that is the number the shipped code holds.
    """
    if isinstance(published, dict):
        return published[FLOAT64]
    return float(published)


def joined_part_view(column, place):
    """One position of a joined column, as a numeric column (G6B.2).

    The same trick the affixed core view plays, for the same reason: a
    cell reading `120/80` is not itself a number, so the universal
    counts say the column holds none, while the block for a position
    answers for that position's numbers alone.

    DISTINCTNESS IS SWAPPED FOR THE GRAIN'S OWN COUNT, which is G5.2's
    grain rule and G6B.2's sentence pointing at it.  The counts a
    position arrives with are counts of whole CELLS -- a 36-row column
    of `N/M` publishes 36 different cells while its first position
    holds 11 different numbers -- and a stratum holds a value.  So the
    division reads `n_distinct_values` from the position's own block.
    THE SPELLING BUDGETS DO NOT: a budget buys the second way of
    writing one number, and a count of numbers cannot pay for it, so
    they keep the counts the block arrives with.
    """
    view = dict(column)
    view.update(column["parts"][place])
    view["n_present"] = column["n_joined"]
    view["n_numeric"] = column["n_joined"]
    view["n_not_numeric"] = 0
    view["n_out_of_range"] = 0
    view["n_contradictory"] = 0
    view["_grain_values"] = column["parts"][place]["n_distinct_values"]
    if view["_grain_values"] < 1:
        raise AssertionError(
            "a position reached the numeric machinery with no count of "
            "different numbers: G5.2's grain rule would divide it into "
            "one stratum and the case would freeze a column nobody "
            "described.  Invariant Q17 forbids a block that used a "
            "value from publishing zero here"
        )
    return view


def joined_ranks(values):
    """Zero-based ranks, ties sharing the average of the ranks they span.

    G6B.4 step 4 pins the ORIGIN as well as the tie rule: the smallest
    value takes rank 0 and the largest takes `T - 1`.  The one-based
    convention is at least as common and writes different cells.
    """
    order = sorted(range(len(values)), key=lambda seat: values[seat])
    ranks = [0.0] * len(values)
    at = 0
    while at < len(order):
        last = at
        while (
            last + 1 < len(order)
            and values[order[last + 1]] == values[order[at]]
        ):
            last = last + 1
        shared = (at + last) / 2.0
        for seat in range(at, last + 1):
            ranks[order[seat]] = shared
        at = last + 1
    return ranks


def joined_cell(held, column, row):
    """One finished cell: each position padded, the separator between."""
    written = ""
    for place in range(column["n_parts"]):
        if place:
            written = written + column["separator"]
        text = held[place][row]
        width = column["part_min_widths"][place]
        while len(text) < width:
            text = "0" + text
        written = written + text
    return written


def joined_part_budget(column, place):
    """The content words one position of a joined column draws (G4.3)."""
    view = joined_part_view(column, place)
    view["role"] = "continuous"
    content, _placement = word_budget(view, column["n_joined"])
    return content


def _joined_content(column):
    """The content list of a joined column -- method section G6B.

    Each position is built by the numeric rules over its own view, the
    reserve is what remains, and the pairing walk then decides which
    number of one position meets which of the next.
    """
    n_parts = column["n_parts"]
    n_joined = column["n_joined"]
    words = list(column["_content_words"])
    at = 0
    drawn = []
    for place in range(n_parts):
        view = joined_part_view(column, place)
        budget = joined_part_budget(column, place)
        view["_content_words"] = words[at: at + budget]
        view["_rungs"] = column["_rungs"][place]
        at = at + budget
        values, _chain, _missed = _numeric_content(view)
        drawn.append(values)
    # THE RESERVE is everything the positions did not take: G4.3 sets
    # aside `max(n_joined - 1, 0)` for every position after the first.
    reserve = words[at:]
    # WHAT THE WALK IS ASKED FOR is not the whole column's count where
    # any cell did not split: the stand-ins built afterwards are all one
    # spelling and add exactly one.
    invented = 1 if column["n_present"] > n_joined else 0
    wanted = max(column["n_distinct"] - invented, 0)
    held = repaired_pairing(drawn, column, wanted, reserve)
    content = [joined_cell(held, column, row) for row in range(n_joined)]
    stragglers = column["n_present"] - n_joined
    if stragglers:
        raise AssertionError(
            "this case builds no stand-ins; a joined column with cells "
            "that did not split needs the walk of G6B.5 and a case of "
            "its own"
        )
    return content


def repaired_pairing(drawn, column, wanted, words):
    """Which numbers meet in a row -- method section G6B.4.

    Written from that section and from nothing else.  Every step swaps
    two rows' numbers within ONE position, so each position keeps its
    multiset and only the pairing moves.
    """
    total = column["n_joined"]
    n_parts = column["n_parts"]
    agreements = column["part_agreements"]
    above_targets = column["part_above"]
    # STEP 1: each position sorted by (value, spelling).
    held = []
    for place in range(n_parts):
        pairs = sorted((float(text), text) for text in drawn[place])
        held.append([pair[1] for pair in pairs])
    # STEP 2: position 0 is the anchor and never moves.  Each position
    # after it starts where the pair it makes with the anchor says --
    # seat `p - 1` of the key, since the seats run (0,1), (0,2), ...
    # -- and a shuffling position takes its own slice of the reserve.
    slice_size = max(total - 1, 0)
    for place in range(1, n_parts):
        seat = place - 1
        anchored = (
            _field_value(agreements[seat]) if seat < len(agreements) else 0.0
        )
        taken = words[(place - 1) * slice_size:]
        if anchored < -0.4:
            held[place] = [held[place][total - 1 - i] for i in range(total)]
        elif anchored < 0.4 and len(taken) >= slice_size:
            order = permutation(total, list(taken[:slice_size]))
            held[place] = [held[place][i] for i in order]
    numbers = [[float(text) for text in held[place]]
               for place in range(n_parts)]
    ranks = [joined_ranks(numbers[place]) for place in range(n_parts)]
    middle = (total - 1) / 2.0
    spread = []
    for place in range(n_parts):
        summed = 0.0
        for row in range(total):
            away_from = ranks[place][row] - middle
            summed = summed + away_from * away_from
        spread.append(summed)
    # STEP 3: every pair is scored, because a pair has two different
    # positions and at most one of them can be the anchor.
    firsts = []
    seconds = []
    seats = []
    seat = 0
    for first in range(n_parts):
        for second in range(first + 1, n_parts):
            if seat < len(agreements) and seat < len(above_targets):
                seats.append(seat)
                firsts.append(first)
                seconds.append(second)
            seat = seat + 1
    tops = []
    aboves = []
    for index in range(len(seats)):
        first = firsts[index]
        second = seconds[index]
        summed = 0.0
        counted = 0
        for row in range(total):
            summed = summed + (ranks[first][row] - middle) * (
                ranks[second][row] - middle
            )
            if numbers[first][row] > numbers[second][row]:
                counted = counted + 1
        tops.append(summed)
        aboves.append(counted)
    cells = []
    seen = {}
    for row in range(total):
        text = joined_cell(held, column, row)
        cells.append(text)
        seen[text] = seen.get(text, 0) + 1
    room = RANK_AGREEMENT_WINDOW - AGREEMENT_ROUNDING
    tip = 1.0 / float(total * (len(seats) + 1)) if seats else 0.0

    def distance():
        """STEP 4, and an agreement is scored OUTSIDE its own window.

        `part_above` and the count of different cells are checked
        exactly; an agreement is checked inside G12.9's window.  So the
        agreement costs only what it lies outside HALF that window, and
        the raw gap is kept as a tie-break worth less, over every pair
        at once, than one different cell.
        """
        out = abs(len(seen) - wanted) / float(total)
        for index in range(len(seats)):
            place = seats[index]
            first = firsts[index]
            second = seconds[index]
            out = out + float(abs(aboves[index] - above_targets[place]))
            divisor = (spread[first] * spread[second]) ** 0.5
            agreed = tops[index] / divisor if divisor > 0.0 else 0.0
            gap = abs(agreed - _field_value(agreements[place]))
            out = out + (gap - room if gap > room else 0.0)
            inside = gap if gap < room else room
            out = out + (inside / room) * tip
        return out

    def conforming():
        """WHICH pairs sit inside the window G12.9 publishes -- step 5.

        A mask seat by seat.  The rule the mask serves is about a pair
        LEAVING its window, and a count cannot say which pair is which:
        one leaving while another enters holds the count still.
        """
        mask = []
        for index in range(len(seats)):
            place = seats[index]
            first = firsts[index]
            second = seconds[index]
            divisor = (spread[first] * spread[second]) ** 0.5
            agreed = tops[index] / divisor if divisor > 0.0 else 0.0
            mask.append(
                abs(agreed - _field_value(agreements[place])) <= room
            )
        return mask

    def cells_gap():
        """How far the count of DIFFERENT CELLS stands -- step 5.

        Its own reading.  Step 5 keeps the two exact facts apart: this
        one belongs to no pair and is the one deliberately licensed to
        yield, so adding it to the above-counts would let a gained cell
        buy a lost row of `part_above` with nothing able to see it.
        """
        return abs(len(seen) - wanted)

    def above_marks():
        """One above-count gap PER PAIR, in seat order -- step 5.

        By identity, because step 5's refusals are per pair.  A SUM
        cannot serve: an above-count can go from held to missed while
        another improves by one, and the total says nothing happened.

        Every pair is read rather than only the pairs the swap moved.
        A pair the swap cannot touch has the same gap on both sides, so
        it changes neither a comparison between the two readings nor
        any per-entry test between them.
        """
        marks = []
        for index in range(len(seats)):
            place = seats[index]
            marks.append(abs(aboves[index] - above_targets[place]))
        return marks

    def swap_allowed(before_mask, after_mask, before_above, after_above,
                     before_cells, after_cells):
        """May a swap be taken, given what it did?  Step 5.

        THREE refusals, in the order step 5 gives them, and the first
        two are asked on EVERY try rather than only where a pair left
        its window:

        1. a swap taking any pair's above-count from HELD to missed;
        2. a swap taking any above-count further from its published
           value, while the above-counts do not fall as a whole and no
           other above-count reaches its published value in the same
           swap;
        3. a swap taking any pair out of its window, while neither
           exact fact comes closer -- neither the above-counts as a
           whole nor the count of different cells.

        The third is a DISJUNCTION and not a re-mixed total, because
        "an exactly-checked fact" is singular: netting rows against
        cells is the arithmetic step 5 forbids.
        """
        sold = False
        worsened = False
        entered = False
        for index in range(len(before_above)):
            if before_above[index] == 0 and after_above[index] != 0:
                sold = True
            if after_above[index] > before_above[index]:
                worsened = True
            if before_above[index] != 0 and after_above[index] == 0:
                entered = True
        was = sum(before_above)
        now = sum(after_above)
        if sold:
            return False
        if worsened and now >= was and not entered:
            return False
        left = any(
            before_mask[index] and not after_mask[index]
            for index in range(len(before_mask))
        )
        if not left:
            return True
        return now < was or after_cells < before_cells

    def owed():
        """Is any published pairing fact still unmet?  Step 5."""
        if len(seen) != wanted:
            return True
        for index in range(len(seats)):
            place = seats[index]
            if aboves[index] != above_targets[place]:
                return True
            first = firsts[index]
            second = seconds[index]
            divisor = (spread[first] * spread[second]) ** 0.5
            agreed = tops[index] / divisor if divisor > 0.0 else 0.0
            if abs(agreed - _field_value(agreements[place])) > (
                AGREEMENT_ROUNDING
            ):
                return True
        return False

    def would_write(row, place, text):
        """The cell `row` would hold if position `place` held `text`."""
        written = ""
        for step in range(n_parts):
            if step:
                written = written + column["separator"]
            spelling = text if step == place else held[step][row]
            width = column["part_min_widths"][step]
            while len(spelling) < width:
                spelling = "0" + spelling
            written = written + spelling
        return written

    def proposed(one, two, place, turn):
        """STEP 5's proposal, method section G6B.4a."""
        if len(seen) == wanted:
            # G6B.4a's first bullet, second sub-case: the count of
            # different cells is met and an above-count may not be.
            # The acceptance rule refuses to trade one above-count for
            # another, so the walk cannot reach the repair sideways and
            # has to aim at it -- on every OTHER turn of this
            # position only, because aiming on every turn starves the
            # agreement.  The turn is the position's own: `turn` is
            # how many turns it has already had, and gating on the
            # walk's own counter instead starves one parity outright
            # wherever the mover count is even (method G6B.4a,
            # amendment A-P4-52).
            if (turn + place) % 2:
                return one, two
            for index in range(len(seats)):
                place_seat = seats[index]
                gap = aboves[index] - above_targets[place_seat]
                if gap == 0:
                    continue
                if firsts[index] != place and seconds[index] != place:
                    continue
                over = gap > 0
                found = one
                for step in range(PROPOSAL_REACH):
                    row = (one + step) % total
                    higher = (
                        numbers[firsts[index]][row]
                        > numbers[seconds[index]][row]
                    )
                    if higher == over:
                        found = row
                        break
                partner = two
                for step in range(PROPOSAL_REACH):
                    row = (two + step) % total
                    if row != found and (
                        held[place][row] != held[place][found]
                    ):
                        partner = row
                        break
                return found, partner
            return one, two
        short = len(seen) < wanted
        found = one
        if short:
            for step in range(PROPOSAL_REACH):
                row = (one + step) % total
                if seen[cells[row]] > 1:
                    found = row
                    break
        else:
            fewest = 0
            for step in range(PROPOSAL_REACH):
                row = (one + step) % total
                holding = seen[cells[row]]
                if step == 0 or holding < fewest:
                    fewest = holding
                    found = row
        partner = two
        for step in range(PROPOSAL_REACH):
            row = (two + step) % total
            if row == found or held[place][row] == held[place][found]:
                continue
            made_here = would_write(found, place, held[place][row])
            made_there = would_write(row, place, held[place][found])
            if short:
                if made_here not in seen and (
                    made_there not in seen or seen[cells[row]] > 1
                ):
                    partner = row
                    break
            elif made_here in seen and (
                made_there in seen or made_there == made_here
            ):
                partner = row
                break
        return found, partner

    away = distance()
    tries = 0
    at = 0
    restarts = 0
    movers = n_parts - 1
    # Step 5: at least one try for every movable position.
    ceiling = max(200 * total, movers)
    while owed() and tries < ceiling and len(words) >= 2:
        place = 1 + tries % movers
        turn = tries // movers
        tries = tries + 1
        # STEP 5's cursor: it starts again inside the reserve, ONE WORD
        # further along than the restart before it, so a second pass
        # does not draw the pairs the first one drew.
        if at + 1 >= len(words):
            restarts = restarts + 1
            at = restarts % max(len(words) - 1, 1)
        one = bounded(words[at], total)
        two = bounded(words[at + 1], total)
        at = at + 2
        one, two = proposed(one, two, place, turn)
        if one == two or held[place][one] == held[place][two]:
            continue
        kept_tops = list(tops)
        kept_aboves = list(aboves)
        kept_conforming = conforming()
        kept_above = above_marks()
        kept_cells = cells_gap()
        moved = [
            index
            for index in range(len(seats))
            if firsts[index] == place or seconds[index] == place
        ]
        for index in moved:
            first = firsts[index]
            second = seconds[index]
            other = first if second == place else second
            tops[index] = tops[index] + (
                ranks[other][one] - ranks[other][two]
            ) * (ranks[place][two] - ranks[place][one])
            for row in (one, two):
                if numbers[first][row] > numbers[second][row]:
                    aboves[index] = aboves[index] - 1
        held[place][one], held[place][two] = held[place][two], held[place][one]
        numbers[place][one], numbers[place][two] = (
            numbers[place][two], numbers[place][one])
        ranks[place][one], ranks[place][two] = (
            ranks[place][two], ranks[place][one])
        for index in moved:
            first = firsts[index]
            second = seconds[index]
            for row in (one, two):
                if numbers[first][row] > numbers[second][row]:
                    aboves[index] = aboves[index] + 1
        made_one = joined_cell(held, column, one)
        made_two = joined_cell(held, column, two)
        for gone in (cells[one], cells[two]):
            seen[gone] = seen[gone] - 1
            if seen[gone] < 1:
                del seen[gone]
        for made in (made_one, made_two):
            seen[made] = seen.get(made, 0) + 1
        now = distance()
        # Step 5's three refusals, per pair and per exact fact.
        keep = swap_allowed(kept_conforming, conforming(),
                            kept_above, above_marks(),
                            kept_cells, cells_gap())
        # AN EQUAL SWAP IS TAKEN, not only a better one.
        if keep and now <= away:
            away = now
            cells[one] = made_one
            cells[two] = made_two
            continue
        for made in (made_one, made_two):
            seen[made] = seen[made] - 1
            if seen[made] < 1:
                del seen[made]
        for back in (cells[one], cells[two]):
            seen[back] = seen.get(back, 0) + 1
        held[place][one], held[place][two] = held[place][two], held[place][one]
        numbers[place][one], numbers[place][two] = (
            numbers[place][two], numbers[place][one])
        ranks[place][one], ranks[place][two] = (
            ranks[place][two], ranks[place][one])
        tops = kept_tops
        aboves = kept_aboves
    return held

def affixed_core_view(column):
    """An affixed column as the numeric machinery must see it (G6A.2).

    THE ROLE HAS TWO POPULATIONS and the profile publishes facts about
    both.  The universal class counts answer for the CELLS -- a cell
    reading `[12]` is not itself a number, so such a column publishes
    `n_numeric` of 0 -- while the quantitative block answers for the
    CORES, the text left when the pair comes off.  An implementer who
    reads one set as the other builds a column of nothing at all.

    So the cores are handed over as a column in their own right, with
    the CORE class counts standing where the cell counts were.  Every
    rule of G5 and G6 then applies unchanged.

    DISTINCTNESS IS SWAPPED FOR THE CORES' OWN COUNT, which is G5.2's
    grain rule.  The counts an affixed column publishes are counts of
    whole CELLS, and a cell wearing an affix can differ from another
    while their cores hold one number -- so the division and the
    division reads `n_distinct_values` from the quantitative block,
    which answers for the cores.  THE SPELLING BUDGETS DO NOT: an
    affixed cell's spelling is its core's spelling with fixed text
    around it, so the cells' count IS the cores' count, and a count of
    numbers cannot buy a second way of writing one number.
    """
    core = dict(column)
    core["n_numeric"] = column["n_core_numeric"]
    core["n_not_numeric"] = column["n_core_not_numeric"]
    core["n_out_of_range"] = column["n_core_out_of_range"]
    core["n_contradictory"] = column["n_core_contradictory"]
    core["n_present"] = column["n_affixed"]
    core["_grain_values"] = column["n_distinct_values"]
    if core["_grain_values"] < 1:
        raise AssertionError(
            "an affixed column reached the numeric machinery with no "
            "count of different numbers: G5.2's grain rule would "
            "divide its cores into one stratum.  Invariant Q17 forbids "
            "a block that used a value from publishing zero here"
        )
    return core


def _affixed_content(column):
    """The content list of an affixed column -- method section G6A.

    The cores first, by the numeric rules over the core view, then the
    pair character for character as published.  A case whose every
    present cell wore the pair has no stragglers, and this file builds
    only such a case: the straggler walk of G6A.3 is a second branch
    with its own refusals and belongs to a case of its own.
    """
    core = affixed_core_view(column)
    cores, _chain, _missed = _numeric_content(core)
    prefix = column["affix_prefix"]
    suffix = column["affix_suffix"]
    stragglers = column["n_present"] - column["n_affixed"]
    if stragglers:
        raise AssertionError(
            "this case builds no stragglers; a column with cells that "
            "wore no pair needs the walk of G6A.3 and a case of its own"
        )
    return [prefix + core_text + suffix for core_text in cores]


def _clock_content(column):
    """The content list of a clock column -- method section G7A.

    The same stratified inverse transform the date role uses, with the
    ladder read in the form's OWN unit, plus the one repair that belongs
    to this role alone: where the column's values were all different, so
    are the twin's, because a closed finite space of times has a place
    for each of them.
    """
    form = column["clock_form"]
    parsed = column["n_present"] - column["n_unparsed"]
    rungs = [
        clock_ordinal_of(column["clock_percentiles"][key], form)
        for key in LADDER_KEYS
    ]
    # G7A.4's condition, stated on the published counts alone.  The
    # obligation is EXACT for this role where every other shape's
    # distinctness falls to an envelope.
    apart = column["n_distinct"] - column["n_unparsed"] >= parsed
    ceiling = clock_ordinal_of(column["latest"], form)
    last = clock_ordinal_of(column["earliest"], form)
    words = iter(column["_content_words"])
    content = []
    for rank in range(parsed):
        # The two ends are the published TEXT and not a re-spelling of
        # an ordinal, and neither costs a word.
        if rank == 0:
            content.append(column["earliest"])
            continue
        if rank == parsed - 1 and parsed >= 2:
            content.append(column["latest"])
            continue
        ordinal = interpolated_ordinal(
            rank * TWO64 + next(words), parsed * TWO64, rungs
        )
        if apart:
            ordinal = clock_repair(ordinal, last, ceiling)
        last = ordinal
        content.append(clock_spelling_of(ordinal, form))
    # G7A.5.  The stand-ins this file builds are `text-N`, which reads
    # as a clock time in NEITHER form, so the exclusion that belongs to
    # this role is met by construction rather than by a search.
    content.extend(text_stand_ins(content, column["n_unparsed"]))
    return content


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


def _date_gap_places():
    """A short study span whose rungs fall on shared days (plan P4-D130).

    Forty dates over ten days: four of the pins stand on the first day
    and three on the last, and the gaps between the others are one to
    three days wide -- the shape where WHERE a pin stands inside its own
    day decides how many of a gap's ranks each day receives.
    """
    rungs = [
        "2024-03-01", "2024-03-01", "2024-03-01", "2024-03-01", "2024-03-03",
        "2024-03-05", "2024-03-08", "2024-03-09", "2024-03-10", "2024-03-10",
        "2024-03-10",
    ]
    column = _universal(
        "column_1", "datetime", "datetime", "data", "ok",
        n_present=40, n_missing=0, n_distinct=10, n_distinct_folded=10,
        n_numeric=0, n_not_numeric=40, n_out_of_range=0, n_contradictory=0,
        format="iso-date", resolution="date", time_precision="date",
        subsecond_digits=0, datetimes_read_at="local",
        earliest=rungs[0], latest=rungs[10],
        earliest_utc_offset="(none)", latest_utc_offset="(none)",
        date_percentiles=dict(zip(LADDER_KEYS, rungs)),
        n_unparsed=0, utc_offsets={"(none)": 40},
    )
    return {
        "why": "the places G7.3 gives its pins inside their own days (plan "
        "P4-D130): the first pin at the start of its day, the last at the end "
        "of its own, every other on the straightest count the pins allow, and "
        "a gap's ranks drawn across the stretch between two places. Drawn over "
        "each gap's two pinned days whole, a pinned day took a day's share from "
        "each side of it -- a spike at every rung of a short study span -- and "
        "that is this case's mutant.",
        "column": column,
        "rows": 40,
        "identifier_declared": False,
    }


def _date_thinning_week():
    """A week of dates thinning out from its first day (plan P4-D138).

    Forty dates, a dozen on the first day and one on the last: the five
    lowest pins share the first day, and every other gap is a day or two
    wide. The straightest count gives the first day only the ranks its
    pins span, so the middles bend the count less and are taken.
    """
    rungs = [
        "2024-03-01", "2024-03-01", "2024-03-01", "2024-03-01", "2024-03-01",
        "2024-03-02", "2024-03-03", "2024-03-05", "2024-03-05", "2024-03-06",
        "2024-03-07",
    ]
    column = _universal(
        "column_1", "datetime", "datetime", "data", "ok",
        n_present=40, n_missing=0, n_distinct=7, n_distinct_folded=7,
        n_numeric=0, n_not_numeric=40, n_out_of_range=0, n_contradictory=0,
        format="iso-date", resolution="date", time_precision="date",
        subsecond_digits=0, datetimes_read_at="local",
        earliest=rungs[0], latest=rungs[10],
        earliest_utc_offset="(none)", latest_utc_offset="(none)",
        date_percentiles=dict(zip(LADDER_KEYS, rungs)),
        n_unparsed=0, utc_offsets={"(none)": 40},
    )
    return {
        "why": "G7.3's choice between its two sets of places (plan P4-D138): on "
        "a week whose dates thin out from the first day, every pin at its "
        "unit's middle bends the count from day to day less than the "
        "straightest count does, so the middles are taken. The straightest "
        "count alone gave the first day only the ranks its pins span -- 0.57 "
        "of a thinning week's real first day -- and that is this case's "
        "mutant.",
        "column": column,
        "rows": 40,
        "identifier_declared": False,
    }


def _date_peak_heap():
    """Forty dates peaking over a week, two pins on each of three days (P4-D138).

    The pins at the tenth and twenty-fifth percents share a day, the
    fiftieth and seventy-fifth share the next, the ninetieth and
    ninety-fifth the one after: three heaps, none holding an end, each
    standing at its unit's middle in the straightest count, which is
    taken.
    """
    rungs = [
        "2024-03-02", "2024-03-02", "2024-03-02", "2024-03-04", "2024-03-04",
        "2024-03-05", "2024-03-05", "2024-03-06", "2024-03-06", "2024-03-06",
        "2024-03-07",
    ]
    column = _universal(
        "column_1", "datetime", "datetime", "data", "ok",
        n_present=40, n_missing=0, n_distinct=6, n_distinct_folded=6,
        n_numeric=0, n_not_numeric=40, n_out_of_range=0, n_contradictory=0,
        format="iso-date", resolution="date", time_precision="date",
        subsecond_digits=0, datetimes_read_at="local",
        earliest=rungs[0], latest=rungs[10],
        earliest_utc_offset="(none)", latest_utc_offset="(none)",
        date_percentiles=dict(zip(LADDER_KEYS, rungs)),
        n_unparsed=0, utc_offsets={"(none)": 40},
    )
    return {
        "why": "G7.3's heaps (plan P4-D138): two or more pins on a day holding "
        "neither end stand at that day's middle in the straightest count and "
        "do not move. Moved onto the straight line like any other pin, a "
        "peak's day kept only the ranks its pins span -- 0.74 of a peaked "
        "fortnight's real peak -- and that is this case's mutant.",
        "column": column,
        "rows": 40,
        "identifier_declared": False,
    }


def _month_first_widths():
    """A month-first column counting each class of width by its own words.

    Eighty dates over a year, eleven of them written with both fields
    padded, eleven with neither, and the dates whose month alone is below
    ten written unpadded thirty times and padded eleven (plan P4-D132).
    """
    rungs = [
        "2024-01-02", "2024-01-05", "2024-01-20", "2024-02-09", "2024-04-01",
        "2024-06-15", "2024-09-05", "2024-10-28", "2024-11-19", "2024-12-10",
        "2024-12-30",
    ]
    column = _universal(
        "column_1", "datetime", "datetime", "data", "ok",
        n_present=80, n_missing=0, n_distinct=70, n_distinct_folded=70,
        n_numeric=0, n_not_numeric=80, n_out_of_range=0, n_contradictory=0,
        format="month-first-date", resolution="date", time_precision="date",
        subsecond_digits=0, datetimes_read_at="local",
        earliest=rungs[0], latest=rungs[10],
        earliest_utc_offset="(none)", latest_utc_offset="(none)",
        date_percentiles=dict(zip(LADDER_KEYS, rungs)),
        n_unparsed=0, utc_offsets={"(none)": 80},
        date_field_widths={
            "padded": 11, "unpadded": 11,
            "first-field-padded": 11, "first-field-unpadded": 30,
        },
    )
    return {
        "why": "the classes of width of G7.5 (plan P4-D132): a date whose "
        "month alone is below ten is written from the first-field words the "
        "census counts for such dates, and not from the joint words of dates "
        "whose two fields both are. This case's mutant writes that class as "
        "the joint words pad its field, eleven to eleven, and the dates whose "
        "month alone shows a width take the other padding.",
        "column": column,
        "rows": 80,
        "identifier_declared": False,
    }


def _may_month_names():
    """A textual column whose cells of May wrote their own style (P4-D133)."""
    rungs = [
        "2024-01-03", "2024-01-10", "2024-02-01", "2024-03-15", "2024-05-02",
        "2024-05-14", "2024-05-28", "2024-08-11", "2024-10-02", "2024-12-01",
        "2024-12-20",
    ]
    column = _universal(
        "column_1", "datetime", "datetime", "data", "ok",
        n_present=60, n_missing=0, n_distinct=55, n_distinct_folded=55,
        n_numeric=0, n_not_numeric=60, n_out_of_range=0, n_contradictory=0,
        format="textual-day-first-date", resolution="date", time_precision="date",
        subsecond_digits=0, datetimes_read_at="local",
        earliest=rungs[0], latest=rungs[10],
        earliest_utc_offset="(none)", latest_utc_offset="(none)",
        date_percentiles=dict(zip(LADDER_KEYS, rungs)),
        n_unparsed=0, utc_offsets={"(none)": 60},
        month_name_styles={
            "title-either-space-no-comma": 20,
            "upper-abbreviated-hyphen-no-comma": 40,
        },
    )
    return {
        "why": "the length a name of May shows, which is either (plan P4-D133): "
        "a rank of May is written from the census's `either` words, here a "
        "title-case name between spaces, and every other rank from the words "
        "that name a length. This case's mutant offers the ranks of May no "
        "`either` word, so they take the other ranks' upper-case name between "
        "hyphens.",
        "column": column,
        "rows": 60,
        "identifier_declared": False,
    }


def _reserved_name_floor():
    """A named style at the floor, in a class the twin holds fewer of (P4-D132)."""
    rungs = [
        "2024-03-02", "2024-03-05", "2024-03-20", "2024-04-10", "2024-05-01",
        "2024-05-15", "2024-05-31", "2024-06-20", "2024-07-02", "2024-07-20",
        "2024-07-30",
    ]
    column = _universal(
        "column_1", "datetime", "datetime", "data", "ok",
        n_present=60, n_missing=0, n_distinct=40, n_distinct_folded=40,
        n_numeric=0, n_not_numeric=60, n_out_of_range=0, n_contradictory=0,
        format="textual-day-first-date", resolution="date", time_precision="date",
        subsecond_digits=0, datetimes_read_at="local",
        earliest=rungs[0], latest=rungs[10],
        earliest_utc_offset="(none)", latest_utc_offset="(none)",
        date_percentiles=dict(zip(LADDER_KEYS, rungs)),
        n_unparsed=0, utc_offsets={"(none)": 60},
        month_name_styles={
            "title-abbreviated-space-no-comma": 11,
            "upper-abbreviated-hyphen-no-comma": 30,
            "upper-either-hyphen-no-comma": 19,
        },
    )
    return {
        "why": "the reservation of G7.5 (plan P4-D132): a form the census names "
        "at the floor keeps the floor in a twin whose own class of ranks is "
        "smaller than the real column's, where a proportional share falls "
        "under it. This case's mutant spends the class by the rotation alone.",
        "column": column,
        "rows": 60,
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



def _midnight_days():
    column = _universal(
        "column_1", "datetime", "datetime", "data", "ok",
        n_present=12, n_missing=0, n_distinct=12, n_distinct_folded=12,
        n_numeric=0, n_not_numeric=12, n_out_of_range=0, n_contradictory=0,
        format="iso-datetime", resolution="datetime", time_precision="second",
        subsecond_digits=0, datetimes_read_at="local",
        earliest="2024-01-08 00:00:00", latest="2024-12-16 00:00:00",
        earliest_utc_offset="(none)", latest_utc_offset="(none)",
        date_percentiles={
            "min": "2024-01-08 00:00:00", "p01": "2024-01-08 00:00:00",
            "p05": "2024-01-20 00:00:00", "p10": "2024-02-14 00:00:00",
            "p25": "2024-04-21 00:00:00", "p50": "2024-06-30 00:00:00",
            "p75": "2024-09-23 00:00:00", "p90": "2024-11-29 00:00:00",
            "p95": "2024-12-08 00:00:00", "p99": "2024-12-15 00:00:00",
            "max": "2024-12-16 00:00:00",
        },
        n_unparsed=0, utc_offsets={"(none)": 12},
        datetime_separators={"space": 12}, all_at_midnight=True,
    )
    return {
        "why": "the day-unit rule of plan P4-D39. Every moment of this column "
        "stands at midnight, which is how a warehouse holds a date with no "
        "time, so the ladder, both ends and the ten interior ranks are "
        "counted in whole days and each cell is written as its day with a "
        "midnight clock at the published precision, carrying the space the "
        "census names. Counted in seconds, as every column of moments was "
        "before this rule, the interior ranks land part-way through a day "
        "and the twin invents a time of day for each of them: that is the "
        "regression this case is frozen to stop, and its mutant is exactly "
        "that.",
        "column": column,
        "rows": 12,
        "identifier_declared": False,
    }


def _mixed_marks():
    column = _universal(
        "column_1", "datetime", "datetime", "data", "ok",
        n_present=24, n_missing=0, n_distinct=24, n_distinct_folded=24,
        n_numeric=0, n_not_numeric=24, n_out_of_range=0, n_contradictory=0,
        format="iso-datetime", resolution="datetime", time_precision="minute",
        subsecond_digits=0, datetimes_read_at="local",
        earliest="2024-05-01 06:30:00", latest="2024-05-28 21:45:00",
        earliest_utc_offset="(none)", latest_utc_offset="(none)",
        date_percentiles={
            "min": "2024-05-01 06:30:00", "p01": "2024-05-01 06:30:00",
            "p05": "2024-05-02 09:15:00", "p10": "2024-05-04 13:40:00",
            "p25": "2024-05-08 07:05:00", "p50": "2024-05-14 18:20:00",
            "p75": "2024-05-21 11:55:00", "p90": "2024-05-25 16:10:00",
            "p95": "2024-05-27 08:25:00", "p99": "2024-05-28 20:50:00",
            "max": "2024-05-28 21:45:00",
        },
        n_unparsed=0, utc_offsets={"(none)": 24},
        datetime_separators={"lower_t": 11, "space": 11, "(withheld)": 2},
        all_at_midnight=False,
    )
    return {
        "why": "the rotation of marks between day and clock of plan P4-D39. "
        "The census names two marks at eleven cells each and holds two more "
        "back, so it pins three rules at once: the named marks are spread "
        "evenly over the ranks rather than spent from the earliest rank "
        "upward, the earliest name in sorted order is the commonest on a "
        "tie, and since landing 2b.3 the withheld pool is written with the "
        "one mark the census leaves unnamed, a capital T. A "
        "walk that spent the names from the first rank upward would write "
        "every lower-case t on the earliest dates and every space on the "
        "latest, making up a link between how early a moment is and how it "
        "was spelled; this case's mutant is that walk.",
        "column": column,
        "rows": 24,
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
    ladder, ladder_claims, rungs, finer = _ladder_fields({
        "min": "-8", "p01": "-7.75", "p05": "-7", "p10": "-6.5",
        "p25": "-3.25", "p50": "2.5", "p75": "2.5", "p90": "16.25",
        "p95": "21.5", "p99": "29.75", "max": "34",
    })
    claims = {
        ("column",) + key: value
        for key, value in ladder_claims.items()
    }
    moments = {}
    for name, text in (("mean", "4.25"), ("std", "14.5"), ("skew", "0.5"),
                       ("kurtosis", "2.5"), ("numeric_share", "1")):
        field, claim = nearest_field(text)
        moments[name] = field
        claims[("column", name)] = claim
    column = _universal(
        "column_1", "continuous", "continuous", "data", "ok",
        n_present=20, n_missing=2, n_distinct=12, n_distinct_folded=12,
        n_numeric=20, n_not_numeric=0, n_out_of_range=0, n_contradictory=0,
        percentiles=ladder, percentiles_between=finer, std_unrepresentable=False,
        n_zero=4, n_negative=6, n_negative_unrepresentable=0,
        n_used_in_statistics=20, n_left_out_of_statistics=0,
        integer_valued=True, n_rows=22, numeric_styles={"plain": 20},
        # THE CENSUS OF WHOLE-NUMBER FIELD WIDTHS (contract 7.10).
        # Every one of this column's twenty cells is `plain`, so every
        # one of them is counted here and the total is twenty exactly
        # (invariant P9c).  The described source wrote sixteen of them
        # with a SINGLE figure and four with two: its ladder puts the
        # p75 rung at 2.5 and the p90 at 11, so three quarters of the
        # column is at or under 3 and the wide cells are the top of it.
        # Four is below the smallest group size, so that width has no
        # key and its cells are pooled -- which is why this case pins
        # the narrow width alone and leaves the twin the room the pool
        # gives it.  The case is not otherwise about widths.
        field_widths={"1": 16, "(withheld)": 4},
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
    ladder, ladder_claims, rungs, finer = _ladder_fields({
        "min": "0.5", "p01": "4", "p05": "4", "p10": "4",
        "p25": "4", "p50": "4", "p75": "4",
        "p90": "4", "p95": "4", "p99": "4",
        "max": "1e+20",
    })
    claims = {
        ("column",) + key: value
        for key, value in ladder_claims.items()
    }
    moments = {}
    for name, text in (("mean", "1e+19"), ("std", "3e+19"),
                       ("skew", "3"), ("kurtosis", "2.5"),
                       ("numeric_share", "1")):
        field, claim = nearest_field(text)
        moments[name] = field
        claims[("column", name)] = claim
    column = _universal(
        "column_1", "continuous", "continuous", "data", "ok",
        n_present=12, n_missing=0, n_distinct=3, n_distinct_folded=3,
        n_numeric=12, n_not_numeric=0, n_out_of_range=0, n_contradictory=0,
        percentiles=ladder, percentiles_between=finer, std_unrepresentable=False,
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
        # No cell of this case is padded, so the padded-field-width
        # census is empty and pins nothing.
        pad_widths={},
        # THE WHOLE-NUMBER FIELD-WIDTH CENSUS, WHOLLY POOLED (contract
        # 7.10).  Eleven cells are published `plain` and the twelfth is
        # the held-back one that carries a point, so this census counts
        # eleven -- P9c's two bounds being 11 and 12 here.  The
        # described source wrote those eleven at two widths, neither
        # shared by as many as eleven cells, so NEITHER is named and
        # the census is the pooled remainder alone.  It therefore pins
        # no width at all, which is right for a case about spellings.
        field_widths={"(withheld)": 11},
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
    ladder, ladder_claims, rungs, finer = _ladder_fields({
        "min": "1e-05", "p01": "0.0001", "p05": "0.001", "p10": "0.01",
        "p25": "1", "p50": "5", "p75": "1000000000000000",
        "p90": "1000000000000000", "p95": "1000000000000000",
        "p99": "1000000000000000", "max": "1e+16",
    })
    claims = {
        ("column",) + key: value
        for key, value in ladder_claims.items()
    }
    moments = {}
    for name, text in (("mean", "1000000000000"), ("std", "3000000000000"),
                       ("skew", "4.5"), ("kurtosis", "2.5"),
                       ("numeric_share", "1")):
        field, claim = nearest_field(text)
        moments[name] = field
        claims[("column", name)] = claim
    column = _universal(
        "column_1", "continuous", "continuous", "data", "ok",
        n_present=25, n_missing=0, n_distinct=24, n_distinct_folded=23,
        n_numeric=25, n_not_numeric=0, n_out_of_range=0, n_contradictory=0,
        percentiles=ladder, percentiles_between=finer, std_unrepresentable=False,
        n_zero=0, n_negative=0, n_negative_unrepresentable=0,
        n_used_in_statistics=25, n_left_out_of_statistics=0,
        integer_valued=False, n_rows=25,
        numeric_styles={"(withheld)": 3, "exponent_lower": 11,
                        "exponent_upper": 11},
        # THE WHOLE-NUMBER FIELD-WIDTH CENSUS (contract 7.10).  This
        # map names NO point-free form -- the three plain cells are the
        # held-back remainder -- so P9c bounds this census between
        # nought and three, and three cells cannot reach the smallest
        # group size at any width.  The census is the pooled remainder
        # alone and pins no width.
        field_widths={"(withheld)": 3},
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
            # `shape_form_cells` is how many of the level's rows wrote
            # the label in the LABEL'S OWN written form (contract
            # 7.4.8).  `north` and `south` are letters alone, and a form
            # carries two of the three kinds, so neither label has a
            # form and no spelling of either can wear one: both carry
            # nought, and W8 requires it.
            {
                "label": "north", "count": 13,
                "variants": {"North": 11}, "variants_withheld": {"1": 2},
                "shape_form_cells": 0,
            },
            {
                "label": "south", "count": 13,
                "variants": {}, "variants_withheld": {"1": 3, "5": 2},
                "shape_form_cells": 0,
            },
            # `7-11` wears `%-%%`, so one of its three held-back groups
            # of four rows CAN have been written in the label's own
            # shape -- and exactly one, because a label with no letters
            # has no case flip, so the only form-bearing spelling of it
            # is the label's own.  Four is therefore the largest number
            # a source of this shape could have written, and this case
            # takes it: it is what puts G8.1a's debt walk and G8.1's
            # spare-spelling offer on a label whose case-flip supply is
            # empty.
            {
                "label": "7-11", "count": 12,
                "variants": {}, "variants_withheld": {"4": 3},
                "shape_form_cells": 4,
            },
        ],
        suppressed_levels=2, suppressed_rows=10,
        level_ceiling=20,
        # The forms this column's cells were written in (P4-D18). The
        # published and made-up variants would cover 26 cells were the
        # labels shaped like codes; they are words, so the census here
        # is WRITTEN rather than derived, and it owes the two stand-ins
        # ten cells of `@@@-@`, which is exactly what their published
        # sizes cover -- so this case pins the shaped walk as well as
        # the variant allocation.
        shape_forms={"@@@-@": 36, "(withheld)": 12},
    )
    return {
        "why": "the variant allocation of G8.1, including the label's own "
        "spelling offered to the largest held-back group of every level its "
        "spellings already cover; the case flips of G8.2 with a candidate "
        "skipped because a published variant already spells it; the "
        "trailing-space family a parent with no letters falls straight "
        "through to; and the neutral stand-in labels of G8.3 at the "
        "sizes read off their pooled total (plan P4-D201), this column publishing no census of written forms. "
        "A label column consumes no content word, so every byte here is "
        "fixed by published counts.",
        "column": column,
        "rows": 50,
        "identifier_declared": False,
    }


def _long_tail_levels():
    """The FIRST frozen vector for any role Phase 4 added (R-P4-17).

    Every case in this oracle before it exercises a role Phase 1 to 3
    built. The four roles Phase 4 added -- `long_tail_labels`,
    `affixed_number`, `time_of_day` and `joined_numbers` -- had no
    independent vector at all, so their generator branches were checked
    only against themselves: a second implementer in another language
    had nothing to reproduce, and a defect written into the
    implementation would have been written into its own proof.

    THIS ROLE IS THE ONE THAT COSTS LEAST TO PROVE, and that is why it
    goes first rather than because it is the most interesting. Contract
    6.6 states that a long tail "adds no key of its own": it publishes
    the label roles' four keys and nothing else, and the generator
    dispatches on `LabelFacts`, which both label roles share. So the
    method this case pins is G8.1 to G8.4 exactly as `label_variants`
    pins it -- what is NEW is that the role reaches those sections at
    all, which nothing outside the implementation had said.

    The shape is a long tail's own: many levels, each covering few
    rows, with more held back than published. A categorical column of
    the same counts would have been refused the role by its ceiling,
    so this case cannot be mistaken for the one above it.
    """
    column = _universal(
        "column_1", "long_tail_labels", "long_tail_labels", "data", "ok",
        # EVERY LEVEL'S VARIANTS AND HELD-BACK GROUPS SUM TO ITS COUNT,
        # which is the arithmetic G8.1 is stated over: a level of five
        # rows whose own spelling is published twice owes three more
        # spellings, and `variants_withheld` counts them by GROUP SIZE
        # -- `{"1": 3}` is three groups of one row, not one group of
        # three.
        # WHAT MAKES THIS COLUMN A LONG TAIL AND NOT A SET OF
        # CATEGORIES (invariant LT2): it holds MORE folded identities
        # than the categorical ceiling of twenty. That is the whole
        # shape of the role, and the first four drafts of this case did
        # not have it -- they were categorical columns wearing the
        # name, and the loader said so.
        #
        # The floor these vectors are recorded at is ELEVEN, so a
        # PUBLISHED level covers eleven rows or more (invariant B5) and
        # a published VARIANT does too. With forty rows that leaves
        # room for exactly one published level; the other twenty cover
        # one or two rows each and are held back. One level named,
        # twenty suppressed -- which is what a long tail looks like
        # from the inside.
        n_present=40, n_missing=0, n_distinct=21, n_distinct_folded=21,
        n_numeric=0, n_not_numeric=40, n_out_of_range=0, n_contradictory=0,
        levels=[
            # `note alpha` holds a SPACE, so it has no written form at
            # all (C6-31a) and neither has any spelling of it: the level
            # carries nought, and W8 requires it.  The column's own
            # census beside it is a different fact and is not this
            # number's total -- residual R-P4-80's three reasons, of
            # which the first applies here: the twenty suppressed
            # levels' cells belong to no published level.
            {
                "label": "note alpha", "count": 11,
                "variants": {"Note Alpha": 11}, "variants_withheld": {},
                "shape_form_cells": 0,
            },
        ],
        suppressed_levels=20, suppressed_rows=29,
        # NO `level_ceiling`: contract 6.6 gives a long tail the four
        # SHARED label keys and not categorical's own fifth. Its
        # invariant -- folded distinctness at or under the ceiling --
        # is exactly what this role breaks by definition, so the
        # ceiling it passed is recorded in its evidence sentence
        # instead. Writing it here was the first thing the loader
        # refused, and rightly.
        # THE FORM CENSUS IS WHAT LETS THE STAND-INS BE WORDS (P4-D18).
        # Without it the twenty suppressed levels take the neutral
        # labels of G8.3, which carry a figure -- and a candidate that
        # could read back as a number or a date is one this file
        # refuses to reason about rather than reason around. The census
        # names a letters-and-hyphen form covering all twenty-nine
        # held-back rows, so every stand-in this case builds is a word.
        #
        # IT COVERS TWENTY-NINE OF FORTY CELLS AND NOT ALL FORTY, and
        # that is the census a profiler writes rather than a rounding
        # of it. The eleven published cells are spelled `Note Alpha`,
        # and a cell holding a SPACE has no form at all -- nor would it
        # if the space were closed up, because a form carries two of
        # the three kinds and letters alone are one. So those eleven
        # are not counted, not pooled, and above all not `(withheld)`:
        # that key means one thing in this format, a group too small to
        # name, and eleven cells at a floor of eleven are not that. An
        # earlier draft of this case wrote `"(withheld)": 11` here,
        # which no profiler could produce; the real one was measured on
        # a table of this exact shape and reads `{"@@@@-@@": 29}`.
        shape_forms={"@@@@-@@": 29},
    )
    return {
        "why": "the first frozen case for a role Phase 4 added, and the "
        "one that proves a long tail of labels reaches G8.1 to G8.4 at "
        "all. It carries far more rows in its held-back levels than in "
        "its published one -- twenty-nine against eleven -- which is "
        "the shape a long tail has and a column of categories cannot: "
        "its twenty-one folded identities stand above the ceiling of "
        "twenty this column passed, and that is the admission a rename "
        "to `categorical` could not survive. At a floor of eleven, "
        "forty rows leave room for exactly one published level; the "
        "other twenty cover one or two rows each and are held back. "
        "The case flips of G8.2 answer the one level carrying a "
        "published variant, and the twenty suppressed levels take the "
        "neutral stand-ins of G8.3 at the sizes read off their pooled total -- as "
        "words rather than as numbered labels, because the form census "
        "names a letters-and-hyphen form for all twenty-nine held-back "
        "rows. A label column consumes no content word, so every byte "
        "here is fixed by published counts. What this case does NOT "
        "prove is a generator branch of its own: a long tail is "
        "admitted by rules the categorical role would fail and is then "
        "written by the shared G8 machinery, so what is pinned here is "
        "admission and routing, and the cells are the label path's.",
        "column": column,
        "rows": 40,
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
    ladder, ladder_claims, rungs, finer = _ladder_fields({key: "5" for key in LADDER_KEYS})
    claims = {
        ("column",) + key: value
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
        percentiles=ladder, percentiles_between=finer, std_unrepresentable=False, skew=None,
        # No spread, so no tails to weigh: null, as the skewness is.
        kurtosis=None,
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
        # THE ONE CASE THAT PLACES A PADDED CELL. All eleven leading-zero
        # cells are `05`, two figures wide, and eleven is the smallest
        # group size -- so the census names the width rather than
        # pooling it. The value needs one figure and the field holds
        # two, so the one zero the style already wrote is the one the
        # width asks for and the committed bytes do not move (P4-D14).
        pad_widths={"2": 11},
        # THE WHOLE-NUMBER FIELD-WIDTH CENSUS, AND THE ONE CASE THAT
        # NAMES TWO WIDTHS (contract 7.10).  Twenty-two of the
        # thirty-three cells carry no point -- the eleven `leading_plus`
        # and the eleven `leading_zero` -- and the eleven `decimal`
        # cells are counted nowhere here.  The described source wrote
        # its plus-signed cells one figure wide and its padded cells
        # two, and eleven is the smallest group size, so both widths
        # are named rather than pooled.  Read against `pad_widths`
        # above, the pair asks G6.6 for eleven values of at most one
        # figure to carry the padding and eleven more of exactly one
        # figure for the rest: every value of this column is 5, so both
        # demands are met and no cell moves.
        field_widths={"1": 11, "2": 11},
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


def _count_spellings():
    ladder, ladder_claims, rungs, finer = _ladder_fields(
        {
            "min": "0", "p01": "0", "p05": "0", "p10": "0", "p25": "5.25",
            "p50": "7", "p75": "7", "p90": "7", "p95": "7", "p99": "7",
            "max": "7",
        }
    )
    claims = {("column",) + key: value for key, value in ladder_claims.items()}
    moments = {}
    for name, text in (
        ("mean", "5.25"),
        ("std", "3.066131567740966"),
        ("skew", "-1.1547005383792515"),
        ("kurtosis", "2.3333333333333335"),
        ("numeric_share", "1"),
    ):
        field, claim = nearest_field(text)
        moments[name] = field
        claims[("column", name)] = claim
    column = _universal(
        "column_1", "count", "count", "data", "ok",
        n_present=44, n_missing=0, n_distinct=4, n_distinct_folded=4,
        n_numeric=44, n_not_numeric=0, n_out_of_range=0, n_contradictory=0,
        percentiles=ladder, percentiles_between=finer,
        std_unrepresentable=False,
        n_zero=11, n_negative=0, n_negative_unrepresentable=0,
        n_used_in_statistics=44, n_left_out_of_statistics=0,
        integer_valued=True, n_rows=44, n_distinct_values=2,
        numeric_styles={"leading_zero": 22, "plain": 22},
        pad_widths={"2": 11, "3": 11},
        field_widths={"1": 22, "2": 11, "3": 11},
        # THE CENSUS OF SPELLINGS (contract 7.13, landing 2b.18 part 2).
        # Seven is written three ways and nought one, eleven cells each,
        # which is the smallest group size these vectors are recorded at:
        # every spelling clears it, so the census names all four.
        number_spellings={"0": 11, "007": 11, "07": 11, "7": 11},
        **moments,
    )
    return {
        "why": "a count column that wrote one number more than one way -- "
        "`7`, `07` and `007` beside `0` -- and so publishes the census of "
        "its spellings (contract section 7.13, method G6.8, landing 2b.18 "
        "part 2). Before the census a count published how many cells wore "
        "each field width and never which number wore which, and the twin "
        "of a column shaped like this one wrote `00` and `05`, spellings "
        "its source never had. The census names every cell read as a "
        "number, so it is the column's numbers: the forty-four cells here "
        "are its four spellings eleven times each, in the order of the "
        "number spelled and then of the spelling, and nothing is drawn "
        "for them. This case's mutant withdraws the rule, and the ladder "
        "walk of G5 and the style walk of G6 write the column instead: "
        "the cells move.",
        "column": column,
        "rows": 44,
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
        # THE TWO PUBLISHED WIDTHS OF REVISION 4 (P4-D4.4, closing
        # R-P2-1), and they are the widths a REAL column of these cells
        # would publish rather than any convenient pair. Three of this
        # column's six cells carry the contradictory construction of
        # G10.3, which is four characters long and which the producer
        # counts -- notation that conflicts with itself is numeric-
        # LOOKING even though it settles no value -- so the narrowest
        # numeric-looking cell here is four characters and the
        # description says four. Publishing a wider floor would freeze
        # a description no table could produce.
        min_length=4,
        max_length=400,
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


def _unrepresentable_exponent():
    column = _universal(
        "column_1", "numeric_unrepresentable", "numeric", "data",
        "unrepresentable",
        n_present=6, n_missing=0, n_distinct=4, n_distinct_folded=4,
        n_numeric=0, n_not_numeric=0, n_out_of_range=6, n_contradictory=0,
        n_whole=6, n_fraction=0, n_whole_unknown=0,
        n_positive=4, n_negative=2, n_sign_unknown=0,
        n_distinct_by_occurrences={"1": 2, "2": 2},
        # THE TWO WIDTHS A REAL COLUMN OF `1e400` PUBLISHES. Five
        # characters for a positive cell and six for a negative one,
        # which is the pair residual R-P4-68 was opened on: the
        # description was right and the twin was written three hundred
        # and ten characters wide, because the only spelling either
        # out-of-range shape had was a digit string.
        min_length=5,
        max_length=6,
    )
    return {
        "why": "G10.5 revision 5's EXPONENT SPELLING FAMILY, on the narrowest "
        "column that can reach it. Six cells over four groups, every one of "
        "them a whole number too large for binary64 to hold, published at "
        "five and six characters wide -- widths no digit string can be "
        "written at, because a whole numeral needs 310 figures to be certain "
        "of leaving the format's range. The exponent family says the same "
        "magnitude in five characters, so both published ends are carried: "
        "the first group whose shape and sign can be written at the floor "
        "takes it and the rest take the ceiling. It also pins the walk's "
        "bookkeeping, which revision 5 had to state before this case could "
        "be frozen: each shape-and-sign pair walks each family from that "
        "family's own start, so the positive and the negative groups both "
        "begin at that shape's first spelling. No frozen case carried a "
        "positive and a negative group of one shape before this one, which "
        "is why two implementations could count differently and agree on "
        "every committed byte.",
        "column": column,
        "rows": 6,
        "identifier_declared": False,
    }


def _free_text_joint():
    length, length_claims = {}, {}
    # THE DOUBLED NUMBER IS ONE FIGURE LONG (G9.5 step 3a, landing 2b.4):
    # a number carrying no published end takes the shortest length its
    # band has a number without a leading zero at, so the column this
    # case describes is `A`, `!!`, `0`, `0` -- average 1.25, middle 1 --
    # and the packing it pins is exactly the one it pinned before.
    for name, text in (("mean", "1.25"), ("p50", "1")):
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
        # The census of written forms (plan P4-D18). Four cells at the
        # smallest group size of eleven: no form is shared by enough of
        # them to be named, so the whole census is the pooled
        # remainder.
        shape_forms={"(withheld)": 4},
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


def _date_widths_reached():
    """A month-first column whose cells showing a width are counted (P4-D192).

    Eighty dates over a year leaning into its last quarter, where a day
    past the ninth of October, November or December shows no width. The
    census names one convention, `unpadded`, on forty-four cells, so the
    twin's cells showing a width must be forty-four: each gap's ranks move
    a whole day at a time to the nearest day of the other kind, nearest
    first, until they are.
    """
    rungs = [
        "2024-01-03", "2024-02-20", "2024-04-11", "2024-06-01", "2024-09-28",
        "2024-10-08", "2024-10-21", "2024-11-06", "2024-11-25", "2024-12-14",
        "2024-12-30",
    ]
    column = _universal(
        "column_1", "datetime", "datetime", "data", "ok",
        n_present=80, n_missing=0, n_distinct=60, n_distinct_folded=60,
        n_numeric=0, n_not_numeric=80, n_out_of_range=0, n_contradictory=0,
        format="month-first-date", resolution="date", time_precision="date",
        subsecond_digits=0, datetimes_read_at="local",
        earliest=rungs[0], latest=rungs[10],
        earliest_utc_offset="(none)", latest_utc_offset="(none)",
        date_percentiles=dict(zip(LADDER_KEYS, rungs)),
        n_unparsed=0, utc_offsets={"(none)": 80},
        date_field_widths={"unpadded": 44},
    )
    return {
        "why": "the widths count of G7.3's count passes (plan P4-D192): a "
        "census naming one convention is worn by every cell showing a width, "
        "so the twin holds as many dates whose day shows one as the census "
        "counts, moving ranks whole days inside their gaps. Drawn alone, the "
        "ranks put a different number of dates in the last quarter's days past "
        "the ninth, and that is this case's mutant.",
        "column": column,
        "rows": 80,
        "identifier_declared": False,
    }


def _date_distinct_reached():
    """A month of dates holding fewer different days than its ranks (P4-D192).

    Sixty ISO dates over thirty days publishing twelve different days, one
    more than the eleven the pins hold: runs of ranks on one day move whole
    onto a neighbouring rank's day, nearest first, until twelve are held.
    """
    rungs = [
        "2024-03-01", "2024-03-02", "2024-03-04", "2024-03-07", "2024-03-10",
        "2024-03-15", "2024-03-18", "2024-03-22", "2024-03-26", "2024-03-28",
        "2024-03-30",
    ]
    column = _universal(
        "column_1", "datetime", "datetime", "data", "ok",
        n_present=60, n_missing=0, n_distinct=12, n_distinct_folded=12,
        n_numeric=0, n_not_numeric=60, n_out_of_range=0, n_contradictory=0,
        format="iso-date", resolution="date", time_precision="date",
        subsecond_digits=0, datetimes_read_at="local",
        earliest=rungs[0], latest=rungs[10],
        earliest_utc_offset="(none)", latest_utc_offset="(none)",
        date_percentiles=dict(zip(LADDER_KEYS, rungs)),
        n_unparsed=0, utc_offsets={"(none)": 60},
    )
    return {
        "why": "the count of different values of G7.3's count passes (plan "
        "P4-D192): one instant written one way, so the different days the twin "
        "holds must be the published twelve, reached by moving runs of ranks on "
        "one day whole onto a neighbour's inside their gaps. Drawn alone, the "
        "ranks spread over more days, and that is this case's mutant.",
        "column": column,
        "rows": 60,
        "identifier_declared": False,
    }


def _midnight_withheld_kept():
    """Moments to the minute whose count at midnight was withheld (P4-D191).

    Sixty moments over twelve days whose pins stand a minute before and a
    minute after midnight in turn, so the ranks drawn between a `23:59` and
    the next day's `00:01` land in the minute of midnight about half the
    time. The description publishes no `n_at_midnight`, and its pins stand
    off midnight, so fewer than the line of eleven may stand there: the
    ranks written at midnight step a minute later, in rank order, until
    fewer do.
    """
    rungs = []
    for index in range(11):
        clock = "23:59:00" if index % 2 == 0 else "00:01:00"
        rungs += [f"2024-03-{1 + index:02d} {clock}"]
    column = _universal(
        "column_1", "datetime", "datetime", "data", "ok",
        n_present=60, n_missing=0, n_distinct=60, n_distinct_folded=60,
        n_numeric=0, n_not_numeric=60, n_out_of_range=0, n_contradictory=0,
        format="iso-datetime", resolution="datetime", time_precision="minute",
        subsecond_digits=0, datetimes_read_at="local",
        earliest=rungs[0], latest=rungs[10],
        earliest_utc_offset="(none)", latest_utc_offset="(none)",
        date_percentiles=dict(zip(LADDER_KEYS, rungs)),
        n_unparsed=0, utc_offsets={"(none)": 60},
        resolution_mix={"iso-datetime": 60},
        datetime_separators={"space": 60},
        all_at_midnight=False, n_at_midnight=None,
    )
    return {
        "why": "G7.3's rule for a count at midnight the description withholds "
        "(plan P4-D191): withheld because too few stood on one side, so the "
        "twin keeps fewer than the line on the side its published instants "
        "stand on. Left where they were drawn, a dozen or more ranks stand in "
        "the minute of midnight -- a count the description would publish -- "
        "and that is this case's mutant.",
        "column": column,
        "rows": 60,
        "identifier_declared": False,
    }


def _pooled_level_sizes():
    """Method G8.3's sizes read off a pooled total (plan P4-D201).

    Owner ruling of 2026-09-17, item 2, option A: a label column publishes
    how many labels the floor held back and the rows they covered
    together, and no size of any one of them.  Five labels on twenty-one
    rows at a floor of eleven, all owed to the one form the census names,
    take the three labels that pay twenty-one below the floor and then two
    more, one to a cell at most, and the rows are shared one each and the
    rest by the square of each label's place: `1, 2, 4, 6, 8`.
    """
    column = _universal(
        "column_1", "categorical", "categorical", "data", "ok",
        n_present=54, n_missing=0, n_distinct=7, n_distinct_folded=7,
        n_numeric=0, n_not_numeric=54, n_out_of_range=0, n_contradictory=0,
        levels=[
            # Letters alone carry no written form (a form carries two of
            # the three kinds), so both levels carry nought, as W8 asks.
            {
                "label": "alpha", "count": 22,
                "variants": {"Alpha": 22}, "variants_withheld": {},
                "shape_form_cells": 0,
            },
            {
                "label": "beta", "count": 11,
                "variants": {"beta": 11}, "variants_withheld": {},
                "shape_form_cells": 0,
            },
        ],
        suppressed_levels=5, suppressed_rows=21, level_ceiling=20,
        # The held-back cells wore one form of letters and a hyphen, so the
        # stand-ins are words of that form and no figure reaches them.
        shape_forms={"@@@@-@@": 21},
    )
    return {
        "why": "the sizes of the held-back labels read off their pooled total "
        "(method G8.3, plan P4-D201, owner ruling of 2026-09-17): five labels "
        "on twenty-one rows at a floor of eleven, one row each and the rest "
        "shared by the square of each label's place, so the stand-ins, "
        "written in the one form the census names, cover 1, 2, 4, 6 and 8 "
        "rows. "
        "Its mutant shares the pool out evenly, 4, 4, 4, 4 and 5, and the "
        "stand-ins' rows move. A label column consumes no content word.",
        "column": column,
        "rows": 54,
        "identifier_declared": False,
    }


def _numbers_carry_the_average():
    """What the walk could not spend goes to the numbers (plan P4-D190).

    Ten cells of free text: eight numbers and two words. The two words
    carry the published ends -- `A` at one character and `A--` at three --
    so no group the ordinary walk of G9.5 step 5 may move is left, and
    every number stands at its own shortest length, one figure. The
    column's cells average two characters, which those lengths miss by
    eight: the walk used to stop there, the recount found an average of
    six fifths, and the twin missed `length.mean`. The numbers are walked
    instead, largest group first and one character at a time, so four of
    them grow to three figures -- `100` to `103` -- and the average is met
    exactly, with the middle length two.
    """
    length, claims = {}, {}
    for name, text in (("mean", "2.0"), ("p50", "2")):
        field, claim = nearest_field(text)
        length[name] = field
        claims[("column", "length", name)] = claim
    length["min"] = 1
    length["max"] = 3
    words = {"min": 1, "max": 1}
    field, claim = nearest_field("1")
    words["mean"] = field
    claims[("column", "words", "mean")] = claim
    column = _universal(
        "column_1", "free_text", "text", "data", "ok",
        n_present=10, n_missing=0, n_distinct=10, n_distinct_folded=10,
        n_numeric=8, n_not_numeric=2, n_out_of_range=0, n_contradictory=0,
        length=length, words=words,
        n_all_digits=8, n_code_alphabet=10,
        n_distinct_by_occurrences={"1": 10},
        # Ten cells at the smallest group of eleven: no form is named.
        shape_forms={"(withheld)": 10},
    )
    return {
        "why": "method section G9.5 step 5 as plan P4-D190 left it: a column "
        "of eight numbers and two words whose words carry both published "
        "length ends, so the ordinary walk has no group to move and the "
        "numbers, each at its own shortest length, carry what is left of the "
        "published average. Without that walk the cells average six fifths "
        "against two, and the description's own length.mean is missed.",
        "column": column,
        "rows": 10,
        "identifier_declared": False,
        "claims": claims,
    }


def _label_numbers():
    """The class debt of a column of labels (method G8.3a, landing 2b.4).

    Every label case before this one publishes no number at all, so the
    rule that writes a held-back number AS a number could be withdrawn
    with every committed byte unchanged -- and until landing 2b.4 the
    method had no such rule: a column of readings beside two labels had
    its held-back readings written as words, and at a floor of twenty a
    column of 853 readings kept 359 of them.

    Forty-four rows at a floor of eleven. One published label, `ab-cd`,
    on twelve rows; two published readings, `5.1` and `5.3`, on eleven
    each; and four held-back levels of one, two, three and four rows,
    which the source it stands for wrote `xy-zw`, `12.5`, `5.0` and
    `5.2`. The published spellings pay twenty-two of the thirty-one
    numbers, so the held-back levels owe nine; the census names `%.%`
    on twenty-nine cells and `@@-@@` on thirteen, and pools the two
    cells of `12.5` under the withheld key.

    SINCE THE OWNER'S RULING OF 2026-09-17 (plan P4-D201) the description
    publishes those four levels as a pool of ten rows and no size of any
    one, and G8.3 reads the sizes off the pool and its debts: nine
    numbers, seven of them `%.%`, and one word, written `1, 2, 2, 5`.
    What each rule of G8.3a does here, in order:

    - the class split: nine is `5 + 2 + 2`, read off the reachable sums
      largest first, so the level of one row stays a word;
    - the forms inside the number class: `%.%` still owes seven, which
      is `5 + 2`, so one level of two wears no named form;
    - the gap: `5.2` is the one value strictly between the published
      numbers that no published number holds, and the largest level
      takes it; the next takes the first outward step, `5.0`;
    - a number wearing no named form: every value of one figure, a point
      and a figure wears `%.%`, which the census names, so the level of
      two wearing none walks the ladder up to `10.0`;
    - the word: `@@-@@` owes one cell, and the level of one row takes
      that form's first spelling, `AA-AA`.
    """
    column = _universal(
        "column_1", "categorical", "categorical", "data", "ok",
        n_present=44, n_missing=0, n_distinct=7, n_distinct_folded=7,
        n_numeric=31, n_not_numeric=13, n_out_of_range=0, n_contradictory=0,
        levels=[
            {
                "label": "ab-cd", "count": 12,
                "variants": {"ab-cd": 12}, "variants_withheld": {},
                "shape_form_cells": 12,
            },
            {
                "label": "5.1", "count": 11,
                "variants": {"5.1": 11}, "variants_withheld": {},
                "shape_form_cells": 11,
            },
            {
                "label": "5.3", "count": 11,
                "variants": {"5.3": 11}, "variants_withheld": {},
                "shape_form_cells": 11,
            },
        ],
        suppressed_levels=4, suppressed_rows=10,
        level_ceiling=20,
        shape_forms={"%.%": 29, "@@-@@": 13, "(withheld)": 2},
    )
    return {
        "why": "the class debt of G8.3a: a held-back level that was a number "
        "is written as a number. The published spellings pay twenty-two of "
        "the thirty-one numbers; the four held-back levels, published as a "
        "pool of ten rows (plan P4-D201), owe nine, and the sizes G8.3 reads "
        "off the pool and its debts, one, two, two and five, make nine as "
        "five, two and two, so the level of one row stays a word. Inside the "
        "number class `%.%` still owes seven, which five and two make, so "
        "one level of two wears no named form. The "
        "numbers come from the published ones: the one value strictly "
        "between them that none holds, `5.2`, goes to the largest level, "
        "the first step outward, `5.0`, to the next, and the level wearing "
        "no named form walks past every value `%.%` writes to `10.0`. The "
        "word takes the first spelling of `@@-@@`. A label column consumes "
        "no content word, so every byte here is fixed by published counts.",
        "column": column,
        "rows": 44,
        "identifier_declared": False,
    }



def _label_number_tiers():
    """What the census could hold, and the places a number may take (G8.3a).

    Landing 2b.4's repair. Fifty-five rows at a floor of eleven: one
    published label, `ab-cd`, on twelve rows; two published readings,
    `5.1` and `5.3`, and one published whole number, `7`, on eleven
    each; and four held-back levels of one, two, three and four rows,
    which the source it stands for wrote `xy-zw`, `6`, `5.0` and `5.2`.
    The census names `%.%` on twenty-nine cells and `@@-@@` on thirteen
    and pools nothing: the whole numbers wear no form. Since the owner's
    ruling of 2026-09-17 (plan P4-D201) the four levels are published as a
    pool of ten rows, and G8.3 reads their sizes off it and its debts:
    `1, 2, 2, 5`.

    - the class split: the published spellings pay thirty-three of the
      forty-two numbers, and nine is `5 + 2 + 2`;
    - the forms inside the number class: `%.%` owes seven, `5 + 2`, and
      they take the gaps nearest each end, `5.2` and `6.9`;
    - the other level of two wears no named form. At one place every value it
      could step to wears `%.%`, which the census names, until `10.0`,
      which wears `%%.%`: a form with room for a thousand cells, which
      the census would have counted and pooled -- and it pools nothing,
      so that side ENDS rather than write it. The walk then takes the
      next count of places a published number was written with, none,
      and writes the gap between `5` and `7`: `6`;
    - the word: `@@-@@` owes one cell, `AA-AA`.
    """
    column = _universal(
        "column_1", "categorical", "categorical", "data", "ok",
        n_present=55, n_missing=0, n_distinct=8, n_distinct_folded=8,
        n_numeric=42, n_not_numeric=13, n_out_of_range=0, n_contradictory=0,
        levels=[
            {
                "label": "ab-cd", "count": 12,
                "variants": {"ab-cd": 12}, "variants_withheld": {},
                "shape_form_cells": 12,
            },
            {
                "label": "5.1", "count": 11,
                "variants": {"5.1": 11}, "variants_withheld": {},
                "shape_form_cells": 11,
            },
            {
                "label": "5.3", "count": 11,
                "variants": {"5.3": 11}, "variants_withheld": {},
                "shape_form_cells": 11,
            },
            {
                "label": "7", "count": 11,
                "variants": {"7": 11}, "variants_withheld": {},
                "shape_form_cells": 0,
            },
        ],
        suppressed_levels=4, suppressed_rows=10,
        level_ceiling=20,
        shape_forms={"%.%": 29, "@@-@@": 13},
    )
    return {
        "why": "what the census could hold, and the places a number wearing no "
        "named form may take (G8.3a, landing 2b.4's repair). The held-back "
        "levels, a pool of ten rows whose sizes G8.3 reads as `1, 2, 2, 5` "
        "(plan P4-D201), owe nine numbers, `5 + 2 + 2`, and `%.%` owes seven "
        "of them, `5 + 2`, which take the gaps `5.2` and `6.9`. The other "
        "level of two wears "
        "no named form: every one-place value it could step to wears the "
        "named `%.%` until `10.0`, whose form the census would have counted "
        "and pooled, and it pools nothing, so that side ends. The walk then "
        "takes the other count of places the published numbers were written "
        "with, none, and writes the gap `6`. The word takes `AA-AA`.",
        "column": column,
        "rows": 55,
        "identifier_declared": False,
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


def _identifier_layout():
    column = _universal(
        "column_1", "identifier", "code", "identifier", "ok",
        n_present=24, n_missing=0, n_distinct=18, n_distinct_folded=18,
        n_numeric=0, n_not_numeric=24, n_out_of_range=0, n_contradictory=0,
        min_length=6, max_length=6, all_whole_numbers=False,
        n_all_digits=0, n_code_alphabet=24,
        n_distinct_by_occurrences={"1": 12, "2": 6},
        layout_forms={"@%%%%%": 12, "@@%%%%": 12},
    )
    return {
        "why": "a declared identifier that publishes a census of LAYOUTS "
        "(contract section 7.12, landing 2b.18), which every case frozen "
        "before it publishes empty. The census says what KIND of character "
        "stood at each position and never which one, and G9.6 writes each "
        "cell to it: the twenty-four cells here wear `@%%%%%` twelve times "
        "and `@@%%%%` twelve times instead of the band enumeration's own "
        "spellings. Without this case the whole layout rule could be "
        "withdrawn with every committed byte unchanged, because the three "
        "identifier cases beside it publish no layout at all. TWO RULES ARE "
        "FROZEN HERE. The fill is a COUNTER taken apart LEFTMOST FIRST, so "
        "consecutive cells of one layout differ in their leading characters "
        "rather than their trailing ones, which is what stops a column of "
        "record numbers coming out as a near-consecutive walk. And the "
        "census is SPREAD over the identities by the smooth weighted "
        "rotation, largest group first, rather than poured into them in "
        "walk order: twelve values are written once and six twice, and a "
        "walk taking the first layout with room left gives every singleton "
        "`@%%%%%` and every repeated value `@@%%%%`, binding a layout to how "
        "often its record numbers recur. This case's mutant withdraws the "
        "preference, and the cells move. Every other published fact "
        "survives the offer and is recounted from the finished cells: the "
        "two alphabet counts and the four class counts, because a candidate "
        "the readers do not recount into its slot's band is stepped over, "
        "and both length ends, because a layout is one mark per character. "
        "Withdrawing the offer altogether stops this oracle before any byte "
        "is written, because the recount of 7.12 then finds each layout "
        "worn nought times.",
        "column": column,
        "rows": 24,
        "identifier_declared": True,
    }


def _identifier_layout_mixes():
    column = _universal(
        "column_1", "identifier", "code", "identifier", "ok",
        n_present=47, n_missing=0, n_distinct=47, n_distinct_folded=47,
        n_numeric=11, n_not_numeric=36, n_out_of_range=0, n_contradictory=0,
        min_length=9, max_length=9, all_whole_numbers=False,
        n_all_digits=11, n_code_alphabet=36,
        n_distinct_by_occurrences={"1": 47},
        layout_forms={
            "!!%%%%%%%": 11, "@%-------": 11, "@@%% %%%%": 11, "(withheld)": 14,
        },
    )
    return {
        "why": "a declared identifier whose census of LAYOUTS names a zero "
        "fill two noughts deep, a layout holding a single interior SPACE, "
        "and a pool of fourteen cells no named layout serves (contract "
        "section 7.12, plans P4-D126, P4-D127 and P4-D128). THREE RULES OF "
        "G9.6 ARE FROZEN HERE. A zero-filled layout writes a nought for "
        "every `!` and steps over a filling whose next figure is a nought, "
        "because that cell recounts one nought deeper. A space stands in a "
        "layout as a mark does. And the fourteen pooled cells, which every "
        "case before this one wrote by the band enumeration, are written to "
        "MIXES of the kinds the census names -- figures and capitals over "
        "the two places of `@%-------`, the first base in sorted order -- and "
        "of its four mixes the one the census names, `@%-------` itself, is "
        "stepped over, so no pooled cell is counted into a published layout. Every layout "
        "is walked from step one, and a step is spread by the exact golden "
        "section of the layout's room. NINE characters wide, because G9.6's bar "
        "on a filling that reads as a date is not carried by this oracle, "
        "which reads no date, and no date format this package reads is nine "
        "figures or four and four around a space: at eight, `00330816` reads "
        "as the compact date 0033-08-16 and is stepped over. This case's mutant withdraws the "
        "mixes, and the fourteen cells move; withdrawing the fill or the "
        "space stops this oracle at the recount of 7.12.",
        "column": column,
        "rows": 47,
        "identifier_declared": True,
    }


def _identifier_absent_words():
    column = _universal(
        "column_1", "identifier", "code", "identifier", "ok",
        n_present=20, n_missing=0, n_distinct=20, n_distinct_folded=20,
        n_numeric=0, n_not_numeric=20, n_out_of_range=0, n_contradictory=0,
        min_length=2, max_length=2, all_whole_numbers=False,
        n_all_digits=0, n_code_alphabet=20,
        n_distinct_by_occurrences={"1": 20},
        layout_forms={"@@": 20},
    )
    return {
        "why": "a declared identifier publishing `{\"@@\": 20}`, whose layout "
        "walk reaches `NA` at its thirteenth filling (G9.6, plan P4-D158). A "
        "record number is never written in a spelling a reader reads as "
        "absent, so `NA` is stepped over and the walk takes `VY` after `UI`; "
        "presence is recounted as a reader counts it, so a construction that "
        "wrote `NA` would recount nineteen present cells. This case's mutant "
        "withdraws the reading of absence, `NA` is written, and the cells "
        "move.",
        "column": column,
        "rows": 20,
        "identifier_declared": True,
    }


def _identifier_signed_layout():
    column = _universal(
        "column_1", "identifier", "code", "identifier", "ok",
        n_present=12, n_missing=0, n_distinct=12, n_distinct_folded=12,
        n_numeric=12, n_not_numeric=0, n_out_of_range=0, n_contradictory=0,
        min_length=5, max_length=5, all_whole_numbers=True,
        n_all_digits=0, n_code_alphabet=12,
        n_distinct_by_occurrences={"1": 12},
        layout_forms={"-%%%%": 12},
    )
    return {
        "why": "a declared identifier of signed whole numbers publishing "
        "`{\"-%%%%\": 12}` (G9.6, plan P4-D156). A layout that is a sign "
        "before figures is worn by signed numbers alone, so the census proves "
        "the table held them and the opening sign is not refused as a "
        "formula: every cell is a minus and four figures. This case's mutant "
        "refuses the sign, no filling of the layout is written, and the "
        "check of 7.12 stops the oracle.",
        "column": column,
        "rows": 12,
        "identifier_declared": True,
    }


def _identifier_column_prefix():
    column = _universal(
        "column_1", "identifier", "code", "identifier", "ok",
        n_present=24, n_missing=0, n_distinct=18, n_distinct_folded=18,
        n_numeric=0, n_not_numeric=24, n_out_of_range=0, n_contradictory=0,
        min_length=7, max_length=7, all_whole_numbers=False,
        n_all_digits=0, n_code_alphabet=24,
        n_distinct_by_occurrences={"1": 12, "2": 6},
        layout_forms={"@@@%%%%": 24},
        layout_prefixes={"(column)": "REC"},
    )
    return {
        "why": "a declared identifier every present cell of which opens with "
        "the literal prefix `REC` (contract section 7.12a, owner ruling of "
        "2026-09-17, item 1). G9.6a writes a prefixed layout as its TEMPLATE, "
        "`REC%%%%`: the prefix stands in every cell and only the four figures "
        "are filled from the step, so the room is ten thousand and the "
        "eighteen identities stay different. This case's mutant withdraws "
        "the templates, the three letters are filled from the step as the "
        "layout's own marks, and the cells move.",
        "column": column,
        "rows": 24,
        "identifier_declared": True,
    }


def _identifier_layout_prefixes():
    column = _universal(
        "column_1", "identifier", "code", "identifier", "ok",
        n_present=24, n_missing=0, n_distinct=24, n_distinct_folded=24,
        n_numeric=0, n_not_numeric=24, n_out_of_range=0, n_contradictory=0,
        min_length=6, max_length=6, all_whole_numbers=False,
        n_all_digits=0, n_code_alphabet=24,
        n_distinct_by_occurrences={"1": 24},
        layout_forms={"@%%%%%": 12, "@@%%%%": 12},
        layout_prefixes={"@%%%%%": "E", "@@%%%%": "ST"},
    )
    return {
        "why": "a declared identifier holding two layouts, each publishing a "
        "prefix of its own, `E` before five figures and `ST` before four "
        "(contract section 7.12a; the per-layout reading of the owner's "
        "ruling of 2026-09-17, item 1). Each layout is written as its own "
        "template, so the smooth weighted rotation spreads `E%%%%%` and "
        "`ST%%%%` over the identities exactly as it spread the layouts, and "
        "every cell of a layout opens with that layout's prefix. This case's "
        "mutant withdraws the templates, and the cells move.",
        "column": column,
        "rows": 24,
        "identifier_declared": True,
    }


def _identifier_layout_partners():
    column = _universal(
        "column_1", "identifier", "code", "identifier", "ok",
        n_present=33, n_missing=0, n_distinct=33, n_distinct_folded=22,
        n_numeric=0, n_not_numeric=33, n_out_of_range=0, n_contradictory=0,
        min_length=3, max_length=3, all_whole_numbers=False,
        n_all_digits=0, n_code_alphabet=33,
        n_distinct_by_occurrences={"1": 33},
        layout_forms={"&%%": 11, "@%%": 22},
    )
    return {
        "why": "a declared identifier whose eleven fold-collision partners "
        "wear a published layout (G9.6, plan P4-D157), `{\"@%%\": 22, "
        "\"&%%\": 11}` over twenty-two identities. An identity owed a "
        "partner is visited first and takes a layout only where its "
        "partner's layout, its letter turned over, has a cell left, and both "
        "are debited together; the partner takes the member wearing a layout "
        "with a cell left. This case's mutant withdraws the partners' "
        "layouts, the identities take the census, the partners turn them "
        "over, and the check of 7.12 stops the oracle.",
        "column": column,
        "rows": 33,
        "identifier_declared": True,
    }


def _lower_case_stand_ins():
    column = _universal(
        "column_1", "categorical", "categorical", "data", "ok",
        n_present=51, n_missing=0, n_distinct=22, n_distinct_folded=22,
        n_numeric=0, n_not_numeric=51, n_out_of_range=0, n_contradictory=0,
        levels=[
            # `note alpha` holds a space and has no form; `ab-cd` has the
            # form `@@-@@` and every cell of it is lower case, so it settles
            # the census's lower-case key `&&-&&` in full -- and a walk
            # reading it blind to case would find that key unpaid.
            {
                "label": "ab-cd", "count": 11,
                "variants": {"ab-cd": 11}, "variants_withheld": {},
                "shape_form_cells": 11,
            },
            {
                "label": "note alpha", "count": 11,
                "variants": {"note alpha": 11}, "variants_withheld": {},
                "shape_form_cells": 0,
            },
        ],
        suppressed_levels=20, suppressed_rows=29,
        # Fifty-one rows give a ceiling of twenty-five and twenty-two
        # values stand under it, so this column is a set of categories;
        # the census and the stand-in walk are the four label roles' own.
        level_ceiling=25,
        # THE LOWER-CASE KEYS (contract C6-31a, landing 2b.18 part 2).
        # Every formed cell wrote every letter lower case, so the census
        # names each form with `&` in each letter place, and the column's
        # twenty-two values fold to twenty-two, which SF5 asks.
        shape_forms={"&&&&-&&": 29, "&&-&&": 11},
    )
    return {
        "why": "a column of categories whose census names LOWER-CASE keys (contract "
        "C6-31a, landing 2b.18 part 2): every formed cell wrote every letter "
        "in lower case, so the census names `&&&&-&&` and `&&-&&` and not "
        "their capital forms. The published level `ab-cd` settles `&&-&&` in "
        "full, counted under the key the census files it under, so the "
        "twenty stand-ins owe `&&&&-&&` alone -- twenty-nine cells, exactly "
        "their sizes -- and G8.3 fills each `&` from the lower-case alphabet "
        "at the position and by the arithmetic a `@` is filled. Before this "
        "key existed a column of lower-case codes came back in capitals on "
        "every stand-in and a case-sensitive pattern matched none of them. "
        "This case's mutant fills the key in capitals, and every stand-in "
        "moves; a walk reading the published level blind to case hands "
        "`&&-&&` stand-ins it does not owe, and the cells move too.",
        "column": column,
        "rows": 51,
        "identifier_declared": False,
    }


def _level_shape_stand_ins():
    column = _universal(
        "column_1", "long_tail_labels", "long_tail_labels", "data", "ok",
        n_present=LEVEL_SHAPE_ROWS, n_missing=0,
        n_distinct=1 + len(LEVEL_SHAPE_SIZES),
        n_distinct_folded=1 + len(LEVEL_SHAPE_SIZES),
        n_numeric=0, n_not_numeric=LEVEL_SHAPE_ROWS, n_out_of_range=0,
        n_contradictory=0,
        levels=[
            {
                "label": "a-", "count": 11,
                "variants": {"a-": 11}, "variants_withheld": {},
                "shape_form_cells": 11,
            },
        ],
        suppressed_levels=len(LEVEL_SHAPE_SIZES),
        suppressed_rows=sum(LEVEL_SHAPE_SIZES),
        # THE CENSUS NAMES ONE FORM AND NOT THE SHAPE THE PUBLISHED LEVEL
        # WEARS. `a-` has fifty-two spellings to a profiler, fewer than the
        # column's different values and the floor, so the small-supply rule
        # of C6-31 names no key for it -- the shape of the carried column of
        # landing 2b.12, `4-F`, in letters alone.
        shape_forms={"@@@@-@@": LEVEL_SHAPE_DEBT},
    )
    return {
        "why": "the shape a held-back label takes where the census owes it "
        "no form (method G8.3b, landing 2b.18 part 2, the carried item of "
        "landing 2b.12). The column publishes one level, `a-`, whose shape "
        "no census key names because it has too few spellings; before "
        "this rule every stand-in the census owed nothing was `group-N`, "
        "and on the carried column that made the twin's mean cell length "
        "9.907 against the real 7.204. The stand-ins owed no form are "
        "written in the level's own shape with its case kept, `&-`, whose "
        "supply here is twenty-five spellings against more places owed "
        "nothing -- so the TRADE of G8.3b is frozen too: a large held-back "
        "group paying `@@@@-@@` trades places with single rows summing to "
        "it exactly, the named form keeps its count, and the shape covers "
        "every row it can. This case's mutant withdraws the trade, and a "
        "place past the shape's supply takes the neutral spelling, which "
        "this oracle refuses to reason about.",
        "column": column,
        "rows": LEVEL_SHAPE_ROWS,
        "identifier_declared": False,
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
# The third file: the cases the carried landings 2b.2, 2b.3 and 2b.4 added,
# which with the second file's own would pass the provenance byte cap.
SECOND_BRANCH_PART = "branches-2"
# The fifth file: the cases the repair of the final Codex review of the
# number censuses added (plans P4-D142, P4-D145 and its amendment, P4-D147
# and P4-D149), which the
# second and third files, each within a few kilobytes of the provenance
# byte cap, could not hold.
THIRD_BRANCH_PART = "branches-3"
# The sixth file: the cases the reconciliation of G6.5a's walk (plan
# P4-D183), the fills of plans P4-D176 and P4-D178 and the census of marks
# at a thousand (plan P4-D185) added, which the fifth could not hold.
FOURTH_BRANCH_PART = "branches-4"
# The seventh file: the cases of a whole number written two ways (plan
# P4-D193), which the sixth, within a few kilobytes of the byte cap, could
# not hold.
FIFTH_BRANCH_PART = "branches-5"

NAMED_CASE_BUILDERS = {
    "date_only": _date_only,
    # THE FOUR CASES OF THE REVIEW OF 158c811 (plans P4-D130, P4-D132 and
    # P4-D133). No frozen case in any of the three files published a
    # non-empty census of written forms, so every allocation of G7.5 could
    # have been withdrawn with every committed byte unchanged, and G7.3's
    # places were pinned by none. They go in this file, which has the room.
    # AND TWO MORE FROM ITS SKEPTIC (plan P4-D138): G7.3's choice of the
    # middles and its heaps, each with its own mutant.
    "date_gap_places": _date_gap_places,
    "date_peak_heap": _date_peak_heap,
    "date_thinning_week": _date_thinning_week,
    "may_month_names": _may_month_names,
    "month_first_widths": _month_first_widths,
    "reserved_name_floor": _reserved_name_floor,
    "identifier_fold_collisions": _identifier_fold_collisions,
    "identifier_whole_numbers": _identifier_whole_numbers,
    "label_variants": _label_variants,
    "mixed_parsed_unparsed": _mixed_parsed_unparsed,
    "numeric_decimal_styles": _numeric_decimal_styles,
    "numeric_integer": _numeric_integer,
    "offset_bearing": _offset_bearing,
    "quarter": _quarter,
}

def _clock_ladder():
    """A clock column whose span is exactly as wide as its values."""
    column = _universal(
        "column_1", "time_of_day", "time_of_day", "data", "ok",
        n_present=12, n_missing=0, n_distinct=12, n_distinct_folded=12,
        n_numeric=0, n_not_numeric=12, n_out_of_range=0, n_contradictory=0,
        clock_form="hh-mm-ss",
        clock_percentiles={
            "min": "08:00:00", "p01": "08:00:00", "p05": "08:00:00",
            "p10": "08:00:01", "p25": "08:00:02", "p50": "08:00:05",
            "p75": "08:00:07", "p90": "08:00:09", "p95": "08:00:09",
            "p99": "08:00:09", "max": "08:00:10",
        },
        earliest="08:00:00", latest="08:00:10", n_unparsed=1,
        detection_evidence=(
            "11 value(s) are clock times written as hours, minutes and "
            "seconds, `09:30:00`, and 1 value(s) are not"
        ),
    )
    return {
        "why": "the first frozen case for the clock role, and the one "
        "that reaches its own repair rather than only its ladder. "
        "ELEVEN SECONDS HOLD ELEVEN PARSED CELLS: the ends are "
        "`08:00:00` and `08:00:10`, the eleven ordinals between them "
        "inclusive are exactly as many as the cells that parsed, and "
        "the column publishes every value different. So the all-"
        "different obligation of G7A.4 -- EXACT for this role where "
        "every other shape's distinctness falls to an envelope -- has "
        "no slack at all: each interior rank must land on the one "
        "ordinal left for it. Measured against the shipped generator "
        "with the step-up removed, the same column comes out holding "
        "`08:00:01` and `08:00:06` twice each, so the repair is doing "
        "the work here and not merely present.\n\n"
        "It also carries a cell that is not a clock time at all, which "
        "is what makes `n_unparsed` non-zero and puts a stand-in "
        "beside the parsed cells (G7A.5). The two ends are the "
        "published TEXT and cost no word, so the budget is the nine "
        "interior ranks, and the ladder is read in SECONDS OF DAY -- "
        "the form's own unit -- which is the whole of what makes this "
        "role different from the date role it borrows its transform "
        "from.",
        "column": column,
        "rows": 12,
    }


def _affixed_brackets():
    """A column of numbers each written inside a bracket pair."""
    ladder, ladder_claims, rungs, finer = _ladder_fields({
        "min": "12", "p01": "12.33", "p05": "13.65", "p10": "15.3",
        "p25": "20.25", "p50": "28.5", "p75": "36.75", "p90": "41.7",
        "p95": "43.35", "p99": "44.67", "max": "45",
    })
    claims = {
        ("column",) + key: value
        for key, value in ladder_claims.items()
    }
    moments = {}
    for name, text in (
        ("mean", "28.5"),
        ("std", "10.816653826391969"),
        ("skew", "0"),
        ("kurtosis", "1.7832167832167831"),
        ("numeric_share", "1"),
    ):
        field, claim = nearest_field(text)
        moments[name] = field
        claims[("column", name)] = claim
    column = _universal(
        "column_1", "affixed_number", "affixed_number", "data", "ok",
        n_present=12, n_missing=0, n_distinct=12, n_distinct_folded=12,
        # THE CELL COUNTS, and they are the ones an implementer is most
        # likely to hand to the numeric machinery by mistake.  A cell
        # reading `[12]` is NOT a number, so this column publishes no
        # numeric cells at all and twelve cells of ordinary text.
        n_numeric=0, n_not_numeric=12, n_out_of_range=0, n_contradictory=0,
        # ...and the CORE counts beside them, which are what G5 and G6
        # actually consume (G6A.1, G6A.2).
        n_affixed=12, n_core_numeric=12, n_core_not_numeric=0,
        n_core_out_of_range=0, n_core_contradictory=0,
        affix_prefix="[", affix_suffix="]",
        # THE OTHER WRAPPERS THIS COLUMN WEARS (plan P4-D36), and it
        # wears none: every cell of this case carries the same pair,
        # which is the ordinary shape of this role.  The key is
        # present and empty because this format has no optional keys.
        affix_variants=[],
        # ...and how many DIFFERENT cores the cells carry.  On a column
        # wearing one wrapper this is the count of different cells, and
        # every cell of this case carries a different number.
        n_core_distinct=12, n_core_distinct_folded=12,
        percentiles=ladder, percentiles_between=finer, std_unrepresentable=False,
        n_zero=0, n_negative=0, n_negative_unrepresentable=0,
        n_used_in_statistics=12, n_left_out_of_statistics=0,
        # THE SOURCE COLUMN HELD TWELVE DIFFERENT NUMBERS, and this
        # says so. The twin built from it held ELEVEN until the
        # integer-grid landing -- values drawn to a published ladder
        # repeat more evenly than real ones did, and `23` came out
        # twice -- which made this the one place in either file where a
        # conforming generator MISSED `n_distinct_values` and had to
        # say so. G6.5a's pass reaches the integer grid now, the twin
        # holds twelve, and NO committed case exercises that miss any
        # more. The reporting control is not lost with it -- a suite
        # test asserts the deviation seed by seed -- and what R-P4-145
        # records is that this harness pins cells and bytes and has
        # never pinned what a twin says.
        n_distinct_values=12,
        integer_valued=True, n_rows=12, numeric_styles={"plain": 12},
        # THE WHOLE-NUMBER FIELD-WIDTH CENSUS, READ OVER THE CORES
        # (contract 7.10 and AF7).  All twelve cores are `plain`, so
        # all twelve are counted, and the described source wrote every
        # one of them at TWO figures -- which is what a bracketed code
        # column looks like and is the shape residual R-P4-30 was
        # opened on.  Twelve clears the smallest group size, so the
        # width is named, and it asks G6.6 for twelve values of exactly
        # two figures.  The column's own ends are 12 and 45, so every
        # value the ladder yields is already two figures wide and no
        # core moves.
        field_widths={"2": 12},
        # THE REMARK THIS ROLE MUST CARRY (contract invariant AF-R).
        # A block of this role with no remark, or with any other
        # sentence in its place, is refused by the loader: the reader
        # of a profile must be told that the numbers described as
        # quantities came out of cells wearing shared text, and told
        # what to run if they are codes instead. The oracle discovered
        # this by being refused, which is the argument residual
        # R-P4-17 makes.
        # IT NAMES `--code` FIRST (residual R-P4-72, landing L19). The
        # sentence named `--identifier` alone, which is the OPPOSITE
        # declaration: a person told "if these are codes, run with
        # --identifier", doing exactly as they were told, published no
        # value of the column at all. The oracle is written from the
        # contract, so this text follows contract NF35 and is the
        # reason that clause and this line move in one commit.
        remarks=[
            "12 of this column's values are written as '[', a number, "
            "then ']', and synthtwin described those numbers as "
            "quantities: their average, their spread and their ends "
            "are in this profile. If these are codes rather than "
            "measurements, run the command again with --code NAME, "
            "where NAME is this column's name, and no average will be "
            "published over them; each code a smallest-group's worth "
            "of rows share is kept exactly as written, with the number "
            "of rows that carried it. If instead they are record "
            "numbers nothing should publish, --identifier NAME leaves "
            "them out of the profile altogether"
        ],
        **moments,
    )
    return {
        "why": "the first frozen case for the affixed role, and the one "
        "that pins the rule the role exists for: A COLUMN OF THIS ROLE "
        "PUBLISHES TWO SETS OF CLASS COUNTS AND THEY ARE NOT THE SAME "
        "SET. The universal counts answer for the CELLS, and a cell "
        "reading `[12]` is not a number, so this column publishes "
        "`n_numeric` of nought and twelve cells of ordinary text. The "
        "quantitative block answers for the CORES, and there "
        "`n_core_numeric` is twelve. An implementer who hands the "
        "numeric machinery the cell counts builds a column of no cells "
        "at all, which is what this case's mutant does and why it stops "
        "the oracle rather than moving its bytes. "
        "The pair is TWO-SIDED and its two characters differ, so the "
        "committed bytes pin the order of the wrap: `[` before the core "
        "and `]` after it, character for character as published, with "
        "no trimming and no normalization of either side. Every present "
        "cell wore the pair, so this case has no stragglers -- the walk "
        "of G6A.3, with its ceiling and its three refusals, is a second "
        "branch and belongs to a case of its own. The word budget is "
        "the numeric one read over the cores (G4.3): ten content words "
        "for twelve cells, which is what the shipped generator plans "
        "for this column as well. "
        "AND IT WAS THE ONE CASE IN EITHER FILE WHERE A CONFORMING "
        "GENERATOR MISSED A PUBLISHED FACT AND SAID SO. Its source "
        "column held twelve different numbers and it publishes twelve; "
        "the twin held eleven, because values drawn to a published "
        "ladder repeat more evenly than real ones did and `23` came "
        "out twice. The integer-grid landing gave method G6.5a's pass "
        "the whole-number columns it had been declining, this case is "
        "one of them, and the twin holds twelve now -- so the file no "
        "longer carries a case where that miss is exercised at all, "
        "which is residual R-P4-145. `n_distinct_values` stays "
        "REPORT-ONLY (residual R-P4-20): what changed is that no "
        "committed vector still shows the report doing its work.",
        "column": column,
        "rows": 12,
        "identifier_declared": False,
        "rungs": rungs,
        "claims": claims,
    }


def _joined_readings():
    """Two numbers in one cell, and the walk that decides which meet."""
    first_ladder, first_claims, first_rungs, first_finer = _ladder_fields({
        "min": "24", "p01": "24", "p05": "24", "p10": "24.2",
        "p25": "29", "p50": "36.5", "p75": "40", "p90": "50.8",
        "p95": "54.25", "p99": "56.45", "max": "57",
    })
    second_ladder, second_claims, second_rungs, second_finer = _ladder_fields({
        "min": "25", "p01": "25", "p05": "25", "p10": "25",
        "p25": "25", "p50": "30", "p75": "40", "p90": "44.5",
        "p95": "45", "p99": "45", "max": "45",
    })
    claims = {}
    for place, ladder_claims in ((0, first_claims), (1, second_claims)):
        for key, value in ladder_claims.items():
            claims[("column", "parts", place) + key] = value
    parts = []
    for place, ladder, finer_block, moments in (
        (0, first_ladder, first_finer, (
            ("mean", "36.666666666666664"),
            ("std", "10.236595077850778"),
            ("skew", "0.5765321212279275"),
            ("kurtosis", "2.645135996997432"),
            ("numeric_share", "1"))),
        (1, second_ladder, second_finer, (
            ("mean", "32.916666666666664"),
            ("std", "7.821396449755148"),
            ("skew", "0.43445149772021224"),
            ("kurtosis", "1.685945422653337"),
            ("numeric_share", "1"))),
    ):
        block = {
            "percentiles": ladder,
            "percentiles_between": finer_block, "n_rows": 12, "n_zero": 0,
            "n_negative": 0, "n_negative_unrepresentable": 0,
            "n_used_in_statistics": 12, "n_left_out_of_statistics": 0,
            "integer_valued": True, "numeric_styles": {"plain": 12},
            "fraction_widths": {}, "pad_widths": {},
            # No mark between thousands: a reading of two figures has
            # no thousands to group (plan P4-D38, at a part's depth).
            "group_separator": "",
            # ...no negative reading and no signed decimal either
            # (landing 2b.2): a pressure is written unsigned.
            "negative_form": "minus",
            "decimal_plus": {},
            # ...and neither census of a MIXED convention (landing 2b.7,
            # invariants NS2 and TM1). A position is read from figures
            # and one point alone, so it can wear no notation and no
            # mark at all, and both censuses are empty at this depth for
            # every joined column there can be. They are stated here
            # rather than defaulted because a part block states its own
            # keys: the defaults this file applies reach a COLUMN block
            # and never a position, which is what made this case the one
            # the loader refused when the two keys arrived.
            "negative_notations": {},
            "thousands_marks": {},
            # ...and the wide-run word of this POSITION (landing 2b.13).
            # Stated here for the same reason the two censuses above
            # are: the defaults this file applies reach a COLUMN block
            # and never a position. Every reading a position holds is
            # two figures, so none of them is a run past what a double
            # keeps and the word is the one a column with no such run
            # publishes.
            "wide_runs": "none",
            # The whole-number field-width census of this POSITION
            # (contract 7.10 read at that depth).  Every one of the
            # twelve readings a position holds is `plain`, and the
            # described source wrote all of them at two figures -- a
            # blood pressure is written `120/80`, never `120/8` -- so
            # the census names one width for all twelve.
            "field_widths": {"2": 12},
            "std_unrepresentable": False, "value_histogram": {},
            # ...and the bins holding NOTHING (contract 7.11, plan
            # P4-D32), read at this depth like every other fact of a
            # block of numbers.  Empty, because this position's twelve
            # readings are stated by hand and nothing here turns on
            # where they are NOT; with no stretch named, method G6.7
            # does nothing and no cell of this case depends on it.
            "empty_bins": [],
            # ...and the edges of those stretches (contract 7.11a),
            # empty for the same reason: no stretch is named, so there
            # is no run for a pair to belong to.
            "empty_edges": [],
            "n_distinct_values": 9 if place == 0 else 5,
            # Each position carries the mode pair like any block of
            # numbers (contract Q18). Both positions of this column
            # repeat values, so a real profile of it would publish a
            # mode; this case publishes the withheld pair because the
            # fact is REPORT-ONLY. Withholding it is not nothing since
            # landing 2b.1: G5.2a's cap then reads the ladder, and on
            # this straight-line ladder over twelve cells that cap is
            # two, which is why the first position no longer writes one
            # number three times.
            "mode": None,
            "mode_count": 0,
        }
        for name, text in moments:
            field, claim = nearest_field(text)
            block[name] = field
            claims[("column", "parts", place, name)] = claim
        parts.append(block)
    agreement, agreement_claim = nearest_field("0.4323")
    claims[("column", "part_agreements", 0)] = agreement_claim
    column = _universal(
        "column_1", "joined_numbers", "joined_numbers", "data", "ok",
        n_present=12, n_missing=0, n_distinct=12, n_distinct_folded=12,
        n_numeric=0, n_not_numeric=12, n_out_of_range=0, n_contradictory=0,
        parts=parts, separator="/", n_parts=2, n_joined=12, n_unparsed=0,
        part_min_widths=[2, 2], part_agreements=[agreement],
        part_above=[7],
    )
    return {
        "why": "the first frozen case for the joined role, and the one "
        "that pins the PAIRING WALK of G6B.4 -- the only search in this "
        "method, and the only place where synthtwin reproduces "
        "structure between two quantities at all. Each position is "
        "built by the numeric rules over its own view, laid out by "
        "G5.2's grain rule from that position's own count of different "
        "numbers, and the walk then decides which number of one meets "
        "which of the other, holding the FIRST position still so that "
        "no position's multiset can change. "
        "IT IS NOT A COLUMN THE WALK CAN IGNORE, and it was chosen "
        "against that check rather than assumed. A first draft "
        "published an agreement of 0.9983, which a rank-for-rank start "
        "already meets, so removing the walk entirely changed no "
        "committed byte: that case pinned the sort and the start rule "
        "and nothing else. This column publishes 0.4323, holds the "
        "earlier position above the later in only seven of twelve "
        "rows, and repeats values in both positions. "
        "WHAT IT PINS, MEASURED RULE BY RULE AND RE-MEASURED AT "
        "LANDING L7. Withdrawn one at a time from this file, these "
        "move its cells: the walk itself, six; the VALUE of the 0.4 "
        "threshold, eleven, because moving it to 0.9 pulls this column "
        "into the permutation branch; the proposal step of G6B.4a, "
        "six; and the distinct-cell term of the distance, two. A fifth "
        "is REFUSED rather than moved: taking the whole cell's "
        "distinctness for a position instead of the position's own "
        "changes the draw budget, and the case is rejected before a "
        "cell is built. "
        "AND IT PINS FEWER RULES THAN IT DID, WHICH IS SAID HERE "
        "RATHER THAN LEFT TO BE NOTICED. Before L7 it also pinned the "
        "reserve cursor's restart, accept-on-equal, that a try ceiling "
        "exists, and the `part_above` term. It pins none of those now: "
        "the proposal step reaches this column's published cell count "
        "early, so the walk stops moving long before the ceiling, "
        "before an equal swap matters and before the cursor wraps -- "
        "and `part_above` is already met at the start. TEN rules of "
        "this walk therefore stand on the method's word and on the "
        "mutation testing of the shipped generator, not on this case: "
        "the anchor, each position's own start, the cursor restart "
        "stepping along, accept-on-equal, both facts about the "
        "ceiling, the `part_above` term, the agreement scored outside "
        "its window, the agreement tie-break, and the proposal's "
        "partner condition. A case that bites on those wants a longer "
        "column and more than two positions, and is owed. "
        "AND THE WALK DOES NOT CONVERGE ON THIS COLUMN, which the case "
        "freezes rather than hides. The twin meets `part_above` "
        "exactly, seven of twelve, holds all twelve readings "
        "different, and reaches a rank agreement of 0.5103 against the "
        "0.4323 published -- outside G12.9's window, reported as a "
        "miss by both pages: it stops at its try ceiling, never on "
        "distance. It also holds EIGHT different first numbers where "
        "the block publishes nine, which is residual R-P4-120 frozen "
        "into a committed case.",
        "column": column,
        "rows": 12,
        "identifier_declared": False,
        "rungs": [first_rungs, second_rungs],
        "claims": claims,
    }

def _pooled_marks():
    column = _universal(
        "column_1", "datetime", "datetime", "data", "ok",
        n_present=24, n_missing=0, n_distinct=24, n_distinct_folded=24,
        n_numeric=0, n_not_numeric=24, n_out_of_range=0, n_contradictory=0,
        format="iso-datetime", resolution="datetime", time_precision="minute",
        subsecond_digits=0, datetimes_read_at="local",
        earliest="2024-05-01 06:30:00", latest="2024-05-24 21:45:00",
        earliest_utc_offset="(none)", latest_utc_offset="(none)",
        date_percentiles={
            "min": "2024-05-01 06:30:00",
            "p01": "2024-05-01 06:30:00",
            "p05": "2024-05-02 09:15:00",
            "p10": "2024-05-03 13:40:00",
            "p25": "2024-05-06 11:55:00",
            "p50": "2024-05-12 12:35:00",
            "p75": "2024-05-18 08:50:00",
            "p90": "2024-05-21 17:05:00",
            "p95": "2024-05-22 10:55:00",
            "p99": "2024-05-23 14:20:00",
            "max": "2024-05-24 21:45:00",
        },
        n_unparsed=0, utc_offsets={"(none)": 24},
        resolution_mix={"iso-datetime": 24},
        datetime_separators={"upper_t": 14, "(withheld)": 10},
        all_at_midnight=False, n_at_midnight=None,
    )
    return {
        "why": (
            "the withheld pool of landing 2b.3. The census names one mark at "
            "fourteen values and holds ten back, and every value of a named mark is "
            "counted under its name, so the ten wore the two marks it leaves "
            "unnamed: they are split evenly over those two, five a space and five a "
            "lower-case t, and spread by the same rotation as the named mark. The "
            "rule this overturns wrote the pool with the commonest mark, erasing "
            "the two spellings; this case's mutant is that rule."
        ),
        "column": column,
        "rows": 24,
        "identifier_declared": False,
    }


def _slashed_pool():
    column = _universal(
        "column_1", "datetime", "datetime", "data", "ok",
        n_present=10, n_missing=0, n_distinct=10, n_distinct_folded=10,
        n_numeric=0, n_not_numeric=10, n_out_of_range=0, n_contradictory=0,
        format="slashed-iso-datetime", resolution="datetime", time_precision="minute",
        subsecond_digits=0, datetimes_read_at="local",
        earliest="2024-06-03 08:10:00", latest="2024-06-28 11:50:00",
        earliest_utc_offset="(none)", latest_utc_offset="(none)",
        date_percentiles={
            "min": "2024-06-03 08:10:00",
            "p01": "2024-06-03 08:10:00",
            "p05": "2024-06-03 08:10:00",
            "p10": "2024-06-03 08:10:00",
            "p25": "2024-06-08 09:05:00",
            "p50": "2024-06-13 07:55:00",
            "p75": "2024-06-19 10:45:00",
            "p90": "2024-06-25 16:25:00",
            "p95": "2024-06-25 16:25:00",
            "p99": "2024-06-25 16:25:00",
            "max": "2024-06-28 11:50:00",
        },
        n_unparsed=0, utc_offsets={"(withheld)": 10},
        resolution_mix={"slashed-iso-datetime": 10},
        datetime_separators={"(withheld)": 10},
        all_at_midnight=False, n_at_midnight=None,
    )
    return {
        "why": (
            "the permitted marks of a slashed stamp, landing 2b.3. Ten year-first "
            "slashed stamps whose every mark is pooled: the reader of that form "
            "splits the day from the clock on one space and takes nothing else, so "
            "the pool is spent on the space alone and every cell carries one. It is "
            "also the first frozen case for the slashed-iso-datetime member. "
            "Offered all three marks, as an ISO stamp is, the cells take a T and a "
            "t that no such table could write; this case's mutant is that offer."
        ),
        "column": column,
        "rows": 10,
        "identifier_declared": False,
    }


def _midnight_mixed_forms():
    column = _universal(
        "column_1", "datetime", "datetime", "data", "ok",
        n_present=24, n_missing=0, n_distinct=24, n_distinct_folded=24,
        n_numeric=0, n_not_numeric=24, n_out_of_range=0, n_contradictory=0,
        format="iso-mixed", resolution="datetime", time_precision="second",
        subsecond_digits=0, datetimes_read_at="local",
        earliest="2024-01-04 00:00:00", latest="2024-12-16 00:00:00",
        earliest_utc_offset="(none)", latest_utc_offset="(none)",
        date_percentiles={
            "min": "2024-01-04 00:00:00",
            "p01": "2024-01-04 00:00:00",
            "p05": "2024-01-19 00:00:00",
            "p10": "2024-02-02 00:00:00",
            "p25": "2024-03-25 00:00:00",
            "p50": "2024-06-27 00:00:00",
            "p75": "2024-09-18 00:00:00",
            "p90": "2024-11-05 00:00:00",
            "p95": "2024-11-20 00:00:00",
            "p99": "2024-12-02 00:00:00",
            "max": "2024-12-16 00:00:00",
        },
        n_unparsed=0, utc_offsets={"(none)": 24},
        resolution_mix={"iso-date": 13, "iso-datetime": 11},
        datetime_separators={"space": 11},
        all_at_midnight=True, n_at_midnight=24,
    )
    return {
        "why": (
            "the narrowing of owner decision 4, landing 2b.3. Twenty-four days at "
            "midnight read jointly, thirteen written as bare dates and eleven with "
            "a midnight clock: the column is counted in whole days, so every rank "
            "is a day a bare date spells exactly, and the form census is spent over "
            "the ranks by the smooth rotation, the census of marks over the ranks "
            "that write a clock. Writing every rank as a moment, as decision 4 did "
            "for every joint column, is this case's mutant."
        ),
        "column": column,
        "rows": 24,
        "identifier_declared": False,
    }


def _partial_midnight():
    column = _universal(
        "column_1", "datetime", "datetime", "data", "ok",
        n_present=24, n_missing=0, n_distinct=24, n_distinct_folded=24,
        n_numeric=0, n_not_numeric=24, n_out_of_range=0, n_contradictory=0,
        format="iso-datetime", resolution="datetime", time_precision="second",
        subsecond_digits=0, datetimes_read_at="local",
        earliest="2024-03-01 00:00:00", latest="2024-03-30 15:31:16",
        earliest_utc_offset="(none)", latest_utc_offset="(none)",
        date_percentiles={
            "min": "2024-03-01 00:00:00",
            "p01": "2024-03-01 00:00:00",
            "p05": "2024-03-02 09:14:07",
            "p10": "2024-03-03 00:00:00",
            "p25": "2024-03-06 16:40:12",
            "p50": "2024-03-13 18:05:58",
            "p75": "2024-03-21 10:59:41",
            "p90": "2024-03-26 00:00:00",
            "p95": "2024-03-27 12:07:50",
            "p99": "2024-03-29 00:00:00",
            "max": "2024-03-30 15:31:16",
        },
        n_unparsed=0, utc_offsets={"(none)": 24},
        resolution_mix={"iso-datetime": 24},
        datetime_separators={"space": 24},
        all_at_midnight=False, n_at_midnight=12,
    )
    return {
        "why": (
            "the move onto midnight of landing 2b.3. Twenty-four moments to the "
            "second, twelve of them at midnight: the ranks are interpolated in "
            "seconds, each rung rank takes its published rung, the values at midnight still "
            "owed are spread over the other ranks by the smooth rotation, and each "
            "chosen rank moves to its nearest midnight without passing a pinned "
            "rank. Keeping the interpolated instants, which put nearly every value "
            "part-way through a day, is this case's mutant."
        ),
        "column": column,
        "rows": 24,
        "identifier_declared": False,
    }


def _midnight_two_offsets():
    column = _universal(
        "column_1", "datetime", "datetime", "data", "ok",
        n_present=24, n_missing=0, n_distinct=24, n_distinct_folded=24,
        n_numeric=0, n_not_numeric=24, n_out_of_range=0, n_contradictory=0,
        format="iso-datetime", resolution="datetime", time_precision="second",
        subsecond_digits=0, datetimes_read_at="utc",
        earliest="2024-01-07 23:00:00", latest="2024-06-27 22:00:00",
        earliest_utc_offset="+01:00", latest_utc_offset="+02:00",
        date_percentiles={
            "min": "2024-01-07 23:00:00",
            "p01": "2024-01-07 23:00:00",
            "p05": "2024-01-21 23:00:00",
            "p10": "2024-02-04 23:00:00",
            "p25": "2024-03-03 23:00:00",
            "p50": "2024-03-28 23:00:00",
            "p75": "2024-05-14 22:00:00",
            "p90": "2024-06-11 22:00:00",
            "p95": "2024-06-18 22:00:00",
            "p99": "2024-06-23 22:00:00",
            "max": "2024-06-27 22:00:00",
        },
        n_unparsed=0, utc_offsets={"+01:00": 12, "+02:00": 12},
        resolution_mix={"iso-datetime": 24},
        datetime_separators={"upper_t": 24},
        all_at_midnight=True, n_at_midnight=24,
    )
    return {
        "why": (
            "midnight on two offsets, landing 2b.3. Twenty-four local midnight values, "
            "the winter days written at +01:00 and the summer days at +02:00, "
            "published on the shared clock: the column is counted in seconds, each "
            "rung rank takes its rung and the offset that rung is a midnight under, "
            "and every rank moves onto a midnight of its own offset. Counting it in "
            "days on the shared clock, which reads 23:00 as the day before, is this "
            "case's mutant."
        ),
        "column": column,
        "rows": 24,
        "identifier_declared": False,
    }


def _midnight_bare_offsets():
    column = _universal(
        "column_1", "datetime", "datetime", "data", "ok",
        n_present=24, n_missing=0, n_distinct=12, n_distinct_folded=12,
        n_numeric=0, n_not_numeric=24, n_out_of_range=0, n_contradictory=0,
        format="iso-mixed", resolution="datetime", time_precision="second",
        subsecond_digits=0, datetimes_read_at="utc",
        earliest="2024-04-30 22:00:00", latest="2024-05-07 00:00:00",
        earliest_utc_offset="+02:00", latest_utc_offset="(none)",
        date_percentiles={
            "min": "2024-04-30 22:00:00",
            "p01": "2024-04-30 22:00:00",
            "p05": "2024-05-01 00:00:00",
            "p10": "2024-05-01 22:00:00",
            "p25": "2024-05-02 22:00:00",
            "p50": "2024-05-02 22:00:00",
            "p75": "2024-05-06 00:00:00",
            "p90": "2024-05-06 00:00:00",
            "p95": "2024-05-06 00:00:00",
            "p99": "2024-05-06 22:00:00",
            "max": "2024-05-07 00:00:00",
        },
        n_unparsed=0, utc_offsets={"(none)": 13, "+02:00": 11},
        resolution_mix={"iso-date": 13, "iso-datetime": 11},
        datetime_separators={"upper_t": 11},
        all_at_midnight=True, n_at_midnight=24,
    )
    return {
        "why": (
            "the repair pass of landing 2b.3. Twenty-four values at local midnight read "
            "jointly on the shared clock, thirteen bare dates and eleven moments at "
            "T00:00:00+02:00, whose rungs stand at 22:00 where a moment stood and at "
            "00:00 where a bare date did, with seven ranks between p25 and p50 on one "
            "22:00 instant and five between p75 and p95 on one midnight of the shared "
            "clock. Every rank whose instant the tail fixes takes the form and the "
            "offset that instant stands at midnight under before the rotation spends "
            "the rest. Settling only the two ends, which wrote rung ranks as the day "
            "before and moments at T02:00:00+02:00, is this case's mutant."
        ),
        "column": column,
        "rows": 24,
        "identifier_declared": False,
    }


def _flat_numbers(value_text, rows, **facts):
    """A column of one number written several ways, as landing 2b.2's cases need.

    Every rung and every moment is the one value, so no cell of these
    cases turns on where a value is placed -- only on how it is written,
    which is what each of them is for.  The spread is nought, so the
    shape and the tails are null, as a column of one value publishes
    them.
    """
    ladder, ladder_claims, rungs, finer = _ladder_fields(
        {key: value_text for key in LADDER_KEYS}
    )
    claims = {("column",) + key: value for key, value in ladder_claims.items()}
    moments = {}
    for name, text in (("mean", value_text), ("std", "0"), ("numeric_share", "1")):
        field, claim = nearest_field(text)
        moments[name] = field
        claims[("column", name)] = claim
    present = facts.pop("n_present", rows)
    column = _universal(
        "column_1", "continuous", "continuous", "data", "ok",
        n_present=present, n_numeric=present, n_not_numeric=0,
        n_out_of_range=0, n_contradictory=0,
        percentiles=ladder, percentiles_between=finer,
        std_unrepresentable=False, skew=None, kurtosis=None,
        n_zero=0, n_negative_unrepresentable=0,
        n_used_in_statistics=present, n_left_out_of_statistics=0,
        integer_valued=False, n_rows=rows, n_distinct_values=1,
        **moments,
        **facts,
    )
    return column, rungs, claims


def _grouped_charges():
    column, rungs, claims = _flat_numbers(
        "12345", 44,
        n_missing=0, n_distinct=6, n_distinct_folded=6, n_negative=0,
        numeric_styles={"decimal": 22, "leading_plus": 11, "plain": 11},
        fraction_widths={"1": 22}, pad_widths={}, field_widths={"5": 22},
        group_separator=",", decimal_plus={"+": 11},
    )
    return {
        "why": "the mark between thousands of plan P4-D38, the first frozen "
        "case publishing a comma, beside the count of signed decimals "
        "landing 2b.2 publishes. Every cell holds one value, twelve "
        "thousand three hundred and forty-five, written plain, with a plus, "
        "and with a point -- and eleven of the twenty-two written with a "
        "point carry a plus too, spread one in every two rather than taken "
        "from the first cell upward, which would tie a plus to the smallest "
        "values. The column counts six spellings where those four supply "
        "four, so two cells spend a zero, and it pins that a cell which "
        "spends one carries no mark and keeps its plus in front of the "
        "zeros: `012345.0` and `+012345.0`, never a padded field wearing a "
        "comma. This case's mutant takes the plus from the first cell "
        "upward, and cells move.",
        "column": column,
        "rows": 44,
        "identifier_declared": False,
        "rungs": rungs,
        "claims": claims,
    }


def _grouped_decimal_comma():
    column, rungs, claims = _flat_numbers(
        "42037.34", 24,
        n_present=22, n_missing=2,
        n_distinct=2, n_distinct_folded=2, n_negative=0,
        numeric_styles={"decimal": 22},
        fraction_widths={"2": 22}, pad_widths={}, field_widths={},
        group_separator=".",
    )
    return {
        "why": "the exchange of plan P4-D26 on a column whose grouping is "
        "published as a point, the first frozen case publishing one. The "
        "column is DECLARED to write its decimals with a comma, which this "
        "case's own test settings name, so its numbers are grouped with a "
        "comma and then have every point and comma exchanged: `42.037,34`. "
        "One cell spends a zero and carries no mark, `042037,34`, and the "
        "two absent cells are written empty and exchanged by nothing. This "
        "case's mutant withdraws the exchange, and every present cell "
        "moves.",
        "column": column,
        "rows": 24,
        "identifier_declared": False,
        "decimal_comma_declared": True,
        "rungs": rungs,
        "claims": claims,
    }


def _spaced_brackets():
    column, rungs, claims = _flat_numbers(
        "-12345.5", 22,
        n_missing=0, n_distinct=2, n_distinct_folded=2, n_negative=22,
        numeric_styles={"decimal": 22},
        fraction_widths={"1": 22}, pad_widths={}, field_widths={},
        group_separator=" ", negative_form="brackets",
    )
    return {
        "why": "two spellings landing 2b.2 publishes: a space between "
        "thousands and accounting brackets for a negative number. Every "
        "cell is minus twelve thousand three hundred and forty-five and a "
        "half, written `(12 345.5)`; one cell spends a zero and is written "
        "`(012345.5)`, the brackets closing around the zeros with no mark "
        "and no sign inside them, which is what keeps a written negative "
        "apart from the contradictory stand-in of G10.3. This case's mutant "
        "withdraws the notation, and every cell is written with a minus "
        "instead.",
        "column": column,
        "rows": 22,
        "identifier_declared": False,
        "rungs": rungs,
        "claims": claims,
    }


def _mixed_conventions():
    column, rungs, claims = _flat_numbers(
        "-12345.5", 22,
        n_missing=0, n_distinct=2, n_distinct_folded=2, n_negative=22,
        numeric_styles={"decimal": 22},
        fraction_widths={"1": 22}, pad_widths={}, field_widths={},
        group_separator=" ", negative_form="brackets",
        # THE TWO MIXED CONVENTIONS OF LANDING 2b.7, each naming two.
        negative_notations={"minus": 11, "brackets": 11},
        thousands_marks={" ": 11, " ": 11},
    )
    return {
        "why": "the two censuses landing 2b.7 adds, and the ONLY case in "
        "either file that names more than one convention -- which is the "
        "whole of what it is for. `negative_form` and `group_separator` "
        "publish a column's MAJORITY, and until this landing the twin "
        "wrote every cell that way, so a column mixing two came back "
        "written wholly as one with every check passing. Where a census "
        "names ONE convention nothing can show that: the census path and "
        "the majority path write the same cell, so a mutant that withdraws "
        "the census is invisible. Here each census names two at eleven "
        "cells apiece, so the cells divide and a mutant moves them. Every "
        "cell is minus twelve thousand three hundred and forty-five and a "
        "half. EACH CENSUS IS SPENT IN THE CONTRACT'S OWN ORDER OF "
        "CONVENTIONS, so the earliest cells take the earliest convention "
        "each names: the first eleven are written `-12 345.5`, a minus in "
        "front and an ordinary space between the thousands, and the last "
        "eleven `(12 345.5)`, in brackets and grouped with a narrow "
        "no-break space. That the two pairings fall the way they do is "
        "the ORDER rule showing, and a generator that spent either "
        "census the other way round writes different cells here. Two "
        "spellings of one number is the count of different cells this "
        "column publishes, so no cell spends a leading zero to reach it. "
        "This case's mutant withdraws the notation census and every cell "
        "is written in the majority, brackets, as the twin wrote them "
        "before this landing.",
        "column": column,
        "rows": 22,
        "identifier_declared": False,
        "rungs": rungs,
        "claims": claims,
    }


def _bare_mark_remainder():
    column, rungs, claims = _flat_numbers(
        "12345.5", 33,
        n_missing=0, n_distinct=2, n_distinct_folded=2, n_negative=0,
        numeric_styles={"decimal": 33},
        fraction_widths={"1": 33}, pad_widths={}, field_widths={},
        group_separator=",",
        # THE BARE REMAINDER OF PLAN P4-D142. Twenty-two cells grouped
        # with a comma beside eleven the source wrote bare: the census
        # names the comma alone and is published because what it leaves
        # of the thirty-three groupable cells is eleven, the census floor.
        thousands_marks={",": 22},
    )
    return {
        "why": "G6.1's bare remainder (plan P4-D142): a census naming ONE "
        "mark is the whole of the grouped cells, so the groupable cells it "
        "does not cover are written with no mark wherever at least the "
        "census floor of them are left. Every cell is twelve thousand three "
        "hundred and forty-five and a half: the first twenty-two are "
        "written `12,345.5` and the last eleven `12345.5`. The mutant "
        "restores the rule this decision replaced -- every cell no named "
        "count covers wears the published mark -- and all thirty-three are "
        "grouped, which is the twin the final Codex review measured.",
        "column": column,
        "rows": 33,
        "identifier_declared": False,
        "rungs": rungs,
        "claims": claims,
    }


def _pooled_mark_cells():
    column, rungs, claims = _flat_numbers(
        "12345.5", 44,
        n_missing=0, n_distinct=2, n_distinct_folded=2, n_negative=0,
        numeric_styles={"decimal": 44},
        fraction_widths={"1": 44}, pad_widths={}, field_widths={},
        group_separator=",",
        # A POOLED REMAINDER OF ELEVEN beside thirty-three commas: marks
        # each worn by fewer cells than the floor, together a group.
        thousands_marks={",": 33, "(withheld)": 11},
    )
    return {
        "why": "G6.1's pooled remainder of a census of marks (plan P4-D142): "
        "it is written with the first of a space, an apostrophe, U+2019, "
        "U+00A0, U+202F and U+2009 that the census does not name, never with "
        "a named mark. Every cell is twelve thousand three hundred and "
        "forty-five and a half: the first thirty-three are written "
        "`12,345.5` and the last eleven `12 345.5`. The mutant writes the "
        "pool with the published comma, as the generator did before this "
        "decision, and the twin's comma count passes the published one.",
        "column": column,
        "rows": 44,
        "identifier_declared": False,
        "rungs": rungs,
        "claims": claims,
    }


def _unpublished_majority_marks():
    column, rungs, claims = _flat_numbers(
        "12345.5", 22,
        n_missing=0, n_distinct=2, n_distinct_folded=2, n_negative=0,
        numeric_styles={"decimal": 22},
        fraction_widths={"1": 22}, pad_widths={}, field_widths={},
        # NO MAJORITY, SO NO PUBLISHED MARK, beside a census naming two.
        group_separator="",
        thousands_marks={",": 11, " ": 11},
    )
    return {
        "why": "G6.1's groupable cells asked with a mark that writes one (plan "
        "P4-D142). The column publishes no mark between thousands -- eleven "
        "cells grouped with a comma and eleven with a space make no "
        "majority -- so a cell asked whether the PUBLISHED mark puts a mark "
        "in it is groupable nowhere. It is asked with the first mark the "
        "census names instead: the first eleven cells are written "
        "`12,345.5` and the last eleven `12 345.5`. The mutant asks with the "
        "published mark and every cell is written `12345.5`.",
        "column": column,
        "rows": 22,
        "identifier_declared": False,
        "rungs": rungs,
        "claims": claims,
    }


def _plus_padded_field():
    column, rungs, claims = _flat_numbers(
        "12345", 22,
        n_missing=0, n_distinct=1, n_distinct_folded=1, n_negative=0,
        numeric_styles={"leading_plus": 22},
        fraction_widths={}, pad_widths={"7": 22}, field_widths={"7": 22},
    )
    return {
        "why": "G6.3's second tier of named field widths (plan P4-D145): a "
        "plus does not hide a pad. The census counts twenty-two cells seven "
        "figures wide, every one of them written with a plus, so the widths "
        "are served to the plus-signed cells once the padded form has none "
        "to take them. Every cell is twelve thousand three hundred and "
        "forty-five, written `+0012345`. The mutant serves the padded form "
        "alone and every cell is written `+12345`, two figures short of its "
        "field.",
        "column": column,
        "rows": 22,
        "identifier_declared": False,
        "rungs": rungs,
        "claims": claims,
    }


def _identifier_layout_packing():
    column = _universal(
        "column_1", "identifier", "code", "identifier", "ok",
        n_present=88, n_missing=0, n_distinct=6, n_distinct_folded=6,
        n_numeric=0, n_not_numeric=88, n_out_of_range=0, n_contradictory=0,
        min_length=5, max_length=5, all_whole_numbers=False,
        n_all_digits=0, n_code_alphabet=44,
        n_distinct_by_occurrences={"11": 4, "22": 2},
        layout_forms={
            "@@#%%": 11, "@@*%%": 11, "@@-%%": 22, "@@.%%": 11,
            "@@:%%": 11, "@@_%%": 22,
        },
    )
    return {
        "why": "G9.6's layout packing (plan P4-D182): a declared identifier "
        "of four groups of eleven rows and two of twenty-two, whose census "
        "names two code-alphabet layouts of twenty-two cells and four "
        "wide-alphabet layouts of eleven. The class-and-alphabet packing "
        "fills the code band first and offers the smaller groups first, so "
        "it gives the code band the four groups of eleven and the wide band "
        "the two of twenty-two, and no whole group of twenty-two can wear a "
        "layout of eleven: the first layout writes `@@.%%` and `@@:%%` "
        "nought times. The census is then packed as a third margin of the "
        "same grid, which gives each band the groups its layouts can take, "
        "and every group is offered its packed layout alone. This case's "
        "mutant withdraws the layout packing, and the check of 7.12 stops "
        "the oracle before any byte is written.",
        "column": column,
        "rows": 88,
        "identifier_declared": True,
    }


def _saturated_levels():
    ladder, ladder_claims, rungs, finer = _ladder_fields({
        "min": "2", "p01": "2", "p05": "2", "p10": "2",
        "p25": "3.2", "p50": "3.2", "p75": "6.5", "p90": "6.5",
        "p95": "15", "p99": "15", "max": "15",
    })
    claims = {("column",) + key: value for key, value in ladder_claims.items()}
    moments = {}
    for name, text in (("mean", "5.181818181818182"),
                       ("std", "3.6670368270456586"),
                       ("skew", "1.62901186981742"),
                       ("kurtosis", "5.148273554762339"),
                       ("numeric_share", "1"), ("mode", "6.5")):
        field, claim = nearest_field(text)
        moments[name] = field
        claims[("column", name)] = claim
    column = _universal(
        "column_1", "continuous", "continuous", "data", "ok",
        n_present=33, n_missing=0, n_distinct=4, n_distinct_folded=4,
        n_distinct_values=4,
        n_numeric=33, n_not_numeric=0, n_out_of_range=0, n_contradictory=0,
        percentiles=ladder, percentiles_between=finer, std_unrepresentable=False,
        n_zero=0, n_negative=0, n_negative_unrepresentable=0,
        n_used_in_statistics=33, n_left_out_of_statistics=0,
        integer_valued=False, n_rows=33, numeric_styles={"decimal": 33},
        mode_count=12, fraction_widths={"1": 33}, field_widths={},
        # FOUR LEVELS, EIGHT, TEN, TWELVE AND THREE CELLS: 2.0, 3.2, 6.5 and
        # 15.0, each named by two rungs or more, with 6.5 the mode.
        **moments,
    )
    return {
        "why": "G6.5a's fill of a column whose published levels are its "
        "strata (plan P4-D178): thirty-three readings at one place of four "
        "levels, 2.0, 3.2, 6.5 and 15.0, each named by at least two of the "
        "hundred and one rungs, with the mode at 6.5 and four different "
        "values published. The rungs name more than four numbers -- a rung "
        "between two plateaus is interpolated -- so the levels are the "
        "numbers two rungs or more name, with the ends and the mode, and the "
        "four strata take them in order. The mutant withdraws the fill, and "
        "the walk writes `4.6` for a level no source cell held.",
        "column": column,
        "rows": 33,
        "identifier_declared": False,
        "rungs": rungs,
        "claims": claims,
    }


def _saturated_tenths():
    ladder, ladder_claims, rungs, finer = _ladder_fields({
        "min": "0.1", "p01": "0.132", "p05": "0.26", "p10": "0.42",
        "p25": "0.9", "p50": "1.1", "p75": "1.4", "p90": "1.88",
        "p95": "2.04", "p99": "2.168", "max": "2.2",
    })
    claims = {("column",) + key: value for key, value in ladder_claims.items()}
    moments = {}
    for name, text in (("mean", "1.1333333333333333"),
                       ("std", "0.526584909265986"),
                       ("skew", "0.09615802208472209"),
                       ("kurtosis", "2.687623796188785"),
                       ("numeric_share", "1"), ("mode", "1.1")):
        field, claim = nearest_field(text)
        moments[name] = field
        claims[("column", name)] = claim
    column = _universal(
        "column_1", "continuous", "continuous", "data", "ok",
        n_present=33, n_missing=0, n_distinct=22, n_distinct_folded=22,
        n_distinct_values=22,
        n_numeric=33, n_not_numeric=0, n_out_of_range=0, n_contradictory=0,
        percentiles=ladder, percentiles_between=finer, std_unrepresentable=False,
        n_zero=0, n_negative=0, n_negative_unrepresentable=0,
        n_used_in_statistics=33, n_left_out_of_statistics=0,
        integer_valued=False, n_rows=33, numeric_styles={"decimal": 33},
        mode_count=12, fraction_widths={"1": 33}, field_widths={},
        **moments,
    )
    return {
        "why": "G6.5a's fill of a saturated grid of TENTHS (plan P4-D176): "
        "thirty-three readings at one place publishing twenty-two different "
        "numbers between the ends 0.1 and 2.2, which hold exactly twenty-two "
        "tenths, so the strata take those tenths in order, each once. The "
        "mutant withdraws the fill on a written grid and leaves the integer "
        "one, and the walk places the strata elsewhere.",
        "column": column,
        "rows": 33,
        "identifier_declared": False,
        "rungs": rungs,
        "claims": claims,
    }


def _separated_in_order():
    built = _signed_pads()
    column = built["column"]
    # ELEVEN WHOLE NUMBERS FROM 100 TO 110, written three times each: the
    # padded column of `signed_pads` publishing all eleven and twenty-two
    # spellings, so its separation walk has work to do.
    column["n_distinct"] = 22
    column["n_distinct_folded"] = 22
    column["n_distinct_values"] = 11
    built["why"] = (
        "G6.5a's reaches taken walk by walk (plan P4-D183): thirty-three "
        "cells of the whole numbers 100 to 110, twenty-two strata publishing "
        "eleven different values. Every stratum is walked inside its own "
        "share before any is walked on its neighbours' ground, so the "
        "thirteenth stratum takes 105 inside its share. The mutant takes the "
        "three reaches stratum by stratum, as the walk did before, and the "
        "tenth stratum walks out of its share onto 105 above the 104 after "
        "it, and the cells move."
    )
    return built


def _truth_values_written():
    """A workbook column of free text writes its truth values (plan P4-D198).

    Thirty-two cells of free text: twenty-one one-letter codes and eleven
    truth values, which the column's workbook census counts as `boolean
    11`. The packing gives the eleven-row group the text class in the code
    alphabet, so it is spelled `TRUE` and held at four characters before
    the walk spends the average; the shortest length is one letter and the
    longest a made-up word of four.
    """
    length, claims = {}, {}
    for name, text in (("mean", "2.125"), ("p50", "1")):
        field, claim = nearest_field(text)
        length[name] = field
        claims[("column", "length", name)] = claim
    length["min"] = 1
    length["max"] = 4
    words = {"min": 1, "max": 1}
    field, claim = nearest_field("1")
    words["mean"] = field
    claims[("column", "words", "mean")] = claim
    column = _universal(
        "column_1", "free_text", "text", "data", "ok",
        n_present=32, n_missing=0, n_distinct=22, n_distinct_folded=22,
        n_numeric=0, n_not_numeric=32, n_out_of_range=0, n_contradictory=0,
        length=length, words=words,
        n_all_digits=0, n_code_alphabet=32,
        n_distinct_by_occurrences={"01": 21, "11": 1},
        shape_forms={"(withheld)": 32},
    )
    return {
        "why": "method section G9.5 as plan P4-D198 left it: a workbook column "
        "of free text whose census counts eleven truth values, and the "
        "group of eleven the packing puts in the code alphabet as text is "
        "spelled `TRUE` at its own four characters, so the writer gives those "
        "cells the boolean class. The mutant spells no truth value, and the "
        "group is a made-up word.",
        "column": column,
        "rows": 32,
        "identifier_declared": False,
        "claims": claims,
        "workbook_truths": 11,
    }


def _identifier_unnamed_partners():
    column = _universal(
        "column_1", "identifier", "code", "identifier", "ok",
        n_present=44, n_missing=0, n_distinct=44, n_distinct_folded=33,
        n_numeric=0, n_not_numeric=44, n_out_of_range=0, n_contradictory=0,
        min_length=4, max_length=4, all_whole_numbers=False,
        n_all_digits=0, n_code_alphabet=44,
        n_distinct_by_occurrences={"1": 44},
        # EVERY CELL WEARS A NAMED LAYOUT, so the census names no layout
        # for none of them, and a partner of a `@-%%` identity -- `&-%%`
        # or an edge-spaced member, neither named -- has no cell to take.
        layout_forms={"&%%%": 11, "@%%%": 22, "@-%%": 11},
    )
    return {
        "why": "a declared identifier whose census names a layout for every "
        "cell (G9.6, plan P4-D196), `{\"&%%%\": 11, \"@%%%\": 22, "
        "\"@-%%\": 11}` over thirty-three identities and eleven fold-collision "
        "partners. The cells the census names no layout for are a quota of "
        "nought, so an identity owed a partner takes no layout whose partner "
        "wears none, and every partner wears `&%%%`. This case's mutant "
        "withdraws that quota, an identity owed a partner takes `@-%%`, and "
        "the check of 7.12 stops the oracle.",
        "column": column,
        "rows": 44,
        "identifier_declared": True,
    }


def _grouped_thousands_signed():
    ladder, ladder_claims, rungs, finer = _ladder_fields({
        "min": "-1080.4", "p01": "-1075.2", "p05": "-1050.6", "p10": "-1008.4",
        "p25": "-981.2", "p50": "-20.5", "p75": "1050.3", "p90": "1081.84",
        "p95": "1086.88", "p99": "1095.544", "max": "1096.6",
    })
    claims = {("column",) + key: value for key, value in ladder_claims.items()}
    moments = {}
    for name, text in (("mean", "300.5"), ("std", "990.2"), ("skew", "-0.6"),
                       ("kurtosis", "1.4"), ("numeric_share", "1")):
        field, claim = nearest_field(text)
        moments[name] = field
        claims[("column", name)] = claim
    column = _universal(
        "column_1", "continuous", "continuous", "data", "ok",
        n_present=33, n_missing=0, n_distinct=33, n_distinct_folded=33,
        n_distinct_values=33,
        n_numeric=33, n_not_numeric=0, n_out_of_range=0, n_contradictory=0,
        percentiles=ladder, percentiles_between=finer, std_unrepresentable=False,
        n_zero=0, n_negative=17, n_negative_unrepresentable=0,
        n_used_in_statistics=33, n_left_out_of_statistics=0,
        integer_valued=False, n_rows=33, numeric_styles={"decimal": 33},
        mode=None, mode_count=0, fraction_widths={"1": 33}, pad_widths={},
        field_widths={}, group_separator=",",
        # TWENTY-TWO OF THE THIRTY-THREE amounts reach a thousand in size,
        # refunds among them, and eleven are bare.
        thousands_marks={",": 22},
        **moments,
    )
    return {
        "why": "G6.1's census of marks held at a thousand on a column with "
        "refunds (plan P4-D194): thirty-three amounts at one place between "
        "-1080.4 and 1096.6, seventeen of them negative, twenty-two reaching "
        "a thousand in size and written with a comma. The positive side moves "
        "the strata just below a thousand up to it and still leaves one cell "
        "short, so the count is taken again and the negative stratum just "
        "above minus a thousand moves below it. The mutant withdraws the "
        "negative side, and twenty-one cells wear a comma.",
        "column": column,
        "rows": 33,
        "identifier_declared": False,
        "rungs": rungs,
        "claims": claims,
    }


def _twice_written_column(rung_texts, moment_texts, rows, spellings, numbers,
                          plain, mode_count):
    """One column of readings at one place, some whole ones written bare.

    Shared by the two cases of plan P4-D193: a reading written `4` in most
    cells and `4.0` in a few, so the column publishes one more spelling
    than it has numbers.
    """
    ladder, ladder_claims, rungs, finer = _ladder_fields(rung_texts)
    claims = {("column",) + key: value for key, value in ladder_claims.items()}
    moments = {}
    for name, text in moment_texts + (("numeric_share", "1"),):
        field, claim = nearest_field(text)
        moments[name] = field
        claims[("column", name)] = claim
    column = _universal(
        "column_1", "continuous", "continuous", "data", "ok",
        n_present=rows, n_missing=0, n_distinct=spellings,
        n_distinct_folded=spellings, n_distinct_values=numbers,
        n_numeric=rows, n_not_numeric=0, n_out_of_range=0, n_contradictory=0,
        percentiles=ladder, percentiles_between=finer, std_unrepresentable=False,
        n_zero=0, n_negative=0, n_negative_unrepresentable=0,
        n_used_in_statistics=rows, n_left_out_of_statistics=0,
        integer_valued=False, n_rows=rows,
        numeric_styles={"decimal": rows - plain, "plain": plain},
        mode_count=mode_count, fraction_widths={"1": rows - plain},
        pad_widths={}, field_widths={"1": plain},
        **moments,
    )
    return column, rungs, claims


def _twice_written_filled():
    column, rungs, claims = _twice_written_column(
        {
            "min": "3.5", "p01": "3.5", "p05": "3.7", "p10": "3.7",
            "p25": "3.8", "p50": "3.9", "p75": "4.0", "p90": "4.1",
            "p95": "4.155", "p99": "4.211", "max": "4.3",
        },
        (("mean", "3.897777777777778"), ("std", "0.15720721155784406"),
         ("skew", "-0.03296493326801872"), ("kurtosis", "3.0402915149762997"),
         ("mode", "3.9")),
        90, 10, 9, 14, 29,
    )
    return {
        "why": "G6.5a's whole number written two ways, the fill (plan "
        "P4-D193): ninety readings at one place between 3.5 and 4.3, "
        "fourteen whole ones written bare, publishing ten spellings of nine "
        "numbers. The grid from 3.5 to 4.3 holds exactly nine tenths, so the "
        "ten strata take them in order with the whole 4.0 taken twice, and "
        "the column is written `4` and `4.0`. The mutant withdraws the rule, "
        "and the walk leaves two strata on a tenth that is not whole.",
        "column": column,
        "rows": 90,
        "identifier_declared": False,
        "rungs": rungs,
        "claims": claims,
    }


def _twice_written_merged():
    column, rungs, claims = _twice_written_column(
        {
            "min": "3.3", "p01": "3.338", "p05": "3.6950000000000003",
            "p10": "3.7", "p25": "3.8", "p50": "4.0", "p75": "4.2",
            "p90": "4.3", "p95": "4.4", "p99": "4.481", "max": "4.5",
        },
        (("mean", "4.004166666666666"), ("std", "0.24301877139286943"),
         ("skew", "-0.19688422880912423"), ("kurtosis", "2.8823084380726773"),
         ("mode", "4.0")),
        120, 13, 12, 21, 22,
    )
    return {
        "why": "G6.5a's whole number written two ways, the merge (plan "
        "P4-D193): a hundred and twenty readings at one place between 3.3 "
        "and 4.5, twenty-one whole ones written bare, publishing thirteen "
        "spellings of twelve numbers. The walk leaves thirteen numbers, one "
        "on every stratum, so the stratum beside the whole 4.0 nearest to it "
        "takes 4.0 and the column is written `4` and `4.0`. The mutant "
        "withdraws the rule, and the twin holds thirteen numbers.",
        "column": column,
        "rows": 120,
        "identifier_declared": False,
        "rungs": rungs,
        "claims": claims,
    }


def _grouped_thousands():
    ladder, ladder_claims, rungs, finer = _ladder_fields({
        "min": "920.1", "p01": "929.7", "p05": "951.12", "p10": "952.96",
        "p25": "984.1", "p50": "1022.2", "p75": "1068.9", "p90": "1081.84",
        "p95": "1086.88", "p99": "1095.544", "max": "1096.6",
    })
    claims = {("column",) + key: value for key, value in ladder_claims.items()}
    moments = {}
    for name, text in (("mean", "1021.1696969696969"),
                       ("std", "50.85734635261952"),
                       ("skew", "-0.1575495088527798"),
                       ("kurtosis", "1.7838152479174922"),
                       ("numeric_share", "1")):
        field, claim = nearest_field(text)
        moments[name] = field
        claims[("column", name)] = claim
    column = _universal(
        "column_1", "continuous", "continuous", "data", "ok",
        n_present=33, n_missing=0, n_distinct=33, n_distinct_folded=33,
        n_distinct_values=33,
        n_numeric=33, n_not_numeric=0, n_out_of_range=0, n_contradictory=0,
        percentiles=ladder, percentiles_between=finer, std_unrepresentable=False,
        n_zero=0, n_negative=0, n_negative_unrepresentable=0,
        n_used_in_statistics=33, n_left_out_of_statistics=0,
        integer_valued=False, n_rows=33, numeric_styles={"decimal": 33},
        mode=None, mode_count=0, fraction_widths={"1": 33}, pad_widths={},
        field_widths={}, group_separator=",",
        # TWENTY OF THE THIRTY-THREE readings reach a thousand, and every
        # one of them was written with a comma.
        thousands_marks={",": 20},
        **moments,
    )
    return {
        "why": "G6.1's census of marks held at a thousand (plan P4-D185): "
        "thirty-three different readings at one place between 920.1 and "
        "1096.6, twenty of them a thousand or more and written with a comma. "
        "The ladder puts one stratum fewer at a thousand or more, so the "
        "highest stratum below a thousand takes the lowest free tenth of a "
        "thousand or more, below the stratum above it, and twenty cells are "
        "written with a comma. The mutant withdraws the rule, and the "
        "stratum stays below a thousand and bare.",
        "column": column,
        "rows": 33,
        "identifier_declared": False,
        "rungs": rungs,
        "claims": claims,
    }


def _saturated_integers():
    ladder, ladder_claims, rungs, finer = _ladder_fields({
        "min": "1", "p01": "1.32", "p05": "2.6", "p10": "4.2",
        "p25": "9", "p50": "11", "p75": "14", "p90": "18.8",
        "p95": "20.4", "p99": "21.68", "max": "22",
    })
    claims = {
        ("column",) + key: value
        for key, value in ladder_claims.items()
    }
    moments = {}
    for name, text in (("mean", "11.333333333333334"),
                       ("std", "5.26584909265986"),
                       ("skew", "0.09615802208472209"),
                       ("kurtosis", "2.687623796188785"),
                       ("numeric_share", "1"), ("mode", "11")):
        field, claim = nearest_field(text)
        moments[name] = field
        claims[("column", name)] = claim
    column = _universal(
        "column_1", "count", "count", "data", "ok",
        n_present=33, n_missing=0, n_distinct=22, n_distinct_folded=22,
        n_distinct_values=22,
        n_numeric=33, n_not_numeric=0, n_out_of_range=0, n_contradictory=0,
        percentiles=ladder, percentiles_between=finer, std_unrepresentable=False,
        n_zero=0, n_negative=0, n_negative_unrepresentable=0,
        n_used_in_statistics=33, n_left_out_of_statistics=0,
        integer_valued=True, n_rows=33, numeric_styles={"plain": 33},
        mode_count=12,
        # THE WHOLE NUMBERS ONE TO TWENTY-TWO, each once, and eleven more
        # cells holding eleven: twenty-four cells two figures wide and nine
        # held back below the floor.
        field_widths={"2": 24, "(withheld)": 9},
        **moments,
    )
    return {
        "why": "G6.5a's saturated grid (plan P4-D147). The column is on the "
        "integer grid, publishes twenty-two different numbers, and its "
        "published ends are one and twenty-two -- exactly twenty-two "
        "integers -- so there is no spare grid point and the strata are "
        "given those integers in order, each once: every whole number from "
        "one to twenty-two is written. The mutant withdraws the fill and "
        "runs the walk alone, which leaves twenty-one different numbers, "
        "because every stratum that moves lands on a point another stratum "
        "still needs.",
        "column": column,
        "rows": 33,
        "identifier_declared": False,
        "rungs": rungs,
        "claims": claims,
    }


def _spread_conventions():
    ladder, ladder_claims, rungs, finer = _ladder_fields({
        "min": "-1021", "p01": "-1020.79", "p05": "-1019.95",
        "p10": "-1018.9", "p25": "-1015.75", "p50": "-1010.5",
        "p75": "-1005.25", "p90": "-1002.1", "p95": "-1001.05",
        "p99": "-1000.21", "max": "-1000",
    })
    claims = {("column",) + key: value for key, value in ladder_claims.items()}
    moments = {}
    for name, text in (("mean", "-1010.5"),
                       ("std", "6.493586579592719"),
                       ("skew", "0"),
                       ("kurtosis", "1.795031055900621"),
                       ("numeric_share", "1")):
        field, claim = nearest_field(text)
        moments[name] = field
        claims[("column", name)] = claim
    column = _universal(
        "column_1", "continuous", "continuous", "data", "ok",
        n_present=22, n_missing=0, n_distinct=22, n_distinct_folded=22,
        n_distinct_values=22,
        n_numeric=22, n_not_numeric=0, n_out_of_range=0, n_contradictory=0,
        percentiles=ladder, percentiles_between=finer, std_unrepresentable=False,
        n_zero=0, n_negative=22, n_negative_unrepresentable=0,
        n_used_in_statistics=22, n_left_out_of_statistics=0,
        integer_valued=True, n_rows=22, numeric_styles={"plain": 22},
        mode=None, mode_count=0, pad_widths={}, fraction_widths={},
        field_widths={"4": 22},
        # THE WHOLE NUMBERS FROM MINUS 1,021 TO MINUS 1,000, each once:
        # eleven grouped with a comma and eleven bare, eleven in brackets
        # and eleven with a minus -- every count and every complement the
        # census floor.
        group_separator=",", thousands_marks={",": 11},
        negative_form="minus",
        negative_notations={"brackets": 11, "minus": 11},
        **moments,
    )
    return {
        "why": "G6.1's spread of the two censuses of conventions (plan "
        "P4-D149). The column holds every whole number from minus one "
        "thousand and twenty-one to minus one thousand once, so the saturated "
        "fill of G6.5a stands its cells in ascending order before either "
        "census is spent. Each named count is taken by the spread rule the "
        "plus sign uses, over the cells no earlier count took, and not from "
        "the first cell upward: the brackets, the minus signs, the grouped "
        "cells and the bare ones each fall across the whole range of values "
        "rather than on its most negative or its least negative half. The "
        "mutant restores the first version's walk, and the eleven most "
        "negative numbers are the ones in brackets and the ones grouped.",
        "column": column,
        "rows": 22,
        "identifier_declared": False,
        "rungs": rungs,
        "claims": claims,
    }


def _signed_pads():
    ladder, ladder_claims, rungs, finer = _ladder_fields({
        "min": "100", "p01": "100", "p05": "100.5", "p10": "101.25",
        "p25": "102", "p50": "105", "p75": "108", "p90": "109.25",
        "p95": "110", "p99": "110", "max": "110",
    })
    claims = {("column",) + key: value for key, value in ladder_claims.items()}
    moments = {}
    for name, text in (("mean", "105"),
                       ("std", "3.2113081446662823"),
                       ("skew", "0"),
                       ("kurtosis", "1.78"),
                       ("numeric_share", "1")):
        field, claim = nearest_field(text)
        moments[name] = field
        claims[("column", name)] = claim
    column = _universal(
        "column_1", "count", "count", "data", "ok",
        n_present=33, n_missing=0, n_distinct=20, n_distinct_folded=20,
        n_distinct_values=10,
        n_numeric=33, n_not_numeric=0, n_out_of_range=0, n_contradictory=0,
        percentiles=ladder, percentiles_between=finer, std_unrepresentable=False,
        n_zero=0, n_negative=0, n_negative_unrepresentable=0,
        n_used_in_statistics=33, n_left_out_of_statistics=0,
        integer_valued=True, n_rows=33,
        # TEN WHOLE NUMBERS FROM 100 TO 110, written thirty-three times:
        # twenty-two as `+0100` and eleven as `0100`, and every value in
        # both padded forms at one field width of four figures.
        numeric_styles={"leading_plus": 22, "leading_zero": 11},
        mode=None, mode_count=0, fraction_widths={},
        pad_widths={"4": 33}, field_widths={"4": 33},
        **moments,
    )
    return {
        "why": "G6.5's padded sign exchange (plan P4-D145, as amended). Every cell is "
        "padded to a named field width of four figures, so no cell can spend "
        "a zero to reach the twenty spellings the column publishes, and "
        "the style walk leaves most of its ten values wearing one of the "
        "two padded forms. Cells written with a plus trade forms with cells "
        "written with a zero at the same width, first between values each "
        "wearing only one form and then with values wearing both, so every "
        "count of forms and widths is unchanged and more values are written "
        "both ways. The mutant withdraws the exchange, and the column comes "
        "back with fewer spellings.",
        "column": column,
        "rows": 33,
        "identifier_declared": False,
        "rungs": rungs,
        "claims": claims,
    }


def _apostrophe_minus_sign():
    column, rungs, claims = _flat_numbers(
        "-12345.5", 11,
        n_missing=0, n_distinct=2, n_distinct_folded=2, n_negative=11,
        numeric_styles={"decimal": 11},
        fraction_widths={"1": 11}, pad_widths={}, field_widths={},
        group_separator="'", negative_form="minus_sign",
    )
    return {
        "why": "an apostrophe between thousands and the minus sign U+2212 for "
        "a negative number, two spellings landing 2b.2 publishes that no "
        "frozen case reached while every branch case shared one file. Every "
        "cell is minus twelve thousand three hundred and forty-five and a "
        "half, written `−12'345.5`; one cell spends a zero and is written "
        "`−012345.5`, with the sign in front of the zeros and no mark. "
        "This case's mutant withdraws the notation, and every cell is written "
        "with a hyphen-minus instead.",
        "column": column,
        "rows": 11,
        "identifier_declared": False,
        "rungs": rungs,
        "claims": claims,
    }


def _quoted_trailing_minus():
    column, rungs, claims = _flat_numbers(
        "-12345.5", 11,
        n_missing=0, n_distinct=2, n_distinct_folded=2, n_negative=11,
        numeric_styles={"decimal": 11},
        fraction_widths={"1": 11}, pad_widths={}, field_widths={},
        group_separator="’", negative_form="trailing_minus",
    )
    return {
        "why": "the right single quotation mark U+2019 between thousands and a "
        "minus written after the figures, which a trailing minus is only "
        "where the figures carry a decimal point. Every cell is minus twelve "
        "thousand three hundred and forty-five and a half, written "
        "`12’345.5-`; one cell spends a zero and is written `012345.5-`, "
        "with no mark. This case's mutant writes every mark as a comma, and "
        "every cell that carries one moves.",
        "column": column,
        "rows": 11,
        "identifier_declared": False,
        "rungs": rungs,
        "claims": claims,
    }


def _spaced_decimal_comma():
    column, rungs, claims = _flat_numbers(
        "42037.34", 13,
        n_present=11, n_missing=2,
        n_distinct=2, n_distinct_folded=2, n_negative=0,
        numeric_styles={"decimal": 11},
        fraction_widths={"2": 11}, pad_widths={}, field_widths={},
        group_separator=" ",
    )
    return {
        "why": "a no-break space U+00A0 between thousands on a column DECLARED "
        "to write its decimals with a comma, which this case's own test "
        "settings name: the mark is neither decimal mark, so it is written as "
        "published and only the point becomes a comma, `42 037,34`. One "
        "cell spends a zero and carries no mark, `042037,34`, and the two "
        "absent cells are written empty. This case's mutant withdraws the "
        "exchange of plan P4-D26, the rule `grouped_decimal_comma` pins by "
        "its mark instead, and every present cell moves.",
        "column": column,
        "rows": 13,
        "identifier_declared": False,
        "decimal_comma_declared": True,
        "rungs": rungs,
        "claims": claims,
    }


def _narrow_spaced():
    column, rungs, claims = _flat_numbers(
        "12345.5", 11,
        n_missing=0, n_distinct=2, n_distinct_folded=2, n_negative=0,
        numeric_styles={"decimal": 11},
        fraction_widths={"1": 11}, pad_widths={}, field_widths={},
        group_separator=" ",
    )
    return {
        "why": "a narrow no-break space U+202F between thousands. Every cell is "
        "twelve thousand three hundred and forty-five and a half, written "
        "`12 345.5`; one cell spends a zero and is written `012345.5`, "
        "with no mark. This case's mutant writes every mark as a comma, and "
        "every cell that carries one moves.",
        "column": column,
        "rows": 11,
        "identifier_declared": False,
        "rungs": rungs,
        "claims": claims,
    }


def _thin_spaced():
    column, rungs, claims = _flat_numbers(
        "12345.5", 11,
        n_missing=0, n_distinct=2, n_distinct_folded=2, n_negative=0,
        numeric_styles={"decimal": 11},
        fraction_widths={"1": 11}, pad_widths={}, field_widths={},
        group_separator=" ",
    )
    return {
        "why": "a thin space U+2009 between thousands, the last mark landing "
        "2b.2's repair added. Every cell is twelve thousand three hundred and "
        "forty-five and a half, written `12 345.5`; one cell spends a "
        "zero and is written `012345.5`, with no mark. This case's mutant "
        "writes every mark as a comma, and every cell that carries one moves.",
        "column": column,
        "rows": 11,
        "identifier_declared": False,
        "rungs": rungs,
        "claims": claims,
    }


# ---------------------------------------------------------------------
# THE DOCUMENT TRANSFORMS: the written form (G2), the arrangement of the
# rows (G2.1) and the twin of a workbook (G2.2)
#
# Everything above this line answers the question "what does ONE COLUMN
# hold".  Everything below answers "what does the FILE look like", which
# is a different transform with different inputs: no word is drawn here
# at all, and the inputs are the description's own `source.dialect` and
# `source.workbook` blocks rather than a column block.
#
# WHY THESE EXIST (landing 2b.17).  Landings 2b.9, 2b.10 and 2b.11 built
# the written form, the row arrangement and the workbook writer, and left
# all three with NO second implementation: `grep` for `twin_text`,
# `arranged`, `row_order` or `workbook` in this file found nothing, so
# the only check on any of them was a round trip through the very code
# they check.  The method document stated none of the workbook writer's
# rules either, which is why G2.2 had to be written before this could be.
#
# Each rule below is written from the METHOD'S STATEMENT of it and not
# from the shipped code, which is the whole of what this file is for.
# Where a rule the method states reaches further than the frozen cases
# do, the mirror REFUSES rather than guessing: a mirror that quietly
# invents a reading is worse than one that stops, because it agrees with
# nothing and nobody notices.
# ---------------------------------------------------------------------

DOC_QUOTE = '"'
DOC_BACKSLASH = "\\"
DOC_BYTE_ORDER_MARK = "﻿"
DOC_END_OF_FILE = "\x1a"
DOC_SPACE = " "
DOC_TAB = "\t"
DOC_CR = "\r"
DOC_LF = "\n"

# G2: each line takes the next ending of `line_endings`, in file order.
DOC_ENDING_TEXT = {"lf": "\n", "crlf": "\r\n", "cr": "\r", "crcrlf": "\r\r\n"}
DOC_ENDING_ORDER = ("lf", "crlf", "cr", "crcrlf")

# G2: quoting is per column and per cell class, in this order.
DOC_CELL_CLASSES = ("absent", "empty", "number", "text")
DOC_QUOTE_NEEDED = "needed"
DOC_QUOTE_BARE = "bare"
DOC_QUOTE_ALWAYS = "always"

# G2: the four delimiters a description may publish, in the order the
# reading rule below breaks a tie with.
DOC_DELIMITERS = (",", ";", "\t", "|")
DOC_ESCAPE_DOUBLED = "doubled"
DOC_ESCAPE_BACKSLASH = "backslash"
DOC_ESCAPES = (DOC_ESCAPE_DOUBLED, DOC_ESCAPE_BACKSLASH)

# G2 and contract FD11: the shapes a line before the table is published
# as, and the two neutral words a withheld line is written as.
DOC_PREAMBLE_BLANK = "blank"
DOC_PREAMBLE_COMMENT = "comment"
DOC_PREAMBLE_TEXT = "text"
DOC_WITHHELD_LINE = "withheld line"

# How many records the reading rule looks at.
DOC_SAMPLE_RECORDS = 400

# The marks a cell of these cases may hold beside letters, digits and
# spaces.  The class of a cell decides which quoting rule it takes, and
# a class read wrongly writes the wrong bytes -- so this mirror reads
# only cells it can place with certainty and stops on any other.  The
# question mark and the exclamation mark joined at plan P4-D173, because
# five of contract 5.4.1's spellings of absence are written with them and
# a mirror that stopped on `?` could not be shown reading it as text.
DOC_TEXT_MARKS = "-_.,;|/#()\"'+:%&*[]@?!"

# The spellings read as holding no value, as contract section 5.4.1
# lists them: seventeen compared after trimming and a case fold, and one
# compared byte for byte.  A cell whose text is one of them is ABSENT and
# not text, which is a different quoting rule (method G2's quoting row).
#
# THE WHOLE LIST AND NOT A SAMPLE OF IT (plan P4-D173).  This mirror held
# seven spellings of its own vocabulary, so `-`, `?`, `#N/A` and a cell of
# spaces were classed TEXT here and ABSENT by the product: a column whose
# absent and text cells take different quoting rules was written two ways
# with nothing stopping, the same silent misclassification as `1,234`.
DOC_NOTHING_SPELLINGS_FOLDED = (
    "", "-", "--", ".", "?", "n/a", "na", "nan", "none", "null",
    "#DIV/0!", "#N/A", "#NAME?", "#NULL!", "#NUM!", "#REF!", "#VALUE!",
)
DOC_NOTHING_SPELLINGS_EXACT = ("NaT",)

# The marks a number may be written with beyond the narrow grammar's:
# figures, signs, a point, a comma, an apostrophe, brackets, a percent
# and an exponent mark.  A cell of these and figures alone is refused by
# `written_cell_class` rather than classed (plan P4-D173).
DOC_NUMBER_MARKS = "0123456789+-.,'()%eE"


def doc_is_a_plain_number(text):
    """Whether the text is a plain number: sign, figures, point, exponent.

    The narrow grammar, stated rather than assumed: an optional sign,
    figures, an optional point with figures on one side or both, and an
    optional exponent with an optional sign.  A grouped number, a
    decimal comma, a bracketed negative and a trailing minus are NOT
    plain numbers here -- they are read as numbers by the profiler's own
    grammar, and a case whose cells need that reading is refused below
    rather than classed by a guess.

    AN EXPONENT MARK WITH NO FIGURES AFTER IT IS NOT AN EXPONENT (plan
    P4-D173). `1e` was read here as the number 1, because an empty
    exponent was skipped rather than refused; the profiler reads it as
    text, so the two wrote a different quoting for the same cell.
    """
    body = text
    if body[:1] in ("-", "+"):
        body = body[1:]
    mantissa = body
    exponent = ""
    marked = False
    for marker in ("e", "E"):
        place = mantissa.find(marker)
        if place >= 0:
            exponent = mantissa[place + 1 :]
            mantissa = mantissa[:place]
            marked = True
            break
    if marked:
        if exponent[:1] in ("-", "+"):
            exponent = exponent[1:]
        if not exponent or not all(mark in "0123456789" for mark in exponent):
            return False
    point = mantissa.find(".")
    if point >= 0:
        whole = mantissa[:point]
        fraction = mantissa[point + 1 :]
        if not whole and not fraction:
            return False
        for piece in (whole, fraction):
            if piece and not all(mark in "0123456789" for mark in piece):
                return False
        return True
    if not mantissa:
        return False
    return all(mark in "0123456789" for mark in mantissa)


def doc_reads_as_nothing(text):
    """Whether the cell's text is one of the spellings meaning no value.

    Contract 5.4.1's two rules: the exact member matches the cell byte for
    byte, and every other member matches after both are trimmed and
    case-folded.
    """
    if text in DOC_NOTHING_SPELLINGS_EXACT:
        return True
    body = text.strip().casefold()
    for spelling in DOC_NOTHING_SPELLINGS_FOLDED:
        if body == spelling.strip().casefold():
            return True
    return False


def written_cell_class(cell):
    """Which of G2's four cell classes one cell belongs to.

    A column whose four quoting rules agree needs no class at all, which
    is why an ordinary twin never reaches this.  Where they differ the
    class decides the bytes, so this stops on a cell it cannot place.
    """
    if cell == "":
        return "empty"
    if doc_reads_as_nothing(cell):
        return "absent"
    if doc_is_a_plain_number(cell):
        return "number"
    # A CELL THE PROFILER'S WIDER GRAMMAR MAY READ AS A NUMBER IS REFUSED,
    # NOT CLASSED AS TEXT (plan P4-D173). The profiler reads `1,234`,
    # `(12)`, ` 12` and `1 234` as numbers; the narrow grammar above does
    # not, and this used to fall through to `text` -- so a form quoting
    # numbers always and text bare wrote `"1,234";A` in the product and
    # `1,234;A` here, with nothing stopping. A cell holding a figure and
    # nothing but the marks a number can be written with is outside the
    # reading this mirror states, and it stops.
    if any(mark in "0123456789" for mark in cell) and all(
        mark in DOC_NUMBER_MARKS or mark.isspace() for mark in cell
    ):
        raise AssertionError(
            f"this oracle will not class the cell {cell!r}: it holds a "
            "figure and only the marks a number is written with, so the "
            "profiler's own number grammar may read it as a number while "
            "the narrow grammar method section G2's per-class quoting is "
            "mirrored under does not. Freeze a cell the narrow grammar "
            "reads, or state the wider one."
        )
    for mark in cell:
        if mark.isalpha() or mark.isdigit():
            continue
        if mark == DOC_SPACE or mark in DOC_TEXT_MARKS:
            continue
        raise AssertionError(
            f"this oracle will not class the cell {cell!r}: its characters "
            "are outside the narrow reading method section G2's per-class "
            "quoting is mirrored under here, and a class read wrongly "
            "writes the wrong bytes. State the reading, or freeze a cell "
            "the reading covers."
        )
    return "text"


def written_needs_quoting(cell, delimiter, escape, initial_space, alone):
    """G2's `needed` rule: quoted when and only when it has to be.

    ``alone`` says the cell is the only one on its line, where an empty
    cell written bare would be a blank line and not a record -- which is
    G2's canonical quoting exception 2.
    """
    if not cell:
        return alone
    for mark in (delimiter, DOC_QUOTE, DOC_CR, DOC_LF):
        if mark and mark in cell:
            return True
    if escape == DOC_ESCAPE_BACKSLASH and DOC_BACKSLASH in cell:
        return True
    return initial_space and cell[:1] == DOC_SPACE


def written_must_quote(cell, delimiter, escape, initial_space, alone):
    """G2's `bare` rule: quoted only where it could not be read back."""
    if not cell:
        return alone
    for mark in (delimiter, DOC_CR, DOC_LF):
        if mark and mark in cell:
            return True
    if cell[:1] == DOC_QUOTE:
        return True
    if escape == DOC_ESCAPE_BACKSLASH and DOC_BACKSLASH in cell:
        return True
    return initial_space and cell[:1] == DOC_SPACE


def written_field(cell, rule, form, alone, marked=False):
    """One cell as the twin writes it, under one quoting rule of the form.

    `mixed` is written `needed` (G2), which is the last branch here: a
    rule that is neither `always` nor `bare` quotes when and only when
    it must.
    """
    delimiter = form["delimiter"]
    escape = form["escape"]
    initial_space = form["initial_space"]
    if rule == DOC_QUOTE_ALWAYS:
        quote = True
    elif rule == DOC_QUOTE_BARE:
        quote = marked or written_must_quote(
            cell, delimiter, escape, initial_space, alone
        )
    else:
        quote = marked or written_needs_quoting(
            cell, delimiter, escape, initial_space, alone
        )
    if not quote:
        return cell
    body = ""
    for mark in cell:
        if escape == DOC_ESCAPE_BACKSLASH:
            if mark == DOC_QUOTE or mark == DOC_BACKSLASH:
                body = body + DOC_BACKSLASH
        elif mark == DOC_QUOTE:
            body = body + DOC_QUOTE
        body = body + mark
    return DOC_QUOTE + body + DOC_QUOTE


def quoting_rule_for(column, cell):
    """The quoting rule a column applies to one cell (G2, per class)."""
    rules = column["quoting"]
    every = [rules[name] for name in DOC_CELL_CLASSES]
    if every[0] == every[1] == every[2] == every[3]:
        return every[0]
    return rules[written_cell_class(cell)]


def padded_cell(cell, column):
    """A cell padded with spaces to its column's width, where shorter (G2)."""
    pad = column["pad"]
    if pad is None or len(cell) >= pad["width"]:
        return cell
    spaces = DOC_SPACE * (pad["width"] - len(cell))
    if pad["side"] == "left":
        return spaces + cell
    return cell + spaces


def joined_fields(parts, form):
    """Fields put on one line with the form's delimiter (G2)."""
    separator = form["delimiter"] + (DOC_SPACE if form["initial_space"] else "")
    line = ""
    for index in range(len(parts)):
        if index:
            line = line + separator
        line = line + parts[index]
    return line


def header_written(names, form):
    """The header record as the twin writes it, without its line ending.

    G2's canonical quoting exception 1: a first column name beginning
    with the byte-order mark is ALWAYS quoted.  Written bare it would
    begin the file with that mark's own bytes, which the reader then
    consumes, silently renaming the column.
    """
    shown = list(names)
    for written in form["written_names"]:
        if 1 <= written["position"] <= len(shown):
            shown[written["position"] - 1] = written["text"]
    alone = len(shown) == 1
    parts = []
    for index in range(len(shown)):
        cell = shown[index]
        marked = index == 0 and cell[:1] == DOC_BYTE_ORDER_MARK
        parts += [written_field(cell, form["header_quoting"], form, alone, marked)]
    line = joined_fields(parts, form)
    if form["trailing_delimiter"]["header"]:
        line = line + form["delimiter"]
    return line


def record_written(cells, form):
    """One data record as the twin writes it, without its line ending (G2)."""
    width = len(cells)
    kept = width
    if form["short_rows"]:
        while kept > 1 and cells[kept - 1] == "":
            kept = kept - 1
    alone = width == 1
    parts = []
    for index in range(kept):
        column = form["columns"][index]
        cell = padded_cell(cells[index], column)
        parts += [written_field(cell, quoting_rule_for(column, cell), form, alone)]
    line = joined_fields(parts, form)
    if form["trailing_delimiter"]["rows"]:
        line = line + form["delimiter"]
    return line


def mark_breaks_a_line(mark, delimiter):
    """Whether a published mark would stop its stand-in being one record.

    Contract FD11, plan P4-D83.  A quote character opens a field nothing
    closes; the delimiter cuts the stand-in into fields a reader takes
    for the table's header.  Either leaves a twin that is not the file
    the description published.
    """
    if DOC_QUOTE in mark:
        return True
    return bool(delimiter) and delimiter in mark


def line_shape(line):
    """One line before the table as its kind and its mark, never its text.

    G2 and contract 4.3a: a line holding nothing, or nothing but spaces
    and tabs, is BLANK and its mark is that whitespace; a line beginning
    with anything that is not a letter or a digit is a COMMENT whose
    mark is that opening punctuation; anything else is TEXT, of which
    nothing whatever is published.
    """
    if not line or all(mark in (DOC_SPACE, DOC_TAB) for mark in line):
        return (DOC_PREAMBLE_BLANK, line)
    kept = ""
    for mark in line:
        if mark.isalpha() or mark.isdigit():
            break
        kept = kept + mark
    if kept:
        return (DOC_PREAMBLE_COMMENT, kept)
    return (DOC_PREAMBLE_TEXT, "")


def writable_mark(kind, mark, delimiter):
    """A line's shape narrowed to a mark the twin can write (plan P4-D83).

    The mark is written into the twin ahead of the stand-in, so a mark
    that cannot be written leaves a twin that is not a file.  The mark
    therefore ends before the first quote character or delimiter, and a
    line whose punctuation BEGINS with one is a line of TEXT, whose
    stand-in is the two neutral words -- which every reader reads as one
    field.  A blank line is untouched: its mark is spaces and tabs,
    which hold neither character.
    """
    if kind == DOC_PREAMBLE_BLANK or not mark_breaks_a_line(mark, delimiter):
        return (kind, mark)
    kept = ""
    for mark_character in mark:
        if mark_character == DOC_QUOTE or (
            delimiter and mark_character == delimiter
        ):
            break
        kept = kept + mark_character
    if kept:
        return (DOC_PREAMBLE_COMMENT, kept)
    return (DOC_PREAMBLE_TEXT, "")


def preamble_runs_of(lines, delimiter):
    """The lines before the table, run-length encoded by their shape.

    Contract FD11: seventeen leading blank lines are seventeen lines of
    ONE shape, and are published as one run of seventeen.
    """
    runs = []
    for line in lines:
        kind, mark = writable_mark(*line_shape(line), delimiter)
        last = len(runs) - 1
        if last >= 0 and runs[last]["kind"] == kind and runs[last]["mark"] == mark:
            runs[last] = {
                "kind": kind,
                "lines": runs[last]["lines"] + 1,
                "mark": mark,
            }
            continue
        runs += [{"kind": kind, "lines": 1, "mark": mark}]
    return runs


def preamble_stand_in(run):
    """The neutral line a twin writes for one line of a run (G2).

    A blank line stays blank and keeps its spaces, a comment keeps its
    mark, and a line of text becomes two words holding a space.  No word
    of the line itself is in the description to write.
    """
    if run["kind"] == DOC_PREAMBLE_BLANK:
        return run["mark"]
    return run["mark"] + DOC_WITHHELD_LINE


def preamble_lines_for(form):
    """Every line the twin writes before the table, in file order (G2)."""
    lines = []
    for run in form["preamble"]:
        for _line in range(run["lines"]):
            lines += [preamble_stand_in(run)]
    return lines


def spread_blank_places(spread):
    """Where counted blank lines stand: evenly from the first to the last.

    G2: the k-th of n stands after `first + k * (last - first) // (n - 1)`
    records, so a file with one blank line after every record is written
    exactly as it was.
    """
    places = []
    span = spread["last"] - spread["first"]
    for index in range(spread["lines"]):
        after = spread["first"]
        if spread["lines"] > 1:
            after = spread["first"] + (index * span) // (spread["lines"] - 1)
        last = len(places) - 1
        if last >= 0 and places[last]["after"] == after:
            places[last] = {
                "after": after,
                "lines": places[last]["lines"] + 1,
                "text": spread["text"],
            }
            continue
        places += [{"after": after, "lines": 1, "text": spread["text"]}]
    return places


def spread_line_endings(census):
    """Each line's ending where the endings are published counted (G2).

    Written from G2's line-ending row as it is stated there: the
    commonest ending (the earlier in the listed order on a tie) ends
    every line no rarer one takes; each rarer ending, in the listed
    order, places its c lines one at a time, its k-th offered the line
    ((2k + 1) * total) // (2c) or the line just below the one it took
    last where that stands lower; a taken line passes the offer down to
    the next free line, and past the end of the file to the first free
    line from the top.

    The rarer endings' lines are kept as a mapping from line to ending
    and every other line is filled in at the end, because the rule
    names which lines the rarer endings TAKE and leaves the rest to the
    commonest.
    """
    if not census:
        return []
    counts = [entry["lines"] for entry in census]
    total = sum(counts)
    commonest = 0
    for index in range(1, len(counts)):
        if counts[index] > counts[commonest]:
            commonest = index
    placed = {}
    for index in range(len(census)):
        if index == commonest:
            continue
        c = counts[index]
        below_last = 0
        for k in range(c):
            line = max(((2 * k + 1) * total) // (2 * c), below_last)
            while line < total and line in placed:
                line = line + 1
            if line >= total:
                line = 0
                while line in placed:
                    line = line + 1
            placed[line] = census[index]["ending"]
            below_last = line + 1
    return [
        placed[line] if line in placed else census[commonest]["ending"]
        for line in range(total)
    ]


def written_form_lines(names, rows, write_header, form):
    """Every line of the twin in file order, without its line endings (G2).

    The order is the one G2's table fixes: the separator hint, the lines
    before the table, the header, the rows of column descriptions, then
    the data records with the blank lines standing where the form places
    them.
    """
    lines = []
    if form["separator_line"]:
        lines += ["sep=" + form["delimiter"]]
    lines += preamble_lines_for(form)
    if write_header:
        lines += [header_written(names, form)]
    for row in form["header_rows"]:
        alone = len(row) == 1
        parts = [
            written_field(cell, form["header_rows_quoting"], form, alone)
            for cell in row
        ]
        lines += [joined_fields(parts, form)]
    places = form["blank_lines"]
    if form["blank_lines_spread"] is not None:
        places = spread_blank_places(form["blank_lines_spread"])
    at = 0
    for index in range(len(rows)):
        while at < len(places) and places[at]["after"] == index:
            for _line in range(places[at]["lines"]):
                lines += [places[at]["text"]]
            at = at + 1
        lines += [record_written(rows[index], form)]
    while at < len(places):
        for _line in range(places[at]["lines"]):
            lines += [places[at]["text"]]
        at = at + 1
    return lines


def written_form_text(names, rows, write_header, form):
    """The whole twin in its source's written form, as text (G2).

    A byte-order mark leads where the form has one; each line takes the
    next ending of the form's runs, or the ending the spread gives it;
    the last line takes none unless the form ends its last line; and the
    end-of-file mark follows where the form has one.
    """
    lines = written_form_lines(names, rows, write_header, form)
    endings = []
    for run in form["line_endings"]:
        for _line in range(run["lines"]):
            endings += [DOC_ENDING_TEXT[run["ending"]]]
    if form["line_endings_spread"]:
        endings = [
            DOC_ENDING_TEXT[name]
            for name in spread_line_endings(form["line_endings_spread"])
        ]
    text = DOC_BYTE_ORDER_MARK if form["byte_order_mark"] else ""
    for index in range(len(lines)):
        text = text + lines[index]
        if index < len(endings):
            text = text + endings[index]
        elif index < len(lines) - 1 or form["final_line_ending"]:
            text = text + DOC_LF
    if form["end_of_file_mark"]:
        text = text + DOC_END_OF_FILE
    return text


# -- G2.1: where the rows stand ----------------------------------------


def sequence_cells_written(start, n_rows):
    """The row sequence as cells: start, start + 1, ... in row order."""
    return [f"{start + index}" for index in range(n_rows)]


def empty_record_targets(form, n_rows):
    """Which rows the form's records holding nothing stand in (G2.1 step 2).

    Written from G2.1's placement paragraph: the leading block, the
    trailing block, and the k-th interior record at
    `leading + k * middle // (interior + 1)`, moved down past a row
    already taken and never past the last row above the trailing block.

    The places are collected as a set and the row-by-row answer is
    built from it at the end, because the rule is about WHICH ROWS are
    taken and says nothing about walking the table.
    """
    empties = form["empty_rows"]
    leading = min(empties["leading"], n_rows)
    trailing = min(empties["trailing"], n_rows - leading)
    middle = n_rows - leading - trailing
    interior = min(empties["interior"], middle)
    taken = {}
    for row in range(leading):
        taken[row] = True
    for row in range(n_rows - trailing, n_rows):
        taken[row] = True
    lowest = n_rows - trailing - 1
    for step in range(interior):
        place = leading + ((step + 1) * middle) // (interior + 1)
        while place in taken and place < lowest:
            place = place + 1
        taken[place] = True
    return [row in taken for row in range(n_rows)]


def place_empty_records(grid, form, n_rows):
    """Exchange cells within columns so exactly the target rows are empty.

    G2.1 step 2.  First every target row is emptied: a cell holding
    something is exchanged for an empty cell of the same column from the
    first row that is not a target and has one.  Then every OTHER row
    left with nothing in it is given a cell, taken from the first
    non-target row that keeps something else.  Nothing is added, removed
    or altered, so no column's cells change as a multiset.
    """
    width = len(grid)
    targets = empty_record_targets(form, n_rows)

    # THE FIRST WALK. Each column's rows that are not targets and hold
    # nothing are the rows that can receive, in row order; a target row
    # holding something hands its cell to the next one of them. The
    # rule says each such row gives once, so they are listed once and
    # spent in order rather than searched for again per row.
    for place in range(width):
        column = grid[place]
        receivers = [
            row
            for row in range(n_rows)
            if not targets[row] and column[row] == ""
        ]
        spent = 0
        for row in range(n_rows):
            if not targets[row] or column[row] == "":
                continue
            if spent >= len(receivers):
                break
            other = receivers[spent]
            spent = spent + 1
            column[row], column[other] = column[other], column[row]

    # THE SECOND WALK. How many columns each row now holds something in
    # decides both who needs a cell (none) and who may give one (two or
    # more, since a giver must still hold something afterwards).
    holds = []
    for row in range(n_rows):
        held = 0
        for place in range(width):
            if grid[place][row] != "":
                held = held + 1
        holds += [held]
    for row in range(n_rows):
        if targets[row] or holds[row]:
            continue
        for place in range(width):
            column = grid[place]
            source = -1
            for other in range(n_rows):
                if targets[other] or column[other] == "" or holds[other] < 2:
                    continue
                source = other
                break
            if source < 0:
                continue
            column[row], column[source] = column[source], column[row]
            holds[row] = holds[row] + 1
            holds[source] = holds[source] - 1
            break


def decimal_comma_exchanged(text):
    """A declared column's cell written the way the ordinary grammar reads.

    Plan P4-D26: the COMMA is the person's decimal point and the POINT
    their thousands mark, so both roles swap in one pass -- drop every
    point, then read every comma as a point -- and `1.234,56` becomes
    `1234.56`.
    """
    out = ""
    for mark in text:
        if mark == ".":
            continue
        out = out + ("." if mark == "," else mark)
    return out


def doc_read_number(text):
    """The number a sort key holds, or None where it holds none (G2.1).

    The narrow grammar again, and for the same reason: a key read
    wrongly puts the rows in the wrong order, so a cell this cannot
    place with certainty stops the run instead of sorting last by
    accident.
    """
    body = text.strip()
    if not body:
        return None
    if doc_is_a_plain_number(body):
        return float(body)
    for mark in body:
        if mark.isalpha() or mark == DOC_SPACE or mark in DOC_TEXT_MARKS:
            continue
        raise AssertionError(
            f"this oracle will not read {text!r} as a sort key: it is "
            "neither a plain number nor ordinary text, and the collation "
            "of method section G2.1 decides the twin's row order."
        )
    return None


def sort_permutation(keys, order, count):
    """The rows in the order the form's sort key puts them (G2.1 step 3).

    Under the number collation a cell holding no number goes LAST; under
    `decimal_comma` the same reader is applied to the cell with its
    declared comma and point exchanged first, because the twin writes
    this column's numbers with a comma and the ordinary grammar would
    put `10,0` before `9,9`.  The sort is stable: rows the key cannot
    tell apart keep the order the generator gave them.
    """
    collation = order["collation"]
    direction = order["direction"]
    if collation in ("number", "decimal_comma"):
        numbered = []
        for index in range(count):
            text = keys[index]
            if collation == "decimal_comma":
                text = decimal_comma_exchanged(text)
            number = doc_read_number(text)
            if number is None:
                numbered += [(1, 0.0, index)]
            elif direction == "descending":
                numbered += [(0, -number, index)]
            else:
                numbered += [(0, number, index)]
        return [entry[2] for entry in sorted(numbered)]
    lettered = []
    for index in range(count):
        lettered += [
            (keys[index], index if direction == "ascending" else -index)
        ]
    placed = sorted(lettered)
    if direction == "descending":
        placed = list(reversed(placed))
    return [abs(entry[1]) for entry in placed]


def sequence_columns_written(grid, form, n_rows):
    """Write every row-sequence column in place -- G2.1's LAST step.

    It is last, and that is the rule rather than an ordering detail: the
    sequence reads 0, 1, 2, ... down the finished file whatever moved,
    so a reader who takes it for a record number gets the file's own row
    numbers and not the generator's.
    """
    for index in range(len(grid)):
        start = form["columns"][index]["sequence_start"]
        if start is not None:
            grid[index] = sequence_cells_written(start, n_rows)


def row_arrangement(columns, form, n_rows):
    """A twin's rows placed where the form says they stand (G2.1).

    Three steps, drawing no word: the records holding nothing are placed
    by moving cells WITHIN one column; whole rows are then permuted by
    the sort column, the records holding nothing staying where they were
    put and the others sorted into the places around them; and every
    row-sequence column is written in place last.
    """
    width = len(columns)
    if not width or not n_rows:
        return [list(column) for column in columns]
    grid = [list(column) for column in columns]
    order = form["row_order"]
    empties = form["empty_rows"]
    total_empty = empties["leading"] + empties["interior"] + empties["trailing"]
    targets = [False for _row in range(n_rows)]
    if width >= 2 and (total_empty or order is None):
        place_empty_records(grid, form, n_rows)
        targets = empty_record_targets(form, n_rows)
    if order is not None and order["column"] <= width:
        free = [row for row in range(n_rows) if not targets[row]]
        key = grid[order["column"] - 1]
        placed = sort_permutation([key[row] for row in free], order, len(free))
        for place in range(width):
            column = grid[place]
            moved = list(column)
            for index in range(len(free)):
                moved[free[index]] = column[free[placed[index]]]
            grid[place] = moved
    sequence_columns_written(grid, form, n_rows)
    return grid


# -- the reading that settles a file's delimiter (review item CODEX-5) --


def physical_lines_of(text):
    """The text cut into lines, each keeping its own ending."""
    lines = []
    line = ""
    index = 0
    while index < len(text):
        mark = text[index]
        line = line + mark
        if mark == DOC_LF:
            lines += [line]
            line = ""
        elif mark == DOC_CR:
            if text[index + 1 : index + 2] == DOC_LF:
                line = line + DOC_LF
                index = index + 1
            lines += [line]
            line = ""
        index = index + 1
    if line:
        lines += [line]
    return lines


def doc_read_records(text, delimiter, escape, initial_space, at, limit):
    """Every record the standard reader yields, from ``at``.

    A quoted field opens with a quote character and closes with one; a
    quote inside it is written twice, or after a backslash under
    backslash escaping.  A blank line is a record with no fields, which
    is what the standard reader yields for one.

    THIS MIRROR REFUSES WHAT IT DOES NOT MODEL, by name: a quoted field
    that spans a line ending, and text following a closing quote.  Both
    are readings the shipped lexer has rules for, and a mirror that
    silently produced something else for them would agree with nothing.
    """
    span = text[at:] if limit < 0 else text[at : at + 1_048_576]
    taken = []
    for line in physical_lines_of(span):
        if limit >= 0 and len(taken) >= limit:
            break
        body = line
        for ending in ("\r\n", DOC_LF, DOC_CR):
            if body[len(body) - len(ending) :] == ending:
                body = body[: len(body) - len(ending)]
                break
        if not body:
            taken += [{"fields": [], "raw": ""}]
            continue
        fields = []
        value = ""
        inside = False
        closed = False
        malformed = 0
        skipping = initial_space
        index = 0
        while index < len(body):
            mark = body[index]
            if inside:
                if escape == DOC_ESCAPE_BACKSLASH and mark == DOC_BACKSLASH:
                    value = value + body[index + 1 : index + 2]
                    index = index + 2
                    continue
                if mark == DOC_QUOTE:
                    if (
                        escape == DOC_ESCAPE_DOUBLED
                        and body[index + 1 : index + 2] == DOC_QUOTE
                    ):
                        value = value + DOC_QUOTE
                        index = index + 2
                        continue
                    inside = False
                    closed = True
                    index = index + 1
                    continue
                value = value + mark
                index = index + 1
                continue
            if mark == delimiter:
                fields += [value]
                value = ""
                closed = False
                skipping = initial_space
                index = index + 1
                continue
            if skipping and mark == DOC_SPACE:
                index = index + 1
                continue
            skipping = False
            if mark == DOC_QUOTE and not value and not closed:
                inside = True
                index = index + 1
                continue
            if closed:
                # TEXT AFTER A CLOSING QUOTE is neither an error nor a
                # refusal: the reader counts the field MALFORMED and
                # carries on appending, so `"id"; "note"` read under the
                # COMMA is one field reading `id; "note"`.  That reading
                # is the whole reason the comma is rejected below, so a
                # mirror that stopped here could not score any candidate
                # against a file whose fields are quoted -- which is
                # every file this rule was measured on.
                malformed = malformed + 1
                closed = False
            value = value + mark
            index = index + 1
        if inside:
            raise AssertionError(
                "this oracle does not model a quoted field spanning a line "
                f"ending, and the line {body!r} opens one"
            )
        fields += [value]
        taken += [{"fields": fields, "malformed": malformed, "raw": body}]
    return taken


def leads_the_table(record):
    """Whether a record has the shape of a line BEFORE a table, not a row.

    A blank line; a line beginning `#`; or a line of one field that
    reads as a title because it holds a space.  A one-field line holding
    no space is the name of a one-column table as often as it is a
    title, so it is not one.
    """
    if not record["fields"]:
        return True
    if record["raw"][:1] == "#":
        return True
    return len(record["fields"]) == 1 and DOC_SPACE in record["raw"]


def width_share(sample):
    """How many records sit at their commonest width, and that width.

    Blank lines and lines of nothing but spaces are not records of any
    width and are not counted.
    """
    counted = {}
    total = 0
    for record in sample:
        width = len(record["fields"])
        if not width:
            continue
        if width == 1 and all(
            mark in (DOC_SPACE, DOC_TAB) for mark in record["fields"][0]
        ):
            continue
        counted[width] = counted.get(width, 0) + 1
        total = total + 1
    if not total:
        return (0, 0, 0)
    best = 0
    best_count = 0
    for width in sorted(counted):
        if counted[width] >= best_count:
            best = width
            best_count = counted[width]
    return (best_count, total, best)


def best_reading(text, candidate, at):
    """The best the first records read under one candidate delimiter.

    EVERY SETTING IS SCORED WITH THE DELIMITER (review item CODEX-5).
    The settings decide what a delimiter READS AS, so choosing the
    delimiter first and the spacing and escaping afterwards reads a
    two-column file as one column: a file written `"id"; "note"` with
    `"1"; "alpha; beta"` under it reads, with no space skipped, as a
    header of two fields and rows of three -- the space before the quote
    makes that quote an ordinary character -- and is rejected as ragged.

    So each candidate is scored at its own best over the two spacings
    and the two escapings, a reading counts only where the commonest
    width is two or more, and THE TABLE'S FIRST RECORD HAS THE TABLE'S
    WIDTH: the first record that is not a line before the table must
    stand at that width, or the reading is rejected.
    """
    best = None
    for spaced in (False, True):
        for escape in DOC_ESCAPES:
            sample = doc_read_records(
                text, candidate, escape, spaced, at, DOC_SAMPLE_RECORDS
            )
            at_width, total, width = width_share(sample)
            if width < 2:
                continue
            opening = 0
            while opening < len(sample) and leads_the_table(sample[opening]):
                opening = opening + 1
            if opening < len(sample) and len(sample[opening]["fields"]) != width:
                continue
            found = {
                "at_that_width": at_width,
                "records": total,
                "width": width,
            }
            if best is None or (at_width * best["records"], width) > (
                best["at_that_width"] * total,
                best["width"],
            ):
                best = found
    return best


def chosen_delimiter(readings):
    """The delimiter a table is written with, from the readings above.

    The candidate under which the most records share one width of two or
    more fields wins, a wider table breaking a tie.  A table no candidate
    reads as two or more fields is one column and its delimiter is the
    comma.

    A TIE OF BOTH is decided by the cells, which this oracle does not
    reach: it stops rather than choosing, because the rule that settles
    it counts how many cells read as numbers under each reading, and a
    frozen case that needed it would need the whole number grammar with
    it.
    """
    chosen = ","
    best = None
    for candidate in DOC_DELIMITERS:
        found = readings[candidate]
        if found is None:
            continue
        if best is None:
            chosen, best = candidate, found
            continue
        here = found["at_that_width"] * best["records"]
        there = best["at_that_width"] * found["records"]
        if here > there or (here == there and found["width"] > best["width"]):
            chosen, best = candidate, found
            continue
        if here == there and found["width"] == best["width"]:
            raise AssertionError(
                f"the readings under {best!r} and {found!r} tie on both the "
                "share and the width, and the rule that settles such a tie "
                "counts the cells that read as numbers, which this oracle "
                "does not implement"
            )
    return chosen


# -- G2.2: the twin of a workbook --------------------------------------

SHEET_NOTHING_CLASSES = ("absent", "blank", "empty")
SHEET_VALUE_CLASSES = ("error", "boolean", "date", "number", "text")
# G2.2 step 1: the classes a value-holding cell is told apart by, in the
# order their published counts are handed out in.
SHEET_TOLD_BY_SPELLING = ("error", "boolean", "date", "number")
SHEET_ERROR_KINDS = (
    "#DIV/0!", "#N/A", "#NAME?", "#NULL!", "#NUM!", "#REF!", "#VALUE!",
    "#GETTING_DATA", "#SPILL!", "#CALC!",
)
SHEET_FORMAT_KINDS = ("plain", "date", "datetime", "time", "elapsed", "text")
SHEET_WITHHELD_CELL = "withheld"
SHEET_NEUTRAL_NAME = "Sheet"
SHEET_TABLE_NAME = "Table1"

# The closed vocabulary of format codes a description may publish, with
# the id a workbook stores each built-in one under.  These are the codes
# of the file format itself and not text of anybody's table, which is
# what makes them publishable at all.
SHEET_BUILT_IN_FORMAT_IDS = {
    "General": 0, "0": 1, "0.00": 2, "#,##0": 3, "#,##0.00": 4, "0%": 9,
    "0.00%": 10, "0.00E+00": 11, "# ?/?": 12, "# ??/??": 13, "mm-dd-yy": 14,
    "d-mmm-yy": 15, "d-mmm": 16, "mmm-yy": 17, "h:mm AM/PM": 18,
    "h:mm:ss AM/PM": 19, "h:mm": 20, "h:mm:ss": 21, "m/d/yy h:mm": 22,
    "#,##0 ;(#,##0)": 37, "#,##0 ;[Red](#,##0)": 38,
    "#,##0.00;(#,##0.00)": 39, "#,##0.00;[Red](#,##0.00)": 40, "mm:ss": 45,
    "[h]:mm:ss": 46, "mmss.0": 47, "##0.0E+0": 48, "@": 49,
}

SHEET_CANONICAL_FORMAT_CODES = {
    "plain": "General",
    "date": "yyyy\\-mm\\-dd",
    "datetime": "yyyy\\-mm\\-dd\\ hh:mm:ss",
    "time": "h:mm:ss",
    "elapsed": "[h]:mm:ss",
    "text": "@",
}

SHEET_FORMAT_CODE_KINDS = {
    "General": "plain", "0": "plain", "0.00": "plain", "#,##0": "plain",
    "#,##0.00": "plain", "0%": "plain", "0.00%": "plain",
    "0.00E+00": "plain", "# ?/?": "plain", "# ??/??": "plain",
    "mm-dd-yy": "date", "d-mmm-yy": "date", "d-mmm": "date",
    "mmm-yy": "date", "h:mm AM/PM": "time", "h:mm:ss AM/PM": "time",
    "h:mm": "time", "h:mm:ss": "time", "m/d/yy h:mm": "datetime",
    "#,##0 ;(#,##0)": "plain", "#,##0 ;[Red](#,##0)": "plain",
    "#,##0.00;(#,##0.00)": "plain", "#,##0.00;[Red](#,##0.00)": "plain",
    "mm:ss": "time", "[h]:mm:ss": "elapsed", "mmss.0": "time",
    "##0.0E+0": "plain", "@": "text",
    "yyyy\\-mm\\-dd": "date",
    "yyyy\\-mm\\-dd\\ hh:mm:ss": "datetime",
}

SHEET_DECLARATION = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
)
SHEET_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
SHEET_RELS = (
    "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
)
SHEET_PACKAGE = (
    "http://schemas.openxmlformats.org/package/2006/relationships"
)
SHEET_TYPES = "http://schemas.openxmlformats.org/package/2006/content-types"
SHEET_BOOK_TYPE = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"
)


def sheet_escaped(text):
    """One piece of text as XML content (G2.2 step 11).

    A carriage return is written as its character reference, because a
    reader turns a literal one into a line feed before the text reaches
    it.
    """
    out = text
    out = out.replace("&", "&amp;")
    out = out.replace("<", "&lt;")
    out = out.replace(">", "&gt;")
    out = out.replace('"', "&quot;")
    out = out.replace("\r", "&#13;")
    return out


def sheet_attribute(text):
    """One piece of text as an attribute's value (G2.2 step 11)."""
    out = sheet_escaped(text)
    out = out.replace("\n", "&#10;")
    out = out.replace("\t", "&#9;")
    return out


def sheet_cleaned(text):
    """The text with the characters XML cannot carry taken out."""
    out = ""
    for mark in text:
        place = ord(mark)
        if place in (9, 10, 13) or place >= 32:
            out = out + mark
    return out


def column_letters(number):
    """The letters naming a column, counting from one: 1 is A, 28 is AB."""
    letters = ""
    left = number
    while left > 0:
        left = left - 1
        letters = chr(65 + left % 26) + letters
        left = left // 26
    return letters


def sheet_number_spelling(text):
    """The text as a workbook stores a number, or "" where it is not one.

    G2.2 step 1.  A grouped number, a decimal comma, a bracketed
    negative, a percent or a currency mark is NOT one: in a workbook
    those are a FORMAT worn by a plain number and never the stored
    value, so a cell written that way is written as text and keeps its
    characters.
    """
    if not text:
        return ""
    return text if doc_is_a_plain_number(text) else ""


def sheet_is_iso_date(text):
    """Whether the text is ISO date text, as G2.2 step 1 states it.

    `YYYY-MM-DD`, optionally followed by `T` and a clock, or a clock
    alone; the clock `hh:mm`, `hh:mm:ss`, or `hh:mm:ss` with a point and
    figures.
    """
    def figures(piece, count):
        return len(piece) == count and all(mark in "0123456789" for mark in piece)

    clock = text
    if figures(text[0:4], 4) and text[4:5] == "-":
        if not (figures(text[5:7], 2) and text[7:8] == "-" and figures(text[8:10], 2)):
            return False
        if len(text) == 10:
            return True
        if text[10:11] != "T":
            return False
        clock = text[11:]
    if not (figures(clock[0:2], 2) and clock[2:3] == ":" and figures(clock[3:5], 2)):
        return False
    if len(clock) == 5:
        return True
    if clock[5:6] != ":" or not figures(clock[6:8], 2):
        return False
    if len(clock) == 8:
        return True
    fraction = clock[9:]
    return (
        clock[8:9] == "."
        and bool(fraction)
        and all(mark in "0123456789" for mark in fraction)
    )


def sheet_fits(kind, text):
    """Whether a cell holding this text can be written as this class (G2.2)."""
    if kind == "error":
        return text in SHEET_ERROR_KINDS
    if kind == "boolean":
        return text in ("TRUE", "FALSE")
    if kind == "date":
        return sheet_is_iso_date(text)
    if kind == "number":
        return sheet_number_spelling(text) != ""
    return True


def sheet_boolean_spelling(text):
    """`1` or `0` where the text is a boolean's spelling, else nothing."""
    folded = text.casefold()
    if folded in ("true", "1"):
        return "1"
    if folded in ("false", "0"):
        return "0"
    return ""


def sheet_wanted(census, kind):
    """How many cells of this class the description asks for (G2.2 step 1).

    A count the smallest group held back is not a licence to write none:
    it means the number was not published, so nothing is asked for here
    and the leading class answers for those cells.
    """
    found = census.get(kind)
    return found if isinstance(found, int) else 0


def sheet_denied(census, kind):
    """Whether the census says outright that no cell has this class."""
    found = census.get(kind)
    return isinstance(found, int) and found == 0


def sheet_leading(census, among):
    """Which of these classes the column holds most of (G2.2 step 1).

    Ties go to the earlier of the order given, and A CLASS PUBLISHED AS
    NOUGHT IS NEVER THE LEADING ONE: a published nought is a fact about
    the column, so the remainder goes to a class whose number was not
    published rather than to one the description denies.
    """
    best = among[len(among) - 1]
    seen = -1
    best_denied = True
    for kind in among:
        count = sheet_wanted(census, kind)
        denied = sheet_denied(census, kind)
        if count > seen:
            seen, best, best_denied = count, kind, denied
            continue
        if count == seen and best_denied and not denied:
            best, best_denied = kind, denied
    return best


def sheet_withheld(census, kind):
    """Whether the census held this class's count back (`null`)."""
    return not isinstance(census.get(kind), int)


def sheet_spread_over(fitting, wanted):
    """The cells a class takes of those it fits (G2.2 step 1, plan P4-D187).

    Every one, in row order, where no more fit than its count names;
    otherwise the count spread evenly over them by the smooth rotation:
    each fitting cell adds the count to a credit and is taken where the
    credit reaches the number of fitting cells, which is then taken back.
    """
    if wanted <= 0:
        return []
    if len(fitting) <= wanted:
        return list(fitting)
    chosen = []
    credit = 0
    for index in fitting:
        credit += wanted
        if credit >= len(fitting):
            credit -= len(fitting)
            chosen.append(index)
    return chosen


def sheet_cell_classes(census, cells, value_class=None):
    """Which class each generated cell of one column is written as (G2.2).

    THE CLASS COMES FROM WHAT THE SOURCE HELD, never from what the
    twin's characters could be read as -- which is what keeps a column
    of text whose every cell looks like a number written as TEXT -- and
    a class goes only to a cell it FITS, which is what keeps an error
    count off a column's labels.
    """
    empty_order = []
    full_order = []
    for index in range(len(cells)):
        if cells[index] == "":
            empty_order += [index]
            continue
        full_order += [index]
    out = ["" for _index in range(len(cells))]

    leading_nothing = sheet_leading(census, SHEET_NOTHING_CLASSES)
    at = 0
    for kind in SHEET_NOTHING_CLASSES:
        left = sheet_wanted(census, kind)
        while left > 0 and at < len(empty_order):
            out[empty_order[at]] = kind
            at = at + 1
            left = left - 1
    withheld = [
        kind for kind in SHEET_NOTHING_CLASSES if sheet_withheld(census, kind)
    ]
    rest = withheld[0] if withheld else leading_nothing
    while at < len(empty_order):
        out[empty_order[at]] = rest
        at = at + 1

    # Each published count of a class told apart by its spelling, handed
    # out in row order to the cells it fits.
    left = {
        kind: (None if sheet_withheld(census, kind) else census[kind])
        for kind in SHEET_VALUE_CLASSES
    }
    given = set()
    for kind in SHEET_TOLD_BY_SPELLING:
        if left[kind] is None:
            continue
        fitting = [
            index for index in full_order
            if index not in given and sheet_fits(kind, cells[index])
        ]
        for index in sheet_spread_over(fitting, left[kind]):
            out[index] = kind
            given.add(index)
        left[kind] = left[kind] - min(left[kind], len(fitting))

    def wanted_by_another(text):
        return any(
            (left[kind] is None or left[kind] > 0) and sheet_fits(kind, text)
            for kind in SHEET_TOLD_BY_SPELLING
        )

    if left["text"] is not None:
        for first_pass in (True, False):
            for index in full_order:
                if left["text"] <= 0:
                    break
                if index in given:
                    continue
                if first_pass and wanted_by_another(cells[index]):
                    continue
                out[index] = "text"
                given.add(index)
                left["text"] = left["text"] - 1

    leading_value = sheet_leading(census, SHEET_VALUE_CLASSES)
    candidates = list(SHEET_VALUE_CLASSES)
    if value_class is not None:
        candidates = [value_class] + candidates
    for index in full_order:
        if index in given:
            continue
        text = cells[index]
        chosen = None
        for kind in candidates:
            if left[kind] is None and sheet_fits(kind, text):
                chosen = kind
                break
        if chosen is None:
            chosen = leading_value if sheet_fits(leading_value, text) else "text"
        out[index] = chosen
    return out


def sheet_format_kinds(census, classes, format_code="General", dated=None):
    """Which kind of format each cell of one column wears (G2.2 step 2).

    A mixture is reproduced as its COUNTS and never collapsed to the
    majority.  An ABSENT cell is always plain: nothing is written for
    it, so every reader sees the general format there.

    A date format goes to a date first: ``dated`` names per cell the
    kind of date its text was (``date``, ``datetime`` or ``""``), and
    each of those two kinds is offered to the cells of its own kind,
    then to the cells of the other, then by the class tiers: a text
    format to text and empty cells, any other to number and date cells,
    then to blank cells, then to any cell.

    A withheld count is not a licence for plain: a date no count claims
    keeps its own kind where that kind's count was withheld, and any
    other cell no count claims takes the kind of the column's published
    code where that kind was withheld, else plain where plain was
    withheld, else the first withheld kind.
    """
    written = [
        index for index in range(len(classes)) if classes[index] != "absent"
    ]
    dated = dated or ["" for _index in range(len(classes))]
    absent = len(classes) - len(written)
    out = ["plain" for _index in range(len(classes))]
    given = set()

    def suits(kind, cell_class):
        if kind == "text":
            if cell_class in ("text", "empty"):
                return 0
        elif cell_class in ("number", "date"):
            return 0
        return 1 if cell_class == "blank" else 2

    for kind in SHEET_FORMAT_KINDS:
        if kind == "plain":
            continue
        left = sheet_wanted(census, kind)
        order = []
        if kind in ("date", "datetime"):
            order += [index for index in written if dated[index] == kind]
            order += [
                index for index in written if dated[index] and dated[index] != kind
            ]
        for tier in (0, 1, 2):
            order += [index for index in written if suits(kind, classes[index]) == tier]
        for index in order:
            if left <= 0:
                break
            if index in given:
                continue
            out[index] = kind
            given.add(index)
            left -= 1
    for index in written:
        if index in given or not dated[index]:
            continue
        if not sheet_withheld(census, dated[index]):
            continue
        out[index] = dated[index]
        given.add(index)

    plain_withheld = sheet_withheld(census, "plain")
    plain_left = None if plain_withheld else census["plain"] - absent
    code_kind = sheet_code_kind(format_code)
    for index in written:
        if index in given:
            continue
        if not plain_withheld and plain_left > 0:
            plain_left = plain_left - 1
            continue
        if sheet_withheld(census, code_kind):
            out[index] = code_kind
        elif plain_withheld:
            out[index] = "plain"
        else:
            spare = [
                kind for kind in SHEET_FORMAT_KINDS
                if sheet_withheld(census, kind)
            ]
            out[index] = spare[0] if spare else "plain"
    return out


# -- G2.2 step 0: a date is written back as the day count it was read as

SHEET_EPOCH_1900 = datetime.datetime(1899, 12, 30)
SHEET_EPOCH_1904 = datetime.datetime(1904, 1, 1)


def sheet_date_kind(text):
    """``date`` for ``YYYY-MM-DD``, ``datetime`` for the moment, else ``""``.

    The two spellings are the ones contract 4.3b says a number cell
    wearing a date or datetime format is read as: the date, or the date,
    a space and ``HH:MM:SS`` with ``.fff`` where the time is not a whole
    second.
    """
    for kind, pattern in (
        ("date", "%Y-%m-%d"),
        ("datetime", "%Y-%m-%d %H:%M:%S"),
        ("datetime", "%Y-%m-%d %H:%M:%S.%f"),
    ):
        try:
            moment = datetime.datetime.strptime(text, pattern)
        except ValueError:
            continue
        if moment.strftime(pattern) == text or (
            pattern.endswith("%f") and len(text) == 23
            and moment.strftime("%Y-%m-%d %H:%M:%S.%f")[:23] == text
        ):
            return kind
    return ""


def sheet_day_count(text, epoch_1904):
    """The day count a workbook stores for one of those spellings, or ``""``.

    The 1900 system counts 1900-01-01 as day 1 and carries a day 60 that
    never was, so a date before 1900-03-01 is one day nearer its epoch;
    the 1904 system counts 1904-01-01 as day 0.  A whole day is written
    in figures and a moment as the shortest spelling of its double.
    """
    kind = sheet_date_kind(text)
    if not kind:
        return ""
    pattern = "%Y-%m-%d" if kind == "date" else (
        "%Y-%m-%d %H:%M:%S.%f" if len(text) == 23 else "%Y-%m-%d %H:%M:%S"
    )
    moment = datetime.datetime.strptime(text, pattern)
    if epoch_1904:
        span = moment - SHEET_EPOCH_1904
        if span.days < 0:
            return ""
    else:
        span = moment - SHEET_EPOCH_1900
        if span.days <= 60:
            span = span - datetime.timedelta(days=1)
            if span.days < 1 or span.days >= 60:
                return ""
    milliseconds = span.seconds * 1000 + span.microseconds // 1000
    if milliseconds == 0:
        return str(span.days)
    return repr(span.days + milliseconds / 86400000)


def sheet_dates_as_day_counts(column, own, epoch_1904):
    """A column's dates as day counts, where it publishes a date format."""
    wants = any(
        sheet_wanted(column["format_kinds"], kind) > 0
        for kind in ("date", "datetime")
    ) or sheet_code_kind(column["format_code"]) in ("date", "datetime")
    out = []
    dated = []
    for text in own:
        serial = sheet_day_count(text, epoch_1904) if wants and text else ""
        out += [serial or text]
        dated += [sheet_date_kind(text) if serial else ""]
    return out, dated


def sheet_code_kind(code):
    """Which kind a published format code is (G2.2 step 3, plan P4-D189).

    Read off the code, as the method states the rule, because a code
    published as the source wrote it is in no closed list: `General` and
    the empty code are plain and `@` is text; otherwise the first section
    alone, read left to right: a square bracket outside a quoted run is
    read to its close -- one never closed ends the reading -- and counts
    only where it holds an elapsed count
    (`h`, `m` or `s` repeated), which makes the code elapsed; the
    character after a backslash, an underscore or an asterisk is skipped,
    inside a quoted run too; a quotation mark opens or closes a quoted
    run, whose characters are not read. Of what is left, a `d` or `y` beside an `h` or `s`
    is datetime; a `d` or `y`, or an `m` with no `h` or `s`, is date; an
    `h` or `s` is time; anything else is plain -- each letter in either
    case.
    """
    if code in ("General", ""):
        return "plain"
    if code == "@":
        return "text"
    body = code.split(";")[0]
    letters = []
    elapsed = False
    index = 0
    quoted = False
    while index < len(body):
        mark = body[index]
        if mark == "[" and not quoted:
            close = body.find("]", index)
            if close < 0:
                break
            inside = body[index + 1:close]
            if inside and inside[0] in "hHmMsS" and inside == inside[0] * len(inside):
                elapsed = True
            index = close + 1
            continue
        if mark in "\\_*":
            index += 2
            continue
        if mark == '"':
            quoted = not quoted
            index += 1
            continue
        if not quoted:
            letters.append(mark.lower())
        index += 1
    if elapsed:
        return "elapsed"
    day = "d" in letters or "y" in letters
    clock = "h" in letters or "s" in letters
    if day and clock:
        return "datetime"
    if day or ("m" in letters and not clock):
        return "date"
    if clock:
        return "time"
    return "plain"


def sheet_code_for_kind(kind, published):
    """The code a cell of this kind is written with (G2.2 step 3)."""
    if sheet_code_kind(published) == kind:
        return published
    return SHEET_CANONICAL_FORMAT_CODES[kind]


def sheet_placeholder_rows(above, n_columns):
    """How many rows the twin writes above its header (G2.2 step 5).

    A ONE-COLUMN TABLE CANNOT CARRY THEM: the header is found as the
    first row reaching the table's width, so a one-cell row above the
    header IS that width and would be read back as the header.
    """
    return 0 if n_columns <= 1 else above


def sheet_aligned_for_empty_records(classes, cells, n_rows, wanted, tags=None):
    """Move each column's cells holding nothing onto shared rows (G2.2).

    A permutation WITHIN EACH COLUMN and nothing else, so each column
    keeps its exact multiset of values and every published fact about it
    still holds.  ``tags`` travel with their cells.
    """
    tags = tags if tags is not None else [["" for _v in column] for column in cells]
    if wanted <= 0 or not classes:
        return (classes, cells, tags)
    room = n_rows
    for column in classes:
        spare = 0
        for kind in column:
            if kind in SHEET_NOTHING_CLASSES:
                spare = spare + 1
        if spare < room:
            room = spare
    if room < wanted:
        wanted = room
    if wanted <= 0:
        return (classes, cells, tags)
    out_classes = []
    out_cells = []
    out_tags = []
    for index in range(len(classes)):
        kinds = list(classes[index])
        values = list(cells[index])
        marks = list(tags[index])
        spare_rows = [
            row
            for row in range(len(kinds))
            if row >= wanted and kinds[row] in SHEET_NOTHING_CLASSES
        ]
        at = 0
        for row in range(wanted):
            if row < len(kinds) and kinds[row] in SHEET_NOTHING_CLASSES:
                continue
            if at >= len(spare_rows):
                break
            other = spare_rows[at]
            at = at + 1
            kinds[row], kinds[other] = kinds[other], kinds[row]
            values[row], values[other] = values[other], values[row]
            marks[row], marks[other] = marks[other], marks[row]
        out_classes += [kinds]
        out_cells += [values]
        out_tags += [marks]
    return (out_classes, out_cells, out_tags)


def sheet_empty_row_places(classes, n_rows, wanted):
    """Which generated rows are written as records holding nothing (G2.2).

    G2.2 step 6: a row is written as a record holding nothing only
    where EVERY column's class already holds nothing, and those rows
    are taken in row order until the published count is met. So the
    rows that QUALIFY are gathered first and the count is spent on
    them, which is the shape of the rule's own sentence.
    """
    qualifying = []
    for row in range(n_rows):
        empty = True
        for column in classes:
            if row < len(column) and column[row] not in SHEET_NOTHING_CLASSES:
                empty = False
                break
        if empty:
            qualifying += [row]
    places = {}
    if wanted <= 0:
        return places
    for index in range(len(qualifying)):
        if index >= wanted:
            break
        places[qualifying[index]] = True
    return places


def sheet_shared_place(items, places, text):
    """Where this text sits in the shared-string table, adding it if new."""
    if text in places:
        return places[text]
    place = len(items)
    items += [text]
    places[text] = place
    return place


def sheet_published_name(name):
    """The sheet's name where it may be published, else nothing.

    One of the closed vocabulary of generic names, alone or followed by
    one or two figures that do not begin with a nought.  A sheet name
    can hold a person's name, so what is not one of those is withheld
    and the twin writes a neutral name.
    """
    if not name:
        return None
    figures = 0
    for index in range(len(name)):
        if name[len(name) - 1 - index] in "0123456789":
            figures = figures + 1
            continue
        break
    if figures > 2 or (figures and name[len(name) - figures] == "0"):
        return None
    stem = name[: len(name) - figures]
    safe = (
        "codebook", "data", "export", "info", "notes", "page", "raw",
        "report", "results", "sheet", "summary", "table", "values",
        "worksheet",
    )
    return name if stem.casefold() in safe else None


def sheet_twin_names(published):
    """The name the twin writes each sheet under (G2.2 step 9).

    A PUBLISHED NAME IS CLAIMED FIRST and a placeholder then walks up
    until it finds a number no published name has taken, so a workbook
    whose first sheet is withheld and whose second is called `Sheet1`
    does not rename the sheet whose name the description publishes.
    A name is taken whatever its case: a spreadsheet holds no two sheets
    whose names differ in case alone.
    """
    taken = {}
    for name in published:
        if name is not None:
            taken[name.casefold()] = True
    out = []
    for index in range(len(published)):
        here = published[index]
        if here is not None:
            out += [here]
            continue
        number = index + 1
        neutral = SHEET_NEUTRAL_NAME + f"{number}"
        while neutral.casefold() in taken:
            number = number + 1
            neutral = SHEET_NEUTRAL_NAME + f"{number}"
        taken[neutral.casefold()] = True
        out += [neutral]
    return out


def sheet_hidden_states(sheets, chosen, chosen_hidden):
    """Which of the twin's sheets are hidden (G2.2 step 9).

    The reading rule read backwards: every sheet BEFORE the chosen one
    is hidden, so the chosen sheet is the first visible one and the
    twin's own reader lands on the table.  Where that would leave
    nothing visible -- a workbook no spreadsheet application can open --
    one sheet that is not the table's is shown instead.
    """
    states = []
    for index in range(sheets):
        number = index + 1
        if number < chosen:
            states += [True]
            continue
        if number == chosen:
            states += [chosen_hidden]
            continue
        states += [False]
    if states and all(states):
        last = len(states) - 1
        if last == chosen - 1 and last > 0:
            last = last - 1
        states[last] = False
    return states


def sheet_cell_element(reference, kind, value, style):
    """One cell element.  It never carries a formula, whatever it holds."""
    marks = f' r="{reference}"'
    if kind:
        marks = marks + f' t="{kind}"'
    if style:
        marks = marks + f' s="{style}"'
    if not value:
        return f"<c{marks}/>"
    return f"<c{marks}><v>{sheet_escaped(value)}</v></c>"


def sheet_styles_part(codes):
    """The style table: one style per published code, plus the header's."""
    customs = []
    for code in codes:
        if code not in SHEET_BUILT_IN_FORMAT_IDS and code not in customs:
            customs += [code]
    text = SHEET_DECLARATION + f'<styleSheet xmlns="{SHEET_MAIN}">'
    if customs:
        text = text + f'<numFmts count="{len(customs)}">'
        for index in range(len(customs)):
            text = text + (
                f'<numFmt numFmtId="{164 + index}" '
                f'formatCode="{sheet_attribute(customs[index])}"/>'
            )
        text = text + "</numFmts>"
    text = text + (
        '<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font>'
        '<font><b/><sz val="11"/><name val="Calibri"/></font></fonts>'
        '<fills count="2"><fill><patternFill patternType="none"/></fill>'
        '<fill><patternFill patternType="gray125"/></fill></fills>'
        '<borders count="1"><border><left/><right/><top/><bottom/>'
        "<diagonal/></border></borders>"
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" '
        'borderId="0"/></cellStyleXfs>'
    )
    text = text + f'<cellXfs count="{len(codes) + 1}">'
    for code in codes:
        number = 0
        if code in SHEET_BUILT_IN_FORMAT_IDS:
            number = SHEET_BUILT_IN_FORMAT_IDS[code]
        else:
            for index in range(len(customs)):
                if customs[index] == code:
                    number = 164 + index
        text = text + (
            f'<xf numFmtId="{number}" fontId="0" fillId="0" borderId="0" '
            'xfId="0" applyNumberFormat="1"/>'
        )
    text = text + (
        '<xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" '
        'applyFont="1"/>'
    )
    text = text + "</cellXfs>"
    text = text + (
        '<cellStyles count="1"><cellStyle name="Normal" xfId="0" '
        'builtinId="0"/></cellStyles></styleSheet>'
    )
    return text


def sheet_shared_strings_part(items):
    """The shared-string table, preserving every space a cell's text has."""
    text = SHEET_DECLARATION + (
        f'<sst xmlns="{SHEET_MAIN}" count="{len(items)}" '
        f'uniqueCount="{len(items)}">'
    )
    for item in items:
        shown = sheet_escaped(item)
        if item != item.strip():
            text = text + f'<si><t xml:space="preserve">{shown}</t></si>'
            continue
        text = text + f"<si><t>{shown}</t></si>"
    return text + "</sst>"


def sheet_core_part():
    """Document properties, written NEUTRAL: they can name a person."""
    return SHEET_DECLARATION + (
        '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/'
        'package/2006/metadata/core-properties" xmlns:dc="http://purl.org/'
        'dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        "<dc:title></dc:title><dc:subject></dc:subject>"
        "<dc:creator></dc:creator><cp:lastModifiedBy></cp:lastModifiedBy>"
        "</cp:coreProperties>"
    )


def sheet_app_part():
    """The other half of the document properties, equally neutral."""
    return SHEET_DECLARATION + (
        '<Properties xmlns="http://schemas.openxmlformats.org/'
        'officeDocument/2006/extended-properties">'
        "<Application>synthtwin</Application><Company></Company>"
        "</Properties>"
    )


def sheet_table_part(names, first_row, last_row, autofilter):
    """A defined table over the twin's OWN rows, under a neutral name."""
    width = len(names)
    span = f"A{first_row}:{column_letters(width)}{last_row}"
    text = SHEET_DECLARATION + (
        f'<table xmlns="{SHEET_MAIN}" id="1" name="{SHEET_TABLE_NAME}" '
        f'displayName="{SHEET_TABLE_NAME}" ref="{span}" totalsRowShown="0">'
    )
    if autofilter:
        text = text + f'<autoFilter ref="{span}"/>'
    text = text + f'<tableColumns count="{width}">'
    for index in range(width):
        shown = sheet_attribute(sheet_cleaned(names[index]))
        text = text + f'<tableColumn id="{index + 1}" name="{shown}"/>'
    text = text + "</tableColumns>"
    text = text + (
        '<tableStyleInfo name="TableStyleMedium2" showFirstColumn="0" '
        'showLastColumn="0" showRowStripes="1" showColumnStripes="0"/>'
    )
    return text + "</table>"


def sheet_book_part(sheet_names, hidden, epoch_1904):
    """The workbook: every sheet in its place, its state, and the epoch."""
    text = SHEET_DECLARATION + (
        f'<workbook xmlns="{SHEET_MAIN}" xmlns:r="{SHEET_RELS}">'
    )
    if epoch_1904:
        text = text + '<workbookPr date1904="1"/>'
    text = text + "<sheets>"
    for index in range(len(sheet_names)):
        shown = sheet_attribute(sheet_names[index])
        state = ' state="hidden"' if hidden[index] else ""
        text = text + (
            f'<sheet name="{shown}" sheetId="{index + 1}"{state} '
            f'r:id="rId{index + 1}"/>'
        )
    return text + "</sheets></workbook>"


def sheet_book_rels_part(sheets):
    """What the workbook points at: its sheets, its styles, its strings."""
    text = SHEET_DECLARATION + f'<Relationships xmlns="{SHEET_PACKAGE}">'
    for number in range(1, sheets + 1):
        text = text + (
            f'<Relationship Id="rId{number}" Type="{SHEET_RELS}/worksheet" '
            f'Target="worksheets/sheet{number}.xml"/>'
        )
    following = sheets + 1
    text = text + (
        f'<Relationship Id="rId{following}" Type="{SHEET_RELS}/styles" '
        'Target="styles.xml"/>'
        f'<Relationship Id="rId{following + 1}" '
        f'Type="{SHEET_RELS}/sharedStrings" Target="sharedStrings.xml"/>'
    )
    return text + "</Relationships>"


def sheet_root_rels_part():
    """What the package points at: the workbook and the property parts."""
    return SHEET_DECLARATION + (
        f'<Relationships xmlns="{SHEET_PACKAGE}">'
        f'<Relationship Id="rId1" Type="{SHEET_RELS}/officeDocument" '
        'Target="xl/workbook.xml"/>'
        f'<Relationship Id="rId2" '
        f'Type="{SHEET_PACKAGE}/metadata/core-properties" '
        'Target="docProps/core.xml"/>'
        f'<Relationship Id="rId3" Type="{SHEET_RELS}/extended-properties" '
        'Target="docProps/app.xml"/>'
        "</Relationships>"
    )


def sheet_content_types_part(sheets, table):
    """What each part of the package is.  No macro type is ever written."""
    text = SHEET_DECLARATION + f'<Types xmlns="{SHEET_TYPES}">'
    text = text + (
        '<Default Extension="rels" ContentType="application/vnd.'
        'openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        f'<Override PartName="/xl/workbook.xml" '
        f'ContentType="{SHEET_BOOK_TYPE}"/>'
    )
    for number in range(1, sheets + 1):
        text = text + (
            f'<Override PartName="/xl/worksheets/sheet{number}.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.'
            'spreadsheetml.worksheet+xml"/>'
        )
    text = text + (
        '<Override PartName="/xl/styles.xml" ContentType="application/vnd.'
        'openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        '<Override PartName="/xl/sharedStrings.xml" ContentType='
        '"application/vnd.openxmlformats-officedocument.spreadsheetml.'
        'sharedStrings+xml"/>'
    )
    if table:
        text = text + (
            '<Override PartName="/xl/tables/table1.xml" ContentType='
            '"application/vnd.openxmlformats-officedocument.spreadsheetml.'
            'table+xml"/>'
        )
    text = text + (
        '<Override PartName="/docProps/core.xml" ContentType="application/'
        'vnd.openxmlformats-package.core-properties+xml"/>'
        '<Override PartName="/docProps/app.xml" ContentType="application/'
        'vnd.openxmlformats-officedocument.extended-properties+xml"/>'
    )
    return text + "</Types>"


def sheet_rels_part():
    """What a sheet carrying a defined table points at."""
    return SHEET_DECLARATION + (
        f'<Relationships xmlns="{SHEET_PACKAGE}">'
        f'<Relationship Id="rId1" Type="{SHEET_RELS}/table" '
        'Target="../tables/table1.xml"/>'
        "</Relationships>"
    )


def sheet_other_part(extent, items, places):
    """A sheet that is not the table's: its shape, and none of its cells.

    G2.2 step 8.  It was written EMPTY once and a reader then met a
    different workbook, so it is written with as many cells as it held,
    each carrying one word of synthtwin's own.  A sheet that held
    nothing is written holding nothing.
    """
    rows = extent["rows"] if extent is not None else 0
    columns = extent["columns"] if extent is not None else 0
    text = SHEET_DECLARATION + (
        f'<worksheet xmlns="{SHEET_MAIN}" xmlns:r="{SHEET_RELS}">'
    )
    if rows and columns:
        text = text + (
            f'<dimension ref="A1:{column_letters(columns)}{rows}"/>'
        )
    else:
        text = text + '<dimension ref="A1"/>'
    text = text + (
        '<sheetViews><sheetView workbookViewId="0"/></sheetViews>'
        "<sheetFormatPr/>"
    )
    if not rows or not columns:
        return text + "<sheetData/></worksheet>"
    place = sheet_shared_place(items, places, SHEET_WITHHELD_CELL)
    text = text + "<sheetData>"
    for row in range(rows):
        number = row + 1
        text = text + f'<row r="{number}">'
        for column in range(columns):
            reference = column_letters(column + 1) + f"{number}"
            text = text + sheet_cell_element(reference, "s", f"{place}", 0)
        text = text + "</row>"
    return text + "</sheetData></worksheet>"


def sheet_table_sheet_part(
    names, cells, classes, styles, n_rows, write_header, header_style,
    rows_above, empty_places, block, items, places,
):
    """The worksheet the table stands on (G2.2 step 7)."""
    width = len(names)
    trailing_rows = block["trailing_blank_rows"]
    trailing_columns = block["trailing_blank_columns"]
    empty_place = sheet_shared_place(items, places, "")
    text = SHEET_DECLARATION + (
        f'<worksheet xmlns="{SHEET_MAIN}" xmlns:r="{SHEET_RELS}">'
    )
    last_row = rows_above + (1 if write_header else 0) + n_rows + trailing_rows
    last_column = width + trailing_columns
    last_row = max(last_row, 1)
    last_column = max(last_column, 1)
    text = text + (
        f'<dimension ref="A1:{column_letters(last_column)}{last_row}"/>'
    )
    frozen = block["frozen_rows"]
    if frozen:
        text = text + (
            '<sheetViews><sheetView workbookViewId="0">'
            f'<pane ySplit="{frozen}" topLeftCell="A{frozen + 1}" '
            'activePane="bottomLeft" state="frozen"/>'
            "</sheetView></sheetViews>"
        )
    else:
        text = text + (
            '<sheetViews><sheetView workbookViewId="0"/></sheetViews>'
        )
    text = text + "<sheetFormatPr/><sheetData>"

    number = 0
    for _above in range(rows_above):
        number = number + 1
        text = text + f'<row r="{number}">'
        text = text + sheet_cell_element(f"A{number}", "s", f"{empty_place}", 0)
        text = text + "</row>"

    if write_header:
        number = number + 1
        text = text + f'<row r="{number}">'
        for index in range(width):
            reference = column_letters(index + 1) + f"{number}"
            # A column named for a blank header cell gets no cell.
            if names[index] == f"Unnamed: {index}":
                continue
            place = sheet_shared_place(
                items, places, sheet_cleaned(names[index])
            )
            text = text + sheet_cell_element(
                reference, "s", f"{place}", header_style
            )
        for extra in range(trailing_columns):
            reference = column_letters(width + extra + 1) + f"{number}"
            text = text + sheet_cell_element(reference, "", "", 0)
        text = text + "</row>"

    for row in range(n_rows):
        number = number + 1
        if row in empty_places:
            text = text + f'<row r="{number}"/>'
            continue
        line = ""
        for index in range(width):
            kind = classes[index][row]
            if kind == "absent":
                continue
            reference = column_letters(index + 1) + f"{number}"
            style = styles[index][row]
            if kind == "blank":
                line = line + sheet_cell_element(reference, "", "", style)
                continue
            if kind == "empty":
                line = line + sheet_cell_element(
                    reference, "s", f"{empty_place}", style
                )
                continue
            value = sheet_cleaned(cells[index][row])
            if kind == "error":
                line = line + sheet_cell_element(reference, "e", value, style)
                continue
            if kind == "date" and sheet_is_iso_date(value):
                line = line + sheet_cell_element(reference, "d", value, style)
                continue
            if kind == "boolean":
                spelled = sheet_boolean_spelling(value)
                if spelled:
                    line = line + sheet_cell_element(
                        reference, "b", spelled, style
                    )
                    continue
                place = sheet_shared_place(items, places, value)
                line = line + sheet_cell_element(
                    reference, "s", f"{place}", style
                )
                continue
            if kind == "number":
                spelled = sheet_number_spelling(value)
                if spelled:
                    line = line + sheet_cell_element(
                        reference, "", spelled, style
                    )
                    continue
                place = sheet_shared_place(items, places, value)
                line = line + sheet_cell_element(
                    reference, "s", f"{place}", style
                )
                continue
            place = sheet_shared_place(items, places, value)
            line = line + sheet_cell_element(reference, "s", f"{place}", style)
        if not line:
            text = text + f'<row r="{number}"/>'
            continue
        text = text + f'<row r="{number}">' + line + "</row>"

    for _below in range(trailing_rows):
        number = number + 1
        text = text + f'<row r="{number}">'
        text = text + sheet_cell_element(f"A{number}", "", "", 0)
        text = text + "</row>"

    text = text + "</sheetData>"
    if block["autofilter"] and write_header and width:
        first = rows_above + 1
        text = text + (
            f'<autoFilter ref="A{first}:{column_letters(width)}{last_row}"/>'
        )
    if block["defined_table"]:
        text = text + (
            '<tableParts count="1"><tablePart r:id="rId1"/></tableParts>'
        )
    return text + "</worksheet>"


def workbook_parts(block, names, cells, n_rows, write_header):
    """Every part of the twin's package, in the one fixed order (G2.2).

    The order is part of the determinism, and so is the order the
    shared-string table is built in: the sheets are written in workbook
    order, and the table is filled as they are written.
    """
    width = len(names)
    codes = ["General"]
    style_of = {"General": 0}
    classes = []
    columns = []
    dates = []
    for index in range(width):
        census = block["columns"][index]["cell_classes"]
        own, dated = sheet_dates_as_day_counts(
            block["columns"][index], list(cells[index]),
            block["date_system"] == "1904",
        )
        columns += [own]
        dates += [dated]
        classes += [
            sheet_cell_classes(
                census, own, block["columns"][index]["value_class"]
            )
        ]

    items = []
    places = {}
    rows_above = sheet_placeholder_rows(block["rows_above_header"], width)
    wanted_empty = block["empty_rows_inside"] or 0
    classes, columns, dates = sheet_aligned_for_empty_records(
        classes, columns, n_rows, wanted_empty, dates
    )
    empty_places = sheet_empty_row_places(classes, n_rows, wanted_empty)

    styles = []
    for index in range(width):
        column = block["columns"][index]
        kinds = sheet_format_kinds(
            column["format_kinds"], classes[index], column["format_code"],
            dates[index],
        )
        row_styles = []
        for row in range(len(kinds)):
            code = sheet_code_for_kind(kinds[row], column["format_code"])
            if code not in style_of:
                style_of[code] = len(codes)
                codes += [code]
            row_styles += [style_of[code]]
        styles += [row_styles]

    published = []
    for index in range(block["sheet_count"]):
        here = None
        if index < len(block["sheet_names"]):
            here = block["sheet_names"][index]
        published += [here]
    sheet_names = sheet_twin_names(published)

    chosen = block["sheet_position"]
    if chosen < 1 or chosen > len(sheet_names):
        chosen = 1
    hidden = sheet_hidden_states(
        len(sheet_names), chosen, block["sheet_hidden"]
    )

    sheets = []
    for index in range(len(sheet_names)):
        number = index + 1
        if number != chosen:
            extent = None
            if index < len(block["sheet_extents"]):
                extent = block["sheet_extents"][index]
            sheets += [
                (
                    f"xl/worksheets/sheet{number}.xml",
                    sheet_other_part(extent, items, places),
                )
            ]
            continue
        sheets += [
            (
                f"xl/worksheets/sheet{number}.xml",
                sheet_table_sheet_part(
                    names, columns, classes, styles, n_rows, write_header,
                    len(codes), rows_above, empty_places, block, items,
                    places,
                ),
            )
        ]

    table = block["defined_table"]
    first_row = rows_above + 1
    last_row = rows_above + (1 if write_header else 0) + n_rows
    members = [
        (
            "[Content_Types].xml",
            sheet_content_types_part(len(sheet_names), table),
        ),
        ("_rels/.rels", sheet_root_rels_part()),
        ("docProps/app.xml", sheet_app_part()),
        ("docProps/core.xml", sheet_core_part()),
        (
            "xl/workbook.xml",
            sheet_book_part(
                sheet_names, hidden, block["date_system"] == "1904"
            ),
        ),
        (
            "xl/_rels/workbook.xml.rels",
            sheet_book_rels_part(len(sheet_names)),
        ),
        ("xl/styles.xml", sheet_styles_part(codes)),
        ("xl/sharedStrings.xml", sheet_shared_strings_part(items)),
    ]
    members += sheets
    if table:
        members += [
            (
                f"xl/worksheets/_rels/sheet{chosen}.xml.rels",
                sheet_rels_part(),
            ),
            (
                "xl/tables/table1.xml",
                sheet_table_part(
                    names, first_row, last_row, block["autofilter"]
                ),
            ),
        ]
    return members


# -- the document cases ------------------------------------------------
#
# These five are a DIFFERENT SHAPE from every case above, and the shape
# is the point rather than an inconvenience: a document case carries no
# column block, no words and no word budget, because none of the
# transforms it freezes consumes a word or reads a column's facts.  What
# it carries is the description's own `source.dialect` or
# `source.workbook` block -- the inputs those transforms really take --
# and the bytes they produce.


def _written_form_lines():
    """A delimited file wearing most of what a written form can say."""
    return {
        "why": "method section G2's written form, end to end, on a file "
        "that exercises most of what a dialect block can say: an Excel "
        "separator hint, a byte-order mark, four lines before the table "
        "in three runs of two shapes, an always-quoted header, a column "
        "padded left to five characters, a second column whose four cell "
        "classes take three DIFFERENT quoting rules, a trailing "
        "delimiter on every record and none on the header, a blank line "
        "after the third record, two runs of line endings, no ending on "
        "the last line and an end-of-file mark after it. Before this "
        "case the written form had no second implementation at all: "
        "landing 2b.9 built it and `grep` for `twin_text` in this file "
        "found nothing, so the only check on any of its rules was a "
        "round trip through the code that implements them. This case's "
        "mutant withdraws the lines before the table, and the file's "
        "lines move.",
        "kind": "delimited",
        "names": ["reading", "note"],
        "write_header": True,
        "rows": [
            ["12.5", "alpha"],
            ["3", "beta; gamma"],
            ["", "delta"],
            ["100", ""],
            ["7.25", "epsilon"],
            ["42", "zeta"],
        ],
        "dialect": {
            "blank_lines": [{"after": 3, "lines": 1, "text": ""}],
            "blank_lines_spread": None,
            "byte_order_mark": True,
            "columns": [
                {
                    "pad": {"side": "left", "width": 5},
                    "quoting": {
                        "absent": "needed",
                        "empty": "needed",
                        "number": "needed",
                        "text": "needed",
                    },
                    "sequence_start": None,
                },
                {
                    "pad": None,
                    "quoting": {
                        "absent": "needed",
                        "empty": "always",
                        "number": "bare",
                        "text": "always",
                    },
                    "sequence_start": None,
                },
            ],
            "delimiter": ";",
            "empty_rows": {"interior": 0, "leading": 0, "trailing": 0},
            "end_of_file_mark": True,
            "escape": "doubled",
            "final_line_ending": False,
            "header_quoting": "always",
            "header_rows": [],
            "header_rows_quoting": "needed",
            "initial_space": False,
            # Thirteen lines stand in this file and its last one ends with
            # nothing, so twelve endings account for it (contract FD2).
            "line_endings": [
                {"ending": "lf", "lines": 5},
                {"ending": "crlf", "lines": 7},
            ],
            "line_endings_spread": [],
            "preamble": [
                {"kind": "blank", "lines": 1, "mark": "  "},
                {"kind": "comment", "lines": 2, "mark": "# "},
                {"kind": "text", "lines": 1, "mark": ""},
            ],
            "preamble_withheld": True,
            "row_order": None,
            "separator_line": True,
            "short_rows": False,
            "trailing_delimiter": {"header": False, "rows": True},
            "written_names": [],
        },
    }


def _written_form_classes():
    """G2's quoting per cell class, where the four classes disagree."""
    return {
        "why": "method section G2's quoting PER CELL CLASS on the two "
        "classes `written_form_lines` never reaches: that case's column of "
        "differing rules holds no number and no absent cell, so a writer "
        "that read `1,234` as text, or `-` and `#N/A` as text, wrote the "
        "same bytes there (files review MAJOR 19, plan P4-D173). Two "
        "columns take opposite rules -- numbers and absent cells always "
        "quoted in the first and text bare, text and empty cells always "
        "quoted in the second and the rest as needed -- over cells that sit "
        "at each class's edge: a point with no whole part, an exponent, "
        "leading zeros, a sign; `-`, `?`, `#N/A`, a cell of spaces, `NaT` "
        "byte for byte beside `nat`, which is text; and `3 kg`, a figure "
        "that does not make a number. Its mutants read every cell under the text rule, which "
        "moves the numbers and the absent cells, and read absence from the "
        "seven spellings this mirror used to hold, which moves `-`, `?`, "
        "`#N/A`, the spaces and `NaT`.",
        "kind": "delimited",
        "names": ["reading", "note"],
        "write_header": True,
        "rows": [
            ["12", "North"],
            [".5", "12"],
            ["2.5e3", "-"],
            ["0012", "?"],
            ["-3", "#N/A"],
            ["-", "   "],
            ["?", "NaT"],
            ["#N/A", "nat"],
            ["   ", "3 kg"],
            ["NaT", ".5"],
            ["nat", ""],
            ["3 kg", "NA"],
            ["", "West"],
            ["NA", "-3"],
        ],
        "dialect": {
            "blank_lines": [],
            "blank_lines_spread": None,
            "byte_order_mark": False,
            "columns": [
                {
                    "pad": None,
                    "quoting": {
                        "absent": "always",
                        "empty": "bare",
                        "number": "always",
                        "text": "bare",
                    },
                    "sequence_start": None,
                },
                {
                    "pad": None,
                    "quoting": {
                        "absent": "needed",
                        "empty": "always",
                        "number": "needed",
                        "text": "always",
                    },
                    "sequence_start": None,
                },
            ],
            "delimiter": ",",
            "empty_rows": {"interior": 0, "leading": 0, "trailing": 0},
            "end_of_file_mark": False,
            "escape": "doubled",
            "final_line_ending": True,
            "header_quoting": "needed",
            "header_rows": [],
            "header_rows_quoting": "needed",
            "initial_space": False,
            "line_endings": [],
            "line_endings_spread": [],
            "preamble": [],
            "preamble_withheld": False,
            "row_order": None,
            "separator_line": False,
            "short_rows": False,
            "trailing_delimiter": {"header": False, "rows": False},
            "written_names": [],
        },
    }


def _row_arrangement():
    """Both halves of G2.1: the sort, and the records holding nothing."""
    plain_quoting = {
        "absent": "needed",
        "empty": "needed",
        "number": "needed",
        "text": "needed",
    }

    def column_form(sequence_start=None):
        return {
            "pad": None,
            "quoting": dict(plain_quoting),
            "sequence_start": sequence_start,
        }

    def form(columns, order, empty_rows):
        return {
            "blank_lines": [],
            "blank_lines_spread": None,
            "byte_order_mark": False,
            "columns": columns,
            "delimiter": ",",
            "empty_rows": empty_rows,
            "end_of_file_mark": False,
            "escape": "doubled",
            "final_line_ending": True,
            "header_quoting": "needed",
            "header_rows": [],
            "header_rows_quoting": "needed",
            "initial_space": False,
            "line_endings": [],
            "line_endings_spread": [],
            "preamble": [],
            "preamble_withheld": False,
            "row_order": order,
            "separator_line": False,
            "short_rows": False,
            "trailing_delimiter": {"header": False, "rows": False},
            "written_names": [],
        }

    return {
        "why": "method section G2.1, whose three steps had no second "
        "implementation either: `grep` for `arranged` or `row_order` in "
        "this file found nothing, so a sorted twin was checked only "
        "against the code that sorts it. Two arrangements stand here "
        "because the steps do not meet in one file: a table with a row "
        "order publishes no records holding nothing unless it also "
        "publishes some, and contract FD5 refuses records holding "
        "nothing beside a row sequence at all. The first pins the SORT "
        "and the rule that the row sequence is written in place LAST -- "
        "its nine rows are shuffled by a key that is not their order, "
        "and every one of the three columns moves as a whole row. The "
        "second pins WHERE the records holding nothing stand: one at the "
        "top, one at the bottom and one spread into the middle, reached "
        "by exchanging cells within each column alone, which is what "
        "leaves every column's cells the same multiset. This case "
        "carries TWO mutants, one for each rule.",
        "kind": "arrangement",
        "arrangements": [
            {
                "why": "the sort of G2.1 step 3 under the number "
                "collation, with the row sequence written in place last. "
                "Column 1 is the row sequence and stands first, as "
                "contract FD12 requires; its generated cells are letters "
                "so that a twin which failed to write the sequence back "
                "could not be mistaken for one that did.",
                "n_rows": 9,
                "columns": [
                    ["x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8", "x9"],
                    ["5", "3", "9", "1", "7", "2", "8", "4", "6"],
                    ["p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8", "p9"],
                ],
                "dialect": form(
                    [column_form(0), column_form(), column_form()],
                    {
                        "collation": "number",
                        "column": 2,
                        "direction": "ascending",
                    },
                    {"interior": 0, "leading": 0, "trailing": 0},
                ),
            },
            {
                "why": "the records holding nothing of G2.1 step 2: one "
                "leading, one trailing and one interior, over eight rows "
                "whose two columns hold their empty cells in DIFFERENT "
                "rows, so that no row is empty in both until the cells "
                "are moved.",
                "n_rows": 8,
                "columns": [
                    ["", "u", "v", "", "w", "x", "", "y"],
                    ["m", "", "n", "o", "", "p", "q", ""],
                ],
                "dialect": form(
                    [column_form(), column_form()],
                    None,
                    {"interior": 1, "leading": 1, "trailing": 1},
                ),
            },
        ],
    }


def _withheld_line_marks():
    """The shape of a line before a table, and the mark a twin may write."""
    return {
        "why": "plan P4-D83 and contract FD11: what a description may "
        "carry of a line standing before the table, and what the twin "
        "writes in its place. Six lines of five shapes, over a file "
        "whose delimiter is the semicolon. Two of them are the measured "
        "defect this rule exists for: a title line wearing quotation "
        "marks gives the mark `\"`, and the twin's first line was then "
        "written `\"withheld line` -- a quoted field nothing closes -- "
        "so the twin missed about 120 obligations of its own description "
        "and could not be read back at all; a line whose punctuation "
        "begins with the table's own delimiter breaks it the other way, "
        "cutting the stand-in into fields a reader takes for the "
        "header. Both are narrowed here to a line of TEXT, whose "
        "stand-in is the two neutral words and is one field to every "
        "reader. The case also pins that consecutive lines of one shape "
        "are published as ONE RUN (review item CODEX-11) and that no "
        "word of any line survives. Its mutant withdraws the narrowing, "
        "and both the runs published and the lines written move.",
        "kind": "preamble",
        "delimiter": ";",
        "lines": [
            "   ",
            "# exported for the unit",
            "*** note ***",
            '"Extract for unit 7"',
            ";; leading",
            "plain title line",
        ],
    }


def _delimiter_reading():
    """Which delimiter a file is written with, settings and all."""
    return {
        "why": "review item CODEX-5: every setting is scored WITH the "
        "delimiter, because the settings decide what a delimiter reads "
        "as. This is the file that measurement was taken on. Read with "
        "the semicolon and no space skipped, its header is two fields "
        "and its rows are three -- the space before the quotation mark "
        "makes that mark an ordinary character, so the semicolon inside "
        "the note splits the field -- and that reading is rejected as "
        "ragged; nothing else reads as two fields at all, so the file "
        "was described as ONE column whose name held a semicolon. Read "
        "with the space skipped it is the two columns it is. The case "
        "freezes the reading every candidate delimiter reaches and the "
        "one the file is settled to be written with. Its mutant scores "
        "each candidate ONE way, which is the rule this one replaced, "
        "and the file is then read as one column under the comma.",
        "kind": "reading",
        "text": '"id"; "note"\n"1"; "alpha; beta"\n"2"; "gamma"\n',
    }


def _workbook_sheet():
    """The twin of a workbook: every part of the package, as text."""
    def census(**counts):
        out = {
            "absent": 0, "blank": 0, "empty": 0, "text": 0, "number": 0,
            "boolean": 0, "error": 0, "date": 0,
        }
        out.update(counts)
        return out

    def kinds(**counts):
        out = {
            "plain": 0, "date": 0, "datetime": 0, "time": 0, "elapsed": 0,
            "text": 0,
        }
        out.update(counts)
        return out

    rows = 22
    half = 11
    first = [f"10{index:02d}" for index in range(half)] + ["" for _ in range(half)]
    second = ["" for _ in range(half)] + [f"20{index:02d}" for index in range(half)]
    # THE DATES A READER TOOK OUT OF DATE CELLS (repair of the stage-2b
    # integration). `recorded_on` holds eight bare days and three moments
    # among eleven formatted blanks, and publishes eleven datetime
    # formats: they go to the three moments first, then to the eight
    # days. `seen_at` holds six days and five
    # moments -- one at midnight, one carrying milliseconds -- whose
    # format counts the smallest group held back, so each keeps its own
    # kind rather than the general format.
    recorded = []
    for index, day in enumerate((
        "1904-01-01", "2023-03-01", "2024-06-15 13:45:07", "2024-02-29",
        "2030-01-02", "1950-05-05", "2012-07-04 08:00:00", "2024-11-30",
        "2001-09-10", "1999-12-31 23:59:59", "2019-10-10",
    )):
        recorded += ["", day] if index % 2 else [day, ""]
    seen = [
        "", "1904-01-02", "2024-06-15 00:00:00", "", "2024-06-16", "",
        "1999-12-31 23:59:59.250", "", "", "2031-02-03", "2031-02-03 04:05:06",
        "", "2020-02-29", "", "", "2021-12-31", "", "2021-12-31 12:00:00", "",
        "", "2022-01-01", "",
    ]
    return {
        "why": "method section G2.2, written at this landing because the "
        "method stated NONE of the workbook writer's rules and nothing "
        "could be mirrored from a statement that did not exist. Every "
        "part of the package is frozen as TEXT, never as the packed "
        "bytes: the deflate stream differs between zlib builds, which "
        "the landing that wrote the writer states as a limit. Four "
        "columns of twenty-two rows reach the rules that matter. The "
        "second column's cells are digit strings and its census says "
        "TEXT, so it pins the rule the whole seam exists for -- the "
        "class comes from what the source held and never from what the "
        "twin's characters could be read as -- and that is this case's "
        "mutant. Each column holds its eleven cells that hold nothing in "
        "DIFFERENT rows from the other, so the eleven records holding "
        "nothing exist only after the alignment step has moved cells "
        "within each column. One column's cells wear a published "
        "built-in format code and the other's wear a kind their "
        "published code is not, so the canonical code of that kind is "
        "written as a custom format. The table's sheet is the SECOND of "
        "three, so the first is hidden for the twin's own reader to land "
        "on the table, the third's name is withheld and is written "
        "neutrally, and the shared-string table is filled in the order "
        "the sheets are written -- the word a sheet that is not the "
        "table's carries comes before the empty string of the table's "
        "own sheet, which no reading of the parts alone would predict. "
        "The last two columns hold DATES as the reader spells a date "
        "cell, and they are written back as day counts of the 1904 "
        "system wearing a date format. The third publishes eleven "
        "datetime formats beside eleven formatted blanks, which take "
        "formats too, and the eleven go to the dates. The fourth's format "
        "counts were held back by the smallest group, and each date "
        "keeps its own kind rather than being written as a bare day "
        "count.",
        "kind": "workbook",
        "names": ["reading", "note", "recorded_on", "seen_at"],
        "n_rows": rows,
        "write_header": True,
        "cells": [first, second, recorded, seen],
        "workbook": {
            "autofilter": True,
            "columns": [
                {
                    "cell_classes": census(absent=half, number=half),
                    "format_code": "mm-dd-yy",
                    "format_kinds": kinds(date=half, plain=half),
                    "formulas": None,
                    "value_class": "number",
                },
                {
                    "cell_classes": census(absent=half, text=half),
                    "format_code": "@",
                    "format_kinds": kinds(datetime=half, text=half),
                    "formulas": None,
                    "value_class": "text",
                },
                {
                    "cell_classes": census(blank=half, number=half),
                    "format_code": "m/d/yy h:mm",
                    "format_kinds": kinds(
                        date=None, datetime=half, plain=None, time=None,
                        elapsed=None, text=None,
                    ),
                    "formulas": None,
                    "value_class": "number",
                },
                {
                    "cell_classes": census(absent=half, number=half),
                    "format_code": "mm-dd-yy",
                    "format_kinds": kinds(
                        date=None, datetime=None, plain=None, time=None,
                        elapsed=None, text=None,
                    ),
                    "formulas": None,
                    "value_class": "number",
                },
            ],
            "date_system": "1904",
            "defined_names": 0,
            "defined_table": True,
            "empty_rows_inside": half,
            "frozen_rows": 1,
            "macro_project": False,
            "rows_above_header": 2,
            "sheet_count": 3,
            "sheet_extents": [
                {"columns": 1, "rows": 1},
                None,
                {"columns": 0, "rows": 0},
            ],
            "sheet_hidden": False,
            "sheet_names": ["Notes", "Data", None],
            "sheet_position": 2,
            "trailing_blank_columns": 1,
            "trailing_blank_rows": 1,
        },
    }


def _workbook_classes_by_spelling():
    """G2.2 steps 1, 2, 7, 9 and 11 as the files review left them."""
    withheld = {
        "absent": None, "blank": None, "empty": None, "text": None,
        "number": None, "boolean": None, "error": None, "date": None,
    }
    kinds_withheld = {
        "plain": None, "date": None, "datetime": None, "time": None,
        "elapsed": None, "text": None,
    }
    # Not every other cell: a count spread over cells that all fit it
    # (plan P4-D187) would land on alternate rows and hide the mutant
    # that lets every class fit every cell.
    status = ["North", "South", "TRUE", "#N/A", "#N/A"]
    for row in range(8):
        status += ["#N/A", ("North", "South")[row % 2]]
    status += ["#N/A"]
    codes = ["00123", ""] + [f"0{1000 + 7 * row}" for row in range(20)]
    days = [f"2026-01-{day:02d}T00:00:00" for day in range(1, 23)]
    amounts = [f"{10 + day}.5" for day in range(22)]
    return {
        "why": "method section G2.2 as the files review left it (plan "
        "P4-D164 to P4-D171), in one table of four columns and twenty-two "
        "rows, at the floor of eleven every case here is held to. The "
        "first column holds eleven errors between eleven labels -- one of "
        "them `TRUE`, which is a boolean's spelling and TEXT by its "
        "census -- so a class goes only to a cell it FITS: handed out in "
        "row order as before, the error count landed on the labels and "
        "the twin carried the wrong missing values. The second "
        "holds digit strings with ONE empty cell, so its whole census is "
        "withheld and only its published commonest class keeps the digits "
        "text. The third holds ISO dates written back as date cells, its "
        "format census withheld and its published code a date, so its "
        "cells wear the date format rather than plain. The fourth is "
        "named for a blank header cell and gets none, and the first "
        "column's own name carries a carriage return, written as its "
        "character reference. The sheets are published as `Data`, "
        "withheld and `sheet2`, so the placeholder for the withheld one "
        "walks past `Sheet2`, which a spreadsheet cannot hold beside "
        "`sheet2`. It carries FOUR mutants, one for each rule.",
        "kind": "workbook",
        "names": ["status\rcode", "code", "when", "Unnamed: 3"],
        "n_rows": 22,
        "write_header": True,
        "cells": [status, codes, days, amounts],
        "workbook": {
            "autofilter": False,
            "columns": [
                {
                    "cell_classes": {
                        "absent": 0, "blank": 0, "empty": 0, "text": 11,
                        "number": 0, "boolean": 0, "error": 11, "date": 0,
                    },
                    "format_code": "General",
                    "format_kinds": {
                        "plain": 22, "date": 0, "datetime": 0, "time": 0,
                        "elapsed": 0, "text": 0,
                    },
                    "formulas": None,
                    "value_class": "text",
                },
                {
                    "cell_classes": dict(withheld),
                    "format_code": "General",
                    "format_kinds": dict(kinds_withheld),
                    "formulas": None,
                    "value_class": "text",
                },
                {
                    "cell_classes": {
                        "absent": 0, "blank": 0, "empty": 0, "text": 0,
                        "number": 0, "boolean": 0, "error": 0, "date": 22,
                    },
                    "format_code": "yyyy\\-mm\\-dd",
                    "format_kinds": dict(kinds_withheld),
                    "formulas": None,
                    "value_class": "date",
                },
                {
                    "cell_classes": {
                        "absent": 0, "blank": 0, "empty": 0, "text": 0,
                        "number": 22, "boolean": 0, "error": 0, "date": 0,
                    },
                    "format_code": "General",
                    "format_kinds": {
                        "plain": 22, "date": 0, "datetime": 0, "time": 0,
                        "elapsed": 0, "text": 0,
                    },
                    "formulas": None,
                    "value_class": "number",
                },
            ],
            "date_system": "1900",
            "defined_names": 0,
            "defined_table": False,
            "empty_rows_inside": None,
            "frozen_rows": 0,
            "macro_project": False,
            "rows_above_header": 0,
            "sheet_count": 3,
            "sheet_extents": [
                None,
                {"columns": 0, "rows": 0},
                {"columns": 0, "rows": 0},
            ],
            "sheet_hidden": False,
            "sheet_names": ["Data", None, "sheet2"],
            "sheet_position": 1,
            "trailing_blank_columns": 0,
            "trailing_blank_rows": 0,
        },
    }


def _workbook_as_written():
    """G2.2 steps 1 and 3 as part 2 of the carried items left them."""
    plain_kinds = {
        "plain": 22, "date": 0, "datetime": 0, "time": 0, "elapsed": 0,
        "text": 0,
    }
    moment_kinds = {
        "plain": 0, "date": 0, "datetime": 22, "time": 0, "elapsed": 0,
        "text": 0,
    }
    weights = [f"{60 + 3 * row}.5" for row in range(22)]
    regions = [("802", "1101", "901")[row % 3] for row in range(22)]
    visits = [
        f"2026-03-{1 + row:02d} {8 + row % 9:02d}:{(15 * row) % 60:02d}:00"
        for row in range(22)
    ]

    def census(number, text):
        return {
            "absent": 0, "blank": 0, "empty": 0, "text": text,
            "number": number, "boolean": 0, "error": 0, "date": 0,
        }

    return {
        "why": "method section G2.2 steps 1 and 3 as part 2 of the carried "
        "items left them (plans P4-D187 and P4-D189), in one table of three "
        "columns and twenty-two rows. The first column holds twenty-two "
        "figures, eleven of them stored as TEXT, so more cells fit `number` than its "
        "count names and the count is SPREAD over them: handed out in row "
        "order, the text cells stood in the last eleven rows. The second "
        "column's numbers wear `00000` and the third's moments `yyyy-mm-dd "
        "hh:mm`, codes built of the format language's own tokens alone, "
        "which are published and written as the source wrote them rather "
        "than as the general format and the canonical datetime code. It "
        "carries TWO mutants, one for each rule.",
        "kind": "workbook",
        "names": ["weight", "region", "visit"],
        "n_rows": 22,
        "write_header": True,
        "cells": [weights, regions, visits],
        "workbook": {
            "autofilter": False,
            "columns": [
                {
                    "cell_classes": census(11, 11),
                    "format_code": "0.0",
                    "format_kinds": dict(plain_kinds),
                    "formulas": None,
                    "value_class": "number",
                },
                {
                    "cell_classes": census(22, 0),
                    "format_code": "00000",
                    "format_kinds": dict(plain_kinds),
                    "formulas": None,
                    "value_class": "number",
                },
                {
                    "cell_classes": census(22, 0),
                    "format_code": "yyyy-mm-dd hh:mm",
                    "format_kinds": dict(moment_kinds),
                    "formulas": None,
                    "value_class": "number",
                },
            ],
            "date_system": "1900",
            "defined_names": 0,
            "defined_table": False,
            "empty_rows_inside": None,
            "frozen_rows": 1,
            "macro_project": False,
            "rows_above_header": 0,
            "sheet_count": 1,
            "sheet_extents": [None],
            "sheet_hidden": False,
            "sheet_names": [None],
            "sheet_position": 1,
            "trailing_blank_columns": 0,
            "trailing_blank_rows": 0,
        },
    }


DOCUMENT_PART = "documents"

# The cases landing 2b.17 added for the transforms that produce a WHOLE
# DOCUMENT rather than one column's cells (G14.3).
DOCUMENT_CASE_BUILDERS = {
    "delimiter_reading": _delimiter_reading,
    "row_arrangement": _row_arrangement,
    "withheld_line_marks": _withheld_line_marks,
    "workbook_sheet": _workbook_sheet,
    "workbook_as_written": _workbook_as_written,
    "workbook_classes_by_spelling": _workbook_classes_by_spelling,
    "written_form_classes": _written_form_classes,
    "written_form_lines": _written_form_lines,
}

_DOCUMENT_ACCOUNT = (
    "cases method section G14.3 adds for the transforms that produce a "
    "WHOLE DOCUMENT rather than one column's cells (landing 2b.17): the "
    "written form of a delimited file (G2), the arrangement of its rows "
    "(G2.1), the twin of a workbook (G2.2, written at that landing "
    "because the method had stated none of the writer's rules), the "
    "shape a line before the table is published as together with the "
    "mark a twin may write for it (contract FD11, plan P4-D83), and the "
    "reading that settles which delimiter a file is written with (review "
    "item CODEX-5). Every one of those rules reached the twin's bytes "
    "with NO second implementation at all, which landings 2b.9, 2b.10 "
    "and 2b.11 each recorded and none could close. These cases carry no "
    "words and no word budget, because none of these transforms draws a "
    "word; what they carry is the description's own dialect or workbook "
    "block, which is the input each of them really takes. They are "
    "computed by the same oracle and the same proof layer as the three "
    "files beside them -- tests/reference/generation-reference-vectors."
    "json, tests/reference/generation-branch-vectors.json and "
    "tests/reference/generation-branch-vectors-2.json -- and live in a "
    "fourth file because the third holds 245567 bytes against the "
    "provenance manifest's byte cap, which leaves room for no case of "
    "any size. The cases the repair of the final Codex review of the number censuses added are a fifth file, tests/reference/generation-branch-vectors-3.json, for the same reason."
    " The cases the reconciliation of the separation walk, the fills of a saturated grid and a column's published levels, and the census of marks at a thousand added are a sixth file, tests/reference/generation-branch-vectors-4.json, for the same reason."
    " The cases the final pass over the close of stage 2 added are a seventh file, tests/reference/generation-branch-vectors-5.json, for the same reason."
)

# The transforms this file's own cases name, stated the way every other
# definition here is stated: the rule, and the section that fixes it.
DOCUMENT_DEFINITIONS = {
    "written_form": "the twin's lines in file order -- the separator "
    "hint, the lines before the table, the header, the rows of column "
    "descriptions, then the records with the blank lines where the form "
    "places them -- each cell written under its column's rule for its "
    "own class -- a cell holding nothing is empty, one spelled as contract "
    "5.4.1's vocabulary of absence is absent, one the number grammar reads "
    "is a number, and every other is text -- (`needed` quotes when and "
    "only when the field holds the "
    "delimiter, a quote character or a line break; `bare` only where it "
    "could not be read back; `always`; `mixed` is written `needed`), "
    "padded where its column is padded, joined by the delimiter and one "
    "space where the form has one, with a trailing delimiter where the "
    "form says so. A byte-order mark leads where the form has one, each "
    "line takes the next ending of the runs, the last takes none unless "
    "the form ends its last line, and the end-of-file mark follows "
    "(G2).",
    "row_arrangement": "three steps drawing no word: cells move WITHIN "
    "one column so that exactly the published number of rows hold "
    "nothing in every cell, leading at the top, trailing at the bottom "
    "and interior spread evenly between; whole rows are then permuted by "
    "the sort column's cells under its collation, stably, the records "
    "holding nothing staying where they were put and the others sorted "
    "into the places around them; and every row-sequence column is "
    "written in place LAST, so it reads 0, 1, 2, ... whatever moved "
    "(G2.1).",
    "workbook_sheet": "the parts of the twin's package, in the one fixed "
    "order, each carrying one fixed moment rather than the clock. Each "
    "cell's CLASS comes from the column's published census and never "
    "from the twin's own characters, the classes that hold nothing "
    "taking the cells holding no text, and each class holding a value "
    "going only to a cell it FITS -- an error to an error kind, a boolean "
    "to TRUE or FALSE, a date to ISO text, a number to a plain number -- "
    "before text takes its count; a cell no published count claims takes "
    "the column's published commonest class, or a withheld class, that "
    "fits it, and a group's remainder never goes to a class published as "
    "nought; each cell's format KIND likewise, a text format first to "
    "text and a date or time format first to numbers, an absent cell "
    "always plain, and a cell no count claims wearing its published "
    "code's kind where that kind was withheld; cells holding nothing are "
    "then moved onto shared rows so that the published records holding "
    "nothing exist; a column named for a blank header cell gets no header "
    "cell; a carriage return is written as its character reference; a "
    "withheld sheet's placeholder is a name no published name takes in "
    "any case; and every other sheet is written with as many cells as it "
    "held, each carrying one word of synthtwin's own (G2.2).",
    "writable_mark": "a line before the table is published as its SHAPE "
    "and never its text: blank with the whitespace it held, a comment "
    "with the punctuation it began with, or text with nothing at all. "
    "The mark is then narrowed to what the twin can write -- it ends "
    "before the first quote character or delimiter, and a line whose "
    "punctuation begins with one is a line of TEXT -- because the mark "
    "is written into the twin ahead of the stand-in and a mark carrying "
    "either leaves a twin that is not a file (contract FD11, plan "
    "P4-D83).",
    "best_reading": "each candidate delimiter is scored at its own best "
    "over the two spacings and the two escapings, because the settings "
    "decide what a delimiter reads as; a reading counts only where the "
    "commonest width is two or more fields and the first record that is "
    "not a line before the table stands at that width; and the candidate "
    "under which the most records share one width wins, a wider table "
    "breaking a tie (review item CODEX-5).",
}

# Where a document case publishes a whole number.  Every one of them is
# a count or a place in a description's own dialect or workbook block,
# or a count of records in a reading; a number at any other path in one
# of these cases stops the run exactly as it does for every case above.
DOCUMENT_NUMBER_KEYS = frozenset({
    "after", "at_that_width", "column", "columns", "defined_names",
    "empty_rows_inside", "first", "formulas", "frozen_rows", "interior",
    "last", "leading", "lines", "n_rows", "position", "records", "rows",
    "rows_above_header", "sequence_start", "sheet_count", "sheet_position",
    "trailing", "trailing_blank_columns", "trailing_blank_rows", "width",
})

DOCUMENT_NUMBER_MAPS = frozenset({"cell_classes", "format_kinds"})


def build_document_case(name):
    """One finished document case, and the exact values recorded for it.

    Nothing is proved here and nothing needs to be: these transforms
    publish no binary64 at all.  The pair is returned so that this
    builder and `build_case` can be used the same way, and so that a
    document case which ever DID publish one would reach the same proof
    layer rather than a second one.
    """
    spec = DOCUMENT_CASE_BUILDERS[name]()
    kind = spec["kind"]
    case = {"why": spec["why"], "kind": kind}
    if kind == "delimited":
        form = spec["dialect"]
        names = spec["names"]
        rows = spec["rows"]
        headed = spec["write_header"]
        case["names"] = names
        case["rows"] = rows
        case["write_header"] = headed
        case["dialect"] = form
        case["lines"] = written_form_lines(names, rows, headed, form)
        case["text"] = written_form_text(names, rows, headed, form)
    elif kind == "arrangement":
        arranged = []
        for entry in spec["arrangements"]:
            grid = row_arrangement(
                entry["columns"], entry["dialect"], entry["n_rows"]
            )
            placed = dict(entry)
            placed["arranged"] = [list(column) for column in grid]
            arranged += [placed]
        case["arrangements"] = arranged
    elif kind == "preamble":
        delimiter = spec["delimiter"]
        runs = preamble_runs_of(spec["lines"], delimiter)
        written = []
        for run in runs:
            for _line in range(run["lines"]):
                written += [preamble_stand_in(run)]
        case["delimiter"] = delimiter
        case["lines"] = spec["lines"]
        case["runs"] = runs
        case["written"] = written
    elif kind == "reading":
        text = spec["text"]
        readings = {}
        for candidate in DOC_DELIMITERS:
            readings[candidate] = best_reading(text, candidate, 0)
        case["text"] = text
        case["readings"] = readings
        case["delimiter"] = chosen_delimiter(readings)
    elif kind == "workbook":
        block = spec["workbook"]
        names = spec["names"]
        parts = workbook_parts(
            block, names, spec["cells"], spec["n_rows"], spec["write_header"]
        )
        case["names"] = names
        case["n_rows"] = spec["n_rows"]
        case["write_header"] = spec["write_header"]
        case["cells"] = [list(column) for column in spec["cells"]]
        case["workbook"] = block
        case["members"] = [member for member, _text in parts]
        case["parts"] = {member: text for member, text in parts}
    else:
        raise AssertionError(
            f"{name} names the case kind {kind!r}, which this builder has "
            "no rule for"
        )
    return case, {}


BRANCH_CASE_BUILDERS = {
    "free_text_joint": _free_text_joint,
    "numeric_pooled_spelling": _numeric_pooled_spelling,
    "identifier_edge_spacing": _identifier_edge_spacing,
    # THE LAYOUT OF A RECORD NUMBER (contract 7.12, landing 2b.18). It
    # goes in THIS file and not the third, which stands at the cap.
    "identifier_layout": _identifier_layout,
    # THE FILL, THE SPACE AND THE MIXES OF A LAYOUT CENSUS (landing 2b.18's
    # repair pass). In this file, which has the room.
    "identifier_layout_mixes": _identifier_layout_mixes,
    # THE PROVEN SIGN OF A LAYOUT CENSUS (plan P4-D156), in this file
    # because the third had no room left beside its two neighbours.
    "identifier_signed_layout": _identifier_signed_layout,
    # THE CASE OF A LETTER AND THE SHAPE OF A PUBLISHED LABEL (landing
    # 2b.18 part 2). Both go in this file, which has the room.
    "lower_case_stand_ins": _lower_case_stand_ins,
    "count_spellings": _count_spellings,
    "level_shape_stand_ins": _level_shape_stand_ins,
    "leap_second_endpoint": _leap_second_endpoint,
    "month_span": _month_span,
    "numeric_point_free_styles": _numeric_point_free_styles,
    "unrepresentable_joint": _unrepresentable_joint,
    "unrepresentable_exponent": _unrepresentable_exponent,
    "long_tail_levels": _long_tail_levels,
    "clock_ladder": _clock_ladder,
    "affixed_brackets": _affixed_brackets,
    "joined_readings": _joined_readings,
    "midnight_days": _midnight_days,
    "mixed_marks": _mixed_marks,
    # ...and the case that pins the two MIXED-CONVENTION censuses of
    # landing 2b.7 (plan P4-D65.2). It goes in this file rather than the
    # third because this one has the room: it stands at 172046 bytes of
    # the unchanged 250000-byte cap, and no cap is raised and no fourth
    # file opened to hold it.
    "mixed_conventions": _mixed_conventions,
}

# The cases the carried landings 2b.4, 2b.3 and 2b.2 added, the third file
# (G14.2): one oracle, one proof layer, and a file of their own only
# because the second would otherwise pass the provenance byte cap.
SECOND_BRANCH_CASE_BUILDERS = {
    "label_numbers": _label_numbers,
    "label_number_tiers": _label_number_tiers,
    # The five cases of landing 2b.3: a withheld pool spent on the unnamed
    # marks, a slashed stamp's one permitted mark, bare dates beside
    # midnight moments, a column partly at midnight, and midnight on two
    # offsets.
    "pooled_marks": _pooled_marks,
    "slashed_pool": _slashed_pool,
    "midnight_mixed_forms": _midnight_mixed_forms,
    "partial_midnight": _partial_midnight,
    "midnight_two_offsets": _midnight_two_offsets,
    # The case of landing 2b.3's repair pass that survives: bare dates beside
    # moments at local midnight on a real offset, whose published instants settle
    # their form and offset first. Its neighbour, an accidental midnight moved off
    # a column publishing a nought, went with the nought at landing 2b.6: no
    # column publishes a count of values at midnight of nought any more, so there
    # is no rule left for a case to pin.
    "midnight_bare_offsets": _midnight_bare_offsets,
    # The spellings of a number landing 2b.2 publishes and freezes.
    "grouped_charges": _grouped_charges,
    "grouped_decimal_comma": _grouped_decimal_comma,
    "spaced_brackets": _spaced_brackets,
    # The rest of landing 2b.2's marks and notations, frozen at the
    # integration of landings 2b.1 to 2b.5 once this file had room: the
    # apostrophe, U+2019, U+00A0 on a declared decimal comma, U+202F and
    # U+2009, with the minus sign and the trailing minus.
    "apostrophe_minus_sign": _apostrophe_minus_sign,
    "quoted_trailing_minus": _quoted_trailing_minus,
    "spaced_decimal_comma": _spaced_decimal_comma,
    "narrow_spaced": _narrow_spaced,
    "thin_spaced": _thin_spaced,
    # TWO RULES OF G9.6 THE REPAIR OF THE FINAL REVIEW OF THE LABELS ADDED
    # (plans P4-D157 and P4-D158): a spelling read as absent is never
    # written, and a partner wears the layout its identity reserved. The
    # third, the proven sign, is in the first branch file, because both
    # together passed this file's byte cap.
    "identifier_absent_words": _identifier_absent_words,
    "identifier_layout_partners": _identifier_layout_partners,
}

# The cases of the repair of the final Codex review of the number
# censuses: the bare remainder, the pooled remainder and the groupable
# cells of a census of marks, the plus-signed tier of a named field
# width, and the saturated integer grid.
THIRD_BRANCH_CASE_BUILDERS = {
    "bare_mark_remainder": _bare_mark_remainder,
    # G9.6's layout packing (plan P4-D182), which fits beside them.
    "identifier_layout_packing": _identifier_layout_packing,
    "plus_padded_field": _plus_padded_field,
    "pooled_mark_cells": _pooled_mark_cells,
    "saturated_integers": _saturated_integers,
    "signed_pads": _signed_pads,
    "spread_conventions": _spread_conventions,
    "unpublished_majority_marks": _unpublished_majority_marks,
}

FOURTH_BRANCH_CASE_BUILDERS = {
    "date_distinct_reached": _date_distinct_reached,
    "date_widths_reached": _date_widths_reached,
    "grouped_thousands": _grouped_thousands,
    # The literal prefix of a record number (owner ruling of 2026-09-17,
    # item 1; method G9.6a), for the whole column and per layout.
    "identifier_column_prefix": _identifier_column_prefix,
    "identifier_layout_prefixes": _identifier_layout_prefixes,
    "midnight_withheld_kept": _midnight_withheld_kept,
    "numbers_carry_the_average": _numbers_carry_the_average,
    "pooled_level_sizes": _pooled_level_sizes,
    "saturated_levels": _saturated_levels,
    "saturated_tenths": _saturated_tenths,
    "separated_in_order": _separated_in_order,
}

FIFTH_BRANCH_CASE_BUILDERS = {
    # The census of marks held on a column with refunds (plan P4-D194).
    "grouped_thousands_signed": _grouped_thousands_signed,
    # The cells no layout is named for, a quota for partners (P4-D196).
    "identifier_unnamed_partners": _identifier_unnamed_partners,
    # A workbook column's truth values written as them (plan P4-D198).
    "truth_values_written": _truth_values_written,
    # A whole number written two ways (plan P4-D193).
    "twice_written_filled": _twice_written_filled,
    "twice_written_merged": _twice_written_merged,
}

CASE_SETS = {
    FIFTH_BRANCH_PART: FIFTH_BRANCH_CASE_BUILDERS,
    FOURTH_BRANCH_PART: FOURTH_BRANCH_CASE_BUILDERS,
    NAMED_PART: NAMED_CASE_BUILDERS,
    BRANCH_PART: BRANCH_CASE_BUILDERS,
    SECOND_BRANCH_PART: SECOND_BRANCH_CASE_BUILDERS,
    THIRD_BRANCH_PART: THIRD_BRANCH_CASE_BUILDERS,
    DOCUMENT_PART: DOCUMENT_CASE_BUILDERS,
}

CASE_BUILDERS = {
    **NAMED_CASE_BUILDERS,
    **BRANCH_CASE_BUILDERS,
    **SECOND_BRANCH_CASE_BUILDERS,
    **THIRD_BRANCH_CASE_BUILDERS,
    **FOURTH_BRANCH_CASE_BUILDERS,
    **FIFTH_BRANCH_CASE_BUILDERS,
}

# What each file says about itself, so that neither can be read as the
# whole of the oracle and neither hides the other.
# EACH ACCOUNT COUNTS ITS OWN CASE SET RATHER THAN SAYING A NUMBER.
# Both said one -- "nine" and "seven", then "eight" -- and both had gone
# stale by four cases and then by five, because a case can be added
# without a hand-written sentence beside it moving.  A count restated
# beside the thing it counts will drift; a count taken FROM the thing it
# counts cannot.  The written half of each account says what the set is
# FOR, which is the half no walk can work out.
_NAMED_ACCOUNT = (
    "cases method section G14.3 names, committed as "
    "tests/reference/generation-reference-vectors.json. The cases that "
    "reach the branches these leave unexercised (review items P2-C3-F3 "
    "and P2-C4-C3, owner decision 11, the month resolution of plan "
    "P4-D4.3, residual R-P4-17's four Phase 4 roles, and G10.5 revision "
    "5's second spelling family) are the same oracle's second file, "
    "tests/reference/generation-branch-vectors.json, and the cases the "
    "carried landings 2b.2, 2b.3 and 2b.4 added are its third, "
    "tests/reference/generation-branch-vectors-2.json, and the cases "
    "landing 2b.17 added for the transforms that produce a whole "
    "DOCUMENT rather than one column's cells are its fourth, "
    "tests/reference/generation-document-vectors.json: one transform, one "
    "proof layer, four files, because a committed fixture must stay under "
    "the provenance manifest's byte cap and these already spend most of "
    "it. The cases the repair of the final Codex review of the number censuses added are a fifth file, tests/reference/generation-branch-vectors-3.json, for the same reason."
    " The cases the reconciliation of the separation walk, the fills of a saturated grid and a column's published levels, and the census of marks at a thousand added are a sixth file, tests/reference/generation-branch-vectors-4.json, for the same reason."
    " The cases the final pass over the close of stage 2 added are a seventh file, tests/reference/generation-branch-vectors-5.json, for the same reason."
)
_BRANCH_ACCOUNT = (
    "cases method section G14.3 adds for the branches its first nine "
    "leave unexercised (review items P2-C3-F3 and P2-C4-C3, owner "
    "decision 11, plan P4-D4.3, residual R-P4-17, and residuals R-P4-48 "
    "and R-P4-68 for the newest of them): "
    "the joint class-and-sign packing of an unrepresentable column, the "
    "joint class-and-alphabet packing of free text, a fold collision no "
    "case change can build, the literal decimal, leading-zero and "
    "leading-plus style placements, the published end whose seconds "
    "field is 60, which the ordinal space cannot hold and the "
    "endpoint-fields route writes exactly, the pooled remainder written "
    "by its own value beside a whole number wider than the fixed-point "
    "window, the month, which is the second resolution naming a SPAN "
    "rather than an instant, the four roles Phase 4 added, the "
    "EXPONENT spelling family of an unrepresentable column, on widths no "
    "digit string can be written at, and, for landing 2b.18, the layout "
    "census of a declared record number, the lower-case key of a form "
    "census, and the shape of a published label worn by the stand-ins "
    "a census owes no form. "
    "They are computed by the same oracle and the same proof "
    "layer as tests/reference/generation-reference-vectors.json, and live "
    "in their own file only because a committed fixture must stay under "
    "the provenance manifest's byte cap; the cases the carried landings "
    "2b.2, 2b.3 and 2b.4 added are the third file, "
    "tests/reference/generation-branch-vectors-2.json, for the same "
    "reason, and the five landing 2b.17 added for the transforms that "
    "produce a whole DOCUMENT rather than one column's cells are the "
    "fourth, tests/reference/generation-document-vectors.json, for that "
    "same reason again. The cases the repair of the final Codex review of the number censuses added are a fifth file, tests/reference/generation-branch-vectors-3.json, for the same reason."
    " The cases the reconciliation of the separation walk, the fills of a saturated grid and a column's published levels, and the census of marks at a thousand added are a sixth file, tests/reference/generation-branch-vectors-4.json, for the same reason."
    " The cases the final pass over the close of stage 2 added are a seventh file, tests/reference/generation-branch-vectors-5.json, for the same reason."
)
_SECOND_BRANCH_ACCOUNT = (
    "cases method section G14.3 adds with the carried landings 2b.2, 2b.3 "
    "and 2b.4: the class debt of a column of labels, whose held-back "
    "numbers are written as numbers stepped from the published ones, and "
    "what the census could hold beside the places such a number may take "
    "(landing 2b.4); the withheld pool of a moment's marks, a slashed "
    "stamp's one permitted mark, bare dates beside moments at midnight, "
    "the move onto midnight and off an accidental one, and midnight on two "
    "offsets (landing 2b.3); and the mark between thousands, the exchange "
    "on a declared decimal-comma column and accounting brackets, and the "
    "apostrophe, the right single quotation mark, the no-break, narrow "
    "no-break and thin spaces, the minus sign and the trailing minus "
    "(landing 2b.2). They are computed by the same oracle and the same proof layer "
    "as tests/reference/generation-reference-vectors.json and "
    "tests/reference/generation-branch-vectors.json, and live in a third "
    "file only because with them the second would pass the provenance "
    "manifest's byte cap. The five cases landing 2b.17 added are the "
    "fourth file, tests/reference/generation-document-vectors.json, "
    "opened because this one holds 245567 bytes against that cap and has "
    "room for no case of any size. The cases the repair of the final Codex review of the number censuses added are a fifth file, tests/reference/generation-branch-vectors-3.json, for the same reason."
    " The cases the reconciliation of the separation walk, the fills of a saturated grid and a column's published levels, and the census of marks at a thousand added are a sixth file, tests/reference/generation-branch-vectors-4.json, for the same reason."
    " The cases the final pass over the close of stage 2 added are a seventh file, tests/reference/generation-branch-vectors-5.json, for the same reason."
)

_THIRD_BRANCH_ACCOUNT = (
    "cases method section G14.3 adds with the repair of the final Codex "
    "review of the number censuses: a census of marks spent as the whole "
    "of the grouped cells -- its bare remainder, its pooled remainder and "
    "the cells asked with a mark where the column publishes none (plan "
    "P4-D142) -- the plus-signed tier of a named field width (plan "
    "P4-D145), the saturated integer grid (plan P4-D147), both censuses of "
    "conventions spread across a column's values (plan P4-D149) and the "
    "padded sign exchange (plan P4-D145, as amended). They are "
    "computed by the same oracle and the same proof layer as "
    "tests/reference/generation-reference-vectors.json, "
    "tests/reference/generation-branch-vectors.json, "
    "tests/reference/generation-branch-vectors-2.json and "
    "tests/reference/generation-document-vectors.json, and live in a fifth "
    "file only because the second and third each stand within a few "
    "kilobytes of the provenance manifest's byte cap. The layout packing "
    "of a declared identifier (plan P4-D182) fits beside them."
    " The cases the reconciliation of the separation walk, the fills of a saturated grid and a column's published levels, and the census of marks at a thousand added are a sixth file, tests/reference/generation-branch-vectors-4.json, for the same reason."
    " The cases the final pass over the close of stage 2 added are a seventh file, tests/reference/generation-branch-vectors-5.json, for the same reason."
)

_FOURTH_BRANCH_ACCOUNT = (
    "cases method section G14.3 adds with the repair of the carried items "
    "of landing 2b: G6.5a's walks taken reach by reach (plan P4-D183), the "
    "fill of a saturated grid of tenths (plan P4-D176) and of a column whose "
    "published levels are its strata (plan P4-D178), the census of "
    "marks held at a thousand (plan P4-D185), the numbers of a free-text "
    "column carrying what the walk of G9.5 step 5 could not spend (plan "
    "P4-D190), a withheld count at midnight kept on its side (plan P4-D191), "
    "the counts of different dates and of widths reached (plan P4-D192), "
    "the sizes of the held-back labels read off their pooled total (plan "
    "P4-D201, owner ruling of 2026-09-17), and a record number's literal "
    "prefix written as part of its layout, for the whole column and per "
    "layout (plan P4-D202, owner ruling of 2026-09-17). They are computed by the same "
    "oracle and the same proof layer as "
    "tests/reference/generation-reference-vectors.json, "
    "tests/reference/generation-branch-vectors.json, "
    "tests/reference/generation-branch-vectors-2.json, "
    "tests/reference/generation-branch-vectors-3.json and "
    "tests/reference/generation-document-vectors.json, and live in a sixth "
    "file only because the fifth stands within a few kilobytes of the "
    "provenance manifest's byte cap."
    " The cases the final pass over the close of stage 2 added are a seventh file, tests/reference/generation-branch-vectors-5.json, for the same reason."
)

_FIFTH_BRANCH_ACCOUNT = (
    "cases method section G14.3 adds with the final pass over the close of "
    "stage 2: a whole number a column writes two ways held by two strata, "
    "by the fill of a grid with no spare point and by the merge onto a "
    "whole neighbour (plan P4-D193), the census of marks held at a "
    "thousand on a column with refunds (plan P4-D194), and a declared "
    "identifier's partners held to the cells its layout census names no "
    "layout for (plan P4-D196), and a workbook column's truth values "
    "written as them (plan P4-D198). They are computed by the same oracle "
    "and the same proof layer as "
    "tests/reference/generation-reference-vectors.json, "
    "tests/reference/generation-branch-vectors.json, "
    "tests/reference/generation-branch-vectors-2.json, "
    "tests/reference/generation-branch-vectors-3.json, "
    "tests/reference/generation-branch-vectors-4.json and "
    "tests/reference/generation-document-vectors.json, and live in a "
    "seventh file only because the sixth stands within a few kilobytes of "
    "the provenance manifest's byte cap."
)

CASE_SET_ACCOUNTS = {
    FIFTH_BRANCH_PART: (
        f"The {len(FIFTH_BRANCH_CASE_BUILDERS)} {_FIFTH_BRANCH_ACCOUNT}"
    ),
    FOURTH_BRANCH_PART: (
        f"The {len(FOURTH_BRANCH_CASE_BUILDERS)} {_FOURTH_BRANCH_ACCOUNT}"
    ),
    THIRD_BRANCH_PART: (
        f"The {len(THIRD_BRANCH_CASE_BUILDERS)} {_THIRD_BRANCH_ACCOUNT}"
    ),
    NAMED_PART: f"The {len(NAMED_CASE_BUILDERS)} {_NAMED_ACCOUNT}",
    BRANCH_PART: f"The {len(BRANCH_CASE_BUILDERS)} {_BRANCH_ACCOUNT}",
    SECOND_BRANCH_PART: (
        f"The {len(SECOND_BRANCH_CASE_BUILDERS)} {_SECOND_BRANCH_ACCOUNT}"
    ),
    DOCUMENT_PART: f"The {len(DOCUMENT_CASE_BUILDERS)} {_DOCUMENT_ACCOUNT}",
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
    "midnight_withheld_kept": (
        17551090684801377981, 16650619119811956828, 12704379148014193341,
        1470516867917299906, 14234896628325533118, 13760769856689378753,
        15843287095454313940, 6686001451241062572, 6483221652129005370,
        10018969653191239690, 16987001854715402434, 6364668551598740481,
        17253496263519568448, 17194042364863309276, 16445183733654758925,
        729837871655531995, 7004220985266061634, 10678429518161287340,
        13216182509454129256, 11526912948551648022, 14395194102043263527,
        15958569293869687487, 13828546498280174558, 14781750980734635530,
        17115347366413959801, 10329361025022159271, 7309268652589156511,
        1941344405543320325, 3513104732651651517, 9082848050828434811,
        9347148726960988599, 8171118197025816307, 14139289071174730690,
        14476290504645707955, 12736271519091695104, 13248514608869633059,
        10048460179392272910, 6808865592907123790, 10489182374973375518,
        3764126484771282562, 17401434261529277290, 1997699371249332940,
        3853191120774194654, 12111613831027796587, 8257035804968719541,
        3281518542951413774, 16902457925941960027, 1577314926174456385,
        3571721316330339128, 3632759249961684891, 6036857599048762757,
        17072643571230322550, 12212353607130513097, 5032079857479771423,
        15279184147750535392, 13921927448296970884, 2714826505722387395,
        14885795702968293240, 5487718275570894882, 16506489437856182174,
        1827811738924048769, 17894970178715192409, 2752034617290294828,
        8858913980465724092, 9006281645932868736, 2220937795758718553,
        17993301598516268751, 10646006485186826300, 10789759814116224441,
        16186222206038569500, 500265645373097072, 17080651452242860349,
        16859383448578883026, 5624084903747257919, 7618968780481998127,
        10390956201801329345, 12454952179642059359, 15647070938746437427,
        7868321390031446875, 17288709147328421915, 9434797129881810119,
        3427540836201938837, 17962470418559468859, 10086523397953569829,
        9426069394118860687, 2854347107458092323, 1446532671212469644,
        14374862207223311175, 2529715503210935193, 10738895422622507309,
        14667472936507844622, 9914567021678529474, 4014399186248788985,
        13235508742897569089, 12789114728251350580, 7483063860254813273,
        3549092466026791545, 3909187779161451529, 4894517832606607801,
        12564778331872822250, 7054617904358594782, 14056521888433651558,
        17699851006796334062, 18424361737082109850, 3425867695814959981,
        15011293075503690962, 7911628907359117596, 10345259859604758229,
        5262758336534277671, 12387325111195293438, 8823330775828479160,
        5051212590319471477, 8907346585770479000, 957770307745227181,
        7401665936957252591, 344460183265729817, 8437626280411890725,
    ),
    "date_distinct_reached": (
        3061740411821215145, 5874610367343361219, 8763751094270247612,
        5493714875881230449, 14547900339701097427, 5360483490234401489,
        10536803725042870699, 4634121734832662942, 12292684201773665750,
        17987454090803019818, 1507538563068616686, 4860554217819105754,
        14236841435124810691, 15509084887108510108, 17949580744652508096,
        9325913314935363107, 11330670882483395081, 10939684036886110394,
        12789058582849516048, 16138779007688339459, 8201492361247696221,
        494462450164762963, 1473961589368021212, 9483618607550906872,
        9614792647402016706, 2981809199062673534, 17115982138301997372,
        1268285901671485301, 17607254743267843318, 12141787224787381149,
        9034400403592133886, 17081299476408104357, 11310060175648228244,
        8213513764028967930, 1550143625696853061, 5193568581522395178,
        18320759549461543706, 343353679643274651, 16981091010189984772,
        1127335032250988769, 7343830754429533202, 13395638553958401302,
        3853518119418589390, 14060982124727088882, 6249284790269974799,
        962254871324899203, 1647226141620182462, 6866328845694261142,
        160857479074612337, 11769048251495170020, 12479270054270521114,
        4612285415428455993, 13083930477738099837, 12743223112995699494,
        14101723170551195202, 8835222895573899099, 13378102330388601998,
        4621241356165817604, 2080566113816425086, 8745400614187005844,
        17652316012369031400, 16817846441060845372, 9578084047924620891,
        17039589895084922008, 4126375629404365791, 1841946999524808557,
        9632250933746799816, 6578030056972447976, 14408466671101935866,
        5897769537137918415, 13637386315398282076, 9137744193588285091,
        2887561890750385031, 18052727225356459682, 6489222072630471669,
        16492792467628536747, 5915660275593679722, 18408678847220776332,
        15851753409565695000, 5027477187603294052, 17077304762508798865,
        11877061373591312776, 15705890308291817016, 17456467651633765256,
        7458870914002113179, 7745945286074027623, 9485252949926794105,
        14919001102759425039, 15687636180685884189, 10978122644559632805,
        1380565965767859697, 5732771784453050942, 7648682236438550391,
        6703324466218905672, 7258176069208112796, 10513181526446384844,
        8516956228476194337, 8187423479071580641, 4939897912566353509,
        239009515722984464, 1570302549466705920, 5023156146789521265,
        13334069172946418087, 4507255431079682827, 7654605772621032415,
        389311098498436713, 6814052246240330990, 13384822115742354385,
        11437338394895598663, 11966325123866449203, 927239868501970815,
        87775699129378448, 14758693293188921953, 837610758122112120,
        1255785365733462255, 4005496808730151489, 9737744793259259161,
    ),
    "date_widths_reached": (
        14503370031981946312, 10866797266022480803, 8287125103648255445,
        11108705830317081577, 16333968570406870456, 10030759462676471524,
        14139967319966187385, 8452089710054864625, 6709729794954378509,
        6209031230569317548, 10616107825243607814, 17490282079299735511,
        8201042098641689693, 16475121054896813466, 15947340541416902269,
        17811804237383367440, 14348986573916741728, 914223630667449887,
        1803977476998879168, 2470995526265008042, 6114870152074773036,
        5014545139925030887, 10597310505843796866, 10269221740081601114,
        7689241243174046839, 14168138758025302740, 16925239941123661715,
        7620178991453369610, 9756488692190460251, 13308397254140816106,
        10018343273389482918, 3251745803743674210, 11794400615492374491,
        3930763003594469912, 16314861076756185012, 5708820582558523157,
        1832331693607467705, 3789485779610978932, 10634189693522173346,
        16591361099430093667, 8780048720305331841, 2746001561619615445,
        14432653669150635819, 5763991315859282061, 15213806625919386031,
        5419991622837870749, 2967813317392210345, 15554097204915943944,
        3888979100133777966, 11092673691278721043, 4790282693615546005,
        10723327437146037336, 2021117712388464576, 5810880655291830001,
        11786649536620733553, 13179049003775934508, 4115665128465393703,
        806615668816766861, 17462785602845384858, 8475917443231798752,
        15086460086292982161, 12150375907463746851, 1044975256463954909,
        17126109290499727251, 18388857861338452997, 17020926993482274192,
        12331286796224238311, 9529525800305607780, 11003782314987078866,
        17700898285568263616, 6235643088442936131, 15536858090847099423,
        9201596883156673215, 13557277156284579949, 8335572171055100393,
        15761648759211362206, 12750000349006915295, 12927329853368049432,
        590043870235632632, 8009178086869916013, 14369347757295465224,
        9682355851595937045, 5864586321055381623, 9220114625122944486,
        3034213714221929396, 657582775195887908, 10208500871916544518,
        11042177312424398297, 10608005239736782652, 1535639717428092810,
        12113558023538034880, 17155130600877507601, 16080438896949696516,
        10084651684459338283, 16163908490087433660, 10406579554241953501,
        12983462217381843630, 10737209616061932065, 11966988928689263393,
        4632107896951899985, 11927270826016244903, 16822010694655451858,
        4772409169570224244, 9258912185553840493, 15249215780016786025,
        6303212565181813929, 6543914570309209687, 15764336083159214746,
        7989279621966642204, 12832292108602039993, 14023964090594969013,
        10816787447296866385, 7258562043135517985, 10824819768088642885,
        9111501418007739449, 1250847132368556878, 1806959428513740802,
        453816639670605496, 4972379801067700487, 16256446635078432001,
        6869595703439404471, 50762772331071480, 9915576901993371334,
        13161554416627718301, 15690530119825638023, 3703525155988520456,
        8285714569848074989, 17784870520283344874, 14163079622034647007,
        6814863221425407060, 3019970333774057811, 9220860368507287000,
        14738739462793145024, 13036750704111579758, 1818890063891153570,
        7402611035981723568, 4973011594125508496, 8477407492454146055,
        8441849475738023893, 10859725886648518445, 15041772982091045833,
        7661393699094030752, 7952595765015330510, 934561596451465384,
        6014435017725633725, 8766297133615031409, 5172576490018880616,
        6306293910861366171, 13976761765960603492, 6968752022453786186,
        2288397721481960300, 1245103124046357554, 5413929969708689040,
        15713347547806987945, 16103736577416861924, 9183068736795409678,
        8622311728014625025,
    ),
    "twice_written_filled": (
        9807102915954300313, 1533499287027722403, 18268952151052867855,
        12060899387110967807, 10860169690069155741, 16405807712074503210,
        11336088225392016739, 2199797941764082403, 13739613106571616197,
        18334924317143458956, 4063140605235012501, 16735655150261518428,
        11476877683815293559, 17792322667094641263, 12014792995761957629,
        5546249749367379967, 2054948804072260868, 8843760835513865372,
        8921864288772521283, 1043303225908046733, 13531801461799973060,
        1312901891449209078, 12638412808799657383, 6604206209950781413,
        9159008789754050014, 9850019097210461608, 9078212282080136838,
        16062800011441196216, 11024637831316460781, 1054563244285494147,
        14217947680471629166, 12494806716618703808, 8487968904770489354,
        14179523892304556319, 14300323049879018697, 7702075684126994096,
        10387428897563260934, 16460161366402206157, 9779607677780132610,
        7359278948084398671, 1365355997015429071, 7910910513118479494,
        9046696453008240357, 11808962128504117011, 5907786448897427363,
        15258910377865481342, 18276120277371717161, 653860939496642140,
        11750185583532740204, 2926393443850106355, 12663527996916665122,
        15526235133111378989, 17863175474026329274, 10674844640458800832,
        1685502358086292255, 2068178283234361881, 980707999487100314,
        10527962165262783203, 11940237489962913421, 8709957525082340366,
        17248150222454450564, 12225533581493515641, 11403195766673220243,
        17892774679099047886, 8091529709238459994, 7165727519895529347,
        344173643448963457, 1172731408924079945, 7159376183485932204,
        14993078684666494856, 9259832398559991538, 1828606630694215736,
        6710665284434231816, 15691012611080758491, 4359192425805010911,
        16589627835342335060, 5213741823166526012, 8146321774261281396,
        16573630057958593333, 5659440468652638042, 5532891247317196394,
        17039249489079275410, 15588517994549673291, 4767767765745599977,
        15543608561451580053, 18427540554821171873, 11808744165459225662,
        13011499182488043987, 14011887690245873623, 13821131567305158457,
        7334475033472636811, 14990006749503847837, 12405236883591238526,
        1861542916895868644, 10907038022445448462, 5848479566958409677,
        13394087866135454608,
    ),
    "twice_written_merged": (
        17941141834044325940, 14632875602993385311, 1862964910129272931,
        7363349168769164783, 10905083648639855186, 12679517769122161104,
        5369928061998501952, 14149119457853621279, 2369194901864358058,
        10440462113439885886, 10470231362912602076, 14464120173577525591,
        11151443790158101993, 18092319329684162870, 13000430769986063631,
        12133323377778885408, 4820289028885458240, 2002056790605865618,
        17185272890892055757, 872275374056328234, 2717430306966218220,
        2467500710049965192, 5118748686751558798, 15764242969079277010,
        16251094162997129511, 5905145003520722963, 9338937380208644096,
        15727110635765447088, 1706602891273181323, 6996846332238721061,
        9355617325862668404, 1462911225084311079, 8003742341482945701,
        9391411819831992840, 8977085388481956218, 13590558613441251117,
        539121795653847616, 10293424940174116985, 13019922291688965959,
        12040277978966163042, 6304079187398257782, 14485882459981124634,
        11609117520597510371, 11254564439295682884, 12714468921962315229,
        13822972392035162507, 1893444944996769225, 8938236064161844909,
        17650531480333116824, 14150240104731752243, 17474247189529220076,
        7293533692642602194, 18433963793544359861, 8897103369927101066,
        7951466397750767904, 15538889139360837295, 10614738487572276606,
        5430917947221349670, 15348424941277940027, 722121686270846841,
        6529774961653100056, 16872555452065103719, 116755439182217275,
        16920865390407826573, 13440839399673389038, 16199239915310000628,
        2669061496563282748, 1469928219296655217, 11528670697013833693,
        13819738769330299168, 14639405829595498708, 5889069431413270485,
        6879310536419436465, 11862151229248521760, 12210652471992693469,
        10074653044288614926, 6906772344722180470, 10100795457891813292,
        16373602583696267104, 2642057701305312903, 3071943731113988213,
        8246230164498673047, 9702191232940167731, 10339425341125031740,
        3896566248825868558, 2243792059062295508, 3178383758616819416,
        40547085148408980, 615306504248009032, 17887963927018895161,
        4730173464511932072, 14545911963571886087, 16905505775258707312,
        10892877730744188944, 5317318492369062559, 11550158690267553171,
        4171607160914778088, 13990584268567972547, 14189884023817311489,
        2899485916812505692, 11306746194681249213, 16752901920372956797,
        17928493761582744681, 11061644431823411053, 15513550840873650291,
        7934469473966306063, 18055550523792248467, 5490762053517788937,
        4106344814970686777, 108223448409825497, 12995969785168454426,
        10565515385444184662, 18130538850862103141, 15950525092357073735,
        7054028094876032818, 13956858393576102721, 701468661446754139,
        8588256808573578130, 14104470163682385804, 11550104608444942108,
        15722878387300869045, 4785160873426347094, 11318782721475158477,
        2506653207403379257, 14905726631369685909, 17281674914564274087,
        5056064720274300460, 3851070252375274713, 13079390315137301171,
        2821987267926086543,
    ),
    "grouped_thousands_signed": (
        16764337760561268504, 2731616558881925338, 17185388039533249358,
        16031378487509627551, 15160868482438834999, 6637459220541204986,
        15123971167182751075, 3351835981126318400, 3922164463738353987,
        12838904352352051024, 6749974009010182171, 11897635254429754797,
        3589255144021274194, 2272530937002182543, 17723882233313489793,
        17880655199774217365, 12903243294484815341, 6060319119888242051,
        9792324251942424635, 1316350560725249257, 11298045394577903508,
        319787961644205726, 4227536886557650405, 3166140487822241612,
        14580508496985908028, 12477511979628408542, 16006882270660894428,
        10255978691090338018, 11969493266267571745, 17124451362386733504,
        17999064314377457741, 11619338791520210541, 4648542702066671943,
        3166176537359448825, 13854899688496727299, 12854584151190606912,
        643817797855686085, 4668018689313732711, 11856565551534559409,
        13347311644159046894, 11947745601761639628, 4615861695526443095,
        4823975300852224202, 4982792375470054363, 11902251730531125228,
        12163044196976761632, 12615304700235415088, 8090137416499771209,
        6206666377834488744, 5838079606327013852, 15118918263967301859,
        16282177319729402544, 2946751026715272847, 15358258244492707711,
        16354300077055048188, 17734105561450111891, 5516491044845484039,
        6580534715984554274, 716820483704791096, 11248283820011754988,
        15341664938743949054, 9664387329628178451, 10601925008818727566,
    ),
    "identifier_unnamed_partners": (
        328013719168398332, 10766562923109368970, 16233426283648288427,
        13239842561461432069, 14800997116164779575, 4377843721856348356,
        7222283941641418829, 7232807586903716336, 4315214641349666465,
        13079633532412175305, 12140737764186525698, 11480906620815575688,
        172832741148225563, 3701825696883128410, 5352797094984980934,
        10446816553269624071, 14013187791600110188, 9559059927570196849,
        13257472263824864606, 1362579972805652153, 17937509842064448139,
        8788690047843151584, 14525690285098805381, 2791640362165878406,
        1517141610631836426, 449048779143352735, 2900156140636176997,
        8101479771955358020, 17208540454124857984, 1508648639110351944,
        5742590452969085064, 16397150062865857893, 15071087078404451892,
        7478694804942252120, 10219456386863542526, 17899529849511623624,
        15182428401504193236, 3569707100093630577, 13063176584291511810,
        12097044742257023668, 4989164670432844878, 16397286255010340607,
        16754686801907319504,
    ),
    "truth_values_written": (
        8981042716644221465, 2594304037482169389, 8493817443954993786,
        15260377241988477239, 2596126174957726585, 508029927280819144,
        3517168720076184496, 1046876500064735596, 4536341902756269341,
        7344723933826314326, 16894106758750882493, 8812529051543134519,
        13116912689864044726, 6521778171008371473, 1024194013544763580,
        1039422670693554331, 11064341314598592928, 17841714156589934435,
        17653894005588130276, 5336491974741777481, 16719485571701108735,
        588539776915580619, 12008556488172240525, 7149429951284806153,
        1110101954372367595, 2159851726275514585, 11334768227782759701,
        527807927264194347, 7974245992836738982, 12317518035908784132,
        15377880167602324455,
    ),
    "identifier_column_prefix": (
        3061740411821215145, 5874610367343361219, 8763751094270247612,
        5493714875881230449, 14547900339701097427, 5360483490234401489,
        10536803725042870699, 4634121734832662942, 12292684201773665750,
        17987454090803019818, 1507538563068616686, 4860554217819105754,
        14236841435124810691, 15509084887108510108, 17949580744652508096,
        9325913314935363107, 11330670882483395081, 10939684036886110394,
        12789058582849516048, 16138779007688339459, 8201492361247696221,
        494462450164762963, 1473961589368021212,
    ),
    "identifier_layout_prefixes": (
        17551090684801377981, 16650619119811956828, 12704379148014193341,
        1470516867917299906, 14234896628325533118, 13760769856689378753,
        15843287095454313940, 6686001451241062572, 6483221652129005370,
        10018969653191239690, 16987001854715402434, 6364668551598740481,
        17253496263519568448, 17194042364863309276, 16445183733654758925,
        729837871655531995, 7004220985266061634, 10678429518161287340,
        13216182509454129256, 11526912948551648022, 14395194102043263527,
        15958569293869687487, 13828546498280174558,
    ),
    "pooled_level_sizes": (
        14503370031981946312, 10866797266022480803, 8287125103648255445,
        11108705830317081577, 16333968570406870456, 10030759462676471524,
        14139967319966187385, 8452089710054864625, 6709729794954378509,
        6209031230569317548, 10616107825243607814, 17490282079299735511,
        8201042098641689693, 16475121054896813466, 15947340541416902269,
        17811804237383367440, 14348986573916741728, 914223630667449887,
        1803977476998879168, 2470995526265008042, 6114870152074773036,
        5014545139925030887, 10597310505843796866, 10269221740081601114,
        7689241243174046839, 14168138758025302740, 16925239941123661715,
        7620178991453369610, 9756488692190460251, 13308397254140816106,
        10018343273389482918, 3251745803743674210, 11794400615492374491,
        3930763003594469912, 16314861076756185012, 5708820582558523157,
        1832331693607467705, 3789485779610978932, 10634189693522173346,
        16591361099430093667, 8780048720305331841, 2746001561619615445,
        14432653669150635819, 5763991315859282061, 15213806625919386031,
        5419991622837870749, 2967813317392210345, 15554097204915943944,
        3888979100133777966, 11092673691278721043, 4790282693615546005,
        10723327437146037336, 2021117712388464576,
    ),
    "numbers_carry_the_average": (
        10626364091995481622, 12324380702380665290, 10206021613485447140,
        3833008408733653600, 3279155949837417361, 9726853267425906631,
        5483846556130625623, 17748825266372060920, 15858599329263601550,
    ),
    "date_peak_heap": (
        14766693206355676505, 6992157754349396863, 7838749716675263788,
        6260884635299288984, 16683963525250038006, 2929686537832769934,
        2071875313487354258, 13349647098881792378, 1551110936622519113,
        1353110449592196458, 17307339043402969394, 6151673706957319088,
        1919595005328611936, 8476328626393059232, 15247229415546912329,
        6517722599748709312, 11553436059773369373, 11269210997479015415,
        6167618492286883184, 14625991199064179370, 8138596820396397001,
        8539488409251745151, 779240757970203613, 16679182503145436217,
        11982031602075414604, 5508324759865584647, 2610525744345252956,
        8749227166237231008, 18242928711690456347, 7498450071216871015,
        736853949146623621, 6729718628367637034, 14304344870152288214,
        7616852576711505503, 8381666801314064950, 13780545569617316078,
        4826664362350657762, 3492663118806061649, 6089009591588996131,
        17756337892691158891, 16719592472474065696, 72079691224040853,
        6523895488822866630, 5647034530723381259, 5029885900170472086,
        12793461229313348238, 1303226997728965567, 8258220809841507654,
        11130630313922382584, 9676368676516251084, 4659117894285289725,
        2201284052227080037, 7227452119973509919, 13727759001878204432,
        9795480541515733080, 6434767888092282255, 994462249439909175,
        12118406020017173180, 15104171236716321650, 6920231579164432269,
        4962820653922746784, 12434911003628762574, 1656476672774081503,
        3791232627580938504, 15974657973910230499, 5129423072227879236,
        18191266426893455499, 2844670899663405278, 11703772692705477423,
        7065468433315722716, 385531002873873270, 5614027444090623099,
        10561073587658038565, 1483354294859502419, 6996927556167716518,
        10118285601421975715, 13817057510851749147,
    ),
    "date_thinning_week": (
        11079678160230914977, 4954812553690575453, 16055455646014030800,
        3862566106636356417, 16245795031161184184, 12569060163420238655,
        5009103289862267414, 14215352683306337838, 4865000564004434859,
        16796880053323686440, 5194306685916341992, 7847678842380058076,
        5230705852901393350, 11798063569124903186, 6075326664027947,
        9455656810271046659, 11701532591040608264, 3579216433710878606,
        12411381346985564628, 2716908277590758005, 11965093471224593099,
        12633817745152957120, 2274065125571139258, 15394111227982530067,
        15649011496529710023, 15469938750659786732, 15777769424741237768,
        17891270777846587067, 7705746092959135942, 17068665242803066670,
        515995206931573676, 9324249909376588643, 8872584017910170190,
        14932960399753190805, 15607457803414003521, 17750121684488565463,
        1599950418171924953, 5060213957147658689, 1603727249314529272,
        8126335040947758948, 2053321559920411412, 11189687114212635589,
        4268490824490242005, 8703147062316955401, 10322674905973002807,
        17787473613551231505, 519604157333400118, 41980820982561003,
        667108904226507373, 2318141621240746246, 14441661313213643469,
        18302446780740922673, 11646858179307892659, 5015360047219947662,
        5412554084687807230, 6731110393170337823, 12901609537192193203,
        12967157853018607235, 3839606383366968531, 4603813393130198212,
        528261728206944320, 1797334392541920177, 7207154503668962165,
        13126400342626726343, 13379377835769567197, 14867530458230300932,
        15140659055465307474, 11011854492896435342, 1323904669204375680,
        11120658615021462214, 16172915239446243357, 13518863192834238754,
        11381489319053512577, 17182182428581280277, 351165963239372741,
        17316092617392718017, 12973131163195499433,
    ),
    "date_gap_places": (
        13582273234154262364, 18398104693322419879, 34070170978230141,
        3341762675134395213, 9954870715852195741, 11074722499558924578,
        7086877514108549857, 5428095448531052280, 9858665311344715186,
        14335373683300192717, 13568817218928113682, 7443554488824773121,
        1507543091965614910, 15036176574875485406, 11305006835104430484,
        3919574237267079812, 4662566541854203892, 2785393505384254902,
        18167102002877775314, 5359666550153224208, 7236600271796893858,
        17385850831391360195, 3925679704441438369, 3038158995283776929,
        15701766632821214956, 13026092740937741156, 2498239939632209053,
        17296191950373657039, 6847993915250886595, 12485244363494887806,
        51361926512820441, 12713452909872939155, 17194683308519976880,
        9494292973446406325, 14730974571768802911, 2841443329483980571,
        2667530140144481129, 11380515728777247132, 737974217191884336,
        10391720074859047821, 18293336038511823674, 3525874951485151382,
        4517838858738345043, 3258589018767612300, 6706364538686908349,
        11182159666482384533, 3516022594493227618, 6308409673052286782,
        11850633565165211552, 7679926888191552712, 1657569582579748018,
        11972005199951131055, 10028842102051215123, 12742782212818117389,
        9933968653272506701, 496418581426523829, 14144889129156548452,
        15965513364425147980, 374061103416361254, 15654188217680370882,
        6455266257794122148, 7385787955482912886, 10113432378818351743,
        15354656899906861865, 734920368336317215, 3847523236932794809,
        4146042310942044437, 11197141226713801472, 16678001095954234764,
        8611373354917936658, 15212068172050906663, 12694360102965796299,
        2455431899680794908, 6257650374097338146, 5035423415907333659,
        3519908956784654975, 4766840363336960650,
    ),
    "may_month_names": (
        7624411207500017663, 18018633891298768539, 9327666861298971719,
        12069654061041524425, 13056208526174774753, 16270608102264184673,
        7136254884387832689, 2146649404055757979, 8299392471497780641,
        2314006865244965464, 6452669892852346852, 14498537279786915597,
        5807170461159552380, 13761051749839567673, 13496788994203422708,
        17658594639995542130, 11946899400267459287, 8643193479102873906,
        7601562399756904492, 5111893150072507382, 10575175848735182819,
        8657697069614245099, 13726072828175306438, 5859875945738675844,
        808640240039876655, 9923500839825069631, 17981466901741366856,
        7759697397388857000, 9890344465002701988, 16504403711328310884,
        5583668501587289150, 12607117446844355094, 6416464472314343483,
        7592797837861997308, 15138115336174373457, 4935601597921276445,
        10758720803369674723, 6964314223450828242, 15292528797945022755,
        13740842348072460030, 15396328783190958164, 7719600006794446018,
        905991238421201453, 56940693478711805, 11659378853640090815,
        13667056686878142958, 13591130304668766307, 5611183999838444833,
        14486748888324642628, 805064969381655923, 5779178795863039304,
        2517284497528460800, 7660217245323276297, 3944086074187690930,
        5372858886023790304, 6782654724682573173, 16671154529923172776,
        15562778397555716616, 17512210119283651415, 11567803277685074371,
        14850724956931474721, 15592690270084742326, 385981727893807494,
        15848880712555865719, 8137220622671396494, 7656217565899852781,
        1144373002008331905, 6602777931861346560, 17841643452398935496,
        2506193253089931904, 1309043816144866151, 7708036139903193080,
        9025252944961652358, 8967701710532311394, 3487065727761632458,
        9934413647790001839, 8563300156939537552, 2760514152702228199,
        8868029545318544314, 12562004475371503752, 14190205986353647595,
        2629143075635293573, 10487506365024993360, 6739891884306616565,
        1878536241103684347, 3042520936062070123, 1224816337772787332,
        15859284841252763922, 8399253708832300187, 8231292199958444561,
        267999977985944891, 15329268351129830934, 8625128670384588298,
        9629229551755704301, 2212292450141092125, 17951824220492435690,
        16538119457046801484, 229215839790942484, 6009309351158102581,
        5338620045300819643, 8893160517664995548, 5217683502981550127,
        3717397070281156217, 13501784885117613869, 14595536583200122307,
        8729445688262197857, 11804382767031582502, 16547910807485101073,
        4421150326374061424, 16014603019965692538, 4310419175388662263,
        8399851095629229409, 4524278052714247995, 12760947352800175382,
        15556524842886129440, 8137365897068648256, 2026758182161805605,
    ),
    "month_first_widths": (
        411179136531786142, 1982861595377018348, 11950373906050309963,
        17721752918347183196, 14209512559177407037, 16754303442300708120,
        4204783424237075846, 4681831488814884530, 6446403972659101316,
        8427775216937654035, 10211324520233377560, 14897660508276153688,
        4119102538551897917, 11528631760795248871, 13680582909623253025,
        5050023849856481481, 15426892616632391898, 1344415077473076424,
        3548945409361116972, 11196694034525503384, 14134339850899949647,
        15165696423381130897, 928241016773350984, 15642353362727755533,
        17362049571715137677, 15242205530261741041, 12959114041094333088,
        16865646998156285503, 15816863424214543421, 9801909270355076948,
        13728644927686090528, 1786202545825901014, 15538461658316695806,
        9644221894854668897, 6086745284886571550, 3127861309882536035,
        18132025607915282028, 2842718885136013032, 17241930218749103116,
        11769528337410745237, 3850826887315116052, 1002220865474413709,
        14075977698047610473, 5313044812902553181, 9210600903144167403,
        13576584346228663122, 3663643525571522422, 3552571132942207646,
        9565653044739084407, 4476061822367667314, 15935959815877436672,
        6403099971614457318, 11088012163186082225, 11095367244768531463,
        11941700571575285519, 2379930996147948145, 1955096052585405554,
        17049134867150053668, 10774395072817291487, 9843786281826380692,
        14492276334385789553, 11074664596990320200, 7818360990588182762,
        1867696055970647816, 11200790933624410449, 638309788351256812,
        3787310517169562468, 16403101154199417981, 10657160950261735322,
        6221448103850843730, 13661847569940294117, 10163873516409404965,
        16988335295198201096, 6396025306240461033, 3887233775807296745,
        8914788032463173469, 9452505947385594084, 17417394955496580473,
        2352815866357263676, 17437323303254055949, 3459099539059255397,
        18255219232487623935, 3768917603948231104, 17440364014431786452,
        12948655395728103603, 10157491014976767066, 12206205453975203626,
        9202583578927681270, 7851036029079190878, 2975664875499536293,
        9901783940380317614, 3605211869800606754, 18312056231403621872,
        1973696451736411069, 7942003875206605288, 14917770109698994816,
        12389731789689874765, 3638949933892086143, 7073925058834514027,
        9316046909703266377, 138078049388591866, 11961864247517425040,
        2931561304536649676, 9384740067447835997, 11724434961959452881,
        9119066722579331924, 6406834048616516286, 15635722290643100831,
        14905501778878416464, 6406021435679565582, 9883646930997604554,
        8466450575998059501, 4819874132864666478, 11682646618220050432,
        9908875432428958714, 4932027330917746235, 4372836446734248766,
        632371899483025425, 15686285522474206717, 8328887754863586730,
        10327989218327734635, 5345580297214523348, 82455626676672626,
        16094329303020788750, 12338479874812628152, 6799900024413448020,
        1888286422515864212, 15445931168191014177, 9567541687797507218,
        13794241483115522894, 14903833624867689943, 14042228942360637079,
        15290286991052671256, 5057162519325636383, 13694753004799791277,
        16009584575343888391, 3066718014106726196, 15632463617834816528,
        9499652758200475511, 8230973084346629935, 12098504964439687067,
        502274704102108626, 1940995440909574143, 16454116080535054363,
        3585997863464261346, 10755140139989322426, 15131322259882437229,
        6873497722355805633, 10278296925117640323, 4366553848268032246,
        15479383200039777841, 17238311582049077504, 552055450390777709,
        10716461978115377217, 8303388334756885260, 3449629778044979667,
        17813848995454805689,
    ),
    "reserved_name_floor": (
        14623874773869021584, 1101037575172097884, 5528030038320947979,
        1699340121551730223, 5454536252365829639, 1333847586185654792,
        17367226935657727899, 15206410914701422190, 9158671040774120562,
        2847321121796634861, 3399716060311506324, 9499599905314123420,
        3051216536723952660, 1208495941364316850, 14853431797248919579,
        3319744482987375808, 15502635411836727604, 2103947150920060691,
        12132576086552238465, 16326155779624797612, 13388441183058422449,
        8076135440911114655, 1565888969560626412, 4520163913881794397,
        11893059189667771165, 12455213725711919012, 9141233052823609683,
        14085275310457618459, 15253271526096648295, 4451797894901836087,
        3987687593621620212, 15308600684770179542, 17341966074345044894,
        2732801519954006964, 12626772174586582950, 10293069316180546743,
        1437633474046423043, 5153890254976745998, 6340772465703091576,
        464993280591146766, 3703185578599393983, 5466984106213162016,
        14681180694026834037, 13125109837185110329, 14331615095099845517,
        8888473045443467731, 8601508638089744456, 7464430089623489557,
        8218178065693237477, 9437984029933491426, 8897354558295532528,
        12354909706614814710, 7348291356150268448, 9417309548711967136,
        9485351808358171794, 10326315335785634363, 11443964344319546858,
        1173689839334216406, 11661854196924763153, 15673530368129812832,
        6620251914062754495, 501558566552455045, 6602903477725220906,
        14373863816331114938, 13666727983278221077, 628751199085098848,
        13536575237492494218, 10462784050771066947, 6733380652916483413,
        4161010082677869325, 5708465227444101763, 10033966980455710473,
        14712806327218517384, 8633916700064892745, 15444497031438146400,
        2110329586575307916, 8117987480605378558, 5902837482755024816,
        17328345872520175831, 11460201502140085074, 9545891024025883835,
        16794107050916823933, 14532499305748203100, 4701332688300008424,
        17192204656337117218, 6244928794548366517, 2300924658641544161,
        5537922084714231767, 2298268045110366501, 738218565872598432,
        18106830409664396687, 741004680788995115, 17738663479198600070,
        18176114160339740264, 794059215261464934, 8841952738601512434,
        11047982240278322272, 8332516584242874547, 12289793846246020017,
        13655851112103408406, 13455720045157898040, 6210290200932685741,
        11366821022591337199, 11595059985168785951, 940556683472547086,
        17234113755524698283, 12024101677787473005, 12261416769281802181,
        11150656840147725573, 13012614294713038304, 17412104601454545783,
        15105031069839681244, 2100161541399946618, 2233435826553224402,
        3002586960114501916, 990047594424617782, 4949717121568885802,
    ),
    # THE FIVE CASES OF THE REPAIR OF THE FINAL CODEX REVIEW OF THE NUMBER
    # CENSUSES (plans P4-D142, P4-D145, P4-D147), each on words of its own.
    "bare_mark_remainder": (
        10230562801701554171, 10882335407542933515, 6570972072887124803,
        11857385787778254424, 11681720171326079955, 6697628568793574888,
        6506093658873571512, 173444645080011720, 8790126255322325552,
        8526121642652699146, 7867282631661948028, 2927330444169323273,
        4867773957703973463, 9351438374392144045, 7740983589954650251,
        4398855351457282119, 18157944978038611123, 2205944257538293394,
        7745775686338785774, 3606453119442194128, 10248005926873581348,
        15882956519972502681, 544139770496131276, 14365378523966179831,
        17814902903086060267, 1924418624669310983, 5211734944709046033,
        12856630741275191957, 8707376934106425517, 4744523554769013776,
        6918410480491980403, 17494621849549501098,
    ),
    "plus_padded_field": (
        8644321475060649706, 13342060022048535175, 4386477189466737275,
        4817317762195363321, 10838217378249481108, 3193400635613152710,
        14610496117762081290, 4480871890857582723, 8482016572596299882,
        9934854820934900419, 17619945725788226678, 12191743190426113647,
        17124417922633490440, 10563810070520916058, 4530325858210985661,
        8175653497514675007, 13683103267468974161, 911020027536109385,
        15770637544372271411, 8150443195637369686, 7986483148572826507,
    ),
    "pooled_mark_cells": (
        1322960043824829993, 4304802946738339076, 11895184769386787494,
        15009259507049410023, 78993831906502904, 10971129210712623180,
        4454802098459831302, 3919104916175081190, 11301454504177651760,
        10876104050411173251, 3818899092672013249, 14689249687027394562,
        3151252208776280391, 18235135037081768198, 835930238996300419,
        7503890040188187972, 9114893047779386832, 7017482890592370321,
        7147789796798429405, 5347282328632239398, 771449634150066618,
        1131677457324217486, 17632547210338453579, 5080361708878916008,
        13558759084650799507, 2421595825779520715, 7474172207584753057,
        5163264729849672854, 12350491381345414113, 9903918297005948690,
        6255565913863860433, 7442815280172368983, 15858502137304993443,
        15658150804610581967, 6552320915313180100, 17442561852129629341,
        12162652257482499351, 3980212925754409253, 12601674924802918477,
        10510655947281068492, 15827142554425099459, 14901164406314707724,
        4769898078730312955,
    ),
    "saturated_integers": (
        14879902173004397569, 503399789666721949, 10476823234844804248,
        14725702895512817707, 4587014834849774817, 9279855135876106751,
        6803146933366991059, 1532293904337974881, 9362555539303934505,
        16370094004056428629, 12693624624178350761, 16860559768109715714,
        8015318411210495840, 6149656975692699412, 11103150938359135680,
        14344583037527603303, 3490511329577715108, 15691292786574181688,
        7198919312352813142, 5870320715306567926, 1578933477760145330,
        12834078685172071723, 17830221585956419260, 3648325267357870799,
        16665645298385905117, 17322575995722424511, 15991085234721632358,
        7766376635727288410, 16506158817992780411, 14101117120472187812,
        15665249402409925566, 8400174299784145447, 7772493750593601408,
        12293083517151523044, 4844143670376836803, 4101920866307836832,
        10918581997357866759, 6838804601340763056, 8996440360190559353,
        10221778785837101644, 11932259800571609058, 11846314781776006506,
        7324927472604893835, 9862610037906826939, 16374467061013442683,
        15378872738563111551, 14372216327767465923, 11389554098232228365,
        9811363188700176784, 15109080552199181041, 14800070410420609622,
        4630607423294290951,
    ),
    "identifier_layout_packing": (
        2133445670946539098, 11981192592242442652, 10590080120497718362,
        2873831576859777791, 14691394533195391903, 6960121324938299066,
        6864737569749334100, 14869315022140156599, 16968290254832028037,
        5645913014257962301, 13066870849114815344, 9340397039500233319,
        10182114925467700576, 2097201764946789935, 9866926844510420059,
        4730807059393854279, 8758714791461785548, 4746865290939205165,
        5862885024567401376, 7086486961727365988, 16023757274257844766,
        5579323079509963844, 953824599976055511, 13253607986884489203,
        11581242300632279511, 2853535824041280845, 12998511296963757887,
        4193238102763151999, 14135930288177834819, 4116316145845327410,
        14567619838209041966, 14127649457793223153, 4735969490069522297,
        7367495102748624401, 13502886630143229924, 7311416373004073758,
        14189303352631987021, 3547133639880423604, 3737092542043582233,
        16315758591796193756, 16044769024858297099, 11520132607229236167,
        16245689211597603055, 14021403906309388758, 16843212092882274907,
        8423358473771967612, 86063611898626637, 12426668096033639842,
        4507278949400584981, 1135750359633044887, 8705752165939891696,
        13439801069961426753, 16688779884370038781, 5756434633376951189,
        13798635845593858936, 7202896243676816013, 1728208303232906376,
        15266522445212351309, 17113158684710626050, 6109070393417281268,
        664113016435541617, 18342136840665693534, 7836730298500805326,
        1728371594612039943, 6827507768706501140, 12297261894398137284,
        7670253390345383337, 7645774422493251043, 8958665183747190690,
        12814485477245598738, 16385352943234104771, 5699628160137858854,
        16135631896510165742, 16856857133637666360, 13115401875083798471,
        9874359980855131462, 15072624225022042877, 15768674062192538527,
        10598217203527022344, 7843501903378271152, 16318887542207898663,
        516211843469013799, 13938422710030144739, 9671003108732408407,
        6838044191481520333, 1629336804731282581, 6280493944316425496,
    ),
    "grouped_thousands": (
        10390682183339692644, 9709370117967825422, 1372135379889647302,
        797770577654099785, 2059790281346799348, 5809501225432164383,
        14853133582192799163, 4179684481535051309, 4625664472293759910,
        5990395913938564001, 13157394052974122422, 14286365859936689720,
        17146589981717906051, 16066197736220705519, 17303559612018801585,
        11495140397646416117, 4462410273845329648, 16232650578599091989,
        3329199271902338807, 14795963718401349756, 6204604198220237244,
        5321820312771371471, 10242919181991826863, 14966208708333309526,
        2060593695541399422, 852927086334939308, 4719829434531730015,
        6482149258410386223, 10432785415879352139, 4510105822620746293,
        1996075189852565409, 12410475006317560029, 7938441945924962221,
        1629741512823749819, 7370505432670325408, 14293540600515971891,
        7212269041450258622, 8408971025494151927, 13048797574411966705,
        17707692510942992751, 11779135534545971196, 7426863932049670845,
        614321125549422288, 15438947051010758225, 982307153398426982,
        3839575058364275966, 6345803081246716224, 14385672579639797466,
        11121322036425621047, 14819602634791337062, 13109639223323109304,
        3508217396645203032, 8820429240431121788, 8288121219677707094,
        5053074673881699973, 9825486303775514040, 9274500925110878753,
        9677241593423573480, 16400367825954858004, 7456068766970619122,
        8021429493413364028, 3142289566579720811, 8820810108656237450,
    ),
    "saturated_levels": (
        8789877641477584451, 14061771737494511513, 8492866395041342171,
        13064620638720277127, 3689484532654513670, 3766860248324257315,
        14441056460575882611, 13192628943897223606, 12739264937288114779,
        1882456247130088232, 16796672780467978087, 5809247065094172459,
        9571706159049136460, 7614245059267381523, 5433360213451458586,
        14085150011940750490, 16595808210465114085, 18042535707410537438,
        1771121451650387029, 6619488517674498275, 16402812875543374449,
        3061434956137513573, 5700837183761211429, 15090668173431700156,
        3963563055271773100, 7610192062330998712, 13958065400964255909,
        4342087006595381866, 3563334622968888497, 14712353890326176370,
        12746088402424799577, 17061171485078427565, 7392803631007743490,
        2713251227109512726,
    ),
    "saturated_tenths": (
        4984763646974463998, 716103067423287981, 15074666484794473745,
        14878593753724019072, 11105398073562172977, 6416581269359930381,
        1712818984024196130, 9080840327248245155, 1889021173754608625,
        7833099873658681513, 15550149982404660089, 14831192675479380791,
        716718993118661328, 2610152525058997562, 3993651508691504232,
        1452656520331701246, 694088508874988200, 17559094681620418242,
        18391224952021625716, 16872764544456532931, 828445734486120416,
        15276387572753110033, 17727615588666294074, 2724589288697796876,
        4430597342985768167, 13199553917031906621, 9257698873507771352,
        13922538599275867805, 1499485798835382966, 11564759450904159921,
        10718968918846684004, 2719701454904616416, 8032361673053953483,
        16678186435369128231, 18226735024736992849, 10671742016647448392,
        11076209537418418687, 17815594684644229472, 15927319255364401078,
        16585763707187574832, 10598665134041044592, 3635732530539702086,
        3715561364890015233, 7875301453500344443, 5656052095118657969,
        9201843469929726796, 17725008181634169157, 15997173712771747604,
        6481159937467421349, 5043800076391680734, 7338855808358865470,
        14937651906208576329,
    ),
    "separated_in_order": (
        13212319373645991198, 3124858977475633898, 13010056197012345531,
        4264904321941588231, 17383293044662711306, 12411720386434298775,
        8024866301577146682, 2749438196418611484, 6219451852441515048,
        17283582658421246541, 6222816430999155403, 17733799514538467927,
        8683638793174787581, 12957134877525461792, 17376073554016844179,
        339335848901217406, 143123105700361814, 8887644370560360123,
        13396192934278525122, 11377940140862159552, 11266547905149177465,
        8626284110326026960, 1610467004518196393, 7255042512922810081,
        4431569082447787604, 12692686399018873006, 11909838672017454383,
        12090785649312243742, 7230969391896325039, 1757209359893068939,
        15380960111715861860, 16721858549975570198, 2014827285520046748,
        4917272234921210154, 13591257825598483686, 2024586551144361539,
        9076499461175541656, 6101882392942214126, 2232447955143357544,
        14237503022909562119, 10753502952628846387, 7252923574144308443,
        10924290978578477268, 9393162400314167372, 17226066490847573428,
        6427255367641620637, 15109245959838334317, 3523195627623299933,
        2245074948595071685, 7848834666989494380, 17945467848151263025,
        6079415186056573731,
    ),
    "signed_pads": (
        13212319373645991198, 3124858977475633898, 13010056197012345531,
        4264904321941588231, 17383293044662711306, 12411720386434298775,
        8024866301577146682, 2749438196418611484, 6219451852441515048,
        17283582658421246541, 6222816430999155403, 17733799514538467927,
        8683638793174787581, 12957134877525461792, 17376073554016844179,
        339335848901217406, 143123105700361814, 8887644370560360123,
        13396192934278525122, 11377940140862159552, 11266547905149177465,
        8626284110326026960, 1610467004518196393, 7255042512922810081,
        4431569082447787604, 12692686399018873006, 11909838672017454383,
        12090785649312243742, 7230969391896325039, 1757209359893068939,
        15380960111715861860, 16721858549975570198, 2014827285520046748,
        4917272234921210154, 13591257825598483686, 2024586551144361539,
        9076499461175541656, 6101882392942214126, 2232447955143357544,
        14237503022909562119, 10753502952628846387, 7252923574144308443,
        10924290978578477268, 9393162400314167372, 17226066490847573428,
        6427255367641620637, 15109245959838334317, 3523195627623299933,
        2245074948595071685, 7848834666989494380,
    ),
    "spread_conventions": (
        8534970996080522473, 10651013169768465969, 14220378708344514053,
        17388286930902395248, 15839605715532107887, 2181967384112697610,
        2081241836159808957, 18152595152790328074, 18400558490050716633,
        17665438258481253967, 11655804304781717907, 18427173534392809611,
        12627368640545344342, 10010273130661333008, 14743586705166533874,
        15965174774999632031, 9430749340472921501, 2957304431918809990,
        12791799876815227451, 18319110582472954230, 2366364817818337052,
        11273422484744424991, 12425776669340539470, 3479944894903800314,
        14551308883365979779, 9343463772395556516, 825903289611820609,
        14583976519615148561, 3903986395746195009, 1579304517159551676,
        8278147222135142430, 628696166431624940, 6502607461124114879,
        16527195317326587663, 9849141810659476556, 7376985502948974837,
        11208155520699624620, 5758566266419332141, 696075165213873737,
        15176580905599048150, 3016086853034679107,
    ),
    "unpublished_majority_marks": (
        1347355342221236955, 6558018661785960475, 6761212542403308974,
        2970702021573651188, 3215071037161132660, 17800126851394464143,
        9859298425996435787, 584811875340559264, 1887488034494385385,
        1293091210345907109, 2818233852915444725, 15946189749909443455,
        2629213739374526, 15788398730289372229, 12154568446441856461,
        14036540276504434596, 8179006762177092765, 17613636635921120393,
        6232925410137821842, 8522117911449044090, 12607871449741400097,
    ),
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
    # Thirty-nine words, which is a forty-row label column's placement
    # budget and its whole budget: the role consumes no content word,
    # so every cell of the twin is fixed by published counts and these
    # decide only the ORDER the rows come out in.
    # THIRTY-TWO WORDS, and there were forty-two before landing L7.
    # The budget of G4.3 is the sum over positions of what each
    # draws, and a position draws by its own STRATUM count -- which
    # G5.2's grain rule takes from the position's own
    # `n_distinct_values`, nine and five here, where it took the
    # whole cell's twelve. The SPELLING budgets moved with it for
    # one revision and review round 1 put them back; they are not
    # read by the draw budget at all, so this count did not move
    # again. These are the first thirty-two of the same stream.
    "joined_readings": (
        15748752049046439706, 1052754991355682497, 4631623576966815744,
        12064659840558517754, 10657191057255707380, 10378248564851026865,
        10021198239630938960, 6883748916460414070, 18067353361653053739,
        11892363277122465327, 602886262687784400, 8704353156322424958,
        6379347427865422855, 3598830946331392386, 10329267094791843675,
        6649749446851944564, 9555332664539838988, 1525621960858135254,
        2224251045539429228, 16128073529113414212, 2556883604043696129,
        3134567652162207724, 7622991860140729128, 4021366232906136322,
        16488111908451590613, 11196021744312784249, 11554654619999588298,
        7340016323151300764, 14290091057079116538, 6838773607184501349,
        2127311776424462157, 16897824151333146762,
    ),
    "affixed_brackets": (
        17639521920205238616, 13505086616814382279, 15108206413291935612,
        2648109655521823620, 13957488783681493234, 440424866904614487,
        10392828958468768899, 307661453259722614, 10328600741271277179,
        18028049770950982553, 2493915044553599588, 16250571819090705811,
        3648116078256326511, 12380433607203903270, 11280011279662351746,
        6666421730586177324, 2346116348095104722, 3316129054665061780,
        4395871943553304390, 17732992366768506823, 9781242035145962743,
    ),
    "clock_ladder": (
        17168193686452184398, 17294964732501811759, 5119971829015185418,
        3974762115987730418, 9783861565524925563, 676574683570638621,
        12408121771224495461, 17120944728125855256, 8074603130316608142,
        16171205420250064347, 1348050307520104417, 14805382045011159389,
        12528853194802204718, 7870325075990001275, 8800084849072185159,
        11241460431909986162, 9287835057163713957, 11122896599893611155,
        15231939135091175662, 12051230916723616950,
    ),
    "label_numbers": (
        14485363227759379260, 14496546446215838655, 17877404087858154871,
        13799267182700036431, 12092778006306275581, 17319362901013630541,
        3294855028839219168, 10858624428905468031, 8168203010090694442,
        6435093561335128686, 6104571710385768880, 2939833306085970469,
        18252379738369854919, 4742856688619991640, 13203531316936026217,
        9331933324833785766, 12250691627341533157, 12955931837302369919,
        960710691341638366, 1108584512337328690, 17438679814386998998,
        4618150261496032979, 7485577089883912648, 5090626598207926334,
        5546068173886288405, 6763907908498900843, 2744688177708167075,
        6425753487679248711, 11015110302746343300, 18339080949187871663,
        3417281073695313348, 18320094770021572713, 14492109870859816788,
        8266784616822606329, 15687942191941692266, 15880471324755436178,
        17841136179427949105, 3153720365097832194, 12904746883321067555,
        15289589415482460436, 11790829620896665457, 16118600836855221284,
        14339110349838762356,
    ),
    "label_number_tiers": (
        15712004738899576826, 9106234749995103221, 7197214430348145549,
        3313175008234788654, 1858441125794321210, 14392887498122039256,
        14505558076215610779, 16068856989174244207, 5942574399079652759,
        2192282604479703364, 11260024226675101652, 13534188194726011293,
        4063389463222510494, 14541140093590011962, 5139732853110514003,
        1004173694524156974, 4999747325177310008, 36812468473126634,
        12195136472623052346, 14062518629859044726, 4687709092736208221,
        1597459712860693187, 470876766907946440, 8236041365792050124,
        7730361621478316229, 543650611795532731, 14596876895218142794,
        8631733672137465319, 15781029449199713140, 10833549348437045843,
        16670281662855218962, 14691742750537098749, 12958625416149823508,
        11816259790482739471, 14752909853014227733, 9116783273885634726,
        13344587108756686254, 4833903204111742558, 18063145974116289591,
        14736869239197373521, 5874016634768137613, 17202436296877165178,
        3518497538150768636, 7884522024368171274, 5784798466896332461,
        1786132738446827029, 12470419375819469909, 1224946779267958078,
        14893380431211633658, 11306254306392298651, 12068320809430943003,
        347872208542651383, 18007349395004237999, 17724797172735929015,
    ),
    "long_tail_levels": (
        16141117999568644869, 2912390137437105406, 11142961259136265613,
        6649429050765924510, 9469698730514687439, 5579144964475137875,
        12872973492368199229, 7223177790597929199, 3344454729737302937,
        10285472521140763709, 15899452662498998082, 5815724960036124325,
        41521252156152542, 16244079925127836306, 16602194588370141660,
        15590272638216937006, 12261121709717609306, 5959776043330656727,
        8749314566909052889, 1838166636128818935, 16830835450031427436,
        2394200286403428241, 13014561226645067534, 13850225979970345509,
        1491081199983217612, 7888999454250188185, 754576511652955794,
        13319788797896474011, 1161974799008428245, 14280985510514793536,
        7512075171393035397, 472393997099740481, 13756099177883521641,
        629654845121351311, 3416056298896993148, 17989065697282896171,
        15281512689324940288, 17576893266494880556, 5388882302899227045,
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
    # Twenty-three words, which is a twenty-four-row identifier column's
    # placement budget and its whole budget: the role consumes no content word, so
    # every cell is fixed by the published facts and these decide only
    # the ORDER the rows come out in.
    "identifier_layout": (
        2350890344146344126, 1295412325827091444, 2148692853705598588,
        6856365061159066252, 15421135529079413842, 9337190313697136114,
        17443182240601902554, 3945372972456016603, 3231109804060922937,
        14928184306589085733, 9623648095902836919, 2833255648229499529,
        2484211853885415346, 9206020379377428048, 10880630985268877757,
        11539897411331388552, 13221390389229023683, 5089869681841105310,
        12063417803171021458, 3253571153139736265, 17680378324194345923,
        17516376728897238031, 2135463789325316001,
    ),
    # Forty-six words: a forty-seven-row identifier column's placement
    # budget and its whole budget, as `identifier_layout`'s are.
    "identifier_layout_mixes": (
        12315416199638712830, 11461917734807452332, 13043389866221201829,
        4117057510935812347, 11166822964374134715, 10306677672402459178,
        8646002244923713862, 4041989434868756395, 3102189724845197795,
        18075701478311684605, 1857492319440419448, 13086464872739884056,
        581282553384915289, 7586242669707928484, 10323704345614453502,
        2255447556845704593, 1703153506126005306, 2692500561440188756,
        3055453076326589704, 97091045728570219, 14343194256563202997,
        9217557811682092942, 15888849271152112244, 2757548850731508731,
        14119304420836053316, 6472162727552187798, 5861169136430044779,
        13671056489289250396, 13691116676054877367, 5333278273152096980,
        4851488638743472859, 17583254726709643303, 18085613694544194866,
        16045974538112549444, 12577078091213710482, 11805424536042655935,
        10109715328958355953, 1696310926535484208, 7655097596069497137,
        17270314890295469748, 7499453768873882173, 4012621328774350190,
        10699857760492589064, 6430887874155946278, 17302433675516304856,
        15120724432689965450,
    ),
    # Fifty words and seventy: each label column's placement budget
    # and its whole budget, since the role consumes no content word.
    "lower_case_stand_ins": (
        15830664673893228848, 5073698456080673279, 7875838601216900988,
        11535154252214777058, 8621941330772045083, 8772339449381309270,
        10488852849884475397, 6371871893467202343, 1246799487542206975,
        9064597751508696776, 15332551243623560934, 14774754731362542570,
        14534231870623192905, 9408872517084544776, 3320777161477635281,
        8654342408759465470, 12447963985929670088, 5106417360233856539,
        18427915347586493865, 10570067524607262016, 14439736570525528903,
        16546367209938517481, 8477631004882138497, 10913147923967033456,
        4194028020326342935, 14495905327524417777, 583302282863258999,
        139154040289801448, 18046683419125720843, 1296118245588486310,
        2636961127756418768, 9001931390103612218, 7741167511558814911,
        18041580935583591676, 13694740739387581868, 553546565315490563,
        22513546439589079, 16709646298868681502, 1447791936714280564,
        5098489623189836073, 4374303835978440748, 9815100461200391397,
        15679049804236764501, 18155049002991901528, 8469325124826455278,
        946244536432157447, 7040022859543152818, 15636706020943181500,
        10620482021486410816, 741266932377646521,
    ),
    "level_shape_stand_ins": (
        10572201364969750517, 14488452992183049686, 10338980211685271540,
        17310746628490101705, 15930516927233095031, 10925981946687229523,
        11984375984483652018, 3115820831674141766, 1491667508731758021,
        12095184894851438023, 6616027349516039298, 4869191475851910318,
        3667299028267463384, 6287211967338772842, 10303464976186970092,
        3778724444670585346, 5518558728777231354, 15069916103189709611,
        13902520522701011481, 14960497023170678489, 7361620293930603418,
        17783812003195909956, 902419012765408100, 9861278426630039680,
        550339003356881841, 17324367625225383559, 16634594057315558326,
        17745590132511631737, 4661080672871936834, 3041321162227143340,
        5680036735926225649, 3863807788710707093, 9729211348814354707,
        15791412086449201245, 3530221954823534184, 4612587005460363641,
        7044370326001245642, 10055541422525994635, 14970981537008481323,
        7666065712349092006, 6886019483394326737, 14772245721026608204,
        15083889930239009629, 16666244600805875045, 11435779303634445760,
        11864111828352662593, 10236277314942045383, 2765469866442712258,
        15636219563350824567, 8863328807930096672, 12914777269208835441,
        3595536836711968274, 1433759923759427814, 13624577672746584616,
        4873316314549421849, 7932092449336148476, 7739797739499316257,
        123464669902506341, 11181717779831646623, 9263968744977333854,
        14344049750293701763, 16366278832934763060, 12179873843408294288,
        2444068681713350805, 12848255613891529191, 12641691033048600769,
        14952483995130744131, 8283423452509650775, 12601060826970560254,
        8872082779446286874,
    ),
    # Two content words and forty-three placement words: the G4.3 budget
    # a forty-four-cell count column is given whether or not its census
    # of spellings leaves the words anything to decide.
    "count_spellings": (
        7687911214574418412, 10663533608816953314, 2616547998438772155,
        1366869589866334087, 17520374349558038042, 1609274745335312500,
        14208627795420856630, 4243662745333721072, 16049732717786980771,
        13998553070692769882, 1474326905162042579, 2312802121902820003,
        2469587400300821282, 18252884443183030911, 3161585658302330964,
        5124052084043109061, 12069967067160595751, 18101372447488982082,
        1747047840045718174, 8772433440031119127, 503463901603744489,
        14446097835952004249, 5275666164281917924, 17786018302256602457,
        9531465300822991939, 16454979768288460259, 14153358980504684320,
        544672169205711433, 17575418052128749653, 1651629124224001023,
        12674954058559114794, 6112529208509423379, 12384984089675196170,
        236106178430280789, 16664337307126418403, 600496068526828757,
        17536768382670458704, 2828983999751666805, 4820344975137709250,
        15646717198495412648, 15130515098698616441, 4009465223591371070,
        5131576334512893944, 4352129982649265412, 11759005967142306325,
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
    "unrepresentable_exponent": (
        11673391271091347200, 5495330693160871804, 15204918087645570054,
        10712428183187122067, 10949282274109216441,
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
    "midnight_days": (
        15225067758405650424, 3239691001737042761, 6965203772582325307,
        3861130776911679617, 15173224978910387615, 9323792062223508955,
        14250404113572641605, 1387121928156927234, 16727263926372204009,
        17058543561537392661, 590429885636454433, 11726181845119428326,
        11691978854857713329, 2605788068526521694, 15564275702978365942,
        9295767331320370689, 4588766561642468171, 10672129521899455171,
        1873019329306020848, 1526646873211970272, 11345087966265059162,
    ),
    "mixed_marks": (
        12587170189557361101, 992822559630912803, 4064922177151560342,
        3401059606364785669, 3244891138370822358, 14980499527944476233,
        17032708870344961936, 5101897133503557865, 15121802600962083084,
        16415622762886201840, 9462634704993459244, 4518799303034446728,
        15204573778114825406, 3943230677818135853, 13677652951661521469,
        11620345735806077694, 17107644350114347775, 4277951003820173595,
        14741256730524897565, 9558457822766297307, 4271447349828353003,
        3060388504118456040, 9182585704594671237, 10749372310875182232,
        3400435677155855496, 274762717475212626, 8690874097962755731,
        13433718298383103069, 16945188177730290244, 11539065713204468302,
        16917925380007743293, 15950719764958515555, 4024025754346188944,
        15977231050047964636, 13479993951608207110, 5125709897111330840,
        14702858441175478488, 15960523503845024435, 5523654226794324199,
        9722210440181412196, 1318698826428569177, 10758849686013811633,
        4388598467465224327, 14111088605365728606, 3202938355627100572,
    ),
    "pooled_marks": (
        14485363227759379260, 14496546446215838655, 17877404087858154871,
        13799267182700036431, 12092778006306275581, 17319362901013630541,
        3294855028839219168, 10858624428905468031, 8168203010090694442,
        6435093561335128686, 6104571710385768880, 2939833306085970469,
        18252379738369854919, 4742856688619991640, 13203531316936026217,
        9331933324833785766, 12250691627341533157, 12955931837302369919,
        960710691341638366, 1108584512337328690, 17438679814386998998,
        4618150261496032979, 7485577089883912648, 5090626598207926334,
        5546068173886288405, 6763907908498900843, 2744688177708167075,
        6425753487679248711, 11015110302746343300, 18339080949187871663,
        3417281073695313348, 18320094770021572713, 14492109870859816788,
        8266784616822606329, 15687942191941692266, 15880471324755436178,
        17841136179427949105, 3153720365097832194, 12904746883321067555,
        15289589415482460436, 11790829620896665457, 16118600836855221284,
        14339110349838762356, 3346176665544244880, 11953169525016169803,
    ),
    "slashed_pool": (
        15712004738899576826, 9106234749995103221, 7197214430348145549,
        3313175008234788654, 1858441125794321210, 14392887498122039256,
        14505558076215610779, 16068856989174244207, 5942574399079652759,
        2192282604479703364, 11260024226675101652, 13534188194726011293,
        4063389463222510494, 14541140093590011962, 5139732853110514003,
        1004173694524156974, 4999747325177310008,
    ),
    "midnight_mixed_forms": (
        113928492773646949, 17372370786837566977, 1219843214052797780,
        18060177847918427891, 2269749036259349544, 1894645877340042640,
        15072375343841275966, 17346076489125329089, 9786844728708983233,
        2313887177159651904, 14383211509980887204, 1891469827612902315,
        1918039791416009201, 8866012333022508572, 3304104628595658101,
        5361620680766448462, 2128419656908236178, 13372904720345244078,
        8759118553313331063, 13069717736981496796, 6138377388608102850,
        17738937843285025801, 16667688310731956123, 17093977340954483409,
        5384618276592245486, 8995304594082110260, 8135910953244645417,
        16621120088989500265, 14548498363494084155, 4169421069517691136,
        14648778205617844717, 6737328632369445978, 375313268482488846,
        12411956739066342091, 18299847717392466046, 14808335859639834358,
        11864420252033652509, 5003249159363248133, 10869925071936347938,
        3426327052426443793, 14627413773893209962, 6434163649656049356,
        3201641117064018439, 8953199931265607348, 3374173106152786677,
    ),
    "partial_midnight": (
        1152304788140580860, 3867042428245129712, 5521709652331476041,
        16787588637765382555, 5839333488759457276, 10801019328581594845,
        17705012502391288466, 15020103291960895461, 4943810138468162983,
        877893562404209578, 16922643984788468846, 3306002626557328184,
        17502856997231273229, 7897228658841342621, 14826654116142264846,
        5793616776277113670, 10796600254155222444, 7765144065563217641,
        6715930928981767690, 16153726339302755246, 1646178210335255695,
        11111103851345892514, 15010111191794066299, 2975547439463384818,
        17642205489684340623, 13212108929575244868, 14895492880472523042,
        4192985432969924647, 9820426250463759087, 10234548067267463062,
        5189587264895563080, 2452702763937307337, 10205308364826528282,
        14316190813908941328, 15202294529749275567, 4195364331076296629,
        12775844997860775945, 8647740450583316597, 17918419582921289744,
        8290940002445848808, 16147188500045453846, 10018618111265336882,
        10632733031110977480, 3763983169410323083, 15701824487642497391,
    ),
    "midnight_two_offsets": (
        12159711863008289878, 8709007662888919493, 7997898239127022494,
        7451265919803795170, 1470248478108607712, 10818965659882411781,
        16981746518262132939, 15548278071263449747, 9419688407408251252,
        7614032419161006808, 16046008259160574575, 6387722803170484949,
        15119183407783803397, 12885227414193446729, 1987203789594237335,
        4632279376113977152, 18045010286009548665, 862031965623451883,
        5744765592436122078, 446953054251727269, 18317086482641423628,
        17822566509887301813, 9910238047150026831, 18244926176802880538,
        5416248856541669996, 1095152913536448474, 10708723326105226653,
        4509920326808090827, 6941920607344609533, 7092262075666499652,
        17071520747136474617, 14106376023458908189, 261922282994547843,
        16270548520809097675, 16511931872268775318, 3503721415149997583,
        7182340396267010647, 10134588438343447637, 3433681718526137788,
        2159141692022912887, 11722352740023183471, 2331279634929741441,
        17681242563859316791, 10856412895652481, 12549459677246770462,
    ),
    "midnight_bare_offsets": (
        7089385755461974538, 4314764982914698682, 16567534149198797734,
        16464795469777924000, 14318121936348965621, 14620420000527275332,
        16782936558013819173, 6593487092538202917, 16926022121086143958,
        5291891043476227775, 3580209385984035972, 17785491288986074348,
        856540425896113702, 11674233117865919641, 17240571081310899840,
        13807000861013954160, 14524779962867225389, 6486544850949051387,
        3673561687381706519, 12801222241337981710, 6856693191474359356,
        10595972535340100382, 16923529454583407121, 5876904505267725559,
        15121633124576497790, 14328305676225814364, 960200242413647887,
        17892645618493081823, 8763750044574266882, 3135842330771061634,
        7376019224115783948, 6743593554889592790, 4587082567632806684,
        928840032145345843, 8611965826350869657, 15952738046520582940,
        15170548298862574888, 18078340560188216414, 17961755548169570166,
        1709256287998433444, 2601830613986780518, 16802502615291089435,
        5371919591216636188, 10726450709361837683, 10163254344864448410,
    ),
    "grouped_charges": (
        14485363227759379260, 14496546446215838655, 17877404087858154871,
        13799267182700036431, 12092778006306275581, 17319362901013630541,
        3294855028839219168, 10858624428905468031, 8168203010090694442,
        6435093561335128686, 6104571710385768880, 2939833306085970469,
        18252379738369854919, 4742856688619991640, 13203531316936026217,
        9331933324833785766, 12250691627341533157, 12955931837302369919,
        960710691341638366, 1108584512337328690, 17438679814386998998,
        4618150261496032979, 7485577089883912648, 5090626598207926334,
        5546068173886288405, 6763907908498900843, 2744688177708167075,
        6425753487679248711, 11015110302746343300, 18339080949187871663,
        3417281073695313348, 18320094770021572713, 14492109870859816788,
        8266784616822606329, 15687942191941692266, 15880471324755436178,
        17841136179427949105, 3153720365097832194, 12904746883321067555,
        15289589415482460436, 11790829620896665457, 16118600836855221284,
        14339110349838762356, 3346176665544244880, 11953169525016169803,
        3963784740836385802, 3229704822604864282,
    ),
    "grouped_decimal_comma": (
        15712004738899576826, 9106234749995103221, 7197214430348145549,
        3313175008234788654, 1858441125794321210, 14392887498122039256,
        14505558076215610779, 16068856989174244207, 5942574399079652759,
        2192282604479703364, 11260024226675101652, 13534188194726011293,
        4063389463222510494, 14541140093590011962, 5139732853110514003,
        1004173694524156974, 4999747325177310008, 36812468473126634,
        12195136472623052346, 14062518629859044726, 4687709092736208221,
        1597459712860693187, 470876766907946440,
    ),
    "spaced_brackets": (
        113928492773646949, 17372370786837566977, 1219843214052797780,
        18060177847918427891, 2269749036259349544, 1894645877340042640,
        15072375343841275966, 17346076489125329089, 9786844728708983233,
        2313887177159651904, 14383211509980887204, 1891469827612902315,
        1918039791416009201, 8866012333022508572, 3304104628595658101,
        5361620680766448462, 2128419656908236178, 13372904720345244078,
        8759118553313331063, 13069717736981496796, 6138377388608102850,
    ),
    # The mixed-convention case of landing 2b.7 (plan P4-D65.2). Its
    # budget is `spaced_brackets`' own -- twenty-two rows of one value,
    # so no content word is drawn and twenty-one place the rows -- and
    # these are words of its own rather than that case's, so neither
    # case's cells can move by borrowing the other's draw.
    "mixed_conventions": (
        2350890344146344126, 1295412325827091444, 2148692853705598588,
        6856365061159066252, 15421135529079413842, 9337190313697136114,
        17443182240601902554, 3945372972456016603, 3231109804060922937,
        14928184306589085733, 9623648095902836919, 2833255648229499529,
        2484211853885415346, 9206020379377428048, 10880630985268877757,
        11539897411331388552, 13221390389229023683, 5089869681841105310,
        12063417803171021458, 3253571153139736265, 17680378324194345923,
    ),
    "apostrophe_minus_sign": (
        11925147295444600069, 11089240203900317313, 9819830666471227869,
        2749346133703871953, 1508733343006715641, 18180139909873991228,
        16463840791222180813, 10654012495794051676, 11710431502531830591,
        16252906971658573958,
    ),
    "quoted_trailing_minus": (
        2630530136600429752, 14843464820283064329, 13746219337496006556,
        16276882424652558323, 15421845663344080015, 11250483033371735923,
        9927756422451768005, 17351084460761096619, 17896605624886333308,
        5365177923225636576,
    ),
    "spaced_decimal_comma": (
        17988365877429453726, 9448520390256751155, 6656490661682814805,
        10629575347112315327, 11033422561547849900, 4389274299741060645,
        15177587718132664213, 16104903271661744053, 10595740474962929323,
        11197535970092085343, 13866510609922126994, 12730807114626703150,
    ),
    "narrow_spaced": (
        17865164054464875118, 9302008414438268749, 10038449414269515851,
        14390649795119895464, 5582022101676062047, 14699329782199672301,
        13849334626973602526, 12166305398364482328, 3728389681362057086,
        6349893863503400983,
    ),
    "thin_spaced": (
        10113102895414097955, 5178904941191796344, 16615958821304445730,
        18209141115321277810, 4121229174028038910, 3400813849530246077,
        16764169360987406787, 9284587010259531064, 16054953443299658383,
        10855639821522867941,
    ),
    # Nineteen, eleven and thirty-two words: each identifier column's
    # placement budget and its whole budget, as `identifier_layout`'s are.
    "identifier_absent_words": (
        13582273234154262364, 18398104693322419879, 34070170978230141,
        3341762675134395213, 9954870715852195741, 11074722499558924578,
        7086877514108549857, 5428095448531052280, 9858665311344715186,
        14335373683300192717, 13568817218928113682, 7443554488824773121,
        1507543091965614910, 15036176574875485406, 11305006835104430484,
        3919574237267079812, 4662566541854203892, 2785393505384254902,
        18167102002877775314,
    ),
    "identifier_signed_layout": (
        411179136531786142, 1982861595377018348, 11950373906050309963,
        17721752918347183196, 14209512559177407037, 16754303442300708120,
        4204783424237075846, 4681831488814884530, 6446403972659101316,
        8427775216937654035, 10211324520233377560,
    ),
    "identifier_layout_partners": (
        7624411207500017663, 18018633891298768539, 9327666861298971719,
        12069654061041524425, 13056208526174774753, 16270608102264184673,
        7136254884387832689, 2146649404055757979, 8299392471497780641,
        2314006865244965464, 6452669892852346852, 14498537279786915597,
        5807170461159552380, 13761051749839567673, 13496788994203422708,
        17658594639995542130, 11946899400267459287, 8643193479102873906,
        7601562399756904492, 5111893150072507382, 10575175848735182819,
        8657697069614245099, 13726072828175306438, 5859875945738675844,
        808640240039876655, 9923500839825069631, 17981466901741366856,
        7759697397388857000, 9890344465002701988, 16504403711328310884,
        5583668501587289150, 12607117446844355094,
    ),
}


def word_budget(column, rows):
    """The draw budget of method section G4.3, as a function of the facts."""
    role = column["role"]
    placement = max(rows - 1, 0)
    if role == "datetime":
        parsed = column["n_present"] - column["n_unparsed"]
        return max(parsed - 2, 0), placement
    # The clock role budgets by the same shape and for the same reason
    # (G4.3, G7A.4): both ends are pinned by fixed rule and cost no
    # word, every stand-in is stepped past its neighbours and costs
    # none, and each rank between the ends takes exactly one.
    if role == "time_of_day":
        parsed = column["n_present"] - column["n_unparsed"]
        return max(parsed - 2, 0), placement
    if role == "joined_numbers":
        # G4.3: each position's numeric budget, plus a reserve of
        # `max(n_joined - 1, 0)` for every position after the first.
        total = 0
        for place in range(column["n_parts"]):
            total = total + joined_part_budget(column, place)
            if place:
                total = total + max(column["n_joined"] - 1, 0)
        return total, placement
    if role == "affixed_number":
        # G4.3: the numeric budget read over the CORES.  The pair is
        # fixed text and costs no word.
        return word_budget(
            {**affixed_core_view(column), "role": "continuous"}, rows
        )
    if role in ("count", "continuous"):
        numeric = column["n_numeric"]
        negatives = column["n_negative"] - column["n_negative_unrepresentable"]
        zeros = column["n_zero"]
        positives = numeric - negatives - zeros
        # G5.2's grain rule: a grain inside a role divides by its own
        # count of different NUMBERS.  The SPELLING budgets are not
        # read here at all, and they are what keeps the block's counts.
        divided = column.get("_grain_values")
        values = min(
            numeric,
            numbers_class_budget(column, column["n_distinct_folded"])
            if divided is None else divided,
        )
        # G5.2's carrier step moves cells between strata of one band and
        # changes neither how many strata there are nor which band each
        # is in, so the budget does not read it.  Neither does it read
        # the ladder: G5.2a decides the SIZES of the strata and G5.2b
        # only how `M_rest` splits between two bands that each keep at
        # least one, so the number of strata and the band of each are
        # what they were, and those are the whole of what this reads.
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
    "n_distinct_values",
    "n_left_out_of_statistics", "n_rows", "suppressed_levels",
    "suppressed_rows", "level_ceiling", "subsecond_digits", "n_unparsed",
    # How many parsed cells stood at midnight (landing 2b.3).
    "n_at_midnight",
    "min_length", "max_length", "n_all_digits", "n_code_alphabet", "count",
    "n_occurrences", "n_whole", "n_fraction", "n_whole_unknown",
    "n_positive", "n_sign_unknown",
    # How many cells held the commonest number (contract Q18). The
    # mode's VALUE beside it is a published binary64 and is proved as
    # one, or `null` where the pair is withheld.
    "mode_count",
    # The affixed role's own five counts (contract 6.12, method G6A.1):
    # how many cells wore the pair, and the four class counts read over
    # the CORES rather than over the cells.
    "n_affixed", "n_core_numeric", "n_core_not_numeric",
    # ...and how many DIFFERENT cores the cells carry (plan P4-D36).
    "n_core_distinct", "n_core_distinct_folded",
    "n_core_out_of_range", "n_core_contradictory",
    # The joined role's own whole numbers (contract 6.13, method
    # G6B.1): how many positions, and how many cells split that way.
    # `part_above` and `part_min_widths` are ARRAYS and are named only
    # in INTEGER_COLUMN_ARRAYS -- naming `part_above` here as well let
    # a scalar stand where an array belongs and the proof layer
    # certified it. `part_agreements` is a binary64 and is proved as
    # one.
    "n_parts", "n_joined",
    # How many rows of ONE published level wrote it in that level's own
    # written form (contract 7.4.8, plan amendment A-P4-47). It stands
    # inside a level entry beside `count`, which is named above for the
    # same reason.
    "shape_form_cells",
})
INTEGER_COLUMN_MAPS = frozenset({
    "missing_by_class", "missing_by_source", "numeric_styles", "utc_offsets",
    "datetime_separators",
    "variants", "variants_withheld", "n_distinct_by_occurrences",
    "fraction_widths", "pad_widths", "field_widths", "resolution_mix",
    # The census of signed decimals (landing 2b.2), a map of counts.
    "decimal_plus",
    # ...and the two censuses of a MIXED convention (landing 2b.7),
    # which are maps of counts for the same reason: how many of the
    # column's negative cells wore each notation, and how many of its
    # grouped cells wore each mark.
    "negative_notations", "thousands_marks",
    "shape_forms",
    # The census of LAYOUTS on a declared identifier (contract 7.12,
    # landing 2b.18), a map of counts like the form census beside it.
    "layout_forms",
    # The census of SPELLINGS on a count column (contract 7.13, landing
    # 2b.18 part 2), a map of counts keyed by the spellings themselves.
    "number_spellings",
    # The four censuses of how a column's dates were WRITTEN (landing
    # 2b.6, contract C6-25d to C6-25g), maps of counts keyed by a form's
    # word. No case published a non-empty one until the review of 158c811
    # froze four (plans P4-D130, P4-D132, P4-D133).
    "date_field_widths", "month_name_styles", "quarter_marker_case",
    "zulu_case",
})
# The whole-number keys a NUMERIC PART of a joined column may carry
# (contract 6.7 read at that depth).  It is deliberately narrower than
# INTEGER_COLUMN_KEYS: a part is a block of numbers, so the universal
# census keys, the label keys and the joined block's own keys have no
# place inside one.
NUMERIC_PART_KEYS = frozenset({
    "n_rows", "n_zero", "n_negative", "n_negative_unrepresentable",
    "n_used_in_statistics", "n_left_out_of_statistics",
    "n_distinct_values", "mode_count",
})
INTEGER_COLUMN_ARRAYS = frozenset({
    "part_min_widths", "part_above",
    # The bins holding no value (contract 7.11, plan P4-D32).  Bin
    # NUMBERS, ascending: whole numbers, never a measurement, so they
    # are certified as whole numbers exactly as the two arrays above
    # are.
    "empty_bins",
})
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
        # THE TRUTH VALUES A CASE'S WORKBOOK CENSUS COUNTS (plan P4-D198),
        # which that case carries beside its column.
        if len(path) == 3 and path[0] == "cases" and path[2] == "workbook_truths":
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
            # ONE POSITION OF A JOINED COLUMN is a numeric block of its
            # own (method G6B.1), so its whole numbers are the same
            # whole numbers a column carries, one level deeper.
            # ONE POSITION OF A JOINED COLUMN is a numeric block of its
            # own (method G6B.1), so its whole numbers are the column's
            # whole numbers one level deeper -- and ONLY those. The
            # lengths are exact rather than `>=`: a review found that a
            # loose rule certified `parts[0]["n_rows"]` replaced by a
            # mapping, and a key belonging to the joined block itself
            # written inside a part.
            if (
                len(inside) == 3
                and inside[0] == "parts"
                and inside[2] in NUMERIC_PART_KEYS
            ):
                allowed.add(path)
                continue
            if (
                len(inside) == 4
                and inside[0] == "parts"
                and inside[2] in INTEGER_COLUMN_MAPS
            ):
                allowed.add(path)
                continue
        # A DOCUMENT CASE publishes counts and places of a description's
        # own dialect or workbook block, and counts of records in a
        # reading.  They are named the same way every other count here is
        # named -- by leaf key -- so a field added to one of those blocks
        # cannot arrive as a number nobody accounted for either.
        if (
            len(path) >= 3
            and path[0] == "cases"
            and path[1] in DOCUMENT_CASE_BUILDERS
        ):
            leaf = path[len(path) - 1]
            if isinstance(leaf, str) and leaf in DOCUMENT_NUMBER_KEYS:
                allowed.add(path)
                continue
            holder = path[len(path) - 2] if len(path) >= 4 else None
            if isinstance(holder, str) and holder in DOCUMENT_NUMBER_MAPS:
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
    # A WORKBOOK COLUMN'S CENSUS OF TRUTH VALUES (plan P4-D198), which a
    # case carries beside its column because it is a workbook fact.
    working["_truths"] = spec.get("workbook_truths", 0)
    chain = []
    if column["role"] == "datetime":
        content = _datetime_content(working)
    elif column["role"] == "time_of_day":
        content = _clock_content(working)
    elif column["role"] == "affixed_number":
        content = _affixed_content(working)
    elif column["role"] == "joined_numbers":
        content = _joined_content(working)
    elif column["role"] in ("count", "continuous"):
        content, chain, _missed = _numeric_content(working)
        # A column DECLARED to write its decimals with a comma has its
        # numbers' points and commas exchanged, and nothing else of it
        # (P4-D26, landing 2b.2's frozen case of it).
        if spec.get("decimal_comma_declared"):
            content = decimal_comma_spelled(content)
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
    # HOW MANY DIFFERENT NUMBERS the finished content holds (contract
    # Q17, plan P4-D4.9).  Counted off the cells this oracle built,
    # because it is a fact ABOUT those cells and a hand-written figure
    # would be a second answer: `01E+16` and `1e+16` are two spellings
    # of one number, and a case whose cells hold both publishes one
    # number for the two.  Computed only where the role carries the
    # key, which is the three that carry a ladder.
    # A CASE MAY PUBLISH ITS OWN, and where it does that figure stands.
    # The placeholder is 0, which no conforming block can carry: Q17
    # requires at least one different number wherever the statistics
    # used a value, and every column reaching here used one. So a
    # non-zero figure is one the case CHOSE, describing the source
    # column it stands for, and overwriting it would publish a fact
    # about the twin where a profiler publishes a fact about the table
    # -- which is how a case comes to describe a different column from
    # the one its own account names.
    if column.get("n_distinct_values") == 0:
        column["n_distinct_values"] = _distinct_numbers_of(
            content,
            column.get("affix_prefix", ""),
            column.get("affix_suffix", ""),
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
        **(
            {"workbook_truths": spec["workbook_truths"]}
            if "workbook_truths" in spec
            else {}
        ),
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
    "positives ascending. M = min(K, F_num) different values. M_neg is the "
    "nearest whole number to M_rest*A_neg/(A_neg+A_pos) with ties upward, "
    "computed as (2*M_rest*A_neg + (A_neg+A_pos)) // (2*(A_neg+A_pos)) and "
    "clamped into [1, M_rest-1], where A_neg and A_pos are how many RUNS the "
    "ladder gives each band and fall back to G and P where there is no "
    "ladder (G5.2b). The zero stratum holds Z cells; each other band divides "
    "its C cells by the ladder's own plateaus (G5.2a): the value at every "
    "rank lo+i is read by Interpolate(Ladder, (lo+i)*2**53, K*2**53) with "
    "G5.4 applied where integer_valued is true, equal neighbours make a run, "
    "and runs are joined -- smallest (min(L[j],L[j+1]), 0 if "
    "Whole(H[j])==Whole(H[j+1]) else 1, |H[j+1]-H[j]|/(|H[j+1]|+|H[j]|)) "
    "first, leftmost on a tie -- or the longest divided into floor(L/2) and "
    "L-floor(L/2), leftmost on a tie, until there are M of them. The even "
    "split floor((i+1)*C/M) - floor(i*C/M) is the FALLBACK, taken only where "
    "there is no ladder or M >= C.",
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
    "datetime writes YYYY-MM-DD?HH:MM, ...:SS or ...:SS.ddd by the "
    "published time_precision, the ? being the mark separator_allocation "
    "gives the rank (T where the census names none), a column whose every "
    "moment stands at midnight writing its day with a midnight clock, and "
    "the fractional "
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
    "separator_allocation": "the census of marks between day and clock is "
    "spent over the parsed ranks by a smooth weighted rotation: each rank "
    "adds every named count to that name's credit, takes the name holding "
    "the most credit (the first in sorted order among equals) and takes "
    "the weights' total back from it; ranks the named counts leave over "
    "are added to the commonest name's weight. No rank is pinned and no "
    "word is drawn; a column counted in days by ordinal_space is written "
    "with a midnight clock (P4-D39). Where a cell's text is a declared absent "
    "spelling (matched whatever the case of its letters) it takes the first "
    "mark the census names, then the other common mark (a space for T or t, "
    "a T for a "
    "space) unless that is absent too, and the mark it owed is handed to the "
    "first rank, in rank order, allocated the mark it now wears whose new "
    "text is not absent and whose change leaves the column no spelling "
    "fewer, nor one value fewer once case is ignored; no rank is touched "
    "twice. An interior rank of a column counted in whole units whose unit "
    "wears only absent spellings steps to the nearest unit, earlier before "
    "later, inside its own window and then inside the published range. "
    "No frozen case declares an absent spelling, so that exception "
    "is pinned by the agreement test rather than by committed cells (G7.5).",
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
    method section G14.3 names, or one of the two sets it adds for the
    branches those nine leave unexercised.  The three sets share this one
    oracle and are three files only because a committed fixture must stay
    under the manifest's byte cap.
    """
    if part is None:
        part = NAMED_PART
    if part not in CASE_SETS:
        raise AssertionError(
            f"{part!r} is not one of the case sets this oracle writes: "
            f"{', '.join(sorted(CASE_SETS))}"
        )
    builders = CASE_SETS[part]
    # WHICH BUILDER, and why there are two.  A document case carries no
    # column block, no words and no word budget, because none of the
    # transforms it freezes draws a word or reads a column's facts
    # (G14.3).  It is the same oracle and the same proof layer: only the
    # shape of what is published differs, and running one builder over
    # both shapes is what would make a case describe something other
    # than its own account.
    builder = build_document_case if part == DOCUMENT_PART else build_case
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
    if part == DOCUMENT_PART:
        document["definitions"] = {**DEFINITIONS, **DOCUMENT_DEFINITIONS}
        document["word_source"] = (
            "The cases in this file are given NO WORDS, and that is a fact "
            "about the transforms rather than an omission: the written "
            "form, the arrangement of the rows, the twin of a workbook, "
            "the shape of a line before the table and the reading that "
            "settles a delimiter each draw nothing at all. What these "
            "vectors freeze is the transform from a description's own "
            "blocks to the bytes of a file."
        )
    claims = {}
    for name in sorted(builders):
        case, case_claims = builder(name)
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
    the two entry points beside this one, which name this file's own
    ``BRANCH_PART`` and ``SECOND_BRANCH_PART`` rather than repeating a
    word.

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
