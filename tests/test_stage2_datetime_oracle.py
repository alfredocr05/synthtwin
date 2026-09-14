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
) -> contract.DatetimeFacts:
    """Datetime facts carrying only what these two rules read."""
    return contract.DatetimeFacts(
        parser_family="iso-datetime",
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


def _census(draw: random.Random) -> "tuple[dict[str, int], int]":
    census: dict[str, int] = {}
    for name in NAMES:
        if draw.random() < 0.65:
            census[name] = draw.randint(1, 40)
    if draw.random() < 0.3:
        census["(withheld)"] = draw.randint(1, 12)
    total = sum(census.values())
    # Some columns carry more parsed ranks than the census counts, as a
    # joint ISO column's whole dates do.
    extra = draw.randint(1, 15) if draw.random() < 0.3 else 0
    return census, total + extra


def test_the_rotation_of_marks_agrees_with_the_oracle() -> None:
    """Every rank gets the same mark from both writings, over 6,000 censuses."""
    oracle = _oracle()
    column = types.SimpleNamespace(name="seen_at")
    draw = random.Random(39)
    compared = 0
    for _trial in range(6000):
        census, parsed = _census(draw)
        mine, _notes = generation._separator_allocation(
            typing.cast(contract.ColumnBlock, column), _facts(census), parsed
        )
        theirs = oracle["_separator_allocation"](
            {"resolution": "datetime", "datetime_separators": census}, parsed
        )
        assert mine == theirs, (census, parsed)
        compared += 1
    assert compared == 6000


def test_each_named_mark_is_written_its_published_number_of_times() -> None:
    """Exact counts, the withheld pool on the commonest, and no clustering."""
    column = typing.cast(contract.ColumnBlock, types.SimpleNamespace(name="c"))
    census = {"lower_t": 11, "space": 11, "(withheld)": 2}
    marks, notes = generation._separator_allocation(column, _facts(census), 24)
    # A tie between two names goes to the earliest in sorted order, and
    # the withheld pool is written with it.
    assert marks.count("t") == 13 and marks.count(" ") == 11
    assert [note.fact for note in notes] == ["datetime_separators"]
    # Spread, not spent from the first rank: neither half of the ranks
    # holds all of one mark.
    assert 0 < marks[:12].count("t") < 13
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
        column = {"resolution": "datetime", "all_at_midnight": midnight}
        assert generation._ordinal_space(facts) == oracle["ordinal_space"](
            column
        )
    assert generation._ordinal_space(_facts({}, True)) == "date"


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
        holes = tuple(sorted(set(draw.sample(pool, draw.randint(0, 6)))))
        mine = [generation._kept_datetime_cell(cell, holes) for cell in cells]
        mine, _notes = generation._rebalanced_marks(column, wanted, mine, holes)
        theirs = [oracle["kept_cell"](cell, set(holes)) for cell in cells]
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
    kept = [generation._kept_datetime_cell(cell, holes) for cell in cells]
    assert kept[0][10] == "T"
    fixed, notes = generation._rebalanced_marks(column, wanted, kept, holes)
    assert sorted(cell[10] for cell in fixed) == sorted(wanted)
    assert notes == []
    assert holes[0] not in fixed
    # Every rank allocated a T is itself an absent spelling once spaced,
    # so nothing can take the owed space: the shortfall is named.
    blocked = holes + tuple(f"{cell[0:10]} {cell[11:]}" for cell in cells)
    kept = [generation._kept_datetime_cell(cell, blocked) for cell in cells]
    fixed, notes = generation._rebalanced_marks(column, wanted, kept, blocked)
    assert [note.fact for note in notes] == ["datetime_separators"]
