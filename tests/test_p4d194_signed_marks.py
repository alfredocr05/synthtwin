"""Plan P4-D194: the census of marks is held on a column with refunds.

THE REPRODUCTION (final skeptic of stage 2's close, MAJOR). P4-D185's rule
held a census of marks at a thousand only on a column holding no negative
value. An amount column of 1,500 lognormal amounts written `1,234.56`, one in
ten negated, published `{",": 396}`; the twin wrote 397 at seeds 4 and 11,
the validator printed WITHHELD, the twin exited 0, and the report named
nothing. Over forty such columns at two seeds, 36 of 80 twins wrote one to
three cells too many or too few.

THE REPAIR: the count of cells reaching a thousand is taken by size, the
positive side's run is taken first, and where a difference is left the count
is taken again and the same run is taken among the negative strata. A surplus
the rule still cannot move is named in the twin's report.

Every test is a round trip: describe, generate, describe the twin, and
validate the twin and the real table at exit 0. The mutation named is
`generation._grouped_enough` reading the column as holding no negative value.
"""

import pathlib
import random

import pytest

from tests.test_stage2_round_trip import _round_trip


def _amounts(source: int, rows: int, share: float, mu: float, sigma: float) -> "list[str]":
    draw = random.Random(source)
    cells: "list[str]" = []
    for _row in range(rows):
        value = round(draw.lognormvariate(mu, sigma), 2)
        if draw.random() < share:
            value = -value
        cells += [f"{value:,.2f}"]
    return cells


# (name, source, rows, share negated, mu, sigma): the skeptic's column, and
# three of the battery's that missed before the repair (one under, two over).
SHAPES = (
    ("skeptic-refunds", 2, 1500, 0.1, 6.3, 1.0),
    ("short-by-three", 5, 1500, 0.1, 6.5, 1.1),
    ("over-by-one", 7, 800, 0.05, 6.5, 1.1),
    ("heavy-refunds", 11, 800, 0.3, 6.5, 1.1),
)


@pytest.mark.parametrize("name,source,rows,share,mu,sigma", SHAPES)
def test_the_marks_census_comes_back_on_a_signed_column(
    name: str,
    source: int,
    rows: int,
    share: float,
    mu: float,
    sigma: float,
    tmp_path: pathlib.Path,
) -> None:
    """The twin's own description publishes the table's marks census.

    Mutation: with P4-D185's old condition put back -- no run at all on a
    column holding a negative value -- the skeptic's column comes back 397
    against 396 and the heavy refunds 285 against 286.
    """
    cells = _amounts(source, rows, share, mu, sigma)
    for seed in ("4", "11"):
        first, second, written, twin_exit, real_exit = _round_trip(
            tmp_path / f"{name}-{seed}", cells, (), seed=seed
        )
        assert first["n_negative"] > 0
        assert first["thousands_marks"] == {",": sum("," in c for c in cells)}
        assert sum("," in c for c in written) == first["thousands_marks"][","], (name, seed)
        assert second["thousands_marks"] == first["thousands_marks"], (name, seed)
        for fact in ("n_distinct_values", "n_negative", "fraction_widths"):
            assert second[fact] == first[fact], (name, seed, fact)
        assert twin_exit == 0, (name, seed)
        assert real_exit == 0, (name, seed)


def test_a_surplus_under_the_census_line_is_named() -> None:
    """A grouped surplus the values rule could not move is named, not pooled.

    Before this, a twin holding one or two grouped cells more than the
    census wrote them with the published mark, the validator printed
    WITHHELD and the report said nothing. Mutation: with the note removed
    from `_mark_places`, no `thousands_marks` note is returned.
    """
    import tempfile

    from synthtwin import contract, generation, profile, reading, taxonomy
    from tests import fixtures

    cells = _amounts(2, 1500, 0.1, 6.3, 1.0)
    folder = pathlib.Path(tempfile.mkdtemp())
    path = fixtures.write(folder, "t.csv", fixtures.single_column_table("value", cells))
    document = profile.build_document(
        reading.read_table(str(path)), taxonomy.Settings(), [], [], [], []
    )
    loaded = contract.load_profile(str(fixtures.write_profile(folder, "p.json", document)))
    column = loaded.columns[0]
    facts = column.facts
    assert isinstance(facts, contract.NumericFacts)
    census = facts.thousands_marks[","]
    for surplus in (0, 1, 2):
        groupable = [True] * (census + surplus) + [False] * (1500 - census - surplus)
        worn, notes = generation._mark_places(column, facts, groupable, 11)
        named = [note for note in notes if note.fact == "thousands_marks"]
        assert sum(
            worn[place] == "," for place in range(1500) if groupable[place]
        ) == census + surplus
        if surplus == 0:
            assert named == []
        else:
            assert len(named) == 1, surplus
            assert named[0].achieved == f"{census + surplus}"
            assert named[0].published == f"{census}"
