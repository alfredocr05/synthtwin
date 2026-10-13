"""Lane D4s (plan P4-D369 part one): G7.3's count pass splits the two tails' ranks first, and the day-count items owed to lane D4.

Where a column's different values are too few, the count pass splits
ranks sharing a unit onto free units inside their gaps. It split nearest
first, then the lower rank, so a body rank a day from a free day split
before a high tail rank whose free day stood further: on logs just above
one row an open day the body passed what the weekday census lets it
reach, the high tail kept fewer days than its most, and the day pass
took the body's extra days back -- P4-D388's pinned near-one log came
back a value or two short at seven seeds of ten, and P4-D367's midnight
twins a day or two short with nothing named on an ISO member. The pass
now offers every rank of the two tails (`generation._tail_ranks`) its
nearest free unit first, then the body's, each nearest first and then
the lower rank. The pinned near-one log keeps its census and every
value at seeds 0 to 9 (`tests/test_stage3b_count_room.py` and
`tests/test_stage3b_weekday_moments.py`), and the frozen case
`tails_split_first` holds the order beside the oracle.

THE ITEMS LANE D4 WAS OWED THAT THE ORDER DOES NOT REACH, each a strict
expected failure naming its measured cause: the seven-day logs, whose
rebuilt tail ends one or two days inside the real end, so the strata
hold fewer days than the real tails while the body holds every day; the
fifteen Mondays at the floor of 36, whose rebuilt tails hold at least 30
days for the column's 15; and the Tuesday-to-Thursday clinic at the
floor of 11, whose body draws past the expectation the count rules read,
so the pass merges where the rules read a split.

Each test names the mutation that turns it red.
"""

from __future__ import annotations

import json
import pathlib
import types
import typing

import pytest

import kpi_shapes
from synthtwin import calendar_rules, contract, generation
import test_stage3b_count_room as count_room

_ROOT = pathlib.Path(__file__).resolve().parents[1]


def _layout(low: int, high: int) -> "generation._DateLayout":
    """A stand-in layout holding only what `_tail_ranks` reads: each tail's rows and side."""
    return typing.cast(
        "generation._DateLayout",
        types.SimpleNamespace(
            low=types.SimpleNamespace(rows=low, low_side=True) if low else None,
            high=types.SimpleNamespace(rows=high, low_side=False) if high else None,
        ),
    )


def test_the_tail_ranks_are_the_first_and_last_rows_of_the_two_tails() -> None:
    """`_tail_ranks` names the low tail's first rows and the high tail's last rows, and nothing without a layout.

    Mutation: the high tail's ranks counted from the start, or a tail's
    rows off by one, turns this red.
    """
    assert generation._tail_ranks(_layout(3, 2), 12) == frozenset({0, 1, 2, 10, 11})
    assert generation._tail_ranks(_layout(0, 2), 12) == frozenset({10, 11})
    assert generation._tail_ranks(None, 12) == frozenset()


def _state() -> "dict[str, typing.Any]":
    """Fourteen ranks of whole days, two pairs sharing a day and the count one short.

    Ranks 0 to 2 are a low tail and 9 to 13 a high tail. Body rank 5
    shares day 50 with rank 4, which cannot move, and has day 51 free one
    day off; high tail rank 10 shares day 100 with rank 9, which cannot
    move, and its nearest free day is 103, three days off, ranks 11 and
    12 holding 101 and 102. The count wants one more day, so one rank
    splits.
    """
    moved = [10, 12, 14, 40, 50, 50, 60, 70, 90, 100, 100, 101, 102, 110]
    lows = [10, 12, 14, 40, 50, 50, 55, 65, 85, 100, 100, 101, 102, 110]
    highs = [10, 12, 14, 44, 50, 51, 64, 75, 95, 100, 103, 101, 102, 110]
    pinned = [True, False, True] + [False] * 10 + [True]
    return {"moved": moved, "lows": lows, "highs": highs, "pinned": pinned, "wanted": len(set(moved)) + 1}


def _split(state: "dict[str, typing.Any]", tails: "frozenset[int]") -> "list[int]":
    moved = list(state["moved"])
    generation._distinct_reached(
        typing.cast(contract.DatetimeFacts, None), moved, list(state["pinned"]), state["lows"], state["highs"],
        1, 1, state["wanted"], False, "", frozenset(), tails,
    )
    return moved


def test_the_count_pass_splits_a_tail_rank_before_a_nearer_body_rank() -> None:
    """Too few different days: the high tail's rank splits three days out before the body's rank one day out.

    With no tail named the pass splits as it did before lane D4s: the body
    rank, one day from its free day, goes first and the count is met
    there, the high tail keeping one day fewer than it can hold.
    Mutation: the tails' ranks not put first (the sort's first key
    dropped), or the tail set not handed on, turns this red.
    """
    state = _state()
    tails = generation._tail_ranks(_layout(3, 5), 14)
    assert _split(state, tails) == [10, 12, 14, 40, 50, 50, 60, 70, 90, 100, 103, 101, 102, 110]
    assert _split(state, frozenset()) == [10, 12, 14, 40, 50, 51, 60, 70, 90, 100, 100, 101, 102, 110]


def test_the_split_order_s_work_grows_with_the_shared_ranks_not_the_column(monkeypatch: pytest.MonkeyPatch) -> None:
    """Machine-free: up to a million ranks, the tail set costs one step a tail row and the splits one search a shared rank.

    A column of N whole days, each rank alone on its day but fifty, each
    of which shares its neighbour's day and has its own free, its first
    and last 1,000 ranks two tails: the count wants the fifty days back.
    `_tail_rank_of` runs once per tail row whatever N is, and the free-unit
    search once per shared rank and once more per split taken, at 1,000,
    10,000, 100,000 and 1,000,000 ranks alike. Mutation: the tail set's
    walk visiting more than its tail rows, or the shared ranks searched
    afresh per split taken, turns this red. The test builds the tail set
    by hand and runs no `_units_settled`, so it does not see where that
    function builds the set.
    """
    calls = {"rank_of": 0, "search": 0}
    rank_of = generation._tail_rank_of
    search = generation._nearest_free_unit

    def counted_rank_of(*arguments: typing.Any) -> int:
        calls["rank_of"] += 1
        return rank_of(*arguments)

    def counted_search(*arguments: typing.Any) -> "int | None":
        calls["search"] += 1
        return search(*arguments)

    monkeypatch.setattr(generation, "_tail_rank_of", counted_rank_of)
    monkeypatch.setattr(generation, "_nearest_free_unit", counted_search)
    for size in (1_000, 10_000, 100_000, 1_000_000):
        calls["rank_of"] = 0
        calls["search"] = 0
        tails = generation._tail_ranks(_layout(1_000, 1_000), size)
        assert calls["rank_of"] == 2_000, (size, calls)
        moved = list(range(size))
        step = size // 50
        shared = [step * place + step // 2 for place in range(50)]
        for rank in shared:
            moved[rank] = rank - 1
        lows = [rank - 1 for rank in range(size)]
        highs = [rank + 1 for rank in range(size)]
        pinned = [False] * size
        generation._distinct_reached(
            typing.cast(contract.DatetimeFacts, None), moved, pinned, lows, highs, 1, 1, size, False, "",
            frozenset(), tails,
        )
        assert len(set(moved)) == size, size
        assert calls["search"] <= 2 * 2 * len(shared), (size, calls)


def _most_held(ranks: "list[int]", lows: "list[int]", highs: "list[int]") -> int:
    """The most different days `ranks` can stand on, each inside its own span: earliest end first, earliest free day."""
    taken: "dict[int, bool]" = {}
    for rank in sorted(ranks, key=lambda each: (highs[each], lows[each])):
        for day in range(lows[rank], highs[rank] + 1):
            if day not in taken:
                taken[day] = True
                break
    return len(taken)


def test_the_body_splits_once_no_tail_rank_can_split_directly_which_is_not_the_most_the_tails_could_hold(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The Codex review of lane D4s: the tails first exhaust their DIRECT splits, not the most their strata hold.

    `_every_open_day(1.1, 26, 900, Monday to Friday)` at the floor of 36,
    seed 3: 142 rows on 130 days, its weekday census published. The count
    pass splits, and the two tails' 36 ranks each could stand on 36
    different days inside their own spans; the pass takes (low, body,
    high) from (34, 48, 35) to (36, 59, 35). High tail rank 107 shares day
    19129 with pinned rank 106, and its one other day, 19130, holds rank
    108 alone, whose span reaches the free day 19131: moving 108 there
    would let 107 split onto 19130, a chain the pass does not make, so the
    body takes the day the high tail could have held. No tail rank left
    sharing a day has a free day inside its own span, the twin still holds
    the column's 130 days, and the order before lane D4s gives 130 too.
    The texts that state the order -- the contract, P4-D369, G7.3, the
    docstrings of `tails_kept`, `count_reach_short` and
    `_distinct_reached`, the count-room module, K-S3-59's evidence, the
    changelog and the oracle's why of the frozen case `tails_split_first`
    (from the verification of the Codex fix) -- say the body splits only
    once no tail rank sharing a day can split directly, which is not the
    most the tails could hold, and no longer that no body rank splits
    while a tail rank still can. Red where a text claims that again or
    drops the difference, or where the pass starts making the chain (the
    high tail reaching 36).
    """
    cells = count_room._every_open_day(1.1, 26, 900, frozenset(range(5)))
    assert (len(cells), len(set(cells))) == (142, 130)
    described = count_room._described(tmp_path, "chain", cells, 36)
    assert described.block("visit")["weekday_census"]
    reached = generation._distinct_reached
    seen: "list[tuple[typing.Any, ...]]" = []

    def watched(*arguments: typing.Any) -> bool:
        before = list(arguments[1])
        changed = reached(*arguments)
        seen.append((before, list(arguments[1]), *arguments[2:5], arguments[11]))
        return changed

    monkeypatch.setattr(generation, "_distinct_reached", watched)
    twin = generation.generate(described.loaded, 3)
    assert len(set(cell for cell in twin.columns[0] if cell)) == 130
    before, after, pinned, lows, highs, tails = seen[0]
    low = sorted(rank for rank in tails if rank < len(after) // 2)
    high = sorted(rank for rank in tails if rank >= len(after) // 2)
    body = [rank for rank in range(len(after)) if rank not in tails]

    def parts(moved: "list[int]") -> "tuple[int, int, int]":
        return tuple(len({moved[rank] for rank in group}) for group in (low, body, high))  # type: ignore[return-value]

    assert (len(low), len(high)) == (36, 36)
    assert (parts(before), parts(after)) == ((34, 48, 35), (36, 59, 35))
    assert (_most_held(low, lows, highs), _most_held(high, lows, highs)) == (36, 36)
    held: "dict[int, int]" = {}
    for day in after:
        held[day] = (held[day] if day in held else 0) + 1
    for rank in low + high:
        if held[after[rank]] > 1 and not pinned[rank]:
            assert all(day in held for day in range(lows[rank], highs[rank] + 1)), rank
    assert (after[106], after[107], pinned[106], highs[107]) == (19129, 19129, True, 19130)
    assert (after[108], held[19130], highs[108], 19131 in held) == (19130, 1, 19131, False)
    monkeypatch.setattr(generation, "_distinct_reached", reached)
    monkeypatch.setattr(generation, "_tail_ranks", lambda layout, parsed: frozenset())
    before_d4s = generation.generate(described.loaded, 3)
    assert len(set(cell for cell in before_d4s.columns[0] if cell)) == 130
    plan = (_ROOT / "docs" / "plans" / "phase-4-columns.md").read_text(encoding="utf-8")
    begin = plan.index("## Decision P4-D369")
    method = (_ROOT / "docs" / "spec" / "generation-method-v1.md").read_text(encoding="utf-8")
    changelog = (_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    start = changelog.index("### The count pass splits the tails first")
    ledger = json.loads((_ROOT / "tests" / "kpi" / "ledger.json").read_text(encoding="utf-8"))
    entry = [item for item in ledger["entries"] if item["id"] == "K-S3-59"][0]
    vectors = json.loads(
        (_ROOT / "tests" / "reference" / "generation-branch-vectors-14.json").read_text(encoding="utf-8")
    )
    texts = (
        ("the contract", (_ROOT / "docs" / "spec" / "profile-contract-v6.md").read_text(encoding="utf-8")),
        ("P4-D369", plan[begin : plan.index("\n## ", begin)]),
        ("G7.3", [part for part in method.split("\n\n") if "THE TWO TAILS' RANKS" in part][0]),
        ("tails_kept", calendar_rules.tails_kept.__doc__ or ""),
        ("count_reach_short", calendar_rules.count_reach_short.__doc__ or ""),
        ("_distinct_reached", reached.__doc__ or ""),
        ("the count-room module", count_room.__doc__ or ""),
        ("K-S3-59", entry["evidence"]),
        ("the changelog", changelog[start : changelog.index("\n### ", start)]),
        ("the oracle's why", vectors["cases"]["tails_split_first"]["why"]),
    )
    for name, text in texts:
        flat = " ".join(text.split())
        assert "no tail rank sharing a day can split directly" in flat, name
        assert "not the most the tails could hold" in flat, name
        for old in (
            "while a tail rank still can",
            "the tails can split no further",
            "every day their strata give",
            "so the tails reach their most before the body",
        ):
            assert old not in flat, (name, old)


# THE ITEMS THE SPLIT ORDER DOES NOT REACH (P4-D369 part one), each a
# strict expected failure naming its measured cause.


@pytest.mark.xfail(
    strict=True,
    reason="P4-D369 part one, item 3, measured: on seven-day logs holding every day the rebuilt tail's end "
    "(G7.3b step 5) stands one or two days inside the real end, so its strata hold fewer days than the real "
    "tail while the body holds every day between its boundaries; every short tail's real distances lie inside "
    "G12.14's summed window, but no step moves a tail rank past its stratum where the count is short",
)
def test_a_seven_day_log_holding_every_day_comes_back_with_every_day(tmp_path: typing.Any) -> None:
    """`_every_open_day(2.0, 52, 91, every day)` at the floor of 11: 779 rows on all 364 days.

    Its low tail's twelve rows stand one to six days out, the rebuilt end
    five: the twin's tails hold 5 and 6 days for the real 6 and 6, and
    every twin at seeds 0 to 2 holds 363 different values for 364.
    """
    cells = count_room._every_open_day(2.0, 52, 91, frozenset(range(7)))
    described = count_room._described(tmp_path, "seven", cells, 11)
    for seed in (0, 1, 2):
        twin = generation.generate(described.loaded, seed)
        assert len(set(cell for cell in twin.columns[0] if cell)) == 364, seed


@pytest.mark.xfail(
    strict=True,
    reason="P4-D369 part one, item 4, measured: fifteen Mondays at the floor of 36 publish both tails' two "
    "distances over 40 rows each, and G7.3b rebuilds each tail on at least 15 different days whatever its "
    "draws (`tails_fewest` 30 for the two), twice the column's 15; the census is not the cause",
)
def test_fifteen_mondays_at_the_floor_of_36_come_back_with_fifteen_values(tmp_path: typing.Any) -> None:
    """The twins of fifteen Mondays at 36 hold 33 different values for 15 (P4-D388), with or without the census."""
    described = count_room._described(tmp_path, "mondays", count_room._mondays(), 36)
    for seed in (0, 1, 2):
        assert len(set(generation.generate(described.loaded, seed).columns[0])) == 15, seed


@pytest.mark.xfail(
    strict=True,
    reason="P4-D369 part one, item 4, measured: the count rules read the body's draw at its expectation "
    "(`calendar_rules.body_draw`) and read a split on this Tuesday-to-Thursday clinic; at seeds 2, 4, 6 and 8 "
    "its twin draws 137 to 139 different days for its 135, the count pass merges and takes the low tail to 8 or "
    "9 of its 11 days, and the twin comes back one or two values short, both distinct counts MISSED",
)
def test_a_clinic_whose_body_draws_past_its_expectation_keeps_its_count(tmp_path: typing.Any) -> None:
    """`_every_open_day(1.15, 45, 5459, Tuesday to Thursday)` at the floor of 11 (P4-D388's fresh clinic).

    Published, its census Tuesday, Wednesday and Thursday; its twins at
    seeds 0 to 9 hold the column's 135 different values.
    """
    cells = count_room._every_open_day(1.15, 45, 5459, frozenset({1, 2, 3}))
    assert (len(cells), len(set(cells))) == (165, 135)
    described = count_room._described(tmp_path, "clinic", cells, 11)
    assert described.block("visit")["weekday_census"]
    for seed in range(10):
        written = kpi_shapes.twin_text(described, seed)
        assert kpi_shapes.missed(kpi_shapes.measure(described, written, f"clinic-{seed}.csv")) == [], seed
