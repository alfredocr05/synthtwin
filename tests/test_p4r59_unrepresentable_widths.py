"""Residual R-P4-59: the two widths nothing measured.

A `numeric_unrepresentable` column holds numbers too long for this
format to carry as numbers -- kept as text, counted by sign and by
whether they are whole. It publishes `min_length` and `max_length`, the
character counts of its shortest and longest. Both are exactly
evidencible: count the characters of the written cells. Neither was
checked, and neither was on the not-checkable census either, while the
report claimed the census accounts for every obligation.

A column of numbers this long is rare in the tables this tool is for --
an identifier out of a sequencing pipeline, at most -- which is why it
stayed open while the width defect of an ordinary code column did not.
Rare is not never, and an obligation nothing measures is the shape this
phase has spent itself closing.
"""

import pathlib

import fixtures
from synthtwin import (
    contract,
    generation,
    profile,
    reading,
    rendering,
    taxonomy,
    validation,
)

SEED = 3
FLOOR = 11


def _described(folder: pathlib.Path):
    """Twelve numerals too long to hold, half 399 wide and half 401."""
    rows = [("9" * 399) if step % 2 else ("9" * 401) for step in range(12)]
    path = fixtures.write(
        folder, "long.csv", "code\n" + "\n".join(rows) + "\n"
    )
    table = reading.read_table(
        str(path), first_row=reading.FIRST_ROW_AUTOMATIC
    )
    document = profile.build_document(
        table, taxonomy.Settings(small_cell_floor=FLOOR), []
    )
    written = fixtures.write_profile(folder, "long-p.json", document)
    return document, contract.load_profile(str(written))


def _widths(outcome: "validation.Outcome") -> "dict[str, validation.Check]":
    return {
        one.subcheck: one
        for one in outcome.checks
        if one.subcheck in ("counts.min_length", "counts.max_length")
    }


def test_the_two_widths_are_published_and_now_checked(
    tmp_path: pathlib.Path,
) -> None:
    """Held on the twin that wears them."""
    document, described = _described(tmp_path)
    block = document["columns"][0]
    assert block["role"] == "numeric_unrepresentable"
    assert block["min_length"] == 399
    assert block["max_length"] == 401

    twin = generation.generate(described, SEED)
    outcome = validation.measure(
        described,
        str(fixtures.write(tmp_path, "twin.csv", rendering.twin_csv(twin))),
    )
    widths = _widths(outcome)
    assert set(widths) == {"counts.min_length", "counts.max_length"}
    assert widths["counts.min_length"].verdict == validation.HELD
    assert widths["counts.max_length"].verdict == validation.HELD
    assert not [
        one for one in outcome.checks if one.verdict == validation.MISSED
    ]


def test_a_file_of_one_width_misses_both(tmp_path: pathlib.Path) -> None:
    """The red case, and it agrees on everything else.

    Twelve numerals all 400 characters wide agree on the role, on every
    sign and whole count, on distinctness and on the repetition
    pattern. They violate BOTH published widths, and before this
    residual was built the report came back with no miss at all.
    """
    _document, described = _described(tmp_path)
    same = "code\n" + "\n".join(["9" * 400] * 12) + "\n"
    outcome = validation.measure(
        described, str(fixtures.write(tmp_path, "same.csv", same))
    )
    widths = _widths(outcome)
    assert widths["counts.min_length"].verdict == validation.MISSED
    assert widths["counts.min_length"].published == "399"
    assert widths["counts.min_length"].achieved == "400"
    assert widths["counts.max_length"].verdict == validation.MISSED
    assert widths["counts.max_length"].published == "401"
    assert widths["counts.max_length"].achieved == "400"
