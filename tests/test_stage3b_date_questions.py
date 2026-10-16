"""THE DATE QUESTIONS' GATE (stage 3b lane R1, plan P4-D381).

Two things the values of a column of dates cannot settle, put to the
person through the questions file and the screen, and answered there
(the owner's ruling of 2026-10-01: "we try to replicate the database
without the imput of the user, but this does not mean that the user
shouldn't be asked!"):

* DAY OR MONTH FIRST, where every cell of a column of dates reads both
  ways. Before, such a column was read month first and nothing was said:
  written day first, its twin parsed 41 to 74 in 100 cells under the
  person's own `%d/%m/%Y` (month starts `01/03/2023` put every date in
  January). The answer `day-first` is `--day-first`.
* A FEW REPEATED CODES IN A COLUMN OF DATES OR TIMES -- `UNK`,
  `00/00/0000`, `0000-00-00`, Caboodle's `-1` and `-2`, `99:99`. Before,
  they kept the column off the date rule's line, it was read as labels or
  numbers, and its twin parsed 0 to 59 in 100; three of them were asked
  whether they were blood pressures. The answer `missing` is
  `--missing-value` naming each code, found again in the table by the run
  that reads the answer, so the questions file names none.

One clause per rule, each beside the mutant it is red on:

* `test_every_day_or_month_column_is_asked_and_answering_repairs_it` and
  `test_every_column_with_codes_is_asked_and_answering_repairs_it` -- each
  battery column is asked, and answered its twin parses whole under the
  person's own format, the codes come back as often as the table wrote
  them, validation misses nothing and nothing is asked again;
* `test_the_clean_spellings_raise_neither_question` -- the thirty-seven
  spellings the reach audit read with no gap raise nothing, but the one
  whose cells read both ways, which raises the day-or-month question and
  stays right on its standing answer;
* `test_the_shapes_left_alone_raise_neither_question` and its five
  mutants, one per rule: a code on fewer than eleven rows (`_DATE_CODES_LINE`),
  codes over a tenth of the column (`_DATE_CODES_SHARE`), more than five
  codes (`_DATE_CODES_MOST`), fewer than three dates left
  (`_DATE_CODES_VARIETY`), and no dates at all
  (`taxonomy.reading_of_the_rest`);
* `test_one_cell_only_one_reading_parses_settles_the_order` -- the
  day-or-month question's own rule, red when that cell is taken out;
* `test_an_answer_names_every_other_column_it_reaches` -- `--missing-value`
  reaches every column, so the question counts the same spellings in the
  others and names each, red when that count is taken out; and the run
  that applies the answer says the words were answered, not typed;
* `test_the_count_elsewhere_is_what_the_declaration_takes_there` -- each
  count is the rise in that column's missing rows once answered, under
  that column's own rule (`-1,0` beside `--decimal-comma`, `-1.0`,
  ` unk `), red on a count by spelling or one blind to the comma; and
  `test_every_question_is_counted_elsewhere_in_one_pass` -- one judgement
  per different spelling of the table, however many columns are asked;
* `test_a_column_with_codes_and_dates_read_either_way_is_asked_both_at_once`
  -- one file, one answering run, the twin read whole, and the line that
  repeats the run names `--day-first` and each code once;
* and the rest: a declaration answers the question, `real-value` keeps
  the reading and stops the question, neither the file nor the screen
  names a code, an answer that finds no codes says so, two answers that
  make one spelling both a value and none are refused, a column asked
  about its codes loses only the questions they answer, a column no code
  can stand in -- every cell read, or every value different -- is not
  counted, and the weighed date rule reads every battery column as the
  classifier does.
"""

import contextlib
import dataclasses
import csv
import io
import json
import pathlib

import pytest

import date_question_shapes as shapes
import fixtures
import workbooks
from synthtwin import asking, cli, profile, reading, taxonomy


def _quiet(argv: "list[str]") -> "tuple[int, str]":
    held = io.StringIO()
    with contextlib.redirect_stdout(held), contextlib.redirect_stderr(held):
        code = cli.main(argv)
    return code, held.getvalue()


def _table(folder: pathlib.Path, values: "list[str]", name: str = "seen_at") -> pathlib.Path:
    folder.mkdir(parents=True, exist_ok=True)
    names, built = fixtures.rows_at_the_floor(name, values)
    table = folder / "real.csv"
    table.write_text(fixtures.rows_to_csv(names, built), encoding="utf-8", newline="")
    return table


def _profiled(folder: pathlib.Path, values: "list[str]", *options: str) -> "tuple[int, str]":
    table = _table(folder, values)
    return _quiet(["profile", str(table), "--out-dir", str(folder), "--replace", *options])


def _questions(folder: pathlib.Path) -> "dict":
    found = json.loads((folder / "real-questions.json").read_text(encoding="utf-8"))
    assert isinstance(found, dict)
    return found


def _block(folder: pathlib.Path) -> "dict":
    document = json.loads((folder / "real-profile.json").read_text(encoding="utf-8"))
    return document["columns"][0]


def _day_or_month_entry(questions: "dict") -> "dict | None":
    for entry in questions["about_your_file"]:
        if entry["column"] == asking.DAY_FIRST_SUBJECT:
            return entry
    return None


def _code_entries(questions: "dict") -> "list[dict]":
    return [
        entry
        for entry in questions["asked"]
        if asking.ANSWER_NO_DATE in [choice["answer"] for choice in entry["answers_you_can_give"]]
    ]


def _answer(folder: pathlib.Path, entry_column: str, answer: str) -> pathlib.Path:
    questions = _questions(folder)
    for section in ("asked", "about_your_file"):
        for entry in questions[section]:
            if entry["column"] == entry_column:
                entry["your_answer"] = answer
    written = folder / "answers.json"
    written.write_text(json.dumps(questions, indent=2), encoding="utf-8", newline="\n")
    return written


def _twin(folder: pathlib.Path) -> "list[str]":
    assert _quiet(["generate", str(folder / "real-profile.json"), "--seed", "0", "--out-dir", str(folder), "--replace"])[0] == 0
    rows = list(csv.reader(io.StringIO((folder / "real-twin.csv").read_text(encoding="utf-8"))))[1:]
    return [row[0] for row in rows if row]


def _validates(folder: pathlib.Path) -> bool:
    return _quiet(["validate", str(folder / "real-profile.json"), "--out-dir", str(folder), "--replace"])[0] == 0


# -- the day-or-month question --------------------------------------------


@pytest.mark.parametrize("name", [shape.name for shape in shapes.DAY_OR_MONTH])
def test_every_day_or_month_column_is_asked_and_answering_repairs_it(
    tmp_path: pathlib.Path, name: str
) -> None:
    """Asked about, month first standing; answered, read the way it is written."""
    shape = shapes.by_name(name)
    values = shapes.cells(shape)
    code, said = _profiled(tmp_path, values)
    assert code == 0
    entry = _day_or_month_entry(_questions(tmp_path))
    assert entry is not None, f"{name} is not asked which comes first"
    assert entry["read_as_now"] == asking.ANSWER_MONTH_FIRST
    assert "'seen_at'" in entry["what_synthtwin_saw"]
    assert "THE ORDER OF THE DAY AND THE MONTH CANNOT BE TOLD" in said
    answers = _answer(tmp_path, asking.DAY_FIRST_SUBJECT, shape.answer)
    code, said = _profiled(tmp_path, values, "--answers", str(answers))
    assert code == 0, said
    block = _block(tmp_path)
    assert block["role"] == "datetime"
    wanted_day_first = shape.answer == asking.ANSWER_DAY_FIRST
    assert ("day-first" in block["format"]) == wanted_day_first, block["format"]
    settings = json.loads((tmp_path / "real-profile.json").read_text(encoding="utf-8"))["settings"]
    assert settings["day_first"] is wanted_day_first
    twin = _twin(tmp_path)
    assert all(shapes.parses(cell, shape.fmt) for cell in twin), name
    assert _validates(tmp_path)
    assert _day_or_month_entry(_questions(tmp_path)) is None, "answered, it is not asked again"
    assert "THE ORDER OF THE DAY AND THE MONTH" not in said, "nor said again on the screen"


def test_month_starts_say_what_each_reading_makes_of_them(tmp_path: pathlib.Path) -> None:
    """`01/03/2023` read month first is every date in one month of the year."""
    _profiled(tmp_path, shapes.cells(shapes.by_name("month_start_dmy")))
    entry = _day_or_month_entry(_questions(tmp_path))
    assert entry is not None
    assert (
        "read month first, every date in 'seen_at' falls in one month of the year, "
        "and read day first, every one falls on one day of a month"
    ) in entry["what_synthtwin_saw"]


def test_one_cell_only_one_reading_parses_settles_the_order(tmp_path: pathlib.Path) -> None:
    """A 25th settles day first, and nothing is asked; without it, the question stands."""
    values = shapes.cells(shapes.by_name("dmy_ambiguous"))
    settled = values[:-1] + ["25/03/2023"]
    _profiled(tmp_path / "settled", settled)
    assert _block(tmp_path / "settled")["format"] == "day-first-date"
    assert _day_or_month_entry(_questions(tmp_path / "settled")) is None
    _profiled(tmp_path / "open", values[:-1] + ["03/03/2023"])
    assert _day_or_month_entry(_questions(tmp_path / "open")) is not None


def test_a_declared_day_first_is_an_answer(tmp_path: pathlib.Path) -> None:
    """`--day-first` typed is the question answered, so it is not put."""
    code, said = _profiled(tmp_path, shapes.cells(shapes.by_name("dmy_ambiguous")), "--day-first")
    assert code == 0
    assert _day_or_month_entry(_questions(tmp_path)) is None
    assert "THE ORDER OF THE DAY AND THE MONTH" not in said


# -- the codes question ------------------------------------------------------


@pytest.mark.parametrize("name", [shape.name for shape in shapes.CODES])
def test_every_column_with_codes_is_asked_and_answering_repairs_it(
    tmp_path: pathlib.Path, name: str
) -> None:
    """Asked, and nothing else about it; answered `missing`, read whole."""
    shape = shapes.by_name(name)
    values = shapes.cells(shape)
    code, said = _profiled(tmp_path, values)
    assert code == 0
    questions = _questions(tmp_path)
    entries = _code_entries(questions)
    assert [entry["column"] for entry in entries] == ["seen_at"], f"{name} is not asked about its codes"
    assert entries[0]["read_as_now"] == asking.ANSWER_KEEP
    assert [entry["column"] for entry in questions["asked"]] == ["seen_at"], (
        "a column asked about its codes is asked nothing else"
    )
    assert "seen_at" not in [entry["column"] for entry in questions["checklist"]["columns"]]
    assert "THESE COLUMNS READ AS DATES OR TIMES BUT FOR A FEW REPEATED SPELLINGS" in said
    # NEITHER THE FILE NOR THE SCREEN NAMES A CODE: the questions file
    # carries no value of the table (A-P4-58), and the screen asks the
    # same question in the same words.
    written = (tmp_path / "real-questions.json").read_text(encoding="utf-8")
    notice = said[said.index("THESE COLUMNS READ AS DATES"):]
    notice = notice[: notice.index("Nothing is wrong with this profile")]
    for one in set(shape.codes):
        assert json.dumps(one) not in written, f"{one} is in the questions file"
        assert one not in notice, f"{one} is on the screen"
    answers = _answer(tmp_path, "seen_at", asking.ANSWER_NO_DATE)
    code, said = _profiled(tmp_path, values, "--answers", str(answers))
    assert code == 0, said
    block = _block(tmp_path)
    assert block["role"] in ("datetime", "time_of_day"), block["role"]
    twin = _twin(tmp_path)
    outside = [cell for cell in twin if cell not in shape.codes]
    assert outside and all(shapes.parses(cell, shape.fmt) for cell in outside), name
    for one in set(shape.codes):
        assert twin.count(one) == values.count(one), f"{one} comes back as often"
    assert _validates(tmp_path)
    assert not _code_entries(_questions(tmp_path)), "answered, it is not asked again"
    assert "--missing-value" in said


def test_a_column_asked_about_its_codes_loses_only_the_questions_they_answer() -> None:
    """The joined and the figures questions give way; a question of another kind stands.

    `00/00/0000` beside dates raises the joined question, which the codes
    question answers in its place. A question about the same column that
    is not about what kind of value it holds -- landing T1 asks which
    clock a column's hours are written on -- is not the codes question's
    to take away, and neither is any question about another column.
    """
    codes = asking.Question("seen_at", "long_tail_labels", asking.BECAUSE_DATE_CODES, "", [], asking.ANSWER_KEEP)
    joined = asking.Question("seen_at", "long_tail_labels", asking.BECAUSE_JOINED, "", [], asking.ANSWER_KEEP)
    padded = asking.Question("seen_at", "count", asking.BECAUSE_PADDED, "", [], asking.ANSWER_MEASUREMENT)
    clock = asking.Question("seen_at", "time_of_day", "another-kind-of-question", "", [], asking.ANSWER_KEEP)
    other = asking.Question("ward", "long_tail_labels", asking.BECAUSE_JOINED, "", [], asking.ANSWER_KEEP)
    kept = asking.without_columns_of([joined, padded, clock, other], [codes])
    assert kept == [clock, other]


def test_one_code_spelled_several_ways_is_one_declaration() -> None:
    """`UNK`, `unk` and `Unk` are one `--missing-value`: their rows add up, under the commonest spelling.

    Red when the commonest is judged against the rows added up so far:
    `Unk` on 14 rows would then lose to the 23 already counted.
    """
    values = [cell for cell in shapes.cells(shapes.by_name("iso_unk")) if cell != "UNK"]
    values = values[:900] + ["UNK"] * 11 + ["unk"] * 12 + ["Unk"] * 14
    seen = asking.date_codes_of(values, taxonomy.Settings())
    assert seen is not None
    assert seen.codes == (("Unk", 37),)
    assert seen.reading == "iso-date" and seen.n_read == 900


def test_real_value_keeps_the_reading_and_stops_the_question(tmp_path: pathlib.Path) -> None:
    """`real-value` is `--keep-value`: the column reads as it did, and is not asked again."""
    values = shapes.cells(shapes.by_name("mdy_unk"))
    _profiled(tmp_path, values)
    before = _block(tmp_path)["role"]
    answers = _answer(tmp_path, "seen_at", asking.ANSWER_REAL_VALUE)
    code, said = _profiled(tmp_path, values, "--answers", str(answers))
    assert code == 0, said
    assert _block(tmp_path)["role"] == before
    settings = json.loads((tmp_path / "real-profile.json").read_text(encoding="utf-8"))["settings"]
    assert settings["kept_values"]["n_declared"] == 1
    assert not _code_entries(_questions(tmp_path))
    assert "--keep-value" in said


def test_an_answer_that_finds_no_codes_says_so(tmp_path: pathlib.Path) -> None:
    """The table changed since the file was written: nothing declared, and said."""
    shape = shapes.by_name("mdy_unk")
    _profiled(tmp_path, shapes.cells(shape))
    answers = _answer(tmp_path, "seen_at", asking.ANSWER_NO_DATE)
    clean = [cell if cell not in shape.codes else "03/17/2023" for cell in shapes.cells(shape)]
    code, said = _profiled(tmp_path, clean, "--answers", str(answers))
    assert code == 0
    assert "no longer sees that column as dates or times beside a few repeated spellings" in said
    assert "TO REPEAT THIS RUN" not in said, "nothing was declared, so nothing is to repeat"


def test_two_answers_making_one_spelling_both_are_refused(tmp_path: pathlib.Path) -> None:
    """`UNK` answered missing in one column and a value in another is one contradiction."""
    first = shapes.cells(shapes.by_name("mdy_unk"))
    second = shapes.cells(shapes.by_name("iso_unk"))
    tmp_path.mkdir(parents=True, exist_ok=True)
    table = tmp_path / "real.csv"
    rows = [[first[place], second[place]] for place in range(len(first))]
    table.write_text(fixtures.rows_to_csv(["first", "second"], rows), encoding="utf-8", newline="")
    assert _quiet(["profile", str(table), "--out-dir", str(tmp_path), "--replace"])[0] == 0
    questions = _questions(tmp_path)
    assert sorted(entry["column"] for entry in _code_entries(questions)) == ["first", "second"]
    for entry in questions["asked"]:
        entry["your_answer"] = (
            asking.ANSWER_NO_DATE if entry["column"] == "first" else asking.ANSWER_REAL_VALUE
        )
    answers = tmp_path / "answers.json"
    answers.write_text(json.dumps(questions), encoding="utf-8", newline="\n")
    code, said = _quiet(["profile", str(table), "--out-dir", str(tmp_path), "--replace", "--answers", str(answers)])
    assert code == 2
    assert "one spelling is both a value and 'no value'" in said


# -- what neither question may reach -------------------------------------------


def _asked_here(
    folder: pathlib.Path, values: "list[str]", floor: int = 11
) -> "tuple[bool, bool]":
    """Whether the codes question and the day-or-month question reach one column."""
    table = _table(folder, values)
    read = reading.read_table(str(table), small_cell_floor=floor)
    settings = taxonomy.Settings(small_cell_floor=floor)
    document = profile.build_document(read, settings, [], [])
    codes = asking.date_code_questions(document, read.columns, settings, [])
    order = asking.day_or_month_columns(document, read.columns, settings)
    return bool(codes), bool(order)


def test_the_clean_spellings_raise_neither_question(tmp_path: pathlib.Path) -> None:
    """Thirty-six raise nothing; the one whose every cell reads both ways is asked which comes first."""
    asked: "list[str]" = []
    for shape in shapes.CLEAN:
        codes, order = _asked_here(tmp_path / shape.name, shapes.cells(shape))
        if codes or (order and shape.name not in shapes.CLEAN_AMBIGUOUS):
            asked += [shape.name]
        if shape.name in shapes.CLEAN_AMBIGUOUS:
            assert order and not codes, shape.name
    assert len(shapes.CLEAN) == 37
    assert not asked, asked


@pytest.mark.parametrize("name", [shape.name for shape in shapes.NOT_ASKED])
def test_the_shapes_left_alone_raise_neither_question(tmp_path: pathlib.Path, name: str) -> None:
    """A code on five rows, a third of the column, six codes, two dates, no dates."""
    assert _asked_here(tmp_path, shapes.cells(shapes.by_name(name))) == (False, False)


def test_the_line_holds_at_a_lowered_floor_and_rises_with_a_raised_one(
    tmp_path: pathlib.Path,
) -> None:
    """Eleven rows a code at a floor of 2, and the floor's own rows at 36."""
    few = shapes.cells(shapes.by_name("iso_unk_few"))
    assert _asked_here(tmp_path / "two", few, floor=2) == (False, False)
    twenty = shapes.cells(shapes.by_name("iso_unk"))
    assert _asked_here(tmp_path / "eleven", twenty)[0]
    assert _asked_here(tmp_path / "thirty-six", twenty, floor=36) == (False, False)


@pytest.mark.parametrize(
    "name, rule, value, floor",
    [
        ("iso_unk_few", "_DATE_CODES_LINE", 2, 2),
        ("iso_unk_third", "_DATE_CODES_SHARE", 1, 11),
        ("iso_six_codes", "_DATE_CODES_MOST", 6, 11),
        ("two_dates_and_unk", "_DATE_CODES_VARIETY", 1, 11),
    ],
)
def test_red_on_each_rule_of_the_codes_question(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
    name: str,
    rule: str,
    value: int,
    floor: int,
) -> None:
    """Each shape left alone is asked once its own rule is moved: the rule is what keeps it out.

    The classifier's own reading, asked since the Codex review of lane
    R1 (item 3), would refuse some of them too -- two dates beside a code
    are two values -- so the witness takes it out of the way as well, and
    the rule alone is what is moved.
    """
    values = shapes.cells(shapes.by_name(name))
    assert not _asked_here(tmp_path / "shipped", values, floor)[0], (name, rule)
    monkeypatch.setattr(asking, "_as_the_classifier_reads", lambda name, values, settings, found, comma, stored: found)
    assert not _asked_here(tmp_path / "unchecked", values, floor)[0], (name, rule)
    monkeypatch.setattr(asking, rule, value)
    assert _asked_here(tmp_path / "moved", values, floor)[0], (name, rule)


def test_red_without_the_date_rule(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A column of notes beside a code is asked once the rest need not read as dates."""

    def anything(counted: "dict[str, int]", settings: taxonomy.Settings, n_rows: int) -> "tuple[str, int]":
        return "iso-date", sum(counted[spelling] for spelling in counted)

    values = shapes.cells(shapes.by_name("notes_with_codes"))
    assert not _asked_here(tmp_path / "shipped", values)[0]
    monkeypatch.setattr(asking, "_as_the_classifier_reads", lambda name, values, settings, found, comma, stored: found)
    assert not _asked_here(tmp_path / "unchecked", values)[0]
    monkeypatch.setattr(taxonomy, "reading_of_the_rest", anything)
    assert _asked_here(tmp_path / "moved", values)[0]


def test_a_column_no_code_can_stand_in_is_not_counted(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Every cell parsed, or every value different: no code can be there, so no cell is counted.

    A column of dates its reading parsed whole has no cell to be a code,
    and a column whose block publishes as many different values as
    cells has no spelling on two rows, let alone eleven -- so neither is
    walked, which is what keeps a table of a million rows and fifty
    columns from paying a dictionary per column for nothing.
    """
    called = {"columns": 0}
    shipped = asking._spellings_counted

    def counting(present: "list[str]") -> "dict[str, int]":
        called["columns"] = called["columns"] + 1
        return shipped(present)

    monkeypatch.setattr(asking, "_spellings_counted", counting)
    _asked_here(tmp_path / "read", shapes.cells(shapes.by_name("ss_date")))
    _asked_here(tmp_path / "different", [f"note number {index}" for index in range(1000)])
    assert called["columns"] == 0
    # ...and the mutant's witness: a column of dates with cells left
    # unread is walked, so the count above is not a counter that never
    # moves.
    _asked_here(tmp_path / "unread", shapes.cells(shapes.by_name("iso_unk_sparse")))
    assert called["columns"] == 1


def test_the_weighed_date_rule_reads_each_column_as_the_classifier_does() -> None:
    """`reading_of_the_rest` over different spellings is `_matching_date_format` over cells."""
    settings = taxonomy.Settings()
    for shape in shapes.CLEAN + shapes.DAY_OR_MONTH:
        values = shapes.cells(shape)
        counted: "dict[str, int]" = {}
        for value in values:
            counted[value] = counted[value] + 1 if value in counted else 1
        weighed = taxonomy.reading_of_the_rest(counted, settings, len(values))
        assert weighed is not None, shape.name
        matched = taxonomy._matching_date_format(values, settings)
        if matched is None:
            assert weighed[0] in ("hh-mm", "hh-mm-ss"), shape.name
            continue
        assert weighed[0] == matched[0], shape.name
        assert weighed[1] == len(matched[1]), shape.name


# -- the review of lane R1 --------------------------------------------------


def _two_columns(folder: pathlib.Path, columns: "dict[str, list[str]]") -> pathlib.Path:
    folder.mkdir(parents=True, exist_ok=True)
    names = list(columns)
    rows = [[columns[name][place] for name in names] for place in range(len(columns[names[0]]))]
    table = folder / "real.csv"
    table.write_text(fixtures.rows_to_csv(names, rows), encoding="utf-8", newline="")
    return table


def _answered_all(folder: pathlib.Path, answers: "dict[str, str]") -> pathlib.Path:
    questions = _questions(folder)
    for section in ("asked", "about_your_file"):
        for entry in questions[section]:
            if entry["column"] in answers:
                entry["your_answer"] = answers[entry["column"]]
    written = folder / "answers.json"
    written.write_text(json.dumps(questions, indent=2), encoding="utf-8", newline="\n")
    return written


def _repeat_line(said: str) -> str:
    """The options under TO REPEAT THIS RUN, as one line."""
    tail = said[said.index("TO REPEAT THIS RUN"):]
    return tail.splitlines()[1].strip()


def _scores(count: int) -> "list[str]":
    """A column of scores of change that holds -1 and -2 legitimately."""
    steps = ["-3", "-2", "-1", "-1", "0", "0", "0", "1", "1", "2", "3"]
    return [steps[(place * 7) % len(steps)] for place in range(count)]


def test_an_answer_names_every_other_column_it_reaches(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`-1` in a DateKey column is a real score elsewhere: the question says where, and how many.

    The review of lane R1, item 1: answered `missing`, a column of scores
    holding -1 and -2 lost 27.6 in 100 of its rows to "missing" and its
    mean moved from -0.032 to +0.477, while the question named neither
    spelling nor column. A third column holding `-1` on three rows is
    named with "some rows", which is the disclosure rule's (a count of
    three is not printed). Red when the count is taken out.
    """
    keys = shapes.cells(shapes.by_name("cab_datekey_sentinels"))
    scores = _scores(len(keys))
    few = ["-1" if place in (5, 50, 500) else f"{place % 40}" for place in range(len(keys))]
    table = _two_columns(tmp_path, {"visit_key": keys, "score_change": scores, "ward": few})
    assert _quiet(["profile", str(table), "--out-dir", str(tmp_path), "--replace"])[0] == 0
    entries = _code_entries(_questions(tmp_path))
    assert [entry["column"] for entry in entries] == ["visit_key"]
    held = scores.count("-1") + scores.count("-2")
    where = f"on {held} rows of 'score_change', on some rows of 'ward'"
    assert where in entries[0]["what_synthtwin_saw"]
    means = {choice["answer"]: choice["then_the_description_publishes"] for choice in entries[0]["answers_you_can_give"]}
    assert f"{where}, which this answer reads as missing there too" in means[asking.ANSWER_NO_DATE]
    assert f"{where}, which this answer keeps as values there too" in means[asking.ANSWER_REAL_VALUE]
    answers = _answer(tmp_path, "visit_key", asking.ANSWER_NO_DATE)
    code, said = _quiet(["profile", str(table), "--out-dir", str(tmp_path), "--replace", "--answers", str(answers)])
    assert code == 0, said
    assert "your answers in the questions file declared missing are written into the description" in said
    assert "you typed after --missing-value" not in said
    # The way back names the answer, not only an option nobody typed.
    assert "or with your answer about the column they were found in changed back to 'keep'" in said
    # ...and the mutant's witness: without the count, nothing names them.
    monkeypatch.setattr(asking, "codes_elsewhere", lambda *arguments: {})
    alone = tmp_path / "uncounted"
    table = _two_columns(alone, {"visit_key": keys, "score_change": scores, "ward": few})
    assert _quiet(["profile", str(table), "--out-dir", str(alone), "--replace"])[0] == 0
    assert "'score_change'" not in json.dumps(_code_entries(_questions(alone)))


def test_a_column_alone_with_its_codes_says_no_other_column_holds_them(tmp_path: pathlib.Path) -> None:
    """Where the answer reaches nothing else, the choice says that instead."""
    _profiled(tmp_path, shapes.cells(shapes.by_name("mdy_unk")))
    entry = _code_entries(_questions(tmp_path))[0]
    for choice in entry["answers_you_can_give"]:
        if choice["answer"] in (asking.ANSWER_NO_DATE, asking.ANSWER_REAL_VALUE):
            assert "no other column of your table holds them" in choice["then_the_description_publishes"]


def _missing_in(folder: pathlib.Path) -> "dict[str, int]":
    document = json.loads((folder / "real-profile.json").read_text(encoding="utf-8"))
    return {block["name"]: block["n_missing"] for block in document["columns"]}


def test_the_count_elsewhere_is_what_the_declaration_takes_there(tmp_path: pathlib.Path) -> None:
    """Each other column's count is the rows the answer then reads as missing, under that column's own rule.

    The second review of lane R1, item 1: a column declared
    `--decimal-comma` writing `-1,0` was said to hold none of a DateKey
    column's codes, and the answer took 112 of its rows. Here that column
    sits beside `-1.0` and `-2.00` in an ordinary column and ` unk `,
    `Unk` and `UNK` beside a column of dates written `UNK`: every count
    the questions file says is the rise in that column's missing rows
    once both columns are answered `missing`. Red when the count asks the
    spelling rather than the declaration, or reads the comma column as an
    ordinary one.
    """
    keys = shapes.cells(shapes.by_name("cab_datekey_sentinels"))
    count = len(keys)
    dated = (shapes.cells(shapes.by_name("iso_unk")) * 2)[:count]
    columns = {
        "visit_key": keys,
        "seen_at": dated,
        "volume": ["-1,0" if place % 9 == 0 else f"{place % 7 + 1},5" for place in range(count)],
        "flt": ["-1.0" if place % 9 == 0 else ("-2.00" if place % 13 == 0 else f"{place % 7}.5") for place in range(count)],
        "colour": [
            [" unk ", "Unk", "UNK"][place % 3] if place % 10 == 0 else ["red", "green", "blue", "grey"][place % 4]
            for place in range(count)
        ],
    }
    expected = {
        "volume": columns["volume"].count("-1,0"),
        "flt": columns["flt"].count("-1.0") + columns["flt"].count("-2.00"),
        "colour": count // 10,
    }
    table = _two_columns(tmp_path, columns)
    comma = ("--decimal-comma", "volume")
    assert _quiet(["profile", str(table), "--out-dir", str(tmp_path), "--replace", *comma])[0] == 0
    before = _missing_in(tmp_path)
    saw = {entry["column"]: entry["what_synthtwin_saw"] for entry in _code_entries(_questions(tmp_path))}
    assert sorted(saw) == ["seen_at", "visit_key"]
    assert f"on {expected['volume']} rows of 'volume', on {expected['flt']} rows of 'flt'" in saw["visit_key"]
    assert "'colour'" not in saw["visit_key"]
    assert f"on {expected['colour']} rows of 'colour'" in saw["seen_at"]
    assert "'volume'" not in saw["seen_at"] and "'flt'" not in saw["seen_at"]
    answers = _answered_all(tmp_path, {"visit_key": asking.ANSWER_NO_DATE, "seen_at": asking.ANSWER_NO_DATE})
    code, said = _quiet(["profile", str(table), "--out-dir", str(tmp_path), "--replace", *comma, "--answers", str(answers)])
    assert code == 0, said
    after = _missing_in(tmp_path)
    for name in expected:
        assert after[name] - before[name] == expected[name], name


def test_a_count_elsewhere_is_said_over_that_column_s_present_cells(tmp_path: pathlib.Path) -> None:
    """Fifteen `unk` among twenty present cells of a sparse column: the count is withheld, as the rule says.

    The second review of lane R1, item 4: the disclosure rule weighs a
    count against the cells that are not missing, and fifteen of twenty
    leaves five, under the line; weighed against the column's thousand
    rows it would have been printed. Red when the count is weighed
    against every row.
    """
    dated = shapes.cells(shapes.by_name("mdy_unk"))
    sparse = [""] * len(dated)
    for place in range(15):
        sparse[place * 50] = "unk"
    for place in range(5):
        sparse[place * 50 + 25] = "red"
    table = _two_columns(tmp_path, {"seen_at": dated, "sparse": sparse})
    assert _quiet(["profile", str(table), "--out-dir", str(tmp_path), "--replace"])[0] == 0
    entry = _code_entries(_questions(tmp_path))[0]
    assert "on some rows of 'sparse'" in entry["what_synthtwin_saw"]
    assert "15 rows" not in entry["what_synthtwin_saw"]


def test_every_question_is_counted_elsewhere_in_one_pass(monkeypatch: pytest.MonkeyPatch) -> None:
    """Six DateKey columns cost one judgement per different spelling of the table, not six.

    The second review of lane R1, item 2: each column asked re-read
    every other one, so thirty DateKey columns at 20,000 rows spent
    16.2 s of a 154 s describe there. Counted here as the judgements of
    what a declaration would match: one pass judges each different
    spelling of each column once (twice for the codes themselves), where
    a pass per question judges each about six times.
    """
    keys = shapes.cells(shapes.by_name("cab_datekey_sentinels"))
    columns = [list(reversed(keys)) if place % 2 else keys[place:] + keys[:place] for place in range(6)]
    different = sum(len(set(column)) for column in columns)
    blocks = [
        {"name": f"key_{place}", "role": taxonomy.ROLE_CONTINUOUS, "n_present": len(keys)}
        for place in range(6)
    ]
    settings = taxonomy.Settings()
    found = asking.date_codes_of(keys, settings)
    assert found is not None
    judged = [0]
    shipped = asking._declared_identity

    def counted(*arguments: object) -> "tuple[str, object]":
        judged[0] = judged[0] + 1
        return shipped(*arguments)  # type: ignore[arg-type]

    monkeypatch.setattr(asking, "_declared_identity", counted)
    reached = asking.codes_elsewhere(
        {"columns": blocks}, columns, [(place, found) for place in range(6)], settings
    )
    assert sorted(reached) == list(range(6))
    for place in range(6):
        assert len(reached[place]) == 5
    assert judged[0] <= different + 4 * len(found.codes) * 6


def _ambiguous_with_codes() -> "list[str]":
    values = shapes.cells(shapes.by_name("dmy_ambiguous"))
    return ["UNK" if place % 33 == 0 else values[place] for place in range(len(values))]


def test_a_column_with_codes_and_dates_read_either_way_is_asked_both_at_once(
    tmp_path: pathlib.Path,
) -> None:
    """One file asks the codes and the order, and one answering run reads the column whole.

    The review of lane R1, items 3x, 3y and 4: before, the questions file
    asked the codes alone, `missing` read the column month first (405 of
    1,000 twin cells under `%d/%m/%Y`), and only the next file asked the
    order. A second column with the same code, answered too, is named
    once on the line that repeats the run.
    """
    first = _ambiguous_with_codes()
    second = shapes.cells(shapes.by_name("iso_unk"))
    table = _two_columns(tmp_path, {"seen_at": first, "other": second})
    assert _quiet(["profile", str(table), "--out-dir", str(tmp_path), "--replace"])[0] == 0
    questions = _questions(tmp_path)
    assert sorted(entry["column"] for entry in _code_entries(questions)) == ["other", "seen_at"]
    order = _day_or_month_entry(questions)
    assert order is not None and "'seen_at'" in order["what_synthtwin_saw"]
    answers = _answered_all(
        tmp_path,
        {
            "seen_at": asking.ANSWER_NO_DATE,
            "other": asking.ANSWER_NO_DATE,
            asking.DAY_FIRST_SUBJECT: asking.ANSWER_DAY_FIRST,
        },
    )
    code, said = _quiet(["profile", str(table), "--out-dir", str(tmp_path), "--replace", "--answers", str(answers)])
    assert code == 0, said
    assert _block(tmp_path)["format"] == "day-first-date"
    assert _repeat_line(said) == "--day-first --missing-value UNK"
    assert _quiet(["generate", str(tmp_path / "real-profile.json"), "--seed", "0", "--out-dir", str(tmp_path), "--replace"])[0] == 0
    rows = list(csv.reader(io.StringIO((tmp_path / "real-twin.csv").read_text(encoding="utf-8"))))[1:]
    twin = [row[0] for row in rows if row and row[0] != "UNK"]
    assert twin and all(shapes.parses(cell, "%d/%m/%Y") for cell in twin)


def test_a_tie_beside_codes_under_day_first_is_read_day_first(tmp_path: pathlib.Path) -> None:
    """`--day-first` decides the tie in the rest of a column with codes, as it does in the classifier."""
    code, _said = _profiled(tmp_path, _ambiguous_with_codes(), "--day-first")
    assert code == 0
    entry = _code_entries(_questions(tmp_path))[0]
    assert "dates written as 17/03/2024 (day first)" in entry["what_synthtwin_saw"]
    assert _day_or_month_entry(_questions(tmp_path)) is None


def test_a_cell_naming_a_zero_field_keeps_the_dotted_pair_out(tmp_path: pathlib.Path) -> None:
    """`01.00.24` is a version number, so dotted two-figure cells beside a code are not dates."""
    values: "list[str]" = []
    for place in range(1000):
        if place % 40 == 0:
            values += ["NA_VER"]
        elif place == 7:
            values += ["01.00.24"]
        else:
            values += [f"{place % 12 + 1:02d}.{place % 11 + 1:02d}.{10 + place % 15}"]
    assert _asked_here(tmp_path, values) == (False, False)


def _as_labels_once_answered(monkeypatch: pytest.MonkeyPatch) -> None:
    """A classifier that reads a clock column as labels once its code is declared missing.

    The classifier before lane C1, as lane R1's reviews measured it: the
    stand-in for the question's mutant, since the question follows
    whatever the answer `missing` reads (lane R2c, plan P4-D383).
    """
    shipped = taxonomy.role_read

    def labels(name: str, values: "list[str]", settings: taxonomy.Settings, *rest: object) -> "tuple[str, str, int, int]":
        found = shipped(name, values, settings, *rest)  # type: ignore[arg-type]
        if settings.declared_missing_values and found[0] == taxonomy.ROLE_CLOCK:
            return taxonomy.ROLE_CATEGORICAL, "", found[2], found[3]
        return found

    monkeypatch.setattr(taxonomy, "role_read", labels)


def test_a_clock_of_few_values_is_not_promised_a_reading_of_times(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Four times beside `99:99` are asked exactly where the answer reads them as times.

    The review of lane R1, item 5: the `missing` choice promised "the
    column read as times of day" and the answer left it categorical. At
    batch 3's integration the question follows the classifier (lane R2c,
    plan P4-D383), and lane C1's classifier reads the four times as times
    of day once the code is out (`taxonomy.role_read`), so the question
    is put and promises what the answer gives. Red the other way: a
    classifier reading them as labels puts no question.
    """
    values = [["08:00", "12:00", "16:00", "20:00"][place % 4] if place % 33 else "99:99" for place in range(1000)]
    answered = dataclasses.replace(taxonomy.Settings(), declared_missing_values=("99:99",))
    assert taxonomy.role_read("seen_at", values, answered, False, "")[0] == taxonomy.ROLE_CLOCK
    assert _asked_here(tmp_path / "shipped", values)[0]
    _as_labels_once_answered(monkeypatch)
    assert not _asked_here(tmp_path / "labels", values)[0]


@pytest.mark.parametrize("different, asked", [(100, True), (101, True)])
def test_a_clock_is_asked_only_past_the_categories_line(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, different: int, asked: bool
) -> None:
    """At a thousand rows, a hundred times and 101 are both read as times once answered, and both asked.

    The second review of lane R1, item 4, measured a hundred different
    times beside `99:99` staying categories once the code was declared
    missing and 101 read as times of day, so the question stood at the
    categories line. At batch 3's integration lane C1's classifier reads
    both as times of day and the question follows it (lane R2c, plan
    P4-D383): the line no longer stands between. Where a classifier reads
    the column as labels the question is not put.
    """
    assert taxonomy.categories_ceiling(1000, taxonomy.Settings()) == 100
    times = [f"{6 + place // 60:02d}:{place % 60:02d}" for place in range(different)]
    values = ["99:99" if place % 33 == 0 else times[place % different] for place in range(1000)]
    assert _asked_here(tmp_path / "shipped", values)[0] is asked
    _as_labels_once_answered(monkeypatch)
    assert not _asked_here(tmp_path / "labels", values)[0]


@pytest.mark.parametrize("name", ["mdy_zero", "iso_zero_date", "clock_9999"])
def test_real_value_brings_no_other_question_back(tmp_path: pathlib.Path, name: str) -> None:
    """Answered `real-value`, the column is asked nothing: not the joined question either.

    The review of lane R1, item 2: the codes kept, the codes question
    was gone, and the blood-pressure question it had stood in front of
    came back.
    """
    values = shapes.cells(shapes.by_name(name))
    _profiled(tmp_path, values)
    answers = _answer(tmp_path, "seen_at", asking.ANSWER_REAL_VALUE)
    code, said = _profiled(tmp_path, values, "--answers", str(answers))
    assert code == 0, said
    questions = _questions(tmp_path)
    for entry in questions["asked"]:
        assert asking.ANSWER_JOINED not in [choice["answer"] for choice in entry["answers_you_can_give"]], name
    assert "seen_at" not in [entry["column"] for entry in questions["checklist"]["columns"]]


def test_a_measurement_answered_real_value_keeps_its_checklist_line(tmp_path: pathlib.Path) -> None:
    """A DateKey column answered `real-value` is read as a number, and owner decision D14 lists it.

    The second review of lane R1, item 3: the column's codes kept, it is
    read as a measurement and its twin parses 569 of 1,000 cells as
    dates, yet the repair had taken it off the one list that reaches a
    column of figures no rule can tell from a quantity.
    """
    values = shapes.cells(shapes.by_name("cab_datekey_sentinels"))
    _profiled(tmp_path, values)
    answers = _answer(tmp_path, "seen_at", asking.ANSWER_REAL_VALUE)
    code, said = _profiled(tmp_path, values, "--answers", str(answers))
    assert code == 0, said
    questions = _questions(tmp_path)
    assert "seen_at" not in [entry["column"] for entry in questions["asked"]]
    listed = {entry["column"]: entry["what_synthtwin_saw"] for entry in questions["checklist"]["columns"]}
    assert "seen_at" in listed
    assert listed["seen_at"].startswith("read as a measurement")
    # ...and the screen's list says it too, worked out before the file's.
    assert "\n  'seen_at' -- read as a measurement" in said


def test_a_word_typed_beside_an_answered_code_says_both_ways(tmp_path: pathlib.Path) -> None:
    """`--missing-value ZZZ` typed and a DateKey column answered `missing`: the notice names both doors.

    The second review of lane R1, item 4: the notice's opening line says
    which way each word arrived, and a run with one of each was never
    checked.
    """
    keys = shapes.cells(shapes.by_name("cab_datekey_sentinels"))
    ward = ["ZZZ" if place % 20 == 0 else ["north", "south", "east"][place % 3] for place in range(len(keys))]
    table = _two_columns(tmp_path, {"visit_key": keys, "ward": ward})
    typed = ("--missing-value", "ZZZ")
    assert _quiet(["profile", str(table), "--out-dir", str(tmp_path), "--replace", *typed])[0] == 0
    answers = _answer(tmp_path, "visit_key", asking.ANSWER_NO_DATE)
    code, said = _quiet(["profile", str(table), "--out-dir", str(tmp_path), "--replace", *typed, "--answers", str(answers)])
    assert code == 0, said
    assert (
        "3 words you typed after --missing-value or your answers in the questions file declared missing "
        "are written into the description"
    ) in said


def test_an_answer_is_the_newer_statement_than_a_typed_keep(tmp_path: pathlib.Path) -> None:
    """`--keep-value UNK` typed, `missing` answered: UNK is declared missing, and nothing is refused."""
    values = shapes.cells(shapes.by_name("mdy_unk"))
    _profiled(tmp_path, values)
    answers = _answer(tmp_path, "seen_at", asking.ANSWER_NO_DATE)
    code, said = _profiled(tmp_path, values, "--keep-value", "UNK", "--answers", str(answers))
    assert code == 0, said
    settings = json.loads((tmp_path / "real-profile.json").read_text(encoding="utf-8"))["settings"]
    assert settings["declared_missing_values"]["n_declared"] == 1
    assert settings["kept_values"]["n_declared"] == 0
    assert _block(tmp_path)["role"] == "datetime"


def test_an_answered_column_the_table_lacks_is_refused(tmp_path: pathlib.Path) -> None:
    """The file names a column this table does not hold: exit 2, and the column named."""
    values = shapes.cells(shapes.by_name("mdy_unk"))
    _profiled(tmp_path, values)
    questions = _questions(tmp_path)
    questions["asked"][0]["column"] = "nowhere"
    questions["asked"][0]["your_answer"] = asking.ANSWER_NO_DATE
    answers = tmp_path / "answers.json"
    answers.write_text(json.dumps(questions), encoding="utf-8", newline="\n")
    code, said = _profiled(tmp_path, values, "--answers", str(answers))
    assert code == 2
    assert "a column called 'nowhere' as a column of dates or times beside a few repeated codes" in said


def test_an_answered_code_that_reads_as_two_numbers_is_refused_beside_a_comma(
    tmp_path: pathlib.Path,
) -> None:
    """`-1,0` is -1 under a decimal comma and another number elsewhere: refused, as when typed."""
    dates = shapes.cells(shapes.by_name("mdy_unk"))
    coded = ["-1,0" if cell == "UNK" else cell for cell in dates]
    volumes = [f"{place % 9 + 1},5" for place in range(len(coded))]
    table = _two_columns(tmp_path, {"seen_at": coded, "volume": volumes})
    assert _quiet(["profile", str(table), "--out-dir", str(tmp_path), "--replace", "--decimal-comma", "volume"])[0] == 0
    answers = _answer(tmp_path, "seen_at", asking.ANSWER_NO_DATE)
    code, said = _quiet(
        ["profile", str(table), "--out-dir", str(tmp_path), "--replace", "--decimal-comma", "volume", "--answers", str(answers)]
    )
    assert code == 2
    assert "You named the value '-1,0' with --missing-value, and you also used --decimal-comma" in said


def _typed_dates_beside(code: str) -> bytes:
    """A workbook column of typed dates beside a code stored as text on every 33rd row."""
    import datetime

    body = [(1, [workbooks.cell("A1", "seen_at", "inlineStr")])]
    for place in range(1000):
        number = 2 + place
        if place % 33 == 0:
            one = workbooks.cell(f"A{number}", code, "inlineStr")
        else:
            day = datetime.date(2021, 1, 1) + datetime.timedelta(days=(place * 37) % 1461)
            one = workbooks.cell(f"A{number}", f"{(day - datetime.date(1899, 12, 30)).days}", "", 1)
        body += [(number, [one])]
    return workbooks.package(
        [
            ("[Content_Types].xml", workbooks._content_types(1, False, False, False)),
            ("_rels/.rels", workbooks._root_rels()),
            ("xl/workbook.xml", workbooks._workbook([("Data", "")])),
            ("xl/_rels/workbook.xml.rels", workbooks._workbook_rels(1, False)),
            ("xl/styles.xml", workbooks._styles()),
            ("xl/worksheets/sheet1.xml", workbooks.sheet(body, dimension="A1:A1001")),
        ]
    )


@pytest.mark.parametrize(
    "code",
    [
        pytest.param(
            "-1",
            marks=pytest.mark.xfail(
                strict=True,
                reason=(
                    "a declared number against a text cell of a typed workbook date column: "
                    "the twin fails its own validation (exit 3), as `--missing-value -1` "
                    "does on 668f276 -- a limit P4-D381 states"
                ),
            ),
        ),
        "UNK",
    ],
)
def test_typed_workbook_dates_beside_a_text_code_answered_missing_validate(
    tmp_path: pathlib.Path, code: str
) -> None:
    """Typed dates beside a text code, answered `missing`: the twin passes its own validation."""
    table = tmp_path / "real.xlsx"
    table.write_bytes(_typed_dates_beside(code))
    assert _quiet(["profile", str(table), "--out-dir", str(tmp_path), "--replace"])[0] == 0
    answers = _answer(tmp_path, "seen_at", asking.ANSWER_NO_DATE)
    code_of, said = _quiet(["profile", str(table), "--out-dir", str(tmp_path), "--replace", "--answers", str(answers)])
    assert code_of == 0, said
    assert _block(tmp_path)["role"] == "datetime"
    generated = ["generate", str(tmp_path / "real-profile.json"), "--seed", "0", "--out-dir", str(tmp_path), "--replace"]
    assert _quiet(generated)[0] == 0
    assert _validates(tmp_path)


# -- the Codex review of lane R1 ----------------------------------------------


def _iso_days(count: int) -> "list[str]":
    """``count`` ISO dates over about two years, every one a real day."""
    import datetime

    first = datetime.date(2023, 1, 2)
    return [(first + datetime.timedelta(days=place % 700)).isoformat() for place in range(count)]


@pytest.mark.parametrize("code", ["$(printf marker)", "NOT RECORDED", "-UNK", "it's", "=echo"])
def test_the_repeat_line_quotes_each_value_for_the_shell(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, code: str
) -> None:
    """A code the table wrote is quoted on the line to type, and that line repeats the run.

    The Codex review of lane R1, item 1: `--missing-value $(printf
    marker)` was printed bare, so a POSIX shell would run it, and `NOT
    RECORDED` became two words and the repeat exited 2. A leading minus
    is joined with `=`, which argparse reads as the option's value. The
    line is split here as a POSIX shell splits it, and the run it names
    declares the same code. Red on the bare line.
    """
    import shlex

    monkeypatch.setattr(cli, "_on_windows", lambda: False, raising=False)
    values = _iso_days(970) + [code] * 30
    table = _table(tmp_path, values)
    _profiled(tmp_path, values)
    answers = _answer(tmp_path, "seen_at", asking.ANSWER_NO_DATE)
    code_of, said = _profiled(tmp_path, values, "--answers", str(answers))
    assert code_of == 0, said
    line = _repeat_line(said)
    words = shlex.split(line)
    if code.startswith("-"):
        assert words == [f"--missing-value={code}"], line
    else:
        assert words == ["--missing-value", code], line
    assert "quoted for a POSIX shell" in said
    again = tmp_path / "again"
    again.mkdir()
    code_of, said = _quiet(["profile", str(table), "--out-dir", str(again), "--replace", *words])
    assert code_of == 0, said
    assert _block(again)["role"] == "datetime"
    assert _block(again)["n_missing"] == 30


def test_a_column_name_with_a_space_is_one_word_on_the_repeat_line(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`--twelve-hour Visit time` was two words; quoted, it names the column."""
    import shlex

    monkeypatch.setattr(cli, "_on_windows", lambda: False, raising=False)
    dated = _iso_days(970) + ["UNK"] * 30
    clocks = [f"{1 + place % 12}:{place % 60:02d}" for place in range(1000)]
    table = _two_columns(tmp_path, {"seen_at": dated, "Visit time": clocks})
    typed = ("--twelve-hour", "Visit time")
    assert _quiet(["profile", str(table), "--out-dir", str(tmp_path), "--replace", *typed])[0] == 0
    answers = _answer(tmp_path, "seen_at", asking.ANSWER_NO_DATE)
    code, said = _quiet(["profile", str(table), "--out-dir", str(tmp_path), "--replace", *typed, "--answers", str(answers)])
    assert code == 0, said
    words = shlex.split(_repeat_line(said))
    assert words == ["--twelve-hour", "Visit time", "--missing-value", "UNK"], words


def test_the_line_to_type_is_quoted_for_both_windows_shells_on_windows() -> None:
    """On Windows each value is in double quotes, which the Command Prompt and PowerShell both read.

    Lane CF4b (plan P4-D397): PowerShell's single quotes, written here
    before, are text to the Command Prompt, where the install script
    tells the person to type. A `$` PowerShell would expand is written
    after its backtick; a single quote is text inside double quotes.
    """
    assert cli._quoted_for_the_shell("seen_at", windows=True) == "seen_at"
    assert cli._quoted_for_the_shell("C:\\data\\real.csv", windows=True) == "C:\\data\\real.csv"
    assert cli._quoted_for_the_shell("C:\\RUNNER~1\\real.csv", windows=True) == "C:\\RUNNER~1\\real.csv"
    assert cli._quoted_for_the_shell("~/real.csv", windows=False) == "'~/real.csv'"
    assert cli._quoted_for_the_shell("$(printf marker)", windows=True) == '"`$(printf marker)"'
    assert cli._quoted_for_the_shell("it's", windows=True) == '"it\'s"'
    assert cli._quoted_for_the_shell("it\u2019s", windows=True) == '"it\u2019s"'
    assert cli._quoted_for_the_shell("a,b", windows=True) == '"a,b"'
    assert cli._typed_option("--missing-value", "-NOT KNOWN", windows=True) == '"--missing-value=-NOT KNOWN"'
    assert cli._typed_option("--missing-value", "NOT RECORDED", windows=False) == "--missing-value 'NOT RECORDED'"
    assert cli._typed_option("--code", "dose", windows=False) == "--code dose"
    assert cli._typed_path("-out/real-profile.json", windows=False).startswith("./-out")


def test_a_tilde_and_a_leading_minus_are_quoted_where_a_shell_reads_them() -> None:
    """bash reads `a=~` as a home folder, and Windows PowerShell splits `-a.b` at its point.

    Measured with bash 3.2: `printf '%s' a=~ a=x:~` prints the home folder
    after the `=` and after the `:`, so a code written `a=~` printed bare
    was declared as another; zsh leaves both alone. And Windows
    PowerShell hands a program the bare word `--missing-value=-1.5` as
    two words, split before the point. So on POSIX a word holding `~`
    anywhere is quoted, and on PowerShell a word starting with `-` is.
    Red on the first repair of this review, which printed all of them
    bare.
    """
    for word in ("a=~", "a=x:~", "N=~", "x~y"):
        assert cli._quoted_for_the_shell(word, windows=False) == f"'{word}'"
    assert cli._quoted_for_the_shell("RUNNER~1", windows=True) == "RUNNER~1"
    assert cli._typed_option("--missing-value", "-1.5", windows=False) == "--missing-value=-1.5"
    assert cli._typed_option("--missing-value", "-1.5", windows=True) == '"--missing-value=-1.5"'
    assert cli._typed_option("--missing-value", "-UNK", windows=True) == '"--missing-value=-UNK"'


def _read_by_the_c_runtime(built: str) -> "list[str]":
    """The words a program reads from its command line by the C runtime's rule.

    Backslashes are text unless a `"` follows, where each pair is one
    backslash and an odd one makes the `"` text; inside quotes `""` is
    one `"` and the quotes go on; any other `"` opens or closes them.
    """
    read: "list[str]" = []
    word, quoted, started, place = "", False, False, 0
    while place < len(built):
        slashes = 0
        while place < len(built) and built[place] == "\\":
            slashes, place = slashes + 1, place + 1
        if place < len(built) and built[place] == '"':
            word += "\\" * (slashes // 2)
            if slashes % 2:
                word += '"'
            elif quoted and built[place + 1 : place + 2] == '"':
                word, place = word + '"', place + 1
            else:
                quoted = not quoted
            started, place = True, place + 1
            continue
        word += "\\" * slashes
        if slashes:
            started = True
        if place >= len(built):
            break
        if built[place] == " " and not quoted:
            if started:
                read, word, started = read + [word], "", False
        else:
            word, started = word + built[place], True
        place += 1
    if started:
        read += [word]
    return read


def _handed_over_by_the_command_prompt(line: str) -> "list[str]":
    """The words a program receives from a line the Command Prompt runs.

    The Command Prompt opens or closes its quotes at every `"`, reads
    `&`, `|`, `<`, `>`, `(`, `)` and `%` outside them as its own -- none
    may stand there -- and hands the program the line, which it reads
    by the C runtime's rule.
    """
    quoted = False
    for character in line:
        if character == '"':
            quoted = not quoted
        assert quoted or character not in "&|<>()%^", line
    return _read_by_the_c_runtime(line)


def _read_by_powershell(line: str) -> "list[str]":
    """The strings PowerShell reads from a line of bare and double-quoted words.

    Inside double quotes a backtick makes the character after it text
    and `""` is one `"`; a `$` before a letter, a digit or one of
    `_{(?^$:` would be expanded, which is refused.
    """
    words: "list[str]" = []
    place = 0
    while place < len(line):
        if line[place] == " ":
            place += 1
            continue
        word = ""
        if line[place] == '"':
            place += 1
            while True:
                if line[place] == "`":
                    word, place = word + line[place + 1], place + 2
                elif line[place : place + 2] == '""':
                    word, place = word + '"', place + 2
                elif line[place] == '"':
                    place += 1
                    break
                else:
                    following = line[place + 1 : place + 2]
                    assert not (line[place] == "$" and following and (following.isalnum() or following in "_{(?^$:")), line
                    word, place = word + line[place], place + 1
        else:
            while place < len(line) and line[place] != " ":
                word, place = word + line[place], place + 1
        words += [word]
    return words


def _handed_over_by_windows_powershell(words: "list[str]") -> "list[str]":
    """The words a program receives from Windows PowerShell 5.1, given what it read.

    It builds the program's command line from them, wrapping a word in
    double quotes only where white space stands outside a run its own
    `"` open -- any character .NET's `Char.IsWhiteSpace` names, the
    no-break space among them, which `str.isspace` names too; a `"`
    after a backslash opens no run -- and leaving every `"` inside as it
    is (`NeedQuotes` of its native command binder). The program reads
    that line by the C runtime's rule.
    """

    def wrapped(word: str) -> str:
        quotes, after_slash = 0, False
        for character in word:
            if character == '"' and not after_slash:
                quotes += 1
            elif character.isspace() and quotes % 2 == 0:
                return f'"{word}"'
            after_slash = character == "\\"
        return word

    return _read_by_the_c_runtime(" ".join(wrapped(word) for word in words))


@pytest.mark.parametrize(
    "value",
    [
        'UNK"',
        'a" b',
        'say "no" twice',
        'x" --code "y',
        'a\\"b',
        "a b\\",
        "C:\\my data\\real.csv",
        "a\u00a0b\\",
        "Visit\u3000time\\",
        "x\u2003\\\\",
        "a & b",
        "50% (of 7)",
    ],
)
def test_a_double_quote_reaches_the_program_whole_from_the_command_prompt(value: str) -> None:
    """`UNK"` typed into the Command Prompt stays `UNK"`, and the option after it stays an option.

    Lane CF4b (plan P4-D397): the line is written in double quotes, for
    the Command Prompt and PowerShell both. A `"` inside is written
    `""`, which keeps the Command Prompt inside its quotes and which the
    C runtime reads as one `"`; the backslashes before a `"` or at the
    end are doubled. Nothing stands outside the quotes for the Command
    Prompt to run.

    PowerShell reads the same line, nothing expanded. Windows PowerShell
    5.1 then wraps a value holding white space -- every character .NET
    counts as white space (the verification of the repairs of the Codex
    review of lane R1, its open item 2) -- and the program reads it
    whole; a value holding `"` it hands over with that quote bare, which
    the program reads as a quote of its own: P4-D397's stated limit,
    pinned here, where the Codex review of lane R1, item 1, had it
    whole from PowerShell's single quotes, which the Command Prompt does
    not read. PowerShell 7.3 and later hand over what they read, which
    is the value where no backslash comes before a quote or ends it. On
    a POSIX shell nothing changes.
    """
    import shlex

    line = f"{cli._typed_option('--missing-value', value, windows=True)} --code dose"
    expected = ["--missing-value", value, "--code", "dose"]
    assert _handed_over_by_the_command_prompt(line) == expected, line
    powershell = _read_by_powershell(line)
    if '"' not in value:
        assert _handed_over_by_windows_powershell(powershell) == expected, line
    else:
        assert _handed_over_by_windows_powershell(powershell) != expected, line
    if "\\" not in value:
        assert powershell == expected, line
    posix = f"{cli._typed_option('--missing-value', value, windows=False)} --code dose"
    assert shlex.split(posix) == expected, posix


def test_every_line_to_type_says_its_shell_where_it_quotes_a_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The options a notice offers and the `validate` line are quoted, and then say for which shell.

    The Codex review of lane R1, item 1: the value placed in a line the
    person is told to type is quoted for the shell -- the column `Visit
    time` offered after `--identifier` was two words, and a path with a
    space after `synthtwin validate` the same -- and a line that quotes
    one says which shell it was written for, since PowerShell's quotes
    are not the command prompt's. A line of plain words is unchanged.
    Red on 110cb46, which printed both bare.
    """
    import shlex

    monkeypatch.setattr(cli, "_on_windows", lambda: False, raising=False)
    spaced = asking.Question("Visit time", "long_tail_labels", asking.BECAUSE_REPEATS_AND_MANY, "a shape", [], "")
    notice = cli._assumptions_notice([spaced])
    offered = notice.splitlines()[notice.splitlines().index("If any of them names people, run the command again naming them:") + 1]
    assert shlex.split(offered) == ["--identifier", "Visit time"], offered
    assert "(each value quoted for a POSIX shell such as bash or zsh)" in notice
    plain = asking.Question("visit_time", "long_tail_labels", asking.BECAUSE_REPEATS_AND_MANY, "a shape", [], "")
    assert "each value quoted" not in cli._assumptions_notice([plain])
    twin = pathlib.Path("my data") / "real-twin.csv"
    taught = cli._teaching_validate("my data/real-profile.json", twin)
    line = taught.splitlines()[2]
    assert shlex.split(line) == ["synthtwin", "validate", "my data/real-profile.json", "--twin", str(twin)], line
    assert "(each value quoted for a POSIX shell such as bash or zsh)" in taught
    assert "each value quoted" not in cli._teaching_validate("real-profile.json", pathlib.Path("real-twin.csv"))


def test_the_refusal_of_a_column_too_wide_puts_no_name_inside_the_option() -> None:
    """A column's name stood inside `'--identifier NAME'`, where a quote in it ended the quotes.

    The Codex review of lane R1, item 1, at the one other line that told
    a person what to type with a value of the table in it: the
    generator's refusal of a column whose width cannot hold its values.
    That module cannot know the shell, so the option is named and the
    column is named in the sentence before it, not inside the option.
    Red on 110cb46, whose line held `'--identifier x'$(touch y)''`.
    """
    from synthtwin import generation

    name = "x'$(touch y)'"
    said = generation._domain_too_small(name, "one character long", 200, 95)
    assert f"--identifier {name}" not in said
    assert "with --identifier followed by this column's name" in said
    assert f"The description of the column '{name}'" in said


def _asked_and_answered(
    folder: pathlib.Path, values: "list[str]", *options: str
) -> "tuple[dict | None, dict]":
    """The codes entry the file asks of `seen_at`, and its block once answered `missing` (or as it stands)."""
    _profiled(folder, values, *options)
    entries = _code_entries(_questions(folder))
    if not entries:
        return None, _block(folder)
    answers = _answer(folder, "seen_at", asking.ANSWER_NO_DATE)
    code, said = _profiled(folder, values, *options, "--answers", str(answers))
    assert code == 0, said
    return entries[0], _block(folder)


def test_the_count_a_code_is_said_on_is_every_cell_its_answer_takes(tmp_path: pathlib.Path) -> None:
    """Twenty `UNK` and five `unk` are one code on 25 rows, which is what `missing` takes.

    The Codex review of lane R1, item 2: the question said 20 rows and the
    answer took 25, because a spelling under the line that the same
    declaration matches was left out of the count. Red on 110cb46.
    """
    entry, block = _asked_and_answered(tmp_path, _iso_days(975) + ["UNK"] * 20 + ["unk"] * 5)
    assert entry is not None
    assert "on 25 rows" in entry["what_synthtwin_saw"], entry["what_synthtwin_saw"]
    assert block["role"] == "datetime"
    assert block["n_missing"] == 25


def test_a_code_whose_declaration_takes_real_dates_is_not_asked(tmp_path: pathlib.Path) -> None:
    """`20,230,101` is the number 20230101, which a declaration also takes from `20230101`, a real day.

    The Codex review of lane R1, item 2: 900 compact dates, 80 cells of
    `20230101` and 20 of `20,230,101` were asked about a code on 20 rows,
    and the answer `missing` took 100 rows, the 80 real first days of
    January with them. A declaration that would take a cell some date
    reading reads is no code, so nothing is asked. Red on 110cb46.
    """
    import datetime

    first = datetime.date(2023, 1, 2)
    compact = [(first + datetime.timedelta(days=place % 300)).strftime("%Y%m%d") for place in range(900)]
    values = compact + ["20230101"] * 80 + ["20,230,101"] * 20
    entry, block = _asked_and_answered(tmp_path, values)
    assert entry is None, entry["what_synthtwin_saw"] if entry else ""
    assert block["n_missing"] == 0


@pytest.mark.parametrize(
    "case",
    ["two_clock_faces", "one_date_three_spellings", "stamps_half_marked"],
)
def test_a_question_is_put_only_where_the_classifier_gives_the_reading_it_promises(
    tmp_path: pathlib.Path, case: str
) -> None:
    """Where the answer would not give dates or times, the question that promises them is not put.

    The Codex review of lane R1, item 3, and of landing T1, item 5: slashed
    stamps half on the 24-hour face and half marked AM leave half their
    cells unread under T1's one face; `17 Mar 2024` in three cases is one
    value, `constant` by rule 3 before the date rule is asked; and stamps
    marked on every other row are read on one face. Each was promised
    dates, and each answered column was labels or text. Red on 110cb46.
    """
    if case == "two_clock_faces":
        plain = [f"3/{1 + place // 20}/2023 {13 + place % 10}:{place % 60:02d}" for place in range(475)]
        marked = [f"3/{1 + place // 20}/2023 {1 + place % 10}:{place % 60:02d} AM" for place in range(475)]
        values = plain + marked + ["UNK"] * 50
    elif case == "one_date_three_spellings":
        values = ["17 Mar 2024"] * 324 + ["17 MAR 2024"] * 323 + ["17 mar 2024"] * 323 + ["UNK"] * 30
    else:
        values = [
            f"3/{1 + place // 20}/2023 {1 + place % 10}:{place % 60:02d}" + (" AM" if place % 2 else "")
            for place in range(300)
        ] + ["UNK"] * 15
    entry, block = _asked_and_answered(tmp_path, values)
    assert entry is None, (case, block["role"])


@pytest.mark.parametrize("marker, declared", [("", False), (" AM", False), ("", True)])
def test_t1_clocks_beside_a_code_are_asked_and_read_as_times(
    tmp_path: pathlib.Path, marker: str, declared: bool
) -> None:
    """`9:30`, `9:30 AM` and a declared 12-hour clock beside `UNK`: asked, and answered they are times of day.

    The Codex review of lane R1, item 4, and of landing T1, item 4: the
    question read only `HH:MM` and `HH:MM:SS`, so 970 clocks spanning
    `1:00` to `9:59` beside thirty `UNK`, with or without a marker, were
    never asked, though declaring `UNK` missing reads them as times of
    day. The example the question gives is written in the column's own
    form. Red on 110cb46.
    """
    clocks = [f"{hour}:{minute:02d}{marker}" for hour in range(1, 10) for minute in range(60)]
    values = [clocks[place % len(clocks)] for place in range(970)] + ["UNK"] * 30
    options = ("--twelve-hour", "seen_at") if declared else ()
    entry, block = _asked_and_answered(tmp_path, values, *options)
    assert entry is not None
    assert "970 of the 1000 values read as times of day written as " in entry["what_synthtwin_saw"]
    if marker:
        assert "written as 2:05 PM" in entry["what_synthtwin_saw"]
    assert block["role"] == "time_of_day"
    assert block["n_missing"] == 30


def test_a_few_cells_that_are_neither_are_said(tmp_path: pathlib.Path) -> None:
    """975 dates, 20 `UNK` and five `ODD`: the five are said, as "a few", and not called codes.

    The Codex review of lane R1, item 6: "every other value is one
    spelling" was false where the date rule's line left room for cells
    that read as neither, and the answer left them unread. Their count
    is under the floor, so it is not printed. Red on 110cb46.
    """
    entry, block = _asked_and_answered(tmp_path, _iso_days(975) + ["UNK"] * 20 + ["ODD"] * 5)
    assert entry is not None
    saw = entry["what_synthtwin_saw"]
    assert "every other value but a few of them is one spelling" in saw, saw
    assert "stay unread whatever the answer" in saw
    assert " 5 " not in saw
    means = {choice["answer"]: choice["then_the_description_publishes"] for choice in entry["answers_you_can_give"]}
    assert "the few cells that read as neither counted unread" in means[asking.ANSWER_NO_DATE]
    assert block["n_missing"] == 20
    assert block["n_unparsed"] == 5


@pytest.mark.parametrize(
    "dates, codes, odd, read, said",
    [(950, 20, 0, "980 of the 1000 values", ""), (1930, 25, 15, "1960 of the 2000 values", "15")],
    ids=["stand_ins_alone", "stand_ins_beside_fifteen_unread"],
)
def test_stand_in_dates_the_classifier_sets_aside_are_read_and_never_said_unread(
    tmp_path: pathlib.Path, dates: int, codes: int, odd: int, read: str, said: str
) -> None:
    """Thirty `1900-01-01` beside ISO dates and `UNK` read as dates, and the cells said unread are the answer's own.

    The verification of the repairs of the Codex review of lane R1, its
    open item 1: the classifier sets a stand-in date aside, so it was
    counted with the cells that read as neither -- 950 dates, thirty
    `1900-01-01` and twenty `UNK` were said to be "950 of the 1000"
    dates, with "every other value but 30 of them" the code and those 30
    left to "stay unread whatever the answer", while `missing` left none
    unread and counted the thirty missing by their spelling. Beside
    fifteen cells that read as nothing, 45 were said where the answer
    leaves 15. The cells said unread are those the answer leaves unread.
    Red on 27c604b, which says "but 30 of them" and "but 45 of them";
    110cb46 said 980.
    """
    values = _iso_days(dates) + ["1900-01-01"] * 30 + ["UNK"] * codes + [f"junk{place}" for place in range(odd)]
    entry, block = _asked_and_answered(tmp_path, values)
    assert entry is not None
    saw = entry["what_synthtwin_saw"]
    means = {choice["answer"]: choice["then_the_description_publishes"] for choice in entry["answers_you_can_give"]}
    assert f"{read} read as dates" in saw, saw
    if said:
        assert f"every other value but {said} of them is one spelling" in saw, saw
        assert f"the {said} cells that read as neither counted unread" in means[asking.ANSWER_NO_DATE]
    else:
        assert "every other value is one spelling" in saw, saw
        assert "stay unread" not in saw and "counted unread" not in means[asking.ANSWER_NO_DATE], saw
    assert block["role"] == "datetime"
    assert block["n_unparsed"] == odd
    assert block["missing_by_source"] == {"1900-01-01": 30, "UNK": codes}


def test_real_value_answered_beside_a_typed_missing_value_keeps_every_code(tmp_path: pathlib.Path) -> None:
    """`--missing-value UNK` typed, `real-value` answered about `UNK` and `PENDING`: both are kept.

    The Codex review of lane R1, item 5: the run found the codes again
    under the typed declaration, so `UNK` was already gone, `PENDING`
    alone was kept, and the thirty `UNK` cells stayed missing without a
    word. Red on 110cb46.
    """
    values = _iso_days(940) + ["UNK"] * 30 + ["PENDING"] * 30
    _profiled(tmp_path, values)
    entry = _code_entries(_questions(tmp_path))[0]
    assert "2 spellings" in entry["what_synthtwin_saw"]
    answers = _answer(tmp_path, "seen_at", asking.ANSWER_REAL_VALUE)
    code, said = _profiled(tmp_path, values, "--missing-value", "UNK", "--answers", str(answers))
    assert code == 0, said
    settings = json.loads((tmp_path / "real-profile.json").read_text(encoding="utf-8"))["settings"]
    assert settings["kept_values"]["n_declared"] == 2
    assert settings["declared_missing_values"]["n_declared"] == 0
    assert _block(tmp_path)["n_missing"] == 0


@pytest.mark.parametrize(
    "answer, typed, values, n_missing, n_kept, n_declared_missing",
    [
        # `XX` under the line, typed missing on both runs: the answer
        # `missing` reads the column as dates.
        (asking.ANSWER_NO_DATE, ("--missing-value", "XX"), ["UNK"] * 30 + ["XX"] * 10, 40, 0, 2),
        # `NOTE` on the line, typed missing on both runs: `real-value`
        # about `UNK` keeps `UNK` and leaves the twenty `NOTE` missing.
        (asking.ANSWER_REAL_VALUE, ("--missing-value", "NOTE"), ["UNK"] * 30 + ["NOTE"] * 20, 20, 1, 1),
        # `NOTE` typed kept on both runs: `missing` about `UNK` takes
        # `UNK` alone and `NOTE` stays a value.
        (asking.ANSWER_NO_DATE, ("--keep-value", "NOTE"), ["UNK"] * 30 + ["NOTE"] * 12, 30, 1, 1),
    ],
)
def test_a_word_typed_on_both_runs_that_the_question_never_counted_stays_as_typed(
    tmp_path: pathlib.Path,
    answer: str,
    typed: "tuple[str, str]",
    values: "list[str]",
    n_missing: int,
    n_kept: int,
    n_declared_missing: int,
) -> None:
    """A word typed on the run that asked and on the run that answers is not the answer's to take.

    The regression the first repair of the Codex review of lane R1, item
    5, brought: it found the codes again under NO typed declaration, so
    a word typed on both runs -- which the question, worked out under it,
    never counted -- was taken by the answer as well. `XX` typed missing
    came back among the dates, the column read as labels and the answer
    declared nothing; `NOTE` typed missing was kept by `real-value`;
    `NOTE` typed kept was declared missing. The question's own words say
    which codes it counted, and the codes found under the typed
    declarations are those. Red on 622e810; the third is red on 110cb46
    as well, which counted a typed `--keep-value` into the answer.
    """
    dates = _iso_days(1200 if typed[0] == "--keep-value" else 1000 - len(values))
    cells = dates + values
    _profiled(tmp_path, cells, *typed)
    entries = _code_entries(_questions(tmp_path))
    assert entries and "one spelling" in entries[0]["what_synthtwin_saw"], entries
    answers = _answer(tmp_path, "seen_at", answer)
    code, said = _profiled(tmp_path, cells, *typed, "--answers", str(answers))
    assert code == 0, said
    assert "declared nothing" not in said
    assert "did not reach" not in said
    assert "take these out" not in said
    settings = json.loads((tmp_path / "real-profile.json").read_text(encoding="utf-8"))["settings"]
    assert settings["kept_values"]["n_declared"] == n_kept
    assert settings["declared_missing_values"]["n_declared"] == n_declared_missing
    assert _block(tmp_path)["n_missing"] == n_missing
    if answer == asking.ANSWER_NO_DATE:
        assert _block(tmp_path)["role"] == "datetime"


def test_an_answer_whose_codes_moved_leaves_the_typed_word_and_says_so(tmp_path: pathlib.Path) -> None:
    """The table changed since the questions file: the typed `--missing-value UNK` stands, and the run says so.

    The Codex review of lane R1, item 5: an answer that did not reach a
    typed word stayed silent. Where neither reading of the codes is the
    one the question described -- here the table gained ten `PENDING`
    rows -- synthtwin cannot tell whether the answer was about `UNK`, so
    the typed word stands and the run says the answer did not reach it.
    Red on 622e810, which kept `UNK` without a word, and on 110cb46.
    """
    _profiled(tmp_path, _iso_days(940) + ["UNK"] * 30 + ["PENDING"] * 30)
    answers = _answer(tmp_path, "seen_at", asking.ANSWER_REAL_VALUE)
    later = _iso_days(930) + ["UNK"] * 30 + ["PENDING"] * 40
    code, said = _profiled(tmp_path, later, "--missing-value", "UNK", "--answers", str(answers))
    assert code == 0, said
    assert (
        "about the codes in the column 'seen_at' did not reach a word you typed after --missing-value"
    ) in said
    settings = json.loads((tmp_path / "real-profile.json").read_text(encoding="utf-8"))["settings"]
    assert settings["kept_values"]["n_declared"] == 1
    assert settings["declared_missing_values"]["n_declared"] == 1
    assert _block(tmp_path)["n_missing"] == 30


def test_the_repeat_line_says_which_typed_option_an_answer_replaced(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`--keep-value UNK` typed and `missing` answered: the line says to take the typed option out.

    The Codex review of lane R1, item 7: the line said only to add
    `--missing-value UNK`, and the command with both exits 2. Followed as
    written -- the typed options less those taken out, with those added
    -- the run declares what the answered one did. Red on 110cb46.
    """
    import shlex

    monkeypatch.setattr(cli, "_on_windows", lambda: False, raising=False)
    values = _iso_days(970) + ["UNK"] * 30
    table = _table(tmp_path, values)
    _profiled(tmp_path, values)
    answers = _answer(tmp_path, "seen_at", asking.ANSWER_NO_DATE)
    code, said = _profiled(tmp_path, values, "--keep-value", "UNK", "--answers", str(answers))
    assert code == 0, said
    lines = said[said.index("TO REPEAT THIS RUN"):].splitlines()
    assert shlex.split(lines[1]) == ["--missing-value", "UNK"]
    assert lines[2].startswith("and take these out of the command you typed")
    assert shlex.split(lines[3]) == ["--keep-value", "UNK"]
    again = tmp_path / "again"
    again.mkdir()
    code, said = _quiet(["profile", str(table), "--out-dir", str(again), "--replace", *shlex.split(lines[1])])
    assert code == 0, said
    assert _block(again)["n_missing"] == 30


def test_one_column_answered_both_ways_is_refused(tmp_path: pathlib.Path) -> None:
    """Two entries for one column, `missing` and `real-value`: refused, and nothing written.

    The Codex review of lane R1, item 8: both answers were read, and the
    column was read under `missing` alone without a word. Red on 110cb46.
    """
    values = _iso_days(970) + ["UNK"] * 30
    _profiled(tmp_path, values)
    questions = _questions(tmp_path)
    entry = _code_entries(questions)[0]
    second = json.loads(json.dumps(entry))
    entry["your_answer"] = asking.ANSWER_NO_DATE
    second["your_answer"] = asking.ANSWER_REAL_VALUE
    questions["asked"] += [second]
    answers = tmp_path / "answers.json"
    answers.write_text(json.dumps(questions), encoding="utf-8", newline="\n")
    (tmp_path / "real-profile.json").unlink()
    code, said = _profiled(tmp_path, values, "--answers", str(answers))
    assert code == 2
    assert "one entry answers 'missing' and another answers 'real-value'" in said
    assert not (tmp_path / "real-profile.json").exists()


class _CountedList(list):  # type: ignore[type-arg]
    """A list that counts how often it is walked whole, or searched."""

    walks = 0

    def __iter__(self):  # type: ignore[no-untyped-def]
        _CountedList.walks += 1
        return super().__iter__()

    def __contains__(self, item: object) -> bool:
        _CountedList.walks += 1
        return super().__contains__(item)

    def __getitem__(self, index):  # type: ignore[no-untyped-def]
        _CountedList.walks += 1
        return super().__getitem__(index)


def test_codes_elsewhere_grows_with_the_columns_not_their_square() -> None:
    """Forty columns, each with a code of its own that no other holds: about one look per column.

    The Codex review of lane R1, item 9: each column walked every
    question, so C columns cost C * C comparisons for an empty answer.
    Counted here as the reads of the list of asked columns. Red on
    110cb46, where forty columns read it about 1,600 times.
    """
    count = 40
    columns: "list[list[str]]" = []
    asked: "list[tuple[int, asking.DateCodes]]" = []
    for place in range(count):
        code = f"C{place}X"
        columns += [_iso_days(99)[place:] + _iso_days(place) + [code] * 11]
        asked += [(place, asking.DateCodes("iso-date", ((code, 11),), 99, 110))]
    blocks = [{"name": f"c{place}", "role": "long_tail_labels", "n_present": 110} for place in range(count)]
    counted = _CountedList(asked)
    _CountedList.walks = 0
    reached = asking.codes_elsewhere({"columns": blocks}, columns, counted, taxonomy.Settings())
    assert reached == {}
    assert _CountedList.walks <= 4 * count, _CountedList.walks


def test_the_day_or_month_question_takes_coded_columns_by_name_once() -> None:
    """The coded columns are looked up by name, not walked once per column of the table."""
    count = 40
    blocks = [{"name": f"c{place}", "role": "long_tail_labels"} for place in range(count)]
    also = _CountedList(
        [asking.DayOrMonth(f"c{place}", True, False) for place in range(0, count, 2)]
    )
    _CountedList.walks = 0
    found = asking.day_or_month_columns({"columns": blocks}, [[] for _ in range(count)], taxonomy.Settings(), None, tuple(also))
    assert [one.name for one in found] == [f"c{place}" for place in range(0, count, 2)]
    _CountedList.walks = 0
    found = asking.day_or_month_columns({"columns": blocks}, [[] for _ in range(count)], taxonomy.Settings(), None, also)  # type: ignore[arg-type]
    assert _CountedList.walks <= 2, _CountedList.walks


def test_answered_columns_are_found_by_name_once(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Thirty answered columns cost the names list no more walks than five.

    The Codex review of lane R1, item 9: each answered column walked the
    table's names to find itself, and searched them once more to check
    it was there. Red on 110cb46, where 25 more answers walk them 50
    more times.
    """
    count = 40
    columns = {f"c{place}": [f"{(row * (place + 3)) % 97}" for row in range(120)] for place in range(count)}
    table = _two_columns(tmp_path, columns)
    shipped = reading.read_table

    def counting(*arguments: object, **options: object) -> object:
        read = shipped(*arguments, **options)  # type: ignore[arg-type]
        return dataclasses.replace(read, column_names=_CountedList(read.column_names))

    monkeypatch.setattr(reading, "read_table", counting)
    walks: "list[int]" = []
    for answered in (5, 30):
        entries = [
            {
                "column": f"c{place}",
                "your_answer": asking.ANSWER_NO_DATE,
                "answers_you_can_give": [{"answer": asking.ANSWER_KEEP}, {"answer": asking.ANSWER_NO_DATE}],
            }
            for place in range(answered)
        ]
        answers = tmp_path / f"answers-{answered}.json"
        answers.write_text(
            json.dumps({"asked": entries, "checklist": {"columns": []}}), encoding="utf-8", newline="\n"
        )
        _CountedList.walks = 0
        code, said = _quiet(["profile", str(table), "--out-dir", str(tmp_path), "--replace", "--answers", str(answers)])
        assert code == 0, said
        walks += [_CountedList.walks]
    assert walks[1] - walks[0] < 25, walks


def test_a_count_elsewhere_leaves_out_cells_already_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """`NAT` codes beside a column of 100 `NaT` and 40 `nat`: the answer takes 40 there, and 40 is said.

    The verifier of lane R1's second repair: `NaT` is missing already, by
    synthtwin's own word, so a declaration naming `NAT` takes only the
    40 `nat` cells -- and nothing pinned the filter that counts only the
    cells not already missing. Red on the mutant that counts every
    matched spelling, which says 140.
    """
    dated = _iso_days(970) + ["NAT"] * 30
    flags = ["NaT"] * 100 + ["nat"] * 40 + [["red", "green", "blue"][place % 3] for place in range(860)]
    blocks = [{"name": "seen_at", "role": "long_tail_labels"}, {"name": "flag", "role": "categorical"}]
    asked = [(0, asking.DateCodes("iso-date", (("NAT", 30),), 970, 1000))]
    reached = asking.codes_elsewhere({"columns": blocks}, [dated, flags], asked, taxonomy.Settings())
    assert reached == {0: (asking.Elsewhere("flag", 40, 900),)}
    monkeypatch.setattr(
        taxonomy, "split_missing", lambda cells, settings, comma=False: (list(cells), [])
    )
    mutant = asking.codes_elsewhere({"columns": blocks}, [dated, flags], asked, taxonomy.Settings())
    assert mutant[0][0].rows == 140


def test_a_refused_control_fails_the_date_questions_measurement(monkeypatch: pytest.MonkeyPatch) -> None:
    """A clean spelling `synthtwin profile` refuses stops K-S3-56's driver with exit 1.

    The Codex review of lane R1, item 10: a control that wrote no
    questions file was a prose note while its totals counted it clean,
    so the entry stayed green. Red on 110cb46, whose driver exits 0.
    """
    import importlib.util

    path = pathlib.Path(__file__).resolve().parents[1] / "tools" / "measurements" / "kpi_date_questions.py"
    spec = importlib.util.spec_from_file_location("kpi_date_questions_under_test", path)
    assert spec is not None and spec.loader is not None
    driver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(driver)
    for name in ("DAY_OR_MONTH", "CODES", "NOT_ASKED"):
        monkeypatch.setattr(driver.shapes, name, ())
    monkeypatch.setattr(driver.shapes, "CLEAN", shapes.CLEAN[:1])
    monkeypatch.setattr(driver, "described", lambda folder, shape, *options: 2)
    held = io.StringIO()
    with contextlib.redirect_stdout(held):
        code = driver.main()
    assert code == 1, held.getvalue()
    assert '"not_described": 1' in held.getvalue()
