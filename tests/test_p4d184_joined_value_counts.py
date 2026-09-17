"""Plan P4-D184: a joined position short of its numbers is named.

THE DEFECT. Every position of a column of two or more numbers in one cell
publishes its own `n_distinct_values` under `parts[i]`, and a grouping by
that position meets exactly that count. The twin's report recounted the
count of different numbers through the column's quantitative block, which
a joined column does not have, so a position holding a number fewer than
the table was named nowhere: on the joined battery of review round
P4-G3-R1 -- twelve columns of three and four positions -- 85 positions at
four seeds came back one or two numbers short with no line in the report.

Each column here is described through the real producer, built, and its
positions recounted from the written cells; the report must name exactly
the positions whose count differs, with the plain column's sentence.
The mutation is `_joined_value_count_notes` answering nothing.
"""

import pathlib
import tempfile

from synthtwin import generation, parsing
from tests.test_p4g3r1_joined_review import _battery_column, _described
from tests.test_stage2_round_trip import _exit_of


def test_every_position_short_of_its_numbers_is_named() -> None:
    """Named where the recount differs, and nowhere else.

    Mutation: with `_joined_value_count_notes` returning [], every short
    position is silent and the first assertion fails.
    """
    short = 0
    for which in (7, 8, 11):
        _document, loaded, _folder, _table = _described(_battery_column(which))
        facts = loaded.columns[0].facts
        for seed in (0, 1, 2, 3):
            twin = generation.generate(loaded, seed)
            present = [cell for cell in twin.columns[0] if cell]
            named = {
                note.fact: note for note in twin.deviations
                if note.fact.endswith("].n_distinct_values")
            }
            for place in range(facts.n_parts):
                numbers = generation._joined_position_numbers(
                    present, facts, place
                )
                held = len({parsing.exact_of_spelling(one) for one in numbers})
                published = facts.parts[place].n_distinct_values
                fact = f"parts[{place}].n_distinct_values"
                if held == published:
                    assert fact not in named, (which, seed, place)
                    continue
                short = short + 1
                assert fact in named, (which, seed, place, published, held)
                note = named[fact]
                assert note.published == f"{published} different number(s)"
                assert note.achieved == f"{held}"
                assert note.note.startswith(f"Number {place + 1} of each cell: ")
    # THE VACUITY FLOOR: the battery really holds short positions.
    assert short >= 10, short


def test_the_real_table_still_meets_its_own_description() -> None:
    """The count is the position's own, so the table is never told it missed."""
    folder = pathlib.Path(tempfile.mkdtemp())
    _document, _loaded, described_in, table = _described(_battery_column(8))
    profile = described_in / "t.json"
    assert _exit_of(
        ["validate", str(profile), "--twin", str(table), "--out-dir", str(folder), "--replace"]
    ) == 0
