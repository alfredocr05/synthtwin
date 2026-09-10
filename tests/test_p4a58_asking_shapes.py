"""A question describes a column's shape and carries none of its values.

AMENDMENT A-P4-58 and the owner's ruling of 2026-09-10. Two things
land here and they are one decision seen twice.

**The question stops showing cells.** It carried four real values,
because a question about a column looked unanswerable without them. It
is answerable: what a person needs is what synthtwin SAW, and "every
value is written in figures alone, all five characters wide" says that
in words that may leave the machine where a cell may not. The rule the
plan fixes for the questions file is that it may name the column, the
choices, and any spelling the description itself would publish -- a
separator is one -- and no value of the table. A screen that showed
values while the file withheld them would be a second question, which
is the thing that rule exists to stop.

**And every column read as a number is listed under ONE question.** The
questions above are the columns whose VALUES raised one. A register of
drug concept identifiers six and seven figures wide raises nothing and
can raise nothing: it is written exactly as a count is written, and the
rule that tried to tell them apart was deleted for guessing in review
item P1-R6-F7. Nothing reaches such a column but a person reading a
list of their own columns -- so they get one list and one question,
which is a minute's reading, rather than a question per column, which
is a form nobody finishes (amendment A-P4-56 point 1).
"""

import pathlib
import random
import tempfile

import fixtures
from synthtwin import asking, cli, profile, reading, taxonomy


def _described(
    columns: "dict[str, list[str]]",
) -> "tuple[dict, object, taxonomy.Settings]":
    folder = pathlib.Path(tempfile.mkdtemp())
    names = sorted(columns)
    rows: list[list[str]] = []
    deep = len(columns[names[0]])
    for place in range(deep):
        rows = rows + [[columns[name][place] for name in names]]
    table = fixtures.write(
        folder, "t.csv", fixtures.rows_to_csv(names, rows)
    )
    read = reading.read_table(f"{table}")
    settings = taxonomy.Settings()
    document = profile.build_document(read, settings, [], [])
    return document, read, settings


def _clinic() -> "dict[str, list[str]]":
    draw = random.Random(5)
    return {
        "procedure_code": [
            f"{draw.choice([80053, 99213, 29881, 45378, 20610]):05d}"
            for _index in range(300)
        ],
        "drug_concept_id": [
            f"{draw.randint(100000, 9999999)}" for _index in range(300)
        ],
        "age": [f"{draw.randint(20, 90)}" for _index in range(300)],
        "diagnosis": [
            draw.choice(["E11.9", "I10", "N18.3", "J45.909"])
            for _index in range(300)
        ],
    }


def test_no_question_carries_a_value_of_the_table() -> None:
    """The property the disclosure rule rests on, over a whole table."""
    columns = _clinic()
    document, read, settings = _described(columns)
    asked = asking.questions_for(document, read.columns, settings, [])
    listed = asking.checklist_for(
        document, read.columns, settings, [], asked
    )
    assert asked, "the padded and fixed-width columns must be asked about"
    assert listed, "the identifier register must be listed"
    cells: set = set()
    for values in columns.values():
        for value in values:
            cells.add(value)
    for question in asked + listed:
        spoken = f"{question.name} {question.shape}"
        for choice in question.choices:
            spoken = f"{spoken} {choice.means} {choice.publishes}"
        for value in cells:
            if len(value) < 3:
                # A one- or two-character value is a substring of
                # ordinary prose and says nothing about disclosure; the
                # rule is about a CELL leaving, not about the figure 20
                # appearing in a count.
                continue
            assert value not in spoken, (question.name, value)


def test_the_shape_says_what_synthtwin_saw() -> None:
    """Each reason describes itself in words a person can act on."""
    columns = _clinic()
    document, read, settings = _described(columns)
    asked = asking.questions_for(document, read.columns, settings, [])
    shapes = {question.name: question.shape for question in asked}
    assert "5 characters wide" in shapes["procedure_code"], shapes
    assert "figures alone" in shapes["procedure_code"], shapes
    # ...and the padded column says HOW MANY carry a leading zero,
    # which is a count of cells and not one of their values.
    padded = 0
    for value in columns["procedure_code"]:
        if value[0] == "0":
            padded = padded + 1
    assert padded == 0, (
        "the fixture's procedure codes are five figures with no "
        "leading zero, so this column is asked about for its WIDTH; a "
        "fixture that drifted into padding would test the other reason "
        "under this name"
    )


def test_the_checklist_reaches_the_column_no_rule_can_see() -> None:
    """THE SHAPE THIS EXISTS FOR, and the reason it is a list.

    A register of drug concept identifiers is six and seven figures
    wide, so it is not one fixed width; it carries no leading zero; and
    every value differs. Nothing in it is a signal. It lands on `count`
    and its description publishes an average over concept identifiers.
    No rule finds it and no remark can honestly single it out.
    """
    columns = _clinic()
    document, read, settings = _described(columns)
    asked = asking.questions_for(document, read.columns, settings, [])
    listed = asking.checklist_for(
        document, read.columns, settings, [], asked
    )
    names = [question.name for question in listed]
    assert "drug_concept_id" in names, names
    # ...it is not ALSO asked about, so a person meets it once...
    assert "drug_concept_id" not in [
        question.name for question in asked
    ]
    # ...a column already read as codes is listed as such...
    for question in listed:
        if question.name == "diagnosis":
            assert question.taken == asking.ANSWER_CODE
            assert "already read as codes" in question.shape
    # ...and a genuine measurement is listed too, because nothing
    # separates it either and the person is the one who knows.
    assert "age" in names


def test_a_column_already_asked_or_declared_is_not_listed_twice() -> None:
    """One column, one place: a person answers it once."""
    columns = _clinic()
    document, read, settings = _described(columns)
    asked = asking.questions_for(document, read.columns, settings, [])
    listed = asking.checklist_for(
        document, read.columns, settings, [], asked
    )
    spoken = [question.name for question in asked]
    for question in listed:
        assert question.name not in spoken, question.name
    # ...and a declared column is in neither.
    declared = asking.checklist_for(
        document, read.columns, settings, ["drug_concept_id"], asked
    )
    assert "drug_concept_id" not in [
        question.name for question in declared
    ]


def test_every_choice_says_what_the_description_would_publish() -> None:
    """The half a person actually decides on.

    "Codes" and "measurements" are labels for a choice whose real
    content is what the description will carry. A person choosing
    between two words is guessing; a person choosing between "an
    average, a spread, a smallest and a largest" and "every value
    exactly as written, with the number of rows that carried it" is
    deciding.
    """
    columns = _clinic()
    document, read, settings = _described(columns)
    asked = asking.questions_for(document, read.columns, settings, [])
    for question in asked:
        assert len(question.choices) == 3
        for choice in question.choices:
            assert choice.publishes and choice.means
        # THE STANDING READING IS FIRST, because a person reads the
        # first of three as the default whatever the words say, so the
        # order has to agree with the behaviour.
        assert question.choices[0].answer == question.taken
        # ...and it is the reading the tool ACTUALLY takes today. The
        # owner ruled that an unanswered column of figures should read
        # as codes; that is a change to what `profile` does and lands
        # with the answers path that makes it. A file naming a reading
        # the run does not take is the one thing it may never be.
        assert question.taken == asking.ANSWER_MEASUREMENT


def test_the_scripted_notice_puts_the_checklist_and_shows_no_cell(
) -> None:
    """What a run with nobody at the keyboard tells the person."""
    columns = _clinic()
    document, read, settings = _described(columns)
    asked = asking.questions_for(document, read.columns, settings, [])
    listed = asking.checklist_for(
        document, read.columns, settings, [], asked
    )
    # THE TWO NOTICES ARE SEPARATE, and that is review round 1's first
    # item: the checklist hung off the scripted one and so reached
    # three of the four ways a person runs this command not at all.
    notice = cli._assumptions_notice(asked)
    checklist = cli._checklist_notice(listed)
    assert asking.CHECKLIST_HEADING in checklist
    assert "drug_concept_id" in checklist
    assert "--code" in checklist and "--identifier" in checklist
    for values in columns.values():
        for value in set(values):
            if len(value) < 3:
                continue
            assert value not in notice, value
            assert value not in checklist, value


def test_the_questions_document_is_the_same_bytes_every_time() -> None:
    """Determinism (plan D12): the same table, the same file."""
    from synthtwin import canonical

    columns = _clinic()
    first = ""
    for _run in range(3):
        document, read, settings = _described(columns)
        asked = asking.questions_for(document, read.columns, settings, [])
        listed = asking.checklist_for(
            document, read.columns, settings, [], asked
        )
        text = canonical.serialize(
            asking.questions_document("t.csv", asked, listed)
        )
        if not first:
            first = text
        assert text == first
    assert "asked" in first and "checklist" in first


# -- what review round 1 of landing L17a sent back --------------------


def test_the_checklist_reaches_a_run_whose_only_finding_it_is() -> None:
    """ROUND 1, ITEM 1: it hung off a notice that rarely fires.

    The checklist was rendered inside the scripted assumptions notice,
    which fires only where a column's VALUES raised a question AND only
    where nobody is at the keyboard. Three of the four ways a person
    runs this command therefore never saw it -- and a table whose ONLY
    finding is the checklist, which is the case it exists for, showed
    nothing at all.

    It is the one class of column nothing else can reach, so it is the
    last thing that should depend on another column raising a question.
    """
    columns = {
        "drug_concept_id": [
            f"{100000 + index * 40001}" for index in range(300)
        ]
    }
    document, read, settings = _described(columns)
    asked = asking.questions_for(document, read.columns, settings, [])
    listed = asking.checklist_for(
        document, read.columns, settings, [], asked
    )
    assert not asked, "nothing in this column's values raises a question"
    assert listed, "and the checklist is the only thing that reaches it"
    # ...and it has a renderer of its own, so it does not depend on the
    # other notice being written at all.
    spoken = cli._checklist_notice(listed)
    assert "drug_concept_id" in spoken
    assert asking.CHECKLIST_HEADING in spoken


def test_a_count_below_the_floor_is_not_named() -> None:
    """ROUND 1, ITEM 2: the disclosure floor reaches the shape.

    At a smallest-group size of eleven, a column of one `001` beside
    299 ordinary numbers said "1 of them carry a leading zero" -- a
    count of one, on a surface the plan holds to naming no count below
    the floor, and one that reaches the prompt and, once the file
    lands, a document that travels.

    THAT A COLUMN CARRIES PADDING IS A FACT ABOUT HOW IT WAS WRITTEN,
    which is what the question is about; how MANY cells carry it is a
    count of a group, and a group under the floor is not named here any
    more than anywhere else.
    """
    below = {"code": ["001"] + [f"{1000 + index}" for index in range(299)]}
    document, read, settings = _described(below)
    settings = taxonomy.Settings(small_cell_floor=11)
    document = profile.build_document(read, settings, [], [])
    asked = asking.questions_for(document, read.columns, settings, [])
    assert asked
    assert "some of them" in asked[0].shape, asked[0].shape
    assert " 1 of them" not in asked[0].shape, asked[0].shape
    # ...and a count AT or above the floor is named, so the rule is a
    # floor and not a silence.
    above = {"code": [f"{index:04d}" for index in range(300)]}
    document, read, settings = _described(above)
    settings = taxonomy.Settings(small_cell_floor=11)
    document = profile.build_document(read, settings, [], [])
    asked = asking.questions_for(document, read.columns, settings, [])
    assert asked and "300 of them" in asked[0].shape, asked[0].shape


def test_the_standing_reading_is_the_one_enter_gives() -> None:
    """ROUND 1, ITEM 3: a joined question named a default it is not.

    Three hundred different `100|30` cells land on `free_text`. The
    question recorded `joined` as the reading taken and the prompt said
    Enter would keep it -- but Enter makes no declaration, so it keeps
    free text, and declaring `joined` is what CHANGES the reading. The
    standing answer is now one of its own.
    """
    columns = {
        "bp": [f"{100 + index}|{30 + index}" for index in range(300)]
    }
    document, read, settings = _described(columns)
    assert document["columns"][0]["role"] == "free_text"
    asked = asking.questions_for(document, read.columns, settings, [])
    assert asked and asked[0].taken == asking.ANSWER_KEEP
    assert asked[0].choices[0].answer == asking.ANSWER_KEEP
    # ...and what it says that publishes is what free text publishes.
    assert "no value of the column" in asked[0].choices[0].publishes
    # ...and the prompt renders it rather than failing on an unknown key.
    spoken = cli._the_question(asked[0], 1, 1)
    assert "leave it as it is" in spoken


def test_no_choice_promises_what_the_role_or_the_floor_forbids() -> None:
    """ROUND 1, ITEM 4: two promises were measurably false.

    A column of 400-figure integers takes `numeric_unrepresentable`,
    which publishes NO numeric statistic at all, and its measurement
    choice offered an average, a spread and ends. At a smallest-group
    size of eleven a label column withholds its rare values, and the
    code choice promised that every value is kept exactly as written.

    A choice that overstates what it buys is worse than no choice: the
    person is deciding on that sentence and it is the only part of the
    question they cannot check themselves.
    """
    document, read, settings = _described(
        {"big": ["9" * 400 for _index in range(300)]}
    )
    assert document["columns"][0]["role"] == "numeric_unrepresentable"
    asked = asking.questions_for(document, read.columns, settings, [])
    listed = asking.checklist_for(
        document, read.columns, settings, [], asked
    )
    for question in asked + listed:
        for choice in question.choices:
            if choice.answer == asking.ANSWER_MEASUREMENT:
                assert "no average" in choice.publishes, choice.publishes

    # ...and the floor reaches the code promise.
    rare = {
        "g": ["A1"] * 140 + ["B2"] * 140 + ["C3"] * 19 + ["D4"] * 1
    }
    document, read, _settings = _described(rare)
    settings = taxonomy.Settings(small_cell_floor=11)
    document = profile.build_document(read, settings, [], [])
    asked = asking.questions_for(document, read.columns, settings, [])
    listed = asking.checklist_for(
        document, read.columns, settings, [], asked
    )
    for question in asked + listed:
        for choice in question.choices:
            if choice.answer == asking.ANSWER_CODE:
                assert "at least 11 rows share" in choice.publishes
