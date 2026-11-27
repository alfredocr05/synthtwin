"""K-S6-02 clause (x), THE READER ON THE COMMAND'S PATH (lane BT3a, plan P4-D467; contract 4.6b.2).

The chain's reader reads every cell as its description read it
(`chain.described_cells`, `chain.declarations_read`): the Safe Harbor age
top-code with its placeholders set aside and its small top category
pooled, the year top-code, dates in disguise held, a column counted
absent, the comma the description inferred. The library-path drivers of
K-S6-02, K-S6-03 and K-S6-14 describe with `profile.build_document`'s
defaults (no top-code) and never meet those readings, so this clause runs
the SHIPPED COMMAND, `cli.main(["profile", ...])`, with the chain's switch
and the fixed test key, over the reach lane BT3a's step 0 measured
(`REACH`: every table of its cause table whose description changed a
column the chain reads, or whose chain the recount turned off, at 20,000
rows; GRa's long tables at 400 visits a patient) and the code-heavy and
mixed tables at 200,000 rows (`LEGS_200K`, each in a process of its own):

- `recount_columns` (at least): the eligible columns recounted, every
  column `chain.ineligible_reason` leaves eligible once no column is held
  (lane CHs's cost device, `+unheld`, where a hold masks the reader);
  `recount_off` (target 0) of them disagree with their published counts
  when read as the chain reads them, each named in `recount_off_named`;
- `reach_named`: each table's chain (`chain:N`, its families; `+grain`
  where the patient layer stands) or its other reason no chain is
  published, as the command ran it, and after `/` with the device where a
  hold turned it off;
- `scan_hits` (target 0) over `scan_tables` chained descriptions, each
  hit named in `scan_named`: a published cell of a family or patient
  table, or a moment's count, of 1 to 10; a reading, position-list value
  or derived column's edge of a top-coded column above its mark, or of a
  year column below its `top_coded_year`; a spelling the description set
  aside or held standing in a position list, an edge or a private note;
  and each column's block as the switched command published it (the
  patient table's block for a patient-fixed column) against the
  protections the rows' description gave that column: a value above its
  mark or below its year cut, a value it set aside or held, its remark
  that dates in disguise are held lost (lane BT3a's repair 1, LANE BT3
  RULINGS 4 (2) and 5 (1)), or its Safe Harbor mark (`top_coded`,
  `top_coded_year`) lost (repair 2, its verify's item 1); each set-aside
  spelling is checked in full, only the hit's own words naming it (repair
  2, RULINGS 6 (4)), in the private report's texts once its JSON is
  decoded, word by word, the words' ends shed of their punctuation
  (`_in_note`, LANE I4r RULINGS 2 (1));
- `scan_accepted_named` (reported, never counted in `scan_hits`): the one
  hit ruled accepted, BY NAME (`ACCEPTED_HITS`: the vitals export's weight
  read past 125 as no age, LANE BT3 RULINGS 3 (1) and 6 (3)); any other
  hit, that column's above its mark among them, counts;
- `loader_refused` (target 0): a chained description its own loader
  refuses (`contract.load_profile(..., chain=True)`);
- `legs_200k`: each 200,000-row leg's outcome, CPU seconds (process time)
  and exact lifetime footprint.

    PYTHONPATH=src:tests python tools/measurements/kpi_chain_recount.py [--kpi] [--no-200k] [--tables NAME,...] [--detail FILE]

Called by `kpi_band_totals.py --kpi` (K-S6-02's driver), one table at a
time, each 200,000-row leg in a process of its own.
"""

import contextlib
import dataclasses
import hashlib
import inspect
import io
import json
import math
import os
import pathlib
import random
import shutil
import subprocess
import sys
import tempfile
import time
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "tools" / "measurements"))

KEY = bytes(range(32))
ROWS = 20_000
BIG_ROWS = 200_000
# STEP 0'S REACH (lane BT3a's cause table, 85 tables at 20,000 rows on batch 4p's merged head): every table
# with a column whose cells or declarations the description changed (LANE BT3 RULINGS 2 (1)).
REACH = (
    "zoo:vitals", "zoo:us_vitals", "zoo:risk_adjustment", "analyst:ST1", "analyst:ST3", "analyst:ST4", "analyst:ST5",
    "analyst:ST6", "shape:probe", "shape:codes120", "shape:codes400", "shape:mixed", "shape:numeric", "shape:a0b",
    "long:000", "long:100", "long:110", "long:001", "wide:bedside_results", "wide:pharmacy_fills",
    "wide:pcornet_diagnosis", "wide:warehouse_export", "wide:workbook_1904", "wide:day_numbers", "wide:paired_clocks",
    # Lane BT3a's repair 1 (LANE BT3 RULINGS 4 (2) (c) and 5 (1)): batch 4p's sibling-sweep tables of 24,000 rows (an
    # age that runs with the visit, a year of birth fixed by patient, a year that runs with the visit, a year repeated
    # across patients) and GRa's heavy long table with three patient-fixed columns (an amount held as dates in
    # disguise on a few patients, a score with 222 and 333, a reading written with a decimal comma).
    "sweep:age_run", "sweep:year_fixed", "sweep:year_run_aligned", "sweep:year_repeated", "long:fixed",
)
LEGS_200K = ("shape:codes120", "shape:codes400", "shape:mixed+unheld")
# THE ONE HIT RULED ACCEPTED, BY TABLE, COLUMN AND KIND (LANE BT3 RULINGS 3 (1); its repair 2, RULINGS 6 (3)): the
# vitals export's weight, whose top-code keeps a value past 125 written as no age (11 cells, 125.1 to 129.9 kg), read
# so by the chain as by the description; no file holds it. A reading of it from the mark to 125 is no such case.
ACCEPTED_HITS = frozenset({"zoo:vitals: a reading of weight past 125, kept as no age"})
HOLDS = ("person", "held repeats", "subject open", "no person column")
CODES = tuple(word for at in range(12) for word in ("--code", f"code{at:02d}")) + tuple(
    word for at in range(10) for word in ("--code", f"padded{at:02d}")
)


def codes_table(path: pathlib.Path, rows: int, top: int) -> None:
    """The code-heavy table of 50 columns (lane CHs's driver shape): twelve codes, ten padded numbers topped at ``top``
    (or at 3,000, 800, 20,000 and 400 in turn where ``top`` is 0), three keys, ten labels, fifteen measurements."""
    draw = random.Random(20261104)
    letters = "ABCDEFGHJKLMNPRSTVWXYZ"
    vocabularies = []
    for at in range(12):
        size = (40, 100, 200, 400)[at % 4]
        vocabularies += [[f"{draw.choice(letters)}{draw.randrange(100):02d}.{draw.randrange(10)}" for _ in range(size)]]
    weights = [[1.0 / (rank + 1) for rank in range(len(vocabulary))] for vocabulary in vocabularies]
    words = ("north", "south", "east", "west", "inner", "outer", "upper", "lower", "first", "second", "third", "other")
    header = (
        [f"code{at:02d}" for at in range(12)] + [f"padded{at:02d}" for at in range(10)] + ["record", "order_key", "account"]
        + [f"label{at:02d}" for at in range(10)] + [f"value{at:02d}" for at in range(15)]
    )
    with path.open("w", encoding="utf-8", newline="\n") as out:
        out.write(",".join(header) + "\n")
        for row in range(rows):
            cells: "list[str]" = []
            for at in range(12):
                cells += [""] if draw.random() < 0.05 else [draw.choices(vocabularies[at], weights[at])[0]]
            for at in range(10):
                width = 6 if at % 2 == 0 else 7
                most = top if top else (3000, 800, 20000, 400)[at % 4]
                cells += [f"{min(int(draw.expovariate(4.0 / most)), most - 1):0{width}d}"]
            cells += [f"R{1000000 + row * 7 % 9000000:07d}", f"{40000000 + row:08d}", f"AC{(row * 7919) % 10000000:07d}"]
            for at in range(10):
                cells += [words[min(int(draw.expovariate(0.6)), 2 + at)]]
            for at in range(15):
                cells += [""] if at % 5 == 4 and draw.random() < 0.1 else [f"{draw.gauss(40 + 3 * at, 4 + at % 6):.1f}"]
            out.write(",".join(cells) + "\n")


def probe_table(path: pathlib.Path, rows: int) -> None:
    """The planning probe's table: labels, a declared padded code topped at 120, a count with every whole number from 126
    to 400 once, a measurement written with a decimal comma, a measurement and a small count."""
    draw = random.Random(20261105)
    tail_rows = set(draw.sample(range(rows), 275))
    tail_values = list(range(126, 401))
    draw.shuffle(tail_values)
    with path.open("w", encoding="utf-8", newline="\n") as out:
        out.write("ward,padded_code,visit_count,temp_c,weight,score\n")
        for row in range(rows):
            ward = "ABCDE"[min(int(draw.expovariate(0.7)), 4)]
            padded = f"{min(int(draw.expovariate(4.0 / 120)), 119):07d}"
            visits = tail_values.pop() if row in tail_rows else min(int(draw.expovariate(1.0 / 15)), 100)
            temp = f"{draw.gauss(37.0, 0.5):.1f}".replace(".", ",")
            out.write(f'{ward},{padded},{visits},"{temp}",{draw.gauss(72.0, 12.0):.1f},{min(int(draw.expovariate(0.4)), 10)}\n')


def _logistic(x: float) -> float:
    return 0.0 if x < -40 else 1.0 / (1.0 + math.exp(-x))


def a0b_table(path: pathlib.Path, rows: int) -> None:
    """Lane A0b's invented table of 50 columns (seed 1): ages, vitals, labs, outcomes, a follow-up, ten lab values and a
    ten-step chain of one factor, flags and counts, each from shared factors; absent values blank."""
    r = random.Random(1)
    g, u = r.gauss, r.random
    names = (["age", "gender", "mass_index", "sbp", "dbp", "hr", "lact", "crp", "flag0", "diab", "smoker", "died", "stay", "cost",
              "ward", "group", "readmit", "fu", "event"] + [f"lab{k}" for k in range(10)] + [f"ch{k}" for k in range(10)]
             + ["b1", "b2", "xor", "flag1", "flag2", "ins", "region", "stage", "visits", "vis2", "vis3"])
    with path.open("w", encoding="utf-8", newline="\n") as out:
        out.write(",".join(names) + "\n")
        for _ in range(rows):
            f1, f2, f3 = g(0, 1), g(0, 1), g(0, 1)
            age = min(95, max(18, int(g(55, 15))))
            gender = 1 if u() < 0.5 else 0
            mass_v = round(22 + 0.06 * age + 1.5 * gender + 4 * (0.5 * f1 + 0.866 * g(0, 1)), 1)
            mass = None if u() < (0.25 if age > 80 else 0.05) else mass_v
            sbp = int(100 + 0.5 * age + 0.8 * mass_v + 5 * gender + 0.3 * (age - 55) * gender + g(0, 10))
            dbp = int(0.55 * sbp + 10 + g(0, 7))
            hr = int(70 + 5 * f2 + g(0, 8))
            lact = round(math.exp(0.3 + 0.35 * f3 + 0.2 * g(0, 1)), 2)
            flag0 = 1 if u() < _logistic(-2.5 + (1.8 if lact > 4 else 0.0) + 0.02 * (age - 55)) else 0
            crp_v = round(math.exp(2 + 0.5 * f3 + 0.6 * g(0, 1)), 1)
            crp = None if u() < (0.08 if flag0 else 0.45) else crp_v
            diab = 1 if u() < _logistic(-2.2 + (1.2 if mass_v > 30 else 0.0) + 0.02 * (age - 55)) else 0
            sm = r.choices((0, 1, 2), (0.55, 0.28, 0.17))[0]
            cur = 1 if sm == 2 else 0
            eta = (-4.2 + 0.06 * max(0, age - 60) + 0.01 * (sbp - 130) + 1.0 * flag0 - 0.9 * flag0 * (1 if age > 75 else 0)
                   + 0.5 * diab + 0.3 * cur - 1.6 * diab * cur + (0.8 if age > 75 else 0.0))
            died = 1 if u() < _logistic(eta) else 0
            mu = 3 + 0.004 * (age - 55) ** 2 + 2 * flag0
            stay = int(r.gammavariate(2.0, mu / 2.0))
            cost = 0.0 if u() < 0.3 else round(math.exp(7 + 0.3 * stay ** 0.5 + 0.5 * g(0, 1)), 2)
            ward = min(11, int(r.expovariate(0.35)))
            grp = r.choices((0, 1, 2, 3, 4), (0.62, 0.2, 0.165, 0.01, 0.005))[0]
            readmit = 1 if u() < _logistic(-4.4 + 0.12 * ward + 0.7 * diab) else 0
            hazard = math.exp(0.03 * (age - 55) + 0.7 * flag0 + 0.4 * diab + 0.25 * gender)
            t_event = r.weibullvariate(900 / hazard, 1.3)
            censored = r.uniform(30, 1500)
            labs: "list[object]" = [
                round(10 + 0.8 * f1 + 0.5 * f2 + g(0, 1), 2), round(5 + (age - 55) ** 2 / 100.0 + g(0, 2), 2),
                round(3 + (2.0 if age > 70 else 0.0) + g(0, 1), 2), round(((age - 55) / 15.0) * (1 if gender else -1) + g(0, 1), 2),
                round(1 + 0.6 * f3 + g(0, 1), 2), round(50 + 4 * f1 - 3 * f3 + g(0, 5), 1), round(0.5 * hr + g(0, 4), 1),
                round(2 + 0.03 * age + 0.4 * f2 + g(0, 1), 2), round(g(0, 1) + 0.5 * f1 * f2, 2), round(7 + 0.5 * f2 + g(0, 1), 2),
            ]
            if u() < (0.4 if hr > 80 else 0.05):
                labs[9] = None
            steps: "list[object]" = []
            x = g(0, 1) + 0.3 * f1
            for _step in range(10):
                x = 0.6 * x + 0.8 * g(0, 1)
                steps += [round(x, 3)]
            b1 = 1 if u() < 0.5 else 0
            b2 = 1 if u() < 0.5 else 0
            xor = 1 if u() < (0.7 if (b1 ^ b2) else 0.3) else 0
            flag1 = 1 if u() < _logistic(-1 + 0.5 * f1) else 0
            flag2 = 1 if u() < _logistic(-2 + 0.03 * (age - 55) + 0.5 * gender) else 0
            ins = r.choices((0, 1, 2, 3), (0.4, 0.3, 0.2, 0.1) if age < 65 else (0.1, 0.1, 0.2, 0.6))[0]
            region = r.randrange(8)
            stage = min(3, max(0, int((age - 30) / 20 + g(0, 0.8))))
            visits = int(r.gammavariate(1.5, (2 + 0.05 * age) / 1.5)) if u() > 0.2 else 0
            vis2 = int(r.gammavariate(2.0, 1.5 + diab))
            vis3 = int(r.gammavariate(1.0, 3.0 + 2 * flag0))
            row: "list[object]" = ([age, gender, mass, sbp, dbp, hr, lact, crp, flag0, diab, sm, died, stay, cost, ward, grp,
                                   readmit, int(min(t_event, censored)), 1 if t_event <= censored else 0] + labs + steps
                                  + [b1, b2, xor, flag1, flag2, ins, region, stage, visits, vis2, vis3])
            out.write(",".join("" if cell is None else repr(cell) for cell in row) + "\n")


SWEEP_PATIENTS = 1200
SWEEP_VISITS = 20


def sweep_table(path: pathlib.Path, which: str) -> "tuple[str, ...]":
    """One of batch 4p's sibling-sweep tables (24,000 rows, 1,200 patients of 20 visits, `pid` the person by its name, an
    arm alternating by patient, a reading), written at ``path``: `age_run` an age of 80 plus the visit's index;
    `year_fixed` a year of birth fixed by patient from 1925 to 1960, `year_run_aligned` a year of 1925 plus the visit's
    index, `year_repeated` a year from 1925 to 1960 repeated across patients and visits, each beside one stray cell `19`
    on a patient's sixth row; its declarations."""
    draw = random.Random(20261106)
    column = {"age_run": "age", "year_fixed": "birth_year"}.get(which, "year")
    lines = [",".join(["pid", "arm", column] + ([] if which == "age_run" else ["value"]))]
    at = 0
    for patient in range(SWEEP_PATIENTS):
        for visit in range(SWEEP_VISITS):
            arm = "a" if patient % 2 == 0 else "b"
            if which == "age_run":
                lines += [f"P{patient:05d},{arm},{80 + visit}"]
                continue
            year = {"year_fixed": 1925 + patient % 36, "year_run_aligned": 1925 + visit, "year_repeated": 1925 + (patient + visit) % 36}[which]
            lines += [f"P{patient:05d},{arm},{'19' if at == 5 else year},{draw.gauss(100, 12):.1f}"]
            at += 1
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    measured = (column,) if which == "age_run" else (column, "value")
    return ("--identifier", "pid") + tuple(word for one in measured for word in ("--measurement", one))


def fixed_long_rows() -> "tuple[list[str], list[list[str]]]":
    """GRa's heavy long table at up to 400 visits a patient with three patient-fixed columns beside it (lane BT3a's
    skeptic 1): `fee` 100 to 900, or 15000, 20000 or 25000 on about 3 in 100 patients; `score` 0 to 100 in steps of 5,
    or 222 or 333 on about 2 in 100; `base_temp` a reading of one place from 36,0 to 37,9 written with a decimal comma."""
    import patient_enumeration

    held_at = patient_enumeration.VISITS_MAX
    patient_enumeration.VISITS_MAX = 400
    try:
        header, body = patient_enumeration._long_rows(2600, 7, False)
    finally:
        patient_enumeration.VISITS_MAX = held_at
    draw = random.Random(99)
    fixed: "dict[str, dict[str, str]]" = {"fee": {}, "score": {}, "base_temp": {}}
    for row in body:
        if row[0] not in fixed["fee"]:
            fixed["fee"][row[0]] = f"{draw.choice([15000, 20000, 25000]) if draw.random() < 0.03 else 100 * draw.randint(1, 9)}"
            fixed["score"][row[0]] = f"{draw.choice([222, 333]) if draw.random() < 0.02 else 5 * draw.randint(0, 20)}"
            fixed["base_temp"][row[0]] = f"{36.0 + 0.1 * draw.randrange(20):.1f}".replace(".", ",")
    return header + list(fixed), [row + [fixed[name][row[0]] for name in fixed] for row in body]


def write_table(name: str, rows: int, folder: pathlib.Path) -> "tuple[pathlib.Path, tuple[str, ...], str]":
    """The named table written at ``rows`` rows: its path, its declarations and the subject question's answer."""
    from synthtwin import asking

    family, _, which = name.partition(":")
    folder.mkdir(parents=True, exist_ok=True)
    one_row_each = asking.ANSWER_ONE_ROW_EACH
    if family == "sweep":
        path = folder / f"{which}.csv"
        return path, sweep_table(path, which), ""
    if name == "long:fixed":
        header, body = fixed_long_rows()
        path = folder / "long-fixed.csv"
        with path.open("w", encoding="utf-8", newline="\n") as out:
            out.write(",".join(header) + "\n" + "".join(",".join(f'"{cell}"' if "," in cell else cell for cell in row) + "\n" for row in body))
        return path, ("--identifier", "pid"), ""
    if family in ("zoo", "wide"):
        import health_zoo
        import health_zoo_wide

        tables = health_zoo.TABLES if family == "zoo" else health_zoo_wide.WIDE_TABLES
        return health_zoo.write_table([one for one in tables if one.name == which][0], folder, rows, 1), (), one_row_each
    if family == "analyst":
        import analyst_tables

        path = folder / f"{which}.csv"
        analyst_tables.write(path, which, rows, 1)
        return path, (), one_row_each
    if family == "long":
        import patient_enumeration

        held_at = patient_enumeration.VISITS_MAX
        patient_enumeration.VISITS_MAX = 400
        try:
            header, body = patient_enumeration._long_rows(2600 if which[0] == "1" else 4200, 7, which[0] == "1", which[1] == "1", which[2] == "1")
        finally:
            patient_enumeration.VISITS_MAX = held_at
        path = folder / f"long-{which}.csv"
        with path.open("w", encoding="utf-8", newline="\n") as out:
            out.write(",".join(header) + "\n" + "".join(",".join(row) + "\n" for row in body))
        return path, ("--identifier", "pid"), ""
    path = folder / f"{which}-{rows}.csv"
    if which == "numeric":
        import kpi_scale

        kpi_scale.write_numeric(path, rows, 50)
    elif which == "mixed":
        import kpi_reader_memory

        kpi_reader_memory.write_table(path, rows)
    elif which in ("codes120", "codes400"):
        codes_table(path, rows, 120 if which == "codes120" else 0)
        return path, CODES, one_row_each
    elif which == "probe":
        probe_table(path, rows)
        return path, ("--code", "padded_code"), one_row_each
    elif which == "a0b":
        a0b_table(path, rows)
    else:
        raise SystemExit(f"no table {name}")
    return path, (), one_row_each


def footprint() -> int:
    """This process's lifetime peak physical footprint in bytes (macOS), or the resident high-water mark; -1 if neither."""
    if sys.platform == "darwin":
        import ctypes

        buffer = (ctypes.c_uint64 * 48)()
        library = ctypes.CDLL("/usr/lib/libproc.dylib")
        if library.proc_pid_rusage(os.getpid(), 4, ctypes.byref(buffer)) != 0:
            return -1
        return int(list(buffer)[2:][28])
    import resource

    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024


def _outcome(chained: object) -> str:
    """`chain:N` (N families, `+grain` where the patient layer stands), or the reason no chain is published, in a word."""
    from synthtwin import chain, patient_layer

    statistical = getattr(chained, "statistical")
    if statistical is not None:
        return f"chain:{len(statistical['chain'])}" + ("+grain" if getattr(chained, "grain") is not None else "")
    words = {chain.OFF_RECOUNT: "recount", chain.OFF_HELD_REPEATS: "held repeats", chain.OFF_SUBJECT: "subject open",
             chain.OFF_NO_PERSON: "no person column", chain.OFF_PERSON: "person", chain.OFF_FEW: "few columns",
             chain.OFF_ROOT: "root drew none", patient_layer.OFF_HELD: "held", patient_layer.OFF_PERSONS: "persons",
             patient_layer.OFF_BLANK: "blank person", patient_layer.OFF_MERGED: "merged", patient_layer.OFF_EXTRA: "extra rows",
             patient_layer.OFF_CENSUS: "no census", patient_layer.OFF_DRAWN: "census off"}
    notes = list(getattr(chained, "notes"))
    layer = [note for note in notes if note.startswith("the patient layer is off: ")]
    if layer:
        said = layer[-1][len("the patient layer is off: "):]
        return "layer " + (words[said] if said in words else said)
    offs = [note for note in notes if note.startswith("no chain is published: ")]
    said = offs[-1][len("no chain is published: "):] if offs else "off"
    return words[said] if said in words else said


def _device(document: "dict[str, object]", switch: object) -> "tuple[dict[str, object], object]":
    """Lane CHs's cost device: no column held and none held as an identifier; the subject question answered one row each
    where no person column stands."""
    from synthtwin import chain

    settings_block = document.get("settings")
    written = dict(document)
    persons: "list[object]" = []
    if isinstance(settings_block, dict):
        written["settings"] = dict(settings_block, forced_identifiers=[])
        persons = list(settings_block.get("person_columns") or [])
    rows = getattr(switch, "rows_per_person")
    if not persons and rows in (chain.ROWS_OPEN, chain.ROWS_UNNAMED, chain.ROWS_UNASKED):
        rows = chain.ROWS_ONE
    return written, dataclasses.replace(switch, held=(), held_by_person=(), rows_per_person=rows)  # type: ignore[type-var]


def _set_aside(written: "list[str]", cells: "list[str]") -> "frozenset[str]":
    """Every spelling of a column the description wrote blank, the WHOLE set: the scan checks each one (lane BT3a's
    repair 2, LANE BT3 RULINGS 6 (4); only a hit's own words name a spelling)."""
    return frozenset(one for one, two in zip(written, cells) if one != two and two == "" and one.strip())


def _reading_hit(name: str, readings: "tuple[tuple[object, int], ...]", mark: int) -> "list[str]":
    """A top-coded column's readings above its mark, named; past 125 years in the mark's unit alone, the kind
    `ACCEPTED_HITS` can name (a value past 125 the top-code keeps, written as no age)."""
    from synthtwin import taxonomy

    past = [value for value, _rows in readings if isinstance(value, (int, float)) and not isinstance(value, bool) and value > mark]
    if not past:
        return []
    if min(past) > taxonomy.TOP_CODE_REACH_CEILING * mark / taxonomy.TOP_CODE:
        return [f"a reading of {name} past 125, kept as no age"]
    return [f"a reading of {name} above its mark"]


def _counted(name: str, hits: "list[str]") -> "tuple[list[str], list[str]]":
    """One table's hits split into those `ACCEPTED_HITS` names (reported) and every other (counted), each prefixed
    with the table's name."""
    named = [f"{name}: {hit}" for hit in hits]
    return [hit for hit in named if hit in ACCEPTED_HITS], [hit for hit in named if hit not in ACCEPTED_HITS]


def _recount(table: object, document: "dict[str, object]", settings: object, codes: "list[str]", measured: "list[str]", commas: "list[str]", stored_as: "tuple[str, ...]", answered: "dict[str, int] | None" = None) -> "tuple[int, list[str], dict[str, frozenset[str]], list[str]]":
    """Every column eligible once nothing is held, recounted as the tree's chain reads it; each changed column's
    set-aside spellings; and each top-coded column the chain reads a value above the mark of. ``answered``: each age
    column's answered unit's mark, as the switch hands it to the chain."""
    from synthtwin import chain, reading
    from synthtwin import chain_rules as rules

    read_as = getattr(chain, "read_as_described", None)
    declarations = getattr(chain, "declarations_read", None)
    if declarations is not None:
        codes_read, measured_read, commas_read = declarations(document, codes, measured, commas)
    else:
        codes_read, measured_read, commas_read = set(codes), set(measured), set(commas)
    blocks = [block for block in document["columns"] if isinstance(block, dict)]  # type: ignore[union-attr]
    sequences = chain._sequence_places(document)
    blank_rows = rules.records_holding_nothing(document)
    persons = set((document.get("settings") or {}).get("person_columns") or [])  # type: ignore[union-attr]
    columns = 0
    off: "list[str]" = []
    aside: "dict[str, frozenset[str]]" = {}
    above: "list[str]" = []
    units = answered or {}
    for place, block in enumerate(blocks):
        name = f"{block.get('name')}"
        if name in persons or chain.ineligible_reason(block, place in sequences, False, set()) is not None:
            continue
        declared = {"code": name in codes_read, "measurement": name in measured_read, "decimal_comma": name in commas_read}
        stored = stored_as[place] if place < len(stored_as) else ""
        cells: "list[str] | None" = None
        if read_as is not None and units.get(name):
            found, cells = read_as(table, place, block, settings, declared, stored, blank_rows, units[name])
        elif read_as is not None:
            found, cells = read_as(table, place, block, settings, declared, stored, blank_rows)
        else:
            found = chain.read_column(table, place, block, settings, declared, stored, blank_rows)
        columns += 1
        if found is None or not found.agrees:
            off += [name]
        mark = block.get("top_coded")
        if found is not None and isinstance(mark, int) and not isinstance(mark, bool):
            above += _reading_hit(name, found.readings, mark)
        cut = block.get("top_coded_year")
        if found is not None and isinstance(cut, int) and not isinstance(cut, bool) and any(
            isinstance(value, (int, float)) and not isinstance(value, bool) and 1800 <= value < cut for value, _rows in found.readings
        ):
            above += [f"a reading of {name} below its year cut"]
        if cells is not None:
            written = reading.column_values(table, place)
            if cells is not written:
                aside[name] = _set_aside(written, cells)
    return columns, off, aside, above


def _marks(document: "dict[str, object]", key: str = "top_coded") -> "dict[str, int]":
    """Each top-coded column's mark (or, with ``key`` `top_coded_year`, its year cut), a whole number; a block carrying
    none, or carrying it emptied (`null`), has none."""
    out: "dict[str, int]" = {}
    columns = document.get("columns")
    for block in columns if isinstance(columns, list) else []:
        mark = block.get(key) if isinstance(block, dict) else None
        if isinstance(mark, int) and not isinstance(mark, bool):
            out[f"{block['name']}"] = mark
    return out


def _number(value: object) -> "float | None":
    """A published entry read as a number (a text such as `0000090` or `36,8` too), or None."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip().replace(",", "."))
        except ValueError:
            return None
    return None


def _figures(block: "dict[str, object]") -> "list[float]":
    """Every value a column block publishes (its ends, mean, mode, rungs, tails, empty edges and levels), never a count."""
    found: "list[object]" = [block.get(key) for key in ("min", "max", "mean", "median", "mode")]
    for key in ("percentiles", "percentiles_between"):
        part = block.get(key)
        found += list(part.values()) if isinstance(part, dict) else []
    tails = block.get("tails")
    for side in tails.values() if isinstance(tails, dict) else []:
        if isinstance(side, dict) and isinstance(side.get("values"), list):
            found += list(side["values"])
    edges = block.get("empty_edges")
    for pair in edges if isinstance(edges, list) else []:
        found += list(pair) if isinstance(pair, list) else []
    levels = block.get("levels")
    for level in levels if isinstance(levels, list) else []:
        if isinstance(level, dict):
            found += [level.get("label")]
    return [number for number in (_number(one) for one in found) if number is not None]


def _held_numbers(aside: "dict[str, frozenset[str]]") -> "dict[str, frozenset[float]]":
    """Each column's set-aside spellings read as numbers, once for the whole scan."""
    return {name: frozenset(number for number in (_number(one) for one in spellings) if number is not None) for name, spellings in aside.items()}


def _strings_in(found: object) -> "set[str]":
    """Every text a published object holds, as a key or a value, at any depth (a set-aside spelling stands in the
    chain where one equals it: the literal `"spelling"` its JSON writes)."""
    out: "set[str]" = set()
    waiting: "list[object]" = [found]
    while waiting:
        one = waiting.pop()
        if isinstance(one, str):
            out.add(one)
        elif isinstance(one, dict):
            out.update(f"{key}" for key in one)
            waiting += list(one.values())
        elif isinstance(one, (list, tuple)):
            waiting += list(one)
    return out


def _beyond(name: str, values: "list[object]", marks: "dict[str, int]", cuts: "dict[str, int]", held_numbers: "dict[str, frozenset[float]]", where: str) -> "list[str]":
    """Each value of ``values`` above the column's mark, below its year cut, or a spelling its reading set aside, named."""
    hits: "list[str]" = []
    held = held_numbers.get(name, frozenset())
    for value in values:
        number = _number(value)
        if number is None:
            continue
        if name in marks and number > marks[name]:
            hits += [f"{where} of {name} above its mark"]
        if name in cuts and 1800 <= number < cuts[name]:
            hits += [f"{where} of {name} below its year cut"]
        if number in held:
            hits += [f"{where} of {name} a value its description set aside or held"]
    return hits


def _strippable(one: str) -> bool:
    """A character a word of a note sheds at its ends: anything but a letter, a figure or a combining mark (Unicode
    categories L, N and M), so punctuation, quotation marks, brackets, symbols such as the backtick or the degree sign,
    and invisible format characters such as a zero-width space."""
    return unicodedata.category(one)[0] not in "LNM"


def _inside(word: str) -> "tuple[int, int]":
    """Where ``word``'s inside starts and ends once its ends shed every strippable character; (n, n) for a word of n
    strippable characters only."""
    start = 0
    while start < len(word) and _strippable(word[start]):
        start += 1
    end = len(word)
    while end > start and _strippable(word[end - 1]):
        end -= 1
    return start, end


def _report_texts(private: str) -> "list[str]":
    """Every text of the private report, its JSON decoded: each string and each key at any depth, a key written twice
    kept twice. A report that is not JSON is one text. A number, true, false or null is no text and is not read: the
    report's numbers are counts and statistics of the ladder's codes (contract 4.6d.1), never a spelling as the source
    wrote it, and a serialized number never stood alone between spaces for the space-split scan before this one."""
    try:
        decoded: object = json.loads(private, object_pairs_hook=lambda pairs: [part for pair in pairs for part in pair])
    except (ValueError, RecursionError):
        return [private]
    texts: "list[str]" = []
    waiting: "list[object]" = [decoded]
    while waiting:
        one = waiting.pop()
        if isinstance(one, str):
            texts += [one]
        elif isinstance(one, list):
            waiting += one
    return texts


def _note_words(texts: "list[str]") -> "tuple[dict[str, set[tuple[str, str]]], list[str], list[str]]":
    """The private report's words, each text split on any whitespace (a tab and a line break too): each word holding a
    letter, figure or mark indexed by its inside, with the ends it shed; each word strippable through; and each text
    with its words joined by one space, for a spelling of several words."""
    inside: "dict[str, set[tuple[str, str]]]" = {}
    bare: "list[str]" = []
    joined: "list[str]" = []
    for text in dict.fromkeys(texts):
        words = text.split()
        for word in words:
            start, end = _inside(word)
            if start == end:
                bare += [word]
            else:
                inside.setdefault(word[start:end], set()).add((word[:start], word[end:]))
        joined += [" ".join(words)]
    return inside, bare, joined


def _in_note(spelling: str, inside: "dict[str, set[tuple[str, str]]]", bare: "list[str]", joined: "list[str]") -> bool:
    """Whether ``spelling`` stands in the private report (`_note_words`) as a word, or as words in turn, once the
    words' ends shed strippable characters: `50000` stands in `value 50000`, `50000.`, `(50000);`, a quoted `50000`
    and `value<TAB>50000`, never in `500001`, `150000` or `50000.5`; a spelling with punctuation of its own (`-1`,
    `N/A`, `36,8`) stands where a word sheds characters down to it, never where a letter or figure is beside it."""
    words = spelling.split()
    if len(words) == 1:
        word = words[0]
        start, end = _inside(word)
        if start == end:
            return any(word in one for one in bare)
        front, back = word[:start], word[end:]
        return any(shed_front.endswith(front) and shed_back.startswith(back) for shed_front, shed_back in inside.get(word[start:end], ()))
    target = " ".join(words)
    for text in joined if words else []:
        at = text.find(target)
        while at >= 0:
            begin = text.rfind(" ", 0, at) + 1
            after = at + len(target)
            close = text.find(" ", after)
            if all(_strippable(one) for one in text[begin:at] + text[after:(len(text) if close < 0 else close)]):
                return True
            at = text.find(target, at + 1)
    return False


def _scan(
    document: "dict[str, object]", private: str, aside: "dict[str, frozenset[str]]", floor: int, read_marks: "dict[str, int]",
    read_cuts: "dict[str, int] | None" = None, row_blocks: "dict[str, dict[str, object]] | None" = None,
) -> "list[str]":
    """The HIPAA scan of one chained description and its private notes; each hit named.

    ``read_marks`` and ``read_cuts`` are the marks and year cuts of the
    description the chain read: the patient layer publishes a
    position-like column's block emptied, its mark `null`, and that
    column's position list is read against the mark the row description
    gave it. ``row_blocks`` are that description's blocks: each block as
    published is read against the protections its row block carries.
    ``aside`` holds each column's set-aside spellings WHOLE (`_set_aside`),
    each checked: the private report holds one standing as a word of any
    of its texts once ``private``'s JSON is decoded, the words' ends shed
    of their punctuation and quotation marks (`_in_note`; never the
    serialized text split on spaces, which left a closing quotation mark
    on a note's last word, LANE I4r RULINGS 2 (1)), the chain one a text
    of it equals (lane BT3a's repair 2, LANE BT3 RULINGS 6 (4)); one hit a
    column's spelling, however often it stands.
    """
    hits: "list[str]" = []
    held_numbers = _held_numbers(aside)
    relationships = document["relationships"]
    statistical = relationships["statistical"]  # type: ignore[index]
    grain = relationships.get("grain")  # type: ignore[union-attr]
    marks = _marks(document)
    marks.update(read_marks)
    cuts = _marks(document, "top_coded_year")
    cuts.update(read_cuts or {})
    tables = [family["table"] for family in statistical["chain"]]
    if isinstance(grain, dict):
        for family in grain.get("rows") or []:
            tables += [family["table"]]
        census = grain.get("census") or {}
        tables += [[[band.get("patients", 0) for band in census.get("bands") or []]]]
    for table in tables:
        for row in table:
            for cell in row if isinstance(row, list) else [row]:
                if isinstance(cell, int) and 0 < cell < floor:
                    hits += [f"a published cell of {cell}"]
    # The moments are read on the published ladder's codes (contract 4.6d.1),
    # never on values: their counts are scanned, and a value above the mark
    # is looked for where the chain reads values, its readings (`_recount`).
    moments = statistical.get("moments")
    if isinstance(moments, dict):
        for entry in moments.get("columns") or []:
            if isinstance(entry.get("n"), int) and 0 < entry["n"] < floor:
                hits += [f"moment n {entry['n']} of {entry.get('column')}"]
        for entry in moments.get("within") or []:
            for group in entry.get("groups") or []:
                if group and isinstance(group[0], int) and 0 < group[0] < floor:
                    hits += [f"a within group of {group[0]} on {entry.get('column')}"]
    lists = grain.get("positions") if isinstance(grain, dict) else None
    for entry in lists or []:
        name = entry.get("column") if isinstance(entry, dict) else None
        for value in (entry.get("values") or []) if isinstance(entry, dict) else []:
            if name in marks and isinstance(value, str):
                try:
                    above = float(value) > marks[name]
                except ValueError:
                    above = False
                if above:
                    hits += [f"a position value of {name} above its mark"]
            if name in aside and value in aside[name]:
                hits += [f"a set-aside spelling in a position list of {name}"]
            if isinstance(name, str) and name in cuts:
                hits += _beyond(name, [value], {}, cuts, {}, "a position value")
    # A derived column's edges (the own mean, the first date) are values of
    # their source (lane BT3a's repair 1, LANE BT3 RULINGS 4 (2) (b)).
    derived = grain.get("derived") if isinstance(grain, dict) else None
    for entry in derived or []:
        source = entry.get("source") if isinstance(entry, dict) else None
        if isinstance(source, str) and isinstance(entry.get("edges"), list):
            hits += _beyond(source, entry["edges"], marks, cuts, held_numbers, "a derived edge")
    # Each block as published against its row block's protections: the
    # patient layer publishes a patient-fixed column's block from the
    # patient table, whose own description is told of no hold.
    from synthtwin import taxonomy

    dated = taxonomy.rendered(taxonomy.REMARK_DATED_VALUES_HELD, ())
    columns = document.get("columns")
    for block in columns if isinstance(columns, list) and row_blocks else []:
        name = f"{block.get('name')}" if isinstance(block, dict) else ""
        row = (row_blocks or {}).get(name)
        if not isinstance(row, dict):
            continue
        row_marks = _marks({"columns": [row]})
        row_cuts = _marks({"columns": [row]}, "top_coded_year")
        figures = _figures(block)
        hits += _beyond(name, figures, row_marks, row_cuts, held_numbers, "a published value")
        remarks = row.get("remarks")
        if figures and isinstance(remarks, list) and dated in remarks and dated not in (block.get("remarks") or []):
            hits += [f"the remark that dates in disguise of {name} are held lost from its published block"]
        # ...and the rows' Safe Harbor marks, which the column's question, the
        # summary's sentence and a checked file's reading stand on (lane
        # BT3a's repair 2, its verify's item 1).
        for key in ("top_coded", "top_coded_year"):
            if figures and row.get(key) is not None and key not in block:
                hits += [f"the Safe Harbor mark {key} of {name} lost from its published block"]
    # Each set-aside spelling, the whole set: the private report's words, its
    # JSON decoded, and the chain's texts, each read once.
    inside, bare, joined = _note_words(_report_texts(private))
    texts = _strings_in(statistical)
    for name, spellings in aside.items():
        for spelling in sorted(spellings):
            if _in_note(spelling, inside, bare, joined) or spelling in texts:
                hits += [f"the set-aside spelling {spelling} of {name} in a note or the chain"]
    return hits


def run_table(name: str, rows: int, work: pathlib.Path) -> "dict[str, object]":
    """One table through the switched command: its outcome, recount, scan and loader."""
    from synthtwin import chain, cli, contract

    table_name, _, device = name.partition("+")
    path, declared, answer = write_table(table_name, rows, work / "tables")
    out = work / "out"
    data = work / "installation"
    shutil.rmtree(out, ignore_errors=True)
    shutil.rmtree(data, ignore_errors=True)
    out.mkdir(parents=True)
    data.mkdir(mode=0o700)
    (data / "chain-key").write_bytes(KEY)
    os.chmod(data / "chain-key", 0o600)
    found: "dict[str, object]" = {}
    real = chain.describe

    def describing(*given, **named):  # type: ignore[no-untyped-def]
        # Every argument the command hands the chain is handed on as given and read by the name `chain.describe` gives
        # it: batch 4r's merge put lane CHs's kept readings (plan P4-D462) ninth among them, beside a wrapper here that
        # took eight, and the first table stopped with a TypeError.
        arguments = inspect.signature(real).bind(*given, **named).arguments
        table, document, settings, switch = (arguments[key] for key in ("table", "document", "settings", "switch"))
        codes, measured, commas, stored_as = (arguments.get(key) for key in ("forced_codes", "forced_measurements", "forced_decimal_commas", "stored_as"))
        if device == "unheld":
            document, switch = _device(document, switch)
            arguments.update(document=document, switch=switch)
        result = real(**arguments)
        outcome = _outcome(result)
        if device != "unheld" and outcome in HOLDS:
            written, unheld = _device(document, switch)
            lifted = real(table, written, settings, unheld, codes, measured, commas, stored_as)
            outcome += " / " + _outcome(lifted)
            if lifted.statistical is not None:
                # The chain the device draws is scanned as the command's is.
                found["lifted"] = {"relationships": {"statistical": lifted.statistical, "grain": lifted.grain}, "columns": document["columns"]}
                found["lifted_private"] = json.dumps({"notes": list(lifted.notes), "moments": lifted.moments}, sort_keys=True, default=str)
        found["outcome"] = outcome
        answered = dict(getattr(switch, "ages_counted_in", ()) or ())
        columns, off, aside, above = _recount(table, document, settings, list(codes or []), list(measured or []), list(commas or []), stored_as or (), answered)
        found["columns"], found["off"], found["aside"], found["above"] = columns, off, aside, above
        found["private"] = json.dumps({"notes": list(result.notes), "moments": result.moments}, sort_keys=True, default=str)
        found["floor"] = settings.small_cell_floor
        found["marks"] = _marks(document)
        found["cuts"] = _marks(document, "top_coded_year")
        found["row_blocks"] = {f"{block.get('name')}": block for block in document["columns"] if isinstance(block, dict)}  # type: ignore[union-attr]
        return result

    chain.describe = describing  # type: ignore[assignment]
    began = time.process_time()
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            code = cli.main(["profile", str(path), "--out-dir", str(out), "--replace"] + list(declared), chain=cli.ChainRun(rows_per_person=answer, folder=str(data)))
    finally:
        chain.describe = real  # type: ignore[assignment]
    record: "dict[str, object]" = {"exit": code, "cpu": round(time.process_time() - began, 1), "outcome": found.get("outcome", "describe not reached"),
                                   "columns": found.get("columns", 0), "off": found.get("off", []), "hits": [], "refused": 0, "chained": False}
    written = sorted(out.glob("*-profile.json"))
    for one in written + sorted(out.glob("*-profile.txt")) + sorted(out.glob("*-questions.json")):
        record[one.name.rsplit("-", 1)[-1]] = hashlib.sha256(one.read_bytes()).hexdigest()[:16]
    record["private"] = hashlib.sha256(f"{found.get('private', '')}".encode("utf-8")).hexdigest()[:16]
    if written and "outcome" in found:
        document = json.loads(written[0].read_text(encoding="utf-8"))
        statistical = document["relationships"]["statistical"]
        if statistical is not None:
            record["ladder_digests"] = {f"{entry['column']}": hashlib.sha256(json.dumps(entry, sort_keys=True).encode("utf-8")).hexdigest()[:12] for entry in statistical["ladder"]}
        if document["relationships"]["statistical"] is not None:
            record["chained"] = True
            record["hits"] = list(found["above"]) + _scan(document, f"{found['private']}", found["aside"], int(f"{found['floor']}"), found["marks"], found["cuts"], found["row_blocks"])  # type: ignore[arg-type,call-overload]
            try:
                contract.load_profile(str(written[0]), chain=True)
            except Exception:  # noqa: BLE001 -- a refusal is the measurement
                record["refused"] = 1
    if "lifted" in found:
        record["chained"] = True
        record["hits"] = list(record["hits"]) + list(found["above"]) + _scan(found["lifted"], f"{found['lifted_private']}", found["aside"], int(f"{found['floor']}"), found["marks"], found["cuts"])  # type: ignore[arg-type,call-overload]
    shutil.rmtree(out, ignore_errors=True)
    shutil.rmtree(data, ignore_errors=True)
    path.unlink()
    return record


def _leg(name: str, rows: int) -> "dict[str, object]":
    """One 200,000-row leg in a process of its own: its outcome, recount, CPU seconds and exact lifetime footprint."""
    done = subprocess.run([sys.executable, str(pathlib.Path(__file__).resolve()), "--one", name, str(rows)],
                          capture_output=True, text=True, check=False)
    lines = [line for line in done.stdout.splitlines() if line.startswith("{")]
    if done.returncode != 0 or not lines:
        raise SystemExit(f"the {rows}-row leg {name} exited {done.returncode}: {done.stderr[-600:]}")
    return json.loads(lines[-1])


def measure(names: "tuple[str, ...]" = (), legs: bool = True, detail: str = "") -> "dict[str, object]":
    """Clause (x) over the reach (and the 200,000-row legs); with ``detail``, each table's record written there too."""
    reach = names or REACH
    named: "dict[str, str]" = {}
    off_named: "list[str]" = []
    scan_named: "list[str]" = []
    accepted_named: "list[str]" = []
    columns = refused = scanned = 0
    with tempfile.TemporaryDirectory() as folder:
        for name in reach:
            record = run_table(name, ROWS, pathlib.Path(folder))
            if detail:
                with open(detail, "a", encoding="utf-8") as out:
                    out.write(json.dumps({"name": name, **record}, sort_keys=True) + "\n")
            named[name] = f"{record['outcome']}"
            columns += int(f"{record['columns']}")
            off_named += [f"{name}: {column}" for column in record["off"]]  # type: ignore[attr-defined]
            accepted, counted = _counted(name, list(record["hits"]))  # type: ignore[call-overload]
            accepted_named += accepted
            scan_named += counted
            scanned += 1 if record["chained"] else 0
            refused += int(f"{record['refused']}")
    big: "dict[str, object]" = {}
    for name in LEGS_200K if legs else ():
        record = _leg(name, BIG_ROWS)
        big[name] = {key: record[key] for key in ("outcome", "columns", "off", "cpu", "peak_mb")}
        named[f"{name}@200000"] = f"{record['outcome']}"
        columns += int(f"{record['columns']}")
        off_named += [f"{name}@200000: {column}" for column in record["off"]]
        accepted, counted = _counted(f"{name}@200000", list(record["hits"]))
        accepted_named += accepted
        scan_named += counted
        scanned += 1 if record["chained"] else 0
        refused += int(f"{record['refused']}")
    # Every hit but the one `ACCEPTED_HITS` names counts (LANE BT3 RULINGS 6 (3)); the printed lists alone are cut.
    return {
        "recount_tables": len(named),
        "recount_columns": columns,
        "recount_off": len(off_named),
        "recount_off_named": off_named,
        "reach_named": named,
        "scan_tables": scanned,
        "scan_hits": len(scan_named),
        "scan_named": scan_named[:20],
        "scan_accepted_named": accepted_named,
        "loader_refused": refused,
        "legs_200k": big,
    }


def main() -> int:
    if "--one" in sys.argv:
        place = sys.argv.index("--one")
        name, rows = sys.argv[place + 1], int(sys.argv[place + 2])
        with tempfile.TemporaryDirectory() as folder:
            record = run_table(name, rows, pathlib.Path(folder))
        record["peak_mb"] = round(footprint() / 1048576, 1)
        print(json.dumps(record))
        return 0
    names = tuple(sys.argv[sys.argv.index("--tables") + 1].split(",")) if "--tables" in sys.argv else ()
    detail = sys.argv[sys.argv.index("--detail") + 1] if "--detail" in sys.argv else ""
    value = measure(names, "--no-200k" not in sys.argv, detail)
    if "--kpi" in sys.argv:
        print("KPI " + json.dumps({"id": "K-S6-02", "value": value, "detail": "clause (x), the reader on the command's path (lane BT3a)"}, sort_keys=True))
    else:
        print(json.dumps(value, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
