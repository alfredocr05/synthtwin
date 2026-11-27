"""K-2B-34: a spreadsheet's twin is a spreadsheet that validates, at three sizes.

Three writers' study workbooks (`tests/workbooks.py::study_book`: Excel,
pandas and writexl) at 200, 1,200 and 3,000 rows: described, generated,
and validated -- the REAL book and its TWIN both. The pinned
large-workbook test asserts the real book only, so this counts every
nonzero exit among the three commands. About five minutes.

    .venv/bin/python tools/measurements/kpi_large_workbooks.py --kpi
"""

import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import kpi_rules  # noqa: E402
import kpi_shapes  # noqa: E402
import workbooks  # noqa: E402

kpi_rules.guard_this_tree()
nonzero = []
runs = 0
with tempfile.TemporaryDirectory() as folder:
    base = pathlib.Path(folder)
    for shape in ("excel", "pandas", "writexl"):
        for rows, seed in ((200, 0), (1200, 5), (3000, 9)):
            here = base / f"{shape}-{rows}"
            here.mkdir()
            book = here / f"{shape}.xlsx"
            book.write_bytes(workbooks.study_book(rows, seed, shape))
            assert kpi_shapes.quiet_cli(["profile", str(book), "--out-dir", str(here)]) == 0
            description = here / f"{shape}-profile.json"
            exits = {"generate": kpi_shapes.quiet_cli(
                ["generate", str(description), "--out-dir", str(here), "--seed", str(seed)])}
            for side, checked in (("real", book), ("twin", here / f"{shape}-twin.xlsx")):
                report = here / side
                report.mkdir()
                exits[side] = kpi_shapes.quiet_cli(
                    ["validate", str(description), "--twin", str(checked), "--out-dir", str(report)])
            runs += 1
            print(shape, rows, exits, flush=True)
            nonzero += [f"{shape} {rows} {k}={v}" for k, v in exits.items() if v != 0]
kpi_rules.emit("K-2B-34", {"nonzero_exits": len(nonzero), "books": runs}, "; ".join(nonzero))
