"""Landing 2b.15: the number debt of a column with an unanchored ladder.

Landing 2b.12 left Codex item 7 of landing 2b.4 PARTLY closed. A published
exponent, grouped or plus-signed number reaches the number debt (P4-D91),
and P4-D92 then holds the form's own walk to the published ends -- but it
asked the LADDER for those ends, and the ladder is built from plain
decimals alone. A column whose every published number wears an exponent
therefore had no ends at all, so every spelling of its own form was
refused and the debt stood.

P4-D100 takes the ends from the published VALUES instead. Each test here
is a ROUND TRIP: the table is described, a twin is built, the twin is
described AGAIN, and both the twin AND the real table are validated. The
census is recounted off the written twin cells rather than read out of a
report, because a report naming no miss is what the defect produced.

THE LIMIT IS PINNED AS HARD AS THE CLOSE. A column whose published span
holds no reachable spelling of its form still goes short, and still says
so at exit 3 -- and the test asserting that is here so a later change
cannot quietly buy the census count with a number the column never held,
which is the trade P4-D92 was written to forbid.

Every table is built by seeded neutral code at runtime (plan D13).
"""

import pathlib

import pytest

from synthtwin import parsing

from tests.test_landing_2b12_identifiers_codes_text import _round_trip

# The floor every column here is described under: eleven rows.
_FLOOR = ("--smallest-group", "11")


def _worn(written: "list[str]") -> "dict[str, int]":
    """The census the twin actually wears, recounted off its own cells."""
    seen: "dict[str, int]" = {}
    for cell in written:
        if not cell:
            continue
        form = parsing.shape_form(cell)
        seen[form] = (seen[form] if form in seen else 0) + 1
    return seen


def _numbers(written: "list[str]") -> "list[float]":
    """Every twin cell that reads as a number, as a value."""
    got: "list[float]" = []
    for cell in written:
        value = parsing.parse_number(cell)
        if value is not None:
            got += [float(value)]
    return got


# -- P4-D100: the ends are the published values, not the ladder's rungs --


def _amounts_in_scientific_notation() -> "list[str]":
    """A spreadsheet's large amounts, written in scientific notation.

    Twenty-six cells read as numbers and every one of them wears `%.%@%`,
    so the census names that form twenty-six times. Twenty-two of them are
    published; the four held back owe the rest of it. No plain decimal is
    published anywhere, so the ladder is UNANCHORED and step 3 cannot
    spell a single rung -- which is the whole point of the column.
    """
    return (
        ["alpha"] * 20
        + ["1.1e6"] * 11
        + ["8.8e6"] * 11
        + ["5.5e6"] * 4
    )


@pytest.mark.parametrize("seed", ["4", "13", "77"])
def test_an_unanchored_exponent_column_settles_its_form_debt(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """The commonest shape, and the one the landing is for.

    Measured on the base at seven generate seeds: the census named
    `%.%@%` twenty-six times, the twin wore it TWENTY-TWO, the four
    held-back cells were written `1`, and `synthtwin validate` exited 3
    on the twin while the table passed at 0. The twin's numbers ran from
    1.0 with mean 4,188,462 against the table's 1,100,000 and 5,034,615.
    """
    cells = _amounts_in_scientific_notation()
    _first, _second, written, twin_exit, real_exit = _round_trip(
        tmp_path, cells, _FLOOR, seed
    )
    worn = _worn(written)
    assert worn["%.%@%"] == 26
    assert twin_exit == 0
    assert real_exit == 0
    # AND THE NUMBERS STAY INSIDE THE MAGNITUDES THE COLUMN PUBLISHED,
    # which is what P4-D92 bought with the census count and what P4-D100
    # must not spend again.
    values = _numbers(written)
    assert len(values) == 26
    for value in values:
        assert 1100000.0 <= value <= 8800000.0


@pytest.mark.parametrize("seed", ["4", "125"])
def test_the_close_is_not_an_accident_of_one_exponent(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """The same column three orders of magnitude down.

    Its stand-in is `4.6E2`, and the twin's numbers then match the
    table's exactly -- mean 506.54 and spread 277.47 on both -- because
    the one made-up level lands on a magnitude the column holds.
    """
    cells = (
        ["alpha"] * 20
        + ["2.2e2"] * 11
        + ["8.1e2"] * 11
        + ["4.6e2"] * 4
    )
    _first, _second, written, twin_exit, real_exit = _round_trip(
        tmp_path, cells, _FLOOR, seed
    )
    assert _worn(written)["%.%@%"] == 26
    assert twin_exit == 0
    assert real_exit == 0
    for value in _numbers(written):
        assert 220.0 <= value <= 810.0


@pytest.mark.parametrize("seed", ["4", "13"])
def test_a_span_with_no_reachable_spelling_still_goes_short_and_says_so(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """THE NAMED LIMIT, pinned so it cannot be closed by cheating.

    The reviewer's own column: published `1.1e6` and `1.2e6`, with
    `1.3e6` held back on four rows. The only spelling of `%.%@%` the
    form's own walk reaches anywhere near that magnitude is `1.3E6`,
    whose value is ABOVE the published maximum of 1,200,000 -- so the
    debt cannot be paid without writing a number larger than any the
    column published. It is therefore left unpaid and ANNOUNCED: the
    twin wears the form twenty-two times of twenty-six and validate
    exits 3 while the table passes.

    If a later change makes this test's twin exit 0, the question to ask
    is which number it invented to get there.
    """
    cells = (
        ["alpha"] * 20
        + ["1.1e6"] * 11
        + ["1.2e6"] * 11
        + ["1.3e6"] * 4
    )
    _first, _second, written, twin_exit, real_exit = _round_trip(
        tmp_path, cells, _FLOOR, seed
    )
    assert _worn(written)["%.%@%"] == 22
    assert twin_exit == 3
    assert real_exit == 0
    # The shortfall is announced, and NOT paid with an overshoot.
    for value in _numbers(written):
        assert value <= 1200000.0


@pytest.mark.parametrize("seed", ["4", "77"])
def test_p4_d92_is_not_withdrawn_where_the_ladder_has_its_own_ends(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """The anchored control: a column publishing both notations.

    P4-D100 changes nothing here -- the ladder has rungs of its own, so
    the bound is the ladder's ends exactly as P4-D92 left it. Measured
    byte-identical to the base at seven generate seeds.
    """
    cells = (
        ["alpha"] * 20
        + ["1000000"] * 11
        + ["9000000"] * 11
        + ["1.1e6"] * 11
        + ["1.2e6"] * 11
        + ["5.5e6"] * 4
    )
    _first, _second, written, twin_exit, real_exit = _round_trip(
        tmp_path, cells, _FLOOR, seed
    )
    assert _worn(written)["%.%@%"] == 26
    assert twin_exit == 0
    assert real_exit == 0
    assert "5.0E6" in written
