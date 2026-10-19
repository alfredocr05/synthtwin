"""Layer L0's method page holds what its first repair round fixed (plan P4-D404).

WHY A FILE OF ITS OWN. Layer L0 of stage 6 is written before its code:
G4.2a, G4.2b, G5.7, G7.3l, G7A.4d, G12.15 and G14.3a of the generation
method bind lane BT, which has not started, and nothing in the product
reads them yet. The seal turns red on any edit of a sealed passage and
is re-sealed by whoever makes the edit, so it cannot tell a correction
from its undoing. This file can. Lane BTp's two reviews of 2026-10-18
found the page wrong in ten places; each check below is red on the page
as it stood at 8aa98356, and each says which finding it holds.

WHAT IS COMPUTED HERE, NOT READ. The share over pieces is run as G5.7d
item 3 writes it, with and without its ceiling `hi_p`, on the oracle's
three share cases; the ranks a heaped median can stand below its rung
are enumerated; the bands and deciles of the two fixed columns of oracle
case 1 are worked out from their counts; every row of G5.7i's table of
the count of few values is checked for its rows off; the twin's counts
of case 1 are read back without the lift; the window test of G12.15 is
checked against the exact positions it stands for; and the workbook
reader's own test of a record holding nothing is read from its source.
The rest pins wording, where the finding was a missing or wrong
sentence.

WHAT IS NOT HERE. No L0 code exists to run, so nothing here says a twin
meets its band totals. The oracle's cases (G14.3a) and K-S6-02 are where
lane BT runs the method.
"""
import pathlib
import re
from fractions import Fraction

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
METHOD = REPOSITORY / "docs" / "spec" / "generation-method-v1.md"
PLAN = REPOSITORY / "docs" / "plans" / "phase-4-columns.md"
CHANGES = REPOSITORY / "CHANGELOG.md"
WORKBOOK_READER = REPOSITORY / "src" / "synthtwin" / "workbook.py"


def _between(path, start, end):
    text = path.read_text(encoding="utf-8")
    at = text.index(start)
    stop = text.find(end, at + len(start))
    return text[at:] if stop < 0 else text[at:stop]


def _flat(text):
    return " ".join(text.split())


def _g42a():
    return _flat(_between(METHOD, "### G4.2a ", "### G4.2b "))


def _g42b():
    return _flat(_between(METHOD, "### G4.2b ", "### G4.3 "))


def _g57():
    return _flat(_between(METHOD, "### G5.7 The L0 band totals", "## G6. Numeric spelling"))


def _g57d():
    return _flat(_between(METHOD, "#### G5.7d ", "#### G5.7e "))


def _g57h():
    return _flat(_between(METHOD, "#### G5.7h ", "#### G5.7i "))


def _g57i():
    return _between(METHOD, "#### G5.7i ", "## G6. Numeric spelling")


def _g7a4d():
    return _flat(_between(METHOD, "### G7A.4d ", "### G7A.5 "))


def _g1215():
    return _flat(_between(METHOD, "### G12.15 ", "## G13. "))


def _g143a():
    return _flat(_between(METHOD, "### G14.3a ", "### G14.4 "))


def _case(number):
    cases = _g143a()
    at = cases.index(" %d. **" % number)
    stop = cases.find(" %d. **" % (number + 1), at)
    return cases[at:] if stop < 0 else cases[at:stop]


def _decision():
    return _flat(_between(PLAN, "## Decision P4-D404", "\n## Decision P4-D405"))


def _change():
    return _flat(
        _between(CHANGES, "### The method for twins whose columns meet", "\n### ")
    )


def _figure(text):
    return int(text.replace(",", ""))


# ------------------------------------------------- the share over pieces


def _share(runs, ceilings, strata):
    """G5.7d item 3: every piece starts at one stratum, and the rest go one
    at a time to the piece below its ceiling with the largest
    `A_p / (2 m_p + 1)`, compared without division, the lower piece on a
    tie. Strata no piece can take are not made."""
    given = [1 for _ in runs]
    for _ in range(strata - len(runs)):
        best = -1
        for p in range(len(runs)):
            if given[p] >= ceilings[p]:
                continue
            if best < 0 or runs[p] * (2 * given[best] + 1) > runs[best] * (
                2 * given[p] + 1
            ):
                best = p
        if best < 0:
            break
        given[best] = given[best] + 1
    return given


def _dhondt(runs, strata):
    given = [1 for _ in runs]
    for _ in range(strata - len(runs)):
        best = 0
        for p in range(1, len(runs)):
            if runs[p] * (given[best] + 1) > runs[best] * (given[p] + 1):
                best = p
        given[best] = given[best] + 1
    return given


def _free_points(points, read, low_published, high_published):
    """G5.7d item 3's F_p on whole numbers: the points of the piece no run
    reads, between two runs, or between a run and an end that is
    published."""
    lowest, highest = min(read), max(read)
    free = 0
    for point in points:
        if point in read:
            continue
        if lowest < point < highest:
            free = free + 1
        elif point < lowest and low_published:
            free = free + 1
        elif point > highest and high_published:
            free = free + 1
    return free


SHARE_CASE_B = (
    # (whole numbers of the piece, the values its runs read)
    (range(1, 2), {1}),
    (range(2, 4), {2, 3}),
    (range(4, 5), {4}),
    (range(5, 19), {5, 6, 7, 8, 9, 10, 11, 18}),
)
SHARE_CASE_C = (
    (range(1, 2), {1}),
    (range(2, 3), {2}),
    (range(3, 17), {3, 4, 5, 16}),
)
MANY_CELLS = 10_000


def _ceilings(pieces):
    return [
        min(MANY_CELLS, len(read) + _free_points(points, read, True, True))
        for points, read in pieces
    ]


def test_a_piece_is_never_given_more_strata_than_its_runs_and_free_points():
    """Skeptic 1, item 2, and the statistics skeptic, item 2 (b): held only
    to its cells, a piece of one whole number took two strata and a piece
    of two took three, strata no step can separate."""
    method = _g57d()
    assert "`hi_p = min(C_p, A_p + F_p)`" in method
    assert "**Strata that no piece can take are not made**" in method
    assert "`hi_p` is raised to `lo_p`" in method
    case = _case(6)
    for pieces, strata, held, today in (
        (SHARE_CASE_B, 18, [1, 2, 1, 14], [2, 3, 1, 12]),
        (SHARE_CASE_C, 15, [1, 1, 13], [3, 2, 10]),
    ):
        runs = [len(read) for _, read in pieces]
        assert _share(runs, _ceilings(pieces), strata) == held
        assert _share(runs, [MANY_CELLS for _ in runs], strata) == today
    assert "share 1, 2, 1 and 14" in case
    assert "share 1, 1 and 13" in case
    assert "`hi_p = C_p`, which gives 2, 3, 1 and 12, and 3, 2 and 10" in case
    assert "runs 1, 2, 1 and 8" in case and "`M_rest = 18`" in case
    assert "runs 1, 1 and 4" in case and "`M_rest = 15`" in case


def test_the_share_rounds_to_the_nearest_share_and_not_down():
    """The oracle's first share case, kept: Sainte-Lague against d'Hondt."""
    case = _case(6)
    assert _share([10, 3], [MANY_CELLS, MANY_CELLS], 7) == [5, 2]
    assert _dhondt([10, 3], 7) == [6, 1]
    assert "`M_rest = 7` share 5 and 2 strata" in case
    assert "`m_p + 1`, which gives 6 and 1" in case


def test_the_strata_beyond_the_runs_go_into_a_gap_and_lift_no_run():
    """Skeptic 1, item 1, and the statistics skeptic, item 2: walls alone
    move the division of the longest run and the lift above it into the
    top piece, which keeps the band totals and moves the threes onto 4."""
    method = _g57d()
    assert "3a. **WHERE THE STRATA BEYOND THE RUNS GO.**" in method
    assert "step 3 of G5.2a does NOT divide the piece's longest run" in method
    assert "the gap's free point NEAREST the divided stratum's value" in method
    assert "That was all but 416 of the 29,676 rows off" in method


# ------------------------------------------------- the count of few values

CASE_A = [800, 4157, 2952, 1247, 500, 200, 80, 30, 15, 8, 4, 2, 1, 1, 1, 1, 1]
CASE_B = {0: 1568, 1: 8436, 2: 5813, 3: 2464, 4: 1018, 5: 425, 6: 162, 7: 59,
          8: 30, 9: 14, 10: 7, 11: 1, 12: 2, 16: 1}
TWIN_A = {0: 800, 1: 2075, 2: 2075, 3: 3000, 4: 1200, 5: 500, 6: 200, 7: 51,
          8: 1, 9: 1, 10: 1, 11: 1, 12: 1, 13: 1, 14: 93}


def _cells(counts):
    out = []
    for value in sorted(counts):
        out += [value] * counts[value]
    return out


def _type7(cells, percent):
    h = Fraction((len(cells) - 1) * percent, 100)
    low = int(h)
    high = min(low + 1, len(cells) - 1)
    return cells[low] + (cells[high] - cells[low]) * (h - low)


def _bands(counts, edges):
    out = [0 for _ in range(len(edges) + 1)]
    for value, count in counts.items():
        band = sum(1 for edge in edges if value >= edge)
        out[band] = out[band] + count
    return out


def _rows_off(twin, real):
    return sum(r - t for t, r in zip(twin, real) if r > t)


def test_oracle_case_one_is_the_count_whose_twin_lifts_its_values():
    """Skeptic 1, item 1, and the statistics skeptic, item 2 (a): the case
    was a 1,000-row column today's product misses by five rows; it is now
    the two fixed columns that reproduce the 30,000-row defect, frozen at
    each value."""
    case = _case(1)
    fixed_a = dict(enumerate(CASE_A))
    assert ("800, 4,157, 2,952, 1,247, 500, 200, 80, 30, 15, 8, 4 and 2 cells "
            "at 0 to 11 and one at each of 12 to 16") in case
    assert ("1,568, 8,436, 5,813, 2,464, 1,018, 425, 162, 59, 30, 14, 7, 1 and 2 "
            "cells at 0 to 12 and one at 16") in case
    assert sum(CASE_A) == 10_000 and sum(CASE_B.values()) == 20_000
    for counts, stated in (
        (fixed_a, "800, 4,157, 2,952 and 2,091"),
        (CASE_B, "1,568, 8,436, 5,813 and 4,183"),
    ):
        cells = _cells(counts)
        deciles = sorted({_type7(cells, k) for k in range(10, 100, 10)})
        assert deciles == [1, 2, 3]
        bands = _bands(counts, deciles)
        assert ", ".join("{:,}".format(b) for b in bands[:-1]) + " and {:,}".format(
            bands[-1]
        ) == stated
        assert stated in case
        share = Fraction(counts[3], bands[3])
        assert share > Fraction(55, 100)
        assert "{:.1f}".format(float(share) * 100) in case
    assert "The vector freezes the twin's count AT EACH VALUE" in case
    assert "more than 55 per cent of the top band" in case
    assert "G6.5a's ascending fill kept inside the top piece" in case
    assert "1,000-row column" not in case


def test_g57i_measures_the_defect_on_the_products_twins_and_names_its_cause():
    """Skeptic 1, item 1, and the statistics skeptic, item 4: the page said
    the misses came from the ties, measured 90 rows on one lucky draw, and
    gave M6's 30,000 rows to a prototype."""
    measured = _g57i()
    rows = 0
    for line in measured.splitlines():
        found = re.match(
            r"\| ([0-9,]+), (fixed counts|drawn)[^|]*\| ([0-9, /]+) \| ([0-9, /]+) \| ([0-9,]+) \|",
            line,
        )
        if not found:
            continue
        twin = [_figure(x) for x in found.group(3).split(" / ")]
        real = [_figure(x) for x in found.group(4).split(" / ")]
        assert sum(twin) == sum(real) == _figure(found.group(1))
        assert _rows_off(twin, real) == _figure(found.group(5))
        rows = rows + 1
    assert rows == 5
    flat = _flat(measured)
    assert "30,000 rows on the value 3 against the real 12,465" in flat
    assert "375 rows on its age" in flat and "11 to 28" in flat
    assert "m6_200000" in flat
    assert "prototype" not in _g57()
    assert "held prototype" not in _decision()
    assert "not on a prototype" in _decision()
    assert "29,676" in _decision() and "29,676" in _change()


def test_the_lift_is_read_back_from_what_the_twin_wrote():
    """The mechanism paragraph's own numbers: today's twin of case 1 (a), and
    the same strata without the lift."""
    flat = _flat(_g57i())
    assert ("800 zeros, 2,075 ones, 2,075 twos, 3,000 threes, 1,200 fours, 500 "
            "fives, 200 sixes, 51 sevens, one cell at each of 8 to 13 and 93 at 14") in flat
    real = _bands(dict(enumerate(CASE_A)), [1, 2, 3])
    written = _bands(TWIN_A, [1, 2, 3])
    assert written == [800, 2075, 2075, 5050]
    assert _rows_off(written, real) == 2959
    unlifted = {0: 800, 1: TWIN_A[1] + TWIN_A[2], 2: TWIN_A[3]}
    unlifted[3] = sum(TWIN_A[v] for v in TWIN_A if v >= 4)
    assert _rows_off(_bands(unlifted, [1, 2, 3]), real) == 48
    assert "the same strata miss by 48 rows, not 2,959" in flat
    assert "at 100,000 rows by 416, not 29,676" in flat


def test_the_shape_inside_a_band_l0_leaves_has_an_owner():
    """Skeptic 1, item 1: the counts at each value inside the top band, the
    mode count, the count of different numbers and the field widths."""
    decision = _decision()
    assert "lane G2T's, G5's statistics lane" in decision
    assert "`mode_count`, `n_distinct_values`, `field_widths`" in decision
    assert "named in plan P4-D404 with its owner" in _flat(_g57i())


# ------------------------------------------------- the records holding nothing


def test_the_workbook_reader_counts_only_absent_and_blank_cells_as_holding_nothing():
    """The fact skeptic 1's item 3 rests on, read from the reader itself: an
    `empty` cell makes its record hold something."""
    source = WORKBOOK_READER.read_text(encoding="utf-8")
    assert "if standing.kind not in (CELL_ABSENT, CELL_BLANK):\n                holding = True" in source
    assert "`empty` cell, the empty string, is content to every reader" in _g42a()


def test_a_workbook_reserves_by_class_and_writes_a_reserved_blank_as_blank():
    """Skeptic 1, item 3: a reservation of cells holding no text, written
    with no cells at all, turned twelve formatted blank records into absent
    ones and missed every column's class census."""
    reservation = _g42a()
    assert "2. in a workbook, BY CLASS" in reservation
    assert "No cell that step 1 makes `empty` is ever reserved." in reservation
    assert "`absent` while the number of `absent` cells it hands out lasts and then `blank`" in reservation
    assert "a `blank` cell as a cell holding nothing in its style, and NOT as a row with no cells at all" in reservation
    assert "in G4.2's order (the order the placement wrote them in, so before the arrangement" in reservation
    assert "`H` is at least `E` there too" in reservation
    assert "by the class G2.2 step 1 fixes for it before the arrangement" in _g42b()
    case = _case(12)
    assert "a reserved row written with no cells at all" in case
    assert "`blank` 12, `absent` 0 and `empty_rows_inside` 12" in case
    assert "step 1's classes handed out in row order alone" in case
    assert "lane LM2's" in _decision()


# ------------------------------------------------- the KPI and its yardstick


def test_k_s6_02_counts_every_b1_miss_and_names_its_yardstick():
    """Skeptic 1, item 4, and the statistics skeptic, items 2 (c) and 3:
    clause (iv) passed every miss rule B1 names, and named no window."""
    facts = _g57h()
    assert "save the misses rule B1 names" not in facts
    assert "4. 0 within-column facts that the twin made without L0 HOLDS and the twin made with it MISSES" in facts
    assert "at G12.2's half unit, extended only beside a cut as G12.15 says" in facts
    assert "a count above 0 is a named residual in the plan, never a pass" in facts
    assert "it is not an allowance of this KPI" in facts
    assert "5. within the bands, on every count column" in facts
    assert "0 regressions" in facts
    decision = _decision()
    assert "save rule B1's named misses" not in decision
    assert "never a pass" in decision


def _reaches_above(k, K, g, cut):
    return k * K + (g + 2) * (K - 1) >= cut * (K - 1)


def _reaches_below(k, K, g, cut):
    return k * K - (g + 2) * (K - 1) <= cut * (K - 1)


def test_g1215_keeps_the_half_unit_and_extends_only_beside_a_cut():
    """The statistics skeptic, item 1: one whole unit on both ends of every
    window widened the mean windows of whole-number columns by 9 to 20 per
    cent, where the piece repair acts only beside a cut."""
    windows = _g1215()
    assert "each end widens by ONE unit of the grid, not half" not in windows
    assert "**The half unit stays G12.2's; only an end beside a cut is extended.**" in windows
    assert "A[k] = min(A[k], hf_p) where k * K + (g_max + 2) * (K - 1) >= R_hi * (K - 1)" in windows
    assert "B[k] = max(B[k], lf_p) where k * K - (g_max + 2) * (K - 1) <= R_lo * (K - 1)" in windows
    assert "**Why not one whole unit on both ends everywhere**" in windows
    for K in (5, 12, 40):
        for g in (0, 1, 3):
            for k in range(K):
                position = Fraction(k * K, K - 1)
                for cut in range(K + 1):
                    assert _reaches_above(k, K, g, cut) == (position + g + 2 >= cut)
                    assert _reaches_below(k, K, g, cut) == (position - g - 2 <= cut)
    case = _case(5)
    assert "every window widened by a whole unit" in case
    assert "the extension withdrawn" in case


# ------------------------------------------------- the two small corrections


def test_a_heaped_median_stands_at_most_eight_ranks_below_its_rung():
    """Skeptic 1, item 5: the type-7 median of 1,000 rows reads ranks 499 and
    500, so a heap of nine rows holding it starts at rank 492 at the
    lowest."""
    K, heap = 1000, 9
    h = Fraction(K - 1, 2)
    rung_rank = K * 50 // 100
    gaps = []
    for start in range(K - heap + 1):
        held = range(start, start + heap)
        if int(h) in held and int(h) + 1 in held:
            gaps += [rung_rank - start]
    assert max(gaps) == 8 and min(gaps) == 1
    case = _case(4)
    assert "`R_j` lies up to eight ranks below `P_j = 500`" in case
    assert "nine ranks" not in case


def test_a_half_groups_derived_count_is_never_printed():
    """Skeptic 1, item 6: a half's count is formed by subtraction and can
    fall below the floor."""
    clocks = _g7a4d()
    assert "**A half's count is never printed.**" in clocks
    assert "named against the whole group's published count" in clocks
