"""LANE L1: codes and tables written as the source wrote them (plans P4-D390 and P4-D384, 2026-10-13).

The owner's ruling of 2026-09-15 is that the twin writes every value as
the source wrote it. Five shapes older than this lane did not, each
reproduced here on the base 45191fa and each pinned by a mutant:

* MADE-UP FIGURE CODES LOSE THEIR LEADING NOUGHTS (P4-D390's carried
  item (i)). Four-figure codes `0100` to `0999` declared a code came back
  `414` and `57`: 1,448 of 5,000 twin cells narrower than every source
  cell. Mutant: `_padded_to_the_source` writes the plain spelling.
* EXPONENT-SHAPED CODES BESIDE NUMBERS ARE WRITTEN AS NUMBERS NO CELL
  HOLDS (item (ii)). The walk stepped out from `5E77` and wrote integers of
  78 figures and more, and from `41E026` of 28 and 300. Mutants:
  `_walk_ladder` gives the full ladder back; `figures_cap` is ignored.
* A CODE WITH ONE LETTER AMONG FIGURES MISSES ITS FORM (`K-S3-61`). The
  form `%%@%%%` was the number class's alone, so the held-back words and
  the numbers too large to hold wore no form, `1e999` among them. Mutants:
  `_form_also_reads` answers False; `_shared_forms_kept` keeps nothing;
  `_overflow_room` is nought.
* FREE TEXT WRITTEN ON `HH:MM:SS` DURATIONS AND A FACE COLUMN MISSES ITS
  FORM (G9.5). 10,000 durations written once: 4,096 in their form and
  5,904 such as `!!!!!!"N`. 887 `HH:MM` beside 113 spaced `9:15 AM`: 888
  in the form. Mutants: the form walk's old bound of 4,096; `_form_asks`
  never told the census is exact.
* NO SOURCE CRASHES THE WRITER, AND EVERY PUBLISHED STYLE IS HELD (lane
  R4's routed items). 5,000 places raised ValueError in `_grid_units`;
  Excel serials at 50 places, and `0E15588` beside figure codes, failed
  `styles.spelled` on their own source. Mutants: integers read at once;
  `_wears_figures_past_binary64` answers False; the nought stripped.
"""

from __future__ import annotations

import csv
import io
import pathlib
import random
import re
import sys
import typing

import pytest

import fixtures
from synthtwin import contract, generation, parsing, profile, reading, rendering, taxonomy, validation


def _described(
    folder: pathlib.Path,
    cells: "list[str]",
    floor: int = 11,
    codes: "tuple[str, ...]" = (),
) -> "tuple[dict[str, typing.Any], contract.Profile]":
    """One column `t` described by the real producer, written and loaded."""
    folder.mkdir(parents=True, exist_ok=True)
    table = fixtures.write(folder, "table.csv", "\n".join(["t"] + cells) + "\n")
    settings = taxonomy.Settings(small_cell_floor=floor)
    document = profile.build_document(
        reading.read_table(str(table), small_cell_floor=floor), settings, [], list(codes)
    )
    written = fixtures.write_profile(folder, "table.json", document)
    return document, contract.load_profile(str(written))


def _twin(loaded: contract.Profile, seed: int, folder: pathlib.Path) -> "tuple[list[str], pathlib.Path]":
    text = rendering.twin_csv(generation.generate(loaded, seed))
    path = fixtures.write(folder, f"twin-{seed}.csv", text)
    rows = list(csv.reader(io.StringIO(text)))
    return [row[0] for row in rows[1:] if row], path


def _missed(loaded: contract.Profile, path: pathlib.Path) -> "list[str]":
    return sorted(
        check.subcheck
        for check in validation.measure(loaded, str(path)).checks
        if check.verdict == validation.MISSED
    )


def _zipf(draw: random.Random, codes: "list[str]", rows: int) -> "list[str]":
    weights = [1.0 / (rank + 1) ** 1.1 for rank in range(len(codes))]
    return draw.choices(codes, weights, k=rows)


def _round(folder: pathlib.Path, cells: "list[str]", floor: int, codes: "tuple[str, ...]" = ()) -> "tuple[list[str], list[str], list[str]]":
    """Describe, generate seed 0, and measure both files: (twin, source misses, twin misses)."""
    _document, loaded = _described(folder, cells, floor, codes)
    source = fixtures.write(folder, "source.csv", "\n".join(["t"] + cells) + "\n")
    twin, path = _twin(loaded, 0, folder)
    return twin, _missed(loaded, source), _missed(loaded, path)


# -- (1) made-up figure codes keep the source's width -----------------


def _four_figure_codes() -> "list[str]":
    draw = random.Random(1)
    codes = [f"{code:04d}" for code in range(100, 1000)]
    draw.shuffle(codes)
    return _zipf(draw, codes, 5000)


@pytest.mark.parametrize("floor", [11, 36])
def test_made_up_figure_codes_are_written_at_the_source_width(tmp_path: pathlib.Path, floor: int) -> None:
    twin, source_missed, twin_missed = _round(tmp_path, _four_figure_codes(), floor, ("t",))
    assert source_missed == [] and twin_missed == []
    assert {len(cell) for cell in twin} == {4}
    assert all(parsing.is_digit_text(cell) for cell in twin)


def test_made_up_figure_codes_red_without_the_width(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTATION: a made-up code written plainly, as on 45191fa: 1,448 cells narrower."""
    monkeypatch.setattr(generation, "_padded_to_the_source", lambda candidate, _ladder: candidate)
    twin, _source, _missed_now = _round(tmp_path, _four_figure_codes(), 11, ("t",))
    assert sum(1 for cell in twin if len(cell) < 4) == 1448


def test_no_width_is_inferred_where_the_published_codes_differ_in_width() -> None:
    """Codes `07` beside `123` publish no one width, so nothing is padded."""
    ladder = generation._number_ladder(["07", "123", "456"], False, [])
    assert ladder.padded == 0
    assert generation._padded_to_the_source("5", ladder) == "5"
    assert generation._number_ladder(["0468", "0830"], False, []).padded == 4


# -- (2) exponent-shaped codes beside numbers -------------------------


def _numbers_beside_exponent_codes() -> "list[str]":
    draw = random.Random(3)
    cells = [f"{draw.randrange(20, 90)}" for _row in range(6000)]
    shaped: "list[str]" = []
    for _code in range(400):
        kind = draw.randrange(4)
        if kind == 0:
            shaped += [f"{draw.randrange(10)}E{draw.randrange(100000):05d}"]
        elif kind == 1:
            shaped += [f"0{draw.randrange(1000000):06d}"]
        elif kind == 2:
            shaped += [f"{draw.randrange(1, 10)}E{draw.randrange(10, 99)}"]
        else:
            shaped += [f"{draw.randrange(10000):04d}A"]
    cells += _zipf(draw, shaped, 4000)
    draw.shuffle(cells)
    return cells


def _wild(twin: "list[str]") -> "list[str]":
    """Cells wider than any source cell, or the out-of-range construction."""
    return [cell for cell in twin if len(cell) > 7 or "e999" in cell]


@pytest.mark.parametrize("floor", [11, 36])
def test_exponent_codes_beside_numbers_keep_their_forms_and_range(tmp_path: pathlib.Path, floor: int) -> None:
    twin, source_missed, twin_missed = _round(tmp_path, _numbers_beside_exponent_codes(), floor)
    assert source_missed == []
    assert _wild(twin) == []
    # The held-back numbers' pooled mean, 2.9e94 at a floor of eleven, is
    # missed here and on 45191fa alike: no number wearing no form is wider
    # than the column's own cells, and that mean is only an exponent's.
    assert [name for name in twin_missed if name != "suppressed.numbers.mean"] == []


def test_exponent_codes_red_when_the_walk_steps_from_an_exponent(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTATION: the outward walk on the full ladder, as on 45191fa: `5E77` an end."""
    monkeypatch.setattr(generation, "_walk_ladder", lambda ladder: ladder)
    twin, _source, _twin_missed = _round(tmp_path, _numbers_beside_exponent_codes(), 11)
    assert max(len(cell) for cell in twin) >= 78


def test_where_every_number_wears_an_exponent_no_plain_number_is_wider_than_a_label() -> None:
    """`1E2`, `3E1` and `5E2` alone published: the walk stops at three figures."""
    ladder = generation._number_ladder(["1E2", "3E1", "5E2", "alpha"], False, [])
    assert ladder.figures_cap == 5 and ladder.steps is None
    cursor: "dict[str, int]" = {}
    written: "list[str]" = []
    for _step in range(100000):
        found = generation._next_on_ladder(
            ladder, generation._OWED_NUMBER, cursor, {}, {}, {}, (), False
        )
        if not found:
            break
        written += [found]
    assert written and max(len(cell) for cell in written) <= 5
    assert len(written) < 100000


def test_where_every_number_wears_an_exponent_red_without_the_cap() -> None:
    """MUTATION: the cap left off -- the walk writes six figures and more."""
    ladder = generation._number_ladder(["1E2", "3E1", "5E2", "alpha"], False, [])
    ladder = generation.dataclasses.replace(ladder, figures_cap=0)
    cursor: "dict[str, int]" = {}
    widest = 0
    for _step in range(200000):
        found = generation._next_on_ladder(
            ladder, generation._OWED_NUMBER, cursor, {}, {}, {}, (), False
        )
        if not found:
            break
        widest = max(widest, len(found))
    assert widest >= 6


# -- (3) K-S3-61: one letter among figures -----------------------------


def _codes_with_one_letter() -> "list[str]":
    draw = random.Random(4)
    cells = [f"{draw.randrange(100, 900)}" for _row in range(5000)]
    shaped = [f"{draw.randrange(100):02d}E{draw.randrange(1000):03d}" for _code in range(600)]
    shaped += [f"{draw.randrange(1000):03d}D{draw.randrange(100):02d}" for _code in range(600)]
    cells += _zipf(draw, shaped, 5000)
    draw.shuffle(cells)
    return cells


def _census(cells: "list[str]") -> "dict[str, int]":
    counted: "dict[str, int]" = {}
    for cell in cells:
        form = parsing.shape_form(cell)
        counted[form] = (counted[form] if form in counted else 0) + 1
    return counted


@pytest.mark.parametrize("floor", [11, 36])
def test_a_code_with_one_letter_among_figures_is_written_in_its_form(tmp_path: pathlib.Path, floor: int) -> None:
    cells = _codes_with_one_letter()
    twin, source_missed, twin_missed = _round(tmp_path, cells, floor)
    assert source_missed == [] and twin_missed == []
    source, made = _census(cells), _census(twin)
    assert made["%%@%%%"] == source["%%@%%%"] == 4674
    assert made["%%%@%%"] == source["%%%@%%"] == 326
    assert _wild(twin) == []


@pytest.mark.parametrize(
    "mutant",
    ["also_reads", "kept", "overflow"],
)
def test_one_letter_among_figures_red_on_each_mutant(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, mutant: str) -> None:
    """MUTATIONS: the form the number class's alone (45191fa); nothing kept
    for the classes after it; no overflowing spelling of a shared form."""
    if mutant == "also_reads":
        monkeypatch.setattr(generation, "_form_also_reads", lambda _form, _reads, _comma: False)
    elif mutant == "kept":
        monkeypatch.setattr(generation, "_shared_forms_kept", lambda *_args: {})
    else:
        monkeypatch.setattr(generation, "_overflow_room", lambda _form: 0)
    missed: "list[str]" = []
    for floor in (11, 36):
        _twin_cells, _source, twin_missed = _round(tmp_path / f"f{floor}", _codes_with_one_letter(), floor)
        missed += twin_missed
    assert any(name.startswith("forms.published.") for name in missed)


def _numbers_beside_exponent_codes_wide() -> "list[str]":
    """The lane's battery table of numbers beside exponent codes: at a floor of 36 the words'
    own form `%%%%@` owes every word cell the column holds back."""
    draw = random.Random(52008)
    cells = [f"{draw.randrange(20, 90)}" for _row in range(6000)]
    shaped: "list[str]" = []
    for _code in range(400):
        kind = draw.randrange(4)
        if kind == 0:
            shaped += [f"{draw.randrange(10)}E{draw.randrange(100000):05d}"]
        elif kind == 1:
            shaped += [f"0{draw.randrange(1000000):06d}"]
        elif kind == 2:
            shaped += [f"{draw.randrange(1, 10)}E{draw.randrange(10, 99)}"]
        else:
            shaped += [f"{draw.randrange(10000):04d}A"]
    cells += _zipf(draw, shaped, 4000)
    draw.shuffle(cells)
    return cells


def test_words_take_of_a_shared_form_only_what_was_kept_for_them(tmp_path: pathlib.Path) -> None:
    """A shared form the number class leaves unpaid takes no word the
    words' own form is owed: `%%%%@` met at a floor of 36, as on 45191fa
    (`%@%%`, missed before and after, is the number class's supply)."""
    _twin_cells, source_missed, twin_missed = _round(tmp_path, _numbers_beside_exponent_codes_wide(), 36)
    assert source_missed == []
    assert "forms.published.%%%%@" not in twin_missed


def test_words_red_when_they_take_a_shared_form_s_whole_remainder(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTATION: the words handed all a shared form's remainder, as this
    lane first wrote it: 186 groups to `%%%%@` and 54 to `%@%%`."""
    kept = generation._shared_forms_kept

    def greedy(*args: typing.Any) -> "dict[str, dict[str, int]]":
        answer = kept(*args)
        if generation._OWED_TEXT in answer:
            for form in args[3]:
                answer[generation._OWED_TEXT][form] = 10**9
        return answer

    monkeypatch.setattr(generation, "_shared_forms_kept", greedy)
    _twin_cells, _source, twin_missed = _round(tmp_path, _numbers_beside_exponent_codes_wide(), 36)
    assert "forms.published.%%%%@" in twin_missed


def test_an_overflowing_spelling_reads_as_out_of_range_and_wears_its_form() -> None:
    for form in ("%%@%%%", "%@%%%%%", "%.%@%%%"):
        room = generation._overflow_room(form)
        assert room > 0
        for step in (0, 1, 2, room // 3, room - 1):
            spelled = generation._overflow_spelling(form, step)
            assert parsing.shape_form(spelled) == form
            assert parsing.classify_number(spelled) == parsing.NUMBER_OUT_OF_RANGE
    assert generation._overflow_room("%@%%") == 0
    assert generation._overflow_room("%@%@%%%") == 0



def _overflow_beside_words() -> "list[str]":
    """Skeptic 1's att_dec_overflow table (item 2): numbers 1-59, codes
    `%dE%03d` too large to hold, and words `%02dA%03d` in a form no
    published label wears."""
    draw = random.Random(52043)
    cells = [f"{draw.randrange(1, 60)}" for _row in range(4000)]
    shaped = [f"{draw.randrange(1, 10)}E{draw.randrange(300, 1000):03d}" for _code in range(500)]
    shaped += [f"{draw.randrange(100):02d}A{draw.randrange(1000):03d}" for _code in range(300)]
    cells += _zipf(draw, shaped, 4000)
    draw.shuffle(cells)
    return cells


def _census_by_class(cells: "list[str]", form: str) -> "dict[str, int]":
    counted: "dict[str, int]" = {}
    for cell in cells:
        if parsing.shape_form(cell) == form:
            kind = parsing.classify_number(cell)
            counted[kind] = (counted[kind] if kind in counted else 0) + 1
    return counted


@pytest.mark.parametrize("floor", [11, 36])
def test_each_class_takes_first_the_shared_forms_its_own_labels_wear(tmp_path: pathlib.Path, floor: int) -> None:
    """The words' form `%%@%%%`, which no published label wears, goes to the
    words, and the numbers too large to hold take `%@%%%`, the form their
    published labels wear: 163 words and 3,817 such numbers, as the source
    wrote them. The 20 held-back numbers of `%@%%%` are the number class's
    supply, 5 of them written in the form here and on 45191fa alike."""
    cells = _overflow_beside_words()
    twin, source_missed, twin_missed = _round(tmp_path, cells, floor)
    assert source_missed == []
    assert _census_by_class(cells, "%%@%%%") == {parsing.NOT_A_NUMBER: 163}
    assert _census_by_class(twin, "%%@%%%") == {parsing.NOT_A_NUMBER: 163}
    assert _census_by_class(twin, "%@%%%")[parsing.NUMBER_OUT_OF_RANGE] == 3817
    assert "forms.published.%%@%%%" not in twin_missed
    assert [name for name in twin_missed if name != "forms.published.%@%%%"] == []


def test_each_class_red_when_the_shared_forms_are_served_in_their_order(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTATION: no form's own labels read first, so the forms are served in
    their sorted order, as this lane first wrote it: the out-of-range class
    takes `%%@%%%` and its words come out `group-N`."""
    kept = generation._shared_forms_kept
    monkeypatch.setattr(generation, "_shared_forms_kept", lambda _written, *rest: kept([], *rest))
    twin, _source, twin_missed = _round(tmp_path, _overflow_beside_words(), 11)
    assert "forms.published.%%@%%%" in twin_missed
    assert parsing.NUMBER_OUT_OF_RANGE in _census_by_class(twin, "%%@%%%")


def test_shared_forms_kept_reads_each_form_s_own_labels_first() -> None:
    """GATE CASES of `_shared_forms_kept` (method G8.3a): a class is served
    first from the forms its own labels wear; a form whose published labels
    are numbers alone (`1.1e6` beside `1.2e6`) is kept for no word."""
    out_of_range = generation._OWED_OUT_OF_RANGE
    words = generation._OWED_TEXT
    kept = generation._shared_forms_kept(
        ["5E400"] * 15, (12, 10), {0: out_of_range}, {"%%@%%%": 10, "%@%%%": 12}, False
    )
    assert kept == {out_of_range: {"%@%%%": 12}, words: {"%%@%%%": 10}}
    numbers = ["1.1e6"] * 15 + ["1.2e6"] * 15
    assert generation._shared_forms_kept(numbers, (12, 12), {}, {"%.%@%": 24}, False) == {
        out_of_range: {},
        words: {},
    }
    assert generation._shared_forms_kept(numbers, (12, 12), {}, {"%.%@%": 24, "%%@%%": 10}, False)[words] == {
        "%%@%%": 10
    }


# -- (4) free text on durations and a face column ----------------------


def _durations(rows: int) -> "list[str]":
    draw = random.Random(31024)
    made: "list[str]" = []
    for _row in range(rows):
        while True:
            minutes = draw.lognormvariate(0.0, 0.7) * 8.0 * 60
            if minutes < 48 * 60:
                break
        whole = int(minutes)
        made += [f"{whole // 60:02d}:{whole % 60:02d}:{draw.randrange(60):02d}"]
    return made


def _as_durations(cells: "list[str]") -> int:
    """Code reading every cell as a duration: split on ':' and int() each part."""
    total = 0
    for cell in cells:
        parts = [int(part) for part in cell.split(":")]
        total += parts[0] * 3600 + parts[1] * 60 + parts[2]
    return total


@pytest.mark.parametrize("floor", [11, 36])
def test_free_text_durations_past_4096_keep_their_form(tmp_path: pathlib.Path, floor: int) -> None:
    twin, source_missed, twin_missed = _round(tmp_path, _durations(10000), floor)
    assert source_missed == [] and twin_missed == []
    assert all(re.fullmatch(r"\d\d:\d\d:\d\d", cell) for cell in twin)
    assert _as_durations(twin) > 0


def test_free_text_durations_red_at_the_old_bound(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTATION: a free-text form's walk stopped at 4,096 spellings in all, as on 45191fa."""
    monkeypatch.setattr(
        generation,
        "_form_walk_bounds",
        lambda form, figured=False: (
            min(generation._form_room(form), generation._STAND_IN_STEPS),
            min(generation._form_room(form), generation._STAND_IN_STEPS),
        ),
    )
    twin, _source, twin_missed = _round(tmp_path, _durations(10000), 11)
    assert sum(1 for cell in twin if not re.fullmatch(r"\d\d:\d\d:\d\d", cell)) == 5904
    assert "forms.published.%%:%%:%%" in twin_missed


def _face(share: float, rows: int, floor: int) -> "list[str]":
    """Lane C1's mixsweep face table: `HH:MM` beside a minority written `9:15 AM`."""
    draw = random.Random(int(share * 1000) + rows + floor)
    cells: "list[str]" = []
    for _row in range(rows):
        pick = draw.random()
        if pick < 0.80:
            hour = draw.choices(range(7, 17), weights=(3, 9, 10, 10, 8, 4, 8, 9, 8, 5))[0]
            minute = hour * 60 + 15 * draw.randrange(4)
        elif pick < 0.92:
            minute = 390 + draw.randrange(750)
        else:
            minute = 17 * 60 + 30 * draw.randrange(6)
        if draw.random() < share:
            hour = minute // 60
            cells += [f"{hour % 12 or 12}:{minute % 60:02d} {'AM' if hour < 12 else 'PM'}"]
        else:
            cells += [f"{minute // 60:02d}:{minute % 60:02d}"]
    return cells


def test_a_free_text_face_column_meets_its_form_exactly(tmp_path: pathlib.Path) -> None:
    twin, source_missed, twin_missed = _round(tmp_path, _face(0.10, 1000, 36), 36)
    assert source_missed == [] and twin_missed == []
    assert sum(1 for cell in twin if re.fullmatch(r"\d\d:\d\d", cell)) == 887


def test_a_free_text_face_column_red_when_a_group_overpays(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTATION: `_form_asks` never told the census pools nothing: 888 in the form."""
    asked = generation._form_asks

    def blind(*args: typing.Any) -> "list[str]":
        return asked(*args[:11])

    monkeypatch.setattr(generation, "_form_asks", blind)
    twin, _source, twin_missed = _round(tmp_path, _face(0.10, 1000, 36), 36)
    assert sum(1 for cell in twin if re.fullmatch(r"\d\d:\d\d", cell)) == 888
    assert "forms.published.%%:%%" in twin_missed


def test_the_free_text_form_walk_is_bounded_by_what_it_writes_to_a_million(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MACHINE-FREE: a form's walk tries at most twice what it writes plus
    `_STAND_IN_STEPS` spellings, at every count up to 1,000,000 cells, so a
    form none of whose spellings is usable costs `_STAND_IN_STEPS` and no
    more; and the 10,000 durations' twin fills its form in no more steps
    than that bound allows."""
    room = 10**12
    for written in (0, 1, 4096, 100000, 1000000):
        steps = 0
        while generation._walk_goes_on(steps, written, room):
            steps = steps + 1
        assert steps == 2 * written + generation._STAND_IN_STEPS
    counted = {"filled": 0}
    filled = generation._filled_form

    def counting(form: str, step: int, clocks: bool = True) -> str:
        if sys._getframe(1).f_code.co_name == "_walked_cell":
            counted["filled"] = counted["filled"] + 1
        return filled(form, step, clocks)

    monkeypatch.setattr(generation, "_filled_form", counting)
    _document, loaded = _described(tmp_path, _durations(10000), 11)
    counted["filled"] = 0
    _twin(loaded, 0, tmp_path)
    assert counted["filled"] <= 2 * 10000 + generation._STAND_IN_STEPS



def _durations_beside_notes(rows: int) -> "list[str]":
    """Skeptic 1's fold_dur table (item 3): 90 % durations `HH:MM:SS`, 10 %
    notes written `note N` or `NOTE N`, so the column folds."""
    draw = random.Random(9)
    cells: "list[str]" = []
    for _row in range(rows):
        if draw.random() < 0.10:
            word = f"note {draw.randrange(rows // 20)}"
            cells += [word.upper() if draw.random() >= 0.5 else word]
        else:
            minutes = int(draw.lognormvariate(0.0, 0.7) * 480) % (48 * 60)
            cells += [f"{minutes // 60:02d}:{minutes % 60:02d}:{draw.randrange(60):02d}"]
    return cells


def _in_duration_form(cells: "list[str]") -> int:
    return sum(1 for cell in cells if re.fullmatch(r"\d\d:\d\d:\d\d", cell))


@pytest.mark.parametrize(("rows", "floor"), [(4000, 11), (4000, 36), (30000, 11)])
def test_durations_beside_notes_in_two_cases_keep_their_form(tmp_path: pathlib.Path, rows: int, floor: int) -> None:
    """A fold slot is never a group asked a form with no letter place, such a
    group is no parent while another is left and is asked for no letter: the
    duration form is met (45191fa and ffc3904 wrote 24,572 of 27,037 at
    30,000 rows, 3,281 of 3,585 at 4,000)."""
    cells = _durations_beside_notes(rows)
    twin, source_missed, twin_missed = _round(tmp_path, cells, floor)
    assert source_missed == [] and twin_missed == []
    assert _in_duration_form(twin) == _in_duration_form(cells)


@pytest.mark.parametrize("mutant", ["slot", "parent"])
def test_durations_beside_notes_red_on_each_mutant(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, mutant: str) -> None:
    """MUTATIONS: the fold slots kept where they were; a parent asked a form
    with no letter place taken like any other and asked for a letter."""
    if mutant == "slot":
        monkeypatch.setattr(generation, "_fold_slot_order", lambda *_args: None)
    else:
        partner = generation._partner_of
        asks = generation._letter_asks

        def any_parent(*args: typing.Any, **named: typing.Any) -> "str | None":
            named["barred"] = frozenset()
            return partner(*args, **named)

        def every_ask(families: "list[str]", folded: int) -> "list[bool]":
            return asks([family.split("/no letter place")[0] for family in families], folded)

        monkeypatch.setattr(generation, "_partner_of", any_parent)
        monkeypatch.setattr(generation, "_letter_asks", every_ask)
    cells = _durations_beside_notes(4000)
    twin, _source, twin_missed = _round(tmp_path, cells, 11)
    assert _in_duration_form(twin) < _in_duration_form(cells)
    assert "forms.published.%%:%%:%%" in twin_missed


def _text_beside_formula_codes(rows: int) -> "list[str]":
    """Skeptic 1's refused-form table (item 1): free text beside held-back
    codes `-abcde`, every spelling of whose form `-&&&&&` a spreadsheet
    reads as a formula, so the form's walk refuses every spelling."""
    draw = random.Random(5)
    letters = "abcdefghijklmnopqrstuvwxyz"
    cells: "list[str]" = []
    for _row in range(rows):
        if draw.random() < 0.3:
            cells += ["-" + "".join(draw.choice(letters) for _letter in range(5))]
        else:
            cells += [
                " ".join(
                    "".join(draw.choice(letters) for _letter in range(draw.randrange(3, 8)))
                    for _word in range(draw.randrange(2, 5))
                )
            ]
    return cells


def test_a_form_whose_every_spelling_is_refused_costs_the_bound_and_no_more(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MACHINE-FREE: every form state's walk tries at most twice what it
    writes plus `_STAND_IN_STEPS` spellings. The form `-&&&&&` holds 26**5
    spellings and the walk takes none of them, so it gives the form up
    after 4,096; unbounded it walks them all (killed at 300 s unfinished at
    6,000 rows). A cap raises rather than hangs, so the mutant fails."""
    cap = 200000
    counted = {"filled": 0}
    walked: "dict[int, list[int]]" = {}
    filled = generation._filled_form
    walk = generation._walked_cell

    def counting(form: str, step: int, clocks: bool = True) -> str:
        if sys._getframe(1).f_code.co_name == "_walked_cell":
            counted["filled"] = counted["filled"] + 1
            if counted["filled"] > cap:
                raise RuntimeError("the form walk went past its bound")
        return filled(form, step, clocks)

    def watching(*args: typing.Any, **named: typing.Any) -> "str | None":
        answer = walk(*args, **named)
        form = args[7] if len(args) > 7 else (named["form"] if "form" in named else "")
        if form:
            walked[id(args[5])] = args[5]
        return answer

    monkeypatch.setattr(generation, "_filled_form", counting)
    monkeypatch.setattr(generation, "_walked_cell", watching)
    document, loaded = _described(tmp_path, _text_beside_formula_codes(2000), 11)
    assert document["columns"][0]["role"] == "free_text"
    assert document["columns"][0]["shape_forms"] == {"-&&&&&": 616}
    _twin(loaded, 0, tmp_path)
    assert walked
    for state in walked.values():
        assert len(state) > 1
        assert state[0] <= 2 * state[1] + generation._STAND_IN_STEPS
    assert counted["filled"] == generation._STAND_IN_STEPS


# -- (5) no source crashes the writer; every published style is held ---


def _long_fractions(seed: int, rows: int, places: int) -> "list[str]":
    draw = random.Random(seed)
    return [
        f"{45000 + draw.randrange(900)}."
        + "".join(draw.choice("0123456789") for _place in range(places - 1))
        + draw.choice("123456789")
        for _row in range(rows)
    ]


def test_cells_of_5000_places_are_generated(tmp_path: pathlib.Path) -> None:
    twin, source_missed, twin_missed = _round(tmp_path, _long_fractions(4, 120, 5000), 11)
    assert source_missed == [] and twin_missed == []
    assert len(twin) == 120 and all(len(cell.partition(".")[2]) == 5000 for cell in twin)


def test_cells_of_5000_places_red_when_read_at_once(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTATION: the grid count read as one integer, as on 45191fa."""
    monkeypatch.setattr(generation, "_whole_of_figures", int)
    with pytest.raises(ValueError):
        _round(tmp_path, _long_fractions(4, 120, 5000), 11)


def test_a_whole_number_of_many_figures_round_trips_in_pieces() -> None:
    for figures in (1, 4000, 4001, 8001, 12345):
        digits = "9" + "".join(str(place % 10) for place in range(figures - 1))
        number = generation._whole_of_figures(digits)
        assert generation._figures_of_whole(number) == digits
    assert generation._figures_of_whole(10**8000) == "1" + "0" * 8000


@pytest.mark.parametrize("floor", [11, 36])
def test_serials_written_to_50_places_meet_their_own_description(tmp_path: pathlib.Path, floor: int) -> None:
    _twin_cells, source_missed, twin_missed = _round(tmp_path, _long_fractions(1, 200, 50), floor)
    assert source_missed == [] and twin_missed == []


def test_serials_written_to_50_places_red_without_the_shape(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTATION: a fraction past seventeen figures no spelling of its value."""
    monkeypatch.setattr(validation, "_wears_figures_past_binary64", lambda _text, _value, _widths: False)
    _twin_cells, source_missed, _twin_missed = _round(tmp_path, _long_fractions(1, 200, 50), 11)
    assert "styles.spelled" in source_missed


def test_the_past_binary64_shape_admits_only_its_own_value_at_a_published_width() -> None:
    long = "45000." + "1" * 49 + "3"
    value = float(long)
    assert validation._wears_figures_past_binary64(long, value, (50,))
    assert not validation._wears_figures_past_binary64(long, value, (49,))
    assert not validation._wears_figures_past_binary64(long, value + 1.0, (50,))
    assert not validation._wears_figures_past_binary64("45000.12345", 45000.12345, (5,))


def _figure_codes_beside_a_nought_exponent() -> "list[str]":
    draw = random.Random(8)
    cells = [f"{draw.randrange(1000000, 10000000)}" for _row in range(3000)]
    cells += ["0E15588"] * 40 + ["0E71958"] * 23
    draw.shuffle(cells)
    return cells


def test_a_nought_written_with_an_exponent_is_a_spelling_of_its_value(tmp_path: pathlib.Path) -> None:
    _document, loaded = _described(tmp_path, _figure_codes_beside_a_nought_exponent(), 11)
    source = fixtures.write(tmp_path, "source.csv", "\n".join(["t"] + _figure_codes_beside_a_nought_exponent()) + "\n")
    assert "styles.spelled" not in _missed(loaded, source)


def test_a_nought_written_with_an_exponent_red_when_its_mantissa_is_stripped(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTATION: the run of noughts stops only at a point, as on 45191fa."""

    def stripped(text: str, sign: str) -> "str | None":
        body = text
        if sign == "-":
            if body[:1] != "-":
                return None
            body = body[1:]
        elif body[:1] == "+":
            body = body[1:]
        elif body[:1] == "-":
            return None
        while body[:1] == "0" and len(body) > 1 and body[1:2] != ".":
            body = body[1:]
        return body or None

    monkeypatch.setattr(validation, "_body_without_sign_or_zeros", stripped)
    _document, loaded = _described(tmp_path, _figure_codes_beside_a_nought_exponent(), 11)
    source = fixtures.write(tmp_path, "source.csv", "\n".join(["t"] + _figure_codes_beside_a_nought_exponent()) + "\n")
    assert "styles.spelled" in _missed(loaded, source)
