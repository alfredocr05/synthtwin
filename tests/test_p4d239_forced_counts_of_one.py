"""The pool that FORCES a count of one, and the spelling one row wrote.

The final review of 2026-09-18 broke the owner's ruling 5 of 2026-09-17
twice, on shapes the first writing of it (plan P4-D231) did not reach.

**P4-D239, the pool.** `parsing.pool_names_a_level` asked `levels == 1
and rows == 1`, and a count of one is forced wherever the held-back rows
come to fewer than TWICE the held-back levels. Measured: a clinical
`site` column of 2,000 rows at a floor of eleven, four sites from 137 to
700 rows and three sites with one patient each, published
`suppressed_levels` 3 and `suppressed_rows` 3, and its plain summary said
in English that three values are each shared by fewer than eleven rows
and cover three rows in total. Three levels over three rows can only be
one and one and one. The twin then wrote `group-1`, `group-2` and
`group-3` in exactly one row each, at both seeds. It survived both wider
readings P4-D231 deferred: eight levels over twelve rows has a pool of
twelve, which REACHES the census floor of eleven, and eight levels, and
yet twelve is fewer than sixteen, so four of them are single rows and the
twin wrote four single-row labels.

**The band is bounded by an exception**, and that half is measured too:
`rows < 2 * levels` is true of every long tail, so the pool must also be
smaller than the smallest PUBLISHED level or a column of 780 unique codes
comes back blank. `test_a_pool_that_is_not_an_exception_stands` of
`tests/test_ruling_levels_counted_by_subtraction.py` is that witness.

**P4-D240, the spelling.** A published level's `variants_withheld`
carried the key `1` -- by the census's own definition, one held-back
spelling covering exactly one row -- and the twin wrote that spelling in
exactly one row. Measured: 490 `F`, 500 `M` and one `f` at a floor of
eleven published `variants {"F": 490}` beside `variants_withheld
{"1": 1}` for the level `f`. Ruling 6 of the same day (plan P4-D222,
CONFIRMED) counts a rare spelling into the commonest one so that no row
is named; the label variants census was not given that treatment and now
is.

THE RED CHECKS, each measured by withdrawing the rule in place:

* the widened band (`pool_names_a_level` restored to `levels == 1 and
  rows == 1`) -- `test_three_one_patient_sites_are_counted_as_missing`,
  `test_eight_levels_over_twelve_rows_is_reached` and
  `test_a_pool_of_more_than_one_level_is_closed_too` of the ruling's own
  file;
* the exception half (`smallest_published` ignored) --
  `test_a_pool_that_is_not_an_exception_stands`, and fifteen witnesses
  of the code and long-tail batteries with it;
* the spelling pass (`_absorb_lone_spellings` returning its argument) --
  `test_a_lone_spelling_is_counted_into_the_commonest` and
  `test_no_variants_census_carries_a_count_of_one`.

Every table is built by seeded neutral code at runtime (plan D13).
"""

import pathlib
import random

import pytest

from synthtwin import taxonomy
from tests.test_final_review_labels import _round_trip
from tests.test_ruling_levels_counted_by_subtraction import (
    _blank_cells,
    _column,
)

_SITES = ("NORTH", "SOUTH", "EAST", "WEST")


def _clinical_sites() -> "list[str]":
    """2,000 rows: four sites, and three sites of one patient each."""
    cells = (
        ["NORTH"] * 700 + ["SOUTH"] * 660 + ["EAST"] * 500 + ["WEST"] * 137
        + ["STANMORE_ANNEX", "KIRKLEES_MOBILE", "PORTVALE_PILOT"]
    )
    random.Random(55).shuffle(cells)
    return cells


@pytest.mark.parametrize("seed", ["4", "11"])
def test_three_one_patient_sites_are_counted_as_missing(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """The review's own blocker, at both its seeds.

    Three levels over three rows can only be one and one and one, so
    every cell of them is counted as missing: the pool is nought, the
    twin writes three blanks and no single-row label, and both files
    validate.
    """
    result = _round_trip(
        tmp_path, {"site": _clinical_sites()},
        ("--smallest-group", "11"), seed,
    )
    column = _column(result, "site")
    assert (column["suppressed_levels"], column["suppressed_rows"]) == (0, 0)
    assert (column["n_present"], column["n_missing"]) == (1997, 3)
    assert column["n_missing_withheld"] == 3
    assert [level["label"] for level in column["levels"]] == [
        "north", "south", "east", "west",
    ]
    assert _blank_cells(result, "site") == 3
    written: "dict[str, int]" = {}
    for cell in result["twin"]["site"]:
        written[cell] = (written[cell] if cell in written else 0) + 1
    for cell in sorted(written):
        assert cell == "" or written[cell] > 1, cell
    assert (result["twin_exit"], result["real_exit"]) == (0, 0)


def test_the_summary_no_longer_counts_three_values_over_three_rows(
    tmp_path: pathlib.Path,
) -> None:
    """The sentence a reader worked the count out of, in plain English."""
    assert _round_trip(
        tmp_path, {"site": _clinical_sites()}, ("--smallest-group", "11")
    )["generated"] == 0
    summary = (tmp_path / "real-profile.txt").read_text("utf-8")
    assert "counted together instead of being published" not in summary
    for name in ("STANMORE_ANNEX", "KIRKLEES_MOBILE", "PORTVALE_PILOT"):
        assert name not in summary


@pytest.mark.parametrize("seed", ["4", "11"])
def test_eight_levels_over_twelve_rows_is_reached(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """The attack that survived BOTH wider readings the plan deferred.

    Twelve rows over eight levels: the pool reaches the census floor of
    eleven, so reading (b) does not see it, and there are eight levels,
    so reading (a) does not either -- and twelve is fewer than sixteen,
    so four of the eight are single rows whatever the rest does.
    """
    cells = ["A"] * 900 + ["B"] * 880 + ["C"] * 700
    cells += ["T1", "T1", "T2", "T2", "T3", "T3", "T4", "T4"]
    cells += ["T5", "T6", "T7", "T8"]
    random.Random(7).shuffle(cells)
    result = _round_trip(
        tmp_path, {"value": cells}, ("--smallest-group", "11"), seed
    )
    column = _column(result)
    assert (column["suppressed_levels"], column["suppressed_rows"]) == (0, 0)
    assert (column["n_present"], column["n_missing"]) == (2480, 12)
    assert _blank_cells(result) == 12
    assert (result["twin_exit"], result["real_exit"]) == (0, 0)


def test_the_floor_of_one_still_moves_nothing(tmp_path: pathlib.Path) -> None:
    """At the default floor nothing is held back, so nothing is counted out."""
    result = _round_trip(tmp_path, {"site": _clinical_sites()})
    column = _column(result, "site")
    assert column["n_missing"] == 0
    assert _blank_cells(result, "site") == 0
    assert (result["twin_exit"], result["real_exit"]) == (0, 0)


# ------------------------------------------- P4-D240, the lone spelling


def _arms() -> "list[str]":
    cells = ["F"] * 490 + ["M"] * 500 + ["f"]
    random.Random(3).shuffle(cells)
    return cells


def test_a_lone_spelling_is_counted_into_the_commonest(
    tmp_path: pathlib.Path,
) -> None:
    """490 `F`, 500 `M` and one `f` at a floor of eleven."""
    result = _round_trip(
        tmp_path, {"arm": _arms()}, ("--smallest-group", "11")
    )
    column = _column(result, "arm")
    levels = {level["label"]: level for level in column["levels"]}
    assert levels["f"]["variants"] == {"F": 491}
    assert levels["f"]["variants_withheld"] == {}
    assert levels["m"]["variants"] == {"M": 500}
    written: "dict[str, int]" = {}
    for cell in result["twin"]["arm"]:
        written[cell] = (written[cell] if cell in written else 0) + 1
    assert written == {"F": 491, "M": 500}
    assert (result["twin_exit"], result["real_exit"]) == (0, 0)


def test_no_variants_census_carries_a_count_of_one(
    tmp_path: pathlib.Path,
) -> None:
    """The census's key `1` is what states a count of one outright."""
    for floor in ("5", "11", "20"):
        folder = tmp_path / floor
        result = _round_trip(
            folder, {"arm": _arms()}, ("--smallest-group", floor)
        )
        for block in result["document"]["columns"]:
            for level in block["levels"] if "levels" in block else []:
                assert "1" not in level["variants_withheld"], floor


def test_the_default_floor_keeps_every_spelling(
    tmp_path: pathlib.Path,
) -> None:
    """A floor of one holds no spelling back, so none is counted in."""
    result = _round_trip(tmp_path, {"arm": _arms()})
    column = _column(result, "arm")
    levels = {level["label"]: level for level in column["levels"]}
    assert levels["f"]["variants"] == {"F": 490, "f": 1}
    assert levels["f"]["variants_withheld"] == {}


def test_the_spelling_rule_asked_of_the_map_itself() -> None:
    """`_absorb_lone_spellings`, stated as a check.

    A raised floor counts every spelling BELOW THE FLOOR into the
    commonest; a floor of one counts none; and where no spelling reaches
    the floor the first in sorted order takes them all, which is the tie
    rule `parsing.absorbed_census` already states.

    THE LINE IS THE FLOOR AND NOT ONE (plan P4-D275, the repair of the
    extra review round of 2026-09-18). This rule was written for a count
    of ONE and stopped there, so a spelling THREE rows wrote stood in
    `variants_withheld` under the key `3` -- a group below the line whose
    size the map states outright, and ruling 6 of 2026-09-17 draws the
    line at the floor. `{"F": 20, "f": 1, "fF": 1, "Ff": 3}` was
    `{"F": 22, "Ff": 3}` and is now `{"F": 25}`.
    """
    raised = taxonomy.Settings(small_cell_floor=11)
    plain = taxonomy.Settings(small_cell_floor=1)
    assert taxonomy._absorb_lone_spellings(
        {"F": 490, "f": 1}, raised
    ) == {"F": 491}
    assert taxonomy._absorb_lone_spellings(
        {"F": 490, "f": 1}, plain
    ) == {"F": 490, "f": 1}
    assert taxonomy._absorb_lone_spellings(
        {"F": 20, "f": 1, "fF": 1, "Ff": 3}, raised
    ) == {"F": 25}
    assert taxonomy._absorb_lone_spellings(
        {"F": 490, "f": 12}, raised
    ) == {"F": 490, "f": 12}
    assert taxonomy._absorb_lone_spellings(
        {"a": 1, "b": 1, "c": 1}, raised
    ) == {"a": 3}
