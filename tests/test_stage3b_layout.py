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
"""

import csv
import datetime
import io
import json
import pathlib
import random
import re
import sys

import pytest

from synthtwin import asking, contract, errors, parsing, taxonomy, validation
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
    folder: pathlib.Path, cells: "list[str]", *flags: str
) -> "tuple[dict[str, object], pathlib.Path, dict[str, object]]":
    """Describe one column the way `synthtwin profile` does."""
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "real.csv"
    names, rows = fixtures.rows_at_the_floor("seen_at", cells)
    table.write_text(fixtures.rows_to_csv(names, rows), encoding="utf-8", newline="\n")
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
