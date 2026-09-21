"""What the pool's published scale must NOT say (repair pass 2026-09-21).

THE LANDING THIS REPAIRS is plan P4-D301: contract 6.3.3 publishes how
many of a column's held-back cells read as numbers, their mean and their
population spread, and method G8.3c places the twin's made-up numbers on
them. `tests/test_pooled_number_scale.py` holds the landing's own
reproduction and is untouched by this file; what is here is the three
things the review of 2026-09-21 measured the landing getting wrong away
from the nine shapes it was built on.

1. A SCALE THE GENERATOR IS FORBIDDEN TO WRITE was published. Method
   G8.3a step 3 allows no made-up number more figures before the mark
   than the widest number the column SHOWS, and G8.3c is held to the
   same bound; where the pool ran wider than that, the description
   stated an obligation no conforming twin could meet and `validate`
   said the twin was wrong for obeying the rule it was given. Measured:
   300 `hold`, twenty `7` and five each of 1000000 to 5000000 at a floor
   of eleven published a mean of 3000000 and a spread of
   1414213.562373095, its twin's own pool stood at 6.68 and 1.434, and
   the twin exited 3 where the real table exited 0. Over a sixty-shape
   sweep of the same family, 52 of 120 runs did that.

2. A POOL OF NO SPREAD published the value of every cell in it. Four
   spellings of one number are four levels and one value, so the mean IS
   what each of those cells held and the spread says so: 200 `blank`,
   forty `3` and eight each of `5`, `5.0`, `05` and `5.00` published
   "32 cells, average 5.0, spread 0.0" on the page a person reads. The
   shape below spells the five SIX ways for the same thirty-two cells,
   so that the level rule of finding 4 is not what refuses it.

3. A FILE THAT LOST THE POOL closed the check on itself. The two
   obligations are measured against the checked file's own re-described
   block, and that block is written by the producer rules that refuse a
   pool -- so a twin that collapsed its pool onto one value published no
   scale, and both obligations came back WITHHELD rather than MISSED.

(The fourth thing the review measured, that three held-back levels leave
the reader one answer and not a family, is closed in the producer by
`taxonomy._POOLED_SCALE_LEVELS`, whose own comment carries the sweep
that chose six; `test_a_pool_of_too_few_levels_is_not_published` below
is its reproduction.)

Every table is built by seeded neutral code at runtime (plan D13).
"""

import json
import math
import pathlib
import statistics

from synthtwin import contract, parsing, summary, taxonomy
from tests.test_pooled_number_scale import (
    FLOOR,
    _anchored_cells,
    _loaded,
    _missed,
)
from tests.test_stage2_round_trip import _round_trip

_SILENT = {"n_cells": 0, "mean": None, "spread": None}


def _wider_than_the_column_shows() -> "list[str]":
    """The width reproduction: a pool seven figures wide beside a `7`.

    Six held-back numeric levels, unevenly spaced, so that neither the
    level rule nor the looseness rule refuses this shape and the width
    rule is measured on its own.
    """
    cells = ["hold"] * 300 + ["7"] * 20
    for value in (1000000, 1000001, 2400000, 3900000, 5100000, 6800000):
        cells += [str(value)] * 4
    return cells


def _one_value_spelled_six_ways() -> "list[str]":
    """The flat reproduction: six levels and one number, five.

    SIX and not the four the review measured, so that the level rule is
    not what refuses this shape and the flat rule is measured on its
    own; and the published `3` is one figure wide like the five, so the
    width rule is not what refuses it either.
    """
    cells = ["blank"] * 200 + ["3"] * 40
    for spelling in ("5", "5.0", "05", "5.00", "5.000", "05.0"):
        cells += [spelling] * 8
    return cells


def _three_levels_of_whole_numbers() -> "list[str]":
    """The solvable reproduction: three held-back levels of ten rows."""
    cells = ["yes"] * 200 + ["50"] * 30
    for value in (44, 45, 62):
        cells += [str(value)] * 10
    return cells


def test_a_pool_wider_than_the_column_shows_is_not_published(
    tmp_path: pathlib.Path,
) -> None:
    """Finding 1: a scale G8.3a forbids the generator is not stated.

    The column publishes one number, `7`, so a made-up number of this
    column has one figure before the mark and no more. Its held-back
    numbers have seven. Publishing their mean would ask every file for
    a pool around three million that no conforming twin may write, so
    the block reaches the state that says nothing and the column is
    left exactly as it stood before plan P4-D301.
    """
    cells = _wider_than_the_column_shows()
    first, second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "wide", cells, FLOOR
    )
    assert (twin_exit, real_exit) == (0, 0)
    assert first["suppressed_numbers"] == _SILENT
    assert second["suppressed_numbers"] == _SILENT
    # THE COLUMN STILL PUBLISHES ITS POOL AS A POOL: what is withheld is
    # the scale alone, and the counts the floor does publish are there.
    assert first["suppressed_levels"] == 6
    assert first["suppressed_rows"] == 24


def test_withdrawing_the_width_rule_states_an_obligation_no_twin_can_meet(
    tmp_path: pathlib.Path, monkeypatch: object
) -> None:
    """THE MUTATION CHECK for finding 1, run in place.

    `taxonomy._whole_figures_of` answering one for every number makes
    the pool's own width and the column's published width equal, which
    is the rule withdrawn: the comparison can no longer refuse
    anything. The description then publishes a mean above three million
    while every number the twin is ALLOWED to write has the one figure
    `7` shows, so the twin's own numbers stand two decimal orders below
    the scale its description states -- an obligation no conforming file
    could meet.

    THE EXIT CODE IS NOT WHAT THIS ASSERTS, and that is itself measured:
    the twin's own description publishes no pool, so `validate` withholds
    both obligations and exits 0. `validation._pooled_scale_checks` says
    in as many words why this check is vacuous today and what closes it.
    """
    cells = _wider_than_the_column_shows()
    folder = tmp_path / "wide"
    monkeypatch.setattr(  # type: ignore[attr-defined]
        taxonomy, "_whole_figures_of", lambda _value: 1
    )
    first, _second, written, twin_exit, real_exit = _round_trip(
        folder, cells, FLOOR
    )
    scale = first["suppressed_numbers"]
    assert scale["n_cells"] == 24
    assert scale["mean"] is not None and scale["mean"] > 3000000.0
    twin = [
        float(parsing.parse_number(parsing.trimmed(cell)) or 0.0)
        for cell in written
        if parsing.classify_number(parsing.trimmed(cell)) == parsing.NUMBER
    ]
    assert twin and max(twin) < 100.0
    assert (twin_exit, real_exit) == (0, 0)
    assert _missed(_loaded(folder), folder / "same.csv", cells) == []


def test_a_pool_of_one_value_spelled_several_ways_is_not_published(
    tmp_path: pathlib.Path,
) -> None:
    """Finding 2: a pool of no spread is not published, and not printed.

    Six spellings of five are six levels the floor holds back and one
    value, so a mean of 5.0 beside a spread of 0.0 names what all
    forty-eight of those cells held. The block says nothing instead, and
    the page a person reads carries no line about them.
    """
    cells = _one_value_spelled_six_ways()
    folder = tmp_path / "flat"
    first, second, _written, twin_exit, real_exit = _round_trip(
        folder, cells, FLOOR
    )
    assert (twin_exit, real_exit) == (0, 0)
    assert first["suppressed_numbers"] == _SILENT
    # AND THE TWIN'S OWN POOL SAYS NOTHING EITHER, for the looseness
    # reason `_POOLED_SCALE_LOOSENESS` states rather than this one: the
    # twin writes six different made-up numbers evenly spaced where the
    # table held one value, which is the tightest arrangement there is.
    assert second["suppressed_numbers"] == _SILENT
    # AND THE PAGE SAYS NOTHING EITHER. The summary line stands only
    # where the block speaks, so the sentence that printed the value is
    # gone with the fact behind it.
    page = summary.render(
        json.loads(
            (folder / "real-profile.json").read_text(encoding="utf-8")
        ),
        "",
    )
    assert "spread 0.0" not in page
    assert "the ones that were numbers" not in page


def test_withdrawing_the_flat_rule_publishes_the_held_back_value(
    tmp_path: pathlib.Path, monkeypatch: object
) -> None:
    """THE MUTATION CHECK for finding 2, run in place.

    The refusal is `spread <= 0.0` in `taxonomy._pooled_numbers`, asked
    of the moments once they are computed. Here the moments are made to
    answer a spread of nought for the LANDING'S OWN reproduction, whose
    hundred pooled cells hold ten different numbers: with the rule in
    place the block goes silent, and with it withdrawn the block would
    publish mean 204.5 beside spread 0.0 -- which says every one of
    those hundred held-back cells holds 204.5.
    """
    monkeypatch.setattr(  # type: ignore[attr-defined]
        taxonomy,
        "population_moments_of",
        lambda _numbers: (204.5, 0.0),
    )
    first, _second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "anchored", _anchored_cells(), FLOOR
    )
    assert (twin_exit, real_exit) == (0, 0)
    assert first["suppressed_numbers"] == _SILENT
    assert first["suppressed_levels"] == 10


def test_a_pool_of_too_few_levels_is_not_published(
    tmp_path: pathlib.Path,
) -> None:
    """Finding 4: three held-back levels leave the reader one answer.

    200 `yes`, thirty `50` and ten each of 44, 45 and 62 at a floor of
    eleven -- the published number two figures wide like the pool, and
    the pool loose enough to clear `_POOLED_SCALE_LOOSENESS`, so that
    only the level count is under measurement. Three levels over thirty rows with every level under eleven
    admits the sizes (10, 10, 10) and no others; `n_cells` equal to
    `suppressed_rows` says all three hold numbers; and a search over
    whole numbers with that mean and that spread returns (44, 46, 48)
    and nothing else. The producer now asks for six levels, and
    `taxonomy._POOLED_SCALE_LEVELS` carries the sweep that chose six.
    """
    cells = _three_levels_of_whole_numbers()
    first, _second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "three", cells, FLOOR
    )
    assert (twin_exit, real_exit) == (0, 0)
    assert first["suppressed_levels"] == 3
    assert first["suppressed_numbers"] == _SILENT
    # THE SOLUTION THE OLD RULE HANDED OVER, stated so that the reason
    # is in the suite and not only in a comment: the pool's own mean and
    # spread, and the three values they come back to.
    values = (44, 45, 62)
    total = sum(values)
    square = sum(value * value for value in values)
    answers: "list[tuple[int, int, int]]" = []
    for low in range(0, 120):
        for middle in range(low + 1, 120):
            high = total - low - middle
            if high <= middle or high >= 120:
                continue
            if low * low + middle * middle + high * high == square:
                answers += [(low, middle, high)]
    assert answers == [values]


def test_withdrawing_the_level_rule_publishes_a_solvable_pool(
    tmp_path: pathlib.Path, monkeypatch: object
) -> None:
    """THE MUTATION CHECK for finding 4, run in place.

    With the count put back to the three this landing first shipped,
    the description publishes mean 46.0 over thirty cells of three
    levels -- the block the sweep above solves outright.
    """
    monkeypatch.setattr(  # type: ignore[attr-defined]
        taxonomy, "_POOLED_SCALE_LEVELS", 3
    )
    first, _second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "three", _three_levels_of_whole_numbers(), FLOOR
    )
    assert (twin_exit, real_exit) == (0, 0)
    scale = first["suppressed_numbers"]
    assert scale["n_cells"] == 30
    assert scale["mean"] == statistics.fmean([44.0, 45.0, 62.0])


def test_the_landings_own_reproduction_is_named_by_its_own_block(
    tmp_path: pathlib.Path,
) -> None:
    """Finding 5, which this pass found and the review did not.

    The shape ledger K-2B-50 names -- 100 `alpha`, twenty `100` and ten
    each of 200 to 209 at a floor of eleven -- published a mean of 204.5
    and a population spread of 2.8722813232690143. That spread is
    EXACTLY the smallest a pool of ten distinct whole numbers can have,
    `sqrt((10 * 10 - 1) / 12)`, so the ten values are forced to be ten
    consecutive whole numbers and the mean says which ten: 200 to 209,
    every one of them, by arithmetic from the block written to protect
    them. No count of levels closes that, which is why
    `_POOLED_SCALE_LEVELS` alone was not the answer and
    `_POOLED_SCALE_LOOSENESS` is asked beside it. The reproduction is
    refused, and ledger K-2B-50 is OPEN again because of it.
    """
    pooled = [float(value) for value in range(200, 210) for _each in range(10)]
    middle, spread = taxonomy.population_moments_of(pooled)
    assert (middle, spread) == (204.5, math.sqrt(99.0 / 12.0))
    assert taxonomy._tightest_variance([10] * 10, 1.0) == 99.0 / 12.0
    assert spread * spread == taxonomy._tightest_variance([10] * 10, 1.0)
    # AND THE PRODUCER REFUSES IT, which is what the arithmetic above
    # asks of it.
    first, _second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "anchored", _anchored_cells(), FLOOR
    )
    assert (twin_exit, real_exit) == (0, 0)
    assert first["suppressed_levels"] == 10
    assert first["suppressed_numbers"] == _SILENT


def test_a_pool_loose_enough_to_hide_its_values_still_publishes(
    tmp_path: pathlib.Path,
) -> None:
    """The refusals are a gate and not a withdrawal.

    Six held-back levels whose values are spaced unevenly -- the closest
    two one apart, the rest far wider -- stand well clear of the
    tightest arrangement their own grid allows, so the pair does not
    name them and the block speaks.
    """
    cells = ["pending"] * 250 + ["500"] * 30
    for value in (301, 302, 420, 560, 705, 860):
        cells += [str(value)] * 6
    first, _second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "loose", cells, FLOOR
    )
    assert (twin_exit, real_exit) == (0, 0)
    assert first["suppressed_levels"] == 6
    scale = first["suppressed_numbers"]
    assert scale["n_cells"] == 36
    assert scale["mean"] is not None and scale["spread"] is not None


def test_withdrawing_the_looseness_rule_names_the_reproduction(
    tmp_path: pathlib.Path, monkeypatch: object
) -> None:
    """THE MUTATION CHECK for finding 5, run in place.

    With the looseness asked of a pool put back to one -- which is the
    state before this pass, where the rule does not exist -- the
    reproduction publishes 204.5 and 2.8722813232690143 again, and the
    test above shows what that pair comes back to.
    """
    monkeypatch.setattr(  # type: ignore[attr-defined]
        taxonomy, "_POOLED_SCALE_LOOSENESS", 1.0
    )
    first, _second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "anchored", _anchored_cells(), FLOOR
    )
    assert (twin_exit, real_exit) == (0, 0)
    scale = first["suppressed_numbers"]
    assert scale["n_cells"] == 100
    assert scale["mean"] == 204.5
    assert scale["spread"] == math.sqrt(99.0 / 12.0)


def test_the_refusals_reach_one_state_a_reader_cannot_tell_apart(
    tmp_path: pathlib.Path,
) -> None:
    """Every refusal this pass adds lands in the state that says nothing.

    A refusal a reader could tell from silence would itself say that the
    held-back levels hold numbers, and something about them, which is
    what the floor exists to withhold. All three shapes here, and a
    column whose held-back levels hold no number at all, publish the
    same three values.
    """
    words = ["alpha"] * 100 + ["beta"] * 3 + ["gamma"] * 3 + ["delta"] * 3
    for name, cells in (
        ("wide", _wider_than_the_column_shows()),
        ("flat", _one_value_spelled_six_ways()),
        ("three", _three_levels_of_whole_numbers()),
        ("words", words),
    ):
        first, _second, _written, twin_exit, real_exit = _round_trip(
            tmp_path / name, cells, FLOOR
        )
        assert (twin_exit, real_exit) == (0, 0), name
        assert first["suppressed_numbers"] == _SILENT, name


def test_a_description_carrying_a_flat_pool_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    """The loader's half of finding 2, asked of a hand-edited document.

    The producer will not write a pool of no spread; invariant B4d is
    what stops a description that was not written by it from carrying
    one. The battery of `tests/test_contract_loader.py` holds the entry;
    this states the sentence a reader of the refusal sees.
    """
    assert "above nought" in contract.INVARIANTS["B4d"]
    assert "value of every cell" in contract.INVARIANTS["B4d"]
