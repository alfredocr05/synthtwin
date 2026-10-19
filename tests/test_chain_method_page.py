"""The chain's method page holds what its first review round fixed (plan P4-D407).

WHY A FILE OF ITS OWN. Stage 6's first layer, the chain, is written
before its code: contract section 4.6b, the generation method's G16 and
the validation method's V12 bind lanes CHa, CHb, CHv and CHo, which have
not started, and nothing in the product reads them yet. The disposition
seal turns red on any edit of a sealed passage and is re-sealed by
whoever makes the edit, so it cannot tell a correction from its undoing.
This file can. The page's first skeptic and its statistics review of
2026-10-19 found it wrong in twenty places; every check below is red on
the page as the first build left it (e713688b) and says which item it
holds.

WHAT IS COMPUTED HERE, NOT READ. The first review's three probes are
re-run on invented numbers: the draw's words before and after one
column becomes eligible, the counts a derived difference fixed when its
band totals were published alone, and the cells a four-decimal distance
gave back. The sufficient form of row 9's one test is checked against
every union on small models; case (ii)'s example is enumerated; a
slope's standard error with two parents is worked out both ways; the
weights' raises are put on the score's scale; and the `L0` cut is read
against the ladder lane A0a measured. The rest pins wording, where the
finding was a missing or wrong sentence.

WHAT IS NOT HERE. No chain code exists to run, so nothing here says a
twin meets a family. `K-S6-08`'s enumeration and the oracle's cases
(G16.12) are where lanes CHa and CHo run the method.
"""
import hashlib
import itertools
import json
import pathlib
import re
from fractions import Fraction

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
CONTRACT = REPOSITORY / "docs" / "spec" / "profile-contract-v6.md"
METHOD = REPOSITORY / "docs" / "spec" / "generation-method-v1.md"
VALIDATION = REPOSITORY / "docs" / "spec" / "validation-method-v1.md"
PLAN = REPOSITORY / "docs" / "plans" / "phase-4-columns.md"
CHANGES = REPOSITORY / "CHANGELOG.md"

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


def _section():
    return _between(
        CONTRACT,
        "### 4.6b `relationships.statistical`",
        "<!-- s5: the column block",
    )


def _part(number):
    text = _section()
    at = text.index("#### 4.6b." + number + " ")
    stop = text.find("\n#### 4.6b.", at + 10)
    return _flat(text[at:] if stop < 0 else text[at:stop])


def _proof(letter, following):
    text = _part("9")
    at = text.index("**(" + letter + ") ")
    stop = text.find("**(" + following + ") ", at)
    return text[at:] if stop < 0 else text[at:stop]


def _g16():
    return _flat(_between(METHOD, "## G16. Between columns", "## Conformance checklist"))


def _v12():
    return _flat(_between(VALIDATION, "## V12. Between columns"))


def _decision():
    return _flat(_between(PLAN, "## Decision P4-D407"))


def _without_code(text):
    return re.sub(r"`[^`\n]*`", "", text)


# --- skeptic 1, item 1: the whole suite went red on the page -------------


def test_the_section_cites_no_identifier_in_plain_text_and_binds_no_argument():
    """Item 1. The contract's assembly checker reads a bare `A0a` or `L0` as
    a citation of a rule no section defines, and a settings row reading
    `` `tau` | 2 | `` as a row of C6-143's argument-binding table."""
    plain = _without_code(_section())
    for name in ("A0a", "A0b", "D2r", "L0", "L2b", "M5", "M6", "S15", "S22", "V12", "X5c"):
        found = re.search(r"(?<![A-Za-z0-9_-])" + name + r"(?![A-Za-z0-9_])", plain)
        assert found is None, name + " stands outside a code span in 4.6b"
    binding = re.compile(r"^\|\s*`([a-z0-9_]+)`\s*\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|$", re.MULTILINE)
    assert binding.findall(_section()) == []


# --- skeptic 1, items 2 and 11: the derived difference --------------------


def _derived_difference_counts(rows, a_absent, b_absent, overlap):
    """What the first draft let a reader work out from published numbers."""
    either = a_absent + b_absent - overlap
    d_present = rows - either
    a_recorded_b_absent = (rows - a_absent) - d_present
    a_absent_b_recorded = (rows - b_absent) - d_present
    return a_recorded_b_absent, a_absent_b_recorded


def test_the_first_drafts_derived_difference_fixed_counts_across_columns():
    """Item 2, measured again: 1,000 rows, admission absent on 15, discharge
    on 20. Under the first draft the derived difference's band totals with
    the admission's absent cells fixed "admission recorded, discharge
    absent", and the discharge's own absent cells fixed the converse."""
    assert _derived_difference_counts(1000, 15, 20, 13) == (7, 2)
    assert _derived_difference_counts(1000, 15, 20, 10) == (10, 5)
    assert _derived_difference_counts(1000, 15, 20, 6) == (14, 9)


def test_a_floored_family_leaves_a_small_count_no_eligible_split():
    """Item 2's repair. Under rule 3 the rows where A holds a reading and B
    does not are a sum of family cells, one a band of A; wherever they
    number 1 to f - 1, every split over any number of bands holds a cell
    of 1 to f - 1, so only "not carried" is eligible."""
    for small in range(1, FLOOR):
        for bands in (1, 2, 3):
            for split in itertools.product(range(small + 1), repeat=bands):
                if sum(split) != small:
                    continue
                assert any(0 < cell < FLOOR for cell in split)


def test_a_derived_difference_is_published_only_inside_its_family():
    """Items 2 and 11: the family, its structural zeros, the floor, the
    computed column's absent cells withheld, and no ladder entry."""
    rules = _part("7")
    assert "is published ONLY as the child of one family `{D | A}`" in rules
    assert "`A`'s `missing` band is a band of its own" in rules
    assert "the STRUCTURAL ZEROS of a derived column, published as cells of its table" in rules
    assert "every cell of the family's table is 0 or at least `f`" in rules
    assert "`n_missing`" in rules and "each written `null`" in rules
    assert "publishes only floored band totals at ONE LEVEL" not in rules
    assert "fewer than `max(2 f, f + 4)` tabled rows), the derived column" not in rules
    assert "has no `ladder` entry" in _part("1")
    assert "the derived column's entry `{name, edges, totals, parent, table}`" in _part("5")
    assert "STRUCTURAL ZEROS of 4.6b.7 rule 2 to be published cells" in _part("9")
    invariants = _part("11")
    assert "holding 0 in every value band of the derived column" in invariants
    fixtures = _part("10")
    assert "the first review's derived difference" in fixtures
    assert "(mutant: the first draft's band totals alone)" in fixtures


# --- skeptic 1, item 3: a second description of one table ----------------


def _word(key, name, kind, index, columns):
    message = json.dumps([name, kind, index, columns], separators=(",", ":"), ensure_ascii=False)
    return hashlib.blake2b(
        message.encode("utf-8"), key=key, digest_size=16, person=b"synthtwin.draw.1"
    ).digest()


def test_an_answer_that_makes_a_column_eligible_changes_every_word():
    """Item 3, measured again with the page's own word: no step's word
    survives one more eligible column, so the two descriptions draw
    independently, the two-keys case."""
    key = bytes(range(32))
    before = ["age", "group", "stay", "died"]
    after = ["age", "group", "record_answered", "stay", "died"]
    same = sum(
        _word(key, "clinic", "place", step, before) == _word(key, "clinic", "place", step, after)
        for step in range(1, 40)
    )
    assert same == 0


def test_the_ledger_refuses_a_different_description_of_one_table():
    """Item 3's repair: the digest, the refusal, the declaration, the lost
    key, and the limits the ledger cannot see."""
    draw = _part("4")
    assert "DESCRIPTION DIGEST" in draw
    assert 'person=b"synthtwin.desc.1"' in draw
    assert "this run would publish a different description of it" in draw
    assert "--replace-description" in draw
    assert "`--new-key` is accepted only where the ledger exists and no key file can be read" in draw
    assert "the same settings, the same answers in the questions file and the same `procedure` constants" in draw
    keys = _proof("g", "h")
    assert "with the same settings, the same answers in the questions file" in keys
    assert "0 of 39 step words equal" in keys
    assert "A re-profile of one table under one name and one key is deterministic," not in keys
    limits = _part("13")
    assert "a description replaced with `--replace-description` although it had been shared" in limits
    assert "a deleted data folder, which loses the key and the ledger together" in limits
    assert "before and after an answer makes one more column eligible" in _part("10")


# --- skeptic 1, item 4: case (ii), as ruled --------------------------------


def test_case_two_fixes_only_the_groups_own_count_in_the_example():
    """Item 4's example: six rows with days 0 in a band whose family row
    reads A 56, B 0, C 44, D 0. Over every placement of the six rows,
    "days 0 AND type A or C" is 6, and "days 0 AND type A" (the one band
    of the type's L2 the union meets) reaches 0."""
    row = {"A": 56, "B": 0, "C": 44, "D": 0}
    union = set()
    level_a = set()
    for in_a in range(0, 7):
        in_c = 6 - in_a
        if in_a <= row["A"] and in_c <= row["C"]:
            union.add(in_a + in_c)
            level_a.add(in_a)
    assert union == {6}
    assert min(level_a) == 0 and max(level_a) == 6


def test_case_two_is_stated_as_the_ruled_reading_with_its_example():
    lemma = _proof("c", "d")
    assert "confirmed by the orchestrator's ruling of 2026-10-19 (12:14)" in lemma
    assert "PROVIDED that RULE W1 fixes no band of any published level of any other column" in lemma
    assert "the six rows with days 0 have type A or C" in lemma
    assert "**Stated limit 3 (case (ii) of Lemma 3, as ruled).**" in _part("13")
    assert "case (ii) of Lemma 3 read as the orchestrator ruled" in _part("9")
    assert "reported as accepted under the orchestrator's ruling" in _part("10")


# --- skeptic 1, item 5: what one validation report may print -------------


def _total_variation(cell, a_small, b_first, rows):
    implied = Fraction(a_small * b_first, rows)
    real = [cell, a_small - cell, b_first - cell, rows - a_small - b_first + cell]
    model = [
        implied,
        Fraction(a_small * (rows - b_first), rows),
        Fraction((rows - a_small) * b_first, rows),
        Fraction((rows - a_small) * (rows - b_first), rows),
    ]
    return sum(abs(Fraction(r) - m) for r, m in zip(real, model)) / (2 * rows)


def test_a_four_decimal_distance_gave_a_small_cell_back():
    """Item 5, measured again: 1,000 rows, a column of 15 and 985 beside one
    of 400 and 600, the implied cell 6; the printed distance 0.0060 leaves
    the real cell 3 or 9, both inside 1 to 10."""
    printed = f"{float(_total_variation(3, 15, 400, 1000)):.4f}"
    consistent = [
        cell for cell in range(0, 16)
        if f"{float(_total_variation(cell, 15, 400, 1000)):.4f}" == printed
    ]
    assert printed == "0.0060" and consistent == [3, 9]


def test_inside_or_outside_alone_can_bound_a_cell():
    """Why the repair prints nothing measured, not only a mark: on 60 rows,
    columns of 15 and 45 and of 30 and 30, "inside the dealing spread"
    holds the cell to 5 to 10."""
    rows, a_small, b_first = 60, 15, 30
    shares = [
        Fraction(a_small * b_first, rows * rows),
        Fraction(a_small * (rows - b_first), rows * rows),
        Fraction((rows - a_small) * b_first, rows * rows),
        Fraction((rows - a_small) * (rows - b_first), rows * rows),
    ]
    spread = sum((float(p * (1 - p)) / rows) ** 0.5 for p in shares) / 2
    inside = [
        cell for cell in range(0, a_small + 1)
        if float(_total_variation(cell, a_small, b_first, rows)) <= spread
    ]
    assert inside == list(range(5, 11))


def test_a_report_prints_nothing_measured_for_an_implied_pair():
    report = _v12()
    assert "nothing measured on the file is printed for it" in report
    assert "a pair reading `implied` prints nothing measured" in report
    assert "prints no cell, no count and no flag" in report
    assert "only where it is nought or at least `f`" in report
    assert "which are not counts" not in report
    assert "a table holding a cell of 1 to `f - 1` is reported as holding one" not in report
    assert "nothing measured on the file is printed for it" in _part("12")


# --- skeptic 1, item 6: row 9's test, computable, and its base ------------


def _worlds(totals, classes):
    """Every table over cells (band, mark) with the bands' totals, by the
    class its failing rows fall in. Mark 1 is FAILS."""
    by_class = {name: [] for name in classes}
    ranges = [range(total + 1) for total in totals]
    for fails in itertools.product(*ranges):
        table = []
        for band, total in enumerate(totals):
            table += [(band, 1, fails[band]), (band, 0, total - fails[band])]
        failing = sum(fails)
        for name, members in classes.items():
            if failing in members:
                by_class[name] += [{(b, m): c for b, m, c in table}]
    return by_class


def _passes(worlds):
    cells = list(worlds[0])
    largest = {cell: max(world[cell] for world in worlds) for cell in cells}
    small = [cell for cell in cells if largest[cell] <= FLOOR - 1]
    return any(all(world[cell] == 0 for cell in small) for world in worlds)


def _leaks(worlds):
    cells = list(worlds[0])
    for size in range(1, len(cells) + 1):
        for union in itertools.combinations(cells, size):
            counts = [sum(world[c] for c in union) for world in worlds]
            if min(counts) >= 1 and max(counts) <= FLOOR - 1:
                return True
    return False


def test_a_class_the_sufficient_form_passes_leaks_no_union():
    """Item 6: the sufficient form checked against every union on small
    models of one to three bands. The models where it refuses include
    leaking ones, so it is not vacuous."""
    passed = refused_and_leaking = 0
    for totals in ([12], [3, 14], [12, 12], [2, 9, 13], [11, 11, 11]):
        limit = sum(totals)
        classes = {"phrase": set(range(0, FLOOR))}
        for count in range(FLOOR, limit + 1):
            classes["count " + str(count)] = {count}
        for name, worlds in _worlds(totals, classes).items():
            if not worlds:
                continue
            if _passes(worlds):
                passed += 1
                assert not _leaks(worlds), (totals, name)
            elif _leaks(worlds):
                refused_and_leaking += 1
    assert passed > 0 and refused_and_leaking > 0


def test_the_test_reads_the_rules_base_once_before_the_chain():
    rules = _part("7")
    assert "*Its BASE.* The rule's base is the facts the description publishes whether or not the rule is carried" in rules
    assert "It never holds the facts of the column the rule would compute" in rules
    assert "all of them taken before the chain is searched" in rules
    assert "let `S(K)` be the joint cells whose largest count over the worlds of `K` is at most `f - 1`" in rules
    assert "one exact integer program over the joint cells" in rules
    assert '"not carried", which is ALWAYS eligible' in rules
    every_count = _part("9")
    assert "the one test checks every union of the joint cells around the rule in every class, exactly" not in every_count
    assert "| 9, 9b, 10 | an order rule or formula rule carried" in _section()


# --- skeptic 1, items 7, 8, 10 and 12 --------------------------------------


def test_limit_one_bounds_the_ratio_by_the_steps_eligible_options():
    """Item 7: a step gives an eligible option at least 2**-30 over m and
    at most 1, so the ratio is bounded by m times 2**30, not k_max's."""
    for options in (2, 3, 1000):
        least = Fraction(1, 2**30) * Fraction(2**64 // options, 2**64)
        assert 1 / least >= options * 2**30
        assert 1 / least < (options + 1) * 2**30
    limits = _part("13")
    assert "beyond `m` times `2**30` at each step, `m` being the step's count of eligible options" in limits
    assert "beyond `k_max` times `2**30`" not in limits


def test_every_promise_reads_the_floor():
    """Item 8: a floor below 11 is allowed, so 'no count of 1 to 10' would
    be false there."""
    promised = _part("13")
    assert "no count of 1 to `f - 1` (1 to 10 at the default floor of 11) is fixed" in promised
    assert "no count of 1 to 10 is fixed" not in promised
    decision = _decision()
    assert "no printed joint cell holds 1 to `f - 1` (1 to 10 at the default floor of 11)" in decision
    assert "no count of 1 to `f - 1` can be fixed or bounded inside 1 to `f - 1`" in decision


def test_the_promises_carry_the_statistics_and_the_hours():
    """Item 10: 'unchanged' cannot drop two of the three promise lines."""
    promised = _part("13")
    assert "**Statistics, as measured before this page**" in promised
    assert "63 per cent of supported estimates" in promised and "by 21.5 at 100,000" in promised
    assert '"stops drifting" is withdrawn' in promised
    assert "**Hours**" in promised and "7.3 to 10 hours on Python 3.13" in promised


def test_the_prototypes_cell_count_is_attributed():
    """Item 12: 37 to 95 is A3's average of nonzero cells under its own
    rules, not a measurement under this page's RULE W3."""
    chain = _part("5")
    assert "averaged 37 to 95 NON-ZERO cells a family" in chain
    assert "not under this section's RULE W3" in chain


# --- skeptic 1, item 9: V12's mutants and a slope's standard error -------


def test_a_slopes_error_with_two_parents_reads_the_inverse():
    """Item 9: with two correlated slope parents the one-parent error,
    sigma over the root of the parent's own sum of squares, is too small."""
    first = [-2, -1, 0, 1, 2]
    second = [-1, -1, 0, 1, 1]
    sxx = sum(x * x for x in first)
    syy = sum(y * y for y in second)
    sxy = sum(x * y for x, y in zip(first, second))
    determinant = Fraction(sxx * syy - sxy * sxy)
    inverse_first = Fraction(syy) / determinant
    one_parent = Fraction(1, sxx)
    assert inverse_first > one_parent
    report = _v12()
    assert "the inverse of the parents' pooled within-cell cross-product matrix of codes" in report


def test_v12s_mutants_name_what_moves_a_table():
    report = _v12()
    assert "in DIFFERENT bands of the column at the family's level" in report
    assert "every family holding it as a child under a parent, or as a parent, MISSED" in report
    assert "the implied lines of the pairs whose path runs through `F` printed outside" not in report


# --- the statistics review, items 1 to 8 -----------------------------------


def _settings():
    return _part("14")


def test_the_time_and_event_raise_has_no_measured_effect():
    """Statistics item 1: A0a's t1 placed the pair as the root; t0 and t1
    differ only in the root pair's orientation."""
    settings = _settings()
    assert "`w_te`, the time-and-event raise | `\"0\"`: no measured effect" in settings
    assert "differ only in the root pair's orientation" in settings
    assert "measures that orientation, not this raise" in settings
    assert "| `w_te` | 10 (on) |" not in settings


def test_every_raise_is_read_on_the_scores_scale():
    """Statistics item 2: the bake-off scored (X2 - df) / n and added 0.05
    a seed, which is 0.05 n on the scale of u; a raise of 10 tau is a
    fiftieth of that at 20,000 rows and a five-hundredth at 200,000."""
    tau = 2
    for rows, ratio in ((20000, 50), (200000, 500)):
        raise_on_u = Fraction(1, 20) * rows
        assert raise_on_u / (10 * tau) == ratio
    search = _part("3")
    for raised in ("by `w_rule n`", "by `w_te n`", "by `w_seed n`"):
        assert raised in search
    assert "by `10 tau`" not in search and "`w_seed tau`" not in search
    assert "`w_rule`, the inferred rule's raise | `\"1/20\"` | PROVISIONAL" in _settings()


def test_the_kpi_minimums_are_read_against_the_batterys_ledger():
    """Statistics item 3: each id against lane E0b's ledger target."""
    decision = _decision()
    assert "| `K-BC-02` | McNemar's z of the truths only Rep gets back" in decision
    assert "the AUC gap within 3 yardsticks, importance rank at most 0.3 under Rep" in decision
    assert "| `K-BC-05` | at most 3 times Rep |" in decision
    assert "`analyses_stopping` 0" in decision
    assert "stable across twin seeds AND inside the yardstick, at most 10 points under Rep" in decision
    assert "`controls_hold`" in decision and "`families_control_void`" in decision
    assert "the median over twin seeds with the worst beside it" in decision
    assert "none lowered beyond question 6's accepted limit" in decision
    for withdrawn in (
        "60 per cent of the AUC today's twin loses recovered,",
        "`K-BC-05` at most 4 x Rep",
        "a run void unless Rep meets its target and Shuf fails it",
        "CLOSES at this page's ratification with none lowered:",
    ):
        assert withdrawn not in decision


def test_the_stage_six_gate_risk_is_stated():
    """Statistics item 4: the gate's K-BC-01 minimum is judged on the chain
    alone, which A0b's 50-column panel puts short of the midpoint."""
    decision = _decision()
    assert "171 of 273 at 20,000 rows against a midpoint of 183" in decision
    assert "141 of 280 at 50,000 rows against 169" in decision
    assert "whose midpoint is 59.2 per cent" in decision
    assert "trades about 3 points of the chain alone" in decision


def test_every_bake_off_count_says_what_it_was_measured_without():
    """Statistics item 5."""
    assert "without the draw and without the design's disclosure rules beyond the floor" in _settings()
    decision = _decision()
    assert "for the chain together with lane MPOL's polish" in decision
    assert "10 points behind a fresh sample at 50,000 rows under version 2.1's rules" in decision


def test_the_l0_cut_is_fixed_only_where_it_was_measured():
    """Statistics item 6."""
    settings = _settings()
    assert "FIXED up to 50,000 rows: every fifth percentile" in settings
    assert "166 against 153 of 279, not on every seed" in settings
    assert "FIXED below 200,000 rows" not in settings


def test_tau_is_provisional_with_a_named_measurement():
    """Statistics item 7."""
    settings = _settings()
    assert "| `tau` | two, provisionally | PROVISIONAL" in settings
    assert "Lane CHa's battery run measures the chain under the draw, at `tau` = 2" in settings


def test_the_hours_carry_measured_prices_and_the_sample_is_a_constant():
    """Statistics item 8."""
    decision = _decision()
    assert "the chain search 177 s at 200,000 x 50 with exponent 1.23" in decision
    assert "the level variants and RULE W1's check are not priced" in decision
    assert "the constant `selftest_sample` of 4.6b.14" in _part("8")
    assert "l0_cut, selftest_sample}`" in _part("5")
    assert "on 3.10, 12 hours only with all three savings" not in decision


# --- the orchestrator's rulings and addendum --------------------------------


def test_lane_mrs_price_is_cited_by_a_dated_sentence():
    """The addendum of 2026-10-19, 14:11, items (a) to (d)."""
    decision = _decision()
    assert "**Row 9's one test on real shapes (lane MR, measured 2026-10-19;" in decision
    assert "in all 768 outcome classes" in decision
    assert "(5, 8 and 87 rows at 20,000 rows on the emergency, lab and stay shapes)" in decision
    assert "49.8 per cent at 20,000 rows" in decision
    assert "a later refinement, once it has a written proof and its four fixtures" in decision
    assert "scipy's HiGHS" in decision and "scipy's HiGHS" in _part("7")
    assert "which has not landed and enters here by a dated sentence" not in decision


def test_l0_is_the_ladder_the_bake_off_measured():
    """Ruling (9): lane A0a's `dec` ladder cut at the 10th, 20th, 25th, 30th,
    40th, 50th, 60th, 70th, 75th, 80th and 90th percentiles."""
    measured = {10, 20, 25, 30, 40, 50, 60, 70, 75, 80, 90}
    ladder = _part("2")
    row = ladder[ladder.index("| `count`, `continuous`;"):]
    row = row[: row.index("| `datetime` |")]
    edges = {int(p) for p in re.findall(r"`p(\d\d)`", row.split("|")[2])}
    assert edges == measured
    assert "its `dec` ladder" in _settings()


def test_the_rulings_on_the_first_build_are_recorded():
    """Rulings (1) to (3) of 2026-10-19, 12:14."""
    decision = _decision()
    assert "The orchestrator's rulings of 2026-10-19 (12:14) on this page's first build" in decision
    assert "case (ii) of Lemma 3 is confirmed as R1's reading" in decision
    assert "R3 read through a model of the key" in decision
    assert "Repair round 1 (2026-10-19)" in decision
    entry = _flat(_between(CHANGES, "### Between columns: the chain's method page", "\n### "))
    assert "The page's first review round repaired it before any code." in entry
