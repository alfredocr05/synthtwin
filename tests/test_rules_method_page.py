"""The rules page holds what it proves (contract 4.6b.7's amendment of 2026-11-01, repaired 2026-11-02; plan P4-D452).

WHY A FILE OF ITS OWN. Lane MR writes no product code: order rules, computed columns and impossible
combinations are built by lanes RO, RD and RZ from a page nothing yet runs, and the disposition seal
cannot tell a correction of a sealed passage from its undoing. So this file computes each small case
the page's proofs rest on, in plain integers, and pins, word for word, the sentences a builder could
misread: a mutant of any of them turns a case here red.

WHAT IS COMPUTED. Row 9's one test in its closed form `R - v` against every world of small bases; the
phrase class passing on every small base; the rule's preimages searched for a union of raw cells
held inside 1 to f - 1, under rule 1 as repaired, with each mutant that must leak (rule 5 off among
them); the precondition, every table of each preimage opening the step, beside a builder's extra
condition; the right-closed bands; skeptic 1's table, where tied rungs pin a count of 1 to 10 under
the first text's rule 1 and the repaired clause refuses it; a source `D` on a pair of dates, its
cells holding the arithmetic, leaking only where the two source conditions are dropped; OPEN1's
top-code on two ages; the person table's partition; the score's new items on their fixtures; a
formula's failing row written from binary64; the table of number forms; the event table at the
owner's floor; and, through the product, the three cells that turn a column's `role`.

WHAT IS NOT HERE. The page's larger counts: its work folder's `rules_enum.py` and `price_probe2.py`
printed them. No twin: `K-S6-06` is judged on the head that ships the chain, after lane CHON.
"""
import datetime
import inspect
import itertools
import pathlib
import random
from decimal import Decimal
from fractions import Fraction

import fixtures
import rules_event_table as event_table
from synthtwin import chain_walk, profile, reading, taxonomy

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
CONTRACT = REPOSITORY / "docs" / "spec" / "profile-contract-v6.md"
PLAN = REPOSITORY / "docs" / "plans" / "phase-4-columns.md"
CHANGES = REPOSITORY / "CHANGELOG.md"
START = "**AMENDED 2026-11-01: THE RULES PAGE"
END = "#### 4.6b.8 Words (O7)"


def _page() -> str:
    text = CONTRACT.read_text(encoding="utf-8")
    return " ".join(text[text.index(START) : text.index(END)].split())


def _splits(total, cells):
    if cells == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in _splits(total - first, cells - 1):
            yield (first,) + rest


# -- ROW 9'S ONE TEST ON THE BASE: THE CLOSED FORM AGAINST EVERY WORLD -------------------------


def _closed_form_passes(totals, readings, v, f):
    """Proposition T (ii) as repaired: the count class passes exactly where R - v is 0 or at least f."""
    every = sum(readings)
    return v <= every and (every - v == 0 or every - v >= f)


def _worlds(totals, readings, v):
    for fails in itertools.product(*[range(top + 1) for top in readings]):
        if sum(fails) == v:
            yield fails


def _every_world_passes(totals, readings, v, f):
    """The test itself: S(K) from the largest counts, then one world holding S at 0."""
    worlds = list(_worlds(totals, readings, v))
    if not worlds:
        return False
    cells = len(totals)
    top_fails = [max(world[at] for world in worlds) for at in range(cells)]
    top_holds = [max(totals[at] - world[at] for world in worlds) for at in range(cells)]
    for world in worlds:
        good = True
        for at in range(cells):
            if top_fails[at] <= f - 1 and world[at]:
                good = False
            if top_holds[at] <= f - 1 and totals[at] - world[at]:
                good = False
        if good:
            return True
    return False


def test_row_nine_s_closed_form_is_the_test_on_every_small_base():
    f = 3
    seen = 0
    refused = 0
    for bands in (1, 2, 3):
        for totals in itertools.product((0, 3, 4, 5, 7), repeat=bands):
            for held in itertools.product((False, True), repeat=bands):
                readings = tuple(totals[at] if held[at] else 0 for at in range(bands))
                for v in range(f, sum(readings) + 2):
                    seen += 1
                    expected = _every_world_passes(totals, readings, v, f)
                    refused += not expected
                    assert _closed_form_passes(totals, readings, v, f) == expected, (totals, readings, v)
    assert seen > 1000 and refused > 50
    # At 20,000 rows, `v` at most 200: a class is refused only where `A` reads on at most 210 rows.
    refusing = {r for r in range(11, 400) if any(not _closed_form_passes((r,), (r,), v, 11) for v in range(11, min(r, 200) + 1))}
    assert refusing == set(range(12, 211))
    page = _page()
    assert "A count class `v` passes exactly where `R - v` is 0 or at least `f`, `R` the rows where `A` holds a reading" in page
    assert "only on a pair whose `A` reads on at most 210 rows (ARITHMETIC" in page


def test_the_phrase_class_passes_on_every_small_base_of_two_margins():
    # Proposition T (i): every band 0 or at least f; the world with no failing row holds S at 0.
    f = 3
    for first in itertools.product((0, 3, 4, 6), repeat=3):
        for second in itertools.product((0, 3, 4, 6), repeat=3):
            if sum(first) != sum(second) or not sum(first):
                continue
            # The north-west corner rule builds a table of these margins with no failing row.
            left = list(first)
            right = list(second)
            table = [[0] * 3 for _ in range(3)]
            for i in range(3):
                for j in range(3):
                    moved = min(left[i], right[j])
                    table[i][j] = moved
                    left[i] -= moved
                    right[j] -= moved
            assert not any(left) and not any(right)
            for i in range(3):
                for j in range(3):
                    if first[i] and second[j]:
                        assert min(first[i], second[j]) >= f


# -- RULE 1 AS REPAIRED ----------------------------------------------------------------------


def _rule_one(totals, m, percents, f, first_text=False, bound=None):
    """Rule 1 of the derived option (MR.2): the bound, the empty highest band, the rank-gap clause."""
    need = max(2 * f, f + 4)
    if bound is not None:
        need = bound
    if first_text:
        return min(totals) >= need
    if min(totals[:-1], default=need) < need or 0 < totals[-1] < need:
        return False
    ranks = [(p * (m - 1)) // 100 for p in percents]
    if any(ranks[at + 1] - ranks[at] < f + 1 for at in range(len(ranks) - 1)):
        return False
    if not totals[-1] and (len(totals) == 1 or (m - 1) - ranks[-1] < f + 1):
        return False
    return True


# -- THE PREIMAGES: NO UNION HELD INSIDE 1 TO f - 1, AND THE MUTANTS THAT MUST LEAK -------------

VALUES = (-1, 0, 1, 2)
LEVEL_PERCENTS = (("L1", (25, 50, 75, 90)), ("L2", (50,)), ("one", ()))


def _rung(counts, percent, values=VALUES):
    m = sum(counts)
    position = Fraction(percent * (m - 1), 100)
    k = position.numerator // position.denominator
    part = position - k
    seen = 0
    low = high = None
    for at in range(len(values)):
        seen += counts[at]
        if low is None and seen > k:
            low = values[at]
        if high is None and seen > k + 1:
            high = values[at]
            break
    return low + part * ((low if high is None else high) - low)


_EDGES = {}


def _edges(counts, percents, values=VALUES):
    known = _EDGES.get((counts, percents, values))
    if known is not None:
        return known
    out = []
    for percent in percents:
        edge = _rung(counts, percent, values)
        if not out or edge != out[-1]:
            out += [edge]
    _EDGES[(counts, percents, values)] = tuple(out)
    return _EDGES[(counts, percents, values)]


def _band(value, edges, right_closed):
    place = 0
    for edge in edges:
        if (value <= edge) if right_closed else (value < edge):
            break
        place += 1
    return place


def _options(table, f, limit, mutant=None):
    """The published key of each eligible option of one table: two bands of A, D over VALUES."""
    rows = (table[:4], table[4:])
    margin = tuple(rows[0][at] + rows[1][at] for at in range(4))
    if any(0 < sum(row) < f for row in rows) or not sum(margin) or margin[0] > limit:
        return
    v = margin[0]
    right = mutant != "left_closed"
    for name, percents in LEVEL_PERCENTS:
        edges = _edges(margin, percents)
        places = [_band(x, edges, right) for x in VALUES]
        totals = [0] * (len(edges) + 1)
        family = [[0] * (len(edges) + 1), [0] * (len(edges) + 1)]
        for at in range(4):
            totals[places[at]] += margin[at]
            family[0][places[at]] += rows[0][at]
            family[1][places[at]] += rows[1][at]
        if not _rule_one(totals, sum(margin), percents if edges else (), f, mutant == "first_rule1"):
            continue
        if mutant != "no_rule3" and any(0 < cell < f for line in family for cell in line):
            continue
        if v >= f and mutant != "no_rule5":
            below = [0] * len(totals)
            below[places[0]] += margin[0]
            if any(0 < below[b] < f or 0 < totals[b] - below[b] < f for b in range(len(totals))):
                continue
        word = ("phrase",) if v < f else ("count", v)
        if mutant == "exact":
            word = ("count", v)
        if mutant == "role_word":
            word = ("phrase", v > 0) if v < f else ("count", v)
        yield (name, edges, tuple(tuple(line) for line in family), word)


def _preimages(rows, f, limit, mutant=None):
    keys = {}
    for table in _splits(rows, 8):
        for key in _options(table, f, limit, mutant):
            keys.setdefault(key, set()).add(table)
    return keys


def _leaks(keys, f):
    found = 0
    for tables in keys.values():
        tops = [max(table[cell] for table in tables) for cell in range(8)]
        small = [cell for cell in range(8) if 0 < tops[cell] <= f - 1]
        vectors = {tuple(table[cell] for cell in small) for table in tables}
        for size in range(1, len(small) + 1):
            for picks in itertools.combinations(range(len(small)), size):
                counts = [sum(vector[p] for p in picks) for vector in vectors]
                if min(counts) >= 1 and max(counts) <= f - 1:
                    found += 1
    return found


def test_no_union_is_held_inside_the_small_counts_and_the_mutants_leak():
    assert _leaks(_preimages(16, 3, 4), 3) == 0
    assert _leaks(_preimages(16, 3, 4, "exact"), 3) > 0
    assert _leaks(_preimages(16, 3, 4, "role_word"), 3) > 0
    assert _leaks(_preimages(16, 3, 4, "no_rule3"), 3) > 0


RULE_FIVE_ROWS = 14
RULE_FIVE_LIMIT = 10


def test_rule_five_is_what_keeps_a_count_class_from_leaking():
    # REPAIR 1: the first text said rule 5 turned no case red; it does where the class reaches the band.
    assert _leaks(_preimages(RULE_FIVE_ROWS, 3, RULE_FIVE_LIMIT), 3) == 0
    assert _leaks(_preimages(RULE_FIVE_ROWS, 3, RULE_FIVE_LIMIT, "no_rule5"), 3) > 0
    assert "Rule 5 turns cases red where the class reaches the band" in _page()


def test_every_table_of_a_preimage_opens_the_step_and_a_builder_s_extra_condition_does_not():
    # Theorem P: OPEN2 and OPEN3 are implied by the class and the bound. An extra real-table condition is not.
    f = 3
    limit = 4
    keys = _preimages(16, f, limit)
    assert keys
    broken_by_page = 0
    broken_by_extra = 0
    for tables in keys.values():
        closed_page = closed_extra = 0
        for table in tables:
            margin = [table[at] + table[at + 4] for at in range(4)]
            if margin[0] > limit or sum(margin) < f:
                closed_page += 1
            if 2 * margin[1] > sum(margin):  # "at most half the gaps are zero", a filter a builder might add
                closed_extra += 1
        broken_by_page += closed_page > 0
        broken_by_extra += 0 < closed_extra
    assert broken_by_page == 0
    assert broken_by_extra > 0


def test_right_closed_bands_keep_an_edge_at_nought_that_left_closed_bands_lose():
    keys_right = _preimages(16, 3, 4)
    keys_left = _preimages(16, 3, 4, "left_closed")
    at_nought_right = sum(1 for key in keys_right if 0 in key[1])
    at_nought_left = sum(1 for key in keys_left if 0 in key[1])
    assert at_nought_right > 0
    assert at_nought_left == 0


# -- PROPOSITION B: TIED RUNGS, AND THE CLAUSE THAT REFUSES THEM --------------------------------

DECILES = (10, 20, 25, 30, 40, 50, 60, 70, 75, 80, 90)
SKEPTIC_TABLE = {0: 24, 1: 23, 2: 1, 3: 23, 4: 22, 5: 23, 6: 23, 7: 47, 8: 22, 9: 24}


def _level_of(counts, percents=DECILES):
    """(edges, band totals, m) of a level (the deciles unless named) over readings, bands right-closed."""
    values = tuple(sorted(value for value in counts if counts[value]))
    weights = tuple(counts[value] for value in values)
    edges = _edges(weights, percents, values)
    totals = [0] * (len(edges) + 1)
    for value in values:
        totals[_band(value, edges, True)] += counts[value]
    return edges, tuple(totals), sum(weights)


def test_tied_rungs_pin_a_count_of_one_to_ten_and_the_repaired_rule_one_refuses_the_level():
    f = 11
    edges, totals, m = _level_of(SKEPTIC_TABLE)
    assert m == 232 and min(totals) >= max(2 * f, f + 4)
    assert edges == (Fraction(1, 10), Fraction(6, 5), 3, Fraction(22, 5), Fraction(11, 2), Fraction(33, 5), 7, Fraction(89, 10))
    assert _rule_one(totals, m, DECILES, f, first_text=True)
    assert not _rule_one(totals, m, DECILES, f)
    assert (25 * (m - 1)) // 100 - (20 * (m - 1)) // 100 == 11
    # Every split of the band (1.2, 3] between its two whole readings that keeps the level: 1 to 10 stays of 2 days.
    band = totals[2]
    kept = []
    for twos in range(band + 1):
        other = dict(SKEPTIC_TABLE)
        other[2] = twos
        other[3] = band - twos
        if _level_of(other)[:2] == (edges, totals):
            kept += [twos]
    assert kept and min(kept) >= 1 and max(kept) <= f - 1
    page = _page()
    assert "a tied edge pins every rank its rungs enclose" in page
    assert "`k(q) - k(p) >= f + 1`" in page
    assert "`k(25) - k(20) = 57 - 46 = 11 < 12`, and the level is refused" in page


def _pinned_counts(table, edges, totals, low, high):
    """Every count of reading `low` over the splits of its band with `high` that keep the level."""
    band = table[low] + table[high]
    kept = []
    for lows in range(band + 1):
        other = dict(table)
        other[low] = lows
        other[high] = band - lows
        if _level_of(other)[:2] == (edges, totals):
            kept += [lows]
    return kept


def test_the_repaired_rule_one_leaves_no_small_count_where_the_first_text_s_leaves_one():
    # Skeptic 1's shape at f = 3: whole readings 0 to 4, one reading of 2 held between rungs, the deciles.
    f = 3
    leaking = {False: [], True: []}
    for n in range(66, 80):
        for zeros, ones, twos, fours in itertools.product(range(6, 10), range(6, 10), (1, 2), range(6, 10)):
            table = {0: zeros, 1: ones, 2: twos, 3: n - zeros - ones - twos - fours, 4: fours}
            edges, totals, m = _level_of(table)
            for first_text in (False, True):
                if not _rule_one(totals, m, DECILES, f, first_text) or _band(2, edges, True) != _band(3, edges, True):
                    continue
                kept = _pinned_counts(table, edges, totals, 2, 3)
                if kept and min(kept) >= 1 and max(kept) <= f - 1:
                    leaking[first_text] += [table]
    assert leaking[False] == []
    assert {0: 8, 1: 7, 2: 1, 3: 49, 4: 7} in leaking[True]


# -- REPAIR 2: A HEAP WITH A FEW ROWS ABOVE ITS TOP RUNG, AND THE EMPTY HIGHEST BAND --------------

LADDER_PERCENTS = (("L0", DECILES), ("L1", (25, 50, 75, 90)), ("L2", (50,)))


def _gap_counts(rows):
    counts = {}
    for opened, closed, _site in rows:
        gap = _day(closed) - _day(opened)
        counts[gap] = counts.get(gap, 0) + 1
    return counts


def _kept_level(counts, f, bound=None):
    """The first level of L0, L1 and L2 with an edge that rule 1 keeps, or None."""
    for name, percents in LADDER_PERCENTS:
        edges, totals, m = _level_of(counts, percents)
        if edges and _rule_one(totals, m, percents, f, bound=bound):
            return name
    return None


def _one_band_worth(counts):
    """MR.7's no-edge item as repair 2 writes it: worth carrying where the gap is 0 on 99 of 100 rows or more."""
    return 100 * counts.get(0, 0) >= 99 * sum(counts.values())


def test_a_heap_at_nought_with_a_few_rows_above_its_top_rung_keeps_its_rule_at_the_one_band():
    f = 11
    for above, failing in ((21, 0), (15, 5)):
        counts = _gap_counts(event_table.heap_rows(above=above, failing=failing))
        assert counts[0] == 20000 - above - failing and counts.get(-1, 0) == failing
        # The band bound, read at f = 11: every level with an edge is refused, its highest band 1 to 21 rows.
        assert _kept_level(counts, f) is None
        # Repair 1's item ("the real gaps are not all 0") refused the one band and lost the rule; repair 2's carries it.
        assert any(gap != 0 for gap in counts)
        assert _one_band_worth(counts)
    # From 22 rows above the deciles carry it.
    assert _kept_level(_gap_counts(event_table.heap_rows(above=22)), f) == "L0"
    # The caution's price: the proof's bound f + 1 keeps the deciles from 12 rows above; 11 rows, the one band under either.
    assert _kept_level(_gap_counts(event_table.heap_rows(above=12)), f) is None
    assert _kept_level(_gap_counts(event_table.heap_rows(above=12)), f, bound=f + 1) == "L0"
    assert _kept_level(_gap_counts(event_table.heap_rows(above=11)), f, bound=f + 1) is None
    # Away from 0 the rule is lost (limit 19): no level, and the one band would erase the 7 days.
    seven = _gap_counts(event_table.heap_rows(heap_days=7, above=1))
    assert _kept_level(seven, f) is None and not _one_band_worth(seven)
    # The bound's price, a stated limit (the orchestrator's ruling 3 (1) keeps the bound): 12 to 21 rows above lose it.
    for above in (12, 21):
        priced = _gap_counts(event_table.heap_rows(heap_days=7, above=above))
        assert _kept_level(priced, f) is None and _kept_level(priced, f, bound=f + 1) == "L0"
    assert _kept_level(_gap_counts(event_table.heap_rows(heap_days=7, above=22)), f) == "L0"
    page = _page()
    for words in (
        "every eligible level of `D` has no edge, and the real gap is 0 on fewer than 99 of 100 of the rows where both read",
        "**A heap with 1 to 21 rows above its top rung** (REPAIR 2, at `f` = 11).",
        "**A STATED LIMIT: THE BOUND'S PRICE** (REPAIR 2; the orchestrator's ruling 3 (1) of 2026-11-03 keeps rule 1's bound at `max(2 f, f + 4)`",
        "a heap with 12 to 21 rows above its top rung keeps no level with an edge, where `f + 1` would keep the deciles.",
        "Owner: RO, whose order rule keeps end after start in the generator without any new published fact (limit 19).",
    ):
        assert words in page, words


def test_the_empty_highest_band_keeps_a_heap_at_the_largest_gap_and_its_top_clause_refuses_a_thin_one():
    f = 3
    upper = (25, 50, 75, 90)
    # A 30-day cap on 70 rows in 100: kept only because the highest band may hold 0 rows.
    edges, totals, m = _level_of({0: 6, 3: 6, 7: 6, 14: 6, 21: 6, 30: 70}, upper)
    assert edges == (21, 30) and totals == (30, 70, 0)
    assert _rule_one(totals, m, upper, f)
    # A heap at the top whose top rung leaves fewer than f + 1 ranks above it: the top clause alone refuses it.
    edges, totals, m = _level_of({0: 8, 10: 7, 30: 15}, upper)
    ranks = [(p * (m - 1)) // 100 for p in upper]
    assert totals[-1] == 0 and min(totals[:-1]) >= max(2 * f, f + 4)
    assert all(ranks[at + 1] - ranks[at] >= f + 1 for at in range(len(ranks) - 1))
    assert (m - 1) - ranks[-1] < f + 1
    assert not _rule_one(totals, m, upper, f)


# -- REPAIR 2: THE BANDS' READINGS ON THE GRID ----------------------------------------------------


def _up(value, g):
    """The smallest multiple of `g` above `value`."""
    steps = Fraction(value) / g
    return (steps.numerator // steps.denominator + 1) * g


def _highest_band(lo, inner_width, lowest_edge, g=1):
    """MR.2's highest band as repair 2 writes it: `up(lo)` alone where `w` is at most `g`, else (lo, lo + 3 w]."""
    w = inner_width if inner_width is not None else max(lowest_edge, 0)
    first = _up(lo, g)
    if w <= g:
        return [first]
    out = []
    reading = first
    while reading <= lo + 3 * w:
        out += [reading]
        reading += g
    return out


def _lowest_band(rungs, ranks, g=1):
    """MR.2's lowest band in the phrase class: its edge on every rank where two or more rungs tie there, else
    its multiples from 0 to the edge by position."""
    edge = rungs[0]
    if sum(1 for rung in rungs if rung == edge) > 1:
        return [edge] * ranks
    count = int(Fraction(edge) / g) + 1
    return [((at * count) // ranks) * g for at in range(ranks)]


def test_each_band_reads_on_the_grid_and_a_heap_tied_at_the_lowest_edge_is_written_there():
    # The outside review's item 2: gaps of 0 and 1 day on half the rows each keep the median alone, its edge 1/2.
    edges, totals, _m = _level_of({0: 10000, 1: 10000}, (50,))
    assert edges == (Fraction(1, 2),) and totals == (10000, 10000)
    assert _highest_band(edges[-1], None, edges[0]) == [1]
    assert (edges[-1] + 1).denominator != 1  # repair 1's `lo + g`: 3/2 days, off the grid
    # The verify's item 2: no inner band, the upper half spread over three widths of the lowest band.
    assert _highest_band(4, None, 4) == list(range(5, 17))
    assert _highest_band(8, 1, 0) == [9] and _highest_band(8, 3, 0) == list(range(9, 18))
    assert _highest_band(Fraction(-1, 2), None, Fraction(-1, 2)) == [0]
    assert _highest_band(90, None, 90, g=60) == [120, 180, 240, 300, 360]
    # The verify's item 3: a gap of exactly 7 days on every row, every rung tied at 7, is written 7 on every rank.
    rungs = [_rung((20000,), percent, (7,)) for percent in DECILES]
    assert _lowest_band(rungs, 2000) == [7] * 2000
    assert min(_lowest_band([7], 2000)) == 0
    assert _lowest_band([2, 5], 9) == [0, 0, 0, 1, 1, 1, 2, 2, 2]
    page = _page()
    for words in (
        "Let `w` be the width of the nearest inner band or, where no inner band exists, the lowest band's width read from 0 (its edge, 0 where the edge is below 0), and `up(lo)` the smallest multiple of `g` above `lo`.",
        "The band takes `up(lo)` alone where `w` is at most `g`, and otherwise its multiples in `(lo, lo + 3 w]`",
        "where two or more rungs tie at its edge, it takes that edge on every rank instead",
    ):
        assert words in page, words


# -- REPAIR 2: A COARSER `B`, THE DAY'S END, E-NOTATION IN `B` ---------------------------------------


def _clock(text):
    parts = [int(part) for part in text.split(":")] + [0]
    return parts[0] * 3600 + parts[1] * 60 + parts[2]


def _written_coarser(total, gap, step):
    """MR.2: `A + D` in `B`'s coarser layout, on `D`'s side of `A`: up where `D >= 0`, down where `D < 0`."""
    down = (total // step) * step
    if gap >= 0 and down < total:
        return down + step
    return down


def test_a_sum_is_written_in_b_s_coarser_layout_on_d_s_side_of_a():
    for any_second in (False, True):
        rows = event_table.seconds_rows(rows=2000, any_second=any_second)
        starts = [_clock(row[0]) for row in rows]
        assert all(_clock(row[1]) % 60 == 0 and _clock(row[1]) > _clock(row[0]) for row in rows)
        cut = kept = 0
        for start in starts:
            for gap in range(61):  # the lowest band's readings, 0 to its edge of a minute
                cut += (start + gap) // 60 * 60 < start
                kept += _written_coarser(start + gap, gap, 60) < start
            for gap in (-1, -30, -61):
                assert _written_coarser(start + gap, gap, 60) < start
        assert cut > 0 and kept == 0
    page = _page()
    assert "the twin writes the value `B`'s layout writes nearest the sum on `D`'s side of `A`: the first at or above `A + D` where `D >= 0`, the last at or below it where `D < 0`." in page
    assert "a row's reading `d` is allocated as the gap its `B` can write beside its `A`" in page


def test_a_source_sum_past_the_day_s_end_is_held_at_its_last_minute():
    rows = event_table.day_end_rows()
    last = 23 * 60 + 59
    starts = {_clock(row[0]) // 60 for row in rows}
    longest = max(int(row[1]) for row in rows)
    # Beside any of the clocks A holds, the length of 3 passes 23:59: no world keeps its sum as it stands.
    assert starts == {last - 2, last - 1, last} and all(start + longest > last for start in starts)
    as_it_stands = sum(1 for row in rows if _clock(row[0]) // 60 + int(row[1]) != _clock(row[2]) // 60)
    held = sum(1 for row in rows if min(_clock(row[0]) // 60 + int(row[1]), last) != _clock(row[2]) // 60)
    assert as_it_stands == 1 and held == 0
    page = _page()
    assert "its reading is `A + D x unit`, HELD at the last value `B`'s layout writes where the sum passes it, in the real table's reading (MR.1) and in the twin alike" in page
    assert "`B = A + D x unit` (held at the last value `B`'s layout writes where a source's sum passes it, as MR.2 reads it; REPAIR 2)" in page
    assert "and `B`'s first published layout writes every step `g` writes, so that `A + D x unit` is a value it writes." in page
    assert "the theorem is stated where its `W'` exists, every computed value one `B`'s first layout writes." in page
    assert "A source carrier lies in it on every pair: MR.3's third source condition, and its sum HELD at the last value `B`'s layout writes, the output policy at a clock's or a calendar's end (MR.2)" in page


def test_b_written_in_e_notation_opens_no_step(tmp_path):
    rows = event_table.exponent_rows(rows=3000)
    assert all(int(b[: -len("e2")]) * 100 == int(a) + 200 for a, b, _site in rows)
    path = fixtures.write(tmp_path, "t.csv", event_table.as_text(event_table.EXPONENT_HEADER, rows))
    table = reading.read_table(str(path), small_cell_floor=11)
    document = profile.build_document(table, taxonomy.Settings(small_cell_floor=11), [], [], [])
    blocks = {block["name"]: block for block in document["columns"]}
    assert blocks["dose_given"]["numeric_styles"] == {"exponent_lower": 3000}
    assert _opens(blocks["dose_base"], {"role": "count"})
    assert not _opens(blocks["dose_base"], blocks["dose_given"])
    assert _opens(blocks["dose_base"], {"role": "count", "numeric_styles": {"plain": 2000, "exponent_lower": 1000}})
    assert not _opens(blocks["dose_base"], {"role": "count", "numeric_styles": {"plain": 1500, "exponent_lower": 1500}})
    page = _page()
    assert "Its first published form (MR.6 (a)) is no E-notation, a tie putting E-notation first" in page
    assert "or where `B`'s first published form is one of them (REPAIR 2) |" in page


# -- THE SOURCE CONDITIONS: ARITHMETIC IN THE CELLS --------------------------------------------


def _source_leaks(d_values, unit_whole_of_grain, mutant, f=3, n=7):
    """A source `D` on a pair of dates; cells (a, d, mark); leaks where a union is held in 1 to f - 1."""
    cells = []
    for a in (0, 1):
        for d in d_values:
            whole = (d * (1 if unit_whole_of_grain else Fraction(1, 24))).denominator == 1
            cells += [(a, d, "holds")] if whole else []
            cells += [(a, d, "fails")]
    keys = {}
    for table in _splits(n, len(cells)):
        v = sum(table[at] for at in range(len(cells)) if cells[at][2] == "fails")
        a_counts = [sum(table[at] for at in range(len(cells)) if cells[at][0] == a) for a in (0, 1)]
        if v >= f or any(0 < x < f for x in a_counts):
            continue
        d_counts = tuple(sum(table[at] for at in range(len(cells)) if cells[at][1] == d) for d in d_values)
        integer_valued = all(not d_counts[at] or d_values[at].denominator == 1 for at in range(len(d_values)))
        offered = {"page": integer_valued and unit_whole_of_grain, "integer": integer_valued, "any": True}[mutant]
        if not offered:
            continue
        median = _rung(d_counts, 50, d_values)
        keys.setdefault((tuple(a_counts), integer_valued, median), set()).add(table)
    found = 0
    for tables in keys.values():
        for picks in range(1, 1 << len(cells)):
            inside = [sum(table[at] for at in range(len(cells)) if picks >> at & 1) for table in tables]
            if min(inside) >= 1 and max(inside) <= f - 1:
                found += 1
    return found


def test_a_source_difference_is_offered_only_where_its_arithmetic_leaves_a_world_with_no_failing_row():
    half = (Fraction(0), Fraction(1, 2), Fraction(1))
    hours = (Fraction(0), Fraction(12), Fraction(24))
    assert _source_leaks(half, True, "page") == 0
    assert _source_leaks(half, True, "any") > 0
    assert _source_leaks(hours, False, "page") == 0
    assert _source_leaks(hours, False, "integer") > 0
    page = _page()
    assert "on a date, stamp or clock pair the unit is a whole multiple of the pair's `g` (one day on a date pair or under `grain` `\"day\"`, never finer), and `D`'s published `integer_valued` is true" in page
    assert "**`D` has ONE UNIT for the pair (REPAIR 1):** seconds where every layout `A` publishes holds a clock and the option's `grain` is `\"A\"`; whole calendar days on every row otherwise, the clock never read." in page


# -- OPEN1: THE AGE TOP-CODE, THE YEAR POOLING, E-NOTATION --------------------------------------


def _opens(a_block, b_block):
    """OPEN1 as the page writes it, on two published blocks (`B`'s first form: REPAIR 2)."""
    styles = a_block.get("numeric_styles") or {}
    if any(style.startswith("exponent") for style in styles):
        return False
    forms = b_block.get("numeric_styles") or {}
    if forms and max(forms.items(), key=lambda item: (item[1], item[0].startswith("exponent")))[0].startswith("exponent"):
        return False
    if b_block.get("held") or b_block.get("role") == "identifier":
        return False
    return "top_coded" not in b_block and "top_coded_year" not in b_block


def test_a_column_under_the_age_top_code_is_never_computed():
    assert inspect.signature(event_table.ages_rows).parameters["rows"].default == event_table.ROWS_AT_THE_FLOOR
    rows = event_table.ages_rows(rows=3000)
    # Computed from the top-coded first age, the second would write cells above 90: a Safe Harbor value.
    above = sum(1 for a, b, _site in rows if min(int(a), 90) + int(b) - int(a) > 90)
    assert above > 10
    assert max(int(b) for _a, b, _site in rows) > 89
    plain = {"role": "count", "held": None}
    assert not _opens(plain, {"role": "count", "held": None, "top_coded": 90})
    assert not _opens(plain, {"role": "count", "top_coded_year": 1937})
    assert not _opens({"role": "count", "numeric_styles": {"exponent_lower": 40}}, plain)
    assert not _opens(plain, {"role": "count", "held": "identifier"})
    assert not _opens(plain, {"role": "identifier"})
    assert _opens(plain, plain)
    page = _page()
    assert "and not reached by a Safe Harbor top-code or year pooling: its block, described on its own, carries no `top_coded` and no `top_coded_year`, and a Safe Harbor question put on it is answered `no` (REPAIR 1)" in page
    assert "HIPAA first: a held or reached column is never computed, whatever the draw says, and keeps its own block." in page
    assert "whose published `numeric_styles` hold no E-notation" in page
    assert "a top-coded `A` reads as its twin writes it, 90 for every age past the cap" in page


# -- A TABLE OF SEVERAL ROWS A PERSON -----------------------------------------------------------


def _classes(v, f, limit, person_table):
    """The one threshold of MR.5, with the person table's partition of MR.3."""
    if v < f:
        return ("phrase",)
    if v <= limit and not person_table:
        return ("count",)
    return ()


def test_a_table_of_several_rows_a_person_publishes_no_count_class():
    assert inspect.signature(event_table.person_rows).parameters["rows"].default == event_table.ROWS_AT_THE_FLOOR
    rows = event_table.person_rows(rows=3000)
    failing = [row for row in rows if row[2] < row[1]]
    assert len(failing) == 12 and {row[0] for row in failing} == {"S000000"}
    assert len({row[0] for row in rows}) == 300
    assert _classes(12, 11, 200, True) == ()
    assert _classes(12, 11, 200, False) == ("count",)
    assert _classes(3, 11, 200, True) == ("phrase",)
    page = _page()
    assert "a step offers the phrase class only, until lane GR counts failing rows in people (4.6c.7), and off 4.6c.7's route no derived option is offered" in page
    assert "the exact count `v` from `f` to `L(n)`, a derived carrier only, and never on a table of several rows a person" in page


# -- THE SCORE'S NEW ITEMS, EACH ON ITS FIXTURE ---------------------------------------------------


def _day(text):
    if "/" in text:
        month, day, year = text.split("/")
        return datetime.date(int(year), int(month), int(day)).toordinal()
    return datetime.date.fromisoformat(text).toordinal()


def _not_worth(a_cells, b_cells):
    """MR.7's items that read the pair's cells (REPAIR 1), in the page's words; [] where worth carrying."""
    out = []
    b_present = [at for at in range(len(b_cells)) if b_cells[at]]
    if sum(1 for at in b_present if not a_cells[at]) > len(b_present) / 100:
        out += ["B reads where A holds none"]
    both = [at for at in b_present if a_cells[at]]
    v = sum(1 for at in both if _day(b_cells[at]) < _day(a_cells[at]))
    firsts = sorted(_day(a_cells[at]) for at in range(len(a_cells)) if a_cells[at])
    seconds = sorted(_day(b_cells[at]) for at in b_present)
    below = 0
    at = 0
    for second in seconds:
        while at < len(firsts) and firsts[at] <= second:
            at += 1
        below += len(firsts) - at
    broken = below / (len(firsts) * len(seconds))
    if v > len(both) / 100 or v / len(both) >= broken / 2:
        out += ["chance order"]
    return out


def test_the_score_keeps_out_a_sparse_partner_and_a_chance_order():
    draw = random.Random(3)
    visits = [datetime.date(2023, 1, 2) + datetime.timedelta(days=draw.randrange(720)) for _ in range(2000)]
    priors = ["" if draw.random() < 0.95 else (visit - datetime.timedelta(days=draw.randint(0, 60))).isoformat() for visit in visits]
    # A dense column is never computed from a sparse one, nor from one absent on 3 of its rows in 100.
    assert "B reads where A holds none" in _not_worth(priors, [visit.isoformat() for visit in visits])
    starts = [(visit - datetime.timedelta(days=2)).isoformat() for visit in visits]
    nearly = ["" if at % 100 < 3 else start for at, start in enumerate(starts)]
    assert "B reads where A holds none" in _not_worth(nearly, [visit.isoformat() for visit in visits])
    assert _not_worth(starts, [visit.isoformat() for visit in visits]) == []
    # Two dates read together on few rows, in no order: a chance order, not a rule.
    first = [visit.isoformat() if at % 7 == 0 else "" for at, visit in enumerate(visits)]
    second = [(datetime.date(2023, 1, 2) + datetime.timedelta(days=draw.randrange(720))).isoformat() if at % 7 == 0 else "" for at in range(2000)]
    assert "chance order" in _not_worth(first, second)
    # The event table's real order is worth carrying.
    events = event_table.event_rows(rows=2000)
    assert _not_worth([row[1] for row in events], [row[2] for row in events]) == []
    page = _page()
    for words in (
        "or `B` holds a reading on more than 1/100 of its present cells where `A` holds none",
        "`v` above 1/100 of the rows where both read, or `v` over those rows at least half of BREAK (REPAIR 1)",
        "`B`'s strongest association with a column other than `A`, read on the real table, is lost by computing it",
        "another rule that is worth carrying by every other item of this list computes the same column from an input not computed, by a smaller median gap",
    ):
        assert words in page, words


def _write_computed(a_text, gap_days, b_layouts):
    """MR.6 (a): `B = A + D` written in `B`'s own first layout word, never `A`'s."""
    day = datetime.date.fromisoformat(a_text) + datetime.timedelta(days=gap_days)
    return day.strftime(b_layouts[0])


def test_a_computed_column_is_written_in_its_own_layout_so_code_on_the_twin_runs_on_the_real_table():
    rows = event_table.layout_rows(rows=2000)
    real_b = [row[1] for row in rows]
    for text in real_b:
        datetime.datetime.strptime(text, "%m/%d/%Y")  # code written against the real column
    written = [_write_computed(row[0], _day(row[1]) - _day(row[0]), ("%m/%d/%Y",)) for row in rows]
    assert written == real_b
    for text in written:
        datetime.datetime.strptime(text, "%m/%d/%Y")  # the same code on the twin
    page = _page()
    assert "**A computed column keeps its LAYOUT WORDS (REPAIR 1; the orchestrator's ruling 2 (3); AMENDS \"it is written in `A`'s published layout words\"):**" in page
    assert "listed with the most rows first, WITHOUT their counts; the twin writes every cell of `B` in the first." in page
    assert "| DATE beside DATE | whole days | `B`'s own first layout |" in page
    assert "**UNDER THE OWNER'S RULE B (R13, 2026-11-02; the orchestrator's ruling 2 for this lane, which repair 1 follows).**" in page


# -- A FORMULA WRITTEN FROM BINARY64 -------------------------------------------------------------


def _holds(written, exact):
    """MR.8's failing-row reading: exact, or 15 significant figures where `C` carries 15 or more."""
    if Fraction(written) == exact:
        return True
    if len(written.lstrip("+-").replace(".", "").lstrip("0")) < 15:
        return False
    return f"{Decimal(written):.14e}" == f"{Decimal(exact.numerator) / Decimal(exact.denominator):.14e}"


def _holds_sum(written, first, second):
    """MR.8's reading of a sum (REPAIR 2): exact, 15 figures, or within 10 ** -14 of the inputs' size."""
    exact = Fraction(first) + Fraction(second)
    if _holds(written, exact):
        return True
    return abs(Fraction(written) - exact) <= Fraction(1, 10**14) * (abs(Fraction(first)) + abs(Fraction(second)))


def test_a_total_written_from_binary64_is_no_failing_row():
    rows = event_table.event_rows(rows=3000, binary_rates=True)
    header = {name: at for at, name in enumerate(event_table.HEADER)}
    exact_misses = 0
    for row in rows:
        exact = Fraction(row[header["units"]]) * Fraction(row[header["rate"]])
        exact_misses += Fraction(row[header["total"]]) != exact
        assert _holds(row[header["total"]], exact)
    assert exact_misses > 500
    assert not _holds("59.98", Fraction("59.97"))
    assert _holds("59.970000000000006", Fraction(3) * Fraction("19.99"))
    # A sum whose inputs nearly cancel (the outside review's item 5): 15 figures of the small result show binary64's error.
    sums = event_table.sum_rows(rows=3000)
    exact_misses = fifteen_misses = 0
    for charge, adjustment, net, _site in sums:
        exact = Fraction(charge) + Fraction(adjustment)
        exact_misses += Fraction(net) != exact
        fifteen_misses += not _holds(net, exact)
        assert _holds_sum(net, charge, adjustment)
        assert not _holds_sum(repr(float(exact + Fraction(1, 100))), charge, adjustment)  # a cent keyed wrong fails
    assert exact_misses > 1000 and fifteen_misses > 500
    assert _holds_sum("0.010000000000005116", "-100.00", "100.01")
    assert not _holds("0.010000000000005116", Fraction("0.01"))
    page = _page()
    assert "where `C` is written with 15 or more significant figures and `C` rounded to 15 significant figures equals the exact result rounded the same way" in page
    assert "a row also holds where `|C - (X + Y)|` is at most `10 ** -14 (|X| + |Y|)`" in page
    assert "This is the failing-row reading only; the twin writes the exact result." in page


# -- THE TABLE OF NUMBER FORMS --------------------------------------------------------------------


def _written(cell, plain):
    """The plain sum written in the form of `A`'s cell (MR.2's table)."""
    sign = "-" if plain.startswith("-") else ""
    figures = plain.lstrip("-")
    if cell.startswith("+") and not sign:
        sign = "+"
    core = cell.lstrip("+-")
    if core.startswith(".") and figures.startswith("0."):
        figures = figures[1:]
    if core.endswith(".") and "." not in figures:
        figures += "."
    if "," in core:
        whole, dot, rest = figures.partition(".")
        grouped = ""
        while len(whole) > 3:
            grouped = "," + whole[-3:] + grouped
            whole = whole[:-3]
        figures = whole + grouped + (("." + rest) if dot else "")
    if len(core) > 1 and core.startswith("0") and not core.startswith("0."):
        figures = figures.rjust(len(core), "0")
    return sign + figures


def test_each_number_form_writes_the_plain_sum_in_the_cell_s_own_form():
    for cell, plain, written in (
        (".42", "1.42", "1.42"), (".42", "0.52", ".52"), ("42.", "43", "43."), ("+42", "43", "+43"),
        ("+42", "-58", "-58"), ("00042", "43", "00043"), ("00042", "100043", "100043"), ("1,042", "1043", "1,043"),
    ):
        assert _written(cell, plain) == written, (cell, plain)
    # The plain sums come from the product's exact adder on the figures alone.
    assert chain_walk.added_decimal("42", "1") == "43" and chain_walk.added_decimal("0.42", "1") == "1.42"
    # Today's adder on each form (the outside review's item 6): nothing on five, and the padding dropped on one.
    for form in (".42", "42.", "+42", "1,042", "42e2"):
        assert chain_walk.added_decimal(form, "1") is None, form
    assert chain_walk.added_decimal("00042", "1") == "43"
    page = _page()
    assert "today's `added_decimal` returns nothing on `.42`, `42.`, `+42`, `1,042` and `42e2`, and writes `00042` + 1 as `43`, the padding dropped" in page
    for row in (
        "| `.42` | the point with no figure before it | `1.42` (the form holds only below 1; above it the sum is plain) |",
        "| `42.` | a point with no figure after it | `43.` |",
        "| `+42` | a plus sign | `+43` (a sum below 0 writes `-`) |",
        "| `00042` | padded with noughts to five places | `00043` (a sum wider than the cell is written whole) |",
        "| `1,042` | figures grouped in threes | `1,043` |",
    ):
        assert row in page, row


# -- THE BOUNDS ----------------------------------------------------------------------------


def test_the_limit_is_a_function_of_the_tabled_rows_and_never_under_the_floor():
    page = _page()
    assert "`L(n) = max(f, floor(n / 100))`" in page
    assert "`L` is NOT the line between a rule and a chance order (REPAIR 1)" in page
    assert "(MR.7: `v` above 1/100 of the rows where both read, or at least half of BREAK, is not worth carrying)" in page
    for n, f, limit in ((20000, 11, 200), (2000000, 11, 20000), (500, 11, 11), (20000, 20, 200), (1000, 20, 20)):
        assert max(f, n // 100) == limit


def test_a_formula_and_a_difference_write_exactly_with_no_binary_float():
    assert chain_walk.added_decimal("0.10", "0.2") == "0.30"
    assert chain_walk.added_decimal("1.5", "-2") == "-0.5"
    # MR.8: a difference computes its minuend, so no cell is the gap of two placed columns.
    assert Fraction("12.50") * 3 == Fraction("37.50")
    assert 0.1 + 0.2 != 0.3
    page = _page()
    assert "with `max(p_X, p_Y)` places for a sum and `p_X + p_Y` for a product" in page


# -- THREE CELLS TURN A ROLE ----------------------------------------------------------------


def test_three_cells_turn_a_columns_role_so_a_computed_columns_role_is_the_rule_s(tmp_path):
    draw = random.Random(1)
    lines = ["a,d,b,e"]
    for row in range(3000):
        a = draw.randint(10, 90)
        gap = draw.randint(0, 9)
        written = f"{a + gap}.5" if row < 3 else f"{a + gap}"
        lines += [f"{a},{gap},{written},{draw.randint(0, 5)}"]
    path = fixtures.write(tmp_path, "t.csv", "\n".join(lines) + "\n")
    settings = taxonomy.Settings(small_cell_floor=11)
    table = reading.read_table(str(path), small_cell_floor=11)
    document = profile.build_document(table, settings, [], [], [])
    roles = {block["name"]: block["role"] for block in document["columns"]}
    assert roles["a"] == "count" and roles["d"] == "count"
    assert roles["b"] == "continuous"
    page = _page()
    assert "its `role` is read from the rule, not from its cells" in page
    assert "a computed column's published `role` is: `A`'s role for an order rule" in page


# -- THE EVENT TABLE AT THE OWNER'S FLOOR ------------------------------------------------------


def test_the_event_table_sits_at_the_owner_s_floor_and_holds_each_rule():
    assert event_table.ROWS_AT_THE_FLOOR == 20000
    for maker in (
        event_table.event_rows, event_table.event_table, event_table.chain_rows, event_table.layout_rows,
        event_table.heap_rows, event_table.sum_rows, event_table.exponent_rows, event_table.seconds_rows,
        event_table.day_end_rows,
    ):
        assert inspect.signature(maker).parameters["rows"].default == 20000, maker
    rows = event_table.event_rows(rows=3000)
    assert event_table.event_table(rows=3000).count("\n") == 3001
    assert event_table.event_table(rows=50) == event_table.event_table(rows=50)
    header = {name: at for at, name in enumerate(event_table.HEADER)}
    pregnant = 0
    for row in rows:
        started = row[header["started_on"]]
        ended = row[header["ended_on"]]
        assert ended >= started
        gap = datetime.date.fromisoformat(ended) - datetime.date.fromisoformat(started)
        assert gap.days == int(row[header["days_open"]])
        assert row[header["closed_at"]] >= row[header["opened_at"]]
        assert Fraction(row[header["units"]]) * Fraction(row[header["rate"]]) == Fraction(row[header["total"]])
        assert not (row[header["gender"]] == "M" and row[header["pregnant"]] == "yes")
        pregnant += row[header["pregnant"]] == "yes"
    assert pregnant > 11
    keyed = event_table.event_rows(rows=3000, keyed_rows=150)
    assert sum(1 for row in keyed if row[header["closed_at"]] < row[header["opened_at"]]) == 150
    assert event_table.event_rows(rows=300, keyed_rows=0) == event_table.event_rows(rows=300)
    subjects = {row[0] for row in event_table.event_rows(rows=30, events_per_subject=3)}
    assert len(subjects) == 10
    for arrived, seen, left, left_on, _site in event_table.chain_rows(rows=3000):
        assert arrived <= seen <= left and left.startswith(left_on)


# -- THE SENTENCES A BUILDER COULD MISREAD ------------------------------------------------------


def test_the_page_holds_each_ruling_a_builder_reads():
    page = _page()
    for words in (
        "**A BUILDER MAY NOT ADD A CONDITION.**",
        "`D`'s bands close on the RIGHT.",
        "A value band of `D` holds `edge(k) < x <= edge(k + 1)`",
        "A rule that was never one is not a violated rule.",
        "**Theorem P.**",
        "Theorem R (the phrase class, for every carrier).**",
        "**Proposition T.**",
        "**Proposition B.**",
        "ties by kind take `formula` first",
        "a source option for EVERY number column and unit",
        "A step's word is keyed by the rule's identity",
        "**A NEW RULE 6 of the derived option:** every inner band holds a multiple of `g`",
        "**Rule 4 reads a level with no edge, and no row in `D`'s `missing` band beside that band of `A`, as met:**",
        "**A CHAIN OF EVENTS IS CARRIED AS A STAR.**",
        "The ONE THRESHOLD, in words a builder cannot misread: phrase for `v` from 0 to `f - 1`; the exact count `v` from `f` to `L(n)`, a derived carrier only",
        "and `B` (`C`) is another column, not named `identifier` by the person, not held,",
        "- **OPEN2.** `v(T) <= L(n)`, `v` read over `T`'s own cells",
        "- **OPEN3.** The rows where every column of the rule's BASE holds a reading (`A`; `A` and a source `D`; `X` and `Y`) number at least `f`",
        "| DATE beside STAMP: either column written as a date on any cell, or `grain` `\"day\"` | whole calendar days between the two days on every row, the clock never read, in either order |",
        "| CLOCK beside CLOCK | seconds within the day, with no wrap: a pair crossing midnight is a failing row |",
        "A gap of 0 HOLDS the rule",
        "the rule's `grain` is `\"day\"` and any `B` cell holding a clock counts as failing in that option",
        "under `grain` `\"day\"` it is one day.",
        "a level with no edge takes 0 on every row, so `B` is `A`; in a count class its `v` failing rows take `-g`, and the count class wins.",
        "the band holding 0 gives EXACTLY the failing rows they leave, `v` less their rows, readings below 0",
        "read once on the base for the whole partition, never on the real `v`",
        "Where the band holds 0 rows, every rank from `k(p_top)` up takes the top edge;",
        "readings below 0 (`-g` in the lowest band;",
        "FIXTURE: `tests/rules_event_table.py`, `event_table()` at 20,000 rows, seed 7, invented, one rule of each kind written on every row.",
        "`L(n) = max(f, floor(n / 100))`, so 200 rows at 20,000 rows and 20,000 at 2,000,000, and never under `f`.",
        "where `B`'s first layout is coarser than `g`, a derived option's sum in `W'` may be a value that layout does not write",
        "a number form tied to a value's size or sign (figures grouped from 1,000, a point with no figure before it below 1, a plus sign, a padded width) held by `f` rows of `B` asks `W'` for `f` rows whose sum takes that form",
        "That case alone: a date's, a stamp's or a clock's layout writes any value, and a form the sums can take on `f` rows tells nothing.",
        "where THREE SOURCE CONDITIONS hold (REPAIR 1; the third REPAIR 2)",
        "where `D`'s class is the phrase, its readings below 0 are set to 0, which Lemma 4 (ii) shows moves no edge, and a count class's readings stay as they are",
        "Every value band of `D`'s level but the highest holds at least `max(2 f, f + 4)` rows; the highest holds at least that many or 0 rows, its edge then `D`'s largest reading.",
        "where the highest band holds 0 rows, `(m - 1) - k(p_top) >= f + 1`, `p_top` the level's highest percent.",
    ):
        assert words in page, words


def test_the_kpis_are_restated_at_the_floor_and_unstamped():
    page = _page()
    assert "**`K-S6-06`, restated at 20,000 rows, a HEADLINE.**" in page
    assert "`tests/rules_event_table.py`" in page
    assert "after lane CHON's switch-on" in page
    assert "by `synthtwin profile`, `generate` and `validate`, three twin seeds; green only where (i) to (v) and (viii) are met on all three." in page
    assert "| (v) classes | `event_rows(keyed_rows=6)` and `event_rows(keyed_rows=150)`: that many rows keyed into (ii) | the phrase and 0 twin rows; the count 150 and exactly 150 |" in page
    assert "| (vii) a chain of events (REPAIR 1) | `chain_rows()`" in page
    assert "| (viii) a formula written from binary64 (REPAIR 1) | `event_rows(binary_rates=True)`" in page
    assert "**`K-S6-11`, DEFINED for lane RD.**" in page
    assert "**`K-BC-10`'s three readings.** PLACED:" in page
    assert "UNPLACED:" in page
    assert "and never fail the KPI, since nothing promised otherwise." in page
    assert "NEAR-RULE (REPAIR 1; private only, never published): a pair over the limit, `L < v`, whose failing share over the rows where both read is under a fifth of BREAK" in page
    assert "Neither is stamped by this page" in page


def test_every_limit_names_its_owner_and_verdict_three_has_its_rows():
    page = _page()
    limits = page[page.index("*MR.13 Stated limits") : page.index("**4.6b.9 (h), read with this page.**")]
    for number in range(1, 20):
        one = limits[limits.index(f" {number}. ") :]
        following = f" {number + 1}. "
        one = one[: one.index(following)] if following in one else one
        assert "Owner" in one or "owner" in one, number
    table = page[page.index("*MR.11 VERDICT-3's five items*") : page.index("*MR.12 The builders")]
    for item in ("| 1, ", "| 2, ", "| 3, ", "| 4, ", "| 5, "):
        assert item in table
    assert "**RO2 (a chain of events; the orchestrator's ruling 1 (1) of 2026-11-02), after the rules gate. What it must PUBLISH:**" in page
    assert "Staying: the bound on a derived column's pinned order statistics, until the verify reads Proposition B as rewritten (REPAIR 1)" in page


def test_the_page_is_recorded_as_a_plan_decision_and_a_changelog_entry():
    assert "## Decision P4-D452" in PLAN.read_text(encoding="utf-8")
    assert "P4-D452" in CHANGES.read_text(encoding="utf-8")


# -- REPAIR 2'S SENTENCES AND THE ONE BAND'S THRESHOLD, PINNED AT THE MERGE (MR OWES 1 AND 2) ----


def test_repair_two_s_sentences_a_builder_could_misread_are_pinned_word_for_word():
    """The nine sentences of repair 2 that the page's verify 2 mutated with no case going red, and
    the corner limit 19 states beside a count class within a few rows of `L` (batch 4o's merge)."""
    page = _page()
    for words in (
        # Theorem R's domain.
        "A derived carrier lies in it where `B`'s first layout writes `g` and its `W'` needs no sum past "
        "that layout's last value; a derived pair whose `B` is coarser than `A`, or a clock pair whose every "
        "`W'` needs such a sum, lies outside it, rule B's residual named in the proof, where the twin's "
        "writer still keeps `B >= A` (MR.2).",
        # MR.2's count class.
        "its other rows its multiples from 0 to `hi` (that edge where its rungs tie) (REPAIR 1: the first "
        "text spread such a band's multiples evenly, and the twin then held 160 or 152 failing rows against "
        "a class of 163, MEASURED by skeptic 1)",
        # MR.1's SOURCE row.
        "| order `A <= B`, SOURCE `D` | those rows, and rows where `B` differs from `A + D x unit`, held at "
        "the last value `B`'s layout writes where the sum passes it (REPAIR 2; a reading on one side only "
        "included) |",
        # MR.2's move past a band's upper edge.
        "So `B >= A` exactly where `D >= 0`, each class holds as placed, and the twin's `B - A` differs "
        "from its reading by less than one step of `B`'s layout, and may pass its band's upper edge by as "
        "much: a move `K-S6-11` names, and the row stands among the twin's DEVIATIONS.",
        # Theorem P (a)'s first published form.
        "(a) OPEN1 reads names, positions, roles, answers, `numeric_styles`, `B`'s first published form "
        "(named the same whether or not the rule is carried, MR.6 (a); REPAIR 2) and the holds and "
        "top-codes `DESC` publishes, which `T` shares (the hold, top-code and pooling words for `B`: "
        "limit 6).",
        # The builder rule's OPEN1 clause.
        "No filter on `B`'s role, its facts (but those OPEN1 and the third source condition name, published "
        "alike whether or not the rule is carried), its overlap with `A`, its share of zero gaps, a "
        "correlation, a sample or a screen may decide them: a test on a sample may only prove a rule false "
        "by finding `L + 1` failing rows.",
        # Limit 19: the one band refused away from 0.
        "Away from 0 the rule is lost: `B = A + 7` on every row but 1 to 21 rows a day or more later "
        "(`heap_rows(heap_days=7, above=1)`) keeps no level, the one band is refused (writing `B = A` would "
        "erase the 7 days), and the twin breaks the order on about half its rows (49.8 per cent, MR.9); "
        "from 22 rows above the deciles carry it.",
        # MR.9: from 22 rows above.
        "With 11 or fewer rows above, no level under either bound; from 22, the deciles under either.",
        # MR.9's lab paragraph.
        "`ref_high` from `ref_low`: rule 4 refuses each of the 9 pairs of levels with an edge, only the "
        "one-band level is left, and the gap is 0 on fewer than 99 of 100 rows (limit 14).",
        # Limit 19: the corner beside a count class within a few rows of `L` (MR OWES 2).
        "Beside a count class within a few rows of `L` the heap at 0 is lost too (MEASURED by the page's "
        "verify 2 at 20,000 rows, `L` = 200): 190 rows at -1 and 15 above read a class count of 190, every "
        "level with an edge refused, and the gap 0 on 98.98 per cent of rows, under MR.7's 99 of 100, so "
        "the family is REFUSED and the rule lost; so are 200 failing rows with 1 above and 180 with 21 "
        "above, while 185 with 15 and 179 with 21 carry it and the twin breaks exactly `v` rows; uncarried, "
        "the twin breaks about half its ordered pairs (49.8 per cent, MR.9).",
        "The loss needs `v` and the rows above together past 1 in 100 of the rows, and `v` is at most `L`, "
        "so the corner is narrow; MR.7's item and `K-S6-08`'s fixtures stay as they are. Owner: RO.",
    ):
        assert words in page, words


def test_the_one_band_item_reads_its_99_in_100_below_the_floor_and_at_it():
    """MR.7's no-edge item at its threshold: 21 rows above a heap at 0 are 1.05 in 100 of 2,000 rows, so
    the gap is 0 on 98.95 per cent of them and the one band is not worth carrying; at the floor's 20,000
    rows they are 0.105 in 100 and it is (the page's verify 2, its helper leg)."""
    below = _gap_counts(event_table.heap_rows(rows=2000, above=21))
    assert below[0] == 1979 and sum(below.values()) == 2000
    assert not _one_band_worth(below)
    at_floor = _gap_counts(event_table.heap_rows(rows=20000, above=21))
    assert at_floor[0] == 19979 and sum(at_floor.values()) == 20000
    assert _one_band_worth(at_floor)
