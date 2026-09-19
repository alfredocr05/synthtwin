"""K-P0-05: the decontamination scan over the whole repository, with its non-vacuity floor.

`tests/test_decontamination.py` asserts only that the scan exits 0, and
a scan that walked no file exits 0 too: on a copy of this repository
under a folder named `build`, the scanner's non-git fallback skipped
every file and printed `clean`. So this counts the files the scan
reads and the matches it finds, and the ledger holds both: at least
400 files, and none matching. About five minutes.

    .venv/bin/python tools/measurements/kpi_decontamination.py --kpi
"""

import contextlib
import importlib.util
import io
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import kpi_rules  # noqa: E402

kpi_rules.guard_this_tree()
sys.path.insert(0, str(ROOT / "tools" / "decontamination"))
spec = importlib.util.spec_from_file_location(
    "kpi_check", ROOT / "tools" / "decontamination" / "check.py"
)
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)
scanned = check.tracked_files(ROOT)
printed = io.StringIO()
with contextlib.redirect_stdout(printed), contextlib.redirect_stderr(printed):
    code = check.main([str(ROOT)])
lines = printed.getvalue().splitlines()
matches = sum(1 for line in lines if line.startswith("MATCH"))
violations = sum(1 for line in lines if line.startswith("VIOLATION"))
print(f"files scanned {len(scanned)}, matches {matches}, violations {violations}, exit {code}")
kpi_rules.emit(
    "K-P0-05",
    {"files_scanned": len(scanned), "matches": matches + violations, "exit": code},
)
