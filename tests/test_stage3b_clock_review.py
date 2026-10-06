"""The clock census's one review (stage 3b landing 3b.5, lane C1, plan P4-D373): each item it raised, pinned.

Codex read landing 3b.5 at 90466b2 and raised eight items, each fixed in
this stream and none sent back (the owner, 2026-09-28); the items fixed
so far stand below. Each clause below
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
  (mutant: asked only where heaps hold the body, as before).
"""

from __future__ import annotations

import collections
import csv
import io
import json
import pathlib
import random
import typing

import pytest

import fixtures

from synthtwin import (
    asking,
    calendar_clock,
    contract,
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
    blocks = calendar_clock.clock_body_blocks(
        parsed, (low["rows"], high["rows"]), body, groups, heaps, form, stride  # type: ignore[arg-type]
    )
    assert blocks is not None
    absent = tuple(column.get("missing_by_source") or {})
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
