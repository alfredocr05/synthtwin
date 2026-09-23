"""P4-D340 and P4-D341: the population floor, and who the rows are about.

THE GATE OF LANDING 3.2. `synthtwin profile` refuses a table whose
population is under `parsing.POPULATION_FLOOR` and writes nothing;
between there and `parsing.POPULATION_NOTICE_LINE` it runs and says so
on the screen and on every page it writes; at or above the line it says
nothing at all. The population is counted in ROWS where no declared
identifier repeats and in PEOPLE where one does.

EVERY NUMBER IN THIS FILE IS DERIVED FROM THE RULE. The refusal band is
`range(1, parsing.POPULATION_FLOOR)`, the notice band is
`[parsing.POPULATION_FLOOR, parsing.POPULATION_NOTICE_LINE - 1]` and
the silent band starts at the line, so moving either constant moves
every expectation here with it and a run's output is never copied in.

WHAT THIS FILE ALSO REFUSES TO LET DRIFT. The floor is the COMMAND's,
so `profile.build_document`, the loader and `synthtwin validate` still
work on small files -- that is asserted here rather than left to be
noticed when somebody puts the check in a shared place.
"""

import json
import pathlib
import random

import pytest

from synthtwin import asking, contract, errors, parsing, profile, taxonomy
from synthtwin.cli import main

import fixtures


# -- tables ------------------------------------------------------------


def _rows(count: int, subjects: "int | None" = None) -> "list[list[str]]":
    """`count` rows; `subjects` people repeating in `subject_id` if given.

    With no subject count every identifier is different, which is a
    column that names a ROW and never a person.
    """
    draw = random.Random(4)
    built: "list[list[str]]" = []
    for place in range(count):
        who = place if subjects is None else place % subjects
        built += [
            [
                f"P{who + 1:05d}",
                fixtures.REGIONS[place % 4],
                f"{draw.randint(0, 100)}",
            ]
        ]
    return built


def _table(
    folder: pathlib.Path, count: int, subjects: "int | None" = None
) -> pathlib.Path:
    return fixtures.write(
        folder,
        "clinic.csv",
        fixtures.rows_to_csv(
            ["subject_id", "site", "score"], _rows(count, subjects)
        ),
    )


def _pages(folder: pathlib.Path) -> "list[str]":
    return sorted(one.name for one in folder.iterdir())


def _table_note(folder: pathlib.Path) -> str:
    """The description's note about the whole table, or the empty text."""
    document = json.loads(
        (folder / "clinic-profile.json").read_text(encoding="utf-8")
    )
    for note in document["publication_notes"]:
        if note["column"] == "":
            return f"{note['note']}"
    return ""


# -- the refusal -------------------------------------------------------


@pytest.mark.parametrize(
    "count", [1, parsing.POPULATION_FLOOR - 1]
)
def test_a_table_under_the_floor_is_refused_and_nothing_is_written(
    tmp_path: pathlib.Path, count: int
) -> None:
    """One row and one row short of the floor, through `cli.main`.

    The two ends of the refusal band: the smallest table there is, and
    the largest one the floor still refuses. Both are counted in rows,
    because no identifier is declared.
    """
    folder = tmp_path / f"n{count}"
    folder.mkdir()
    table = _table(folder, count)
    assert main(["profile", f"{table}"]) == 1
    assert _pages(folder) == ["clinic.csv"], (
        "a refused run wrote a file: the refusal happens before the "
        "description is built and nothing may reach the disk"
    )


def test_the_refusal_names_the_count_the_line_and_what_to_do() -> None:
    """The four things P4-D341 says this message owes its reader."""
    message = errors.the_population_is_too_small(
        parsing.POPULATION_FLOOR - 1, taxonomy.NOTE_UNIT_ROWS, ""
    )
    assert f"{parsing.POPULATION_FLOOR - 1} rows" in message
    assert f"{parsing.POPULATION_FLOOR} rows" in message
    assert "run the command again" in message
    assert message.rstrip().endswith("Nothing was written.")


def test_the_people_refusal_names_the_column_the_people_were_counted_by(
) -> None:
    said = errors.the_population_is_too_small(
        7, taxonomy.NOTE_UNIT_PEOPLE, "subject_id"
    )
    assert "7 people" in said
    assert "'subject_id'" in said
    assert "--identifier" in said


# -- the notice band ---------------------------------------------------


@pytest.mark.parametrize(
    "count",
    [parsing.POPULATION_FLOOR, parsing.POPULATION_NOTICE_LINE - 1],
)
def test_a_table_in_the_notice_band_runs_and_says_so_everywhere(
    tmp_path: pathlib.Path, count: int, capsys: pytest.CaptureFixture[str]
) -> None:
    """Both ends of the notice band: the screen and every written page.

    The sentence is the description's own note, so this asserts the
    note is THERE and that each page carries that same text -- never a
    second sentence written at a call site.
    """
    folder = tmp_path / f"n{count}"
    folder.mkdir()
    table = _table(folder, count)
    assert main(["profile", f"{table}"]) == 0
    screen = capsys.readouterr()
    said = _table_note(folder)
    assert said, "the description carries no note about the whole table"
    assert f"{count} rows" in said
    # THE SCREEN'S OWN NOTICE, and not the summary's copy of the note.
    # The summary is printed to the screen too, so a check for the
    # sentence alone passes with the command's notice deleted; the
    # heading `_small_population_notice` writes is what only the
    # command prints.
    assert "ABOUT THE SIZE OF THIS TABLE" in screen.err + screen.out
    for page, text in (
        ("the screen", screen.err + screen.out),
        (
            "the summary",
            (folder / "clinic-profile.txt").read_text(encoding="utf-8"),
        ),
        (
            "the questions file",
            (folder / "clinic-questions.json").read_text(encoding="utf-8"),
        ),
    ):
        assert said in text, f"{page} does not carry the notice"


def test_the_notice_reaches_the_twin_report_and_the_quality_report(
    tmp_path: pathlib.Path,
) -> None:
    """Both are rendered FROM the description's note, so both must show it."""
    folder = tmp_path / "band"
    folder.mkdir()
    table = _table(folder, parsing.POPULATION_FLOOR)
    assert main(["profile", f"{table}"]) == 0
    description = folder / "clinic-profile.json"
    assert main(["generate", f"{description}"]) == 0
    assert main(["validate", f"{description}"]) == 0
    said = _table_note(folder)
    for name in ("clinic-twin-report.txt", "clinic-twin-quality.txt"):
        text = (folder / name).read_text(encoding="utf-8")
        assert said in text, f"{name} does not carry the notice"


def test_the_twin_table_carries_no_trace_of_the_notice(
    tmp_path: pathlib.Path,
) -> None:
    """Code written against the twin runs unchanged (the first goal).

    The same table is described twice -- once through the command, so
    the note is there, and once through `build_document`, where it is
    not -- and the two twins are compared byte for byte. A note that
    reached the twin's cells would show up here as a difference.
    """
    folder = tmp_path / "with"
    folder.mkdir()
    table = _table(folder, parsing.POPULATION_FLOOR)
    assert main(["profile", f"{table}"]) == 0
    assert main(["generate", f"{folder / 'clinic-profile.json'}"]) == 0
    noticed = (folder / "clinic-twin.csv").read_bytes()

    from synthtwin import generation, reading, rendering

    settings = taxonomy.Settings()
    read = reading.read_table(
        f"{table}", "auto", small_cell_floor=settings.small_cell_floor
    )
    plain = profile.build_document(read, settings, [])
    notes = plain["publication_notes"]
    assert isinstance(notes, list)
    assert not [note for note in notes if note["column"] == ""]
    quiet = tmp_path / "without"
    quiet.mkdir()
    at = fixtures.write(quiet, "clinic-profile.json", profile.serialize(plain))
    written = rendering.twin_csv(
        generation.generate(contract.load_profile(f"{at}"), 0)
    )
    assert written.encode("utf-8") == noticed


def test_a_table_at_the_line_carries_no_notice(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """At `POPULATION_NOTICE_LINE` the run says nothing about its size."""
    folder = tmp_path / "big"
    folder.mkdir()
    table = _table(folder, parsing.POPULATION_NOTICE_LINE)
    assert main(["profile", f"{table}"]) == 0
    screen = capsys.readouterr()
    assert _table_note(folder) == ""
    assert "ABOUT THE SIZE OF THIS TABLE" not in screen.err + screen.out


# -- counted in people -------------------------------------------------


def test_people_under_the_floor_over_many_rows_are_refused(
    tmp_path: pathlib.Path,
) -> None:
    """500 rows, one short of the floor in people: refused, nothing written."""
    folder = tmp_path / "few"
    folder.mkdir()
    table = _table(folder, 500, subjects=parsing.POPULATION_FLOOR - 1)
    assert main(["profile", f"{table}", "--identifier", "subject_id"]) == 1
    assert _pages(folder) == ["clinic.csv"]


def test_people_at_the_floor_over_many_rows_get_the_notice(
    tmp_path: pathlib.Path,
) -> None:
    """500 rows and exactly the floor in people: it runs, counted in people."""
    folder = tmp_path / "enough"
    folder.mkdir()
    table = _table(folder, 500, subjects=parsing.POPULATION_FLOOR)
    assert main(["profile", f"{table}", "--identifier", "subject_id"]) == 0
    said = _table_note(folder)
    assert f"{parsing.POPULATION_FLOOR} people" in said
    document = json.loads(
        (folder / "clinic-profile.json").read_text(encoding="utf-8")
    )
    assert document["settings"]["person_columns"] == ["subject_id"]


# -- the person rule ---------------------------------------------------


def _people(
    names: "list[str]",
    columns: "list[list[str]]",
    declared: "list[str]",
) -> "tuple[tuple[str, ...], int]":
    settings = taxonomy.Settings()
    repeating = taxonomy.repeating_identifiers(
        names, columns, declared, settings
    )
    return repeating, taxonomy.people_in(names, columns, repeating, settings)


def test_a_unique_identifier_beside_a_repeating_one_is_not_the_person(
) -> None:
    """`visit_id` is one row's name; `subject_id` is one person's.

    Both are declared. The unique one has no folded value on two rows,
    so it names nobody and the count is the repeating one's.
    """
    names = ["subject_id", "visit_id"]
    subjects = [f"P{place % 30:05d}" for place in range(120)]
    visits = [f"V{place:07d}" for place in range(120)]
    repeating, people = _people(names, [subjects, visits], names)
    assert repeating == ("subject_id",)
    assert people == 30


def test_the_sparse_unique_identifier_case_counts_the_repeating_one() -> None:
    """The skeptic's refuted case, at the size it was measured at.

    150 subjects, and a second declared identifier standing on 90 of
    the rows and different on every one of them. The rule this replaces
    chose the sparse one and counted 91 people, which REFUSED a table
    of 150 subjects. Counting the identifiers that REPEAT gives 150.
    """
    subjects: "list[str]" = []
    samples: "list[str]" = []
    for place in range(450):
        subjects += [f"P{place % 150:05d}"]
        samples += [f"S{place:07d}" if place < 90 else ""]
    repeating, people = _people(
        ["subject_id", "sample_id"],
        [subjects, samples],
        ["sample_id", "subject_id"],
    )
    assert repeating == ("subject_id",)
    assert people == 150


def test_rows_naming_nobody_are_one_unknown_person() -> None:
    """Twelve rows hold no subject; between them they are ONE person.

    Counting one person per such row would count people the table does
    not evidence, in the direction that lets a small table through.
    """
    subjects = [f"P{place % 20:05d}" for place in range(100)] + [""] * 12
    repeating, people = _people(
        ["subject_id"], [subjects], ["subject_id"]
    )
    assert repeating == ("subject_id",)
    assert people == 21


def test_several_repeating_identifiers_are_a_union() -> None:
    """Rows sharing a value of EITHER column are one person.

    Two columns, each repeating, whose groups overlap on one row: the
    union joins those two groups into one, so the count is lower than
    either column alone would give.
    """
    left = ["a", "a", "b", "b", "c", "c"]
    right = ["x", "y", "y", "z", "z", "w"]
    repeating, people = _people(
        ["left", "right"], [left, right], ["left", "right"]
    )
    assert repeating == ("left", "right")
    # a-a joins rows 0 and 1; y joins 1 and 2; b joins 2 and 3; z joins
    # 3 and 4; c joins 4 and 5 -- one chain over all six rows.
    assert people == 1


def test_identity_is_folded() -> None:
    """`A12` and `a12 ` are one person, which can only lower the count."""
    cells = ["A12", "a12 ", " A12", "B7", "b7"]
    repeating, people = _people(["who"], [cells], ["who"])
    assert repeating == ("who",)
    assert people == 2


def test_an_identifier_that_never_repeats_leaves_the_count_in_rows() -> None:
    cells = [f"V{place:05d}" for place in range(40)]
    repeating, people = _people(["visit_id"], [cells], ["visit_id"])
    assert repeating == ()
    assert people == 40


# -- the floor is the command's, and nothing else's --------------------


def test_build_document_still_describes_a_five_row_table(
    tmp_path: pathlib.Path,
) -> None:
    """The producer refuses no table for its size (P4-D341)."""
    from synthtwin import reading

    folder = tmp_path / "five"
    folder.mkdir()
    table = _table(folder, 5)
    settings = taxonomy.Settings()
    read = reading.read_table(
        f"{table}", "auto", small_cell_floor=settings.small_cell_floor
    )
    document = profile.build_document(read, settings, [])
    assert document["n_rows"] == 5
    written = fixtures.write(
        folder, "clinic-profile.json", profile.serialize(document)
    )
    assert contract.load_profile(f"{written}").n_rows == 5


def test_validate_still_checks_a_fifty_row_file(
    tmp_path: pathlib.Path,
) -> None:
    """A description of a 50-row table, checked against a 50-row file.

    The description is built by the PRODUCER rather than by the
    command, because the command would refuse the table -- which is the
    separation this asserts.
    """
    from synthtwin import reading, validation

    folder = tmp_path / "small"
    folder.mkdir()
    table = _table(folder, 50)
    settings = taxonomy.Settings()
    read = reading.read_table(
        f"{table}", "auto", small_cell_floor=settings.small_cell_floor
    )
    document = profile.build_document(read, settings, [])
    written = fixtures.write(
        folder, "clinic-profile.json", profile.serialize(document)
    )
    outcome = validation.measure(
        contract.load_profile(f"{written}"), f"{table}"
    )
    assert outcome.census.missed == 0


# -- the person question -----------------------------------------------


def _asked_about(
    folder: pathlib.Path, rows: "list[list[str]]", declared: "list[str]"
) -> "list[str]":
    from synthtwin import reading

    table = fixtures.write(
        folder,
        "ask.csv",
        fixtures.rows_to_csv(["subject_id", "site", "score"], rows),
    )
    settings = taxonomy.Settings()
    read = reading.read_table(
        f"{table}", "auto", small_cell_floor=settings.small_cell_floor
    )
    document = profile.build_document(read, settings, list(declared))
    asked = asking.questions_for(
        document, read.columns, settings, list(declared)
    )
    person = asking.person_questions(
        document, read.columns, settings, list(declared), list(declared), asked
    )
    return [question.name for question in person]


def test_a_subject_column_with_a_few_visits_each_is_asked_about(
    tmp_path: pathlib.Path,
) -> None:
    """500 rows over 111 subjects, nothing declared: the question is put."""
    folder = tmp_path / "ask"
    folder.mkdir()
    assert _asked_about(folder, _rows(500, subjects=111), []) == [
        "subject_id"
    ]


def test_nothing_is_asked_once_an_identifier_is_declared(
    tmp_path: pathlib.Path,
) -> None:
    """The person has answered; asking again says it was not heard."""
    folder = tmp_path / "declared"
    folder.mkdir()
    assert _asked_about(
        folder, _rows(500, subjects=111), ["subject_id"]
    ) == []


def test_another_column_declared_silences_the_question_too(
    tmp_path: pathlib.Path,
) -> None:
    """The rule is "NO identifier declared", not "not THIS one".

    `site` is declared here and `subject_id` is not, so a rule that
    only skipped the declared column would still ask about
    `subject_id`. Somebody who has said which column holds their record
    numbers has answered the question, and asking a second one says
    their answer was not heard.
    """
    folder = tmp_path / "other"
    folder.mkdir()
    assert _asked_about(folder, _rows(500, subjects=111), ["site"]) == []


def test_a_label_column_and_a_scale_column_are_never_asked_about(
    tmp_path: pathlib.Path,
) -> None:
    """`site` is a set of categories; `score` is a bounded scale.

    Both repeat, and `score` has more different values than `site`; the
    two measured conditions and the role test keep both out. This is
    the owner's ruling of 2026-09-22 about bounded scales, in a test.
    """
    folder = tmp_path / "labels"
    folder.mkdir()
    asked = _asked_about(folder, _rows(500, subjects=111), [])
    assert "site" not in asked
    assert "score" not in asked


def test_a_unique_column_is_never_asked_about(
    tmp_path: pathlib.Path,
) -> None:
    """Its values do not repeat, so it names a row and not a person."""
    folder = tmp_path / "unique"
    folder.mkdir()
    assert _asked_about(folder, _rows(500), []) == []


def test_the_question_offers_the_identifier_declaration(
    tmp_path: pathlib.Path,
) -> None:
    """Its answer becomes `--identifier`, by the route every answer takes."""
    from synthtwin import reading

    folder = tmp_path / "offer"
    folder.mkdir()
    table = fixtures.write(
        folder,
        "ask.csv",
        fixtures.rows_to_csv(
            ["subject_id", "site", "score"], _rows(500, subjects=111)
        ),
    )
    settings = taxonomy.Settings()
    read = reading.read_table(
        f"{table}", "auto", small_cell_floor=settings.small_cell_floor
    )
    document = profile.build_document(read, settings, [])
    person = asking.person_questions(
        document, read.columns, settings, [], [], []
    )
    assert len(person) == 1
    offered = [choice.answer for choice in person[0].choices]
    assert asking.ANSWER_IDENTIFIER in offered
    assert offered[0] == asking.ANSWER_KEEP
    assert person[0].taken == asking.ANSWER_KEEP
    assert person[0].reason == asking.BECAUSE_REPEATS_AND_MANY


def test_the_screen_says_the_count_was_taken_in_rows_at_the_terminal(
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The person is asked, answers nothing, and is told what was done.

    A question about a column that might name people, with no answer,
    leaves the run counting ROWS -- and a person who was asked and
    said nothing has to be told which way it went, or the question
    reads as information wanted rather than a decision with a standing
    answer. The scripted path says the same thing inside its own
    notice; this is the path where somebody is at the keyboard.
    """
    from synthtwin import cli

    monkeypatch.setattr(cli, "_there_is_somebody_to_ask", lambda: True)
    answers = iter([""] * 9)
    monkeypatch.setattr(
        cli, "_read_one_answer", lambda standing: next(answers)
    )
    folder = tmp_path / "silent"
    folder.mkdir()
    table = _table(folder, 500, subjects=111)
    assert main(["profile", f"{table}"]) == 0
    said = capsys.readouterr()
    assert "counted in ROWS" in said.err
    assert "subject_id" in said.err
    document = json.loads(
        (folder / "clinic-profile.json").read_text(encoding="utf-8")
    )
    assert document["settings"]["person_columns"] == []
    assert "500 rows" in _table_note(folder)


def test_the_question_reaches_the_questions_file_and_the_screen(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Asking is part of the product (A-P4-56, A-P4-58).

    And the screen says what the run did in the meantime: the
    population was counted in ROWS.
    """
    folder = tmp_path / "run"
    folder.mkdir()
    table = _table(folder, 500, subjects=111)
    assert main(["profile", f"{table}"]) == 0
    screen = capsys.readouterr()
    written = json.loads(
        (folder / "clinic-questions.json").read_text(encoding="utf-8")
    )
    asked = [entry["column"] for entry in written["asked"]]
    assert "subject_id" in asked
    assert "counted in ROWS" in screen.err + screen.out


# -- the gate after the on-screen answers ------------------------------


def test_an_answer_at_the_terminal_can_refuse_the_run(
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The second gate, and it is the one that decides.

    500 rows over 80 subjects. Counted in rows the table is over the
    floor and the run starts; the person then answers, on the screen,
    that `subject_id` holds record numbers -- and the population is 80
    people, which is under the floor. The refusal has to arrive HERE,
    before anything is announced and before anything is written, or a
    table of 80 people is described because nobody asked a second time.

    The 80 is derived: it has to be under `POPULATION_FLOOR` so the
    second gate refuses, and above the categorical ceiling of a 500-row
    table so the question is put at all.
    """
    from synthtwin import cli

    monkeypatch.setattr(cli, "_there_is_somebody_to_ask", lambda: True)
    answers = iter([asking.ANSWER_IDENTIFIER] + [""] * 8)
    monkeypatch.setattr(
        cli, "_read_one_answer", lambda standing: next(answers)
    )
    folder = tmp_path / "answered"
    folder.mkdir()
    table = _table(folder, 500, subjects=80)
    assert main(["profile", f"{table}"]) == 1
    said = capsys.readouterr()
    assert "80 people" in said.err
    assert _pages(folder) == ["clinic.csv"], (
        "the run answered at the terminal and then wrote a file: the "
        "second gate must refuse before anything is written"
    )


def test_an_answer_at_the_terminal_can_move_the_count_into_the_band(
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """1,200 rows over 300 subjects: silent in rows, noticed in people.

    The first gate counts 1,200 rows and says nothing. The answer makes
    it 300 people, which is in the notice band -- so the note the
    description carries is the one taken AFTER the answer.
    """
    from synthtwin import cli

    monkeypatch.setattr(cli, "_there_is_somebody_to_ask", lambda: True)
    answers = iter([asking.ANSWER_IDENTIFIER] + [""] * 8)
    monkeypatch.setattr(
        cli, "_read_one_answer", lambda standing: next(answers)
    )
    folder = tmp_path / "moved"
    folder.mkdir()
    table = _table(folder, 1200, subjects=300)
    assert main(["profile", f"{table}"]) == 0
    capsys.readouterr()
    assert "300 people" in _table_note(folder)
    document = json.loads(
        (folder / "clinic-profile.json").read_text(encoding="utf-8")
    )
    assert document["settings"]["person_columns"] == ["subject_id"]


# -- no cell of the table reaches any of it ----------------------------


def test_the_notice_and_the_question_carry_no_value_of_the_table(
    tmp_path: pathlib.Path,
) -> None:
    """The one rule both the notice and the questions file live under.

    A spelling written into every cell of a column must appear on no
    page this run writes except where the description already publishes
    it, and it is written into a column that publishes nothing.
    """
    folder = tmp_path / "secret"
    folder.mkdir()
    rows = _rows(500, subjects=111)
    for row in rows:
        row[0] = f"{row[0]}-GOLDFINCH"
    table = fixtures.write(
        folder,
        "clinic.csv",
        fixtures.rows_to_csv(["subject_id", "site", "score"], rows),
    )
    assert main(["profile", f"{table}", "--identifier", "subject_id"]) == 0
    for name in ("clinic-profile.json", "clinic-profile.txt",
                 "clinic-questions.json"):
        text = (folder / name).read_text(encoding="utf-8")
        assert "GOLDFINCH" not in text, f"{name} carries a cell"


# -- what the guard and the loader still refuse ------------------------


def _described(folder: pathlib.Path, count: int) -> "dict[str, object]":
    from synthtwin import reading

    table = _table(folder, count)
    settings = taxonomy.Settings()
    read = reading.read_table(
        f"{table}", "auto", small_cell_floor=settings.small_cell_floor
    )
    return profile.build_document(read, settings, [])


def test_a_note_may_name_no_column_that_is_not_one(
    tmp_path: pathlib.Path,
) -> None:
    """The publication guard's widening admits the EMPTY name and nothing else.

    A note about the whole table names no column, so the guard takes
    the empty spelling there (plan P4-D341). What it may not take is a
    name this table does not have -- which is the half a widening can
    quietly lose, so it is asserted rather than assumed.
    """
    folder = tmp_path / "guard"
    folder.mkdir()
    document = _described(folder, parsing.POPULATION_FLOOR)
    notes = document["publication_notes"]
    assert isinstance(notes, list)
    said = taxonomy.note(
        taxonomy.NOTE_SMALL_POPULATION,
        (parsing.POPULATION_FLOOR, taxonomy.NOTE_UNIT_ROWS),
    )
    document["publication_notes"] = [{"column": "", "note": said}] + notes
    profile.check_publication(document)
    document["publication_notes"] = [
        {"column": "no_such_column", "note": said}
    ] + notes
    with pytest.raises(errors.ProfileError):
        profile.check_publication(document)


def test_the_loader_refuses_a_person_column_nobody_declared(
    tmp_path: pathlib.Path,
) -> None:
    """Invariant S8b: `person_columns` is derived from the declarations.

    A name here that is not under `forced_identifiers` says the rows
    were counted by a column whose values the description never looked
    at that way, so no producer of this contract writes it.
    """
    folder = tmp_path / "s8b"
    folder.mkdir()
    document = _described(folder, parsing.POPULATION_FLOOR)
    settings = document["settings"]
    assert isinstance(settings, dict)
    settings["person_columns"] = ["subject_id"]
    written = fixtures.write(
        folder, "broken-profile.json", profile.serialize(document)
    )
    with pytest.raises(errors.ProfileError) as caught:
        contract.load_profile(f"{written}")
    assert "S8b" in f"{caught.value}"


def test_the_loader_refuses_a_table_wide_note_after_a_column_s(
    tmp_path: pathlib.Path,
) -> None:
    """Invariant S11: a note about the table comes before every column's."""
    folder = tmp_path / "s11"
    folder.mkdir()
    document = _described(folder, parsing.POPULATION_FLOOR)
    notes = document["publication_notes"]
    assert isinstance(notes, list) and notes, (
        "this shape needs at least one column note to put a table-wide "
        "note after"
    )
    said = f"{taxonomy.note(taxonomy.NOTE_SMALL_POPULATION, (parsing.POPULATION_FLOOR, taxonomy.NOTE_UNIT_ROWS))}"
    document["publication_notes"] = notes + [{"column": "", "note": said}]
    written = fixtures.write(
        folder, "broken-profile.json", profile.serialize(document)
    )
    with pytest.raises(errors.ProfileError) as caught:
        contract.load_profile(f"{written}")
    assert "S11" in f"{caught.value}"
