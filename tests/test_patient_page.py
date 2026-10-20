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

WHAT IS NOT HERE. No patient-layer code exists to run, so nothing here
says a twin meets a census or a trend. `K-S6-08`'s enumeration and the
oracle's cases (G16.17) are where lanes CHa, GR and CHo run the method.
"""
import itertools
import pathlib
import re

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
    assert "6. **The unpinned total (the exact mean's guard).**" in part
    assert "the published `min` is below `p01` or the published `max` above `p99`" in part
    assert "`Q_P` is ELIGIBLE when SWING passes, item 6 holds" in part
    assert "873 descriptions SWING passed leak because `Q` stands beside the total" in part
    assert "4.6c.1 (b) 6); the loader recomputes SWING" in _part("10")
    assert "``MEAN" not in part


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
    assert "then on every three values of `0 .. t`" in census
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
    assert "within 0.024 of the real on fifteen runs" not in _flat(_section())
    assert "within 0.024 on fifteen runs" not in _entry()
    assert "``RUN3" not in _flat(_section())


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
