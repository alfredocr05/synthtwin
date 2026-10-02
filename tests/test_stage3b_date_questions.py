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
import csv
import io
import json
import pathlib

import pytest

import date_question_shapes as shapes
import fixtures
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
    read = reading.read_table(str(table))
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
    """Each shape left alone is asked once its own rule is moved: the rule is what keeps it out."""
    values = shapes.cells(shapes.by_name(name))
    assert not _asked_here(tmp_path / "shipped", values, floor)[0], (name, rule)
    monkeypatch.setattr(asking, rule, value)
    assert _asked_here(tmp_path / "moved", values, floor)[0], (name, rule)


def test_red_without_the_date_rule(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A column of notes beside a code is asked once the rest need not read as dates."""

    def anything(counted: "dict[str, int]", settings: taxonomy.Settings) -> "tuple[str, int]":
        return "iso-date", sum(counted[spelling] for spelling in counted)

    values = shapes.cells(shapes.by_name("notes_with_codes"))
    assert not _asked_here(tmp_path / "shipped", values)[0]
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
    shipped = asking.date_codes_of

    def counting(present: "list[str]", settings: taxonomy.Settings) -> "asking.DateCodes | None":
        called["columns"] = called["columns"] + 1
        return shipped(present, settings)

    monkeypatch.setattr(asking, "date_codes_of", counting)
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
        weighed = taxonomy.reading_of_the_rest(counted, settings)
        assert weighed is not None, shape.name
        matched = taxonomy._matching_date_format(values, settings)
        if matched is None:
            assert weighed[0] in ("hh-mm", "hh-mm-ss"), shape.name
            continue
        assert weighed[0] == matched[0], shape.name
        assert weighed[1] == len(matched[1]), shape.name
