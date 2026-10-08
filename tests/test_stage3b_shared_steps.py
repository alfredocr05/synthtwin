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
  empties, step 7b's search, step 8.2's stop, step 8.3's cycle undone (a
  cycle of three made whole since the verification of the Codex review's
  item 1), step 8.4's ties, window, alone-only rule and second round, step 8.5's
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
  last move first (a cycle of four made whole since that verification)
  -- each red on that review's mutant (N01, N04, N06, N10 and N13, and
  N14 until the undo it edited went; the review's other mutants of the
  repair's lines were already red on this file's other tests, all but
  N07, which is the same pass);
* the Codex review's cases (its item 1): step 8.3's gain counts the
  WRITTEN units its mover can take at its own place inside its unit --
  Codex's own state of forty ranks each at 00:15, 01:15 and 02:30, and a
  free second on a held day -- each step's mover is the rank on the
  written unit holding the most, and a place past the gap is no take (the
  two states the landing's reviews froze a cycle undone on now offer no
  cycle): C1a to C1d in the mutant table;
* the verification of that item: each move of a cycle takes the mover
  its gain was asked of, not the mover as the ranks then stand, which a
  move made before it can make the rank it put on that group -- its
  states of hours and of moments, which the mover as the ranks then
  stood left one short (`an_hour_cycle_moves_its_asked_movers` and
  `a_moments_cycle_moves_its_asked_movers`), and the two cycles the
  reviews above froze undone, made whole now
  (`a_cycle_of_three_moves_its_asked_movers` and
  `a_cycle_of_four_moves_its_asked_movers`): C1e in the mutant table;
  and, as the repair of that verification extended it to step 7b, each
  move of a chain takes the mover as the ranks then stand, or, where
  that rank has no place of the next group, the mover its link was asked
  of, so no chain is left half made -- a chain of hours and one of
  moments through the whole pass (`a_chain_moves_its_asked_mover` and
  `a_chain_moves_its_asked_mover_in_the_pass`): C1f in the mutant table;
* the Codex review's growth tests (its items 2 to 5), machine-free, on
  the review's own states at its own sizes and at 40,000 rows:
  `test_step_8_3_asks_only_the_retained_day` (item 2),
  `test_step_8_4_asks_the_retained_day_and_builds_its_places_once`
  (item 3), `test_step_8_5_asks_only_the_cells_holding_a_source` (item
  4, and a state whose cells hold sources but none beside the place a
  pair needs) and `test_the_index_holds_few_units_for_each_rank` (item
  5, at the review's 102,528 units); and its item 6,
  `test_a_cycle_of_four_groups_is_not_asked_above_seven`, the bound on
  step 8.3's cycles kept and its limit stated on the review's ten groups
  of days of the month;
* `test_a_trade_keeps_a_way_back_once_the_count_is_put_back` -- a strict
  xfail owned by landing D3, the first to keep a second census: on the
  second-census state the verification of the Codex review's item 1
  noted, a cycle of step 8.3 and a merge of step 8.4 leave step 8.6 no
  way back, and the census is missed where 9cb2eb5 met it (P4-D366's
  stated limit);
  `test_a_chain_reaches_a_group_through_the_rank_beside_its_mover`, a
  strict xfail owned by D3 the same way: on a second-census state of
  that item's repair's own battery, step 7b's link, asked of each
  cell's mover alone, finds no chain where the rank beside the mover
  has the place, and the census is missed where 9cb2eb5's chain, moved
  half way, was finished by step 8.6; and
  `test_a_chain_spends_a_value_only_where_the_census_is_then_met`, a
  strict xfail owned by landing D2, the first to publish a weekday
  census of moments: on a day of moments the second verification of
  that item found, where no placement keeping every clock meets both
  facts, step 7b's chain, made whole through the mover its link was
  asked of, halves the census's miss and keeps 12 different minutes
  where 9cb2eb5 kept the 13 asked (P4-D366's third stated limit);
* `test_the_body_is_full_only_where_every_unit_the_census_counts_holds_a_rank`
  -- the test the short cause asks (the review's M65), and
  `test_the_body_counts_a_unit_a_move_empties` -- the review's M09 and
  M10 on the count of each unit's ranks, which only that test reads;
* `test_a_schedule_at_floor_36_reaches_step_8_5`,
  `test_a_count_left_long_is_named_long` and
  `test_a_cause_stands_only_where_the_recount_went_its_way` -- a column
  of the batteries through the whole generator, and the report's cause;
* the third verification of the Codex review's item 1:
  `test_a_trade_meets_the_census_and_keeps_the_count` and
  `test_a_chain_meets_the_census_and_the_count_is_still_put_back`,
  strict xfails owned by landing D3, on two second-census states of its
  200,000 where 9cb2eb5 met both facts and the census is met by both --
  one value short, where 9cb2eb5's chain left half made led step 8.6 to
  a trade keeping a value the head's trade empties, and one value long,
  where step 7b's chain made whole meets the census 9cb2eb5's trade met
  and steps 8.1 to 8.5 leave one value more than asked -- and
  `test_every_step_keeps_the_written_time_of_day_on_the_held_minute`: on
  the second verification's day of moments above no step of the pass
  takes a moment off its written time of day, and steps 8.4 and 8.5,
  which hold the only moves that do on a day of moments, move no rank
  (P4-D366's third stated limit, its clause restated);
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

import fixtures
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
        return [[giving, taking] for _cell, giving, taking, _mover in module._weekday_cycle(state, cells, case["short"])]
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
    "a_chain_in_order", "a_chain_in_the_pass", "a_cycle_of_three_moves_its_asked_movers", "a_day_freed_for_a_cycle",
    "a_long_pair_in_the_pass", "a_long_pair_one_long", "a_moments_run", "a_trade_back_31",
    "a_trade_in_the_pass", "a_trade_of_hours", "a_trade_reaching_62", "an_hour_run",
    "long_pairs_leave_an_emptied_unit", "long_pairs_twice", "merged_in_a_second_round",
    "merged_in_the_pass", "merged_inside_the_shared_gap", "merged_only_alone", "merged_ties",
    "runs_merged_until_the_count_is_back", "the_index_reach", "the_index_tie",
    "the_prior_of_hours", "trades_in_rank_order",
    # the second review's (its item 1)
    "a_cycle_of_four_moves_its_asked_movers", "a_long_pair_by_first_places", "a_long_pair_by_two_first",
    "long_pairs_count_the_pinned_rank", "long_pairs_move_a_joined_rank_again", "runs_merged_in_one_round",
    # the Codex review's (its item 1)
    "a_chains_mover_holds_the_most", "a_cycles_mover_holds_the_most", "a_free_second_on_a_held_day",
    "a_link_past_its_gap", "a_place_past_the_gap_offers_no_cycle",
    "a_third_place_past_its_gap_offers_no_cycle", "written_units_free_in_held_hours",
    # its verification's (item 1)
    "a_moments_cycle_moves_its_asked_movers", "an_hour_cycle_moves_its_asked_movers",
    # ...and its repair's, on step 7b
    "a_chain_moves_its_asked_mover", "a_chain_moves_its_asked_mover_in_the_pass",
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
    """A case's answer, and the rank each move of steps 7b and 8.3 took (-1 where it found no
    place)."""
    made: "list[int]" = []
    moved_near = module._weekday_moved_near

    def recorded(state, rank, *arguments):
        nonlocal made
        found = moved_near(state, rank, *arguments)
        made += [rank if found else -1]
        return found

    monkeypatch.setattr(module, "_weekday_moved_near", recorded)
    return _answer(case, module), made


# The cycle's moves taking the mover as the ranks then stand, as the Codex review's item 1 had it
# until its verification: the move of step 7b's chain in place of the asked mover's.
AS_THE_RANKS_THEN_STAND = (
    "        _weekday_moved_near(state, mover, taking, key[2])\n",
    "        _weekday_cell_move(state, list(range(len(state.moved))), key, _giving, taking)\n",
)


def test_a_cycle_moves_the_movers_its_gain_was_asked_of(monkeypatch: pytest.MonkeyPatch) -> None:
    """Each move of step 8.3's cycle takes the mover its gain was asked of (the verification of
    the Codex review, item 1), so every move finds its place and the cycle is made whole. A Tuesday
    moment goes to Sunday 10:01:05 and is then the lower rank of Sunday's two lone moments, yet
    Sunday's move takes 10:00:30 to Thursday 10:00:30 and a Thursday moment goes to Tuesday
    10:00:00: the count gains two. On four groups, minutes written, Tuesday 10:00:10 goes to
    Thursday, where it is the lower rank, and Thursday's move takes 10:01:30 to Wednesday; then
    Wednesday 10:00:20 to Sunday and a Sunday moment to Tuesday 10:01:30, and the count gains two.
    Taken as the ranks then stand, the moment just moved is the next group's mover and finds no
    place: Thursday 10:01:05 stands past the first gap's close, Sunday 10:00:10 before the second
    gap opens (the cycle was undone on both until the verification)."""
    for case, movers, undone in (
        (_case("a_cycle_of_three_moves_its_asked_movers"), [0, 2, 3], [0, -1]),
        (_case("a_cycle_of_four_moves_its_asked_movers"), [0, 3, 2, 4], [0, 0, -1]),
    ):
        answer, made = _made(monkeypatch, case)
        assert answer == case["answer"], case["why"]
        assert made == movers, case["why"]
        assert _holding(case, answer, range(len(answer))) == case["counts"], case["why"]
        step = case["written_unit"]
        assert len({ordinal // step for ordinal in answer}) == len({ordinal // step for ordinal in case["ordinals"]}) + 2
        answer, made = _made(monkeypatch, case, _mutant(monkeypatch, *AS_THE_RANKS_THEN_STAND))
        assert made[:len(undone)] == undone, case["why"]
        assert _holding(case, answer, range(len(answer))) != case["counts"], case["why"]
        monkeypatch.undo()


def test_a_cycle_of_hours_or_moments_meets_the_count_its_movers_reach(monkeypatch: pytest.MonkeyPatch) -> None:
    """The two states the verification of the Codex review's item 1 found one short, through the
    whole pass. Hours, minutes written, the day kept: on Thursday 00:14 three times and 01:07
    alone; a 00:14 rank goes to 01:14, and hour 1's move takes 01:07, its gain's mover, to 00:07.
    A day of moments, minutes written: a Monday 09:49:00 moment goes to Tuesday, and Tuesday's move
    takes 11:33:00, its gain's mover, to Monday. Each meets the census and the count. Taken as the
    ranks then stand, the next group's mover is the rank just moved, which goes straight back, and
    the count stays one short (9cb2eb5 met both facts on each through another cycle)."""
    for case, movers in (
        (_case("an_hour_cycle_moves_its_asked_movers"), [1, 4]),
        (_case("a_moments_cycle_moves_its_asked_movers"), [2, 4]),
    ):
        answer, made = _made(monkeypatch, case)
        assert answer == case["answer"], case["why"]
        assert made == movers, case["why"]
        assert _holding(case, answer, range(len(answer))) == case["counts"], case["why"]
        assert len({ordinal // case["written_unit"] for ordinal in answer}) == case["wanted"], case["why"]
        answer, made = _made(monkeypatch, case, _mutant(monkeypatch, *AS_THE_RANKS_THEN_STAND))
        assert made == [movers[0], movers[0]], case["why"]
        assert _holding(case, answer, range(len(answer))) == case["counts"], case["why"]
        assert len({ordinal // case["written_unit"] for ordinal in answer}) == case["wanted"] - 1, case["why"]
        monkeypatch.undo()


def test_a_cycle_whose_move_has_no_place_is_not_asked(monkeypatch: pytest.MonkeyPatch) -> None:
    """Step 8.3 asks a pair's take of its mover's own places, inside its gap (the Codex review,
    item 1): the two states the landing's reviews froze a cycle undone on offer no cycle, a
    weekday at 10:00:00 standing outside the first gap of one and Monday 22:00:00 past the second
    gap's close of the other, and no move is tried. Mutant: the take counts places past its gap,
    a cycle is chosen whose move finds no place, and it is left half made, the census broken."""
    for case, half in (
        (_case("a_place_past_the_gap_offers_no_cycle"), [4, -1]),
        (_case("a_third_place_past_its_gap_offers_no_cycle"), [1, 2, -1]),
    ):
        answer, made = _made(monkeypatch, case)
        assert answer == case["answer"] == case["ordinals"], case["why"]
        assert made == [], case["why"]
        mutant = _mutant(monkeypatch, *REVIEW_MUTANTS["C1b_take_ignores_the_gap"][1:])
        answer, made = _made(monkeypatch, case, mutant)
        assert made[:len(half)] == half, case["why"]
        assert _holding(case, answer, range(len(answer))) != case["counts"], case["why"]
        monkeypatch.undo()


# Step 7b's move taking the mover as the ranks then stand and no other, as it stood until the
# repair of the verification of the Codex review's item 1: no move onto the mover its link was
# asked of where that rank has no place.
CHAIN_AS_THE_RANKS_THEN_STAND = (
    "            ) and not _weekday_moved_near(\n"
    "                state, asked[(giving, taking)], taking, key[2]\n"
    "            ):\n",
    "            ):\n",
)


def test_a_chain_moves_the_mover_its_link_was_asked_of(monkeypatch: pytest.MonkeyPatch) -> None:
    """Step 7b moves the mover as the ranks then stand, or, where that rank has no place of the
    next group, the mover the link was asked of (the repair of the verification of the Codex
    review's item 1, on step 7b), so every move finds its place and the chain is made whole. Hours,
    minutes written, the day kept: 00:47 goes to 01:47, where it is the lower rank of two lone
    minutes, and its hour 10 place stands past the gap's close, so 08:37, the mover asked, goes to
    10:37. A day of moments, through the whole pass: a Friday moment goes to Saturday 23:20:20,
    whose Monday stands past the gap's close, so Saturday 05:59:12, the mover asked, goes to
    Monday, and the census is met with the count kept. Moved as the ranks then stand alone, each
    chain is left half made, one group over, and the census is missed."""
    for case, movers, over in (
        (_case("a_chain_moves_its_asked_mover"), [1, -1, 2], [1, 2, 1, 0]),
        (_case("a_chain_moves_its_asked_mover_in_the_pass"), [1, -1, 4], [1, 0, 0, 3, 3, 3]),
    ):
        answer, made = _made(monkeypatch, case)
        assert answer == case["answer"], case["why"]
        assert made == movers, case["why"]
        assert _holding(case, answer, range(len(answer))) == case["counts"], case["why"]
        if case["step"] == "settled":
            assert len({ordinal // case["written_unit"] for ordinal in answer}) == case["wanted"], case["why"]
        answer, made = _made(monkeypatch, case, _mutant(monkeypatch, *CHAIN_AS_THE_RANKS_THEN_STAND))
        assert made == movers[:2], case["why"]
        assert _holding(case, answer, range(len(answer))) == over, case["why"]
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


# THE REVIEW'S MUTANTS (review of landing 3b.D0, items 3 to 5, by the reviewer's ids; M70 on are
# the repair's own lines, N01, N04, N06, N10 and N13 the second review's, item 1, on the repair's
# own lines too, and C1a to C1f its Codex review's, item 1, on the lines of the take that counts
# written units, of the cycle's move that takes the mover its gain was asked of, and of the
# chain's move onto the mover its link was asked of), each a source edit of
# the product, each red on the case beside it. The review's M09 and M10 are `BODY_MUTANTS`' now:
# since the Codex review step 8.3 asks written units, and the count of each unit's ranks has one
# reader, the short cause's test of a full body. The repair's M83 and the second review's N14 are
# gone with the lines they edited: a cycle's moves take the movers its gain was asked of since the
# verification of the Codex review's item 1, every one finds its place, and no cycle is undone.
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
    "C1e_cycle_moves_the_mover_as_the_ranks_stand": (
        "an_hour_cycle_moves_its_asked_movers", *AS_THE_RANKS_THEN_STAND,
    ),
    "C1e_cycle_moves_the_mover_as_the_ranks_stand_moments": (
        "a_moments_cycle_moves_its_asked_movers", *AS_THE_RANKS_THEN_STAND,
    ),
    "C1f_chain_moves_the_mover_as_the_ranks_stand": (
        "a_chain_moves_its_asked_mover", *CHAIN_AS_THE_RANKS_THEN_STAND,
    ),
    "C1f_chain_moves_the_mover_as_the_ranks_stand_in_the_pass": (
        "a_chain_moves_its_asked_mover_in_the_pass", *CHAIN_AS_THE_RANKS_THEN_STAND,
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
        # Restated at the Codex review's item 3: step 8.4's second place files every ordinal once a
        # round (`_weekday_merge_look`), so the mutant files each as starting a day.
        "merged_ties",
        "        _weekday_kind(state, ordinal),\n        ordinal % state.day == 0,\n    )",
        "        _weekday_kind(state, ordinal),\n        True,\n    )",
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
}


@pytest.mark.parametrize("name", sorted(REVIEW_MUTANTS))
def test_each_clause_is_red_on_its_mutant(name: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """Every clause a reviewer's mutant changed while every case before the review still passed
    (review of landing 3b.D0, items 3 to 5), every line the repair added that its own mutants
    (M70 on) needed a case for, every line of the repair a mutant of the second review changed
    while all those cases still held (its item 1: N01, N04, N06, N10 and N13), and every line
    of the take its Codex review asked for (item 1: C1a to C1f, the written unit, the gap, each
    step's mover, the cycle's move taking the mover its gain was asked of, as that item's
    verification asked, and the chain's move onto the mover its link was asked of where the
    mover as the ranks then stand has no place, as the repair of that verification extended
    it): under its source edit the case beside it answers otherwise, or its
    tables raise (M73). Every other mutant of the repair's lines, its own or the second review's,
    is red on this file's other tests, but two that change no answer: the second review's N07, a
    unit's status kept in its first cell alone, is the same pass, a unit two cells hold having
    two holders, and M71, step 8.5's early stop withdrawn, changes only its speed."""
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
    """The review's weekly sessions `_weekly_schedule(92)`, described at a floor of 36, with the census the
    menu offers written back: plan P4-D388 withholds it there, its body left too little room."""
    import kpi_shapes
    import test_stage3b_weekday_review as review
    from synthtwin import calendar_rules, contract, parsing

    cells = review._weekly_schedule(92)
    described = kpi_shapes.describe(tmp_path, "sessions", "visit\n" + "".join(f"{cell}\n" for cell in cells), 36)
    block = described.block("visit")
    days = sorted(parsing.days_from_civil(int(c[0:4]), int(c[5:7]), int(c[8:10])) for c in cells)
    body = days[block["low_tail"]["rows"] : len(days) - block["high_tail"]["rows"]]
    groups, _entry = calendar_rules.menu_groups(calendar_rules.body_bins(body), parsing.census_floor(36))
    census = [{"first": first, "last": last, "count": count} for first, last, count in groups]
    document = dict(described.document, columns=[dict(block, weekday_census=census)])
    loaded = contract.load_profile(str(fixtures.write_profile(tmp_path, "sessions-restored.json", document)))
    return kpi_shapes.Described(described.folder, described.table, document, loaded)


def test_a_schedule_at_floor_36_reaches_step_8_5(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A column of the batteries reaches a new step through the whole generator at a floor of 36
    (review of landing 3b.D0, item 1): 538 weekly sessions on 46 days with their census (written
    back by `_sessions`, since plan P4-D388 withholds it at this floor), and every twin at seeds 0
    to 2 holds 52 different days, a count 110cb46 left at 53. Red with step 8.5 withdrawn: 53."""
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


# -- the Codex review's growth tests (its items 2 to 5) and its item 6 ----------------------
#
# Machine-free: each counts the work one step does -- the entries it builds, the reads it makes --
# on the review's own state at the review's own sizes, red on 9cb2eb5 there, and again at 40,000
# rows, where the count must stay a fixed multiple of the rows; item 5's counts the units the
# index holds and the kinds kept, and item 6's states the bound on step 8.3's cycles and its limit,
# each red on 9cb2eb5 too.

MONDAY_DAY = (datetime.date(2024, 3, 4) - datetime.date(1970, 1, 1)).days


def _counting(monkeypatch: pytest.MonkeyPatch, name: str, measure) -> "list[int]":
    """While the pass runs, each call of `generation.<name>` adds `measure(its answer)`."""
    tally = [0]
    original = getattr(generation, name)

    def counted(*arguments):
        found = original(*arguments)
        tally[0] += measure(found)
        return found

    monkeypatch.setattr(generation, name, counted)
    return tally


def _hours_case(ordinals: "list[int]", counts: "list[int]", wanted: int, days: int) -> dict:
    """A whole pass over one gap of `days` days of moments, a unit of an hour, minutes written, the
    day kept, each hour its own group."""
    low, high = MONDAY_DAY * DAY, (MONDAY_DAY + days) * DAY - 1
    ranks = len(ordinals)
    return {
        "ordinals": sorted(ordinals), "lows": [low] * ranks, "highs": [high] * ranks, "pinned": [False] * ranks,
        "counts": counts, "where": list(range(24)), "unit": HOUR, "written_unit": 60, "day": DAY, "bin": "hour",
        "period": 24, "keep": "day", "pair": "", "pair_where": [], "holes": [], "reachable": True,
        "body": [0, ranks - 1], "wanted": wanted, "step": "settled",
    }


def _two_a_day(days: int) -> dict:
    """The Codex review's item 2 state: two ranks a day at 00:01 over `days` days but one at 01:01 on
    the first, every rank asked in hour 0, `days + 1` values kept."""
    ordinals: "list[int]" = []
    for day in range(days):
        ordinals += [(MONDAY_DAY + day) * DAY + 60] * 2
    ordinals[1] = MONDAY_DAY * DAY + HOUR + 60
    return _hours_case(ordinals, [2 * days] + [0] * 23, days + 1, days)


def test_step_8_3_asks_only_the_retained_day(monkeypatch: pytest.MonkeyPatch) -> None:
    """Step 8.3 where every move keeps the day grows with the days, not their square (the Codex
    review, item 2). Two ranks a day at 00:01 over D days, but one at 01:01 on the first, each hour
    its own group, every rank asked in hour 0 and D + 1 values kept: step 6 puts the 01:01 rank on
    00:01, and step 8.3 asks each day's cell for a cycle. Its take asks the units of each hour on
    that cell's day alone, 24 a day, where it built every hour of the gap for every cell: 24 D
    squared entries, 24,576, 98,304 and 393,216 at 32, 64 and 128 days. Asked at those sizes and at
    20,000 days, 40,000 rows; the census holds and no place lets the count reach D + 1."""
    for days in (32, 64, 128, 20000):
        case = _two_a_day(days)
        built = _counting(monkeypatch, "_weekday_units_of", len)
        moved = _answer(case)
        monkeypatch.undo()
        assert built[0] == 24 * days, (days, built[0])
        assert _holding(case, moved, range(len(moved))) == case["counts"], days
        assert len({ordinal // 60 for ordinal in moved}) == days, days


def _counting_in(monkeypatch: pytest.MonkeyPatch, step: str, name: str) -> "list[int]":
    """While `generation.<step>` runs, count the calls of `generation.<name>`."""
    tally = [0]
    inside = [False]
    original_step = getattr(generation, step)
    original = getattr(generation, name)

    def stepped(*arguments):
        inside[0] = True
        try:
            return original_step(*arguments)
        finally:
            inside[0] = False

    def counted(*arguments):
        if inside[0]:
            tally[0] += 1
        return original(*arguments)

    monkeypatch.setattr(generation, step, stepped)
    monkeypatch.setattr(generation, name, counted)
    return tally


def _every_hour(days: int) -> dict:
    """The Codex review's items 3 and 4 state: one rank at every hour's :01 over `days` days, but day
    zero's 01:01 standing on 00:01, `days` ranks asked in each hour, N - 1 values kept (N, the
    ranks, 24 a day)."""
    ordinals = [(MONDAY_DAY + day) * DAY + hour * HOUR + 60 for day in range(days) for hour in range(24)]
    ordinals[1] = ordinals[0]
    return _hours_case(ordinals, [days] * 24, len(ordinals) - 1, days)


def _every_hour_settled(monkeypatch: pytest.MonkeyPatch, step: str, name: str, per_row: int) -> None:
    """At the review's 120, 240 and 480 rows and at 40,008, in turn: the calls of `name` made inside
    `step` are `per_row` a row, the census holds and the count of different values is left one
    long. Each size is asserted before the next is asked."""
    for days in (5, 10, 20, 1667):
        case = _every_hour(days)
        calls = _counting_in(monkeypatch, step, name)
        moved = _answer(case)
        monkeypatch.undo()
        rows = len(moved)
        assert calls[0] == per_row * rows, (rows, calls[0])
        assert _holding(case, moved, range(rows)) == case["counts"], rows
        assert len({ordinal // 60 for ordinal in moved}) == rows == case["wanted"] + 1, rows


def test_step_8_4_asks_the_retained_day_and_builds_its_places_once(monkeypatch: pytest.MonkeyPatch) -> None:
    """Step 8.4 where every move keeps the day grows with the rows (the Codex review, item 3). One
    rank at every hour's :01 over D days, day zero's 01:01 on 00:01, D asked in each hour and N - 1
    values kept: step 6 moves a 00:01 rank to 01:01, and step 8.4 is asked one value long, with no
    merge to make -- every hour of every day holds one written unit. Its same-clock search walked
    every day of the gap for each unit, and its other-clock places were read again from the whole
    column for each group and day: 28,920, 115,440 and 461,280 reads of a group at 120, 240 and 480
    rows, 2 N squared + N. It asks the unit's own day and builds the places once a round: 26 reads a
    row, the unit's own and its day's 23 other hours in the same-clock search, its own in the
    other-clock search, and one to build its places."""
    _every_hour_settled(monkeypatch, "_weekday_units_merged", "_weekday_group", 26)


def _alternate_days(days: int) -> dict:
    """Days in turn holding 00:01 and 01:01 alone, and 01:01 and 02:01 twice each: the census as
    they stand and one value fewer kept. A pair from the first kind of day sends its 00:01 onto
    01:01 and needs a day holding 01:01 twice beside an hour 0, and none holds one; the second
    kind holds no unit alone."""
    ordinals: "list[int]" = []
    for day in range(days):
        start = (MONDAY_DAY + day) * DAY
        if day % 2 == 0:
            ordinals += [start + 60, start + HOUR + 60]
        else:
            ordinals += [start + HOUR + 60] * 2 + [start + 2 * HOUR + 60] * 2
    counts = [0] * 24
    for ordinal in ordinals:
        counts[ordinal % DAY // HOUR] += 1
    return _hours_case(ordinals, counts, days * 2 - 1, days)


def test_step_8_5_asks_only_the_cells_holding_a_source(monkeypatch: pytest.MonkeyPatch) -> None:
    """Step 8.5 grows with the rows where no pair exists (the Codex review, item 4). On the same
    state, one value long, every written unit is held alone, so a pair needs a written unit two
    ranks hold in its second cell, and none does: still every ordered pair of day cells was asked,
    36,000, 154,800 and 640,800 reads of its tables at 120, 240 and 480 rows, 2.875 N squared - 45
    N. The cells holding a lone or a shared unit of each group are indexed before a pair is asked,
    and only those are asked as the second cell, and only where a cell other than the first holds
    such a unit beside a place of the first's group (`lone_with`, `shared_with`): 27 reads a row,
    each day's cell asking its 24 groups for a lone unit and each of those the 23 other groups for
    a place, and its tables read 72 times as it is counted in. Where cells hold sources but none
    beside the place a pair needs, indexing the sources alone still asked every two cells: on days
    holding 00:01 and 01:01 alone in turn with days holding 01:01 and 02:01 twice each, 144, 244
    and 444 reads a day at 40, 80 and 160 days on 9cb2eb5. 119 a day now, to 13,334 days (40,002
    rows), the state left as it stood."""
    _every_hour_settled(monkeypatch, "_weekday_long_paired", "_weekday_first_of", 27)
    for days in (40, 80, 160, 13334):
        case = _alternate_days(days)
        calls = _counting_in(monkeypatch, "_weekday_long_paired", "_weekday_first_of")
        moved = _answer(case)
        monkeypatch.undo()
        assert calls[0] == 119 * days, (days, calls[0])
        assert moved == case["ordinals"], days


def _minutes_apart(ranks: int, apart: int) -> dict:
    """The Codex review's item 5 state: `ranks` ranks at `apart` minutes and a second from one
    another, one gap of `ranks * apart` minutes, a unit of a minute, seconds written, each hour a
    group with no period, the day kept, and one count of hour 0 asked in hour 1."""
    ordinals = [rank * apart * 60 + 1 for rank in range(ranks)]
    counts = [0] * 24
    for ordinal in ordinals:
        counts[ordinal % DAY // HOUR] += 1
    counts[0] -= 1
    counts[1] += 1
    return {
        "ordinals": ordinals, "lows": [0] * ranks, "highs": [ranks * apart * 60 - 1] * ranks,
        "pinned": [False] * ranks, "counts": counts, "where": list(range(24)), "unit": 60, "written_unit": 1,
        "day": DAY, "bin": "hour", "period": 0, "keep": "day", "pair": "", "pair_where": [], "holes": [],
        "reachable": True, "body": [0, ranks - 1], "wanted": ranks, "step": "settled",
    }


def test_the_index_holds_few_units_for_each_rank() -> None:
    """Steps 5 and 6's index holds no more units than one rank's walk asks, 801, or four for each
    movable rank, and the pass's kinds one for each day it asks (the Codex review, item 5). On the
    review's state -- 128 ranks 801 minutes apart, a gap of 102,528 minutes kept by the day -- the
    index held every one of its 102,528 units and a kind for each, 801 a rank; now it is not
    built, and the gap is walked. The same at the review's 64 ranks and at 1,280; and where the
    ranks stand three minutes apart the index is still built, three units a rank. The census
    holds in each, one value moved and no other."""
    for ranks, apart, built in ((128, 801, False), (64, 801, False), (1280, 801, False), (1000, 3, True)):
        case = _minutes_apart(ranks, apart)
        state = _state(case)
        generation._bins_settled(state, list(case["counts"]), 0, ranks - 1, list(case["pinned"]), ranks)
        indexes = [index for index in state.indexes.values() if index is not None]
        units = sum(len(found) for index in indexes for found in index.units.values())
        assert units <= max(801, 4 * ranks), (ranks, units)
        assert (units == ranks * apart) if built else (units == 0), (ranks, units)
        assert len(state.kinds) <= ranks * apart // 1440 + 1, (ranks, len(state.kinds))
        assert _holding(case, state.moved, range(ranks)) == case["counts"], ranks
        assert len(set(case["ordinals"]) - set(state.moved)) == len(set(state.moved) - set(case["ordinals"])) == 1, ranks


def _days_of_the_month_in_a_ring() -> dict:
    """The Codex review's item 6 state: ten groups of days of the month -- the first to the ninth
    each alone, the tenth to the thirty-first together -- two ranks each on 1 January, 2 February,
    3 March and 4 April 2024, their gaps ending on 2 January, 3 February, 4 March and 1 May, the
    census as they stand and eight different days asked."""
    firsts = [datetime.date(2024, month, month) for month in (1, 2, 3, 4)]
    lasts = [datetime.date(2024, 1, 2), datetime.date(2024, 2, 3), datetime.date(2024, 3, 4), datetime.date(2024, 5, 1)]
    epoch = datetime.date(1970, 1, 1)
    ordinals = [(first - epoch).days for first in firsts for _twice in (0, 1)]
    highs = [(last - epoch).days for last in lasts for _twice in (0, 1)]
    return {
        "ordinals": ordinals, "lows": list(ordinals), "highs": highs, "pinned": [False] * 8,
        "counts": [2, 2, 2, 2, 0, 0, 0, 0, 0, 0], "where": [min(day, 9) for day in range(31)], "unit": 1,
        "written_unit": 1, "day": 1, "bin": "day_of_month", "period": 0, "keep": "", "pair": "",
        "pair_where": [], "holes": [], "reachable": True, "body": [0, 7], "wanted": 8, "step": "settled",
    }


def test_a_cycle_of_four_groups_is_not_asked_above_seven(monkeypatch: pytest.MonkeyPatch) -> None:
    """The bound on step 8.3's cycles, kept and stated (the Codex review, item 6). On ten groups of
    days of the month, two ranks each on 1 January, 2 February, 3 March and 4 April, their gaps
    ending on 2 January, 3 February, 4 March and 1 May, and eight different days asked, only a
    cycle of four groups gains -- one rank of each day onto its gap's last day, which keeps every
    group's count and reaches eight -- and above seven groups none of more than three is asked: the
    search offers no cycle and the pass keeps four days. Asked with cycles of four, it reaches
    eight. The method's text and step 8.3's own docstring say no gaining cycle makes the count the
    most the census allows only where every cycle is asked and a unit is one written unit; on
    9cb2eb5 they said it of every census."""
    case = _days_of_the_month_in_a_ring()
    state = _state(case)
    assert generation._weekday_cycle(state, generation._weekday_cells(state, 0, 7, [False] * 8), 4) == []
    moved = _answer(case)
    assert _holding(case, moved, range(8)) == case["counts"]
    assert len(set(moved)) == 4
    reached = [case["highs"][rank] if rank % 2 else case["ordinals"][rank] for rank in range(8)]
    assert _holding(case, reached, range(8)) == case["counts"] and len(set(reached)) == 8
    four = _mutant(monkeypatch, "_WEEKDAY_CYCLE_LONGEST = 3", "_WEEKDAY_CYCLE_LONGEST = 4")
    assert len(set(_answer(case, four))) == 8
    method = (REPOSITORY / "docs" / "spec" / "generation-method-v1.md").read_text(encoding="utf-8")
    section = method[method.index("#### G7.3f "):method.index("### G7.4 ")]
    said = " ".join(section.split())
    assert "Where a unit is one written unit and every cycle is asked, the count" in said
    assert "SO A COUNT LEFT SHORT MAY BE BELOW THE MOST THE CENSUS ALLOWS where it has more than seven groups" in said
    assert "4 April, their gaps ending on 2 January, 3 February, 4 March and 1 May" in said
    docstring = " ".join(generation._weekday_exchanged.__doc__.split())
    assert "Where a unit is one written unit and every cycle is asked" in docstring
    assert "There a count left short may be below that most." in docstring
    assert "a gaining cycle of four groups or more is never asked" in " ".join(generation._weekday_cycle.__doc__.split())


def _a_trade_left_no_way_back() -> dict:
    """The second-census state the verification of the Codex review's item 1 noted (non-blocking):
    a day of moments, each weekday its own group and the half of the month a second census, a gap
    from Thursday 25 July 2024 15:44:27 to Friday 2 August 09:51:35 holding Friday 26 July
    05:47:46 twice, Monday 29 July 21:12:50 twice and 23:51:26 three times, Thursday 1 August
    19:04:15 three times and Friday 2 August 09:51:35 twice. The census asks one Thursday moment
    on a Saturday, and the gap's one Saturday, 27 July, stands in the other half of its month."""
    day = (datetime.date(2024, 7, 25) - datetime.date(1970, 1, 1)).days
    clocks = [(0, 15, 44, 27)] + [(1, 5, 47, 46)] * 2 + [(4, 21, 12, 50)] * 2 + [(4, 23, 51, 26)] * 3
    clocks += [(7, 19, 4, 15)] * 3 + [(8, 9, 51, 35)] * 3
    ordinals = [(day + days) * DAY + hours * HOUR + minutes * 60 + seconds for days, hours, minutes, seconds in clocks]
    return {
        "ordinals": ordinals, "lows": [ordinals[0]] * 13 + [ordinals[13]],
        "highs": [ordinals[0]] + [ordinals[13]] * 13, "pinned": [rank in (0, 13) for rank in range(14)],
        "counts": [5, 0, 0, 3, 5, 1, 0], "where": list(range(7)), "unit": DAY, "written_unit": 1,
        "day": DAY, "bin": "weekday", "period": 7, "keep": "", "pair": "day_of_month",
        "pair_where": [0] * 15 + [1] * 16, "holes": [], "reachable": True, "body": [0, 13],
        "wanted": 7, "step": "settled",
    }


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason=(
        "plan P4-D366's stated limit, owned by landing D3, the first to keep a second census: a "
        "cycle of step 8.3 and a merge of step 8.4 made before step 8.6 can leave it no way back, "
        "and the census is missed where 9cb2eb5 met it; step 8.6 asked first meets this state "
        "but measured worse over states keeping the half of the month, so the order stays"
    ),
)
def test_a_trade_keeps_a_way_back_once_the_count_is_put_back() -> None:
    """Strict, and owned by landing D3 (P4-D366's limit). Step 8.3, its take counting written
    units since the Codex review's item 1, moves Friday 26 July 05:47:46 to Monday 29 July and
    Monday 23:51:26 to Friday 26 July, a gain of two where one is asked, and step 8.4 merges the
    other Friday moment onto 23:51:26: each Friday moment of July now stands at 23:51:26, whose
    Friday in the first half of August, the 2nd, lies past the gap's close, and no Monday of
    August is in the gap, so step 8.6 has no second move into August and the Thursday moment
    never reaches Saturday 27 July. 9cb2eb5's take found no cycle, so its step 8.6 traded. D3's
    battery turns this into a passing test, or restates it."""
    case = _a_trade_left_no_way_back()
    moved = _answer(case)
    assert len(set(moved)) == case["wanted"]
    assert _holding(case, moved, range(len(moved))) == case["counts"]


def _a_chain_asked_of_its_mover_alone() -> dict:
    """A second-census state the repair of the verification of the Codex review's item 1 found in
    its own battery of states keeping the half of the month: a day of moments, the groups Monday
    to Wednesday, Thursday and Friday, and Saturday and Sunday, a gap from Sunday 28 April 2024
    20:11:04 to Thursday 2 May 04:11:48 holding Monday 29 April 12:41:51 twice and 20:25:45 twice
    and Thursday 2 May 04:11:48, and a gap of that Thursday to 11:06:36. The census asks one
    Thursday moment on a Saturday or a Sunday, as the battery drew it."""
    day = (datetime.date(2024, 4, 28) - datetime.date(1970, 1, 1)).days
    clocks = [(0, 20, 11, 4)] + [(1, 12, 41, 51)] * 2 + [(1, 20, 25, 45)] * 2 + [(4, 4, 11, 48)] * 5
    clocks += [(4, 11, 6, 36)] * 2
    ordinals = [(day + days) * DAY + hours * HOUR + minutes * 60 + seconds for days, hours, minutes, seconds in clocks]
    return {
        "ordinals": ordinals, "lows": [ordinals[0]] * 6 + [ordinals[5]] * 5 + [ordinals[11]],
        "highs": [ordinals[0]] + [ordinals[5]] * 8 + [ordinals[11]] * 3,
        "pinned": [rank in (0, 6, 8, 11) for rank in range(12)], "counts": [4, 6, 2],
        "where": [0, 0, 0, 1, 1, 2, 2], "unit": DAY, "written_unit": 1, "day": DAY,
        "bin": "weekday", "period": 7, "keep": "", "pair": "day_of_month",
        "pair_where": [0] * 15 + [1] * 16, "holes": [], "reachable": True, "body": [0, 11],
        "wanted": 20, "step": "settled",
    }


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason=(
        "plan P4-D366's stated limit, owned by landing D3, the first to keep a second census: "
        "step 7b's link is asked of each cell's mover alone, and where the rank beside the mover "
        "has the place the mover lacks, no chain reaches that group and the census is missed "
        "where 9cb2eb5's chain, asked by unit, moved half way and step 8.6 traded the rest"
    ),
)
def test_a_chain_reaches_a_group_through_the_rank_beside_its_mover() -> None:
    """Strict, and owned by landing D3 (P4-D366's limit). Since the Codex review's item 1, step
    7b asks the link from Monday to Wednesday to Saturday and Sunday of the cell's mover alone:
    Monday 12:41:51, the lower rank where two seconds are held twice each, whose Sunday, 28 April
    12:41:51, stands before the gap opens. Monday 20:25:45 has Sunday 20:25:45 but is not asked,
    and the Thursday moment's own Sunday, 04:11:48, stands before the gap too, so no chain is
    found, step 8.6 has no trade from Thursday, and the census is missed. 9cb2eb5 asked the link
    of the unit, moved the Thursday moment to Wednesday 1 May and found no Sunday place for the
    Monday mover; its step 8.6 then traded Tuesday 30 April 20:25:45, where step 8.1 had put it,
    to Sunday 28 April, inside the same half of the month. D3's battery turns this into a passing
    test, or restates it."""
    case = _a_chain_asked_of_its_mover_alone()
    moved = _answer(case)
    assert _holding(case, moved, range(len(moved))) == case["counts"]


def _a_trade_emptying_a_held_second() -> dict:
    """The state the third verification of the Codex review's item 1 found among 120,000 random
    states of its own generator (its 6717): a day of moments, seconds written, the groups Thursday;
    Tuesday; Sunday; Monday; Wednesday and Saturday; and Friday, a second census of the day of the
    month in six groups (the 1st to the 6th, 7th to 15th, 16th and 17th, 18th to 20th, 21st to
    27th and 28th to 31st), and 124 moments at 05:19:54, 16:45:06 and 19:49:00 of every day from
    Sunday 11 to Sunday 18 January 2026. The first, Sunday 11 January's second 19:49:00 and the
    last are pinned, the ten moments of that Sunday between the first two in a gap of that day
    alone. The census asks 10, 19, 37, 18, 28 and 12, and 23 different values are asked."""
    day = (datetime.date(2026, 1, 11) - datetime.date(1970, 1, 1)).days
    clocks = ((5, 19, 54), (16, 45, 6), (19, 49, 0))
    held = ((1, 9, 2), (7, 8, 5), (5, 4, 7), (5, 6, 4), (4, 6, 5), (3, 9, 4), (4, 6, 5), (5, 2, 8))
    ordinals = [
        (day + days) * DAY + hours * HOUR + minutes * 60 + seconds
        for days, times in enumerate(held)
        for (hours, minutes, seconds), many in zip(clocks, times)
        for _time in range(many)
    ]
    return {
        "ordinals": ordinals, "lows": [ordinals[0]] * 11 + [ordinals[10]] * 112 + [ordinals[123]],
        "highs": [ordinals[0]] + [ordinals[10]] * 11 + [ordinals[123]] * 112,
        "pinned": [rank in (0, 11, 123) for rank in range(124)], "counts": [10, 19, 37, 18, 28, 12],
        "where": [3, 1, 4, 0, 5, 4, 2], "unit": DAY, "written_unit": 1, "day": DAY,
        "bin": "weekday", "period": 7, "keep": "", "pair": "day_of_month",
        "pair_where": [0] * 6 + [1] * 9 + [2] * 2 + [3] * 3 + [4] * 7 + [5] * 4, "holes": [],
        "reachable": True, "body": [0, 123], "wanted": 23, "step": "settled",
    }


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason=(
        "plan P4-D366's stated limits, owned by landing D3, the first to keep a second census: "
        "with no chain left half made, step 8.6's trade empties a value 9cb2eb5's trade kept, "
        "and the count is left one short with the census met"
    ),
)
def test_a_trade_meets_the_census_and_keeps_the_count() -> None:
    """Strict, and owned by landing D3 (P4-D366's limits, as the third verification of the Codex
    review's item 1 found them). Steps 1 to 7 leave the census missed by four ranks each way, and
    the 23 values asked. 9cb2eb5's step 7b moved Friday 16 January 16:45:06 to Saturday and stopped there, its
    chain half made, and its step 8.6 then met the census moving three of the four Friday 19:49:00
    moments to Sunday 11 January, the fourth kept: 23 values. The head's step 7b finds no chain,
    its step 8.6 moves all four Friday 19:49:00 moments, and steps 8.1 to 8.5, run again, put no
    value back: the census met and 22 values. D3's battery turns this into a passing test, both
    facts met, or restates it."""
    case = _a_trade_emptying_a_held_second()
    moved = _answer(case)
    assert _holding(case, moved, range(case["body"][0], case["body"][1] + 1)) == case["counts"]
    assert len(set(moved)) == case["wanted"]


def _a_chain_meeting_the_census_one_long() -> dict:
    """The state the third verification of the Codex review's item 1 found among 80,000 random
    states of the second verification's generator (its 15920): a day of moments, seconds written,
    the groups Monday, Tuesday, Wednesday, Thursday, and Friday to Sunday, the half of the month
    kept as a second census, and 111 moments from Friday 28 March to Sunday 20 April 2025 at seven
    places -- 17 at Friday 28 March 01:18:32, 16 at Tuesday 1 April 01:18:32, 17 at Wednesday 9
    April 07:43:07, 14 at Sunday 13 April 05:26:19, 21 at Thursday 17 April 01:18:32, 11 at Friday
    18 April 07:43:07 and 15 at Sunday 20 April 02:40:52 -- in four gaps between pinned moments
    of 28 March, 9, 17 and 18 April and 20 April. The census, of the moments from the second to
    the last but one, asks 0, 16, 17, 21 and 55, and 8 different values are asked."""
    day = (datetime.date(2025, 3, 28) - datetime.date(1970, 1, 1)).days
    places = (
        (0, 1, 18, 32, 17), (4, 1, 18, 32, 16), (12, 7, 43, 7, 17), (16, 5, 26, 19, 14),
        (20, 1, 18, 32, 21), (21, 7, 43, 7, 11), (23, 2, 40, 52, 15),
    )
    ordinals = [
        (day + days) * DAY + hours * HOUR + minutes * 60 + seconds
        for days, hours, minutes, seconds, many in places
        for _time in range(many)
    ]
    first, ninth, seventeenth, eighteenth, last = (ordinals[spot] for spot in (0, 33, 64, 85, 96))
    return {
        "ordinals": ordinals,
        "lows": [first] * 47 + [ninth] * 18 + [seventeenth] * 28 + [eighteenth] * 16 + [last] * 2,
        "highs": [first] * 2 + [ninth] * 46 + [seventeenth] * 18 + [eighteenth] * 28 + [last] * 17,
        "pinned": [rank in (0, 1, 47, 65, 93, 109, 110) for rank in range(111)],
        "counts": [0, 16, 17, 21, 55], "where": [0, 1, 2, 3, 4, 4, 4], "unit": DAY,
        "written_unit": 1, "day": DAY, "bin": "weekday", "period": 7, "keep": "",
        "pair": "day_of_month", "pair_where": [0] * 15 + [1] * 16, "holes": [], "reachable": True,
        "body": [1, 109], "wanted": 8, "step": "settled",
    }


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason=(
        "plan P4-D366's stated limits, owned by landing D3, the first to keep a second census: "
        "step 7b's chain, made whole, meets the census before step 8, and steps 8.1 to 8.5 leave "
        "one value more than asked where 9cb2eb5's trade met both facts"
    ),
)
def test_a_chain_meets_the_census_and_the_count_is_still_put_back() -> None:
    """Strict, and owned by landing D3 (P4-D366's limits, as the third verification of the Codex
    review's item 1 found them). Steps 1 to 7 leave the census missed by one rank each way, and 13
    values.
    9cb2eb5's step 7b moved nothing: steps 8.1, 8.4 and 8.5 merged the values to the 8 asked,
    step 8.6 traded two ranks to meet the census, and step 8.5, run again, merged the two values
    the trade had made: both facts. The head's step 7b chain, made whole, moves Sunday 13 April
    05:26:19 to Tuesday 15 April and Tuesday 1 April 01:18:32 to Wednesday 2 April and meets the
    census with 14 values, and steps 8.1, 8.4 and 8.5 merge them only to 9: one value long. D3's
    battery turns this into a passing test, both facts met, or restates it."""
    case = _a_chain_meeting_the_census_one_long()
    moved = _answer(case)
    assert _holding(case, moved, range(case["body"][0], case["body"][1] + 1)) == case["counts"]
    assert len(set(moved)) == case["wanted"]


# The steps of the pass that move ranks, each called by its name from `_bins_settled` or from
# step 8's `_weekday_count_kept`.
MOVING_STEPS = (
    "_weekday_holes_swept", "_weekday_runs_moved", "_weekday_singles_moved", "_weekday_chained",
    "_weekday_repaired", "_weekday_exchanged", "_weekday_units_merged", "_weekday_long_paired",
    "_weekday_traded",
)


def _off_the_written_time(monkeypatch: pytest.MonkeyPatch, case: dict, module=generation) -> "list[str]":
    """Each step of the pass watched through a case: a line for every rank a step leaves at
    another written time of day than it found it at, and for every rank step 8.4 or 8.5 moves."""
    found: "list[str]" = []
    written = case["written_unit"]

    def watched(name: str, step):
        def run(state, *arguments):
            nonlocal found
            before = list(state.moved)
            answer = step(state, *arguments)
            for rank, (was, now) in enumerate(zip(before, state.moved)):
                if was % DAY // written != now % DAY // written or (
                    was != now and name in ("_weekday_units_merged", "_weekday_long_paired")
                ):
                    found += [f"{name}: rank {rank} from {was} to {now}"]
            return answer

        return run

    for name in MOVING_STEPS:
        monkeypatch.setattr(module, name, watched(name, getattr(module, name)))
    _answer(case, module)
    return found


def test_every_step_keeps_the_written_time_of_day_on_the_held_minute(monkeypatch: pytest.MonkeyPatch) -> None:
    """P4-D366's third limit, its clause restated at the third verification of the Codex review's
    item 1: no placement of the held-minute state (`_a_chain_made_whole_on_a_held_minute`,
    below) keeping every moment's written time of day meets both facts, and no move of the pass
    leaves those placements there. On a day of moments a move takes a rank a whole number of
    days, or every rank of a written unit together onto one place at its written time of day, but
    step 8.4's second place and step 8.5, which join an ordinal another rank stands on, keep every
    group's count and run only where the count is long, never on this state: every step leaves
    each moment at the minute of the day it found it at, and steps 8.4 and 8.5 move no rank.
    Mutant: the indexed search drops the rank's place inside its unit, and step 5 takes two Sunday
    09:52 moments to Friday at midnight."""
    case = _a_chain_made_whole_on_a_held_minute()
    assert _off_the_written_time(monkeypatch, case) == []
    mutant = _mutant(monkeypatch, "    return unit, place, first, last\n", "    return unit, 0, first, last\n")
    assert _off_the_written_time(monkeypatch, case, mutant)[:2] == [
        f"_weekday_runs_moved: rank {rank} from {case['ordinals'][13]} to {case['ordinals'][0] // DAY * DAY}"
        for rank in (13, 14)
    ]


def _a_chain_made_whole_on_a_held_minute() -> dict:
    """The state the second verification of the Codex review's item 1 found among 140,000 random
    states (its 11902): a day of moments, minutes written, no second census, the groups Monday,
    Tuesday, Wednesday to Friday, Saturday and Sunday, and Tuesday 23 to Thursday 25 April 2024
    holes. A gap from Friday 19 April 04:36 to Thursday 25 April 12:30 holds Friday 04:36 three
    times, 09:52, 12:30 twice and 13:33:04 three times, Saturday 02:08 twice and 12:30, Sunday
    09:52 twice, Monday 02:08 and 13:33:04 twice, Tuesday 13:33:04 twice, Wednesday 02:08 twice
    and 13:33:04, and Thursday 02:08 three times; Friday 04:36 once more, Thursday 12:30 and
    Thursday 13:33:04 are pinned, and Thursday 12:30 and 13:33:04 stand once more in a gap of that
    Thursday alone. The census asks 3, 0, 20, 5 and 2, and 13 different minutes are asked."""
    day = (datetime.date(2024, 4, 19) - datetime.date(1970, 1, 1)).days
    clocks = [(0, 4, 36, 0)] * 4 + [(0, 9, 52, 0)] + [(0, 12, 30, 0)] * 2 + [(0, 13, 33, 4)] * 3
    clocks += [(1, 2, 8, 0)] * 2 + [(1, 12, 30, 0)] + [(2, 9, 52, 0)] * 2 + [(3, 2, 8, 0)]
    clocks += [(3, 13, 33, 4)] * 2 + [(4, 13, 33, 4)] * 2 + [(5, 2, 8, 0)] * 2 + [(5, 13, 33, 4)]
    clocks += [(6, 2, 8, 0)] * 3 + [(6, 12, 30, 0)] * 2 + [(6, 13, 33, 4)] * 2
    ordinals = [(day + days) * DAY + hours * HOUR + minutes * 60 + seconds for days, hours, minutes, seconds in clocks]
    return {
        "ordinals": ordinals, "lows": [ordinals[0]] * 26 + [ordinals[26]] * 3 + [ordinals[29]],
        "highs": [ordinals[0]] + [ordinals[26]] * 26 + [ordinals[29]] * 3,
        "pinned": [rank in (0, 26, 29) for rank in range(30)], "counts": [3, 0, 20, 5, 2],
        "where": [0, 1, 2, 2, 2, 3, 4], "unit": DAY, "written_unit": 60, "day": DAY,
        "bin": "weekday", "period": 7, "keep": "", "pair": "", "pair_where": [],
        "holes": [day + 4, day + 5, day + 6], "reachable": True, "body": [0, 29], "wanted": 13,
        "step": "settled",
    }


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason=(
        "plan P4-D366's third stated limit, owned by landing D2, the first to publish a weekday "
        "census of moments: no placement of this state keeping every moment's clock meets both "
        "the census and the count, and step 7b's chain, made whole through the mover its link "
        "was asked of, halves 9cb2eb5's miss of the census at the cost of one of the 13 minutes "
        "asked, the census still missed"
    ),
)
def test_a_chain_spends_a_value_only_where_the_census_is_then_met() -> None:
    """Strict, and owned by landing D2 (P4-D366's third limit). Steps 1 to 7 leave Monday two over
    and Wednesday to Friday two under, and no Monday rank has a place from Wednesday to Friday:
    each stands at 02:08, before the gap opens on Friday 19 April, and Wednesday and Thursday are
    holes. Step 7b's chain moves Monday 22 April 02:08 to Sunday, where 02:08, held twice now, is
    Sunday's mover and has no such place either, so the move takes the mover the link was asked
    of, the lone Sunday 21 April 13:33:04, onto Friday 19 April 13:33:04, which six ranks hold:
    the census is missed by one rank each way, and 12 different minutes are kept. 9cb2eb5's chain,
    its link asked by unit, linked Monday straight to Wednesday to Friday and could not move a
    Monday rank there, and the repairs before ba15cc3 left it half made, the census missed by two
    ranks each way and the 13 minutes asked kept. No placement inside the gaps and off the holes
    that keeps every moment's written time of day meets both facts -- with the census met at most
    11 different minutes, with one rank each way 12 -- and no move of the pass leaves those
    placements: on a day of moments the only moves that change a moment's written time of day,
    step 8.4's second place and step 8.5, join an ordinal a rank stands on, keep every group's
    count and run only where the count is long, never on this state
    (`test_every_step_keeps_the_written_time_of_day_on_the_held_minute`). So the chain trades a
    minute for half the miss of the method's first fact, and the census, reachable so, is missed
    on every commit. A moment taking another clock on its gap's first day meets both, Monday 02:08
    at Friday 04:37, the move landing D2's step 7c is reserved for (P4-D367). D2's battery turns
    this into a passing test, the census met or the count kept where it is missed, or restates
    it."""
    case = _a_chain_made_whole_on_a_held_minute()
    moved = _answer(case)
    met = _holding(case, moved, range(len(moved))) == case["counts"]
    assert met or len({ordinal // case["written_unit"] for ordinal in moved}) == case["wanted"]
