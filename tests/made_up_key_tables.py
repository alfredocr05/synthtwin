"""Invented tables of keys and codes a twin must never write as real ones (lane ID-ROOM4, plan P4-D489).

Two invented tables, each a fixed function of its row count, with generic names (nothing here is a
real form or comes from a real table; a health table can hold every shape below):

THE CODE TABLE (no person column; 2,000 codes of ten rows each unless said): ``e5`` codes ``1e400``
to ``9e622`` (one figure, a small ``e``, three figures from 400); ``E5`` the same with a capital E;
``e5nine`` nine codes ``1e400`` to ``9e400`` among codes written ``dE+1ddd``; ``e6`` a two-figure
mantissa; ``neg`` a leading minus; ``small`` ``e-400`` onward; ``paren`` a minus inside brackets,
``(-1)`` onward; ``e6one`` two-figure codes one a row; ``e5seven`` codes from ``1e700``; ``zpad7``
seven figures zero-padded; ``numoor`` and ``numpar`` decimals with 45 stragglers ``Ne999`` or
``(-N)``.

THE PERSON TABLE (2,000 people of ten rows each): ``pid`` the person key ``S10000`` onward; ``pkey``
a second key one a person (``P100000`` onward); ``pnum`` six figures one a person; ``rand7`` random
seven figures one a person; ``zp8`` eight figures zero-padded one a person; ``enc`` an encounter
key ``E1000000`` onward, five encounters a person and two rows each; ``encnum`` the same encounters
in figures; ``visit1`` a key one a row; ``k4`` a letter and four figures one a person; ``k4num``
four figures one a person; ``wt`` a whole number fixed per person (45 to 140); ``hr`` a whole number
a row (48 to 130).

`run` puts a table through the commands a person types (profile with nobody at the keyboard and
the owner's table floor on, an answers round where asked, generate seed 0, validate) and counts,
per column, the twin cells equal to a present real cell of that column exactly, case-folded and by
merged key (`parsing.merged_key`, the form people are counted by), with counters linear in the
cells (the real cells in sets, each twin cell read once). Counts only: no value is printed.
"""

from __future__ import annotations

import contextlib
import csv
import io
import json
import pathlib
import random
import re
import time

from synthtwin import cli
from synthtwin import parsing
from synthtwin import reading
from synthtwin import taxonomy

CODE_COLUMNS = (
    "e5", "E5", "e5nine", "e6", "neg", "small", "paren", "e6one", "e5seven", "zpad7", "numoor", "numpar",
)
# The code columns whose codes group rows alike, and the one a row: what `--identifier` names in the
# code table's identifier mode (declaring the two decimal columns too would count the people by
# them and the floor would refuse the table).
CODES_DECLARED = ("e5", "E5", "e5nine", "e6", "neg", "small", "paren", "e6one", "e5seven")
# The columns lane ID-ROOM4's dry run reaches in the code table (every one written in the made-up
# figure writer's grammar or past a double's range; zpad7 and the two decimal columns are read
# otherwise).
CODES_UNREPRESENTABLE = CODES_DECLARED

PERSON_COLUMNS = ("pid", "pkey", "pnum", "rand7", "zp8", "enc", "encnum", "visit1", "k4", "k4num", "wt", "hr")
KEY_COLUMNS = PERSON_COLUMNS[:10]
# The keys of letters and figures that repeat on a person's rows beside a declared person key: what
# the people arm of lane HX5's rule reaches (plan P4-D489, part A2).
SECOND_KEYS = ("pkey", "enc", "k4")


def code_table(rows: int) -> "tuple[list[str], list[list[str]]]":
    """The code table at ``rows`` rows (ten rows a code): its header and its rows."""
    draw = random.Random(4004)
    body: "list[list[str]]" = []
    for row in range(rows):
        code = row // 10
        nine = f"{1 + code % 9}e400" if code < 9 else f"{1 + code % 9}E+{1000 + code // 9}"
        measured = f"{draw.uniform(1.0, 500.0):.1f}"
        outside = measured
        bracketed = measured
        if row % 400 < 9 and row // 400 < 5:
            outside = f"{1 + row % 400}e999"
            bracketed = f"(-{1 + row % 400})"
        body += [[
            f"{1 + code % 9}e{400 + code // 9}",
            f"{1 + code % 9}E{400 + code // 9}",
            nine,
            f"{10 + code % 90}e{400 + code // 90}",
            f"-{1 + code % 9}e{400 + code // 9}",
            f"{1 + code % 9}e-{400 + code // 9}",
            f"(-{1 + code})",
            f"{10 + row % 90}e{400 + row // 90}",
            f"{1 + code % 9}e{700 + code // 9}",
            f"{1 + code:07d}",
            outside,
            bracketed,
        ]]
    return list(CODE_COLUMNS), body


def person_table(rows: int) -> "tuple[list[str], list[list[str]]]":
    """The person table at ``rows`` rows (a tenth as many people, ten rows each): its header and rows."""
    people = max(rows // 10, 1)
    draw = random.Random(5005)
    sevens = draw.sample(range(1000000, 9999999), people)
    weights = [draw.randint(45, 140) for _each in range(people)]
    body: "list[list[str]]" = []
    for row in range(rows):
        person = row % people
        visit = row // people
        encounter = person * 5 + visit // 2
        body += [[
            f"S{10000 + person}",
            f"P{100000 + person}",
            f"{500000 + person}",
            f"{sevens[person]}",
            f"{3000 + person:08d}",
            f"E{1000000 + encounter}",
            f"{7000000 + encounter}",
            f"V{2000000 + row}",
            f"K{1000 + person}",
            f"{3000 + person}",
            f"{weights[person]}",
            f"{draw.randint(48, 130)}",
        ]]
    return list(PERSON_COLUMNS), body


SERIAL_COLUMNS = ("serial", "level")


def serial_table(rows: int) -> "tuple[list[str], list[list[str]]]":
    """A device table: ``serial`` numbers written a figure, a capital E and four figures (``1E0800``
    onward, ten rows each, numbers past a double's range when read as figures) beside ``level``, a
    decimal reading a row."""
    draw = random.Random(6006)
    body: "list[list[str]]" = []
    for row in range(rows):
        code = row // 10
        body += [[f"{1 + code % 9}E{800 + code // 9:04d}", f"{draw.uniform(1.0, 90.0):.1f}"]]
    return list(SERIAL_COLUMNS), body


PEOPLE_CODE_COLUMNS = ("pid", "code", "code3", "hr")


def people_code_table(rows: int) -> "tuple[list[str], list[list[str]]]":
    """Codes held by few people (skeptic 1 of lane ID-ROOM4, item 2): ``pid`` the person key ``S10000``
    onward, twenty rows a person (a twentieth as many people: 1,000 at 20,000 rows); ``code`` one code a
    person in the made-up figure writer's grammar (``1e400`` onward), each on the twenty rows of ONE
    person; ``code3`` one code for every three people (``1e500`` onward); ``hr`` a whole number a row."""
    draw = random.Random(7007)
    body: "list[list[str]]" = []
    for row in range(rows):
        person = row // 20
        third = person // 3
        body += [[
            f"S{10000 + person}",
            f"{1 + person % 9}e{400 + person // 9}",
            f"{1 + third % 9}e{500 + third // 9}",
            f"{draw.randint(48, 130)}",
        ]]
    return list(PEOPLE_CODE_COLUMNS), body


def repaired_table(which: str, rows: int) -> "tuple[list[str], list[list[str]]]":
    """The tables of repair 2's reproductions, each at ``rows`` rows (the reviews of lane ID-ROOM4's repair 1).

    ``codes-beside-long``: codes `1e-400` onward ten rows each, then ten cells of a number of 100 figures
    and ten of 310, beside a decimal (the verify's item 1: the column could not generate).
    ``codes-text``: codes `1e400` onward ten rows each and eleven cells `t10000` (Codex's item 5), at
    least ``rows``. ``nines``: 2,000 people over the rows and a key `8,900` onward with comma thousands,
    `9999` bare (Codex's item 3). ``persons-groups``: a person key and a second key one a person with a
    pulse between them (Codex's item 2, read in groups). ``codes-folded``: codes `1e400` onward, each
    written once with a small `e` and once with a capital `E`, one row a spelling, beside a pulse: a
    column spelled wider whose every value has a folded partner (Codex's item 4, the writer's time).
    """
    people = max(rows // 10, 1)
    body: "list[list[str]]" = []
    if which == "codes-beside-long":
        cells: "list[str]" = []
        for index in range(max((rows - 20) // 10, 1)):
            cells += [f"{index % 9 + 1}e-{400 + index // 9}"] * 10
        cells += [f"{10 ** 99 + 12345}"] * 10 + [f"{10 ** 309 + 54321}"] * 10
        return ["s", "dec"], [[cells[row], f"{(row * 37) % 1000 / 10:.1f}"] for row in range(len(cells))]
    if which == "codes-text":
        cells = []
        for index in range(max((rows - 11 + 9) // 10, 1)):
            cells += [f"{index % 9 + 1}e{400 + index // 9}"] * 10
        cells += ["t10000"] * 11
        return ["code", "hr"], [[cells[row], f"{60 + (row * 7) % 40}"] for row in range(len(cells))]
    if which == "nines":
        for row in range(rows):
            value = 8900 + row % people
            body += [[f"S{10000 + row % people}", "9999" if value == 9999 else f"{value:,}", f"{60 + (row * 7) % 40}"]]
        return ["pid", "v", "hr"], body
    if which == "persons-groups":
        for row in range(rows):
            body += [[f"S{10000 + row % people}", f"{60 + (row * 7) % 40}", f"P{100000 + row % people}"]]
        return ["pid", "hr", "pkey"], body
    if which == "codes-folded":
        cells = []
        for index in range(max(rows // 2, 1)):
            code = f"{index % 9999 + 1}e{400 + index // 9999}"
            cells += [code, code.upper()]
        return [FOLDED_COLUMN, "hr"], [[cells[row], f"{60 + (row * 7) % 40}"] for row in range(len(cells))]
    raise ValueError(f"no such table: {which}")


REPAIRED = ("codes-beside-long", "codes-text", "nines", "persons-groups", "codes-folded")
# The one column of ``codes-folded``, whose twin cells the timed runs count beside the code table's.
FOLDED_COLUMN = "fold"
# The modes read in groups, one column a group and a walk, as a table too large to read whole is read.
GROUPED = ("persons-groups-declared",)


def _flags(word: str, names: "tuple[str, ...]") -> "list[str]":
    found: "list[str]" = []
    for name in names:
        found += [f"--{word}", name]
    return found


# THE PERSON QUESTION ANSWERED AS THE ZOO ANSWERS IT (skeptic 1 of lane ID-ROOM4, item 1; THE ZOO
# ANSWERS TRUTHFULLY): the person key names the people, and a key beside it is "not a person: it
# repeats for some other reason". Then the people's own question of those keys, answered.
TRUTHFUL = {"pid": "identifier", "pkey": "keep", "enc": "keep", "k4": "keep"}
# The words the people's own question says it saw (`asking.on_one_persons_rows`).
OWN_QUESTION_SEEN = "as a second patient number or an encounter number does"
OWN_IDENTIFIER = {name: "identifier" for name in SECOND_KEYS}
OWN_KEEP = {name: "keep" for name in SECOND_KEYS}

# Each mode: the table, the flags typed, and the answers written into the questions file before a
# second profile (column -> answer), or a tuple of such rounds, each before one more profile, or None.
MODES: "dict[str, tuple[str, list[str], dict[str, str] | tuple[dict[str, str], ...] | None]]" = {
    "codes-unanswered": ("codes", [], None),
    "codes-measurement": ("codes", _flags("measurement", CODE_COLUMNS), None),
    "codes-code": ("codes", _flags("code", CODE_COLUMNS), None),
    "codes-identifier": ("codes", _flags("identifier", CODES_DECLARED), None),
    "codes-answered-measurement": ("codes", [], {name: "measurement" for name in CODES_UNREPRESENTABLE}),
    "codes-answered-code": ("codes", [], {name: "code" for name in CODES_UNREPRESENTABLE}),
    "persons-declared": ("persons", ["--identifier", "pid"], None),
    "persons-unanswered": ("persons", [], None),
    "persons-every-key": ("persons", _flags("identifier", KEY_COLUMNS), None),
    # `--person` (lane EZ-a, plan P4-D479): a tree without it refuses the option.
    "persons-person": ("persons", ["--person", "pid"], None),
    "persons-declared-keep": ("persons", ["--identifier", "pid"], {name: "keep" for name in SECOND_KEYS}),
    "persons-declared-code": ("persons", ["--identifier", "pid"], {name: "code" for name in SECOND_KEYS}),
    "persons-declared-identifier": (
        "persons", ["--identifier", "pid"], {name: "identifier" for name in SECOND_KEYS},
    ),
    "persons-declared-measurement": ("persons", ["--identifier", "pid"] + _flags("measurement", SECOND_KEYS), None),
    "serials-measurement": ("serials", ["--measurement", "serial"], None),
    "codes-slim-unanswered": ("codes-slim", [], None),
    "persons-slim-declared": ("persons-slim", ["--identifier", "pid"], None),
    # The person question answered as the zoo answers it, then the people's own question (skeptic 1
    # of lane ID-ROOM4, item 1): the keys stay held until that question itself is answered.
    "persons-truthful-keep": ("persons", [], (TRUTHFUL,)),
    "persons-own-identifier": ("persons", [], (TRUTHFUL, OWN_IDENTIFIER)),
    "persons-own-keep": ("persons", [], (TRUTHFUL, OWN_KEEP)),
    # Codes held by few people, the person question open and with the person key declared (item 2).
    "people-codes-unanswered": ("people-codes", [], None),
    "people-codes-declared": ("people-codes", ["--identifier", "pid"], None),
    # The code table answered `code` in a questions file written as the base wrote it, each code
    # column a checklist entry (the statistics check of lane ID-ROOM4, item 3): a held column leaves
    # the checklist, so the head's own file offers no entry to answer.
    "codes-base-answered-code": ("codes", [], ({},)),
    # Repair 2's reproductions at the table floor (Codex's items 1 to 3 and 5, the verify's item 1).
    "codes-beside-long-unanswered": ("codes-beside-long", [], None),
    "codes-text-unanswered": ("codes-text", [], None),
    "nines-declared": ("nines", ["--identifier", "pid"], None),
    "persons-groups-declared": ("persons-groups", ["--identifier", "pid"], None),
}
# The modes whose answers round adds the base's checklist entries first: (the answer, the columns).
BASE_CHECKLIST = {"codes-base-answered-code": ("code", CODES_UNREPRESENTABLE)}


# The suite's two 20,000-row cases read fewer columns, so the gate file keeps to its three CPU minutes:
# each family of the writer's grammar that A1 reaches once (exact, a capital E, a zero-padded mantissa,
# a minus, a minus in brackets), the codes off the writer's start and a decimal column beside them; and
# the person key, the three second keys and two measurements.
SLIM = {
    "codes-slim": ("e5", "E5", "e6", "neg", "paren", "e5seven", "numoor"),
    "persons-slim": ("pid", "pkey", "enc", "k4", "wt", "hr"),
    # ...and one column of codes one a row, the shape whose held writer grew fastest (the statistics
    # check of lane ID-ROOM4, item 1): what the writer's time is measured on.
    "codes-one-a-row": ("e6one",),
}


def _slim(table: "tuple[list[str], list[list[str]]]", names: "tuple[str, ...]") -> "tuple[list[str], list[list[str]]]":
    header, body = table
    places = [header.index(name) for name in names]
    return list(names), [[row[place] for place in places] for row in body]


def table_of(which: str, rows: int) -> "tuple[list[str], list[list[str]]]":
    """The named table (``codes``, ``persons``, ``serials``, or a slim one of `SLIM`) at ``rows`` rows."""
    if which == "codes":
        return code_table(rows)
    if which == "persons":
        return person_table(rows)
    if which == "serials":
        return serial_table(rows)
    if which == "codes-slim":
        return _slim(code_table(rows), SLIM[which])
    if which == "persons-slim":
        return _slim(person_table(rows), SLIM[which])
    if which == "people-codes":
        return people_code_table(rows)
    if which == "codes-one-a-row":
        return _slim(code_table(rows), SLIM[which])
    if which in REPAIRED:
        return repaired_table(which, rows)
    raise ValueError(f"no such table: {which}")


def write_table(path: pathlib.Path, header: "list[str]", body: "list[list[str]]") -> pathlib.Path:
    """Write the table as a comma-separated file; its path."""
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(body)
    return path


def columns_of(path: pathlib.Path) -> "dict[str, list[str]]":
    """Every column of a comma-separated file, by name."""
    with open(path, encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        found: "dict[str, list[str]]" = {name: [] for name in header}
        for row in reader:
            for place in range(len(header)):
                found[header[place]].append(row[place] if place < len(row) else "")
    return found


def equal_cells(real: "list[str]", twin: "list[str]") -> "dict[str, int]":
    """Twin cells equal to a present real cell: exactly, case-folded and by merged key; linear.

    The real present cells go into three sets once; each twin cell is read once. A blank cell is no
    value on either side.
    """
    exact: "dict[str, bool]" = {}
    folded: "dict[str, bool]" = {}
    merged: "dict[str, bool]" = {}
    for cell in real:
        if not cell.strip():
            continue
        exact[cell] = True
        folded[parsing.folded(cell)] = True
        merged[parsing.merged_key(cell)] = True
    counts = {"equal": 0, "folded": 0, "merged": 0, "values": 0}
    named: "dict[str, bool]" = {}
    for cell in twin:
        if not cell.strip():
            continue
        if cell in exact:
            counts["equal"] += 1
            named[cell] = True
        if parsing.folded(cell) in folded:
            counts["folded"] += 1
        if parsing.merged_key(cell) in merged:
            counts["merged"] += 1
    counts["values"] = len(named)
    return counts


_TOKEN = re.compile(r"[A-Za-z0-9+\-().]+")


# The product's own fixed marks, which its sentences print whatever the table holds (the Safe Harbor
# top-code of ages in years, months, weeks and days, `taxonomy.TOP_CODE_MARKS`): a key of the same
# figures is no value the run published.
_PRODUCT_MARKS = {f"{mark}" for mark in taxonomy.TOP_CODE_MARKS}


def real_in_texts(texts: "list[str]", real: "dict[str, bool]") -> int:
    """How many tokens of the texts are a real value (each text read once, its tokens looked up).

    The product's own fixed marks (`_PRODUCT_MARKS`) are not counted.
    """
    found = 0
    for text in texts:
        for token in _TOKEN.findall(text):
            for form in (token, token.strip("()."), token.rstrip(".")):
                if form in real and form not in _PRODUCT_MARKS:
                    found += 1
                    break
    return found


def _quietly(arguments: "list[str]", screen: "list[str]") -> int:
    sink = io.StringIO()
    with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
        code = cli.main(arguments, small_tables_refused=True)
    screen += [sink.getvalue()]
    return int(code)


@contextlib.contextmanager
def nobody_at_the_keyboard():
    """A scripted run, whatever terminal it is started from (the zoo's and lane HX's rule)."""
    asked = cli._there_is_somebody_to_ask
    cli._there_is_somebody_to_ask = lambda: False
    try:
        yield
    finally:
        cli._there_is_somebody_to_ask = asked


def answered(
    questions: pathlib.Path,
    answers: "dict[str, str]",
    base_checklist: "tuple[str, tuple[str, ...]] | None" = None,
) -> "dict[str, str]":
    """Write each named column's answer into the questions file where its entry offers it; what was written.

    ``base_checklist`` (an answer and columns) first adds, for each named column the checklist does not
    list, a checklist entry built as the checklist's own entries are (a copy of its first, renamed,
    read as `measurement`), answered so: the file an earlier version wrote for a column it listed.
    """
    document = json.loads(questions.read_text(encoding="utf-8"))
    if base_checklist is not None:
        answer, names = base_checklist
        listed = document.get("checklist")
        columns = listed.get("columns") if isinstance(listed, dict) else None
        if isinstance(columns, list) and columns and isinstance(columns[0], dict):
            there = {f"{entry.get('column')}" for entry in columns if isinstance(entry, dict)}
            for name in names:
                if name in there:
                    continue
                entry = json.loads(json.dumps(columns[0]))
                entry["column"] = name
                entry["read_as_now"] = "measurement"
                entry["your_answer"] = ""
                columns += [entry]
            answers = dict(answers)
            for name in names:
                answers.setdefault(name, answer)
    written: "dict[str, str]" = {}
    entries: "list[dict[str, object]]" = []
    for part in ("asked", "about_your_file"):
        if isinstance(document.get(part), list):
            entries += [entry for entry in document[part] if isinstance(entry, dict)]
    checklist = document.get("checklist")
    if isinstance(checklist, dict) and isinstance(checklist.get("columns"), list):
        entries += [entry for entry in checklist["columns"] if isinstance(entry, dict)]
    for entry in entries:
        name = f"{entry.get('column') or ''}"
        if name not in answers or name in written:
            continue
        offered = [
            f"{choice.get('answer')}" for choice in entry.get("answers_you_can_give") or [] if isinstance(choice, dict)
        ]
        if answers[name] in offered:
            entry["your_answer"] = answers[name]
            written[name] = answers[name]
    questions.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
    return written


def _rounds(
    mode: str,
    which: str,
    source: pathlib.Path,
    folder: pathlib.Path,
    flags: "list[str]",
    rounds: "tuple[dict[str, str], ...]",
    screen: "list[str]",
    written: "dict[str, str]",
) -> "list[int]":
    """One mode's commands: profile, each answers round, generate (seed 0) and validate; their exits."""
    profiled = f"{folder / which}-profile.json"
    exits = [_quietly(["profile", f"{source}", "--out-dir", f"{folder}", "--replace"] + flags, screen)]
    for each in rounds:
        if exits[-1] != 0:
            break
        questions = folder / f"{which}-questions.json"
        written.update(answered(questions, each, BASE_CHECKLIST.get(mode)))
        exits += [_quietly(
            ["profile", f"{source}", "--out-dir", f"{folder}", "--replace", "--answers", f"{questions}"] + flags,
            screen,
        )]
    exits += [_quietly(["generate", profiled, "--out-dir", f"{folder}", "--seed", "0", "--replace"], screen)]
    exits += [_quietly(
        ["validate", profiled, "--twin", f"{folder / which}-twin.csv", "--out-dir", f"{folder}", "--replace"],
        screen,
    )]
    return exits


def run(folder: pathlib.Path, mode: str, rows: int = 20000) -> "dict[str, object]":
    """Put one mode's table through profile, the answers round, generate (seed 0) and validate; the counts.

    Returns the exits, the wall and CPU seconds of the commands, the answers written, each column's
    role in the final description and its twin cells equal to a real cell of it (`equal_cells`), and
    how many real key or code values stand in the description, the summary, the questions file and
    on the screen (`real_in_texts`).
    """
    which, flags, answers = MODES[mode]
    folder.mkdir(parents=True, exist_ok=True)
    header, body = table_of(which, rows)
    source = write_table(folder / f"{which}.csv", header, body)
    del body
    screen: "list[str]" = []
    exits: "list[int]" = []
    written: "dict[str, str]" = {}
    began = time.perf_counter()
    cpu = time.process_time()
    profiled = f"{folder / which}-profile.json"
    rounds: "tuple[dict[str, str], ...]" = ()
    if isinstance(answers, dict):
        rounds = (answers,)
    elif answers is not None:
        rounds = answers
    budgets = (reading.GROUP_BYTES, reading.WALK_BYTES)
    if mode in GROUPED:
        reading.GROUP_BYTES = 1
        reading.WALK_BYTES = 1
    try:
        with nobody_at_the_keyboard():
            exits += _rounds(mode, which, source, folder, flags, rounds, screen, written)
    finally:
        reading.GROUP_BYTES, reading.WALK_BYTES = budgets
    seen: "dict[str, object]" = {
        "mode": mode, "rows": rows, "exits": exits, "answered": written,
        "seconds": round(time.perf_counter() - began, 1), "cpu_seconds": round(time.process_time() - cpu, 1),
    }
    real = columns_of(source)
    twin_path = folder / f"{which}-twin.csv"
    twin = columns_of(twin_path) if twin_path.is_file() else {}
    roles: "dict[str, str]" = {}
    description = pathlib.Path(profiled)
    if description.is_file():
        for block in json.loads(description.read_text(encoding="utf-8")).get("columns", []):
            if isinstance(block, dict):
                roles[f"{block.get('name')}"] = f"{block.get('role')}"
    keys = {
        "persons": KEY_COLUMNS, "codes": CODE_COLUMNS[:10], "serials": SERIAL_COLUMNS[:1],
        "codes-slim": SLIM["codes-slim"][:-1], "persons-slim": SLIM["persons-slim"][:4],
        "people-codes": PEOPLE_CODE_COLUMNS[:3],
        "codes-beside-long": ("s",), "codes-text": ("code",), "nines": ("pid", "v"), "persons-groups": ("pid", "pkey"),
    }[which]
    columns: "dict[str, object]" = {}
    present: "dict[str, dict[str, bool]]" = {}
    for name in keys:
        present[name] = {cell: True for cell in real[name] if cell.strip()}
    for name in header:
        counts: "dict[str, object]" = dict(equal_cells(real[name], twin.get(name, [])))
        counts["role"] = roles.get(name, "")
        # ...and the twin cells equal to a real key or code of ANOTHER column (part b's item B1).
        counts["another"] = {
            other: hits
            for other in keys
            if other != name
            for hits in [sum(1 for cell in twin.get(name, []) if cell in present[other])]
            if hits
        }
        columns[name] = counts
    seen["columns"] = columns
    values: "dict[str, bool]" = {}
    for name in keys:
        for cell in real[name]:
            if cell.strip():
                values[cell] = True
    texts = list(screen)
    for path in sorted(folder.glob(f"{which}-*")):
        if path.suffix in (".json", ".txt", ".md", ".html") and path.is_file():
            texts += [path.read_text(encoding="utf-8", errors="replace")]
    seen["real_in_files_and_screen"] = real_in_texts(texts, values)
    # ...and validate's own outcome: its exit and whether its quality report was written (Codex's review
    # of lane ID-ROOM4, item 8): None where no report stands.
    seen["validated"] = exits[-1]
    seen["misses"] = missed_facts(folder / f"{which}-twin-quality.txt")
    return seen


def run_own_question(folder: pathlib.Path, rows: int = 20000, which: str = "persons-slim") -> "dict[str, object]":
    """The people's own question in its four modes, on one table, sharing its rounds (skeptic 1 of lane ID-ROOM4, item 1).

    Round 1 with nothing declared, generated (``nothing``); the person question answered as the zoo
    answers it (`TRUTHFUL`), generated (``person-keep``); then from that round's questions file the
    people's own question answered `identifier` (``own-identifier``) and, from the same file again,
    `keep` (``own-keep``), each generated (seed 0). Returns, for each mode, the exits and each second
    key's role and twin cells equal to a real key (`equal_cells`), and how many real key values stand
    in the files and on the screen over every round.
    """
    folder.mkdir(parents=True, exist_ok=True)
    header, body = table_of(which, rows)
    source = write_table(folder / f"{which}.csv", header, body)
    del body
    real = columns_of(source)
    screen: "list[str]" = []
    questions = folder / f"{which}-questions.json"
    profiled = f"{folder / which}-profile.json"
    seen: "dict[str, object]" = {}
    began = time.process_time()

    def generated(mode: str, codes: "list[int]") -> None:
        codes += [_quietly(["generate", profiled, "--out-dir", f"{folder}", "--seed", "0", "--replace"], screen)]
        roles: "dict[str, str]" = {}
        described = json.loads(pathlib.Path(profiled).read_text(encoding="utf-8"))
        for block in described.get("columns", []):
            if isinstance(block, dict):
                roles[f"{block.get('name')}"] = f"{block.get('role')}"
        twin = columns_of(folder / f"{which}-twin.csv")
        columns: "dict[str, object]" = {}
        for name in SECOND_KEYS:
            counts: "dict[str, object]" = dict(equal_cells(real[name], twin.get(name, [])))
            counts["role"] = roles.get(name, "")
            columns[name] = counts
        seen[mode] = {
            "exits": codes, "columns": columns, "person_columns": list(described.get("settings", {}).get("person_columns", [])),
        }

    def profiled_with(answers: "dict[str, str] | None") -> int:
        arguments = ["profile", f"{source}", "--out-dir", f"{folder}", "--replace"]
        if answers is not None:
            answered(questions, answers)
            # An answered round of a table one person stands on several rows of may be the first to publish between
            # columns (the patient layer, lane W5-PL): the record of earlier descriptions then asks for
            # --replace-description, as the earlier round's screen says it will.
            arguments += ["--answers", f"{questions}", "--replace-description"]
        return _quietly(arguments, screen)

    with nobody_at_the_keyboard():
        first = [profiled_with(None)]
        generated("nothing", first)
        second = [profiled_with(TRUTHFUL)]
        generated("person-keep", second)
        kept = questions.read_text(encoding="utf-8")
        # ...and what the people's own question says each key is read as meanwhile: the held reading.
        seen["own_read_as_now"] = {
            f"{entry.get('column')}": f"{entry.get('read_as_now')}"
            for entry in json.loads(kept).get("asked", [])
            if isinstance(entry, dict) and OWN_QUESTION_SEEN in f"{entry.get('what_synthtwin_saw')}"
        }
        third = [profiled_with(OWN_IDENTIFIER)]
        generated("own-identifier", third)
        questions.write_text(kept, encoding="utf-8", newline="\n")
        fourth = [profiled_with(OWN_KEEP)]
        generated("own-keep", fourth)
    values: "dict[str, bool]" = {}
    for name in SLIM["persons-slim"][:4]:
        for cell in real[name]:
            if cell.strip():
                values[cell] = True
    texts = list(screen)
    for path in sorted(folder.glob(f"{which}-*")):
        if path.suffix in (".json", ".txt", ".md", ".html") and path.is_file():
            texts += [path.read_text(encoding="utf-8", errors="replace")]
    seen["real_in_files_and_screen"] = real_in_texts(texts, values)
    seen["cpu_seconds"] = round(time.process_time() - began, 1)
    return seen


def generate_cpu(folder: pathlib.Path, which: str, rows: int) -> "dict[str, object]":
    """One table profiled with nothing declared, then generated (seed 0), the generate step's CPU seconds apart.

    Returns the exits, the CPU seconds of profile and of generate (user and system, this process),
    and each code column's role and twin cells equal to a real code (`equal_cells`). The table is
    deleted after the counts.
    """
    folder.mkdir(parents=True, exist_ok=True)
    header, body = table_of(which, rows)
    source = write_table(folder / f"{which}.csv", header, body)
    del body
    screen: "list[str]" = []

    def cpu() -> float:
        return time.process_time()

    with nobody_at_the_keyboard():
        began = cpu()
        exits = [_quietly(["profile", f"{source}", "--out-dir", f"{folder}", "--replace"], screen)]
        profiled = cpu() - began
        began = cpu()
        exits += [_quietly(
            ["generate", f"{folder / which}-profile.json", "--out-dir", f"{folder}", "--seed", "0", "--replace"], screen,
        )]
        generated = cpu() - began
    real = columns_of(source)
    twin_path = folder / f"{which}-twin.csv"
    twin = columns_of(twin_path) if twin_path.is_file() else {}
    roles: "dict[str, str]" = {}
    for block in json.loads((folder / f"{which}-profile.json").read_text(encoding="utf-8")).get("columns", []):
        if isinstance(block, dict):
            roles[f"{block.get('name')}"] = f"{block.get('role')}"
    columns: "dict[str, object]" = {}
    for name in header:
        if name not in CODE_COLUMNS[:9] + (FOLDED_COLUMN,):
            continue
        counts: "dict[str, object]" = dict(equal_cells(real[name], twin.get(name, [])))
        counts["role"] = roles.get(name, "")
        columns[name] = counts
    for path in folder.glob("*"):
        if path.is_file():
            path.unlink()
    return {
        "which": which, "rows": rows, "exits": exits, "profile_cpu": round(profiled, 1),
        "generate_cpu": round(generated, 1), "columns": columns,
    }


def missed_facts(quality: pathlib.Path) -> "list[list[str]] | None":
    """Each (column, fact) the validation report marks MISSED, once, in its order; None where there is no report.

    An absent report is no list of misses (Codex's review of lane ID-ROOM4, item 8: read as an empty one,
    a validation refused with no report counted as a validation that missed nothing).
    """
    if not quality.is_file():
        return None
    found: "list[list[str]]" = []
    column = ""
    for line in quality.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("'") and line.endswith("'") and len(line) > 1:
            column = line[1:-1]
        elif line.strip().endswith(": MISSED") and column:
            fact = [column, line.strip()[: -len(": MISSED")]]
            if fact not in found:
                found += [fact]
    return found


# K-HZ-39's driver's modes, in its order (the driver adds `persons-person` where the tree has `--person`).
DRIVER_MODES = (
    "codes-unanswered", "codes-measurement", "codes-code", "codes-identifier", "codes-base-answered-code",
    "persons-declared", "persons-unanswered", "persons-every-key", "persons-declared-code",
    "persons-declared-keep", "persons-declared-measurement", "serials-measurement",
    # The people's own question (skeptic 1 of lane ID-ROOM4, item 1): the person question answered as
    # the zoo answers it, then that question answered identifier and keep.
    "persons-truthful-keep", "persons-own-identifier", "persons-own-keep",
    # Codes held by few people, the person question open and the person key declared (items 2 and 3).
    "people-codes-unanswered", "people-codes-declared",
    # Repair 2's reproductions (Codex's items 1 to 3 and 5, the verify's item 1): codes too small beside
    # numbers of 100 and 310 figures, codes beside eleven cells `t10000`, a key in sequence across 9,999
    # with comma thousands save `9999`, and a second key beside the person key read one column a group.
    "codes-beside-long-unanswered", "codes-text-unanswered", "nines-declared", "persons-groups-declared",
)
# The column each of repair 2's reproduction modes holds, read BEFORE the code table's prefix below: their
# names begin `codes-` too, and read by that prefix they were taken for the code table's columns, so
# K-HZ-39's driver stopped at its first such mode (repair 2's first run of it, `KeyError`).
REPAIRED_HELD = {
    "codes-beside-long-unanswered": ("s",), "codes-text-unanswered": ("code",), "nines-declared": ("v",),
    "persons-groups-declared": ("pkey",),
}


def held_in(mode: str) -> "tuple[str, ...]":
    """The columns the lane holds in a mode (or a person declares), whose twin cells must name no real value (K-HZ-39).

    Repair 2's reproductions first (`REPAIRED_HELD`); then the code table's columns past a double's
    range but `e5seven`, whose codes the writer's counters never reach (its twin's equality with another
    column's codes is part b's item B1); the person table's keys where the hold applies; the codes few
    people hold. Raises nothing. No I/O.
    """
    if mode in REPAIRED_HELD:
        return REPAIRED_HELD[mode]
    if mode.startswith("codes-"):
        return tuple(name for name in CODES_UNREPRESENTABLE if name != "e5seven")
    if mode in ("persons-declared", "persons-declared-identifier", "persons-person", "persons-unanswered",
                "persons-every-key", "persons-truthful-keep", "persons-own-identifier"):
        return KEY_COLUMNS
    if mode.startswith("people-codes-"):
        return ("code", "code3")
    return ()


# CARRY C2, EXACTLY (lane HB3-b's; Codex's review of lane ID-ROOM4, item 7; LANE ID-ROOM4 RULINGS 6 (7)):
# the facts the identifier writer misses on the code table's columns past a double's range answered
# `identifier`, measured on this lane's heads -- a leading minus and the column of codes at its
# narrowest width among codes the writer never spells, eight facts on two columns of one mode. Each is
# the mode, the column and the fact's bracketed name in the quality report; any other miss on a held
# column, in any mode, is counted.
C2_MISSES = (
    ("codes-identifier", "e5nine", "[identifier.n_distinct]"),
    ("codes-identifier", "e5nine", "[identifier.n_distinct_folded]"),
    ("codes-identifier", "e5nine", "[identifier.n_code_alphabet]"),
    ("codes-identifier", "e5nine", "[identifier.n_distinct_by_occurrences]"),
    ("codes-identifier", "neg", "[identifier.n_distinct]"),
    ("codes-identifier", "neg", "[identifier.n_distinct_folded]"),
    ("codes-identifier", "neg", "[identifier.layout_forms]"),
    ("codes-identifier", "neg", "[identifier.n_distinct_by_occurrences]"),
)


# ...AND CARRY C2b, EXACTLY (lane HB3-b's, found by repair 2 of lane ID-ROOM4): the identifier writer's
# facts on a key written with comma thousands, `8,900` onward, held beside a declared person -- the same
# three misses with the key declared `--identifier` on the public head's source.
C2B_MISSES = (
    ("nines-declared", "v", "[universal.n_numeric]"),
    ("nines-declared", "v", "[universal.n_not_numeric]"),
    ("nines-declared", "v", "[identifier.all_whole_numbers]"),
)


def misses_outside_the_carries(mode: str, held: "tuple[str, ...]", misses: "list[list[str]]") -> int:
    """How many of a mode's validate misses on a column it holds are not one of carries C2 and C2b's exact misses (K-HZ-39)."""
    counted = 0
    for column, fact in misses:
        if column not in held:
            continue
        if any(
            mode == one and column == name and fact.endswith(said)
            for one, name, said in C2_MISSES + C2B_MISSES
        ):
            continue
        counted += 1
    return counted


def validation_completed(seen: "dict[str, object]") -> bool:
    """Whether a run's validate ran to its end: exit 0 (nothing missed) or 3 (misses named), its quality report written.

    Exit 1 (it could not run) or 2 (its command line could not be used), or no report, is a refusal: no
    evidence that the twin meets its description, so the measure fails rather than read it as met
    (Codex's review of lane ID-ROOM4, item 8).
    """
    return seen.get("validated") in (0, 3) and seen.get("misses") is not None
