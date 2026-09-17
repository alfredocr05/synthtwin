"""Finding 3: the lost-grouping warning must reach every numeric block."""

import pathlib

import pytest

from tests.test_stage2_round_trip import _round_trip

# TWO CELLS ARE WRITTEN AT ONE PLACE, so the column is on no single grid
# and plan P4-D185's move of a stratum across a thousand does not reach it:
# that move keeps the mark these tests need lost.
#
# IT WAS ONE CELL UNTIL THE OWNER'S RULINGS OF 2026-09-17 WERE MERGED IN
# (plan P4-D222). A count of one is below `parsing.census_floor`, so the
# width census now counts that cell into the commonest width instead of
# naming it: `fraction_widths` published `{"1": 1, "2": 9}` and publishes
# `{"2": 10}`, which puts the column on a single grid after all, lets
# P4-D185's move reach it, and KEEPS the mark -- so every witness below
# passed vacuously on its own precondition. Two cells at one place are
# named at the default floor, where the line is two, and the shape is the
# one these tests were written for. Measured on the merged tree: with one
# such cell the twin of `$1,040.16` and its fellows comes back with its
# comma, with two it comes back without.
SMALL = ["1,040.16", "1,091.80", "801.65", "766.75", "229.5",
         "540.78", "283.64", "180.77", "115.02", "222.0"]


def _report(folder: pathlib.Path) -> str:
    return (folder / "real-twin-report.txt").read_text(encoding="utf-8")


@pytest.mark.parametrize("wrap", ["${}", "{} kg", "{}%"])
def test_an_affixed_twin_too_small_to_prove_its_mark_says_so(
    tmp_path: pathlib.Path, wrap: str
) -> None:
    folder = tmp_path / "affixed"
    first, second, _written, _t, _r = _round_trip(
        folder, [wrap.format(cell) for cell in SMALL], ("--smallest-group", "2"), False
    )
    assert first["role"] == "affixed_number" and second["role"] == "affixed_number"
    assert first["group_separator"] == ","
    # THE PRECONDITION IS PINNED, so the test cannot pass vacuously.
    assert second["group_separator"] == ""
    report = _report(folder)
    assert "'value' -- group_separator\n" in report
    assert "Nothing was given up in this run" not in report


def test_one_wrapper_of_a_set_too_small_to_prove_its_mark_says_so(
    tmp_path: pathlib.Path,
) -> None:
    folder = tmp_path / "set"
    cells = [f"{1000 + 437 * i:,.1f} kg" for i in range(20)] + [c + " lb" for c in SMALL]
    first, second, _written, _t, _r = _round_trip(
        folder, cells, ("--smallest-group", "2"), False, seed="8"
    )
    assert first["affix_suffix"] == " kg"
    assert first["group_separator"] == "," and second["group_separator"] == ","
    assert first["affix_variants"][0]["numbers"]["group_separator"] == ","
    assert second["affix_variants"][0]["numbers"]["group_separator"] == ""
    report = _report(folder)
    assert "'value' -- affix_variants[0].numbers.group_separator\n" in report
    assert "'value' -- group_separator\n" not in report


def test_the_numbers_beside_labels_too_small_to_prove_their_mark_say_so(
    tmp_path: pathlib.Path,
) -> None:
    folder = tmp_path / "compound"
    # TWO READINGS WRITTEN WITH AN EXPONENT, so plan P4-D185's move across a
    # thousand, which would keep the mark this test needs lost, does not
    # reach the column: that rule asks for the decimal and plain forms
    # alone. A negative reading kept it out until plan P4-D194 took the
    # rule to the negative side. It was ONE reading until the owner's
    # rulings of 2026-09-17 were merged in (plan P4-D222): a count of one
    # is below `parsing.census_floor`, so the forms map counted that cell
    # into the commonest form, the column went onto one grid and the mark
    # came back -- the precondition below, not the rule it is about.
    cells = [f"{100 + 47.3 * i:.2f}" for i in range(16)] + ["3.25e0", "4.75e0"] + ["1,040.16", "1,091.80"] + ["pending"] * 5
    first, second, _written, _t, _r = _round_trip(
        folder, cells, ("--smallest-group", "2"), False, seed="1"
    )
    assert first["role"] == "numbers_with_labels" and second["role"] == "numbers_with_labels"
    assert first["numbers"]["group_separator"] == ","
    assert second["numbers"]["group_separator"] == ""
    assert "'value' -- numbers.group_separator\n" in _report(folder)


@pytest.mark.parametrize("seed", ["0", "1", "2", "3", "5", "6", "7"])
def test_a_wrapped_twin_warns_exactly_when_its_mark_is_lost(
    tmp_path: pathlib.Path, seed: str
) -> None:
    folder = tmp_path / "sweep"
    first, second, _written, _t, _r = _round_trip(
        folder, ["$" + cell for cell in SMALL], ("--smallest-group", "2"), False, seed=seed
    )
    lost = first["group_separator"] != second["group_separator"]
    assert lost == ("'value' -- group_separator\n" in _report(folder))
