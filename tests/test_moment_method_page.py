"""The moment page holds what it proves and the cases it is checked on (plan P4-D413).

WHY A FILE OF ITS OWN. Stage 6's moment layer is written before its
code: contract section 4.6d, the generation method's G17 and the
validation method's V13 bind lanes CHa, CHb, MPp, MPn, CHv and CHo,
which have not started, and nothing in the product reads them yet. The
disposition seal turns red on any edit of a sealed passage and is
re-sealed by whoever makes the edit, so it cannot tell a correction from
its undoing. This file can: each proof's stated objects, each safety
rule and each measured case is pinned or computed here, and each check
is red on the mutant its docstring names (skeptic 1 of 2026-10-20 found
nine of ten mutants of the first build's file surviving).

WHAT IS COMPUTED HERE, NOT READ. The page's own cases are enumerated in
whole numbers: Codex's reference case for the witness's quantifiers and
the query that would have refused it; the cell where a small own-fact
group beside an unreachable group gives a union of 3 to 6 rows; the two
cells where clause (c) refuses a small atom neither can hold whole; the
one-region cases `Q` and `S` that clause (c) read only over the points
zero on `V-` admitted; the 22-row cell where a refusal decided on the
real sums bounds a count and the drawn refusal does not; the closed form
`CF1` against enumeration, its clause (b) included; the split union
across two regions; the three two-way margins with no filling; the
correlation test; the second code on the rungs' probability scale; an
integer column's codes; the kernel's and the decode's bounds; and, from
Codex's round of 2026-10-20, the correlation targets in the twin's own
count, the weight of a constant cell, the conserved rounding of a band's
targets and the poorer option that tells tables apart.

THE CENTRAL SENTENCES. The verify of 2026-10-20 (item 2) found 19 of 20
one-line mutants of the page's central rules surviving the file; each is
pinned now, on the flattened section, by the test that names it.

WHAT IS NOT HERE. No moment code exists to run, so nothing here says a
twin meets a moment. `K-S6-08`'s enumeration and the oracle's cases
(G17.8) are where lanes CHa and CHo run the method.
"""
import itertools
import math
import pathlib
import re
from fractions import Fraction

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
CONTRACT = REPOSITORY / "docs" / "spec" / "profile-contract-v6.md"
METHOD = REPOSITORY / "docs" / "spec" / "generation-method-v1.md"
VALIDATION = REPOSITORY / "docs" / "spec" / "validation-method-v1.md"
PLAN = REPOSITORY / "docs" / "plans" / "phase-4-columns.md"
STATE = REPOSITORY / "docs" / "STATE.md"

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


def _part(start, end):
    section = _section()
    at = section.index(start)
    return section[at : section.index(end, at + len(start))]


def _g17():
    return _flat(_between(METHOD, "## G17. Between columns: the polish", "## Conformance checklist"))


def _v13():
    return _flat(_between(VALIDATION, "## V13. Between columns"))


def _decision():
    return _flat(_between(PLAN, "## Decision P4-D413", "\n## Decision"))


def _state_limit():
    return _flat(_between(STATE, "- **Relationships between columns are not carried.**", "\n- **"))


# --- the witness's predicate, computed on explicit point sets ------------


def _reach_and_zero(points, groups, small=()):
    """Clauses (a) and (b) of contract 4.6d.4: `V-` and the points zero on it."""
    free = [g for g in groups if g not in small]
    unreachable = [g for g in free if max(p[g] for p in points) < FLOOR]
    zeros = [p for p in points if all(p[g] == 0 for g in unreachable)]
    return unreachable, zeros


def _witness(points, groups, small=(), zeros_only=False):
    """Clauses (a) to (c) of contract 4.6d.4 over an explicit point list.

    `points` maps each group to its rows; `small` lists the groups of the
    one small atom of a case (each point puts all of its rows in them).
    Clause (c) asks, for every group of the atom that SOME POINT makes
    non-empty, a point zero on `V-` putting the whole atom there;
    `zeros_only` reads it as the first repair did, over the points zero
    on `V-` only (the mutant cases `Q` and `S` pass). Returns whether the
    witness holds, and `V-`."""
    unreachable, zeros = _reach_and_zero(points, groups, small)
    if not zeros:
        return False, unreachable
    asked = zeros if zeros_only else points
    for g in small:
        if any(p[g] > 0 for p in asked):
            total = max(sum(p[h] for h in small) for p in points)
            if not any(p[g] == total for p in zeros):
                return False, unreachable
    return True, unreachable


def _cell_points(rows, codes, total):
    """Every way to put `rows` rows on `codes` with code sum `total`."""
    found = []
    for counts in itertools.product(range(rows + 1), repeat=len(codes) - 1):
        if sum(counts) > rows:
            continue
        full = list(counts) + [rows - sum(counts)]
        if sum(c * n for c, n in zip(codes, full)) == total:
            found += [dict(zip(codes, full))]
    return found


def _codex_points(sum_a=100):
    """Two cells of 100 rows over codes 0 to 2, atom counts (50, 100, 50); `A`'s code sum `sum_a`, `B`'s the rest."""
    found = []
    for a0 in range(101):
        for a2 in range(101 - a0):
            a1 = 100 - a0 - a2
            if a1 + 2 * a2 != sum_a:
                continue
            b = (50 - a0, 100 - a1, 50 - a2)
            if min(b) < 0 or sum(b) != 100 or b[1] + 2 * b[2] != 200 - sum_a:
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
    """Codex's condition, as the page writes it (the verify of 2026-10-20,
    item 2: mutants X7, reach asked of EVERY point; X8, the zero asked for
    SOME group of `V-`; X9, clause (c) moving A ROW of the atom; X10,
    HiGHS's "infeasible" proving the absence; X13, the reference case
    written as refused; X20, a time limit)."""
    section = _section()
    assert "Codex's, at `f` = 11): two base cells `A` and `B` of 100 rows each" in section
    assert "It never asks whether some point puts 1 to `f - 1` rows on a group" in section
    assert 'The MUTANT is the query "refuse where some point puts 1 to 10 rows on a group"' in section
    assert "is proven only by the EXACT ROUTE" in section
    assert "its output silenced) may only reach it sooner" in section
    assert "never a time limit" in section
    assert "For every group `g` whose atom vector holds no small atom, some point has `n(g) >= f`, or `g` is in `V-`" in section
    assert "**(b) zero.** Some point has `n(g) = 0` for every `g` in `V-`;" in section
    assert "some point with 0 rows on `V-` puts all of `G`'s rows into `g`." in section
    assert 'its "infeasible", a reached budget, an error or a non-integer answer prove nothing.' in section
    assert "every group reaches at least 50 rows, `V-` is empty, and WIT holds: the option publishes." in section
    assert "its `node_limit` a whole number written in the call, never a time limit" in section


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
    alone, stay 0-able, which is Theorem 2's reading of "own facts" that
    ruling R9 confirmed (mutant: the page still asking for a ruling)."""
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
    assert "Ruling R9 (the orchestrator, 2026-10-20) confirms this reading" in section
    assert '"(d) where a column of the region has a small atom, `V-` is empty"' in section
    assert "stays a NAMED OPTION of 4.6d.10" in section
    assert "RULING NEEDED" not in section


def _two_cell_small_atom_points():
    """Clause (c)'s case: `n_zero` 3 over two cells of 22 rows on codes 0 to 2, code sums 30 and 40."""
    found = []
    for first in _cell_points(22, (0, 1, 2), 30):
        for second in _cell_points(22, (0, 1, 2), 40):
            if first[0] + second[0] == 3:
                point = {("A", v): first[v] for v in (0, 1, 2)}
                point.update({("B", v): second[v] for v in (0, 1, 2)})
                found += [point]
    return found


def test_clause_c_refuses_a_small_atom_neither_cell_can_hold_whole():
    """Skeptic 1 of 2026-10-20, item 5 (mutant M1, clause (c) dropped from
    the witness): the second cell holds 0 to 2 of the 3 zeros, its code 1
    lies in V-, the one point zero on V- splits the zeros 1 and 2, and
    the first cell's zeros lie in 1 to 3 in every point. (a) and (b) hold;
    (c) alone refuses it, and the page and its fixture say so."""
    points = _two_cell_small_atom_points()
    assert sorted((p[("A", 0)], p[("B", 0)]) for p in points) == [(1, 2), (2, 1), (3, 0)]
    groups = sorted(points[0])
    small = (("A", 0), ("B", 0))
    unreachable, zeros = _reach_and_zero(points, groups, small)
    assert unreachable == [("B", 1)]
    assert [(p[("A", 0)], p[("B", 0)]) for p in zeros] == [(1, 2)]
    holds, _ = _witness(points, groups, small=small)
    assert not holds
    first_cell_zeros = [p[("A", 0)] for p in points]
    assert (min(first_cell_zeros), max(first_cell_zeros)) == (1, 3)
    assert not _witness(points, groups, small=small, zeros_only=True)[0]
    section = _section()
    assert "**(c) small atoms.** For every small atom `G` and every group `g` holding `G`" in section
    assert "that SOME POINT makes non-empty (any point, zero on `V-` or not)" in section
    assert "**clause (c)'s case:** a small atom of 3 rows (`n_zero` 3) over two cells of 22 rows" in section


def _one_region_points(total, square=None):
    """Cases `Q` and `S`: one cell of 22 rows; `c`'s `n_zero` atom `G` of 3
    rows and its other 19 rows `H`; `e` of the same region on codes 10 to
    12 with code sum `total` (and square sum `square`). Groups are
    (atom of `c`, code of `e`)."""
    codes = (10, 11, 12)
    found = []
    for g in itertools.product(range(4), repeat=3):
        if sum(g) != 3:
            continue
        for h10 in range(20):
            for h11 in range(20 - h10):
                h = (h10, h11, 19 - h10 - h11)
                rows = [a + b for a, b in zip(g, h)]
                if sum(v * n for v, n in zip(codes, rows)) != total:
                    continue
                if square is not None and sum(v * v * n for v, n in zip(codes, rows)) != square:
                    continue
                point = {("G", v): n for v, n in zip(codes, g)}
                point.update({("H", v): n for v, n in zip(codes, h)})
                found += [point]
    return found


def test_cases_q_and_s_are_refused_by_clause_c_over_every_point():
    """The verify of 2026-10-20, item 1 (the BLOCKER of its round): inside
    ONE region, clause (c) read only over the points zero on `V-` admitted
    case `Q` (exactly 3 rows of the cell at code 11 in every point) and case
    `S` (a union of 1 to 9 rows in every point), counts no column's own
    facts publish, while `e` alone is refused at (b). Read over every
    point, (c) refuses both (mutant: `zeros_only`, the first repair's
    clause, and the page's sentence for it)."""
    small = tuple(("G", v) for v in (10, 11, 12))
    q_points = _one_region_points(223, 2263)
    assert len(q_points) == 4
    assert sorted(tuple(p[("G", v)] for v in (10, 11, 12)) for p in q_points) == [
        (0, 3, 0),
        (1, 2, 0),
        (2, 1, 0),
        (3, 0, 0),
    ]
    groups = sorted(q_points[0])
    unreachable, zeros = _reach_and_zero(q_points, groups, small)
    assert unreachable == [("H", 11), ("H", 12)]
    assert [tuple(p[("G", v)] for v in (10, 11, 12)) for p in zeros] == [(0, 3, 0)]
    assert {p[("G", 11)] + p[("H", 11)] for p in q_points} == {3}
    assert _witness(q_points, groups, small=small, zeros_only=True)[0]
    assert not _witness(q_points, groups, small=small)[0]
    s_points = _one_region_points(226)
    assert len(s_points) == 23
    unreachable, zeros = _reach_and_zero(s_points, groups, small)
    assert unreachable == [("H", 11), ("H", 12)]
    assert [(p[("G", 12)], p[("H", 10)]) for p in zeros] == [(3, 19)]
    union = [p[("G", 10)] + p[("G", 12)] + p[("H", 11)] for p in s_points]
    assert (min(union), max(union)) == (1, 9)
    assert _witness(s_points, groups, small=small, zeros_only=True)[0]
    assert not _witness(s_points, groups, small=small)[0]
    for total, square in ((223, 2263), (226, None)):
        alone = []
        for p in _one_region_points(total, square):
            alone += [{v: p[("G", v)] + p[("H", v)] for v in (10, 11, 12)}]
        assert not _witness(alone, [10, 11, 12])[0]
    section = _section()
    assert "**Case `Q`** (`spread`): `e`'s published code sum 223 and square sum 2263" in section
    assert "The cell holds EXACTLY 3 rows at code 11 in every point." in section
    assert "The union of `G` at codes 10 or 12 with `H` at code 11 holds 1 to 9 rows in every point." in section
    assert "**cases `Q` and `S`** of 4.6d.5 (c), MEASURED" in section
    assert "refused by clause (c) read over every point" in section
    assert "does not write Theorem 2 \"with no clause (c)\"" in section


def test_a_refusal_decided_on_the_real_sums_bounds_a_count_and_a_drawn_one_does_not():
    """4.6d.3, Lemma 5 and 4.6d.7 (skeptic 1 of 2026-10-20, item 9: the
    first build's fixture used 11 rows, which the mean's `2 f` rule never
    offers). On a cell of 22 rows over codes 0 to k the witness fails
    exactly when the code sum lies in 1 to 10 or in 22 k - 10 to 22 k - 1,
    so a refusal decided on the real sums tells that 1 to 10 rows lie off
    one end code; under the draw `none` stands on every sum."""
    for top in (1, 2, 3):
        codes = tuple(range(top + 1))
        refused = []
        for total in range(22 * top + 1):
            points = _cell_points(22, codes, total)
            if not _witness(points, list(codes))[0]:
                refused += [total]
                off_low = [22 - p[0] for p in points]
                off_high = [22 - p[top] for p in points]
                assert (1 <= min(off_low) and max(off_low) <= FLOOR - 1) or (
                    1 <= min(off_high) and max(off_high) <= FLOOR - 1
                ), (top, total)
        assert refused == list(range(1, 11)) + list(range(22 * top - 10, 22 * top)), top
    section = _section()
    assert "`none` is always eligible." in section
    assert "the preimage of a drawn refusal is the whole of its context's" in section
    assert "**the one-cell refusal:** a cell of 22 rows (the size rule `2 f` of `mean`) over codes 0 to `k`" in section
    assert "a cell of 11 rows over two codes" not in section


def _cf1_reach(rows, total, low, high, code):
    return (rows - FLOOR) * low + FLOOR * code <= total <= (rows - FLOOR) * high + FLOOR * code


def _cf1_holds(rows, total, low, high):
    run = [c for c in range(low, high + 1) if _cf1_reach(rows, total, low, high, c)]
    return bool(run) and rows * run[0] <= total <= rows * run[-1]


def test_the_closed_form_agrees_with_enumeration():
    """CF1: in a cell of N rows over an unbroken run of codes with sum S,
    code v can hold f rows exactly when (N - f) lo + f v <= S <= (N - f)
    hi + f v, the codes that can form an unbroken run, and (b) holds
    exactly when N u_lo <= S <= N u_hi (mutant M4, (b) dropped: it would
    publish the 22-row cell at sums 1 to 10)."""
    for rows in (22, 23, 25):
        for low, high in ((0, 2), (3, 6)):
            codes = list(range(low, high + 1))
            best = {}
            by_total = {}
            for counts in itertools.product(range(rows + 1), repeat=len(codes) - 1):
                if sum(counts) > rows:
                    continue
                full = list(counts) + [rows - sum(counts)]
                total = sum(c * n for c, n in zip(codes, full))
                bucket = by_total.setdefault(total, [])
                bucket += [dict(zip(codes, full))]
                for c, n in zip(codes, full):
                    best[(total, c)] = max(best.get((total, c), 0), n)
            for total, points in by_total.items():
                reach = [c for c in codes if best[(total, c)] >= FLOOR]
                assert reach == [c for c in codes if _cf1_reach(rows, total, low, high, c)]
                if reach:
                    assert reach == list(range(reach[0], reach[-1] + 1))
                assert _cf1_holds(rows, total, low, high) == _witness(points, codes)[0], (rows, low, total)
    without_b = [s for s in range(1, 11) if any(_cf1_reach(22, s, 0, 2, c) for c in range(3))]
    assert without_b == list(range(1, 11))
    assert not any(_cf1_holds(22, s, 0, 2) for s in range(1, 11))
    section = _section()
    assert "and (b) holds exactly when every cell has a run and `N u_lo <= S <= N u_hi`" in section
    assert "in exactly one chain family `F` (its `L0` totals node aside" in section


def test_the_correlation_test_is_r_squared_below_the_square_of_nineteen_twentieths():
    """Rule M5's first test, now on published sums (mutant M2, 361 read as
    400): `400 cov**2 < 361 var_a var_b` is r^2 < (95/100)^2, it refuses a
    pair at exactly r = 0.95 and a column paired with itself, and the
    page writes it in 4.6d.6 and S36 with the constants of 4.6d.3."""
    section = _section()
    found = re.findall(r"`(\d+) cov\*\*2 < (\d+) var_a var_b`", section)
    assert found == [("400", "361"), ("400", "361")]
    assert "`r^2 < (95/100)^2`" in section
    left, right = (int(x) for x in found[0])
    assert Fraction(right, left) == Fraction(95, 100) ** 2
    for cov, var_a, var_b in ((19, 20, 20), (380, 400, 400), (5, 5, 5), (3, 4, 3), (0, 4, 4), (2, 0, 4)):
        page = left * cov**2 < right * var_a * var_b
        exact = var_a * var_b > 0 and Fraction(cov**2, var_a * var_b) < Fraction(95, 100) ** 2
        assert page == exact, (cov, var_a, var_b)
    assert not (left * 380**2 < right * 400 * 400)
    readings = [1, 2, 4, 7, 11]
    n = len(readings)
    sum_a = sum(readings)
    sum_aa = sum(r * r for r in readings)
    cov = n * sum_aa - sum_a * sum_a
    var = n * sum_aa - sum_a**2
    assert not (left * cov**2 < right * var * var)


def test_the_draw_takes_the_eligible_options_and_defaults_to_the_last():
    """4.6d.3's draw (mutants M3, the FIRST eligible option by default, and
    M8, a uniform choice over the OFFERED options): Lemma 5 needs every
    published option to be eligible and every eligible one to have a
    chance; the default is the richest the witness admits."""
    section = _section()
    assert (
        "it takes a uniform choice among the eligible options; otherwise the LAST eligible option of the order above"
        in section
    )
    assert "the description's choice is, but for that share, the richest option the witness admits" in section
    offered = ["none", "mean S", "mean L", "mean and correlation S"]
    eligible = ["none", "mean L"]

    def draw(uniform_word, share_hit):
        pool = [o for o in offered if o in eligible]
        return pool[uniform_word % len(pool)] if share_hit else pool[-1]

    drawn = {draw(word, hit) for word in range(8) for hit in (True, False)}
    assert drawn == {"none", "mean L"}
    assert draw(0, False) == "mean L"


def test_the_size_rules_and_the_patient_refusal_are_pinned():
    """S35's size rules (mutant M6, `2 f` read as `f`) and S38 (mutant M7,
    a patient-fixed column's correlation with a repeated one allowed)."""
    section = _section()
    assert (
        "(`2 f` rows for `mean`, `spread` and `product`; `f` rows with a reading of both for `cell_slopes`)"
        in section
    )
    assert "holds 0 or at least `2 f` rows" in section
    assert "| 22 | FINE, the code's clip, the cells' size rule (`2 f`, or `f` for `cell_slopes`) |" in section
    assert "no `correlation` pairs a patient-fixed column with a repeated one." in section
    assert "is REFUSED: it is not offered while the layer is on" in section


def test_theorem_two_states_its_premises_its_one_exception_and_ruling_r11():
    """Skeptic 1 of 2026-10-20, items 1, 3 and 6; ruling R11; the verify of
    2026-10-20, items 1 to 3 (mutants: exception (i) removed; X1, SOME
    group in the split condition; X2, the proof's group no longer kept off
    `U`; the proof's (c) over zero points again; `O*(U)` read as R11's
    every-group-met reading; (S) read as one region's premise; test (iii)
    dropped). Theorem 2 holds under (R) and (S) for publishing regions, in
    the forms (A) and (B), but for one exception; a union that splits a
    small atom counts its rows by ruling R11."""
    theorem = _part("*Theorem 2.*", "*Proof of (A).*")
    assert "Under (R), (S) and the model of 4.6b.9 (b)" in theorem
    assert "let every publishing region's drawn option satisfy `WIT`" in theorem
    assert "**(A)** some table of the preimage puts at least `f` rows in `U`" in theorem
    assert "some table puts none of `U`'s rows outside `O*(U)`" in theorem
    assert "which is ruling R9's wording" in theorem
    assert "The EXCEPTION is (i): two small atoms of one publishing region, neither split by `U`" in theorem
    assert "ACROSS REGIONS" not in theorem
    section = _section()
    assert (
        "`U` SPLITS a small atom `G` of a publishing region `R` when it meets `G` without wholly holding it and "
        "every group of `R` holding `G` that SOME POINT of `Sigma(R, o_R)` makes non-empty shares a refined cell "
        "with `U`" in section
    )
    assert "`O*(U)` is `O(U)` together with the rows of every small atom `U` splits" in section
    proof = _part("*Proof of (A).*", "*Proof of (B).*")
    assert (
        "some group `g` of `R` holding `G` that some point makes non-empty shares no refined cell with `U`, "
        "and (c) gives a point with 0 rows on `V-_R` putting all of `G`'s rows into `g`" in proof
    )
    assert "The step needs (c) over EVERY point" in proof
    assert "Inside one region clause (c) refuses this" not in section
    assert "(A) then holds with no clause (c) and no exception" not in section
    assert "**(S) is a premise on the WHOLE description, not on one region:**" in section
    assert "and (iii) PREMISE (S) of 4.6d.5 is met, read on the published chain" in section
    assert "no slope the chain publishes (4.6b.6) stands in a family outside the region's nodes" in section
    assert "for every published number Lemma 6 and Theorem 2 stand PROVEN under (R)" in section
    assert "**The premise (S), slopes.** Every slope the description publishes" in section
    assert "*Remainder:* (R) and (S); where (S) fails, (d) (ii)" in section
    assert "*Remainder:* (R) only" not in section
    assert "A PUBLISHING region is one whose drawn option (below) is not `none`" in section
    assert "Lemma 6 and Theorem 2 read only PUBLISHING regions" in section
    assert "Condition (5) stays in `Sigma` where the region also publishes the per-cell slope carrier's sums" in section
    assert "adds no condition at all" not in section
    assert "brings every column its slopes read, each FINE, as a column of the region" in section
    assert "a column's `L0` band of 15 rows holding its `n_zero` 6, `U` that band, holds 9 rows" in section
    band, n_zero = 15, 6
    assert 1 <= band - n_zero <= FLOOR - 1 and band >= FLOOR


def _band_points(rows, low, high, total):
    """Every way to put `rows` rows on the codes `low` to `high` with code sum `total`."""
    codes = list(range(low, high + 1))

    def place(at, left, excess):
        if at == len(codes):
            return [{}] if left == 0 and excess == 0 else []
        found = []
        for n in range(left + 1):
            extra = n * (codes[at] - low)
            if extra > excess:
                break
            for rest in place(at + 1, left - n, excess - extra):
                found += [{codes[at]: n, **rest}]
        return found

    return place(0, rows, total - rows * low)


def test_the_split_union_across_two_regions_is_read_by_ruling_r11():
    """Skeptic 1 of 2026-10-20, item 1, and ruling R11: a small atom of 3
    rows in one region beside another region's band of 30 rows over codes
    10 to 20 with sum 320. That region publishes (codes 10 and 11 reach
    f, V- is 12 to 20 and zero-able), code 20 holds at most 2 rows, so the
    atom's rows whose code is not 20 number 1 to 3 in every table. The
    union splits the atom by the other region's atoms; ruling R11 counts
    the atom's rows among its own facts, and the GATE no longer waits
    (mutants: the GATE waiting again; the fixture reported as open)."""
    points = _band_points(30, 10, 20, 320)
    assert len(points) == 530
    reach = [v for v in range(10, 21) if max(p.get(v, 0) for p in points) >= FLOOR]
    unreachable = [v for v in range(10, 21) if v not in reach]
    assert reach == [10, 11] and unreachable == list(range(12, 21))
    zero_points = [p for p in points if all(p.get(v, 0) == 0 for v in unreachable)]
    assert [(p.get(10, 0), p.get(11, 0)) for p in zero_points] == [(10, 20)]
    rows_at_twenty = sorted({p.get(20, 0) for p in points})
    assert rows_at_twenty == [0, 1, 2]
    atom = 3
    outside = [atom - shared for at_twenty in rows_at_twenty for shared in range(min(atom, at_twenty) + 1)]
    assert (min(outside), max(outside)) == (1, 3)
    assert max(rows_at_twenty) < atom
    section = _section()
    assert "*Unions that split a small atom: the case across two regions, MEASURED, read by ruling R11" in section
    assert "`R2` has 530 points; codes 10 and 11 can hold `f` rows, `V-` is codes 12 to 20" in section
    assert "`U` splits `G` by `R2`'s atoms. Ruling R11 reads it as a count of `c`'s own facts" in section
    assert "Option (b) of the first repair, a witness clause across regions, is NOT adopted (R11)" in section
    assert "must check it on cases `Q` and `S`" in section
    assert "- **the split union across two regions**" in section
    assert "reported as accepted under ruling R11, the atom's rows read in `O*(U)`" in section
    assert "the orchestrator has chosen how exception (ii) closes" not in section
    assert "so the GATE no longer waits for a choice" in section
    assert "- **Measured and open:**" not in section
    promise = _part("**Promised, when in force**", "**Stated limits.**")
    assert "but for Theorem 2's exception (i)" in promise
    assert "it wholly holds or, by ruling R11, splits" in promise
    assert "ACROSS TWO REGIONS the guarantee R9 words does not hold" not in section
    assert "2. **\"Own facts\" as rulings R9 and R11 read them.**" in section


def test_three_two_way_margins_can_have_no_filling():
    """Why regions sharing a node are joined (skeptic 1's item 4, the lever
    this page declines, with its measurement): dealing a child against
    two regions' points and the rows' own pairing fixes three two-way
    margins, and two rows can meet the identity on two of them and the
    reverse diagonal on the third in no 2 x 2 x 2 table."""
    cells = list(itertools.product((0, 1), repeat=3))
    identity = {(0, 0): 1, (0, 1): 0, (1, 0): 0, (1, 1): 1}
    reverse = {(0, 0): 0, (0, 1): 1, (1, 0): 1, (1, 1): 0}

    def margin(table, keep):
        out = {key: 0 for key in identity}
        for cell, n in table.items():
            key = (cell[keep[0]], cell[keep[1]])
            out[key] = out[key] + n
        return out

    fillings = 0
    tables = 0
    for counts in itertools.product(range(3), repeat=8):
        if sum(counts) != 2:
            continue
        tables += 1
        table = dict(zip(cells, counts))
        if margin(table, (0, 1)) == identity and margin(table, (0, 2)) == identity:
            if margin(table, (1, 2)) == reverse:
                fillings += 1
    assert tables == 36 and fillings == 0
    section = _section()
    assert "fill no 2 x 2 x 2 table: `tests/test_moment_method_page.py` computes it" in section


def _second_code(rungs, low, high, reading):
    """4.6d.1's second code: the rungs' probability scale, `floor(256 t)`."""
    values = sorted({v for v, _ in rungs})
    spans = {v: (min(p for w, p in rungs if w == v), max(p for w, p in rungs if w == v)) for v in values}
    position = sum(spans[values[-1]]) / 2
    if reading <= values[0]:
        position = sum(spans[values[0]]) / 2
    for here, there in zip(values, values[1:]):
        if reading == here:
            position = sum(spans[here]) / 2
        elif here < reading < there:
            position = spans[here][1] + (reading - here) / (there - here) * (spans[there][0] - spans[here][1])
    return min(255, max(0, math.floor(256 * (position - low) / (high - low))))


def test_the_second_code_is_read_on_the_rungs_probability_scale():
    """The statistics review of 2026-10-20, item 4: the measured kit coded a
    skewed column by its position on the rungs' probabilities; the first
    build's equal share of the codes for each interval between rungs gave
    `p05` code 18 and `p95` 237 (its mutant), the page's code 10 and 245,
    the kit's own `1 + round(254 t)` at most one code away."""
    percents = (1, 5, 10, 20, 25, 30, 40, 50, 60, 70, 75, 80, 90, 95, 99)
    probabilities = [Fraction(p, 100) for p in percents]
    values = [Fraction(v) for v in (1, 2, 3, 5, 6, 7, 9, 12, 15, 19, 22, 26, 38, 55, 120)]
    rungs = list(zip(values, probabilities))
    low, high = probabilities[0], probabilities[-1]
    page = {int(p * 100): _second_code(rungs, low, high, v) for v, p in rungs}
    assert [page[k] for k in (5, 10, 20, 50, 95)] == [10, 23, 49, 128, 245]
    kit = {k: 1 + round(254 * float((Fraction(k, 100) - low) / (high - low))) for k in (5, 10, 20, 50, 95)}
    assert [kit[k] for k in (5, 10, 20, 50, 95)] == [11, 24, 50, 128, 245]
    assert all(abs(page[k] - kit[k]) <= 1 for k in kit)
    equal_share = {k: math.floor(Fraction(256 * j, 14)) for j, k in enumerate(percents)}
    assert (equal_share[5], equal_share[95]) == (18, 237)
    heap = [(Fraction(0), Fraction(1, 100)), (Fraction(0), Fraction(5, 100))] + rungs[2:]
    assert _second_code(heap, low, high, Fraction(0)) == math.floor(256 * Fraction(2, 100) / Fraction(98, 100))
    section = _section()
    assert (
        "So, with `lo` and `hi` at `p01` and `p99`, `p05` takes code 10, `p10` 23, `p20` 49, `p50` 128 and `p95` 245"
        in section
    )
    assert "on the rungs' PROBABILITY scale" in section
    assert "`floor(256 (j + (x - r_j) / (r_(j+1) - r_j)) / m)`" not in section


def test_an_integer_column_gives_each_reading_its_own_code():
    """Skeptic 1 of 2026-10-20, item 8: an age from 20 to 88 at p01 and p99
    takes 69 codes for 69 readings, so the published mean and std are
    exact equations on its atoms' counts; premise (R)'s judgement says so
    and `K-S6-08` holds the column as a fixture."""
    codes = [min(255, max(0, math.floor(Fraction(256 * (x - 20), 88 - 20)))) for x in range(20, 89)]
    assert len(codes) == 69 and len(set(codes)) == 69
    assert codes == [math.floor(Fraction(64 * (x - 20), 17)) if x < 88 else 255 for x in range(20, 89)]
    section = _section()
    assert "takes `floor(64 (x - 20) / 17)`, 69 readings on 69 codes" in section
    assert "an integer column of 69 readings from 20 to 88 at `p01` and `p99`" in section
    assert "an 8-bit code leaves each atom an interval of readings" not in section


def test_the_kernel_and_decode_bounds_hold_in_whole_numbers():
    """G17.1 and G17.3's bounds: every term below 2**32, every change below
    2**33, every sum inside n' 2**32 for n' below 2**30, and the decode's
    halves cast to int64 before any product, each product below 2**62
    (skeptic 1 of 2026-10-20, item 10: numba promotes uint64 times int64
    to binary64)."""
    assert 255 ** 4 < 2 ** 32
    assert 2 * 255 ** 4 < 2 ** 33
    largest_rows = 2 ** 30 - 1
    assert largest_rows * 2 ** 32 + 2 ** 33 < 2 ** 63
    assert 2 * largest_rows * 2 ** 32 < 2 ** 63
    assert (2 ** 32 - 1) * (2 ** 30 - 1) < 2 ** 62
    method = _g17()
    assert "no fused multiply-add" in method
    assert "there is no division, no square root and no library call" in method
    assert "`n'` below `2**30`" in method
    assert "are taken in `uint64` and cast to `int64` (each below `2**32`) before any product with `n'` or `len(B)`" in method
    assert "the decode multiplies `int64` by `int64` only" in method


def test_the_passes_and_the_weights_follow_the_measurements():
    """The statistics review of 2026-10-20, items 2 and 5: P = 2 scored 172
    against P = 4's 188 of 287 at 200,000 rows, so P is 4 at every size;
    a correlation's (1, 1) sum keeps the kit's weight, which `1 / (m v)`
    would cut about 2.2, 8.2 and 50 times at r = 0.5, 0.75 and 0.9."""
    method = _g17()
    assert "`P` passes: 4 at every size, PROVISIONAL" in method
    assert "`P` = 2 at 172 of 287 supported estimates against `P` = 4's 188" in method
    assert "and 2 from 1,000,000" not in method
    assert "`w = 1 / max(n v_a v_b max(1 - r**2, 1/20)**2, 1)`" in method
    ratios = []
    for r in (Fraction(1, 2), Fraction(3, 4), Fraction(9, 10)):
        ratios += [round(float((1 + r * r) / max(1 - r * r, Fraction(1, 20)) ** 2), 1)]
    assert ratios == [2.2, 8.2, 50.1]
    assert "about 2.2 times less than the kit at `r` = 0.5, 8.2 times at 0.75 and 50 times at 0.9" in method
    assert round(2 * 30 * 2_000_000 * 22.4e-6 / 60) == 45
    section = _section()
    assert "its passes `P`, 4 at every size, PROVISIONAL" in section


def test_the_validator_prints_held_or_missed_and_no_measured_number():
    """Skeptic 1 of 2026-10-20, item 2: V13.3 withheld a line on the file's
    own sums, so on a 22-row cell the withheld line stood exactly for a
    file sum in 1 to 10 or 22 k - 10 to 22 k - 1. The gate now reads the
    published sums and the file's own tables and facts only, so whether a
    line stands is the same for every file sum (mutant: the old rule)."""
    top = 2
    codes = list(range(top + 1))
    old_withheld = [s for s in range(22 * top + 1) if not _witness(_cell_points(22, codes, s), codes)[0]]
    assert old_withheld == list(range(1, 11)) + list(range(22 * top - 10, 22 * top))
    for published in (0, 5, 22, 40):
        stands = _witness(_cell_points(22, codes, published), codes)[0]
        new_withheld = [s for s in range(22 * top + 1) if not stands]
        assert new_withheld in ([], list(range(22 * top + 1)))
    lines = _v13()
    assert "The lines, every one REPORT-ONLY, never a verdict." in lines
    assert "no measured sum, product, correlation or distance stands on any line of this section" in lines
    assert "with the published sums, never with the file's own" in lines
    assert "its witness holding with the file's own sums" not in lines
    assert "`X**2 + Y**2 - T**2 <= 2 X Y`" in lines
    assert "exactly when `(S_file - S_pub)**2 <= m v`" in lines


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
    assert "No number of this section reads a derived or a computed column's readings" in section
    assert "199,023 configurations before its 280 s time cap" in section
    assert "Theorem M" not in section
    assert "checked the refusal-by-context rule this page replaces" in section


def test_the_two_carriers_are_written_with_their_checks_and_their_runs():
    """The statistics review of 2026-10-20, items 3 and 6: each figure with
    its run; the finer-band carrier at its own weight delivered nothing in
    its one measurement; the screen's ranking is measured, the chain run
    offering it is not; the refinement node is deferred with its reason."""
    section = _section()
    assert "**The finer-band carrier.** *What it publishes:* nothing outside 4.6b" in section
    assert "**The per-cell slope carrier.** *What it publishes:*" in section
    assert "*Its safe check:*" in section and "*Its remainder:*" in section
    assert "blood pressure came to 0.275 (6.6 SE, 93 per cent of the real slope)" in section
    assert "at 1.0 the same triple gave 146.5" in section
    assert "the polished chain without seeds left blood pressure 82.3 standard errors off (0.036)" in section
    assert "(rank 10 of its `fseq` set) is MEASURED" in section
    assert "It is DEFERRED, not written" in section
    assert "28 to 47 standard errors off there" not in section


def test_the_witness_yield_is_stated_as_measured():
    """Skeptic 1 of 2026-10-20, item 4, and the statistics review's item 1:
    under `cf1` the moment layer publishes almost nothing, and the page
    says so with the counts. Codex's round of 2026-10-20, item 6, and the
    verify's item 4 (mutants: the yield written as lying between 127 and
    188; the seeded chain left out): 127, 188 and 202 are reference
    measurements, the seeded chain without moments was never run, and the
    yield with the witness on is unmeasured and no bound."""
    section = _section()
    assert "join every FINE number column into ONE region: 20 columns and 38 of the 50 families" in section
    assert 'with `witness` `"cf1"` no option but `none` is eligible on that chain' in section
    assert "68 of the polish's 85 estimates at 20,000 rows" in section
    assert "since `CF1` decides none and offering it would be a no-op" in section
    assert ((371 - 303), (388 - 303), (131 - 103), (138 - 103)) == (68, 85, 28, 35)
    assert "The witness's price is unmeasured." in section
    assert "lies between" not in section
    assert "REFERENCE MEASUREMENT, not a bound on December's yield: 127 of 287" in section
    assert "the seeded chain WITHOUT moments was never run" in section
    assert "202 for the seeded chain polished" in section
    assert "The yield with the witness on is UNMEASURED and has no stated bound" in section
    assert "lane MPp measures it, or lane `A0c`'s queue if it runs first" in section
    for text in (_decision(), _state_limit()):
        assert "lies between" not in text
        assert "202" in text and "unmeasured" in text


def test_the_small_definitions_the_review_asked_for_are_written():
    """Skeptic 1 of 2026-10-20, items 11 and 13: every spread cell kind is
    an atom, and S34 reads a column whose p10 equals its p90 as not
    skewed."""
    section = _section()
    assert "Each kind of SPREAD cell the column holds in an `L0` band" in section
    assert "is ONE atom more of that band, holding no reading and no code" in section
    assert "below `procedure.skew_cut` in magnitude or its `p10` equals its `p90`" in section


def test_the_section_cites_no_identifier_in_plain_text():
    """The contract's assembly checker reads a bare design name as a
    citation; every such name stands in a code span here."""
    plain = re.sub(r"`[^`\n]*`", "", _section_raw())
    for name in ("A0a", "A0b", "A0c", "E0b", "L0", "M1", "M2", "M3", "M5", "B5", "B6", "N11", "P1", "P1b", "V12", "V13"):
        found = re.search(r"(?<![A-Za-z0-9_-])" + name + r"(?![A-Za-z0-9_])", plain)
        assert found is None, name


def test_the_plan_decision_records_the_page_and_its_repair():
    decision = _decision()
    assert "lane MPOL" in decision
    assert "RULING NEEDED" not in decision
    assert "ruling R9" in decision
    assert "`K-S6-08`" in decision
    assert "**Repair round 1 (2026-10-20).**" in decision
    assert "**Repair round 2 (2026-10-20).**" in decision
    assert "ruling R10" in decision and "ruling R11" in decision
    assert "THE MAIN FIDELITY RISK" in decision
    assert "the GATE waits for the choice" not in decision


def test_the_central_sentences_are_pinned():
    """The verify of 2026-10-20, item 2: each sentence below survived a
    one-line mutant of the page; each mutant now turns this test red (X3,
    the GATE's closing clause; X4 and X5, `CF1`'s slope and own-fact
    conditions; X6, S36's recompute; X11, the repeated column; X12, V13's
    `L0` totals; X14, S38's derived column; X15, Lemma 5's `none`; X16,
    the numpy rule; X17, zone P; X18, the order of `dJ`; X19, the
    reading-map bit)."""
    section = _section()
    for sentence in (
        "until then `procedure.classes` is empty and `moments` is `null`.",
        "an unbroken run `v_lo` to `v_hi`; and no published slope reads `c`.",
        "are INTERIOR (no rung inside them but their edges) and hold no own-fact group;",
        "and the loader recomputes the witness of every region inside the closed form `CF1`'s class and finds it holding.",
        "a repeated column takes part in no class;",
        "No entry of `codes` or `sums` names a derived column, a column a `rules` entry names",
        "If `o` is `none`, it is eligible on every table.",
        "the shifts and bitwise operators included; `bincount` takes whole-number weights only where every partial "
        "sum stays below `2**53`; no float reduction;",
        "no output of them enters the offers, the regions, the witness, the draw or any published number;",
    ):
        assert sentence in section, sentence
    lines = _v13()
    assert (
        "every `L0` total line of the region's columns reads HELD, so the file's bands are the published ones, and "
        "the region's PUBLISHED option is ELIGIBLE" in lines
    )
    method = _g17()
    assert "4. `dJ` is the sum of the `term_k` from left to right in the listed order, starting from `0.0`" in method
    assert (
        "`x` and `y` hold the same bit of the reading map (G16.1) of `c` and of each column `c` has a published "
        "`correlation` with" in method
    )


def test_strict_proof_only_is_stated():
    """Ruling R10, the owner's decision D1 of 2026-10-20 (mutants: the
    design's "rules plus enumeration" label kept; the sentence dropped)."""
    section = _section()
    assert "**Strict proof only** (ruling R10, the owner's decision of 2026-10-20)" in section
    assert 'this page has no rule-checked class and no "safe statistics" class' in section
    assert '"rules plus enumeration" for the classes `M-a`, `M-b` and `M-d` is WITHDRAWN' in section
    assert "stands until (R) is proven" not in section


def _pair_sums(pairs):
    return {(i, j): sum(a**i * b**j for a, b in pairs) for i in range(3) for j in range(3)}


def _correlation_targets(published, twin, own_count=True):
    """G17.2's four mixed targets in exact fractions (`q` is 0 where the published covariance is 0)."""
    s = _pair_sums(published)
    w = _pair_sums(twin)
    n, n_twin = s[(0, 0)], w[(0, 0)]
    count = n_twin if own_count else n
    scale = Fraction(n_twin, n) if own_count else 1
    cov = s[(1, 1)] - Fraction(s[(1, 0)] * s[(0, 1)], n)
    assert cov == 0
    found = [Fraction(w[(1, 0)] * w[(0, 1)], count)]
    for i, j in ((2, 1), (1, 2), (2, 2)):
        found += [Fraction(w[(i, 0)] * w[(0, j)], count) + scale * (s[(i, j)] - Fraction(s[(i, 0)] * s[(0, j)], n))]
    return found


def test_correlation_targets_read_each_count_on_its_own_table():
    """Codex's round of 2026-10-20, item 1 (mutant: the published `n` in
    the twin's terms): published centred pairs (0, 0), (0, 2), (2, 0) and
    (2, 2) 25 times each, the twin's 50 times each, both at r = 0. With
    each count on its own table the targets are the twin's own sums; with
    the published n they are twice as large, and the twin meeting them by
    aligning every 2 with another 2 has r = 1."""
    published = [(a, b) for a in (0, 2) for b in (0, 2) for _ in range(25)]
    twin = [(a, b) for a in (0, 2) for b in (0, 2) for _ in range(50)]
    assert _correlation_targets(published, twin) == [200, 400, 400, 800]
    assert [_pair_sums(twin)[k] for k in ((1, 1), (2, 1), (1, 2), (2, 2))] == [200, 400, 400, 800]
    assert _correlation_targets(published, twin, own_count=False) == [400, 800, 800, 1600]
    aligned = [(0, 0)] * 100 + [(2, 2)] * 100
    s = _pair_sums(aligned)
    assert [s[k] for k in ((1, 1), (2, 1), (1, 2), (2, 2))] == [400, 800, 800, 1600]
    n = s[(0, 0)]
    cov = n * s[(1, 1)] - s[(1, 0)] * s[(0, 1)]
    assert cov**2 == (n * s[(2, 0)] - s[(1, 0)] ** 2) * (n * s[(0, 2)] - s[(0, 1)] ** 2)
    method = _g17()
    assert "For `i = j = 1`, `T = S'_10 S'_01 / n' + q`" in method
    assert "`T = S'_i0 S'_0j / n' + (n' / n) (S_ij - S_i0 S_0j / n)`" in method
    assert "`T = S'_10 S'_01 / n + q`" not in method
    assert "(8) a pair whose twin overlap `n'` differs from the published `n`" in method


def _term(weight, delta, error):
    return weight * (float(delta) * (2.0 * float(error) + float(delta)))


def test_a_constant_cell_keeps_a_weight_where_an_exchange_can_move_it():
    """Codex's round of 2026-10-20, item 2 (mutant: weight 0 wherever the
    cell's own variance is 0): two `mean` cells of 22 rows in one band,
    each publishing 2442, left by the walk at 110 and 112 throughout. With
    `v` read as 1 the greedy kernel of G17.3 makes exactly 11 exchanges
    and meets both targets; with weights of 0 it makes none."""
    for weight, expected in ((1 / 22, 11), (0.0, 0)):
        first, second = [110] * 22, [112] * 22
        made = 0
        while True:
            x, y = first.index(110) if 110 in first else None, second.index(112) if 112 in second else None
            if x is None or y is None:
                break
            change = second[y] - first[x]
            d_j = 0.0
            d_j = d_j + _term(weight, change, sum(first) - 2442)
            d_j = d_j + _term(weight, -change, sum(second) - 2442)
            if not d_j < 0.0:
                break
            first[x], second[y] = second[y], first[x]
            made += 1
        assert made == expected, weight
        if expected:
            assert sum(first) == sum(second) == 2442
    method = _g17()
    assert "**Where `v` is 0** the target is weighed with `v` read as 1, unless no exchange can change its sum" in method
    assert "meet both targets after 11 exchanges" in method
    assert "a target with `v` = 0 has weight 0 and is not weighed" not in method


def _conserved(exact, total):
    """G17.2's whole targets of one conserved group: floors, then 1 more to the largest fractional parts."""
    floors = [math.floor(x) for x in exact]
    extra = int(total - sum(floors))
    order = sorted(range(len(exact)), key=lambda i: (-(exact[i] - floors[i]), i))
    for i in order[:extra]:
        floors[i] += 1
    return floors


def test_a_bands_targets_are_rounded_to_keep_its_sum():
    """Codex's round of 2026-10-20, item 8 (mutant: each target rounded
    alone, half to even): three cells of 22 rows publishing 220 each
    beside a twin band sum of 661 give exact targets of 220 1/3; rounded
    alone they total 660, while every exchange keeps 661."""
    exact = [220 + Fraction(1, 3)] * 3
    assert sum(exact) == 661
    assert [round(x) for x in exact] == [220, 220, 220]
    assert _conserved(exact, 661) == [221, 220, 220]
    for parts in ((Fraction(1, 2), Fraction(1, 2)), (Fraction(5, 7), Fraction(4, 7), Fraction(5, 7)), (Fraction(0),)):
        exact = [100 + x for x in parts]
        whole = _conserved(exact, sum(exact))
        assert sum(whole) == sum(exact) and all(abs(w - x) < 1 for w, x in zip(whole, exact))
    method = _g17()
    assert "add 1 to the `k` targets with the largest fractional parts, ties to the cell first in its table's order" in method
    assert "and rounded to a whole number, half to even. A cell of a" not in method


def _sum_key(entry):
    order = ("band", "mean", "spread", "product", "correlation")
    return (order.index(entry["class"]), entry["columns"], entry["codes"], entry.get("family"), entry.get("cell"),
            entry.get("band"), entry["powers"])


def test_every_sum_names_what_it_sums_and_omitted_regions_drew_none():
    """Codex's round of 2026-10-20, items 3 and 4 (mutants: a band sum with
    no band named, which makes two band sums one key; a correlation's sums
    with no powers; `regions` holding every offered region): every sum
    names its class, columns, codes, powers and cell or band in one
    canonical order, a duplicate is refused, and a region that drew `none`
    has no entry and is rebuilt from the offers."""
    bands = [{"class": "band", "columns": ("c",), "codes": ("L",), "powers": (1,), "band": b, "value": v}
             for b, v in ((1, 440), (0, 220))]
    assert len({_sum_key(e) for e in bands}) == 2
    assert [e["value"] for e in sorted(bands, key=_sum_key)] == [220, 440]
    without_band = [{k: v for k, v in e.items() if k != "band"} for e in bands]
    assert len({_sum_key(e) for e in without_band}) == 1
    nine = [{"class": "correlation", "columns": ("c", "d"), "codes": ("L", "L"), "powers": (i, j), "value": 0}
            for i in range(3) for j in range(3)]
    assert len({_sum_key(e) for e in nine}) == 9
    section = _section()
    assert "each `{class, columns, codes, powers, family, cell, band, value}`" in section
    assert "The `sums` of a region are listed in ONE canonical order" in section
    assert "Two sums agreeing on every field but `value` are a DUPLICATE, which a loader refuses (S35)" in section
    assert "- `regions`: one entry per PUBLISHING region (4.6d.3) only" in section
    assert "each region it builds and `regions` omits is read as one that drew `none`" in section
    assert "every class it offered must be named in `withheld` (S37)" in section
    assert "are exactly those of `regions`, in order" not in section


def _file_r(pairs):
    s = _pair_sums(pairs)
    n = s[(0, 0)]
    var_a = n * s[(2, 0)] - s[(1, 0)] ** 2
    var_b = n * s[(0, 2)] - s[(0, 1)] ** 2
    if n == 0 or var_a == 0 or var_b == 0:
        return None
    return Fraction(n * s[(1, 1)] - s[(1, 0)] * s[(0, 1)]) ** 2 / (var_a * var_b)


def test_undefined_measures_have_a_reporting_rule():
    """Codex's round of 2026-10-20, item 5 (mutant: the rule dropped, which
    leaves the file's r a division by 0): a file whose two columns share
    no row with both readings, or hold one code on one side, has no r."""
    assert _file_r([]) is None
    assert _file_r([(3, 1), (3, 2), (3, 5)]) is None
    assert _file_r([(1, 1), (2, 2), (3, 3)]) == 1
    lines = _v13()
    assert "its `r` is UNDEFINED. The private report then prints the word `undefined` for the file's `r`" in lines
    assert "marks the pair outside, and computes no `T`" in lines
    assert "A sum's distance is likewise UNDEFINED where `m v` is 0" in lines
    assert "whose `r` prints `undefined` and outside, with no division" in lines


def test_a_poorer_option_that_publishes_tells_tables_apart():
    """Codex's round of 2026-10-20, item 7 (mutant: Lemma 5's "or any
    poorer option" restored): in the reference case `A = B = (25, 50,
    25)` and one exchange of a code-0 row of `A` with a code-2 row of `B`
    keep every own fact and cell size, both are eligible for `mean`, and
    their published sums differ, so a poorer option that publishes does
    not leave its context's preimage whole."""
    for sum_a in (100, 102):
        points = _codex_points(sum_a)
        assert points and _witness(points, sorted(points[0]))[0], sum_a
    first = {("A", 0): 25, ("A", 1): 50, ("A", 2): 25, ("B", 0): 25, ("B", 1): 50, ("B", 2): 25}
    second = dict(first)
    second[("A", 0)], second[("A", 2)], second[("B", 0)], second[("B", 2)] = 24, 26, 26, 24
    for point in (first, second):
        assert [sum(point[(cell, v)] for v in (0, 1, 2)) for cell in "AB"] == [100, 100]
        assert [point[("A", v)] + point[("B", v)] for v in (0, 1, 2)] == [50, 100, 50]
    sums = [tuple(sum(v * point[(cell, v)] for v in (0, 1, 2)) for cell in "AB") for point in (first, second)]
    assert sums == [(100, 100), (102, 98)]
    assert first in _codex_points(100) and second in _codex_points(102)
    section = _section()
    assert "a region whose drawn option is `none` leaves the preimage of its context whole." in section
    assert "is `none` (or any poorer option) leaves" not in section
