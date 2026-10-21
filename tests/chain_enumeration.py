"""K-S6-08's tables part: every description the chain's draw can publish, and its preimage, enumerated (plan P4-D418).

WHAT IS COUNTED. On small fixtures at the floor of 11, never a scaled-down
one, every whole-number table of the fixture's size is enumerated, every
description the procedure of contract 4.6b can publish from it is listed
(every ELIGIBLE option of every step, the draw's full support, 4.6b.4),
and a description's PREIMAGE is every table from which some draw publishes
it. A count LEAKS where, over the whole preimage of a description, it lies
inside 1 to 10, fixed or bounded (rulings R1 and R3). A union that is a
count of one column alone (a function of its own published facts) is
accepted within one column (plan P4-D363) and skipped.

WHAT DECIDES ELIGIBILITY. The product's own rules (`chain_rules`: RULES
W3 and NE's offered levels, the floor, RULE W1 in full, the score), in an
option model of three binary columns that mirrors the producer's search
(`chain._root_options`, `chain._step_options`); `mirror_agrees` checks the
mirror against the producer itself, option by option, on sampled tables.

THE FIXTURES (BC-ARCH 2.7, as lane CHa stamps them):
- the margin-set scan: three binary columns, n from 100 to 124, one-way
  totals of each margin set at least 2f (the design's `n3d.py` sets);
- RULE W1's part C, recast as a filter (`w1_recast.py`): a day count with
  `n_zero` 6 inside its lowest band beside a post-op flag; the mutant is
  the version 2.2 merge;
- the two-keys pairs: two descriptions of ONE table (a stated limit,
  reported and never passed);
- different names: two tables under different names draw independent
  words, so the pair's preimage is the product of the two single preimages
  and leaks exactly where a single description does (passed at 0).
"""

import itertools

from synthtwin import chain_rules as rules

F = 11

# A cell of three binary columns (a, b, c) is a*4 + b*2 + c.
CELLS = [(a, b, c) for a in (0, 1) for b in (0, 1) for c in (0, 1)]


def binary_scale(name: str, low: int, high: int) -> rules.Ladder:
    """A binary column's ladder: its two levels at every level."""
    return rules.Ladder(name, ((("0",),), (("1",),)), ((0, 1), (0, 1), (0, 1)), (2, 2, 2), (low, high), (True, True))


def tables_with_margins(n: int, a1: int, b1: int, c1: int) -> "list[tuple[int, ...]]":
    """Every 2 x 2 x 2 table of whole numbers with these one-way totals of the value 1."""
    out: "list[tuple[int, ...]]" = []
    for t111 in range(0, min(a1, b1, c1) + 1):
        for t110 in range(0, min(a1, b1) - t111 + 1):
            for t101 in range(0, min(a1 - t111 - t110, c1 - t111) + 1):
                t100 = a1 - t111 - t110 - t101
                if t100 < 0:
                    continue
                for t011 in range(0, min(b1 - t111 - t110, c1 - t111 - t101) + 1):
                    t010 = b1 - t111 - t110 - t011
                    t001 = c1 - t111 - t101 - t011
                    if t010 < 0 or t001 < 0:
                        continue
                    t000 = n - (t100 + t101 + t110 + t111 + t010 + t011 + t001)
                    if t000 < 0:
                        continue
                    out += [(t000, t001, t010, t011, t100, t101, t110, t111)]
    return out


def margin(table: "tuple[int, ...]", parents: "tuple[int, ...]", child: int) -> "tuple[int, ...]":
    """A family's complete table: rows the parents' joint cells (last fastest), columns the child's two bands."""
    width = 1 << len(parents)
    out = [0] * (width * 2)
    for index in range(8):
        cell = CELLS[index]
        row = 0
        for parent in parents:
            row = row * 2 + cell[parent]
        out[row * 2 + cell[child]] += table[index]
    return tuple(out)


def _floored(table: "tuple[int, ...]") -> bool:
    return all(cell == 0 or cell >= F for cell in table)


_OFFERED: "dict[tuple, object]" = {}


def _offered_once(key: tuple, scales: "list[rules.Ladder]", start: "list[int]", order: "list[int]", margins: rules.ParentCells, n: int) -> "list[int] | None":
    """W3 and NE's levels, kept by what they read (the members' totals and the anchor's table)."""
    if key not in _OFFERED:
        _OFFERED[key] = rules.offered_levels(scales, start, order, margins, n, F)
    found = _OFFERED[key]
    return found if isinstance(found, list) else None


def options(table: "tuple[int, ...]", scales: "list[rules.Ladder]") -> "list[tuple]":
    """Every description the draw can publish from one table: (root, step) pairs, in option order.

    The root step: `no family`, then each pair (child later in schema order),
    at every variant of W3 and NE's levels, each eligible where its table
    passes the floor. The step: `no family` for the third column, then every
    family whose parents lie in the root family (anchor the earliest family
    holding them), at every variant. Binary bands are the same at every
    level, so W1 (no small group) and WE (no blank cell) hold throughout.
    """
    n = sum(table)
    out: "list[tuple]" = [("none",)]
    names = [scale.column for scale in scales]
    for child in range(3):
        for parent in range(child):
            margins = rules.parent_cells({names[parent]: scales[parent]}, (names[parent],), None)
            offered = _offered_once(
                ("root", child, parent, scales[child].totals, scales[parent].totals, n),
                [scales[child], scales[parent]], [0, 0], [child, parent], margins, n,
            )
            if offered is None:
                continue
            root_table = margin(table, (parent,), child)
            if not _floored(root_table):
                continue
            # A binary column's bands are one at every level, so each coarser
            # variant publishes the same table and is eligible exactly where
            # the offered levels are: the variants differ in their labels
            # alone, which `canonical` drops, so the scan reads the offered
            # levels (the producer offers every variant; `mirror_agrees`).
            for root_levels in [tuple(offered)]:
                roots = [
                    rules.Family(names[parent], root_levels[1], (), None, scales[parent].totals),
                    rules.Family(names[child], root_levels[0], ((names[parent], root_levels[1]),), 0, root_table),
                ]
                third = 3 - child - parent
                steps: "list[tuple]" = [("none",)]
                held = {names[parent]: (0, root_levels[1]), names[child]: (1, root_levels[0])}
                for subset in ((parent,), (child,), tuple(sorted((parent, child)))):
                    anchor_at = 0 if subset == (parent,) else 1
                    anchor = roots[anchor_at]
                    start = [0] + [held[names[one]][1] for one in subset]
                    margins = rules.parent_cells({names[one]: scales[one] for one in range(3)}, tuple(names[one] for one in subset), anchor)
                    offered_step = _offered_once(
                        ("step", third, subset, tuple(start), anchor.table, tuple(scale.totals for scale in scales), n),
                        [scales[third]] + [scales[one] for one in subset],
                        start,
                        [third] + list(subset),
                        margins,
                        n,
                    )
                    if offered_step is None:
                        continue
                    step_table = margin(table, subset, third)
                    if not _floored(step_table):
                        continue
                    steps += [(subset, tuple(offered_step), anchor_at, step_table)]
                for step in steps:
                    out += [((child, parent, root_levels, root_table), step)]
    return out


def canonical(description: tuple) -> tuple:
    """A description with its level labels dropped (a binary column's bands are one at every level)."""
    if description == ("none",):
        return description
    root, step = description
    child, parent, _levels, root_table = root
    if step == ("none",):
        return (child, parent, root_table, "none")
    subset, _step_levels, _anchor, step_table = step
    return (child, parent, root_table, subset, step_table)


UNIONS = [tuple(i for i in range(8) if mask >> i & 1) for mask in range(1, 255)]


def _one_column(union: "tuple[int, ...]") -> bool:
    """A union that is every cell where one column takes one value: that column's own count."""
    cells = set(union)
    for column in range(3):
        for value in (0, 1):
            if cells == {i for i in range(8) if CELLS[i][column] == value}:
                return True
    return False


CROSS_UNIONS = [union for union in UNIONS if not _one_column(union)]


def leaking(tables: "list[tuple[int, ...]]") -> "tuple[int, ...] | None":
    """A union whose count lies inside 1 to 10 on every table given, or None."""
    survivors = None
    for table in tables:
        survivors = survive(survivors, table)
        if not survivors:
            return None
    return min(survivors) if survivors else None


def survive(survivors: "set[tuple[int, ...]] | None", table: "tuple[int, ...]") -> "set[tuple[int, ...]]":
    """The cross-column unions still inside 1 to 10 after one more table of a preimage.

    A union leaks only where its count lies inside 1 to 10 on EVERY table
    of the preimage, so the set of unions that might leak only shrinks as
    the tables stream past, and a description can be judged without its
    preimage held.
    """
    candidates = CROSS_UNIONS if survivors is None else survivors
    out: "set[tuple[int, ...]]" = set()
    for union in candidates:
        value = 0
        for i in union:
            value += table[i]
        if 1 <= value <= F - 1:
            out.add(union)
    return out


def margin_scan(sets: "list[tuple[int, int, int, int]]", pairs_on: int = 0) -> "dict[str, object]":
    """The margin-set scan: tables, descriptions reachable, descriptions leaking, and the two-keys pairs.

    Streams every table of each margin set past each description it can
    publish (`survive`). The TWO-KEYS pairs (a stated limit) are streamed
    the same way on the first `pairs_on` sets: each pair of descriptions
    of one table, its preimage the tables from which both can be
    published.
    """
    counts = {"margin_sets": len(sets), "tables": 0, "descriptions": 0, "descriptions_leaking": 0,
              "two_key_sets": min(pairs_on, len(sets)), "two_key_pairs": 0, "two_key_pairs_leaking": 0}
    for place in range(len(sets)):
        n, a1, b1, c1 = sets[place]
        scales = [binary_scale("a", n - a1, a1), binary_scale("b", n - b1, b1), binary_scale("c", n - c1, c1)]
        single: "dict[tuple, set[tuple[int, ...]]]" = {}
        paired: "dict[tuple, set[tuple[int, ...]]]" = {}
        for table in tables_with_margins(n, a1, b1, c1):
            counts["tables"] += 1
            reached = sorted({canonical(description) for description in options(table, scales)}, key=repr)
            for key in reached:
                single[key] = survive(single[key] if key in single else None, table)
            if place < pairs_on:
                for first, second in itertools.combinations(reached, 2):
                    pair = (first, second)
                    paired[pair] = survive(paired[pair] if pair in paired else None, table)
        counts["descriptions"] += len(single)
        counts["descriptions_leaking"] += len([key for key in single if single[key]])
        counts["two_key_pairs"] += len(paired)
        counts["two_key_pairs_leaking"] += len([pair for pair in paired if paired[pair]])
    return counts


def scan_sets(n_low: int, n_high: int, count: int, seed: int) -> "list[tuple[int, int, int, int]]":
    """The design's margin sets (`n3d.py`): n from `n_low` to `n_high`, each one-way total of the value 1 at least 2f."""
    import random

    sets: "list[tuple[int, int, int, int]]" = []
    for n in range(n_low, n_high + 1):
        for a1 in range(2 * F, n // 2 + 1):
            for b1 in range(2 * F, n - 2 * F + 1):
                for c1 in range(2 * F, n - 2 * F + 1):
                    sets += [(n, a1, b1, c1)]
    random.Random(seed).shuffle(sets)
    return sets[:count]


# -- RULE W1'S PART C, RECAST AS A FILTER (`w1_recast.py`) ------------------

PART_C_BANDS = (25, 32, 40, 60)
PART_C_ZERO = 6
PART_C_FLAG = (79, 78)


def part_c(variant: str) -> "dict[str, object]":
    """Every table of the part-C example and every description the draw can publish from it.

    `variant` "filter" reads RULE W1 as the product's eligibility filter
    (`rules.w1_refusals` on the option placed); "merge" is the version 2.2
    mutant, the band holding day 0 merged with its neighbour after the draw
    until its row holds two non-zero cells.
    """
    n = sum(PART_C_BANDS)
    day = rules.Ladder(
        "day",
        tuple(((f"B{at}",),) for at in range(4)),
        ((0, 1, 2, 3), (0, 0, 0, 1), (0, 0, 0, 1)),
        (4, 2, 2),
        PART_C_BANDS,
        (True, True, True, True),
    )
    flag = binary_scale("post", PART_C_FLAG[0], PART_C_FLAG[1])
    scales = {"day": day, "post": flag}
    groups = {"day": {0}}
    preimage: "dict[tuple, list[tuple[int, ...]]]" = {}
    tables = 0
    for x1 in range(0, PART_C_BANDS[0] + 1):
        for x2 in range(0, PART_C_BANDS[1] + 1):
            for x3 in range(0, PART_C_BANDS[2] + 1):
                x4 = PART_C_FLAG[1] - x1 - x2 - x3
                if not 0 <= x4 <= PART_C_BANDS[3]:
                    continue
                for zeros_flagged in range(0, min(PART_C_ZERO, x1) + 1):
                    if PART_C_BANDS[0] - x1 < PART_C_ZERO - zeros_flagged:
                        continue
                    tables += 1
                    fine = (
                        PART_C_ZERO - zeros_flagged,
                        zeros_flagged,
                        PART_C_BANDS[0] - x1 - (PART_C_ZERO - zeros_flagged),
                        x1 - zeros_flagged,
                        PART_C_BANDS[1] - x2,
                        x2,
                        PART_C_BANDS[2] - x3,
                        x3,
                        PART_C_BANDS[3] - x4,
                        x4,
                    )
                    for key in _part_c_descriptions((x1, x2, x3, x4), day, flag, scales, groups, variant, n):
                        if key not in preimage:
                            preimage[key] = []
                        preimage[key] += [fine]
    leaks = 0
    for key in preimage:
        if _part_c_leak(preimage[key]):
            leaks += 1
    return {"tables": tables, "descriptions": len(preimage), "descriptions_leaking": leaks}


def _part_c_descriptions(x, day, flag, scales, groups, variant, n):
    out = [("none",)]
    margins = rules.parent_cells(scales, ("day",), None)
    offered = rules.offered_levels([flag, day], [0, 0], [1, 0], margins, n, F)
    if offered is None:
        return out
    for levels in rules.variants_of(offered):
        day_level = levels[1]
        rows = rules.totals_at(day, day_level)
        ones = [0] * len(rows)
        for at in range(4):
            ones[day.maps[day_level][at]] += x[at]
        table = []
        for row in range(len(rows)):
            table += [rows[row] - ones[row], ones[row]]
        if not all(cell == 0 or cell >= F for cell in table):
            continue
        families = [
            rules.Family("day", day_level, (), None, tuple(rows)),
            rules.Family("post", levels[0], (("day", day_level),), 0, tuple(table)),
        ]
        if variant == "filter":
            if rules.w1_refusals(families, scales, groups):
                continue
            out += [("pair", levels, tuple(table))]
        else:
            band = day.maps[day_level][0]
            if table[band * 2] and table[band * 2 + 1]:
                out += [("pair", levels, tuple(table))]
            else:
                # The merge: the band holding day 0 joined with the one after it, shown as merged.
                merged = list(table)
                merged[band * 2] += merged[band * 2 + 2]
                merged[band * 2 + 1] += merged[band * 2 + 3]
                out += [("merged", levels, tuple(merged[: band * 2 + 2] + merged[band * 2 + 4 :]))]
    return out


def _part_c_leak(tables: "list[tuple[int, ...]]") -> bool:
    """A cross-column union of the ten finest cells inside 1 to 10 on every table (day-only unions skipped)."""
    zero = {i for i in range(10) if all(table[i] == 0 for table in tables)}
    seen: "set[tuple[int, ...]]" = set()
    for size in range(1, 11):
        for union0 in itertools.combinations(range(10), size):
            union = tuple(i for i in union0 if i not in zero)
            if not union or union in seen:
                continue
            seen.add(union)
            cells = set(union)
            if all((2 * group in cells) == (2 * group + 1 in cells) for group in range(5)):
                continue
            inside = True
            for table in tables:
                value = sum(table[i] for i in union)
                if value == 0 or value >= F:
                    inside = False
                    break
            if inside:
                return True
    return False


# -- THE MIRROR AGAINST THE PRODUCER ----------------------------------------


def mirror_agrees(table: "tuple[int, ...]", scales: "list[rules.Ladder]") -> bool:
    """Whether the producer's own search reaches exactly the descriptions `options` lists.

    The table's rows are laid out as the producer reads them (one byte a
    row a level), and `chain._root_options` and `chain._step_options` are
    asked every step, every eligible root placed in turn: the set of
    descriptions they reach, level labels dropped, must equal the mirror's.
    """
    from synthtwin import chain

    names = [scale.column for scale in scales]
    rows: "list[tuple[int, int, int]]" = []
    for index in range(8):
        rows += [CELLS[index]] * table[index]
    columns = {}
    for place in range(3):
        codes = bytes(row[place] for row in rows)
        columns[names[place]] = chain.Column(names[place], scales[place], (codes, codes, codes), frozenset(), b"", 4, True, 0)
    counts = {key: 0 for key in ("tables_counted", "candidates", "floor_refusals", "w1_refusals", "we_refusals", "eligible_options")}
    search = chain._Search(
        columns,
        {names[place]: scales[place] for place in range(3)},
        tuple(names),
        {names[place]: place for place in range(3)},
        sum(table),
        F,
        frozenset(),
        (),
        {},
        counts,
        {},
        {},
    )
    index_of = {names[place]: place for place in range(3)}
    reached: "set[tuple]" = set()
    for root in chain._root_options(search, None, 0):
        if not root.child:
            reached.add(("none",))
            continue
        parent = root.parents[0]
        placed = [
            rules.Family(parent, root.levels[1], (), None, tuple(rules.totals_at(scales[index_of[parent]], root.levels[1]))),
            rules.Family(root.child, root.levels[0], ((parent, root.levels[1]),), 0, root.table),
        ]
        head = (index_of[root.child], index_of[parent], root.table)
        clamps = chain._clamps_of(search, placed, False)
        for option in chain._step_options(search, placed, clamps, {}):
            if not option.parents:
                reached.add(head + ("none",))
            else:
                reached.add(head + (tuple(sorted(index_of[name] for name in option.parents)), option.table))
    return reached == {canonical(description) for description in options(table, scales)}


# -- THE OWN-FACT SOURCES W1 MISSED BEFORE REPAIR 1 (skeptic 1's item 1) ----


def _slice_rows() -> "tuple[list[str], list[list[str]], tuple[str, str]]":
    """600 all-different ages, sex F on every row of [p40, p50): each 1 % slice holds six rows."""
    import random

    draw = random.Random(5)
    ages = sorted(20 + 0.01 * value for value in draw.sample(range(6000), 600))
    rows = [[f"{ages[at]:.2f}", "F" if 240 <= at < 300 else draw.choice("FM")] for at in range(600)]
    draw.shuffle(rows)
    return ["age", "sex"], rows, ("p40", "p50")


def _clock_rows() -> "tuple[list[str], list[list[str]], tuple[str, str]]":
    """600 clocks; g = a on every row of [p25, p50), whose total less the census groups inside it is 1."""
    import random

    draw = random.Random(2)
    clocks = [draw.randint(0, 1439) for _ in range(600)]
    ordered = sorted(clocks)
    # The type-7 readings of p25 and p50 at 600 rows (positions 149.75 and 299.5).
    low = ordered[149] + (ordered[150] - ordered[149]) * 3 // 4
    high = ordered[299] + (ordered[300] - ordered[299]) // 2
    marks = random.Random(7)
    plain = [marks.choice("ab") for _ in clocks]
    rows = [[f"{c // 60:02d}:{c % 60:02d}", "a" if low <= c < high else plain[at]] for at, c in enumerate(clocks)]
    return ["clock", "g"], rows, ("p25", "p50")


def own_fact_case(name: str, product: bool) -> "dict[str, int]":
    """Every root option the draw can take on one fixture (two columns: the chain is its root
    pair), and how many confine the band holding the fixture's own-fact group to one `L2` band of
    the other column (RULE W1 read in full with the TRUE group). `product` False is the mutant:
    the groups `chain.value_run_bands` reads on the column's own values left out."""
    import pathlib
    import tempfile

    from synthtwin import chain, profile, reading, taxonomy

    header, rows, band_name = _slice_rows() if name == "slice" else _clock_rows()
    folder = pathlib.Path(tempfile.mkdtemp(prefix="chain-own-facts-"))
    path = folder / f"{name}.csv"
    path.write_text(",".join(header) + "\n" + "".join(",".join(row) + "\n" for row in rows), encoding="utf-8", newline="\n")
    settings = taxonomy.Settings(small_cell_floor=F)
    table = reading.read_table(str(path), small_cell_floor=F)
    document = profile.build_document(table, settings, [], [], [])
    seen: "list[object]" = []
    original_options = chain._root_options
    original_runs = chain.value_run_bands

    def recording(search, x0, room):  # type: ignore[no-untyped-def]
        found = original_options(search, x0, room)
        seen.extend([(option, search.scales) for option in found])
        return found

    try:
        chain._root_options = recording  # type: ignore[assignment]
        if not product:
            chain.value_run_bands = lambda *arguments: set()  # type: ignore[assignment]
        chain.describe(table, document, settings, chain.ChainSwitch(name, bytes(32)))
    finally:
        chain._root_options = original_options  # type: ignore[assignment]
        chain.value_run_bands = original_runs  # type: ignore[assignment]
        path.unlink()
        folder.rmdir()
    column = header[0]
    options = 0
    confining = 0
    for option, scales in seen:
        if not option.child:  # type: ignore[attr-defined]
            continue
        options += 1
        ladder = scales[column]
        group = [at for at in range(len(ladder.l0)) if any(isinstance(one, tuple) and one == band_name for one in ladder.l0[at])]
        parent = option.parents[0]  # type: ignore[attr-defined]
        placed = [
            rules.Family(parent, option.levels[1], (), None, tuple(rules.totals_at(scales[parent], option.levels[1]))),  # type: ignore[attr-defined]
            rules.Family(option.child, option.levels[0], ((parent, option.levels[1]),), 0, option.table),  # type: ignore[attr-defined]
        ]
        if rules.w1_refusals(placed, scales, {column: set(group), header[1]: set()}):
            confining += 1
    return {"options": options, "confining": confining}


def own_fact_sources() -> "dict[str, int]":
    """K-S6-08's two own-fact fixtures, the product and its mutant (no group read on the values)."""
    out = {"own_fact_options": 0, "own_fact_confining": 0, "own_fact_mutant_confining": 0}
    for name in ("slice", "clock"):
        found = own_fact_case(name, True)
        mutant = own_fact_case(name, False)
        out["own_fact_options"] += found["options"]
        out["own_fact_confining"] += found["confining"]
        out["own_fact_mutant_confining"] += mutant["confining"]
    return out
