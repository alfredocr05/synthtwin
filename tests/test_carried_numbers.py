"""The carried numbers pass of 2026-09-18: each defect, from its reproduction.

Four fix branches of the extra review round each ran their own area's
tests, and the merged tree went red where one branch's rule reached
another's ground. Every test here is built from the reproduction that
found the defect, states what was measured BEFORE the repair, and turns
red when the repair is withdrawn -- each one was run against the
withdrawn repair before it was committed, and the report of this pass
records which line was reverted and what the test said.

Every table is built by seeded neutral code at runtime (plan D13) and no
value here comes from any real table.
"""

import collections
import pathlib

import pytest

from synthtwin import contract, generation, parsing, profile, reading, taxonomy
from tests import fixtures
from tests.test_extra_round_numbers import _round_trip
from tests.test_generation import _described, _every_role_text


# -- the absorbed notation and the saturated band (the merge skeptic's
#    MAJOR finding 5) -------------------------------------------------


def _absorbed_notation_cells() -> "list[str]":
    """388 positive amounts, eleven in brackets and one written with a minus.

    The merge skeptic's own shape: the positive amounts run 100.00 to
    103.87 at two places, so their grid holds exactly 388 points.
    """
    cells = [f"{100 + index * 0.01:.2f}" for index in range(388)]
    cells += [f"({1.25 + index:.2f})" for index in range(11)]
    return cells + ["-12.25"]


@pytest.mark.parametrize("seed", ["4", "1", "2", "3"])
def test_an_absorbed_notation_leaves_the_twin_every_number(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """The twin held 400 spellings of 399 numbers, and validate exited 3.

    MEASURED before the repair, at seeds 4, 1, 2 and 3 alike: ruling 6
    counts the lone `-12.25` into the brackets, so the census names
    `{"brackets": 12}`; the ladder's third percentile falls inside the
    published empty pair `(-1.25, 100.00)` and put three positive strata
    below 100; the other 385 shared the 388 points of the positive grid,
    two of them on `101.88`, and G6.5 spelled the second one `0101.88`.
    The twin wrote 400 different spellings of 399 different numbers and
    `validate` MISSED `distinct.n_distinct_values` on it while the real
    table passed.
    """
    block, written, twin_exit, real_exit = _round_trip(
        tmp_path / "absorbed", _absorbed_notation_cells(),
        ("--smallest-group", "11"), seed,
    )
    assert block["negative_notations"] == {"brackets": 11 + 1}
    assert block["n_distinct_values"] == 400
    numbers = collections.Counter(
        parsing.parse_number(cell) for cell in written
    )
    assert len(numbers) == 400, [n for n, k in numbers.items() if k > 1]
    # ...and not one number is written a second way to make up the count.
    assert not [cell for cell in written if cell[:1] == "0"], written
    # The positive band takes every point of its grid, in order.
    positive = sorted(
        value for value in numbers if value is not None and value > 0
    )
    assert positive == [
        float(f"{100 + index * 0.01:.2f}") for index in range(388)
    ]
    assert twin_exit == 0
    assert real_exit == 0


# -- the compound column's own count (plan P4-D276, amended) -----------


def test_a_compound_column_counts_the_spellings_its_halves_speak_of(
    tmp_path: pathlib.Path,
) -> None:
    """The producer wrote a compound column its own loader refused.

    MEASURED before the repair, at a floor of eleven, on forty exponents
    beside `alpha` 6, `Alpha` 6, `beta` 5 and `Beta` 5: the label half
    published `n_distinct` 3 (P4-D276), the numeric half 40, and the
    column the raw 44 -- and `contract.load_profile` refused it, because
    contract 7.14 holds the column to the two halves added.
    """
    values = (
        [f"{index * 2}e0" for index in range(1, 41)]
        + ["alpha"] * 6 + ["Alpha"] * 6 + ["beta"] * 5 + ["Beta"] * 5
    )
    path = fixtures.write(
        tmp_path,
        "compound.csv",
        fixtures.rows_to_csv(["c"], [[value] for value in values]),
    )
    document = profile.build_document(
        reading.read_table(str(path)),
        taxonomy.Settings(small_cell_floor=11),
        [],
    )
    block = document["columns"][0]
    assert block["role"] == "numbers_with_labels"
    assert block["n_numeric_distinct"] == 40
    assert block["labels"]["n_distinct"] == 1 + 2
    assert block["n_distinct"] == 40 + 1 + 2
    written = fixtures.write_profile(tmp_path, "compound.json", document)
    loaded = contract.load_profile(str(written))
    assert loaded.columns[0].n_distinct == 43


# -- the mode's plain-language note (plan P4-D267) --------------------


def test_the_mode_note_the_every_role_twin_carries_speaks_plainly(
    tmp_path: pathlib.Path,
) -> None:
    """The one note the round added spelled `str` inside a plain word.

    MEASURED before the repair: the every-role twin at seed 7 carries a
    `mode` deviation, and its note said "the stretches your table leaves
    empty" -- which the plain-language guard every deviation note answers
    to reads as the type name `str`. The guard keeps its strength; the
    sentence changed.
    """
    described = _described(
        tmp_path, _every_role_text(), ["record_code"], [fixtures.JOINED_COLUMN]
    )
    twin = generation.generate(described, 7)
    notes = [
        deviation.note
        for deviation in twin.deviations
        if deviation.fact == "mode"
    ]
    assert notes, "the every-role twin no longer reaches the mode's note"
    for note in notes:
        for jargon in ("null", "None", "int", "str", "dtype", "n_rows"):
            assert jargon not in note, (jargon, note)
