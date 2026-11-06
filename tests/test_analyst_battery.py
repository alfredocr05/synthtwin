"""The analyst battery's own guarantees: its controls can fail, and it scores only what it says (plan P4-D398).

A check that cannot fail is a defect (CLAUDE.md, "Built-in
validation"). The battery's KPIs carry `controls_hold`, and a run whose
controls do not behave as controls is void; these tests show the
mechanism biting rather than assume it:

* a run whose shuffled twin is really a fresh replicate, or whose
  replicate is really a shuffle, is void on every KPI that reads them --
  each of K-BC-01 to K-BC-10 named, on the fast part's own run, and
  K-BC-12 (twin-seed stability) on a run made up to its shape;
* K-BC-01 is void where one family's shuffle meets the family target,
  and leaves out the margins a shuffle keeps exactly;
* K-BC-02 charges the twin only with truths the replicate gets back,
  K-BC-05 keeps a clustered table out of its maximum, K-BC-06 reads the
  fixed effects against the replicate's, and K-BC-10 charges no twin with
  an analysis a replicate draw stops on too;
* the automatic panel holds every number to the real table's range and
  admits an indicator term into a logistic model only where it holds 22
  events and 22 non-events; at the slow tier a trained model predicts
  every two-valued column;
* the null table tests a label against a many-valued number by ranks;
* the half split is a partition, and on ST2 it never splits a subject;
* the shuffled twin keeps every column's cells, as written, and only
  their order changes;
* an estimate whose smallest defining cell is under 22 rows, or under
  11 in any half, is never scored, whatever its value; a rule the real
  table keeps on every row is scored, with a yardstick of 0;
* a mixed model over fewer than 22 subjects of two rows stops;
* K-BC-04 counts a model missing on any seed of a side as that side's
  failure and divides by the yardstick as measured; K-BC-05 never
  leaves out a discriminator that could not be fitted; K-BC-02's
  McNemar targets are stated only where a twin recovering nothing would
  miss them;
* the automatic panel keeps room for pair products;
* the slow driver's cache reads every module the panels come from, and
  the driver runs where `resource` does not exist;
* the report reading finds a block of family lines where one exists, so
  K-BC-11's "no line exists" is a reading and not a constant.

ST2 at 1,500 rows keeps most of the file to a few seconds; the swaps read
the fast part's run (`analyst_battery.fast_run`, made once a process).
"""

from __future__ import annotations

import dataclasses
import math
import pathlib

import pytest

import analyst_battery as B
import analyst_kit as K
import analyst_tables as T


@pytest.fixture(scope="module")
def small_run(tmp_path_factory: pytest.TempPathFactory) -> B.TableRun:
    """ST2 at 1,500 rows, seed 1, today's twin at seed 0, both controls."""
    return B.run_table("ST2", 1500, 1, (0,), "fast", tmp_path_factory.mktemp("battery-small"))


def _swapped(run: B.TableRun, side: str, by: str) -> B.TableRun:
    sides = dict(run.sides)
    sides[side] = run.sides[by]
    return dataclasses.replace(run, sides=sides)


def test_a_run_whose_controls_are_swapped_is_void(small_run: B.TableRun) -> None:
    """On ST2 alone at 1,500 rows: the ICC's controls hold, and fail with either control swapped."""
    assert B.kpi_06([small_run])["controls_hold"] is True
    for side, by in (("shuffled", "replicate"), ("replicate", "shuffled")):
        broken = _swapped(small_run, side, by)
        assert B.kpi_06([broken])["controls_hold"] is False, (side, by)
        assert "K-BC-06" in B.controls_failing(B.kpi_values([broken])), (side, by)


def test_the_replicate_control_is_a_binomial_bound_under_the_fresh_share() -> None:
    """At many estimates a share far under 77 % fails; at few, only a share under 30 % does."""
    assert B.replicate_holds(0.77, 400) and not B.replicate_holds(0.60, 400)
    assert B.replicate_holds(0.40, 8) and not B.replicate_holds(0.25, 8)
    assert not B.replicate_holds(math.nan, 100) and not B.replicate_holds(0.9, 0)


def test_the_half_split_is_a_partition_and_keeps_a_subject_whole() -> None:
    """Each split puts every row in exactly one half; on ST2 a subject's rows share a half."""
    view = B.read(T.text("ST2", 1500, 1), "ST2")
    groups = B.groups_of(view, "ST2", 1)
    sid = view.text("sid")
    for s in range(4):
        a, b = B.split(groups, s)
        assert sorted(a + b) == list(range(view.rows)) and not set(a) & set(b)
        half_of: "dict[str | None, int]" = {}
        for i in a:
            half_of[sid[i]] = 0
        assert all(sid[i] not in half_of for i in b)
    flat = B.groups_of(B.read(T.text("ST1", 600, 1), "ST1"), "ST1", 1)
    assert len(set(flat)) == 16


def test_the_shuffled_twin_keeps_every_column_s_cells() -> None:
    """Every column holds the same cells, as written; the rows are not the table's rows."""
    text = T.text("ST1", 800, 3)
    shuffled = B.shuffled_text(text, 9)
    columns = [sorted(c) for c in zip(*(line.split(",") for line in text.splitlines()))]
    again = [sorted(c) for c in zip(*(line.split(",") for line in shuffled.splitlines()))]
    assert columns == again
    assert sum(a == b for a, b in zip(text.splitlines()[1:], shuffled.splitlines()[1:])) < 10


def test_an_estimate_under_the_support_floor_is_never_scored(tmp_path: pathlib.Path) -> None:
    """A rate over 21 rows is left out of the yardstick however its halves agree; at 22 it is scored."""
    rows = [{"x": float(i < 21), "y": float(i % 2)} for i in range(400)]
    import pandas

    view = B.View(pandas.DataFrame(rows), "made up")

    def rates(v: B.View) -> "list[B.Estimate]":
        x, y = v.num("x"), v.num("y")
        out = B.rate("few", "F1", y, [a == 1.0 for a in x])
        return out + [dataclasses.replace(e, key="many", support=22) for e in out]

    y = B.yardstick([B.Analysis("rates", rates)], view, [i % 16 for i in range(400)])
    assert "few" not in y.h
    assert "many" in y.h


def test_the_report_reading_finds_family_lines_where_a_block_exists() -> None:
    """A block under the heading is read line by line; no heading, no block; carried means not 'not carried'."""
    report = "\n".join([
        "Something before.", "", B.REPORT_HEADING + ":",
        "F1 subgroup rates: carried", "F6 time to event: not carried (method)",
        "F10 your code runs: approximate", "", "after"])
    reading = B.report_reading(report)
    assert reading == {"block": True, "named": ["F1", "F6", "F10"], "carried": ["F1"]}
    assert B.report_reading("no block here") == {"block": False, "named": [], "carried": []}
    assert B.kpi_11([]) == {"families_unnamed": 10, "overclaims": 0, "report_block": False}


def test_a_value_the_ledger_cannot_hold_is_written_as_none() -> None:
    """NaN and the infinities become None, at any depth; other values stand."""
    assert B.finite({"a": math.nan, "b": {"c": math.inf}, "d": 1.5, "e": True}) == {
        "a": None, "b": {"c": None}, "d": 1.5, "e": True}


# -- the controls of every KPI, on the fast part's own run -------------------


@pytest.fixture(scope="module")
def fast_runs(tmp_path_factory: pytest.TempPathFactory) -> "list[B.TableRun]":
    """The fast part's runs: ST1 and ST2 at 5,000 rows, seed 1, today's twin at seed 0, both controls."""
    return B.fast_run(tmp_path_factory.mktemp("battery-fast"))["runs"]  # type: ignore[return-value]


CONTROLLED = ("K-BC-01", "K-BC-02", "K-BC-03", "K-BC-04", "K-BC-05", "K-BC-06", "K-BC-07", "K-BC-08",
              "K-BC-09", "K-BC-10")


def test_every_kpis_controls_hold_on_the_fast_run_and_fail_on_either_swap(fast_runs: "list[B.TableRun]") -> None:
    """K-BC-01 to K-BC-10 each: controls_hold on the run as made, false with either control swapped."""
    values = B.kpi_values(fast_runs)
    assert [k for k in CONTROLLED if values[k]["controls_hold"] is not True] == []
    for side, by in (("shuffled", "replicate"), ("replicate", "shuffled")):
        broken = B.kpi_values([_swapped(r, side, by) for r in fast_runs])
        assert [k for k in CONTROLLED if broken[k]["controls_hold"] is not False] == [], (side, by)


def test_k_bc_01_is_void_where_one_familys_shuffle_meets_its_target(fast_runs: "list[B.TableRun]") -> None:
    """F7's shuffled rows replaced by the replicate's: the pooled control still holds, F7's does not."""
    def leaky(run: B.TableRun) -> B.TableRun:
        rep = {c.key: c for c in run.sides["replicate"][0].compared if c.family == "F7"}
        sides = dict(run.sides)
        sides["shuffled"] = [dataclasses.replace(s, compared=[rep.get(c.key, c) for c in s.compared])
                             for s in run.sides["shuffled"]]
        return dataclasses.replace(run, sides=sides)

    broken = B.kpi_01([leaky(r) for r in fast_runs])
    assert broken["families_control_void"] == 1 and broken["controls_hold"] is False
    assert "void: F7" in str(broken["_detail"])
    assert B.kpi_01(fast_runs)["families_control_void"] == 0


def test_a_margin_is_kept_exactly_by_the_shuffle_and_left_out_of_k_bc_01(fast_runs: "list[B.TableRun]") -> None:
    """Every estimate tagged 'margin' reads the same on the shuffled twin; K-BC-01 counts none of them."""
    margins = [c for r in fast_runs for c in r.sides["shuffled"][0].compared if "margin" in c.tags]
    assert {c.key.split(":")[0] for c in margins} >= {"ST2/rows", "ST1/rate", "ST1/complete"}
    assert all(c.value is not None and abs(c.value - c.real) < 1e-12 for c in margins)
    joint = sum(1 for r in fast_runs for c in r.sides["replicate"][0].compared
                if not c.key.startswith("ST5/") and "margin" not in c.tags)
    assert B.kpi_01(fast_runs)["supported_estimates"] == joint + sum(len(r.tstr_yard) for r in fast_runs)


def _perfect(run: B.TableRun) -> B.TableRun:
    """Today's twin replaced by the replicate: what a perfect twin reads."""
    return _swapped(run, "twin", "replicate")


def test_a_perfect_twin_is_charged_with_no_truth_and_no_fixed_effect(fast_runs: "list[B.TableRun]") -> None:
    """K-BC-02 misses only what the replicate gets back; K-BC-06 counts fixed effects against the replicate's."""
    perfect = [_perfect(r) for r in fast_runs]
    two = B.kpi_02(perfect)
    assert two["truths_missed_unnamed"] == 0 and two["three_way_missed_unnamed"] == 0
    assert two["missed_over_replicate_z"] == 0.0 and two["three_way_missed_over_replicate_z"] == 0.0
    assert B.mcnemar(6, 3) == 1.0 and B.mcnemar(78, 0) > 8.0 and B.mcnemar(0, 0) == 0.0
    assert two["replicate_missed"] == two["truths_measured"] - two["replicate_recovered"] > 0
    assert B.kpi_06(perfect)["fixed_effects_outside_over_replicate"] == 0
    today = B.kpi_02(fast_runs)
    assert today["truths_missed_unnamed"] == today["replicate_recovered"] - today["truths_recovered"]
    exchanged = B.kpi_02([dataclasses.replace(r, sides=dict(r.sides, twin=r.sides["replicate"],
                                                            replicate=r.sides["twin"])) for r in fast_runs])
    assert exchanged["truths_recovered_beyond_replicate"] == today["truths_missed_unnamed"] > 0
    assert exchanged["missed_over_replicate_z"] == -today["missed_over_replicate_z"] < 0


def test_k_bc_05_reads_a_clustered_table_beside_its_maximum(fast_runs: "list[B.TableRun]") -> None:
    """ST2 alone gives no maximum and no control, only its ratio beside; ST1 sets the maximum."""
    st2 = [r for r in fast_runs if r.table == "ST2"]
    alone = B.kpi_05(st2)
    assert alone["pmse_over_replicate"] is None and alone["controls_hold"] is False
    assert alone["clustered_pmse_over_replicate"] is not None
    both = B.kpi_05(fast_runs)
    assert both["pmse_over_replicate"] == B.kpi_05([r for r in fast_runs if r.table == "ST1"])["pmse_over_replicate"]


def test_k_bc_10_charges_no_twin_with_an_analysis_a_replicate_draw_stops_on(fast_runs: "list[B.TableRun]") -> None:
    """The wide table made to stop on the replicate draw: it leaves the twin's count and is named fragile."""
    def fragile_wide(run: B.TableRun) -> B.TableRun:
        if run.table != "ST2":
            return run
        sides = dict(run.sides)
        sides["replicate"] = [dataclasses.replace(s, panel=B.Panel(s.panel.estimates,
                                                                   dict(s.panel.status, **{"ST2 wide table": "error"})))
                              for s in run.sides["replicate"]]
        return dataclasses.replace(run, sides=sides)

    before = B.kpi_10(fast_runs)
    after = B.kpi_10([fragile_wide(r) for r in fast_runs])
    assert before["fragile_analyses"] == 0 and after["fragile_analyses"] == 1
    assert after["analyses_stopping"] == before["analyses_stopping"] - 1 >= 0
    assert after["shuffled_stopping"] == before["shuffled_stopping"] - 1


def _made_up_stability_run() -> B.TableRun:
    """Twenty estimates, yardstick 1: the replicate near and steady, the shuffle steady and far, the thin noisy."""
    keys = [f"ST1/made:{k}" for k in range(20)]
    real = B.Panel({k: B.Estimate(k, "F3", 0.0, 0.1, 100) for k in keys}, {})

    def side(values: "list[float]") -> B.Side:
        panel = B.Panel({k: B.Estimate(k, "F3", v + 0.01 * i, 0.1, 100) for i, k in enumerate(keys)
                         for v in [values[i % len(values)]]}, {})
        return B.Side([], [], panel, {}, math.nan, [])

    sides = {"replicate": [side([0.3]), side([-0.2]), side([0.1])],
             "twin": [side([5.0]), side([5.1]), side([5.0])],
             "shuffled": [side([5.0]), side([5.1]), side([5.0])],
             "thin": [side([3.0]), side([-3.0]), side([0.4])]}
    return B.TableRun("ST1", 1000, 1, B.Yardstick(real, {k: 1.0 for k in keys}, set()), {}, sides, {}, 0.0, 0.0)


def test_k_bc_12_is_stable_and_inside_and_void_on_any_swap() -> None:
    """Stable at the wrong answer scores nothing; the thin, shuffled or replicate side swapped voids the run."""
    run = _made_up_stability_run()
    value = B.kpi_12([run])
    assert value["stable_share"] == 0.0 and value["replicate_stable_share"] == 1.0
    assert value["shuffled_stable_share"] == 0.0 and value["thin_stable_share"] == 0.0
    assert value["controls_hold"] is True
    for side, by in (("thin", "replicate"), ("shuffled", "replicate"), ("replicate", "shuffled")):
        assert B.kpi_12([_swapped(run, side, by)])["controls_hold"] is False, (side, by)


# -- the automatic panel and the null table ----------------------------------


def test_an_automatic_term_holds_its_number_to_the_real_tables_range() -> None:
    """A value far past the real table's largest reads as the largest, in the number and its spline terms."""
    column = B.Column("cost", "number", [], [1.0, 3.0, 5.0, 9.0], 0.0, "", 4.0, 2.0, 0.0, 10.0)
    terms = B.column_terms(column, 3)
    assert [n for n, _t in terms] == ["cost", "cost_s1", "cost_s2"]
    far = [t({"cost": [1e6, 10.0, -5.0, 0.0, math.nan]}) for _n, t in terms]
    for values in far:
        assert values[0] == values[1] and values[2] == values[3]
        assert values[4] != values[4]
    assert far[0][1] == (10.0 - 4.0) / 2.0


def test_a_logistic_model_admits_no_indicator_short_of_the_floors_events() -> None:
    """A label level of 120 rows and 3 events stays out of the automatic logistic model; the others go in."""
    import pandas

    rows = []
    for i in range(3000):
        group = "rare" if i < 120 else ("b" if i % 3 == 0 else "a")
        event = (i % 40 == 0) if group == "rare" else (i % 7 == 0 if group == "a" else i % 4 == 0)
        rows += [{"y": int(event), "grp": group, "x": float(i % 13)}]
    view = B.View(pandas.DataFrame(rows), "made up")
    columns = B.schema(view)
    assert next(c for c in columns if c.name == "grp").levels[1:] == ["b", "rare"]
    analysis = next(a for a in B.plan_auto(view, columns, "slow", "TX") if a.name == "TX auto y")
    keys = {e.key for e in analysis.run(view)}
    assert "TX/auto:y:lvl_grp=b" in keys
    assert "TX/auto:y:lvl_grp=rare" not in keys


def test_the_null_tables_test_of_a_label_and_a_many_valued_number_is_by_ranks() -> None:
    """Cost doubled for one language: Kruskal-Wallis finds it, a table of cost's values does not."""
    lines = T.text("ST5", 3000, 3).splitlines()
    head = lines[0].split(",")
    lang, cost = head.index("language"), head.index("cost")
    shifted = [lines[0]]
    for line in lines[1:]:
        cells = line.split(",")
        if cells[lang] == "es" and cells[cost]:
            cells[cost] = "%.2f" % (float(cells[cost]) * 2.0)
        shifted += [",".join(cells)]
    view = B.read("\n".join(shifted) + "\n", "shifted")
    assert B.st5_pair_p(view, "language", "cost") < 1e-6
    assert B.st5_pair_p(B.read(T.text("ST5", 3000, 3), "null"), "language", "cost") > 0.05
    ta, tb = view.text("language"), view.text("cost")
    both = [(a, b) for a, b in zip(ta, tb) if a is not None and b is not None]
    stat, df, _small = K.chi_square(K.contingency([a for a, _b in both], [b for _a, b in both]))
    assert df > 1000 and K.chi2_sf(stat, df) > 0.05


def test_at_the_slow_tier_a_trained_model_predicts_every_two_valued_column() -> None:
    """The seeded outcome first, then every binary column at the slow tier; the seeded one alone elsewhere."""
    columns = B.schema(B.read(T.text("ST1", 600, 1), "ST1"))
    binary = [c.name for c in columns if c.kind == "binary"]
    slow = [c.name for c in B.trained_outcomes(columns, "ST1", "slow")]
    assert slow[0] == "died" and sorted(slow) == sorted(binary) and len(binary) >= 5
    assert [c.name for c in B.trained_outcomes(columns, "ST1", "fast")] == ["died"]
    assert [c.name for c in B.trained_outcomes(columns, "ST1", "night")] == ["died"]
    assert B.trained_outcomes(columns, "ST3", "fast") == []


def test_the_battery_entries_bounds_can_fail_and_state_the_tiers_they_judge() -> None:
    """No share-gap bound at 100 points or more, the fast part's seconds bound at the lane's 60, K-BC-05's key columns as run.

    And every McNemar target of K-BC-02 one a twin recovering no truth
    would miss: such a twin reads sqrt(the replicate's recoveries), so a
    target of 2 binds only where the replicate gets back more than 4.
    """
    import json

    import kpi_rules

    ledger = json.loads(kpi_rules.LEDGER_PATH.read_text(encoding="utf-8"))
    entries = {e["id"]: e for e in ledger["entries"] if e["id"].startswith("K-BC-")}
    assert len(entries) == 13
    for kid, entry in entries.items():
        for key, bound in entry["expected"].items():
            if key.startswith("points_below_shuffled"):
                assert bound < 100, (kid, key, bound)
    for kid in ("K-BC-07", "K-BC-08", "K-BC-09"):
        assert "points_below_shuffled" not in entries[kid]["expected"]
        assert "the controls alone are judged" in entries[kid]["rule"]
    assert entries["K-BC-13"]["expected"]["fast_part_seconds"] <= 60.0
    words = {6: "six", 8: "eight", 10: "ten"}
    assert (f"the first {words[B.TIERS['slow']['keys']]} key columns ({words[B.TIERS['fast']['keys']]} at 5,000 rows)"
            in entries["K-BC-05"]["rule"])
    assert B.TIERS["night"]["keys"] == B.TIERS["slow"]["keys"]
    two = entries["K-BC-02"]
    measured = two["value_at"]["value"]
    stated = [key for key in two["target"] if "missed_over_replicate_z" in key]
    assert {"missed_over_replicate_z", "missed_over_replicate_z_20k", "three_way_missed_over_replicate_z_20k"} <= set(stated)
    for key in stated:
        suffix = "_20k" if key.endswith("_20k") else ""
        count = measured[("three_way_replicate_recovered" if key.startswith("three_way") else "replicate_recovered")
                         + suffix]
        assert B.mcnemar(count, 0) > two["target"][key], (key, count)


# -- the second review round's guarantees ------------------------------------


@pytest.mark.parametrize("pairs", [1, 3, 10])
def test_a_mixed_model_over_a_few_repeated_subjects_stops(pairs: int) -> None:
    """ST2 with a subject number of its own on every row but a few pairs: 'singular', never an ICC; 30 pairs fit."""
    lines = T.text("ST2", 1500, 2).splitlines()

    def renumbered(k: int) -> B.View:
        out = [lines[0]]
        for i, line in enumerate(lines[1:]):
            sid = f"P{i // 2:05d}" if i < 2 * k else f"U{i:06d}"
            out += [sid + line[line.index(","):]]
        return B.read("\n".join(out) + "\n", f"{k} pairs")

    with pytest.raises(K.FitTrouble) as refused:
        B.st2_mixed(renumbered(pairs))
    assert refused.value.kind == "singular"
    held = {e.key: e for e in B.st2_mixed(renumbered(30))}
    assert held["ST2/mixed:icc"].support == 30


def test_a_rule_the_real_table_keeps_is_scored_with_a_yardstick_of_zero() -> None:
    """The dose formula: in the yardstick at 0, the real rows inside, one broken row outside; a rate's support would drop it."""
    real = B.read(T.text("ST4", 1200, 4), "ST4")
    plan = [B.Analysis("formula", lambda v: [e for e in B.st4_linear(v) if e.key == "ST4/rule:dose_formula"])]
    y = B.yardstick(plan, real, B.groups_of(real, "ST4", 4))
    assert y.h == {"ST4/rule:dose_formula": 0.0}
    assert [c.inside for c in B.compare(y, B.run_panel(plan, real))] == [True]
    lines = T.text("ST4", 1200, 4).splitlines()
    cells = lines[5].split(",")
    cells[T.ST4_COLUMNS.index("dose")] = "%.1f" % (float(cells[T.ST4_COLUMNS.index("dose")]) + 1.0)
    broken = B.read("\n".join(lines[:5] + [",".join(cells)] + lines[6:]) + "\n", "one broken")
    assert [c.inside for c in B.compare(y, B.run_panel(plan, broken))] == [False]


def test_a_dose_that_keeps_the_regression_and_breaks_the_formula_misses_the_truth() -> None:
    """Dose replaced by 2 x fitted - dose: the weight's coefficient stands to the last digits, the formula's share does not."""
    key, value = T.TRUTHS["ST4"]["dose from weight and rate"]
    assert (key, value) == ("ST4/rule:dose_formula", 0.0)
    lines = T.text("ST4", 3000, 1).splitlines()
    real = B.read("\n".join(lines) + "\n", "ST4")
    cols, y = B.complete({"weight": real.num("weight"), "rate": real.num("dose_rate")}, real.num("dose"))
    fit = K.ols(K.Design(cols, [("int", K.intercept), ("weight", B.col("weight")), ("rate", B.col("rate"))]), y)
    at = T.ST4_COLUMNS.index
    out = [lines[0]]
    for line in lines[1:]:
        cells = line.split(",")
        w, q, d = float(cells[at("weight")]), float(cells[at("dose_rate")]), float(cells[at("dose")])
        fitted = fit.beta[0] + fit.beta[1] * w + fit.beta[2] * q
        cells[at("dose")] = repr(2.0 * fitted - d)
        out += [",".join(cells)]
    attacked = {e.key: e for e in B.st4_linear(B.read("\n".join(out) + "\n", "attacked"))}
    original = {e.key: e for e in B.st4_linear(real)}
    assert attacked["ST4/ols:dose_weight"].value == pytest.approx(original["ST4/ols:dose_weight"].value, rel=1e-9)
    assert original[key].value == 0.0 and attacked[key].value > 0.9


def test_an_estimate_thin_in_any_half_is_never_scored() -> None:
    """22 events and 22 non-events, 21 and 1 in every half: left out; 64 and 64, 32 in every half: scored."""
    import pandas

    rows = 400

    def view_of(events: int) -> B.View:
        flag = [1.0 if i < 2 * events else 0.0 for i in range(rows)]
        event = [1.0 if i < events else 0.0 for i in range(rows)]
        return B.View(pandas.DataFrame({"x": flag, "y": event}), "made up")

    def rates(v: B.View) -> "list[B.Estimate]":
        return B.rate("events", "F1", v.num("y"), [a == 1.0 for a in v.num("x")])

    plan = [B.Analysis("rates", rates)]
    lopsided = [0 if i < 21 else 15 if i < 43 else 0 if i < 44 else i % 16 for i in range(rows)]
    thin = B.yardstick(plan, view_of(22), lopsided)
    assert thin.real.estimates["events"].support == B.SUPPORT and "events" not in thin.h
    assert "events" in B.yardstick(plan, view_of(64), [i % 16 for i in range(rows)]).h


def _with_side(run: B.TableRun, side: str, change: "dict[str, object]") -> B.TableRun:
    sides = dict(run.sides)
    sides[side] = [dataclasses.replace(s, **change) for s in run.sides[side]]  # type: ignore[arg-type]
    return dataclasses.replace(run, sides=sides)


def test_k_bc_04_counts_a_missing_model_as_a_failure_and_divides_by_the_yardstick(
        fast_runs: "list[B.TableRun]") -> None:
    """The twin's model gone: an infinite gap, counted missing; a control's gone: void; a yardstick of 0.001 is not floored.

    Gone on one of five twin seeds whose other four score as the
    replicate does, the gap is infinite and the rank correlation -1, not
    the four seeds' median, which meets the target (the verify after
    Codex's review: one or two failed seeds of five read as none).
    """
    st1 = next(r for r in fast_runs if r.table == "ST1")
    assert list(st1.tstr_yard) == ["died"]
    before = B.kpi_04([st1])
    assert before["controls_hold"] is True and before["twin_models_missing"] == 0
    gone = B.kpi_04([_with_side(st1, "twin", {"tstr": {}})])
    assert gone["auc_gap_over_yardstick"] == math.inf and gone["twin_models_missing"] == 1
    assert gone["importance_rank_below_replicate"] >= before["importance_rank_below_replicate"]
    good = dataclasses.replace(st1.sides["twin"][0], tstr=dict(st1.sides["replicate"][0].tstr))
    lost = dataclasses.replace(good, tstr={})
    whole, one_lost = [B.kpi_04([dataclasses.replace(st1, sides=dict(st1.sides, twin=twin))])
                       for twin in ([good] * 5, [good, good, lost, good, good])]
    assert whole["auc_gap_over_yardstick"] == whole["replicate_auc_gap_over_yardstick"] <= 3.0
    assert whole["importance_rank_below_replicate"] == 0.0 and whole["twin_models_missing"] == 0
    assert one_lost["auc_gap_over_yardstick"] == math.inf and one_lost["twin_models_missing"] == 1
    assert one_lost["importance_rank_below_replicate"] == pytest.approx(
        st1.sides["replicate"][0].tstr["died"][1] + 1.0, abs=1e-3)
    assert B.kpi_04([_with_side(st1, "replicate", {"tstr": {}})])["controls_hold"] is False
    assert B.kpi_04([_with_side(st1, "shuffled", {"tstr": {}})])["controls_hold"] is False
    auc_ab, _yard, rank = st1.tstr_yard["died"]
    tiny = dataclasses.replace(st1, tstr_yard={"died": (auc_ab, 0.001, rank)})
    tiny = _with_side(tiny, "twin", {"tstr": {"died": (auc_ab - 0.01, 0.5)}})
    assert B.kpi_04([tiny])["auc_gap_over_yardstick"] == pytest.approx(10.0)


def test_k_bc_05_never_leaves_out_a_discriminator_that_could_not_be_fitted(
        fast_runs: "list[B.TableRun]") -> None:
    """A twin's failed discriminator on a second table: infinite whichever table comes first; a control's: void."""
    st1 = next(r for r in fast_runs if r.table == "ST1")
    failed = dataclasses.replace(_with_side(st1, "twin", {"pmse": math.nan}), table="ST3")
    for runs in ([st1, failed], [failed, st1]):
        value = B.kpi_05(runs)
        assert value["pmse_over_replicate"] == math.inf and value["discriminators_failed"] == 1
    assert B.kpi_05([st1])["controls_hold"] is True and B.kpi_05([st1])["discriminators_failed"] == 0
    for side in ("shuffled", "replicate"):
        assert B.kpi_05([st1, dataclasses.replace(_with_side(st1, side, {"pmse": math.nan}), table="ST3")])[
            "controls_hold"] is False, side


def test_the_automatic_panel_keeps_room_for_pair_products() -> None:
    """ST1 at 3,000 rows, the slow tier's cap: every automatic model but the rare readmission's holds a product."""
    view = B.read(T.text("ST1", 3000, 1), "ST1")
    panel = B.run_panel(B.plan_auto(view, B.schema(view), "slow", "ST1"), view)
    products: "dict[str, int]" = {}
    for key in panel.estimates:
        if "/auto:" in key:
            outcome = key.split(":")[1]
            products[outcome] = products.get(outcome, 0) + ("*" in key)
    assert len(products) >= 10
    assert [o for o, n in products.items() if n == 0 and o != "readmit"] == []
    assert sum(1 for n in products.values() if n == B.TIERS["slow"]["cap"] // B.INTERACTION_SHARE) >= 8


def _driver(monkeypatch: pytest.MonkeyPatch) -> object:
    """The slow driver, imported afresh by its name from tools/measurements, the search path restored after.

    A plain import, not a file loaded as a module: `tests/test_version_reach.py`
    holds the loads of that second kind to a recorded count.
    """
    import importlib
    import sys

    monkeypatch.syspath_prepend(str(pathlib.Path(__file__).resolve().parents[1] / "tools" / "measurements"))
    monkeypatch.delitem(sys.modules, "kpi_analyst_battery", raising=False)
    return importlib.import_module("kpi_analyst_battery")


def test_the_slow_drivers_cache_reads_every_module_its_panels_come_from(monkeypatch: pytest.MonkeyPatch) -> None:
    """kpi_shapes, fixtures and workbooks are in the digest beside the kit, the tables and the battery; the judge is not."""
    driver = _driver(monkeypatch)
    names = {p.name for p in driver.panel_code_files()}  # type: ignore[attr-defined]
    assert {"analyst_kit.py", "analyst_tables.py", "analyst_battery.py", "kpi_shapes.py", "fixtures.py",
            "workbooks.py", "generation.py"} <= names
    assert "kpi_rules.py" not in names


def test_the_slow_driver_runs_where_resource_does_not_exist(monkeypatch: pytest.MonkeyPatch) -> None:
    """With `resource` missing, as on Windows, the driver loads and the peak reads None."""
    import sys

    monkeypatch.setitem(sys.modules, "resource", None)  # type: ignore[arg-type]
    driver = _driver(monkeypatch)
    assert driver.peak_mb() is None  # type: ignore[attr-defined]
