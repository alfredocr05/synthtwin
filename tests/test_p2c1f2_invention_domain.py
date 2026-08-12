"""The invention domain: what it holds, and that a run always ends.

Review item P2-C1-F2. Two defects, one root. The method's capacity rule
counted every string of an alphabet at every permitted length, which is a
far larger number than the constructions can actually write: a cell has
to read back as its own numeric class, has to begin with a character its
band permits, and may not be a spelling that means "no value" or one that
reads as a date. And the walk that produced the cells came back to
spellings it had already written, so a column asking for more different
values than the walk could reach never finished at all -- a genuine
description, accepted by the shipped loader, made `generate` consume the
processor without end and without a message.

What this file holds to:

* the capacity a family STATES is not below what its walk PRODUCES, for
  every class and band combination, so the number a refusal quotes is
  the number a run could actually have written;
* every walk ENDS -- it returns "no more" rather than searching on --
  for every class and band combination, when asked for more than the
  family holds;
* the producer-made description the review found is refused, in words, in
  well under a deadline this file enforces, so a regression fails loudly
  instead of hanging a test run;
* one below the boundary builds and one above it refuses, on genuine
  producer output, so the boundary is a fact and not a claim.
"""

import pathlib
import threading
import typing

import pytest

import fixtures
from synthtwin import (
    contract,
    errors,
    generation,
    parsing,
    profile,
    reading,
    taxonomy,
)

# How long a single generation run may take in this file. Nothing here
# builds more than a few dozen cells, so any run that reaches this has
# stopped making progress; the deadline exists so that a walk which
# starts searching for ever fails a test instead of hanging a run.
DEADLINE_SECONDS = 30.0

PAIRS = [
    (kind, band)
    for kind in generation._CLASSES
    for band in generation._BANDS
]


def _described(
    folder: pathlib.Path, text: str, declared: "list[str] | None" = None
) -> contract.Profile:
    """Write a table, describe it with the producer, load the description."""
    path = fixtures.write(folder, "table.csv", text)
    table = reading.read_table(str(path))
    document = profile.build_document(
        table, taxonomy.Settings(), declared if declared else []
    )
    target = fixtures.write_profile(folder, "table-profile.json", document)
    return contract.load_profile(str(target))


def _within_the_deadline(
    work: "typing.Callable[[], None]", what: str
) -> None:
    """Run ``work`` on a worker and fail if it is still going at the end.

    A hang is not an ordinary failure: it produces no message and no
    line number, and on a build machine it stops the whole run rather
    than one test. So the work is done beside this thread and the
    deadline is asserted, which turns "never finishes" into "failed
    here, with this sentence".
    """
    worker = threading.Thread(target=work, daemon=True)
    worker.start()
    worker.join(DEADLINE_SECONDS)
    assert not worker.is_alive(), (
        f"{what} did not finish within {DEADLINE_SECONDS} seconds. The "
        f"invention walk has stopped making progress, which is the "
        f"non-termination review item P2-C1-F2 closed."
    )


def _walk(kind: str, band: str, length: int, wanted: int) -> "list[str]":
    """Take up to ``wanted`` values from one family's own walk."""
    used: dict[str, int] = {}
    states: dict[str, list[int]] = {}
    taken: list[str] = []
    for _step in range(wanted):
        found = generation._made_up_cell(
            kind, band, length, 1, False, states, used
        )
        if found is None:
            return taken
        taken = taken + [found]
    return taken


@pytest.mark.parametrize("pair", PAIRS, ids=[f"{a}-{b}" for a, b in PAIRS])
@pytest.mark.parametrize("length", [1, 2, 3, 5])
def test_a_family_never_writes_more_than_its_stated_capacity(
    pair: "tuple[str, str]", length: int
) -> None:
    """The stated capacity is not below the generated domain.

    This is the half of P2-C1-F2 that made a refusal message untrue: the
    planner said one number and the construction wrote a different one.
    The walk is asked for more values than the family claims to hold, so
    a claim above the truth shows up as a short walk and a claim below
    the truth shows up as a walk that overruns it.
    """
    kind, band = pair
    room = generation._family_room(kind, band, length, 1)
    ceiling = min(room, 64)
    taken = _walk(kind, band, length, ceiling + 8)
    assert len(taken) <= room, (
        f"{kind}/{band} at length {length} wrote {len(taken)} values "
        f"where its stated capacity is {room}"
    )
    assert len(set(taken)) == len(taken), "a family repeated a spelling"


@pytest.mark.parametrize("pair", PAIRS, ids=[f"{a}-{b}" for a, b in PAIRS])
@pytest.mark.parametrize("length", [1, 2, 3, 5])
def test_every_family_walk_ends_when_it_is_asked_for_too_much(
    pair: "tuple[str, str]", length: int
) -> None:
    """A spent family says "no more" instead of searching for ever.

    Asked for one more value than a small family holds, the walk must
    return nothing rather than come back to a spelling it has already
    written. The deadline is what makes the old behaviour -- an
    unbounded search over a walk that had begun to repeat -- fail here.
    """
    kind, band = pair
    room = generation._family_room(kind, band, length, 1)
    if room > 64:
        pytest.skip("this family is far larger than a bounded walk can end")
    answers: list[object] = []

    def work() -> None:
        answers.append(_walk(kind, band, length, room + 4))

    _within_the_deadline(work, f"the {kind}/{band} walk at length {length}")
    assert answers, "the walk produced no answer at all"


@pytest.mark.parametrize("pair", PAIRS, ids=[f"{a}-{b}" for a, b in PAIRS])
def test_every_value_a_family_writes_reads_back_in_its_own_class(
    pair: "tuple[str, str]",
) -> None:
    """Class-preserving construction, checked over every family.

    The four class counts are EXACT-OBSERVABLE on every role, which they
    can only be if every constructed spelling reads back through the
    shipped classifier as the class it was built for.
    """
    kind, band = pair
    for length in (1, 2, 3, 4, 6, 9):
        for value in _walk(kind, band, length, 6):
            assert parsing.classify_number(value) == generation._reads_as(
                kind
            ), f"{kind}/{band} at length {length} wrote {value!r}"
            assert not parsing.is_missing_text(value)
            if band == generation._BAND_DIGITS:
                assert parsing.is_digit_text(value), value
            if band == generation._BAND_CODE:
                assert parsing.is_code_text(value), value
                assert not parsing.is_digit_text(value), value
            if band == generation._BAND_WIDE:
                assert not parsing.is_code_text(value), value


def _single_character_table(count: int) -> str:
    """A table of ``count`` different one-character values outside the code
    alphabet, each written once."""
    values = [chr(0x100 + 2 * index) for index in range(count)]
    return fixtures.single_column_table("note", values)


def test_the_producer_made_column_the_domain_cannot_hold_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    """The exact case review item P2-C1-F2 found, end to end.

    A genuine table of twenty-six different one-character values, none of
    them in the code alphabet, describes as free text with twenty-six
    different values each one character long and both alphabet counts
    zero. The one-character values synthtwin can write outside the code
    alphabet number twenty-five: the space is refused at both ends, the
    four characters a spreadsheet reads as the start of a formula are
    refused at the front, and two of the remainder are spellings that
    mean "no value". Twenty-six of them cannot be written, and the run
    must SAY so before writing anything -- which is what the promised
    `generation-domain-too-small` refusal is for. It used to consume the
    processor instead, without end and without a message.
    """
    folder = tmp_path / "too-small"
    folder.mkdir(parents=True, exist_ok=True)
    described = _described(folder, _single_character_table(26))
    column = described.columns[0]
    facts = column.facts
    assert isinstance(facts, contract.TextFacts)
    assert column.n_distinct == 26
    assert facts.length.minimum == 1
    assert facts.length.maximum == 1
    assert facts.n_all_digits == 0
    assert facts.n_code_alphabet == 0
    answers: list[object] = []

    def work() -> None:
        try:
            generation.generate(described, 0)
            answers.append(None)
        except errors.ProfileError as raised:
            answers.append(f"{raised}")

    _within_the_deadline(work, "generation of a column the domain cannot hold")
    assert answers, "generation produced no answer at all"
    message = answers[0]
    assert isinstance(message, str), (
        "generation built a twin for a description no table can satisfy"
    )
    assert "is valid" in message
    assert "note" in message
    assert "26" in message
    assert "25" in message
    assert "Nothing has been written" in message


def test_the_refusal_lands_exactly_at_the_boundary(
    tmp_path: pathlib.Path,
) -> None:
    """One below builds; one above refuses. The boundary is a fact.

    Both descriptions come from the shipped producer, so this is the
    capacity of the construction as a person meets it and not a number
    written into a test.
    """
    below = tmp_path / "below"
    below.mkdir(parents=True, exist_ok=True)
    described = _described(below, _single_character_table(25))
    built = generation.generate(described, 0)
    present = [cell for cell in built.columns[0] if cell != ""]
    assert len(set(present)) == 25
    for cell in present:
        assert len(cell) == 1
        assert not parsing.is_code_text(cell)
    above = tmp_path / "above"
    above.mkdir(parents=True, exist_ok=True)
    beyond = _described(above, _single_character_table(26))
    answers: list[object] = []

    def work() -> None:
        try:
            generation.generate(beyond, 0)
            answers.append(None)
        except errors.ProfileError as raised:
            answers.append(f"{raised}")

    _within_the_deadline(work, "generation one value past the boundary")
    assert answers and isinstance(answers[0], str), (
        "one value past the boundary must refuse, not build"
    )


def test_the_refusal_is_settled_before_any_cell_is_built(
    tmp_path: pathlib.Path,
) -> None:
    """The capacity question is answered in the planning stage.

    Method G9.4 puts the refusal before any output file exists, and the
    command builds nothing until the plan is settled. Asserting it on
    `plan_generation` is what makes "nothing has been written" true
    rather than merely likely.
    """
    folder = tmp_path / "planned"
    folder.mkdir(parents=True, exist_ok=True)
    described = _described(folder, _single_character_table(26))
    with pytest.raises(errors.ProfileError) as raised:
        generation.plan_generation(described)
    assert "is valid" in f"{raised.value}"
