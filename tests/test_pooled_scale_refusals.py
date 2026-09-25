"""What the pool's published mean must NOT say (plan P4-D302).

THE LANDING THIS REWRITES is plan P4-D301, which published a cell
count, a mean and a POPULATION SPREAD over a column's held-back numbers
and guarded them with four producer refusals. The owner's decision of
2026-09-21 withdrew the spread, and a mean alone is a different
arithmetic, so the four refusals were re-measured one at a time rather
than carried over. NONE OF THE FOUR SURVIVES AS ITSELF, and one rule
replaces all four: `taxonomy._arrangements` counts how many populations
fit everything the description says about the pool, and
`taxonomy._POOLED_SCALE_ROOM` is the bound.

THE FOUR, AND WHAT BECAME OF EACH.

1. A LEVEL COUNT OF SIX. The count asked how many unknowns stood
   against two equations. With one equation the answer is different at
   every level count, and it is counted rather than assumed: a pool of
   ONE different number has exactly one arrangement and is refused, and
   the rest are decided by room and not by counting levels.
2. A SPREAD ABOVE NOUGHT. No spread is published, so there is nothing
   to ask. Its reason -- one value in every cell means the mean IS that
   value -- is the one-arrangement case of the rule above.
3. THE POOL NOT STANDING AT THE TIGHTEST ARRANGEMENT ITS VALUES COULD
   TAKE. Withdrawn, with the number that withdrew it: the owner's own
   shape, which the published spread named outright, has
   429,466,368,887,745,697 arrangements under its mean alone, and over
   twenty-five random pools at each level count a pool drawn AT the
   tightest arrangement leaves a median of 189, 45,757 and 6,318,400
   answers at two, three and four levels against a loose pool's 224,
   47,502 and 4,219,740.
4. THE POOL FITTING INSIDE THE WIDTH THE COLUMN SHOWS. Withdrawn, and
   this one by proof rather than by measurement: the obligation a
   description now states is the MEAN, every arrangement stands on the
   grid inside that width, so a mean beyond it has no arrangement at
   all and the room rule answers nought. What the width rule still
   refused was a pool holding one wide value beside small ones, whose
   mean a twin writes exactly. Measured over 200,000 random pools at
   four widths: not one had a mean the twin could not write and room
   enough to publish, while 2,915 were refused with a mean it could.

Every table is built by seeded neutral code at runtime (plan D13).
"""

import functools
import itertools
import json
import pathlib

from synthtwin import contract, summary, taxonomy
from tests.test_pooled_number_scale import (
    FLOOR,
    _anchored_cells,
    _loaded,
    _missed,
)
from tests.test_stage2_round_trip import _round_trip

_SILENT = {"n_cells": 0, "mean": None}


def _wider_than_the_column_shows() -> "list[str]":
    """The width reproduction: a pool seven figures wide beside a `7`.

    Six held-back numeric levels, unevenly spaced, so that the room rule
    does not refuse this shape and the width rule is measured on its own.
    """
    cells = ["hold"] * 300 + ["7"] * 20
    for value in (1000000, 1000001, 2400000, 3900000, 5100000, 6800000):
        cells += [str(value)] * 4
    return cells


def _one_value_spelled_six_ways() -> "list[str]":
    """The flat reproduction: six levels and one number, five.

    The published `3` is one figure wide like the five, so the width
    rule is not what refuses this shape.
    """
    cells = ["blank"] * 200 + ["3"] * 40
    for spelling in ("5", "5.0", "05", "5.00", "5.000", "05.0"):
        cells += [spelling] * 8
    return cells


def _six_one_figure_numbers() -> "list[str]":
    """The room reproduction: six of the ten one-figure numbers there are.

    Six held-back numeric levels, so the withdrawn level rule of six
    would have published it; a spread well above nought, so the
    withdrawn flat rule would have; and values spaced 1, 2, 1, 2, 2
    apart, so the withdrawn looseness rule would have too. Its mean
    leaves sixteen arrangements.
    """
    cells = ["hold"] * 200 + ["3"] * 40
    for value in (1, 2, 4, 5, 7, 9):
        cells += [str(value)] * 8
    return cells


def test_the_arrangement_count_is_the_count_and_not_an_estimate() -> None:
    """The one rule this landing rests on, checked against brute force.

    `taxonomy._arrangements` answers a Gaussian binomial coefficient
    rather than walking the sets themselves, and a closed form that is
    subtly wrong would be a rule that refuses the wrong pools in both
    directions. So it is asked of every case small enough to enumerate:
    every sum reachable by `k` different places out of `n`, at four
    range sizes and six level counts, counted by walking every subset.

    AND THE UNBOUNDED BRANCH TOO, which a column publishing no number
    reaches: no width then holds the values, so the count is the number
    of ways to split the room into at most `k` parts of any size, and
    that is checked against a plain recursion on partitions.
    """
    checked = 0
    for points in (6, 9, 12, 15):
        for levels in range(1, min(6, points) + 1):
            smallest = levels * (levels - 1) // 2
            for total in range(smallest, levels * (points - 1) - smallest + 1):
                want = sum(
                    1
                    for chosen in itertools.combinations(range(points), levels)
                    if sum(chosen) == total
                )
                assert taxonomy._arrangements(
                    levels, points, total - smallest, True
                ) == want, (points, levels, total)
                checked += 1
    assert checked == 542

    @functools.lru_cache(None)
    def partitions(owed: int, parts: int) -> int:
        if owed == 0:
            return 1
        if parts == 0:
            return 0
        if owed < parts:
            return partitions(owed, parts - 1)
        return partitions(owed - parts, parts) + partitions(owed, parts - 1)

    for levels in range(1, 7):
        for owed in range(0, 60):
            assert taxonomy._arrangements(levels, 0, owed, False) == (
                partitions(owed, levels)
            ), (levels, owed)


def test_a_pool_whose_mean_no_twin_could_write_is_not_published(
    tmp_path: pathlib.Path,
) -> None:
    """The width reason, now answered by the room rule.

    The column publishes one number, `7`, so a made-up number of this
    column has one figure before the mark and no more. Its held-back
    numbers have seven, and so does their mean. There is no arrangement
    of six different one-figure numbers whose mean is above three
    million, so the count is nought and the block says nothing.
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
    # AND THE COUNT IS THE REASON, stated as arithmetic: six different
    # places out of the ten `7` allows cannot add up to what a mean
    # above three million asks for.
    assert taxonomy._arrangements(6, 10, 4000000, True) == 0


def test_a_wide_value_beside_small_ones_is_published_now(
    tmp_path: pathlib.Path,
) -> None:
    """What withdrawing the width rule bought, measured on one shape.

    Eight held-back levels of five rows: seven two-figure numbers and
    one of three. The old width rule refused the whole block because of
    the one wide value; the mean it would have published, 73.875, is
    one a conforming twin writes exactly, and the twin does.
    """
    cells = ["hold"] * 300 + ["70"] * 20
    for value in (10, 11, 12, 13, 14, 15, 16, 500):
        cells += [str(value)] * 5
    first, _second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "onewide", cells, FLOOR
    )
    assert (twin_exit, real_exit) == (0, 0)
    scale = first["suppressed_numbers"]
    assert scale["n_cells"] == 40
    assert scale["mean"] == 73.875


def test_a_pool_of_one_value_spelled_several_ways_is_not_published(
    tmp_path: pathlib.Path,
) -> None:
    """Refusal 2: one different number has one arrangement.

    Six spellings of five are six levels the floor holds back and one
    value, so a mean of 5.0 names what all forty-eight of those cells
    held. The block says nothing instead, and the page a person reads
    carries no line about them.
    """
    cells = _one_value_spelled_six_ways()
    folder = tmp_path / "flat"
    first, second, _written, twin_exit, real_exit = _round_trip(
        folder, cells, FLOOR
    )
    assert (twin_exit, real_exit) == (0, 0)
    assert first["suppressed_numbers"] == _SILENT
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
    assert "average 5.0" not in page
    assert "the ones that were numbers" not in page


def test_a_pool_with_no_room_to_move_is_not_published(
    tmp_path: pathlib.Path,
) -> None:
    """Refusal 3, and the shape every OLD rule published.

    Six different one-figure numbers beside a published one-figure
    number. The old level rule asked for six and got six; the old flat
    rule asked for a spread above nought and got 2.75; the old looseness
    rule asked for two and a half times the tightest variance and got
    past it. The room rule counts the arrangements its own mean would
    leave -- sixteen, over the ten one-figure numbers the width allows
    -- and refuses.
    """
    cells = _six_one_figure_numbers()
    first, _second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "narrow", cells, FLOOR
    )
    assert (twin_exit, real_exit) == (0, 0)
    assert first["suppressed_levels"] == 6
    assert first["suppressed_rows"] == 48
    assert first["suppressed_numbers"] == _SILENT
    # THE COUNT THIS RESTS ON, stated as arithmetic rather than as a
    # verdict: six different places out of the ten `3` allows, whose sum
    # is the pool's own.
    assert taxonomy._arrangements(6, 10, 28 - 15, True) == 16
    assert 16 < taxonomy._POOLED_SCALE_ROOM


def test_withdrawing_the_room_rule_publishes_a_pool_it_names(
    tmp_path: pathlib.Path, monkeypatch: object
) -> None:
    """THE MUTATION CHECK for refusal 3, run in place.

    With the bound at nought the room rule refuses nothing, and the
    block publishes forty-eight cells at a mean of 4.666666666666667 --
    which, with the six levels and the forty-eight rows the floor
    already publishes and the one figure `3` allows, leaves sixteen
    populations and no more.
    """
    monkeypatch.setattr(  # type: ignore[attr-defined]
        taxonomy, "_POOLED_SCALE_ROOM", 0
    )
    first, _second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "narrow", _six_one_figure_numbers(), FLOOR
    )
    assert (twin_exit, real_exit) == (0, 0)
    scale = first["suppressed_numbers"]
    assert scale["n_cells"] == 48
    assert scale["mean"] == 4.666666666666667


def test_the_tightest_arrangement_is_published_and_the_count_says_why(
    tmp_path: pathlib.Path,
) -> None:
    """Refusal 4 WITHDRAWN, with the number that withdrew it.

    The owner's own shape is ten consecutive whole numbers -- the
    tightest arrangement ten distinct whole numbers can take, and the
    one the published SPREAD named outright, because its spread was
    exactly the smallest such a pool can have. Under a mean alone it is
    not named at all: over the thousand places the column's own
    three-figure width allows, 429,466,368,887,745,697 sets of ten
    different whole numbers share that mean.
    """
    first, _second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "anchored", _anchored_cells(), FLOOR
    )
    assert (twin_exit, real_exit) == (0, 0)
    assert first["suppressed_numbers"]["n_cells"] == 100
    assert first["suppressed_numbers"]["mean"] == 204.5
    # The producer's own walk stops at `_POOLED_SCALE_COUNTED` steps of
    # room, so what it answers is a floor and not the total: the whole
    # count, walked to the end, is 429,466,368,887,745,697.
    assert taxonomy._arrangements(10, 1000, 2045 - 45, True) == 8855101766
    assert taxonomy._arrangements(
        10, 1000, 2045 - 45, True
    ) > taxonomy._POOLED_SCALE_ROOM


def test_the_refusals_reach_one_state_a_reader_cannot_tell_apart(
    tmp_path: pathlib.Path,
) -> None:
    """Every refusal, and a column with no held-back number, agree.

    A refusal a reader could tell apart from nought would itself
    publish that the pool holds numbers and how few of them, which is
    the count the floor exists to withhold.
    """
    shapes = {
        "wide": _wider_than_the_column_shows(),
        "flat": _one_value_spelled_six_ways(),
        "narrow": _six_one_figure_numbers(),
        "wordy": ["alpha"] * 200 + ["beta"] * 3 + ["gamma"] * 3,
    }
    for name in sorted(shapes):
        first, _second, _written, twin_exit, real_exit = _round_trip(
            tmp_path / name, shapes[name], FLOOR
        )
        assert (twin_exit, real_exit) == (0, 0), name
        assert first["suppressed_numbers"] == _SILENT, name


def test_the_loader_cannot_re_ask_what_no_published_fact_carries() -> None:
    """WHAT B4d NO LONGER RE-ASKS, said plainly because it is a loss.

    While a spread was published, invariant B4d re-asked that it stood
    above nought, so a HAND-WRITTEN description could not carry a pool
    of one value. No spread is published now, so there is nothing for
    the loader to re-ask: the block below is one the producer would
    never write -- forty-eight cells at one value's own mean -- and the
    loader takes it. The producer's own refusal is the only guard, and
    `test_a_pool_of_one_value_spelled_several_ways_is_not_published` is
    what holds it.

    The same is true of the width rule and the room rule, and contract
    6.3.3 gives one reason for all three: what the loader would need to
    re-ask them is more numbers about the pool than the pool publishes.
    """
    got = contract._pooled_numbers(
        {"suppressed_numbers": {"n_cells": 48, "mean": 5.0}, "n_numeric": 88},
        "column 'value'",
        11,
    )
    assert got.n_cells == 48
    assert got.mean == 5.0


def test_what_b4d_still_re_asks_is_the_disclosure_rule() -> None:
    """A pool of one cell would BE that cell's value under the name `mean`.

    And a pool leaving one published numeric cell behind hands that cell
    over by subtraction. Both are refused wherever the block is read,
    which is the half of contract 6.3.3 the loader does keep.
    """
    for cells, numeric, why in (
        (1, 88, "a pool of one cell"),
        (87, 88, "a pool leaving one numeric cell behind"),
        (89, 88, "a pool of more cells than the column counts numbers"),
    ):
        try:
            contract._pooled_numbers(
                {
                    "suppressed_numbers": {"n_cells": cells, "mean": 5.0},
                    "n_numeric": numeric,
                },
                "column 'value'",
                11,
            )
        except Exception as refusal:  # noqa: BLE001 - the message is the point
            assert "B4d" in str(refusal), why
        else:  # pragma: no cover - a passing load is the defect
            raise AssertionError(why)
    # AND SILENCE IS TOTAL: a mean written over no cells at all is
    # refused too, because a block that spoke one without the other
    # would say by its shape what the count is for.
    try:
        contract._pooled_numbers(
            {"suppressed_numbers": {"n_cells": 0, "mean": 5.0}},
            "column 'value'",
            11,
        )
    except Exception as refusal:  # noqa: BLE001 - the message is the point
        assert "B4d" in str(refusal)
    else:  # pragma: no cover - a passing load is the defect
        raise AssertionError("a mean over no cells was accepted")


def test_the_real_table_is_never_missed_on_any_refused_shape(
    tmp_path: pathlib.Path,
) -> None:
    """Whatever the block says, the table it was written from meets it."""
    shapes = {
        "wide": _wider_than_the_column_shows(),
        "flat": _one_value_spelled_six_ways(),
        "narrow": _six_one_figure_numbers(),
        "anchored": _anchored_cells(),
    }
    for name in sorted(shapes):
        folder = tmp_path / name
        _round_trip(folder, shapes[name], FLOOR)
        assert _missed(_loaded(folder), folder / "same.csv", shapes[name]) == []
