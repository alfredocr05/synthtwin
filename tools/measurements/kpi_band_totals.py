"""K-S6-02, layer L0: every within-column fact unchanged with and without L0; the column meets its L0 band totals (plan P4-D429).

Lane BT's stamp of `K-S6-02` as method G5.7h rewords it, on the product's
own twins of invented tables (no real data), each described with the
chain's switch (`chain.describe`, a fixed test key), loaded behind it
(`contract.load_profile(..., chain=True)`) and generated with and without
its ladder:

- (i) THE SWITCH OFF: every switched description, its ladder emptied,
  makes byte for byte the twin of the same table described without the
  chain, at every seed: `switch_off_differences`, target 0, over
  `switch_off_checked` pairs;
- (ii) THE SAME CELLS: each eligible column's cells, as a multiset, are
  the cells the interface G16 calls hands over plus the reserved ones
  (`generation.cells_by_band`): `multiset_differences`, target 0;
- (iii) THE BAND TOTALS: each eligible column's twin, read back the way
  the profile reads a table (`chain.read_column`), holds every published
  `L0` band count: `rows_off`, target 0, over `bands_checked` bands of
  `columns_checked` columns;
- (iv) NO FACT LOST: the within-column facts the twin made without L0
  holds and the twin made with it misses, both judged by one yardstick,
  the quality report (`validation.measure`, today's windows of G12.2,
  G12.3 and G12.3a at G12.2's half unit, against the description without
  its chain): `facts_lost`, target 0, each named in `facts_lost_named`;
- (v) THE SHAPE INSIDE THE BANDS: on every count column, the twin's count
  at each value summed over each band as `sum |twin - real|` is no larger
  with L0 than without it, and each published rung the twin's own
  description reads is no further from the published one:
  `shape_regressions`, target 0;
- THE LAST GUARD (G5.7g): the values it moved back inside their band,
  read from each twin's own report: `guard_moves`, reported, each column
  named in `guard_moved`;
- the columns made without their band totals (rule B3, named):
  `made_without`, reported; the tables whose switched description its own
  loader refused: `chain_refused`, reported.

    PYTHONPATH=src:tests python tools/measurements/kpi_band_totals.py --kpi [--rows 5000,20000] [--seeds 0,1,2]

The default is the ten-column table of G5.7i at 5,000 and 20,000 rows and
the count of few values of G14.3a case 1 at 20,000, seeds 0 to 2, and the
every-role table at 2,000 rows, seeds 0 to 4; about 10 to 15 minutes, one
process of a few hundred megabytes. The 200,000-row leg is a separate run
under the heavy-slot guard (`--rows 200000 --seeds 0,1,2,3,4`).
"""

import dataclasses
import json
import pathlib
import random
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import fixtures  # noqa: E402

from synthtwin import (  # noqa: E402
    canonical,
    chain,
    chain_rules,
    contract,
    errors,
    generation,
    parsing,
    profile,
    reading,
    rendering,
    taxonomy,
    validation,
)

FLOOR = 11
TEST_KEY = bytes(range(32))
SPELLED = {"code": False, "measurement": False, "decimal_comma": False}
ORDERED = ("count", "continuous", "datetime", "time_of_day", "affixed_number")
# Each table whose switched description its own loader refused, with the
# loader's words: the chain's profile side's, reported and never judged.
REFUSED: "dict[str, str]" = {}


def _ten(rows: int, seed: int = 7) -> "tuple[list[str], list[list[str]]]":
    """G5.7i's invented ten-column table: an age, a pressure, a stay, a count of few values, visits, money, a change, a date, a clock."""
    draw = random.Random(seed)
    body: "list[list[str]]" = []
    for place in range(rows):
        age = draw.randint(1, 9) * 10 + draw.randint(0, 9)
        pressure = "" if draw.random() < 0.05 else f"{round(draw.gauss(120, 15), 1)}"
        stay = f"{round(draw.lognormvariate(1.2, 0.8), 2)}"
        few = min(int(draw.expovariate(0.6)), 12)
        visits = min(int(draw.gammavariate(2, 2)), 25)
        money = f"{round(draw.lognormvariate(5, 1), 2):.2f}"
        change = f"{round(draw.gauss(0, 2), 1)}"
        day = draw.randint(0, 364)
        visit = f"2023-{1 + day // 31 if day // 31 < 12 else 12:02d}-{1 + day % 28:02d}"
        if draw.random() < 0.15:
            clock = "08:00"
        else:
            minutes = int(min(max(draw.gauss(13 * 60, 150), 6 * 60), 22 * 60))
            clock = f"{minutes // 60:02d}:{minutes % 60:02d}"
        body += [[f"R{place:06d}", str(age), pressure, stay, str(few), str(visits), money, change, visit, clock, draw.choice(["F", "M"])]]
    return ["id", "age", "pressure", "stay", "few", "visits", "money", "change", "visit_date", "clock", "gender"], body


def _few(rows: int) -> "tuple[list[str], list[list[str]]]":
    """G14.3a case 1 (b): a count of few values with one rare high value, scaled to ``rows``."""
    counts = [1568, 8436, 5813, 2464, 1018, 425, 162, 59, 30, 14, 7, 1, 2]
    cells: "list[str]" = []
    for value in range(len(counts)):
        cells += [str(value)] * round(counts[value] * rows / 20000)
    cells += ["16"]
    while len(cells) < rows:
        cells += ["1"]
    cells = cells[:rows]
    draw = random.Random(5)
    draw.shuffle(cells)
    return ["id", "count", "group"], [[f"R{place:06d}", cells[place], draw.choice(["a", "b"])] for place in range(rows)]


def _described(folder: pathlib.Path, name: str, text: str) -> "tuple[dict[str, object], dict[str, object] | None, contract.Profile | None, contract.Profile, pathlib.Path]":
    path = folder / f"{name}.csv"
    path.write_text(text, encoding="utf-8", newline="\n")
    settings = taxonomy.Settings(small_cell_floor=FLOOR)
    table = reading.read_table(str(path), small_cell_floor=FLOOR)
    document = profile.build_document(table, settings, [], [], [])
    plain_path = folder / f"{name}-plain.json"
    plain_path.write_text(canonical.serialize(document), encoding="utf-8", newline="\n")
    plain = contract.load_profile(str(plain_path))
    chained = chain.describe(table, document, settings, chain.ChainSwitch(name, TEST_KEY))
    if chained.statistical is None:
        return document, None, None, plain, path
    written = dict(document)
    relationships = dict(written["relationships"])  # type: ignore[call-overload]
    relationships["statistical"] = chained.statistical
    written["relationships"] = relationships
    on = folder / f"{name}-switched.json"
    on.write_text(canonical.serialize(written), encoding="utf-8", newline="\n")
    try:
        loaded = contract.load_profile(str(on), chain=True)
    except errors.ProfileError as refused:
        REFUSED[name] = f"{refused}"[:200]
        return document, None, None, plain, path
    return document, chained.statistical, loaded, plain, path


def _twin_csv(folder: pathlib.Path, twin: generation.Twin, tag: str) -> pathlib.Path:
    out = folder / f"twin-{tag}.csv"
    out.write_text("".join(rendering.twin_csv_pieces(twin)), encoding="utf-8", newline="")
    return out


def _l0_totals(path: pathlib.Path, document: "dict[str, object]", statistical: "dict[str, object]") -> "dict[str, list[int]]":
    back = reading.read_table(str(path), small_cell_floor=FLOOR)
    settings = taxonomy.Settings(small_cell_floor=FLOOR)
    blocks: "dict[str, tuple[int, dict[str, object]]]" = {}
    for place, block in enumerate(document["columns"]):  # type: ignore[arg-type]
        blocks[f"{block['name']}"] = (place, block)
    blank = chain_rules.records_holding_nothing(document)
    found: "dict[str, list[int]]" = {}
    for entry in statistical["ladder"]:  # type: ignore[union-attr]
        place, block = blocks[entry["column"]]
        read = chain.read_column(back, place, block, settings, SPELLED, "", blank)
        if read is None:
            continue
        start = [0] * len(read.start.names)
        for row in range(back.n_rows):
            start[read.codes[row]] += 1
        totals: "list[int]" = []
        for band in entry["l0"]:
            names = [tuple(item) if isinstance(item, list) else item for item in band]
            totals += [sum(start[k] for k in range(len(read.start.names)) if read.start.names[k] in names)]
        found[entry["column"]] = totals
    return found


def _missed(plain: contract.Profile, path: pathlib.Path, names: "set[str]") -> "set[tuple[str, str, str]]":
    outcome = validation.measure(plain, str(path))
    return {
        (check.column, check.fact, check.subcheck)
        for check in outcome.checks
        if check.verdict == validation.MISSED and check.column in names
    }


def _value_counts(path: pathlib.Path, name: str) -> "dict[float, int]":
    back = reading.read_table(str(path), small_cell_floor=FLOOR)
    counts: "dict[float, int]" = {}
    for cell in reading.column_values(back, back.column_names.index(name)):
        value = parsing.parse_number(cell) if isinstance(cell, str) else None
        if value is not None:
            counts[value] = counts.get(value, 0) + 1
    return counts


def _shape_off(counts: "dict[float, int]", real: "dict[float, int]") -> int:
    """`sum |twin count - real count|` over every value: within the bands, since L0 holds each band's total."""
    off = 0
    for value in set(counts) | set(real):
        off += abs(counts.get(value, 0) - real.get(value, 0))
    return off


def measure(rows_list: "list[int]", seeds: "list[int]") -> "dict[str, object]":
    started = time.time()
    value: "dict[str, object]" = {
        "switch_off_differences": 0,
        "switch_off_checked": 0,
        "multiset_differences": 0,
        "rows_off": 0,
        "bands_checked": 0,
        "columns_checked": 0,
        "facts_lost": 0,
        "facts_lost_named": [],
        "shape_regressions": 0,
        "made_without": [],
        "twins": 0,
        "guard_moves": 0,
    }
    lost_named: "list[str]" = []
    guard_moved: "list[str]" = []
    made_without: "list[str]" = []
    with tempfile.TemporaryDirectory(prefix="synthtwin-band-totals-") as held:
        folder = pathlib.Path(held)
        every = fixtures.every_role_table(n_rows=2000)
        tables: "list[tuple[str, str]]" = []
        for rows in rows_list:
            header, body = _ten(rows)
            tables += [(f"ten{rows}", fixtures.rows_to_csv(header, body))]
        header, body = _few(max(rows_list) if max(rows_list) <= 20000 else 20000)
        tables += [("few", fixtures.rows_to_csv(header, body))]
        tables += [("every_role", every)]
        for name, text in tables:
            document, statistical, loaded, plain, source = _described(folder, name, text)
            if loaded is None or statistical is None:
                continue
            roles = {column.name: column.statistical_type for column in loaded.columns}
            eligible = {entry["column"] for entry in statistical["ladder"]}  # type: ignore[union-attr, index]
            published = {entry["column"]: entry["totals"] for entry in statistical["ladder"]}  # type: ignore[union-attr, index]
            for column_name, (cut, why) in generation._l0_columns(loaded).items():
                if cut is None:
                    made_without += [f"{name}.{column_name}: {why}"]
            real_counts = {column_name: _value_counts(source, column_name) for column_name in eligible if roles[column_name] == "count"}
            for seed in (seeds if name != "every_role" else list(range(5))):
                handed: "list[tuple[str, list[int], int]]" = []
                built = generation._row_placement

                def hooked(step, profile_, content, drawn, finished, reserved=None, readings=None):  # type: ignore[no-untyped-def]
                    found = generation.cells_by_band(profile_, step, content, drawn, reserved, readings)
                    if found is not None:
                        cells = sorted([cell for group in found.groups for cell in group] + list(found.reserved))
                        handed.append((found.column, cells, len(content)))
                    if reserved is None:
                        return built(step, profile_, content, drawn, finished)
                    return built(step, profile_, content, drawn, finished, reserved, readings)

                generation._row_placement = hooked
                try:
                    twin = generation.generate_held(loaded, seed)
                finally:
                    generation._row_placement = built
                for _column, cells, count in handed:
                    if cells != list(range(count)):
                        value["multiset_differences"] = int(value["multiset_differences"]) + 1  # type: ignore[call-overload]
                bare = generation.generate_held(plain, seed)
                value["twins"] = int(value["twins"]) + 2  # type: ignore[call-overload]
                # (i) the switch off: the switched description with its
                # ladder emptied, through every seam a ladder would reach,
                # against the table described without the chain.
                stripped = dataclasses.replace(
                    loaded, relationships=dataclasses.replace(loaded.relationships, ladder=(), families=0)
                )
                left = "".join(rendering.twin_csv_pieces(generation.generate_held(stripped, seed)))
                value["switch_off_checked"] = int(value["switch_off_checked"]) + 1  # type: ignore[call-overload]
                if left != "".join(rendering.twin_csv_pieces(bare)):
                    value["switch_off_differences"] = int(value["switch_off_differences"]) + 1  # type: ignore[call-overload]
                for note in twin.deviations:
                    # The guard's note, never rule B3's "made without" one.
                    if note.fact == "band totals" and note.published == "every value inside its band":
                        value["guard_moves"] = int(value["guard_moves"]) + int(note.achieved.split(" ", 1)[0])  # type: ignore[call-overload]
                        guard_moved += [f"{name}@{seed}: {note.column}"]
                with_path = _twin_csv(folder, twin, f"{name}-{seed}-l0")
                bare_path = _twin_csv(folder, bare, f"{name}-{seed}-bare")
                found_totals = _l0_totals(with_path, document, statistical)
                for column_name in found_totals:
                    if roles[column_name] not in ORDERED and roles[column_name] not in ("binary", "categorical", "long_tail_labels", "constant"):
                        continue
                    value["columns_checked"] = int(value["columns_checked"]) + 1  # type: ignore[call-overload]
                    value["bands_checked"] = int(value["bands_checked"]) + len(found_totals[column_name])  # type: ignore[call-overload]
                    off = sum(abs(left - right) for left, right in zip(found_totals[column_name], published[column_name])) // 2
                    if any(column_name in line for line in made_without if line.startswith(f"{name}.")):
                        continue
                    value["rows_off"] = int(value["rows_off"]) + off  # type: ignore[call-overload]
                lost = _missed(plain, with_path, eligible) - _missed(plain, bare_path, eligible)
                value["facts_lost"] = int(value["facts_lost"]) + len(lost)  # type: ignore[call-overload]
                lost_named += [f"{name}@{seed}: {column}.{fact}.{subcheck}" for column, fact, subcheck in sorted(lost)]
                for column_name in real_counts:
                    with_off = _shape_off(_value_counts(with_path, column_name), real_counts[column_name])
                    bare_off = _shape_off(_value_counts(bare_path, column_name), real_counts[column_name])
                    if with_off > bare_off:
                        value["shape_regressions"] = int(value["shape_regressions"]) + 1  # type: ignore[call-overload]
                        lost_named += [f"{name}@{seed}: {column_name} shape {with_off} > {bare_off}"]
                with_path.unlink()
                bare_path.unlink()
    value["facts_lost_named"] = lost_named
    value["made_without"] = sorted(set(made_without))
    value["guard_moved"] = guard_moved
    value["chain_refused"] = sorted(f"{name}: {why}" for name, why in REFUSED.items())
    value["seconds"] = round(time.time() - started, 1)
    return value


def _argument(flag: str, default: "list[int]") -> "list[int]":
    if flag in sys.argv:
        place = sys.argv.index(flag)
        return [int(item) for item in sys.argv[place + 1].split(",")]
    return default


def main() -> int:
    value = measure(_argument("--rows", [5000, 20000]), _argument("--seeds", [0, 1, 2]))
    if "--kpi" in sys.argv:
        print("KPI " + json.dumps({"id": "K-S6-02", "value": value, "detail": "layer L0's band totals (lane BT)"}, sort_keys=True))
    else:
        print(json.dumps(value, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
