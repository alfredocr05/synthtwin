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
    assert B.script_files() == sorted(list(B.SCRIPTS) + list(B.EXTENDED_SCRIPTS))
    assert not set(B.SCRIPTS) & set(B.EXTENDED_SCRIPTS)
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


# -- the extended battery (lane STATS-B) ---------------------------------------------------------


def test_the_extended_scripts_are_catalogued_apart_from_k_ru_01_s() -> None:
    """Each extended script reads one table of `ALL_TABLES` by its file name and writes its results; every extended
    family has a script; the catalogue holds them only where asked, so K-RU-01's runs and families are as before
    (mutant: the extended scripts in the default catalogue)."""
    assert set(T.EXTENDED_TABLES) & set(T.TABLES) == set()
    assert {s.stem for s in B.catalogue()} == set(B.SCRIPTS)
    extended = [s for s in B.catalogue(extended=True) if s.stem in B.EXTENDED_SCRIPTS]
    assert {s.stem for s in extended} == set(B.EXTENDED_SCRIPTS)
    assert {s.family for s in extended} == set(B.EXTENDED_FAMILIES)
    assert not set(B.EXTENDED_FAMILIES) & set(B.FAMILIES)
    for script in extended:
        assert script.table in T.ALL_TABLES
        text = script.path.read_text(encoding="utf-8")
        assert f'pd.read_csv("{T.FILES[script.table]}")' in text, script.stem
        assert 'open("results.json", "w"' in text, script.stem
    lines = T.text("T9", 400, 3).splitlines()
    assert lines[0].split(",") == T.COLUMNS["T9"] and T.text("T9", 400, 3) == T.text("T9", 400, 3)
    assert T.text("T9", 400, 3) != T.text("T9", 400, 4)


def test_every_extended_script_runs_on_its_real_table(tmp_path: pathlib.Path) -> None:
    pytest.importorskip("statsmodels")
    pytest.importorskip("sklearn")
    for table in ("T1", "T2", "T9", "T10"):
        scripts = [s for s in B.catalogue((table,), extended=True) if s.stem in B.EXTENDED_SCRIPTS]
        assert scripts, table
        extra = {B.HOLDOUT_FILE: T.text("T1", 2500, B.holdout_seed(1))} if table == "T1" else {}
        found = B.run_side(tmp_path / table, table, T.text(table, 4000, 1), scripts, extra)
        for stem, run in found.items():
            assert run.ok, (stem, run.error)
            assert run.estimands and all(B.finite(e["estimate"]) for e in run.estimands.values()), stem
            assert any(e["primary"] for e in run.estimands.values()), stem


def test_the_extended_value_reads_its_families_alone(monkeypatch: pytest.MonkeyPatch) -> None:
    """`extended_value` counts the extended families and `kpi_value` never does: a run of one headline script and one
    extended script reads 1.0 in each where both pass, and K-RU-01's value is the same with the extended run beside it
    (mutants: the extended families counted in K-RU-01's; the headline counted in the extended value)."""
    hit = {"x": estimate(1.0, se=0.1, p=1e-20)}
    miss = {"x": estimate(0.0, se=0.1, p=0.9)}
    monkeypatch.setattr(B, "SCRIPTS", {"f03_one": ("T4", True)})
    monkeypatch.setattr(B, "EXTENDED_SCRIPTS", {"f17_two": ("T9", True)})
    monkeypatch.setattr(B, "WITH_EXTENDED", True)
    headline = _table_run("T4", "f03_one", hit, hit, miss)
    extended = _table_run("T9", "f17_two", miss, hit, miss)
    alone = B.kpi_value([headline], "_20k")
    beside = B.kpi_value([headline, extended], "_20k")
    for key in ("runs_20k", "same_20k", "same_rel_20k", "script_runs_20k", "families_20k"):
        assert alone[key] == beside[key], key
    value = B.extended_value([headline, extended], "_20k")
    assert value["extended_script_runs_20k"] == 1
    assert value["extended_same_20k"] == 0.0 and value["extended_same_replicate_20k"] == 1.0
    assert value["extended_families_20k"] == {"F17": {"n": 1, "runs": 1.0, "twin": 0.0, "replicate": 1.0,
                                                      "shuffled": 0.0}}


# -- lane STATS-C: the competing death and the analyses the battery had not tried ----------------------------------


def test_the_competing_death_leaves_every_earlier_column_as_it_was_and_ends_follow_up_first() -> None:
    """T9's second follow-up ends at the first of a readmission, a death from another cause and its end, every time
    drawn from a stream of its own: every column before it is the bytes a table drawn without it held; the death draws
    on age and diabetes and never on the treatment, the readmission on the treatment; an exit falls within the
    follow-up (mutant: the times drawn from the table's own stream)."""
    pandas = pytest.importorskip("pandas")
    smf = pytest.importorskip("statsmodels.formula.api")
    frame = _frame("T9", 12000, 5)
    assert list(frame.columns) == T.COLUMNS["T9"] and T.COLUMNS["T9"][-2:] == ["exit_days", "exit_reason"]
    assert set(frame["exit_reason"]) == set(T.EXIT_REASONS)
    assert frame["exit_days"].between(1, T.T9_TRUTH["exit_censor_days"][1]).all()
    # The columns before the exit: the bytes the table held before the exit was added (3,000 rows, seed 5, its first
    # fifteen columns, as batch 4zz's head wrote the whole table).
    import hashlib

    before = "".join(",".join(line.split(",")[:-2]) + "\n" for line in T.text("T9", 3000, 5).splitlines())
    assert hashlib.sha256(before.encode("utf-8")).hexdigest() == (
        "e04cbfae5229b4dd0a0c3e9103a74a5465b37b6c764e9c8f7fb76fe20af07095")
    data = pandas.DataFrame({"time": frame["exit_days"], "age_c": (frame["age"] - 62) / 10,
                             "diabetes": frame["diabetes"].eq("Y").astype(int),
                             "treated": frame["treated"].eq("Y").astype(int)})
    for reason, truth in (("died", T.T9_TRUTH["competing_death"]), ("readmitted", T.T9_TRUTH["readmission"])):
        status = frame["exit_reason"].eq(reason).astype(int).to_numpy()
        fit = smf.phreg("time ~ age_c + diabetes + treated", data=data, status=status, ties="breslow").fit()
        names = list(fit.model.exog_names)
        for term, key, scale in (("age_c", "age", 10.0), ("treated", "treated", 1.0)):
            at = names.index(term)
            assert abs(fit.params[at] - scale * truth[key]) < 4 * fit.bse[at], (reason, term, fit.params[at])
    shares = frame["exit_reason"].value_counts(normalize=True)
    assert 0.05 < shares["died"] < 0.25 and 0.1 < shares["readmitted"] < 0.4, shares.to_dict()


def _fine_gray_on(tmp_path: pathlib.Path, text: str) -> "dict[str, dict]":
    folder = tmp_path / "fine-gray"
    found = B.run_side(folder, "T9", text, [s for s in B.catalogue(("T9",), extended=True) if s.stem == "f29_fine_gray"],
                       {})
    run = found["f29_fine_gray"]
    assert run.ok, run.error
    return run.estimands


def test_the_fine_gray_script_is_cox_s_model_where_nobody_dies_of_another_cause(tmp_path: pathlib.Path) -> None:
    """The battery's Fine-Gray estimator, written out in the script, is checked against Cox's model where it must equal
    it: with every death from another cause read as censored, the subdistribution's risk set is the cause's own and
    the two agree to 1e-6; with those who died kept, the coefficients move off the cause-specific ones, and age, which
    brings the competing death, lowers the readmission's subdistribution hazard below its cause-specific one
    (mutant: those who died dropped from the weighted risk set)."""
    pandas = pytest.importorskip("pandas")
    smf = pytest.importorskip("statsmodels.formula.api")
    text = T.text("T9", 6000, 2)
    censored_only = text.replace(",died\n", ",censored\n")
    frame = pandas.read_csv(io.StringIO(censored_only))
    data = pandas.DataFrame({"time": frame["exit_days"], "status": frame["exit_reason"].eq("readmitted").astype(int),
                             "treated": frame["treated"].eq("Y").astype(int),
                             "age_c": (frame["age"] - 62) / 10, "diabetes": frame["diabetes"].eq("Y").astype(int)})
    cox = smf.phreg("time ~ treated + age_c + diabetes", data=data, status=data["status"].to_numpy(),
                    ties="breslow").fit()
    names = list(cox.model.exog_names)
    plain = _fine_gray_on(tmp_path, censored_only)
    for term in ("treated", "age_c", "diabetes"):
        assert abs(plain[f"subdistribution_{term}"]["estimate"] - cox.params[names.index(term)]) < 1e-6, term
        assert abs(plain[f"subdistribution_{term}"]["se"] - cox.bse[names.index(term)]) < 1e-6, term
    weighted = _fine_gray_on(tmp_path, text)
    moved = [abs(weighted[f"subdistribution_{term}"]["estimate"] - plain[f"subdistribution_{term}"]["estimate"])
             for term in ("treated", "age_c", "diabetes")]
    assert max(moved) > 0.01, moved
    # Older patients die of other causes more often, so their subdistribution hazard of a readmission is lower than
    # their cause-specific one.
    assert weighted["subdistribution_age_c"]["estimate"] < plain["subdistribution_age_c"]["estimate"]


# -- lane STATS-D: T10 (operations) and the analyses of the owner's list ---------------------------------------------


def test_t10_holds_its_crossed_surgeons_and_anaesthetists_its_zeros_and_its_missing_albumin() -> None:
    """T10's surgeons and anaesthetists are the same in every table seed (their effects from fixed streams), so a real
    table and its fresh sample are two draws of one hospital: a surgeon's mean minutes at one seed foretell them at
    another; the crossed model gives back both spreads; albumin is missing more often after a complication; its bytes
    are pinned (mutant: the effects drawn from the table's seed)."""
    pandas = pytest.importorskip("pandas")
    numpy = pytest.importorskip("numpy")
    smf = pytest.importorskip("statsmodels.formula.api")
    import hashlib

    first, second = _frame("T10", 12000, 5), _frame("T10", 12000, 6)
    assert list(first.columns) == T.COLUMNS["T10"] and T.FILES["T10"] == "operations.csv"
    assert "T10" in T.EXTENDED_TABLES and "T10" not in T.TABLES
    by_first = first.groupby("surgeon")["minutes"].mean()
    by_second = second.groupby("surgeon")["minutes"].mean()
    assert by_first.corr(by_second) > 0.8, by_first.corr(by_second)
    data = first.assign(complication=first["complication"].eq("Y").astype(int),
                        emergency=first["emergency"].eq("Y").astype(int),
                        age_c=(first["age"] - 60) / 10, everyone=1)
    fit = smf.mixedlm("minutes ~ age_c + emergency + complication", data=data, groups="everyone",
                      vc_formula={"s": "0 + C(surgeon)", "a": "0 + C(anaesthetist)"}).fit()
    spreads = dict(zip(fit.model.exog_vc.names, numpy.sqrt(numpy.asarray(fit.vcomp))))
    truth = T.T10_TRUTH["minutes"]
    assert 0.6 * truth["surgeon_sd"] < spreads["s"] < 1.4 * truth["surgeon_sd"], spreads
    assert 0.4 * truth["anaesthetist_sd"] < spreads["a"] < 1.6 * truth["anaesthetist_sd"], spreads
    assert abs(fit.params["complication"] - truth["complication"]) < 4 * fit.bse["complication"]
    missing = first["albumin"].isna()
    assert missing[data["complication"] == 1].mean() > 1.8 * missing[data["complication"] == 0].mean()
    assert T.text("T10", 400, 3) == T.text("T10", 400, 3) != T.text("T10", 400, 4)
    # T10's bytes as this lane wrote it (3,000 rows, seed 5): a change to its draws changes every twin measured on it.
    assert hashlib.sha256(T.text("T10", 3000, 5).encode("utf-8")).hexdigest() == (
        "f11e1df1fb26710d636f99489776ee990ab0a737da334fd220658f9c84057998")
    pandas.testing.assert_series_equal(first["patient_id"], _frame("T10", 12000, 5)["patient_id"])


def _extended_on(tmp_path: pathlib.Path, table: str, stem: str, text: str) -> "dict[str, dict]":
    extra = {B.HOLDOUT_FILE: T.text("T1", 2500, B.holdout_seed(1))} if table == "T1" else {}
    found = B.run_side(tmp_path / stem, table, text, [s for s in B.catalogue((table,), extended=True)
                                                      if s.stem == stem], extra)
    run = found[stem]
    assert run.ok, run.error
    return {**run.context, **run.estimands}


def test_the_clustered_roc_area_is_the_plain_area_with_a_wider_error(tmp_path: pathlib.Path) -> None:
    """f38's area over every visit is the Mann-Whitney area of all rows, and its Obuchowski standard error, clustered
    by patient, is wider than the rows-as-independent one on a table of several rows a patient; with every row its own
    patient the two agree (mutant: the clusters not read)."""
    numpy = pytest.importorskip("numpy")
    pytest.importorskip("scipy")
    text = T.text("T2", 6000, 3)
    found = _extended_on(tmp_path, "T2", "f38_repeated_roc", text)
    frame = _frame("T2", 6000, 3)
    y = frame["hospitalized"].eq("Y").to_numpy()
    sbp = frame["sbp"].to_numpy(dtype=float)
    pos, neg = sbp[y], sbp[~y]
    plain = float(numpy.mean((pos[:, None] > neg[None, :]) + 0.5 * (pos[:, None] == neg[None, :])))
    assert abs(found["area_pressure_all_visits"]["estimate"] - plain) < 1e-9
    assert found["clustered_over_naive_se"]["estimate"] > 1.15, found["clustered_over_naive_se"]
    lines = text.splitlines()
    alone = lines[0] + "\n" + "".join(f"P{1000000 + k}," + line.split(",", 1)[1] + "\n"
                                       for k, line in enumerate(lines[1:]))
    separate = _extended_on(tmp_path, "T2", "f38_repeated_roc", alone)
    assert abs(separate["clustered_over_naive_se"]["estimate"] - 1.0) < 0.02, separate["clustered_over_naive_se"]


def test_the_frailty_script_finds_the_surgeons_frailty_and_none_where_the_surgeons_are_shuffled(
        tmp_path: pathlib.Path) -> None:
    """f32_shared_frailty's Weibull model with a gamma frailty by surgeon gives back the frailty's variance T10 sets (its
    thirty surgeons' realised spread about it) and the complication's log hazard ratio; with the surgeons shuffled
    over the rows the frailty's variance falls near nought (mutant: the frailty's term left out of the likelihood)."""
    pytest.importorskip("scipy")
    pytest.importorskip("statsmodels")
    import random

    text = T.text("T10", 12000, 4)
    found = _extended_on(tmp_path, "T10", "f32_shared_frailty", text)
    truth = T.T10_TRUTH["readmission"]
    assert 0.15 < found["frailty_variance"]["estimate"] < 0.9, found["frailty_variance"]
    assert abs(found["frailty_complication"]["estimate"] - truth["complication"]) < 4 * found[
        "frailty_complication"]["se"]
    lines = text.splitlines()
    place = lines[0].split(",").index("surgeon")
    surgeons = [line.split(",")[place] for line in lines[1:]]
    random.Random(1).shuffle(surgeons)
    shuffled = lines[0] + "\n" + "".join(",".join(line.split(",")[:place] + [surgeon] + line.split(",")[place + 1:])
                                          + "\n" for line, surgeon in zip(lines[1:], surgeons))
    flat = _extended_on(tmp_path, "T10", "f32_shared_frailty", shuffled)
    assert flat["frailty_variance"]["estimate"] < 0.05, flat["frailty_variance"]


def test_the_mediation_script_splits_the_total_effect(tmp_path: pathlib.Path) -> None:
    """f37's indirect and direct effects add to its total, and the total is the exposure's coefficient in the outcome's
    model without the mediator to within two of its standard errors (a binary mediator through a logistic model, so
    not exactly); the indirect effect is
    the complication's coefficient times the average change in its chance (mutant: the indirect effect read on the
    log odds scale)."""
    smf = pytest.importorskip("statsmodels.formula.api")
    numpy = pytest.importorskip("numpy")
    text = T.text("T1", 8000, 2)
    found = _extended_on(tmp_path, "T1", "f37_mediation", text)
    assert abs(found["indirect"]["estimate"] + found["direct"]["estimate"] - found["total"]["estimate"]) < 1e-12
    frame = _frame("T1", 8000, 2)
    data = frame.assign(log_stay=numpy.log(frame["stay_days"]), diabetes=frame["diabetes"].eq("Y").astype(int),
                        age_c=(frame["age"] - 57) / 10)
    reduced = smf.ols("log_stay ~ diabetes + age_c + risk_class", data=data).fit()
    assert abs(found["total"]["estimate"] - reduced.params["diabetes"]) < 2 * found["total"]["se"], (
        found["total"], reduced.params)
    assert 0.0 < found["indirect"]["estimate"] < found["path_complication_to_stay"]["estimate"] * 0.2


def test_the_zero_inflated_script_finds_the_patients_who_never_come(tmp_path: pathlib.Path) -> None:
    """f31's zero-inflated model gives back T10's never-comers: their share falls with age and in emergencies (the
    inflation's terms within four standard errors of T10's), and its count part the complication's effect (mutant:
    the inflation's columns swapped for the count's)."""
    pytest.importorskip("statsmodels")
    found = _extended_on(tmp_path, "T10", "f31_zero_inflated_visits", T.text("T10", 12000, 4))
    truth = T.T10_TRUTH["visits_after"]
    for key, value in (("zinb_inflate_age_c", 10 * truth["structural_zero_age"]),
                       ("zinb_inflate_emergency", truth["structural_zero_emergency"]),
                       ("zinb_complication", truth["complication"])):
        assert abs(found[key]["estimate"] - value) < 4 * found[key]["se"], (key, found[key])


def test_the_incidence_differences_carry_a_standard_error_the_spread_of_tables_bears_out(tmp_path: pathlib.Path) -> None:
    """f29's differences of two cumulative incidences at a year carry their delta-method standard error (Marubini and
    Valsecchi): over sixteen independent tables its mean is the spread of the difference across them, within 0.75 to
    1.3 times it, for the readmission and for the competing death (mutant: one group's variance read as the
    difference's). Before lane STATS-D the differences carried none and the battery's half-split
    yardstick, read on four splits, judged them: a fresh sample passed three runs of nine."""
    pytest.importorskip("pandas")
    pytest.importorskip("statsmodels")
    import statistics

    keys = ("readmitted_by_a_year_treated_minus_not", "death_by_a_year_treated_minus_not")
    values: "dict[str, list[float]]" = {key: [] for key in keys}
    errors: "dict[str, list[float]]" = {key: [] for key in keys}
    for seed in range(300, 316):
        found = _extended_on(tmp_path, "T9", "f29_cumulative_incidence", T.text("T9", 6000, seed))
        for key in keys:
            values[key] += [found[key]["estimate"]]
            errors[key] += [found[key]["se"]]
            assert found[key]["p"] is not None, key
    for key in keys:
        ratio = statistics.mean(errors[key]) / statistics.stdev(values[key])
        assert 0.75 < ratio < 1.3, (key, ratio)


def test_the_weighted_kappa_carries_a_standard_error_the_spread_of_tables_bears_out(tmp_path: pathlib.Path) -> None:
    """f17's quadratic weighted kappa carries its large-sample standard error (Fleiss, Cohen and Everitt): over
    sixteen independent tables its mean is the spread of the kappa across them, within 0.7 to 1.4 times it (mutant:
    the error's centring term left out). Before lane STATS-D it carried none and the half-split yardstick, near
    nought for so stable an estimate, judged it: twins within 0.003 of the real kappa failed it."""
    pytest.importorskip("pandas")
    pytest.importorskip("sklearn")
    pytest.importorskip("statsmodels")
    import statistics

    values: "list[float]" = []
    errors: "list[float]" = []
    for seed in range(400, 416):
        found = _extended_on(tmp_path, "T9", "f17_reader_agreement", T.text("T9", 6000, seed))
        values += [found["quadratic_weighted_kappa"]["estimate"]]
        errors += [found["quadratic_weighted_kappa"]["se"]]
    ratio = statistics.mean(errors) / statistics.stdev(values)
    assert 0.7 < ratio < 1.4, ratio
