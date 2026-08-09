"""The oracle's proof layer, tested by trying to make it certify a lie.

The reference vectors are only worth what their proof layer is worth. If
a proof routine can be handed a wrong answer and return normally, then a
future defect in the arithmetic can be certified and frozen into the
committed fixture without anything going red -- and the fixture is the
one thing the numeric machinery is graded against.

Review round 6 (item P1-R6-F1) reported three ways the layer could be
made to certify a wrong answer:

a. at the largest finite float there is no upper neighbour to take a
   midpoint with, and the upper comparison was made to pass
   unconditionally instead of being taken against the point where
   binary64 rounds up to an infinity;
b. ``+0.0 == -0.0``, so the ``< 0`` and ``> 0`` sign guards were blind to
   the sign of a zero;
c. every quantile ladder rung went straight through the construction and
   was never compared against its neighbours at all, so the file's claim
   that every published number is proved was not true of the ladder.

Each test below is the exact counterexample the review named. The
arithmetic these proofs certify was audited independently and found
correct in every published value, so nothing here is expected to change
a number: these tests hold the certification honest, not the answers.
"""

import fractions
import importlib.util
import math
import pathlib
import struct
import sys

import pytest

GENERATOR = (
    pathlib.Path(__file__).resolve().parent.parent
    / "tools"
    / "reference"
    / "make_numeric_reference_vectors.py"
)

F = fractions.Fraction


def _generator():
    """The vector generator, loaded from its path (it is not a package)."""
    spec = importlib.util.spec_from_file_location(
        "make_numeric_reference_vectors", GENERATOR
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gen = _generator()

LARGEST_FINITE = sys.float_info.max
# The first value binary64 cannot hold, and the point where round-to-
# nearest sends a value up to an infinity instead of down to the largest
# finite float. The midpoint itself rounds up, because the tie goes to
# the even significand and 2**1024 is the even one.
FIRST_VALUE_PAST_THE_RANGE = F(1 << 1024)
OVERFLOW_MIDPOINT = (F(LARGEST_FINITE) + FIRST_VALUE_PAST_THE_RANGE) / 2


def _sign_bit(value: float) -> int:
    return struct.unpack("<Q", struct.pack("<d", value))[0] >> 63


# -- (a) the boundary where binary64 rounds up to an infinity ----------


def test_the_generator_agrees_on_where_the_finite_range_stops() -> None:
    assert gen.LARGEST_FINITE == F(LARGEST_FINITE)
    assert gen.FIRST_VALUE_PAST_THE_RANGE == FIRST_VALUE_PAST_THE_RANGE
    assert gen.OVERFLOW_MIDPOINT == OVERFLOW_MIDPOINT
    # Stated the other way round, as the textbook number: the threshold
    # is (2 - 2**-53) * 2**1023.
    assert OVERFLOW_MIDPOINT == F(1 << 1024) - F(1 << 970)


def test_a_value_past_the_overflow_boundary_is_not_certified() -> None:
    """P1-R6-F1(a): the exact call the review said returns normally."""
    with pytest.raises(AssertionError) as refusal:
        gen.prove_nearest_float(F(1 << 1024), LARGEST_FINITE)
    assert "infinity" in str(refusal.value)


def test_a_value_exactly_on_the_overflow_midpoint_is_not_certified() -> None:
    # The tie goes up, to a value the format cannot hold, so the largest
    # finite float is not the answer here either.
    with pytest.raises(AssertionError):
        gen.prove_nearest_float(OVERFLOW_MIDPOINT, LARGEST_FINITE)


def test_the_mirror_of_that_boundary_below_zero_is_not_certified() -> None:
    with pytest.raises(AssertionError):
        gen.prove_nearest_float(-F(1 << 1024), -LARGEST_FINITE)
    with pytest.raises(AssertionError):
        gen.prove_nearest_float(-OVERFLOW_MIDPOINT, -LARGEST_FINITE)


def test_the_largest_finite_float_is_still_certified_below_the_midpoint() -> None:
    """The repair must refuse the overflow, not the whole top binade."""
    just_below = OVERFLOW_MIDPOINT - F(1, 1 << 8)
    gen.prove_nearest_float(just_below, LARGEST_FINITE)
    gen.prove_nearest_float(F(LARGEST_FINITE), LARGEST_FINITE)
    gen.prove_nearest_float(-just_below, -LARGEST_FINITE)


def test_a_square_root_past_the_overflow_boundary_is_not_certified() -> None:
    """P1-R6-F1(a): the second call the review said returns normally."""
    with pytest.raises(AssertionError) as refusal:
        gen.prove_correctly_rounded_sqrt(F(1 << 2048), LARGEST_FINITE)
    assert "infinity" in str(refusal.value)


def test_a_square_root_just_below_the_boundary_is_still_certified() -> None:
    radicand = (OVERFLOW_MIDPOINT - F(1, 1 << 8)) ** 2
    gen.prove_correctly_rounded_sqrt(radicand, LARGEST_FINITE)


def test_the_construction_refuses_the_same_overflow() -> None:
    # The construction already refused it; the proof layer is what did
    # not. Both must, or a hand-written value could slip past the one
    # that does not.
    with pytest.raises(ValueError):
        gen.round_rational_to_float(F(1 << 1024))
    with pytest.raises(ValueError):
        gen.correctly_rounded_sqrt(F(1 << 2048))


# -- (b) the sign of a zero -------------------------------------------


def test_positive_zero_is_not_certified_for_a_value_below_zero() -> None:
    """P1-R6-F1(b): the correctly rounded answer here is -0.0."""
    with pytest.raises(AssertionError) as refusal:
        gen.prove_nearest_float(F(-1, 1 << 2000), 0.0)
    assert "sign" in str(refusal.value)


def test_negative_zero_is_certified_for_a_value_below_zero() -> None:
    value = F(-1, 1 << 2000)
    result = gen.round_rational_to_float(value)
    assert _sign_bit(result) == 1, "a value below zero must round to -0.0"
    assert result == 0.0
    gen.prove_nearest_float(value, result)


def test_negative_zero_is_not_certified_for_a_value_above_zero() -> None:
    with pytest.raises(AssertionError):
        gen.prove_nearest_float(F(1, 1 << 2000), -0.0)
    with pytest.raises(AssertionError):
        gen.prove_nearest_float(F(0), -0.0)


def test_a_negative_zero_square_root_is_not_certified() -> None:
    """P1-R6-F1(b): ``-0.0 < 0.0`` is false, so the old guard passed it."""
    with pytest.raises(AssertionError) as refusal:
        gen.prove_correctly_rounded_sqrt(F(0), -0.0)
    assert "negative" in str(refusal.value)
    # The honest answer is still accepted.
    gen.prove_correctly_rounded_sqrt(F(0), 0.0)


def test_the_sign_bit_reader_tells_the_two_zeros_apart() -> None:
    assert gen.sign_bit_is_set(-0.0) is True
    assert gen.sign_bit_is_set(0.0) is False
    assert gen.sign_bit_is_set(-1.0) is True
    assert gen.sign_bit_is_set(1.0) is False
    # The guard it replaces cannot do this.
    assert not (-0.0 < 0.0)


def test_a_signed_root_must_carry_the_sign_it_claims() -> None:
    square = F(9, 4)
    gen.prove_correctly_rounded_signed_sqrt(square, False, 1.5)
    gen.prove_correctly_rounded_signed_sqrt(square, True, -1.5)
    with pytest.raises(AssertionError):
        gen.prove_correctly_rounded_signed_sqrt(square, True, 1.5)
    with pytest.raises(AssertionError):
        gen.prove_correctly_rounded_signed_sqrt(square, False, -1.5)
    # And for a shape that rounds to zero, the sign is still checked.
    with pytest.raises(AssertionError):
        gen.prove_correctly_rounded_signed_sqrt(F(0), True, 0.0)
    with pytest.raises(AssertionError):
        gen.prove_correctly_rounded_signed_sqrt(F(0), False, -0.0)


# -- (c) every published number is proved, the ladder included ---------


SAMPLE = [1.0, 2.0, 6.0]


def test_every_number_a_case_publishes_sits_in_a_float64_field() -> None:
    out = gen.stats(SAMPLE)
    places = [path for path, _value in gen._published_floats(out)]
    assert places, "a case published no numbers at all"
    assert all(path[-1] == "float64" for path in places)
    assert ("mean", "float64") in places
    assert ("std", "float64") in places
    assert ("skew", "float64") in places
    for label in ("min", "p01", "p25", "p50", "p75", "p99", "max"):
        assert ("ladder_exact_p", label, "float64") in places


def test_a_ladder_rung_that_comes_out_wrong_stops_the_run(monkeypatch) -> None:
    """P1-R6-F1(c): a wrong rung used to be published without a murmur.

    The first call to the construction is the mean; every call after it
    is a ladder rung. Pushing each rung one representable number off
    must stop the run, which is only true if the rungs are proved.
    """
    real = gen.round_rational_to_float
    state = {"calls": 0}

    def one_step_off(value):
        state["calls"] += 1
        result = real(value)
        return gen.next_up(result) if state["calls"] > 1 else result

    monkeypatch.setattr(gen, "round_rational_to_float", one_step_off)
    with pytest.raises(AssertionError) as refusal:
        gen.stats(SAMPLE)
    assert "not the float64 nearest" in str(refusal.value)


def test_a_wrong_mean_stops_the_run(monkeypatch) -> None:
    real = gen.round_rational_to_float
    monkeypatch.setattr(
        gen, "round_rational_to_float", lambda value: gen.next_up(real(value))
    )
    with pytest.raises(AssertionError):
        gen.stats(SAMPLE)


def test_a_wrong_spread_stops_the_run(monkeypatch) -> None:
    real = gen.correctly_rounded_sqrt
    monkeypatch.setattr(
        gen, "correctly_rounded_sqrt", lambda value: gen.next_up(real(value))
    )
    with pytest.raises(AssertionError):
        gen.stats(SAMPLE)


def test_the_sweep_refuses_a_number_with_no_exact_value_recorded() -> None:
    published = {"mean": {"float64": 1.0}, "extra": {"float64": 2.0}}
    exact_values = {("mean",): (gen.NEAREST, F(1))}
    with pytest.raises(AssertionError) as refusal:
        gen.prove_every_published_float(published, exact_values)
    assert "no exact value" in str(refusal.value)


def test_the_sweep_refuses_a_number_outside_a_float64_field() -> None:
    published = {"mean": {"float64": 1.0, "loose": 2.0}}
    exact_values = {("mean",): (gen.NEAREST, F(1))}
    with pytest.raises(AssertionError) as refusal:
        gen.prove_every_published_float(published, exact_values)
    assert "nothing proved it" in str(refusal.value)


def test_the_sweep_counts_what_it_proved() -> None:
    published = {
        "mean": {"float64": 0.5},
        "std": {"float64": 1.5},
        "skew": {"float64": -1.5},
        "ladder_exact_p": {"p50": {"float64": 0.5}},
    }
    exact_values = {
        ("mean",): (gen.NEAREST, F(1, 2)),
        ("std",): (gen.ROOT, F(9, 4)),
        ("skew",): (gen.SIGNED_ROOT, F(9, 4), True),
        ("ladder_exact_p", "p50"): (gen.NEAREST, F(1, 2)),
    }
    assert gen.prove_every_published_float(published, exact_values) == 4


def test_the_sweep_refuses_a_proof_shape_it_does_not_know() -> None:
    with pytest.raises(AssertionError) as refusal:
        gen.prove_every_published_float(
            {"mean": {"float64": 1.0}}, {("mean",): ("guesswork", F(1))}
        )
    assert "guesswork" in str(refusal.value)


# -- the committed fixture, checked without the generator's help -------


VECTORS = (
    pathlib.Path(__file__).resolve().parent
    / "reference"
    / "numeric-reference-vectors.json"
)


def _exact_rung(ordered: list, count: int, probability) -> fractions.Fraction:
    """One ladder rung of an ascending sample, as an exact rational.

    Hyndman-Fan type 7, written straight from the definition rather than
    called out of the generator, so this is an independent check of the
    numbers the generator published.
    """
    position = (count - 1) * probability
    lower = int(position)
    if lower >= count - 1:
        return ordered[count - 1]
    share = position - lower
    if share == 0:
        return ordered[lower]
    return ordered[lower] + share * (ordered[lower + 1] - ordered[lower])


def _document() -> dict:
    import json

    return json.loads(VECTORS.read_text(encoding="utf-8"))


def test_every_ladder_rung_in_the_committed_file_is_the_nearest_float() -> None:
    """P1-R6-F1(c), at the file level: every rung, one by one.

    The rung is recomputed here from the definition rather than from the
    generator's own ladder code, so this is a check of the published
    numbers and not a restatement of how they were made.
    """
    document = _document()
    checked = 0
    expected = 0
    for name, case in sorted(document["cases"].items()):
        values = [float(text) for text in case["values_float64_repr"]]
        ordered = sorted(F(value) for value in values)
        count = len(ordered)
        expected += len(case["ladder_exact_p"]) + len(case["ladder_binary_p"])
        for key, table in (
            ("ladder_exact_p", gen.LADDER),
            ("ladder_binary_p", gen.LADDER_BINARY),
        ):
            for label, probability in table:
                if label not in case[key]:
                    continue
                exact = _exact_rung(ordered, count, probability)
                published = case[key][label]["float64"]
                assert math.isfinite(published), f"{name}.{key}.{label}"
                gen.prove_nearest_float(exact, published)
                checked += 1
    assert checked == expected, "a published rung was skipped"
    assert checked >= 266, f"only {checked} rungs were checked"


def test_every_mean_spread_and_shape_in_the_file_is_the_nearest_float() -> None:
    """The other half of "each emitted float", recomputed from scratch."""
    document = _document()
    checked = 0
    for name, case in sorted(document["cases"].items()):
        values = [F(float(text)) for text in case["values_float64_repr"]]
        count = len(values)
        mean = sum(values, F(0)) / count
        gen.prove_nearest_float(mean, case["mean"]["float64"])
        checked += 1

        deviations = [value - mean for value in values]
        second = sum((d * d for d in deviations), F(0))
        third = sum((d * d * d for d in deviations), F(0))
        if count >= 2:
            assert (case["std"] is not None) == (count >= 2), name
            gen.prove_correctly_rounded_sqrt(
                second / (count - 1), case["std"]["float64"]
            )
            checked += 1
        else:
            assert case["std"] is None, name
        if count >= 3 and second != 0 and third != 0:
            m2 = second / count
            m3 = third / count
            gen.prove_correctly_rounded_signed_sqrt(
                (m3 * m3) / (m2 * m2 * m2), m3 < 0, case["skew"]["float64"]
            )
            checked += 1
        elif count >= 3 and second != 0:
            gen.prove_nearest_float(F(0), case["skew"]["float64"])
            checked += 1
        else:
            assert case["skew"] is None, name
    assert checked >= 46, f"only {checked} numbers were checked"
