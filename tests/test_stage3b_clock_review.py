"""The clock census's one review (stage 3b landing 3b.5, lane C1, plan P4-D373): each item it raised, pinned.

Codex read landing 3b.5 at 90466b2 and raised eight items, every one
fixed here and none sent back (the owner, 2026-09-28). Each clause below
failed at 90466b2 and passes with its fix, and each fix that is a rule
rather than a sentence has a mutant that turns its clause red again:

* item 1 `test_item_1_every_rung_of_an_all_different_column_stays_at_its_rank`
  -- on a column whose values all differ the run's ranks were read
  without their pins and then stepped apart over the whole run, which
  moved the pins: 100 different minutes published their median at
  `09:43` and the twin held `09:49`, the third quartile `11:21` and the
  twin `11:24`, and the oracle froze the same error (vectors file 21's
  `clock_census_all_different` held `07:39` at its first quartile's rank,
  published `07:30`); `test_item_1_every_frozen_case_holds_its_rungs`
  checks every frozen case of file 21 with the product's own runs, not
  the oracle's; `test_item_1_a_pin_is_a_wall_of_the_step_apart` holds the
  step apart off a pin it crowds, which the step as built moved; and
  `test_item_1_a_rank_off_a_hole_stays_between_its_pins` the hole step,
  which crossed a pin where the free step nearest a declared absence lay
  past it (mutant: a rank off a hole free to cross a pin);
* item 2 `test_item_2_the_twelve_hour_question_offers_the_labels_answer`
  -- 100 rows each of `07:00`, `08:00` and `09:00` were asked the 12-hour
  question alone, `keep` or `twelve-hour`, and the questions file refused
  `code` (mutant: the 12-hour question asked without the labels answer);
* item 3 `test_item_3_neighbouring_times_on_many_rows_are_asked_about` --
  twenty rows each of `14:00` to `14:11` stand out from nothing, so they
  publish a census, and nobody was asked; read as clock times the seed-0
  twin wrote `14:01` 39 times and `14:08` 10, where each label had 20
  (mutant: asked only where heaps hold the body, as before);
* item 4 `test_item_4_the_report_counts_a_code_once` -- the generation
  report counted every cell of a code as a different value, drew 113 to
  405 against validation's 14 to 306 and called both the table's 102 and
  the twin's 111 outside (mutant: a code counted once a cell);
* item 5 `test_item_5_the_loader_refuses_what_generation_cannot_lay` --
  a heap of a body all at one time one row short loaded and generation
  stopped on an internal error, and a heap holding all of a listing
  tail's rows beside a second listed value loaded and the twin lost the
  value and the mean (mutants: no room asked without a census; a listed
  tail's heaps not reconciled);
* item 6 `test_item_6_the_heaps_are_looked_up_in_work_that_grows_with_them`
  -- every published value asked the LIST of heaps whether it was one,
  so the loader's work grew with the square of the heaps (mutant: the
  list again);
* item 7 `test_item_7_a_time_of_another_precision_is_not_called_no_time`
  -- NF107 called `14:00:00` among times written to the minute "text
  that is not a time of day";
* item 8 `test_item_8_the_clock_kpi_says_where_a_clock_shaped_cell_is_no_time`
  -- K-S3-49 promised every clock-shaped twin cell a time, while file 21's
  `labels_clock_line` writes ten `26:32` to keep its label column labels.

And one more, not Codex's, found by lane R2a's reach battery and fixed in
the same stream: `test_time7_every_twin_cell_is_a_time_in_the_columns_spelling`
-- a SQL Server `time(7)` column, every cell `HH:MM:SS` and seven figures
of fraction, is free text, and its twin wrote `44:40:00.0023504` and 855
more cells that are no time of day, because G8.3's clock supply did not
know a fraction (mutant: the supply blind to it again); past 4,096
different times a walk of the form stopped and wrote the rest in no
time's spelling, in free text and in a long tail's held-back labels
alike (mutants: each walk bounded as every other form's); and the oracle
states the same supply and bounds, call by call, since no frozen case
holds such a form. Each failed at cc50fd7.

And one the verification of this stream found in landing 3b.5 itself:
`test_tail_order_a_listing_tail_holds_the_order_of_the_day` -- a tail
that lists its values listed them sorted as text, so on a 12-hour clock,
a one-figure hour and the declared half-day face the loader refused the
producer's own description under DT3, and `synthtwin generate` told the
person it had been changed since it was written (mutant: the values
sorted as text again). It failed at 90466b2 and at 0138325.

And one its second verification found, at d4f5ee4:
`test_round_2_an_absence_declared_on_a_laid_column_stays_absent` -- a
time declared missing on a column laid on its census came back as
present cells, a run holding nothing but the absence taking a share of
its group and a tail's draw landing on it (mutants: a run's share over
its absent steps again; a tail drawn without skipping them, at the
minute placed as G7A.4 places it); the oracle lays the minute column as
the product does; and CC5 refuses a hand-edited group, or a drawn tail,
left no step to stand on (mutants: each refusal withdrawn). Each clause
failed at d4f5ee4. And `test_round_2_an_absence_another_column_publishes_stays_absent`
-- a declaration reaches the whole table, so the places are those any
column's absent spellings name: one column writing `00:00` for unknown
times and another pressed against midnight wrote it in the second
column's twin at d4f5ee4 and at d0ae8f7 (mutant: the column's own
spellings alone).

And two rules the verification of that round found no clause held, at
baaf9de: `test_round_2_the_loader_asks_room_beside_every_columns_absence`
patched the loader's reading of the table's absent spellings on every
call, so it held nothing of that reading; it now builds two columns, `u`'s
absent key moved by hand onto the only step of `t`'s group of 14, and CC5
refuses the description naming `t` (mutant: each column's own spellings
alone -- it loads, and generation stops on an internal error); and
`test_round_2_a_marker_typed_in_lower_case_names_its_absent_place` --
`12:00 am` declared missing names the place a column of `h:mm AM` writes
`12:00 AM`, where a reading in its own case alone let the low tail draw
a cell onto it (mutant: the case not folded). And one defect it found
older than that round, the same at d4f5ee4 and at baaf9de:
`test_round_2_a_present_time_on_an_absent_spelling_is_written_as_the_table_wrote_it`
-- a column of `hh:mm` holding 15 real times at midnight written `0:00`
beside `00:00` declared missing publishes a heap and a listed low tail
on `00:00`, and every twin wrote all 35 such cells `00:00`; those times
are now written `0:00`, the one other spelling the reader reads there,
on a column laid on its census, laid as before by G7A.4 and beside
another column's `00:00` alike, and so are a heap and a low boundary on
such a place; the oracle writes the same (mutants: every present time
in the form's own spelling; each column's own absent spellings alone).
And its note on K-S3-11's driver:
`test_round_2_the_tail_leak_driver_draws_its_windows_beside_the_tables_absences`
-- the driver drew a clock tail's window beside the column's own absent
spellings alone, where the checker draws it beside every column's.
"""

from __future__ import annotations

import collections
import copy
import csv
import importlib.util
import io
import json
import pathlib
import random
import re
import types
import typing

import pytest

import fixtures

from synthtwin import (
    asking,
    calendar_clock,
    cli,
    contract,
    errors,
    generation,
    parsing,
    profile,
    reading,
    rendering,
    taxonomy,
    validation,
)

_HERE = pathlib.Path(__file__).resolve().parent
_VECTORS_21 = _HERE / "reference" / "generation-branch-vectors-21.json"
_LEDGER = _HERE / "kpi" / "ledger.json"


def _minutes(ordinals: "typing.Iterable[int]") -> "list[str]":
    return [f"{at // 60:02d}:{at % 60:02d}" for at in ordinals]


def _described(
    folder: pathlib.Path,
    cells: "list[str]",
    floor: int = 11,
    codes: "tuple[str, ...]" = (),
    declared: "tuple[str, ...]" = (),
) -> "tuple[dict[str, typing.Any], contract.Profile]":
    """One column `t` described by the real producer, written and loaded."""
    folder.mkdir(parents=True, exist_ok=True)
    table = fixtures.write(folder, "table.csv", "\n".join(["t"] + cells) + "\n")
    settings = taxonomy.Settings(small_cell_floor=floor, declared_missing_values=declared)
    document = profile.build_document(
        reading.read_table(str(table), small_cell_floor=floor), settings, [], list(codes)
    )
    written = fixtures.write_profile(folder, "table.json", document)
    return document, contract.load_profile(str(written))


def _block(document: "dict[str, typing.Any]") -> "dict[str, typing.Any]":
    block = document["columns"][0]
    assert block["name"] == "t"
    return typing.cast("dict[str, typing.Any]", block)


def _twin(loaded: contract.Profile, seed: int, folder: pathlib.Path) -> "tuple[list[str], pathlib.Path]":
    text = rendering.twin_csv(generation.generate(loaded, seed))
    path = fixtures.write(folder, f"twin-{seed}.csv", text)
    rows = list(csv.reader(io.StringIO(text)))
    return [row[0] for row in rows[1:] if row], path


def _missed(loaded: contract.Profile, path: pathlib.Path) -> "list[str]":
    return sorted(
        f"{check.column}:{check.subcheck}"
        for check in validation.measure(loaded, str(path)).checks
        if check.verdict == validation.MISSED
    )


def _rungs_off(block: "dict[str, typing.Any]", cells: "list[str]", absent: "tuple[str, ...]" = ()) -> "list[str]":
    """Every published rung the twin's parsed cells do not hold at its rank.

    ON A COLUMN WHOSE VALUES ALL DIFFER EVERY PUBLISHED RUNG IS PINNED,
    whatever the runs: no heap stands in such a column, so each census
    group is one run, and the twin's group holds the real group's ranks,
    its count being the real one -- a rung's rank lies in the run holding
    its value. So the twin's value at the rung's rank is the rung, read
    off the cells alone, with nothing of the layout asked.
    """
    form = block["clock_form"]
    ordered = sorted(
        found
        for found in (parsing.clock_ordinal(cell, form) for cell in cells if cell not in absent)
        if found is not None
    )
    off: "list[str]" = []
    for step in range(1, len(generation._PCT) - 1):
        name = generation._LADDER_NAMES[step]
        rung = block["clock_percentiles"][name]
        if rung is None:
            continue
        rank = generation._rung_rank(generation._PCT[step], len(ordered))
        if ordered[rank] != parsing.clock_ordinal(rung, form):
            off += [f"{name}: {rung} published, {parsing.clock_spelling(ordered[rank], form)} at its rank"]
    return off


# -- item 1: a published rung stays where it is published ---------------


def _codex_minutes() -> "list[str]":
    """Codex's column: 100 different minutes from 07:00 to 12:59."""
    return _minutes(random.Random(0).sample(range(420, 780), 100))


def _all_different(seed: int) -> "list[str]":
    """A seeded column of different minutes, 100 to 300 of them."""
    draw = random.Random(9373 + seed)
    count = draw.choice((100, 150, 300))
    start = draw.choice((360, 420, 600))
    return _minutes(draw.sample(range(start, start + count + draw.randrange(40, 400)), count))


def _step_apart_as_built(places: "list[int]", units: int) -> "list[int]":
    """90466b2's step apart: over the whole run, its pins moved with the rest."""
    for index in range(1, len(places)):
        places[index] = max(places[index], places[index - 1] + 1)
    for index in range(len(places) - 1, -1, -1):
        ceiling = units - (len(places) - index)
        if index + 1 < len(places):
            ceiling = min(ceiling, places[index + 1] - 1)
        places[index] = max(0, min(places[index], ceiling))
    return places


def _rungs_off_all_different(folder: pathlib.Path, seeds: "tuple[int, ...]") -> "list[str]":
    off: "list[str]" = []
    for which, cells in [("codex", _codex_minutes())] + [(f"seeded-{one}", _all_different(one)) for one in range(4)]:
        document, loaded = _described(folder / which, cells)
        block = _block(document)
        assert block["clock_step"] is not None and block["n_distinct"] == len(cells), which
        for seed in seeds:
            twin, path = _twin(loaded, seed, folder / which)
            assert len(set(twin)) == len(twin), (which, seed)
            off += [f"{which} seed {seed} {line}" for line in _rungs_off(block, twin)]
            assert _missed(loaded, path) == [], (which, seed)
    return off


def test_item_1_every_rung_of_an_all_different_column_stays_at_its_rank(tmp_path: pathlib.Path) -> None:
    """The median `09:43` and third quartile `11:21` of Codex's 100 minutes stay at their ranks.

    At 90466b2 the twin held `09:49` and `11:24` there at seed 0, and over
    Codex's column and four seeded ones at seeds 0 to 2 most published
    rungs moved, every twin validating with nothing missed: the report's
    windows are the census groups', which hold a moved rung.
    """
    document, loaded = _described(tmp_path / "codex", _codex_minutes())
    block = _block(document)
    assert (block["clock_percentiles"]["p50"], block["clock_percentiles"]["p75"]) == ("09:43", "11:21")
    twin, _path = _twin(loaded, 0, tmp_path / "codex")
    assert _rungs_off(block, twin) == []
    assert _rungs_off_all_different(tmp_path / "battery", (0, 1, 2)) == []


def test_item_1_a_pin_is_a_wall_of_the_step_apart() -> None:
    """A run of ten steps, its pin on step 4 with four ranks below it and two laid on one step.

    The ranks below the pin take steps 0 to 3 and the pin stays on 4.
    Where the run's pins are its knots the layout seldom crowds a pin so
    -- none of 200,000 random runs did -- and the wall makes it never:
    the step apart as built pushed the pin itself to step 5.
    """
    kept = generation._clock_kept_apart([0, 2, 2, 3, 4, 6, 8], [4], 10)
    assert kept == [0, 1, 2, 3, 4, 6, 8]
    assert _step_apart_as_built([0, 2, 2, 3, 4, 6, 8], 10)[4] == 5


def _pin_beside_a_hole() -> "tuple[list[str], str]":
    """A first quartile with a declared absence one minute above it and its stretch packed.

    Twenty-five minutes three apart up to the first quartile, `08:01` one
    minute above it declared missing and written by twelve rows, the
    next twenty-four minutes from `08:03` one apart, and the rest three
    apart again. A rank the twin lays on `08:01` must move; inside its
    pins the nearest free minute is above the packed stretch, and the
    free minute past the pin below is nearer.
    """
    rank_25 = generation._rung_rank(25, 100)
    rank_50 = generation._rung_rank(50, 100)
    below = [420 + 3 * place for place in range(rank_25 + 1)]
    pin = below[len(below) - 1]
    packed = list(range(pin + 3, pin + 3 + rank_50 - rank_25 - 1))
    above = [packed[len(packed) - 1] + 2 + 3 * place for place in range(100 - len(below) - len(packed))]
    hole = _minutes([pin + 1])[0]
    cells = _minutes(below + packed + above) + [hole] * 12
    random.Random(31).shuffle(cells)
    return cells, hole


def test_item_1_a_rank_off_a_hole_stays_between_its_pins(tmp_path: pathlib.Path) -> None:
    """The first quartile stays at its rank where a rank beside it steps off a declared absence."""
    cells, hole = _pin_beside_a_hole()
    document, loaded = _described(tmp_path, cells, declared=(hole,))
    block = _block(document)
    assert block["missing_by_source"] == {hole: 12} and block["clock_step"] == 60
    for seed in (4, 6, 7):
        twin, path = _twin(loaded, seed, tmp_path)
        assert twin.count(hole) == 12, seed
        assert _rungs_off(block, twin, (hole,)) == [], seed
        assert _missed(loaded, path) == [], seed


def test_item_1_red_when_a_rank_off_a_hole_crosses_a_pin(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(generation, "_clock_between_pins", lambda _index, _fixed, _places, units: (0, units - 1))
    cells, hole = _pin_beside_a_hole()
    document, loaded = _described(tmp_path, cells, declared=(hole,))
    twin, _path = _twin(loaded, 4, tmp_path)
    assert _rungs_off(_block(document), twin, (hole,)) != []


def _frozen_rungs_off(case: "dict[str, typing.Any]") -> "tuple[int, list[str]]":
    """How many rungs a frozen case pins, and which its frozen content misses.

    The runs are the PRODUCT's (`calendar_clock.clock_body_blocks`) over
    the case's published column, and the cells the oracle's: a rung whose
    rank lies in a run holding its value on the step is pinned (method
    G7A.4b, step 3), and the frozen value at its rank must be the rung.
    """
    column = case["column"]
    if column.get("clock_step") is None or column["low_tail"] is None:
        return 0, []
    form = column["clock_form"]
    stride = max(1, column["clock_step"] // parsing.clock_step(form))
    parsed = column["n_present"] - column["n_unparsed"]
    low, high = column["low_tail"], column["high_tail"]
    body = (parsing.clock_ordinal(low["boundary"], form), parsing.clock_ordinal(high["boundary"], form))
    groups = tuple((group["first"], group["last"], group["count"]) for group in column["clock_census"])
    heaps = tuple((parsing.clock_ordinal(heap["value"], form), heap["count"]) for heap in column["clock_heaps"])
    absent = tuple(column.get("missing_by_source") or {})
    blocks = calendar_clock.clock_body_blocks(
        parsed, (low["rows"], high["rows"]), body, groups, heaps, form, stride,  # type: ignore[arg-type]
        calendar_clock.absent_places(absent, form),
    )
    assert blocks is not None
    ordered = sorted(
        found
        for found in (parsing.clock_ordinal(cell, form) for cell in case["content"] if cell not in absent)
        if found is not None
    )
    assert len(ordered) == parsed
    pinned = 0
    off: "list[str]" = []
    for step in range(1, len(generation._PCT) - 1):
        rung = column["clock_percentiles"][generation._LADDER_NAMES[step]]
        if rung is None:
            continue
        rank = generation._rung_rank(generation._PCT[step], parsed)
        value = parsing.clock_ordinal(rung, form)
        assert value is not None
        for block in blocks:
            if (
                not block.heap
                and block.first_rank <= rank < block.first_rank + block.cells
                and block.low <= value <= block.high
                and (value - block.low) % stride == 0
            ):
                pinned = pinned + 1
                if ordered[rank] != value:
                    off += [f"{rung} published, {parsing.clock_spelling(ordered[rank], form)} frozen"]
    return pinned, off


def test_item_1_every_frozen_case_holds_its_rungs() -> None:
    """Vectors file 21, read by the product's runs: every pinned rung is frozen at its rank.

    At 90466b2 `clock_census_all_different` froze `07:39` at the rank of
    its first quartile, published `07:30`, and the oracle wrote it.
    """
    cases = json.loads(_VECTORS_21.read_text(encoding="utf-8"))["cases"]
    pinned = 0
    off: "list[str]" = []
    for name in sorted(cases):
        found, missed = _frozen_rungs_off(cases[name])
        pinned = pinned + found
        off += [f"{name}: {line}" for line in missed]
    assert off == []
    assert pinned >= 20, pinned


# -- item 2: the clock-face question offers every answer that fits ------


def _three_hours() -> "list[str]":
    cells = ["07:00"] * 100 + ["08:00"] * 100 + ["09:00"] * 100
    random.Random(2).shuffle(cells)
    return cells


def _questions(document: "dict[str, typing.Any]", cells: "list[str]") -> "list[asking.Question]":
    return asking.questions_for(document, [cells], taxonomy.Settings(), [])


def _many_times_on_twelve_hours() -> "list[str]":
    """709 different minutes on hours 01 to 12 over 3,000 rows: too many for labels."""
    draw = random.Random(49)
    cells = _minutes(draw.sample(range(60, 13 * 60), 709))
    cells += [draw.choice(cells) for _row in range(3000 - 709)]
    draw.shuffle(cells)
    return cells


def test_item_2_the_twelve_hour_question_offers_the_labels_answer(tmp_path: pathlib.Path) -> None:
    """`keep`, `twelve-hour` and `code`, and the questions file takes `code` as `--code`.

    At 90466b2 the column was asked the 12-hour question alone, so the
    clock-or-labels question never ran, and the questions file refused
    `code` as an answer the entry did not offer.
    """
    cells = _three_hours()
    document, _loaded = _described(tmp_path, cells)
    assert _block(document)["role"] == taxonomy.ROLE_CLOCK
    asked = _questions(document, cells)
    assert [question.name for question in asked] == ["t"]
    question = asked[0]
    assert question.reason == asking.BECAUSE_TWELVE_HOUR
    assert [choice.answer for choice in question.choices] == [
        asking.ANSWER_KEEP, asking.ANSWER_TWELVE_HOUR, asking.ANSWER_CODE,
    ]
    assert question.taken == asking.ANSWER_KEEP
    assert "a list of labels written as times also holds" in question.shape
    written = asking.questions_document("table.csv", asked, [])
    written["asked"][0]["your_answer"] = asking.ANSWER_CODE  # type: ignore[index]
    assert asking.answers_in(written, "questions.json").codes == ("t",)
    declared, _loaded = _described(tmp_path / "answered", cells, codes=("t",))
    assert _block(declared)["role"] == taxonomy.ROLE_CATEGORICAL
    # ...and a clock in one figure, whose colon question offers `code`
    # already, offers it once.
    figures = [cell.lstrip("0") for cell in cells]
    document, _loaded = _described(tmp_path / "figures", figures)
    answers = [choice.answer for choice in _questions(document, figures)[0].choices]
    assert answers.count(asking.ANSWER_CODE) == 1 and asking.ANSWER_TWELVE_HOUR in answers
    # ...and a column the 12-hour question fits and the clock-or-labels
    # question does not, too many different times for labels, is offered
    # no code: `code` comes only with the other question, as K-S3-49 now
    # says (the verification of the review stream).
    many = _many_times_on_twelve_hours()
    document, _loaded = _described(tmp_path / "many", many)
    asked = _questions(document, many)
    assert [question.reason for question in asked] == [asking.BECAUSE_TWELVE_HOUR]
    assert [choice.answer for choice in asked[0].choices] == [asking.ANSWER_KEEP, asking.ANSWER_TWELVE_HOUR]


def test_item_2_red_without_the_labels_answer(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(asking, "_with_the_labels_answer", lambda question, _labels: question)
    cells = _three_hours()
    document, _loaded = _described(tmp_path, cells)
    assert asking.ANSWER_CODE not in [choice.answer for choice in _questions(document, cells)[0].choices]


# -- item 3: neighbouring times on many rows are asked about -------------


def _twelve_minutes() -> "list[str]":
    """Codex's column: twenty rows each of `14:00` to `14:11`."""
    cells: "list[str]" = []
    for minute in range(12):
        cells += [f"14:{minute:02d}"] * 20
    random.Random(3).shuffle(cells)
    return cells


def test_item_3_neighbouring_times_on_many_rows_are_asked_about(tmp_path: pathlib.Path) -> None:
    """Twelve minutes twenty rows each publish a census and are asked about; `code` keeps each count.

    At 90466b2 nobody was asked: the question waited for heaps to hold
    the body, and neighbouring values on as many rows as each other stand
    out from nothing. Enter keeps the clock reading; `code` reads them as
    labels, and the twin then holds each one's twenty rows exactly, where
    read as times its seed-0 twin wrote `14:01` 39 times and `14:08` 10.
    """
    cells = _twelve_minutes()
    document, _loaded = _described(tmp_path, cells)
    block = _block(document)
    assert block["role"] == taxonomy.ROLE_CLOCK
    assert block["clock_heaps"] == [] and block["clock_census"] != []
    asked = _questions(document, cells)
    assert [question.reason for question in asked] == [asking.BECAUSE_FEW_CLOCK_TIMES]
    assert [choice.answer for choice in asked[0].choices] == [asking.ANSWER_KEEP, asking.ANSWER_CODE]
    assert asked[0].taken == asking.ANSWER_KEEP
    assert "written by at least 11 rows" in asked[0].shape
    declared, loaded = _described(tmp_path / "answered", cells, codes=("t",))
    assert _block(declared)["role"] == taxonomy.ROLE_CATEGORICAL
    twin, _path = _twin(loaded, 0, tmp_path / "answered")
    assert collections.Counter(twin) == collections.Counter(cells)
    # ...and one of those minutes on fewer rows than the line is times, as
    # a list of labels the floor publishes holds no such value: not asked.
    fewer = [cell for cell in cells if cell != "14:05"] + ["14:05"] * 5
    document, _loaded = _described(tmp_path / "fewer", fewer)
    assert _questions(document, fewer) == []


def test_item_3_red_when_asked_only_where_heaps_hold_the_body(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    built = asking._times_each_shared

    def heaps_alone(block: "dict[str, object]", present: "list[str]", line: int) -> bool:
        return block["clock_census"] == [] and built(block, present, line)

    monkeypatch.setattr(asking, "_times_each_shared", heaps_alone)
    cells = _twelve_minutes()
    document, _loaded = _described(tmp_path, cells)
    assert _questions(document, cells) == []


# -- item 4: the generation report counts a code once --------------------


def _beside_a_code() -> "list[str]":
    """Codex's column: 9,900 times over 102 minutes, and 100 `UNK`."""
    cells = _minutes(480 + (place % 101) + (place % 101) // 10 for place in range(9900))
    return cells + ["UNK"] * 100


def _distinct_windows(tmp_path: pathlib.Path) -> "tuple[list[tuple[str, str, str, str, bool]], list[tuple[str, str]]]":
    document, loaded = _described(tmp_path, _beside_a_code())
    block = _block(document)
    assert block["clock_codes"] == [{"count": 100, "spelling": "UNK"}] and block["n_distinct"] == 102
    twin = generation.generate(loaded, 0)
    reported = [
        (found.fact, found.achieved, found.lowest, found.highest, found.inside)
        for found in twin.approximations
        if found.fact in ("n_distinct", "n_distinct_folded")
    ]
    path = fixtures.write(tmp_path, "twin.csv", rendering.twin_csv(twin))
    checked = [
        (check.subcheck, check.verdict)
        for check in validation.measure(loaded, str(path)).checks
        if check.subcheck in ("distinct.n_distinct", "distinct.n_distinct_folded")
    ]
    return reported, checked


def test_item_4_the_report_counts_a_code_once(tmp_path: pathlib.Path) -> None:
    """The report's window for the different values is validation's, 14 to 306, and holds 111.

    At 90466b2 it counted each of the 100 `UNK` cells as a value of its
    own, drew 113 to 405, and said the twin's 111 -- and the table's 102
    -- lay outside, where validation held the twin inside its 14 to 306.
    """
    reported, checked = _distinct_windows(tmp_path)
    assert reported == [
        ("n_distinct", "111", "14", "306", True),
        ("n_distinct_folded", "111", "14", "306", True),
    ]
    assert checked == [
        ("distinct.n_distinct", validation.WITHIN_BOUND),
        ("distinct.n_distinct_folded", validation.WITHIN_BOUND),
    ]


def test_item_4_red_when_a_code_counts_once_a_cell(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    built = generation._clock_approximations

    def every_cell(
        column: contract.ColumnBlock,
        facts: contract.ClockFacts,
        written: "list[str]",
        floor: int,
        holes: "tuple[str, ...]" = (),
    ) -> "list[generation.Approximation]":
        import dataclasses

        return built(column, dataclasses.replace(facts, clock_codes=()), written, floor, holes)

    monkeypatch.setattr(generation, "_clock_approximations", every_cell)
    reported, _checked = _distinct_windows(tmp_path)
    assert [inside for *_rest, inside in reported] == [False, False]


# -- item 5: the loader refuses what generation cannot lay ---------------


def _three_heaps(tmp_path: pathlib.Path) -> "tuple[dict[str, typing.Any], pathlib.Path]":
    document, _loaded = _described(tmp_path, _three_hours())
    block = _block(document)
    assert block["clock_census"] == [] and [heap["count"] for heap in block["clock_heaps"]] == [100, 100, 100]
    assert block["low_tail"]["boundary"] == block["high_tail"]["boundary"] == "08:00"
    return document, tmp_path


def _loads(folder: pathlib.Path, document: "dict[str, typing.Any]", name: str) -> "contract.Profile | str":
    path = fixtures.write_profile(folder, f"{name}.json", document)
    try:
        return contract.load_profile(str(path))
    except errors.ProfileError as refused:
        return f"{refused}"


def _one_row_short(document: "dict[str, typing.Any]") -> "dict[str, typing.Any]":
    """`08:00`'s heap 99 of the body's 100 cells, all of them at `08:00`."""
    changed = copy.deepcopy(document)
    for heap in _block(changed)["clock_heaps"]:
        if heap["value"] == "08:00":
            heap["count"] = 99
    return changed


def _listed_beside_a_full_heap(document: "dict[str, typing.Any]") -> "dict[str, typing.Any]":
    """The low tail's 100 rows listing `07:00` and `07:30` at a mean of 45, its heap on `07:00` 100."""
    changed = copy.deepcopy(document)
    block = _block(changed)
    block["clock_step"] = 1800
    block["low_tail"]["values"] = ["07:00", "07:30"]
    block["low_tail"]["mean_distance"] = 45.0
    return changed


def test_item_5_the_loader_refuses_what_generation_cannot_lay(tmp_path: pathlib.Path) -> None:
    """CC5 asks a block with no census for room; CH1 holds a listing tail to its heaps.

    At 90466b2 both loaded: the first stopped generation on an internal
    error, a body cell on no heap with no step to stand on, and the
    second's twin wrote no `07:30` and a low tail 60 minutes out on
    average against a published 45. The unchanged description loads,
    generates and validates.
    """
    document, folder = _three_heaps(tmp_path)
    loaded = _loads(folder, document, "unchanged")
    assert isinstance(loaded, contract.Profile)
    _twin_cells, path = _twin(loaded, 0, folder)
    assert _missed(loaded, path) == []
    short = _loads(folder, _one_row_short(document), "short")
    assert isinstance(short, str) and "no census is published, and 1 cells" in short, short
    listed = _loads(folder, _listed_beside_a_full_heap(document), "listed")
    assert isinstance(listed, str) and "beside 1 value(s) it lists on no heap" in listed, listed
    # ...and the mean on its own: 99 rows of the heap leave the one row of
    # `07:30` 30 minutes out where the mean wants 1,500 more.
    meant = _listed_beside_a_full_heap(document)
    for heap in _block(meant)["clock_heaps"]:
        if heap["value"] == "07:00":
            heap["count"] = 99
    refused = _loads(folder, meant, "meant")
    assert isinstance(refused, str) and "the low tail's mean puts the sum of its distances" in refused, refused


def test_item_5_red_without_the_room_asked_beside_no_census(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    built = calendar_clock.clock_group_reach
    monkeypatch.setattr(
        calendar_clock, "clock_group_reach",
        lambda groups, form, stride, body, heaps, absent=(): [
            max(1, units) for units in built(groups, form, stride, body, heaps, absent)
        ],
    )
    document, folder = _three_heaps(tmp_path)
    loaded = _loads(folder, _one_row_short(document), "short")
    assert isinstance(loaded, contract.Profile)
    with pytest.raises(errors.ProfileError):
        generation.generate(loaded, 0)


def test_item_5_red_without_the_listed_tails_reconciled(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(contract, "_listed_tails_hold_their_heaps", lambda *_a: None)
    document, folder = _three_heaps(tmp_path)
    loaded = _loads(folder, _listed_beside_a_full_heap(document), "listed")
    assert isinstance(loaded, contract.Profile)
    twin, path = _twin(loaded, 0, folder)
    assert "07:30" not in twin
    assert "t:tails.low.values" in _missed(loaded, path)


# -- item 6: the heaps are looked up in work that grows with them --------

# What work that grows with the heaps may grow by when they double, and
# what the list lookup reaches, so the measure is known to see it.
_LINEAR_AT_MOST = 2.5
_SQUARE_AT_LEAST = 3.0


class _Counted(int):
    """A clock ordinal whose every equality test is counted."""

    __hash__ = int.__hash__

    def __eq__(self, other: object) -> bool:
        _COMPARED[0] += 1
        return int.__eq__(self, other)


_COMPARED = [0]


def _heaped_description(folder: pathlib.Path, heaps: int) -> pathlib.Path:
    """Codex's shape, smaller: every third second from 08:00:00 on twelve rows, and twenty between.

    Each third second stands out from the empty seconds beside it, so the
    column publishes one heap a value; the twenty single seconds between
    two of them leave a census to count.
    """
    start = 8 * 3600
    cells: "list[str]" = []
    for place in range(heaps):
        at = start + 3 * place
        cells += [f"{at // 3600:02d}:{at // 60 % 60:02d}:{at % 60:02d}"] * 12
    middle = start + 3 * (heaps // 2)
    for place in range(20):
        at = middle + 3 * place + 1
        cells += [f"{at // 3600:02d}:{at // 60 % 60:02d}:{at % 60:02d}"]
    random.Random(heaps).shuffle(cells)
    document, _loaded = _described(folder, cells)
    block = _block(document)
    assert len(block["clock_heaps"]) >= heaps - 2 and block["clock_census"] != []
    return folder / "table.json"


def _comparisons(path: pathlib.Path) -> int:
    """How many times a clock ordinal is compared for equality while the loader reads one description."""
    built = contract._clock_at

    def counted(text: str, form: str) -> "tuple[int, str]":
        at, said = built(text, form)
        return _Counted(at), said

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(contract, "_clock_at", counted)
        _COMPARED[0] = 0
        contract.load_profile(str(path))
    return _COMPARED[0]


@pytest.fixture(scope="module")
def _heaped(tmp_path_factory: pytest.TempPathFactory) -> "tuple[pathlib.Path, pathlib.Path]":
    folder = tmp_path_factory.mktemp("heaped")
    return _heaped_description(folder / "small", 300), _heaped_description(folder / "large", 600)


def test_item_6_the_heaps_are_looked_up_in_work_that_grows_with_them(
    _heaped: "tuple[pathlib.Path, pathlib.Path]",
) -> None:
    """Comparisons at 600 heaps against 300: about two now, and about four at 90466b2.

    At 90466b2 every published heap, rung and boundary asked the list of
    heaps whether it was one, so the comparisons grew with the square of
    the heaps -- about 414 million at the 28,800 heaps of Codex's million
    rows. A set answers each with one.
    """
    small, large = _comparisons(_heaped[0]), _comparisons(_heaped[1])
    assert small > 0
    assert large / small < _LINEAR_AT_MOST, (small, large)


def test_item_6_red_when_the_heaps_are_a_list_again(
    _heaped: "tuple[pathlib.Path, pathlib.Path]", monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(contract, "set", list, raising=False)
    small, large = _comparisons(_heaped[0]), _comparisons(_heaped[1])
    assert large / small >= _SQUARE_AT_LEAST, (small, large)


# -- item 7: a time of another precision is not called no time -----------


def test_item_7_a_time_of_another_precision_is_not_called_no_time(tmp_path: pathlib.Path) -> None:
    """NF107 beside `14:00:00` among times to the minute says what its form does not read.

    At 90466b2 the remark said "some cells of this column hold text that
    is not a time of day", of twelve cells that are times at the second.
    """
    cells = ["14:00"] * 700 + ["15:00"] * 700 + ["14:00:00"] * 12
    random.Random(7).shuffle(cells)
    document, _loaded = _described(tmp_path, cells)
    block = _block(document)
    assert block["clock_form"] == "hh-mm" and block["clock_codes"] == [{"count": 12, "spelling": "14:00:00"}]
    said = taxonomy.rendered(taxonomy.REMARK_CLOCK_CODES_WRITTEN, (11,))
    assert said in block["remarks"]
    assert "not a time of day" not in said
    assert "not read as times of day in the form its times are written in" in said
    assert "a time written another way" in said


# -- item 8: the clock KPI says where a clock-shaped cell is no time -----


def test_item_8_the_clock_kpi_says_where_a_clock_shaped_cell_is_no_time() -> None:
    """K-S3-49 names G8.3's clock line, past which a label column's stand-in is no time.

    File 21's `labels_clock_line` writes ten `26:32` so its column stays
    labels, as G8.3 means it to; at 90466b2 the KPI's name said "every
    clock-shaped twin cell is a time" and its rule said nothing of them.
    """
    cases = json.loads(_VECTORS_21.read_text(encoding="utf-8"))["cases"]
    shaped = [
        cell
        for cell in cases["labels_clock_line"]["cells"]
        if len(cell) == 5 and cell[2] == ":" and parsing.clock_ordinal(cell, "hh-mm") is None
    ]
    assert shaped == ["26:32"] * 10
    entries = json.loads(_LEDGER.read_text(encoding="utf-8"))["entries"]
    entry = next(one for one in entries if one["id"] == "K-S3-49")
    assert "every clock-shaped twin cell is a time" not in entry["name"]
    assert "labels" in entry["name"] and "clock line" in entry["name"]
    assert "labels_clock_line" in entry["rule"] and "26:32" in entry["rule"]
    assert "the 12-hour question and the clock-or-labels question both fit is offered code too" in entry["rule"]


# -- one more, not Codex's: a SQL Server `time(7)` column -----------------
#
# Lane R2a's reach battery (its build report, item 7) wrote a SQL Server
# `time(7)` column -- every cell a time of day and seven figures of a
# fraction, `14:40:05.1234567` -- and its twin held `44:40:00.0023504`:
# no clock reader takes a fraction, so the column is free text and its
# cells are stand-ins of the form `%%:%%:%%.%%%%%%%`, which G8.3's clock
# supply did not know, so the form was filled figure by figure and 856 of
# the 1,000 cells were no time of day. The battery's own reader stopped on
# the first of them, as code reading the real column's times would.


_TIME7 = re.compile(r"\d\d:\d\d:\d\d\.\d{7}")


def _time7(rows: int, seed: int = 0) -> "list[str]":
    """A made-up `time(7)` column: a time of day and seven figures of fraction a cell, all different."""
    draw = random.Random(7 + seed)
    made: "list[str]" = []
    for _row in range(rows):
        at = draw.randrange(86400)
        made += [f"{at // 3600:02d}:{at % 3600 // 60:02d}:{at % 60:02d}.{draw.randrange(10**7):07d}"]
    return made


def _off_its_spelling(cells: "list[str]") -> "list[str]":
    """The cells that are not a time of day written `HH:MM:SS` and seven figures."""
    return [cell for cell in cells if not _TIME7.fullmatch(cell) or parsing.clock_parts(cell[:8]) is None]


def _time7_twins(
    folder: pathlib.Path, cells: "list[str]", seeds: "tuple[int, ...]"
) -> "tuple[str, list[list[str]], list[str]]":
    """The column's role, its twins at the seeds, and what validation missed on them."""
    document, loaded = _described(folder, cells)
    twins: "list[list[str]]" = []
    missed: "list[str]" = []
    for seed in seeds:
        twin, path = _twin(loaded, seed, folder)
        twins += [twin]
        missed += [f"seed {seed} {line}" for line in _missed(loaded, path)]
    return f"{_block(document)['role']}", twins, missed


def test_time7_every_twin_cell_is_a_time_in_the_columns_spelling(tmp_path: pathlib.Path) -> None:
    """The battery's own size: 1,000 rows, free text, every stand-in a time of its form.

    At cc50fd7 seed 0's twin held 856 cells that were no time of day here,
    `44:40:00.0023504` among them, where the table holds none.
    """
    role, twins, missed = _time7_twins(tmp_path / "t7", _time7(1000), (0, 1, 2))
    assert role == taxonomy.ROLE_TEXT
    for twin in twins:
        assert len(twin) == 1000 and len(set(twin)) == 1000
        assert _off_its_spelling(twin) == []
    assert missed == []


def test_time7_red_when_the_fraction_is_filled_figure_by_figure(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MUTATION: the clock supply blind to a fraction, as at cc50fd7, writes hours past 23."""
    built = generation._clock_shape
    monkeypatch.setattr(generation, "_clock_shape", lambda form: None if "." in form else built(form))
    _role, twins, _missed_now = _time7_twins(tmp_path / "t7", _time7(1000), (0,))
    assert len(_off_its_spelling(twins[0])) > 500


def test_time7_a_column_past_the_walks_bound_is_a_time_in_every_cell(tmp_path: pathlib.Path) -> None:
    """4,200 different times: the walk of the form runs past 4,096 spellings.

    A walk stops at `_STAND_IN_STEPS` spellings of one form. Bounded so,
    with the fraction filled as a clock, a twin needing more wrote the
    rest as text in no time's spelling -- 104 cells here (the mutant
    below), 5,904 of 10,000 rows and 95,904 of 100,000 -- and missed its
    own census of forms; at cc50fd7, blind to the fraction as well, 3,600
    of these 4,200 cells were no time. A clock's form written to a
    fraction of the second is walked to the end of its clock supply.
    """
    role, twins, missed = _time7_twins(tmp_path / "t7", _time7(4200, 1), (0,))
    assert role == taxonomy.ROLE_TEXT
    assert len(set(twins[0])) == 4200 and _off_its_spelling(twins[0]) == []
    assert missed == []


def test_time7_red_when_the_walk_stops_at_its_bound(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MUTATION: the fraction clock's walk bounded like every other form's."""
    monkeypatch.setattr(generation, "_fraction_clock_supply", lambda _form: 0)
    _role, twins, missed = _time7_twins(tmp_path / "t7", _time7(4200, 1), (0,))
    assert len(_off_its_spelling(twins[0])) == 4200 - generation._STAND_IN_STEPS
    assert "t:forms.published.%%:%%:%%.%%%%%%%" in missed[0]


def _time7_long_tail(rows: int) -> "list[str]":
    """Times at the second over `rows / 10` seconds from 08:00, fraction nought: labels, many held back."""
    draw = random.Random(rows)
    made: "list[str]" = []
    for _row in range(rows):
        at = 8 * 3600 + draw.randrange(rows // 10)
        made += [f"{at // 3600:02d}:{at % 3600 // 60:02d}:{at % 60:02d}.0000000"]
    return made


def _long_tail_twin(folder: pathlib.Path) -> "tuple[dict[str, typing.Any], list[str], list[str]]":
    document, loaded = _described(folder, _time7_long_tail(2000))
    twin, path = _twin(loaded, 0, folder)
    return _block(document), twin, _missed(loaded, path)


def test_time7_held_back_labels_past_the_walks_bound_are_times(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A long tail's held-back times, more than the walk's bound, every one a time.

    The label walk of G8.3 is bounded as the free text's is. Measured with
    the bound as shipped, a long tail of 100,000 rows holds back 5,863
    times: at cc50fd7 its twin wrote 5,244 cells `group-N` and 34,960
    that were no time, and missed its own census of forms; with the
    fraction filled as a clock and the walk still bounded, 7,294 `group-N`;
    now none, and nothing missed. The bound is set at 32 here, so a table
    of 2,000 rows crosses it.
    """
    monkeypatch.setattr(generation, "_STAND_IN_STEPS", 32)
    block, twin, missed = _long_tail_twin(tmp_path / "tail")
    assert block["role"] in (taxonomy.ROLE_LONG_TAIL, taxonomy.ROLE_CATEGORICAL)
    assert block["suppressed_levels"] > 32
    assert _off_its_spelling(twin) == [] and missed == []


def test_time7_red_when_the_label_walk_stops_at_its_bound(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MUTATION: the held-back labels' walk bounded like every other form's."""
    monkeypatch.setattr(generation, "_STAND_IN_STEPS", 32)
    monkeypatch.setattr(generation, "_fraction_clock_supply", lambda _form: 0)
    _block_now, twin, missed = _long_tail_twin(tmp_path / "tail")
    assert any(cell.startswith("group-") for cell in _off_its_spelling(twin))
    assert "t:forms.published.%%:%%:%%.%%%%%%%" in missed


def _tool_module(relative: str, name: str) -> types.ModuleType:
    """A committed tool, loaded from its file as a module of its own.

    Unedited, so it is loaded as the file it is -- as every test that
    asks a tool unchanged loads it -- and no string of source is run
    (`tests/test_version_reach.py` counts this loader among its thirty-one).
    """
    spec = importlib.util.spec_from_file_location(name, _HERE.parent / relative)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _oracle_module() -> types.ModuleType:
    """The generation oracle, `tools/reference/make_generation_reference_vectors.py`."""
    return _tool_module("tools/reference/make_generation_reference_vectors.py", "oracle_of_the_time7_fix")


def test_time7_the_oracle_states_the_same_supply_and_bounds() -> None:
    """No frozen case holds a fraction's form, so its rule is witnessed call by call (A-P4-59).

    The oracle's clock supply, walk bounds and stand-in test read the
    method's text, and give what the product gives: on forms written to
    a fraction, and on the forms beside them that are no clock's.
    """
    oracle = _oracle_module()
    forms = (
        "%%:%%:%%.%%%%%%%", "%:%%:%%.%%%", "%%:%%:%%.%", "%:%%:%%.%%@@", "%%:%%:%%.%%%%%% &&",
        "%%:%%", "%%:%%:%%", "%:%%@.@.", "%%:%%.%", "%%.%%", ".%%", "%%:%%:%%.", "@%%%%-%%%%",
    )
    steps = tuple(range(300)) + (4095, 4096, 4097, 86399, 86400, 86401, 10**6, 10**9)
    for form in forms:
        assert oracle.fraction_clock_supply(form) == generation._fraction_clock_supply(form), form
        assert oracle.form_walk_bounds(form) == generation._form_walk_bounds(form), form
        assert oracle.form_walk_bounds(form, True) == generation._form_walk_bounds(form, True), form
        for step in steps:
            made = generation._clock_filled_form(form, step)
            assert oracle.clock_filled_form(form, step) == made, (form, step)
            if made is not None and generation._fraction_clock_supply(form):
                assert oracle.fraction_clock(made) and oracle.usable_stand_in(made), made
    assert generation._clock_filled_form("%%:%%:%%.%%%%%%%", 0) == "00:00:00.0000000"
    supply = generation._fraction_clock_supply("%%:%%:%%.%%%%%%%")
    assert supply == 86400 * 10**7
    firsts = {generation._clock_filled_form("%%:%%:%%.%%%%%%%", step) for step in range(86400)}
    assert len(firsts) == 86400 and all(cell[8:] == ".0000000" for cell in firsts)


# -- the verification's catch: a listing tail in the order of the day ----
#
# The verification of this stream profiled 514 random clock columns, and
# the loader refused the producer's own description of 8 of them. A tail
# that lists its values listed them sorted as TEXT, which is the order of
# the day only on the two two-figure 24-hour forms: on a 12-hour clock
# `02:30:00 PM` sorts before `11:30:00 AM`, on a one-figure hour
# `12:30:00` before `9:30:00`, and on the declared half-day face `01:05`
# before `12:50`. DT3 refused each list as out of order, and generate
# told the person the file had been changed since it was written. The
# defect is landing 3b.5's own: at 110cb46 such columns were read as
# labels.

# The verification's fuzz case 126: 498 rows of a 12-hour clock at the
# second, as a second of the day and how many rows wrote it. Its high tail
# is a heap of 101 rows at 11:30 AM beside two rows at 2:30 PM.
_CASE_126 = (
    (18000, 6), (23400, 29), (25200, 1), (28800, 1), (30600, 4), (32400, 50),
    (34200, 122), (36000, 133), (37800, 42), (39600, 7), (41400, 101), (52200, 2),
)


def _case_126(spelling: "typing.Callable[[int, int, int], str]", earlier: int = 0) -> "list[str]":
    """Case 126's cells `earlier` seconds earlier, each written `spelling(hour, minute, second)`."""
    cells: "list[str]" = []
    for at, rows in _CASE_126:
        moved = at - earlier
        cells += [spelling(moved // 3600, moved // 60 % 60, moved % 60)] * rows
    random.Random(126).shuffle(cells)
    return cells


def _twelve_hour(hour: int, minute: int, second: int) -> str:
    return f"{hour % 12 or 12:02d}:{minute:02d}:{second:02d} {'AM' if hour < 12 else 'PM'}"


def _one_figure(hour: int, minute: int, second: int) -> str:
    return f"{hour}:{minute:02d}:{second:02d}"


def _two_figures(hour: int, minute: int, second: int) -> str:
    return f"{hour:02d}:{minute:02d}:{second:02d}"


def _half_day_face() -> "list[str]":
    """Hours 2 to 5 every ten minutes on ten rows, and `12:50` and `01:05` on six each below them."""
    cells: "list[str]" = []
    for minute in range(120, 360, 10):
        cells += [f"{minute // 60:02d}:{minute % 60:02d}"] * 10
    cells += ["12:50"] * 6 + ["01:05"] * 6
    random.Random(12).shuffle(cells)
    return cells


def _through_the_commands(
    folder: pathlib.Path, cells: "list[str]", capsys: "pytest.CaptureFixture[str]", *extra: str
) -> "tuple[dict[str, typing.Any], list[tuple[str, int, str]]]":
    """`synthtwin profile`, `generate` and `validate` on one column `t`, up to the first that fails.

    Returns the published block and each command run, its exit code and
    what it said.
    """
    folder.mkdir(parents=True, exist_ok=True)
    table = fixtures.write(folder, "table.csv", "\n".join(["t"] + cells) + "\n")
    description = folder / "table-profile.json"
    twin = folder / "twin" / "table-twin.csv"
    twin.parent.mkdir()
    commands = (
        ("profile", ["profile", str(table), *extra]),
        ("generate", ["generate", str(description), "--seed", "0", "--out-dir", str(twin.parent)]),
        ("validate", ["validate", str(description), "--twin", str(twin), "--out-dir", str(twin.parent)]),
    )
    ran: "list[tuple[str, int, str]]" = []
    for name, argv in commands:
        code = cli.main(argv)
        said = capsys.readouterr()
        ran += [(name, code, said.out + said.err)]
        if code != 0:
            break
    return _block(json.loads(description.read_text(encoding="utf-8"))), ran


def test_tail_order_a_listing_tail_holds_the_order_of_the_day(
    tmp_path: pathlib.Path, capsys: "pytest.CaptureFixture[str]"
) -> None:
    """Case 126 on a 12-hour clock and on a one-figure hour, and a declared half-day face: profiled, generated, validated.

    At 90466b2 and at 0138325 their tails listed `02:30:00 PM` before
    `11:30:00 AM`, `12:30:00` before `9:30:00` and `01:05` before
    `12:50`, and `synthtwin generate` stopped with exit 1. The same cells
    two hours earlier on two figures list the same values in the same
    order either way, and generated then as now.
    """
    cases = (
        ("twelve-hour", _case_126(_twelve_hour), (), "high_tail", ["11:30:00 AM", "02:30:00 PM"]),
        ("one-figure", _case_126(_one_figure, 7200), (), "high_tail", ["9:30:00", "12:30:00"]),
        ("half-day", _half_day_face(), ("--twelve-hour", "t"), "low_tail", ["12:50", "01:05"]),
        ("two-figures", _case_126(_two_figures, 7200), (), "high_tail", ["09:30:00", "12:30:00"]),
    )
    for name, cells, extra, side, listed in cases:
        block, ran = _through_the_commands(tmp_path / name, cells, capsys, *extra)
        assert [(command, code) for command, code, _said in ran] == [
            ("profile", 0), ("generate", 0), ("validate", 0),
        ], (name, ran)
        assert block["role"] == taxonomy.ROLE_CLOCK, name
        assert block[side]["values"] == listed, name


def test_tail_order_red_when_the_values_are_sorted_as_text(
    tmp_path: pathlib.Path, capsys: "pytest.CaptureFixture[str]", monkeypatch: pytest.MonkeyPatch
) -> None:
    """MUTATION: a listing tail's values sorted as text again, as at 0138325."""
    monkeypatch.setattr(taxonomy, "_listed_values", lambda _distances, texts: sorted(set(texts)))
    block, ran = _through_the_commands(tmp_path / "twelve-hour", _case_126(_twelve_hour), capsys)
    assert block["high_tail"]["values"] == ["02:30:00 PM", "11:30:00 AM"]
    assert [(command, code) for command, code, _said in ran] == [("profile", 0), ("generate", 1)]
    assert "changed since it was written" in ran[1][2]


# -- round 2 of the verification: an absence declared on a laid column ---
#
# The second verification of this stream (at d4f5ee4) declared missing the
# time a column writes for an unknown one -- `00:00`, `12:00` -- beside
# times on a five- to sixty-minute grid, and 16 of its 150 such columns
# MISSED at every seed: the twin wrote present cells on the absence. A
# census group's count was shared over runs by every step, the absent one
# too, so a run holding nothing but the absence took cells that no rank
# could move off it; and a tail drawn through its shape skipped its heaps'
# distances but not the absence's, so a draw could land on it -- `00:00`
# is the low tail's own edge. At the minute, where a heap-free tail was
# placed as G7A.4 places it, the same edge took one cell (method G7A.4b,
# steps 1 and 2, amended).
#
# The verification's five columns and one at the minute, each as a
# minute of the day and how many rows wrote it, beside the absence.
_ABSENCES: "dict[str, tuple[str, tuple[tuple[int, int], ...]]]" = {
    # A run of the body holding nothing but the absence: a 30-minute grid
    # whose `22:30` stands between the heaps at `22:00` and `23:00`...
    "slots": ("22:30", ((0, 1), (1230, 100), (1290, 6), (1320, 16), (1350, 43), (1380, 38), (1410, 23))),
    # ...a 30-minute grid whose `14:00` stands between two heaps...
    "afternoon": (
        "14:00",
        ((630, 11), (720, 4), (750, 82), (780, 336), (810, 809), (840, 811), (870, 323), (900, 50), (930, 45), (1050, 22)),
    ),
    # ...and an hourly grid whose `12:00` stands between `11:00` and `13:00`.
    "hourly": (
        "12:00",
        (
            (0, 7), (60, 7), (120, 12), (180, 5), (240, 6), (300, 4), (360, 6), (420, 8), (480, 59), (540, 71),
            (600, 308), (660, 105), (720, 279), (780, 57), (840, 10), (900, 14), (960, 6), (1020, 7), (1080, 8),
            (1140, 2), (1200, 8), (1260, 6), (1320, 3), (1380, 2),
        ),
    ),
    # Beyond a tail's boundary: `17:30` inside the high tail of a 30-minute grid...
    "evening": (
        "17:30",
        ((720, 6), (750, 12), (870, 4), (900, 15), (930, 47), (960, 37), (990, 21), (1020, 3), (1050, 60), (1110, 1),
         (1170, 3), (1200, 3)),
    ),
    # ...and `00:00`, the low tail's edge, on a ten-minute grid.
    "ten-minute": (
        "00:00",
        (
            (0, 20), (20, 1), (40, 1), (50, 1), (70, 1), (90, 1), (110, 1), (120, 1), (140, 1), (190, 2), (200, 3),
            (210, 3), (220, 1), (260, 2), (280, 1), (290, 1), (300, 2), (320, 1), (340, 3), (350, 1), (370, 20),
            (380, 2), (390, 21), (400, 18), (410, 9), (420, 8), (430, 8), (440, 14), (450, 24), (460, 8), (470, 5),
            (480, 6), (490, 17), (500, 10), (510, 8), (520, 5), (530, 7), (540, 15), (550, 2), (560, 3), (570, 21),
            (580, 2), (590, 8), (600, 5), (610, 6), (620, 6), (630, 3), (640, 22), (650, 20), (660, 5), (670, 6),
            (680, 7), (690, 2), (700, 6), (710, 18), (720, 15), (730, 2), (740, 14), (750, 4), (760, 16), (770, 14),
            (780, 3), (790, 9), (800, 13), (810, 6), (820, 21), (830, 5), (840, 3), (850, 7), (860, 4), (870, 5),
            (880, 6), (890, 5), (900, 29), (920, 1), (930, 1), (960, 1), (980, 1), (990, 1), (1010, 1), (1040, 1),
            (1060, 1), (1080, 1), (1100, 1), (1110, 1), (1120, 1), (1130, 1), (1150, 1), (1160, 1), (1200, 1),
            (1230, 1), (1240, 1), (1270, 1), (1290, 1), (1310, 1), (1340, 1), (1350, 1), (1380, 1),
        ),
    ),
}


def _minute_column(seed: int = 5) -> "list[str]":
    """277 times to the minute, nine in ten after 14:00, beside 23 `00:00` written for an unknown time."""
    draw = random.Random(seed)
    cells: "list[str]" = []
    for _row in range(277):
        cells += _minutes([draw.randrange(840, 1440) if draw.random() < 0.9 else draw.randrange(1, 1440)])
    cells += ["00:00"] * 23
    draw.shuffle(cells)
    return cells


def _absence_column(name: str) -> "tuple[list[str], str]":
    """One of the round's columns and the time it writes for an unknown one."""
    if name == "minute":
        return _minute_column(), "00:00"
    hole, pairs = _ABSENCES[name]
    cells: "list[str]" = []
    for minute, rows in pairs:
        cells += _minutes([minute]) * rows
    random.Random(len(cells)).shuffle(cells)
    return cells, hole


def _absence_twins(
    folder: pathlib.Path, name: str, seeds: "tuple[int, ...]" = (0, 1, 2)
) -> "tuple[dict[str, typing.Any], int, list[tuple[int, int, list[str]]], list[str]]":
    """One column, its absence declared, through the producer, the generator and the checker.

    Returns the published block, the table's rows on the absence, each
    seed's twin's rows on it with what the checker MISSED of that twin,
    and what it MISSED of the table itself.
    """
    cells, hole = _absence_column(name)
    document, loaded = _described(folder / name, cells, declared=(hole,))
    twins: "list[tuple[int, int, list[str]]]" = []
    for seed in seeds:
        twin, path = _twin(loaded, seed, folder / name)
        twins += [(seed, twin.count(hole), _missed(loaded, path))]
    return _block(document), cells.count(hole), twins, _missed(loaded, folder / name / "table.csv")


def test_round_2_an_absence_declared_on_a_laid_column_stays_absent(tmp_path: pathlib.Path) -> None:
    """Six columns laid on their census beside a declared absence: every twin writes it on the table's rows, nothing MISSED.

    At d4f5ee4 the twins of `slots` wrote 46 `22:30` against 43, of
    `afternoon` 829 `14:00` against 811 and of `hourly` 285 `12:00`
    against 279 -- a run holding only the absence took its share -- and
    of `evening` 61 or 62 `17:30` against 60, of `ten-minute` 21 `00:00`
    against 20 and of `minute` 24 against 23 -- a tail's draw landing on
    it -- each twin MISSING the presence counts and, beyond a tail, that
    tail's distances; at seed 2 `evening`'s draw missed the absence.
    """
    for name in tuple(_ABSENCES) + ("minute",):
        block, real, twins, table = _absence_twins(tmp_path, name)
        assert block["role"] == taxonomy.ROLE_CLOCK and block["clock_step"] is not None, name
        assert real >= 11 and table == [], (name, real, table)
        assert twins == [(seed, real, []) for seed in (0, 1, 2)], (name, real, twins)


def test_round_2_red_when_a_run_counts_its_absent_steps(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MUTATION: a run's share counted over every step, the absent one too, as at d4f5ee4."""
    built = calendar_clock.clock_body_blocks

    def every_step(parsed, tails, body, groups, heaps, form, stride, absent=()):  # type: ignore[no-untyped-def]
        return built(parsed, tails, body, groups, heaps, form, stride)

    monkeypatch.setattr(calendar_clock, "clock_body_blocks", every_step)
    for name in ("slots", "afternoon", "hourly"):
        _block_of, real, twins, _table = _absence_twins(tmp_path, name, (0,))
        assert twins[0][1] > real and twins[0][2] != [], (name, real, twins)


def test_round_2_red_when_a_tail_draws_onto_an_absence(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MUTATION: a tail drawn without skipping the absence, as at d4f5ee4 -- at the minute, placed as G7A.4 places it."""
    monkeypatch.setattr(calendar_clock, "absent_beyond", lambda *_a: [])
    for name in ("evening", "ten-minute", "minute"):
        _block_of, real, twins, _table = _absence_twins(tmp_path, name, (0,))
        assert twins[0][1] > real and twins[0][2] != [], (name, real, twins)


def _absent_only_group(document: "dict[str, typing.Any]") -> "dict[str, typing.Any]":
    """`hourly`'s description, its absent spelling moved by hand to `15:00`, the only step of a group counting 14."""
    edited = copy.deepcopy(document)
    block = edited["columns"][0]
    assert {"count": 14, "first": 90, "last": 90} in [dict(group) for group in block["clock_census"]]
    block["missing_by_source"] = {"15:00": block["missing_by_source"]["12:00"]}
    return typing.cast("dict[str, typing.Any]", edited)


def test_round_2_the_loader_refuses_a_group_with_no_step_left(tmp_path: pathlib.Path) -> None:
    """CC5 leaves out the steps the column calls absent, as the runs do, so such a group is refused at load."""
    cells, hole = _absence_column("hourly")
    document, _loaded = _described(tmp_path, cells, declared=(hole,))
    refused = _loads(tmp_path, _absent_only_group(document), "absent-only")
    assert isinstance(refused, str) and "CC5" in refused and "bin 90 to bin 90 counts 14" in refused, refused
    assert "on no spelling the table calls absent" in refused, refused


def test_round_2_red_when_the_loader_counts_absent_steps_as_room(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MUTATION: CC5 counting the absent steps as room again -- it loads, and generation stops on an internal error."""
    built = calendar_clock.clock_group_reach
    monkeypatch.setattr(
        calendar_clock, "clock_group_reach",
        lambda groups, form, stride, body, heaps, absent=(): built(groups, form, stride, body, heaps),
    )
    cells, hole = _absence_column("hourly")
    document, _loaded = _described(tmp_path, cells, declared=(hole,))
    loaded = _loads(tmp_path, _absent_only_group(document), "absent-only")
    assert isinstance(loaded, contract.Profile)
    with pytest.raises(errors.ProfileError):
        generation.generate(loaded, 0)


def test_round_2_the_oracle_lays_the_minute_column_as_the_product(tmp_path: pathlib.Path) -> None:
    """No frozen case holds a tail at the minute beside an absence, so the oracle is held to the product on one (A-P4-59).

    The oracle's content list for the `minute` column, from the opening
    words of the stream the product draws at seed 0, holds the cells the
    product's twin holds; at the minute the tail is drawn past `00:00`.
    """
    numpy = pytest.importorskip("numpy")
    oracle = _oracle_module()
    cells, hole = _absence_column("minute")
    document, loaded = _described(tmp_path, cells, declared=(hole,))
    column = dict(_block(document))
    content_words, _placement = oracle.word_budget(column, len(cells))
    stream = numpy.random.default_rng(0)
    words = stream.integers(0, 18446744073709551615, size=content_words, dtype="uint64", endpoint=True)
    column["_content_words"] = [int(word) for word in words]
    laid = oracle.clock_census_content(column)
    twin, _path = _twin(loaded, 0, tmp_path)
    present = [cell for cell in twin if cell and cell != hole]
    assert collections.Counter(laid) == collections.Counter(present)
    assert hole not in laid


def _no_room_beyond(document: "dict[str, typing.Any]") -> "dict[str, typing.Any]":
    """`hourly`'s description, its low tail drawn by hand beside a heap of 11 on `01:00` and `00:00` declared missing.

    The tail keeps 14 rows beyond `02:00`, and its heap leaves three that
    no step beyond the boundary can hold: `01:00` is the heap's and
    `00:00` the absence's.
    """
    edited = copy.deepcopy(document)
    block = edited["columns"][0]
    assert block["low_tail"]["boundary"] == "02:00" and block["low_tail"]["rows"] == 14
    block["low_tail"] = {
        "boundary": "02:00",
        "rows": 14,
        "mean_distance": 72.85714285714286,
        "rms_distance": 76.9043933353987,
        "values": None,
    }
    block["clock_heaps"] = [{"count": 11, "value": "01:00"}] + list(block["clock_heaps"])
    block["missing_by_source"] = {"00:00": block["missing_by_source"]["12:00"]}
    return typing.cast("dict[str, typing.Any]", edited)


def test_round_2_the_loader_refuses_a_drawn_tail_with_no_step_left(tmp_path: pathlib.Path) -> None:
    """CC5 asks a tail drawn through its shape for a step beyond its boundary on no heap and no absent place."""
    cells, hole = _absence_column("hourly")
    document, _loaded = _described(tmp_path, cells, declared=(hole,))
    refused = _loads(tmp_path, _no_room_beyond(document), "no-room")
    assert isinstance(refused, str) and "CC5" in refused and "the low tail draws 3 of its rows" in refused, refused


def test_round_2_red_without_the_room_beyond_a_drawn_tail(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MUTATION: no room asked beyond a drawn tail -- it loads, and its draw stands past the dial."""
    monkeypatch.setattr(contract, "_drawn_tails_have_room", lambda *_a: None)
    cells, hole = _absence_column("hourly")
    document, _loaded = _described(tmp_path, cells, declared=(hole,))
    loaded = _loads(tmp_path, _no_room_beyond(document), "no-room")
    assert isinstance(loaded, contract.Profile)
    with pytest.raises((ValueError, errors.ProfileError)):
        generation.generate(loaded, 0)


def _two_columns(seed: int = 0) -> "tuple[list[str], list[str]]":
    """Two clock columns of 300 rows on a five-minute grid beside `00:00` declared missing.

    `a` writes `00:00` for 17 unknown times; `b` never writes it, and its
    low tail is pressed against midnight, eleven rows from `00:05` to
    `00:15` beyond a boundary at `00:20`.
    """
    draw = random.Random(seed)

    def body(rows: int) -> "list[str]":
        return _minutes([draw.randrange(72, 240) * 5 for _row in range(rows)])

    b = ["00:05"] * 7 + ["00:10"] * 3 + ["00:15", "00:20"] + body(288)
    a = ["00:00"] * 17 + body(283)
    draw.shuffle(a)
    draw.shuffle(b)
    return a, b


def _two_column_twins(
    folder: pathlib.Path, seeds: "tuple[int, ...]" = (0, 1, 2)
) -> "tuple[dict[str, typing.Any], list[tuple[int, int, list[str]]], list[str]]":
    """The two columns through the producer, the generator and the checker.

    Returns the description, each seed's twin's `b` cells on `00:00` with
    what the checker MISSED of that twin, and what it MISSED of the table.
    """
    a, b = _two_columns()
    folder.mkdir(parents=True, exist_ok=True)
    table = fixtures.write(folder, "table.csv", "\n".join(["a,b"] + [f"{x},{y}" for x, y in zip(a, b)]) + "\n")
    settings = taxonomy.Settings(small_cell_floor=11, declared_missing_values=("00:00",))
    document = profile.build_document(reading.read_table(str(table), small_cell_floor=11), settings, [], [])
    loaded = contract.load_profile(str(fixtures.write_profile(folder, "table.json", document)))
    twins: "list[tuple[int, int, list[str]]]" = []
    for seed in seeds:
        text = rendering.twin_csv(generation.generate(loaded, seed))
        path = fixtures.write(folder, f"twin-{seed}.csv", text)
        rows = list(csv.reader(io.StringIO(text)))[1:]
        twins += [(seed, len([row for row in rows if row and row[1] == "00:00"]), _missed(loaded, path))]
    return document, twins, _missed(loaded, table)


def test_round_2_an_absence_another_column_publishes_stays_absent(tmp_path: pathlib.Path) -> None:
    """`b` publishes no absence, but `a` publishes `00:00`, so the checker reads a `00:00` of `b` as no value too.

    A declaration reaches the whole table, so the places a census-laid
    column keeps its cells off are those any column's absent spellings
    name in its form. Read off `b`'s own spellings alone (at d0ae8f7 and
    at d4f5ee4), `b`'s low tail drew one cell onto `00:00`, its edge, at
    every seed, and the twin MISSED `b`'s presence counts and tail.
    """
    document, twins, table = _two_column_twins(tmp_path)
    a, b = document["columns"]
    assert a["missing_by_source"] == {"00:00": 17} and b["missing_by_source"] == {}
    assert b["role"] == taxonomy.ROLE_CLOCK and b["clock_step"] == 300
    assert b["low_tail"]["boundary"] == "00:20" and b["low_tail"]["values"] is None
    assert table == [], table
    assert twins == [(seed, 0, []) for seed in (0, 1, 2)], twins


def test_round_2_red_when_a_column_reads_its_own_absences_alone(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MUTATION: the layout handed the column's own absent spellings alone, as at d0ae8f7."""
    built = generation._clock_layout
    monkeypatch.setattr(
        generation, "_clock_layout",
        lambda column, facts, floor, holes=(): built(column, facts, floor),
    )
    _document, twins, _table = _two_column_twins(tmp_path, (0,))
    assert twins[0][1] == 1 and twins[0][2] != [], twins


def test_round_2_the_tail_leak_driver_draws_its_windows_beside_the_tables_absences(tmp_path: pathlib.Path) -> None:
    """K-S3-11's driver draws a clock tail's window beside every column's absent spellings, as the checker does.

    `b` publishes no absence, but `a`'s `00:00` is no value in `b` too, so
    `b`'s low tail is drawn past `00:00` (method G7A.4b step 1) and its
    window starts 15 minutes out, not 20. The driver read `b`'s own
    spellings alone at baaf9de, so its window was not the checker's.
    """
    driver = _tool_module("tools/measurements/kpi_stage3_tail_leak.py", "kpi_stage3_tail_leak_of_the_clock_review")
    _two_column_twins(tmp_path, ())
    loaded = contract.load_profile(str(tmp_path / "table.json"))
    column = loaded.columns[1]
    facts = column.facts
    assert isinstance(facts, contract.ClockFacts)
    floor = loaded.settings.small_cell_floor
    holes = tuple(validation.settings_for(loaded).declared_missing_values)
    checker = validation._clock_tail_windows(column, facts, floor, holes)
    own = validation._clock_tail_windows(column, facts, floor)
    assert checker["low"][0][0] == 15 and own["low"][0][0] == 20, (checker["low"], own["low"])
    assert driver._tail_windows(loaded, column) == checker


def _two_hourly_columns(folder: pathlib.Path) -> "dict[str, typing.Any]":
    """`hourly` as `t` beside `u`, the same column with its `15:00` rows on `16:00`, `u`'s absent key moved by hand to `15:00`.

    Both are described by the real producer beside `12:00` declared
    missing. `u` holds no `15:00`, so its own group there counts nothing
    and its block asks no room of it; but its key now names `15:00`, the
    only step of `t`'s group of 14, and a spelling any column publishes
    absent is no value in every column.
    """
    t, hole = _absence_column("hourly")
    u = ["16:00" if cell == "15:00" else cell for cell in t]
    folder.mkdir(parents=True, exist_ok=True)
    table = fixtures.write(folder, "table.csv", "\n".join(["t,u"] + [f"{x},{y}" for x, y in zip(t, u)]) + "\n")
    settings = taxonomy.Settings(small_cell_floor=11, declared_missing_values=(hole,))
    document = profile.build_document(reading.read_table(str(table), small_cell_floor=11), settings, [], [])
    edited = copy.deepcopy(document)
    first, second = edited["columns"]
    assert first["name"] == "t" and {"count": 14, "first": 90, "last": 90} in [
        dict(group) for group in first["clock_census"]
    ]
    assert second["name"] == "u" and second["missing_by_source"] == {"12:00": 279}
    assert [group["count"] for group in second["clock_census"] if group["first"] <= 90 <= group["last"]] == [0]
    second["missing_by_source"] = {"15:00": second["missing_by_source"]["12:00"]}
    return typing.cast("dict[str, typing.Any]", edited)


def test_round_2_the_loader_asks_room_beside_every_columns_absence(tmp_path: pathlib.Path) -> None:
    """CC5 counts out the places any column's absent spellings name, read off the description itself.

    `u`'s key moved by hand to `15:00` leaves `t`'s group of 14 on `15:00`
    no step, so the two-column description is refused, naming `t`. Read
    off each column's own spellings alone (the verification of round 2,
    its mutants M7 and M7b) it loaded, and generate stopped on an
    internal error.
    """
    refused = _loads(tmp_path, _two_hourly_columns(tmp_path), "beside-another")
    assert isinstance(refused, str) and "CC5" in refused, refused
    assert "the column named 't'" in refused and "bin 90 to bin 90 counts 14" in refused, refused


def test_round_2_red_when_the_loader_reads_each_columns_own_absences_alone(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MUTATION: no spelling read off the table's blocks, each column's own alone -- it loads, and generation stops on an internal error."""
    built = contract._table_holes
    monkeypatch.setattr(
        contract, "_table_holes",
        lambda columns: () if isinstance(columns, list) and len(columns) > 1 else built(columns),
    )
    loaded = _loads(tmp_path, _two_hourly_columns(tmp_path), "beside-another")
    assert isinstance(loaded, contract.Profile)
    with pytest.raises(errors.ProfileError):
        generation.generate(loaded, 0)


def _on_the_marked_face(minute: int) -> str:
    """A minute of the day written `h:mm AM`."""
    hour = minute // 60
    return f"{hour % 12 or 12}:{minute % 60:02d} {'AM' if hour < 12 else 'PM'}"


def _marker_twins(
    folder: pathlib.Path, seeds: "tuple[int, ...]" = (0, 1, 2)
) -> "tuple[dict[str, typing.Any], int, list[tuple[int, int, list[str]]], list[str]]":
    """`ten-minute` written `h:mm AM`, its unknown time typed `12:00 am` and declared so.

    Returns the published block, the table's rows the reader counts as
    no value on `12:00 am`, each seed's twin's with what the checker
    MISSED of that twin, and what it MISSED of the table itself.
    """
    _hole, pairs = _ABSENCES["ten-minute"]
    cells: "list[str]" = []
    for minute, rows in pairs:
        cells += [_on_the_marked_face(minute)] * rows
    random.Random(len(cells)).shuffle(cells)
    cells = ["12:00 am" if cell == "12:00 AM" else cell for cell in cells]
    document, loaded = _described(folder, cells, declared=("12:00 am",))
    twins: "list[tuple[int, int, list[str]]]" = []
    for seed in seeds:
        twin, path = _twin(loaded, seed, folder)
        twins += [(seed, len([cell for cell in twin if parsing.folded(cell) == "12:00 am"]), _missed(loaded, path))]
    return _block(document), cells.count("12:00 am"), twins, _missed(loaded, folder / "table.csv")


def test_round_2_a_marker_typed_in_lower_case_names_its_absent_place(tmp_path: pathlib.Path) -> None:
    """`12:00 am` declared missing names the place the form writes `12:00 AM`: a marker's case is folded (G7A.4b step 1).

    Read in its own case alone (the verification of round 2, its mutant
    M13, as at d4f5ee4) it named no place, the low tail drew a cell onto
    it, and every twin wrote 21 such cells of 20 and MISSED the presence
    counts and the low tail.
    """
    block, real, twins, table = _marker_twins(tmp_path)
    assert block["clock_form"] == "h-mm AM-PM" and block["clock_step"] == 600, block
    assert block["missing_by_source"] == {"12:00 am": real} and real == 20 and table == [], (block, table)
    assert twins == [(seed, real, []) for seed in (0, 1, 2)], (real, twins)


def test_round_2_red_when_an_absent_spelling_is_read_in_its_own_case_alone(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MUTATION: `absent_places` reads the trimmed spelling alone -- `12:00 am` names no place, and the tail draws onto it."""

    def own_case(spellings: "tuple[str, ...] | list[str]", form: str) -> "tuple[int, ...]":
        found: "list[int]" = []
        for spelling in spellings:
            at = parsing.clock_ordinal(parsing.trimmed(spelling), form)
            if at is None or at in found:
                continue
            if parsing.folded(parsing.clock_spelling(at, form)) == parsing.folded(spelling):
                found += [at]
        return tuple(sorted(found))

    monkeypatch.setattr(calendar_clock, "absent_places", own_case)
    _block_of, real, twins, _table = _marker_twins(tmp_path, (0,))
    assert twins[0][1] > real and twins[0][2] != [], (real, twins)


# -- the verification of round 2: a present time on an absent spelling ---
#
# A column of `hh:mm` holding real times at midnight written `0:00` beside `00:00`
# written for an unknown time and declared missing. The column's reader
# reads `0:00` at the place `00:00` names, so the description publishes a
# heap and a listed low tail on `00:00`, the form's own spelling of that
# place -- and every twin wrote all 35 of those cells `00:00`, 15 of them
# present cells its own reader counts as no value (at d4f5ee4 and at
# baaf9de alike), where the table validates. The only other spelling the
# reader reads at that place is the hour's other width, so it is the one
# the table wrote, and the twin now writes it wherever the description
# stands present cells on such a place -- a heap's value, a tail's
# boundary or a listed tail value (method G7A.4).


def _at_midnight_column() -> "tuple[list[str], str]":
    """`ten-minute` beside 15 real times at midnight written `0:00`: the verification's column."""
    cells, hole = _absence_column("ten-minute")
    cells = cells + ["0:00"] * 15
    random.Random(7).shuffle(cells)
    return cells, hole


def _laid_as_before(document: "dict[str, typing.Any]") -> "dict[str, typing.Any]":
    """The description with landing 3b.5's keys emptied, so each column is laid by G7A.4 as a description written before it is."""
    edited = copy.deepcopy(document)
    for block in edited["columns"]:
        block["clock_step"] = None
        for key in ("clock_heaps", "clock_census", "clock_codes"):
            block[key] = []
    return typing.cast("dict[str, typing.Any]", edited)


def _midnight_twins(
    folder: pathlib.Path, seeds: "tuple[int, ...]" = (0, 1, 2), as_before: bool = False
) -> "tuple[dict[str, typing.Any], tuple[int, int], list[tuple[int, int, int, list[str]]], list[str]]":
    """The verification's column through the producer, the generator and the checker.

    Returns the published block, the table's `00:00` and `0:00` rows,
    each seed's twin's with what the checker MISSED of that twin, and
    what it MISSED of the table itself; `as_before` lays it by G7A.4.
    """
    cells, hole = _at_midnight_column()
    document, loaded = _described(folder, cells, declared=(hole,))
    if as_before:
        written = _loads(folder, _laid_as_before(document), "as-before")
        assert isinstance(written, contract.Profile), written
        loaded = written
    twins: "list[tuple[int, int, int, list[str]]]" = []
    for seed in seeds:
        twin, path = _twin(loaded, seed, folder)
        twins += [(seed, twin.count(hole), twin.count("0:00"), _missed(loaded, path))]
    table = _missed(loaded, folder / "table.csv")
    return _block(document), (cells.count(hole), cells.count("0:00")), twins, table


def test_round_2_a_present_time_on_an_absent_spelling_is_written_as_the_table_wrote_it(tmp_path: pathlib.Path) -> None:
    """`0:00` read at the place `00:00` names is written `0:00`: every twin holds 20 `00:00` and 15 `0:00`, and nothing is MISSED.

    At baaf9de every twin wrote 35 `00:00` and MISSED eleven checks at
    seeds 0 to 2 -- the presence counts, the heap counts, three rungs, the
    count of cells no number reads, the absence's own count and the low
    tail's boundary, rows and values.
    """
    block, real, twins, table = _midnight_twins(tmp_path)
    assert block["clock_form"] == "hh-mm" and block["clock_step"] == 600, block
    assert block["missing_by_source"] == {"00:00": 20}, block["missing_by_source"]
    assert {"count": 15, "value": "00:00"} in block["clock_heaps"], block["clock_heaps"]
    assert block["low_tail"]["values"] == ["00:00"], block["low_tail"]
    assert real == (20, 15) and table == [], (real, table)
    assert twins == [(seed, 20, 15, []) for seed in (0, 1, 2)], twins


def test_round_2_a_column_laid_as_before_writes_a_present_time_on_an_absent_spelling_as_the_table_wrote_it(
    tmp_path: pathlib.Path,
) -> None:
    """The same column laid by G7A.4, its description stripped of landing 3b.5's keys: its listed low tail writes `0:00` too.

    At baaf9de every twin wrote 35 `00:00` and MISSED twelve or thirteen
    checks at seeds 0 to 2.
    """
    _block_of, real, twins, table = _midnight_twins(tmp_path, as_before=True)
    assert real == (20, 15) and table == [], (real, table)
    assert twins == [(seed, 20, 15, []) for seed in (0, 1, 2)], twins


def _other_width_shape(name: str) -> "tuple[list[str], str, str]":
    """A column of `hh:mm` on a ten-minute grid whose present cells on an absent spelling show the other width.

    `heap`: 30 real `8:00` in the body, a heap, beside 25 `08:00`
    declared missing. `boundary`: eleven times before `07:00`, then four
    real `7:00` -- the low boundary stands on the first -- beside 14
    `07:00` declared missing. Returns the cells, the absent spelling and
    the other width's.
    """
    draw = random.Random(3)
    if name == "heap":
        cells = [cell for cell in _minutes([draw.randrange(36, 108) * 10 for _row in range(400)]) if cell != "08:00"]
        cells += ["8:00"] * 30 + ["08:00"] * 25
        hole, other = "08:00", "8:00"
    else:
        cells = _minutes([draw.randrange(30, 42) * 10 for _row in range(11)]) + ["7:00"] * 4
        cells += _minutes([draw.randrange(43, 108) * 10 for _row in range(380)]) + ["07:00"] * 14
        hole, other = "07:00", "7:00"
    draw.shuffle(cells)
    return cells, hole, other


def _other_width_twins(
    folder: pathlib.Path, name: str, seeds: "tuple[int, ...]" = (0, 1, 2)
) -> "tuple[dict[str, typing.Any], list[tuple[int, int, int, list[str]]], list[str]]":
    """One of those columns through the producer, the generator and the checker."""
    cells, hole, other = _other_width_shape(name)
    document, loaded = _described(folder / name, cells, declared=(hole,))
    twins: "list[tuple[int, int, int, list[str]]]" = []
    for seed in seeds:
        twin, path = _twin(loaded, seed, folder / name)
        twins += [(seed, twin.count(hole), twin.count(other), _missed(loaded, path))]
    return _block(document), twins, _missed(loaded, folder / name / "table.csv")


def test_round_2_a_heap_and_a_boundary_on_an_absent_spelling_are_written_as_the_table_wrote_them(
    tmp_path: pathlib.Path,
) -> None:
    """A heap of 30 `8:00` beside `08:00` declared missing, and a low boundary on `7:00` beside `07:00`, are written in their own width.

    At baaf9de the heap's twins wrote 55 `08:00` and MISSED eight checks,
    and the boundary's 15 `07:00` and MISSED six, at seeds 0 to 2. The
    boundary's three other `7:00` rows are counted in its census group
    and laid on the group's other steps, as every run's cells are.
    """
    block, twins, table = _other_width_twins(tmp_path, "heap")
    assert block["missing_by_source"] == {"08:00": 25} and {"count": 30, "value": "08:00"} in block["clock_heaps"]
    assert table == [] and twins == [(seed, 25, 30, []) for seed in (0, 1, 2)], (table, twins)
    block, twins, table = _other_width_twins(tmp_path, "boundary")
    assert block["missing_by_source"] == {"07:00": 14} and block["low_tail"]["boundary"] == "07:00", block
    assert all(heap["value"] != "07:00" for heap in block["clock_heaps"]), block["clock_heaps"]
    assert table == [] and twins == [(seed, 14, 1, []) for seed in (0, 1, 2)], (table, twins)


def test_round_2_red_when_a_present_time_on_an_absent_spelling_is_written_in_the_forms(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MUTATION: every present time written in the form's own spelling, as at baaf9de -- on either layout."""
    monkeypatch.setattr(calendar_clock, "present_spellings", lambda *_a: {})
    for as_before in (False, True):
        _block_of, _real, twins, _table = _midnight_twins(tmp_path / f"{as_before}", (0,), as_before)
        assert twins[0][1:3] == (35, 0) and twins[0][3] != [], (as_before, twins)


def _at_midnight_beside_another_column() -> "tuple[list[str], list[str]]":
    """`a` writes `00:00` for 20 unknown times on the ten-minute grid; `b` holds 15 real times at midnight written `0:00` and never `00:00`."""
    a, hole = _absence_column("ten-minute")
    b = [cell for cell in a if cell != hole] + ["0:00"] * 15 + ["06:10"] * 5
    random.Random(7).shuffle(b)
    return a, b


def _beside_another_twins(
    folder: pathlib.Path, seeds: "tuple[int, ...]" = (0, 1, 2), as_before: bool = False
) -> "tuple[dict[str, typing.Any], list[tuple[int, int, int, list[str]]], list[str]]":
    """The two columns through the producer, the generator and the checker: each seed's `b` on `00:00` and on `0:00`.

    `as_before` lays both columns by G7A.4.
    """
    a, b = _at_midnight_beside_another_column()
    folder.mkdir(parents=True, exist_ok=True)
    table = fixtures.write(folder, "table.csv", "\n".join(["a,b"] + [f"{x},{y}" for x, y in zip(a, b)]) + "\n")
    settings = taxonomy.Settings(small_cell_floor=11, declared_missing_values=("00:00",))
    document = profile.build_document(reading.read_table(str(table), small_cell_floor=11), settings, [], [])
    written = _laid_as_before(document) if as_before else document
    loaded = contract.load_profile(str(fixtures.write_profile(folder, "table.json", written)))
    twins: "list[tuple[int, int, int, list[str]]]" = []
    for seed in seeds:
        text = rendering.twin_csv(generation.generate(loaded, seed))
        path = fixtures.write(folder, f"twin-{seed}.csv", text)
        column = [row[1] for row in list(csv.reader(io.StringIO(text)))[1:] if row]
        twins += [(seed, column.count("00:00"), column.count("0:00"), _missed(loaded, path))]
    return document, twins, _missed(loaded, table)


def test_round_2_a_present_time_on_another_columns_absent_spelling_is_written_as_the_table_wrote_it(
    tmp_path: pathlib.Path,
) -> None:
    """`b` publishes no absence of its own, but `a`'s `00:00` is no value in `b` too, so `b`'s 15 times at midnight are written `0:00`.

    On its census and laid as before by G7A.4 alike; at baaf9de every
    twin wrote them `00:00` and MISSED nine of `b`'s checks at seeds 0 to
    2 on its census, and eleven laid as before.
    """
    for as_before in (False, True):
        document, twins, table = _beside_another_twins(tmp_path / f"{as_before}", as_before=as_before)
        a, b = document["columns"]
        assert a["missing_by_source"] == {"00:00": 20} and b["missing_by_source"] == {}, (a, b)
        assert b["clock_form"] == "hh-mm" and b["low_tail"]["values"] == ["00:00"], b
        assert table == [], (as_before, table)
        assert twins == [(seed, 0, 15, []) for seed in (0, 1, 2)], (as_before, twins)


def test_round_2_red_when_a_present_time_is_spelled_beside_the_columns_own_absences_alone(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MUTATION: the twin handed each column's own absent spellings alone -- `b`'s times at midnight are written `00:00` again, on either layout."""
    monkeypatch.setattr(generation, "_all_holes_of", lambda plan: generation._hole_spellings(plan.column))
    for as_before in (False, True):
        _document, twins, _table = _beside_another_twins(tmp_path / f"{as_before}", (0,), as_before)
        assert twins[0][1:3] == (15, 0) and twins[0][3] != [], (as_before, twins)


def test_round_2_the_oracle_writes_a_present_time_on_an_absent_spelling_as_the_product(tmp_path: pathlib.Path) -> None:
    """No frozen case holds a present time on an absent spelling, so the oracle is held to the product on five columns (A-P4-59).

    The oracle's content list, from the opening words of the stream the
    product draws at seed 0, holds the cells the product's twin holds
    beside its absent ones: the verification's column on its census and
    laid as before by G7A.4, 15 `0:00` each; the heap of `8:00` and the
    boundary on `7:00`, on their census; and round 2's `minute` column
    laid as before, whose G7A.4 draw -- skipping no absent place -- lands
    one cell on `00:00`, a place its description stands nothing present
    on, so both write that cell `00:00`.
    """
    numpy = pytest.importorskip("numpy")
    oracle = _oracle_module()
    cells, hole = _at_midnight_column()
    shapes = [("at-midnight", cells, hole, "0:00", False, (0, 15)), ("at-midnight-before", cells, hole, "0:00", True, (0, 15))]
    for name, (on, off) in (("heap", (0, 30)), ("boundary", (0, 1))):
        cells, hole, other = _other_width_shape(name)
        shapes += [(name, cells, hole, other, False, (on, off))]
    cells, hole = _absence_column("minute")
    shapes += [("minute-before", cells, hole, "0:00", True, (1, 0))]
    for name, cells, hole, other, as_before, counts in shapes:
        folder = tmp_path / name
        document, loaded = _described(folder, cells, declared=(hole,))
        if as_before:
            document = _laid_as_before(document)
            written_before = _loads(folder, document, "as-before")
            assert isinstance(written_before, contract.Profile), written_before
            loaded = written_before
        column = dict(_block(document))
        content_words, _placement = oracle.word_budget(column, len(cells))
        stream = numpy.random.default_rng(0)
        words = stream.integers(0, 18446744073709551615, size=content_words, dtype="uint64", endpoint=True)
        column["_content_words"] = [int(word) for word in words]
        laid = oracle._clock_content(column)
        twin, _path = _twin(loaded, 0, folder)
        written = collections.Counter(cell for cell in twin if cell)
        written[hole] -= column["missing_by_source"][hole]
        assert collections.Counter(laid) == +written, name
        assert (laid.count(hole), laid.count(other)) == counts, (name, laid.count(hole), laid.count(other))
