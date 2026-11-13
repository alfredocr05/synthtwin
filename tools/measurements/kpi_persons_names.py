"""K-HZ-30: columns of persons' names per layout, shape and mode at 20,000 rows: real names shown, real twin cells, complete real names inside wider twin cells, questions put, and the price over the zoo (plan P4-D478).

THE TABLES (`tests/persons_names_forms.py`, lane CZ-F), each an invented
look-alike at the owner's table floor, one name a person, 1,000 people on
20 rows each: the names column alone under a neutral name (counted in
rows), beside a person column, under `patient_full_name`, family names
alone under `patient_surname`, 60 clinicians' names under `surgeon` beside a case
number, one name a row (20,000 people) and visits spread unevenly (about
5,000 people, 300 on 11 to 30 rows); the names written `Family, Given`,
`O'Family, Given`, `Given Family`, `FAMILY, GIVEN`, every family of
spellings drawn per person, or the family name alone.

AND (lane CZ-F's repair) the names written as a health message's name
field (`FAMILY^GIVEN^M`, one in three `Family^Given^^^`) alone and under
`person_name`; `Family,` U+200B `Given` and `Family, Given` U+200E alone;
116,400 rows in date order, an early era of 4,200 people in small letters
on 2 rows each before 9,000 written `Family, Given` on 12 rows each; 60
clinicians written `Family J.` under `surgeon`; and family names alone
under `PERSONLASTNAME`, a name in capitals with no mark between its words.

AND (lane CZ-F's repair 2, Codex's review and the combined verify) one,
two, three and sixty family names under `patient_surname`, `surgeon` and
`PERSONLASTNAME` beside a case number; 60 family names each with a suffix
(` Jr.` after each, or every spelling of the family-name reader's
suffixes) under `patient_surname`; and 49,152 rows in blocks of 12, a name
in small letters first in each block and 11 of 4,096 names after it. The
counter reads every string of each JSON file the commands write DECODED
and each text for the eye a second time with its escapes decoded
(`persons_names_forms.published_texts`).

EACH ITEM is one table in one mode (`persons_names_forms.MODES`): nobody
answering; the zoo's truthful answers round by round (`yes` to the names
column's Safe Harbor question); the person question `keep` and the names
column a reading that publishes values, its Safe Harbor question blank
(`coded`: on the tables whose names column is asked only its Safe Harbor
question it answers nothing, as nobody answering); `no` to every Safe
Harbor question, which says what that answer frees; and a reading typed on
every profile call, `--code <names column>` (`typed`) or `--measurement
<names column>` (`measured`), the zoo's answers round by round and the
names column's Safe Harbor question blank. Through the real profile,
generate (seed 0) and validate, the table floor on. Every count reads by a
counter LINEAR IN THE DATA (`persons_names_forms.counted`,
`unanswered_identifier_shapes.count_real(..., linear=True)` beside it).

THE VALUE, summed over the items, in every mode but `no`:
`real_values_shown` (a real name written whole, exact or folded, in the
description, its summary, the questions file of any round, the screen or
the twin's report and quality files), `real_twin_cells` (twin cells equal
to a real name, exact or folded), `twin_complete_runs` (twin cells holding
a complete real name inside a wider value), `questions_not_put` (an
unanswered names column with no Safe Harbor question and no question
offering `identifier`, read as a role that publishes values), each
failing its item; recorded apart, never failing, what `no` frees
(`freed_by_no_values_shown`) and THE RESIDUAL (`RESIDUAL`, the reader's
stated limits, each unanswered: family names alone and names in small
letters or in a script with no capitals under a neutral name, and 60
clinicians' names under a neutral name), its real names shown and twin
cells (`residual_values_shown`, `residual_twin_cells`), and, from lane
CZ-F's repair, 1,000 names of which 520 people are also written once in
small letters (the share under two in three), 60 clinicians under
`social_worker` (a staff heading outside the closed list) and 60 clinicians written
`Family J.` under a neutral name. AND THE PRICE OVER THE WHOLE ZOO
(`zoo_price`): every catalogue table built at 20,000 rows from its own
seed and described as the command's first description does; the columns
the persons' names holds reach are listed by name, and
`zoo_columns_newly_held` counts those the zoo does not know as a Safe
Harbor element or a person's name (a false alarm, freed by `no`). One line
an item -- the counts, the product's seconds apart from the counting -- is
printed and written to `synthtwin-kpi/kpi_persons_names-items.txt` under
the system's temporary folder. `--only` (a shell pattern over
`layout:shape:mode`) is for a mutant's red and never writes the KPI line;
`--price` measures the zoo's price alone.

    .venv/bin/python tools/measurements/kpi_persons_names.py --kpi
    .venv/bin/python tools/measurements/kpi_persons_names.py --only 'alone:*:unanswered'
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
ITEMS = pathlib.Path(tempfile.gettempdir()) / "synthtwin-kpi" / "kpi_persons_names-items.txt"
SUMS = ("real_values_shown", "real_twin_cells", "twin_complete_runs", "questions_not_put", "freed_by_no_values_shown",
        "residual_values_shown", "residual_twin_cells")
# The layouts and shapes measured, each with its modes: every shape alone,
# the others in the shape a patient table writes most, in every mode; and
# those of lane CZ-F's repair in the modes its rulings name.
TABLES = (
    [(("alone", shape), names.MODES) for shape in ("comma", "apostrophe", "given_first", "capitals", "mixed")]
    + [((layout, shape), names.MODES) for layout, shape in (
        ("beside", "comma"), ("beside", "mixed"), ("heading", "comma"), ("surname", "family"),
        ("clinician", "comma"), ("one_a_row", "comma"), ("uneven", "comma"))]
    + [((layout, shape), ("unanswered", "truthful", "coded")) for layout, shape in (
        ("alone", "caret"), ("person_name", "caret"), ("alone", "zero_width"), ("alone", "format_trailing"),
        ("clinician", "initials"), ("run_together", "family"))]
    + [(("era", "comma"), ("unanswered", "coded"))]
    # ...and lane CZ-F's repair 2: one to sixty family names under three
    # names that say a person's name (Codex's item 1), unanswered and coded,
    # one and two also typed; 60 family names with a suffix (Codex's item 2:
    # through the description, the questions and the twin), unanswered,
    # coded and typed; and the blocks of 12 rows (the combined verify's
    # item 1), unanswered and coded.
    + [((layout, shape), ("unanswered", "coded", "typed") if shape in ("one", "two") else ("unanswered", "coded"))
       for layout in ("few_surname", "few_clinician", "few_run_together") for shape in names.FEW]
    + [(("suffix_surname", shape), ("unanswered", "coded", "typed")) for shape in ("suffix_jr", "suffixes")]
    + [(("blocks", "comma"), ("unanswered", "coded"))]
)
# THE RESIDUAL, recorded and never failed (the reader's stated limits, owner
# lane CZ-G): family names alone under a neutral name, names in small
# letters, names in a script with no capitals, and 60 clinicians' names
# under a neutral name; the share under two in three, 60 clinicians under a
# staff heading outside the closed list, and 60 written `Family J.` under a
# neutral name -- each unanswered.
RESIDUAL = (("alone", "family"), ("alone", "small_letters"), ("alone", "no_capitals"), ("staff", "comma"),
            ("share_edge", "comma"), ("unlisted_role", "comma"), ("staff", "initials"))


def judge(seen: "dict") -> "dict[str, int]":
    """One item's counts."""
    counts = {key: 0 for key in SUMS}
    shown = max(int(seen.get("shown") or 0), int(seen.get("shown_folded") or 0))
    if seen.get("residual"):
        counts["residual_values_shown"] = shown
        counts["residual_twin_cells"] = int(seen.get("twin_folded") or 0)
        return counts
    if seen["mode"] == "no":
        counts["freed_by_no_values_shown"] = shown
        return counts
    counts["real_values_shown"] = shown
    counts["real_twin_cells"] = int(seen.get("twin_folded") or 0)
    counts["twin_complete_runs"] = int(seen.get("twin_inside") or 0)
    counts["questions_not_put"] = 1 if "no question put" in names.failures(seen) else 0
    return counts


def items() -> "list[tuple[str, str, str, str]]":
    """Every (name, layout, shape, mode) the KPI reads, the residual's last."""
    return [(f"{layout}:{shape}:{mode}", layout, shape, mode) for (layout, shape), modes in TABLES for mode in modes] + [
        (f"residual:{layout}:{shape}:unanswered", layout, shape, "unanswered") for layout, shape in RESIDUAL
    ]


def zoo_price() -> "tuple[list[str], list[str]]":
    """THE PRICE ON THE ZOO: the catalogue's columns the persons' names holds reach, by name, and those of them that are no Safe Harbor element and no person's name."""
    import health_zoo as zoo

    from synthtwin import profile, reading, taxonomy

    reached: "list[str]" = []
    alarms: "list[str]" = []
    with tempfile.TemporaryDirectory() as scratch:
        for table in zoo.catalogue():
            header, rows = table.build(zoo.KPI_ROWS, zoo.seed_of(table))
            path = pathlib.Path(scratch) / f"{table.name}{table.suffix}"
            path.write_bytes(table.write(header, rows))
            reasons: "dict[str, str]" = {}
            document = profile.build_document(
                reading.read_table(f"{path}"), taxonomy.Settings(), [], top_code=True, five_figures=[],
                ages_held=[], harbor_year=taxonomy.SAFE_HARBOR_REFERENCE_YEAR, harbor_reasons=reasons,
                ages_established={},
            )
            path.unlink()
            for block in document["columns"]:  # type: ignore[attr-defined]
                name = f"{block['name']}"
                if reasons.get(name, "") in taxonomy.PERSONS_NAMES_HOLDS:
                    reached += [f"{table.name}.{name} ({reasons[name]})"]
                    if not zoo.names_a_safe_harbor_element(table, name):
                        alarms += [f"{table.name}.{name}"]
    return reached, alarms


def main(argv: "list[str]") -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--kpi", action="store_true", help="print the KPI line for kpi_run")
    parser.add_argument("--only", action="append", default=[], help="a shell pattern over layout:shape:mode")
    parser.add_argument("--price", action="store_true", help="the zoo's price alone")
    chosen = parser.parse_args(argv)
    value: "dict[str, int]" = {"tables": len(TABLES), "items": 0, "items_failing": 0}
    for key in SUMS:
        value[key] = 0
    ITEMS.parent.mkdir(parents=True, exist_ok=True)
    product = 0.0
    with open(ITEMS, "w", encoding="utf-8", newline="\n") as written, tempfile.TemporaryDirectory() as scratch:
        for name, layout, shape, mode in [] if chosen.price else items():
            if chosen.only and not any(fnmatch.fnmatch(name, one) for one in chosen.only):
                continue
            folder = pathlib.Path(scratch) / name.replace(":", "-")
            started = time.monotonic()
            rows = (names.ERA_EARLY * names.ERA_EARLY_ROWS + names.ERA_LATE * names.ERA_LATE_ROWS if layout == "era"
                    else names.BLOCKS * names.BLOCK_ROWS if layout == "blocks" else ROWS)
            seen = names.measure(folder, layout, shape, rows, mode)
            seen["residual"] = name.startswith("residual:")
            wall = time.monotonic() - started
            counts = judge(seen)
            failed = [] if seen["residual"] else names.failures(seen)
            value["items"] += 1
            if failed:
                value["items_failing"] += 1
            for key in SUMS:
                value[key] += counts[key]
            seconds = float(seen.get("product_seconds") or 0.0)  # type: ignore[arg-type]
            product += seconds
            line = (
                f"{name}: {'FAIL ' + '; '.join(failed) if failed else 'RECORDED' if seen['residual'] else 'PASS'} "
                + " ".join(f"{key}={counts[key]}" for key in SUMS)
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
                f"zoo price: {len(reached)} catalogue columns reached ({'; '.join(reached) or 'none'}); "
                f"{len(alarms)} not a Safe Harbor element ({'; '.join(alarms) or 'none'}); "
                f"{time.monotonic() - started:.0f} s"
            )
            print(line, flush=True)
            written.write(line + "\n")
    detail = (
        f"{value['items']} items over {len(TABLES)} tables at {ROWS:,} rows (the era's at 116,400, the blocks' at "
        f"49,152), {value['items_failing']} failing; the product's own seconds {product:.0f}"
    )
    print(detail)
    if not value["items"] and not chosen.price:
        print(f"no item matches {chosen.only}: nothing was measured")
        return 1
    if chosen.kpi and not chosen.only and not chosen.price:
        kpi_rules.emit("K-HZ-30", value, detail)
    return 1 if value["items_failing"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
