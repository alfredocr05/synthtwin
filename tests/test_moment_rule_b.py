"""Rule B's moments (contract 4.6d.0, plan P4-D455): what the chain's description publishes between columns, and what it never does.

THE OWNER'S RULE B (2026-11-02; bc-design ruling R13): a moment between
columns is published where it is computed over at least 11 people and
every count it implies directly is 0 or at least 11, rounded to a stated
precision; no proof beyond that. Each test here names the clause it
holds and the mutant that turns it red.

WHAT IS HELD:
- the product's object equals the reference's (tools/reference/
  moment_rule_b.py), computed apart in exact fractions, on the same coded
  rows (mutant: a rounding or a floor check changed in `chain_moments`);
- HIPAA first, the attacks on the rule itself: a share implying 1 to 10
  rows, a band mean over 1 to 10 people, a held, identifier or date
  column, a tail value, a top-coded age, a count one subtraction away,
  the pair's fourth presence cell (rows holding neither column, 1 to
  10), and RULE W1 read from a description (a binary constant in the
  band holding a number's own small group);
- the prices of rule B, each kept as small as the rule allows: a
  column with a few blanks keeps its correlations with complete columns
  (its own unread count is its own fact), and a rare level refused on a
  grouping's `L1` bands is read on its `L2` bands;
- the units: Fisher's z for a correlation, on a grid of ten-thousandths
  of z at the floor (LANE MPp RULINGS 7), the loader taking exactly the
  printed grid point and nothing beside it, and every unit one decimal
  finer for each 100-fold a moment's count passes 20,000 (product
  against the reference on a table past it); a coefficient between two
  nearly collinear predictors keeps its rounding a small part of its own
  standard error;
- the loader's S39 to S43, each red on a mutant description;
- `K-S6-08`'s moment fixtures restated under rule B: every count a
  published moment implies directly is 0 or at least the floor, by
  exhaustive enumeration at `f` = 3 and `f` = 11, RULE W1, the `L2`
  bands and the pair's four presence cells included (the driver runs
  the wider enumeration; mutants: each floor check, W1 and the neither
  cell dropped);
- the amendment's sentences on the contract page.
"""

import importlib.util
import json
import math
import pathlib
import random
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction

import fixtures
import moment_rule_b_enumeration as enumeration
import pytest

from synthtwin import canonical, chain, chain_check, chain_moments, cli, contract, errors, profile, reading, taxonomy

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
CONTRACT = REPOSITORY / "docs" / "spec" / "profile-contract-v6.md"
FLOOR = 11
KEY = bytes(range(32))


def _reference():
    spec = importlib.util.spec_from_file_location("moment_rule_b", REPOSITORY / "tools" / "reference" / "moment_rule_b.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _csv(header, rows):
    return ",".join(header) + "\n" + "".join(",".join(row) + "\n" for row in rows)


def _clinic(n_rows=1500, seed=7, change=None):
    """An invented clinic table: a record key, an age, a gender, a group, a pressure, a lab, a flag and an event."""
    draw = random.Random(seed)
    rows = []
    for place in range(n_rows):
        age = draw.randint(18, 89)
        gender = draw.choice(["F", "M"])
        group = draw.choice(["a", "b", "c", "d"])
        pressure = "" if draw.random() < 0.05 else f"{round(100 + age * 0.5 + draw.gauss(0, 12), 1)}"
        lab = f"{round(3 + (0.8 if gender == 'M' else 0) + draw.gauss(0, 1), 2)}"
        flag = "yes" if draw.random() < 0.2 + (0.3 if group == "b" else 0) else "no"
        died = "1" if draw.random() < 0.1 + age / 300 else "0"
        seen = f"2023-{draw.randint(1, 12):02d}-{draw.randint(1, 28):02d}"
        rows += [[f"P{place:05d}", f"{age}", gender, group, pressure, lab, flag, died, seen]]
    if change is not None:
        change(rows)
    return _csv(["record", "age", "gender", "group", "pressure", "lab", "flag", "event", "seen"], rows)


def _describe(tmp_path, text, name="clinic", held=(), floor=FLOOR):
    settings = taxonomy.Settings(small_cell_floor=floor)
    tmp_path.mkdir(parents=True, exist_ok=True)
    path = fixtures.write(tmp_path, f"{name}.csv", text)
    table = reading.read_table(str(path), small_cell_floor=floor)
    document = profile.build_document(table, settings, [], [], [])
    chained = chain.describe(table, document, settings, chain.ChainSwitch(name, KEY, tuple(held)))
    return table, document, chained


def _coded(table, document, statistical, floor=FLOOR):
    """Each eligible column's rows read as the chain reads them (`moment_rule_b_enumeration.coded`)."""
    return enumeration.coded(table, document, statistical, floor)


def _loads(tmp_path, document, statistical, name="mutant"):
    written = dict(document)
    written["relationships"] = dict(written["relationships"], statistical=statistical)
    path = fixtures.write_profile(tmp_path, f"{name}.json", written)
    return contract.load_profile(str(path), chain=True)


@pytest.fixture(scope="module")
def clinic(tmp_path_factory):
    folder = tmp_path_factory.mktemp("clinic")
    table, document, chained = _describe(folder, _clinic())
    assert chained.statistical is not None, chained.notes
    return folder, table, document, chained


# -- THE PRODUCT AGAINST THE REFERENCE ----------------------------------------


def test_the_product_equals_the_reference_on_the_same_rows(clinic):
    """Every published number equals the reference's, computed apart (mutant: any rounding, floor or partner rule changed)."""
    _folder, table, document, chained = clinic
    moments = chained.statistical["moments"]
    assert moments is not None and moments["rule"] == "B"
    columns, groupings = _coded(table, document, chained.statistical)
    expected, _refused = _reference().describe(columns, groupings, FLOOR)
    assert moments == expected
    kinds = {entry["column"]: entry["kind"] for entry in moments["columns"]}
    assert kinds == {"age": "number", "gender": "binary", "pressure": "number", "lab": "number", "flag": "binary", "event": "binary"}
    assert any(entry["column"] == "flag" and entry["by"] == "group" for entry in moments["within"])


def test_the_rounding_is_exact_and_half_away_from_nought():
    """The units are tenths of a code (a mean, a band's spread), thousandths (a column's and a pair's spread) and
    ten-thousandths of a share; a correlation is the tanh of its grid point of Fisher's z (ten-thousandths of z at
    20,000 rows or fewer, LANE MPp RULINGS 7), printed to 12 decimals, as the decimal module's correctly rounded ln and
    exp give it, and the loader's grid check takes that print and not one place of the twelfth decimal beside it
    (mutants: half to even, a float, r rounded on its own scale, the old step of a thousandth of z, or the old grid
    check's tolerance of 1e-9)."""
    assert (chain_moments.SCALE_MEAN, chain_moments.SCALE_SPREAD, chain_moments.SCALE_SHARE) == (10, 10, 10000)
    assert chain_moments.SCALE_COLUMN_SPREAD == 1000
    assert (chain_moments.SCALE_FISHER_Z, chain_moments.SCALE_CORRELATION, chain_moments.CORRELATION_TOP) == (10000, 10**12, 999999 * 10**6)
    draw = random.Random(5)
    for _case in range(400):
        n = draw.randint(1, 5000)
        total = draw.randint(0, 255 * n)
        expect = int((Decimal(total) / Decimal(n) * 10).quantize(Decimal(1), rounding=ROUND_HALF_UP))
        assert chain_moments.rounded_ratio(total, n, 10) == expect
        square = draw.randint(0, 10**12)
        expect_root = int((Decimal(square).sqrt() * 10).quantize(Decimal(1), rounding=ROUND_HALF_UP))
        assert chain_moments.rounded_root(square, 1, 10) == expect_root
    assert chain_moments.rounded_ratio(5, 1000, 1000) == 5
    assert chain_moments.rounded_ratio(1, 200, 100) == 1
    assert chain_moments.rounded_ratio(-1, 200, 100) == -1
    reference = _reference()
    for _case in range(200):
        first = draw.randint(1, 10 ** draw.randint(1, 18))
        second = draw.randint(1, 10 ** draw.randint(1, 18))
        top = chain_moments._isqrt(first * second)
        cross = draw.choice([draw.randint(-top, top), top - draw.randint(0, 3), -(top - draw.randint(0, 50))])
        n = draw.choice([11, 20000, 20001, 2000001])
        found = reference.published_r(Fraction(cross * cross, first * second), -1 if cross < 0 else 1, n)
        assert chain_moments.rounded_correlation(cross, first, second, n) == found
        assert chain_moments.on_the_grid(found, n)
        if n <= 20000 and abs(found) < chain_moments.CORRELATION_TOP:
            # Neighbouring grid points stand (1 - r ** 2) / 10,000 apart in r here, at least 2e-10 (200 places of the
            # twelfth decimal) up to |r| = 0.999999, so one place off a printed grid point is off the grid.
            assert not chain_moments.on_the_grid(found + 1, n) and not chain_moments.on_the_grid(found - 1, n)
    assert chain_moments.rounded_correlation(0, 4, 9, 11) == 0
    assert chain_moments.rounded_correlation(-1, 1, 4, 11) == -chain_moments.tanh_units(5493, 10000)
    assert chain_moments.correlation_top_units(10000) == 72543
    assert chain_moments.rounded_correlation(6, 4, 9, 11) == chain_moments.tanh_units(72543, 10000) <= chain_moments.CORRELATION_TOP
    assert chain_moments.tanh_units(72544, 10000) > chain_moments.CORRELATION_TOP


def test_the_correlation_s_rounding_is_a_hundredth_of_its_standard_error_at_every_r():
    """Half a step of z over z's standard error, 1 / sqrt(n - 3), is at most 0.00707 at every count, so r's rounding over
    r's standard error, (1 - r ** 2) / sqrt(n), stays at most 0.01 at every |r| up to 0.999 (mutants: a step of r, or
    the old step of a thousandth of z, which reached 0.0707)."""
    worst = 0.0
    for n in (11, 1000, 20000, 20001, 200000, 2000000, 2000001, 20000000):
        scale = chain_moments.unit(chain_moments.SCALE_FISHER_Z, n)
        for size in range(0, 999001, 3331):
            r = size / 10**6
            z = math.atanh(r)
            grid = math.tanh(math.floor(z * scale + 0.5) / scale)
            worst = max(worst, abs(grid - r) / ((1 - r * r) / math.sqrt(n)))
    assert worst <= 0.01, worst


def test_the_loader_s_grid_check_tells_neighbouring_grid_points_apart():
    """LANE MPp RULINGS 7 (2): near |r| = 0.999999 neighbouring grid points of z stand (1 - r ** 2) times the step
    apart in r, 2e-10 at the floor's ten-thousandths of z and 2e-11 one place finer, so the check compares on the grid
    integer: every grid point's print loads and every value between two neighbouring prints is refused, at every count
    up to 200,000,000 rows; past it, where neighbouring points print alike, their shared print loads. A point of the
    first grid built, thousandths of z, is a point of this one (ten of its steps) and loads where it lies on it (mutant:
    the old tolerance of 1e-9, which loaded the values between neighbouring points near the top)."""
    for n in (11, 20000, 20001, 2000000, 2000001, 200000000, 200000001):
        scale = chain_moments.unit(chain_moments.SCALE_FISHER_Z, n)
        top = chain_moments.correlation_top_units(scale)
        for point in (top, top - 1, top - 7, scale, scale // 2, 3):
            printed = chain_moments.tanh_units(point, scale)
            below = chain_moments.tanh_units(point - 1, scale)
            assert chain_moments.on_the_grid(printed, n) and chain_moments.on_the_grid(-printed, n), (n, point)
            between = [value for value in (below + 1, (below + printed) // 2, printed - 1) if below < value < printed]
            assert not any(chain_moments.on_the_grid(value, n) or chain_moments.on_the_grid(-value, n) for value in between), (n, point)
            if n == 20000 and point == top:
                # The value halfway between the top two grid points stands 100 places of the twelfth decimal from
                # each: within the old tolerance of 1e-9 (1,000 places), off the grid.
                assert printed - below == 200 and between
        assert not chain_moments.on_the_grid(chain_moments.tanh_units(top + 1, scale), n) or scale > 10**6
    for point in list(range(0, 7254, 97)) + [7254]:
        old = chain_moments.tanh_units(point, 1000)
        assert old == chain_moments.tanh_units(10 * point, 10000) and chain_moments.on_the_grid(old, 20000), point
        halfway = (old + chain_moments.tanh_units(10 * point + 1, 10000)) // 2
        assert not chain_moments.on_the_grid(old + 1, 20000) and not chain_moments.on_the_grid(halfway, 20000), point


def _collinear_rounding(rho, settings, z_unit, spread_unit, draws, seed, n=20000):
    """The 95th percentile over draws, and the largest, of a collinear coefficient's rounding over its own standard error.

    Two predictors of correlation `rho` and an outcome at R^2 0.3 (each coefficient setting); each draw places the
    three true correlations at a uniformly drawn offset from their grid points of z, as a sample correlation's z falls,
    and rounds each to its NEAREST grid point, as the product does, with spreads of 40 to 70 codes rounded to the
    column's unit; a draw reads the larger of its two coefficients (both slope directions)."""
    draw = random.Random(seed)
    found = []
    for first, second in settings:
        spread = math.sqrt((first * first + second * second + 2 * first * second * rho) / 0.3)
        truths = (rho, (first + second * rho) / spread, (second + first * rho) / spread)
        for _draw in range(draws):
            true = [math.tanh(math.atanh(r) + draw.uniform(-0.5, 0.5) / z_unit) for r in truths]
            shown = [math.tanh(math.floor(math.atanh(r) * z_unit + 0.5) / z_unit) for r in true]
            sds = [draw.uniform(40, 70) for _column in range(3)]
            shown_sds = [math.floor(sd * spread_unit + 0.5) / spread_unit for sd in sds]

            def coefficients(r12, r1y, r2y, s):
                rest = 1 - r12 * r12
                return (r1y - r12 * r2y) / rest * s[2] / s[0], (r2y - r12 * r1y) / rest * s[2] / s[1]

            exact, rounded = coefficients(*true, sds), coefficients(*shown, shown_sds)
            r_sq = (true[1] ** 2 + true[2] ** 2 - 2 * true[1] * true[2] * true[0]) / (1 - true[0] ** 2)
            base = math.sqrt((1 - r_sq) / ((n - 3) * (1 - true[0] ** 2)))
            found += [max(abs(rounded[k] - exact[k]) / (base * sds[2] / sds[k]) for k in range(2))]
    found.sort()
    return found[int(0.95 * len(found))], found[-1]


def test_a_collinear_coefficient_s_rounding_is_a_small_part_of_its_standard_error():
    """LANE MPp RULINGS 7 (the owner's criterion: advanced parametric methods hold on the twin): a regression on two
    nearly collinear predictors amplifies r's rounding on its grid of z by about 1 / (1 - r12 ** 2). At 20,000 rows
    (R^2 0.3, coefficient settings (0.3, 0.3) and (0.5, -0.3), 6,000 draws each, the product's units), the 95th
    percentile of a coefficient's rounding over its own standard error, sqrt((1 - R^2) / ((n - 3)(1 - r12 ** 2))) *
    sd_y / sd_x, is at most 0.05 at a predictor correlation of 0.9, 0.06 at 0.95, 0.10 at 0.99 and 0.33 at 0.999, and
    at most 0.02, 0.03, 0.04 and 0.11 at 200,001 and 2,000,001 rows, about twice K-S6-14's readings there, so a
    regression at a large count cannot pass unseen (batch 4o's merge); K-S6-14 measures the same on the product's `released` (mutant: the old step
    of a thousandth of z, which reads about 0.25, 0.33, 0.67 and 2.08 here)."""
    bounds = {0.9: 0.05, 0.95: 0.06, 0.99: 0.10, 0.999: 0.33}
    past_the_floor = {0.9: 0.02, 0.95: 0.03, 0.99: 0.04, 0.999: 0.11}
    for n in (20000, 200001, 2000001):
        z_unit = chain_moments.unit(chain_moments.SCALE_FISHER_Z, n)
        spread_unit = chain_moments.unit(chain_moments.SCALE_COLUMN_SPREAD, n)
        for rho, bound in (bounds if n == 20000 else past_the_floor).items():
            p95, _largest = _collinear_rounding(rho, ((0.3, 0.3), (0.5, -0.3)), z_unit, spread_unit, 6000 if n == 20000 else 1500, 11, n)
            assert p95 <= bound, (n, rho, p95)


def test_each_unit_grows_with_its_own_count():
    """One decimal place finer for each 100-fold, or part of one, a moment's count passes 20,000, so the rounding stays the
    same part of the sampling error at every size (mutant: a fixed unit, or the step at the wrong count)."""
    reference = _reference()
    for n, factor in ((11, 1), (20000, 1), (20001, 10), (2000000, 10), (2000001, 100), (200000000, 100), (200000001, 1000)):
        assert chain_moments.unit(10, n) == 10 * factor == reference.unit(10, n)


def test_the_product_equals_the_reference_past_twenty_thousand_rows():
    """On 30,000 coded rows (two numbers, a binary, a three-band grouping) every moment stands in the unit of its own count:
    the columns and the pair in the finer unit, each band of 10,000 in the floor's (mutant: one unit for all)."""
    draw = random.Random(11)
    rows = 30000
    bands = bytes(draw.randrange(3) for _row in range(rows))
    first = bytes(min(255, max(0, 100 + 30 * band + draw.randint(-40, 40))) for band in bands)
    second = bytes(min(255, max(0, value // 2 + draw.randint(0, 60))) for value in first)
    flag = bytes(1 if draw.random() < 0.2 + 0.2 * band else 0 for band in bands)
    full = bytearray([1] * rows)
    columns = [
        chain_moments.Released("first", chain_moments.KIND_NUMBER, first, full),
        chain_moments.Released("second", chain_moments.KIND_NUMBER, second, full),
        chain_moments.Released("flag", chain_moments.KIND_BINARY, flag, full),
    ]
    totals = tuple(bands.count(band) for band in range(3))
    grouping = chain_moments.Grouping("group", bands, totals, frozenset(), (0, 0, 1))
    found, _counts = chain_moments.released(columns, [grouping], FLOOR)
    expected, _refused = _reference().describe(
        [(c.name, c.kind, list(c.values)) for c in columns], [("group", list(bands), list(totals), set(), [0, 0, 1])], FLOOR
    )
    assert found == expected
    assert found["columns"][0]["mean"] == chain_moments.rounded_ratio(sum(first), rows, 100)
    group = next(entry for entry in found["within"] if entry["column"] == "first")["groups"][0]
    assert group[1] == chain_moments.rounded_ratio(sum(v for v, b in zip(first, bands) if b == 0), totals[0], 10)
    # The loader reads it back, each spread's range at its own count's unit (the verify's item 3 on repair 1: a range
    # taken at the floor's unit refused nothing a test wrote past 20,000 rows; mutant: the range at the floor's unit,
    # which refuses this genuine description, whose column spreads stand in ten-thousandths of a code).
    inputs = enumeration.loader_inputs(columns, [grouping])
    chain_check.check_moments(found, *inputs[:3], FLOOR, inputs[3], inputs[4])
    assert found["columns"][0]["sd"] > 128 * chain_moments.SCALE_COLUMN_SPREAD
    over = json.loads(json.dumps(found))
    over["columns"][0]["sd"] = chain_moments.spread_top(rows, chain_moments.unit(chain_moments.SCALE_COLUMN_SPREAD, rows)) + 1
    floor_unit = json.loads(json.dumps(found))
    floor_unit["columns"][0]["sd"] = chain_moments.rounded_ratio(found["columns"][0]["sd"], 10, 1)
    for mutant, words in ((over, "the sd is a whole number"), (floor_unit, "total-variance identity")):
        with pytest.raises(errors.ProfileError) as refused:
            chain_check.check_moments(mutant, *inputs[:3], FLOOR, inputs[3], inputs[4])
        assert "S42" in str(refused.value) and words in str(refused.value)


# -- HIPAA FIRST: THE ATTACKS ON THE RULE ------------------------------------


def test_held_identifier_and_date_columns_take_no_moment(tmp_path, clinic):
    """No moment reads a held column or an identifier, and a date or a column of all-different values is no moment column (mutants: a held column read as a number; an identifier read as a grouping)."""
    _folder, table, document, chained = clinic
    moments = chained.statistical["moments"]
    assert not {"record", "seen"} & {entry["column"] for entry in moments["columns"]}
    _t, _d, held = _describe(tmp_path, _clinic(), name="held", held=("record",))
    assert {"column": "record", "reason": "held"} in held.statistical["ineligible"]
    held_named = {entry["column"] for entry in held.statistical["moments"]["columns"]}
    held_by = {entry["by"] for entry in held.statistical["moments"]["within"]}
    assert "record" not in held_named and "record" not in held_by
    settings = taxonomy.Settings(small_cell_floor=FLOOR)
    forced = dict(document, settings=dict(document["settings"], forced_identifiers=["record"]))
    keyed = chain.describe(table, forced, settings, chain.ChainSwitch("keyed", KEY))
    keyed_named = {entry["column"] for entry in keyed.statistical["moments"]["columns"]}
    keyed_by = {entry["by"] for entry in keyed.statistical["moments"]["within"]}
    assert "record" not in keyed_named and "record" not in keyed_by


def test_no_tail_value_enters_a_moment(tmp_path, clinic):
    """The largest reading moved far out leaves every moment byte for byte (codes clip at the published rungs; mutant: the raw value read)."""
    _folder, _table, _document, chained = clinic

    def far(rows):
        top = max(range(len(rows)), key=lambda at: float(rows[at][5]))
        rows[top][5] = f"{float(rows[top][5]) * 40:.2f}"

    _t, _d, moved = _describe(tmp_path, _clinic(change=far), name="far")
    assert canonical.serialize(moved.statistical["moments"]) == canonical.serialize(chained.statistical["moments"])


def test_a_share_implying_one_to_ten_rows_is_refused(tmp_path):
    """A binary with 5 of one group's rows at `yes` publishes no share on that grouping's `L1` bands; on its `L2` bands,
    where that group is pooled with others, every count passes or nothing stands (mutant: the level floor dropped)."""

    def five(rows):
        seen = 0
        for row in rows:
            if row[3] == "d":
                row[6] = "yes" if seen < 5 else "no"
                seen += 1

    table, document, chained = _describe(tmp_path, _clinic(change=five), name="five")
    moments = chained.statistical["moments"]
    assert not any(entry["column"] == "flag" and entry["by"] == "group" and "level" not in entry for entry in moments["within"])
    refused = chained.counts.get("moments refused within: a count of 1 to f - 1", 0)
    assert refused + chained.counts.get("moments L1 bands refused, L2 published: a count of 1 to f - 1", 0) >= 1
    columns, groupings = _coded(table, document, chained.statistical)
    assert _reference().describe(columns, groupings, FLOOR)[0] == moments


def test_a_band_mean_over_one_to_ten_people_is_refused(tmp_path):
    """A pressure read on 5 rows of one group publishes no mean on that grouping's `L1` bands (mutant: the band floor dropped)."""

    def sparse(rows):
        seen = 0
        for row in rows:
            if row[3] == "c":
                row[4] = row[4] if seen < 5 else ""
                seen += 1

    _table, _document, chained = _describe(tmp_path, _clinic(change=sparse), name="sparse")
    moments = chained.statistical["moments"]
    assert not any(entry["column"] == "pressure" and entry["by"] == "group" and "level" not in entry for entry in moments["within"])


def test_every_count_one_subtraction_gives_is_nought_or_the_floor(clinic):
    """Every band's readings add to the column's and every complement passes; every pair's four presence cells pass
    (mutant: a band left out, or the neither cell unread)."""
    _folder, table, _document, chained = clinic
    statistical = chained.statistical
    moments = statistical["moments"]
    totals = {
        (entry["column"], level): [sum(entry["totals"][b] for b in band) for band in entry[f"l{level}"]]
        for entry in statistical["ladder"]
        for level in (1, 2)
    }
    counts = {entry["column"]: entry["n"] for entry in moments["columns"]}
    for entry in moments["within"]:
        groups = entry["groups"]
        assert sum(group[0] for group in groups) == counts[entry["column"]]
        for band, group in enumerate(groups):
            for found in (group[0], totals[(entry["by"], entry.get("level", 1))][band] - group[0]):
                assert found == 0 or found >= FLOOR
    numbers = [entry["column"] for entry in moments["columns"] if entry["kind"] == "number"]
    for at, line in enumerate(moments["correlations"]):
        for other, pair in enumerate(line):
            if pair is not None:
                first, second = counts[numbers[at]], counts[numbers[other]]
                for found in (pair[1], first - pair[1], second - pair[1], table.n_rows - first - second + pair[1]):
                    assert found == 0 or found >= FLOOR


def _two_labs(n_rows, both_blank, x_blank=60, y_blank=60, seed=7):
    """An invented table of two lab values and a group: x blank on `x_blank` rows, y on `y_blank`, both on `both_blank`."""
    draw = random.Random(seed)
    rows = []
    for _place in range(n_rows):
        age = draw.randint(18, 89)
        rows += [[f"{age}", f"{round(100 + age * 0.5 + draw.gauss(0, 12), 1)}", f"{round(3 + draw.gauss(0, 1) + age / 50, 2)}", draw.choice("abcd")]]
    for place in range(x_blank):
        rows[place][1] = ""
    for place in range(x_blank - both_blank, x_blank - both_blank + y_blank):
        rows[place][2] = ""
    return _csv(["age", "xval", "yval", "grp"], rows)


def _pair(moments, one, two):
    numbers = [entry["column"] for entry in moments["columns"] if entry["kind"] == "number"]
    at, other = sorted((numbers.index(one), numbers.index(two)), reverse=True)
    return moments["correlations"][at][other]


@pytest.mark.parametrize("both_blank", [1, 3, 5])
def test_the_rows_holding_neither_column_are_floored(tmp_path, both_blank):
    """Two labs blank alone on 60 rows each and together on 1, 3 or 5: the pair's fourth presence cell, rows less each
    column's readings plus the pair's, is that small count, so no correlation is published (mutant: the neither cell
    unread, which published 1,500 - 1,440 - 1,440 + 1,383 = 3 rows)."""
    table, document, chained = _describe(tmp_path, _two_labs(1500, both_blank), name=f"neither{both_blank}")
    moments = chained.statistical["moments"]
    assert _pair(moments, "xval", "yval") is None
    assert chained.counts["moments refused correlation: rows holding neither, 1 to f - 1"] == 1
    columns, groupings = _coded(table, document, chained.statistical)
    assert _reference().describe(columns, groupings, FLOOR)[0] == moments


def test_the_rows_holding_neither_column_publish_at_the_floor(tmp_path):
    """The same pair blank together on 11 rows publishes its correlation (the floor's own count passes)."""
    _table, _document, chained = _describe(tmp_path, _two_labs(1500, 11), name="neither11")
    pair = _pair(chained.statistical["moments"], "xval", "yval")
    assert pair is not None and pair[1] == 1500 - 60 - 60 + 11


def _w1_table(edge):
    """An invented table: a number holding five noughts (its own published group of 5), another number, a group, and a
    flag that holds 1 on every row up to the number's value at sorted place `edge` (its lowest band)."""
    draw = random.Random(3)
    rows = []
    for place in range(3000):
        value = round(draw.uniform(1, 100), 1) if place >= 5 else 0
        rows += [[f"{value}", f"{round(draw.gauss(50, 10), 1)}", draw.choice("abc"), ""]]
    low = sorted(float(row[0]) for row in rows)[edge]
    for row in rows:
        row[3] = "1" if float(row[0]) <= low else ("1" if draw.random() < 0.5 else "0")
    return _csv(["xval", "other", "grp", "flag"], rows)


def test_rule_w1_is_read_in_a_band_holding_an_own_small_group(tmp_path, monkeypatch):
    """The number publishes its five noughts as its own group; the flag holds 1 on every row of the number's lowest
    band, so a share of 1 there would say all five hold the flag. RULE W1 refuses that band's share on the `L1` bands,
    and the loader's S41 refuses the description W1's mutant writes, reading the noughts from the number's block
    (mutants: W1 dropped in the product, which publishes it; W1 dropped in the loader, which loads it)."""
    table, document, chained = _describe(tmp_path, _w1_table(749), name="w1")
    moments = chained.statistical["moments"]
    assert chained.counts.get("moments refused within: RULE W1", 0) + chained.counts.get("moments L1 bands refused, L2 published: RULE W1", 0) >= 1
    fine = [entry for entry in moments["within"] if entry["column"] == "flag" and entry["by"] == "xval"]
    assert all(entry.get("level") == 2 for entry in fine)
    columns, groupings = _coded(table, document, chained.statistical)
    assert _reference().describe(columns, groupings, FLOOR)[0] == moments
    monkeypatch.setattr(chain_moments, "_bands_refused", _without_w1(chain_moments._bands_refused))
    _t, mutant_document, mutant = _describe(tmp_path, _w1_table(749), name="w1mutant")
    assert any(entry["column"] == "flag" and entry["by"] == "xval" and "level" not in entry for entry in mutant.statistical["moments"]["within"])
    monkeypatch.undo()
    with pytest.raises(errors.ProfileError) as refused:
        _loads(tmp_path, mutant_document, mutant.statistical, name="w1_loaded")
    assert "S41" in str(refused.value) and "RULE W1" in str(refused.value)


def _without_w1(refused):
    def mutant(kind, found, totals, small, floor):
        return refused(kind, found, totals, frozenset(), floor)

    return mutant


def test_a_few_blanks_keep_the_correlations_with_complete_columns(tmp_path):
    """A lab blank on 3 rows publishes that 3 in its own block; beside a column read on every row, the pair's only outside
    count is that same 3, the lab's own fact, so the correlation stands (contract 4.6d.0 (2); mutant: the own count
    floored, which refused it). Its `within` stays refused: the blanks fall 1 to 10 in a band, a count across columns."""
    table, document, chained = _describe(tmp_path, _two_labs(1500, 0, x_blank=3, y_blank=0), name="fewblanks")
    moments = chained.statistical["moments"]
    pair = _pair(moments, "xval", "age")
    assert pair is not None and pair[1] == 1497
    # Both orders of the pair: xval (3 blanks) before the complete age, and the complete yval before xval; each pair
    # holds fewer rows than the complete column's readings, so it carries its own two spreads.
    other = _pair(moments, "yval", "xval")
    assert other is not None and other[1] == 1497 and len(pair) == len(other) == 3
    assert not any(entry["column"] == "xval" and "level" not in entry for entry in moments["within"])
    columns, groupings = _coded(table, document, chained.statistical)
    assert _reference().describe(columns, groupings, FLOOR)[0] == moments
    # The loader reads it back (Codex's item 1 and the verify's item 1 on repair 1: S41's waiver read the other
    # column's completeness and refused this description; mutant: the waiver on the other column).
    assert _loads(tmp_path, document, chained.statistical, name="fewblanks_loaded") is not None


def test_a_rare_level_refused_on_narrow_bands_is_read_on_the_coarser_ones(tmp_path):
    """A flag held by 30 of 3,000 rows falls 1 to 10 into some `L1` band of the age; on the age's published `L2` bands
    every count passes, so the share stands there, all bands or none (mutant: no `L2` reading, which refused it)."""

    def rare(rows):
        for at in range(len(rows)):
            rows[at][6] = "yes" if at % 100 == 0 else "no"

    table, document, chained = _describe(tmp_path, _clinic(n_rows=3000, seed=5, change=rare), name="rare")
    moments = chained.statistical["moments"]
    coarse = [entry for entry in moments["within"] if entry["column"] == "flag" and entry.get("level") == 2]
    assert coarse and chained.counts["moments within on the L2 bands: binary"] >= 1
    columns, groupings = _coded(table, document, chained.statistical)
    assert _reference().describe(columns, groupings, FLOOR)[0] == moments


def test_a_table_of_several_rows_a_person_publishes_no_moment(tmp_path):
    """The chain, and so every moment, is off where a person column is named (the patient layer is lane GRa's; mutant: rows counted as people)."""
    settings = taxonomy.Settings(small_cell_floor=FLOOR)
    path = fixtures.write(tmp_path, "persons.csv", _clinic(n_rows=600))
    table = reading.read_table(str(path), small_cell_floor=FLOOR)
    document = profile.build_document(table, settings, [], [], [])
    document["settings"] = dict(document["settings"], person_columns=["record"])
    chained = chain.describe(table, document, settings, chain.ChainSwitch("persons", KEY))
    assert chained.statistical is None and chained.notes[-1] == f"no chain is published: {chain.OFF_PERSON}"


def test_a_top_coded_age_is_read_top_coded(tmp_path, monkeypatch, capsys):
    """Through `synthtwin profile` at 20,000 rows, where the command top-codes ages over 89 (its Safe Harbor rule; the
    library alone does not, P4-D427 and P4-D433), the age's moments stand on its code, which tops at a published rung
    of 90 or less, and every age over that rung reads the top code, so no age over 90 enters a moment (one case at the
    size the top-code reaches; mutant: the raw age read, or a clip above the published rungs)."""

    def old(rows):
        for at in range(0, len(rows), 50):
            rows[at][1] = f"{91 + (at // 50) % 14}"

    monkeypatch.chdir(tmp_path)
    path = fixtures.write(tmp_path, "aged.csv", _clinic(n_rows=20000, seed=3, change=old))
    capsys.readouterr()
    assert cli.main(["profile", "aged.csv"], chain=cli.ChainRun(folder=str(tmp_path / "data"))) == 0
    capsys.readouterr()
    document = json.loads((tmp_path / "aged-profile.json").read_text(encoding="utf-8"))
    statistical = document["relationships"]["statistical"]
    assert statistical is not None and statistical["moments"] is not None
    assert any(entry["column"] == "age" for entry in statistical["moments"]["columns"])
    # The command's description loads with the chain's switch on, its moments with it (the verify's hunt on repair 1).
    assert contract.load_profile(str(tmp_path / "aged-profile.json"), chain=True) is not None
    block = next(b for b in document["columns"] if b["name"] == "age")
    codes = chain_moments.codes_of(block)
    assert codes is not None and codes.hi_value <= 90
    table = reading.read_table(str(path), small_cell_floor=FLOOR)
    names = [b["name"] for b in document["columns"]]
    read = chain.read_column(table, names.index("age"), block, taxonomy.Settings(small_cell_floor=FLOOR), enumeration.DECLARED, "", 0)
    values = reading.column_values(table, names.index("age"))
    tops = [read.linear[r] for r in range(table.n_rows) if read.has_reading[r] and float(values[r]) >= 90]
    assert tops and set(tops) == {255}


# -- THE LOADER: S39 TO S43 ---------------------------------------------------


def _mutated(clinic, edit):
    _folder, _table, document, chained = clinic
    statistical = json.loads(json.dumps(chained.statistical))
    edit(statistical["moments"], statistical)
    return document, statistical


def test_the_loader_reads_the_published_moments_back(tmp_path, clinic):
    _folder, _table, document, chained = clinic
    loaded = _loads(tmp_path, document, chained.statistical, name="clean")
    assert loaded is not None


def _first_binary_within(moments):
    for entry in moments["within"]:
        if any(c["column"] == entry["column"] and c["kind"] == "binary" for c in moments["columns"]):
            return entry
    raise AssertionError("no binary within entry")


def _first_number_within(moments):
    for entry in moments["within"]:
        if any(c["column"] == entry["column"] and c["kind"] == "number" for c in moments["columns"]) and len(entry["groups"][0]) == 3:
            return entry
    raise AssertionError("no number within entry")


def _tenfold_means(entry):
    for group in entry["groups"]:
        if len(group) == 3:
            group[1] *= 10


MUTANTS = {
    "S39 scales": lambda m, s: m["scales"].update(fisher_z=1000),
    "S39 rule": lambda m, s: m.update(rule="A"),
    "S40 an ineligible column": lambda m, s: m["columns"][0].update(column="record"),
    "S40 a column of no ladder": lambda m, s: m["within"][0].update(by="nowhere"),
    "S41 a band of five": lambda m, s: _first_binary_within(m)["groups"][0].__setitem__(0, 5),
    "S41 a share pinning a small count": lambda m, s: _first_binary_within(m)["groups"][0].__setitem__(
        1, chain_moments.rounded_ratio(5, _first_binary_within(m)["groups"][0][0], chain_moments.SCALE_SHARE)
    ),
    "S42 an r off its grid": lambda m, s: next(p for line in m["correlations"] for p in line if p).__setitem__(
        0, next(p for line in m["correlations"] for p in line if p)[0] + 2000
    ),
    "S42 an r past 0.999999": lambda m, s: next(p for line in m["correlations"] for p in line if p).__setitem__(
        0, chain_moments.CORRELATION_TOP + 1
    ),
    # One place of the twelfth decimal off its grid point (LANE MPp RULINGS 7 (2); mutant: the old tolerance of 1e-9).
    "S42 an r a twelfth decimal off its grid": lambda m, s: next(p for line in m["correlations"] for p in line if p).__setitem__(
        0, next(p for line in m["correlations"] for p in line if p)[0] + 1
    ),
    "S42 band means in another unit": lambda m, s: _tenfold_means(_first_number_within(m)),
    "S43 a level of no ladder": lambda m, s: m["within"][0].update(level=3),
    "S43 level 1 named": lambda m, s: m["within"][0].update(level=1),
    "S42 a binary's share": lambda m, s: next(c for c in m["columns"] if c["kind"] == "binary").update(share=999),
    "S43 a pair twice": lambda m, s: m.update(within=m["within"] + [dict(m["within"][0])]),
    "S43 a short row": lambda m, s: m["correlations"].__setitem__(-1, m["correlations"][-1][:-1]),
}


@pytest.mark.parametrize("name", sorted(MUTANTS))
def test_each_loader_invariant_refuses_its_mutant(tmp_path, clinic, name):
    document, statistical = _mutated(clinic, MUTANTS[name])
    with pytest.raises(errors.ProfileError) as refused:
        _loads(tmp_path, document, statistical, name=name.replace(" ", "_").replace("'", ""))
    assert name.split()[0] in str(refused.value)


def _number_alone(moments, name, n):
    """Codex's item 4 on repair 1: a number's count set to `n`, its `within` entries removed and its correlations nulled."""
    next(entry for entry in moments["columns"] if entry["column"] == name)["n"] = n
    moments["within"] = [entry for entry in moments["within"] if entry["column"] != name]
    numbers = [entry["column"] for entry in moments["columns"] if entry["kind"] == "number"]
    at = numbers.index(name)
    for row in range(len(numbers)):
        for other in range(row):
            if at in (row, other):
                moments["correlations"][row][other] = None


def _a_band_mean_moved(moments):
    """The verify's item 3 on repair 1: one band's mean moved one code (ten tenths), inside the code's range."""
    group = _first_number_within(moments)["groups"][0]
    group[1] += 10 if group[1] + 10 <= 2550 else -10


def _an_incomplete_pair(moments):
    return next(pair for line in moments["correlations"] for pair in line if pair is not None and len(pair) == 3)


def _a_pair_spread_past_its_range(moments):
    """Lane MPp verify 2's C1: an incomplete pair's own spread of the column read outside the pair (so no equality with
    the column's own spread binds it) set one unit past the largest its count of codes can hold."""
    numbers = [entry["column"] for entry in moments["columns"] if entry["kind"] == "number"]
    counts = {entry["column"]: entry["n"] for entry in moments["columns"]}
    for at, line in enumerate(moments["correlations"]):
        for other, pair in enumerate(line):
            if pair is None or len(pair) != 3:
                continue
            for place, name in enumerate((numbers[at], numbers[other])):
                if counts[name] > pair[1]:
                    pair[2][place] = chain_moments.spread_top(pair[1], chain_moments.unit(chain_moments.SCALE_COLUMN_SPREAD, pair[1])) + 1
                    return
    raise AssertionError("no incomplete pair beside a column read outside it")


def _pressure_spread_moved(moments):
    """The pair (pressure, age): every pressure reading lies in the pair, so its pair spread is its own; moved by one."""
    _pair(moments, "pressure", "age")[2][0] += 1


DESCRIBED_MUTANTS = {
    "a number's count": (lambda m: _number_alone(m, "lab", 11), "S41", "a number's count is the readings its column block lays out"),
    "a spread beside its bands": (
        lambda m: next(e for e in m["columns"] if e["column"] == "lab").update(sd=0),
        "S42",
        "the total-variance identity",
    ),
    "a band's mean moved": (_a_band_mean_moved, "S42", "add up to the column's mean within the rounding"),
    "a pair's spreads dropped": (lambda m: _an_incomplete_pair(m).pop(), "S42", "a pair publishes its own two spreads exactly where"),
    "a pair's spread unlike its column's": (_pressure_spread_moved, "S42", "has the pair's spread equal to its own"),
    "a pair's spread past its range": (_a_pair_spread_past_its_range, "S42", "a pair's spread lies on the code's range"),
    "spreads beside a complete pair": (
        lambda m: _pair(m, "lab", "age").append([1, 1]),
        "S42",
        "a pair publishes its own two spreads exactly where",
    ),
}


@pytest.mark.parametrize("name", sorted(DESCRIBED_MUTANTS))
def test_each_repaired_loader_check_refuses_its_mutant(tmp_path, clinic, name):
    """Codex's items 4 and 5 and the verify's item 3 on repair 1, the pair spreads of LANE MPp RULINGS 5 (2) and verify
    2's C1 (a pair's own spread past its range, LANE MPp RULINGS 7 (3)): each mutant description is refused by its own
    check, named by its words (mutants: each check dropped, which loaded it; pair_spread_range_dropped for C1)."""
    edit, invariant, words = DESCRIBED_MUTANTS[name]
    document, statistical = _mutated(clinic, lambda m, s: edit(m))
    with pytest.raises(errors.ProfileError) as refused:
        _loads(tmp_path, document, statistical, name=name.replace(" ", "_").replace("'", ""))
    assert invariant in str(refused.value) and words in str(refused.value)


def test_the_loader_refuses_rows_holding_neither_of_one_to_ten(tmp_path):
    """S41 reads the pair's fourth presence cell: two labs blank together on 11 rows publish; the pair's rows moved
    down by 8 leave each column's outside readings at the floor or more and the neither cell at 3 (mutant: S41 without
    the neither cell, which loaded it)."""
    _table, document, chained = _describe(tmp_path, _two_labs(1500, 11), name="neitherload")
    statistical = json.loads(json.dumps(chained.statistical))
    pair = _pair(statistical["moments"], "xval", "yval")
    pair[1] -= 8
    with pytest.raises(errors.ProfileError) as refused:
        _loads(tmp_path, document, statistical, name="neither_mutant")
    assert "S41" in str(refused.value) and "neither" in str(refused.value)


def test_the_loader_refuses_an_outside_count_of_one_to_ten_beside_no_complete_column(tmp_path):
    """S41 reads each column's readings outside the pair where neither column is read on every row: the two labs blank
    together on 11 rows publish; the pair's rows moved up to 3 under each column's readings leave an outside count of 3
    in both columns and the neither cell at 57 (the verify's item 1 on repair 1; mutant: S41's outside check dropped,
    which loaded it)."""
    _table, document, chained = _describe(tmp_path, _two_labs(1500, 11), name="outsideload")
    statistical = json.loads(json.dumps(chained.statistical))
    readings = {entry["column"]: entry["n"] for entry in statistical["moments"]["columns"]}
    pair = _pair(statistical["moments"], "xval", "yval")
    assert readings["xval"] == readings["yval"] == 1440 and pair[1] == 1391
    pair[1] = readings["xval"] - 3
    with pytest.raises(errors.ProfileError) as refused:
        _loads(tmp_path, document, statistical, name="outside_mutant")
    assert "S41" in str(refused.value) and "outside the pair" in str(refused.value)


# -- THE ROUND TRIP: WHAT THE PRODUCT WRITES, ITS LOADER READS ----------------


def test_every_description_the_product_writes_its_loader_reads():
    """2,000 seeded random tables of codes 0 to 255 (bands of 11 to 40 rows, complete and blank-bearing numbers in both
    pair orders, spreads at the code's two ends, binaries, `L2` bands and own-fact bands): every object
    `chain_moments.released` writes, `chain_check.check_moments` reads back, and the first 200 equal the reference's
    (LANE MPp RULINGS 5 (1); the whole-object equality held while the loader refused: mutants, 23a9a358's loader checks,
    the waiver on the other column, refusing 929, and the spread ceiling of 128 codes, refusing 715)."""
    found = enumeration.round_trip(2000)
    assert found["published"] == 2000 and found["refused"] == 0, found["first_refusal"]
    assert found["pairs_with_spreads"] > 0 and found["band_spreads_past_128"] > 0
    reference = _reference()
    for seed in range(200):
        columns, groupings = enumeration.random_table(seed)
        produced, _counts = chain_moments.released(columns, groupings, FLOOR)
        coded = [(c.name, c.kind, [v if h else None for v, h in zip(c.values, c.present)]) for c in columns]
        grouped = [(g.name, list(g.bands), list(g.totals), set(g.small), list(g.coarsest)) for g in groupings]
        assert reference.describe(coded, grouped, FLOOR)[0] == produced, seed


def test_a_band_of_twelve_at_the_code_s_two_ends_loads():
    """Codex's item 2 on repair 1: a band of twelve, six readings at 0 and six at 255, has a spread of 133.17 codes
    (the n - 1 divisor), more than half the code's range; it publishes [12, 1275, 1332] and loads, the ceiling read at
    its count (mutant: a fixed ceiling of 128 codes, which refused it); the reference states the same ceiling."""
    rows = 12 + 30
    values = bytes([0] * 6 + [255] * 6 + [100 + (row % 30) for row in range(30)])
    bands = bytes([0] * 12 + [1] * 30)
    columns = [chain_moments.Released("x", chain_moments.KIND_NUMBER, values, bytearray([1] * rows))]
    grouping = chain_moments.Grouping("g", bands, (12, 30), frozenset(), (0, 1))
    found, _counts = chain_moments.released(columns, [grouping], FLOOR)
    assert found["within"][0]["groups"][0] == [12, 1275, 1332]
    inputs = enumeration.loader_inputs(columns, [grouping])
    chain_check.check_moments(found, *inputs[:3], FLOOR, inputs[3], inputs[4])
    reference = _reference()
    for n in (2, 11, 12, 13, 40, 20000, 20001, 2000001):
        for scale in (10, 1000, 100000):
            assert chain_moments.spread_top(n, scale) == reference.spread_top(n, scale)
    assert chain_moments.spread_top(12, 10) == 1332


# -- THE PAIR'S OWN SPREADS: A COMPLETE-CASE SLOPE BESIDE UNSHARED BLANKS ------


def _codex_slope_table():
    """Codex's item 3 on repair 1, invented: 21,000 rows, x reads 0 to 20 then 100 to 120, 500 rows each value; y equals
    x on the first block and is blank on the second; a three-level group."""
    rows = []
    for block in (range(0, 21), range(100, 121)):
        for value in block:
            for place in range(500):
                rows += [[f"{value}", f"{value}" if block.start == 0 else "", "abc"[place % 3]]]
    return _csv(["x", "y", "g"], rows)


@pytest.fixture(scope="module")
def codex_slope(tmp_path_factory):
    folder = tmp_path_factory.mktemp("codexslope")
    table, document, chained = _describe(folder, _codex_slope_table(), name="codexslope")
    return folder, table, document, chained


def test_a_complete_case_slope_reads_the_pair_s_own_spreads(codex_slope):
    """The slope of y on x over the rows holding both, from the published numbers: r times the pair's spread of y over
    the pair's spread of x reads 6.0144 codes a code, the least-squares slope on those rows, where the columns' own
    spreads read 0.7212 (LANE MPp RULINGS 5 (2); mutant: no pair spreads); the description loads past 20,000 rows, each
    spread in the unit of its own count, and a spread over its range is refused at S42."""
    folder, table, document, chained = codex_slope
    moments = chained.statistical["moments"]
    pair = _pair(moments, "y", "x")
    assert pair[1] == 10500 and len(pair) == 3
    columns, groupings = _coded(table, document, chained.statistical)
    reference = _reference()
    assert reference.describe(columns, groupings, FLOOR)[0] == moments
    values = {name: vals for name, _kind, vals in columns}
    exact = reference.slope(values["x"], values["y"])
    published = reference.published_slope(moments, "x", "y")
    assert round(float(exact), 4) == 6.0144 and abs(published - exact) < Fraction(1, 10**4)
    own = {entry["column"]: entry for entry in moments["columns"]}
    by_columns = Fraction(pair[0], 10**12) * Fraction(own["y"]["sd"], 1000) / Fraction(own["x"]["sd"], 10000)
    assert round(float(by_columns), 4) == 0.7212
    assert _loads(folder, document, chained.statistical, name="codexslope_loaded") is not None
    statistical = json.loads(json.dumps(chained.statistical))
    statistical["moments"]["columns"][0]["sd"] = chain_moments.spread_top(21000, 10000) + 1
    with pytest.raises(errors.ProfileError) as refused:
        _loads(folder, document, statistical, name="codexslope_over")
    assert "S42" in str(refused.value) and "the sd is a whole number" in str(refused.value)


def test_a_simple_slope_s_rounding_is_a_tenth_of_its_standard_error_up_to_r_0_999():
    """The verify's simulation (item 2 on repair 1): at 20,000 rows, spreads of 40 to 70 codes in the column's unit and
    r on its grid of z, the simple slope r * sd_y / sd_x is off its unrounded value by at most a tenth of its standard
    error, sqrt((1 - r ** 2) / (n - 2)) * sd_y / sd_x, at the 95th percentile, at every |r| up to 0.999 (mutant: the
    column's spread in tenths, which reached 4.65 at r = 0.999)."""
    draw = random.Random(17)
    n = 20000
    spread_unit = chain_moments.unit(chain_moments.SCALE_COLUMN_SPREAD, n)
    z_unit = chain_moments.unit(chain_moments.SCALE_FISHER_Z, n)
    for r in (0.9, 0.95, 0.99, 0.995, 0.999):
        ratios = []
        for _draw in range(4000):
            z = math.atanh(r) + draw.uniform(-0.5, 0.5) / z_unit
            truth = math.tanh(z)
            sd_x, sd_y = draw.uniform(40, 70), draw.uniform(40, 70)
            printed = math.tanh(math.floor(z * z_unit + 0.5) / z_unit)
            shown_x = math.floor(sd_x * spread_unit + 0.5) / spread_unit
            shown_y = math.floor(sd_y * spread_unit + 0.5) / spread_unit
            error = abs(printed * shown_y / shown_x - truth * sd_y / sd_x)
            ratios += [error / (math.sqrt((1 - truth * truth) / (n - 2)) * sd_y / sd_x)]
        ratios.sort()
        assert ratios[int(0.95 * len(ratios))] <= 0.1, (r, ratios[int(0.95 * len(ratios))])


# -- THE COMMAND'S FAIL-SAFE ----------------------------------------------------


def test_the_command_never_writes_moments_its_loader_refuses(tmp_path, monkeypatch, capsys):
    """Where the chain's check refuses a description with its moments and passes it without them, `synthtwin profile`
    writes it without the moments and says why in a caution, on the screen and as the summary file's last line (LANE
    MPp RULINGS 6 (1) and 7 (3); mutants: the refusal unread, which wrote moments the loader refuses; the summary's
    line dropped). No other gate case needs this: the round trip passes without it."""

    def refuse(*_args, **_kwargs):
        raise errors.ProfileError("a refusal written for this test.")

    monkeypatch.chdir(tmp_path)
    fixtures.write(tmp_path, "failsafe.csv", _clinic(n_rows=1500, seed=4))
    monkeypatch.setattr(chain_check, "check_moments", refuse)
    capsys.readouterr()
    assert cli.main(["profile", "failsafe.csv"], chain=cli.ChainRun(folder=str(tmp_path / "data")), small_tables_refused=False) == 0
    said = capsys.readouterr().err
    document = json.loads((tmp_path / "failsafe-profile.json").read_text(encoding="utf-8"))
    statistical = document["relationships"]["statistical"]
    assert statistical is not None and statistical["moments"] is None and statistical["chain"]
    assert "the moments (means, spreads, correlations and shares) were left out" in said and "a refusal written for this test." in said
    written = (tmp_path / "failsafe-profile.txt").read_text(encoding="utf-8").splitlines()
    assert written[-1].startswith("Between columns: the moments (means, spreads, correlations and shares) were left out")
    assert written[-1].endswith("a refusal written for this test. The family tables stand.")
    monkeypatch.undo()
    assert contract.load_profile(str(tmp_path / "failsafe-profile.json"), chain=True) is not None


# -- K-S6-08's MOMENT FIXTURES UNDER RULE B: EXHAUSTIVE ENUMERATION ------------


@pytest.mark.parametrize("floor, largest", [(3, 7), (11, 12)])
def test_no_published_moment_implies_a_small_count_directly(floor, largest):
    """Exhaustive over every two-band split of a binary and of a number, every band holding an own-fact group (W1),
    every `L2` reading of three `L1` bands, every presence table of two numbers (both, the first alone, the second alone,
    neither) and every binary: no published moment holds a direct count of 1 to f - 1 (mutants: the level, the absent
    rows', the readings', W1's, the outside readings' and the neither cell's checks each dropped, each leaking). The
    driver runs the wider enumeration for `K-S6-08`."""
    binary = enumeration.shares(floor, largest)
    number = enumeration.shares(floor, largest, chain_moments.KIND_NUMBER)
    w1_one = enumeration.shares(floor, largest, small=frozenset({0}), counts=enumeration.w1_counts(floor))
    w1_both = enumeration.shares(floor, largest, small=frozenset({0, 1}), counts=enumeration.w1_counts(floor))
    coarse = enumeration.coarse(floor, enumeration._coarse_counts(floor))
    coarse_number = enumeration.coarse(floor, enumeration._coarse_counts(floor), chain_moments.KIND_NUMBER)
    pair = enumeration.pairs(floor, floor + 2)
    own = enumeration.columns(floor, 3 * floor)
    for found in (binary, number, w1_one, w1_both, coarse, coarse_number, pair, own):
        assert found["published"] > 0 and found["leaking"] == 0, found
    # The loader's S41 reads back every presence table the product publishes, in both pair orders.
    assert pair["loader_refused"] == 0, pair
    assert coarse["coarser"] > 0 and coarse_number["coarser"] > 0
    assert enumeration.shares(floor, largest, drop="ones")["leaking"] > 0
    assert enumeration.shares(floor, largest, drop="absent")["leaking"] > 0
    assert enumeration.shares(floor, largest, chain_moments.KIND_NUMBER, drop="readings")["leaking"] > 0
    assert enumeration.shares(floor, largest, drop="W1", small=frozenset({0}), counts=enumeration.w1_counts(floor))["leaking"] > 0
    assert enumeration.pairs(floor, floor + 2, drop="outside")["leaking"] > 0
    assert enumeration.pairs(floor, floor + 2, drop="neither")["leaking"] > 0


# -- THE PAGE: THE AMENDMENT'S SENTENCES --------------------------------------


def _amendment():
    text = CONTRACT.read_text(encoding="utf-8")
    start = text.index("#### 4.6d.0 ")
    end = text.index("#### 4.6d.1 ")
    return " ".join(text[start:end].split())


def test_the_amendment_states_rule_b_and_its_limit():
    """Contract 4.6d.0 states the owner's rule, its units, its floor, what it supersedes, the residual the owner accepted
    and MPg's interface, with repair 2's pair spreads, units, yardstick, loader checks and fail-safe, and the finer grid
    of z of LANE MPp RULINGS 7 with its exact grid check and its collinear measurement (mutants: any sentence dropped)."""
    page = _amendment()
    for sentence in (
        "the owner's answer \"B\" of Monday 2026-11-02",
        "computed over at least `f` people",
        "every count it implies DIRECTLY is 0 or at least `f`",
        "R10's strict proof no longer governs these moments, and ruling R12 (slopes withheld) is withdrawn",
        "A mean and a standard deviation in tenths of a code",
        "a share in ten-thousandths",
        "a correlation on its grid of Fisher's z, ten-thousandths of z",
        "EVERY UNIT FOLLOWS ITS OWN COUNT",
        "all FOUR cells of a pair's presence table",
        "no tail value enters a moment",
        "THE RESIDUAL THE OWNER ACCEPTED",
        "the COUNT of the people between them is known exactly",
        "EACH FIGURE NAMED BY ITS PATH",
        "projects such a target to the nearest positive semidefinite matrix",
        "The generator does not yet read them",
        # Repair 2 (LANE MPp RULINGS 5 and 6).
        "a column's and a pair's standard deviation in thousandths of a code",
        "the pair's own two standard deviations over the `n` rows",
        "the pair's spread of `Y` over the pair's spread of `X`",
        "THE YARDSTICK IS THE NORMAL MODEL'S",
        "the total-variance identity",
        "THE COMMAND'S FAIL-SAFE",
        "THE ROUND TRIP",
        "STATED LIMITS, DERIVED STATISTICS",
        # The finer grid of z (LANE MPp RULINGS 7).
        "THE FINER GRID OF Z",
        "compared on the grid integer",
        "a coefficient between two collinear predictors on the product's own `released`",
    ):
        assert sentence in page, sentence
    assert "No proof is required beyond (2) and (3)." in page
    assert "MEASURED_" not in page
