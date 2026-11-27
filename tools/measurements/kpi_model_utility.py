"""K-BC-14, the model-utility battery: advanced analyses on the twin a person gets (lane MU, plan P4-D485).

The battery is `tests/model_utility.py` (the six invented tables of
`tests/utility_tables.py`, the thirteen families F11 to F22 and F24, the
controls, the routes of `tests/twin_routes.py`); this driver runs it at
the sizes the suite never does:

* ``--kpi`` -- the 20,000-row tier (kpi_run --slow): the six tables, table
  seeds 1 to 3, the twin at twin seeds 0 to 2 by route S (the commands a
  person types; each twin seed's description under its own installation
  key where the description reads one) beside the fresh replicate, the
  shuffled twin and, on ST7 and ST9, the flattened replicate; route U (the
  same commands unswitched) beside it on a tree whose typed commands
  switch the chain on, and route P (the patient layer on) on ST7 and ST8
  where the tree draws that layer (labelled, never in the ratchet).
  Prints K-BC-14's `_20k` keys. One guarded process. Where an analysis of
  the owner's four families (F11 to F14) is not robust on a real table
  (it stops on the table or one of its eight halves), it prints that
  analysis and exits 1 with no KPI line.
* ``--night`` -- the 200,000-row tier: first every table's truth-holding
  analyses at 200,000 rows, each table in a child process of its own
  (`model_utility.generated_truth_checks`; a truth missed or an analysis
  that stops exits 1 before any table runs); then each table once, seed 1,
  twin seed 0, in a child process of its own, which records its wall
  seconds, its CPU seconds (`ru_utime` + `ru_stime`) and its peak (the
  child's `ru_maxrss`). Prints K-BC-14's `_200k` keys and the drift
  (BC-ARCH's slot: per family, the gap to the replicate at 200,000 rows
  minus the gap at 20,000, the 20,000-row gaps read from the ledger's
  K-BC-14 entry where it holds them; the detail names the commit of that
  stamp and of this head). The parent imports no fitting library until
  every child has ended, so the guard's sum over the parent and a child
  holds the child's own memory and little else (41 MB of its own). Each
  frame of 50,000 rows or more is collected after every analysis and its
  free pages handed back; ST9's child still passed the machine guard's
  1.9 GB three times, so the night reads every frame of ST9 on a
  person-sampled half (`model_utility.HALVED_FRAMES_AT_NIGHT`, said in the
  run's notes: a cost of the measurement, never of the twin). Never beside a whole
  suite: SYNTHTWIN_PAUSE_WHILE is honoured before each child, as
  `kpi_analyst_battery.py` honours it.
* ``--preview TREE`` -- the 20,000-row tier against another tree's src
  (an extracted read-only copy of a branch head): route S there is that
  tree's typed commands; routes C and U beside it. Written to the build
  report, never to the ledger.
* ``--one TABLE`` -- one table in this process, its run written as JSON to
  ``--json`` (a night's child; ``--route`` names the twin's route,
  ``--no-controls`` leaves out the controls a labelled route's child does
  not need). ``--truths TABLE`` -- the table's truth-holding analyses at
  ``--rows`` rows, the result written to ``--json`` (the night's first
  step).
* ``--tables A,B`` -- a subset of the tables: what a later lane's
  statistician runs on the families its change touches; ``--seeds 1``
  a subset of the table seeds (a preview's cost, named in its output).
* ``--layer-tree TREE`` -- route P's twin of ST7 and ST8 made in a child
  process against that tree (the patient layer's branch head) and set
  beside the headline's sides.

ONE OPENMP THREAD. scikit-learn's histogram booster takes its threads from
OpenMP, one a core, whatever `n_jobs` says; on a loaded machine that
oversubscribes the cores (skeptic 1's item 2 on the gate file: 6,035 s
wall against 279 with one thread). The driver sets OMP_NUM_THREADS to 1
(where the environment does not name it) before scikit-learn is
imported, and `model_utility.one_openmp_thread` holds every booster's fit
and prediction to one thread besides.

A RUN KEPT. Where SYNTHTWIN_MODEL_RUNS names a folder, ``--kpi`` writes each
table run there beside a digest of the code its panels come from (src/,
every module under tests/ the battery loads, those it imports only on
first need included, the interpreter's version and those of numpy, scipy,
statsmodels and scikit-learn: a run of another interpreter or library line
is never read back as this one's) and the routes it was asked for, and on
a later ``--kpi`` (or ``--preview``) reads a run back instead of running
it again only where both are unchanged: a ``--preview`` that asks for
route C never reads back a ``--kpi`` run that did not.

TIERS. The KPI line names the tier it produced (``_20k`` or ``_200k``), so
an ordinary ``kpi_run.py --slow`` judges K-BC-14's keys of that tier and
never rejects the other tier's keys as not measured (`kpi_rules.tier_bounds`;
the entry names its two tiers and their commands).

    PYTHONPATH=src:tests python tools/measurements/kpi_model_utility.py --kpi
"""

from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")

import argparse  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import pathlib  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402
from typing import Any  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
THIS = pathlib.Path(__file__).resolve()


def _preview_tree(argv: "list[str]") -> "str | None":
    for i, word in enumerate(argv):
        if word == "--preview" and i + 1 < len(argv):
            return argv[i + 1]
        if word.startswith("--preview="):
            return word.split("=", 1)[1]
    return None


PREVIEW = _preview_tree(sys.argv[1:])
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(pathlib.Path(PREVIEW).resolve()) if PREVIEW else str(ROOT / "src"))
import kpi_rules  # noqa: E402
import twin_routes  # noqa: E402
import utility_tables as U  # noqa: E402

# THE GUARD, AMONG THE MODULE'S OWN STATEMENTS (LANE CHON RULINGS 7 (1)(c); batch 4u's checks): every run of the
# shipped `profile` this driver makes, through `twin_routes` or any module, has a data folder of the run's own and
# the floor off, and the code measured is this tree's -- or, under --preview, the previewed tree's own.
kpi_rules.guard_this_tree(PREVIEW)

NOT_PANEL = ("kpi_rules",)
# The night's size and its rows, stated here so that the night's parent need not import the battery (a gate case holds
# them equal to `model_utility.TIERS`).
NIGHT_ROWS = 200_000
LIBRARIES = ("numpy", "scipy", "pandas", "statsmodels", "sklearn")


def _battery() -> Any:
    """`tests/model_utility.py`, imported on first need (the night's parent imports it only after its children end)."""
    import model_utility

    return model_utility


def peak_mb() -> "float | None":
    """This process's peak resident memory in MB; None without `resource` (Windows)."""
    try:
        import resource
    except ImportError:
        return None
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return round(peak / 1e6 if sys.platform == "darwin" else peak / 1e3, 1)


def cpu_seconds() -> "float | None":
    """This process's CPU seconds so far (user plus system); None without `resource` (Windows)."""
    try:
        import resource
    except ImportError:
        return None
    used = resource.getrusage(resource.RUSAGE_SELF)
    return round(used.ru_utime + used.ru_stime, 1)


def versions() -> str:
    """The interpreter's version and the fitting libraries' (each imported: the digest names what the panels came from)."""
    import importlib

    found = [sys.version.split()[0]]
    for name in LIBRARIES:
        found += [f"{name} {getattr(importlib.import_module(name), '__version__', '?')}"]
    return "; ".join(found)


# The modules under tests/ a run imports only on first need (route P's description writes its profile through
# `fixtures`): imported before the digest is read, so a change to one of them is a change of the code a kept run came
# from (LANE MU RULINGS 6 (6), Codex's review, its item 9).
LAZY = ("fixtures",)


def panel_code_files() -> "list[pathlib.Path]":
    """The files a table run's panels come from: the product's source and each module under tests/ the battery loads,
    the lazily imported ones (`LAZY`) included."""
    import importlib

    import synthtwin

    _battery()
    for name in LAZY:
        importlib.import_module(name)
    tests = (ROOT / "tests").resolve()
    files = sorted(pathlib.Path(synthtwin.__file__).resolve().parent.rglob("*.py"))
    for name, module in sorted(list(sys.modules.items())):
        where = getattr(module, "__file__", None)
        if where and name not in NOT_PANEL and pathlib.Path(where).resolve().parent == tests:
            files += [pathlib.Path(where).resolve()]
    return files


def panel_code_digest() -> str:
    """The sha256 of what a table run's panels come from (`panel_code_files`), and the interpreter's and the fitting
    libraries' versions (the statistics check's item 13)."""
    digest = hashlib.sha256(versions().encode("utf-8") + b"\0")
    for path in panel_code_files():
        digest.update(path.name.encode("utf-8") + b"\0" + path.read_bytes())
    return digest.hexdigest()


def kept_routes(route: str, extra: "tuple[str, ...]") -> "list[str]":
    """The routes a run is asked for: its headline route, then the labelled ones in order (a kept run asked for other
    routes is another run, never read back as this one; Codex's review, its item 9)."""
    return [route] + sorted(set(extra) - {route})


def kept_file(folder: pathlib.Path, table: str, seed: int, routes: "list[str]") -> pathlib.Path:
    """Where a table run asked for these routes is kept."""
    return folder / f"{table}-{seed}-{'+'.join(routes)}.json"


def busy() -> "list[str]":
    """The paths named in SYNTHTWIN_PAUSE_WHILE that exist as a file or a folder with anything in it."""
    held = []
    for name in os.environ.get("SYNTHTWIN_PAUSE_WHILE", "").split(os.pathsep):
        path = pathlib.Path(name) if name else None
        if path is not None and (path.is_file() or (path.is_dir() and any(path.iterdir()))):
            held += [name]
    return held


def wait_turn(label: str) -> None:
    waited = 0
    while busy():
        if waited % 600 == 0:
            print(f"{label}: waiting while {', '.join(busy())} is held", flush=True)
        time.sleep(30)
        waited += 30


def head_commit(root: pathlib.Path = ROOT) -> str:
    """The measured tree's commit, seven figures, or 'unknown' outside a repository."""
    try:
        done = subprocess.run(["git", "-C", str(root), "rev-parse", "--short=7", "HEAD"], capture_output=True,
                              text=True, check=False, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    return done.stdout.strip() or "unknown"


def child(arguments: "list[str]", record: pathlib.Path) -> "dict[str, Any] | None":
    """A child process of this driver; its JSON record, or None where it failed."""
    done = subprocess.run([sys.executable, str(THIS)] + arguments + ["--json", str(record)], check=False)
    if done.returncode == 0 and record.exists():
        return json.loads(record.read_text(encoding="utf-8"))  # type: ignore[no-any-return]
    print(f"{' '.join(arguments[:2])}: the child exited {done.returncode}", flush=True)
    return None


def layer_runs(tree: str, tables: "list[str]", rows: int, seeds: "tuple[int, ...]", twins: "tuple[int, ...]",
               folder: pathlib.Path) -> "dict[tuple[str, int], Any]":
    """Route P's runs of the tables a person stands on several rows of, each in a child process against ``tree``, with
    no controls (the headline's run reads them already)."""
    M = _battery()
    out = {}
    for table in [t for t in tables if t in U.PERSON]:
        for seed in seeds:
            record = child(["--one", table, "--rows", str(rows), "--seed", str(seed), "--twins",
                            ",".join(str(k) for k in twins), "--route", "P", "--no-controls", "--preview", tree,
                            "--out", str(folder / "layer")], folder / f"layer-{table}-{seed}.json")
            if record is not None:
                out[(table, seed)] = M.run_from_dict(record["run"])
    return out


def attach(runs: "list[Any]", layered: "dict[tuple[str, int], Any]") -> None:
    """Set route P's twin sides beside the headline's, as `twin_P` (labelled, never read by the KPIs)."""
    for run in runs:
        other = layered.get((run.table, run.seed))
        if other is not None:
            run.sides["twin_P"] = other.sides["twin"]
            run.notes += [f"route P beside route {run.route} on {run.table}: {len(other.sides['twin'])} twin seed(s)"]
            run.notes += [f"{run.table} route P: {note}" for note in other.notes]


def detail_text(found: "dict[str, Any]", runs: "list[Any]", seconds: float, more: str = "") -> str:
    M = _battery()
    bars = found["bars"]

    def shown(b: "dict[str, Any]") -> str:
        return f"{b['bar']}: {'met' if b['twin'] else 'MISSED'} ({b.get('value')})"

    judged = "; ".join(shown(b) for b in bars if not b["void"])
    void = "; ".join(f"{b['bar']} ({b.get('void_reason') or 'void'}; twin {b.get('value')})" for b in bars
                     if b["void"] and b["read"])
    unread = "; ".join(str(b["bar"]) for b in bars if not b["read"])
    routes = M.route_shares(runs)
    tables = ", ".join(f"{r.table}-{r.seed} route {r.route}" for r in runs)
    notes = sorted({n for r in runs for n in r.notes})
    stopping = sorted({f"{r.table} {name} ({s.panel.status.get(name, 'missing')})" for r in runs
                       for s in r.sides.get("twin", []) for name in s.stops})
    held = sorted({note for note in notes if "held as record numbers" in note})
    return (f"tables: {tables}; bars judged: {judged or 'none'}; bars void: {void or 'none'}; "
            f"bars not read in this run: {unread or 'none'}; columns the twin's description holds: "
            f"{' | '.join(held) or 'none'}; stopping on the twin: {'; '.join(stopping) or 'none'}; "
            f"twin variance components on ST7: {json.dumps(M.varcomp(runs, 'twin'))}; "
            f"labelled routes beside the twin over the same runs: {json.dumps(_finite(routes), sort_keys=True)}; "
            f"curvature: {json.dumps(_finite(found.get('curvature', {})), sort_keys=True)}; "
            f"notes: {' | '.join(notes) or 'none'}; {more}{round(seconds, 1)} s")


def run_tier(tier: str, folder: pathlib.Path, tables: "list[str]", route: str, extra: "tuple[str, ...]",
             layer_tree: "str | None", seeds: "tuple[int, ...] | None" = None) -> "tuple[list[Any], float]":
    M = _battery()
    started = time.perf_counter()
    settings = dict(M.TIERS[tier])
    if seeds:
        settings["seeds"] = seeds
    kept = os.environ.get("SYNTHTWIN_MODEL_RUNS")
    code = panel_code_digest()
    routes = kept_routes(route, extra)
    runs = []
    for table in tables:
        for seed in settings["seeds"]:  # type: ignore[attr-defined]
            saved = kept_file(pathlib.Path(kept), table, seed, routes) if kept else None
            if saved is not None and saved.exists():
                record = json.loads(saved.read_text(encoding="utf-8"))
                if record.get("code") == code and record.get("routes") == routes:
                    runs += [M.run_from_dict(record["run"])]
                    print(f"{table} seed {seed}: read back from {saved}", flush=True)
                    continue
            run = M.run_table(table, settings["rows"], seed, settings["twins"], folder / f"{table}-{seed}",  # type: ignore
                              route, extra)
            print(f"{table} seed {seed}: {run.seconds:.0f} s ({run.product_seconds:.0f} s in the product)", flush=True)
            if saved is not None:
                saved.parent.mkdir(parents=True, exist_ok=True)
                saved.write_text(json.dumps({"code": code, "routes": routes, "run": M.run_to_dict(run)}),
                                 encoding="utf-8", newline="\n")
            runs += [run]
    if layer_tree:
        attach(runs, layer_runs(layer_tree, tables, settings["rows"], settings["seeds"],  # type: ignore[arg-type]
                                settings["twins"][:1], folder))  # type: ignore[index]
    return runs, time.perf_counter() - started


def robust_or_exit(runs: "list[Any]") -> None:
    """Exit 1 with no KPI line where an analysis of the owner's four families is not robust on a real table, naming it."""
    unrobust = _battery().owner_four_unrobust(runs)
    if unrobust:
        print("K-BC-14 NOT STAMPED: the owner's four families are not all measured on these real tables: "
              + "; ".join(unrobust), flush=True)
        sys.exit(1)


def emit(runs: "list[Any]", suffix: str, seconds: float, extra_keys: "dict[str, object]", more: str = "") -> None:
    M = _battery()
    robust_or_exit(runs)
    found = M.measures(runs, suffix)
    value = dict(found["value"])
    value[f"route{suffix}"] = {r.table: r.route for r in runs}
    value.update(extra_keys)
    # The tier this run produced: an ordinary `kpi_run.py --slow` judges K-BC-14's keys of that tier alone (its other
    # tier on its own run; `kpi_rules.tier_bounds`).
    kpi_rules.emit("K-BC-14", _finite(value), detail_text(found, runs, seconds, more), tiers=[suffix])


def _finite(value: object) -> object:
    """A value the ledger can hold (`model_utility.finite`: no NaN or infinity at any depth; skeptic 1's item 7)."""
    return _battery().finite(value)


def ledger_stamp_20k(path: "pathlib.Path | None" = None) -> "tuple[dict[str, list[object]], str]":
    """The 20,000-row family shares of the ledger's K-BC-14 stamp (``path``: the repository's ledger where None), and
    that stamp's commit and date (or '' where no K-BC-14 entry, or none with 20,000-row shares, stands)."""
    try:
        ledger = json.loads((path or ROOT / "tests" / "kpi" / "ledger.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}, ""
    for entry in ledger.get("entries", []):
        if entry.get("id") == "K-BC-14":
            at = entry.get("value_at") or {}
            fam = (at.get("value") or {}).get("fam_20k")
            return (fam if isinstance(fam, dict) else {}), f"{at.get('commit', '')} ({at.get('date', '')})"
    return {}, ""


def run_truths(folder: pathlib.Path, tables: "list[str]", rows: int = NIGHT_ROWS) -> bool:
    """Every table's truth-holding analyses at ``rows`` rows, a child each: True where none stops and none misses."""
    held = True
    for table in tables:
        wait_turn(f"{table} truths")
        record = child(["--truths", table, "--rows", str(rows)], folder / f"truths-{table}.json")
        if record is None:
            held = False
            continue
        found = record["truths"][table]
        print(f"{table} truths at {rows:,} rows: stopped {found['stopped'] or 'none'}; missed "
              f"{found['misses'] or 'none'} ({record['cpu_s']} CPU s, peak {record['peak_mb']} MB)", flush=True)
        held = held and not found["stopped"] and not found["misses"]
    return held


def run_night(folder: pathlib.Path, tables: "list[str]", layer_tree: "str | None") -> None:
    if not run_truths(folder, tables):
        sys.exit(1)
    started = time.perf_counter()
    found = []
    for table in tables:
        wait_turn(table)
        record = child(["--one", table, "--rows", str(NIGHT_ROWS), "--out", str(folder)], folder / f"{table}.json")
        if record is None:
            sys.exit(1)
        print(f"{table}: {record['seconds']} s wall, {record['cpu_s']} CPU s, peak {record['peak_mb']} MB", flush=True)
        found += [record]
    M = _battery()
    runs = [M.run_from_dict(record["run"]) for record in found]
    if layer_tree:
        attach(runs, layer_runs(layer_tree, tables, NIGHT_ROWS, (1,), (0,), folder))
    value = M.measures(runs, "_200k")["value"]
    fam_20k, stamp = ledger_stamp_20k()
    keys: "dict[str, object]" = {
        "seconds_per_table_200k": {r["run"]["table"]: r["seconds"] for r in found},
        "cpu_seconds_per_table_200k": {r["run"]["table"]: r["cpu_s"] for r in found},
        "peak_mb_200k": max((r["peak_mb"] for r in found if r["peak_mb"] is not None), default=None),
        "drift": M.drift(fam_20k, value["fam_200k"]),
    }
    more = (f"drift: the 20,000-row shares of the ledger's K-BC-14 stamp at {stamp or 'none (no 20,000-row stamp)'}, "
            f"the 200,000-row shares of this head {head_commit()}; ")
    emit(runs, "_200k", time.perf_counter() - started, keys, more)


def main(argv: "list[str] | None" = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--kpi", action="store_true", help="the 20,000-row tier")
    parser.add_argument("--night", action="store_true", help="the 200,000-row tier, a child per table")
    parser.add_argument("--preview", metavar="TREE", help="another tree's src (an extracted copy of a branch head)")
    parser.add_argument("--layer-tree", metavar="TREE", help="route P's tree for ST7 and ST8, in a child process")
    parser.add_argument("--one", metavar="TABLE", help="one table in this process")
    parser.add_argument("--truths", metavar="TABLE", help="one table's truth-holding analyses in this process")
    parser.add_argument("--tables", help="a comma-separated subset of the tables")
    parser.add_argument("--seeds", help="a comma-separated subset of the tier's table seeds (a preview's cost)")
    parser.add_argument("--rows", type=int, default=NIGHT_ROWS)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--twins", default="0")
    parser.add_argument("--route", default="S", choices=list(twin_routes.ROUTES))
    parser.add_argument("--no-controls", action="store_true", help="--one without the replicate and shuffled twin")
    parser.add_argument("--json", help="where --one and --truths write their record")
    parser.add_argument("--out", help="the folder for tables, descriptions and twins")
    args = parser.parse_args(argv)
    # The guard ran as the module was read (above), the preview's tree named where there is one.
    tables = args.tables.split(",") if args.tables else list(U.TABLES)
    if args.truths:
        started = time.perf_counter()
        truths = _battery().generated_truth_checks((args.truths,), args.rows, args.seed)
        record = {"truths": truths, "seconds": round(time.perf_counter() - started, 1), "cpu_s": cpu_seconds(),
                  "peak_mb": peak_mb()}
        pathlib.Path(args.json).write_text(json.dumps(record), encoding="utf-8", newline="\n")
        return 0
    if args.one:
        M = _battery()
        started = time.perf_counter()
        twins = tuple(int(k) for k in args.twins.split(","))
        run = M.run_table(args.one, args.rows, args.seed, twins, pathlib.Path(args.out) / f"{args.one}-{args.seed}",
                          args.route, controls=not args.no_controls)
        record = {"run": M.run_to_dict(run), "seconds": round(time.perf_counter() - started, 1),
                  "cpu_s": cpu_seconds(), "peak_mb": peak_mb()}
        pathlib.Path(args.json).write_text(json.dumps(_finite(record)), encoding="utf-8", newline="\n")
        return 0
    with tempfile.TemporaryDirectory(prefix="synthtwin-utility-") as scratch:
        folder = pathlib.Path(args.out) if args.out else pathlib.Path(scratch)
        folder.mkdir(parents=True, exist_ok=True)
        if args.kpi or PREVIEW:
            # Route U beside route S where the typed commands switch the chain on (elsewhere route U is route S).
            unswitched = ("U",) if twin_routes.typed_switched() else ()
            extra = (("C",) + unswitched + ("P",)) if PREVIEW else (unswitched + ("P",))
            seeds = tuple(int(x) for x in args.seeds.split(",")) if args.seeds else None
            runs, seconds = run_tier("slow", folder / "slow", tables, "S", extra, args.layer_tree, seeds)
            more = "" if unswitched else "route U is route S on this tree (its typed commands do not switch); "
            emit(runs, "_20k", seconds, {"seconds_20k": round(seconds, 1)}, more)
        if args.night:
            (folder / "night").mkdir(parents=True, exist_ok=True)
            run_night(folder / "night", tables, args.layer_tree)
    return 0


if __name__ == "__main__":
    sys.exit(main())
