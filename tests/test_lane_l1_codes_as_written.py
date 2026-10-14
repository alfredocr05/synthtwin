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
import test_commonest_width_grid as width_grid
import test_files_review_repairs as review_repairs
from synthtwin import contract, generation, parsing, profile, reading, rendering, taxonomy, validation


def _described(
    folder: pathlib.Path,
    cells: "list[str]",
    floor: int = 11,
    codes: "tuple[str, ...]" = (),
    name: str = "t",
) -> "tuple[dict[str, typing.Any], contract.Profile]":
    """One column (`t` unless named) described by the real producer, written and loaded."""
    folder.mkdir(parents=True, exist_ok=True)
    table = fixtures.write(folder, "table.csv", "\n".join([name] + cells) + "\n")
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


def test_a_later_class_is_offered_only_what_the_number_class_left_of_a_shared_form(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """GATE CASE of `_class_stand_ins_walked`: a class after the number
    class is offered of a shared form only what the form still owes once
    the numbers are written, so the two never pay it past its count. On
    the overflow table the numbers write 5 cells of `%@%%%`; the
    out-of-range class is offered 1,006 of its 1,011, and 1,011 where the
    written numbers are not taken off (`left` not decremented)."""
    walks: "list[dict[str, typing.Any]]" = []
    walked = generation._class_stand_ins_walked
    kept = generation._shared_forms_kept
    shared_out = generation._shared_out

    def walking(*args: typing.Any, **named: typing.Any) -> typing.Any:
        nonlocal walks
        walks += [{"offers": [], "owing": {}, "sizes": args[2]}]
        answer = walked(*args, **named)
        walks[-1]["answer"] = answer
        return answer

    def keeping(*args: typing.Any) -> "dict[str, dict[str, int]]":
        if walks:
            walks[-1]["owing"] = dict(args[3])
        return kept(*args)

    def offering(sub: typing.Any, mine: "dict[str, int]", *rest: typing.Any) -> typing.Any:
        if walks:
            walks[-1]["offers"] += [dict(mine)]
        return shared_out(sub, mine, *rest)

    monkeypatch.setattr(generation, "_class_stand_ins_walked", walking)
    monkeypatch.setattr(generation, "_shared_forms_kept", keeping)
    monkeypatch.setattr(generation, "_shared_out", offering)
    _round(tmp_path, _overflow_beside_words(), 11)
    checked = 0
    for walk in walks:
        if "answer" not in walk or "%@%%%" not in walk["owing"]:
            continue
        classes, written_as = walk["answer"][0], walk["answer"][1]
        numbers = sum(
            walk["sizes"][place]
            for place in written_as
            if classes.get(place) == generation._OWED_NUMBER and parsing.shape_form(written_as[place]) == "%@%%%"
        )
        for offer in walk["offers"][1:]:
            if "%@%%%" in offer:
                assert offer["%@%%%"] + numbers <= walk["owing"]["%@%%%"]
                checked = checked + 1
    assert checked > 0


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


def test_form_asks_skips_a_large_group_only_while_later_groups_cover_the_form() -> None:
    """GATE CASES of `_form_asks` on an exact census (method G9.5 step 7):
    a group of 2 is not asked for a form owing 1 while a group of 1 comes
    after it; a group of 5 IS asked for a form owing 3 where only a group of
    1 comes after, which could not cover it. Red where the rule skips
    every group larger than the debt (`after[step] >= left[form]` dropped)."""
    form = "%%:%%"
    assert generation._form_asks(
        {form: 1}, (2, 1), [5, 5], [1, 1], (0, 1), 5, 5, [0, 0], None, None, False, True
    ) == ["", form]
    assert generation._form_asks(
        {form: 3}, (5, 1), [5, 5], [1, 1], (0, 1), 5, 5, [0, 0], None, None, False, True
    ) == [form, ""]


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



def _durations_beside_notes(rows: int, seed: int = 9) -> "list[str]":
    """Skeptic 1's table of durations beside notes (item 3): 90 % durations `HH:MM:SS`, 10 %
    notes written `note N` or `NOTE N`, so the column folds. Skeptic 2 drew it with seed 4242."""
    draw = random.Random(seed)
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
    with no letter place asked for a letter like any other."""
    if mutant == "slot":
        monkeypatch.setattr(generation, "_fold_slot_order", lambda *_args: None)
    else:
        asks = generation._letter_asks

        def every_ask(families: "list[str]", folded: int) -> "list[bool]":
            return asks([family.split("/no letter place")[0] for family in families], folded)

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
    # Either side of the least number written in pieces (`_PIECE_LIMIT`).
    for number in (generation._PIECE_LIMIT - 1, generation._PIECE_LIMIT, generation._PIECE_LIMIT + 1):
        assert generation._whole_of_figures(generation._figures_of_whole(number)) == number


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


# -- (6) skeptic 2's leftover items: fold slots at scale ---------------


def _notes_majority(rows: int) -> "list[str]":
    """Skeptic 2's notes_majority table (item 1): 70 % notes `obs N word`, half
    in capitals, 30 % durations `HH:MM:SS`."""
    draw = random.Random(61000 + 8)
    scale = max(200, rows // 25)
    cells: "list[str]" = []
    for _row in range(rows):
        if draw.random() < 0.70:
            word = f"obs {draw.randrange(scale)} {draw.choice(['ok', 'high', 'low'])}"
            cells += [word.upper() if draw.random() < 0.5 else word]
        else:
            minutes = int(draw.lognormvariate(0.0, 0.7) * 480) % (48 * 60)
            cells += [f"{minutes // 60:02d}:{minutes % 60:02d}:{draw.randrange(60):02d}"]
    return cells


def test_the_fold_partner_search_costs_what_it_finds(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MACHINE-FREE (skeptic 2 item 1): on notes_majority at 10,000 rows and a
    floor of 36, the parents asked for a partner number at most four per
    slot. 7b28976 asked 2,304,853 at 5,000 rows, 8,820,368 at 10,000 with
    `_partner_indexed` off; this head asks 1,084 for 1,623 slots."""
    _document, loaded = _described(tmp_path, _notes_majority(10_000), 36)
    asked = {"parents": 0, "slots": 0}
    partner_of = generation._partner_of
    partner_from = generation._partner_from

    def counted_of(index: int, folded: int, *args: typing.Any, **named: typing.Any) -> "str | None":
        if 0 < folded <= index:
            asked["slots"] += 1
        return partner_of(index, folded, *args, **named)

    def counted_from(*args: typing.Any, **named: typing.Any) -> "str | None":
        asked["parents"] += 1
        return partner_from(*args, **named)

    monkeypatch.setattr(generation, "_partner_of", counted_of)
    monkeypatch.setattr(generation, "_partner_from", counted_from)
    generation.generate(loaded, 0)
    assert asked["slots"] > 1000
    assert asked["parents"] <= 4 * asked["slots"]


def test_the_indexed_partner_walk_answers_as_the_plain_walk() -> None:
    """GATE CASES of `_partner_indexed` (skeptic 2 item 1): the same partner as
    `_partner_of`'s own walk, call after call, where a walk is cut by its step
    bound on a hole (`NaT`, the one member matched byte for byte) and reaches
    further once `used` grows. Red where every parent and window that
    answered None is recorded spent."""
    families = ["f", "f", "f"]
    windows = [(3, 3), (3, 3), (3, 3)]

    def walked(indexed: bool) -> "list[str | None]":
        used: "dict[str, int]" = {}
        kept: "tuple[typing.Any, typing.Any]" = ({}, {}) if indexed else (None, None)
        answers: "list[str | None]" = []
        for extra in ["", "zz", "yy"]:
            if extra:
                used[extra] = generation._WRITTEN
            answers += [generation._partner_of(1, 1, ["naT"], families, used, windows, holes=("NaT",), parents=kept[0], spent=kept[1])]
        return answers

    assert walked(False) == [None, "nAT", "nAT"]
    assert walked(True) == walked(False)
    draw = random.Random(5)
    for _case in range(40):
        folded = draw.randrange(2, 9)
        total = folded + draw.randrange(1, 9)
        spellings = ["".join(draw.choice("ab1-") for _each in range(draw.randrange(1, 4))) for _each in range(folded)]
        families = [draw.choice(["f", "g"]) for _each in range(total)]
        sizes = [draw.randrange(1, 6) for _each in range(total)]
        results: "list[list[str | None]]" = []
        for indexed in (False, True):
            used = {spelling: generation._WRITTEN for spelling in spellings}
            carried: "dict[int, int]" = {}
            written = list(spellings)
            kept = ({}, {}) if indexed else (None, None)
            answers = []
            for index in range(folded, total):
                windows = [(1, 4)] * total
                found = generation._partner_of(
                    index, folded, written, families, used, windows, sizes, 8, carried,
                    parents=kept[0], spent=kept[1],
                )
                if found is not None:
                    used[found] = generation._WRITTEN
                answers += [found]
                written += [found or f"made{index}"]
            results += [answers]
        assert results[0] == results[1]


@pytest.mark.parametrize("rows", [50_000, 100_000])
def test_durations_beside_notes_keep_their_form_and_average_past_30000_rows(tmp_path: pathlib.Path, rows: int) -> None:
    """SKEPTIC 2 ITEM 1, BY COUNTS: durations beside notes in two cases meet
    their duration form and `length.mean` at 50,000 and 100,000 rows. On
    7b28976 `length.mean` was missed at 50,000 rows (8.06626 against
    8.05436 on skeptic 2's draw) and 100,000 rows did not finish in 900 s."""
    cells = _durations_beside_notes(rows, 4242)
    twin, source_missed, twin_missed = _round(tmp_path, cells, 11)
    assert source_missed == []
    assert twin_missed == []
    assert len(twin) == rows


def test_durations_beside_notes_red_when_the_slots_extra_characters_are_not_paid_back(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MUTATION: `_paid_back` returns at once; the slots' edge-spaced partners one
    character over their plan move `length.mean` out of its window."""
    monkeypatch.setattr(generation, "_paid_back", lambda *args: args[5])
    _twin_cells, _source, twin_missed = _round(tmp_path, _durations_beside_notes(50_000, 4242), 11)
    assert "length.mean" in twin_missed


def _workbook_truths_beside_folding_notes() -> bytes:
    """Skeptic 2's workbook column (item 2): `noteNN`/`NOTENN`, times `HH:MM`
    as text, and one TRUE and one FALSE, 400 rows."""
    draw = random.Random(900)
    rows = 400
    values: "list[typing.Any]" = []
    for _row in range(rows - 2):
        if draw.random() < 0.45:
            word = f"note{draw.randrange(10, 99)}"
            values += [word.upper() if draw.random() < 0.5 else word]
        else:
            values += ["%02d:%02d" % (draw.randrange(24), draw.randrange(60))]
    values += [True, False]
    draw.shuffle(values)
    strings = ["flag", "arm"]
    grid = {1: [review_repairs._cell("A1", "0", "s"), review_repairs._cell("B1", "1", "s")]}
    for place in range(rows):
        number = 2 + place
        value = values[place]
        if isinstance(value, bool):
            cell = review_repairs._cell(f"A{number}", "1" if value else "0", "b")
        else:
            strings += [value]
            cell = review_repairs._cell(f"A{number}", f"{len(strings) - 1}", "s")
        grid[number] = [cell, review_repairs._cell(f"B{number}", f"{place % 3}")]
    return review_repairs._book([("Data", review_repairs._rows(grid))], strings)


def _cell_classes_missed(folder: pathlib.Path) -> bool:
    result = review_repairs._trip(folder, "flags", _workbook_truths_beside_folding_notes(), ("--smallest-group", "1"), seed=4)
    return any("workbook.cell-classes" in line for line in typing.cast("list[str]", result["twin_missed"]))


def test_a_truth_group_never_moves_into_a_fold_slot(tmp_path: pathlib.Path) -> None:
    """SKEPTIC 2 ITEM 2: the FALSE group is not moved into a fold slot and
    written as a partner, so `workbook.cell-classes` holds (P4-D198)."""
    assert not _cell_classes_missed(tmp_path)


def test_a_truth_group_red_when_it_may_move_into_a_fold_slot(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTATION: `_fold_slot_order` handed no truth places, as on 7b28976."""
    order = generation._fold_slot_order
    monkeypatch.setattr(generation, "_fold_slot_order", lambda *args: order(*args[:8]))
    assert _cell_classes_missed(tmp_path)


def _durations_beside_single_letter_codes() -> "list[str]":
    """Durations `HH:MM:SS` beside one tenth `x12`/`X12`, 4,000 rows: every
    parent of the durations' family is barred and already as long as the
    longest published length."""
    draw = random.Random(7)
    cells: "list[str]" = []
    for _row in range(4000):
        if draw.random() < 0.1:
            word = f"x{draw.randrange(100)}"
            cells += [word.upper() if draw.random() < 0.5 else word]
        else:
            minutes = int(draw.lognormvariate(0.0, 0.7) * 480) % (48 * 60)
            cells += [f"{minutes // 60:02d}:{minutes % 60:02d}:{draw.randrange(60):02d}"]
    return cells


def test_a_family_keeps_parents_for_its_slots(tmp_path: pathlib.Path) -> None:
    """GATE CASE of `_barred_kept`: the folded count holds (70 slots found no
    partner on 7b28976 and `n_distinct_folded` was missed; 45191fa held it)."""
    _twin_cells, source_missed, twin_missed = _round(tmp_path, _durations_beside_single_letter_codes(), 11)
    assert source_missed == []
    assert "distinct.n_distinct_folded" not in twin_missed


def test_a_family_keeps_parents_red_when_every_asked_parent_stays_barred(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MUTATION: `_barred_kept` frees no parent."""
    monkeypatch.setattr(generation, "_barred_kept", lambda barred, *_args: barred)
    _twin_cells, _source, twin_missed = _round(tmp_path, _durations_beside_single_letter_codes(), 11)
    assert "distinct.n_distinct_folded" in twin_missed


def test_shared_forms_kept_last_gives_numbers_too_large_a_form_numbers_wear() -> None:
    """GATE CASE of `_shared_forms_kept`'s third round (skeptic 2 item 3c): a
    form whose published labels are numbers alone (`1E100`) is still kept for
    the numbers too large to hold, which can be written no other way, as on
    45191fa. Red where the third round gives nothing."""
    out_of_range = generation._OWED_OUT_OF_RANGE
    kept = generation._shared_forms_kept(["1E100"] * 15, (12,), {0: out_of_range}, {"%@%%%": 12}, False)
    assert kept == {out_of_range: {"%@%%%": 12}, generation._OWED_TEXT: {}}


# -- Codex's review of lane L1 (head e994b5f), five items ---------------

def _oracle() -> typing.Any:
    """The oracle, loaded by the width-grid tests' own loader (no new file load)."""
    return width_grid._oracle()


def _held_back_counted(cells: "typing.Iterable[str]") -> "dict[str, int]":
    counted: "dict[str, int]" = {}
    for cell in cells:
        counted[cell] = (counted[cell] if cell in counted else 0) + 1
    return counted


def _exponent_nought_beside_numbers(letter: str) -> "list[str]":
    """Codex item 1: `alpha` x100, `1` x20, `2` x20, `0E2` x20, `3` x5, `4` x5."""
    return ["alpha"] * 100 + ["1"] * 20 + ["2"] * 20 + [f"0{letter}2"] * 20 + ["3"] * 5 + ["4"] * 5


@pytest.mark.parametrize("letter", ["E", "e"])
def test_a_published_exponent_value_is_never_written_on_the_outward_walk(tmp_path: pathlib.Path, letter: str) -> None:
    """CODEX ITEM 1 (HIGH). The walk stepping from `1` and `2` reached `0`,
    the value `0E2` publishes, and wrote seven cells of it on e994b5f: 27
    noughts read where the table held 20, four values where it held five.
    G8.3a's exclusion holds on the outward walk too, in product and oracle."""
    document, _loaded = _described(tmp_path, _exponent_nought_beside_numbers(letter), 11, ("t",))
    twin, _path = _twin(_loaded, 0, tmp_path)
    values = [float(cell) for cell in twin if cell != "alpha"]
    assert values.count(0.0) == 20
    assert sorted(set(values)) == [0.0, 1.0, 2.0, 3.0, 4.0]
    oracle = _oracle()
    assert _held_back_counted(oracle._label_content(document["columns"][0])) == _held_back_counted(twin)


def test_the_outward_walk_skips_a_published_value_and_steps_on() -> None:
    """GATE CASE of `_outward_at`: on the ladder stepping from `1` and `2`, the
    low side's first step is `0`, published as `0E2`, so it holds no value
    and the side is not ended; red where the outward walk asks nothing."""
    ladder = generation._number_ladder(["1", "2", "0E2"], False, [])
    walk = generation._walk_ladder(ladder)
    assert (walk.lowest, walk.highest) == (1, 2)
    states = [generation._outward_at(walk, 0, position) for position in range(4)]
    assert states[0][0] == generation._LADDER_SKIP
    assert states[1] == (generation._LADDER_HERE, 3, generation._SIDE_HIGH)


def _exponent_codes_of_eight_figures() -> "list[str]":
    """Codex item 2: every cell at most five characters, values near 1.45e7."""
    cells = ["alpha"] * 100 + ["1E2"] * 11 + ["3E7"] * 11
    cells += [f"1.{step}E7" for step in range(10)] + [f"1{step}E6" for step in range(10)]
    return cells


def test_a_pooled_placement_is_no_wider_than_any_published_label(tmp_path: pathlib.Path) -> None:
    """CODEX ITEM 2 (MEDIUM). `_pooled_spelling` never asked `figures_cap`, so
    the pool's twenty cells were written as eight-figure integers 14499952
    to 14500048 beside labels of five characters at most (e994b5f, and wide
    at the base too). The pool's mean is then missed, named: the stated
    limit of G8.3a's cap. Product and oracle alike."""
    document, loaded = _described(tmp_path, _exponent_codes_of_eight_figures(), 11, ("t",))
    twin, path = _twin(loaded, 0, tmp_path)
    assert max(len(cell) for cell in twin) <= 5
    assert "suppressed.numbers.mean" in _missed(loaded, path)
    oracle = _oracle()
    assert _held_back_counted(oracle._label_content(document["columns"][0])) == _held_back_counted(twin)


def test_a_pooled_placement_red_without_the_cap(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTATION: every ladder's cap read as nought by the pooled placement alone."""
    original = generation._pooled_spelling

    def uncapped(ladder: typing.Any, *args: typing.Any) -> str:
        return original(generation.dataclasses.replace(ladder, figures_cap=0), *args)

    monkeypatch.setattr(generation, "_pooled_spelling", uncapped)
    _document, loaded = _described(tmp_path, _exponent_codes_of_eight_figures(), 11, ("t",))
    twin, _path = _twin(loaded, 0, tmp_path)
    assert sum(1 for cell in twin if len(cell) == 8) == 20


def _durations_beside_notes_of_two_words(seed: int) -> "list[str]":
    """Codex item 3: 400 cells, a tenth `note N` (half upper-cased), the rest
    durations `HH:MM:SS`."""
    draw = random.Random(seed)
    cells: "list[str]" = []
    for _row in range(400):
        if draw.random() < 0.1:
            cell = f"note {draw.randrange(15)}"
            if draw.random() < 0.5:
                cell = cell.upper()
        else:
            minute = draw.randrange(2880)
            cell = f"{minute // 60:02d}:{minute % 60:02d}:{draw.randrange(60):02d}"
        cells += [cell]
    return cells


def _word_mean_deviated(tmp_path: pathlib.Path, seed: int) -> "tuple[bool, list[str]]":
    _document, loaded = _described(tmp_path, _durations_beside_notes_of_two_words(seed), 11)
    built = generation.generate(loaded, 0)
    return any(deviation.fact == "words.mean" for deviation in built.deviations), list(built.columns[0])


@pytest.mark.parametrize("seed", [849, 1, 3, 8, 21])
def test_a_fold_slot_takes_a_partner_of_its_planned_words(tmp_path: pathlib.Path, seed: int) -> None:
    """CODEX ITEM 3 (MEDIUM). Seed 849: two slots of four and five rows planned
    one word took two-word partners and `words.mean` came back 1.135 against
    1.105 to 1.13 on e994b5f, a deviation the base did not have; seeds 1, 3, 8
    and 21 the same. The slot's planned words are asked first inside each
    pass keeping the long-tail line, and the form's 344 durations stay."""
    deviated, cells = _word_mean_deviated(tmp_path, seed)
    assert not deviated
    if seed == 849:
        assert sum(parsing.token_count(cell) for cell in cells) == 446
        assert sum(1 for cell in cells if re.fullmatch(r"\d\d:\d\d:\d\d", cell)) == 344


def test_a_fold_slot_red_when_its_planned_words_are_not_asked(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTATION: the slot's planned words dropped before the partner search."""
    original = generation._partner_of

    def wordless(*args: typing.Any, **named: typing.Any) -> "str | None":
        named.pop("words", None)
        return original(*args, **named)

    monkeypatch.setattr(generation, "_partner_of", wordless)
    deviated, _cells = _word_mean_deviated(tmp_path, 849)
    assert deviated


def test_the_indexed_partner_walk_answers_as_the_plain_walk_when_words_are_asked() -> None:
    """GATE CASE of `_partner_indexed` with ``words``: the plain walk's answer,
    a parent of the asked words first and any other after it."""
    draw = random.Random(11)
    for _case in range(40):
        folded = draw.randrange(2, 9)
        total = folded + draw.randrange(1, 9)
        spellings = ["".join(draw.choice("ab1 -") for _each in range(draw.randrange(1, 5))) for _each in range(folded)]
        families = [draw.choice(["f", "g"]) for _each in range(total)]
        sizes = [draw.randrange(1, 6) for _each in range(total)]
        results: "list[list[str | None]]" = []
        for indexed in (False, True):
            used = {spelling: generation._WRITTEN for spelling in spellings}
            carried: "dict[int, int]" = {}
            written = list(spellings)
            kept = ({}, {}) if indexed else (None, None)
            answers = []
            for index in range(folded, total):
                windows = [(1, 5)] * total
                found = generation._partner_of(
                    index, folded, written, families, used, windows, sizes, 8, carried,
                    parents=kept[0], spent=kept[1], words=1 + index % 2,
                )
                if found is not None:
                    used[found] = generation._WRITTEN
                answers += [found]
                written += [found or f"made{index}"]
            results += [answers]
        assert results[0] == results[1]


@pytest.mark.parametrize("place", ["@", "&"])
def test_the_oracle_reads_and_writes_its_own_overflow_spelling(tmp_path: pathlib.Path, place: str) -> None:
    """CODEX ITEM 4 (MEDIUM). Method-derived witnesses of G8.3a's overflow
    spelling: `1` nought-padded before the letter, `E` in a case-blind place
    and `e` in a lower-case one, `309` after it, a number too large to hold.
    On e994b5f the oracle read `01E309` as a word, so `%%@%%%` was not shared
    and its held-back codes were written `1` and `2`."""
    oracle = _oracle()
    form = f"%%{place}%%%"
    letter = "E" if place == "@" else "e"
    assert oracle.overflow_spelling(form, 0) == f"01{letter}309"
    assert oracle.notation_reading(f"01{letter}309")[0] == oracle.NOTATION_OUT_OF_RANGE
    assert oracle.notation_reading(f"12{letter}005")[0] == oracle.NOTATION_NUMBER
    assert oracle.form_also_reads(form, oracle.NOTATION_OUT_OF_RANGE)
    cells = ["alpha"] * 100 + [f"12{letter}005"] * 20 + [f"13{letter}005"] * 20 + [f"52{letter}638"] * 5 + [f"41{letter}626"] * 5
    document, loaded = _described(tmp_path, cells, 11, ("t",))
    content = oracle._label_content(document["columns"][0])
    stand_ins = [cell for cell in content if cell not in ("alpha", f"12{letter}005", f"13{letter}005")]
    assert len(stand_ins) == 10
    for cell in stand_ins:
        assert oracle.notation_reading(cell)[0] == oracle.NOTATION_OUT_OF_RANGE
        assert parsing.census_form(cell, {form: 1}) == form
    assert document["columns"][0]["shape_forms"] == {form: 50}
    assert f"01{letter}309" in stand_ins
    twin, _path = _twin(loaded, 0, tmp_path)
    assert _held_back_counted(content) == _held_back_counted(twin)


def test_the_past_binary64_shape_states_the_boundary_it_holds() -> None:
    """CODEX ITEM 5 (LOW). The shape's own statement said that at seventeen
    figures or fewer the family offers a cell's spelling at a width; it does
    not: `45000.123456789012`, seventeen figures, reads back as
    `45000.12345678901` and is outside the styles at a published width of
    twelve (older than lane L1). The boundary stays where P3-V4-F1's near
    neighbours need it, past seventeen, and the statement now says what it
    leaves outside. Red on e994b5f, whose docstring claimed the false
    guarantee."""
    statement = " ".join((validation._wears_figures_past_binary64.__doc__ or "").split())
    assert "at seventeen figures or fewer one spelling at a width is the value's own" not in statement
    assert "`45000.123456789012` reads back as `45000.12345678901`" in statement
    assert validation._cells_outside_the_styles(["45000.123456789012"], False, (12,)) == 1
    assert validation._cells_outside_the_styles(["45000.1234567890123"], False, (13,)) == 0
    assert validation._cells_outside_the_styles(["45000.1234567890123"], False, (12,)) == 1


def test_the_past_binary64_boundary_red_at_sixteen(monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTATION: the boundary moved to sixteen figures admits the seventeen-figure cell."""
    monkeypatch.setattr(validation, "_BINARY64_FIGURES", 16)
    assert validation._cells_outside_the_styles(["45000.123456789012"], False, (12,)) == 0
