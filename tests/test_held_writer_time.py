"""The held writer's time: the layout pass ends (plan P4-D490, lane HB3-b part a; ledger K-HZ-40).

THE DEFECT. A column of record numbers -- or a label column held as one,
while its Safe Harbor question is open or after `yes` -- whose first
answer leaves a published layout short is laid out again over packings
that settle every group's layout (`generation._layout_packed`, plan
P4-D182), and the allocator it asks, the walk of `_allotted_over`, has
no ceiling by design. On a column of many values held by similar, spread
numbers of rows the question is a partition of the repeat counts into
the layout counts and the walk grows exponentially: 120 made-up exam
names drawn on 154 to 174 rows each at 20,000 rows, held unanswered,
passed 82,531 walk steps and 90 CPU seconds without an answer, and
`synthtwin generate` did not end.

THE RULE. The layout pass climbs its rungs under ONE meter per column
(`generation._layout_meter`, `_layout_allotted`): the walk as it is,
within `_LAYOUT_WALK_STEPS` steps and `_LAYOUT_WALK_WORK` units of work
over every question and look of every reading of the column, its own
answer byte for byte; past them the exact re-packing allocator where
one margin binds (`_layout_repacked`), its work counted on the same
meter; else the nearest assignment the allocator held, laid out where it
stands nearer the census than the first layout, and every layout left
short filed with its cause (`_layout_filed`, `_layout_causes`).

THE CHECKS, each red on its mutant (LANE I4r RULINGS 1 (4)):

- THE EQUALITY CHECK: generated packing questions small enough for the
  walk (`held_writer_tables.allocation_question`) give the metered
  allocator's answer and the walk's alike wherever the walk ends inside
  the meter, and past it an exact answer by the independent recount
  (`met_exactly`), or the nearest one with every permission kept, or
  none; a metered walk that passes its meter is a failure, never a hung
  case;
- THE RE-PACKING CHECK: generated questions of the layout pass's own
  shape past the walk (`layout_question`, up to 200,000 rows): every
  answer exact where the allocator says so, the nearest kept to every
  permission where it does not;
- THE INVARIANT CHECK: generated columns of record numbers
  (`held_column`) and held label columns (`held_label_rows`, the Safe
  Harbor question open or answered `yes`) described and generated
  through the product with the meter as shipped, with none and with a
  far larger one: every published layout at its count or filed, the
  repeats, the counts of different values and the lengths held, no twin
  cell equal to a value 1 to 10 rows hold, and the shipped meter's twin
  the walk's own wherever the walk ends inside it (the driver runs the
  same check over more columns);
- ONE METER A COLUMN at the product level: every step of every question
  and every reading of one column within the meter;
- rung 2's work one budget a column, a column that stopped short asking
  it no more; the rare exam column's own walk kept inside the meter;
- the cliff's own question answered inside the meter and exactly; the
  nearest assignment of the third rung written where it is nearer; the
  meter at least twice the census's largest walk; the stand-ins' memory
  changing no stand-in, pinned to the base's 900 spellings;
- ONE 20,000-row case: the exam column held unanswered through the
  commands a person types, generated in under 60 CPU seconds, validated
  with nothing missed, no twin cell equal to a real one.
"""

from __future__ import annotations

import contextlib
import csv
import hashlib
import inspect
import io
import json
import math
import pathlib
import random
import subprocess
import sys
import textwrap
import time

import pytest

import held_writer_tables as tables
import kpi_rules
from synthtwin import cli, contract, generation, parsing, reading, taxonomy
from synthtwin import profile as producer
from tests import fixtures

# The sizes of the generated checks in this file; the driver
# (tools/measurements/kpi_held_writer_time.py, K-HZ-40) runs them larger.
EQUALITY_QUESTIONS = 1500
REPACKING_QUESTIONS = 500
COLUMNS = 10
LABEL_COLUMNS = 3
# THE METER THE EQUALITY CHECK READS THE WALK UNDER. The check is of the
# metered walk itself -- its answer the walk's wherever the walk ends
# inside the meter, an exact or nearest answer past it -- which holds for
# every count of steps; a meter of this many keeps the questions inside
# the gate file's time, and the meter as shipped is read on the columns.
EQUALITY_METER = 200
# THE STEPS THE CLIFF'S QUESTION IS READ UNDER: its claims -- the walk does
# not end inside them, the pass does, exactly -- hold for any meter, and a
# small one keeps the case's walks short (lane HB3-b's statistics check).
CLIFF_METER = 200
# How many steps the walk is let run on the cliff's question: more than
# that meter, so passing them without an answer shows the pass would not
# have ended inside the meter without it.
CLIFF_STEPS = 1000
# THE INVARIANT CHECK'S "NO CEILING" IS A STATED COUNT TOO. The walk is
# let run this many steps for the column, with no bound on its work, so
# wherever it ends inside the shipped meter the comparison is made, and a
# generated column whose walk would not end is answered past it, never
# left walking.
CEILING_STEPS = 20000
# THE CENSUS'S LARGEST RECORDED WALK (lane HB3-b's step 0, wave6
# census-zoo.jsonl): a held column of patients' names in the zoo at
# 20,000 rows walks 302 steps in the layout pass; no recorded column
# walks more, so a meter of at least twice it moves none.
CENSUS_MOST = 302
# THE BASE'S STAND-INS (099671f1, lane HB3-b's skeptic 1): the sha256 of
# the 900 spellings `_layout_stand_in` gives for the three censuses of
# `_STAND_IN_CENSUSES`, 300 calls each.
STAND_INS_BASE = "edaadc5082ccff7023a4526164a7304dd0e5cb0880c2d38614889cfa158bb7cd"


class _Past(Exception):
    """The walk took more steps than a case allows it."""


def _walk_steps(monkeypatch: pytest.MonkeyPatch, most: int) -> "list[int]":
    """Count the walks' steps -- calls of `_cell_next` and of the metered `_layout_next` -- stopping them past ``most``."""
    counter = [0]
    stepped = generation._cell_next
    metered = generation._layout_next

    def counted(*given):  # type: ignore[no-untyped-def]
        counter[0] += 1
        if counter[0] > most:
            raise _Past()
        return stepped(*given)

    def counted_metered(*given):  # type: ignore[no-untyped-def]
        counter[0] += 1
        if counter[0] > most:
            raise _Past()
        return metered(*given)

    monkeypatch.setattr(generation, "_cell_next", counted)
    monkeypatch.setattr(generation, "_layout_next", counted_metered)
    return counter


def _meter(steps: int, groups: int) -> "list[int]":
    """A column's meter with ``steps`` walk steps, the shipped work and the shipped re-packing work for ``groups`` groups."""
    meter = generation._layout_meter(groups)
    meter[0] = steps
    return meter


def _stopped_on_work(meter: "list[int]") -> bool:
    """Whether a column's pass went past its walk because the walk's work ran out with steps left (LANE HB3-b RULINGS 5 (2))."""
    return meter[1] == 1 and meter[0] > 0 and meter[2] <= 0


def _equality_failures(
    monkeypatch: pytest.MonkeyPatch, budget: int, questions: int = EQUALITY_QUESTIONS
) -> "tuple[list[str], dict[str, int]]":
    """The equality check over every generated question: what fails, and what was seen."""
    counter = _walk_steps(monkeypatch, budget)
    draw = random.Random(20261111)
    seen = {"within": 0, "past": 0, "past_exact": 0, "past_nearest": 0, "one_margin_past": 0}
    failures: "list[str]" = []
    for number in range(questions):
        groups, margins, allowed, shaped = tables.allocation_question(draw)
        counter[0] = 0
        try:
            walked = generation._allotted_over(groups, margins, allowed)
            ended = True
        except _Past:
            walked = None
            ended = False
        # THE METERED WALK MAY TAKE ITS METER'S STEPS AND NO MORE: past
        # twice them and one it is stopped and counted as a failure, so a
        # meter that never counts down fails here in a stated number of
        # steps rather than hanging the case.
        counter[0] = -(budget + 1)
        meter = _meter(budget, len(groups))
        try:
            metered = generation._layout_allotted(groups, margins, allowed, meter)
        except _Past:
            failures += [f"question {number}: the metered walk passed its meter"]
            continue
        if not meter[1]:
            seen["within"] += 1
            if not ended or metered != walked:
                failures += [f"question {number}: the metered answer is not the walk's"]
            continue
        if ended and meter[2] > 0:
            failures += [f"question {number}: the metered walk stopped where the walk ends"]
        seen["past"] += 1
        seen["one_margin_past"] += int(shaped)
        if metered is None:
            continue
        if not meter[4]:
            seen["past_exact"] += 1
            if not tables.met_exactly(groups, margins, allowed, metered):
                failures += [f"question {number}: an exact answer past the meter misses a count or a permission"]
        else:
            seen["past_nearest"] += 1
            if tables.off_by(groups, margins, allowed, metered) < 0:
                failures += [f"question {number}: the nearest answer breaks a permission"]
    return failures, seen


def test_the_metered_walk_answers_as_the_walk_answers(monkeypatch: pytest.MonkeyPatch) -> None:
    """Rung 1 is the walk's own answer inside the meter; past it, an exact answer, the nearest one, or none.

    Mutants: a meter that never counts down, a meter that lets the walk
    stop early, or a rung 2 that calls an inexact answer exact
    (`test_each_mutant_turns_a_check_red`).
    """
    failures, seen = _equality_failures(monkeypatch, EQUALITY_METER)
    assert not failures, failures[:5]
    assert seen["within"] >= 800 and seen["past"] >= 10 and seen["past_exact"] >= 1, seen


def _repacking_failures(questions: int = REPACKING_QUESTIONS) -> "tuple[list[str], dict[str, int]]":
    """The re-packing check over generated questions of the layout pass's shape, the walk skipped."""
    draw = random.Random(20261112)
    seen = {"answered": 0, "exact": 0, "unanswerable": 0, "nearest": 0, "nearest_nearer": 0}
    failures: "list[str]" = []
    for number in range(questions):
        groups, margins, allowed, answered = tables.layout_question(draw, draw.choice((20000, 200000)))
        meter = _meter(0, len(groups))
        chosen = generation._layout_allotted(groups, margins, allowed, meter)
        seen["answered"] += int(answered)
        seen["unanswerable"] += int(not answered)
        if chosen is None:
            continue
        if not meter[4]:
            if not tables.met_exactly(groups, margins, allowed, chosen):
                failures += [f"question {number}: the re-packing misses a count or a permission"]
            elif answered:
                seen["exact"] += 1
            continue
        seen["nearest"] += 1
        off = tables.off_by(groups, margins, allowed, chosen)
        if off <= 0:
            failures += [f"question {number}: the nearest answer breaks a permission or is called inexact while exact"]
        started = _start_off(groups, margins, allowed)
        if 0 <= started and off <= started:
            seen["nearest_nearer"] += 1
        elif started >= 0:
            failures += [f"question {number}: the nearest answer stands farther than the allocator's start"]
    return failures, seen


def _start_off(groups, margins, allowed) -> int:  # type: ignore[no-untyped-def]
    """How far the re-packing allocator's first start stands from the counts, before any re-packing; -1 where none."""
    quotas = [quota for quota in margins[-1][0] if quota > 0]
    cells = [cell for cell in range(len(margins[0][1])) if all(m[0][m[1][cell]] > 0 for m in margins)]
    if len(cells) != len(quotas):
        return -1
    opens = [sum(1 << index for index in range(len(cells)) if (allowed[place] >> cells[index]) & 1) for place in range(len(groups))]
    where, _read = generation._repack_start(list(groups), quotas, opens, True)
    if where is None:
        return -1
    return tables.off_by(groups, margins, allowed, [cells[index] for index in where])


def test_the_repacking_meets_every_count_or_answers_nearest() -> None:
    """Rung 2's answer meets every count of every margin and every permission where it says exact; else the nearest.

    It is also measured for how often it answers exactly: on questions
    drawn with an answer it found an exact one on most (the share is
    K-HZ-40's); its nearest answer never stands farther than its start.
    """
    failures, seen = _repacking_failures()
    assert not failures, failures[:5]
    assert seen["exact"] >= 0.8 * seen["answered"] and seen["nearest"] >= 1, seen


def test_the_cliff_question_is_answered_inside_the_meter(monkeypatch: pytest.MonkeyPatch) -> None:
    """The cliff's own question: the walk passes its steps; the pass ends inside its meter, exactly.

    Mutant: the meter removed (`test_each_mutant_turns_a_check_red`).
    """
    monkeypatch.setattr(generation, "_LAYOUT_WALK_STEPS", CLIFF_METER)
    groups, margins, allowed = tables.cliff_question()
    counter = _walk_steps(monkeypatch, CLIFF_STEPS)
    with pytest.raises(_Past):
        generation._allotted_over(groups, margins, allowed)
    counter[0] = -CLIFF_STEPS
    meter = generation._layout_meter(len(groups))
    chosen = generation._layout_allotted(groups, margins, allowed, meter)
    assert counter[0] + CLIFF_STEPS <= CLIFF_METER
    assert chosen is not None and tables.met_exactly(groups, margins, allowed, chosen)
    assert meter[0] == 0 and meter[1] == 1 and meter[4] == 0


def test_the_meter_keeps_the_rare_column_s_own_walk() -> None:
    """The walk packs the rare exam column's question exactly inside the shipped meter (LANE HB3-b RULINGS 4 (1)).

    6,514 steps and 228,333 units of work, the walk's own answer, which
    the build's 604 steps did not reach (13 of its 14 layouts were then
    filed short). Mutant: a meter of 604 steps
    (`test_each_mutant_turns_a_check_red`).
    """
    groups, margins, allowed = tables.rare_question()
    meter = generation._layout_meter(len(groups))
    ended, chosen = generation._layout_walked(groups, margins, allowed, meter)
    assert ended and chosen is not None and tables.met_exactly(groups, margins, allowed, chosen)
    assert generation._LAYOUT_WALK_STEPS - meter[0] == 6514 and generation._LAYOUT_WALK_WORK - meter[2] == 228333


def test_the_meter_covers_the_census() -> None:
    """The shipped meter is at least twice the largest walk the census recorded, so no recorded column moves.

    Mutant: a meter below it (`test_each_mutant_turns_a_check_red`).
    """
    assert generation._LAYOUT_WALK_STEPS >= 2 * CENSUS_MOST
    assert generation._layout_meter(10)[:3] == [generation._LAYOUT_WALK_STEPS, 0, generation._LAYOUT_WALK_WORK]
    assert generation._layout_meter(10)[3] == generation._REPACK_WORK + 10 * generation._REPACK_WORK_A_GROUP


def _described(folder: pathlib.Path, cells: "list[str]") -> "tuple[contract.Profile, contract.ColumnBlock]":
    """One column of record numbers, declared, described by the producer as `synthtwin profile` would."""
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "real.csv"
    table.write_text(fixtures.rows_to_csv(["value"], [[cell] for cell in cells]), encoding="utf-8", newline="")
    settings = taxonomy.Settings()
    read = reading.read_table(str(table), "auto", small_cell_floor=settings.small_cell_floor)
    document = producer.build_document(read, settings, ["value"])
    fixtures.write_profile(folder, "real-profile.json", document)
    described = contract.load_profile(str(folder / "real-profile.json"))
    return described, [column for column in described.columns if column.name == "value"][0]


def _quietly(arguments: "list[str]") -> int:
    """One command a person types, its screen kept off the test's (the table floor off for the small tables)."""
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return cli.main(arguments, small_tables_refused=False)


def _held_label(
    folder: pathlib.Path, rows: "list[list[str]]", answer: str
) -> "tuple[contract.Profile, contract.ColumnBlock | None]":
    """One table through `synthtwin profile`: the person column answered `identifier`, the label column's question left open or answered."""
    folder.mkdir(parents=True, exist_ok=True)
    source = folder / "t.csv"
    tables.write_csv(source, ["person_id", "value", "score"], rows)
    out = ["--out-dir", str(folder), "--replace"]
    assert _quietly(["profile", str(source), *out]) == 0
    questions = folder / "t-questions.json"
    for column, given in (("person_id", "identifier"), ("value", answer)):
        if not given or not questions.exists():
            continue
        document = json.loads(questions.read_text(encoding="utf-8"))
        changed = False
        for entry in document.get("asked", []):
            if entry.get("column") == column and not entry.get("your_answer"):
                entry["your_answer"] = given
                changed = True
        if changed:
            questions.write_text(json.dumps(document), encoding="utf-8", newline="\n")
            assert _quietly(["profile", str(source), *out, "--answers", str(questions)]) == 0
    described = contract.load_profile(str(folder / "t-profile.json"))
    block = [column for column in described.columns if column.name == "value"][0]
    return described, (block if block.role == "identifier" else None)


def _twin_column(described: contract.Profile) -> "tuple[list[str], dict[str, str]]":
    """The twin's cells of the column and its deviations, fact to sentence."""
    twin = generation.generate(described, 0)
    place = [column.name for column in described.columns].index("value")
    filed = {note.fact: note.note for note in twin.outcomes[place].deviations}
    return list(twin.columns[place]), filed


def _invariant_failures(
    monkeypatch: pytest.MonkeyPatch, folder: pathlib.Path, columns: int, labels: int = 0
) -> "tuple[list[str], dict[str, int]]":
    """The invariant check over generated columns and held label columns, at the meter as shipped, at none and at `CEILING_STEPS`."""
    draw = random.Random(20261113)
    labelled = random.Random(20261114)
    shipped = generation._LAYOUT_WALK_STEPS
    work = generation._LAYOUT_WALK_WORK
    made: "list[list[int]]" = []
    making = generation._layout_meter

    def kept_meter(*given: int) -> "list[int]":
        meter = making(*given)
        made.append(meter)
        return meter

    monkeypatch.setattr(generation, "_layout_meter", kept_meter)
    failures: "list[str]" = []
    seen = {"columns": 0, "labels": 0, "stopped": 0, "walk_inside": 0}
    for number in range(columns + labels):
        if number < columns:
            family, cells = tables.held_column(draw)
            described, block = _described(folder / f"c{number}", cells)
            if block.role != "identifier":
                continue
            seen["columns"] += 1
        else:
            family, answer, rows = tables.held_label_rows(labelled)
            family = f"held label, {family}, {answer or 'unanswered'}"
            cells = [row[1] for row in rows]
            described, found = _held_label(folder / f"c{number}", rows, answer)
            if found is None:
                failures += [f"column {number} ({family}): the label column is not held"]
                continue
            block = found
            seen["labels"] += 1
        twins: "dict[str, list[str]]" = {}
        for name, steps, budget in (("shipped", shipped, work), ("none", 0, work), ("ceiling", CEILING_STEPS, 10 ** 12)):
            monkeypatch.setattr(generation, "_LAYOUT_WALK_STEPS", steps)
            monkeypatch.setattr(generation, "_LAYOUT_WALK_WORK", budget)
            made.clear()
            twin, filed = _twin_column(described)
            twins[name] = twin
            if name == "none" and any(meter[1] for meter in made):
                seen["stopped"] += 1
            if name == "ceiling":
                used = max([CEILING_STEPS - meter[0] for meter in made] or [0])
                spent = max([10 ** 12 - meter[2] for meter in made] or [0])
                if used <= shipped and spent <= work:
                    seen["walk_inside"] += 1
                    if twins["shipped"] != twin:
                        failures += [f"column {number} ({family}): the shipped meter moved a twin the walk ends"]
            for miss in tables.column_misses(cells, twin, block, filed):
                failures += [f"column {number} ({family}), meter {name}: {miss}"]
    monkeypatch.setattr(generation, "_LAYOUT_WALK_STEPS", shipped)
    monkeypatch.setattr(generation, "_LAYOUT_WALK_WORK", work)
    return failures, seen


def test_every_generated_column_holds_its_counts(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path) -> None:
    """Every generated column's twin holds what it publishes, or files the layout it leaves short.

    Mutant: rung 3's filing removed (`test_each_mutant_turns_a_check_red`).
    """
    failures, seen = _invariant_failures(monkeypatch, tmp_path, COLUMNS, LABEL_COLUMNS)
    assert not failures, failures[:5]
    assert seen["columns"] >= COLUMNS // 2 and seen["labels"] == LABEL_COLUMNS, seen
    assert seen["walk_inside"] >= COLUMNS // 2 and seen["stopped"] >= 1, seen


def _filing_cells() -> "list[str]":
    """A column whose first answer leaves layouts short: 60 word values of one layout beside 60 of another."""
    cells: "list[str]" = []
    for index in range(60):
        cells += [f"AB{index:02d} RUN"] * (20 + index % 7)
        cells += [f"CD{index:02d} PRESS"] * (25 + index % 5)
    return cells


def _column_steps(monkeypatch: pytest.MonkeyPatch, folder: pathlib.Path, readings: int) -> int:
    """The walk's steps over one column's generation, every question and every reading together.

    The filing column, its pass held past its walk (a small meter, and a
    second rung that answers nothing); where ``readings`` is above nought
    the published reading is recounted as missed and the column is offered
    that many other readings (plan P4-D298), each of which reaches the
    layout pass, so the meter is read across readings as the product's
    own loop (`_identifier_cells`) hands it on.
    """
    described, block = _described(folder, _filing_cells())
    steps = [0]
    metered = generation._layout_next

    def counted(*given):  # type: ignore[no-untyped-def]
        steps[0] += 1
        return metered(*given)

    monkeypatch.setattr(generation, "_layout_next", counted)
    monkeypatch.setattr(generation, "_layout_repacked", lambda *given: (None, False))
    if readings:
        monkeypatch.setattr(generation, "_reading_missed", lambda *given: True)
        monkeypatch.setattr(generation, "_identifier_readings", lambda column, *given: [column] * readings)
    _twin_column(described)
    return steps[0]


COLUMN_METER = 40


def test_one_meter_holds_every_question_and_reading_of_a_column(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path
) -> None:
    """At the product level, the walk's steps over a whole column stay within ONE meter (lane HB3-b's skeptic 1, item 3).

    Counted over `generate` on one column: every question of its pass and
    every reading its loop builds share the column's meter. Mutants: the
    steps given back before every question, before every reading, and a
    fresh meter for every reading -- each walks past the meter.
    """
    monkeypatch.setattr(generation, "_LAYOUT_WALK_STEPS", COLUMN_METER)
    with monkeypatch.context() as patched:
        assert _column_steps(patched, tmp_path / "one", 0) <= COLUMN_METER
    with monkeypatch.context() as patched:
        assert _column_steps(patched, tmp_path / "readings", 3) <= COLUMN_METER
    for mutant in ("question", "reading", "fresh"):
        with monkeypatch.context() as patched:
            _meter_mutant(patched, mutant)
            assert _column_steps(patched, tmp_path / mutant, 3) > COLUMN_METER, mutant


def _meter_mutant(patched: pytest.MonkeyPatch, mutant: str) -> None:
    """The meter's three defects, made in the product for the length of a check."""
    if mutant == "question":
        allotted = generation._layout_allotted

        def per_question(groups, margins, allowed, meter):  # type: ignore[no-untyped-def]
            meter[0] = generation._LAYOUT_WALK_STEPS
            return allotted(groups, margins, allowed, meter)

        patched.setattr(generation, "_layout_allotted", per_question)
        return
    as_read = generation._identifier_cells_as_read

    def per_reading(column, groups, holes=(), floor=parsing.DEFAULT_SMALL_CELL_FLOOR, meter=None):  # type: ignore[no-untyped-def]
        if mutant == "fresh" or meter is None:
            meter = generation._layout_meter(len(groups))
        else:
            meter[0] = generation._LAYOUT_WALK_STEPS
        return as_read(column, groups, holes, floor, meter)

    patched.setattr(generation, "_identifier_cells_as_read", per_reading)


def test_the_nearest_assignment_is_written_where_it_is_nearer(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path
) -> None:
    """Rung 3 writes the nearest assignment rung 2 held, not the layout-blind first answer (LANE HB3-b RULINGS 4 (1)).

    A column of 60 made-up exam names drawn on 3,000 rows in 26 layouts,
    declared, its pass sent past its walk: no pair or three of its counts
    re-packs, so rung 2 stops short, and the twin written from its
    nearest assignment stands nearer the published census than the first
    answer does, each layout it leaves short filed with its cause.
    Mutant: rung 3 as the first answer (the nearest assignment dropped)
    stands farther and leaves more layouts short.
    """
    monkeypatch.setattr(generation, "_LAYOUT_WALK_STEPS", 0)
    _header, rows = tables.wide_exam_rows(3000, 60, "drawn")
    described, block = _described(tmp_path / "near", [row[1] for row in rows])
    twin, filed = _twin_column(described)
    near = generation._layout_gap(block, twin, 1)
    short = [fact for fact in filed if fact[: len("layout_forms.")] == "layout_forms."]
    assert short and all(filed[fact] == generation._LAYOUT_PASS_STOPPED for fact in short)
    with monkeypatch.context() as patched:
        repacked = generation._layout_repacked

        def first_answer(*given):  # type: ignore[no-untyped-def]
            chosen, exact = repacked(*given)
            return (chosen, True) if exact else (None, False)

        patched.setattr(generation, "_layout_repacked", first_answer)
        twin_first, filed_first = _twin_column(described)
    far = generation._layout_gap(block, twin_first, 1)
    short_first = [fact for fact in filed_first if fact[: len("layout_forms.")] == "layout_forms."]
    assert 0 < near < far and len(short) < len(short_first), (near, far, len(short), len(short_first))


_STAND_IN_CENSUSES = (
    ({"@@-@%%%": 400, "@@-%%%%": 390, "(withheld)": 10}, {"@@-@%%%": "ST", "@@-%%%%": "XY"}, 7),
    ({"@@%%%%": 300, "@%%%%%": 300, "%%%%@@": 190, "(withheld)": 10}, {}, 6),
    ({"@@&&-%%": 500, "@&&&-%%": 290, "(withheld)": 10}, {}, 7),
)


def _stand_ins(remembered: bool) -> "list[str | None]":
    """The 900 stand-ins of `_STAND_IN_CENSUSES`, 300 a census, with the lay-out's memories or made afresh each call."""
    made: "list[str | None]" = []
    for forms, prefixes, width in _STAND_IN_CENSUSES:
        facts = generation._templated_facts(contract.IdentifierFacts(
            min_length=width, max_length=width, all_whole_numbers=False, n_all_digits=0,
            n_code_alphabet=800, n_distinct_by_occurrences={"1": 800},
            layout_forms=forms, layout_prefixes=prefixes,
        ))
        plain = generation._layout_convention(facts)
        bases = generation._layout_stand_in_bases(facts)
        state: "tuple[dict, dict, dict, dict, dict, dict]" = ({}, {}, {}, {}, {}, {})
        real = generation._stand_in_real(facts, plain)
        for _each in range(300):
            if remembered:
                made += [generation._layout_stand_in(
                    generation._CLASS_TEXT, generation._BAND_CODE, (width, width), plain, facts, bases,
                    state[0], state[1], state[2], state[3], (), real, state[4], state[5],
                )]
            else:
                made += [generation._layout_stand_in(
                    generation._CLASS_TEXT, generation._BAND_CODE, (width, width), plain, facts, bases,
                    state[0], state[1], state[2], state[3],
                )]
    return made


def test_the_stand_ins_memory_changes_no_stand_in() -> None:
    """A lay-out's stand-ins with the census read once and the mixes remembered are the base's, spelling for spelling.

    Every call writes a stand-in, and the 900 are those the base wrote
    (`STAND_INS_BASE`), with the memories and without. Mutants: a mix
    remembered by its base alone, a refusal remembered by its base
    (`test_each_mutant_turns_a_check_red`).
    """
    for remembered in (True, False):
        made = _stand_ins(remembered)
        assert None not in made
        assert made[:3] == ["ST-X60Q", "ST-3J01", "ST-XY9P"]
        assert hashlib.sha256(repr(made).encode()).hexdigest() == STAND_INS_BASE


def _one_margin(
    groups: "tuple[int, ...]", quotas: "list[int]"
) -> "tuple[tuple[int, ...], list[tuple[list[int], list[int]]], list[int]]":
    """A question of the layout pass's shape: one count of text and one of the band beside ``quotas`` as the layouts, every group free to take every layout."""
    _cells, part_of = tables.grid([4, 3, len(quotas)])
    total = sum(groups)
    margins = [([0, 0, 0, total], part_of[0]), ([0, 0, total], part_of[1]), (list(quotas), part_of[2])]
    mask = 0
    for cell in range(len(part_of[0])):
        if part_of[0][cell] == 3 and part_of[1][cell] == 2 and quotas[part_of[2][cell]] > 0:
            mask |= 1 << cell
    return groups, margins, [mask] * len(groups)


def _starts_alone(
    question: "tuple[tuple[int, ...], list[tuple[list[int], list[int]]], list[int]]"
) -> "tuple[int, int]":
    """How far each start of rung 2 alone ends from the counts, re-packings included: the largest groups first, then the slicing."""
    groups, margins, _allowed = question
    sizes, quotas = list(groups), [quota for quota in margins[2][0] if quota > 0]
    opens = [(1 << len(quotas)) - 1] * len(groups)
    _largest, largest_off = generation._repacked(sizes, quotas, opens, False, generation._layout_meter(len(groups)))
    _sliced, sliced_off = generation._repacked(sizes, quotas, opens, True, generation._layout_meter(len(groups)))
    return largest_off, sliced_off


def test_each_start_packs_what_the_other_does_not() -> None:
    """Rung 2 tries both starts: each packs a question the other leaves short (lane HB3-b's skeptic 1, item 8).

    Layouts of 13, 4, 6 and 2 rows over groups of 7, 6, 4, 3, 2, 2 and 1
    rows: the slicing ends 4 rows off with no pair or three to re-pack,
    and the largest groups first lay 7 and 6 into the 13 and pack the
    rest (lane HB3-b's repair 1). Layouts of 9, 20 and 10 rows over groups
    of 7, 6, 4, 3, 5, 7 and 7: the largest groups first end 2 rows off,
    the slicing packs it (found by a generated search of repair 2).
    Mutants: either start removed (`test_each_mutant_turns_a_check_red`).
    """
    for groups, quotas, alone in (((7, 6, 4, 3, 2, 2, 1), [13, 4, 6, 2], (0, 4)), ((7, 6, 4, 3, 5, 7, 7), [9, 20, 10], (2, 0))):
        question = _one_margin(groups, quotas)
        assert _starts_alone(question) == alone
        chosen, exact = generation._layout_repacked(*question, _meter(0, len(groups)))
        assert exact and tables.met_exactly(*question, chosen)


def _codex_family(k: int) -> "tuple[tuple[int, ...], list[tuple[list[int], list[int]]], list[int]]":
    """Codex's family of its review of lane HB3-b, item 4: K made-up values on one row, 100 K on two, K counts of 201 rows."""
    return _one_margin(tuple([1] * k + [2] * (100 * k)), [201] * k)


# THE WORK RUNG 2 IS CHARGED ON CODEX'S FAMILY at K = 20, 40 and 100 (lane
# HB3-b's repair 2): each group the start places and each count it reads,
# each group a re-packing pools and each the bitset sum reads. And on the
# wide column's question, where it re-packs until no pair or three of its
# counts moves, 6 rows short of the exact answer that exists.
CODEX_FAMILY_WORK = (31108, 73932, 224220)
WIDE_QUESTION_WORK = 225052


def test_rung_two_s_work_is_charged_and_linear_on_codex_s_family() -> None:
    """Codex's family packed exactly at K = 20, 40 and 100, the work charged for each doubling of the rows at most 2.5 times.

    The largest groups first lay every count out exactly as they start
    (Codex's review of lane HB3-b, item 4: sliced first, the re-packings
    took 6,428 and 57,648 bitset sums at K = 20 and 40, 9.19 times the
    work for twice the rows, and none past the meter at K = 100). The
    work as charged is pinned, there and on the wide column's question,
    whose re-packings stop 6 rows short inside the budget. Mutants: the
    slicing first, as before; a start's work or a re-packing's pool not
    charged (`test_each_mutant_turns_a_check_red`).
    """
    work: "list[int]" = []
    rows: "list[int]" = []
    for k in (20, 40, 100):
        groups, margins, allowed = _codex_family(k)
        meter = _meter(0, len(groups))
        budget = meter[3]
        chosen, exact = generation._layout_repacked(groups, margins, allowed, meter)
        assert exact and tables.met_exactly(groups, margins, allowed, chosen), k
        work += [budget - meter[3]]
        rows += [sum(groups)]
    for at in range(1, len(work)):
        assert work[at] <= work[at - 1] * (rows[at] / rows[at - 1]) ** math.log2(2.5), (work, rows)
    assert tuple(work) == CODEX_FAMILY_WORK, work
    groups, margins, allowed = tables.wide_question()
    meter = _meter(0, len(groups))
    budget = meter[3]
    chosen, exact = generation._layout_repacked(groups, margins, allowed, meter)
    assert not exact and tables.off_by(groups, margins, allowed, chosen) == 6
    assert budget - meter[3] == WIDE_QUESTION_WORK < budget


def _codex_million() -> "tuple[tuple[int, ...], list[tuple[list[int], list[int]]], list[int]]":
    """Codex's question of its review of lane HB3-b, item 5: two groups of every size 1 to 999 and one of 1,000 -- 1,000,000 rows -- in 1,000 counts of 1,000."""
    groups: "list[int]" = []
    for size in range(1, 1000):
        groups += [size, size]
    return _one_margin(tuple(groups + [1000]), [1000] * 1000)


def test_an_entry_the_meter_cannot_pay_for_is_never_built() -> None:
    """Codex's million-row question: the walk stops at its first cell before building it, the work never below nought.

    The first cell's reserves cost 1,000,000 units against the meter's
    350,000; on the reviewed head the walk built them, took the work to
    minus 650,000 and built the cell's table of reachable totals
    (`_reach_bits`) before it stopped (Codex's review of lane HB3-b, item
    5). Now they are costed as they are made and the walk stops on its
    work with every step left: no table is built and the meter reads
    nought. The re-packing allocator then packs the question exactly.
    Mutant: the entry built and charged after, as before
    (`test_each_mutant_turns_a_check_red`).
    """
    groups, margins, allowed = _codex_million()
    meter = generation._layout_meter(len(groups))
    tables_built: "list[int]" = []
    reach = generation._reach_bits

    def watched(*given):  # type: ignore[no-untyped-def]
        tables_built.append(meter[2])
        return reach(*given)

    with pytest.MonkeyPatch.context() as patched:
        patched.setattr(generation, "_reach_bits", watched)
        ended, chosen = generation._layout_walked(groups, margins, allowed, meter)
    assert not ended and chosen is None and not tables_built
    assert meter[0] == generation._LAYOUT_WALK_STEPS and meter[2] == 0
    meter[1] = 1
    assert _stopped_on_work(meter)
    chosen, exact = generation._layout_repacked(groups, margins, allowed, meter)
    assert exact and tables.met_exactly(groups, margins, allowed, chosen)


def test_the_cliff_question_s_walk_stops_on_its_work() -> None:
    """With little work and many steps, the walk on the cliff's question stops on the work with steps left (LANE HB3-b RULINGS 5 (2)).

    The verify of repair 1 found no case red when the work no longer
    stopped the walk: here a meter of 3,000 steps and 2,000 units stops
    the walk on its work, the meter never below nought, and rung 2 packs
    the question exactly. Mutant: the work's tests removed -- the walk
    then runs out of steps (`test_each_mutant_turns_a_check_red`).
    """
    groups, margins, allowed = tables.cliff_question()
    meter = generation._layout_meter(len(groups))
    meter[0] = 3000
    meter[2] = 2000
    chosen = generation._layout_allotted(groups, margins, allowed, meter)
    assert _stopped_on_work(meter) and meter[2] == 0, meter
    assert chosen is not None and tables.met_exactly(groups, margins, allowed, chosen)


def _three_layout_cells() -> "list[str]":
    """A column of three layouts of 100 rows each: 50 values a layout, each on 2 rows."""
    cells: "list[str]" = []
    for index in range(50):
        cells += [f"AB{index:02d}"] * 2 + [f"CD{index:03d}"] * 2 + [f"EF{index:04d}"] * 2
    return cells


def _laid(cells: "list[str]", counts: "tuple[int, int, int]") -> "list[str]":
    """The column's own cells, ``counts`` of each layout in turn (only the layouts are read)."""
    written: "list[str]" = []
    for head, count in zip(("AB", "CD", "EF"), counts):
        mine = [cell for cell in cells if cell.startswith(head)]
        written += [mine[place % len(mine)] for place in range(count)]
    return written


def test_rung_three_takes_the_nearer_assignment_not_the_fewer_short_layouts(tmp_path: pathlib.Path) -> None:
    """Past the walk, a lay-out is taken by its distance from the census, not by its layouts short (LANE HB3-b RULINGS 4 (1)).

    Three layouts of 100 rows: one lay-out writes 99, 99 and 102 (4 rows
    off, three layouts short), another 100, 80 and 120 (40 rows off, two
    short). Past the walk the first is taken over the second and the
    second not over the first; inside the meter the fewer layouts short
    stands, as before. The verify of repair 1 found the distance rule
    pinned by no case: its mutant compared by layouts short alone.
    Mutant: that comparison (`test_each_mutant_turns_a_check_red`).
    """
    cells = _three_layout_cells()
    _described_profile, block = _described(tmp_path / "three", cells)
    near, far = _laid(cells, (99, 99, 102)), _laid(cells, (100, 80, 120))

    def short(written: "list[str]") -> int:
        return len([note for note in generation._layout_notes(block, written, 1) if note.fact.startswith("layout_forms.")])

    assert (generation._layout_gap(block, near, 1), short(near)) == (4, 3)
    assert (generation._layout_gap(block, far, 1), short(far)) == (40, 2)
    meter = generation._layout_meter(1)
    meter[1] = 1
    assert generation._layout_nearer(block, near, short(near), (far, []), short(far), meter, 1)
    assert not generation._layout_nearer(block, far, short(far), (near, []), short(near), meter, 1)
    meter[1] = 0
    assert not generation._layout_nearer(block, near, short(near), (far, []), short(far), meter, 1)
    assert generation._layout_nearer(block, far, short(far), (near, []), short(near), meter, 1)


def test_both_files_load_where_the_platform_has_no_resource_module() -> None:
    """This file and the K-HZ-40 driver import and read their clocks where `resource` does not exist (Codex's review of lane HB3-b, item 3).

    Windows has no `resource` module and CI's Windows cells collect this
    file: one process imports both with `resource` made unavailable and
    reads each one's CPU clock and the driver's peak, which is then None.
    Mutant: a module-level `import resource`, which
    `tests/test_p3v4f10_windows_reach.py` refuses for this file as well.
    """
    root = pathlib.Path(__file__).resolve().parents[1]
    script = textwrap.dedent(f"""
        import importlib.util
        import sys
        sys.modules["resource"] = None
        sys.path[:0] = [{str(root / "tests")!r}, {str(root)!r}]

        def load(name, path):
            spec = importlib.util.spec_from_file_location(name, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module

        gate = load("held_writer_time_gate", {str(root / "tests" / "test_held_writer_time.py")!r})
        driver = load("held_writer_time_driver", {str(root / "tools" / "measurements" / "kpi_held_writer_time.py")!r})
        print(gate._cpu() >= 0, driver._cpu() >= 0, driver._peak_megabytes())
    """)
    done = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, timeout=600)
    assert done.returncode == 0, done.stderr[-3000:]
    assert done.stdout.strip().splitlines()[-1] == "True True None", done.stdout[-3000:]


def _short_question() -> "tuple[tuple[int, ...], list[tuple[list[int], list[int]]], list[int]]":
    """A question of the layout pass's shape no assignment meets: three groups of 4 rows, two layouts of 6."""
    parts = [4, 3, 3]
    _cells, part_of = tables.grid(parts)
    groups = (4, 4, 4)
    margins = [([0, 0, 0, 12], part_of[0]), ([0, 0, 12], part_of[1]), ([6, 6, 0], part_of[2])]
    mask = 0
    for cell in range(len(part_of[0])):
        if part_of[0][cell] == 3 and part_of[1][cell] == 2:
            mask |= 1 << cell
    return groups, margins, [mask] * len(groups)


def test_rung_two_spends_one_budget_a_column() -> None:
    """Rung 2's tries come off the column's meter, and a column whose re-packing stopped short asks it no more.

    Lane HB3-b's skeptic 1, item 2: the first ask of a question no
    assignment meets spends work from the column's budget and stops
    short with its nearest assignment; a second ask on the same meter
    spends none and has no answer.
    Mutant: the tries and the stop given back for every question, a
    budget a question (`test_each_mutant_turns_a_check_red`).
    """
    groups, margins, allowed = _short_question()
    meter = _meter(0, len(groups))
    budget = meter[3]
    first = generation._layout_allotted(groups, margins, allowed, meter)
    spent = budget - meter[3]
    assert first is not None and meter[4] == 1 and 0 < spent <= budget
    second = generation._layout_allotted(groups, margins, allowed, meter)
    assert second is None and budget - meter[3] == spent


def _mutant_rung_two_inexact(groups, margins, allowed, meter):  # type: ignore[no-untyped-def]
    """A rung 2 that calls its start's answer exact, re-packed or not."""
    sizes = list(groups)
    quotas = [quota for quota in margins[-1][0] if quota > 0]
    where, _read = generation._repack_start(sizes, quotas, [(1 << len(quotas)) - 1] * len(sizes), True)
    if where is None:
        return None, False
    cells = [cell for cell in range(len(margins[0][1])) if all(m[0][m[1][cell]] > 0 for m in margins)]
    return ([cells[index] for index in where], True) if len(cells) == len(quotas) else (None, False)


def test_each_mutant_turns_a_check_red(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path) -> None:
    """Each defect a check guards against, made in the product for the length of the check, turns it red.

    The meter removed and the meter per question are read on the cliff's
    own question by the walk's steps under a small meter (a stated count,
    never a hung case); a metered walk that never counts down fails the
    equality check by its stated count.
    """
    groups, margins, allowed = tables.cliff_question()
    # The meter removed: the cliff's question walks past the steps it is let run.
    with monkeypatch.context() as patched:
        patched.setattr(generation, "_LAYOUT_WALK_STEPS", 10 ** 9)
        patched.setattr(generation, "_LAYOUT_WALK_WORK", 10 ** 12)
        _walk_steps(patched, CLIFF_STEPS)
        with pytest.raises(_Past):
            generation._layout_allotted(groups, margins, allowed, generation._layout_meter(len(groups)))
    # The meter per question: two questions of one column spend twice the steps.
    with monkeypatch.context() as patched:
        patched.setattr(generation, "_LAYOUT_WALK_STEPS", CLIFF_METER)
        counter = _walk_steps(patched, 10 ** 9)
        meter = generation._layout_meter(len(groups))
        generation._layout_allotted(groups, margins, allowed, meter)
        generation._layout_allotted(groups, margins, allowed, meter)
        one_meter = counter[0]
        counter[0] = 0
        generation._layout_allotted(groups, margins, allowed, generation._layout_meter(len(groups)))
        generation._layout_allotted(groups, margins, allowed, generation._layout_meter(len(groups)))
        assert one_meter <= CLIFF_METER < counter[0]
    # A metered walk that never counts down: the equality check stops it at its stated count and fails.
    with monkeypatch.context() as patched:
        next_step = generation._layout_next

        def never_counted(*given):  # type: ignore[no-untyped-def]
            given[-1][0] += 1
            given[-1][2] = 10 ** 12
            return next_step(*given)

        patched.setattr(generation, "_layout_next", never_counted)
        failures, _seen = _equality_failures(patched, EQUALITY_METER, 300)
        assert any("passed its meter" in failure for failure in failures)
    # An inexact rung 2 called exact: the re-packing check fails.
    with monkeypatch.context() as patched:
        patched.setattr(generation, "_layout_repacked", _mutant_rung_two_inexact)
        failures, _seen = _repacking_failures(200)
        assert failures
    # A permission ignored: the recount inside rung 2 and its starts open every count.
    with monkeypatch.context() as patched:
        counted = generation._layout_off
        patched.setattr(
            generation, "_layout_off",
            lambda groups, margins, allowed, chosen: counted(groups, margins, [-1] * len(groups), chosen),
        )
        original = generation._repack_start
        patched.setattr(
            generation, "_repack_start",
            lambda sizes, quotas, opens, sliced: original(sizes, quotas, [(1 << len(quotas)) - 1] * len(sizes), sliced),
        )
        failures, _seen = _repacking_failures(400)
        assert failures
    # A budget a question: the tries and the stop given back, the column's second ask spends again.
    with monkeypatch.context() as patched:
        allotted = generation._layout_allotted

        def per_question(groups, margins, allowed, meter):  # type: ignore[no-untyped-def]
            meter[3] = generation._REPACK_WORK + generation._REPACK_WORK_A_GROUP * len(groups)
            meter[4] = 0
            return allotted(groups, margins, allowed, meter)

        patched.setattr(generation, "_layout_allotted", per_question)
        with pytest.raises(AssertionError):
            test_rung_two_spends_one_budget_a_column()
    # Either start removed: the question only the other packs is not packed.
    for removed in (False, True):
        with monkeypatch.context() as patched:
            repacked = generation._repacked
            patched.setattr(
                generation, "_repacked",
                lambda sizes, quotas, opens, sliced, meter, removed=removed: (
                    (None, 0) if sliced == removed else repacked(sizes, quotas, opens, sliced, meter)
                ),
            )
            with pytest.raises(AssertionError):
                test_each_start_packs_what_the_other_does_not()
    # Rung 2's work: the slicing first as before, a start's work uncharged, a re-packing's pool uncharged.
    for name, edits in (
        ("_layout_repacked", (("for sliced in (False, True):", "for sliced in (True, False):", 1),)),
        ("_repacked", (("meter[3] = meter[3] - len(sizes) - read", "meter[3] = meter[3] - 0", 1),)),
        ("_repacked_with", (("work = len(pool)", "work = 0", 1),)),
    ):
        with monkeypatch.context() as patched:
            _compiled_mutant(patched, {name: edits})
            with pytest.raises(AssertionError):
                test_rung_two_s_work_is_charged_and_linear_on_codex_s_family()
    # An entry built and charged after, as on the reviewed head: its table is built past the meter.
    with monkeypatch.context() as patched:

        def built_then_charged(keys, left, owed, part_at, part_cells, families, cell, room, meter):  # type: ignore[no-untyped-def]
            entry = generation._cell_entry(keys, left, owed, part_at, part_cells, families, cell, room)
            if entry is not None:
                meter[2] = meter[2] - len(entry[4]) - sum(len(filed) for filed in entry[3])
            return entry

        patched.setattr(generation, "_layout_cell_entry", built_then_charged)
        with pytest.raises(AssertionError):
            test_an_entry_the_meter_cannot_pay_for_is_never_built()
    # The work's tests removed (the verify of repair 1's mutant M1): the walk runs out of steps instead.
    with monkeypatch.context() as patched:
        _compiled_mutant(patched, {
            "_layout_allotted": (("meter[0] > 0 and meter[2] > 0", "meter[0] > 0", 1),),
            "_layout_walk_counted": (
                ("if meter[0] < 1 or meter[2] < 1:", "if meter[0] < 1:", 1),
                ("                if meter[2] < 1:\n                    return False, None\n", "", 1),
            ),
            "_layout_next": (("            if meter[2] < 1:\n                return walk, None, False\n", "", 1),),
            "_layout_found_from": (("        if meter[2] < 1:\n            raise _LayoutSpent()\n", "", 2),),
            "_layout_cell_entry": (("if paid and meter[2] - cost >= 1:", "if paid:", 1),),
        })
        with pytest.raises(AssertionError):
            test_the_cliff_question_s_walk_stops_on_its_work()
    # Rung 3 compared by its layouts short alone (the verify of repair 1's mutant M2).
    with monkeypatch.context() as patched:
        _compiled_mutant(patched, {"_layout_nearer": (("if not meter[1]:", "if True:", 1),)})
        with pytest.raises(AssertionError):
            test_rung_three_takes_the_nearer_assignment_not_the_fewer_short_layouts(tmp_path)
    # The build's meter: the rare column's walk does not end inside 604 steps.
    with monkeypatch.context() as patched:
        patched.setattr(generation, "_LAYOUT_WALK_STEPS", 604)
        with pytest.raises(AssertionError):
            test_the_meter_keeps_the_rare_column_s_own_walk()
    # A meter below twice the census's largest walk.
    with monkeypatch.context() as patched:
        patched.setattr(generation, "_LAYOUT_WALK_STEPS", 2 * CENSUS_MOST - 1)
        with pytest.raises(AssertionError):
            test_the_meter_covers_the_census()
    # The stand-ins' memories keyed wrong: a mix by its base alone, a refusal by its base.
    for mutant in ("made", "refused"):
        with monkeypatch.context() as patched:
            _stand_in_mutant(patched, mutant)
            with pytest.raises(AssertionError):
                test_the_stand_ins_memory_changes_no_stand_in()
    # Rung 3 unfiled: a column whose pass stops and leaves a layout short goes unnamed.
    with monkeypatch.context() as patched:
        patched.setattr(generation, "_layout_filed", lambda column, answer, meter, floor: answer)
        patched.setattr(generation, "_layout_repacked", lambda *given: (None, False))
        patched.setattr(generation, "_LAYOUT_WALK_STEPS", 0)
        failures = _filing_failures(tmp_path / "unfiled")
        assert failures
    # ...and filed, the same column names each short layout with its cause.
    with monkeypatch.context() as patched:
        patched.setattr(generation, "_layout_repacked", lambda *given: (None, False))
        patched.setattr(generation, "_LAYOUT_WALK_STEPS", 0)
        assert not _filing_failures(tmp_path / "filed")


def _compiled_mutant(patched: pytest.MonkeyPatch, edits: "dict[str, tuple[tuple[str, str, int], ...]]") -> None:
    """Functions of the product compiled again from their own text with ``edits`` made, for the length of a check.

    ``edits`` maps a function's name to (text, replacement, how many
    times the text stands); the functions are compiled into one namespace,
    so a mutated function calls the others mutated too.
    """
    namespace = dict(vars(generation))
    for name, changes in edits.items():
        source = textwrap.dedent(inspect.getsource(getattr(generation, name)))
        for old, new, times in changes:
            assert source.count(old) == times, (name, old)
            source = source.replace(old, new)
        exec(compile(source, generation.__file__, "exec"), namespace)  # noqa: S102
    for name in edits:
        patched.setattr(generation, name, namespace[name])


def _stand_in_mutant(patched: pytest.MonkeyPatch, mutant: str) -> None:
    """The stand-ins' two memories keyed wrong, compiled from the product's own text for the length of a check."""
    source = textwrap.dedent(inspect.getsource(generation._layout_stand_in))
    if mutant == "made":
        edits = (("(base, mixed[base] % mixes)", "(base, 0)"),)
    else:
        edits = (("if mix not in refused:", "if base not in refused:"), ("refused[mix]", "refused[base]"))
    for old, new in edits:
        assert old in source, old
        source = source.replace(old, new)
    namespace = dict(vars(generation))
    exec(compile(source, generation.__file__, "exec"), namespace)  # noqa: S102
    patched.setattr(generation, "_layout_stand_in", namespace["_layout_stand_in"])


def _filing_failures(folder: pathlib.Path) -> "list[str]":
    """A column whose pass is stopped and whose layouts are left short: each short layout filed with its cause."""
    described, block = _described(folder, _filing_cells())
    twin, filed = _twin_column(described)
    forms = dict(block.facts.layout_forms)
    present = [cell for cell in twin if cell.strip()]
    census = taxonomy.layout_census(present, 1, len(set(present)))
    pool = forms.get("(withheld)", 0)
    failures: "list[str]" = []
    short = 0
    for layout, count in forms.items():
        if layout == "(withheld)" or count <= census.get(layout, 0) <= count + pool:
            continue
        short += 1
        if filed.get(f"layout_forms.{layout}") != generation._LAYOUT_PASS_STOPPED:
            failures += [f"layout {layout} left short and not filed with its cause"]
    assert short, "the filing case left no layout short"
    return failures


def _cpu() -> float:
    """This process's CPU seconds, user plus system, on every platform (Codex's review of lane HB3-b, item 3)."""
    return time.process_time()


# THE 20,000-ROW CASE'S STATED TIME, in CPU seconds of generate (plan
# P4-D490; K-HZ-40's bound). A time is a number the machine decides
# (STATE's rule 9): it is judged only where `kpi_rules.seconds_judged_here`
# allows a seconds rule -- the quiet reference machine -- and reported
# elsewhere (Codex's review of lane HB3-b, item 6); what every machine
# judges is the meter itself, the steps and the work the pass spent.
STATED_SECONDS = 60.0


def test_the_held_exam_column_is_generated_at_the_floor(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path
) -> None:
    """The 20,000-row case: the exam column held unanswered, its pass inside its meter, generated in under 60 CPU seconds.

    Through the commands a person types, the table floor on: profile, the
    person column answered `identifier`, profile again, generate, validate.
    On every machine: the column's layout pass spent no more steps and no
    more work than its meter holds, and its walk stopped on the work with
    steps left (4,629 steps on lane HB3-b's repair 1), so the re-packing
    allocator answered and the twin met every count; the seconds are
    judged on the quiet reference machine only (`STATED_SECONDS`). The
    patient layer, which the shipped command draws at the floor (lane
    W5-PL), makes the column within its own row run: left out here.
    Mutant: the work no longer stops the walk -- it then runs out of
    steps (`test_each_mutant_turns_a_check_red`, on the cliff's question).
    """
    monkeypatch.setattr(cli, "_PATIENT_LAYER_SHIPPED", False)
    header, rows = tables.exam_rows(20000)
    source = tmp_path / "exams.csv"
    tables.write_csv(source, header, rows)

    def typed(arguments: "list[str]") -> int:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return cli.main(arguments)

    assert typed(["profile", str(source), "--out-dir", str(tmp_path), "--replace"]) == 0
    questions = tmp_path / "exams-questions.json"
    document = json.loads(questions.read_text(encoding="utf-8"))
    for entry in document["asked"]:
        if entry["column"] == "person_id":
            entry["your_answer"] = "identifier"
    questions.write_text(json.dumps(document), encoding="utf-8", newline="\n")
    # The answered round is the first to publish between columns (the patient layer at the floor, lane W5-PL): the
    # record of earlier descriptions asks for --replace-description, as the first round's screen says.
    assert typed(["profile", str(source), "--out-dir", str(tmp_path), "--replace", "--answers", str(questions),
                  "--replace-description"]) == 0
    described = json.loads((tmp_path / "exams-profile.json").read_text(encoding="utf-8"))
    exam = [column for column in described["columns"] if column["name"] == "exam"][0]
    assert exam["role"] == "identifier"
    profile = str(tmp_path / "exams-profile.json")
    meters: "list[list[int]]" = []
    making = generation._layout_meter

    def kept_meter(*given: int) -> "list[int]":
        meter = making(*given)
        meters.append(meter)
        return meter

    monkeypatch.setattr(generation, "_layout_meter", kept_meter)
    started = _cpu()
    assert typed(["generate", profile, "--out-dir", str(tmp_path), "--replace", "--seed", "0"]) == 0
    spent = _cpu() - started
    exam_meters = [meter for meter in meters if meter[1]]
    assert len(exam_meters) == 1, meters
    assert _stopped_on_work(exam_meters[0]), exam_meters[0]
    judged, why = kpi_rules.seconds_judged_here(kpi_rules.load_ledger())
    if judged:
        assert spent < STATED_SECONDS, spent
    else:
        print(f"generate took {spent:.1f} CPU s; the {STATED_SECONDS:.0f} s stated time is reported and not judged here: {why}")
    assert typed(["validate", profile, "--twin", str(tmp_path / "exams-twin.csv"), "--out-dir", str(tmp_path), "--replace"]) == 0
    with open(source, encoding="utf-8", newline="") as handle:
        real = {row["exam"] for row in csv.DictReader(handle)}
    with open(tmp_path / "exams-twin.csv", encoding="utf-8", newline="") as handle:
        written = [row["exam"] for row in csv.DictReader(handle)]
    # NO TWIN CELL EQUALS A REAL ONE, exactly, folded or by the merged key a person is counted by.
    folded = {value.casefold() for value in real}
    merged = {str(parsing.merged_key(parsing.trimmed(value))) for value in real}
    assert not [
        cell for cell in written
        if cell in real or cell.casefold() in folded or str(parsing.merged_key(parsing.trimmed(cell))) in merged
    ]
