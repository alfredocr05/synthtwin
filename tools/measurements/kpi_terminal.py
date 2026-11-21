"""K-S8-01 and K-S8-03: one command for the whole journey (lane TT, plan P4-D460).

Runs `tests/test_terminal_twin.py`'s journey once, through
`synthtwin.cli.run` with a screen that records, on the stage-5 battery's
Step 0 table at the table floor of 20,000 rows: a `synthtwin twin` whose
reader ends input at the first question, the same answered on screen,
again without and with `--replace`, then profile, generate and validate
each again without and with `--replace`, and the same table with Enter
pressed at its question, then again with `--replace` (lane TT's repair);
and on the held table, a twin with nobody at the keyboard beside the
three commands run apart. It reads both KPIs off that one pass with that
file's own measures:

- `K-S8-01`: from a folder holding only the table to a validated twin,
  the install commands of README's install block (lane TI's count), the
  command lines the journey typed and the files it edited by hand.
- `K-S8-03`: the files a twin stopped at its first question left, the
  questions a second run in the folder put (after answers typed by
  number, and after Enter at every question), the commands that keep the
  one overwrite rule, and the held table's twin against the three
  commands run apart (measured here alone, not in the gate).

About three minutes on the reference machine.

    .venv/bin/python tools/measurements/kpi_terminal.py --kpi
"""

import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import kpi_rules  # noqa: E402

kpi_rules.guard_this_tree()
import test_terminal_twin as twin  # noqa: E402


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="kpi-terminal-") as made:
        root = pathlib.Path(made)
        kpi_rules.emit(
            "K-S8-01",
            twin.journey_measures(root),
            "commands typed and files edited from a folder holding a battery table to a validated twin",
        )
        # ...and, measured here alone (the orchestrator's LANE TT RULINGS 2
        # (7)(b): the gate files are judged by CPU seconds), the held
        # table's twin against the three commands run apart.
        rule = twin.rule_measures(root)
        apart = twin.apart_measures(root)
        rule["questions_put_on_a_second_run"] = (
            rule["questions_put_on_a_second_run"] + apart["questions_put_on_a_second_run"]
        )
        rule["twin_other_than_the_three_commands_apart"] = apart["twin_other_than_the_three_commands_apart"]
        kpi_rules.emit(
            "K-S8-03",
            rule,
            "no file before the answers, a second run that asks nothing, one overwrite rule, the twin the three commands' own",
        )
    return 0


if __name__ == "__main__":
    if "--kpi" not in sys.argv[1:]:
        print(__doc__)
        sys.exit(0)
    sys.exit(main())
