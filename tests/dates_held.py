"""P4-D433 (lane PS2): the tables and the count of dates held by the floor, shared by the gate and the KPI driver.

THE COUNT (`K-HZ-07`). Every real date a description publishes -- a
percentile, a rung, a tail boundary, a census entry, a mode, a span's end,
a written form -- is counted in PEOPLE where a person column is declared or
answered and repeats (`persons_counted.count`, the independent count lane
HX2's gate and K-S3-65 read), else in ROWS by the calendar part it names
(one row a person: a row is a person; no person column: a row is the one
holder the table names): a published day, month or quarter that one to ten
rows fall on is counted (`_in_rows`), and so is a pooled or held record's
span end or bucket one to ten rows hold. Beside it, lane E0c's leak scan
read as a search of the description's text (`printed`): a real date one to
ten people (else rows, by its day) hold, printed anywhere as written or as
its canonical day. Written apart from `profile._counted_in_subjects` and
`profile._dates_few_in_rows`.

THE SWEEP (the lane's spec): birth dates over seventy years, death dates,
sparse event dates and dense admission dates that must stay at the day, on
a table of one row a person, of several rows a person, and of no person
column; and lane E0c's two live exposures, the zoo's `patients.csv`
(`dob_iso`, one row a person, `patient_id` answered `identifier`) and
`phi_registry.csv` (`birth_date`, no question flags it), the second rebuilt
here as lane E0c's build writes it (`tests/health_zoo_wide.py` is not on
this lane's base). Every table runs the zoo's own path: profile, the
general answers, profile --answers (`answered`).
"""

from __future__ import annotations

import contextlib
import datetime
import io
import json
import pathlib
import random
import re

from synthtwin import cli, parsing

import health_zoo
import persons_counted

FLOOR = 11


def _day(draw: random.Random, first: datetime.date, last: datetime.date) -> datetime.date:
    return first + datetime.timedelta(days=draw.randrange((last - first).days + 1))


def one_row_a_person(rows: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """A patient a row: a birth date over seventy years, a dense admission day, a sparse death date."""
    draw = random.Random(seed)
    lines: "list[list[str]]" = []
    for index in range(rows):
        born = _day(draw, datetime.date(1930, 1, 1), datetime.date(1999, 12, 31))
        admitted = _day(draw, datetime.date(2023, 1, 1), datetime.date(2023, 12, 31))
        died = _day(draw, datetime.date(2015, 1, 1), datetime.date(2024, 12, 31)) if draw.random() < 0.03 else None
        lines += [[
            f"P{1000000 + index:07d}", born.isoformat(), admitted.isoformat(),
            died.isoformat() if died else "", f"{draw.uniform(40, 140):.1f}",
        ]]
    return ["patient_id", "birth_date", "admit_date", "death_date", "weight"], lines


def several_rows_a_person(rows: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Four visits a patient: the birth and death date repeated on each, a dense visit day."""
    draw = random.Random(seed)
    lines: "list[list[str]]" = []
    people = max(rows // 4, 1)
    born = [_day(draw, datetime.date(1930, 1, 1), datetime.date(1999, 12, 31)) for _person in range(people)]
    died = [
        _day(draw, datetime.date(2015, 1, 1), datetime.date(2024, 12, 31)) if draw.random() < 0.03 else None
        for _person in range(people)
    ]
    for index in range(rows):
        person = index % people
        seen = _day(draw, datetime.date(2023, 1, 1), datetime.date(2023, 12, 31))
        death = died[person]
        lines += [[
            f"P{1000000 + person:07d}", born[person].isoformat(), seen.isoformat(),
            death.isoformat() if death else "", f"{draw.uniform(40, 140):.1f}",
        ]]
    return ["patient_id", "birth_date", "visit_date", "death_date", "weight"], lines


def no_person_column(rows: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """An event log naming nobody: a birth date, a dense admission day, an event over thirty years on few rows."""
    draw = random.Random(seed)
    lines: "list[list[str]]" = []
    for _index in range(rows):
        born = _day(draw, datetime.date(1930, 1, 1), datetime.date(1999, 12, 31))
        admitted = _day(draw, datetime.date(2023, 1, 1), datetime.date(2023, 12, 31))
        event = _day(draw, datetime.date(1990, 1, 1), datetime.date(2019, 12, 31)) if draw.random() < 0.02 else None
        lines += [[
            born.isoformat(), admitted.isoformat(), event.isoformat() if event else "",
            draw.choice(("A", "B", "C")),
        ]]
    return ["birth_date", "admit_date", "event_date", "ward"], lines


def dense_only(rows: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """No person column, every date column dense: an admission day over a year and a stamp to the minute."""
    draw = random.Random(seed)
    lines: "list[list[str]]" = []
    for _index in range(rows):
        admitted = _day(draw, datetime.date(2023, 1, 1), datetime.date(2023, 12, 31))
        stamp = datetime.datetime.combine(
            _day(draw, datetime.date(2023, 1, 1), datetime.date(2023, 12, 31)),
            datetime.time(draw.randrange(24), draw.randrange(60)),
        )
        lines += [[admitted.isoformat(), stamp.strftime("%Y-%m-%d %H:%M"), draw.choice(("A", "B", "C"))]]
    return ["admit_date", "arrived_at", "ward"], lines


# Lane E0c's `phi_registry` (tests/health_zoo_wide.py on lane E0c's head
# a974b1d9), the same builder: every value invented.
FIRST_NAMES = (
    "Maria", "James", "Aisha", "Wei", "Olga", "Carlos", "Fatima", "John", "Priya", "Liam", "Sofia", "Kwame", "Hannah",
    "Mateo", "Yuki", "Omar", "Elena", "Noah", "Amara", "Lucas", "Mei", "Diego", "Zara", "Ethan", "Ines", "Tariq",
    "Grace", "Ivan", "Leila", "Samuel", "Nadia", "Jonah", "Rosa", "Arjun", "Clara", "Kofi", "Anya", "Felix", "Lina",
    "Hugo",
)
LAST_NAMES = (
    "Gonzalez", "Smith", "Okafor", "Zhang", "Ivanova", "Mendes", "Haddad", "Murphy", "Raman", "Walsh", "Rossi",
    "Mensah", "Becker", "Silva", "Tanaka", "Farouk", "Petrova", "Clarke", "Diallo", "Moreau", "Chen", "Ortiz", "Khan",
    "Novak", "Duarte", "Aziz", "Bennett", "Kowalski", "Rahimi", "Adeyemi", "Sato", "Lindqvist", "Vargas", "Iyer",
    "Hoffmann", "Boateng", "Sokolova", "Weber", "Nasser", "Laurent",
)
STREETS = ("Elm", "Maple", "Oak", "Cedar", "Pine", "Willow", "Harbor", "Lake", "Hill", "River", "Mill", "Park")
SUFFIXES = ("St", "Ave", "Rd", "Blvd", "Ln")
PHI_ZIPS = tuple(f"{52240 + 7 * place}" for place in range(59))
PHI_COLUMNS = ("med_rec_no", "patient_name", "street_address", "phone", "email", "ssn", "zip5", "birth_date")


def phi_registry(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Lane E0c's registry export: every direct identifier of HIPAA's Safe Harbor list a hospital file carries."""
    draw = random.Random(seed)
    rows: "list[list[str]]" = []
    for index in range(n):
        first, last = draw.choice(FIRST_NAMES), draw.choice(LAST_NAMES)
        born = health_zoo._day(draw, datetime.date(1930, 1, 1), datetime.date(2005, 12, 31))
        rows += [[
            f"MR{4000000 + index}",
            f"{first} {last}",
            f"{draw.randint(1, 9999)} {draw.choice(STREETS)} {draw.choice(SUFFIXES)}",
            f"({draw.randint(201, 989)}) 555-{draw.randint(0, 9999):04d}",
            f"{first.lower()}.{last.lower()}{draw.randint(1, 999)}@example.org",
            f"9{draw.randint(0, 99):02d}-{draw.randint(10, 99)}-{draw.randint(0, 9999):04d}",
            draw.choice(PHI_ZIPS),
            born.isoformat(),
        ]]
    return list(PHI_COLUMNS), rows


def _table(name: str, build: object, columns: "tuple[str, ...]", knows: "dict[str, str]") -> health_zoo.Table:
    return health_zoo.Table(
        name, ".csv", build,  # type: ignore[arg-type]
        lambda header, rows: health_zoo.csv_bytes(header, rows),
        {name: columns}, knows, health_zoo._csv_reader(), (),
    )


def _zoo_table(name: str) -> health_zoo.Table:
    return [table for table in health_zoo.TABLES if table.name == name][0]


# The sweep: each shape's table; DENSE names the columns whose day grain
# the floor holds (their bytes pinned by the gate).
SWEEP: "dict[str, health_zoo.Table]" = {
    "one_row": _table("one_row", one_row_a_person,
                      ("patient_id", "birth_date", "admit_date", "death_date", "weight"),
                      {"patient_id": "identifier", "weight": "measurement"}),
    "several_rows": _table("several_rows", several_rows_a_person,
                           ("patient_id", "birth_date", "visit_date", "death_date", "weight"),
                           {"patient_id": "identifier", "weight": "measurement"}),
    "no_person": _table("no_person", no_person_column, ("birth_date", "admit_date", "event_date", "ward"), {}),
    "dense_only": _table("dense_only", dense_only, ("admit_date", "arrived_at", "ward"), {}),
    "demographics": _zoo_table("patients"),
    # The person question answered for the record number only, `keep` for
    # every other column it is put to, as lane E0c's zoo answers it (its
    # build: two repeating identifiers made 5 and 66 "people"): so no
    # subject column repeats and the birth dates are counted in rows.
    "phi_registry": _table("phi_registry", phi_registry, PHI_COLUMNS, {
        "med_rec_no": "identifier", "patient_name": "keep", "street_address": "keep",
        "phone": "keep", "email": "keep", "ssn": "keep", "zip5": "code",
    }),
}
DENSE: "dict[str, tuple[str, ...]]" = {
    "one_row": ("admit_date",),
    "several_rows": ("visit_date",),
    "no_person": ("admit_date",),
    "dense_only": ("admit_date", "arrived_at"),
}
SEED = 20261016


def _quietly(arguments: "list[str]", refused: bool) -> int:
    screen = io.StringIO()
    with contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
        code = cli.main(arguments, small_tables_refused=refused)
    assert code in (0, 3), screen.getvalue()[-2000:]
    return code


def answered(table: health_zoo.Table, folder: pathlib.Path, rows: int) -> pathlib.Path:
    """The zoo's path for one table: written from its seed, profiled, its questions answered generally, profiled again.

    The table floor stays on at 20,000 rows and above (the command's own
    rule); below it only the internal switch reaches the table. Returns
    the table's path; its description and questions sit beside it.
    """
    from unanswered_identifier_shapes import nobody_at_the_keyboard

    source = health_zoo.write_table(table, folder, rows, SEED)
    refused = rows >= 20000
    asked = folder / f"{table.name}-questions.json"
    with nobody_at_the_keyboard():
        _quietly(["profile", f"{source}", "--out-dir", f"{folder}", "--replace"], refused)
        # An answer may put the next question (a column answered `keep` to
        # the person question is then asked what it holds): the person
        # answers each round the file asks something they know, three at most.
        for _round in range(ROUNDS):
            if not asked.exists():
                break
            document = json.loads(asked.read_text(encoding="utf-8"))
            answers, _general = health_zoo.answer_generally(table, document)
            if not [answer for answer in answers if answer["given"]]:
                break
            asked.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
            _quietly(["profile", f"{source}", "--out-dir", f"{folder}", "--replace", "--answers", f"{asked}"], refused)
    return source


ROUNDS = 3


def block_of(folder: pathlib.Path, table: str, column: str) -> "dict[str, object]":
    """One column's block of a table's description in ``folder``."""
    described = json.loads((folder / f"{table}-profile.json").read_text(encoding="utf-8"))
    return [block for block in described["columns"] if block["name"] == column][0]


def dates_held_few(table: pathlib.Path, folder: pathlib.Path) -> "dict[str, object]":
    """K-HZ-07 over one table: the real dates one to ten people (else rows) hold that its description publishes.

    Each column the description reads as dates (or holds with a
    `time_grain` record) is counted alone, beside the person columns that
    repeat and hold the floor's number of people
    (`persons_counted.subject_columns`), or, with none, in rows
    (`_in_rows`). Returns the count, the named dates and groups, the date
    columns, the unit and the printed real dates (`printed`).
    """
    stem = table.name[: -len(table.suffix)]
    text = (folder / f"{stem}-profile.json").read_text(encoding="utf-8")
    described = json.loads(text)
    asked = folder / f"{stem}-questions.json"
    questions = json.loads(asked.read_text(encoding="utf-8")) if asked.exists() else None
    names, columns = persons_counted.table_columns(table, *persons_counted._written(described))
    # A question answered in an earlier round is asked again only to show
    # the reading it keeps (`answered_before`): not an open question.
    settled = {
        entry["column"] for entry in (questions or {}).get("answered_before", [])
        if entry.get("your_answer") and entry.get("column") not in described["settings"]["person_columns"]
    }
    people = [
        name for name in persons_counted.subject_columns(described, questions)
        if name in names and name not in settled
        and persons_counted.repeats(columns[names.index(name)])
        and persons_counted.counts_people([persons_counted.subject_of(cell) for cell in columns[names.index(name)]])
    ]
    if not people:
        found = _in_rows(described, names, columns)
        found["printed"] = printed(text, found["dated"], names, columns, [], described)  # type: ignore[arg-type]
        return found
    held_columns = [columns[names.index(name)] for name in people]
    # The person column's own census of rows a person is lane MG's, not a
    # date: the count reads the description with no declared person column.
    settings = dict(described["settings"])
    settings["person_columns"] = []
    plain = dict(described)
    plain["settings"] = settings
    few = 0
    named: "list[str]" = []
    dated: "list[str]" = []
    for block in described["columns"]:
        if block["name"] not in names or block["name"] in people or not (
            block.get("role") == "datetime" or isinstance(block.get("time_grain"), dict)
        ):
            continue
        dated += [block["name"]]
        found = persons_counted.count(
            [block["name"]] + people,
            [columns[names.index(block["name"])]] + held_columns,
            plain,
            people,
        )
        few += int(found["few"])  # type: ignore[call-overload]
        named += list(found["named"])  # type: ignore[call-overload]
    shown = printed(text, dated, names, columns, held_columns, described)
    return {"few": few, "named": named, "dated": dated, "counted_in": "people", "printed": shown}


_PART = re.compile(r"^([0-9]{4})-(?:q([1-4])|([0-9]{2})(?:-([0-9]{2}))?)")


def parts_of(text: str) -> "list[str]":
    """The calendar parts a canonical date text names, finest first (day, month, quarter), by pattern."""
    found = _PART.match(parsing.folded(text))
    if not found:
        return []
    year, quarter, month, day = found.groups()
    if quarter:
        return [f"{year}-q{quarter}"]
    if not 1 <= int(month) <= 12:
        return []
    named = [f"{year}-{month}", f"{year}-q{(int(month) - 1) // 3 + 1}"]
    return ([f"{year}-{month}-{day}"] if day else []) + named


def _in_rows(described: "dict[str, object]", names: "list[str]", columns: "list[list[str]]") -> "dict[str, object]":
    """The count where no person column repeats: each published date's day, month or quarter against the rows on it.

    Each column read as dates: its cells at the grain its block publishes
    (`persons_counted.at_the_grain`), else read by its format; every text
    the block publishes that names a date (`persons_counted.leaves`) is
    counted as the part it names, against the rows whose date falls in
    it; and a pooled or held record's spans and buckets
    (`persons_counted.spans_few`, `grain_groups`) with each row its own
    holder.
    """
    settings = described["settings"]
    members = {pair[0]: pair[1] for pair in settings.get("forced_date_counts", [])} \
        if isinstance(settings, dict) else {}
    few = 0
    named: "list[str]" = []
    dated: "list[str]" = []
    for block in described["columns"]:  # type: ignore[union-attr]
        name = block["name"]
        grain = block.get("time_grain")
        if name not in names or not (block.get("role") == "datetime" or isinstance(grain, dict)):
            continue
        dated += [name]
        raw = columns[names.index(name)]
        rows = [f"{place}" for place in range(len(raw))]
        member = members.get(name, "")
        values = persons_counted.at_the_grain(raw, block, member)
        shown = f"{block.get('format', '')}"
        on: "dict[str, int]" = {}
        for cell, at in zip(raw, values):
            if not parsing.folded(cell) or parsing.folded(cell) in persons_counted._NOBODY:
                continue
            text = at if at != cell else ""
            if not text and member:
                text = persons_counted._counted_day(cell, member) or ""
            elif not text and shown:
                read = parsing.parse_datetime(cell, shown)
                text = read[0] if read is not None else ""
            for part in parts_of(text):
                on[part] = on.get(part, 0) + 1
        texts, _numbers = persons_counted.leaves(block)
        for text in sorted(texts):
            mine = parts_of(text)
            if mine and 0 < on.get(mine[0], 0) < FLOOR:
                few += 1
                named += [f"{name}={text}"]
        if isinstance(grain, dict):
            groups = persons_counted.spans_few(raw, rows, block, member)
            groups += persons_counted.grain_groups(raw, values, rows, block, member)
            few += len(groups)
            named += [f"{name}:{group}" for group in groups]
    return {"few": few, "named": named, "dated": dated, "counted_in": "rows"}


def printed(text: str, dated: "list[str]", names: "list[str]", columns: "list[list[str]]",
            people: "list[list[str]]", described: "dict[str, object]") -> "list[str]":
    """The real dates one to ten people (else rows: by their day) hold whose text the description prints anywhere.

    Lane E0c's leak scan, read as a search of the column's own block: each
    cell of a date column, as written and as its canonical form (in rows
    its day), held by one to ten people under some person column, or, with
    none, whose day one to ten rows fall on. A bucket start a pooled or
    held record names at a month, a quarter or a year (`1962-01-01` for
    1962) names that bucket, not a day, and is not searched for.
    """
    blocks = {block["name"]: block for block in described["columns"]}  # type: ignore[union-attr]
    found: "set[str]" = set()
    rows = [[f"{row}" for row in range(len(columns[0]))]] if columns else []
    for name in dated:
        raw = columns[names.index(name)]
        canonical: "dict[str, str]" = {}
        keys: "list[str]" = []
        for cell in raw:
            folded = parsing.folded(cell)
            if not folded or folded in persons_counted._NOBODY:
                keys += [""]
                continue
            if cell not in canonical:
                canonical[cell] = ""
                for shown in _READINGS:
                    read = parsing.parse_datetime(cell, shown)
                    if read is not None:
                        # in people the value as the block writes it; in rows its day
                        canonical[cell] = read[0] if people else read[0][:10]
                        break
            keys += [cell if people else (canonical[cell] or cell)]
        grain = blocks[name].get("time_grain") if name in blocks else None
        starts: "set[str]" = set()
        if isinstance(grain, dict):
            if [rung for rung, _first, _last in grain.get("spans", []) if rung in _ABOVE_THE_DAY]:
                starts = persons_counted.bucket_names(grain)
            if grain.get("rung") in _ABOVE_THE_DAY:
                starts |= set(persons_counted.at_the_grain(raw, blocks[name]))
            starts |= {start[:10] for start in starts}
        own = json.dumps(blocks[name], indent=2) if name in blocks else text
        written: "dict[str, set[str]]" = {}
        for cell, key in zip(raw, keys):
            if key:
                written.setdefault(key, set()).update({cell, canonical.get(cell, "")} - {""})
        for column in people or rows:
            holders: "dict[str, set[str]]" = {}
            for key, holder in zip(keys, column):
                if key:
                    holders.setdefault(key, set()).add(persons_counted.subject_of(holder) if people else holder)
            for key, who in holders.items():
                if len(who) >= FLOOR:
                    continue
                for form in written[key] - starts:
                    if f'"{form}' in own or f" {form}" in own:
                        found.add(f"{name}={form}")
    return sorted(found)


_ABOVE_THE_DAY = ("year", "quarter", "month")
_READINGS = ("iso-datetime", "iso-date", "month-first-date", "textual-day-first-date")
