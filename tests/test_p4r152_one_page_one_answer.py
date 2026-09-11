"""A fact inside its own bound is not also named as a fact the twin missed.

RESIDUAL R-P4-152, opened 2026-09-04 by review round 8 of landing L8
and closed by landing L19.

**THE MEASUREMENT THAT OPENED IT.** A plain numeric column of a hundred
values `1` to `100`, one seed:

* the deviations section said `n_distinct 100 -> 94`;
* the approximations section said `n_distinct`, published 100, achieved
  94, **inside its range**.

A reader was told a fact was not met and, four lines later, that the
measurement landed where the method said it would. A compound column
did the same for its own counts and for both halves'.

**WHY IT WAS NOT LANDING L8'S TO CHANGE, AND IS THIS ONE'S.** The
convention was the tool's rather than any role's: `_recount_notes` has
raised a deviation for any recount differing from the published count
since Phase 2, and the approximation records were added beside it
later. Changing it moves the report of every role that recounts a count
with a window -- numeric, label, affixed, joined, clock and compound --
which is why it is done in ONE place, where the two kinds of note are
assembled, rather than in six.

**WHAT A DEVIATION MEANS NOW, and it is the meaning `_bound_notes`
already used:** the twin does not hold what the description published.
For an approximated fact the publication IS the range, so landing
inside it is holding the fact. Landing outside it is still a deviation
and is still raised. Nothing is silenced: the approximations section
prints every one of them with both ends of the bound either way.
"""

import dataclasses
import pathlib

import fixtures
from synthtwin import contract, generation, taxonomy
from synthtwin import profile as profile_module
from synthtwin import reading as reading_module


def _twin(
    folder: pathlib.Path, values: "list[str]"
) -> "tuple[contract.Profile, generation.Twin]":
    table = fixtures.write(
        folder, "t.csv", fixtures.single_column_table("reading", values)
    )
    read = reading_module.read_table(f"{table}")
    document = profile_module.build_document(read, taxonomy.Settings(), [])
    written = fixtures.write_profile(folder, "t-profile.json", document)
    loaded = contract.load_profile(f"{written}")
    return loaded, generation.generate(loaded, seed=7)


def _the_hundred() -> "list[str]":
    """The residual's own column, so this closes what it opened."""
    return [f"{number}" for number in range(1, 101)]


def test_no_fact_is_both_missed_and_inside_a_range_that_covers_it(
    tmp_path: pathlib.Path,
) -> None:
    """The property, stated over every fact of every column.

    This is the one that generalizes: it does not name `n_distinct`,
    so a fact that grows a window later cannot reintroduce the
    contradiction without turning this red.
    """
    _loaded, twin = _twin(tmp_path, _the_hundred())
    settled = {
        (found.column, found.fact)
        for found in twin.approximations
        if found.inside and found.covers_published
    }
    assert settled, "the fixture must produce approximated facts"
    for note in twin.deviations:
        assert (note.column, note.fact) not in settled, (
            f"{note.fact!r} is named as a fact the twin could not meet "
            f"and, in the section below, as a measurement inside a "
            f"range that contains the published value"
        )


def test_a_bound_that_misses_the_published_value_settles_nothing() -> None:
    """The half that makes this a repair rather than a silencing.

    NONE OF THESE BOUNDS IS A MARGIN AROUND THE PUBLISHED VALUE: each
    is worked out from the description and the size of the column, so a
    bound can lie wholly to one side of the number printed beside it.
    Measured on the demonstration table, `recorded_on` publishes
    `n_distinct` 84, the twin holds 224, and the bound runs 106 to 240
    -- the twin landed inside what the method promises AND nowhere near
    what the description says. A reader grouping rows by that column
    meets 224 groups where the real table has 84.

    Dropping the deviation on `inside` alone hid exactly that, which is
    the defect this filter exists to avoid rather than to commit. It is
    dropped only where landing inside the range MEANS the published
    fact was honoured.
    """
    missed = generation.Approximation(
        column="recorded_on",
        fact="n_distinct",
        published="84",
        achieved="224",
        lowest="106",
        highest="240",
        inside=True,
        covers_published=False,
        note="how many different spellings this column holds",
    )
    raised = [
        generation.Deviation(
            column="recorded_on",
            fact="n_distinct",
            published="84",
            achieved="224",
            note="the twin holds more different spellings",
        )
    ]
    assert generation._not_settled_by_a_bound(raised, [missed]) == raised, (
        "a bound that does not contain the published value cannot say "
        "the published value was honoured"
    )
    covered = dataclasses.replace(missed, covers_published=True)
    assert generation._not_settled_by_a_bound(raised, [covered]) == []


def test_the_residuals_own_two_facts_left_the_deviations(
    tmp_path: pathlib.Path,
) -> None:
    """The specific case, measured before and after it was opened.

    Before this landing the column below raised three deviations:
    `n_distinct`, `n_distinct_folded` and `n_distinct_values`. The
    first two were also printed as inside their range.
    """
    _loaded, twin = _twin(tmp_path, _the_hundred())
    named = [note.fact for note in twin.deviations]
    assert "n_distinct" not in named
    assert "n_distinct_folded" not in named
    for fact in ("n_distinct", "n_distinct_folded"):
        assert any(
            found.fact == fact and found.inside
            for found in twin.approximations
        ), f"{fact} is still reported, in the section that bounds it"


def test_an_unwindowed_shortfall_is_as_loud_as_it_was(
    tmp_path: pathlib.Path,
) -> None:
    """The half that must NOT change, and the reason for the filter's shape.

    `n_distinct_values` counts different NUMBERS, which no method
    window authorizes to move. The twin holds 99 where the description
    publishes 100, and that is a fact the twin did not hold -- so it
    stays in the deviations exactly as it was. A filter that dropped
    every count would have made the report quieter, not honester.
    """
    _loaded, twin = _twin(tmp_path, _the_hundred())
    named = [note.fact for note in twin.deviations]
    assert "n_distinct_values" in named
    assert not any(
        found.fact == "n_distinct_values" for found in twin.approximations
    ), "and it is not windowed, which is why it must stay"


def test_a_fact_outside_its_bound_is_still_a_deviation() -> None:
    """`_bound_notes` is untouched, asserted on the function itself.

    The filter drops a deviation only where the record says `inside`.
    An approximated fact that landed outside its bound still becomes a
    deviation, and one that landed inside still cannot introduce one.
    """
    outside = generation.Approximation(
        column="reading",
        fact="mean",
        published="50.5",
        achieved="99.0",
        lowest="49.0",
        highest="52.0",
        inside=False,
        covers_published=True,
        note="the average of this column",
    )
    raised = generation._bound_notes([outside])
    assert [note.fact for note in raised] == ["mean"]
    kept = generation._not_settled_by_a_bound(raised, [outside])
    assert [note.fact for note in kept] == ["mean"], (
        "a fact outside its bound is never settled by that bound"
    )
