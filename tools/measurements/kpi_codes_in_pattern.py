"""K-HZ-10 and K-HZ-11: held-back codes written in pattern at 20,000 rows (plan P4-D439).

Lane CODES-1 of the zoo-fix track (wave6/ZOO/PLAN.md section 2.2; the
stand-ins page, P4-D422's ZS.2). Each table below is a long tail of
made-up codes written from one coding system's public grammar, 20,000
rows at the shipped floor of 11, described through the library with the
column declared `--code` (nobody at the keyboard), generated at seeds 0,
1 and 2, and validated -- the twin and the table both. A twin cell no
real cell writes is a stand-in; the driver counts the stand-ins outside
their system's grammar.

- K-HZ-10: the eighteen coding systems of K-P4-11
  (`tests/test_p4d19_declared_codes._SYSTEMS`), each widened to a long
  tail by the same generator: stand-in cells outside the system's
  grammar where the column publishes a form, systems writing `group-N`
  where a form is published, and UB-04 revenue codes not ending in 0;
  recorded beside them, the systems that publish no form at all (letters
  alone, a mark outside the set, or longer than a form) and their
  stand-in cells, which are lane CODES-2's (names, under the owner's Z1).
- K-HZ-11: the zoo plan's shapes -- ICD-10-CM with the dot, tumour stages
  (TNM), Glasgow coma scores, LOINC, NAACCR primary sites, i2b2
  `concept_cd`, Gleason scores, blood types and PCORnet's diagnoses --
  stand-in cells outside their grammar, and the twins and tables that
  fail validation.

Beside them (lane CODES-1's repair): K-HZ-10 counts the made-up whole
numbers of a column whose published codes are all whole numbers written
in figures alone that leave the published widths or ends (rule A3), and
K-HZ-11 counts the shapes whose held-back cells in the twin hold two equal
neighbouring figures more than one and a half times as often as the real
held-back cells do (ICD-10, PCORnet's diagnoses and i2b2's concepts; the
balanced walk's tie, rule A2), and records three system rules no pattern
reads, lane CODES-2's under Z1: Gleason scores whose sum is wrong, LOINC
codes whose check figure is wrong (the table's own rule, the sum of the
figures modulo 10), and NAACCR primary sites past C809. Since its second
repair: K-HZ-10 runs three dense declared scales beside the systems (physical-status
classes, Glasgow components beside totals, two codes beside four held
back) and counts their `group-N` cells and failing twins, and K-HZ-11
holds pathological tumour stages (`pT1aN1bM0`, `ypT2N0M1`) among its
shapes.

Every leak-free count here is machine-free: cells are compared as text, in
one pass each (a set of the real values; no pairwise count). The seconds
the library took are printed beside them.

    python tools/measurements/kpi_codes_in_pattern.py --kpi

`--rows N` runs the same tables at N rows, a smoke a lane takes below
the owner's table floor; kpi_run never passes it.
"""

import pathlib
import random
import re
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import fixtures  # noqa: E402
import kpi_rules  # noqa: E402
from synthtwin import contract, generation, profile, reading, rendering, taxonomy, validation  # noqa: E402

kpi_rules.guard_this_tree()

ROWS = 20_000
if "--rows" in sys.argv:
    ROWS = int(sys.argv[sys.argv.index("--rows") + 1])
FLOOR = 11
SEEDS = (0, 1, 2)


def _zipf(draw: random.Random, values: "list[str]", count: int, power: float) -> "list[str]":
    weights = [1.0 / ((rank + 1) ** power) for rank in range(len(values))]
    return draw.choices(values, weights=weights, k=count)


def _distinct(draw: random.Random, make: "object", count: int) -> "list[str]":
    """``count`` different codes from ``make`` (a function of the draw)."""
    found: "dict[str, int]" = {}
    tries = 0
    while len(found) < count and tries < count * 50:
        tries = tries + 1
        found[make(draw)] = 1  # type: ignore[operator]
    return list(found)


# -- K-HZ-10: the eighteen systems, widened to a long tail -----------------

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

SYSTEMS: "dict[str, tuple[object, int, str]]" = {
    # name: (one code from a draw, how many different codes, the grammar)
    "ndc": (lambda d: f"{d.randrange(10**4, 10**5):05d}-{d.randrange(10**3, 10**4):04d}-{d.randrange(0, 99):02d}", 3000, r"\d{5}-\d{4}-\d{2}"),
    "cvx": (lambda d: d.choice([f"{d.randrange(1, 99):02d}", f"{d.randrange(100, 300)}"]), 280, r"\d{2,3}"),
    "mvx": (lambda d: "".join(d.choice(LETTERS) for _ in range(3)), 900, r"[A-Z]{3}"),
    "udi": (lambda d: f"(01){d.randrange(10**13, 10**14)}(17){d.randrange(200000, 301231)}(10)LOT{d.randrange(100, 999)}", 2000, r"\(01\)\d{14}\(17\)\d{6}\(10\)LOT\d{3}"),
    "ms_drg": (lambda d: f"{d.randrange(1, 999):03d}", 900, r"\d{3}"),
    "apc": (lambda d: f"{d.randrange(1000, 9999)}", 3000, r"\d{4}"),
    "ub04_rev": (lambda d: f"{d.randrange(1, 999) * 10:04d}", 300, r"\d{3}0"),
    "npi": (lambda d: f"{d.randrange(10**9, 10**10)}", 4000, r"\d{10}"),
    "clinical_class": (lambda d: f"{d.randrange(1, 259)}", 250, r"\d{1,3}"),
    "elixhauser": (lambda d: d.choice(["CHF", "VALV", "PULMCIRC", "PERIVASC", "HTN", "PARA", "NRO", "CHRNLUNG", "DM", "HYPOTHY", "RENLFAIL", "LIVER", "ULCER", "AIDS", "LYMPH", "METS", "TUMOR", "ARTH", "COAG", "OBESE", "WGHTLOSS", "LYTES", "BLDLOSS", "ANEMDEF", "ALCOHOL", "DRUG", "PSYCH", "DEPRESS"]), 28, r"[A-Z]{2,8}"),
    "charlson": (lambda d: f"{d.randrange(0, 13)}", 13, r"\d{1,2}"),
    "cms_hcc": (lambda d: f"HCC{d.randrange(1, 189)}", 188, r"HCC\d{1,3}"),
    "cdps": (lambda d: f"{d.choice(['CAR', 'PSY', 'SKC', 'CNS', 'PUL', 'GI'])}-{d.choice(['L', 'M', 'H', 'VH'])}", 24, r"(CAR|PSY|SKC|CNS|PUL|GI)-(L|M|H|VH)"),
    "hgnc_id": (lambda d: f"HGNC:{d.randrange(1, 45000)}", 3000, r"HGNC:\d{1,5}"),
    "hgvs": (lambda d: f"NM_{d.randrange(10**5, 10**6):06d}.{d.randrange(1, 9)}:c.{d.randrange(1, 3000)}{d.choice('ACGT')}>{d.choice('ACGT')}", 3000, r"NM_\d{6}\.\d:c\.\d{1,4}[ACGT]>[ACGT]"),
    "omim": (lambda d: f"{d.randrange(100000, 620000)}", 3000, r"\d{6}"),
    "clinvar": (lambda d: f"VCV{d.randrange(10**8, 10**9):09d}", 3000, r"VCV\d{9}"),
    "ga4gh": (lambda d: "ga4gh:VA." + "".join(d.choice(LETTERS + LETTERS.lower() + "0123456789_-") for _ in range(32)), 3000, r"ga4gh:VA\.[A-Za-z0-9_-]{32}"),
}


# -- K-HZ-10's dense scales (lane CODES-1's second repair) ------------------
#
# Declared whole-number scales whose every number between the published ends
# is published, a level held back past one end: rule A3 keeps the ends only
# where they leave room (`generation._with_code_ends`), so these keep the
# ladder as it was -- held to the ends, their held-back cells came back
# `group-N` and the twin missed its count of numbers (the combined verify's
# item 2, Codex's item 1).


def _status_class(draw: random.Random) -> "list[str]":
    cells = draw.choices(["1", "2", "3", "4", "5"], weights=[20, 40, 30, 8, 2], k=ROWS - 5) + ["6"] * 5
    draw.shuffle(cells)
    return cells


def _gcs_beside_totals(draw: random.Random) -> "list[str]":
    cells: "list[str]" = []
    for _row in range(ROWS):
        e = int(draw.choices("1234", weights=[2, 3, 10, 85])[0])
        v = int(draw.choices("12345", weights=[2, 2, 3, 8, 85])[0])
        m = int(draw.choices("123456", weights=[1, 1, 2, 3, 8, 85])[0])
        cells += [f"E{e}V{v}M{m}" if draw.random() < 0.6 else f"{e + v + m}"]
    return cells


def _two_codes(draw: random.Random) -> "list[str]":
    half = (ROWS - 20) // 2
    cells = ["200"] * half + ["201"] * (ROWS - 20 - half) + ["198", "199", "202", "203"] * 5
    draw.shuffle(cells)
    return cells


DENSE: "dict[str, object]" = {
    "status_class": _status_class,
    "gcs_beside_totals": _gcs_beside_totals,
    "two_codes": _two_codes,
}


# -- K-HZ-11: the zoo plan's shapes at 20,000 rows -------------------------


def _icd10(draw: random.Random) -> "list[str]":
    def make(d: random.Random) -> str:
        head = f"{d.choice('ABCDEFGHIJKLMNOPQRSTVWXYZ')}{d.randrange(0, 100):02d}"
        tail = d.choice(["", f".{d.randrange(0, 10)}", f".{d.randrange(0, 100):02d}", f".{d.randrange(0, 1000):03d}{d.choice('ADS')}"])
        return head + tail
    return _zipf(draw, _distinct(draw, make, 1500), ROWS, 1.15)


def _tnm(draw: random.Random) -> "list[str]":
    cells: "list[str]" = []
    for _row in range(ROWS):
        t = draw.choices("01234", weights=[2, 40, 35, 15, 8])[0]
        n = draw.choices("0123", weights=[60, 25, 10, 5])[0]
        m = draw.choices("01", weights=[97, 3])[0]
        cells += [f"T{t}N{n}M{m}"]
    return cells


def _tnm_pathological(draw: random.Random) -> "list[str]":
    """Pathological stages, `pT1aN1bM0` and `ypT2N0bM1` (lane CODES-1's second repair, its verify's item 3)."""
    cells: "list[str]" = []
    for _row in range(ROWS):
        t = draw.choices("01234", weights=[2, 40, 35, 15, 8])[0]
        n = draw.choices("0123", weights=[60, 25, 10, 5])[0]
        m = draw.choices("01", weights=[97, 3])[0]
        cells += [f"{draw.choice(['p', 'yp'])}T{t}{draw.choice(['', 'a', 'b'])}N{n}{draw.choice(['', 'a', 'b'])}M{m}"]
    return cells


def _gcs(draw: random.Random) -> "list[str]":
    cells: "list[str]" = []
    for _row in range(ROWS):
        e = draw.choices("1234", weights=[2, 3, 10, 85])[0]
        v = draw.choices("12345", weights=[2, 2, 3, 8, 85])[0]
        m = draw.choices("123456", weights=[1, 1, 2, 3, 8, 85])[0]
        cells += [f"E{e}V{v}M{m}"]
    return cells


def _loinc(draw: random.Random) -> "list[str]":
    def make(d: random.Random) -> str:
        body = d.randrange(100, 100000)
        total = sum(int(c) for c in f"{body}") % 10
        return f"{body}-{total}"
    return _zipf(draw, _distinct(draw, make, 2000), ROWS, 1.1)


def _naaccr(draw: random.Random) -> "list[str]":
    return _zipf(draw, [f"C{value:03d}" for value in range(0, 810)], ROWS, 1.2)


def _concepts(draw: random.Random) -> "list[str]":
    def make(d: random.Random) -> str:
        kind = d.choices(["ICD10CM", "LOINC", "PRC", "DEM"], weights=[60, 20, 15, 5])[0]
        if kind == "ICD10CM":
            return f"ICD10CM:{d.choice('ABCDEFGHIJKLMNOPQRSTVWXYZ')}{d.randrange(0, 100):02d}.{d.randrange(0, 10)}"
        if kind == "LOINC":
            return f"LOINC:{d.randrange(1000, 99999)}-{d.randrange(0, 10)}"
        if kind == "PRC":
            return f"PRC:{d.randrange(10000, 99999)}"
        return d.choice(["DEM|LNG:E", "DEM|LNG:S", "DEM|ETHN:H", "DEM|ETHN:N", "DEM|ETHN:U"])
    return _zipf(draw, _distinct(draw, make, 2500), ROWS, 1.1)


def _gleason(draw: random.Random) -> "list[str]":
    scores = ["3+3=6", "3+4=7", "4+3=7", "4+4=8", "4+5=9", "5+4=9", "5+5=10", "3+5=8", "5+3=8"]
    return draw.choices(scores, weights=[4000, 3000, 1500, 800, 300, 200, 6, 5, 4], k=ROWS)


def _blood(draw: random.Random) -> "list[str]":
    return draw.choices(["O+", "A+", "B+", "O-", "A-", "AB+", "B-", "AB-"], weights=[38, 34, 9, 7, 6, 3, 2, 1], k=ROWS)


def _pcornet_dx(draw: random.Random) -> "list[str]":
    """Row 44's PCORnet diagnosis column at 20,000 rows: ICD-10 (a long tail),
    ICD-9 and SNOMED CT ids answered `code`, a few ICD-9 and SNOMED values
    under the floor among published ones (the critic's shape, wave6/ZOO
    CRITIC-work/probe_shapes.py, widened to the table floor)."""
    icd10 = _icd10(draw)
    icd9 = draw.choices(["250.00", "401.9", "486", "585.3", "311", "272.4"], weights=[900, 700, 300, 6, 8, 5], k=ROWS)
    snomed = draw.choices(["44054006", "38341003", "233604007", "431855005"], weights=[700, 300, 7, 3], k=ROWS)
    cells: "list[str]" = []
    for place in range(ROWS):
        kind = draw.choices([0, 1, 2], weights=[84, 11, 5])[0]
        cells += [(icd10, icd9, snomed)[kind][place]]
    return cells


SHAPES: "dict[str, tuple[object, str]]" = {
    "icd10_dotted": (_icd10, r"[A-Z]\d{2}(\.[0-9A-Z]{1,4})?"),
    "tnm": (_tnm, r"T[0-4]N[0-3]M[01]"),
    "tnm_pathological": (_tnm_pathological, r"y?pT[0-4][ab]?N[0-3][ab]?M[01]"),
    "gcs": (_gcs, r"E[1-4]V[1-5]M[1-6]"),
    "loinc": (_loinc, r"[1-9]\d{0,5}-\d"),
    "naaccr_site": (_naaccr, r"C\d{3}"),
    "i2b2_concept_cd": (_concepts, r"ICD10CM:[A-Z]\d{2}\.\d|LOINC:\d{4,5}-\d|PRC:\d{5}|DEM\|(LNG|ETHN):[A-Z]"),
    "gleason": (_gleason, r"[1-5]\+[1-5]=([2-9]|10)"),
    "blood_type": (_blood, r"(A|B|AB|O)[+-]"),
    "pcornet_dx": (_pcornet_dx, r"[A-Z]\d{2}(\.[0-9A-Z]{1,4})?|\d{3}(\.\d{1,2})?|\d{6,18}"),
}


# -- one table -------------------------------------------------------------


def _form_of(cell: str) -> str:
    """A cell's figures as `%` and letters as `@`, its marks as written."""
    return "".join("%" if ch.isdigit() else "@" if ch.isalpha() else ch for ch in cell)


def _one(folder: pathlib.Path, cells: "list[str]", pattern: str, seed: int) -> "dict[str, object]":
    """Describe, generate at ``seed``, validate both: the stand-ins out of pattern and the misses."""
    folder.mkdir(parents=True, exist_ok=True)
    table = fixtures.write(folder, "t.csv", fixtures.rows_to_csv(["code", "other"], [[cell, "x"] for cell in cells]))
    began = time.perf_counter()
    document = profile.build_document(
        reading.read_table(f"{table}", small_cell_floor=FLOOR),
        taxonomy.Settings(small_cell_floor=FLOOR),
        [],
        forced_codes=["code"],
    )
    described_seconds = time.perf_counter() - began
    written = fixtures.write_profile(folder, "t.json", document)
    described = contract.load_profile(f"{written}")
    began = time.perf_counter()
    twin = generation.generate(described, seed)
    generated_seconds = time.perf_counter() - began
    path = fixtures.write(folder, "twin.csv", rendering.twin_csv(twin))
    began = time.perf_counter()
    twin_missed = [c.subcheck for c in validation.measure(described, f"{path}").checks if c.verdict == validation.MISSED]
    source_missed = [c.subcheck for c in validation.measure(described, f"{table}").checks if c.verdict == validation.MISSED]
    validated_seconds = time.perf_counter() - began
    real = set(cells)
    block = document["columns"][0]
    forms = block["shape_forms"] if isinstance(block.get("shape_forms"), dict) else {}
    named = [form for form in forms if form != taxonomy.SUPPRESSED_LABEL]
    # A level's label is its folded spelling (`e11.9`); a cell is held back
    # where its folded spelling is no published level's.
    published = {level["label"] for level in block.get("levels") or [] if isinstance(level.get("label"), str)}
    # RULE A3'S WIDTHS AND ENDS: only where every published code is a whole
    # number written in figures alone.
    whole = bool(published) and all(label.isdigit() for label in published)
    widths = {len(label) for label in published} if whole else set()
    low = min(int(label) for label in published) if whole else 0
    high = max(int(label) for label in published) if whole else 0
    out = 0
    group = 0
    stand = 0
    off_ends = 0
    off_ends_out = 0
    gleason_broken = 0
    loinc_wrong = 0
    naaccr_past = 0
    for cell in twin.columns[0]:
        if not cell or cell in real:
            continue
        stand = stand + 1
        if cell.startswith("group-"):
            group = group + 1
        outside = not re.fullmatch(pattern, cell)
        if outside:
            out = out + 1
        if whole and cell.isdigit() and (len(cell) not in widths or not low <= int(cell) <= high):
            off_ends = off_ends + 1
            off_ends_out = off_ends_out + (1 if outside else 0)
        score = re.fullmatch(r"(\d+)\+(\d+)=(\d+)", cell)
        if score and int(score.group(1)) + int(score.group(2)) != int(score.group(3)):
            gleason_broken = gleason_broken + 1
        coded = re.fullmatch(r"(\d+)-(\d)", cell)
        if coded and sum(int(figure) for figure in coded.group(1)) % 10 != int(coded.group(2)):
            loinc_wrong = loinc_wrong + 1
        site = re.fullmatch(r"C(\d{3})", cell)
        if site and int(site.group(1)) > 809:
            naaccr_past = naaccr_past + 1
    # THE HELD-BACK CELLS' NEIGHBOURING FIGURES, the real against the twin
    # (the statistics skeptic's measure): over the cells no published level
    # writes, in each of the three forms the most real held-back cells wear
    # (30 cells or more), each two places of figures next to each other
    # among the form's figures and letters (marks skipped), leaving out a
    # place every real held-back cell of the form holds alike (a prefix).
    pairs: "dict[str, list[int]]" = {}
    severe = {"real": 0, "twin": 0}
    diagonal = {"real": [0, 0], "twin": [0, 0]}
    held_by_form: "dict[str, list[str]]" = {}
    for cell in cells:
        if cell and cell.strip().casefold() not in published:
            bucket = held_by_form.get(_form_of(cell))
            if bucket is None:
                held_by_form[_form_of(cell)] = [cell]
            else:
                bucket += [cell]
    varying: "dict[str, list[int]]" = {}
    commonest = sorted(held_by_form, key=lambda form: (-len(held_by_form[form]), form))[:3]
    for form in commonest:
        held_cells = held_by_form[form]
        if len(held_cells) < 30:
            continue
        pairs[form] = [0, 0, 0, 0]
        varying[form] = [
            at for at in range(len(form))
            if form[at] in "%@" and len({held[at] for held in held_cells}) > 1
        ]
    for side, column in (("real", cells), ("twin", list(twin.columns[0]))):
        for cell in column:
            if not cell or cell.strip().casefold() in published:
                continue
            places = varying.get(_form_of(cell), [])
            shift = 0 if side == "real" else 2
            for index in range(len(places) - 1):
                first, second = places[index], places[index + 1]
                if cell[first].isdigit() and cell[second].isdigit():
                    pairs[_form_of(cell)][shift] += 1 if cell[first] == cell[second] else 0
                    pairs[_form_of(cell)][shift + 1] += 1
            if re.fullmatch(r"[A-Z]\d\d\.\d", cell):
                diagonal[side][0] += 1 if cell[1] == cell[2] == cell[4] else 0
                diagonal[side][1] += 1
            coma = re.fullmatch(r"E(\d)V(\d)M(\d)", cell)
            if coma and sum(int(part) for part in coma.groups()) <= 8:
                severe[side] += 1
    # REAL HELD-BACK CODES THE TWIN WRITES (P4-D439's stated limit 2, the
    # owner's acceptance of 2026-09-18): twin cells equal to a real code
    # no published level writes, and how many different ones of how many.
    real_held = {cell for cell in cells if cell and cell.strip().casefold() not in published}
    rewritten = [cell for cell in twin.columns[0] if cell in real_held]
    for path_done in (table, written, path):
        path_done.unlink()
    return {
        "role": block["role"],
        "forms_named": len(named),
        "stand_in_cells": stand,
        "out_of_pattern": out,
        "group_n": group,
        "twin_missed": twin_missed,
        "source_missed": source_missed,
        "seconds": (round(described_seconds, 1), round(generated_seconds, 1), round(validated_seconds, 1)),
        "ub04_not_0": sum(1 for cell in twin.columns[0] if cell and cell not in real and not cell.endswith("0")),
        "number_off_widths_or_ends": off_ends,
        "number_off_widths_or_ends_out_of_pattern": off_ends_out,
        "gleason_sum_broken": gleason_broken,
        "loinc_check_figure_wrong": loinc_wrong,
        "naaccr_past_c809": naaccr_past,
        "held_back_neighbouring_figures_equal": pairs,
        "gcs_cells_8_or_less": severe,
        "real_held_back_codes_written": [len(rewritten), len(set(rewritten)), len(real_held)],
        "held_back_a99_9_every_figure_equal": diagonal,
    }


def main() -> None:
    systems: "dict[str, dict[str, int]]" = {}
    shapes: "dict[str, dict[str, int]]" = {}
    with tempfile.TemporaryDirectory(prefix="synthtwin-codes-in-pattern-") as folder:
        for name in sorted(SYSTEMS):
            make, distinct, pattern = SYSTEMS[name]
            totals = {"out": 0, "group": 0, "stand": 0, "formed": 0, "ub04": 0, "failing": 0, "ends": 0, "ends_out": 0}
            for seed in SEEDS:
                draw = random.Random(4390 + seed)
                cells = _zipf(draw, _distinct(draw, make, distinct), ROWS, 1.1)
                found = _one(pathlib.Path(folder) / name / f"{seed}", cells, f"{pattern}", seed)
                totals["out"] += int(found["out_of_pattern"])  # type: ignore[call-overload]
                totals["group"] += int(found["group_n"])  # type: ignore[call-overload]
                totals["stand"] += int(found["stand_in_cells"])  # type: ignore[call-overload]
                totals["formed"] = max(totals["formed"], int(found["forms_named"]))  # type: ignore[call-overload]
                if name == "ub04_rev":
                    totals["ub04"] += int(found["ub04_not_0"])  # type: ignore[call-overload]
                totals["failing"] += 1 if found["twin_missed"] or found["source_missed"] else 0
                totals["ends"] += int(found["number_off_widths_or_ends"])  # type: ignore[call-overload]
                totals["ends_out"] += int(found["number_off_widths_or_ends_out_of_pattern"])  # type: ignore[call-overload]
                print(f"K-HZ-10 {name} seed {seed}: {found}", flush=True)
            systems[name] = totals
        dense = {"group": 0, "failing": 0}
        for name in sorted(DENSE):
            for seed in SEEDS:
                cells = DENSE[name](random.Random(4392 + seed))  # type: ignore[operator]
                found = _one(pathlib.Path(folder) / name / f"{seed}", cells, r"E[1-4]V[1-5]M[1-6]|\d{1,3}", seed)
                dense["group"] += int(found["group_n"])  # type: ignore[call-overload]
                dense["failing"] += 1 if found["twin_missed"] or found["source_missed"] else 0
                print(f"K-HZ-10 dense {name} seed {seed}: {found}", flush=True)
        for name in sorted(SHAPES):
            build, pattern = SHAPES[name]
            totals = {
                "out": 0, "group": 0, "stand": 0, "twin_failing": 0, "source_failing": 0,
                "gleason": 0, "loinc": 0, "naaccr": 0,
                "neighbours": {},
                "real_severe": 0, "twin_severe": 0,
            }
            for seed in SEEDS:
                cells = build(random.Random(4391 + seed))  # type: ignore[operator]
                found = _one(pathlib.Path(folder) / name / f"{seed}", cells, f"{pattern}", seed)
                totals["out"] += int(found["out_of_pattern"])  # type: ignore[call-overload]
                totals["group"] += int(found["group_n"])  # type: ignore[call-overload]
                totals["stand"] += int(found["stand_in_cells"])  # type: ignore[call-overload]
                totals["twin_failing"] += 1 if found["twin_missed"] else 0
                totals["source_failing"] += 1 if found["source_missed"] else 0
                totals["gleason"] += int(found["gleason_sum_broken"])  # type: ignore[call-overload]
                totals["loinc"] += int(found["loinc_check_figure_wrong"])  # type: ignore[call-overload]
                totals["naaccr"] += int(found["naaccr_past_c809"])  # type: ignore[call-overload]
                neighbours = found["held_back_neighbouring_figures_equal"]
                for form, counted in neighbours.items():  # type: ignore[attr-defined]
                    summed = totals["neighbours"].get(form, [0, 0, 0, 0])  # type: ignore[attr-defined]
                    totals["neighbours"][form] = [summed[at] + counted[at] for at in range(4)]  # type: ignore[index]
                totals["real_severe"] += found["gcs_cells_8_or_less"]["real"]  # type: ignore[index]
                totals["twin_severe"] += found["gcs_cells_8_or_less"]["twin"]  # type: ignore[index]
                print(f"K-HZ-11 {name} seed {seed}: {found}", flush=True)
            shapes[name] = totals
    formed = [name for name in sorted(systems) if systems[name]["formed"] > 0]
    unformed = [name for name in sorted(systems) if systems[name]["formed"] == 0]
    # THE NEIGHBOURING FIGURES OF THE HELD-BACK CELLS, twin against real,
    # pooled over the seeds, on the three shapes of many figures a cell.
    rates: "dict[str, tuple[float, float]]" = {}
    for name in ("icd10_dotted", "pcornet_dx", "i2b2_concept_cd"):
        for form, counted in sorted(shapes[name]["neighbours"].items()):  # type: ignore[attr-defined]
            if counted[1] and counted[3]:
                rates[f"{name} {form}"] = (counted[2] / counted[3], counted[0] / counted[1])
    kpi_rules.emit(
        "K-HZ-10",
        {
            "stand_in_cells_outside_grammar": sum(systems[name]["out"] for name in formed),
            "systems_outside_grammar": sum(1 for name in formed if systems[name]["out"] > 0),
            "systems_with_group_n_where_a_form_is_published": sum(1 for name in formed if systems[name]["group"] > 0),
            "ub04_cells_not_ending_in_0": systems["ub04_rev"]["ub04"],
            "twins_or_tables_failing_validation": sum(systems[name]["failing"] for name in sorted(systems)),
            "systems_publishing_no_form": len(unformed),
            # Rule A3's misses are this lane's, not CODES-2's: taken out of
            # the systems publishing no form.
            "stand_in_cells_where_no_form_is_published": sum(
                systems[name]["out"] - systems[name]["ends_out"] for name in unformed
            ),
            "number_stand_ins_outside_published_widths_or_range": sum(systems[name]["ends"] for name in sorted(systems)),
            # The dense scales (lane CODES-1's second repair): physical-status classes,
            # Glasgow components beside totals, two codes beside four.
            "dense_scale_cells_written_group_n": dense["group"],
            "dense_scale_twins_or_tables_failing_validation": dense["failing"],
        },
        "20,000 rows, floor 11, seeds 0 to 2; publishing no form (CODES-2's names, Z1): "
        + (", ".join(unformed) or "none")
        + "; outside their grammar: "
        + (", ".join(f"{name} {systems[name]['out']}" for name in formed if systems[name]["out"]) or "none")
        + "; made-up whole numbers off the published widths or ends: "
        + (", ".join(f"{name} {systems[name]['ends']}" for name in sorted(systems) if systems[name]["ends"]) or "none")
        + "; dense scales (" + ", ".join(sorted(DENSE)) + "): "
        + f"{dense['group']} cells group-N, {dense['failing']} failing",
    )
    kpi_rules.emit(
        "K-HZ-11",
        {
            "stand_in_cells_out_of_pattern": sum(shapes[name]["out"] for name in sorted(shapes) if name != "blood_type"),
            "shapes_out_of_pattern": sum(1 for name in sorted(shapes) if name != "blood_type" and shapes[name]["out"] > 0),
            "blood_type_cells_out_of_pattern": shapes["blood_type"]["out"],
            "twins_failing_validation": sum(shapes[name]["twin_failing"] for name in sorted(shapes)),
            "tables_failing_validation": sum(shapes[name]["source_failing"] for name in sorted(shapes)),
            "pcornet_dx_twins_failing_validation": shapes["pcornet_dx"]["twin_failing"],
            "forms_with_neighbouring_figures_equal_past_1_5_times_the_real": sum(
                1 for name in sorted(rates) if rates[name][0] > 1.5 * rates[name][1]
            ),
            # Three system rules no pattern reads (CODES-2's, under Z1).
            "gleason_stand_in_cells_with_a_wrong_sum": shapes["gleason"]["gleason"],
            "loinc_stand_in_cells_with_a_wrong_check_figure": shapes["loinc"]["loinc"],
            "naaccr_stand_in_cells_past_c809": shapes["naaccr_site"]["naaccr"],
        },
        "20,000 rows, floor 11, seeds 0 to 2; per shape (stand-in cells out of pattern / stand-in cells): "
        + ", ".join(f"{name} {shapes[name]['out']}/{shapes[name]['stand']}" for name in sorted(shapes))
        + "; held-back cells' neighbouring figures equal by form (three commonest), twin against real: "
        + ", ".join(f"{name} {rates[name][0]:.3f}/{rates[name][1]:.3f}" for name in sorted(rates))
        + "; Glasgow coma scores of 8 or less over the column, twin against real: "
        + f"{shapes['gcs']['twin_severe']}/{shapes['gcs']['real_severe']}",
    )


if __name__ == "__main__":
    main()
