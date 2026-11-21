"""P4-D479 item 2: people counted by the column said to name them (lane EZ-a).

THE USABILITY WALKTHROUGH'S ITEM 2. Two record-number columns that both
repeat -- a patient number and a clinician number -- were counted as ONE
key: rows sharing a value of ANY of them are one person
(`taxonomy.repeating_identifiers`), so a clinician seen by many patients
joined them all, and `--identifier subject_id --identifier clinician_id`
refused a table of 1,000 patients as "1 people". Now the column SAID to
name the person counts the people (`--person`, the person question's
`identifier`, the subject question at the keyboard), every other
repeating key is held and joins nobody, and where nothing is said the
union stands as before, with a message that names the cause and the fix.

ONE CASE AT 20,000 ROWS AND 1,000 PEOPLE (the table floor); every other
case reads a small table with the two floors lowered by the test alone
(`parsing.TABLE_ROW_FLOOR`, `parsing.TABLE_PEOPLE_FLOOR`), the command's
own refusal rules otherwise as shipped. Every table is invented here.
"""

from __future__ import annotations

import csv
import json
import pathlib
import random
import re

import pytest

import keyboard_answers_measures as measures
from synthtwin import asking, cli, errors, parsing, reading, results, taxonomy

# A bare '1 people', never a count of 11 or 101 people.
ONE_PEOPLE = re.compile(r"(?<![\d,])1 people")


def _table(
    folder: pathlib.Path, rows: int, people: int, clinicians: int = 40, seed: int = 5, patient: str = "subject_id"
) -> "tuple[pathlib.Path, set[str], set[str]]":
    """A long table of visits: patient, clinician, a reading, a ward; and the real keys of both.

    ``patient`` names the patient key. EVERY SHIPPED RUN IS SWITCHED since
    lane CHON (plan P4-D464), and there a key whose name says the person
    (`subject_id`) is the person by lane GRa's rule (`asking.names_a_person`;
    LANE EZ RULINGS 1 (2): the switched path's vocabulary), so the cases of
    a table where NOTHING says which key names the patients name it
    `record_no`, a record number whose name says no person (batch 4u's
    checks).
    """
    draw = random.Random(seed)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "visits.csv"
    patients = [f"P{70000 + place * 3:06d}" for place in range(people)]
    staff = [f"D{4000 + place:05d}" for place in range(clinicians)]
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow([patient, "clinician_id", "reading", "ward"])
        for place in range(rows):
            writer.writerow([
                patients[place % people],
                staff[draw.randrange(clinicians)],
                f"{draw.randint(40, 180)}",
                draw.choice(("north", "south", "east", "west")),
            ])
    return path, set(patients), set(staff)


def _run(argv: "list[str]", ask: "list[str | None] | None" = None, refused: bool = True) -> "tuple[results.Result, str]":
    screen: "list[tuple[str, str]]" = []
    result = cli.run(argv, screen=screen, ask=ask, small_tables_refused=refused)
    return result, "".join(text for _stream, text in screen)


def _settings(folder: pathlib.Path, stem: str = "visits") -> "dict[str, object]":
    document = json.loads((folder / f"{stem}-profile.json").read_text(encoding="utf-8"))
    return document["settings"]


@pytest.fixture
def small_floors(monkeypatch: pytest.MonkeyPatch) -> None:
    """The table floor at 400 rows and 40 people, for this file's small tables only."""
    monkeypatch.setattr(parsing, "TABLE_ROW_FLOOR", 400)
    monkeypatch.setattr(parsing, "TABLE_PEOPLE_FLOOR", 40)


def test_the_said_person_counts_the_people_at_the_table_floor(tmp_path: pathlib.Path) -> None:
    """20,000 rows over 1,000 patients and 40 clinicians, through profile, generate and validate.

    `--person subject_id --identifier clinician_id` is described in 1,000
    people, the clinician number held and joining nobody: no real value of
    either key in the description, its summary, its questions file or the
    twin. Two such keys both named `--identifier`, the patient key's name
    saying no person, are refused in words that name the cause and
    `--person`, never as '1 people' (a name that says the person counts the
    people by it on the shipped road: lane GRa's rule).
    """
    table, patients, staff = _table(tmp_path / "said", 20000, 1000)
    result, screen = _run(["profile", f"{table}", "--person", "subject_id", "--identifier", "clinician_id"])
    assert result.verdict == results.NO_MISS, result.refusal
    settings = _settings(table.parent)
    assert settings["person_columns"] == ["subject_id"]
    assert "clinician_id" in settings["forced_identifiers"]
    written = "".join(
        (table.parent / name).read_text(encoding="utf-8")
        for name in ("visits-profile.json", "visits-profile.txt", "visits-questions.json")
    ) + screen
    assert [one for one in sorted(patients | staff) if one in written] == []
    # generate misses on 'reading' alone (its commonest number and two
    # field-width counts, the base generator's limit, measured the same with
    # one --identifier: the statistics check's item 6); validate is clean.
    generated, _generate_screen = _run(["generate", f"{table.parent / 'visits-profile.json'}", "--seed", "0"])
    assert generated.verdict in (results.NO_MISS, results.MISSED), generated.refusal
    with open(table.parent / "visits-twin.csv", encoding="utf-8", newline="") as handle:
        twin = list(csv.reader(handle))
    cells = {cell for row in twin[1:] for cell in row[:2]}
    assert cells & (patients | staff) == set()
    checked, _validate_screen = _run(["validate", f"{table.parent / 'visits-profile.json'}"])
    assert checked.verdict == results.NO_MISS, checked.misses
    # ...and the same two keys both named `--identifier`, where the patient
    # key's name says no person (`_table`'s ``patient``): refused in the words
    # that name the cause and `--person` on the shipped (switched) road too.
    named, _patients, _staff = _table(tmp_path / "named", 20000, 1000, patient="record_no")
    together, words = _run(["profile", f"{named}", "--identifier", "record_no", "--identifier", "clinician_id"])
    assert together.verdict == results.REFUSED
    assert together.refusal is not None
    assert "ANY of clinician_id, record_no" in together.refusal.words
    assert "--person" in together.refusal.words
    assert ONE_PEOPLE.search(words) is None


def test_two_keys_said_nothing_at_the_keyboard_put_the_subject_question(
    tmp_path: pathlib.Path, small_floors: None
) -> None:
    """Nothing says which key is the person: the subject question; its number counts by that key, Enter keeps the union."""
    table, _patients, _staff = _table(tmp_path / "keys", 600, 120, clinicians=8, patient="record_no")
    said, screen = _run(["profile", f"{table}", "--identifier", "record_no", "--identifier", "clinician_id"],
                        ask=["2"])
    assert "WHO ARE THE ROWS ABOUT?" in screen
    assert said.verdict == results.NO_MISS, said.refusal
    assert _settings(table.parent)["person_columns"] == ["record_no"]
    kept, kept_screen = _run(["profile", f"{table}", "--out-dir", f"{tmp_path}", "--identifier", "record_no",
                              "--identifier", "clinician_id"], ask=[""])
    assert kept.verdict == results.REFUSED
    assert kept.refusal is not None and "--person" in kept.refusal.words
    assert ONE_PEOPLE.search(kept_screen) is None


def test_the_keyboard_helper_s_empty_answer_keeps_the_union(
    tmp_path: pathlib.Path, small_floors: None, monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """`tests/keyboard.py`'s reader hands back the empty text: the subject question keeps counting the keys together."""
    import keyboard

    keyboard.every_reading_kept(monkeypatch)
    table, _patients, _staff = _table(tmp_path / "helper", 600, 120, clinicians=8, patient="record_no")
    code = cli.main(["profile", f"{table}", "--identifier", "record_no", "--identifier", "clinician_id"],
                    small_tables_refused=True)
    assert code == 1
    said = capsys.readouterr()
    assert "WHO ARE THE ROWS ABOUT?" in said.out
    assert "ANY of clinician_id, record_no" in said.err


def test_one_said_person_keeps_the_description_s_bytes(tmp_path: pathlib.Path) -> None:
    """With one repeating key, `--person` describes the table byte for byte as `--identifier` does."""
    table, _patients, _staff = _table(tmp_path / "one", 600, 120, clinicians=8)
    typed, _screen = _run(["profile", f"{table}", "--out-dir", f"{tmp_path}", "--identifier", "subject_id"], refused=False)
    first = (tmp_path / "visits-profile.json").read_bytes()
    said, _screen = _run(["profile", f"{table}", "--person", "subject_id"], refused=False)
    assert typed.verdict == said.verdict == results.NO_MISS
    assert (table.parent / "visits-profile.json").read_bytes() == first


def test_the_person_question_s_answer_says_the_person_across_rounds(
    tmp_path: pathlib.Path, small_floors: None
) -> None:
    """The person question answered `identifier` in the file counts by that column; the next file keeps saying so.

    On the shipped (switched) road the question's `identifier` answer says the
    person in lane GRa's words (`asking.PERSON_ANSWER_MEANS`, beside its
    `record` answer; LANE EZ RULINGS 1 (2)), where the unswitched path says
    'the people the rows are about' (batch 4u's checks).
    """
    table, _patients, _staff = _table(tmp_path / "rounds", 600, 120, clinicians=8)
    first, _screen = _run(["profile", f"{table}"])
    assert first.verdict == results.NO_MISS, first.refusal
    questions = table.parent / "visits-questions.json"
    document = json.loads(questions.read_text(encoding="utf-8"))
    person = [entry for entry in document["asked"] if entry["column"] == "subject_id"]
    assert person and any(
        choice["answer"] == "identifier" and choice["means"] == asking.PERSON_ANSWER_MEANS
        for choice in person[0]["answers_you_can_give"]
    )
    person[0]["your_answer"] = "identifier"
    questions.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
    # The answered round is the first to publish between columns (the patient layer, lane W5-PL), so the record of
    # earlier descriptions asks for --replace-description, as the first round's screen says it will.
    replaced = ["--replace-description"]
    second, _screen = _run(["profile", f"{table}", "--answers", f"{questions}", "--identifier", "clinician_id"] + replaced)
    assert second.verdict == results.NO_MISS, second.refusal
    assert _settings(table.parent)["person_columns"] == ["subject_id"]
    third, _screen = _run(["profile", f"{table}", "--answers", f"{questions}", "--identifier", "clinician_id"] + replaced)
    assert third.verdict == results.NO_MISS, third.refusal
    assert _settings(table.parent)["person_columns"] == ["subject_id"]


def test_a_person_said_before_a_second_key_is_declared_still_counts(
    tmp_path: pathlib.Path, small_floors: None
) -> None:
    """Said in one round beside no other record number, the person still counts the people when a later round declares one.

    K-HZ-31's first run (9678254b): the clinician table answered its
    person question in the first round and the clinician number
    `identifier` in the second; the said column was written to the file
    only where saying changed that round's count, so the second round
    counted both numbers together and refused the table as 1 person.
    """
    table, _patients, _staff = _table(tmp_path / "later", 600, 120, clinicians=8)
    first, _screen = _run(["profile", f"{table}"])
    assert first.verdict == results.NO_MISS, first.refusal
    questions = table.parent / "visits-questions.json"
    document = json.loads(questions.read_text(encoding="utf-8"))
    for entry in document["asked"]:
        if entry["column"] == "subject_id":
            entry["your_answer"] = "identifier"
    questions.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
    # The answered rounds publish between columns where the first did not (the patient layer, lane W5-PL): the
    # record of earlier descriptions asks for --replace-description, as the first round's screen says it will.
    replaced = ["--replace-description"]
    second, _screen = _run(["profile", f"{table}", "--answers", f"{questions}"] + replaced)
    assert second.verdict == results.NO_MISS, second.refusal
    kept = json.loads(questions.read_text(encoding="utf-8"))["answered_before"]
    assert [
        entry["column"] for entry in kept
        if any(choice["answer"] == "identifier" and choice["means"].startswith("the people the rows are about")
               for choice in entry["answers_you_can_give"])
    ] == ["subject_id"]
    third, _screen = _run(["profile", f"{table}", "--answers", f"{questions}", "--identifier", "clinician_id"] + replaced)
    assert third.verdict == results.NO_MISS, third.refusal
    assert _settings(table.parent)["person_columns"] == ["subject_id"]
    assert "clinician_id" in _settings(table.parent)["forced_identifiers"]


def test_the_repeat_line_says_person(tmp_path: pathlib.Path, small_floors: None) -> None:
    """A column said to name the person is repeated as `--person`."""
    table, _patients, _staff = _table(tmp_path / "repeat", 600, 120, clinicians=8, patient="record_no")
    said, screen = _run(["profile", f"{table}", "--identifier", "record_no", "--identifier", "clinician_id"],
                        ask=["2"])
    assert said.verdict == results.NO_MISS, said.refusal
    assert _settings(table.parent)["person_columns"] == ["record_no"]
    assert "--person record_no" in screen
    assert "--identifier clinician_id" in screen


def _stays_with_staff(
    folder: pathlib.Path, rows: int, people: int, seed: int = 41, patient: str = "patient_no"
) -> "tuple[pathlib.Path, set[str]]":
    """Hospital stays: a seven-figure patient number, a staff number many patients share, a date, a ward, a pulse, sodium, a code.

    ``patient`` names the patient number (`_table`'s ``patient``: `record_no` where nothing may say the person).
    """
    draw = random.Random(seed)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "stays.csv"
    patients = [f"{5100000 + place * 17 + draw.randint(0, 16)}" for place in range(people)]
    order = [place % people for place in range(rows)]
    draw.shuffle(order)
    staff: "set[str]" = set()
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow([patient, "staff_no", "seen_on", "ward", "pulse", "sodium", "dx"])
        for person in order:
            one = f"ST-{draw.randint(100, 159)}"
            staff.add(one)
            writer.writerow([
                patients[person], one, f"2023-{draw.randint(1, 12):02d}-{draw.randint(1, 28):02d}",
                draw.choice(("Ward North", "Ward South", "Recovery", "Clinic East")), f"{draw.randint(44, 136)}",
                f"{draw.randint(128, 150)}", draw.choice(("I10", "E11.9", "J44.1", "N18.3", "K59.00")),
            ])
    return path, staff


def test_a_staff_number_declared_in_a_later_round_puts_the_subject_question(
    tmp_path: pathlib.Path, small_floors: None
) -> None:
    """THE TRIAL'S OWN CASE: a patient number in figures alone and a staff number, declared in the round after the files.

    Lane EZ-a's repair (skeptic 1's item 2; the orchestrator's LANE EZ
    RULINGS 4 (3)): the round's description held its screen and reader
    back, so the subject question was never put, and two repeating record
    numbers fell to the scripted refusal, 'Nothing was written' printed
    while the first round's files stood, the questions file already
    rewritten with the round's answers. Now, every key typed: the patient
    number answered record numbers and the staff number 'not a person' at
    the first prompt, then record numbers in the round after the files; the
    subject question is put there, and 1 counts by the patient number, the
    staff number held and published nowhere. Enter there refuses in the
    words that name the cause and `--person`, the questions file is the
    first round's byte for byte, and the screen says what stands on disk;
    the end of input there keeps the first round's files (R7). The patient
    number is named `record_no` here: on the shipped (switched) road a name
    that says the patient (`patient_no`) counts the people by it with no
    question (lane GRa's rule, LANE EZ RULINGS 1 (2)), and the question is
    put where nothing says (batch 4u's checks).
    """
    plan: "dict[str, object]" = {
        "record_no": ("means:record numbers",), "staff_no": ("means:not a person", "means:record numbers"),
        "pulse": ("measurement", "no"), "sodium": ("measurement",), "dx": ("code",),
    }
    table, staff = _stays_with_staff(tmp_path / "said", 2000, 100, patient="record_no")
    # The round after the files publishes between columns where the first did not (the patient layer, lane W5-PL):
    # the record of earlier descriptions asks for --replace-description, typed up front in each run below.
    said, screen, typist = measures.typed_run(["profile", f"{table}", "--replace-description"], plan, person="record_no")
    assert typist.subject_put == 1 and (typist.refused, typist.mismatched) == (0, 0)
    assert said.verdict == results.NO_MISS, said.refusal
    settings = _settings(table.parent, "stays")
    assert settings["person_columns"] == ["record_no"] and "staff_no" in settings["forced_identifiers"]
    written = screen + "".join(
        (table.parent / name).read_text(encoding="utf-8")
        for name in ("stays-profile.json", "stays-profile.txt", "stays-questions.json")
    )
    assert [one for one in sorted(staff) if one in written] == []
    table, _staff = _stays_with_staff(tmp_path / "enter", 2000, 100, patient="record_no")
    kept, kept_screen, kept_typist = measures.typed_run(["profile", f"{table}", "--replace-description"], plan, person="")
    assert kept_typist.subject_put == 1
    assert kept.verdict == results.REFUSED
    assert kept.refusal is not None and "ANY of record_no, staff_no" in kept.refusal.words
    assert "--person" in kept.refusal.words and "Nothing was written" not in kept.refusal.words
    assert kept_typist.snapshot is not None
    assert (table.parent / "stays-questions.json").read_bytes() == kept_typist.snapshot
    assert "Nothing was written" not in kept_screen and "stand as they were" in kept_screen
    assert ONE_PEOPLE.search(kept_screen) is None
    table, _staff = _stays_with_staff(tmp_path / "ended", 2000, 100, patient="record_no")
    ended, ended_screen, ended_typist = measures.typed_run(["profile", f"{table}", "--replace-description"], plan,
                                                          person=None)
    assert ended.verdict == results.NO_MISS and ended_typist.subject_put == 1
    assert "You ended the questions here. The files written above stand as they are." in ended_screen
    assert (table.parent / "stays-questions.json").read_bytes() == ended_typist.snapshot


def test_a_said_person_one_row_each_counts_the_table_in_rows(tmp_path: pathlib.Path, small_floors: None) -> None:
    """`--person` on a key that is different on every row, beside a clinician number that repeats: the table in rows, its people.

    Lane EZ-a's repair (the statistics check's item 1): the said column
    was looked for among the repeating keys alone, so the clinician number
    counted the people and the table was refused as 20 people; and the
    screen said no column names people and taught `--identifier` on the
    clinician number. Now the said key counts the table in rows, which are
    its people, the clinician number is held, and that notice is not shown.
    Two `--identifier`, nothing said, are counted as before.
    """
    draw = random.Random(3)
    folder = tmp_path / "single"
    folder.mkdir()
    table = folder / "visits.csv"
    with open(table, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["subject_id", "clinician_id", "reading", "ward"])
        for place in range(600):
            writer.writerow([f"P{1000000 + place * 3}", f"D{4000 + draw.randrange(20):05d}",
                             f"{draw.randint(40, 180)}", draw.choice(("north", "south", "east", "west"))])
    said, screen = _run(["profile", f"{table}", "--person", "subject_id", "--identifier", "clinician_id"])
    assert said.verdict == results.NO_MISS, said.refusal
    settings = _settings(folder)
    assert settings["person_columns"] == []
    assert sorted(settings["forced_identifiers"]) == ["clinician_id", "subject_id"]
    assert "No column that names PEOPLE" not in screen
    # ...and `--person` alone, the clinician number put the person question:
    # no notice that no column names people, no `--identifier` taught on it.
    # Each run after the first describes the table again in the same data
    # folder, so on the shipped (switched) road it names the earlier
    # description as replaced (`--replace-description`, the record's own
    # remedy, contract 4.6b.4; batch 4u's checks).
    alone, alone_screen = _run(["profile", f"{table}", "--replace", "--replace-description", "--person", "subject_id"])
    assert alone.verdict == results.NO_MISS, alone.refusal
    assert "MIGHT NAME THE PEOPLE" not in alone_screen and "No column that names PEOPLE" not in alone_screen
    together, words = _run(["profile", f"{table}", "--replace", "--replace-description", "--identifier", "subject_id",
                            "--identifier", "clinician_id"])
    assert together.verdict == results.REFUSED
    assert "20 people, counted by 'clinician_id'" in words


def test_a_key_too_few_to_name_the_patients_is_said_and_no_command_is_offered(tmp_path: pathlib.Path) -> None:
    """Rule (e)'s shape, the README's own line: a said key different on every row beside a key of fewer values than the people floor.

    The verify 2's MINOR 3 of lane EZ-a (the orchestrator's LANE EZ
    RULINGS 9 (1)): `--person subject_id --identifier clinician_id` on
    20,000 patients of one row each and 40 clinicians said to run the
    command again with `--person clinician_id`, which the table floor then
    refuses: a physician who typed the README's line was told the wrong
    column might have been named. The clinician number, with fewer
    different values than the people floor, cannot name the patients, so
    the line says that and offers no command. Words only: the table is
    counted in its rows, as before.
    """
    draw = random.Random(8)
    folder = tmp_path / "readme"
    folder.mkdir()
    table = folder / "visits.csv"
    with open(table, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["subject_id", "clinician_id", "reading", "ward"])
        for place in range(20000):
            writer.writerow([f"P{2000000 + place * 3}", f"D{4000 + draw.randrange(40):05d}",
                             f"{draw.randint(40, 180)}", draw.choice(("north", "south", "east", "west"))])
    said, screen = _run(["profile", f"{table}", "--person", "subject_id", "--identifier", "clinician_id"])
    assert said.verdict == results.NO_MISS, said.refusal
    assert (
        f"clinician_id repeats with fewer than {parsing.TABLE_PEOPLE_FLOOR:,} different values, so it cannot "
        f"name the patients: each row was counted as one person."
    ) in screen
    assert "run the command again" not in screen and "--person clinician_id" not in screen
    settings = _settings(folder)
    assert settings["person_columns"] == []
    assert sorted(settings["forced_identifiers"]) == ["clinician_id", "subject_id"]


def test_no_message_counts_one_people() -> None:
    """The floor's messages count '1 person', never '1 people'."""
    assert ONE_PEOPLE.search(errors.the_table_is_below_the_floor(20000, 1, "a and b", 11)) is None
    assert "1 person" in errors.the_table_is_below_the_floor(20000, 1, "a and b", 11)
    assert ONE_PEOPLE.search(errors.people_counted_together(20000, 1, ["a", "b"])) is None
    assert ONE_PEOPLE.search(errors.the_population_is_too_small(1, "people", "a")) is None


def test_person_feeds_the_switched_run_s_persons_said(tmp_path: pathlib.Path) -> None:
    """On a run with the chain's switch, `--person` is what `persons_said` counts the people by: one option, one meaning."""
    table, _patients, _staff = _table(tmp_path / "switched", 600, 120, clinicians=8)
    read = reading.read_table(f"{table}")
    session = cli._Session(None, None)
    session.persons_typed = ["subject_id"]
    session.persons_said = ["subject_id"]
    cli._OPEN.sessions += [session]
    try:
        state = cli._ChainState(cli.ChainRun(), None)
        found = cli._population_settled(
            state, read, taxonomy.Settings(), ["subject_id", "clinician_id"], [], [], [], ()
        )
    finally:
        del cli._OPEN.sessions[len(cli._OPEN.sessions) - 1]
    assert state.persons_said == ("subject_id",)
    assert found[0] == ("subject_id",)
    assert found[1] == 120


def _visits_beside_patients(folder: pathlib.Path, rows: int = 2000, people: int = 100) -> "tuple[pathlib.Path, set[str]]":
    """A visit key different on every row beside a patient key, and a grade column whose two rare levels 5 and 8 patients hold (the verify's X21)."""
    draw = random.Random(21)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "visits.csv"
    patients = [f"P{300000 + place * 7:07d}" for place in range(people)]
    keys: "set[str]" = set(patients)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["subject_id", "visit_id", "reading", "severity"])
        for place in range(rows):
            person = place % people
            visit = f"V{5000000 + place:08d}"
            keys.add(visit)
            grade = "grade A" if person < 5 else "grade B" if person < 13 else draw.choice(("mild", "moderate", "severe"))
            writer.writerow([patients[person], visit, f"{draw.randint(40, 180)}", grade])
    return path, keys


def _published_levels(folder: pathlib.Path, column: str = "severity") -> "set[str]":
    document = json.loads((folder / "visits-profile.json").read_text(encoding="utf-8"))
    for block in document["columns"]:
        if block.get("name") == column:
            return {f"{level.get('label')}" for level in block.get("levels") or [] if isinstance(level, dict)}
    return set()


def test_a_wrong_said_key_beside_a_patient_key_is_counted_by_both(tmp_path: pathlib.Path, small_floors: None) -> None:
    """A visit key different on every row said to name the people, beside a patient key that repeats (the verify's X21; LANE EZ RULINGS 8 (2) (d), (3)).

    Measured on repair 1's head at 20,000 rows over 1,000 patients: `--person
    visit_id --identifier subject_id` published the levels 5 and 8 patients
    hold and the screen said nothing, where both keys declared
    `--identifier` withheld them. Now the patient key, repeating with as
    many values as the people floor, counts the floor of 11 beside the said
    key: neither rare level is published, the description is the one both
    keys named `--identifier` give, and one line says what was counted and
    what to run again. Said rightly, `--person subject_id`, nothing changes
    and no such line is shown.
    """
    table, keys = _visits_beside_patients(tmp_path / "wrong")
    wrong, screen = _run(["profile", f"{table}", "--person", "visit_id", "--identifier", "subject_id"])
    assert wrong.verdict == results.NO_MISS, wrong.refusal
    assert "You said visit_id names the people. Its values are different on every row" in screen
    assert "run the command again with --person subject_id in place of --person visit_id" in screen
    assert {"grade A", "grade B"} & _published_levels(table.parent) == set()
    assert _settings(table.parent)["person_columns"] == ["subject_id"]
    said_wrongly = (table.parent / "visits-profile.json").read_bytes()
    written = screen + "".join(
        (table.parent / name).read_text(encoding="utf-8")
        for name in ("visits-profile.json", "visits-profile.txt", "visits-questions.json")
    )
    assert [one for one in sorted(keys) if one in written] == []
    both, _screen = _run(["profile", f"{table}", "--replace", "--identifier", "subject_id", "--identifier", "visit_id"])
    assert both.verdict == results.NO_MISS
    assert (table.parent / "visits-profile.json").read_bytes() == said_wrongly
    right, right_screen = _run(["profile", f"{table}", "--replace", "--person", "subject_id", "--identifier", "visit_id"])
    assert right.verdict == results.NO_MISS
    assert (table.parent / "visits-profile.json").read_bytes() == said_wrongly
    assert "You said" not in right_screen


def test_the_line_shows_beside_a_column_put_the_person_question(tmp_path: pathlib.Path, small_floors: None) -> None:
    """The verify's X21 with the patient key undeclared: `--person visit_id` alone, the patient key put the person question.

    The verify 2's MINOR 1 (c) of lane EZ-a (the orchestrator's LANE EZ
    RULINGS 9 (2)): the line where the column put the person question
    repeats beside a said column that counted the table in rows
    (`cli._rows_counted_beside`) was pinned by no case. The visit key,
    different on every row, is said with `--person`: the screen says it
    counted each row as one person and that subject_id repeats, and the
    description is the one `--identifier visit_id` gives, byte for byte.
    """
    table, keys = _visits_beside_patients(tmp_path / "undeclared")
    said, screen = _run(["profile", f"{table}", "--person", "visit_id"])
    assert said.verdict == results.NO_MISS, said.refusal
    assert "You said visit_id names the people. Its values are different on every row" in screen
    assert "subject_id repeats" in screen
    described = (table.parent / "visits-profile.json").read_bytes()
    written = screen + "".join(
        (table.parent / name).read_text(encoding="utf-8")
        for name in ("visits-profile.json", "visits-profile.txt", "visits-questions.json")
    )
    assert [one for one in sorted(keys) if one in written] == []
    plain, _screen = _run(["profile", f"{table}", "--replace", "--identifier", "visit_id"])
    assert plain.verdict == results.NO_MISS, plain.refusal
    assert (table.parent / "visits-profile.json").read_bytes() == described


def test_the_refusal_offers_each_column_and_no_example(tmp_path: pathlib.Path, small_floors: None) -> None:
    """Two repeating keys and nothing said: the refusal asks which names the patients, offers each column, and names none as an example.

    The verify's MAJOR 2 of lane EZ-a (LANE EZ RULINGS 8 (4)): the refusal
    said 'for example --person' and the first column in name order, which
    on this table is the clinician number; followed, it counted the
    clinicians as the people.
    """
    table, _patients, _staff = _table(tmp_path / "crossing", 600, 120, clinicians=8, patient="record_no")
    refused, screen = _run(["profile", f"{table}", "--identifier", "record_no", "--identifier", "clinician_id"])
    assert refused.verdict == results.REFUSED and refused.refusal is not None
    words = refused.refusal.words
    assert "for example" not in words and "example" not in words
    assert "Which of these columns names the patients the rows are about?" in words
    assert "--person clinician_id, --person record_no" in words
    assert ONE_PEOPLE.search(screen) is None


def test_choosing_the_person_reads_every_declared_column_as_declared(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Counting by the said column never reads another declared identifier's cells otherwise (Codex's item 4 of lane EZ-a).

    The verdict's table: the patient number names 100 patients over the
    first 1,900 rows and is blank after; the declared `other_id` holds
    repeated June 2022 dates, then `1900-01-01` on the last 100 rows. Read
    as declared, record numbers, every row holds a value; the recount by
    the said column alone took `other_id` out of the declarations, read its
    last cells as no date and refused 2,000 rows as 1,900. The row floor at
    2,000 for this file's table alone.
    """
    monkeypatch.setattr(parsing, "TABLE_ROW_FLOOR", 2000)
    monkeypatch.setattr(parsing, "TABLE_PEOPLE_FLOOR", 40)
    folder = tmp_path / "dated"
    folder.mkdir()
    table = folder / "visits.csv"
    draw = random.Random(4)
    with open(table, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["subject_id", "other_id"])
        for place in range(2000):
            subject = f"P{400000 + (place % 100) * 9:07d}" if place < 1900 else ""
            other = f"2022-06-{draw.randint(1, 28):02d}" if place < 1900 else "1900-01-01"
            writer.writerow([subject, other])
    said, screen = _run(["profile", f"{table}", "--person", "subject_id", "--identifier", "other_id"], refused=True)
    assert said.verdict == results.NO_MISS, screen
    assert _settings(folder)["person_columns"] == ["subject_id"]


def test_a_said_key_one_row_each_counts_rows_on_the_switched_path_too(tmp_path: pathlib.Path) -> None:
    """With the chain's switch, `--person` on a key different on every row beside forty clinicians counts the rows, never forty people (Codex's item 5).

    The same decision table as the unswitched path (LANE EZ RULINGS 8 (2)):
    the clinician number, with fewer values than the people floor, cannot
    name the patients and never governs.
    """
    from synthtwin import chain

    draw = random.Random(5)
    folder = tmp_path / "switched"
    folder.mkdir()
    path = folder / "visits.csv"
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["subject_id", "clinician_id", "reading"])
        for place in range(2000):
            writer.writerow([f"P{1000000 + place * 3}", f"D{4000 + draw.randrange(40):05d}", f"{draw.randint(40, 180)}"])
    read = reading.read_table(f"{path}")
    session = cli._Session(None, None)
    session.persons_typed = ["subject_id"]
    session.persons_said = ["subject_id"]
    cli._OPEN.sessions += [session]
    try:
        state = cli._ChainState(cli.ChainRun(), None)
        found = cli._population_settled(
            state, read, taxonomy.Settings(), ["subject_id", "clinician_id"], [], [], [], ()
        )
    finally:
        del cli._OPEN.sessions[len(cli._OPEN.sessions) - 1]
    assert found[0] == () and found[1] == 2000 and found[4] == 2000
    assert state.rows_per_person == chain.ROWS_ONE and "subject_id" in state.persons_said


def test_the_refusal_reads_each_key_once(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The refusal's question whether one key alone would reach the floor reads each key once (Codex's item 6 of lane EZ-a).

    Keys holding values in the first rows alone, a status column after
    them: a census of each key alone walked every column for the rows that
    hold a value, 28 readings for four keys and 88 for eight (k (k + 3)).
    Counted here as the readings of a column under the finished reading
    (`taxonomy._present_spellings`): one walk and one reading a key, so at
    most 2 k + 1. At 1,000,000 rows and 50 keys that is 101 readings where
    the census of each read 2,650 (P4-D479).
    """
    monkeypatch.setattr(parsing, "TABLE_ROW_FLOOR", 400)
    monkeypatch.setattr(parsing, "TABLE_PEOPLE_FLOOR", 40)
    for keys in (4, 8):
        folder = tmp_path / f"keys{keys}"
        folder.mkdir()
        path = folder / "visits.csv"
        with open(path, "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow([f"key_{one}" for one in range(keys)] + ["status"])
            for place in range(2000):
                writer.writerow(
                    [f"K{one}-{place % 10:03d}" if place < 200 else "" for one in range(keys)]
                    + [("open", "closed")[place % 2]]
                )
        read = reading.read_table(f"{path}")
        declared = [f"key_{one}" for one in range(keys)]
        session = cli._Session(None, None)
        cli._OPEN.sessions += [session]
        try:
            found = cli._population_of(read, taxonomy.Settings(), declared)
            counted = [0]
            real = taxonomy._present_spellings

            def reading_counted(*args: object, **kwargs: object) -> object:
                counted[0] += 1
                return real(*args, **kwargs)  # type: ignore[arg-type]

            monkeypatch.setattr(taxonomy, "_present_spellings", reading_counted)
            settled = cli._people_said_settled(found, read, taxonomy.Settings(), [], [], [], (), declared)
            monkeypatch.setattr(taxonomy, "_present_spellings", real)
        finally:
            del cli._OPEN.sessions[len(cli._OPEN.sessions) - 1]
        assert settled == found
        assert 0 < counted[0] <= 2 * keys + 1, (keys, counted[0])


def test_the_people_key_reads_the_count_and_every_label_column(
    tmp_path: pathlib.Path, small_floors: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    """K-HZ-32 reads the product's own count beside the column it names, and every label column whatever role it was given (Codex's item 9).

    A count of twice the people under the right column's name passed, and
    a label column turned wholly to record numbers carried no levels and
    was skipped, so the common levels it lost were never counted: here the
    ward's four levels, each many patients hold, taken out of its block.
    """
    source, _keys = measures.people_table(tmp_path / "crossing", "crossing", rows=600, people=100)
    said, _screen = _run(["profile", f"{source}", "--person", "subject_id", "--identifier", "clinician_id"])
    assert said.verdict == results.NO_MISS, said.refusal
    assert measures._people_counted(source, ["subject_id", "clinician_id"], "subject_id") == 100
    real = cli._population_of

    def doubled(*args: object, **kwargs: object) -> "tuple[object, ...]":
        found = real(*args, **kwargs)  # type: ignore[arg-type]
        return found[:5] + (found[5] * 2,)

    monkeypatch.setattr(cli, "_population_of", doubled)
    assert measures._people_counted(source, ["subject_id", "clinician_id"], "subject_id") == 200
    monkeypatch.setattr(cli, "_population_of", real)
    before = measures._levels_by_said_persons(source, "subject_id")[1]
    described = source.parent / f"{source.stem}-profile.json"
    document = json.loads(described.read_text(encoding="utf-8"))
    wards = [block for block in document["columns"] if block.get("name") == "ward"]
    assert wards and len(wards[0].get("levels") or []) == 4
    wards[0].pop("levels")
    described.write_text(json.dumps(document), encoding="utf-8", newline="\n")
    assert measures._levels_by_said_persons(source, "subject_id")[1] == before + 4
