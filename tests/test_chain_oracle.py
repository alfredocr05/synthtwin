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
    E(1491/2): t is about 1075.53, j = 1075 > 1074, so exactly 0, as the
    page's cut-off says. (A cut-off at 1075 gives 0 there too, and at
    every gap with j = 1075: `p(r)` lies in (1/2, 1], so `p(r) 2**-1075`
    is at most half the least subnormal and rounds to 0, a tie going to
    the even 0; that mutant is equivalent, MEASURED in the lane's repair.)
    MUTANT (a float in a decision): the libm exponential differs from the
    stated one in the last bits at gaps 1/2, 2 and 10 (0x1.368b2fc6f960ap-1
    against the stated 0x1.368b2fc6f9604p-1 at 1/2), so a weight read
    from it would move the frozen vectors."""
    case = FROZEN["chain"]["stated_exponential"]
    assert case["values"][0] == "0x1.0000000000000p+0"
    assert co.stated_exponential(745) == Fraction(2) ** -1074
    assert case["values"][5] == "0x0.0000000000001p-1022"
    assert case["values"][6] == "0x0.0p+0" and case["values"][7] == "0x0.0p+0"
    assert case["gaps"][7] == "1491/2" and co.b64_floor(co.b64_mul(co.b64(Fraction(1491, 2)), co.LOG2E)) == 1075
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


def test_a_date_and_a_clock_are_cut_at_their_nine_interior_rungs():
    """Contract 4.6b.2: a `datetime` column's `L0` edges are the nine
    interior rungs `p01` to `p99` of `date_percentiles`, a `time_of_day`
    column's those of `clock_percentiles`, each on its own ordinal; `L1`
    `p25`, `p50`, `p75`, `p90`; `L2` `p50` (Codex's item 1 of the
    landing's review). DATE: ordinals 0 to 2,000, one row each, rungs 20,
    100, 200, 500, 1,000, 1,500, 1,800, 1,900, 1,980: the bands below 20
    (20 rows), [20, 100) 80, [100, 200) 100, [200, 500) 300, [500, 1000)
    500, [1000, 1500) 500, [1500, 1800) 300, [1800, 1900) 100, [1900,
    1980) 80 and from 1,980 to 2,000 21; every band at least 11, so no
    merge. L1 cuts at p25 (500), p50, p75 and p90 (1,800): {0..3}, {4},
    {5}, {6}, {7, 8, 9}; L2 at p50: {0..4}, {5..9}. CLOCK: 60 absent and
    the seconds 0 to 999, rungs 10, 50, 100, 250, 500, 750, 900, 950, 990:
    `missing` 60, then 10, 40, 50, 150, 250, 250, 150, 50, 40, 10. The band
    below p01 (10 rows) joins the neighbour holding fewer rows, [p01,
    p05) (40) rather than `missing` (60): 50; the band from p99 (10) joins
    its one neighbour [p95, p99) (40): 50. Totals 60, 50, 50, 150, 250,
    250, 150, 50, 50; the taken-in sub-bands in L0 bands 1 and 8. MUTANT:
    the number columns' cuts (the first build's), which read p10 to p90
    alone: the date's totals 200, 300, 500, 500, 300, 201 and the clock's
    60, 100, 150, 250, 250, 150, 100."""
    case = FROZEN["chain"]["temporal_ladders"]
    date, clock = case["datetime"], case["time_of_day"]
    assert date["totals"] == [20, 80, 100, 300, 500, 500, 300, 100, 80, 21]
    assert date["l1"] == [[0, 1, 2, 3], [4], [5], [6], [7, 8, 9]]
    assert date["l2"] == [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]
    assert date["l0"][0] == [["range", None, "p01"]] and date["l0"][9] == [["range", "p99", None]]
    assert clock["totals"] == [60, 50, 50, 150, 250, 250, 150, 50, 50]
    assert clock["l0"][1] == [["range", None, "p01"], ["range", "p01", "p05"]]
    assert clock["l0"][8] == [["range", "p95", "p99"], ["range", "p99", None]]
    assert clock["l1"] == [[0], [1, 2, 3], [4], [5], [6], [7, 8]]
    assert clock["l2"] == [[0], [1, 2, 3, 4], [5, 6, 7, 8]] and clock["taken_in"] == [1, 8]
    cells, rungs = oc.date_ladder_cells()
    assert co.ladder_of("visit_date", "datetime", cells, rungs=rungs).totals == date["totals"]
    mutant = FROZEN["chain"]["temporal_ladders_mutant_number_cuts"]
    assert mutant["datetime"]["totals"] == [200, 300, 500, 500, 300, 201]
    assert mutant["time_of_day"]["totals"] == [60, 100, 150, 250, 250, 150, 100]
    assert co.ladder_of("visit_date", "count", cells, rungs=rungs).totals == mutant["datetime"]["totals"]
    with pytest.raises(ValueError):
        co.ladder_of("visit_date", "date", cells, rungs=rungs)


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
    -14165/65536, exact. The slope family's latent orders `L` are frozen
    bit for bit, so a cell mean left unrounded (G16.2: "an exact integer
    sum divided once in binary64") moves them. MUTANTS: rows sorted by row number instead of L
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


# --- RULE W1 in full (contract 4.6b.3, 4.6b.9 (c), 4.6b.10) ---------------------------------


def test_w1_reads_a_confinement_across_the_chain_both_ways():
    """`A` (a1 60, a2 40), `B | A` = [[30, 0, 30], [20, 20, 0]], `C | B` =
    [[0, 50], [0, 20], [15, 15]] on 100 rows; `B`'s `L2` is b1 against
    {b2, b3}. `A`'s group in a2: `B | A` admits b1 and b2 beside it (two
    `L2` bands: passes), and `C | B`'s rows b1 and b2 read c2 alone, so
    `C` is confined to c2 by noughts in ANOTHER family: W1 fails on `C`.
    `C`'s group in c1: only row b3 of `C | B` reads c1, so `B` is b3 (one
    `L2` band) and, through `B | A`'s column b3, `A` is a1: W1 fails on
    `A` and on `B`. MUTANTS: the support without its downward pass misses
    (A, C); without its upward pass, (C, A)."""
    case = FROZEN["chain"]["w1_across"]
    assert case["tables"] == [[[60, 40]], [[30, 0, 30], [20, 20, 0]], [[0, 50], [0, 20], [15, 15]]]
    assert case["failures"] == [["A", 1, "C", [1]], ["C", 0, "A", [0]], ["C", 0, "B", [1]]]
    assert case["admitted"]["A1"] == {"A": [1], "B": [0, 1], "C": [1]}
    assert case["admitted"]["C0"] == {"A": [0], "B": [2], "C": [0]}
    assert _json(oc.case_w1_across()) == case


def test_w1_reads_a_derived_family_codex_s_item_2():
    """Codex's item 2 of 2026-10-19 (contract 4.6b.3, a `K-S6-08`
    fixture): `{D | A}` = [[0, 45], [0, 15], [20, 20]] is placed at its
    rule's step; the root pair `(B, A)` then places `A | B` = [[20, 0,
    40], [25, 15, 0]], whose child `A` already stands in `{D | A}`. `B`'s
    group in b2: `A` is a1 or a2 beside it (two `L2` bands of `A`, a1
    against {a2, a3}: passes), and `{D | A}`'s rows a1 and a2 read d2
    alone, so `D`, read at its one level as its coarsest, is confined:
    W1 refuses the option. The pair (B, D) holds neither the step's child
    nor its parent's own family: the junction tree joins `{D | A}` to
    `A | B`, the family `A` is the child of (edges [0, 2] and [2, 1]).
    MUTANT: the withdrawn shortcut, W1 read only on the pairs holding the
    step's child, which finds no failure and makes it eligible."""
    case = FROZEN["chain"]["w1_derived"]
    assert case["option_table"] == [[20, 0, 40], [25, 15, 0]] and case["derived_table"] == [[0, 45], [0, 15], [20, 20]]
    assert case["edges"] == [[0, 2], [2, 1]]
    assert (case["eligible"], case["why"], case["failures"]) == (False, "W1", [["B", 1, "D", [1]]])
    assert _json(oc.case_w1_derived()) == case
    mutant = FROZEN["chain"]["w1_derived_mutant_step_pairs_only"]
    assert (mutant["eligible"], mutant["why"]) == (True, "eligible")


def test_w1_reads_member_by_member():
    """4.6b.9 (c)'s second case: `A` and `B | A` = [[30, 20], [25, 25]]
    placed, the option `X | A, B` = [[15, 15], [0, 20], [12, 13], [0,
    25]] (rows (a1, b1), (a1, b2), (a2, b1), (a2, b2)). `X`'s group in x1:
    its column holds two non-zero cells, (a1, b1) and (a2, b1), which
    differ in `A` and agree in `B`, so `B` is b1 beside it: W1 refuses on
    `B` (A passes). MUTANT: the design's own clause (two non-zero cells
    beside the group's band), which passes it."""
    case = FROZEN["chain"]["w1_member"]
    assert case["option_table"] == [[15, 15], [0, 20], [12, 13], [0, 25]]
    assert (case["eligible"], case["why"], case["failures"]) == (False, "W1", [["X", 0, "B", [0]]])
    assert _json(oc.case_w1_member()) == case
    assert FROZEN["chain"]["w1_member_mutant_design_clause"]["eligible"] is True


# --- the boundaries the page states ------------------------------------------------------------


def test_the_floor_ne_and_w3_at_their_boundaries():
    """THE FLOOR at f = 11: a cell of 10 refused, of 11 or 0 kept (MUTANT:
    the test at f - 1). NE, a root pair of binary columns on 300 rows,
    child (30, 270): beside parent (120, 180) the least expected count is
    30 * 120 / 300 = 12 = f + 1, offered at L0; beside (110, 190) it is 11
    = f, and binary columns cannot coarsen, so not offered (MUTANT: NE at
    f, which offers it). NE ON A PARENTS' CELL OF TOTAL 0: `C | A, B` on
    1,000 rows with `B | A` = [[200, 200, 200], [0, 150, 250]]; the cell
    (a2, b1) holds 0, its expected count 0 < 12, so the member whose
    smallest total is smallest, `B` (200 against 400 and 500), coarsens
    to `L2` (b3 against {b1, b2}), where the cells are 200, 400, 250, 150
    and the least expected is 500 * 150 / 1000 = 75: offered at (A L0, B
    L2, C L0) (MUTANT: NE skipping cells of total 0, which offers L0).
    W3 AT EQUALITY: X (22, 40, 38, 100), Y (30, 170) on 200 rows: X's 22
    meets 11 * 2 = 22 and holds; Y's 30 is below 11 * 4 = 44 and fails
    alone, and a binary Y cannot coarsen, so not offered (MUTANT: W3
    failing at equality coarsens X to L2, (100, 100), where both hold and
    NE holds, 30 * 100 >= 12 * 200: offered). W3'S CHOICE: X (15, 85,
    100) and Y (25, 75, 100) both fail 33; the smaller smallest total, X,
    coarsens to L2 (100, 100), where Y's 25 meets 22: offered at (X L2, Y
    L0), NE 25 * 100 >= 2400 (MUTANT: the larger, Y, coarsens first and
    ends at (L2, L2))."""
    chain = FROZEN["chain"]
    assert chain["floor_edge"] == {"ten": False, "eleven": True, "nought": True}
    assert chain["ne_edge"] == {"twelve": {"P": 0, "C": 0}, "eleven": None}
    assert chain["ne_zero_cell"] == {"anchor_table": [[200, 200, 200], [0, 150, 250]],
                                     "offered": {"A": 0, "B": 2, "C": 0}}
    assert chain["w3_equality"] == {"offered": None}
    assert chain["w3_choice"] == {"offered": {"X": 2, "Y": 0}}
    for name, build in (("floor_edge", oc.case_floor_edge), ("ne_edge", oc.case_ne_edge),
                        ("ne_zero_cell", oc.case_ne_zero_cell), ("w3_equality", oc.case_w3_equality),
                        ("w3_choice", oc.case_w3_choice)):
        assert _json(build()) == chain[name], name


def test_the_merge_s_tie_and_the_score_s_empty_row():
    """THE MERGE: bands of 20, 20, 5, 20, ... (225 rows): the band of 5
    joins the neighbour holding fewer rows, a tie of 20 and 20, so the
    EARLIER: totals 20, 25, 20, ..., the taken-in sub-band in L0 band 1
    (MUTANT: ties to the later, 20, 20, 25). THE SCORE: [[30, 10, 0], [0,
    0, 0], [10, 25, 5]] reads `df` over the rows whose totals are not
    nought, (2 - 1)(3 - 1) = 2, so u = 150/7 - 2 = 136/7 as without the
    empty row (MUTANT: df over every row, 4, u = 122/7)."""
    assert FROZEN["chain"]["merge_tie"] == {"totals": [20, 25] + [20] * 9, "taken_in": [1]}
    assert _json(oc.case_merge_tie()) == FROZEN["chain"]["merge_tie"]
    assert FROZEN["chain"]["score_empty_row"]["u"] == "136/7"
    assert co.score([[30, 10, 0], [0, 0, 0], [10, 25, 5]]) == Fraction(136, 7)


def test_we_refuses_codex_s_133_rows():
    """Contract 4.6b.3's own case: 133 rows, 33 records holding nothing
    published as 11, 11 and 11 (none as nought, so Z = 0, and P = 0),
    100 tabled rows over A, B and C, each one level or blank. AB = [[22,
    22], [28, 28]] and C | B = [[22, 28], [22, 28]]; no row is blank in all
    three, and 6 read A and C recorded beside a blank B. x0 is the cell
    blank in all three; b(x0) is the least published count holding it:
    22 for (A, B) (its cell (blank, blank)), 11 for (A, C) ([[11, 33],
    [33, 23]]), 22 for (B, C); each is above Z + P = 0, so RULE WE
    refuses every root pair and only "no family" is eligible (MUTANT: no
    RULE WE, which makes all 27 root options eligible)."""
    case = FROZEN["chain"]["we133"]
    assert case["totals"] == {"A": [44, 56], "B": [50, 50], "C": [44, 56]}
    assert [(p["pair"], p["table"], p["b_x0"], p["eligible"], p["why"]) for p in case["pairs"]] == [
        (["A", "B"], [[22, 22], [28, 28]], 22, False, "WE"),
        (["A", "C"], [[11, 33], [33, 23]], 11, False, "WE"),
        (["B", "C"], [[22, 28], [22, 28]], 22, False, "WE")]
    assert case["eligible_options"] == 1
    assert FROZEN["chain"]["we133_mutant_no_we"]["eligible_options"] == 28
    assert _json(oc.case_we133()) == case


def test_the_draw_s_edges_and_the_moved_target_s_tie():
    """THE UNIFORM SHARE at its edge: U1 = 2**33 has its top 30 bits clear
    (U1 >> 34 = 0, though U1 >> 33 = 1), so the share is uniform and
    places (2**63 * 4) >> 64 = 2 (MUTANT: 31 bits, which weighs it). THE
    WEIGHTED CHOICE's tie: two equal scores weigh 1 and 1, running sums 1
    and 2; U2 = 2**63 gives U2 >> 11 = 2**52, a share of 1/2, threshold
    1/2 * 2 = 1; the first running sum ABOVE 1 is the second: place 1
    (MUTANT: at or above, place 0). THE MOVED TARGET's last tie:
    [[10, 10], [10, 10]] against rows [21, 19] and columns [20, 20]: the
    tables [[a, 21 - a], [20 - a, a - 1]] hold no nought; the distance
    2 (|a - 10| + |a - 11|) is least, 2, at a = 10 and 11, whose squares
    are both 2; row-major [11, 10, 9, 10] is greater than [10, 11, 10, 9]
    at the first place: a = 11 (MUTANT: the least). THE MOVED TARGET's
    first key: [[20, 0, 10], [0, 20, 10]] against rows [11, 49] and columns
    [0, 42, 18]: the tables [[0, b, 11 - b], [0, 42 - b, 7 + b]] put b units
    in the published nought (0, 1), fewest at b = 0, [[0, 0, 11], [0, 42,
    7]], distance 20 + 1 + 22 + 3 = 46, though b = 1 to 3 reach distance 44
    (MUTANT: the distance before the noughts, which takes b = 1, the one
    of those three with fewest noughts)."""
    case = FROZEN["chain"]["draw_edges"]
    assert int(case["edge_word"][:16], 16) == 2 ** 33 and case["edge"] == {"place": 2, "how": "uniform"}
    assert case["tie"]["place"] == 1 and case["tie"]["how"] == "weighted"
    assert case["tie"]["weights"] == ["0x1.0000000000000p+0", "0x1.0000000000000p+0"]
    assert _json(oc.case_draw_edges()) == case
    assert FROZEN["chain"]["moved_tie"] == {"moved": [[11, 10], [9, 10]], "units_in_noughts": [],
                                            "noughts_first": {"moved": [[0, 0, 11], [0, 42, 7]], "units_in_noughts": []}}
    assert _json(oc.case_moved_tie()) == FROZEN["chain"]["moved_tie"]
    assert co.moved_target([[10, 10], [10, 10]], [21, 19], [20, 20])[0] == [[11, 10], [9, 10]]


def test_a_slope_parent_s_absent_cells_take_no_term():
    """G16.12 item 11: `X` holds 5 absent cells and the readings 1 to 95,
    its one edge at 46; the absent band (5 rows) joins its one neighbour,
    the readings below 46 (45 rows), an ORDERED band of 50. `Y | X`
    publishes a slope on `X` (beta 0.5, sigma 2), value codes on 0 to 98.
    The walk deals `X`'s 5 absent cells inside the band; their rows'
    reading map is clear, so their term is nought and L = 2 z exactly as
    binary64 rounds it, and the cell's mean reads the 45 readings alone:
    the codes floor(256 x / 98) for x from 1 to 45 sum to 2,681, so the
    mean is 2681/45, about 59.58, divided once in binary64; the other
    cell's 50 codes sum to 9,184, a mean of 4592/25 = 183.68, rounded the
    same way. MUTANTS: the term read on rows whose map is clear
    (the band code read as the mark), and the mean left unrounded."""
    case = FROZEN["chain"]["slope_absent"]
    assert case["x_l0"] == [["missing", ["range", None, "p10"]], [["range", "p10", None]]]
    assert case["x_totals"] == [50, 50] and case["met"]
    assert sum((256 * x) // 98 for x in range(1, 46)) == 2681 and sum((256 * x) // 98 for x in range(46, 96)) == 9184
    assert case["means"] == {"0": co.b64_hex(co.b64(Fraction(2681, 45))), "1": co.b64_hex(co.b64(Fraction(4592, 25)))}
    assert co.b64(Fraction(2681, 45)) != Fraction(2681, 45) and co.b64(Fraction(4592, 25)) != Fraction(4592, 25)
    _, _, _, words, _, _ = oc.slope_absent_setup()
    assert len(case["absent_rows"]) == 5
    for r in case["absent_rows"]:
        expected = co.b64(co.b64_mul(co.published_decimal("2.0000"), co.hidden_score(words[1][r])))
        assert case["latent"][r] == co.b64_hex(expected)
    assert _json(oc.case_slope_absent()) == case


def test_a_step_s_candidates_in_option_order():
    """A later step's candidates for `D` beside `A`, `B | A` and `C | A`
    (four binary columns on 2,000 rows, every cell 125, so every candidate
    is offered): ordered by the anchor's place in the chain, then by the
    parents' places in schema order compared as lists: (A) at 0; (A, B)
    and (B) at 1; (A, C) and (C) at 2. MUTANT: the parents' places first,
    which reads (A), (A, B), (A, C), (B), (C)."""
    assert FROZEN["chain"]["step_order"]["candidates"] == [
        [["A"], 0], [["A", "B"], 1], [["B"], 1], [["A", "C"], 2], [["C"], 2]]
    assert _json(oc.case_step_order()) == FROZEN["chain"]["step_order"]


# --- G16.12 items 8, 9, 9b, 10 and 12 (Codex's item 4 of the landing's review) ---------------


def test_the_cell_index_reads_back_at_three_bytes_and_at_four():
    """G16.12 item 8; G16.2 step 4: an index is 3 bytes a row, 4 where the
    column holds more than 16,777,215 cells (the byte order is the
    oracle's own reading, little-endian). At 16,777,215 cells, 3 bytes:
    16,777,214 is fe ff ff. At 20,000,000 cells, 4 bytes: 16,777,216 is
    00 00 00 01 and 19,999,999 = 0x01312cff is ff 2c 31 01; every index
    reads back. MUTANT: 3 bytes whatever the column holds, which reads
    16,777,216 back as 0 and 19,999,999 as 19,999,999 - 2**24 =
    3,222,783."""
    case = FROZEN["chain"]["cell_index"]
    assert case["three"]["bytes"] == "000000010000ff0000000001feffff"
    assert case["four"]["bytes"] == "00000000ffffff0000000001ff2c3101"
    for part in ("three", "four"):
        assert case[part]["read_back"] == case[part]["indices"]
    assert (co.index_width(16_777_215), co.index_width(16_777_216)) == (3, 4)
    mutant = FROZEN["chain"]["cell_index_mutant_three_bytes"]["four"]["read_back"]
    assert mutant == [0, 16_777_215, 0, 3_222_783]
    assert _json(oc.case_cell_index()) == case


def test_a_stray_row_takes_a_cell_only_from_an_ineligible_column():
    """G16.12 item 9; G16.5 and G2.1 step 2's second walk. `A` and `Y`
    eligible, `X` ineligible and named by no rule. (i) Rows (4, x1, 8),
    nothing, (6, x2, 2): the stray row 1 takes a cell in the first column
    that may give and has a giver, `X`; its giver is the first row holding
    `X` and two or more cells, row 0: rows (4, -, 8), (-, x1, -), (6, x2,
    2), no eligible cell moved. (ii) Rows (4, -, 8), nothing, (-, x2, -):
    `X`'s one holder holds one cell, so no column may give and row 1
    stays holding nothing, named. MUTANT: an eligible column giving (the
    held page's fix, withdrawn), which moves `A`'s 4 from row 0 into row 1
    in both, two eligible cells off their rows each time."""
    case = FROZEN["chain"]["stray_rows"]
    assert case["giver"] == {"rows": [["4", "", "8"], ["", "x1", ""], ["6", "x2", "2"]],
                             "exchanges": [[1, "X", 0]], "stayed": [], "eligible_cells_moved": 0}
    assert case["no_giver"]["stayed"] == [1] and case["no_giver"]["exchanges"] == []
    mutant = FROZEN["chain"]["stray_rows_mutant_eligible_gives"]
    assert [mutant[p]["eligible_cells_moved"] for p in ("giver", "no_giver")] == [2, 2]
    assert mutant["no_giver"]["exchanges"] == [[1, "A", 0]]
    assert _json(oc.case_stray_rows()) == case


def test_a_stray_row_beside_a_computed_column():
    """G16.12 item 9b: `B` computed as `A + D` (`D` 2, absent, 1 on the
    three rows), `A` eligible, and a stray row 1. (i) Columns `A`, `B`:
    `B` is computed and `A` eligible, so no column may give and the row
    stays, named; `B = A + D` holds on every row. (ii) Beside `C`, which
    no rule computes or reads: the row takes `C`'s c1 from row 0, and
    `B = A + D` still holds on every row. MUTANT: the computed column
    giving its cell (B's 5 moves from row 0 to row 1), which breaks `B = A
    + D` on 2 rows: row 0 holds `A` and `D` without `B`, row 1 `B` without
    `A`."""
    case = FROZEN["chain"]["stray_computed"]
    assert (case["alone"]["stayed"], case["alone"]["rows_breaking_b_eq_a_plus_d"]) == ([1], 0)
    assert case["beside_c"]["exchanges"] == [[1, "C", 0]] and case["beside_c"]["rows_breaking_b_eq_a_plus_d"] == 0
    mutant = FROZEN["chain"]["stray_computed_mutant_computed_gives"]
    assert [mutant[p]["rows_breaking_b_eq_a_plus_d"] for p in ("alone", "beside_c")] == [2, 2]
    assert _json(oc.case_stray_beside_a_computed_column()) == case


def test_a_moved_parent_count_moves_a_later_family_by_its_parent_cells():
    """G16.12 item 10; G16.0's target test, read on the parent cells. `AB`
    [[60, 40], [40, 60]] with `B`'s twin totals [80, 120]: the tables
    [[x, 100 - x], [80 - x, 20 + x]] are 2|x - 60| + 2|40 - x| off,
    smallest (40) for x in 40 to 60, and the squares 2 (x - 60)**2 + 2
    (40 - x)**2 are smallest at x = 50: [[50, 50], [30, 70]]. `C | AB`
    [[60, 0], [0, 40], [0, 40], [60, 0]] against the cells (50, 50, 30, 70)
    and C's totals (120, 80): [[50, 0], [0, 50], [0, 30], [70, 0]], no
    unit in a nought. `A` keeps (100, 100) and `C` (120, 80), but `AC`'s
    cells go from 60, 40, 60, 40 to 50, 50, 70, 30, so `D | AC` [[30, 30],
    [20, 20], [30, 30], [20, 20]] moves: each row r splits as (x, r - x),
    10 off at best, the 40 reached with x summing to 100, and the squares
    smallest at x = r / 2: [[25, 25], [25, 25], [35, 35], [15, 15]]. The
    walk meets every target, the moved ones included. MUTANT: the first
    build's test on each member's totals alone, which finds A, C and D
    unchanged and keeps `D | AC`'s published table, whose row totals (60,
    40, 60, 40) the parent cells (50, 50, 70, 30) cannot hold: no table to
    deal, and the walk stops before `D`."""
    case = FROZEN["chain"]["joint_move"]
    assert case["moved"] == {"1": {"table": [[50, 50], [30, 70]], "units_in_noughts": []},
                             "2": {"table": [[50, 0], [0, 50], [0, 30], [70, 0]], "units_in_noughts": []},
                             "3": {"table": [[25, 25], [25, 25], [35, 35], [15, 15]], "units_in_noughts": []}}
    assert case["met"] and case["families_dealt"] == 4 and case["ac_joint"] == [50, 50, 70, 30]
    mutant = FROZEN["chain"]["joint_move_mutant_members_test"]
    assert mutant["moved"]["3"] == {"undealable": True, "row_totals": [60, 40, 60, 40], "parent_counts": [50, 50, 70, 30]}
    assert mutant["families_dealt"] == 3 and not mutant["met"]
    assert _json(oc.case_joint_move()) == case


def test_the_moved_table_by_rows_equals_the_enumeration():
    """G16.6's order read row by row (`moved_target`) against every table
    enumerated (`moved_target_by_enumeration`) on the frozen cases and on
    small tables of 2 to 3 rows and 2 to 3 columns: the same table and the
    same units named."""
    cases = [([[50, 0], [0, 50]], [60, 40], [40, 60]), ([[10, 10], [10, 10]], [21, 19], [20, 20]),
             ([[20, 0, 10], [0, 20, 10]], [11, 49], [0, 42, 18]), ([[60, 40], [40, 60]], [100, 100], [80, 120])]
    for seed in range(40):
        rows = [(seed * 7 + 3 * i) % 9 + 1 for i in range(2 + seed % 2)]
        width = 2 + (seed // 2) % 2
        columns = [sum(rows) // width] * width
        columns[0] += sum(rows) - sum(columns)
        published = [[(seed + i * width + j) % 4 for j in range(width)] for i in range(len(rows))]
        cases += [(published, rows, columns)]
    for published, rows, columns in cases:
        assert co.moved_target(published, rows, columns) == co.moved_target_by_enumeration(published, rows, columns)


def test_a_rules_only_description_deals_a_alone_and_writes_b():
    """G16.12 item 12; G16.10's RULES-ONLY branch. `A`: 4 absent and the
    readings 1 to 36; `{D | A}` at `A`'s L2 (`missing`, below p50 = 19,
    from 19): [[4, 0, 0], [0, 12, 6], [0, 8, 10]], `D` 1 on its `short`
    band and 7 on `long`. `A` is dealt alone in its one cell, `D` as its
    child, every target met; `B = A + D` is written on the 36 rows where
    both hold a reading and absent on the 4 where `A` is (no reading of
    `D` stands beside an absent `A`), so `B >= A` on every row. MUTANT: the
    section not running, which writes no `B`."""
    case = FROZEN["chain"]["rules_only"]
    assert case["d_table"] == [[4, 0, 0], [0, 12, 6], [0, 8, 10]] and case["met"]
    assert (case["b_written"], case["rows_breaking_a_le_b"], case["d_beside_an_absent_a"]) == (36, 0, 0)
    assert FROZEN["chain"]["rules_only_mutant_section_off"]["b_written"] == 0
    assert _json(oc.case_rules_only()) == case


# --- the product against the oracle -------------------------------------------------------


LABEL_ROLES = ("binary", "categorical", "long_tail_labels", "constant")
NUMBER_ROLES = ("count", "continuous")


def _published_rungs(block):
    """A number column's published rungs by key (`percentiles` and `percentiles_between`), nulls left out."""
    rungs = dict(block.get("percentiles") or {})
    rungs.update(block.get("percentiles_between") or {})
    return {key: Fraction(value) for key, value in rungs.items() if value is not None}


def _oracle_ladder(name, block, raw, floor, position):
    """The oracle's ladder of one column from its published block and the table's cells:
    a label column's published `levels` (each `{label, count}`, a cell outside them in the
    held-back pool), a number column's published rungs; another role is not read here."""
    role = block["role"]
    if role in LABEL_ROLES:
        levels = [(entry["label"], entry["count"]) for entry in block["levels"]]
        published = {label for label, _ in levels}
        cells = [("missing",) if v == "" else (("level", v) if v in published else ("held",)) for v in raw]
        return co.ladder_of(name, role, cells, levels=levels, floor=floor, position=position)
    if role in NUMBER_ROLES:
        cells = [("missing",) if v == "" else ("value", Fraction(v)) for v in raw]
        return co.ladder_of(name, role, cells, rungs=_published_rungs(block), floor=floor, position=position)
    pytest.fail("the oracle reads no ladder for role %r (column %s)" % (role, name))


def _pair_of(entry):
    return tuple(entry["columns"]) if isinstance(entry, dict) else tuple(entry)


def _second_code(x, rungs, lo_key, hi_key):
    """Contract 4.6d.1's second code on the rungs' probability scale, in exact fractions."""
    lo, hi = rungs[lo_key], rungs[hi_key]
    by_value = {}
    for key, value in rungs.items():
        if lo <= value <= hi:
            by_value[value] = by_value.get(value, []) + [Fraction(int(key[1:]), 100)]
    points = sorted(by_value)
    middle = {v: (min(by_value[v]) + max(by_value[v])) / 2 for v in points}
    position = middle[points[0]] if x <= points[0] else middle[points[-1]]
    for j in range(len(points) - 1):
        if x == points[j]:
            position = middle[points[j]]
        elif points[j] < x < points[j + 1]:
            step = (x - points[j]) / (points[j + 1] - points[j])
            position = max(by_value[points[j]]) + step * (min(by_value[points[j + 1]]) - max(by_value[points[j]]))
    p_lo, p_hi = Fraction(int(lo_key[1:]), 100), Fraction(int(hi_key[1:]), 100)
    q = 256 * (position - p_lo) / (p_hi - p_lo)
    return min(255, max(0, q.numerator // q.denominator))


def test_the_product_s_chain_against_the_oracle(tmp_path, monkeypatch):
    """Runs `synthtwin profile` on a seeded neutral table and compares what
    it publishes in `relationships.statistical` with the oracle, as the
    page defines each object (contract 4.6b.2, 4.6b.5, 4.6b.8, 4.6d.2):
    - `ladder`: each column's `L0` totals, `l1` and `l2` from the table's
      cells, a label column read at its published role and `levels`, a
      number column at its published rungs;
    - `chain`: each family's complete table at its published levels, its
      anchor (the earliest family holding every parent), the floor on
      every cell, and RULE W1 on the placed chain with every sub-band an
      `L0` merge took in as an own-fact group (the producer's other
      own-fact groups are read from the column's facts, which the oracle
      does not list);
    - `words` and `not_carried`: each candidate pair's structural word,
      `exact` where one placed family holds both and `implied` otherwise
      (`pinned` where a correlation is published and no family holds
      both), `not_carried` the pairs reading `implied`; `ineligible`:
      every column of the table either in `ladder` or named once there;
    - `moments`: `witness` naming the oracle's class `cho1` (plan
      P4-D421); each published region outside the class's tests (1) and
      (3) is a failure (a node of the region publishing a slope; the
      base cells counted from the members' published bands above
      GROUPS_MAX); every published sum recomputed exactly from the
      table, on the linear or the second code. The witness's verdict
      itself is not compared here: rebuilding the joint space's atoms
      from the published description (pieces holding a POSSIBLE reading,
      each rung's count of readings below it as the rungs bound it,
      4.6d.1 and 4.6d.4) is the producer's construction, which this
      oracle does not hold (plan P4-D421, a stated remainder).
    SKIPPED while the product publishes no `relationships.statistical`
    (contract 4.6b: lane CHa's `ladder`, `chain`, `procedure`, `rules`,
    `words`, `not_carried`, `ineligible`, `withheld`; 4.6d:
    `moments.codes` and `moments.regions`), which invariant S12 holds
    `null` until the landing that ships stage 6."""
    sys.path.insert(0, str(REPOSITORY / "src"))
    from synthtwin.cli import main

    mo = _load("moment_oracle")
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
    floor = described["settings"]["small_cell_floor"]
    names = rows[0].split(",")
    columns = {c["name"]: c for c in described["columns"]}
    values = {name: [line.split(",")[at] for line in rows[1:]] for at, name in enumerate(names)}
    lads = {}
    for entry in statistical["ladder"]:
        name = entry["column"]
        lads[name] = _oracle_ladder(name, columns[name], values[name], floor, names.index(name))
        assert (lads[name].totals, lads[name].l1, lads[name].l2) == (entry["totals"], entry["l1"], entry["l2"]), name
    named = [entry["column"] for entry in statistical["ineligible"]]
    assert sorted(named + list(lads)) == sorted(names) and len(set(named)) == len(named)
    chain = []
    for at, family in enumerate(statistical["chain"]):
        parents = [(p["column"], int(p["level"][1])) for p in family["parents"]]
        level = int(family["level"][1])
        expected = co.table_of(lads, family["child"], level, parents) if parents else [lads[family["child"]].band_totals(level)]
        assert family["table"] == expected, family["child"]
        holding = [i for i, f in enumerate(chain) if all(p in f.members() for p, _ in parents)]
        assert family["anchor"] == (holding[0] if parents and holding else None), family["child"]
        chain += [co.Family(family["child"], level, parents, family["anchor"], family["table"])]
    assert all(co.floor_holds(f.table, floor) for f in chain)
    groups = [(c, band) for c in sorted(lads) for band in lads[c].taken_in]
    assert co.w1_holds(chain, lads, groups)[0]
    moments = statistical.get("moments") or {}
    correlated = set()
    for region in moments.get("regions") or []:
        for total in region["sums"]:
            if total["class"] == "correlation":
                correlated.add(tuple(total["columns"]))
    eligible = [n for n in names if n in lads]
    words = []
    for i, a in enumerate(eligible):
        for b in eligible[i + 1:]:
            together = any(a in f.members() and b in f.members() for f in chain)
            words += [{"columns": [a, b], "word": "exact" if together else ("pinned" if (a, b) in correlated else "implied")}]
    assert [(_pair_of(w), w["word"]) for w in statistical["words"]] == [(_pair_of(w), w["word"]) for w in words]
    assert sorted(_pair_of(e) for e in statistical["not_carried"]) == sorted(
        _pair_of(w) for w in words if w["word"] == "implied")
    if not moments:
        return
    assert moments["procedure"]["witness"] == mo.CLASS_NAME
    codes = {entry["column"]: entry for entry in moments["codes"]}
    for region in moments["regions"]:
        held = [chain[i] for i in region["families"]]
        assert not any(statistical["chain"][i].get("slopes") for i in region["families"]), region["columns"]
        finest = {}
        for family in held:
            for member, lv in zip(family.members(), family.levels()):
                finest[member] = min(lv, finest.get(member, 2))
        for column in region["columns"]:
            finest[column] = 0
        cells = 1
        for member, lv in finest.items():
            cells *= len(lads[member].bands(lv))
        assert cells <= mo.GROUPS_MAX, region["columns"]
        for total in region["sums"]:
            rungs = {c: _published_rungs(columns[c]) for c in total["columns"]}

            def code(c, x, kind):
                entry = codes[c]
                if kind == "S":
                    return _second_code(x, rungs[c], entry["lo"], entry["hi"])
                return co.value_code(x, rungs[c][entry["lo"]], rungs[c][entry["hi"]])

            chosen = []
            for r in range(len(rows) - 1):
                readings = [values[c][r] for c in total["columns"]]
                if any(v == "" for v in readings):
                    continue
                if total["class"] == "band" and lads[total["columns"][0]].row_l0[r] != total["band"]:
                    continue
                if total["family"] is not None:
                    family = chain[total["family"]]
                    where = [lads[m].codes(lv)[r] for m, lv in zip(family.members(), family.levels())]
                    if where[:len(total["cell"])] != list(total["cell"]):
                        continue
                chosen += [r]
            value = 0
            for r in chosen:
                term = 1
                for c, kind, power in zip(total["columns"], total["codes"], total["powers"]):
                    x = Fraction(values[c][r])
                    centre = code(c, rungs[c][codes[c]["p50"]], kind) if total["class"] == "correlation" else 0
                    term *= (code(c, x, kind) - centre) ** power
                value += term
            assert total["value"] == value, total
