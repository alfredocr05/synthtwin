"""K-S5-01 and K-S5-02: results become data, every byte held (plan P4-D395; lane S5a, plan P4-D437).

Runs the whole golden battery of `tests/stage5_battery.py` once, through
`synthtwin.cli.run` with a screen that records, at the table floor of
20,000 rows -- every recorded case, the every-role run G5 included, then
the cases `K-S5-01` alone runs (a reader that ends input, two injected
faults, three memory readings of doctor, and a floor of 5 carried
through the internal setting) -- and reads both KPIs off that one pass
with `tests/test_stage5_gate.py`'s own checker and comparison:

- `K-S5-01`: the cases that name a class, those whose result meets
  every clause (a) to (i) the page writes, and the correct results
  corrupted one field at a time that the checker met (each must be
  unmet).
- `K-S5-02`: the records compared with `tests/stage5_goldens.py` and
  those skipped on this platform, the records that differ and the
  cases holding them, and the goldens' three digests that differ from
  the ones computed again.

About six minutes on the reference machine, five of them G5's.

    .venv/bin/python tools/measurements/kpi_stage5.py --kpi
"""

import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import kpi_rules  # noqa: E402

kpi_rules.guard_this_tree()
import test_stage5_gate as gate  # noqa: E402


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="kpi-stage5-") as made:
        ran = gate.run_battery(pathlib.Path(made), slow=True)
        values = gate.kpi_values(ran)
    kpi_rules.emit(
        "K-S5-01",
        values["K-S5-01"],
        "cases of the golden battery that name a class, met from the result alone",
    )
    kpi_rules.emit(
        "K-S5-02",
        values["K-S5-02"],
        "records of the golden battery against tests/stage5_goldens.py",
    )
    return 0


if __name__ == "__main__":
    if "--kpi" not in sys.argv[1:]:
        print(__doc__)
        sys.exit(0)
    sys.exit(main())
