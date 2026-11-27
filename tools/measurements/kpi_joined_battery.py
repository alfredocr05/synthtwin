"""K-P4-06 and K-P4-08: the joined-number battery, read off the L7 driver.

Runs `r_p4_40_l7_joined.py`'s own battery of three- and four-position
columns and its count of different numbers over forty seeds, unchanged,
and reads their printed totals back as two ledger values:

- K-P4-06: pair agreements outside the 0.02 window, and rows-above
  counts missed, over every pair of the battery (OPEN: 597 and 7 on
  e53d5f4, 609 and 3 on the integrated tree of 2026-09-19, where
  G6.5a's push traded twelve agreements for four above-counts, against
  a target of 550 and 0);
- K-P4-08: runs whose count of different numbers is not met exactly.

Nothing is re-implemented here, so the ledger's number and the L7
driver's printed number cannot drift apart. About four and a half
minutes on the reference machine.

    .venv/bin/python tools/measurements/kpi_joined_battery.py --kpi
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
    "r_p4_40_l7_joined", ROOT / "tools" / "measurements" / "r_p4_40_l7_joined.py"
)
joined = importlib.util.module_from_spec(spec)
spec.loader.exec_module(joined)

printed = io.StringIO()
with contextlib.redirect_stdout(printed):
    joined.battery()
    joined.value_counts()
text = printed.getvalue()
print(text)
outside = re.search(r"agreements outside the 0\.02 window: (\d+) of (\d+)", text)
above = re.search(r"above-counts missed: (\d+) of (\d+)", text)
met = re.search(r"met exactly: (\d+) of (\d+) runs", text)
kpi_rules.emit(
    "K-P4-06",
    {"agreements_outside": int(outside.group(1)), "above_counts_missed": int(above.group(1)),
     "pairs": int(outside.group(2))},
)
kpi_rules.emit(
    "K-P4-08",
    {"n_distinct_values_short_runs": int(met.group(2)) - int(met.group(1)),
     "runs": int(met.group(2))},
)
