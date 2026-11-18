"""The oracle's cases (lane CHo): each built from given numbers and words, each beside its mutant.

The chain's cases are the design's list (BC-ARCH 10.3) as the method's
G16.12 and contract 4.6b.10 state them; the moments' cases are contract
4.6d.7's. Every case is a pure function of the numbers written here:
no table is read and nothing is drawn (the words are SplitMix64 outputs
of fixed seeds, computed in integers and written into the vectors).
`chain_cases()` and `moment_cases()` return plain JSON-ready values;
`make_chain_oracle_vectors.py` writes them, and the tests rebuild them.
"""

import hashlib
import importlib.util
import json
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


# RULE ONE_BAND's columns (contract 4.6b.2, amended 2026-11-01), each a count
# column given as (value, rows) pairs, its absent cells, and the rungs `p10` to
# `p90` a profiler publishes for exactly these cells (the linear-interpolation
# percentile at 1,000 rows and more, where every one of them is published;
# lane CHa2's repair: the gate holds the product's own rungs and ladder to
# each shape). Every rung is a value the column holds, so each cut is exact.
ONE_BAND_SHAPES = {
    # nought on 550 of 1,000 rows, one on 260, two on 190: `p10` to `p50`
    # nought, `p60` to `p80` one, `p90` two.
    "one_band": (((0, 550), (1, 260), (2, 190)), 0, (0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2)),
    # the same beside 30 blank cells.
    "one_band_beside_blanks": (((0, 550), (1, 260), (2, 190)), 30, (0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2)),
    # the exact rung: nought on 601 of 1,001 rows puts `p60` on the last
    # nought itself, one on 250, two on 150: `p70` is the edge of one.
    "one_band_at_the_exact_rung": (((0, 601), (1, 250), (2, 150)), 0, (0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 2)),
    # nought on 220, one on 100, two on 400, then 40 rows of each of three to
    # nine: `p50` reads two, which `p40` names as an edge, so `p50` still cuts
    # and the rule reaches nothing; a level read by key finds no edge `p50`.
    "one_band_median_named_by_a_lower_rung": (
        ((0, 220), (1, 100), (2, 400), (3, 40), (4, 40), (5, 40), (6, 40), (7, 40), (8, 40), (9, 40)), 0,
        (0, 0, 1, 1, 2, 2, 2, 2, 3, F(21, 5), 7)),
    # nought on 970, one on 15, two on 15: every rung nought, no `L1` cut.
    "one_band_no_cut": (((0, 970), (1, 15), (2, 15)), 0, (0,) * 11),
    # the same beside 30 blank cells: blank against present is the level.
    "one_band_no_cut_beside_blanks": (((0, 970), (1, 15), (2, 15)), 30, (0,) * 11),
}


def one_band_cells(name):
    """The cells and the rungs of one of `ONE_BAND_SHAPES`."""
    counts, blank, edges = ONE_BAND_SHAPES[name]
    cells = [("missing",)] * blank
    for value, rows in counts:
        cells += [("value", F(value))] * rows
    return cells, _number_rungs(edges)


def one_band_shapes():
    """The shapes as the vectors carry them, for the product's side of the gate."""
    out = {}
    for name in ONE_BAND_SHAPES:
        counts, blank, edges = ONE_BAND_SHAPES[name]
        out[name] = {"counts": [[value, rows] for value, rows in counts], "blank": blank,
                     "rungs": {key: _fraction_text(value) for key, value in _number_rungs(edges).items()}}
    return out


def case_one_band(name="one_band", mutant=False):
    """RULE ONE_BAND of contract 4.6b.2 (amended 2026-11-01): the median at the lowest value leaves `p50`
    no row below it, and `L2` reads the lowest `L1` cut with rows on both sides, nought against the rest.
    The mutant is the level before the rule: one value band."""
    cells, rungs = one_band_cells(name)
    if mutant:
        kept = co._one_band
        co._one_band = lambda l0, totals, l1, l2: l2
        try:
            return co.ladder_of("visits", "count", cells, rungs=rungs).as_dict()
        finally:
            co._one_band = kept
    return co.ladder_of("visits", "count", cells, rungs=rungs).as_dict()


TEMPORAL_KEYS = ("p01", "p05", "p10", "p25", "p50", "p75", "p90", "p95", "p99")


def date_ladder_cells():
    """Codex's date case: ordinals 0 to 2,000 (one row each), the nine interior rungs at 20,
    100, 200, 500, 1,000, 1,500, 1,800, 1,900 and 1,980 on the column's own ordinal."""
    cells = [("value", F(x)) for x in range(2001)]
    rungs = dict(zip(TEMPORAL_KEYS, [F(e) for e in (20, 100, 200, 500, 1000, 1500, 1800, 1900, 1980)]))
    return cells, rungs


def clock_ladder_cells():
    """A clock column of 1,060 rows: 60 absent and the seconds 0 to 999 one row each, its nine
    interior rungs at 10, 50, 100, 250, 500, 750, 900, 950 and 990 on the clock's ordinal."""
    cells = [("missing",)] * 60 + [("value", F(x)) for x in range(1000)]
    rungs = dict(zip(TEMPORAL_KEYS, [F(e) for e in (10, 50, 100, 250, 500, 750, 900, 950, 990)]))
    return cells, rungs


def case_temporal_ladder(role_as_number=False):
    """A date's ladder and a clock's (contract 4.6b.2: `L0` cut at their nine interior
    rungs); MUTANT: each read as a number column, cut at the deciles with `p25` and `p75`."""
    out = {}
    for name, role, (cells, rungs) in (("visit_date", "datetime", date_ladder_cells()),
                                        ("visit_clock", "time_of_day", clock_ladder_cells())):
        lad = co.ladder_of(name, "count" if role_as_number else role, cells, rungs=rungs)
        out[role] = lad.as_dict()
    return out


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


def case_walk40_implied(implied=True):
    """G16.2 step 2's IMPLIED SLOPE on the 40-row walk (lane MPg, plan P4-D456), no slope published: each
    family's slope from its published table and the members' published `L0` totals, every row's latent
    order, the ranged parents' ranks, the hidden sums and the cell indices. MUTANT: `L = z` (the walk
    before it), which deals other rows."""
    lads, chain, twin, words, _slopes, _codes = walk40_setup()
    trace = {}
    index, lists, dealt = co.walk_rows(chain, lads, twin, words, implied=implied, trace=trace)
    out = {"index": {c: index[c] for c in ("X", "Y", "Z")}, "dealt": dealt,
           "met": [d == fam.table for d, fam in zip(dealt, chain)]}
    if not implied:
        return out
    sums = []
    for fam_words in words:
        sums += [[sum((w >> shift) & 0xFFFF for w in row for shift in (0, 16, 32, 48)) for row in fam_words]]
    families = {}
    for fi in (1, 2):
        used, beta, sigma, means = trace[fi]["means"]["slope"]
        families[str(fi)] = {
            "used": used,
            "beta": [co.b64_hex(b) for b in beta],
            "sigma": co.b64_hex(sigma),
            "means": [None if m is None else co.b64_hex(m) for m in means],
            "latent": [co.b64_hex(x) for x in trace[fi]["latent"]],
            "sums": sums[fi],
            "cells": trace[fi]["cells"],
            "table": chain[fi].table,
            "sizes": [len(lads[p].bands(lv)) for p, lv in chain[fi].parents],
            "parent_scores": [[None if v is None else co.b64_hex(v) for v in co.lad_scores(lads[p], lv)]
                              for p, lv in chain[fi].parents],
            "child_scores": [None if v is None else co.b64_hex(v) for v in co.lad_scores(lads[chain[fi].child], chain[fi].level)],
            "level_totals": {p: [lads[p].band_totals(lv), [any(isinstance(s, tuple) for i in m for s in lads[p].l0[i])
                                                          for m in lads[p].bands(lv)]]
                             for p, lv in list(chain[fi].parents) + [(chain[fi].child, chain[fi].level)]},
        }
    out["families"] = families
    out["ranks"] = {}
    for name in ("X", "Y"):
        held = []
        listing = lists[name]
        readings = [cell for cell in listing if cell[1] is not None]
        for r in range(40):
            cell = listing[index[name][r]]
            held += [None if cell[1] is None else sorted(range(len(readings)), key=lambda k: (readings[k][1], k)).index(
                [k for k in range(len(readings)) if readings[k] is cell][0])]
        out["ranks"][name] = held
    out["readings"] = {name: len([c for c in lists[name] if c[1] is not None]) for name in ("X", "Y")}
    return out


def polish_setup():
    """A 64-row twin of three FINE number columns, a binary and a grouping column for G16.3's polish (lane MPg).

    `Y`, `X` and `W` hold value codes in cell-list order (sorted, rising), each row's place a SplitMix64
    permutation; `Y` holds 6 places without a reading (absent cells, the end of its last band); each
    column's `L0` band is its place's eighth, its `L1` band the same, its `L2` and chain-level band the
    place's quarter, so a row moved inside its chain-level band may cross an `L1` band; each place's rank
    code from its reading's place among the readings. `B` is a binary: its first 40 places level 0, its
    last 24 level 1, its frame `X`'s `L2` band (the one table that crosses it). `G` groups the rows in
    three `L1` bands. Targets: `Y` with `W` (r -0.300), `Y`'s means in `G`'s bands (with their published
    spreads) and in `X`'s `L1` bands (a polished grouping column, read again after each of its rounds);
    `X` with `W` (0.250) and with `Y` (0.600; `Y`'s 58 readings give rank codes off the multiples of 256; the pair
    holds 58 of `X`'s 64 readings, so it publishes `X`'s own spread over them, 66 codes, a target of the pair since
    repair 2), each pair's aim bounded by the larger of 0.999 and half way from its goal to 1; `B` by `X`'s split (`X`'s means in `B`'s two bands) and by its shares in `G`'s
    bands, each at the slope a binary's threshold gives. Each row's hidden sums from SplitMix64 words,
    one set a round of each polished column. Published figures in the units contract 4.6d.0 (3) sets at
    their counts (a mean in tenths, a column's spread in thousandths, a band's in tenths, a share in
    ten-thousandths)."""
    n = 64
    words = splitmix64(0x9017, 3 * n * 6)
    columns = {}
    for at, name in enumerate(("Y", "X", "W", "B")):
        perm = list(range(n))
        draw = splitmix64(0x50 + at, n)
        perm = [p for _w, p in sorted(zip(draw, perm))]
        if name == "B":
            slot_l0 = [0 if k < 40 else 1 for k in range(n)]
            column = {"index": perm, "slot_codes": list(slot_l0), "slot_has": [1] * n, "slot_l0": slot_l0,
                      "maps": {0: [0, 1], 1: [0, 1], 2: [0, 1]}, "frame": [slot_l0[perm[r]] for r in range(n)]}
            columns[name] = column
            continue
        slot_codes = [(k * 251) // (n - 1) for k in range(n)]
        slot_has = [1] * n
        if name == "Y":
            for k in range(n - 6, n):
                slot_has[k] = 0
                slot_codes[k] = 0
        slot_l0 = [(8 * k) // n for k in range(n)]
        column = {"index": perm, "slot_codes": slot_codes, "slot_has": slot_has, "slot_l0": slot_l0,
                  "maps": {0: list(range(8)), 1: list(range(8)), 2: [b // 2 for b in range(8)]},
                  "slot_rank": co.rank_codes([c if h else None for c, h in zip(slot_codes, slot_has)])}
        column["frame"] = [slot_l0[perm[r]] // 2 for r in range(n)]
        columns[name] = column
    codes = {name: [c["slot_codes"][c["index"][r]] for r in range(n)] for name, c in columns.items()}
    has = {name: [c["slot_has"][c["index"][r]] for r in range(n)] for name, c in columns.items()}
    ranks = {name: [c["slot_rank"][c["index"][r]] for r in range(n)] for name, c in columns.items() if "slot_rank" in c}
    bands = {("G", 1): [(5 * r) % 3 for r in range(n)],
             ("X", 1): [columns["X"]["slot_l0"][columns["X"]["index"][r]] for r in range(n)],
             ("B", 1): [columns["B"]["slot_l0"][columns["B"]["index"][r]] for r in range(n)]}
    spreads = {name: co.code_spread(codes[name], has[name]) for name in codes}
    encoding, sds, goal = co.within_target([[20, 1280, 400], [24, 1300, 380], [20, 1350, 420]], 1310, 42000, 58)
    by_x, by_x_sds, by_x_goal = co.within_target([[7, 1050 + 50 * g, 300] for g in range(8)], 1310, 42000, 58)
    split, _split_sds, split_goal = co.within_target([[40, 1150, 690], [24, 1450, 620]], 1260, 74000, 64)
    shares, shares_goal = co.share_target([[20, 3000], [24, 3500], [20, 4500]], 3750, 64)
    share = co.b64_div(3750, 10000)
    density = co.normal_density(share)
    plan = [
        ("Y", [{"kind": "pair", "name": "W", "goal": co.b64(F(-300, 1000))},
               {"kind": "within", "name": "G", "goal": goal, "encoding": encoding, "sds": sds,
                "scales": [F(1)] * 3},
               {"kind": "within", "name": "X", "goal": by_x_goal, "encoding": by_x}]),
        ("X", [{"kind": "pair", "name": "W", "goal": co.b64(F(250, 1000))},
               {"kind": "pair", "name": "Y", "goal": co.b64(F(600, 1000)),
                "sds": [co.b64_div(66000, co.moment_unit(1000, 58))], "scales": [F(1)]}]),
        ("B", [{"kind": "by", "name": "X", "goal": split_goal, "encoding": split,
                "slope": co.b64_mul(co.b64_sub(split[1], split[0]), density)},
               {"kind": "share", "name": "G", "goal": shares_goal, "encoding": shares,
                "slope": co.b64_div(density, co.b64_sqrt(co.b64_mul(share, co.b64_sub(1, share))))}]),
    ]
    for _name, targets in plan:
        for target in targets:
            target.setdefault("slope", F(1))
            target["aim"] = co.b64_div(target["goal"], target["slope"])
            if target["kind"] == "pair":
                target["most"] = max(co.b64(F(999, 1000)), co.b64_div(co.b64_add(F(1), abs(target["goal"])), 2))
            target.setdefault("encoding", [])
            target.setdefault("level", 1)
    sums = []
    for k in range(6):
        sums += [[sum((w >> shift) & 0xFFFF for w in words[3 * (k * n + r):3 * (k * n + r) + 3]
                      for shift in (0, 16, 32, 48)) for r in range(n)]]
    state = {"rows": n, "codes": codes, "has": has, "ranks": ranks, "bands": bands, "spreads": spreads,
             "keys": {"B": [("X", 2)]}, "columns": columns}
    return n, columns, state, plan, sums


def case_polish(frame_l0=False, adjust=True, stale=False, spreads_on=True, feasible=True):
    """G16.3's polish on `polish_setup`'s twin: two rounds of each polished column in plan order, the
    second the last, which re-sorts each column `POLISH_LAST_STEPS` times on its one set of hidden sums,
    moving the aims between them: after each re-sort, the column's places, each target's aim and spread
    factors, and `X`'s `L1` bands as the next re-sort reads them. MUTANTS: each row kept in its `L0` band
    (G16.3's first frame); the aims never moved; a moved column's bands never read again; no band's spread
    scaled; the aims never scaled together."""
    n, columns, state, plan, sums = polish_setup()
    trail = []
    turn = 0
    for rnd in range(2):
        for name, targets in plan:
            steps = co.POLISH_LAST_STEPS if rnd == 1 else 1
            for step in range(steps):
                moving = adjust and (rnd == 0 or step + 1 < steps)
                co.polish_column(columns[name], name, targets, sums[turn], state, moving,
                                 frame_l0=frame_l0, stale=stale, spreads_on=spreads_on, feasible=feasible)
                trail += [{"column": name, "index": list(columns[name]["index"]),
                           "aims": [co.b64_hex(t["aim"]) for t in targets],
                           "scales": [[co.b64_hex(v) for v in t.get("scales", [])] for t in targets],
                           "x_bands": list(state["bands"][("X", 1)])}]
            turn += 1
    return {"rows": n, "trail": trail,
            "multiset_kept": all(sorted(columns[c]["index"]) == list(range(n)) for c in columns),
            "b_levels_kept": sum(state["codes"]["B"]) == 24}


def held_trail_digest(trail, field):
    """The sha256 of one field of a polish trail, each step `column:value value ...` and the steps `;`-joined (the
    frozen file stays small: the held cases keep their digests and the held column's aims in full)."""
    text = ";".join(step["column"] + ":" + " ".join(str(v) for v in step[field]) for step in trail)
    return hashlib.sha256(text.encode("ascii")).hexdigest()


def case_polish_held(held=True):
    """THE HELD FEATURES (lane CHG-b, plan P4-D492 part b): `polish_setup`'s twin with the binary `B`'s share target
    in `G`'s bands dropped by the grouping gate and HELD (its goal and aim nought in the plan, marked `held`): when
    `B`'s first round starts its goal is set to the covariance `B` then holds with the share encoding and its aim to
    the goal over its slope (`held_goals`), and the rounds move it like any aim; two rounds of each polished column
    in plan order, the second the last, as `case_polish`. Recorded: the held goal and aim as set, `B`'s aims after
    each of its re-sorts, and the sha256 (`held_trail_digest`) of every re-sort's places, aims and `X`'s `L1` bands.
    MUTANT (`held` False): the dropped target leaves `B`'s targets (lane CHG's polish), another trail."""
    n, columns, state, plan, sums = polish_setup()
    for name, targets in plan:
        if name == "B":
            if held:
                targets[1].update(goal=F(0), aim=F(0), held=True)
            else:
                del targets[1]
    trail = []
    set_goals = []
    turn = 0
    for rnd in range(2):
        for name, targets in plan:
            if rnd == 0 and any(t.get("held") for t in targets):
                co.held_goals(name, targets, state)
                set_goals += [[name, [[t["kind"], t["name"], co.b64_hex(t["goal"]), co.b64_hex(t["aim"])]
                                      for t in targets if t.get("held")]]]
            steps = co.POLISH_LAST_STEPS if rnd == 1 else 1
            for step in range(steps):
                moving = rnd == 0 or step + 1 < steps
                co.polish_column(columns[name], name, targets, sums[turn], state, moving)
                trail += [{"column": name, "index": list(columns[name]["index"]),
                           "aims": [co.b64_hex(t["aim"]) for t in targets],
                           "x_bands": list(state["bands"][("X", 1)])}]
            turn += 1
    return {"rows": n, "held_goals": set_goals, "steps": len(trail),
            "b_aims": [step["aims"] for step in trail if step["column"] == "B"],
            "index_sha256": held_trail_digest(trail, "index"), "aims_sha256": held_trail_digest(trail, "aims"),
            "x_bands_sha256": held_trail_digest(trail, "x_bands"),
            "multiset_kept": all(sorted(columns[c]["index"]) == list(range(n)) for c in columns),
            "b_levels_kept": sum(state["codes"]["B"]) == 24}


def polish_curve_inputs():
    """`case_polish_curve`'s published-fact inputs (lane CHG-b): a number of 12,000 readings (mean 120.0, spread 30.000,
    in the units contract 4.6d.0 (3) sets) in the five value bands of a partner whose `L1` totals are 2,400 rows each,
    every band's spread 28.0: means 105.0, 112.0, 117.0, 124.0 and 142.0 (a bend: kept), 115.0, 117.0, 119.0, 122.5 and
    129.0 (a bend past the point whose feature's mean square is under 0.01: dropped by the floor), 115.0, 117.5,
    120.0, 122.5 and 125.0 (a straight line: dropped), and 116.0, 118.0, 119.5, 121.5 and 125.0 (a small bend under
    the point on three degrees of freedom: dropped). Each as `(label, groups, column)`."""
    column = [1200, 30000, 12000]
    return [
        ("bend", [[2400, m, 280] for m in (1050, 1120, 1170, 1240, 1420)], column),
        ("bend_under_floor", [[2400, m, 280] for m in (1150, 1170, 1190, 1225, 1290)], column),
        ("line", [[2400, m, 280] for m in (1150, 1175, 1200, 1225, 1250)], column),
        ("small", [[2400, m, 280] for m in (1160, 1180, 1195, 1215, 1250)], column),
    ]


def polish_binary_curve_inputs():
    """`case_polish_curve`'s yes/no inputs (lane CHG-b): a yes/no column of 12,000 readings in the same five bands of
    2,400, its shares 0.0500, 0.0800, 0.1200, 0.2000 and 0.3500 (overall 0.1600; a bend on the threshold's scale: kept)
    and 0.0778, 0.1232, 0.1587, 0.2002 and 0.2810 (overall 0.1682; near a straight probit: dropped), in
    ten-thousandths. Each as `(label, groups, column)`."""
    return [
        ("binary_bend", [[2400, s] for s in (500, 800, 1200, 2000, 3500)], [1600, 12000]),
        ("binary_line", [[2400, s] for s in (778, 1232, 1587, 2002, 2810)], [1682, 12000]),
    ]


def case_polish_curve(curve=True):
    """THE CURVES (lane CHG-b, plan P4-D492 part b): each input of `polish_curve_inputs` read by `curve_target` over the
    partner's band scores and squared scores (`band_mean_scores` on five value bands of 2,400 rows): its statistic,
    decision and goal and the sha256 (hex, comma-joined) of its knots, its residuals from the squared partner score's
    fit and its feature's 4,096 values, beside the sha256 of the band scores (each band's two in turn) and of the grid;
    then each yes/no input of `polish_binary_curve_inputs` read by `binary_curve_target` (on the threshold's scale: its
    aim and slope beside); then `polish_setup`'s twin with
    `Y` given the kept bend as a curve target on `X` (its aim nought at the start), two rounds of each polished column as
    `case_polish`: `Y`'s aims after each of its re-sorts and the digests (`held_trail_digest`) of every re-sort's places,
    aims and `X`'s bands. MUTANT (`curve` False): `Y` without the curve target."""
    grid = co.curve_grid()
    scores = co.band_mean_scores([True] * 5, [2400] * 5)
    read = {}
    def digest(values):
        return hashlib.sha256(",".join(co.b64_hex(v) for v in values).encode("ascii")).hexdigest()

    out = {"scores_sha256": digest([v for pair in scores for v in pair]), "grid_sha256": digest(grid), "inputs": {}}
    for label, groups, column in polish_curve_inputs():
        made = co.curve_target(groups, column[0], column[1], column[2], scores, grid)
        if made is None:
            out["inputs"][label] = {"kept": False}
            continue
        knots, departures, statistic, values, goal = made
        read[label] = made
        out["inputs"][label] = {"kept": True, "knots_sha256": digest(knots), "departures_sha256": digest(departures),
                                "statistic": co.b64_hex(statistic), "goal": co.b64_hex(goal), "table_sha256": digest(values)}
    for label, groups, column in polish_binary_curve_inputs():
        made = co.binary_curve_target(groups, column[0], column[1], scores, grid)
        if made is None:
            out["inputs"][label] = {"kept": False}
            continue
        knots, residuals, statistic, values, goal, aim, slope = made
        out["inputs"][label] = {"kept": True, "knots_sha256": digest(knots), "departures_sha256": digest(residuals),
                                "statistic": co.b64_hex(statistic), "goal": co.b64_hex(goal), "aim": co.b64_hex(aim),
                                "slope": co.b64_hex(slope), "table_sha256": digest(values)}
    n, columns, state, plan, sums = polish_setup()
    if curve and "bend" in read:
        knots, departures, _statistic, values, goal = read["bend"]
        for name, targets in plan:
            if name == "Y":
                targets += [{"kind": "curve", "name": "X", "goal": goal, "aim": F(0), "slope": F(1), "level": 1,
                             "encoding": departures, "knots": knots, "table": values}]
    trail = []
    turn = 0
    for rnd in range(2):
        for name, targets in plan:
            steps = co.POLISH_LAST_STEPS if rnd == 1 else 1
            for step in range(steps):
                moving = rnd == 0 or step + 1 < steps
                co.polish_column(columns[name], name, targets, sums[turn], state, moving)
                trail += [{"column": name, "index": list(columns[name]["index"]),
                           "aims": [co.b64_hex(t["aim"]) for t in targets],
                           "x_bands": list(state["bands"][("X", 1)])}]
            turn += 1
    out.update({"steps": len(trail), "y_aims": [step["aims"] for step in trail if step["column"] == "Y"],
                "index_sha256": held_trail_digest(trail, "index"), "aims_sha256": held_trail_digest(trail, "aims"),
                "x_bands_sha256": held_trail_digest(trail, "x_bands"),
                "multiset_kept": all(sorted(columns[c]["index"]) == list(range(n)) for c in columns)})
    return out


def polish_spread_inputs():
    """`case_polish_spread`'s published-fact inputs (lane CHG-b): a number of 12,000 readings (mean 120.0, spread
    30.000) in twelve bands of 1,000 readings, its band means flat at 120.0, its band spreads (in tenths) and its
    published kurtosis: 17.0 and 60.0 in turn with a kurtosis of 5.2 (a spread by group: kept), 33.0 and 39.0 in turn
    with a kurtosis of 29.0 (a skewed column's chance spreads: dropped), 30.0 flat with 3.0 (dropped), and the first
    with no kurtosis published (not tested). Each as `(label, groups, column, kurtosis text or None)`."""
    column = [1200, 30000, 12000]
    return [
        ("by_group", [[1000, 1200, 170 if g % 2 else 600] for g in range(12)], column, "5.2"),
        ("skewed_chance", [[1000, 1200, 330 if g % 2 else 390] for g in range(12)], column, "29.0"),
        ("flat", [[1000, 1200, 300] for _g in range(12)], column, "3.0"),
        ("unpublished", [[1000, 1200, 170 if g % 2 else 600] for g in range(12)], column, None),
    ]


def case_polish_spread():
    """THE SPREAD TEST (lane CHG-b, plan P4-D492 part b): each input of `polish_spread_inputs` read as G16.3's spread
    test reads a `within` target (its band spreads from `within_target`, its counts, the column's kurtosis): the
    decision and the statistic (None where not tested), and the means' own decision (`beyond_chance` on the target's
    goal: dropped on every input, the means flat)."""
    out = {}
    for label, groups, column, kurtosis in polish_spread_inputs():
        _encoding, sds, goal = co.within_target(groups, column[0], column[1], column[2])
        counts = [g[0] for g in groups]
        kept, statistic = co.spreads_beyond_chance(counts, sds, None if kurtosis is None else co.b64(F(kurtosis)))
        out[label] = {"kept": kept, "statistic": None if statistic is None else co.b64_hex(statistic),
                      "means_kept": co.beyond_chance(counts, goal)}
    return out


def case_psd_projection():
    """G16.3's PSD projection (LANE MPg RULINGS 2 (2)) on three matrices: a 3 x 3 whose correlations no data can
    hold (0.9, 0.9, -0.9), a 4 x 4 with one refused pair read as 0 and an impossible triple, and the probe's near
    pair (0.997 beside 0.650 and 0.654), positive definite and so unchanged. Each published value is a binary64
    number; the projected matrix, the least eigenvalue and the largest change frozen to the bit."""
    cases = [
        [["1", "0.9", "0.9"], ["0.9", "1", "-0.9"], ["0.9", "-0.9", "1"]],
        [["1", "0.95", "0.95", "0"], ["0.95", "1", "0.5", "0.3"], ["0.95", "0.5", "1", "0.2"], ["0", "0.3", "0.2", "1"]],
        [["1", "0.997", "0.65"], ["0.997", "1", "0.654"], ["0.65", "0.654", "1"]],
    ]
    out = []
    for matrix in cases:
        held = [[co.b64(F(x)) for x in row] for row in matrix]
        projected, least, change = co.nearest_correlations(held)
        out += [{"matrix": [[co.b64_hex(x) for x in row] for row in held],
                 "projected": [[co.b64_hex(x) for x in row] for row in projected],
                 "least": co.b64_hex(least), "change": co.b64_hex(change)}]
    return out


def polish_target_inputs():
    """`case_polish_targets`' five sets: each a list of `(name, own count)`, and the published pairs `{(later, earlier):
    (printed r, count)}` in the moments' order. The r of 0.9 is printed as rule B prints it at 10,000 or 20,000 rows
    (ten-thousandths of z: 0.899996296914)."""
    r9 = 899996296914
    return {
        # Codex's first probe: X on the first half, Z on the second, Y throughout; XZ never observed.
        "halves": ([("X", 10000), ("Y", 20000), ("Z", 10000)], {(1, 0): (r9, 10000), (2, 1): (r9, 10000)}),
        # Codex's second: three disjoint cohorts of 10,000 rows observe XY, YZ and XZ apart.
        "cohorts": ([("X", 20000), ("Y", 20000), ("Z", 20000)],
                    {(1, 0): (r9, 10000), (2, 1): (r9, 10000), (2, 0): (-r9, 10000)}),
        # One row set whose three correlations no data can hold: projected, each move disclosed.
        "one_row_set": ([("X", 20000), ("Y", 20000), ("Z", 20000)],
                        {(1, 0): (r9, 20000), (2, 1): (-r9, 20000), (2, 0): (r9, 20000)}),
        # One row set, positive definite: every goal its published r.
        "one_row_set_kept": ([("X", 20000), ("Y", 20000), ("Z", 20000)],
                             {(1, 0): (997000000000, 20000), (2, 1): (654000000000, 20000), (2, 0): (650000000000, 20000)}),
        # Thirty numbers, the first one's partners: 29 published r of sizes 0.01 times ceil(k / 2), alternating
        # in sign, so the 24 largest leave out 1 to 4 and, of the tied 5 and 6, the later one. Every pair
        # of the others is unpublished, so their one row set holds pairs not published: nothing is projected.
        "partners": ([(f"N{k:02d}", 20000) for k in range(30)],
                     {(k, 0): ((-1) ** k * ((k + 1) // 2) * 10000000000, 20000) for k in range(1, 30)}),
    }


def case_polish_targets():
    """G16.3's correlation goals (lane MPg's repair 2, Codex's item 2, LANE MPg RULINGS 9 (2)) and a number's
    partners (the verify's item 2): for each set of `polish_target_inputs`, the goals (hex, None where no goal),
    the disclosed moves and, for `partners`, the chosen partners of the first number. The old projection
    zero-filled an unobserved pair and moved Codex's two probes' targets (0.9 to about 0.729; to about 0.5)."""
    out = {}
    for label, (columns, pairs) in polish_target_inputs().items():
        size = len(columns)
        own = [n for _name, n in columns]
        values = [[F(1) if a == b else None for b in range(size)] for a in range(size)]
        counts = [[0] * size for _ in range(size)]
        for (a, b), (printed, n) in pairs.items():
            values[a][b] = values[b][a] = co.b64(F(printed, 10 ** 12))
            counts[a][b] = counts[b][a] = n
        goals, moves = co.target_correlations(own, values, counts)
        entry = {"goals": [[None if g is None else co.b64_hex(g) for g in row] for row in goals],
                 "moves": [[b, a, co.b64_hex(p), co.b64_hex(g)] for b, a, p, g in moves]}
        if label == "partners":
            entry["chosen"] = co.chosen_partners(values[0], 0, goals[0])
        out[label] = entry
    return out


def _alternating(base, step, groups, n, sd=None):
    """`groups` published bands of `n` readings each, their means (or shares) `base` plus and minus `step` in turn
    (a last odd band at `base`), each with a band spread of `sd` where one is given; units as published."""
    out = []
    for g in range(groups):
        value = base if groups % 2 == 1 and g == groups - 1 else base + (step if g % 2 == 0 else -step)
        out += [[n, value] if sd is None else [n, value, sd]]
    return out


def polish_gate_edges():
    """`case_polish_gate`'s published-fact inputs at both sides of the gate's level: each `(label, kind, groups,
    column)`, the groups and the column in the units contract 4.6d.0 (3) sets at their counts (a mean in tenths, a
    column's spread in thousandths, a band's spread in tenths, a share in ten-thousandths). A 12-band `within`
    entry of 1,000 readings a band (a column of mean 120.0 and spread 30.000 at 12,000 readings), its means 1.5 and
    1.6 codes either side of the column's in turn (group chi-square 30.0 and about 34.1 on 11 degrees of freedom,
    the point about 31.43); a two-band split of 6,000 readings a band, 0.9 and 1.0 either side (about 10.8 and
    13.3 on one, the point about 11.16), and 0.6 (4.8: over the 0.05 point, under the 0.001 point); a binary's
    shares in 11 bands of 1,000 readings, its column share 0.2000, ten bands 0.0218 and 0.0219 either side in
    turn and one at 0.2000 (about 29.7 and 30.0 on ten, the point about 29.76). AND TWO ENTRIES WITH EMPTY BANDS
    (repair 1, skeptic 1's item 2: a band holding none of the column's readings, `[0]`, as a measurement taken in
    some bands only): a 12-band `within` entry whose bands 3 and 8 hold nothing and whose ten others hold 1,000
    readings 1.6 codes either side in turn (a column of 10,000 readings): about 28.4 on nine degrees of freedom,
    over the point there (about 28.06) and under the point on eleven (about 31.43), so it is kept only when k
    counts the bands holding a count; and a 12-band entry with ONE band holding readings (12,000 at 125.0), the
    other eleven empty: no grouping shown, dropped with no test taken (a point on nought degrees of freedom does
    not exist)."""
    live10 = _alternating(1200, 16, 10, 1000, 300)
    return [
        ("within12_under", "within", _alternating(1200, 15, 12, 1000, 300), [1200, 30000, 12000]),
        ("within12_over", "within", _alternating(1200, 16, 12, 1000, 300), [1200, 30000, 12000]),
        ("split_under", "within", _alternating(1200, 9, 2, 6000, 300), [1200, 30000, 12000]),
        ("split_over", "within", _alternating(1200, 10, 2, 6000, 300), [1200, 30000, 12000]),
        ("split_between", "within", _alternating(1200, 6, 2, 6000, 300), [1200, 30000, 12000]),
        ("shares11_under", "share", _alternating(2000, 218, 11, 1000), [2000, 11000]),
        ("shares11_over", "share", _alternating(2000, 219, 11, 1000), [2000, 11000]),
        ("empty12_live10", "within", live10[:3] + [[0]] + live10[3:7] + [[0]] + live10[7:], [1200, 30000, 10000]),
        ("empty12_live1", "within", [[0]] * 5 + [[12000, 1250, 300]] + [[0]] * 6, [1200, 30000, 12000]),
    ]


def polish_gate_plan():
    """`case_polish_gate`'s description: numbers `A`, `B` and `C` of 12,000 readings (means 120.0, 90.0 and 70.0,
    spreads 30.000, 20.000 and 10.000), a binary `F` (share 0.3000) and a 12-level grouping label `G`; published
    pairs B-A 0.3, C-A 0.01, C-B 0.02 (printed r over 10 ** 12, 12,000 rows each); `within` entries, in order:
    A in G's bands 1.6 codes either side (beyond chance), B in G's 1.0 either side (not), C in F's two bands
    (8,400 at 69.7, 3,600 at 70.7: beyond chance, a `within` of C and a `by` of F), A in F's (119.9, 120.2: not),
    B in F's (89.8, 90.6: over the 0.05 point only), F's shares in G's bands 0.0200 either side (not) and in B's four
    `L1` bands of 3,000 readings 0.0300 either side (beyond chance). Returns the columns, the pairs and the
    entries as `(column, by, groups)`, every one at level 1."""
    columns = {"A": [1200, 30000, 12000], "B": [900, 20000, 12000], "C": [700, 10000, 12000], "F": [3000, 12000]}
    pairs = {("B", "A"): 300000000000, ("C", "A"): 10000000000, ("C", "B"): 20000000000}
    split = [[8400, 697, 300], [3600, 707, 300]]
    entries = [
        ("A", "G", _alternating(1200, 16, 12, 1000, 300)),
        ("B", "G", _alternating(900, 10, 12, 1000, 200)),
        ("C", "F", split),
        ("A", "F", [[8400, 1199, 300], [3600, 1202, 300]]),
        ("B", "F", [[8400, 898, 200], [3600, 906, 200]]),
        ("F", "G", _alternating(3000, 200, 12, 1000)),
        ("F", "B", _alternating(3000, 300, 4, 3000)),
    ]
    return columns, pairs, entries


def _gate_targets(columns, pairs, entries):
    """The ungated plan of `polish_gate_plan`'s description, as G16.3 builds it before the gate: each number's pairs
    in the moments' order (A, B, C), then its `within` entries in order; the binary's `by` targets (each number's
    entry grouped by it), then its `share` targets. Each goal emulated (`within_target`, `share_target`)."""
    numbers = ["A", "B", "C"]
    plan = []
    for name in numbers:
        targets = []
        for other in numbers:
            key = (name, other) if (name, other) in pairs else (other, name)
            if other != name and key in pairs:
                targets += [{"kind": "pair", "name": other, "level": 1, "goal": co.b64(F(pairs[key], 10 ** 12)),
                             "n": 12000}]
        mean, sd, n = columns[name]
        for column, by, groups in entries:
            if column == name:
                encoding, _sds, goal = co.within_target(groups, mean, sd, n)
                targets += [{"kind": "within", "name": by, "level": 1, "goal": goal, "encoding": encoding,
                             "counts": [group[0] for group in groups]}]
        plan += [(name, targets)]
    targets = []
    for column, by, groups in entries:
        if by == "F" and column in numbers:
            mean, sd, n = columns[column]
            encoding, _sds, goal = co.within_target(groups, mean, sd, n)
            targets += [{"kind": "by", "name": column, "level": 1, "goal": goal, "encoding": encoding,
                         "counts": [group[0] for group in groups]}]
    for column, by, groups in entries:
        if column == "F":
            encoding, goal = co.share_target(groups, columns["F"][0], columns["F"][1])
            targets += [{"kind": "share", "name": by, "level": 1, "goal": goal, "encoding": encoding,
                         "counts": [group[0] for group in groups]}]
    plan += [("F", targets)]
    return plan


def plan_digest(listing):
    """The sha256 of a plan's listing (`{column: [[kind, name, goal or "held"], ...]}`), its JSON with sorted keys and
    no spaces: three of `case_polish_gate`'s mutant plans are frozen so, the file kept under its size bound."""
    return hashlib.sha256(json.dumps(listing, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()


def case_polish_gate():
    """G16.3's GROUPING GATE (lane CHG, plan P4-D492; LANE CHG RULINGS 1 (2) and (8)): the 0.001 point by Wilson and
    Hilferty's cube on eleven counts of degrees of freedom from 1 to 1,000 (and the 0.05 point, the level's mutant);
    each published-fact input of `polish_gate_edges` (two with empty bands among them) with its goal, statistic,
    degrees of freedom and both decisions; and the plan of `polish_gate_plan`'s
    description kept by the gate, beside its six MUTANTS (the level 0.05's, no feature held's and no whole vector's as
    `plan_digest`s): the gate off (every target kept), the level 0.05, a
    dropped target kept with a goal of nought, the correlations gated too, no feature held (lane CHG's plan), no
    and no whole vector (lane CHG-b: `A`'s kept means in the twelve bands of the label `G` aimed band by band, eleven
    targets).
    Each kept target is `[kind, name, goal]` in plan order, a held feature `[kind, name, "held"]` (lane CHG-b: the
    yes/no column `F` keeps the `by` and `share` targets the gate dropped, their goals set from the walk), a column
    left with none absent."""
    degrees = [1, 2, 3, 4, 5, 10, 11, 20, 50, 100, 1000]
    z005 = co.b64(F("1.6449"))
    edges = {}
    for label, kind, groups, column in polish_gate_edges():
        if kind == "within":
            _encoding, _sds, goal = co.within_target(groups, column[0], column[1], column[2])
        else:
            _encoding, goal = co.share_target(groups, column[0], column[1])
        counts = [group[0] for group in groups]
        live = [n for n in counts if n > 0]
        edges[label] = {"kind": kind, "groups": groups, "column": column, "goal": co.b64_hex(goal),
                        "df": len(live) - 1, "statistic": co.b64_hex(co.b64_mul(sum(live), goal)),
                        "kept": co.beyond_chance(counts, goal), "kept_005": co.beyond_chance(counts, goal, z005)}
    columns, pairs, entries = polish_gate_plan()
    counts_of = {(column, by, 1): [group[0] for group in groups] for column, by, groups in entries}
    plan = _gate_targets(columns, pairs, entries)
    # A yes/no column's curves (lane CHG-b) are measured and not adopted (G16.3's `_POLISH_BINARY_CURVES` off), so
    # the description's yes/no column `F` gains none; no number of it holds a partner's bands.
    curved = plan
    def listed(gated):
        return {column: [[t["kind"], t["name"], "held" if t.get("held") else co.b64_hex(t["goal"])] for t in targets]
                for column, targets in gated}

    return {
        "points": {f"{df}": co.b64_hex(co.gate_point(df)) for df in degrees},
        "points_005": {f"{df}": co.b64_hex(co.gate_point(df, z005)) for df in degrees},
        "edges": edges,
        "plan_ungated": listed(plan),
        "plan": listed(co.whole_vectors(co.gated_plan(curved, counts_of), {"G", "F"})),
        "plan_mutant_off": listed(co.gated_plan(curved, counts_of, "off")),
        "plan_mutant_level_005_sha256": plan_digest(listed(co.whole_vectors(co.gated_plan(curved, counts_of, "level_005"),
                                                                            {"G", "F"}))),
        "plan_mutant_nought": listed(co.gated_plan(curved, counts_of, "nought")),
        "plan_mutant_pairs": listed(co.gated_plan(curved, counts_of, "pairs")),
        "plan_mutant_held_off_sha256": plan_digest(listed(co.whole_vectors(co.gated_plan(curved, counts_of, "held_off"),
                                                                           {"G", "F"}))),
        "plan_mutant_whole_off_sha256": plan_digest(listed(co.gated_plan(curved, counts_of))),
    }


def implied_nofit_inputs(half):
    """`case_implied_nofit`'s inputs at `half` rows a cell: the table, each row's cell, the parent's ranks (None in
    cell 0, which holds no parent reading; 0 to half - 1 in cell 1) and each row's hidden sum from SplitMix64 words."""
    n = 2 * half
    words = splitmix64(0x4E0F, 3 * n)
    sums = [sum((w >> shift) & 0xFFFF for w in words[3 * r:3 * r + 3] for shift in (0, 16, 32, 48)) for r in range(n)]
    return [[0, half], [half, 0]], [0] * half + [1] * half, [None] * half + list(range(half)), sums


def case_implied_nofit(half=20):
    """G16.2 step 2 where no published cell holds a reading of every used parent (lane MPg's repair 2, Codex's
    item 4): the family table ((0, half), (half, 0)), the parent's band scores (None, 0), the child's (None, 0),
    one ranged parent. Cell 0 holds the child's readings but no parent reading, cell 1 the parent's readings
    and no child score, so the slope fits nothing: no coefficient, sigma 1, cell means (0, None), and every
    row's latent order is `sigma z + mu_c`. At 20 rows a cell the forty values are frozen; at 10,000 (the
    floor's 20,000 rows) their count, the first four and the sha256 of their hex list, comma-joined."""
    table, cells, ranks, sums = implied_nofit_inputs(half)
    slope = co.implied_slope(table, [2], [[None, F(0)]], [0], [None, F(0)])
    z = [F(s - 393210, 65536) for s in sums]
    latent = co.implied_latent(cells, slope, [(ranks, half)], z)
    hexes = [co.b64_hex(x) for x in latent]
    out = {"half": half, "used": list(slope[0]), "beta": [co.b64_hex(b) for b in slope[1]],
           "sigma": co.b64_hex(slope[2]), "means": [None if m is None else co.b64_hex(m) for m in slope[3]]}
    if half <= 20:
        out["latent"] = hexes
    else:
        out["count"] = len(hexes)
        out["head"] = hexes[:4]
        out["sha256"] = hashlib.sha256(",".join(hexes).encode("ascii")).hexdigest()
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


def case_te_raise():
    """`w_te` at the oracle's default (contract 4.6b.14, amended 2026-11-02: nought): a time-and-event
    pair named to the setting raises its family by `w_te * n`, nothing at the default. The search with
    the pair named stands beside it, the same chain as without it (the keyed draw reads the setting's name, so
    both settings are named alike)."""
    lads, n = search_lads()
    setting = co.Setting("trial", TEST_KEY, te_pairs=[("A", "B")])
    return {"raise": _fraction_text(co.raise_of(setting, n, "B", ["A"])), "chain": case_search(setting)["chain"]}


def case_search(setting=None):
    lads, n = search_lads()
    if setting is None:
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
    """Each label column's ladder from joint rows `[(values, count)]`; `specs` lists, for each
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
    """G16.6's order: the units in published noughts before the distance, and the last tie,
    two tables equal on noughts, distance and squares, the greater in row-major order taken."""
    table, named = co.moved_target([[10, 10], [10, 10]], [21, 19], [20, 20])
    first, first_named = co.moved_target([[20, 0, 10], [0, 20, 10]], [11, 49], [0, 42, 18])
    return {"moved": table, "units_in_noughts": [list(x) for x in named],
            "noughts_first": {"moved": first, "units_in_noughts": [list(x) for x in first_named]}}


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
    codes = {"X": (F(0), F(98))}
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



# --- G16.12 items 8, 9, 9b, 10 and 12 (Codex's item 4 of the landing's review) -----------


def case_cell_index(width=None):
    """G16.12 item 8: the cell index read back, at 3 bytes and at 4 (MUTANT `width` 3: every
    index packed in 3 bytes whatever the column holds)."""
    out = {}
    for label, cells, indices in (("three", 16_777_215, [0, 1, 255, 65_536, 16_777_214]),
                                  ("four", 20_000_000, [0, 16_777_215, 16_777_216, 19_999_999])):
        data = co.pack_indices(indices, cells, width)
        out[label] = {"cells": cells, "indices": indices, "bytes": bytes(data).hex(),
                      "read_back": co.unpack_indices(data, cells, width)}
    return out


def case_stray_rows(eligible_gives=False):
    """G16.12 item 9: a stray row given a cell by an ineligible column (`X`, beside the
    eligible `A` and `Y`), and one with no ineligible giver, which stays and is named
    (MUTANT: an eligible column's cell moved)."""
    columns = ["A", "X", "Y"]
    givers = columns if eligible_gives else None
    out = {}
    for label, rows in (("giver", [["4", "x1", "8"], ["", "", ""], ["6", "x2", "2"]]),
                        ("no_giver", [["4", "", "8"], ["", "", ""], ["", "x2", ""]])):
        table, exchanges, stayed = co.stray_rows(rows, columns, eligible={"A", "Y"}, rule_named=set(), givers=givers)
        moved_eligible = sum(1 for r in range(len(rows)) for j in (0, 2) if table[r][j] != rows[r][j])
        out[label] = {"rows": table, "exchanges": [list(e) for e in exchanges], "stayed": stayed,
                      "eligible_cells_moved": moved_eligible}
    return out


def case_stray_beside_a_computed_column(computed_gives=False):
    """G16.12 item 9b: `B` computed as `A + D` (`D` derived, no column of the table), one
    stray row. Without another column the computed column gives no cell and the row stays,
    named; beside `C`, a column no rule computes or reads, the row takes `C`'s cell (MUTANT:
    the computed column giving its cell, which breaks `B = A + D` on 2 rows)."""
    d = [F(2), None, F(1)]
    out = {}
    for label, columns, rows in (("alone", ["A", "B"], [["3", "5"], ["", ""], ["6", "7"]]),
                                 ("beside_c", ["A", "B", "C"], [["3", "5", "c1"], ["", "", ""], ["6", "7", "c2"]])):
        givers = [c for c in columns if c != "A"] if computed_gives else None
        table, exchanges, stayed = co.stray_rows(rows, columns, eligible={"A"}, rule_named={"A", "B"}, givers=givers)
        a = [F(r[0]) if r[0] != "" else None for r in table]
        b = [F(r[1]) if r[1] != "" else None for r in table]
        breaking = sum(1 for x, y in zip(co.computed_column(a, d), b) if x != y)
        out[label] = {"rows": table, "exchanges": [list(e) for e in exchanges], "stayed": stayed,
                      "rows_breaking_b_eq_a_plus_d": breaking}
    return out


def joint_move_rows():
    """G16.0's case: `AB` [[60, 40], [40, 60]], `C | AB` [[60, 0], [0, 40], [0, 40], [60,
    0]], `D | AC` [[30, 30], [20, 20], [30, 30], [20, 20]] on 200 rows."""
    return [(("a0", "b0", "c0", "d0"), 30), (("a0", "b0", "c0", "d1"), 30),
            (("a0", "b1", "c1", "d0"), 20), (("a0", "b1", "c1", "d1"), 20),
            (("a1", "b0", "c1", "d0"), 20), (("a1", "b0", "c1", "d1"), 20),
            (("a1", "b1", "c0", "d0"), 30), (("a1", "b1", "c0", "d1"), 30)]


def case_joint_move(members_test=False):
    """G16.12 item 10: `B`'s totals made [80, 120] in the twin, so `AB` moves, then `C | AB`,
    and `D | AC` takes its moved target by G16.0's test on the parent cells, every target
    met (MUTANT: the first build's test on members' totals alone, which leaves `D | AC` no
    table to deal)."""
    lads = _rows_lads(joint_move_rows(), [("A", "binary", [("a0", 100), ("a1", 100)]),
                                          ("B", "binary", [("b0", 100), ("b1", 100)]),
                                          ("C", "binary", [("c0", 120), ("c1", 80)]),
                                          ("D", "binary", [("d0", 100), ("d1", 100)])])
    chain = [co.Family("A", 0, [], None, [lads["A"].band_totals(0)]),
             co.Family("B", 0, [("A", 0)], 0, co.table_of(lads, "B", 0, [("A", 0)])),
             co.Family("C", 0, [("A", 0), ("B", 0)], 1, co.table_of(lads, "C", 0, [("A", 0), ("B", 0)])),
             co.Family("D", 0, [("A", 0), ("C", 0)], 2, co.table_of(lads, "D", 0, [("A", 0), ("C", 0)]))]
    twin = {"A": [[("a0", 0)] * 100, [("a1", 1)] * 100], "B": [[("b0", 0)] * 80, [("b1", 1)] * 120],
            "C": [[("c0", 0)] * 120, [("c1", 1)] * 80], "D": [[("d0", 0)] * 100, [("d1", 1)] * 100]}
    moved = {}
    index, lists, dealt = co.walk_rows(chain, lads, twin, _words_for(0x10AB, 4, 200), moved=moved,
                                       members_test=members_test)
    out_moved = {}
    for fi, entry in sorted(moved.items()):
        if entry[0] == "undealable":
            out_moved[str(fi)] = {"undealable": True, "row_totals": entry[1], "parent_counts": entry[2]}
        else:
            out_moved[str(fi)] = {"table": entry[0], "units_in_noughts": [list(x) for x in entry[1]]}
    targets = [moved[fi][0] if fi in moved else fam.table for fi, fam in enumerate(chain)]
    texts = {c: [lists[c][index[c][r]][0] for r in range(200)] for c in ("A", "C")}
    joint = [sum(1 for r in range(200) if (texts["A"][r], texts["C"][r]) == (a, c))
             for a in ("a0", "a1") for c in ("c0", "c1")]
    return {"published": [fam.table for fam in chain], "moved": out_moved, "dealt": dealt,
            "families_dealt": len(dealt), "met": len(dealt) == 4 and dealt == targets, "ac_joint": joint}


def case_rules_only(section_runs=True):
    """G16.12 item 12: a RULES-ONLY description, one eligible column `A` (36 readings 1 to 36,
    4 absent) beside a computed `B = A + D` and its derived family `{D | A}` at `A`'s `L2`:
    `A` dealt alone in its one cell, `D` dealt as `A`'s child, `B` written (MUTANT: the
    section not running, which writes no `B`)."""
    a_values = [None] * 4 + list(range(1, 37))
    a_cells = [("missing",) if v is None else ("value", F(v)) for v in a_values]
    d_names = ["missing"] * 4 + ["short"] * 12 + ["long"] * 6 + ["short"] * 8 + ["long"] * 10
    d_cells = [("missing",) if v == "missing" else ("level", v) for v in d_names]
    lads = {"A": co.ladder_of("A", "count", a_cells, rungs=_rungs_of(range(1, 37)), floor=1, position=0),
            "D": co.ladder_of("D", "derived", d_cells, levels=[("short", 20), ("long", 16)], floor=1, position=1)}
    chain = [co.Family("A", 0, [], None, [lads["A"].band_totals(0)]),
             co.Family("D", 0, [("A", 2)], 0, co.table_of(lads, "D", 0, [("A", 2)]))]
    twin = {"A": _twin_groups(lads["A"], a_cells),
            "D": [[("", None)] * 4, [("1", F(1))] * 20, [("7", F(7))] * 16]}
    index, lists, dealt = co.walk_rows(chain, lads, twin, _words_for(0x12C0, 2, 40))
    a = [lists["A"][index["A"][r]][1] for r in range(40)]
    d = [lists["D"][index["D"][r]][1] for r in range(40)]
    b = co.computed_column(a, d) if section_runs else [None] * 40
    return {"d_table": chain[1].table, "dealt": dealt, "met": dealt == [fam.table for fam in chain],
            "b": [None if x is None else _fraction_text(x) for x in b],
            "b_written": sum(1 for x in b if x is not None),
            "rows_breaking_a_le_b": sum(1 for x, y in zip(a, b) if x is not None and y is not None and y < x),
            "d_beside_an_absent_a": sum(1 for x, y in zip(a, d) if x is None and y is not None)}


# --- lane CHb's cases (plan P4-D435): the decimal rung, the groups a band joins, the hashes ---


def case_decimal_rung(exact=False):
    """A cell written `114.7` beside a rung published as 114.7: read as the binary64 value nearest
    its text it stands AT the rung, in the band above (mutant: the cell read exactly, below it)."""
    texts = ["114.5"] * 20 + ["114.7"] * 15 + ["114.9"] * 25
    rung = co.reading_of("114.7")
    read = (lambda text: F(text)) if exact else co.reading_of
    cells = [("value", read(text)) for text in texts]
    lad = co.ladder_of("bp", "continuous", cells, rungs={"p50": rung}, floor=11, position=0)
    return {"rung": co.b64_hex(rung), "l0": lad.as_dict()["l0"], "totals": lad.totals}


def case_interface_join(earlier_first=False):
    """The interface's groups joined into `L0` bands (method G16.0): absent cells the reservation's
    shortfall leaves a number column whose ladder holds `other` and no `missing` band join the band
    holding the NEXT starting band in band order, the lowest range, not `other` before it; on a
    label column cells of a withheld level beside no pool join the last level's band, absent cells
    beside no `missing` band the first level's (mutant: the band before preferred)."""
    number = co.ladder_of("x", "count", [("other",)] * 12 + [("value", F(v)) for v in [1] * 30 + [5] * 30],
                          rungs={"p50": F(5)}, floor=11, position=0)
    groups = [(("range", 0), [("1", F(1))] * 30), (("range", 1), [("5", F(5))] * 30),
              ("missing", [("", None)] * 3), ("other", [("n/a", None)] * 12)]
    label = co.ladder_of("g", "categorical", [("level", "a")] * 25 + [("level", "b")] * 35,
                         levels=[("a", 25), ("b", 35)], floor=11, position=1)
    label_groups = [(("level", "a"), [("a", 0)] * 25), (("level", "b"), [("b", 1)] * 31),
                    ("missing", [("", None)] * 2), ("other", [("c", None)] * 2)]
    # An `L0` band joining two starting ranges hands ONE range group (G4.2b): the 3s'
    # five rows merge into the 1s' band, so the second range group is the 5s' band.
    merged = co.ladder_of("m", "count", [("value", F(v)) for v in [1] * 30 + [3] * 5 + [5] * 30],
                          rungs={"p25": F(3), "p50": F(5)}, floor=11, position=2)
    merged_groups = [(("range", 0), [("1", F(1))] * 30 + [("3", F(3))] * 5), (("range", 1), [("5", F(5))] * 30)]
    out_merged = co.interface_bands(merged, merged_groups)
    if earlier_first:
        out_number = co.interface_bands(number, [g for g in groups if g[0] != "missing"])
        out_number[0] += groups[2][1]
        out_label = co.interface_bands(label, label_groups[:2])
        out_label[len(out_label) - 1] += label_groups[2][1] + label_groups[3][1]
    else:
        out_number = co.interface_bands(number, groups)
        out_label = co.interface_bands(label, label_groups)
    return {
        "number_l0": number.as_dict()["l0"],
        "number_bands": [[text for text, _ in band] for band in out_number],
        "label_l0": label.as_dict()["l0"],
        "label_bands": [[text for text, _ in band] for band in out_label],
        "merged_l0": merged.as_dict()["l0"],
        "merged_bands": [len(band) for band in out_merged],
    }


def case_reader_bands(interface_other=False):
    """A column made without its band totals (rule B3), its twin's cells banded by the reader's
    reading of each (method G16.0 (h), lane CHb's first repair): a column whose real cells hold
    12 outside its pair of affixes, 30 at 1 and 30 at 5 publishes `other` and two ranges; the
    twin writes 28 at 1, 32 at 5, 12 outside the pair and 3 absent, the absent ones joining the
    lowest range (no `missing` band). Mutant: the interface's grouping of a column whose readings
    were not supplied, every present cell in `other` (the build's quirk the skeptics measured
    on the claims' adjustment)."""
    real = [("other",)] * 12 + [("value", F(1))] * 30 + [("value", F(5))] * 30
    lad = co.ladder_of("adj", "affixed_number", real, rungs={"p50": F(5)}, floor=11, position=0)
    twin = [("value", F(1))] * 28 + [("value", F(5))] * 32 + [("other",)] * 12 + [("missing",)] * 3
    if interface_other:
        read = [cell if cell[0] == "missing" else ("other",) for cell in twin]
    else:
        read = twin
    bands = co.reader_bands(lad, read, {"p50": F(5)})
    return {"l0": lad.as_dict()["l0"], "published": lad.totals,
            "twin_totals": [bands.count(b) for b in range(len(lad.l0))], "first_bands": bands[:4] + bands[-4:]}


def case_row_hash(separators=False, raw=False):
    """The content hash of 4.6b.8: Codex's two rows under columns `A` and `B` take two hashes in
    the length-framed form (mutant: the first build's separator bytes give them one); the table's
    hash is free of row order and leaves out a row holding nothing in every column; and a cell
    holding nothing is the empty text, so `["x", ""]` and `["x", " \t"]` take one hash (lane
    CHb's second repair, Codex's item 4; mutant `raw`: each cell framed as written)."""
    names = ["A", "B"]
    first = co.row_hash(names, ["x\u001eB\u001fy", "z"], separators=separators, raw=raw)
    second = co.row_hash(names, ["x", "y\u001eB\u001fz"], separators=separators, raw=raw)
    rows = [["3", "red"], ["4", ""], ["3", "red"]]
    empty = co.row_hash(names, ["x", ""], separators=separators, raw=raw)
    spaces = co.row_hash(names, ["x", " \t"], separators=separators, raw=raw)
    return {
        "codex_rows_differ": first != second,
        "first": first.hex(),
        "table": co.table_hash(names, rows).hex(),
        "table_shuffled": co.table_hash(names, [rows[2], rows[0], rows[1]]).hex(),
        "table_with_a_blank_row": co.table_hash(names, rows + [["", " "]]).hex(),
        "blank_and_spaces_alike": empty == spaces,
        "spaces_row": spaces.hex(),
    }


def case_band_codes(two_bytes=False):
    """G16.1's band code at the widths' edges (lane CHb's second repair, Codex's item 2): the
    fewest bytes holding a level's count of bands, and the codes 0, 255, 256, 65,535 and 65,536
    of a level of 65,537 bands read back whole (mutant: the first build's two bytes above 255
    bands, which reads band 65,536 back as band 0)."""
    counts = [1, 255, 256, 65_535, 65_536, 65_537, 16_777_215, 16_777_216]
    width = (lambda bands: 2 if bands > 255 else 1) if two_bytes else co.band_code_width
    codes = [0, 255, 256, 65_535, 65_536]
    data = co.pack_band_codes(codes, 65_537, width=width(65_537))
    return {"widths": [width(bands) for bands in counts],
            "codes": co.unpack_band_codes(data, 65_537, width=width(65_537))}


def case_reader_joins(join="next"):
    """G16.0's reading (h), a kind no `L0` band joins (lane CHb's second repair, its verify's item
    1): (a) a number column whose ladder holds its two ranges alone, a cell outside the column's
    reading and an absent cell joining the lowest range, the NEXT starting band; (b) beside an
    `other` band and no `missing` band, absent cells joining the lowest range, not `other` before
    it; (c) a ladder of `other` and `labels` alone, absent cells joining `labels`, the band before,
    since none follows. Mutants: the next band never tried (the verify's V1) and the one before
    never tried, each answering 'no band' where its side is the only one."""
    rungs = {"p50": F(5)}
    low, high = ("range", None, "p50"), ("range", "p50", None)
    cases = {
        "ranges_alone": (co.Ladder("a", "count", [[low], [high]], [30, 30], [[0, 1]], [[0, 1]], [], [], [True, True]),
                         [("value", F(1)), ("other",), ("value", F(9)), ("missing",), ("other",)]),
        "other_beside_ranges": (co.Ladder("b", "count", [["other"], [low], [high]], [12, 30, 30], [[0], [1, 2]],
                                          [[0, 1, 2]], [], [], [False, True, True]),
                                [("missing",), ("other",), ("value", F(9)), ("missing",)]),
        "kinds_alone": (co.Ladder("c", "count", [["other"], ["labels"]], [20, 20], [[0, 1]], [[0, 1]], [], [],
                                  [False, False]),
                        [("other",), ("labels",), ("missing",), ("missing",)]),
    }
    out = {}
    for name, (lad, cells) in cases.items():
        try:
            out[name] = co.reader_bands(lad, cells, rungs, join=join)
        except ValueError:
            out[name] = "no band"
    return out


def case_sample_key(cut=False):
    """The self-test's sample on 400 rows, 200 of `0,0` beside 200 of `1,1`, `m` = 100: exactly 100
    rows, about half of each (mutant: the first build's cut on the content hash, which takes every
    copy of a row or none)."""
    names = ["a", "b"]
    hashes = [co.row_hash(names, ["0", "0"])] * 200 + [co.row_hash(names, ["1", "1"])] * 200
    taken = co.sample_of(hashes, 100, cut=cut)
    return {"rows": len(taken), "of_the_first": sum(1 for at in taken if at < 200),
            "of_the_second": sum(1 for at in taken if at >= 200), "first_places": taken[:8]}


# --- rules between columns (contract 4.6b.7; lane RO, plan P4-D459) ---------------------


def _texts(values):
    return [co.written_sum(v) for v in values]


def case_rules_limit():
    """MR.1's limit `L(n) = max(f, floor(n / 100))` at the floor of 11."""
    return [[n, co.rule_limit(n, 11)] for n in (500, 1100, 1199, 20000, 20099, 2000000)]


def skeptic_one_readings():
    """Skeptic 1's table of MR.6 (e): readings 0 to 9 on 24, 23, 1, 23, 22, 23, 23, 47, 22 and 24 rows."""
    out = []
    for value, rows in zip(range(10), (24, 23, 1, 23, 22, 23, 23, 47, 22, 24)):
        out += [value] * rows
    return out


def case_rules_levels(first_text=False):
    """D's four levels on skeptic 1's table, right-closed totals and rule 1 (MUTANT: the first text's rule 1)."""
    readings = skeptic_one_readings()
    out = []
    for name, percents, edges in co.derived_levels(readings):
        totals = co.band_totals(edges, readings)
        out += [{"name": name, "edges": _texts(edges), "totals": totals,
                 "rule1": co.rule_one(totals, percents, 11, first_text=first_text)}]
    return out


def case_rules_partition():
    """Proposition T read for the whole partition at `f` = 11, `L` = 200: `R` from 11 to 212."""
    return {"passing": [r for r in range(11, 213) if co.partition_passes(r, 11, 200)],
            "classes": [[v, 300, str(co.class_of(v, 300, 11, 200))] for v in (0, 10, 11, 150, 200, 201)],
            "phrase_only": [str(co.class_of(v, 300, 11, 200, phrase_only=True)) for v in (10, 11)]}


def case_rules_family(rule5=True):
    """A derived option in the count class 15, its band holding 0 cut into 15 below and 9 at or above 0
    (rule 5 refuses it; MUTANT: rule 5 off), and the same table in the phrase class (eligible)."""
    edges = [F(0), F(4)]
    totals = [24, 60, 60]
    table = [[24, 60, 60, 0], [0, 0, 0, 30]]
    counted = co.derived_eligible(edges, (25, 75), totals, table, {1}, True, set(), 15, 1, 11, rule5=rule5)
    phrase = co.derived_eligible(edges, (25, 75), totals, table, {1}, True, set(), "phrase", 1, 11, rule5=rule5)
    sixth = co.derived_eligible([F(1, 4), F(3, 4)], (25, 75), totals, table, {1}, True, set(), "phrase", 1, 11)
    return {"count": list(counted), "phrase": list(phrase), "rule6": list(sixth)}


def case_rules_readings():
    """D's readings in the twin (MR.2): a gap of 7 on every row; gaps of 0 and 1 day on half the rows
    each, its median edge 1/2 alone; a count class of 15 below 0; the highest band of an L2 level; an
    empty highest band."""
    out = {}
    seven = [7] * 200
    for name, percents, edges in co.derived_levels(seven):
        if name == "L0":
            totals = co.band_totals(edges, seven)
            out["seven"] = {"edges": _texts(edges), "totals": totals,
                            "readings": [_texts(b) for b in co.derived_readings(edges, totals, totals, percents, 0, 1)]}
    halves = [0] * 100 + [1] * 100
    for name, percents, edges in co.derived_levels(halves):
        if name == "L2":
            totals = co.band_totals(edges, halves)
            out["halves"] = {"edges": _texts(edges), "totals": totals,
                             "readings": [_texts(b) for b in co.derived_readings(edges, totals, totals, percents, 0, 1)]}
    counted = [-1] * 15 + [0] * 45 + [2] * 70 + [5] * 70
    for name, percents, edges in co.derived_levels(counted):
        if name == "L2":
            totals = co.band_totals(edges, counted)
            out["count15"] = {"edges": _texts(edges), "totals": totals,
                              "readings": [_texts(b) for b in co.derived_readings(edges, totals, totals, percents, 15, 1)]}
    spread = [x // 10 for x in range(300)]
    for name, percents, edges in co.derived_levels(spread):
        if name == "L1":
            totals = co.band_totals(edges, spread)
            out["spread_l1"] = {"edges": _texts(edges), "totals": totals,
                                "readings": [_texts(b) for b in co.derived_readings(edges, totals, totals, percents, 0, 1)]}
    capped = [x % 20 for x in range(60)] + [30] * 140
    for name, percents, edges in co.derived_levels(capped):
        if name == "L2":
            totals = co.band_totals(edges, capped)
            out["capped_l2"] = {"edges": _texts(edges), "totals": totals,
                                "readings": [_texts(b) for b in co.derived_readings(edges, totals, totals, percents, 0, 1)]}
    return out


def case_rules_written():
    """MR.2's table of number forms, and a clock sum held at the day's last minute."""
    return {"forms": [co.written_sum(43), co.written_sum(F(142, 100)), co.written_sum(43, "leading_plus"),
                      co.written_sum(43, "leading_zero", 5), co.written_sum(1043, group=","),
                      co.written_sum(-5, "leading_plus"), co.written_sum(F(-25, 10))],
            "clock": [co.held_clock(86280, 180, 60), co.held_clock(86270, 30, 60), co.held_clock(3600, -30, 60)]}


def case_rules_forms():
    """`B` in its own form (lane RO's repair 1): a sum in a declared decimal comma and grouped, an affixed
    sum, both; `A`'s offset written in `B`'s first offset's spelling."""
    forms = [co.written_form(co.written_sum(F(123456, 100), group=","), comma=True),
             co.written_form(co.written_sum(1769), prefix="", suffix=" mg"),
             co.written_form(co.written_sum(F(-25, 10)), comma=True, prefix="$ ", suffix=""),
             co.written_form(co.written_sum(43, "leading_zero", 5))]
    offsets = [co.offset_like(7200, "+02:00"), co.offset_like(7200, "+0200"), co.offset_like(-18000, "-05"),
               co.offset_like(19800, "+05"), co.offset_like(0, "Z", "lower"), co.offset_like(0, "+00:00"),
               co.offset_like(3600, "Z")]
    return {"forms": forms, "offsets": offsets}


def case_rules_one_band(amended=True):
    """MR.7's one-band item per option (AMENDED 2026-11-05): a level with no edge NOT WORTH unless the gap is 0
    on 99 of 100 rows where both read; scores at n = 20,000 (MUTANT: the build's reading, one band judged only
    where no level with an edge is eligible, so it keeps its score beside one)."""
    out = []
    for edges, zero, both, edged_beside in (((), 0, 20000, True), ((), 2400, 20000, True), ((), 19800, 20000, True),
                                            ((), 19799, 20000, False), ((F(0), F(3)), 0, 20000, True), ((), 0, 0, False)):
        worth = co.one_band_worth(edges, zero, both) if amended else (bool(edges) or edged_beside or co.one_band_worth(edges, zero, both))
        out += [{"edges": len(edges), "zero": zero, "both": both, "worth": worth,
                 "score": str(co.rule_option_score(worth, F(-30), 20000))}]
    return out


def case_rules_items(amended=True):
    """MR.7's items as amended 2026-11-05 (LANE RO RULINGS 3): the association read as the smaller of D's
    share and B's own (MUTANT: D's share alone, the build's), the tighter-rule item with its clause and its
    tie (MUTANT: the build's loop, no clause and no tie), and a presence's share between bands."""
    d_ten = [x % 10 for x in range(40)]
    by_ten = [x % 10 for x in range(40)]
    flat = [x // 4 for x in range(40)]
    groups = [x % 4 for x in range(40)]
    lost_kept = [(co.share_between(d_ten, by_ten), co.share_between(flat, by_ten)),
                 (co.share_between(d_ten, groups), co.share_between(d_ten, groups))]
    association = co.association_lost(lost_kept) if amended else max(lost for lost, _kept in lost_kept)
    if amended:
        tight = [co.tighter_refuses(("arrived_at", 60, 70), [("seen_at", 30, 40)], {"seen_at"}),
                 co.tighter_refuses(("arrived_at", 0, 40), [("left_at", 0, 0)], set()),
                 co.tighter_refuses(("arrived_at", 0, 0), [("left_at", 0, 40)], set())]
    else:
        tight = [True, False, False]
    presence = co.share_between([1, 1, 1, 0, 0, 0, 1, 1], [0, 0, 0, 1, 1, 1, 2, 2])
    return {"association": str(association), "shares": [[str(lost), str(kept)] for lost, kept in lost_kept],
            "tighter": tight, "presence": str(presence)}


def case_rules_repair2():
    """Lane RO's repair 2: `B`'s own forms (a point after figures holding no places, `42.` + 1 written `43.`;
    a negative in brackets, the minus sign, or a hyphen-minus after an amount), a stamp's fraction (`A`'s
    count of figures in zeros, to the second where it is none), and `D`'s readings in a band reaching far
    below 0 read one by one (the outside review's item 9, its own case: 600 gaps of -10**9, -1, 0, 1, 2 and
    3 at a grain of 10**-6 on 150, 50, 100, 150, 90 and 60 rows, class 200, its L1 level), each band
    summed up as its rows, its least and largest reading and its readings below 0 (the build's ring held
    the band's whole span of 250,000,000,749,999 multiples: no mutant outcome can be computed beside it)."""
    forms = [co.written_sum(43, point=True), co.written_sum(-43, point=True, negative="brackets"),
             co.written_sum(F(-125, 100), negative="brackets"), co.written_sum(F(-125, 100), negative="trailing_minus"),
             co.written_sum(-43, negative="trailing_minus"), co.written_sum(-43, negative="minus_sign"),
             co.written_sum(F(425, 100), point=True)]
    fraction = [list(co.stamp_fraction(word, digits)) for word, digits in (("subsecond", 3), ("subsecond", 0), ("second", 3), ("minute", 6))]
    gaps = [-10**15] * 150 + [-10**6] * 50 + [0] * 100 + [10**6] * 150 + [2 * 10**6] * 90 + [3 * 10**6] * 60
    wide = {}
    for name, percents, edges in co.derived_levels(gaps):
        if name != "L1":
            continue
        totals = co.band_totals(edges, gaps)
        bands = co.derived_readings(edges, totals, totals, percents, 200, 1)
        summary = [[len(b), str(min(b)) if b else "", str(max(b)) if b else "", sum(1 for x in b if x < 0)] for b in bands]
        wide = {"edges": _texts(edges), "totals": totals, "bands": summary}
    return {"forms": forms, "fraction": fraction, "wide": wide}


def case_rules_step():
    """A rule step's word keyed by the rule's identity, and the option it draws among three scores."""
    columns = ["started_on", "ended_on", "opened_at", "closed_at"]
    out = []
    for computed, inputs in (("closed_at", ["opened_at"]), ("ended_on", ["started_on"])):
        w = co.rule_word(TEST_KEY, "event", "order", computed, inputs, columns)
        place, how, _weights = co.choose(w, [F(0), F(1000), F(1003)], F(2))
        out += [{"computed": computed, "word": w.hex(), "choice": place, "how": how}]
    return out


# --- the patient layer's cases (method G16.17's 1, 14, 15; lane GRb, plan P4-D465) ---------

PATIENT_SEED = 465
CDF_POINTS = ["-7.9", "-5", "-3", "-1.5", "-0.3", "0", "0.7", "2.2", "4", "7.5"]
EXP_POINTS = ["-744", "-30.5", "-1", "-0.125", "0", "0.5", "1", "3.75", "40", "700"]


def case_patient_line(mean_excess=False):
    """Case 1: `r` from a census with an open top band; the census met exactly (mutant: the mean excess each)."""
    out = []
    for q, m in ((11, 3), (0, 4), (57, 7), (1000, 11), (5, 13)):
        line = [q // m] * m if mean_excess else co.straight_line(q, m)
        out += [{"q": q, "m": m, "line": line, "met": sum(line) == q}]
    return out


def case_patient_split(first_minimiser=False):
    """Case 14: the excess split's tie, two grain cells of 55 top-band patients under one parent cell, q = 11: (5, 6)
    (mutant: the solver's first minimiser, the greatest vector, (6, 5)); and three small splits beside it."""
    out = []
    for targets, total in (([F(11, 2), F(11, 2)], 11), ([F(1, 3), F(5, 2), F(7, 4)], 6), ([F(0), F(3)], 1), ([F(9, 4), F(9, 4), F(9, 4)], 10)):
        found = co.excess_split(targets, total)
        if first_minimiser:
            cost = sum(abs(F(found[at]) - targets[at]) for at in range(len(targets)))
            ties = [found]
            for vector in _vectors(total, len(targets)):
                if sum(abs(F(vector[at]) - targets[at]) for at in range(len(targets))) == cost:
                    ties += [list(vector)]
            found = max(ties)
        out += [{"targets": [[t.numerator, t.denominator] for t in targets], "total": total, "split": found}]
    return out


def _vectors(left, places):
    if places == 1:
        yield (left,)
        return
    for first in range(left + 1):
        for rest in _vectors(left - first, places - 1):
            yield (first,) + rest


def case_patient_scores():
    """Case 15 (a): the patient scores of 1,000 patients in five bands, bit for bit."""
    words = splitmix64(PATIENT_SEED, 4 * 1000)
    sums = [co.hidden_score(words[4 * p:4 * p + 3]) * 65536 + 393210 for p in range(1000)]
    sums = [int(one) for one in sums]
    places = [words[4 * p + 3] for p in range(1000)]
    bands = [(7 * p) % 5 for p in range(1000)]
    scores = [co.b64_hex(one) for one in co.patient_scores(sums, places, bands)]
    digest = hashlib.sha256(",".join(scores).encode("ascii")).hexdigest()
    return {"seed": PATIENT_SEED, "bands": "7 p mod 5", "count": len(scores), "first": scores[:8], "sha256": digest}


def case_patient_omega():
    """Case 15 (b): the weight of a published three-by-two table on a reduced grid (six steps, three points a band), bit for bit."""
    table = [[300, 60], [180, 180], [50, 310]]
    shares = [40, 45, 35]
    return {
        "table": table,
        "shares": shares,
        "steps": 6,
        "points": 3,
        "omega": co.b64_hex(co.omega_of(table, shares, 6, 3)),
    }


def case_two_exchange_close(no_pair=False):
    """Case 6: the two-exchange close, the random exchanges off: two patients of three rows, codes (0, 0, 1) and
    (0, 0, 2), `S_P` 6, window 0 (`Q_P` 0, odd `r`): no single exchange meets the gap of -6, and the largest step that
    fits (-4) leaves 2 with no step left that fits, while two exchanges on different patients (-2 and -4) meet it
    (repair 1 of lane GRb, the first skeptic's item 3: a case the largest-fit fallback cannot meet alone; mutant: the
    two-exchange step removed, which stalls at 2)."""
    codes, total = co.trend_close([0, 0, 1, 0, 0, 2], [0, 3], 3, 6, 0, 0, None, not no_pair)
    return {"codes": codes, "total": total, "met": total == 0}


def case_shared_functions():
    """The shared module's exponential and normal distribution function at fixed points, bit for bit."""
    return {
        "cdf": [[point, co.b64_hex(co.normal_cdf(co.b64(F(point))))] for point in CDF_POINTS],
        "exp": [[point, co.b64_hex(co.exponential(co.b64(F(point))))] for point in EXP_POINTS],
    }


def chain_cases():
    return {
        "patient_line": case_patient_line(),
        "patient_line_mutant_mean_excess": case_patient_line(mean_excess=True),
        "patient_split": case_patient_split(),
        "patient_split_mutant_first_minimiser": case_patient_split(first_minimiser=True),
        "patient_scores": case_patient_scores(),
        "patient_omega": case_patient_omega(),
        "patient_shared_functions": case_shared_functions(),
        "patient_two_exchange_close": case_two_exchange_close(),
        "patient_two_exchange_close_mutant_no_pair": case_two_exchange_close(True),
        "stated_exponential": case_stated_exponential(),
        "ladder_merge": case_ladder_merge(),
        "one_band": case_one_band(),
        "one_band_mutant_before_the_rule": case_one_band(mutant=True),
        "one_band_beside_blanks": case_one_band("one_band_beside_blanks"),
        "one_band_at_the_exact_rung": case_one_band("one_band_at_the_exact_rung"),
        "one_band_median_named_by_a_lower_rung": case_one_band("one_band_median_named_by_a_lower_rung"),
        "one_band_no_cut": case_one_band("one_band_no_cut"),
        "one_band_no_cut_beside_blanks": case_one_band("one_band_no_cut_beside_blanks"),
        "one_band_shapes": one_band_shapes(),
        "te_raise": case_te_raise(),
        "temporal_ladder": case_temporal_ladder(),
        "temporal_ladder_mutant_number_cuts": case_temporal_ladder(role_as_number=True),
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
        "walk40_implied": case_walk40_implied(),
        "walk40_implied_mutant_hidden_score_only": case_walk40_implied(implied=False),
        "polish": case_polish(),
        "polish_mutant_l0_frame": case_polish(frame_l0=True),
        "polish_mutant_aims_fixed": case_polish(adjust=False),
        "polish_mutant_stale_bands": case_polish(stale=True),
        "polish_mutant_no_spreads": case_polish(spreads_on=False),
        "polish_mutant_aims_apart": case_polish(feasible=False),
        "psd_projection": case_psd_projection(),
        "polish_targets": case_polish_targets(),
        "polish_gate": case_polish_gate(),
        "polish_held": case_polish_held(),
        "polish_held_mutant_dropped": case_polish_held(held=False),
        "polish_curve": case_polish_curve(),
        "polish_curve_mutant_none": case_polish_curve(curve=False),
        "polish_spread": case_polish_spread(),
        "implied_nofit": case_implied_nofit(),
        "implied_nofit_floor": case_implied_nofit(10000),
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
        "cell_index": case_cell_index(),
        "cell_index_mutant_three_bytes": case_cell_index(width=3),
        "stray_rows": case_stray_rows(),
        "stray_rows_mutant_eligible_gives": case_stray_rows(eligible_gives=True),
        "stray_computed": case_stray_beside_a_computed_column(),
        "stray_computed_mutant_computed_gives": case_stray_beside_a_computed_column(computed_gives=True),
        "joint_move": case_joint_move(),
        "joint_move_mutant_members_test": case_joint_move(members_test=True),
        "rules_only": case_rules_only(),
        "rules_only_mutant_section_off": case_rules_only(section_runs=False),
        "decimal_rung": case_decimal_rung(),
        "decimal_rung_mutant_exact": case_decimal_rung(exact=True),
        "interface_join": case_interface_join(),
        "interface_join_mutant_earlier_first": case_interface_join(earlier_first=True),
        "reader_bands": case_reader_bands(),
        "reader_bands_mutant_interface_other": case_reader_bands(interface_other=True),
        "row_hash": case_row_hash(),
        "row_hash_mutant_separators": case_row_hash(separators=True),
        "row_hash_mutant_raw": case_row_hash(raw=True),
        "band_codes": case_band_codes(),
        "band_codes_mutant_two_bytes": case_band_codes(two_bytes=True),
        "reader_joins": case_reader_joins(),
        "reader_joins_mutant_later_never": case_reader_joins(join="later_never"),
        "reader_joins_mutant_earlier_never": case_reader_joins(join="earlier_never"),
        "sample_key": case_sample_key(),
        "sample_key_mutant_cut": case_sample_key(cut=True),
        "rules_limit": case_rules_limit(),
        "rules_levels": case_rules_levels(),
        "rules_levels_mutant_first_text": case_rules_levels(first_text=True),
        "rules_partition": case_rules_partition(),
        "rules_family": case_rules_family(),
        "rules_family_mutant_rule5_off": case_rules_family(rule5=False),
        "rules_readings": case_rules_readings(),
        "rules_written": case_rules_written(),
        "rules_step": case_rules_step(),
        "rules_forms": case_rules_forms(),
        "rules_one_band": case_rules_one_band(),
        "rules_one_band_mutant_build": case_rules_one_band(amended=False),
        "rules_items": case_rules_items(),
        "rules_items_mutant_build": case_rules_items(amended=False),
        "rules_repair2": case_rules_repair2(),
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
    edge = correlation_sums([[3, 1, 0], [1, 10, 0], [0, 0, 37]])
    out["test_i_edge"] = {"sums": [edge[(0, 0)], edge[(1, 0)], edge[(0, 1)], edge[(2, 0)], edge[(0, 2)], edge[(1, 1)]],
                          "allowed": mo.correlation_allowed(edge[(0, 0)], edge[(1, 0)], edge[(0, 1)],
                                                            edge[(2, 0)], edge[(0, 2)], edge[(1, 1)])}
    loose = [[4, 4, 3], [4, 3, 4], [3, 4, 4]]
    inst, out["correlation_one_cell"] = _verdict(spec_correlation(33, correlation_sums(loose)))
    out["cf1_against_the_oracle"] = cf1_agreement([22, 40])
    out["class_boundary"] = [class_boundary(w) for w in (2, 3, 4, 6)]
    out["class"] = {"name": mo.CLASS_NAME, "nodes_max": mo.NODES_MAX, "entries_max": mo.ENTRIES_MAX,
                    "groups_max": mo.GROUPS_MAX, "setup_max": mo.SETUP_MAX}
    return out
