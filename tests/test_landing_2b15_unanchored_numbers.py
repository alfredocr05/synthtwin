"""Landing 2b.15: the number debt of a column with an unanchored ladder.

Landing 2b.12 left Codex item 7 of landing 2b.4 PARTLY closed. A published
exponent, grouped or plus-signed number reaches the number debt (P4-D94),
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
    """The census the twin actually wears, recounted off its own cells.

    Every column here writes its exponent in LOWER case, `1.1e6`, so
    since landing 2b.18's second part (plan P4-D121) the census names
    `%.%&%` and a cell is counted under the key the census counts it
    under -- the lower-case key for a lower-case cell.
    """
    seen: "dict[str, int]" = {}
    for cell in written:
        if not cell:
            continue
        form = parsing.census_form(cell, {"%.%&%": 1})
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
    assert worn["%.%&%"] == 26
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
    assert _worn(written)["%.%&%"] == 26
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

    **THAT QUESTION WAS ASKED AND ANSWERED AT THE NUMBERS PASS OF THE
    SECOND CODEX ROUND** (2026-09-19, item 3). The twin does now exit 0,
    and the number it invented is `1.0e6`: one step of the form's own
    grid BELOW the published minimum, placed by the LADDER, which P4-D268
    already lets step outside the published ends -- its own frozen case
    `held_back_dressed` writes `+14` and `+16` around a published `+15`.
    What P4-D92 and P4-D100 bound is the form's OWN walk of step 2, which
    is not a ladder at all and which is still held to the published ends;
    this column's debt was unpaid because the ladder could not SPELL an
    exponent form, not because a rule forbade it. Measured at seeds 4 and
    13 alike: the census comes out twenty-six of twenty-six, and the
    twin's numbers have mean 1,126,923 and standard deviation 72,430.3
    against the table's 1,173,077 and 72,430.3 -- the spread reproduced
    EXACTLY, where the unpaid twin gave 50,383, 30 per cent low -- with a
    maximum of 1,200,000 against the table's 1,300,000. The overshoot
    P4-D92 was written against was `9.6E6`, 7.4 times the largest number
    the table holds; this is 100,000 below the smallest.
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
    assert _worn(written)["%.%&%"] == 26
    assert twin_exit == 0
    assert real_exit == 0
    # ...and NOT paid with an overshoot: nothing reaches past the
    # largest number the table holds, which is what P4-D92 forbids.
    for value in _numbers(written):
        assert value <= 1300000.0
    assert max(_numbers(written)) == 1200000.0
    assert min(_numbers(written)) == 1000000.0


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
    assert _worn(written)["%.%&%"] == 26
    assert twin_exit == 0
    assert real_exit == 0
    # Lower case since landing 2b.18 part 2 (P4-D121): the column wrote
    # `1.1e6`, and the census now carries that case.
    assert "5.0e6" in written


# -- P4-D101: what the bound costs where the held-back level is a TAIL --


def _amounts_with_the_rare_level_below_the_span() -> "list[str]":
    """The same column, with its held-back level BELOW everything it
    published -- which is where a rare value usually sits.

    Twenty-six cells read as numbers and wear `%.%@%`; the published
    levels are 5,000,000 and 8,800,000 and the level held back on four
    rows is 1,100,000, smaller than either. No in-span spelling can
    stand where that level stood.
    """
    return (
        ["alpha"] * 20
        + ["5.0e6"] * 11
        + ["8.8e6"] * 11
        + ["1.1e6"] * 4
    )


@pytest.mark.parametrize("seed", ["4", "13"])
def test_a_held_back_level_below_the_span_is_paid_from_inside_it(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """THE NAMED COST, pinned so it cannot be mistaken for a win.

    P4-D100 settles this column's census in full -- and every spelling it
    can reach lies above the level it is standing in for, so the twin's
    numbers move AWAY from the table's while the exit code goes quiet.
    Measured at three seeds on both trees: the base wrote `1` four
    times at twin validate 3, with the mean 2.82 per cent low and the
    spread 11.56 per cent high; this rule writes `8.1E6` four times at
    twin validate 0, with the mean 17.93 per cent HIGH and the spread
    33.96 per cent LOW.

    This test asserts what the twin actually does, not that it is good.
    If a later change makes the mean here land on the table's, read
    P4-D101 before believing it: no spelling inside the published span
    can do that, so the question to ask is what left the span.
    """
    cells = _amounts_with_the_rare_level_below_the_span()
    _first, _second, written, twin_exit, real_exit = _round_trip(
        tmp_path, cells, _FLOOR, seed
    )
    assert _worn(written)["%.%&%"] == 26
    assert twin_exit == 0
    assert real_exit == 0
    # The stand-in is held inside the published span, which is the one
    # thing P4-D92 bought and P4-D100 must never spend.
    values = _numbers(written)
    assert len(values) == 26
    for value in values:
        assert 5000000.0 <= value <= 8800000.0
    # AND THE COST IS REAL: the twin's mean stands above the table's,
    # because the level it stood in for lay below the whole span.
    table = _numbers(cells)
    assert sum(values) / len(values) > sum(table) / len(table)


@pytest.mark.parametrize("seed", ["4"])
def test_the_report_says_where_the_made_up_numbers_were_held(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """The twin's report describes the cells this rule actually writes.

    While the bound refused every spelling, the note said those cells
    "count upward from the smallest step this column's forms write",
    and that was true -- they came out `1`. Under P4-D100 they come out
    `5.0E6`, chosen because its value lies inside the published ends, so
    the sentence became false about the very cells it describes. That is
    the class of defect this repository treats as a defect rather than a
    nuance, which is why the constant it lives in exists at all.
    """
    cells = _amounts_in_scientific_notation()
    _first, _second, written, twin_exit, _real_exit = _round_trip(
        tmp_path, cells, _FLOOR, seed
    )
    assert twin_exit == 0
    # Lower case since landing 2b.18 part 2 (P4-D121): the column wrote
    # `1.1e6`, and the census now carries that case.
    assert "5.0e6" in written
    report = (tmp_path / "real-twin-report.txt").read_text(encoding="utf-8")
    # WHAT IS TRUE OF THESE CELLS NOW (plan P4-D268, Codex item 5 of the
    # extra round of 2026-09-18). The ladder is ANCHORED on this column
    # since the anchors are taken from every accepted numeric spelling,
    # so the report carries the anchored sentence and not the unspelled
    # one: the numbers are stepped outward from the published ends, which
    # is what the walk now really does here.
    assert "stepped outward from the smallest and the largest" in report
    assert "held between the smallest and the largest number" not in report
    # ...and the clause the placed sentence already carried.
    assert "can equal one your table held back" in report
    # The sentence that was false of them is GONE as an unconditional
    # claim: it now stands only as the case where the span spells none.
    assert "made-up ones lie: they count upward" not in report
    # ...and the anchored sentence carries the statistical warning the
    # two unanchored ones always carried (plan P4-D266).
    assert "is not a fact about your table" in report


# -- NAMED LIMIT 3 of P4-D100, pinned (it was pinned by nothing) --


def _rungs_narrower_than_the_published_values() -> "list[str]":
    """A column whose PLAIN rungs are narrower than its own values.

    `1100000` and `1200000` are plain decimals, so the ladder is
    anchored and its ends are 1,100,000 to 1,200,000; `8.8e6` is a
    value those rungs do not reach, so the published span runs to
    8,800,000. The held-back level owes `%.%@%` four times, and the
    stand-in is `''` under the rungs against `5.0E6` under the span.
    """
    return (
        ["alpha"] * 20
        + ["1100000"] * 11
        + ["1200000"] * 11
        + ["8.8e6"] * 11
        + ["5.5e6"] * 4
    )


@pytest.mark.parametrize("seed", ["4", "77"])
def test_the_anchored_bound_keeps_its_own_narrower_ends(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """P4-D100 limit 3, CLOSED by plan P4-D268, and this says so.

    The limit was written to be taken: "a later change that takes it now
    has to say so". Codex item 5 of the extra round of 2026-09-18 takes
    it. The ladder's anchors come from every ACCEPTED numeric spelling
    now, not only from the ones `_plain_units` can step in, so `8.8e6` is
    an anchor of this column as well as a value of its span -- and the
    form debt is paid rather than going short.

    MEASURED, at both seeds: the census names `%.%&%` fifteen times, the
    twin wears it fifteen times where it wore it eleven, its four made-up
    cells come out `5.0e6` where they came out the plain `1100001`, and
    the twin validates at exit 0 where it exited 3. The real table exits
    0 as it always did.
    """
    cells = _rungs_narrower_than_the_published_values()
    first, _second, written, twin_exit, real_exit = _round_trip(
        tmp_path, cells, _FLOOR, seed
    )
    assert first["shape_forms"]["%.%&%"] == 15
    assert _worn(written)["%.%&%"] == 15
    assert "5.0e6" in written
    assert twin_exit == 0
    assert real_exit == 0
