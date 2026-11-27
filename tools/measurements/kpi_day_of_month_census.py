"""K-S3-44: what the day-of-month pass costs a large table.

LANDING 3b.3 (plan P4-D368). A column of dates whose day of the month
departs publishes its day-of-month census beside its weekday census, and
the twin meets both by the joint day plan (method G7.3i): pass A over the
census's thirty-four bins, then pass B over the weekday census keeping
each rank's day-of-month group. The 3b.3 skeptic's minor 1 measured the
pass growing near n^1.5, so it is held at 40,000 rows with a budget.

K-S3-44, at 40,000 rows, a floor of eleven and seed 0, over seven date
columns each publishing its day-of-month census -- the gate's billing on
the 1st and 15th and births over seventy years, and the design's month
ends, last business days, business billing, visits on the 10th rolled to
Monday and births with a weekend dip:

* `censuses`: the columns that publish a day-of-month census;
* `missed`: obligations MISSED on the twin;
* `pass_share_percent`: the joint day plan's seconds -- `_day_settled`
  timed on each column publishing a census -- as a whole per cent of the
  whole generation's seconds, so at most fifty means the pass costs no
  more than the rest of generation; a share, so a loaded machine slows
  both sides of it alike;
* `pass_seconds`, `generate_seconds`: recorded, never judged.

    .venv/bin/python tools/measurements/kpi_day_of_month_census.py --kpi
"""

import pathlib
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT))
import kpi_rules  # noqa: E402
import kpi_shapes  # noqa: E402
import test_stage3b_day_of_month as lane  # noqa: E402
import test_stage3b_gate as gate  # noqa: E402

from synthtwin import generation  # noqa: E402

kpi_rules.guard_this_tree()

ROWS = 40000
SEED = 0


def measure(home: pathlib.Path) -> "tuple[dict[str, int], str]":
    columns = dict(gate._BATTERY["heaps"](ROWS))
    columns.update(lane._monthend(ROWS))
    described = kpi_shapes.describe(home, "large", lane._text(columns), 11)
    censuses = [name for name in columns if described.block(name)["day_of_month_census"]]
    spent = [0.0]
    settled = generation._day_settled

    def timed(column, facts, *rest, **named):  # type: ignore[no-untyped-def]
        started = time.perf_counter()
        answer = settled(column, facts, *rest, **named)
        if facts.day_of_month_census:
            spent[0] += time.perf_counter() - started
        return answer

    generation._day_settled = timed
    try:
        started = time.perf_counter()
        written = kpi_shapes.twin_text(described, SEED)
        total = time.perf_counter() - started
    finally:
        generation._day_settled = settled
    missed = kpi_shapes.missed(kpi_shapes.measure(described, written, "twin.csv"))
    value = {
        "censuses": len(censuses),
        "missed": len(missed),
        "pass_share_percent": int(round(100 * spent[0] / total)) if total > 0 else 0,
        "pass_seconds": int(round(spent[0])),
        "generate_seconds": int(round(total)),
    }
    detail = (
        f"{len(censuses)} of {len(columns)} columns publish; the pass {spent[0]:.1f} s of "
        f"{total:.1f} s generating; " + ("; ".join(missed) if missed else "nothing missed")
    )
    return value, detail


def main() -> int:
    with tempfile.TemporaryDirectory() as folder:
        value, detail = measure(pathlib.Path(folder))
        kpi_rules.emit("K-S3-44", value, detail)
    return 0


if __name__ == "__main__":
    if "--kpi" not in sys.argv[1:]:
        print(__doc__)
    sys.exit(main())
