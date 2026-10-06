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
  key this landing adds taken out, hash to their digests before it;
* R8 the loader's own rules for what this landing publishes, one refused
  description each: `test_r8_a_stamp_names_one_written_clock` (D12a; its
  other half, a stamp word on ISO moments, is in the loader's battery),
  `test_r8_clock_rungs_are_ordered_by_the_instant` (T3 by instant, red
  when the rungs are compared as text) and
  `test_r8_a_twelve_hour_declaration_names_columns_of_the_table` (S8, and
  the list's own order);
* R9 `test_r9_a_declared_twelve_hour_stamp_says_what_it_cannot_hold` --
  P4-D370's stated limit, pinned: a stamp declared a 12-hour clock with no
  AM or PM writes every cell in its table's own format, and its twin
  report measures what it holds on the column's face and names each fact
  it missed instead of saying the ladder is met (red when the report
  reads the twin back on the 24-hour face). Its other half,
  `test_r9_a_declared_twelve_hour_stamp_validates_clean`, is a strict
  xfail EXCEPTED from this gate and owned by landing T2 (P4-D370): the half-day
  draw belongs to T2's hour census, whose gate turns it into a passing
  test.

And the T1 design skeptic's items: the 12-hour question and its answer
(item 1), the colon question kept (item 3), the day-first question
(item 4), and an `h-mm` column said in minutes (item 8).

And skeptic 1's repair round: the 12-hour question typed at in a
terminal, Enter and `6`, on the three shapes it is offered on (item 1:
it stopped with a KeyError), with a guard that every answer a column's
question offers has a key; one clause for each guard no test turned red
(item 3: the loader's T1 spelling, DT3's order by instant, the warning
where `--twelve-hour` reaches nothing, the style words of the summary and
the twin report, and the width tie); and an answer of `day-first` on the
repeat line (item 4).

And skeptic 2's: a key the question did not offer is asked again rather
than recorded (item 2: `6` on a column of codes recorded a 12-hour clock),
and the two guards near item 3 no test turned red -- the style words of
an `h-mm` and an `h-mm-ss` clock on the summary, and a width tie that
writes one figure on as many hours as two (item 3).
"""

import copy
import csv
import hashlib
import io
import json
import pathlib
import sys

import pytest

from synthtwin import asking, contract, errors, generation, parsing, taxonomy, validation
# -- 3b.R4 (P4-D384)
from synthtwin import date_counts
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
    """Both goldens, the new settings key taken out, hash as they did before T1.

    RE-RECORDED AT THE MERGE OF 3b.T1 (2026-10-02): "before T1" is the tree
    it merged into, where 3b.K, 3b.D1 and 3b.G1 had moved both goldens
    (`tests/test_profile_document.py` and `tests/test_twin_golden.py` say
    how); on 668f276 they were 83e1fc4f... and f2cad811....
    """
    from synthtwin import profile as producer, reading
    import tests.test_profile_document as demo
    import tests.test_twin_golden as golden

    document = demo._demo_document(tmp_path)
    document["created_with"] = "(version normalized for the golden test)"
    _without_the_second_cut(document)
    del document["settings"]["forced_twelve_hour_clocks"]
    assert hashlib.sha256(producer.serialize(document).encode("utf-8")).hexdigest() == (
        "17f1d514335b2eb06005f32357cd42c96c7b42036d5d1f71e23aee62ce08912f"
    )
    folder = tmp_path / "golden"
    folder.mkdir()
    table = fixtures.write(folder, "table.csv", fixtures.every_role_and_joined_table())
    read = reading.read_table(str(table), small_cell_floor=11)
    described = producer.build_document(
        read, taxonomy.Settings(small_cell_floor=11), ["record_code"], [], [fixtures.JOINED_COLUMN]
    )
    described["created_with"] = golden.NORMALIZED_VERSION
    _without_the_second_cut(described)
    del described["settings"]["forced_twelve_hour_clocks"]
    written = fixtures.write_profile(folder, "table-profile.json", described)
    assert hashlib.sha256(written.read_bytes()).hexdigest() == (
        "c126adc7722a717079b62801c73d02de97e2f65de624b0be82faffeb022f0eda"
    )


def _without_the_second_cut(document: dict) -> None:
    """The four keys the second cut reserves (plan P4-D386), taken out empty.

    They arrived after T1, so "as before T1" reads the document without
    them as well as without T1's own key.

    IT STANDS BELOW R7, AND R7 CALLS IT ABOVE THE LINE THAT TAKES T1's KEY
    OUT, because a landing that puts keys of its own back for R7 does so
    above R7 and below that line (3b.C1's clock census does): the two then
    merge with no line in common, both stay, both are called at R7's two
    places, and R7's two digests do not move. Taking either one alone
    turns R7 red, and re-recording its digests then would hide that.
    """
    for key in ("century_windows", "forced_date_columns", "forced_date_counts"):
        assert document["settings"].pop(key) == [], key
    for column in document["columns"]:
        if "count_form" in column:
            assert column.pop("count_form") is None, column["name"]


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
    answers.write_text(json.dumps(questions), encoding="utf-8", newline="\n")
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
    answers.write_text(json.dumps(questions), encoding="utf-8", newline="\n")
    block, profile, _questions = _described(tmp_path / "answered", cells, "--answers", str(answers))
    assert block["format"] == "day-first-datetime"
    assert json.loads(profile.read_text(encoding="utf-8"))["settings"]["day_first"] is True


def test_a_minute_clock_is_said_in_minutes() -> None:
    """Item 8: every site that names a clock's unit asks the form's step."""
    for form in parsing.CLOCK_FORMS:
        word = "minute" if parsing.clock_step(form) == 60 else "second"
        assert validation._clock_units(form) == word, form
    assert parsing.clock_step("h-mm") == 60 and parsing.clock_step("h-mm-ss AM-PM") == 1


# -- R8: the loader's own rules for what this landing publishes ----------


def _refusal(folder: pathlib.Path, document: "dict[str, object]") -> str:
    """The loader's refusal of one changed description, as a person reads it."""
    written = fixtures.write_profile(folder, "changed-profile.json", document)
    with pytest.raises(errors.ProfileError) as raised:
        contract.load_profile(str(written))
    return f"{raised.value}"


def test_r8_a_stamp_names_one_written_clock(tmp_path: pathlib.Path) -> None:
    """D12a: a slashed stamp writes its clock one way, so its census names one word."""
    _block, profile, _questions = _described(tmp_path, spellings.cells("excel_us", ROWS))
    document = json.loads(profile.read_text(encoding="utf-8"))
    contract.load_profile(str(profile))
    census = document["columns"][0]["datetime_separators"]
    assert census == {"space h": ROWS}, census
    changed = copy.deepcopy(document)
    changed["columns"][0]["datetime_separators"] = {"space h": ROWS - 20, "space": 20}
    assert contract.INVARIANTS["D12a"] in _refusal(tmp_path, changed)


def _rungs(block: "dict[str, object]") -> "list[str]":
    ladder = block["clock_percentiles"]
    assert isinstance(ladder, dict)
    return [f"{ladder[key]}" for key in sorted(ladder) if ladder[key] is not None]


def test_r8_clock_rungs_are_ordered_by_the_instant(tmp_path: pathlib.Path) -> None:
    """T3 compares instants: `9:45 AM` before `1:51 PM`, whatever the text says."""
    block, profile, _questions = _described(tmp_path, spellings.cells("clock_twelve_hour", ROWS))
    assert block["clock_form"] == "h-mm AM-PM"
    ladder = block["clock_percentiles"]
    assert isinstance(ladder, dict)
    named = [key for key in ("p05", "p10", "p25", "p50", "p75", "p90", "p95") if ladder[key] is not None]
    texts = [f"{ladder[key]}" for key in named]
    # The producer's own ladder rises by the instant and not by the text...
    assert texts != sorted(texts), texts
    contract.load_profile(str(profile))
    # ...and one rising by the text and falling by the instant is refused.
    document = json.loads(profile.read_text(encoding="utf-8"))
    changed = copy.deepcopy(document)
    for place, key in enumerate(named):
        changed["columns"][0]["clock_percentiles"][key] = "1:05 PM" if place == 0 else "11:00 AM"
    assert contract.INVARIANTS["T3"] in _refusal(tmp_path, changed)


def test_r8_red_when_rungs_are_compared_as_text(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _block, profile, _questions = _described(tmp_path, spellings.cells("clock_twelve_hour", ROWS))
    monkeypatch.setattr(contract, "_clock_at", lambda text, form: (0, text))
    with pytest.raises(errors.ProfileError) as raised:
        contract.load_profile(str(profile))
    assert contract.INVARIANTS["T3"] in f"{raised.value}"


def test_r8_a_twelve_hour_declaration_names_columns_of_the_table(tmp_path: pathlib.Path) -> None:
    """S8 holds every declared name to a column; the list is in rising order, each once."""
    cells = spellings.cells("unmarked_twelve_hour_clock", ROWS)
    _block, profile, _questions = _described(tmp_path, cells, "--twelve-hour", "seen_at")
    document = json.loads(profile.read_text(encoding="utf-8"))
    assert document["settings"]["forced_twelve_hour_clocks"] == ["seen_at"]
    contract.load_profile(str(profile))
    changed = copy.deepcopy(document)
    changed["settings"]["forced_twelve_hour_clocks"] = ["seen_at", "zzz_missing"]
    assert contract.INVARIANTS["S8"] in _refusal(tmp_path, changed)
    changed["settings"]["forced_twelve_hour_clocks"] = ["seen_at", "seen_at"]
    said = _refusal(tmp_path, changed)
    assert "forced_twelve_hour_clocks" in said and "rising order" in said, said


# -- R9: the declared 12-hour stamp's stated limit, pinned -----------------

# At a thousand rows the limit shows at seeds 0 to 2 (P4-D370); at three
# hundred, seed 0 happens to draw no time after noon that leaves its gap.
DECLARED_ROWS = 1000


def _outside(report: str, prefix: str) -> "set[str]":
    """The rung keys one report names under a prefix, as `key: MISSED` or OUTSIDE."""
    found: "set[str]" = set()
    for line in report.splitlines():
        text = line.strip()
        if text.startswith(prefix) and text.endswith(": MISSED"):
            found.add(text[len(prefix):].split(" ")[0].split(":")[0])
    return found


def _twin_report_outside(report: str) -> "set[str]":
    """The `date_percentiles` keys the twin report names as not held."""
    found: "set[str]" = set()
    for line in report.splitlines():
        text = line.strip()
        if text.startswith("'seen_at' -- date_percentiles."):
            found.add(text.split("date_percentiles.")[1].strip())
    return found


def test_r9_a_declared_twelve_hour_stamp_says_what_it_cannot_hold(tmp_path: pathlib.Path) -> None:
    """THE STATED LIMIT (P4-D370): every cell in the table's own format, every miss named."""
    name = "unmarked_twelve_hour_stamp"
    block, profile, _questions = _described(tmp_path, spellings.cells(name, DECLARED_ROWS), "--twelve-hour", "seen_at")
    assert parsing.clock_face(_style_of(block)) == parsing.CLOCK_TWELVE_HOUR
    twin, written = _twin(profile, 0)
    assert all(spellings.parses(cell, spellings.format_of(name)) for cell in written)
    report = (twin.parent / "real-twin-report.txt").read_text(encoding="utf-8")
    # The plain held clause, as plan P4-D364's builder writes it where no
    # census is published (it was the constant `_SPREAD_HELD` before).
    assert generation._spread_written(generation._SPREAD_NOTHING_MET)[0] not in report
    assert generation._SPREAD_TWELVE_HOUR_HELD in report
    _code, quality = _validated(profile, twin)
    # The rungs validation misses are the rungs the twin report names:
    # both read the twin on the column's own face.
    assert _outside(quality, "date-ladder.") == _twin_report_outside(report)


def test_r9_red_when_the_report_reads_the_24_hour_face(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    name = "unmarked_twelve_hour_stamp"
    _block, profile, _questions = _described(tmp_path, spellings.cells(name, DECLARED_ROWS), "--twelve-hour", "seen_at")
    monkeypatch.setattr(parsing, "stamp_canonical", lambda canonical, style: canonical)
    twin, _written = _twin(profile, 0)
    monkeypatch.undo()
    report = (twin.parent / "real-twin-report.txt").read_text(encoding="utf-8")
    _code, quality = _validated(profile, twin)
    assert _outside(quality, "date-ladder.") != _twin_report_outside(report)


@pytest.mark.xfail(
    strict=True,
    reason=(
        "P4-D370's stated limit, excepted from T1's gate and owned by landing T2: a "
        "stamp declared a 12-hour clock draws its time of day over the whole "
        "day, and a time after noon reads twelve hours earlier on the dial; "
        "the half-day draw belongs to T2's hour census, which must close it"
    ),
)
def test_r9_a_declared_twelve_hour_stamp_validates_clean(tmp_path: pathlib.Path) -> None:
    """Strict, and owned by landing T2 (P4-D370's carve-out).

    T1's gate holds every other clause; this one is excepted and owned by T2,
    whose hour census confines a declared 12-hour stamp's draws to the
    half day. T2's gate turns this into a passing test, and the day it
    passes the stated limit is gone and P4-D370 says so.
    """
    name = "unmarked_twelve_hour_stamp"
    _block, profile, _questions = _described(tmp_path, spellings.cells(name, DECLARED_ROWS), "--twelve-hour", "seen_at")
    twin, _written = _twin(profile, 0)
    code, _report = _validated(profile, twin)
    assert code == 0


# -- the repair round of skeptic 1 ---------------------------------------
#
# Item 1: the terminal question path, typed at, on every shape the
# 12-hour answer is offered on, with a guard that no answer a column's
# question can offer lacks a key. Item 3: one clause for each guard no
# test turned red (the loader's T1 spelling, DT3's order by instant, the
# warning where `--twelve-hour` reaches nothing, the style words of the
# summary and of the twin report, and the width tie). Item 4: an answer
# of `day-first` on the repeat line.


def _morning_clinic_stamps(rows: int) -> "list[str]":
    """`MM/dd/yyyy HH:mm` whose hours all lie 08 to 12: read before T1, asked since."""
    import random

    draw = random.Random(5)
    return [
        f"{draw.randrange(1, 13):02d}/{draw.randrange(1, 29):02d}/2024 "
        f"{draw.randrange(8, 13):02d}:{draw.choice([0, 15, 30, 45]):02d}"
        for _row in range(rows)
    ]


_TYPED_SHAPES = {
    "unmarked_twelve_hour_clock": lambda: spellings.cells("unmarked_twelve_hour_clock", ROWS),
    "unmarked_twelve_hour_stamp": lambda: spellings.cells("unmarked_twelve_hour_stamp", ROWS),
    "morning_clinic_stamp": lambda: _morning_clinic_stamps(ROWS),
}


def _typed_at_the_terminal(
    folder: pathlib.Path,
    cells: "list[str]",
    typed: "str | list[str]",
    monkeypatch: pytest.MonkeyPatch,
) -> "tuple[int, str, dict[str, object]]":
    """`synthtwin profile` with a person at the keyboard typing at every prompt.

    One line typed four times, or the lines given, in order. The question
    is drawn by `cli._the_question` and the line read by
    `cli._read_one_answer`, both as shipped: only who answers is changed.
    Returns the exit code, everything printed, and the description.
    """
    from synthtwin import cli

    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "real.csv"
    names, rows = fixtures.rows_at_the_floor("seen_at", cells)
    table.write_text(fixtures.rows_to_csv(names, rows), encoding="utf-8", newline="")
    monkeypatch.setattr(cli, "_there_is_somebody_to_ask", lambda: True)
    # A FEW LINES AND THEN THE END OF INPUT, so a key the run does not
    # know -- asked again and again -- ends the run instead of the test.
    lines = iter([typed] * 4 if isinstance(typed, str) else typed)

    def typing(prompt: str = "") -> str:
        for line in lines:
            return line
        raise EOFError

    monkeypatch.setattr("builtins.input", typing)
    said = io.StringIO()
    before = sys.stdout, sys.stderr
    sys.stdout = sys.stderr = said
    try:
        code = _exit_of(
            ["profile", str(table), "--out-dir", str(folder), "--replace", "--smallest-group", "11"]
        )
    finally:
        sys.stdout, sys.stderr = before
    document = json.loads((folder / "real-profile.json").read_text(encoding="utf-8"))
    return code, said.getvalue(), document


@pytest.mark.parametrize("shape", sorted(_TYPED_SHAPES))
def test_the_twelve_hour_question_at_the_terminal(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, shape: str
) -> None:
    """Item 1: Enter keeps the 24-hour reading; 6 declares the 12-hour clock.

    Before the repair the first of these stopped with `KeyError:
    'twelve-hour'` in `_the_question`, on columns the base read and asked
    nothing about.
    """
    cells = _TYPED_SHAPES[shape]()
    code, said, document = _typed_at_the_terminal(tmp_path / "enter", cells, "", monkeypatch)
    assert code == 0, said[-2000:]
    assert "[6] a 12-hour clock written without AM or PM" in said
    assert document["settings"]["forced_twelve_hour_clocks"] == []
    assert parsing.clock_face(_style_of(document["columns"][0])) != parsing.CLOCK_TWELVE_HOUR
    assert "--twelve-hour" not in said
    code, said, document = _typed_at_the_terminal(tmp_path / "six", cells, "6", monkeypatch)
    assert code == 0, said[-2000:]
    assert document["settings"]["forced_twelve_hour_clocks"] == ["seen_at"]
    assert parsing.clock_face(_style_of(document["columns"][0])) == parsing.CLOCK_TWELVE_HOUR
    assert "TO REPEAT THIS RUN WITHOUT THE QUESTIONS" in said
    assert "--twelve-hour seen_at" in said


def _offered_by_each_builder(skipped: "set[str]") -> "dict[str, set[str]]":
    """Every answer each function of `asking` but the skipped offers through a `Choice`, read from its source."""
    import ast

    tree = ast.parse(pathlib.Path(asking.__file__).read_text(encoding="utf-8"))
    found: "dict[str, set[str]]" = {}
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef) or node.name in skipped:
            continue
        for inner in ast.walk(node):
            if not (
                isinstance(inner, ast.Call)
                and isinstance(inner.func, ast.Name)
                and inner.func.id == "Choice"
            ):
                continue
            assert inner.args and isinstance(inner.args[0], ast.Name), (
                f"a Choice in {node.name} names its answer by a constant of asking"
            )
            # -- 3b.R4 (P4-D384): QUESTION Q3 OFFERS EACH COUNTING SYSTEM it
            # read the column in, by the system's own word, so every member
            # of `date_counts.MEMBERS` must have a key at the terminal.
            if node.name == "_date_count_choices" and inner.args[0].id == "member":
                found.setdefault(node.name, set()).update(date_counts.MEMBERS)
                continue
            found.setdefault(node.name, set()).add(getattr(asking, inner.args[0].id))
    return found


def _file_question_builders() -> "set[str]":
    """The functions `asking.file_questions` calls: their questions go to the file, never the terminal."""
    import ast

    tree = ast.parse(pathlib.Path(asking.__file__).read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "file_questions":
            return {
                inner.func.id
                for inner in ast.walk(node)
                if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Name)
            }
    raise AssertionError("asking.file_questions is gone")


def test_every_answer_a_column_question_offers_has_a_key() -> None:
    """Item 1's guard: an answer with no key stops the terminal run, so none may lack one.

    AND THE CODES QUESTION OF LANE R1 IS THE FILE'S ONLY (merge of 3b.R1,
    plan P4-D381): `_date_code_choices` builds a column question, but
    `synthtwin profile` takes every such column out of what the terminal
    asks (`asking.without_columns_of`) and puts it in the questions file
    alone, so its answers `missing` and `real-value` need no key.
    """
    from synthtwin import cli

    to_the_file = _file_question_builders()
    assert {"_day_first_questions", "_first_row_questions", "_delimiter_questions"} <= to_the_file
    assert callable(asking._date_code_choices)
    offered = _offered_by_each_builder(to_the_file | {"_date_code_choices"})
    assert "_clock_question" in offered and "_person_choices" in offered
    column_answers: "set[str]" = set()
    for builder in offered:
        column_answers |= offered[builder]
    assert asking.ANSWER_TWELVE_HOUR in column_answers
    for answer in sorted(column_answers):
        assert answer in cli._KEY_OF, answer
        key = cli._KEY_OF[answer]
        assert key in cli._ANSWER_KEYS, (answer, key)
        reached = cli._ANSWER_KEYS[key]
        # `keep` shares key 1 with `measurement`: both declare nothing.
        assert reached == answer or (
            answer == asking.ANSWER_KEEP and reached == asking.ANSWER_MEASUREMENT
        ), (answer, key, reached)


def test_the_twelve_hour_question_shows_each_key_once(tmp_path: pathlib.Path) -> None:
    """Item 1: the keys one question shows are different, so each typed key is one answer."""
    from synthtwin import cli

    for name in sorted(spellings.UNMARKED):
        _block, _profile, questions = _described(tmp_path / name, spellings.cells(name, ROWS))
        asked = [entry for entry in questions["asked"] if entry["column"] == "seen_at"]
        offered = [choice["answer"] for choice in asked[0]["answers_you_can_give"]]
        keys = [cli._KEY_OF[answer] for answer in offered]
        assert len(keys) == len(set(keys)), (name, offered, keys)


def _first_rung_before_ten(block: "dict[str, object]") -> str:
    ladder = block["clock_percentiles"]
    assert isinstance(ladder, dict)
    for key in ("p05", "p10", "p25", "p50"):
        text = ladder[key]
        if isinstance(text, str) and parsing.clock_ordinal(text, f"{block['clock_form']}") is not None:
            parts = parsing.clock_parts(text)
            if parts is not None and parts[0] < 10:
                return key
    raise AssertionError(ladder)


@pytest.mark.parametrize(
    ("name", "form", "respelled"),
    [
        ("control_clock", "hh-mm", lambda text: text[1:] if text[0] == "0" else text),
        ("clock_one_figure_hour", "h-mm", lambda text: f"0{text}"),
    ],
)
def test_r8_a_rung_of_the_other_hour_width_is_refused(
    tmp_path: pathlib.Path, name: str, form: str, respelled: "object"
) -> None:
    """Item 3 (M04): the loader's T1 holds a clock value to its form's exact spelling.

    `9:30` is the right instant on `hh-mm` and the wrong spelling, and so is
    `08:34` on `h-mm`.
    """
    block, profile, _questions = _described(tmp_path, spellings.cells(name, ROWS))
    assert block["clock_form"] == form
    contract.load_profile(str(profile))
    key = _first_rung_before_ten(block)
    document = json.loads(profile.read_text(encoding="utf-8"))
    changed = copy.deepcopy(document)
    text = changed["columns"][0]["clock_percentiles"][key]
    assert callable(respelled)
    other = respelled(text)
    assert other != text
    assert parsing.clock_ordinal(other, form) == parsing.clock_ordinal(text, form)
    changed["columns"][0]["clock_percentiles"][key] = other
    assert contract.INVARIANTS["T1"] in _refusal(tmp_path, changed)


def test_r8_listed_clock_tail_values_are_ordered_by_the_instant(tmp_path: pathlib.Path) -> None:
    """Item 3 (M05): DT3 orders a listed tail's values by instant, so `9:59 AM`
    then `10:00 AM` -- falling as text -- loads clean."""
    import random

    draw = random.Random(3)
    later: "list[str]" = []
    for _row in range(300):
        second = draw.randrange(36060, 86400)
        hour = second // 3600
        later += [f"{hour % 12 or 12}:{(second % 3600) // 60:02d} {'AM' if hour < 12 else 'PM'}"]
    block, profile, _questions = _described(tmp_path, ["9:58 AM"] * 12 + ["10:00 AM"] * 12 + later)
    assert block["clock_form"] == "h-mm AM-PM"
    assert block["low_tail"]["values"] == ["9:58 AM"]
    document = json.loads(profile.read_text(encoding="utf-8"))
    changed = copy.deepcopy(document)
    changed["columns"][0]["low_tail"] = {
        "boundary": "10:01 AM",
        "mean_distance": 1.5,
        "rms_distance": None,
        "rows": 24,
        "values": ["9:59 AM", "10:00 AM"],
    }
    changed["columns"][0]["clock_percentiles"]["p05"] = None
    written = fixtures.write_profile(tmp_path, "crossing-profile.json", changed)
    contract.load_profile(str(written))
    # ...and the same two values the other way round are refused.
    changed["columns"][0]["low_tail"]["values"] = ["10:00 AM", "9:59 AM"]
    assert contract.INVARIANTS["DT3"] in _refusal(tmp_path, changed)


def test_twelve_hour_naming_a_column_it_cannot_reach_is_said(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Item 3 (M22): `--twelve-hour` on a column of numbers warns; on an unmarked clock it does not."""
    folder = tmp_path / "numbers"
    folder.mkdir()
    table = folder / "real.csv"
    rows = [[f"{place % 37}.{place % 10}", spellings.cells("unmarked_twelve_hour_clock", ROWS)[place]] for place in range(ROWS)]
    table.write_text(fixtures.rows_to_csv(["dose", "seen_at"], rows), encoding="utf-8", newline="")
    capsys.readouterr()
    assert _exit_of(
        ["profile", str(table), "--out-dir", str(folder), "--replace",
         "--twelve-hour", "dose", "--twelve-hour", "seen_at"]
    ) == 0
    said = capsys.readouterr()
    text = said.out + said.err
    assert "The column 'dose' was named with --twelve-hour" in text
    assert "Nothing about this column was read on a 12-hour clock" in text
    assert "'seen_at' was named with --twelve-hour" not in text


def test_the_written_clock_is_said_in_the_summary_and_the_twin_report(tmp_path: pathlib.Path) -> None:
    """Item 3 (M23, M24): NF109's words, on the summary of a clock column and
    on the twin report of a stamp column, each naming the column's own style."""
    block, _profile, _questions = _described(tmp_path / "clock", spellings.cells("clock_twelve_hour", ROWS))
    summary = (tmp_path / "clock" / "real-profile.txt").read_text(encoding="utf-8")
    said = parsing.clock_style_said(_style_of(block))
    assert f"written with {said}" in summary
    # ...and the 24-hour clock written with one figure below ten, at the
    # minute and at the second (skeptic 2, item 3: M23b, the summary's
    # line held for the 12-hour forms alone).
    for name, form in (("clock_one_figure_hour", "h-mm"), ("clock_one_figure_hour_seconds", "h-mm-ss")):
        block, _profile, _questions = _described(tmp_path / name, spellings.cells(name, ROWS))
        assert block["clock_form"] == form
        summary = (tmp_path / name / "real-profile.txt").read_text(encoding="utf-8")
        said = parsing.clock_style_said(_style_of(block))
        assert said == "the hour in one figure below ten, on a 24-hour clock"
        assert f"written with {said}" in summary
    block, profile, _questions = _described(tmp_path / "stamp", spellings.cells("excel_twelve_hour", ROWS))
    twin, _written = _twin(profile, 0)
    report = (twin.parent / "real-twin-report.txt").read_text(encoding="utf-8")
    said = parsing.clock_style_said(_style_of(block))
    assert f"Its time of day is written as your table wrote it: {said}." in report
    summary = (tmp_path / "stamp" / "real-profile.txt").read_text(encoding="utf-8")
    assert f"and then {said}" in summary
    # ...and the two-figure 24-hour clock every earlier page wrote adds no line.
    _block, profile, _questions = _described(tmp_path / "control", spellings.cells("control_stamp", ROWS))
    twin, _written = _twin(profile, 0)
    report = (twin.parent / "real-twin-report.txt").read_text(encoding="utf-8")
    assert "Its time of day is written as your table wrote it" not in report


def test_a_clock_whose_hours_show_no_width_publishes_two_figures(tmp_path: pathlib.Path) -> None:
    """Item 3 (M26): every hour 10 or more shows no width, and the tie goes to `hh`."""
    import random

    draw = random.Random(11)
    cells = [f"{draw.randrange(10, 24)}:{draw.randrange(60):02d}" for _row in range(ROWS)]
    block, _profile, _questions = _described(tmp_path / "wide", cells)
    assert block["role"] == taxonomy.ROLE_CLOCK
    assert block["clock_form"] == "hh-mm"
    # ...and an exact tie between the widths goes to `hh` too (skeptic 2,
    # item 3: M26c, one figure taken on a tie wherever any hour shows it):
    # 200 hours written in one figure, 200 in two below ten, 600 from 10.
    draw = random.Random(7)
    cells = (
        [f"{draw.randrange(1, 10)}:{draw.randrange(60):02d}" for _row in range(200)]
        + [f"{draw.randrange(0, 10):02d}:{draw.randrange(60):02d}" for _row in range(200)]
        + [f"{draw.randrange(10, 24)}:{draw.randrange(60):02d}" for _row in range(600)]
    )
    draw.shuffle(cells)
    block, _profile, _questions = _described(tmp_path / "tie", cells)
    assert block["role"] == taxonomy.ROLE_CLOCK
    assert block["clock_form"] == "hh-mm"


def test_a_day_first_answer_is_on_the_repeat_line(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Item 4: a column read day first because of an answer prints `--day-first` to repeat it."""
    cells = [
        f"{moment.month}/{moment.month % 12 + 1}/{moment.year} {moment.hour}:{moment.minute:02d}"
        for moment in spellings.moments(ROWS, 9)
    ]
    _block, _profile, questions = _described(tmp_path / "asked", cells)
    about = [entry for entry in questions["about_your_file"] if "seen_at" in entry["what_synthtwin_saw"]]
    about[0]["your_answer"] = "day-first"
    answers = tmp_path / "answers.json"
    answers.write_text(json.dumps(questions), encoding="utf-8", newline="\n")
    capsys.readouterr()
    block, _profile, _questions = _described(tmp_path / "answered", cells, "--answers", str(answers))
    said = capsys.readouterr()
    assert block["format"] == "day-first-datetime"
    assert "TO REPEAT THIS RUN WITHOUT THE QUESTIONS" in said.out + said.err
    assert "--day-first" in said.out + said.err
    # ...and a typed `--day-first` is on the line the person typed already.
    capsys.readouterr()
    _described(tmp_path / "typed", cells, "--day-first")
    said = capsys.readouterr()
    assert "TO REPEAT THIS RUN WITHOUT THE QUESTIONS" not in said.out + said.err


# -- skeptic 2 of the repair round ---------------------------------------
#
# Item 2: a key of an answer the question did not offer is asked again.


def _padded_codes(rows: int) -> "list[str]":
    """Five-figure padded codes: the question offers measurement, code and record number."""
    import random

    draw = random.Random(5)
    return [f"{draw.randrange(1, 17) * 37:05d}" for _row in range(rows)]


def test_a_key_the_question_did_not_offer_is_asked_again(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Item 2: `6` on a column of codes is asked again, and Enter then keeps the reading.

    Before the fix `6` was taken on a question offering only `[1] [2]
    [3]`: the run recorded `forced_twelve_hour_clocks: ["seen_at"]` on a
    column of codes, warned of nothing and printed `--twelve-hour
    seen_at` to repeat it.
    """
    cells = _padded_codes(ROWS)
    code, said, document = _typed_at_the_terminal(tmp_path / "six", cells, ["6", ""], monkeypatch)
    assert code == 0, said[-2000:]
    assert "[2] codes" in said and "[6]" not in said
    assert said.count("Please type one of the numbers offered") == 1
    assert document["settings"]["forced_twelve_hour_clocks"] == []
    assert document["settings"]["forced_decimal_commas"] == []
    assert "--twelve-hour" not in said
    # ...`5`, a decimal comma, is asked again the same way, and a key the
    # question offers is taken at once.
    code, said, document = _typed_at_the_terminal(tmp_path / "five", cells, ["5", "2"], monkeypatch)
    assert code == 0, said[-2000:]
    assert said.count("Please type one of the numbers offered") == 1
    assert document["settings"]["forced_decimal_commas"] == []
    assert document["settings"]["forced_codes"] == ["seen_at"]
    assert "--code seen_at" in said
    # ...and `1` on the 12-hour question, whose first answer is `keep`
    # under the key it shares with `measurement`, is taken at once.
    cells = spellings.cells("unmarked_twelve_hour_clock", ROWS)
    code, said, document = _typed_at_the_terminal(tmp_path / "one", cells, ["1"], monkeypatch)
    assert code == 0, said[-2000:]
    assert "[1] leave it as it is" in said
    assert "Please type one of the numbers offered" not in said
    assert document["settings"]["forced_twelve_hour_clocks"] == []



def test_the_reading_enter_keeps_is_always_taken() -> None:
    """Item 2's rule, each clause on its own: Enter's reading, a non-answer,
    an offered answer and `measurement` for `keep` are taken; another
    question's answer is not."""
    from synthtwin import cli

    def question(taken: str, *offered: str) -> asking.Question:
        return asking.Question(
            "seen_at", taxonomy.ROLE_CLOCK, "", "",
            [asking.Choice(answer, "", "") for answer in offered], taken,
        )

    assert cli._offered_here(asking.ANSWER_MEASUREMENT, question(asking.ANSWER_MEASUREMENT, asking.ANSWER_CODE))
    assert cli._offered_here("", question(asking.ANSWER_KEEP, asking.ANSWER_KEEP))
    assert cli._offered_here(asking.ANSWER_CODE, question(asking.ANSWER_MEASUREMENT, asking.ANSWER_MEASUREMENT, asking.ANSWER_CODE))
    keep = question(asking.ANSWER_KEEP, asking.ANSWER_KEEP, asking.ANSWER_TWELVE_HOUR)
    assert cli._offered_here(asking.ANSWER_MEASUREMENT, keep)
    assert cli._offered_here(asking.ANSWER_TWELVE_HOUR, keep)
    assert not cli._offered_here(asking.ANSWER_CODE, keep)
    numbers = question(asking.ANSWER_MEASUREMENT, asking.ANSWER_MEASUREMENT, asking.ANSWER_CODE, asking.ANSWER_IDENTIFIER)
    assert not cli._offered_here(asking.ANSWER_TWELVE_HOUR, numbers)
    assert not cli._offered_here(asking.ANSWER_DECIMAL_COMMA, numbers)
    # `measurement` stands for `keep` only where `keep` is offered.
    assert not cli._offered_here(asking.ANSWER_MEASUREMENT, question(asking.ANSWER_CODE, asking.ANSWER_CODE, asking.ANSWER_IDENTIFIER))
