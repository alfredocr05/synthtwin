"""P4-D32: no value stands where the description says there is none.

WHAT THIS FILE PINS, AND WHY EACH PIECE IS HERE. A column with two
clusters and nothing between them publishes a middle rung BETWEEN the
clusters -- the median of a hundred and fifty values around twenty and
a hundred and fifty around eighty is 49.65, a number no cell of that
column holds -- and the value stage interpolated the rungs and honoured
it (residual R-P4-136). The key `empty_bins` names the bins holding
NOBODY, published whatever the smallest group size is because there is
no group smaller than nobody, and method G6.7 makes the value stage
read it.

**The repair is in the VALUE DRAW**, so the witness has to be a whole
run: build the CSV, describe it with the real producer, load it with
the real loader, generate, and recount the twin's own finished cells
against the bin rule all three modules share. Every table here is built
by the seeded neutral builders of `fixtures.py` (plan D13); no
committed data file is read.

THE MEASUREMENT EACH WITNESS STANDS ON, taken on the tree this landing
branched from and on this one, forty seeds each, at the default floor
and again at a floor of eleven:

* 150 around 20 + 150 around 80: 4-6 cells of 300 in a bin the source
  leaves empty, against 0 at every seed;
* 250 around 10 + 50 around 90: 2-3 of 300, against 0 at every seed;
* 150 around 40 + 150 around 60: 3-6 of 300, against 0 at every seed.

`test_a_two_cluster_column_writes_nothing_in_its_empty_middle` is the
one that turns red when the pass alone is withdrawn.

THE STRETCH'S REAL EDGES ARE PUBLISHED TOO (`empty_edges`, residual
R-P4-138, closed by the owner's ruling of 2026-09-04), AND THE PASS
ASKS THEM which stretch a stratum stands in. A bin is a thirty-second
of the column's reach, so the empty BINS lie strictly inside the
stretch the SOURCE leaves empty: a cell moved to a bin edge was still
in the source's own gap, and a stratum could stand inside the gap
while standing in a bin that held plenty, where a queue built from the
bins never saw it.

THE LEDGER, on the three witnesses here, forty seeds each, counting
cells inside the SOURCE's own widest gap rather than inside a bin:

* moved to the nearest occupied BIN: one cell per column per seed,
  15.7 to 23.0 units from the nearest real value;
* walking from the published EDGES, queue still gathered from the
  bins: 8, 4 and 27 of 12,000;
* asking the published PAIRS: 0, 0 and 0, which is what
  `test_no_cell_stands_inside_the_sources_own_gap` asserts.
"""

import ast
import copy
import dataclasses
import pathlib
import random

import fixtures
import pytest
from synthtwin import (
    contract,
    errors,
    generation,
    parsing,
    profile,
    quality,
    reading,
    summary,
    taxonomy,
    validation,
)

# THE SEEDS, FIXED AND WRITTEN OUT. A witness that draws its own seeds
# is a witness whose failure nobody can reproduce.
SEEDS = (0, 3, 11, 29, 47)


def _two_tight_rows() -> "list[str]":
    """R-P4-136's own column: 150 around 20 and 150 around 80.

    Drawn from `random.Random(11)` and written out by this file rather
    than committed, which is plan D13's rule; the seed is fixed, so the
    column is a function of this file and of nothing else.
    """
    draw = random.Random(11)
    return (
        [f"{round(draw.gauss(20, 2), 1)}" for _index in range(150)]
        + [f"{round(draw.gauss(80, 3), 1)}" for _index in range(150)]
    )


def _uneven_rows() -> "list[str]":
    """250 around 10 and 50 around 90: the clusters are not the same size."""
    draw = random.Random(12)
    return (
        [f"{round(draw.gauss(10, 2), 1)}" for _index in range(250)]
        + [f"{round(draw.gauss(90, 3), 1)}" for _index in range(50)]
    )


def _closer_rows() -> "list[str]":
    """150 around 40 and 150 around 60: a NARROW empty middle.

    It matters because the stretch is a handful of bins rather than
    nineteen, and because the bins it leaves empty are not contiguous:
    one bin between the clusters holds a single value, so the rule has
    two stretches to keep out of and not one.
    """
    draw = random.Random(13)
    return (
        [f"{round(draw.gauss(40, 2), 1)}" for _index in range(150)]
        + [f"{round(draw.gauss(60, 3), 1)}" for _index in range(150)]
    )


def _described(
    folder: pathlib.Path,
    name: str,
    rows: "list[str]",
    floor: int = 1,
    header: str = "amount",
) -> "tuple[dict, contract.Profile]":
    """The real reader, the real producer and the real loader."""
    path = fixtures.write(
        folder, f"{name}.csv", header + "\n" + "\n".join(rows) + "\n"
    )
    table = reading.read_table(
        str(path), first_row=reading.FIRST_ROW_AUTOMATIC
    )
    document = profile.build_document(
        table, taxonomy.Settings(small_cell_floor=floor), []
    )
    loaded = contract.load_profile(
        str(fixtures.write_profile(folder, f"{name}-profile.json", document))
    )
    return document, loaded


def _empty_of(rows: "list[str]") -> "tuple[float, float, list[int]]":
    """The bins the SOURCE leaves empty, by the shipped bin rule.

    Computed here from the rows rather than read out of the
    description, so the assertion below compares the twin against the
    TABLE and not against the key under test. A recount that read the
    key would pass on a producer that published the wrong bins.
    """
    numbers = [float(one) for one in rows]
    lowest = min(numbers)
    highest = max(numbers)
    held = {
        parsing.histogram_bin(one, lowest, highest) for one in numbers
    }
    return lowest, highest, [
        place
        for place in range(parsing.HISTOGRAM_BINS)
        if place not in held
    ]


def _cells_in(
    twin: generation.Twin, lowest: float, highest: float, barred: "set[int]"
) -> "list[str]":
    """Every cell of the twin's one column standing in a barred bin."""
    found: list[str] = []
    for cell in twin.columns[0]:
        if cell == "":
            continue
        value = parsing.parse_number(cell)
        if value is None:
            continue
        if parsing.histogram_bin(value, lowest, highest) in barred:
            found = found + [cell]
    return found


# -- the producer publishes the fact ----------------------------------


def test_a_two_cluster_column_publishes_the_bins_that_hold_nothing(
    tmp_path: pathlib.Path,
) -> None:
    """The description names exactly the bins the table leaves empty."""
    rows = _two_tight_rows()
    lowest, highest, barred = _empty_of(rows)
    document, _loaded = _described(tmp_path, "tight", rows)
    assert barred, "this column is chosen for having an empty middle"
    assert document["columns"][0]["empty_bins"] == barred
    assert lowest == document["columns"][0]["percentiles"]["min"]
    assert highest == document["columns"][0]["percentiles"]["max"]


def test_the_fact_survives_a_floor_the_census_beside_it_does_not(
    tmp_path: pathlib.Path,
) -> None:
    """The whole reason the key exists beside `value_histogram`.

    The census is all or nothing, so it vanishes at every floor above
    one on exactly the columns whose shape matters most: a two-cluster
    column has thin bins at the edges of each cluster. The empty-bin
    list is under no floor and says the same thing at every one.
    """
    rows = _two_tight_rows()
    _lowest, _highest, barred = _empty_of(rows)
    seen = []
    for floor in (1, 2, 3, 5, 11):
        document, _loaded = _described(
            tmp_path, f"floors-{floor}", rows, floor=floor
        )
        block = document["columns"][0]
        seen = seen + [len(block["value_histogram"])]
        assert block["empty_bins"] == barred, floor
    assert seen[0] > 0, "at a floor of one the census is publishable"
    assert seen[1:] == [0, 0, 0, 0], (
        "above a floor of one this column's census is withheld, which is "
        "the measurement plan P4-D32 rests on"
    )


def test_a_column_with_no_empty_stretch_names_none(
    tmp_path: pathlib.Path,
) -> None:
    """A check that CAN fail the other way.

    A rule that named bins on every column would pass every assertion
    above and be useless, so one column with values spread over its
    whole range is described here and must name nothing.
    """
    rows = [f"{index * 0.5:.1f}" for index in range(400)]
    document, _loaded = _described(tmp_path, "even", rows)
    assert document["columns"][0]["empty_bins"] == []


# -- the loader refuses what no column could be ------------------------


def _tampered(
    tmp_path: pathlib.Path, name: str, bins: "list[int]"
) -> "str | None":
    """Load a description whose empty-bin list has been rewritten.

    BUILT AT A RAISED FLOOR, so the census beside it is legitimately
    absent and the complement condition has nothing to say. Editing a
    floor-one description instead put the census and the list in
    disagreement, and the loader then refused on Q15 -- which is a real
    refusal about the wrong fact, and would have let a missing Q20
    condition pass unnoticed.
    """
    document, _loaded = _described(
        tmp_path, name, _two_tight_rows(), floor=11
    )
    assert document["columns"][0]["value_histogram"] == {}
    document["columns"][0]["empty_bins"] = bins
    path = fixtures.write_profile(tmp_path, f"{name}-edited.json", document)
    try:
        contract.load_profile(str(path))
    except errors.ProfileError as refusal:
        return f"{refusal}"
    return None


def test_the_loader_refuses_a_repeated_bin(tmp_path: pathlib.Path) -> None:
    """Each bin named once, in order (invariant Q20)."""
    refusal = _tampered(tmp_path, "repeat", [5, 5, 6])
    assert refusal is not None
    assert "Q20" in refusal or "ascending" in refusal


def test_the_loader_refuses_a_bin_out_of_order(
    tmp_path: pathlib.Path,
) -> None:
    """A list a producer may write two ways is one two producers differ on."""
    refusal = _tampered(tmp_path, "order", [7, 6])
    assert refusal is not None


def test_the_loader_refuses_an_end_bin(tmp_path: pathlib.Path) -> None:
    """The smallest value is in the first bin and the largest in the last."""
    assert _tampered(tmp_path, "first", [0, 5]) is not None
    assert _tampered(
        tmp_path, "last", [5, parsing.HISTOGRAM_BINS - 1]
    ) is not None


def test_the_loader_refuses_a_bin_the_census_names(
    tmp_path: pathlib.Path,
) -> None:
    """ONE FACT WRITTEN TWICE, and the guard against one copy moving.

    Where the census is published it names every bin that holds
    something, so the two are complements. A description whose two
    shape facts disagree is refused rather than read.
    """
    document, _loaded = _described(tmp_path, "clash", _two_tight_rows())
    block = document["columns"][0]
    named = sorted(int(key) for key in block["value_histogram"])
    assert named, "this column publishes its census at the default floor"
    block["empty_bins"] = sorted(set(block["empty_bins"]) | {named[1]})
    path = fixtures.write_profile(tmp_path, "clash-edited.json", document)
    with pytest.raises(errors.ProfileError):
        contract.load_profile(str(path))


def _forwarded_fact_places(
    tree: "ast.Module",
) -> "dict[str, set[int]]":
    """Which helpers pass a caller's argument on as a deviation's fact.

    `_deviation` is called with a LITERAL key in most places and with a
    variable in five, and those five take it from a caller -- through
    `_named_miss`, `_endpoint_notes` and `_cleared_into`. A scan that
    read only the literals at `_deviation` saw twenty-seven of the
    forty keys a report can carry, and the method's own inventory was
    missing three of them with nothing to notice (review rounds 4 and
    5).

    Guarantees: accepts the parsed module; returns each forwarding
    helper's name against the argument positions it forwards.
    Determinism: a function of the source. Raises nothing. No I/O.
    """
    functions: "dict[str, ast.FunctionDef]" = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef,)):
            functions[node.name] = node
    places: "dict[str, set[int]]" = {}

    def look(holder: str, body: "ast.FunctionDef", called: str) -> None:
        for inner in ast.walk(body):
            if not isinstance(inner, ast.Call):
                continue
            if not isinstance(inner.func, ast.Name):
                continue
            if inner.func.id != called or len(inner.args) < 2:
                continue
            second = inner.args[1]
            if not isinstance(second, ast.Name):
                continue
            named = [one.arg for one in body.args.args]
            if second.id in named:
                found = places[holder] if holder in places else set()
                places[holder] = found | {named.index(second.id)}

    for name in functions:
        look(name, functions[name], "_deviation")
    # ...and one more hop, twice, for a helper that forwards to a
    # helper. Three passes is more than the file has ever needed and
    # is bounded, which a walk over a call graph has to be.
    for _round in range(3):
        for name in functions:
            for holder in list(places):
                look(name, functions[name], holder)
    return places


def test_every_deviation_key_is_one_the_method_authorizes(
    tmp_path: pathlib.Path,
) -> None:
    """G12 calls its list COMPLETE, and this is what makes that checkable.

    THE PROSE LIST NAMES SHAPES AND NOT KEYS, which is what a reader
    needs and what nothing could check: "a raised distinct count
    (G5.2)" is the entry, and `n_distinct` is the key the report
    carries. G12 carries a KEY INDEX beside the prose for that reason,
    and this holds the two together in BOTH directions -- a key the
    generator can pass and the index does not name, and a name in the
    index no call can produce.

    THREE KEYS WERE MISSING when this was first written: `shape_forms`,
    `empty_bins` and `empty_edges`, the last two authorized by G6.7.8
    from the landing that added them. A report built from that list
    would have omitted them; an auditor holding a report to it would
    have refused them.
    """
    tree = ast.parse(
        pathlib.Path(generation.__file__).read_text(encoding="utf-8")
    )
    places = _forwarded_fact_places(tree)
    named: "set[str]" = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Name):
            continue
        if node.func.id == "_deviation":
            wanted = {1}
        elif node.func.id in places:
            wanted = places[node.func.id]
        else:
            continue
        for place in wanted:
            if place >= len(node.args):
                continue
            arg = node.args[place]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                named.add(arg.value)
    # THE TWO GAP KEYS ARE CHOSEN INSIDE `_clear_enough` and passed on
    # from a local, so no static walk reaches them. They are read from
    # a RUN instead -- the same mixed-route shape the witness above
    # drives -- so this guard reads what the generator really emits.
    rows = (
        ["0.0", "32.0", "9.9", "13.1"]
        + [f"{place}.5" for place in range(1, 10)]
        + [f"{place}.5" for place in range(13, 32)]
    )
    _document, loaded = _described(tmp_path, "keys", rows)
    column = loaded.columns[0]
    facts = dataclasses.replace(
        column.facts,
        empty_bins=(10, 11, 12),
        empty_edges=((9.9, 13.1),),
    )
    layout = generation._NumericLayout(
        sizes=(1, 1, 1, 1, 1, 1),
        starts=(0, 1, 2, 3, 4, 5),
        bands=(
            generation._BAND_ZERO,
        ) + (generation._BAND_POSITIVE,) * 5,
        raw_budgets=(),
        folded_budgets=(),
    )
    _moved, notes = generation._clear_enough(
        column, facts, layout, [0.0, 11.0, 11.0, 13.05, 13.05, 32.0]
    )
    for note in notes:
        named.add(note.fact)
    assert "empty_bins" in named and "empty_edges" in named, sorted(named)

    said = (
        fixtures.GOVERNING_CONTRACT.parent / "generation-method-v1.md"
    ).read_text(encoding="utf-8")
    start = said.index("**THE KEY INDEX, so that")
    stop = said.index(
        "A name here is a key a report MAY carry", start
    )
    listed = {
        line[3:-1]
        for line in said[start:stop].split("\n")
        if line.startswith("* `") and line.endswith("`")
    }
    assert named - listed == set(), sorted(named - listed)
    assert listed - named == set(), sorted(listed - named)


def test_the_disclosure_ceiling_is_the_one_the_documents_state() -> None:
    """The worst case, built rather than reasoned about (round 3 item 1).

    `SECURITY.md` and contract 12.3 row 21 state what this key can put
    in a description, and that sentence was wrong twice before it was
    built: first "two more beside eleven", then "sixteen distinct
    values" from a probe that MINIMISED the values in each occupied
    bin. The construction that maximises it puts TWO values in every
    separating bin, so no two runs share an edge and all thirty
    entries are different.

    Driven on the producer directly, because what is under test is a
    bound on what a description can carry rather than a twin.
    """
    lowest, highest = 0.0, 32.0
    values = [lowest, 0.9]
    for place in range(2, 30, 2):
        values = values + [place + 0.1, place + 0.9]
    values = values + [30.1, highest]
    # THE ALLOCATION THE DOCUMENTS STATE, asserted here rather than
    # left to the totals (review round 4 item 1): bins 0 and 2 to 28
    # hold two values each and bins 30 and 31 hold one each, which is
    # thirty-two rows. "Two in every occupied bin" would be
    # thirty-four, and the documents said it until this line was
    # written.
    assert len(values) == 32, len(values)
    held: "dict[int, int]" = {}
    for one in values:
        place = parsing.histogram_bin(one, lowest, highest)
        held[place] = held[place] + 1 if place in held else 1
    assert sorted(held) == [0] + list(range(2, 32, 2)) + [31], sorted(held)
    assert [held[place] for place in range(0, 30, 2)] == [2] * 15, held
    assert held[30] == 1 and held[31] == 1, held
    bins = taxonomy._empty_bins(values)
    edges = taxonomy._empty_edges(values)
    named = [one for pair in edges for one in pair]
    assert len(bins) == 15, bins
    assert len(edges) == 15, edges
    assert len(named) == 30, named
    assert len(set(named)) == 30, sorted(set(named))
    # ...and with the two endpoints the ladder publishes beside them,
    # the description names every value this column holds, which is
    # the sentence the documents owe a reader.
    assert set(named) | {lowest, highest} == set(values), sorted(
        set(values) - (set(named) | {lowest, highest})
    )
    # AND FIFTEEN IS THE MOST THERE CAN BE: the first bin and the last
    # always hold the two endpoints, and two runs are separated by an
    # occupied bin, so thirty interior bins give fifteen runs at most.
    assert parsing.HISTOGRAM_BINS == 32
    assert len(edges) == (parsing.HISTOGRAM_BINS - 2) // 2


def test_a_stretch_reached_both_ways_names_both_facts(
    tmp_path: pathlib.Path,
) -> None:
    """One stretch, two routes, two fact names (round 3 item 2).

    A stretch can hold strata BOTH ways at once: some standing in a
    bin it says holds nothing, and others standing in a bin that holds
    plenty while their value is inside the published pair -- a gap is
    finer than a bin, so both are possible in the same stretch. The
    note that says which fact a stuck cell missed was kept per
    STRETCH, so every one of them was told whichever route the first
    arrival took.

    Driven through `_clear_enough` rather than through a table,
    because what is under test is the bookkeeping and a column that
    produced this shape by chance would pin nothing.
    """
    # A REAL DESCRIPTION FIRST, so the block handed to the pass is one
    # the loader built; only the two keys under test are replaced.
    # Bins are one wide on a scale of 0 to 32. Bins 10 to 12 hold
    # nothing, and the published gap runs 9.9 to 13.1, so it reaches
    # into occupied bins 9 and 13 -- which is the shape that makes one
    # stretch reachable both ways.
    rows = (
        ["0.0", "32.0", "9.9", "13.1"]
        + [f"{place}.5" for place in range(1, 10)]
        + [f"{place}.5" for place in range(13, 32)]
    )
    _document, loaded = _described(tmp_path, "bothways", rows)
    column = loaded.columns[0]
    facts = dataclasses.replace(
        column.facts,
        empty_bins=(10, 11, 12),
        empty_edges=((9.9, 13.1),),
    )
    assert facts.percentiles.rungs[0] == 0.0
    assert facts.percentiles.rungs[-1] == 32.0
    # 11.0 stands in bin 11, which the description says holds nothing.
    # 13.05 stands in bin 13, which holds plenty, and is inside the
    # published pair -- and so is every spelling of it, so the bins
    # have nothing to say about it and only the pair queues it.
    # Each value is held TWICE, so the sole-holder rule refuses every
    # move and each one gets a note of its own.
    values = [0.0, 11.0, 11.0, 13.05, 13.05, 32.0]
    layout = generation._NumericLayout(
        sizes=(1, 1, 1, 1, 1, 1),
        starts=(0, 1, 2, 3, 4, 5),
        bands=(
            generation._BAND_ZERO,
        ) + (generation._BAND_POSITIVE,) * 5,
        raw_budgets=(),
        folded_budgets=(),
    )
    _moved, notes = generation._clear_enough(
        column, facts, layout, values
    )
    named = sorted(note.fact for note in notes)
    assert named == [
        "empty_bins", "empty_bins", "empty_edges", "empty_edges"
    ], named
    # ...and the order the two routes are met in must not decide it
    # either, which is what a note kept per STRETCH got wrong: the
    # same six values with the pair-only pair FIRST in the ladder.
    other = [0.0, 13.05, 13.05, 11.0, 11.0, 32.0]
    _again, more = generation._clear_enough(
        column, facts, layout, other
    )
    assert sorted(note.fact for note in more) == [
        "empty_bins", "empty_bins", "empty_edges", "empty_edges"
    ], sorted(note.fact for note in more)
    # ...and each note carries the stretch as the DESCRIPTION states
    # it -- the published pair, not the bin boundaries -- and the value
    # that stayed inside it.
    for note in more:
        assert note.published == "no value from 9.9 to 13.1", note
    assert sorted(note.achieved for note in more) == [
        "one cell holds 11.0", "one cell holds 11.0",
        "one cell holds 13.05", "one cell holds 13.05",
    ], sorted(note.achieved for note in more)


def test_the_bin_rule_is_total_and_says_which_bin_an_edge_belongs_to(
) -> None:
    """C6-31f, driven directly (review round 3 items 7 and 8).

    TWO THINGS THE ONE RULE THREE MODULES SHARE HAD TO SAY. A value on
    a shared edge belongs to the UPPER bin -- the one that starts
    there -- which the code comment denied while the arithmetic did
    it. And the function RAISES NOTHING, which it did not: a value far
    outside a narrow scale gave a finite share that overflowed when it
    was multiplied, so `histogram_bin(1e308, -1.0, 1.0)` raised
    `OverflowError` inside a function whose contract says it raises
    nothing.
    """
    # THE SHARED EDGE. On a scale of 0 to 32 a bin is one wide, so the
    # whole numbers ARE the shared edges and each belongs to the bin
    # that starts there.
    for place in range(parsing.HISTOGRAM_BINS):
        assert parsing.histogram_bin(
            float(place), 0.0, 32.0
        ) == place, place
    # ...and the last bin is closed, so the published maximum has
    # somewhere to go.
    assert parsing.histogram_bin(32.0, 0.0, 32.0) == 31
    # TOTALITY, at both signs and past both ends.
    assert parsing.histogram_bin(1e308, -1.0, 1.0) == 31
    assert parsing.histogram_bin(-1e308, -1.0, 1.0) == 0
    assert parsing.histogram_bin(float("inf"), 0.0, 32.0) == 0
    assert parsing.histogram_bin(0.0, 5.0, 5.0) == 0
    # ...AND THE SUBTRACTION ITSELF CAN LEAVE THE FORMAT where the
    # reach does not (review round 4 item 5). On a scale of -1e308 to
    # 0 a value of 1e308 made `value - lowest` an infinity, the share
    # a NaN, and the guard for a NaN share answered bin ZERO -- for a
    # value above the MAXIMUM. Both directions, on scales whose reach
    # is finite and whose distance to the value is not.
    assert parsing.histogram_bin(1e308, -1e308, 0.0) == 31
    assert parsing.histogram_bin(-1e308, 0.0, 1e308) == 0


def test_the_loader_refuses_an_edge_standing_in_its_own_empty_stretch(
    tmp_path: pathlib.Path,
) -> None:
    """Q21 binds each pair to the RUN it belongs to (round 1 item 4).

    A pair whose two values both stand in bins the same description
    says hold nothing satisfies every other condition -- as many pairs
    as runs, ascending, inside the two ends -- and describes no column
    any table holds. The value stage read those two numbers as values
    of real cells and walked out to them.
    """
    document, loaded = _described(tmp_path, "inward", _two_tight_rows())
    block = document["columns"][0]
    assert block["empty_edges"], "this column has an empty middle"
    ends = (
        loaded.columns[0].facts.percentiles.rungs[0],
        loaded.columns[0].facts.percentiles.rungs[-1],
    )
    width = (ends[1] - ends[0]) / parsing.HISTOGRAM_BINS
    first = block["empty_bins"][0]
    # Two values INSIDE the first empty bin, ascending and inside the
    # published ends: everything Q21 asked before this landing.
    inward = [
        ends[0] + width * first + width * 0.2,
        ends[0] + width * first + width * 0.8,
    ]
    block["empty_edges"] = [inward] + block["empty_edges"][1:]
    path = fixtures.write_profile(tmp_path, "inward-edited.json", document)
    with pytest.raises(errors.ProfileError):
        contract.load_profile(str(path))


def test_the_loader_refuses_a_bin_the_census_accounts_for_neither_way(
    tmp_path: pathlib.Path,
) -> None:
    """The other half of the complement, and it fails differently.

    Dropping a bin from the empty list while the census still names
    only what it named leaves one bin claimed by neither fact. A
    one-directional check would pass this.
    """
    document, _loaded = _described(tmp_path, "hole", _two_tight_rows())
    block = document["columns"][0]
    assert block["empty_bins"], "this column has an empty middle"
    block["empty_bins"] = block["empty_bins"][1:]
    path = fixtures.write_profile(tmp_path, "hole-edited.json", document)
    with pytest.raises(errors.ProfileError):
        contract.load_profile(str(path))


def test_the_plain_page_names_the_edges_of_a_nested_block(
    tmp_path: pathlib.Path,
) -> None:
    """The page reaches `parts[]` and the compound halves (round 2 item 1).

    A `joined_numbers` column carries no `empty_bins` of its own: it
    carries one block per POSITION, and each of those publishes the
    stretches and the two real values each stretch lies between. A
    page that read the column alone told the holder of such a
    description nothing about the exact values in it, which is the one
    line of this page that puts a real cell's value in front of a
    reader.
    """
    draw = random.Random(7)
    rows = [
        f"{round(draw.gauss(20, 2), 0):.0f}/{draw.randint(60, 90)}"
        for _index in range(150)
    ] + [
        f"{round(draw.gauss(80, 3), 0):.0f}/{draw.randint(60, 90)}"
        for _index in range(150)
    ]
    path = fixtures.write(
        tmp_path, "bp.csv", "bp\n" + "\n".join(rows) + "\n"
    )
    document = profile.build_document(
        reading.read_table(
            str(path), first_row=reading.FIRST_ROW_AUTOMATIC
        ),
        taxonomy.Settings(small_cell_floor=1),
        [],
        [],
        ["bp"],
    )
    block = document["columns"][0]
    assert block["role"] == "joined_numbers", block["role"]
    assert "empty_bins" not in block, (
        "this witness needs the fact to live BELOW the column, or it "
        "witnesses nothing"
    )
    assert block["parts"][0]["empty_edges"], block["parts"][0]
    page = summary.render(document, "")
    said = [
        line for line in page.splitlines() if "either side of it" in line
    ]
    assert said, (
        "the page says nothing about the exact values this joined "
        "description carries:\n" + page
    )
    named = [line for line in page.splitlines() if "part 1 of each" in line]
    assert named, "the page does not say WHICH position it is about"


# -- the twin keeps out of the stretches -------------------------------


@pytest.mark.parametrize(
    "name,build",
    (
        ("tight", _two_tight_rows),
        ("uneven", _uneven_rows),
        ("closer", _closer_rows),
    ),
)
def test_a_two_cluster_column_writes_nothing_in_its_empty_middle(
    tmp_path: pathlib.Path, name: str, build
) -> None:
    """THE WITNESS. Before this landing, 4-6, 2-3 and 3-6 cells of 300.

    Recounted off the twin's own finished text, against the bins
    computed from the SOURCE rows, so neither side of the comparison
    is the key under test.
    """
    rows = build()
    lowest, highest, barred = _empty_of(rows)
    assert barred, f"{name} is chosen for having an empty middle"
    _document, loaded = _described(tmp_path, f"gap-{name}", rows)
    for seed in SEEDS:
        twin = generation.generate(loaded, seed)
        found = _cells_in(twin, lowest, highest, set(barred))
        assert found == [], (
            f"{name} at seed {seed}: the twin wrote {found} where the "
            f"description says the real column holds nothing"
        )


def test_the_twin_keeps_out_at_a_raised_floor_too(
    tmp_path: pathlib.Path,
) -> None:
    """At a floor of eleven the census is gone and the fact is not.

    This is the assertion the key exists for: the same repair on the
    same column with `value_histogram` withheld.
    """
    rows = _two_tight_rows()
    lowest, highest, barred = _empty_of(rows)
    _document, loaded = _described(tmp_path, "gap-raised", rows, floor=11)
    assert loaded.columns[0].facts.value_histogram == {}
    assert list(loaded.columns[0].facts.empty_bins) == barred
    for seed in SEEDS:
        twin = generation.generate(loaded, seed)
        assert _cells_in(twin, lowest, highest, set(barred)) == []


def test_the_twin_still_meets_everything_else_it_used_to(
    tmp_path: pathlib.Path,
) -> None:
    """The pass takes nothing back from the passes before it.

    Measured at forty seeds on the tree this branched from and on this
    one: the quality report on these twins misses exactly
    `widths.published.1` at every seed and `ladder.p90` at some, both
    PRE-EXISTING (residual R-P4-139). What must not appear is a new
    miss -- an end of the ladder, a sign count, `n_zero`, or the style
    census -- so those are named here rather than left to a total.
    """
    rows = _two_tight_rows()
    _document, loaded = _described(tmp_path, "keeps", rows)
    guarded = (
        "ladder.min",
        "ladder.max",
        "counts.n_zero",
        "counts.n_negative",
        "counts.n_used_in_statistics",
        "counts.n_left_out_of_statistics",
        "type.integer_valued",
    )
    for seed in SEEDS:
        twin = generation.generate(loaded, seed)
        path = fixtures.write(
            tmp_path,
            f"keeps-{seed}.csv",
            fixtures.rows_to_csv(
                list(twin.names), [list(row) for row in twin.rows]
            ),
        )
        outcome = validation.measure(loaded, f"{path}")
        missed = {
            check.subcheck
            for check in outcome.checks
            if check.verdict == validation.MISSED
        }
        for one in guarded:
            assert one not in missed, (
                f"seed {seed} missed {one}, which this landing must not "
                f"cost: {sorted(missed)}"
            )
        for one in ("styles.published.plain", "styles.published.decimal"):
            assert one not in missed, f"seed {seed} missed {one}"


def test_no_cell_stands_inside_the_sources_own_gap(
    tmp_path: pathlib.Path,
) -> None:
    """WHERE THE STRETCH REALLY LIES, and nothing is left inside it.

    Residual R-P4-138, closed by the owner's ruling of 2026-09-04. A
    bin is a thirty-second of the column's reach, so the bins a source
    leaves empty are strictly INSIDE the stretch the source really
    leaves empty. Two consequences followed, and BOTH had to be closed
    before this assertion could be made:

    * a cell moved to the edge of the nearest occupied BIN was still in
      the source's own gap -- `empty_edges` publishes the two values
      each stretch really lies between, and the walk starts there;
    * a stratum could stand INSIDE the gap and still be in a bin that
      holds plenty, so a queue built from the bins never saw it. The
      pass asks the published PAIRS which stretch a stratum is in, and
      the bins only where the pairs say nothing (review round 1 item
      2).

    MEASURED on all three witnesses of this file, FORTY seeds each,
    counting cells inside the SOURCE's widest gap rather than inside a
    bin:

    * before the edges: one cell per column per seed, 15.7 to 23.0
      units from the nearest real value;
    * with the edges but the bins still queueing: 8, 4 and 27 cells of
      12,000, the furthest 1.3 units away;
    * with both: **0, 0 and 0 of 12,000**.

    THE THREE WITNESSES ARE COUNTED SEPARATELY and at forty seeds
    rather than five, because the documents state a number for each and
    an aggregate over five seeds would leave three claims resting on
    one total (review round 1 item 7).
    """
    for name, build in (
        ("tight", _two_tight_rows),
        ("uneven", _uneven_rows),
        ("closer", _closer_rows),
    ):
        rows = build()
        numbers = sorted(float(one) for one in rows)
        widest = (0.0, 0.0, 0.0)
        for low, high in zip(numbers, numbers[1:]):
            if high - low > widest[0]:
                widest = (high - low, low, high)
        _document, loaded = _described(tmp_path, f"reach-{name}", rows)
        inside = []
        for seed in range(40):
            twin = generation.generate(loaded, seed)
            for cell in twin.columns[0]:
                if cell == "":
                    continue
                value = parsing.parse_number(cell)
                if value is None or not widest[1] < value < widest[2]:
                    continue
                inside = inside + [(seed, cell)]
        assert inside == [], (
            f"{name}: the source holds nothing between {widest[1]} and "
            f"{widest[2]}, and the twin wrote {len(inside)} cell(s) "
            f"there: {inside[:5]}"
        )


def test_where_the_twin_cannot_move_a_value_it_says_so(
    tmp_path: pathlib.Path,
) -> None:
    """The report is never silent about a cell that had to stay.

    THE WITNESS HAD TO BE REBUILT (review round 4 item 7). It stood on
    a whole-numbered column whose bins are barely wider than a unit,
    and after the queue repair that column's move never fails at all:
    driven at forty seeds it left NOTHING and named nothing, and its
    assertion was written so that nothing-and-nothing was accepted. A
    witness that is green when the reporting path is deleted witnesses
    nothing.

    THIS COLUMN STILL FAILS, and for the reason residual R-P4-140
    records: it straddles zero, and G6.7.4's SIGN BAND is what stops
    the move. The column holds no zero at all -- `n_zero` is nought --
    so the arm is not the zero band; it is the positive band. The
    stratum stuck in the gap holds a POSITIVE value, its nearer edge
    is the stretch's lower one at -23.0, and every candidate below
    that edge is negative, which the sign band refuses because
    `n_negative` is EXACT-OBSERVABLE while this fact is not. The
    further edge is walked after it and has nothing free either.

    Measured over forty seeds: five of them leave one cell, and the
    report names each by its own stretch and value.
    """
    draw = random.Random(2)
    rows = (
        [f"{round(draw.gauss(-30, 3), 1)}" for _index in range(150)]
        + [f"{round(draw.gauss(25, 2), 1)}" for _index in range(150)]
    )
    lowest, highest, barred = _empty_of(rows)
    assert barred, "this column is chosen for having an empty middle"
    assert lowest < 0.0 < highest, (lowest, highest)
    _document, loaded = _described(tmp_path, "across-zero", rows)
    stayed = 0
    for seed in range(40):
        twin = generation.generate(loaded, seed)
        left = _cells_in(twin, lowest, highest, set(barred))
        named = [
            note
            for note in twin.deviations
            if note.fact in ("empty_bins", "empty_edges")
        ]
        if not left:
            continue
        stayed = stayed + 1
        # THE NOTES ARE MATCHED TO THE CELLS, one for one. "Some gap
        # note exists" would be met by a note about a DIFFERENT cell
        # while the one left behind went unreported, which is the
        # silence this witness exists to refuse.
        edges = loaded.columns[0].facts.empty_edges
        holding = []
        for cell in left:
            value = parsing.parse_number(cell)
            place = parsing.histogram_bin(value, lowest, highest)
            for pair in edges:
                below = parsing.histogram_bin(pair[0], lowest, highest)
                above = parsing.histogram_bin(pair[1], lowest, highest)
                if below < place < above:
                    holding = holding + [
                        (
                            f"no value from {pair[0]} to {pair[1]}",
                            f"one cell holds {value}",
                        )
                    ]
                    break
        assert len(holding) == len(left), (left, edges)
        assert sorted(
            (note.published, note.achieved) for note in named
        ) == sorted(holding), (
            f"seed {seed}: the twin left {left} in a stretch and the "
            f"report named "
            f"{sorted((n.published, n.achieved) for n in named)}"
        )
        # ...and the value that stayed is POSITIVE on this column,
        # which is what says the sign band is the arm under test.
        for cell in left:
            assert parsing.parse_number(cell) > 0.0, cell
    assert loaded.columns[0].facts.n_zero == 0, (
        "this column is chosen for having NO zero, so the arm cannot "
        "be the zero band"
    )
    assert stayed > 0, (
        "the move never failed on this column at any of forty seeds, "
        "so this witness would stay green with the reporting path "
        "deleted -- which is the defect it was rebuilt to end"
    )
    assert stayed < 40, (
        "a column on which the move NEVER succeeds is not the witness "
        "this test means to be"
    )


# -- the fact reaches the pages a person reads -------------------------


def test_the_summary_says_the_column_held_nothing_in_a_stretch(
    tmp_path: pathlib.Path,
) -> None:
    """A person reading the summary is told, in words.

    Every other numeric line of that page names where the values ARE,
    and a two-cluster column looks in all of them exactly like one
    smooth column.
    """
    document, _loaded = _described(tmp_path, "summary", _two_tight_rows())
    page = summary.render(document, "")
    assert "held no value at all in" in page
    assert "equal steps between its smallest value and its largest" in page


def test_the_quality_report_lists_the_fact_rather_than_checking_it(
    tmp_path: pathlib.Path,
) -> None:
    """REPORT-ONLY, and the page says so where a person meets it."""
    rows = _two_tight_rows()
    _document, loaded = _described(tmp_path, "listed", rows)
    twin = generation.generate(loaded, 3)
    path = fixtures.write(
        tmp_path,
        "listed-twin.csv",
        fixtures.rows_to_csv(
            list(twin.names), [list(row) for row in twin.rows]
        ),
    )
    outcome = validation.measure(loaded, f"{path}")
    facts = {listing.fact for listing in outcome.listings}
    assert "numeric.empty_bins" in facts
    for check in outcome.checks:
        assert check.fact != "numeric.empty_bins", (
            "the fact is REPORT-ONLY on the measurement plan P4-D32 "
            "carries; a check here would hold a file to it"
        )
    page = quality.quality_report(loaded, outcome)
    assert "held no value at all" in page


# -- the rules of the move, each pinned where it is decided ------------
#
# EVERY TEST BELOW WAS WRITTEN AGAINST A SILENT MUTANT. The mutation run
# of this landing withdrew each rule of method G6.7 from the shipped
# generator in turn and ran 535 tests against each: the pass itself, the
# written-form test, and all four loader and producer rules turned the
# suite red, and these six did not. A rule a twin's BYTES cannot
# separate is pinned where it is decided instead -- which is the
# treatment residual R-P4-126 names for exactly this shape of gap -- so
# each one drives the named function directly rather than hoping a
# column can be found whose cells move when it is withdrawn.

# The scale these use: ends 0 to 3200, so a bin is a hundred wide and
# the stretch of bins 15 to 19 runs from 1500 to 2000.
#
# THE STRETCH IS DELIBERATELY NOT ON A DECADE BOUNDARY. A move keeps
# the value's figure count, so a stretch running from 100 to 200 would
# let a stratum move UP into three figures and refuse every move DOWN,
# because 99 is two figures and 110 is three. That is the rule working,
# not a defect -- but it would make one direction of these tests pass
# for the wrong reason. Here both neighbouring bins hold four-figure
# values, so direction is the only thing under test.
_ENDS = (0.0, 3200.0)
_BARRED = {place: 1 for place in range(15, 20)}
_RUN = (15, 19)
# THE STRETCH'S REAL EDGES, which `_cleared_value` takes after
# residual R-P4-138 (2026-09-04): the two values the source really
# holds either side of the stretch. Here they are put ON the bin
# edges, which is the scale these cases were written against, so
# what each of them drives is unchanged and only the way the walk is
# told where the stretch lies has moved.
_EDGES = (1500.0, 2000.0)
_WIDTHS = (-1, 1)


def test_a_value_nearer_the_top_of_a_stretch_goes_up() -> None:
    """The nearer edge, and not always the same one (G6.7.5).

    Withdrawn, every stratum went DOWN and 535 tests stayed green,
    because the twin's OWN ladder still put its cells in two clusters
    and no published count separates "moved down" from "was always
    down". The rule is what keeps a cell near the cluster it was
    drawn beside.
    """
    high = generation._cleared_value(
        _ENDS, _BARRED, _RUN, _EDGES, (_EDGES,), 1900.0, generation._BAND_POSITIVE,
        True, {}, {}, False, _WIDTHS,
    )
    assert high is not None and high >= 2000.0, high
    low = generation._cleared_value(
        _ENDS, _BARRED, _RUN, _EDGES, (_EDGES,), 1600.0, generation._BAND_POSITIVE,
        True, {}, {}, False, _WIDTHS,
    )
    assert low is not None and low < 1500.0, low


def test_the_move_stops_at_the_bin_next_to_the_stretch() -> None:
    """The reach, stated in the fact's own terms (G6.7.5).

    A value moves out of the stretch and into the bin beside it, and
    no further. Ten wide here, so a value sent up lands in [200, 210)
    and one sent down in [90, 100).
    """
    high = generation._cleared_value(
        _ENDS, _BARRED, _RUN, _EDGES, (_EDGES,), 1900.0, generation._BAND_POSITIVE,
        True, {}, {}, False, _WIDTHS,
    )
    assert 2000.0 <= high < 2100.0, high
    low = generation._cleared_value(
        _ENDS, _BARRED, _RUN, _EDGES, (_EDGES,), 1600.0, generation._BAND_POSITIVE,
        True, {}, {}, False, _WIDTHS,
    )
    assert 1400.0 <= low < 1500.0, low


def test_no_two_strata_of_one_stretch_take_one_cell() -> None:
    """The spelling-distinctness rule (G6.7.4, clause 5).

    Two values a thousandth apart are two values and ONE cell. The
    walk is told what is already spoken for and must land on a text
    none of it reads as.
    """
    # A NARROW SCALE, so the walk's own step is finer than the width
    # the cells are written at. That is the whole condition the rule
    # exists for: on the wide scale above, two neighbouring candidates
    # are two different cells anyway and a run that checked only the
    # NUMBERS would pass. Ends 0 to 3.2 make a bin a tenth wide and a
    # step a six-hundred-and-fortieth, so sixteen consecutive
    # candidates all read `2.0` at one figure after the point.
    narrow = (0.0, 3.2)
    # the same stretch on that scale: bins 15 to 19 run 1.5 to 2.0
    edges = (1.5, 2.0)
    first = generation._cleared_value(
        narrow, _BARRED, _RUN, edges, (edges,), 1.94, generation._BAND_POSITIVE,
        True, {}, {}, False, _WIDTHS,
    )
    spoken = {
        spelling: 1
        for spelling in generation._spellings_of(first, _WIDTHS, False)
    }
    second = generation._cleared_value(
        narrow, _BARRED, _RUN, edges, (edges,), 1.94, generation._BAND_POSITIVE,
        True, spoken, {first: 1}, False, _WIDTHS,
    )
    assert second is not None and second != first
    assert not (
        set(generation._spellings_of(second, _WIDTHS, False))
        & set(spoken)
    ), (
        f"the second stratum lands on {second}, which reads back the way "
        f"the first one does at a width the census could reach it at"
    )


def test_a_moved_value_keeps_the_form_it_was_written_in() -> None:
    """The written form is kept (G6.7.4, clause 4).

    `_pool_enough` puts a column's pooled cells on the strata whose
    values carry a point and `_whole_enough` puts the point-free count
    on the ones that do not, so a move that changed which was which
    would take back the count those two just met.
    """
    pointed = generation._cleared_value(
        _ENDS, _BARRED, _RUN, _EDGES, (_EDGES,), 1900.5, generation._BAND_POSITIVE,
        True, {}, {}, False, _WIDTHS,
    )
    assert pointed is not None
    assert not generation._carries_plainly(pointed, False), pointed
    plain = generation._cleared_value(
        _ENDS, _BARRED, _RUN, _EDGES, (_EDGES,), 1900.0, generation._BAND_POSITIVE,
        True, {}, {}, False, _WIDTHS,
    )
    assert plain is not None
    assert generation._carries_plainly(plain, False), plain


def test_a_moved_value_never_crosses_zero() -> None:
    """The sign band (G6.7.4, clause 3).

    A stratum in the negative band whose nearer edge is above zero has
    nowhere to go, and the answer is None -- which the caller turns
    into the deviation that names the stretch -- rather than a positive
    value that would take a cell out of the negative count.
    """
    # THE STRETCH ENDS AT ZERO, so the nearer edge of it for a value
    # just below zero is the bin ABOVE, and the bin above is positive.
    # A stretch whose nearer edge is still negative would pass whether
    # the rule were there or not, which is the shape this test had
    # first and the reason it saw nothing.
    ends = (-100.0, 220.0)
    barred = {place: 1 for place in range(5, 10)}
    found = generation._cleared_value(
        ends, barred, (5, 9), (-50.0, 0.0), ((-50.0, 0.0),), -5.0, generation._BAND_NEGATIVE,
        True, {}, {}, False, (-1, 1),
    )
    assert found is None or found < 0.0, found
    # ...and the mirror, so the test cannot pass by the walk simply
    # failing: a POSITIVE stratum in the same stretch does get a value,
    # and it is above zero.
    other = generation._cleared_value(
        ends, barred, (5, 9), (-50.0, 0.0), ((-50.0, 0.0),), -5.0, generation._BAND_POSITIVE,
        True, {}, {}, False, (-1, 1),
    )
    assert other is not None and other > 0.0, other


def test_a_stratum_in_the_zero_band_is_never_moved(
    tmp_path: pathlib.Path,
) -> None:
    """The zero band (G6.7.4, clause 2), so the count of zeroes stands.

    Driven through the whole pass rather than through `_cleared_value`,
    because the rule lives in the gathering step and not in the walk:
    the zero stratum is never put in a queue at all.
    """
    rows = (
        ["0"] * 40
        + [f"{-90 - (index * 3) % 20}" for index in range(80)]
        + [f"{90 + (index * 3) % 20}" for index in range(80)]
    )
    _document, loaded = _described(tmp_path, "zeroes", rows)
    facts = loaded.columns[0].facts
    assert facts.n_zero == 40
    assert facts.empty_bins, "this column has an empty middle"
    for seed in SEEDS:
        twin = generation.generate(loaded, seed)
        held = [cell for cell in twin.columns[0] if cell == "0"]
        assert len(held) == 40, (
            f"seed {seed} wrote {len(held)} zeroes against a published 40"
        )


def test_a_stratum_is_gathered_by_its_spelling_and_not_only_its_value(
) -> None:
    """The queue reads the SPELLINGS (G6.7.6).

    A value a thousandth outside a stretch is written back inside it at
    the width the fraction census gives that cell, which is exactly the
    defect the walk's own candidate test exists to stop. The gathering
    step had the same hole and this is the rule that closes it: 99.96
    is in bin 9 as a value and reads `100.0` at one figure, which is in
    bin 10 and barred.
    """
    # 1499.96 is in bin 14 as a VALUE and reads `1500.0` at one figure
    # after the point, which is in bin 15 and barred.
    assert parsing.histogram_bin(1499.96, *_ENDS) == 14
    assert generation._barred_bin(
        1499.96, _ENDS, _BARRED, _WIDTHS, False
    ) == 15
    assert not generation._reads_outside(
        1499.96, _ENDS, _BARRED, _WIDTHS, False
    )
    # ...and a value that reads outside at every width is left alone.
    assert generation._barred_bin(
        800.0, _ENDS, _BARRED, _WIDTHS, False
    ) == -1
    assert generation._reads_outside(800.0, _ENDS, _BARRED, _WIDTHS, False)


def test_a_column_whose_values_are_all_one_number_names_no_bin(
    tmp_path: pathlib.Path,
) -> None:
    """The producer and the loader agree that there is no scale.

    THE DEFECT THIS PINS WAS FOUND BY THE SUITE, and it is the shape
    this repository calls one fact written twice. A column whose values
    are all ONE number has two equal ends and no width to divide, and
    `parsing.histogram_bin` is TOTAL: it answers "the first bin" for
    every value. So the count of bins reads `{0: n}` and thirty-one
    bins look empty -- of a division that does not exist. The producer
    named all thirty-one; the loader's own `_has_width` said there was
    no scale and refused the description outright, and every joined
    column with a constant position became unloadable.

    Both sides ask the same question now. The census beside it is
    UNCHANGED -- one bin holding every value -- which is what it read
    before this landing, so nothing here moves a fact that was already
    published.
    """
    # THE WITNESS IS A POSITION INSIDE A JOINED COLUMN, which is where
    # this case arises at all: a whole column of one number is read as
    # a `constant` LABEL and publishes no quantitative block, so the
    # only numeric block that can have two equal ends is one grain of
    # one. `1/2, 1/3, ... 1/121` is the review fixture that found it.
    rows = [f"1/{second}" for second in range(2, 122)]
    # DECLARED as a measurement, which is how the review fixture that
    # found this reaches the joined role: undeclared, a column of
    # `1/2` is read as free text and publishes no numeric block at all.
    path = fixtures.write(
        tmp_path, "constant.csv", fixtures.single_column_table("bp", rows)
    )
    document = profile.build_document(
        reading.read_table(f"{path}"), taxonomy.Settings(), [], [], ["bp"]
    )
    loaded = contract.load_profile(
        str(fixtures.write_profile(tmp_path, "constant-p.json", document))
    )
    block = document["columns"][0]
    assert block["role"] == "joined_numbers", block["role"]
    first = block["parts"][0]
    assert first["value_histogram"] == {"0": 120}, first["value_histogram"]
    assert first["empty_bins"] == [], first["empty_bins"]
    assert loaded.columns[0].facts.parts[0].empty_bins == ()
    # ...and the SECOND position, which does vary, still names its own
    # empty bins if it has any -- so the repair is about the scale and
    # not about the role.
    second = block["parts"][1]
    assert second["value_histogram"], second["value_histogram"]
    # ...and a twin of it still comes back, which is what the joined
    # role's own fixture found when this did not hold: the loader
    # refused the description outright.
    twin = generation.generate(loaded, 3)
    assert len([cell for cell in twin.columns[0] if cell]) == 120
    # AND THE FLOOR AT ITS BOUNDARY, both sides (review round 5 item
    # 6). C6-31f states that a one-value block's census is governed by
    # the floor like any other -- published while its one bin clears
    # it, withheld whole below it -- while BOTH gap keys stay empty at
    # every floor. A `count < floor` written as `count <= floor` would
    # hide the census at 120 and no witness would see it.
    for floor, census in ((1, {"0": 120}), (120, {"0": 120}), (121, {})):
        built = profile.build_document(
            reading.read_table(f"{path}"),
            taxonomy.Settings(small_cell_floor=floor),
            [],
            [],
            ["bp"],
        )
        one = built["columns"][0]["parts"][0]
        assert one["value_histogram"] == census, (floor, one)
        assert one["empty_bins"] == [], (floor, one)
        assert one["empty_edges"] == [], (floor, one)
        # ...and the loader takes every one of them.
        contract.load_profile(
            str(
                fixtures.write_profile(
                    tmp_path, f"constant-{floor}.json", built
                )
            )
        )


def test_the_twins_cells_are_a_function_of_the_published_fact(
    tmp_path: pathlib.Path,
) -> None:
    """THE FACT IS CONSUMED, and this is what that sentence means.

    `value_histogram` is REPORT-ONLY precisely BECAUSE nothing consumes
    it: a comment in `generation.py` says so. A landing that added
    another such key would have changed nothing about any twin. So the
    claim owed here is not "the value stage calls a function" -- it is
    that the twin's own CELLS move when the published fact moves, with
    the code, the column and the seeds all held still.

    One description, taken at a floor of eleven so the census beside it
    is withheld and this fact stands alone. Generated forty times as
    written; then the same document with `empty_bins` emptied and
    nothing else touched, generated forty times again.

    Measured: 0 cells in a named stretch at every one of forty seeds as
    written, and 4 to 6 of 300 with the fact removed.
    """
    rows = _two_tight_rows()
    lowest, highest, barred = _empty_of(rows)
    document, _loaded = _described(tmp_path, "consumed", rows, floor=11)
    assert document["columns"][0]["value_histogram"] == {}, (
        "this witness needs the census withheld, so that what moves "
        "the cells can only be the fact under test"
    )

    def counted(built: "dict", stem: str) -> "list[int]":
        loaded = contract.load_profile(
            str(fixtures.write_profile(tmp_path, stem, built))
        )
        return [
            len(_cells_in(
                generation.generate(loaded, seed),
                lowest,
                highest,
                set(barred),
            ))
            for seed in SEEDS
        ]

    written = counted(document, "consumed-as-written.json")
    blanked = copy.deepcopy(document)
    # BOTH HALVES OF THE FACT, because it is now published as two
    # keys: the bins and the two real values each stretch lies between
    # (residual R-P4-138). Emptying one and leaving the other is a
    # description the loader refuses outright, so the control arm has
    # to remove the whole fact.
    blanked["columns"][0]["empty_bins"] = []
    blanked["columns"][0]["empty_edges"] = []
    without = counted(blanked, "consumed-without.json")
    assert written == [0] * len(SEEDS), written
    assert min(without) >= 4 and max(without) <= 6, without


def test_a_stratum_sharing_its_value_does_not_move() -> None:
    """The sole-holder rule (G6.7.4, clause 6), driven directly.

    Moving costs nothing only when the stratum VACATES what it leaves.
    A stratum sharing its value vacates nothing, so a fresh value adds
    a NUMBER and joining another stratum's value adds a SPELLING. Both
    were measured on the floored witness of review item P3-V7-F4: the
    twin wrote ten different spellings against a published nine and
    `distinct.n_distinct` fell from HELD to an authorized deviation.

    The same call that succeeds for a sole holder must answer None for
    a sharing one, which is what this pins: one argument apart, so the
    test cannot pass because the walk had nowhere to go anyway.
    """
    alone = generation._cleared_value(
        _ENDS, _BARRED, _RUN, _EDGES, (_EDGES,), 1900.0, generation._BAND_POSITIVE,
        True, {}, {}, False, _WIDTHS,
    )
    assert alone is not None
    shared = generation._cleared_value(
        _ENDS, _BARRED, _RUN, _EDGES, (_EDGES,), 1900.0, generation._BAND_POSITIVE,
        False, {}, {}, False, _WIDTHS,
    )
    assert shared is None, shared
