"""K-HZ-14: the Safe Harbor identifier forms the zoo did not test before, per form at 600 and 20,000 rows (plan P4-D445).

THE FORMS (`tests/safe_harbor_forms.py`, lane CZ-A): social security
numbers dashed and undashed in one column, a few spaced or with an en
dash, about one in fifty with a trailing capital letter; a payer's member
number in more than ten formats; a name and a record number in one cell; a
relative's social security number beside the patient's under neutral
names; opaque tokens of 32 and 64 hexadecimal and 22 and 24 base64
characters; device lot and serial numbers and UDIs carrying a serial (21)
or a lot (10); accession numbers in three layouts and ISBT 128 blood-unit
numbers; identifiers of 16 and 19 figures. Each table holds 1,000 people
at 20,000 rows (20 rows each, an identifier's thousand values inside the
reach of a set of categories) and 100 at 600 rows, beside a closed list of
codes of 6 to 15 characters where the form allows one. AND, BESIDE THE
FORMS, A VARIANT COLUMN for each reading lane CZ-A's repair 1 added
(social security numbers with another dash or space and a letter of
either case; base64 keys of 24, 43 and 44 characters; a name beside a
labelled number; UDIs in square brackets; accession numbers in two
undashed layouts; unit numbers with their check character; numbers of 12
to 18 figures), and four closed lists, three of which the forms' rule
holds until `no` (codes of 32 small hexadecimal characters, of three
capitals, two figures, a dash and four figures, and of 16 to 18 figures:
the price) and one it spares (labels with a code of five figures).
AND THE DRIVER'S OWN FORM (`safe_harbor_forms.KIND_NAME_ROWS`, Codex's
review of batch 4q, item 1), which the zoo's catalogue does not hold: a
name beside a record number of its own on every row, the numbers running
on from one another, 1,000 people of 20 records at 20,000 rows.

EACH ITEM is one form at one size in one mode (`safe_harbor_forms.MODES`),
and the long identifiers written as an Excel workbook of text cells too
(`long_ids_book`, three modes), and of NUMBER cells, each in a float's own
spelling, the exponent form among them (`long_ids_numbers`, three modes;
lane CZ-A's repair 2, the verify's item 2):
nobody answering; the zoo's truthful answers round by round; the form's
columns answered a reading that publishes values (`code`, `keep` or
`measurement`) with their Safe Harbor question left blank; and every Safe
Harbor question answered `no`. Through the real profile, generate (seed 0)
and validate, the table floor on at 20,000 rows; the 600-row runs are a
test size under it (the library's switch). Every count reads by the
counter LINEAR IN THE DATA (`unanswered_identifier_shapes.count_real(...,
linear=True)`: each real value and its fragments in two lookups, each text
and each different twin cell scanned once), over the description, its
summary and the questions file of every round and the screen.

THE VALUE, summed over the items: `real_values_shown` (a real value of an
identifier column whole in any of those texts; target 0), `real_twin_cells`
(twin cells equal to a real value; target 0), `twin_complete_tokens` (twin
cells holding a COMPLETE real record token inside a wider cell -- a run of
five figures or more of a real value, standing whole in a twin cell of two
words or more however it is glued there: as its own word, after a label,
before a letter, joined by a code's marks (`safe_harbor_forms.
complete_tokens`); target 0, and it FAILS its item: Codex's review of batch
4q, item 1, 46 such cells of a name beside a record number of its own on
every row, and its fix round 2, 46, 46 and 47 such cells of the number
glued to its label or before a letter, where the fragments below are
recorded and fail nothing), `questions_not_put` (an identifier column of an unanswered
run put no question offering `identifier` and no Safe Harbor question;
target 0), `identifier_columns_published_unanswered_or_coded` (an
identifier column read as anything but a held identifier in the
unanswered and coded modes; target 0), `false_alarms_freed_by_no` (a
closed list of codes beside a form held unanswered and freed by `no`, at
20,000 rows: the 600-row runs are a test size under the owner's table
floor, the orchestrator's LANE I4m RULINGS 18), and, recorded apart, the
fragments (`description_fragments`, `twin_fragments`: a run of five
letters or figures of a real value, or the text every real value opens
with), and THE CHANCE OF A FIGURE RUN once a column (lane CZ-A's repair
1, the statistics skeptic's item 3): at 20,000 rows, the different twin
values of each identifier column, every mode's together, carrying a real
value's run of five figures or more -- every run of it, inside a longer
run too (`safe_harbor_forms.carrying_runs`, lane CZ-A's repair 2, Codex
item 4) -- (`twin_values_carrying_a_real_figure_run`), beside the mean of what they
carry of `safe_harbor_forms.CONTROL_TABLES` tables of the form at other
seeds, which the twin never read (`twin_values_by_chance_mean`), and the
columns whose count no control table reaches
(`columns_past_every_control`), each column's line, with how many
controls reach it, printed; and the items run and failing. One line
an item -- the counts, the product's seconds (profile, generate and
validate) apart from the counting -- is printed and written to
`synthtwin-kpi/kpi_safe_harbor_forms-items.txt` under the system's
temporary folder. `--only` (a shell pattern over `form:rows:mode`) is for a
mutant's red and never writes the KPI line; `--rows` keeps one size.

    .venv/bin/python tools/measurements/kpi_safe_harbor_forms.py --kpi
    .venv/bin/python tools/measurements/kpi_safe_harbor_forms.py --only 'member_numbers:20000:*'
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

import safe_harbor_forms as forms  # noqa: E402

SIZES = (600, 20000)
ITEMS = pathlib.Path(tempfile.gettempdir()) / "synthtwin-kpi" / "kpi_safe_harbor_forms-items.txt"
SUMS = (
    "real_values_shown", "real_twin_cells", "twin_complete_tokens", "questions_not_put",
    "identifier_columns_published_unanswered_or_coded", "false_alarms_freed_by_no",
    "description_fragments", "twin_fragments",
)
# The keys an item fails on: the rest are recorded (the fragments; the
# chance of a figure run is read once a column, `chance_lines`).
FAILING_ON = (
    "real_values_shown", "real_twin_cells", "twin_complete_tokens", "questions_not_put",
    "identifier_columns_published_unanswered_or_coded",
)


def judge(seen: "dict") -> "dict[str, int]":
    """One item's counts: what is real in what the commands wrote, the questions put, the false alarms freed."""
    counts = {key: 0 for key in SUMS}
    kind = f"{seen['kind']}"
    mode = f"{seen['mode']}"
    columns = seen.get("columns") or {}
    for column in forms.IDENTIFIERS[kind]:
        counted = columns.get(column) or {}
        if mode != "no":
            counts["real_values_shown"] += int(counted.get("description_values", 0))
            counts["real_twin_cells"] += int(counted.get("twin_cells_equal", 0))
            counts["twin_complete_tokens"] += int(counted.get("twin_complete_tokens", 0))
        counts["description_fragments"] += int(counted.get("description_fragments", 0))
        counts["twin_fragments"] += int(counted.get("twin_fragments", 0))
        offered = counted.get("asked") or []
        if mode == "unanswered" and not any("identifier" in one or one == ["no", "yes"] for one in offered):
            counts["questions_not_put"] += 1
        if mode in ("unanswered", "coded") and counted.get("role") != "identifier":
            counts["identifier_columns_published_unanswered_or_coded"] += 1
    if mode == "no" and int(seen["rows"]) >= forms.zoo.KPI_ROWS:
        # ...a closed list of codes beside the form that the Safe Harbor
        # question held (put it, read as a held identifier unanswered) and
        # its `no` freed: a false alarm of the forms' rule, at 20,000 rows.
        # One another rule holds and another answer frees is not the
        # forms'.
        for column in forms.CODES_BESIDE.get(kind, ()):
            counted = columns.get(column) or {}
            if (
                ["no", "yes"] in (counted.get("asked") or [])
                and counted.get("role_unanswered") == "identifier"
                and counted.get("role") != "identifier"
            ):
                counts["false_alarms_freed_by_no"] += 1
    return counts


# The workbook variants of the long identifiers (the forms' eighth kind
# written as an Excel workbook of text cells, and -- lane CZ-A's repair 2,
# the verify's item 2 -- of NUMBER cells, the long identifiers in a float's
# own spelling, the exponent form among them), in the modes that publish.
BOOK_MODES = ("unanswered", "truthful", "coded")


def items(rows: "tuple[int, ...]") -> "list[tuple[str, str, int, str, bool, bool]]":
    found = [
        (f"{kind}:{size}:{mode}", kind, size, mode, False, False)
        for size in rows for kind in forms.DRIVER_KINDS for mode in forms.MODES
    ]
    return found + [
        (f"{forms.KIND_LONG}_book:{size}:{mode}", forms.KIND_LONG, size, mode, True, False)
        for size in rows for mode in BOOK_MODES
    ] + [
        (f"{forms.KIND_LONG}_numbers:{size}:{mode}", forms.KIND_LONG, size, mode, True, True)
        for size in rows for mode in BOOK_MODES
    ]


def chance_lines(collected: "dict[tuple[str, str, str], set[str]]", value: "dict[str, object]") -> "list[str]":
    """THE CHANCE OF A FIGURE RUN once a column at 20,000 rows: each column's line, and the sums into ``value``."""
    carrying = 0
    by_chance = 0.0
    past = 0
    lines: "list[str]" = []
    for (family, kind, column), values in sorted(collected.items()):
        found = forms.chance_of_runs(kind, column, forms.zoo.KPI_ROWS, sorted(values))
        carrying += int(found["carrying"])  # type: ignore[call-overload]
        by_chance += float(found["control_mean"])  # type: ignore[arg-type]
        if found["carrying"] and not found["controls_reaching"]:
            past += 1
        lines += [
            f"chance {family}.{column}: {found['carrying']} of {found['twin_values']} different twin values hold a "
            f"run of five figures or more of a real value, against a mean of {found['control_mean']} over "
            f"{forms.CONTROL_TABLES} unseen tables ({found['controls_reaching']} of {forms.CONTROL_TABLES} as high; "
            f"each {found['controls']})"
        ]
    value["twin_values_carrying_a_real_figure_run"] = carrying
    value["twin_values_by_chance_mean"] = round(by_chance, 2)
    value["columns_past_every_control"] = past
    return lines


def main(argv: "list[str]") -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--kpi", action="store_true", help="print the KPI line for kpi_run")
    parser.add_argument("--only", action="append", default=[], help="a shell pattern over form:rows:mode")
    parser.add_argument("--rows", type=int, action="append", default=[], help="one size only")
    chosen = parser.parse_args(argv)
    sizes = tuple(chosen.rows) or SIZES
    value: "dict[str, int]" = {"forms": len(forms.KINDS), "items": 0, "items_failing": 0}
    for key in SUMS:
        value[key] = 0
    ITEMS.parent.mkdir(parents=True, exist_ok=True)
    product = 0.0
    collected: "dict[tuple[str, str, str], set[str]]" = {}
    with open(ITEMS, "w", encoding="utf-8", newline="\n") as written, tempfile.TemporaryDirectory() as scratch:
        for name, kind, size, mode, book, numbers in items(sizes):
            if chosen.only and not any(fnmatch.fnmatch(name, one) for one in chosen.only):
                continue
            folder = pathlib.Path(scratch) / name.replace(":", "-")
            started = time.monotonic()
            seen = forms.measure(folder, kind, size, mode, book=book, numbers=numbers)
            wall = time.monotonic() - started
            counts = judge(seen)
            value["items"] += 1
            steps = (seen.get("profile"), seen.get("generate"))
            failing = steps != (0, 0) or any(counts[key] for key in FAILING_ON)
            if failing:
                value["items_failing"] += 1
            for key in SUMS:
                value[key] += counts[key]
            seconds = float(seen.get("product_seconds") or 0.0)
            product += seconds
            line = (
                f"{name}: {'FAIL' if failing else 'PASS'} "
                + " ".join(f"{key}={counts[key]}" for key in SUMS)
                + f" exits profile={seen.get('profile')} generate={seen.get('generate')} "
                f"validate={seen.get('validate')} product {seconds:.1f} s (profile {seen.get('profile_seconds')}, "
                f"generate {seen.get('generate_seconds')}, validate {seen.get('validate_seconds')}), "
                f"counting {wall - seconds:.1f} s"
            )
            print(line, flush=True)
            written.write(line + "\n")
            shutil.rmtree(folder, ignore_errors=True)
            if size >= forms.zoo.KPI_ROWS and mode != "no":
                family = name.split(":")[0]
                for column, values in (seen.get("twin_values") or {}).items():
                    collected.setdefault((family, kind, column), set()).update(values)
        for line in chance_lines(collected, value) if collected else []:
            print(line, flush=True)
            written.write(line + "\n")
    detail = (
        f"{value['items']} items over {len(forms.KINDS)} forms at {', '.join(f'{size:,}' for size in sizes)} rows, "
        f"{value['items_failing']} failing; the product's own seconds {product:.0f}"
    )
    print(detail)
    if not value["items"]:
        print(f"no item matches {chosen.only}: nothing was measured")
        return 1
    if chosen.kpi and not chosen.only:
        kpi_rules.emit("K-HZ-14", value, detail)
    return 1 if value["items_failing"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
