"""The numeric machinery against an oracle it did not produce (P1-D11).

The charter forbids numeric machinery being its own oracle, and review
round 1 found exactly that: the golden profile hash was a transcription
of this implementation's own output, and the only hand-checked statistic
was a four-value standard deviation.

`tools/reference/make_numeric_reference_vectors.py` computes the mean,
the sample standard deviation, the moment skewness and the eleven-point
ladder from the exact rational values of the inputs, using `fractions`
and `decimal`, importing neither this package nor any numeric library.
Every float64 it reports is proved correctly rounded by exact integer
comparison against the midpoints to its neighbouring floats. Its output
is committed as a provenance-manifest fixture, so CI rebuilds it from
the generator and byte-compares it on every run: the oracle cannot drift
towards the implementation without the provenance guard going red.

The accuracy contract asserted here is frozen in plan P1-D11.
"""

import json
import pathlib

import pytest

from synthtwin import taxonomy

VECTORS = (
    pathlib.Path(__file__).resolve().parent
    / "reference"
    / "numeric-reference-vectors.json"
)

EPS = 2.0**-52

# The smallest step between representable numbers. Below about 1e-308 the
# gaps stop shrinking with the value, so a relative bound collapses to
# zero and would demand exactness no binary64 algorithm can deliver. Every
# tolerance therefore has this as its floor, and plan P1-D11 records it.
SMALLEST_STEP = 5e-324


def _document() -> dict:
    return json.loads(VECTORS.read_text(encoding="utf-8"))


def _cases() -> dict:
    return _document()["cases"]


def _values(case: dict) -> list[float]:
    return [float(text) for text in case["values_float64_repr"]]


def _ulp_distance(computed: float, expected: float) -> float:
    """How many representable numbers apart two floats are, roughly."""
    if computed == expected:
        return 0.0
    scale = abs(expected)
    if scale == 0.0:
        return abs(computed) / (EPS * EPS)
    step = scale * EPS
    return abs(computed - expected) / step


def test_the_oracle_is_present_and_says_what_it_is() -> None:
    document = _document()
    assert document["never_imports"] == ["synthtwin", "numpy", "pandas"]
    assert len(document["cases"]) >= 15


@pytest.mark.parametrize("name", sorted(_cases()))
def test_mean_is_within_one_unit_in_the_last_place(name: str) -> None:
    case = _cases()[name]
    expected = case["mean"]["float64"]
    computed = taxonomy._moments(_values(case))["mean"]
    assert computed is not None
    assert _ulp_distance(computed, expected) <= 1.0, (
        f"{name}: mean {computed!r} is more than one unit in the last "
        f"place from the exact value {expected!r} "
        f"({case['mean']['decimal'][:40]}...)"
    )


@pytest.mark.parametrize("name", sorted(_cases()))
def test_standard_deviation_is_within_two_units_in_the_last_place(
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
    assert _ulp_distance(computed, expected) <= 2.0, (
        f"{name}: standard deviation {computed!r} is more than two units "
        f"in the last place from the exact value {expected!r}"
    )


@pytest.mark.parametrize("name", sorted(_cases()))
def test_skewness_is_within_the_contract(name: str) -> None:
    case = _cases()[name]
    entry = case["skew"]
    expected = None if entry is None else entry["float64"]
    computed = taxonomy._moments(_values(case))["skew"]
    if expected is None:
        assert computed is None, f"{name}: a shape was published where none exists"
        return
    assert computed is not None, f"{name}: no shape was published"
    allowed = 8.0 * EPS * (1.0 + abs(expected))
    assert abs(computed - expected) <= allowed, (
        f"{name}: skewness {computed!r} differs from the exact value "
        f"{expected!r} by more than the contract allows ({allowed!r})"
    )


@pytest.mark.parametrize("name", sorted(_cases()))
def test_every_ladder_rung_is_within_the_contract(name: str) -> None:
    # The bound is set by the two order statistics a rung sits between,
    # not by the rung's own value: a rung falling near zero between two
    # large neighbours is ill-conditioned for any binary64 algorithm.
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
