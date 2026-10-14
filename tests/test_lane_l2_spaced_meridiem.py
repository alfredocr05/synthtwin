"""LANE L2: forms that hold a space -- the spaced meridiem (plan P4-D392, 2026-10-14).

`parsing.shape_form` gave no form to a cell holding a space or U+202F
(contract C6-31a, section 7.9), so a column of `9:15 AM` or
`08:15:30.123 AM` -- or with the narrow no-break space U+202F, as Excel and
macOS write it -- beside rare words published no forms, and its twin wrote
0 of its 969 clock cells in their shape where `9:15AM` wrote 969 (X4 in
tests/test_stage3b_layout.py). A form now holds ONE space or ONE U+202F,
standing as itself, between a clock's figures and a meridiem marker, and
nowhere else (option (a) of P4-D392; option (b), one interior space
anywhere, moved 27 descriptions of the lane's battery that hold no spaced
meridiem, made-up names and `Ward 7` among them, where (a) moved none).

Each clause is red on the mutant its docstring names:

* G1 the cells that take a form and the cells that do not (mutants: the
  gap refused, as before L2; one interior gap anywhere, option (b));
* G2 the loader's key rule agrees with the producer on every gapped form
  and refuses every other gapped key (mutant: the key rule blind to gaps);
* G3 every cell holding no gap a meridiem marker stands behind has the
  form it had before L2 (mutant: the gap rule taking a cell it should
  not);
* G4 the clock supply of a U+202F form writes U+202F, and its words are
  two (mutants: `_clock_shape` reading only a plain space; `_form_words`
  blind to U+202F);
* G5 the producer always loads: every spaced-meridiem shape, at floors 2,
  11 and 36, is described, loaded, generated and validated, twin and
  table, each gap written back as the source wrote it;
* G6 a description written before L2 (6a248e7) loads, generates the twin
  6a248e7 generated and validates;
* G7 machine-free: one gap scan per cell ending in a marker's last
  character and none for any other, at every column size, so a census of
  1,000,000 cells costs at most 1,000,000 scans of at most 24 characters.
"""

from __future__ import annotations

import contextlib
import csv
import hashlib
import io
import json
import pathlib
import random
import re
import sys

import pytest

from synthtwin import contract, generation, parsing, taxonomy
from tests import lane_l2_described_before as before

NARROW = "\u202f"


def _exit_of(argv: "list[str]") -> int:
    """Run one synthtwin command in this process and return its exit code."""
    from synthtwin import cli

    saved = sys.argv
    sys.argv = ["synthtwin"] + argv
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            code = cli.main()
    except SystemExit as stop:
        return 0 if stop.code is None else int(stop.code)
    finally:
        sys.argv = saved
    return code


def _round(
    folder: pathlib.Path, cells: "list[str]", floor: int
) -> "tuple[dict[str, object], list[str], int, int]":
    """Describe, load, generate and validate one column: its block, its twin, both exits."""
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "real.csv"
    table.write_text("seen_at\n" + "\n".join(cells) + "\n", encoding="utf-8", newline="\n")
    assert _exit_of(
        ["profile", str(table), "--out-dir", str(folder), "--replace", "--smallest-group", str(floor)]
    ) == 0
    profile = folder / "real-profile.json"
    contract.load_profile(str(profile))
    block = json.loads(profile.read_text(encoding="utf-8"))["columns"][0]
    out = folder / "twin"
    out.mkdir(exist_ok=True)
    assert _exit_of(["generate", str(profile), "--seed", "0", "--out-dir", str(out), "--replace"]) == 0
    twin = out / "real-twin.csv"
    rows = list(csv.reader(io.StringIO(twin.read_text(encoding="utf-8"))))
    written = [row[0] for row in rows[1:] if row and row[0] != ""]
    checks = []
    for checked, name in ((twin, "vt"), (table, "vs")):
        report = folder / name
        report.mkdir(exist_ok=True)
        checks += [
            _exit_of(["validate", str(profile), "--twin", str(checked), "--out-dir", str(report), "--replace"])
        ]
    return block, written, checks[0], checks[1]


# -- G1: which cells take a form ------------------------------------------

_GAPPED = {
    "9:15 AM": "%:%% @@",
    "12:05 pm": "%%:%% @@",
    "9:15" + NARROW + "AM": "%:%%" + NARROW + "@@",
    "08:15:30 PM": "%%:%%:%% @@",
    "08:15:30.123 AM": "%%:%%:%%.%%% @@",
    "7:30:00.5" + NARROW + "p.m.": "%:%%:%%.%" + NARROW + "@.@.",
    "11:59 A.M.": "%%:%% @.@.",
}

_FORMLESS = (
    "9:15  AM",  # two spaces
    "9:15 Am",  # a marker no clock writes
    "9:15 XM",
    "9 AM",  # no minutes
    "12:30.5 PM",  # a fraction after the minutes
    "9:15 AM ",  # a trailing space
    " 9:15 AM",
    "9:15\u00a0AM",  # a no-break space
    "9:15\u2009AM",  # a thin space
    "2024-01-05 9:15 AM",  # two gaps
    "2024-01-05 9:15AM",
    "Ward 7",
    "Bed 12A",
    "120/80 mmHg",
    "250 mg",
    "AM 9:15",
    "9:15 AM PM",
    "9:5 AM",
    "123:15 AM",
)


def test_g1_a_clock_before_its_marker_holds_one_gap_and_nothing_else_does() -> None:
    """G1: the gap a marker stands behind is kept as itself; every other space stays formless.

    Mutants (below): the gap refused, as before L2, turns the gapped half
    red; a tail that need not be a marker word gives `9:15 Am` and
    `9:15 XM` a form; a head that need not be a clock gives `9 AM` and
    `12:30.5 PM` one.
    """
    for cell, form in _GAPPED.items():
        assert parsing.shape_form(cell) == form, cell
        gap = " " if " " in cell else NARROW
        assert parsing.meridiem_gap_at(cell) == cell.index(gap), cell
    for cell in _FORMLESS:
        assert parsing.shape_form(cell) == "", cell
        assert parsing.meridiem_gap_at(cell) == -1, cell
    # No key names a marker word, and a key is no cell (C6-31a).
    for form in _GAPPED.values():
        assert "A" not in form and "P" not in form and "M" not in form
        assert parsing.shape_form(form) == ""


def test_g1_red_where_the_gap_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTATION: no gap admitted, as on 6a248e7: every gapped cell is formless."""
    monkeypatch.setattr(parsing, "meridiem_gap_at", lambda text: -1)
    assert [cell for cell in _GAPPED if parsing.shape_form(cell)] == []


def test_g1_red_where_the_tail_is_any_word(monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTATION: a tail that need not be one of the eight marker words."""
    monkeypatch.setattr(
        parsing, "_SHAPE_MERIDIEM_WORDS", parsing._SHAPE_MERIDIEM_WORDS + ("Am", "XM")
    )
    assert parsing.shape_form("9:15 Am") == "%:%% @@"
    assert parsing.shape_form("9:15 XM") == "%:%% @@"


def test_g1_red_where_the_head_is_any_figures(monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTATION: a head that need not be a clock's figures."""
    monkeypatch.setattr(parsing, "_is_a_clock_body_form", lambda head: True)
    assert parsing.shape_form("9 AM") == "% @@"
    assert parsing.shape_form("12:30.5 PM") == "%%:%%.% @@"


# -- G2: the loader's key rule ---------------------------------------------


def test_g2_every_gapped_form_is_a_written_form_and_no_other_gapped_key_is() -> None:
    """G2: producer and loader agree, the lower-case key included (P4-D121).

    Mutant: `is_a_written_form` blind to gaps (`_key_gap_at` answers -1)
    refuses every key the producer now writes, so every description of
    such a column would be refused on load.
    """
    for form in _GAPPED.values():
        assert parsing.is_a_written_form(form), form
        lower = parsing.lower_case_form(form)
        assert parsing.is_a_written_form(lower), lower
    for key in (
        "%:%%  @@",
        "%:%% @@@",
        "% @@",
        "@@@@ %",
        "%%%% @@",
        "%:%% @&",
        "%:%%\u00a0@@",
        "%:%% @@ ",
        " %:%% @@",
        "%%%%-%%-%% %:%% @@",
        "%%:%%.% @@",
    ):
        assert not parsing.is_a_written_form(key), key


def test_g2_red_where_the_key_rule_is_blind_to_gaps(monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTATION: the key rule without its gap: no gapped key loads."""
    monkeypatch.setattr(parsing, "_key_gap_at", lambda name: -1)
    assert [form for form in _GAPPED.values() if parsing.is_a_written_form(form)] == []


# -- G3: nothing else moves ------------------------------------------------


def _shape_form_before_l2(text: str) -> str:
    """`parsing.shape_form` as 6a248e7 wrote it, for the cells L2 must not move."""
    if not text or len(text) > parsing.SHAPE_FORM_LIMIT:
        return ""
    form = ""
    figures = letters = marks = 0
    for character in text:
        if character in (parsing.SHAPE_DIGIT, parsing.SHAPE_LETTER):
            return ""
        if "0" <= character <= "9":
            form += parsing.SHAPE_DIGIT
            figures = 1
        elif "a" <= character <= "z" or "A" <= character <= "Z":
            form += parsing.SHAPE_LETTER
            letters = 1
        elif character in parsing.SHAPE_MARKS:
            form += character
            marks = 1
        else:
            return ""
    return form if figures + letters + marks >= 2 else ""


def test_g3_every_cell_without_a_marker_gap_keeps_its_form() -> None:
    """G3: 60,000 seeded cells over figures, letters, marks, gaps and markers.

    Every cell `meridiem_gap_at` gives no gap has exactly the form it had
    on 6a248e7. Mutant: the gap scan answering for a cell ending in a
    figure (`9:15 9`) would move such a cell; the test counts that none
    moved and that the sample held cells of every kind.
    """
    draw = random.Random(392)
    alphabet = "0123456789AMPampm.:-/ " + NARROW + "\u00a0xyz#"
    moved = 0
    gapped = 0
    spaced = 0
    for _cell in range(60000):
        cell = "".join(draw.choice(alphabet) for _place in range(draw.randrange(1, 14)))
        if draw.randrange(4) == 0:
            cell = f"{draw.randrange(1, 13)}:{draw.randrange(60):02d}{draw.choice(('', ' ', NARROW, '  '))}{draw.choice(('AM', 'pm', 'A.M.', 'Am', 'x'))}"
        if parsing.meridiem_gap_at(cell) >= 0:
            gapped += 1
            assert parsing.shape_form(cell) != ""
            continue
        if " " in cell or NARROW in cell:
            spaced += 1
        if parsing.shape_form(cell) != _shape_form_before_l2(cell):
            moved += 1
    assert moved == 0
    assert gapped > 1000 and spaced > 10000


# -- G4: the generator ------------------------------------------------------


def test_g4_a_narrow_gap_form_is_filled_with_times_written_with_that_gap() -> None:
    """G4: the clock supply of `%:%%` + U+202F + `@@` writes U+202F, never a plain space.

    Mutants: `_clock_shape` reading only a plain space before the marker
    (as before L2) fills the form figure by figure, `0:00`+U+202F+`AA`;
    `_form_words` blind to U+202F counts one word where
    `parsing.token_count` counts two.
    """
    form = "%:%%" + NARROW + "@@"
    seen = set()
    for step in range(2 * 9 * 60):
        time = generation._clock_filled_form(form, step)
        assert time is not None
        assert re.fullmatch(r"[1-9]:[0-5][0-9]" + NARROW + "(AM|PM)", time), time
        seen.add(time)
    assert len(seen) == 2 * 9 * 60
    assert generation._clock_filled_form(form, 2 * 9 * 60) is None
    assert generation._filled_form(form, 0).endswith(NARROW + "AM") or generation._filled_form(
        form, 0
    ).endswith(NARROW + "PM")
    spaced = "%%:%%:%%.%%% &.&."
    assert re.fullmatch(r"\d\d:\d\d:\d\d\.\d{3} (a\.m\.|p\.m\.)", generation._filled_form(spaced, 7))
    for gapped in (form, spaced):
        assert generation._form_words(gapped) == 2
        assert generation._form_words(gapped) == parsing.token_count(generation._filled_form(gapped, 3))


# -- G5: the producer always loads -------------------------------------------


def _clock(draw: random.Random, shape: str, gap: str, pair: "tuple[str, str]") -> str:
    hour = draw.randrange(1, 13)
    if shape == "frac":
        text = f"{hour:02d}:{draw.randrange(60):02d}:{draw.randrange(60):02d}.{draw.randrange(1000):03d}"
    else:
        text = f"{hour}:{draw.randrange(60):02d}"
    return text + gap + pair[draw.randrange(2)]


def _cells(role: str, shape: str, gap: str, pair: "tuple[str, str]") -> "list[str]":
    draw = random.Random(11)
    if role == "labels":
        pool = [_clock(draw, shape, gap, pair) for _value in range(40)]
        return [pool[min(int(draw.paretovariate(1.0)) - 1, 39)] for _row in range(600)]
    cells = []
    for row in range(400):
        if role == "free" and row % 33 == 7:
            cells += [f"pending review {row}"]
            continue
        cells += [_clock(draw, shape, gap, pair)]
    return cells


@pytest.mark.parametrize("floor", (2, 11, 36))
@pytest.mark.parametrize("role", ("free", "labels", "clean"))
@pytest.mark.parametrize("gap", (" ", NARROW))
def test_g5_every_spaced_meridiem_description_loads_generates_and_validates(
    tmp_path: pathlib.Path, floor: int, role: str, gap: str
) -> None:
    """G5: the producer-always-loads battery over the gapped shapes.

    Two clocks (`H:MM` and `HH:MM:SS.fff`) and two markers (`AM`/`PM` and
    `a.m.`/`p.m.`), beside rare words, as labels and alone, at floors 2,
    11 and 36: every description loads, generates, and validates against
    its twin and its table with exit 0; and wherever a form holding the
    gap is published, no twin cell writes the other gap before a marker.
    """
    other = NARROW if gap == " " else " "
    for shape in ("hmm", "frac"):
        for pair in (("AM", "PM"), ("a.m.", "p.m.")):
            cells = _cells(role, shape, gap, pair)
            block, written, twin_exit, table_exit = _round(
                tmp_path / f"{shape}-{pair[0]}", cells, floor
            )
            assert (twin_exit, table_exit) == (0, 0), (shape, pair, block.get("role"))
            forms = block.get("shape_forms") or {}
            if any(gap in key for key in forms):
                assert not [cell for cell in written if other + pair[0] in cell or other + pair[1] in cell]


# -- G6: a description written before L2 ---------------------------------------


def _narrow_beside_words() -> "list[str]":
    draw = random.Random(7)
    cells = []
    for row in range(200):
        if row % 33 == 7:
            cells += [f"pending review {row}"]
            continue
        cells += [f"{draw.randrange(1, 13)}:{draw.randrange(60):02d}{NARROW}{('AM', 'PM')[draw.randrange(2)]}"]
    return cells


def test_g6_a_description_written_before_l2_loads_generates_and_validates(tmp_path: pathlib.Path) -> None:
    """G6: 6a248e7's own description of a U+202F column beside rare words.

    It publishes no form, loads, generates the twin 6a248e7 generated byte
    for byte, and validates against that twin and its table with exit 0;
    this producer now writes its forms.
    """
    text = before.NARROW_BESIDE_WORDS
    assert hashlib.sha256(text.encode("utf-8")).hexdigest() == before.NARROW_BESIDE_WORDS_SHA256
    profile = tmp_path / "real-profile.json"
    profile.write_text(text, encoding="utf-8", newline="\n")
    contract.load_profile(str(profile))
    out = tmp_path / "twin"
    out.mkdir()
    assert _exit_of(["generate", str(profile), "--seed", "0", "--out-dir", str(out), "--replace"]) == 0
    twin = out / "real-twin.csv"
    assert hashlib.sha256(twin.read_bytes()).hexdigest() == before.NARROW_BESIDE_WORDS_TWIN_SHA256
    table = tmp_path / "real.csv"
    table.write_text("seen_at\n" + "\n".join(_narrow_beside_words()) + "\n", encoding="utf-8", newline="\n")
    for checked, name in ((twin, "vt"), (table, "vs")):
        report = tmp_path / name
        report.mkdir()
        assert _exit_of(["validate", str(profile), "--twin", str(checked), "--out-dir", str(report), "--replace"]) == 0
    block, _written, twin_exit, table_exit = _round(tmp_path / "now", _narrow_beside_words(), 11)
    assert sorted(block["shape_forms"]) == ["%%:%%" + NARROW + "@@", "%:%%" + NARROW + "@@"]
    assert (twin_exit, table_exit) == (0, 0)


# -- G7: machine-free work bound -----------------------------------------------------


def test_g7_one_gap_scan_per_cell_ending_in_a_marker_and_none_otherwise(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """G7 (MACHINE-FREE): the census's gap scans are counted, not timed.

    `taxonomy.profile_column` over N cells of `9:15 AM` beside rare words
    (a column whose form census is taken) asks `meridiem_gap_at` at least
    once and at most twice per clock cell at N = 1,000 and N = 10,000 --
    no set rebuilt per cell, no scan restarted -- and never for a cell
    ending in a figure; each scan reads at most `SHAPE_FORM_LIMIT`
    characters. So at 1,000,000 cells the scans number at most 2,000,000. Mutant: a scan asked
    of every cell, whatever it ends in, is counted on the figure column
    and on the rare words.
    """
    asked = {"n": 0}
    scan = parsing.meridiem_gap_at

    def counted(text: str) -> int:
        asked["n"] += 1
        return scan(text)

    monkeypatch.setattr(parsing, "meridiem_gap_at", counted)
    per_cell = []
    for rows in (1000, 10000):
        draw = random.Random(rows)
        cells = [
            f"pending review {row}" if row % 33 == 7
            else f"{draw.randrange(1, 13)}:{draw.randrange(60):02d} {('AM', 'PM')[row % 2]}"
            for row in range(rows)
        ]
        clocks = sum(1 for cell in cells if cell.endswith("M"))
        asked["n"] = 0
        taxonomy.profile_column("seen_at", 1, cells, rows, taxonomy.Settings())
        assert clocks <= asked["n"] <= 2 * clocks
        per_cell += [asked["n"]]
    assert per_cell[0] < per_cell[1]
    asked["n"] = 0
    figures = [f"{row % 24:02d}:{row % 60:02d}" for row in range(10000)]
    taxonomy.profile_column("seen_at", 1, figures, 10000, taxonomy.Settings())
    assert asked["n"] == 0
