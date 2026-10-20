"""What a description publishes that fewer than eleven people hold (plan P4-D406).

Shared by `tests/test_stage4_counted_in_persons.py` and
`tools/measurements/kpi_counted_in_persons.py` (ledger K-S3-65), so the gate
and the ledger count the same way.

THE COUNT, made from the table and the description alone and written apart
from the product's own (`profile._counted_in_subjects`,
`profile._layouts_in_subjects`, `taxonomy.with_census_in_people`), so a slip
in one is seen by the other. The SUBJECT columns are the declared person
columns (`settings.person_columns`) and the candidates of an open person
question (the columns the questions file asks it of), each that repeats;
one of fewer than eleven different values counts only the columns ATTACHED
to it. For every other column and each subject column:

- each different value of the column, folded, is held by some rows and by
  some different subjects;
- the column is ATTACHED to the subject where at most one in ten of the
  rows of a subject met again holds another value than the one it was first
  met with;
- a value is IN THE RULE'S SCOPE where one to ten subjects hold it and the
  column is attached or holds dates or times of day, or at least eleven
  rows hold it and it is published off the rungs (the points along the
  range and the tails' boundaries, which the floor publishes whatever the
  rows at the point);
- a value is PUBLISHED where its column's block in the description carries
  it: a text leaf or a mapping key equal to it folded, a word of a sentence
  equal to it, a number leaf (not a count) equal to its reading as a
  number, or a date leaf equal to its reading in the block's date format;
- a written FORM the block names (`shape_forms`, or a record number's
  `layout_forms`) is published, and in scope where one to ten subjects
  wear it;
- the REMAINDER -- the present rows reading as no published value -- and
  the column's present rows as a whole are in scope, where the block
  publishes statistics over them (any role but a record number's), when
  eleven rows or more and one to ten subjects hold them;
- a declared person column's census of rows a person publishes no entry
  of one to ten people that is not the even spread of a pool of eleven
  people or more.

`few` is the number of values, forms and groups in scope and published,
under any subject column (the KPI's target, 0); `literal` the number of
published values one to ten subjects hold whatever their rows and
attachment (recorded beside it, never failed: the measurements a patient
holds on one row each, which the floor judges in rows on a table of one row
a person too).
"""

from __future__ import annotations

import csv
import json
import pathlib
import random

from synthtwin import parsing

FLOOR = 11

# Number leaves under these keys are counts, shares or sizes, never values.
_COUNTS = ("count", "rows", "n_", "share", "width", "length",
           "position", "ceiling", "distance", "std", "mean", "skew",
           "kurtosis", "digits", "suppressed", "first", "last", "bins")
# Entries that publish no value of the column at all.
_NOTHING = ("missing", "withheld", "occurrences", "widths")
# The points along a range and the tails' boundaries.
_RUNGS = ("percentiles", "percentiles_between", "date_percentiles",
            "clock_percentiles", "boundary")


def _number(text: str) -> "float | None":
    try:
        return parsing.parse_number(text)
    except (TypeError, ValueError):
        return None


def leaves(block: "dict[str, object]", rungs: bool = True) -> "tuple[set[str], set[float]]":
    """Every text and number a column block publishes, texts folded (``rungs``: its points too)."""
    texts: "set[str]" = set()
    numbers: "set[float]" = set()
    stack: "list[tuple[str, object]]" = [(key, block[key]) for key in block if key != "name"]
    while stack:
        key, leaf = stack.pop()
        if any(word in key for word in _NOTHING):
            continue
        if not rungs and any(part in _RUNGS for part in key.split(".")):
            continue
        if isinstance(leaf, bool) or leaf is None:
            continue
        if isinstance(leaf, dict):
            for inner, value in leaf.items():
                texts.add(parsing.folded(f"{inner}"))
                stack += [(f"{key}.{inner}", value)]
        elif isinstance(leaf, list):
            stack += [(key, item) for item in leaf]
        elif isinstance(leaf, (int, float)):
            own = key.split(".")[-1]
            field = own[:1].islower() and all(c.islower() or c.isdigit() or c == "_" for c in own)
            if own != "percent" and field and not any(word in own for word in _COUNTS):
                numbers.add(float(leaf))
        elif isinstance(leaf, str):
            texts.add(parsing.folded(leaf))
            for word in leaf.split():
                texts.add(parsing.folded(word.strip(",.;:()[]{}'\"`")))
    return texts, numbers


def _figures(text: str) -> "float | None":
    runs = "".join(c if c.isdigit() else " " for c in text).split()
    if not runs:
        return None
    return float(int(max(runs, key=len)))


def is_published(value: str, block: "dict[str, object]",
                 seen: "tuple[set[str], set[float]]") -> bool:
    """Whether a column block carries one value of the column, by any reading."""
    texts, numbers = seen
    folded = parsing.folded(value)
    if folded in texts:
        return True
    number = _number(value)
    if number is None:
        number = _figures(value)
    if number is not None and number in numbers:
        return True
    shown = block.get("format")
    if block.get("role") == "datetime" and isinstance(shown, str):
        read = parsing.parse_datetime(value, shown)
        if read is not None and parsing.folded(read[0]) in texts:
            return True
    return False


def held_by(values: "list[str]", subjects: "list[str]") -> "tuple[dict[str, set[str]], dict[str, int], bool]":
    """Each folded value's subjects and rows, and whether the column is attached."""
    holders: "dict[str, set[str]]" = {}
    rows: "dict[str, int]" = {}
    first: "dict[str, str]" = {}
    again = 0
    other = 0
    for value, subject in zip(values, subjects):
        folded = parsing.folded(value)
        if not folded:
            continue
        holders.setdefault(folded, set()).add(subject)
        rows[folded] = rows.get(folded, 0) + 1
        if subject in first:
            again += 1
            other += first[subject] != folded
        else:
            first[subject] = folded
    return holders, rows, again > 0 and other * 10 <= again


def table_columns(path: pathlib.Path, encoding: str = "utf-8-sig",
                  delimiter: str = ",") -> "tuple[list[str], list[list[str]]]":
    """A CSV table's names and columns, as text, read as its description says it is written."""
    with open(path, encoding=encoding, newline="") as handle:
        rows = list(csv.reader(handle, delimiter=delimiter))
    names = rows[0]
    return names, [[row[place] if place < len(row) else "" for row in rows[1:]]
                   for place in range(len(names))]


def _written(described: "dict[str, object]") -> "tuple[str, str]":
    source = described["source"]
    assert isinstance(source, dict)
    encoding = f"{source['encoding']}"
    if encoding in ("utf-8", "ascii"):
        encoding = "utf-8-sig"
    dialect = source["dialect"]
    delimiter = dialect.get("delimiter", ",") if isinstance(dialect, dict) else ","
    return encoding, f"{delimiter}" or ","


def repeats(cells: "list[str]") -> bool:
    """A subject column the count uses: two present cells hold the same text."""
    present = [cell for cell in cells if parsing.folded(cell)]
    return len(set(present)) < len(present)


def counts_people(cells: "list[str]") -> bool:
    """A subject column holding at least FLOOR different values."""
    return len({cell for cell in cells if parsing.folded(cell)}) >= FLOOR


def subject_columns(described: "dict[str, object]",
                    questions: "dict[str, object] | None") -> "list[str]":
    """The declared person columns and the open person question's candidates."""
    settings = described["settings"]
    assert isinstance(settings, dict)
    found = list(settings["person_columns"])
    for entry in (questions or {}).get("asked", []):
        offered = [choice["answer"] for choice in entry["answers_you_can_give"]]
        if ("identifier" in offered and "keep" in offered
                and entry.get("your_answer", "") == ""
                and "the people the rows are about" in json.dumps(entry)
                and entry["column"] not in found):
            found += [entry["column"]]
    return found


def _layout_of(cell: str, convention: str, named: "dict[str, int]") -> str:
    layout = parsing.layout_form(cell, convention)
    while layout and layout not in named and parsing.layout_fill(layout) >= 2:
        layout = parsing.layout_shallower(layout)
    return layout if layout in named else ""


def _forms_of(block: "dict[str, object]", values: "list[str]") -> "list[str]":
    """The published form each cell wears, or "" (record-number layouts or shape forms)."""
    if isinstance(block.get("layout_forms"), dict):
        named = {k: v for k, v in block["layout_forms"].items() if k != "(withheld)"}
        present = [v for v in values if parsing.folded(v)]
        convention = parsing.layout_convention(present)
        return [_layout_of(v, convention, named) if parsing.folded(v) else "" for v in values]
    forms = block.get("shape_forms")
    if isinstance(forms, dict):
        named = {k: v for k, v in forms.items() if k != "(withheld)"}
        found = []
        for value in values:
            form = parsing.census_form(value, named) if parsing.folded(value) else ""
            found += [form if form in named else ""]
        return found
    return ["" for _value in values]


def census_few(block: "dict[str, object]", cells: "list[str]") -> int:
    """Entries of a person column's census that name one to ten people.

    The real census counts how many people have each number of rows. A
    published entry under eleven stands only as the even spread of a pool:
    at most two such entries, a row apart, and the people outside the real
    entries published exactly at eleven or more number at least eleven.
    """
    census = block.get("n_distinct_by_occurrences")
    if not isinstance(census, dict) or not census:
        return 0
    rows: "dict[str, int]" = {}
    for cell in cells:
        if parsing.folded(cell):
            rows[cell] = rows.get(cell, 0) + 1
    real: "dict[int, int]" = {}
    for count in rows.values():
        real[count] = real.get(count, 0) + 1
    shown = {int(key): int(value) for key, value in census.items()}
    small = sorted(key for key, value in shown.items() if 1 <= value < FLOOR)
    if not small:
        return 0
    exact = sum(value for key, value in shown.items()
                if value >= FLOOR and real.get(key, 0) == value)
    pool = len(rows) - exact
    if len(small) <= 2 and small[-1] - small[0] <= 1 and pool >= FLOOR:
        return 0
    return len(small)


def count(names: "list[str]", columns: "list[list[str]]",
          described: "dict[str, object]", subjects: "list[str]") -> "dict[str, object]":
    """Published values, forms and groups of the other columns held by one to ten people."""
    blocks = {block["name"]: block for block in described["columns"]}
    settings = described["settings"]
    declared = list(settings["person_columns"]) if isinstance(settings, dict) else []
    few = 0
    literal = 0
    named: "list[str]" = []
    for name in subjects:
        if name in declared and name in blocks:
            found = census_few(blocks[name], columns[names.index(name)])
            few += found
            if found:
                named += [f"{name}=census"]
    for name, values in zip(names, columns):
        if name in subjects or name not in blocks:
            continue
        block = blocks[name]
        dated = block.get("role") in ("datetime", "time_of_day")
        statistics = block.get("role") != "identifier"
        seen = leaves(block)
        plain = leaves(block, rungs=False)
        spelled: "dict[str, str]" = {}
        for value in values:
            spelled.setdefault(parsing.folded(value), value)
        forms = _forms_of(block, values)
        remainder = [value if parsing.folded(value) and not is_published(value, block, seen)
                     else "" for value in values]
        in_scope: "set[str]" = set()
        any_few: "set[str]" = set()
        groups: "set[str]" = set()
        for subject in subjects:
            people = columns[names.index(subject)]
            holders, rows, attached = held_by(values, people)
            enough = counts_people(people)
            if not enough and not attached and not dated:
                continue
            for value, who in holders.items():
                if len(who) < FLOOR:
                    any_few.add(value)
                    if (not enough or attached or dated
                            or (rows[value] >= FLOOR
                                and is_published(spelled[value], block, plain))):
                        in_scope.add(value)
            form_holders, _rows, _attached = held_by(forms, people)
            for form, who in form_holders.items():
                if len(who) < FLOOR and (enough or attached or statistics):
                    groups.add(f"form {form}")
            if not enough or not statistics:
                continue
            for label, cells in (("remainder", remainder), ("present", values)):
                group_holders, group_rows, _attached = held_by(
                    ["x" if parsing.folded(cell) else "" for cell in cells], people)
                if "x" in group_holders and len(group_holders["x"]) < FLOOR \
                        and group_rows["x"] >= FLOOR:
                    groups.add(label)
        for value in sorted(any_few):
            if not is_published(spelled[value], block, seen):
                continue
            literal += 1
            if value in in_scope:
                few += 1
                named += [f"{name}={spelled[value]}"]
        few += len(groups)
        named += [f"{name}:{group}" for group in sorted(groups)]
    return {"few": few, "literal": literal, "named": named}


def count_files(table: pathlib.Path, folder: pathlib.Path) -> "dict[str, object]":
    """`count` over a table and the description and questions profile wrote beside it."""
    stem = table.name[: -len(".csv")]
    described = json.loads((folder / f"{stem}-profile.json").read_text(encoding="utf-8"))
    asked = folder / f"{stem}-questions.json"
    questions = json.loads(asked.read_text(encoding="utf-8")) if asked.exists() else None
    names, columns = table_columns(table, *_written(described))
    subjects = [name for name in subject_columns(described, questions)
                if name in names and repeats(columns[names.index(name)])]
    found = count(names, columns, described, subjects)
    found["subjects"] = subjects
    return found


# -- the gate's own tables, shared with the KPI driver ----------------------


def two_candidates(rows: int) -> str:
    """`site` North stands on five visit codes only, beside twenty patients and more."""
    draw = random.Random(7)
    lines = ["patient,visit,site,value"]
    for _row in range(rows):
        person = draw.randrange(44)
        if draw.random() < 0.15:
            visit = draw.randrange(5)
            site = "North"
        else:
            visit = 5 + draw.randrange(25)
            site = ("South", "East")[draw.randrange(2)]
        lines += [f"REC{20000000 + 7 * person:08d},V{100 + visit:03d},{site},"
                  f"{draw.uniform(3, 150):.1f}"]
    return "\n".join(lines) + "\n"


def site_table(rows: int) -> str:
    """120 declared patients; `site` C on 15 rows of three of them, B beside fifty."""
    draw = random.Random(9)
    lines = ["patient,site,value"]
    for place in range(rows):
        person = place % 120
        if person < 3 and (place // 120) % 2 == 0:
            site = "C"
        elif person < 50:
            site = "B"
        else:
            site = "A"
        lines += [f"REC{30000000 + 11 * person:08d},{site},{draw.uniform(3, 150):.1f}"]
    return "\n".join(lines) + "\n"


def published_values(cells: "list[str]", block: "dict[str, object]") -> "set[str]":
    """The different values of a column, folded, that its block publishes."""
    seen = leaves(block)
    spelled: "dict[str, str]" = {}
    for cell in cells:
        spelled.setdefault(parsing.folded(cell), cell)
    return {folded for folded, cell in spelled.items()
            if folded and is_published(cell, block, seen)}


def withheld_values(table: pathlib.Path, ruled: pathlib.Path, plain: pathlib.Path) -> int:
    """Values the count in people withholds that the row floor alone publishes.

    ``ruled`` and ``plain`` hold the table's description made with the count
    and without it; the subject columns themselves are left out.
    """
    stem = table.name[: -len(".csv")]
    on = json.loads((ruled / f"{stem}-profile.json").read_text(encoding="utf-8"))
    off = json.loads((plain / f"{stem}-profile.json").read_text(encoding="utf-8"))
    asked = ruled / f"{stem}-questions.json"
    questions = json.loads(asked.read_text(encoding="utf-8")) if asked.exists() else None
    names, columns = table_columns(table, *_written(on))
    subjects = [name for name in subject_columns(on, questions)
                if name in names and repeats(columns[names.index(name)])]
    blocks_on = {block["name"]: block for block in on["columns"]}
    blocks_off = {block["name"]: block for block in off["columns"]}
    lost = 0
    for name, cells in zip(names, columns):
        if name in subjects or name not in blocks_on or name not in blocks_off:
            continue
        lost += len(published_values(cells, blocks_off[name])
                    - published_values(cells, blocks_on[name]))
    return lost


# -- the first repair's tables (skeptic 1 of lane HX2) ----------------------


def two_candidates_reversed(rows: int) -> str:
    """`two_candidates` with its two candidate columns in the other order."""
    lines = two_candidates(rows).splitlines()
    turned = []
    for line in lines:
        patient, visit, rest = line.split(",", 2)
        turned += [f"{visit},{patient},{rest}"]
    return "\n".join(turned) + "\n"


def remainder_table(rows: int) -> str:
    """150 declared patients; `site` North and South, and rare sites three patients visit.

    Each rare site stands on too few rows to be named, so the floor merges
    them into one remainder of more than eleven rows -- held by three
    patients.
    """
    draw = random.Random(21)
    lines = ["patient,site,value"]
    for _row in range(rows):
        person = draw.randrange(150)
        if person in (7, 16, 25) and draw.random() < 0.5:
            site = f"Rare{draw.randrange(12)}"
        else:
            site = ("North", "South")[draw.randrange(2)]
        lines += [f"REC{50000000 + 3 * person:08d},{site},{draw.uniform(3, 150):.1f}"]
    return "\n".join(lines) + "\n"


def sparse_table(rows: int) -> str:
    """150 declared patients; `dose` written on the rows of two of them only, fifteen values."""
    draw = random.Random(23)
    lines = ["patient,dose,value"]
    written = 0
    for _row in range(rows):
        person = draw.randrange(150)
        dose = ""
        if person in (4, 9):
            dose = f"{1 + written % 15}"
            written += 1
        lines += [f"REC{60000000 + 3 * person:08d},{dose},{draw.uniform(3, 150):.1f}"]
    return "\n".join(lines) + "\n"


def height_table(differing: float) -> str:
    """150 declared patients on four rows each; `height` one value a patient.

    ``differing`` is the share of a patient's later rows written with
    another height: nought keeps the column attached to the patient, a
    quarter does not.
    """
    draw = random.Random(29)
    heights = [f"{draw.uniform(150, 199):.1f}" for _person in range(150)]
    lines = ["patient,height,value"]
    for place in range(600):
        person = place % 150
        height = heights[person]
        if place >= 150 and draw.random() < differing:
            height = f"{draw.uniform(150, 199):.1f}"
        lines += [f"REC{70000000 + 3 * person:08d},{height},{draw.uniform(3, 150):.1f}"]
    return "\n".join(lines) + "\n"


def visit_table(rows: int, written: str) -> str:
    """150 declared patients; `seen` a visit date over eight years, no date on eleven rows.

    ``written`` is `iso` (2019-04-17) or `us` (04/17/2019); the description
    publishes its dates as ISO either way, so a US cell is the published
    date only read again in the block's format.
    """
    draw = random.Random(31)
    lines = ["patient,seen,at,value"]
    for _row in range(rows):
        person = draw.randrange(150)
        year, month, day = draw.randint(2015, 2022), draw.randint(1, 12), draw.randint(1, 28)
        seen = (f"{year}-{month:02d}-{day:02d}" if written == "iso"
                else f"{month:02d}/{day:02d}/{year}")
        at = f"{draw.randint(0, 23):02d}:{draw.randint(0, 59):02d}"
        lines += [f"REC{80000000 + 3 * person:08d},{seen},{at},{draw.uniform(3, 150):.1f}"]
    return "\n".join(lines) + "\n"


def census_table(small: bool) -> str:
    """Declared patients on one to five rows; every rows-a-person group has eleven people or more.

    ``small`` adds three patients on nine rows each: a group of three.
    """
    draw = random.Random(37)
    sizes = [1] * 30 + [2] * 40 + [3] * 25 + [4] * 20 + [5] * 15
    if small:
        sizes += [9] * 3
    lines = ["patient,value"]
    for person, size in enumerate(sizes):
        for _row in range(size):
            lines += [f"REC{90000000 + 3 * person:08d},{draw.uniform(3, 150):.1f}"]
    return "\n".join(lines) + "\n"
