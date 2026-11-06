"""K-2B-05: verdicts the twin's report and the quality report disagree on.

Runs `r_p4_61_window_agreement.py` unchanged and reads its printed
totals back: how many rung and moment verdicts one report calls inside
while the other calls MISSED (OPEN: 4 of 1,128 on the frozen copy,
target 0), with the windows whose printed ends differ beside it. About
ninety seconds on the reference machine.

    .venv/bin/python tools/measurements/kpi_window_flips.py --kpi
"""

import contextlib
import importlib.util
import io
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import kpi_rules  # noqa: E402

kpi_rules.guard_this_tree()
spec = importlib.util.spec_from_file_location(
    "r_p4_61_window_agreement", ROOT / "tools" / "measurements" / "r_p4_61_window_agreement.py"
)
agreement = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agreement)
printed = io.StringIO()
with contextlib.redirect_stdout(printed):
    agreement.main()
text = printed.getvalue()
print(text)
flips = int(re.search(r"inside and the other MISSED: (\d+)", text).group(1))
verdicts = int(re.search(r"verdicts compared: (\d+)", text).group(1))
differ = int(re.search(r"whose printed ends differ: (\d+)", text).group(1))
kpi_rules.emit("K-2B-05", {"flips": flips, "verdicts": verdicts, "windows_differ": differ})
