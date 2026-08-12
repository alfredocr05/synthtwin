"""What the invention walk's bound is, and what it is not.

Review item P2-C2-F8. The method's G9.2 carried, beside its true
finite-family termination proof, a tighter sentence: that the walk
visits at most one more index than the number of pieces of text the
column has already written. That sentence was FALSE. It counted only
the rejection that consults the column's history and left out the ones
that do not -- a candidate reading back as the wrong numeric class, a
candidate that means "no value", a candidate that reads as a date, and,
while a fold collision is being asked for, a candidate holding no
character with a case. A false normative bound is worse than a missing
one: an independent implementation that used `used + 1` as its refusal
threshold would refuse a family from which the shipped walk returns a
value.

What this file holds to:

* one direct adversarial case per rejection rule, each exercised with
  an EMPTY history, so each proves on its own that the retired sentence
  cannot hold;
* the true bound instead: the cursor of one family never moves
  backwards outside the collision ask's single rewind, no index is ever
  taken twice by the ordinary rule, and the walk stops at the family's
  own size;
* the collision ask, when it gives up, hands back "no more" so the walk
  is put back where the pass began -- the promise G9.2 makes -- rather
  than carrying on and spending the indices the rewind exists to
  protect;
* the retired sentence is gone from the normative text and the true
  statement is there in its place.
"""

import pathlib

from synthtwin import generation, parsing

METHOD = pathlib.Path(__file__).resolve().parents[1] / (
    "docs/spec/generation-method-v1.md"
)

# The three families this file holds the specification to, each named in
# G9.2's own table. Every one of them is reachable with nothing written.
WRONG_CLASS = ("out_of_range", "code", 5, 1, 0)
MEANS_NO_VALUE = ("text", "wide", 1, 1, 11)
READS_AS_A_DATE = ("number", "digits", 8, 1, 10101)


def _at(case: "tuple[str, str, int, int, int]") -> str:
    """The candidate one named family's enumeration puts at one index."""
    kind, band, length, words, index = case
    built = generation._family_at(kind, band, length, words, index)
    assert built is not None
    return built


# -- one adversarial case per rejection rule ---------------------------


def test_a_wrong_class_candidate_is_stepped_past_with_nothing_written() -> (
    None
):
    """The review's own case, and it settles the retired sentence alone.

    With an empty history the walk visits index 0, refuses it because it
    reads back as an ordinary number rather than one off the range, and
    produces its value at index 1. The retired sentence allowed one
    index; the walk needs two.
    """
    kind, band, length, words, index = WRONG_CLASS
    candidate = _at(WRONG_CLASS)
    assert candidate == "0e999"
    assert parsing.classify_number(candidate) == parsing.NUMBER
    assert generation._reads_as(kind) == parsing.NUMBER_OUT_OF_RANGE

    used: dict[str, int] = {}
    state = [index]
    built = generation._walked_cell(
        kind, band, length, words, False, state, used
    )
    assert built == "1e999"
    assert state[0] == index + 2, (
        "two indices were visited for the first value of an empty column, "
        "so no bound stated in what the column has already written holds"
    )


def test_a_no_value_candidate_is_stepped_past_with_nothing_written() -> None:
    """The spellings that mean "no value" reject on their own list."""
    kind, band, length, words, index = MEANS_NO_VALUE
    candidate = _at(MEANS_NO_VALUE)
    assert parsing.is_missing_text(candidate)
    assert generation._family_at(kind, band, length, words, 17) == "?"

    used: dict[str, int] = {}
    state = [index]
    built = generation._walked_cell(
        kind, band, length, words, False, state, used
    )
    assert built is not None and not parsing.is_missing_text(built)
    assert state[0] > index + 1


def test_a_date_reading_candidate_is_stepped_past_with_nothing_written() -> (
    None
):
    """Thirty-one consecutive rejections, with an empty history.

    The eight-figure family reaches the first day of the first year at
    index 10101 and steps past every day of that month. A walk allowed
    one index per value already written would stop on the first of them.
    """
    kind, band, length, words, index = READS_AS_A_DATE
    run = [
        generation._family_at(kind, band, length, words, step)
        for step in range(index, index + 31)
    ]
    assert all(
        candidate is not None and generation._reads_as_a_date(candidate)
        for candidate in run
    )
    assert not generation._reads_as_a_date(
        _at((kind, band, length, words, index + 31))
    )

    used: dict[str, int] = {}
    state = [index]
    built = generation._walked_cell(
        kind, band, length, words, False, state, used
    )
    assert built == "00010132"
    assert state[0] == index + 32


def test_the_collision_ask_rejects_a_candidate_with_no_case() -> None:
    """Rule five, and it is the only rule the ask itself adds."""
    kind, band, length, words = ("number", "digits", 4, 1)
    used: dict[str, int] = {}
    state = [0]
    asked = generation._walked_cell(
        kind, band, length, words, True, state, used
    )
    assert asked is None, (
        "no spelling written in figures alone holds a character with a "
        "case, so the pass that asks for one finds nothing"
    )
    assert used == {}, "a pass that produced nothing claimed nothing"


def test_an_already_written_candidate_is_stepped_past() -> None:
    """Rule one, the only rejection the retired sentence accounted for."""
    kind, band, length, words = ("number", "digits", 4, 1)
    used: dict[str, int] = {}
    first = generation._walked_cell(
        kind, band, length, words, False, [0], used
    )
    second = generation._walked_cell(
        kind, band, length, words, False, [0], used
    )
    assert first is not None and second is not None
    assert first != second


# -- the bound that IS true --------------------------------------------


def test_the_ask_that_gives_up_puts_the_walk_back_where_it_began() -> None:
    """G9.2's promise, asked of the code rather than assumed.

    The ask may be abandoned after a stated number of rejections. What
    the abandoning may NOT do is carry on inside the same pass: the
    indices it stepped over would then be spent for good, and a column
    asking for more different values than the family had left would lose
    them. Giving up hands back "no more" so the caller rewinds.
    """
    kind, band, length, words = ("number", "digits", 6, 1)
    states: dict[str, list[int]] = {}
    used: dict[str, int] = {}
    built = generation._made_up_cell(
        kind, band, length, words, True, states, used
    )
    assert built is not None
    key = f"{kind}/{band}/{length}/{words}"
    assert states[key][0] == 1, (
        "the value came from the family's FIRST index, so the pass that "
        "asked for a letter and gave up spent none of it"
    )
    assert generation._family_at(kind, band, length, words, 0) == built


def test_one_family_never_takes_an_index_twice() -> None:
    """The termination argument, exercised rather than asserted."""
    kind, band, length, words = ("text", "wide", 2, 1)
    states: dict[str, list[int]] = {}
    used: dict[str, int] = {}
    key = f"{kind}/{band}/{length}/{words}"
    seen: list[str] = []
    cursors: list[int] = []
    for _step in range(60):
        built = generation._made_up_cell(
            kind, band, length, words, False, states, used
        )
        if built is None:
            break
        seen = seen + [built]
        cursors = cursors + [states[key][0]]
    assert len(set(seen)) == len(seen)
    assert cursors == sorted(cursors)
    assert cursors[0] >= 1
    assert cursors[-1] <= generation._family_room(kind, band, length, words)


def test_the_walk_stops_at_the_familys_own_size() -> None:
    """A spent family says "no more" rather than beginning again."""
    kind, band, length, words = ("contradictory", "wide", 4, 1)
    room = generation._family_room(kind, band, length, words)
    used: dict[str, int] = {}
    state = [room]
    assert (
        generation._walked_cell(kind, band, length, words, False, state, used)
        is None
    )
    assert state[0] == room


# -- the normative text says the true thing ----------------------------


def test_the_false_bound_is_gone_and_the_true_one_is_stated() -> None:
    """The specification is the artifact an independent reader trusts."""
    text = METHOD.read_text(encoding="utf-8")
    assert "at most one more than the number of pieces of text" not in text, (
        "the retired sentence is a refusal threshold an independent "
        "implementation would adopt, and it is false"
    )
    assert "P2-C2-F8" in text
    for rule in (
        "reads back as some other numeric class",
        'means "no value"',
        "reads as a date under",
        "holds no character with a case",
    ):
        assert rule in text, rule
    assert "0e999" in text
    assert "10101" in text


def test_the_ask_ceiling_is_the_one_the_method_states() -> None:
    """A limit two programs could pick differently is not a local choice.

    Where the ask gives up decides which value a column writes whenever
    a family holds a value with a case beyond one program's ceiling and
    inside another's. The twin's bytes are a function of the description
    and the seed, so the number belongs in the method text and this
    module has to spell the same one.
    """
    text = METHOD.read_text(encoding="utf-8")
    assert "4,096" in text
    assert generation._ASK_STEPS == 4096
