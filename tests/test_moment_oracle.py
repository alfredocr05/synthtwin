"""The moments' exact route and its class against the page and against their mutants (lane CHo).

WHAT IS CHECKED. `tools/reference/moment_oracle.py` decides the witness
of contract 4.6d.4 (clauses (a) to (c)) in whole numbers, by a layered
dynamic programme over a region's groups, and names the class it always
decides within its node budget, `cho1`, by a rule read on the region's
published sizes before any search (plan P4-D421). Each case of contract
4.6d.7 is derived by hand in its docstring and recomputed here; the
mutants the lane's gate names are red: a float in a decision, a node
budget ignored, an instance outside the class decided anyway, and the
witness's own mutants (Codex's query, clause (c) dropped, clause (c)
read only over the points zero on `V-`).

WHAT IS NOT. The product's moments (lanes CHa and MPp): no description
carries `moments` yet, so the product's comparison stands in
`tests/test_chain_oracle.py`, skipped until it does.
"""
import ast
import importlib.util
import json
import math
import pathlib
import time

import pytest

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
REFERENCE = REPOSITORY / "tools" / "reference"
VECTORS = REPOSITORY / "tests" / "reference" / "chain-oracle-vectors.json"
CONTRACT = REPOSITORY / "docs" / "spec" / "profile-contract-v6.md"
PLAN = REPOSITORY / "docs" / "plans" / "phase-4-columns.md"

# The stated time a decision inside the class takes on the reference
# machine (plan P4-D421 after its repair of 2026-10-22, MEASURED at the
# widest instances the two caps admit: at most 7.0 seconds and 0.37 GB;
# 6.4 seconds on the one-cell boundary over two codes); the boundary
# cases below take under a second, and a test allows that bound before
# it calls the budget unmet.
STATED_SECONDS = 15


def _wide(groups, constraints):
    """Skeptic 1's wide instance (wave6/CHo-sk1-work/probe_width.py): `groups` groups of
    largest count 1, `constraints` constraints each reading every group with distinct
    coefficients and an open window, so every state is new and holds one partial sum for
    each constraint."""
    held = []
    for d in range(constraints):
        terms = [(g, (2 ** g) * (d + 1) + 1000003 * d) for g in range(groups)]
        held += [(terms, 0, sum(c for _, c in terms))]
    return mo.Instance(list(range(groups)), [1] * groups, held)


def _load(name):
    spec = importlib.util.spec_from_file_location("cho_m_" + name, REFERENCE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


mo = _load("moment_oracle")
oc = _load("oracle_cases")
FROZEN = json.loads(VECTORS.read_text(encoding="utf-8"))["moments"]


def _decide(spec):
    instance = mo.build_instance(spec)
    return instance, mo.decide(instance)


def _keys(instance, ks):
    return [instance.keys[k] for k in ks]


# --- the route holds no float and reads no solver ----------------------------


def test_the_route_holds_no_float_and_no_solver():
    """No float literal, no `float()`, no `math` float function, no `/`
    between whole numbers in the route: its divisions are `_ceil_div` and
    `_floor_div`, whole-number floors. No numpy, scipy or HiGHS import."""
    source = (REFERENCE / "moment_oracle.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        assert not (isinstance(node, ast.Constant) and isinstance(node.value, float)), node.value
        assert not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "float")
        assert not isinstance(node, ast.Div), "a true division in the exact route"
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""]
            assert not any(n.partition(".")[0] in ("numpy", "scipy", "highspy", "synthtwin") for n in names)


def test_a_float_in_a_decision_changes_a_verdict():
    """MUTANT (a float in a decision): one group `g`, its window 2**60 + 1
    <= 2**20 g <= 2**60 + 2**20 - 1, so in whole numbers g lies in
    [2**40 + 1, 2**40]: no point, the space is EMPTY. Read through binary64
    the two ends round to 2**40 and 2**40 + 1, a range of two values, and
    the mutant finds points: the verdict changes. The route keeps the
    whole-number floors and finds the space empty."""
    instance = mo.Instance(["g"], [2 ** 41], [([(0, 2 ** 20)], 2 ** 60 + 1, 2 ** 60 + 2 ** 20 - 1)])
    exact = mo.decide(instance)
    assert exact.inside and exact.empty and not exact.holds
    saved = (mo._ceil_div, mo._floor_div)
    try:
        mo._ceil_div = lambda a, b: math.ceil(a / b)
        mo._floor_div = lambda a, b: math.floor(a / b)
        mutant = mo.decide(mo.Instance(["g"], [2 ** 41], [([(0, 2 ** 20)], 2 ** 60 + 1, 2 ** 60 + 2 ** 20 - 1)]))
    finally:
        mo._ceil_div, mo._floor_div = saved
    assert not mutant.empty


# --- contract 4.6d.7's cases ----------------------------------------------------


def test_codex_s_reference_case_publishes_and_the_old_query_refuses_it():
    """Two cells A and B of 100 rows over codes 0, 1, 2, each code sum 100,
    the column's atom counts (50, 100, 50) fixed by its own facts. The
    points are A = (t, 100 - 2t, t), B = (50 - t, 2t, 50 - t), t from 0 to
    50: every group reaches at least 50 rows (A's code 1 at t = 0, B's at
    t = 50, each end code 50 at one end), so V- is empty and WIT holds.
    MUTANT: Codex's query, refusing where some point puts 1 to 10 rows on a
    group (t = 5 puts 5 and 10), refuses it."""
    instance, verdict = _decide(oc.spec_reference())
    assert verdict.inside and verdict.holds and verdict.unreachable == []
    assert min(verdict.largest) == 50
    assert FROZEN["reference"]["holds"] is True and FROZEN["reference_mutant_old_query"] is False
    assert oc.decide_mutant(instance, "old_query") is False


def test_a_small_atom_beside_an_unreachable_code():
    """One cell of 30 rows: 3 at code 0 (`n_zero` 3, a small atom), 27 over
    codes 1 to 4 with code sum 84 and square sum 286. The points put (0,
    11, 2, 14), (1, 8, 5, 13), (2, 5, 8, 12) or (3, 2, 11, 11) rows on codes
    1 to 4: code 1 holds at most 3, so V- = {code 1}; the first point is
    zero on it; the atom's one group holds it whole: WIT holds."""
    instance, verdict = _decide(oc.spec_small_atom())
    assert verdict.holds and _keys(instance, verdict.unreachable) == [("X", 1)]
    assert [verdict.largest[k] for k in range(5)] == [3, 3, 11, 11, 14]


def test_clause_c_refuses_a_small_atom_no_cell_holds_whole():
    """`n_zero` 3 over two cells of 22 rows on codes 0 to 2, code sums 30
    and 40. The second cell's code 1 holds at most 2 rows (V-); the one
    point zero on it splits the zeros 1 and 2, and no point zero on V- puts
    all three zeros in either cell, while some point puts a zero in each:
    (c) refuses. MUTANT: clause (c) dropped, which publishes it."""
    instance, verdict = _decide(oc.spec_clause_c())
    assert _keys(instance, verdict.unreachable) == [("B", 1)]
    assert verdict.zero and not verdict.small and not verdict.holds
    assert oc.decide_mutant(instance, "no_c") is True


def test_cases_q_and_s_are_refused_by_clause_c_over_every_point():
    """One cell of 22 rows; c's `n_zero` atom G (3 rows) and H (19 rows); e
    on codes 10 to 12 in the same region. Q: e's sums 223 and 2263 fix 19
    rows at 10 and 3 at 11, four points; S: e's sum 226, 23 points. In both
    V- is H at 11 and 12; read over every point, (c) asks a point zero on
    V- putting all of G at code 10, and none exists: refused. MUTANT: (c)
    read only over the points zero on V- (the first build), which
    publishes both."""
    for spec, label in ((oc.spec_q_or_s(223, 2263), "case_q"), (oc.spec_q_or_s(226), "case_s")):
        instance, verdict = _decide(spec)
        assert _keys(instance, verdict.unreachable) == [("X", "H", 11), ("X", "H", 12)]
        assert verdict.zero and not verdict.holds
        assert FROZEN[label + "_mutant_zero_points_only"] is True
        assert oc.decide_mutant(instance, "c_zero_points_only") is True


def test_the_one_cell_refusal_lies_off_one_end_code():
    """A cell of 22 rows over codes 0 to k: the witness fails exactly at
    code sums 1 to 10 and 22k - 10 to 22k - 1 (1 to 10 rows off an end
    code that the other 12 to 21 must hold), and holds everywhere else."""
    for top in (1, 2, 3):
        expected = list(range(1, 11)) + list(range(22 * top - 10, 22 * top))
        assert oc.one_cell_refusals(top) == expected == FROZEN["one_cell_refusals"][str(top)]


def test_the_band_of_the_split_union_across_two_regions():
    """One band of 30 rows over codes 10 to 20, code sum 320: code v holds
    11 rows exactly when 19 * 10 + 11 v <= 320 <= 19 * 20 + 11 v, that is v
    <= 11; so V- is codes 12 to 20; the zero point puts 10 rows at code 10
    and 20 at code 11 (sum 320): WIT holds (4.6d.5 (c)'s R2)."""
    instance, verdict = _decide(mo.one_cell_spec(30, 10, 20, 320))
    assert verdict.holds and [k[1] for k in _keys(instance, verdict.unreachable)] == list(range(12, 21))
    upper = [0 if k in verdict.unreachable else u for k, u in enumerate(instance.upper)]
    point = mo.point_through(instance, upper)
    assert point[:2] == [10, 20] and mo.holds_point(instance, point)


def test_exception_i_is_reported_and_never_passed():
    """Two small atoms of one region (`n_zero` 3 and a heap of 4 at code
    2) over two cells of 22 rows on codes 0 to 3, sums 30 and 33: the rows
    at code 3 number 9 in every point (63 = 8 + n1 + 3 n3 with n1 + n3 =
    37), so code 3 holds at most 5 and 7 rows in the two cells (V-) and
    no point is zero there: refused, recorded as exception (i)'s fixture."""
    instance, verdict = _decide(oc.spec_two_small_atoms())
    assert _keys(instance, verdict.unreachable) == [("A", 3), ("B", 3)]
    assert not verdict.zero and not verdict.holds
    assert FROZEN["exception_i"]["holds"] is False


def test_two_duplicate_columns_are_withheld_by_test_i():
    """Two FINE columns equal row for row: their correlation is 1, and
    test (i), `400 cov**2 < 361 var_a var_b`, fails in whole numbers."""
    sums = oc.correlation_sums([[11, 0, 0], [0, 22, 0], [0, 0, 11]])
    assert mo.correlation_allowed(sums[(0, 0)], sums[(1, 0)], sums[(0, 1)], sums[(2, 0)], sums[(0, 2)], sums[(1, 1)]) is False
    assert FROZEN["duplicate_columns_test_i"] is False


def test_cf1_and_the_exact_route_agree_on_every_group():
    """CF1 (4.6d.4's closed form) against the route on every cell of 22
    and 23 rows over runs of 1 to 6 codes and every code sum: the same
    codes reach `f` and the same verdict on (b). The frozen file holds the
    sweep at 22 and 40 rows (942 cells); the lane's run at every size from
    22 to 40 rows (8,949 cells) found no difference (plan P4-D421)."""
    assert oc.cf1_agreement([22, 23]) == {"cells": 687, "differ": []}
    assert FROZEN["cf1_against_the_oracle"] == {"cells": 942, "differ": []}


# --- the class: its rule, its boundary, its budget ---------------------------------


def test_the_class_rule_reads_sizes_before_any_search():
    """`cho1`: an instance is inside where its groups number at most
    GROUPS_MAX (50,000), no node of its region publishes a slope, the
    bound `class_bounds` reads from its sizes (each group's largest count,
    each constraint's coefficients and total) on the transitions is at
    most NODES_MAX (10,000,000), and its bound on the entries the passes
    write and read is at most ENTRIES_MAX (40,000,000). On one cell of N
    rows over w codes the boundary is N = 1,666,665 at w = 2, 1,289 at
    w = 3, 147 at w = 4 and 81 at w = 6, set by the transitions (each
    reads about 15,000,000 to 20,000,000 entries): the instance one row
    larger lies outside. A cell of 22 rows over all 256 codes is
    outside."""
    expected = {2: (1666665, 1666666), 3: (1289, 1290), 4: (147, 148), 6: (81, 82)}
    for entry in FROZEN["class_boundary"]:
        inside, outside = expected[entry["width"]]
        assert entry["inside"][0] == inside and entry["outside"][0] == outside
        assert entry["inside"][2] <= mo.NODES_MAX < entry["outside"][2]
        assert entry["inside"][3] <= mo.ENTRIES_MAX
    assert (mo.CLASS_NAME, mo.NODES_MAX, mo.ENTRIES_MAX, mo.GROUPS_MAX) == ("cho1", 10_000_000, 40_000_000, 50_000)
    wide = mo.build_instance(mo.one_cell_spec(22, 0, 255, 22 * 127))
    assert mo.class_bound(wide) > mo.NODES_MAX and not mo.decide(wide).inside


def test_a_region_publishing_a_slope_lies_outside():
    """Rule (3): a slope is point condition (5), which is not linear, so
    the space the route lists without it holds more than `Sigma(R, o)`.
    Codex's reference case, decided inside and holding, lies outside
    once a node of its region publishes a slope: no transition is made
    and the option is not eligible. MUTANT: `build_instance` leaving the
    `slopes` key unread (skeptic 1's probe_slope.py: inside, holds), red
    here. A fact the route does not read is refused, never left out in
    silence: a spec naming its slopes under another key raises."""
    plain = mo.decide(mo.build_instance(oc.spec_reference()))
    assert plain.inside and plain.holds
    spec = oc.spec_reference()
    spec["slopes"] = ["c | THE TABLE"]
    instance = mo.build_instance(spec)
    assert instance.slopes == ("c | THE TABLE",)
    verdict = mo.decide(instance)
    assert (verdict.inside, verdict.why, verdict.nodes, verdict.holds) == (False, "slope", 0, False)
    assert FROZEN["reference_with_a_slope"]["class"] == "outside" and FROZEN["reference_with_a_slope"]["why"] == "slope"
    assert mo.in_class_by_sizes([2], [[3]]) and not mo.in_class_by_sizes([2], [[3]], slopes=True)
    other = oc.spec_reference()
    other["nodes_with_slopes"] = ["c"]
    with pytest.raises(ValueError):
        mo.build_instance(other)


def test_the_groups_are_counted_before_any_is_listed():
    """Rule (1): an instance of 50,001 groups, each of largest count 0
    and no constraint, lies outside with no transition (its transitions
    bound is 3 passes of one value each, 150,003, so only the groups'
    count puts it outside;
    MUTANT: the count's test removed, which decides it inside). A region
    whose base cell holds 300 atoms of each of two columns counts 90,000
    groups from its sizes and is returned with none listed, outside."""
    many = mo.Instance(list(range(50_001)), [0] * 50_001, [])
    verdict = mo.decide(many)
    assert (verdict.inside, verdict.why, verdict.nodes) == (False, "groups", 0)
    assert mo.class_bounds(many) == (150_003, 0)
    spec = {"floor": 11, "cells": [{"name": "X", "bands": {"c": 0, "d": 0}}],
            "atoms": {"c": [oc._atom(v, 0, v) for v in range(300)], "d": [oc._atom(v, 0, v) for v in range(300)]},
            "margins": [{"cells": [0], "count": 600}], "facts": [], "sums": []}
    unlisted = mo.build_instance(spec)
    assert (unlisted.keys, unlisted.counted) == ([], 90_000)
    assert mo.decide(unlisted).why == "groups"


def test_the_budget_covers_the_passes_of_clause_c():
    """`class_bounds` counts the forward and backward pass, one pass for
    clause (b) and one for each group holding a small atom, (c)'s: on
    exception (i)'s case two small atoms each in two groups, so 3 + 4 = 7
    passes, each bounded by the first. MUTANT: the bound read as 3 passes
    (clause (c) left out), which leaves (c)'s passes outside the budget."""
    instance = mo.build_instance(oc.spec_two_small_atoms())
    one, entries = mo.pass_bounds(instance)
    assert sum(len(groups) for _, groups in instance.small_atoms) == 4
    assert mo.class_bounds(instance) == (one * 7, entries * 7)
    verdict = mo.decide(instance)
    assert verdict.inside and verdict.nodes <= verdict.bound and verdict.read <= verdict.entries


def test_the_entries_cap_bounds_the_width_of_a_state():
    """Rule (2b): the transitions alone bound neither the time nor the
    memory, since a transition writes one entry for each constraint open
    after its group. Skeptic 1's instance of 20 groups under 30 open
    constraints (6,291,450 transitions, inside rule (2); MEASURED there
    at 36.65 seconds and 1.31 GB) reads 188,743,410 entries: outside, with
    no transition. Its widest version inside both caps holds 6 open
    constraints (37,748,682 entries; MEASURED at 6.97 seconds and 0.37 GB,
    plan P4-D421) and one more lies outside (44,040,129). A narrower
    wide instance is decided within both budgets. MUTANT: the entries'
    test removed, which decides the wide instances."""
    for constraints, entries, inside in ((30, 188743410, False), (7, 44040129, False), (6, 37748682, True)):
        instance = _wide(20, constraints)
        assert mo.class_bounds(instance) == (6291450, entries)
        if not inside:
            verdict = mo.decide(instance)
            assert (verdict.inside, verdict.why, verdict.nodes) == (False, "entries", 0)
    narrow = _wide(12, 100)
    started = time.perf_counter()
    verdict = mo.decide(narrow)
    assert verdict.inside and verdict.holds and verdict.nodes <= verdict.bound and verdict.read <= verdict.entries
    assert time.perf_counter() - started < STATED_SECONDS
    with pytest.raises(mo.BudgetSpent):
        mo._solve(narrow, list(narrow.upper), [mo.NODES_MAX, 1000])


def test_a_decision_at_the_boundary_meets_its_budget_within_the_stated_time():
    """The largest one-cell instance over 4 codes the class holds (147
    rows, code sum 220): decided within NODES_MAX transitions and within
    the stated time; the next one (148 rows) is outside and decided with
    no transition at all."""
    instance = mo.build_instance(mo.one_cell_spec(147, 0, 3, 220))
    started = time.perf_counter()
    verdict = mo.decide(instance)
    elapsed = time.perf_counter() - started
    assert verdict.inside and verdict.nodes <= verdict.bound <= mo.NODES_MAX
    assert verdict.read <= verdict.entries <= mo.ENTRIES_MAX
    assert elapsed < STATED_SECONDS
    beyond = mo.decide(mo.build_instance(mo.one_cell_spec(148, 0, 3, 222)))
    assert not beyond.inside and beyond.nodes == 0


def test_an_instance_outside_the_class_is_never_decided(monkeypatch):
    """Codex's reference case under a budget of 1,000 transitions (its
    bound is 39,168): outside, so `decide` searches nothing and the option
    is not eligible, whatever a search would find. MUTANTS: the budget
    ignored (the class check read as always met and no pass counting its
    transitions), which decides the instance and publishes it; and a pass
    told to spend more than its budget holds, which stops (`BudgetSpent`)
    rather than run on."""
    instance = mo.build_instance(oc.spec_reference())
    verdict = mo.decide(instance, nodes_max=1000)
    assert not verdict.inside and verdict.nodes == 0 and not verdict.holds and verdict.why == "nodes"
    monkeypatch.setattr(mo, "class_bounds", lambda _instance: (0, 0))
    monkeypatch.setattr(mo, "_spend", lambda _box, _transitions, _entries: None)
    ignored = mo.decide(instance, nodes_max=1000)
    assert ignored.inside and ignored.holds
    monkeypatch.undo()
    with pytest.raises(mo.BudgetSpent):
        mo._solve(instance, list(instance.upper), [10, mo.ENTRIES_MAX])


def test_a_two_column_correlation_cell_lies_outside_the_class():
    """Class M-a on one cell of 33 rows, c and d each on codes 0 to 2
    centred at code 1, the nine sums of a^i b^j published. The nine
    monomials are independent on the nine code pairs, so the sums fix
    every group, but the route's bound is read before any search: the
    first eight groups each take up to 34 values, about 34**8 = 1.8e12
    transitions, so the instance is outside and the option not eligible.
    The bound reads the published sums too: 6 rows, one in each of the
    first six code pairs, bound 1,999,368, inside; 7 rows, bound
    13,063,896, outside. Under this route no M-a region holding `f` rows
    or more is inside."""
    instance, verdict = _decide(oc.spec_correlation(33, oc.correlation_sums([[4, 4, 3], [4, 3, 4], [3, 4, 4]])))
    assert not verdict.inside and verdict.bound > 10 ** 12
    six = mo.build_instance(oc.spec_correlation(6, oc.correlation_sums([[1, 1, 1], [1, 1, 1], [0, 0, 0]])))
    seven = mo.build_instance(oc.spec_correlation(7, oc.correlation_sums([[1, 1, 1], [1, 1, 1], [1, 0, 0]])))
    assert (mo.class_bounds(six), mo.class_bounds(seven)) == ((1999368, 20554335), (13063896, 135623850))
    assert mo.decide(six).inside


def test_an_exhibited_point_is_rechecked_in_whole_numbers():
    """An existence claim stands on a point exhibited and re-checked
    against every constraint as published (not the presolved form): the
    reference case's point through its layers meets all eight."""
    instance = mo.build_instance(oc.spec_reference())
    point = mo.point_through(instance)
    assert mo.holds_point(instance, point)
    assert sum(point[:3]) == 100 and point[1] + 2 * point[2] == 100
    broken = list(point)
    broken[0] += 1
    assert not mo.holds_point(instance, broken)


def test_the_presolve_keeps_every_point():
    """Codes 100 to 105 over 40 rows read as codes 0 to 5 after the shift by
    the cell's count: the same verdict and the same bound as the cell over
    0 to 5 (the bound reads the presolved form, so the class does not
    depend on where a band's codes lie)."""
    low = mo.build_instance(mo.one_cell_spec(40, 0, 5, 100))
    high = mo.build_instance(mo.one_cell_spec(40, 100, 105, 4100))
    assert mo.class_bound(low) == mo.class_bound(high)
    a, b = mo.decide(low), mo.decide(high)
    assert (a.holds, a.unreachable) == (b.holds, b.unreachable)


# --- the page states the decision ------------------------------------------------------


def test_the_settings_name_the_class_and_the_decision_records_it():
    """Contract 4.6d.10's `witness` setting, amended by a dated sentence,
    names `"cho1"`; plan P4-D421 records the class, its rule, its measured
    times and its reach."""
    contract = " ".join(CONTRACT.read_text(encoding="utf-8").split())
    plan = " ".join(PLAN.read_text(encoding="utf-8").split())
    assert '`witness`: `"cf1"` until lane CHo\'s decision names the oracle\'s class.' in contract
    assert "AMENDED 2026-10-21 (plan P4-D421)" in contract
    assert '`witness` is `"cho1"`' in contract
    assert "## Decision P4-D421" in plan
    decision = plan[plan.index("## Decision P4-D421"):]
    for words in ("NODES_MAX", "10,000,000", "50,000", "0 of lane `A0b`'s 287 analysis results", "8,949"):
        assert words in decision, words
