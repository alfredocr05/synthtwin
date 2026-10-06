"""THE GATE OF LANDING R4 (plan P4-D384): numbers that are dates.

A column whose dates an export wrote as counts -- Excel serials, SAS and
Stata days and seconds, Unix seconds and milliseconds, Epic day numbers --
is asked about (question Q3), and once declared (`--date-count`, or an
answer) is read exactly as the dates its counts name, described as dates
with its `count_form`, and twinned as the same counts. Each clause below
turns red on the mutant it names.

* C1 -- the twenty-sixth vectors file's readings and spellings are the
  product's, and each mutant -- float arithmetic, the 1970 epoch read for
  1960, halves rounded up, figures not trimmed, Excel's leap day ignored,
  exact rounding where an exporter writes the binary64 -- turns a case red;
* C2 -- Q3 asks thirteen of the battery's fourteen shapes with the member
  that wrote them among its answers, clean and under every stray-value
  scenario but one, and raises no question the fixed-width question did
  not raise already on the chance battery (mutant: a band from 1970);
* C3 -- an answered questions file and the typed option give one
  description, byte for byte, with its `count_form` (mutant: the answer
  dropped);
* C4 -- every twin cell keeps the column's spelling and names a date, the
  weekday census and the contact census are met (mutant: the twin written
  with the 1970 epoch);
* C5 -- `validate` holds the faithful twin and the source, and MISSES a
  twin written as ISO dates, in another member or with other figures
  (mutant: a check of the form that asks nothing);
* C6 -- a column NF51 told about now carries question Q3's own words and
  no NF51;
* C7 -- a workbook's column of serials stored as numbers round-trips as
  number cells.

Every table is built here, seeded and made up (plan D13).
"""

from __future__ import annotations

import contextlib
import csv
import dataclasses
import datetime
import io
import json
import pathlib
import random
import sys

import pytest

import counted_dates as battery
from synthtwin import (
    asking,
    contract,
    date_counts,
    generation,
    parsing,
    profile,
    reading,
    taxonomy,
    validation,
)

REPOSITORY = pathlib.Path(__file__).resolve().parent.parent
VECTORS = REPOSITORY / "tests" / "reference" / "generation-branch-vectors-26.json"
_FILE = json.loads(VECTORS.read_text(encoding="utf-8"))
_UNITS = {
    "day": date_counts.DAY,
    "minute": date_counts.MINUTE,
    "second": date_counts.SECOND,
    "millisecond": date_counts.MILLISECOND,
    "microsecond": date_counts.MICROSECOND,
    "nanosecond": date_counts.NANOSECOND,
}


def _exit_of(argv: "list[str]") -> "tuple[int, str]":
    from synthtwin import cli

    said = io.StringIO()
    with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
        code = cli.main(argv)
    return code, said.getvalue()


def _table(folder: pathlib.Path, cells: "list[str]", name: str = "seen") -> pathlib.Path:
    """One column in a CSV file, each cell quoted where it holds a comma."""
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "table.csv"
    written = [f'"{cell}"' if "," in cell else cell for cell in cells]
    path.write_text(name + "\n" + "\n".join(written) + "\n", encoding="utf-8", newline="")
    return path


def _block_of(tmp: pathlib.Path, cells: "list[str]", counted: str = "") -> "dict[str, object]":
    """One column `seen` described in process, with the declaration where given."""
    path = _table(tmp, cells)
    table = reading.read_table(str(path))
    declared = (("seen", counted),) if counted else ()
    document = profile.build_document(
        table, taxonomy.Settings(forced_date_counts=declared), []
    )
    return document["columns"][0]


def _q3(block: "dict[str, object]") -> "asking.DateCountsSaid | None":
    return asking._date_counts_said(block)


# -- C1: the twenty-sixth file ------------------------------------------


def _read(case: "dict[str, object]") -> "str | None":
    written = date_counts.written_count(f"{case['text']}", f"{case['mark']}")
    if written is None:
        return None
    numerator, denominator = date_counts.exact_value(written)
    unit = _UNITS[f"{case['unit']}"]
    moment = date_counts.moment_of(f"{case['member']}", numerator, denominator, unit)
    return None if moment is None else date_counts.iso_text(moment, unit, unit)


def _spelled(case: "dict[str, object]") -> "str | None":
    iso = f"{case['iso']}"
    unit = {10: date_counts.DAY, 16: date_counts.MINUTE, 19: date_counts.SECOND,
            23: date_counts.MILLISECOND, 26: date_counts.MICROSECOND,
            29: date_counts.NANOSECOND}[len(iso)]
    form = case["form"]
    assert isinstance(form, dict)
    shaped = date_counts.CountForm(
        form["places"], form["trimmed"], form["significant"], form["exponent"],
        form["mark"], form["contacts"],
    )
    moment = date_counts.moment_of_iso(iso, unit)
    assert moment is not None
    return date_counts.written_for(f"{case['member']}", moment, unit, shaped, f"{case['contact']}")


def _wrong() -> "list[str]":
    """Every case of the file the product answers otherwise."""
    wrong: "list[str]" = []
    for name, case in sorted(_FILE["readings"].items()):
        if _read(case) != case["answer"]:
            wrong += [f"reading {name}"]
    for name, case in sorted(_FILE["spellings"].items()):
        if _spelled(case) != case["answer"]:
            wrong += [f"spelling {name}"]
    return wrong


def test_c1_every_case_of_the_twenty_sixth_file_is_the_products() -> None:
    assert len(_FILE["readings"]) >= 14 and len(_FILE["spellings"]) >= 15
    assert _wrong() == []


def _float_arithmetic(monkeypatch: pytest.MonkeyPatch) -> None:
    original = date_counts.exact_value

    def through_a_float(written: "date_counts.Written") -> "tuple[int, int]":
        numerator, denominator = original(written)
        return float(numerator / denominator).as_integer_ratio()

    monkeypatch.setattr(date_counts, "exact_value", through_a_float)


def _epoch_1970_for_1960(monkeypatch: pytest.MonkeyPatch) -> None:
    table = dict(date_counts.TABLE)
    for word in ("days-since-1960", "seconds-since-1960", "milliseconds-since-1960"):
        table[word] = dataclasses.replace(table[word], epoch=parsing.days_from_civil(1970, 1, 1))
    monkeypatch.setattr(date_counts, "TABLE", table)


def _halves_up(monkeypatch: pytest.MonkeyPatch) -> None:
    def up(numerator: int, denominator: int) -> int:
        quotient, rest = divmod(numerator, denominator)
        return quotient + (1 if 2 * rest >= denominator else 0)

    monkeypatch.setattr(date_counts, "_rounded", up)


def _not_trimmed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(date_counts, "_trimmed_number", lambda text: text)
    monkeypatch.setattr(date_counts, "_trimmed_fraction", lambda text: text)


def _no_leap_day(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(date_counts, "_EXCEL_LEAP_SERIAL", -5)
    monkeypatch.setattr(date_counts, "_EXCEL_EARLY_EPOCH", parsing.days_from_civil(1899, 12, 30))


def _exact_where_binary64(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(date_counts, "_spelled_inexact", date_counts._spelled_exact)


@pytest.mark.parametrize(
    "mutant",
    (
        _float_arithmetic, _epoch_1970_for_1960, _halves_up, _not_trimmed,
        _no_leap_day, _exact_where_binary64,
    ),
    ids=lambda mutant: mutant.__name__.strip("_"),
)
def test_c1_each_mutant_turns_a_case_red(
    monkeypatch: pytest.MonkeyPatch, mutant: object
) -> None:
    assert _wrong() == []
    mutant(monkeypatch)  # type: ignore[operator]
    assert _wrong(), "the mutant changed no answer of the file"


def test_c1_the_binary64_an_exporter_writes_is_held() -> None:
    """`%.15g` of 00:03:07 on 4 April 2024 ends in 8, where rounding the exact count gives 9."""
    case = _FILE["spellings"]["excel_15g_binary64"]
    assert _spelled(case) == case["answer"] == "45386.0021643518"
    form = date_counts.CountForm(10, True, 15, False, ".", None)
    moment = date_counts.moment_of_iso(f"{case['iso']}", date_counts.SECOND)
    assert moment is not None
    found = date_counts.count_of("excel-1900", moment, date_counts.SECOND)
    assert found is not None
    sign, digits, exponent = date_counts._significant_figures(found[0], found[1], 15)
    assert (sign, digits, exponent) == (False, "453860021643519", 4)
    assert date_counts.spelled_count(found[0], found[1], form) == "45386.0021643518"


def test_c1_the_spreadsheet_reading_is_the_workbook_readers_on_every_whole_serial() -> None:
    """One leap rule: `dialect.sheet_serial_moment` and the counted reading agree on 1 to 70,000."""
    from synthtwin import dialect

    for serial in range(1, 70000):
        moment = date_counts.moment_of("excel-1900", serial, 1, date_counts.DAY)
        mine = f"{serial}" if moment is None else date_counts.iso_text(moment, date_counts.DAY, date_counts.DAY)
        assert dialect.sheet_serial_moment(f"{serial}", "date", False) == mine, serial


# -- C2: question Q3 ------------------------------------------------------


def test_c2_q3_asks_thirteen_of_fourteen_shapes_with_their_member(tmp_path: pathlib.Path) -> None:
    asked: "dict[str, bool]" = {}
    for shape in battery.SHAPES:
        cells, _truth = battery.cells(shape, battery.ROWS, 0)
        said = _q3(_block_of(tmp_path / shape.name, cells))
        asked[shape.name] = said is not None
        if said is not None:
            members = [member for member, _first, _last in said.readings]
            assert shape.system in members, (shape.name, members)
    assert sorted(name for name in asked if not asked[name]) == list(battery.NOT_ASKED)


@pytest.mark.parametrize("scenario", battery.SCENARIOS[1:])
def test_c2_one_stray_value_does_not_silence_q3(tmp_path: pathlib.Path, scenario: str) -> None:
    """The R4 design review's BLOCKER: a typo or a placeholder in one cell in a hundred."""
    asked = 0
    for shape in battery.SHAPES:
        cells, truth = battery.cells(shape, battery.ROWS, 0)
        said = _q3(_block_of(tmp_path / shape.name, battery.dirty(shape, cells, truth, scenario, 0)))
        if said is not None:
            members = [member for member, _first, _last in said.readings]
            assert shape.system in members, (shape.name, scenario)
            asked += 1
    assert asked >= (12 if scenario == "typo_past_1" else 13), scenario


@pytest.mark.parametrize("name,least", (("events_1985", 6), ("births_1920", 3)))
def test_c2_the_two_ranges_offer_the_member_that_wrote_them(
    tmp_path: pathlib.Path, name: str, least: int
) -> None:
    """Item 2 of the review: every member of the unit whose wide band holds the column is offered."""
    asked = 0
    for shape in battery.SHAPES:
        said = _q3(_block_of(tmp_path / shape.name, battery.ranged(shape, name, battery.ROWS, 0)))
        if said is None:
            continue
        asked += 1
        assert shape.system in [member for member, _first, _last in said.readings], shape.name
    assert asked >= least


def _median(ordered: "list[float]") -> float:
    middle = (len(ordered) - 1) * 0.5
    low = int(middle)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (middle - low) * (ordered[high] - ordered[low])


def _new_questions(draws: int) -> "tuple[int, int, list[str]]":
    """Columns of the chance battery Q3 asks, and those the fixed-width question did not ask already."""
    asked = 0
    new: "list[str]" = []
    for name in sorted(battery.ORDINARY):
        for draw in range(draws):
            texts = battery.ordinary(name, 1000, draw)
            numbers = [float(text) for text in texts]
            whole = all(value == int(value) for value in numbers)
            found = date_counts.asked_of(
                texts, numbers, taxonomy._needed(0.99, len(texts)),
                _median(sorted(numbers)), whole,
            )
            if found is None:
                continue
            asked += 1
            if asking.why_worth_asking(texts) is None:
                new += [f"{name}:{draw}"]
    return asked, len(battery.ORDINARY) * draws, new


def test_c2_no_ordinary_column_gets_a_new_question() -> None:
    """Items 1 and 5: 0 new questions over the chance battery and the review's identifiers."""
    asked, draws, new = _new_questions(10)
    assert draws == 670 and asked > 0
    assert new == []


def test_c2_a_band_from_1970_would_ask_ordinary_columns(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(date_counts, "NARROW_FROM", 1970)
    _asked, _draws, new = _new_questions(4)
    assert new, "a band from 1970 asked nothing new"


def test_c2_variable_width_identifiers_are_not_asked() -> None:
    """Item 5: nine- and ten-figure order numbers lie in Unix seconds' band and are not asked."""
    for name in ("csn_9to10", "order_id_9to10"):
        for draw in range(8):
            texts = battery.ordinary(name, 1000, draw)
            numbers = [float(text) for text in texts]
            assert date_counts.asked_of(
                texts, numbers, taxonomy._needed(0.99, len(texts)), _median(sorted(numbers)), True
            ) is None, (name, draw)


def test_c2_dates_kept_at_local_midnight_are_not_read_as_utc_midnights(tmp_path: pathlib.Path) -> None:
    """Item 3: rule B reads ONE residue, midnight UTC; New York's two are a stated limit."""
    draw = random.Random(384)
    cells: "list[str]" = []
    for _row in range(1000):
        day = datetime.date(1930, 1, 1) + datetime.timedelta(days=draw.randrange(27394))
        shift = 4 if 4 <= day.month <= 10 else 5
        moment = datetime.datetime(day.year, day.month, day.day, shift)
        cells += [f"{int((moment - datetime.datetime(1970, 1, 1)).total_seconds())}"]
    assert _q3(_block_of(tmp_path, cells)) is None
    midnights = [f"{int(cell) - int(cell) % 86400}" for cell in cells]
    said = _q3(_block_of(tmp_path / "utc", midnights))
    assert said is not None and said.rule == date_counts.RULE_MIDNIGHT


def test_c2_the_question_names_no_value_and_says_the_set_aside_numbers(tmp_path: pathlib.Path) -> None:
    shape = battery.BY_NAME["xl_date"]
    cells, truth = battery.cells(shape, battery.ROWS, 0)
    cells = battery.dirty(shape, cells, truth, "zero_1pct", 0)
    path = _table(tmp_path, cells)
    code, said = _exit_of(["profile", str(path), "--out-dir", str(tmp_path), "--replace"])
    assert code == 0, said[-500:]
    questions = json.loads((tmp_path / "table-questions.json").read_text(encoding="utf-8"))
    entries = [entry for entry in questions["asked"] if entry["column"] == "seen"]
    assert len(entries) == 1
    entry = entries[0]
    offered = [choice["answer"] for choice in entry["answers_you_can_give"]]
    assert offered[0] == asking.ANSWER_MEASUREMENT and entry["read_as_now"] == asking.ANSWER_MEASUREMENT
    assert "excel-1900" in offered and "excel-1904" in offered
    shown = entry["what_synthtwin_saw"]
    assert "some cells hold 0" in shown and "they run from 2016 to 2025" in shown
    for cell in set(cells):
        if cell != "0":
            assert cell not in shown


def _offered_of(folder: pathlib.Path) -> "list[str]":
    """The answers the questions file offers about `seen`, or none where it is not asked."""
    questions = json.loads((folder / "table-questions.json").read_text(encoding="utf-8"))
    offered: "list[str]" = []
    for entry in questions["asked"]:
        if entry["column"] == "seen":
            offered += [choice["answer"] for choice in entry["answers_you_can_give"]]
    return offered


def test_c2_a_declared_decimal_comma_is_read_with_the_comma(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Item 8: clinic date-times exported with a comma for the point.

    Under `--decimal-comma` the column is numbers, and Q3 reads its counts
    with the comma, so it is asked with the 1900 system among its answers.
    Undeclared, the cells are text and nothing asks about dates (a stated
    limit). THE MUTANT: Q3 reading the declared column with the point.
    """
    shape = battery.BY_NAME["xl_dt15g"]
    cells, _truth = battery.cells(shape, battery.ROWS, 0)
    commas = [cell.replace(".", ",") for cell in cells]
    assert sum("," in cell for cell in commas) > 900
    path = _table(tmp_path, commas)
    runs = {}
    for name, extra in (("declared", ["--decimal-comma", "seen"]), ("plain", [])):
        folder = tmp_path / name
        folder.mkdir()
        code, said = _exit_of(["profile", str(path), *extra, "--out-dir", str(folder), "--replace"])
        assert code == 0, said[-500:]
        runs[name] = _offered_of(folder)
    assert "excel-1900" in runs["declared"]
    assert not [word for word in runs["plain"] if word in date_counts.MEMBERS]
    original = date_counts.asked_of

    def pointed(*arguments: object) -> "date_counts.Asked | None":
        return original(*arguments[:5])  # type: ignore[arg-type]

    monkeypatch.setattr(date_counts, "asked_of", pointed)
    mutated = tmp_path / "mutated"
    mutated.mkdir()
    code, said = _exit_of(["profile", str(path), "--decimal-comma", "seen", "--out-dir", str(mutated), "--replace"])
    assert code == 0, said[-500:]
    assert "excel-1900" not in _offered_of(mutated)


# -- C3: the answer and the option ---------------------------------------


def test_c3_an_answered_file_and_the_typed_option_give_one_description(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    shape = battery.BY_NAME["sas_days"]
    cells, _truth = battery.cells(shape, battery.ROWS, 0)
    path = _table(tmp_path, cells)
    plain = tmp_path / "plain"
    plain.mkdir()
    assert _exit_of(["profile", str(path), "--out-dir", str(plain), "--replace"])[0] == 0
    questions = json.loads((plain / "table-questions.json").read_text(encoding="utf-8"))
    for entry in questions["asked"]:
        if entry["column"] == "seen":
            entry["your_answer"] = "days-since-1960"
    answers = tmp_path / "answers.json"
    answers.write_text(json.dumps(questions), encoding="utf-8")
    answered = tmp_path / "answered"
    typed = tmp_path / "typed"
    answered.mkdir()
    typed.mkdir()
    assert _exit_of(["profile", str(path), "--answers", str(answers), "--out-dir", str(answered), "--replace"])[0] == 0
    assert _exit_of(["profile", str(path), "--date-count", "seen", "days-since-1960", "--out-dir", str(typed), "--replace"])[0] == 0
    one = (answered / "table-profile.json").read_bytes()
    assert one == (typed / "table-profile.json").read_bytes()
    document = json.loads(one)
    assert document["settings"]["forced_date_counts"] == [["seen", "days-since-1960"]]
    block = document["columns"][0]
    assert block["role"] == "datetime" and block["format"] == "iso-date"
    assert block["count_form"] == {
        "contacts": None, "exponent": False, "mark": ".", "places": 0,
        "significant": None, "trimmed": False,
    }
    # THE MUTANT: the answer dropped.
    original = asking.answers_in

    def dropped(document: object, shown: str) -> asking.Answers:
        return dataclasses.replace(original(document, shown), date_counts=())

    monkeypatch.setattr(asking, "answers_in", dropped)
    mutated = tmp_path / "mutated"
    mutated.mkdir()
    assert _exit_of(["profile", str(path), "--answers", str(answers), "--out-dir", str(mutated), "--replace"])[0] == 0
    assert (mutated / "table-profile.json").read_bytes() != one


def test_c3_a_system_outside_the_twelve_is_refused_before_the_table_is_read(tmp_path: pathlib.Path) -> None:
    path = _table(tmp_path, ["45000"] * 200)
    code, said = _exit_of(["profile", str(path), "--date-count", "seen", "excel-2000", "--out-dir", str(tmp_path)])
    assert code == 2 and "is not one of the systems synthtwin reads" in said
    assert not (tmp_path / "table-profile.json").exists()


def test_c3_a_counted_column_also_named_a_code_is_refused(tmp_path: pathlib.Path) -> None:
    path = _table(tmp_path, ["45000"] * 200)
    code, said = _exit_of([
        "profile", str(path), "--date-count", "seen", "excel-1900", "--code", "seen",
        "--out-dir", str(tmp_path),
    ])
    assert code == 2
    assert not (tmp_path / "table-profile.json").exists()


# -- C4 and C5: the twin, and its check ----------------------------------


def _trip(folder: pathlib.Path, cells: "list[str]", member: str, *extra: str) -> "dict[str, object]":
    path = _table(folder, cells)
    code, said = _exit_of(["profile", str(path), "--date-count", "seen", member, "--out-dir", str(folder), "--replace", *extra])
    assert code == 0, said[-800:]
    described = folder / "table-profile.json"
    code, said = _exit_of(["generate", str(described), "--seed", "0", "--out-dir", str(folder), "--replace"])
    assert code == 0, said[-800:]
    twin = [row[0] for row in list(csv.reader(io.StringIO((folder / "table-twin.csv").read_text(encoding="utf-8"))))[1:] if row]
    exits = []
    for checked in (folder / "table-twin.csv", path):
        out = folder / f"check-{checked.stem}"
        out.mkdir(exist_ok=True)
        exits += [_exit_of(["validate", str(described), "--twin", str(checked), "--out-dir", str(out), "--replace"])[0]]
    return {
        "described": described,
        "block": json.loads(described.read_text(encoding="utf-8"))["columns"][0],
        "twin": twin,
        "twin_exit": exits[0],
        "real_exit": exits[1],
        "path": path,
    }


@pytest.mark.parametrize("name", ("xl_date", "xl_dt15g", "sas_secs", "unix_ms", "epic_real", "unix_s_birth"))
def test_c4_every_twin_cell_keeps_the_columns_spelling_and_names_a_date(
    tmp_path: pathlib.Path, name: str
) -> None:
    shape = battery.BY_NAME[name]
    cells, _truth = battery.cells(shape, battery.ROWS, 0)
    trip = _trip(tmp_path, cells, shape.system)
    loaded = contract.load_profile(str(trip["described"]))
    facts = loaded.columns[0].facts
    assert isinstance(facts, contract.DatetimeFacts) and facts.count_form is not None
    unit = contract.counted_unit(facts)
    for cell in trip["twin"]:
        written = date_counts.written_count(cell, facts.count_form.mark)
        assert written is not None and date_counts.form_holds(facts.count_form, written), cell
        numerator, denominator = date_counts.exact_value(written)
        assert date_counts.moment_of(shape.system, numerator, denominator, unit) is not None, cell
    assert trip["twin_exit"] == 0 and trip["real_exit"] == 0
    if shape.kind == "date":
        real = [battery.decode(shape.system, cell) for cell in cells]
        fake = [battery.decode(shape.system, cell) for cell in trip["twin"]]
        assert battery.tvd(
            battery.weekday_shares([m for m in real if m is not None]),
            battery.weekday_shares([m for m in fake if m is not None]),
        ) <= 0.03
    if name == "epic_real":
        assert facts.count_form.contacts is not None
        words = [date_counts.contact_word(date_counts.written_count(cell)) for cell in trip["twin"]]  # type: ignore[arg-type]
        for word, count in facts.count_form.contacts.items():
            assert words.count(word) == count


def test_c4_the_twin_written_with_the_1970_epoch_is_missed(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    shape = battery.BY_NAME["sas_days"]
    cells, _truth = battery.cells(shape, battery.ROWS, 0)
    original = date_counts.written_for

    def shifted(member: str, moment: int, unit: int, form: "date_counts.CountForm", contact: str = date_counts.NO_CONTACT) -> "str | None":
        return original("days-since-1970" if member == "days-since-1960" else member, moment, unit, form, contact)

    monkeypatch.setattr(generation.date_counts, "written_for", shifted)
    trip = _trip(tmp_path, cells, shape.system)
    assert trip["twin_exit"] == 3


def _rewritten(trip: "dict[str, object]", folder: pathlib.Path, change: "object") -> int:
    twin = [change(cell) for cell in trip["twin"]]  # type: ignore[operator]
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "changed.csv"
    path.write_text("seen\n" + "\n".join(twin) + "\n", encoding="utf-8", newline="")
    out = folder / "check-changed"
    out.mkdir(exist_ok=True)
    return _exit_of(["validate", str(trip["described"]), "--twin", str(path), "--out-dir", str(out), "--replace"])[0]


def test_c5_validate_misses_a_twin_written_another_way(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    shape = battery.BY_NAME["xl_date"]
    cells, _truth = battery.cells(shape, battery.ROWS, 0)
    trip = _trip(tmp_path, cells, shape.system)
    assert trip["twin_exit"] == 0

    def as_iso(cell: str) -> str:
        return (datetime.date(1899, 12, 30) + datetime.timedelta(days=int(cell))).isoformat()

    assert _rewritten(trip, tmp_path / "iso", as_iso) == 3
    assert _rewritten(trip, tmp_path / "member", lambda cell: f"{int(cell) - 1462}") == 3
    assert _rewritten(trip, tmp_path / "places", lambda cell: f"{cell}.000") == 3
    # THE MUTANT: a check of the form that asks nothing passes the ISO twin.
    monkeypatch.setattr(validation, "_count_form_checks", lambda *arguments: [])
    assert _rewritten(trip, tmp_path / "vacuous", as_iso) == 0


def test_c5_a_count_that_names_no_date_is_no_value_and_written_back(tmp_path: pathlib.Path) -> None:
    """Item 1 under a declaration: Excel's 0 and 60 are counted as no value, never voiding it."""
    shape = battery.BY_NAME["xl_date"]
    cells, truth = battery.cells(shape, battery.ROWS, 0)
    cells = battery.dirty(shape, cells, truth, "zero_1pct", 0)
    for place in range(20, 40):
        cells[place] = "60"
    trip = _trip(tmp_path, cells, shape.system)
    block = trip["block"]
    assert block["role"] == "datetime"
    assert block["missing_by_source"] == {"0": 10, "60": 20} or block["missing_by_source"] == {"60": 20}
    assert block["missing_by_class"]["(declared-missing)"] >= 20
    assert trip["twin"].count("60") == 20
    assert trip["twin_exit"] == 0 and trip["real_exit"] == 0


def test_c5_a_declaration_whose_cells_are_no_dates_decides_nothing(tmp_path: pathlib.Path) -> None:
    """CD1 and NF115: the column is described as it reads, and the run says so."""
    draw = random.Random(115)
    cells = [f"A{draw.randrange(100, 999)}" for _row in range(300)]
    path = _table(tmp_path, cells)
    code, said = _exit_of(["profile", str(path), "--date-count", "seen", "excel-1900", "--out-dir", str(tmp_path), "--replace"])
    assert code == 0 and "did not read as such" in said
    block = json.loads((tmp_path / "table-profile.json").read_text(encoding="utf-8"))["columns"][0]
    assert block["role"] != "datetime"
    assert any(contract.COUNTED_NOT_READ_MARK in remark for remark in block["remarks"])
    rendered = taxonomy.rendered(taxonomy.REMARK_COUNTED_DATES_NOT_READ, ("excel-1900",))
    assert contract.COUNTED_NOT_READ_MARK in rendered


def test_c5_a_table_of_one_counted_column_is_counted_in_rows(tmp_path: pathlib.Path) -> None:
    """The population census reads each count's date: one counted column is a table of rows."""
    shape = battery.BY_NAME["unix_s"]
    cells, _truth = battery.cells(shape, 150, 0)
    trip = _trip(tmp_path, cells, shape.system)
    assert trip["block"]["n_present"] == 150


def test_c5_r_exponent_form_and_a_decimal_comma_round_trip(tmp_path: pathlib.Path) -> None:
    """Items 6 and 8: R's shorter form, and a comma for the point, read and written back."""
    draw = random.Random(6)
    cells: "list[str]" = []
    for _row in range(400):
        day = datetime.date(2016, 1, 1) + datetime.timedelta(days=draw.randrange(3653))
        milliseconds = (day - datetime.date(1970, 1, 1)).days * 86400000 + draw.choice((0, 0, 0, draw.randrange(86400) * 1000))
        form = date_counts.CountForm(0, True, 15, True, ".", None)
        cells += [date_counts.spelled_count(milliseconds, 1, form)]
    assert any("e+" in cell for cell in cells) and not all("e+" in cell for cell in cells)
    trip = _trip(tmp_path / "r", cells, "milliseconds-since-1970")
    assert trip["block"]["count_form"]["exponent"] is True
    assert any("e+" in cell for cell in trip["twin"])
    assert trip["twin_exit"] == 0 and trip["real_exit"] == 0
    commas = [f"{45000 + draw.randrange(3000)},{draw.randrange(10**6):06d}".rstrip("0").rstrip(",") for _row in range(400)]
    trip = _trip(tmp_path / "comma", commas, "excel-1900", "--decimal-comma", "seen")
    assert trip["block"]["count_form"]["mark"] == ","
    assert all("," in cell or cell.isdigit() for cell in trip["twin"])
    assert trip["twin_exit"] == 0 and trip["real_exit"] == 0


def test_c5_fifteen_figures_crossing_serial_ten_thousand_round_trip(tmp_path: pathlib.Path) -> None:
    """Item 7: `%.15g` writes one figure fewer after the point past serial 10,000."""
    shape = battery.BY_NAME["xl_dt15g"]
    cells = battery.ranged(shape, "births_1920", battery.ROWS, 0)
    assert any(len(cell.split(".")[0]) == 4 for cell in cells) and any(len(cell.split(".")[0]) == 5 for cell in cells)
    trip = _trip(tmp_path, cells, "excel-1900")
    form = trip["block"]["count_form"]
    assert form["significant"] == 15 and trip["block"]["time_precision"] == "second"
    assert trip["twin_exit"] == 0 and trip["real_exit"] == 0
    loaded = contract.load_profile(str(trip["described"]))
    facts = loaded.columns[0].facts
    assert isinstance(facts, contract.DatetimeFacts) and facts.count_form is not None
    unit = contract.counted_unit(facts)
    for cell in cells:
        written = date_counts.written_count(cell)
        assert written is not None
        numerator, denominator = date_counts.exact_value(written)
        moment = date_counts.moment_of("excel-1900", numerator, denominator, unit)
        assert moment is not None
        assert date_counts.written_for("excel-1900", moment, unit, facts.count_form) == cell


# -- C6: NF51's place -----------------------------------------------------


def test_c6_a_column_of_unix_seconds_carries_q3s_words_and_no_nf51(tmp_path: pathlib.Path) -> None:
    shape = battery.BY_NAME["unix_s"]
    cells, _truth = battery.cells(shape, battery.ROWS, 0)
    path = _table(tmp_path, cells)
    table = reading.read_table(str(path))
    document = profile.build_document(table, taxonomy.Settings(), [])
    forms = [remark.form for remark in document["columns"][0]["remarks"]]
    assert taxonomy.REMARK_EPOCH_BAND not in forms
    assert taxonomy.REMARK_NUMBERS_COULD_BE_DATES in forms
    assert forms.count(taxonomy.REMARK_READ_AS_COUNTED_DATES) == 2
    said = " ".join(document["columns"][0]["remarks"])
    assert "changes nothing about your twin" not in said
    assert "run from" not in said or "runs from 2016 to 2025" in said


def test_c6_the_years_are_the_published_edges_said_another_way(tmp_path: pathlib.Path) -> None:
    """NF114 quotes the block's own edges: a description naming other years is refused."""
    shape = battery.BY_NAME["sas_days"]
    cells, _truth = battery.cells(shape, battery.ROWS, 0)
    block = _block_of(tmp_path, cells)
    for remark in block["remarks"]:
        if remark.form == taxonomy.REMARK_READ_AS_COUNTED_DATES:
            edges = taxonomy.published_ends(block)
            assert edges is not None
            assert remark.arguments[1:] == (
                date_counts.years_of(remark.arguments[0], edges[0]),
                date_counts.years_of(remark.arguments[0], edges[1]),
            )
            with pytest.raises(Exception):
                profile._counted_years_quote_the_published_edges(
                    (remark.arguments[0], remark.arguments[1] - 1, remark.arguments[2]), block
                )


# -- C7: a workbook --------------------------------------------------------


def test_c7_a_workbooks_serials_stored_as_numbers_come_back_as_number_cells(tmp_path: pathlib.Path) -> None:
    from tests import crosscheck

    openpyxl = crosscheck.fixture_writer()
    shape = battery.BY_NAME["xl_date"]
    cells, _truth = battery.cells(shape, 300, 0)
    book = openpyxl.Workbook()
    sheet = book.active
    sheet.title = "Data"
    sheet.cell(row=1, column=1, value="seen")
    for row, cell in enumerate(cells, start=2):
        sheet.cell(row=row, column=1, value=int(cell))
    table = tmp_path / "table.xlsx"
    held = io.BytesIO()
    book.save(held)
    table.write_bytes(held.getvalue())
    code, said = _exit_of(["profile", str(table), "--date-count", "seen", "excel-1900", "--out-dir", str(tmp_path), "--replace"])
    assert code == 0, said[-600:]
    described = tmp_path / "table-profile.json"
    assert json.loads(described.read_text(encoding="utf-8"))["columns"][0]["role"] == "datetime"
    code, said = _exit_of(["generate", str(described), "--seed", "0", "--out-dir", str(tmp_path), "--replace"])
    assert code == 0, said[-600:]
    twin = tmp_path / "table-twin.xlsx"
    read = crosscheck.reader().load_workbook(twin).worksheets[0]
    values = [row[0].value for row in read.iter_rows(min_row=2, max_col=1)]
    assert values and all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in values)
    out = tmp_path / "check"
    out.mkdir()
    assert _exit_of(["validate", str(described), "--twin", str(twin), "--out-dir", str(out), "--replace"])[0] == 0


# -- the loader's own words ------------------------------------------------


def test_the_loaders_mark_is_the_rendered_sentences() -> None:
    """CD1 reads NF115 by one phrase, a second spelling of it; held to the rendered form."""
    for member in date_counts.MEMBERS:
        assert contract.COUNTED_NOT_READ_MARK in taxonomy.rendered(
            taxonomy.REMARK_COUNTED_DATES_NOT_READ, (member,)
        )


def test_every_member_has_a_terminal_key() -> None:
    from synthtwin import cli

    keys = {cli._KEY_OF[member] for member in date_counts.MEMBERS}
    assert len(keys) == 12
    for member in date_counts.MEMBERS:
        assert cli._ANSWER_KEYS[cli._KEY_OF[member]] == member


@pytest.mark.parametrize("member", date_counts.MEMBERS)
def test_every_member_reads_and_writes_its_own_counts(member: str) -> None:
    """Every member, at its own unit: a moment written as its count reads back as itself."""
    found = date_counts.TABLE[member]
    unit = found.unit if found.unit < date_counts.DAY else date_counts.DAY
    form = date_counts.CountForm(0, False, None, False, ".", None)
    for day in (parsing.days_from_civil(1950, 6, 1), parsing.days_from_civil(2024, 2, 29)):
        moment = day * (date_counts.DAY // unit) + (7 if unit < date_counts.DAY else 0)
        text = date_counts.written_for(member, moment, unit, form)
        assert text is not None
        written = date_counts.written_count(text)
        assert written is not None
        numerator, denominator = date_counts.exact_value(written)
        assert date_counts.moment_of(member, numerator, denominator, unit) == moment, (member, text)
