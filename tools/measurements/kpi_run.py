"""The ONE command that reruns every KPI and says whether anything behind is broken.

    .venv/bin/python tools/measurements/kpi_run.py [--slow] [--only 'K-2B-*'] \
        [--report PATH] [--print-values]

The owner, 2026-09-18: "when we will be stages ahead from here, we will
rerun everything and know that nothing behind is broken." This is that
rerun. It reads `tests/kpi/ledger.json`, measures every entry it selects,
and prints one line per KPI -- id, name, the value measured now, the rule
and a verdict -- grouped by phase or stage with the headlines first.

HOW EACH ENTRY IS MEASURED.
* Its PINNED nodes and its own KPI test (tests/test_kpi_ledger.py) run in
  ONE pytest subprocess with `--junitxml`; each KPI test records its value
  through `record_property("kpi", ...)`, and the pinned nodes are counted
  as `pinned_nodes_failing`.
* With `--slow`, the pinned nodes in the ledger's slow files also run, and
  every driver the ledger names runs with `--kpi`, printing one line
  `KPI {"id": ..., "value": ..., "detail": ...}` per entry it measures.
* The value is judged by `tests/kpi_rules.py`, the same code the KPI
  tests judge with, so the runner and the suite cannot disagree.

EXIT CODES. 0 when every GREEN entry passes and every OPEN or
ACCEPTED_LIMIT entry is at or inside its must-not-get-worse bound; 1 on
any drop, and a KPI test that fails before it records its value is a
drop (FAIL), as is an entry whose DRIVER exited non-zero, whatever the
driver printed before it died; 2 when the ledger fails its own
integrity check (a pinned
node that no longer exists or is not collected, fewer pinned cases
collected than the entry's `nodes_min_collected`, a pinned case that was
SKIPPED -- a skipped case measures nothing, so it may never read as a
pass -- unless the entry lists that node in `allowed_skips`, a KPI test
with no entry, and the rest of `kpi_rules.integrity_problems`) or when
synthtwin would not be imported from this tree's `src`. An OPEN entry
that reaches its target prints IMPROVED and asks for its status to be
flipped; it never fails.

WHAT THE MACHINE DECIDES. A rule of a MACHINE KIND (`kpi_rules.MACHINE_KINDS`:
an absolute time, `seconds_below`, and a peak memory, `peak_memory_below`)
is judged only on the reference machine the ledger names -- its
architecture and core count, and never a continuous-integration runner --
and only while its one-minute load average is under the ledger's
`quiet_load_average_below`. Anywhere else such a rule warns, its number
is REPORTED and never failed, and the machine-free ratio or count beside
it is what can fail. Peak memory joined seconds here on 2026-09-20:
a million-cell workbook refused at 539 MB on the reference machine read
703 MB on a CI runner, against a bound of 600, with no change in the code.

WHAT IT NEVER DOES. It never rewrites the ledger. `--print-values`
prints what it measured in the ledger's own `value_at` form -- value,
commit, date -- for a person to review and write in, in a commit whose
CHANGELOG entry names the ids.

The report (`--report`, default kpi-report.json under the system's temp
folder) is the machine-readable form the owner's board reads: one row per
KPI with id, phase_stage, category, headline, name, status, rule, value
now and pass.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ElementTree

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src"
sys.path.insert(0, str(SOURCE))
sys.path.insert(0, str(ROOT / "tests"))

import kpi_rules  # noqa: E402

GROUP_ORDER = ("P0", "P1", "P2", "P3", "P4", "S1", "S2", "2B", "S3", "S4", "S5", "S6", "S7", "S8")
GROUP_TITLES = {
    "P0": "Phase 0 - skeleton and security",
    "P1": "Phase 1 - the profiler",
    "P2": "Phase 2 - the generator",
    "P3": "Phase 3 - the end-to-end product",
    "P4": "Phase 4 - comprehensive column handling",
    "S1": "Stage 1 - speed",
    "S2": "Stage 2 - spellings",
    "2B": "Stage 2b - the twin writes as the source wrote",
    "S6": "Stage 6 - relationships between columns (baseline)",
}


def _environment() -> "dict[str, str]":
    environment = dict(os.environ)
    environment["PYTHONPATH"] = os.pathsep.join(
        [str(SOURCE)] + [p for p in [environment.get("PYTHONPATH", "")] if p]
    )
    return environment


def _refuse_unless_this_tree() -> str:
    """The synthtwin this run measures must be the one under ./src, here and in pytest.

    THIS IS A STRICTER RULE THAN `kpi_rules.guard_this_tree`, on purpose,
    and the difference is the arrangement each one runs in. This command
    is the source tree's own: it puts `./src` first on its own path and
    on every child's `PYTHONPATH` above, so the module it wants is
    always reachable and anything else resolving instead is a fault to
    stop on. `guard_this_tree` runs inside the drivers, which the suite
    also drives when CI has installed the wheel built from this commit
    and is testing THAT -- so it asks whether the imported package IS
    this tree's code rather than where it sits.
    """
    import synthtwin

    here = pathlib.Path(synthtwin.__file__).resolve()
    print(f"synthtwin imported from {here}")
    probe = subprocess.run(
        [sys.executable, "-c", "import synthtwin; print(synthtwin.__file__)"],
        cwd=str(ROOT), env=_environment(), capture_output=True, text=True, check=False,
    )
    child = pathlib.Path(probe.stdout.strip() or "/nonexistent").resolve()
    for place in (here, child):
        if SOURCE.resolve() not in place.parents:
            print(
                f"REFUSING: synthtwin resolves to {place}, not under {SOURCE}. "
                "An installed copy from another checkout would be measured instead "
                "of this tree. Run from this checkout's own environment.",
                flush=True,
            )
            sys.exit(kpi_rules.REFUSED_EXIT)
    return str(here)


def _commit() -> str:
    done = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], cwd=str(ROOT),
        capture_output=True, text=True, check=False,
    )
    return done.stdout.strip() or "unknown"


def _is_slow_node(ledger: "dict", node: str) -> bool:
    return node.split("::")[0] in ledger["slow_pytest_files"] or node in ledger["slow_nodes"]


def _run_pytest(nodes: "list[str]", work: pathlib.Path) -> "dict[str, list[dict]]":
    """Run the nodes in one pytest process; return per 'file::function' its cases."""
    if not nodes:
        return {}
    junit = work / "junit.xml"
    command = [
        sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
        f"--basetemp={work / 'pytest'}", "-o", "junit_family=xunit1",
        f"--junitxml={junit}", *nodes,
    ]
    print(f"running pytest over {len(nodes)} node ids ...", flush=True)
    subprocess.run(command, cwd=str(ROOT), env=_environment(), check=False,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    cases: "dict[str, list[dict]]" = {}
    if not junit.exists():
        return cases
    for case in ElementTree.parse(junit).iter("testcase"):
        module = case.get("classname", "").split(".")
        name = case.get("name", "").split("[")[0]
        path = "/".join(module) + ".py"
        outcome = "passed"
        for child in case:
            if child.tag in ("failure", "error"):
                outcome = "failed"
            elif child.tag == "skipped" and outcome == "passed":
                outcome = "skipped"
        kpi = None
        for prop in case.iter("property"):
            if prop.get("name") == "kpi":
                kpi = json.loads(prop.get("value") or "null")
        cases.setdefault(f"{path}::{name}", []).append({"outcome": outcome, "kpi": kpi})
    return cases


def _run_drivers(commands: "list[str]") -> "tuple[dict[str, list[dict]], dict[str, int]]":
    """Run each driver with its arguments; its KPI lines by id, AND how it exited.

    A DRIVER THAT PRINTED A VALUE AND THEN DIED HAS MEASURED NOTHING
    (round-2 ledger item 5). Its exit status used to be printed and
    thrown away, so a driver that emitted K-2B-14's record and then
    failed an assertion, exiting 1, produced verdict PASS, pass True,
    partial False: the runner reported green over a measurement that
    never finished. The status is returned beside the records now, and
    `judge_rows` fails every entry a non-zero driver was to measure.
    """
    found: "dict[str, list[dict]]" = {}
    exits: "dict[str, int]" = {}
    for command in commands:
        parts = command.split()
        print(f"running {command} ...", flush=True)
        done = subprocess.run(
            [sys.executable, *parts], cwd=str(ROOT), env=_environment(),
            capture_output=True, text=True, check=False,
        )
        exits[command] = done.returncode
        lines = [line[4:] for line in done.stdout.splitlines() if line.startswith("KPI ")]
        if done.returncode != 0 or not lines:
            print(f"  the driver exited {done.returncode} and printed {len(lines)} KPI lines")
            print("  " + done.stderr.strip()[-800:].replace("\n", "\n  "))
        for line in lines:
            record = json.loads(line)
            found.setdefault(record["id"], []).append(record)
    return found, exits


def _merge(parts: "list[object]") -> object:
    """One value from the test's, the drivers' and the nodes' parts."""
    dicts = [p for p in parts if isinstance(p, dict)]
    if len(dicts) == len(parts):
        merged: "dict" = {}
        for part in dicts:
            merged.update(part)
        return merged
    return parts[0] if len(parts) == 1 else parts


def _shown(value: object, width: int = 70) -> str:
    if isinstance(value, dict):
        text = ", ".join(f"{k}={v}" for k, v in value.items() if not isinstance(v, (dict, list)))
        if len(value) > 12 and not text:
            text = f"{len(value)} keyed values"
    else:
        text = json.dumps(value)
    return text if len(text) <= width else text[: width - 3] + "..."


def measure(entries: "list[dict]", ledger: "dict", slow: bool, work: pathlib.Path) -> "list[dict]":
    """Measure the entries; return one result row per entry."""
    nodes: "list[str]" = []
    for entry in entries:
        for node in entry.get("nodes", []):
            if slow or not _is_slow_node(ledger, node):
                nodes += [node]
        if entry.get("test"):
            nodes += [entry["test"]]
    cases = _run_pytest(sorted(set(nodes)), work)
    drivers: "dict[str, list[dict]]" = {}
    driver_exits: "dict[str, int]" = {}
    if slow:
        drivers, driver_exits = _run_drivers(
            sorted({e["driver"] for e in entries if e.get("driver")})
        )
    seconds_count, _why = kpi_rules.seconds_judged_here(ledger)
    return judge_rows(entries, ledger, slow, cases, drivers, seconds_count, driver_exits)


def judge_rows(
    entries: "list[dict]", ledger: "dict", slow: bool,
    cases: "dict[str, list[dict]]", drivers: "dict[str, list[dict]]", seconds_count: bool,
    driver_exits: "dict[str, int] | None" = None,
) -> "list[dict]":
    """One result row per entry, from the pytest cases and driver records already gathered.

    ``cases`` maps 'file::function' to its collected cases, each
    {"outcome": "passed" | "failed" | "skipped", "kpi": recorded or None}.
    ``driver_exits`` maps a driver command to the status it exited with;
    a command absent from it was not run here, and one that exited
    non-zero FAILS every entry it was to measure, whatever it printed
    before it died. A PROBLEM is an integrity fault (exit 2); a FAILURE
    is a drop (exit 1).
    """
    rows = []
    for entry in entries:
        parts: "list[object]" = []
        details: "list[str]" = []
        partial = False
        problem = ""
        failure = ""
        failed_after = False
        test_skipped = False
        test = entry.get("test")
        if test:
            ran = cases.get(test, [])
            if not ran:
                problem = f"its test {test} was not collected"
            elif ran[0]["kpi"] is not None:
                parts += [ran[0]["kpi"]["value"]]
                if ran[0]["kpi"].get("detail"):
                    details += [ran[0]["kpi"]["detail"]]
                failed_after = ran[0]["outcome"] == "failed"
            elif ran[0]["outcome"] == "skipped":
                test_skipped = True
            else:
                failure = f"its test {ran[0]['outcome']} before recording a value"
        failing = collected = 0
        slow_left = 0
        allowed = set(entry.get("allowed_skips", []))
        for node in entry.get("nodes", []):
            if not slow and _is_slow_node(ledger, node):
                slow_left += 1
                continue
            ran = cases.get(node, [])
            if not ran:
                problem = f"pinned node {node} was not collected"
            skipped = sum(1 for case in ran if case["outcome"] == "skipped")
            if skipped and node not in allowed:
                problem = (f"{skipped} case(s) of pinned node {node} were SKIPPED: a skipped "
                           "case measures nothing (list the node in allowed_skips only "
                           "where a skip is the rule)")
            collected += len(ran) - skipped
            failing += sum(1 for case in ran if case["outcome"] == "failed")
        if entry.get("nodes") and slow_left < len(entry["nodes"]):
            parts += [{"pinned_nodes_failing": failing}]
            if not problem and collected < entry.get("nodes_min_collected", 0):
                problem = (f"{collected} pinned cases collected and run, fewer than the "
                           f"{entry['nodes_min_collected']} the ledger requires")
        partial = slow_left > 0 or test_skipped
        if entry.get("driver"):
            if slow:
                records = drivers.get(entry["id"], [])
                if records:
                    parts += [record["value"] for record in records]
                    details += [r["detail"] for r in records if r.get("detail")]
                else:
                    problem = f"its driver {entry['driver']} printed no value for it"
                code = (driver_exits or {}).get(entry["driver"])
                if code:
                    # It printed a value and then died: the measurement
                    # did not finish, so nothing it printed is a pass.
                    failure = (
                        f"its driver {entry['driver']} exited {code}: the measurement "
                        "did not finish, so the value it printed is not a pass"
                    )
            else:
                partial = True
        if problem:
            word = "INTEGRITY"
            message = problem
            value: object = None
        elif failure:
            word, message = kpi_rules.FAIL, failure
            value = _merge(parts) if parts else None
        elif test_skipped and not parts:
            word, message, value = kpi_rules.NOT_MEASURED, "its test was skipped here", None
        elif not parts:
            word, message, value = kpi_rules.NOT_RUN, "slow tier: run with --slow", None
        else:
            value = _merge(parts)
            verdict = kpi_rules.judge(entry, value, seconds_count, partial)
            word, message = verdict.word, verdict.message
            if failed_after and word not in kpi_rules.DROPS:
                # The test judged its value red, or failed on an assertion
                # of its own after recording it: never a pass.
                word, message = kpi_rules.FAIL, f"its test failed after recording (runner: {message})"
            if partial and word not in kpi_rules.DROPS:
                message += " (fast part only: run with --slow for the rest)"
        rows += [{
            "id": entry["id"], "phase_stage": entry["phase_stage"],
            "group": kpi_rules.group_of(entry["id"]), "category": entry["category"],
            "headline": entry["headline"], "name": entry["name"], "status": entry["status"],
            "rule": entry["rule"], "value_now": value, "verdict": word, "message": message,
            "pass": word not in kpi_rules.DROPS and word != "INTEGRITY",
            "partial": partial, "tier": entry["tier"], "detail": "; ".join(details),
            "value_at": entry.get("value_at"),
        }]
    return rows


def main(argv: "list[str] | None" = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--slow", action="store_true", help="also run the slow nodes and every driver")
    parser.add_argument("--only", action="append", default=[], metavar="PATTERN",
                        help="only the ids matching this shell pattern (repeatable), e.g. 'K-2B-*'")
    parser.add_argument("--report", default=str(pathlib.Path(tempfile.gettempdir()) / "synthtwin-kpi" / "kpi-report.json"),
                        help="where to write the machine-readable report")
    parser.add_argument("--print-values", action="store_true",
                        help="print the measured values in the ledger's value_at form, for review")
    args = parser.parse_args(argv)

    module = _refuse_unless_this_tree()
    ledger = kpi_rules.load_ledger()
    problems = kpi_rules.integrity_problems(ledger)
    if problems:
        print("THE LEDGER FAILS ITS OWN INTEGRITY CHECK:")
        for problem in problems:
            print(f"  {problem}")
        return kpi_rules.REFUSED_EXIT
    entries = kpi_rules.select(ledger["entries"], args.only)
    if not entries:
        print(f"no ledger id matches {args.only}")
        return kpi_rules.REFUSED_EXIT
    on_reference = kpi_rules.on_reference_machine(ledger)
    seconds_count, why = kpi_rules.seconds_judged_here(ledger)
    if not seconds_count:
        print(f"WARNING: {why}; rules of a machine kind "
              f"({', '.join(kpi_rules.MACHINE_KINDS)}) are reported, never failed, "
              "and ratios and counts still fail.")
    with tempfile.TemporaryDirectory(prefix="synthtwin-kpi-") as folder:
        rows = measure(entries, ledger, args.slow, pathlib.Path(folder))

    commit = _commit()
    width = max(len(r["id"]) for r in rows)
    print()
    print("* = headline on the owner's board. Columns: id | name | value now | verdict.")
    for group in GROUP_ORDER:
        mine = [r for r in rows if r["group"] == group]
        if not mine:
            continue
        print(f"== {GROUP_TITLES.get(group, group)} ==")
        for row in sorted(mine, key=lambda r: (not r["headline"], r["id"])):
            mark = "*" if row["headline"] else " "
            shown = "-" if row["value_now"] is None else _shown(row["value_now"])
            verdict = row["verdict"] + (
                " (fast part)" if row["partial"] and row["value_now"] is not None else "")
            print(f"{mark}{row['id']:<{width}} | {row['name'][:60]:<60} | "
                  f"{shown:<70} | {verdict}")
            if row["verdict"] not in (kpi_rules.PASS, kpi_rules.NOT_RUN, kpi_rules.OPEN_HELD,
                                      kpi_rules.ACCEPTED_HELD):
                print(f"  {'':<{width}}   rule: {row['rule'][:150]}")
                print(f"  {'':<{width}}   {row['message'][:200]}")
    totals: "dict[str, int]" = {}
    for row in rows:
        totals[row["verdict"]] = totals.get(row["verdict"], 0) + 1
    print()
    print("TOTALS " + ", ".join(f"{k} {v}" for k, v in sorted(totals.items()))
          + f" -- {len(rows)} KPIs, {sum(r['headline'] for r in rows)} headlines, "
          + ("slow tier included" if args.slow else "fast tier (add --slow for the rest)")
          + f", commit {commit}")
    drops = [r for r in rows if not r["pass"]]
    if drops:
        print("DROPS:")
        for row in drops:
            print(f"  {row['id']} {row['verdict']}: {row['message'][:200]}")
    else:
        print("DROPS: none")

    report = pathlib.Path(args.report)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps({
        "commit": commit, "date": datetime.date.today().isoformat(),
        "mode": "slow" if args.slow else "fast", "synthtwin": module,
        "reference_machine": on_reference, "machine_kinds_judged": seconds_count,
        "totals": totals,
        "kpis": [{k: r[k] for k in ("id", "phase_stage", "category", "headline", "name",
                                   "status", "rule", "value_now", "verdict", "pass",
                                   "partial", "tier", "detail")} for r in rows],
    }, indent=1, sort_keys=False, default=str) + "\n", encoding="utf-8")
    print(f"report written to {report}")

    if args.print_values:
        stamped = {
            r["id"]: {"value": r["value_now"], "commit": commit,
                      "date": datetime.date.today().isoformat()}
            for r in rows if r["value_now"] is not None
        }
        print("VALUES (the ledger's value_at form; review before writing any in):")
        print(json.dumps(stamped, indent=1, sort_keys=True))

    if any(r["verdict"] == "INTEGRITY" for r in rows):
        return kpi_rules.REFUSED_EXIT
    return 1 if drops else 0


if __name__ == "__main__":
    sys.exit(main())
