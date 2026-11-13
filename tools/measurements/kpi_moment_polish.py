"""K-S6-12, the twin meets rule B's published moments (generation method G16.2 and G16.3; lane MPg, plan P4-D456).

On lane E0b's battery tables ST1 to ST6 and on the invented table of two
nearly collinear pairs (tests/moment_polish_tables.py, `COLLINEAR`), each at
20,000 rows (seed 1), described with the chain behind its switch (the
ledger's fixed test key) and generated from that description: the walk by
hidden scores alone (the implied slope and the polish off) at twin seed 0,
the walk with the implied slope (the polish off) and the SHIPPED twin (both
on) at twin seeds 0, 1 and 2. Beside them, in the same run, three FRESH
samples of each table's population (the battery's replicate seeds 1100 to
1102, the invented table's too, cut to the real table's rows).

- every published moment (a number's mean and spread on its code, a
  binary's share, a pair's correlation and, where the pair holds fewer
  rows than either column's readings, its own two spreads (`pair spread`,
  repair 2), a column's mean and spread or share in each band of a
  grouping column) recomputed on each file, coded
  as the chain reads a file (`moment_rule_b_enumeration.coded`), and judged
  as validation method V13's line reads it (repair 1): INSIDE where the
  file's value lies within half a unit of the published rounding (the unit
  its own count sets, contract 4.6d.0 (3); a correlation's half step of
  Fisher's z read on r) plus twice the root of two times its standard
  error at the file's count, each standard error read from published
  values: a file and the published value are two samples, so their
  difference carries root two standard errors (lane MPg's statistics
  review, item 1). The twin's share is read beside the FRESH samples'
  share, kind by kind (`by_kind`), the target being at least theirs; the
  share at two standard errors alone is recorded too (`*_2se`);
- held EXACTLY on each shipped twin against the implied slope's twin of
  the same seed (the same cells and the same walk, the polish only
  added): each column's multiset of cells (`multisets_off`); the twin's
  rows read as a multiset, so the file's sort (plan P4-D86), which moves
  whole rows after the polish, moves none of these: each row's cells in
  every column the polish does not name (`unpolished_changed`) and,
  beside them, each polished column's blank rows (`blanks_moved`); every
  family's table at its published levels (`family_tables_off`); and every
  column's `L0` band totals against the published ones (`l0_totals_off`).
  `rows_resorted` counts the tables whose sorted rows moved whole because
  the sort's key was polished (recorded, never judged);
- the invented table's two pairs: each shipped twin's r on codes against
  the published r and the pair's bound (`collinear`).

    PYTHONPATH=src:tests python tools/measurements/kpi_moment_polish.py --kpi

About forty minutes; one process of a few hundred megabytes.
"""

import json
import math
import pathlib
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import analyst_tables  # noqa: E402
import moment_polish_tables  # noqa: E402
import moment_rule_b_enumeration as enumeration  # noqa: E402

from synthtwin import canonical, chain, chain_check, chain_moments, chain_rules, contract, generation, profile, reading, rendering, taxonomy  # noqa: E402

FLOOR = 11
ROWS = 20000
SEED = 1
KEY = bytes(range(32))
TWIN_SEEDS = (0, 1, 2)
FRESH_SEEDS = (1100, 1101, 1102)
COLLINEAR = "COLLINEAR"
TABLES = tuple(analyst_tables.TABLES) + (COLLINEAR,)
ROOT_TWO = math.sqrt(2.0)


def _table_text(name: str, rows: int, seed: int) -> str:
    if name == COLLINEAR:
        return moment_polish_tables.collinear_text(rows, seed)
    return analyst_tables.text(name, rows, seed)


def _stats(values: "list[float]") -> "tuple[int, float, float]":
    n = len(values)
    mean = sum(values) / n
    sd = math.sqrt(sum((v - mean) ** 2 for v in values) / (n - 1)) if n > 1 else 0.0
    return n, mean, sd


def _half(scale: int, n: int) -> float:
    """Half a unit of a moment published at count `n` (contract 4.6d.0 (3))."""
    return 0.5 / chain_moments.unit(scale, n)


def moments_on(table: object, document: "dict[str, object]", statistical: "dict[str, object]") -> "list[tuple[str, float, float, float]]":
    """Every published moment recomputed on a file: (kind, gap, half a unit, standard error)."""
    moments = statistical["moments"]
    columns, groupings = enumeration.coded(table, document, statistical, FLOOR)
    values = {name: (kind, vals) for name, kind, vals in columns}
    l1 = {grouping[0]: grouping[1] for grouping in groupings}
    # A grouping published on its `L2` bands (`level: 2`): each row's `L1` band read on its `L2` band.
    l2 = {grouping[0]: [grouping[4][band] for band in grouping[1]] for grouping in groupings}
    scales = moments["scales"]  # type: ignore[index]
    out: "list[tuple[str, float, float, float]]" = []
    for entry in moments["columns"]:  # type: ignore[index]
        kind, vals = values[entry["column"]]
        n, mean, sd = _stats([float(v) for v in vals if v is not None])
        count = entry["n"]
        if entry["kind"] == "number":
            pub_mean = entry["mean"] / chain_moments.unit(scales["mean"], count)
            pub_sd = entry["sd"] / chain_moments.unit(scales["column_sd"], count)
            out += [("column mean", abs(mean - pub_mean), _half(scales["mean"], count), pub_sd / math.sqrt(n))]
            out += [("column spread", abs(sd - pub_sd), _half(scales["column_sd"], count), pub_sd / math.sqrt(2 * (n - 1)))]
        else:
            share = entry["share"] / chain_moments.unit(scales["share"], count)
            out += [("column share", abs(mean - share), _half(scales["share"], count), math.sqrt(share * (1 - share) / n))]
    numbers = [entry["column"] for entry in moments["columns"] if entry["kind"] == "number"]  # type: ignore[index]
    for at, line in enumerate(moments["correlations"]):  # type: ignore[index]
        for other, pair in enumerate(line):
            if pair is None:
                continue
            first, second = values[numbers[at]][1], values[numbers[other]][1]
            both = [(float(a), float(b)) for a, b in zip(first, second) if a is not None and b is not None]
            n = len(both)
            ma = sum(a for a, _b in both) / n
            mb = sum(b for _a, b in both) / n
            va = sum((a - ma) ** 2 for a, _b in both)
            vb = sum((b - mb) ** 2 for _a, b in both)
            r = sum((a - ma) * (b - mb) for a, b in both) / math.sqrt(va * vb) if va > 0 and vb > 0 else 0.0
            published = pair[0] / scales["correlation"]
            half = _half(scales["fisher_z"], pair[1]) * (1 - published * published)
            out += [("correlation", abs(r - published), half, max(1 - published * published, 1 / 20) / math.sqrt(n))]
            if len(pair) == 3 and n > 1:
                # An incomplete pair's own two spreads (repair 2, Codex's item 3): each column's spread over the
                # rows holding both, the row's column first, judged as a column's spread is.
                for own, spread in ((pair[2][0], va), (pair[2][1], vb)):
                    pub_sd = own / chain_moments.unit(scales["column_sd"], pair[1])
                    out += [("pair spread", abs(math.sqrt(spread / (n - 1)) - pub_sd), _half(scales["column_sd"], pair[1]), pub_sd / math.sqrt(2 * (n - 1)))]
    for entry in moments["within"]:  # type: ignore[index]
        kind, vals = values[entry["column"]]
        bands = l2[entry["by"]] if entry.get("level") == 2 and entry["by"] in l2 else l1[entry["by"]]
        for band, group in enumerate(entry["groups"]):
            if group[0] == 0:
                continue
            held = [float(v) for v, g in zip(vals, bands) if g == band and v is not None]
            if len(held) < 2:
                out += [("band mean" if kind == "number" else "band share", math.inf, 0.0, 0.0)]
                continue
            n, mean, sd = _stats(held)
            if kind == "number":
                pub_mean = group[1] / chain_moments.unit(scales["mean"], group[0])
                pub_sd = group[2] / chain_moments.unit(scales["sd"], group[0])
                out += [("band mean", abs(mean - pub_mean), _half(scales["mean"], group[0]), pub_sd / math.sqrt(n))]
                out += [("band spread", abs(sd - pub_sd), _half(scales["sd"], group[0]), pub_sd / math.sqrt(2 * (n - 1)))]
            else:
                share = group[1] / chain_moments.unit(scales["share"], group[0])
                out += [("band share", abs(mean - share), _half(scales["share"], group[0]), math.sqrt(share * (1 - share) / n))]
    return out


def inside(found: "list[tuple[str, float, float, float]]", times: float) -> "list[tuple[str, bool]]":
    """Each moment's kind and whether its gap lies within half a unit plus `times` standard errors."""
    return [(kind, gap <= half + times * se) for kind, gap, half, se in found]


def collinear_pairs(table: object, document: "dict[str, object]", statistical: "dict[str, object]") -> "dict[str, list[float]]":
    """The invented table's two pairs on a file: [r on codes, the published r, its bound at root two]."""
    moments = statistical["moments"]
    columns, _groupings = enumeration.coded(table, document, statistical, FLOOR)
    values = {name: vals for name, _kind, vals in columns}
    numbers = [entry["column"] for entry in moments["columns"] if entry["kind"] == "number"]  # type: ignore[index]
    out: "dict[str, list[float]]" = {}
    for first, second in (("pa", "pb"), ("qa", "qb")):
        if first not in numbers or second not in numbers:
            continue
        i, j = sorted((numbers.index(first), numbers.index(second)), reverse=True)
        pair = moments["correlations"][i][j]  # type: ignore[index]
        if pair is None:
            continue
        both = [(float(a), float(b)) for a, b in zip(values[first], values[second]) if a is not None and b is not None]
        n = len(both)
        ma = sum(a for a, _b in both) / n
        mb = sum(b for _a, b in both) / n
        r = sum((a - ma) * (b - mb) for a, b in both) / math.sqrt(sum((a - ma) ** 2 for a, _b in both) * sum((b - mb) ** 2 for _a, b in both))
        published = pair[0] / moments["scales"]["correlation"]  # type: ignore[index]
        bound = _half(moments["scales"]["fisher_z"], pair[1]) * (1 - published * published) + 2 * ROOT_TWO * (1 - published * published) / math.sqrt(n)  # type: ignore[index]
        out[f"{first}~{second}"] = [round(r, 6), round(published, 6), round(bound, 6)]
    return out


def levels_on(table: object, document: "dict[str, object]", statistical: "dict[str, object]") -> "dict[str, tuple[list[int], object]]":
    """Each eligible column's `L0` band a row of a file and its ladder, read as the chain reads a file."""
    settings = taxonomy.Settings(small_cell_floor=FLOOR)
    blocks = {f"{block['name']}": block for block in document["columns"]}  # type: ignore[union-attr, index, attr-defined]
    names = [f"{block['name']}" for block in document["columns"]]  # type: ignore[union-attr, index, attr-defined]
    out: "dict[str, tuple[list[int], object]]" = {}
    # Which `L2` the description was cut under, read from its own record as
    # the loader reads it (S24; RULE ONE_BAND, lane CHa2, plan P4-D451).
    one_band = chain_rules.reads_one_band(statistical["procedure"], table.n_rows)  # type: ignore[attr-defined]
    assert one_band is not None, "the description's procedure record is of neither version"
    for entry in statistical["ladder"]:  # type: ignore[attr-defined]
        name = entry["column"]
        scale, _start = chain_check._ladder_of(entry, blocks[name], FLOOR, table.n_rows, 0, one_band)  # type: ignore[attr-defined]
        read = chain.read_column(table, names.index(name), blocks[name], settings, enumeration.DECLARED, "", 0)  # type: ignore[arg-type]
        assert read is not None
        to_l0: "dict[object, int]" = {}
        for at in range(len(scale.l0)):
            for one in scale.l0[at]:
                to_l0[one] = at
        out[name] = ([to_l0[read.start.names[code]] for code in read.codes], scale)
    return out


def family_tables(levels: "dict[str, tuple[list[int], object]]", statistical: "dict[str, object]", rows: int) -> "list[dict[tuple[int, ...], int]]":
    """Each family's table at its published levels, counted on a file's rows."""
    out: "list[dict[tuple[int, ...], int]]" = []
    for family in statistical["chain"]:  # type: ignore[attr-defined]
        members = [(p["column"], int(p["level"][1])) for p in family["parents"]] + [(family["child"], int(family["level"][1]))]
        counted: "dict[tuple[int, ...], int]" = {}
        for row in range(rows):
            key = tuple(
                levels[m][1].maps[level][levels[m][0][row]] if level else levels[m][0][row]  # type: ignore[attr-defined]
                for m, level in members
            )
            counted[key] = counted.get(key, 0) + 1
        out += [counted]
    return out


def measure_table(name: str, folder: pathlib.Path) -> "dict[str, object]":
    settings = taxonomy.Settings(small_cell_floor=FLOOR)
    path = folder / f"{name}.csv"
    path.write_text(_table_text(name, ROWS, SEED), encoding="utf-8", newline="\n")
    table = reading.read_table(str(path), small_cell_floor=FLOOR)
    document = profile.build_document(table, settings, [], [], [])
    chained = chain.describe(table, document, settings, chain.ChainSwitch(f"{name}-{SEED}", KEY, rows_per_person=chain.ROWS_UNASKED))
    statistical = chained.statistical
    out: "dict[str, object]" = {"table": name}
    if statistical is None or statistical["moments"] is None:
        out["moments"] = None
        return out
    del table
    written = dict(document)
    written["relationships"] = dict(written["relationships"], statistical=statistical)  # type: ignore[arg-type]
    described = folder / f"{name}-switched.json"
    described.write_text(canonical.serialize(written), encoding="utf-8", newline="\n")
    loaded = contract.load_profile(str(described), chain=True)
    polished = [column for column, _targets in generation._polish_plan(loaded)]
    out["polished"] = len(polished)
    found: "dict[str, list[tuple[str, float, float, float]]]" = {}
    # THE FRESH SAMPLES: the same population at other seeds, cut to the real table's rows.
    lines = path.read_text(encoding="utf-8").count("\n")
    for seed in FRESH_SEEDS:
        fresh_path = folder / f"{name}-fresh{seed}.csv"
        fresh = _table_text(name, ROWS + 3000, seed).split("\n")
        fresh_path.write_text("\n".join(fresh[:lines]) + "\n", encoding="utf-8", newline="\n")
        found[f"fresh{seed}"] = moments_on(reading.read_table(str(fresh_path), small_cell_floor=FLOOR), written, statistical)
        fresh_path.unlink()
    seconds: "dict[str, float]" = {}
    exact = {"multisets_off": 0, "blanks_moved": 0, "unpolished_changed": 0, "family_tables_off": 0, "l0_totals_off": 0}
    resorted = 0
    pairs: "dict[str, dict[str, list[float]]]" = {}
    names = list(loaded.columns)
    kept = [at for at, column in enumerate(names) if column.name not in polished]
    moved = [at for at, column in enumerate(names) if column.name in polished]

    def rows_of(columns: "list[list[str]]", extra: "list[int]") -> "list[tuple[object, ...]]":
        parts: "list[list[object]]" = [list(columns[at]) for at in kept]
        parts += [[cell == "" for cell in columns[at]] for at in extra]
        return sorted(zip(*parts))

    for seed in TWIN_SEEDS:
        cells: "dict[str, list[list[str]]]" = {}
        tables: "dict[str, list[dict[tuple[int, ...], int]]]" = {}
        for step, implied, rounds in (("walk", False, 0), ("implied", True, 0), ("shipped", True, None)):
            if step == "walk" and seed != TWIN_SEEDS[0]:
                continue
            generation._IMPLIED_SLOPE = implied
            if rounds is not None:
                generation._POLISH_ROUNDS = rounds
            clock = time.perf_counter()
            twin = generation.generate_held(loaded, seed)
            seconds[f"{step} {seed}"] = round(time.perf_counter() - clock, 1)
            generation._IMPLIED_SLOPE = True
            generation._POLISH_ROUNDS = 8
            cells[step] = [list(generation.twin_column(twin, at)) for at in range(len(twin.names))]
            twin_path = folder / f"{name}-{step}.csv"
            twin_path.write_text("".join(rendering.twin_csv_pieces(twin)), encoding="utf-8", newline="\n")
            del twin
            twin_table = reading.read_table(str(twin_path), small_cell_floor=FLOOR)
            found[f"{step}{seed}"] = moments_on(twin_table, written, statistical)
            if step in ("implied", "shipped"):
                levels = levels_on(twin_table, written, statistical)
                tables[step] = family_tables(levels, statistical, twin_table.n_rows)
                if step == "shipped":
                    for entry in statistical["ladder"]:  # type: ignore[attr-defined]
                        held = levels[entry["column"]][0]
                        counted = [held.count(band) for band in range(len(entry["totals"]))]
                        exact["l0_totals_off"] += 0 if counted == list(entry["totals"]) else 1
                    if name == COLLINEAR:
                        pairs[f"{seed}"] = collinear_pairs(twin_table, written, statistical)
            twin_path.unlink()
        shipped, before = cells["shipped"], cells["implied"]
        exact["multisets_off"] += sum(1 for a, b in zip(shipped, before) if sorted(a) != sorted(b))
        # ROWS TAKEN WHOLE: where the real table was sorted, the twin's rows are
        # sorted the same way after the polish (plan P4-D86), whole rows moving;
        # where the sort's key is a polished column, every column then moves
        # with its rows. So each check reads the twin's rows as a multiset.
        whole = rows_of(shipped, []) == rows_of(before, [])
        exact["unpolished_changed"] += 0 if whole else sum(1 for at in kept if shipped[at] != before[at])
        exact["blanks_moved"] += sum(1 for at in moved if rows_of(shipped, [at]) != rows_of(before, [at]))
        resorted += 1 if whole and any(shipped[at] != before[at] for at in kept) else 0
        exact["family_tables_off"] += sum(1 for a, b in zip(tables["shipped"], tables["implied"]) if a != b)
    out.update(exact)
    out["rows_resorted"] = resorted
    out["found"] = found
    out["seconds"] = seconds
    out["collinear"] = pairs
    path.unlink()
    return out


def _shares(rows: "list[tuple[str, bool]]") -> "dict[str, list[int]]":
    counted: "dict[str, list[int]]" = {}
    for kind, good in rows:
        held = counted.setdefault(kind, [0, 0])
        held[0] += 1
        held[1] += 1 if good else 0
    return counted


def measure() -> "dict[str, object]":
    started = time.time()
    value: "dict[str, object]" = {}
    exact = {"multisets_off": 0, "blanks_moved": 0, "unpolished_changed": 0, "family_tables_off": 0, "l0_totals_off": 0}
    files = [f"fresh{seed}" for seed in FRESH_SEEDS] + ["walk0"] + [f"implied{seed}" for seed in TWIN_SEEDS]
    files += [f"shipped{seed}" for seed in TWIN_SEEDS]
    found: "dict[str, list[tuple[str, float, float, float]]]" = {key: [] for key in files}
    polished = 0
    seconds: "dict[str, float]" = {}
    tables = 0
    resorted = 0
    collinear: "dict[str, dict[str, list[float]]]" = {}
    with tempfile.TemporaryDirectory() as folder:
        for name in TABLES:
            measured = measure_table(name, pathlib.Path(folder))
            if measured.get("moments", True) is None:
                continue
            tables += 1
            polished += measured["polished"]  # type: ignore[operator]
            for key in exact:
                exact[key] += measured[key]  # type: ignore[operator]
            resorted += measured["rows_resorted"]  # type: ignore[operator]
            for key in files:
                found[key] += measured["found"][key]  # type: ignore[index]
            for key, secs in measured["seconds"].items():  # type: ignore[attr-defined]
                seconds[key] = round(seconds.get(key, 0.0) + secs, 1)
            if name == COLLINEAR:
                collinear = measured["collinear"]  # type: ignore[assignment]
    value.update(exact)
    value["rows_resorted"] = resorted
    value["moments_judged"] = len(found["shipped0"])
    # THE RULE (V13, repair 1): half a unit plus twice the root of two times the standard error.
    judged = {key: inside(rows, 2 * ROOT_TWO) for key, rows in found.items()}
    at_two = {key: inside(rows, 2.0) for key, rows in found.items()}
    share = {key: round(sum(1 for _kind, good in rows if good) / max(1, len(rows)), 4) for key, rows in judged.items()}
    value["share_inside"] = {key: share[key] for key in files}
    value["share_inside_2se"] = {key: round(sum(1 for _kind, good in rows if good) / max(1, len(rows)), 4) for key, rows in at_two.items()}
    shipped_keys = [f"shipped{seed}" for seed in TWIN_SEEDS]
    fresh_keys = [f"fresh{seed}" for seed in FRESH_SEEDS]
    value["shipped_share_least"] = min(share[key] for key in shipped_keys)
    value["fresh_share_mean"] = round(sum(share[key] for key in fresh_keys) / len(fresh_keys), 4)
    kinds: "dict[str, dict[str, object]]" = {}
    below: "list[str]" = []
    counted = {key: _shares(rows) for key, rows in judged.items()}
    for kind in sorted(counted["shipped0"]):
        twin = [counted[key][kind][1] for key in shipped_keys]
        fresh = [counted[key][kind][1] for key in fresh_keys]
        kinds[kind] = {"judged": counted["shipped0"][kind][0], "shipped": twin, "fresh": fresh,
                       "implied0": counted["implied0"][kind][1], "walk0": counted["walk0"][kind][1]}
        if sum(twin) / len(twin) < sum(fresh) / len(fresh):
            below += [kind]
    value["by_kind"] = kinds
    value["kinds_below_fresh"] = below
    value["correlations_inside_least"] = min(counted[key]["correlation"][1] for key in shipped_keys)
    value["collinear"] = collinear
    value["polished_columns"] = polished
    value["tables"] = tables
    value["generate_seconds"] = seconds
    value["seconds"] = round(time.time() - started, 1)
    return value


def main() -> int:
    value = measure()
    if "--kpi" in sys.argv:
        print("KPI " + json.dumps({"id": "K-S6-12", "value": value, "detail": "the twin meets rule B's moments (lane MPg)"}, sort_keys=True))
    else:
        print(json.dumps(value, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
