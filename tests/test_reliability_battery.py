"""The reliability battery's gate (K-RU-01): its tables, its runner, its pass rule and its controls, on small tables.

The headline itself is measured by `tools/measurements/kpi_reliability_battery.py`
at the owner's table floor (20,000 rows and 1,000 people; the product
refuses anything smaller), so nothing here is a product claim. What is
held here is that the measuring instrument can fail: each clause of the
pass rule is shown failing on the case it names (a mutant per clause), the
seven tables are shown to carry the truths their generator sets (on its
own draws), every analysis file is shown to run on its real table, and
the controls are shown to separate a fresh sample from a shuffled table.
The end-to-end case runs the shipped commands on a small cohort through
`cli.main`'s internal `small_tables_refused=False`, a TEST DEVICE.
"""

from __future__ import annotations

import io
import json
import math
import pathlib

import pytest

import kpi_rules
import reliability_battery as B
import reliability_tables as T


def estimate(value: float, se: "float | None" = None, p: "float | None" = None, support: "int | None" = 1000,
             primary: bool = False) -> "dict":
    return {"estimate": value, "se": se, "p": p, "support": support, "primary": primary}


def run_of(estimands: "dict[str, dict]", ok: bool = True, trouble: "list[str] | None" = None,
           checks: "dict[str, float] | None" = None) -> B.ScriptRun:
    return B.ScriptRun(ok, "" if ok else "ValueError: stopped", estimands, checks or {}, trouble or [])


# -- the catalogue and the tables ---------------------------------------------------


def test_every_script_file_is_catalogued_and_every_entry_is_a_file() -> None:
    assert B.script_files() == sorted(B.SCRIPTS)
    for script in B.catalogue():
        assert script.table in T.TABLES
        assert script.family in B.FAMILIES
        text = script.path.read_text(encoding="utf-8")
        assert f'pd.read_csv("{T.FILES[script.table]}")' in text, script.stem
        assert 'open("results.json", "w"' in text, script.stem
    # Every headline family has a script of its own (F0 is the zoo's).
    assert {s.family for s in B.catalogue()} == set(B.FAMILIES) - {"F0"}
    # No script is a test file pytest would collect.
    assert not any(stem.startswith("test_") or stem.endswith("_test") for stem in B.SCRIPTS)


def test_each_table_is_drawn_from_its_seed_alone() -> None:
    for table in T.TABLES:
        first, again, other = T.text(table, 400, 3), T.text(table, 400, 3), T.text(table, 400, 4)
        assert first == again, table
        assert first != other, table
        lines = first.splitlines()
        assert lines[0].split(",") == T.COLUMNS[table]
        assert all(len(line.split(",")) == len(T.COLUMNS[table]) for line in lines[1:]), table
        assert "patient_id" in T.COLUMNS[table]


def test_the_orders_belong_to_the_cohort_of_the_same_seed() -> None:
    cohort = {line.split(",")[0] for line in T.text("T1", 600, 5).splitlines()[1:]}
    orders = {line.split(",")[1] for line in T.text("T5", 600, 5).splitlines()[1:]}
    assert orders and orders <= cohort
    assert len(orders) < len(cohort)  # most patients have no order


def _frame(table: str, rows: int, seed: int):  # type: ignore[no-untyped-def]
    pandas = pytest.importorskip("pandas")
    return pandas.read_csv(io.StringIO(T.text(table, rows, seed)))


def test_the_rules_the_tables_carry_hold_on_every_row() -> None:
    pandas = pytest.importorskip("pandas")
    cases = _frame("T4", 3000, 2)
    local = pandas.to_datetime(cases["in_room"], format="%Y-%m-%d %H:%M")
    universal = pandas.to_datetime(cases["in_room_utc"], format="%Y-%m-%dT%H:%MZ")
    assert ((universal - local).dt.total_seconds() == T.UTC_OFFSET_MINUTES * 60).all()
    steps = [pandas.to_datetime(cases[c], format="%Y-%m-%d %H:%M") for c in ("in_room", "incision", "close", "out_room")]
    assert all((steps[k] <= steps[k + 1]).all() for k in range(3))
    labs = _frame("T6", 3000, 2)
    number = pandas.to_numeric(labs["result"], errors="coerce")
    assert ((labs["result_num"] == T.SENTINEL) == number.isna()).all()
    assert (labs["result"].astype("string").str.startswith(".").fillna(False)).any()
    orders = _frame("T5", 3000, 2)
    units = orders["dose"].str.split(" ", n=1, expand=True)[1]
    assert (units.groupby(orders["drug"]).nunique() == 1).all()
    accounts = _frame("T7", 3000, 2)
    own = accounts["relationship"] == "Self"
    assert ((accounts["subscriber_id"] == accounts["patient_id"]) == own).all()
    charting = _frame("T3", 3000, 2)
    lag = (pandas.to_datetime(charting["entered_at"], format="%Y-%m-%d %H:%M")
           - pandas.to_datetime(charting["charted_at"], format="%Y-%m-%d %H:%M"))
    assert (lag[charting["device"] == "Y"].dt.total_seconds() == 0).all()


def test_the_seeded_effects_come_back_on_the_generator_s_own_draws() -> None:
    """Truths recovered on fresh draws: the cohort's logistic and survival effects, the visits' trajectory by arm."""
    sm = pytest.importorskip("statsmodels.api")
    smf = pytest.importorskip("statsmodels.formula.api")
    cohort = _frame("T1", 12000, 7)
    creat = cohort["creat"].astype("string").str.replace("<", "", regex=False).astype(float)
    data = cohort.assign(
        y=cohort["complication"].eq("Y").astype(int), diabetes=cohort["diabetes"].eq("Y").astype(int),
        smoker=cohort["smoker"].eq("Y").astype(int), age_c=cohort["age"] - 57, creat_high=(creat > 1.3).astype(int),
    )
    fit = smf.glm("y ~ age_c + I(age_c ** 2) + risk_class + diabetes * smoker + creat_high", data=data,
                  family=sm.families.Binomial()).fit()
    truth = T.T1_TRUTH["complication"]
    for term, key in (("risk_class", "risk_class"), ("smoker", "smoker"), ("age_c", "age"), ("diabetes", "diabetes"),
                      ("creat_high", "creat_high")):
        assert abs(fit.params[term] - truth[key]) < 4 * fit.bse[term], (term, fit.params[term], truth[key])
    visits = _frame("T2", 12000, 7)
    visits = visits.assign(arm_b=visits["arm"].eq("B").astype(int), visit0=visits["visit"] - 1)
    slope = smf.mixedlm("sbp ~ visit0 * arm_b + age", data=visits, groups=visits["patient_id"],
                        re_formula="~visit0").fit(reml=True, method=["lbfgs"])
    wanted = T.T2_TRUTH["sbp"]["arm_b_x_visit"]
    assert abs(slope.params["visit0:arm_b"] - wanted) < 4 * slope.bse["visit0:arm_b"], slope.params["visit0:arm_b"]
    assert slope.bse["visit0:arm_b"] < 0.15


# -- one script on one table -------------------------------------------------------------


def test_a_script_is_run_in_its_folder_and_what_it_raises_is_recorded(tmp_path: pathlib.Path) -> None:
    script = tmp_path / "f02_example.py"
    script.write_text(
        "import json, warnings\n"
        "rows = open('table.csv', encoding='utf-8').read().splitlines()\n"
        "class ConvergenceWarning(UserWarning):\n    pass\n"
        "if len(rows) > 3:\n    warnings.warn('no', ConvergenceWarning)\n"
        "if len(rows) > 5:\n    raise ValueError('too many rows')\n"
        "json.dump({'estimands': {'n': {'estimate': len(rows), 'se': None, 'p': None, 'support': 30,"
        " 'primary': True}}, 'checks': {'kept_rows': len(rows) - 1}}, open('results.json', 'w'))\n",
        encoding="utf-8", newline="\n")
    folder = tmp_path / "work"
    folder.mkdir()
    (folder / "table.csv").write_text("a\n1\n", encoding="utf-8", newline="\n")
    calm = B.run_script(script, folder)
    assert calm.ok and calm.estimands["n"]["estimate"] == 2 and calm.trouble == [] and calm.checks == {"kept_rows": 1.0}
    assert not (folder / B.RESULTS_FILE).exists()
    (folder / "table.csv").write_text("a\n1\n2\n3\n", encoding="utf-8", newline="\n")
    loud = B.run_script(script, folder)
    assert loud.ok and loud.trouble == ["ConvergenceWarning"]
    (folder / "table.csv").write_text("a\n1\n2\n3\n4\n5\n", encoding="utf-8", newline="\n")
    stopped = B.run_script(script, folder)
    assert not stopped.ok and stopped.error.startswith("ValueError: too many rows")
    assert B.runs(calm, loud) == "warns: ConvergenceWarning"
    assert B.runs(calm, stopped).startswith("stops: ValueError")


# -- the pass rule, clause by clause ----------------------------------------------------------


def test_each_clause_of_same_fails_on_its_own_case() -> None:
    real = estimate(1.0, se=0.1, p=1e-20)
    assert B.same(real, estimate(1.1, se=0.1, p=1e-20), math.nan) == ""
    # (a) direction, where the real p is under 0.05
    assert B.same(estimate(0.25, se=0.1, p=0.012), estimate(-0.02, se=0.1, p=0.84), math.nan) == "direction"
    # (b) the significance class, and the band where a flip is not charged
    assert B.same(estimate(0.3, se=0.1, p=0.003), estimate(0.1, se=0.1, p=0.32), math.nan) == "significance"
    assert B.same(estimate(0.2, se=0.1, p=0.046), estimate(0.12, se=0.1, p=0.23), math.nan) == ""
    assert B.same(estimate(0.05, se=0.1, p=0.62), estimate(0.21, se=0.1, p=0.035), math.nan) == "significance"
    # (c) size: within 2.77 standard errors, and not past them
    assert B.same(real, estimate(1.27, se=0.1, p=1e-20), math.nan) == ""
    assert B.same(real, estimate(1.28, se=0.1, p=1e-20), math.nan) == "size"
    # (d) precision: the standard errors' ratio inside 0.8 to 1.25
    assert B.same(real, estimate(1.0, se=0.079, p=1e-20), math.nan) == "precision"
    assert B.same(real, estimate(1.0, se=0.126, p=1e-20), math.nan) == "precision"
    # (e) the intervals: met whenever (c) and (d) are, so shown on an estimate with no standard error of its own
    assert B.same(estimate(1.0), estimate(1.27), 0.2) == ""
    assert B.same(estimate(1.0), estimate(1.28), 0.2) == "size"
    # an estimate the other table lacks is never the same
    assert B.same(real, None, math.nan) == "absent"
    assert B.same(real, estimate(math.nan), math.nan) == "absent"


def test_a_rule_the_real_table_keeps_on_every_row_must_be_kept_exactly() -> None:
    real = run_of({"rule": estimate(1.0, primary=True)})
    halves = [run_of({"rule": estimate(1.0)}) for _ in range(8)]
    yards = B.yardsticks(real, halves)
    assert yards["rule"].supported and yards["rule"].h == 0.0
    assert B.judge(real, yards, run_of({"rule": estimate(1.0)})).passed
    broken = B.judge(real, yards, run_of({"rule": estimate(0.98)}))
    assert not broken.passed and broken.failing == {"rule": "size"}


def test_an_estimate_is_supported_only_on_the_real_table_and_all_eight_halves() -> None:
    real = run_of({"a": estimate(1.0, se=0.1, support=22), "b": estimate(1.0, se=0.1, support=21),
                   "c": estimate(1.0, se=0.1, support=500), "d": estimate(1.0, se=0.1, support=None)})
    halves = [run_of({"a": estimate(1.0 + 0.01 * k, support=11), "b": estimate(1.0, support=11),
                      "c": estimate(1.0, support=10 if k == 5 else 300), "d": estimate(1.0, support=None)})
              for k in range(8)]
    yards = B.yardsticks(real, halves)
    assert yards["a"].supported and abs(yards["a"].h - 0.01) < 1e-12
    assert not yards["b"].supported  # 21 people on the real table
    assert not yards["c"].supported  # 10 in one half
    assert yards["d"].supported  # no cell to count, written on all eight halves
    seven = B.yardsticks(real, halves[:7])
    assert not any(y.supported for y in seven.values())
    missing = [run_of({}) if k == 3 else halves[k] for k in range(8)]
    assert not B.yardsticks(real, missing)["a"].supported


def test_a_run_passes_only_with_every_primary_and_nine_in_ten_estimates_the_same() -> None:
    names = [f"e{k}" for k in range(10)]
    real = run_of({n: estimate(1.0, se=0.1, p=1e-20, primary=(n == "e0")) for n in names})
    halves = [run_of({n: estimate(1.0, se=0.14) for n in names}) for _ in range(8)]
    yards = B.yardsticks(real, halves)
    good = {n: estimate(1.0, se=0.1, p=1e-20) for n in names}
    assert B.judge(real, yards, run_of(good)).passed
    one_off = dict(good, e9=estimate(2.0, se=0.1, p=1e-20))
    assert B.judge(real, yards, run_of(one_off)).passed  # 9 of 10
    two_off = dict(one_off, e8=estimate(2.0, se=0.1, p=1e-20))
    assert not B.judge(real, yards, run_of(two_off)).passed  # 8 of 10
    primary_off = dict(good, e0=estimate(2.0, se=0.1, p=1e-20))
    verdict = B.judge(real, yards, run_of(primary_off))
    assert not verdict.passed and verdict.why == "not the same: e0 (size)"
    assert verdict.runs  # it ran; it did not reach the conclusion


def test_each_clause_of_runs_fails_on_its_own_case() -> None:
    real = run_of({"a": estimate(1.0, se=0.1)}, checks={"unparsed_date": 0.0, "kept_rows": 50.0},
                  trouble=["ConvergenceWarning"])
    assert B.runs(real, run_of({"a": estimate(1.0, se=0.1)}, checks={"unparsed_date": 0.005, "kept_rows": 3.0},
                               trouble=["ConvergenceWarning"])) == ""
    assert B.runs(real, run_of({}, ok=False)).startswith("stops")
    assert B.runs(real, run_of({"a": estimate(math.nan)})) == "no estimate a"
    assert B.runs(real, run_of({"a": estimate(1.0)}, trouble=["ConvergenceWarning", "PerfectSeparationWarning"])) \
        == "warns: PerfectSeparationWarning"
    assert B.runs(real, run_of({"a": estimate(1.0)}, checks={"unparsed_date": 0.2})).startswith("parses worse")
    assert B.runs(real, run_of({"a": estimate(1.0)}, checks={"kept_rows": 0.0})) == "keeps no row: kept_rows"


def test_the_null_table_s_script_passes_while_it_invents_no_relation() -> None:
    pairs = {f"{B.PAIR_PREFIX}a{k}~b": estimate(0.0, p=0.5) for k in range(20)}
    real = run_of(pairs)
    halves = [run_of({key: estimate(0.0) for key in pairs}) for _ in range(8)]
    yards = B.yardsticks(real, halves)
    quiet = dict(pairs, **{f"{B.PAIR_PREFIX}a0~b": estimate(0.1, p=0.01)})
    assert B.judge(real, yards, run_of(quiet)).passed  # 1 of 20 related
    loud = dict(pairs, **{f"{B.PAIR_PREFIX}a{k}~b": estimate(0.1, p=0.01) for k in range(4)})
    verdict = B.judge(real, yards, run_of(loud))
    assert not verdict.passed and verdict.null_share == 0.2


def _table_run(table: str, stem: str, twin: "dict", replicate: "dict", shuffled: "dict") -> B.TableRun:
    real = run_of({"x": estimate(1.0, se=0.1, p=1e-20, primary=True)})
    halves = [run_of({"x": estimate(1.0, se=0.14)}) for _ in range(8)]
    sides = {"twin-0": {stem: run_of(twin)}, "replicate-0": {stem: run_of(replicate)},
             "shuffled-0": {stem: run_of(shuffled)}}
    return B.TableRun(table, 20000, 1, (0,), {stem: real}, {stem: halves}, sides, {"relations_drawn": False}, 0.0)


def test_the_controls_void_a_family_and_invalidate_a_blind_run(monkeypatch: pytest.MonkeyPatch) -> None:
    hit = {"x": estimate(1.0, se=0.1, p=1e-20)}
    miss = {"x": estimate(0.0, se=0.1, p=0.9)}
    monkeypatch.setattr(B, "SCRIPTS", {"f03_one": ("T4", True), "f04_two": ("T4", True), B.NULL_SCRIPT: ("T8", False)})
    nulls = {f"{B.PAIR_PREFIX}a~b": estimate(0.0, p=0.5)}
    null_real = run_of(nulls)
    null_run = B.TableRun("T8", 20000, 1, (0,), {B.NULL_SCRIPT: null_real},
                          {B.NULL_SCRIPT: [run_of(nulls) for _ in range(8)]},
                          {f"{kind}-0": {B.NULL_SCRIPT: run_of(nulls)} for kind in ("twin", "replicate", "shuffled")},
                          {"relations_drawn": False}, 0.0)
    good = [_table_run("T4", "f03_one", miss, hit, miss), _table_run("T4", "f04_two", hit, hit, miss)]
    value = B.kpi_value([*good, null_run], "_20k")
    assert value["controls_hold_20k"] is True and value["void_families_20k"] == []
    assert value["same_rel_20k"] == pytest.approx(2 / 3, abs=1e-3)  # F3 0, F4 1, the null script 1, over 1
    assert value["runs_20k"] == 1.0 and value["null_pairs_share_20k"] == 0.0
    blind = [_table_run("T4", "f03_one", miss, hit, hit), _table_run("T4", "f04_two", hit, hit, hit)]
    assert B.kpi_value([*blind, null_run], "_20k")["controls_hold_20k"] is False
    strict = [_table_run("T4", "f03_one", miss, miss, miss), _table_run("T4", "f04_two", hit, hit, miss)]
    assert B.kpi_value([*strict, null_run], "_20k")["void_families_20k"] == ["F3"]


def test_the_halves_keep_a_patient_s_rows_together_and_the_shuffle_keeps_each_column() -> None:
    text = T.text("T2", 3000, 9)
    halves = B.halves_of(text, 9)
    assert len(halves) == 8
    rows = text.splitlines()[1:]
    for s in range(4):
        a, b = halves[2 * s].splitlines()[1:], halves[2 * s + 1].splitlines()[1:]
        assert sorted(a + b) == sorted(rows)
        assert not {r.split(",")[0] for r in a} & {r.split(",")[0] for r in b}
    shuffled = B.shuffled_text(text, 4).splitlines()
    assert shuffled[0] == text.splitlines()[0]
    for k in range(len(T.COLUMNS["T2"])):
        assert sorted(r.split(",")[k] for r in shuffled[1:]) == sorted(r.split(",")[k] for r in rows)
    assert shuffled[1:] != rows


def test_the_person_answers_truthfully() -> None:
    assert B.truthful("T1", "age", ["no", "yes", "years", "months"], False) == "yes"
    assert B.truthful("T5", "dose", ["no", "yes", "years"], False) == "no"
    assert B.truthful("T2", "patient_id", ["keep", "identifier"], True) == "identifier"
    assert B.truthful("T7", "guarantor_id", ["keep", "identifier"], True) == "keep"
    assert B.truthful("T7", "guarantor_id", ["keep", "code", "identifier"], False) == "identifier"
    assert B.truthful("T3", "value", ["keep", "identifier"], True) == "keep"
    assert B.truthful("T1", "creat", ["keep", "measurement", "code"], False) == "measurement"
    assert B.truthful("T2", "arm", ["keep", "measurement", "code"], False) == ""
    assert B.truthful("T1", "risk_class", ["measurement", "code", "identifier"], False) == "code"
    assert B.truthful("T6", "test", ["no", "yes"], False) == "no"


def test_the_switched_person_question_is_read_as_the_person_question() -> None:
    """The person question every shipped run puts ("identifies the person", beside `record`) is the person question.

    Read as a record number's question, its `identifier` was given to the
    guarantor's and the staff member's keys of T7, which said both name the
    person: the people were counted by the two together and the table was
    refused at the 1,000-people floor (lane W5-ACC). The patient's key is
    still answered `identifier` there, every other key `keep`.
    """
    from synthtwin import asking

    def entry(*means: "tuple[str, str]") -> "dict":
        return {"answers_you_can_give": [{"answer": answer, "means": words} for answer, words in means]}

    switched = entry(("keep", "not a person -- it repeats for some other reason"),
                     ("identifier", asking.PERSON_ANSWER_MEANS), ("record", asking.RECORD_ANSWER_MEANS))
    first = entry(("keep", "not a person"), ("identifier", "the people the rows are about -- rows sharing a value"))
    record_numbers = entry(("keep", "measurements or counts"), ("code", "codes of a coding system"),
                           ("identifier", "record numbers -- each value names one record, report, sample, visit "
                                          "or person, and it is a key nothing should publish"))
    assert B._asks_for_people(switched) and B._asks_for_people(first)
    assert not B._asks_for_people(record_numbers)
    # Lane MU's route S harness reads the question the same way.
    import twin_routes

    assert twin_routes.asks_for_people(switched) and twin_routes.asks_for_people(first)
    assert not twin_routes.asks_for_people(record_numbers)
    offered = B._offered(switched)
    others = [name for name in T.COLUMNS["T7"] if T.KNOWS["T7"].get(name) == "identifier" and name != T.PERSON["T7"]]
    assert len(others) == 4
    for column in others:
        assert B.truthful("T7", column, offered, B._asks_for_people(switched)) == "keep", column
        assert B.truthful("T7", column, B._offered(record_numbers), B._asks_for_people(record_numbers)) == "identifier"
    assert B.truthful("T7", T.PERSON["T7"], offered, B._asks_for_people(switched)) == "identifier"


def test_f0_is_read_from_the_zoo_s_own_entry() -> None:
    ledger = kpi_rules.load_ledger()
    f0 = B.f0_from_ledger(ledger)
    assert set(f0) == {"F0_twin", "F0_kinds", "F0_from"}
    assert 0.0 <= float(f0["F0_twin"]) <= 1.0 and f0["F0_from"].startswith("K-HZ-01 on ")  # type: ignore[union-attr]
    assert B.f0_from_ledger({"entries": []}) == {}


def test_the_ledger_entry_bounds_only_keys_the_battery_writes() -> None:
    entries = kpi_rules.entries_by_id(kpi_rules.load_ledger())
    entry = entries["K-RU-01"]
    assert entry["headline"] is True and entry["driver"].startswith("tools/measurements/kpi_reliability_battery.py")
    written = set(B.kpi_value([], "_20k"))
    for bounds in (entry["expected"], entry["target"]):
        assert set(bounds) <= written, set(bounds) - written
    assert len(json.dumps(entry, indent=1)) < 12000


# -- the scripts on their real tables, and the whole battery on a small cohort ---------------


def test_every_script_runs_on_its_real_table(tmp_path: pathlib.Path) -> None:
    pytest.importorskip("statsmodels")
    pytest.importorskip("sklearn")
    for table in T.TABLES:
        extra = {B.HOLDOUT_FILE: T.text("T1", 2500, B.holdout_seed(1))} if table == "T1" else {}
        if table == "T5":
            extra = {"cohort.csv": T.text("T1", 2500, 1)}
        found = B.run_side(tmp_path / table, table, T.text(table, 2500, 1), B.catalogue((table,)), extra)
        for stem, run in found.items():
            assert run.ok, (stem, run.error)
            assert run.estimands and all(B.finite(e["estimate"]) for e in run.estimands.values()), stem


def test_the_battery_separates_a_fresh_sample_from_a_shuffled_cohort(tmp_path: pathlib.Path) -> None:
    """The whole battery on T1 at 3,000 rows, one twin seed, below the floor (the test device)."""
    pytest.importorskip("statsmodels")
    pytest.importorskip("sklearn")
    run = B.run_table("T1", 3000, 1, (0,), tmp_path / "T1", below_floor=True)
    assert run.product["not_made"] == {}
    scored = B.score(run)
    assert all(s.real_ok for s in scored)
    relation = [s for s in scored if s.relation]
    fresh = sum(s.sides["replicate"].passed for s in relation)
    shuffled = sum(s.sides["shuffled"].passed for s in relation)
    assert fresh >= 0.6 * len(relation), [s.sides["replicate"].why for s in relation]
    assert shuffled <= 0.25 * len(relation), [s.stem for s in relation if s.sides["shuffled"].passed]
    assert all(s.sides["twin"].runs or s.sides["twin"].why for s in scored)
    value = B.kpi_value([run], "_small")
    assert value["script_runs_small"] == len([s for s in scored if s.family in B.HEADLINE_FAMILIES])
