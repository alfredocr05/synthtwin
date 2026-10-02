"""Columns of numbers written to full precision describe, and a column nothing reads is split once (plan P4-D380).

THE DEFECT, MEASURED ON 668f276 BY THE DATE-AND-TIME REACH AUDIT'S
SKEPTIC. A number a program computes and writes in full -- the hours
between two times as seconds over 3,600, a ratio of two counts, an
Excel time as a fraction of a day: what Python's `repr` and pandas
write by default -- has a different spelling on almost every row, so
the census of how many figures follow the point can be one pool beside
about a thousand widths. Two things then went wrong in the walk that
asks whether such a pool may stand (`parsing.mixture_pool_holds`):

1. **It nested once per width.** `parsing._fill` called itself once per
   convention, and `synthtwin profile` stopped on a bare
   `RecursionError` with no file written: hours-between columns at
   1,000 rows in 14 of 20 seeds, ratios in 7 of 20, CSV time fractions
   in 15 of 20 and every workbook time column holding seconds.
2. **One step of its budget could cost seconds.** `parsing._topped_up`
   -- a reading of the free cells -- wrote the free conventions one at
   a time over every count of written conventions, about ``seen``
   times the free conventions in big-number steps, and the budget
   charged the reading one step. Walking the same column iteratively
   took 4.2 s at 1,000 rows, 41 s at 3,000 and more than twelve CPU
   minutes at 10,000.

AND A COLUMN NOTHING READS was split sixteen times a cell: four
readings ask `taxonomy.affixed_split` of every present cell, in each of
the census's and the description's passes. An unread column of 1,000
Oracle-style timestamps took about ten seconds, nine of them there.

THE REPAIR, AND WHAT THIS FILE PINS:

- `_fill` carries its own stack and finds what the recursion found at
  the same cost, against the pre-repair text carried below;
- `_topped_up` is worked out as the sum it is, and answers what the
  walk over every free convention answered, against that text too,
  and `parsing._free_totals` holds exactly the totals free conventions
  can hold;
- the budget is charged for the work each step does
  (`POOL_WORDS_A_STEP`, `POOL_CELLS_A_STEP`), so the stop-short answer
  the walk always had takes over where the work is too large;
- a census wider than the interpreter can nest describes through the
  command, and the same column under the recursive walk ends in a
  sentence, never a stack trace (`errors.stopped_nested_too_deep`);
- computed numbers at 10,000 and 100,000 rows describe, with the work
  counted machine-free and the seconds judged only where
  `kpi_rules.seconds_judged_here` allows;
- the description of such a column is the one the pre-repair walk
  gives, byte for byte;
- and `affixed_split` runs once per different text of a reading, its
  answers the same.
"""

from __future__ import annotations

import ast
import contextlib
import io
import json
import pathlib
import random
import sys
import time

import pytest

import kpi_rules
from synthtwin import cli, errors, generation, parsing, taxonomy, validation

# The shipped default smallest group.
FLOOR = 11


# -- the pre-repair walk, carried whole -----------------------------------
#
# VERBATIM, but for their names and for naming `parsing`'s helpers through
# the module. They are the references the repair is proved against and the
# mutations the regression tests are watched failing under, so they are
# copied rather than paraphrased: a reference written afresh would prove
# agreement with itself.


def recursive_fill(state, slots, after, amounts, slot, left, parts, found, budget) -> None:
    """`parsing._fill` as it stood before the repair: it calls itself once per slot."""
    budget[0] = budget[0] - 1
    if budget[0] < 1:
        return
    if left == 0:
        grown = []
        start = 0
        for kind in range(len(state)):
            loads = []
            for position in range(len(state[kind])):
                loads += [state[kind][position] + amounts[start + position]]
            start = start + len(state[kind])
            grown += [tuple(sorted(loads, reverse=True))]
        found[tuple(grown)] = True
        return
    if slot >= len(slots) or parts < 1 or after[slot] < left:
        return
    kind, position, share = slots[slot]
    top = min(share, left)
    if position > 0 and state[kind][position - 1] == state[kind][position]:
        top = min(top, amounts[slot - 1])
    for amount in range(top, -1, -1):
        amounts[slot] = amount
        recursive_fill(
            state, slots, after, amounts, slot + 1, left - amount,
            parts - (1 if amount > 0 else 0), found, budget,
        )
    amounts[slot] = 0


def walked_topped_up(population, kinds, state, seen, barred, empty, work=None) -> bool:
    """`parsing._topped_up` as it stood before the repair: every free convention written one at a time.

    ``work`` is accepted and left alone, so this can stand in the shipped
    walk's place; the pre-repair walk charged a reading one step.
    """
    within = (1 << (population + 1)) - 1
    layers = [1] + [0] * seen
    for kind in range(len(kinds)):
        most = kinds[kind][0]
        loads = state[kind]
        idle = 0
        for load in loads:
            if load == 0:
                idle += 1
        if kind == empty:
            idle = idle - 1
        for load in loads:
            if load < 1:
                continue
            grown = [0] * (seen + 1)
            for written in range(seen):
                if layers[written]:
                    grown[written + 1] = parsing._spread(layers[written], load, most, barred) & within
            layers = grown
        if idle < 1:
            continue
        batch = [0] * (seen + 1)
        for written in range(seen + 1):
            batch[written] = layers[written]
        reach = layers
        for _ in range(min(idle, seen)):
            step = [0] * (seen + 1)
            for written in range(seen):
                if reach[written]:
                    step[written + 1] = parsing._spread(reach[written], 1, most, barred) & within
            for written in range(seen + 1):
                batch[written] = batch[written] | step[written]
            reach = step
        layers = batch
    for written in range(seen + 1):
        if (layers[written] >> population) & 1:
            return True
    return False


# -- the columns ------------------------------------------------------------


def hours_between(rows: int, seed: int) -> "list[str]":
    """Hours between two times at second resolution, written in full as Python and pandas write a float."""
    draw = random.Random(seed)
    return [repr(draw.randrange(1, 72 * 3600) / 3600) for _cell in range(rows)]


# A 1,000-row column of `hours_between` whose fraction widths reach the walk
# with more widths than the interpreter nests by default (1,014 at seed 1),
# and the 10,000- and 100,000-row columns of the gate (seed 5000: 9,825
# widths beside 16 values a reader places, and about 83,000 beside 364).
NESTED_SEED = 1
GATE_SEED = 5000


def _table(folder: pathlib.Path, name: str, cells: "list[str]") -> pathlib.Path:
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{name}.csv"
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("value\n" + "".join(cell + "\n" for cell in cells))
    return path


def _profile(path: pathlib.Path, out: pathlib.Path) -> "tuple[int, str]":
    """`synthtwin profile` on one table: its exit code and what it said."""
    out.mkdir(parents=True, exist_ok=True)
    said = io.StringIO()
    with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
        code = cli.main(["profile", str(path), "--out-dir", str(out), "--replace"])
    return code, said.getvalue()


class _Widest:
    """Counts the walk's placements, the widest state it placed onto, and its readings' big-number steps."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self.placements = 0
        self.widest = 0
        self.spreads = 0
        placements = parsing._placements
        spread = parsing._spread

        def counted_placements(state, kinds, index, rows, spellings, budget):
            self.placements += 1
            self.widest = max(self.widest, sum(len(loads) for loads in state))
            return placements(state, kinds, index, rows, spellings, budget)

        def counted_spread(sums, low, high, barred):
            self.spreads += 1
            return spread(sums, low, high, barred)

        monkeypatch.setattr(parsing, "_placements", counted_placements)
        monkeypatch.setattr(parsing, "_spread", counted_spread)


# -- 1. the walk carries its own stack ---------------------------------------


def _fill_shape(draw: random.Random) -> "tuple[tuple[tuple[int, ...], ...], list[tuple[int, ...]], int, int]":
    """A state of loads over kinds, as `_pool_readings` builds them, and one value's rows and spellings."""
    kinds: "list[tuple[int, ...]]" = []
    state: "list[tuple[int, ...]]" = []
    for _kind in range(draw.randint(1, 4)):
        most = draw.randint(1, 12)
        share = draw.randint(0, most)
        size = draw.choice((1, 2, 3, 5, 9, draw.randint(1, 30)))
        loads = sorted((draw.randint(0, most) if draw.random() < 0.5 else 0 for _slot in range(size)), reverse=True)
        kinds += [(most, share)]
        state += [tuple(loads)]
    return tuple(state), kinds, draw.randint(0, 25), draw.randint(0, 8)


def _slots(state, kinds) -> "tuple[list[tuple[int, int, int]], list[int]]":
    """`_placements`' table, built as it builds it, for the one value ``kinds`` holds a share of."""
    slots: "list[tuple[int, int, int]]" = []
    for kind in range(len(kinds)):
        for position in range(len(state[kind])):
            slots += [(kind, position, max(0, min(kinds[kind][0] - state[kind][position], kinds[kind][1])))]
    after = [0] * (len(slots) + 1)
    for slot in range(len(slots) - 1, -1, -1):
        after[slot] = after[slot + 1] + slots[slot][2]
    return slots, after


FILL_SHAPES = 1_500
FILL_BUDGETS = (20_000, 1_000, 50, 7, 2, 1, 0)


def test_the_walk_finds_what_the_recursion_found_at_the_same_cost(monkeypatch: pytest.MonkeyPatch) -> None:
    """Same states in the same order, same budget left, the amounts cleared: at every budget.

    The charge this landing added for a state written out is set aside
    (`POOL_CELLS_A_STEP` made too large to charge anything), so what is
    compared is the recursion's own accounting, one step per call, at
    budgets from one most shapes finish under down to none. Mutations:
    skipping every other amount, or dropping the falling order among
    conventions of one load, turns it red.
    """
    monkeypatch.setattr(parsing, "POOL_CELLS_A_STEP", 10**12)
    draw = random.Random(20261001)
    differed: "list[str]" = []
    spent_out = found_some = 0
    for _shape in range(FILL_SHAPES):
        state, kinds, rows, spellings = _fill_shape(draw)
        slots, after = _slots(state, kinds)
        for budget in FILL_BUDGETS:
            here: "dict" = {}
            there: "dict" = {}
            budget_here, budget_there = [budget], [budget]
            amounts_here, amounts_there = [0] * len(slots), [0] * len(slots)
            parsing._fill(state, slots, after, amounts_here, 0, rows, spellings, here, budget_here)
            recursive_fill(state, slots, after, amounts_there, 0, rows, spellings, there, budget_there)
            if list(here) != list(there) or budget_here != budget_there or amounts_here != amounts_there:
                differed += [f"{kinds} {state} rows {rows} over {spellings} at {budget}: "
                             f"{len(here)}/{len(there)} states, budget {budget_here}/{budget_there}"]
            spent_out += budget_there[0] < 1
            found_some += len(there) > 0
    assert differed == [], "\n".join(differed[:10])
    # BOTH ROADS ARE TAKEN OFTEN, or the agreement is about one of them.
    assert spent_out >= FILL_SHAPES, spent_out
    assert found_some >= FILL_SHAPES, found_some


def test_a_state_written_out_is_charged_its_size() -> None:
    """One step a call, and one more for every `POOL_CELLS_A_STEP` conventions a state found holds.

    Forty conventions of one kind, none loaded, one value of three rows on
    one spelling: the walk finds the one state (three rows on the first
    convention). Mutation: the charge left out turns it red.
    """
    state = ((0,) * 40,)
    kinds = [(10, 10)]
    slots, after = _slots(state, kinds)
    budget = [10**9]
    found: "dict" = {}
    parsing._fill(state, slots, after, [0] * len(slots), 0, 3, 1, found, budget)
    plain = [10**9]
    recursive_fill(state, slots, after, [0] * len(slots), 0, 3, 1, {}, plain)
    assert list(found) == [((3,) + (0,) * 39,)], list(found)
    assert plain[0] - budget[0] == len(found) * (40 // parsing.POOL_CELLS_A_STEP), (plain, budget)


def test_the_walk_can_never_reach_itself() -> None:
    """Read off the source: `_fill` names no function that names `_fill`.

    The defect counted directly rather than its symptom, as
    `tests/test_tail_back_solve_without_recursion.py` counts it for the
    tail's walk: a test that only described a wide census would go quiet
    the day the census changed shape.
    """
    tree = ast.parse(pathlib.Path(parsing.__file__).resolve().read_text(encoding="utf-8"))
    walk = ("_fill", "_placements", "_pool_readings", "_topped_up", "_free_totals", "_spread_over",
            "_strided", "_total_among", "_charged")
    names: "dict[str, set[str]]" = {name: set() for name in walk}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in names:
            for inner in ast.walk(node):
                if isinstance(inner, ast.Name) and inner.id in names and inner.id != node.name:
                    names[node.name] = names[node.name] | {inner.id}
                if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Name) and inner.func.id == node.name:
                    names[node.name] = names[node.name] | {node.name}
    for start in walk:
        reached = set(names[start])
        while True:
            onward = set(reached)
            for name in reached:
                onward = onward | names[name]
            if onward == reached:
                break
            reached = onward
        assert start not in reached, f"{start} reaches itself through {sorted(reached)}"


# -- 2. a reading of the free cells is a sum -----------------------------------


def _reading_case(draw: random.Random) -> "tuple[int, list[tuple[int, ...]], tuple[tuple[int, ...], ...], int, int, int]":
    """One reading `_pool_readings` can ask: kinds of capacities under a line, loads, the room, a barred count, a kind to leave empty."""
    line = draw.choice((2, 3, 4, 5, 6, 11, 12))
    kinds: "list[tuple[int, ...]]" = []
    state: "list[tuple[int, ...]]" = []
    for _kind in range(draw.randint(1, 5)):
        most = line - 1 if draw.random() < 0.7 else draw.randint(1, line - 1)
        size = draw.choice((1, 1, 2, 3, 5, 8, draw.randint(1, 24), draw.randint(20, 60)))
        loads = sorted((draw.randint(1, most) if draw.random() < 0.3 else 0 for _slot in range(size)), reverse=True)
        kinds += [(most,)]
        state += [tuple(loads)]
    total = sum(len(loads) for loads in state)
    seen = draw.randint(0, total + 2)
    population = draw.randint(1, 10 * (line - 1) + 30)
    barred = draw.choice((-1, -1) + tuple(range(1, line)))
    empty = -1
    if draw.random() < 0.4:
        open_kinds = [kind for kind in range(len(state)) if state[kind][len(state[kind]) - 1] == 0]
        if open_kinds:
            empty = draw.choice(open_kinds)
    return population, kinds, tuple(state), seen, barred, empty


READINGS = 6_000


def test_the_sum_answers_what_the_walk_over_every_free_convention_answered() -> None:
    """Seeded readings, every capacity, room and barred count: the same truth value.

    The family reaches every road of the sum -- one capacity of free
    conventions or several, a room that holds them all or one too small
    for them, a barred count at either end of the counts or inside them,
    a kind with one convention left empty -- and both answers often.
    Mutations: `_free_totals` holding ``count * most - 1`` where the
    barred count is ``most - 1``; reading the largest pool with the whole
    room where another pool already spent some of it; a loaded convention
    allowed past ``seen``: each turns it red.
    """
    draw = random.Random(20261002)
    differed: "list[str]" = []
    held = bound = several = 0
    for _case in range(READINGS):
        case = _reading_case(draw)
        shipped = parsing._topped_up(*case)
        walked = walked_topped_up(*case)
        if shipped != walked:
            differed += [f"{case}: {shipped} where the walk read {walked}"]
        held += walked
        population, kinds, state, seen, _barred, _empty = case
        idle = sum(1 for loads in state for load in loads if load == 0)
        loaded = sum(1 for loads in state for load in loads if load > 0)
        bound += 0 < seen - loaded < idle
        several += len({kinds[kind][0] for kind in range(len(kinds)) if 0 in state[kind]}) > 1
    assert differed == [], "\n".join(differed[:10])
    assert READINGS // 10 <= held <= READINGS - READINGS // 10, held
    assert bound >= READINGS // 10, bound
    assert several >= READINGS // 10, several


def _held_by(most: int, barred: int, count: int, ceiling: int) -> "set[int]":
    """Every total ``count`` or fewer free conventions hold, found by writing them one at a time."""
    counts = [value for value in range(1, most + 1) if value != barred]
    reach = 1
    every = 1
    mask = (1 << (ceiling + 1)) - 1
    for _convention in range(count):
        moved = 0
        for value in counts:
            moved = moved | (reach << value)
        reach = moved & mask
        every = every | reach
    return {total for total in range(ceiling + 1) if (every >> total) & 1}


def _runs_hold(runs: "list[tuple[int, int]]", stride: int, ceiling: int) -> "set[int]":
    held: "set[int]" = set()
    for low, high in runs:
        for total in range(low, min(high, ceiling) + 1, stride):
            held.add(total)
    return held


def test_the_free_totals_are_every_total_the_free_conventions_hold() -> None:
    """Every capacity to fifteen, every barred count, every number of conventions to thirty-nine.

    The closed forms `parsing._free_totals` returns, against the totals
    written out one convention at a time. Mutation: dropping the barred
    count's own run where only one convention is written, or the lone
    total the top loses where the barred count is one below it, turns it
    red.
    """
    differed: "list[str]" = []
    for most in range(1, 16):
        for barred in [-1, 0] + list(range(1, 18)):
            for count in range(0, 40):
                ceiling = count * most + 2
                runs, stride = parsing._free_totals(most, barred, count)
                if _runs_hold(runs, stride, ceiling) != _held_by(most, barred, count, ceiling):
                    differed += [f"capacity {most}, barred {barred}, {count} conventions: {runs} by {stride}"]
    assert differed == [], "\n".join(differed[:10])


# -- 3. a census wider than the interpreter can nest ---------------------------


def test_a_census_wider_than_the_interpreter_can_nest_describes(tmp_path, monkeypatch) -> None:
    """The regression: the whole command, on hours between two times written in full.

    The column's fraction widths are one pool beside more widths than
    `sys.getrecursionlimit()`, so the pre-repair walk nested past it on
    every reading; the walk is counted to show it was reached that wide.
    """
    counted = _Widest(monkeypatch)
    path = _table(tmp_path / "in", "hours", hours_between(1000, NESTED_SEED))
    code, said = _profile(path, tmp_path / "out")
    assert code == 0, said
    assert counted.widest > sys.getrecursionlimit(), (counted.widest, sys.getrecursionlimit())
    block = json.loads((tmp_path / "out" / "hours-profile.json").read_text(encoding="utf-8"))["columns"][0]
    assert block["role"] == taxonomy.ROLE_CONTINUOUS, block["role"]
    assert block["fraction_widths"], block["fraction_widths"]


def test_the_same_column_under_the_recursive_walk_ends_in_a_sentence(tmp_path, monkeypatch) -> None:
    """RED CHECK, and the message: put the old walk back and the command stops, in words.

    Without it the test above says only that a table describes. And the
    stop is the catalogue's sentence on the error stream with the exit
    code of a refusal, never a stack trace: a step that still nests too
    deep ends the run the way every other refusal does.
    """
    monkeypatch.setattr(parsing, "_fill", recursive_fill)
    path = _table(tmp_path / "in", "hours", hours_between(1000, NESTED_SEED))
    code, said = _profile(path, tmp_path / "out")
    assert code == 1, said
    assert errors.stopped_nested_too_deep(str(path)) in said, said
    assert "Traceback" not in said and "RecursionError" not in said, said
    assert not (tmp_path / "out" / "hours-profile.json").exists()


@pytest.mark.parametrize("command", ("generate", "validate"))
def test_a_step_nesting_too_deep_in_the_other_commands_ends_in_a_sentence(command, tmp_path, monkeypatch) -> None:
    """The same sentence for a twin being built and a file being checked, on the description the person typed."""
    path = _table(tmp_path / "in", "hours", hours_between(200, NESTED_SEED))
    code, said = _profile(path, tmp_path / "out")
    assert code == 0, said
    described = tmp_path / "out" / "hours-profile.json"

    def too_deep(*_arguments: object, **_keywords: object) -> None:
        raise RecursionError("maximum recursion depth exceeded")

    if command == "generate":
        monkeypatch.setattr(generation, "generate", too_deep)
        argv = ["generate", str(described), "--seed", "0", "--out-dir", str(tmp_path / "twin")]
    else:
        monkeypatch.setattr(validation, "measure", too_deep)
        argv = ["validate", str(described), "--twin", str(path), "--out-dir", str(tmp_path / "check")]
    (tmp_path / "twin").mkdir()
    (tmp_path / "check").mkdir()
    heard = io.StringIO()
    with contextlib.redirect_stdout(heard), contextlib.redirect_stderr(heard):
        code = cli.main(argv)
    assert code == 1, heard.getvalue()
    assert errors.stopped_nested_too_deep(str(described)) in heard.getvalue(), heard.getvalue()
    assert "Traceback" not in heard.getvalue(), heard.getvalue()


# -- 4. the description is the pre-repair walk's own --------------------------


def test_the_description_is_the_one_the_walk_over_every_free_convention_gives(tmp_path, monkeypatch) -> None:
    """Byte for byte, against the pre-repair accounting and the pre-repair reading of the free cells.

    The shipped run, then the same command with `_topped_up` replaced by
    the pre-repair text and both work charges set aside, so every step
    costs one as it did: the walk then answers exactly as the pre-repair
    walk answered (its `_fill` is proved equal above). Both describe the
    column the same.
    """
    path = _table(tmp_path / "in", "hours", hours_between(1000, NESTED_SEED))
    code, said = _profile(path, tmp_path / "shipped")
    assert code == 0, said
    monkeypatch.setattr(parsing, "_topped_up", walked_topped_up)
    monkeypatch.setattr(parsing, "POOL_CELLS_A_STEP", 10**12)
    monkeypatch.setattr(parsing, "POOL_WORDS_A_STEP", 10**12)
    code, said = _profile(path, tmp_path / "walked")
    assert code == 0, said
    for name in ("hours-profile.json", "hours-profile.txt", "hours-questions.json"):
        shipped = (tmp_path / "shipped" / name).read_bytes()
        walked = (tmp_path / "walked" / name).read_bytes()
        assert shipped == walked, name


# -- 5. the gate: 10,000 and 100,000 rows ----------------------------------------

# The most big-number steps the readings of the 10,000-row column may take
# in all, across the four times the census is asked. Measured at 820; the
# pre-repair readings of one 3,000-row column took about 1.5 million.
SPREADS_AT_TEN_THOUSAND = 4_000

# The seconds each size may take to describe on the quiet reference
# machine, judged only there (`kpi_rules.seconds_judged_here`).
SECONDS = {10_000: 30.0, 100_000: 120.0}


@pytest.mark.parametrize("rows", (10_000, 100_000))
def test_computed_numbers_describe_at_ten_thousand_and_a_hundred_thousand_rows(rows, tmp_path, monkeypatch) -> None:
    """The gate: no stack trace, the stop-short answer standing, the work counted, the seconds judged where they are.

    At 10,000 rows the walk is taken and spends its budget, and its
    readings are a few big-number steps each. At 100,000 rows the table
    of about 83,000 widths beside 364 values is charged before it is
    built and is more than the whole budget, so no step is taken and the
    census is counted at one width at once. Mutations: the pre-repair
    reading of the free cells takes the 10,000-row column past the bound
    on big-number steps; the table charge left out puts the 100,000-row
    column's widths into the walk.
    """
    counted = _Widest(monkeypatch)
    path = _table(tmp_path / "in", "hours", hours_between(rows, GATE_SEED))
    started = time.perf_counter()
    code, said = _profile(path, tmp_path / "out")
    seconds = time.perf_counter() - started
    assert code == 0, said
    block = json.loads((tmp_path / "out" / "hours-profile.json").read_text(encoding="utf-8"))["columns"][0]
    assert block["role"] == taxonomy.ROLE_CONTINUOUS, block["role"]
    widths = block["fraction_widths"]
    assert len(widths) == 1 and taxonomy.SUPPRESSED_LABEL not in widths, widths
    assert sum(widths.values()) == rows, widths
    if rows == 10_000:
        assert counted.widest > rows // 2, counted.widest
        assert counted.spreads <= SPREADS_AT_TEN_THOUSAND, counted.spreads
    else:
        assert counted.widest < rows // 2, counted.widest
    judged, why = kpi_rules.seconds_judged_here(kpi_rules.load_ledger())
    if judged:
        assert seconds < SECONDS[rows], seconds
    else:
        print(f"{rows} rows described in {seconds:.1f} s, reported and not judged here: {why}")


# -- 6. a column nothing reads is split once per different text ---------------


def oracle_timestamps(rows: int, seed: int) -> "list[str]":
    """Oracle TIMESTAMP spellings, `18-SEP-21 09.51.52.229882 PM`: a column no reader of this tool reads."""
    draw = random.Random(seed)
    months = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")
    cells: "list[str]" = []
    for _cell in range(rows):
        cells += [
            f"{draw.randint(1, 28):02d}-{months[draw.randrange(12)]}-{draw.randint(19, 24):02d} "
            f"{draw.randint(1, 12):02d}.{draw.randint(0, 59):02d}.{draw.randint(0, 59):02d}."
            f"{draw.randrange(1000000):06d} {draw.choice(('AM', 'PM'))}"
        ]
    return cells


def test_a_column_nothing_reads_is_split_once_per_different_text(tmp_path, monkeypatch) -> None:
    """One `affixed_split` per different text across the census's reading and the description's, and the same files.

    Counted through the command, where the census reads the column first
    and the description takes its kept reading over. Then the same run
    with every split worked out afresh, as before: the description and
    the twin are the same bytes. Mutation: `_split_once` not keeping its
    answer turns the count red at sixteen a text.
    """
    cells = oracle_timestamps(1000, 7)
    path = _table(tmp_path / "in", "stamps", cells)
    splits = {"calls": 0}
    split = taxonomy.affixed_split

    def counted_split(text, decimal_comma=False):
        splits["calls"] += 1
        return split(text, decimal_comma)

    monkeypatch.setattr(taxonomy, "affixed_split", counted_split)
    code, said = _profile(path, tmp_path / "once")
    assert code == 0, said
    assert splits["calls"] == len(set(cells)), (splits["calls"], len(set(cells)))
    monkeypatch.setattr(taxonomy, "_split_once", lambda cells_, text: split(text, cells_.decimal_comma))
    code, said = _profile(path, tmp_path / "afresh")
    assert code == 0, said
    for name in ("stamps-profile.json", "stamps-profile.txt", "stamps-questions.json"):
        assert (tmp_path / "once" / name).read_bytes() == (tmp_path / "afresh" / name).read_bytes(), name
    twins = {}
    for run in ("once", "afresh"):
        heard = io.StringIO()
        with contextlib.redirect_stdout(heard), contextlib.redirect_stderr(heard):
            assert cli.main(["generate", str(tmp_path / run / "stamps-profile.json"), "--seed", "4",
                             "--out-dir", str(tmp_path / run), "--replace"]) == 0, heard.getvalue()
        written = sorted((tmp_path / run).glob("*-twin.csv"))
        assert len(written) == 1, written
        twins[run] = written[0].read_bytes()
    assert twins["once"] == twins["afresh"]


def test_a_copy_of_a_reading_keeps_its_splits() -> None:
    """The kept reading `profile_column` takes over is a `dataclasses.replace` copy, and it shares the answers.

    And a reading under the other grammar never reads them: the answers
    are kept by grammar. Mutation: the memo keyed by text alone turns the
    second half red.
    """
    import dataclasses

    settings = taxonomy.Settings()
    cells = taxonomy._tally(taxonomy._classify_all(["5 mg", "7 mg", "5,5 mg"]), 3, settings)
    assert taxonomy._split_once(cells, "5,5 mg") == taxonomy.affixed_split("5,5 mg", False)
    copied = dataclasses.replace(cells, settings=taxonomy.Settings(small_cell_floor=3))
    assert copied.affixes is cells.affixes
    declared = dataclasses.replace(cells, decimal_comma=True)
    assert taxonomy._split_once(declared, "5,5 mg") == taxonomy.affixed_split("5,5 mg", True)
    assert taxonomy._split_once(cells, "5,5 mg") == taxonomy.affixed_split("5,5 mg", False)
