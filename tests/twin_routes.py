"""The twin the batteries read, made by the route a person takes (lane MU, plan P4-D485).

Lane E0b's battery (`tests/analyst_battery.py`) and lane MU's
(`tests/model_utility.py`) ask what an analysis fitted on the twin says
against the real table. Which twin they read is the first thing a stamp
must name, so each is made by one of four ROUTES, and a stamp never
mixes them.

* ROUTE S, THE TWIN A PERSON GETS (the headline of every stamp): the
  commands a person types. `synthtwin profile TABLE --out-dir FOLDER`;
  then EVERY entry of the questions file it writes that is left blank
  (`about_your_file`, `asked` and the checklist's columns) is answered
  as the person who holds the table answers it, truthfully, by the zoo's
  rule (the orchestrator's ruling THE ZOO ANSWERS TRUTHFULLY;
  `health_zoo.answer_generally`) from what that person knows of each
  column (the table's KNOWS: a measurement, a code, the identifier of
  the person): the known reading where the question offers it; 'keep'
  where it does not but offers 'identifier' and 'keep'; the question
  whether a column names the people the rows are about 'identifier' for
  the person column and 'keep' for any other; an age column's Safe
  Harbor question 'yes'; any other column's Safe Harbor question 'no'.
  The subject question (can one person stand on more than one row?) is
  answered 'one row each' or with the name of the column that identifies
  the person. `synthtwin profile` runs again with `--answers` (and, where
  the screen refuses that round because the earlier round's description
  was published without its chain, once more with
  `--replace-description`, the remedy the screen names), up to three
  rounds while a round writes an answer; then
  `synthtwin generate DESCRIPTION --seed K`. Every entry still blank after
  the last round is named in what the route returns (`Described.left`)
  and in the run's notes. On a line whose typed commands do not switch
  the chain on, route S is the chain-off twin; where they do, route S is
  the switched twin, with no change here. (MEASURED by the statistics
  check of the lane: a route that left the checklist blank held ST12's
  stay column as record numbers, and through it the procedure group: a
  twin no truthful person gets.)
* ROUTE U, THE SAME COMMANDS UNSWITCHED: route S run with `cli.main`'s
  internal keyword `unswitched` (no option or environment variable sets
  it; the measured tree's commands as they ran before the chain's switch
  was shipped). Where the tree's `main` has no such keyword its typed
  commands do not switch, and route U is route S. A stamp that reads
  route U beside route S on one head measures the switch's effect as
  their difference (LANE MU RULINGS 3 (2) item 6).
* ROUTE C, THE CHAIN'S SWITCH HANDED IN (the preview, where the typed
  commands do not switch yet): `synthtwin profile` run with a
  `cli.ChainRun` handed to `cli.main` (the subject answered in advance,
  'one row each', where no column names the person; the questions file
  answered as in route S; the rule steps on and the patient layer off
  where the tree knows them, as the shipped switch sets them), then
  `contract.load_profile(..., chain=True)` and `generation.generate_held`.
* ROUTE P, THE PATIENT LAYER ON (several rows a person, until the shipped
  switch draws the layer): described as lane GRb's driver
  (`tools/measurements/kpi_patient_twin.py`) describes, the person column
  declared and the chain drawn with `chain.ROWS_PERSON`; only on a tree
  that holds the patient walk, the generator that reads the layer
  (`RouteMissing` elsewhere).

THE INSTALLATION. A switched run opens the installation's data folder (its
key, its record of descriptions, its lock, its private reports), which the
platform places from XDG_DATA_HOME or LOCALAPPDATA. Every route runs with
both pointed at a folder of its own under the run's folder, holding the
key it is given and an empty record, so no run ever reads or writes the
account's own folder and a run's chain is the same on every machine. The
key is the fixed test key (`bytes(range(32))`, as `tests/conftest.py`
hands each test) unless the caller derives one (`key_for`: lane MU's
battery draws each twin seed's twin under a key of its own, so a stamp
reads several keys and their spread).

THE FOLDERS OF A RUN. The installation folder lies OUTSIDE both the
folder that holds the table and the folder the description is written
to: the table goes in a folder of its own (`table_file`), each route's
description in its own (`out_folder`), the installation beside them
(`installation_place`). The switched commands refuse a data folder that
is, stands in or lies inside either of the two (lane CHON's repair 1,
`cli._data_folder_refusal`: the private key and the record never travel
beside the files that are shared); a harness that kept the table beside
the installation was refused there (lane MU's combined verify, its item
1: route S could not describe a table on chon's head).

BELOW THE TABLE FLOOR. `synthtwin profile` refuses a table under 20,000
rows; a table read below it here (the suite's 5,000-row fast parts, the
half of a 20,000-row table a trained model is fitted on) runs with
`cli.main`'s internal `small_tables_refused=False`: a TEST DEVICE, whose
results are no product claim (LANE I4m RULINGS 18).

Nothing here changes the product: each route runs the product's own code
and only reads what it writes.
"""

from __future__ import annotations

import contextlib
import dataclasses
import hashlib
import importlib.util
import inspect
import io
import json
import os
import pathlib
import time
from typing import Iterator

ROUTES = ("S", "C", "U", "P")
ROUTE_NAMES = {"S": "the commands a person types", "C": "the chain's switch handed in",
               "U": "the commands a person types, unswitched (an internal setting no command reaches)",
               "P": "the patient layer on"}
# The fixed test key and the empty record of `tests/conftest.py`'s installation folder.
TEST_KEY = bytes(range(32))
_DATA_FOLDER = "synthtwin"
_KEY_FILE = "chain-key"
_LEDGER_FILE = "chain-ledger"
_EMPTY_LEDGER = '{\n  "tables": [],\n  "version": 1\n}\n'


class RouteTrouble(Exception):
    """A route's command did not finish: the twin could not be made (its screen's last words kept)."""


class RouteMissing(Exception):
    """The tree measured has no such route (route P before the patient layer's generator exists)."""


def floor_rows() -> int:
    """The table floor in rows, as the measured tree's command reads it."""
    from synthtwin import parsing

    return int(getattr(parsing, "TABLE_ROW_FLOOR", 20000))


def data_rows(text: str) -> int:
    """The data rows of a table's text (its lines but the header)."""
    return max(0, text.count("\n") - 1)


def key_for(table_seed: int, twin_seed: int) -> bytes:
    """A twin seed's installation key, derived from the seeds: the SHA-256 of a fixed text naming both.

    The statistics check of lane MU (its item 10): a switched twin moves
    with the installation's key, so a stamp that read one key read one
    draw of the method; three twin seeds a table seed are three keys.
    """
    return hashlib.sha256(f"lane MU installation key, table seed {table_seed}, twin seed {twin_seed}".encode(
        "utf-8")).digest()


def typed_switched() -> bool:
    """Whether the measured tree's typed commands switch the chain on: its `cli.main` takes the internal `unswitched`."""
    from synthtwin import cli

    return "unswitched" in inspect.signature(cli.main).parameters


def keyed(route: str) -> bool:
    """Whether a route's description reads the installation's key: C and P always, S where the typed commands switch,
    U never."""
    return route in ("C", "P") or (route == "S" and typed_switched())


_TABLE_FOLDER = "table"
_INSTALLATION_FOLDER = "installation"
_OUT_SUFFIX = {"S": "typed", "U": "unswitched", "C": "switched", "P": "layer"}


def table_file(folder: pathlib.Path, stem: str) -> pathlib.Path:
    """Where a route writes the table it describes: a folder of its own under the run's folder, never holding the
    installation folder (THE FOLDERS OF A RUN)."""
    return folder / _TABLE_FOLDER / f"{stem}.csv"


def out_folder(folder: pathlib.Path, stem: str, route: str) -> pathlib.Path:
    """Where a route writes its description, the questions file and the twin: a folder of its own a route."""
    return folder / f"{stem}-{_OUT_SUFFIX[route]}"


def installation_place(folder: pathlib.Path) -> pathlib.Path:
    """The run's installation folder (XDG_DATA_HOME and LOCALAPPDATA point at it): beside the table's folder and the
    out folders, inside neither (THE FOLDERS OF A RUN). Nothing is made here."""
    return folder / _INSTALLATION_FOLDER


def installation_folder(folder: pathlib.Path, key: bytes = TEST_KEY) -> pathlib.Path:
    """A data folder of its own for one run: the given key and an empty record (made once; one key a folder)."""
    place = installation_place(folder)
    data = place / _DATA_FOLDER
    if not data.exists():
        data.mkdir(parents=True, mode=0o700)
        key_file = data / _KEY_FILE
        key_file.write_bytes(key)
        ledger = data / _LEDGER_FILE
        ledger.write_text(_EMPTY_LEDGER, encoding="utf-8", newline="\n")
        if os.name != "nt":
            data.chmod(0o700)
            key_file.chmod(0o600)
            ledger.chmod(0o600)
    elif (data / _KEY_FILE).read_bytes() != key:
        raise ValueError(f"{data} already holds another key: one installation folder holds one key")
    return place


@contextlib.contextmanager
def installed(folder: pathlib.Path, key: bytes = TEST_KEY) -> "Iterator[pathlib.Path]":
    """XDG_DATA_HOME and LOCALAPPDATA pointed at the run's own installation folder for the block, then restored."""
    place = installation_folder(folder, key)
    saved = {name: os.environ.get(name) for name in ("XDG_DATA_HOME", "LOCALAPPDATA")}
    os.environ["XDG_DATA_HOME"] = str(place)
    os.environ["LOCALAPPDATA"] = str(place)
    try:
        yield place / _DATA_FOLDER
    finally:
        for name, value in saved.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


def command(argv: "list[str]", below_floor: bool, chain: object = None, unswitched: bool = False) -> "tuple[int, str]":
    """One `synthtwin` command run in this process: its exit code and the last of what it said.

    ``unswitched`` passes `cli.main`'s internal keyword of that name where
    the measured tree has it (route U); a tree without it has typed
    commands that do not switch, and runs as it stands.
    """
    from synthtwin import cli

    said = io.StringIO()
    keywords: "dict[str, object]" = {"small_tables_refused": not below_floor}
    if chain is not None:
        keywords["chain"] = chain
    if unswitched and typed_switched():
        keywords["unswitched"] = True
    with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
        code = cli.main(argv, **keywords)  # type: ignore[arg-type]
    return code, said.getvalue()[-1500:]


@dataclasses.dataclass
class Described:
    """A table described by one route: where its description lies, how its questions were answered, its seconds."""

    route: str
    folder: pathlib.Path
    out: pathlib.Path
    stem: str
    description: pathlib.Path
    below_floor: bool
    answered: str = ""
    seconds: float = 0.0
    left: "tuple[str, ...]" = ()
    key: bytes = dataclasses.field(default=TEST_KEY, repr=False)


AGES = ("age",)


def entries(document: object) -> "list[dict]":
    """Every entry of a questions file that takes an answer: `about_your_file`, `asked` and the checklist's columns."""
    if not isinstance(document, dict):
        return []
    found: "list[dict]" = []
    for key in ("about_your_file", "asked"):
        found += [e for e in document.get(key) or [] if isinstance(e, dict) and "answers_you_can_give" in e]
    checklist = document.get("checklist")
    if isinstance(checklist, dict):
        found += [e for e in checklist.get("columns") or [] if isinstance(e, dict) and "answers_you_can_give" in e]
    return found


def offered(entry: dict) -> "list[str]":
    return [str(a.get("answer")) for a in entry.get("answers_you_can_give", []) if isinstance(a, dict)]


def asks_for_people(entry: dict) -> bool:
    """Whether an entry is the person question: its `identifier` answer means the person the rows are about.

    Both wordings, as `health_zoo._asks_for_people` reads them: the first
    ("the people the rows are about") and the switched one every shipped run
    puts ("identifies the person", beside `record`), which holds no word
    "people". Read as the first alone, a key of another person (a guarantor's,
    a member of staff's) is answered `identifier` there and said to name the
    person (lane W5-ACC: the reliability battery's accounts table was refused
    so). No table of lane MU's or lane E0b's knows such a key today, so no
    answer of theirs moves.
    """
    return any(str(a.get("answer")) == "identifier"
               and ("people" in str(a.get("means", "")) or "identifies the person" in str(a.get("means", "")))
               for a in entry.get("answers_you_can_give", []) if isinstance(a, dict))


def truthful(column: str, choices: "list[str]", person: str, ages: "tuple[str, ...]",
             knows: "dict[str, str] | None" = None, people: bool = False) -> str:
    """The answer the person who holds an invented table gives to a column's question, or '' where none offered fits.

    The zoo's rule (`health_zoo.answer_generally`), from ``knows`` (what
    the person knows of each column): an age column's Safe Harbor
    question 'yes'; the known reading where offered; else 'keep' where the
    known reading is not offered but 'identifier' and 'keep' are; the
    person question (``people``) 'identifier' for the person column alone
    and 'keep' for any other column; any other column's Safe Harbor
    question (yes or no) 'no': no column of an invented table is a Safe
    Harbor element but an age.
    """
    known = (knows or {}).get(column, "identifier" if column == person and person else "")
    if column in ages and "yes" in choices:
        return "yes"
    given = known if known in choices else ""
    if not given and known and "identifier" in choices and "keep" in choices:
        given = "keep"
    if given == "identifier" and people and column != person:
        given = "keep" if "keep" in choices else ""
    if not given and "yes" in choices and "no" in choices:
        given = "no"
    return given


def answer_questions(questions: pathlib.Path, person: str, ages: "tuple[str, ...]" = AGES,
                     knows: "dict[str, str] | None" = None) -> "tuple[list[str], list[str]]":
    """Answer, in a questions file, every entry left blank that the person can answer truthfully (`truthful`), and the
    subject question.

    Returns the answers written this round (`column=answer`) and the
    entries left blank (no truthful answer offered). A file that does not
    exist, or puts nothing the person can answer, is left as it is.
    """
    from synthtwin import asking

    if not questions.exists():
        return [], []
    document = json.loads(questions.read_text(encoding="utf-8"))
    written, left = [], []
    for entry in entries(document):
        if entry.get("your_answer"):
            continue
        column = str(entry.get("column", ""))
        pick = truthful(column, offered(entry), person, ages, knows, asks_for_people(entry))
        if pick:
            entry["your_answer"] = pick
            written += [f"{column or 'the file'}={pick}"]
        else:
            left += [column or "the file"]
    between = document.get(asking.BETWEEN_COLUMNS) if isinstance(document, dict) else None
    question = between.get(asking.ROWS_PER_PERSON) if isinstance(between, dict) else None
    if isinstance(question, dict) and not question.get("your_answer"):
        question["your_answer"] = person or asking.ANSWER_ONE_ROW_EACH
        written += [f"the subject question={question['your_answer']}"]
    if written:
        questions.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return written, left


def blank_entries(questions: pathlib.Path, person: str, ages: "tuple[str, ...]" = AGES,
                  knows: "dict[str, str] | None" = None) -> "list[str]":
    """Every entry a questions file leaves blank, named: its column (or 'the file'), and whether the person could answer
    it (an entry the product put again after the last round answered it) or no answer offered fits."""
    if not questions.exists():
        return []
    left = []
    for entry in entries(json.loads(questions.read_text(encoding="utf-8"))):
        if entry.get("your_answer"):
            continue
        column = str(entry.get("column", ""))
        pick = truthful(column, offered(entry), person, ages, knows, asks_for_people(entry))
        left += [f"{column or 'the file'} ({'put again after the last round; ' + pick if pick else 'no answer fits'})"]
    return left


def _write_table(folder: pathlib.Path, stem: str, text: str) -> pathlib.Path:
    path = table_file(folder, stem)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    return path


def _replace_description_known() -> bool:
    from synthtwin import cli

    return "--replace-description" in getattr(cli, "_RECORD_OPTIONS", ())


ROUNDS = 3


def _answered_rounds(path: pathlib.Path, out: pathlib.Path, stem: str, below: bool, person: str,
                     ages: "tuple[str, ...]", knows: "dict[str, str] | None", chain: "object | None" = None,
                     again_chain: "object | None" = None, unswitched: bool = False,
                     answers_from: "pathlib.Path | None" = None) -> "tuple[int, str, str, tuple[str, ...]]":
    """`synthtwin profile`, then up to `ROUNDS` answers rounds while a round writes an answer; the entries left blank.

    ``answers_from`` (a part of a table already described, such as the
    half a trained model is fitted on): the first `profile` run is handed
    the whole table's answered questions file, so the part is described as
    the whole was answered; where the command refuses it, the part walks
    its own rounds and the words say so.
    """
    first = ["profile", str(path), "--out-dir", str(out), "--replace"]
    questions = out / f"{stem}-questions.json"
    answered: "list[str]" = []
    if answers_from is not None and answers_from.exists():
        questions.write_bytes(answers_from.read_bytes())
        code, said = command(first + ["--answers", str(questions)], below, chain, unswitched)
        if code == 0:
            answered += ["the whole table's answers carried"]
        else:
            answered += [f"the whole table's answers refused ({said.strip().splitlines()[-1][:120] if said.strip() else code})"]
            code, said = command(first, below, chain, unswitched)
    else:
        code, said = command(first, below, chain, unswitched)
    for _round in range(ROUNDS):
        if code != 0:
            break
        written, _left = answer_questions(questions, person, ages, knows)
        if not written:
            break
        answered += written
        again = ["profile", str(path), "--out-dir", str(out), "--answers", str(questions)]
        code, said = command(again, below, again_chain, unswitched)
        if code != 0 and _replace_description_known():
            code, said = command(again + ["--replace-description"], below, again_chain, unswitched)
    left = tuple(blank_entries(questions, person, ages, knows))
    words = "; ".join(answered) or "nothing asked"
    if left:
        words += "; left blank: " + ", ".join(left)
    return code, said, words, left


def describe_typed(folder: pathlib.Path, stem: str, text: str, person: str = "",
                   ages: "tuple[str, ...]" = AGES, knows: "dict[str, str] | None" = None,
                   key: bytes = TEST_KEY, unswitched: bool = False,
                   answers_from: "pathlib.Path | None" = None) -> Described:
    """ROUTE S's description (ROUTE U's with ``unswitched``): `synthtwin profile`, its questions answered as the person
    who holds the table answers them (``answers_from``: a part described as the whole table was answered)."""
    clock = time.perf_counter()
    path = _write_table(folder, stem, text)
    route = "U" if unswitched else "S"
    out = out_folder(folder, stem, route)
    out.mkdir(parents=True, exist_ok=True)
    below = data_rows(text) < floor_rows()
    with installed(folder, key):
        code, said, answered, left = _answered_rounds(path, out, stem, below, person, ages, knows,
                                                      unswitched=unswitched, answers_from=answers_from)
    if code != 0:
        raise RouteTrouble(f"route {route}: synthtwin profile exited {code}: {said[-600:]}")
    return Described(route, folder, out, stem, out / f"{stem}-profile.json", below, answered,
                     time.perf_counter() - clock, left, key)


def _chain_run(folder: pathlib.Path, person: str, again: bool, key: bytes) -> object:
    """The switch handed in: the run's own installation and private folder, the subject answered in advance where it can be."""
    from synthtwin import asking, cli

    fields = {f.name for f in dataclasses.fields(cli.ChainRun)}
    private = folder / "private"
    private.mkdir(parents=True, exist_ok=True)
    settings: "dict[str, object]" = {"folder": str(installation_folder(folder, key) / _DATA_FOLDER),
                                     "private_folder": str(private)}
    if not person:
        settings["rows_per_person"] = asking.ANSWER_ONE_ROW_EACH
    if again:
        settings["replace_description"] = True
    if "rules" in fields:
        settings["rules"] = True
    if "patient_layer" in fields:
        settings["patient_layer"] = False
    return cli.ChainRun(**{k: v for k, v in settings.items() if k in fields})  # type: ignore[arg-type]


def describe_switched(folder: pathlib.Path, stem: str, text: str, person: str = "",
                      ages: "tuple[str, ...]" = AGES, knows: "dict[str, str] | None" = None,
                      key: bytes = TEST_KEY) -> Described:
    """ROUTE C's description: `synthtwin profile` with the chain's switch handed in, its questions answered as in route S."""
    clock = time.perf_counter()
    path = _write_table(folder, stem, text)
    out = out_folder(folder, stem, "C")
    out.mkdir(parents=True, exist_ok=True)
    below = data_rows(text) < floor_rows()
    with installed(folder, key):
        code, said, answered, left = _answered_rounds(path, out, stem, below, person, ages, knows,
                                                      _chain_run(folder, person, False, key),
                                                      _chain_run(folder, person, True, key))
    if code != 0:
        raise RouteTrouble(f"route C: synthtwin profile exited {code}: {said[-600:]}")
    return Described("C", folder, out, stem, out / f"{stem}-profile.json", below, answered,
                     time.perf_counter() - clock, left, key)


def describe_layer(folder: pathlib.Path, stem: str, text: str, person: str, key: bytes = TEST_KEY) -> Described:
    """ROUTE P's description: the person column declared and the chain drawn with the patient layer, as lane GRb's driver does."""
    from synthtwin import chain, profile, reading, taxonomy

    import fixtures

    if not person or not hasattr(chain, "ROWS_PERSON"):
        raise RouteMissing("route P: this tree's chain has no patient layer to draw")
    if importlib.util.find_spec("synthtwin.patient_walk") is None:
        raise RouteMissing("route P: this tree has no patient walk (the generator that reads the patient layer)")
    clock = time.perf_counter()
    path = _write_table(folder, stem, text)
    out = out_folder(folder, stem, "P")
    out.mkdir(parents=True, exist_ok=True)
    settings = dataclasses.replace(taxonomy.Settings(small_cell_floor=11), person_columns=(person,))
    table = reading.read_table(str(path), small_cell_floor=11)
    try:
        document = profile.build_document(table, settings, [person], [], [], subjects=[person],  # type: ignore[call-arg]
                                          top_code=True)
    except TypeError as error:
        raise RouteMissing(f"route P: this tree's description takes no subjects ({error})") from error
    chained = chain.describe(table, document, settings, chain.ChainSwitch(stem, key, rows_per_person=chain.ROWS_PERSON))
    grain = getattr(chained, "grain", None)
    switched = json.loads(json.dumps(document))
    if chained.statistical is not None:
        switched["relationships"]["statistical"] = chained.statistical
    if grain is not None:
        switched["relationships"]["grain"] = grain
    if getattr(chained, "columns", None) is not None:
        switched["columns"] = chained.columns
    written = fixtures.write_profile(out, f"{stem}-profile.json", switched)
    answered = person if grain is not None else f"{person} (no layer drawn)"
    return Described("P", folder, out, stem, pathlib.Path(written), False, answered, time.perf_counter() - clock,
                     (), key)


def held_columns(described: Described) -> "list[str]":
    """The columns a typed description reads as record numbers though nobody named them (its screen text's 'read as:'
    lines; the column a person named as the person column is left out), each with the reason the text gives."""
    page = described.out / f"{described.stem}-profile.txt"
    if not page.exists():
        return []
    lines = page.read_text(encoding="utf-8").splitlines()
    held = []
    for i, line in enumerate(lines):
        if i and "read as:" in line and "record numbers" in line and "you named this column" not in line:
            reason = line.split("record numbers or codes", 1)[-1].strip(" ,.")
            held += [f"{lines[i - 1].strip()} ({reason or 'held'})"]
    return held


def describe(route: str, folder: pathlib.Path, stem: str, text: str, person: str = "",
             ages: "tuple[str, ...]" = AGES, knows: "dict[str, str] | None" = None,
             key: bytes = TEST_KEY) -> Described:
    """A table's description by route S, C, U or P (`ROUTES`)."""
    if route == "S":
        return describe_typed(folder, stem, text, person, ages, knows, key)
    if route == "U":
        return describe_typed(folder, stem, text, person, ages, knows, key, unswitched=True)
    if route == "C":
        return describe_switched(folder, stem, text, person, ages, knows, key)
    if route == "P":
        return describe_layer(folder, stem, text, person, key)
    raise ValueError(f"no route {route!r}")


def generate(described: Described, seed: int) -> "tuple[str, str]":
    """The twin of a description at one seed, and its report, as the route makes them.

    Routes S and U run `synthtwin generate DESCRIPTION --seed K` (route U
    unswitched) and read the twin and its report from the files the
    command writes; routes C and P load the description with its chain and
    generate it with `generation.generate_held`, as the pilot and lane
    GRb's driver do.
    """
    if described.route in ("S", "U"):
        with installed(described.folder, described.key):
            code, said = command(["generate", str(described.description), "--out-dir", str(described.out),
                                  "--seed", str(seed), "--replace"], described.below_floor,
                                 unswitched=described.route == "U")
        if code != 0:
            raise RouteTrouble(f"route {described.route}: synthtwin generate exited {code}: {said[-600:]}")
        twin = described.out / f"{described.stem}-twin.csv"
        report = described.out / f"{described.stem}-twin-report.txt"
        return twin.read_text(encoding="utf-8"), report.read_text(encoding="utf-8")
    from synthtwin import contract, generation, rendering

    with installed(described.folder, described.key):
        loaded = contract.load_profile(str(described.description), chain=True)
        made = generation.generate_held(loaded, seed)
        text = "".join(rendering.twin_csv_pieces(made))
        report = rendering.report(loaded, made)
    return text, report
