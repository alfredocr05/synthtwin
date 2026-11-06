"""K-S6-14, the moment layer's yield under the owner's rule B (contract 4.6d.0, plan P4-D455; lane MPp).

On lane E0b's battery tables ST1 to ST6 at 20,000 rows (seed 1), each
described with the chain behind its switch (the ledger's fixed test key),
ST2 with its subject column `sid` declared as the person column, as the
product reads it (one row a visit: the chain, and so every moment, is off
there), and on one invented table of this driver's own, `prices`, which
carries the shapes rule B's prices and limits turn on: a lab with 3
blanks, two labs blank alone on 600 rows each and together on 5, a
collinear pair of pressures (r near 0.95), a column computed from them
(their weighted mean), a copy of one pressure (a tie: r capped at
0.999999), a rare outcome (about 1 row in 200) and a ward:

- PUBLISHED by kind (`published_columns_number`, `_binary`,
  `published_correlations`, `published_within_number`, `_binary`, and of
  those `published_within_on_l2`, read on a grouping's `L2` bands after
  its `L1` bands were refused) and REFUSED by reason (`refused`, a map;
  `l1_refused_l2_published`, a map, the `L1` reasons the `L2` reading
  answered), summed over the tables;
- `direct_small`: published moments whose direct counts, recomputed from
  the rows (a band's readings and its rows without one at the level
  published, a binary's two levels, a pair's four presence cells less a
  column's own unread count beside a complete column), lie in 1 to 10:
  target 0;
- `reference_mismatches`: tables on which the product's object differs
  from the reference's (`tools/reference/moment_rule_b.py`), computed
  apart on the same coded rows: target 0;
- `descriptions_loaded`: tables whose description, written with its
  chain and moments, `contract.load_profile(..., chain=True)` reads back
  (target: every table; the verify's item 1 on repair 1);
- ROUNDING AGAINST THE NORMAL-MODEL SAMPLING ERROR: for every published
  correlation (the tanh of its grid point of Fisher's z), mean, standard
  deviation (a column's, a pair's and a band's) and share, the rounding
  error (published less the unrounded value) over the sampling standard
  error at its count, as the normal model states it (a mean's sd /
  sqrt(n), a spread's sd / sqrt(2 (n - 1)), r's (1 - r ** 2) / sqrt(n),
  a share's sqrt(p (1 - p) / n)):
  `rounding_over_normal_model_sampling_max` and `_median`, and the same
  over the moments of a whole column (the table floor's 20,000 rows),
  `rounding_over_normal_model_sampling_at_the_floor_max`;
  `moments_rounded` counts every published moment, those whose standard
  error is 0 named in `rounding_ratio_undefined` (a share of 0 or 1, a
  constant band's spread, a tie's correlation) and a tie's correlation
  also in `correlations_capped_at_a_tie` (r capped at 0.999999, its
  error not 0, its normal-model error 0); over the correlations alone,
  `correlation_rounding_over_sampling_max` (at most 0.1 at every |r| up
  to 0.999, the collinear pair and the computed column included);
- THE SPREADS AGAINST THEIR KURTOSIS (LANE MPp RULINGS 5 (4)): a spread's
  standard error beside the normal model's, sd * sqrt((kurtosis - 1) /
  (4 (n - 1))), the kurtosis the readings' own: its largest ratio
  `spread_rounding_over_kurtosis_sampling_max`, the spreads over half of
  it `spread_rounding_over_half_a_kurtosis_standard_error` (the first
  named in `spreads_over_half_a_kurtosis_standard_error`) and those of
  a kurtosis of 1 (two values, equally held: no first-order error) in
  `spread_kurtosis_undefined`;
- SLOPES: the simple slope of each number on the other, for every
  published pair with |r| of at least 0.5, from the published numbers (r
  times the pair's spread of one over the pair's spread of the other,
  the columns' own where the pair holds every reading) against the
  least-squares slope on the rows holding both, over its standard error
  sqrt((1 - r ** 2) / (n - 2)) * sd_y / sd_x:
  `simple_slope_rounding_over_sampling_max` (bound 0.25, LANE MPp
  RULINGS 6 (2)) over `simple_slopes_measured`; and on `prices`, the two
  coefficients of a lab regressed on the collinear pair, computed from
  the rounded moments against the exact ones, over their standard
  errors, `collinear_coefficients_rounding_over_sampling_max`;
- A COLLINEAR COEFFICIENT ON THE PRODUCT (LANE MPp RULINGS 7 (4) (a), lane
  MPp verify 2's Probe C protocol): two predictors of correlation r (0.9,
  0.95, 0.99, 0.999) and an outcome at R^2 0.3, coefficient settings
  (0.3, 0.3) and (0.5, -0.3), each column written as integer codes 0 to
  255 (round(128 + s * u / 2.2), s drawn in 40 to 70), with a grouping of
  four bands, through `chain_moments.released` at f = 11, 40 draws for
  each r and setting, at 20,000, 200,001 and 2,000,001 rows: the two
  coefficients of y ~ x1 + x2 from the published numbers (the three r and
  the three spreads, each in the unit of its count) against least squares
  on the codes, over the coefficient's own standard error
  sqrt((1 - R^2) / ((n - 3)(1 - r12 ** 2))) * sd_y / sd_x, the larger of
  the two a draw; the 95th percentile (the 38th of 40) over the worse
  setting: `collinear_coefficient_p95_r_0_9`, `_0_95`, `_0_99` and
  `_0_999` at 20,000 rows (bounds 0.05, 0.06, 0.10 and 0.33), the same
  keys `_past_the_floor` the worse of 200,001 and 2,000,001 rows (bounds
  0.02, 0.03, 0.04 and 0.11, about twice their readings), and every
  reading in `collinear_coefficient_probe`;
- `moments_bytes`: the moment objects' size, summed; `prices`: that
  table's own counts (its few-blank lab's correlations, its neither pair,
  its collinear pair's r, its rare outcome's `within` at each level).

THE TWIN is not measured here: the generator reads no moment yet (lane
MPg's polish, G16.3). `K-BC-01` and the coefficients' agreement on a twin
calibrated to the moments by lane MPp's reference script, beside the floor
without them, are cited in `twin_cited` from that run.

    PYTHONPATH=src:tests python tools/measurements/kpi_moment_rule_b.py --kpi

About eighteen minutes, eight of them the collinear probe at 2,000,001 rows;
one process of a few hundred megabytes.
"""

import importlib.util
import json
import math
import pathlib
import random
import sys
import tempfile
import time
from fractions import Fraction

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import analyst_tables  # noqa: E402
import moment_rule_b_enumeration as enumeration  # noqa: E402

from synthtwin import canonical, chain, chain_moments, contract, errors, profile, reading, taxonomy  # noqa: E402

FLOOR = 11
ROWS = 20000
SEED = 1
KEY = bytes(range(32))
PERSON_COLUMNS = {"ST2": ["sid"]}
PRICES = "prices"
COLLINEAR_SIZES = (ROWS, 200001, 2000001)
COLLINEAR_RS = (0.9, 0.95, 0.99, 0.999)
COLLINEAR_SETTINGS = ((0.3, 0.3), (0.5, -0.3))
COLLINEAR_DRAWS = 40
COLLINEAR_R_SQUARED = 0.3
TWIN_CITED = (
    "lane MPp's harness (planning notes, wave6/MPp), a twin moved onto the published moments by its reference script: "
    "K-BC-01 on the analyst battery at 20,000 rows, table seed 1, 970 estimates, the walk's twin 0.436 (k0, five twin "
    "seeds), 0.437 and 0.426 (k1, k2, one), the moved twin 0.539, 0.519 and 0.520, a fresh sample 0.746, the shuffled "
    "twin 0.384; sign flips of the coefficients significant on the real table 17.4 %, moved 9.6 %, a fresh sample 2.5 %; "
    "lane A0b's 50-column table, 273 estimates at 20,000 rows, twin seed 1 at these units: the walk 127, moved 169"
)


def _reference():
    spec = importlib.util.spec_from_file_location("moment_rule_b", ROOT / "tools" / "reference" / "moment_rule_b.py")
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def _stats(values: "list[float]") -> "tuple[int, float, float]":
    n = len(values)
    mean = sum(values) / n
    sd = math.sqrt(sum((v - mean) ** 2 for v in values) / (n - 1)) if n > 1 else 0.0
    return n, mean, sd


def _ratio(error: float, se: float) -> "float | None":
    return error / se if se > 0 else None


def _kurtosis_se(held: "list[float]") -> "float | None":
    """A spread's standard error from its readings' own kurtosis, sd * sqrt((kurtosis - 1) / (4 (n - 1))); None at a kurtosis of 1."""
    n, mean, sd = _stats(held)
    second = sum((v - mean) ** 2 for v in held) / n
    if second <= 0:
        return None
    fourth = sum((v - mean) ** 4 for v in held) / n
    excess = fourth / (second * second) - 1
    if excess <= 1e-12:
        return None
    return sd * math.sqrt(excess / (4 * (n - 1)))


def prices_text(rows: int, seed: int) -> str:
    """The invented table `prices`: the shapes rule B's prices and limits turn on (this driver's own values)."""
    draw = random.Random(seed)
    lines = ["age,pressure_high,pressure_low,pressure_mean,pressure_copy,lab_few,lab_a,lab_b,lab_c,outcome,ward"]
    for place in range(rows):
        age = draw.randint(18, 89)
        high = 105 + 0.4 * age + draw.gauss(0, 14)
        low = 0.6 * high + draw.gauss(0, 2.9)
        mean = (high + 2 * low) / 3
        few = "" if place in (17, 4021, 13377) else f"{round(5 + 0.02 * age + draw.gauss(0, 1), 2)}"
        lab_a = f"{round(40 + 0.1 * age + draw.gauss(0, 6), 1)}"
        lab_b = f"{round(1.2 + 0.004 * age + draw.gauss(0, 0.3), 2)}"
        if 100 <= place < 700 or 1300 <= place < 1305:
            lab_a = ""
        if 700 <= place < 1305:
            lab_b = ""
        lab_c = f"{round(2 + 0.03 * high - 0.02 * low + draw.gauss(0, 0.5), 2)}"
        outcome = "1" if draw.random() < 0.001 + 0.0001 * (age - 18) else "0"
        ward = draw.choice(["east", "north", "south", "west"])
        lines += [f"{age},{high:.1f},{low:.1f},{mean:.1f},{high:.1f},{few},{lab_a},{lab_b},{lab_c},{outcome},{ward}"]
    return "\n".join(lines) + "\n"


def _collinear(moments: "dict[str, object]", values: "dict[str, tuple[str, list[object]]]") -> "float | None":
    """The two coefficients of lab_c on the collinear pressures, from the rounded moments against the exact codes, over their SEs."""
    names = ["pressure_high", "pressure_low", "lab_c"]
    entries = {entry["column"]: entry for entry in moments["columns"]}  # type: ignore[index, union-attr, attr-defined]
    numbers = [entry["column"] for entry in moments["columns"] if entry["kind"] == "number"]  # type: ignore[index, union-attr]
    if any(name not in numbers for name in names):
        return None

    def published_r(one: str, two: str) -> "float | None":
        at, other = sorted((numbers.index(one), numbers.index(two)), reverse=True)
        pair = moments["correlations"][at][other]  # type: ignore[index]
        if pair is None:
            return None
        return pair[0] / chain_moments.SCALE_CORRELATION

    rows = [(values[names[0]][1][r], values[names[1]][1][r], values[names[2]][1][r]) for r in range(len(values[names[0]][1]))]
    rows = [row for row in rows if None not in row]
    n = len(rows)
    sd = [_stats([float(row[k]) for row in rows])[2] for k in range(3)]
    mean = [sum(float(row[k]) for row in rows) / n for k in range(3)]

    def exact_r(i: int, j: int) -> float:
        cross = sum((float(row[i]) - mean[i]) * (float(row[j]) - mean[j]) for row in rows)
        return cross / ((n - 1) * sd[i] * sd[j])

    r12, r1y, r2y = exact_r(0, 1), exact_r(0, 2), exact_r(1, 2)
    p12, p1y, p2y = published_r(names[0], names[1]), published_r(names[0], names[2]), published_r(names[1], names[2])
    if None in (p12, p1y, p2y):
        return None
    psd = [entries[name]["sd"] / chain_moments.unit(chain_moments.SCALE_COLUMN_SPREAD, entries[name]["n"]) for name in names]

    def coefficients(a: float, b: float, c: float, s: "list[float]") -> "tuple[float, float]":
        det = 1 - a * a
        return (b - a * c) / det * s[2] / s[0], (c - a * b) / det * s[2] / s[1]

    exact = coefficients(r12, r1y, r2y, sd)
    rounded = coefficients(p12, p1y, p2y, psd)  # type: ignore[arg-type]
    r2 = (r1y * r1y + r2y * r2y - 2 * r1y * r2y * r12) / (1 - r12 * r12)
    worst = 0.0
    for k in range(2):
        se = math.sqrt((1 - r2) / ((n - 3) * (1 - r12 * r12))) * sd[2] / sd[k]
        worst = max(worst, abs(rounded[k] - exact[k]) / se)
    return worst


def collinear_draw(n: int, r: float, setting: int, draw: int) -> float:
    """One draw of the collinear probe: the larger of the two coefficients' rounding over its own standard error.

    Seeded by (n, r, setting, draw) alone, so a draw reads the same bytes in
    every run; the codes are written as Probe C writes them and described
    by the product's own `released`; the exact coefficients come from the
    codes' whole-number sums, in fractions.
    """
    import numpy as np

    first, second = COLLINEAR_SETTINGS[setting]
    draws = np.random.default_rng([20261104, n, int(round(r * 10000)), setting, draw, 0])
    spreads = [float(value) for value in draws.uniform(40, 70, 3)]
    u1 = draws.standard_normal(n)
    u2 = r * u1 + math.sqrt(1 - r * r) * draws.standard_normal(n)
    variance = first * first + second * second + 2 * first * second * r
    noise = math.sqrt(variance * (1 - COLLINEAR_R_SQUARED) / COLLINEAR_R_SQUARED) * draws.standard_normal(n)
    v = (first * u1 + second * u2 + noise) / math.sqrt(variance / COLLINEAR_R_SQUARED)
    codes = [np.clip(np.rint(128 + spread * u / 2.2), 0, 255).astype(np.uint8) for spread, u in zip(spreads, (u1, u2, v))]
    present = bytearray(b"\x01" * n)
    columns = [chain_moments.Released(name, chain_moments.KIND_NUMBER, code.tobytes(), present) for name, code in zip(("x1", "x2", "y"), codes)]
    bands = (np.arange(n) % 4).astype(np.uint8)
    totals = tuple(int(count) for count in np.bincount(bands, minlength=4))
    moments, _counts = chain_moments.released(columns, [chain_moments.Grouping("g", bands.tobytes(), totals, frozenset(), (0, 1, 2, 3))], FLOOR)
    if moments is None:
        raise RuntimeError("the collinear probe's table published no moment")
    scales = moments["scales"]
    own = {entry["column"]: entry for entry in moments["columns"]}  # type: ignore[union-attr, index]
    triangle = moments["correlations"]
    pairs = {"12": triangle[1][0], "1y": triangle[2][0], "2y": triangle[2][1]}  # type: ignore[index]
    if any(pair is None or len(pair) != 2 or pair[1] != n for pair in pairs.values()):
        raise RuntimeError(f"the collinear probe's pairs are not [r, n] at {n} rows: {pairs}")
    shown = {key: Fraction(pair[0], scales["correlation"]) for key, pair in pairs.items()}  # type: ignore[index]
    sd = {name: Fraction(own[name]["sd"], chain_moments.unit(scales["column_sd"], own[name]["n"])) for name in ("x1", "x2", "y")}  # type: ignore[index]
    held = [code.astype(np.int64) for code in codes]
    total = {"1": int(held[0].sum()), "2": int(held[1].sum()), "y": int(held[2].sum())}
    square = {"11": (0, 0), "22": (1, 1), "yy": (2, 2), "12": (0, 1), "1y": (0, 2), "2y": (1, 2)}
    centred = {key: n * int((held[a] * held[b]).sum()) - total[key[0]] * total[key[1]] for key, (a, b) in square.items()}
    det = centred["11"] * centred["22"] - centred["12"] * centred["12"]
    exact = (
        Fraction(centred["1y"] * centred["22"] - centred["2y"] * centred["12"], det),
        Fraction(centred["2y"] * centred["11"] - centred["1y"] * centred["12"], det),
    )
    rest = 1 - shown["12"] * shown["12"]
    rounded = (
        (shown["1y"] - shown["12"] * shown["2y"]) / rest * sd["y"] / sd["x1"],
        (shown["2y"] - shown["12"] * shown["1y"]) / rest * sd["y"] / sd["x2"],
    )
    r_squared = float((exact[0] * centred["1y"] + exact[1] * centred["2y"]) / centred["yy"])
    r12 = centred["12"] / math.sqrt(centred["11"] * centred["22"])
    base = math.sqrt((1 - r_squared) / ((n - 3) * (1 - r12 * r12)))
    return max(abs(float(rounded[k] - exact[k])) / (base * math.sqrt(centred["yy"] / centred[("11", "22")[k]])) for k in range(2))


def collinear_probe() -> "dict[str, object]":
    """The collinear probe's keys: the 95th percentile at each r, the worse setting, at 20,000 rows and past the floor."""
    out: "dict[str, object]" = {}
    readings: "dict[str, dict[str, list[float]]]" = {}
    for n in COLLINEAR_SIZES:
        readings[f"{n}"] = {}
        for r in COLLINEAR_RS:
            worst = largest = 0.0
            for setting in range(len(COLLINEAR_SETTINGS)):
                ratios = sorted(collinear_draw(n, r, setting, draw) for draw in range(COLLINEAR_DRAWS))
                worst = max(worst, ratios[int(0.95 * len(ratios)) - 1])
                largest = max(largest, ratios[-1])
            readings[f"{n}"][f"{r}"] = [round(worst, 4), round(largest, 4)]
            key = "collinear_coefficient_p95_r_" + f"{r}".replace(".", "_")
            if n == ROWS:
                out[key] = round(worst, 4)
            else:
                out[key + "_past_the_floor"] = max(float(out.get(key + "_past_the_floor", 0.0)), round(worst, 4))  # type: ignore[arg-type]
    out["collinear_coefficient_probe"] = readings
    return out


def measure_table(name: str, folder: pathlib.Path, reference: object) -> "dict[str, object]":
    persons = PERSON_COLUMNS.get(name, [])
    # A subject column is declared as the product declares it: held as an identifier and named as the person column.
    settings = taxonomy.Settings(small_cell_floor=FLOOR, person_columns=tuple(persons))
    path = folder / f"{name}.csv"
    text = prices_text(ROWS, SEED) if name == PRICES else analyst_tables.text(name, ROWS, SEED)
    path.write_text(text, encoding="utf-8", newline="\n")
    table = reading.read_table(str(path), small_cell_floor=FLOOR)
    document = profile.build_document(table, settings, list(persons), [], [])
    chained = chain.describe(table, document, settings, chain.ChainSwitch(f"{name}-{SEED}", KEY))
    statistical = chained.statistical
    out: "dict[str, object]" = {"table": name, "counts": {k: v for k, v in chained.counts.items() if k.startswith("moments ")}}
    # The description as the profile command writes it, read back with the chain's switch on.
    written = dict(document)
    written["relationships"] = dict(written["relationships"], statistical=statistical)  # type: ignore[arg-type]
    described = folder / f"{name}-profile.json"
    described.write_text(profile.serialize(written), encoding="utf-8", newline="\n")
    try:
        contract.load_profile(str(described), chain=True)
        out["loaded"] = ""
    except errors.ProfileError as refusal:
        out["loaded"] = f"{refusal}"[:300]
    described.unlink()
    if statistical is None or statistical["moments"] is None:
        out["moments"] = None
        path.unlink()
        return out
    moments = statistical["moments"]
    out["bytes"] = len(canonical.serialize(moments).encode("utf-8"))
    columns, groupings = enumeration.coded(table, document, statistical, FLOOR)
    expected, _refused = reference.describe(columns, groupings, FLOOR)  # type: ignore[attr-defined]
    out["agrees"] = expected == moments
    values = {name_: (kind, vals) for name_, kind, vals in columns}
    bands: "dict[tuple[str, int], tuple[list[int], list[int]]]" = {}
    for name_, l1, totals, _small, coarsest in groupings:
        bands[(name_, 1)] = (l1, totals)
        coarse_totals = [0] * (max(coarsest) + 1)
        for band, total in enumerate(totals):
            coarse_totals[coarsest[band]] += total
        bands[(name_, 2)] = ([coarsest[band] for band in l1], coarse_totals)
    scales = moments["scales"]
    ratios: "list[float]" = []
    floor_ratios: "list[float]" = []
    kurtosis: "list[float]" = []
    over_half: "list[str]" = []
    undefined: "dict[str, int]" = {}
    capped = 0
    direct_small = 0
    unit = chain_moments.unit

    def keep(found: "float | None", why: str, at_the_floor: bool = False) -> None:
        nonlocal ratios, floor_ratios
        if found is None:
            undefined[why] = undefined.get(why, 0) + 1
            return
        ratios += [found]
        if at_the_floor:
            floor_ratios += [found]

    def spread(published: float, held: "list[float]", where: str, at_the_floor: bool = False) -> None:
        nonlocal kurtosis, over_half
        n, _mean, sd = _stats(held)
        error = abs(published - sd)
        keep(_ratio(error, sd / math.sqrt(2 * (n - 1))), "a spread of 0", at_the_floor)
        se = _kurtosis_se(held)
        if se is None:
            undefined["a spread of a kurtosis of 1"] = undefined.get("a spread of a kurtosis of 1", 0) + 1
            return
        kurtosis += [error / se]
        if error / se > 0.5:
            over_half += [f"{name} {where}: {round(error / se, 3)}"]

    for entry in moments["columns"]:
        kind, vals = values[entry["column"]]
        held = [float(v) for v in vals if v is not None]
        n, mean, sd = _stats(held)
        if kind == "number":
            keep(_ratio(abs(entry["mean"] / unit(scales["mean"], n) - mean), sd / math.sqrt(n)), "a mean of a constant column", True)
            spread(entry["sd"] / unit(scales["column_sd"], n), held, entry["column"], True)
        else:
            keep(_ratio(abs(entry["share"] / unit(scales["share"], n) - mean), math.sqrt(mean * (1 - mean) / n)), "a share of 0 or 1", True)
    correlations: "dict[tuple[str, str], float]" = {}
    correlation_ratios: "list[float]" = []
    slope_ratios: "list[float]" = []
    own = {entry["column"]: entry for entry in moments["columns"]}
    numbers = [entry["column"] for entry in moments["columns"] if entry["kind"] == "number"]
    for at, line in enumerate(moments["correlations"]):
        for other, pair in enumerate(line):
            if pair is None:
                continue
            first, second = values[numbers[at]][1], values[numbers[other]][1]
            both = [(float(a), float(b)) for a, b in zip(first, second) if a is not None and b is not None]
            n = len(both)
            nx, ny = len([a for a in first if a is not None]), len([b for b in second if b is not None])
            direct = [n, len(first) - nx - ny + n] + ([] if nx == len(first) else [nx - n]) + ([] if ny == len(second) else [ny - n])
            if any(0 < c < FLOOR for c in direct):
                direct_small += 1
            ma = sum(a for a, _b in both) / n
            mb = sum(b for _a, b in both) / n
            cross = sum((a - ma) * (b - mb) for a, b in both)
            va = sum((a - ma) ** 2 for a, _b in both)
            vb = sum((b - mb) ** 2 for _a, b in both)
            r = max(-1.0, min(1.0, cross / math.sqrt(va * vb)))
            correlations[(numbers[at], numbers[other])] = r
            printed = pair[0] / scales["correlation"]
            found = _ratio(abs(printed - r), (1 - r * r) / math.sqrt(n))
            if found is None:
                capped += 1 if printed != r else 0
                undefined["a correlation of a tie"] = undefined.get("a correlation of a tie", 0) + 1
            else:
                correlation_ratios += [found]
                ratios += [found]
                if n >= ROWS:
                    floor_ratios += [found]
            sd_a, sd_b = math.sqrt(va / (n - 1)), math.sqrt(vb / (n - 1))
            if len(pair) == 3:
                shown = [pair[2][k] / unit(scales["column_sd"], n) for k in range(2)]
                spread(shown[0], [a for a, _b in both], f"{numbers[at]} beside {numbers[other]}")
                spread(shown[1], [b for _a, b in both], f"{numbers[other]} beside {numbers[at]}")
            else:
                shown = [own[numbers[at]]["sd"] / unit(scales["column_sd"], n), own[numbers[other]]["sd"] / unit(scales["column_sd"], n)]
            if abs(r) < 0.5:
                continue
            for x, y in ((0, 1), (1, 0)):
                exact = r * (sd_a, sd_b)[y] / (sd_a, sd_b)[x]
                derived = printed * shown[y] / shown[x]
                se = math.sqrt(max(0.0, 1 - r * r) / (n - 2)) * (sd_a, sd_b)[y] / (sd_a, sd_b)[x]
                slope = _ratio(abs(derived - exact), se)
                if slope is None:
                    undefined["a slope of a tie"] = undefined.get("a slope of a tie", 0) + 1
                else:
                    slope_ratios += [slope]
    for entry in moments["within"]:
        kind, vals = values[entry["column"]]
        l1, totals = bands[(entry["by"], entry.get("level", 1))]
        for band, group in enumerate(entry["groups"]):
            held = [float(v) for v, g in zip(vals, l1) if g == band and v is not None]
            direct = [len(held), totals[band] - len(held)]
            if kind == "binary":
                direct += [int(sum(held)), len(held) - int(sum(held))]
            if any(0 < c < FLOOR for c in direct):
                direct_small += 1
            if group[0] == 0:
                continue
            n, mean, sd = _stats(held)
            if kind == "number":
                keep(_ratio(abs(group[1] / unit(scales["mean"], n) - mean), sd / math.sqrt(n)), "a mean of a constant band")
                spread(group[2] / unit(scales["sd"], n), held, f"{entry['column']} within {entry['by']} band {band}")
            else:
                keep(_ratio(abs(group[1] / unit(scales["share"], n) - mean), math.sqrt(mean * (1 - mean) / n)), "a share of 0 or 1")
    if name == PRICES:
        numbers_ = [entry["column"] for entry in moments["columns"] if entry["kind"] == "number"]

        def pair_of(one: str, two: str) -> object:
            if one not in numbers_ or two not in numbers_:
                return "not a moment column"
            at_, other_ = sorted((numbers_.index(one), numbers_.index(two)), reverse=True)
            return moments["correlations"][at_][other_]

        out["prices"] = {
            "lab_few_correlations_published": len([o for o in numbers_ if o != "lab_few" and pair_of("lab_few", o) not in (None, "not a moment column")]),
            "lab_few_within_published": len([e for e in moments["within"] if e["column"] == "lab_few"]),
            "lab_a_lab_b_neither_rows": len([r for r in range(len(values["lab_a"][1])) if values["lab_a"][1][r] is None and values["lab_b"][1][r] is None]),
            "lab_a_lab_b_pair": pair_of("lab_a", "lab_b"),
            "pressure_pair_r": round(correlations.get(("pressure_low", "pressure_high"), correlations.get(("pressure_high", "pressure_low"), 0.0)), 4),
            "pressure_mean_with_high_r": round(correlations.get(("pressure_mean", "pressure_high"), correlations.get(("pressure_high", "pressure_mean"), 0.0)), 4),
            "pressure_copy_with_high_pair": pair_of("pressure_copy", "pressure_high"),
            "outcome_ones": int(sum(v for v in values["outcome"][1] if v is not None)) if "outcome" in values else None,
            "outcome_within_l1": len([e for e in moments["within"] if e["column"] == "outcome" and "level" not in e]),
            "outcome_within_l2": len([e for e in moments["within"] if e["column"] == "outcome" and e.get("level") == 2]),
        }
        out["collinear"] = _collinear(moments, values)
    # Rule (1)'s proportions of a FEW-VALUED column (3 to 8 levels) are not
    # built: such a column only groups (P4-D455's stated limit, owner MPg).
    named = {entry["column"] for entry in moments["columns"]}
    roles = {f"{block['name']}": block.get("role") for block in document["columns"]}  # type: ignore[union-attr, attr-defined, index]
    few = 0
    for entry in statistical["ladder"]:  # type: ignore[attr-defined]
        levels = [band for band in entry["l0"] if band != ["missing"]]
        if entry["column"] not in named and roles.get(entry["column"]) in ("categorical", "binary", "long_tail_labels") and 3 <= len(levels) <= 8:
            few += 1
    out["few_valued"] = few
    out["ratios"] = ratios
    out["correlation_ratios"] = correlation_ratios
    out["floor_ratios"] = floor_ratios
    out["kurtosis"] = kurtosis
    out["over_half"] = over_half
    out["undefined"] = undefined
    out["capped"] = capped
    out["slope_ratios"] = slope_ratios
    out["direct_small"] = direct_small
    path.unlink()
    return out


def measure() -> "dict[str, object]":
    started = time.time()
    reference = _reference()
    value: "dict[str, object]" = {}
    refused: "dict[str, int]" = {}
    ratios: "list[float]" = []
    floor_ratios: "list[float]" = []
    totals = {"published_columns_number": 0, "published_columns_binary": 0, "published_correlations": 0,
              "published_within_number": 0, "published_within_binary": 0, "published_within_on_l2": 0}
    answered: "dict[str, int]" = {}
    prices: "dict[str, object]" = {}
    collinear: "float | None" = None
    keys = {"published column: number": "published_columns_number", "published column: binary": "published_columns_binary",
            "published correlation": "published_correlations", "published within: number": "published_within_number",
            "published within: binary": "published_within_binary"}
    direct_small = mismatches = size = few_valued = capped = loaded = 0
    correlation_ratios: "list[float]" = []
    kurtosis: "list[float]" = []
    over_half: "list[str]" = []
    slope_ratios: "list[float]" = []
    undefined: "dict[str, int]" = {}
    refusals: "list[str]" = []
    with tempfile.TemporaryDirectory() as folder:
        for name in analyst_tables.TABLES + (PRICES,):
            found = measure_table(name, pathlib.Path(folder), reference)
            if found["loaded"]:
                refusals += [f"{name}: {found['loaded']}"]
            else:
                loaded += 1
            counts = found["counts"]
            for key, count in counts.items():  # type: ignore[attr-defined]
                word = key[len("moments "):]
                if word in keys:
                    totals[keys[word]] += count
                elif word.startswith("within on the L2 bands"):
                    totals["published_within_on_l2"] += count
                elif word.startswith("L1 bands refused, L2 published: "):
                    reason = word[len("L1 bands refused, L2 published: "):]
                    answered[reason] = answered.get(reason, 0) + count
                elif word.startswith("refused") or word == "not among the partners":
                    refused[word] = refused.get(word, 0) + count
            if found.get("moments", True) is None:
                continue
            if name == PRICES:
                prices = found["prices"]  # type: ignore[assignment]
                collinear = found["collinear"]  # type: ignore[assignment]
            few_valued += found["few_valued"]  # type: ignore[operator]
            correlation_ratios += found["correlation_ratios"]  # type: ignore[arg-type]
            kurtosis += found["kurtosis"]  # type: ignore[arg-type]
            over_half += found["over_half"]  # type: ignore[arg-type]
            slope_ratios += found["slope_ratios"]  # type: ignore[arg-type]
            capped += found["capped"]  # type: ignore[operator]
            for why, count in found["undefined"].items():  # type: ignore[attr-defined]
                undefined[why] = undefined.get(why, 0) + count
            ratios += found["ratios"]  # type: ignore[arg-type]
            floor_ratios += found["floor_ratios"]  # type: ignore[arg-type]
            direct_small += found["direct_small"]  # type: ignore[operator]
            mismatches += 0 if found["agrees"] else 1
            size += found["bytes"]  # type: ignore[operator]
    ratios.sort()
    value.update(totals)
    value["refused"] = dict(sorted(refused.items()))
    value["l1_refused_l2_published"] = dict(sorted(answered.items()))
    value["prices"] = prices
    value["collinear_coefficients_rounding_over_sampling_max"] = round(collinear, 3) if collinear is not None else None
    value.update(collinear_probe())
    value["direct_small"] = direct_small
    value["reference_mismatches"] = mismatches
    value["tables"] = len(analyst_tables.TABLES) + 1
    value["descriptions_loaded"] = loaded
    value["descriptions_refused"] = refusals
    value["moments_rounded"] = len(ratios) + sum(count for why, count in undefined.items() if "slope" not in why and "kurtosis" not in why)
    value["rounding_ratio_undefined"] = dict(sorted(undefined.items()))
    value["correlations_capped_at_a_tie"] = capped
    value["rounding_over_normal_model_sampling_max"] = round(ratios[-1], 3) if ratios else None
    value["rounding_over_normal_model_sampling_median"] = round(ratios[len(ratios) // 2], 4) if ratios else None
    value["rounding_over_normal_model_sampling_at_the_floor_max"] = round(max(floor_ratios), 3) if floor_ratios else None
    value["rounding_over_half_a_normal_model_standard_error"] = len([r for r in ratios if r > 0.5])
    value["spread_rounding_over_kurtosis_sampling_max"] = round(max(kurtosis), 3) if kurtosis else None
    value["spread_rounding_over_half_a_kurtosis_standard_error"] = len(over_half)
    value["spreads_over_half_a_kurtosis_standard_error"] = over_half[:10]
    value["spread_kurtosis_undefined"] = undefined.get("a spread of a kurtosis of 1", 0)
    value["simple_slope_rounding_over_sampling_max"] = round(max(slope_ratios), 3) if slope_ratios else None
    value["simple_slopes_measured"] = len(slope_ratios)
    value["correlation_rounding_over_sampling_max"] = round(max(correlation_ratios), 4) if correlation_ratios else None
    value["moments_bytes"] = size
    value["few_valued_columns_without_a_share"] = few_valued
    value["twin_cited"] = TWIN_CITED
    value["seconds"] = round(time.time() - started, 1)
    return value


def main() -> int:
    value = measure()
    if "--kpi" in sys.argv:
        print("KPI " + json.dumps({"id": "K-S6-14", "value": value, "detail": "the moment layer's yield under rule B (lane MPp)"}, sort_keys=True))
    else:
        print(json.dumps(value, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
