"""K-HZ-42: the persons' names reader's residuals per shape and mode at 20,000 rows and 1,000 people: real names shown, real twin cells, complete real names inside wider twin cells, questions put, and the price in control columns per heading and over the whole zoo (plan P4-D494).

THE TABLES (`tests/persons_names_forms.py`, lanes CZ-F and CZ-G-b), each
an invented look-alike at the owner's table floor through the commands a
person types -- profile, its rounds of answers by mode, generate (seed 0)
and validate, the table floor on -- counted by the linear counter
(`persons_names_forms.counted`), in the modes of `persons_names_forms.MODES`
the rulings name: nobody answering, and `coded` (the person question
`keep`, the names column a reading that publishes values, its Safe Harbor
question blank).

THE BAR, each item failing where a real name is shown, a twin cell equals
one or holds one inside a wider value, or the column is published or put no
question (lane CZ-G-b's items 1 to 4, each a residual of plan P4-D478 (a)
this lane closes): the share at two in three (`share_edge`, 1,000 names
beside 520 small-letter spellings of them) and at half (`share_half`); a
spelling cycled in row order (`cycled`, 60,000 rows) and names on fewer
rows than codes (`frequency`, 110,200 rows), each of which the walk over
the cells left unheld; the name field repeated after `~` and its family
name in `&` subcomponents, the apostrophe marks the one definition gained,
a title before a particle-led family name, the suffix words it gained
after a name written whole and after a family name alone under
`patient_surname`, a mark drawn as nothing inside the family name
(`inside_word`, the orchestrator's LANE CZ-G-b RULINGS 2); and 60
clinicians under each of seven staff headings the
heading arm gained (`social_worker`, `case_manager`, `next_of_kin`,
`witness`, `pharmacy_resident`, `er_md`, `second_reader`).

AND (lane CZ-G-b's repair 1) names on many rows beside more rare spellings
(`many_rows`, 73,000 rows, answered `keep`: the walk's reading kept beside
the sample) and 60 clinicians written `Given Family CRNA` under
`anesthesia_provider` beside 1,000 patients (`crna_beside`, unanswered
and coded: a word lane CZ-G-b made a role never makes one of a name
written whole before it).

THE PRICE, recorded and never failing: each heading's control of 40
ordinary labels such a column could hold (`control_<heading>`), whether it
is held (a false alarm: `control_columns_held`); and over the zoo's
catalogue at 20,000 rows, every column read as if its role published its
levels (a superset of what a description reaches, no description made), the
columns the holds reach, by name, and those the zoo knows as no Safe Harbor
element (`zoo_columns_newly_held`). AND, since lane CZ-G-b's repair 1,
three tables of label columns read through the first profile run
(`persons_names_forms.price_table`), each column held counted, never
asserted: the HELD-OUT controls, 40 labels of each staff heading's kind
outside the closed list's words, under each of the 18 headings
(`held_out_columns_held`, the stated price of keeping them); and the
NEAR-MISS labels, medicines, procedures and departments of 300 labels at
shares of two capitalised words from 45 to 70 per cent, in mixed case and
in capitals, and one column of labels ending in an ordinal
(`near_miss_columns_held`, the stated band of the value arm's half).

THE RESIDUAL, recorded and never failing (the stated limits of plan P4-D494
(a), each unanswered AND answered `coded` since lane CZ-G-b's repair 1):
family names alone, names in small letters and names in a script with no
capitals under a neutral name, 60 clinicians and 60 written `Family J.`
under a neutral name, 60 clinicians under `np` (a heading left out), and
names past half (`share_beyond`): their real names shown and twin cells
(`residual_values_shown`, `residual_twin_cells`).

Each item's generate is bounded at `GENERATE_BOUND` CPU seconds (the held
writer's time cliff of STANDING NOTE ADDENDUM 2 (8), owner lane HB3-b): an
item stopped there counts in `generate_stopped`, its twin unread.

One line an item is printed and written to
`synthtwin-kpi/kpi_persons_names_residuals-items.txt` under the system's
temporary folder. `--only` (a shell pattern over `layout:shape:mode`) is
for a mutant's red and never writes the KPI line.

    .venv/bin/python tools/measurements/kpi_persons_names_residuals.py --kpi
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

import persons_names_forms as names  # noqa: E402

ROWS = 20000
ITEMS = pathlib.Path(tempfile.gettempdir()) / "synthtwin-kpi" / "kpi_persons_names_residuals-items.txt"
SUMS = ("real_values_shown", "real_twin_cells", "twin_complete_runs", "questions_not_put", "control_columns_held",
        "residual_values_shown", "residual_twin_cells", "generate_stopped", "held_out_columns_held",
        "near_miss_columns_held")
# THE HELD WRITER'S TIME CLIFF (STANDING NOTE ADDENDUM 2 (8), owner lane
# HB3-b, whose part a meters it): a held names column of some censuses is not
# generated in hours on this line, so each item's generate is bounded at
# this many seconds of CPU; an item stopped there counts in
# `generate_stopped`, its twin unread, its description, questions and
# screen still counted.
GENERATE_BOUND = 120.0
_BOTH = ("unanswered", "coded")
_ALONE = ("unanswered",)
BAR = (
    (("share_edge", "comma"), _BOTH), (("share_half", "comma"), _ALONE), (("cycled", "comma"), _BOTH),
    (("frequency", "comma"), ("coded",)),
    (("alone", "caret_repeat"), _BOTH), (("alone", "caret_amp"), _BOTH), (("alone", "apostrophe_more"), _BOTH),
    (("alone", "title_particle"), _ALONE), (("alone", "suffix_more"), _BOTH), (("alone", "inside_word"), _BOTH),
    (("suffix_surname", "suffixes_more"), _BOTH), (("unlisted_role", "comma"), _BOTH),
    (("role_case_manager", "comma"), _ALONE), (("role_next_of_kin", "comma"), _ALONE),
    (("role_witness", "comma"), _ALONE), (("role_pharmacy_resident", "comma"), _ALONE),
    (("role_er_md", "comma"), _ALONE), (("role_second_reader", "comma"), _ALONE),
    (("many_rows", "comma"), ("coded",)), (("crna_beside", "crna"), _BOTH),
)
PRICE = tuple(((layout, "labels"), _ALONE) for layout in names.CONTROL_LAYOUT_HEADING)
RESIDUAL = (("alone", "family"), ("alone", "small_letters"), ("alone", "no_capitals"), ("staff", "comma"),
            ("staff", "initials"), ("role_np", "comma"), ("share_beyond", "comma"))
# The rows of the layouts that are not at the KPI size.
SIZES = {"cycled": names.CYCLED_ROWS, "frequency": names.FREQUENCY_NAMES * names.FREQUENCY_NAME_ROWS
         + names.FREQUENCY_CODES * names.FREQUENCY_CODE_ROWS, "many_rows": names.MANY_ROWS}


def items() -> "list[tuple[str, str, str, str, str]]":
    """Every (name, part, layout, shape, mode) the KPI reads: the bar, the price, the price families, the residual."""
    found: "list[tuple[str, str, str, str, str]]" = []
    for part, tables in (("bar", BAR), ("price", PRICE)):
        found += [(f"{layout}:{shape}:{mode}", part, layout, shape, mode) for (layout, shape), modes in tables
                  for mode in modes]
    found += [(f"price:{family}", "family", family, "labels", "unanswered") for family in names.PRICE_FAMILIES]
    found += [(f"residual:{layout}:{shape}:{mode}", "residual", layout, shape, mode)
              for layout, shape in RESIDUAL for mode in _BOTH]
    return found


def judge(part: str, seen: "dict") -> "tuple[dict[str, int], list[str]]":
    """One item's counts and its failures (the bar's only)."""
    counts = {key: 0 for key in SUMS}
    if part == "family":
        # ...a price family, read through the first profile run: its columns
        # held, recorded (lane CZ-G-b's repair 1).
        held = seen.get("held") or []
        key = "held_out_columns_held" if seen.get("family") == "held_out" else "near_miss_columns_held"
        counts[key] = len(held)  # type: ignore[arg-type]
        return counts, [] if seen.get("profile") == 0 else [f"exits {seen.get('profile')}"]
    stopped = seen.get("generate") == names.GENERATE_STOPPED
    counts["generate_stopped"] = 1 if stopped else 0
    shown = max(int(seen.get("shown") or 0), int(seen.get("shown_folded") or 0))
    roles = seen.get("roles") or []
    exits = [] if seen.get("profile") == 0 and (seen.get("generate") == 0 or stopped) else [
        f"exits {seen.get('profile')} {seen.get('generate')}"]
    if part == "residual":
        counts["residual_values_shown"] = shown
        counts["residual_twin_cells"] = int(seen.get("twin_folded") or 0)
        return counts, exits
    if part == "price":
        held = bool(roles) and roles[-1] in names.PUBLISHING_NOTHING
        counts["control_columns_held"] = 1 if held else 0
        return counts, exits
    counts["real_values_shown"] = shown
    counts["real_twin_cells"] = int(seen.get("twin_folded") or 0)
    counts["twin_complete_runs"] = int(seen.get("twin_inside") or 0)
    failed = [one for one in names.failures(seen) if not (stopped and one.startswith("exits "))]
    counts["questions_not_put"] = 1 if "no question put" in failed else 0
    return counts, failed


def zoo_price() -> "tuple[list[str], list[str]]":
    """THE PRICE ON THE ZOO, A SUPERSET: every column of every catalogue table at 20,000 rows read by `persons_names_hold` as if its role published its levels; the columns reached, by name, and those of them the zoo knows as no Safe Harbor element."""
    import health_zoo as zoo

    from synthtwin import taxonomy

    reached: "list[str]" = []
    alarms: "list[str]" = []
    for table in zoo.catalogue():
        header, rows = table.build(zoo.KPI_ROWS, zoo.seed_of(table))
        for place, name in enumerate(header):
            cells = [row[place] if place < len(row) else "" for row in rows]
            reason = taxonomy.persons_names_hold(name, taxonomy.ROLE_CATEGORICAL, cells, frozenset())
            if reason:
                reached += [f"{table.name}.{name} ({reason})"]
                if not zoo.names_a_safe_harbor_element(table, name):
                    alarms += [f"{table.name}.{name}"]
    return reached, alarms


def main(argv: "list[str]") -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--kpi", action="store_true", help="print the KPI line for kpi_run")
    parser.add_argument("--only", action="append", default=[], help="a shell pattern over layout:shape:mode")
    chosen = parser.parse_args(argv)
    every = items()
    value: "dict[str, int]" = {"tables": len(BAR) + len(PRICE) + len(names.PRICE_FAMILIES) + len(RESIDUAL), "items": 0,
                               "items_failing": 0}
    for key in SUMS:
        value[key] = 0
    ITEMS.parent.mkdir(parents=True, exist_ok=True)
    product = 0.0
    with open(ITEMS, "w", encoding="utf-8", newline="\n") as written, tempfile.TemporaryDirectory() as scratch:
        for name, part, layout, shape, mode in every:
            if chosen.only and not any(fnmatch.fnmatch(name, one) for one in chosen.only):
                continue
            folder = pathlib.Path(scratch) / name.replace(":", "-")
            started = time.monotonic()
            if part == "family":
                seen = names.price_table(folder, layout, ROWS)
            else:
                seen = names.measure(folder, layout, shape, SIZES.get(layout, ROWS), mode,
                                     generate_cpu_at_most=GENERATE_BOUND)
            wall = time.monotonic() - started
            counts, failed = judge(part, seen)
            value["items"] += 1
            if failed and part in ("bar", "family"):
                value["items_failing"] += 1
            for key in SUMS:
                value[key] += counts[key]
            seconds = float(seen.get("product_seconds") or 0.0)  # type: ignore[arg-type]
            product += seconds
            verdict = ("FAIL " + "; ".join(failed)) if failed and part in ("bar", "family") else part.upper()
            if part == "family":
                line = (
                    f"{name}: {verdict} " + " ".join(f"{key}={counts[key]}" for key in SUMS)
                    + f" columns={seen.get('columns')} held={seen.get('held')} roles={seen.get('roles')}"
                    f" asked={seen.get('asked')} exit profile={seen.get('profile')} product {seconds:.1f} s (the first"
                    f" profile run alone), counting {wall - seconds:.1f} s"
                )
            else:
                line = (
                    f"{name}: {verdict} " + " ".join(f"{key}={counts[key]}" for key in SUMS)
                    + f" names={seen.get('different_names')} roles={seen.get('roles')} asked={seen.get('asked')}"
                    f" exits profile={seen.get('profile')} generate={seen.get('generate')} validate={seen.get('validate')}"
                    f" product {seconds:.1f} s (profile {seen.get('profile_seconds')}, generate "
                    f"{seen.get('generate_seconds')}, validate {seen.get('validate_seconds')}), counting {wall - seconds:.1f} s"
                )
            print(line, flush=True)
            written.write(line + "\n")
            shutil.rmtree(folder, ignore_errors=True)
        if not chosen.only:
            started = time.monotonic()
            reached, alarms = zoo_price()
            value["zoo_columns_reached"] = len(reached)
            value["zoo_columns_newly_held"] = len(alarms)
            line = (
                f"zoo price (a superset: every column read as if it published its levels): {len(reached)} catalogue "
                f"columns reached ({'; '.join(reached) or 'none'}); {len(alarms)} not a Safe Harbor element "
                f"({'; '.join(alarms) or 'none'}); {time.monotonic() - started:.0f} s"
            )
            print(line, flush=True)
            written.write(line + "\n")
    detail = (
        f"{value['items']} items over {value['tables']} tables at {ROWS:,} rows (the cycled layout's at "
        f"{names.CYCLED_ROWS:,}, the frequency layout's at {SIZES['frequency']:,}, the many-rows layout's at "
        f"{names.MANY_ROWS:,}), {value['items_failing']} failing; the product's own seconds {product:.0f}"
    )
    print(detail)
    if not value["items"]:
        print(f"no item matches {chosen.only}: nothing was measured")
        return 1
    if chosen.kpi and not chosen.only:
        kpi_rules.emit("K-HZ-42", value, detail)
    return 1 if value["items_failing"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
