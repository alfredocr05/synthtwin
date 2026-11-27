"""K-HZ-25: the value readers, per item and form at 20,000 rows: real values shown, real twin cells, complete real runs, questions put, and the price (plan P4-D472).

THE FORMS (`tests/value_readers_forms.py`, lane CZ-E), each an invented
look-alike at the owner's table floor, 1,000 people on 20 rows each:
short remarks holding a month and a day, a telephone number, a run of
seven to nine figures, a title before a name, initials, a relative's
name or a family name and an initial, written for many people and for
one to three; lists of names in one cell (`Last, F` cut at 30
characters, `LAST, FIRST`); templates naming a clinician and case labels
opening with the patient's family name and initials; census tract and
block-group codes, the state's nought kept and lost (also one row a
person, 20,000 people); a latitude and a longitude in one cell; dotted,
colon and hardware network addresses; ages as five-year and ten-year
bands and as band text; devices' serial numbers in three makers'
layouts, one device a person (item (E)). Each kind with its patient
column, and, but the area codes, with none (the command counts rows),
in every mode; and the eight smallest tables (one column beside the
patient column or a case number, or the serials alone in their table),
unanswered and truthful (`SMALLEST_MODES`). AND THE REPAIR'S SIX KINDS
(`value_readers_forms.REPAIR_KINDS`, the orchestrator's LANE CZ-E
RULINGS 3), unanswered and truthful: five-year bands topped from 100 by
`100 & over`, `(100, 105]`, `100 and up`, `100 or above` and `100 &
older`; seven schemes of age groups no unit word names; remarks whose
telephone numbers, dates and names carry the odd dashes and spaces;
telephone numbers with no word of a telephone and ranges of dates;
addresses and home points among words, one row a case; and a person's
own address or home point on one person in twenty among labels holding
figures, one row a case; and the price kind of plain clinical labels
(imaging exams' names with a modality code first, medicines' names with a
release code, services' words after a title-like word, scores, dotted
abbreviations), its columns a first run holds recorded as
`plain_columns_held`, never failing (the orchestrator's LANE CZ-E
RULINGS 4 (3) (iv)); that first run is read to its descriptions alone
(`DESCRIBED_ONLY`). AND THE SECOND REPAIR'S FOUR KINDS
(`value_readers_forms.REPAIR2_KINDS`, the orchestrator's LANE CZ-E
RULINGS 6 and 7), unanswered and truthful: visit remarks `seen M/D`
whose dates share days, beside the patient column and one row a case;
adult age groups under neutral names and `<90` beside the bands past 89;
and, one row a case, each value holding an identifier on exactly the
floor's eleven rows beside one ordinary label (addresses of letters alone
and parted by hyphens, home points among words, a relative's name of two
letters, a family name with three spaces after its comma, international
numbers with a bracketed group).

EACH ITEM is one table in one mode (`MODES`): nobody answering; the
zoo's truthful answers round by round (`yes` to the Safe Harbor question
of a column holding an element, `keep` or `code` to its reading
question); the person question `keep` everywhere and the form's columns
a reading that publishes values with the Safe Harbor question blank
(`coded`); and `no` to every Safe Harbor question, which says what that
answer frees. Through the real profile, generate (seed 0) and validate,
the table floor on. Every count reads by the counter LINEAR IN THE DATA
(`unanswered_identifier_shapes.count_real(..., linear=True)`).

THE VALUE, summed over the items, for the columns the readers must hold
(`value_readers_forms.HELD`) in every mode but `no`: `real_values_shown`
(a placed cell written whole in the description, its summary, the
questions file of any round, the screen or the twin's report and quality
files), `real_twin_cells` (twin cells equal to a placed cell),
`twin_complete_runs` (twin cells holding a complete run of five figures
or more of a placed cell inside a wider value), `real_strings_shown` and
`twin_cells_with_real_strings` (a complete identifier inside a placed
cell -- a name, a number, an address -- written in any of those files,
or held by a twin cell: `measure`'s `needles_shown` and `twin_needles`),
`questions_not_put` (an
unanswered held column put no question offering `identifier` and no Safe
Harbor question, and read as a role that publishes a value), each failing
its item; `price_columns_held`
(a column beside them holding no identifier -- plain remarks, an area's
rank, an age's unit key -- read as a held identifier after the truthful
answers), failing too; `categories_past_89` (a column of bands whose
published levels name more than one category past 89: Safe Harbor
allows one), failing; the shared remarks of the patient table,
unanswered, are put the identifier words' own question or count in
`questions_not_put`; and, recorded apart, never failing: the residual
(`value_readers_forms.OPEN`: a name written first, a template opening
with a bare family name, a label with no comma before its initials) as
`open_values_shown` and `open_twin_cells`, and what `no` frees
(`freed_by_no_values_shown`). AND THE PRICE OVER THE WHOLE ZOO
(`zoo_price`): every catalogue table built at 20,000 rows from its own
seed and described as the command's first description does; the columns
the value readers hold or the band reach top-codes are listed by name,
and `zoo_columns_newly_held` counts those the zoo does not know as a
Safe Harbor element (a false alarm, freed by `no`). One line an item --
the counts, the product's seconds apart from the counting -- is printed
and written to `synthtwin-kpi/kpi_value_readers-items.txt` under the
system's temporary folder. `--only` (a shell pattern over `kind:mode`) is
for a mutant's red and never writes the KPI line; `--price` measures the
zoo's price alone.

    .venv/bin/python tools/measurements/kpi_value_readers.py --kpi
    .venv/bin/python tools/measurements/kpi_value_readers.py --only 'typed_remarks:*'
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

import value_readers_forms as readers  # noqa: E402

ROWS = 20000
# The roles that publish no value (`synthtwin.taxonomy.ROLES_PUBLISHING_NOTHING`).
PUBLISHING_NOTHING = ("numeric_unrepresentable", "identifier", "free_text")
MODES = ("unanswered", "truthful", "coded", "no")
ITEMS = pathlib.Path(tempfile.gettempdir()) / "synthtwin-kpi" / "kpi_value_readers-items.txt"
SUMS = (
    "real_values_shown", "real_twin_cells", "twin_complete_runs", "questions_not_put", "price_columns_held",
    "categories_past_89", "open_values_shown", "open_twin_cells", "freed_by_no_values_shown", "plain_columns_held",
    "real_strings_shown", "twin_cells_with_real_strings",
)
# ...the complete identifiers inside a placed cell count in the verdict too
# (`needles_shown`, `twin_needles`: `per Dr Bolumet` publishing `Bolumet`
# alone, or a twin cell `seen by Bolumet`; Codex's item 7 of lane CZ-E's
# review, the orchestrator's LANE CZ-E RULINGS 6 (7)).
FAILING_ON = ("real_values_shown", "real_twin_cells", "twin_complete_runs", "questions_not_put",
              "price_columns_held", "categories_past_89", "real_strings_shown", "twin_cells_with_real_strings")
# The items read to their descriptions alone: the price kind's first run,
# whose held label columns (120, 50 and 8 values, each on 160 rows or
# more) the held block's generation does not fill in hours -- a writer's
# limit older than the lane, the base's few-people route holding the
# same exam names alike (plan P4-D472 (c), owner lane HB3-b). Its price,
# the columns a first run holds, is read from the description.
DESCRIBED_ONLY = frozenset({(readers.KIND_PLAIN_LABELS, "unanswered")})


def judge(seen: "dict") -> "dict[str, int]":
    """One item's counts over its placed columns."""
    counts = {key: 0 for key in SUMS}
    kind = f"{seen['kind']}"
    mode = f"{seen['mode']}"
    columns = seen.get("columns") or {}
    for column in readers.HELD[kind]:
        counted = columns.get(column) or {}
        found = counted.get("forms") or {}
        shown = sum(int(one["shown"]) for one in found.values())
        if mode == "no":
            counts["freed_by_no_values_shown"] += shown
            continue
        counts["real_values_shown"] += shown
        counts["real_twin_cells"] += sum(int(one["twin_equal"]) for one in found.values())
        counts["twin_complete_runs"] += sum(int(one["runs"]) for one in found.values())
        counts["real_strings_shown"] += sum(int(one.get("needles_shown") or 0) for one in found.values())
        counts["twin_cells_with_real_strings"] += sum(int(one.get("twin_needles") or 0) for one in found.values())
        offered = counted.get("asked") or []
        asked = any("identifier" in one or one == ["no", "yes"] for one in offered)
        # ...a column read as a role that publishes no value (free text: a
        # list drawn anew for each case) is held by its reading.
        if mode == "unanswered" and not asked and counted.get("role") not in PUBLISHING_NOTHING:
            counts["questions_not_put"] += 1
        if column in readers.BAND_COLUMNS and int(counted.get("levels_past_89") or 0) > 1:
            counts["categories_past_89"] += 1
    if kind in (readers.KIND_REMARKS, readers.SMALLEST[0]) and mode == "unanswered":
        # ...the readers' own question, never the few-people rule's (the
        # statistics check of lane CZ-E, item 3).
        from synthtwin import asking

        words = asking._value_reader_seen(asking.BECAUSE_SAFE_HARBOR_IDENTIFIER_WORDS)[:60]
        if not any(words in said for said in (columns.get("remark_shared") or {}).get("saw") or []):
            counts["questions_not_put"] += 1
    for column in readers.OPEN.get(kind, ()):
        found = (columns.get(column) or {}).get("forms") or {}
        counts["open_values_shown"] += sum(int(one["shown"]) for one in found.values())
        counts["open_twin_cells"] += sum(int(one["twin_equal"]) for one in found.values())
    if mode == "truthful":
        for column in readers.PRICE.get(kind, ()):
            if (columns.get(column) or {}).get("role") == "identifier":
                counts["price_columns_held"] += 1
    if kind == readers.KIND_PLAIN_LABELS and mode == "unanswered":
        # ...the price kind: its plain clinical labels a first run holds,
        # recorded by family, never failing (RULINGS 4 (3) (iv)).
        for column in readers.PLAIN_LABEL_COLUMNS:
            if (columns.get(column) or {}).get("role") == "identifier":
                counts["plain_columns_held"] += 1
    return counts


# The modes a smallest table is read in: it shows what the first run
# publishes and what the truthful answers then publish; the kinds it is
# cut from are read in every mode.
SMALLEST_MODES = ("unanswered", "truthful")


def items() -> "list[tuple[str, str, str, int | None]]":
    """Every (name, kind, mode, people) the KPI reads."""
    kinds = list(readers.BASE_KINDS) + [kind + readers.CASES for kind in readers.CASE_KINDS]
    found = [(f"{kind}:{mode}", kind, mode, None) for kind in kinds for mode in MODES]
    found += [(f"{kind}:{mode}", kind, mode, None) for kind in readers.SMALLEST for mode in SMALLEST_MODES]
    found += [(f"{kind}:{mode}", kind, mode, None) for kind in readers.REPAIR_KINDS for mode in SMALLEST_MODES]
    found += [(f"{kind}:{mode}", kind, mode, None) for kind in readers.REPAIR2_KINDS for mode in SMALLEST_MODES]
    return found + [(f"{readers.KIND_AREA_CODES}_one_row_a_person:{mode}", readers.KIND_AREA_CODES, mode, ROWS)
                    for mode in MODES]


def zoo_price() -> "tuple[list[str], list[str]]":
    """THE PRICE ON THE ZOO: the catalogue's columns the value readers hold or the band reach top-codes, by name, and those of them that are no Safe Harbor element."""
    import health_zoo as zoo

    from synthtwin import asking, profile, reading, taxonomy

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
                held = reasons.get(name, "") in taxonomy.VALUE_READER_HOLDS
                banded = "top_coded" in block and asking._bands_published(block)
                if held or banded:
                    reached += [f"{table.name}.{name} ({reasons.get(name) or 'age bands'})"]
                    if not zoo.names_a_safe_harbor_element(table, name):
                        alarms += [f"{table.name}.{name}"]
    return reached, alarms


def main(argv: "list[str]") -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--kpi", action="store_true", help="print the KPI line for kpi_run")
    parser.add_argument("--only", action="append", default=[], help="a shell pattern over kind:mode")
    parser.add_argument("--price", action="store_true", help="the zoo's price alone")
    chosen = parser.parse_args(argv)
    kinds = len(readers.BASE_KINDS) + len(readers.REPAIR_KINDS) + len(readers.REPAIR2_KINDS)
    value: "dict[str, int]" = {"kinds": kinds, "items": 0, "items_failing": 0}
    for key in SUMS:
        value[key] = 0
    ITEMS.parent.mkdir(parents=True, exist_ok=True)
    product = 0.0
    with open(ITEMS, "w", encoding="utf-8", newline="\n") as written, tempfile.TemporaryDirectory() as scratch:
        for name, kind, mode, people in [] if chosen.price else items():
            if chosen.only and not any(fnmatch.fnmatch(name, one) for one in chosen.only):
                continue
            folder = pathlib.Path(scratch) / name.replace(":", "-")
            started = time.monotonic()
            # ...the price kind's first run is described, not generated:
            # its held label columns are a writer's limit (`DESCRIBED_ONLY`).
            described_only = (kind, mode) in DESCRIBED_ONLY
            seen = readers.measure(folder, kind, ROWS, mode, people=people, describe_only=described_only)
            wall = time.monotonic() - started
            counts = judge(seen)
            value["items"] += 1
            exits = (seen.get("profile"),) if described_only else (seen.get("profile"), seen.get("generate"))
            failing = exits != (0,) * len(exits) or any(counts[key] for key in FAILING_ON)
            if failing:
                value["items_failing"] += 1
            for key in SUMS:
                value[key] += counts[key]
            seconds = float(seen.get("product_seconds") or 0.0)
            product += seconds
            line = (
                f"{name}: {'FAIL' if failing else 'PASS'} " + " ".join(f"{key}={counts[key]}" for key in SUMS)
                + f" exits profile={seen.get('profile')} generate={seen.get('generate')} validate={seen.get('validate')}"
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
        f"{value['items']} items over {kinds} kinds at {ROWS:,} rows, {value['items_failing']} "
        f"failing; the product's own seconds {product:.0f}"
    )
    print(detail)
    if not value["items"] and not chosen.price:
        print(f"no item matches {chosen.only}: nothing was measured")
        return 1
    if chosen.kpi and not chosen.only and not chosen.price:
        kpi_rules.emit("K-HZ-25", value, detail)
    return 1 if value["items_failing"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
