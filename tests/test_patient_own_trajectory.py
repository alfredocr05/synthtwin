"""A patient's own trajectory: rounded, floor-gated moments of a repeated number or date column (lane GRb2-c, plan P4-D491 part c; contract 4.6c.15, method G16.20; NOT IN FORCE while the layer's sub-switch is off).

THE GATE OF LANE GRb2-c. Where the patient layer stands, each repeated
number column and each dealt date column publishes its level, slope and
serial term over a patient's positions as rounded moments of rule B on its
normal-score scale, grouped by the patient-fixed columns of the patient
chain, and the patient walk deals the column's cells in the order of the
scores those moments give. This file holds, each rule red on its mutant
(named beside each case; the lane's mutation script runs them):

- THE MOMENTS: on invented trajectories of KNOWN level, slope and serial
  spread, trend, curve and trend by group, the producer's moments come back
  within about three times their sampling error, on the position axis and
  on the years axis of irregular visits;
- THE ROUND TRIP: the generator's scores, drawn from an entry, give the
  entry back;
- NO COUNT: an entry holds its nine keys and every moment is a decimal
  text, no whole number anywhere; it stands only where twice the floor of
  patients hold four consecutive readings, a grouping column only where
  each band holds that many patients of two readings;
- S35: the loader refuses every broken entry, and the layer's other keys
  stay exactly its own;
- THE TWIN: an invented visit table described behind the switch carries
  its between-patient spread, its trend by arm, its slope spread and its
  serial correlation on the twin, every published patient fact held, and
  no twin patient's readings equal to a real patient's;
- THE RUN: a visit number's whole-number run goes on past its list.

Every fixture is invented here; the key is a fixed test key.
"""

import copy
import dataclasses
import fractions
import json
import math
import pathlib
import random
import sys

import pytest

import fixtures

from synthtwin import chain, chain_walk, contract, errors, generation, patient_trajectory, patient_walk, profile, reading, taxonomy, twinstore

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools" / "measurements"))

import kpi_patient_twin  # noqa: E402

KEY = bytes(range(32))
FLOOR = 11
# The invented trajectories' truths, on their own scale.
TRUTH = {"level_sd": 0.7, "slope_sd": 0.04, "corr": -0.3, "noise_sd": 0.45, "lag1": 0.5, "trend": -0.02,
         "curve": 0.0004, "shift": 0.1, "by_trend": -0.04, "by_curve": -0.0012}
# About three and a half times each moment's spread over five draws of 2,000 patients on the years axis of gamma
# gaps, the wider of the two axes (the lane's measurement).
TOLERANCE = {"level_sd": 0.11, "slope_sd": 0.026, "corr": 0.56, "noise_sd": 0.08, "lag1": 0.14, "trend": 0.035,
             "curve": 0.0021, "shift": 0.15, "by_trend": 0.061, "by_curve": 0.0042}


def _trajectories(seed: int, patients: int, longest: int = 30, years: bool = False,
                  truth: "dict[str, float] | None" = None, pace: float = 1.0) -> "tuple[list[float | None], list[list[int]], list[int], list[float | None]]":
    """Invented readings of KNOWN trajectories (`TRUTH`): each patient's rows in position order, its arm (0 or 1), and each
    row's time: its position, or with `years` the years since the patient's first visit, gaps of a gamma's draw (mean `pace` years)."""
    r = random.Random(seed)
    values: "list[float | None]" = []
    rows: "list[list[int]]" = []
    arm: "list[int]" = []
    times: "list[float | None]" = []
    t = TRUTH if truth is None else truth
    for _patient in range(patients):
        count = 1 + min(longest - 1, int(r.expovariate(1.0 / 7.0)))
        group = 1 if r.random() < 0.5 else 0
        arm += [group]
        z0, z1 = r.gauss(0.0, 1.0), r.gauss(0.0, 1.0)
        b0 = t["level_sd"] * z0
        b1 = t["slope_sd"] * (t["corr"] * z0 + math.sqrt(1.0 - t["corr"] ** 2) * z1)
        noise = 0.0
        clock = 0.0
        held: "list[int]" = []
        for j in range(count):
            if years and j > 0:
                clock += r.gammavariate(2.0, pace / 2.0)
            at = clock if years else float(j)
            shock = r.gauss(0.0, t["noise_sd"])
            noise = shock if j == 0 else t["lag1"] * noise + math.sqrt(1.0 - t["lag1"] ** 2) * shock
            held += [len(values)]
            times += [at]
            values += [t["shift"] * group + b0 + (t["trend"] + t["by_trend"] * group + b1) * at
                       + (t["curve"] + t["by_curve"] * group) * at * at + noise]
        rows += [held]
    return values, rows, arm, times


def _arm(arm: "list[int]") -> "list[patient_trajectory.Grouping]":
    return patient_trajectory.grouping_levels("arm", (arm, arm, arm), (2, 2, 2))


def _read(entry: "dict[str, object]") -> "dict[str, float]":
    by = entry["by"]
    assert isinstance(by, list) and len(by) == 1
    out = {key: float(fractions.Fraction(f"{entry[key]}")) for key in ("level_sd", "slope_sd", "corr", "noise_sd", "lag1", "trend", "curve")}
    out["shift"] = float(fractions.Fraction(by[0]["shift"][1]))
    out["by_trend"] = float(fractions.Fraction(by[0]["trend"][1]))
    out["by_curve"] = float(fractions.Fraction(by[0]["curve"][1]))
    return out


@pytest.fixture(scope="module")
def known() -> "dict[str, object]":
    """The producer's entry of 2,000 invented patients of known trajectories, on their own scale."""
    values, rows, arm, _times = _trajectories(3, 2000)
    entry = patient_trajectory.from_scores("y", values, rows, _arm(arm), FLOOR)
    assert entry is not None
    return entry


# -- THE MOMENTS ----------------------------------------------------------------------------------


def test_the_moments_of_known_trajectories_come_back(known):
    """MUTANTS: the lag-one coefficient read as nought; the slope variance left with its noise; the fixed part's change a position dropped."""
    got = _read(known)
    assert known["axis"] == "position"
    for key, truth in TRUTH.items():
        assert abs(got[key] - truth) <= TOLERANCE[key], (key, got[key], truth)


def test_the_level_spread_is_read_apart_from_the_serial_noise():
    """MUTANT: the products of two readings left with their noise part. A small level beside a loud, serially correlated noise."""
    loud = dict(TRUTH, level_sd=0.3, noise_sd=0.9, lag1=0.6, slope_sd=0.02, corr=0.0)
    values, rows, arm, _times = _trajectories(10, 2000, truth=loud)
    got = _read(patient_trajectory.from_scores("y", values, rows, _arm(arm), FLOOR))  # type: ignore[arg-type]
    assert abs(got["level_sd"] - 0.3) <= 0.12 and abs(got["noise_sd"] - 0.9) <= 0.08 and abs(got["lag1"] - 0.6) <= 0.1, got


def test_the_axis_on_which_each_patient_s_line_leaves_less_is_chosen():
    """MUTANT: the years taken whatever their lines leave. A pressure linear in its visits beside dates jittered about a
    monthly step reads its positions; one linear in years beside gaps of a gamma's draw reads its years."""
    by_visits, rows, arm, _times = _trajectories(11, 1500)
    stream = random.Random(12)
    monthly: "list[float | None]" = [None for _value in by_visits]
    for held in rows:
        for j in range(len(held)):
            monthly[held[j]] = j * 0.08 + stream.uniform(-0.04, 0.04) if j else 0.0
    on_positions = patient_trajectory.from_scores("y", by_visits, rows, _arm(arm), FLOOR)
    in_years = patient_trajectory.from_scores("y", by_visits, rows, _arm(arm), FLOOR, monthly)
    by_position, by_date = patient_trajectory.line_misfit(by_visits, rows), patient_trajectory.line_misfit(by_visits, rows, monthly)
    assert by_position < by_date
    assert patient_trajectory.chosen(on_positions, in_years, by_position, by_date) is on_positions
    by_years, rows, arm, gaps = _trajectories(13, 1500, years=True)
    on_positions = patient_trajectory.from_scores("y", by_years, rows, _arm(arm), FLOOR)
    in_years = patient_trajectory.from_scores("y", by_years, rows, _arm(arm), FLOOR, gaps)
    by_position, by_date = patient_trajectory.line_misfit(by_years, rows), patient_trajectory.line_misfit(by_years, rows, gaps)
    assert by_date < by_position
    assert patient_trajectory.chosen(on_positions, in_years, by_position, by_date) is in_years
    assert patient_trajectory.chosen(None, in_years) is in_years and patient_trajectory.chosen(on_positions, None) is on_positions


def test_the_linear_scale_standardizes_the_readings():
    readings = [fractions.Fraction(3), None, fractions.Fraction(1), fractions.Fraction(5)]
    scores = patient_trajectory.linear_scores(readings)
    assert scores[1] is None and scores[2] == -1.0 and scores[0] == 0.0 and scores[3] == 1.0
    assert patient_trajectory.linear_scores([fractions.Fraction(2), fractions.Fraction(2)]) == [None, None]


def test_the_years_axis_reads_the_change_a_year_on_irregular_visits():
    """MUTANT: the producer reading positions where it is handed years. The same readings on times halved read a change
    twice as steep, a curve four times and a slope spread twice, and nothing else moves."""
    values, rows, arm, times = _trajectories(8, 2000, years=True)
    entry = patient_trajectory.from_scores("y", values, rows, _arm(arm), FLOOR, times)
    assert entry is not None and entry["axis"] == "years"
    got = _read(entry)
    for key, truth in TRUTH.items():
        assert abs(got[key] - truth) <= TOLERANCE[key], (key, got[key], truth)
    halved = patient_trajectory.from_scores("y", values, rows, _arm(arm), FLOOR, [None if t is None else 0.5 * t for t in times])
    assert halved is not None
    half = _read(halved)
    assert abs(half["trend"] - 2 * got["trend"]) <= 0.0003 and abs(half["by_trend"] - 2 * got["by_trend"]) <= 0.0003
    assert abs(half["curve"] - 4 * got["curve"]) <= 0.00001 and abs(half["slope_sd"] - 2 * got["slope_sd"]) <= 0.0003
    assert (half["level_sd"], half["noise_sd"], half["lag1"]) == (got["level_sd"], got["noise_sd"], got["lag1"])


def test_the_normal_scores_are_mid_ranks_through_the_shared_quantile():
    readings = [fractions.Fraction(3), None, fractions.Fraction(1), fractions.Fraction(3), fractions.Fraction(2)]
    scores = patient_trajectory.normal_scores(readings)
    assert scores[1] is None
    assert scores[2] == chain_walk.normal_score(0.5 / 4) and scores[4] == chain_walk.normal_score(1.5 / 4)
    assert scores[0] == scores[3] == chain_walk.normal_score(3.0 / 4)


def test_a_moment_is_rounded_half_away_from_nought_to_its_places():
    assert patient_trajectory.rounded_text(0.12345, 4) == "0.1235" and patient_trajectory.rounded_text(-0.12345, 4) == "-0.1235"
    assert patient_trajectory.rounded_text(0.00004, 4) == "0" and patient_trajectory.rounded_text(-0.00004, 4) == "0"
    assert patient_trajectory.rounded_text(2.5, 0) == "3" and patient_trajectory.rounded_text(0.1, 3) == "0.1"


# -- THE ROUND TRIP -------------------------------------------------------------------------------


def _drawn(entry: "dict[str, object]", r_values: "list[int]", arm: "list[int]", seed: int, times: "list[float] | None" = None) -> "list[float]":
    read = patient_trajectory.entries_of({"trajectory": [entry]})[0]
    count = patient_trajectory.words_needed(1, len(r_values), sum(r_values))
    words = chain_walk.packed(count, 8)
    stream = random.Random(seed)
    for at in range(count):
        chain_walk.put(words, at, stream.getrandbits(64))
    return patient_trajectory.scores(read, r_values, {"arm": arm}, words, 0, None, times)


def test_the_generator_draws_an_entry_in_years_back_on_its_own_times():
    """MUTANT: the scores reading positions where they are handed times."""
    values, rows, arm, times = _trajectories(9, 2000, years=True)
    entry = patient_trajectory.from_scores("y", values, rows, _arm(arm), FLOOR, times)
    assert entry is not None
    r_values = [len(one) for one in rows]
    # The twin's own times, half a year a visit on average (the table's are a year): its scores read them, not its positions.
    laid_times = [0.5 * float(times[k]) for held in rows for k in held]  # type: ignore[arg-type]
    scores = _drawn(entry, r_values, arm, 12, laid_times)
    at = 0
    laid: "list[list[int]]" = []
    for count in r_values:
        laid += [list(range(at, at + count))]
        at += count
    back = patient_trajectory.from_scores("y", list(scores), laid, _arm(arm), FLOOR, list(laid_times))
    assert back is not None
    want = _read(entry)
    got = _read(back)
    for key in TRUTH:
        assert abs(got[key] - want[key]) <= TOLERANCE[key], (key, got[key], want[key])


# An entry of strong curves, so a twin that drops them is seen (the round trip's own entry).
DRAWN = {"axis": "position", "by": [{"column": "arm", "curve": ["0", "-0.004"], "level": "L0", "shift": ["0", "0.1"],
                                     "trend": ["0", "-0.04"]}],
         "column": "y", "corr": "-0.3", "curve": "0.002", "lag1": "0.5", "level_sd": "0.7", "noise_sd": "0.45",
         "slope_sd": "0.04", "trend": "-0.02"}


def test_the_generator_draws_its_entry_back():
    """MUTANTS: the level's hidden score dropped; the slope's random part dropped; the serial term dropped; a band's change a position dropped; the curve dropped."""
    _values, rows, arm, _times = _trajectories(4, 2000)
    r_values = [len(one) for one in rows]
    known = DRAWN
    scores = _drawn(known, r_values, arm, 11)
    at = 0
    laid: "list[list[int]]" = []
    for count in r_values:
        laid += [list(range(at, at + count))]
        at += count
    back = patient_trajectory.from_scores("y", list(scores), laid, _arm(arm), FLOOR)
    assert back is not None
    want = _read(known)
    got = _read(back)
    for key in TRUTH:
        assert abs(got[key] - want[key]) <= TOLERANCE[key], (key, got[key], want[key])


# -- NO COUNT, AND THE FLOOR ----------------------------------------------------------------------


def _leaves(value: object) -> "list[object]":
    if isinstance(value, dict):
        return [leaf for key in sorted(value) for leaf in _leaves(value[key])]
    if isinstance(value, list):
        return [leaf for one in value for leaf in _leaves(one)]
    return [value]


def test_an_entry_publishes_no_count(known):
    """MUTANT: the entry written with the patients it read."""
    assert sorted(known) == list(patient_trajectory.ENTRY_KEYS)
    for group in known["by"]:  # type: ignore[union-attr]
        assert sorted(group) == list(patient_trajectory.BY_KEYS)
    for leaf in _leaves(known):
        assert isinstance(leaf, str), leaf
        if leaf not in ("position", "years", "linear", "normal", "y", "arm", "L0", "L1", "L2"):
            exact = fractions.Fraction(leaf)
            assert abs(exact) <= 10 and (exact * 10 ** 6).denominator == 1, leaf


def _short_table(reaching: int, extra_short: int) -> "tuple[list[float | None], list[list[int]], list[int]]":
    """`reaching` patients of four consecutive readings and `extra_short` of three, each arm alike."""
    r = random.Random(5)
    values: "list[float | None]" = []
    rows: "list[list[int]]" = []
    arm: "list[int]" = []
    for patient in range(reaching + extra_short):
        count = 4 if patient < reaching else 3
        held = []
        for _j in range(count):
            held += [len(values)]
            values += [r.gauss(0.0, 1.0)]
        rows += [held]
        arm += [patient % 2]
    return values, rows, arm


def test_an_entry_stands_only_where_twice_the_floor_of_patients_hold_four_consecutive_readings():
    """MUTANT: the floor's multiple taken as nought."""
    least = patient_trajectory.FLOOR_TIMES * FLOOR
    values, rows, arm = _short_table(least - 1, 500)
    assert patient_trajectory.from_scores("y", values, rows, _arm(arm), FLOOR) is None
    values, rows, arm = _short_table(least, 500)
    assert patient_trajectory.from_scores("y", values, rows, _arm(arm), FLOOR) is not None
    # A reading missing in the middle breaks a run: four rows with a blank second hold no four consecutive readings.
    values, rows, arm = _short_table(least + 40, 0)
    for held in rows:
        values[held[1]] = None
    assert patient_trajectory.from_scores("y", values, rows, _arm(arm), FLOOR) is None


def test_a_grouping_column_stands_only_where_each_band_holds_twice_the_floor():
    """MUTANT: a band's patients left uncounted."""
    least = patient_trajectory.FLOOR_TIMES * FLOOR
    values, rows, _arm_bands, _times = _trajectories(6, 600)
    for few in (least - 1, least):
        # The second band holds `few` patients of two readings or more and every patient of one reading.
        bands = [0 for _patient in rows]
        taken = 0
        for patient in range(len(rows)):
            if len(rows[patient]) < 2:
                bands[patient] = 1
            elif taken < few:
                bands[patient] = 1
                taken += 1
        entry = patient_trajectory.from_scores("y", values, rows, _arm(bands), FLOOR)
        assert entry is not None
        kept = [group["column"] for group in entry["by"]]  # type: ignore[union-attr]
        assert kept == (["arm"] if few >= least else []), (few, kept)


def test_a_grouping_column_is_read_at_its_finest_level_that_holds():
    values, rows, _arm_bands, _times = _trajectories(7, 1200)
    fine = [patient % 4 for patient in range(len(rows))]
    coarse = [band // 2 for band in fine]
    tiny = [0 if patient % 300 else 1 for patient in range(len(rows))]
    groupings = patient_trajectory.grouping_levels("ward", (fine, coarse, coarse), (4, 2, 2))
    entry = patient_trajectory.from_scores("y", values, rows, groupings, FLOOR)
    assert entry is not None and entry["by"][0]["level"] == "L0" and len(entry["by"][0]["shift"]) == 4  # type: ignore[index]
    groupings = patient_trajectory.grouping_levels("ward", (tiny, coarse, coarse), (2, 2, 2))
    entry = patient_trajectory.from_scores("y", values, rows, groupings, FLOOR)
    assert entry is not None and entry["by"][0]["level"] == "L1"  # type: ignore[index]


# -- S35: THE LOADER --------------------------------------------------------------------------------


def _loader_case() -> "tuple[dict[str, object], dict[str, str], dict[str, str], dict[str, tuple[int, int, int]], set[str]]":
    entry = {"axis": "years", "by": [{"column": "arm", "curve": ["0", "-0.0012"], "level": "L2", "shift": ["0", "-0.1"],
                                      "trend": ["0", "-0.04"]}],
             "column": "sbp", "corr": "-0.25", "curve": "0.000412", "lag1": "0.48", "level_sd": "0.76", "noise_sd": "0.46",
             "scale": "normal", "slope_sd": "0.0273", "trend": "-0.0287"}
    dated = dict(entry, column="seen", by=[], axis="position", scale="linear")
    grain = {"position": "seen", "trajectory": [dated, entry]}
    classes = {"pid": "person", "arm": "patient_fixed", "seen": "dealt_date", "sbp": "repeated", "flag": "repeated"}
    roles = {"pid": "identifier", "arm": "categorical", "seen": "datetime", "sbp": "continuous", "flag": "categorical"}
    return grain, classes, roles, {"arm": (2, 2, 2)}, set()


def _damaged(change) -> "dict[str, object]":
    grain, _classes, _roles, _bands, _counted = _loader_case()
    out = copy.deepcopy(grain)
    change(out["trajectory"])
    return out


DAMAGES = {
    "a count beside the moments": lambda entries: entries[1].update(n=1200),
    "an empty list": lambda entries: entries.clear(),
    "a patient-fixed column": lambda entries: entries[1].update(column="arm"),
    "a label column": lambda entries: entries[1].update(column="flag"),
    "two entries of one column": lambda entries: entries.append(copy.deepcopy(entries[1])),
    "out of schema order": lambda entries: entries.reverse(),
    "another axis": lambda entries: entries[1].update(axis="days"),
    "a date read in years": lambda entries: entries[0].update(axis="years"),
    "a date on the normal scale": lambda entries: entries[0].update(scale="normal"),
    "a scale that is not one": lambda entries: entries[1].update(scale="log"),
    "a curve written past its places": lambda entries: entries[1].update(curve="0.0000001"),
    "a curve past ten": lambda entries: entries[1].update(curve="-12"),
    "a band's curve missing": lambda entries: entries[1]["by"][0].update(curve=["0"]),
    "a spread below nought": lambda entries: entries[1].update(level_sd="-0.1"),
    "a spread written past its places": lambda entries: entries[1].update(noise_sd="0.4567"),
    "a moment in exponent form": lambda entries: entries[1].update(slope_sd="2e-2"),
    "a moment as a fraction": lambda entries: entries[1].update(trend="-1/50"),
    "a moment as a number": lambda entries: entries[1].update(lag1=0.48),
    "a correlation past its bound": lambda entries: entries[1].update(corr="0.99"),
    "a lag past its top": lambda entries: entries[1].update(lag1="0.97"),
    "a lag past its foot": lambda entries: entries[1].update(lag1="-0.95"),
    "a change past ten": lambda entries: entries[1].update(trend="11"),
    "a grouping column that is not patient-fixed": lambda entries: entries[1]["by"][0].update(column="sbp"),
    "a grouping column twice": lambda entries: entries[1]["by"].append(copy.deepcopy(entries[1]["by"][0])),
    "a level that is not one": lambda entries: entries[1]["by"][0].update(level="L3"),
    "a band too few": lambda entries: entries[1]["by"][0].update(shift=["0"]),
    "a first band not nought": lambda entries: entries[1]["by"][0].update(trend=["0.1", "-0.04"]),
    "a grouping key too many": lambda entries: entries[1]["by"][0].update(n=33),
}


def test_the_loader_reads_a_sound_entry_and_refuses_every_broken_one():
    """MUTANT: S35 returning at once."""
    grain, classes, roles, bands, counted = _loader_case()
    patient_trajectory.checked(grain, classes, roles, bands, counted)
    read = patient_trajectory.entries_of(grain)
    assert [one.column for one in read] == ["seen", "sbp"] and read[1].by[0].level == 2 and read[1].lag1 == 0.48
    assert read[1].axis == "years" and read[0].axis == "position" and read[1].curve == 0.000412 and read[1].by[0].curve == (0.0, -0.0012)
    for name, change in DAMAGES.items():
        with pytest.raises(errors.ProfileError, match="S35") as refused:
            patient_trajectory.checked(_damaged(change), classes, roles, bands, counted)
        assert refused is not None, name
    with pytest.raises(errors.ProfileError, match="S35"):
        patient_trajectory.checked(grain, classes, roles, bands, {"sbp"})
    # The years beside no dated position column are refused; the positions stand beside one.
    undated = copy.deepcopy(grain)
    del undated["position"]
    with pytest.raises(errors.ProfileError, match="S35"):
        patient_trajectory.checked(undated, classes, roles, bands, counted)
    on_positions = copy.deepcopy(grain)
    on_positions["trajectory"][1]["axis"] = "position"  # type: ignore[index]
    patient_trajectory.checked(on_positions, classes, roles, bands, counted)


# -- THE TWIN -------------------------------------------------------------------------------------


VISIT_HEADER = ["pid", "arm", "age", "visit", "seen", "sbp", "flag", "loss"]


def _visit_rows(patients: int, seed: int) -> "list[list[str]]":
    """An invented visit table: an arm and an age fixed a patient, visits a month apart, a pressure with a random level and slope, an arm-by-visit trend and serially correlated noise."""
    r = random.Random(seed)
    out: "list[list[str]]" = []
    for patient in range(patients):
        count = 1 + min(23, int(r.expovariate(1.0 / 6.0)))
        group = "B" if r.random() < 0.5 else "A"
        age = int(min(85, max(30, r.gauss(58.0, 11.0))))
        b0 = r.gauss(0.0, 11.0)
        b1 = r.gauss(0.0, 0.5)
        day = 18263 + r.randrange(900)
        noise = 0.0
        for j in range(count):
            shock = r.gauss(0.0, 7.0)
            noise = shock if j == 0 else 0.5 * noise + math.sqrt(0.75) * shock
            sbp = 132.0 + b0 + 0.12 * (age - 58) + (-0.3 - (0.7 if group == "B" else 0.0) + b1) * j + noise
            seen = f"{_civil(day)}"
            loss = int(math.exp(r.gauss(5.0, 1.1) + 0.02 * j))
            out += [[f"Q{100000 + 7 * patient}", group, f"{age}", f"{j + 1}", seen, f"{int(round(sbp))}",
                     "Y" if r.random() < 0.3 else "N", f"{loss}"]]
            day += 26 + r.randrange(9)
    return out


def _civil(days: int) -> str:
    """Days from 1970-01-01 as a date (Howard Hinnant's civil-from-days)."""
    z = days + 719468
    era = z // 146097
    doe = z - era * 146097
    yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
    y = yoe + era * 400
    doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
    mp = (5 * doy + 2) // 153
    d = doy - (153 * mp + 2) // 5 + 1
    m = mp + 3 if mp < 10 else mp - 9
    return f"{y + (1 if m <= 2 else 0):04d}-{m:02d}-{d:02d}"


def _described(folder: pathlib.Path, rows: "list[list[str]]", trajectories: bool = True) -> pathlib.Path:
    path = folder / "visits.csv"
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(",".join(VISIT_HEADER) + "\n")
        for row in rows:
            handle.write(",".join(row) + "\n")
    settings = dataclasses.replace(taxonomy.Settings(small_cell_floor=FLOOR), person_columns=("pid",))
    table = reading.read_table(str(path), small_cell_floor=FLOOR)
    document = profile.build_document(table, settings, ["pid"], [], [], subjects=["pid"], top_code=True)
    chained = chain.describe(table, document, settings, chain.ChainSwitch("visits", KEY, rows_per_person=chain.ROWS_PERSON,
                                                                           trajectories=trajectories))
    assert chained.grain is not None and chained.statistical is not None and chained.columns is not None
    floored = kpi_patient_twin.floor_cells(chained.statistical, chained.grain, FLOOR)
    assert floored == {"patient_cells_1_to_f_minus_1": 0, "row_cells_1_to_f_minus_1": 0}, floored
    switched = json.loads(json.dumps(document))
    switched["relationships"]["statistical"] = chained.statistical
    switched["relationships"]["grain"] = chained.grain
    switched["columns"] = chained.columns
    return fixtures.write_profile(folder, "visits-profile.json", switched)


@pytest.fixture(scope="module")
def visits(tmp_path_factory) -> "tuple[pathlib.Path, list[list[str]]]":
    rows = _visit_rows(1400, 2)
    return _described(tmp_path_factory.mktemp("trajectory"), rows), rows


@pytest.fixture(scope="module")
def visit_twin(visits) -> "tuple[contract.Profile, generation.Twin, list[list[str]]]":
    path, _rows = visits
    loaded = contract.load_profile(str(path), chain=True)
    made = generation.generate_held(loaded, 7)
    held = made.held_columns if made.held_columns is not None else ()
    columns = [twinstore.column_cells(one) for one in held]
    return loaded, made, [list(row) for row in zip(*columns)]


def _patients(rows: "list[list[str]]") -> "dict[str, list[list[str]]]":
    out: "dict[str, list[list[str]]]" = {}
    for row in rows:
        out.setdefault(row[0], []).append(row)
    for key in out:
        out[key].sort(key=lambda row: (row[4], int(row[3]) if row[3].strip() else 0))
    return out


def _shape(rows: "list[list[str]]") -> "dict[str, float]":
    """The per-patient shape of a visit table: between-patient share, the slope a visit by arm, the slope spread, the lag-one residual correlation."""
    patients = _patients(rows)
    values = [float(row[5]) for row in rows]
    grand = sum(values) / len(values)
    total = sum((v - grand) ** 2 for v in values) / len(values)
    means: "list[float]" = []
    slopes: "dict[str, list[float]]" = {"A": [], "B": []}
    long_slopes: "list[float]" = []
    pairs: "list[tuple[float, float]]" = []
    for held in patients.values():
        ys = [float(row[5]) for row in held]
        if len(ys) >= 4:
            means += [sum(ys) / len(ys)]
        if len(ys) >= 3:
            js = list(range(len(ys)))
            jb = sum(js) / len(js)
            yb = sum(ys) / len(ys)
            sxx = sum((j - jb) ** 2 for j in js)
            slope = sum((j - jb) * (y - yb) for j, y in zip(js, ys)) / sxx
            slopes[held[0][1]] += [slope]
            if len(ys) >= 8:
                long_slopes += [slope]
            if len(ys) >= 6:
                resid = [y - yb - slope * (j - jb) for j, y in zip(js, ys)]
                pairs += list(zip(resid[:-1], resid[1:]))
    mean_of_means = sum(means) / len(means)
    between = sum((m - mean_of_means) ** 2 for m in means) / len(means)
    a = [p for p, _q in pairs]
    b = [q for _p, q in pairs]
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b)) / len(a)
    lag = cov / math.sqrt((sum((x - ma) ** 2 for x in a) / len(a)) * (sum((y - mb) ** 2 for y in b) / len(b)))
    mean_long = sum(long_slopes) / len(long_slopes)
    return {
        "between_share": between / total,
        "slope_a": sum(slopes["A"]) / len(slopes["A"]),
        "slope_b": sum(slopes["B"]) / len(slopes["B"]),
        "slope_sd_long": math.sqrt(sum((s - mean_long) ** 2 for s in long_slopes) / len(long_slopes)),
        "lag_one": lag,
    }


def test_the_layer_publishes_an_entry_for_the_pressure_and_the_dates_and_no_derived_column_of_them(visits):
    path, _rows = visits
    document = json.loads(path.read_text(encoding="utf-8"))
    grain = document["relationships"]["grain"]
    entries = {entry["column"]: entry for entry in grain["trajectory"]}
    assert sorted(entries) == ["loss", "sbp", "seen"]
    assert entries["sbp"]["axis"] in ("position", "years") and entries["seen"]["axis"] == "position"
    # A symmetric pressure and the dates on the linear scale, a skewed loss on normal scores.
    assert (entries["sbp"]["scale"], entries["seen"]["scale"], entries["loss"]["scale"]) == ("linear", "linear", "normal")
    assert [group["column"] for group in entries["sbp"]["by"]][:1] == ["arm"]
    assert not any(derived["source"] in entries for derived in grain["derived"])
    # Nothing in an entry grows with the patients: its numbers are its moments, a few each grouping band.
    for entry in entries.values():
        assert len(_leaves(entry)) <= 11 + sum(2 + 3 * len(group["shift"]) for group in entry["by"])


def test_the_twin_carries_the_spread_the_trend_by_arm_the_slopes_and_the_serial_term(visits, visit_twin):
    """MUTANTS: the walk reading no entry; the scores without their level; without their serial term; without the change by arm."""
    _path, rows = visits
    _loaded, _made, twin_rows = visit_twin
    real = _shape(rows)
    twin = _shape(twin_rows)
    assert abs(twin["between_share"] - real["between_share"]) <= 0.08, (real, twin)
    assert abs(twin["slope_a"] - real["slope_a"]) <= 0.25 and abs(twin["slope_b"] - real["slope_b"]) <= 0.25, (real, twin)
    assert (twin["slope_b"] - twin["slope_a"]) < -0.35, (real, twin)
    assert abs(twin["slope_sd_long"] - real["slope_sd_long"]) <= 0.3, (real, twin)
    assert abs(twin["lag_one"] - real["lag_one"]) <= 0.12, (real, twin)


def test_the_twin_still_meets_every_published_patient_fact(visit_twin):
    loaded, made, twin_rows = visit_twin
    names = [column.name for column in loaded.columns]
    checks = kpi_patient_twin.grain_checks(loaded, names, [list(column) for column in zip(*twin_rows)])
    assert checks["census_held"] is True
    assert checks["fixed_constant"] == 1.0
    assert all(one["held"] for one in checks["row_families"])  # type: ignore[union-attr]
    assert checks["position_cells_wrong"] == 0
    assert [(one.column, one.fact) for one in made.deviations if one.fact.startswith("grain.")] == []


def test_no_twin_patient_holds_a_real_patient_s_readings(visits, visit_twin):
    """HIPAA, measured: the twin's patients draw their readings from the published moments and the column's own values;
    none holds a real patient's sequence of five readings or more (three whole numbers in a row can meet by chance)."""
    _path, rows = visits
    _loaded, _made, twin_rows = visit_twin
    real = {tuple(row[5] for row in held) for held in _patients(rows).values() if len(held) >= 5}
    twin = [tuple(row[5] for row in held) for held in _patients(twin_rows).values() if len(held) >= 5]
    assert len(twin) > 300 and sum(1 for one in twin if one in real) == 0


def test_with_the_entries_off_the_layer_is_described_as_before(tmp_path, visits):
    _path, rows = visits
    off = json.loads(_described(tmp_path, rows, trajectories=False).read_text(encoding="utf-8"))
    assert "trajectory" not in off["relationships"]["grain"]


# -- THE RUN ----------------------------------------------------------------------------------------


def test_a_whole_number_run_goes_on_past_its_list(visit_twin):
    """MUTANT: the run read as none (the stand-in beyond the list)."""
    assert patient_walk._whole_run(("1", "2", "3")) == (3, 1)
    assert patient_walk._whole_run(("10", "8", "6")) == (6, -2)
    for broken in (("1", None, "3"), ("1", "2", "4"), ("1",), ("1.0", "2.0"), ("01", "02"), ("a", "b"), ("2", "2")):
        assert patient_walk._whole_run(broken) is None, broken
    _loaded, _made, twin_rows = visit_twin
    for held in _patients(twin_rows).values():
        assert [row[3] for row in held] == [f"{j + 1}" for j in range(len(held))]
