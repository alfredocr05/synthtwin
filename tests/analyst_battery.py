"""The analyst battery: "stable statistical results", made measurable (plan P4-D398).

THE ONE SENTENCE IT TESTS. For every analysis a researcher might run,
the twin's answer should sit about as close to the real table's answer
as a second, independent sample of the same size would. The yardstick is
the real table against itself: split it into halves four ways (bits 0 to
3 of sixteen SplitMix64 groups, as M6's half split does), and an
estimate's yardstick ``h`` is the root mean square of half A's value
minus half B's. A twin is INSIDE for that estimate when it lies within
``h`` of the real value. A fresh sample is inside about 77 % of the
time; nothing here asks for more than the fresh sample scores.

WHAT IS RUN. Six seeded tables (`tests/analyst_tables.py`) with known
truths. On each, two panels, every table read with `pandas.read_csv`
exactly as an analyst's script would read it:

* the TARGETED panel -- for each seeded truth, the analysis an epidemiologist
  would write to find it, and the naive misspecified models analysts
  actually fit (a straight line, no interaction), because a twin must
  give back the answer to a wrong model too;
* the AUTOMATIC panel, generated from the schema alone, because the
  person may not know the analyses in advance: two-valued columns as
  outcomes of logistic models, counts of Poisson models, other numbers
  of linear models, a detected time and event pair of a Cox model;
  predictors ranked by their strength on the real table, splines on
  numbers at the real table's quantile knots, label levels of at least
  22 rows, the five strongest predictors' pairwise products (a quarter
  of the terms kept for them), and the terms capped by the events per
  variable (ten events a term; Peduzzi et al. 1996) and by the tier's
  cap; in a logistic model an indicator
  term only where its own ones and zeros hold 22 events and 22
  non-events. Every choice is fixed on the real table and then asked of
  every other table unchanged, each number held to the range the real
  table showed, as a model fitted there is applied. At the slow tier a
  trained model predicts every two-valued column it can learn.

THE TWO CONTROLS, IN EVERY RUN. The FRESH REPLICATE is the same
generator at another seed: what a perfect twin scores in this very run.
The SHUFFLED TWIN is the real table with every column shuffled on its
own: what a twin with no joint structure scores, which is today's twin
(CLAUDE.md: "It carries no cross-column structure at all"). Every KPI's
target is stated relative to the replicate, and every KPI value carries
`controls_hold`, false -- the run VOID, and the KPI red -- unless the
replicate passes the KPI's control and the shuffled twin fails it. Where
a shuffle cannot fail a check, the negative control is named instead:
twin-seed stability (a shuffle adds no noise of its own) uses a THIN
REPLICATE, a tenth of the rows resampled back to the full count; the null
table (on which a shuffle IS a perfect twin) uses the structured table.

SUPPORTED ESTIMATES ONLY. An estimate is scored only where every cell
defining it holds at least 22 rows on the real table and at least 11 in
each of the eight halves -- on a two-valued outcome, events and
non-events alike -- and only where its analysis ran on the real table
and all eight halves. A RULE the real table keeps on every row (the dose
formula, an event date present exactly where the status is not
censored) is read as the share of rows breaking it, supported by the
rows it reads: its yardstick is 0, and a table is inside only where it
breaks the rule exactly as often as the real one. A MARGIN
(tag 'margin': one column's own count, which a column-wise shuffle keeps
exactly, such as ST2's rows per subject) is scored where it is read on
its own and left out of the KPIs of joint structure.

THE TIERS. `run_tables(..., tier="fast")` is the suite's part: ST1 and
ST2 at 5,000 rows, one table seed, one twin seed, the controls and
today's twin. The slow driver `tools/measurements/kpi_analyst_battery.py`
runs all six tables at 20,000 rows over table seeds 1 to 3 and twin
seeds 0 to 4, and at 200,000 rows one seed each.

Nothing here changes the product: the twin is made by the product's own
path (`kpi_shapes.describe`, `generation.generate`, `rendering`), and
this module only reads what it writes.
"""

from __future__ import annotations

import array
import dataclasses
import io
import math
import pathlib
import random
import statistics
import time
from typing import Callable, Iterator

import analyst_kit as K
import analyst_tables as T

SUPPORT = 22
# Each half's own floor: 11 rows in every defining cell of every half.
HALF_SUPPORT = SUPPORT // 2
Z = 1.959963984540054
FAMILIES = {
    "F1": "subgroup rates",
    "F2": "correlations",
    "F3": "linear regression",
    "F4": "logistic regression",
    "F5": "count regression",
    "F6": "time to event",
    "F7": "several rows per subject",
    "F8": "trained models",
    "F9": "missing data",
}
# The families the twin's report would name, one line each (K-BC-11):
# F1 to F9 and F10, the analyst's code running at all.
REPORT_FAMILIES = tuple(FAMILIES) + ("F10",)
REPORT_HEADING = "What you can analyse on this twin"
TIERS = {
    # rows, table seeds, twin seeds, automatic term cap, automatic outcomes, pMSE key columns, boosting
    # rounds, and which outcomes a trained model predicts: the seeded one, or every two-valued column
    "fast": {"rows": 5000, "tables": ("ST1", "ST2"), "seeds": (1,), "twins": (0,),
             "cap": 8, "outcomes": 6, "keys": 6, "rounds": 40, "trained": "seeded"},
    "slow": {"rows": 20000, "tables": T.TABLES, "seeds": (1, 2, 3), "twins": (0, 1, 2, 3, 4),
             "cap": 16, "outcomes": 99, "keys": 8, "rounds": 60, "trained": "binary"},
    "night": {"rows": 200000, "tables": T.TABLES, "seeds": (1,), "twins": (0,),
              "cap": 16, "outcomes": 99, "keys": 8, "rounds": 60, "trained": "seeded"},
}
# The controls' discriminator and trained models are run at these twin
# seeds only (today's twin at every seed): they are the costliest parts,
# and a control's median needs no more.
CONTROL_HEAVY_SEEDS = (0, 1)
# The seeded outcomes a trained model predicts (F8, K-BC-04), per table.
# ST4's readmission is left out: its signal is a pure three-way parity,
# whose every pair margin is flat, so a greedy tree finds no first split
# on the real table either (measured: AUC 0.48 trained on half A). At the
# slow tier every other two-valued column is an outcome as well, where a
# model trained on half A reaches TRAINED_AUC on half B (S2 3.2: one
# boosting model per binary outcome); below it a model has nothing to
# carry, and its AUC's yardstick measures noise.
PREDICTED = {"ST1": "died", "ST6": "died"}
TRAINED_AUC = 0.6
# A family with fewer supported estimates does not set K-BC-01's worst family.
FAMILY_MINIMUM = 5


class AnalysisError(Exception):
    """The analyst's script stopping on this table, with the reason a person would see."""

    def __init__(self, kind: str, message: str) -> None:
        super().__init__(f"{kind}: {message}")
        self.kind = kind


@dataclasses.dataclass(frozen=True)
class Estimate:
    """One number an analysis produces, with its standard error and its smallest defining cell."""

    key: str
    family: str
    value: float
    se: "float | None"
    support: int
    tags: "tuple[str, ...]" = ()


@dataclasses.dataclass
class Analysis:
    """A named analysis: a function of a table view returning its estimates."""

    name: str
    run: "Callable[[View], list[Estimate]]"


@dataclasses.dataclass
class Panel:
    """Every estimate of one table, and how each analysis ended on it ('ok' or why it stopped)."""

    estimates: "dict[str, Estimate]"
    status: "dict[str, str]"


# -- one table as an analyst's script sees it ---------------------------


class View:
    """A table read by `pandas.read_csv`, with the column readings an analyst's code makes.

    A column read as text where numbers are asked for stops the analysis
    ('not numbers'), as `df.age / 10` stops on a text column. Numbers are
    held as `array('d')`, eight bytes a cell.
    """

    def __init__(self, frame: object, name: str) -> None:
        self.frame = frame
        self.name = name
        self.rows = len(frame)  # type: ignore[arg-type]
        self._numbers: "dict[str, array.array]" = {}
        self._labels: "dict[str, list[str | None]]" = {}
        self._derived: "dict[tuple[str, str, str], list[float]]" = {}

    def has(self, column: str) -> bool:
        return column in self.frame.columns  # type: ignore[attr-defined]

    def num(self, column: str) -> "array.array":
        """The column as floats, NaN where the cell is empty."""
        if column not in self._numbers:
            import pandas

            series = self.frame[column]  # type: ignore[index]
            if not pandas.api.types.is_numeric_dtype(series):
                raise AnalysisError("not numbers", f"{column} is read as text")
            self._numbers[column] = array.array("d", series.astype(float).tolist())
        return self._numbers[column]

    def text(self, column: str) -> "list[str | None]":
        """The column as text, None where the cell is empty; whole numbers without '.0'."""
        if column not in self._labels:
            out: "list[str | None]" = []
            for v in self.frame[column].tolist():  # type: ignore[index]
                if v is None or (isinstance(v, float) and v != v):
                    out += [None]
                elif isinstance(v, float) and v == int(v):
                    out += [str(int(v))]
                else:
                    out += [str(v)]
            self._labels[column] = out
        return self._labels[column]

    def eq(self, column: str, value: str) -> "list[float]":
        """1.0 where the cell is ``value``, 0.0 elsewhere, NaN where it is empty."""
        key = ("eq", column, value)
        if key not in self._derived:
            self._derived[key] = [math.nan if v is None else float(v == value)
                                  for v in self.text(column)]
        return self._derived[key]

    def above(self, column: str, cut: float) -> "list[float]":
        """1.0 where the number exceeds ``cut``, 0.0 at or below it, NaN where empty."""
        return [math.nan if v != v else float(v > cut) for v in self.num(column)]

    def missing(self, column: str) -> "list[float]":
        """1.0 where the cell is empty."""
        return [1.0 if v is None else 0.0 for v in self.text(column)]

    def days(self, start: str, ends: "list[str]") -> "tuple[list[float], list[int]]":
        """Days from ``start`` to the first present of ``ends``, and which end it was (-1: none).

        Parsed with `pandas.to_datetime` at the ISO format, as an analyst
        would; a cell that does not parse stops the analysis.
        """
        import pandas

        try:
            first = pandas.to_datetime(self.frame[start], format="%Y-%m-%d")  # type: ignore[index]
            later = [pandas.to_datetime(self.frame[e], format="%Y-%m-%d") for e in ends]  # type: ignore[index]
        except (ValueError, TypeError) as error:
            raise AnalysisError("not dates", str(error)[:80]) from error
        base = first.tolist()
        days = [math.nan] * self.rows
        which = [-1] * self.rows
        for k, column in enumerate(later):
            for i, v in enumerate(column.tolist()):
                if which[i] < 0 and v == v and base[i] == base[i]:
                    days[i] = float((v - base[i]).days)
                    which[i] = k
        return days, which

    def date_days(self, column: str) -> "array.array":
        """An ISO date column as days since 1970-01-01, NaN where empty or unreadable."""
        import pandas

        parsed = pandas.to_datetime(self.frame[column], format="%Y-%m-%d", errors="coerce")  # type: ignore[index]
        epoch = pandas.Timestamp("1970-01-01")
        return array.array("d", [math.nan if v != v else float((v - epoch).days) for v in parsed.tolist()])

    def subset(self, rows: "list[int]", name: str) -> "View":
        """The view of some rows, in their order (a half of the table)."""
        return View(self.frame.iloc[rows].reset_index(drop=True), name)  # type: ignore[attr-defined]


def read(source: "str | pathlib.Path", name: str) -> View:
    """A table read exactly as an analyst would: `pandas.read_csv` with its defaults."""
    import pandas

    if isinstance(source, pathlib.Path):
        return View(pandas.read_csv(source), name)
    return View(pandas.read_csv(io.StringIO(source)), name)


# -- designs, supports and estimates ------------------------------------------


def complete(columns: "dict[str, object]", outcome: "object | None" = None,
             keep: "list[bool] | None" = None) -> "tuple[dict[str, list[float]], list[float]]":
    """The rows where every column (and the outcome) is present and ``keep`` holds.

    An analyst's complete-case filter. No row left stops the analysis
    ('empty filter'), as a model fitted to an empty frame does.
    """
    names = list(columns)
    lists = [columns[n] for n in names]
    out: "dict[str, list[float]]" = {n: [] for n in names}
    ys: "list[float]" = []
    rows = len(lists[0]) if lists else len(outcome)  # type: ignore[arg-type]
    for i in range(rows):
        if keep is not None and not keep[i]:
            continue
        if outcome is not None and outcome[i] != outcome[i]:  # type: ignore[index]
            continue
        if any(column[i] != column[i] for column in lists):  # type: ignore[index]
            continue
        for n, column in zip(names, lists):
            out[n] += [column[i]]  # type: ignore[index]
        if outcome is not None:
            ys += [outcome[i]]  # type: ignore[index]
    kept = len(out[names[0]]) if names else len(ys)
    if kept == 0:
        raise AnalysisError("empty filter", "no row keeps every column the model names")
    return out, ys


def col(name: str) -> "K.Term":
    """The term that is a column as it stands."""
    return lambda c: list(c[name])


def scaled(name: str, shift: float, scale: float) -> "K.Term":
    """(column - shift) / scale."""
    return lambda c: [(v - shift) / scale for v in c[name]]


def product(*terms: "K.Term") -> "K.Term":
    """The product of terms (an interaction)."""
    def term(c: "dict[str, list]") -> "list[float]":
        out = terms[0](c)
        for other in terms[1:]:
            out = [a * b for a, b in zip(out, other(c))]
        return out
    return term


def spline(name: str, knots: "list[float]", j: int, scale: float = 1.0) -> "K.Term":
    """The j-th restricted cubic spline term of a column (times ``scale``)."""
    term = K.rcs_term(knots, j, scale)
    return lambda c: [term(v) for v in c[name]]


def supports(design: K.Design, y: "list[float] | None", binary: bool) -> "dict[str, int]":
    """Each term's smallest defining cell.

    An indicator term (every value 0 or 1) is defined by its two groups
    and, on a two-valued outcome, by the events and non-events of each;
    any other term by the whole model's rows (or events and non-events).
    """
    p = len(design.names)
    indicator = [True] * p
    ones = [0.0] * p
    ones_events = [0.0] * p
    events = 0.0
    for start, stop, cols in design.chunks():
        part = y[start:stop] if y is not None else None
        if part is not None:
            events += sum(part)
        for i, column in enumerate(cols):
            if indicator[i] and any(v != 0.0 and v != 1.0 for v in column):
                indicator[i] = False
            ones[i] += sum(column)
            if part is not None:
                ones_events[i] += sum(a * b for a, b in zip(column, part))
    n = design.rows
    whole = int(min(events, n - events)) if binary else n
    out = {}
    for i, name in enumerate(design.names):
        if indicator[i] and ones[i] != n:
            if binary:
                e1, n1 = ones_events[i], ones[i]
                e0, n0 = events - e1, n - n1
                out[name] = int(min(e1, n1 - e1, e0, n0 - e0))
            else:
                out[name] = int(min(ones[i], n - ones[i]))
        else:
            out[name] = whole
    return out


def levels_present(design: K.Design) -> None:
    """Stop where an indicator the model names for a label level has no row ('level missing')."""
    for name, function in design.terms:
        if name.startswith("lvl_") and not any(v != 0.0 for v in function(design.columns)):
            raise AnalysisError("level missing", f"no row holds {name[4:]}")


def coefs(fit: K.Fit, prefix: str, family: str, support: "dict[str, int]",
          names: "list[str]", tags: "tuple[str, ...]" = ()) -> "list[Estimate]":
    """One estimate per named coefficient, keyed `prefix:name`."""
    out = []
    for name in names:
        value, se = fit.coef(name)
        out += [Estimate(f"{prefix}:{name}", family, value, se, support[name], tags)]
    return out


def one(fit: K.Fit, key: str, name: str, family: str, support: "dict[str, int]",
        tags: "tuple[str, ...]" = ()) -> Estimate:
    """One coefficient under a key of its own (a seeded truth's estimate)."""
    value, se = fit.coef(name)
    return Estimate(key, family, value, se, support[name], tags)


def near(values: "list[float]", y: "list[float] | None", point: float, half: float,
         binary: bool) -> int:
    """A curve point's cell: rows within ``half`` of ``point`` (with their events and non-events)."""
    n = e = 0
    for i, v in enumerate(values):
        if abs(v - point) <= half:
            n += 1
            if y is not None and y[i]:
                e += 1
    return min(n, e, n - e) if binary else n


def curve(fit: K.Fit, prefix: str, family: str, column: "list[float]", y: "list[float] | None",
          binary: bool, terms: "Callable[[float], dict[str, float]]", reference: float,
          points: "list[float]", half: float, label: str) -> "list[Estimate]":
    """The fitted value at each grid point minus its value at ``reference`` (tagged 'curve')."""
    base = terms(reference)
    base_cell = near(column, y, reference, half, binary)
    out = []
    for point in points:
        at = terms(point)
        weights = {k: at.get(k, 0.0) - base.get(k, 0.0) for k in sorted(set(at) | set(base))}
        value, se = fit.contrast(weights)
        cell = min(base_cell, near(column, y, point, half, binary))
        name = str(int(point)) if point == int(point) else str(point)
        out += [Estimate(f"{prefix}:{label}_{name}", family, value, se, cell, ("curve",))]
    return out


def rate(key: str, family: str, flags: "list[float]", keep: "list[bool]",
         tags: "tuple[str, ...]" = ()) -> "list[Estimate]":
    """The share of 1 among the kept rows whose flag is present."""
    n = e = 0
    for f, k in zip(flags, keep):
        if k and f == f:
            n += 1
            if f:
                e += 1
    if n == 0:
        return []
    share = e / n
    return [Estimate(key, family, share, math.sqrt(max(share * (1 - share), 1e-12) / n),
                     min(n, e, n - e), tags)]


def rule(key: str, family: str, broken: "list[float]", tags: "tuple[str, ...]" = ()) -> "list[Estimate]":
    """The share of rows breaking a rule (1.0 broken, 0.0 kept, NaN not read), supported by the rows read.

    A rule the real table keeps on every row has no breaking row, and a
    rate's support -- its rarer side -- would leave that genuine zero
    unscored for ever (the date-against-status check was never scored,
    nor could the dose formula be). Its support is the rows it reads, so
    its half-split yardstick is 0 and a table is inside only where it
    breaks the rule on exactly the real table's share of rows. No
    standard error: a rule is a fact about the rows, not a test.
    """
    read_rows = [f for f in broken if f == f]
    if not read_rows:
        return []
    return [Estimate(key, family, sum(read_rows) / len(read_rows), None, len(read_rows), tags)]


def mean(key: str, family: str, values: "list[float]", keep: "list[bool]") -> "list[Estimate]":
    """The mean of the kept, present values."""
    kept = [v for v, k in zip(values, keep) if k and v == v]
    if len(kept) < 2:
        return []
    return [Estimate(key, family, statistics.fmean(kept),
                     statistics.stdev(kept) / math.sqrt(len(kept)), len(kept))]


def rho(key: str, family: str, a: "list[float]", b: "list[float]") -> "list[Estimate]":
    """Spearman's correlation over the rows where both are present."""
    pairs = [(x, y) for x, y in zip(a, b) if x == x and y == y]
    if len(pairs) < 10:
        return []
    value = K.spearman([x for x, _y in pairs], [y for _x, y in pairs])
    se = (1.0 - value * value) / math.sqrt(len(pairs) - 3)
    return [Estimate(key, family, value, max(se, 1e-9), len(pairs))]


def cramer(key: str, family: str, a: "list[str | None]", b: "list[str | None]") -> "list[Estimate]":
    """Cramer's V over the rows where both are present; its cell is the table's smallest."""
    both = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
    if not both:
        return []
    counts = K.contingency([x for x, _y in both], [y for _x, y in both])
    _stat, _df, smallest = K.chi_square(counts)
    return [Estimate(key, family, K.cramers_v(counts), None, smallest)]


def ageband(age: float) -> int:
    return 0 if age < 45 else 1 if age < 60 else 2 if age < 75 else 3 if age < 85 else 4


AGE_KNOTS = [27.0, 48.0, 62.0, 84.0]
AGE_GRID = [30.0, 40.0, 50.0, 70.0, 80.0, 90.0]


def age_terms(age: float) -> "dict[str, float]":
    s = K.rcs(age, AGE_KNOTS)
    return {"age10": age / 10.0, "s1": s[0] * 100.0, "s2": s[1] * 100.0}


def age_spline() -> "list[tuple[str, K.Term]]":
    return [("age10", scaled("age", 0.0, 10.0)), ("s1", spline("age", AGE_KNOTS, 0, 100.0)),
            ("s2", spline("age", AGE_KNOTS, 1, 100.0))]


# -- ST1: the patient cohort's targeted panel --------------------------------

ST1_NUMBERS = ["age", "glucose", "sbp", "lactate", "crp", "procedures", "cost", "fu_days"]
ST1_LABELS = ["urban", "language", "ward", "smoker", "diabetes", "ventilated", "died", "event", "readmit"]


def st1_rates(v: View) -> "list[Estimate]":
    """Death and ventilation rates by age band, urban living and lactate; the threshold bands; zero costs; wards."""
    age, died, vent, lact = v.num("age"), v.num("died"), v.num("ventilated"), v.num("lactate")
    urban = v.text("urban")
    band = [ageband(a) for a in age]
    out: "list[Estimate]" = []
    for b in range(5):
        for u in ("no", "yes"):
            out += rate(f"ST1/rate:died_{b}_{u}", "F1", died, [x == b and y == u for x, y in zip(band, urban)])
        for hi in (False, True):
            out += rate(f"ST1/rate:vent_{b}_lact{int(hi)}", "F1", vent,
                        [x == b and (y > 4) == hi for x, y in zip(band, lact)])
    glucose, diab = v.num("glucose"), v.num("diabetes")
    for low, high in ((0, 100), (100, 110), (110, 120), (120, 126), (126, 135), (135, 999)):
        out += rate(f"ST1/curve:diabetes_glucose_{low}", "F1", diab,
                    [g == g and low <= g < high for g in glucose], ("curve",))
    for low, high in ((0, 2), (2, 3), (3, 4), (4, 5), (5, 99)):
        out += rate(f"ST1/curve:vent_lactate_{low}", "F1", vent,
                    [low < x <= high for x in lact], ("curve",))
    out += rate("ST1/rate:cost_zero", "F1", [float(c == 0.0) if c == c else c for c in v.num("cost")],
                [True] * v.rows, ("margin",))
    readmit, ward = v.num("readmit"), v.text("ward")
    for w in T.WARDS:
        out += rate(f"ST1/rate:readmit_{w}", "F1", readmit, [x == w for x in ward])
    return out


def st1_pairs(v: View) -> "list[Estimate]":
    """Spearman's correlation of every pair of numbers; Cramer's V of every pair of labels."""
    out: "list[Estimate]" = []
    for i, a in enumerate(ST1_NUMBERS):
        for b in ST1_NUMBERS[i + 1:]:
            out += rho(f"ST1/rho:{a}~{b}", "F2", v.num(a), v.num(b))
    for i, a in enumerate(ST1_LABELS):
        for b in ST1_LABELS[i + 1:]:
            out += cramer(f"ST1/v:{a}~{b}", "F2", v.text(a), v.text(b))
    return out


def st1_linear(v: View) -> "list[Estimate]":
    """Blood pressure, naive and splined in age; cost by procedures, among the costed and naively."""
    cols, y = complete({"age": v.num("age"), "glucose": v.num("glucose"), "urban": v.eq("urban", "yes"),
                        "diab": v.num("diabetes")}, v.num("sbp"))
    d = K.Design(cols, [("int", K.intercept), ("age", col("age")), ("glucose", col("glucose")),
                        ("urban", col("urban")), ("diab", col("diab"))])
    out = coefs(K.ols(d, y), "ST1/ols_naive", "F3", supports(d, None, False), d.names)
    d2 = K.Design(cols, [("int", K.intercept)] + age_spline()
                  + [("glucose", col("glucose")), ("urban", col("urban"))])
    fit2 = K.ols(d2, y)
    out += coefs(fit2, "ST1/ols_spline", "F3", supports(d2, None, False), ["glucose", "urban"])
    out += curve(fit2, "ST1/curve", "F3", cols["age"], None, False, age_terms, 60.0, AGE_GRID,
                 5.0, "sbp_age")
    cost, procedures = v.num("cost"), v.num("procedures")
    c3, y3 = complete({"procedures": procedures}, [math.log(c) if c == c and c > 0 else math.nan for c in cost])
    d3 = K.Design(c3, [("int", K.intercept), ("procedures", col("procedures"))])
    out += [one(K.ols(d3, y3), "ST1/ols:logcost_procedures", "procedures", "F3", supports(d3, None, False))]
    c4, y4 = complete({"procedures": procedures}, cost)
    d4 = K.Design(c4, [("int", K.intercept), ("procedures", col("procedures"))])
    out += coefs(K.ols(d4, y4), "ST1/ols_naive_cost", "F3", supports(d4, None, False), d4.names)
    return out


def st1_logistic(v: View) -> "list[Estimate]":
    """Death: main effects; spline, ventilation x over-75 and diabetes x current smoker; the thresholds."""
    died = v.num("died")
    base = {"age": v.num("age"), "urban": v.eq("urban", "yes"), "vent": v.num("ventilated"),
            "lact4": v.above("lactate", 4.0), "diab": v.num("diabetes"),
            "cur": v.eq("smoker", "current"), "form": v.eq("smoker", "former")}
    cols, y = complete(dict(base, glucose=v.num("glucose")), died)
    d = K.Design(cols, [("int", K.intercept), ("age10", scaled("age", 0.0, 10.0)),
                        ("urban", col("urban")), ("vent", col("vent")), ("lact4", col("lact4")),
                        ("diab", col("diab")), ("cur", col("cur")), ("form", col("form")),
                        ("glucose10", scaled("glucose", 100.0, 10.0))])
    out = coefs(K.glm(d, y, "logistic"), "ST1/logistic_main", "F4", supports(d, y, True), d.names)
    cols2, y2 = complete(base, died)
    cols2["old"] = [float(a > 75) for a in cols2["age"]]
    d2 = K.Design(cols2, [("int", K.intercept)] + age_spline() + [
        ("vent", col("vent")), ("vent_old75", product(col("vent"), col("old"))),
        ("lact4", col("lact4")), ("urban", col("urban")), ("diab", col("diab")),
        ("cur", col("cur")), ("diab_cur", product(col("diab"), col("cur")))])
    fit2 = K.glm(d2, y2, "logistic")
    sup = supports(d2, y2, True)
    out += coefs(fit2, "ST1/logistic_ix", "F4", sup,
                 ["vent", "vent_old75", "lact4", "urban", "diab", "cur", "diab_cur"])
    out += curve(fit2, "ST1/curve", "F4", cols2["age"], y2, True, age_terms, 60.0, AGE_GRID,
                 5.0, "died_age")
    value, se = fit2.contrast({"vent": 1.0, "vent_old75": 1.0})
    out += [Estimate("ST1/curve:vent_over_75", "F4", value, se, sup["vent_old75"], ("curve",))]
    c3, y3 = complete({"glucose126": v.above("glucose", 125.5), "age": v.num("age")}, v.num("diabetes"))
    d3 = K.Design(c3, [("int", K.intercept), ("glucose126", col("glucose126")),
                       ("age10", scaled("age", 0.0, 10.0))])
    out += [one(K.glm(d3, y3, "logistic"), "ST1/logistic:diabetes_glucose126", "glucose126", "F4",
                supports(d3, y3, True))]
    c4, y4 = complete({"lact4": v.above("lactate", 4.0), "lactate": v.num("lactate"),
                       "age": v.num("age")}, v.num("ventilated"))
    d4 = K.Design(c4, [("int", K.intercept), ("lact4", col("lact4")), ("age10", scaled("age", 0.0, 10.0))])
    out += [one(K.glm(d4, y4, "logistic"), "ST1/logistic:vent_lact4", "lact4", "F4", supports(d4, y4, True))]
    d5 = K.Design(c4, [("int", K.intercept), ("lactate", col("lactate")), ("age10", scaled("age", 0.0, 10.0))])
    out += coefs(K.glm(d5, y4, "logistic"), "ST1/logistic_naive_vent", "F4", supports(d5, y4, True),
                 ["lactate", "age10"])
    return out


def st1_rare_band(v: View) -> "list[Estimate]":
    """Readmission (2 %): diabetes x the upper wards, the truth the floor of 11 may hide."""
    high = [float(w is not None and w >= "w06") for w in v.text("ward")]
    cols, y = complete({"diab": v.num("diabetes"), "high": high}, v.num("readmit"))
    d = K.Design(cols, [("int", K.intercept), ("diab", col("diab")), ("high", col("high")),
                        ("diab_high", product(col("diab"), col("high")))])
    return [one(K.glm(d, y, "logistic"), "ST1/logistic:readmit_diab_highward", "diab_high", "F4",
                supports(d, y, True))]


def st1_rare_wards(v: View) -> "list[Estimate]":
    """Readmission by every ward: the rare outcome's unsupported family."""
    ward = v.text("ward")
    columns: "dict[str, object]" = {"diab": v.num("diabetes")}
    for w in T.WARDS[1:]:
        columns["lvl_" + w] = [math.nan if x is None else float(x == w) for x in ward]
    cols, y = complete(columns, v.num("readmit"))
    d = K.Design(cols, [("int", K.intercept), ("diab", col("diab"))]
                 + [("lvl_" + w, col("lvl_" + w)) for w in T.WARDS[1:]])
    levels_present(d)
    return coefs(K.glm(d, y, "logistic"), "ST1/rare", "F4", supports(d, y, True), d.names)


def st1_counts(v: View) -> "list[Estimate]":
    """Procedures, Poisson, and their overdispersion."""
    cols, y = complete({"vent": v.num("ventilated"), "age": v.num("age"), "diab": v.num("diabetes")},
                       v.num("procedures"))
    d = K.Design(cols, [("int", K.intercept), ("vent", col("vent")),
                        ("age10", scaled("age", 60.0, 10.0)), ("diab", col("diab"))])
    fit = K.glm(d, y, "poisson")
    out = coefs(fit, "ST1/pois", "F5", supports(d, None, False), d.names)
    return out + [Estimate("ST1/poisson:procedures_dispersion", "F5", fit.extra["dispersion"], None, d.rows)]


def st1_survival(v: View) -> "list[Estimate]":
    """Cox on (fu_days, event); Kaplan-Meier medians and censored shares by ventilation."""
    cols, _y = complete({"age": v.num("age"), "vent": v.num("ventilated"), "diab": v.num("diabetes"),
                         "urban": v.eq("urban", "yes"), "t": v.num("fu_days"), "e": v.num("event")})
    if any(t < 0 for t in cols["t"]):
        raise AnalysisError("negative time", "a follow-up time is below zero")
    d = K.Design({k: cols[k] for k in ("age", "vent", "diab", "urban")},
                 [("age10", scaled("age", 60.0, 10.0)), ("vent", col("vent")),
                  ("diab", col("diab")), ("urban", col("urban"))])
    out = coefs(K.cox(d, cols["t"], [int(e) for e in cols["e"]]), "ST1/cox", "F6",
                supports(d, cols["e"], True), d.names, ("time",))
    for g in (0.0, 1.0):
        keep = [x == g for x in cols["vent"]]
        times = [t for t, k in zip(cols["t"], keep) if k]
        events = [int(e) for e, k in zip(cols["e"], keep) if k]
        median = K.km_median(times, events)
        if median is not None:
            out += [Estimate(f"ST1/km:median_vent{int(g)}", "F6", median, None,
                             min(sum(events), len(events) - sum(events)), ("time",))]
        out += rate(f"ST1/censored:vent{int(g)}", "F6", [1.0 - e for e in cols["e"]], keep, ("time",))
    return out


def st1_missing(v: View) -> "list[Estimate]":
    """Who is missing glucose and CRP: the two models, who is missing by group, the patterns, complete cases."""
    cols, _y = complete({"old": v.above("age", 80.0), "vent": v.num("ventilated")})
    out: "list[Estimate]" = []
    for column in ("glucose", "crp"):
        miss = v.missing(column)
        d = K.Design(cols, [("int", K.intercept), ("old80", col("old")), ("vent", col("vent"))])
        fit, sup = K.glm(d, miss, "logistic"), supports(d, miss, True)
        out += [one(fit, f"ST1/miss:{column}_old80", "old80", "F9", sup, ("missing",)),
                one(fit, f"ST1/miss:{column}_vent", "vent", "F9", sup, ("missing",))]
    glucose_miss, crp_miss = v.missing("glucose"), v.missing("crp")
    band = [ageband(a) for a in v.num("age")]
    for b in range(5):
        out += rate(f"ST1/miss:glucose_by_age{b}", "F9", glucose_miss, [x == b for x in band], ("missing",))
    for g in (0.0, 1.0):
        out += rate(f"ST1/miss:crp_by_vent{int(g)}", "F9", crp_miss, [x == g for x in v.num("ventilated")],
                    ("missing",))
    # The pattern shares are mostly each column's own missing share,
    # which a shuffle keeps: they stay in F9 for K-BC-01 and are left out
    # of K-BC-08's joint measure. The complete-case share IS one column's
    # (glucose alone goes missing among the model's columns): a margin.
    for a in (0.0, 1.0):
        for b in (0.0, 1.0):
            out += rate(f"ST1/pattern:glucose{int(a)}_crp{int(b)}", "F9",
                        [float(x == a and y == b) for x, y in zip(glucose_miss, crp_miss)], [True] * v.rows)
    out += rate("ST1/complete:logistic_main", "F9", [1.0 - m for m in glucose_miss], [True] * v.rows,
                ("margin",))
    return out


def plan_st1(real: View) -> "list[Analysis]":
    """ST1's targeted panel."""
    return [Analysis("ST1 rates", st1_rates), Analysis("ST1 pairs", st1_pairs),
            Analysis("ST1 linear", st1_linear), Analysis("ST1 logistic", st1_logistic),
            Analysis("ST1 rare by ward band", st1_rare_band),
            Analysis("ST1 rare by ward", st1_rare_wards), Analysis("ST1 counts", st1_counts),
            Analysis("ST1 survival", st1_survival), Analysis("ST1 missing cells", st1_missing)]


# -- ST2: several rows per subject -----------------------------------------


def st2_mixed(v: View) -> "list[Estimate]":
    """marker ~ visit * arm + age + (1 | sid): the fixed effects and the ICC.

    The subjects of two rows or more carry the ICC, so they are its
    support and the fixed effects', and fewer than `SUPPORT` of them stop
    the model ('singular', K-BC-10): a twin whose subject numbers collide
    a few times among unique ones (one collision at 5,000 rows, as a
    random 7-figure number gives) would otherwise read an arbitrary ICC
    over a support of thousands.
    """
    sid = v.text("sid")
    keep = [s is not None for s in sid]
    cols, y = complete({"visit": v.num("visit"), "arm": v.num("arm"), "age": v.num("age"),
                        "g": [float(i) for i in range(v.rows)]}, v.num("marker"), keep)
    groups = [sid[int(i)] for i in cols.pop("g")]
    d = K.Design(cols, [("int", K.intercept), ("visit", col("visit")), ("arm", col("arm")),
                        ("arm_visit", product(col("arm"), col("visit"))),
                        ("age10", scaled("age", 55.0, 10.0))])
    fit, icc = K.random_intercept(d, y, groups, min_repeated=SUPPORT)
    subjects = int(fit.extra["repeated"])
    out = coefs(fit, "ST2/mixed", "F7", {n: subjects for n in d.names}, d.names, ("subject",))
    return out + [Estimate("ST2/mixed:icc", "F7", icc, None, subjects, ("subject",))]


def st2_subjects(v: View) -> "list[Estimate]":
    """Rows per subject; the correlation of a subject's consecutive visits; means by arm and visit."""
    sid, visit, y = v.text("sid"), v.num("visit"), v.num("marker")
    counts: "dict[str | None, int]" = {}
    for s in sid:
        counts[s] = counts.get(s, 0) + 1
    out: "list[Estimate]" = []
    total = len(counts)
    for k in range(1, 9):
        hit = sum(1 for c in counts.values() if c == k)
        share = hit / total
        out += [Estimate(f"ST2/rows:{k}", "F7", share, math.sqrt(max(share * (1 - share), 1e-12) / total),
                         min(hit, total - hit), ("subject", "margin"))]
    by: "dict[tuple[str | None, float], float]" = {}
    for s, x, h in zip(sid, visit, y):
        by[(s, x)] = h
    first: "list[float]" = []
    second: "list[float]" = []
    for (s, x), h in by.items():
        nxt = by.get((s, x + 1.0))
        if nxt is not None and h == h and nxt == nxt:
            first += [h]
            second += [nxt]
    if len(first) > 3:
        r = K.pearson(first, second)
        out += [Estimate("ST2/serial:next_visit", "F7", r, (1 - r * r) / math.sqrt(len(first) - 3),
                         len(first), ("subject",))]
    arm = v.num("arm")
    for a in (0.0, 1.0):
        for x in range(8):
            out += mean(f"ST2/mean:arm{int(a)}_visit{x}", "F1", y,
                        [p == a and q == x for p, q in zip(arm, visit)])
    for a, b in (("age", "marker"), ("visit", "marker"), ("age", "visit")):
        out += rho(f"ST2/rho:{a}~{b}", "F2", v.num(a), v.num(b))
    return out


def st2_dropout(v: View) -> "list[Estimate]":
    """Leaving after a visit, by that visit's value (the dependent dropout)."""
    sid, visit, y = v.text("sid"), v.num("visit"), v.num("marker")
    present = set(zip(sid, visit))
    previous: "list[float]" = []
    dropped: "list[float]" = []
    for s, x, h in zip(sid, visit, y):
        if x < 7 and h == h:
            previous += [h]
            dropped += [0.0 if (s, x + 1.0) in present else 1.0]
    cols, ys = complete({"prev": previous}, dropped)
    d = K.Design(cols, [("int", K.intercept), ("prev", scaled("prev", 7.5, 1.0))])
    return [one(K.glm(d, ys, "logistic"), "ST2/logistic:dropout_previous", "prev", "F9",
                supports(d, ys, True), ("missing",))]


def st2_wide(v: View) -> "list[Estimate]":
    """The analyst's wide table, one row per subject and one column per visit (`pivot`)."""
    try:
        v.frame.pivot(index="sid", columns="visit", values="marker")  # type: ignore[attr-defined]
    except ValueError as error:
        raise AnalysisError("error", "pivot: " + str(error)[:60]) from error
    return []


def st2_subject_table(v: View) -> "list[Estimate]":
    """The analyst's subject table, one arm and one age per subject, merged back many-to-one."""
    subjects = v.frame[["sid", "arm", "age"]].drop_duplicates()  # type: ignore[index]
    try:
        v.frame[["sid", "visit", "marker"]].merge(subjects, on="sid", validate="many_to_one")  # type: ignore[index]
    except ValueError as error:
        raise AnalysisError("error", "subject table: " + str(error)[:60]) from error
    return []


def plan_st2(real: View) -> "list[Analysis]":
    """ST2's targeted panel."""
    return [Analysis("ST2 mixed model", st2_mixed), Analysis("ST2 subjects", st2_subjects),
            Analysis("ST2 dropout", st2_dropout), Analysis("ST2 wide table", st2_wide),
            Analysis("ST2 subject table", st2_subject_table)]


# -- ST3: the registry with dates -------------------------------------------


def st3_times(v: View) -> "tuple[list[float], list[float], list[float]]":
    """Follow-up days, the event flag and the competing flag, as an analyst derives them."""
    days, which = v.days("entry_date", ["event_date", "censor_date"])
    status = v.text("status")
    event = [math.nan if w < 0 else float(s == "event") for s, w in zip(status, which)]
    competing = [math.nan if w < 0 else float(s == "competing") for s, w in zip(status, which)]
    if any(d == d and d < 0 for d in days):
        raise AnalysisError("negative time", "an end date falls before its entry date")
    return days, event, competing


def st3_survival(v: View) -> "list[Estimate]":
    """Cause-specific Cox for the event and the competing event; the stage effect early and late; medians."""
    days, event, competing = st3_times(v)
    cols, _y = complete({"stage": v.num("stage"), "age": v.num("age"), "urban": v.eq("urban", "yes"),
                         "t": days, "e": event, "c": competing})
    terms = [("stage", col("stage")), ("age10", scaled("age", 65.0, 10.0)), ("urban", col("urban"))]
    d = K.Design({k: cols[k] for k in ("stage", "age", "urban")}, terms)
    out = coefs(K.cox(d, cols["t"], [int(e) for e in cols["e"]]), "ST3/cox", "F6",
                supports(d, cols["e"], True), d.names, ("time",))
    out += coefs(K.cox(d, cols["t"], [int(c) for c in cols["c"]]), "ST3/cox_competing", "F6",
                 supports(d, cols["c"], True), ["age10", "stage"], ("time",))
    early_e = [int(e and t <= 365.0) for e, t in zip(cols["e"], cols["t"])]
    fe = K.cox(d, [min(t, 365.0) for t in cols["t"]], early_e)
    keep = [i for i, t in enumerate(cols["t"]) if t > 365.0]
    late = K.Design({k: [cols[k][i] for i in keep] for k in ("stage", "age", "urban")}, terms)
    fl = K.cox(late, [cols["t"][i] for i in keep], [int(cols["e"][i]) for i in keep])
    (be, se_e), (bl, se_l) = fe.coef("stage"), fl.coef("stage")
    cell = min(sum(early_e), sum(int(cols["e"][i]) for i in keep))
    out += [Estimate("ST3/cox:stage_early", "F6", be, se_e, cell, ("time",)),
            Estimate("ST3/cox:stage_late", "F6", bl, se_l, cell, ("time",)),
            Estimate("ST3/cox:stage_early_minus_late", "F6", be - bl,
                     math.sqrt(se_e ** 2 + se_l ** 2), cell, ("time",))]
    for g in (1.0, 2.0, 3.0, 4.0):
        sel = [s == g for s in cols["stage"]]
        events = [int(e) for e, k in zip(cols["e"], sel) if k]
        median = K.km_median([t for t, k in zip(cols["t"], sel) if k], events)
        if median is not None:
            out += [Estimate(f"ST3/km:median_stage{int(g)}", "F6", median, None,
                             min(sum(events), len(events) - sum(events)), ("time",))]
    return out


def st3_censoring(v: View) -> "list[Estimate]":
    """Censored shares by centre, the low centres' model, end shares by stage, the date pattern."""
    days, event, competing = st3_times(v)
    centre = v.text("centre")
    censored = [math.nan if e != e else float(not e and not c) for e, c in zip(event, competing)]
    out: "list[Estimate]" = []
    for k in range(1, 21):
        name = "C%02d" % k
        out += rate(f"ST3/censored:{name}", "F6", censored, [x == name for x in centre], ("time",))
    low = [float(x in ("C01", "C02", "C03", "C04")) for x in centre]
    cols, y = complete({"low": low, "t": days}, censored)
    d = K.Design(cols, [("int", K.intercept), ("low", col("low")), ("years", scaled("t", 0.0, 365.0))])
    out += [one(K.glm(d, y, "logistic"), "ST3/logistic:censored_low_centres", "low", "F6",
                supports(d, y, True), ("time",))]
    stage, status = v.num("stage"), v.text("status")
    for g in (1.0, 2.0, 3.0, 4.0):
        keep = [s == g for s in stage]
        out += rate(f"ST3/rate:event_stage{int(g)}", "F1", [float(x == "event") for x in status], keep)
        out += rate(f"ST3/rate:competing_stage{int(g)}", "F1", [float(x == "competing") for x in status], keep)
    out += rule("ST3/pattern:event_date_vs_status", "F9",
                [float((m == 1.0) != (s == "censored")) for m, s in zip(v.missing("event_date"), status)],
                ("missing",))
    return out


def plan_st3(real: View) -> "list[Analysis]":
    """ST3's targeted panel."""
    return [Analysis("ST3 survival", st3_survival), Analysis("ST3 censoring", st3_censoring)]


# -- ST4: claims -------------------------------------------------------------


def chapters(v: View) -> "list[str | None]":
    """A code's chapter, its first letter, as an analyst derives it."""
    return [None if c is None else c[:1] for c in v.text("code")]


def st4_chapters(v: View) -> "list[Estimate]":
    """Visits by chapter and payer (Poisson); the rare outcome by the three hot chapters."""
    chapter = chapters(v)
    columns: "dict[str, object]" = {"private": v.eq("payer", "private")}
    for ch in T.CHAPTERS[1:]:
        columns["lvl_" + ch] = [math.nan if c is None else float(c == ch) for c in chapter]
    cols, y = complete(columns, v.num("visits"))
    d = K.Design(cols, [("int", K.intercept), ("private", col("private"))]
                 + [("lvl_" + ch, col("lvl_" + ch)) for ch in T.CHAPTERS[1:]])
    levels_present(d)
    fit = K.glm(d, y, "poisson")
    sup = supports(d, None, False)
    out = coefs(fit, "ST4/pois", "F5", sup, d.names)
    out += [one(fit, "ST4/poisson:visits_chD", "lvl_D", "F5", sup),
            one(fit, "ST4/poisson:visits_private", "private", "F5", sup)]
    hot = {"chB": "B", "chD": "D", "chG": "G"}
    columns2: "dict[str, object]" = {k: [math.nan if c is None else float(c == ch) for c in chapter]
                                     for k, ch in hot.items()}
    columns2["weight"] = v.num("weight")
    cols2, y2 = complete(columns2, v.num("outcome"))
    d2 = K.Design(cols2, [("int", K.intercept)] + [(k, col(k)) for k in hot]
                  + [("weight10", scaled("weight", 80.0, 10.0))])
    fit2 = K.glm(d2, y2, "logistic")
    sup2 = supports(d2, y2, True)
    out += coefs(fit2, "ST4/logistic_outcome", "F4", sup2, d2.names)
    return out + [one(fit2, "ST4/logistic:outcome_chB", "chB", "F4", sup2)]


def st4_parity(v: View) -> "list[Estimate]":
    """Readmission on three flags: the pairs model (all near 0) and the full model (the parity term)."""
    cols, y = complete({"a": v.num("cond_a"), "b": v.num("cond_b"), "c": v.num("cond_c")}, v.num("readmit"))
    a, b, c = col("a"), col("b"), col("c")
    pairs = [("int", K.intercept), ("a", a), ("b", b), ("c", c),
             ("ab", product(a, b)), ("ac", product(a, c)), ("bc", product(b, c))]
    d = K.Design(cols, pairs)
    out = coefs(K.glm(d, y, "logistic"), "ST4/logistic_pairs:readmit", "F4", supports(d, y, True),
                ["a", "b", "c", "ab", "ac", "bc"])
    out = [dataclasses.replace(e, key=e.key.replace("readmit:", "readmit_")) for e in out]
    d2 = K.Design(cols, pairs + [("abc", product(a, b, c))])
    return out + [one(K.glm(d2, y, "logistic"), "ST4/logistic:readmit_abc", "abc", "F4", supports(d2, y, True))]


def st4_linear(v: View) -> "list[Estimate]":
    """The dose formula and the dose on weight and dose rate; amounts; zero amounts; visits by payer; rates; pairs.

    The formula is read as itself: the share of rows whose dose is not
    weight times dose rate to the tenth (`round(weight * rate, 1)`, within
    0.051 for the written decimals). A regression cannot stand in for it:
    a dose of 2 x fitted - dose keeps the weight's coefficient, its
    standard error and R^2 to the last digit while breaking the formula
    on 2,989 of 3,000 rows (Codex's review).
    """
    weight, dose_rate, dose = v.num("weight"), v.num("dose_rate"), v.num("dose")
    out = rule("ST4/rule:dose_formula", "F3",
               [math.nan if w != w or q != q or x != x else float(abs(x - round(w * q, 1)) > 0.051)
                for w, q, x in zip(weight, dose_rate, dose)])
    cols, y = complete({"weight": weight, "rate": dose_rate}, dose)
    d = K.Design(cols, [("int", K.intercept), ("weight", col("weight")), ("rate", col("rate"))])
    fit = K.ols(d, y)
    sup = supports(d, None, False)
    out += [one(fit, "ST4/ols:dose_weight", "weight", "F3", sup),
            one(fit, "ST4/ols:dose_rate", "rate", "F3", sup),
            Estimate("ST4/ols:dose_r2", "F3", fit.extra["r2"], None, d.rows)]
    amount, visits = v.num("amount"), v.num("visits")
    cols2, y2 = complete({"lv": [math.log1p(x) if x == x else x for x in visits],
                          "private": v.eq("payer", "private")},
                         [math.log1p(x) if x == x else x for x in amount])
    d2 = K.Design(cols2, [("int", K.intercept), ("lv", col("lv")), ("private", col("private"))])
    out += coefs(K.ols(d2, y2), "ST4/ols_amount", "F3", supports(d2, None, False), d2.names)
    out += rate("ST4/rate:amount_zero", "F1", [float(x == 0.0) if x == x else x for x in amount],
                [True] * v.rows, ("margin",))
    payer = v.text("payer")
    for p in T.PAYERS:
        out += mean(f"ST4/mean:visits_{p}", "F1", visits, [x == p for x in payer])
    chapter, outcome = chapters(v), v.num("outcome")
    for ch in T.CHAPTERS:
        out += rate(f"ST4/rate:outcome_{ch}", "F1", outcome, [c == ch for c in chapter])
    numbers = ["visits", "amount", "weight", "dose_rate", "dose"]
    for i, x in enumerate(numbers):
        for z in numbers[i + 1:]:
            out += rho(f"ST4/rho:{x}~{z}", "F2", v.num(x), v.num(z))
    return out


def plan_st4(real: View) -> "list[Analysis]":
    """ST4's targeted panel."""
    return [Analysis("ST4 chapters", st4_chapters), Analysis("ST4 parity", st4_parity),
            Analysis("ST4 linear and rates", st4_linear)]


# -- ST5: the null table ----------------------------------------------------

ST5_LABELS = {"urban", "language", "ward", "smoker"}


# A number of more different values than this is tested against a label
# by its ranks, not by a table of its values.
FEW_VALUES = 30


def st5_pair_p(v: View, a: str, b: str) -> float:
    """The p-value an analyst's test of association gives one column pair.

    Two labels, or a label and a number of at most `FEW_VALUES` different
    values: Pearson's chi-square of their table. A label and a number of
    more: Kruskal-Wallis on the number's ranks by the label's levels -- a
    table of a many-valued number's values has thousands of degrees of
    freedom (language by cost: 69,295) and sees a shifted level about as
    often as its false alarms (measured: a 25 % cost shift in one language
    found on 5 of 20 seeds by the table, 20 of 20 by the ranks). Two
    numbers: Spearman's correlation through Fisher's z.
    """
    ta, tb = v.text(a), v.text(b)
    keep = [x is not None and y is not None for x, y in zip(ta, tb)]
    if a in ST5_LABELS or b in ST5_LABELS:
        label, number = (a, b) if a in ST5_LABELS else (b, a)
        labels = [x for x, k in zip(v.text(label), keep) if k]
        if number not in ST5_LABELS:
            values = [x for x, k in zip(v.num(number), keep) if k]
            if len(set(values)) > FEW_VALUES:
                h, df = K.kruskal_wallis(values, labels)
                return K.chi2_sf(h, df) if df > 0 else 1.0
        counts = K.contingency([x for x, k in zip(ta, keep) if k], [y for y, k in zip(tb, keep) if k])
        stat, df, _small = K.chi_square(counts)
        return K.chi2_sf(stat, df) if df > 0 else 1.0
    xa = [x for x, k in zip(v.num(a), keep) if k]
    xb = [y for y, k in zip(v.num(b), keep) if k]
    r = max(-0.999999, min(0.999999, K.spearman(xa, xb)))
    return 2.0 * (1.0 - statistics.NormalDist().cdf(abs(math.atanh(r)) * math.sqrt(len(xa) - 3)))


def st5_null(v: View) -> "list[Estimate]":
    """The share of the 105 column pairs a 5 % test calls associated: about 5 % on a null table."""
    names = T.ST5_COLUMNS
    significant = tests = 0
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            tests += 1
            significant += 1 if st5_pair_p(v, a, b) < 0.05 else 0
    return [Estimate("ST5/null:significant_share", "F2", significant / tests, None, v.rows, ("null",))]


def plan_st5(real: View) -> "list[Analysis]":
    """ST5's panel: the one count of associations found."""
    return [Analysis("ST5 every pair", st5_null)]


# -- ST6: curves that turn ---------------------------------------------------


def plan_st6(real: View) -> "list[Analysis]":
    """ST6's targeted panel: death splined in glucose and creatinine on a fixed grid, and naively.

    The splined model holds every other term of the generator's death
    risk (the age spline, ventilation and its over-75 interaction,
    lactate, urban living, diabetes x current smoker), so the two curves
    are not asked to carry what those terms carry.
    """
    glucose_knots = knots_of([g for g in real.num("glucose") if g == g])
    cr_knots = knots_of([c for c in real.num("creatinine") if c == c])

    def glucose_terms(g: float) -> "dict[str, float]":
        s = K.rcs(g, glucose_knots)
        return {"glucose": g / 10.0, "g1": s[0] / 10.0, "g2": s[1] / 10.0}

    def cr_terms(c: float) -> "dict[str, float]":
        s = K.rcs(c, cr_knots)
        return {"cr": c, "c1": s[0], "c2": s[1]}

    def run(v: View) -> "list[Estimate]":
        cols, y = complete({"glucose": v.num("glucose"), "cr": v.num("creatinine"), "age": v.num("age"),
                            "vent": v.num("ventilated"), "urban": v.eq("urban", "yes"),
                            "lact4": v.above("lactate", 4.0), "diab": v.num("diabetes"),
                            "cur": v.eq("smoker", "current")}, v.num("died"))
        cols["old"] = [float(a > 75) for a in cols["age"]]
        others = age_spline() + [
            ("vent", col("vent")), ("vent_old75", product(col("vent"), col("old"))),
            ("lact4", col("lact4")), ("urban", col("urban")), ("diab", col("diab")),
            ("cur", col("cur")), ("diab_cur", product(col("diab"), col("cur")))]
        d = K.Design(cols, [("int", K.intercept), ("glucose", scaled("glucose", 0.0, 10.0)),
                            ("g1", spline("glucose", glucose_knots, 0, 0.1)),
                            ("g2", spline("glucose", glucose_knots, 1, 0.1)),
                            ("cr", col("cr")), ("c1", spline("cr", cr_knots, 0)),
                            ("c2", spline("cr", cr_knots, 1))] + others)
        fit = K.glm(d, y, "logistic")
        out = curve(fit, "ST6/curve", "F4", cols["glucose"], y, True, glucose_terms, 100.0,
                    [70.0, 85.0, 115.0, 130.0, 145.0], 5.0, "died_glucose")
        out += curve(fit, "ST6/curve", "F4", cols["cr"], y, True, cr_terms, 1.0,
                     [0.6, 0.8, 1.4, 1.7, 2.0], 0.1, "died_creat")
        d2 = K.Design(cols, [("int", K.intercept), ("glucose", scaled("glucose", 0.0, 10.0)),
                             ("cr", col("cr")), ("age10", scaled("age", 60.0, 10.0)),
                             ("vent", col("vent")), ("urban", col("urban"))])
        return out + coefs(K.glm(d2, y, "logistic"), "ST6/logistic_naive", "F4", supports(d2, y, True),
                           ["glucose", "cr", "age10", "vent", "urban"])

    return [Analysis("ST6 curves", run)]


TARGETED = {"ST1": plan_st1, "ST2": plan_st2, "ST3": plan_st3, "ST4": plan_st4,
           "ST5": plan_st5, "ST6": plan_st6}


# -- the automatic panel, from the schema alone -----------------------------


def knots_of(values: "list[float]") -> "list[float]":
    """Four knots at the 5, 35, 65 and 95 % quantiles."""
    ordered = sorted(values)
    knots = [K.quantile(ordered, q) for q in (0.05, 0.35, 0.65, 0.95)]
    if len(set(knots)) < 4:
        raise AnalysisError("error", "too few different values for a spline")
    return knots


@dataclasses.dataclass
class Column:
    """One column as the schema reads it: kind, levels, knots, missing share, the value read as 1, its range."""

    name: str
    kind: str
    levels: "list[str]"
    knots: "list[float] | None"
    missing: float
    one: str = ""
    center: float = 0.0
    scale: float = 1.0
    low: float = -math.inf
    high: float = math.inf


def clamped(c: Column, value: float) -> float:
    """A number held to the real table's range, NaN kept: an automatic model never extrapolates.

    A heavy-tailed number drawn afresh can land far past the real table's
    largest (measured: a fresh ST1 at 20,000 rows put cost at 50,015
    standard deviations), where a number and its two straight-armed
    spline terms are proportional and the model's cross products
    singular. Every automatic term reads its number clamped to the range
    the real table showed, as a model fitted there would be applied.
    """
    return clamped_chunk(c, [value])[0]


def clamped_chunk(c: Column, values: "list[float]") -> "list[float]":
    """`clamped` over a chunk of values in one comprehension (NaN fails both comparisons and is kept).

    A call a value made 29 million calls in one fast part (counted
    under a profiler).
    """
    low, high = c.low, c.high
    return [low if v < low else high if v > high else v for v in values]


def standardized(c: Column) -> "K.Term":
    """(the clamped number - the real table's mean) / its spread."""
    return lambda ch: [(v - c.center) / c.scale for v in clamped_chunk(c, ch[c.name])]


def schema(real: View) -> "list[Column]":
    """Each column's kind, read from the real table alone.

    Text that `pandas.to_datetime` reads at the ISO format is a DATE;
    other text with two values is BINARY (the second in sorted order
    reads as 1), up to thirty a LABEL, more a KEY (an identifier or a
    code: never a predictor). A label's levels are those of at least 22
    rows, by count; the first is the reference and rarer levels join it.
    Numbers whose two values are 0 and 1 are BINARY; whole numbers at or
    above 0 with a median of 20 or less a COUNT; the rest NUMBERS. A
    count or number enters a model standardized by the real table's mean
    and spread, splined at its 5, 35, 65 and 95 % quantiles where it
    holds fifty different values and four different knots.
    """
    import pandas

    out = []
    for name in real.frame.columns:  # type: ignore[attr-defined]
        series = real.frame[name]  # type: ignore[index]
        missing = float(series.isna().mean())
        if not pandas.api.types.is_numeric_dtype(series):
            values = [x for x in real.text(name) if x is not None]
            counts: "dict[str, int]" = {}
            for x in values:
                counts[x] = counts.get(x, 0) + 1
            try:
                pandas.to_datetime(series.dropna(), format="%Y-%m-%d")
                out += [Column(name, "date", [], None, missing)]
                continue
            except (ValueError, TypeError):
                pass
            distinct = sorted(counts)
            if len(distinct) == 2:
                out += [Column(name, "binary", distinct, None, missing, distinct[1])]
            elif len(distinct) <= 30:
                ranked = sorted(distinct, key=lambda d: (-counts[d], d))
                levels = [ranked[0]] + [d for d in ranked[1:] if counts[d] >= SUPPORT]
                out += [Column(name, "label", levels, None, missing)]
            else:
                out += [Column(name, "key", [], None, missing)]
            continue
        numbers = [x for x in real.num(name) if x == x]
        distinct_numbers = set(numbers)
        if distinct_numbers == {0.0, 1.0}:
            out += [Column(name, "binary", ["0", "1"], None, missing, "1")]
            continue
        whole = all(x == int(x) for x in numbers)
        kind = "count" if whole and min(numbers) >= 0 and statistics.median(numbers) <= 20 else "number"
        knots = None
        if len(distinct_numbers) >= 50:
            try:
                knots = knots_of(numbers)
            except AnalysisError:
                knots = None
        center = statistics.fmean(numbers)
        out += [Column(name, kind, [], knots, missing, "", center, statistics.pstdev(numbers) or 1.0,
                       min(numbers), max(numbers))]
    return out


def column_values(v: View, c: Column) -> "dict[str, object]":
    """The design columns a schema column gives: itself, its 0/1 reading, or one per label level."""
    if c.kind == "binary":
        return {c.name: v.num(c.name) if c.levels == ["0", "1"] else v.eq(c.name, c.one)}
    if c.kind == "label":
        text = v.text(c.name)
        return {f"lvl_{c.name}={lv}": [math.nan if x is None else float(x == lv) for x in text]
                for lv in c.levels[1:]}
    return {c.name: v.num(c.name)}


def outcome_values(v: View, c: Column) -> "object":
    """A column as an outcome: its 0/1 reading where it is binary, else its numbers."""
    return next(iter(column_values(v, c).values())) if c.kind == "binary" else v.num(c.name)


def column_terms(c: Column, room: int) -> "list[tuple[str, K.Term]]":
    """A predictor's terms: a binary's flag, a label's levels, a number and its two spline terms."""
    if c.kind == "binary":
        return [(c.name, col(c.name))]
    if c.kind == "label":
        return [(f"lvl_{c.name}={lv}", col(f"lvl_{c.name}={lv}")) for lv in c.levels[1:]][:room]
    terms: "list[tuple[str, K.Term]]" = [(c.name, standardized(c))]
    if c.knots is not None and room >= 3:
        for j in (0, 1):
            term = K.rcs_term(standard_knots(c), j)
            terms += [(f"{c.name}_s{j + 1}", lambda ch, c=c, f=term:
                       [f((v - c.center) / c.scale) for v in clamped_chunk(c, ch[c.name])])]
    return terms


def standard_knots(c: Column) -> "list[float]":
    """A number's knots on its standardized scale."""
    return [(k - c.center) / c.scale for k in (c.knots or [])]


def strength(v: View, c: Column, y: "object") -> float:
    """How strongly a predictor goes with an outcome on the real table: |Spearman|, or eta for a label."""
    if c.kind == "label":
        groups: "dict[str, list[float]]" = {}
        for x, yi in zip(v.text(c.name), y):  # type: ignore[call-overload]
            if x is not None and yi == yi:
                if x not in groups:
                    groups[x] = []
                groups[x] += [yi]
        values = [yi for vals in groups.values() for yi in vals]
        if len(values) < 3:
            return 0.0
        grand = statistics.fmean(values)
        total = sum((yi - grand) ** 2 for yi in values)
        between = sum(len(vals) * (statistics.fmean(vals) - grand) ** 2 for vals in groups.values())
        return math.sqrt(between / total) if total > 0 else 0.0
    x = next(iter(column_values(v, c).values()))
    pairs = [(a, b) for a, b in zip(x, y) if a == a and b == b]  # type: ignore[call-overload]
    if len(pairs) < 10:
        return 0.0
    return abs(K.spearman([a for a, _b in pairs], [b for _a, b in pairs]))


def time_event(columns: "list[Column]") -> "tuple[str, list[str], str] | None":
    """A time and event pair the schema shows: entry and end dates, or a duration and an event flag by name."""
    dates = [c for c in columns if c.kind == "date"]
    starts = [c for c in dates if c.missing == 0.0]
    ends = [c for c in dates if c.missing > 0.0]
    if len(starts) == 1 and ends:
        return (starts[0].name, [c.name for c in ends], "date")
    durations = [c.name for c in columns if c.kind in ("count", "number")
                 and ("day" in c.name or "time" in c.name or c.name.startswith("fu"))]
    flags = [c.name for c in columns if c.kind == "binary" and ("event" in c.name or "status" in c.name)]
    if durations and flags:
        return (durations[0], [flags[0]], "flag")
    return None


def indicator_supported(real: View, sources: "list[Column]", term: "K.Term", y: object) -> bool:
    """Whether a term holds `SUPPORT` events and non-events on each of its sides on the real table.

    A term that takes any value but 0 and 1 (a number, a product with a
    number) is not an indicator and always holds. An indicator -- a
    two-valued column, a label level, a product of two of them -- whose
    ones or zeros hold fewer events or non-events than the floor would
    leave a half of the table, or a fresh sample, with a separated term:
    the events-per-variable rule counts terms, this counts each term's
    own events (the rare outcomes' automatic models lost a half to it in
    5 of 18 table runs at 20,000 rows).
    """
    columns: "dict[str, object]" = {}
    for c in sources:
        columns.update(column_values(real, c))
    e1 = n1 = e0 = n0 = 0.0
    for value, outcome in zip(term(columns), y):  # type: ignore[arg-type, call-overload]
        if value != value or outcome != outcome:
            continue
        if value not in (0.0, 1.0):
            return True
        if value:
            n1, e1 = n1 + 1, e1 + outcome
        else:
            n0, e0 = n0 + 1, e0 + outcome
    return min(e1, n1 - e1, e0, n0 - e0) >= SUPPORT


# One term in this many of an automatic model is kept for pair products.
INTERACTION_SHARE = 4


def plan_auto(real: View, columns: "list[Column]", tier: str, table: str) -> "list[Analysis]":
    """The automatic panel of one table: its models fixed on the real table, asked of any table."""
    settings = TIERS[tier]
    eligible = [c for c in columns if c.kind in ("binary", "label", "count", "number") and c.missing <= 0.2]
    chosen = []
    for outcome in [c for c in columns if c.kind in ("binary", "count", "number")]:
        y = outcome_values(real, outcome)
        present = [b for b in y if b == b]  # type: ignore[attr-defined]
        if outcome.kind == "binary":
            events = sum(present)
            budget, family, kind = int(min(events, len(present) - events) // 10), "F4", "logistic"
        elif outcome.kind == "count":
            budget, family, kind = len(present) // 20, "F5", "poisson"
        else:
            budget, family, kind = len(present) // 20, "F3", "ols"
        budget = min(budget, settings["cap"])
        if budget < 1:
            continue
        ranked = sorted((c for c in eligible if c.name != outcome.name),
                        key=lambda c: (-strength(real, c, y), c.name))
        terms: "list[tuple[str, K.Term]]" = []
        used: "list[Column]" = []
        # A quarter of the terms is kept for the pair products: with the
        # main terms first, every automatic model on ST1, ST4 and ST6 at
        # 20,000 rows held no product (Codex's review), so an interaction
        # nobody named was never asked of a twin.
        kept_for_pairs = budget // INTERACTION_SHARE
        for c in ranked:
            room = budget - kept_for_pairs - len(terms)
            if room < 1:
                break
            add = column_terms(c, len(c.levels) if c.kind == "label" else room)
            if kind == "logistic":
                add = [(n, t) for n, t in add if indicator_supported(real, [c], t, y)]
            add = add[:room]
            if add:
                terms += add
                used += [c]
        if not used:
            continue
        strongest = used[:5]
        for i, a in enumerate(strongest):
            for b in strongest[i + 1:]:
                if len(terms) < budget:
                    (na, ta), (nb, tb) = column_terms(a, 1)[0], column_terms(b, 1)[0]
                    if kind != "logistic" or indicator_supported(real, [a, b], product(ta, tb), y):
                        terms += [(f"{na}*{nb}", product(ta, tb))]
        chosen += [(outcome, kind, family, used, terms)]
    if tier == "fast":
        by_kind = {"logistic": 3, "poisson": 1, "ols": 2}
        kept = []
        for item in chosen:
            if by_kind[item[1]] > 0:
                by_kind[item[1]] -= 1
                kept += [item]
        chosen = kept[:settings["outcomes"]]
    analyses = [Analysis(f"{table} auto {o.name}", auto_model(table, o, kind, family, used, terms))
                for o, kind, family, used, terms in chosen]
    pair = time_event(columns)
    if pair is not None:
        analyses += [Analysis(f"{table} auto survival", auto_cox(table, pair, eligible, real, settings["cap"]))]
    return analyses


def auto_model(table: str, outcome: Column, kind: str, family: str, used: "list[Column]",
               terms: "list[tuple[str, K.Term]]") -> "Callable[[View], list[Estimate]]":
    """One automatic model: its coefficients, and for a splined number its curve at the outer knots."""
    splined = [c for c in used if c.knots is not None and any(n == f"{c.name}_s1" for n, _t in terms)]
    # The first table a plan runs on is the real one (`yardstick`); its fit
    # starts every later table's Newton steps, which end at the same maximum.
    first: "dict[str, list[float]]" = {}

    def run(v: View) -> "list[Estimate]":
        columns: "dict[str, object]" = {}
        for c in used:
            columns.update(column_values(v, c))
        cols, ys = complete(columns, outcome_values(v, outcome))
        design = K.Design(cols, [("int", K.intercept)] + terms)
        levels_present(design)
        if kind == "ols":
            fit = K.ols(design, ys)
        else:
            fit = K.glm(design, ys, kind, start=first.get("beta"))
            if "beta" not in first:
                first["beta"] = fit.beta
        support = supports(design, ys, kind == "logistic")
        bent = {c.name for c in splined}
        names = [n for n in design.names
                 if n not in bent and not n.endswith("_s1") and not n.endswith("_s2")]
        out = coefs(fit, f"{table}/auto:{outcome.name}", family, support, names)
        for c in splined:
            knots = c.knots or []
            standard = standard_knots(c)

            def at(x: float, c: Column = c, standard: "list[float]" = standard) -> "dict[str, float]":
                z = (clamped(c, x) - c.center) / c.scale
                s = K.rcs(z, standard)
                return {c.name: z, f"{c.name}_s1": s[0], f"{c.name}_s2": s[1]}

            out += curve(fit, f"{table}/auto:{outcome.name}", family, cols[c.name],
                         ys if kind == "logistic" else None, kind == "logistic", at,
                         (knots[1] + knots[2]) / 2.0, [knots[0], knots[3]],
                         (knots[3] - knots[0]) / 10.0, f"curve_{c.name}")
        return [dataclasses.replace(e, tags=()) for e in out]

    return run


def auto_cox(table: str, pair: "tuple[str, list[str], str]", eligible: "list[Column]",
             real: View, cap: int) -> "Callable[[View], list[Estimate]]":
    """The automatic Cox model of a detected time and event pair."""
    start, ends, how = pair
    predictors = [c for c in eligible if c.name not in {start, *ends} and c.kind != "label"
                  and not ("status" in c.name or "event" in c.name)]

    def times(v: View) -> "tuple[list[float], list[float]]":
        if how == "date":
            days, which = v.days(start, ends)
            event = [math.nan if w < 0 else float(w == 0) for w in which]
        else:
            days, event = list(v.num(start)), list(v.num(ends[0]))
        if any(d == d and d < 0 for d in days):
            raise AnalysisError("negative time", "a follow-up time is below zero")
        return days, event

    days, event = times(real)
    budget = max(1, min(cap // 2, int(sum(e for e in event if e == e) // 10)))
    used = sorted(predictors, key=lambda c: (-strength(real, c, days), c.name))[:budget]

    def run(v: View) -> "list[Estimate]":
        days, event = times(v)
        columns: "dict[str, object]" = {"t": days, "e": event}
        for c in used:
            columns.update(column_values(v, c))
        cols, _y = complete(columns)
        names = [c.name for c in used]
        design = K.Design({n: cols[n] for n in names},
                          [(c.name, col(c.name) if c.kind == "binary" else standardized(c)) for c in used])
        fit = K.cox(design, cols["t"], [int(e) for e in cols["e"]])
        return coefs(fit, f"{table}/auto_cox", "F6", supports(design, cols["e"], True), names, ("time",))

    return run


# -- panels, halves and the yardstick ----------------------------------------


def run_panel(plan: "list[Analysis]", view: View) -> Panel:
    """Run every analysis on the view; one that stops is recorded by why, not raised."""
    estimates: "dict[str, Estimate]" = {}
    status: "dict[str, str]" = {}
    for analysis in plan:
        try:
            found = analysis.run(view)
        except K.FitTrouble as trouble:
            status[analysis.name] = trouble.kind
            continue
        except AnalysisError as error:
            status[analysis.name] = error.kind
            continue
        status[analysis.name] = "ok"
        for estimate in found:
            if math.isfinite(estimate.value):
                estimates[estimate.key] = estimate
    return Panel(estimates, status)


_MASK = (1 << 64) - 1


def splitmix64(x: int) -> int:
    """SplitMix64's output for one input."""
    z = (x + 0x9E3779B97F4A7C15) & _MASK
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & _MASK
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & _MASK
    return z ^ (z >> 31)


def groups_of(view: View, table: str, seed: int) -> "list[int]":
    """Each row's group of sixteen; on ST2 every row of a subject shares its subject's group."""
    if table == "ST2":
        out = []
        for s in view.text("sid"):
            key = int(s[1:]) if s is not None and s[1:].isdigit() else 0
            out += [splitmix64(seed * 1_000_003 + key) % 16]
        return out
    return [splitmix64(seed * 1_000_003 + i) % 16 for i in range(view.rows)]


def split(g: "list[int]", s: int) -> "tuple[list[int], list[int]]":
    """Rows whose group has bit ``s`` clear (half A) and set (half B)."""
    return [i for i, x in enumerate(g) if not (x >> s) & 1], [i for i, x in enumerate(g) if (x >> s) & 1]


@dataclasses.dataclass
class Yardstick:
    """The real panel, each supported estimate's half-split yardstick, and the analyses that held."""

    real: Panel
    h: "dict[str, float]"
    robust: "set[str]"


def yardstick(plan: "list[Analysis]", real: View, g: "list[int]") -> Yardstick:
    """Run the plan on the real table and its eight halves, one half at a time; keep what is supported.

    Supported: 22 rows in every defining cell on the real table and
    `HALF_SUPPORT` (11) in each of the eight halves -- a cell of 22 events
    split 21 and 1 in every half has a yardstick of noise (Codex's review:
    0.909, and a twin's 1.0 read inside against the real 0.5).
    """
    panel = run_panel(plan, real)
    diffs: "dict[str, list[float]]" = {k: [] for k, e in panel.estimates.items() if e.support >= SUPPORT}
    robust = {name for name, s in panel.status.items() if s == "ok"}
    for s in range(4):
        a, b = split(g, s)
        pa = run_panel(plan, real.subset(a, f"{real.name} A{s}"))
        pb = run_panel(plan, real.subset(b, f"{real.name} B{s}"))
        robust &= {n for n in pa.status if pa.status[n] == "ok" and pb.status.get(n) == "ok"}
        for key in diffs:
            if (key in pa.estimates and key in pb.estimates
                    and min(pa.estimates[key].support, pb.estimates[key].support) >= HALF_SUPPORT):
                diffs[key] += [pa.estimates[key].value - pb.estimates[key].value]
    h = {k: math.sqrt(sum(d * d for d in v) / 4.0) for k, v in diffs.items() if len(v) == 4}
    return Yardstick(panel, h, robust)


@dataclasses.dataclass
class Compared:
    """One supported estimate of one table against the real one."""

    key: str
    family: str
    tags: "tuple[str, ...]"
    real: float
    value: "float | None"
    h: float
    inside: bool
    sig_real: "bool | None"
    sig_twin: "bool | None"
    same_sign: bool


def compare(y: Yardstick, other: Panel) -> "list[Compared]":
    """Every supported estimate, inside its yardstick or not; one the table lacks is outside."""
    out = []
    for key in sorted(y.h):
        est = y.real.estimates[key]
        got = other.estimates.get(key)
        value = None if got is None else got.value
        inside = value is not None and abs(value - est.value) <= y.h[key]
        sig_r = sig_t = None
        if est.se:
            sig_r = abs(est.value / est.se) > Z
            sig_t = bool(got is not None and got.se and abs(got.value / got.se) > Z)
        same = value is not None and (value > 0) == (est.value > 0)
        out += [Compared(key, est.family, est.tags, est.value, value, y.h[key], inside, sig_r, sig_t, same)]
    return out


def stops(y: Yardstick, other: Panel) -> "list[str]":
    """The robust analyses (ran on the real table and all eight halves) that stop on this table."""
    return sorted(n for n in y.robust if other.status.get(n, "missing") != "ok")


# -- the controls, the product's twin, the report -----------------------------


def shuffled_text(text: str, seed: int) -> str:
    """The table with every column shuffled on its own (cells exactly as written)."""
    lines = text.splitlines()
    columns = [list(c) for c in zip(*(line.split(",") for line in lines[1:]))]
    r = random.Random(seed)
    for c in columns:
        r.shuffle(c)
    return lines[0] + "\n" + "".join(",".join(row) + "\n" for row in zip(*columns))


def thin_text(table: str, rows: int, wanted: int, seed: int) -> str:
    """A fresh draw of a tenth of the rows, resampled with replacement to ``wanted`` rows.

    A method that adds noise of its own: the negative control of
    twin-seed stability, which a shuffle cannot fail.
    """
    lines = T.text(table, max(SUPPORT * 10, rows // 10), seed).splitlines()
    r = random.Random(seed + 77)
    return lines[0] + "\n" + "".join(lines[1 + r.randrange(len(lines) - 1)] + "\n" for _ in range(wanted))


def rows_text(text: str, rows: "list[int]") -> str:
    """The header and the given data rows of a table's text, in their order."""
    lines = text.splitlines()
    return lines[0] + "\n" + "".join(lines[1 + i] + "\n" for i in rows)


def describe(folder: pathlib.Path, stem: str, text: str) -> object:
    """The product's description of a table: read, described, written and loaded (`kpi_shapes.describe`)."""
    import kpi_shapes

    return kpi_shapes.describe(folder, stem, text)


def generate(described: object, seed: int) -> "tuple[str, str]":
    """The product's twin of a description at one seed, as `synthtwin generate` writes it, and its report."""
    from synthtwin import generation, rendering

    loaded = described.loaded  # type: ignore[attr-defined]
    twin = generation.generate(loaded, seed)
    return rendering.twin_csv(twin), rendering.report(loaded, twin)


def report_reading(report: str) -> "dict[str, object]":
    """What the twin's report says per analysis family (K-BC-11).

    Plan P4-D398 records the block a later lane is to add: under
    `REPORT_HEADING`, one line per family F1 to F10 saying `carried`,
    `approximate` or `not carried` with its reason. Today's report has no
    such block, and this reads that it has none: the families named and
    the ones called carried.
    """
    lines = report.splitlines()
    at = [i for i, line in enumerate(lines) if REPORT_HEADING.lower() in line.lower()]
    if not at:
        return {"block": False, "named": [], "carried": []}
    named: "list[str]" = []
    carried: "list[str]" = []
    for line in lines[at[0] + 1:]:
        if not line.strip():
            break
        for family in REPORT_FAMILIES:
            if line.strip().startswith(family + " ") or line.strip().startswith(family + ":"):
                named += [family]
                if " carried" in line and "not carried" not in line:
                    carried += [family]
    return {"block": True, "named": named, "carried": carried}


# -- trained models (TSTR) and the broad discriminator --------------------


def features(v: View, columns: "list[Column]", skip: str) -> "list[list[float | None]]":
    """Every usable column but ``skip`` as a feature: numbers, 0/1 flags, label levels by code."""
    out: "list[list[float | None]]" = []
    for c in columns:
        if c.name == skip or c.kind not in ("binary", "label", "count", "number"):
            continue
        if c.kind == "label":
            code = {lv: float(k) for k, lv in enumerate(sorted(c.levels))}
            out += [[None if x is None else code.get(x) for x in v.text(c.name)]]
        else:
            out += [[None if x != x else x for x in outcome_values(v, c)]]  # type: ignore[attr-defined]
    return out


def tstr(train: View, test: View, columns: "list[Column]", outcome: Column,
         rounds: int) -> "tuple[float, list[float]]":
    """The AUC on ``test`` of boosted trees trained on ``train``, and their gain per feature."""
    y = outcome_values(train, outcome)
    keep = [x == x for x in y]  # type: ignore[attr-defined]
    found = [[x for x, k in zip(f, keep) if k] for f in features(train, columns, outcome.name)]
    booster = K.Booster(rounds=rounds).fit(found, [int(x) for x in y if x == x])  # type: ignore[attr-defined]
    ty = outcome_values(test, outcome)
    tkeep = [x == x for x in ty]  # type: ignore[attr-defined]
    tf = [[x for x, k in zip(f, tkeep) if k] for f in features(test, columns, outcome.name)]
    return K.auc(booster.predict(tf), [int(x) for x in ty if x == x]), booster.gain  # type: ignore[attr-defined]


def pmse(real: View, other: View, columns: "list[Column]", keys: int) -> "tuple[float, list[str]]":
    """The propensity mean-squared error over its value under no difference, and the columns it rests on most.

    A logistic discriminator of real rows against the other table's, on
    every usable column's main effect (numbers and dates standardized and
    held to the real table's range, numbers with their two spline terms,
    labels by level, a missing indicator where a column has empty cells)
    and the products of the first ``keys`` columns that are not labels. The ratio is pMSE / ((k - 1)(1 - c)^2 c / N) (Woo et
    al. 2009; Snoke et al. 2018): about 1 where the two cannot be told
    apart. Terms are built a chunk at a time from the two tables' own
    columns, so memory is the two tables.
    """
    usable = [c for c in columns if c.kind in ("binary", "label", "count", "number", "date")]
    joined: "dict[str, object]" = {}
    terms: "list[tuple[str, K.Term]]" = [("int", K.intercept)]
    standard: "dict[str, K.Term]" = {}
    for c in usable:
        if c.kind == "label":
            joined[c.name] = real.text(c.name) + other.text(c.name)
            for lv in c.levels[1:]:
                terms += [(f"{c.name}={lv}", lambda ch, n=c.name, lv=lv: [float(x == lv) for x in ch[n]])]
            continue
        if c.kind == "date":
            a, b = real.date_days(c.name), other.date_days(c.name)
        else:
            a, b = outcome_values(real, c), outcome_values(other, c)
        joined[c.name] = array.array("d", a) + array.array("d", b)  # type: ignore[arg-type]
        present = [x for x in a if x == x]  # type: ignore[attr-defined]
        m = statistics.fmean(present)
        sd = statistics.pstdev(present) or 1.0
        held = dataclasses.replace(c, low=min(present), high=max(present))
        standard[c.name] = (lambda ch, h=held, m=m, sd=sd: [0.0 if x != x else (x - m) / sd
                                                             for x in clamped_chunk(h, ch[h.name])])
        terms += [(c.name, standard[c.name])]
        if c.knots is not None:
            for j in (0, 1):
                term = K.rcs_term(c.knots, j, 1.0 / sd)
                terms += [(f"{c.name}_s{j + 1}", lambda ch, h=held, m=m, f=term:
                           [f(m if x != x else x) for x in clamped_chunk(h, ch[h.name])])]
        if c.missing > 0:
            terms += [(f"{c.name}_na", lambda ch, n=c.name: [1.0 if x != x else 0.0 for x in ch[n]])]
    key_names = [c.name for c in usable if c.kind != "label"][:keys]
    for i, x in enumerate(key_names):
        for z in key_names[i + 1:]:
            terms += [(f"{x}*{z}", product(standard[x], standard[z]))]
    label = [1.0] * real.rows + [0.0] * other.rows
    design = K.Design(joined, terms)  # type: ignore[arg-type]
    kept = set(K.independent_terms(design))
    if len(kept) < len(terms):
        terms = [t for t in terms if t[0] in kept]
        design = K.Design(joined, terms)  # type: ignore[arg-type]
    fit = K.glm(design, label, "logistic", max_iter=15, tol=1e-6, strict=False)
    n, share = len(label), real.rows / len(label)
    total = 0.0
    for start, stop, cols in design.chunks():
        eta = K.linear(cols, fit.beta)
        total += sum((1.0 / (1.0 + math.exp(-max(-35.0, min(35.0, e)))) - share) ** 2 for e in eta)
    k = len(terms)
    null = (k - 1) * (1.0 - share) ** 2 * share / n
    order = sorted((i for i in range(1, k)), key=lambda i: -abs(fit.beta[i] / fit.se[i]) if fit.se[i] else 0.0)
    named: "list[str]" = []
    for i in order:
        base = fit.names[i].split("*")[0].split("=")[0]
        for tail in ("_na", "_s1", "_s2"):
            base = base[: -len(tail)] if base.endswith(tail) else base
        if base not in named:
            named += [base]
        if len(named) == 10:
            break
    return (total / n) / null, named


# -- one table, end to end ---------------------------------------------------------


@dataclasses.dataclass
class Side:
    """One table set against the real one: its comparisons, stops, prediction and discrimination."""

    compared: "list[Compared]"
    stops: "list[str]"
    panel: Panel
    tstr: "dict[str, tuple[float, float]]"
    pmse: float
    leaning: "list[str]"
    heavy: bool = True


@dataclasses.dataclass
class TableRun:
    """Everything one table at one seed gave: the yardstick, each side's runs, the report, the cost."""

    table: str
    rows: int
    seed: int
    yard: Yardstick
    tstr_yard: "dict[str, tuple[float, float, float]]"
    sides: "dict[str, list[Side]]"
    report: "dict[str, object]"
    seconds: float
    product_seconds: float


def trained_outcomes(columns: "list[Column]", table: str, tier: str) -> "list[Column]":
    """The outcomes a trained model is asked to predict: the seeded one; at the slow tier every two-valued column."""
    seeded = [c for c in columns if c.name == PREDICTED.get(table)]
    if TIERS[tier]["trained"] != "binary":
        return seeded
    return seeded + [c for c in columns if c.kind == "binary" and c.name != PREDICTED.get(table)]


def _side(y: Yardstick, plan: "list[Analysis]", real: View, view: View, columns: "list[Column]",
          tier: str, train: "View | None", test: "View | None", predicted: "list[Column]",
          imp_a: "dict[str, list[float]]", heavy: bool = True) -> Side:
    """One table against the real one; ``heavy`` adds the discriminator and the trained models.

    A discriminator or a model that cannot be fitted on this table leaves
    its number out, and a missing trained-model AUC is scored outside.
    """
    panel = run_panel(plan, view)
    settings = TIERS[tier]
    ratio, leaning = math.nan, []
    found: "dict[str, tuple[float, float]]" = {}
    if heavy:
        try:
            ratio, leaning = pmse(real, view, columns, settings["keys"])
        except (K.FitTrouble, AnalysisError):
            ratio, leaning = math.nan, ["(the discriminator could not be fitted)"]
        if train is not None and test is not None:
            for outcome in predicted:
                try:
                    auc, gain = tstr(train, test, columns, outcome, settings["rounds"])
                    found[outcome.name] = (auc, K.spearman(gain, imp_a[outcome.name]))
                except (K.FitTrouble, AnalysisError):
                    pass
    return Side(compare(y, panel), stops(y, panel), panel, found, ratio, leaning, heavy)


def run_table(table: str, rows: int, seed: int, twins: "tuple[int, ...]", tier: str,
              folder: pathlib.Path, thin: bool = False) -> TableRun:
    """One table at one seed: the yardstick, today's twin at each twin seed, the controls, the report."""
    started = time.perf_counter()
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{table}-{seed}.csv"
    T.write(path, table, rows, seed)
    text = path.read_text(encoding="utf-8")
    real = read(path, f"{table} real")
    columns = schema(real)
    plan = TARGETED[table](real) + plan_auto(real, columns, tier, table)
    g = groups_of(real, table, seed)
    y = yardstick(plan, real, g)
    candidates = trained_outcomes(columns, table, tier)
    a_rows, b_rows = split(g, 0)
    half_a = real.subset(a_rows, "A") if candidates else None
    half_b = real.subset(b_rows, "B") if candidates else None
    tstr_yard: "dict[str, tuple[float, float, float]]" = {}
    imp_a: "dict[str, list[float]]" = {}
    predicted: "list[Column]" = []
    rounds = TIERS[tier]["rounds"]
    # Split 0 first, every candidate: a model kept is one the seeded
    # table names or one whose half-A model reaches TRAINED_AUC on half B.
    # Then the other three splits, one pair of halves held at a time.
    first: "dict[str, tuple[float, list[float], list[float], float]]" = {}
    for outcome in candidates if half_a is not None and half_b is not None else []:
        try:
            auc_ab, gain_a = tstr(half_a, half_b, columns, outcome, rounds)  # type: ignore[arg-type]
            if outcome.name != PREDICTED.get(table) and auc_ab < TRAINED_AUC:
                continue
            auc_ba, gain_b = tstr(half_b, half_a, columns, outcome, rounds)  # type: ignore[arg-type]
        except (K.FitTrouble, AnalysisError):
            continue
        first[outcome.name] = (auc_ab, gain_a, gain_b, auc_ab - auc_ba)
    diffs: "dict[str, list[float]]" = {name: [held[3]] for name, held in first.items()}
    for s in (1, 2, 3) if first else ():
        sa, sb = split(g, s)
        va, vb = real.subset(sa, "A"), real.subset(sb, "B")
        for outcome in [c for c in candidates if c.name in diffs]:
            try:
                diffs[outcome.name] += [tstr(va, vb, columns, outcome, rounds)[0]
                                        - tstr(vb, va, columns, outcome, rounds)[0]]
            except (K.FitTrouble, AnalysisError):
                del diffs[outcome.name]
    for outcome in [c for c in candidates if c.name in diffs]:
        auc_ab, gain_a, gain_b, _d = first[outcome.name]
        found = diffs[outcome.name]
        tstr_yard[outcome.name] = (auc_ab, math.sqrt(sum(d * d for d in found) / 4.0), K.spearman(gain_a, gain_b))
        imp_a[outcome.name] = gain_a
        predicted += [outcome]
    sides: "dict[str, list[Side]]" = {"twin": [], "replicate": [], "shuffled": [], "thin": []}
    product_seconds = 0.0
    clock = time.perf_counter()
    described = describe(folder / "product", f"{table}-{seed}", text)
    described_a = (describe(folder / "product", f"{table}-{seed}-A", rows_text(text, a_rows))
                   if predicted else None)
    product_seconds += time.perf_counter() - clock
    report: "dict[str, object]" = {}
    for k in twins:
        clock = time.perf_counter()
        twin_text, twin_report = generate(described, k)
        twin_a = read(generate(described_a, k)[0], "twin A") if described_a is not None else None
        product_seconds += time.perf_counter() - clock
        if not report:
            report = report_reading(twin_report)
        sides["twin"] += [_side(y, plan, real, read(twin_text, "twin"), columns, tier, twin_a, half_b,
                                predicted, imp_a)]
        replicate_seed = seed * 1000 + 100 + k
        heavy = k in CONTROL_HEAVY_SEEDS
        rep_a = (read(T.text(table, len(a_rows), replicate_seed + 500), "replicate A")
                 if predicted and heavy else None)
        sides["replicate"] += [_side(y, plan, real, read(T.text(table, rows, replicate_seed), "replicate"),
                                     columns, tier, rep_a, half_b, predicted, imp_a, heavy)]
        shuf_a = read(shuffled_text(rows_text(text, a_rows), seed * 31 + k + 7), "shuffled A") \
            if predicted and heavy else None
        sides["shuffled"] += [_side(y, plan, real, read(shuffled_text(text, seed * 31 + k), "shuffled"),
                                    columns, tier, shuf_a, half_b, predicted, imp_a, heavy)]
        if thin:
            view = read(thin_text(table, rows, real.rows, seed * 1000 + 300 + k), "thin")
            panel = run_panel(plan, view)
            sides["thin"] += [Side(compare(y, panel), stops(y, panel), panel, {}, math.nan, [], False)]
    if table == "ST5":
        # On a null table a shuffle IS a perfect twin, so the negative
        # control of the fabrication count is the structured table: ST1
        # at the same seed holds ST5's columns, related.
        panel = run_panel(plan, read(T.text("ST1", rows, seed), "structured"))
        sides["structured"] = [Side(compare(y, panel), stops(y, panel), panel, {}, math.nan, [], False)]
    return TableRun(table, real.rows, seed, y, tstr_yard, sides, report,
                    time.perf_counter() - started, product_seconds)


def run_to_dict(run: TableRun) -> "dict[str, object]":
    """A table run as plain data, for a child process to hand back as JSON."""
    out = dataclasses.asdict(run)
    out["yard"]["robust"] = sorted(run.yard.robust)  # type: ignore[index]
    return out


def _panel_from(data: "dict") -> Panel:
    return Panel({k: Estimate(e["key"], e["family"], e["value"], e["se"], e["support"], tuple(e["tags"]))
                  for k, e in data["estimates"].items()}, dict(data["status"]))


def run_from_dict(data: "dict") -> TableRun:
    """The table run `run_to_dict` wrote."""
    yard = Yardstick(_panel_from(data["yard"]["real"]), dict(data["yard"]["h"]), set(data["yard"]["robust"]))
    sides: "dict[str, list[Side]]" = {}
    for name, items in data["sides"].items():
        sides[name] = [Side([Compared(c["key"], c["family"], tuple(c["tags"]), c["real"], c["value"], c["h"],
                                      c["inside"], c["sig_real"], c["sig_twin"], c["same_sign"])
                             for c in s["compared"]],
                            list(s["stops"]), _panel_from(s["panel"]),
                            {k: (v[0], v[1]) for k, v in s["tstr"].items()}, s["pmse"], list(s["leaning"]),
                            bool(s.get("heavy", True)))
                       for s in items]
    return TableRun(data["table"], data["rows"], data["seed"], yard,
                    {k: (v[0], v[1], v[2]) for k, v in data["tstr_yard"].items()}, sides,
                    dict(data["report"]), data["seconds"], data["product_seconds"])


def run_tables(tier: str, folder: pathlib.Path, tables: "tuple[str, ...] | None" = None,
               seeds: "tuple[int, ...] | None" = None, twins: "tuple[int, ...] | None" = None,
               rows: "int | None" = None) -> "list[TableRun]":
    """Every table and seed of a tier (or the ones named), each in a folder of its own."""
    settings = TIERS[tier]
    out = []
    for table in tables or settings["tables"]:
        for seed in seeds or settings["seeds"]:
            out += [run_table(table, rows or settings["rows"], seed, twins or settings["twins"], tier,
                              folder / f"{table}-{seed}", thin=tier == "slow")]
    return out


# -- the KPIs --------------------------------------------------------------------


def _share(rows: "list[Compared]") -> "float | None":
    return None if not rows else sum(1 for r in rows if r.inside) / len(rows)


def _median(values: "list[float]") -> float:
    return statistics.median(values) if values else math.nan


def _seeds(run: TableRun, side: str) -> "list[Side]":
    return run.sides[side]


def shares(runs: "list[TableRun]", side: str, pick: "Callable[[Compared], bool]") -> "list[float]":
    """The share inside, one per twin seed, pooled over every table run, of the picked estimates."""
    count = max((len(r.sides[side]) for r in runs), default=0)
    out = []
    for k in range(count):
        rows = [c for r in runs if k < len(r.sides[side]) for c in r.sides[side][k].compared if pick(c)]
        value = _share(rows)
        if value is not None:
            out += [value]
    return out


def gap_points(runs: "list[TableRun]", pick: "Callable[[Compared], bool]",
               side: str = "twin") -> "tuple[float, float, int]":
    """(replicate's median share minus the side's, in points; the worst seed's gap; supported count)."""
    rep = shares(runs, "replicate", pick)
    mine = shares(runs, side, pick)
    supported = sum(1 for r in runs for c in (r.sides["replicate"][0].compared if r.sides["replicate"] else [])
                    if pick(c))
    if not rep or not mine:
        return math.nan, math.nan, supported
    return (round(100.0 * (_median(rep) - _median(mine)), 1),
            round(100.0 * (_median(rep) - min(mine)), 1), supported)


def _not_null(c: Compared) -> bool:
    return not c.key.startswith("ST5/")


def _joint(c: Compared) -> bool:
    """An estimate of how columns go together: not the null table's, and not one column's own margin.

    A margin -- rows per subject, a zero share, the complete-case share
    of a model whose columns but one are whole -- is one column's own
    count, which a column-wise shuffle keeps exactly (measured: the
    shuffle inside on all eight of ST2's rows-per-subject shares), so it
    says nothing of the relations the joint KPIs measure. K-BC-06 reads
    the rows per subject on their own.
    """
    return _not_null(c) and "margin" not in c.tags


def _f8_rows(runs: "list[TableRun]", side: str, k: int) -> "list[Compared]":
    out = []
    for r in runs:
        if k >= len(r.sides[side]):
            continue
        if not r.sides[side][k].heavy:
            continue
        for name, (auc_ab, yard, _rank) in r.tstr_yard.items():
            got = r.sides[side][k].tstr.get(name)
            value = None if got is None else got[0]
            inside = value is not None and abs(value - auc_ab) <= yard
            out += [Compared(f"{r.table}/tstr:{name}", "F8", (), auc_ab, value, yard, inside,
                             None, None, True)]
    return out


def family_shares(runs: "list[TableRun]", side: str) -> "dict[str, list[float]]":
    """Per family F1 to F9, the share inside per twin seed (F8 from the trained models)."""
    out: "dict[str, list[float]]" = {}
    count = max((len(r.sides[side]) for r in runs), default=0)
    for family in FAMILIES:
        per = []
        for k in range(count):
            if family == "F8":
                rows = _f8_rows(runs, side, k)
            else:
                rows = [c for r in runs if k < len(r.sides[side]) for c in r.sides[side][k].compared
                        if c.family == family and _joint(c)]
            value = _share(rows)
            if value is not None:
                per += [value]
        if per:
            out[family] = per
    return out


# A family's checkpoint target, in points under the replicate (K-BC-01):
# its shuffled twin must stand further under than this, or the family's
# clause cannot fail for a twin with no joint structure.
FAMILY_TARGET = 25.0


def kpi_01(runs: "list[TableRun]", suffix: str = "") -> "dict[str, object]":
    """K-BC-01, replication parity family by family (F1 to F9), margins left out.

    Its controls hold where the replicate's pooled share is a fresh
    sample's, the shuffled twin's pooled share stands more than 10 points
    under it, and the shuffled twin stands more than `FAMILY_TARGET`
    points under the replicate in EVERY family of at least
    `FAMILY_MINIMUM` supported estimates -- a family whose shuffle meets
    the family target is named, and the run is void for this KPI.
    """
    fam = {side: family_shares(runs, side) for side in ("twin", "replicate", "shuffled")}

    def pooled(side: str) -> "list[float]":
        count = max((len(r.sides[side]) for r in runs), default=0)
        out = []
        for k in range(count):
            rows = [c for r in runs if k < len(r.sides[side]) for c in r.sides[side][k].compared if _joint(c)]
            rows += _f8_rows(runs, side, k)
            value = _share(rows)
            if value is not None:
                out += [value]
        return out

    p = {side: pooled(side) for side in fam}
    gap = round(100.0 * (_median(p["replicate"]) - _median(p["twin"])), 1)
    shuf_gap = 100.0 * (_median(p["replicate"]) - _median(p["shuffled"]))
    sizes = {f: sum(1 for r in runs for c in r.sides["replicate"][0].compared
                    if c.family == f and _joint(c)) + (sum(len(r.tstr_yard) for r in runs) if f == "F8" else 0)
             for f in fam["replicate"]}
    judged = [f for f in sorted(fam["replicate"]) if sizes[f] >= FAMILY_MINIMUM]
    worst = max((100.0 * (_median(fam["replicate"][f]) - _median(fam["twin"].get(f, [0.0]))) for f in judged),
                default=math.nan)
    void = [f for f in judged
            if not 100.0 * (_median(fam["replicate"][f]) - _median(fam["shuffled"].get(f, [math.nan]))) > FAMILY_TARGET]
    supported = sum(1 for r in runs for c in r.sides["replicate"][0].compared if _joint(c)) + sum(
        len(r.tstr_yard) for r in runs)
    detail = "; ".join(
        f"{f} twin {_median(fam['twin'].get(f, [math.nan])):.2f} rep {_median(fam['replicate'][f]):.2f} "
        f"shuf {_median(fam['shuffled'].get(f, [math.nan])):.2f}" for f in sorted(fam["replicate"]))
    detail += "; the shuffle meets the family target, void: " + (", ".join(void) or "none")
    return {
        f"pooled_points_below_replicate{suffix}": gap,
        f"worst_family_points_below_replicate{suffix}": round(worst, 1),
        f"twin_pooled_share{suffix}": round(_median(p["twin"]), 3),
        f"replicate_pooled_share{suffix}": round(_median(p["replicate"]), 3),
        f"shuffled_pooled_share{suffix}": round(_median(p["shuffled"]), 3),
        f"supported_estimates{suffix}": supported,
        f"points_below_shuffled{suffix}": round(gap - shuf_gap, 1),
        f"families_control_void{suffix}": len(void),
        f"controls_hold{suffix}": bool(replicate_holds(_median(p["replicate"]), supported) and shuf_gap > 10.0
                                       and not void),
        "_detail": detail,
    }


def _truth_rows(runs: "list[TableRun]") -> "list[tuple[TableRun, str, str]]":
    out = []
    for r in runs:
        for truth, (key, _value) in T.TRUTHS[r.table].items():
            out += [(r, truth, key)]
    return out


def _recovered(r: TableRun, key: str, side: Side) -> bool:
    if key not in r.yard.h:
        return False
    if key == "ST5/null:significant_share":
        got = side.panel.estimates.get(key)
        return got is not None and got.value <= 0.08
    row = next((c for c in side.compared if c.key == key), None)
    if row is None or not row.inside:
        return False
    if row.sig_real is not None and row.sig_twin != row.sig_real:
        return False
    return not (row.sig_real and not row.same_sign)


def mcnemar(only_replicate: int, only_twin: int) -> float:
    """McNemar's z of a paired count: (b - c) / sqrt(b + c), 0 where neither side holds one alone."""
    total = only_replicate + only_twin
    return 0.0 if total == 0 else round((only_replicate - only_twin) / math.sqrt(total), 2)


def kpi_02(runs: "list[TableRun]", suffix: str = "") -> "dict[str, object]":
    """K-BC-02, the seeded truths recovered, or named as not carried (today: none named).

    A truth is charged to the twin only where the fresh replicate of the
    same run gets it back: one the replicate misses is counted beside, as
    `replicate_missed`, never as the twin's. Even so a perfect twin, a
    second draw of the same noise, misses some truths the replicate gets
    and gets some it misses (measured at 20,000 rows: 6 and 3 of 96 on a
    stand-in perfect twin, one of the 6 of three columns), so the target
    is McNemar's paired comparison of the two: the truths only the
    replicate gets less those only the twin gets, over the square root of
    their sum, at most 2 -- for all truths and for those of three columns.
    A twin recovering none reads sqrt(replicate_recovered) (all truths)
    and sqrt(three_way_replicate_recovered) (three columns), so a clause
    can fail only where that count exceeds 4; the ledger states no target
    where it does not (the fast part's three-way clause: one truth).
    """
    truths = _truth_rows(runs)
    eligible = [(r, p, k) for r, p, k in truths if k in r.yard.h]

    def recovered(side: str) -> "list[tuple[TableRun, str, str]]":
        out = []
        for r, p, k in truths:
            seeds = r.sides[side]
            hits = sum(1 for s in seeds if _recovered(r, k, s))
            if seeds and hits * 2 > len(seeds):
                out += [(r, p, k)]
        return out

    got = {side: recovered(side) for side in ("twin", "replicate", "shuffled")}
    named: "list[tuple[TableRun, str, str]]" = []
    missed = [x for x in truths if x not in got["twin"] and x not in named and x in got["replicate"]]
    three = [x for x in missed if x[1] in T.THREE_WAY]
    beyond = [x for x in got["twin"] if x not in got["replicate"]]
    beyond_three = [x for x in beyond if x[1] in T.THREE_WAY]
    rep_share = len([x for x in got["replicate"] if x in eligible]) / max(1, len(eligible))
    shuf_share = len([x for x in got["shuffled"] if x in eligible]) / max(1, len(eligible))
    return {
        f"truths_missed_unnamed{suffix}": len(missed),
        f"three_way_missed_unnamed{suffix}": len(three),
        f"missed_over_replicate_z{suffix}": mcnemar(len(missed), len(beyond)),
        f"three_way_missed_over_replicate_z{suffix}": mcnemar(len(three), len(beyond_three)),
        f"truths_recovered_beyond_replicate{suffix}": len(beyond),
        f"truths_measured{suffix}": len(truths),
        f"truths_floor_eligible{suffix}": len(eligible),
        f"truths_recovered{suffix}": len(got["twin"]),
        f"truths_named{suffix}": len(named),
        f"replicate_recovered{suffix}": len(got["replicate"]),
        f"three_way_replicate_recovered{suffix}": len([x for x in got["replicate"] if x[1] in T.THREE_WAY]),
        f"replicate_missed{suffix}": len(truths) - len(got["replicate"]),
        f"shuffled_recovered{suffix}": len(got["shuffled"]),
        f"truths_recovered_below_shuffled{suffix}": len(got["shuffled"]) - len(got["twin"]),
        f"controls_hold{suffix}": bool(rep_share >= 0.5 and shuf_share <= rep_share - 0.25),
        "_detail": "recovered by the twin: " + (", ".join(f"{r.table}-{r.seed} {p}" for r, p, _k in got["twin"]) or "none")
        + "; missed: " + ", ".join(f"{r.table}-{r.seed} {p}" for r, p, _k in missed),
    }


def kpi_03(runs: "list[TableRun]", suffix: str = "") -> "dict[str, object]":
    """K-BC-03, decisions kept and significance invented; on ST5 the share of pairs called associated."""
    significant = sum(1 for r in runs for c in (r.sides["replicate"][0].compared if r.sides["replicate"] else [])
                      if c.sig_real and c.family != "F1" and _joint(c))

    def rates(side: str) -> "tuple[float, float]":
        kept, fabricated = [], []
        count = max((len(r.sides[side]) for r in runs), default=0)
        for k in range(count):
            rows = [c for r in runs if k < len(r.sides[side]) for c in r.sides[side][k].compared
                    if c.sig_real is not None and c.family != "F1" and _joint(c)]
            sig = [c for c in rows if c.sig_real]
            not_sig = [c for c in rows if not c.sig_real]
            if sig:
                kept += [sum(1 for c in sig if c.sig_twin and c.same_sign) / len(sig)]
            if not_sig:
                fabricated += [sum(1 for c in not_sig if c.sig_twin) / len(not_sig)]
        return _median(kept), _median(fabricated)

    out_rates = {side: rates(side) for side in ("twin", "replicate", "shuffled")}
    kept_gap = 100.0 * (out_rates["replicate"][0] - out_rates["twin"][0])
    value: "dict[str, object]" = {
        f"kept_points_below_replicate{suffix}": round(kept_gap, 1),
        f"fabricated_points_above_replicate{suffix}": round(
            100.0 * (out_rates["twin"][1] - out_rates["replicate"][1]), 1),
        f"kept_points_below_shuffled{suffix}": round(100.0 * (out_rates["shuffled"][0] - out_rates["twin"][0]), 1),
        f"real_significant{suffix}": significant,
        f"twin_kept{suffix}": round(out_rates["twin"][0], 3),
        f"replicate_kept{suffix}": round(out_rates["replicate"][0], 3),
        f"shuffled_kept{suffix}": round(out_rates["shuffled"][0], 3),
        f"controls_hold{suffix}": bool(out_rates["replicate"][0] >= 0.8
                                       and out_rates["shuffled"][0] < out_rates["replicate"][0] - 0.10),
    }
    null_runs = [r for r in runs if r.table == "ST5"]
    if null_runs:
        def null_share(side: str) -> float:
            values = [s.panel.estimates["ST5/null:significant_share"].value
                      for r in null_runs for s in r.sides[side]
                      if "ST5/null:significant_share" in s.panel.estimates]
            return _median(values)

        structured = [r.sides["structured"][0].panel.estimates["ST5/null:significant_share"].value
                      for r in null_runs if r.sides.get("structured")]
        value[f"null_significant_share{suffix}"] = round(null_share("twin"), 3)
        value[f"null_replicate_share{suffix}"] = round(null_share("replicate"), 3)
        value[f"null_controls_hold{suffix}"] = bool(null_share("replicate") <= 0.08
                                                    and structured and min(structured) > 0.08)
    return value


def _over(gap: float, yard: float) -> float:
    """An AUC gap in yardsticks: the yardstick as measured; at a yardstick of 0, any shortfall is infinite."""
    if yard > 0.0:
        return gap / yard
    return 0.0 if gap <= 0.0 else math.inf


def kpi_04(runs: "list[TableRun]", suffix: str = "") -> "dict[str, object]":
    """K-BC-04, prediction: the trained model's AUC gap over its yardstick; importance ranks against the replicate.

    Every scored model is asked of every side at every seed it is
    expected on -- today's twin at each twin seed, the controls at their
    heavy seeds -- and one missing there (a model that could not be
    trained or scored) counts as an infinite gap and a rank correlation
    of -1, never as nothing: a twin whose models fail cannot read as a
    twin that matches (Codex's review). The controls hold only where
    neither control misses a model. The gap's denominator is the model's
    half-split yardstick as measured, as the ledger states it.
    """
    gaps: "dict[str, dict[tuple[str, int, str], float]]" = {"twin": {}, "replicate": {}, "shuffled": {}}
    ranks: "dict[str, dict[tuple[str, int, str], float]]" = {"twin": {}, "replicate": {}, "shuffled": {}}
    missing = {side: 0 for side in gaps}
    for r in runs:
        for name, (auc_ab, yard, _rank) in r.tstr_yard.items():
            if auc_ab < TRAINED_AUC:
                continue
            for side in gaps:
                expected = [s for s in r.sides[side] if s.heavy]
                per_gap: "list[float]" = []
                per_rank: "list[float]" = []
                for s in expected:
                    got = s.tstr.get(name)
                    if got is None:
                        missing[side] += 1
                        per_gap += [math.inf]
                        per_rank += [-1.0]
                    else:
                        per_gap += [_over(auc_ab - got[0], yard)]
                        per_rank += [got[1]]
                if not expected:
                    missing[side] += 1
                    per_gap, per_rank = [math.inf], [-1.0]
                gaps[side][(r.table, r.seed, name)] = _median(per_gap)
                ranks[side][(r.table, r.seed, name)] = _median(per_rank)
    if not gaps["twin"] or not gaps["replicate"] or not gaps["shuffled"]:
        return {f"controls_hold{suffix}": False}
    worst = {side: max(v.values()) for side, v in gaps.items()}
    rank_gap = max((ranks["replicate"][k] - ranks["twin"][k] for k in ranks["twin"] if k in ranks["replicate"]),
                   default=math.nan)
    return {
        f"auc_gap_over_yardstick{suffix}": round(worst["twin"], 2),
        f"auc_gap_over_shuffled{suffix}": round(worst["twin"] - worst["shuffled"], 2),
        f"importance_rank_below_replicate{suffix}": round(rank_gap, 3),
        f"replicate_auc_gap_over_yardstick{suffix}": round(worst["replicate"], 2),
        f"shuffled_auc_gap_over_yardstick{suffix}": round(worst["shuffled"], 2),
        f"trained_models{suffix}": len(gaps["replicate"]),
        f"twin_models_missing{suffix}": missing["twin"],
        f"controls_hold{suffix}": bool(worst["replicate"] <= 3.0 and min(gaps["shuffled"].values()) > 3.0
                                       and missing["replicate"] == 0 and missing["shuffled"] == 0),
        "_detail": "trained models scored: " + ", ".join(f"{t}-{d} {n}" for t, d, n in sorted(gaps["replicate"]))
        + "; missing on today's twin, the replicate, the shuffle: "
        + ", ".join(str(missing[side]) for side in ("twin", "replicate", "shuffled")),
    }


# Tables whose rows are not independent: ST2's rows come several to a
# subject, which the discriminator's null value (Woo et al.) does not
# allow for -- the replicate's own ratio there ranged from 2.57 to 15.16
# over twin seeds at 20,000 rows -- so its ratio stands beside the
# maximum, not in it; K-BC-06 measures that table.
CLUSTERED = ("ST2",)


def kpi_05(runs: "list[TableRun]", suffix: str = "") -> "dict[str, object]":
    """K-BC-05, the broad discriminator: the twin's pMSE ratio over the replicate's, worst table.

    On the null table a shuffle IS a perfect twin with exact marginals,
    its ratio under 1, and on a clustered table the ratio's null value
    does not hold; the maximum, the shuffled control and the twin's ratio
    to the shuffle are read on the other tables, and the null and
    clustered tables' ratios over the replicate stand beside them.

    A discriminator is expected on every side at every heavy seed. One
    that could not be fitted is never left out (a NaN in a maximum hides
    it, or not, by the tables' order -- Codex's review): on today's twin
    it counts as an infinite ratio, and on either control it voids the
    controls, as does a replicate whose discriminator is missing.
    """
    over: "dict[str, list[float]]" = {"twin": [], "shuffled": []}
    leaning = []
    shuffled_control: "list[float]" = []
    twin_control: "list[float]" = []
    beside: "dict[str, list[float]]" = {"null": [], "clustered": []}
    failed = {"twin": 0, "replicate": 0, "shuffled": 0}

    def measured(r: TableRun, side: str) -> float:
        """The median ratio over the side's heavy seeds; NaN where any is missing."""
        values = [s.pmse for s in r.sides[side] if s.heavy]
        if not values or any(v != v for v in values):
            failed[side] += 1
            return math.nan
        return _median(values)

    for r in runs:
        rep = measured(r, "replicate")
        found = {side: measured(r, side) for side in over}
        ratios = {side: (math.inf if found[side] != found[side] else found[side] / rep) for side in over}
        if rep != rep:
            ratios = {side: math.inf for side in over}
        if r.table == "ST5":
            beside["null"] += [ratios["twin"]]
        elif r.table in CLUSTERED:
            beside["clustered"] += [ratios["twin"]]
        else:
            over["twin"] += [ratios["twin"]]
            shuffled_control += [ratios["shuffled"]]
            twin_control += [ratios["twin"] / ratios["shuffled"] if math.isfinite(ratios["shuffled"]) else math.inf]
        if r.sides["twin"]:
            leaning += [f"{r.table}: " + ", ".join(r.sides["twin"][0].leaning)]
    return {
        f"pmse_over_replicate{suffix}": round(max(over["twin"]), 2) if over["twin"] else None,
        f"pmse_over_shuffled{suffix}": round(max(twin_control), 2) if twin_control else None,
        f"shuffled_pmse_over_replicate{suffix}": round(min(shuffled_control), 2) if shuffled_control else None,
        f"null_pmse_over_replicate{suffix}": round(max(beside["null"]), 2) if beside["null"] else None,
        f"clustered_pmse_over_replicate{suffix}": (round(max(beside["clustered"]), 2)
                                                   if beside["clustered"] else None),
        f"discriminators_failed{suffix}": failed["twin"],
        f"controls_hold{suffix}": bool(shuffled_control and min(shuffled_control) > 3.0
                                       and failed["replicate"] == 0 and failed["shuffled"] == 0),
        "_detail": "the discriminator rests most on " + "; ".join(leaning)
        + "; discriminators that could not be fitted on today's twin, the replicate, the shuffle: "
        + ", ".join(str(failed[side]) for side in ("twin", "replicate", "shuffled")),
    }


def kpi_06(runs: "list[TableRun]", suffix: str = "") -> "dict[str, object]":
    """K-BC-06, several rows per subject (ST2): the ICC, the fixed effects, rows per subject."""
    st2 = [r for r in runs if r.table == "ST2"]
    if not st2:
        return {}

    def icc_gap(side: str) -> float:
        return max(_median([abs(s.panel.estimates.get("ST2/mixed:icc", Estimate("", "", -9.0, None, 0)).value
                                - r.yard.real.estimates["ST2/mixed:icc"].value) for s in r.sides[side]])
                   for r in st2)

    def outside(side: str) -> int:
        return int(max(_median([sum(1 for c in s.compared if c.key.startswith("ST2/mixed:")
                                    and c.key != "ST2/mixed:icc" and not c.inside) for s in r.sides[side]])
                       for r in st2))

    def held(panel: Panel, key: str) -> float:
        got = panel.estimates.get(key)
        return 0.0 if got is None else got.value

    tvd = max(_median([0.5 * sum(abs(held(s.panel, f"ST2/rows:{k}") - held(r.yard.real, f"ST2/rows:{k}"))
                                 for k in range(1, 9)) for s in r.sides["twin"]]) for r in st2)
    gaps = {side: icc_gap(side) for side in ("twin", "replicate", "shuffled")}
    # A fixed effect is outside its yardstick for a fresh sample too (a
    # perfect twin had two of five outside, median over seeds, at 20,000
    # rows): the twin's count is read against the replicate's.
    twin_out, rep_out = outside("twin"), outside("replicate")
    return {
        f"icc_gap{suffix}": round(gaps["twin"], 3),
        f"icc_gap_over_shuffled{suffix}": round(gaps["twin"] - gaps["shuffled"], 3),
        f"fixed_effects_outside{suffix}": twin_out,
        f"replicate_fixed_effects_outside{suffix}": rep_out,
        f"fixed_effects_outside_over_replicate{suffix}": twin_out - rep_out,
        f"rows_per_subject_tvd{suffix}": round(tvd, 3),
        f"replicate_icc_gap{suffix}": round(gaps["replicate"], 3),
        f"shuffled_icc_gap{suffix}": round(gaps["shuffled"], 3),
        f"controls_hold{suffix}": bool(gaps["replicate"] <= 0.05 and gaps["shuffled"] > 0.05),
    }


# A fresh sample of the same size is inside its yardstick about 77 % of
# the time (S2's simulation, 200,000 draws, four splits). The replicate's
# control holds unless its share falls three binomial standard deviations
# below that, and never below 30 %.
FRESH_INSIDE = 0.77


def replicate_holds(share: float, n: int) -> bool:
    """Whether the replicate's share inside is what a fresh sample of n estimates gives."""
    if n <= 0 or share != share:
        return False
    return share >= max(0.3, FRESH_INSIDE - 3.0 * math.sqrt(FRESH_INSIDE * (1 - FRESH_INSIDE) / n))


def _gap_kpi(runs: "list[TableRun]", pick: "Callable[[Compared], bool]", fail_at: float,
             suffix: str) -> "dict[str, object]":
    gap, worst, supported = gap_points(runs, pick)
    shuf_gap, _w, _s = gap_points(runs, pick, "shuffled")
    rep = shares(runs, "replicate", pick)
    return {
        f"points_below_replicate{suffix}": gap,
        f"worst_seed_points_below_replicate{suffix}": worst,
        f"points_below_shuffled{suffix}": round(gap - shuf_gap, 1),
        f"supported_estimates{suffix}": supported,
        f"replicate_share{suffix}": round(_median(rep), 3) if rep else None,
        f"shuffled_points_below_replicate{suffix}": shuf_gap,
        f"controls_hold{suffix}": bool(rep and replicate_holds(_median(rep), supported) and shuf_gap > fail_at),
    }


def kpi_07(runs: "list[TableRun]", suffix: str = "") -> "dict[str, object]":
    """K-BC-07, time to event (F6)."""
    return _gap_kpi(runs, lambda c: c.family == "F6" and _not_null(c), 25.0, suffix)


def kpi_08(runs: "list[TableRun]", suffix: str = "") -> "dict[str, object]":
    """K-BC-08, missing data: who is missing, the models of missing cells, dropout, the date pattern (tag 'missing')."""
    return _gap_kpi(runs, lambda c: "missing" in c.tags and _not_null(c), 25.0, suffix)


def kpi_09(runs: "list[TableRun]", suffix: str = "") -> "dict[str, object]":
    """K-BC-09, the seeded curves on their fixed grids."""
    return _gap_kpi(runs, lambda c: "curve" in c.tags, 20.0, suffix)


def fragile(run: TableRun) -> "set[str]":
    """The robust analyses that stop on at least one replicate draw of the run: no twin is charged for them."""
    return {n for n in run.yard.robust
            if any(s.panel.status.get(n, "missing") != "ok" for s in run.sides["replicate"])}


def kpi_10(runs: "list[TableRun]", suffix: str = "") -> "dict[str, object]":
    """K-BC-10, runs unchanged: robust analyses that stop on the table and not on the real one.

    A twin or shuffle is charged only with analyses that run on every
    replicate draw of the same table run: one a fresh sample stops on too
    is the analysis's fragility, not the twin's, and is named beside. The
    replicate's own count stays whole, as its control.
    """
    weak = {(r.table, r.seed): fragile(r) for r in runs}

    def count(side: str) -> int:
        per = []
        k_max = max((len(r.sides[side]) for r in runs), default=0)
        for k in range(k_max):
            per += [sum(len([n for n in r.sides[side][k].stops
                             if side == "replicate" or n not in weak[(r.table, r.seed)]])
                        for r in runs if k < len(r.sides[side]))]
        return int(_median(per)) if per else 0

    named = sorted({f"{n} ({r.sides['twin'][0].panel.status.get(n)})" for r in runs if r.sides["twin"]
                    for n in r.sides["twin"][0].stops if n not in weak[(r.table, r.seed)]})
    counts = {side: count(side) for side in ("twin", "replicate", "shuffled")}
    return {
        f"analyses_stopping{suffix}": counts["twin"],
        f"replicate_stopping{suffix}": counts["replicate"],
        f"shuffled_stopping{suffix}": counts["shuffled"],
        f"robust_analyses{suffix}": sum(len(r.yard.robust) for r in runs),
        f"fragile_analyses{suffix}": sum(len(v) for v in weak.values()),
        f"controls_hold{suffix}": bool(counts["replicate"] == 0 and counts["shuffled"] >= 1),
        "_detail": "stopping on today's twin: " + ("; ".join(named) or "none") + "; stopping on a replicate draw: "
        + ("; ".join(f"{t}-{d} {n}" for (t, d), names in sorted(weak.items()) for n in sorted(names)) or "none"),
    }


def kpi_11(runs: "list[TableRun]") -> "dict[str, object]":
    """K-BC-11, the honest report: families the twin's report names, and overclaims (none can be: no line exists)."""
    named: "set[str]" = set()
    carried: "set[str]" = set()
    block = False
    for r in runs:
        block = block or bool(r.report.get("block"))
        named |= set(r.report.get("named", []))  # type: ignore[arg-type]
        carried |= set(r.report.get("carried", []))  # type: ignore[arg-type]
    return {"families_unnamed": len(REPORT_FAMILIES) - len(named), "overclaims": 0 if not carried else len(carried),
            "report_block": block}


# K-BC-12's controls: the replicate's stable-and-inside share is at least
# this, and the shuffled twin and the thin replicate each stand more than
# STABLE_GAP points under it.
STABLE_REPLICATE = 0.5
STABLE_GAP = 25.0


def kpi_12(runs: "list[TableRun]", suffix: str = "") -> "dict[str, object]":
    """K-BC-12, twin-seed stability that is also fidelity.

    Per supported joint estimate, a side scores it where its values over
    the twin seeds spread no more than the yardstick AND lie inside the
    yardstick on a majority of the seeds. Stability alone is not fidelity
    -- today's twin and a column-wise shuffle are each stable at the
    wrong answer (0.857 and 0.858 of estimates at 20,000 rows, against
    the replicate's 0.897) -- so both are asked. The negative controls are
    the shuffled twin (stable, not inside) and the thin replicate (inside
    no more steadily than its own noise allows).
    """
    def share(side: str) -> float:
        hits = total = 0
        for r in runs:
            seeds = r.sides[side]
            if len(seeds) < 2:
                continue
            for key, h in r.yard.h.items():
                real = r.yard.real.estimates[key]
                if key.startswith("ST5/") or "margin" in real.tags:
                    continue
                total += 1
                values = [s.panel.estimates[key].value for s in seeds if key in s.panel.estimates]
                inside = sum(1 for v in values if abs(v - real.value) <= h)
                if len(values) >= 2 and statistics.stdev(values) <= h and inside * 2 > len(seeds):
                    hits += 1
        return hits / total if total else math.nan

    values = {side: share(side) for side in ("twin", "replicate", "shuffled", "thin")}
    under = {side: 100.0 * (values["replicate"] - values[side]) for side in values}
    return {
        f"stable_share{suffix}": round(values["twin"], 3),
        f"points_below_replicate{suffix}": round(under["twin"], 1),
        f"points_below_shuffled{suffix}": round(under["twin"] - under["shuffled"], 1),
        f"replicate_stable_share{suffix}": round(values["replicate"], 3),
        f"shuffled_stable_share{suffix}": round(values["shuffled"], 3),
        f"thin_stable_share{suffix}": round(values["thin"], 3),
        f"controls_hold{suffix}": bool(values["replicate"] >= STABLE_REPLICATE and under["shuffled"] > STABLE_GAP
                                       and under["thin"] > STABLE_GAP),
    }


KPIS = {"K-BC-01": kpi_01, "K-BC-02": kpi_02, "K-BC-03": kpi_03, "K-BC-04": kpi_04,
        "K-BC-05": kpi_05, "K-BC-06": kpi_06, "K-BC-07": kpi_07, "K-BC-08": kpi_08,
        "K-BC-09": kpi_09, "K-BC-10": kpi_10}


def finite(value: object) -> object:
    """A value the ledger can hold: NaN and infinities become None, at any depth."""
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {k: finite(v) for k, v in value.items()}
    return value


def kpi_values(runs: "list[TableRun]", suffix: str = "") -> "dict[str, dict[str, object]]":
    """Every KPI's value from a set of table runs (``suffix`` names the tier's keys)."""
    out = {kpi: function(runs, suffix) for kpi, function in KPIS.items()}
    return {k: v for k, v in out.items() if v}


def controls_failing(values: "dict[str, dict[str, object]]") -> "list[str]":
    """The KPIs whose controls do not hold: the run is void for them."""
    return sorted(k for k, v in values.items()
                  for key, hold in v.items() if key.startswith(("controls_hold", "null_controls_hold"))
                  and hold is False)


_FAST: "dict[str, object]" = {}


def fast_run(folder: pathlib.Path) -> "dict[str, object]":
    """The suite's part: ST1 and ST2 at 5,000 rows, one seed, the controls and today's twin, timed.

    Run once per process and kept (a few megabytes of panels, no table):
    the KPI tests (`tests/test_kpi_ledger.py`) and the controls' own tests
    (`tests/test_analyst_battery.py`) read the same run, so a shard holding
    both runs it once. ``folder`` is the first caller's.
    """
    if not _FAST:
        started = time.perf_counter()
        runs = run_tables("fast", folder)
        values = kpi_values(runs)
        values["K-BC-11"] = kpi_11(runs)
        _FAST.update({"runs": runs, "values": values, "seconds": time.perf_counter() - started})
    return dict(_FAST)


def iterate(runs: "list[TableRun]") -> "Iterator[Compared]":
    """Every comparison of today's twin, for a reader of the detail."""
    for r in runs:
        for s in r.sides["twin"]:
            yield from s.compared
