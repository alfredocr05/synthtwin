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
those checks is red on the page at 0147e236. The verify of 11dd0b6b found
two more (a band written only at widths the census does not name, and a
stretch of no free point read as a gap); each of those checks is red on
the page at 11dd0b6b. The verify of that repair found three places that
read the first of them as always failing (P3), where it only can; their
checks are red on the repair as that verify read it.

LANE BT'S REPAIR (plan P4-D429, 2026-10-25) rebuilt the number columns'
half of G5.7 after its statistics skeptic measured the band map erasing
real codes: the column is made as today and moved the least the
description proves (G5.7c). The checks of the band map's layout (the
share over pieces held to `hi_p`, the strata beyond the runs in the
widest eligible gap, a heaped median's knot, the whole-unit window
extension beside a cut) went with it; each withdrawal is checked as
stated on the page, and the least move's proof is computed in their
place.

WHAT IS COMPUTED HERE, NOT READ. The ranks two equal published rungs
prove (G5.7c step 1) are checked over every column of up to nine cells
on three values, and a span one rank wider is shown unsound; the bands
and deciles of the two fixed columns of oracle case 1 are worked out
from their counts; every row of G5.7i's table of the count of few
values is checked for its rows off; the twin's counts of case 1 are read
back without the lift; and the workbook reader's own test of a record
holding nothing is read from its source. The rest pins wording, where
the finding was a missing or wrong sentence.

WHAT IS NOT HERE. Whether a twin meets its band totals: the gate
(`tests/test_stage6_band_totals.py`), the oracle's cases (G14.3a) and
K-S6-02 run the method.
"""
import pathlib
import re
from fractions import Fraction

from synthtwin.parsing import census_floor

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


# ------------------------------------------------- the least move (lane BT's repair)


def _type7_at(cells, percent):
    h = Fraction((len(cells) - 1) * percent, 100)
    low = int(h)
    high = min(low + 1, len(cells) - 1)
    return cells[low] + (cells[high] - cells[low]) * (h - low), h


def _ceil(fraction):
    return -((-fraction.numerator) // fraction.denominator)


def _heap_ranks(h_1, h_2, wider=0):
    """G5.7c step 1: two equal published rungs at `h_1 < h_2` prove the
    ranks from `floor(h_1)` to `ceil(h_2)`, where `ceil(h_1) <= floor(h_2)`;
    `wider` widens the span, the mutant."""
    if _ceil(h_1) > int(h_2):
        return None
    return range(int(h_1) - wider, _ceil(h_2) + 1 + wider)


def _proven_heaps_hold(wider):
    """Every column of up to nine cells on three values, every pair of
    percents in steps of five: the ranks two equal rungs prove hold the
    rungs' value. False at the first column where one does not."""
    percents = range(0, 101, 5)
    for size in range(2, 10):
        for low in range(size + 1):
            for high in range(size - low + 1):
                cells = [0] * low + [1] * high + [2] * (size - low - high)
                readings = [_type7_at(cells, q) for q in percents]
                for first in range(len(readings)):
                    for second in range(first + 1, len(readings)):
                        (v_1, h_1), (v_2, h_2) = readings[first], readings[second]
                        if v_1 != v_2:
                            continue
                        span = _heap_ranks(h_1, h_2, wider)
                        if span is None:
                            continue
                        for rank in span:
                            if 0 <= rank < size and cells[rank] != v_1:
                                return False
    return True


def test_two_equal_rungs_prove_the_ranks_the_page_says_and_no_more():
    """The statistics skeptic, item 1 (lane BT's repair): the band map read
    values the real column never held between a heap and a cut; the least
    move reads only what two equal rungs prove. Computed over every small
    column: the proven span holds the rungs' value, and a span one rank
    wider does not."""
    assert _proven_heaps_hold(0)
    assert not _proven_heaps_hold(1)
    least = _flat(_between(METHOD, "#### G5.7c ", "#### G5.7d "))
    assert "every order statistic from `ceil(h_1)` to `floor(h_2)`" in least
    assert "the real column holds `v` at every rank from `floor(h_1)` to `ceil(h_2)`: a PROVEN HEAP" in least
    assert "`min(max(w, L(r)), U(r))`" in least
    assert "Only published rungs are read, never a filled rung or a tail's reading" in least


def test_the_band_map_is_withdrawn_and_the_least_move_says_why():
    """The statistics skeptic, item 1: on the zoo's claims the band map
    emptied the code 871 and wrote 788, a code nobody wrote; the repair
    withdraws the layout over pieces, its share, its gap and its last
    guard, and states the least move's four steps."""
    least = _flat(_between(METHOD, "#### G5.7c ", "#### G5.7d "))
    for step in (
        "1. **THE PROVEN HEAPS.**",
        "2. **THE BAND TOTALS.**",
        "2a. **THE KEYS ONCE A ROW.**",
        "3. **THE DIFFERENT VALUES KEPT.**",
        "4. **THE MODE KEPT.**",
    ):
        assert step in least
    assert "**THE COLUMN IS MADE AS IT IS TODAY.**" in least
    assert "today's value nearest the piece, never a value made up" in least
    assert "And a rank moves toward the real column, save in one case." in least
    assert "Held to the band totals and to no value made up, no twin of that piece does better." in least
    assert "`hi_p`" not in least and "Sainte-Lague" not in least
    withdrawn = _g57d()
    assert "(withdrawn by lane BT's repair)" in withdrawn
    why = _g57()
    assert "**Why the least move, and not the band map the first build read the" in _between(
        METHOD, "### G5.7 The L0 band totals", "#### G5.7a "
    )
    assert "872" in why and "788, a code nobody wrote" in why
    assert "2,232 rows of the Kolmogorov-Smirnov distance" in why
    assert "today's twin's 70" in why and "the distance is 26 rows" in why
    passes = _flat(_between(METHOD, "#### G5.7f ", "#### G5.7g "))
    assert "runs on an eligible column exactly as on any other" in passes
    assert "So no pass needs a wall" in passes
    assert "16. *(Withdrawn by lane BT's repair" in _g143a()


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
    assert "The vectors freeze the twin's count AT EACH VALUE" in case
    assert "more than 55 per cent of the top band" in case
    assert "Mutant: G5.7c withdrawn, which is today's twin, its bands missed" in case
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
    assert ("4. 0 checks of the quality report, on any column or on the file, that "
            "the twin made without L0 holds and the twin made with it misses") in facts
    assert "(today's windows of G12.2, G12.3 and G12.3a at G12.2's half unit)" in facts
    assert "the mode's among them" in facts
    assert "a count above 0 is a named residual in the plan, never a pass" in facts
    assert "Rule B1 is how the generator behaves, and it excuses nothing" in facts
    assert "5. on every eligible column of numbers, the Kolmogorov-Smirnov distance" in facts
    assert "0 regressions" in facts
    assert "6. on every eligible column whose real cells all differ" in facts
    assert "the health zoo's 25 exports" in facts
    decision = _decision()
    assert "save rule B1's named misses" not in decision
    assert "never a pass" in decision


def test_g1215_keeps_todays_windows_and_owes_the_clock_mirror_before_chc():
    """The statistics skeptic of lane BTp, item 1: one whole unit on both
    ends of every window widened the mean windows of whole-number columns
    by 9 to 20 per cent. Lane BT's repair withdraws the band map, so a
    number column's windows are today's; the orchestrator's ruling (b) of
    2026-10-25 puts the clock's quality-report mirror in G12.15's own text."""
    windows = _g1215()
    assert "each end widens by ONE unit of the grid, not half" not in windows
    assert "**On an eligible number column the windows are today's.**" in windows
    assert "**Why not one whole unit on both ends everywhere**" in windows
    assert "**The quality report's mirror of the clock's knots is OWED BY LANE BT2**" in windows
    assert "BUILT BEFORE THE LANDING THAT LETS `validate` READ A CHAIN (lane CHc)" in windows
    assert "`validate` refuses a description whose `statistical` slot is filled (S12)" in windows


# ------------------------------------------------- the two small corrections


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
    assert ("Mutant: the classes not carried (`Twin.sheet_dealt` empty), the "
            "writer dealing them again in row order") in case


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
    assert ("so it is never subtracted on its own, and never where it stands "
            "in the group being cut") in clocks
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
    assert ("Mutant: the windows uncut, which lets a rank below the cut be "
            "stepped onto the edge or after it") in _case(7)


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
    assert "which fails (P3) and makes the column without L0 (rule B3)" in case


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
    least = _flat(_between(METHOD, "#### G5.7c ", "#### G5.7d "))
    assert ("**What it promises.** No word: the column draws exactly the words "
            "G4.3 budgets for it, in today's order, so no later column moves") in least
    assert "G4.3's word budget reads the lowered `M`" not in _g57()
    case = _case(15)
    assert "the first column draws its 100 words" in case
    assert "byte for byte its cells without L0" in case


CASE_17_SPELLINGS = []
for _k in range(1, 11):
    CASE_17_SPELLINGS += ["%.1f" % (_k / 10)] * 20
CASE_17_SPELLINGS += ["1.0%d" % _k for _k in range(1, 10)] + ["1.01"]
CASE_17_SPELLINGS += ["1.0%02d" % _k for _k in range(11, 21)]
CASE_17_SPELLINGS += ["1.0%03d" % _k for _k in range(211, 221)]
CASE_17_SPELLINGS += ["1.0%04d" % _k for _k in range(2211, 2221)]
for _k in range(11, 21):
    CASE_17_SPELLINGS += ["%.1f" % (_k / 10)] * 16
L0_PERCENTS = (10, 20, 25, 30, 40, 50, 60, 70, 75, 80, 90)


def test_p3_fails_where_a_band_was_written_only_at_unnamed_widths():
    """Verify of 11dd0b6b, finding 1: the proof said every real cell was
    written at a named width, but a width fewer than the census floor of
    cells wrote is counted into the commonest one and never named.

    The verify of the repair, its finding 1: the CHANGELOG, P4-D404 and
    rule B3 read that exception as always failing (P3). It is needed for
    a failure but not enough: a finer width the census names elsewhere in
    the column can put a point of its grid inside the band."""
    floor = census_floor(11)
    widths = {}
    for spelling in CASE_17_SPELLINGS:
        width = len(spelling.split(".")[1])
        widths[width] = widths.get(width, 0) + 1
    assert len(CASE_17_SPELLINGS) == 400
    assert widths == {1: 360, 2: 10, 3: 10, 4: 10, 5: 10}
    named = [w for w, n in widths.items() if n >= floor]
    assert named == [1]
    cells = sorted(Fraction(v) for v in CASE_17_SPELLINGS)
    edges = sorted({_type7(cells, k) for k in L0_PERCENTS})
    assert _type7(cells, 50) == Fraction(1005, 1000)
    assert _type7(cells, 60) == Fraction(1094, 1000)
    counts = {}
    for value in cells:
        counts[value] = counts.get(value, 0) + 1
    bands = _bands(counts, edges)
    assert len(bands) == 12 and min(bands) >= 16
    low, high = Fraction(1005, 1000), Fraction(1094, 1000)
    inside = [v for v in CASE_17_SPELLINGS if low <= Fraction(v) < high]
    assert len(inside) == 40
    assert all(widths[len(v.split(".")[1])] < floor for v in inside)
    assert min(Fraction(v) for v in inside) == Fraction(101, 100)
    assert max(Fraction(v) for v in inside) == Fraction(109, 100)
    # The widest named width's grid holds no point of the band: passing
    # (P3) on it alone, the mutant, leaves a band that cannot be laid out.
    assert _points(max(named), low, high) == []
    assert _points(2, low, high) != []
    # The same values, twenty written `0.10` and the ten two-figure cells
    # written at six figures: hundredths are named, and their grid holds
    # `1.01` inside the band although each of its 40 cells was written at
    # a width the census does not name. So the exception CAN fail (P3).
    variant = [
        "0.10" if v == "0.1" else v + "0000" if len(v.split(".")[1]) == 2 else v
        for v in CASE_17_SPELLINGS
    ]
    variant_widths = {}
    for spelling in variant:
        width = len(spelling.split(".")[1])
        variant_widths[width] = variant_widths.get(width, 0) + 1
    assert variant_widths == {1: 340, 2: 20, 3: 10, 4: 10, 5: 10, 6: 10}
    variant_named = sorted(w for w, n in variant_widths.items() if n >= floor)
    assert variant_named == [1, 2]
    assert sorted(Fraction(v) for v in variant) == cells
    variant_inside = [v for v in variant if low <= Fraction(v) < high]
    assert len(variant_inside) == 40
    assert all(variant_widths[len(v.split(".")[1])] < floor for v in variant_inside)
    assert Fraction(101, 100) in _points(max(variant_named), low, high)
    preconditions = _g57a()
    assert "40 cells from `1.01` to `1.09` written ten each" in preconditions
    assert "1.0222" not in preconditions
    assert ("**(P3) holds on every description a producer writes EXCEPT where a "
            "band's or a piece's cells were all written at widths the census "
            "counts into its commonest width**") in preconditions
    assert "every real cell was written at a named width" not in preconditions
    assert "which only a hand-written description can do" not in preconditions
    assert "Such a column is made WITHOUT L0 under rule B3 and named" in preconditions
    rule = _g57h()
    assert "**RULE B3: a description that is no real column's.**" not in rule
    assert "so that (P3) fails" not in rule
    assert ("a column where a band's or a piece's cells were all written at "
            "widths the census counts into its commonest width can fail (P3), "
            "and where it does it is made without L0 under this rule and named "
            "(G5.7a; G14.3a case 17)") in rule
    case = _case(17)
    assert "40 from `1.01` to `1.09`, ten each written" in case
    assert "1.0222" not in case
    assert "ten each written at two, three, four and five figures" in case
    assert "`fraction_widths` `{\"1\": 400}`" in case
    assert "the column is made without L0 under rule B3, named in the twin's report" in case
    assert "Mutant: (P3) passed whatever the band holds" in case
    decision = _decision()
    assert "**A stated limit, owned by lane BT**, which may lift it later with a measured cost" in decision
    assert "(G14.3a case 17, expected outcome B3)" in decision
    assert "and such a column is made without L0 under rule B3 and named" not in decision
    assert ("such a column can fail (P3), and where it does it is made without "
            "L0 under rule B3 and named") in decision
    assert "40 cells from 1.01 to 1.09 written ten each" in decision
    assert "1.0222" not in decision
    change = _change()
    assert "counted on its own, is made as today" not in change
    assert ("can fail one of the checks the method makes before it places a "
            "cell; where it does, the column is made as today and named in "
            "the twin's report") in change


def test_a_label_cells_band_is_its_level_never_its_text():
    """Codex item 6: label cells have no number or clock reading, so the
    page sent every one of them to `other`."""
    interface = _g42b()
    assert "**On a label column a cell's band is its LEVEL, never its text.**" in interface
    assert "read off the cell's place in G8.4's content list" in interface
    assert "A cell G8.3 writes for a WITHHELD level has no published level and lies in `other`" in interface
    assert "the place of its level in the block's published order, counted from nought" in interface
    case = _case(13)
    assert "a label column's cells grouped by level and not by text (each level group one reading)" in case


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
    assert "the twin's report names the shortfall" in case


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
