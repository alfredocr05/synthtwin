"""K-BC-06 on the patient layer's twin: several rows per patient, measured (lane GRb, plan P4-D465).

The measurements of the patient layer's generator (method G16.13 to
G16.17), on invented tables only (`tests/patient_enumeration.st2_rows`,
`tests/analyst_tables.st2`, `tests/patient_twin_tables`):

- the within-patient correlation (the random-intercept model's ICC by
  maximum likelihood, `analyst_kit.random_intercept`) of the real table,
  of a twin and of the twin with its reading shuffled over rows;
- the arm-by-visit coefficient of that model (`reading ~ visit * arm`,
  plus `(age - 55) / 10` where the table holds an age), as a share of the
  real one, and the arm difference of the mean per-patient least-squares
  slope over patients of two rows or more;
- rows per patient: the distance between the twin's census and the
  table's (Kolmogorov's, over patients), its 50th, 90th and 99th
  percentiles, the top band's share of rows and the share of rows on the
  top 1 per cent of patients;
- the share of twin patients whose patient-fixed columns hold one value
  on every row, and whose dated rows run in date order;
- K-BC-10's stops on the twin: patients holding several arms, repeated
  (patient, visit) pairs, and persons holding more than one value of a
  column the real table holds constant inside every patient;
- G16.17 case 10 on every description it makes: no published
  patient-level cell and no row family's cell of 1 to `f - 1`;
- r under a census as method G16.14 writes it, from the census alone.

Every function reads cells as text and draws nothing but the shuffle's
own seeded words. Standard library and the tests' own helpers only.

Usage (the K-BC-06 driver, every check at 20,000 rows and above under
`kpi_run.py --slow`):
    PYTHONPATH=src:tests python tools/measurements/kpi_patient_twin.py --kpi
"""
from __future__ import annotations

import json
import math
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).resolve().parents[2]
if str(HERE / "tests") not in sys.path:
    sys.path.insert(0, str(HERE / "tests"))

import analyst_kit as K  # noqa: E402


# -- reading a table's patients ------------------------------------------------


def patients_of(person: "list[str]") -> "dict[str, list[int]]":
    """Each patient's rows, in row order (a blank person cell is no patient)."""
    out: "dict[str, list[int]]" = {}
    for row in range(len(person)):
        key = person[row]
        if key == "":
            continue
        if key not in out:
            out[key] = []
        out[key] += [row]
    return out


def number(text: str) -> "float | None":
    """A cell read as a number, None where it is blank or not one."""
    try:
        value = float(text)
    except ValueError:
        return None
    return value if value == value and abs(value) != float("inf") else None


def positions(person: "list[str]") -> "list[int]":
    """Each row's position inside its patient, 1 for the patient's first row in row order."""
    seen: "dict[str, int]" = {}
    out: "list[int]" = []
    for key in person:
        seen[key] = seen[key] + 1 if key in seen else 1
        out += [seen[key]]
    return out


# -- rows per patient ----------------------------------------------------------


def quantile_low(sorted_values: "list[int]", share: float) -> int:
    """The smallest value at or above the given share of the sorted values (the lower empirical quantile)."""
    if not sorted_values:
        return 0
    at = max(0, min(len(sorted_values) - 1, int(math.ceil(share * len(sorted_values))) - 1))
    return sorted_values[at]


def r_summary(r_values: "list[int]", top_edge: int = 0) -> "dict[str, float]":
    """Rows per patient: p50, p90, p99, the rows on the top 1 per cent of patients and, given the census's top edge, its band's share of rows."""
    ordered = sorted(r_values)
    rows = sum(ordered)
    out: "dict[str, float]" = {
        "patients": len(ordered),
        "rows": rows,
        "p50": quantile_low(ordered, 0.5),
        "p90": quantile_low(ordered, 0.9),
        "p99": quantile_low(ordered, 0.99),
        "max_over_p99": round(ordered[-1] / max(1, quantile_low(ordered, 0.99)), 3) if ordered else 0.0,
    }
    top = max(1, int(math.ceil(len(ordered) / 100)))
    out["top1_share"] = round(sum(ordered[len(ordered) - top:]) / rows, 4) if rows else 0.0
    if top_edge:
        out["top_band_share"] = round(sum(one for one in ordered if one >= top_edge) / rows, 4) if rows else 0.0
    return out


def r_distance(first: "list[int]", second: "list[int]") -> float:
    """Kolmogorov's distance between two censuses of rows per patient, each read over its own patients."""
    if not first or not second:
        return 1.0
    a = sorted(first)
    b = sorted(second)
    values = sorted(set(a) | set(b))
    i = 0
    j = 0
    worst = 0.0
    for value in values:
        while i < len(a) and a[i] <= value:
            i += 1
        while j < len(b) and b[j] <= value:
            j += 1
        worst = max(worst, abs(i / len(a) - j / len(b)))
    return round(worst, 4)


def census_line(census: "dict[str, object]") -> "list[int]":
    """`r`'s values as method G16.14's one straight line writes them from a published census (no row family).

    Each value below `lo` on its published count; the top band's `m`
    patients take excess values `floor(q (2 m - 2 i - 1) / m^2)`, then one
    unit added or taken in turn from the largest until they sum to `q`.
    """
    bands = census["bands"] if isinstance(census["bands"], list) else []
    out: "list[int]" = []
    for entry in bands:
        if isinstance(entry, dict):
            out += [int(entry["r"])] * int(entry["patients"])
    top = census["top"] if isinstance(census["top"], dict) else {"patients": 0, "rows": 0}
    lo = int(census["lo"])  # type: ignore[call-overload]
    m = int(top["patients"])
    if m:
        q = int(top["rows"]) - lo * m
        out += [lo + one for one in straight_line(q, m)]
    return out


def straight_line(q: int, m: int) -> "list[int]":
    """Method G16.14's excess line: `m` whole numbers summing to `q`, largest first."""
    if m <= 0:
        return []
    values = [(q * (2 * m - 2 * i - 1)) // (m * m) for i in range(m)]
    at = 0
    while sum(values) < q:
        values[at % m] += 1
        at += 1
    at = 0
    while sum(values) > q:
        if values[at % m] > 0:
            values[at % m] -= 1
        at += 1
    return values


# -- the panel's estimates -----------------------------------------------------


def model_fit(person: "list[str]", visit: "list[float]", arm: "list[float]", y: "list[float | None]", age: "list[float] | None", old_term: bool = False) -> "dict[str, float]":
    """The random-intercept model `y ~ visit + arm + arm x visit (+ age10) (+ old + old x visit)`, groups the patients: its coefficients and ICC.

    `old` is an age of 55 or more (`ST2-AGE`'s second group, SLOPE-design-v2 section 11 clause (6)).
    """
    keep = [k for k in range(len(person)) if person[k] != "" and y[k] is not None and visit[k] == visit[k] and arm[k] == arm[k]
            and (age is None or age[k] == age[k])]
    columns: "dict[str, list]" = {
        "visit": [visit[k] for k in keep],
        "arm": [arm[k] for k in keep],
    }
    terms: "list[tuple[str, K.Term]]" = [
        ("int", K.intercept),
        ("visit", lambda chunk: list(chunk["visit"])),
        ("arm", lambda chunk: list(chunk["arm"])),
        ("arm_visit", lambda chunk: [a * v for a, v in zip(chunk["arm"], chunk["visit"])]),
    ]
    if age is not None:
        columns["age"] = [age[k] for k in keep]
        terms += [("age10", lambda chunk: [(a - 55.0) / 10.0 for a in chunk["age"]])]
        if old_term:
            terms += [
                ("old", lambda chunk: [1.0 if a >= 55.0 else 0.0 for a in chunk["age"]]),
                ("old_visit", lambda chunk: [(1.0 if a >= 55.0 else 0.0) * v for a, v in zip(chunk["age"], chunk["visit"])]),
            ]
    design = K.Design(columns, terms)
    values = [float(y[k]) for k in keep]  # type: ignore[arg-type]
    groups = [person[k] for k in keep]
    try:
        fit, icc = K.random_intercept(design, values, groups, min_repeated=22)
    except Exception:  # noqa: BLE001 -- a model that stops is the measurement
        return {"stopped": 1.0}
    out = {name: float(fit.beta[at]) for at, name in enumerate(design.names)}
    out["icc"] = float(icc)
    return out


def slope_difference(person: "list[str]", visit: "list[float]", arm: "list[float]", y: "list[float | None]") -> "float | None":
    """The arm difference of the mean per-patient least-squares slope of `y` on `visit`, over patients of two rows or more.

    A patient's arm is its first row's.
    """
    by = patients_of(person)
    sums = {0: [0.0, 0], 1: [0.0, 0]}
    for rows in by.values():
        pairs = [(visit[k], y[k]) for k in rows if y[k] is not None and visit[k] == visit[k]]
        if len(pairs) < 2:
            continue
        mx = math.fsum(p[0] for p in pairs) / len(pairs)
        my = math.fsum(float(p[1]) for p in pairs) / len(pairs)  # type: ignore[arg-type]
        sxx = math.fsum((p[0] - mx) ** 2 for p in pairs)
        if sxx == 0:
            continue
        slope = math.fsum((p[0] - mx) * (float(p[1]) - my) for p in pairs) / sxx  # type: ignore[arg-type]
        side = 1 if arm[rows[0]] == 1.0 else 0
        sums[side][0] += slope
        sums[side][1] = int(sums[side][1]) + 1
    if not sums[0][1] or not sums[1][1]:
        return None
    return sums[1][0] / sums[1][1] - sums[0][0] / sums[0][1]


def fixed_constant_share(person: "list[str]", fixed: "list[list[str]]") -> float:
    """The share of patients whose every listed column holds one value on all of their rows."""
    by = patients_of(person)
    if not by:
        return 0.0
    held = 0
    for rows in by.values():
        if all(len({column[k] for k in rows}) == 1 for column in fixed):
            held += 1
    return round(held / len(by), 4)


def dates_in_order_share(person: "list[str]", dates: "list[str]") -> float:
    """The share of patients of two dated rows or more whose dates never fall in row order (ISO dates compare as text)."""
    by = patients_of(person)
    counted = 0
    held = 0
    for rows in by.values():
        stamps = [dates[k] for k in rows if dates[k] != ""]
        if len(stamps) < 2:
            continue
        counted += 1
        if all(stamps[at] <= stamps[at + 1] for at in range(len(stamps) - 1)):
            held += 1
    return round(held / counted, 4) if counted else 1.0


def shuffled(values: "list[str]", seed: int) -> "list[str]":
    """The column's cells in a seeded random order: the twin with no within-patient correlation."""
    out = list(values)
    random.Random(seed).shuffle(out)
    return out


def constant_columns(header: "list[str]", columns: "list[list[str]]", person_name: str) -> "list[str]":
    """The columns a table holds constant inside every patient (one value on all of a patient's rows), the person column aside."""
    by = patients_of(columns[header.index(person_name)])
    out: "list[str]" = []
    for at, name in enumerate(header):
        if name == person_name:
            continue
        cells = columns[at]
        if all(len({cells[row] for row in rows}) == 1 for rows in by.values()):
            out += [name]
    return out


def varying_where_constant(names: "list[str]", columns: "list[list[str]]", person_name: str, constant: "list[str]") -> "dict[str, int]":
    """K-BC-10's third stop (repair 1 of lane GRb, the statistics check's item 3): for each column the REAL table holds
    constant inside every patient, the twin's persons holding more than one value of it; `any` the persons holding more
    than one value of any of them. A subject table merged back many-to-one stops on each."""
    by = patients_of(columns[names.index(person_name)])
    out: "dict[str, int]" = {}
    several: "set[str]" = set()
    for name in constant:
        if name not in names:
            continue
        cells = columns[names.index(name)]
        varying = [key for key, rows in by.items() if len({cells[row] for row in rows}) > 1]
        out[name] = len(varying)
        several |= set(varying)
    out["any"] = len(several)
    return out


def floor_cells(statistical: "dict[str, object]", grain: "dict[str, object]", floor: int) -> "dict[str, int]":
    """G16.17 case 10, the floor gate, on a switched description: its published patient-level cells (the patient chain's
    tables, its ladder totals, the census) and its row families' cells holding 1 to `f - 1` (each must be 0 or at least `f`)."""
    patient_cells: "list[int]" = []
    chain_written = statistical.get("chain") if isinstance(statistical.get("chain"), list) else []
    for family in chain_written or []:
        for line in family["table"]:
            patient_cells += [int(one) for one in (line if isinstance(line, list) else [line])]
    ladder = statistical.get("ladder") if isinstance(statistical.get("ladder"), list) else []
    for entry in ladder or []:
        patient_cells += [int(one) for one in entry.get("totals", [])]
    census = grain["census"] if isinstance(grain.get("census"), dict) else {}
    patient_cells += [int(band["patients"]) for band in census.get("bands", [])]
    top = census.get("top") if isinstance(census.get("top"), dict) else {}
    patient_cells += [int(top.get("patients", 0))]
    row_cells = [int(one) for family in grain.get("rows") or [] for line in family["table"] for one in line]
    return {
        "patient_cells_1_to_f_minus_1": len([one for one in patient_cells if 0 < one < floor]),
        "row_cells_1_to_f_minus_1": len([one for one in row_cells if 0 < one < floor]),
    }


ROLES = {
    # kind: person, arm, visit (None: the row's position), reading, fixed, date, age
    "st2": ("sid", "arm", "visit", "marker", ("arm", "age"), None, "age"),
    "st2age": ("sid", "arm", "visit", "reading", ("arm", "age"), None, "age"),
    "st2c": ("sid", "arm", "visit", "reading", ("arm", "age"), None, "age"),
    "st2l": ("sid", "arm", "visit", "reading", ("arm", "age"), None, "age"),
    "enc": ("pid", "group", "visit_no", "reading", ("group", "gender", "birth_year"), "visit_date", None),
    "lab": ("pid", "arm", "visit_no", "result", ("arm", "gender", "birth_year"), "draw_date", None),
    "flow": ("pid", "group", None, "reading", ("group", "birth_year"), "taken_on", None),
}


def measured(kind: str, header: "list[str]", columns: "list[list[str]]", seed: int = 0, old_term: bool = False) -> "dict[str, object]":
    """Every K-BC-06 number of one table (real or twin), its cells as text, by the kind's roles."""
    person_name, arm_name, visit_name, reading_name, fixed_names, date_name, age_name = ROLES[kind]
    at = {name: place for place, name in enumerate(header)}
    person = columns[at[person_name]]
    arm_text = columns[at[arm_name]]
    levels = sorted({cell for cell in arm_text if cell != ""})
    first_level = levels[0] if levels else ""
    arm = [float("nan") if cell == "" else (0.0 if cell == first_level else 1.0) for cell in arm_text]
    if visit_name is None:
        visit = [float(one) for one in positions(person)]
    else:
        visit = [v if v is not None else float("nan") for v in (number(cell) for cell in columns[at[visit_name]])]
    y = [number(cell) for cell in columns[at[reading_name]]]
    age = None
    if age_name is not None:
        age = [v if v is not None else float("nan") for v in (number(cell) for cell in columns[at[age_name]])]
    by = patients_of(person)
    r_values = [len(rows) for rows in by.values()]
    out: "dict[str, object]" = {"model": model_fit(person, visit, arm, y, age, old_term)}
    out["slope_diff"] = slope_difference(person, visit, arm, y)
    out["r"] = r_summary(r_values)
    out["r_values"] = r_values
    out["fixed_constant"] = fixed_constant_share(person, [columns[at[name]] for name in fixed_names if name in at])
    # K-BC-10's two stops on the table: patients holding several arms, and repeated (patient, visit) pairs.
    arms_of: "dict[str, set[str]]" = {}
    pairs: "set[tuple[str, str]]" = set()
    repeated = 0
    visit_text = columns[at[visit_name]] if visit_name is not None else None
    for row in range(len(person)):
        if person[row] == "":
            continue
        arms_of.setdefault(person[row], set()).add(arm_text[row])
        if visit_text is not None:
            pair = (person[row], visit_text[row])
            if pair in pairs:
                repeated += 1
            pairs.add(pair)
    out["patients_with_several_arms"] = len([key for key, held in arms_of.items() if len(held) > 1])
    out["repeated_patient_visits"] = repeated
    if date_name is not None and date_name in at:
        out["dates_in_order"] = dates_in_order_share(person, columns[at[date_name]])
    if seed:
        mixed = list(columns)
        mixed[at[reading_name]] = shuffled(columns[at[reading_name]], seed)
        out["shuffled_model"] = model_fit(person, visit, arm, [number(cell) for cell in mixed[at[reading_name]]], age, old_term)
    return out


def grain_checks(profile: "object", names: "list[str]", columns: "list[list[str]]") -> "dict[str, object]":
    """A twin's cells against its description's `grain`, read on the twin's own patients (BC-ARCH 5.2's clauses).

    `r`'s census exact; every patient-fixed column constant on every
    patient; each row family's table counted on the twin (parent cells
    read on the twin's patient table: a patient-fixed column at the
    patient's first row, `r` as its rows, an own mean from its readings
    against the published edges, exactly, each cell read by the profile's
    reader (`patient_walk.exact_meaning`); a first date by the reader's
    own order, at the derived column's level); each published `Q_P`'s
    `S_P` in its window; each position-like column at its listed
    positions; each dealt date column in order inside every patient. A
    derived column whose source the layer holds (contract 4.6c.12,
    departure 6) has no reading on the twin: the families and trend cells
    it is a member of are skipped and counted (repair 1 of lane GRb, the
    first skeptic's item 4).
    """
    from synthtwin import patient_rules, patient_walk

    grain = profile.relationships.grain  # type: ignore[attr-defined]
    cols = dict(zip(names, columns))
    by = patients_of(cols[grain.person])
    order = list(by)
    out: "dict[str, object]" = {}
    rs = [len(by[key]) for key in order]
    census: "dict[int, int]" = {}
    for one in rs:
        census[one] = census.get(one, 0) + 1
    top = [one for one in rs if one >= grain.lo]
    out["census_held"] = all(census.get(at + 1, 0) == grain.bands[at] for at in range(len(grain.bands))) and len(top) == grain.top_patients and sum(top) == grain.top_rows
    from synthtwin import contract

    fixed = [name for name in names if contract.class_in(grain, name) == patient_rules.CLASS_FIXED]
    out["fixed_constant"] = round(sum(1 for key in order if all(len({cols[name][row] for row in by[key]}) == 1 for name in fixed)) / max(1, len(order)), 4)
    row_entries = {entry.column: entry for entry in grain.ladder}
    pt_entries = {entry.column: entry for entry in grain.patient_ladder}
    blocks = {column.name: column for column in profile.columns}  # type: ignore[attr-defined]
    held_sources = {derived.name for derived in grain.derived if derived.source not in row_entries or derived.source not in cols}
    out["derived_source_held"] = sorted(held_sources)
    meanings: "dict[str, dict]" = {}

    def meaning_of(name: str) -> "dict":
        if name not in meanings:
            meanings[name] = patient_walk.exact_meaning(profile, blocks[name], cols[name])  # type: ignore[arg-type]
        return meanings[name]

    def code_of(name: str, key: str) -> int:
        rows = by[key]
        if name == patient_rules.R_NAME:
            for at, band in enumerate(pt_entries[name].bands):
                label = f"{band[0][0]}"
                if label == f"{len(rows)}" or (label.endswith("or more") and len(rows) >= grain.lo):
                    return at
            return -1
        for derived in grain.derived:
            if derived.name != name:
                continue
            if name in held_sources:
                return -1
            if derived.kind == patient_rules.OWN_MEAN:
                meaning = meaning_of(derived.source)
                return patient_rules.own_mean_band([meaning[cols[derived.source][row]] for row in rows], list(derived.edges))
            reader = patient_walk._reading_of(profile, blocks[derived.source], row_entries[derived.source])  # type: ignore[arg-type]
            present: "list[tuple[object, int, int]]" = []
            for row in rows:
                l0, value = patient_walk._read(reader, cols[derived.source][row])
                if value is not None:
                    present += [(value, row, l0)]
            if not present:
                return -1
            # the first date by the reader's own order (a date's canonical text), ties by row, at the derived column's level
            first = min(present, key=lambda one: (one[0], one[1]))  # type: ignore[arg-type,return-value]
            return patient_walk._level_map(row_entries[derived.source], derived.level)[first[2]]
        reader = patient_walk._reading_of(profile, blocks[name], pt_entries[name])  # type: ignore[arg-type]
        return patient_walk._read(reader, cols[name][rows[0]])[0]

    families: "list[dict[str, object]]" = []
    skipped = 0
    for family in grain.rows:
        if family.child not in cols:
            continue
        if any(name in held_sources for name, _level in family.parents):
            skipped += 1
            continue
        entry = row_entries[family.child]
        maps = patient_walk._level_map(entry, family.level)
        bands = max(maps) + 1
        reader = patient_walk._reading_of(profile, blocks[family.child], entry)  # type: ignore[arg-type]
        level_maps = [patient_walk._level_map(pt_entries[name], level) for name, level in family.parents]
        sizes = [max(one) + 1 for one in level_maps]
        table = [[0 for _band in range(bands)] for _line in family.table]
        outside = 0
        for key in order:
            cell = 0
            broken = False
            for (name, _level), size, level_map in zip(family.parents, sizes, level_maps):
                code = code_of(name, key)
                if code < 0:
                    broken = True
                    break
                cell = cell * size + level_map[code]
            if broken or cell >= len(table):
                outside += len(by[key])
                continue
            for row in by[key]:
                table[cell][maps[patient_walk._read(reader, cols[family.child][row])[0]]] += 1
        held = [list(line) for line in family.table] == table
        families += [{"child": family.child, "held": held, "rows_off": sum(abs(a - b) for x, y in zip(family.table, table) for a, b in zip(x, y)), "rows_outside": outside}]
    out["row_families"] = families
    grids = {name: patient_walk._Grid(u, low, int(top_code)) for name, u, low, top_code in grain.grid}
    trends: "list[dict[str, object]]" = []
    for cell in grain.trend:
        grid = grids[cell.column]
        want: "dict[str, str]" = {}
        for label in cell.cell:
            key_name, value = label.rsplit("=", 1)
            want[key_name] = value
        if any(name in held_sources for name in want):
            skipped += 1
            continue
        coded = {text: patient_walk.grid_code(grid, value) for text, value in meaning_of(cell.column).items()}
        rho = int(want[patient_rules.R_NAME])
        levels = patient_walk.trend_levels(grain, list(want))
        total = 0
        members = 0
        for key in order:
            rows = by[key]
            if len(rows) != rho:
                continue
            same = True
            for name, value in want.items():
                if name == patient_rules.R_NAME:
                    continue
                code = code_of(name, key)
                band = patient_walk._level_map(pt_entries[name], levels[name] if name in levels else 0)[code] if code >= 0 else -1
                if value != f"{band}":
                    same = False
            if not same:
                continue
            members += 1
            codes = [coded[cols[cell.column][row]] for row in rows]
            total += patient_walk._s_of(codes)
        low = 2 * cell.q
        high = low + (1 if rho % 2 == 0 else 0)
        trends += [{"met": low <= total <= high, "gap": max(0, low - total, total - high)}]
    out["trend_cells"] = len(trends)
    out["trend_met"] = len([one for one in trends if one["met"]])
    out["skipped_for_a_held_source"] = skipped
    wrong = 0
    for name, values in grain.positions:
        for key in order:
            for j, row in enumerate(by[key]):
                if j < len(values) and values[j] is not None and cols[name][row] != values[j]:
                    wrong += 1
    out["position_cells_wrong"] = wrong
    disorder = 0
    for name in names:
        if contract.class_in(grain, name) != patient_rules.CLASS_DEALT or name not in row_entries:
            continue
        reader = patient_walk._reading_of(profile, blocks[name], row_entries[name])  # type: ignore[arg-type]
        for key in order:
            readings = [patient_walk._read(reader, cols[name][row])[1] for row in by[key]]
            present = [one for one in readings if one is not None]
            if any(present[at] > present[at + 1] for at in range(len(present) - 1)):
                disorder += 1
    out["patients_dates_out_of_order"] = disorder
    return out


# -- K-BC-06 on the chain's twin (SLOPE-design-v2 section 11; contract 4.6c.11) -----------

RUNS = (
    # (kind, size, seed): ST2 at 20,000 rows (seeds 1 to 3) and 100,000 rows (seeds 1 to 3);
    # ST2-AGE at 20,000 rows (seeds 21 to 23) and 100,000 rows (seed 21); ST2 without dropout
    # (seeds 21 and 22); the long ST2, reported.
    ("st2", 20000, 1), ("st2", 20000, 2), ("st2", 20000, 3),
    ("st2age", 3000, 21), ("st2age", 3000, 22), ("st2age", 3000, 23),
    ("st2c", 3000, 21), ("st2c", 3000, 22),
    ("st2l", 1000, 1),
    ("st2", 100000, 1), ("st2", 100000, 2), ("st2", 100000, 3),
    ("st2age", 15000, 21),
)
TWIN_SEED = 7
SHUFFLE_SEED = 11
KEY = bytes(range(32))


def table_of(kind: str, size: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """One invented table of the runs: its header and rows."""
    import analyst_tables
    import patient_enumeration
    import patient_twin_tables

    if kind == "st2":
        return list(analyst_tables.ST2_COLUMNS), [row for row in analyst_tables.st2(size, seed)]
    if kind == "st2age":
        return patient_enumeration.st2_rows(size, seed, True)
    if kind == "st2c":
        return patient_twin_tables.st2_complete(size, seed)
    if kind == "st2l":
        return patient_twin_tables.st2_long(size, seed)
    if kind == "enc":
        return patient_twin_tables.encounter_like(size, seed)
    if kind == "lab":
        return patient_twin_tables.lab_like(size, seed)
    return patient_twin_tables.flowsheet_like(size, seed)


def one_run(kind: str, size: int, seed: int, folder: "object") -> "dict[str, object]":
    """One table: described behind the switch and plainly, both twins made, every K-BC-06 number measured."""
    import dataclasses

    import fixtures

    from synthtwin import chain, contract, generation, profile, reading, taxonomy, twinstore

    header, rows = table_of(kind, size, seed)
    person = ROLES[kind][0]
    place = pathlib.Path(f"{folder}")
    name = f"{kind}-{size}-{seed}"
    path = place / f"{name}.csv"
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(",".join(header) + "\n")
        for row in rows:
            handle.write(",".join(row) + "\n")
    real_columns = [[row[k] for row in rows] for k in range(len(header))]
    rows = []
    old_term = kind == "st2age"
    out: "dict[str, object]" = {"table": name, "rows": len(real_columns[0])}
    settings = dataclasses.replace(taxonomy.Settings(small_cell_floor=11), person_columns=(person,))
    table = reading.read_table(str(path), small_cell_floor=11)
    document = profile.build_document(table, settings, [person], [], [], subjects=[person], top_code=True)
    plain = fixtures.write_profile(place, f"{name}-plain.json", document)
    chained = chain.describe(table, document, settings, chain.ChainSwitch(name, KEY, rows_per_person=chain.ROWS_PERSON))
    table = None
    real = measured(kind, header, real_columns, 0, old_term)
    real_r = real.pop("r_values")
    out["real"] = real
    constant = constant_columns(header, real_columns, person)
    loaded_plain = contract.load_profile(str(plain))
    made = generation.generate_held(loaded_plain, TWIN_SEED)
    plain_columns = [twinstore.column_cells(one) for one in (made.held_columns or ())]
    made = None
    plain_m = measured(kind, header, plain_columns, 0, old_term)
    plain_m.pop("r_values")
    plain_m["varying_where_real_constant"] = varying_where_constant(header, plain_columns, person, constant)
    out["plain_twin"] = plain_m
    plain_columns = []
    if chained.grain is None or chained.statistical is None or chained.columns is None:
        out["layer"] = False
        return out
    out["layer"] = True
    # G16.17 case 10, asserted on every description this driver generates: no published patient-level cell, and no
    # row family's cell, holds 1 to f - 1 (HIPAA first; repair 1 of lane GRb, the first skeptic's item 7).
    floored = floor_cells(chained.statistical, chained.grain, 11)
    out["floor_cells"] = floored
    assert floored["patient_cells_1_to_f_minus_1"] == 0 and floored["row_cells_1_to_f_minus_1"] == 0, f"{name}: a published cell holds 1 to f - 1"
    switched = json.loads(json.dumps(document))
    switched["relationships"]["statistical"] = chained.statistical
    switched["relationships"]["grain"] = chained.grain
    switched["columns"] = chained.columns
    published = fixtures.write_profile(place, f"{name}-switched.json", switched)
    out["derived"] = [entry["name"] for entry in chained.grain["derived"]]
    out["trend_published"] = len(chained.grain["trend"])
    chained = None
    loaded = contract.load_profile(str(published), chain=True)
    made = generation.generate_held(loaded, TWIN_SEED)
    names = [column.name for column in loaded.columns]
    twin_columns = [twinstore.column_cells(one) for one in (made.held_columns or ())]
    out["deviations"] = sorted({f"{one.fact}" for one in made.deviations if f"{one.fact}".startswith("grain.")})
    made = None
    out["checks"] = grain_checks(loaded, names, twin_columns)
    # the shuffled control is the TWIN's reading shuffled over its rows (the first skeptic's item 4)
    twin = measured(kind, names, twin_columns, SHUFFLE_SEED, old_term)
    twin_r = twin.pop("r_values")
    twin["varying_where_real_constant"] = varying_where_constant(names, twin_columns, person, constant)
    out["twin"] = twin
    out["r_distance"] = r_distance(twin_r, real_r)  # type: ignore[arg-type]
    for file in place.glob(f"{name}*"):
        file.unlink()
    return out


def _within_half(twin: object, real: object) -> "bool | None":
    if not isinstance(twin, float) or not isinstance(real, float) or real == 0.0:
        return None
    return abs(twin - real) <= 0.5 * abs(real)


def judged(runs: "list[dict[str, object]]") -> "dict[str, object]":
    """K-BC-06's December clauses over the runs (SLOPE-design-v2 section 11, clauses (1) to (4) and (6); BC-ARCH 5.2)."""
    value: "dict[str, object]" = {}
    for label, picked in (("20k", [one for one in runs if one["table"].split("-")[0] in ("st2", "st2age") and int(f"{one['rows']}") < 50000]),
                          ("100k", [one for one in runs if one["table"].split("-")[0] in ("st2", "st2age") and int(f"{one['rows']}") >= 50000])):
        arm = 0
        slope = 0
        icc = 0
        old = 0
        old_runs = 0
        for one in picked:
            twin = one.get("twin")
            real = one.get("real")
            if not isinstance(twin, dict) or not isinstance(real, dict):
                continue
            tm = twin.get("model") if isinstance(twin.get("model"), dict) else {}
            rm = real.get("model") if isinstance(real.get("model"), dict) else {}
            assert isinstance(tm, dict) and isinstance(rm, dict)
            arm += 1 if _within_half(tm.get("arm_visit"), rm.get("arm_visit")) else 0
            slope += 1 if _within_half(twin.get("slope_diff"), real.get("slope_diff")) else 0
            if isinstance(tm.get("icc"), float) and isinstance(rm.get("icc"), float) and abs(tm["icc"] - rm["icc"]) <= 0.07:
                icc += 1
            if "old_visit" in rm:
                old_runs += 1
                old += 1 if _within_half(tm.get("old_visit"), rm.get("old_visit")) else 0
        value[f"runs_{label}"] = len(picked)
        value[f"arm_visit_within_half_{label}"] = arm
        value[f"slope_diff_within_half_{label}"] = slope
        value[f"icc_within_007_{label}"] = icc
        value[f"old_visit_within_half_{label}"] = old
        value[f"old_runs_{label}"] = old_runs
    cells = 0
    met = 0
    fixed = 1.0
    census = 0
    families = 0
    families_held = 0
    disorder = 0
    for one in runs:
        checks = one.get("checks")
        if not isinstance(checks, dict):
            continue
        cells += int(f"{checks['trend_cells']}")
        met += int(f"{checks['trend_met']}")
        fixed = min(fixed, float(f"{checks['fixed_constant']}"))
        census += 1 if checks["census_held"] else 0
        listed = checks["row_families"] if isinstance(checks["row_families"], list) else []
        families += len(listed)
        families_held += len([entry for entry in listed if entry["held"]])
        disorder += int(f"{checks['patients_dates_out_of_order']}")
    value["q_cells"] = cells
    value["q_cells_met"] = met
    value["fixed_constant_least"] = fixed
    value["census_exact_runs"] = census
    value["row_families"] = families
    value["row_families_held"] = families_held
    value["patients_dates_out_of_order"] = disorder
    value["runs"] = len(runs)
    stops = 0
    plain_stops = 0
    varying = 0
    plain_varying = 0
    skipped = 0
    floored = 0
    for one in runs:
        twin = one.get("twin")
        plain = one.get("plain_twin")
        if isinstance(twin, dict):
            stops += int(f"{twin.get('patients_with_several_arms', 0)}") + int(f"{twin.get('repeated_patient_visits', 0)}")
            held = twin.get("varying_where_real_constant")
            varying += int(f"{held.get('any', 0)}") if isinstance(held, dict) else 0
        if isinstance(plain, dict):
            plain_stops += int(f"{plain.get('patients_with_several_arms', 0)}") + int(f"{plain.get('repeated_patient_visits', 0)}")
            held = plain.get("varying_where_real_constant")
            plain_varying += int(f"{held.get('any', 0)}") if isinstance(held, dict) else 0
        checks = one.get("checks")
        if isinstance(checks, dict):
            skipped += int(f"{checks.get('skipped_for_a_held_source', 0)}")
        cells = one.get("floor_cells")
        if isinstance(cells, dict):
            floored += int(f"{cells['patient_cells_1_to_f_minus_1']}") + int(f"{cells['row_cells_1_to_f_minus_1']}")
    value["k_bc_10_stop_rows"] = stops
    value["k_bc_10_stop_rows_plain_twin"] = plain_stops
    # K-BC-10's third stop: twin persons holding more than one value of a column the real table holds constant
    # inside every patient, which only the CLASSED patient-fixed columns are built to keep (the statistics check's item 3)
    value["k_bc_10_persons_varying_where_real_constant"] = varying
    value["k_bc_10_persons_varying_where_real_constant_plain_twin"] = plain_varying
    value["families_and_cells_skipped_for_a_held_source"] = skipped
    value["case_10_cells_1_to_f_minus_1"] = floored
    return value


def main() -> int:
    """`--kpi`: K-BC-06 over the runs (every table at 20,000 rows and above), one KPI line; `--only KIND:SIZE:SEED` for one run."""
    import tempfile

    wanted = list(RUNS)
    if "--only" in sys.argv:
        spec = sys.argv[sys.argv.index("--only") + 1].split(":")
        wanted = [(spec[0], int(spec[1]), int(spec[2]))]
    runs: "list[dict[str, object]]" = []
    with tempfile.TemporaryDirectory() as folder:
        for kind, size, seed in wanted:
            runs += [one_run(kind, size, seed, folder)]
            print(json.dumps(runs[-1], sort_keys=True), file=sys.stderr, flush=True)
    value = judged(runs)
    print("KPI " + json.dumps({"id": "K-BC-06", "value": value, "detail": "several rows per patient on the chain's twin (lane GRb)"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
