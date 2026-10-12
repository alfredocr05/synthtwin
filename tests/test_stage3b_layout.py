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

And the Codex review's eight items, each clause failing on the reviewed
head and run against the mutants its docstring names: a compact
month-word date read whichever day comes first, candidate discovery and
LY1 one set both ways, and the choice stopping at a layout reading every
row (item 1); a sparse layout column loading as it was written (item
2); a run every cell of which ends in a suffix asked (item 3); whole
repeated texts carrying the offsets owed, with G7.9b step 5's choice and
room (item 4); Q5 beside the codes question (item 5); no zulu key on a
signed field (item 6); a layout admitting only values its reader reads
back (item 7); and G7.9b's provenance sentence (item 8).

And the verification of that review's repair, each clause run against
the mutants its docstring names, the item 1 and item 3 ones failing on
f747e7b's code: Codex's column with eleven and with thirteen offset
cells wearing every one, a shape for each rule of G7.9b step 5's aim and
look ahead -- the bar on one offset among them -- and of step 6's fewer
texts standing alone, and no text already wearing an offset walked (item
1); the five rules of the Codex round no test turned red -- the choice
stopping only at a layout reading every row, Q5 beside a member's codes
question, LY3 asking a tail's listed values, no text with a copy at an
end, and the texts of one size spread (item 2); and step 5 respelling
only the texts it writes (item 3).
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
import zlib

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


def test_item2_a_repeated_text_is_never_paid_on_in_part(tmp_path: pathlib.Path) -> None:
    """G7.9b writes an offset on a text another rank repeats only on every rank of it.

    1,000 HL7 stamps to the minute over three days -- many minutes repeat
    -- fifteen of them ending in an offset the census counts into
    `(none)`; step 4 writes them on texts standing alone, and a repeated
    text is paid on only whole, by step 5 (the Codex review of landing
    R2a, item 4). Mutant, run: one rank of a repeated text paid on, and
    the twin holds more different values than its description publishes,
    missing `distinct.n_distinct` at every seed.
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


# Five dates beside 995 blank cells, in each kind of offset field a layout
# has: (the five, the layout read).
_SPARSE_SHAPES = {
    "no_field": ([f"{day}MAR2023" for day in range(17, 22)], "layout {DD}{MON}{YYYY}"),
    "two_figure_year": ([f"{day}-MAR-23" for day in range(17, 22)], "layout {DD}-{MON}-{YY}"),
    "every_cell": (
        [f"202303{day}140500+0100" for day in range(17, 22)],
        "layout {YYYY}{MM}{DD}{HH}{MI}{SS}{+HHMM}",
    ),
    "zulu": ([f"202303{day}T140500Z" for day in range(17, 22)], "layout {YYYY}{MM}{DD}T{HH}{MI}{SS}{Z}"),
    "some_cells": (
        [f"202303{day}140500" + ("-0500" if day % 2 else "") for day in range(17, 22)],
        "layout {YYYY}{MM}{DD}{HH}{MI}{SS}{+HHMM?}",
    ),
}


@pytest.mark.parametrize("name", sorted(_SPARSE_SHAPES))
def test_codex_item2_a_sparse_layout_column_loads_as_it_was_written(
    tmp_path: pathlib.Path, name: str
) -> None:
    """Item 2: five dates beside 995 blank cells, at floor 11, load and are checked.

    Each census pools its five, `{"(withheld)": 5}` -- on a layout with no
    offset field a pool of `(none)` -- and LY4 refused the pool wherever
    the layout had no offset field, blaming an edited description that
    `synthtwin profile` had written, as it would again. Every one loads
    now, as the same five in ISO's spelling do; the twins validate, but
    the run some of whose cells write an offset, whose pooled census
    leaves the twin no offset to write: it misses its two class counts
    and nothing else, the limit plan P4-D383 states. Mutant, run: the
    pool admitted only beside an offset field, and the first two shapes
    fail to load.
    """
    five, layout = _SPARSE_SHAPES[name]
    block, profile, _questions = _described(tmp_path, five + [""] * 995)
    assert block["format"] == layout
    assert block["utc_offsets"] == {"(withheld)": 5}
    contract.load_profile(str(profile))
    twin, written = _twin(profile, 0)
    assert len(written) == 5
    code, report = _validated(profile, twin)
    if name != "some_cells":
        assert code == 0
        return
    assert code == 3
    missed = {line.split(" [")[0].strip() for line in report.splitlines() if line.rstrip().endswith(": MISSED")}
    assert missed == {"counts.n_numeric", "counts.n_not_numeric"}


def _accessions() -> "list[str]":
    """1,000 accession numbers: a run of 14 figures and one of a hundred suffixes.

    The prefixes are consecutive seconds from `20240317140500`; the
    suffixes `-0000` to `-0059` and `-0100` to `-0139`, ten cells each --
    every one a valid offset, none on enough cells to be named.
    """
    start = datetime.datetime(2024, 3, 17, 14, 5, 0)
    suffixes = [f"-00{minute:02d}" for minute in range(60)] + [f"-01{minute:02d}" for minute in range(40)]
    return [
        (start + datetime.timedelta(seconds=place)).strftime("%Y%m%d%H%M%S") + suffixes[place // 10]
        for place in range(1000)
    ]


def test_codex_item3_a_run_every_cell_of_which_ends_in_a_suffix_is_asked(
    tmp_path: pathlib.Path,
) -> None:
    """Item 3: identifiers whose every cell ends in a suffix read as an offset are asked.

    The thousand accession numbers read under `{+HHMM}`, every offset in
    one pool, and were asked nothing, where their bare prefixes are asked
    keep, code or identifier: a suffix on every cell changed identifiers
    into dates without a question. They are asked now, at the run's own
    width, the sentence saying each value carries the suffix, Enter
    keeping the dates; declared identifiers, they are described as such.
    Mutants, run: the rule held to an offset some cells omit, as before,
    and the column is asked nothing; the sentence saying "some of them" of
    a suffix every cell carries.
    """
    cells = _accessions()
    block, _profile, questions = _described(tmp_path / "suffixed", cells)
    assert block["format"] == "layout {YYYY}{MM}{DD}{HH}{MI}{SS}{+HHMM}"
    assert block["utc_offsets"] == {"(withheld)": 1000}
    asked = [entry for entry in questions["asked"] if entry["read_as_now"] == asking.ANSWER_KEEP]
    assert len(asked) == 1
    seen = asked[0]["what_synthtwin_saw"]
    assert "14 characters wide, each of them followed by what is read as an offset" in seen
    assert {"keep", "code", "identifier"} <= {
        choice["answer"] for choice in asked[0]["answers_you_can_give"]
    }
    block, profile, questions = _described(tmp_path / "declared", cells, "--identifier", "seen_at")
    assert block["role"] == taxonomy.ROLE_IDENTIFIER
    twin, _written = _twin(profile, 0)
    assert _validated(profile, twin)[0] == 0


def test_codex_item5_q5_is_asked_beside_the_codes_question(tmp_path: pathlib.Path) -> None:
    """Item 5: a column read as dates only once its codes are answered is asked its century too.

    970 consecutive births from the 1st of January 1931, written `01JAN31`,
    beside 30 `UNK`: the column is labels, and its first questions file
    asked about the code alone, so the run answering it read the births as
    2031 to 2033 and only then asked their century -- a second round to
    read one column right. Q5 stands beside the codes question in the first
    file now, each choice saying it holds once the codes are answered
    `missing`, and one answering run reads the births in 1931 to 1933,
    asks nothing more of the column and its twin validates. Mutants, run:
    the codes question's columns not handed to Q5, as before; the choices
    saying what the column publishes now, which is labels.
    """
    start = datetime.date(1931, 1, 1)
    cells = [
        (start + datetime.timedelta(days=day)).strftime("%d%b%y").upper() for day in range(970)
    ] + ["UNK"] * 30
    block, _profile, questions = _described(tmp_path / "asked", cells)
    assert block["role"] == taxonomy.ROLE_LONG_TAIL
    entries = questions["asked"]
    assert isinstance(entries, list)
    codes = [entry for entry in entries if entry["read_as_now"] == asking.ANSWER_KEEP]
    centuries = [entry for entry in entries if entry["read_as_now"] == asking.ANSWER_CENTURY_POSIX]
    assert len(codes) == 1 and len(centuries) == 1
    for choice in centuries[0]["answers_you_can_give"]:
        assert choice["then_the_description_publishes"].startswith(
            "once its codes are answered 'missing', "
        ), choice
    codes[0]["your_answer"] = asking.ANSWER_NO_DATE
    centuries[0]["your_answer"] = asking.ANSWER_CENTURY_1930
    answers = tmp_path / "answers.json"
    answers.write_text(json.dumps(questions), encoding="utf-8", newline="\n")
    block, profile, questions = _described(tmp_path / "answered", cells, "--answers", str(answers))
    assert block["format"] == "layout {DD}{MON}{YY1930}"
    assert block["n_unparsed"] == 0
    read = [parsing.parse_datetime(cell, f"{block['format']}") for cell in cells[0:970]]
    assert all(found is not None and "1931" <= found[0][0:4] <= "1933" for found in read)
    assert [entry for entry in questions["asked"] if entry["column"] == "seen_at"] == []
    twin, _written = _twin(profile, 0)
    assert _validated(profile, twin)[0] == 0


def test_codex_item6_a_signed_field_takes_no_zulu_key(tmp_path: pathlib.Path) -> None:
    """Item 6: `Z` is refused on a signed offset field, and nothing loadable parts writer from oracle.

    HL7 stamps with a fraction and `+0000` on every cell, the census
    changed to `{"Z": 300}` and nothing else: the loader took it, and the
    twin wrote cells such as `20210101000000.0000Z` under a layout ending
    `{+HHMM}`, every one unreadable by it, where the oracle writes
    `+0000`. A signed field reads `+0000` as `+00:00`, never as `Z`, so no
    description of its own carries that key: LY4 refuses it now. And for
    every offset field, every key LY4 admits is written alike by the
    shipped writer and the oracle, and read back by the layout. Mutant,
    run: `Z` admitted on a signed field, as before.
    """
    _block, profile, _questions = _described(tmp_path, spellings.cells("hl7_ts_fraction_offset", ROWS))
    document = json.loads(profile.read_text(encoding="utf-8"))
    block = document["columns"][0]
    assert block["format"] == "layout {YYYY}{MM}{DD}{HH}{MI}{SS}.{F}{+HHMM}"
    assert block["utc_offsets"] == {"+00:00": ROWS}
    block["utc_offsets"] = {"Z": ROWS}
    edited = fixtures.write_profile(tmp_path, "edited-profile.json", document)
    with pytest.raises(errors.ProfileError) as refused:
        contract.load_profile(str(edited))
    assert "LY4" in str(refused.value)
    oracle = _oracle()
    keys = ("Z", "+00:00", "+01:00", "-05:00", "+05:30", "(none)", "(withheld)")
    for layout in (
        "layout {YYYY}{MM}{DD}{HH}{MI}{SS}{+HHMM}",
        "layout {YYYY}{MM}{DD}{HH}{MI}{SS}{+HHMM?}",
        "layout {YYYY}-{MM}-{DD} {HH}:{MI}:{SS} {+HH:MM}",
        "layout {YYYY}-{MM}-{DD} {HH}:{MI}:{SS}{+HH}",
        "layout {YYYY}{MM}{DD}T{HH}{MI}{SS}{Z}",
        "layout {YYYY}-{MM}-{DD} {HH}:{MI}:{SS} {UTC}",
        "layout {YYYY}{MM}{DD}{HH}{MI}{SS}{Z?}",
    ):
        assert parsing.is_layout_format(layout), layout
        items = parsing.layout_items(layout)
        assert items is not None
        assert parsing.layout_offset_writable(layout, "Z") == (
            parsing.layout_offset_field(layout) in ("Z", "z", "UTC", "GMT")
        ), layout
        for key in keys:
            if not parsing.layout_offset_writable(layout, key):
                continue
            offset = key if key[0:1] != "(" else ""
            written = parsing.layout_cell(items, "2024-03-17 14:05:09", offset, (), 0)
            assert written == oracle.layout_written(  # type: ignore[attr-defined]
                layout, 2024, 3, 17, 14 * 3600 + 5 * 60 + 9, offset, "padded", 0
            ), (layout, key)
            assert parsing.layout_reading(written, items) is not None, (layout, key, written)


def _edited_moments(block: "dict[str, object]", old: str, new: str) -> None:
    """Every published moment of a block of dates with ``old`` written ``new``."""
    ladder = block["date_percentiles"]
    assert isinstance(ladder, dict)
    for rung in sorted(ladder):
        if isinstance(ladder[rung], str):
            ladder[rung] = ladder[rung].replace(old, new)
    for side in ("low_tail", "high_tail"):
        tail = block[side]
        if not isinstance(tail, dict):
            continue
        tail["boundary"] = f"{tail['boundary']}".replace(old, new)
        if isinstance(tail["values"], list):
            tail["values"] = [f"{value}".replace(old, new) for value in tail["values"]]


def test_codex_item7_a_layout_admits_only_values_its_reader_reads_back(
    tmp_path: pathlib.Path,
) -> None:
    """Item 7: the loader holds a layout's fraction and moments to what it reads.

    Three hundred compact stamps with `.123` after the second, the
    description changed in one fact each time: ten figures after the
    second, which `{F}` cannot read (the twin wrote ten zeros and every
    cell was unreadable); every published moment moved to 1724, before the
    layout's band; a sixtieth second on the high tail's boundary; and a
    two-figure year's moments moved to 1951, outside the window `{YY}`
    reads, where the twin's `51` would be read as 2051. Each is refused
    under LY3 now, and the description as written loads and validates.
    Mutants, run: no limit on the figures; no limit on the moments.
    """
    start = datetime.datetime(2024, 3, 17, 14, 5, 0)
    cells = [
        (start + datetime.timedelta(seconds=step)).strftime("%Y%m%d%H%M%S") + ".123"
        for step in range(ROWS)
    ]
    _block, profile, _questions = _described(tmp_path / "stamps", cells)
    twin, _written = _twin(profile, 0)
    assert _validated(profile, twin)[0] == 0
    oracle_cells = spellings.cells("oracle_dd_mon_rr", ROWS)
    _block, two_figure, _questions = _described(tmp_path / "oracle", oracle_cells)
    for name, source, edit in (
        ("figures", profile, lambda block: block.update(subsecond_digits=10)),
        ("1724", profile, lambda block: _edited_moments(block, "2024-", "1724-")),
        (
            "sixtieth",
            profile,
            lambda block: block["high_tail"].update(  # type: ignore[union-attr]
                boundary=f"{block['high_tail']['boundary'][0:17]}60"  # type: ignore[index]
            ),
        ),
        ("window", two_figure, lambda block: [
            _edited_moments(block, f"{year}-", f"{year - 70}-") for year in (2021, 2022, 2023)
        ]),
    ):
        document = json.loads(source.read_text(encoding="utf-8"))
        edit(document["columns"][0])
        edited = fixtures.write_profile(tmp_path, f"{name}-profile.json", document)
        with pytest.raises(errors.ProfileError) as refused:
            contract.load_profile(str(edited))
        assert "LY3" in str(refused.value), name


def _repeated_stamps() -> "list[str]":
    """Codex's column: 100 stamps 123 seconds apart, ten copies each, seven ending `-0500`."""
    start = datetime.datetime(2024, 1, 1)
    stamps = [
        (start + datetime.timedelta(seconds=123 * step)).strftime("%Y%m%d%H%M%S")
        for step in range(100)
    ]
    cells = [stamp for stamp in stamps for _copy in range(10)]
    for place in (100, 130, 160, 190, 220, 250, 280):
        cells[place] = cells[place] + "-0500"
    random.Random(31).shuffle(cells)
    return cells


def test_codex_item4_repeated_stamps_wear_the_offsets_their_class_count_owes(
    tmp_path: pathlib.Path,
) -> None:
    """Item 4: where no text stands alone, whole repeated texts carry the debt.

    One hundred stamps ten times each, seven cells ending `-0500`: the
    description publishes 107 different texts, seven cells that are not
    numbers and `{"(none)": 1000}`. G7.9b paid only on a text no other rank
    repeats, and the twin's texts all repeat, so seeds 1 and 2 wrote no
    offset and missed both class counts. Step 5 writes the rest on whole
    texts, every copy at one offset, so the twin holds seven cells that are
    not numbers and 107 different texts at seeds 0 to 3, and validates;
    and on each twin's stamps as the pass meets them, bare and in rank
    order, the shipped pass and the oracle write the same cells. Mutant,
    run: step 5 withdrawn, and seeds 1 to 3 hold no cell that is not a
    number.
    """
    cells = _repeated_stamps()
    block, profile, _questions = _described(tmp_path, cells)
    assert block["format"] == "layout {YYYY}{MM}{DD}{HH}{MI}{SS}{+HHMM?}"
    assert block["utc_offsets"] == {"(none)": 1000}
    assert (block["n_distinct"], block["n_not_numeric"]) == (107, 7)
    column, facts = _loaded(profile)
    oracle = _oracle()
    for seed in (0, 1, 2, 3):
        twin, written = _twin(profile, seed)
        assert _not_numbers(written) == 7, seed
        assert len(set(written)) == 107, seed
        assert _validated(profile, twin)[0] == 0, seed
        bare = sorted(cell[0:14] for cell in written)
        paid = generation._offsets_owed_by_the_classes(column, facts, list(bare), (), 11)
        assert _not_numbers(paid) == 7, seed
        assert oracle.offsets_paid_to_the_classes(block, list(bare), (), 11) == paid, seed  # type: ignore[attr-defined]


def _ranked_stamps(copies: "list[int]") -> "list[str]":
    """Stamps in rank order: an end, a text of each number of ``copies``, an end."""
    start = datetime.datetime(2024, 1, 1)
    cells = [start.strftime("%Y%m%d%H%M%S")]
    step = 0
    for size in copies:
        step = step + 1
        cells += [(start + datetime.timedelta(minutes=step)).strftime("%Y%m%d%H%M%S")] * size
    cells += [(start + datetime.timedelta(minutes=step + 1)).strftime("%Y%m%d%H%M%S")]
    return cells


def test_codex_item4_whole_texts_reach_the_rest_and_keep_each_offset_under_the_line(
    tmp_path: pathlib.Path,
) -> None:
    """Item 4's step 5, asked of the pass itself and of the oracle on stamps in rank order.

    Texts of three, four and five copies beside texts of twelve, which no
    offset holds, and seven owed: the choice reaches seven with the texts
    of four and three, where taking the largest first without asking
    whether the rest stays reachable would stop at five. And six stamps
    standing alone beside the same texts, thirteen owed: step 4 writes the
    six at `+0000`, which then has room for four more, so step 5 writes the
    text of four there and the text of three at `+0100` -- no offset on
    eleven cells or more, which the twin's own description would name.
    Each time the shipped pass and the oracle write the same cells.
    Mutants, run: the remainder's reach unasked; the room at an offset
    taken whole, step 4's payments there forgotten.
    """
    cells = _hl7_with_offsets(ROWS, 2)
    block, profile, _questions = _described(tmp_path, cells)
    column, facts = _loaded(profile)
    oracle = _oracle()
    for copies, owed in (
        ([12, 3, 12, 4, 12, 5, 12], 7),
        ([12, 1, 1, 1, 12, 1, 1, 1, 12, 3, 12, 4, 12, 5, 12], 13),
    ):
        bare = _ranked_stamps(copies)
        numbers = len(bare) - owed
        owing = dataclasses.replace(column, n_numeric=numbers, n_not_numeric=owed)
        whole = {"(none)": len(bare)}
        paid = generation._offsets_owed_by_the_classes(
            owing, dataclasses.replace(facts, utc_offsets=whole), list(bare), (), 11
        )
        assert _not_numbers(paid) == owed, copies
        assert len(set(paid)) == len(set(bare)), copies
        worn = collections.Counter(cell[14:] for cell in paid if len(cell) > 14)
        assert max(worn.values()) < parsing.census_floor(11), (copies, worn)
        owing_block = dict(block, n_numeric=numbers, n_not_numeric=owed, utc_offsets=whole)
        assert oracle.offsets_paid_to_the_classes(owing_block, list(bare), (), 11) == paid, copies  # type: ignore[attr-defined]


def test_codex_item8_a_made_up_offset_may_be_one_the_real_column_wore(
    tmp_path: pathlib.Path,
) -> None:
    """Item 8: G7.9b's provenance sentence says derived, never that it differs.

    1,000 different stamps, seven of them ending in a real `+0000` that the
    census counted into `(none)`: the twin writes seven made-up offsets,
    and each is `+0000`, the real ones' own. Method G7.9b and the pass's
    docstring said no offset written is the real column's; they say now
    that each is worked out from the census and the field, and may still
    be one some real cells wore. A wording correction, not a new rule.
    """
    start = datetime.datetime(2024, 3, 17, 14, 5, 0)
    cells = [(start + datetime.timedelta(seconds=7 * step)).strftime("%Y%m%d%H%M%S") for step in range(1000)]
    for place in random.Random(8).sample(range(1, 999), 7):
        cells[place] = cells[place] + "+0000"
    block, profile, _questions = _described(tmp_path, cells)
    assert block["utc_offsets"] == {"(none)": 1000} and block["n_not_numeric"] == 7
    _twin_path, written = _twin(profile, 1)
    assert sorted(cell[14:] for cell in written if len(cell) > 14) == ["+0000"] * 7
    method = pathlib.Path(__file__).resolve().parents[1] / "docs" / "spec" / "generation-method-v1.md"
    section = method.read_text(encoding="utf-8").split("### G7.9b ")[1].split("\n## ")[0]
    shipped = " ".join(f"{generation._offsets_owed_by_the_classes.__doc__}".split())
    for said in (" ".join(section.split()), shipped):
        assert "No offset written is the real column's" not in said
        assert "may still be one some real cells wore" in said


# -- the verification of the Codex review's repair (its open items) ---------


_SUFFIXES = ("-0500", "-0400", "-0600", "-0700", "-0800", "+0100", "+0200", "+0530", "-0300", "+0900")


def _repeated_stamps_wearing(worn: int) -> "list[str]":
    """Codex's column with ``worn`` offset cells, as the verification built it.

    100 stamps 123 seconds apart, ten copies each; ``worn`` interior cells
    drawn by `Random(worn)`, each ending in the next of ten offsets in
    turn, none on enough cells to be named; shuffled by `Random(31)`.
    """
    start = datetime.datetime(2024, 1, 1)
    stamps = [
        (start + datetime.timedelta(seconds=123 * step)).strftime("%Y%m%d%H%M%S")
        for step in range(100)
    ]
    cells = [stamp for stamp in stamps for _copy in range(10)]
    places = sorted(random.Random(worn).sample(range(1, 999), worn))
    for turn, place in enumerate(places):
        cells[place] = cells[place] + _SUFFIXES[turn % len(_SUFFIXES)]
    random.Random(31).shuffle(cells)
    return cells


def test_cxv_item1_offsets_past_one_offsets_room_are_all_worn(tmp_path: pathlib.Path) -> None:
    """Item 1: Codex's column with eleven and with thirteen offset cells wears every one.

    Step 5 chose offset by offset, each taking the most it held: with
    eleven offset cells every seed from 0 to 5 wrote ten and missed both
    class counts -- at seed 0 step 4 wrote the one text standing alone at
    `+0000`, a text of nine copies filled the nine cells left there and
    the one cell over fitted no text -- and with thirteen, seeds 0, 3 and
    4 wrote ten, ten and twelve. Step 5 aims once over the offsets and
    looks ahead, so each of those seeds holds every cell that is not a
    number and every different text, and validates; on each twin's
    stamps, bare and in rank order, the shipped pass and the oracle write
    the same cells. Mutants, run: each offset taking the most it holds,
    as before; the reach of what is left of the aim unasked.
    """
    oracle = _oracle()
    for worn, seeds in ((11, (0, 1, 2, 3, 4, 5)), (13, (0, 3, 4))):
        cells = _repeated_stamps_wearing(worn)
        block, profile, _questions = _described(tmp_path / f"worn-{worn}", cells)
        assert block["format"] == "layout {YYYY}{MM}{DD}{HH}{MI}{SS}{+HHMM?}"
        assert block["utc_offsets"] == {"(none)": 1000}
        assert (block["n_distinct"], block["n_not_numeric"]) == (100 + worn, worn)
        column, facts = _loaded(profile)
        for seed in seeds:
            twin, written = _twin(profile, seed)
            assert _not_numbers(written) == worn, (worn, seed)
            assert len(set(written)) == 100 + worn, (worn, seed)
            assert _validated(profile, twin)[0] == 0, (worn, seed)
            bare = sorted(cell[0:14] for cell in written)
            paid = generation._offsets_owed_by_the_classes(column, facts, list(bare), (), 11)
            assert _not_numbers(paid) == worn, (worn, seed)
            assert oracle.offsets_paid_to_the_classes(block, list(bare), (), 11) == paid, (worn, seed)  # type: ignore[attr-defined]


def _owing_column(
    folder: pathlib.Path,
) -> "tuple[contract.ColumnBlock, contract.DatetimeFacts, dict[str, object]]":
    """A described HL7 column, whose block and facts step 5's own shapes are handed with."""
    block, profile, _questions = _described(folder, _hl7_with_offsets(ROWS, 2))
    column, facts = _loaded(profile)
    return column, facts, block


def _step5_written(
    owing: "tuple[contract.ColumnBlock, contract.DatetimeFacts, dict[str, object]]",
    bare: "list[str]",
    owed: int,
    named: int = 0,
    holes: "tuple[str, ...]" = (),
) -> "list[str]":
    """What the shipped G7.9b pass writes on stamps in rank order, the oracle held to the same cells.

    ``owed`` cells that are not numbers are published; the census names
    ``named`` offsets from `+00:00` up, one cell each, so the offer starts
    after them; ``holes`` are the column's absent spellings.
    """
    column, facts, block = owing
    census = {"(none)": len(bare)}
    for hour in range(named):
        census[f"+{hour:02d}:00"] = 1
    owing_column = dataclasses.replace(column, n_numeric=len(bare) - owed, n_not_numeric=owed)
    paid = generation._offsets_owed_by_the_classes(
        owing_column, dataclasses.replace(facts, utc_offsets=census, n_unparsed=0), list(bare), holes, 11
    )
    owing_block = dict(block, n_numeric=len(bare) - owed, n_not_numeric=owed, utc_offsets=census, n_unparsed=0)
    assert _oracle().offsets_paid_to_the_classes(owing_block, list(bare), holes, 11) == paid  # type: ignore[attr-defined]
    return paid


def _worn_by_text(bare: "list[str]", paid: "list[str]") -> "dict[int, str]":
    """Each text written again -- by its place among the different texts, 0 the lowest -- and its offset.

    Every copy of a text written again wears the same offset, and no copy
    of it is left bare: a text is written whole or not at all.
    """
    order = {text: place for place, text in enumerate(sorted(set(bare)))}
    worn: "dict[int, str]" = {}
    for before, after in zip(bare, paid):
        if after != before:
            assert after[0:14] == before and worn.get(order[before], after[14:]) == after[14:], before
            worn[order[before]] = after[14:]
    for before, after in zip(bare, paid):
        assert (order[before] in worn) == (after != before), before
    return worn


# G7.9b step 5's shapes at floor 11, asked of the pass itself on stamps in
# rank order (`_ranked_stamps`: an end, the texts, an end): the copies of
# each text between the two ends, the cells owed, how many offsets from
# `+00:00` up the census names, the absent spellings as (text, offset)
# pairs, and each text written again -- 1 the first between the ends --
# with the offset it wears. Each line's mutants are named in the clause.
_STEP5_SHAPES: "dict[str, tuple[list[int], int, int, tuple[tuple[int, str], ...], dict[int, str]]]" = {
    "the_aim_over_two_offsets": ([7, 7, 5, 5], 14, 0, (), {1: "+0000", 2: "+0100"}),
    "none_where_only_none_reaches": ([1, 10, 9], 11, 0, (), {1: "+0000", 2: "+0100"}),
    "the_later_rooms_counted": ([9, 6, 6, 5], 17, 13, (), {1: "+1300", 2: "+1400"}),
    "the_aim_a_total_reached": ([10, 3, 8], 12, 12, (), {2: "+1300", 3: "+1200"}),
    "the_most_copies_first": ([2, 2, 5, 4], 4, 0, (), {4: "+0000"}),
    "texts_of_one_size_spread": ([3, 3, 3, 3, 12, 12], 6, 0, (), {1: "+0000", 3: "+0000"}),
    "no_text_standing_alone": ([2, 2, 3, 1, 6], 5, 0, (), {1: "+0000", 2: "+0000", 4: "+0000"}),
    "a_refused_offset_bars_that_offset": ([9, 2], 2, 0, ((2, "+0000"),), {2: "+0100"}),
}


@pytest.mark.parametrize("name", sorted(_STEP5_SHAPES))
def test_cxv_item1_step5_aims_once_and_looks_ahead(tmp_path: pathlib.Path, name: str) -> None:
    """Item 1: G7.9b step 5's aim and its look ahead, each rule on a shape of its own.

    Each shape is written by the shipped pass exactly as listed, the oracle
    writes the same cells, and every text is written whole. Mutants, run,
    one per rule, each turning its own shape red:

    * `the_aim_over_two_offsets` -- 7, 7, 5 and 5 owing 14: `+0000` holds
      ten, and the two fives there would leave four no text fits, so a
      seven goes to each of two offsets. Mutants: each offset taking the
      most it holds, f747e7b's rule, and the reach of what is left of the
      aim unasked -- each writes the two fives, 10.
    * `none_where_only_none_reaches` -- a text standing alone, then texts
      of ten and nine, owing 11: step 4 writes the lone text at `+0000`,
      which then holds nine; the nine there would leave one cell no text
      fits, so `+0000` takes none and the ten goes to `+0100`. Mutant: an
      offset never taking none, which writes the nine, 10.
    * `the_later_rooms_counted` -- 9, 6, 6 and 5 owing 17, `+13:00` and
      `+14:00` alone on offer: no packing of two rooms of ten reaches 17,
      and whatever `+1300` takes leaves more than `+1400` holds, so each
      takes the most it holds, the nine and then a six, 15. Mutants: the
      rooms of the offsets after one unasked, and those rooms counted with
      its own -- each writes two sixes, 12; an offset where nothing reaches
      the rest taking none, which writes nothing.
    * `the_aim_a_total_reached` -- 10, 3 and 8 owing 12, three offsets on
      offer: 12 is no total of the texts, so the aim is 11, the eight at
      `+1200` and the three at `+1300`. Mutant: the aim the rest itself,
      which writes the ten alone, 10.
    * `the_most_copies_first` -- 2, 2, 5 and 4 owing 4: the text of four,
      not the two of two. Mutant: an amount counted from the fewest copies
      up.
    * `texts_of_one_size_spread` -- four texts of three, owing 6: the first
      and the third, choice `j` of `k` at position `j * n // k` (the
      verification's shape (e)). Mutant: the first `k` taken, the first and
      the second.
    * `no_text_standing_alone` -- 2, 2, 3, a text standing alone and 6,
      owing 5: step 4 writes the lone text and step 5 the two texts of two.
      Mutant: texts of one copy on offer to step 5, which takes the three
      and the lone text step 4 already wrote, 4.
    * `a_refused_offset_bars_that_offset` -- 9 and 2 owing 2, the text of
      two's `+0000` an absent spelling: it is barred from `+0000` alone and
      written at `+0100`. Mutant: a refused text set aside whole, as 5e575de
      did, which writes nothing.
    """
    copies, owed, named, refused, expected = _STEP5_SHAPES[name]
    bare = _ranked_stamps(copies)
    order = sorted(set(bare))
    holes = tuple(order[place] + offset for place, offset in refused)
    paid = _step5_written(_owing_column(tmp_path), bare, owed, named, holes)
    assert _worn_by_text(bare, paid) == expected
    worn = collections.Counter(cell[14:] for cell in paid if len(cell) > 14)
    assert not worn or max(worn.values()) < parsing.census_floor(11)



# Step 6's shapes, listed as step 5's are.
_STEP6_SHAPES: "dict[str, tuple[list[int], int, int, tuple[tuple[int, str], ...], dict[int, str]]]" = {
    "one_alone_fewer_beside_a_text_of_two": ([1, 1, 2, 12], 3, 0, (), {1: "+0000", 3: "+0000"}),
    "a_count_the_whole_texts_complete": ([1, 1, 1, 3, 12], 4, 0, (), {1: "+0000", 4: "+0000"}),
    "the_most_texts_alone_that_reach_it": (
        [1, 1, 1, 2, 2, 12], 4, 0, (), {1: "+0000", 2: "+0000", 4: "+0000"}
    ),
    "a_second_pass_kept_only_where_it_writes_more": (
        [2, 7, 8, 1, 8, 5], 20, 13, (), {1: "+1400", 3: "+1300", 4: "+1300", 5: "+1400"}
    ),
    "a_tie_keeps_the_first_pass": (
        [1, 6, 7, 4, 7, 5], 20, 13, (), {1: "+1300", 3: "+1400", 4: "+1300", 6: "+1300"}
    ),
    "step5_after_refused_payments": (
        [1, 1, 1, 1, 2, 12], 4, 0, ((1, "+0000"), (2, "+0000")), {3: "+0000", 4: "+0000", 5: "+0000"}
    ),
}


@pytest.mark.parametrize("name", sorted(_STEP6_SHAPES))
def test_cxv_item1_step6_fewer_texts_alone_where_whole_texts_write_more(
    tmp_path: pathlib.Path, name: str
) -> None:
    """Item 1: G7.9b step 6, a second pass with fewer texts standing alone, kept where it writes more.

    Step 4 wrote every text standing alone it might before step 5 saw the
    rest, so a rest no whole text reaches was left owed where one lone
    text fewer and a text of two would have written it -- five of 180
    twins of repeated stamps. Each shape is written by the shipped pass
    exactly as listed and the oracle writes the same cells. Mutants, run:

    * `one_alone_fewer_beside_a_text_of_two` -- two texts standing alone, a
      text of two and one of twelve, owing 3: both lone texts leave one
      cell no whole text reaches, and the second pass writes one lone text
      and the text of two. Mutants: step 6 withdrawn, and the texts step 5
      may take read only where step 4 leaves two cells or more -- each
      writes the two lone texts, 2.
    * `a_count_the_whole_texts_complete` -- three texts standing alone, a
      text of three and one of twelve, owing 4: two lone texts leave two
      cells no whole text reaches, and one leaves three, which the text of
      three writes; the count is the one whose rest the texts reach.
      Mutant: every total taken as reached, which chooses two lone texts,
      and that second pass writing no more, the three lone texts stand, 3.
    * `the_most_texts_alone_that_reach_it` -- three texts standing alone,
      two of two and one of twelve, owing 4: two lone texts and a text of
      two reach 4, as do the two texts of two alone, and the largest count
      of lone texts is the one taken. Mutant: the fewest, which writes the
      two texts of two.
    * `a_second_pass_kept_only_where_it_writes_more` -- 2, 7, 8, a text
      standing alone, 8 and 5, owing 20 with `+13:00` and `+14:00` alone on
      offer: the first pass writes 19; without the lone text the whole
      texts reach 20 but two rooms of ten hold 18 of them, so the first
      pass's cells stand. Mutant: the second pass kept whatever it writes,
      18.
    * `a_tie_keeps_the_first_pass` -- a text standing alone, then 6, 7, 4,
      7 and 5, owing 20 with `+13:00` and `+14:00` alone on offer: the first
      pass writes 17 with the lone text, and the second, without it, 17 as
      well; a second pass is kept only where it writes more, so the first
      stands. Mutant: the second pass kept on a tie, which writes the text
      of six for the lone text and the five.
    * `step5_after_refused_payments` -- four texts standing alone, two of
      whose `+0000` are absent spellings, a text of two and one of twelve,
      owing 4: step 4, owed the whole bound, makes two payments, and step 5
      writes the text of two for the two cells left. Mutant: the texts
      step 5 may take read only where step 4 is owed less than the bound,
      which writes 2.
    """
    copies, owed, named, refused, expected = _STEP6_SHAPES[name]
    bare = _ranked_stamps(copies)
    order = sorted(set(bare))
    holes = tuple(order[place] + offset for place, offset in refused)
    paid = _step5_written(_owing_column(tmp_path), bare, owed, named, holes)
    assert _worn_by_text(bare, paid) == expected

def test_cxv_item1_step5_offers_only_texts_that_are_numbers(tmp_path: pathlib.Path) -> None:
    """Item 1: step 5 offers a text only where it is a number, so one already wearing an offset is not walked.

    A text of three copies already wearing `+0000`, which the census names,
    then a text standing alone, a text of two and one of ten, fifteen
    owed: step 4 writes the lone text at `+0100`, the first offset on offer,
    and step 5 the text of two there too; the text wearing `+0000` is left
    as it is. Mutant, run: the class unasked, and the walk takes the text
    already wearing an offset, which no field can write again, at each
    offset in turn, so the text of two is written at `+1400`.
    """
    bare = _ranked_stamps([3, 1, 2, 10])
    first = sorted(set(bare))[1]
    worn_cells = [cell + "+0000" if cell == first else cell for cell in bare]
    paid = _step5_written(_owing_column(tmp_path), worn_cells, 15, named=1)
    assert _worn_by_text(worn_cells, paid) == {2: "+0100", 3: "+0100"}


def test_cxv_item2d_step5_takes_no_text_with_a_copy_at_an_end(tmp_path: pathlib.Path) -> None:
    """Item 2 (d): a text one of whose copies is an end is not on offer to step 5.

    The verification's shape: texts of three, twelve and twelve copies and
    a last text standing alone, with no other ends -- the text of three
    holds the first rank, an end the description prints -- and three
    owed. No text fits but the one at the end, so nothing is written, and
    the oracle writes the same. Mutant, run: texts with a copy at an end
    taken, and the three copies of the first text, the end among them,
    are written at `+0000`.
    """
    start = datetime.datetime(2024, 1, 1)
    bare: "list[str]" = []
    for step, size in enumerate([3, 12, 12, 1]):
        bare += [(start + datetime.timedelta(minutes=step)).strftime("%Y%m%d%H%M%S")] * size
    paid = _step5_written(_owing_column(tmp_path), bare, 3)
    assert _worn_by_text(bare, paid) == {}


def test_cxv_item2a_the_choice_stops_only_at_a_layout_reading_every_row() -> None:
    """Item 2 (a): the walk over the candidates stops at one reading every row, not at one reaching the line.

    995 SAS dates with a two-figure day and five with a one-figure day: the
    padded `{DD}{MON}{YYYY}`, first in key order, reaches the line and
    reads 995, and only the flexible `{D}{MON}{YYYY}` reads all 1,000, so
    the column is read under it with nothing left over. Mutant, run: the
    walk stopping at the first candidate that reaches the line, which reads
    the column under `{DD}{MON}{YYYY}` and leaves the five unparsed.
    """
    cells = [f"{10 + place % 19}MAR2023" for place in range(995)]
    cells += [f"{day}APR2023" for day in range(1, 6)]
    described = taxonomy.profile_column("seen_at", 1, cells, 1000, taxonomy.Settings())
    details = described.details or {}
    assert described.role == taxonomy.ROLE_DATETIME
    assert details["format"] == "layout {D}{MON}{YYYY}"
    assert details["n_unparsed"] == 0


def test_cxv_item2b_q5_is_asked_beside_the_codes_question_of_a_member_column(
    tmp_path: pathlib.Path,
) -> None:
    """Item 2 (b): Q5 is handed every coded column read with a two-figure year, not only a layout's.

    970 births from the 1st of January 1931 written `%d/%m/%y`, beside 30
    `UNK`: labels until the code is answered `missing`, then read by the
    day-first member with a two-figure year. The first questions file asks
    the codes question and Q5 together, and one answering run reads every
    birth in 1931 to 1933 and asks nothing more of the column. Mutant, run:
    Q5 handed only the coded columns read under a layout, and the file asks
    about the code alone -- item 5's failure again, on a member's column.
    """
    start = datetime.date(1931, 1, 1)
    cells = [(start + datetime.timedelta(days=day)).strftime("%d/%m/%y") for day in range(970)]
    cells += ["UNK"] * 30
    block, _profile, questions = _described(tmp_path / "asked", cells)
    assert block["role"] == taxonomy.ROLE_LONG_TAIL
    entries = questions["asked"]
    assert isinstance(entries, list)
    codes = [entry for entry in entries if entry["read_as_now"] == asking.ANSWER_KEEP]
    centuries = [entry for entry in entries if entry["read_as_now"] == asking.ANSWER_CENTURY_POSIX]
    assert len(codes) == 1 and len(centuries) == 1
    codes[0]["your_answer"] = asking.ANSWER_NO_DATE
    centuries[0]["your_answer"] = asking.ANSWER_CENTURY_1930
    answers = tmp_path / "answers.json"
    answers.write_text(json.dumps(questions), encoding="utf-8", newline="\n")
    block, _profile, questions = _described(tmp_path / "answered", cells, "--answers", str(answers))
    assert block["format"] == "layout {DD}/{MM}/{YY1930}"
    assert block["n_unparsed"] == 0
    assert f"{block['low_tail']['boundary']}"[0:4] == "1931"  # type: ignore[index]
    assert f"{block['high_tail']['boundary']}"[0:4] == "1933"  # type: ignore[index]
    assert [entry for entry in questions["asked"] if entry["column"] == "seen_at"] == []


def test_cxv_item2c_ly3_holds_a_tails_listed_values_to_the_band(tmp_path: pathlib.Path) -> None:
    """Item 2 (c): LY3 asks a tail's listed values, beside its boundary and the rungs.

    Eleven `01JAN2020`, eleven `02JAN2020`, then daily dates from the 1st
    of March 2020 to 400 cells: the low tail lists `2020-01-01` beside its
    boundary, and the description loads. That listed value moved to 1720,
    before the years `{YYYY}` reads, is refused under LY3. Mutant, run: LY3
    asking the boundaries and the rungs alone, and the edited description
    loads and its twin writes eleven `01JAN1720` the layout cannot read.
    """
    months = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")
    cells = ["01JAN2020"] * 11 + ["02JAN2020"] * 11
    day = datetime.date(2020, 3, 1)
    while len(cells) < 400:
        cells += [f"{day.day:02d}{months[day.month - 1]}{day.year}"]
        day = day + datetime.timedelta(days=1)
    block, profile, _questions = _described(tmp_path, cells)
    assert block["format"] == "layout {DD}{MON}{YYYY}"
    low = block["low_tail"]
    assert isinstance(low, dict) and low["values"] == ["2020-01-01"]
    contract.load_profile(str(profile))
    document = json.loads(profile.read_text(encoding="utf-8"))
    document["columns"][0]["low_tail"]["values"] = ["1720-01-01"]
    edited = fixtures.write_profile(tmp_path, "edited-profile.json", document)
    with pytest.raises(errors.ProfileError) as refused:
        contract.load_profile(str(edited))
    assert "LY3" in str(refused.value)


def test_cxv_item3_step5_respells_only_the_texts_it_writes(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Item 3: step 5 respells the texts it writes, one respelling each, whatever it owes.

    Step 5 respelled every text on offer at every offset it wrote at, each
    offset choosing among them all anew: 68 CPU seconds at a million rows
    owing 140, where one offset's share cost 8. It aims once and respells
    only what the walk takes: 400 texts of two, three, five and seven
    copies, 140 owed, are written at fourteen offsets with one respelling
    for each text written. Mutant, run: every text on offer respelled at
    every offset on offer before the walk, as the choice at each offset
    did, and the respellings outnumber the texts written by 6,000.
    """
    owing = _owing_column(tmp_path)
    bare = _ranked_stamps([(2, 3, 5, 7)[place % 4] for place in range(400)])
    writes = 0
    shipped_added = parsing.layout_offset_added

    def write_counted(cell: str, name: str, offset: str) -> "str | None":
        nonlocal writes
        writes = writes + 1
        return shipped_added(cell, name, offset)

    monkeypatch.setattr(parsing, "layout_offset_added", write_counted)
    paid = _step5_written(owing, bare, 140)
    worn = _worn_by_text(bare, paid)
    assert _not_numbers(paid) == 140
    assert sorted(set(worn.values())) == [f"+{hour:02d}00" for hour in range(14)]
    assert writes == len(worn)


# -- 3b.R2c (P4-D383): THE LAYOUT READER'S QUESTIONS AND PARTIAL DATES ----
#
# Lane R2c's clauses, each red on the mutant its docstring names:
#
# * P1 every partial spelling is read, every cell at some precision
#   (mutant: the partial reading withdrawn);
# * P2 the twin writes each cell at its own precision and spelling, its
#   forms at their published counts, and validates (mutant: the partial
#   cells written as stand-ins);
# * P3 the day-level facts are the full cells' alone (the R2 design
#   skeptic, M5; mutant: a partial cell read at the start of its span);
# * P4 a column a layout reads at the line counts no partial form, so no
#   column R2a reads moves (mutant: forms counted whatever the line);
# * P5 years or months alone are not partial dates, nor a column whose
#   full cells are fewer than half (mutant: a lower half);
# * Q6 a column mostly of dates is asked, and one of dates beside a few
#   codes is R1's question Q2 (M6; mutant: R1's trigger not asked first);
#   the answer `dates` reads at half the cells and validates (mutant: the
#   date rule's own line); a day of the year is read only where declared
#   (mutant: every column declared); and the question names no cell
#   (mutant: an example taken from the column);
# * LY the producer writes no description it cannot load and generate,
#   and no twin that misses, over every partial and declared shape at
#   floors 2, 11 and 36, seeds 0 to 2.
#
# And the repair round's clauses, after its skeptic (each red on 144ac4d
# or on the mutant its docstring names): the battery above validated (a
# form below the census line counted toward the date rule's line); a
# declared column beside one repeated word keeps its dates apart (the
# count pass aimed at the count less the unread cells); Q6 worked out
# once a run; the declaration narrowed to its column; G12.5's lower
# bound, G7.9b's debt and the offset growth of the partial choice each
# on a shape of its own; the four things `--date-column` says; and no
# partial form of a weekday or a day of the year.

_PARTIAL_ROWS = 400


def _partial_forms_of(block: "dict[str, object]") -> "dict[str, int]":
    """A described column's partial forms with their counts."""
    mix = block["resolution_mix"]
    assert isinstance(mix, dict)
    return {key: mix[key] for key in mix if key != block["format"]}


def _form_of(cell: str, block: "dict[str, object]") -> str:
    """The form one twin cell reads under: the layout, one of its partial forms, or ''."""
    items = parsing.layout_items(f"{block['format']}")
    if items is not None and parsing.layout_reading(cell, items) is not None:
        return f"{block['format']}"
    for key in sorted(_partial_forms_of(block)):
        shape = parsing.partial_items(key)
        if shape is not None and parsing.layout_partial_reading(cell, shape) is not None:
            return key
    return ""


@pytest.mark.parametrize("name", sorted(spellings.PARTIAL_SPELLINGS))
def test_r2c_p1_every_partial_spelling_is_read(tmp_path: pathlib.Path, name: str) -> None:
    """P1: a column of partial dates is read under its layout, every cell at some precision."""
    block, _profile, _questions = _described(tmp_path, spellings.cells(name, _PARTIAL_ROWS))
    assert block["role"] == "datetime"
    assert parsing.is_layout_format(f"{block['format']}")
    forms = _partial_forms_of(block)
    assert forms
    assert block["n_unparsed"] == sum(forms.values())


def test_r2c_p1_red_without_the_partial_reading(monkeypatch: pytest.MonkeyPatch) -> None:
    """P1's mutant: the partial reading withdrawn, and a FHIR column is no date."""
    monkeypatch.setattr(taxonomy, "_partial_layout", lambda *_args: None)
    cells = spellings.cells("fhir_partial", _PARTIAL_ROWS)
    described = taxonomy.profile_column("seen_at", 1, cells, len(cells), taxonomy.Settings())
    assert described.role != "datetime"


@pytest.mark.parametrize("name", sorted(spellings.PARTIAL_SPELLINGS))
def test_r2c_p2_each_cell_is_written_at_its_own_precision(tmp_path: pathlib.Path, name: str) -> None:
    """P2: every twin cell in the source's spelling, each form at its count, and the twin validates."""
    block, profile, _questions = _described(tmp_path, spellings.cells(name, _PARTIAL_ROWS))
    forms = _partial_forms_of(block)
    for seed in SEEDS:
        twin, cells = _twin(profile, seed)
        written: "dict[str, int]" = {}
        for cell in cells:
            assert spellings.written_as_the_source(name, cell), cell
            assert spellings.parses(cell, spellings.format_of(name)), cell
            form = _form_of(cell, block)
            written[form] = written.get(form, 0) + 1
        for key in forms:
            assert written.get(key, 0) == forms[key]
        assert _validated(profile, twin)[0] == 0


def test_r2c_p2_red_when_the_partial_cells_are_stand_ins(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """P2's mutant: the partial cells written as made-up stand-ins, and the twin misses."""
    _block, profile, _questions = _described(tmp_path, spellings.cells("fhir_partial", _PARTIAL_ROWS))
    monkeypatch.setattr(generation, "_partial_cells", lambda *_args: [])
    twin, _cells = _twin(profile, 0)
    assert _validated(profile, twin)[0] != 0


def _share_on_the_first(cells: "list[str]", items: "tuple[tuple[str, str], ...]") -> float:
    """The share of the cells a layout reads whole that fall on the 1st of a month."""
    whole = 0
    first = 0
    for cell in cells:
        read = parsing.layout_reading(cell, items)
        if read is None:
            continue
        whole = whole + 1
        if read[0][8:10] == "01":
            first = first + 1
    return first / max(whole, 1)


def test_r2c_p3_the_day_facts_are_the_full_cells_alone(tmp_path: pathlib.Path) -> None:
    """P3 (the R2 design skeptic, M5): the twin's full cells hold the source's share on the 1st within .03."""
    source = spellings.cells("fhir_partial", 2000)
    block, profile, _questions = _described(tmp_path, source)
    items = parsing.layout_items(f"{block['format']}")
    assert items is not None
    real = _share_on_the_first(source, items)
    for seed in SEEDS:
        _twin_path, cells = _twin(profile, seed)
        assert abs(_share_on_the_first(cells, items) - real) <= 0.03


def test_r2c_p3_red_when_a_partial_cell_is_read_at_its_span_start(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """P3's mutant: each partial cell read as the first day of its span, and the 1st heaps."""
    shipped = taxonomy._matching_layout

    def at_the_start(present, settings, contradicted):  # type: ignore[no-untyped-def]
        found = shipped(present, settings, contradicted)
        if found is None:
            return None
        pairs = list(found[1])
        sources = list(found[2])
        for value in present:
            if len(value) in (4, 7) and value[0:4].isdigit():
                pairs += [((value + "-01-01")[0:10], "")]
                sources += [value]
        return (found[0], pairs, sources, len(present) - len(pairs), found[4], found[5])

    monkeypatch.setattr(taxonomy, "_matching_layout", at_the_start)
    source = spellings.cells("fhir_partial", 2000)
    block, profile, _questions = _described(tmp_path, source)
    items = parsing.layout_items(f"{block['format']}")
    assert items is not None
    _twin_path, cells = _twin(profile, 0)
    assert abs(_share_on_the_first(cells, items) - _share_on_the_first(source, items)) > 0.03


def _hl7_with_minutes(rows: int, cut: int) -> "list[str]":
    """HL7 stamps to the second, ``cut`` of them to the minute, spread over the column."""
    found = [moment.strftime("%Y%m%d%H%M%S") for moment in spellings.moments(rows, 5)]
    for place in range(cut):
        spot = (place * rows) // cut
        found[spot] = found[spot][0:12]
    return found


def test_r2c_p4_a_column_read_at_the_line_counts_no_partial_form() -> None:
    """P4: 18 minute cells among 3,000 stamps leave R2a's reading as it was: no form named."""
    cells = _hl7_with_minutes(3000, 18)
    described = taxonomy.profile_column("seen_at", 1, cells, len(cells), taxonomy.Settings())
    details = described.details or {}
    assert details["n_unparsed"] == 18
    assert list(details["resolution_mix"]) == [details["format"]]


def test_r2c_p4_red_when_forms_are_counted_whatever_the_line(monkeypatch: pytest.MonkeyPatch) -> None:
    """P4's mutant: the partial forms counted on a column the layout reads at the line."""
    shipped = taxonomy.layout_partial_counts
    monkeypatch.setattr(
        taxonomy, "layout_partial_counts",
        lambda name, present, _read, settings: shipped(name, present, 0, settings),
    )
    cells = _hl7_with_minutes(3000, 18)
    described = taxonomy.profile_column("seen_at", 1, cells, len(cells), taxonomy.Settings())
    assert len((described.details or {})["resolution_mix"]) == 2


def _fhir_share(rows: int, whole: float) -> "list[str]":
    """FHIR dates, ``whole`` of them to the day and the rest to the month."""
    found: "list[str]" = []
    for place, moment in enumerate(spellings.moments(rows, 9)):
        found += [moment.strftime("%Y-%m-%d" if place % 100 < whole * 100 else "%Y-%m")]
    return found


def test_r2c_p5_years_or_months_alone_are_not_partial_dates() -> None:
    """P5: a column of years, one of months and one whose full cells are 40 in 100 keep their reading."""
    settings = taxonomy.Settings()
    years = [moment.strftime("%Y") for moment in spellings.moments(1000, 3)]
    months = [moment.strftime("%Y-%m") for moment in spellings.moments(1000, 3)]
    assert taxonomy.profile_column("y", 1, years, 1000, settings).role != "datetime"
    assert (taxonomy.profile_column("m", 1, months, 1000, settings).details or {})["format"] == "iso-month"
    assert taxonomy.profile_column("f", 1, _fhir_share(1000, 0.4), 1000, settings).role != "datetime"


def test_r2c_p5_red_on_a_lower_half(monkeypatch: pytest.MonkeyPatch) -> None:
    """P5's mutant: the full layout asked to read 30 in 100, and the 40-in-100 column is claimed."""
    monkeypatch.setattr(taxonomy, "PARTIAL_FULL_SHARE", 0.3)
    cells = _fhir_share(1000, 0.4)
    assert taxonomy.profile_column("f", 1, cells, 1000, taxonomy.Settings()).role == "datetime"


def _q6_shapes() -> "dict[str, list[str]]":
    """Columns the date rule cannot settle, and three it can (made-up cells)."""
    draw = random.Random(17)
    moments = spellings.moments(_PARTIAL_ROWS, 11)
    mixed = [
        (f"{m.month}/{m.day}/{m.year}" if place % 10 < 7 else m.strftime("%Y-%m-%d"))
        for place, m in enumerate(moments)
    ]
    beds = [
        f"{draw.randint(1, 12)}-{draw.randint(1, 28)}-{draw.randint(10, 60):02d}"
        if place % 100 >= 2 else f"{draw.randint(13, 40)}-{draw.randint(1, 28)}-{draw.randint(10, 60):02d}"
        for place in range(_PARTIAL_ROWS)
    ]
    coded = [(m.strftime("%Y-%m-%d") if place % 100 >= 3 else "UNK") for place, m in enumerate(moments)]
    return {
        "mixed": mixed,
        "beds": beds,
        "ordinal": spellings.cells("iso_ordinal", _PARTIAL_ROWS),
        "julian": spellings.cells("julian_seven", _PARTIAL_ROWS),
        "coded": coded,
        "words": [f"note {draw.randint(1, 900)} about the visit" for _row in range(_PARTIAL_ROWS)],
        "figures": [f"{draw.randint(1, 99999)}" for _row in range(_PARTIAL_ROWS)],
    }


def _asked(questions: "dict[str, object]") -> "list[str]":
    """The reasons the questions file asks the one column about."""
    asked = questions["asked"]
    assert isinstance(asked, list)
    return [f"{entry['reason']}" if "reason" in entry else _reason_of(entry) for entry in asked]


def _reason_of(entry: "dict[str, object]") -> str:
    """Which question an entry is, read off the answers it offers."""
    offered = [f"{choice['answer']}" for choice in entry["answers_you_can_give"]]  # type: ignore[union-attr]
    if asking.ANSWER_DATES in offered:
        return "q6"
    if asking.ANSWER_NO_DATE in offered:
        return "q2"
    return "other"


@pytest.mark.parametrize(
    "shape, wanted",
    [("mixed", "q6"), ("beds", "q6"), ("ordinal", "q6"), ("julian", "q6"), ("coded", "q2")],
)
def test_r2c_q6_is_asked_where_the_cells_cannot_settle_it(
    tmp_path: pathlib.Path, shape: str, wanted: str
) -> None:
    """Q6 asks a column mostly of dates or of days of the year; one beside a few codes is Q2's."""
    _block, _profile, questions = _described(tmp_path, _q6_shapes()[shape])
    reasons = _asked(questions)
    assert wanted in reasons
    if wanted == "q2":
        assert "q6" not in reasons


@pytest.mark.parametrize("shape", ["words", "figures"])
def test_r2c_q6_asks_no_column_that_is_not_dates(tmp_path: pathlib.Path, shape: str) -> None:
    """Q6 is put to no column of words or of figures."""
    _block, _profile, questions = _described(tmp_path, _q6_shapes()[shape])
    assert "q6" not in _asked(questions)


def test_r2c_q6_red_when_q2_is_not_asked_first(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Q6's deferral's mutant: R1's trigger not asked first, and the coded column is asked Q6 too."""
    monkeypatch.setattr(asking, "date_codes_of", lambda *_args, **_kwargs: None)
    _block, _profile, questions = _described(tmp_path, _q6_shapes()["coded"])
    assert "q6" in _asked(questions)


def _answered_dates(tmp_path: pathlib.Path, cells: "list[str]") -> "tuple[dict[str, object], pathlib.Path]":
    """Describe a column, answer `dates` to its Q6, and describe it again with the answers."""
    _block, profile, questions = _described(tmp_path / "first", cells)
    for entry in questions["asked"]:  # type: ignore[union-attr]
        if _reason_of(entry) == "q6":
            entry["your_answer"] = asking.ANSWER_DATES
    answers = tmp_path / "answers.json"
    answers.write_text(json.dumps(questions), encoding="utf-8", newline="\n")
    block, again, _questions = _described(tmp_path / "again", cells, "--answers", str(answers))
    return block, again


@pytest.mark.parametrize("shape", ["mixed", "julian"])
def test_r2c_q6_dates_reads_the_column_at_half_and_validates(tmp_path: pathlib.Path, shape: str) -> None:
    """Q6's answer: the column is read as dates at half its cells, and its twin validates."""
    block, profile = _answered_dates(tmp_path, _q6_shapes()[shape])
    assert block["role"] == "datetime"
    document = json.loads(profile.read_text(encoding="utf-8"))
    assert document["settings"]["forced_date_columns"] == ["seen_at"]
    typed, _again, _questions = _described(tmp_path / "typed", _q6_shapes()[shape], "--date-column", "seen_at")
    assert typed == block
    for seed in SEEDS:
        twin, _cells = _twin(profile, seed)
        assert _validated(profile, twin)[0] == 0


def test_r2c_q6_red_on_the_date_rules_own_line(monkeypatch: pytest.MonkeyPatch) -> None:
    """The answer's mutant: a declared column held to the date rule's line, and the mix is no date."""
    monkeypatch.setattr(taxonomy, "DECLARED_DATE_SHARE", 0.99)
    cells = _q6_shapes()["mixed"]
    settings = taxonomy.Settings(forced_date_columns=("seen_at",))
    assert taxonomy.profile_column("seen_at", 1, cells, len(cells), settings).role != "datetime"


def test_r2c_q6_a_day_of_the_year_is_read_only_where_declared() -> None:
    """The ask-first layouts: undeclared, a column of `2023076` is not read as dates."""
    cells = _q6_shapes()["julian"]
    plain = taxonomy.profile_column("seen_at", 1, cells, len(cells), taxonomy.Settings())
    declared = taxonomy.profile_column(
        "seen_at", 1, cells, len(cells), taxonomy.Settings(forced_date_columns=("seen_at",))
    )
    assert plain.role != "datetime"
    assert (declared.details or {})["format"] == "layout {YYYY}{DDD}"


def test_r2c_q6_red_when_every_column_is_declared(monkeypatch: pytest.MonkeyPatch) -> None:
    """The ask-first mutant: every column read as declared dates, and the Julian column is claimed."""
    monkeypatch.setattr(taxonomy, "dates_declared", lambda _settings: True)
    cells = _q6_shapes()["julian"]
    assert taxonomy.profile_column("seen_at", 1, cells, len(cells), taxonomy.Settings()).role == "datetime"


@pytest.mark.parametrize("shape", ["mixed", "beds", "julian"])
def test_r2c_q6_names_no_cell_of_the_column(tmp_path: pathlib.Path, shape: str) -> None:
    """Q6's sentences carry no value of the table (A-P4-58): no cell appears in the questions file."""
    cells = _q6_shapes()[shape]
    _block, _profile, questions = _described(tmp_path, cells)
    text = json.dumps(questions)
    assert "q6" in _asked(questions)
    for cell in set(cells):
        assert f'"{cell}"' not in text and f" {cell} " not in text and f" {cell}," not in text


def test_r2c_q6_red_when_the_example_is_a_cell(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The example's mutant: the column's first cell shown in place of a made-up instant."""
    cells = _q6_shapes()["julian"]
    monkeypatch.setattr(parsing, "format_example", lambda _name: cells[0])
    _block, _profile, questions = _described(tmp_path, cells)
    assert f" {cells[0]}," in json.dumps(questions)


def _battery() -> "dict[str, tuple[list[str], tuple[str, ...]]]":
    """Every partial and declared shape the producer writes, with the flags it is described under."""
    moments = spellings.moments(240, 13)
    upper = [word.upper() for word in ("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec")]

    def cut(writes: "list[str]", shares: "tuple[int, ...]") -> "list[str]":
        found: "list[str]" = []
        for place, moment in enumerate(moments):
            step = place % 100
            index = 0
            total = 0
            for share in shares:
                total = total + share
                if step >= total:
                    index = index + 1
            found += [moment.strftime(writes[min(index, len(writes) - 1)])]
        return found

    shapes: "dict[str, tuple[list[str], tuple[str, ...]]]" = {
        "fhir": (cut(["%Y-%m-%d", "%Y-%m", "%Y"], (58, 27)), ()),
        "fhir_few_years": (cut(["%Y-%m-%d", "%Y-%m", "%Y"], (60, 37)), ()),
        "fhir_half": (cut(["%Y-%m-%d", "%Y-%m"], (50,)), ()),
        "hl7_three": (cut(["%Y%m%d%H%M%S", "%Y%m%d%H%M", "%Y%m%d%H"], (55, 30)), ()),
        "hl7_two": (cut(["%Y%m%d%H%M%S", "%Y%m%d%H%M"], (70,)), ()),
        "hl7_offsets": (
            [
                (moment.strftime("%Y%m%d%H%M%S") + ("-0500" if place % 3 == 0 else ""))
                if place % 100 < 70 else moment.strftime("%Y%m%d%H%M")
                for place, moment in enumerate(moments)
            ],
            (),
        ),
        "oracle_seconds": (cut(["%d-%b-%Y %H:%M:%S", "%d-%b-%Y %H:%M"], (75,)), ()),
        "flexible": (
            [
                f"{m.year}-{m.month}-{m.day}" if place % 100 < 65 else f"{m.year}-{m.month}"
                for place, m in enumerate(moments)
            ],
            (),
        ),
        "dotted": (
            [
                f"{m.day:02d}.{m.month:02d}.{m.year}" if place % 100 < 70 else f"{m.month:02d}.{m.year}"
                for place, m in enumerate(moments)
            ],
            (),
        ),
        "sas": (cut(["%d%b%Y", "%b%Y"], (80,)), ()),
        "medidata": (
            [
                f"{m.day:02d} {upper[m.month - 1]} {m.year}" if place % 100 < 80
                else (f"UN {upper[m.month - 1]} {m.year}" if place % 100 < 92 else f"UN UNK {m.year}")
                for place, m in enumerate(moments)
            ],
            (),
        ),
        "markers_dashed": (
            [
                f"{m.year}-{m.month:02d}-{m.day:02d}" if place % 100 < 85 else f"{m.year}-{m.month:02d}---"
                for place, m in enumerate(moments)
            ],
            (),
        ),
        "slashed_years": (
            [f"{m.month:02d}/{m.day:02d}/{m.year}" if place % 100 < 80 else f"{m.year}" for place, m in enumerate(moments)],
            (),
        ),
        # Forms on fewer cells than the line at eleven and at 36: absorbed.
        "sparse": (cut(["%Y-%m-%d", "%Y-%m", "%Y"], (95, 3)), ()),
        "ordinal": ([moment.strftime("%Y-%j") for moment in moments], ("--date-column", "seen_at")),
        "julian": ([moment.strftime("%Y%j") for moment in moments], ("--date-column", "seen_at")),
        "declared_mix": (
            [f"{m.month}/{m.day}/{m.year}" if place % 10 < 6 else "pending" for place, m in enumerate(moments)],
            ("--date-column", "seen_at"),
        ),
        "declared_partial": (cut(["%Y-%m-%d", "%Y-%m", "%Y"], (52, 30)), ("--date-column", "seen_at")),
        # Skeptic 2 of the repair, item 2: the layout's named months count as read.
        "declared_few_years": (cut(["%Y-%m-%d", "%Y-%m", "%Y"], (60, 37)), ("--date-column", "seen_at")),
    }
    # Skeptic 2 of the repair, item 1: a form of figures below the census
    # line, within the room, at 2,000 and 10,000 rows (made up).
    more = spellings.moments(2000, 13)
    most = spellings.moments(10000, 13)
    shapes["figures_fhir_2k"] = (
        [m.strftime("%Y-%m-%d") for m in more[:1400]]
        + [m.strftime("%Y-%m") for m in more[1400:1990]]
        + [m.strftime("%Y") for m in more[1990:]],
        (),
    )
    shapes["figures_fhir_10k"] = (
        [
            m.strftime("%Y") if place % 2000 == 7
            else (m.strftime("%Y-%m-%d") if place % 10 < 7 else m.strftime("%Y-%m"))
            for place, m in enumerate(most)
        ],
        (),
    )
    shapes["figures_hl7_2k"] = (
        [m.strftime("%Y%m%d%H%M%S") for m in more[:1400]]
        + [m.strftime("%Y%m%d%H%M") for m in more[1400:1990]]
        + [m.strftime("%Y%m%d%H") for m in more[1990:]],
        (),
    )
    return shapes


# A form below the census line leaves this column to the reading it had
# before the landing (the repair, item 1): its free-text twin misses its
# mean length there on the landing's base as well, which is the free-text
# writer's and none of this landing's, so only the reading is held.
_UNREAD_AS_BEFORE = {("fhir_few_years", 11), ("fhir_few_years", 36)}


@pytest.mark.parametrize("floor", [2, 11, 36])
@pytest.mark.parametrize("shape", sorted(_battery()))
def test_r2c_every_description_the_producer_writes_loads_and_generates(
    tmp_path: pathlib.Path, shape: str, floor: int
) -> None:
    """The producer-always-loads battery of LY6, LY7 and S8f: every description loads and every twin validates.

    The repair round, item 1: a partial form below the census line counted
    toward the date rule's line, though its cells are written as stand-ins,
    so six of these shapes were read as dates and their twins, re-read, were
    no date at all: `axes.role` missed at seeds 0 to 2 (fhir, hl7_three,
    markers_dashed and medidata at 36, sparse at 11 and 36). Red on 144ac4d.

    Skeptic 2 of the repair, item 1: the three `figures_*` shapes, a form
    of figures below the line written `text-N`, missed `n_numeric` and
    `n_not_numeric` at every seed and both floors; item 2:
    `declared_few_years` was read as `iso-date` with its months written
    `text-N`. Red on dd6b77f.
    """
    cells, flags = _battery()[shape]
    block, profile, _questions = _described(tmp_path, cells, *flags, floor=floor)
    contract.load_profile(str(profile))
    if (shape, floor) in _UNREAD_AS_BEFORE:
        assert block["role"] != "datetime"
        _twin(profile, 0)
        return
    for seed in SEEDS:
        twin, _cells = _twin(profile, seed)
        assert _validated(profile, twin)[0] == 0, (shape, floor, seed)


# -- the repair round's clauses (3b.R2c, P4-D383) -----------------------

_SLASHED_DATE = re.compile(r"[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}")


def _pending(rows: int, share: int) -> "list[str]":
    """Dates written `m/d/yyyy` on ``share`` rows in a hundred and `pending` on the rest (made up)."""
    return [
        f"{m.month}/{m.day}/{m.year}" if place % 100 < share else "pending"
        for place, m in enumerate(spellings.moments(rows, 13))
    ]


def _date_spread(cells: "list[str]") -> "tuple[int, int]":
    """How many different dates the cells hold, and the most copies of one."""
    copies: "dict[str, int]" = {}
    for cell in cells:
        if _SLASHED_DATE.fullmatch(cell):
            copies[cell] = (copies[cell] if cell in copies else 0) + 1
    most = 0
    for cell in copies:
        most = max(most, copies[cell])
    return len(copies), most


@pytest.mark.parametrize("floor", [11, 36])
@pytest.mark.parametrize("rows, share", [(240, 60), (2000, 80)])
def test_r2c_q6_a_declared_column_beside_one_word_keeps_its_dates_apart(
    tmp_path: pathlib.Path, rows: int, share: int, floor: int
) -> None:
    """Item 2: `--date-column` on dates beside a repeated `pending` keeps the different dates.

    The count pass aimed at `n_distinct` less `n_unparsed`, which counts
    `pending` once and the twin's made-up stand-ins once each: 149
    different dates of a 240-row column came back as 70, one of them on 41
    rows, and validation passed. The twin's different dates now fall within
    a tenth of the source's, no date on more than two rows more than the
    source's commonest, and it validates. Red on 144ac4d.
    """
    cells = _pending(rows, share)
    _block, profile, _questions = _described(tmp_path, cells, "--date-column", "seen_at", floor=floor)
    distinct, most = _date_spread(cells)
    for seed in SEEDS:
        twin, written = _twin(profile, seed)
        found, heaviest = _date_spread(written)
        assert abs(found - distinct) * 10 <= distinct, (seed, found, distinct)
        assert heaviest <= most + 2, (seed, heaviest, most)
        assert _validated(profile, twin)[0] == 0


def test_r2c_q6_red_when_the_count_pass_aims_at_the_declared_column(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Item 2's mutant: the loader's mark withdrawn, and the dates are squeezed again."""
    monkeypatch.setattr(contract, "_declared_short", lambda facts, *_args: facts)
    cells = _pending(240, 60)
    _block, profile, _questions = _described(tmp_path, cells, "--date-column", "seen_at")
    distinct, _most = _date_spread(cells)
    _twin_path, written = _twin(profile, 0)
    assert _date_spread(written)[0] * 10 < distinct * 9


def test_r2c_q6_is_worked_out_once_a_run(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Item 3: one profile run asks `date_column_questions` once, for the screen and the file.

    Each call describes every candidate again under the declaration, three
    to four times its own describe; the run made two identical calls.
    Mutant, run: the questions file's call made whatever the first found.
    """
    shipped = asking.date_column_questions
    calls = {"made": 0}

    def counted(*args: object, **kwargs: object) -> object:
        calls["made"] = calls["made"] + 1
        return shipped(*args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(asking, "date_column_questions", counted)
    _block, _profile, questions = _described(tmp_path, _q6_shapes()["mixed"])
    assert "q6" in _asked(questions)
    assert calls["made"] == 1


def test_r2c_q6_the_declaration_reaches_only_the_column_it_names(tmp_path: pathlib.Path) -> None:
    """Item 4: `--date-column a` leaves column b, seven-figure codes like `2023076`, as it was read.

    Mutant, run: every column given the declaration (`for_the_column`
    widened), and b is read as days of the year nobody declared.
    """
    first = _q6_shapes()["mixed"]
    second = _q6_shapes()["julian"]
    table = tmp_path / "real.csv"
    lines = ["a,b"] + [f"{one},{two}" for one, two in zip(first, second)]
    table.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    assert _exit_of(
        ["profile", str(table), "--out-dir", str(tmp_path), "--replace", "--date-column", "a"]
    ) == 0
    profile = tmp_path / "real-profile.json"
    contract.load_profile(str(profile))
    columns = json.loads(profile.read_text(encoding="utf-8"))["columns"]
    alone = taxonomy.profile_column("b", 2, second, len(second), taxonomy.Settings())
    assert columns[0]["role"] == "datetime"
    assert columns[1]["role"] == alone.role != "datetime"


@pytest.mark.parametrize("floor", [11, 36])
def test_r2c_p2_days_beside_years_meet_their_count(tmp_path: pathlib.Path, floor: int) -> None:
    """Item 6: G12.5's lower bound counts a partial form once, on 2,000 FHIR dates 55 in 100 to the day.

    Mutant, run: the lower bound counting every partial cell as a value of
    its own, and `n_distinct` and `n_distinct_folded` miss at every seed.
    """
    cells = [
        m.strftime("%Y-%m-%d" if place % 100 < 55 else "%Y")
        for place, m in enumerate(spellings.moments(2000, 13))
    ]
    block, profile, _questions = _described(tmp_path, cells, floor=floor)
    assert _partial_forms_of(block) == {"layout {YYYY}": 900}
    for seed in SEEDS:
        twin, _cells = _twin(profile, seed)
        assert _validated(profile, twin)[0] == 0


def _hl7_beside_offsets() -> "list[str]":
    """1,000 HL7 stamps: 300 cut to the minute, and seven of the rest ending `-0500` (made up)."""
    found: "list[str]" = []
    for place, m in enumerate(spellings.moments(1000, 13)):
        if place % 100 >= 70:
            found += [m.strftime("%Y%m%d%H%M")]
            continue
        text = m.strftime("%Y%m%d%H%M%S")
        if place % 100 == 7 and place < 700:
            text = text + "-0500"
        found += [text]
    return found


@pytest.mark.parametrize("floor", [11, 36])
def test_r2c_g79b_a_partial_run_of_figures_owes_no_offset(tmp_path: pathlib.Path, floor: int) -> None:
    """Item 7: G7.9b's debt counts the cells cut to the minute as the numbers they are.

    Seven offsets, fewer than the census line, are counted into `(none)`
    and owed by `n_not_numeric`; the 300 partial cells are inside
    `n_unparsed` and are numbers, so a debt less every unread cell is
    below nought and the twin wrote no offset. Its layout is grown from
    the seven it missed, wherever they stand (`_layout_extended`): read
    from the sample, the twin, whose seven fell elsewhere, missed
    `n_unparsed` at two seeds of three.
    """
    block, profile, _questions = _described(tmp_path, _hl7_beside_offsets(), floor=floor)
    assert block["format"] == "layout {YYYY}{MM}{DD}{HH}{MI}{SS}{+HHMM?}"
    assert _partial_forms_of(block) == {"layout {YYYY}{MM}{DD}{HH}{MI}": 300}
    assert block["n_not_numeric"] == 7
    for seed in SEEDS:
        twin, cells = _twin(profile, seed)
        assert len([cell for cell in cells if not cell.isdigit()]) == 7
        assert _validated(profile, twin)[0] == 0


def test_r2c_g79b_red_when_the_debt_takes_every_unread_cell(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Item 7's mutant: no partial cell counted a number, and the twin writes no offset."""
    monkeypatch.setattr(generation, "_partial_numbers", lambda _facts: 0)
    _block, profile, _questions = _described(tmp_path, _hl7_beside_offsets())
    twin, cells = _twin(profile, 0)
    assert all(cell.isdigit() for cell in cells)
    assert _validated(profile, twin)[0] != 0


def test_r2c_red_when_the_partial_choice_is_not_grown(monkeypatch: pytest.MonkeyPatch) -> None:
    """The growth's mutant: no layout grown from the misses, and the seven are stand-ins."""
    monkeypatch.setattr(taxonomy, "_layout_extended", lambda *_args: [])
    cells = _hl7_beside_offsets()
    described = taxonomy.profile_column("seen_at", 1, cells, len(cells), taxonomy.Settings())
    assert (described.details or {})["format"] == "layout {YYYY}{MM}{DD}{HH}{MI}{SS}"


def _one_column_table(tmp_path: pathlib.Path, cells: "list[str]") -> pathlib.Path:
    """A one-column table of ``cells``, written as `_described` writes it."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    table = tmp_path / "real.csv"
    names, rows = fixtures.rows_at_the_floor("seen_at", cells)
    table.write_text(fixtures.rows_to_csv(names, rows), encoding="utf-8", newline="\n")
    return table


def test_r2c_q6_an_unknown_date_column_is_refused(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Item 8: `--date-column` naming no column is refused, and no description is written.

    Mutant, run: the check withdrawn, and a description S8 refuses is written.
    """
    table = _one_column_table(tmp_path, _q6_shapes()["mixed"])
    capsys.readouterr()
    code = _exit_of(
        ["profile", str(table), "--out-dir", str(tmp_path), "--replace", "--date-column", "no_such"]
    )
    said = capsys.readouterr()
    assert code == 2
    assert "no_such" in said.out + said.err
    assert not (tmp_path / "real-profile.json").exists()


def test_r2c_q6_a_declaration_that_reaches_no_column_is_said(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Item 8: `--date-column` on a column of words is warned about. Mutant, run: the warning withdrawn."""
    table = _one_column_table(tmp_path, _q6_shapes()["words"])
    capsys.readouterr()
    assert _exit_of(
        ["profile", str(table), "--out-dir", str(tmp_path), "--replace", "--date-column", "seen_at"]
    ) == 0
    said = capsys.readouterr()
    assert errors.the_dates_declaration_did_not_reach("seen_at", "free_text")[0:60] in said.out + said.err


def test_r2c_q6_the_answer_is_on_the_repeat_line(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Item 8: the answer `dates` is said again as `--date-column`. Mutant, run: left off the line."""
    cells = _q6_shapes()["mixed"]
    _block, _profile, questions = _described(tmp_path / "first", cells)
    for entry in questions["asked"]:  # type: ignore[union-attr]
        if _reason_of(entry) == "q6":
            entry["your_answer"] = asking.ANSWER_DATES
    answers = tmp_path / "answers.json"
    answers.write_text(json.dumps(questions), encoding="utf-8", newline="\n")
    capsys.readouterr()
    _described(tmp_path / "again", cells, "--answers", str(answers))
    said = capsys.readouterr()
    assert "--date-column seen_at" in said.out + said.err


def test_r2c_q6_is_said_on_the_screen(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Item 8: a column Q6 asks is named on the screen as well. Mutant, run: the notice withdrawn."""
    capsys.readouterr()
    _described(tmp_path, _q6_shapes()["mixed"])
    said = capsys.readouterr()
    assert "THESE COLUMNS MAY HOLD DATES" in said.out
    assert "'seen_at'" in said.out


@pytest.mark.parametrize(
    "name",
    [
        "layout {Dy} {DD} {Mon} {YYYY}",
        "layout {Day}, {DD}-{MM}-{YYYY}",
        "layout {YYYY}{DDD}",
        "layout {YYYY}-{DDD}",
    ],
)
def test_r2c_no_partial_form_of_a_weekday_or_a_day_of_the_year(name: str) -> None:
    """Item 9: a layout with a field outside the partial levels has no partial form.

    Mutant, run: the field passed over rather than refused, and a weekday
    layout gains cuts and masks.
    """
    assert parsing.is_layout_name(name)
    assert parsing.layout_truncations(name) == ()


# -- skeptic 2 of the repair (3b.R2c, P4-D383) ---------------------------


def test_r2c_figures_red_when_no_stand_in_is_a_figure(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Item 1's mutant: every stand-in written `text-N`, and the count of numbers is missed again."""
    monkeypatch.setattr(generation, "_figures_owed", lambda *_args: 0)
    cells, _flags = _battery()["figures_fhir_2k"]
    _block, profile, _questions = _described(tmp_path, cells)
    twin, _cells = _twin(profile, 0)
    code, report = _validated(profile, twin)
    assert code == 3 and "n_numeric" in report


@pytest.mark.parametrize("floor", [11, 36])
def test_r2c_declared_few_years_is_read_under_the_layout(tmp_path: pathlib.Path, floor: int) -> None:
    """Item 2: `--date-column` on days, months and a few years keeps the layout and names the months.

    The member tied the layout on whole pairs and won, and named no
    partial form: every month cell became `text-N` and the twin exited 3.
    Mutant, run: the named partial counts left out of the comparison.
    """
    cells, flags = _battery()["declared_few_years"]
    block, _profile, _questions = _described(tmp_path, cells, *flags, floor=floor)
    assert block["format"] == "layout {YYYY}-{MM}-{DD}"
    mix = block["resolution_mix"]
    assert isinstance(mix, dict) and mix["layout {YYYY}-{MM}"] > 0


def _distinct_present(cells: "list[str]") -> int:
    """How many different cells a column holds, its stand-ins among them."""
    return len(set(cells))


def _first_of_month() -> "list[str]":
    """10,000 FHIR cells: 70 in 100 the first of a month, 29 a month, 1 a year (made up)."""
    return [
        m.strftime("%Y-%m-01") if place % 100 < 70 else (m.strftime("%Y-%m") if place % 100 < 99 else m.strftime("%Y"))
        for place, m in enumerate(spellings.moments(10000, 13))
    ]


def _repeating_declared() -> "list[str]":
    """2,000 cells: twelve dates repeated on 60 in 100 rows, `pending` on the rest (made up)."""
    return [f"{1 + place % 12}/{1 + place % 3}/2023" if place % 10 < 6 else "pending" for place in range(2000)]


@pytest.mark.parametrize("floor", [11, 36])
@pytest.mark.parametrize("shape", ["first_of_month", "repeating_declared"])
def test_r2c_repeating_dates_keep_their_count(tmp_path: pathlib.Path, shape: str, floor: int) -> None:
    """Item 3: where the dates repeat, a partial or declared-short twin keeps near the source's different values.

    With no count target the twin spread its ranks over the whole range:
    75 different values came back as 1,045, and 12 declared dates as 262
    to 267, and validation passed. G7.3 now aims at an upper target
    (`contract.datetime_count_target`): at most 1.5 times the source's
    different values, and the twin validates. Red on dd6b77f.
    """
    cells = _first_of_month() if shape == "first_of_month" else _repeating_declared()
    flags = () if shape == "first_of_month" else ("--date-column", "seen_at")
    _block, profile, _questions = _described(tmp_path, cells, *flags, floor=floor)
    source = _distinct_present(cells)
    for seed in SEEDS:
        twin, written = _twin(profile, seed)
        found = _distinct_present(written)
        if shape == "repeating_declared":
            source, found = _date_spread(cells)[0], _date_spread(written)[0]
        assert found * 2 <= source * 3, (seed, found, source)
        assert _validated(profile, twin)[0] == 0


def test_r2c_repeating_red_when_no_target_is_given(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Item 3's mutant: the upper target withdrawn, and the declared dates spread again."""
    shipped = contract.datetime_count_target

    def exact_only(column: "contract.ColumnBlock", parsed: int) -> int:
        if not contract.datetime_counts_reachable(column):
            return -1
        return shipped(column, parsed)

    monkeypatch.setattr(contract, "datetime_count_target", exact_only)
    cells = _repeating_declared()
    _block, profile, _questions = _described(tmp_path, cells, "--date-column", "seen_at")
    _twin_path, written = _twin(profile, 0)
    assert _date_spread(written)[0] * 2 > _date_spread(cells)[0] * 3


@pytest.mark.parametrize("unread, short", [(2, False), (3, True)])
def test_r2c_declared_mark_at_the_line(tmp_path: pathlib.Path, unread: int, short: bool) -> None:
    """Item 4: at 240 rows the line leaves room for two unread cells; three mark the column short.

    Mutant, run: `_declared_short`'s `<=` turned into `<` marks the column
    read at exactly the line.
    """
    cells = [
        f"{m.month}/{m.day}/{m.year}" if place >= unread else "pending"
        for place, m in enumerate(spellings.moments(240, 13))
    ]
    _block, profile, _questions = _described(tmp_path, cells, "--date-column", "seen_at")
    facts = contract.load_profile(str(profile)).columns[0].facts
    assert isinstance(facts, contract.DatetimeFacts)
    assert facts.n_unparsed == unread
    assert facts.declared_short_of_the_line is short


# -- The R2c leftover verify, finding 1: an upper target lowers, never raises --


def _partial_fhir_unfilled(rows: int) -> "list[str]":
    """FHIR cells over three years: 70 in 100 a day, 27 a month, 3 a year (made up).

    The full dates do not fill their range, so the full ranks drawn hold
    fewer different days than the target the count pass is given.
    """
    return [
        m.strftime("%Y-%m-%d") if place % 100 < 70 else (m.strftime("%Y-%m") if place % 100 < 97 else m.strftime("%Y"))
        for place, m in enumerate(spellings.moments(rows, 11))
    ]


def _battery_fhir_partial() -> "list[str]":
    """The reach battery's `fhir_partial`: 1,000 days of 2021 to 2024, 15 in 100 a year, 25 a month (made up)."""
    draw = random.Random(zlib.crc32(b"fhir_partial"))
    found: "list[str]" = []
    for _row in range(1000):
        day = datetime.date(2021, 1, 1) + datetime.timedelta(days=draw.randrange(1461))
        share = draw.random()
        found += [day.strftime("%Y") if share < 0.15 else (day.strftime("%Y-%m") if share < 0.40 else day.strftime("%Y-%m-%d"))]
    return found


def test_r2c_partial_fhir_holds_its_count(tmp_path: pathlib.Path) -> None:
    """Finding 1, the battery shape: 1,000 FHIR partial cells keep their different values exactly at seed 0.

    Reached exactly, the upper target raised this column from 534
    different values to 586 (a1f8adb). `_units_settled` now runs no pass
    where the full ranks hold no more units than it.
    """
    block, profile, _questions = _described(tmp_path, _battery_fhir_partial())
    twin, written = _twin(profile, 0)
    assert _distinct_present(written) == block["n_distinct"]
    assert _validated(profile, twin)[0] == 0


def test_r2c_unfilled_partial_fhir_stays_within_three_in_a_hundred(tmp_path: pathlib.Path) -> None:
    """Finding 1: 2,000 partial FHIR cells over three years keep their different values within 3 %.

    a1f8adb wrote 868 to 875 against the source's 828 (made-up shape of
    the verifier's probe); dd6b77f and this head 819 to 844.
    """
    block, profile, _questions = _described(tmp_path, _partial_fhir_unfilled(2000))
    source = block["n_distinct"]
    assert isinstance(source, int)
    for seed in SEEDS:
        twin, written = _twin(profile, seed)
        assert abs(_distinct_present(written) - source) * 100 <= source * 3, (seed, source)
        assert _validated(profile, twin)[0] == 0


def test_r2c_unfilled_partial_fhir_red_when_the_target_is_reached_exactly(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Finding 1's mutant: the upper target never counted as met, so the pass raises the count past 3 %."""
    monkeypatch.setattr(generation, "_upper_target_met", lambda *_args: False)
    block, profile, _questions = _described(tmp_path, _partial_fhir_unfilled(2000))
    source = block["n_distinct"]
    assert isinstance(source, int)
    _twin_path, written = _twin(profile, 0)
    assert abs(_distinct_present(written) - source) * 100 > source * 3, source
