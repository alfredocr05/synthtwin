"""The oracle's cases (lane CHo): each built from given numbers and words, each beside its mutant.

The chain's cases are the design's list (BC-ARCH 10.3) as the method's
G16.12 and contract 4.6b.10 state them; the moments' cases are contract
4.6d.7's. Every case is a pure function of the numbers written here:
no table is read and nothing is drawn (the words are SplitMix64 outputs
of fixed seeds, computed in integers and written into the vectors).
`chain_cases()` and `moment_cases()` return plain JSON-ready values;
`make_chain_oracle_vectors.py` writes them, and the tests rebuild them.
"""

import importlib.util
import os

# `pathlib` is not imported: on Python 3.11 it reaches `ntpath`, whose
# import of `_winapi` the provenance guard refuses.
HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


co = _load("chain_oracle")
mo = _load("moment_oracle")
F = co.F

TEST_KEY = bytes(range(32))
MASK64 = (1 << 64) - 1


def splitmix64(seed, count):
    """`count` SplitMix64 outputs from `seed`, in whole numbers (the vectors' given words)."""
    out = []
    state = seed & MASK64
    for _ in range(count):
        state = (state + 0x9E3779B97F4A7C15) & MASK64
        z = state
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK64
        out += [z ^ (z >> 31)]
    return out


def _fraction_text(q):
    q = F(q)
    return str(q.numerator) if q.denominator == 1 else "%d/%d" % (q.numerator, q.denominator)


def _number_rungs(edges):
    keys = ("p10", "p20", "p25", "p30", "p40", "p50", "p60", "p70", "p75", "p80", "p90")
    return dict(zip(keys, [F(e) for e in edges]))


# --- the chain's cases ------------------------------------------------------


def case_stated_exponential():
    """RULE W5's stated exponential on fixed gaps, and the choice on fixed words."""
    gaps = [F(0), F(1, 2), F(1), F(2), F(10), F(745), F(2500), F(1491, 2)]
    values = [co.stated_exponential(g) for g in gaps]
    word = co.word(TEST_KEY, "visits", "place", 3, ["age", "sbp", "stage"])
    scores = [F(0), F(41, 2), F(20), F(3)]
    weighted = co.choose(word, scores, F(2))
    uniform_word = bytes(4) + bytes([1, 2, 3, 4]) + bytes([0x80] + [0] * 7)
    uniform = co.choose(uniform_word, scores, F(2))
    return {
        "gaps": [_fraction_text(g) for g in gaps],
        "values": [co.b64_hex(v) for v in values],
        "word": word.hex(),
        "fingerprint": co.fingerprint(TEST_KEY).hex(),
        "scores": [_fraction_text(s) for s in scores],
        "weighted": {"place": weighted[0], "how": weighted[1], "weights": [co.b64_hex(w) for w in weighted[2]]},
        "uniform_word": uniform_word.hex(),
        "uniform": {"place": uniform[0], "how": uniform[1]},
    }


def ladder_merge_cells():
    """A number column of 207 tabled rows, 7 of them absent. Its band `[p20, p25)` holds no
    reading, so `p25` stops being an edge; the band then `[p20, p30)` holds 10 readings and
    joins `[p10, p20)` (20 readings, fewer than `[p30, p40)`'s 25); and the 7 absent cells
    join the lowest value band, an ORDERED band of 27."""
    cells = [("missing",)] * 7
    runs = [(10, 20), (100, 20), (250, 10), (300, 25), (400, 20), (500, 20), (600, 20),
            (700, 12), (750, 13), (800, 20), (900, 20)]
    for start, count in runs:
        cells += [("value", F(start + i)) for i in range(count)]
    rungs = _number_rungs([100, 200, 250, 300, 400, 500, 600, 700, 750, 800, 900])
    return cells, rungs


def case_ladder_merge():
    """The `L0` merge of contract 4.6b.2 on one column, with its levels and taken-in bands."""
    cells, rungs = ladder_merge_cells()
    lad = co.ladder_of("stay", "count", cells, rungs=rungs)
    return lad.as_dict()


def _labels(name, counts):
    cells = []
    for level, count in counts:
        cells += [("level", level)] * count
    return cells


def floor36_lads(floor):
    joint = [[20, 60, 60], [60, 60, 60], [60, 60, 60]]
    a_cells = []
    b_cells = []
    for i in range(3):
        for j in range(3):
            a_cells += [("level", "a%d" % (i + 1))] * joint[i][j]
            b_cells += [("level", "b%d" % (j + 1))] * joint[i][j]
    la = co.ladder_of("A", "categorical", a_cells, levels=[("a1", 140), ("a2", 180), ("a3", 180)], floor=floor, position=0)
    lb = co.ladder_of("B", "categorical", b_cells, levels=[("b1", 140), ("b2", 180), ("b3", 180)], floor=floor, position=1)
    return {"A": la, "B": lb}


def case_floor36(floor=36):
    """The held page's Codex table `[[20, 60, 60], [60, 60, 60], [60, 60, 60]]` at a floor of 36."""
    lads = floor36_lads(floor)
    setting = co.Setting("floor36", TEST_KEY, floor=floor)
    offered = co.offered_levels(lads, "B", [("A", 0)], None, 500, floor)
    rows = []
    for option, v in co.root_options(setting, lads, 500):
        if option["kind"] != "root":
            continue
        ok, why = co.eligible(setting, [], option, lads, 500)
        rows += [{"levels": [option["levels"]["A"], option["levels"]["B"]], "score": _fraction_text(v),
                  "eligible": ok, "why": why}]
    return {"floor": floor, "offered": [offered["A"], offered["B"]], "options": rows}


def case_p2():
    """The second red team's P2: one column at 11 and 989 rows, the other at 500 and 500."""
    lx = co.ladder_of("X", "binary", _labels("X", [("x1", 11), ("x2", 989)]), levels=[("x1", 11), ("x2", 989)], position=0)
    ly = co.ladder_of("Y", "binary", _labels("Y", [("y1", 500), ("y2", 500)]), levels=[("y1", 500), ("y2", 500)], position=1)
    lads = {"X": lx, "Y": ly}
    offered = co.offered_levels(lads, "Y", [("X", 0)], None, 1000)
    setting = co.Setting("p2", TEST_KEY)
    options = co.root_options(setting, lads, 1000)
    return {"offered": offered, "options": len(options)}


def part_c_rows():
    """Part C on 500 rows: a day count `D` whose `n_zero` 6 lies in its lowest `L0` band of 50
    rows, every one of them post-op 0; the other bands split between both post-op levels."""
    rows = [(0, "p0")] * 6
    rows += [(1 + k % 4, "p0") for k in range(44)]
    edges = [5, 10, 13, 15, 20, 25, 30, 33, 35, 40, 45]
    counts = [50, 25, 25, 50, 50, 50, 50, 25, 25, 50, 50]
    for low, count in zip(edges, counts):
        ones = 28 if count == 50 else 14
        rows += [(low + (k % 2), "p1" if k < ones else "p0") for k in range(count)]
    return rows, _number_rungs(edges)


def part_c_lads():
    rows, rungs = part_c_rows()
    n0 = sum(1 for r in rows if r[1] == "p0")
    ld = co.ladder_of("D", "count", [("value", F(r[0])) for r in rows], rungs=rungs, position=0)
    lp = co.ladder_of("P", "binary", [("level", r[1]) for r in rows], levels=[("p0", n0), ("p1", len(rows) - n0)], position=1)
    return {"D": ld, "P": lp}, len(rows)


def case_part_c(w1=None):
    """RULE W1's confined band (the red team's part C): the fine option refused, `L1` eligible."""
    lads, n = part_c_lads()
    setting = co.Setting("partc", TEST_KEY, own_groups=[("D", 0)])
    rows = []
    for option, v in co.root_options(setting, lads, n):
        if option["kind"] != "root":
            continue
        ok, why = co.eligible(setting, [], option, lads, n, w1=w1)
        rows += [{"levels": [option["levels"]["D"], option["levels"]["P"]], "eligible": ok, "why": why}]
    first = co.table_of(lads, "P", 0, [("D", 0)])
    return {"n": n, "d_totals": lads["D"].totals, "row_of_the_group": first[0], "options": rows}


def case_transport():
    """G16.6's moved target on Codex's case, with the units it places in a published nought."""
    table, named = co.moved_target([[50, 0], [0, 50]], [60, 40], [40, 60])
    return {"published": [[50, 0], [0, 50]], "rows": [60, 40], "columns": [40, 60], "moved": table,
            "units_in_noughts": [list(x) for x in named]}


def held_page_fit(published, rows, columns, rounds=20):
    """The MUTANT: the held page's fitting and rounding (proportional fitting, then rounding)."""
    t = [[F(x) for x in r] for r in published]
    for _ in range(rounds):
        for i, r in enumerate(t):
            s = sum(r)
            if s:
                t[i] = [x * rows[i] / s for x in r]
        for j in range(len(columns)):
            s = sum(t[i][j] for i in range(len(t)))
            if s:
                for i in range(len(t)):
                    t[i][j] = t[i][j] * columns[j] / s
    return [[(x * 2 + 1).numerator // ((x * 2 + 1).denominator * 2) for x in r] for r in t]


# --- the walk on 40 rows (G16.12 item 2) --------------------------------------

WALK_SEED = 0x5EED0C40


def walk40_source():
    """The 40-row source: `X` 1 to 40, `Y` read from `X` with a twist, `Z` 11 absent and 29 readings."""
    xs = list(range(1, 41))
    ys = [2 * x + ((7 * x) % 11) - 5 for x in xs]
    zs = []
    for x in xs:
        if x % 4 == 0 and len([z for z in zs if z is None]) < 10 or x == 39:
            zs += [None]
        else:
            zs += [3 * x + ((5 * x) % 13)]
    return xs, ys, zs


def _rungs_of(values):
    """Interior rungs at the deciles with p25 and p75, read as the readings at those ranks."""
    ordered = sorted(values)
    n = len(ordered)
    out = {}
    for key, pct in (("p10", 10), ("p20", 20), ("p25", 25), ("p30", 30), ("p40", 40), ("p50", 50),
                     ("p60", 60), ("p70", 70), ("p75", 75), ("p80", 80), ("p90", 90)):
        out[key] = F(ordered[(n * pct) // 100])
    return out


def walk40_setup():
    """The published side of the 40-row walk and the twin's cells, at a floor of one."""
    xs, ys, zs = walk40_source()
    cells = {
        "X": [("value", F(x)) for x in xs],
        "Y": [("value", F(y)) for y in ys],
        "Z": [("missing",) if z is None else ("value", F(z)) for z in zs],
    }
    rungs = {"X": _rungs_of(xs), "Y": _rungs_of(ys), "Z": _rungs_of([z for z in zs if z is not None])}
    lads = {}
    for at, name in enumerate(("X", "Y", "Z")):
        lads[name] = co.ladder_of(name, "count", cells[name], rungs=rungs[name], floor=1, position=at)
    chain = [
        co.Family("X", 1, [], None, None),
        co.Family("Y", 1, [("X", 1)], 0, None),
        co.Family("Z", 2, [("X", 2), ("Y", 2)], 1, None),
    ]
    for fam in chain:
        fam.table = co.table_of(lads, fam.child, fam.level, fam.parents) if fam.parents else [lads[fam.child].band_totals(fam.level)]
    slopes = {2: ([("X", "0.4123"), ("Y", "0.2875")], "13.5000")}
    codes = {name: (rungs[name]["p10"], rungs[name]["p90"]) for name in ("X", "Y", "Z")}
    twin = {}
    for name in ("X", "Y", "Z"):
        lad = lads[name]
        groups = [[] for _ in lad.l0]
        for r, cell in enumerate(cells[name]):
            text = "" if cell[0] == "missing" else str(cell[1])
            value = None if cell[0] == "missing" else cell[1]
            groups[lad.row_l0[r]] += [(text, value)]
        twin[name] = groups
    words = splitmix64(WALK_SEED, 3 * 40 * len(chain))
    by_family = []
    at = 0
    for _ in chain:
        rows = []
        for _ in range(40):
            rows += [tuple(words[at:at + 3])]
            at += 3
        by_family += [rows]
    return lads, chain, twin, by_family, slopes, codes


def case_walk40(sort_by_row=False, spread_after=False):
    lads, chain, twin, words, slopes, codes = walk40_setup()
    trace = {}
    index, lists, dealt = co.walk_rows(chain, lads, twin, words, slopes=slopes, codes=codes,
                                       sort_by_row=sort_by_row, spread_after=spread_after, trace=trace)
    out = {
        "latent_z": [co.b64_hex(x) for x in trace[2]["latent"]],
        "families": [fam.as_dict() for fam in chain],
        "dealt": dealt,
        "met": [d == fam.table for d, fam in zip(dealt, chain)],
        "index": {c: index[c] for c in ("X", "Y", "Z")},
        "rows": [[lists[c][index[c][r]][0] for c in ("X", "Y", "Z")] for r in range(40)],
    }
    return out


def case_walk_words():
    lads, chain, twin, words, slopes, codes = walk40_setup()
    return {"seed": WALK_SEED, "words": [["%016x" % w for w in row] for fam in words for row in fam]}


# --- an empty-support cell, a label child, a rule word (G16.12 items 4 to 6) ---


def small_chain(parent_counts, child_rows, child_role="categorical", child_levels=None, parent_role="categorical"):
    """A family `C | A` on given rows, `A` and `C` label columns (or `C` a number column)."""
    a_cells = []
    c_cells = []
    for (a, c), count in child_rows:
        a_cells += [("level", a)] * count
        c_cells += [c] * count
    la = co.ladder_of("A", parent_role, a_cells, levels=parent_counts, floor=1, position=0)
    if child_role == "count":
        lc = co.ladder_of("C", "count", c_cells, rungs=child_levels, floor=1, position=1)
    else:
        lc = co.ladder_of("C", child_role, c_cells, levels=child_levels, floor=1, position=1)
    return {"A": la, "C": lc}, a_cells, c_cells


def _twin_groups(lad, cells, order=()):
    """The twin's cells of a column, grouped by `L0` band in the interface's order.

    A level cell's reading is its level's place in the published order
    (method G4.2b); an absent cell holds no reading.
    """
    places = {name: at for at, name in enumerate(order)}
    groups = [[] for _ in lad.l0]
    for r, cell in enumerate(cells):
        if cell[0] == "missing":
            groups[lad.row_l0[r]] += [("", None)]
        elif cell[0] == "level":
            groups[lad.row_l0[r]] += [(cell[1], places.get(cell[1], 0))]
        else:
            groups[lad.row_l0[r]] += [(str(cell[1]), cell[1])]
    return groups


def _words_for(seed, families, n):
    words = splitmix64(seed, 3 * n * families)
    return [[tuple(words[3 * (f * n + r): 3 * (f * n + r) + 3]) for r in range(n)] for f in range(families)]


def case_empty_and_absent():
    """`C | A, B`: the parent cell (a2, b1) holds no row, and in (a2, b2) the child is always absent."""
    rows = [
        (("a1", "b1", ("level", "c1")), 20), (("a1", "b1", ("level", "c2")), 20),
        (("a1", "b2", ("level", "c1")), 10), (("a1", "b2", ("level", "c2")), 10),
        (("a2", "b2", ("missing",)), 15),
    ]
    a_cells, b_cells, c_cells = [], [], []
    for (a, b, c), count in rows:
        a_cells += [("level", a)] * count
        b_cells += [("level", b)] * count
        c_cells += [c] * count
    lads = {
        "A": co.ladder_of("A", "categorical", a_cells, levels=[("a1", 60), ("a2", 15)], floor=1, position=0),
        "B": co.ladder_of("B", "categorical", b_cells, levels=[("b1", 40), ("b2", 35)], floor=1, position=1),
        "C": co.ladder_of("C", "categorical", c_cells, levels=[("c1", 30), ("c2", 30)], floor=1, position=2),
    }
    chain = [co.Family("A", 0, [], None, [lads["A"].band_totals(0)]),
             co.Family("B", 0, [("A", 0)], 0, co.table_of(lads, "B", 0, [("A", 0)])),
             co.Family("C", 0, [("A", 0), ("B", 0)], 1, co.table_of(lads, "C", 0, [("A", 0), ("B", 0)]))]
    twin = {"A": _twin_groups(lads["A"], a_cells, ("a1", "a2")),
            "B": _twin_groups(lads["B"], b_cells, ("b1", "b2")),
            "C": _twin_groups(lads["C"], c_cells, ("c1", "c2"))}
    n = len(a_cells)
    index, lists, dealt = co.walk_rows(chain, lads, twin, _words_for(0xE0C1, 3, n))
    out_rows = [[lists[c][index[c][r]][0] for c in ("A", "B", "C")] for r in range(n)]
    return {"c_l0": lads["C"].as_dict()["l0"], "table": chain[2].table, "dealt": dealt[2],
            "met": dealt == [fam.table for fam in chain],
            "rows_in_the_empty_cell": sum(1 for a, b, _ in out_rows if (a, b) == ("a2", "b1")),
            "child_present_in_the_absent_cell": sum(1 for a, b, c in out_rows if (a, b) == ("a2", "b2") and c != ""),
            "rows": out_rows}


def case_label_child():
    """A label child dealt by its hidden score; a label parent entering only as a cell."""
    rows = [
        (("north", ("level", "x")), 12), (("north", ("level", "y")), 13),
        (("south", ("level", "x")), 14), (("south", ("level", "y")), 11),
    ]
    lads, a_cells, c_cells = small_chain([("north", 25), ("south", 25)], rows, child_levels=[("x", 26), ("y", 24)])
    chain = [co.Family("A", 0, [], None, [lads["A"].band_totals(0)]),
             co.Family("C", 0, [("A", 0)], 0, co.table_of(lads, "C", 0, [("A", 0)]))]
    twin = {"A": _twin_groups(lads["A"], a_cells, ("north", "south")),
            "C": _twin_groups(lads["C"], c_cells, ("x", "y"))}
    n = len(a_cells)
    by_family = _words_for(0x1ABE1, 2, n)
    index, lists, dealt = co.walk_rows(chain, lads, twin, by_family)
    scores = [co.hidden_score(by_family[1][r]) for r in range(n)]
    return {"table": chain[1].table, "dealt": dealt[1], "met": dealt[1] == chain[1].table,
            "rows": [[lists[c][index[c][r]][0] for c in ("A", "C")] for r in range(n)],
            "first_scores": [_fraction_text(s) for s in scores[:5]]}


def case_rule_word(as_one=False):
    """A family whose published nought lies between two bands of at least `f` rows: the walk
    deals no row there (mutant: the cell's target taken as one)."""
    rows = [
        (("adm", ("level", "pre")), 30), (("adm", ("level", "post")), 0),
        (("dis", ("level", "pre")), 12), (("dis", ("level", "post")), 18),
    ]
    rows = [r for r in rows if r[1]]
    lads, a_cells, c_cells = small_chain([("adm", 30), ("dis", 30)], rows, child_levels=[("pre", 42), ("post", 18)])
    table = co.table_of(lads, "C", 0, [("A", 0)])
    target = [list(r) for r in table]
    if as_one:
        target[0] = [target[0][0] - 1, target[0][1] + 1]
        target[1] = [target[1][0] + 1, target[1][1] - 1]
    chain = [co.Family("A", 0, [], None, [lads["A"].band_totals(0)]),
             co.Family("C", 0, [("A", 0)], 0, table)]
    twin = {"A": _twin_groups(lads["A"], a_cells, ("adm", "dis")),
            "C": _twin_groups(lads["C"], c_cells, ("pre", "post"))}
    n = len(a_cells)
    index, lists, dealt = co.walk_rows(chain, lads, twin, _words_for(0x30E0, 2, n), targets={1: target})
    rows_out = [[lists[c][index[c][r]][0] for c in ("A", "C")] for r in range(n)]
    broken = sum(1 for a, c in rows_out if a == "adm" and c == "post")
    return {"table": table, "dealt": dealt[1], "rows_breaking_the_word": broken}


# --- a carried order rule (G16.12 item 7) ----------------------------------------


def case_order_rule(own_column=False):
    """`B` written as `A + D` on every row; mutant: `B` dealt as a column of its own."""
    a = [F(x) if x is not None else None for x in (3, 5, 8, 2, 7, 1, 4, 6, 9, 10, None, 12)]
    d = [F(x) if x is not None else None for x in (1, 0, 2, 4, 1, 3, 0, 2, 5, 1, 2, None)]
    b = co.computed_column(a, d)
    if own_column:
        present = [x for x in b if x is not None]
        present = present[3:] + present[:3]
        b = [present.pop(0) if x is not None else None for x in b]
    breaking = sum(1 for x, y in zip(a, b) if x is not None and y is not None and y < x)
    return {"a": [None if x is None else _fraction_text(x) for x in a],
            "d": [None if x is None else _fraction_text(x) for x in d],
            "b": [None if x is None else _fraction_text(x) for x in b],
            "rows_breaking_a_le_b": breaking}


def case_derived_family(totals_alone=False):
    """A derived `D` dealt as the child of `{D | A}`: every row of `A`'s `missing` band takes
    `D`'s `missing` band (mutant: `D` dealt by its band totals alone)."""
    rows = [
        (("missing", ("missing",)), 11),
        (("low", ("level", "short")), 20), (("low", ("level", "long")), 11),
        (("high", ("level", "short")), 12), (("high", ("level", "long")), 22),
    ]
    a_cells = []
    d_cells = []
    for (a, dd), count in rows:
        a_cells += [("missing",) if a == "missing" else ("level", a)] * count
        d_cells += [dd] * count
    la = co.ladder_of("A", "categorical", a_cells, levels=[("low", 31), ("high", 34)], floor=1, position=0)
    ld = co.ladder_of("D", "categorical", d_cells, levels=[("short", 32), ("long", 33)], floor=1, position=1)
    lads = {"A": la, "D": ld}
    table = co.table_of(lads, "D", 0, [("A", 0)])
    if totals_alone:
        parent = [co.Family("A", 0, [], None, [la.band_totals(0)])]
        chain = parent + [co.Family("D", 0, [], None, [ld.band_totals(0)])]
    else:
        chain = [co.Family("A", 0, [], None, [la.band_totals(0)]), co.Family("D", 0, [("A", 0)], 0, table)]
    twin = {"A": _twin_groups(la, a_cells, ("low", "high")), "D": _twin_groups(ld, d_cells, ("short", "long"))}
    n = len(a_cells)
    index, lists, dealt = co.walk_rows(chain, lads, twin, _words_for(0xDE41, 2, n))
    rows_out = [[lists[c][index[c][r]][0] for c in ("A", "D")] for r in range(n)]
    beside_absent = sum(1 for a_text, d_text in rows_out if a_text == "" and d_text != "")
    return {"table": table, "readings_of_d_beside_an_absent_a": beside_absent}


# --- a pair's implied table and its dealing spread (V12.2) -----------------------


def case_implied_pair():
    """The implied table of `A` and `C` through `B` (`A`, `B | A`, `C | B`), in exact fractions."""
    ab = [[30, 10], [10, 30]]
    bc = [[25, 15], [5, 35]]
    n = 80
    implied = [[F(0)] * 2 for _ in range(2)]
    a_tot = [sum(r) for r in ab]
    b_tot = [sum(ab[i][j] for i in range(2)) for j in range(2)]
    for i in range(2):
        for j in range(2):
            for k in range(2):
                implied[i][k] += F(ab[i][j]) * F(bc[j][k], b_tot[j])
    radicands, low, high = co.dealing_spread(implied, n)
    return {"ab": ab, "bc": bc, "a_totals": a_tot, "implied": [[_fraction_text(x) for x in r] for r in implied],
            "radicands": [_fraction_text(q) for q in radicands],
            "spread_low": _fraction_text(low), "spread_high": _fraction_text(high)}


def case_score():
    table = [[30, 10, 0], [10, 25, 5]]
    return {"table": table, "u": _fraction_text(co.score(table))}


# --- a whole search for the test key ---------------------------------------------


def search_lads():
    """Three label columns on 400 rows, their joint fixed by a rule of whole numbers."""
    rows = []
    for r in range(400):
        a = "a%d" % (r % 3)
        b = "b%d" % ((r // 3 + r % 3) % 2)
        c = "c%d" % ((r // 7 + (r % 3 == 0)) % 3)
        rows += [(a, b, c)]
    lads = {}
    for at, name in enumerate(("A", "B", "C")):
        cells = [("level", row[at]) for row in rows]
        counts = {}
        for cell in cells:
            counts[cell[1]] = counts.get(cell[1], 0) + 1
        levels = sorted(counts.items())
        lads[name] = co.ladder_of(name, "categorical", cells, levels=levels, position=at)
    return lads, len(rows)


def case_search():
    lads, n = search_lads()
    setting = co.Setting("trial", TEST_KEY)
    chain, steps = co.search(setting, lads, n)
    out_steps = []
    for step in steps:
        out_steps += [{
            "index": step["index"],
            "eligible": len(step["eligible"]),
            "word": step["word"],
            "how": step["how"],
            "placed": step["placed"],
            "scores": [_fraction_text(v) for _, v in step["eligible"]],
        }]
    return {"chain": [fam.as_dict() for fam in chain], "steps": out_steps}


# --- RULE W1 in full: across the chain, through a derived family, member by member --------


def _rows_lads(rows, specs):
    """Ladders of label columns from joint rows `[(values, count)]`; `specs` lists, for each
    column in schema order, `(name, role, levels)`."""
    lads = {}
    for at, (name, role, levels) in enumerate(specs):
        cells = []
        for values, count in rows:
            cells += [("level", values[at])] * count
        lads[name] = co.ladder_of(name, role, cells, levels=levels, position=at)
    return lads


def w1_across_setup():
    """`A`, `B | A`, `C | B` on 100 rows; `A`'s group in band `a2`, `C`'s in band `c1`."""
    rows = [(("a1", "b1", "c2"), 30), (("a1", "b3", "c1"), 15), (("a1", "b3", "c2"), 15),
            (("a2", "b1", "c2"), 20), (("a2", "b2", "c2"), 20)]
    lads = _rows_lads(rows, [("A", "binary", [("a1", 60), ("a2", 40)]),
                             ("B", "categorical", [("b1", 50), ("b2", 20), ("b3", 30)]),
                             ("C", "binary", [("c1", 15), ("c2", 85)])])
    chain = [co.Family("A", 0, [], None, [lads["A"].band_totals(0)]),
             co.Family("B", 0, [("A", 0)], 0, co.table_of(lads, "B", 0, [("A", 0)])),
             co.Family("C", 0, [("B", 0)], 1, co.table_of(lads, "C", 0, [("B", 0)]))]
    return lads, chain, [("A", 1), ("C", 0)]


def case_w1_across():
    """RULE W1 read across the chain: a published nought in ANOTHER family confines a band
    (both directions along the chain)."""
    lads, chain, groups = w1_across_setup()
    holds, failures = co.w1_holds(chain, lads, groups)
    admitted = {"%s%d" % g: {c: sorted(b) for c, b in sorted(co.support(chain, lads, {g[0]: {g[1]}}).items())}
                for g in groups}
    return {"tables": [fam.table for fam in chain], "holds": holds, "failures": [list(f) for f in failures],
            "admitted": admitted}


def w1_derived_setup():
    """Codex's item 2 of 2026-10-19: a derived family `{D | A}` placed at its rule's step,
    then the root pair `B`, `A | B`: the step's child `A` already stands in a placed family."""
    rows = [(("b1", "a1", "d2"), 20), (("b1", "a3", "d1"), 20), (("b1", "a3", "d2"), 20),
            (("b2", "a1", "d2"), 25), (("b2", "a2", "d2"), 15)]
    lads = _rows_lads(rows, [("B", "binary", [("b1", 60), ("b2", 40)]),
                             ("A", "categorical", [("a1", 45), ("a2", 15), ("a3", 40)]),
                             ("D", "derived", [("d1", 20), ("d2", 80)])])
    derived = co.Family("D", 0, [("A", 0)], None, co.table_of(lads, "D", 0, [("A", 0)]))
    option = {"kind": "root", "parent": "B", "child": "A", "levels": {"B": 0, "A": 0}}
    return lads, [derived], option


def w1_step_pairs_only(lads, groups):
    """The MUTANT the page withdraws (4.6b.3): W1 read only on the pairs holding the step's
    child, the first build's shortcut "adding a family never narrows an earlier support"."""
    def check(placed):
        child = placed[-1].child
        _, failures = co.w1_holds(placed, lads, groups)
        return not [f for f in failures if child in (f[0], f[2])]
    return check


def case_w1_derived(w1=None):
    """The root pair `(B, A)` beside `{D | A}`: `B`'s group in band `b2` confines `D` through
    `A`, a pair holding neither the step's child nor its parent's family alone."""
    lads, chain, option = w1_derived_setup()
    setting = co.Setting("w1derived", TEST_KEY, own_groups=[("B", 1)])
    ok, why = co.eligible(setting, chain, option, lads, 100, w1=w1)
    placed = co._placed(chain, option, lads)
    holds, failures = co.w1_holds(placed, lads, [("B", 1)])
    return {"derived_table": chain[0].table, "option_table": placed[-1].table, "edges": co.tree_edges(placed),
            "eligible": ok, "why": why, "failures": [list(f) for f in failures]}


def w1_member_setup():
    """`A`, `B | A`, then the option `X | A, B` on 100 rows; `X`'s group in band `x1`."""
    rows = [(("a1", "b1", "x1"), 15), (("a1", "b1", "x2"), 15), (("a1", "b2", "x2"), 20),
            (("a2", "b1", "x1"), 12), (("a2", "b1", "x2"), 13), (("a2", "b2", "x2"), 25)]
    lads = _rows_lads(rows, [("A", "binary", [("a1", 50), ("a2", 50)]),
                             ("B", "binary", [("b1", 55), ("b2", 45)]),
                             ("X", "binary", [("x1", 27), ("x2", 73)])])
    chain = [co.Family("A", 0, [], None, [lads["A"].band_totals(0)]),
             co.Family("B", 0, [("A", 0)], 0, co.table_of(lads, "B", 0, [("A", 0)]))]
    option = {"kind": "family", "child": "X", "parents": ["A", "B"], "anchor": 1, "levels": {"A": 0, "B": 0, "X": 0}}
    return lads, chain, option


def design_clause(lads, groups):
    """The MUTANT of 4.6b.9 (c)'s cases: the design's own clause, two non-zero cells beside
    the group's band in each placed family's table holding its column, read on joint cells."""
    def check(placed):
        levels_at = {f.child: f.level for f in placed}
        for column, band in groups:
            if column not in levels_at:
                continue
            for family in placed:
                members = family.members()
                if column not in members:
                    continue
                at = members.index(column)
                level = family.levels()[at]
                beta = lads[column].coarsen(level)[lads[column].coarsen(levels_at[column])[band]]
                sizes = [len(lads[c].bands(lv)) for c, lv in zip(members, family.levels())]
                beside = 0
                for row, cells in enumerate(family.table):
                    rest = row
                    coords = []
                    for size in reversed(sizes[:-1]):
                        coords += [rest % size]
                        rest //= size
                    coords = list(reversed(coords))
                    for j, count in enumerate(cells):
                        if (coords + [j])[at] == beta and count > 0:
                            beside += 1
                if beside < 2:
                    return False
        return True
    return check


def case_w1_member(design=False):
    """RULE W1 member by member: the option's column `x1` holds two non-zero cells that differ
    in `A` and agree in `B`, so `B` is confined beside `X`'s group."""
    lads, chain, option = w1_member_setup()
    setting = co.Setting("w1member", TEST_KEY, own_groups=[("X", 0)])
    w1 = design_clause(lads, [("X", 0)]) if design else None
    ok, why = co.eligible(setting, chain, option, lads, 100, w1=w1)
    placed = co._placed(chain, option, lads)
    holds, failures = co.w1_holds(placed, lads, [("X", 0)])
    return {"option_table": placed[-1].table, "eligible": ok, "why": why, "failures": [list(f) for f in failures]}


# --- the boundaries the page states (the floor, NE, W3, the merge, the score, WE) -----------


def case_floor_edge():
    """The floor at `f` = 11: a cell of 10 refused, of 11 and of 0 kept."""
    return {"ten": co.floor_holds([[10, 30]]), "eleven": co.floor_holds([[11, 29]]), "nought": co.floor_holds([[0, 40]])}


def _binary_pair(parent_totals, child_totals):
    lads = {"P": co.ladder_of("P", "binary", _labels("P", [("p1", parent_totals[0]), ("p2", parent_totals[1])]),
                              levels=[("p1", parent_totals[0]), ("p2", parent_totals[1])], position=0),
            "C": co.ladder_of("C", "binary", _labels("C", [("c1", child_totals[0]), ("c2", child_totals[1])]),
                              levels=[("c1", child_totals[0]), ("c2", child_totals[1])], position=1)}
    return lads


def case_ne_edge():
    """RULE NE at its boundary, a root pair on 300 rows: least expected count exactly `f + 1`
    (offered) against exactly `f` (not offered)."""
    out = {}
    for label, parent in (("twelve", (120, 180)), ("eleven", (110, 190))):
        lads = _binary_pair(parent, (30, 270))
        out[label] = co.offered_levels(lads, "C", [("P", 0)], None, 300)
    return out


def case_w3_equality():
    """RULE W3 at equality: `X`'s smallest total 22 against `f` times `Y`'s 2 bands holds;
    `Y` fails alone, cannot coarsen past `L2`, and the candidate is not offered."""
    lads = {"X": co.ladder_of("X", "categorical", _labels("X", [("x1", 22), ("x2", 40), ("x3", 38), ("x4", 100)]),
                              levels=[("x1", 22), ("x2", 40), ("x3", 38), ("x4", 100)], position=0),
            "Y": co.ladder_of("Y", "binary", _labels("Y", [("y1", 30), ("y2", 170)]),
                              levels=[("y1", 30), ("y2", 170)], position=1)}
    return {"offered": co.offered_levels(lads, "Y", [("X", 0)], None, 200)}


def case_w3_choice():
    """RULE W3's choice: of the failing members, the one whose smallest band total is
    smallest goes coarser."""
    lads = {"X": co.ladder_of("X", "categorical", _labels("X", [("x1", 15), ("x2", 85), ("x3", 100)]),
                              levels=[("x1", 15), ("x2", 85), ("x3", 100)], position=0),
            "Y": co.ladder_of("Y", "categorical", _labels("Y", [("y1", 25), ("y2", 75), ("y3", 100)]),
                              levels=[("y1", 25), ("y2", 75), ("y3", 100)], position=1)}
    return {"offered": co.offered_levels(lads, "Y", [("X", 0)], None, 200)}


def case_ne_zero_cell():
    """RULE NE read literally on a parents' cell of total 0: its expected count is 0, below
    `f + 1`, so the candidate coarsens until the cell is gone."""
    rows = [(("a1", "b1", "c1"), 100), (("a1", "b1", "c2"), 100), (("a1", "b2", "c1"), 100),
            (("a1", "b2", "c2"), 100), (("a1", "b3", "c1"), 100), (("a1", "b3", "c2"), 100),
            (("a2", "b2", "c1"), 75), (("a2", "b2", "c2"), 75), (("a2", "b3", "c1"), 125), (("a2", "b3", "c2"), 125)]
    lads = _rows_lads(rows, [("A", "binary", [("a1", 600), ("a2", 400)]),
                             ("B", "categorical", [("b1", 200), ("b2", 350), ("b3", 450)]),
                             ("C", "binary", [("c1", 500), ("c2", 500)])])
    anchor = co.Family("B", 0, [("A", 0)], 0, co.table_of(lads, "B", 0, [("A", 0)]))
    return {"anchor_table": anchor.table,
            "offered": co.offered_levels(lads, "C", [("A", 0), ("B", 0)], anchor, 1000)}


def merge_tie_cells():
    cells = []
    for start, count in ((10, 20), (100, 20), (200, 5), (250, 20), (300, 20), (400, 20), (500, 20),
                         (600, 20), (700, 20), (750, 20), (800, 20), (900, 20)):
        cells += [("value", F(start + i)) for i in range(count)]
    return cells, _number_rungs([100, 200, 250, 300, 400, 500, 600, 700, 750, 800, 900])


def case_merge_tie():
    """The `L0` merge's tie: a band of 5 between two of 20 joins the EARLIER neighbour."""
    cells, rungs = merge_tie_cells()
    lad = co.ladder_of("tie", "count", cells, rungs=rungs)
    return {"totals": lad.totals, "taken_in": lad.taken_in}


def case_score_empty_row():
    """The score's `df` over the rows and columns whose totals are not nought."""
    table = [[30, 10, 0], [0, 0, 0], [10, 25, 5]]
    return {"table": table, "u": _fraction_text(co.score(table))}


def we133_rows():
    """Codex's 133 rows of contract 4.6b.3's RULE WE: 33 records holding nothing (11 leading, 11
    interior, 11 trailing, so `Z` = 0) and 100 tabled rows over `A`, `B`, `C`, each one level
    or blank; no row is blank in all three, and 6 read `A` and `C` recorded beside a blank `B`."""
    return [((None, None, "c"), 22), (("a", None, None), 22), (("a", None, "c"), 6),
            ((None, "b", None), 11), ((None, "b", "c"), 11), (("a", "b", None), 11), (("a", "b", "c"), 17)]


def case_we133(we=True):
    """RULE WE on Codex's 133 rows: every root pair is refused (`b(x0)` above `Z + P` = 0)."""
    rows = we133_rows()
    lads = {}
    for at, name in enumerate(("A", "B", "C")):
        cells = []
        for values, count in rows:
            cells += [("missing",) if values[at] is None else ("level", values[at])] * count
        present = sum(count for values, count in rows if values[at] is not None)
        lads[name] = co.ladder_of(name, "categorical", cells, levels=[(name.lower(), present)], position=at)
    blank = {"A": 0, "B": 0, "C": 0}
    setting = co.Setting("we133", TEST_KEY, we={"blank": blank, "z": 0, "p": 0} if we else None)
    out = {"totals": {c: lads[c].totals for c in ("A", "B", "C")}, "pairs": []}
    for option, _ in co.root_options(setting, lads, 100):
        if option["kind"] != "root" or any(option["levels"][c] for c in option["levels"]):
            continue
        a, b = option["parent"], option["child"]
        placed = co._placed([], option, lads)
        ok, why = co.eligible(setting, [], option, lads, 100)
        out["pairs"] += [{"pair": [a, b], "table": placed[-1].table, "b_x0": co.cell_bound(placed, lads, blank, 100),
                          "eligible": ok, "why": why}]
    kept = [option for option, _ in co.root_options(setting, lads, 100)
            if co.eligible(setting, [], option, lads, 100)[0]]
    out["eligible_options"] = len(kept)
    return out


# --- the draw's and the moved target's ties, and the slope's reading map (G16.2, G16.6) -------


def case_draw_edges():
    """The uniform share's edge (U1 = 2**33: top 30 bits clear) and the weighted choice's
    tie (a running sum exactly at the threshold)."""
    scores = [F(0), F(41, 2), F(20), F(3)]
    edge = (1 << 33).to_bytes(8, "big") + (1 << 63).to_bytes(8, "big")
    tie = (1 << 40).to_bytes(8, "big") + (1 << 63).to_bytes(8, "big")
    place, how, _ = co.choose(edge, scores, F(2))
    tie_place, tie_how, weights = co.choose(tie, [F(0), F(0)], F(2))
    return {"edge_word": edge.hex(), "edge": {"place": place, "how": how},
            "tie_word": tie.hex(), "tie": {"place": tie_place, "how": tie_how,
                                           "weights": [co.b64_hex(w) for w in weights]}}


def case_moved_tie():
    """G16.6's last tie: two tables equal on noughts, distance and squares; the greater in
    row-major order is taken."""
    table, named = co.moved_target([[10, 10], [10, 10]], [21, 19], [20, 20])
    return {"moved": table, "units_in_noughts": [list(x) for x in named]}


SLOPE_SEED = 0x51A0E


def slope_absent_setup():
    """G16.12 item 11: a slope parent `X` whose 5 absent cells the `L0` merge joins with 45
    readings below its one edge into one ORDERED band; `Y | X` publishes a slope on `X`."""
    xs = [None] * 5 + list(range(1, 96))
    ys = [60, 70, 80, 90, 150] + [2 * x + (7 * x) % 5 for x in range(1, 96)]
    rungs = _number_rungs([46] * 11)
    cells = {"X": [("missing",) if x is None else ("value", F(x)) for x in xs],
             "Y": [("value", F(y)) for y in ys]}
    y_rungs = _number_rungs([100] * 11)
    lads = {"X": co.ladder_of("X", "count", cells["X"], rungs=rungs, position=0),
            "Y": co.ladder_of("Y", "count", cells["Y"], rungs=y_rungs, position=1)}
    chain = [co.Family("X", 0, [], None, [lads["X"].band_totals(0)]),
             co.Family("Y", 0, [("X", 0)], 0, co.table_of(lads, "Y", 0, [("X", 0)]))]
    twin = {}
    for name in ("X", "Y"):
        groups = [[] for _ in lads[name].l0]
        for r, cell in enumerate(cells[name]):
            groups[lads[name].row_l0[r]] += [("", None) if cell[0] == "missing" else (str(cell[1]), cell[1])]
        twin[name] = groups
    slopes = {1: ([("X", "0.5000")], "2.0000")}
    codes = {"X": (F(0), F(100))}
    return lads, chain, twin, _words_for(SLOPE_SEED, 2, 100), slopes, codes


def case_slope_absent():
    lads, chain, twin, words, slopes, codes = slope_absent_setup()
    trace = {}
    index, lists, dealt = co.walk_rows(chain, lads, twin, words, slopes=slopes, codes=codes, trace=trace)
    absent = [r for r in range(100) if lists["X"][index["X"][r]][1] is None]
    return {"x_l0": lads["X"].as_dict()["l0"], "x_totals": lads["X"].totals, "table": chain[1].table,
            "met": dealt == [fam.table for fam in chain], "absent_rows": absent,
            "means": {str(c): co.b64_hex(m) for c, m in sorted(trace[1]["means"]["X"].items())},
            "latent": [co.b64_hex(x) for x in trace[1]["latent"]]}


# --- a later step's option order (contract 4.6b.3) ----------------------------------------


def case_step_order():
    """A step's candidates in option order: by the anchor's place in the chain, then by the
    parents' places in schema order; four binary columns on 2,000 rows, each cell 125."""
    rows = []
    for r in range(16):
        rows += [((("a%d" % (r % 2)), ("b%d" % ((r // 2) % 2)), ("c%d" % ((r // 4) % 2)), ("d%d" % ((r // 8) % 2))), 125)]
    lads = _rows_lads(rows, [(name, "binary", [(name.lower() + "0", 1000), (name.lower() + "1", 1000)])
                             for name in ("A", "B", "C", "D")])
    chain = [co.Family("A", 0, [], None, [lads["A"].band_totals(0)]),
             co.Family("B", 0, [("A", 0)], 0, co.table_of(lads, "B", 0, [("A", 0)])),
             co.Family("C", 0, [("A", 0)], 0, co.table_of(lads, "C", 0, [("A", 0)]))]
    setting = co.Setting("order", TEST_KEY)
    seen = []
    for option, _ in co.step_options(setting, lads, chain, 2000):
        if option["kind"] != "family":
            continue
        key = [option["parents"], option["anchor"]]
        if key not in seen:
            seen += [key]
    return {"candidates": seen}


def chain_cases():
    return {
        "stated_exponential": case_stated_exponential(),
        "ladder_merge": case_ladder_merge(),
        "floor36": case_floor36(),
        "floor36_mutant_literal_11": case_floor36(11),
        "p2": case_p2(),
        "part_c": case_part_c(),
        "part_c_mutant_old_clause": case_part_c(w1=lambda placed: True),
        "transport": case_transport(),
        "transport_mutant_held_page": held_page_fit([[50, 0], [0, 50]], [60, 40], [40, 60]),
        "walk40_words": case_walk_words(),
        "walk40": case_walk40(),
        "walk40_mutant_row_order": case_walk40(sort_by_row=True),
        "walk40_mutant_spread_after": case_walk40(spread_after=True),
        "empty_and_absent": case_empty_and_absent(),
        "label_child": case_label_child(),
        "rule_word": case_rule_word(),
        "rule_word_mutant_as_one": case_rule_word(as_one=True),
        "order_rule": case_order_rule(),
        "order_rule_mutant_own_column": case_order_rule(own_column=True),
        "derived_family": case_derived_family(),
        "derived_family_mutant_totals_alone": case_derived_family(totals_alone=True),
        "implied_pair": case_implied_pair(),
        "score": case_score(),
        "search": case_search(),
        "w1_across": case_w1_across(),
        "w1_derived": case_w1_derived(),
        "w1_derived_mutant_step_pairs_only": case_w1_derived(w1=w1_step_pairs_only(w1_derived_setup()[0], [("B", 1)])),
        "w1_member": case_w1_member(),
        "w1_member_mutant_design_clause": case_w1_member(design=True),
        "floor_edge": case_floor_edge(),
        "ne_edge": case_ne_edge(),
        "ne_zero_cell": case_ne_zero_cell(),
        "w3_equality": case_w3_equality(),
        "w3_choice": case_w3_choice(),
        "merge_tie": case_merge_tie(),
        "score_empty_row": case_score_empty_row(),
        "we133": case_we133(),
        "we133_mutant_no_we": case_we133(we=False),
        "draw_edges": case_draw_edges(),
        "moved_tie": case_moved_tie(),
        "slope_absent": case_slope_absent(),
        "step_order": case_step_order(),
    }


# --- the moments' cases (contract 4.6d.7) -----------------------------------------


def _atom(name, band, code, small=False, reading=True):
    return {"name": name, "band": band, "codes": {"L": code}, "reading": reading, "small": small}


def _sum(columns, powers, cells, value, centres=None):
    return {"columns": list(columns), "codes": ["L"] * len(columns), "powers": list(powers),
            "centres": list(centres or [0] * len(columns)), "cells": list(cells), "value": value}


def spec_reference():
    """Codex's reference case: two base cells of 100 rows over codes 0 to 2, code sums 100,
    and the column's atom counts (50, 100, 50) fixed by its own facts."""
    return {"floor": 11,
            "cells": [{"name": "A", "bands": {"c": 0}}, {"name": "B", "bands": {"c": 0}}],
            "atoms": {"c": [_atom(0, 0, 0), _atom(1, 0, 1), _atom(2, 0, 2)]},
            "margins": [{"cells": [0], "count": 100}, {"cells": [1], "count": 100}],
            "facts": [{"column": "c", "atoms": [0], "lo": 50, "hi": 50},
                      {"column": "c", "atoms": [1], "lo": 100, "hi": 100},
                      {"column": "c", "atoms": [2], "lo": 50, "hi": 50}],
            "sums": [_sum(["c"], [1], [0], 100), _sum(["c"], [1], [1], 100)]}


def spec_small_atom():
    """One cell of 30 rows: `n_zero` 3 (a small atom at code 0), 27 over codes 1 to 4, sums 84 and 286."""
    return {"floor": 11, "cells": [{"name": "X", "bands": {"c": 0}}],
            "atoms": {"c": [_atom("zero", 0, 0, small=True)] + [_atom(v, 0, v) for v in (1, 2, 3, 4)]},
            "margins": [{"cells": [0], "count": 30}],
            "facts": [{"column": "c", "atoms": ["zero"], "lo": 3, "hi": 3}],
            "sums": [_sum(["c"], [1], [0], 84), _sum(["c"], [2], [0], 286)]}


def spec_clause_c():
    """`n_zero` 3 over two cells of 22 rows on codes 0 to 2, code sums 30 and 40."""
    return {"floor": 11, "cells": [{"name": "A", "bands": {"c": 0}}, {"name": "B", "bands": {"c": 0}}],
            "atoms": {"c": [_atom("zero", 0, 0, small=True), _atom(1, 0, 1), _atom(2, 0, 2)]},
            "margins": [{"cells": [0], "count": 22}, {"cells": [1], "count": 22}],
            "facts": [{"column": "c", "atoms": ["zero"], "lo": 3, "hi": 3}],
            "sums": [_sum(["c"], [1], [0], 30), _sum(["c"], [1], [1], 40)]}


def spec_q_or_s(total, square=None):
    """Cases `Q` and `S`: one cell of 22 rows; `c`'s `n_zero` atom `G` of 3 rows and its other
    19 rows `H`; `e` of the same region on codes 10 to 12."""
    sums = [_sum(["e"], [1], [0], total)]
    if square is not None:
        sums += [_sum(["e"], [2], [0], square)]
    return {"floor": 11, "cells": [{"name": "X", "bands": {"c": 0, "e": 0}}],
            "atoms": {"c": [_atom("G", 0, 0, small=True), _atom("H", 0, 1)],
                      "e": [_atom(v, 0, v) for v in (10, 11, 12)]},
            "margins": [{"cells": [0], "count": 22}],
            "facts": [{"column": "c", "atoms": ["G"], "lo": 3, "hi": 3},
                      {"column": "c", "atoms": ["H"], "lo": 19, "hi": 19}],
            "sums": sums}


def spec_two_small_atoms():
    """Exception (i) of Theorem 2: two small atoms of one region (`n_zero` 3 at code 0 and a
    heap of 4 at code 2) over two cells of 22 rows on codes 0 to 3, code sums 30 and 33."""
    return {"floor": 11, "cells": [{"name": "A", "bands": {"c": 0}}, {"name": "B", "bands": {"c": 0}}],
            "atoms": {"c": [_atom("zero", 0, 0, small=True), _atom(1, 0, 1), _atom("heap", 0, 2, small=True),
                            _atom(3, 0, 3)]},
            "margins": [{"cells": [0], "count": 22}, {"cells": [1], "count": 22}],
            "facts": [{"column": "c", "atoms": ["zero"], "lo": 3, "hi": 3},
                      {"column": "c", "atoms": ["heap"], "lo": 4, "hi": 4}],
            "sums": [_sum(["c"], [1], [0], 30), _sum(["c"], [1], [1], 33)]}


def spec_correlation(rows, sums):
    """A two-column correlation region (class `M-a`) on one base cell: `c` and `d` each on
    codes 0 to 2, centred at code 1, with the nine sums of `a^i b^j` published."""
    out = []
    for i in range(3):
        for j in range(3):
            out += [_sum(["c", "d"], [i, j], [0], sums[(i, j)], centres=[1, 1])]
    return {"floor": 11, "cells": [{"name": "X", "bands": {"c": 0, "d": 0}}],
            "atoms": {"c": [_atom(v, 0, v) for v in (0, 1, 2)], "d": [_atom(v, 0, v) for v in (0, 1, 2)]},
            "margins": [{"cells": [0], "count": rows}], "facts": [], "sums": out}


def correlation_sums(counts):
    """The nine sums of a joint count table over codes 0 to 2 centred at 1."""
    out = {}
    for i in range(3):
        for j in range(3):
            out[(i, j)] = sum(counts[u][v] * (u - 1) ** i * (v - 1) ** j for u in range(3) for v in range(3))
    return out


def decide_mutant(instance, mutant):
    """The witness with one clause changed, for the mutants of contract 4.6d.7.

    - "old_query": Codex's mutant, refuse where SOME point puts 1 to `f - 1` rows on a group;
    - "no_c": clause (c) dropped;
    - "c_zero_points_only": clause (c) asked only of the groups a point ZERO ON `V-` fills.
    """
    f = instance.floor
    values = mo.feasible_values(instance)
    if values is None:
        return False
    if mutant == "old_query":
        return not any(1 <= v <= f - 1 for vs in values for v in vs)
    largest = [max(vs) for vs in values]
    unreachable = [k for k in range(len(values)) if k not in instance.holds_small and largest[k] < f]
    zeroed = list(instance.upper)
    for k in unreachable:
        zeroed[k] = 0
    zero_values = mo.feasible_values(instance, zeroed)
    if zero_values is None:
        return False
    if mutant == "no_c":
        return True
    for _, groups in instance.small_atoms:
        for g in groups:
            asked = max(zero_values[g]) >= 1 if mutant == "c_zero_points_only" else largest[g] >= 1
            if not asked:
                continue
            upper = list(zeroed)
            for other in groups:
                if other != g:
                    upper[other] = 0
            if mo.feasible_values(instance, upper) is None:
                return False
    return True


def _verdict(spec):
    inst = mo.build_instance(spec)
    v = mo.decide(inst)
    out = v.as_dict(inst)
    out["v_minus"] = [list(k) for k in out.get("v_minus", [])]
    return inst, out


def one_cell_refusals(top):
    refused = []
    for total in range(22 * top + 1):
        inst = mo.build_instance(mo.one_cell_spec(22, 0, top, total))
        if not mo.decide(inst).holds:
            refused += [total]
    return refused


def cf1_agreement(rows_list, widths=range(1, 7)):
    """CF1 against the oracle on every cell of the given sizes over runs of `widths` codes."""
    count = 0
    differ = []
    for rows in rows_list:
        for width in widths:
            for total in range(0, rows * (width - 1) + 1):
                inst = mo.build_instance(mo.one_cell_spec(rows, 0, width - 1, total))
                v = mo.decide(inst)
                reach = [inst.keys[k][1] for k in range(len(inst.keys)) if v.largest[k] >= inst.floor]
                expected = [c for c in range(width) if mo.cf1_reach(rows, total, 0, width - 1, c)]
                count += 1
                if reach != expected or v.holds != mo.cf1_holds(rows, total, 0, width - 1):
                    differ += [[rows, width, total]]
    return {"cells": count, "differ": differ}


def class_boundary(width):
    """The largest one-cell mean instance over `width` codes the class holds, and the next one.

    The cell's code sum is the middle of its range; the bound grows with
    the rows, so the boundary is found by doubling and halving.
    """
    def bounds(rows):
        total = rows * (width - 1) // 2
        return mo.class_bounds(mo.build_instance(mo.one_cell_spec(rows, 0, width - 1, total)))

    def bound(rows):
        return bounds(rows)[0]

    low = 22
    high = 44
    while bound(high) <= mo.NODES_MAX:
        low, high = high, high * 2
    while high - low > 1:
        middle = (low + high) // 2
        if bound(middle) <= mo.NODES_MAX:
            low = middle
        else:
            high = middle
    return {"width": width, "inside": [low, low * (width - 1) // 2] + list(bounds(low)),
            "outside": [high, high * (width - 1) // 2] + list(bounds(high))}


def moment_cases():
    out = {}
    inst, out["reference"] = _verdict(spec_reference())
    out["reference_mutant_old_query"] = decide_mutant(inst, "old_query")
    sloped = spec_reference()
    sloped["slopes"] = ["c | THE TABLE"]
    inst, out["reference_with_a_slope"] = _verdict(sloped)
    inst, out["small_atom"] = _verdict(spec_small_atom())
    inst, out["clause_c"] = _verdict(spec_clause_c())
    out["clause_c_mutant_no_c"] = decide_mutant(inst, "no_c")
    inst, out["case_q"] = _verdict(spec_q_or_s(223, 2263))
    out["case_q_mutant_zero_points_only"] = decide_mutant(inst, "c_zero_points_only")
    inst, out["case_s"] = _verdict(spec_q_or_s(226))
    out["case_s_mutant_zero_points_only"] = decide_mutant(inst, "c_zero_points_only")
    inst, out["cross_region_band"] = _verdict(mo.one_cell_spec(30, 10, 20, 320))
    out["one_cell_refusals"] = {str(top): one_cell_refusals(top) for top in (1, 2, 3)}
    inst, out["exception_i"] = _verdict(spec_two_small_atoms())
    duplicate = [[11, 0, 0], [0, 22, 0], [0, 0, 11]]
    sums = correlation_sums(duplicate)
    out["duplicate_columns_test_i"] = mo.correlation_allowed(sums[(0, 0)], sums[(1, 0)], sums[(0, 1)],
                                                             sums[(2, 0)], sums[(0, 2)], sums[(1, 1)])
    loose = [[4, 4, 3], [4, 3, 4], [3, 4, 4]]
    inst, out["correlation_one_cell"] = _verdict(spec_correlation(33, correlation_sums(loose)))
    out["cf1_against_the_oracle"] = cf1_agreement([22, 40])
    out["class_boundary"] = [class_boundary(w) for w in (2, 3, 4, 6)]
    out["class"] = {"name": mo.CLASS_NAME, "nodes_max": mo.NODES_MAX, "entries_max": mo.ENTRIES_MAX,
                    "groups_max": mo.GROUPS_MAX}
    return out
