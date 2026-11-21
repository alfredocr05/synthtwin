"""K-HZ-32: people counted by the column said to name them (lane EZ-a, plan P4-D479).

Six local shapes of 20,000 rows, invented in
`tests/keyboard_answers_measures.py` (`k_hz_32`): 1,000 patients beside a
clinician, an encounter, a second numbering of the patient and a mother,
and 20,000 patients one row each beside a clinician, each said with
`--person`, at the subject question at the keyboard and scripted with two
`--identifier`, and `--person X` alone compared with `--identifier X`
alone; a visit key different on every row said beside the patient key; and
a control at a floor of 5. The people key reads the product's own count
beside the column it names, and every label column of the source is read
for its levels whatever role the description gave it. No zoo kind is read
and no zoo comparison is made (lane EZ-a's second repair: Codex's items 9
and 11). About ten minutes on the reference machine under load.

    .venv/bin/python tools/measurements/kpi_people_said.py --kpi
"""

import json
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import kpi_rules  # noqa: E402

kpi_rules.guard_this_tree()
import keyboard_answers_measures as measures  # noqa: E402


def _slim(value: "dict[str, object]") -> "tuple[dict[str, object], str]":
    """The value the ledger keeps, and each table's own figures for the detail beside it.

    `kpi_run` keeps a driver's KPI line alone, so the figures travel in its
    detail, which the run's report keeps.
    """
    figures = json.dumps(value.get("per_run"), sort_keys=True, separators=(",", ":"))
    return {one: value[one] for one in value if one != "per_run"}, figures


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="kpi-people-said-") as made:
        value, figures = _slim(measures.k_hz_32(pathlib.Path(made)))
        kpi_rules.emit("K-HZ-32", value, f"people counted by the column said to name them, at 20,000 rows and 1,000 people; each table: {figures}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
