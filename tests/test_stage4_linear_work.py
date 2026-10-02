"""Stage 4, tier 1: four paths whose work grew faster than the table (plan P4-D385).

Each was measured on made-up tables before it was changed, and each
changes no byte of any output -- so each change keeps
the function it replaced as this file's ORACLE, asks both the same
questions over seeded tables, and requires the same answers. Each also
has a growth measure that needs no clock: a count of the work the path
does, taken at N rows and at 2N, whose ratio is about 2 for a path whose
work grows with the rows and about 4 for one whose work grows with their
square. Every growth test takes the measure of the replaced function too
and requires IT to grow as the square, so the measure is known to see
the defect it guards against rather than assumed to.

1. **The end-carrier search** (`generation._shape_choices`). The order
   of the pairs of groups that may carry a free-text or identifier
   column's two published ends was built as a list of every pair -- the
   square of the groups, and an all-different column has one group per
   row: 430 MB to build the twin of 2,000 such rows, 1,220 MB at 4,000,
   and the twin of the health table could not be built at 100,000 rows.
   The searches step over a pair whose two group SIZES were offered
   already, so they are now handed only the first pair of each, and the
   one walk that needs every pair works each one out from its step.
2. **The held-back level lookups** (`taxonomy._levels_read_by_form`,
   `taxonomy._read_the_column`'s level pass, and
   `taxonomy._levels_read_by_class` beside them). Every cell asked a
   LIST of the levels the floor holds back whether its own level was one
   of them, so describing a code register cost its cells times its rare
   codes: 36.2 s at 200,000 rows and 126.6 s at 400,000, measured with
   the rest of the first tier's sketch in place.
3. **The label column** (`generation._label_content`), which was grown
   by copying the column written so far once per level: 16.7 s for the
   twin of the same register at 200,000 rows and 44.0 s at 400,000,
   measured the same way.
4. **The role decision** (`taxonomy._decision`). A column is asked its
   role up to four times over the same tally, and every question walked
   the whole ladder of rules again. The tally now keeps each answer
   under the question it answers, and the memory goes with the tally.
"""

from __future__ import annotations

import ast
import csv
import gc
import inspect
import io
import itertools
import json
import pathlib
import random
import sys
import tempfile
import textwrap
import tracemalloc
import weakref

import pytest

import fixtures
from synthtwin import (
    contract,
    generation,
    parsing,
    profile,
    reading,
    rendering,
    taxonomy,
)

# What a path whose work grows with the rows may grow by when the rows
# double, and what the replaced path must reach to show the measure can
# fail. Linear work doubles; work in the square of the rows quadruples.
LINEAR_AT_MOST = 2.5
SQUARE_AT_LEAST = 3.0


def _table(values: "list[str]") -> str:
    """A one-column table of ``values``, every cell quoted so an edge space survives."""
    out = io.StringIO()
    writer = csv.writer(out, quoting=csv.QUOTE_ALL, lineterminator="\n")
    writer.writerow(["value"])
    for value in values:
        writer.writerow([value])
    return out.getvalue()


def _described(
    folder: pathlib.Path,
    values: "list[str]",
    floor: "int | None" = None,
    declared: "list[str] | None" = None,
) -> contract.Profile:
    """Write ``values`` as a one-column table, describe it with the real producer, load it."""
    folder.mkdir(parents=True, exist_ok=True)
    path = fixtures.write(folder, "table.csv", _table(values))
    settings = (
        taxonomy.Settings()
        if floor is None
        else taxonomy.Settings(small_cell_floor=floor)
    )
    table = reading.read_table(str(path), small_cell_floor=settings.small_cell_floor)
    document = profile.build_document(table, settings, declared or [])
    target = fixtures.write_profile(folder, "table-profile.json", document)
    return contract.load_profile(str(target))


def _twin(loaded: contract.Profile, seed: int) -> "tuple[str, str]":
    """The twin's bytes and its report, as `synthtwin generate` writes them."""
    twin = generation.generate(loaded, seed)
    return rendering.twin_csv(twin), rendering.report(loaded, twin)


def _notes(rows: int, seed: int) -> "list[str]":
    """``rows`` made-up notes, every one different: a column of free text."""
    draw = random.Random(seed)
    words = ("mild", "pain", "since", "left", "stable", "noted", "plan", "recheck")
    return [
        f"{' '.join(draw.choice(words) for _ in range(draw.randrange(3, 7)))} {place}"
        for place in range(rows)
    ]


# -- 1. the end-carrier search ------------------------------------------


def _shape_choices_as_built(total: int) -> "list[tuple[int, int]]":
    """`generation._shape_choices` as 668f276 shipped it: every pair, listed."""
    if total < 2:
        return [(0, 0)]
    return [
        (low, high)
        for low in range(total)
        for high in range(total)
        if high != low
    ]


def _first_of_each_shape(groups: "tuple[int, ...]") -> "list[tuple[int, int]]":
    """The old walk with every pair whose two group sizes were offered left out."""
    offered: "set[tuple[int, int]]" = set()
    kept: "list[tuple[int, int]]" = []
    for carriers in _shape_choices_as_built(len(groups)):
        shape = (groups[carriers[0]], groups[carriers[1]])
        if shape in offered:
            continue
        offered.add(shape)
        kept += [carriers]
    return kept


def test_the_order_worked_out_is_the_order_the_list_held() -> None:
    """Every step of the order is the pair the old list held at that place."""
    for total in range(41):
        worked = [
            generation._shape_choice_at(total, step)
            for step in range(generation._shape_choice_count(total))
        ]
        assert worked == _shape_choices_as_built(total), total


def test_one_pair_per_shape_is_the_old_walk_without_its_repeats() -> None:
    """The searches are handed exactly the pairs the old walk did not step over.

    Over 3,000 seeded tuples of group sizes, in the ascending order
    `generation._groups_of` builds and in no order at all, and with few
    sizes and many.
    """
    draw = random.Random(385)
    for case in range(3000):
        sizes = (1, 1, 2, 3) if case % 3 else (1, 2, 2, 3, 4, 5, 8, 13, 21)
        groups = tuple(draw.choice(sizes) for _ in range(draw.randrange(1, 41)))
        if case % 2:
            groups = tuple(sorted(groups))
        assert generation._shape_choices(groups) == _first_of_each_shape(groups), groups


# The free-text values of the text-shape battery (review item P2-C4-F2),
# whose three-value columns reach several group sizes at once.
_TEXT_POOL = (
    "7", "42", "913", "5.5", "ab", "q_z", "x!", "no!!", "a b", "one two",
    "x", "!!", "z9", "-3",
)


def _shape_battery() -> "list[tuple[list[str], int, list[str]]]":
    """Free-text and record-number columns whose end-carrier search steps over shapes."""
    import test_ap312_fold_repair as fold

    cases: "list[tuple[list[str], int, list[str]]]" = []
    for step, trio in enumerate(itertools.combinations(_TEXT_POOL, 3)):
        if step % 7:
            continue
        for pattern in ((1, 5, 6), (2, 2, 8), (1, 2, 3)):
            values: "list[str]" = []
            for place in range(3):
                values += [trio[place]] * pattern[place]
            cases += [(values, 1, [])]
    draw = random.Random(3851)
    for _case in range(20):
        values = []
        for place in range(draw.randrange(8, 20)):
            words = draw.choice(("a b", "one two", "x!", "q_z", "no!!"))
            values += [f"{words} {place}"] * draw.choice((1, 1, 2, 3))
        draw.shuffle(values)
        cases += [(values, 1, [])]
    for seed in range(4):
        cases += [(fold._a_column(seed), 1, ["value"])]
    for _shape, values in fold.WITNESSES:
        cases += [(list(values), 1, ["value"])]
    return cases


def test_the_searches_give_what_the_whole_order_gave(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Handed the old list of every pair, every search answers as it does now.

    Each search steps over a pair whose shape was offered, so handing it
    the old list IS the old search. The twin's bytes and its report are
    required equal, over free-text columns and declared record numbers
    -- the fold repair's own battery among them. That repair's second
    tier works each pair out from its step and is not handed this list,
    so the patch does not reach it: the order test above holds that tier
    to the old order. The search draws nothing, so one seed asks it all.
    """
    reached = {"text": 0, "identifier": 0}
    for step, (values, floor, declared) in enumerate(_shape_battery()):
        loaded = _described(tmp_path / f"case-{step}", values, floor, declared)
        facts = loaded.columns[0].facts
        if isinstance(facts, contract.TextFacts):
            reached["text"] += 1
        elif isinstance(facts, contract.IdentifierFacts):
            reached["identifier"] += 1
        else:
            continue
        shipped = _twin(loaded, 3)
        with monkeypatch.context() as patch:
            patch.setattr(
                generation,
                "_shape_choices",
                lambda groups: _shape_choices_as_built(len(groups)),
            )
            as_built = _twin(loaded, 3)
        assert shipped == as_built, values
    assert reached["text"] >= 120 and reached["identifier"] >= 10, reached


def shape_pairs_handed(rows: int, as_built: bool = False) -> int:
    """How many end-carrier pairs the searches are handed for two all-different columns.

    One column of free text and one declared column of record numbers,
    each of ``rows`` different values, are described and their twin is
    built; every pair `generation._shape_choices` hands a search is
    counted. With ``as_built`` the searches are handed the old list.
    """
    handed = [0]
    shipped = generation._shape_choices

    def counted(groups: "tuple[int, ...]") -> "list[tuple[int, int]]":
        pairs = (
            _shape_choices_as_built(len(groups)) if as_built else shipped(groups)
        )
        handed[0] += len(pairs)
        return pairs

    with tempfile.TemporaryDirectory() as home:
        folder = pathlib.Path(home)
        notes = _described(folder / "notes", _notes(rows, rows))
        assert isinstance(notes.columns[0].facts, contract.TextFacts)
        numbers = _described(
            folder / "numbers",
            [f"E{(place * 7919) % 1000003:07d}" for place in range(rows)],
            declared=["value"],
        )
        assert isinstance(numbers.columns[0].facts, contract.IdentifierFacts)
        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(generation, "_shape_choices", counted)
            generation.generate(notes, 0)
            generation.generate(numbers, 0)
    return handed[0]


def test_the_end_carrier_search_is_handed_no_more_pairs_as_the_rows_double() -> None:
    """Pairs handed at 2N rows against N: about one now, and four as built."""
    small, large = shape_pairs_handed(250), shape_pairs_handed(500)
    assert large / small < LINEAR_AT_MOST, (small, large)
    old_small = shape_pairs_handed(250, as_built=True)
    old_large = shape_pairs_handed(500, as_built=True)
    assert old_large / old_small >= SQUARE_AT_LEAST, (old_small, old_large)


# -- 2. the held-back level lookups --------------------------------------


def _levels_read_by_class_as_built(
    cells: "taxonomy._Cells", role: str, rare: "list[str]", smallest: int
) -> "tuple[str, ...]":
    """`taxonomy._levels_read_by_class` as 668f276 shipped it, its docstring aside."""
    if not rare or smallest < 0:
        return ()
    population = cells.classified
    if role == taxonomy.ROLE_COMPOUND:
        compound = taxonomy._compound_reading(cells)
        if compound is None:
            return ()
        population = compound.labels
    by_class: "dict[str, str]" = {}
    counts: "dict[str, int]" = {}
    totals: "dict[str, int]" = {}
    for cell in population:
        key = cell.folded
        counts[key] = (counts[key] if key in counts else 0) + 1
        totals[cell.kind] = (totals[cell.kind] if cell.kind in totals else 0) + 1
        if key in by_class and by_class[key] != cell.kind:
            by_class[key] = taxonomy._CLASS_MIXED
            continue
        by_class[key] = cell.kind
    held: "dict[str, list[str]]" = {}
    for label in rare:
        if label not in by_class:
            continue
        kind = by_class[label]
        held[kind] = (held[kind] if kind in held else []) + [label]
    counted_out: "list[str]" = []
    for kind in taxonomy._READING_CLASSES:
        if kind not in held:
            continue
        total = totals[kind] if kind in totals else 0
        rows = 0
        for label in held[kind]:
            rows = rows + counts[label]
        covered = total - rows
        if parsing.census_names_one_row({kind: rows}, [(total, covered)]) != -1:
            counted_out += held[kind]
    return tuple(sorted(counted_out))


def _levels_read_by_form_as_built(
    cells: "taxonomy._Cells", role: str, rare: "list[str]"
) -> "tuple[str, ...]":
    """`taxonomy._levels_read_by_form` as 668f276 shipped it, its docstring aside."""
    if not rare:
        return ()
    population = cells
    with_text_total = True
    if role == taxonomy.ROLE_COMPOUND:
        compound = taxonomy._compound_reading(cells)
        if compound is None:
            return ()
        population = taxonomy._tally(
            taxonomy._classify_all(
                [cell.text for cell in compound.labels], cells.decimal_comma
            ),
            len(compound.labels),
            cells.settings,
            cells.decimal_comma,
        )
        with_text_total = False
    elif role not in taxonomy._LEVEL_ROLES:
        return ()
    spelled = taxonomy.described_spellings(population.present, population.settings)
    census = taxonomy._shape_forms(population, False, with_text_total, spelled)
    held: "dict[str, list[str]]" = {}
    rows: "dict[str, int]" = {}
    covered: "dict[str, int]" = {}
    for value in spelled:
        form = taxonomy._census_key_of(value, census)
        if not form:
            continue
        key = parsing.folded(value)
        if key not in rare:
            covered[form] = (covered[form] if form in covered else 0) + 1
            continue
        rows[form] = (rows[form] if form in rows else 0) + 1
        named = held[form] if form in held else []
        held[form] = named if key in named else named + [key]
    counted_out: "list[str]" = []
    for form in sorted(census):
        if form not in held:
            continue
        seen = covered[form] if form in covered else 0
        if parsing.census_names_one_row(
            {form: rows[form]}, [(census[form], seen)]
        ) != -1:
            counted_out += held[form]
    return tuple(sorted(counted_out))


def _read_the_column_as_built() -> "tuple[object, dict]":
    """`taxonomy._read_the_column` with its level pass walking the sorted list again.

    Rebuilt from the shipped function's own source rather than copied
    beside it: the one lookup of the level pass asks the sorted tuple
    `counted_out` again, as 668f276 asked it, and nothing else moves --
    which the rewrite counts. Returns the function and the copy of the
    module's names it runs in, so a measure can replace one of them.
    """
    tree = ast.parse(textwrap.dedent(inspect.getsource(taxonomy._read_the_column)))
    walked = [0]

    class Walked(ast.NodeTransformer):
        def visit_Compare(self, node: ast.Compare) -> ast.Compare:
            self.generic_visit(node)
            if (
                len(node.ops) == 1
                and isinstance(node.ops[0], ast.In)
                and isinstance(node.comparators[0], ast.Name)
                and node.comparators[0].id == "counted_keys"
            ):
                walked[0] += 1
                node.comparators[0] = ast.Name("counted_out", ast.Load())
            return node

    tree = ast.fix_missing_locations(Walked().visit(tree))
    assert walked[0] == 1, "the level pass's one lookup was not found"
    names = dict(vars(taxonomy))
    exec(compile(tree, "<_read_the_column as built>", "exec"), names)
    return names["_read_the_column"], names


def _register(rows: int, seed: int, codes: int, held_rows: "tuple[int, ...]") -> "list[str]":
    """A made-up code register: common codes in several written forms, and rare ones."""
    draw = random.Random(seed)
    forms = ("C%03d", "AB-%03d", "X%d.%d", "%05d")
    values: "list[str]" = []
    for place in range(codes):
        form = forms[place % len(forms)]
        code = form % ((place, place % 7) if form.count("%") == 2 else (place,))
        values += [code] * draw.randrange(12, 60)
    while len(values) < rows:
        place = draw.randrange(10**4)
        form = forms[place % len(forms)]
        code = form % ((place, place % 9) if form.count("%") == 2 else (place + 500,))
        values += [code] * draw.choice(held_rows)
    draw.shuffle(values)
    return values[:rows]


def _level_battery() -> "list[tuple[list[str], int]]":
    """Label columns whose floor holds levels back: named witnesses, then seeded registers."""
    cases: "list[tuple[list[str], int]]" = [
        # The form pass's own witness (round 2 of the review): 201 less
        # 100 less 100 is one held-back row wearing a published form.
        (["ABC-100"] * 100 + ["ABC-200"] * 100 + ["ABC-300"] + ["QQ-400"] * 5
         + ["RR-500"] * 6, 11),
        # The class pass's witnesses (plan P4-D261): one row reading as a
        # number, out of range, or contradictory beside two words.
        (["alpha"] * 100 + ["beta"] * 100 + ["7"], 11),
        (["alpha"] * 100 + ["beta"] * 100 + ["1e999"], 11),
        (["alpha"] * 100 + ["beta"] * 100 + ["(+5)"], 11),
        # A lone level beside two common ones (the owner's ruling of
        # 2026-09-17, item 5).
        (["F"] * 480 + ["M"] * 519 + ["U"], 11),
        # Readings beside words (numbers with labels).
        ([f"{1 + (place % 97) / 10:.1f}" for place in range(296)]
         + ["NOT DETECTED"] * 13 + ["trace"] * 2, 11),
    ]
    for seed in range(10):
        for floor in (11, 36):
            cases += [(_register(400 + 90 * seed, seed, 6 + seed, (1, 1, 2, 3, 5)), floor)]
    # Registers whose codes written once are counted out by the level
    # pass: their pool is smaller than the published rows, and fewer than
    # twice its levels.
    for rows in (400, 800, 1600):
        cases += [(_counted_out_register(rows), 11)]
    cases += [(_register(900, 11, 12, (1,)), 11)]
    return cases


def test_the_held_back_levels_are_counted_out_as_the_lists_counted_them() -> None:
    """The form and class passes give what 668f276's list walks gave, role by role."""
    nonempty = 0
    for values, floor in _level_battery():
        settings = taxonomy.Settings(small_cell_floor=floor)
        tally = taxonomy._tally(taxonomy._classify_all(values), len(values), settings)
        counts = tally.folded_counts
        rare = sorted(label for label in counts if counts[label] < floor)
        published = [counts[label] for label in counts if counts[label] >= floor]
        smallest = min(published) if published else 0
        roles = (taxonomy._decide(tally, False).role,) + tuple(taxonomy._LEVEL_ROLES) + (
            taxonomy.ROLE_COMPOUND,
        )
        for role in roles:
            by_form = taxonomy._levels_read_by_form(tally, role, rare)
            assert by_form == _levels_read_by_form_as_built(tally, role, rare), (role, values[:5])
            by_class = taxonomy._levels_read_by_class(tally, role, rare, smallest)
            assert by_class == _levels_read_by_class_as_built(
                tally, role, rare, smallest
            ), (role, values[:5])
            nonempty += bool(by_form) + bool(by_class)
    assert nonempty >= 10, f"only {nonempty} answers named a level: the battery proves little"


def test_the_level_pass_reads_what_the_list_walk_read() -> None:
    """`_read_the_column` gives the reading 668f276's level pass gave, field for field."""
    as_built, _names = _read_the_column_as_built()
    removed = 0
    for values, floor in _level_battery():
        settings = taxonomy.Settings(small_cell_floor=floor)
        shipped = taxonomy._read_the_column(values, len(values), settings)
        assert shipped == as_built(values, len(values), settings), values[:5]
        removed += len(values) - len(shipped.present)
    assert removed >= 100, f"the level pass removed {removed} cells: the battery proves little"


class _Counted(str):
    """A level whose every equality test is counted: the work of looking it up."""

    __hash__ = str.__hash__

    def __eq__(self, other: object) -> bool:
        _COMPARED[0] += 1
        return str.__eq__(self, other)


_COMPARED = [0]


def _counted_out_register(rows: int) -> "list[str]":
    """Twenty common codes over three quarters of the rows, and a quarter written once each."""
    draw = random.Random(rows)
    values: "list[str]" = []
    for place in range(20):
        values += [f"C{place:03d}"] * (3 * rows // 80)
    values += [f"R{place:05d}" for place in range(rows // 4)]
    draw.shuffle(values)
    return values


def held_back_lookups(rows: int, as_built: bool = False) -> int:
    """How many times a held-back level is compared with a cell's while one register is read.

    A register of ``rows`` rows -- a quarter of them codes written once,
    which the floor holds back and the level pass counts out -- is asked
    the form pass and then read whole; every held-back level is a
    `_Counted`, so each equality test against one is counted, whatever
    asks it. With ``as_built`` the form pass and the level pass walk
    their lists as 668f276 walked them.
    """
    values = _counted_out_register(rows)
    settings = taxonomy.Settings()
    tally = taxonomy._tally(taxonomy._classify_all(values), len(values), settings)
    role = taxonomy._decide(tally, False).role
    rare = [
        _Counted(label)
        for label in sorted(tally.folded_counts)
        if tally.folded_counts[label] < settings.small_cell_floor
    ]
    by_form = _levels_read_by_form_as_built if as_built else taxonomy._levels_read_by_form
    reader, names = (
        _read_the_column_as_built() if as_built else (taxonomy._read_the_column, None)
    )
    shipped = taxonomy._levels_read_by_subtraction

    def counted(cells: "taxonomy._Cells", asked: str) -> "tuple[str, ...]":
        return tuple(_Counted(label) for label in shipped(cells, asked))

    _COMPARED[0] = 0
    by_form(tally, role, rare)
    with pytest.MonkeyPatch.context() as patch:
        if names is None:
            patch.setattr(taxonomy, "_levels_read_by_subtraction", counted)
        else:
            patch.setitem(names, "_levels_read_by_subtraction", counted)
        reading_of = reader(values, len(values), settings)
    assert len(reading_of.present) == len(values) - rows // 4, "the level pass did not run"
    return _COMPARED[0]


def test_the_held_back_lookups_grow_with_the_rows_and_not_their_square() -> None:
    """Comparisons at 2N rows against N: about two now, and four as built."""
    small, large = held_back_lookups(1000), held_back_lookups(2000)
    assert large / small < LINEAR_AT_MOST, (small, large)
    old_small = held_back_lookups(1000, as_built=True)
    old_large = held_back_lookups(2000, as_built=True)
    assert old_large / old_small >= SQUARE_AT_LEAST, (old_small, old_large)


# -- 3. the label column -------------------------------------------------


def _label_content_as_built() -> "object":
    """`generation._label_content` growing its column by copying it, as 668f276 grew it.

    Rebuilt from the shipped function's own source rather than copied
    beside it: each `cells += [...]` becomes the `cells = cells + [...]`
    668f276 wrote, and the one copy the shipped function takes before
    its last loop goes, so the two differ by exactly this landing's
    change -- which the rewrite counts.
    """
    tree = ast.parse(textwrap.dedent(inspect.getsource(generation._label_content)))
    found = {"grown": 0, "copied": 0}

    class Copied(ast.NodeTransformer):
        def visit_AugAssign(self, node: ast.AugAssign) -> ast.AST:
            if (
                isinstance(node.target, ast.Name)
                and node.target.id == "cells"
                and isinstance(node.op, ast.Add)
            ):
                found["grown"] += 1
                return ast.copy_location(
                    ast.Assign(
                        targets=[ast.Name("cells", ast.Store())],
                        value=ast.BinOp(ast.Name("cells", ast.Load()), ast.Add(), node.value),
                    ),
                    node,
                )
            return node

        def visit_Assign(self, node: ast.Assign) -> "ast.AST | None":
            value = node.value
            if (
                len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == "cells"
                and isinstance(value, ast.Call)
                and isinstance(value.func, ast.Name)
                and value.func.id == "list"
            ):
                found["copied"] += 1
                return None
            return node

    tree = ast.fix_missing_locations(Copied().visit(tree))
    assert found == {"grown": 4, "copied": 1}, found
    names = dict(vars(generation))
    exec(compile(tree, "<_label_content as built>", "exec"), names)
    return names["_label_content"]


def _label_columns() -> "list[tuple[list[str], int]]":
    """Label columns of every kind `_label_content` writes, at three floors."""
    cases: "list[tuple[list[str], int]]" = []
    for seed in range(6):
        draw = random.Random(9385 + seed)
        values: "list[str]" = []
        for place in range(draw.randrange(8, 30)):
            label = draw.choice(("Clinic", "ward", "Unit-", "Bay ", "12", "4.5"))
            values += [f"{label}{place}"] * draw.randrange(1, 40)
            if place % 5 == 0:
                # Spellings of one label: case, and an edge space.
                values += [f"{label}{place}".upper()] * draw.randrange(1, 4)
                values += [f"{label}{place} "] * draw.randrange(1, 3)
        draw.shuffle(values)
        for floor in (1, 11, 36):
            cases += [(values, floor)]
    cases += [(_register(1200, 7, 9, (2, 3, 4, 5, 6)), 11)]
    cases += [(["F"] * 480 + ["M"] * 519 + ["U"], 11)]
    cases += [([f"{place % 23}" for place in range(300)] + ["n/a lab"] * 30 + ["pending"] * 4, 11)]
    return cases


def test_the_label_column_grown_in_place_is_the_column_grown_by_copying(
    tmp_path: pathlib.Path,
) -> None:
    """Every label column `_label_content` writes is the column 668f276 wrote, and its notes."""
    as_built = _label_content_as_built()
    reached = 0
    for step, (values, floor) in enumerate(_label_columns()):
        loaded = _described(tmp_path / f"labels-{step}", values, floor)
        plan = generation.plan_generation(loaded)
        for column_plan in plan.columns:
            if not isinstance(column_plan.column.facts, contract.LabelFacts):
                continue
            reached += 1
            short_now: "list[int]" = []
            short_then: "list[int]" = []
            assert generation._label_content(column_plan, short_now) == as_built(
                column_plan, short_then
            ), values[:5]
            assert short_now == short_then
    assert reached >= 15, reached


def _allocated_by_lines(function: "object", *arguments: object) -> int:
    """The bytes ``function``'s own lines allocate above what each line found, summed.

    A line that copies a list of n items allocates n more pointers while
    the old list is still held; a line that grows one in place allocates
    what it adds. Read off `tracemalloc`'s peak, which is taken and reset
    at every line of the function's own frame, so no clock plays a part.
    """
    code = function.__code__  # type: ignore[attr-defined]
    total = [0]
    since = [0]

    def local(frame: object, event: str, argument: object) -> object:
        if event in ("line", "return"):
            peak = tracemalloc.get_traced_memory()[1]
            total[0] += max(0, peak - since[0])
            tracemalloc.reset_peak()
            since[0] = tracemalloc.get_traced_memory()[0]
        return local

    def calls(frame: object, event: str, argument: object) -> object:
        if event == "call" and frame.f_code is code:  # type: ignore[attr-defined]
            return local
        return None

    tracing = tracemalloc.is_tracing()
    if not tracing:
        tracemalloc.start()
    previous = sys.gettrace()
    try:
        tracemalloc.reset_peak()
        since[0] = tracemalloc.get_traced_memory()[0]
        sys.settrace(calls)  # type: ignore[arg-type]
        try:
            function(*arguments)  # type: ignore[operator]
        finally:
            sys.settrace(previous)
    finally:
        if not tracing:
            tracemalloc.stop()
    return total[0]


def _label_register(rows: int) -> "list[str]":
    """Half the rows over published codes of twenty rows, half over codes of four the floor holds back."""
    draw = random.Random(rows + 1)
    values: "list[str]" = []
    for place in range(rows // 40):
        values += [f"P{place:05d}"] * 20
    for place in range(rows // 8):
        values += [f"H{place:05d}"] * 4
    draw.shuffle(values)
    return values


def label_bytes(rows: int, as_built: bool = False) -> int:
    """The bytes `_label_content`'s lines allocate writing one label column of ``rows``.

    With ``as_built`` the column is grown by copying, as 668f276 grew it.
    """
    function = _label_content_as_built() if as_built else generation._label_content
    with tempfile.TemporaryDirectory() as home:
        loaded = _described(pathlib.Path(home), _label_register(rows))
    column_plan = generation.plan_generation(loaded).columns[0]
    facts = column_plan.column.facts
    assert isinstance(facts, contract.LabelFacts) and facts.suppressed_levels, facts
    return _allocated_by_lines(function, column_plan)


def test_the_label_column_is_built_with_work_that_grows_with_its_rows() -> None:
    """Bytes allocated at 2N rows against N: about two now, and over three as built."""
    small, large = label_bytes(3000), label_bytes(6000)
    assert large / small < LINEAR_AT_MOST, (small, large)
    old_small = label_bytes(3000, as_built=True)
    old_large = label_bytes(6000, as_built=True)
    assert old_large / old_small >= SQUARE_AT_LEAST, (old_small, old_large)


# -- 4. the role decision ------------------------------------------------


def _mixed_table(rows: int) -> str:
    """A made-up table whose columns reach every pass that asks a role again."""
    draw = random.Random(4385 + rows)
    header = [
        "glucose", "admitted", "dose", "band", "result", "clinic",
        "note", "visit", "charge",
    ]
    body: "list[list[str]]" = []
    for place in range(rows):
        glucose = "-999" if place % 23 == 0 else str(70 + draw.randrange(90))
        admitted = (
            "9999-12-31" if place % 19 == 0
            else f"2024-{1 + place % 12:02d}-{1 + place % 28:02d}"
        )
        dose = "-999 mg" if place % 17 == 0 else f"{1 + draw.randrange(10)} mg"
        band = "Z" if place == 7 else ("A" if place % 2 else "B")
        result = (
            "NOT DETECTED" if place % 29 == 0
            else f"{draw.randrange(10, 400) / 10:.1f}"
        )
        clinic = f"C{place % 6}" if place % 50 else f"R{place:05d}"
        note = f"seen today {draw.randrange(10**6)}"
        visit = f"V{place:06d}"
        charge = f"{draw.randrange(100, 99999)},{draw.randrange(100):02d}"
        body += [[glucose, admitted, dose, band, result, clinic, note, visit, charge]]
    return fixtures.rows_to_csv(header, body)


def _described_table(
    folder: pathlib.Path,
    text: str,
    floor: int = 11,
    declared: "tuple[str, ...]" = (),
    codes: "tuple[str, ...]" = (),
) -> "dict":
    """The description of a written table, with the record numbers and codes named declared."""
    folder.mkdir(parents=True, exist_ok=True)
    path = fixtures.write(folder, "table.csv", text)
    settings = taxonomy.Settings(small_cell_floor=floor)
    table = reading.read_table(str(path), small_cell_floor=floor)
    return profile.build_document(table, settings, list(declared), list(codes))


def test_every_remembered_role_is_the_role_the_ladder_gives(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Each answer `_decision` hands back equals `_decide` walked afresh, at every call.

    And the description built with the memory is the description built
    without it, at two floors.
    """
    remembered = taxonomy._decision
    asked = [0]

    def checked(cells: "taxonomy._Cells", *arguments: object, **named: object) -> object:
        verdict = remembered(cells, *arguments, **named)  # type: ignore[arg-type]
        assert verdict == taxonomy._decide(cells, *arguments, **named)  # type: ignore[arg-type]
        asked[0] += 1
        return verdict

    for floor in (1, 11):
        text = _mixed_table(600)
        with monkeypatch.context() as patch:
            patch.setattr(taxonomy, "_decision", checked)
            kept = _described_table(
                tmp_path / f"kept-{floor}", text, floor, ("visit",), ("clinic",)
            )
        with monkeypatch.context() as patch:
            patch.setattr(
                taxonomy,
                "_decision",
                lambda cells, *arguments, **named: taxonomy._decide(cells, *arguments, **named),
            )
            walked = _described_table(
                tmp_path / f"walked-{floor}", text, floor, ("visit",), ("clinic",)
            )
        assert json.dumps(kept, sort_keys=True) == json.dumps(walked, sort_keys=True)
    assert asked[0] >= 40, asked[0]


def _plain_table(rows: int) -> str:
    """A made-up table whose columns no pass takes a cell out of: each keeps one tally."""
    draw = random.Random(5385 + rows)
    header = ["glucose", "admitted", "band", "clinic", "note", "charge", "arrival"]
    body: "list[list[str]]" = []
    for place in range(rows):
        body += [[
            str(70 + draw.randrange(90)),
            f"2024-{1 + place % 12:02d}-{1 + place % 28:02d}",
            "Z" if place == 7 else ("A" if place % 2 else "B"),
            f"C{place % 6}",
            f"seen today {draw.randrange(10**6)}",
            f"{draw.randrange(1, 99)},{draw.randrange(1000):03d}.{draw.randrange(100):02d}",
            f"{draw.randrange(24):02d}:{draw.randrange(60):02d}",
        ]]
    return fixtures.rows_to_csv(header, body)


def test_each_question_of_one_tally_is_remembered_under_its_own_arguments() -> None:
    """Two questions of one tally get two answers, each the ladder's own.

    No pass asks one tally two questions today -- a pass that takes cells
    out builds a new tally -- so this asks them directly: a column of
    labels decided as it stands, declared a record number, and declared
    a code, each asked twice.
    """
    values = ["ward 1"] * 40 + ["ward 2"] * 35 + ["14"] * 30 + ["9"] * 25
    tally = taxonomy._tally(taxonomy._classify_all(values), len(values), taxonomy.Settings())
    questions = (
        ((False,), {}),
        ((True,), {}),
        ((False,), {"forced_code": True}),
    )
    roles = []
    for _again in range(2):
        for arguments, named in questions:
            verdict = taxonomy._decision(tally, *arguments, **named)
            assert verdict == taxonomy._decide(tally, *arguments, **named), (arguments, named)
            roles += [verdict.role]
    assert len(set(roles)) >= 2, roles
    assert len(tally.decided) == len(questions)


def role_walks(rows: int, as_built: bool = False) -> "tuple[int, int, int]":
    """How often the ladder of role rules is walked while one made-up table is described.

    Returns the walks, the different questions they answered -- one
    tally asked under one set of arguments -- and the columns. With
    ``as_built`` every caller walks the ladder itself, as 668f276's did.
    """
    walks = [0]
    questions: "dict[tuple[int, tuple[object, ...]], int]" = {}
    held: "list[object]" = []
    ladder = taxonomy._decide
    signature = inspect.signature(ladder)

    def watched(cells: "taxonomy._Cells", *arguments: object, **named: object) -> object:
        walks[0] += 1
        held.append(cells)  # alive, so no id is reused while counting
        bound = signature.bind(cells, *arguments, **named)
        bound.apply_defaults()
        asked = tuple(bound.arguments[name] for name in list(bound.arguments)[1:])
        questions[(id(cells), asked)] = 1
        return ladder(cells, *arguments, **named)  # type: ignore[arg-type]

    with tempfile.TemporaryDirectory() as home, pytest.MonkeyPatch.context() as patch:
        patch.setattr(taxonomy, "_decide", watched)
        if as_built:
            patch.setattr(
                taxonomy,
                "_decision",
                lambda cells, *arguments, **named: taxonomy._decide(cells, *arguments, **named),
            )
        document = _described_table(pathlib.Path(home), _plain_table(rows))
    return walks[0], len(questions), len(document["columns"])


def test_no_column_walks_the_ladder_twice_for_one_question() -> None:
    """One walk per question at N rows and at 2N, and about three as built.

    A question is one tally asked under one set of arguments, its
    defaults filled in. A column whose level pass takes a lone level out
    asks a second question of a second tally, so there are a few more
    questions than columns.
    """
    for rows in (500, 1000):
        walks, questions, columns = role_walks(rows)
        assert walks == questions <= 2 * columns, (rows, walks, questions, columns)
    old_walks, old_questions, _columns = role_walks(500, as_built=True)
    assert old_walks >= 2.5 * old_questions, (old_walks, old_questions)


def test_the_memory_goes_with_its_column(monkeypatch: pytest.MonkeyPatch) -> None:
    """No tally a role was decided for outlives the description of its column.

    A memory kept beside the module, as the first sketch of this change
    kept it, held the last four tallies alive -- about 0.7 GB for each
    all-different column of 2,000,000 rows -- into the next column and
    into generation.
    """
    tallies: "list[weakref.ref]" = []
    ladder = taxonomy._decide

    def watched(cells: "taxonomy._Cells", *arguments: object, **named: object) -> object:
        tallies.append(weakref.ref(cells))
        return ladder(cells, *arguments, **named)  # type: ignore[arg-type]

    monkeypatch.setattr(taxonomy, "_decide", watched)
    values = _notes(300, 5) + ["-999"] * 20
    block = taxonomy.profile_column("note", 1, values, len(values), taxonomy.Settings())
    del block
    gc.collect()
    assert tallies, "no role was decided"
    assert all(ref() is None for ref in tallies), "a tally outlived its column"


def test_the_census_keeps_no_remembered_role() -> None:
    """The reading the census keeps holds no verdict until the description ends.

    `profile_column` is handed that reading as a new tally, which starts
    with nothing remembered, so what the census's own tally was decided
    as is never read again. Kept, it was measured at about 75 bytes a
    row of a date column, held after every column.
    """
    values = [f"2023-{1 + i % 12:02d}-{1 + i % 28:02d}" for i in range(400)] + ["9999-12-31"] * 5
    kept, _held = taxonomy._census_reading(
        values, taxonomy.Settings(), False, False, False, False, ()
    )
    assert kept.reading.cells.decided == {}


def test_every_argument_of_the_ladder_is_part_of_the_question() -> None:
    """Each argument `_decide` takes keys the memory, so no stale role is handed back.

    One tally is asked the plain question and then each argument
    changed alone, with the identifier declared and not: every answer
    is the ladder's own, and every question is remembered apart.
    """
    ladder = list(inspect.signature(taxonomy._decide).parameters)
    assert ladder == list(inspect.signature(taxonomy._decision).parameters)
    values = ["ward 1"] * 40 + ["ward 2"] * 35 + ["14"] * 30 + ["9"] * 25
    tally = taxonomy._tally(taxonomy._classify_all(values), len(values), taxonomy.Settings())
    flips: "dict[str, object]" = {
        "removed": 1,
        "after_removal": True,
        "after_days": True,
        "after_levels": True,
        "forced_code": True,
        "forced_measurement": True,
        "probing": True,
        "described_as_pair": True,
    }
    assert sorted(flips) == sorted(ladder[2:])
    asked = 0
    for forced in (False, True):
        for name in [""] + sorted(flips):
            named = {name: flips[name]} if name else {}
            verdict = taxonomy._decision(tally, forced, **named)  # type: ignore[arg-type]
            asked += 1
            assert verdict == taxonomy._decide(tally, forced, **named)  # type: ignore[arg-type]
            assert len(tally.decided) == asked, (forced, name)
