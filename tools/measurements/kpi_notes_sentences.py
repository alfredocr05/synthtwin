"""K-HZ-34: columns of sentences per invented family and mode at 20,000 rows: sentences shown, twin cells, questions put, and the price over the zoo and the goldens (plan P4-D481).

THE TABLES (`tests/notes_sentences_forms.py`, lane NOTES), each an invented
look-alike at the owner's table floor, 1,000 people on 20 rows each:
`banks` (stock banks of 5, 50, 216 and 900 sentences, the bank of five
holding one sentence of one word since lane NOTES's repair 2, free text
all different, 70 per cent stock and 30 per cent unique), `templates` (one
variable part each: a clinician's name with no title, a title and a name,
a month and a day, a figure, a place, a relative's name on 100 patients'
rows) and `neighbours` (lane NOTES's repair 1: label columns whose 24 rows
of one to three people carry twelve typed comments naming a made-up
person -- codes beside them, 45 per cent stock sentences, and 60 per cent,
a column of sentences; and since repair 2 codes beside the same comments
typed with no sentence mark -- and two-part notes of a script written
with no space, each naming a made-up clinician), each beside three control
columns (3 and 30 short codes, complaints joined by commas) that must keep
their levels.

EACH ITEM is one table in one mode (`notes_sentences_forms.TABLE_MODES`):
nobody answering (the person question open), the person column said
(`--identifier subject_id`), no person column (counted in rows), the
person column said and every sentence question answered `text`, and
answered `identifier`; the neighbours unanswered, with the person said,
and with every question offering `no` answered `no`. Through the real
profile, the answers rounds, generate (seed 0) and validate, the table
floor on, nobody at the keyboard. Counted by a counter linear in the data
(`measure`), over every different real value of each note column.

THE VALUE, summed over the items: `sentences_shown` (a real value of a
note column -- of a label column of the neighbours, one fewer than 11
people hold -- whole and folded, in the description, its summary, a
questions file, the screen or the twin's report and quality files),
`sentences_shown_few_people` (of those, held by fewer than 11 people),
`twin_cells_real` (twin cells equal to such a value; free text and a
held column publish none), `questions_not_put` (a column the reading moved
to free text with no question offering `text`, unanswered), `controls_moved`
(a control column not read as the categories it was), each failing its
item; recorded apart, never failing: `identifier_refused` (items whose
`identifier` answer the table floor refuses, counting people by every
record number: lane EZ-a's item), `validate_sentence_misses` (the twin's
column of sentences read back as labels by the validator, `axes.role` and
`axes.statistical_type`, which its hand-over of the columns its description
read so closes since batch 4t's merge of lane NOTES, `validation.
described_text_here`; and since repair 2 the shape form of a
sentence of one word, `free_text.shape_forms`, which the free-text writer
misses on some tables: lane NOTES-b's; any other miss fails its item),
`validate_misses_by_obligation` (every miss of the twin's columns, by the
obligation missed, so the hand-over's landing is measured at the floor),
`neighbour_values_shown` and `neighbour_twin_cells_real` (the two-part
notes the reading does not read, P4-D481 (c)), and THE PRICE: every catalogue table of
the zoo built at 20,000 rows from its own seed and described as the
command's first description does (a table none of whose cells is a
sentence is not described: none of its columns can be), the columns described as free text for
their sentences listed by name (`zoo_columns_reached`, `zoo_columns_not_notes`
for those the zoo does not hold as notes), and the goldens' battery tables
at 20,000 rows (`golden_columns_reached`). One line an item is printed and
written to `synthtwin-kpi/kpi_notes_sentences-items.txt` under the system's
temporary folder. `--only` (a shell pattern over `table:mode`) is for a
mutant's red and never writes the KPI line; `--price` measures the price
alone.

    .venv/bin/python tools/measurements/kpi_notes_sentences.py --kpi
    .venv/bin/python tools/measurements/kpi_notes_sentences.py --only 'banks:unanswered'
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

import notes_sentences_forms as forms  # noqa: E402

ROWS = 20000
ITEMS = pathlib.Path(tempfile.gettempdir()) / "synthtwin-kpi" / "kpi_notes_sentences-items.txt"
SUMS = ("sentences_shown", "sentences_shown_few_people", "twin_cells_real", "questions_not_put", "controls_moved",
        "identifier_refused", "validate_sentence_misses", "neighbour_values_shown", "neighbour_twin_cells_real")
# The zoo's columns of notes: the notes kind's text column and the reports'
# two, named through the catalogue's kinds.
NOTE_KINDS = ("clinical_notes", "report_text_with_headings", "long_cell")


def obligation_of(line: str) -> str:
    """The obligation a missed line of the twin's quality report names (`column: obligation [what]: MISSED`)."""
    named = line.split(": ", 1)[1] if ": " in line else line
    return named.split(" [", 1)[0].strip()


def judge(seen: "dict") -> "tuple[dict[str, int], list[str], dict[str, int]]":
    """One item's counts, its failures and the twin's misses by obligation."""
    counts = {key: 0 for key in SUMS}
    failed: "list[str]" = []
    obligations: "dict[str, int]" = {}
    mode = seen["mode"]
    if mode == "identifier" and (seen.get("profile") != 0 or seen.get("answers", 0) != 0):
        counts["identifier_refused"] = 1
        return counts, failed, obligations
    for name, column in seen["columns"].items():
        if name in forms.NEIGHBOURS:
            counts["neighbour_values_shown"] += int(column["sentences_shown"])
            counts["neighbour_twin_cells_real"] += int(column["twin_cells_real"])
            continue
        counts["sentences_shown"] += int(column["sentences_shown"])
        counts["sentences_shown_few_people"] += int(column["sentences_shown_few_people"])
        counts["twin_cells_real"] += int(column["twin_cells_real"])
        if column["sentences_shown"] or column["twin_cells_real"]:
            failed += [f"{name} shown {column['sentences_shown']}, twin {column['twin_cells_real']}"]
        if name in forms.CONTROLS:
            if column["role"] != "categorical" or not column["levels"]:
                counts["controls_moved"] += 1
                failed += [f"{name} read as {column['role']}"]
            continue
        if column["moved"] and mode in ("unanswered", "person_said", "no_person", "no") and "text" not in column["asked"]:
            counts["questions_not_put"] += 1
            failed += [f"{name}: no question put"]
        if mode == "text" and column["moved"] and "text" in column["asked"]:
            failed += [f"{name}: put again once answered"]
    for line in seen.get("missed") or []:
        column = line.split(":", 1)[0]
        obligation = obligation_of(line)
        obligations[obligation] = obligations.get(obligation, 0) + 1
        stated = column in seen["columns"] and column not in forms.CONTROLS and (
            "axes.role [" in line or "axes.statistical_type [" in line
            # ...and the shape form of a sentence of one word, which the
            # free-text writer misses on some tables (P4-D481 (b)'s second
            # part, owner lane NOTES-b; lane NOTES's repair 2):
            # `forms.published.<form> [free_text.shape_forms]`.
            or "[free_text.shape_forms]" in line
        )
        if stated:
            counts["validate_sentence_misses"] += 1
        else:
            failed += [f"validate misses {line}"]
    return counts, failed, obligations


def items() -> "list[tuple[str, str, str]]":
    """Every (name, table, mode) the KPI reads."""
    return [(f"{table}:{mode}", table, mode) for table in forms.TABLE_FAMILIES for mode in forms.TABLE_MODES[table]]


def price() -> "tuple[list[str], list[str], list[str]]":
    """THE PRICE: the zoo's columns and the goldens' battery columns described as free text for their sentences, by name."""
    import fixtures
    import health_zoo as zoo
    import stage5_battery

    from synthtwin import profile, reading, taxonomy

    said = taxonomy.rendered(taxonomy.EVIDENCE_SENTENCES_AS_TEXT, ())
    notes = {column for kind in NOTE_KINDS for table in zoo.catalogue() for column in table.kinds.get(kind, ())}
    reached: "list[str]" = []
    not_notes: "list[str]" = []
    golden: "list[str]" = []
    with tempfile.TemporaryDirectory() as scratch:
        for table in zoo.catalogue():
            header, rows = table.build(zoo.KPI_ROWS, zoo.seed_of(table))
            # ONLY A TABLE HOLDING A SENTENCE IS DESCRIBED (lane NOTES's repair 1,
            # the measurement made fast): a column none of whose cells is a
            # sentence is never described as free text for its sentences.
            if not any(value and taxonomy.a_sentence(value) for value in {f"{cell}" for row in rows for cell in row}):
                continue
            path = pathlib.Path(scratch) / f"{table.name}{table.suffix}"
            path.write_bytes(table.write(header, rows))
            try:
                document = profile.build_document(
                    reading.read_table(f"{path}"), taxonomy.Settings(), [], top_code=True, five_figures=[],
                    ages_held=[], harbor_year=taxonomy.SAFE_HARBOR_REFERENCE_YEAR, harbor_reasons={},
                    ages_established={},
                )
            finally:
                path.unlink()
            for block in document["columns"]:  # type: ignore[attr-defined]
                if block.get("detection_evidence") == said:
                    reached += [f"{table.name}.{block['name']}"]
                    if f"{block['name']}" not in notes:
                        not_notes += [f"{table.name}.{block['name']}"]
        for label, text in (
            ("step0_table", stage5_battery.step0_table(ROWS)),
            ("every_role_and_joined_table", fixtures.every_role_and_joined_table(ROWS)),
            ("persons_table", stage5_battery._persons_table(ROWS)),
        ):
            path = pathlib.Path(scratch) / f"{label}.csv"
            path.write_text(text, encoding="utf-8", newline="")
            try:
                document = profile.build_document(reading.read_table(f"{path}"), taxonomy.Settings(), [])
            finally:
                path.unlink()
            for block in document["columns"]:  # type: ignore[attr-defined]
                if block.get("detection_evidence") == said:
                    golden += [f"{label}.{block['name']}"]
    return reached, not_notes, golden


def main(argv: "list[str]") -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--kpi", action="store_true", help="print the KPI line for kpi_run")
    parser.add_argument("--only", action="append", default=[], help="a shell pattern over table:mode")
    parser.add_argument("--price", action="store_true", help="the price alone")
    chosen = parser.parse_args(argv)
    value: "dict[str, int]" = {"tables": len(forms.TABLE_FAMILIES), "items": 0, "items_failing": 0}
    for key in SUMS:
        value[key] = 0
    by_obligation: "dict[str, int]" = {}
    ITEMS.parent.mkdir(parents=True, exist_ok=True)
    product = 0.0
    with open(ITEMS, "w", encoding="utf-8", newline="\n") as written, tempfile.TemporaryDirectory() as scratch:
        for name, table, mode in [] if chosen.price else items():
            if chosen.only and not any(fnmatch.fnmatch(name, one) for one in chosen.only):
                continue
            folder = pathlib.Path(scratch) / name.replace(":", "-")
            started = time.monotonic()
            seen = forms.measure(folder, table, mode, ROWS)
            wall = time.monotonic() - started
            counts, failed, obligations = judge(seen)
            value["items"] += 1
            if failed:
                value["items_failing"] += 1
            for key in SUMS:
                value[key] += counts[key]
            for obligation, missed in obligations.items():
                by_obligation[obligation] = by_obligation.get(obligation, 0) + missed
            seconds = float(seen.get("product_seconds") or 0.0)  # type: ignore[arg-type]
            product += seconds
            roles = {column: f"{entry['role']}{'*' if entry['moved'] else ''}" for column, entry in seen["columns"].items()}
            line = (
                f"{name}: {'FAIL ' + '; '.join(failed) if failed else 'PASS'} "
                + " ".join(f"{key}={counts[key]}" for key in SUMS)
                + f" roles={roles} exits profile={seen.get('profile')} answers={seen.get('answers')}"
                f" generate={seen.get('generate')} validate={seen.get('validate')} misses {obligations}"
                f" product {seconds:.1f} s ({seen.get('seconds')}), counting {wall - seconds:.1f} s"
            )
            print(line, flush=True)
            written.write(line + "\n")
            shutil.rmtree(folder, ignore_errors=True)
        if not chosen.only:
            started = time.monotonic()
            reached, not_notes, golden = price()
            value["zoo_columns_reached"] = len(reached)
            value["zoo_columns_not_notes"] = len(not_notes)
            value["golden_columns_reached"] = len(golden)
            line = (
                f"price: {len(reached)} zoo columns described as free text for their sentences "
                f"({'; '.join(reached) or 'none'}); {len(not_notes)} of them no notes ({'; '.join(not_notes) or 'none'}); "
                f"{len(golden)} golden battery columns ({'; '.join(golden) or 'none'}); {time.monotonic() - started:.0f} s"
            )
            print(line, flush=True)
            written.write(line + "\n")
    value["validate_misses_by_obligation"] = dict(sorted(by_obligation.items()))  # type: ignore[assignment]
    detail = (
        f"{value['items']} items over {len(forms.TABLE_FAMILIES)} tables at {ROWS:,} rows, {value['items_failing']} "
        f"failing; the product's own seconds {product:.0f}"
    )
    print(detail)
    if not value["items"] and not chosen.price:
        print(f"no item matches {chosen.only}: nothing was measured")
        return 1
    if chosen.kpi and not chosen.only and not chosen.price:
        kpi_rules.emit("K-HZ-34", value, detail)
    return 1 if value["items_failing"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
