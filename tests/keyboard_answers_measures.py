"""The measurements of K-HZ-31 and K-HZ-32 (lane EZ-a, plan P4-D479), and the invented tables they read.

`tools/measurements/kpi_keyboard_answers.py` and
`tools/measurements/kpi_people_said.py` emit them under `kpi_run --slow`;
the gate files `tests/test_keyboard_answers.py` and
`tests/test_people_said.py` read the same tables at their one case of
20,000 rows. Every table is drawn here, with generic names; nothing comes
from any real system.

K-HZ-31, EVERY QUESTION AT THE KEYBOARD, AND THE KEYBOARD IS THE FILE. On
each table at 20,000 rows: the questions file answered round by round as
the person who holds the table answers it (`health_zoo.answer_generally`
for the zoo's kinds, a repeating column that is not the person answered
`keep` at its person question; `_clinic_truth` for the walkthrough's
look-alike and this module's other tables), the same answers typed at the
keyboard as the KEYS the screen shows (`Typist`, through `cli._asked`, so
the real reader reads them), and the same answers written as a
plain-text file of lines `column = answer`, the column named exactly (an
answer two questions about one column take is written in the questions
file itself, as the refusal of such a line says; a question about the file
by its number alone); the repeat lines the answered runs printed (the file
route's last and the keyboard's), each run as typed and required to
finish and to be printed at all. Its keys: the entries whose question the
file route answered that the keyboard's questions file still holds open
(an entry put again under the reading its answer gave is not open),
entries the file holds that no prompt put, descriptions differing between
the three routes (but for the one stated difference, `_same_but_kept`),
repeat lines missing, refused or describing otherwise, real values on the
keyboard's screen or in its questions file, each found as a whole word
(`_leaks`), keys the reader refused or the screen did not show, and on the
laboratory table the later round's printed numbers that are not the
file's numbering, or that a text line written with its column is not
refused for (`_numbers_leg`).

K-HZ-32, PEOPLE COUNTED BY THE COLUMN SAID TO NAME THEM. On five local
shapes of 20,000 rows -- 1,000 patients beside a clinician (crossing), an
encounter (nested), a second numbering of the same patient, a mother
beside a baby, and 20,000 patients one row each beside a clinician
(single) -- each carrying rare levels that catch a floor counted in rows,
said with `--person`, with the subject question at the keyboard, and
scripted with two `--identifier`; and `--person X` alone against
`--identifier X` alone on each. No zoo kind is read: the zoo's descriptions
against the base are the statistics check's measurement and K-HZ-02's. A
sixth shape (visit) says a visit key different on every row beside the
patient key. Its keys: tables refused whose said person counts 1,000 or
more, tables whose people are not the said column's own count (its name
and the product's count of it), real values of a held key published or
written to the twin, published values fewer than 11 said persons hold and
withheld values 11 or more hold (every label column of the source read,
whatever role the description gave it), bare '1 people' messages,
descriptions moved where one person is said; on the visit shape the
levels fewer than 11 patients hold that are published and the levels its
rule withholds; and a control that shows the values key can fail (the
floor lowered to 5 through the library).
"""

from __future__ import annotations

import csv
import datetime
import json
import pathlib
import random
import re
import shlex
import shutil
import time

from synthtwin import cli, contract, results

ROWS = 20_000
PEOPLE = 1_000


def shell_words(line: str, windows: "bool | None" = None) -> "list[str]":
    """A line the product printed for a person to type, split as the shell it was quoted for splits it.

    POSIX quoting on a Mac or Linux (`shlex`); on Windows (``windows`` true,
    or `cli._on_windows()` where it is None) PowerShell's single quotes, a
    quote inside written twice, and a bare word as it stands, so a path's
    backslashes stay. `shlex`'s POSIX reading takes them as escapes: on
    GitHub's Windows runs of push 24 a bare path `C:\\Users\\...` became
    `C:Users...` and named another file (four cases of
    tests/test_keyboard_answers.py).
    """
    if not (windows or (windows is None and cli._on_windows())):
        return shlex.split(line)
    return [
        word[1:-1].replace("''", "'") if word.startswith("'") else word
        for word in re.findall(r"'(?:[^']|'')*'|\S+", line)
    ]
# A bare '1 people', never a count of 11 or 101 people.
ONE_PEOPLE = re.compile(r"(?<![\d,])1 people")

_DEPARTMENTS = ("Cardiology", "Pediatrics", "Oncology", "Neurology", "Orthopedics", "General Medicine")
_VISITS = ("Inpatient", "Outpatient", "Emergency", "Observation")
_SERVICES = ("0250", "0300", "0320", "0450", "0510", "0636", "0730", "0120")
_DIAGNOSES = ("E11.9", "I10", "J18.9", "N39.0", "K21.9", "F32.9", "M54.5", "R07.9", "J45.909", "E78.5")
_PHRASES = (
    ("follow-up visit.", "new complaint.", "routine check.", "medication review."),
    ("tolerating diet.", "pain controlled.", "no new symptoms.", "vitals stable."),
    ("plan: return if worse.", "plan: recheck in 2 weeks.", "plan: continue treatment.", "plan: refer."),
)


def clinic_table(
    folder: pathlib.Path, rows: int, people: int, seed: int = 11, visit: bool = False, clinician: bool = False,
    numeric: bool = False,
) -> "tuple[pathlib.Path, set[str]]":
    """The walkthrough's look-alike: 13 generic columns of clinic visits, and its identifying cells.

    subject_id, encounter_date, department, visit_type, age, weight
    ('72.40 kg'), heart_rate, blood_pressure ('128/79'), glucose (with
    'NA'), smoker (Yes/No), service_code ('0250'), dx_code ('E11.9'),
    note; with a visit number unique to each row, or a clinician number
    several patients share, where asked; the patient number written in
    seven figures alone where asked (``numeric``: then it is put the
    question about record numbers, not the person question, and a
    clinician number declared beside it puts the subject question).
    """
    draw = random.Random(seed)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "clinic.csv"
    persons = [
        (f"{5100000 + place * 17 + draw.randint(0, 16)}" if numeric else f"S{100000 + place * 7 + draw.randint(0, 6):06d}",
         draw.randint(18, 101), draw.uniform(45.0, 140.0), draw.random() < 0.2)
        for place in range(people)
    ]
    first = datetime.date(2023, 1, 1)
    real: "set[str]" = set()
    header = ["subject_id", "encounter_date", "department", "visit_type", "age", "weight", "heart_rate",
              "blood_pressure", "glucose", "smoker", "service_code", "dx_code", "note"]
    if visit:
        header = header[:1] + ["visit_id"] + header[1:]
    if clinician:
        header = header[:1] + ["clinician_id"] + header[1:]
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        for place in range(rows):
            subject, age, weight, smokes = persons[place % people]
            systolic = draw.randint(95, 175)
            pressure = f"{systolic}/{draw.randint(50, min(110, systolic - 20))}"
            row = [
                subject, (first + datetime.timedelta(days=draw.randint(0, 729))).isoformat(),
                draw.choice(_DEPARTMENTS), draw.choice(_VISITS), f"{age}",
                f"{weight + draw.uniform(-2.0, 2.0):.2f} kg", f"{draw.randint(48, 132)}", pressure,
                "NA" if draw.random() < 0.05 else f"{draw.randint(70, 300)}", "Yes" if smokes else "No",
                draw.choice(_SERVICES), draw.choice(_DIAGNOSES), " ".join(draw.choice(part) for part in _PHRASES),
            ]
            real |= {subject, pressure}
            if visit:
                row = row[:1] + [f"V{5000000 + place}"] + row[1:]
                real |= {row[1]}
            if clinician:
                row = row[:1] + [f"C{2000 + draw.randint(0, 59)}"] + row[1:]
                real |= {row[1]}
            writer.writerow(row)
    return path, real


def stays_table(folder: pathlib.Path, rows: int, people: int, seed: int = 23) -> "tuple[pathlib.Path, set[str]]":
    """Hospital stays: a seven-figure patient number, a date, a ward, a pulse, sodium in three figures, a diagnosis code.

    Sodium is written in three figures alone, every value as wide as the
    next, so the first prompt asks whether it is a measurement, codes or
    record numbers; its truthful answer is a measurement (lane EZ-a's
    repair: skeptic 1's item 4). Returns the table and its patient numbers.
    """
    draw = random.Random(seed)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "stays.csv"
    patients = [f"{6100000 + place * 13 + draw.randint(0, 12)}" for place in range(people)]
    order = [place % people for place in range(rows)]
    draw.shuffle(order)
    first = datetime.date(2022, 1, 1)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["patient_no", "seen_on", "ward", "pulse", "sodium", "dx"])
        for person in order:
            writer.writerow([
                patients[person], (first + datetime.timedelta(days=draw.randint(0, 999))).isoformat(),
                draw.choice(("Ward North", "Ward South", "Recovery", "Clinic East")), f"{draw.randint(44, 136)}",
                "NA" if draw.random() < 0.04 else f"{draw.randint(128, 150)}", draw.choice(_DIAGNOSES),
            ])
    return path, set(patients)


def labs_table(folder: pathlib.Path, rows: int, people: int, seed: int = 31) -> "tuple[pathlib.Path, set[str]]":
    """Laboratory results: a seven-figure patient number, a date, a ward, a diagnosis code, a result, smoking.

    No column a Safe Harbor question reaches, so the round after the files
    opens with the checklist while the patient number's question, left open
    at the first prompt, stands before it in the questions file: skeptic 1's
    item 1, where the round's own count named another question (lane EZ-a's
    repair). Returns the table and its patient numbers.
    """
    draw = random.Random(seed)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "labs.csv"
    patients = [f"{6200000 + place * 13 + draw.randint(0, 12)}" for place in range(people)]
    order = [place % people for place in range(rows)]
    draw.shuffle(order)
    first = datetime.date(2023, 1, 1)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["patient_no", "seen_on", "ward", "dx", "lab_value", "smoker"])
        for person in order:
            writer.writerow([
                patients[person], (first + datetime.timedelta(days=draw.randint(0, 700))).isoformat(),
                draw.choice(("Ward North", "Ward South", "Day Surgery", "Recovery", "Clinic East")),
                draw.choice(_DIAGNOSES), f"{draw.uniform(130.0, 480.0):.1f}", "Yes" if draw.random() < 0.3 else "No",
            ])
    return path, set(patients)


def _is_the_person_question(entry: "dict[object, object]") -> bool:
    """Whether an entry's `identifier` answer means the people the rows are about."""
    for choice in entry["answers_you_can_give"] if isinstance(entry.get("answers_you_can_give"), list) else []:
        if isinstance(choice, dict) and choice.get("answer") == "identifier" and \
                f"{choice.get('means', '')}".startswith("the people the rows are about"):
            return True
    return False


_CLINIC_TRUTH = {
    "subject_id": ("identifier",),
    "blood_pressure": ("joined", "keep"),
    "service_code": ("code",),
    "dx_code": ("code",),
    "age": ("years", "yes"),
    "weight": ("no", "measurement"),
    "heart_rate": ("no", "measurement"),
    "glucose": ("no", "measurement"),
    "note": ("keep",),
}


# The stays and laboratory tables (lane EZ-a's repair): the patient number
# is record numbers, sodium, the pulse and the result are measurements, the
# diagnosis is codes; the ward and smoking keep their readings.
_STAYS_TRUTH = {
    "patient_no": ("identifier",),
    "sodium": ("measurement", "no"),
    "pulse": ("measurement", "no"),
    "lab_value": ("measurement", "no"),
    "dx": ("code",),
}
TRUTHS = {"clinic": _CLINIC_TRUTH, "stays": _STAYS_TRUTH, "labs": _STAYS_TRUTH}


def _clinic_truth(document: "dict[str, object]", truth: "dict[str, tuple[str, ...]]" = _CLINIC_TRUTH) -> None:
    """Answer a look-alike's questions file as the person who holds it would, in place.

    The patient number names the people; a visit or clinician number is no
    person but a record number; the pressure is two measurements in one
    cell; the service and diagnosis columns are codes; the age is ages in
    years; weight, heart rate and glucose are measurements, `no` to the
    Safe Harbor question; the note keeps its reading. Anything else blank.
    """
    for _section, entry in contract.answer_entries(document):
        if _section == "answered_before":
            continue
        column = f"{entry.get('column', '')}"
        offered = [f"{choice.get('answer')}" for choice in entry["answers_you_can_give"]]
        wanted: "tuple[str, ...]" = truth.get(column, ())
        if column in ("visit_id", "clinician_id"):
            wanted = ("keep",) if _is_the_person_question(entry) else ("identifier",)
        entry["your_answer"] = next((one for one in wanted if one in offered), "")


def _answered(table: "object", document: "dict[str, object]") -> None:
    """Answer one questions file truthfully, a zoo kind's or the look-alike's.

    A zoo kind's person question on a column that is not the table's
    person is answered `keep` ("not a person"), as the zoo answers it on a
    column it knows (`health_zoo.answer_generally`), on a column it does
    not know as well: the measure's person answers every question put
    (K-HZ-31's first key). Left blank, the question on a REDCap event name
    goes from the file once the patient number is said to be the person,
    while Enter at the keyboard's first prompt keeps the column held as
    record numbers, as that prompt says: the first run of K-HZ-31
    (9678254b) read that difference of the base's as routes differing.
    """
    if table is None or isinstance(table, str):
        _clinic_truth(document, TRUTHS[table or "clinic"])
        return
    import health_zoo as zoo

    zoo.answer_generally(table, document)  # type: ignore[arg-type]
    person = f"{getattr(table, 'person', '')}"
    for _section, entry in contract.answer_entries(document):
        if _section == "answered_before" or f"{entry.get('your_answer') or ''}":
            continue
        offered = [f"{choice.get('answer')}" for choice in entry["answers_you_can_give"]]
        if _is_the_person_question(entry) and f"{entry.get('column', '')}" != person and "keep" in offered:
            entry["your_answer"] = "keep"


def _quiet(argv: "list[str]", ask: "list[str | None] | None" = None) -> "tuple[results.Result, str]":
    screen: "list[tuple[str, str]]" = []
    result = cli.run(argv, screen=screen, ask=ask, small_tables_refused=True)
    return result, "".join(text for _stream, text in screen)


def _question_key(entry: "dict[object, object]") -> "tuple[str, tuple[str, ...]]":
    about = f"{entry.get('column') or ''}"
    return about, tuple(sorted(f"{choice.get('answer')}" for choice in entry["answers_you_can_give"]))


# An answer the file route gave, for the keyboard to give the same: the
# words of every answer its question offered, the words of the one given,
# and the answer. A column two questions ask about holds one of each.
Given = "tuple[tuple[str, ...], str, str]"


def _offers_said(entry: "dict[object, object]") -> "tuple[str, ...]":
    return tuple(" ".join(f"{choice.get('means', '')}".split()) for choice in entry["answers_you_can_give"])


def _file_route(
    table: object, source: pathlib.Path, extra: "tuple[str, ...]" = ()
) -> "tuple[dict[str, list[Given]], str, str, str, str]":
    """The questions file answered round by round, ``extra`` typed on every command line (`--person` where it is said so).

    Returns the answers given, by column, each with its question's words
    (`Given`); the last screen; the description; every screen and
    questions file the route showed, one text; and the description the
    first run wrote, before any answer, against which a repeat line is
    owed wherever the answers moved the description (Codex's item 8 of
    lane EZ-a).
    """
    questions = source.parent / f"{source.stem}-questions.json"
    result, screen = _quiet(["profile", f"{source}", *extra])
    seen = screen
    if result.verdict != results.NO_MISS:
        return {}, screen, "", seen, ""
    first = source.parent / f"{source.stem}-profile.json"
    unanswered = first.read_text(encoding="utf-8") if first.is_file() else ""
    answers: "dict[str, list[Given]]" = {}
    put: "set[tuple[str, tuple[str, ...]]]" = set()
    for _round in range(6):
        text = questions.read_text(encoding="utf-8")
        seen += text
        document = json.loads(text)
        fresh = [entry for _section, entry in contract.open_questions(document) if _question_key(entry) not in put]
        if not fresh:
            break
        _answered(table, document)
        for _section, entry in contract.open_questions(document) + [
            (section, entry) for section, entry in contract.answer_entries(document) if section != "answered_before"
        ]:
            put.add(_question_key(entry))
            written = f"{entry.get('your_answer') or ''}"
            if not written:
                continue
            offers = _offers_said(entry)
            chosen = next(
                (offers[place] for place in range(len(offers))
                 if f"{entry['answers_you_can_give'][place].get('answer')}" == written), "",
            )
            column = f"{entry.get('column') or ''}"
            answers[column] = [one for one in answers.get(column, []) if one[0] != offers] + [(offers, chosen, written)]
        questions.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
        result, screen = _quiet(["profile", f"{source}", *extra, "--answers", f"{questions}"])
        seen += screen
        if result.verdict != results.NO_MISS:
            break
    seen += questions.read_text(encoding="utf-8") if questions.is_file() else ""
    described = source.parent / f"{source.stem}-profile.json"
    return answers, screen, described.read_text(encoding="utf-8") if described.is_file() else "", seen, unanswered


# A question as the screen heads it: the first prompt's 'Column 2 of 4', a
# later round's 'Question 7 (1 of 2 in this round)' -- the number the
# questions file and a plain-text answers file name it by -- and what it is
# about.
ON_SCREEN = re.compile(
    r"\n  (?:Column \d+ of \d+|Question (?P<number>\d+) \(\d+ of \d+ in this round\)|\(\d+ of \d+ in this round\)): "
    r"(?:'(?P<column>[^\n]*)'|(?P<about>[^\n]*))\n"
)
# The one round's own prompts (lane Q-FLOW, step 2: the twin at a keyboard):
# its grouped lists and its last screen, which this stand-in answers with Enter.
_LISTED_NAME = re.compile(r"\n  ([^ \n]+) +(?=[a-z])")
ROUND_HEADS = re.compile(r"\nQUESTION \d+ OF \d+: |\nBEFORE ANYTHING IS WRITTEN\n|COLUMN\(S\) LOOK LIKE RECORD NUMBERS\n")
_KEY_LINE = re.compile(r"\n      \[([^\]\n]+)\] ([^\n]*)\n          then the description publishes")
_SUBJECT_KEYS = re.compile(r"\n      \[(\d+)\] ([^\n]+)")


def _words(text: str) -> str:
    return " ".join(f"{text}".split())


class Typist:
    """Stands in for `cli._asked`: reads the question on the screen and types the key shown beside the answer wanted.

    THE KEYS ARE TYPED, so the real reader (`cli._read_one_answer`) reads
    them, as a person's are (lane EZ-a's repair; skeptic 1's item 4: the
    measure handed the reader answer words, and never met a key). The
    question's answers come from what the screen renders: the first
    prompt's question (`cli._the_question`, watched as it renders) or the
    record of the later round's entry; the answer wanted is a word, or the
    first of a tuple of words the question offers, or the one the file
    route gave (`Given`, matched by the words its question offered in the
    file); the key typed is the one the screen shows beside that answer's
    words. A key the reader refuses is never typed again: the question is
    then left open with Enter and the refusal counted. ``person`` answers
    the subject question: a column, '' for Enter, None for the end of input.
    Columns answered `measurement` at the first prompt where `keep` is not
    offered keep their reading undeclared (``kept_undeclared``), where the
    file's `measurement` declares it: the one difference of the routes
    K-HZ-31's rule states. The twin's one round (lane Q-FLOW, step 2) --
    its grouped lists and its last screen (`ROUND_HEADS`) -- is answered
    with Enter.
    """

    def __init__(
        self, screen: "list[tuple[str, str]]", answers: "dict[str, object]", person: "str | None" = ""
    ) -> None:
        self.screen = screen
        self.answers = answers
        self.person = person
        self.question: object = None
        self.refused = 0
        self.mismatched = 0
        self.kept_undeclared: "list[str]" = []
        self.subject_put = 0
        self.typed = 0
        self._last = -1
        # The questions file the first round wrote, read when the later
        # round puts its first question (``questions`` names the file).
        self.questions: "pathlib.Path | None" = None
        self.snapshot: "bytes | None" = None

    def __call__(self, prompt: str) -> "str | None":
        text = "".join(one for stream, one in self.screen if stream == "out")
        if self._last >= 0 and "Please type one" in text[self._last:]:
            self.refused += 1
            self._last = len(text)
            return ""
        self._last = len(text)
        who = text.rfind("WHO ARE THE ROWS ABOUT?")
        found = list(ON_SCREEN.finditer(text))
        last = found[len(found) - 1] if found else None
        heads = list(ROUND_HEADS.finditer(text))
        if heads and who < heads[len(heads) - 1].start() and (last is None or heads[len(heads) - 1].start() > last.start()):
            head = heads[len(heads) - 1]
            if "LOOK LIKE RECORD NUMBERS" not in head.group(0):
                return ""
            # The one round's list of record numbers: each column listed
            # whose answer here is `measurement` or `code`, typed by its
            # name and that word (a column of them offers no `keep`).
            typed: "list[str]" = []
            for name in _LISTED_NAME.findall(text[head.start():]):
                wanted = self.answers.get(name)
                words = wanted if isinstance(wanted, tuple) else (wanted,)
                for word in words:
                    if word in ("measurement", "code"):
                        typed += [f"{name} {word}"]
                        if word == "measurement":
                            self.kept_undeclared += [name]
                        break
            self.typed += len(typed)
            return ", ".join(typed)
        if who >= 0 and (last is None or who > last.start()):
            self.subject_put += 1
            if self.person is None:
                return None
            return next((key for key, name in _SUBJECT_KEYS.findall(text[who:]) if name == self.person), "")
        if last is None:
            return ""
        if last.group("number") is not None and self.snapshot is None and self.questions is not None:
            self.snapshot = self.questions.read_bytes()
        about = last.group("column") if last.group("column") is not None else (last.group("about") or "")
        block = text[last.start():]
        lines = [(key, _words(means)) for key, means in _KEY_LINE.findall(block)]
        offers = self._offers(last.group("number") is None and "Column" in last.group(0), about, lines)
        answer = self._chosen(self.answers.get(about), offers, _words(block))
        if not answer:
            return ""
        means = next((said for given, said in offers if given == answer), "")
        keys = [key for key, said in lines if said == means]
        if len(keys) != 1:
            self.mismatched += 1
            return ""
        if "Column" in last.group(0) and answer == "measurement" and "keep" not in [given for given, _said in offers]:
            self.kept_undeclared += [about]
        self.typed += 1
        return keys[0]

    def _offers(self, first: bool, about: str, lines: "list[tuple[str, str]]") -> "list[tuple[str, str]]":
        """The answers the question on screen offers, each with its words."""
        if first:
            question = self.question
            if question is not None and getattr(question, "name", None) == about:
                return [(choice.answer, _words(choice.means)) for choice in question.choices]  # type: ignore[attr-defined]
            return []
        session = cli._current()
        shown = [said for _key, said in lines]
        for record in session.questions if session is not None else ():
            if record.subject == about and [_words(offer.means) for offer in record.offers] == shown:
                return [(offer.answer, _words(offer.means)) for offer in record.offers]
        return []

    @staticmethod
    def _chosen(wanted: object, offers: "list[tuple[str, str]]", block: str) -> str:
        """The answer wanted among those offered: a word, the first of a tuple offered ('means:' and the
        opening words of an answer's meaning choose it by them), or the file route's `Given`."""
        offered = [given for given, _said in offers]
        if isinstance(wanted, str):
            wanted = (wanted,)
        if isinstance(wanted, tuple):
            for one in wanted:
                if one[:6] == "means:":
                    found = [given for given, said in offers if said.startswith(one[6:])]
                    if found:
                        return found[0]
                elif one in offered:
                    return one
            return ""
        if isinstance(wanted, list):
            fitting = [
                (len([one for one in asked if one and one in block]), answer)
                for asked, chosen, answer in wanted if chosen and chosen in block and answer in offered
            ]
            return max(fitting)[1] if fitting else ""
        return ""


def typed_run(
    argv: "list[str]", answers: "dict[str, object]", person: "str | None" = "", refused: bool = True
) -> "tuple[results.Result, str, Typist]":
    """One command line at the keyboard, every answer typed as its key (`Typist`); its result, its screen and the typist."""
    screen: "list[tuple[str, str]]" = []
    typist = Typist(screen, answers, person)
    table = pathlib.Path(argv[1])
    typist.questions = table.parent / f"{table.stem}-questions.json"
    real_asked, real_question = cli._asked, cli._the_question

    def watched(question: object, place: int, total: int, held: bool = False) -> str:
        typist.question = question
        return real_question(question, place, total, held)  # type: ignore[arg-type]

    cli._asked = typist  # type: ignore[assignment]
    cli._the_question = watched  # type: ignore[assignment]
    try:
        result = cli.run(argv, screen=screen, ask=[], small_tables_refused=refused)
    finally:
        cli._asked = real_asked  # type: ignore[assignment]
        cli._the_question = real_question  # type: ignore[assignment]
    return result, "".join(text for _stream, text in screen), typist


def _keyboard_route(
    source: pathlib.Path, answers: "dict[str, object]", person: "str | None" = ""
) -> "tuple[results.Result, str, str, Typist]":
    """The same answers typed at the keyboard as keys (`Typist`): its result, screen, description and typist.

    An answer given as a word answers every question on its column; one
    given as the file route gave it (`Given`) answers the question on screen
    whose answers are shown in the words that question offered in the file,
    so a column two questions ask about is answered twice, each as the file.
    """
    result, screen, typist = typed_run(["profile", f"{source}"], answers, person)
    described = source.parent / f"{source.stem}-profile.json"
    return result, screen, described.read_text(encoding="utf-8") if described.is_file() else "", typist


def _text_route(table: object, source: pathlib.Path, extra: "tuple[str, ...]" = ()) -> str:
    """The same answers written as plain-text lines `column = answer`, each line kept only where it binds to its own question.

    Lane EZ-a's second repair (Codex's items 2 and 3 of that lane): a column
    is named exactly, a number is never written before it, and a question
    about the file is named by its number alone. A line that would not
    answer exactly its own question -- another question about the column
    takes the same answer, or the file keeps that answer already -- is
    refused by the product, whose words send the person to the questions
    file itself: the answer is written there, beside 'your_answer', and the
    text file carries the rest.
    """
    questions = source.parent / f"{source.stem}-questions.json"
    result, _screen = _quiet(["profile", f"{source}", *extra])
    if result.verdict != results.NO_MISS:
        return ""
    put: "set[tuple[str, tuple[str, ...]]]" = set()
    text = source.parent / "answers.txt"
    for _round in range(6):
        document = json.loads(questions.read_text(encoding="utf-8"))
        asked = contract.open_questions(document)
        if not [entry for _section, entry in asked if _question_key(entry) not in put]:
            break
        answered = json.loads(questions.read_text(encoding="utf-8"))
        _answered(table, answered)
        filled = [entry for _section, entry in contract.answer_entries(answered) if _section != "answered_before"]
        lines = ["# answers, one line each"]
        in_the_file: "list[int]" = []
        for number in range(len(asked)):
            put.add(_question_key(asked[number][1]))
            entry = _same_entry(filled, asked[number][1])
            written = f"{entry.get('your_answer') or ''}" if entry is not None else ""
            if not written:
                continue
            name = f"{asked[number][1].get('column') or ''}"
            line = f"{number + 1} = {written}" if asked[number][0] == "about_your_file" else f"{name} = {written.upper() if number % 2 else written}"
            if _binds_alone(text, questions, line, number):
                lines += [line]
            else:
                in_the_file += [number]
        if in_the_file:
            for number in in_the_file:
                entry = _same_entry(filled, asked[number][1])
                asked[number][1]["your_answer"] = f"{entry.get('your_answer') or ''}" if entry is not None else ""
            questions.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
        text.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        result, _screen = _quiet(["profile", f"{source}", *extra, "--answers", f"{text}"])
        if result.verdict != results.NO_MISS:
            break
    described = source.parent / f"{source.stem}-profile.json"
    return described.read_text(encoding="utf-8") if described.is_file() else ""


def _same_entry(entries: "list[dict[object, object]]", entry: "dict[object, object]") -> "dict[object, object] | None":
    """The entry of ``entries`` (in file order) standing where ``entry`` stands: the same column, words and reading."""
    for one in entries:
        if (
            one.get("column") == entry.get("column")
            and one.get("what_synthtwin_saw") == entry.get("what_synthtwin_saw")
            and _offers_said(one) == _offers_said(entry)
        ):
            return one
    return None


def _binds_alone(text: pathlib.Path, questions: pathlib.Path, line: str, number: int) -> bool:
    """Whether the one line, read against the questions file, fills open question ``number`` (from 0) and changes nothing else."""
    text.write_text(line + "\n", encoding="utf-8", newline="\n")
    before = json.loads(questions.read_text(encoding="utf-8"))
    try:
        filled = contract.load_answers(f"{text}", f"{questions}")
    except Exception:  # noqa: BLE001 -- a refused line goes to the questions file
        return False
    old = [(section, entry) for section, entry in contract.answer_entries(before)]
    new = [(section, entry) for section, entry in contract.answer_entries(filled)]
    changed = [
        at for at in range(len(old))
        if f"{old[at][1].get('your_answer') or ''}" != f"{new[at][1].get('your_answer') or ''}"
    ]
    standing = contract.open_questions(before)
    if not 0 <= number < len(standing):
        return False
    target = standing[number][1]
    return [old[at][1] is target for at in changed] == [True]


def _repeated(
    source: pathlib.Path, screen: str, expected: bool, typed: "tuple[str, ...]" = ()
) -> "tuple[bool, str]":
    """The repeat line an answered run printed, run as it says: whether it stands, and the description it writes.

    Lane EZ-a's second repair (Codex's item 8 of that lane): the line must
    be there where the answers moved the description (``expected``), and
    the command it makes must finish: a refused command leaves the earlier
    description in place, so comparing bytes after it proved nothing, and a
    missing line was counted as no difference. The command is the one the
    line describes: the command the person typed (``typed``, its options
    after the table) with the options the line says to add, less those it
    says to take out, `--answers` given once. Returns (False, '') for a
    line missing where owed or a command that does not finish; (True, '')
    where none was owed and none printed.
    """
    if "TO REPEAT THIS RUN WITHOUT THE QUESTIONS, add:" not in screen:
        return (not expected, "")
    lines = screen[screen.rindex("TO REPEAT THIS RUN WITHOUT THE QUESTIONS, add:"):].split("\n")
    words = shell_words(lines[1])
    taken: "list[str]" = []
    for place in range(len(lines) - 1):
        if "take these out of the command you typed" in lines[place]:
            taken = shell_words(lines[place + 1])
    kept = list(typed)
    pairs = [(taken[at], taken[at + 1]) for at in range(0, len(taken) - 1, 2)]
    if "--answers" in words and "--answers" in kept:
        at = kept.index("--answers")
        pairs += [(kept[at], kept[at + 1] if at + 1 < len(kept) else "")]
    for option, value in pairs:
        for at in range(len(kept) - 1):
            if kept[at] == option and kept[at + 1] == value:
                kept = kept[:at] + kept[at + 2:]
                break
    result, _screen = _quiet(["profile", f"{source}", *kept, *words])
    if result.verdict != results.NO_MISS:
        return (False, "")
    described = source.parent / f"{source.stem}-profile.json"
    return (True, described.read_text(encoding="utf-8"))


# A value written in figures alone (a sign and a decimal mark allowed).
_FIGURES = re.compile(r"[+-]?\d+(?:[.,]\d+)?")


def _leaks(values: "set[str]", shown: str, control: str) -> "list[str]":
    """The real values the keyboard's screen or questions file shows, each found as a whole word.

    A value written in figures alone counts only where the file route's own
    screens and questions files (`control`, the route the person has
    always had) do not show it too: those pages print counts, widths and
    statistics, and a record number of four figures meets one of them by
    chance (the first run of K-HZ-31 found 166 such, all inside counts and
    decimals on the first describe's screen, which both routes print).
    """
    found: "list[str]" = []
    for value in sorted(values):
        whole = re.compile(r"(?<![0-9A-Za-z])" + re.escape(value) + r"(?![0-9A-Za-z])")
        if whole.search(shown) and not (_FIGURES.fullmatch(value) and whole.search(control)):
            found += [value]
    return found


def _real_values(table: object, source: pathlib.Path, clinic_real: "set[str]") -> "set[str]":
    """The identifying cells of a table, four characters or longer, that no file or screen may show."""
    if table is None or isinstance(table, str):
        return {value for value in clinic_real if len(value) >= 4}
    import health_zoo as zoo

    with open(source, encoding="utf-8", errors="replace", newline="") as handle:
        rows = list(csv.reader(handle, delimiter=";" if getattr(table, "name", "") == "vitals" else ","))
    header = rows[0] if rows else []
    found: "set[str]" = set()
    for column, how in zoo.leak_list(table, header):  # type: ignore[arg-type]
        if how != "values" or column not in header:
            continue
        place = header.index(column)
        found |= {row[place].strip() for row in rows[1:] if place < len(row) and len(row[place].strip()) >= 4}
    return found


# The zoo's kinds the K-HZ-31 driver reads beside the look-alike: tables
# whose questions files hold many open entries of several families, and
# (lane EZ-a's repair; the statistics check's item 4) three that carry
# families the first six do not: counted dates and a Safe Harbor answer
# (perioperative), two-figure years on an operation date and a birth date
# (registry_extract), ZIP codes answered as codes then under the Safe Harbor
# question, birth dates and a birth city (patients).
ZOO_KINDS = (
    "vitals", "labs", "claims", "immunizations", "titled_report", "redcap",
    "perioperative", "registry_extract", "patients",
)


def _left_open(kept_questions: str, answers: "dict[str, list[Given]]") -> int:
    """The keyboard's questions file's open entries whose question the file route answered, the answer not standing.

    An entry put again under the reading an answer gave it (`read_as_now`
    'keep' after `keep` at the first prompt, plan P4-D401) keeps that answer
    when handed back blank, so it is not left open.
    """
    left = 0
    if not kept_questions:
        return left
    for _section, entry in contract.open_questions(json.loads(kept_questions)):
        asked_so = _offers_said(entry)
        standing = f"{entry.get('read_as_now') or ''}"
        left += int(any(
            one[0] == asked_so and one[2] != standing for one in answers.get(f"{entry.get('column') or ''}", [])
        ))
    return left


def _same_but_kept(keyed: str, filed: str, kept: "list[str]") -> bool:
    """Whether the keyboard's description is the file route's, but for the columns the first prompt's `measurement` kept undeclared.

    K-HZ-31'S ONE STATED DIFFERENCE (lane EZ-a's repair; skeptic 1's item
    4, the orchestrator's LANE EZ RULINGS 4 (5)): at the first prompt the
    key of `measurement`, where `keep` is not offered, keeps the reading
    the column stands on without declaring it, and the file's `measurement`
    declares it, so the file routes' `settings.forced_measurements` names
    that column and the keyboard's does not; nothing else may differ.
    """
    if keyed == filed:
        return True
    if not kept or not keyed or not filed:
        return False
    mine = json.loads(keyed)
    theirs = json.loads(filed)
    declared = theirs["settings"].get("forced_measurements")
    if isinstance(declared, list):
        theirs["settings"]["forced_measurements"] = [one for one in declared if one not in kept]
    return bool(mine == theirs)


def _numbers_leg(root: pathlib.Path) -> "dict[str, object]":
    """Every number the later round prints is the file's, no text line written with it lands anywhere, and 0 real values.

    The laboratory table at 20,000 rows, Enter at every question: the
    patient number's question stays open in the file before the checklist
    the later round opens with (skeptic 1's item 1 of lane EZ-a). Each
    number printed must be that question's place among those the file holds
    open (`contract.question_number`, the closing line's labels); each line
    written from the screen as `N column = answer` must be refused, since a
    text file reads no number back for a column's question (lane EZ-a's
    second repair, Codex's items 2 and 3); and `column = answer` must fill
    that question alone (read by `contract.load_answers`, nothing described).
    Then the diagnosis answered by its name is described, and no real
    patient number may reach the description, its summary, its questions
    file, the screen or the twin.
    """
    source, real = labs_table(root / "numbers" / "table", ROWS, PEOPLE)
    result, screen, _typist = typed_run(["profile", f"{source}"], {}, person="")
    questions = source.parent / f"{source.stem}-questions.json"
    later = screen[screen.index("MORE QUESTION(S)"):] if "MORE QUESTION(S)" in screen else ""
    printed = [
        (int(found.group("number")), found.group("column") or found.group("about") or "")
        for found in ON_SCREEN.finditer(later) if found.group("number")
    ]
    kept = questions.read_text(encoding="utf-8") if questions.is_file() else "{}"
    text = source.parent / "answers.txt"
    missed = 0
    for number, about in printed:
        standing = contract.open_questions(json.loads(kept))
        entry = standing[number - 1][1] if 1 <= number <= len(standing) else {}
        offered = [f"{choice.get('answer')}" for choice in entry.get("answers_you_can_give", [])]
        if entry.get("column") != about or not offered:
            missed += 1
            continue
        text.write_text(f"{number} {about} = {offered[0]}\n", encoding="utf-8", newline="\n")
        try:
            contract.load_answers(f"{text}", f"{questions}")
            missed += 1
        except Exception:  # noqa: BLE001 -- the numbered line is refused, as it must be
            pass
        missed += int(not _binds_alone(text, questions, f"{about} = {offered[0]}", number - 1))
    value: "dict[str, object]" = {"verdict": result.verdict, "printed": len(printed), "not_landing": missed, "leaks": 0}
    if [about for _number, about in printed if about == "dx"]:
        text.write_text("dx = code\n", encoding="utf-8", newline="\n")
        again, again_screen = _quiet(["profile", f"{source}", "--answers", f"{text}"])
        described = source.parent / f"{source.stem}-profile.json"
        written = again_screen + "".join(
            (source.parent / f"{source.stem}{suffix}").read_text(encoding="utf-8")
            for suffix in ("-profile.json", "-profile.txt", "-questions.json")
            if (source.parent / f"{source.stem}{suffix}").is_file()
        )
        cells: "set[str]" = set()
        if again.verdict == results.NO_MISS:
            _quiet(["generate", f"{described}", "--seed", "0"])
            twin = source.parent / f"{source.stem}-twin.csv"
            if twin.is_file():
                with open(twin, encoding="utf-8", newline="") as handle:
                    cells = {row[0] for row in list(csv.reader(handle))[1:] if row}
        tokens = set(re.findall(r"[0-9]+", written + screen))
        value["dx_answered"] = again.verdict
        value["dx_codes"] = _settings(source).get("forced_codes")
        value["leaks"] = len(real & (tokens | cells))
    shutil.rmtree(root / "numbers", ignore_errors=True)
    return value


def k_hz_31(root: pathlib.Path, kinds: "tuple[str, ...]" = ZOO_KINDS) -> "dict[str, object]":
    """K-HZ-31's value: every question at the keyboard, and the keyboard equal to the file, over the tables named.

    Each table: (its name, the truth it is answered by -- a zoo kind's, or
    the name of one of this module's -- the table and its identifying
    cells, the options the file and text routes type, and the column the
    keyboard answers the subject question with). The look-alike with a
    clinician number writes its patient number in figures alone, so the
    clinician number answered `identifier` in a later round puts the
    subject question there (lane EZ-a's repair; LANE EZ RULINGS 4 (3)):
    the file routes say the person with `--person`, the keyboard by
    answering it. Every key typed is a key (`Typist`).
    """
    import health_zoo as zoo

    tables: "list[tuple[str, object, pathlib.Path, set[str], tuple[str, ...], str]]" = []
    source, real = clinic_table(root / "clinic" / "table", ROWS, PEOPLE)
    tables += [("clinic", "clinic", source, real, (), "")]
    source, real = clinic_table(root / "clinic-visit" / "table", ROWS, PEOPLE, visit=True)
    tables += [("clinic-visit", "clinic", source, real, (), "")]
    source, real = clinic_table(root / "clinic-clinician" / "table", ROWS, PEOPLE, clinician=True, numeric=True)
    tables += [("clinic-clinician", "clinic", source, real, ("--person", "subject_id"), "subject_id")]
    source, real = stays_table(root / "stays" / "table", ROWS, PEOPLE)
    tables += [("stays", "stays", source, real, (), "")]
    source, real = labs_table(root / "lab-results" / "table", ROWS, PEOPLE)
    tables += [("lab-results", "labs", source, real, (), "")]
    for kind in kinds:
        table = zoo.table_named(kind)
        source = zoo.write_table(table, root / kind / "table", ROWS, zoo.seed_of(table))
        tables += [(kind, table, source, set(), (), "")]
    value: "dict[str, object]" = {
        "tables": 0, "entries_left_open_after_the_keyboard": 0, "entries_no_prompt_put": 0,
        "descriptions_differing_between_routes": 0, "descriptions_differing_from_the_repeat_line": 0,
        "real_values_on_the_screen_or_in_the_questions_file": 0, "keys_refused_or_unmatched": 0,
        "printed_numbers_not_landing_on_their_question": 0, "seconds": 0.0, "per_table": {},
    }
    started = time.perf_counter()
    for name, table, source, real, extra, person in tables:
        routes: "dict[str, pathlib.Path]" = {}
        for route in ("file", "keyboard", "text"):
            routes[route] = source.parent.parent / route / source.name
            routes[route].parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, routes[route])
        answers, file_screen, file_described, file_seen, unanswered = _file_route(table, routes["file"], extra)
        # A repeat line is owed where the answers moved the description.
        file_repeats, repeated = _repeated(
            routes["file"], file_screen, file_described != unanswered,
            (*extra, "--answers", f"{routes['file'].parent / (routes['file'].stem + '-questions.json')}"),
        )
        typed: "dict[str, object]" = dict(answers)
        if person:
            typed[person] = ("identifier",)
        keyed, keyed_screen, keyed_described, typist = _keyboard_route(routes["keyboard"], typed, person)
        texted = _text_route(table, routes["text"], extra)
        questions = routes["keyboard"].parent / f"{routes['keyboard'].stem}-questions.json"
        kept_questions = questions.read_text(encoding="utf-8") if questions.is_file() else ""
        left = _left_open(kept_questions, answers)
        unput = 0
        for record in keyed.questions:
            unput += int(record.section != results.SECTION_HELD and bool(record.offers) and not record.put)
        leaks = _leaks(_real_values(table, source, real), keyed_screen + kept_questions, file_seen)
        differ = int(
            not file_described
            or not _same_but_kept(keyed_described, file_described, typist.kept_undeclared)
            or texted != file_described
        )
        # The repeat line each answered run printed, run as typed: the file
        # route's last run's and the keyboard run's (the walkthrough's item
        # 15 was a keyboard run's line).
        keyed_repeats, keyed_repeated = _repeated(routes["keyboard"], keyed_screen, keyed_described != unanswered)
        repeat_differs = int(not file_repeats or bool(repeated) and repeated != file_described) + int(
            not keyed_repeats or bool(keyed_repeated) and keyed_repeated != keyed_described
        )
        value["tables"] = int(f"{value['tables']}") + 1
        value["entries_left_open_after_the_keyboard"] = int(f"{value['entries_left_open_after_the_keyboard']}") + left
        value["entries_no_prompt_put"] = int(f"{value['entries_no_prompt_put']}") + unput
        value["descriptions_differing_between_routes"] = int(f"{value['descriptions_differing_between_routes']}") + differ
        value["descriptions_differing_from_the_repeat_line"] = (
            int(f"{value['descriptions_differing_from_the_repeat_line']}") + repeat_differs
        )
        value["real_values_on_the_screen_or_in_the_questions_file"] = (
            int(f"{value['real_values_on_the_screen_or_in_the_questions_file']}") + len(leaks)
        )
        value["keys_refused_or_unmatched"] = int(f"{value['keys_refused_or_unmatched']}") + typist.refused + typist.mismatched
        value["per_table"][name] = {  # type: ignore[index]
            "answers": len(answers), "left": left, "unput": unput, "differ": differ, "repeat": repeat_differs,
            "repeat_lines": int(bool(repeated)) + int(bool(keyed_repeated)), "leaks": len(leaks),
            "keyboard": keyed.verdict, "typed": typist.typed, "kept_undeclared": typist.kept_undeclared,
            "subject_put": typist.subject_put, "refused": typist.refused + typist.mismatched,
        }
        shutil.rmtree(source.parent.parent, ignore_errors=True)
    numbers = _numbers_leg(root)
    value["printed_numbers_not_landing_on_their_question"] = int(f"{numbers['not_landing']}")
    value["real_values_on_the_screen_or_in_the_questions_file"] = (
        int(f"{value['real_values_on_the_screen_or_in_the_questions_file']}") + int(f"{numbers['leaks']}")
    )
    value["per_table"]["numbers"] = numbers  # type: ignore[index]
    value["seconds"] = round(time.perf_counter() - started, 1)
    return value


# THE RARE LEVELS EVERY K-HZ-32 TABLE CARRIES (lane EZ-a's repair; the
# statistics check's item 2 (a)): a label column whose four rare levels are
# held by 5 patients over 100 rows, 8 over 24, 11 over 22 and 12 over 240,
# built to catch a floor counted in rows: the first two are under the floor
# of 11 people and must be withheld though each covers 11 rows or more, the
# last two must be published. Each level: (label, patients, rows each).
RARE_LEVELS = (("grade A", 5, 20), ("grade B", 8, 3), ("grade C", 11, 2), ("grade D", 12, 20))


def people_table(
    folder: pathlib.Path, shape: str, rows: int = ROWS, people: int = PEOPLE, seed: int = 7
) -> "tuple[pathlib.Path, dict[str, set[str]]]":
    """A long table of 1,000 patients beside a second key of the shape named; the real keys of each column.

    `crossing`: a clinician several patients share. `nested`: an encounter
    of one patient, several rows each. `twice`: a second numbering of the
    same patient. `mother`: a mother's number beside each baby's, a mother
    having one to three babies. `single`: one row a patient, 20,000 of them,
    beside a clinician (the statistics check's item 1). `visit`: a visit
    key different on every row beside the patient's (the verify's X21 of
    lane EZ-a, said wrongly with `--person visit_id`). Every shape carries
    the label column `severity` and its rare levels (`RARE_LEVELS`), held by
    the said persons as counted there (one row a patient in `single`).
    """
    draw = random.Random(seed)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{shape}.csv"
    second = {
        "crossing": "clinician_id", "nested": "encounter_id", "twice": "chart_id", "mother": "mother_id",
        "single": "clinician_id", "visit": "visit_id",
    }[shape]
    first = "baby_id" if shape == "mother" else "subject_id"
    keys: "dict[str, set[str]]" = {first: set(), second: set()}
    mothers = [f"M{60000 + place * 5:06d}" for place in range(people)]
    holders = people if shape != "single" else rows
    # Which patient holds which rare level on which of their rows: the
    # first 36 patients, each on its first rows (rows of a patient are
    # `person`, `person + people`, ... in this table's order).
    rare: "dict[tuple[int, int], str]" = {}
    start = 0
    for label, count, each in RARE_LEVELS:
        for person in range(start, start + count):
            for turn in range(each if shape != "single" else 1):
                rare[(person, turn)] = label
        start = start + count
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow([first, second, "reading", "ward", "status", "severity"])
        for place in range(rows):
            person = place % holders
            turn = place // holders
            own = f"P{300000 + person * 11:07d}"
            if shape in ("crossing", "single"):
                other = f"D{4000 + draw.randrange(40):05d}"
            elif shape == "nested":
                other = f"E{800000 + person * 4 + (place // people) % 4:07d}"
            elif shape == "twice":
                other = f"K{900000 + person * 13:07d}"
            elif shape == "visit":
                other = f"V{5000000 + place:08d}"
            else:
                other = mothers[person // 2]
            keys[first].add(own)
            keys[second].add(other)
            level = rare[(person, turn)] if (person, turn) in rare else draw.choice(("mild", "moderate", "severe"))
            writer.writerow([own, other, f"{draw.randint(40, 180)}", draw.choice(("north", "south", "east", "west")),
                             draw.choice(("stable", "improving", "worse")), level])
    return path, keys


def _settings(source: pathlib.Path) -> "dict[str, object]":
    described = source.parent / f"{source.stem}-profile.json"
    if not described.is_file():
        return {}
    return json.loads(described.read_text(encoding="utf-8"))["settings"]


def k_hz_32(root: pathlib.Path) -> "dict[str, object]":
    """K-HZ-32's value: people counted by the column said to name them, over six local shapes and three ways of saying.

    Lane EZ-a's repair (the statistics check's item 2): every shape carries
    rare levels built to catch a floor counted in rows (`RARE_LEVELS`), and
    both sides are counted: published levels fewer than 11 said persons
    hold (an exposure) and levels 11 or more said persons hold that are
    withheld (a cost to the twin), every label column of the source read
    whatever role the description gave it. A CONTROL shows the first key
    can fail: one run with the floor lowered to 5 through the library's
    internal setting, which publishes the levels of 5 and 8 patients, must
    count them. The descriptions of tables with one said person are
    compared with the base's own route, `--person X` alone against
    `--identifier X` alone, byte for byte; no zoo kind is read (the zoo's
    descriptions against the base are the statistics check's measurement and
    K-HZ-02's). The one-row-a-patient shape (`single`) is said with
    `--person`, at the keyboard and scripted with two `--identifier`, where
    only the clinician number repeats. LANE EZ-a'S SECOND REPAIR (Codex's
    item 9; LANE EZ RULINGS 8 (3)): the people key reads the product's own
    count beside the column it names (`_people_counted`), and the visit
    shape (`_visit_shape`) says a visit key different on every row beside
    the patient key.
    """
    value: "dict[str, object]" = {
        "runs": 0, "refused_though_the_said_person_counts_the_floor": 0, "people_not_the_said_column_s_count": 0,
        "held_key_values_published_or_written": 0, "values_fewer_than_11_said_persons_hold": 0,
        "levels_11_or_more_said_persons_hold_withheld": 0, "one_people_messages": 0,
        "descriptions_moved_with_one_said_person": 0, "control_levels_counted_at_a_floor_of_5": 0,
        "patient_levels_under_11_published_beside_a_wrong_said_key": 0,
        "levels_withheld_beside_a_wrong_said_key": 0, "seconds": 0.0, "per_run": {},
    }
    started = time.perf_counter()
    for shape in ("crossing", "nested", "twice", "mother", "single"):
        source, keys = people_table(root / shape, shape)
        first, second = list(keys)
        for way in ("person", "keyboard", "scripted", "alone", "identifier"):
            run_source = root / shape / way / source.name
            run_source.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, run_source)
            if way == "person":
                result, screen = _severity_answered(run_source, ["--person", first, "--identifier", second])
            elif way == "keyboard" and shape == "single":
                # Only the clinician number repeats, so no subject question:
                # `--person` at the keyboard, `no` to the question about the
                # grade's few holders and every other question left open.
                result, screen, _typist = typed_run(
                    ["profile", f"{run_source}", "--person", first, "--identifier", second], {"severity": ("no",)}, person=""
                )
            elif way == "keyboard":
                result, screen, _typist = typed_run(
                    ["profile", f"{run_source}", "--identifier", first, "--identifier", second], {"severity": ("no",)},
                    person=first,
                )
            elif way == "alone":
                result, screen = _severity_answered(run_source, ["--person", first])
            elif way == "identifier":
                result, screen = _severity_answered(run_source, ["--identifier", first])
            else:
                result, screen = _quiet(["profile", f"{run_source}", "--identifier", first, "--identifier", second])
            said = way in ("person", "keyboard")
            settings = _settings(run_source)
            value["runs"] = int(f"{value['runs']}") + 1
            value["one_people_messages"] = int(f"{value['one_people_messages']}") + len(ONE_PEOPLE.findall(screen))
            entry: "dict[str, object]" = {"verdict": result.verdict, "person_columns": settings.get("person_columns")}
            if way == "identifier":
                alone = run_source.parent.parent / "alone" / f"{run_source.stem}-profile.json"
                mine = run_source.parent / f"{run_source.stem}-profile.json"
                moved = int(not alone.is_file() or not mine.is_file() or alone.read_bytes() != mine.read_bytes())
                value["descriptions_moved_with_one_said_person"] = (
                    int(f"{value['descriptions_moved_with_one_said_person']}") + moved
                )
                entry["moved"] = moved
            if said and result.verdict != results.NO_MISS:
                value["refused_though_the_said_person_counts_the_floor"] = (
                    int(f"{value['refused_though_the_said_person_counts_the_floor']}") + 1
                )
            if said and result.verdict == results.NO_MISS:
                # The said column's own count: its people where it repeats,
                # its rows where it names one row each (`single`) -- the
                # column named AND the product's count of it (Codex's item 9
                # of lane EZ-a: a count of 2,000 under the right name passed).
                counted = _people_counted(run_source, [first, second], first)
                if settings.get("person_columns") != ([] if shape == "single" else [first]) or counted != (
                    ROWS if shape == "single" else PEOPLE
                ):
                    value["people_not_the_said_column_s_count"] = int(f"{value['people_not_the_said_column_s_count']}") + 1
                entry["counted"] = counted
                written = "".join(
                    (run_source.parent / f"{run_source.stem}{suffix}").read_text(encoding="utf-8")
                    for suffix in ("-profile.json", "-profile.txt", "-questions.json")
                ) + screen
                generated, _generate_screen = _quiet(["generate", f"{run_source.parent / (run_source.stem + '-profile.json')}",
                                                      "--seed", "0"])
                twin = run_source.parent / f"{run_source.stem}-twin.csv"
                cells: "set[str]" = set()
                if twin.is_file():
                    with open(twin, encoding="utf-8", newline="") as handle:
                        cells = {cell for row in list(csv.reader(handle))[1:] for cell in row[:2]}
                held = [one for one in sorted(keys[second] | keys[first]) if one in written or one in cells]
                value["held_key_values_published_or_written"] = (
                    int(f"{value['held_key_values_published_or_written']}") + len(held)
                )
                few, withheld = _levels_by_said_persons(run_source, first)
                value["values_fewer_than_11_said_persons_hold"] = (
                    int(f"{value['values_fewer_than_11_said_persons_hold']}") + few
                )
                value["levels_11_or_more_said_persons_hold_withheld"] = (
                    int(f"{value['levels_11_or_more_said_persons_hold_withheld']}") + withheld
                )
                entry["generate"] = generated.verdict
                entry["held_values"] = len(held)
                entry["levels"] = [few, withheld]
            value["per_run"][f"{shape}/{way}"] = entry  # type: ignore[index]
        if shape == "crossing":
            value = _visit_shape(root, value)
            # THE CONTROL: the floor at 5, through the library alone.
            control = root / shape / "control" / source.name
            control.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, control)
            cli.run(["profile", f"{control}", "--person", first, "--identifier", second],
                    screen=[], small_tables_refused=True, internal_smallest_group=5)
            value["control_levels_counted_at_a_floor_of_5"] = _levels_by_said_persons(control, first)[0]
        shutil.rmtree(root / shape, ignore_errors=True)
    value["seconds"] = round(time.perf_counter() - started, 1)
    return value


def _visit_shape(root: pathlib.Path, value: "dict[str, object]") -> "dict[str, object]":
    """The visit shape (the verify's X21 of lane EZ-a): a visit key different on every row said to name the people beside the patient key.

    Said wrongly, `--person visit_id --identifier subject_id`: rule (d) of
    LANE EZ RULINGS 8 (2) counts the floor of 11 by the patient key too, so
    no level fewer than 11 patients hold is published (its own key, target
    0), and the levels 5 and 8 patients hold, which 100 and 24 visits hold,
    are withheld: the rule's price, its own key, exactly 2. Said rightly,
    `--person subject_id --identifier visit_id`, it is a said run like the
    others: no level 11 or more patients hold is withheld.
    """
    source, keys = people_table(root / "visit", "visit")
    for way, said, other in (("wrong", "visit_id", "subject_id"), ("right", "subject_id", "visit_id")):
        run_source = root / "visit" / way / source.name
        run_source.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, run_source)
        result, screen = _severity_answered(run_source, ["--person", said, "--identifier", other])
        value["runs"] = int(f"{value['runs']}") + 1
        value["one_people_messages"] = int(f"{value['one_people_messages']}") + len(ONE_PEOPLE.findall(screen))
        entry: "dict[str, object]" = {"verdict": result.verdict, "person_columns": _settings(run_source).get("person_columns")}
        if result.verdict != results.NO_MISS:
            value["refused_though_the_said_person_counts_the_floor"] = (
                int(f"{value['refused_though_the_said_person_counts_the_floor']}") + 1
            )
        else:
            written = "".join(
                (run_source.parent / f"{run_source.stem}{suffix}").read_text(encoding="utf-8")
                for suffix in ("-profile.json", "-profile.txt", "-questions.json")
            ) + screen
            held = [one for one in sorted(keys["subject_id"] | keys["visit_id"]) if one in written]
            value["held_key_values_published_or_written"] = (
                int(f"{value['held_key_values_published_or_written']}") + len(held)
            )
            by_patients = _levels_by_said_persons(run_source, "subject_id")
            if way == "wrong":
                value["patient_levels_under_11_published_beside_a_wrong_said_key"] = (
                    int(f"{value['patient_levels_under_11_published_beside_a_wrong_said_key']}") + by_patients[0]
                )
                value["levels_withheld_beside_a_wrong_said_key"] = (
                    int(f"{value['levels_withheld_beside_a_wrong_said_key']}")
                    + _levels_by_said_persons(run_source, "visit_id")[1]
                )
                entry["notice"] = int("You said visit_id names the people." in screen)
            else:
                value["values_fewer_than_11_said_persons_hold"] = (
                    int(f"{value['values_fewer_than_11_said_persons_hold']}") + by_patients[0]
                )
                value["levels_11_or_more_said_persons_hold_withheld"] = (
                    int(f"{value['levels_11_or_more_said_persons_hold_withheld']}") + by_patients[1]
                )
                counted = _people_counted(run_source, ["subject_id", "visit_id"], "subject_id")
                if entry["person_columns"] != ["subject_id"] or counted != PEOPLE:
                    value["people_not_the_said_column_s_count"] = (
                        int(f"{value['people_not_the_said_column_s_count']}") + 1
                    )
            entry["levels"] = list(by_patients)
        value["per_run"][f"visit/{way}"] = entry  # type: ignore[index]
    shutil.rmtree(root / "visit", ignore_errors=True)
    return value


def _severity_answered(source: pathlib.Path, options: "list[str]") -> "tuple[results.Result, str]":
    """One scripted run, and where its questions file asks about the grade's few holders, the same run with that question answered `no`.

    The truthful answer: the grades name no person. Left open, the question
    holds the grade column whole as record numbers (lane HB's levels rule),
    so its levels -- the ones built to catch a floor counted in rows -- were
    never published or withheld by the people floor at all, and the levels
    keys read 0 by another rule's hold (Codex's item 9 of lane EZ-a). The
    answer goes in a plain-text file, `severity = no`; the screens of both
    runs are returned together.
    """
    result, screen = _quiet(["profile", f"{source}", *options])
    questions = source.parent / f"{source.stem}-questions.json"
    if result.verdict != results.NO_MISS or not questions.is_file():
        return result, screen
    asked = [
        entry for _section, entry in contract.open_questions(json.loads(questions.read_text(encoding="utf-8")))
        if entry.get("column") == "severity" and "no" in [f"{one.get('answer')}" for one in entry["answers_you_can_give"]]
    ]
    if not asked:
        return result, screen
    text = source.parent / "severity.txt"
    text.write_text("severity = no\n", encoding="utf-8", newline="\n")
    again, again_screen = _quiet(["profile", f"{source}", *options, "--answers", f"{text}"])
    return again, screen + again_screen


def _people_counted(source: pathlib.Path, declared: "list[str]", said: str) -> int:
    """The product's own count of the people of a table with ``said`` said to name them: its people, or its rows where none repeats.

    Read by the command's own census (`cli._population_settled`, unswitched),
    the declarations as the run typed them (Codex's item 9 of lane EZ-a).
    """
    from synthtwin import reading, taxonomy

    read = reading.read_table(f"{source}")
    session = cli._Session(None, None)
    session.persons_said = [said]
    session.persons_typed = [said]
    cli._OPEN.sessions += [session]
    try:
        found = cli._population_settled(None, read, taxonomy.Settings(), declared, [], [], [], ())
    finally:
        del cli._OPEN.sessions[len(cli._OPEN.sessions) - 1]
    return found[5] if found[0] else found[4]


def _levels_by_said_persons(source: pathlib.Path, said: str) -> "tuple[int, int]":
    """Of the label columns' levels in the real table: those published that fewer than 11 said persons hold, and those 11 or more hold that are withheld.

    The label columns are read from the SOURCE (`severity`, `ward`,
    `status`, which no other rule of these tables holds), whatever role the
    description gave them (Codex's item 9 of lane EZ-a: a column turned
    wholly to record numbers carried no levels and was skipped, so every
    common level it lost went uncounted); a level is withheld where it is
    not among the levels the description publishes for that column, and a
    column the description publishes no levels of withholds them all. A
    linear counter: one pass over the table.
    """
    path = source.parent / f"{source.stem}-profile.json"
    if not path.is_file():
        return (0, 0)
    described = json.loads(path.read_text(encoding="utf-8"))
    with open(source, encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    header = rows[0]
    place_said = header.index(said)
    blocks = {f"{block.get('name')}": block for block in described["columns"] if isinstance(block, dict)}
    few = 0
    withheld = 0
    for name in ("severity", "ward", "status"):
        if name not in header:
            continue
        place = header.index(name)
        block = blocks.get(name, {})
        levels = block.get("levels") if isinstance(block, dict) else None
        published = {
            f"{level.get('label')}".casefold() for level in (levels if isinstance(levels, list) else [])
            if isinstance(level, dict)
        }
        holders: "dict[str, set[str]]" = {}
        for row in rows[1:]:
            holders.setdefault(row[place].strip().casefold(), set()).add(row[place_said])
        for label, who in holders.items():
            few += int(label in published and 0 < len(who) < 11)
            withheld += int(label not in published and len(who) >= 11)
    return (few, withheld)
