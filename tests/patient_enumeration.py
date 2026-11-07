"""`K-S6-08`'s patient cases by exact enumeration (lane GRa, plan P4-D449; contract 4.6c.10).

Each case enumerates every world a published description allows and asks
whether some union of the patients' TYPES is fixed or bounded inside 1 to
`f - 1` on every one of them (contract 4.6c's leak, ruling R1 as R3 reads
it), beside the product's own decision (`synthtwin.patient_rules`):

- THE CENSUS (4.6c.4): every census of 11 to 20 patients holding 1 to 5
  rows at the floor of 11; no candidate is eligible where the extra rows
  number 1 to 10 (`census_small_extra_eligible`, target 0);
- PWIT IN A CELL OF ONE `r` (4.6c.8 step 3), at `f = 3`: every cell of 3
  to 6 patients of 2 or 3 rows over two bands; every union of patterns
  read over every world; PWIT's passes leak none (`pwit_passing_leaking`,
  target 0);
- THE FLOORED SPLIT IN A CELL OF TWO VALUES OF `r` (4.6c.2 (d), 4.6c.8
  step 4), at `f = 3`: two classes of 3 to 6 patients of 2 and 3 rows;
  every union of types read over every world; a description the split
  certifies leaks none (`split_passing_leaking`, target 0);
- THE CLASS WITNESS (4.6c.5 (e)), at `f = 11`: the first skeptic's
  `key_class_leak` fixture, one grain cell, every patient two rows, a
  two-band label, 11 to 80 patients; every description PWIT passes, read
  with the class `repeated` published (`V` and `V_K` at least `T + 1`);
  the witness refuses every one that then leaks
  (`witness_passing_leaking`, target 0), and the PWIT-only mutant does not
  (`witness_mutant_leaking` above 0);
- THE VISIT-TREND FIXTURES (4.6c.1, item 3 of 4.6c.10), lane MG's fifteen
  at their own floors of 2 and 3: under the product's SWING, 0 leaking
  passes (`trend_passing_leaking`, target 0) (`kpi_run --slow`: most of a
  minute and about 240 MB).

- THE DESIGN'S OWN FIXTURES (items 2 and 3): `fixed_rows.py` and
  `fixed_member_r3.py` ported (`fixed_rows_readings`), every reading 0 with
  the census withheld, its leak beside it; `attack_scale.py`'s cell read by
  SWING (`scale_attack`);
- THE CUTS OF THE TOP BAND (4.6c.8 step 4, `crossing_cuts`): two row families
  each passing alone whose margins leave no floored world, at `f = 11` and
  scaled at `f = 3` by exact enumeration: refused by R*'s one tie;
- THE TREND BESIDE THE COLUMN'S EXACT FACTS (item 4, departure 17 of 4.6c.12,
  `moment_fixtures`), one code in the middle of the ladder included;
- THE PAGE'S SMALL CASES (items 5 and 6, `page_cases`): a FINE child with a
  band of one reading, and the one-cell pigeonhole.

The moments' `MF1` to `MF5` (item 7) stay a stated limit of candidate (c),
cited and never passed: this layer publishes no such moment. Machine-free:
a few seconds, a few megabytes, but for the trend fixtures.
"""

import itertools
import typing

from synthtwin import patient_rules as pr


def _patterns(rows: int) -> "list[int]":
    """A patient's patterns over two bands, as its rows in the second band."""
    return list(range(rows + 1))


def _worlds(patients: int, rows: int, second: int) -> "list[tuple[int, ...]]":
    """Every multiset of patterns (counts per pattern) of `patients` patients holding `second` rows in band two."""
    out: "list[tuple[int, ...]]" = []
    for split in itertools.combinations_with_replacement(range(rows + 1), patients):
        if sum(split) == second:
            counts = [0] * (rows + 1)
            for one in split:
                counts[one] += 1
            out += [tuple(counts)]
    return out


def _leaks(worlds: "list[tuple[int, ...]]", floor: int) -> bool:
    """Whether some union of types holds 1 to `floor - 1` patients in every world."""
    width = len(worlds[0])
    for size in range(1, width + 1):
        for union in itertools.combinations(range(width), size):
            counts = [sum(world[at] for at in union) for world in worlds]
            if min(counts) >= 1 and max(counts) <= floor - 1:
                return True
    return False


def census_scan(floor: int = 11) -> "dict[str, int]":
    """Every census of 11 to 20 patients of 1 to 5 rows: none eligible with 1 to 10 extra rows."""
    censuses = 0
    small_extra = 0
    small_extra_eligible = 0
    for counts in itertools.product(range(0, 21), repeat=5):
        patients = sum(counts)
        if not 11 <= patients <= 20:
            continue
        censuses += 1
        values: "dict[int, int]" = {}
        for rho in range(5):
            if counts[rho]:
                values[rho + 1] = counts[rho]
        extra = sum((rho + 1) * counts[rho] for rho in range(5)) - patients
        if not 1 <= extra <= 10:
            continue
        small_extra += 1
        for lo in range(1, 7):
            if pr.census_eligible(pr.census_at(lo, values), floor)[0]:
                small_extra_eligible += 1
                break
    return {"censuses": censuses, "census_small_extra": small_extra, "census_small_extra_eligible": small_extra_eligible}


def pwit_cells(floor: int = 3) -> "dict[str, int]":
    """Every cell of one `r` (3 to 6 patients, 2 or 3 rows, two bands): PWIT's verdicts against the leak."""
    cells = 0
    passing = 0
    passing_leaking = 0
    refused_leaking = 0
    for patients in range(3, 7):
        for rows in (2, 3):
            for second in range(0, patients * rows + 1):
                worlds = _worlds(patients, rows, second)
                cells += 1
                leaks = _leaks(worlds, floor)
                if pr.pwit(patients, [patients * rows - second, second], floor):
                    passing += 1
                    passing_leaking += 1 if leaks else 0
                else:
                    refused_leaking += 1 if leaks else 0
    return {"pwit_cells": cells, "pwit_passing": passing, "pwit_passing_leaking": passing_leaking, "pwit_refused_leaking": refused_leaking}


def split_cells(floor: int = 3) -> "dict[str, int]":
    """Cells of two values of `r` (2 and 3 rows, 3 to 6 patients each, two bands): the floored split against the leak."""
    cells = 0
    passing = 0
    passing_leaking = 0
    refused_clean = 0
    for first in range(3, 7):
        for second_class in range(3, 7):
            total = 2 * first + 3 * second_class
            for in_two in range(0, total + 1):
                worlds: "list[tuple[int, ...]]" = []
                for share in range(0, 2 * first + 1):
                    if not 0 <= in_two - share <= 3 * second_class:
                        continue
                    for one in _worlds(first, 2, share):
                        for other in _worlds(second_class, 3, in_two - share):
                            worlds += [one + other]
                if not worlds:
                    continue
                cells += 1
                found = pr.floored_split(
                    [pr.Klass(first, 2, (0, 0), (2, 2)), pr.Klass(second_class, 3, (0, 0), (3, 3))],
                    [total - in_two, in_two],
                    floor,
                )
                leaks = _leaks(worlds, floor)
                if found.blocks:
                    passing += 1
                    passing_leaking += 1 if leaks else 0
                elif not leaks:
                    refused_clean += 1
    return {"split_cells": cells, "split_passing": passing, "split_passing_leaking": passing_leaking, "split_refused_not_leaking": refused_clean}


def class_witness(floor: int = 11) -> "dict[str, int]":
    """The `key_class_leak` fixture: one grain cell, two rows a patient, a two-band label, 11 to 80 patients."""
    described = 0
    leaking = 0
    witness_passing_leaking = 0
    mutant_leaking = 0
    refused = 0
    for patients in range(11, 81):
        threshold = max(floor - 1, patients // 100)
        for second in range(0, 2 * patients + 1):
            first = 2 * patients - second
            if not pr.pwit(patients, [first, second], floor):
                continue
            described += 1
            # Worlds: (2, 0), (1, 1), (0, 2) patterns, the class `repeated`
            # published: V = x + z and V_K = y at least T + 1.
            worlds: "list[tuple[int, ...]]" = []
            for both_first in range(patients + 1):
                mixed = first - 2 * both_first
                both_second = patients - both_first - mixed
                if mixed < 0 or both_second < 0:
                    continue
                if both_first + both_second >= threshold + 1 and mixed >= threshold + 1:
                    worlds += [(both_first, mixed, both_second)]
            leaks = bool(worlds) and _leaks(worlds, floor)
            leaking += 1 if leaks else 0
            mutant_leaking += 1 if leaks else 0
            classes = [pr.Klass(patients, 2, (0, 0), (2, 2))]
            found = pr.floored_split(classes, [first, second], floor)
            passes = False
            if found.blocks:
                swung = pr.swung(found.blocks, classes, floor, threshold + 1)
                repeats, mixes = pr.witness_counts(swung)
                passes = repeats >= threshold + 1 and mixes >= threshold + 1
            refused += 0 if passes else 1
            witness_passing_leaking += 1 if (passes and leaks) else 0
    return {
        "witness_descriptions": described,
        "witness_leaking_with_class": leaking,
        "witness_refused": refused,
        "witness_passing_leaking": witness_passing_leaking,
        "witness_mutant_leaking": mutant_leaking,
    }


def patient_cases() -> "dict[str, int]":
    """Every patient case of `K-S6-08`, in one record."""
    out: "dict[str, int]" = {}
    for found in (census_scan(), pwit_cells(), split_cells(), class_witness()):
        for key in found:
            out[key] = found[key]
    return out


# -- THE CHECKS AT THE OWNER'S TABLE FLOOR (20,000 rows; `kpi_run --slow`) --


# At most this many visits a patient on the floor-size tables: a visit number past 125 lets the
# Safe Harbor age reach read the column as ages and set its values past 125 aside (lane SH2's
# rules), and the chain's recount, reading the cells as written, then refuses the whole table
# (measured on lane CHa2's merged line; named for the orchestrator in lane GRa's repair 2).
VISITS_MAX = 120


def _long_rows(patients_wanted: int, seed: int, complete: bool, heap: bool = False, twice: bool = False) -> "tuple[list[str], list[list[str]]]":
    """An invented long table: rows a patient heavy-tailed (or eight each), a group, a gender, a fixed age and two fixed dates, a visit date and number, a reading, a unit.

    `heap` writes one reading far below the rest on about one row in a
    hundred (the verify's `make_heaped_min`: a published `min` below `p01`).
    `twice` writes one visit number twice on one patient in twenty of three
    visits or more (the verify of lane GRa's repair 1, item 2), the table's
    draw untouched, so the rest of the table is the plain one's.
    """
    import math
    import random

    draw = random.Random(seed)
    rows: "list[list[str]]" = []
    for patient in range(patients_wanted):
        count = 8 if complete else 1 + int(math.exp(draw.gauss(math.log(3.0), 1.4)))
        group = draw.choice(["a", "b"])
        gender = draw.choice(["F", "M"])
        base = draw.gauss(100, 12)
        age = draw.randint(18, 104)
        born = f"{draw.randint(1920, 2005)}-{draw.randint(1, 12):02d}-{draw.randint(1, 28):02d}"
        joined = f"{draw.randint(2010, 2020)}-{draw.randint(1, 12):02d}-{draw.randint(1, 28):02d}"
        for j in range(min(count, VISITS_MAX)):
            day = 1 + 9 * j + draw.randint(0, 3)
            date = f"{2024 + day // 336}-{1 + (day // 28) % 12:02d}-{1 + day % 28:02d}"
            value = base + 0.6 * j + draw.gauss(0, 6)
            if heap and draw.random() < 0.01:
                value = 3.0
            rows += [[f"P{patient:06d}", group, gender, f"{age}", born, joined, date, f"{j + 1}", f"{value:.1f}", draw.choice(["mg", "ml", "units"])]]
        if twice and patient % 20 == 0 and min(count, VISITS_MAX) >= 3:
            rows[len(rows) - min(count, VISITS_MAX) + 2][7] = rows[len(rows) - min(count, VISITS_MAX) + 1][7]
    return ["pid", "group", "gender", "age", "birth_date", "joined", "visit_date", "visit_no", "value", "unit"], rows


def span_start(date: str, rung: str) -> str:
    """A day `YYYY-MM-DD` read at a time grain's rung: the start of its year, quarter or month, or the day itself."""
    if rung == "year":
        return f"{date[:4]}-01-01"
    if rung == "quarter":
        month = 1 + 3 * ((int(date[5:7]) - 1) // 3)
        return f"{date[:4]}-{month:02d}-01"
    if rung == "month":
        return f"{date[:7]}-01"
    return date[:10]


def _facts_scan(blocks: "list[dict[str, object]]", header: "list[str]", rows: "list[list[str]]", grain: "dict[str, object]", floor: int) -> "dict[str, int]":
    """Every published fact of the fixed age, the fixed dates and the visit number read against the table's truth.

    Reads what the counts leg cannot: an age above 90 anywhere (the patient
    block, a derived column's edges), a fixed date named at its published
    grain though 1 to `f - 1` patients hold it, a visit number's block.
    """
    import re

    of_name = {f"{block['name']}": block for block in blocks}
    out = {"layer_ages_above_90": 0, "layer_fixed_dates_small": 0, "layer_sequence_blocks": 0}

    def numbers(value: object) -> "list[float]":
        if isinstance(value, bool):
            return []
        if isinstance(value, (int, float)):
            return [float(value)]
        if isinstance(value, dict):
            return [one for item in value.values() for one in numbers(item)]
        if isinstance(value, list):
            return [one for item in value for one in numbers(item)]
        return []

    age = of_name["age"]
    tails = age["tails"] if isinstance(age.get("tails"), dict) else {}
    age_facts = [age.get("mean"), age.get("mode"), age.get("percentiles")] + [side.get("values") for side in tails.values() if isinstance(side, dict)]
    out["layer_ages_above_90"] += len([one for one in numbers(age_facts) if one > 90])
    for entry in typing.cast("list[dict[str, object]]", grain["derived"]):
        if entry["source"] == "age":
            out["layer_ages_above_90"] += len([one for one in typing.cast("list[str]", entry["edges"]) if float(one) > 90])
    # ...and a position list of the age (Codex's review of batch 4p, item 1: a list read from the cells as
    # the file wrote them published 91 and 92 beside a description top-coded at 90).
    for entry in typing.cast("list[dict[str, object]]", grain["positions"]):
        if entry["column"] == "age":
            out["layer_ages_above_90"] += len([one for one in typing.cast("list[object]", entry["values"]) if isinstance(one, str) and one.isdigit() and int(one) > 90])
    for name in ("birth_date", "joined"):
        block = of_name[name]
        place = header.index(name)
        held = {(row[0], row[place]) for row in rows}
        time_grain = block["time_grain"] if "time_grain" in block else None
        rung = f"{time_grain['rung']}" if isinstance(time_grain, dict) and "rung" in time_grain else "day"
        holders: "dict[str, int]" = {}
        for _patient, date in held:
            start = span_start(date, rung)
            holders[start] = holders.get(start, 0) + 1
        named = set(re.findall(r"\d{4}-\d{2}-\d{2}", repr({key: value for key, value in block.items() if key != "time_grain"})))
        out["layer_fixed_dates_small"] += len([one for one in named if 0 < holders.get(span_start(one, rung), 0) < floor])
    block = of_name["visit_no"]
    if any(block[key] not in (None, [], {}) for key in block if key not in ("name", "position", "role")):
        out["layer_sequence_blocks"] += 1
    return out


def floor_size_checks(rows_at_least: int = 20000) -> "dict[str, int]":
    """The patient layer on invented long tables at the owner's table floor: every count floored, the loader's S23 to S33 met.

    Four tables of at least `rows_at_least` rows and 1,000 patients: one of
    heavy-tailed rows a patient, two where every patient holds every visit
    (complete follow-up: no trend), the second with a heap at a published
    `min` below `p01` (4.6c.10 item 6), and the first again with a visit
    number written twice on a few patients (the verify of repair 1, item 2:
    its block stands empty, `layer_sequence_blocks`). Each is described with its person
    column behind the switch, every published count of the layer read
    against the floor, and the switched description loaded with the chain.
    """
    import dataclasses
    import json
    import pathlib
    import tempfile

    import fixtures

    from synthtwin import chain, contract, profile, reading, taxonomy

    out = {
        "layer_tables": 0, "layer_patients_at_least_1000": 0, "layer_counts_below_floor": 0, "layer_loader_refusals": 0,
        "complete_follow_up_trends": 0, "layer_ages_above_90": 0, "layer_fixed_dates_small": 0, "layer_sequence_blocks": 0,
    }
    with tempfile.TemporaryDirectory() as folder:
        for complete, heap, wanted, twice in ((False, False, 4200, False), (True, False, 2600, False), (True, True, 2600, False), (False, False, 4200, True)):
            header, rows = _long_rows(wanted, 7, complete, heap, twice)
            path = pathlib.Path(folder) / f"long-{int(complete)}{int(heap)}{int(twice)}.csv"
            with open(path, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(",".join(header) + "\n")
                for row in rows:
                    handle.write(",".join(row) + "\n")
            if len(rows) < rows_at_least:
                raise ValueError("the invented table is under the floor size")
            settings = dataclasses.replace(taxonomy.Settings(small_cell_floor=11), person_columns=("pid",))
            table = reading.read_table(str(path), small_cell_floor=11)
            document = profile.build_document(table, settings, ["pid"], [], [], subjects=["pid"], top_code=True)
            chained = chain.describe(table, document, settings, chain.ChainSwitch("long", bytes(range(32)), rows_per_person=chain.ROWS_PERSON))
            if chained.grain is None or chained.statistical is None:
                continue
            out["layer_tables"] += 1
            census = chained.grain["census"]
            patients = sum(band["patients"] for band in census["bands"]) + census["top"]["patients"]
            out["layer_patients_at_least_1000"] += 1 if patients >= 1000 else 0
            counted: "list[int]" = [band["patients"] for band in census["bands"]] + [census["top"]["patients"]]
            for family in chained.statistical["chain"]:
                counted += [cell for row in family["table"] for cell in row]
            for family in chained.grain["rows"]:
                counted += [cell for row in family["table"] for cell in row]
            out["layer_counts_below_floor"] += len([one for one in counted if 0 < one < 11])
            if complete:
                out["complete_follow_up_trends"] += len(chained.grain["trend"])
            switched = json.loads(json.dumps(document))
            switched["relationships"]["statistical"] = chained.statistical
            switched["relationships"]["grain"] = chained.grain
            switched["columns"] = chained.columns
            if chained.columns is not None:
                scanned = _facts_scan(chained.columns, header, rows, chained.grain, 11)
                for key in scanned:
                    out[key] += scanned[key]
            written = fixtures.write_profile(pathlib.Path(folder), f"long-{int(complete)}{int(heap)}{int(twice)}-profile.json", switched)
            try:
                contract.load_profile(str(written), chain=True)
            except Exception:  # noqa: BLE001 -- a refusal is the measurement
                out["layer_loader_refusals"] += 1
    return out


# -- THE VISIT-TREND FIXTURES (contract 4.6c.10 item 3; `kpi_run --slow`) --

# Lane MG's fifteen fixtures (its design study's `repair_fix.py`, F1 to
# F15): one patient cell of one `r`, codes 0 to `K`, the own-mean family
# cut on the code sum (`m_cuts`: a sum at or below a cut lies under it),
# the row family's bands (`h_cuts`, None for no row family), the floor,
# the cell sizes, and the row family's own-mean band of each fine band
# (None: the same bands).
TREND_FIXTURES = (
    ("F1", 3, 2, (1,), None, 2, (6, 7, 8, 9), None),
    ("F2", 3, 2, (2,), None, 2, (6, 7, 8, 9), None),
    ("F3", 3, 2, (1,), (2,), 2, (7, 8, 9), None),
    ("F4", 3, 2, (4,), None, 2, (6, 7, 8, 9), None),
    ("F5", 3, 2, (4,), (2,), 2, (7, 8, 9), None),
    ("F6", 2, 3, (1,), None, 2, (5, 6), None),
    ("F7", 2, 3, (2,), None, 2, (5, 6), None),
    ("F8", 3, 2, (1,), None, 3, (8, 9), None),
    ("F9", 5, 2, (4,), (3,), 2, (5,), None),
    ("F10", 4, 2, (1,), None, 2, (5, 6), None),
    ("F11", 3, 2, (1, 4), None, 2, (6, 7, 8, 9), None),
    ("F12", 3, 2, (1, 4), (2,), 2, (8, 9), (0, 0, 1)),
    ("F13", 3, 2, (2, 3), (2,), 2, (8, 9), (0, 0, 1)),
    ("F14", 2, 3, (2,), (1,), 2, (5, 6), None),
    ("F15", 3, 2, (2, 4), (2,), 2, (8, 9), (0, 0, 1)),
)


def _compositions(total: int, parts: int) -> "typing.Iterator[tuple[int, ...]]":
    """Every vector of `parts` counts summing to `total` (stars and bars), one at a time."""
    for bars in itertools.combinations(range(total + parts - 1), parts - 1):
        previous = -1
        counts: "list[int]" = []
        for bar in bars:
            counts += [bar - previous - 1]
            previous = bar
        counts += [total + parts - 2 - previous]
        yield tuple(counts)


def _union_fixed(projections: "set[tuple[int, ...]]", width: int, floor: int) -> "bool | None":
    """Whether some union of the low types holds 1 to `floor - 1` patients in every world; None past 22 types."""
    if width == 0 or any(sum(one) == 0 for one in projections):
        return False
    if width > 22:
        return None
    for mask in range(1, 1 << width):
        chosen = [at for at in range(width) if mask >> at & 1]
        if all(1 <= sum(one[at] for at in chosen) <= floor - 1 for one in projections):
            return True
    return False


def _low_projection(worlds: "list[tuple[int, ...]]", types: int, floor: int) -> "tuple[set[tuple[int, ...]], int]":
    """The worlds read on the types some world holds 1 to `floor - 1` times, and how many such types."""
    most = [0] * types
    for world in worlds:
        for at in range(types):
            if world[at] > most[at]:
                most[at] = world[at]
    low = [at for at in range(types) if 0 < most[at] <= floor - 1]
    return {tuple(world[at] for at in low) for world in worlds}, len(low)


def trend_fixture(codes: int, rows: int, m_cuts: "tuple[int, ...]", h_cuts: "tuple[int, ...] | None", floor: int, sizes: "tuple[int, ...]", coarse: "tuple[int, ...] | None") -> "dict[str, int]":
    """One fixture under the product's SWING (`patient_rules.swing_classes`'s reading and `swing_passes`).

    Every world of `n` patients' code sequences is enumerated; a base
    description (the own-mean family in patients and the row family in
    rows, each cell 0 or at least `f`, the row family certified by PWIT)
    that leaks without `Q_P` is set aside (charged to the families, as the
    design study charges it); every other base and published `Q_P`
    is one description, SWING read on its published counts, and the leak
    read exactly over its preimage. `Q_P` is offered beside a two-band row
    family only (contract 4.6c.12 departure 7): a fixture with no row
    family publishes no `Q_P` (`offered` 0).
    """
    out = {"offered": 0, "descriptions": 0, "passing": 0, "passing_leaking": 0, "leaking": 0, "inexact": 0, "base_unsafe": 0}
    if h_cuts is None or len(h_cuts) != 1:
        return out
    out["offered"] = 1
    types = list(itertools.product(range(codes + 1), repeat=rows))
    count = len(types)
    fine = len(m_cuts) + 1
    band_of_type = [sum(1 for cut in m_cuts if sum(one) > cut) for one in types]
    coarse_of = list(range(fine)) if coarse is None else list(coarse)
    coarse_bands = max(coarse_of) + 1
    cut = h_cuts[0]
    pattern_of = [(sum(1 for code in one if code < cut), sum(1 for code in one if code >= cut)) for one in types]
    s_of = [sum(code * (2 * at - rows + 1) for at, code in enumerate(one)) for one in types]
    ranges = [(0, cut - 1), (cut, codes)]
    sums = list(zip([0] + [one + 1 for one in m_cuts], list(m_cuts) + [codes * rows]))
    weights = [2 * (at + 1) - rows - 1 for at in range(rows)]
    for patients in sizes:
        bases: "dict[tuple[tuple[int, ...], tuple[tuple[int, ...], ...]], list[tuple[tuple[int, ...], int]]]" = {}
        for world in _compositions(patients, count):
            in_band = [0] * fine
            in_coarse = [0] * coarse_bands
            supply = [[0, 0] for _ in range(coarse_bands)]
            for at in range(count):
                held = world[at]
                if held:
                    in_band[band_of_type[at]] += held
                    place = coarse_of[band_of_type[at]]
                    in_coarse[place] += held
                    supply[place][0] += held * pattern_of[at][0]
                    supply[place][1] += held * pattern_of[at][1]
            if any(0 < one < floor for one in in_band):
                continue
            if any(0 < one < floor for cell in supply for one in cell):
                continue
            if not all(pr.pwit(in_coarse[place], supply[place], floor) for place in range(coarse_bands)):
                continue
            key = (tuple(in_band), tuple(tuple(cell) for cell in supply))
            total = sum(world[at] * s_of[at] for at in range(count) if world[at])
            bases.setdefault(key, []).append((world, total))
        for (in_band, supply), worlds in bases.items():
            projections, width = _low_projection([world for world, _total in worlds], count, floor)
            if _union_fixed(projections, width, floor) is not False:
                out["base_unsafe"] += 1
                continue
            classes: "list[pr.TrendClass]" = []
            caps: "list[tuple[int, list[int]]]" = []
            for band in range(fine):
                if not in_band[band]:
                    continue
                rows_there = supply[coarse_of[band]]
                members: "list[int]" = []
                for above in range(rows + 1):
                    pattern = (rows - above, above)
                    if any(pattern[beta] and not rows_there[beta] for beta in range(2)):
                        continue
                    arrangement = [ranges[0]] * pattern[0] + [ranges[1]] * pattern[1]
                    least_sum = sum(low for low, _high in arrangement)
                    most_sum = sum(high for _low, high in arrangement)
                    first = max(sums[band][0], least_sum)
                    last = min(sums[band][1], most_sum)
                    if first > last:
                        continue
                    peak = least_sum + sum(arrangement[j][1] - arrangement[j][0] for j in range(rows) if weights[j] > 0)
                    pair = pr.greedy_pair(arrangement, min(last, max(first, peak)))
                    if pair is None:
                        continue
                    bound = min(patients, in_band[band])
                    for beta in range(2):
                        if pattern[beta]:
                            bound = min(bound, rows_there[beta] // pattern[beta])
                    if bound <= 0:
                        continue
                    members += [len(classes)]
                    classes += [pr.TrendClass(pair[1], pair[0], bound)]
                caps += [(in_band[band], members)]
            by_q: "dict[int, list[tuple[int, ...]]]" = {}
            for world, total in worlds:
                by_q.setdefault(total // 2, []).append(world)
            for q_value, chosen in by_q.items():
                projections, width = _low_projection(chosen, count, floor)
                leak = _union_fixed(projections, width, floor)
                if leak is None:
                    out["inexact"] += 1
                    leak = tuple([0] * width) not in projections
                passing = bool(classes) and pr.swing_passes(q_value, rows, patients, classes, caps, codes, floor)
                out["descriptions"] += 1
                out["leaking"] += int(leak)
                out["passing"] += int(passing)
                out["passing_leaking"] += int(passing and leak)
    return out


def trend_fixtures() -> "dict[str, int]":
    """The fifteen fixtures under the product's SWING, summed (`K-S6-08`'s `trend_*` keys)."""
    out = {"trend_fixtures": 0, "trend_fixtures_offered": 0, "trend_descriptions": 0, "trend_passing": 0, "trend_passing_leaking": 0, "trend_leaking": 0, "trend_inexact": 0}
    for _name, codes, rows, m_cuts, h_cuts, floor, sizes, coarse in TREND_FIXTURES:
        found = trend_fixture(codes, rows, m_cuts, h_cuts, floor, sizes, coarse)
        out["trend_fixtures"] += 1
        out["trend_fixtures_offered"] += found["offered"]
        out["trend_descriptions"] += found["descriptions"]
        out["trend_passing"] += found["passing"]
        out["trend_passing_leaking"] += found["passing_leaking"]
        out["trend_leaking"] += found["leaking"]
        out["trend_inexact"] += found["inexact"]
    return out


# -- THE TREND BESIDE THE COLUMN'S EXACT FACTS (contract 4.6c.10 item 4, 4.6c.12 departure 17) --

# One cell `P` of one `r` beside `k` patients of one row outside it, the row
# family holding the two apart: the fixture, its codes `0 .. K`, the column's `L0`
# bands, the row family's cut, the floor, `|P|`, `k`, and the one heap published
# (a code whose rows the reader holds, or None).
MOMENT_FIXTURES = (
    ("M0, no band of one code", 4, ((0, 1), (2, 3, 4)), 2, 2, (7, 8), (2, 3, 4), None),
    ("M1, one code in the middle", 4, ((0, 1), (2,), (3, 4)), 2, 2, (7, 8), (2, 3, 4), None),
    ("M2, the low band one code a band", 4, ((0,), (1,), (2,), (3, 4)), 2, 2, (7, 8), (2, 3, 4), None),
    ("M3, the high band one code", 3, ((0, 1, 2), (3,)), 3, 2, (6, 7), (2, 3, 4), None),
    ("M4, one code in the middle of the low band", 3, ((0,), (1,), (2,), (3,)), 3, 2, (6, 7), (2, 3, 4), None),
    ("M5, M1 with one heap", 4, ((0, 1), (2,), (3, 4)), 2, 2, (7, 8), (2, 3, 4), 4),
)
MOMENT_WORLDS_MAX = 2000000


def _moment_key(rows_of: "list[tuple[int, int]]", l0: "tuple[tuple[int, ...], ...]", heap: "int | None") -> "tuple[object, ...]":
    """What a reader holds of some rows: their `L0` totals, code total, square total, and the heap's rows (`rows_of`: code, rows)."""
    totals = [0] * len(l0)
    total = 0
    square = 0
    heaped = 0
    for code, rows in rows_of:
        total += code * rows
        square += code * code * rows
        heaped += rows if code == heap else 0
        for band in range(len(l0)):
            if code in l0[band]:
                totals[band] += rows
    return tuple(totals), total, square, heaped


def _moment_add(first: "tuple[object, ...]", second: "tuple[object, ...]") -> "tuple[object, ...]":
    first_totals = typing.cast("tuple[int, ...]", first[0])
    second_totals = typing.cast("tuple[int, ...]", second[0])
    return (
        tuple(first_totals[at] + second_totals[at] for at in range(len(first_totals))),
        typing.cast(int, first[1]) + typing.cast(int, second[1]),
        typing.cast(int, first[2]) + typing.cast(int, second[2]),
        typing.cast(int, first[3]) + typing.cast(int, second[3]),
    )


def _leaks_over(worlds: "typing.Iterable[tuple[int, ...]]", floor: int) -> bool:
    """Whether some union of types holds 1 to `floor - 1` patients on every world (exact; past 22 low types, the conservative reading)."""
    listed = list(worlds)
    width = len(listed[0])
    most = [0] * width
    for world in listed:
        for at in range(width):
            if world[at] > most[at]:
                most[at] = world[at]
    low = [at for at in range(width) if 0 < most[at] <= floor - 1]
    projected = {tuple(world[at] for at in low) for world in listed}
    found = _union_fixed(projected, len(low), floor)
    return (tuple([0] * len(low)) not in projected) if found is None else found


def _trend_classes(codes: int, cut: int, rows: int, patients: int, supply: "tuple[int, int]") -> "tuple[list[pr.TrendClass], list[tuple[int, list[int]]]]":
    """SWING's classes for a cell with no own-mean band: each pattern the row family's table leaves non-zero (4.6c.1 (b) 1 to 3)."""
    ranges = [(0, cut - 1), (cut, codes)]
    weights = [2 * (at + 1) - rows - 1 for at in range(rows)]
    classes: "list[pr.TrendClass]" = []
    members: "list[int]" = []
    for above in range(rows + 1):
        pattern = (rows - above, above)
        if any(pattern[beta] and not supply[beta] for beta in range(2)):
            continue
        arrangement = [ranges[0]] * pattern[0] + [ranges[1]] * pattern[1]
        peak = sum(low for low, _high in arrangement) + sum(arrangement[j][1] - arrangement[j][0] for j in range(rows) if weights[j] > 0)
        pair = pr.greedy_pair(arrangement, peak)
        if pair is None:
            continue
        bound = patients
        for beta in range(2):
            if pattern[beta]:
                bound = min(bound, supply[beta] // pattern[beta])
        if bound > 0:
            members += [len(classes)]
            classes += [pr.TrendClass(pair[1], pair[0], bound)]
    return classes, [(patients, members)]


def trend_beside_moments(name: str, codes: int, l0: "tuple[tuple[int, ...], ...]", cut: int, floor: int, sizes: "tuple[int, ...]", outsides: "tuple[int, ...]", heap: "int | None", rows: int = 2) -> "dict[str, int]":
    """`Q_P` beside the column's exact mean and spread, its `L0` totals and one heap, every world enumerated.

    The reader holds the row family (the cell's rows and the outside rows in
    each of the child's two bands), the `L0` totals over all rows, the exact
    code total and square total over all rows, the heap's rows and `Q_P`, each
    reading on the grid inside the rungs (so the tails add nothing). Each
    description SWING passes is read at three levels: unions of TYPES (a
    patient's rows a band of the row family: this page's promise, 4.6c.11),
    the same at the column's `L0` bands, and unions of exact code vectors
    (the level limit 9 leaves open, its residue reported). A description
    the same facts leak without `Q_P` at that level is not charged to `Q_P`,
    and one publishing an `L0` total of 1 to `f - 1` rows is none the product writes.
    Three guards are read on each: the page's worst case (`O - n_one`), the
    pooled form (`min(O, n - n_one)`) and the product's (`pr.free_rows`).
    """
    out: "dict[str, int]" = {"descriptions": 0, "too_many": 0, "base_leaking_exact": 0, "base_leaking_bands": 0}
    for guard in ("page", "pooled", "product"):
        for key in ("passing", "types_leaking", "bands_leaking", "exact_leaking"):
            out[f"{guard}_{key}"] = 0
    vectors = list(itertools.product(range(codes + 1), repeat=rows))
    outside_band = [0 if code < cut else 1 for code in range(codes + 1)]
    band_of_code = [[band for band in range(len(l0)) if code in l0[band]][0] for code in range(codes + 1)]
    patterns = sorted({tuple(sorted(band_of_code[code] for code in one)) for one in vectors})
    pattern_of = [patterns.index(tuple(sorted(band_of_code[code] for code in one))) for one in vectors]
    for patients in sizes:
        for low_rows in range(0, patients * rows + 1):
            supply = (low_rows, patients * rows - low_rows)
            if any(0 < one < floor for one in supply) or not pr.pwit(patients, list(supply), floor):
                continue
            classes, caps = _trend_classes(codes, cut, rows, patients, supply)
            if not classes or not any(pr.swing_passes(q_value, rows, patients, classes, caps, codes, floor) for q_value in range(-rows * codes * patients, rows * codes * patients + 1)):
                continue
            allowed = [at for at, one in enumerate(vectors) if (low_rows or all(code >= cut for code in one)) and (supply[1] or all(code < cut for code in one))]
            if sum(1 for _world in itertools.islice(_compositions(patients, len(allowed)), MOMENT_WORLDS_MAX + 1)) > MOMENT_WORLDS_MAX:
                out["too_many"] += 1
                continue
            inside: "dict[tuple[object, ...], dict[int, list[tuple[int, ...]]]]" = {}
            s_of = [sum(code * (2 * at - rows + 1) for at, code in enumerate(vectors[place])) for place in allowed]
            in_low = [sum(1 for code in vectors[place] if code < cut) for place in allowed]
            for world in _compositions(patients, len(allowed)):
                if sum(world[at] * in_low[at] for at in range(len(allowed)) if world[at]) != low_rows:
                    continue
                total = sum(world[at] * s_of[at] for at in range(len(allowed)) if world[at])
                held: "dict[int, int]" = {}
                for at in range(len(allowed)):
                    if world[at]:
                        for code in vectors[allowed[at]]:
                            held[code] = (held[code] if code in held else 0) + world[at]
                key = _moment_key(list(held.items()), l0, heap)
                inside.setdefault(key, {}).setdefault(total // 2, []).append(world)
            for outside_rows in outsides:
                outer: "dict[tuple[int, int], dict[tuple[object, ...], list[tuple[int, ...]]]]" = {}
                for world in _compositions(outside_rows, codes + 1):
                    low_out = sum(world[code] for code in range(codes + 1) if outside_band[code] == 0)
                    supply_out = (low_out, outside_rows - low_out)
                    if any(0 < one < floor for one in supply_out):
                        continue
                    key = _moment_key([(code, world[code]) for code in range(codes + 1) if world[code]], l0, heap)
                    outer.setdefault(supply_out, {}).setdefault(key, []).append(world)
                for supply_out, by_moment in outer.items():
                    bases: "dict[tuple[object, ...], dict[int, list[tuple[list[tuple[int, ...]], list[tuple[int, ...]]]]]]" = {}
                    for key_in, by_q in inside.items():
                        for key_out, worlds_out in by_moment.items():
                            joined = _moment_add(key_in, key_out)
                            for q_value, worlds_in in by_q.items():
                                bases.setdefault(joined, {}).setdefault(q_value, []).append((worlds_in, worlds_out))
                    for joined, by_q_all in bases.items():
                        passing = [q_value for q_value in by_q_all if pr.swing_passes(q_value, rows, patients, classes, caps, codes, floor)]
                        if not passing:
                            continue

                        def worlds_of(parts: "list[tuple[list[tuple[int, ...]], list[tuple[int, ...]]]]") -> "typing.Iterator[tuple[int, ...]]":
                            for worlds_in, worlds_out in parts:
                                for left in worlds_in:
                                    for right in worlds_out:
                                        yield left + right

                        totals = typing.cast("tuple[int, ...]", joined[0])
                        if any(0 < one < floor for one in totals):
                            continue

                        def banded_of(world: "tuple[int, ...]") -> "tuple[int, ...]":
                            by_band = [0] * (len(patterns) + codes + 1)
                            for at in range(len(allowed)):
                                if world[at]:
                                    by_band[pattern_of[allowed[at]]] += world[at]
                            for code in range(codes + 1):
                                by_band[len(patterns) + band_of_code[code]] += world[len(allowed) + code]
                            return tuple(by_band)

                        whole = [one for q_value in by_q_all for one in worlds_of(by_q_all[q_value])]
                        base_exact = _leaks_over(whole, floor)
                        base_bands = _leaks_over({banded_of(one) for one in whole}, floor)
                        out["base_leaking_exact"] += int(base_exact)
                        out["base_leaking_bands"] += int(base_bands)
                        del whole
                        n_one = sum(totals[at] for at in range(len(l0)) if len(l0[at]) == 1)
                        everything = patients * rows + outside_rows
                        cells = pr.Cells(((pr.R_NAME, 0),), (2,), (outside_rows, patients), (0, 1))
                        table = [supply_out[0], supply_out[1], supply[0], supply[1]]
                        one_code = [sum(totals[at] for at in range(len(l0)) if len(l0[at]) == 1 and (l0[at][0] < cut) == (beta == 0)) for beta in range(2)]
                        product = pr.free_rows(cells, [(1, 1), (rows, rows)], [0, 1], 2, table, 2, one_code)
                        for q_value in passing:
                            exact = list(worlds_of(by_q_all[q_value]))
                            leak_exact = (not base_exact) and _leaks_over(exact, floor)
                            typed: "set[tuple[int, ...]]" = set()
                            for world in exact:
                                by_type = [0] * (rows + 1 + 2)
                                for at in range(len(allowed)):
                                    if world[at]:
                                        by_type[in_low[at]] += world[at]
                                for code in range(codes + 1):
                                    by_type[rows + 1 + outside_band[code]] += world[len(allowed) + code]
                                typed |= {tuple(by_type)}
                            leak_types = _leaks_over(typed, floor)
                            leak_bands = (not base_bands) and _leaks_over({banded_of(one) for one in exact}, floor)
                            out["descriptions"] += 1
                            for guard, free in (("page", outside_rows - n_one), ("pooled", min(outside_rows, everything - n_one)), ("product", product)):
                                if free >= floor:
                                    out[f"{guard}_passing"] += 1
                                    out[f"{guard}_types_leaking"] += int(leak_types)
                                    out[f"{guard}_bands_leaking"] += int(leak_bands)
                                    out[f"{guard}_exact_leaking"] += int(leak_exact)
    del name
    return out


def moment_fixtures() -> "dict[str, int]":
    """Every fixture of `MOMENT_FIXTURES`, summed: the product's guard reads 0 leaking at the page's level (`moment_types_leaking`)."""
    out = {
        "moment_descriptions": 0, "moment_product_passing": 0, "moment_types_leaking": 0, "moment_bands_residue": 0, "moment_exact_residue": 0,
        "moment_pooled_passing": 0, "moment_pooled_exact_residue": 0, "moment_page_passing": 0, "moment_no_one_code_passing": 0, "moment_no_one_code_exact_residue": 0,
    }
    for fixture in MOMENT_FIXTURES:
        found = trend_beside_moments(*fixture)
        if fixture[0].startswith("M0"):
            out["moment_no_one_code_passing"] += found["product_passing"]
            out["moment_no_one_code_exact_residue"] += found["product_exact_leaking"]
            continue
        out["moment_descriptions"] += found["descriptions"]
        out["moment_product_passing"] += found["product_passing"]
        out["moment_types_leaking"] += found["product_types_leaking"]
        out["moment_bands_residue"] += found["product_bands_leaking"]
        out["moment_exact_residue"] += found["product_exact_leaking"]
        out["moment_pooled_passing"] += found["pooled_passing"]
        out["moment_pooled_exact_residue"] += found["pooled_exact_leaking"]
        out["moment_page_passing"] += found["page_passing"]
    return out


# -- THE CUTS OF THE TOP BAND (4.6c.8 step 4; the first skeptic's item 3) ---


def _splits(patients: int, excess: int, most: int) -> "list[tuple[int, ...]]":
    """Every way `patients` patients hold `excess` extra rows, as patients by extra rows `0 .. most`."""
    out: "list[tuple[int, ...]]" = []

    def walk(value: int, left: int, room: int, held: "tuple[int, ...]") -> None:
        if value == 0:
            if room == 0:
                out.append((left,) + held)
            return
        for count in range(min(left, room // value) + 1):
            walk(value - 1, left - count, room - count * value, (count,) + held)

    walk(most, patients, excess, ())
    return out


def _bounded_inside(patients: int, excess: int, floor: int) -> bool:
    """Whether some "patients with at least `k` extra rows" lies inside 1 to `f - 1` on every split of `excess` over `patients` (closed form, no cap)."""
    for extra in range(1, excess + 1):
        least = 1 if excess > patients * (extra - 1) else 0
        most = min(patients, excess // extra)
        if least >= 1 and most <= floor - 1:
            return True
    return False


def crossing_cuts() -> "dict[str, int]":
    """Two row families' cuts of the top band that cross: each passes alone, together they fix a count, and R*'s tie refuses the second.

    At `f = 11` (the first skeptic's table: top-band cells of 30, 24, 12 and 30
    patients, margins 30 and 54 extra rows by `x`, 0 and 84 by `y`) the two
    margins force the cell of 12 to hold 30 extra rows, so "patients with at
    least 3 extra rows" lies in 1 to 10 on every table (closed form, exact).
    Scaled at `f = 3` (cells of 6, 6, 3 and 6; margins 5 and 6, 0 and 11) every
    world is enumerated: both margins leak, either alone does not.
    """
    out = {"cut_refused": 0, "cut_coarser_taken": 0, "cut_large_margins_leak": 0, "cut_large_alone_leak": 0, "cut_small_both_leak": 0, "cut_small_alone_leak": 0, "cut_no_floored_world": 0}
    by_x = {frozenset((0, 2)): 30, frozenset((1, 3)): 54}
    by_y = {frozenset((0, 1)): 0, frozenset((2, 3)): 84}
    out["cut_refused"] = int(pr.blocks_joined(by_x, by_y) is None)
    both = pr.blocks_joined({frozenset((0, 1, 2, 3)): 84}, by_x)
    out["cut_coarser_taken"] = int(both == by_x)
    out["cut_large_margins_leak"] = int(_bounded_inside(12, 30, 11))
    # Alone, `x`'s margin lets the cell of 12 hold anything from 0 to 30 extra rows: every count may be 0.
    out["cut_large_alone_leak"] = int(all(_bounded_inside(12, share, 11) for share in range(0, 31)))
    cells = pr.Cells(((pr.R_NAME, 0), ("x", 0), ("y", 0)), (1, 2, 2), (30, 24, 12, 30), (0, 0, 0, 0))
    out["cut_no_floored_world"] = int(pr.r_star_of(cells, [(4, None)], 4, {frozenset((2,)): 30, frozenset((0,)): 0, frozenset((1,)): 0, frozenset((3,)): 54}, 11) is None)
    sizes = (6, 6, 3, 6)
    most = 11
    worlds: "dict[tuple[int, int, int, int], list[tuple[int, ...]]]" = {}
    for first in range(0, 6):
        for second in range(0, 7):
            for third in range(0, 6):
                for fourth in range(0, 12):
                    shares = (first, second, third, fourth)
                    if first + third != 5 or second + fourth > 17:
                        continue
                    combined: "list[tuple[int, ...]]" = [()]
                    for at in range(4):
                        combined = [one + split for one in combined for split in _splits(sizes[at], shares[at], most)]
                        if len(combined) > 200000:
                            break
                    worlds[shares] = combined
    margin_x = [one for shares in worlds if shares[0] + shares[2] == 5 and shares[1] + shares[3] == 6 for one in worlds[shares]]
    margin_both = [one for shares in worlds if shares == (0, 0, 5, 6) for one in worlds[shares]]
    out["cut_small_both_leak"] = int(_leaks_over(margin_both, 3))
    out["cut_small_alone_leak"] = int(_leaks_over(margin_x, 3))
    return out


# -- THE DESIGN'S OWN FIXTURES, PORTED (contract 4.6c.10 items 2 and 3) ------


def _level_rows(patients: int, rows: int, most: int) -> "list[tuple[int, ...]]":
    """Patients of one level by `r = 1 .. most`: `patients` patients holding `rows` rows."""
    out: "list[tuple[int, ...]]" = []

    def walk(value: int, left: int, room: int, held: "tuple[int, ...]") -> None:
        if value == most:
            if room == most * left:
                out.append(held + (left,))
            return
        for count in range(left + 1):
            after = left - count
            rest = room - value * count
            if (value + 1) * after <= rest <= most * after:
                walk(value + 1, after, rest, held + (count,))

    if patients == 0:
        return [tuple([0] * most)] if rows == 0 else []
    walk(1, patients, rows, ())
    return out


def _union_count(worlds: "list[tuple[int, ...]]", width: int, floor: int) -> int:
    """How many unions of the `width` cells lie inside 1 to `floor - 1` on every world (depth first, the design's `leak_list`)."""
    if not worlds:
        return 0
    columns = [list(column) for column in zip(*worlds)]
    found = 0

    def walk(start: int, current: "list[int] | None") -> None:
        nonlocal found
        for at in range(start, width):
            summed = columns[at] if current is None else [one + other for one, other in zip(current, columns[at])]
            if min(summed) >= 1 and max(summed) <= floor - 1:
                found += 1
            walk(at + 1, summed)

    walk(0, None)
    return found


def fixed_rows_readings() -> "dict[str, int]":
    """`fixed_rows.py` and `fixed_member_r3.py`: a patient-fixed column's row census beside a family in patients, every table enumerated at `f = 11`.

    `fixed_rows.py`: 40 patients of one row, 25 of `r` at least 2 (30 extra
    rows beyond 2), a family `{gender | r band}` of 20, 20, 12 and 13; the gender's
    row census 49 and 71 fixes each cell's excess. Without the census the
    fixture reads clean, with it a union leaks, and 4.6c.5 (c) withholds it
    (`_fixed_rows`: the top band stands in both levels and no row family has
    the column as a parent). `fixed_member_r3.py`: the same rows with `r` a
    member of no family: its three readings, the census withheld where the
    column's count in patients is published (the rule's reading 0).
    """
    import types

    from synthtwin import chain_rules as rules
    from synthtwin import patient_layer

    out: "dict[str, int]" = {}
    most = 5
    top = {"F": 12, "M": 13}
    excess = {"F": 5, "M": 25}

    def top_splits(patients: int, extra: int) -> "list[tuple[int, ...]]":
        found: "list[tuple[int, ...]]" = []
        for c3 in range(patients + 1):
            for c4 in range(patients - c3 + 1):
                for c5 in range(patients - c3 - c4 + 1):
                    if c3 + 2 * c4 + 3 * c5 == extra:
                        found += [(patients - c3 - c4 - c5, c3, c4, c5)]
        return found

    without: "list[tuple[int, ...]]" = []
    for share in range(0, 31):
        for first_level in top_splits(top["F"], share):
            for second_level in top_splits(top["M"], 30 - share):
                without += [first_level + second_level]
    published = [first_level + second_level for first_level in top_splits(top["F"], excess["F"]) for second_level in top_splits(top["M"], excess["M"])]
    out["fixed_rows_unions_without_census"] = _union_count(without, 8, 11)
    out["fixed_rows_unions_with_census"] = _union_count(published, 8, 11)
    # The product's rule on this fixture: the census is not a function of the rest, so it is not published.
    ladder = rules.Ladder("gender", (("F",), ("M",)), ((0, 1), (0, 1), (0, 1)), (2, 2, 2), (32, 33), (True, True))
    r_ladder = rules.Ladder(pr.R_NAME, (("1",), ("2 or more",)), ((0, 1), (0, 1), (0, 1)), (2, 2, 2), (40, 25), (True, True))
    family = rules.Family(pr.R_NAME, 0, (("gender", 0),), 0, (20, 12, 20, 13))
    codes = [0] * 32 + [1] * 33
    r_codes = [0] * 20 + [1] * 12 + [0] * 20 + [1] * 13
    context = types.SimpleNamespace(
        codes_of={"gender": (codes, codes, codes), pr.R_NAME: (r_codes, r_codes, r_codes)},
        census=pr.census_at(2, {1: 40, 2: 25}), values_r=[(1, 1), (2, None)],
        patients=types.SimpleNamespace(r=[1] * 20 + [2] * 12 + [1] * 20 + [2] * 13), scales={"gender": ladder, pr.R_NAME: r_ladder},
    )
    out["fixed_rows_census_published"] = int(patient_layer._fixed_rows(context, "gender", [family], {}) is not None)  # type: ignore[arg-type]
    # `fixed_member_r3.py`: patients by gender and exact `r`, r = 1 on 40, gender 32 and 33.
    women_rows, men_rows = 49, 71
    with_patients: "list[tuple[int, ...]]" = []
    for rows_f in range(32, 120 - 33 + 1):
        for first_level in _level_rows(32, rows_f, most):
            for second_level in _level_rows(33, 120 - rows_f, most):
                if first_level[0] + second_level[0] == 40:
                    with_patients += [first_level + second_level]
    out["fixed_member_unions_census_withheld"] = _union_count(with_patients, 10, 11)
    published_too = [one for one in with_patients if sum((at + 1) * one[at] for at in range(5)) == women_rows and sum((at + 1) * one[5 + at] for at in range(5)) == men_rows]
    out["fixed_member_unions_census_published"] = _union_count(published_too, 10, 11)
    return out


def scale_attack() -> "dict[str, int]":
    """`attack_scale.py`'s cell on ST2's own published edges: 40 patients, `f = 11`, every row in the row band above 128, the own-mean band below 129.5."""
    import fractions

    grid = pr.Grid("x", fractions.Fraction(1), fractions.Fraction(0), 255)
    cells = pr.Cells((("(own mean of x)", 0),), (2,), (40, 0), (0, 0))
    found = pr.swing_classes(cells, [0], 40, 2, [0, 80, 0, 0], 2, [(0, 122), (128, 255)], grid, [fractions.Fraction(259, 2)], 0, [0, 1])
    passes = found is not None and pr.swing_passes(-60, 2, 40, found[0], found[1], 255, 11)
    return {"scale_attack_passing": int(passes)}


def page_cases() -> "dict[str, int]":
    """4.6c.10's small cases: a FINE child with a band of one reading takes the floored split; the one-cell pigeonhole is refused, its neighbour certified."""
    import fractions

    from synthtwin import chain_rules as rules

    out: "dict[str, int]" = {}
    grid = pr.Grid("x", fractions.Fraction(1), fractions.Fraction(0), 40)
    # A FINE child whose band is one reading wide: PWIT is not read (`spans_two`), the floored split is,
    # with the `V_K` witness of 4.6c.5 (e) item 2 (`pr.class_witness`; Codex's review of lane GRa, item 7).
    band_of_one = rules.Ladder("x", ((("p50", "p60"),), (("p60", None),)), ((0, 1), (0, 1), (0, 1)), (2, 2, 2), (20, 40), (True, True))
    block: "dict[str, object]" = {"percentiles": {"p50": 7, "p60": 7}, "role": "count", "name": "x"}
    out["fine_child_one_reading_spans_two"] = int(pr.spans_two(band_of_one, block, 0, grid))
    cells = pr.Cells(((pr.R_NAME, 0),), (1,), (30,), (0,))
    witness, witness_v = pr.class_witness(False, False, 11)
    out["fine_child_split_taken"] = int(pr.certificate(cells, [(2, 2)], [[0]], [30, 30], 2, [((2, 30),)], False, None, witness, 11, {}, witness_v))
    # `one_cell_pigeonhole.py`: 20 patients of two rows and a band of 21 of 40 rows; 22 with 23 of 44 pass.
    twenty = pr.Cells(((pr.R_NAME, 0),), (1,), (20,), (0,))
    out["one_cell_pigeonhole_passing"] = int(pr.pwit(20, [21, 19], 11)) + int(pr.certificate(twenty, [(2, 2)], [[0]], [21, 19], 2, [((2, 20),)], False, None, None, 11, {}))
    out["one_cell_neighbour_passing"] = int(pr.pwit(22, [23, 21], 11))
    return out


# -- ST2 AND ST2-AGE AT THE OWNER'S TABLE FLOOR (the statistics skeptic's item 1) --


def st2_rows(subjects: int, seed: int, old_term: bool = False) -> "tuple[list[str], list[list[str]]]":
    """An invented visit table: a narrow reading written to one decimal, rungs one grid step apart in its middle, up to eight visits with dropout.

    `old_term` adds the design's `ST2-AGE` trend on the older half. This
    is the shape the page's trend was built on: the reading of few rungs a
    grid step apart is what a laboratory value looks like, so the guard of
    4.6c.1 (b) 6 must not read every row of those bands as outside a cell.
    """
    import math
    import random

    draw = random.Random(seed)
    rows: "list[list[str]]" = []
    for subject in range(subjects):
        arm = 1 if draw.random() < 0.5 else 0
        age = int(min(90, max(25, draw.gauss(55, 12))))
        old = 1 if age >= 55 else 0
        base = draw.gauss(0, 0.8)
        previous: "float | None" = None
        for visit in range(8):
            if previous is not None:
                chance = -3.0 + 0.6 * (previous - 7.5)
                if draw.random() < math.exp(chance) / (1 + math.exp(chance)):
                    break
            trend = 0.02 * visit - 0.15 * arm * visit + (0.12 * old * visit if old_term else 0.0)
            value = round(7.5 + base + 0.01 * (age - 55) + trend + draw.gauss(0, 0.5), 1)
            rows += [[f"S{subject:05d}", f"{arm}", f"{age}", f"{visit}", f"{value}"]]
            previous = value
    return ["sid", "arm", "age", "visit", "reading"], rows


def st2_tables() -> "dict[str, int]":
    """`ST2` and `ST2-AGE` at about 20,000 rows, behind the switch: the cells of change over visits offered and published, every count floored, each loads."""
    import dataclasses
    import json
    import pathlib
    import tempfile

    import fixtures

    from synthtwin import chain, contract, profile, reading, taxonomy

    out = {"st2_trend_cells": 0, "st2_trend_published": 0, "st2_counts_below_floor": 0, "st2_loader_refusals": 0}
    with tempfile.TemporaryDirectory() as folder:
        for name, seed, old_term in (("st2", 1, False), ("st2age", 21, True)):
            header, rows = st2_rows(3000, seed, old_term)
            path = pathlib.Path(folder) / f"{name}.csv"
            with open(path, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(",".join(header) + "\n")
                for row in rows:
                    handle.write(",".join(row) + "\n")
            settings = dataclasses.replace(taxonomy.Settings(small_cell_floor=11), person_columns=("sid",))
            table = reading.read_table(str(path), small_cell_floor=11)
            document = profile.build_document(table, settings, ["sid"], [], [], subjects=["sid"], top_code=True)
            chained = chain.describe(table, document, settings, chain.ChainSwitch(name, bytes(range(32)), rows_per_person=chain.ROWS_PERSON))
            if chained.grain is None or chained.statistical is None or chained.columns is None:
                continue
            out["st2_trend_cells"] += chained.counts["trend_cells"]
            out["st2_trend_published"] += chained.counts["trend_published"]
            counted: "list[int]" = [cell for family in chained.statistical["chain"] for row in family["table"] for cell in row]  # type: ignore[union-attr, index, attr-defined]
            counted += [cell for family in chained.grain["rows"] for row in family["table"] for cell in row]  # type: ignore[union-attr, index, attr-defined]
            out["st2_counts_below_floor"] += len([one for one in counted if 0 < one < 11])
            switched = json.loads(json.dumps(document))
            switched["relationships"]["statistical"] = chained.statistical
            switched["relationships"]["grain"] = chained.grain
            switched["columns"] = chained.columns
            written = fixtures.write_profile(pathlib.Path(folder), f"{name}-profile.json", switched)
            try:
                contract.load_profile(str(written), chain=True)
            except Exception:  # noqa: BLE001 -- a refusal is the measurement
                out["st2_loader_refusals"] += 1
    return out
