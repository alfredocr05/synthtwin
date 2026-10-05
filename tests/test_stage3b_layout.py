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
"""

import csv
import io
import json
import pathlib
import random
import sys

import pytest

from synthtwin import asking, contract, parsing, taxonomy, validation
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
