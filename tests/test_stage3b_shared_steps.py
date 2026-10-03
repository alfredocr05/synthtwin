"""THE SHARED STEPS OF G7.3f (stage 3b landing D0, plan P4-D366), one case each.

Landing D0 makes the weekday pass ONE pass over any census of bins, so
tracks D and T build on it rather than writing it twice: a unit of any
size with a written unit and a day (`_WeekdayPass`), the bin, what a move
keeps and a second census's group as seams, an index for steps 5 and 6,
a bounded cycle search and four new steps -- 7b CHAIN, 8.4 UNITS MERGED,
8.5 LONG PAIRS and 8.6 THE TWO-CENSUS EXCHANGE. On every date battery it
changes no twin (the identity proof is P4-D366's), so no column of dates
reaches the four steps through the whole generator, and each is frozen on
a state of ranks stated by hand in
`tests/reference/generation-branch-vectors-15.json`: the oracle
(`tools/reference/make_generation_reference_vectors.py`, which states the
steps from the method's text) wrote every answer there, and the provenance
guard rebuilds the file on every run. One clause per case, each red on its
own mutant:

* `test_an_hour_moves_inside_its_own_day` -- the whole pass with a unit
  of 3,600 seconds, minutes written and the day kept (the frozen
  hour-unit case of the plan's note M1): the census holds, every rank
  keeps its day and its place inside its hour (mutant: the kind forgets
  what a move keeps);
* `test_a_moments_day_keeps_its_clock` -- the whole pass with a unit of
  86,400 seconds: every move keeps the moment's clock (mutant: the
  indexed search drops the rank's place inside its unit);
* `test_the_index_offers_what_the_walk_offers` -- steps 5 and 6 through
  the gap's index move every rank as the walk of 400 units does (mutant:
  the index offers nothing);
* `test_a_chain_carries_a_rank_through_a_third_group` -- step 7b
  (mutant: the step withdrawn);
* `test_a_unit_merges_at_its_own_clock_first` and
  `test_a_unit_merges_onto_another_clock` -- step 8.4's two places
  (mutants: each place withdrawn);
* `test_a_long_pair_trades_two_cells` -- step 8.5 (mutant: withdrawn);
* `test_a_trade_keeps_the_second_census` -- step 8.6 (mutant: no second
  move is found);
* `test_every_cycle_up_to_seven_groups` and
  `test_three_group_cycles_above_seven` -- step 8.3's bound (mutants: the
  bound of three asked at seven groups; a bound of two);
* `test_every_case_is_asked` -- the file holds these cases and no other,
  and the oracle gives each the answer the file carries.
"""

import datetime
import importlib.util
import json
import pathlib

import pytest

from synthtwin import calendar_rules, generation

REPOSITORY = pathlib.Path(__file__).resolve().parent.parent
VECTORS = REPOSITORY / "tests" / "reference" / "generation-branch-vectors-15.json"
ORACLE = REPOSITORY / "tools" / "reference" / "make_generation_reference_vectors.py"

DAY = 86400


def _oracle():
    spec = importlib.util.spec_from_file_location("make_generation_reference_vectors_d0", ORACLE)
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def _half_month(ordinal: int) -> int:
    """Step 8.6's second census: a date's day of the month to the 15th, or after."""
    return 0 if (datetime.date(1970, 1, 1) + datetime.timedelta(days=ordinal)).day <= 15 else 1


# Each seam the file names, as the product reads it.
_BINS = {
    "weekday": calendar_rules.weekday_of,
    "weekday-of-moment": lambda ordinal: calendar_rules.weekday_of(ordinal // DAY),
    "hour": lambda ordinal: (ordinal // 3600) % 24,
    "tenth": lambda ordinal: ordinal % 10,
}
_KEEPS = {"": None, "day-of-moment": lambda ordinal: ordinal // DAY}
_PAIRS = {"": None, "half-month": _half_month}

_FILE = json.loads(VECTORS.read_text(encoding="utf-8"))


def _case(name: str) -> dict:
    return _FILE["cases"][name]


def _state(case: dict) -> generation._WeekdayPass:
    state = generation._WeekdayPass(
        moved=list(case["ordinals"]), held={}, where=list(case["where"]), facts=None,  # type: ignore[arg-type]
        word="", widths=False, kinds={}, holes=frozenset(case["holes"]), lows=list(case["lows"]),
        highs=list(case["highs"]), keep_units=case["reachable"], unit=case["unit"],
        step=case["written_unit"], day=case["day"], bin_of=_BINS[case["bin"]], period=case["period"],
        keep_of=_KEEPS[case["keep"]], pair_of=_PAIRS[case["pair"]],
    )
    for ordinal in state.moved:
        state.held[ordinal // state.step] = state.held.get(ordinal // state.step, 0) + 1
        if state.unit != state.step:
            state.units_held[ordinal // state.unit] = state.units_held.get(ordinal // state.unit, 0) + 1
    return state


def _movable(case: dict) -> "list[int]":
    return [rank for rank in range(case["body"][0], case["body"][1] + 1) if not case["pinned"][rank]]


def _holding(case: dict, moved: "list[int]", ranks) -> "list[int]":
    found = [0] * len(case["counts"])
    for rank in ranks:
        found[case["where"][_BINS[case["bin"]](moved[rank])]] += 1
    return found


def _answer(case: dict) -> list:
    """What the product's step makes of a case, in the file's own form."""
    state = _state(case)
    step = case["step"]
    if step == "settled":
        generation._bins_settled(
            state, list(case["counts"]), case["body"][0], case["body"][1], list(case["pinned"]), case["wanted"]
        )
    elif step == "chain":
        ranks = _movable(case)
        generation._weekday_chained(state, ranks, _holding(case, state.moved, ranks), list(case["want"]))
    elif step == "units_merged":
        generation._weekday_units_merged(state, case["body"][0], case["body"][1], list(case["pinned"]), case["wanted"])
    elif step == "long_pairs":
        generation._weekday_long_paired(state, case["body"][0], case["body"][1], list(case["pinned"]), case["wanted"])
    elif step == "traded":
        ranks = _movable(case)
        generation._weekday_traded(state, ranks, _holding(case, state.moved, ranks), list(case["want"]))
    else:
        cells = generation._weekday_cells(state, case["body"][0], case["body"][1], list(case["pinned"]))
        return [[giving, taking] for _cell, giving, taking in generation._weekday_cycle(state, cells, case["short"])]
    return state.moved


def _withdrawn(*_arguments, **_named):
    return None


def test_every_case_is_asked() -> None:
    """The file holds the ten cases this module asks and no other, and the oracle, run again,
    gives each the answer the file carries."""
    assert sorted(_FILE["cases"]) == sorted(
        [
            "a_chain", "a_long_pair", "a_moments_day", "a_trade", "an_hour_inside_its_day",
            "every_cycle_of_seven", "merged_at_another_clock", "merged_at_its_clock", "the_index",
            "three_group_cycles_of_ten",
        ]
    )
    oracle = _oracle()
    assert sorted(oracle.SHARED_STEP_CASES) == sorted(_FILE["cases"])
    for name, case in _FILE["cases"].items():
        assert oracle.shared_answer(case) == case["answer"], name


def test_an_hour_moves_inside_its_own_day(monkeypatch: pytest.MonkeyPatch) -> None:
    """A unit of 3,600 seconds, minutes written, the day kept: the census of hours holds, the
    count of different minutes stands, and every rank keeps its day and its place inside its
    hour. Mutant: the kind forgets what a move keeps, and early ranks go to the evening before."""
    case = _case("an_hour_inside_its_day")
    moved = _answer(case)
    assert moved == case["answer"]
    assert _holding(case, moved, range(len(moved))) == case["counts"]
    assert len({ordinal // 60 for ordinal in moved}) == case["wanted"]
    assert sorted(ordinal // DAY for ordinal in moved) == sorted(ordinal // DAY for ordinal in case["ordinals"])
    assert sorted(ordinal % 3600 for ordinal in moved) == sorted(ordinal % 3600 for ordinal in case["ordinals"])
    monkeypatch.setattr(generation, "_weekday_kind", lambda state, ordinal: generation._PLAIN_KIND)
    assert _answer(case) != case["answer"]


def test_a_moments_day_keeps_its_clock(monkeypatch: pytest.MonkeyPatch) -> None:
    """A unit of a day of moments: the census holds and every moved moment keeps its clock to the
    second. Mutant: the indexed search drops the rank's place inside its unit."""
    case = _case("a_moments_day")
    moved = _answer(case)
    assert moved == case["answer"]
    assert _holding(case, moved, range(len(moved))) == case["counts"]
    assert sorted(ordinal % DAY for ordinal in moved) == sorted(ordinal % DAY for ordinal in case["ordinals"])
    window = generation._weekday_window

    def midnight(state, rank):
        unit, _place, first, last = window(state, rank)
        return unit, 0, first, last

    monkeypatch.setattr(generation, "_weekday_window", midnight)
    assert _answer(case) != case["answer"]


def test_the_index_offers_what_the_walk_offers(monkeypatch: pytest.MonkeyPatch) -> None:
    """Steps 5 and 6 through each gap's index (the 3b.3 skeptic's minor 1) move every rank as
    the walk of 400 units each side does, and the index is asked. Mutant: it offers nothing."""
    case = _case("the_index")
    asked: "list[int]" = []
    single = generation._weekday_single_indexed

    def counted(*arguments):
        asked.append(1)
        return single(*arguments)

    monkeypatch.setattr(generation, "_weekday_single_indexed", counted)
    assert _answer(case) == case["answer"]
    assert asked
    monkeypatch.setattr(generation, "_weekday_index", lambda state, low, high: None)
    assert _answer(case) == case["answer"]
    monkeypatch.undo()
    monkeypatch.setattr(generation, "_weekday_single_indexed", _withdrawn)
    assert _answer(case) != case["answer"]


def test_a_chain_carries_a_rank_through_a_third_group(monkeypatch: pytest.MonkeyPatch) -> None:
    """Step 7b: Monday is two over and the last group two under, and no Monday rank's gap holds a
    day of it, so two paths Monday to Tuesday to Wednesday put the totals right. Mutant: the
    step withdrawn."""
    case = _case("a_chain")
    moved = _answer(case)
    assert moved == case["answer"]
    assert _holding(case, moved, _movable(case)) == case["want"]
    monkeypatch.setattr(generation, "_weekday_chained", _withdrawn)
    assert _answer(case) != case["answer"]


def test_a_unit_merges_at_its_own_clock_first(monkeypatch: pytest.MonkeyPatch) -> None:
    """Step 8.4 (the 3b.2-W skeptic, minor 2): a moment alone at 10:17:05 merges onto the held
    10:17:05 a week later, not onto the nearer 14:00:00. Mutant: the same-clock place withdrawn."""
    case = _case("merged_at_its_clock")
    moved = _answer(case)
    assert moved == case["answer"]
    assert len(set(moved)) == case["wanted"]
    assert sorted(ordinal % DAY for ordinal in moved) == sorted(ordinal % DAY for ordinal in case["ordinals"])
    monkeypatch.setattr(generation, "_weekday_merge_same_clock", _withdrawn)
    assert _answer(case) != case["answer"]


def test_a_unit_merges_onto_another_clock(monkeypatch: pytest.MonkeyPatch) -> None:
    """Step 8.4 where no held moment shares the clock: the nearest held moment of its group that is
    not a midnight takes it. Mutant: that place withdrawn, and the count stays long."""
    case = _case("merged_at_another_clock")
    moved = _answer(case)
    assert moved == case["answer"]
    assert len(set(moved)) == case["wanted"]
    monkeypatch.setattr(generation, "_weekday_merge_any_clock", _withdrawn)
    assert _answer(case) != case["answer"]


def test_a_long_pair_trades_two_cells(monkeypatch: pytest.MonkeyPatch) -> None:
    """Step 8.5 (landing 3b.6's step): the lone Saturday joins the held Monday of its cell, and a
    Tuesday rank of the other cell joins its held Saturday, so each group keeps its count and
    the count falls by one. Mutant: the step withdrawn."""
    case = _case("a_long_pair")
    moved = _answer(case)
    assert moved == case["answer"]
    assert len(set(moved)) == case["wanted"]
    assert _holding(case, moved, range(len(moved))) == _holding(case, case["ordinals"], range(len(moved)))
    monkeypatch.setattr(generation, "_weekday_long_paired", _withdrawn)
    assert _answer(case) != case["answer"]


def test_a_trade_keeps_the_second_census(monkeypatch: pytest.MonkeyPatch) -> None:
    """Step 8.6 (the 3b.3 skeptic's blocker 1 (b)): the Saturday the weekend owes back reaches a
    weekday only in the other half of the month, so a Monday crosses the 15th the other way and
    both halves keep their counts. Mutant: no second move is found, and nothing trades."""
    case = _case("a_trade")
    moved = _answer(case)
    assert moved == case["answer"]
    assert _holding(case, moved, _movable(case)) == case["want"]
    assert sorted(_half_month(ordinal) for ordinal in moved) == sorted(
        _half_month(ordinal) for ordinal in case["ordinals"]
    )
    monkeypatch.setattr(generation, "_weekday_ways_back", lambda state, ranks: {})
    assert _answer(case) != case["answer"]


def test_every_cycle_up_to_seven_groups(monkeypatch: pytest.MonkeyPatch) -> None:
    """Step 8.3 on seven groups asks every cycle: only Monday, Tuesday, Wednesday, Thursday and
    back gains. Mutant: the bound of three groups asked at seven too, and no cycle is found."""
    case = _case("every_cycle_of_seven")
    assert _answer(case) == case["answer"] == [[0, 1], [1, 2], [2, 3], [3, 0]]
    monkeypatch.setattr(generation, "_WEEKDAY_CYCLE_GROUPS", 3)
    assert _answer(case) == []


def test_three_group_cycles_above_seven(monkeypatch: pytest.MonkeyPatch) -> None:
    """Step 8.3 on ten groups asks cycles of at most three: the one through groups 0, 1 and 2 is
    found. Mutant: a bound of two groups, and none is."""
    case = _case("three_group_cycles_of_ten")
    assert _answer(case) == case["answer"] == [[0, 1], [1, 2], [2, 0]]
    monkeypatch.setattr(generation, "_WEEKDAY_CYCLE_LONGEST", 2)
    assert _answer(case) == []
