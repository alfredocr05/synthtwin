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
* G7 machine-free: at most two gap scans per cell ending in a marker's
  last character (one on free text) and none for any other, at every
  column size, so a census of 1,000,000 cells costs at most 2,000,000
  scans of at most 24 characters (mutant: a scan asked of every cell);
* G8 a twin writing the other gap is MISSED on both forms (the
  validation method's recount);
* G9 past the clock line a gapped form filled figure by figure keeps its
  gap and its marker word, so the twin validates (lane L2's repair round;
  mutant: the marker key filled letter by letter, `0:00 AA`);
* G10 that figure fill steps the clock's figures at half the step and
  writes the morning word on an even step and the evening word on an odd
  one, so a gapped form holds twice its head's room in spellings, each
  counted under the form it was filled from (lane L2's second repair
  round; mutants: the head filled at the full step, which halves the
  supply; the morning and evening words swapped).

Codex's review of the lane (verdict REJECT, five items), each red on 824c7a4:

* G11 (item 1) a fold partner of a parent wearing a gapped form its slot
  is asked takes the marker word turned over whole, `9:15 am`, and keeps
  the form: 194 times written with both `AM` and `am` beside 12 notes
  publish 388 cells under `%:%% @@` and the twin writes 388, at floors 2,
  11 and 36 and with either gap (mutant: the partner turning one letter,
  `9:15 aM`, which wears no form -- 206);
* G12 (item 2) label and code descriptions written before L2, whose
  levels carry `shape_form_cells` 0 beside named spellings that now wear a
  gapped form, load, generate the twin 6a248e7 generated and validate
  (mutants: W8 counting those spellings, as at 824c7a4; the generator or
  the recount reading such a level as written since L2);
* G13 (item 3) a gapped form advertises the room its figure fill holds,
  twice its head's, in the generator and in the oracle alike, so a column
  of codes holding every `h:mm AM` and `h:mm PM` twice gets every one of
  its 4,000 form-bearing rows (mutant: the marker key counted as two
  letters, 676,000 -- 2,303 rows and 1,697 `group-N`).
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
    # `2024-01-05 9:15 AM` and `2024-01-05 9:15AM`, a stamp's date before
    # the clock, have a form since lane L3 (plan P4-D393): its H1.
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
        "%%%/%%/%% %:%% @@",  # no stamp's date (lane L3, P4-D393)
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


def test_g8_a_twin_writing_the_other_gap_is_missed_on_both_keys(tmp_path: pathlib.Path) -> None:
    """G8: the validation method's recount (P4-D392): a gap counts only under its own key.

    The twin of the U+202F column validates with exit 0; the same twin with
    every U+202F written as a plain space is MISSED on both published forms
    (exit 3). Mutant: a recount blind to which gap a cell holds would pass it.
    """
    _block, _written, twin_exit, _table_exit = _round(tmp_path / "now", _narrow_beside_words(), 11)
    assert twin_exit == 0
    twin = tmp_path / "now" / "twin" / "real-twin.csv"
    swapped = tmp_path / "swapped.csv"
    swapped.write_text(twin.read_text(encoding="utf-8").replace(NARROW, " "), encoding="utf-8", newline="\n")
    report = tmp_path / "vsw"
    report.mkdir()
    profile = tmp_path / "now" / "real-profile.json"
    assert _exit_of(["validate", str(profile), "--twin", str(swapped), "--out-dir", str(report), "--replace"]) == 3
    text = "".join(page.read_text(encoding="utf-8") for page in sorted(report.glob("*quality*")))
    for key in ("%%:%%" + NARROW + "@@", "%:%%" + NARROW + "@@"):
        assert f"forms.published.{key} [free_text.shape_forms]: MISSED" in text, key


# -- G7: machine-free work bound -----------------------------------------------------


def test_g7_one_gap_scan_per_cell_ending_in_a_marker_and_none_otherwise(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """G7 (MACHINE-FREE): the census's gap scans are counted, not timed.

    `taxonomy.profile_column` over N cells of `9:15 AM` beside rare words
    (a column whose form census is taken) asks `meridiem_gap_at` at least
    once per clock cell, at N = 1,000 (free text) never more often than
    the cells ending in a marker's last character and at N = 10,000 (a
    long tail of labels, whose published levels' cells are counted once
    more) never more than twice as often -- no set rebuilt per cell, no
    scan restarted -- and never for a cell ending in a figure; each scan
    reads at most `SHAPE_FORM_LIMIT` characters. So at 1,000,000 cells the
    scans number at most 2,000,000. The second column,
    `h:mm` with no marker beside the same rare words, takes a form census
    (`shape_form` is asked of every cell) and asks no gap scan at all.
    Mutant: a scan asked of every cell, whatever it ends in, is counted on
    the rare words of the first column and on every cell of the second
    (lane L2's repair round: the second column was `HH:MM` alone, read as
    clock times, which takes no census, so it held nothing up).
    """
    asked = {"n": 0}
    scan = parsing.meridiem_gap_at

    def counted(text: str) -> int:
        asked["n"] += 1
        return scan(text)

    monkeypatch.setattr(parsing, "meridiem_gap_at", counted)
    per_cell = []
    roles: "list[str]" = []
    for rows in (1000, 10000):
        draw = random.Random(rows)
        cells = [
            f"pending review {row}" if row % 33 == 7
            else f"{draw.randrange(1, 13)}:{draw.randrange(60):02d} {('AM', 'PM')[row % 2]}"
            for row in range(rows)
        ]
        clocks = sum(1 for cell in cells if cell.endswith("M"))
        marked = sum(1 for cell in cells if cell[-1:] in "Mm.")
        asked["n"] = 0
        role = taxonomy.profile_column("seen_at", 1, cells, rows, taxonomy.Settings()).role
        roles += [role]
        # Free text takes one census of its cells; a long tail of labels
        # takes it and then counts the cells of each published level once
        # more (`shape_form_cells`), so at most twice.
        assert clocks <= asked["n"] <= (marked if role == "free_text" else 2 * marked)
        per_cell += [asked["n"]]
    assert roles == ["free_text", "long_tail_labels"]
    assert per_cell[0] < per_cell[1]
    shaped = {"n": 0}
    shape = parsing.shape_form

    def shape_counted(text: str) -> str:
        shaped["n"] += 1
        return shape(text)

    monkeypatch.setattr(parsing, "shape_form", shape_counted)
    asked["n"] = 0
    draw = random.Random(3)
    figures = [
        f"pending review {row}" if row % 33 == 7
        else f"{draw.randrange(1, 13)}:{draw.randrange(60):02d}"
        for row in range(10000)
    ]
    taxonomy.profile_column("seen_at", 1, figures, 10000, taxonomy.Settings())
    assert shaped["n"] >= 10000
    assert asked["n"] == 0


# -- G9: past the clock line a gapped form keeps its marker word -------------------


def _free_beside_notes(gap: str) -> "list[str]":
    draw = random.Random(1000)
    cells = []
    for row in range(1000):
        if row % 40 == 7:
            cells += [f"note {draw.randrange(10**6)}"]
            continue
        cells += [f"{draw.randrange(1, 13)}:{draw.randrange(60):02d}{gap}{('AM', 'PM')[draw.randrange(2)]}"]
    return cells


@pytest.mark.parametrize("gap", (" ", NARROW))
def test_g9_past_the_clock_line_a_gapped_form_keeps_its_marker_word(
    tmp_path: pathlib.Path, gap: str
) -> None:
    """G9 (lane L2's repair round): free text of `h:mm AM` beside 1 note in 40.

    At 1,000 rows and a floor of eleven the clock line binds, so the last
    stand-ins of the forms `%:%% @@` and `%%:%% @@` are filled figure by
    figure (method G8.3). Each keeps its gap and its marker word, so every
    twin cell beginning with a figure wears a form the description
    publishes, and the twin validates with exit 0. Mutant: the marker key
    filled letter by letter, as before the repair, writes `0:00 AA`, which
    wears no form, and the twin with a plain space is MISSED (exit 3).
    """
    block, written, twin_exit, table_exit = _round(tmp_path / "free", _free_beside_notes(gap), 11)
    assert block["role"] == "free_text"
    forms = block["shape_forms"]
    assert sorted(forms) == ["%%:%%" + gap + "@@", "%:%%" + gap + "@@"]
    clockish = [cell for cell in written if cell[:1] in "0123456789"]
    assert len(clockish) > 900
    assert [cell for cell in clockish if parsing.shape_form(cell) not in forms] == []
    assert (twin_exit, table_exit) == (0, 0)


@pytest.mark.parametrize(
    ("form", "first", "second"),
    (
        ("%:%% @@", "0:00 AM", "0:00 PM"),
        ("%%:%% &&", "00:00 am", "00:00 pm"),
        ("%:%%:%% @.@.", "0:00:00 A.M.", "0:00:00 P.M."),
    ),
)
def test_g10_the_gapped_figure_fill_holds_twice_its_heads_room(
    form: str, first: str, second: str
) -> None:
    """G10 (lane L2's second repair round): the half step and the parity word.

    Method G8.3 fills a gapped form past the clock line by stepping only
    the clock's figures, at half the step, and writing the marker word the
    step's parity names. So the form's ``2 x room`` steps give ``2 x room``
    different spellings, every one counted under the form it was filled
    from (the census's lower-case fold included), and steps 0 and 1 differ
    only in the marker word. Mutants: the head filled at the full step
    (steps s and s + room repeat, half the supply); the morning and evening
    words swapped (step 0 writes the evening word).
    """
    gap = parsing.key_gap_at(form)
    assert gap >= 0
    room = generation._form_room(form[:gap])
    cells = [generation._filled_form(form, step, False) for step in range(2 * room)]
    assert len(set(cells)) == 2 * room
    census = {form: 1}
    assert [cell for cell in cells if parsing.census_form(cell, census) != form] == []
    assert [cell for cell in cells if cell[gap] != form[gap]] == []
    assert cells[:2] == [first, second]


# -- G11: fold partners keep a gapped form (Codex's review, item 1) ---------


def _both_cases(gap: str) -> "list[str]":
    """Codex's table: 194 times written with `AM` and with `am`, then 12 notes."""
    cells: "list[str]" = []
    for index in range(194):
        text = f"{1 + index // 60}:{index % 60:02d}"
        cells += [text + gap + "AM", text + gap + "am"]
    return cells + [f"note {number:02d}" for number in range(12)]


@pytest.mark.parametrize("gap", (" ", NARROW))
@pytest.mark.parametrize("floor", (2, 11, 36))
def test_g11_fold_partners_keep_the_gapped_form_they_are_asked(
    tmp_path: pathlib.Path, gap: str, floor: int
) -> None:
    """G11 (Codex's review of lane L2, item 1): the 400 cells Codex built.

    The description publishes 388 cells under `%:%% @@` (or its U+202F
    twin) and 206 folded values of 400. A partner slot asked that form
    takes its parent with the marker word turned over whole, so the twin
    writes 388 cells in the form, each marker `AM`, `PM`, `am` or `pm`,
    and validates with exit 0. Mutant: no keeper, the family's first
    member `1:00 aM` -- the twin writes 206 and is MISSED (exit 3).
    """
    block, written, twin_exit, table_exit = _round(tmp_path / "fold", _both_cases(gap), floor)
    form = "%:%%" + gap + "@@"
    assert block["shape_forms"] == {form: 388}
    assert (block["n_distinct"], block["n_distinct_folded"]) == (400, 206)
    shaped = [cell for cell in written if parsing.shape_form(cell) == form]
    assert len(shaped) == 388
    assert {cell[cell.index(gap) + 1 :] for cell in shaped} <= {"AM", "PM", "am", "pm"}
    assert (twin_exit, table_exit) == (0, 0)


def test_g11_the_keeper_turns_the_marker_word_whole() -> None:
    """G11: `_form_keeping_partner` turns the word over whole, or answers None."""
    assert generation._form_keeping_partner("9:15 AM", "%:%% @@") == "9:15 am"
    assert generation._form_keeping_partner("9:15 am", "%:%% @@") == "9:15 AM"
    assert generation._form_keeping_partner("09:15 a.m.", "%%:%% @.@.") == "09:15 A.M."
    assert generation._form_keeping_partner("9:15" + NARROW + "PM", "%:%%" + NARROW + "@@") == "9:15" + NARROW + "pm"
    # Asked no form, or another one, or a parent wearing none: no keeper.
    assert generation._form_keeping_partner("9:15 AM", "") is None
    assert generation._form_keeping_partner("9:15 AM", "%%:%% @@") is None
    assert generation._form_keeping_partner("9:15 aM", "%:%% @@") is None
    assert generation._form_keeping_partner("AB12", "@@%%") is None


# -- G12: descriptions written before L2, labels and codes (item 2) ---------


@pytest.mark.parametrize("name", sorted(before.LABELS_AND_CODES))
def test_g12_a_label_or_code_description_written_before_l2_loads_and_generates_its_twin(
    tmp_path: pathlib.Path, name: str
) -> None:
    """G12 (Codex's review of lane L2, item 2): 6a248e7's descriptions of labels and codes.

    Each level's label holds the one gap and carries `shape_form_cells` 0,
    as every description written before L2 does, while its named
    spellings now wear a gapped form. It loads (824c7a4 refused it under
    W8), generates the twin 6a248e7 generated byte for byte, and validates
    against that twin and its table with exit 0. Mutants: W8 counting the
    named spellings (refused); the recount counting them (exit 3); the
    generator's G8.2a walk or its published level shape reading the level
    as written since L2 (another twin).
    """
    text, profile_sha, twin_sha, coded = before.LABELS_AND_CODES[name]
    assert hashlib.sha256(text.encode("utf-8")).hexdigest() == profile_sha
    document = json.loads(text)
    block = document["columns"][0]
    gapped = [level for level in block["levels"] if parsing.meridiem_gap_at(level["label"]) >= 0]
    assert gapped and all(level["shape_form_cells"] == 0 for level in gapped)
    assert any(parsing.shape_form(spelling) for level in gapped for spelling in level["variants"])
    assert (block["role"] in ("binary", "categorical", "long_tail_labels")) and (
        ("seen_at" in document["settings"]["forced_codes"]) == coded
    )
    profile = tmp_path / "real-profile.json"
    profile.write_text(text, encoding="utf-8", newline="\n")
    contract.load_profile(str(profile))
    out = tmp_path / "twin"
    out.mkdir()
    assert _exit_of(["generate", str(profile), "--seed", "0", "--out-dir", str(out), "--replace"]) == 0
    twin = out / "real-twin.csv"
    assert hashlib.sha256(twin.read_bytes()).hexdigest() == twin_sha
    table = tmp_path / "real.csv"
    table.write_text(
        "seen_at\n" + "\n".join(before.label_tables()[name]) + "\n", encoding="utf-8", newline="\n"
    )
    for checked, report_name in ((twin, "vt"), (table, "vs")):
        report = tmp_path / report_name
        report.mkdir()
        assert _exit_of(["validate", str(profile), "--twin", str(checked), "--out-dir", str(report), "--replace"]) == 0


def test_g12_the_reading_is_the_levels_alone() -> None:
    """G12: a level reads as written before L2 only where its label holds the gap and it carries 0."""
    assert parsing.level_unshaped_before_gaps("9:15 am", 0)
    assert parsing.level_unshaped_before_gaps("9:15" + NARROW + "pm", 0)
    assert not parsing.level_unshaped_before_gaps("9:15 am", 100)
    assert not parsing.level_unshaped_before_gaps("e11.9", 0)
    assert not parsing.level_unshaped_before_gaps("9:15am", 0)


# -- G13: a gapped form's advertised room (item 3) ---------------------------


def _oracle_module() -> "dict[str, object]":
    """The generation oracle's own namespace, as the vectors' test loaded it."""
    from tests import test_generation_reference as reference

    return vars(reference.gen)


@pytest.mark.parametrize("form", ("%:%% @@", "%%:%% &&", "%:%%" + NARROW + "@@", "%%:%%" + NARROW + "@.@."))
def test_g13_a_gapped_form_advertises_the_room_its_fill_holds(form: str) -> None:
    """G13 (Codex's review of lane L2, item 3): capacity, not only enumeration.

    `_form_room` -- what allocation and the walks are told a form holds --
    is the number of different spellings its figure fill writes, twice its
    head's room, and the oracle's `form_room` says the same; a form with no
    gap keeps its room. Mutant: the marker key counted as two letters,
    `%:%% @@` at 676,000, 338 times its supply.
    """
    room = generation._form_room(form)
    gap = parsing.key_gap_at(form)
    assert room == 2 * generation._form_room(form[:gap])
    assert len({generation._filled_form(form, step, False) for step in range(room)}) == room
    oracle = _oracle_module()
    form_room = oracle["form_room"]
    assert callable(form_room)
    assert form_room(form) == room
    for plain in ("@%%.%", "%%:%%", "&&-&"):
        assert form_room(plain) == generation._form_room(plain)


@pytest.mark.parametrize("form", ("%:%% @@", "%:%%" + NARROW + "&&"))
def test_g13_the_clock_first_walk_still_reaches_every_spelling(form: str) -> None:
    """G13: the room is the supply; the clock-first walk's steps keep their period.

    A gapped form's clock-first fill writes its clock times and then its
    figure fill, whose half step comes round every room. Its steps run on
    the period its key read as letters gives (`_form_steps`, 676,000 for
    `%:%% @@`), so within its clock supply and twice its room it has
    written every one of its 2,000 spellings, and the free text's walk may
    take that many steps; the oracle counts the same. Mutant: the steps on
    the 2,000 -- the walk meets its clock times again at every turn and
    never writes the fill's earlier heads (free text holding every `h:mm`
    with all four words wrote 4,348 cells in the form, not 5,330).
    """
    room = generation._form_room(form)
    supply = generation._clock_supply(form)
    reach = supply + 2 * room
    assert generation._form_walk_bounds(form)[0] >= reach
    assert len({generation._filled_form(form, step) for step in range(reach)}) == room
    oracle = _oracle_module()
    form_steps = oracle["form_steps"]
    assert callable(form_steps)
    assert form_steps(form) == generation._form_steps(form) == 26 * 26 * room // 2
    assert form_steps("%%:%%") == generation._form_steps("%%:%%") == 10000


def test_g13_codes_of_every_dial_time_get_every_row_of_their_form(tmp_path: pathlib.Path) -> None:
    """G13: Codex's column, declared codes, at a floor of eleven and seed 0.

    Every `h:mm AM` and `h:mm PM`, h 0 to 9 and mm 00 to 99, twice each,
    then `z00000` to `z05999`: 10,000 rows, 8,000 different. The
    description publishes 4,000 cells under `%:%% @@`; the twin writes all
    4,000, no `group-N`, 8,000 different values, and validates with exit 0.
    At 824c7a4 it wrote 2,303 and 1,697 `group-N` and missed the form.
    """
    cells: "list[str]" = []
    for hour in range(10):
        for minute in range(100):
            for mark in ("AM", "PM"):
                cells += [f"{hour}:{minute:02d} {mark}"] * 2
    cells += [f"z{number:05d}" for number in range(6000)]
    folder = tmp_path / "codes"
    folder.mkdir()
    table = folder / "real.csv"
    table.write_text("seen_at\n" + "\n".join(cells) + "\n", encoding="utf-8", newline="\n")
    assert _exit_of(
        ["profile", str(table), "--out-dir", str(folder), "--replace", "--smallest-group", "11", "--code", "seen_at"]
    ) == 0
    profile = folder / "real-profile.json"
    block = json.loads(profile.read_text(encoding="utf-8"))["columns"][0]
    assert block["shape_forms"]["%:%% @@"] == 4000
    out = folder / "twin"
    out.mkdir()
    assert _exit_of(["generate", str(profile), "--seed", "0", "--out-dir", str(out), "--replace"]) == 0
    twin = out / "real-twin.csv"
    written = [row[0] for row in list(csv.reader(io.StringIO(twin.read_text(encoding="utf-8"))))[1:]]
    assert sum(1 for cell in written if parsing.shape_form(cell) == "%:%% @@") == 4000
    assert [cell for cell in written if cell.startswith("group-")] == []
    assert len(set(written)) == 8000
    report = folder / "vt"
    report.mkdir()
    assert _exit_of(["validate", str(profile), "--twin", str(twin), "--out-dir", str(report), "--replace"]) == 0


# -- G14: past its times a U+202F form steps past its own times (verifier) ---


def _dial_codes(gap: str) -> "list[str]":
    """Codex's item-3 column with ``gap`` before the marker: 10,000 rows, 8,000 different."""
    cells: "list[str]" = []
    for hour in range(10):
        for minute in range(100):
            for mark in ("AM", "PM"):
                cells += [f"{hour}:{minute:02d}{gap}{mark}"] * 2
    return cells + [f"z{number:05d}" for number in range(6000)]


def test_g14_a_spelling_past_the_clock_reads_its_narrow_gap_as_a_space() -> None:
    """G14: `_read_as_a_clock` takes a time with either gap and nothing else."""
    for gap in (" ", NARROW):
        assert generation._read_as_a_clock(f"9:15{gap}AM")
        assert generation._read_as_a_clock(f"12:00:30{gap}pm")
        assert not generation._read_as_a_clock(f"9:75{gap}AM")
    assert not generation._read_as_a_clock("z00001")
    with pytest.raises(TypeError):
        generation._read_as_a_clock(b"9:15 AM")  # type: ignore[arg-type]


@pytest.mark.parametrize("floor", (11, 36))
def test_g14_codes_in_a_narrow_gapped_form_past_its_times_get_every_row(
    tmp_path: pathlib.Path, floor: int
) -> None:
    """G14 (the verifier of lane L2's Codex fix stream): Codex's column with U+202F.

    Declared codes, `%:%%` U+202F `@@` holds 1,440 clock times and its
    4,000 rows run past them, so its smaller places are filled figure by
    figure and step past every spelling a clock reader takes -- the U+202F
    read as the space it stands for, as allocation reads the form. The twin
    writes all 4,000 in the form, no `group-N`, 8,000 different values, and
    validates. Mutant: the walk asking `parsing.clock_parts` of the U+202F
    spelling as written, which takes `9:15` U+202F `AM` past the line
    (86e9f7f: 2,314 and 1,686 `group-N`, the form MISSED).
    """
    form = "%:%%" + NARROW + "@@"
    folder = tmp_path / "narrow"
    folder.mkdir()
    table = folder / "real.csv"
    table.write_text("seen_at\n" + "\n".join(_dial_codes(NARROW)) + "\n", encoding="utf-8", newline="\n")
    assert _exit_of(
        ["profile", str(table), "--out-dir", str(folder), "--replace", "--smallest-group", str(floor), "--code", "seen_at"]
    ) == 0
    profile = folder / "real-profile.json"
    block = json.loads(profile.read_text(encoding="utf-8"))["columns"][0]
    assert block["shape_forms"][form] == 4000
    out = folder / "twin"
    out.mkdir()
    assert _exit_of(["generate", str(profile), "--seed", "0", "--out-dir", str(out), "--replace"]) == 0
    twin = out / "real-twin.csv"
    written = [row[0] for row in list(csv.reader(io.StringIO(twin.read_text(encoding="utf-8"))))[1:]]
    assert sum(1 for cell in written if parsing.shape_form(cell) == form) == 4000
    assert [cell for cell in written if cell.startswith("group-")] == []
    assert len(set(written)) == 8000
    report = folder / "vt"
    report.mkdir()
    assert _exit_of(["validate", str(profile), "--twin", str(twin), "--out-dir", str(report), "--replace"]) == 0


def test_g14_the_oracle_steps_past_a_narrow_gapped_time_past_the_clock() -> None:
    """G14: the oracle's mirror (A-P4-59) of the walk past a form's times.

    600 stand-ins of `%:%%` U+202F `@@` with none of its times left are
    filled figure by figure, and no spelling a clock reader takes with its
    U+202F read as a space is written: the U+202F walk is the plain-space
    walk with its gap turned. Mutant: `clock_reads` asked of the U+202F
    spelling as written, 324 such times among the 600.
    """
    oracle = _oracle_module()
    invented = oracle["invented_levels"]
    clock_reads = oracle["clock_reads"]
    assert callable(invented) and callable(clock_reads)
    walks = {}
    for gap in (" ", NARROW):
        form = "%:%%" + gap + "@@"
        walks[gap] = [label for label, _size in invented((), [1] * 600, {form: 600}, past={form: 0})]
        assert [label for label in walks[gap] if clock_reads(label.replace(NARROW, " "), False)] == []
    assert [label.replace(NARROW, " ") for label in walks[NARROW]] == walks[" "]
