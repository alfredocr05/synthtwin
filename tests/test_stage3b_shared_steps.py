"""THE SHARED STEPS OF G7.3f (stage 3b landing D0, plan P4-D366), one case each.

Landing D0 makes the weekday pass ONE pass over any census of bins, so
tracks D and T build on it rather than writing it twice: a unit of any
size with a written unit and a day (`_WeekdayPass`), the bin, what a move
keeps and a second census's group as seams, an index for steps 5 and 6,
a bounded cycle search and four new steps -- 7b CHAIN, 8.4 UNITS MERGED,
8.5 LONG PAIRS and 8.6 THE TWO-CENSUS EXCHANGE.

WHERE A COLUMN OF DATES REACHES THEM (P4-D366's proof, as the review of
the landing measured it, item 1). At the default floor of 11 none does:
on 4,782 tables of the date batteries, 15,152 twins are byte-identical to
110cb46's and no rank moves in the four steps. At a floor of 36 eight of
15,152 twins move -- `monthly3`, `sched120` and `sparse80` columns whose
count of different values 110cb46 already left LONG, steps 8.4 and 8.5
merging one or two of its values -- and each comes nearer the published
count, with the same checks missed. `test_a_schedule_at_floor_36_reaches_step_8_5`
holds one of them. So every step and clause is frozen on a state of ranks
stated by hand in `tests/reference/generation-branch-vectors-15.json`:
the oracle (`tools/reference/make_generation_reference_vectors.py`, which
states the steps from the method's text) wrote every answer there, and
the provenance guard rebuilds the file on every run.

The cases and their clauses:

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
* the review's cases (items 3 to 5): each new step once through the whole
  pass (`_bins_settled`), and a state for every clause a reviewer's
  mutant changed with every case above still passing -- a run keeping its
  clock, the index's tie and reach, step 3's prior on hours, a day step 6
  empties, step 7b's search, step 8.2's stop, step 8.3's cycle undone,
  step 8.4's ties, window, alone-only rule and second round, step 8.5's
  one-long count, hole, nearest gap, repeats and emptied units, and step
  8.6's order, groups at their total, kept day and two reaches. Each test
  holds the product to the file and states what the case shows;
  `test_each_clause_is_red_on_its_mutant` turns each red on its own
  source edit of the product (`REVIEW_MUTANTS`, the reviewer's ids);
* the second review's cases (its item 1): a state for each line the
  repair added whose mutant changed an answer while every case above
  still held -- step 8.2's round asking its runs as they stood, step
  8.5's stop at the most the count allows, the rank its tables list on
  the unit it joins, its count of a unit's holders across the column and
  its distance from the gaps' first places, and step 8.3's cycle undone
  last move first -- each red on that review's mutant (N01, N04, N06,
  N10, N13 and N14; the review's other mutants of the repair's lines
  were already red on this file's other tests, all but N07, which is
  the same pass);
* the Codex review's cases (its item 1): step 8.3's gain counts the
  WRITTEN units its mover can take at its own place inside its unit --
  Codex's own state of forty ranks each at 00:15, 01:15 and 02:30, and a
  free second on a held day -- each step's mover is the rank on the
  written unit holding the most, a place past the gap is no take (the
  two states the landing's reviews froze a cycle undone on now offer no
  cycle), and a cycle is still undone, last move first, where a move
  made changes the mover of the next (`a_cycle_undone` and
  `a_cycle_undone_last_move_first`, restated): C1a to C1d in the mutant
  table, and M83 and N14 on the restated states;
* `test_the_body_is_full_only_where_every_unit_the_census_counts_holds_a_rank`
  -- the test the short cause asks (the review's M65), and
  `test_the_body_counts_a_unit_a_move_empties` -- the review's M09 and
  M10 on the count of each unit's ranks, which only that test reads;
* `test_a_schedule_at_floor_36_reaches_step_8_5`,
  `test_a_count_left_long_is_named_long` and
  `test_a_cause_stands_only_where_the_recount_went_its_way` -- a column
  of the batteries through the whole generator, and the report's cause;
* `test_every_case_is_asked` -- the file holds these cases and no other,
  and the oracle gives each the answer the file carries.
"""

import datetime
import importlib.util
import json
import pathlib
import sys
import types

import pytest

from synthtwin import generation

REPOSITORY = pathlib.Path(__file__).resolve().parent.parent
VECTORS = REPOSITORY / "tests" / "reference" / "generation-branch-vectors-15.json"
ORACLE = REPOSITORY / "tools" / "reference" / "make_generation_reference_vectors.py"
SOURCE = pathlib.Path(generation.__file__).read_text(encoding="utf-8")

DAY = 86400
HOUR = 3600


def _oracle():
    spec = importlib.util.spec_from_file_location("make_generation_reference_vectors_d0", ORACLE)
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def _half_month(ordinal: int) -> int:
    """Step 8.6's second census: a date's day of the month to the 15th, or after."""
    return 0 if (datetime.date(1970, 1, 1) + datetime.timedelta(days=ordinal)).day <= 15 else 1


_FILE = json.loads(VECTORS.read_text(encoding="utf-8"))


def _case(name: str) -> dict:
    return _FILE["cases"][name]


def _state(case: dict, module=generation):
    state = module._WeekdayPass(
        moved=list(case["ordinals"]), held={}, where=list(case["where"]), facts=None,
        word="", widths=False, kinds={}, holes=frozenset(case["holes"]), lows=list(case["lows"]),
        highs=list(case["highs"]), keep_units=case["reachable"], unit=case["unit"],
        step=case["written_unit"], day=case["day"], bins=case["bin"], period=case["period"],
        keeps=case["keep"], pairs=case["pair"], pair_where=tuple(case["pair_where"]),
    )
    for ordinal in state.moved:
        module._weekday_tally(state.held, ordinal // state.step, 1)
        if state.unit != state.step:
            module._weekday_tally(state.units_held, ordinal // state.unit, 1)
    return state


def _movable(case: dict) -> "list[int]":
    return [rank for rank in range(case["body"][0], case["body"][1] + 1) if not case["pinned"][rank]]


def _holding(case: dict, moved: "list[int]", ranks) -> "list[int]":
    state = _state(case)
    found = [0] * len(case["counts"])
    for rank in ranks:
        found[generation._weekday_group(state, moved[rank])] += 1
    return found


def _answer(case: dict, module=generation) -> list:
    """What the product's step makes of a case, in the file's own form."""
    state = _state(case, module)
    step = case["step"]
    low, high, pinned = case["body"][0], case["body"][1], list(case["pinned"])
    if step == "settled":
        module._bins_settled(state, list(case["counts"]), low, high, pinned, case["wanted"])
    elif step == "chain":
        ranks = _movable(case)
        module._weekday_chained(state, ranks, _holding(case, state.moved, ranks), list(case["want"]))
    elif step == "units_merged":
        module._weekday_units_merged(state, low, high, pinned, case["wanted"])
    elif step == "long_pairs":
        module._weekday_long_paired(state, low, high, pinned, case["wanted"])
    elif step == "traded":
        ranks = _movable(case)
        module._weekday_traded(state, ranks, _holding(case, state.moved, ranks), list(case["want"]))
    elif step == "repaired":
        module._weekday_repaired(state, low, high, pinned, case["wanted"])
    elif step == "exchanged":
        module._weekday_exchanged(state, low, high, pinned, case["wanted"])
    elif step == "singles":
        # Steps 5 and 6 on the case's one gap, through its index as the pass builds it.
        ranks = _movable(case)
        assert len({(case["lows"][rank], case["highs"][rank]) for rank in ranks}) == 1
        state.gap_sizes[(case["lows"][ranks[0]], case["highs"][ranks[0]])] = len(ranks)
        have, want = _holding(case, state.moved, ranks), list(case["want"])
        module._weekday_runs_moved(state, ranks, have, want)
        module._weekday_singles_moved(state, ranks, have, want, module._WEEKDAY_SINGLE_ROUNDS, False)
    elif step == "prior":
        gaps = sorted({(case["lows"][rank], case["highs"][rank]) for rank in _movable(case)})
        return [module._weekday_prior(state, first, last, len(case["counts"])) for first, last in gaps]
    else:
        cells = module._weekday_cells(state, low, high, pinned)
        return [[giving, taking] for _cell, giving, taking in module._weekday_cycle(state, cells, case["short"])]
    return state.moved


def _withdrawn(*_arguments, **_named):
    return None


def _mutant(monkeypatch: pytest.MonkeyPatch, before: str, after: str):
    """The product's generation module with ONE source edit, built beside it: a reviewer's
    mutant, applied exactly once (an edit that no longer applies turns the test red)."""
    assert SOURCE.count(before) == 1, before
    name = "synthtwin._generation_mutant"
    module = types.ModuleType(name)
    module.__file__ = generation.__file__
    monkeypatch.setitem(sys.modules, name, module)
    exec(compile(SOURCE.replace(before, after), generation.__file__, "exec"), module.__dict__)
    return module


def _clock(ordinal: int) -> int:
    return ordinal % DAY


CASES = [
    "a_chain", "a_long_pair", "a_moments_day", "a_trade", "an_hour_inside_its_day",
    "every_cycle_of_seven", "merged_at_another_clock", "merged_at_its_clock", "the_index",
    "three_group_cycles_of_ten",
    # the review's (review of landing 3b.D0, items 3 to 5)
    "a_chain_in_order", "a_chain_in_the_pass", "a_cycle_undone", "a_day_freed_for_a_cycle",
    "a_long_pair_in_the_pass", "a_long_pair_one_long", "a_moments_run", "a_trade_back_31",
    "a_trade_in_the_pass", "a_trade_of_hours", "a_trade_reaching_62", "an_hour_run",
    "long_pairs_leave_an_emptied_unit", "long_pairs_twice", "merged_in_a_second_round",
    "merged_in_the_pass", "merged_inside_the_shared_gap", "merged_only_alone", "merged_ties",
    "runs_merged_until_the_count_is_back", "the_index_reach", "the_index_tie",
    "the_prior_of_hours", "trades_in_rank_order",
    # the second review's (its item 1)
    "a_cycle_undone_last_move_first", "a_long_pair_by_first_places", "a_long_pair_by_two_first",
    "long_pairs_count_the_pinned_rank", "long_pairs_move_a_joined_rank_again", "runs_merged_in_one_round",
    # the Codex review's (its item 1)
    "a_chains_mover_holds_the_most", "a_cycles_mover_holds_the_most", "a_free_second_on_a_held_day",
    "a_link_past_its_gap", "a_place_past_the_gap_offers_no_cycle",
    "a_third_place_past_its_gap_offers_no_cycle", "written_units_free_in_held_hours",
]


def test_every_case_is_asked() -> None:
    """The file holds the cases this module asks and no other, every one asked by a test here,
    and the oracle, run again, gives each the answer the file carries."""
    assert sorted(_FILE["cases"]) == sorted(CASES)
    named = {case_name for case_name, _before, _after in REVIEW_MUTANTS.values()}
    source = pathlib.Path(__file__).read_text(encoding="utf-8")
    for name in CASES:
        assert f'_case("{name}")' in source or name in named, name
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
    """Step 8.3 on ten groups of the days of the month asks cycles of at most three: the one
    through groups 0, 1 and 2 is found. Mutant: a bound of two groups, and none is."""
    case = _case("three_group_cycles_of_ten")
    assert _answer(case) == case["answer"] == [[0, 1], [1, 2], [2, 0]]
    monkeypatch.setattr(generation, "_WEEKDAY_CYCLE_LONGEST", 2)
    assert _answer(case) == []


# -- the review's cases (review of landing 3b.D0, items 3 to 5) -----------------------------


def _date(ordinal: int) -> datetime.date:
    return datetime.date(1970, 1, 1) + datetime.timedelta(days=ordinal)


def test_a_run_keeps_its_clock() -> None:
    """Step 5 moves a run of two whole at its place inside its unit (the review's M48 and M49).
    On a day of moments Wednesday's two at 10:00:00 go to the Sunday before at 10:00:00 -- the
    Saturday after stands as near, and the Sunday's midnight holds a rank; on a unit of an hour
    two ranks at 10:30 go to 12:30, beside a rank at 12:00."""
    case = _case("a_moments_run")
    moved = _answer(case)
    assert moved == case["answer"]
    assert _holding(case, moved, range(len(moved))) == case["counts"]
    assert moved.count(case["ordinals"][0] + 10 * HOUR) == 2
    assert len(set(moved)) == case["wanted"]
    hour = _case("an_hour_run")
    moved = _answer(hour)
    assert moved == hour["answer"]
    assert _holding(hour, moved, range(len(moved))) == hour["counts"]
    assert moved.count(hour["ordinals"][0] + 12 * HOUR + 30 * 60) == 2
    assert hour["ordinals"][0] + 12 * HOUR in moved
    assert sorted(ordinal // DAY for ordinal in moved) == sorted(ordinal // DAY for ordinal in hour["ordinals"])


def test_the_index_takes_the_earlier_of_two_as_near(monkeypatch: pytest.MonkeyPatch) -> None:
    """Steps 5 and 6 through the gap's index (the review's M15): the Wednesday's two weekend days
    three days away, the Sunday before and the Saturday after, are both free, and the Sunday is
    taken, as the walk takes it. The index is asked."""
    case = _case("the_index_tie")
    asked: "list[int]" = []
    single = generation._weekday_single_indexed

    def counted(*arguments):
        asked.append(1)
        return single(*arguments)

    monkeypatch.setattr(generation, "_weekday_single_indexed", counted)
    moved = _answer(case)
    assert moved == case["answer"]
    assert asked
    assert moved[1] == case["ordinals"][1] - 3
    assert _date(moved[1]).weekday() == 6


def test_the_index_reaches_400_units_and_no_further() -> None:
    """Steps 5 and 6's reach through the index (the review's M19): the one 31st of the gap that is
    no hole stands 401 days below the rank, and no move is offered."""
    case = _case("the_index_reach")
    assert _answer(case) == case["answer"] == case["ordinals"]
    free = [
        day for day in range(case["lows"][1], case["ordinals"][1])
        if _date(day).day == 31 and day not in case["holes"]
    ]
    assert free == [case["ordinals"][1] - 401]


def test_the_prior_leaves_out_every_hour_of_a_holes_day() -> None:
    """Step 3's prior on a unit of an hour (the review's M12 and M13): a gap from Tuesday 06:00 to
    Friday 18:00, Tuesday and Thursday holes. Wednesday's 24 hours count and Friday's to 18:00,
    Friday's 18:00 at half, and no hour of a hole's day, the gap's first at half included: 24
    hours of [00-11] and 18.5 of [12-23], at the share scale."""
    case = _case("the_prior_of_hours")
    scale = generation._WEEKDAY_SCALE
    assert _answer(case) == case["answer"] == [[24 * scale, 37 * scale // 2]]


def test_a_day_step_6_empties_is_free_to_step_8_3() -> None:
    """Step 8.3 counts a unit free once the ranks on it have left (the review's M09 and M10): step
    6 moves the first gap's Tuesday moment to the Friday, and the cycle Tuesday to Thursday and
    back puts a Thursday moment on that Tuesday at 07:08:34 and the second gap's Tuesday on a
    Thursday. Every group keeps its count, and the count of different moments gains one."""
    case = _case("a_day_freed_for_a_cycle")
    moved = _answer(case)
    assert moved == case["answer"]
    assert _holding(case, moved, range(len(moved))) == case["counts"]
    assert len(set(moved)) == len(set(case["ordinals"])) + 1
    assert (case["ordinals"][1] // DAY) * DAY + 7 * HOUR + 8 * 60 + 34 in moved


def test_step_7b_searches_breadth_first_through_each_links_first_cell() -> None:
    """Step 7b's search (the review's M20 and M21): Monday, Tuesday and Wednesday over and Friday
    under; breadth first, Tuesday reaches Friday before Wednesday does, through its first cell,
    so the first Tuesday moves to the Friday -- not the Wednesday, not the second Tuesday."""
    case = _case("a_chain_in_order")
    moved = _answer(case)
    assert moved == case["answer"]
    assert [rank for rank in range(len(moved)) if moved[rank] != case["ordinals"][rank]] == [1]
    assert moved[1] == case["ordinals"][0] + 4


def test_step_7b_runs_in_the_whole_pass(monkeypatch: pytest.MonkeyPatch) -> None:
    """Step 7b through `_bins_settled` (the review's M60): Wednesday's 08:00 reaches no hour of
    [18-23] on its own day, so the chain moves it to 12:00 and Tuesday's 13:00 to 18:00, and the
    census holds, every rank on its own day. Withdrawn, the census is missed."""
    case = _case("a_chain_in_the_pass")
    moved = _answer(case)
    assert moved == case["answer"]
    assert _holding(case, moved, range(len(moved))) == case["counts"]
    assert sorted(ordinal // DAY for ordinal in moved) == sorted(ordinal // DAY for ordinal in case["ordinals"])
    monkeypatch.setattr(generation, "_weekday_chained", _withdrawn)
    withdrawn = _answer(case)
    assert _holding(case, withdrawn, range(len(withdrawn))) != case["counts"]


def test_step_8_2_stops_once_the_count_is_back() -> None:
    """Step 8.2, its count kept rather than counted again (the repair's M75): the first Monday's run
    joins the second's and the count is back, so the third Monday's run stays."""
    case = _case("runs_merged_until_the_count_is_back")
    moved = _answer(case)
    assert moved == case["answer"]
    assert len(set(moved)) == case["wanted"]
    assert moved.count(case["ordinals"][3]) == 4


def _made(monkeypatch: pytest.MonkeyPatch, case: dict, module=generation) -> "tuple[list[int], list[int]]":
    """A case's answer, and the rank each move of steps 7b and 8.3 took (-1 where none moved)."""
    made: "list[int]" = []
    moved_one = module._weekday_cell_moved

    def recorded(*arguments):
        nonlocal made
        found = moved_one(*arguments)
        made += [found[0]]
        return found

    monkeypatch.setattr(module, "_weekday_cell_moved", recorded)
    return _answer(case, module), made


def test_a_cycle_is_made_whole_or_not_at_all(monkeypatch: pytest.MonkeyPatch) -> None:
    """Step 8.3's cycle, made whole or not at all (the repair; M83 leaves it half made). A move can
    find no place where an earlier move of its cycle changed its group's mover (the Codex review,
    item 1: the gain is asked of each group's mover before the cycle is made): a Tuesday moment
    goes to Sunday 10:01:05 and, the lower rank of Sunday's two lone moments, is Sunday's mover;
    Thursday 10:01:05 stands past the gap's close, so it goes back: every group keeps its count,
    and nothing has moved."""
    case = _case("a_cycle_undone")
    answer, made = _made(monkeypatch, case)
    assert answer == case["answer"] == case["ordinals"]
    assert made == [0, -1]


def test_a_cycle_whose_move_has_no_place_is_not_asked(monkeypatch: pytest.MonkeyPatch) -> None:
    """Step 8.3 asks a pair's take of its mover's own places, inside its gap (the Codex review,
    item 1): the two states the landing's reviews froze a cycle undone on now offer no cycle, a
    weekday at 10:00:00 standing outside the first gap of one and Monday 22:00:00 past the second
    gap's close of the other, and no move is tried. Mutant: the take counts places past its gap,
    and each cycle is made and undone again."""
    for case, undone in (
        (_case("a_place_past_the_gap_offers_no_cycle"), [4, -1]),
        (_case("a_third_place_past_its_gap_offers_no_cycle"), [1, 1, -1]),
    ):
        answer, made = _made(monkeypatch, case)
        assert answer == case["answer"] == case["ordinals"], case["why"]
        assert made == [], case["why"]
        mutant = _mutant(monkeypatch, *REVIEW_MUTANTS["C1b_take_ignores_the_gap"][1:])
        answer, made = _made(monkeypatch, case, mutant)
        assert answer == case["ordinals"] and made == undone, case["why"]
        monkeypatch.undo()


def test_step_8_3_counts_the_written_units_its_mover_can_take() -> None:
    """Step 8.3's gain is asked of written units at its mover's place (the Codex review, item 1).
    Codex's own state: forty ranks each at 00:15, 01:15 and 02:30, asked for eighty in hour 1,
    forty in hour 2 and three values, keep three and the census -- 80 at 01:15, 1 at 02:15 and 39
    at 02:30 -- where asking whether a whole hour stood free left 80 at 01:15 and 40 at 02:30, two
    values. On a day of moments, Tuesday 10:01:30 and Wednesday 10:00:00 stand free though each day
    holds a moment, and the count gains one. Mutant: the take asks whether the unit is free."""
    case = _case("written_units_free_in_held_hours")
    moved = _answer(case)
    assert moved == case["answer"]
    assert _holding(case, moved, range(len(moved))) == case["counts"]
    assert len({ordinal // 60 for ordinal in moved}) == case["wanted"] == 3
    assert sorted({ordinal % DAY for ordinal in moved}) == [HOUR + 15 * 60, 2 * HOUR + 15 * 60, 2 * HOUR + 30 * 60]
    seconds = _case("a_free_second_on_a_held_day")
    moved = _answer(seconds)
    assert moved == seconds["answer"]
    assert len(set(moved)) == len(set(seconds["ordinals"])) + 1
    assert _holding(seconds, moved, range(len(moved))) == seconds["counts"]


def test_the_mover_is_the_rank_on_the_written_unit_holding_the_most() -> None:
    """Steps 7b and 8.3 ask a group's take of its MOVER, the rank its move takes (the Codex review,
    item 1). Step 8.3: a Monday moment sharing its second goes to Tuesday 10:01:05 and the count
    gains one, where the lone Thursday moment, stated first, gains nothing. Step 7b: a Wednesday
    10:01:30 moment, held twice, has a Monday place inside the gap and goes there, where Wednesday
    10:00:00, stated first, has none. Step 7b's link asks the mover's places inside its gap too:
    Saturday 10:01:30 stands past the first gap's close, so a Tuesday moment of the second gap goes
    to the Sunday before it. Mutants: each mover the first rank stated, and the take past its gap."""
    case = _case("a_cycles_mover_holds_the_most")
    moved = _answer(case)
    assert moved == case["answer"]
    assert moved[1] == case["ordinals"][1] + DAY and moved[0] == case["ordinals"][0]
    case = _case("a_chains_mover_holds_the_most")
    moved = _answer(case)
    assert moved == case["answer"]
    assert moved[1] == case["ordinals"][1] - 2 * DAY
    assert _holding(case, moved, _movable(case)) == case["want"]
    case = _case("a_link_past_its_gap")
    moved = _answer(case)
    assert moved == case["answer"]
    assert moved[1] == case["ordinals"][1] - 2 * DAY and moved[0] == case["ordinals"][0]
    assert _holding(case, moved, _movable(case)) == case["want"]


def test_step_8_4_takes_the_earlier_tie_and_keeps_a_midnight_apart() -> None:
    """Step 8.4's ties and its midnight (the review's M25, M26 and M27): Wednesday's lone 10:00:00
    joins Monday's 10:00:00, not Friday's as near; the next Wednesday's 10:30:00 joins its own
    day's 08:30:00, not 12:30:00 as near; the third Wednesday's 10:45:00 joins Thursday's 09:00:00,
    not its own day's midnight, nearer."""
    case = _case("merged_ties")
    moved = _answer(case)
    assert moved == case["answer"]
    assert len(set(moved)) == case["wanted"]
    monday = case["ordinals"][0] // DAY + 1
    assert moved[3] == monday * DAY + 10 * HOUR
    assert moved[8] == (monday + 9) * DAY + 8 * HOUR + 30 * 60
    assert moved[13] == (monday + 17) * DAY + 9 * HOUR


def test_step_8_4_moves_a_unit_inside_the_gap_its_ranks_share() -> None:
    """Step 8.4's window (the review's M24): the two ranks on one Monday, whose gaps start eleven
    days apart, move to the Monday after, inside both gaps, not to the Monday before, as near."""
    case = _case("merged_inside_the_shared_gap")
    moved = _answer(case)
    assert moved == case["answer"]
    assert moved[4] == moved[5] == case["ordinals"][4] + 7
    assert case["lows"][5] > case["ordinals"][4] - 7 >= case["lows"][4]


def test_step_8_4_asks_a_unit_only_while_it_holds_its_own_ranks() -> None:
    """Step 8.4's rule that a unit moves only while it holds its own ranks and no other (the
    review's M52): the second Monday, holding the first's rank too once it has merged, is passed
    over, and the third Monday's two join it."""
    case = _case("merged_only_alone")
    moved = _answer(case)
    assert moved == case["answer"]
    assert moved.count(case["ordinals"][2]) == 4
    assert len(set(moved)) == case["wanted"]


def test_step_8_4_merges_again_in_a_second_round() -> None:
    """Step 8.4's rounds (the review's M61): the first round merges the first Monday onto the
    second; the second merges those two onto the third, which no unit reached in the first."""
    case = _case("merged_in_a_second_round")
    moved = _answer(case)
    assert moved == case["answer"]
    assert len(set(moved)) == case["wanted"]
    assert moved[1] == moved[2] == case["ordinals"][4]


def test_step_8_4_runs_in_the_whole_pass(monkeypatch: pytest.MonkeyPatch) -> None:
    """Step 8.4 through `_bins_settled`: the census moves a Monday moment to the Sunday before, the
    count one long, and the Monday moment left alone joins Tuesday's 14:00:00. Withdrawn, the
    count stays long."""
    case = _case("merged_in_the_pass")
    moved = _answer(case)
    assert moved == case["answer"]
    assert _holding(case, moved, range(len(moved))) == case["counts"]
    assert len(set(moved)) == case["wanted"]
    monkeypatch.setattr(generation, "_weekday_units_merged", _withdrawn)
    assert len(set(_answer(case))) == case["wanted"] + 1


def test_step_8_5_falls_by_one_where_the_count_is_one_long_and_never_onto_a_hole() -> None:
    """Step 8.5 with the count one long (the review's M28 and M53): the second gap's lone Monday,
    which would take the count down by two, is not asked; a Wednesday held twice is. The first
    gap's lone Saturday joins its Tuesday, not its Monday, a hole."""
    case = _case("a_long_pair_one_long")
    moved = _answer(case)
    assert moved == case["answer"]
    assert len(set(moved)) == case["wanted"]
    assert moved[5] == case["ordinals"][3] and moved[5] not in case["holes"]
    assert moved[7] == case["ordinals"][7]


def test_step_8_5_pairs_with_the_nearer_gap_and_keeps_its_tables() -> None:
    """Step 8.5 twice (the review's M29 and M63; the repair's tables, M70 and M72): the third gap's
    Saturday pairs with the second gap, the nearer, not the first, the earlier; then the second
    gap's Monday, held once now, pairs with the first gap; the count comes back exactly."""
    case = _case("long_pairs_twice")
    moved = _answer(case)
    assert moved == case["answer"]
    assert len(set(moved)) == case["wanted"]
    everything = range(len(moved))
    assert _holding(case, moved, everything) == _holding(case, case["ordinals"], everything)
    assert moved[13] == case["ordinals"][11]
    assert moved[6] == moved[7] == case["ordinals"][8]


def test_step_8_5_forgets_a_unit_it_empties() -> None:
    """Step 8.5's tables (the repair's M73): the first gap's Saturday, emptied by the first pair, is
    no place for the third gap's Saturday to pair with, and the count stays one long."""
    case = _case("long_pairs_leave_an_emptied_unit")
    moved = _answer(case)
    assert moved == case["answer"]
    assert len(set(moved)) == case["wanted"] + 1
    assert case["ordinals"][3] not in moved


def test_step_8_5_runs_in_the_whole_pass(monkeypatch: pytest.MonkeyPatch) -> None:
    """Step 8.5 through `_bins_settled`: no held day of its own group stands in either gap, so no
    step before it merges, and the lone Saturday joins the Friday and a Monday rank the other
    gap's Saturday. Withdrawn, the count stays long."""
    case = _case("a_long_pair_in_the_pass")
    moved = _answer(case)
    assert moved == case["answer"]
    assert _holding(case, moved, range(len(moved))) == case["counts"]
    assert len(set(moved)) == case["wanted"]
    monkeypatch.setattr(generation, "_weekday_long_paired", _withdrawn)
    assert len(set(_answer(case))) == case["wanted"] + 1


def test_step_8_6_asks_its_ranks_in_order() -> None:
    """Step 8.6's order and its trades (the review's M31 and M64): the Monday's trade, four days,
    ends the first asking before the 14th's, one day, is asked; the second trade is the 14th's,
    and the 21st stays."""
    case = _case("trades_in_rank_order")
    moved = _answer(case)
    assert moved == case["answer"]
    assert _holding(case, moved, _movable(case)) == case["want"]
    assert [moved[rank] - case["ordinals"][rank] for rank in (1, 4, 7)] == [4, 1, 0]


def test_step_8_6_keeps_the_day_and_never_fills_a_group_past_its_total() -> None:
    """Step 8.6 on a unit of an hour (the review's M42 and M56): 23:00 the evening before is
    another day and 08:00 a group at its total, both nearer; the rank goes to 16:00 of its day."""
    case = _case("a_trade_of_hours")
    moved = _answer(case)
    assert moved == case["answer"]
    assert moved[1] == (case["ordinals"][1] // DAY) * DAY + 16 * HOUR
    assert _holding(case, moved, _movable(case)) == case["want"]


def test_step_8_6_reaches_62_units_and_its_second_move_31() -> None:
    """Step 8.6's two reaches (the review's M32 and M33): 30 May 2024 goes to 31 July, 62 days on;
    and for Saturday the 16th to cross to Friday the 15th, Friday 1 March crosses back to
    Tuesday 30 January, 31 days below."""
    case = _case("a_trade_reaching_62")
    moved = _answer(case)
    assert moved == case["answer"]
    assert moved[1] - case["ordinals"][1] == 62
    back = _case("a_trade_back_31")
    moved = _answer(back)
    assert moved == back["answer"]
    assert back["ordinals"][1] - moved[1] == 31
    assert moved[3] == back["ordinals"][3] - 1
    assert sorted(_half_month(ordinal) for ordinal in moved) == sorted(
        _half_month(ordinal) for ordinal in back["ordinals"]
    )


def test_step_8_6_runs_in_the_whole_pass_and_the_count_after_it(monkeypatch: pytest.MonkeyPatch) -> None:
    """Step 8.6 through `_bins_settled` (the review's M58): Saturday the 16th crosses to the held
    Friday the 15th and Thursday the 14th crosses to Monday the 18th, the count one short; steps
    8.1 to 8.5 run again and a Tuesday rank goes to Wednesday the 6th, so the census, both halves
    of the month and the count all hold. With the trade withdrawn the census is missed."""
    case = _case("a_trade_in_the_pass")
    moved = _answer(case)
    assert moved == case["answer"]
    assert _holding(case, moved, range(len(moved))) == case["counts"]
    assert len(set(moved)) == case["wanted"]
    assert sorted(_half_month(ordinal) for ordinal in moved) == sorted(
        _half_month(ordinal) for ordinal in case["ordinals"]
    )
    monkeypatch.setattr(generation, "_weekday_traded", lambda *arguments: False)
    withdrawn = _answer(case)
    assert _holding(case, withdrawn, range(len(withdrawn))) != case["counts"]


# -- the second review's cases (review of landing 3b.D0, its second round, item 1) ----------


def test_step_8_2_asks_a_round_of_runs_as_they_stood() -> None:
    """Step 8.2's count kept a run at a time (the second review's N01): three Mondays held twice,
    twice and five times, the count two long. The first Monday's two join the second's; the
    second, holding four now, is not asked again in that round, and the third's five join it, the
    nearest Monday held, so all nine stand on the second Monday. Taking the count down by two a
    run ends the round after the first, and the next asks the four first, onto the third Monday."""
    case = _case("runs_merged_in_one_round")
    moved = _answer(case)
    assert moved == case["answer"]
    assert len(set(moved)) == case["wanted"]
    assert moved.count(case["ordinals"][3]) == 9


def test_step_8_5_stops_early_only_at_the_most_the_count_allows() -> None:
    """Step 8.5's early stop (the second review's N04): on a unit of an hour with the day kept,
    the count two long, the Tuesday's lone 09:00 first meets a pair with a Wednesday 15:00 rank,
    its two cells one gap with one first place, taking the count down by one; the pair with the
    Friday's lone 16:00 takes it down by two and is the one made. Stopped at the first pair whose
    gaps stand no distance apart, the count falls by one and a second pair follows."""
    case = _case("a_long_pair_by_two_first")
    moved = _answer(case)
    assert moved == case["answer"]
    assert len({ordinal // 60 for ordinal in moved}) == case["wanted"]
    assert moved[1] == case["ordinals"][2] and moved[9] == case["ordinals"][8]
    assert moved[4:7] == case["ordinals"][4:7]


def test_step_8_5_lists_a_rank_on_the_unit_it_joins() -> None:
    """Step 8.5's tables keep a moved rank on the unit it joins (the second review's N06): the
    Monday rank joins its gap's Saturday and a second-gap Saturday rank its Tuesday; then the
    Thursday joins the Saturday left alone, and of the first gap's Saturday, held three times now,
    the first rank in rank order -- the Monday rank -- goes on to the Tuesday. Left off the
    Saturday's list, the Monday rank stays, and a Saturday rank goes in its place."""
    case = _case("long_pairs_move_a_joined_rank_again")
    moved = _answer(case)
    assert moved == case["answer"]
    assert len(set(moved)) == case["wanted"]
    assert moved[1] == case["ordinals"][4]
    assert moved[2] == moved[3] == case["ordinals"][2]
    assert moved[9] == case["ordinals"][10] and moved[10] == case["ordinals"][7]


def test_step_8_5_counts_every_holder_of_a_unit() -> None:
    """Step 8.5 counts every rank of the column on a written unit, not its cell's alone (the second
    review's N10): the first gap's Sunday is held by its rank and by the pinned rank the gap starts
    at, so it is not alone, and the lone Saturday joins the Monday while a Tuesday rank joins the
    second gap's Saturday: the count falls by one. Counted in its cell, the Sunday rank moves
    first, and the count stays long."""
    case = _case("long_pairs_count_the_pinned_rank")
    moved = _answer(case)
    assert moved == case["answer"]
    assert len(set(moved)) == case["wanted"]
    assert moved[1] == case["ordinals"][1] == case["ordinals"][0]
    assert moved[4] == case["ordinals"][2] and moved[6] == case["ordinals"][8]


def test_step_8_5_measures_two_gaps_apart_from_their_first_places() -> None:
    """Step 8.5's distance between two gaps is between their first places (the second review's
    N13): the one-week gap's lone Saturday pairs with the gap after it, starting a week from its
    first place, and not with the gap before it, starting two weeks before -- though that gap ends
    a week from its last place and the one after it two weeks."""
    case = _case("a_long_pair_by_first_places")
    moved = _answer(case)
    assert moved == case["answer"]
    assert len(set(moved)) == case["wanted"]
    assert moved[8] == case["ordinals"][6] and moved[10] == case["ordinals"][12]
    assert moved[:6] == case["ordinals"][:6]


def test_a_cycle_is_undone_last_move_first(monkeypatch: pytest.MonkeyPatch) -> None:
    """Step 8.3's cycle undone last move first (the second review's N14, on the state its Codex
    review restated, item 1): Tuesday 10:00:10 moves to Thursday 10:00:10 and, the lower rank of
    Thursday's two lone minutes, on to Wednesday 10:00:10, where it is Wednesday's mover too;
    Sunday 10:00:10 stands before the gap opens, so it goes back to Thursday and then to Tuesday,
    and nothing has moved. Undone first move first, it is left on Thursday."""
    case = _case("a_cycle_undone_last_move_first")
    answer, made = _made(monkeypatch, case)
    assert answer == case["answer"] == case["ordinals"]
    assert made == [0, 0, -1]


# THE REVIEW'S MUTANTS (review of landing 3b.D0, items 3 to 5, by the reviewer's ids; M70 on are
# the repair's own lines, N01, N04, N06, N10, N13 and N14 the second review's, item 1, on the
# repair's own lines too, and C1a to C1d its Codex review's, item 1, on the lines of the take that
# counts written units), each a source edit of the product, each red on the case beside it. The
# review's M09 and M10 are `BODY_MUTANTS`' now: since the Codex review step 8.3 asks written units,
# and the count of each unit's ranks has one reader, the short cause's test of a full body.
REVIEW_MUTANTS: "dict[str, tuple[str, str, str]]" = {
    "C1a_take_asks_the_unit": (
        "written_units_free_in_held_hours",
        "            if not _weekday_holds(state, other):\n                return 1",
        "            if _weekday_unit_free(state, unit):\n                return 1",
    ),
    "C1a_take_asks_the_unit_moments": (
        "a_free_second_on_a_held_day",
        "            if not _weekday_holds(state, other):\n                return 1",
        "            if _weekday_unit_free(state, unit):\n                return 1",
    ),
    "C1b_take_ignores_the_gap": (
        "a_link_past_its_gap",
        "if unit == here or other < low or other > high:",
        "if unit == here:",
    ),
    "C1c_cycle_mover_first_rank": (
        "a_cycles_mover_holds_the_most",
        "            mover = _weekday_mover(state, members[giving])",
        "            mover = members[giving][0]",
    ),
    "C1d_chain_mover_first_rank": (
        "a_chains_mover_holds_the_most",
        "                mover = _weekday_mover(state, cells[key][giving])",
        "                mover = cells[key][giving][0]",
    ),
    "M12_prior_hole_ends": (
        "the_prior_of_hours",
        "if first < unit < last:\n                found[index] = found[index] - _WEEKDAY_SCALE\n",
        "if first <= unit <= last:\n                found[index] = found[index] - _WEEKDAY_SCALE\n",
    ),
    "M13_prior_hole_span": (
        "the_prior_of_hours",
        "closing = ((hole + 1) * state.day - 1) // state.unit",
        "closing = opening",
    ),
    "M15_single_tie_upper_side": (
        "the_index_tie",
        "found = (there, distance, side, target)",
        "found = (there, distance, 1 - side, target)",
    ),
    "M19_window_one_wider": (
        "the_index_reach",
        "first = max(unit - _WEEKDAY_REACH, -((place - state.lows[rank]) // state.unit))",
        "first = max(unit - _WEEKDAY_REACH - 1, -((place - state.lows[rank]) // state.unit))",
    ),
    "M20_chain_depth_first": (
        "a_chain_in_order",
        "queue = queue[1:]",
        "queue = queue[1:]\n            queue = queue[::-1]",
    ),
    "M21_chain_last_cell_links": (
        "a_chain_in_order",
        "if taking == giving or (giving, taking) in link:",
        "if taking == giving:",
    ),
    "M24_merge_widest_window": (
        "merged_inside_the_shared_gap",
        "low = max(state.lows[rank] for rank in ranks)",
        "low = min(state.lows[rank] for rank in ranks)",
    ),
    "M25_merge_same_clock_later_tie": (
        "merged_ties",
        "for other in (here - away, here + away):",
        "for other in (here + away, here - away):",
    ),
    "M26_merge_any_clock_no_opens": (
        "merged_ties",
        "and (ordinal % state.day == 0) == opens",
        "and True",
    ),
    "M27_merge_any_clock_later_tie": (
        "merged_ties",
        "if best is None or (abs(other - here), other) < best:",
        "if best is None or (abs(other - here), -other) < (best[0], -best[1]):",
    ),
    "M28_pair_two_when_one_long": (
        "a_long_pair_one_long",
        "if long >= 2 and alone is not None:",
        "if alone is not None:",
    ),
    "M29_pair_score_no_distance": (
        "long_pairs_twice",
        "score = (-gain, abs(pairs.keys[first][0] - pairs.keys[second][0]))",
        "score = (-gain, 0)",
    ),
    "M31_trade_no_early_stop": (
        "trades_in_rank_order",
        "if best is not None and best[0][0] == 0:",
        "if False:",
    ),
    "M32_trade_reach_61": (
        "a_trade_reaching_62",
        "_WEEKDAY_TRADE_REACH = 62",
        "_WEEKDAY_TRADE_REACH = 61",
    ),
    "M33_trade_back_30": (
        "a_trade_back_31",
        "_WEEKDAY_TRADE_BACK = 31",
        "_WEEKDAY_TRADE_BACK = 30",
    ),
    "M42_trade_ignores_keep": (
        "a_trade_of_hours",
        "if kind[0] != base[0] or kind[1] != base[1]:",
        "if kind[0] != base[0]:",
    ),
    "M48_run_target_drops_place_in_check": (
        "a_moments_run",
        "if not _weekday_holds(state, unit * state.unit + place):",
        "if not _weekday_holds(state, unit * state.unit):",
    ),
    "M48_run_target_drops_place_in_check_hours": (
        "an_hour_run",
        "if not _weekday_holds(state, unit * state.unit + place):",
        "if not _weekday_holds(state, unit * state.unit):",
    ),
    "M49_run_lands_at_unit_start": (
        "a_moments_run",
        "return best[2] * state.unit + place",
        "return best[2] * state.unit",
    ),
    "M49_run_lands_at_unit_start_hours": (
        "an_hour_run",
        "return best[2] * state.unit + place",
        "return best[2] * state.unit",
    ),
    "M52_merge_unit_not_alone": (
        "merged_only_alone",
        "            if _weekday_there(state, here) != len(ranks):\n                continue\n            low = max(",
        "            low = max(",
    ),
    "M53_pair_onto_hole": (
        "a_long_pair_one_long",
        "            if not pairs.hole[written]:\n                _weekday_listed(pairs.onto, spot, written, True)",
        "            if True:\n                _weekday_listed(pairs.onto, spot, written, True)",
    ),
    "M56_trade_onto_full_group": (
        "a_trade_of_hours",
        "                    if have[group] >= want[group]:\n                        continue\n"
        "                    kind = _weekday_kind(state, other)",
        "                    if have[group] > want[group]:\n                        continue\n"
        "                    kind = _weekday_kind(state, other)",
    ),
    "M58_no_count_after_trade": (
        "a_trade_in_the_pass",
        "    if have != target and _weekday_traded(state, everything, have, target):\n        if state.keep_units:",
        "    if have != target and _weekday_traded(state, everything, have, target):\n        if False:",
    ),
    "M60_chain_not_run": (
        "a_chain_in_the_pass",
        "    if have != target:\n        _weekday_chained(state, everything, have, target)",
        "    if False:\n        _weekday_chained(state, everything, have, target)",
    ),
    "M61_units_merged_rounds_1": (
        "merged_in_a_second_round",
        "_WEEKDAY_MERGE_ROUNDS = 4",
        "_WEEKDAY_MERGE_ROUNDS = 1",
    ),
    "M63_pairs_1": (
        "long_pairs_twice",
        "_WEEKDAY_PAIRS = 512",
        "_WEEKDAY_PAIRS = 1",
    ),
    "M64_trades_1": (
        "trades_in_rank_order",
        "_WEEKDAY_TRADES = 200",
        "_WEEKDAY_TRADES = 1",
    ),
    "M70_pair_count_not_kept": (
        "long_pairs_twice",
        "        count = count + _weekday_pair_made(state, pairs, best)",
        "        _weekday_pair_made(state, pairs, best)",
    ),
    "M72_pair_status_not_kept": (
        "long_pairs_twice",
        "    for unit in touched:\n        held = _weekday_there(state, unit * state.step)",
        "    for unit in []:\n        held = _weekday_there(state, unit * state.step)",
    ),
    "M73_pair_empty_unit_kept": (
        "long_pairs_leave_an_emptied_unit",
        "    if not found:\n        del units[left]",
        "    if False:\n        del units[left]",
    ),
    "M74_merge_count_not_kept": (
        "merged_at_its_clock",
        "            count = count - 1\n            changed = True\n        if not changed:\n            return",
        "            changed = True\n        if not changed:\n            return",
    ),
    "M75_runs_count_not_kept": (
        "runs_merged_until_the_count_is_back",
        "        count = count - 1\n        changed = True\n    return changed",
        "        changed = True\n    return changed",
    ),
    "M80_no_units_merged_in_pass": (
        "merged_in_the_pass",
        "    if _weekday_count(state) > wanted:\n        _weekday_units_merged(state, body_low, body_high, pinned, wanted)",
        "    if False:\n        _weekday_units_merged(state, body_low, body_high, pinned, wanted)",
    ),
    "M81_no_long_pairs_in_pass": (
        "a_long_pair_in_the_pass",
        "    if _weekday_count(state) > wanted:\n        _weekday_long_paired(state, body_low, body_high, pinned, wanted)",
        "    if False:\n        _weekday_long_paired(state, body_low, body_high, pinned, wanted)",
    ),
    "M82_no_trade_in_pass": (
        "a_trade_in_the_pass",
        "    if have != target and _weekday_traded(state, everything, have, target):",
        "    if False and _weekday_traded(state, everything, have, target):",
    ),
    "M83_cycle_left_half_made": (
        "a_cycle_undone",
        "            for place in range(len(made) - 1, -1, -1):\n"
        "                _weekday_step(state, made[place][0], made[place][1])\n            return False",
        "            return False",
    ),
    "N01_runs_count_falls_two": (
        "runs_merged_in_one_round",
        "        count = count - 1\n        changed = True\n    return changed",
        "        count = count - 2\n        changed = True\n    return changed",
    ),
    "N04_pair_top_always_one": (
        "a_long_pair_by_two_first",
        "    top = (-2 if long >= 2 else -1, 0)",
        "    top = (-1, 0)",
    ),
    "N06_pair_joined_not_listed": (
        "long_pairs_move_a_joined_rank_again",
        "    found = units[joined]\n    at = _weekday_first_from(found, rank)\n    found[at:at] = [rank]",
        "    found = units[joined]\n    at = _weekday_first_from(found, rank)",
    ),
    "N10_pair_held_in_cell_only": (
        "long_pairs_count_the_pinned_rank",
        "            held = _weekday_there(state, written * state.step)\n",
        "            held = len(units[written])\n",
    ),
    "N13_pair_score_last_places": (
        "a_long_pair_by_first_places",
        "score = (-gain, abs(pairs.keys[first][0] - pairs.keys[second][0]))",
        "score = (-gain, abs(pairs.keys[first][1] - pairs.keys[second][1]))",
    ),
    "N14_cycle_undone_first_first": (
        "a_cycle_undone_last_move_first",
        "            for place in range(len(made) - 1, -1, -1):\n",
        "            for place in range(len(made)):\n",
    ),
}


@pytest.mark.parametrize("name", sorted(REVIEW_MUTANTS))
def test_each_clause_is_red_on_its_mutant(name: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """Every clause a reviewer's mutant changed while every case before the review still passed
    (review of landing 3b.D0, items 3 to 5), every line the repair added that its own mutants
    (M70 on) needed a case for, every line of the repair a mutant of the second review changed
    while all those cases still held (its item 1: N01, N04, N06, N10, N13 and N14), and every line
    of the take its Codex review asked for (item 1: C1a to C1d, the written unit, the gap, and
    each step's mover): under its source edit the case beside it answers otherwise, or its tables
    raise (M73). Every other mutant of the repair's lines, its own or the second review's, is red
    on this file's other tests, but two that change no answer: the second review's N07, a unit's
    status kept in its first cell alone, is the same pass, a unit two cells hold having two
    holders, and M71, step 8.5's early stop withdrawn, changes only its speed."""
    case_name, before, after = REVIEW_MUTANTS[name]
    case = _case(case_name)
    mutant = _mutant(monkeypatch, before, after)
    try:
        answered = _answer(case, mutant)
    except IndexError:
        assert name == "M73_pair_empty_unit_kept"
        return
    assert answered != case["answer"], name


def test_the_body_is_full_only_where_every_unit_the_census_counts_holds_a_rank() -> None:
    """The test the short cause asks (`_weekday_body_full`, the review's M65): between a
    Wednesday holding a rank and itself the body is full; to the Thursday after, free, it is not,
    unless the census counts no weekday at all."""
    case = _case("the_index_tie")
    state = _state(case)
    wednesday = case["ordinals"][1]
    census = ((0, 4, 1), (5, 6, 2))
    assert generation._weekday_body_full(state, wednesday, wednesday, census)
    assert not generation._weekday_body_full(state, wednesday, wednesday + 1, census)
    assert generation._weekday_body_full(state, wednesday, wednesday + 1, ((0, 4, 0), (5, 6, 3)))


# The review's M09 and M10, on the count of each unit's ranks (`units_held`), which since the Codex
# review's item 1 only the short cause's test of a full body reads.
BODY_MUTANTS: "dict[str, tuple[str, str]]" = {
    "M09_unit_free_ignores_count": (
        "return unit not in state.units_held or state.units_held[unit] <= 0",
        "return unit not in state.units_held",
    ),
    "M10_units_held_not_moved": (
        "    if state.unit != state.step:\n        key = before // state.unit",
        "    if False:\n        key = before // state.unit",
    ),
}


def test_the_body_counts_a_unit_a_move_empties(monkeypatch: pytest.MonkeyPatch) -> None:
    """The short cause's test of a full body counts the ranks on each unit as they move (the
    review's M09 and M10, moved here from the mutant table once step 8.3 asked written units, its
    Codex review's item 1): a day of moments holding Monday 08:00:00 and Tuesday 08:00:00 is full
    over those two days, and is not once the Monday moment moves to Wednesday. Mutants: a unit
    counted free only where it was never held (M09), and the count left where it was (M10)."""
    monday = (datetime.date(2024, 3, 4) - datetime.date(1970, 1, 1)).days * DAY

    def full_before_and_after(module) -> "tuple[bool, bool]":
        case = {
            "ordinals": [monday + 8 * HOUR, monday + DAY + 8 * HOUR], "where": [0, 0, 0, 0, 0, 1, 1],
            "holes": [], "lows": [monday, monday], "highs": [monday + 6 * DAY, monday + 6 * DAY],
            "reachable": True, "unit": DAY, "written_unit": 1, "day": DAY, "bin": "weekday",
            "period": 7, "keep": "", "pair": "", "pair_where": [],
        }
        state = _state(case, module)
        census = ((0, 4, 2), (5, 6, 0))
        before = module._weekday_body_full(state, monday, monday + 2 * DAY - 1, census)
        module._weekday_step(state, 0, monday + 2 * DAY + 8 * HOUR)
        return before, module._weekday_body_full(state, monday, monday + 2 * DAY - 1, census)

    assert full_before_and_after(generation) == (True, False)
    for name, (before, after) in BODY_MUTANTS.items():
        assert full_before_and_after(_mutant(monkeypatch, before, after)) == (True, True), name
        monkeypatch.undo()


# -- a column of the batteries through the whole generator (items 1 and 2) -----------------


def _sessions(tmp_path: pathlib.Path):
    """The review's weekly sessions `_weekly_schedule(92)`, described at a floor of 36."""
    import kpi_shapes
    import test_stage3b_weekday_review as review

    cells = review._weekly_schedule(92)
    return kpi_shapes.describe(tmp_path, "sessions", "visit\n" + "".join(f"{cell}\n" for cell in cells), 36)


def test_a_schedule_at_floor_36_reaches_step_8_5(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A column of the batteries reaches a new step through the whole generator at a floor of 36
    (review of landing 3b.D0, item 1): 538 weekly sessions on 46 days publish their census, and
    every twin at seeds 0 to 2 holds 52 different days, a count 110cb46 left at 53. Red with
    step 8.5 withdrawn: 53."""
    import kpi_shapes

    described = _sessions(tmp_path)
    block = described.block("visit")
    assert block["weekday_census"] and block["n_distinct"] == 46
    for seed in (0, 1, 2):
        assert len(set(kpi_shapes.twin_text(described, seed).splitlines()[1:])) == 52, seed
    monkeypatch.setattr(generation, "_weekday_long_paired", _withdrawn)
    for seed in (0, 1, 2):
        assert len(set(kpi_shapes.twin_text(described, seed).splitlines()[1:])) == 53, seed


def _distinct_notes(module, described, seed: int) -> "list[tuple[str, str, str, str]]":
    return [
        (note.fact, note.published, note.achieved, note.note)
        for note in module.generate(described.loaded, seed).deviations
        if note.fact in ("n_distinct", "n_distinct_folded") and "approximate by construction" not in note.note
    ]


def test_a_count_left_long_is_named_long(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The report names the day pass's cause for a count it left LONG (review of landing 3b.D0,
    item 2): on the sessions at a floor of 36 the recount's line for the count of different
    values carries `_WEEKDAY_DAYS_LEFT_LONG`, 46 published and 52 held, and the folded count's
    line beside it gives the same cause. Red when the pass names the count short (the review's
    M38), names no cause where it is long (M39), or the long sentence stands over the cause."""
    described = _sessions(tmp_path)
    expected = [
        ("n_distinct", "46", "52", generation._WEEKDAY_DAYS_LEFT_LONG),
        ("n_distinct_folded", "46", "52", generation._WEEKDAY_FOLDED_LEFT_LONG),
    ]
    for seed in (0, 1, 2):
        assert _distinct_notes(generation, described, seed) == expected, seed
    for before, after in (
        (
            "        if _weekday_count(state) > wanted:\n            cause = _WEEKDAY_DAYS_LEFT_LONG",
            "        if False:\n            cause = _WEEKDAY_DAYS_LEFT_LONG",
        ),
        (
            "elif state.keep_units and _weekday_count(state) != wanted:",
            "elif state.keep_units and _weekday_count(state) < wanted:",
        ),
        (
            "            if cause == _WEEKDAY_DAYS_LEFT_LONG and counted[2] > column.n_distinct:\n"
            "                reason = _WEEKDAY_FOLDED_LEFT_LONG",
            "            if False:\n                reason = _WEEKDAY_FOLDED_LEFT_LONG",
        ),
    ):
        mutant = _mutant(monkeypatch, before, after)
        assert _distinct_notes(mutant, described, 0) != expected, before


def test_a_cause_stands_only_where_the_recount_went_its_way(tmp_path: pathlib.Path) -> None:
    """A cause the day pass named stands in the recount's sentence only where the twin's count
    went the cause's way (review of landing 3b.D0, item 2): the long cause over a long count,
    the short ones over a short count; across, the recount's own sentence for its direction."""
    column = _sessions(tmp_path).loaded.columns[0]
    published = column.n_distinct
    for cause in generation._WEEKDAY_CAUSES:
        long_cause = cause == generation._WEEKDAY_DAYS_LEFT_LONG
        for counted in (published + 2, published - 2):
            notes = generation._recount_notes(
                column, (column.n_present, column.n_missing, counted, column.n_distinct_folded), [], cause=cause
            )
            said = [note.note for note in notes if note.fact == "n_distinct"]
            assert len(said) == 1, (cause[-40:], counted)
            if long_cause == (counted > published):
                assert said == [cause], (cause[-40:], counted)
            elif counted > published:
                assert "MORE different spellings" in said[0], (cause[-40:], counted)
            else:
                assert said[0].startswith("The twin holds fewer different spellings"), (cause[-40:], counted)
