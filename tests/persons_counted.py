"""What a description publishes that fewer than eleven people hold (plan P4-D406).

Shared by `tests/test_stage4_counted_in_persons.py` and
`tools/measurements/kpi_counted_in_persons.py` (ledger K-S3-65), so the gate
and the ledger count the same way.

THE COUNT, made from the table and the description alone and written apart
from the product's own (`profile._counted_in_subjects`), so a slip in one is
seen by the other. For every column but the subject columns -- the declared
person columns (`settings.person_columns`) and the candidates of an open
person question (the columns the questions file asks it of) -- and for each
subject column:

- each different value of the column, folded, is held by some rows and by
  some different subjects;
- the column is ATTACHED to the subject where at most one in ten of the
  rows of a subject met again holds another value than the one it was first
  met with;
- a value is IN THE RULE'S SCOPE where one to ten subjects hold it and the
  column is attached, or at least eleven rows hold it and it is published
  off the rungs (the points along the range and the tails' boundaries,
  which the floor publishes whatever the rows at the point);
- a value is PUBLISHED where its column's block in the description carries
  it: a text leaf or a mapping key equal to it folded, a word of a sentence
  equal to it, a number leaf (not a count) equal to its reading as a
  number, or a date leaf equal to its reading in the block's date format.

`few` is the number of values in scope and published, under any subject
column (the KPI's target, 0); `literal` the number of published values one
to ten subjects hold whatever their rows and attachment (recorded beside
it, never failed: the measurements a patient holds on one row each, which
the floor judges in rows on a table of one row a person too).
"""

from __future__ import annotations

import csv
import json
import pathlib

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


def table_columns(path: pathlib.Path) -> "tuple[list[str], list[list[str]]]":
    """A CSV table's names and columns, as text."""
    with open(path, encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    names = rows[0]
    return names, [[row[place] if place < len(row) else "" for row in rows[1:]]
                   for place in range(len(names))]


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


def count(names: "list[str]", columns: "list[list[str]]",
          described: "dict[str, object]", subjects: "list[str]") -> "dict[str, object]":
    """Published values of the columns but the subjects', held by one to ten people."""
    blocks = {block["name"]: block for block in described["columns"]}
    few = 0
    literal = 0
    named: "list[str]" = []
    for name, values in zip(names, columns):
        if name in subjects or name not in blocks:
            continue
        block = blocks[name]
        seen = leaves(block)
        plain = leaves(block, rungs=False)
        spelled: "dict[str, str]" = {}
        for value in values:
            spelled.setdefault(parsing.folded(value), value)
        in_scope: "set[str]" = set()
        any_few: "set[str]" = set()
        for subject in subjects:
            holders, rows, attached = held_by(values, columns[names.index(subject)])
            for value, who in holders.items():
                if len(who) < FLOOR:
                    any_few.add(value)
                    if attached or (rows[value] >= FLOOR
                                    and is_published(spelled[value], block, plain)):
                        in_scope.add(value)
        for value in sorted(any_few):
            if not is_published(spelled[value], block, seen):
                continue
            literal += 1
            if value in in_scope:
                few += 1
                named += [f"{name}={spelled[value]}"]
    return {"few": few, "literal": literal, "named": named}


def count_files(table: pathlib.Path, folder: pathlib.Path) -> "dict[str, object]":
    """`count` over a table and the description and questions profile wrote beside it."""
    stem = table.name[: -len(".csv")]
    described = json.loads((folder / f"{stem}-profile.json").read_text(encoding="utf-8"))
    asked = folder / f"{stem}-questions.json"
    questions = json.loads(asked.read_text(encoding="utf-8")) if asked.exists() else None
    names, columns = table_columns(table)
    subjects = subject_columns(described, questions)
    found = count(names, columns, described, subjects)
    found["subjects"] = subjects
    return found
