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
    for name, case in sorted(_FILE["dealings"].items()):
        if generation._contacts_dealt(case["census"], case["dated"]) != case["answer"]:
            wrong += [f"dealing {name}"]
    return wrong


def test_c1_every_case_of_the_twenty_sixth_file_is_the_products() -> None:
    assert len(_FILE["readings"]) >= 14 and len(_FILE["spellings"]) >= 17
    assert len(_FILE["dealings"]) >= 4
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


def _dealt_down_the_rows(monkeypatch: pytest.MonkeyPatch) -> None:
    """The first build's dealing: the census's words in rank order, down the rows."""

    def in_rank_order(census: "dict[str, int]", dated: int) -> "list[str]":
        words: "list[str]" = []
        for _rank, word in sorted((-census[each], each) for each in census):
            words += [word] * census[word]
        return (words + [date_counts.NO_CONTACT] * dated)[:dated]

    monkeypatch.setattr(generation, "_contacts_dealt", in_rank_order)


def _repr_never(monkeypatch: pytest.MonkeyPatch) -> None:
    """Seventeen figures written by `%.17g` and a whole count with no `.0`, as `repr` never writes them."""
    monkeypatch.setattr(date_counts, "_REPR_WHOLE_BELOW", 0)
    original = date_counts._spelled_inexact

    def seventeen(numerator: int, denominator: int, form: "date_counts.CountForm") -> str:
        if form.significant == 17 and not form.exponent:
            return f"{numerator / denominator:.17g}"
        return original(numerator, denominator, form)

    monkeypatch.setattr(date_counts, "_spelled_inexact", seventeen)


@pytest.mark.parametrize(
    "mutant",
    (
        _float_arithmetic, _epoch_1970_for_1960, _halves_up, _not_trimmed,
        _no_leap_day, _exact_where_binary64, _dealt_down_the_rows, _repr_never,
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
    # A KEYING SLIP A CENTURY EARLY CAN LAND INSIDE THE BAND AT ANOTHER WIDTH,
    # which no rule lets stand (`date_counts._text_holds`): Excel birth dates
    # from 1930 keyed in the 1830s read as four figures.
    assert asked >= (12 if scenario in ("typo_past_1", "typos_2", "typos_5") else 13), scenario


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
                _median(sorted(numbers)), whole, floor=11,
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
    assert draws == 750 and asked > 0
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
                texts, numbers, taxonomy._needed(0.99, len(texts)), _median(sorted(numbers)), True,
                floor=11,
            ) is None, (name, draw)


def test_c2_dates_kept_at_local_midnight_are_not_asked_as_dates_at_utc_midnight(tmp_path: pathlib.Path) -> None:
    """Item 3: rule B reads ONE residue, midnight UTC; New York's two are a stated limit."""
    draw = random.Random(384)
    cells: "list[str]" = []
    for _row in range(1000):
        day = datetime.date(1930, 1, 1) + datetime.timedelta(days=draw.randrange(27394))
        shift = 4 if 4 <= day.month <= 10 else 5
        moment = datetime.datetime(day.year, day.month, day.day, shift)
        cells += [f"{int((moment - datetime.datetime(1970, 1, 1)).total_seconds())}"]
    assert _q3(_block_of(tmp_path, cells)) is None
    at_utc = [f"{int(cell) - int(cell) % 86400}" for cell in cells]
    said = _q3(_block_of(tmp_path / "utc", at_utc))
    assert said is not None and said.rule == date_counts.RULE_MIDNIGHT


def test_c2_the_question_names_no_value_and_says_the_set_aside_numbers(tmp_path: pathlib.Path) -> None:
    """Twenty `0` cells in a thousand: a heap the ladder publishes as the low end.

    The question still offers the 1900 system, its years read past the
    heap (the review of landing R4, item 1: the first build read them off
    the heaped `0`, which names no Excel date, and dropped the system),
    and names `0` among the numbers set aside, which twenty cells hold.
    """
    shape = battery.BY_NAME["xl_date"]
    cells, _truth = battery.cells(shape, battery.ROWS, 0)
    cells = battery.heaped(shape, cells, "zero", 0.02)
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

    def pointed(*arguments: object, **named: object) -> "date_counts.Asked | None":
        return original(*arguments[:5], **named)  # type: ignore[arg-type]

    monkeypatch.setattr(date_counts, "asked_of", pointed)
    mutated = tmp_path / "mutated"
    mutated.mkdir()
    code, said = _exit_of(["profile", str(path), "--decimal-comma", "seen", "--out-dir", str(mutated), "--replace"])
    assert code == 0, said[-500:]
    assert "excel-1900" not in _offered_of(mutated)


def _table_of(folder: pathlib.Path, columns: "dict[str, list[str]]") -> pathlib.Path:
    """Several columns of one length in a CSV file, none holding a comma."""
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "table.csv"
    names = list(columns)
    rows = [",".join(names)]
    for place in range(len(columns[names[0]])):
        rows += [",".join(columns[name][place] for name in names)]
    path.write_text("\n".join(rows) + "\n", encoding="utf-8", newline="")
    return path


@pytest.mark.parametrize("kind", battery.PLACEHOLDERS)
def test_c2_a_heap_of_placeholders_keeps_each_shapes_system_and_years(
    tmp_path: pathlib.Path, kind: str
) -> None:
    """The review of landing R4, item 1: a placeholder common enough to be the column's published end.

    At 10,000 rows, two and ten cells in a thousand holding `0`, `-1` or
    the system's own count for 9999-12-31 or 1900-01-01: every shape Q3
    asks is offered the system that wrote it, with years within one of
    the true span. The first build read the years off the heaped end
    itself -- `0` names no Excel date, so the 1900 system was dropped
    from the four Excel shapes, and the 9999 count gave "2016 to 9999".
    """
    shapes = [shape for shape in battery.SHAPES if shape.name not in battery.NOT_ASKED]
    for share in (0.002, 0.01):
        columns: "dict[str, list[str]]" = {}
        spans: "dict[str, tuple[int, int]]" = {}
        for shape in shapes:
            cells, truth = battery.cells(shape, 10000, 0)
            columns[shape.name] = battery.heaped(shape, cells, kind, share)
            spans[shape.name] = (min(t.year for t in truth), max(t.year for t in truth))
        path = _table_of(tmp_path / f"{kind}-{share}", columns)
        document = profile.build_document(reading.read_table(str(path)), taxonomy.Settings(), [])
        for shape, block in zip(shapes, document["columns"]):
            said = _q3(block)
            assert said is not None, (kind, share, shape.name)
            years = {member: (first, last) for member, first, last in said.readings}
            assert shape.system in years, (kind, share, shape.name, sorted(years))
            first, last = years[shape.system]
            low, high = spans[shape.name]
            assert abs(first - low) <= 1 and abs(last - high) <= 1, (kind, share, shape.name, years)


def test_c2_one_placeholder_cell_is_set_aside_and_not_named(tmp_path: pathlib.Path) -> None:
    """The review of landing R4, item 4: a set-aside number one row holds is no word of NF113.

    One `0` among Unix-second birth dates is a birth on 1 January 1970,
    and one `-1` among SAS days is 31 December 1959: each is still set
    aside for the question, and named only where the census line of
    cells -- eleven -- holds it.
    """
    for name, word in (("unix_s_birth", "0"), ("sas_days", "-1"), ("xl_date", "2")):
        cells, _truth = battery.cells(battery.BY_NAME[name], battery.ROWS, 0)
        for many in (1, 9, 11):
            changed = list(cells)
            for place in range(many):
                changed[100 + 7 * place] = word
            held = changed.count(word)
            said = _q3(_block_of(tmp_path / f"{name}-{many}", changed))
            assert said is not None, (name, many)
            shown = "the count for 1 January 1900" if word == "2" else word
            named = date_counts.aside_listed(said.aside).split(", ")
            assert (shown in named) == (held >= 11), (name, held, said.aside)
            if many == 1:
                assert held < 11 and shown not in named


def test_c2_nine_tenths_of_the_present_cells_stand_beside_the_set_aside_ones(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The 90 % share (mutant M04): twelve cells in a hundred holding `0` leave no question."""
    shape = battery.BY_NAME["xl_date"]
    cells, _truth = battery.cells(shape, battery.ROWS, 0)
    cells = battery.heaped(shape, cells, "zero", 0.12)
    assert _q3(_block_of(tmp_path / "head", cells)) is None
    monkeypatch.setattr(date_counts, "_rest_is_enough", lambda rest, present: rest >= date_counts.REST_LEAST)
    assert _q3(_block_of(tmp_path / "mutant", cells)) is not None


def test_c2_every_system_of_the_unit_whose_years_fit_is_offered(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The R4 design review's item 2 (mutant M07): SAS days of June 1987 to 1989.

    Read in the 1960 system they lie before the band from 1990, and read
    in the 1970 one inside it, so the rule holds for the 1970 system
    alone; the 1960 system that wrote them is offered beside it because
    its years fit 1900 to 2050.
    """
    draw = random.Random(1987)
    first = datetime.date(1987, 6, 1)
    cells = [
        f"{(first + datetime.timedelta(days=draw.randrange(944)) - datetime.date(1960, 1, 1)).days}"
        for _row in range(battery.ROWS)
    ]
    said = _q3(_block_of(tmp_path / "head", cells))
    assert said is not None
    offered = [member for member, _first, _last in said.readings]
    assert "days-since-1960" in offered and "days-since-1970" in offered

    def hits_alone(
        ordered: "list[float]", hits: "list[str]", total: int, *rest: object
    ) -> "tuple[str, ...]":
        return tuple(hits)

    monkeypatch.setattr(date_counts, "_offered", hits_alone)
    said = _q3(_block_of(tmp_path / "mutant", cells))
    assert said is not None
    assert "days-since-1960" not in [member for member, _first, _last in said.readings]


def _days_at_midnight(days: "list[int]") -> "tuple[list[str], list[float]]":
    texts = [f"{day * 86400}" for day in days]
    return texts, [float(text) for text in texts]


def test_c2_rule_b_reads_eleven_different_days_at_midnight(monkeypatch: pytest.MonkeyPatch) -> None:
    """Rule B (mutant M35): Unix seconds at midnight UTC of births before 1990, eleven different days or more.

    Ten different days repeated over a thousand rows are no column of
    dates rule B may ask about; eleven are.
    """
    first = parsing.days_from_civil(1935, 3, 1)
    for different, asked in ((10, False), (11, True)):
        days = [first + 997 * (row % different) for row in range(battery.ROWS)]
        texts, numbers = _days_at_midnight(days)
        found = date_counts.asked_of(
            texts, numbers, taxonomy._needed(0.99, len(texts)), _median(sorted(numbers)), True,
            floor=11,
        )
        assert (found is not None) == asked, different
        if found is not None:
            assert found.rule == date_counts.RULE_MIDNIGHT
    days = [first + 997 * (row % 10) for row in range(battery.ROWS)]
    texts, numbers = _days_at_midnight(days)
    monkeypatch.setattr(date_counts, "REST_LEAST", 1)
    assert date_counts.asked_of(
        texts, numbers, taxonomy._needed(0.99, len(texts)), _median(sorted(numbers)), True,
        floor=11,
    ) is not None


def test_c2_money_amounts_and_lengths_of_time_are_not_asked(monkeypatch: pytest.MonkeyPatch) -> None:
    """The review of landing R4, item 7: four ordinary shapes the first build asked about, newly.

    Salaries and payments in cents and amounts to one decimal in Excel's
    five-figure band, a room charge in cents read as Epic days, and
    lengths of time kept as whole days of seconds or of milliseconds.
    Each is asked once its rule is put back as it was: rule A without its
    four figures of a day or its Epic days mostly whole, rule B without
    its year from the epoch or its thousand-day step.
    """
    names = (
        "salary_cents_45k", "payment_cents_20k", "room_charge_cents_62k", "glucose_area_1dp",
        "dose_total_1dp", "stay_seconds_whole_days", "gap_milliseconds_whole_days",
        "followup_seconds_whole_days",
    )

    def asked(name: str, draw: int) -> bool:
        texts = battery.ordinary(name, 1000, draw)
        numbers = [float(text) for text in texts]
        whole = all(value == int(value) for value in numbers)
        return date_counts.asked_of(
            texts, numbers, taxonomy._needed(0.99, len(texts)), _median(sorted(numbers)), whole,
            floor=11,
        ) is not None

    for name in names:
        assert not any(asked(name, draw) for draw in range(4)), name
    monkeypatch.setattr(date_counts, "DAY_TIME_PLACES", 0)
    assert asked("salary_cents_45k", 0) and asked("dose_total_1dp", 0)
    monkeypatch.undo()
    original = date_counts._text_holds

    def any_contacts(present: "list[str]", member: str, rule: str, needed: int, mark: str = ".") -> bool:
        if date_counts.TABLE[member].contacts:
            return sum(date_counts.counted(member, text, mark) is not None for text in present) >= needed
        return original(present, member, rule, needed, mark)

    monkeypatch.setattr(date_counts, "_text_holds", any_contacts)
    assert asked("room_charge_cents_62k", 0)
    monkeypatch.undo()
    monkeypatch.setattr(date_counts, "EPOCH_YEAR_DAYS", 0)
    assert asked("stay_seconds_whole_days", 0)
    monkeypatch.undo()
    # Whole days of milliseconds read as seconds stand every thousand days.
    monkeypatch.setattr(date_counts, "UNIT_STEP_DAYS", 10**18)
    assert asked("gap_milliseconds_whole_days", 0)


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
    answers.write_text(json.dumps(questions), encoding="utf-8", newline="\n")
    answered = tmp_path / "answered"
    typed = tmp_path / "typed"
    answered.mkdir()
    typed.mkdir()
    code, said = _exit_of(["profile", str(path), "--answers", str(answers), "--out-dir", str(answered), "--replace"])
    assert code == 0, said[-600:]
    # THE LINE THAT REPEATS THE RUN NAMES THE ANSWER AS ITS OPTION (mutant
    # M51: the repeat command dropping `--date-count`).
    assert "TO REPEAT THIS RUN WITHOUT THE QUESTIONS" in said
    assert "--date-count seen days-since-1960" in said
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


def test_c4_the_counted_route_never_calls_the_whole_share_pass(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The R4 design review, item 4: `_whole_enough` is stage 4 lane S2's, and quadratic.

    An Epic `*_DATE_REAL` column read as numbers takes that pass, which
    grows as the square of its rows; declared, it is drawn as dates and
    never reaches it. The undeclared run calling it is what keeps the
    count from being nought by accident.
    """
    shape = battery.BY_NAME["epic_real"]
    cells, _truth = battery.cells(shape, 300, 0)
    calls = [0]
    original = generation._whole_enough

    def counted(*arguments: object, **named: object) -> object:
        calls[0] += 1
        return original(*arguments, **named)  # type: ignore[arg-type]

    monkeypatch.setattr(generation, "_whole_enough", counted)
    _trip(tmp_path / "declared", cells, shape.system)
    assert calls[0] == 0
    path = _table(tmp_path / "plain", cells)
    folder = tmp_path / "plain"
    assert _exit_of(["profile", str(path), "--out-dir", str(folder), "--replace"])[0] == 0
    described = folder / "table-profile.json"
    assert json.loads(described.read_text(encoding="utf-8"))["columns"][0]["role"] == "continuous"
    assert _exit_of(["generate", str(described), "--seed", "0", "--out-dir", str(folder), "--replace"])[0] == 0
    assert calls[0] > 0


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


def test_c5_a_contact_number_rarer_than_the_line_leaves_the_source_whole(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Five `.03` cells are counted into the commonest contact number, and the source still meets its form.

    THE MUTANT: the form holding each cell to a contact number the census
    names, which the source's five cells are not, so the real table
    missed its own description.
    """
    draw = random.Random(3)
    cells: "list[str]" = []
    for row in range(1000):
        contact = "" if row < 850 else ".01" if row < 970 else ".02" if row < 995 else ".03"
        cells += [f"{65000 + draw.randrange(3000)}{contact}"]
    draw.shuffle(cells)
    trip = _trip(tmp_path, cells, "days-since-1840")
    assert trip["block"]["count_form"]["contacts"] == {"(none)": 855, "01": 120, "02": 25}
    assert trip["twin_exit"] == 0 and trip["real_exit"] == 0

    def named_only(form: "date_counts.CountForm", written: "date_counts.Written") -> bool:
        return date_counts.contact_word(written) in (form.contacts or {})

    monkeypatch.setattr(date_counts, "form_holds", named_only)
    out = tmp_path / "mutated"
    out.mkdir()
    assert _exit_of(["validate", str(trip["described"]), "--twin", str(trip["path"]), "--out-dir", str(out), "--replace"])[0] == 3


def test_c5_a_table_of_one_counted_column_is_counted_in_rows(tmp_path: pathlib.Path) -> None:
    """The population census reads each count's date: one counted column is a table of rows."""
    shape = battery.BY_NAME["unix_s"]
    cells, _truth = battery.cells(shape, 150, 0)
    trip = _trip(tmp_path, cells, shape.system)
    assert trip["block"]["n_present"] == 150


def test_c5_r_exponent_form_and_a_decimal_comma_round_trip(tmp_path: pathlib.Path) -> None:
    """Items 6 and 8: R's shorter form asked about undeclared, and both it and a comma for the point read and written back.

    Item 6 said Q3 never asked a column of milliseconds R wrote with an
    exponent on some cells (here about one in six). It is asked, offering
    the system that wrote it; with the exponent cells read as no count by
    the question's walk, it is not, and the round trip still holds.
    """
    draw = random.Random(6)
    cells: "list[str]" = []
    for _row in range(400):
        day = datetime.date(2016, 1, 1) + datetime.timedelta(days=draw.randrange(3653))
        milliseconds = (day - datetime.date(1970, 1, 1)).days * 86400000 + draw.choice((0, 0, 0, draw.randrange(86400) * 1000))
        form = date_counts.CountForm(0, True, 15, True, ".", None)
        cells += [date_counts.spelled_count(milliseconds, 1, form)]
    assert any("e+" in cell for cell in cells) and not all("e+" in cell for cell in cells)
    said = _q3(_block_of(tmp_path / "asked", cells))
    assert said is not None
    assert "milliseconds-since-1970" in [member for member, _first, _last in said.readings]
    trip = _trip(tmp_path / "r", cells, "milliseconds-since-1970")
    assert trip["block"]["count_form"]["exponent"] is True
    assert any("e+" in cell for cell in trip["twin"])
    assert trip["twin_exit"] == 0 and trip["real_exit"] == 0
    commas = [
        f"{45000 + draw.randrange(3000) + draw.randrange(86400) / 86400:.6f}".rstrip("0").rstrip(".").replace(".", ",")
        for _row in range(400)
    ]
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


@pytest.mark.parametrize("name", sorted(battery.COARSE))
def test_c4_figures_no_unit_keeps_are_refused_and_the_rest_written_back(
    tmp_path: pathlib.Path, name: str
) -> None:
    """The review of landing R4, item 2: the reading unit keeps every figure the column wrote, or reads none.

    One and two figures of a day step by 2.4 hours and 14.4 minutes,
    tenths and hundredths of a second by a tenth and a hundredth, and four
    figures of a day of moments off the minute by 8.64 seconds: settled to
    a unit at least the step, a count loses its figures, and settled
    finer the twin's own cells are rounded onto the column's coarser grid
    as they are written -- the first build's twin of one figure missed its
    own description, and its Unix tenths came back as whole seconds. Such a
    column is not read as counted dates (NF115) and is twinned as the
    numbers it reads, both files at exit 0. Four figures of a day at
    whole minutes and five at whole seconds are kept: read as dates, every
    source cell written back as itself.
    """
    system, _write, kept = battery.COARSE[name]
    cells = battery.coarse(name, battery.ROWS, 0)
    trip = _trip(tmp_path, cells, system)
    block = trip["block"]
    assert trip["twin_exit"] == 0 and trip["real_exit"] == 0
    if not kept:
        assert block["role"] != "datetime", name
        assert any(contract.COUNTED_NOT_READ_MARK in remark for remark in block["remarks"])
        return
    assert block["role"] == "datetime" and block["count_form"] is not None
    loaded = contract.load_profile(str(trip["described"]))
    facts = loaded.columns[0].facts
    assert isinstance(facts, contract.DatetimeFacts) and facts.count_form is not None
    unit = contract.counted_unit(facts)
    for cell in cells:
        written = date_counts.written_count(cell)
        assert written is not None
        numerator, denominator = date_counts.exact_value(written)
        moment = date_counts.moment_of(system, numerator, denominator, unit)
        assert moment is not None
        assert date_counts.written_for(system, moment, unit, facts.count_form) == cell


def test_c4_the_settled_unit_is_at_least_the_step(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path) -> None:
    """The first build's minute floor (mutant M52), and a figures check that holds everything.

    Settled to the minute, one figure of a day reads exactly -- 0.1 of a
    day is 144 minutes -- and its twin, drawn at the minute and rounded to
    2.4 hours as it is written, missed its own description. Put back, the
    column is read as dates again; so is a column of Unix tenths where the
    figures check holds every count.
    """
    assert date_counts.settled_unit("excel-1900", 1) == date_counts.DAY
    assert date_counts.settled_unit("excel-1900", 4) == date_counts.MINUTE
    assert date_counts.settled_unit("excel-1900", 6) == date_counts.SECOND
    assert date_counts.settled_unit("excel-1900", 10) == date_counts.MILLISECOND
    assert date_counts.settled_unit("seconds-since-1970", 1) == date_counts.SECOND
    original = date_counts.settled_unit

    def minute_floor(member: str, places: int) -> int:
        found = date_counts.TABLE[member]
        if places > 0 and found.unit >= date_counts.DAY and not found.contacts and places < 4:
            return date_counts.MINUTE
        return original(member, places)

    monkeypatch.setattr(date_counts, "settled_unit", minute_floor)
    block = _block_of(tmp_path / "floor", battery.coarse("excel_1dp", battery.ROWS, 0), "excel-1900")
    assert block["role"] == "datetime"
    monkeypatch.undo()
    monkeypatch.setattr(date_counts, "held_by_its_moment", lambda *arguments: True)
    block = _block_of(tmp_path / "held", battery.coarse("unix_s_1dp", battery.ROWS, 0), "seconds-since-1970")
    assert block["role"] == "datetime"


def test_c4_the_contact_numbers_are_spread_over_the_rows(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The review of landing R4, item 8: each half of the twin holds the census's share of each contact number.

    Dealt in rank order down the rows, the first build's twin of 100,000
    rows held no contact number in its first half at all. At 10,000 rows
    each half of the twin's dated cells is within one point of the
    census's share, and with the first build's dealing it is not.
    """
    shape = battery.BY_NAME["epic_real"]
    cells, _truth = battery.cells(shape, 10000, 0)

    def halves_off(twin: "list[str]", census: "dict[str, int]") -> float:
        words = [date_counts.contact_word(date_counts.written_count(cell)) for cell in twin if cell]  # type: ignore[arg-type]
        total = sum(census.values())
        worst = 0.0
        for half in (words[: len(words) // 2], words[len(words) // 2 :]):
            for word, count in census.items():
                worst = max(worst, abs(half.count(word) / len(half) - count / total) * 100)
        return worst

    trip = _trip(tmp_path / "head", cells, shape.system)
    census = trip["block"]["count_form"]["contacts"]
    assert census is not None and len(census) >= 2
    assert halves_off(trip["twin"], census) <= 1.0
    _dealt_down_the_rows(monkeypatch)
    trip = _trip(tmp_path / "mutant", cells, shape.system)
    assert halves_off(trip["twin"], census) > 1.0


@pytest.mark.parametrize(("writer", "name"), (("repr", "xl_dt15g"), ("repr", "xl_dt6"), ("pandas_point_zero", "xl_date")))
def test_c4_pandas_and_repr_spellings_round_trip(
    tmp_path: pathlib.Path, writer: str, name: str
) -> None:
    """`repr`'s shortest figures (mutant M47) and pandas' `45000.0` (mutant M49) written as their writer writes them.

    A column of Excel serials pandas wrote with `repr` is settled at the
    second or the minute its moments stand on, every source cell is
    written back as itself, and every twin cell is `repr`'s own spelling
    of its double -- not `%.17g`'s seventeen figures. A column of whole
    serials pandas wrote as `45000.0` keeps its one nought after the point
    in the twin, and the source meets its own form.
    """
    shape = battery.BY_NAME[name]
    cells = battery.written_by(writer, shape, battery.ROWS, 0)
    trip = _trip(tmp_path, cells, shape.system)
    assert trip["twin_exit"] == 0 and trip["real_exit"] == 0
    form = trip["block"]["count_form"]
    if writer == "repr":
        assert form["significant"] == 17
        assert trip["block"]["time_precision"] in ("second", "minute")
        assert all(cell == repr(float(cell)) for cell in trip["twin"] if cell)
    else:
        assert form["places"] == 1 and form["trimmed"] is False
        assert all(cell.endswith(".0") for cell in trip["twin"] if cell)
    loaded = contract.load_profile(str(trip["described"]))
    facts = loaded.columns[0].facts
    assert isinstance(facts, contract.DatetimeFacts) and facts.count_form is not None
    unit = contract.counted_unit(facts)
    for cell in cells:
        written = date_counts.written_count(cell)
        assert written is not None
        numerator, denominator = date_counts.exact_value(written)
        moment = date_counts.moment_of(shape.system, numerator, denominator, unit)
        assert moment is not None
        assert date_counts.written_for(shape.system, moment, unit, facts.count_form) == cell


def test_c5_a_placeholder_count_is_set_aside_whole_or_not(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mutant M12: Excel's count for 31 December 9999, and pandas' `2` for 1 January 1900.

    Each is counted as no value and written back as written: the twin
    holds as many of each spelling as the source, no ISO date stands in a
    column of numbers, and both files meet the description. With no
    placeholder day set aside the date role's own judgement withholds
    them under the ISO text it read, and the twin writes that text into
    the column.
    """
    shape = battery.BY_NAME["xl_date"]
    cells, _truth = battery.cells(shape, battery.ROWS, 0)
    for place in range(0, 1000, 50):
        cells[place] = "2958465"
    for place in range(25, 1000, 50):
        cells[place] = "2"
    trip = _trip(tmp_path / "head", cells, shape.system)
    assert trip["block"]["missing_by_source"] == {"2": 20, "2958465": 20}
    assert trip["twin"].count("2958465") == 20 and trip["twin"].count("2") == 20
    assert not [cell for cell in trip["twin"] if "-" in cell]
    assert trip["twin_exit"] == 0 and trip["real_exit"] == 0
    monkeypatch.setattr(date_counts, "declared_aside", lambda member: ())
    monkeypatch.setattr(date_counts, "placeholder_day_named", lambda moment, unit: "")
    path = _table(tmp_path / "mutant", cells)
    code, said = _exit_of(["profile", str(path), "--date-count", "seen", "excel-1900", "--out-dir", str(tmp_path / "mutant"), "--replace"])
    assert code == 0, said[-500:]
    block = json.loads((tmp_path / "mutant" / "table-profile.json").read_text(encoding="utf-8"))["columns"][0]
    assert block["missing_by_source"] != {"2": 20, "2958465": 20}


def test_c5_keep_value_does_not_reach_a_declared_columns_placeholder(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mutant M40: `--keep-value 2958465` beside `--date-count` leaves the count set aside.

    The first build rescued it, read it as 31 December 9999, and the date
    role withheld that day under its ISO text: the twin wrote
    `9999-12-31` twenty times into a column of numbers and the source
    missed its own description. A number kept that way is no word of the
    vocabulary the settings record, so the checker could not keep it too.
    """
    shape = battery.BY_NAME["xl_date"]
    cells, _truth = battery.cells(shape, battery.ROWS, 0)
    for place in range(0, 1000, 50):
        cells[place] = "2958465"
    trip = _trip(tmp_path / "head", cells, shape.system, "--keep-value", "2958465")
    assert trip["block"]["missing_by_source"] == {"2958465": 20}
    assert trip["twin"].count("2958465") == 20 and "9999-12-31" not in trip["twin"]
    assert trip["twin_exit"] == 0 and trip["real_exit"] == 0
    original = date_counts.declared_aside
    monkeypatch.setattr(
        date_counts, "declared_aside", lambda member: tuple(n for n in original(member) if n != 2958465)
    )
    monkeypatch.setattr(date_counts, "placeholder_day_named", lambda moment, unit: "")
    trip = _trip(tmp_path / "mutant", cells, shape.system, "--keep-value", "2958465")
    assert trip["real_exit"] == 3


def test_c5_a_declaration_reading_two_dates_decides_nothing(tmp_path: pathlib.Path) -> None:
    """Mutant M19: two different serials are read as dates, and the date rule does not take two values.

    The column is then read as if nothing had been declared and says so
    (NF115); without that the first build left a column of two dates on
    another role, and `generate` and `validate` stopped.
    """
    cells = ["45000" if row % 2 else "45001" for row in range(battery.ROWS)]
    trip = _trip(tmp_path, cells, "excel-1900")
    assert trip["block"]["role"] != "datetime"
    assert any(contract.COUNTED_NOT_READ_MARK in remark for remark in trip["block"]["remarks"])
    assert sorted(set(trip["twin"])) == ["45000", "45001"]
    assert trip["twin_exit"] == 0 and trip["real_exit"] == 0


def test_c5_the_census_of_contact_numbers_is_held_exactly(tmp_path: pathlib.Path) -> None:
    """Mutant M33: a twin of Epic days whose cells write no contact number misses `form.contacts`."""
    shape = battery.BY_NAME["epic_real"]
    cells, _truth = battery.cells(shape, battery.ROWS, 0)
    trip = _trip(tmp_path, cells, shape.system)
    assert trip["twin_exit"] == 0
    stripped = tmp_path / "stripped"
    assert _rewritten(trip, stripped, lambda cell: cell.split(".")[0]) == 3
    report = "\n".join(
        path.read_text(encoding="utf-8") for path in sorted((stripped / "check-changed").glob("*.txt"))
    )
    assert "form.contacts" in report


@pytest.mark.parametrize("noisy", (137, 5))
def test_c5_an_epic_day_with_a_binary64_tail_is_no_count(tmp_path: pathlib.Path, noisy: int) -> None:
    """The review of landing R4, item 3: `65053.010000000002` is a day and a binary64's tail.

    An Epic `*_DATE_REAL` exported with seventeen significant figures
    stopped `profile` with an internal fault once declared. Such a cell is
    no count: it stands to the date role's own line, so a column of them
    is read as it reads without the declaration and says so (NF115), and
    a column of five among a thousand is read as dates with five cells it
    could not read. Question Q3 does not offer the 1840 system for it.
    """
    shape = battery.BY_NAME["epic_real"]
    cells, truth = battery.cells(shape, battery.ROWS, 0)
    for place in range(noisy):
        day = int(battery.count_of(shape.system, truth[place * 7]))
        cells[place * 7] = f"{day + 0.01:.17g}"
    assert sum(len(cell.split(".")[1]) > 9 for cell in cells if "." in cell) == noisy
    trip = _trip(tmp_path, cells, shape.system)
    if noisy > 10:
        assert trip["block"]["role"] != "datetime"
        assert any(contract.COUNTED_NOT_READ_MARK in remark for remark in trip["block"]["remarks"])
        assert trip["twin_exit"] == 0
        said = _q3(_block_of(tmp_path / "asked", cells))
        assert said is None or "days-since-1840" not in [m for m, _f, _l in said.readings]
    else:
        # Read as dates beside five cells the date role could not read, which
        # the source meets. (Its twin writes those five as text stand-ins, as
        # every column of dates does with cells that are numbers, and so
        # misses `n_numeric` -- method G10.4's, not this landing's.)
        assert trip["block"]["role"] == "datetime" and trip["block"]["n_unparsed"] == noisy
        assert trip["real_exit"] == 0


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


def test_c6_the_years_are_the_published_rungs_said_another_way(tmp_path: pathlib.Path) -> None:
    """NF114 quotes the block's own rungs; the loader refuses other years.

    Twenty `0` cells among a thousand SAS days are the published low end.
    Each system's years are those of the outermost published rung that is
    a date of the column (`taxonomy.counted_edge_years`), and a description
    naming other years -- a year off, or the first build's, read off the
    heaped `0` as 1960 -- is refused (the review of landing R4, item 1).
    """
    shape = battery.BY_NAME["sas_days"]
    cells, _truth = battery.cells(shape, battery.ROWS, 0)
    block = _block_of(tmp_path, battery.heaped(shape, cells, "zero", 0.02))
    edges = taxonomy.published_ends(block)
    assert edges is not None and edges[0] == 0.0
    seen = 0
    for remark in block["remarks"]:
        if remark.form != taxonomy.REMARK_READ_AS_COUNTED_DATES:
            continue
        member = remark.arguments[0]
        years = taxonomy.counted_edge_years(block, member)
        assert years is not None and remark.arguments[1:] == years
        profile._counted_years_quote_the_published_edges(remark.arguments, block)
        first_build = (date_counts.years_of(member, edges[0]), date_counts.years_of(member, edges[1]))
        assert first_build != years
        for wrong in ((member,) + first_build, (member, years[0] - 1, years[1])):
            with pytest.raises(Exception):
                profile._counted_years_quote_the_published_edges(wrong, block)
        seen += 1
    assert seen >= 2


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
