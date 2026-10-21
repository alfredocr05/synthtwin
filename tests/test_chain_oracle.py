"""The chain's oracle against the page and against its mutants (lane CHo, plan P4-D421).

WHAT IS CHECKED. `tools/reference/chain_oracle.py` reads contract 4.6b
and method G16 from the pages alone, in Python integers and exact
fractions, and `tests/reference/chain-oracle-vectors.json` freezes its
cases (the design's list, BC-ARCH 10.3). Each test here derives its
expected values by hand in its docstring, recomputes them from the
oracle, compares them with the frozen file, and shows the mutant its
docstring names moving the result: a float in a decision, a node budget
ignored (the moments' file), RULE W1's part C not firing, a literal 11
for the floor, the walk's two orders, the held page's fitting.

WHAT IS NOT. Lane CHa's and lane CHb's code: the last test runs the
product against the oracle and is skipped while the product publishes
no `relationships.statistical`.
"""
import ast
import importlib.util
import json
import pathlib
import sys
from fractions import Fraction

import pytest

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
REFERENCE = REPOSITORY / "tools" / "reference"
VECTORS = REPOSITORY / "tests" / "reference" / "chain-oracle-vectors.json"
ORACLE_FILES = ("chain_oracle.py", "moment_oracle.py", "oracle_cases.py", "make_chain_oracle_vectors.py")


def _load(name):
    spec = importlib.util.spec_from_file_location("cho_" + name, REFERENCE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


co = _load("chain_oracle")
oc = _load("oracle_cases")
FROZEN = json.loads(VECTORS.read_text(encoding="utf-8"))


def _json(value):
    return json.loads(json.dumps(value))


# --- what the oracle may and may not hold --------------------------------


def _float_uses(source):
    """Every float literal, `float(...)` call and `math` float function in a source text."""
    found = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Constant) and isinstance(node.value, float):
            found += ["literal %r" % node.value]
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "float":
            found += ["float()"]
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "math":
            if node.attr in ("exp", "log", "log2", "log10", "sqrt", "pow", "fsum", "ldexp", "frexp", "expm1", "log1p"):
                found += ["math.%s" % node.attr]
    return found


def test_the_oracle_reads_no_code_it_checks_and_decides_nothing_in_a_float():
    """The oracle imports neither synthtwin, numpy, pandas nor a solver,
    and holds no float literal, no `float()` call and no `math` float
    function: every decision is made in integers or exact fractions, and
    binary64 is emulated by rounding exact fractions (`b64`). MUTANT: a
    float in a decision, the libm exponential put where the stated
    exponential stands, is caught by the same scan."""
    for name in ORACLE_FILES:
        source = (REFERENCE / name).read_text(encoding="utf-8")
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Import):
                roots = [a.name.partition(".")[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                roots = [(node.module or "").partition(".")[0]]
            else:
                continue
            for root in roots:
                assert root not in ("synthtwin", "numpy", "pandas", "scipy", "highspy", "pathlib"), (name, root)
        assert _float_uses(source) == [], (name, _float_uses(source))
    mutant = (REFERENCE / "chain_oracle.py").read_text(encoding="utf-8").replace(
        "    y = b64(gap)\n", "    y = b64(gap)\n    return math.exp(-float(gap))\n"
    )
    assert sorted(_float_uses(mutant)) == ["float()", "math.exp"]


def test_the_frozen_vectors_rebuild_exactly_and_imports_are_named():
    """Every chain case rebuilds to the frozen file's values (the
    provenance check rebuilds the whole file byte for byte under its
    guard; this is the same claim held in the suite)."""
    assert FROZEN["generated_by"] == "tools/reference/make_chain_oracle_vectors.py"
    assert FROZEN["never_imports"] == ["synthtwin", "numpy", "pandas"]
    assert FROZEN["test_key"] == bytes(range(32)).hex()
    assert _json(oc.chain_cases()) == FROZEN["chain"]


# --- binary64 and RULE W5 (contract 4.6b.4) ---------------------------------


def test_binary64_rounding_is_emulated_to_the_last_bit():
    """`b64` rounds an exact fraction to the nearest binary64, ties to the
    even significand: 1 + 2**-53 lies half way between 1 and 1 + 2**-52
    and goes to 1 (even); 1 + 3 * 2**-53 goes up to 1 + 2**-51; 2**-1075
    is half the least subnormal and goes to 0; 3 * 2**-1076 goes to
    2**-1074. These are the cases a careless rounding gets wrong."""
    two = Fraction(2)
    assert co.b64(1 + two ** -53) == 1
    assert co.b64(1 + 3 * two ** -53) == 1 + two ** -51
    assert co.b64(two ** -1075) == 0
    assert co.b64(3 * two ** -1076) == two ** -1074
    assert co.b64_hex(Fraction(1, 2)) == "0x1.0000000000000p-1"
    assert co.from_hex("0x1.71547652b82fep0") == co.LOG2E
    with pytest.raises(OverflowError):
        co.b64(two ** 1024)


def test_the_stated_exponential_is_the_page_s_and_not_libm_s():
    """E(0): y = 0, t = 0, j = 0, r = 0, p(0) = c0 = 1, so E = 1 exactly.
    E(745): t = 745 * LOG2E is about 1074.82, j = 1074, p(r) about
    2**-0.82 = 0.566, and ldexp(0.566, -1074) rounds to one least
    subnormal, 2**-1074. E(2500): j is about 3606 > 1074, so exactly 0.
    MUTANT (a float in a decision): the libm exponential differs from the
    stated one in the last bits at gaps 1/2, 2 and 10 (0x1.368b2fc6f960ap-1
    against the stated 0x1.368b2fc6f9604p-1 at 1/2), so a weight read
    from it would move the frozen vectors."""
    case = FROZEN["chain"]["stated_exponential"]
    assert case["values"][0] == "0x1.0000000000000p+0"
    assert co.stated_exponential(745) == Fraction(2) ** -1074
    assert case["values"][5] == "0x0.0000000000001p-1022"
    assert case["values"][6] == "0x0.0p+0"
    libm_half = co.from_hex("0x1.368b2fc6f960ap-1")
    assert co.stated_exponential(Fraction(1, 2)) != libm_half
    assert case["values"][1] == "0x1.368b2fc6f9604p-1"
    for gap in (0, Fraction(1, 2), 1, 2, 10):
        value = co.stated_exponential(gap)
        assert 0 < value <= 1 and co.b64(value) == value


def test_the_word_and_the_choice_on_fixed_words():
    """THE UNIFORM SHARE: the word 00000000 01020304 | 80000000 00000000
    has U1 = 0x01020304, whose top 30 bits are clear (U1 >> 34 = 0), so
    the option at (U2 * m) >> 64 = (2**63 * 4) >> 64 = 2 is placed,
    whatever its weight. THE WEIGHTED CHOICE on the test key's word for
    ["visits", "place", 3, ["age", "sbp", "stage"]] over raised scores
    (0, 41/2, 20, 3) at tau 2: weights E((41/2 - v) / 2), the option
    scoring 41/2 has weight exactly 1, and the frozen word places option
    2. MUTANT: another key draws another word. The fingerprint is keyed
    under its own domain, so it never equals a word."""
    case = FROZEN["chain"]["stated_exponential"]
    word = bytes.fromhex(case["uniform_word"])
    assert int.from_bytes(word[:8], "big") >> 34 == 0
    place, how, _ = co.choose(word, [Fraction(0), Fraction(41, 2), Fraction(20), Fraction(3)], 2)
    assert (place, how) == (2, "uniform") == (case["uniform"]["place"], case["uniform"]["how"])
    key = oc.TEST_KEY
    drawn = co.word(key, "visits", "place", 3, ["age", "sbp", "stage"])
    assert drawn.hex() == case["word"]
    assert case["weighted"]["weights"][1] == "0x1.0000000000000p+0"
    assert case["weighted"]["place"] == co.choose(drawn, [Fraction(0), Fraction(41, 2), Fraction(20), Fraction(3)], 2)[0]
    other = co.word(bytes(32), "visits", "place", 3, ["age", "sbp", "stage"])
    assert other != drawn
    assert co.fingerprint(key).hex() == case["fingerprint"]
    assert co.fingerprint(key) not in (drawn[:8], drawn[8:])


# --- the ladder (contract 4.6b.2) --------------------------------------------


def test_one_column_s_ladder_through_the_l0_merge():
    """207 tabled rows: 7 absent, readings in runs below p10 (20), [p10,
    p20) (20), [p20, p25) (none), [p25, p30) (10), [p30, p40) (25), then
    20, 20, 20, 12, 13, 20 and 20. (1) [p20, p25) holds no row and is
    dropped, so p25 stops being an edge and the band reads [p20, p30):
    10 rows. (2) `missing` (7 rows) is the first band holding 1 to 10 rows;
    its one neighbour is the lowest value band, so they join: an ORDERED
    band of 27. (3) [p20, p30) (10 rows) joins the neighbour holding fewer
    rows, [p10, p20) (20) rather than [p30, p40) (25): a band of 30. The
    totals are 27, 30, 25, 20, 20, 20, 12, 13, 20, 20. L1's edges p25, p50,
    p75, p90 lose p25 (no longer an L0 edge): bands {0..3}, {4, 5, 6},
    {7, 8}, {9}; L2: {0..3}, {4..9}. The taken-in sub-bands sit in L0
    bands 0 and 1 (RULE W1's own-fact groups). MUTANT: joining the
    LARGER neighbour puts the ten rows with [p30, p40), totals 27, 20, 35."""
    case = FROZEN["chain"]["ladder_merge"]
    assert case["totals"] == [27, 30, 25, 20, 20, 20, 12, 13, 20, 20]
    assert case["l1"] == [[0, 1, 2, 3], [4, 5, 6], [7, 8], [9]]
    assert case["l2"] == [[0, 1, 2, 3], [4, 5, 6, 7, 8, 9]]
    assert case["taken_in"] == [0, 1]
    assert case["l0"][0] == ["missing", ["range", None, "p10"]]
    assert case["l0"][1] == [["range", "p10", "p20"], ["range", "p20", "p25"], ["range", "p25", "p30"]]
    cells, rungs = oc.ladder_merge_cells()
    lad = co.ladder_of("stay", "count", cells, rungs=rungs)
    assert lad.totals == case["totals"] and sum(lad.totals) == 207
    assert all(t == 0 or t >= 11 for t in lad.totals)
    assert lad.ordered[0] and lad.codes(2)[:7] == [0] * 7


# --- W3, NE and the floor (contract 4.6b.3) -----------------------------------


def test_a_floor_36_family_is_read_at_the_person_s_floor():
    """The held page's Codex table [[20, 60, 60], [60, 60, 60], [60, 60,
    60]] (A by B, 500 rows; totals 140, 180, 180 each) at
    `small_cell_floor` 36. W3: 140 >= 36 * 3 = 108 for each member, so
    both start and stay at L0; NE: the least expected cell is 140 * 140 /
    500 = 39.2 >= 37. Offered at (L0, L0) and every coarser combination.
    The floor refuses every option keeping the cell of 20 (A and B at L0
    or L1, where L1 keeps all three levels): 4 of 9. A or B at L2 (its
    commonest level, a2 or b2, against the rest) leaves cells 60, 80, 120
    and 200, all at least 36. MUTANT: the literal 11, which lets all 9
    through."""
    case = FROZEN["chain"]["floor36"]
    assert case["offered"] == [0, 0]
    refused = [o["levels"] for o in case["options"] if not o["eligible"]]
    assert refused == [[0, 0], [0, 1], [1, 0], [1, 1]]
    assert all(o["why"] == "floor" for o in case["options"] if not o["eligible"])
    assert _json(oc.case_floor36()) == case
    mutant = FROZEN["chain"]["floor36_mutant_literal_11"]
    assert all(o["eligible"] for o in mutant["options"]) and len(mutant["options"]) == 9


def test_the_second_red_team_s_p2_is_not_offered():
    """X holds 11 and 989 rows, Y 500 and 500 (1,000 rows). W3: X fails,
    its smaller total 11 being below 11 * 2 = 22, and a binary column has
    one set of bands at every level, so going coarser never helps: the
    pair is not offered and the root step offers "no family" alone.
    MUTANT: W3 skipped would offer the pair (its table then leaves at most
    11 rows in X's small band, cells of 1 to 10 among them)."""
    case = FROZEN["chain"]["p2"]
    assert case == {"offered": None, "options": 1}
    lads = {"X": co.ladder_of("X", "binary", [("level", "x1")] * 11 + [("level", "x2")] * 989,
                              levels=[("x1", 11), ("x2", 989)], position=0),
            "Y": co.ladder_of("Y", "binary", [("level", "y1")] * 500 + [("level", "y2")] * 500,
                              levels=[("y1", 500), ("y2", 500)], position=1)}
    assert co.offered_levels(lads, "Y", [("X", 0)], None, 1000) is None
    assert min(lads["X"].band_totals(2)) < 11 * len(lads["Y"].bands(2))


# --- RULE W1 (contract 4.6b.3, 4.6b.9 (c)) -------------------------------------


def test_w1_fires_on_part_c_and_the_old_clause_does_not():
    """Part C on 500 rows: D's `n_zero` 6 lies in D's lowest L0 band of 50
    rows, and every row of that band reads post-op 0, so in `P | D` at
    D's L0 the band's row is (50, 0): "day 0 AND post-op 0" would be 6 in
    every table. W1 reads the band of D's chain level holding the group
    and asks for two bands of P's coarsest level beside it: one, so every
    option with D at L0 is refused (3 of 9). With D at L1 the band below
    p25 joins L0 bands 0 to 2, whose rows read both post-op levels: those
    options are eligible. MUTANT: the clause the red team found vacuous
    ("until the band holds at least f rows"), which every band meets, so
    the L0 options pass."""
    case = FROZEN["chain"]["part_c"]
    assert case["row_of_the_group"] == [50, 0]
    by_level = {tuple(o["levels"]): (o["eligible"], o["why"]) for o in case["options"]}
    assert all(by_level[(0, p)] == (False, "W1") for p in (0, 1, 2))
    assert all(by_level[(1, p)] == (True, "eligible") for p in (0, 1, 2))
    assert _json(oc.case_part_c()) == case
    mutant = FROZEN["chain"]["part_c_mutant_old_clause"]
    assert all(o["eligible"] for o in mutant["options"])
    lads, n = oc.part_c_lads()
    chain = [co.Family("D", 0, [], None, [lads["D"].band_totals(0)]),
             co.Family("P", 0, [("D", 0)], 0, co.table_of(lads, "P", 0, [("D", 0)]))]
    holds, failures = co.w1_holds(chain, lads, [("D", 0)])
    assert not holds and failures == [("D", 0, "P", [0])]


def test_w1_is_read_at_the_other_column_s_coarsest_level():
    """4.6b.9 (c)'s first case: a parent cut at L0 whose two non-zero
    cells beside the group's band both lie below its median. Here the
    group's band of A (a label column's level a1, holding a group of 6)
    reads B only in B's two lowest L0 bands, both below p50: two non-zero
    cells, so the design's own clause passes, but both lie in one band of
    B's L2, so W1 refuses."""
    rows = []
    rows += [("a1", 1)] * 30 + [("a1", 2)] * 30
    for b in range(1, 13):
        rows += [("a2", b)] * 25
    a_cells = [("level", a) for a, _ in rows]
    b_cells = [("value", Fraction(b)) for _, b in rows]
    lads = {"A": co.ladder_of("A", "categorical", a_cells, levels=[("a1", 60), ("a2", 300)], position=0),
            "B": co.ladder_of("B", "count", b_cells, rungs=oc._number_rungs([2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]),
                              position=1)}
    chain = [co.Family("A", 0, [], None, [lads["A"].band_totals(0)]),
             co.Family("B", 0, [("A", 0)], 0, co.table_of(lads, "B", 0, [("A", 0)]))]
    row = chain[1].table[0]
    assert sum(1 for c in row if c) == 2
    holds, failures = co.w1_holds(chain, lads, [("A", 0)])
    assert not holds and failures[0][:3] == ("A", 0, "B")


# --- the moved target (method G16.6) ------------------------------------------------


def test_the_moved_target_on_codex_s_case_names_its_units():
    """Published [[50, 0], [0, 50]] against row totals [60, 40] and column
    totals [40, 60]: the tables meeting both are [[a, 60 - a], [40 - a,
    a]] for a from 0 to 40, with (60 - a) + (40 - a) = 100 - 2a units in
    the published noughts, fewest at a = 40: [[40, 20], [0, 40]], its 20
    units in cell (0, 1). MUTANT: the held page's fitting and rounding,
    which keeps the noughts and so misses the row totals ([[40, 0], [0,
    60]])."""
    case = FROZEN["chain"]["transport"]
    assert case["moved"] == [[40, 20], [0, 40]]
    assert case["units_in_noughts"] == [[0, 1, 20]]
    assert co.moved_target([[50, 0], [0, 50]], [60, 40], [40, 60]) == ([[40, 20], [0, 40]], [(0, 1, 20)])
    mutant = FROZEN["chain"]["transport_mutant_held_page"]
    assert [sum(r) for r in mutant] != [60, 40]
    assert co.needs_move([[50, 0], [0, 50]], [60, 40], [40, 60])


# --- the walk (method G16.2) ---------------------------------------------------------


def test_the_walk_on_forty_rows_meets_every_table():
    """X (1 to 40), Y and Z (11 absent) at a floor of one: X alone at L1,
    Y | X at L1, Z | X, Y at L2 with pooled slopes 0.4123 and 0.2875 and
    sigma 13.5 published. Every family's table is met cell for cell. The
    first row's hidden score: its three words' twelve 16-bit pieces are
    45873, 7653, 39829, 21507, 40908, 49335, 60596, 10208, 34942, 2811,
    57422 and 7961, summing to 379045, so z = (379045 - 393210) / 65536 =
    -14165/65536, exact. MUTANTS: rows sorted by row number instead of L
    (39, 39 and 40 rows of X, Y and Z change cells), and the spread band
    placed after the ordered ones (37 rows of Z change cells): both move
    the frozen cells while the tables stay met."""
    case = FROZEN["chain"]["walk40"]
    assert case["met"] == [True, True, True]
    words = FROZEN["chain"]["walk40_words"]["words"]
    first = [int(w, 16) for w in words[0]]
    assert co.hidden_score(first) == Fraction(-14165, 65536)
    assert _json(oc.case_walk40()) == case
    for name, moved in (("walk40_mutant_row_order", {"X": 39, "Y": 39, "Z": 40}),
                        ("walk40_mutant_spread_after", {"X": 0, "Y": 0, "Z": 37})):
        mutant = FROZEN["chain"][name]
        assert mutant["met"] == [True, True, True]
        changed = {c: sum(1 for a, b in zip(case["index"][c], mutant["index"][c]) if a != b) for c in "XYZ"}
        assert changed == moved, name
    _, chain, _, _, slopes, _ = oc.walk40_setup()
    assert co.published_decimal(slopes[2][0][0][1]) == co.b64(Fraction(4123, 10000))


def test_an_empty_parent_cell_and_a_child_always_absent():
    """C | A, B: no row holds (a2, b1), so its table row is [0, 0, 0] and
    the walk deals nothing there; in (a2, b2) the child is always absent,
    its row [15, 0, 0], so only the spread placement runs and all 15 rows
    take `missing`."""
    case = FROZEN["chain"]["empty_and_absent"]
    assert case["table"][2] == [0, 0, 0] and case["table"][3] == [15, 0, 0]
    assert case["met"] and case["rows_in_the_empty_cell"] == 0 and case["child_present_in_the_absent_cell"] == 0
    assert _json(oc.case_empty_and_absent()) == case


def test_a_label_child_is_dealt_by_its_hidden_score():
    """C (levels x, y) under A (north, south), table [[12, 13], [14, 11]]:
    a label child takes L = z, and inside each parent cell its rows,
    sorted by z, take x then y. So in the north cell the 12 rows of least
    hidden score hold x: checked on the dealt rows."""
    case = FROZEN["chain"]["label_child"]
    assert case["met"] and case["table"] == [[12, 13], [14, 11]]
    n = len(case["rows"])
    words = oc._words_for(0x1ABE1, 2, n)[1]
    north = sorted([r for r in range(n) if case["rows"][r][0] == "north"], key=lambda r: (co.hidden_score(words[r]), r))
    assert [case["rows"][r][1] for r in north] == ["x"] * 12 + ["y"] * 13
    assert _json(oc.case_label_child()) == case


def test_a_rule_word_is_met_by_the_walk():
    """The family [[30, 0], [12, 18]]: admission rows never read `post`, a
    nought between bands of 30 and 18 rows (both at least f), a rule word.
    The walk deals no row there. MUTANT: the cell's target taken as one
    (and its neighbours moved to keep the totals), which breaks the word
    on 1 row."""
    assert FROZEN["chain"]["rule_word"]["rows_breaking_the_word"] == 0
    assert FROZEN["chain"]["rule_word"]["dealt"] == [[30, 0], [12, 18]]
    assert FROZEN["chain"]["rule_word_mutant_as_one"]["rows_breaking_the_word"] == 1


def test_an_order_rule_is_written_as_a_plus_d():
    """B = A + D where both hold a reading: 3 + 1 = 4, 5 + 0 = 5, 8 + 2 =
    10, ..., absent where A or D is absent (rows 11 and 12), so B >= A on
    every row (D >= 0). MUTANT: B dealt as a column of its own (its
    readings rotated), which breaks A <= B on 3 rows."""
    case = FROZEN["chain"]["order_rule"]
    assert case["b"][:3] == ["4", "5", "10"] and case["b"][10:] == [None, None]
    assert case["rows_breaking_a_le_b"] == 0
    assert FROZEN["chain"]["order_rule_mutant_own_column"]["rows_breaking_a_le_b"] == 3


def test_a_derived_family_keeps_its_structural_zeros():
    """{D | A}: A's `missing` band (11 rows) holds every row in D's
    `missing` band and 0 in every value band, a structural zero published
    as cells: [[11, 0, 0], [0, 20, 11], [0, 12, 22]]. The walk deals D under
    A, so no reading of D stands beside an absent A. MUTANT: D dealt by
    its band totals alone (the first draft), which puts 9 readings of D
    beside an absent A."""
    case = FROZEN["chain"]["derived_family"]
    assert case["table"] == [[11, 0, 0], [0, 20, 11], [0, 12, 22]]
    assert case["readings_of_d_beside_an_absent_a"] == 0
    assert FROZEN["chain"]["derived_family_mutant_totals_alone"]["readings_of_d_beside_an_absent_a"] == 9


# --- a pair's implied table, the score, a whole search ----------------------------------


def test_the_implied_pair_and_its_dealing_spread():
    """A, B | A = [[30, 10], [10, 30]], C | B = [[25, 15], [5, 35]] (80 rows,
    B's totals 40 and 40): the implied table of A and C is sum over b of
    AB[a][b] * BC[b][c] / 40: 750/40 + 50/40 = 20, 450/40 + 350/40 = 20,
    250/40 + 150/40 = 10, 150/40 + 1050/40 = 30. Shares 1/4, 1/4, 1/8, 3/8;
    radicands p (1 - p) / 80: 3/1280, 3/1280, 7/5120, 3/1024. The spread
    s = (2 sqrt(3/1280) + sqrt(7/5120) + sqrt(3/1024)) / 2, about 0.0940,
    is enclosed in whole multiples of 2**-60."""
    case = FROZEN["chain"]["implied_pair"]
    assert case["implied"] == [["20", "20"], ["10", "30"]]
    assert case["radicands"] == ["3/1280", "3/1280", "7/5120", "3/1024"]
    low, high = Fraction(case["spread_low"]), Fraction(case["spread_high"])
    assert low <= high and high - low < Fraction(1, 2 ** 57)
    assert Fraction(939, 10000) < low < Fraction(940, 10000)


def test_the_score_is_an_exact_fraction():
    """[[30, 10, 0], [10, 25, 5]]: rows 40 and 40, columns 40, 35 and 5,
    80 rows; expected 20, 17.5, 2.5 in each row; X2 = 2 (100/20 + 56.25/17.5
    + 6.25/2.5) = 150/7; df = (2 - 1)(3 - 1) = 2; u = 136/7. MUTANT: the
    score in floats is 19.428571428571427, not the fraction."""
    assert FROZEN["chain"]["score"]["u"] == "136/7"
    assert co.score([[30, 10, 0], [10, 25, 5]]) == Fraction(136, 7)


def test_a_whole_search_for_the_test_key():
    """Three label columns on 400 rows: the root step offers "no family"
    and every pair at the levels W3, NE and their variants allow; 28 are
    eligible, and the test key's word places A at L1 with C at L2 under it;
    the next step places B under A and C. Every placed family is complete,
    sums to 400 and meets the floor. MUTANT: another key draws other
    words."""
    case = FROZEN["chain"]["search"]
    assert [s["index"] for s in case["steps"]] == [0, 1]
    assert case["steps"][0]["eligible"] == 28
    assert case["steps"][0]["placed"] == {"kind": "root", "parent": "A", "child": "C", "levels": {"A": 1, "C": 2}}
    for family in case["chain"]:
        cells = [c for row in family["table"] for c in row]
        assert sum(cells) == 400 and all(c == 0 or c >= 11 for c in cells)
    lads, n = oc.search_lads()
    other = co.word(bytes(32), "trial", "place", 0, ["A", "B", "C"]).hex()
    assert other != case["steps"][0]["word"]


# --- the product against the oracle -------------------------------------------------------


def test_the_product_s_chain_against_the_oracle(tmp_path, monkeypatch):
    """Runs `synthtwin profile` on a seeded neutral table and compares what
    it publishes in `relationships.statistical` with the oracle: each
    `ladder` entry's totals with the oracle's L0 totals from the table's
    cells at the published rungs, and each `chain[].table` with the
    oracle's complete table at the published levels (S25). SKIPPED while
    the product publishes no `relationships.statistical` (contract
    4.6b: lane CHa's `ladder`, `chain`, `procedure`, `rules`, `words`,
    `not_carried`, `ineligible`, `withheld`; 4.6d: `moments.codes` and
    `moments.regions`), which invariant S12 holds `null` until the
    landing that ships stage 6."""
    sys.path.insert(0, str(REPOSITORY / "src"))
    from synthtwin.cli import main

    for name in ("HOME", "APPDATA", "LOCALAPPDATA", "XDG_DATA_HOME"):
        monkeypatch.setenv(name, str(tmp_path / "home"))
    rows = ["age,ward,score"]
    for r in range(600):
        rows += ["%d,%s,%d" % (20 + (r * 7) % 61, "w%d" % (r % 3), (r * 13) % 97)]
    table = tmp_path / "trial.csv"
    table.write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
    assert main(["profile", str(table)]) == 0
    described = json.loads((tmp_path / "trial-profile.json").read_text(encoding="utf-8"))
    statistical = described["relationships"]["statistical"]
    if statistical is None:
        pytest.skip(
            "the product publishes no relationships.statistical yet (lane CHa's ladder, chain, "
            "procedure, rules, words, not_carried, ineligible, withheld; moments.codes, moments.regions)"
        )
    columns = {c["name"]: c for c in described["columns"]}
    values = {name: [line.split(",")[at] for line in rows[1:]] for at, name in enumerate(rows[0].split(","))}
    lads = {}
    for entry in statistical["ladder"]:
        name = entry["column"]
        block = columns[name]
        rungs = dict(block.get("percentiles") or {})
        rungs.update(block.get("percentiles_between") or {})
        cells = [("value", Fraction(v)) for v in values[name]]
        lads[name] = co.ladder_of(name, "count", cells, rungs={k: v for k, v in rungs.items() if v is not None},
                                  floor=described["settings"]["small_cell_floor"])
        assert lads[name].totals == entry["totals"], name
    for family in statistical["chain"]:
        parents = [(p["column"], int(p["level"][1])) for p in family["parents"]]
        expected = co.table_of(lads, family["child"], int(family["level"][1]), parents) if parents else None
        if expected is not None:
            assert family["table"] == expected, family["child"]
