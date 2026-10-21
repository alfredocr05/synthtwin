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
to it that tell its subjects apart (`names_people`). For every other column and each subject column:

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
- a declared person column's census of rows a person prints no real
  group of one to ten people, and the people it does not print as they
  are number none or eleven and more (`census_few`).

`few` is the number of values, forms and groups in scope and published,
under any subject column (the KPI's target, 0); `literal` the number of
published values one to ten subjects hold whatever their rows and
attachment (recorded beside it, never failed: the measurements a patient
holds on one row each, which the floor judges in rows on a table of one row
a person too).
"""

from __future__ import annotations

import csv
import datetime
import json
import pathlib
import random
import re

from synthtwin import parsing

FLOOR = 11

# Number leaves under these keys are counts, shares or sizes, never values.
_COUNTS = ("count", "rows", "n_", "share", "width", "length",
           "position", "ceiling", "distance", "std", "mean", "skew",
           "kurtosis", "digits", "suppressed", "first", "last", "bins")
# Entries that publish no value of the column at all.
_NOTHING = ("missing", "withheld", "occurrences", "widths", "time_grain")
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
    runs = "".join(c if c in "0123456789" else " " for c in text).split()
    if not runs or len(max(runs, key=len)) > 300:
        return None
    return float(int(max(runs, key=len)))


# THE COLUMN'S OWN READING, written apart from `profile._keys_of` (Codex's
# review of lane HX2, item 5): a clock time as its minutes and seconds of the
# day, whatever the hour's width; a declared decimal comma; a declared count
# of days as the date it counts.
_CLOCK = re.compile(r"^\s*(\d{1,2}):(\d{2})(?::(\d{2}))?\s*([ap]\.?m\.?)?\s*$", re.IGNORECASE)
_EPOCHS = {"days-since-1970": datetime.date(1970, 1, 1),
           "days-since-1960": datetime.date(1960, 1, 1),
           "excel-1904": datetime.date(1904, 1, 1)}


def _clock(text: str) -> "tuple[int, int] | None":
    found = _CLOCK.match(text)
    if not found:
        return None
    hour, minute = int(found.group(1)), int(found.group(2))
    second = int(found.group(3)) if found.group(3) else -1
    marker = (found.group(4) or "").lower().replace(".", "")
    if marker:
        hour = hour % 12 + (12 if marker == "pm" else 0)
    return hour * 60 + minute, second


def _counted_day(text: str, member: str) -> "str | None":
    """The date a count of days names, for the systems the gate declares."""
    try:
        whole = int(float(text.strip()))
    except ValueError:
        return None
    if member == "excel-1900":
        if whole < 1 or whole == 60:
            return None
        start = datetime.date(1899, 12, 30) if whole > 60 else datetime.date(1899, 12, 31)
        return (start + datetime.timedelta(days=whole)).isoformat()
    if member in _EPOCHS:
        return (_EPOCHS[member] + datetime.timedelta(days=whole)).isoformat()
    return None


# THE GRAIN A BLOCK PUBLISHES (plan P4-D417), read apart from `grains`: each
# value floored to the start of its bucket by `datetime`, written as the
# canonical text the block's points are written in.
_RUNG_ORDER = ("year", "quarter", "month", "day", "four hours", "hour", "minute", "second")


def _grain_moment(value: str, grain: "dict[str, object]", member: str) -> "datetime.datetime | None":
    kind = grain["kind"]
    reading = f"{grain['reading']}"
    if kind == "clock":
        found = _clock(value)
        if found is None:
            return None
        return datetime.datetime(2000, 1, 1) + datetime.timedelta(
            minutes=found[0], seconds=max(found[1], 0))
    if kind == "counted":
        day = _counted_day(value, member or reading)
        return None if day is None else datetime.datetime.fromisoformat(day)
    read = parsing.parse_datetime(value, reading)
    if read is None:
        return None
    text = read[0]
    if len(text) == 7 and text[4:6].upper() == "-Q":
        return datetime.datetime(int(text[:4]), (int(text[6]) - 1) * 3 + 1, 1)
    if len(text) == 7:
        return datetime.datetime(int(text[:4]), int(text[5:7]), 1)
    return datetime.datetime.fromisoformat(text)


def _grain_floor(moment: "datetime.datetime", rung: str) -> "datetime.datetime":
    if rung == "year":
        return datetime.datetime(moment.year, 1, 1)
    if rung == "quarter":
        return datetime.datetime(moment.year, (moment.month - 1) // 3 * 3 + 1, 1)
    if rung == "month":
        return datetime.datetime(moment.year, moment.month, 1)
    if rung == "day":
        return datetime.datetime(moment.year, moment.month, moment.day)
    if rung == "four hours":
        return moment.replace(hour=moment.hour // 4 * 4, minute=0, second=0, microsecond=0)
    if rung == "hour":
        return moment.replace(minute=0, second=0, microsecond=0)
    if rung == "minute":
        return moment.replace(second=0, microsecond=0)
    return moment.replace(microsecond=0)


def _grain_text(moment: "datetime.datetime", grain: "dict[str, object]", block: "dict[str, object]") -> str:
    if grain["kind"] == "clock":
        with_seconds = "-ss" in f"{block.get('clock_form', '')}" or "-ss" in f"{grain['reading']}"
        return moment.strftime("%H:%M:%S" if with_seconds else "%H:%M")
    if grain["kind"] == "stamp" or moment.time() != datetime.time(0):
        return moment.strftime("%Y-%m-%d %H:%M:%S")
    return moment.strftime("%Y-%m-%d")


def bucket_names(grain: "dict[str, object]") -> "set[str]":
    """The bucket starts a `time_grain` record's spans print: each names its bucket, never a day."""
    found: "set[str]" = set()
    for _rung, first, last in grain.get("spans", []):
        found |= {f"{first}", f"{last}", f"{first}"[:10], f"{last}"[:10]}
    return found


def spans_few(values: "list[str]", people: "list[str]", block: "dict[str, object]",
              member: str = "") -> "list[str]":
    """The spans of a block's `time_grain` whose first or last bucket one to ten people hold."""
    grain = block.get("time_grain")
    if not isinstance(grain, dict):
        return []
    clock = grain["kind"] == "clock"
    found: "list[str]" = []
    for rung, first_text, last_text in grain.get("spans", []):
        holders: "dict[str, set[str]]" = {}
        for value, person in zip(values, people):
            moment = _grain_moment(value, grain, member) if parsing.folded(value) else None
            if moment is None:
                continue
            start = _grain_floor(moment, rung)
            text = start.strftime("%H:%M:%S") if clock else (
                start.strftime("%Y-%m-%d %H:%M:%S") if len(f"{first_text}") > 10 else start.strftime("%Y-%m-%d"))
            holders.setdefault(text, set()).add(person)
        for end in (first_text, last_text):
            if len(holders.get(f"{end}", set())) < FLOOR:
                found += [f"span {rung} {end}"]
    return found


def at_the_grain(values: "list[str]", block: "dict[str, object]", member: str = "") -> "list[str]":
    """A column's values as the points of its block's grain name them, or as they are."""
    grain = block.get("time_grain")
    if not isinstance(grain, dict) or grain.get("rung") == "held" or not grain.get("spans"):
        return values
    rung, first_text, last_text = grain["spans"][-1]
    clock = grain["kind"] == "clock"
    first = (datetime.datetime(2000, 1, 1) + (datetime.datetime.strptime(first_text, "%H:%M:%S")
             - datetime.datetime(1900, 1, 1))) if clock else datetime.datetime.fromisoformat(first_text)
    last = (datetime.datetime(2000, 1, 1) + (datetime.datetime.strptime(last_text, "%H:%M:%S")
            - datetime.datetime(1900, 1, 1))) if clock else datetime.datetime.fromisoformat(last_text)
    found: "list[str]" = []
    for value in values:
        moment = _grain_moment(value, grain, member) if parsing.folded(value) else None
        if moment is None:
            found += [value]
            continue
        start = min(max(_grain_floor(moment, rung), first), last)
        found += [_grain_text(start, grain, block)]
    return found


def is_published(value: str, block: "dict[str, object]",
                 seen: "tuple[set[str], set[float]]",
                 how: "tuple[str, bool]" = ("", False)) -> bool:
    """Whether a column block carries one value of the column, by any reading.

    ``how``: the system a declared count of dates is read in ("" for none)
    and whether the column was declared to write a decimal comma.
    """
    texts, numbers = seen
    member, comma = how
    folded = parsing.folded(value)
    if folded in texts:
        return True
    number = _number(value.replace(".", "").replace(",", ".") if comma else value)
    if number is None:
        number = _figures(value)
    if number is not None and number in numbers:
        return True
    shown = block.get("format")
    if block.get("role") == "datetime" and isinstance(shown, str):
        read = parsing.parse_datetime(value, shown)
        if read is not None and parsing.folded(read[0]) in texts:
            return True
    if member and block.get("role") == "datetime":
        day = _counted_day(value, member)
        if day is not None and day in texts:
            return True
    if block.get("role") == "time_of_day":
        mine = _clock(value)
        if mine is not None and any(_clock(text) == mine for text in texts):
            return True
    return False


# The package's spellings of nothing, written out here apart from `parsing`.
_NOBODY = {"", "-", "--", ".", "?", "n/a", "na", "nan", "none", "null",
           "#div/0!", "#n/a", "#name?", "#null!", "#num!", "#ref!", "#value!"}


def subject_of(cell: str) -> str:
    """The subject a person cell names: folded; no zero opening a run of figures; letters and figures only.

    `REC-0007`, `rec7` and `Rec 7` are one patient (lane HX2's skeptic, round
    2, item 6), and `A-01-02` is `a12`: the zeros opening each run AS WRITTEN
    go first (Codex's review of lane HX2, item 12). Every spelling of nobody
    -- blank, `NA`, `#DIV/0!`, `NaT` -- is one unknown subject, "" (item 3).
    Written apart from `profile.subject_keys`, with patterns.
    """
    folded = parsing.folded(cell)
    if folded in _NOBODY or cell == "NaT":
        return ""
    text = re.sub(r"(?<![0-9])0+(?=[0-9])", "", folded)
    return re.sub(r"[\x00-\x2f\x3a-\x60\x7b-\x7f]+", "", text)


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


def names_people(values: "list[str]", subjects: "list[str]") -> bool:
    """No one value is the first met for more than half the subjects (and two or more are met)."""
    first: "dict[str, str]" = {}
    for value, subject in zip(values, subjects):
        folded = parsing.folded(value)
        if folded and subject not in first:
            first[subject] = folded
    tally: "dict[str, int]" = {}
    for folded in first.values():
        tally[folded] = tally.get(folded, 0) + 1
    return len(first) >= 2 and max(tally.values()) * 2 <= len(first)


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
    """The declared person columns and every column an open question offering `identifier` holds.

    The open person question's candidates, and a key another identity
    question holds, such as a patient number of figures padded with zeros
    put the codes-or-measurements question (lane HX2's skeptic, round 2,
    item 1).
    """
    settings = described["settings"]
    assert isinstance(settings, dict)
    found = list(settings["person_columns"])
    for entry in (questions or {}).get("asked", []):
        offered = [choice["answer"] for choice in entry["answers_you_can_give"]]
        if ("identifier" in offered
                and entry.get("your_answer", "") == ""
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
    """Groups of one to ten people a person column's census prints.

    The real census counts how many people have each number of rows. A
    published entry of one to ten people is such a group where the real
    census holds exactly that many people at that number of rows; and the
    people whose real entry is not published as it is form one more group
    (the pool), which may not number one to ten either.

    NO CENSUS IS EXEMPT for being drawn from counts alone (Codex's review
    of lane HX2, item 11): an even spread, or the census the block's
    layouts imply, that reproduces a real group of one to ten people
    prints it.
    """
    census = block.get("n_distinct_by_occurrences")
    if not isinstance(census, dict) or not census:
        return 0
    # A spelling the block counts as missing (`NA`) is nobody.
    absent = block.get("missing_by_source")
    nobody = {parsing.folded(f"{key}") for key in absent} if isinstance(absent, dict) else set()
    rows: "dict[str, int]" = {}
    for cell in cells:
        if parsing.folded(cell) and parsing.folded(cell) not in nobody:
            rows[cell] = rows.get(cell, 0) + 1
    real: "dict[int, int]" = {}
    for count in rows.values():
        real[count] = real.get(count, 0) + 1
    shown = {int(key): int(value) for key, value in census.items()}
    # ...save the one census the column's printed totals force: every
    # value on one row, or all but one on one row and that one on two.
    if sum(rows.values()) - len(rows) <= 1 or len(rows) <= 1:
        return 0
    found = sum(1 for key, value in shown.items()
                if 1 <= value < FLOOR and real.get(key, 0) == value)
    pool = sum(value for key, value in real.items() if shown.get(key) != value)
    if 1 <= pool < FLOOR:
        found += 1
    return found


def _prefixes(block: "dict[str, object]") -> "set[str]":
    """Every text a block publishes under a key naming a prefix, folded."""
    found: "set[str]" = set()
    stack: "list[tuple[str, object]]" = [(key, block[key]) for key in block if key != "name"]
    while stack:
        key, leaf = stack.pop()
        if isinstance(leaf, dict):
            stack += [(f"{key}.{inner}", value) for inner, value in leaf.items()]
        elif isinstance(leaf, list):
            stack += [(key, item) for item in leaf]
        elif isinstance(leaf, str) and leaf and "prefix" in key:
            found.add(parsing.folded(leaf))
    return found


def count(names: "list[str]", columns: "list[list[str]]",
          described: "dict[str, object]", subjects: "list[str]") -> "dict[str, object]":
    """Published values, forms and groups of the other columns held by one to ten people."""
    blocks = {block["name"]: block for block in described["columns"]}
    settings = described["settings"]
    declared = list(settings["person_columns"]) if isinstance(settings, dict) else []
    members = {pair[0]: pair[1] for pair in settings.get("forced_date_counts", [])} \
        if isinstance(settings, dict) else {}
    commas = set(settings.get("forced_decimal_commas", [])) if isinstance(settings, dict) else set()
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
        if name not in blocks:
            continue
        # A subject column is counted too, in every OTHER subject column
        # (lane HX2's skeptic, round 2, item 3): its layouts, its pool.
        others = [subject for subject in subjects if subject != name]
        if not others:
            continue
        block = blocks[name]
        # A COLUMN DESCRIBED AT A GRAIN (plan P4-D417): each of its values
        # is counted as the start of its bucket, the tails pooled into the
        # record's ends -- what each published point names.
        raw = values
        values = at_the_grain(values, block, members.get(name, ""))
        how = (members.get(name, ""), name in commas)
        prefixes = _prefixes(block)
        dated = block.get("role") in ("datetime", "time_of_day")
        statistics = block.get("role") != "identifier"
        seen = leaves(block)
        plain = leaves(block, rungs=False)
        spelled: "dict[str, str]" = {}
        for value in values:
            spelled.setdefault(parsing.folded(value), value)
        forms = _forms_of(block, values)
        remainder = [value if parsing.folded(value) and not is_published(value, block, seen, how)
                     else "" for value in values]
        in_scope: "set[str]" = set()
        any_few: "set[str]" = set()
        groups: "set[str]" = set()
        for subject in others:
            people = [subject_of(cell) for cell in columns[names.index(subject)]]
            holders, rows, attached = held_by(values, people)
            enough = counts_people(people)
            if not enough and not (attached and names_people(values, people)):
                continue
            for value, who in holders.items():
                if len(who) < FLOOR:
                    any_few.add(value)
                    if (not enough or attached or dated
                            or (rows[value] >= FLOOR
                                and is_published(spelled[value], block, plain, how))):
                        in_scope.add(value)
            # THE PREFIXES a block publishes are fragments of its values
            # (Codex's review of lane HX2, item 12): each held by eleven
            # people or none.
            for prefix in prefixes:
                wearing = ["x" if parsing.folded(value).startswith(prefix) else ""
                           for value in values]
                prefix_holders, _rows, _attached = held_by(wearing, people)
                if "x" in prefix_holders and len(prefix_holders["x"]) < FLOOR:
                    groups.add(f"prefix {prefix}")
            form_holders, _rows, _attached = held_by(forms, people)
            for form, who in form_holders.items():
                if len(who) < FLOOR and (enough or attached or statistics):
                    groups.add(f"form {form}")
            # THE LAYOUTS' POOL: the present cells no named layout takes, a
            # count printed as `(withheld)` or left to subtraction
            # (lane HX2's skeptic, round 2, item 4).
            if enough and block.get("layout_forms"):
                pool = ["x" if parsing.folded(value) and not form else ""
                        for value, form in zip(values, forms)]
                pool_holders, _rows, _attached = held_by(pool, people)
                if "x" in pool_holders and len(pool_holders["x"]) < FLOOR:
                    groups.add("layout pool")
            # THE SPANS A `time_grain` RECORD PUBLISHES (plan P4-D417): each
            # end a bucket eleven people hold, under every subject column.
            if enough:
                for span in spans_few(raw, people, block, members.get(name, "")):
                    groups.add(span)
            if not enough or not statistics:
                continue
            for label, cells in (("remainder", remainder), ("present", values)):
                group_holders, group_rows, _attached = held_by(
                    ["x" if parsing.folded(cell) else "" for cell in cells], people)
                if "x" in group_holders and len(group_holders["x"]) < FLOOR \
                        and group_rows["x"] >= FLOOR:
                    groups.add(label)
        for value in sorted(any_few):
            if not is_published(spelled[value], block, seen, how):
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


def size_table(differing: float) -> str:
    """150 declared patients on four rows each; `size` one value a patient.

    ``differing`` is the share of a patient's later rows written with
    another size: nought keeps the column attached to the patient, a
    quarter does not.
    """
    draw = random.Random(29)
    sizes = [f"{draw.uniform(150, 199):.1f}" for _person in range(150)]
    lines = ["patient,size,value"]
    for place in range(600):
        person = place % 150
        size = sizes[person]
        if place >= 150 and draw.random() < differing:
            size = f"{draw.uniform(150, 199):.1f}"
        lines += [f"REC{70000000 + 3 * person:08d},{size},{draw.uniform(3, 150):.1f}"]
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

    ``small`` adds two patients on six rows and one on nine: a pool of
    three, which spread alone would print three people on seven rows.
    """
    draw = random.Random(37)
    sizes = [1] * 30 + [2] * 40 + [3] * 25 + [4] * 20 + [5] * 15
    if small:
        sizes += [6, 6, 9]
    lines = ["patient,value"]
    for person, size in enumerate(sizes):
        for _row in range(size):
            lines += [f"REC{90000000 + 3 * person:08d},{draw.uniform(3, 150):.1f}"]
    return "\n".join(lines) + "\n"


def forms_table(rows: int) -> str:
    """150 declared patients; `site` North and South, rare wards, and two patients' own codes.

    A fifth of every patient's rows name a rare ward (`Annex` and three
    letters), so the remainder the floor merges is held by many patients;
    two patients' rows are written as codes (`Q07-3`), each code on too
    few rows to be named, but the form they wear stands on more than
    eleven rows -- worn by two patients.
    """
    draw = random.Random(41)
    letters = "abcdefghijklmnopqrstuvwxyz"
    lines = ["patient,site,value"]
    for _row in range(rows):
        person = draw.randrange(150)
        if person in (11, 22):
            site = f"Q{draw.randrange(100):02d}-{draw.randrange(10)}"
        elif draw.random() < 0.2:
            site = "Annex" + "".join(letters[draw.randrange(26)] for _place in range(3))
        else:
            site = ("North", "South")[draw.randrange(2)]
        lines += [f"REC{40000000 + 3 * person:08d},{site},{draw.uniform(3, 150):.1f}"]
    return "\n".join(lines) + "\n"


def census_twin_table() -> str:
    """Declared patients on one to five rows; three on five rows beside twenty-two on four.

    Pooled with the four-row entry, the three spread back into exactly
    the census they came from: twenty-two on four rows and three on five.
    """
    draw = random.Random(43)
    sizes = [1] * 30 + [2] * 40 + [3] * 25 + [4] * 22 + [5] * 3
    lines = ["patient,value"]
    for person, size in enumerate(sizes):
        for _row in range(size):
            lines += [f"REC{30000000 + 3 * person:08d},{draw.uniform(3, 150):.1f}"]
    return "\n".join(lines) + "\n"


def filler_table(rows: int) -> str:
    """Dates and a region all but constant beside a filler code of seven values (`row0` to `row6`).

    The filler repeats, so the person question is put to it; a column of
    fewer than eleven values counts only the columns attached to it that
    tell its values apart: the dates are not attached, and the region,
    `north` on all but sixteen rows, is attached to anything but tells
    nothing apart.
    """
    draw = random.Random(47)
    lines = ["seen,region,other"]
    regions = ["north"] * (rows - 16) + ["south"] * 15 + ["west"]
    draw.shuffle(regions)
    for place in range(rows):
        year, month, day = draw.randint(2015, 2022), draw.randint(1, 12), draw.randint(1, 28)
        lines += [f"{year}-{month:02d}-{day:02d},{regions[place]},row{place % 7}"]
    return "\n".join(lines) + "\n"


# -- lane HX2's second repair: the skeptic's round-2 tables -----------------


def _long_rows(rows: int, seed: int, cell) -> str:
    """150 patients on rows weighted one to twenty-five, a column `x` written by ``cell``.

    ``cell(place, row, draw)`` returns the row's (patient key, x).
    """
    draw = random.Random(seed)
    weights = [1.0 + (place % 9) * 3 for place in range(150)]
    lines = ["patient,x,test,value"]
    for row in range(rows):
        place = draw.choices(range(150), weights)[0]
        key, x = cell(place, row, draw)
        test = ("Sodium", "Potassium", "Glucose")[draw.randrange(3)]
        lines += [f"{key},{x},{test},{draw.uniform(3, 150):.1f}"]
    return "\n".join(lines) + "\n"


def two_systems_table(rows: int) -> str:
    """Item 2: twenty patients keyed `P#####` and 130 keyed `REC########` (two record systems merged)."""
    def cell(place: int, _row: int, draw: random.Random) -> "tuple[str, str]":
        key = f"P{50000 + place:05d}" if place < 20 else f"REC{20000000 + 7 * place:08d}"
        return key, ("I10", "E11.9", "J45")[draw.randrange(3)]
    return _long_rows(rows, 91, cell)


def plan_rare_table(rows: int) -> str:
    """Items 3 and 4: three patients' plans written `ZQ-#####`, everyone else's `XKH#########`."""
    def cell(place: int, _row: int, _draw: random.Random) -> "tuple[str, str]":
        plan = f"ZQ-{30000 + place:05d}" if place < 3 else f"XKH{100000000 + 7919 * place:09d}"
        return f"REC{20000000 + 7 * place:08d}", plan
    return _long_rows(rows, 92, cell)


def spellings_table(rows: int) -> str:
    """Item 6: a code six patients hold, their keys written three ways (`REC…`, `rec…`, `REC-…`)."""
    def cell(place: int, _row: int, draw: random.Random) -> "tuple[str, str]":
        key = f"REC{20000000 + 7 * place:08d}"
        key = (key, key.lower(), key[:3] + "-" + key[3:])[draw.randrange(3)]
        code = ("Q87.4" if place < 6 and draw.random() < 0.7
                else ("I10", "E11.9", "J45")[draw.randrange(3)])
        return key, code
    return _long_rows(rows, 93, cell)


def capitals_table(rows: int) -> str:
    """Item 5: each patient's name, in capitals on about 15 % of rows, beside an open patient key."""
    first = ("James", "Maria", "Robert", "Linda", "Michael", "Patricia", "David",
             "Jennifer", "William", "Elizabeth", "Richard", "Susan")
    last = ("Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
            "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez")
    names = [f"{first[(7 * place) % len(first)]} {last[(5 * place + place // 13) % len(last)]}"
             for place in range(150)]

    def cell(place: int, _row: int, draw: random.Random) -> "tuple[str, str]":
        name = names[place] if draw.random() < 0.85 else names[place].upper()
        return f"REC{20000000 + 7 * place:08d}", name
    return _long_rows(rows, 94, cell)


# -- lane HX2's third repair: Codex's review and the combined verify --------


def _lines(head: str, rows: "list[list[str]]") -> str:
    def cell(text: str) -> str:
        return f'"{text}"' if "," in text else text
    return "\n".join([head] + [",".join(cell(one) for one in row) for row in rows]) + "\n"


def layouts_census_table() -> str:
    """Item 1: one patient `P00001` on 14 rows, eleven `REC` on two, 88 on ten.

    Pooled, the census reads 12 people on three rows beside 88 on ten,
    and no three-row group fills the 14 rows of `P#####`.
    """
    draw = random.Random(51)
    rows = [["P00001", f"{draw.uniform(3, 150):.1f}"] for _row in range(14)]
    for person in range(99):
        for _row in range(2 if person < 11 else 10):
            rows += [[f"REC{20000000 + 7 * person:08d}", f"{draw.uniform(3, 150):.1f}"]]
    draw.shuffle(rows)
    return _lines("patient,lab", rows)


def own_layout_table() -> str:
    """Item 1: 150 patients on ten rows each, three of them keyed `P#####`."""
    draw = random.Random(53)
    rows = []
    for person in range(150):
        key = f"P{10000 + person:05d}" if person < 3 else f"REC{20000000 + 7 * person:08d}"
        rows += [[key, f"{draw.uniform(3, 150):.1f}"] for _row in range(10)]
    draw.shuffle(rows)
    return _lines("patient,lab", rows)


def case_variants_table() -> str:
    """Item 2: 120 patients, each key written in twelve cases; `special` five patients hold."""
    draw = random.Random(55)
    rows = []
    for person in range(120):
        base = f"patkey{person:04d}"
        for visit in range(12):
            key = "".join(c.upper() if (visit >> i) & 1 else c for i, c in enumerate(base))
            rows += [[key, "special" if person < 5 else "common", f"{draw.uniform(3, 150):.1f}"]]
    return _lines("patient,flag,lab", rows)


NOBODY_FORMS = ("", "NA", "nan", "none", "null", "#DIV/0!", "#NAME?", "#NUM!", "#REF!",
                "#VALUE!", "NaT")


def nobody_table() -> str:
    """Item 3: 100 patients twice, and 22 visits of one unnamed patient in eleven spellings of nobody."""
    draw = random.Random(57)
    rows = []
    for person in range(100):
        rows += [[f"REC{20000000 + 7 * person:08d}", "seen", f"{draw.uniform(3, 150):.1f}"]
                 for _row in range(2)]
    for form in NOBODY_FORMS:
        rows += [[form, "unk", f"{draw.uniform(3, 150):.1f}"] for _row in range(2)]
    draw.shuffle(rows)
    return _lines("patient,label,lab", rows)


def free_text_key_table() -> "tuple[str, list[str]]":
    """Item 4: 150 patients keyed `participant AB registry`, five visits, a birth date each."""
    draw = random.Random(59)
    letters = "ABCDEFGHJKLMNPQRSTUVWXYZ"
    births = [f"{draw.randint(1930, 2005)}-{draw.randint(1, 12):02d}-{draw.randint(1, 28):02d}"
              for _person in range(150)]
    rows = []
    for person in range(150):
        key = f"participant {letters[person // 24 % 24]}{letters[person % 24]} registry"
        rows += [[key, births[person], f"{draw.uniform(3, 150):.1f}"] for _visit in range(5)]
    draw.shuffle(rows)
    return _lines("patient,dob,lab", rows), births


def clock_table() -> str:
    """Item 5: three of 120 patients at `8:30`, written without the hour's zero, on twelve rows each."""
    draw = random.Random(61)
    rows = []
    for person in range(120):
        for _visit in range(12):
            if person < 3:
                clock = "8:30"
            elif draw.random() < 0.1:
                clock = "7:31"
            else:
                clock = ("07:00", "09:00", "10:00", "11:00")[draw.randrange(4)]
            rows += [[f"REC{20000000 + 7 * person:08d}", clock, f"{draw.uniform(3, 150):.1f}"]]
    draw.shuffle(rows)
    return _lines("patient,clock,lab", rows)


def day_count_table(written: str, people: int = 150, name: str = "day") -> str:
    """Item 5 and the orchestrator's addendum 2: 600 day counts beside ``people`` patients.

    ``written`` `plain`: 19000 to 19599, days since 1970, one a row;
    `pointed`: Excel days 42000 to 42599 written with a point between the
    thousands (`42.345`), which no reading takes as a count. 150 people
    hold four rows each; 600 one each (lane HX2's second verify, `a2_onerow`).
    """
    draw = random.Random(63)
    rows = []
    for row in range(600):
        if written == "plain":
            day = f"{19000 + row}"
        else:
            number = 42000 + row
            day = f"{number // 1000}.{number % 1000:03d}"
        rows += [[f"REC{20000000 + 7 * (row % people):08d}", day, f"{draw.uniform(3, 150):.1f}"]]
    return _lines(f"patient,{name},lab", rows)


def past_one_table() -> str:
    """Lane HX2's second verify, item 1 (`past1`): 95 patients on one row and 5 on two.

    Five rows past one a value, fewer than eleven: no census that closes is
    without a small entry, and the even spread of 105 rows over 100
    patients is the real census, {1: 95, 2: 5}, its group of five printed.
    """
    draw = random.Random(1)
    rows = []
    for person in range(100):
        rows += [[f"REC{20000000 + 7 * person:08d}", f"{draw.uniform(3, 150):.1f}"]
                 for _row in range(2 if person >= 95 else 1)]
    draw.shuffle(rows)
    return _lines("patient,lab", rows)


def comma_table() -> str:
    """Item 5: `10,00` to `11,49`, one a patient over four visits, declared as a decimal comma."""
    draw = random.Random(65)
    rows = []
    for person in range(150):
        value = f"{10 + person / 100:.2f}".replace(".", ",")
        rows += [[f"REC{20000000 + 7 * person:08d}", value, f"{draw.uniform(3, 150):.1f}"]
                 for _visit in range(4)]
    draw.shuffle(rows)
    return _lines("patient,m,lab", rows)


def nine_and_ten_table() -> str:
    """Item 6: 100 patients on nine rows and one on ten: spread evenly, exactly the real census."""
    draw = random.Random(67)
    rows = []
    for person in range(101):
        rows += [[f"REC{20000000 + 7 * person:08d}", f"{draw.uniform(3, 150):.1f}"]
                 for _row in range(10 if person == 0 else 9)]
    draw.shuffle(rows)
    return _lines("patient,lab", rows)


def pool_only_table() -> str:
    """Item 7: two of 100 patients hold `x` (`A12345`, `BB23456`) on their ten rows; blank elsewhere."""
    draw = random.Random(69)
    rows = []
    for person in range(100):
        x = "A12345" if person == 0 else ("BB23456" if person == 1 else "")
        rows += [[f"REC{20000000 + 7 * person:08d}", x, f"{draw.uniform(3, 150):.1f}"]
                 for _row in range(10)]
    draw.shuffle(rows)
    return _lines("patient,x,lab", rows)


def long_figures_table() -> str:
    """Item 8: a note holding 400 nines, beside 100 patients on two rows each."""
    draw = random.Random(71)
    rows = []
    for person in range(100):
        rows += [[f"REC{20000000 + 7 * person:08d}", "item " + "9" * 400 + f" value {person}",
                  f"{draw.uniform(3, 150):.1f}"] for _row in range(2)]
    return _lines("patient,note,lab", rows)


def two_card_table(rows: int) -> str:
    """The combined verify's item 2: `card` `ZZ-####` for the 12 patients of three households.

    The person question is open on `patient` and on `acct`, a household of
    four; every other patient's card is `CARD########`.
    """
    draw = random.Random(7)
    weights = [1.0 + (person % 9) * 3 for person in range(150)]
    lines = []
    for _row in range(rows):
        person = draw.choices(range(150), weights)[0]
        card = f"ZZ-{person:04d}" if person // 4 < 3 else f"CARD{10000000 + 7 * person:08d}"
        lines += [[f"REC{20000000 + 7 * person:08d}", f"H{5000 + person // 4:04d}", card,
                   f"{draw.uniform(3, 150):.1f}"]]
    return _lines("patient,acct,card,lab", lines)
