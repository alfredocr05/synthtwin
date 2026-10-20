"""The chain's method page holds what its two review rounds fixed (plan P4-D407).

WHY A FILE OF ITS OWN. Stage 6's first layer, the chain, is written
before its code: contract section 4.6b, the generation method's G16 and
the validation method's V12 bind lanes CHa, CHb, CHv and CHo, which have
not started, and nothing in the product reads them yet. The disposition
seal turns red on any edit of a sealed passage and is re-sealed by
whoever makes the edit, so it cannot tell a correction from its undoing.
This file can. The page's first skeptic and its statistics review of
2026-10-19 found it wrong in twenty places; every check of the first
part below is red on the page as the first build left it (e713688b) and
says which item it holds. The second round (its verify and the one
outside review, Codex's, the same day) found twenty-four more; every
check of the second part is red on the round-1 page (ff8f9a22).

WHAT IS COMPUTED HERE, NOT READ. The second round's cases are
re-derived too: the census of records holding nothing fixing a count,
a confinement through a derived family, a computed column's census
giving a count back, a stray row breaking a carried rule, the size flag
of "differs", the moved parent counts, the sample of equal rows, the
colliding separators and the whole-description digest. The first review's three probes are
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
    assert "`n_missing`" in rules and "writes EVERY other key `null`" in rules
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
    assert "no measured number stands on any line of this section" in report
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
    assert "the level variants and RULE W1's full check are not priced" in decision
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


# === The second round: the verify and Codex's review of 2026-10-19 ========


def _rules_part():
    return _part("7")


def _ledger_part():
    return _part("4")


# --- the verify, item 1: a computed column's census gave a count back -----


def test_a_computed_columns_census_gave_a_count_back_and_is_withheld():
    """Verify item 1, MEASURED again: on 1,000 rows with A absent on 15 and
    B on 20, B's numeric_styles {"integer": 980} less the derived
    column's present rows fixed "A absent, B recorded" at the truth. With
    B's block reduced to its name, place and role, that count reaches 0."""
    for overlap, truth in ((13, 2), (10, 5), (6, 9)):
        b_styles_total = 1000 - 20
        d_present = 1000 - (15 + 20 - overlap)
        assert b_styles_total - d_present == truth == 15 - overlap
        withheld_range = range(0, 15 + 1)
        assert 0 in withheld_range
    rules = _rules_part()
    assert "its block keeps `name`, `position` and `role`, and writes EVERY other key `null`" in rules
    for key in ("`numeric_styles`", "`datetime_separators`", "`n_zero`", "`integer_valued`",
                "`fraction_widths`", "`utc_offsets`", "`resolution_mix`", "`layout_forms`"):
        assert key in rules, key
    assert "among them P1 and P3 (`numeric_styles`), D13 (`datetime_separators`), SF3 (`shape_forms`), and LF3 and LF4" in rules
    assert "Its block publishes its role, its layout and its written forms" not in rules
    assert "checked key by key over section 5.1 and the role's keys of section 6.11, never against a list" in _part("11")
    assert "since a computed `B` publishes nothing read from its cells but its role" in _part("9")
    assert '`numeric_styles` `{"integer": 980}` published' in _part("10")


def test_a_computed_columns_words_would_tell_a_failing_row():
    """Verify item 1, the part the verify left: with A and a source D whole
    numbers, B is fractional only where B differs from A + D, a failing
    row, so B's integer_valued false would put the phrase's count in
    1 to f - 1."""
    rows = [(a, d, a + d) for a, d in zip(range(30), range(30, 60))]
    rows[4] = (4, 34, 4 + 34 + 0.5)
    rows[9] = (9, 39, 9 + 39 + 0.5)
    fractional = [b for a, d, b in rows if b != int(b)]
    failing = [b for a, d, b in rows if b != a + d]
    assert 0 < len(fractional) <= len(failing) <= FLOOR - 1
    assert "Why the words go: with `A` and a source `D` publishing `integer_valued` true" in _rules_part()


# --- the verify, item 2: a stray row took a computed column's cell --------


def _breaking(rows):
    broken = 0
    for row in rows:
        a, b, d = row["A"], row["B"], row["D"]
        if a is not None and d is not None:
            broken += b != a + d
        elif b is not None:
            broken += 1
    return broken


def test_a_stray_row_takes_no_cell_of_a_computed_column():
    """Verify item 2, MEASURED again on its four rows: G2.1's second walk
    moving the computed B's cell onto the stray row breaks B = A + D on
    two rows; with no column a rule computes or reads as a giver, the
    stray row stays and nothing breaks."""
    rows = [
        {"A": 10, "B": 13, "C": 1, "D": 3},
        {"A": 20, "B": 21, "C": 2, "D": 1},
        {"A": 30, "B": 35, "C": None, "D": 5},
        {"A": None, "B": None, "C": None, "D": None},
    ]
    assert _breaking(rows) == 0
    moved = [dict(row) for row in rows]
    moved[3]["B"], moved[0]["B"] = moved[0]["B"], None
    assert _breaking(moved) == 2
    method = _g16()
    assert "GIVERS taken only from the INELIGIBLE columns that no carried rule computes or reads" in method
    assert "and never from the row-sequence column" in method
    assert "9b. a stray row beside a computed column" in method
    assert "breaks `B = A + D` on 2 rows" in method
    assert "given cells only by ineligible columns that no carried rule computes or reads, never by the row sequence" in _decision()
    assert "an ineligible column that no carried rule computes or reads, every family HELD" in _v12()


# --- the verify, item 3, and Codex's items 6 and 7: what V12 prints --------


def test_differs_with_no_number_was_a_size_flag():
    """Verify item 3, MEASURED again: printing a difference only where it
    is nought or at least f made 'differs, no number' stand exactly for a
    difference of 1 to f - 1; and on a two-by-two table beside a margin of
    f, 'MISSED alone' stood exactly for a free cell of 1 to f - 1."""
    published = 500
    flagged = [
        measured for measured in range(400, 601)
        if measured != published and abs(measured - published) < FLOOR
    ]
    assert flagged == list(range(490, 500)) + list(range(501, 511))
    margin = FLOOR
    alone = [cell for cell in range(margin + 1) if any(0 < c < FLOOR for c in (cell, margin - cell))]
    assert alone == list(range(1, FLOOR))
    report = _v12()
    assert "no measured number stands on any line of this section" in report
    assert "a band total off by 3 and one off by 30 print the same line" in report
    assert "two files whose band totals differ from the published ones by 3 and by 30 rows, whose lines print the same words" in report
    assert "otherwise the line says only that the total differs" not in report


def test_a_verdict_stands_only_where_the_files_own_description_allows():
    """Codex's items 6 and 7: printed cells of [[50, 0], [0, 50]] fixed a
    group of five rows beside B's first band, a family RULE W1 refuses on
    that file; and a moved target with a cell of ten read HELD and MISSED."""
    group = 5
    measured = [[50, 0], [0, 50]]
    published = [[25, 25], [25, 25]]
    admitted_measured = [band for band, cell in enumerate(measured[0]) if cell]
    admitted_published = [band for band, cell in enumerate(published[0]) if cell]
    assert admitted_measured == [0] and admitted_published == [0, 1]
    fixed = {min(group, measured[0][0]) if len(admitted_measured) == 1 else None}
    assert fixed == {5}
    report = _v12()
    assert "a verdict is a statement about the measured file (V5.3), so it is printed only where the file's own description lets it stand" in report
    assert '"not judged: the file\'s band totals differ from the published ones"' in report
    assert "the verdict is the check's result" in report
    assert "`[[45, 10], [0, 45]]`" in report
    assert "The validator computes no moved table" in report
    assert "re-derives from the published table and the file's own totals, and from nothing else" not in report
    assert "compared cell for cell with the PUBLISHED table" in _part("12")


# --- Codex's item 1: the census of records holding nothing ----------------


def _codex_census_case(empty_cell_free):
    """Every table of three presence columns over 100 tabled rows with
    AB = [[22, 22], [28, 28]] and C | B = [[22, 28], [22, 28]]; the count
    of rows with A and C recorded and B blank, over all of them."""
    counts = set()
    for blank in range(0, 23):
        if not empty_cell_free and blank != 0:
            continue
        for other in range(0, 23):
            cells = {
                "000": blank, "001": 22 - blank, "100": 22 - blank, "101": 6 + blank,
                "010": other, "011": 22 - other, "110": 22 - other, "111": 6 + other,
            }
            if min(cells.values()) < 0:
                continue
            ab = [[cells["000"] + cells["001"], cells["010"] + cells["011"]],
                  [cells["100"] + cells["101"], cells["110"] + cells["111"]]]
            cb = [[cells["000"] + cells["100"], cells["001"] + cells["101"]],
                  [cells["010"] + cells["110"], cells["011"] + cells["111"]]]
            assert ab == [[22, 22], [28, 28]] and cb == [[22, 28], [22, 28]]
            counts.add(cells["101"])
    return counts


def test_the_census_of_empty_records_fixes_a_count_without_rule_we():
    """Codex's item 1, enumerated: 133 rows, 33 records holding nothing
    published (11 leading, 11 interior, 11 trailing), so no tabled row is
    blank in all three columns; the tables alone leave the count from 6
    to 28, the census fixes it at 6. RULE WE refuses the root pair: the
    cell bound of the all-blank cell is 22, the census and the other
    columns allow 0."""
    assert _codex_census_case(empty_cell_free=True) == set(range(6, 29))
    assert _codex_census_case(empty_cell_free=False) == {6}
    line = max(2, FLOOR)
    published = [11, 11, 11]
    z = sum(line - 1 for count in published if count == 0)
    p = 0
    bound = min(22, 22, 44, 50, 44, 100)
    assert z + p == 0 and bound == 22 and bound > z + p
    search = _part("3")
    assert "**RULE WE (the records holding nothing;" in search
    assert "only where, with it placed, the cell bound `b(x0)` (4.6b.9 (a)) is at most `Z + P`" in search
    assert "so it removes none" not in search
    assert "the census removes none" in _part("9")
    assert "| 5a | RULE WE |" in _section()
    assert "Codex's 133-row table of three columns with 33 records holding nothing published" in _part("10")
    assert "RULE WE's from the published counts" in _part("11")


# --- Codex's item 2: W1 checked in full ------------------------------------


def test_w1_checked_in_full_refuses_a_confinement_through_a_derived_family():
    """Codex's item 2: C's first band (its six absent cells merged in)
    admits A at 0 and 2, two bands of A's L2, so the shortcut passes; but
    D | A sends both to D's first band, so C's first band admits one band
    of D and "the six AND D below 15" is fixed at 6."""
    d_given_a = [[25, 0], [0, 25], [25, 0], [0, 25]]
    a_given_c = [[25, 0, 25, 0], [0, 25, 0, 25]]
    a_l2 = {0: 0, 1: 0, 2: 1, 3: 1}
    admitted_a = [a for a, cell in enumerate(a_given_c[0]) if cell]
    assert sorted({a_l2[a] for a in admitted_a}) == [0, 1]
    admitted_d = sorted({d for a in admitted_a for d, cell in enumerate(d_given_a[a]) if cell})
    assert admitted_d == [0]
    six_and_low = {6} if admitted_d == [0] else set(range(0, 7))
    assert six_and_low == {6}
    search = _part("3")
    assert "W1 is checked IN FULL for every option of every step" in search
    lemma = _proof("c", "d")
    assert "*W1 is checked in full at every step*" in lemma
    assert "*Adding a family never narrows an earlier support,* so W1 is checked at each step only" not in lemma
    assert "Codex's 100-row derived-family case of 4.6b.9 (c), where W1 checked in full" in _part("10")


# --- Codex's item 3: what the twin can keep --------------------------------


def test_only_a_derived_carrier_takes_a_count_class():
    """Codex's item 3: B written as A + D breaks a source-carried identity
    on no row, so a count class of twelve could not be met; and six
    negative readings of a source D beside a present A break the order on
    six twin rows."""
    real = [(a, 5, a + 5 + (1 if a < 12 else 0)) for a in range(100)]
    twin = [(a, d, a + d) for a, d, _ in real]
    assert sum(b != a + d for a, d, b in real) == 12
    assert sum(b != a + d for a, d, b in twin) == 0
    negatives = [(a, -1 if a < 6 else 3) for a in range(40)]
    assert sum(a + d < a for a, d in negatives) == 6
    rules = _rules_part()
    assert "a SOURCE carrier and a formula rule read the PHRASE-ONLY partition alone" in rules
    assert "A source `D` is offered only where its own block publishes `n_negative` 0" in rules
    assert "MR's page writes how the twin treats the rows where a source `D` is negative" not in rules
    assert "or a count from `settings.small_cell_floor` up where its `carrier` is `derived`" in _part("11")


# --- Codex's item 4: no family at the root with a rule carried -------------


def test_a_root_without_a_family_keeps_the_carried_rules():
    search = _part("3")
    assert "RULES-ONLY description" in search
    assert "places nothing: the description then holds no chain, and `statistical` is `null`." not in search
    assert "Where fewer than two columns are eligible, \"no family\" is the root step's only option." in search
    assert "`statistical` is `null` only where the root step drew \"no family\" and no rule is carried" in _part("11")
    method = _g16()
    assert "A RULES-ONLY description (contract 4.6b.3" in method
    assert "12. a RULES-ONLY description" in method


# --- Codex's item 5: joint parent counts -----------------------------------


def _moved(published, rows, columns):
    """G16.6 by enumeration: fewest units in published noughts, then the
    distance, then its squares, then the greatest in row-major order."""
    best = None

    def fill(index, remaining, cells):
        nonlocal best
        if index == len(rows):
            if all(r == 0 for r in remaining):
                flat = [c for row in cells for c in row]
                pub = [c for row in published for c in row]
                key = (
                    sum(c for c, q in zip(flat, pub) if q == 0),
                    sum(abs(c - q) for c, q in zip(flat, pub)),
                    sum((c - q) * (c - q) for c, q in zip(flat, pub)),
                    [-c for c in flat],
                )
                if best is None or key < best[0]:
                    best = (key, [list(row) for row in cells])
            return
        width = len(columns)
        for head in itertools.product(*(range(min(rows[index], r) + 1) for r in remaining[:-1])):
            last = rows[index] - sum(head)
            if last < 0 or last > remaining[-1]:
                continue
            row = list(head) + [last]
            fill(index + 1, [r - c for r, c in zip(remaining, row)], cells + [row])
        assert width == len(remaining)

    fill(0, list(columns), [])
    return best[1]


def test_a_moved_target_propagates_through_joint_parent_counts():
    """Codex's item 5: A and C keep their totals while their joint cells
    move, so a later family read on its members' totals alone takes a
    published table the twin's parent cells cannot hold."""
    ab = _moved([[60, 40], [40, 60]], [100, 100], [80, 120])
    assert ab == [[50, 50], [30, 70]]
    c_given_ab = _moved([[60, 0], [0, 40], [0, 40], [60, 0]], [50, 50, 30, 70], [120, 80])
    assert c_given_ab == [[50, 0], [0, 50], [0, 30], [70, 0]]
    joint = [c_given_ab[0][0] + c_given_ab[1][0], c_given_ab[0][1] + c_given_ab[1][1],
             c_given_ab[2][0] + c_given_ab[3][0], c_given_ab[2][1] + c_given_ab[3][1]]
    assert joint == [50, 50, 70, 30]
    later = [[30, 30], [20, 20], [30, 30], [20, 20]]
    assert [sum(row) for row in later] == [60, 40, 60, 40] != joint
    method = _g16()
    assert "the twin's count of each of the family's parent cells, as the families before it placed them" in method
    assert "The published table where every member's band totals in the twin equal the published ones" not in method
    assert "10. a moved parent count" in method


# --- Codex's item 8: the self-test's sample of equal rows ------------------


def _framed(cells):
    data = b""
    for name, text in cells:
        for part in (name.encode("utf-8"), text.encode("utf-8")):
            data += len(part).to_bytes(8, "big") + part
    return hashlib.blake2b(data, digest_size=32, person=b"synthtwin.row.1").digest()


def _separated(cells):
    data = b""
    for name, text in cells:
        data += name.encode("utf-8") + b"\x1f" + text.encode("utf-8") + b"\x1e"
    return hashlib.blake2b(data, digest_size=32, person=b"synthtwin.row.1").digest()


def test_the_sample_takes_exactly_its_rows_however_many_repeat():
    """Codex's item 8: under the first build's cut both rows of a table of
    500,000 `0,0` beside 500,000 `1,1` fall above it, so the sample was
    empty. Keyed by content and occurrence, the smallest keys take exactly
    m rows and about half of each (shown at a smaller size)."""
    first = [("a", "0"), ("b", "0")]
    second = [("a", "1"), ("b", "1")]
    rows, wanted = 1_000_000, 200_000
    old_taken = [
        int.from_bytes(_separated(row)[:8], "big") * rows < wanted * 2**64 for row in (first, second)
    ]
    assert old_taken == [False, False]
    copies, size = 2000, 400
    keys = []
    for label, row in (("first", first), ("second", second)):
        content = _framed(row)
        for occurrence in range(copies):
            key = hashlib.blake2b(
                content + occurrence.to_bytes(8, "big"), digest_size=8, person=b"synthtwin.smp.1"
            ).digest()
            keys += [(key, content, occurrence, label)]
    taken = sorted(keys)[:size]
    assert len(taken) == size
    share = sum(1 for item in taken if item[3] == "first")
    assert 150 < share < 250
    sample = _part("8")
    assert "Each row's SAMPLE KEY is BLAKE2b" in sample
    assert "It holds exactly `min(m, n)` rows, never none and never more." in sample
    assert "a row is sampled where `u * n < m * 2**64`" not in sample


# --- Codex's item 9: the whole description, and one run at a time --------


def test_the_ledger_digests_the_whole_description_and_holds_a_lock():
    """Codex's item 9: at floors 11 and 12 a statistical object can come
    out the same while the column blocks move; a digest of statistical
    alone then sees one description."""
    statistical = {"chain": [{"child": "age", "table": [[40, 60]]}]}
    at_11 = {"settings": {"small_cell_floor": 11}, "columns": [{"levels": {"x": 11}}],
             "relationships": {"statistical": statistical}, "producer": {"version": "1"}}
    at_12 = {"settings": {"small_cell_floor": 12}, "columns": [{"levels": {"(withheld)": 11}}],
             "relationships": {"statistical": statistical}, "producer": {"version": "2"}}

    def digest(value):
        text = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.blake2b(text.encode("utf-8"), digest_size=32, person=b"synthtwin.desc.1").digest()

    def protected(description):
        return {k: v for k, v in description.items() if k != "producer"}

    assert digest(at_11["relationships"]["statistical"]) == digest(at_12["relationships"]["statistical"])
    assert digest(protected(at_11)) != digest(protected(at_12))
    ledger = _ledger_part()
    assert "over the PROTECTED PUBLICATION, which is the whole description as written" in ledger
    assert "over the bytes of the description's `relationships.statistical` object as written" not in ledger
    assert "`O_CREAT | O_EXCL`" in ledger
    assert "The ledger entry is written first" in ledger
    assert "one table described at floors 11 and 12 whose `statistical` object comes out the same" in _part("10")


# --- Codex's items 10, 11, 13, 14 and 16: wording the review asked for ----


def test_the_rule_steps_option_order_is_total():
    """Codex's item 10."""
    draw = _ledger_part()
    assert "a step of kind `rule`: \"not carried\" first, then each source carrier by the carrier column's place in schema order" in draw


def test_a_reading_map_marks_the_rows_without_a_reading():
    """Codex's item 11: every byte is a code some reading takes, so no
    value code can mark an absent cell merged into an ordered band."""
    lo, hi = Fraction(0), Fraction(1000)
    codes = {
        min(255, max(0, (256 * (Fraction(x, 10) - lo)) // (hi - lo))) for x in range(0, 10001)
    }
    assert codes == set(range(256))
    method = _g16()
    assert "**the READING MAP**" in method
    assert "whose reading map for `p` is set" in method
    assert "11. five absent cells merged with 95 readings" in method
    assert "is marked by its band code and reads no value code" not in method


def test_the_twins_deviations_and_its_grades_are_stated():
    """Codex's items 13 and 14."""
    reports = _part("8")
    assert "**The twin's DEVIATIONS**" in reports
    assert "**A grade `E` is owed only where the twin met the family's published table.**" in reports
    assert '"moved in this twin"' in reports
    assert "validation's V12 re-derives the moved table" not in _g16()


def test_a_floor_change_keeps_every_word():
    """Codex's item 16: the floor is not an input of a word."""
    key = bytes(range(32))
    columns = ["age", "group", "stay"]
    assert _word(key, "clinic", "place", 3, columns) == _word(key, "clinic", "place", 3, list(columns))
    draw = _ledger_part()
    assert "another floor or another `procedure` constant leaves every word as it was" in draw.replace("Another", "another")
    assert "another floor, or another constant changes every word" not in draw


# --- Codex's item 12: a slope's error where nothing varies ------------------


def test_a_slope_parent_that_does_not_vary_has_no_error():
    """Codex's item 12: two tight clusters coded 0 and 255, each its own
    cell at L2, leave a within-cell sum of squares of nought."""
    lower = [Fraction(10 + k, 100) for k in range(20)]
    upper = [Fraction(900 + k, 100) for k in range(20)]
    lo, hi = Fraction(3, 10), Fraction(9, 1)

    def code(x):
        return min(255, max(0, (256 * (x - lo)) // (hi - lo)))

    def sum_of_squares(values):
        mean = Fraction(sum(values), len(values))
        return sum((v - mean) * (v - mean) for v in values)

    cells = [[code(x) for x in lower], [code(x) for x in upper]]
    assert {code(x) for x in lower} == {0} and {code(x) for x in upper} == {255}
    assert sum(sum_of_squares(cell) for cell in cells) == 0
    report = _v12()
    assert "not measured on this file" in report
    assert "two parents the first determines" in report


# --- Codex's item 15: separators inside a cell ------------------------------


def test_separator_bytes_inside_a_cell_collide_and_framing_does_not():
    first = [("A", "x\u001eB\u001fy"), ("B", "z")]
    second = [("A", "x"), ("B", "y\u001eB\u001fz")]
    assert _separated(first) == _separated(second)
    assert _framed(first) != _framed(second)
    assert "a LENGTH-FRAMED encoding, which no text can imitate" in _part("8")


# --- the verify, items 4 to 8 ------------------------------------------------


def test_the_addendum_of_19_04_is_written_with_its_measurements():
    """Verify item 4: the orchestrator's addendum 2 (lib-study, 19:04)."""
    search = _part("3")
    assert "The screen's seeds are OFFERED to the draw as weights, never forced" in search
    assert "a FINER-CODED screen, which changes weights only" in search
    assert "class M-d" in search
    settings = _settings()
    assert "the three-way xor went from 85.90 and 173.88 SE off to 0.00" in settings
    assert "ranks 187 to 190 of 19,600 triples on its coarse codes" in settings
    assert "A larger `k` is NOT a lever for interactions" in settings
    assert "diabetes x current smoker 7.72 SE at each" in settings
    assert "`A0b`'s 200,000-row legs still decide them" in settings
    decision = _decision()
    assert "a larger `k` is NOT an interaction lever: `k` = 3, 4 and 5 leave the same gaps" in decision
    assert "from 86 and 174 SE off (50,000 and 200,000 rows) to 0.00" in decision


def test_lane_mrs_inference_conditions_are_an_open_precondition():
    """Verify item 5."""
    scope = _proof("h", "zz")
    assert "proven on one PRECONDITION, open until lane MR's page proves it" in scope
    assert "**Open preconditions:**" in scope
    assert "PRECONDITION, open until lane MR's page proves it" in _section()
    assert "on one PRECONDITION, open until lane MR's page proves it" in _decision()


def test_the_ledger_writes_its_two_missing_branches():
    """Verify item 6."""
    ledger = _ledger_part()
    assert "**a key file but no ledger** (the ledger deleted or lost): the run proceeds, starts a new ledger" in ledger
    assert "**a ledger that cannot be read**" in ledger
    assert "a deleted or lost ledger beside a kept key" in _part("13")


def test_a_renamed_column_is_another_table_to_the_ledger():
    """Verify item 7: the content hash reads cells keyed by column name."""
    assert _framed([("age", "40")]) != _framed([("age_years", "40")])
    limits = _part("13")
    assert "a copy with a column renamed, added or dropped" in limits
    assert "with the same columns under the same names" in limits
    assert "with the same columns under the same names, a copy with a column renamed, added or dropped being described as another table" in _part("8")


def test_the_hours_follow_the_owners_python_floor():
    """Verify item 8: the owner's floor of 2026-10-19 (19:00), 3.11."""
    promised = _part("13")
    assert "the oldest Python synthtwin runs on is 3.11" in promised
    assert "11.2 on Python 3.10 with the two savings that remain, under one hour" not in promised
    assert "the lever behind the Python 3.10 hours" not in _settings()
    decision = _decision()
    assert "the oldest supported Python (3.11, from lane DEP-1) measured once" in decision
    assert "Python 3.10 measured once" not in decision


def test_the_second_round_is_recorded():
    decision = _decision()
    assert "**Repair round 2 (2026-10-19)" in decision
    assert "**Codex's sixteen items on this page, answered" in decision
    entry = _flat(_between(CHANGES, "### Between columns: the chain's method page", "\n### "))
    assert "A second review round, with one outside review, repaired it again." in entry
