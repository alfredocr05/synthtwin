"""Stage 2, part two: the generator and the independent oracle agree on moments.

Plan P4-D39 moved two generator rules. A cell of a column of moments now
wears the mark between its day and its clock that the column's census
gives its rank, and a column whose every moment stands at midnight is
counted in whole days and written back with a midnight clock. Rule
amendment A-P4-59 is why this file exists: any generator rule that moves
is mirrored in the independent oracle
(`tools/reference/make_generation_reference_vectors.py`, which imports
nothing it checks) in the same commit, and the two are held to agreeing
here over many more shapes than the two frozen cases can.

The two frozen cases, `midnight_days` and `mixed_marks`, pin the bytes;
this file pins the RULES across the space those two cases sample once.
"""

import pathlib
import random
import runpy
import types
import typing

from synthtwin import contract, generation, validation

ORACLE = (
    pathlib.Path(__file__).resolve().parent.parent
    / "tools"
    / "reference"
    / "make_generation_reference_vectors.py"
)
NAMES = ("lower_t", "space", "upper_t")


def _oracle() -> "dict[str, typing.Any]":
    return runpy.run_path(str(ORACLE))


def _facts(
    census: "dict[str, int]",
    midnight: bool = False,
    precision: str = "second",
    digits: int = 0,
    family: str = "iso-datetime",
) -> contract.DatetimeFacts:
    """Datetime facts carrying only what these two rules read."""
    return contract.DatetimeFacts(
        parser_family=family,
        resolution="datetime",
        time_precision=precision,
        subsecond_digits=digits,
        datetimes_read_at="local",
        earliest="",
        latest="",
        earliest_utc_offset="(none)",
        latest_utc_offset="(none)",
        date_percentiles=typing.cast(contract.DateLadder, None),
        n_unparsed=0,
        utc_offsets={},
        resolution_mix={},
        datetime_separators=census,
        all_at_midnight=midnight,
    )


SLASHED = ("month-first-datetime", "day-first-datetime", "slashed-iso-datetime")


def _census(draw: random.Random) -> "tuple[dict[str, int], int, str]":
    if draw.random() < 0.2:
        # A slashed stamp: its reader takes a space and nothing else, so
        # its census is a space count, a pool, or both (contract D13).
        # A space count or a pool, never both: since plan P4-D220 a pool
        # of marks is the whole census (contract D12).
        family = draw.choice(SLASHED)
        census: dict[str, int] = {}
        if draw.random() < 0.5:
            census["space"] = draw.randint(1, 40)
        else:
            census["(withheld)"] = draw.randint(1, 12)
        return census, sum(census.values()), family
    census = {}
    # A pool only where no mark is named, which is the only census the
    # contract's D12 admits with one since plan P4-D220; its sizes reach
    # one and two, where the pool has fewer values than rarer marks.
    if draw.random() < 0.3:
        census["(withheld)"] = draw.choice((1, 2, 3, draw.randint(1, 900)))
    else:
        for name in NAMES:
            if draw.random() < 0.65:
                census[name] = draw.randint(1, 40)
    total = sum(census.values())
    # Some columns carry more parsed ranks than the census counts, as a
    # joint ISO column's whole dates do.
    extra = draw.randint(1, 15) if draw.random() < 0.3 else 0
    return census, max(1, total + extra), draw.choice(("iso-datetime", "iso-mixed"))


def test_the_rotation_of_marks_agrees_with_the_oracle() -> None:
    """Every rank gets the same mark from both writings, over 6,000 censuses."""
    oracle = _oracle()
    column = types.SimpleNamespace(name="seen_at")
    draw = random.Random(39)
    compared = 0
    pooled = 0
    for _trial in range(6000):
        census, parsed, family = _census(draw)
        facts = _facts(census, family=family)
        mine, _notes = generation._separator_allocation(
            typing.cast(contract.ColumnBlock, column), facts, parsed
        )
        theirs = oracle["_separator_allocation"](
            {"resolution": "datetime", "format": family, "datetime_separators": census},
            parsed,
        )
        assert mine == theirs, (census, parsed, family)
        # ...and the marks the absent-spelling exception offers are the
        # marks the allocation writes, in both writings.
        assert generation._offered_marks(facts) == tuple(
            sorted(oracle["mark_weights"]({"format": family, "datetime_separators": census}))
        ), (census, family)
        if "(withheld)" in census:
            pooled += 1
        compared += 1
    assert compared == 6000
    assert pooled > 1000, pooled


def test_each_named_mark_is_written_its_published_number_of_times() -> None:
    """Exact counts, the withheld pool on every mark, and no clustering."""
    column = typing.cast(contract.ColumnBlock, types.SimpleNamespace(name="c"))
    census = {"lower_t": 12, "space": 12}
    marks, notes = generation._separator_allocation(column, _facts(census), 24)
    # Each named mark exactly its count.
    assert (marks.count("t"), marks.count(" "), marks.count("T")) == (12, 12, 0)
    assert notes == []
    # Spread, not spent from the first rank: neither half of the ranks
    # holds all of one mark.
    assert 0 < marks[:12].count("t") < 12
    # The withheld pool, which since plan P4-D220 is the whole census, split
    # evenly over the three marks since plan P4-D222 (stage 2 closed by the
    # owner rulings of 2026-09-17): a pool stands only where each third of
    # it is below the line, so the twin described again pools the same.
    pooled, notes = generation._separator_allocation(
        column, _facts({"(withheld)": 24}), 24
    )
    assert (pooled.count("t"), pooled.count(" "), pooled.count("T")) == (8, 8, 8)
    assert notes == []
    wide = {"space": 300, "upper_t": 50, "lower_t": 50}
    spread, _ = generation._separator_allocation(column, _facts(wide), 400)
    for part in range(4):
        quarter = spread[part * 100 : (part + 1) * 100]
        assert quarter.count(" ") == 75, (part, quarter.count(" "))


def test_a_cell_is_written_the_same_way_by_both() -> None:
    """Every precision, every mark, and the midnight form, over 9,000 cells."""
    oracle = _oracle()
    draw = random.Random(40)
    for _trial in range(9000):
        mark = draw.choice(("T", " ", "t"))
        precision = draw.choice(("minute", "second", "subsecond"))
        digits = draw.randint(1, 6) if precision == "subsecond" else 0
        day = draw.randint(-719000, 2900000)
        ordinal = day * 86400 + draw.randint(0, 86399)
        assert generation._cell_of_ordinal(
            ordinal, "datetime", precision, digits, mark
        ) == oracle["precision_form"](
            ordinal, "datetime", precision, digits, mark=mark
        )
        midnight = _facts({"space": 1}, True, precision, digits)
        assert generation._space_cell(day, midnight, mark) == oracle[
            "precision_form"
        ](day * 86400, "datetime", precision, digits, mark=mark)


def test_a_midnight_column_is_counted_in_days_by_both() -> None:
    """The one place each writing decides the space, asked the same question."""
    oracle = _oracle()
    for midnight in (True, False):
        facts = _facts({"space": 12}, midnight)
        column = {
            "resolution": "datetime",
            "all_at_midnight": midnight,
            "datetimes_read_at": "local",
        }
        assert generation._ordinal_space(facts) == oracle["ordinal_space"](
            column
        )
    assert generation._ordinal_space(_facts({}, True)) == "date"
    # ON ITS OWN CLOCK ONLY (landing 2b.3): a column wholly at local
    # values at midnight on the shared clock is counted in seconds by both.
    import dataclasses

    shared = dataclasses.replace(_facts({"upper_t": 12}, True), datetimes_read_at="utc")
    assert generation._ordinal_space(shared) == "datetime"
    assert oracle["ordinal_space"](
        {"resolution": "datetime", "all_at_midnight": True, "datetimes_read_at": "utc"}
    ) == "datetime"


def test_the_generator_and_the_checker_count_a_midnight_column_in_days() -> None:
    """The slack, the step and the reading unit agree, at every precision.

    The critic of this landing measured the failure this pins: a column
    written to the minute whose moments stand at midnight, read in days by
    one module and with a minute's slack by the other, files a faithful
    twin's distinct dates as a miss. Both modules must ask the midnight
    statement BEFORE the precision.
    """
    for precision, digits in (("minute", 0), ("second", 0), ("subsecond", 3)):
        midnight = _facts({"space": 12}, True, precision, digits)
        assert generation._precision_slack(midnight) == 0
        assert validation._space_unit(midnight) == 86400
        assert validation._precision_step(midnight) == 86400
        assert validation._reading_unit(midnight) == 86400
        clocked = _facts({"space": 12}, False, precision, digits)
        assert validation._space_unit(clocked) == 1
        assert generation._precision_slack(clocked) + 1 == (
            validation._reading_unit(clocked)
        )


def test_the_absent_spelling_swap_and_its_repair_agree_with_the_oracle() -> None:
    """The exception of G7.5 and the census repair, both writings, 4,000 columns.

    Review round 1 of this landing found the exception changed a cell's
    mark and left the census one short in one name and one over in
    another, and that the oracle did not model the exception at all.
    """
    oracle = _oracle()
    column = typing.cast(contract.ColumnBlock, types.SimpleNamespace(name="c"))
    draw = random.Random(42)
    for _trial in range(4000):
        parsed = draw.randint(2, 24)
        wanted = [draw.choice(("T", " ", "t")) for _rank in range(parsed)]
        days = sorted(draw.randint(19000, 19012) for _rank in range(parsed))
        cells = [
            generation._cell_of_ordinal(
                day * 86400, "datetime", "second", 0, wanted[rank]
            )
            for rank, day in enumerate(days)
        ]
        pool = list(cells)
        for cell in cells:
            for mark in ("T", " ", "t"):
                pool += [f"{cell[0:10]}{mark}{cell[11:]}"]
        chosen = sorted(set(draw.sample(pool, draw.randint(0, 6))))
        # Some absent spellings are published padded with spaces, which the
        # reading trims (stage 2 closure review item 6).
        holes = tuple(
            f" {hole} " if draw.random() < 0.3 else hole for hole in chosen
        )
        named = tuple(
            sorted(
                draw.sample(["lower_t", "space", "upper_t"], draw.randint(0, 3))
            )
        )
        mine = [
            generation._kept_datetime_cell(cell, holes, named) for cell in cells
        ]
        mine, _notes = generation._rebalanced_marks(column, wanted, mine, holes)
        theirs = [oracle["kept_cell"](cell, set(holes), named) for cell in cells]
        theirs = oracle["rebalance_marks"](wanted, theirs, set(holes))
        assert mine == theirs, (wanted, cells, holes)


def test_a_mark_the_swap_took_is_given_back_or_named() -> None:
    """Restored where another rank can take it; a deviation where none can."""
    column = typing.cast(contract.ColumnBlock, types.SimpleNamespace(name="c"))
    wanted = [" ", "T", " ", "T"]
    cells = [
        generation._cell_of_ordinal(
            (19000 + rank) * 86400, "datetime", "second", 0, wanted[rank]
        )
        for rank in range(4)
    ]
    holes = (cells[0],)
    named = ("space", "upper_t")
    kept = [generation._kept_datetime_cell(cell, holes, named) for cell in cells]
    assert kept[0][10] == "T"
    fixed, notes = generation._rebalanced_marks(column, wanted, kept, holes)
    assert sorted(cell[10] for cell in fixed) == sorted(wanted)
    assert notes == []
    assert holes[0] not in fixed
    # Every rank allocated a T is itself an absent spelling once spaced,
    # so nothing can take the owed space: the shortfall is named.
    blocked = holes + tuple(f"{cell[0:10]} {cell[11:]}" for cell in cells)
    kept = [generation._kept_datetime_cell(cell, blocked, named) for cell in cells]
    fixed, notes = generation._rebalanced_marks(column, wanted, kept, blocked)
    assert [note.fact for note in notes] == ["datetime_separators"]


def test_the_swap_offers_the_census_marks_before_a_mark_nobody_wrote() -> None:
    """A space column that also wrote a `t` steps to the `t`, never to a `T`."""
    cell = generation._cell_of_ordinal(19000 * 86400, "datetime", "second", 0, " ")
    holes = (cell,)
    assert generation._kept_datetime_cell(cell, holes, ("lower_t", "space"))[10] == "t"
    assert generation._kept_datetime_cell(cell, holes, ("space",))[10] == "T"


def test_the_census_repair_takes_a_repeated_spelling_and_stays_linear() -> None:
    """Many moments at midnight on one declared-absent day, restored in linear time."""
    import time

    column = typing.cast(contract.ColumnBlock, types.SimpleNamespace(name="c"))
    parsed = 40000
    wanted = [" " if rank % 4 else "T" for rank in range(parsed)]
    days = [19000 + (rank * 29) // parsed for rank in range(parsed)]
    cells = [
        generation._cell_of_ordinal(day * 86400, "datetime", "second", 0, wanted[rank])
        for rank, day in enumerate(days)
    ]
    holes = (generation._cell_of_ordinal(19014 * 86400, "datetime", "second", 0, " "),)
    named = ("space", "upper_t")
    started = time.perf_counter()
    kept = [generation._kept_datetime_cell(cell, holes, named) for cell in cells]
    fixed, notes = generation._rebalanced_marks(column, wanted, kept, holes)
    spent = time.perf_counter() - started
    assert sorted(cell[10] for cell in fixed) == sorted(wanted)
    assert notes == []
    assert holes[0] not in fixed
    assert spent < 10.0, spent


def test_the_census_repair_never_folds_two_values_into_one() -> None:
    """A last copy is never handed a mark that folds it onto another value."""
    from synthtwin import parsing

    oracle = _oracle()
    column = typing.cast(contract.ColumnBlock, types.SimpleNamespace(name="c"))
    wanted = [" ", "T", "t", " ", "T", " "]
    days = [20089, 20089, 20089, 20090, 20090, 20090]
    cells = [
        generation._cell_of_ordinal(day * 86400, "datetime", "second", 0, wanted[rank])
        for rank, day in enumerate(days)
    ]
    holes = ("2025-01-01t00:00:00",)
    named = ("lower_t", "space", "upper_t")
    kept = [generation._kept_datetime_cell(cell, holes, named) for cell in cells]
    fixed, notes = generation._rebalanced_marks(column, wanted, kept, holes)
    assert len({parsing.folded(cell) for cell in fixed}) == 3, fixed
    assert [note.fact for note in notes] == ["datetime_separators"]
    assert oracle["rebalance_marks"](wanted, kept, set(holes)) == fixed

