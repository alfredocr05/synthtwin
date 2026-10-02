"""THE READER'S GATE (stage 3b landing T1, plan P4-D370): written clocks read and written back.

Before this landing Excel's `3/17/2023 6:42` and every 12-hour clock were
free text -- one-figure hours read only from 10 to 23, AM/PM never -- so
the twin wrote made-up strings and no code that read the real column with
its own `strptime` format read one twin cell. One clause per rule, each
red on its own mutant (named beside it):

* R1 `test_r1_every_spelling_is_read` -- the twenty spellings of
  `tests/clock_spellings.py` read with no cell left over (mutant: the
  stamp's clock read in today's two forms alone);
* R2 `test_r2_the_twin_writes_each_spelling_back` -- every twin cell at
  seeds 0 to 2 parses under the source's own format, and its clock wears
  the published style, hour width included (mutants: the writer ignores
  the style; the writer pads every hour);
* R3 `test_r3_the_written_clock_is_held_by_fit` and
  `test_r3_a_twin_rewritten_on_the_24_hour_clock_is_missed` -- a twin
  validates with nothing missed, a twin rewritten as `HH:MM` misses its
  form, and a file whose hours show no width holds a published `h`
  (mutants: an exact compare; a check that cannot fail);
* R4 `test_r4_the_twelve_hour_pitfalls` -- 12 AM is the first hour and 12
  PM noon, a marked 0 or 13 is refused, `12:00 AM` is midnight and comes
  back so, and a column declared a 12-hour clock writes hours 1 to 12
  (mutant: the `% 12` dropped);
* R5 `test_r5_one_written_clock_per_column` -- a minority on another face
  is unread and said (NF108), a minority of the other width is read and
  said (NF109), and a census too small to name falls back to the 24-hour
  clock, a stated limit;
* R6 `test_r6_the_unnamed_width_remainder_is_written` -- G7.5 step 5:
  plan l.17955's carried case (a) validates at seeds 4, 0 and 1 (mutant:
  the step withdrawn);
* R7 `test_r7_no_byte_moves` -- both golden descriptions, with the one
  key this landing adds taken out, hash to their digests before it.

And the T1 design skeptic's items: the 12-hour question and its answer
(item 1), the colon question kept (item 3), the day-first question
(item 4), and an `h-mm` column said in minutes (item 8).
"""

import csv
import datetime
import hashlib
import io
import json
import pathlib
import sys

import pytest

from synthtwin import generation, parsing, taxonomy, validation
from tests import clock_spellings as spellings
from tests import fixtures

ROWS = 300
SEEDS = (0, 1, 2)
# The writer and reader as shipped, held here before any mutant replaces
# them, so a clause judges a mutant's cells by the rule and not by itself.
_WRITTEN_CLOCK = parsing.written_clock
_CLOCK_SECOND = parsing.clock_second


def _exit_of(argv: "list[str]") -> int:
    """Run one synthtwin command in this process and return its exit code."""
    from synthtwin import cli

    before = sys.argv
    sys.argv = ["synthtwin"] + argv
    try:
        code = cli.main()
    except SystemExit as stop:
        return 0 if stop.code is None else int(stop.code)
    finally:
        sys.argv = before
    return code


def _described(
    folder: pathlib.Path, cells: "list[str]", *flags: str
) -> "tuple[dict[str, object], pathlib.Path, dict[str, object]]":
    """Describe one column the way `synthtwin profile` does; the block, the
    description's path and the questions file."""
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "real.csv"
    names, rows = fixtures.rows_at_the_floor("seen_at", cells)
    table.write_text(fixtures.rows_to_csv(names, rows), encoding="utf-8", newline="")
    assert _exit_of(
        ["profile", str(table), "--out-dir", str(folder), "--replace", "--smallest-group", "11"]
        + list(flags)
    ) == 0
    profile = folder / "real-profile.json"
    questions = folder / "real-questions.json"
    document = json.loads(profile.read_text(encoding="utf-8"))
    return document["columns"][0], profile, json.loads(questions.read_text(encoding="utf-8"))


def _twin(profile: pathlib.Path, seed: int) -> "tuple[pathlib.Path, list[str]]":
    """The twin at one seed, and its first column's present cells."""
    folder = profile.parent / f"seed-{seed}"
    folder.mkdir(exist_ok=True)
    assert _exit_of(
        ["generate", str(profile), "--seed", str(seed), "--out-dir", str(folder), "--replace"]
    ) == 0
    twin = folder / "real-twin.csv"
    rows = list(csv.reader(io.StringIO(twin.read_text(encoding="utf-8"))))
    return twin, [row[0] for row in rows[1:] if row and row[0] != ""]


def _validated(profile: pathlib.Path, checked: pathlib.Path) -> "tuple[int, str]":
    """The exit code of `validate` and its report's text."""
    folder = checked.parent / f"check-{checked.stem}"
    folder.mkdir(exist_ok=True)
    code = _exit_of(
        ["validate", str(profile), "--twin", str(checked), "--out-dir", str(folder), "--replace"]
    )
    report = ""
    for page in sorted(folder.glob("*quality*")):
        report += page.read_text(encoding="utf-8")
    return code, report


def _style_of(block: "dict[str, object]") -> str:
    """The written clock a described column publishes."""
    if block["role"] == taxonomy.ROLE_CLOCK:
        return parsing.clock_style_of(f"{block['clock_form']}")
    words = [word for word in block["datetime_separators"] if word != "(withheld)"]
    assert len(words) == 1, block["datetime_separators"]
    style = parsing.stamp_style(words[0])
    assert style is not None, words
    return style


def _clock_half(cell: str, kind: str) -> str:
    return parsing.stamp_halves(cell)[1] if kind == "stamp" else cell


def _wears(cell: str, kind: str, style: str) -> bool:
    """Whether one twin cell's clock is written exactly in one style."""
    parts = parsing.clock_parts(_clock_half(cell, kind))
    if parts is None:
        return False
    second = _CLOCK_SECOND(parts, parsing.clock_face(style))
    if second is None:
        return False
    return _WRITTEN_CLOCK(second, parts[3], style) == _clock_half(cell, kind)


# -- R1: every spelling is read ---------------------------------------


@pytest.mark.parametrize("name", sorted(spellings.SPELLINGS))
def test_r1_every_spelling_is_read(tmp_path: pathlib.Path, name: str) -> None:
    """Before T1 none of these twenty was a date or a clock time."""
    block, _profile, _questions = _described(tmp_path, spellings.cells(name, ROWS))
    wanted = taxonomy.ROLE_DATETIME if spellings.kind_of(name) == "stamp" else taxonomy.ROLE_CLOCK
    assert block["role"] == wanted, name
    assert block["n_unparsed"] == 0, name
    # ...and every real cell wears the style the column publishes.
    style = _style_of(block)
    for cell in spellings.cells(name, ROWS):
        assert _wears(cell, spellings.kind_of(name), style), (name, cell, style)


def _two_forms_only(text: str) -> "str | None":
    """The mutant of R1: a stamp's clock read in `HH:MM` and `HH:MM:SS` alone."""
    if len(text) not in (5, 8) or text[2:3] != ":":
        return None
    parts = parsing.clock_parts(text)
    if parts is None or parts[5] or parts[4] != 2:
        return None
    return f"{text[0:5]}:{text[6:8] if len(text) == 8 else '00'}"


def test_r1_red_on_its_mutant(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(parsing, "_stamp_clock", _two_forms_only)
    block, _profile, _questions = _described(tmp_path, spellings.cells("excel_twelve_hour", ROWS))
    assert block["role"] != taxonomy.ROLE_DATETIME


# -- R2 and R3: written back as written, and checked ------------------


@pytest.mark.parametrize("name", sorted(spellings.SPELLINGS))
def test_r2_the_twin_writes_each_spelling_back(tmp_path: pathlib.Path, name: str) -> None:
    """Every twin cell parses as the source's did, in the published style."""
    block, profile, _questions = _described(tmp_path, spellings.cells(name, ROWS))
    style = _style_of(block)
    kind = spellings.kind_of(name)
    fmt = spellings.format_of(name)
    for seed in SEEDS:
        _twin_path, written = _twin(profile, seed)
        assert written
        for cell in written:
            if fmt is not None:
                assert spellings.parses(cell, fmt), (name, seed, cell)
            assert _wears(cell, kind, style), (name, seed, cell, style)


def _a_writer_that_ignores_the_style(second: int, with_seconds: bool, style: str) -> str:
    return f"{second // 3600:02d}:{(second % 3600) // 60:02d}" + (
        f":{second % 60:02d}" if with_seconds else ""
    )


def test_r2_red_when_the_writer_ignores_the_style(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    block, profile, _questions = _described(tmp_path, spellings.cells("excel_twelve_hour", ROWS))
    monkeypatch.setattr(parsing, "written_clock", _a_writer_that_ignores_the_style)
    _twin_path, written = _twin(profile, 0)
    assert not all(spellings.parses(cell, spellings.format_of("excel_twelve_hour")) for cell in written)


def test_r2_red_when_the_writer_pads_every_hour(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The hour width alone: `%H:%M` reads `08:34` and `8:34` both, so the
    style check is what sees it (the skeptic's item 6)."""
    name = "excel_us"
    block, profile, _questions = _described(tmp_path, spellings.cells(name, ROWS))
    real = parsing.written_clock
    monkeypatch.setattr(
        parsing, "written_clock",
        lambda second, with_seconds, style: real(second, with_seconds, "hh" + style[1:] if style[:2] != "hh" else style),
    )
    _twin_path, written = _twin(profile, 0)
    assert all(spellings.parses(cell, spellings.format_of(name)) for cell in written)
    assert not all(_wears(cell, "stamp", _style_of(block)) for cell in written)


@pytest.mark.parametrize("name", sorted(spellings.SPELLINGS))
def test_r3_a_twin_rewritten_on_the_24_hour_clock_is_missed(
    tmp_path: pathlib.Path, name: str
) -> None:
    """The twin validates; written again as `HH:MM` it misses its clock."""
    block, profile, _questions = _described(tmp_path, spellings.cells(name, ROWS))
    twin, written = _twin(profile, 0)
    code, _report = _validated(profile, twin)
    assert code == 0, name
    style = _style_of(block)
    kind = spellings.kind_of(name)
    if style == parsing.DEFAULT_CLOCK_STYLE:
        return
    rows = list(csv.reader(io.StringIO(twin.read_text(encoding="utf-8"))))
    for row in rows[1:]:
        if not row or not row[0]:
            continue
        parts = parsing.clock_parts(_clock_half(row[0], kind))
        assert parts is not None
        second = parsing.clock_second(parts, parsing.clock_face(style))
        assert second is not None
        rewritten = parsing.written_clock(second, parts[3], parsing.DEFAULT_CLOCK_STYLE)
        row[0] = (parsing.stamp_halves(row[0])[0] + rewritten) if kind == "stamp" else rewritten
    other = twin.parent / "rewritten.csv"
    other.write_text(fixtures.rows_to_csv(rows[0], rows[1:]), encoding="utf-8", newline="")
    code, report = _validated(profile, other)
    assert code != 0, name
    assert "form.clock_form" in report or "marks." in report, name


def test_r3_the_written_clock_is_held_by_fit() -> None:
    """A file whose hours show no width holds `h`; one showing `hh` does not."""
    late = ["10:15", "23:59", "14:05"]
    assert parsing.clock_held_by_fit("h", "hh", late, False)
    assert not parsing.clock_held_by_fit("h", "hh", late + ["08:34"], False)
    assert not parsing.clock_held_by_fit("h AM-PM", "h", late, False)
    check = validation._clock_form_check("seen_at", "h-mm", "hh-mm", late)
    assert check.verdict == validation.HELD
    stamps = ["4/30/2023 10:15", "4/30/2023 23:59"]
    moved = validation._stamp_words_by_fit({"space h": 2}, {"space": 2}, stamps)
    assert moved == {"space h": 2}


def test_r3_red_on_an_exact_compare(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(parsing, "clock_held_by_fit", lambda published, measured, cells, stamps: published == measured)
    check = validation._clock_form_check("seen_at", "h-mm", "hh-mm", ["10:15", "23:59"])
    assert check.verdict == validation.MISSED


def test_r3_red_on_a_check_that_cannot_fail(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(parsing, "clock_held_by_fit", lambda published, measured, cells, stamps: True)
    check = validation._clock_form_check("seen_at", "h-mm AM-PM", "h-mm", ["8:34", "23:59"])
    assert check.verdict == validation.HELD


# -- R4: the 12-hour pitfalls ------------------------------------------


def test_r4_the_twelve_hour_pitfalls(tmp_path: pathlib.Path) -> None:
    """12 AM is the first hour, 12 PM noon; 0 and 13 refused; midnight kept."""
    def second(text: str) -> "int | None":
        parts = parsing.clock_parts(text)
        return None if parts is None else parsing.clock_second(parts, parts[5])

    assert second("12:30 AM") == 30 * 60
    assert second("12:00 PM") == 12 * 3600
    assert second("11:59 PM") == 23 * 3600 + 59 * 60
    for refused in ("0:30 AM", "00:30 AM", "13:00 PM", "24:00", "07:22:60 AM"):
        assert parsing.clock_parts(refused) is None, refused
    assert parsing.clock_at_midnight("4/30/2023 12:00:00 AM", "month-first-datetime")
    assert not parsing.clock_at_midnight("4/30/2023 12:00:00 PM", "month-first-datetime")
    # Ordered by the instant, not by the text.
    ordered = sorted(["1:05 PM", "11:00 AM", "12:30 AM"], key=lambda text: second(text) or 0)
    assert ordered == ["12:30 AM", "11:00 AM", "1:05 PM"]
    # A column of .NET date-only values stands at midnight and comes back so.
    block, profile, _questions = _described(tmp_path, spellings.cells("dotnet_date_only", ROWS))
    assert block["all_at_midnight"] is True
    _twin_path, written = _twin(profile, 0)
    assert all(cell.endswith(" 12:00:00 AM") for cell in written)


def test_r4_red_without_the_top_of_the_dial(monkeypatch: pytest.MonkeyPatch) -> None:
    real = parsing.clock_second

    def no_top(parts: "tuple[int, int, int, bool, int, str, bool]", face: str) -> "int | None":
        hour, minute, second, written, figures, written_face, late = parts
        if written_face and written_face == face:
            return (hour + (12 if late else 0)) * 3600 + minute * 60 + second
        return real(parts, face)

    monkeypatch.setattr(parsing, "clock_second", no_top)
    parts = parsing.clock_parts("12:30 AM")
    assert parts is not None and parsing.clock_second(parts, parts[5]) != 30 * 60


# -- R5: one written clock per column ---------------------------------


def test_r5_one_written_clock_per_column(tmp_path: pathlib.Path) -> None:
    """Another face is unread and said; another width is read and said."""
    faces = spellings.mixed("excel_twelve_hour", "control_stamp", 0.995)
    block, _profile, _questions = _described(tmp_path / "faces", faces)
    marked = sum(1 for cell in faces if cell.endswith("M"))
    assert block["role"] == taxonomy.ROLE_DATETIME
    assert block["n_unparsed"] == len(faces) - marked
    assert taxonomy.rendered(taxonomy.REMARK_CLOCK_OTHER_FACE, ()) in block["remarks"]
    # A tenth on the other face is more than the parse line leaves: free text, as before.
    block, _profile, _questions = _described(
        tmp_path / "tenth", spellings.mixed("excel_twelve_hour", "control_stamp", 0.9)
    )
    assert block["role"] != taxonomy.ROLE_DATETIME
    # Three in a hundred of the other width: read, said, and written the column's way.
    widths = spellings.mixed("control_stamp", "padded_date_one_figure_hour", 0.97)
    block, profile, _questions = _described(tmp_path / "widths", widths)
    assert block["n_unparsed"] == 0
    assert taxonomy.rendered(taxonomy.REMARK_CLOCK_OTHER_WIDTH, ()) in block["remarks"]
    _twin_path, written = _twin(profile, 0)
    assert all(spellings.parses(cell, "%m/%d/%Y %H:%M") for cell in written)
    # Half and half: still a column of moments.
    block, _profile, _questions = _described(
        tmp_path / "half", spellings.mixed("control_stamp", "padded_date_one_figure_hour", 0.5)
    )
    assert block["role"] == taxonomy.ROLE_DATETIME


def test_r5_a_census_too_small_to_name_writes_the_24_hour_clock(tmp_path: pathlib.Path) -> None:
    """THE STATED LIMIT (P4-D370): ten read stamps at a floor of eleven pool
    their one word, and the twin writes the two-figure 24-hour clock."""
    cells = spellings.cells("excel_twelve_hour", 10) + ["NA"] * (parsing.POPULATION_FLOOR - 10)
    block, profile, _questions = _described(tmp_path, cells)
    assert block["datetime_separators"] == {"(withheld)": 10}
    _twin_path, written = _twin(profile, 0)
    stamps = [cell for cell in written if cell != "NA"]
    assert len(stamps) == 10
    assert all(spellings.parses(cell, "%m/%d/%Y %H:%M") for cell in stamps)


# -- R6: G7.5 step 5 -----------------------------------------------------

_REMAINDER = (
    ["03/05/2020"] * 15 + ["04/06/2020"] * 15 + ["3/7/2020"] * 7 + ["03/8/2020"] * 7
    + ["NA"] * 56
)


@pytest.mark.parametrize("seed", (4, 0, 1))
def test_r6_the_unnamed_width_remainder_is_written(tmp_path: pathlib.Path, seed: int) -> None:
    """Plan l.17955's case (a): `{"padded": 30}` over 44 dates validates."""
    block, profile, _questions = _described(tmp_path, _REMAINDER)
    assert block["date_field_widths"] == {"padded": 30}
    twin, _written = _twin(profile, seed)
    code, _report = _validated(profile, twin)
    assert code == 0, seed


def test_r6_red_without_step_five(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(generation, "_unnamed_remainder", lambda *arguments: {})
    _block, profile, _questions = _described(tmp_path, _REMAINDER)
    twin, _written = _twin(profile, 0)
    code, report = _validated(profile, twin)
    assert code != 0 and "widths.padded" in report


# -- R7: no byte moves ---------------------------------------------------


def test_r7_no_byte_moves(tmp_path: pathlib.Path) -> None:
    """Both goldens, the new settings key taken out, hash as they did before T1."""
    from synthtwin import profile as producer, reading
    import tests.test_profile_document as demo
    import tests.test_twin_golden as golden

    document = demo._demo_document(tmp_path)
    document["created_with"] = "(version normalized for the golden test)"
    del document["settings"]["forced_twelve_hour_clocks"]
    assert hashlib.sha256(producer.serialize(document).encode("utf-8")).hexdigest() == (
        "83e1fc4fbb48903866f9290a9e5a93675772b121d602c09ac0e58c753da93400"
    )
    folder = tmp_path / "golden"
    folder.mkdir()
    table = fixtures.write(folder, "table.csv", fixtures.every_role_and_joined_table())
    read = reading.read_table(str(table), small_cell_floor=11)
    described = producer.build_document(
        read, taxonomy.Settings(small_cell_floor=11), ["record_code"], [], [fixtures.JOINED_COLUMN]
    )
    described["created_with"] = golden.NORMALIZED_VERSION
    del described["settings"]["forced_twelve_hour_clocks"]
    written = fixtures.write_profile(folder, "table-profile.json", described)
    assert hashlib.sha256(written.read_bytes()).hexdigest() == (
        "f2cad811ba6b715522c8fc2eedd1b2c325f09fc31a48e47b8388e0b777cecb31"
    )


# -- the design skeptic's items ------------------------------------------


@pytest.mark.parametrize("name", sorted(spellings.UNMARKED))
def test_the_twelve_hour_question_is_asked_and_its_answer_honoured(
    tmp_path: pathlib.Path, name: str
) -> None:
    """Item 1: hours 1 to 12 and no marker is asked about; `twelve-hour`
    writes the twin on that face, every cell read by `%I`."""
    cells = spellings.cells(name, ROWS)
    _block, profile, questions = _described(tmp_path / "asked", cells)
    asked = [entry for entry in questions["asked"] if entry["column"] == "seen_at"]
    assert len(asked) == 1
    offered = [choice["answer"] for choice in asked[0]["answers_you_can_give"]]
    assert offered[:2] == ["keep", "twelve-hour"]
    assert asked[0]["read_as_now"] == "keep"
    asked[0]["your_answer"] = "twelve-hour"
    answers = tmp_path / "answers.json"
    answers.write_text(json.dumps(questions), encoding="utf-8")
    block, profile, _questions = _described(tmp_path / "answered", cells, "--answers", str(answers))
    described = json.loads(profile.read_text(encoding="utf-8"))
    assert described["settings"]["forced_twelve_hour_clocks"] == ["seen_at"]
    assert parsing.clock_face(_style_of(block)) == parsing.CLOCK_TWELVE_HOUR
    for seed in SEEDS:
        _twin_path, written = _twin(profile, seed)
        assert all(spellings.parses(cell, spellings.format_of(name)) for cell in written), seed


def test_a_one_figure_clock_keeps_its_colon_question(tmp_path: pathlib.Path) -> None:
    """Item 3: `8:34` is a time of day and two numbers; Enter keeps the clock."""
    block, _profile, questions = _described(tmp_path, spellings.cells("clock_one_figure_hour", ROWS))
    assert block["role"] == taxonomy.ROLE_CLOCK
    asked = [entry for entry in questions["asked"] if entry["column"] == "seen_at"]
    assert len(asked) == 1
    offered = [choice["answer"] for choice in asked[0]["answers_you_can_give"]]
    assert offered == ["keep", "joined", "code", "identifier"]
    assert asked[0]["read_as_now"] == "keep"
    # ...and a two-figure clock that passes twelve raises none, as before.
    _block, _profile, questions = _described(tmp_path / "control", spellings.cells("control_clock", ROWS))
    assert [entry for entry in questions["asked"] if entry["column"] == "seen_at"] == []


def test_day_and_month_no_value_can_settle_are_asked(tmp_path: pathlib.Path) -> None:
    """Item 4: every day 12 or less reads both ways, so the file asks."""
    cells = [
        f"{moment.month}/{moment.month % 12 + 1}/{moment.year} {moment.hour}:{moment.minute:02d}"
        for moment in spellings.moments(ROWS, 9)
    ]
    block, _profile, questions = _described(tmp_path / "asked", cells)
    assert block["format"] == "month-first-datetime"
    about = [entry for entry in questions["about_your_file"] if "seen_at" in entry["what_synthtwin_saw"]]
    assert len(about) == 1
    about[0]["your_answer"] = "day-first"
    answers = tmp_path / "answers.json"
    answers.write_text(json.dumps(questions), encoding="utf-8")
    block, profile, _questions = _described(tmp_path / "answered", cells, "--answers", str(answers))
    assert block["format"] == "day-first-datetime"
    assert json.loads(profile.read_text(encoding="utf-8"))["settings"]["day_first"] is True


def test_a_minute_clock_is_said_in_minutes() -> None:
    """Item 8: every site that names a clock's unit asks the form's step."""
    for form in parsing.CLOCK_FORMS:
        word = "minute" if parsing.clock_step(form) == 60 else "second"
        assert validation._clock_units(form) == word, form
    assert parsing.clock_step("h-mm") == 60 and parsing.clock_step("h-mm-ss AM-PM") == 1
