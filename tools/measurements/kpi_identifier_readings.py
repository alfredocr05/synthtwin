"""K-HZ-22: record numbers beside labels, names joined to record numbers and one-word codes, per item and layout (plan P4-D469).

THE ITEMS (`tests/labelled_records.py`, lane CZ-A2): each an invented
look-alike, one column `record_label` of 20,000 rows, 1,000 people of 20
rows, nothing declared or answered first -- a record number after a sign before
its label (`#MR1000013`, `* MR1000013`, `@mr1000013`), joined to its label
by a point or a space, closed by a check letter, after a number sign alone,
signed on one row in twenty, of twelve figures; a family name, a given name
and a record number joined by commas, one a row and one a person, with
spaces after the commas, by semicolons, the number first, three parts of
the name; and one-word record numbers glued to their label, bare and
dashed. Through the real profile (nobody at the keyboard), generate (seed
0) and validate, the owner's table floor on.

AND THE ITEMS OF LANE CZ-A2'S REPAIR 1 (its skeptic's items 1 to 4): labels
after spaces and a mark or in brackets, one a row and one a person; the
labels route two of the person rule reads one a person; names joined to a
record number with an empty part, the number first with empty parts after
the names, an underscore, five figures, a flag after the number, small
letters, one a row and one a person; and a declared column of two layouts
whose runs share a width (`#MR` and seven figures beside `#9` and six),
the one item profiled with its column declared an identifier.

THE VALUE, summed over the items, each also named per item in the lines:
`real_values_shown` (a real value of the column whole in the description,
its summary, the questions file, the screen or the twin's report and
quality files; the linear counter of `unanswered_identifier_shapes.
count_real`), `real_twin_cells` (twin cells equal to a real cell),
`complete_runs_in_wider_cells` (twin cells holding a complete real run of
five figures or more inside a wider cell, not equal to a real cell;
`labelled_records.complete_runs`, the real runs in a set and each
different twin cell read once), `questions_not_put` (an item put no
question offering `identifier` and no Safe Harbor question, and not read
as free text, which publishes nothing and writes no real value), and the
same three counts once each item's questions are answered as the column
truly is, round by round (`answered_real_values_shown`,
`answered_real_twin_cells`, `answered_complete_runs_in_wider_cells`), and
`items_failing` (an item with any of those, or a profile or a generate
that did not exit 0 in either round; validate's exit is printed beside, a
miss of fidelity, as K-HZ-14 prints it); target 0 each. RECORDED, never
failing: `read_as_free_text` (the items read as free text, told apart from
a question put), `items_written_as_stand_ins` (items whose twin writes
fewer than half its cells in a real cell's pattern, each item's share
printed: a held value no layout describes is written as stand-ins), and
`false_alarms` and `false_alarms_asked` (the shapes `labelled_records.
FALSE_ALARMS` names -- labelled codes, rooms, lots and charges, a
measurement beside a label and a unit, a dose beside its unit, codes of
few figures, shared nine-figure codes -- and how many were put a question
offering `identifier`, each one's role and question printed). The
product's own seconds (profile, generate, validate) are printed per item
apart from the counting.

    .venv/bin/python tools/measurements/kpi_identifier_readings.py --kpi
    .venv/bin/python tools/measurements/kpi_identifier_readings.py --only 'sign_*'
"""

import argparse
import fnmatch
import pathlib
import shutil
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import kpi_rules  # noqa: E402

kpi_rules.guard_this_tree()

import labelled_records as records  # noqa: E402

SUMS = ("real_values_shown", "real_twin_cells", "complete_runs_in_wider_cells", "questions_not_put")
ANSWERED = ("real_values_shown", "real_twin_cells", "complete_runs_in_wider_cells")
# Below this share of its twin cells in a real cell's pattern an item is
# counted as written in stand-ins (recorded).
IN_PATTERN_AT_LEAST = 0.5


def _seconds(seen: "dict[str, object]") -> float:
    spent = seen["seconds"]
    return float(sum(spent.values()))  # type: ignore[attr-defined]


def main(argv: "list[str]") -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--kpi", action="store_true", help="print the KPI line for kpi_run")
    parser.add_argument("--only", action="append", default=[], help="a shell pattern over the item names")
    chosen = parser.parse_args(argv)
    value: "dict[str, int]" = {"items": 0, "items_failing": 0}
    for key in SUMS:
        value[key] = 0
    for key in ANSWERED:
        value["answered_" + key] = 0
    value.update({"read_as_free_text": 0, "items_written_as_stand_ins": 0, "false_alarms": 0, "false_alarms_asked": 0})
    product = 0.0
    with tempfile.TemporaryDirectory() as scratch:
        for item in list(records.ITEMS) + list(records.FALSE_ALARMS):
            if chosen.only and not any(fnmatch.fnmatch(item, one) for one in chosen.only):
                continue
            folder = pathlib.Path(scratch) / item
            started = time.process_time()
            alarm = item in records.FALSE_ALARMS
            seen = records.measure(folder, item, answered=not alarm)
            took = time.process_time() - started
            spent = _seconds(seen)
            if alarm:
                value["false_alarms"] += 1
                asked = any("identifier" in one or one == ["no", "yes"] for one in seen["asked"])  # type: ignore[attr-defined]
                value["false_alarms_asked"] += 1 if asked else 0
                product += spent
                print(f"{item} (false alarm, recorded): role={seen['role']} asked {seen['asked']} exits {seen['exits']} "
                      f"seconds {seen['seconds']}", flush=True)
                shutil.rmtree(folder, ignore_errors=True)
                continue
            counts = {
                "real_values_shown": int(seen["real_values_shown"]),  # type: ignore[call-overload]
                "real_twin_cells": int(seen["real_twin_cells"]),  # type: ignore[call-overload]
                "complete_runs_in_wider_cells": int(seen["complete_runs_in_wider_cells"]),  # type: ignore[call-overload]
                "questions_not_put": 0 if seen["question_put"] or seen["read_as_free_text"] else 1,
            }
            later = seen["answered"]
            answered = {key: int(later[key]) for key in ANSWERED}  # type: ignore[index, call-overload]
            # ...a step that did not write its file fails the item, as K-HZ-14 judges; validate's exit is
            # printed beside it (a miss of fidelity, not of privacy).
            failing = (
                tuple(seen["exits"])[:2] != (0, 0)  # type: ignore[index]
                or (later["rounds"] and tuple(later["exits"])[:2] != (0, 0))  # type: ignore[index]
                or any(counts.values())
                or any(answered.values())
            )
            value["items"] += 1
            value["items_failing"] += 1 if failing else 0
            for key in SUMS:
                value[key] += counts[key]
            for key in ANSWERED:
                value["answered_" + key] += answered[key]
            value["read_as_free_text"] += 1 if seen["read_as_free_text"] else 0
            share = float(seen["twin_in_a_real_pattern"])  # type: ignore[arg-type]
            value["items_written_as_stand_ins"] += 1 if share < IN_PATTERN_AT_LEAST else 0
            product += spent + _seconds(later)  # type: ignore[arg-type]
            print(
                f"{item} (class {seen['class']}): {'FAIL' if failing else 'PASS'} role={seen['role']} "
                + " ".join(f"{key}={counts[key]}" for key in SUMS)
                + f" exits {seen['exits']} asked {seen['asked']}"
                + (" (read as free text)" if seen["read_as_free_text"] else "")
                + f" twin_in_a_real_pattern={share} seconds {seen['seconds']}; answered in {later['rounds']} rounds: "  # type: ignore[index]
                + " ".join(f"{key}={answered[key]}" for key in ANSWERED)
                + f" role={later['role']} exits {later['exits']} seconds {later['seconds']}"  # type: ignore[index]
                + f", counting {took - spent - _seconds(later):.1f}",  # type: ignore[arg-type]
                flush=True,
            )
            shutil.rmtree(folder, ignore_errors=True)
    detail = (
        f"{value['items']} items at {records.ROWS:,} rows, unanswered and answered, {value['items_failing']} failing; "
        f"{value['read_as_free_text']} read as free text, {value['items_written_as_stand_ins']} written as stand-ins; "
        f"false alarms {value['false_alarms']} shapes, {value['false_alarms_asked']} asked; "
        f"the product's own CPU seconds {product:.0f}"
    )
    print(detail)
    if not value["items"] and not value["false_alarms"]:
        print(f"no item matches {chosen.only}: nothing was measured")
        return 1
    if chosen.kpi and not chosen.only:
        kpi_rules.emit("K-HZ-22", value, detail)
    return 1 if value["items_failing"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
