"""Layer L0's method page holds what its two repair rounds fixed (plan P4-D404).

WHY A FILE OF ITS OWN. Layer L0 of stage 6 is written before its code:
G4.2a, G4.2b, G5.7, G7.3l, G7A.4d, G12.15 and G14.3a of the generation
method bind lane BT, which has not started, and nothing in the product
reads them yet. The seal turns red on any edit of a sealed passage and
is re-sealed by whoever makes the edit, so it cannot tell a correction
from its undoing. This file can. Lane BTp's two reviews of 2026-10-18
found the page wrong in ten places; each check of the first round is red
on the page as it stood at 8aa98356, and each says which finding it
holds. The lane's verify of 0147e236 and the outside review of that head
found nine more (the second round, at the end of this file); each of
those checks is red on the page at 0147e236.

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


def _g43():
    return _flat(_between(METHOD, "### G4.3 ", "## G5. "))


def _g57a():
    return _flat(_between(METHOD, "#### G5.7a ", "#### G5.7b "))


def _g57b():
    return _flat(_between(METHOD, "#### G5.7b ", "#### G5.7c "))


def _g73l():
    return _flat(_between(METHOD, "#### G7.3l ", "### G7.4 "))


def _g75():
    return _flat(_between(METHOD, "### G7.5 ", "### G7.9 "))


def _g7a4():
    return _flat(_between(METHOD, "### G7A.4 ", "### G7A.4b "))


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


# ------------------------------------------------- the second repair round
#
# The lane's verify of 0147e236 (its item 1) and the outside review of that
# head (its items 1 to 8). Every check below is red on the page at 0147e236.


def test_the_interface_hands_over_a_workbook_cells_class():
    """The verify's item 1: G4.2a said G4.2b hands a cell's class over, and
    G4.2b handed over three things, none of them the class, so a writer had
    to deal the classes out again in row order after the arrangement."""
    interface = _g42b()
    assert "Each cell is handed over as four things" in interface
    assert "three things" not in interface
    assert ("in a workbook, its CLASS, the one G2.2 step 1 fixed for it before "
            "the arrangement (G4.2a)") in interface
    assert "one of the five value classes on a cell holding text" in interface
    assert "G16 never changes any of them" in interface
    assert ("The texts handed over, and in a workbook their classes, as a "
            "multiset, are the column's cells less its reserved cells") in interface
    reservation = _g42a()
    assert "**The cells holding text take their classes before the arrangement too**" in reservation
    assert "None of them is handed out again after the arrangement" in reservation
    assert ("step 7 writes each arranged cell by the class G4.2b handed over, "
            "with its format kind and its date or clock kind, never by a class "
            "handed out again after the arrangement") in reservation
    case = _case(13)
    assert ("the class not handed over, step 1 run again in row order after "
            "the arrangement") in case


def _half_before(cut, others_before):
    """G7A.4d: the half of a cut group before the edge holds the cut rank
    less the cells of every OTHER stretch wholly before the edge."""
    return cut - sum(others_before)


def test_a_cut_clock_group_counts_its_boundary_once():
    """Codex item 1: the half count subtracted the low boundary on its own,
    though G7A.4b step 2's `f_j` already counts it inside its group."""
    low_tail, group, cut = 11, 100, 39
    ranks = ["tail"] * low_tail + ["group"] * group
    assert ranks[low_tail] == "group"  # the boundary is the group's first rank
    below = sum(1 for r in ranks[:cut] if r == "group")
    assert _half_before(cut, [low_tail]) == below == 28
    assert group - below == 72
    boundary_again = _half_before(cut, [low_tail, 1])
    assert boundary_again == 27 and low_tail + boundary_again == 38
    clocks = _g7a4d()
    assert "the low tail and its boundary" not in clocks
    assert "so it is never subtracted on its own" in clocks
    assert "its halves count 28 and 72" in clocks
    case = _case(10)
    assert "the halves count 28 and 72" in case
    assert "which gives 27 and 73 and puts 38 cells below the edge" in case


def _nearest_free(drawn, absent, low, high):
    """G7.5's step: the nearest unit not absent, earlier before later at one
    distance, inside [low, high]."""
    for distance in range(0, high - low + 1):
        for unit in (drawn - distance, drawn + distance):
            if low <= unit <= high and unit not in absent:
                return unit
    return None


def test_the_absent_spelling_steps_never_cross_a_cut():
    """Codex item 2: G7.5's last spelling step searched the window and then
    the whole range, so a rank below the edge could be written on it."""
    jan29, edge = 29, 32  # days of January; the edge is February 1
    absent = {30, 31}
    assert _nearest_free(31, absent, 1, 366) == edge
    assert _nearest_free(31, absent, jan29, edge - 1) == jan29
    dates = _g73l()
    assert "**And the spelling step keeps the piece.**" in dates
    assert "both ranges are cut to the rank's PIECE" in dates
    assert "The cell never crosses a cut." in dates
    assert "both ranges are cut to the rank's L0 piece" in _g75()
    assert "the window is cut to the rank's piece" in _g7a4()
    assert "**The absent-spelling step keeps the piece.**" in _g7a4d()
    assert "which writes February 1 and moves a row across the cut" in _case(7)
    assert "Mutant: the window uncut" in _case(9)


CASE_14 = {Fraction(k, 10): 100 for k in range(1, 7)}
CASE_14[Fraction(101, 100)] = 150
CASE_14[Fraction(102, 100)] = 150
CASE_14[Fraction(2)] = 100


def _points(width, low, high):
    """The points of the grid of `width` figures in [low, high)."""
    step = Fraction(1, 10 ** width)
    first = -((-low) // step)
    return [k * step for k in range(int(first), int(-((-high) // step)))]


def test_p3_reads_the_widest_grid_and_a_piece_takes_a_finer_one():
    """Codex item 3: (P3) read on the commonest width's grid refused a real
    column whose band between two hundredths holds no tenth."""
    cells = _cells(CASE_14)
    assert len(cells) == 1000
    deciles = sorted({_type7(cells, k) for k in range(10, 100, 10)})
    assert Fraction(101, 100) in deciles and Fraction(102, 100) in deciles
    band = sum(c for v, c in CASE_14.items() if Fraction(101, 100) <= v < Fraction(102, 100))
    assert band == 150
    assert _points(1, Fraction(101, 100), Fraction(102, 100)) == []
    assert _points(2, Fraction(101, 100), Fraction(102, 100)) == [Fraction(101, 100)]
    preconditions = _g57a()
    assert "a point of the grid of the WIDEST named width" in preconditions
    assert "a point of the written grid where G5.2a step 1 finds one" not in preconditions
    assert "and so does every piece with cells of G5.7b" in preconditions
    assert "**THE PIECE GRID.**" in _g57b()
    assert "NARROWEST named width of `fraction_widths`" in _g57b()
    case = _case(14)
    assert "150 at `1.01`, 150 at `1.02`" in case
    assert "which makes the column without L0 (rule B3)" in case


CASE_15 = {Fraction(1): 800, Fraction(2): 100}
for _k in range(1, 101):
    CASE_15[1 + Fraction(_k, 1000)] = 1


def test_the_word_budget_is_the_columns_without_l0():
    """Codex item 4: G4.3's budget read the lowered `M`, so every later
    column drew other words."""
    cells = _cells(CASE_15)
    edges = sorted({_type7(cells, k) for k in range(10, 100, 10)})
    assert edges == [1, Fraction(10002, 10000), Fraction(119, 100)]
    pieces = [(1, edges[1]), (edges[1], edges[2]), (edges[2], Fraction(2001, 1000))]
    points = sum(len(_points(1, low, high)) for low, high in pieces)
    assert points == 11
    strata = len(CASE_15)
    assert strata == 102 and strata - 2 == 100
    budget = _g43()
    assert ("**On an eligible column (layer L0, G5.7) `S`, `pinned` and `zeroed` "
            "are read as G5.2 gives them to the column WITHOUT L0**") in budget
    layout = _g57d()
    assert "**Neither moves the word budget.**" in layout
    assert "G4.3's word budget reads the lowered `M`" not in layout
    assert "as if its word were `2**63`" in layout
    case = _case(15)
    assert "`M = 102` without L0 is lowered to at most 11" in case
    assert "still draws its 100 words" in case


def _make_in_gap(strata, low_end, high_end, eligible_only):
    """G5.7d item 3a on whole numbers: make one stratum in the widest gap,
    the lowest on a tie, dividing the stratum of more cells beside it."""
    taken = {v for v, _ in strata}
    best = None
    for i in range(len(strata) + 1):
        below = strata[i - 1] if i > 0 else None
        above = strata[i] if i < len(strata) else None
        low = below[0] + 1 if below else low_end
        high = above[0] - 1 if above else high_end
        free = [v for v in range(low, high + 1) if v not in taken]
        sides = [s for s in (below, above) if s is not None]
        if not free or (eligible_only and max(c for _, c in sides) < 2):
            continue
        if best is None or len(free) > best[0]:
            best = (len(free), i, free)
    _, i, free = best
    below = strata[i - 1] if i > 0 else None
    above = strata[i] if i < len(strata) else None
    if below is None or (above is not None and above[1] > below[1]):
        value, cells = above
        point, at = free[-1], i
    else:
        value, cells = below
        point, at = free[0], i - 1
    kept, moved = cells - cells // 2, cells // 2
    out = list(strata)
    out[at] = (value, kept)
    out.insert(at + 1 if point > value else at, (point, moved))
    return sorted(out)


def test_a_stratum_is_made_only_in_an_eligible_gap():
    """Codex item 5: the widest gap between two strata of one cell each
    divided a single cell into strata of none and one."""
    strata = [(1, 1), (10, 1), (11, 100), (13, 100)]
    made = _make_in_gap(strata, 1, 13, True)
    assert made == [(1, 1), (10, 1), (11, 50), (12, 50), (13, 100)]
    assert min(c for _, c in made) >= 1
    mutant = _make_in_gap(strata, 1, 13, False)
    assert min(c for _, c in mutant) == 0
    layout = _g57d()
    assert "in the piece's WIDEST ELIGIBLE GAP" in layout
    assert "a gap no stratum beside which can be divided is never taken" in layout
    case = _case(16)
    assert "the 100 cells at 11 divided into 50 and 50" in case
    assert "strata of 0 and 1" in case


def test_a_label_cells_band_is_its_level_never_its_text():
    """Codex item 6: label cells have no number or clock reading, so the
    page sent every one of them to `other`."""
    interface = _g42b()
    assert "**On a label column a cell's band is its LEVEL, never its text.**" in interface
    assert "read off the cell's place in G8.4's content list" in interface
    assert "A cell G8.3 writes for a WITHHELD level has no published level and lies in `other`" in interface
    assert "the place of its level in the block's published order, counted from nought" in interface
    case = _case(13)
    assert "two level groups of 60 each, by level and not by text" in case


def test_a_short_text_reservation_reserves_the_first_targets():
    """Codex item 7: with `E_eff` below `E` the page still reserved every
    target row and declared one arranged row more than stood outside them."""
    rows, interior, e_eff = 120, 12, 11
    targets = []
    for k in range(1, interior + 1):
        row = k * rows // (interior + 1)
        while row in targets:
            row = row + 1
        targets += [row]
    assert len(set(targets)) == interior
    reserved = sorted(targets)[:e_eff]
    arranged = [r for r in range(rows) if r not in reserved]
    assert len(arranged) == rows - e_eff == 109
    assert rows - interior == 108
    reservation = _g42a()
    assert "the first `E_eff` of the `E` target rows" in reservation
    assert "a target after the first `E_eff` is an arranged row" in reservation
    case = _case(11)
    assert "the first eleven target rows in row order are reserved" in case
    assert "which declares 109 arranged rows with 108 left" in case


PCT = (0, 1, 5, 10, 25, 50, 75, 90, 95, 99, 100)


def test_the_clock_knots_name_index_and_percent_apart():
    """Codex item 8: `k_j` was a percent and was then used as an index of
    the eleven-entry `PCT`."""
    rows, cut, index = 400, 180, PCT.index(50)
    assert index == 5
    lower, upper = 100 * cut, rows * PCT[index]
    assert (lower, upper) == (18000, 20000)
    try:
        PCT[50]
    except IndexError:
        pass
    else:
        raise AssertionError("PCT has eleven entries")
    clocks = _g7a4d()
    assert "own position `P * PCT[k_j] / 100`" not in clocks
    assert "the smallest INDEX of the eleven-entry `PCT`" in clocks
    assert "at `P * q_j * 2**64`" in clocks
    assert "they stand at `18000 * 2**64` and `20000 * 2**64`" in clocks
    case = _case(9)
    assert "the upper knot at `20000 * 2**64`" in case
