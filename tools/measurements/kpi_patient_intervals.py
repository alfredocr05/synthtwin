"""K-BC-15's survival keys: the counting process's twin read by a time-varying Cox model, its rules and its incidences (lane GRb2-b, plan P4-D491 part b).

ROUTE P, the patient layer on behind the chain's switch, described and
generated as `kpi_patient_twin.py` does it, on the invented start-stop
tables of `tests/patient_interval_tables.start_stop` (a treatment that
starts during follow-up, two end causes and censoring, the intervals cut
where the treatment starts and at laboratory updates), at 20,000 rows:
the REGISTRY at table seeds 1 to 3 by twin seeds 0 to 2; the same table
with the treatment given BY INDICATION (by grade and age; repair 1, the
statistics check's item 1) at seeds 1 to 3 by twins 0 to 2; and two
PERSON-PERIOD files (each interval cut in three, and in six; repair 1,
item 4) at seed 1 by twins 0 to 2. `--night` reads one registry table and
one twin at 200,000 rows instead. Beside each twin, in the same run, the
FRESH REPLICATE (the maker at another seed) and the SHUFFLED table (every
column shuffled over its rows on its own), each read the same way.

Per frame: the four structure rules counted on its patients (start below
stop, contiguous from 0, one end on the last row, the treatment never
returning to 0); the Cox model of the event on the start-stop rows with
entry times (the treatment counted from its start, the grade, the age a
decade over 60, the laboratory band), by `statsmodels`' `PHReg` (the
development lock's test-only zone, plan P4-D409; the driver fails, never
skips, without it); and the Aalen-Johansen incidence of the event at 1,
3 and 5 years on the per-patient table (written out here). Each estimate
is judged against the real table's in YARDSTICKS: `h = sqrt(2) * se`,
`se` the real fit's standard error (the spread of the difference
between two independent tables' estimates of one quantity).

The KPI line (`--kpi`): `rules_broken` (twin patients breaking a rule,
summed over every twin; target 0); on the registry `treated_gap`,
`grade3_gap`, `age10_gap` and `incidence_gap` (the largest of the three
incidences' gaps); on the indication tables `indication_treated_gap` and
`indication_start_grade3_gap` (the grade III term of a Cox model of the
time to the treatment's start, the patients never treated censored at
their end); on the person-period files `period_treated_gap` and
`period_incidence_gap`: EACH THE MEDIAN OVER A TABLE'S TWINS OF
`|twin - real| / h`, THEN THE LARGEST OVER THE TABLES (so a miss on one
table is not hidden; the per-table values in the detail; target at most
2); each beside the replicate's and the shuffle's; `bars_void`, the bars
the shuffled table meets in the same run (each VOID, named in the
detail); `controls_hold` (the replicate inside 2 yardsticks on the
treated term and the shuffle outside every bar); and on the registry the
POOLED interval lists equal to a real patient's, for the twins and the
replicates: of one row (`lists_one_*`), of two rows or more
(`lists_two_*`), and whole records (`records_*`: the list, the treatment
and laboratory sequences, the end value and the five patient-level
cells), counted with sets; `lists_bar_met`: the twins' two-row count at
most the replicates' plus two square roots of it plus one, and their
one-row count at most the replicates' (LANE GRb2 RULINGS 3 (5)).

Usage (`kpi_run.py --slow`):
    PYTHONPATH=src:tests python tools/measurements/kpi_patient_intervals.py --kpi
"""
from __future__ import annotations

import json
import math
import pathlib
import random
import statistics
import sys

HERE = pathlib.Path(__file__).resolve().parents[2]
if str(HERE / "tests") not in sys.path:
    sys.path.insert(0, str(HERE / "tests"))

import patient_interval_tables as tables  # noqa: E402

KEY = bytes(range(32))
TERMS = ("treated", "grade2", "grade3", "age10", "lab_low")
JUDGED = ("treated", "grade3", "age10")
TIMES = (1.0, 3.0, 5.0)
DAY = 365.25
# Each kind of table: its maker's options and the keys judged on it (a key's name, the frame's reading it takes).
KINDS = {
    "registry": ({}, (("treated", "treated"), ("grade3", "grade3"), ("age10", "age10"), ("incidence", "incidence"))),
    "indication": ({"confounded": True}, (("indication_treated", "treated"), ("indication_start_grade3", "start_grade3"))),
    "period": ({"pieces": 3}, (("period_treated", "treated"), ("period_incidence", "incidence"))),
    "period6": ({"pieces": 6}, (("period_treated", "treated"), ("period_incidence", "incidence"))),
}
RUNS = [(kind, 20000, seed, (0, 1, 2)) for kind, seeds in (("registry", (1, 2, 3)), ("indication", (1, 2, 3)), ("period", (1,)), ("period6", (1,))) for seed in seeds]
NIGHT = [("registry", 200000, 1, (0,))]


def _columns(header: "list[str]", rows: "list[list[str]]") -> "dict[str, list[str]]":
    return {name: [row[at] for row in rows] for at, name in enumerate(header)}


def _number(text: str) -> "float | None":
    try:
        return float(text)
    except ValueError:
        return None


def rules_broken(columns: "dict[str, list[str]]") -> int:
    """Patients breaking any of the four rules, read in start order."""
    by: "dict[str, list[int]]" = {}
    for row, key in enumerate(columns["pid"]):
        by.setdefault(key, []).append(row)
    broken = 0
    for rows in by.values():
        read = [(_number(columns["start_day"][row]), _number(columns["stop_day"][row]), row) for row in rows]
        if any(a is None or b is None for a, b, _row in read):
            broken += 1
            continue
        order = sorted((float(a), float(b), row) for a, b, row in read if a is not None and b is not None)
        bad = False
        previous = 0.0
        for place, (a, b, row) in enumerate(order):
            if not a < b or a != previous:
                bad = True
            previous = b
            if place < len(order) - 1 and columns["outcome"][row] != "0":
                bad = True
            if place > 0 and columns["on_treatment"][order[place - 1][2]] == "1" and columns["on_treatment"][row] == "0":
                bad = True
        broken += 1 if bad else 0
    return broken


def _design(columns: "dict[str, list[str]]") -> "tuple[list[list[float]], list[float], list[float], list[float], dict[str, tuple[float, float]]]":
    """The start-stop rows as the analyst reads them, and each patient's follow-up (years) and end."""
    x: "list[list[float]]" = []
    start: "list[float]" = []
    stop: "list[float]" = []
    event: "list[float]" = []
    ends: "dict[str, tuple[float, float]]" = {}
    for row in range(len(columns["pid"])):
        a, b = _number(columns["start_day"][row]), _number(columns["stop_day"][row])
        age = _number(columns["age"][row])
        if a is None or b is None or age is None or not b > a:
            continue
        grade = columns["grade"][row]
        x += [[float(columns["on_treatment"][row] == "1"), float(grade == "II"), float(grade == "III"), (age - 60.0) / 10.0, float(columns["lab_band"][row] == "low")]]
        start += [a / DAY]
        stop += [b / DAY]
        outcome = columns["outcome"][row]
        event += [float(outcome == "1")]
        key = columns["pid"][row]
        if key not in ends or b / DAY >= ends[key][0]:
            ends[key] = (b / DAY, float(outcome) if outcome in ("0", "1", "2") else 0.0)
    return x, start, stop, event, ends


def incidence(ends: "dict[str, tuple[float, float]]") -> "dict[float, tuple[float, float]]":
    """The Aalen-Johansen incidence of cause 1 (cause 2 competing, 0 censored) at each of TIMES, with its delta-method standard error.

    At each distinct end time `t_j` with `n_j` at risk, `d_1j` ends of
    cause 1 and `d_j` of either: `F(t_j) = F(t_j-) + S(t_j-) d_1j / n_j`,
    `S(t_j) = S(t_j-) (1 - d_j / n_j)`; the variance by Marubini and
    Valsecchi's sum, as the module's docstring of lane MU states it.
    """
    pairs = sorted(ends.values())
    count = len(pairs)
    times = sorted({time for time, _cause in pairs})
    at_risk = count
    survival = 1.0
    running = 0.0
    steps: "list[tuple[float, float, float, int, int, int]]" = []
    place = 0
    for time in times:
        first = every = censored = 0
        while place < count and pairs[place][0] == time:
            cause = pairs[place][1]
            if cause == 1.0:
                first += 1
            if cause in (1.0, 2.0):
                every += 1
            else:
                censored += 1
            place += 1
        if every and at_risk > 0:
            running += survival * first / at_risk
            steps += [(time, running, survival, first, every, at_risk)]
            survival *= 1.0 - every / at_risk
        at_risk -= every + censored
    out: "dict[float, tuple[float, float]]" = {}
    for point in TIMES:
        upto = [one for one in steps if one[0] <= point]
        if not upto:
            out[point] = (0.0, 0.0)
            continue
        value = upto[-1][1]
        variance = 0.0
        for _time, cumulative, before, first, every, n in upto:
            gap = value - cumulative
            variance += gap * gap * every / (n * max(n - every, 1)) + before * before * first * (n - first) / n ** 3 - 2.0 * gap * before * first / n ** 2
        out[point] = (value, math.sqrt(max(variance, 0.0)))
    return out


def _start_design(columns: "dict[str, list[str]]") -> "tuple[list[list[float]], list[float], list[float]]":
    """Each patient's time to the treatment's start (years; the patients never treated censored at their end), its grade and age."""
    first: "dict[str, list[object]]" = {}
    for row in range(len(columns["pid"])):
        a, b, age = _number(columns["start_day"][row]), _number(columns["stop_day"][row]), _number(columns["age"][row])
        if a is None or b is None or age is None or not b > a:
            continue
        key = columns["pid"][row]
        grade = columns["grade"][row]
        mine = first.setdefault(key, [math.inf, 0.0, [float(grade == "II"), float(grade == "III"), (age - 60.0) / 10.0]])
        mine[1] = max(float(mine[1]), b)  # type: ignore[arg-type]
        if columns["on_treatment"][row] == "1":
            mine[0] = min(float(mine[0]), a)  # type: ignore[arg-type]
    x = [mine[2] for mine in first.values()]  # type: ignore[misc]
    time = [(float(mine[0]) if float(mine[0]) < math.inf else float(mine[1])) / DAY for mine in first.values()]  # type: ignore[arg-type]
    started = [1.0 if float(mine[0]) < math.inf else 0.0 for mine in first.values()]  # type: ignore[arg-type]
    return x, time, started  # type: ignore[return-value]


def fitted(columns: "dict[str, list[str]]") -> "dict[str, object]":
    """The frame's rules, Cox terms (value, standard error), the time-to-start grade III term and incidences."""
    import numpy
    from statsmodels.duration.hazard_regression import PHReg

    x, start, stop, event, ends = _design(columns)
    result = PHReg(numpy.asarray(stop), numpy.asarray(x), status=numpy.asarray(event), entry=numpy.asarray(start)).fit()
    params = [float(one) for one in result.params]
    errors = [float(one) for one in result.bse]
    sx, stime, started = _start_design(columns)
    begun = PHReg(numpy.asarray(stime) + 1e-9, numpy.asarray(sx), status=numpy.asarray(started)).fit()
    return {
        "rules_broken": rules_broken(columns),
        "cox": {name: (params[at], errors[at]) for at, name in enumerate(TERMS)},
        "start_grade3": (float(begun.params[1]), float(begun.bse[1])),
        "incidence": {f"{point:g}": value for point, value in incidence(ends).items()},
    }


def _lists(columns: "dict[str, list[str]]") -> "dict[str, tuple[tuple[tuple[str, str], ...], tuple[str, ...]]]":
    """Each patient's interval list in start order and its whole record (the list, the treatment and laboratory sequences, the end value, the five patient-level cells)."""
    by: "dict[str, list[int]]" = {}
    for row, key in enumerate(columns["pid"]):
        by.setdefault(key, []).append(row)
    out: "dict[str, tuple[tuple[tuple[str, str], ...], tuple[str, ...]]]" = {}
    for key, rows in by.items():
        order = sorted(rows, key=lambda row: (_number(columns["start_day"][row]) or 0.0, row))
        listed = tuple((columns["start_day"][row], columns["stop_day"][row]) for row in order)
        record = tuple(columns["on_treatment"][row] for row in order) + tuple(columns["lab_band"][row] for row in order)
        record += (columns["outcome"][order[-1]],) + tuple(columns[name][order[0]] for name in ("site", "grade", "age", "gender", "entered_on"))
        out[key] = (listed, record)
    return out


def coincidences(real: "dict[str, list[str]]", other: "dict[str, list[str]]") -> "tuple[int, int, int]":
    """The patients of `other` whose interval list equals a real patient's, of one row and of two rows or more, and whose whole record does (sets: linear)."""
    known = _lists(real)
    lists = {listed for listed, _record in known.values()}
    records = {(listed, record) for listed, record in known.values()}
    one = two = whole = 0
    for listed, record in _lists(other).values():
        if listed in lists:
            one += 1 if len(listed) == 1 else 0
            two += 1 if len(listed) >= 2 else 0
        whole += 1 if (listed, record) in records else 0
    return one, two, whole


def shuffled(header: "list[str]", rows: "list[list[str]]", seed: int) -> "list[list[str]]":
    """Every column shuffled over the rows on its own (seeded)."""
    draw = random.Random(seed)
    columns = [[row[at] for row in rows] for at in range(len(header))]
    for column in columns:
        draw.shuffle(column)
    return [[column[row] for column in columns] for row in range(len(rows))]


def twin_of(header: "list[str]", rows: "list[list[str]]", folder: pathlib.Path, name: str, seeds: "tuple[int, ...]") -> "tuple[list[list[list[str]]], dict[str, object]]":
    """Route P: the table described behind the switch with its person column answered, and its twins at the seeds."""
    import dataclasses
    import resource
    import time

    import fixtures

    from synthtwin import chain, contract, generation, profile, reading, taxonomy, twinstore

    path = folder / f"{name}.csv"
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(",".join(header) + "\n")
        for row in rows:
            handle.write(",".join(row) + "\n")
    clock = time.process_time()
    settings = dataclasses.replace(taxonomy.Settings(small_cell_floor=11), person_columns=("pid",))
    table = reading.read_table(str(path), small_cell_floor=11)
    document = profile.build_document(table, settings, ["pid"], [], [], subjects=["pid"], top_code=True)
    chained = chain.describe(table, document, settings, chain.ChainSwitch(name, KEY, rows_per_person=chain.ROWS_PERSON))
    described = time.process_time() - clock
    if chained.grain is None or chained.statistical is None or chained.columns is None:
        return [], {"layer": False}
    switched = json.loads(json.dumps(document))
    switched["relationships"]["statistical"] = chained.statistical
    switched["relationships"]["grain"] = chained.grain
    switched["columns"] = chained.columns
    published = fixtures.write_profile(folder, f"{name}-switched.json", switched)
    out: "list[list[list[str]]]" = []
    generated = 0.0
    for seed in seeds:
        clock = time.process_time()
        loaded = contract.load_profile(str(published), chain=True)
        made = generation.generate_held(loaded, seed)
        generated += time.process_time() - clock
        columns = [twinstore.column_cells(one) for one in (made.held_columns or ())]
        out += [[[column[row] for column in columns] for row in range(len(columns[0]))]]
    grain = chained.grain
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return out, {
        "layer": True, "counting": "intervals" in grain, "describe_cpu_s": round(described, 1),
        "generate_cpu_s_a_twin": round(generated / max(1, len(seeds)), 1),
        "peak_mb": round(peak / (1048576 if sys.platform == "darwin" else 1024), 1),
    }


def _gap(found: "dict[str, object]", real: "dict[str, object]") -> "dict[str, float]":
    out: "dict[str, float]" = {}
    cox, real_cox = found["cox"], real["cox"]
    assert isinstance(cox, dict) and isinstance(real_cox, dict)
    for name in JUDGED:
        value, se = real_cox[name]
        out[name] = abs(cox[name][0] - value) / (math.sqrt(2.0) * se)
    begun, real_begun = found["start_grade3"], real["start_grade3"]
    assert isinstance(begun, tuple) and isinstance(real_begun, tuple)
    out["start_grade3"] = abs(begun[0] - real_begun[0]) / (math.sqrt(2.0) * real_begun[1])
    incidences, real_incidences = found["incidence"], real["incidence"]
    assert isinstance(incidences, dict) and isinstance(real_incidences, dict)
    out["incidence"] = max(abs(incidences[key][0] - real_incidences[key][0]) / max(math.sqrt(2.0) * real_incidences[key][1], 1e-9) for key in real_incidences)
    return out


def one_table(kind: str, size: int, seed: int, twins: "tuple[int, ...]", folder: pathlib.Path) -> "dict[str, object]":
    options = KINDS[kind][0]
    header, rows = tables.start_stop(size, seed, **options)  # type: ignore[arg-type]
    real_columns = _columns(header, rows)
    real = fitted(real_columns)
    made, info = twin_of(header, rows, folder, f"{kind}-{size}-{seed}", twins)
    sides: "dict[str, list[dict[str, object]]]" = {"twin": [], "replicate": [], "shuffled": []}
    for at, twin in enumerate(made):
        twin_columns = _columns(header, twin)
        found = fitted(twin_columns)
        sides["twin"] += [{"rules_broken": found["rules_broken"], "lists": coincidences(real_columns, twin_columns), **_gap(found, real)}]
        _h, replicate_rows = tables.start_stop(size, seed * 1000 + 100 + twins[at], **options)  # type: ignore[arg-type]
        replicate_columns = _columns(header, replicate_rows)
        found = fitted(replicate_columns)
        sides["replicate"] += [{"rules_broken": found["rules_broken"], "lists": coincidences(real_columns, replicate_columns), **_gap(found, real)}]
        found = fitted(_columns(header, shuffled(header, rows, seed * 31 + twins[at])))
        sides["shuffled"] += [{"rules_broken": found["rules_broken"], **_gap(found, real)}]
    for file in folder.glob(f"{kind}-{size}-{seed}*"):
        file.unlink()
    return {"kind": kind, "size": size, "seed": seed, "info": info, "real": {name: real["cox"][name] for name in JUDGED}, "sides": sides}  # type: ignore[index]


def judged(runs: "list[dict[str, object]]") -> "tuple[dict[str, object], str]":
    """The KPI's value over the runs, and the detail naming each table's value and each void bar (see the module's docstring).

    Each gap key is the median over one table's twins, then the largest
    over the tables of its kind (LANE MU RULINGS 3 (1) item 5); a bar the
    shuffled table meets in the same run is VOID (item 4).
    """
    value: "dict[str, object]" = {}
    suffix = "_200k" if runs and runs[0]["size"] == 200000 else ""
    detail: "list[str]" = []
    bars: "list[str]" = []
    for side in ("twin", "replicate", "shuffled"):
        tag = "" if side == "twin" else f"{side}_"
        value[f"{tag}rules_broken{suffix}"] = sum(int(one["rules_broken"]) for run in runs for one in run["sides"][side])  # type: ignore[index, attr-defined]
        for key, reading in sorted({pair for run in runs for pair in KINDS[f"{run['kind']}"][1]}):
            per_table = [statistics.median(float(one[reading]) for one in run["sides"][side]) for run in runs  # type: ignore[index, attr-defined]
                         if (key, reading) in KINDS[f"{run['kind']}"][1] and run["sides"][side]]  # type: ignore[index]
            if not per_table:
                continue
            value[f"{tag}{key}_gap{suffix}"] = round(max(per_table), 2)
            if side == "twin":
                bars += [f"{key}_gap{suffix}"]
                detail += [f"{key} " + "/".join(f"{one:.2f}" for one in per_table)]
    void = [bar for bar in bars if float(value[f"shuffled_{bar}"]) <= 2.0]  # type: ignore[arg-type]
    value[f"bars_void{suffix}"] = len(void)
    value[f"controls_hold{suffix}"] = bool(f"replicate_treated_gap{suffix}" in value and float(value[f"replicate_treated_gap{suffix}"]) <= 2.0  # type: ignore[arg-type]
                                           and not void)
    value[f"counting_stands{suffix}"] = all(bool(run["info"].get("counting")) for run in runs)  # type: ignore[attr-defined]
    registry = [run for run in runs if run["kind"] == "registry"]
    for side in ("twin", "replicate"):
        pooled = [sum(one["lists"][at] for run in registry for one in run["sides"][side]) for at in range(3)]  # type: ignore[index, attr-defined]
        value[f"lists_one_{side}{suffix}"], value[f"lists_two_{side}{suffix}"], value[f"records_{side}{suffix}"] = pooled
    two = int(value[f"lists_two_replicate{suffix}"])  # type: ignore[call-overload]
    value[f"lists_bar_met{suffix}"] = bool(int(value[f"lists_two_twin{suffix}"]) <= two + 2.0 * math.sqrt(two) + 1.0  # type: ignore[call-overload]
                                          and int(value[f"lists_one_twin{suffix}"]) <= int(value[f"lists_one_replicate{suffix}"]))  # type: ignore[call-overload]
    text = "per table, the median of its twins: " + "; ".join(detail)
    if void:
        text += "; VOID (the shuffle meets it): " + ", ".join(void)
    return value, text


def main() -> int:
    """`--kpi`: K-BC-15's survival keys over the runs, one KPI line (`--night`: the 200,000-row run instead)."""
    import tempfile

    wanted = NIGHT if "--night" in sys.argv else RUNS
    runs: "list[dict[str, object]]" = []
    with tempfile.TemporaryDirectory() as folder:
        for kind, size, seed, twins in wanted:
            runs += [one_table(kind, size, seed, twins, pathlib.Path(folder))]
            print(json.dumps(runs[-1], sort_keys=True), file=sys.stderr, flush=True)
    value, detail = judged(runs)
    print("KPI " + json.dumps({"id": "K-BC-15", "value": value, "detail": "the counting process's twin (lane GRb2-b), route P: " + detail}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
