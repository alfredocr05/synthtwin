"""The moment page holds what it proves and the cases it is checked on (plan P4-D413).

WHY A FILE OF ITS OWN. Stage 6's moment layer is written before its
code: contract section 4.6d, the generation method's G17 and the
validation method's V13 bind lanes CHa, CHb, MPp, MPn, CHv and CHo,
which have not started, and nothing in the product reads them yet. The
disposition seal turns red on any edit of a sealed passage and is
re-sealed by whoever makes the edit, so it cannot tell a correction from
its undoing. This file can.

WHAT IS COMPUTED HERE, NOT READ. The page's own cases are enumerated in
whole numbers: Codex's reference case for the witness's quantifiers and
the query that would have refused it; the cell where a small own-fact
group beside an unreachable group gives a union of 3 to 6 rows; the one
cell where a refusal decided on the real sums bounds a count and the
drawn refusal does not; and the closed form `CF1` against enumeration.
The rest pins wording the page's argument rests on.

WHAT IS NOT HERE. No moment code exists to run, so nothing here says a
twin meets a moment. `K-S6-08`'s enumeration and the oracle's cases
(G17.8) are where lanes CHa and CHo run the method.
"""
import itertools
import pathlib
import re

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
CONTRACT = REPOSITORY / "docs" / "spec" / "profile-contract-v6.md"
METHOD = REPOSITORY / "docs" / "spec" / "generation-method-v1.md"
VALIDATION = REPOSITORY / "docs" / "spec" / "validation-method-v1.md"
PLAN = REPOSITORY / "docs" / "plans" / "phase-4-columns.md"

FLOOR = 11


def _between(path, start, end=None):
    text = path.read_text(encoding="utf-8")
    at = text.index(start)
    if end is None:
        return text[at:]
    stop = text.find(end, at + len(start))
    return text[at:] if stop < 0 else text[at:stop]


def _flat(text):
    return " ".join(text.split())


def _section_raw():
    return _between(
        CONTRACT,
        "### 4.6d `relationships.statistical.moments`",
        "<!-- s5: the column block",
    )


def _section():
    return _flat(_section_raw())


def _g17():
    return _flat(_between(METHOD, "## G17. Between columns: the polish", "## Conformance checklist"))


def _v13():
    return _flat(_between(VALIDATION, "## V13. Between columns"))


def _decision():
    return _flat(_between(PLAN, "## Decision P4-D413"))


# --- the witness's predicate, computed on explicit point sets ------------


def _witness(points, groups, small=()):
    """Clauses (a) to (c) of contract 4.6d.4 over an explicit point list.

    `points` maps each group to its rows; `small` lists the groups of the
    one small atom of a case (each point puts all of its rows in them)."""
    free = [g for g in groups if g not in small]
    unreachable = [g for g in free if max(p[g] for p in points) < FLOOR]
    zeros = [p for p in points if all(p[g] == 0 for g in unreachable)]
    if not zeros:
        return False, unreachable
    for g in small:
        if any(p[g] > 0 for p in zeros):
            total = max(sum(p[h] for h in small) for p in zeros)
            if not any(p[g] == total for p in zeros):
                return False, unreachable
    return True, unreachable


def _codex_points():
    """Two cells of 100 rows over codes 0 to 2, code sums 100, atom counts (50, 100, 50)."""
    found = []
    for a0 in range(101):
        for a2 in range(101 - a0):
            a1 = 100 - a0 - a2
            if a1 + 2 * a2 != 100:
                continue
            b = (50 - a0, 100 - a1, 50 - a2)
            if min(b) < 0 or sum(b) != 100 or b[1] + 2 * b[2] != 100:
                continue
            found += [{("A", 0): a0, ("A", 1): a1, ("A", 2): a2, ("B", 0): b[0], ("B", 1): b[1], ("B", 2): b[2]}]
    return found


def test_the_reference_case_is_published_and_the_old_query_refuses_it():
    """Codex's condition on lane MDEP's decision, item 1: a point holding a
    group of 1 to 10 rows does not show that the published facts confine
    the group to 1 to 10. The witness publishes; the query refuses."""
    points = _codex_points()
    assert len(points) == 51
    assert sorted((p[("A", 0)], p[("A", 1)]) for p in points) == [(t, 100 - 2 * t) for t in range(51)]
    groups = sorted(points[0])
    holds, unreachable = _witness(points, groups)
    assert holds and unreachable == []
    assert min(max(p[g] for p in points) for g in groups) == 50
    the_old_query_refuses = any(1 <= p[g] <= FLOOR - 1 for p in points for g in groups)
    assert the_old_query_refuses
    at_five = [p for p in points if p[("A", 0)] == 5][0]
    assert (at_five[("A", 0)], at_five[("B", 1)]) == (5, 10)
    for size in range(1, len(groups) + 1):
        for union in itertools.combinations(groups, size):
            counts = [sum(p[g] for g in union) for p in points]
            assert min(counts) == 0 or max(counts) >= FLOOR, union


def test_the_reference_case_and_its_quantifiers_are_written():
    section = _section()
    assert "Codex's, at `f` = 11): two base cells `A` and `B` of 100 rows each" in section
    assert "It never asks whether some point puts 1 to `f - 1` rows on a group" in section
    assert 'The MUTANT is the query "refuse where some point puts 1 to 10 rows on a group"' in section
    assert "is proven only by the EXACT ROUTE" in section
    assert "its output silenced) may only reach it sooner" in section
    assert "never a time limit" in section


def _small_atom_points():
    """One cell of 30 rows: 3 at code 0 (`n_zero`), 27 over codes 1 to 4, sums 84 and 286."""
    found = []
    for c1 in range(28):
        for c2 in range(28 - c1):
            for c3 in range(28 - c1 - c2):
                c4 = 27 - c1 - c2 - c3
                if c1 + 2 * c2 + 3 * c3 + 4 * c4 != 84 or c1 + 4 * c2 + 9 * c3 + 16 * c4 != 286:
                    continue
                found += [{0: 3, 1: c1, 2: c2, 3: c3, 4: c4}]
    return found


def test_a_small_atom_beside_an_unreachable_group_bounds_their_union():
    """4.6d.4's example: (a) to (c) hold, code 1 lies in V- and the first
    point zeroes it, and the union of the zero group with code 1 holds 3
    to 6 rows in every point; the rows outside the small group, code 1
    alone, stay 0-able, which is Theorem 2's reading of "own facts"."""
    points = _small_atom_points()
    assert [tuple(p[v] for v in (1, 2, 3, 4)) for p in points] == [
        (0, 11, 2, 14),
        (1, 8, 5, 13),
        (2, 5, 8, 12),
        (3, 2, 11, 11),
    ]
    holds, unreachable = _witness(points, [0, 1, 2, 3, 4], small=(0,))
    assert holds and unreachable == [1]
    union = [p[0] + p[1] for p in points]
    assert (min(union), max(union)) == (3, 6)
    outside_the_own_group = [p[1] for p in points]
    assert min(outside_the_own_group) == 0
    section = _section()
    assert "the union of the zero group with code 1 holds 3 to 6 rows in every point" in section
    assert '"(d) where a column of the region has a small atom, `V-` is empty"' in section
    assert "RULING NEEDED" in section


def test_a_refusal_decided_on_the_real_sums_bounds_a_count_and_a_drawn_one_does_not():
    """4.6d.3 and Lemma 5: one cell of 11 rows over codes 0 and 1. The
    witness fails exactly when code 1 holds 1 to 10 rows, so a refusal
    decided on the real sums tells the reader that count; under the draw
    `none` stands on every table, and its preimage is all twelve."""
    refused = []
    for upper in range(12):
        points = [{0: 11 - upper, 1: upper}]
        holds, _ = _witness(points, [0, 1])
        if not holds:
            refused += [upper]
    assert refused == list(range(1, 11))
    assert (min(refused), max(refused)) == (1, FLOOR - 1)
    drawn_none = list(range(12))
    assert (min(drawn_none), max(drawn_none)) == (0, FLOOR)
    section = _section()
    assert "`none` is always eligible." in section
    assert "the preimage of a drawn refusal is the whole of its context's" in section


def _cf1_reach(rows, total, low, high, code):
    return (rows - FLOOR) * low + FLOOR * code <= total <= (rows - FLOOR) * high + FLOOR * code


def test_the_closed_form_agrees_with_enumeration():
    """CF1: in a cell of N rows over an unbroken run of codes with sum S,
    code v can hold f rows exactly when (N - f) lo + f v <= S <= (N - f)
    hi + f v, and the codes that can form an unbroken run."""
    for rows in (22, 23, 25):
        for low, high in ((0, 2), (3, 6)):
            codes = list(range(low, high + 1))
            best = {}
            for counts in itertools.product(range(rows + 1), repeat=len(codes) - 1):
                if sum(counts) > rows:
                    continue
                full = list(counts) + [rows - sum(counts)]
                total = sum(c * n for c, n in zip(codes, full))
                for c, n in zip(codes, full):
                    best[(total, c)] = max(best.get((total, c), 0), n)
            totals = {t for t, _ in best}
            for total in totals:
                reach = [c for c in codes if best[(total, c)] >= FLOOR]
                assert reach == [c for c in codes if _cf1_reach(rows, total, low, high, c)]
                if reach:
                    assert reach == list(range(reach[0], reach[-1] + 1))


def test_the_kernel_bounds_hold_in_whole_numbers():
    """G17.3's bounds: every term below 2**32, every change below 2**33,
    every sum inside n' 2**32 for n' below 2**30, so int64 never wraps."""
    assert 255 ** 4 < 2 ** 32
    assert 2 * 255 ** 4 < 2 ** 33
    largest_rows = 2 ** 30 - 1
    assert largest_rows * 2 ** 32 + 2 ** 33 < 2 ** 63
    assert 2 * largest_rows * 2 ** 32 < 2 ** 63
    assert (2 ** 32 - 1) * (2 ** 30 - 1) < 2 ** 63
    method = _g17()
    assert "no fused multiply-add" in method
    assert "there is no division, no square root and no library call" in method
    assert "`n'` below `2**30`" in method


def test_the_member_of_the_solvers_result_is_named():
    """Lane DEP-1's rule: the solver's result goes nowhere until a lane
    enters a member with its audit; this page names the one it needs."""
    section = _section()
    assert "The one member of `milp`'s result this page's build needs is `x`" in section
    assert "`x` being `None` proves nothing" in section


def test_each_item_of_the_design_list_is_answered():
    section = _section()
    for heading in (
        "**(a) Lemma 5 (item 3):",
        "**(b) Lemma 6 (item 2):",
        "**(c) Theorem 2 (item 1):",
        "**(d) Slopes beside moments (item 4).**",
        "**(e) Derived and computed columns (item 5).**",
        "**(f) The patient layer (item 6), while `grain` is not `null`.**",
        "**(h) The honest label (item 7), and the gate.**",
    ):
        assert heading in section, heading
    assert "*Remainders, CHECKED, NOT PROVEN*" in section
    assert "is REFUSED: it is not offered while the layer is on" in section
    assert "No number of this section reads a derived or a computed column's readings" in section
    assert "199,023 configurations before its 280 s time cap" in section


def test_the_two_carriers_are_written_with_their_checks():
    section = _section()
    assert "**The finer-band carrier.** *What it publishes:* nothing outside 4.6b" in section
    assert "**The per-cell slope carrier.** *What it publishes:*" in section
    assert "*Its safe check:*" in section and "*Its remainder:*" in section
    assert "blood pressure 0.275 against a real 0.296, 6.6 SE" in section


def test_the_section_cites_no_identifier_in_plain_text():
    """The contract's assembly checker reads a bare design name as a
    citation; every such name stands in a code span here."""
    plain = re.sub(r"`[^`\n]*`", "", _section_raw())
    for name in ("A0a", "A0b", "A0c", "E0b", "L0", "M1", "M2", "M3", "M5", "B5", "B6", "N11", "P1", "P1b", "V12", "V13"):
        found = re.search(r"(?<![A-Za-z0-9_-])" + name + r"(?![A-Za-z0-9_])", plain)
        assert found is None, name


def test_the_validator_prints_moments_as_reports_only():
    lines = _v13()
    assert "The lines, every one REPORT-ONLY, never a verdict." in lines
    assert "only where `synthtwin profile` run on that file would publish it" in lines


def test_the_plan_decision_records_the_page():
    decision = _decision()
    assert "lane MPOL" in decision
    assert "RULING NEEDED" in decision
    assert "`K-S6-08`" in decision
