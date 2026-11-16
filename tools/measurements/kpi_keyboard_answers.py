"""K-HZ-31: every question at the keyboard, and the keyboard is the file (lane EZ-a, plan P4-D479).

On 14 invented tables of 20,000 rows (`tests/keyboard_answers_measures.py`,
`k_hz_31`): the walkthrough's look-alike and its variants with a visit
number and with a clinician number, hospital stays, laboratory results and
nine of the health zoo's kinds. Each: the questions file answered round by
round as the person who holds the table answers it; the same answers typed
at the keyboard as the keys the screen shows, through `cli._asked`, so the
real reader reads them; the same answers written as plain-text lines
`column = answer`, the column named exactly; and the repeat lines the
answered runs printed (the file route's last and the keyboard's), run as
typed, each required to be printed and to finish. A last part reads the
laboratory table's later round: every printed number must be the file's,
and a text line written with it must be refused (lane EZ-a's second repair:
Codex's items 2, 3 and 8, the verify's MINOR 5). About an hour on the
reference machine under load; each table's own figures ride in the detail
the run's report keeps.

    .venv/bin/python tools/measurements/kpi_keyboard_answers.py --kpi
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
    figures = json.dumps(value.get("per_table"), sort_keys=True, separators=(",", ":"))
    return {one: value[one] for one in value if one != "per_table"}, figures


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="kpi-keyboard-") as made:
        value, figures = _slim(measures.k_hz_31(pathlib.Path(made)))
        kpi_rules.emit("K-HZ-31", value, f"every question at the keyboard and the keyboard equal to the file, at 20,000 rows; each table: {figures}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
