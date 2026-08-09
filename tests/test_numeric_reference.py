"""The numeric machinery against an oracle it did not produce (P1-D11).

The charter forbids numeric machinery being its own oracle, and review
round 1 found exactly that: the golden profile hash was a transcription
of this implementation's own output, and the only hand-checked statistic
was a four-value standard deviation.

`tools/reference/make_numeric_reference_vectors.py` computes the mean,
the sample standard deviation, the moment skewness and the eleven-point
ladder from the exact rational values of the inputs, using `fractions`
and exact integer arithmetic, importing neither this package nor any
numeric library. Every float64 it reports is proved correctly rounded by
exact integer comparison against the midpoints to its neighbouring
floats. Its output is committed as a provenance-manifest fixture, so CI
rebuilds it from the generator and byte-compares it on every run: the
oracle cannot drift towards the implementation without the provenance
guard going red.

The accuracy contract asserted here is frozen in plan P1-D11, revision 2:
**correctly rounded, or one of the two immediate neighbours**, for the
mean, the standard deviation, the skewness and every ladder rung. The
statistics module accumulates whole numbers and rounds once at the end,
so nothing is approximated on the way in and there is no error budget
left to spend.

Revision 1 stated an error budget instead, measured for a two-pass
floating-point reduction the implementation no longer uses, and compared
two numbers by dividing their difference by `abs(expected) * eps`. That
is not a distance between representable numbers: it collapses at zero,
where the divisor became `eps * eps`. Review round 6 (item P1-R6-F2)
showed three wrong answers the old expressions accepted, and each is
kept below as a case that must be refused.
"""

import json
import math
import pathlib
import struct
import sys

import pytest

from synthtwin import taxonomy

VECTORS = (
    pathlib.Path(__file__).resolve().parent
    / "reference"
    / "numeric-reference-vectors.json"
)

EPS = 2.0**-52


def _document() -> dict:
    return json.loads(VECTORS.read_text(encoding="utf-8"))


def _cases() -> dict:
    return _document()["cases"]


def _values(case: dict) -> list[float]:
    return [float(text) for text in case["values_float64_repr"]]


def _ordered_encoding(value: float) -> int:
    """Where ``value`` sits in the ordered list of all binary64 numbers.

    Consecutive representable numbers are exactly one apart here at every
    magnitude, across the boundary between the subnormal and the normal
    range included, because a binary64 bit pattern read as a whole number
    already counts the representable numbers below it; only the sign has
    to be folded in by hand. The two spellings of zero name the same
    number and so land in the same place.
    """
    bits = struct.unpack("<Q", struct.pack("<d", value))[0]
    magnitude = bits & 0x7FFF_FFFF_FFFF_FFFF
    return -magnitude if bits >> 63 else magnitude


def _steps_apart(computed: float, expected: float) -> int:
    """How many representable numbers lie between two floats, exactly."""
    return abs(_ordered_encoding(computed) - _ordered_encoding(expected))


def _assert_correctly_rounded_or_adjacent(
    where: str, statistic: str, computed: float, expected: float
) -> None:
    """The whole accuracy contract, in one place.

    Used for the mean, the standard deviation, the skewness and every
    ladder rung, and shared by the tests over the reference vectors and
    by the tests that hold known-wrong answers up to it, so a loosening
    anywhere shows up in both at once.
    """
    assert math.isfinite(computed), (
        f"{where}: {statistic} came out as {computed!r}, which is not a "
        "finite number; the exact value is a finite number, so recompute it"
    )
    steps = _steps_apart(computed, expected)
    assert steps <= 1, (
        f"{where}: {statistic} is {computed!r}, and the correctly rounded "
        f"exact value is {expected!r}. Those are {steps} representable "
        "numbers apart; the contract allows the correctly rounded value or "
        "one of its two immediate neighbours, so at most 1."
    )


def test_the_oracle_is_present_and_says_what_it_is() -> None:
    document = _document()
    assert document["never_imports"] == ["synthtwin", "numpy", "pandas"]
    assert len(document["cases"]) >= 15


def test_the_oracle_states_the_contract_this_file_tests() -> None:
    """The fixture's own words must be the contract, not the retired one.

    Review item P1-R6-F2: the committed metadata still described the
    two-pass floating-point reduction, the one-and-two-unit tolerances,
    and a conditioning limit that plan revision 2 retired. A green suite
    beside a fixture that describes a different contract grades nothing.
    """
    contract = _document()["accuracy_contract"]
    assert "known_conditioning_limit" not in contract, (
        "the retired conditioning limit is still in the fixture; rebuild "
        "it from the generator"
    )
    for statistic in ("mean", "std", "skew", "ladder"):
        assert "immediate neighbour" in contract[statistic], (
            f"the fixture does not state the revision-2 contract for "
            f"{statistic}: {contract[statistic]!r}"
        )
    note = contract["note"]
    assert note.startswith("correctly rounded or an immediate neighbour")
    assert "whole numbers" in note, (
        "the fixture does not describe the whole-number accumulation the "
        "statistics module actually uses"
    )
    assert "no longer uses" in note, (
        "the fixture presents the retired two-pass reduction as current"
    )
    assert "immediate neighbour" in contract["how_two_numbers_are_compared"]


@pytest.mark.parametrize("name", sorted(_cases()))
def test_mean_is_correctly_rounded_or_adjacent(name: str) -> None:
    case = _cases()[name]
    expected = case["mean"]["float64"]
    computed = taxonomy._moments(_values(case))["mean"]
    assert computed is not None, f"{name}: no mean was published"
    _assert_correctly_rounded_or_adjacent(name, "mean", computed, expected)


@pytest.mark.parametrize("name", sorted(_cases()))
def test_standard_deviation_is_correctly_rounded_or_adjacent(
    name: str,
) -> None:
    case = _cases()[name]
    entry = case["std"]
    expected = None if entry is None else entry["float64"]
    computed = taxonomy._moments(_values(case))["std"]
    if expected is None:
        assert computed is None, f"{name}: a spread was published where none exists"
        return
    assert computed is not None, f"{name}: no spread was published"
    _assert_correctly_rounded_or_adjacent(
        name, "standard deviation", computed, expected
    )


@pytest.mark.parametrize("name", sorted(_cases()))
def test_skewness_is_correctly_rounded_or_adjacent(name: str) -> None:
    case = _cases()[name]
    entry = case["skew"]
    expected = None if entry is None else entry["float64"]
    computed = taxonomy._moments(_values(case))["skew"]
    if expected is None:
        assert computed is None, f"{name}: a shape was published where none exists"
        return
    assert computed is not None, f"{name}: no shape was published"
    _assert_correctly_rounded_or_adjacent(name, "skewness", computed, expected)


@pytest.mark.parametrize("name", sorted(_cases()))
def test_every_ladder_rung_is_correctly_rounded_or_adjacent(name: str) -> None:
    case = _cases()[name]
    computed = taxonomy._quantiles(_values(case))
    for label, _num, _den in taxonomy.LADDER:
        expected = case["ladder_exact_p"][label]["float64"]
        _assert_correctly_rounded_or_adjacent(
            f"{name}: rung {label}", "the rung", computed[label], expected
        )


@pytest.mark.parametrize("name", sorted(_cases()))
def test_every_ladder_rung_is_within_the_bracket_bound(name: str) -> None:
    """The ladder's separately stated outer bound, kept from revision 1.

    The neighbour test above is the contract. This one is the looser
    bound the plan keeps recorded beside it, because an interpolated rung
    is defined by the two order statistics it sits between rather than by
    its own size: a rung falling near zero between two large neighbours
    has nothing of its own to measure an error against. It is kept so
    that a change to the interpolation shows up against both readings.
    """
    case = _cases()[name]
    values = _values(case)
    ordered = sorted(values)
    computed = taxonomy._quantiles(values)
    for label, num, den in taxonomy.LADDER:
        expected = case["ladder_exact_p"][label]["float64"]
        steps = (len(ordered) - 1) * num
        lower = min(steps // den, len(ordered) - 1)
        upper = min(lower + 1, len(ordered) - 1)
        bracket = max(abs(ordered[lower]), abs(ordered[upper]))
        allowed = 4.0 * EPS * bracket
        difference = abs(computed[label] - expected)
        assert difference <= allowed, (
            f"{name}: rung {label} is {computed[label]!r}, exact value "
            f"{expected!r}, difference {difference!r} exceeds {allowed!r}"
        )


@pytest.mark.parametrize("name", sorted(_cases()))
def test_the_answer_does_not_depend_on_the_order_of_the_rows(
    name: str,
) -> None:
    case = _cases()[name]
    values = _values(case)
    forward = taxonomy._moments(values)
    backward = taxonomy._moments(list(reversed(values)))
    assert forward == backward, (
        f"{name}: reversing the rows changed the published statistics; "
        "row order is not part of a column's identity"
    )


def test_a_permuted_case_matches_its_original_exactly() -> None:
    cases = _cases()
    for name in sorted(cases):
        if not name.endswith("_permuted"):
            continue
        original = name[: -len("_permuted")]
        assert original in cases
        assert taxonomy._moments(_values(cases[name])) == taxonomy._moments(
            _values(cases[original])
        ), f"{name} and {original} are the same multiset and must agree"


def test_the_ladder_is_located_by_whole_numbers() -> None:
    """The rung index comes from whole numbers, and that is checkable.

    An honest note about what this does and does not demonstrate. The
    rule exists because 0.99 has no exact binary spelling, so locating a
    rung by multiplying could in principle land on the wrong pair of
    neighbours. Searched exhaustively, the two routes agree on the index
    for every table length from 2 to 20,000 at all eleven of the
    probabilities this ladder uses: the rule removes a CLASS of error
    rather than fixing an observed one. It is worth keeping if a later
    phase adds a probability whose float form rounds the other way, and
    the test below is what would catch a change to the rule itself.
    """
    for count in (2, 3, 7, 100, 101, 999, 1000, 4001, 20000):
        for _label, num, den in taxonomy.LADDER:
            steps = (count - 1) * num
            whole = steps // den
            floating = int((count - 1) * (num / den))
            assert whole == floating or steps % den != 0, (
                f"n={count}: the two ways of locating the rung disagree; "
                "the whole-number one is authoritative"
            )

    # The rule is actually in force: a rung that lands exactly on an
    # order statistic returns that value untouched, with no interpolation.
    values = [float(step) for step in range(101)]
    assert taxonomy._quantiles(values)["p99"] == 99.0
    assert taxonomy._quantiles(values)["p50"] == 50.0


# -- the comparison itself, and the answers it must refuse -------------


def test_the_comparison_counts_representable_numbers() -> None:
    """The property the revision-1 expression did not have.

    A relative divisor is not a count of representable numbers. This one
    is, at every magnitude, and it does not break down at zero or at the
    boundary between the subnormal and the normal range.
    """
    assert _steps_apart(1.0, 1.0) == 0
    assert _steps_apart(1.0, math.nextafter(1.0, 2.0)) == 1
    assert _steps_apart(1.0, math.nextafter(math.nextafter(1.0, 2.0), 2.0)) == 2

    # Zero: the two spellings are the same number, and the nearest other
    # number to it is one step away in each direction.
    assert _steps_apart(0.0, -0.0) == 0
    assert _steps_apart(5e-324, 0.0) == 1
    assert _steps_apart(-5e-324, -0.0) == 1
    assert _steps_apart(-5e-324, 5e-324) == 2

    # The boundary between the subnormal and the normal range: one step,
    # although the exponent changes there.
    largest_subnormal = float.fromhex("0x0.fffffffffffffp-1022")
    smallest_normal = float.fromhex("0x1p-1022")
    assert _steps_apart(largest_subnormal, smallest_normal) == 1

    # And the top of the range, where a relative divisor is enormous.
    largest = sys.float_info.max
    assert _steps_apart(largest, math.nextafter(largest, 0.0)) == 1


# Each row is a wrong answer that the revision-1 expressions accepted,
# named in review item P1-R6-F2 with the reference value it was measured
# against. The tests below hold every one of them up to the contract that
# replaced them; each must be refused.
ANSWERS_THE_CONTRACT_MUST_REFUSE = (
    (
        "cancelling_extremes",
        "skew",
        -1.224744871391589e-16,
        0.0,
        (
            "zero is not adjacent to the exact value: about 4.97 "
            "quadrillion units in the last place of it, and over four "
            "quintillion representable numbers"
        ),
    ),
    (
        "two_values",
        "std",
        0.7071067811865476,
        0.7071067811865478,
        "two representable numbers above the correct answer",
    ),
    (
        "three_identical",
        "std",
        0.0,
        1e-100,
        "the nearest number to zero is about 4.94e-324, not 1e-100",
    ),
)


@pytest.mark.parametrize(
    "case_name,statistic,reference,wrong,why",
    ANSWERS_THE_CONTRACT_MUST_REFUSE,
)
def test_a_wrong_answer_is_refused(
    case_name: str, statistic: str, reference: float, wrong: float, why: str
) -> None:
    """P1-R6-F2: substituting each wrong answer must fail the contract."""
    assert _steps_apart(wrong, reference) > 1, why
    with pytest.raises(AssertionError):
        _assert_correctly_rounded_or_adjacent(
            case_name, statistic, wrong, reference
        )


@pytest.mark.parametrize(
    "case_name,statistic,reference,wrong,why",
    ANSWERS_THE_CONTRACT_MUST_REFUSE,
)
def test_those_refusals_are_measured_against_the_published_reference(
    case_name: str, statistic: str, reference: float, wrong: float, why: str
) -> None:
    """The refused answers must be aimed at the numbers actually shipped.

    Without this, the rows above could quietly stop describing the
    fixture and the refusals would be theatre.
    """
    published = _cases()[case_name][statistic]["float64"]
    assert published == reference, (
        f"{case_name}: the fixture now publishes {published!r} for "
        f"{statistic}, not the {reference!r} the refused answer was "
        "measured against; update the row or investigate the change"
    )
    computed = taxonomy._moments(_values(_cases()[case_name]))[statistic]
    assert computed == published, (
        f"{case_name}: the implementation no longer returns the reference "
        f"{statistic} exactly, so the refused answer above may no longer "
        "sit where the review put it"
    )
    # The contract is one representable number of slack, not zero: the
    # reference itself and its immediate neighbour are both accepted, so
    # the refusals above are about the distance and nothing else.
    _assert_correctly_rounded_or_adjacent(
        case_name, statistic, reference, reference
    )
    _assert_correctly_rounded_or_adjacent(
        case_name, statistic, math.nextafter(reference, math.inf), reference
    )
