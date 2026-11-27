"""K-HZ-41: the value readers' residuals per item and form at 20,000 rows: real values shown, real twin cells, complete real runs, categories past 89, questions put, and the price (plan P4-D493).

THE KINDS (`tests/value_reader_residual_forms.py`, lane CZ-G), each an
invented look-alike at the owner's table floor, 1,000 people on 20 rows
each: adult age groups under neutral names (`25-44 ... 95+`, `16-24 ...
100+` with nobody under 25, three closed bands, an older cohort, five-year
groups written with the soft hyphen for the dash (LANE CZ-G RULINGS 3, X1),
the strict bound `90-<95` with a hyphen and with `to`, and `25-44 ... 95+`
with one person in twelve written as a stray cell), beside the patient column;
the same groups in Spanish, Portuguese, French, German and Italian; banded
measures that are no ages, truthfully answered `no` (the price); each
person's home written with its hemisphere letters as their own words, one
row a case; remarks holding an age past 89 beside remarks holding an age
under 90 and remarks of scores, amounts with a unit and rooms (the price),
beside the patient column and one row a case; record numbers in two
groups of figures with a run of spaces, a dash after the label, in
brackets, of five figures, and two families half each, one row a case;
telephone numbers parted by ` . ` or `_` and runs of figures with a mark
that prints nothing inside, in remarks many rows share, one row a case.

EACH ITEM is one kind in one mode: nobody answering; the zoo's truthful
answers round by round; and the person question `keep` everywhere with
the forms' columns read as publishing values, the Safe Harbor question
blank (`coded`). Through the real profile, generate (seed 0) and validate,
the table floor on, counted by `value_readers_forms.measure` (the linear
counter, `unanswered_identifier_shapes.count_real(..., linear=True)`).

THE VALUE, summed over the items, for the columns the readers must hold
(`value_reader_residual_forms.HELD`): `real_values_shown`,
`real_twin_cells` (a twin cell holding a placed value whole or one of its
numbers, the counter's needles; a remark of an age of exactly 90, the top
code's own form, is placed with no needle and never counted: batch 4t's
fix round, item 9), `twin_complete_runs` and
`questions_not_put` (unanswered or coded, a held column put no question
offering `identifier`, no Safe Harbor question and no age question), each
failing its item -- but in the coded mode a held column the identifier
question asks, which that mode answers `keep`, is published by the answer
by design and recorded apart (`freed_by_keep_values_shown`,
`freed_by_keep_twin_cells`, never failing); and
`categories_past_89` (a band column whose published levels name more than
one category of 90 or older by the KPI's own reading,
`value_readers_forms.label_reaches_90`), failing; AND THE PRICE, recorded,
never failing: `price_columns_pooled` (a measure column or a control
remark column the first description pools or holds), the measure family's
band columns the age reach reads (`measure_family_read`, by family, at the
unit level), and over the whole zoo (`zoo_columns_newly_reached`) every
catalogue column whose hold, top-code or role the lane's readers change
(the first description with the lane's rules and with them switched off),
by name. One line an item is printed and written to
`synthtwin-kpi/kpi_value_reader_residuals-items.txt` under the system's
temporary folder. `--only` (a shell pattern over `kind:mode`) is for a
mutant's red and never writes the KPI line; `--price` measures the price
alone.

    .venv/bin/python tools/measurements/kpi_value_reader_residuals.py --kpi
"""

import argparse
import contextlib
import fnmatch
import json
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

import value_reader_residual_forms as residual  # noqa: E402
import value_readers_forms as readers  # noqa: E402

ROWS = 20000
MODES = ("unanswered", "truthful", "coded")
ITEMS = pathlib.Path(tempfile.gettempdir()) / "synthtwin-kpi" / "kpi_value_reader_residuals-items.txt"
SUMS = ("real_values_shown", "real_twin_cells", "twin_complete_runs", "questions_not_put", "categories_past_89",
        "price_columns_pooled", "freed_by_keep_values_shown", "freed_by_keep_twin_cells")
FAILING_ON = ("real_values_shown", "real_twin_cells", "twin_complete_runs", "questions_not_put", "categories_past_89")
# The kinds read in every mode; the one-column price item of item 7 is
# recorded apart (`short_names`, a name beside four figures: price first).
KINDS = tuple(kind for kind in residual.KINDS if kind not in (residual.KIND_SHORT_NAMES, residual.KIND_SPLIT_RECORDS))


def _asked(entry: "dict") -> bool:
    for offered in entry.get("asked") or []:
        if "identifier" in offered or offered[-2:] == ["no", "yes"] or "yes" in offered:
            return True
    return False


def judge(kind: str, mode: str, seen: "dict", folder: pathlib.Path) -> "dict[str, int]":
    """One item's counts (see the module's docstring)."""
    counts = {key: 0 for key in SUMS}
    columns = seen.get("columns") or {}
    profile = folder / f"{kind}-profile.json"
    blocks = {}
    if profile.is_file():
        blocks = {f"{c['name']}": c for c in json.loads(profile.read_text(encoding="utf-8"))["columns"]}
    for column in residual.HELD[kind]:
        entry = columns.get(column) or {}
        if mode == "coded" and any("identifier" in offered for offered in entry.get("asked") or []):
            # ...a held column the identifier question asks, answered `keep`
            # in this mode, is published by the answer, by design (an answer
            # restores the description byte for byte; K-HZ-22 reads lane
            # CZ-A2's record numbers unanswered and answered truthfully):
            # recorded, never failing.
            for form in (entry.get("forms") or {}).values():
                counts["freed_by_keep_values_shown"] += int(form.get("shown", 0)) + int(form.get("needles_shown", 0))
                counts["freed_by_keep_twin_cells"] += int(form.get("twin_equal", 0)) + int(form.get("twin_needles", 0))
            continue
        for form in (entry.get("forms") or {}).values():
            counts["real_values_shown"] += int(form.get("shown", 0)) + int(form.get("needles_shown", 0))
            counts["real_twin_cells"] += int(form.get("twin_equal", 0)) + int(form.get("twin_needles", 0))
            counts["twin_complete_runs"] += int(form.get("runs", 0))
        block = blocks.get(column) or {}
        held = block.get("role") in readers.PUBLISHING_NOTHING if hasattr(readers, "PUBLISHING_NOTHING") else False
        if mode != "truthful" and not _asked(entry) and not held and "top_coded" not in block:
            counts["questions_not_put"] += 1
        if column in residual.BAND_COLUMNS and int(entry.get("levels_past_89") or 0) > 1:
            counts["categories_past_89"] += 1
    for column in residual.PRICE.get(kind, ()):
        block = blocks.get(column) or {}
        if "top_coded" in block or block.get("role") in ("identifier", "free_text"):
            counts["price_columns_pooled"] += 1
    return counts


@contextlib.contextmanager
def lane_rules_off():  # type: ignore[no-untyped-def]
    """The lane's rules switched off, for the price: rule A3b, the lettered pairs, the ages inside remarks, the bands of five languages, the telephone marks, the further readings of a cell holding the soft hyphen or a character that prints nothing (`_marks_readings`: LANE CZ-G RULINGS 3) and the tab at an end of two groups, the age names, the two-groups widening, the pairs in degrees, minutes and seconds, the address glued to `IP` and the code written as a float (each the base's reading)."""
    from synthtwin import asking, taxonomy

    saved = {
        (taxonomy, "_age_shaped_groups"): taxonomy._age_shaped_groups,
        (taxonomy, "_a_lettered_pair"): taxonomy._a_lettered_pair,
        (taxonomy, "_an_age_past_89_in_words"): taxonomy._an_age_past_89_in_words,
        (taxonomy, "_BAND_UNITS_ABROAD"): taxonomy._BAND_UNITS_ABROAD,
        (taxonomy, "_TELEPHONE_MARKS"): taxonomy._TELEPHONE_MARKS,
        (taxonomy, "AGE_OWNER_RUN_ONS"): taxonomy.AGE_OWNER_RUN_ONS,
        (asking, "_record_number_groups"): asking._record_number_groups,
        (taxonomy, "_a_dms_pair"): taxonomy._a_dms_pair,
        (taxonomy, "_ADDRESS_GLUED_WORD"): taxonomy._ADDRESS_GLUED_WORD,
        (taxonomy, "_area_figures"): taxonomy._area_figures,
        (taxonomy, "_marks_readings"): taxonomy._marks_readings,
    }
    figures = taxonomy._area_figures
    widened = asking._record_number_groups

    def one_space_only(value: str) -> "tuple[str, str, str] | None":
        # ...the two-groups reader as it read before item 4: one space, no
        # dash after the label, no brackets around the cell, no tab at an end.
        found = widened(value)
        edged = taxonomy.with_plain_marks(value).strip("- ")
        plain = edged.strip()
        if found is None or "  " in plain or "\t " in plain or plain[:1] in "({" or found[0][-1:] == "-":
            return None
        return None if edged[:1] == "\t" or edged[-1:] == "\t" else found

    taxonomy._age_shaped_groups = lambda spans: False  # type: ignore[assignment]
    taxonomy._a_lettered_pair = lambda pieces: False  # type: ignore[assignment]
    taxonomy._an_age_past_89_in_words = lambda body, least=90: False  # type: ignore[assignment]
    taxonomy._BAND_UNITS_ABROAD = ()  # type: ignore[assignment]
    taxonomy._TELEPHONE_MARKS = (" - ", " ", "-", ".", "/", "")  # type: ignore[assignment]
    taxonomy.AGE_OWNER_RUN_ONS = ()  # type: ignore[assignment]
    asking._record_number_groups = one_space_only  # type: ignore[assignment]
    taxonomy._a_dms_pair = lambda body: False  # type: ignore[assignment]
    taxonomy._ADDRESS_GLUED_WORD = "\x00\x00"  # type: ignore[assignment]
    taxonomy._area_figures = lambda text: False if text.strip()[-2:] == ".0" else figures(text)  # type: ignore[assignment]
    taxonomy._marks_readings = lambda text: ()  # type: ignore[assignment]
    try:
        yield
    finally:
        for (module, name), value in saved.items():
            setattr(module, name, value)


def _zoo_decisions() -> "dict[str, str]":
    """Each catalogue column's first description, as the K-HZ-25 driver builds it: its role, Safe Harbor reason and top-code, by name."""
    import health_zoo as zoo

    from synthtwin import profile, reading, taxonomy

    found: "dict[str, str]" = {}
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
                top = json.dumps(block.get("top_coded"), sort_keys=True, default=str) if "top_coded" in block else ""
                found[f"{table.name}.{name}"] = f"{block['role']}|{reasons.get(name, '')}|{top}"
    return found


def zoo_price() -> "list[str]":
    """THE PRICE ON THE ZOO: the catalogue columns whose first description the lane's rules change, by name, with the change."""
    with_rules = _zoo_decisions()
    with lane_rules_off():
        without = _zoo_decisions()
    return [f"{name} ({without.get(name)} -> {with_rules[name]})" for name in sorted(with_rules)
            if with_rules[name] != without.get(name)]


def measure_family() -> "dict[str, int]":
    """The banded measures of the gate's family the age reach reads (`test_value_reader_residuals._MEASURES`, with stray cells and without), by family."""
    from synthtwin import taxonomy

    import test_value_reader_residuals as gate

    read: "dict[str, int]" = {}
    for name, labels in gate._MEASURES.items():
        for strays in (False, True):
            cells = gate._measure_cells(labels, strays)
            if taxonomy.safe_harbor_reach(cells, False, frozenset(), 11) == taxonomy.SAFE_HARBOR_AGES:
                read[name] = read.get(name, 0) + 1
    return read


def main(argv: "list[str]") -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--kpi", action="store_true", help="print the KPI line for kpi_run")
    parser.add_argument("--only", action="append", default=[], help="a shell pattern over kind:mode")
    parser.add_argument("--price", action="store_true", help="the price alone")
    chosen = parser.parse_args(argv)
    value: "dict[str, object]" = {"kinds": len(KINDS), "items": 0, "items_failing": 0}
    for key in SUMS:
        value[key] = 0
    ITEMS.parent.mkdir(parents=True, exist_ok=True)
    product = 0.0
    with open(ITEMS, "w", encoding="utf-8", newline="\n") as written, tempfile.TemporaryDirectory() as scratch:
        for kind in [] if chosen.price else KINDS:
            for mode in MODES:
                name = f"{kind}:{mode}"
                if chosen.only and not any(fnmatch.fnmatch(name, one) for one in chosen.only):
                    continue
                folder = pathlib.Path(scratch) / name.replace(":", "-")
                started = time.monotonic()
                with residual.registered():
                    seen = readers.measure(folder, kind, ROWS, mode, seed=residual.SEED)
                counts = judge(kind, mode, seen, folder)
                wall = time.monotonic() - started
                value["items"] = int(value["items"]) + 1  # type: ignore[call-overload]
                failing = (seen.get("profile"), seen.get("generate")) != (0, 0) or any(counts[key] for key in FAILING_ON)
                if failing:
                    value["items_failing"] = int(value["items_failing"]) + 1  # type: ignore[call-overload]
                for key in SUMS:
                    value[key] = int(value[key]) + counts[key]  # type: ignore[call-overload]
                seconds = float(seen.get("product_seconds") or 0.0)
                product += seconds
                line = (
                    f"{name}: {'FAIL' if failing else 'PASS'} " + " ".join(f"{key}={counts[key]}" for key in SUMS)
                    + f" exits profile={seen.get('profile')} generate={seen.get('generate')} validate={seen.get('validate')}"
                    f" product {seconds:.1f} s (profile {seen.get('profile_seconds')}, generate {seen.get('generate_seconds')},"
                    f" validate {seen.get('validate_seconds')}), counting {wall - seconds:.1f} s"
                )
                print(line, flush=True)
                written.write(line + "\n")
                # ...each item's line kept as it is written, so a run stopped
                # part-way leaves the items it read.
                written.flush()
                shutil.rmtree(folder, ignore_errors=True)
        if not chosen.only:
            started = time.monotonic()
            family = measure_family()
            value["measure_family_read"] = sum(family.values())
            value["measure_family_read_named"] = ", ".join(sorted(family)) or "none"
            changed = zoo_price()
            value["zoo_columns_newly_reached"] = len(changed)
            value["zoo_columns_newly_reached_named"] = "; ".join(changed) or "none"
            line = (f"price: the measure family read {family or 'none'}; zoo columns the lane's rules change "
                    f"{len(changed)} ({'; '.join(changed) or 'none'}); {time.monotonic() - started:.0f} s")
            print(line, flush=True)
            written.write(line + "\n")
            written.flush()
    detail = (f"{value['items']} items over {len(KINDS)} kinds at {ROWS:,} rows, {value['items_failing']} failing; "
              f"the product's own seconds {product:.0f}")
    print(detail)
    if not value["items"] and not chosen.price:
        print(f"no item matches {chosen.only}: nothing was measured")
        return 1
    if chosen.kpi and not chosen.only and not chosen.price:
        kpi_rules.emit("K-HZ-41", value, detail)
    return 1 if value["items_failing"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
