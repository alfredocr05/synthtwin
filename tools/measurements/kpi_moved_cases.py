"""K-HZ-21: the suite's large cases whose files' KPIs name no driver, moved out of the suite (plan P4-D461).

THE SUITE'S TIME, PART 2 (lane SPD2; the orchestrator's rule of 2026-10-26:
checks at 20,000 rows or more run in a KPI driver under `kpi_run --slow` or
as one case a writer). Four files' largest cases left the suite: their
files' KPIs (K-HZ-04, K-S4-15, K-S4-20 and K-S4-08) are measured by pytest nodes of
the ledger's own file and name no driver, so they come here, one item a
node the suite no longer collects, named by that node:

- `tests/test_zoo_identifiers.py` (lane CODES-3, plan P4-D428): the
  20,000-row leg of every case parametrized on its `SIZES`, at
  `MOVED_SIZE` and each row of the case's other parameters, read from the
  case's own marks, and the real VCF at the floor
  (`test_zoo_identifiers.moved_cases`, 44 items). Every 600-row leg, the
  CSV writer's floor-size proof, the one 20,000-row leg a lane mutant
  needs (`STAYS_AT_20000`) and the six legs a size-gated mutant of a
  hold route needs (`FLOOR_LEGS`, LANE SPD2 RULINGS 4 and 5) stay in the suite;
- `tests/test_stage4_numbers_and_codes.py` (lane S4b-num, plan P4-D390):
  the pool of a million-row register (one item), 2,041 s of the file's
  2,326 s in the suite's run of 2af926ce;
- `tests/test_stage4_number_tail.py` (lane G2T, plan P4-D405): the three
  cases at 200,000 and 250,000 rows (three items); its 20,000-row cases
  stay in the suite;
- `tests/test_stage4_describe_memory.py` (lanes S4d and H3, plan P4-D390):
  the bytes a row added from 40,000 to 80,000 rows (one item), which
  K-S4-08's own case in the suite measures by the same function against
  the same bound, and the 40,000-row legs of its two grids of bytes a row
  (six items), whose 20,000-row legs and 80,000-row stamps stay.

Each item CALLS THE SAME FUNCTION the suite's node called, imported from
its test module and never copied: the same tables, seeds, limits and
asserts, the case's own parameters, a folder of its own as `tmp_path`
and, where the case takes one, a `pytest.MonkeyPatch` undone after it.
The process runs with the table floor's internal default off on
`cli.main` and `cli.run`, as `tests/conftest.py` sets it for every case
(`kpi_rules.guard_this_tree`, and `cli.run` here), so each case meets the
command it met in the suite.

It prints one line an item -- its verdict and its seconds; a case's
asserts are its check and it reads no count, which the line says -- and,
on a failing item, the assert's own source line or the error. EVERY
ENDING OF A CASE BUT ITS RETURN IS A FAILURE OF THAT ITEM, AND THE RUN
GOES ON TO THE NEXT (Codex's review of lane SPD2, item 5; its skeptic 1,
item 3): an assert, an error, pytest's own outcomes (`pytest.raises`
whose exception never came raises `Failed`, a `BaseException`), and
`SystemExit` of any code; only an interrupt from the keyboard stops the
run. It exits 1 when any item fails, and when the choice of items selects
none. It REFUSES TO RUN under an optimizing Python (`-O` or
`PYTHONOPTIMIZE`, which kpi_run hands down), before importing a case:
Python drops a bare assert there, so a case would return as passed with
its checks never made (Codex's item 4). The same lines are written to
`synthtwin-kpi/kpi_moved_cases-items.txt` under the system's temporary
folder, since kpi_run keeps only a driver's KPI line. The value: items run
(`cases`) and items failing (`cases_failing`, target 0). `--only` is for
a mutant's red and never writes the KPI line; it takes an item's exact
name (a parametrized node's brackets as they are) or a shell pattern.
A module's `SHOWN_AS` names the line an item is printed under where its
node's name holds a fixture's own word (Codex's review of batch 4q, item
4: the short-arc shapes are printed by their place); `--only` reads the
printed name too.

    .venv/bin/python tools/measurements/kpi_moved_cases.py --kpi
    .venv/bin/python tools/measurements/kpi_moved_cases.py --only 'tests/test_zoo_identifiers.py::*'
    .venv/bin/python tools/measurements/kpi_moved_cases.py --only 'tests/test_zoo_identifiers.py::test_repeating_uids_are_put_q_id_and_held[4-20000]'
"""

import argparse
import fnmatch
import inspect
import linecache
import pathlib
import shutil
import sys
import tempfile
import time
import traceback
import typing

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import kpi_rules  # noqa: E402

kpi_rules.guard_this_tree()
import pytest  # noqa: E402

from synthtwin import cli  # noqa: E402

ITEMS = pathlib.Path(tempfile.gettempdir()) / "synthtwin-kpi" / "kpi_moved_cases-items.txt"

# The test modules whose moved nodes this driver runs, each by its own
# `moved_cases()`: (node name, the function, its parameters).
MODULES = ("test_zoo_identifiers", "test_stage4_numbers_and_codes", "test_stage4_number_tail",
           "test_stage4_describe_memory")


def items() -> "list[tuple[str, typing.Callable[..., None], dict[str, object]]]":
    """Every moved node, one item each, named `tests/<file>::<node>` in the files' order."""
    found: "list[tuple[str, typing.Callable[..., None], dict[str, object]]]" = []
    for name in MODULES:
        module = __import__(name)
        for node, function, given in module.moved_cases():
            found += [(f"tests/{name}.py::{node}", function, dict(given))]
    return found


def shown_names() -> "dict[str, str]":
    """Each item whose module prints it under another name (its `SHOWN_AS`), that name, `tests/<file>::` before both."""
    shown: "dict[str, str]" = {}
    for name in MODULES:
        module = __import__(name)
        for node, printed in getattr(module, "SHOWN_AS", {}).items():
            shown[f"tests/{name}.py::{node}"] = f"tests/{name}.py::{printed}"
    return shown


def _the_floor_default_off() -> None:
    """`cli.run`'s internal default too, as tests/conftest.py moves it beside `cli.main`'s."""
    defaults = cli.run.__kwdefaults__
    if defaults is not None and "small_tables_refused" in defaults:
        defaults["small_tables_refused"] = False


def _failed_line(failure: BaseException) -> str:
    """The source line of the innermost frame a failure was raised in: a bare assert's only message outside pytest."""
    frames = traceback.extract_tb(failure.__traceback__)
    if not frames:
        return ""
    last = frames[len(frames) - 1]
    return linecache.getline(last.filename, last.lineno or 0).strip()


def run_one(function: "typing.Callable[..., None]", given: "dict[str, object]", folder: pathlib.Path) -> "tuple[str, str]":
    """One case, as the suite called it: its verdict and, when it fails, why."""
    wanted = inspect.signature(function).parameters
    arguments = dict(given)
    patch = pytest.MonkeyPatch()
    if "tmp_path" in wanted:
        arguments["tmp_path"] = folder
    if "monkeypatch" in wanted:
        arguments["monkeypatch"] = patch
    try:
        function(**arguments)
    except KeyboardInterrupt:
        raise
    except AssertionError as failure:
        return "FAIL", f"assert failed: {_failed_line(failure)}" + (f" -- {failure}" if f"{failure}" else "")
    except BaseException as failure:  # noqa: BLE001 -- pytest's outcomes and SystemExit too: every ending is named and judged
        return "FAIL", f"{type(failure).__name__}: {failure} (at: {_failed_line(failure)})"
    finally:
        patch.undo()
    return "PASS", ""


def _chosen(name: str, patterns: "list[str]", names: "set[str]") -> bool:
    """Whether ``--only`` names an item: a pattern that is an item's exact name chooses that item alone
    (a parametrized node's brackets are no character class); any other is a shell pattern."""
    return any(name == one if one in names else fnmatch.fnmatch(name, one) for one in patterns)


def _assertions_dropped() -> bool:
    """Whether this Python drops bare asserts (`-O`, `PYTHONOPTIMIZE`): the moved cases' every check is one."""
    return sys.flags.optimize > 0


def main(arguments: "list[str]") -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--kpi", action="store_true", help="print the KPI line (kpi_run passes it)")
    parser.add_argument("--only", action="append", default=[],
                        help="run only the items whose name matches this pattern (repeatable)")
    chosen = parser.parse_args(arguments)
    if chosen.kpi and chosen.only:
        parser.error("--only runs some of the items, so it never writes the KPI line: drop --kpi or --only")
    if _assertions_dropped():
        print("refused: this Python runs optimized (-O or PYTHONOPTIMIZE), which drops every bare assert "
              "the moved cases check with, so a case would pass unchecked: run it without. Nothing was measured.")
        return 2
    _the_floor_default_off()
    value = {"cases": 0, "cases_failing": 0}
    ITEMS.parent.mkdir(parents=True, exist_ok=True)
    ITEMS.write_text("", encoding="utf-8")

    def said(line: str) -> None:
        print(line, flush=True)
        with ITEMS.open("a", encoding="utf-8") as written:
            written.write(line + "\n")

    with tempfile.TemporaryDirectory() as scratch_name:
        every = items()
        shown = shown_names()
        names = {name for name, _function, _given in every} | set(shown.values())
        for place, (name, function, given) in enumerate(every):
            printed = shown[name] if name in shown else name
            if chosen.only and not (_chosen(name, chosen.only, names) or _chosen(printed, chosen.only, names)):
                continue
            folder = pathlib.Path(scratch_name) / f"case-{place}"
            folder.mkdir()
            started = time.monotonic()
            verdict, why = run_one(function, given, folder)
            wall = time.monotonic() - started
            value["cases"] += 1
            if verdict == "FAIL":
                value["cases_failing"] += 1
            said(f"{printed}: {verdict} no counts (the case's asserts are its check) {wall:.1f} s"
                 + (f" -- {why[:600]}" if why else ""))
            shutil.rmtree(folder, ignore_errors=True)
    detail = f"{value['cases']} moved cases, {value['cases_failing']} failing"
    said(detail)
    if not value["cases"]:
        said(f"no item matches {chosen.only}: nothing was measured")
        return 1
    if chosen.kpi:
        kpi_rules.emit("K-HZ-21", value, detail)
    return 1 if value["cases_failing"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
