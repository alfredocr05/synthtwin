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

import importlib.util
import pathlib
import random
import re

import fixtures
from synthtwin import contract, generation, profile, reading, taxonomy

_ORACLE = (
    pathlib.Path(__file__).resolve().parents[1]
    / "tools"
    / "reference"
    / "make_generation_reference_vectors.py"
)


def _oracle():
    """The independent maker, loaded from its path (it is not a package).

    Two implementations of method G6.5a exist on purpose, and a rule
    that only one of them holds is a rule that is not being checked.
    Loaded the way `tests/test_generation_reference.py` loads it.
    """
    spec = importlib.util.spec_from_file_location(
        "make_generation_reference_vectors", _ORACLE
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

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


def test_a_grid_finer_than_a_double_can_step_is_no_grid_at_all() -> None:
    """The 323-and-324 boundary, in BOTH implementations.

    A grid step is `10 ** -figures`. As a double that is positive
    through 323 figures and UNDERFLOWS to nought at 324, and method
    G6.5a stops the walk where the step is not a finite number greater
    than nought -- a column described more finely than a program can
    step has no grid to walk.

    Neither implementation was tested at that boundary until review
    round 6 of the integer-grid landing, and the two had already
    disagreed there once: the oracle's rational arithmetic never
    underflows, so when it was rewritten to be independent it lost the
    refusal and answered `1e-323` where the shipped walk answers
    nothing. So this asserts BOTH, and asserts a real move on the
    reachable side so that neither arm is passing by refusing
    everything.
    """
    oracle = _oracle()
    reachable = 323
    unreachable = 324

    # THE STEP ITSELF, which is what the rule is about.
    assert 10.0 ** -reachable > 0.0
    assert 10.0 ** -unreachable == 0.0

    # ON THE REACHABLE SIDE both implementations MOVE, so the refusal
    # below is a refusal and not the shape of the whole region.
    value = 5e-323
    spelt = generation._grid_text(value, reachable)
    written = {spelt: 2}
    mine = generation._apart_inside(
        value, reachable, generation._BAND_POSITIVE, None, None, dict(written)
    )
    theirs = oracle.apart_inside(
        value, reachable, "positive", None, None, dict(written)
    )
    assert mine is not None, mine
    assert theirs == mine, (mine, theirs)

    # AND ON THE OTHER SIDE both refuse.
    finer = generation._grid_text(5e-324, unreachable)
    refused = {finer: 2}
    assert generation._apart_inside(
        5e-324,
        unreachable,
        generation._BAND_POSITIVE,
        None,
        None,
        dict(refused),
    ) is None
    assert oracle.apart_inside(
        5e-324, unreachable, "positive", None, None, dict(refused)
    ) is None


def test_a_walk_that_answers_badly_cannot_inflate_the_count(
    tmp_path: pathlib.Path,
    monkeypatch: "object",
) -> None:
    """The CALLER's guard, which the helper's own tests cannot reach.

    The pass stops when the column holds as many different texts as the
    description publishes. That count used to be a tally kept beside
    the map and stepped once per accepted move -- so a walk that handed
    back a text the column already held raised the count without
    raising the number of different values, and the pass stopped early
    believing a fact it had not met. Review round 5 measured exactly
    that shape when the walk's round-trip refusal was removed: 26 of
    600 moves.

    The count is now `len(held)`, read from the map itself, so a bad
    answer cannot inflate it. This test proves the CALLER holds that
    even when the walk is broken, which is what the helper's own tests
    cannot show.
    """
    generator = random.Random(31337)
    rows = [str(generator.randint(40, 120)) for _each in range(200)]
    _document, loaded = _described(tmp_path, rows, "crowded")
    column = loaded.columns[0]
    published = column.facts.n_distinct_values
    assert published is not None and published > 40, published

    # A WALK THAT ANSWERS WITH A TEXT THE COLUMN ALREADY HOLDS. Nothing
    # it returns is a new value, so the count of different texts never
    # rises and the pass must keep going until it runs out of strata it
    # is allowed to move. A pass that stops sooner has believed a count
    # that did not rise.
    #
    # ELEVEN IS MEASURED, and it is measured because the difference is
    # small and real: with the count kept as a tally beside the map and
    # stepped once per accepted answer, this same fixture stops at TEN.
    # The deceiving walk does consolidate as it goes -- moving a
    # stratum off a doubled text leaves that text with one holder, so
    # later strata on it stop being eligible -- which is why this is a
    # measured number and not the count of eligible strata.
    called: "list[int]" = []

    def deceiving(value, figures, band, share, ends, written):
        called.append(1)
        for text in sorted(written):
            try:
                return float(text)
            except ValueError:
                continue
        return None

    monkeypatch.setattr(  # type: ignore[attr-defined]
        generation, "_apart_inside", deceiving
    )
    twin = generation.generate(loaded, SEED)

    assert len(called) == 11, len(called)

    # AND NO VALUE WAS INVENTED, which is the other half: a walk that
    # only ever hands back a text the column already holds cannot take
    # it to the published count.
    cells = [cell for cell in twin.columns[0] if cell != ""]
    assert len({float(cell) for cell in cells}) < published


def test_the_walk_never_answers_with_a_text_the_column_already_holds(
) -> None:
    """The refusal that keeps the count honest, and its own guard.

    A grid point is named by its text, but the stratum carries a
    DOUBLE, and the caller re-spells that double to book what the
    stratum took. Where the two disagree the walk hands back a point
    whose text the column already holds, and the count of different
    numbers rises without a different number appearing -- which is the
    whole defect this pass exists to repair, arriving through the
    repair.

    Review round 5 of the integer-grid landing measured it: with the
    round-trip refusal removed, 26 of 600 moves came back spelling a
    text already written, and every test in this file stayed green.
    So the rule is asserted here directly, over the widths where a grid
    is finer than the numbers standing on it.
    """
    generator = random.Random(4212)
    asked = 0
    answered = 0
    for _case in range(700):
        figures = generator.choice((8, 11, 13, 15, 17))
        value = generator.choice((
            generator.uniform(-1e7, 1e7),
            generator.uniform(-1e12, 1e12),
            generator.uniform(-1.0, 1.0),
        ))
        if value == 0.0:
            continue
        band = (
            generation._BAND_POSITIVE if value > 0
            else generation._BAND_NEGATIVE
        )
        spelt = generation._grid_text(value, figures)
        units = generation._grid_units(spelt, figures)
        if units is None:
            continue
        written = {spelt: 1}
        for step in range(1, 6):
            for side in (-step, step):
                written[generation._grid_at(units + side, figures)] = 1
        asked = asked + 1
        taken = generation._apart_inside(
            value, figures, band, None, None, written,
        )
        if taken is None:
            continue
        answered = answered + 1
        # THE WHOLE OF THE RULE: what comes back, re-spelled the way
        # the caller will re-spell it, is a text the column does not
        # already hold.
        assert generation._grid_text(taken, figures) not in written, (
            value, figures, taken,
        )
    # AND THE PROBE REALLY REACHED THE HARD REGION, so a walk that
    # refused everything could not pass by doing nothing.
    assert asked > 400, asked
    assert answered > 0, answered


def test_the_walk_counts_sixty_four_GRID_steps_and_not_sixty_four_sums(
) -> None:
    """The reach is a count of grid units, which binary addition is not.

    Adding `10 ** -figures` to a double sixty-four times does not move
    sixty-four grid units -- the addition accumulates. Measured by
    review round 4 of the integer-grid landing: anchored at
    `1805966.0` on a grid of eleven figures, with the texts of reaches
    1 to 58 already written, the walk returned a point SEVENTY grid
    units from its anchor, and method G6.5a bounds it at sixty-four.

    The walk reads its anchor as a whole number of grid units and adds
    the step to THAT, so sixty-four means sixty-four. This test asserts
    the bound over a spread of widths and magnitudes rather than one
    call, because the defect only shows where the grid is fine against
    the numbers on it.
    """
    generator = random.Random(20260903)
    furthest = 0
    taken_count = 0
    for _case in range(600):
        figures = generator.choice((0, 1, 2, 3, 5, 8, 11))
        value = generator.choice((
            generator.uniform(-1000.0, 1000.0),
            generator.uniform(-1e6, 1e6),
        ))
        if value == 0.0:
            continue
        band = (
            generation._BAND_POSITIVE if value > 0
            else generation._BAND_NEGATIVE
        )
        spelt = generation._grid_text(value, figures)
        units = generation._grid_units(spelt, figures)
        if units is None:
            continue
        written = {spelt: 1}
        for step in range(1, generator.choice((2, 6, 21, 41))):
            for side in (-step, step):
                written[generation._grid_at(units + side, figures)] = 1
        taken = generation._apart_inside(
            value,
            figures,
            band,
            (value - 50.0, value + 50.0),
            (-1e12, 1e12),
            written,
        )
        if taken is None:
            continue
        landed = generation._grid_units(
            generation._grid_text(taken, figures), figures
        )
        assert landed is not None, (taken, figures)
        away = abs(landed - units)
        furthest = max(furthest, away)
        taken_count = taken_count + 1
        assert away <= 64, (value, figures, away)
    # THE PROBE REALLY MOVED SOMETHING, asserted so a walk that refused
    # everything could not pass this test by doing nothing.
    assert taken_count > 100, taken_count
    assert furthest > 1, furthest


def test_a_candidate_on_the_inclusive_end_of_a_share_is_taken() -> None:
    """The share's ends are INCLUSIVE, and binary stepping said otherwise.

    The walk reaches a candidate by adding a grid step to the value it
    anchored on, and that addition accumulates in binary: a tenth added
    to `0.2` is `0.30000000000000004`, which is GREATER than `0.3`. Ask
    the share about that sum and a candidate whose grid text is exactly
    the share's inclusive upper end is refused by the end it sits on,
    and the stratum stays where it is -- which is the shape this whole
    pass exists to prevent, two strata written as one cell.

    WHAT THIS TEST SHOWS AND WHAT IT DOES NOT. It calls the helper
    directly with a share and a written-text map, so it proves the
    RULE. It does not build a column through the producer and the
    loader that arrives in this state, so it is not evidence that a
    real description reaches it -- and no golden or frozen vector
    supplies that either, which is why the helper is pinned here.

    Review round 3 of the integer-grid landing found it. The repair is
    that each step is snapped to its grid text first, and the bounds,
    the sign band and the written-text refusal are all asked about the
    SNAPPED point, which is also what the stratum takes.

    Goes red if the candidate is tested before it is snapped: no
    committed golden or frozen vector sits on such an endpoint, so this
    is the only thing in the tree that holds the rule.
    """
    # The arithmetic the defect turns on, asserted so the fixture
    # cannot quietly stop being the case it was built for.
    assert 0.2 + 0.1 > 0.3
    assert generation._grid_text(0.2 + 0.1, 1) == "0.3"

    taken = generation._apart_inside(
        0.2,
        1,
        generation._BAND_POSITIVE,
        (0.2, 0.3),
        (0.2, 1.0),
        {"0.2": 2, "0.4": 1, "1.0": 1},
    )
    assert taken == 0.3, taken
    # AND WHAT COMES BACK IS THE GRID POINT, not the sum that reached
    # it: the stratum keeps this number, and a later stage writing it
    # would carry the binary tail into the cell.
    assert generation._grid_text(taken, 1) == "0.3"
    assert taken == float("0.3")


def test_a_whole_number_column_is_on_a_grid_too(
    tmp_path: pathlib.Path,
) -> None:
    """THE INTEGERS ARE A GRID, and this pass declined them until now.

    A whole-number column carries no figure after the point, so its
    `fraction_widths` census is EMPTY -- there is no width to count.
    `_pinned_fraction` read that as "no grid" and answered -1, and the
    pass returned before doing anything -- for every whole-valued
    column there is. How many of a real table's columns those are is
    not measured here and is not claimed.

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
    """An empty census ALONE is not the integer grid.

    `integer_valued` is the other half, and it is what stops a decimal
    value being moved onto an integer. The census counts figures after
    the point on `decimal`-styled cells only, so a column written in
    EXPONENT form publishes an empty census while holding values that
    are not whole -- which is the one shape that tells the two halves
    of the rule apart.

    THE FIRST WRITING OF THIS TEST WAS VACUOUS and review round 1 of
    the landing caught it: its fixture was ragged decimals publishing
    widths 1, 2 and 3, so it re-ran the several-widths refusal below
    and would have stayed green if the rule became "every empty census
    is grid zero".
    """
    rows = [
        f"{value}e0"
        for value in ("1.5", "2.5", "3.5", "4.5", "6.5", "7.5",
                      "8.5", "9.5", "1.25", "2.25", "3.25", "4.25")
    ] * 6
    _document, loaded = _described(tmp_path, rows, "powers")
    column = loaded.columns[0]
    facts = column.facts
    # THE FIXTURE IS THE SHAPE THE RULE TURNS ON, asserted rather than
    # assumed: an EMPTY census on a column that is NOT whole-valued.
    assert facts.fraction_widths == {}, facts.fraction_widths
    assert facts.integer_valued is False, facts.integer_valued
    assert generation._pinned_fraction(column, facts) == -1


def test_the_two_halves_of_the_integer_grid_rule_are_both_needed(
    tmp_path: pathlib.Path,
) -> None:
    """The same census, the other answer, so neither half is decoration.

    Multiply every value of the column above by ten and each one is
    whole. The census is empty either way -- both are written in
    exponent form and neither carries a `decimal` cell -- so the census
    cannot be what decides it, and `integer_valued` is.
    """
    rows = [
        f"{value}e1"
        for value in ("1.5", "2.5", "3.5", "4.5", "6.5", "7.5", "8.5", "9.5")
    ] * 9
    _document, loaded = _described(tmp_path, rows, "tens")
    column = loaded.columns[0]
    facts = column.facts
    assert facts.fraction_widths == {}, facts.fraction_widths
    assert facts.integer_valued is True, facts.integer_valued
    assert generation._pinned_fraction(column, facts) == 0


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
