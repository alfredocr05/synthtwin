"""K-HZ-16: Safe Harbor dates in disguise, per form, at 600 and 20,000 rows (lane CZ-H, plan P4-D446).

The five invented forms of `tests/dates_in_disguise.py` -- typed day
numbers (a wide table with a three-part key, and the same columns on one
row a record), key-value answers, values typed by the key, dates as
results, and paired clocks -- each at 600 rows (the library, below the
owner's table floor) and 20,000 rows (the shipped floor), unanswered and
answered as the zoo answers (`health_zoo.answer_generally`, every round),
through profile, generate and validate. Counted by the forms' LINEAR
COUNTER (`dates_in_disguise.count_shown` and `count_twin`: the real
dates in a set once; each published text, screen line and twin cell
read once through its own tokens, every spelling's decoder over the whole
of every file). PER FORM, `<table>` one of the six:

* `clock_text_shown_<state>_<rows>`, `clock_text_twin_<state>_<rows>`: form
  3's clock key's real texts shown and written, recorded apart and no date:
  a time of day alone names none (the orchestrator's LANE CZ-H RULINGS 3 (2)).
* `shown_<table>_<state>_<rows>`: real date elements finer than the year
  shown in any file the run wrote or on screen, in the column's own forms
  or as date text; forms 1 to 4; target 0. On the day-number tables
  answered as dates, `answered_span_ends_finer_than_year_<table>_<rows>`
  counts the ISO dates their `time_grain` publishes apart, and
  `answered_span_ends_fewest_people_<table>_<rows>` the fewest people
  holding the month one names: what the answer publishes.
* `dates_held_few_<state>_<rows>`: the paired clocks, read as dates by
  their shape: the dates one to ten people hold printed (K-HZ-07's
  counter, `dates_held.dates_held_few`), target 0. The months and days
  eleven people or more hold are published, under P4-D433.
* `twin_<table>_<state>_<rows>`: twin cells carrying a real date, as
  written or decoded, in forms 1 to 4's disguised columns; target 0,
  answered day numbers apart (below).
* `not_asked_<table>_<rows>`: disguised columns of forms 1 to 4 put no date
  question in any round (Q3 offering a counting system, or the Safe
  Harbor question about dates among other values); target 0. Unanswered a
  key-value column is put its identity question alone, the date question
  following its answer (LANE SH ADDENDUM 7), and is held meanwhile.
* `misses_<table>_<state>_<rows>`: the checks validate missed, recorded
  (named in the detail; RULINGS 1 (3)).
* `case_<name>_shown`, `case_<name>_twin`, `case_<name>_not_asked`: each
  attack of `dates_in_disguise.CASES` at 20,000 rows, answered (or not, as
  the case says); target 0. The second repair's attacks (spellings read at
  a cell's head, dates as text on most of a column, `no` to the age or
  ZIP question, ages beside an admission day) add
  `case_<name>_not_held`, their disguised columns whose description does
  not hold their dates (NF135): target 0, but where an open question
  holds the column whole, recorded.
* `charges_*` (the verify's item 4: charges a third of which lie in the
  day band, unanswered) and `marker_*` (Codex's item 2: readings beside a
  declared nine-figure missing marker, answered), each at 20,000 rows:
  the twin's cells in a band (exact 0), validate's misses (recorded, each
  named with its owner in P4-D446), the marker's missing count as the
  description records it, the remark NF135 on its column (exact 0) and
  the twin's marker cells.
* `stages_failed`: every stage of every run above that did not finish --
  profile, the answers, generate (exit 0), validate (exit 0, or 3 with its
  report), each chance seed's generate -- named in the detail; target 0.
  A run with a failed stage records no other key, so its keys read "not
  measured" and never 0 (Codex's review of the first repair, item 3).
* THE CHANCE of the answered day numbers' cells on a real day
  (`chance_real_*`, `chance_unrelated_*`): at three twin seeds, those cells
  against the table described and against an unrelated draw of it, whose
  days the twin can know nothing of. A count above chance is a finding.
* RECORDED, each a stated limit with its owner in P4-D446:
  `answered_days_outside_span_<rows>`, form 1's twin cells, answered as
  days since 1840, outside the real span of years (the whole column held
  in people, its stand-ins written past 2086; owner HB2);
  `key_repeats_<state>_<rows>`, the three-part key's repeated rows on
  that twin; `clock_rows_entered_early_<rows>`, paired clocks' twin rows
  entered more than a minute before they were recorded (a relation
  between two columns; owner RO, K-S6-06); `written_wider_<state>_<rows>`,
  the held day columns' cells longer than any real cell (method G9.6b).
* THE PRICE over the WHOLE catalogue but the forms, workbooks too, at
  20,000 rows (`dates_in_disguise.zoo_price`): `price_dated_columns`,
  columns put the Safe Harbor question about values that read as dates;
  `price_dated_columns_answered`, those still held once the zoo has
  answered; `price_q3_new`, columns newly put Q3 by the contact rule, each
  named in the detail with its cells; `price_q3_lost` must be 0. Over the
  batteries (`dates_in_disguise.battery_price`):
  `price_battery_columns` of `battery_columns`, by name. Over forms 2 to 4,
  `values_held_<table>_<rows>`, the cells the rule reads as blank, and
  `price_values_not_dates_<table>_<rows>`, those whose key holds no date.

About two and a half hours on the reference machine, loaded.
`KHZ16_ONLY`, where set, runs the parts it names alone, comma-separated
(`forms`, `form:<table>:<rows>`, `case:<name>`, `charges`, `marker`,
`price`, `battery`), for a re-measure of the keys a change touches.

    .venv/bin/python tools/measurements/kpi_dates_in_disguise.py --kpi
"""

import os
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
import dates_in_disguise as forms  # noqa: E402

SIZES = (600, 20000)
STATES = (("unanswered", False), ("answered", True))
DAY_TABLES = ("day_numbers", "day_numbers_flat")
CHANCE_SEEDS = (0, 1, 2)


def _analyst(result: "dict[str, object]", words: str) -> int:
    """The twin's bad cells an analyst check whose name holds `words` counted."""
    total = 0
    for failure in result.get("analyst", []):  # type: ignore[attr-defined]
        if words in f"{failure[1]}":
            said = f"{failure[2]}".split(" ")[0]
            total += int(said) if said.isdigit() else 0
    return total


_shown = forms.run_counts


def _add(value: "dict[str, object]", key: str, by: int) -> None:
    value[key] = int(f"{value.get(key, 0)}") + by


def _wanted(part: str) -> bool:
    """Whether `KHZ16_ONLY` names this part, or names nothing: every part runs."""
    named = [one.strip() for one in os.environ.get("KHZ16_ONLY", "").split(",") if one.strip()]
    if not named:
        return True
    return part in named or (part.startswith("form:") and "forms" in named)


def _failed(value: "dict[str, object]", failures: "list[str]", run: str, failed: "list[str]") -> bool:
    """Count a run's failed stages in `stages_failed` and name them; whether any failed (its keys are then not written)."""
    _add(value, "stages_failed", len(failed))
    failures += [f"{run}: {stage}" for stage in failed]
    return bool(failed)


def column_values(part: str, found: "dict[str, object]") -> "dict[str, object]":
    """A one-column case's keys: its twin's cells in a band, validate's misses, and for the marker its missing count."""
    from synthtwin import date_counts, taxonomy

    twin = found.get("twin", [])
    block = found.get("block", {})
    values: "dict[str, object]" = {f"{part}_misses": len(found.get("missed", []))}  # type: ignore[arg-type]
    if part == "charges":
        values["charges_twin_in_band"] = sum(1 for cell in twin if date_counts.counted_figures(cell))  # type: ignore[attr-defined]
    if part == "marker":
        missing = block.get("missing_by_source", {})  # type: ignore[attr-defined]
        values["marker_missing_by_source"] = int(missing.get(forms.MISSING_MARKER, 0))
        values["marker_dated_remark"] = int(taxonomy.rendered(taxonomy.REMARK_DATED_VALUES_HELD, ()) in block.get("remarks", []))  # type: ignore[attr-defined]
        values["marker_twin_cells"] = sum(1 for cell in twin if cell == forms.MISSING_MARKER)  # type: ignore[attr-defined]
    return values


def main() -> None:
    value: "dict[str, object]" = {}
    lines: "list[str]" = []
    named: "dict[str, list[str]]" = {}
    failures: "list[str]" = []
    started = time.perf_counter()
    with tempfile.TemporaryDirectory() as scratch_name:
        scratch = pathlib.Path(scratch_name)
        for rows in SIZES:
            for table in forms.TABLES:
                if not _wanted(f"form:{table.name}:{rows}"):
                    continue
                if table.name != "paired_clocks":
                    held, not_dates = forms.values_held_not_dates(table, rows)
                    value[f"values_held_{table.name}_{rows}"] = held
                    value[f"price_values_not_dates_{table.name}_{rows}"] = not_dates
                for state, answered in STATES:
                    folder = scratch / f"{table.name}-{rows}-{state}"
                    began = time.perf_counter()
                    day_table = table.name in DAY_TABLES
                    result = forms.run_form(
                        table, folder, rows, answered,
                        twin_seeds=CHANCE_SEEDS if day_table and answered and rows == 20000 else (),
                    )
                    chance_failed = [
                        f"chance seed {seed}" for seed, counted in result.get("chance", {}).items()  # type: ignore[attr-defined]
                        if counted["exit"] != 0
                    ]
                    if _failed(value, failures, f"{table.name} {rows} {state}", result["failed"] + chance_failed):  # type: ignore[operator]
                        shutil.rmtree(folder, ignore_errors=True)
                        continue
                    value[f"misses_{table.name}_{state}_{rows}"] = len(result.get("missed", []))  # type: ignore[arg-type]
                    named[f"misses {table.name} {state} {rows}"] = result.get("missed", [])  # type: ignore[assignment]
                    if table.name == "paired_clocks":
                        value[f"dates_held_few_{state}_{rows}"] = int(result["dates_held"]["few"])  # type: ignore[index]
                        if answered:
                            _add(value, f"clock_rows_entered_early_{rows}", _analyst(result, "more than a minute before"))
                    else:
                        if table.name == "flow_values":
                            value[f"clock_text_shown_{state}_{rows}"] = int(result["shown"]["result_value"]["clocks"])  # type: ignore[index]
                            value[f"clock_text_twin_{state}_{rows}"] = int(result.get("twin", {})["result_value"]["clock_cells"])  # type: ignore[attr-defined]
                        shown, twin, not_asked = _shown(result, day_table and answered)
                        value[f"shown_{table.name}_{state}_{rows}"] = shown
                        value[f"twin_{table.name}_{state}_{rows}"] = twin
                        if answered:
                            value[f"not_asked_{table.name}_{rows}"] = not_asked
                        if day_table:
                            entries = result["shown"].values()  # type: ignore[attr-defined]
                            _add(value, f"elsewhere_bare_{state}_{rows}", sum(int(one["elsewhere_bare"]) for one in entries))
                            _add(value, f"written_wider_{state}_{rows}", sum(result.get("wider_cells", {}).values()))  # type: ignore[attr-defined]
                            _add(value, f"key_repeats_{state}_{rows}", _analyst(result, "three-part key"))
                            if answered:
                                _add(value, f"answered_days_outside_span_{rows}", _analyst(result, "fall in the real span"))
                                value[f"answered_span_ends_finer_than_year_{table.name}_{rows}"] = sum(int(one["finer"]) for one in entries)
                                value[f"answered_span_ends_fewest_people_{table.name}_{rows}"] = min(
                                    (int(one["finer_fewest"]) for one in entries if int(one["finer"])), default=0,
                                )
                    for seed, counted in result.get("chance", {}).items():  # type: ignore[attr-defined]
                        value[f"chance_real_{table.name}_seed_{seed}"] = counted["real"]
                        value[f"chance_unrelated_{table.name}_seed_{seed}"] = counted["unrelated"]
                        value[f"chance_written_{table.name}_seed_{seed}"] = counted["written"]
                    lines += [
                        f"{table.name} {rows} {state}: steps {result['steps']}, roles {result['roles']}, given {result['given']}, "
                        f"shown {result['shown']}, twin {result.get('twin')}, wider {result.get('wider_cells')}, "
                        f"chance {result.get('chance')}, missed {result.get('missed')}, "
                        f"{round(time.perf_counter() - began, 1)} s"
                    ]
                    print(lines[-1], flush=True)
                    shutil.rmtree(folder, ignore_errors=True)
        for place, case in enumerate(forms.CASES):
            if not _wanted(f"case:{case.name}"):
                continue
            folder = scratch / case.name
            began = time.perf_counter()
            result = forms.run_form(
                case.table, folder, 20000, case.answered, disguised=case.disguised,
                dates_answer=case.dates_answer, extra=case.extra,
            )
            _failed(value, failures, f"case {case.name}", result["failed"])  # type: ignore[arg-type]
            value.update(forms.case_values(case.name, result, place >= forms.FIRST_REPAIR_CASES))
            lines += [
                f"case {case.name}: steps {result['steps']}, roles {result['roles']}, given {result['given']}, "
                f"shown {result['shown']}, twin {result.get('twin')}, missed {result.get('missed')}, "
                f"{round(time.perf_counter() - began, 1)} s"
            ]
            print(lines[-1], flush=True)
            shutil.rmtree(folder, ignore_errors=True)
        for part, table, column, extra, answered in (
            ("charges", forms.CHARGES_TABLE, "charge_amount", (), False),
            ("marker", forms.MARKER_TABLE, "reading_value", ("--missing-value", forms.MISSING_MARKER), True),
        ):
            if not _wanted(part):
                continue
            began = time.perf_counter()
            # The marker's: its identity question answered, any question about
            # dates left open, where the first repair blanked the markers.
            found = forms.column_run(table, scratch / part, 20000, column, extra, answered, "" if answered else None)
            if not _failed(value, failures, part, found["failed"]):  # type: ignore[arg-type]
                value.update(column_values(part, found))
            named[f"misses {part}"] = found.get("missed", [])  # type: ignore[assignment]
            lines += [f"{part}: steps {found['steps']}, missed {found.get('missed')}, {round(time.perf_counter() - began, 1)} s"]
            print(lines[-1], flush=True)
            shutil.rmtree(scratch / part, ignore_errors=True)
        price = forms.zoo_price(scratch / "price", 20000) if _wanted("price") else None
        battery = forms.battery_price(scratch / "battery") if _wanted("battery") else None
    value["forms"] = len(forms.KINDS)
    value["tables"] = len(forms.TABLES)
    value["cases"] = len(forms.CASES)
    value["stages_failed"] = int(f"{value.get('stages_failed', 0)}")
    if price is not None:
        value["price_dated_columns"] = len(price["dated"])  # type: ignore[arg-type]
        value["price_dated_columns_answered"] = len(price["dated_answered"])  # type: ignore[arg-type]
        value["price_q3_new"] = len(price["q3_new"])  # type: ignore[arg-type]
        value["price_q3_lost"] = len(price["q3_lost"])  # type: ignore[arg-type]
    if battery is not None:
        value["price_battery_columns"] = len(battery["reached"])
        value["battery_columns"] = int(battery["columns"][0])
    detail = (
        f"dated {price['dated_cells'] if price else 'not run'}; still held answered {price['dated_answered'] if price else '-'}; "
        f"q3 new {price['q3_new'] if price else '-'}; q3 lost {price['q3_lost'] if price else '-'}; "
        f"battery {battery['reached'] if battery else 'not run'}; misses {named}; stages failed {failures}; "
        f"{round(time.perf_counter() - started)} s"
    )
    kpi_rules.emit("K-HZ-16", value, detail)


if __name__ == "__main__":
    main()
