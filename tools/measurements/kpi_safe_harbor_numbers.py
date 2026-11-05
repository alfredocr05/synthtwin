"""K-HZ-15: lane SH's Safe Harbor numbers at 20,000 rows, the cases moved out of the suite (plan P4-D444).

THE SUITE'S TIME (the orchestrator's rule of 2026-10-26; batch 4l OWES 3,
lane SPD): `tests/test_safe_harbor_numbers.py` took 2,705.8 s, most of it in
its 20,000-row grids. The suite keeps every 600-row case and ONE 20,000-row
case (`safe_harbor_checks.KEPT_AT_20000`) as the floor-size proof; this
driver runs every other 20,000-row case of that file, one item a removed
case, through the SAME check (`tests/safe_harbor_checks.py`), at the owner's
table floor of 20,000 rows, seed 0, the CSV writer the file's tables use:

- `unanswered:<kind>`: each shape of `shapes.SAFE_HARBOR_NUMBERS` (ZIP
  codes of four, five or nine figures in every role, beside words and
  placeholders of any share; ages above 89 in every role, beside an
  outlier, placeholders or words of any share, with a unit word, a plus
  sign, an undeclared decimal comma, one padded cell or an open person
  question; account numbers put the date-count question alone), profiled
  with nothing answered, generated and validated: `check` (0 ZIPs and 0
  ages over 89 in any file and the twin, the one question put, the
  top-code, the validations under the stated limits
  `shapes.SAFE_HARBOR_HELD_LIMITS_AT_20000`);
- `answered:<kind>:<answer>`: each of `shapes.SAFE_HARBOR_ANSWERED`, the
  column's other question answered first: `check_answered`;
- `zoo_zips`: the zoo's `patients.zip5` answered `code` and then `yes`:
  `check_zoo_zips`;
- `padded_cell_measurement`: one `07` beside 20,000 ages declared
  `--measurement`: `check_a_padded_cell_answered_measurement`.

Every leak count reads by a counter LINEAR IN THE DATA (the rule's (3)):
ZIPs by `shapes.count_real(..., linear=True)`, which is
`shapes._count_real_linear` (the real values and their fragments in two
lookups, each text and each different twin cell scanned once), ages by
`shapes.number_token_counts` (each text read once). It prints one line an
item -- the check's verdict, each count, the chance cells counted apart,
the product's seconds (profile, generate and validate) apart from the
counting -- and exits 1 when any item breaches its check, and when the
choice of items selects none. Each count is read and summed under either
verdict, since each item keeps what it measured before its check judges
it; an item that crashed before it measured anything says
`counts unavailable` and adds `cases_without_counts` to the value, a key
a whole green run never has. `padded_cell_measurement` writes no twin:
it profiles the one table (20,001 rows) and reads the description and
the questions, as the case it was did, and its count is the published
numbers over the top-code, summed into `description_values`. The same
lines are written to `synthtwin-kpi/kpi_safe_harbor_numbers-items.txt`
under the system's temporary folder (beside kpi_run's report), since
kpi_run keeps only a driver's KPI line. The value:
items run (`cases`), items failing (`cases_failing`, target 0) and the
four counts summed (target 0 each). `--only` is for a mutant's red and
never writes the KPI line. 3,614 s under kpi_run at one-minute load 33
to 47 (plan P4-D444); one process, the tables written to a temporary folder, each
removed after its item.

    .venv/bin/python tools/measurements/kpi_safe_harbor_numbers.py --kpi
    .venv/bin/python tools/measurements/kpi_safe_harbor_numbers.py --only 'unanswered:age_person'
"""

import argparse
import fnmatch
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
from synthtwin import cli  # noqa: E402

import safe_harbor_checks as checks  # noqa: E402
import unanswered_identifier_shapes as shapes  # noqa: E402

ROWS = 20000
ITEMS = pathlib.Path(tempfile.gettempdir()) / "synthtwin-kpi" / "kpi_safe_harbor_numbers-items.txt"
COUNTS = ("description_values", "description_fragments", "twin_cells", "twin_fragments")


# An item fills its holder before its check judges it, so the counts of a
# failing item are read as a passing item's are.
Item = typing.Callable[[pathlib.Path, "dict[str, object]"], None]


def _unanswered(kind: str) -> Item:
    def run(folder: pathlib.Path, seen: "dict[str, object]") -> None:
        seen.update(shapes.run_safe_harbor(folder, kind, ROWS, linear=True))
        checks.check(seen, kind, ROWS)
    return run


def _answered(kind: str, answer: str) -> Item:
    def run(folder: pathlib.Path, seen: "dict[str, object]") -> None:
        seen.update(shapes.run_safe_harbor(folder, kind, ROWS, answer, linear=True))
        checks.check_answered(seen, kind)
    return run


def _zoo(folder: pathlib.Path, seen: "dict[str, object]") -> None:
    seen.update(shapes.run_zoo_zips(folder, ROWS, linear=True))
    checks.check_zoo_zips(seen)


def _padded(folder: pathlib.Path, seen: "dict[str, object]") -> None:
    checks.check_a_padded_cell_answered_measurement(folder, seen)


def items() -> "list[tuple[str, Item]]":
    """Every moved case, one item each, in the file's order."""
    found: "list[tuple[str, Item]]" = []
    for kind in shapes.SAFE_HARBOR_NUMBERS:
        if kind != checks.KEPT_AT_20000:
            found += [(f"unanswered:{kind}", _unanswered(kind))]
    for kind, answer in shapes.SAFE_HARBOR_ANSWERED:
        found += [(f"answered:{kind}:{answer}", _answered(kind, answer))]
    found += [("zoo_zips", _zoo), ("padded_cell_measurement", _padded)]
    return found


def main(arguments: "list[str]") -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--kpi", action="store_true", help="print the KPI line (kpi_run passes it)")
    parser.add_argument("--only", action="append", default=[],
                        help="run only the items whose name matches this pattern (repeatable)")
    chosen = parser.parse_args(arguments)
    if chosen.kpi and chosen.only:
        parser.error("--only runs some of the items, so it never writes the KPI line: drop --kpi or --only")
    product = {"seconds": 0.0}
    real_main = cli.main

    def timed(argv: "list[str]", **internal: object) -> int:
        started = time.monotonic()
        try:
            return real_main(argv, **internal)  # type: ignore[arg-type]
        finally:
            product["seconds"] += time.monotonic() - started

    value: "dict[str, int]" = {"cases": 0, "cases_failing": 0}
    value.update({name: 0 for name in COUNTS})
    chance = without_counts = 0
    ITEMS.parent.mkdir(parents=True, exist_ok=True)
    ITEMS.write_text("", encoding="utf-8")

    def said(line: str) -> None:
        print(line, flush=True)
        with ITEMS.open("a", encoding="utf-8") as written:
            written.write(line + "\n")

    cli.main = timed  # type: ignore[assignment]
    try:
        with tempfile.TemporaryDirectory() as scratch_name:
            for name, run in items():
                if chosen.only and not any(fnmatch.fnmatch(name, one) for one in chosen.only):
                    continue
                folder = pathlib.Path(scratch_name) / name.replace(":", "-")
                folder.mkdir()
                product["seconds"] = 0.0
                started = time.monotonic()
                verdict, why = "PASS", ""
                seen: "dict[str, object]" = {}
                try:
                    run(folder, seen)
                except AssertionError as failure:
                    verdict, why = "FAIL", f"{failure}" or traceback.format_exc(limit=-1).strip()
                except Exception as failure:  # noqa: BLE001 -- every failure is named and judged
                    verdict, why = "FAIL", f"{type(failure).__name__}: {failure}"
                wall = time.monotonic() - started
                value["cases"] += 1
                if verdict == "FAIL":
                    value["cases_failing"] += 1
                counted = []
                for key in COUNTS:
                    if isinstance(seen.get(key), int):
                        value[key] += int(seen[key])  # type: ignore[call-overload]
                        counted += [f"{key}={seen[key]}"]
                if isinstance(seen.get(checks.OVER_THE_TOP_CODE), int):
                    value["description_values"] += int(seen[checks.OVER_THE_TOP_CODE])  # type: ignore[call-overload]
                    counted += [f"{checks.OVER_THE_TOP_CODE}={seen[checks.OVER_THE_TOP_CODE]}"]
                if not counted:
                    without_counts += 1
                    counted += ["counts unavailable"]
                if isinstance(seen.get("twin_cells_by_chance"), int):
                    chance += int(seen["twin_cells_by_chance"])  # type: ignore[call-overload]
                    counted += [f"twin_cells_by_chance={seen['twin_cells_by_chance']}"]
                said(f"{name}: {verdict} {' '.join(counted)} product {product['seconds']:.1f} s, "
                     f"counting and checks {wall - product['seconds']:.1f} s"
                     + (f" -- {why[:600]}" if why else ""))
                shutil.rmtree(folder, ignore_errors=True)
    finally:
        cli.main = real_main  # type: ignore[assignment]
    said(f"made-up ZIP cells equal to a real one by chance, counted apart: {chance}")
    detail = f"{value['cases']} cases at {ROWS:,} rows, {value['cases_failing']} failing"
    if without_counts:
        value["cases_without_counts"] = without_counts
        detail += f", {without_counts} of them with no counts"
    said(detail)
    if not value["cases"]:
        said(f"no item matches {chosen.only}: nothing was measured")
        return 1
    if chosen.kpi:
        kpi_rules.emit("K-HZ-15", value, detail)
    return 1 if value["cases_failing"] or any(value[key] for key in COUNTS) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
