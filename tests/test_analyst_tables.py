"""The six seeded tables carry the truths their truth files state (plan P4-D398).

`tests/analyst_tables.py` builds the analyst battery's tables and states,
beside each, the values its own code sets. Those values are what the
battery's targeted panel is written to find, so a generator that drifted
from its truth file would leave every seeded-truth KPI measuring the
wrong thing. Each truth is checked here on the real table at seed 1, by
the kit (itself held to closed forms in `tests/test_analyst_kit.py`):

* every coefficient a truth file states, within four standard errors;
* each curve, by the generator's exact functional form (a squared term,
  a hinge, the creatinine J's two arms): the targeted panel reads curves
  through restricted cubic splines, whose straight outer arms bend a
  parabola's estimate near the outer knots -- which is no fault of a twin
  and is never what a KPI compares, since a KPI asks the twin for the
  real table's own estimate;
* each shape (overdispersion, the centre's censoring, the dose formula,
  the null table's 5 %), and the shares and counts the tables are built
  to have.
"""

from __future__ import annotations

import pytest

import analyst_battery as B
import analyst_kit as K
import analyst_tables as T

SIZES = {"ST1": 5000, "ST2": 5000, "ST3": 5000, "ST4": 8000, "ST5": 3000, "ST6": 6000}
SEED = 1


@pytest.fixture(scope="module")
def panels() -> "dict[str, tuple[B.View, B.Panel]]":
    """Each table at its size and seed 1, read as an analyst would, with its targeted panel run."""
    out = {}
    for table, rows in SIZES.items():
        view = B.read(T.text(table, rows, SEED), table)
        out[table] = (view, B.run_panel(B.TARGETED[table](view), view))
    return out


def test_every_targeted_analysis_runs_on_every_real_table(panels: "dict") -> None:
    """No analysis of the targeted panel stops on the table it was written for."""
    stopped = {t: {n: s for n, s in p.status.items() if s != "ok"} for t, (_v, p) in panels.items()}
    assert all(not s for s in stopped.values()), stopped


COEFFICIENTS = [
    (table, name) for table, truths in T.TRUTHS.items()
    for name, (key, value) in truths.items()
    if value is not None and ":" in key and "/curve:" not in key and "/null:" not in key
    and key != "ST2/mixed:icc"
]


@pytest.mark.parametrize("table,name", COEFFICIENTS)
def test_each_seeded_coefficient_is_recovered_within_four_standard_errors(
        panels: "dict", table: str, name: str) -> None:
    """The real table's own estimate of each stated coefficient lies within 4 SE of the generator's value."""
    key, value = T.TRUTHS[table][name]
    estimate = panels[table][1].estimates[key]
    assert estimate.se and abs(estimate.value - value) <= 4.0 * estimate.se, (
        f"{table} {name}: {estimate.value:.3f} (se {estimate.se:.3f}) against the seeded {value:.3f}")


def _fit_exact(view: B.View, curve_terms: "list[tuple[str, K.Term]]",
               extra: "dict[str, object]") -> K.Fit:
    """Death on the generator's own terms: the hinge at 60, ventilation and its over-75 term, the rest."""
    columns: "dict[str, object]" = {
        "age": view.num("age"), "vent": view.num("ventilated"), "lact4": view.above("lactate", 4.0),
        "urban": view.eq("urban", "yes"), "diab": view.num("diabetes"), "cur": view.eq("smoker", "current")}
    columns.update(extra)
    cols, y = B.complete(columns, view.num("died"))
    terms = [("int", K.intercept),
             ("hinge", lambda c: [max(0.0, a - 60.0) for a in c["age"]]),
             ("vent", B.col("vent")),
             ("vent_old75", lambda c: [v * float(a > 75) for v, a in zip(c["vent"], c["age"])]),
             ("lact4", B.col("lact4")), ("urban", B.col("urban")),
             ("parity", lambda c: [float(x != y) for x, y in zip(c["cur"], c["diab"])])]
    return K.glm(K.Design(cols, terms + curve_terms), y, "logistic")


def test_the_curves_are_the_generators_own_shapes(panels: "dict") -> None:
    """ST1's J in age (0.006 a squared year) and hinge at 60 (0.07 a year); ST6's U and J."""
    st1 = panels["ST1"][0]
    cols, y = B.complete({"age": st1.num("age"), "urban": st1.eq("urban", "yes"),
                          "glucose": st1.num("glucose")}, st1.num("sbp"))
    fit = K.ols(K.Design(cols, [("int", K.intercept), ("sq", lambda c: [(a - 40.0) ** 2 for a in c["age"]]),
                                ("urban", B.col("urban")), ("glucose", B.col("glucose"))]), y)
    value, se = fit.coef("sq")
    assert abs(value - 0.006) <= 4 * se, (value, se)
    value, se = _fit_exact(st1, [], {}).coef("hinge")
    assert abs(value - 0.07) <= 4 * se, (value, se)
    st6 = panels["ST6"][0]
    fit6 = _fit_exact(st6, [
        ("u", lambda c: [(g - 100.0) ** 2 for g in c["glucose"]]),
        ("j_low", lambda c: [(1.0 - x) ** 2 if x < 1.0 else 0.0 for x in c["cr"]]),
        ("j_high", lambda c: [x - 1.0 if x >= 1.0 else 0.0 for x in c["cr"]])],
        {"glucose": st6.num("glucose"), "cr": st6.num("creatinine")})
    for name, seeded in (("u", 0.0012), ("j_low", 2.0), ("j_high", 1.2)):
        value, se = fit6.coef(name)
        assert abs(value - seeded) <= 4 * se, (name, value, se)


def test_the_shapes_the_truth_files_state_hold(panels: "dict") -> None:
    """Overdispersed procedures, the ICC near 0.72, the centres' censoring, the dose formula, a null 5 %."""
    est = {t: p.estimates for t, (_v, p) in panels.items()}
    assert est["ST1"]["ST1/poisson:procedures_dispersion"].value > 1.5
    assert abs(est["ST2"]["ST2/mixed:icc"].value - 0.64 / 0.89) < 0.04
    assert est["ST3"]["ST3/logistic:censored_low_centres"].value > 1.0
    assert est["ST4"]["ST4/ols:dose_r2"].value > 0.9
    assert est["ST4"]["ST4/ols:dose_weight"].value > 0
    assert est["ST5"]["ST5/null:significant_share"].value <= 0.12


def test_the_tables_hold_the_shares_and_counts_they_are_built_to(panels: "dict") -> None:
    """A 2 % readmission, 30 % zero costs, a 0.5 % outcome, twenty chapters with codes under the floor of 11."""
    st1 = panels["ST1"][0]
    assert 0.01 <= sum(st1.num("readmit")) / st1.rows <= 0.035
    assert 0.27 <= sum(1 for c in st1.num("cost") if c == 0.0) / st1.rows <= 0.33
    st4 = panels["ST4"][0]
    assert 0.003 <= sum(st4.num("outcome")) / st4.rows <= 0.009
    codes: "dict[str | None, int]" = {}
    for code in st4.text("code"):
        codes[code] = codes.get(code, 0) + 1
    assert len({c[:1] for c in codes if c}) == 20
    assert len(codes) <= 500 and any(n < 11 for n in codes.values())
    st3 = panels["ST3"][0]
    days, which = st3.days("entry_date", ["event_date", "censor_date"])
    assert all(w >= 0 for w in which) and min(days) >= 1
    st2 = panels["ST2"][0]
    per: "dict[str | None, int]" = {}
    for sid in st2.text("sid"):
        per[sid] = per.get(sid, 0) + 1
    assert len(per) == T.subjects_for(SIZES["ST2"]) and max(per.values()) <= 8


@pytest.mark.parametrize("table", T.TABLES)
def test_a_table_is_its_seeds_bytes_and_every_line_holds_every_column(table: str) -> None:
    """The same seed gives the same bytes and another seed others; no cell holds a comma or a line break."""
    first, again, other = T.text(table, 400, 5), T.text(table, 400, 5), T.text(table, 400, 6)
    assert first == again and first != other
    lines = first.splitlines()
    assert lines[0].split(",") == T.HEADERS[table]
    assert all(len(line.split(",")) == len(T.HEADERS[table]) for line in lines[1:])
