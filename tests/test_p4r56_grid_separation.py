"""Residual R-P4-56: two strata are two cells, so they get two spellings.

THE DEFECT, AND WHY IT IS THE ONE THAT MATTERS FOR A CODE COLUMN. A
numeric column with a PINNED fraction width -- a diagnosis code, a
dose, any rounded measurement -- is written on a fixed grid. The ladder
hands the twin different numbers for two neighbouring strata, and where
those two land closer together than the grid's own step they are
written as ONE cell. The column's count of different numbers then comes
out short, and the leading-zero rule of G6.5 supplies the missing
SPELLING the only way it can: by writing one number a second way, with
an extra figure before the point.

So the twin lost two things at once, and the second is the one nobody
was told about. The count of different values is published and the
twin's own report names the miss. The WIDTH is not published for a
plain numeric column, so a cell four figures wide in a column of
three-figure codes is written, shipped, and reported nowhere -- and a
person's analysis code, developed against that twin, meets a shape
their real table never held.

`_apart_enough` moves a stratum whose text another stratum has already
written to the nearest free point of the published width's own grid,
inside its own share of the ladder.
"""

import pathlib
import random
import re

import fixtures
from synthtwin import contract, generation, profile, reading, taxonomy

SEED = 7


def _described(folder: pathlib.Path, rows: "list[str]", stem: str = "code"):
    """One column through the real producer and loader."""
    path = fixtures.write(
        folder, f"{stem}.csv", "code\n" + "\n".join(rows) + "\n"
    )
    table = reading.read_table(
        str(path), first_row=reading.FIRST_ROW_AUTOMATIC
    )
    document = profile.build_document(table, taxonomy.Settings(), [])
    written = fixtures.write_profile(folder, f"{stem}-profile.json", document)
    return document, contract.load_profile(str(written))


# The witness the residual was opened on: 240 cells of `NNN.N`, 99
# different values, integer parts 250 to 348. Two strata land six
# hundredths apart where the real values near there are more than a
# unit apart.
def _code_column() -> "list[str]":
    rows = [f"{250 + step % 99:03d}.{step % 9}" for step in range(240)]
    random.Random(4).shuffle(rows)
    return rows


def test_a_fixed_width_code_column_keeps_its_shape_and_its_count(
    tmp_path: pathlib.Path,
) -> None:
    """Both counts, and every cell the shape the source's cells wore."""
    rows = _code_column()
    document, described = _described(tmp_path, rows)
    published = document["columns"][0]

    twin = generation.generate(described, SEED)
    cells = [cell for cell in twin.columns[0] if cell != ""]
    assert len(cells) == 240

    # EVERY CELL WEARS THE SOURCE'S OWN SHAPE.
    shape = re.compile(r"[0-9]{3}[.][0-9]$")
    off = [cell for cell in cells if not shape.match(cell)]
    assert not off, off[:5]

    # AND THE COUNT OF DIFFERENT NUMBERS IS THE PUBLISHED ONE.
    assert published["n_distinct_values"] == 99
    assert len({float(cell) for cell in cells}) == 99

    # SO THE TWIN FILES NOTHING AGAINST ITSELF.
    assert not twin.deviations, [
        (one.fact, one.published, one.achieved) for one in twin.deviations
    ]


def test_the_grid_walk_is_what_keeps_them_apart(
    tmp_path: pathlib.Path, monkeypatch: "object"
) -> None:
    """The mutant that makes the test above mean something.

    `_apart_enough` reverted to the identity is the twin as the
    residual found it: two strata written as one cell, the count of
    different numbers one short, and the leading-zero rule supplying
    the missing spelling with a figure no source cell had.
    """
    rows = _code_column()
    _document, described = _described(tmp_path, rows)
    monkeypatch.setattr(  # type: ignore[attr-defined]
        generation,
        "_apart_enough",
        lambda column, facts, layout, rungs, values: values,
    )
    cells = [
        cell for cell in generation.generate(described, SEED).columns[0]
        if cell != ""
    ]
    assert len({float(cell) for cell in cells}) == 98
    wide = [cell for cell in cells if len(cell.split(".")[0]) != 3]
    assert wide == ["0250.4"], wide


def test_nothing_published_is_traded_for_the_separation(
    tmp_path: pathlib.Path,
) -> None:
    """The three things the walk may never move.

    The two pinned ends hold the published smallest and largest and are
    EXACT; the zero stratum holds a published count of zeros; and no
    candidate may cross into another sign band, because the counts of
    negative and positive cells are published too.
    """
    rows = (
        [f"-{4 + step % 7}.{step % 9}" for step in range(60)]
        + ["0.0"] * 20
        + [f"{10 + step % 9}.{step % 9}" for step in range(60)]
    )
    random.Random(11).shuffle(rows)
    document, described = _described(tmp_path, rows, stem="signs")
    published = document["columns"][0]
    cells = [
        cell for cell in generation.generate(described, SEED).columns[0]
        if cell != ""
    ]
    numbers = [float(cell) for cell in cells]
    assert sum(1 for one in numbers if one < 0) == published["n_negative"]
    assert sum(1 for one in numbers if one == 0) == published["n_zero"]
    assert min(numbers) == published["percentiles"]["min"]
    assert max(numbers) == published["percentiles"]["max"]


def test_a_whole_number_column_is_on_a_grid_too(
    tmp_path: pathlib.Path,
) -> None:
    """THE INTEGERS ARE A GRID, and this pass declined them until now.

    A whole-number column carries no figure after the point, so its
    `fraction_widths` census is EMPTY -- there is no width to count.
    `_pinned_fraction` read that as "no grid" and answered -1, and the
    pass returned before doing anything. Most of a real table's numeric
    columns hold nothing but whole values -- an age, a count, a dose.

    Measured over twelve seeds, published against held: 300 ages
    between 18 and 89 publishing 70 different numbers held 56 to 66
    with the pass off and 67 to 70 with it on. This test asserts the
    gate itself and one seed's outcome, because the range is a
    measurement and the gate is the rule.
    """
    generator = random.Random(31337)
    rows = [str(generator.randint(18, 89)) for _each in range(300)]
    _document, loaded = _described(tmp_path, rows, "ages")
    column = loaded.columns[0]
    facts = column.facts
    # THE FIXTURE IS THE SHAPE THE RULE IS ABOUT, asserted rather than
    # assumed: an empty census on an integer-valued column.
    assert facts.fraction_widths == {}, facts.fraction_widths
    assert facts.integer_valued is True
    assert generation._pinned_fraction(column, facts) == 0

    published = facts.n_distinct_values
    assert published is not None and published > 60, published
    twin = generation.generate(loaded, SEED)
    cells = [cell for cell in twin.columns[0] if cell != ""]
    held = len({float(cell) for cell in cells})
    # The pass cannot always reach the count -- a tight column's shares
    # hold no free point -- so what is pinned is that it gets CLOSE,
    # where before it lost up to a fifth of the count.
    assert held >= published - 3, (held, published)
    # AND EVERY CELL IS STILL WHOLE, which is the fact the grid is
    # there to keep: a repair that wrote `41.5` would meet the count
    # and change the column's type.
    assert all(float(cell) == int(float(cell)) for cell in cells)
    assert all("." not in cell for cell in cells)


def test_the_integer_grid_is_refused_where_the_column_is_not_whole(
    tmp_path: pathlib.Path,
) -> None:
    """An empty census alone is NOT the integer grid.

    `integer_valued` is what says the column is on it. A column whose
    census is empty because its widths were all withheld under the
    floor is not whole-valued, and answering 0 there would move a
    decimal value onto an integer and change what the column holds.
    """
    generator = random.Random(99)
    rows = [f"{generator.uniform(1, 50):.{generator.choice((1, 2, 3))}f}"
            for _each in range(200)]
    _document, loaded = _described(tmp_path, rows, "ragged")
    column = loaded.columns[0]
    facts = column.facts
    assert facts.integer_valued is False, facts.integer_valued
    assert generation._pinned_fraction(column, facts) == -1


def test_a_column_of_several_widths_is_left_alone(
    tmp_path: pathlib.Path,
) -> None:
    """The rule acts only where ONE width covers every cell.

    Where the census names several, which cell is written at which is
    settled after the styles are, so a value cannot know here what grid
    it will land on. `_pinned_fraction` says so with -1, and R-P4-56
    stays open for those columns rather than being closed by a rule
    that guesses.
    """
    rows = (
        [f"{10 + step}.{step % 9}" for step in range(40)]
        + [f"{60 + step}.{step % 9}{step % 7}" for step in range(40)]
    )
    document, described = _described(tmp_path, rows, stem="mixed")
    facts = described.columns[0].facts
    assert isinstance(facts, contract.NumericFacts)
    assert len(facts.fraction_widths) > 1, facts.fraction_widths
    assert generation._pinned_fraction(described.columns[0], facts) == -1


# ---------------------------------------------------------------------
# The first adversarial round on this repair (P4-R56-R1). Four items,
# all real, and one of them was a CRASH -- which is what a rule reading
# a census key as a number does when the census pools its keys.


def test_a_pooled_width_census_is_not_read_as_a_width(
    tmp_path: pathlib.Path,
) -> None:
    """`(withheld)` is a word, not a number (item P4-R56-R1-F2).

    A census whose every width is used by fewer cells than the
    publication floor names none of them: it publishes one withheld
    total instead, under this package's own word. Reading that word as
    a number raised `ValueError` out of `synthtwin generate` -- a crash,
    on a description the loader accepts. 110 decimal cells spread over
    eleven widths at floor 11 is such a column.
    """
    rows = []
    for width in range(1, 12):
        for step in range(10):
            rows.append(("%." + str(width) + "f") % (10 + step + width / 100.0))
    path = fixtures.write(tmp_path, "pooled.csv", "v\n" + "\n".join(rows) + "\n")
    table = reading.read_table(
        str(path), first_row=reading.FIRST_ROW_AUTOMATIC
    )
    document = profile.build_document(
        table, taxonomy.Settings(small_cell_floor=11), []
    )
    assert document["columns"][0]["fraction_widths"] == {"(withheld)": 110}
    described = contract.load_profile(
        str(fixtures.write_profile(tmp_path, "pooled-p.json", document))
    )
    facts = described.columns[0].facts
    assert isinstance(facts, contract.NumericFacts)
    assert generation._pinned_fraction(described.columns[0], facts) == -1

    twin = generation.generate(described, SEED)
    assert len([cell for cell in twin.columns[0] if cell != ""]) == 110


def test_the_anchor_is_what_the_writer_will_write(
) -> None:
    """Not a second rounding of the same value (item P4-R56-R1-F4).

    The walk anchored with `_whole_valued`, which takes a tie upward,
    while the writer's `_at_width` takes the tie the format takes. On
    1.25 at one figure the two part company: the walk anchored on 1.3,
    stepped to 1.2 and 1.4, and never tried 1.3 -- the free point the
    rule asks for. Reading the anchor off the writer's own text cannot
    disagree with the writer.
    """
    assert generation._grid_text(1.25, 1) == "1.2"
    assert generation._whole_valued(1.25 / 0.1) * 0.1 != 1.2

    written = {"1.2": 0}
    got = generation._apart_inside(
        1.25, 1, generation._BAND_POSITIVE, (1.2, 1.35), (0.0, 9.9), written
    )
    assert got == 1.3, got


def test_the_pinned_ends_claim_their_text_before_anything_moves(
    tmp_path: pathlib.Path,
) -> None:
    """The maximum is one this rule may never move (item P4-R56-R1-F3).

    The walk ran forward and let whichever stratum reached a text first
    keep it, so an interior stratum could take the text the published
    MAXIMUM needs -- and the maximum, reached later, cannot give way.
    The collision then stood and the spelling repair wrote the extra
    figure this residual exists to stop.
    """
    rows = [f"{4 + step % 6}.{step % 9}" for step in range(80)] + ["9.9"] * 8
    random.Random(2).shuffle(rows)
    document, described = _described(tmp_path, rows, stem="ends")
    published = document["columns"][0]
    cells = [
        cell for cell in generation.generate(described, SEED).columns[0]
        if cell != ""
    ]
    numbers = [float(cell) for cell in cells]
    assert max(numbers) == published["percentiles"]["max"]
    assert min(numbers) == published["percentiles"]["min"]
    widest = max(len(row.split(".")[0]) for row in rows)
    assert not [
        cell for cell in cells if len(cell.split(".")[0].lstrip("-")) > widest
    ]


def test_the_published_count_is_a_ceiling_not_a_floor(
    tmp_path: pathlib.Path,
) -> None:
    """Separating past the published count is a miss too (F1).

    A collision is a defect only while the twin holds FEWER different
    numbers than the description publishes. Where a source number was
    written two ways its two strata are meant to come out as one
    number, and separating them would carry the count past the
    published one -- a miss in the other direction, made by the repair
    for the first.
    """
    rows = [f"{10 + step % 30}.{step % 9}" for step in range(120)]
    random.Random(6).shuffle(rows)
    document, described = _described(tmp_path, rows, stem="ceiling")
    facts = described.columns[0].facts
    assert isinstance(facts, contract.NumericFacts)
    wanted = facts.n_distinct_values
    assert wanted is not None

    cells = [
        cell for cell in generation.generate(described, SEED).columns[0]
        if cell != ""
    ]
    assert len({float(cell) for cell in cells}) <= wanted


def test_the_ceiling_counts_the_whole_column_and_not_the_walk(
    tmp_path: pathlib.Path,
) -> None:
    """Four spellings of three numbers stay three numbers (P4-R56-R2-F2).

    The ceiling counted only the texts the walk had reached -- the two
    ends, the zero stratum, and whatever prefix it had passed -- and
    compared that against the published count of different numbers. A
    column whose LATER strata hold values the prefix had not reached
    was separated past its own ceiling.

    Thirty cells each of `+1.0`, `1.0`, `2.0` and `3.0` publish four
    different SPELLINGS and three different NUMBERS. Separating the
    `+1.0` and `1.0` strata makes four numbers and a miss where there
    was none.
    """
    rows = ["+1.0"] * 30 + ["1.0"] * 30 + ["2.0"] * 30 + ["3.0"] * 30
    document, described = _described(tmp_path, rows, stem="plus")
    block = document["columns"][0]
    assert block["n_distinct"] == 4
    assert block["n_distinct_values"] == 3

    for seed in (0, 5, 7):
        twin = generation.generate(described, seed)
        cells = [cell for cell in twin.columns[0] if cell != ""]
        assert len({float(cell) for cell in cells}) == 3, seed
        assert not twin.deviations, [
            (one.fact, one.published, one.achieved) for one in twin.deviations
        ]
