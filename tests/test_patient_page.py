"""The patient page holds what its first review round fixed (plan P4-D412).

WHY A FILE OF ITS OWN. Stage 6's patient layer is written before its
code: contract section 4.6c, the generation method's G16.13 to G16.17
and the validation method's V12.7 to V12.9 bind lanes GR, CHa, CHb,
CHv and CHo, which have not started, and nothing in the product reads
them yet. The disposition seal turns red on any edit of a sealed passage
and is re-sealed by whoever makes the edit, so it cannot tell a
correction from its undoing (the page's first skeptic changed SWING's
"+ 2" to "+ 20", re-sealed, and 108 checks stayed green). This file can.
The page's first skeptic and its statistics review of 2026-10-20 found
it wrong in twenty-two places; each check below is red on the page as
its first build left it (853f442c) or on the mutant its docstring names,
and says which item it holds.

WHAT IS COMPUTED HERE, NOT READ. The cap lemma's refused band (20
patients, 30 extra rows, no floored split), the first skeptic's leaking
class description (22 patients of two rows, 13 and 31 rows in two
bands: the class fixes a count, and no floored world keeps the class),
the slice lemma's walk stalling at a one-code band with wider bands
before and after it (and not stalling without one after it), and the
position list rebuilt from its tie world. The rest pins wording, where
the finding was a missing or wrong sentence.

THE SECOND ROUND. The page's verify and one Codex review of 2026-10-20
found a guard that guarded nothing on the product's block (the exact mean
and the tails fix a column's code total whatever min and max say), the
moments candidate of the orchestrator's addendum unnamed, fourteen of the
first round's guards held by no check, and sixteen defects of
definition, scale and arithmetic. The checks after the marked line hold
each, computing what can be computed (the code total from the mean and
the tails, the one-cell pigeonhole, Codex's 248-patient count, the
deficit search against the full one, the census draw's chance of "off").

THE SECOND VERIFY. It found the moments candidate recorded as not
measured although the design study's run 3c had measured it (the
orchestrator's ADDENDUM 3 rules it measured and not adopted), lane ST
still told "trend flat", and eight repaired rules held by no check; the
orchestrator's ADDENDUM 4 adds the complete-follow-up limit in plain
words. The checks naming the second verify or ADDENDUM 4 hold each,
computing the exact sum of squares' pin on run 3c's smallest fixture,
PWIT's 22 patients and the empty outside of a complete follow-up table.

WHAT IS NOT HERE. No patient-layer code exists to run, so nothing here
says a twin meets a census or a trend. `K-S6-08`'s enumeration and the
oracle's cases (G16.17) are where lanes CHa, GR and CHo run the method.
"""
import itertools
import pathlib

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
CONTRACT = REPOSITORY / "docs" / "spec" / "profile-contract-v6.md"
METHOD = REPOSITORY / "docs" / "spec" / "generation-method-v1.md"
PLAN = REPOSITORY / "docs" / "plans" / "phase-4-columns.md"
CHANGES = REPOSITORY / "CHANGELOG.md"
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


def _section():
    return _between(CONTRACT, "### 4.6c `relationships.grain`", "<!-- s5: the column block")


def _part(number):
    text = _section()
    at = text.index("#### 4.6c." + number + " ")
    stop = text.find("\n#### 4.6c.", at + 10)
    return _flat(text[at:] if stop < 0 else text[at:stop])


def _setting():
    text = _section()
    return _flat(text[: text.index("#### 4.6c.1 ")])


def _g16():
    return _flat(_between(METHOD, "### G16.13 ", "### G16.17 "))


def _g16_cases():
    return _flat(_between(METHOD, "### G16.17 ", "## Conformance checklist"))


def _decision():
    return _flat(_between(PLAN, "## Decision P4-D412"))


def _entry():
    return _flat(_between(CHANGES, "### Between columns: the patient page", "\n### "))


# --- the trend: Q, never S; SWING's two conditions ------------------------


def test_the_trend_publishes_q_and_never_s_exact():
    """The orchestrator's ruling of 2026-10-20: Q only; under S exact SWING
    passes 220 leaking descriptions. Mutant: 'is never published' -> 'is
    published'."""
    part = _part("1")
    assert "Q_P = floor(S_P / 2)" in part
    assert "**`S` exact is never published.**" in part
    assert "220 leaking descriptions" in part


def test_swing_reads_both_conditions_with_their_constants():
    """The skeptic's own mutant ('+ 2' -> '+ 20') left 108 checks green."""
    part = _part("1")
    assert "(i) `|S|max <= cap_b(P) - f (max b_c + K W+(r))`" in part
    assert "(ii) `max (a_c + b_c) <= cap_g(P) - f max (b_c - a_c) + 2`" in part
    assert "`W+(r) = floor(r^2 / 4)`" in part


def _walk_stalls(bounds):
    """The slice lemma's walk: from the greedy minimum, move one code unit from
    a position to the next while some move keeps every position in its band;
    returns (reached S, greedy maximum S)."""
    r = len(bounds)
    w = [2 * j - r + 1 for j in range(r)]
    total = sum(lo for lo, hi in bounds) + 2
    codes = [lo for lo, hi in bounds]
    rest = total - sum(codes)
    for j in range(r):
        add = min(rest, bounds[j][1] - codes[j])
        codes[j] += add
        rest -= add
    maximum = [lo for lo, hi in bounds]
    rest = total - sum(maximum)
    for j in range(r - 1, -1, -1):
        add = min(rest, bounds[j][1] - maximum[j])
        maximum[j] += add
        rest -= add
    moved = True
    while moved:
        moved = False
        for j in range(r - 1):
            if codes[j] > bounds[j][0] and codes[j + 1] < bounds[j + 1][1]:
                codes[j] -= 1
                codes[j + 1] += 1
                moved = True
                break
    return sum(a * b for a, b in zip(w, codes)), sum(a * b for a, b in zip(w, maximum))


def test_a_one_code_band_between_wider_ones_reads_rigid_and_the_rule_says_before_and_after():
    """Skeptic 1, item 12: 'between' must mean a wider band somewhere before
    AND somewhere after, not only next to it. Computed: the walk stalls short
    of the greedy maximum with a one-code band between wider bands (two
    one-code positions in a row too), and reaches it when no wider band
    follows. Mutant: the first build's 'between two positions whose bands hold
    more'."""
    reached, top = _walk_stalls([(0, 2), (3, 3), (4, 6)])
    assert reached < top
    reached, top = _walk_stalls([(0, 2), (3, 3), (4, 4), (5, 7)])
    assert reached < top
    reached, top = _walk_stalls([(0, 2), (3, 5), (6, 6)])
    assert reached == top
    part = _part("1")
    assert "somewhere BEFORE it and somewhere AFTER it (not only next to it" in part
    assert "between two positions whose bands hold more" not in part


def test_the_trend_stands_only_where_no_published_fact_fixes_its_cells_code_total():
    """Skeptic 1, item 2: the exact mean fixes a cell's code total where every
    reading sits on the grid inside [p01, p99] and the cells hold every row;
    Q beside it gives S. Mutant: item (b) 6 dropped, or S33 not checking it."""
    part = _part("1")
    assert "6. **The unpinned total (the exact mean's guard; rewritten by the page's verify" in part
    assert "the published `min` is below `p01` or the published `max` above `p99`" not in part
    assert "`Q_P` is ELIGIBLE when SWING passes, item 6 holds" in part
    assert "873 descriptions SWING passed leak because `Q` stands beside the total" in part
    assert "(4.6c.1 (b) 6; no rule reads `min` or `max`); the loader recomputes SWING" in _part("10")
    assert "``MEAN" not in part
    assert "passes NO description of the fifteen fixtures" in part
    limits = _part("11")
    assert "9. **Counts of patients by their exact readings beside a trend or an own-mean parent**" in limits
    assert "125 to 136 on `F3`" in limits


def test_each_proof_states_its_objects():
    """The orchestrator's ruling of 2026-10-20 10:22, item 3: each proof's
    stated objects, pinned where they stand. Mutant: any one heading removed."""
    text = _flat(_section())
    for words in (
        "**The one-world lemma.** *If some world of the preimage gives every union of a set of types a count of 0 or at least `f`, no union of those types leaks.*",
        "1. **The slice lemma.**",
        "2. **The sign-flip chain.**",
        "3. **The witness worlds keep the cell's trend.**",
        "*Proof that an eligible census leaves every count of `r` 0-able or f-able, for a reader knowing any true cap.*",
        "*The cap lemma.*",
        "**Step 3: one value of `r` in a parent cell: PWIT in closed form.**",
        "3. THE TIE:",
        "Consider the TIE WORLD",
        "**(e) The class witness",
        "*Under the floored split*",
    ):
        assert words in text, words


# --- the gate ---------------------------------------------------------------


def test_the_gate_draws_off_on_every_table_and_reads_no_exact_census():
    """Skeptic 1, item 5: the first build's OFF proof read the person
    column's exact multiset, which plan P4-D406 pools. Mutant: item 4 back to
    'at least one candidate census of 4.6c.4 is eligible'."""
    gate = _part("3")
    assert "1. `settings.person_columns` names exactly ONE column" in gate
    assert "2. no tabled row lacks a person value" in gate
    assert "3. the extra rows `xr = n - N` are at least `f`" in gate
    assert 'AND "off" (always eligible, scored 0), does not draw "off"' in gate
    assert "at least one candidate census of 4.6c.4 is eligible" not in gate
    assert "the OFF description reads nothing of the exact census" in gate
    census = _part("4")
    assert '"off", always eligible and scored 0, which turns the layer off' in census


def test_the_two_new_gate_conditions_are_priced_on_the_zoo():
    """The orchestrator's ruling of 2026-10-20 10:22, item 4: their price on
    the health zoo's 25 tables. Mutant: the first build's 'JUDGEMENT-priced'."""
    gate = _part("3")
    assert "turn OFF NONE of the 25" in gate
    assert "JUDGEMENT-priced" not in gate


def test_while_on_the_person_census_is_null_and_n_present_stays_rows():
    """Skeptic 1, item 13: the first build moved every row-counting key,
    n_present included, while I2 and S29 read the census rows as n."""
    gate = _part("3")
    assert "the person column's `n_distinct_by_occurrences` is `null`" in gate
    assert "One key is NOT moved: `n_present` stays the count of tabled rows" in gate
    assert "counts rows but `n_present` is counted over the patient table" in _part("10")


# --- the census -------------------------------------------------------------


def _floored_split_exists(m, q, top):
    for counts in itertools.product(range(m + 1), repeat=top + 1):
        if sum(counts) != m or sum(v * c for v, c in enumerate(counts)) != q:
            continue
        if all(c == 0 or c >= FLOOR for c in counts):
            return True
    return False


def test_the_census_takes_the_tight_cap_and_refuses_the_cap_lemmas_band():
    """t = ceil(q / m); computed: 20 patients with 30 extra rows, each at most
    2, admit no floored split, as the page says."""
    census = _part("4")
    assert "`t = ceil(q / m)`" in census
    assert "every `d_i <= min(t, D / f)`" in census
    assert not _floored_split_exists(20, 30, 2)
    assert _floored_split_exists(22, 33, 2)


# --- the classes: the class witness ------------------------------------------


def _class_preimage(patients, rows_a, rows_b, t):
    """Every (both rows in A, both in B, one in each) a table of two-row
    patients may hold beside the class `repeated` (V and V_K above T)."""
    out = []
    for a in range(patients + 1):
        for b in range(patients + 1 - a):
            c = patients - a - b
            if 2 * a + c == rows_a and 2 * b + c == rows_b and a + b >= t + 1 and c >= t + 1:
                out += [(a, b, c)]
    return out


def test_the_class_beside_a_row_family_fixed_a_count_and_the_witness_refuses_it():
    """Skeptic 1, item 1, computed: 22 patients of two rows, 13 and 31 rows
    in two bands, T = 10: the class fixes 'both rows in the first band' at 1;
    no floored world keeps the class, so the class witness refuses it.
    Mutant: the witness's V clause dropped."""
    worlds = _class_preimage(22, 13, 31, 10)
    assert worlds == [(1, 10, 11)]
    floored = [w for w in worlds if all(v == 0 or v >= FLOOR for v in w)]
    assert floored == []
    fixed = _part("5")
    assert "**(e) The class witness" in fixed
    assert "at least `T + 1` patients holding one level on two rows (`V`)" in fixed
    assert "at least `T + 1` holding two different levels (`V_K`)" in fixed
    assert "330 of 4,768" in fixed
    assert "the column is drawn HELD" in fixed


def test_t_reads_n2_only_where_the_census_publishes_it():
    """Skeptic 1, item 6: with lo = 1 the census is one open band."""
    fixed = _part("5")
    assert "where `lo = 1` the census is one open band, `N2` is not published, and `T = f - 1`" in fixed


def test_the_price_of_t_is_stated_at_its_largest():
    """Statistics skeptic, item 6: T reaches 141 on ST2 at 100,000 rows."""
    assert "141 on the design's `ST2` at 100,000 rows" in _part("5")
    assert "up to `T = max(f - 1, floor(N2 / 100))` patients' repeats" in _part("6")


# --- the position list ---------------------------------------------------------


def _tie_world(census_positions, entries):
    """Rebuild the list from 4.6c.6 (d)'s tie world: a listed entry on every
    patient at its position; a null one split into a tie of fresh values."""
    fresh = itertools.count(1000)
    rows = {}
    for j, (holders, entry) in enumerate(zip(census_positions, entries)):
        if entry is not None:
            rows[j] = [entry] * holders
        else:
            half = holders // 2
            first, second = next(fresh), next(fresh)
            rows[j] = [first] * half + [second] * half + ([next(fresh)] if holders % 2 else [])
    rebuilt = []
    used = set()
    for j in range(len(entries)):
        counts = {}
        for v in rows[j]:
            counts[v] = counts.get(v, 0) + 1
        best = max(counts.values())
        top = [v for v, k in counts.items() if k == best]
        value = top[0]
        if best < FLOOR or len(top) > 1 or value in used:
            rebuilt += [None]
        else:
            rebuilt += [value]
            used.add(value)
    return rebuilt, rows


def test_the_position_list_runs_to_l_and_its_tie_world_rebuilds_it():
    """Skeptic 1, item 3: the first build's all-modal world was not in the
    preimage. Computed: the tie world rebuilds a list with null entries, and
    no patient holds a value twice. Mutant: the first build's end rule."""
    positions = [40, 33, 25, 25, 18]
    entries = ["baseline", None, "week 4", None, "week 12"]
    rebuilt, rows = _tie_world(positions, entries)
    assert rebuilt == entries
    for patient in range(min(positions)):
        held = [rows[j][patient] for j in range(len(positions))]
        assert len(held) == len(set(held))
    part = _part("6")
    assert "The list runs to `L`; it has no end rule." in part
    assert "two or more values tie for the most patients at `j` (no order breaks a tie)" in part
    assert "the list ENDS before" not in part
    assert "Consider the TIE WORLD" in part


def test_no_date_and_no_fine_number_is_position_like():
    """Skeptic 1, item 6: a dealt date was 'not position-like' while the KEY
    test skipped dealt dates."""
    assert "the KEY test of 4.6c.6 never reads a date-role column, so no date is position-like" in _setting()
    part = _part("6")
    assert "A FINE number column, a column of a date role and a column with no ladder" in part


# --- the row families ----------------------------------------------------------


def test_cells_that_pool_or_hold_an_r_band_take_the_floored_split_and_the_cross_is_proven():
    """Skeptic 1, item 4. Mutant: the first build's 'CHECKED, NOT PROVEN'
    sentence for the cross in r-band and pooled cells."""
    rows = _part("8")
    assert "wherever a parent cell joins two or more grain cells or a grain cell holds a band of `r`" in rows
    assert "*Under the floored split*" in rows
    assert "f-able is CHECKED, NOT PROVEN" not in rows
    assert "a union of patient-level cells crossed with a union of types is 0-able or f-able.*" in rows


def test_the_own_means_exemption_from_the_difference_test_is_argued():
    """Skeptic 1, item 14."""
    assert "The own mean takes no such test, and needs none" in _part("2")


def test_every_patient_level_cell_is_floored_and_a_case_holds_it():
    """Statistics skeptic, item 1 (d); the orchestrator's ruling of 10:41,
    item 4."""
    assert "*Every cell of the families holding a derived column is floored.*" in _part("2")
    cases = _part("10")
    assert "a coarser option published, never the cell" in cases
    assert "lane GR's floor gate case" in _g16_cases()


def test_a_row_family_with_the_column_as_a_parent_publishes_its_row_census():
    """Skeptic 1, under item 11: a row family's parent totals sum to the
    column's row census, which the twin must meet."""
    assert "*A row family with the column as a parent publishes it anyway.*" in _part("5")


# --- generation -----------------------------------------------------------------


def test_the_top_bands_excess_is_dealt_grain_cell_by_grain_cell():
    """Skeptic 1, item 7. Mutant: the one straight line over the whole top
    band, which misses every parent cell's row total."""
    method = _g16()
    assert "each grain cell `C` takes a TOTAL top-band excess `q_C`" in method
    assert "8. the top band's excess under a row family" in _g16_cases()


def test_the_patient_weight_is_read_on_the_published_row_family_and_not_on_the_childs_level():
    """Statistics skeptic, item 2. Mutant: the first build's weight, 'the share
    of the column's between-patient variance its published own-mean bands do
    not carry'."""
    method = _g16()
    assert "THE WEIGHT `omega` is the latent correlation of a row's reading" in method
    assert "it does not depend on the child's level" in method
    assert "the row's noise is not shrunk by the trend's variance" in method
    assert "the share of the column's between-patient variance its published own-mean bands do not carry, read" not in method


def test_the_polish_keeps_every_patient_in_its_own_mean_band():
    """Skeptic 1, item 8."""
    assert "only where both patients' own means stay inside their own-mean bands" in _g16()


# --- the measured figures, restated ---------------------------------------------


def test_no_100000_row_figure_of_run_2_stands_unqualified():
    """Statistics skeptic, item 1 (a): run 2's 100,000-row figures were
    measured on an own-mean family holding cells of 1 to 10 patients."""
    trend = _part("1")
    assert "ITS 100,000-ROW FIGURES WERE MEASURED ON A DESCRIPTION THIS PAGE FORBIDS" in trend
    assert "at 100,000 rows all 14" not in trend
    assert "fifteen runs is inside it" not in _flat(_section())
    assert "within 0.024 of the real on fifteen runs" not in _entry()
    assert "``RUN3" not in _flat(_section())
    assert "ITS 100,000-ROW FIGURES WERE MEASURED ON AN OWN-MEAN FAMILY HOLDING 7 TO 13 CELLS" in _decision()


def test_run_3_is_cited_as_measured_with_its_variants():
    """The orchestrator's ruling of 2026-10-20 10:41: run 3 in-lane, the floor
    enforced, (a) the child at the median and (b) a weight independent of the
    child's level; READY needs clauses (1) to (4) at 100,000 rows on 5 of 6."""
    limits = _part("11")
    assert "clauses (1) to (4) held on all 10 route-runs at 100,000 rows (6 of 6 on `ST2`)" in limits
    assert "broke clause (5) on 21 of 23 runs, so G16.15 takes none" in limits
    assert "So the limit is CLOSED in method for December" not in limits
    assert "OPEN until lane CHa measures the floored split on long tables" in limits
    assert "trend missed clause (1) on 4 of 8 runs at 100,000 rows (0.013 to 0.378 of the real)" in _part("2")
    assert "a split exists at the first option offered, the child at the median, on all 24 route-runs" in _part("2")
    assert "READY's 5 of 6 met" in _decision()
    assert "5 of 8 runs" not in _flat(_section()) and "5 of 8 runs" not in _decision()


def test_the_rigid_rule_was_rerun_on_the_fifteen_fixtures():
    """The orchestrator's ruling of 2026-10-20 10:22, item 2: 0 leaks required,
    the pass count beside run 2's 1,516."""
    assert "the same 1,516 with the rigid rule of 4.6c.1 (b) 2 as repaired" in _part("10")
    assert "the fourteenth's one-code band being its lowest" in _decision()


def test_the_long_tables_gap_reads_0_076():
    """Statistics skeptic, item 3: 0.7194 - 0.6433 = 0.0761."""
    for text in (_flat(_section()), _decision(), _entry(), _flat(STATE.read_text(encoding="utf-8"))):
        assert "0.077 to 0.081" not in text
    assert "0.076 to 0.081" in _part("11")


def test_the_dates_rule_is_priced_on_the_zoo_with_a_trigger():
    """Statistics skeptic, item 5."""
    dates = _part("7")
    assert "8 of the 165" in dates and "351 of 5,344" in dates
    assert "*The trigger:*" in dates


# --- the second review round (2026-10-20: the page's verify and one Codex review) ---

VALIDATION = REPOSITORY / "docs" / "spec" / "validation-method-v1.md"
TAU = 2.0


def _v12():
    return _flat(_between(VALIDATION, "**V12.7 The patient layer's lines", "\n## "))


def _type7(sorted_values, percent):
    """The type-7 rung of a sorted list at a whole percent."""
    h = (len(sorted_values) - 1) * percent / 100
    low = int(h)
    high = min(low + 1, len(sorted_values) - 1)
    return sorted_values[low] + (h - low) * (sorted_values[high] - sorted_values[low])


def test_the_mean_and_the_tails_fix_the_code_total_so_the_min_alternative_is_gone():
    """Verify item 1 (BLOCKER), computed: with readings kept to one decimal
    (whole tenths here), the exact mean and the two tails' rows and mean
    distances give back the code total over every row, whatever min and max
    say. Mutant: the first build's 'the published `min` is below `p01`'
    alternative, or S33 reading min."""
    tenths = [((k * 7919) % 61) + 20 for k in range(2000)] + [3, 5, 140, 151, 160]
    tenths.sort()
    low_rung = round(_type7(tenths, 1))
    high_rung = round(_type7(tenths, 99))
    span = high_rung - low_rung
    codes = [min(span, max(0, t - low_rung)) for t in tenths]
    below = [t for t in tenths if t < low_rung]
    above = [t for t in tenths if t > high_rung]
    total = sum(tenths)
    low_sum = len(below) * low_rung - sum(low_rung - t for t in below)
    high_sum = len(above) * high_rung + sum(t - high_rung for t in above)
    middle = total - low_sum - high_sum
    middle_rows = len(tenths) - len(below) - len(above)
    assert (middle - middle_rows * low_rung) + span * len(above) == sum(codes)
    part = _part("1")
    assert "So the code total over EVERY row of `x` is FIXED wherever the exact mean is published" in part
    assert "`O_free = n - sum |P| r - n_one`" in part
    assert "406,482 with both ends `null`" in part and "397,200 with `min` published at 3.0" in part
    s33 = _part("10")
    assert "`O_free = n - sum |P| r - n_one`, read on the census" in s33
    assert "the column's published `min` is below its `p01`" not in s33


def test_the_grid_is_read_on_the_tail_boundary_rungs_and_never_on_min_or_max():
    """Verify item 1 (b) and Codex item 2: p01 and p99 are withheld on small
    columns, extrema are null, a zero span made u zero. Mutant: the first
    build's '`L` its `p01` rung'."""
    setting = _setting()
    assert "`L` is the rung at `tails.low.percent` and `H` the rung at `tails.high.percent`" in setting
    assert "`L` its `p01` rung" not in setting
    assert "where `H = L` (a zero central span) `u` and `K` are 0 and the column has no grid either" in setting
    assert "No rule of this section reads `min` or `max`" in setting
    assert "has a grid of two or more codes (`tails` standing on both sides and `K >= 1`" in _part("1")


def test_the_own_mean_guard_is_removed_and_its_grid_model_line_is_checked():
    """Verify item 1 (c). Mutant: the parenthetical guard restored, or the
    grid-model line left among the proven."""
    assert "that guard is REMOVED (the page's verify, item 1 (c))" in _part("2")
    limits = _part("11")
    assert "the own-mean certificate's grid-model line moved here by the page's verify" in limits
    assert "where 4.6c.1 (b) 6 leaves the code total of the cells' patients unfixed: every union" not in limits


def test_the_trend_without_dropout_is_restated_and_the_verify_tables_are_cases():
    """Verify item 1 (d): ST2 without dropout publishes no Q under the
    corrected guard; the verify's two tables are K-S6-08 cases."""
    part = _part("1")
    assert "publishes NO `Q_P`, and its arm-by-visit trend falls to BASE's 0.003 and 0.006" in part
    assert "clauses (1) to (4) hold on 12 of the 14 route-runs at 20,000 rows" in part
    cases = _part("10")
    assert "`make_tail_table.py`" in cases and "`make_heaped_min.py`" in cases


def _exact_ssb_pins_a_count():
    """The design study's run 3c fixture `MF1` at 4 patients (`mom_fix.py`):
    every world of four two-row patients over codes 0 to 3 whose eight
    codes sum to 21 with square sum 57 (the column's exact mean and
    spread). Returns, for each sum over patients of the squared code
    total (what an exact SSB adds), the counts of (3, 3) patients."""
    types = list(itertools.product(range(4), repeat=2))
    found = {}
    for world in itertools.combinations_with_replacement(types, 4):
        codes = [c for patient in world for c in patient]
        if sum(codes) == 21 and sum(c * c for c in codes) == 57:
            squares = sum(sum(patient) ** 2 for patient in world)
            found.setdefault(squares, set()).add(world.count((3, 3)))
    return found


def test_the_moments_candidate_is_measured_and_not_adopted():
    """The second verify's item 1 (MAJOR) and the orchestrator's ADDENDUM 3
    (14:55) on `bc-design/SLOPE-run3c.md`: candidate (c) was MEASURED (6 of
    6 at 100,000 rows; on the long table the trend at 0.903 to 0.931 and
    the correlation +0.005 to +0.034 off), is NOT ADOPTED for want of a
    certificate, is owed the `r`-band SWING proof and a joint witness, has
    `mom_fix.py`'s cases in `K-S6-08`, and reads its resolutions from the
    census bound. Computed: on `MF1`'s four patients the count of (3, 3)
    patients is 1 or 2 without the moment (f-able at `f = 2`) and exactly
    1 with an exact SSB, the leak run 3c worked through. Mutants: 'NOT YET
    ADOPTED' -> 'ADOPTED'; the first repair's 'NOT MEASURED' back; item 7
    of `K-S6-08` dropped; the census bound -> the true count; the long
    table's 0.903 to 0.931 dropped from limit 2."""
    found = _exact_ssb_pins_a_count()
    assert found == {111: {1}, 113: {2}}
    assert set().union(*found.values()) == {1, 2} and found[111] == {1}
    limits = _part("11")
    assert "*The third candidate, MEASURED, the long-table route NOT YET ADOPTED (the orchestrator's ADDENDUM 2 of 2026-10-20, 12:51, and ADDENDUM 3, 14:55;" in limits
    assert "MEASURED by the design study's run 3c (`bc-design/SLOPE-run3c.md`" in limits
    assert "*Why it is not adopted:* no existing witness covers its moments." in limits
    assert "the `r`-band SWING proof of limit 2 (the per-arm slope is its coarsest case) plus a joint witness reading the `SSB` with the column's square sum" in limits
    assert "*Owner and date:* the January stretch, beside limit 2's `r`-band form, unless the certificate lands in December" in limits
    assert "takes for `n_g` the lower bound the published census gives on the group's patients with `r >= 2`" in limits
    assert "never the true patient count or the true sum" in limits
    assert "Papadimitropoulou 2020" in limits and "Matthews 1990" in limits
    assert "*Why `A0` stands:* the orchestrator's ADDENDUM 3 (1) adopts candidate (a)" in limits
    assert "NOT MEASURED" not in limits and "stays unmeasured" not in limits
    assert "arm by visit at 0.903 to 0.931 of the real on those long tables, with the correlation's gaps +0.005 to +0.034" in limits
    assert "until then the long-table trend is this limit, at today's 0.012 to 0.019" in limits
    assert "candidate (c) of limit 3 brings the correlation within +0.005 to +0.034 of the real" in limits
    cases = _part("10")
    assert "7. NEW with the page's second verify" in cases and "`bc-design/SLOPE-run3c/mom_fix.py`" in cases
    assert "pins such a count in 6,396 to 6,697 of 8,159 to 8,445 descriptions" in cases
    decision = _decision()
    assert "candidate (c), moments: MEASURED by the design study's run 3c" in decision
    assert "it is written as the long-table route NOT YET ADOPTED, owed a certificate" in decision
    assert "NOT MEASURED in this lane" not in decision
    entry = _entry()
    assert "measured by the design study's run 3c" in entry and "0.903 to 0.931" in entry
    assert "not measured (lane GR" not in entry
    state = _flat(STATE.read_text(encoding="utf-8"))
    assert "is measured and not adopted" in state and "0.903 to 0.931" in state


def test_a_computed_dates_difference_has_levels_and_a_certificate():
    """Verify item 3. Mutant: S31 admitting only a repeated or dealt date."""
    dates = _part("7")
    assert "its CERTIFICATE is PWIT where every parent cell is one grain cell holding one value of `r`" in dates
    assert "it takes NO class witness" in dates
    assert "dealt date child, or a carried rule's difference at 4.6b.7's levels" in _part("10")
    assert "a computed date `B = A + D` whose grain cell holds a band of `r`" in _part("10")


def _both_rows_range(patients, band_rows):
    """Patients holding both rows in a band, over every world of two-row
    patients with `band_rows` rows in the band."""
    held = []
    for both in range(patients + 1):
        one = band_rows - 2 * both
        if one >= 0 and patients - both - one >= 0:
            held += [both]
    return min(held), max(held)


def _pwit(patients, supplies):
    return all(s <= patients * (s // FLOOR) for s in supplies)


def test_a_column_that_is_no_row_familys_child_takes_the_one_cell_certificate():
    """Verify item 4, computed: 20 patients of two rows, a band of 21 of 40
    rows, fix 'both rows in the band' inside 1 to 10; PWIT refuses it, and
    passes 22 patients with a band of 23 of 44. Mutants: PWIT with ceil;
    the one-cell paragraph removed; step 2's all-modal world back."""
    assert _both_rows_range(20, 21) == (1, 10)
    assert not _pwit(20, [21, 19])
    assert _pwit(22, [23, 21])
    assert all(s <= 20 * -(-s // FLOOR) for s in (21, 19))
    rows = _part("8")
    assert "*The one-cell family (the page's verify, item 4).*" in rows
    assert "s_x <= |P| * floor(s_x / f) for every band x." in rows
    assert "a position-like column takes 4.6c.6 (d)'s tie-world values" in rows
    assert "takes 4.6c.6's all-modal values" not in rows
    assert "that is the child of no row family, read as the one-cell family of (a)" in rows


def test_every_family_holding_r_holds_its_other_members_in_g():
    """Verify item 5 and Codex item 6, computed from Codex's published
    numbers: the B0 cells of the lower r group hold rows twice their
    patients, so every r = 1 patient is B1, and 'r = 2, A1, B1' is 34 - 28
    = 6 in every table. Mutant: the rule removed, or the tie left
    undefined."""
    lower_b0 = {"B0C0": (30, 60), "B0C1": (33, 66)}
    assert all(rows == 2 * patients for patients, rows in lower_b0.values())
    r1_a1, lower_a1_b1 = 0 + 28, 28 + 6
    assert lower_a1_b1 - r1_a1 == 6
    rows = _part("8")
    assert "*Every family holding `r` holds its other members in `G`" in rows
    assert "Each such cell IS a union of grain cells crossed with values of `r`" in rows
    assert "inside each grain cell `C`, give its patients the values of `r` that `R*_C` names" in rows
    assert "every family of the patient chain that holds `r` holds its other members among `G`'s".lower() in _part("10").lower()


def test_the_numbers_the_verify_corrected():
    """Verify item 6, sub-items 1 to 10."""
    section = _flat(_section())
    assert "within 0.032)" in _part("2") and "within 0.031)" not in section
    assert "81 to 202 on `F3`" in _part("11") and "81 to 87" not in section
    assert "on ALL FIFTEEN fixtures with `k = 0`, 0 leaking descriptions over 163,755 SWING passes" in _part("1")
    assert "the other fourteen fixtures at this level are lane CHa's" not in section
    assert "the oracle's ten cases after the first repair" in _decision()
    assert "**What is written (specified, NOT BUILT; no product code changed).** Contract section 4.6c" in _decision()
    fixed = _part("5")
    assert "has TWO clauses, and passes where either holds" in fixed
    assert "the health data zoo's 14 tables the gate turns on" in fixed
    limits = _part("11")
    assert "one table described by two installations" in limits and "RELATED tables described twice" in limits
    assert "different tables given the same name" in limits
    assert "lane MDEP's zones of plan P4-D409" in _part("2") and "lane MDEP's zones of plan P4-D409" in _part("8")
    assert "PWIT judging" in _entry() and "PWIT judging" in _flat(STATE.read_text(encoding="utf-8"))
    assert "counts of patients by their exact readings" in _entry()


def test_the_verifys_green_mutants_are_pinned():
    """Verify item 7: fourteen mutants of the first repair's guards stayed
    green; each phrase below is red on its own."""
    assert "classed `repeated` is the child of a row family only under the FLOORED SPLIT" in _part("5")
    assert "takes its child at the median, the two-band level of its ladder," in _part("2")
    assert "s_x <= |P| * floor(s_x / f)   for every band x." in _section()
    assert "2. every `R*_C(rho)` is 0 or at least `f` (FLOORED);" in _part("8")
    assert "`T = max(f - 1, floor(N2 / 100))` where" in _part("5")
    assert "every value band of a published level holds at least `max(2 f, f + 4)` patients" in _part("2")
    assert "2. for the first date only, every DIFFERENCE between the source's" in _part("2")
    assert "else TWO exchanges on different patients whose half-steps sum to it, else" in _g16()
    cases = _part("10")
    assert "extra rows are at least `settings.small_cell_floor` (it is also" in cases
    assert "readings of 4.6c.6 (d)'s tie world at most 20." in cases
    assert "`(2 Q_P + h) u / (2 |P| Sxx(r))`, with `h` one half" in _part("1")
    assert "holds a reading on every row (its published `n_missing` over tabled rows is 0)" in _part("1")
    assert "every other column's `n_distinct_by_occurrences` is `null` unless its" in _part("3")
    assert "and the census of `r`'s top band is empty or lies wholly in one of the column's bands at that level" in _part("5")
    v12 = _v12()
    assert "12. a patient-fixed column's values exchanged, on every row, between 11 patients" in v12
    assert "13. a patient-fixed column's values exchanged, on every row, between a patient of the census's top band" in v12
    assert "(the column's `L0` totals in patients unchanged, so the line is judged)" in v12


def _deficit_search(m, q):
    """4.6c.4 (b)'s bounded deficit search, steps (i) to (iii)."""
    t = -(-q // m)
    deficit = m * t - q
    if deficit == 0:
        return m >= FLOOR
    for d in range(1, min(t, deficit // FLOOR) + 1):
        if deficit % d == 0 and FLOOR <= deficit // d <= m - FLOOR:
            return True
        low = max(2 * FLOOR, -(-(deficit + FLOOR) // (d + 1)))
        if d + 1 <= t and low <= min(m - FLOOR, (deficit - FLOOR) // d):
            return True
    return False


def test_the_censuss_search_is_bounded_and_finds_what_the_full_search_finds():
    """Codex item 7: the three-value search tried 166,616,670,000 triples on
    99 patients of 10,000 rows and one of 9,999. Computed: the deficit
    search refuses that census at its first step and agrees with the full
    search on small top bands. Mutant: the first build's 'every three
    values of 0 .. t' as the producer's search."""
    m, q = 100, 99 * 9999 + 9998
    assert m * (-(-q // m)) - q == 1 and not _deficit_search(m, q)
    for mm in range(11, 31):
        for qq in range(0, 2 * mm + 1):
            if _deficit_search(mm, qq):
                assert _floored_split_exists(mm, qq, -(-qq // mm))
    census = _part("4")
    assert "The producer decides item 2 by the bounded DEFICIT SEARCH" in census
    assert "126,500 bands" in census
    setting = _setting()
    for words in ("`TRIES_MAX = 1,000,000`", "`PATTERNS_MAX = 4,096`", "`NODES_MAX = 10,000`"):
        assert words in setting
    assert "*The floored split's patterns, in order* (the setting's bound)." in _part("8")
    assert "searches by exact integer search over every allowed pattern of every class" not in _part("2")


def test_where_no_family_holds_r_the_grain_family_is_the_census():
    """Codex item 1: 100 patients of two rows leave r one band, so no family
    holds it. Mutant: the paragraph removed."""
    rows = _part("8")
    assert "*Where no family holds `r` (the codex review of 2026-10-20, item 1).*" in rows
    assert "`G` is `r`'s census itself" in rows
    assert "*`statistical` is never `null` while the layer is ON:*" in rows
    assert "`null` where no placed family holds `r`" in _part("9")


def test_a_patient_fixed_row_census_is_read_on_the_patient_table():
    """Codex item 3, computed: 99/101 in the file against 100/100 as defined.
    Mutant: 'how many rows hold each value' as the census."""
    first = ["A"] * 50 + ["B"] * 50
    second = ["B"] + ["A"] * 49 + ["B"] * 50
    file_rows = {v: first.count(v) + second.count(v) for v in "AB"}
    weighted = {v: 2 * first.count(v) for v in "AB"}
    assert file_rows == {"A": 99, "B": 101} and weighted == {"A": 100, "B": 100}
    assert "Its ROW CENSUS is every count of it taken over rows instead, READ ON THE PATIENT TABLE" in _part("5")
    assert "read on the file's PATIENT TABLE" in _v12()


def test_the_first_date_close_exchanges_across_bands():
    """Codex item 4, computed: exchanges inside one band never change a
    patient's band counts; one across bands mends a pair. Mutant: 'the
    same cell and band'."""
    patients = [["U", "U"]] * 20 + [["L", "L"]] * 20 + [["L", "U"]] * 60
    wrong = sum(1 for p in patients if "L" not in p)
    donors = sum(1 for p in patients if p.count("L") == 2)
    assert wrong == 20 and min(wrong, donors) == 20
    method = _g16()
    assert "the exchange is ACROSS bands" in method
    assert "exchanging the date with a row of the same cell and band" not in method


def test_the_census_line_is_judged_first():
    """Codex item 5. Mutant: the first build's sentence making the census
    line 'not judged' when its census differs."""
    v12 = _v12()
    assert "THE CENSUS LINE IS JUDGED FIRST, and always" in v12
    assert "a census, family or trend line of a file whose `L0` totals or census differ" not in v12


def test_a_null_position_entry_writes_the_stand_in():
    """Codex item 8. Mutant: the paragraph removed."""
    assert "the twin writes the column's STAND-IN" in _part("6")
    assert "a list `[null, null]` writes stand-ins on every row" in _g16()
    assert "a `null` entry is not judged" in _v12()


def test_the_derived_close_runs_without_a_row_family():
    """Codex item 9. Mutant: 'No row family: steps 4 and 6 do nothing.'"""
    assert "WHETHER OR NOT its source is the child of a placed row family" in _g16()
    cases = _g16_cases()
    assert "No row family: step 4 does nothing, and step 6 still runs" in cases
    assert "No row family: steps 4 and 6 do nothing." not in cases


def test_a_first_date_pattern_admits_absent_later_dates():
    """Codex item 10. Mutant: the residual's missing supply removed."""
    part = _part("2")
    assert "or in `D`'s `missing` band, and no row in a value band below `b`" in part
    assert "`s'_missing = s_missing` for `D`'s `missing` band" in part


def test_the_extension_carries_u_and_the_rescale_inverts_the_response():
    """Codex items 11 and 12, computed: with a response half the weight,
    gamma_0 times beta reaches a quarter and gamma_0 over beta the target.
    Mutants: the extension without u; 'gamma = gamma_0 beta'."""
    beta = 0.5
    assert beta * beta == 0.25 and beta / beta == 1.0
    method = _g16()
    assert "the pooled slope `u sum (2 Q + h) / sum 2 |P'| Sxx(r')`" in method
    assert "then `gamma = gamma_0 / beta` where `beta > 0.05`" in method


def test_the_excess_split_has_a_total_tie_order():
    """Codex item 13, computed: (5, 6) and (6, 5) both least. Mutant: the
    lexicographic order removed."""
    least = min((a - 5.5) ** 2 + (11 - a - 5.5) ** 2 for a in range(12))
    ties = [(a, 11 - a) for a in range(12) if (a - 5.5) ** 2 + (11 - a - 5.5) ** 2 == least]
    assert ties == [(5, 6), (6, 5)] and min(ties) == (5, 6)
    assert "the vector `(q_C)` that is LEAST in lexicographic order" in _g16()


def test_patient_scores_and_the_weight_follow_the_arithmetic_rule():
    """Codex item 14: G16.8 forbids a library logarithm or quantile. Mutant:
    'the normal quantile of `u_p`'."""
    method = _g16()
    assert "one `integers` call of FOUR words a patient" in method
    assert "two FROZEN TABLES of the shared module" in method
    assert "`z_p` the normal quantile of `u_p`" not in method


def _p_off(eligible, patients, repaired):
    scores = [patients * lo if repaired else lo - 1 for lo in eligible] + [0]
    top = max(scores)
    weights = [2.718281828459045 ** (-(top - v) / TAU) for v in scores]
    return (1 - 2 ** -30) * weights[-1] / sum(weights) + 2 ** -30 / len(scores)


def test_the_census_draw_scores_patients_so_off_keeps_only_the_uniform_share():
    """Codex item 15, computed on its census (only lo = 1 eligible): 'off'
    took one half under 'lo - 1', and below one in a billion under 'N lo'.
    Mutant: 'each scored `lo - 1`'."""
    assert abs(_p_off([1], 100, False) - 0.5) < 1e-6
    assert _p_off([1], 100, True) < 1e-9
    assert _p_off([1, 2, 3], 184, False) > 0.15
    census = _part("4")
    assert "each scored `N lo`" in census and "each scored `lo - 1`," not in census
    assert "scored `N` times its number of bands" in _part("2")
    assert "3.8 to 50 per cent" in _part("3")


def test_uncarried_groups_trends_are_not_called_flat():
    """Codex item 16, and the second verify's item 2: P4-D412 still told
    lane ST to report 'every other group's trend flat'. Mutants: 'every
    other group's trend over visits is flat in the twin'; the decision's
    'trend flat' back."""
    limits = _part("11")
    assert "every other group's trend over visits is flat in the twin" not in limits
    assert "approximate or unconstrained, NOT flat" in limits
    assert "every other group's trend approximate or unconstrained, never flat" in _decision()
    assert "trend flat" not in _flat(PLAN.read_text(encoding="utf-8"))


def test_the_second_verifys_green_mutants_are_pinned():
    """The second verify's item 3: eight repaired rules no check held (its
    `mutate_extra.py`, each mutant alone on a copy). The first two are the
    BLOCKER's threshold, `f` in both places; the third is Codex 5's core.
    Computed: PWIT in one cell holds for every band of at least `f` rows
    once the table holds `2 f` = 22 patients, and refuses a band at 20.
    Mutants, each red on its own: S33's floor -> 1; (b) 6's 'at least `f`'
    -> 'at least one'; the census line 'not judged'; 'drawn HELD' -> 'drawn
    as it is'; 22 -> 11 patients; `D` given a `ladder` entry; STATE's and
    the CHANGELOG's long-table route called closed."""
    for patients in range(2 * FLOOR, 2 * FLOOR + 40):
        for band in range(FLOOR, 10 * patients + 1):
            assert patients * (band // FLOOR) >= band
    assert not _pwit(20, [21, 19])
    assert "`O_free = n - sum |P| r - n_one`, read on the census, `F_S`'s published counts and the column's `L0` totals, is at least `settings.small_cell_floor` (4.6c.1 (b) 6;" in _part("10")
    assert "or where the rows outside those cells keep a free code total: at least `f` of them," in _part("1")
    assert 'a file whose census differs from the published one reads MISSED on the census line, never "not judged"' in _v12()
    rows = _part("8")
    assert "Where the certificate fails the column is drawn HELD (inventory row 19a)" in rows
    assert "so on one `r` it refuses only tables of fewer than 22 patients" in rows
    assert "with the edges 4.6b.7 publishes and no `ladder` entry of its own (the row family's table is its only count)" in _part("7")
    state = _flat(STATE.read_text(encoding="utf-8"))
    assert "three long-table runs of the page's run 3, with PWIT judging the row family (OPEN until lane CHa measures" in state
    assert "within 0.0093 in run 3 with PWIT judging, OPEN until lane CHa measures" in _entry()


def test_complete_follow_up_is_a_stated_december_limit_in_plain_words():
    """The orchestrator's ADDENDUM 4 (17:35), on the second repair's point
    1. Computed: where every patient of the table holds all eight visits,
    the trend's one cell holds every row, so no row outside it keeps a
    free code total (`O_free = 0 < f`) and 4.6c.1 (b) 6 refuses the trend.
    The page's limits, the private report's words the page names, P4-D412
    and STATE say so in plain words, with the measured price (run 3:
    `st2full` only; 22 of 24 route-runs meet clauses (1) to (4)) and the
    owner (lane GR, January). Mutants: the sentence removed from any one
    place; the price or the owner dropped."""
    patients, visits = 3000, 8
    rows = patients * visits
    assert rows - patients * visits - 0 == 0 < FLOOR
    words = "on a table where every patient has every visit, change over visits is not published in December"
    limits = _part("11")
    assert "*Complete follow-up, a December limit* (the orchestrator's ADDENDUM 4 of 2026-10-20, 17:35): On a table where every patient has every visit, change over visits is not published in December." in limits
    assert 'it says, in these words: "' + words + '"' in limits
    assert "22 of 24 route-runs meet clauses (1) to (4), and READY's 6 of 6 on `ST2` at 100,000 rows stands" in limits
    assert "*Owner:* lane GR in January, a certificate covering cells of `F_S` that hold every row, measured on `st2full`." in limits
    decision = _decision()
    assert "COMPLETE FOLLOW-UP, A DECEMBER LIMIT" in decision and words + ", since" in decision
    assert "owner lane GR in January: a certificate covering `F_S` cells that hold every row, measured on `st2full`" in decision
    state = _flat(STATE.read_text(encoding="utf-8"))
    assert "Complete follow-up, a December limit: " + words in state
    assert "22 of 24 route-runs meet `K-BC-06`'s clauses (1) to (4); owner lane GR in January" in state
    assert words in _entry()
