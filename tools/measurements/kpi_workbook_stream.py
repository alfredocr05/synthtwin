"""K-S4-22: the workbook twin written as a stream -- the same bytes, and its peak and seconds.

Lane XW (plan P4-D411). The workbook writer of b075342a grew the sheet as
one text, a copy of the whole sheet per row, and was killed by the
library study's 1.9 GB guard at 19,999 rows of fifty columns after 44 s
and at 100,000 rows after 51 s. Today's writer makes the sheet a row at a
time and streams it into the zip member. Two measures:

* EXACT: every workbook golden of method G2.2, the workbook battery, lane
  E0a's zoo workbook and a seeded wide table, at the gate test's sizes and
  larger (`tests/workbook_stream_cases.py`), each written by the frozen
  b075342a writer and by today's: the count of workbooks that differ, and
  how many were compared. On madler's zlib a workbook differs where any
  byte does; on zlib-ng, whose deflate stream may move with where its
  input was cut, where any member's text or header field does
  (`cases.package_differences`), and the zlib the run linked is recorded.
* RECORDED: the seconds and the peak resident memory of a fresh process
  that writes a twin of 20,000 and of 100,000 rows of fifty columns (a
  real twin of the seeded wide table, its rows repeated), through
  `sheetwriting.workbook_stream` and `writing.write_workbook_file`: the
  seconds making the package's parts (the cells' classes and formats,
  and the sheet's first pass), the seconds writing it (the second pass
  and the zip), and the peak resident memory before the parts are made
  (the twin alone), once they are made, and at the end of the write;
  on Windows, which has no `resource`, the memory is recorded as null.
  The machine's as much as the code's: recorded, never judged.

About four minutes.

    .venv/bin/python tools/measurements/kpi_workbook_stream.py --kpi
    .venv/bin/python tools/measurements/kpi_workbook_stream.py --size 20000

`--size N` measures one size in this process and prints one JSON line;
`--sheet-only N` the sheet alone, of pooled cells; `--kpi` runs each
size in a fresh process of its own, so one size's peak is not another's.
The 1,048,576-row size is the night window's
(planning-notes/work-2026-10/wave6/XW/night-1m.sh), not this driver's.
"""

import json
import pathlib
import subprocess
import sys
import tempfile
import time
import zlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import kpi_rules  # noqa: E402
import workbook_stream_cases as cases  # noqa: E402
import workbooks  # noqa: E402
from synthtwin import generation, sheetwriting, writing  # noqa: E402

# Peak resident memory is read through `resource`, which Windows has not
# (Codex's review of lane XW, item 3): there every memory value is
# recorded as null and the comparisons and seconds are measured as
# everywhere else.
try:
    import resource
except ImportError:  # Windows
    resource = None  # type: ignore[assignment]

SIZES = (20_000, 100_000)

# The larger cases beside the gate test's battery: the study books at
# 3,000 rows and the seeded wide table at 2,000, sizes b075342a's writer
# still finishes in seconds.
LARGER: "dict[str, tuple[object, str]]" = {
    "study_excel_3000": (lambda: workbooks.study_book(3000, 9, "excel"), ""),
    "study_pandas_3000": (lambda: workbooks.study_book(3000, 9, "pandas"), ""),
    "study_writexl_3000": (lambda: workbooks.study_book(3000, 9, "writexl"), ""),
    "wide_2000": (lambda: cases.wide_book(2000), ""),
}


def _peak_mb() -> "float | None":
    """This process's peak resident memory in MB (macOS counts bytes, Linux KB);
    None where `resource` is not (Windows)."""
    if resource is None:
        return None
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return round(peak / (1048576 if sys.platform == "darwin" else 1024), 1)


def one_size(n_rows: int) -> dict:
    """Write a twin of ``n_rows`` rows of fifty columns; its seconds and memory."""
    with tempfile.TemporaryDirectory() as folder:
        base = pathlib.Path(folder)
        described = cases.describe_book(base / "wide", "wide", cases.wide_book(300))
        twin = cases.stretched(generation.generate(described, 0), n_rows)
        before = _peak_mb()
        began = time.perf_counter()
        parts = sheetwriting.workbook_stream(described, twin)
        prepared = time.perf_counter()
        after_parts = _peak_mb()
        sheet = [size for name, size, _pieces in parts if name.startswith("xl/worksheets/")]
        writing.write_workbook_file(base / "twin.xlsx", parts)
        ended = time.perf_counter()
        return {
            "rows": n_rows,
            "columns": len(twin.names),
            "sheet_bytes": sheet[0],
            "file_bytes": (base / "twin.xlsx").stat().st_size,
            "seconds_parts": round(prepared - began, 2),
            "seconds_write": round(ended - prepared, 2),
            "seconds": round(ended - began, 2),
            "rss_mb_before_parts": before,
            "peak_rss_mb_after_parts": after_parts,
            "peak_rss_mb": _peak_mb(),
        }


def sheet_only(n_rows: int) -> dict:
    """The sheet alone, ``n_rows`` rows of fifty columns of pooled cells, streamed.

    The writer's own share at a size the package's per-cell classes and
    formats (one tuple a column each, the twin's cells held as Python
    objects, lane SG's) do not fit in this machine's 2 GB rule: the
    first pass and the second, written into one zip member as
    `workbook_stream` and `write_workbook_file` write the table's sheet.
    """
    arguments = cases.sheet_arguments(n_rows)
    items = arguments[14]
    before = _peak_mb()
    with tempfile.TemporaryDirectory() as folder:
        began = time.perf_counter()
        size = sheetwriting._bytes_of(sheetwriting._sheet_pieces(*arguments))
        counted = time.perf_counter()
        second = sheetwriting._places_already_taken(sheetwriting._sheet_pieces(*arguments), items)
        target = pathlib.Path(folder) / "sheet.zip"
        writing.write_workbook_file(target, [("xl/worksheets/sheet1.xml", size, second)])
        ended = time.perf_counter()
        return {
            "rows": n_rows,
            "columns": 50,
            "sheet_bytes": size,
            "file_bytes": target.stat().st_size,
            "seconds_first_pass": round(counted - began, 2),
            "seconds_write": round(ended - counted, 2),
            "rss_mb_before_sheet": before,
            "peak_rss_mb": _peak_mb(),
        }


def compared() -> "tuple[int, list[str]]":
    """(workbooks compared, the names of those whose bytes differ)."""
    differing: "list[str]" = []
    count = 0
    with tempfile.TemporaryDirectory() as folder:
        base = pathlib.Path(folder)
        for name in cases.GOLDENS:
            described, twin = cases.golden(name, base / name)
            old, new = cases.both_files(base / name / "out", described, twin)
            count += 1
            differing += [name] if cases.package_differences(old, new) else []
        every = dict(cases.BATTERY)
        every.update(LARGER)
        for name, (make, sheet) in every.items():
            described = cases.describe_book(base / name, name, make(), sheet)  # type: ignore[operator]
            twin = generation.generate(described, 0)
            old, new = cases.both_files(base / name / "out", described, twin)
            count += 1
            moved = cases.package_differences(old, new)
            differing += [name] if moved else []
            print(name, twin.n_rows, len(twin.names), "DIFFER " + ", ".join(moved) if moved else "same", flush=True)
    return count, differing


def main() -> None:
    if "--sheet-only" in sys.argv:
        print("SHEET " + json.dumps(sheet_only(int(sys.argv[sys.argv.index("--sheet-only") + 1]))), flush=True)
        return
    if "--size" in sys.argv:
        print("SIZE " + json.dumps(one_size(int(sys.argv[sys.argv.index("--size") + 1]))), flush=True)
        return
    kpi_rules.guard_this_tree()
    count, differing = compared()
    value: "dict[str, object]" = {
        "workbooks_compared": count,
        "workbooks_differing": len(differing),
        "zlib_runtime": zlib.ZLIB_RUNTIME_VERSION + (" (zlib-ng)" if cases.ZLIB_NG else ""),
    }
    for n_rows in SIZES:
        ran = subprocess.run(  # noqa: S603 -- this driver, this interpreter
            [sys.executable, str(pathlib.Path(__file__).resolve()), "--size", str(n_rows)],
            capture_output=True, text=True, check=True,
        )
        line = [one for one in ran.stdout.splitlines() if one.startswith("SIZE ")][-1]
        measured = json.loads(line[5:])
        print(measured, flush=True)
        for key in (
            "seconds_parts",
            "seconds_write",
            "seconds",
            "rss_mb_before_parts",
            "peak_rss_mb_after_parts",
            "peak_rss_mb",
            "sheet_bytes",
        ):
            value[f"{key}_{n_rows}_rows"] = measured[key]
    kpi_rules.emit("K-S4-22", value, ", ".join(differing))


if __name__ == "__main__":
    main()
