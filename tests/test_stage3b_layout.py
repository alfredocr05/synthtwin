"""THE LAYOUT MEMBER'S GATE (stage 3b landing R2a, plan P4-D383): the date half.

Before this landing 60 of the 116 health-export spellings of the reach
audit were read as no date at all -- SAS, Stata, SPSS, HL7, REDCap's
hyphens, Oracle, DB2, PostgreSQL and SQL Server offsets -- and the twin
wrote made-up strings no code reading the real column could parse. One
closed-grammar member, the layout, now reads them, last in the format
walk, and the twin writes every cell back in its source's own spelling.
One clause per rule, each red on its own mutant (named beside it):

* L1 `test_l1_every_spelling_is_read` -- the thirty-nine spellings of
  `tests/layout_spellings.py` read under a layout with no cell left over
  (mutant: the member removed);
* L2 `test_l2_the_twin_writes_each_spelling_back` -- every twin cell at
  seeds 0 to 2 written exactly in the source's spelling and read by the
  person's own `strptime` format (mutants: the widths ignored; the offset
  spelled as ISO does);
* L3 `test_l3_the_twin_is_checked` -- a twin validates with nothing
  missed, a twin rewritten in ISO misses its format, and a twin read under
  another member that writes no cell the layout cannot read holds it by
  fit (mutants: an exact compare; a check that cannot fail);
* L4 `test_l4_no_member_reading_moves` -- columns the named members read
  keep their member, and a firmware column of `MM.DD.YY` versions naming a
  zero field stays text (mutants: the member put first; the dotted-version
  guard withdrawn from the layout);
* L5 `test_l5_columns_that_are_not_dates_keep_their_role` -- twenty-four
  made-up columns that are no dates keep their reading (mutant: no year
  band);
* L6 `test_l6_q5_asks_every_two_figure_year` -- question Q5 is asked of
  every column whose years are two figures and of no other, and 1930 read
  a column of 1930s birth dates right (mutant: it asks a four-figure
  year too);
* L7 `test_l7_the_choice_is_exact_on_the_line` -- a column on the line
  reads under the layout reaching it (mutant: candidates from one cell
  fewer than the line leaves room for).

And the design skeptic's items: the offset some cells omit (M2), the
unpadded dotted dates (M3) and the CLDR month words (M4) are among L1's
spellings; R1's two date questions see layout columns (M6); a layout
nothing in its cells can tell from a code is asked (m4); the day-order and
century remarks stand on layouts (m6); and the memo is bounded (m1).

And skeptic 1's repair round, each clause run against the mutant its
docstring names: a declared century reads every cell its two-figure member
read and says the person's window (item 1, with m6d); an offset on fewer
cells than the room is read, and the twin writes the offsets its class
count owes (item 2, G7.9b); a date spelled as a version is asked (item 3);
an older categorical description of layout dates is described again
(item 4, a stated limit); the evidence and the question say what the
column writes (item 5); and one clause for each rule no test turned red
(item 6): the choice memo's bound, lever b's pair reader, `--century`'s
two spellings, the weekday, the fourteen hours, the space-padded day read
and written, the runs asked, a day-first layout's evidence, R1's codes
with Q1, the per-column century and the readable band.

And skeptic 2's round, each clause run against the mutant its docstring
names: G7.9b writes no offset the census names (item 1); it reads each
cell's class once where nothing is owed and writes an offset only where
it settles one (item 2); a run whose few suffixes read as an offset no
census names is asked as the bare run is (item 3); and one clause for
each of the repair round's rules no test turned red (item 4): the
eighteen layouts that stand in for a two-figure member, the stand-ins
taken off the debt, the zulu word, the run with a fraction, the
hours-only and colon fields, the bound of the offer at 180 owed, the
numbers left at the line, and no offset beside a pool.
"""

import collections
import csv
import dataclasses
import datetime
import io
import json
import pathlib
import random
import re
import sys

import pytest

from synthtwin import (
    asking, contract, errors, generation, parsing, taxonomy, validation,
)
from tests import fixtures
from tests import layout_spellings as spellings

ROWS = 300
SEEDS = (0, 1, 2)
# The writer and the matcher as shipped, held before any mutant replaces them.
_WRITTEN = parsing.written_layout_date
_MATCHING_LAYOUT = taxonomy._matching_layout


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
    folder: pathlib.Path, cells: "list[str]", *flags: str, floor: int = 11
) -> "tuple[dict[str, object], pathlib.Path, dict[str, object]]":
    """Describe one column the way `synthtwin profile` does, at the floor given."""
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "real.csv"
    names, rows = fixtures.rows_at_the_floor("seen_at", cells)
    table.write_text(fixtures.rows_to_csv(names, rows), encoding="utf-8", newline="\n")
    assert _exit_of(
        ["profile", str(table), "--out-dir", str(folder), "--replace", "--smallest-group", str(floor)]
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


# -- L1: every spelling is read -----------------------------------------


@pytest.mark.parametrize("name", sorted(spellings.SPELLINGS))
def test_l1_every_spelling_is_read(name: str) -> None:
    """Before R2a none of these thirty-nine was a date."""
    cells = spellings.cells(name, ROWS)
    described = taxonomy.profile_column("seen_at", 1, cells, ROWS, taxonomy.Settings())
    details = described.details or {}
    assert described.role == taxonomy.ROLE_DATETIME, name
    assert parsing.is_layout_format(f"{details['format']}"), (name, details["format"])
    assert details["n_unparsed"] == 0, name


def test_l1_red_without_the_member(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(taxonomy, "_matching_layout", lambda present, settings, contradicted: None)
    cells = spellings.cells("sas_datetime20", ROWS)
    described = taxonomy.profile_column("seen_at", 1, cells, ROWS, taxonomy.Settings())
    assert described.role != taxonomy.ROLE_DATETIME


# -- L2: written back as written -------------------------------------------


@pytest.mark.parametrize("name", sorted(spellings.SPELLINGS))
def test_l2_the_twin_writes_each_spelling_back(tmp_path: pathlib.Path, name: str) -> None:
    """Every twin cell is the source's spelling and the person's format reads it."""
    _block, profile, _questions = _described(tmp_path, spellings.cells(name, ROWS))
    fmt = spellings.format_of(name)
    for seed in SEEDS:
        _twin_path, written = _twin(profile, seed)
        assert len(written) == ROWS, (name, seed)
        for cell in written:
            assert spellings.written_as_the_source(name, cell), (name, seed, cell)
            assert spellings.parses(cell, fmt), (name, seed, cell)


def test_l2_red_when_the_widths_are_ignored(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    name = "dutch_unpadded"
    _block, profile, _questions = _described(tmp_path, spellings.cells(name, ROWS))
    monkeypatch.setattr(
        parsing, "written_layout_date",
        lambda format_name, canonical, offset="", width="padded", figures=0: _WRITTEN(
            format_name, canonical, offset, "padded", figures
        ),
    )
    _twin_path, written = _twin(profile, 0)
    assert not all(spellings.written_as_the_source(name, cell) for cell in written)


def test_l2_red_when_the_offset_is_spelled_as_iso(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    name = "iso_offset_without_colon"
    _block, profile, _questions = _described(tmp_path, spellings.cells(name, ROWS))
    monkeypatch.setattr(
        parsing, "written_layout_date",
        lambda format_name, canonical, offset="", width="padded", figures=0: _WRITTEN(
            format_name.replace("{+HHMM}", "{+HH:MM}"), canonical, offset, width, figures
        ),
    )
    _twin_path, written = _twin(profile, 0)
    assert not any(spellings.written_as_the_source(name, cell) for cell in written)


# -- L3: checked ----------------------------------------------------------


@pytest.mark.parametrize(
    "name", ("sas_datetime20", "hl7_ts_fraction_offset", "dutch_unpadded", "british_sept_time")
)
def test_l3_the_twin_is_checked(tmp_path: pathlib.Path, name: str) -> None:
    """The twin validates; written again in ISO it misses its format."""
    _block, profile, _questions = _described(tmp_path, spellings.cells(name, ROWS))
    twin, written = _twin(profile, 0)
    code, _report = _validated(profile, twin)
    assert code == 0, name
    published = json.loads(profile.read_text(encoding="utf-8"))["columns"][0]["format"]
    items = parsing.layout_items(published)
    assert items is not None
    iso = []
    for cell in written:
        read = parsing.layout_reading(cell, items)
        assert read is not None, (name, cell)
        iso += [read[0][0:10] + ("T" + read[0][11:] if len(read[0]) > 10 else "")]
    other = twin.parent / "iso.csv"
    other.write_text(fixtures.rows_to_csv(["seen_at"], [[cell] for cell in iso]), encoding="utf-8", newline="\n")
    code, report = _validated(profile, other)
    assert code != 0, name
    assert "format.member" in report, name


def test_l3_a_layout_is_held_by_fit() -> None:
    """A twin read under another member holds the layout if the layout reads its every cell."""
    padded = ["2022-08-09", "2022-10-11", "2023-01-02"]
    check = validation._format_check("seen_on", "layout {YYYY}-{M}-{D}", "iso-date", padded)
    assert check.verdict == validation.HELD
    check = validation._format_check("seen_on", "layout {D}-{M}-{YYYY}", "layout {DD}-{MM}-{YYYY}", ["17-03-2023"])
    assert check.verdict == validation.HELD
    # ...and one cell the layout cannot read misses it.
    check = validation._format_check("seen_on", "layout {YYYY}-{M}-{D}", "iso-datetime", ["2022-08-09 10:00:00"])
    assert check.verdict == validation.MISSED


def test_l3_red_on_an_exact_compare(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(parsing, "is_layout_name", lambda name: False)
    check = validation._format_check("seen_on", "layout {YYYY}-{M}-{D}", "iso-date", ["2022-08-09"])
    assert check.verdict == validation.MISSED


def test_l3_red_on_a_check_that_cannot_fail(monkeypatch: pytest.MonkeyPatch) -> None:
    real = parsing.parse_datetime
    monkeypatch.setattr(
        parsing, "parse_datetime",
        lambda text, format_name: ("2022-08-09", "") if parsing.is_layout_name(format_name) else real(text, format_name),
    )
    check = validation._format_check("seen_on", "layout {YYYY}-{M}-{D}", "iso-datetime", ["2022-08-09 10:00:00"])
    assert check.verdict == validation.HELD


# -- L4: no member reading moves -----------------------------------------


_MEMBER_READ = {
    "iso-date": lambda m: m.strftime("%Y-%m-%d"),
    "iso-datetime": lambda m: m.strftime("%Y-%m-%d %H:%M:%S"),
    "month-first-date": lambda m: f"{m.month}/{m.day}/{m.year}",
    "day-first-date": lambda m: m.strftime("%d/%m/%Y"),
    "textual-day-first-date": lambda m: m.strftime("%d %b %Y"),
    "dotted-day-first-date": lambda m: m.strftime("%d.%m.%Y"),
    "two-digit-month-first-date": lambda m: m.strftime("%m/%d/%y"),
    "compact-date": lambda m: m.strftime("%Y%m%d"),
}


def _firmware(rows: int) -> "list[str]":
    """`MM.DD.YY` firmware versions, half a per cent naming a zero field."""
    draw = random.Random(41)
    found = []
    for _row in range(rows):
        month = draw.randrange(1, 13)
        day = draw.randrange(1, 29)
        if draw.random() < 0.005:
            day = 0
        found += [f"{month:02d}.{day:02d}.{draw.randrange(18, 25):02d}"]
    return found


@pytest.mark.parametrize("member", sorted(_MEMBER_READ))
def test_l4_no_member_reading_moves(member: str) -> None:
    cells = [_MEMBER_READ[member](moment) for moment in spellings.moments(ROWS, 7)]
    described = taxonomy.profile_column("seen_on", 1, cells, ROWS, taxonomy.Settings())
    assert (described.details or {})["format"] == member


def test_l4_the_firmware_column_stays_text() -> None:
    cells = _firmware(2000)
    described = taxonomy.profile_column("firmware", 1, cells, 2000, taxonomy.Settings())
    assert described.role != taxonomy.ROLE_DATETIME


def test_l4_red_when_the_layout_is_put_first(monkeypatch: pytest.MonkeyPatch) -> None:
    real = taxonomy._matching_date_format

    def layout_first(present, settings):
        found = _MATCHING_LAYOUT(present, settings, False)
        return found if found is not None else real(present, settings)

    monkeypatch.setattr(taxonomy, "_matching_date_format", layout_first)
    cells = [_MEMBER_READ["iso-date"](moment) for moment in spellings.moments(ROWS, 7)]
    described = taxonomy.profile_column("seen_on", 1, cells, ROWS, taxonomy.Settings())
    assert (described.details or {})["format"] != "iso-date"


def test_l4_red_without_the_version_guard(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(taxonomy, "_layout_guarded", lambda layout, contradicted: False)
    cells = _firmware(2000)
    described = taxonomy.profile_column("firmware", 1, cells, 2000, taxonomy.Settings())
    assert described.role == taxonomy.ROLE_DATETIME


# -- L5: columns that are not dates keep their role ----------------------


def _r(draw: random.Random, low: int, high: int) -> int:
    return draw.randrange(low, high)


_NOT_DATES = {
    "phone": lambda d: f"{_r(d, 200, 1000)}-{_r(d, 200, 1000)}-{_r(d, 0, 10000):04d}",
    "dotted_phone": lambda d: f"{_r(d, 200, 1000)}.{_r(d, 200, 1000)}.{_r(d, 0, 10000):04d}",
    "ssn_like": lambda d: f"{_r(d, 1, 900):03d}-{_r(d, 1, 100):02d}-{_r(d, 1, 10000):04d}",
    "zip_four": lambda d: f"{_r(d, 501, 99951):05d}-{_r(d, 0, 10000):04d}",
    "icd10": lambda d: f"{d.choice('EIJKMNRZ')}{_r(d, 0, 100):02d}.{_r(d, 0, 100)}",
    "version": lambda d: f"{_r(d, 0, 13)}.{_r(d, 0, 30)}.{_r(d, 0, 40)}",
    "padded_version": lambda d: f"{_r(d, 0, 13):02d}.{_r(d, 0, 32):02d}.{_r(d, 0, 100):02d}",
    "ratio": lambda d: f"{_r(d, 1, 20)}:{_r(d, 1, 20)}",
    "score": lambda d: f"{_r(d, 0, 16)}/15",
    "blood_pressure": lambda d: f"{_r(d, 90, 181)}/{_r(d, 50, 111)}",
    "fraction": lambda d: f"{_r(d, 1, 12)}/{_r(d, 2, 13)}",
    "range": lambda d: (lambda a: f"{a}-{a + _r(d, 1, 50)}")(_r(d, 0, 200)),
    "dose_schedule": lambda d: f"{_r(d, 0, 4)}-{_r(d, 0, 3)}-{_r(d, 0, 4)}",
    "id12": lambda d: f"{_r(d, 10 ** 11, 10 ** 12)}",
    "id14": lambda d: f"{_r(d, 10 ** 13, 10 ** 14)}",
    "accession": lambda d: f"{_r(d, 2015, 2025)}-{_r(d, 1, 400):03d}",
    "lot_four_figures": lambda d: f"{_r(d, 1, 13)}-{_r(d, 1, 29)}-{_r(d, 1000, 10000)}",
    "date_sequence": lambda d: f"2023{_r(d, 1, 13):02d}{_r(d, 1, 29):02d}{_r(d, 0, 100):04d}",
    "ndc": lambda d: f"{_r(d, 0, 100000):05d}-{_r(d, 0, 10000):04d}-{_r(d, 0, 100):02d}",
    "ipv4": lambda d: f"10.{_r(d, 0, 256)}.{_r(d, 0, 256)}.{_r(d, 1, 255)}",
    "gleason": lambda d: f"{_r(d, 3, 6)}+{_r(d, 3, 6)}",
    "acuity": lambda d: f"20/{d.choice([20, 25, 30, 40, 50, 60, 70, 80, 100, 200])}",
    "part_number": lambda d: f"{d.choice('ABCDEFG')}{d.choice('KLMNP')}-{_r(d, 0, 10000):04d}-{d.choice('XYZ')}",
    "lot_years_far": lambda d: f"{_r(d, 1, 13)}-{_r(d, 1, 29)}-{_r(d, 3000, 10000)}",
}


def _not_a_date(name: str, rows: int = 1000) -> "list[str]":
    draw = random.Random(sum(ord(letter) for letter in name))
    return [_NOT_DATES[name](draw) for _row in range(rows)]


@pytest.mark.parametrize("name", sorted(_NOT_DATES))
def test_l5_columns_that_are_not_dates_keep_their_role(name: str) -> None:
    cells = _not_a_date(name)
    described = taxonomy.profile_column(name, 1, cells, len(cells), taxonomy.Settings())
    assert described.role != taxonomy.ROLE_DATETIME, (name, (described.details or {}).get("format"))


def test_l5_red_without_the_year_band(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(parsing, "LAYOUT_LAST_YEAR", 9999)
    cells = _not_a_date("lot_years_far")
    described = taxonomy.profile_column("lot", 1, cells, len(cells), taxonomy.Settings())
    assert described.role == taxonomy.ROLE_DATETIME


# -- L6: question Q5, of every two-figure year and of no other ----------


def _q5_asked(questions: "dict[str, object]") -> bool:
    asked = questions["asked"]
    assert isinstance(asked, list)
    return any(entry["read_as_now"] == asking.ANSWER_CENTURY_POSIX for entry in asked)


def _births(rows: int) -> "list[str]":
    draw = random.Random(1930)
    return [
        f"{draw.randrange(1, 13):02d}/{draw.randrange(1, 29):02d}/{draw.randrange(30, 99):02d}"
        for _row in range(rows)
    ]


@pytest.mark.parametrize("name", spellings.TWO_FIGURE_YEARS)
def test_l6_q5_asks_every_two_figure_year(tmp_path: pathlib.Path, name: str) -> None:
    _block, _profile, questions = _described(tmp_path, spellings.cells(name, ROWS))
    assert _q5_asked(questions), name


def test_l6_q5_asks_no_four_figure_year(tmp_path: pathlib.Path) -> None:
    _block, _profile, questions = _described(tmp_path, spellings.cells("sas_datetime20", ROWS))
    assert not _q5_asked(questions)


def test_l6_an_answer_of_1930_reads_the_birth_dates_right(tmp_path: pathlib.Path) -> None:
    cells = _births(ROWS)
    block, profile, questions = _described(tmp_path / "asked", cells)
    assert block["format"] == "two-digit-month-first-date"
    assert _q5_asked(questions)
    entries = questions["asked"]
    assert isinstance(entries, list)
    for entry in entries:
        if entry["read_as_now"] == asking.ANSWER_CENTURY_POSIX:
            entry["your_answer"] = asking.ANSWER_CENTURY_1930
    answers = tmp_path / "answers.json"
    answers.write_text(json.dumps(questions), encoding="utf-8", newline="\n")
    block, profile, questions = _described(tmp_path / "answered", cells, "--answers", str(answers))
    assert block["format"] == "layout {MM}/{DD}/{YY1930}"
    assert not _q5_asked(questions)
    read = [parsing.parse_datetime(cell, f"{block['format']}") for cell in cells]
    assert all(found is not None and "1930" <= found[0][0:4] <= "1999" for found in read)
    twin, _written = _twin(profile, 0)
    assert _validated(profile, twin)[0] == 0


def test_l6_red_when_q5_asks_a_four_figure_year(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(parsing, "layout_two_figure_year", lambda name: parsing.CENTURY_DEFAULT_FIRST_YEAR)
    document = {
        "columns": [{"name": "seen_at", "role": "datetime", "format": "layout {DD}{MON}{YYYY}"}],
        "settings": {"small_cell_floor": 11},
    }
    assert asking.century_questions(document)


# -- L7: the choice is exact on the line ---------------------------------


def _on_the_line() -> "list[str]":
    """1,000 cells, 990 SAS dates and ten other texts first: the layout reaches the line exactly."""
    sas = spellings.cells("sas_date9", 990, seed=9)
    return [f"note {place}" for place in range(10)] + sas


def test_l7_the_choice_is_exact_on_the_line() -> None:
    cells = _on_the_line()
    described = taxonomy.profile_column("seen_on", 1, cells, len(cells), taxonomy.Settings())
    assert (described.details or {}).get("format") == "layout {DD}{MON}{YYYY}"
    assert (described.details or {}).get("n_unparsed") == 10


def test_l7_red_on_one_seed_fewer(monkeypatch: pytest.MonkeyPatch) -> None:
    real = taxonomy._layout_candidates
    monkeypatch.setattr(
        taxonomy, "_layout_candidates",
        lambda counted, room, contradicted, window: real(counted, room - 1, contradicted, window),
    )
    cells = _on_the_line()
    described = taxonomy.profile_column("seen_on", 1, cells, len(cells), taxonomy.Settings())
    assert (described.details or {}).get("format") != "layout {DD}{MON}{YYYY}"


# -- the design skeptic's items --------------------------------------------


def test_r1_question_two_sees_a_layout_column() -> None:
    """M6: R1's question on a few repeated codes reads the rest through the layout."""
    counted = taxonomy._spelling_rows(spellings.cells("sas_date9", 970) + ["UNK"] * 30)
    rest = dict(counted)
    del rest["UNK"]
    found = taxonomy.reading_of_the_rest(rest, taxonomy.Settings(), 1000)
    assert found is not None and found[0] == "layout {DD}{MON}{YYYY}"


def test_r1_question_one_sees_a_month_first_layout(tmp_path: pathlib.Path) -> None:
    """M6 and the R2 design: a hyphenated date whose every day is 12 or less is asked its order."""
    draw = random.Random(12)
    cells = [f"{draw.randrange(1, 13):02d}-{draw.randrange(1, 13):02d}-2023" for _row in range(ROWS)]
    block, _profile, questions = _described(tmp_path, cells)
    assert block["format"] == "layout {MM}-{DD}-{YYYY}"
    asked = [entry for entry in questions["about_your_file"] if entry["read_as_now"] == asking.ANSWER_MONTH_FIRST]
    assert asked


def test_a_low_evidence_layout_is_asked(tmp_path: pathlib.Path) -> None:
    """m4: three numbers on a hyphen with a two-figure year are read as dates and asked."""
    block, _profile, questions = _described(
        tmp_path, [f"{place % 9 + 1}-{place % 20 + 1}-{place % 40 + 10}" for place in range(ROWS)]
    )
    assert block["format"] == "layout {M}-{D}-{YY}"
    asked = [entry for entry in questions["asked"] if entry["read_as_now"] == asking.ANSWER_KEEP]
    assert asked and {"keep", "code", "identifier"} <= {choice["answer"] for choice in asked[0]["answers_you_can_give"]}


def test_layouts_say_their_guesses(tmp_path: pathlib.Path) -> None:
    """m6: a month-first layout says its order, and a two-figure year its century."""
    block, _profile, _questions = _described(tmp_path / "order", spellings.cells("redcap_mdy_hyphen", ROWS))
    assert taxonomy.rendered(taxonomy.REMARK_MONTH_FIRST, ()) in block["remarks"]
    block, _profile, _questions = _described(tmp_path / "century", spellings.cells("oracle_dd_mon_rr", ROWS))
    assert taxonomy.rendered(taxonomy.REMARK_TWO_DIGIT_YEAR, ()) in block["remarks"]
    assert block["detection_evidence"].endswith("written as 17-MAR-24")


def test_the_memo_is_bounded(monkeypatch: pytest.MonkeyPatch) -> None:
    """m1: each different text is read once, the memos keep at most their bound, and say the same past it.

    Counted by the readings taken: with no bound in reach a layout column's
    census reads each of its different texts once; held to three texts,
    it reads those three once and every other cell each time it stands,
    which is a memo of three; and the reading and the census are the same
    either way. Mutant, run: the census reads every cell (no memo), and
    the first count is the cells, not the texts.
    """
    cells = spellings.cells("sas_datetime20", 400)
    cells = cells + cells
    whole = taxonomy._matching_layout(cells, taxonomy.Settings(), False)
    assert whole is not None
    texts: "list[str]" = []
    for cell in whole[2]:
        if cell not in texts:
            texts += [cell]
    calls: "list[str]" = []
    shipped = parsing.layout_reading

    def counted(text: str, items: "tuple[tuple[str, str], ...]") -> object:
        nonlocal calls
        calls += [text]
        return shipped(text, items)

    monkeypatch.setattr(parsing, "layout_reading", counted)
    census = taxonomy._layout_census(whole[0], whole[2])
    assert len(calls) == len(texts) < len(whole[2])
    calls = []
    monkeypatch.setattr(taxonomy, "LAYOUT_MEMO_TEXTS", 3)
    assert taxonomy._layout_census(whole[0], whole[2]) == census
    others = sum(1 for cell in whole[2] if cell not in texts[0:3])
    assert len(calls) == 3 + others
    bounded = taxonomy._matching_layout(cells, taxonomy.Settings(), False)
    assert bounded is not None and whole[0:4] == bounded[0:4]


def test_ly1_admits_only_layouts_the_grammar_makes() -> None:
    """m9: two flexible fields side by side compile, and are no layout."""
    assert parsing.compiled_layout("{M}{D}{YYYY}") is not None
    assert not parsing.is_layout_format("layout {M}{D}{YYYY}")
    assert parsing.is_layout_format("layout {DD}{MON}{YYYY}:{HH}:{MI}:{SS}")
    assert not parsing.is_layout_format("layout " + "{DD}-" * 20 + "{MON}{YYYY}")
    assert "LY1" in contract.INVARIANTS


# -- skeptic 1's repair round (the report's item numbers) -------------------


def _births_padded(rows: int) -> "list[str]":
    """`MM/DD/YY` births of 1935 to 2004, some written with a space round them.

    The first four cells -- every row the choice may draw its candidates
    from at 300 rows, where the line leaves room for three -- end in a
    space, and every fiftieth from the eighth on starts with one: the two
    shapes skeptic 1 measured (3 per cent trailing, 0.5 per cent leading).
    """
    draw = random.Random(1935)
    found: "list[str]" = []
    for place in range(rows):
        cell = (
            f"{draw.randrange(1, 13):02d}/{draw.randrange(1, 29):02d}/"
            f"{draw.randrange(1935, 2005) % 100:02d}"
        )
        if place < 4:
            cell = cell + " "
        elif place % 50 == 7:
            cell = " " + cell
        found += [cell]
    return found


def test_item1_a_declared_century_reads_every_cell_its_member_read(tmp_path: pathlib.Path) -> None:
    """Item 1: the answer to Q5 changes the century and nothing else.

    The member reads every cell, its spaces set aside; answered 1930, the
    column stays a column of dates read whole in 1930 to 2029, says the
    person's window in NF112 and not the POSIX one of NF42 (m6d), and its
    twin validates. Mutants, run: the layout that stands in for the
    member trims nothing (the column falls to free text); its candidates
    taken from the untrimmed texts (no candidate at all); NF112 replaced
    by NF42's sentence.
    """
    cells = _births_padded(ROWS)
    block, _profile, _questions = _described(tmp_path / "posix", cells)
    assert block["format"] == "two-digit-month-first-date" and block["n_unparsed"] == 0
    block, profile, _questions = _described(tmp_path / "1930", cells, "--century", "seen_at=1930")
    assert block["role"] == taxonomy.ROLE_DATETIME
    assert block["format"] == "layout {MM}/{DD}/{YY1930}"
    assert block["n_unparsed"] == 0
    read = [parsing.parse_datetime(cell, f"{block['format']}") for cell in cells]
    assert all(found is not None and "1930" <= found[0][0:4] <= "2029" for found in read)
    assert taxonomy.rendered(taxonomy.REMARK_CENTURY_DECLARED, (1930,)) in block["remarks"]
    assert taxonomy.rendered(taxonomy.REMARK_TWO_DIGIT_YEAR, ()) not in block["remarks"]
    twin, _written = _twin(profile, 0)
    assert _validated(profile, twin)[0] == 0


def test_item1_red_when_the_layout_trims_nothing(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(parsing, "_LAYOUTS_READ_AS_MEMBERS", {})
    block, _profile, _questions = _described(
        tmp_path, _births_padded(ROWS), "--century", "seen_at=1930"
    )
    assert block["role"] != taxonomy.ROLE_DATETIME or block["n_unparsed"] > 0


def test_item1_only_a_member_shape_in_a_declared_window_trims() -> None:
    """A layout no member reads, or one read in the POSIX window, still reads a cell whole."""
    assert parsing.layout_sets_spaces_aside("layout {M}/{D}/{YY1930}")
    assert parsing.layout_sets_spaces_aside("layout {DD}.{MM}.{YY1900}")
    assert not parsing.layout_sets_spaces_aside("layout {M}/{D}/{YY}")
    assert not parsing.layout_sets_spaces_aside("layout {DD}-{MON}-{YY1930}")
    assert parsing.parse_datetime(" 17-MAR-24", "layout {DD}-{MON}-{YY1930}") is None
    assert parsing.parse_datetime("03/17/24 ", "layout {MM}/{DD}/{YY1930}") == ("2024-03-17", "")


def test_item1_the_unreached_century_says_only_what_the_run_took() -> None:
    said = errors.the_century_declaration_did_not_reach("seen_at", "free_text")
    assert "no two-figure year" not in said
    assert "did not read it as dates whose years are written with two figures" in said


def _hl7_with_offsets(rows: int, worn: int, seed: int = 31) -> "list[str]":
    """HL7 stamps to the second, ``worn`` interior ones ending in an offset."""
    cells = [moment.strftime("%Y%m%d%H%M%S") for moment in spellings.moments(rows, seed)]
    draw = random.Random(seed)
    for place in draw.sample(range(1, rows - 1), worn):
        cells[place] = cells[place] + draw.choice(("-0400", "-0500"))
    return cells


def test_item2_an_offset_on_fewer_cells_than_the_room_is_read() -> None:
    """Item 2: two stamps of 300 wear an offset, under the room of three, and read.

    Mutant, run: the texts a layout that reached the line missed are not
    handed on, so the offset-free layout reads 298 and the two are
    stand-ins.
    """
    cells = _hl7_with_offsets(ROWS, 2)
    described = taxonomy.profile_column("seen_at", 1, cells, ROWS, taxonomy.Settings())
    details = described.details or {}
    assert details["format"] == "layout {YYYY}{MM}{DD}{HH}{MI}{SS}{+HHMM?}"
    assert details["n_unparsed"] == 0


def test_item2_the_twin_writes_the_offsets_its_class_count_owes(tmp_path: pathlib.Path) -> None:
    """Item 2 and G7.9b: the census counts the two offsets into `(none)`, the twin still wears two.

    Mutant, run: the pass withdrawn, and every twin cell is a number,
    missing `counts.n_numeric` and `counts.n_not_numeric`.
    """
    block, profile, _questions = _described(tmp_path, _hl7_with_offsets(ROWS, 2))
    assert block["utc_offsets"] == {"(none)": ROWS}
    assert block["n_not_numeric"] == 2
    for seed in SEEDS:
        twin, written = _twin(profile, seed)
        assert sum(1 for cell in written if not cell.isdigit()) == 2, seed
        assert _validated(profile, twin)[0] == 0, seed


def test_item3_a_date_spelled_as_a_version_is_asked(tmp_path: pathlib.Path) -> None:
    """Item 3: `1.12.2024` is read as a date and asked whether it is one.

    Mutant, run: `layout_low_evidence` without its dotted clause, and the
    column is asked its order alone.
    """
    assert parsing.layout_low_evidence("layout {M}.{D}.{YYYY}") == "."
    assert parsing.layout_low_evidence("layout {D}.{M}.{YYYY}") == "."
    assert parsing.layout_low_evidence("layout {DD}.{MM}.{YYYY} {HH}:{MI}") is None
    versions = [f"{major}.{minor}.2024" for major in range(1, 4) for minor in range(1, 13)] * 3
    block, _profile, questions = _described(tmp_path, versions)
    assert block["format"] == "layout {M}.{D}.{YYYY}"
    asked = [entry for entry in questions["asked"] if entry["read_as_now"] == asking.ANSWER_KEEP]
    assert asked
    assert {"keep", "code", "identifier"} <= {
        choice["answer"] for choice in asked[0]["answers_you_can_give"]
    }
    assert "version numbers" in asked[0]["what_synthtwin_saw"]


def _sas_days(rows: int, days: int) -> "list[str]":
    """SAS `DATE9.` cells over ``days`` different days."""
    draw = random.Random(25)
    names = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")
    chosen = [f"{day + 1:02d}{names[day % 12]}2023" for day in range(days)]
    return [draw.choice(chosen) for _row in range(rows)]


def test_item4_an_older_categorical_description_of_layout_dates_is_described_again(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Item 4, a stated limit (plan P4-D383): describe the table again.

    A description made before R2a -- made here as that tree made it, with
    no layout member -- reads 1,000 SAS dates over 25 days as categories.
    The layout member reads its unchanged twin as dates, so checking the
    twin against that description misses `axes.role`; describing the
    table again reads the dates, and that twin passes.
    """
    cells = _sas_days(1000, 25)
    monkeypatch.setattr(taxonomy, "_matching_layout", lambda present, settings, contradicted: None)
    block, older, _questions = _described(tmp_path / "older", cells)
    assert block["role"] == "categorical"
    monkeypatch.undo()
    twin, _written = _twin(older, 0)
    code, report = _validated(older, twin)
    assert code == 3
    assert "axes.role [universal.role]: MISSED" in report
    block, again, _questions = _described(tmp_path / "again", cells)
    assert block["role"] == taxonomy.ROLE_DATETIME
    twin, _written = _twin(again, 0)
    assert _validated(again, twin)[0] == 0


def test_item5_a_layout_is_shown_as_its_column_writes_it() -> None:
    """Item 5: a flexible field is shown unpadded; rule LY1's sample keeps its padding."""
    assert parsing.layout_example("layout {D}.{M}.{YYYY}") == "17.3.2024"
    assert parsing.layout_example("layout {YYYY}-{M}-{D}") == "2024-3-17"
    assert parsing.layout_example("layout {DD}{MON}{YYYY}") == "17MAR2024"
    assert parsing.is_layout_format("layout {D}.{M}.{YYYY}")
    assert parsing.is_layout_format("layout {YYYY}-{M}-{D}")


def test_item5_the_question_speaks_of_the_values_that_read_at_the_layout_width() -> None:
    """Item 5: the shape names the layout's own width and only the cells it reads."""
    block: "dict[str, object]" = {
        "name": "seen_at", "role": "datetime", "format": "layout {YYYY}{MM}{DD}{HH}{MI}",
    }
    question = asking._layout_question(block, ["202303171405", "20230317140509-0400"], 11)
    assert question is not None
    assert "12 characters wide" in question.shape
    assert "the values that read as dates" in question.shape
    block["format"] = "layout {M}-{D}-{YY}"
    question = asking._layout_question(block, ["3-12-45", "21B-4-17"], 11)
    assert question is not None
    assert "every value" not in question.shape and "every one" not in question.shape


# -- item 6: one clause per rule no test turned red ----------------------


def test_m1m_the_choice_memo_is_bounded(monkeypatch: pytest.MonkeyPatch) -> None:
    """The choice's own memo keeps at most its bound, and reads the same past it.

    800 cells, 400 texts each twice: held to three texts, the final pass
    reads the three once and every other text at each of its two cells,
    397 readings more than with no bound in reach. Mutant, run: the memo
    unbounded, and the count does not move.
    """
    cells = spellings.cells("sas_datetime20", 400)
    cells = cells + cells
    calls: "list[str]" = []
    shipped = parsing.layout_reading

    def counted(text: str, items: "tuple[tuple[str, str], ...]") -> object:
        nonlocal calls
        calls += [text]
        return shipped(text, items)

    monkeypatch.setattr(parsing, "layout_reading", counted)
    whole = taxonomy._matching_layout(cells, taxonomy.Settings(), False)
    unbounded = len(calls)
    calls = []
    monkeypatch.setattr(taxonomy, "LAYOUT_MEMO_TEXTS", 3)
    bounded = taxonomy._matching_layout(cells, taxonomy.Settings(), False)
    assert whole is not None and bounded is not None and whole[0:4] == bounded[0:4]
    assert len(calls) - unbounded == len(set(cells)) - 3


def test_lbr_a_slashed_pair_missing_exactly_its_room_is_weighed() -> None:
    """Lever b's pair reader stops only past the room, never on it.

    990 month-first dates whose days pass twelve, beside ten notes: the
    month-first reading misses exactly the ten the line leaves room for.
    Mutant, run: `_reads_within` stops one miss early, the pair is
    dropped, and the layout takes the column.
    """
    draw = random.Random(990)
    cells = [
        f"{draw.randrange(1, 13)}/{draw.randrange(13, 29)}/2023" for _row in range(990)
    ] + [f"note {place}" for place in range(10)]
    described = taxonomy.profile_column("seen_on", 1, cells, len(cells), taxonomy.Settings())
    details = described.details or {}
    assert details["format"] == "month-first-date"
    assert details["n_unparsed"] == 10


def _births_table(folder: pathlib.Path, name: str) -> pathlib.Path:
    """`MM/DD/YY` births under one column name of the caller's."""
    folder.mkdir(parents=True, exist_ok=True)
    names, rows = fixtures.rows_at_the_floor(name, _births(ROWS))
    table = folder / "real.csv"
    table.write_text(fixtures.rows_to_csv(names, rows), encoding="utf-8", newline="\n")
    return table


def test_clic_a_column_named_with_an_equals_sign_takes_its_century(tmp_path: pathlib.Path) -> None:
    """`--century` splits at its LAST equals sign. Mutant, run: split at the first."""
    table = _births_table(tmp_path, "a=b")
    assert _exit_of(
        ["profile", str(table), "--out-dir", str(tmp_path), "--replace", "--century", "a=b=1930"]
    ) == 0
    document = json.loads((tmp_path / "real-profile.json").read_text(encoding="utf-8"))
    assert document["settings"]["century_windows"] == [["a=b", 1930]]
    assert document["columns"][0]["format"] == "layout {MM}/{DD}/{YY1930}"


def test_cliw_1969_is_the_window_that_stands_and_declares_nothing(tmp_path: pathlib.Path) -> None:
    """`--century NAME=1969` takes back an earlier window. Mutant, run: stored as one."""
    block, profile, _questions = _described(
        tmp_path, _births(ROWS), "--century", "seen_at=1930", "--century", "seen_at=1969"
    )
    document = json.loads(profile.read_text(encoding="utf-8"))
    assert document["settings"]["century_windows"] == []
    assert block["format"] == "two-digit-month-first-date"


def test_wkd_a_weekday_is_read_only_beside_its_own_date() -> None:
    """17 March 2024 was a Sunday. Mutant, run: the weekday not checked."""
    items = parsing.compiled_layout("{Dy}, {DD} {Mon} {YYYY}")
    assert items is not None
    assert parsing.layout_reading("Sun, 17 Mar 2024", items) is not None
    assert parsing.layout_reading("Fri, 17 Mar 2024", items) is None


def test_off14_an_offset_past_fourteen_hours_is_not_read() -> None:
    """Mutant, run: any offset of two figures of hours read."""
    items = parsing.compiled_layout("{YYYY}-{MM}-{DD}T{HH}:{MI}:{SS}{+HH:MM}")
    assert items is not None
    assert parsing.layout_reading("2024-03-17T14:05:00+14:00", items) is not None
    assert parsing.layout_reading("2024-03-17T14:05:00-12:00", items) is not None
    assert parsing.layout_reading("2024-03-17T14:05:00+14:30", items) is None
    assert parsing.layout_reading("2024-03-17T14:05:00+15:00", items) is None


_SPACED_DAY = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (?: [1-9]|[12]\d|3[01]) \d{4}"


def test_spd_a_space_padded_day_reads_no_zero() -> None:
    """`{_D}` reads `Mar  7 2024` and not `Mar 07 2024`. Mutant, run: the zero read."""
    items = parsing.compiled_layout("{Mon} {_D} {YYYY}")
    assert items is not None
    assert parsing.layout_reading("Mar  7 2024", items) is not None
    assert parsing.layout_reading("Mar 17 2024", items) is not None
    assert parsing.layout_reading("Mar 07 2024", items) is None


def test_w_d_the_twin_writes_a_space_padded_day_with_its_space(tmp_path: pathlib.Path) -> None:
    """SQL Server's `Mon dd yyyy`, read and written back whole. Mutant, run: zero-padded."""
    items = parsing.compiled_layout("{Mon} {_D} {YYYY}")
    assert items is not None and parsing.layout_cell(items, "2024-03-07") == "Mar  7 2024"
    names = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
    cells = [
        f"{names[moment.month - 1]} {moment.day:>2d} {moment.year}"
        for moment in spellings.moments(ROWS, 9)
    ]
    block, profile, _questions = _described(tmp_path, cells)
    assert block["format"] == "layout {Mon} {_D} {YYYY}"
    twin, written = _twin(profile, 0)
    assert all(re.fullmatch(_SPACED_DAY, cell) for cell in written)
    assert _validated(profile, twin)[0] == 0


def test_low_runs_of_twelve_and_fourteen_figures_are_asked(tmp_path: pathlib.Path) -> None:
    """A run an order number writes alike is asked, at its own width. Mutant, run: not asked."""
    for name, width in (("hl7_ts12", 12), ("hl7_ts14", 14)):
        _block, _profile, questions = _described(tmp_path / name, spellings.cells(name, ROWS))
        asked = [entry for entry in questions["asked"] if entry["read_as_now"] == asking.ANSWER_KEEP]
        assert asked, name
        assert f"{width} characters wide" in asked[0]["what_synthtwin_saw"], name
        assert {"keep", "code", "identifier"} <= {
            choice["answer"] for choice in asked[0]["answers_you_can_give"]
        }


def test_evd_a_day_first_layout_says_what_decided_it(tmp_path: pathlib.Path) -> None:
    """NF36 on a layout read day first. Mutant, run: the layout's evidence never stands."""
    block, _profile, _questions = _described(tmp_path, spellings.cells("dutch_unpadded", ROWS))
    assert block["format"] == "layout {D}-{M}-{YYYY}"
    assert any("read day first, which parses" in remark for remark in block["remarks"])


def test_dcs_a_month_first_layout_with_codes_is_asked_its_order_too(tmp_path: pathlib.Path) -> None:
    """R1's code question joined by Q1 on a layout. Mutant, run: the order not asked."""
    draw = random.Random(33)
    cells = [
        "UNK"
        if place % 33 == 0
        else f"{draw.randrange(1, 13):02d}-{draw.randrange(1, 13):02d}-{draw.randrange(2015, 2024)}"
        for place in range(1000)
    ]
    _block, _profile, questions = _described(tmp_path, cells)
    coded = [
        entry
        for entry in questions["asked"]
        if asking.ANSWER_NO_DATE in [choice["answer"] for choice in entry["answers_you_can_give"]]
    ]
    assert [entry["column"] for entry in coded] == ["seen_at"]
    order = [
        entry for entry in questions["about_your_file"] if entry["column"] == asking.DAY_FIRST_SUBJECT
    ]
    assert order and "'seen_at'" in order[0]["what_synthtwin_saw"]


def test_narr_a_century_is_read_only_in_its_own_column() -> None:
    """Mutant, run: every column given the declared window."""
    settings = taxonomy.Settings(century_windows=(("born_on", 1930),))
    assert taxonomy.century_window_of(taxonomy.for_the_column(settings, "born_on")) == 1930
    assert taxonomy.century_window_of(taxonomy.for_the_column(settings, "seen_on")) == 0


def test_band_a_layout_writes_back_only_the_years_it_reads(tmp_path: pathlib.Path) -> None:
    """The readable band of a layout: its year band, or its window. Mutant, run: any year.

    Oracle `DD-MON-RR` births of 1935 to 2004 answered 1930: the twin's
    tails stay in 1930 to 2029, so every cell reads back in the century
    its description says, and the twin validates.
    """
    first, last = parsing.readable_days("layout {DD}-{MON}-{YY1930}")
    assert (first, last) == (
        parsing.days_from_civil(1930, 1, 1), parsing.days_from_civil(2029, 12, 31)
    )
    first, last = parsing.readable_days("layout {DD}{MON}{YYYY}")
    assert (first, last) == (
        parsing.days_from_civil(1800, 1, 1), parsing.days_from_civil(2299, 12, 31)
    )
    draw = random.Random(12)
    names = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")
    cells = [
        f"{draw.randrange(1, 29):02d}-{names[draw.randrange(12)]}-{draw.randrange(1935, 2005) % 100:02d}"
        for _row in range(ROWS)
    ]
    block, profile, _questions = _described(tmp_path, cells, "--century", "seen_at=1930")
    assert block["format"] == "layout {DD}-{MON}-{YY1930}"
    twin, _written = _twin(profile, 0)
    assert _validated(profile, twin)[0] == 0


def test_item2_a_repeated_text_is_never_paid_on(tmp_path: pathlib.Path) -> None:
    """G7.9b makes a payment only on a rank whose text no other rank repeats.

    1,000 HL7 stamps to the minute over three days -- many minutes repeat
    -- fifteen of them ending in an offset the census counts into
    `(none)`. Mutant, run: a repeated text paid on, and the twin holds
    more different values than its description publishes, missing
    `distinct.n_distinct` at every seed.
    """
    draw = random.Random(81)
    start = datetime.datetime(2023, 1, 1)
    cells = [
        (start + datetime.timedelta(seconds=draw.randrange(3 * 86400))).strftime("%Y%m%d%H%M")
        for _row in range(1000)
    ]
    places = list(range(1000))
    draw.shuffle(places)
    for place in places[0:15]:
        cells[place] = cells[place] + draw.choice(("-0400", "-0500", "+0100"))
    block, profile, _questions = _described(tmp_path, cells)
    assert block["format"] == "layout {YYYY}{MM}{DD}{HH}{MI}{+HHMM?}"
    assert block["utc_offsets"] == {"(none)": 1000}
    for seed in SEEDS:
        twin, written = _twin(profile, seed)
        assert sum(1 for cell in written if not cell.isdigit()) == 15, seed
        assert _validated(profile, twin)[0] == 0, seed


# -- skeptic 2's round (the report's item numbers) --------------------------


def _oracle() -> object:
    """The generation oracle, imported as the reader review's clauses import it.

    Not loaded from its path: each `spec_from_file_location` is a route the
    version-reach guard counts (`tests/test_version_reach.py`).
    """
    from tools.reference import make_generation_reference_vectors as oracle

    return oracle


def _stamps_wearing(
    rows: int,
    seed: int,
    worn: "list[tuple[str, int]]",
    shape: str = "%Y%m%d%H%M%S",
) -> "list[str]":
    """HL7 stamps over 900 days, interior ones ending in each suffix ``worn`` lists.

    ``worn`` gives each suffix with how many cells end in it; they are
    placed on interior cells in a shuffled order, no cell twice. These are
    the columns skeptic 2 measured, cell for cell.
    """
    draw = random.Random(seed)
    start = datetime.datetime(2021, 1, 1)
    cells = [
        (start + datetime.timedelta(seconds=draw.randrange(900 * 86400))).strftime(shape)
        for _row in range(rows)
    ]
    places = list(range(1, rows - 1))
    draw.shuffle(places)
    at = 0
    for suffix, count in worn:
        for _cell in range(count):
            cells[places[at]] = cells[places[at]] + suffix
            at = at + 1
    return cells


def _not_numbers(cells: "list[str]") -> int:
    """How many cells a reader of numbers refuses."""
    return sum(1 for cell in cells if parsing.classify_number(cell) != parsing.NUMBER)


def test_sk2_item1_no_offset_the_census_names_is_written_for_its_class_count(
    tmp_path: pathlib.Path,
) -> None:
    """Item 1: G7.9b never writes an offset the census names.

    1,000 HL7 stamps, 300 ending `+0000` -- a named offset -- and 5 ending
    `-0500`, which the census counts into `(none)`: the twin wears `+0000`
    on exactly the 300 the census gives it and the five it owes at
    `+0100`, and validates at floors 11 and 36 and seeds 0 to 2. Mutant,
    run: the named offsets left on the offer, and the twin wears `+0000` on
    305 cells -- the twin skeptic 2 measured missing `utc_offsets` at every
    seed and both floors.

    And a named offset after the first one on offer, skeptic 2's spill:
    1,000 stamps, 100 ending `+0100` and fifty `-0300` to `-0800`, nine or
    eight each. The twin wears `+0100` on exactly its 100, holds the 150
    cells that are not numbers and validates at both floors and seeds 0 to
    2; and handed the stamps with the fifty bare, the pass writes `+0100`
    on none of them and the oracle writes the same cells. Mutants, run
    (the leftover round): only a named `+00:00` left off the offer, a
    named `+01:00` kept on it, and the twin wears `+0100` on 110 cells at
    floor 11; the same in the oracle alone, and its cells are not the
    pass's.
    """
    cells = _stamps_wearing(1000, 101, [("+0000", 300), ("-0500", 5)])
    for floor in (11, 36):
        block, profile, _questions = _described(tmp_path / f"floor-{floor}", cells, floor=floor)
        assert block["format"] == "layout {YYYY}{MM}{DD}{HH}{MI}{SS}{+HHMM?}"
        assert block["utc_offsets"] == {"(none)": 700, "+00:00": 300}
        assert block["n_not_numeric"] == 305
        for seed in SEEDS:
            twin, written = _twin(profile, seed)
            assert sum(1 for cell in written if cell.endswith("+0000")) == 300, (floor, seed)
            assert sum(1 for cell in written if cell.endswith("+0100")) == 5, (floor, seed)
            assert _validated(profile, twin)[0] == 0, (floor, seed)
    rare = [("-0300", 9), ("-0400", 9), ("-0500", 8), ("-0600", 8), ("-0700", 8), ("-0800", 8)]
    spill = _stamps_wearing(1000, 3, [("+0100", 100)] + rare)
    bare = [cell if cell.endswith("+0100") else cell[0:14] for cell in spill]
    for floor in (11, 36):
        block, profile, _questions = _described(tmp_path / f"spill-{floor}", spill, floor=floor)
        assert block["format"] == "layout {YYYY}{MM}{DD}{HH}{MI}{SS}{+HHMM?}"
        assert block["utc_offsets"] == {"(none)": 900, "+01:00": 100}
        assert block["n_not_numeric"] == 150
        for seed in SEEDS:
            twin, written = _twin(profile, seed)
            assert sum(1 for cell in written if cell.endswith("+0100")) == 100, (floor, seed)
            assert _not_numbers(written) == 150, (floor, seed)
            assert _validated(profile, twin)[0] == 0, (floor, seed)
        column, facts = _loaded(profile)
        paid = generation._offsets_owed_by_the_classes(column, facts, list(bare), (), floor)
        assert sum(1 for cell in paid if cell.endswith("+0100")) == 100, floor
        assert _not_numbers(paid) == 150, floor
        oracle = _oracle()
        assert oracle.offsets_paid_to_the_classes(block, list(bare), (), floor) == paid, floor  # type: ignore[attr-defined]


def _loaded(profile: pathlib.Path) -> "tuple[contract.ColumnBlock, contract.DatetimeFacts]":
    """The first column of a description as the generator loads it, and its facts."""
    column = contract.load_profile(str(profile)).columns[0]
    facts = column.facts
    assert isinstance(facts, contract.DatetimeFacts)
    return column, facts


def test_sk2_item2_nothing_owed_reads_each_class_once_and_writes_no_offset(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Item 2: G7.9b costs one reading of each cell's class where nothing is owed.

    300 stamps, seven ending in an offset the census counts into `(none)`.
    Handed the cells as the table wrote them -- the seven wearing their
    offsets, so nothing is owed -- the pass reads each cell's class once
    and writes no offset; handed them bare, it writes the seven it owes
    and asks the field for those seven alone. Mutants, run: the stop where
    nothing is owed withdrawn (each open rank's class read a second time);
    the offset written on every open rank before the debt is known, as the
    pass did (298 more writes).
    """
    cells = _hl7_with_offsets(ROWS, 7)
    block, profile, _questions = _described(tmp_path, cells)
    assert block["format"] == "layout {YYYY}{MM}{DD}{HH}{MI}{SS}{+HHMM?}"
    assert block["utc_offsets"] == {"(none)": ROWS} and block["n_not_numeric"] == 7
    column, facts = _loaded(profile)
    classes = 0
    writes = 0
    shipped_class = parsing.classify_number
    shipped_added = parsing.layout_offset_added

    def class_counted(text: str) -> str:
        nonlocal classes
        classes = classes + 1
        return shipped_class(text)

    def write_counted(cell: str, name: str, offset: str) -> "str | None":
        nonlocal writes
        writes = writes + 1
        return shipped_added(cell, name, offset)

    monkeypatch.setattr(parsing, "classify_number", class_counted)
    monkeypatch.setattr(parsing, "layout_offset_added", write_counted)
    kept = generation._offsets_owed_by_the_classes(column, facts, list(cells), (), 11)
    assert kept == cells
    assert (classes, writes) == (ROWS, 0)
    bare = [cell[0:14] for cell in cells]
    paid = generation._offsets_owed_by_the_classes(column, facts, list(bare), (), 11)
    assert _not_numbers(paid) == 7
    assert writes == 7


def test_sk2_item3_a_run_whose_few_suffixes_read_as_an_offset_is_asked(
    tmp_path: pathlib.Path,
) -> None:
    """Item 3: a run ending in an offset no census names is asked as the bare run is.

    1,000 fourteen-figure identifiers, eight ending `-0001` to `-0008`,
    read under `{+HHMM?}`, and 1,000 twelve-figure ones, seven ending `-01`
    or `-02`, under `{+HH?}`: each census names `(none)` alone, and each
    column is asked keep, code or identifier at its run's own width, Enter
    keeping the dates. Stamps half of which wear an offset the census
    names are not asked. Mutant, run: the clause withdrawn, and neither run
    is asked.

    And only a run of 12 or 14 figures: 1,000 stamps with a fraction after
    their seconds, seven ending `-0400` or `-0500`, read under
    `{SS}.{F}{+HHMM?}` with `(none)` alone in the census, are not asked,
    since the layout before their offset is no such run
    (`parsing.layout_low_evidence`). Mutant, run (the leftover round): the
    run's own condition dropped, and that column is asked.
    """
    for name, cells, layout, width in (
        (
            "minutes",
            _stamps_wearing(1000, 111, [(f"-00{suffix:02d}", 1) for suffix in range(1, 9)]),
            "layout {YYYY}{MM}{DD}{HH}{MI}{SS}{+HHMM?}",
            14,
        ),
        (
            "lines",
            _stamps_wearing(1000, 112, [("-01", 4), ("-02", 3)], "%Y%m%d%H%M"),
            "layout {YYYY}{MM}{DD}{HH}{MI}{+HH?}",
            12,
        ),
    ):
        block, _profile, questions = _described(tmp_path / name, cells)
        assert block["format"] == layout, name
        assert block["utc_offsets"] == {"(none)": 1000}, name
        asked = [entry for entry in questions["asked"] if entry["read_as_now"] == asking.ANSWER_KEEP]
        assert asked, name
        assert f"{width} characters wide" in asked[0]["what_synthtwin_saw"], name
        assert "offset" in asked[0]["what_synthtwin_saw"], name
        assert {"keep", "code", "identifier"} <= {
            choice["answer"] for choice in asked[0]["answers_you_can_give"]
        }, name
    block, _profile, questions = _described(
        tmp_path / "named", spellings.cells("hl7_offset_some_omit", ROWS)
    )
    assert block["format"] == "layout {YYYY}{MM}{DD}{HH}{MI}{SS}{+HHMM?}"
    assert not [entry for entry in questions["asked"] if entry["read_as_now"] == asking.ANSWER_KEEP]
    seed, worn, shape, layout = _OWED_SHAPES["fraction"]
    block, _profile, questions = _described(
        tmp_path / "fraction", _stamps_wearing(1000, seed, worn, shape)
    )
    assert block["format"] == layout
    assert block["utc_offsets"] == {"(none)": 1000}
    assert not [entry for entry in questions["asked"] if entry["read_as_now"] == asking.ANSWER_KEEP]


# The eighteen layouts that stand in for a two-figure member in a declared
# century, written out: each member shape on `/` or `.` with its year last,
# in each of the three windows a person may declare.
_MEMBER_LAYOUTS = (
    "layout {M}/{D}/{YY1900}", "layout {M}/{D}/{YY1930}", "layout {M}/{D}/{YY1940}",
    "layout {D}/{M}/{YY1900}", "layout {D}/{M}/{YY1930}", "layout {D}/{M}/{YY1940}",
    "layout {MM}/{DD}/{YY1900}", "layout {MM}/{DD}/{YY1930}", "layout {MM}/{DD}/{YY1940}",
    "layout {DD}/{MM}/{YY1900}", "layout {DD}/{MM}/{YY1930}", "layout {DD}/{MM}/{YY1940}",
    "layout {MM}.{DD}.{YY1900}", "layout {MM}.{DD}.{YY1930}", "layout {MM}.{DD}.{YY1940}",
    "layout {DD}.{MM}.{YY1900}", "layout {DD}.{MM}.{YY1930}", "layout {DD}.{MM}.{YY1940}",
)
_MEMBER_CELLS = {
    "{M}/{D}/": "3/7/35",
    "{D}/{M}/": "7/3/35",
    "{MM}/{DD}/": "03/17/35",
    "{DD}/{MM}/": "17/03/35",
    "{MM}.{DD}.": "03.17.35",
    "{DD}.{MM}.": "17.03.35",
}


def test_sk2_item4_every_member_layout_sets_the_spaces_round_a_cell_aside() -> None:
    """Item 4: the eighteen layouts a declared century stands in with, listed.

    Each reads a cell with a space, a tab or a no-break space before or
    after it as the member it stands in for does, and no other layout is
    among them. Mutants, run: `{D}/{M}/`, `{MM}.{DD}.` or `{DD}/{MM}/` left
    out of the member shapes, or the 1940 window left out of the set. Three
    of the four turned an answered column of births back into free text
    (skeptic 2); the fourth was stood in for by `{D}/{M}/`.
    """
    for name in _MEMBER_LAYOUTS:
        assert parsing.layout_sets_spaces_aside(name), name
        cell = _MEMBER_CELLS[name[len(parsing.LAYOUT_PREFIX) : name.index("{YY")]]
        read = parsing.parse_datetime(cell, name)
        assert read is not None, name
        for spaced in (f" {cell}", f"{cell} ", f"\t{cell}", f"{cell} "):
            assert parsing.parse_datetime(spaced, name) == read, (name, spaced)
    assert len(parsing._LAYOUTS_READ_AS_MEMBERS) == len(_MEMBER_LAYOUTS)


# G7.9b's rules for each field and for the stand-ins: seven of 1,000 stamps
# ending in an offset the census counts into `(none)`, as skeptic 2 wrote
# them -- (seed, suffixes, the stamp's shape, the layout read).
_OWED_SHAPES = {
    "colon": (131, [("-04:00", 4), ("-05:00", 3)], "%Y%m%d%H%M%S", "layout {YYYY}{MM}{DD}{HH}{MI}{SS}{+HH:MM?}"),
    "fraction": (7, [("-0400", 4), ("-0500", 3)], "%Y%m%d%H%M%S.0000", "layout {YYYY}{MM}{DD}{HH}{MI}{SS}.{F}{+HHMM?}"),
    "hours_only": (9, [("-04", 4), ("-05", 3)], "%Y%m%d%H%M%S", "layout {YYYY}{MM}{DD}{HH}{MI}{SS}{+HH?}"),
    "stand_ins": (8, [("-0400", 4), ("-0500", 3)], "%Y%m%d%H%M%S", "layout {YYYY}{MM}{DD}{HH}{MI}{SS}{+HHMM?}"),
    "zulu": (10, [("Z", 7)], "%Y%m%d%H%M%S", "layout {YYYY}{MM}{DD}{HH}{MI}{SS}{Z?}"),
}


@pytest.mark.parametrize("name", sorted(_OWED_SHAPES))
def test_sk2_item4_each_field_writes_the_offsets_its_class_count_owes(
    tmp_path: pathlib.Path, name: str
) -> None:
    """Item 4: one column for each of G7.9b's fields, and one beside stand-ins.

    The twin holds the published count of cells that are not numbers and
    validates: the offset written with its colon (`+00:00`), after a run
    with a fraction (still a number without it), in hours alone (`+00`),
    beside five texts that are no dates (the stand-ins, taken off the
    debt), and on a zulu field (its own word). Mutants, run: the colon
    dropped, the run with a fraction no longer a number, the hours-only
    offset written in four figures, the numeric offsets offered to a zulu
    field -- each wrote no offset -- and the stand-ins left on the debt,
    which wrote twelve offsets for seven.
    """
    seed, worn, shape, layout = _OWED_SHAPES[name]
    cells = _stamps_wearing(1000, seed, worn, shape)
    if name == "stand_ins":
        for place in range(5):
            cells[100 + place * 37] = f"pending {place}"
    block, profile, _questions = _described(tmp_path, cells)
    assert block["format"] == layout
    assert block["utc_offsets"] == {"(none)": block["n_present"] - block["n_unparsed"]}
    assert block["n_not_numeric"] == 7 + block["n_unparsed"]
    twin, written = _twin(profile, 0)
    assert _not_numbers(written) == block["n_not_numeric"]
    assert _validated(profile, twin)[0] == 0


def test_sk2_item4_a_debt_past_the_offer_is_written_as_far_as_it_reaches(
    tmp_path: pathlib.Path,
) -> None:
    """Item 4: 180 offsets owed at a floor of 11, where the offer holds 150.

    Twenty offsets of nine cells each, every one under the line, all
    counted into `(none)`: the twin is written, wearing ten each of the
    fifteen offsets on offer, and misses its two class counts and nothing
    else -- the limit method G7.9b states. Mutant, run: the bound of ten
    cells times the offsets on offer dropped, and generate stops on an
    offset past the fifteenth.
    """
    hours = (-12, -11, -10, -9, -8, -7, -6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6, 7, 8)
    worn = [(f"{'+' if hour > 0 else '-'}{abs(hour):02d}00", 9) for hour in hours]
    block, profile, _questions = _described(tmp_path, _stamps_wearing(1000, 5, worn))
    assert block["utc_offsets"] == {"(none)": 1000} and block["n_not_numeric"] == 180
    twin, written = _twin(profile, 0)
    suffixes = collections.Counter(cell[14:] for cell in written if len(cell) > 14)
    assert suffixes == {f"+{hour:02d}00": 10 for hour in range(15)}
    code, report = _validated(profile, twin)
    assert code == 3
    missed = {line.split(" [")[0].strip() for line in report.splitlines() if line.rstrip().endswith(": MISSED")}
    assert missed == {"counts.n_numeric", "counts.n_not_numeric"}


def test_sk2_item4_the_numbers_left_stay_at_the_line(tmp_path: pathlib.Path) -> None:
    """Item 4: G7.9b never leaves fewer numbers than the census line.

    A description the loader takes, written by hand: 120 stamps all counted
    into `(none)` beside 115 cells that are not numbers. Paid in full, five
    numbers would be left, under the line of eleven, and the twin's own
    description would no longer count its offsets into `(none)`; the pass
    writes 109 and leaves eleven, and the oracle writes the same cells.
    Mutant, run: the bound at the line dropped, 115 written and five
    numbers left.
    """
    cells = _hl7_with_offsets(120, 3)
    _block, profile, _questions = _described(tmp_path, cells)
    document = json.loads(profile.read_text(encoding="utf-8"))
    block = document["columns"][0]
    assert block["utc_offsets"] == {"(none)": 120}
    block["n_numeric"] = 5
    block["n_not_numeric"] = 115
    edited = fixtures.write_profile(tmp_path, "edited-profile.json", document)
    column, facts = _loaded(edited)
    bare = [cell[0:14] for cell in cells]
    paid = generation._offsets_owed_by_the_classes(column, facts, list(bare), (), 11)
    assert len(bare) - _not_numbers(paid) == parsing.census_floor(11)
    oracle = _oracle()
    assert oracle.offsets_paid_to_the_classes(block, list(bare), (), 11) == paid  # type: ignore[attr-defined]


def test_sk2_item4_no_offset_is_written_beside_a_pool(tmp_path: pathlib.Path) -> None:
    """Item 4: G7.9b writes nothing where the census pools any offset.

    The loader refuses a pool beside `(none)` (contract D3), so the rule is
    asked of the function itself, and of the oracle: handed
    `{"(none)": 290, "(withheld)": 10}` and ten cells that are not numbers
    owed, each writes nothing; handed `{"(none)": 300}`, each writes the
    same ten. Mutant, run: the pool's clause withdrawn, and ten are
    written beside the pool.
    """
    cells = _hl7_with_offsets(ROWS, 2)
    block, profile, _questions = _described(tmp_path, cells)
    column, facts = _loaded(profile)
    owing = dataclasses.replace(column, n_numeric=ROWS - 10, n_not_numeric=10)
    bare = [cell[0:14] for cell in cells]
    oracle = _oracle()
    pooled = {"(none)": ROWS - 10, "(withheld)": 10}
    kept = generation._offsets_owed_by_the_classes(
        owing, dataclasses.replace(facts, utc_offsets=pooled), list(bare), (), 11
    )
    assert kept == bare
    pooled_block = dict(block, n_numeric=ROWS - 10, n_not_numeric=10, utc_offsets=pooled)
    assert oracle.offsets_paid_to_the_classes(pooled_block, list(bare), (), 11) == bare  # type: ignore[attr-defined]
    whole = {"(none)": ROWS}
    paid = generation._offsets_owed_by_the_classes(
        owing, dataclasses.replace(facts, utc_offsets=whole), list(bare), (), 11
    )
    assert _not_numbers(paid) == 10
    whole_block = dict(block, n_numeric=ROWS - 10, n_not_numeric=10, utc_offsets=whole)
    assert oracle.offsets_paid_to_the_classes(whole_block, list(bare), (), 11) == paid  # type: ignore[attr-defined]


# -- the Codex review of the landing (the review's item numbers) ------------


def _march_days(first: int) -> "list[str]":
    """1,000 SAS dates cycling the 1st to the 28th of March 2023, from the ``first``-th."""
    days = [f"{day}MAR2023" for day in range(1, 29)]
    turned = days[first - 1 :] + days[0 : first - 1]
    return [turned[place % 28] for place in range(1000)]


def test_codex_item1_a_compact_month_word_date_reads_whichever_day_comes_first(
    tmp_path: pathlib.Path,
) -> None:
    """Item 1: `1MAR2023` to `28MAR2023` read under `{D}{MON}{YYYY}` in either order.

    Starting on a one-figure day the column chose `{D}{MON}{YYYY}`, which
    LY1 refused, and the describe stopped on an internal error; starting
    on a two-figure day it was categorical, since no first cell offered
    the flexible layout. Both read 1,000 now, and the twin is written in
    the source's spelling and validates. Mutant, run: a two-figure day
    read padded alone, as before, and both orders fail again.
    """
    for first in (1, 10):
        cells = _march_days(first)
        described = taxonomy.profile_column("seen_at", 1, cells, 1000, taxonomy.Settings())
        details = described.details or {}
        assert described.role == taxonomy.ROLE_DATETIME, first
        assert details["format"] == "layout {D}{MON}{YYYY}", first
        assert details["n_unparsed"] == 0, first
    block, profile, _questions = _described(tmp_path, _march_days(10))
    assert block["format"] == "layout {D}{MON}{YYYY}"
    pattern = r"(?:[1-9]|[12]\d|3[01])(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\d{4}"
    for seed in SEEDS:
        twin, written = _twin(profile, seed)
        assert all(re.fullmatch(pattern, cell) for cell in written), seed
        assert all(spellings.parses(cell, "%d%b%Y") for cell in written), seed
        assert _validated(profile, twin)[0] == 0, seed


def _agreement_corpus() -> "list[str]":
    """Cells of every production: the gate's spellings and one of each shape by hand."""
    corpus: "list[str]" = []
    for name in sorted(spellings.SPELLINGS):
        corpus += spellings.cells(name, 12)
    corpus += [
        "1MAR2023", "17MAR2023", "1MAR23", "17mar2023", "1-MAR-2023", "17-Mar-23",
        "1 Mar 2023", "17/Mar/2023", "1.Mar.2023", "2023-Mar-1", "2023 Mar 17",
        "Mar 1, 2023", "Mar 17 2023", "Mar  1 2023", "Mar  1 23", "Mar 17 23",
        "Mar-1-2023", "Sun 17 Mar 2024", "Sunday, March 17, 2024",
        "3/4/2024", "03/04/24", "3-4-24", "3.4.2024", "03.04.24", "2024-3-4",
        "2024/03/04", "2024.03.04", "202403041405", "20240304140500.123",
        "20240304140500-05", "20240304T140500Z", "2024-03-04 14.05.00",
        "2024-03-04 14:05:00 UTC", "2024-03-04 14:05:00 +01:00", "2024-03-04 14:05:00:123",
    ]
    return corpus


def test_codex_item1_discovery_and_ly1_agree() -> None:
    """Item 1: what candidate discovery offers, LY1 admits, and the reverse.

    Every layout the grammar's productions give for a cell of the corpus is
    one LY1 admits, so no column can choose a layout its own description
    then refuses; and every cell such a layout writes -- days 1, 9, 10 and
    17, each flexible field padded or not, every offset its field writes --
    is a cell discovery offers that layout for, which is the exactness the
    choice rests on (`taxonomy._layout_candidates`). Mutants, run: a
    two-figure day read padded alone before a month word (both halves
    fail), and a space-padded day before a two-figure year left unread
    (`Mar  1 23`, the second half).
    """
    produced: "dict[str, int]" = {}
    for cell in _agreement_corpus():
        for one in parsing.layouts_of(cell):
            produced[one] = 1
    refused = [one for one in produced if not parsing.is_layout_format(parsing.layout_format(one))]
    assert refused == []
    instants = [
        f"{year}-{month:02d}-{day:02d}{clock}"
        for year in (1969, 2024, 2068)
        for month in (1, 10)
        for day in (1, 9, 10, 17)
        for clock in ("", " 00:00:00", " 23:59:59")
    ]
    unoffered: "dict[str, str]" = {}
    for one in sorted(produced):
        name = parsing.layout_format(one)
        items = parsing.compiled_layout(one)
        assert items is not None, one
        field = parsing.layout_offset_field(name)
        offsets = [""]
        if field:
            offsets = ["Z"] if field in ("Z", "z", "UTC", "GMT") else ["+01:00", "-05:00"]
        for canonical in instants:
            if (len(canonical) > 10) != parsing.layout_has_clock(name):
                continue
            for offset in offsets:
                for widths in ((True, True), (True, False), (False, True), (False, False)):
                    cell = parsing.layout_cell(items, canonical, offset, widths, 3)
                    if parsing.layout_reading(cell, items) is None:
                        continue
                    if one not in parsing.layouts_of(cell):
                        unoffered[one] = cell
    assert unoffered == {}


def test_codex_item1_the_choice_stops_at_a_layout_reading_every_row(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Item 1's price: a column the first candidate reads whole is read once.

    SAS stamps offer six candidates since item 1 -- a padded and a flexible
    day under each of three month-word sets -- and the first in key order,
    `{DD}{MON}{YYYY}:...`, reads every row, so no other can win: the walk
    stops there and the layout chosen is the one it chose before. Mutant,
    run: the stop withdrawn, and the column is read six times.
    """
    cells = spellings.cells("sas_datetime20", ROWS)
    reads = 0
    shipped = taxonomy._layout_reads

    def counted_reads(
        items: "tuple[tuple[str, str], ...]", counted: "dict[str, int]", room: int
    ) -> "tuple[int, int, list[str]]":
        nonlocal reads
        reads = reads + 1
        return shipped(items, counted, room)

    monkeypatch.setattr(taxonomy, "_layout_reads", counted_reads)
    described = taxonomy.profile_column("seen_at", 1, cells, ROWS, taxonomy.Settings())
    assert (described.details or {})["format"] == "layout {DD}{MON}{YYYY}:{HH}:{MI}:{SS}"
    assert reads == 1
