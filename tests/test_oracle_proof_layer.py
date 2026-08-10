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

Review round 7 (item P1-R7-F4) reported a fourth, of the same shape as
the first three -- a value that takes a different path through the code
is never handed to the proof:

d. the walk over the finished document asked ``isinstance(node, float)``,
   so a whole number under an explicit ``float64`` wrapper was neither
   proved nor reported as missing. ``{"new_statistic": {"float64": 7}}``
   with the exact value 1/3 recorded beside it passed while reporting
   that it had proved nothing at all, and the exact value it contradicts
   went unspent.

Review round 8 (item P1-R8-F3) reported a fifth, and it is the same
shape again -- a value the walk never reaches:

e. the walk descended through dictionaries and lists, and Python's JSON
   encoder also writes a tuple as an array. ``{"new_statistic": (7.0,)}``
   reported nothing proved and then serialized as ``{"new_statistic":
   [7.0]}``, so the number was published with no proof behind it.

Four repairs each named the shapes they knew about and the fifth shape
walked through the gap, so the walk is now closed instead: a node of any
shape it has no rule for stops the run. The tests below hold that shut
from both directions -- the tuple family the review named, and the
refusal of an unrecognised shape.

Each test below is the exact counterexample the review named. The
arithmetic these proofs certify was audited independently and found
correct in every published value, so nothing here is expected to change
a number: these tests hold the certification honest, not the answers.
"""

import collections
import fractions
import importlib.util
import json
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
    places = [path for path, _value in gen._published_numbers(out)]
    assert places, "a case published no numbers at all"
    measurements = [path for path in places if path[-1] == "float64"]
    counts = [path for path in places if path[-1] != "float64"]
    assert ("mean", "float64") in measurements
    assert ("std", "float64") in measurements
    assert ("skew", "float64") in measurements
    for label in ("min", "p01", "p25", "p50", "p75", "p99", "max"):
        assert ("ladder_exact_p", label, "float64") in measurements
    # Everything a case publishes that is not a measurement is one of
    # the whole-number fields named in the generator, and each of those
    # really is a whole number rather than a float wearing the name.
    assert set(counts) <= set(gen.CASE_WHOLE_NUMBER_FIELDS), counts
    for path, value in gen._published_numbers(out):
        if path[-1] == "float64":
            assert isinstance(value, float), path
        else:
            assert isinstance(value, int) and not isinstance(value, bool), path


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


# -- (d) a number that is not a Python float is still a number ---------


ONE_THIRD = {("new_statistic",): (gen.NEAREST, F(1, 3))}


def test_a_whole_number_under_a_float64_wrapper_stops_the_run() -> None:
    """P1-R7-F4: the exact document the review said passed, proving nothing."""
    with pytest.raises(AssertionError) as refusal:
        gen.prove_every_published_float({"new_statistic": {"float64": 7}}, ONE_THIRD)
    assert "binary64" in str(refusal.value)
    # The float spelling of the same false field was always refused, for
    # the arithmetic reason. The whole-number spelling is refused now
    # too, and the honest answer is still certified.
    with pytest.raises(AssertionError) as arithmetic:
        gen.prove_every_published_float(
            {"new_statistic": {"float64": 7.0}}, ONE_THIRD
        )
    assert "not the float64 nearest" in str(arithmetic.value)
    nearest = gen.round_rational_to_float(F(1, 3))
    assert (
        gen.prove_every_published_float(
            {"new_statistic": {"float64": nearest}}, ONE_THIRD
        )
        == 1
    )


@pytest.mark.parametrize(
    "value",
    [7, 0, -3, True, False, "0.3333", None, {"float64": 0.5}, [0.5]],
)
def test_a_float64_field_holding_anything_but_a_float_stops_the_run(
    value: object,
) -> None:
    """The wrapper is a promise about the type, so it is held to it.

    ``True`` is a Python int by inheritance and JSON writes ``null`` and
    text as values like any other, so each of these reaches the file as
    something the neighbour comparison cannot be applied to.
    """
    with pytest.raises(AssertionError) as refusal:
        gen.prove_every_published_float(
            {"new_statistic": {"float64": value}}, ONE_THIRD
        )
    assert "binary64" in str(refusal.value)


def test_a_whole_number_outside_the_named_fields_stops_the_run() -> None:
    claims = {("mean",): (gen.NEAREST, F(1, 2))}
    with pytest.raises(AssertionError) as refusal:
        gen.prove_every_published_float(
            {"mean": {"float64": 0.5}, "how_many_rows": 3}, claims
        )
    assert "how_many_rows" in str(refusal.value)
    # Inside a list as well, where the path runs through an index.
    with pytest.raises(AssertionError) as inside:
        gen.prove_every_published_float(
            {"mean": {"float64": 0.5}, "row": [1, 2]}, claims
        )
    assert "row.0" in str(inside.value)


def test_the_named_whole_number_fields_are_still_published() -> None:
    """The repair must refuse unproved measurements, not the counts."""
    published = {
        "n": 3,
        "mean": {"float64": 0.5},
        "std": {"decimal_digits_needed": 17, "float64": 1.5},
    }
    claims = {("mean",): (gen.NEAREST, F(1, 2)), ("std",): (gen.ROOT, F(9, 4))}
    assert gen.prove_every_published_float(published, claims) == 2


def test_true_and_false_are_not_read_as_numbers() -> None:
    """JSON writes them as ``true`` and ``false``, so they are not numbers."""
    published = {"mean": {"float64": 0.5, "decimal_is_exact": True}}
    claims = {("mean",): (gen.NEAREST, F(1, 2))}
    assert gen.prove_every_published_float(published, claims) == 1


def test_an_exact_value_that_nothing_spends_stops_the_run() -> None:
    """The match is one-to-one, so a skipped field cannot hide behind a claim.

    The count of proved numbers on its own cannot tell "the field was
    never published" from "the field was skipped": both leave the claim
    unspent, which is what the whole-number field above did.
    """
    published = {"mean": {"float64": 0.5}}
    claims = {("mean",): (gen.NEAREST, F(1, 2)), ("skew",): (gen.NEAREST, F(0))}
    with pytest.raises(AssertionError) as refusal:
        gen.prove_every_published_float(published, claims)
    assert "skew" in str(refusal.value)


def test_the_glossary_entry_named_float64_is_held_to_being_text() -> None:
    """The one exempt path, and the mutant that would use it as a hiding place.

    The document's own definitions say in words what a ``float64`` field
    means, under that name. The exemption is one enumerated path rather
    than a rule about the word, and what sits there must be text.
    """
    glossary = {"definitions": {"float64": "what a float64 field means"}}
    assert (
        gen.prove_every_published_float(
            glossary, {}, text_fields=gen.DOCUMENT_TEXT_FIELDS
        )
        == 0
    )
    with pytest.raises(AssertionError) as refusal:
        gen.prove_every_published_float(
            {"definitions": {"float64": 1.0}},
            {},
            text_fields=gen.DOCUMENT_TEXT_FIELDS,
        )
    assert "text" in str(refusal.value)
    with pytest.raises(AssertionError):
        gen.prove_every_published_float(glossary, {})


# -- (e) a number inside a container the walk did not descend into -----


Pair = collections.namedtuple("Pair", "low high")

# Each row is a document, and how many numbers the walk must find in it.
# Every container here is one Python's JSON encoder writes as an array
# or an object, so every number in it reaches the file. The tuple rows
# are the family review round 8 named; the plain dictionary and list
# rows are there so a repair that broke them would be visible too.
CONTAINER_SHAPES = (
    ({"a": {"float64": 0.5}}, 1),
    ({"a": [{"float64": 0.5}]}, 1),
    ({"a": ({"float64": 0.5},)}, 1),
    ({"a": [({"float64": 0.5},)]}, 1),
    ({"a": ([{"float64": 0.5}],)}, 1),
    ({"a": {"b": ({"float64": 0.5},)}}, 1),
    ({"a": Pair({"float64": 0.5}, {"float64": 1.5})}, 2),
    ({"a": (0.5,)}, 1),
    ({"a": (7,)}, 1),
    ({"a": ((0.5,),)}, 1),
    ({"a": [(0.5,)]}, 1),
    ({"a": (True, None, "text")}, 0),
)


@pytest.mark.parametrize("document,expected", CONTAINER_SHAPES)
def test_the_walk_finds_every_number_the_encoder_writes(
    document: dict, expected: int
) -> None:
    """The walk's account of the encoder, held up against the encoder.

    Reading the bytes back turns every array the encoder wrote into a
    list, whatever it was built from, so a container the walk stepped
    over shows up here as a number that is in the file and not in the
    walk. The expected count is stated as well, so a walk that found
    nothing on both sides could not pass.
    """
    text = json.dumps(document, sort_keys=True, allow_nan=False)
    from_the_document = list(gen._published_numbers(document))
    from_the_bytes = list(gen._published_numbers(json.loads(text)))
    assert from_the_document == from_the_bytes, (
        f"the walk over {document!r} found {from_the_document!r}, and the "
        f"walk over the bytes it becomes ({text}) found {from_the_bytes!r}"
    )
    assert len(from_the_document) == expected


def test_a_number_inside_a_tuple_is_not_skipped() -> None:
    """P1-R8-F3: the exact mutant the review said reported zero and wrote it."""
    published = {"new_statistic": (7.0,)}
    with pytest.raises(AssertionError) as refusal:
        gen.prove_every_published_float(published, {})
    assert "nothing proved it" in str(refusal.value)
    # Named by where it sits, index and all.
    assert "new_statistic.0" in str(refusal.value)
    # And the number really would have been written: this is the second
    # half of the review's reproduction.
    assert json.dumps(published, allow_nan=False) == '{"new_statistic": [7.0]}'


def test_a_number_inside_a_tuple_is_proved_when_it_is_wrapped() -> None:
    """The repair must prove the tuple's contents, not refuse tuples.

    A tuple is an array to the encoder, so a properly wrapped number
    inside one is an ordinary published number and must be counted.
    """
    published = {"rungs": ({"float64": 0.5}, {"float64": -1.5})}
    claims = {
        ("rungs", 0): (gen.NEAREST, F(1, 2)),
        ("rungs", 1): (gen.SIGNED_ROOT, F(9, 4), True),
    }
    assert gen.prove_every_published_float(published, claims) == 2
    # A wrong number in the same place is still refused.
    wrong = {"rungs": ({"float64": 0.5}, {"float64": 1.5})}
    with pytest.raises(AssertionError):
        gen.prove_every_published_float(wrong, claims)


def test_a_tuple_deep_inside_the_document_is_reached() -> None:
    published = {"outer": [{"inner": ((0.5,),)}]}
    with pytest.raises(AssertionError) as refusal:
        gen.prove_every_published_float(published, {})
    assert "outer.0.inner.0.0" in str(refusal.value)


class _NotJson:
    """A value Python's JSON encoder refuses; the walk must refuse it first."""


@pytest.mark.parametrize(
    "value",
    [{7.0}, frozenset({7.0}), b"\x07", bytearray(b"\x07"), 3 + 4j, _NotJson()],
)
def test_a_shape_the_walk_has_no_rule_for_stops_the_run(value: object) -> None:
    """Fail closed: the point of the repair, stated as a test.

    The four repairs before this one each enumerated the shapes they
    knew about, and the next shape went through the gap. What the walk
    does not recognise now stops the run, so the sixth shape is a
    failure here rather than a silently unproved number in the file.
    """
    with pytest.raises(AssertionError) as refusal:
        gen.prove_every_published_float({"odd": value}, {})
    assert "no rule for" in str(refusal.value)
    assert "odd" in str(refusal.value)


def test_a_key_that_is_not_text_stops_the_run() -> None:
    """A number in a key position would be written as the name of a field."""
    with pytest.raises(AssertionError) as refusal:
        gen.prove_every_published_float({"a": {1.5: 0.5}}, {})
    assert "not text" in str(refusal.value)
    assert json.dumps({"a": {1.5: 0.5}}) == '{"a": {"1.5": 0.5}}'


# Each row is a field added to every case, and what the refusal must
# say. The encoder writes each of these tuples as a JSON array, so every
# one of them really would have reached the file.
TUPLE_MUTANTS = (
    ((7.0,), "nothing proved it"),
    ((7,), "publishes the whole number"),
    (({"float64": 7.0},), "no exact value"),
    (({"float64": 7},), "binary64"),
    (({"nested": [(7.0,)]},), "nothing proved it"),
)


@pytest.mark.parametrize("added,refusal_says", TUPLE_MUTANTS)
def test_a_tuple_valued_field_added_to_every_case_stops_the_run(
    tmp_path, monkeypatch, added: tuple, refusal_says: str
) -> None:
    """P1-R8-F3 at the generator level, which is where the review ran it.

    The review's mutant added one tuple-valued field per case and the
    tool wrote all sixteen unproved numbers while still reporting that
    every published number had been proved. Checking the committed
    fixture after a regeneration would not have caught that: the fixture
    holds no tuple. So the mutant is driven through the whole generator
    here, and nothing may be written.
    """
    assert "[" in json.dumps({"added_later": added}, allow_nan=False)
    real = gen.stats_and_claims

    def with_a_tuple(sample):
        document, claims = real(sample)
        document["added_later"] = added
        return document, claims

    monkeypatch.setattr(gen, "stats_and_claims", with_a_tuple)
    out = tmp_path / "vectors.json"
    with pytest.raises(AssertionError) as refusal:
        gen.main(["--seed", "0", "--out", str(out)])
    assert refusal_says in str(refusal.value)
    assert not out.exists(), "the file was written although a number was unproved"


def test_a_shape_with_no_rule_stops_the_generator_too(tmp_path, monkeypatch) -> None:
    """The fail-closed refusal reaches the whole run, not only the unit."""
    real = gen.stats_and_claims

    def with_a_set(sample):
        document, claims = real(sample)
        document["added_later"] = {7.0}
        return document, claims

    monkeypatch.setattr(gen, "stats_and_claims", with_a_set)
    out = tmp_path / "vectors.json"
    with pytest.raises(AssertionError) as refusal:
        gen.main(["--seed", "0", "--out", str(out)])
    assert "no rule for" in str(refusal.value)
    assert not out.exists()


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
    return json.loads(VECTORS.read_text(encoding="utf-8"))


# How many numbers the committed file publishes today: 312 float64
# fields, and two counts per case. The floor is asserted rather than the
# exact number so that adding a case is not a failure, while a field
# quietly leaving the file shows up as a smaller count.
PUBLISHED_NUMBERS = 312
NAMED_COUNTS = 32


def _whole_number_fields(document: dict) -> frozenset:
    """The paths in the whole file that are allowed to be whole numbers."""
    return frozenset(
        ("cases", name) + field
        for name in document["cases"]
        for field in gen.CASE_WHOLE_NUMBER_FIELDS
    )


def test_the_committed_file_publishes_no_number_that_escapes_the_proof() -> None:
    """P1-R7-F4 at the file level: every number in the file, one by one.

    The proof is only as wide as the walk that feeds it, so this reads
    the committed bytes back and checks that nothing written as a number
    sits anywhere but in a ``float64`` field holding a binary64 value or
    in one of the counts the generator names.
    """
    document = _document()
    allowed = _whole_number_fields(document)
    measurements = 0
    counts = 0
    for path, value in gen._published_numbers(document):
        if path in gen.DOCUMENT_TEXT_FIELDS:
            assert isinstance(value, str), gen._where(path)
            continue
        if path[-1] == "float64":
            assert isinstance(value, float), (
                f"{gen._where(path)} carries {value!r}, which is not a "
                "binary64 value, so the proof could not be applied to it"
            )
            assert math.isfinite(value), gen._where(path)
            measurements += 1
        else:
            assert path in allowed, (
                f"{gen._where(path)} publishes {value!r} outside a 'float64' "
                "field and is not one of the named counts"
            )
            assert isinstance(value, int) and not isinstance(value, bool)
            counts += 1
    for name in document["cases"]:
        assert ("cases", name, "n") in allowed
    assert measurements >= PUBLISHED_NUMBERS, (
        f"the file now publishes {measurements} proved numbers, fewer than "
        f"the {PUBLISHED_NUMBERS} it carried when this floor was written; a "
        "field has left the file"
    )
    assert counts >= len(document["cases"])


def test_the_committed_bytes_are_proved_against_the_recorded_exact_values() -> None:
    """The file as it sits on disk, put through the proof it claims to carry.

    The generator proves the document it holds in memory. This reads the
    committed bytes back and proves those against the same record of
    exact values, so the claim is made about the file a reader gets
    rather than about a structure that existed for a moment inside the
    writer.
    """
    _, claims, whole_number_fields = gen.build_document()
    proved = gen.prove_every_published_float(
        _document(), claims, whole_number_fields, gen.DOCUMENT_TEXT_FIELDS
    )
    assert proved >= PUBLISHED_NUMBERS, (
        f"the committed file now carries {proved} proved numbers, fewer than "
        f"the {PUBLISHED_NUMBERS} it carried when this floor was written"
    )


def test_a_number_added_after_a_case_proved_itself_stops_the_run(
    tmp_path, monkeypatch
) -> None:
    """The second walk is over the assembled file, not over each case.

    The review's scenario is a field arriving after the local proof has
    already run. Here a case hands back one number more than it proved,
    exactly as an assignment made afterwards would; the walk over the
    finished file must refuse it and nothing may be written.
    """
    real = gen.stats_and_claims

    def with_one_more(sample):
        document, claims = real(sample)
        document["added_later"] = {"float64": 7}
        return document, claims

    monkeypatch.setattr(gen, "stats_and_claims", with_one_more)
    out = tmp_path / "vectors.json"
    with pytest.raises(AssertionError) as refusal:
        gen.main(["--seed", "0", "--out", str(out)])
    assert "binary64" in str(refusal.value)
    assert not out.exists(), "the file was written although a number was unproved"


def test_the_generator_says_how_many_numbers_it_proved(tmp_path, capsys) -> None:
    """The count is reported, and it is the count of what the file holds.

    Tying the reported number to the rebuilt file is what stops the
    report from being a constant: if a field stopped being visited, the
    number printed and the number in the file would part company. Both
    halves of what the walk accounted for are reported, the proved
    measurements and the named counts, so a regression in either shows
    up as a smaller number rather than as silence.
    """
    rebuilt = tmp_path / "numeric-reference-vectors.json"
    assert gen.main(["--seed", "0", "--out", str(rebuilt)]) == 0
    reported = capsys.readouterr().err
    document = json.loads(rebuilt.read_text(encoding="utf-8"))
    measurements = sum(
        1
        for path, _value in gen._published_numbers(document)
        if path[-1] == "float64" and path not in gen.DOCUMENT_TEXT_FIELDS
    )
    counts = sum(
        1
        for path, _value in gen._published_numbers(document)
        if path[-1] != "float64"
    )
    assert measurements >= PUBLISHED_NUMBERS
    assert counts >= NAMED_COUNTS
    assert f"proved {measurements} published numbers" in reported
    assert f"beside {counts} named whole-number counts" in reported
    # And the committed file is what this generator produces, byte for
    # byte -- the provenance guard's check, restated here so that a
    # change to the proof layer that moved a number would be visible in
    # this suite as well.
    assert rebuilt.read_bytes() == VECTORS.read_bytes()


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
