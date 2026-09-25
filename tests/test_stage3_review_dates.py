"""The seven date and clock items of stage 3's review round, each measured.

THE ROUND DOES NOT RUN AGAIN (owner, 2026-09-12: one review round per
landing), so every repair here is proved by the reproduction the review
gave for it, run through the product's own path -- the real reader, the
real producer, the strict loader, the real generator and the real
validator, with nothing stubbed -- and each one carries the MUTATION
that withdraws its rule, because a guard that cannot fail is not a
guard.

The seven, in the round's own numbering:

4. **The all-different obligation was silently abandoned.** 100 unique
   months and 100 consecutive quarters came back holding 74 different
   values at seed 4 with no deviation and no missed obligation, because
   G7.3's count pass never ran on those two resolutions; a clock column
   of 100 different times was met by a file holding 99, and a 200-value
   datetime column with a fully published `+02:00` offset by a file
   holding 29, because an envelope stood where G11 fixes the count.
5. **Clock generation invented declared missing cells.** With `08:00`
   declared missing and eleven such cells, seeds 0, 3 and 7 wrote twelve.
6. **A sparse mixed-date column lost its separator census.** Seed 4's
   distinctness repair turned one `T` into a space, and eleven became
   ten beside one, which no census may print.
7. **A calendar edge produced a description its own loader rejects.**
   The shared-clock conversion of `0001-01-01T01:00:00+14:00` falls
   outside the years the canonical form can spell, and the local text
   was left standing in its place.
8. **Generation falsely reported published offsets as withheld**, because
   the offsetless member was filtered out before the diversity was
   counted.
9. **An exactly conforming clock twin got a false percentile failure**,
   because the window omitted the all-different step and the report had
   no equality reading.
10. **The loader accepted impossible tail moments** and generation then
    raised `ValueError` or `OverflowError` out of the shape fitting.

Every table here is built at runtime from fixed values or a fixed seed
(plan D13); nothing is read from any real data.
"""

from __future__ import annotations

import collections
import copy
import datetime
import json
import pathlib

import fixtures
import kpi_shapes
import pytest
from synthtwin import (
    contract,
    generation,
    parsing,
    profile,
    reading,
    taxonomy,
    validation,
)

FLOOR = 11


# -- the shapes the review measured -----------------------------------


def _months(count: int = 100) -> "list[str]":
    """``count`` consecutive months from 2000-01, every one different."""
    made: "list[str]" = []
    year, month = 2000, 1
    for _each in range(count):
        made += [f"{year:04d}-{month:02d}"]
        month = month + 1
        if month == 13:
            month, year = 1, year + 1
    return made


def _quarters(count: int = 100) -> "list[str]":
    """``count`` consecutive quarters from 2000-Q1, every one different."""
    made: "list[str]" = []
    year, quarter = 2000, 1
    for _each in range(count):
        made += [f"{year:04d}-Q{quarter}"]
        quarter = quarter + 1
        if quarter == 5:
            quarter, year = 1, year + 1
    return made


def _minutes(count: int, start: str = "07:00", step: int = 2) -> "list[str]":
    """``count`` clock times ``step`` minutes apart, every one different."""
    first = 60 * int(start[0:2]) + int(start[3:5])
    return [
        f"{(first + step * place) // 60:02d}:{(first + step * place) % 60:02d}"
        for place in range(count)
    ]


def _every_minute_of_a_day() -> "list[str]":
    """All 1,440 minutes of a day, each once."""
    return [f"{hour:02d}:{minute:02d}" for hour in range(24) for minute in range(60)]


def _described(folder: pathlib.Path, name: str, cells: "list[str]"):
    """One column through the whole product path, at the review's floor."""
    text = "value\n" + "\n".join(cells) + "\n"
    return kpi_shapes.describe(folder / name, name, text, FLOOR)


def _missed(described, cells: "list[str]", name: str) -> "list[str]":
    """Every obligation a file of ``cells`` misses against ``described``."""
    return kpi_shapes.missed(
        kpi_shapes.measure(described, "value\n" + "\n".join(cells) + "\n", name)
    )


def _twin(described, seed: int) -> "list[str]":
    """The twin's own cells for one column, at one seed."""
    return [row[0] for row in generation.generate(described.loaded, seed).rows]


def _deviations(described, seed: int) -> "list[tuple[str, str, str]]":
    """Every deviation the twin's report names, as (fact, published, achieved)."""
    twin = generation.generate(described.loaded, seed)
    return [(note.fact, note.published, note.achieved) for note in twin.deviations]


# -- 4. the all-different obligation ----------------------------------


@pytest.mark.parametrize("seed", [0, 1, 4])
@pytest.mark.parametrize("kind", ["month", "quarter"])
def test_a_column_of_months_or_quarters_reaches_its_own_count(
    tmp_path: pathlib.Path, kind: str, seed: int
) -> None:
    """G7.3's count pass reaches a month and a quarter as it reaches a day.

    THE REVIEW'S OWN REPRODUCTION (item 4). A hundred unique months from
    `2000-01` at a floor of eleven came back holding 74 different values
    at seed 4, with no deviation reported and no obligation missed, and a
    hundred consecutive quarters did the same: the pass ran on `date` and
    `datetime` alone, and the envelope of G12.5 then admitted whatever
    the draw held.

    The number asserted is the DESCRIPTION's, not the twin's: the column
    publishes `n_distinct == n_present`, so G11 says every present value
    of the twin differs from every other.
    """
    cells = _months() if kind == "month" else _quarters()
    described = _described(tmp_path, kind, cells)
    block = described.block("value")
    assert block["n_distinct"] == block["n_present"] == len(cells)
    made = _twin(described, seed)
    assert len(set(made)) == block["n_distinct"]
    assert _deviations(described, seed) == []
    assert _missed(described, made, f"{kind}-twin.csv") == []


def test_the_count_pass_is_what_reaches_a_month(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MUTATION: withdraw the pass for months and quarters (item 4).

    `contract.datetime_counts_reachable` as it stood -- `date` and
    `datetime` only -- so the pass returns the ranks untouched and the
    twin holds fewer different months than the description publishes.
    """
    described = _described(tmp_path, "month", _months())
    real = contract.datetime_counts_reachable

    def only_days(column: "contract.ColumnBlock") -> bool:
        facts = column.facts
        if isinstance(facts, contract.DatetimeFacts):
            if facts.resolution not in ("date", "datetime"):
                return False
        return real(column)

    monkeypatch.setattr(contract, "datetime_counts_reachable", only_days)
    monkeypatch.setattr(generation.contract, "datetime_counts_reachable", only_days)
    made = _twin(described, 4)
    assert len(set(made)) < described.block("value")["n_distinct"]


def test_a_clock_column_of_all_different_times_owes_every_one_of_them(
    tmp_path: pathlib.Path,
) -> None:
    """G11 binds on a clock column, and an envelope stood in its place.

    THE REVIEW'S OWN REPRODUCTION (item 4): a column publishing 100
    different times was met by a file holding 99, with every obligation
    passing and nothing said. The construction is EXACT for this role
    (G7A.4), so the count is exact and a file one short misses it.
    """
    cells = _minutes(100)
    described = _described(tmp_path, "clock", cells)
    block = described.block("value")
    assert block["n_distinct"] == block["n_present"] == 100
    assert _missed(described, cells, "clock-real.csv") == []
    one_fewer = list(cells)
    one_fewer[5] = one_fewer[6]
    assert _missed(described, one_fewer, "clock-99.csv") == [
        "value:distinct.n_distinct",
        "value:distinct.n_distinct_folded",
    ]


def test_the_clock_count_is_exact_only_because_g11_binds(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MUTATION: withdraw G11's reading and the envelope passes 99 of 100."""
    described = _described(tmp_path, "clock", _minutes(100))
    monkeypatch.setattr(
        validation.contract,
        "all_different_binds",
        lambda column, published: False,
    )
    one_fewer = _minutes(100)
    one_fewer[5] = one_fewer[6]
    assert _missed(described, one_fewer, "clock-99-mutant.csv") == []


def test_a_published_offset_is_one_way_of_writing_an_instant(
    tmp_path: pathlib.Path,
) -> None:
    """A fully published offset does not lift the count (item 4).

    THE REVIEW'S OWN REPRODUCTION: 200 timestamps seven minutes apart,
    every one different, publishing `{"+02:00": 200}` in full, were met
    by a file holding 29 of those 200 values. One offset written after
    every moment leaves one spelling per instant, so the count pass
    reaches it and the count is exact.
    """
    base = datetime.datetime(2024, 1, 1, 0, 0)
    cells = [
        (base + datetime.timedelta(minutes=7 * place)).strftime(
            "%Y-%m-%dT%H:%M:%S+02:00"
        )
        for place in range(200)
    ]
    described = _described(tmp_path, "offsets", cells)
    block = described.block("value")
    assert block["utc_offsets"] == {"+02:00": 200}
    assert block["n_distinct"] == block["n_present"] == 200
    column = [
        each for each in described.loaded.columns if each.name == "value"
    ][0]
    assert contract.datetime_counts_reachable(column)
    thin = [cells[place % 29] for place in range(200)]
    missed = _missed(described, thin, "offsets-29.csv")
    assert "value:distinct.n_distinct" in missed
    assert "value:distinct.n_distinct_folded" in missed


# -- 5. a declared missing spelling a clock rank landed on -------------


def _declared_hole_column(
    folder: pathlib.Path,
) -> "tuple[contract.Profile, list[str]]":
    """The review's item-5 shape: 99 minutes, `08:00` declared missing.

    Ninety-nine clock times two minutes apart from `07:00` with the
    `08:00` cell taken out, and eleven cells holding `08:00`, which the
    run declares to mean "no value". The description records 99 present
    and 11 missing.
    """
    folder.mkdir(parents=True, exist_ok=True)
    cells = [cell for cell in _minutes(100) if cell != "08:00"] + ["08:00"] * 11
    table = fixtures.write(folder, "hole.csv", "value\n" + "\n".join(cells) + "\n")
    settings = taxonomy.Settings(
        small_cell_floor=FLOOR, declared_missing_values=("08:00",)
    )
    document = profile.build_document(
        reading.read_table(str(table), small_cell_floor=FLOOR), settings, [], [], []
    )
    written = fixtures.write_profile(folder, "hole-profile.json", document)
    return contract.load_profile(str(written)), cells


@pytest.mark.parametrize("seed", [0, 1, 3, 7])
def test_a_clock_twin_invents_no_declared_missing_cell(
    tmp_path: pathlib.Path, seed: int
) -> None:
    """The twin holds the published counts of present and absent cells.

    THE REVIEW'S OWN REPRODUCTION (item 5): seeds 0, 3 and 7 wrote TWELVE
    `08:00` cells, leaving 98 present against a published 99 and 12
    absent against 11, because the parsed clock values were never asked
    whether their spelling is one the table calls absent.
    """
    loaded, _cells = _declared_hole_column(tmp_path / "hole")
    block = [each for each in loaded.columns if each.name == "value"][0]
    assert (block.n_present, block.n_missing) == (99, 11)
    made = [row[0] for row in generation.generate(loaded, seed).rows]
    assert made.count("08:00") == block.n_missing
    assert len(made) - made.count("08:00") == block.n_present
    assert generation.generate(loaded, seed).deviations == ()


def test_the_hole_step_is_what_keeps_the_two_counts(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MUTATION: withdraw the step and seed 0 writes a twelfth `08:00`."""
    loaded, _cells = _declared_hole_column(tmp_path / "hole")
    monkeypatch.setattr(
        generation,
        "_clock_off_the_holes",
        lambda layout, ordinals, form, holes: ordinals,
    )
    made = [row[0] for row in generation.generate(loaded, 0).rows]
    assert made.count("08:00") > 11


# -- 6. a sparse mixed-date column's separator census ------------------


def _sparse_marks() -> "list[str]":
    """22 dates in 2,000 rows: a `T` separator and a bare date, alternating."""
    first = datetime.date(2024, 1, 1)
    made: "list[str]" = []
    for place in range(22):
        day = first + datetime.timedelta(days=place)
        made += [
            day.strftime("%Y-%m-%dT00:00:00")
            if place % 2 == 0
            else day.strftime("%Y-%m-%d")
        ]
    return made + [""] * 1978


@pytest.mark.parametrize("seed", [0, 4, 7])
def test_a_sparse_column_keeps_the_mark_census_it_publishes(
    tmp_path: pathlib.Path, seed: int
) -> None:
    """The spend never takes the named mark below the census line (item 6).

    THE REVIEW'S OWN REPRODUCTION: seed 4's distinctness repair turned
    one of the eleven `T` marks into a space, leaving ten and one; no
    count of that census reaches the floor, so describing the twin pools
    the whole census and `synthtwin validate` named `marks.upper_t` and
    `marks.unnamed` while generation reported nothing.
    """
    described = _described(tmp_path, "sparse", _sparse_marks())
    assert described.block("value")["datetime_separators"] == {"upper_t": 11}
    made = _twin(described, seed)
    marks = collections.Counter(
        cell[10] for cell in made if len(cell) > 10
    )
    assert marks == {"T": 11}
    assert _missed(described, made, f"sparse-{seed}.csv") == []


def test_the_census_floor_is_what_stops_the_spend(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MUTATION: let the spend run to its budget and the census is lost."""
    described = _described(tmp_path, "sparse", _sparse_marks())
    monkeypatch.setattr(
        generation, "_spend_leaves_a_name", lambda wearing, floor: True
    )
    made = _twin(described, 4)
    marks = collections.Counter(cell[10] for cell in made if len(cell) > 10)
    assert marks["T"] < 11


# -- 7. a calendar edge on the shared clock ----------------------------


def _calendar_edge() -> "list[str]":
    """The review's item-7 cells: a `+14:00` moment at the calendar's start."""
    return (
        ["0001-01-01T01:00:00+14:00"] * 12
        + ["0001-01-01T00:00:00Z"] * 20
        + ["0001-01-02T12:00:00Z"] * 68
    )


def test_a_calendar_edge_describes_itself_in_a_form_its_loader_accepts(
    tmp_path: pathlib.Path,
) -> None:
    """The producer writes no description its own loader refuses (item 7).

    THE REVIEW'S OWN REPRODUCTION: the shared-clock conversion of the
    twelve `+14:00` cells falls outside the years `0001` to `9999`, and
    the local text was left standing in the ordered sequence while the
    sort used the instant -- so the low tail published a mean distance
    of MINUS 3,600 and a listed value above its own boundary, and the
    strict loader refused the file under DT3 and told the person it had
    been changed since it was written.

    The clamp of `parsing.utc_moment` publishes the nearest instant the
    canonical form can spell, which is a non-decreasing function of the
    instant, so the sequence stays ordered by construction -- and the
    checker reads the same rule, so the real table meets its own
    description.
    """
    described = _described(tmp_path, "edge", _calendar_edge())
    block = described.block("value")
    assert block["datetimes_read_at"] == "utc"
    for side in ("low_tail", "high_tail"):
        tail = block[side]
        if tail is None:
            continue
        assert tail["mean_distance"] is None or tail["mean_distance"] >= 1
    assert _missed(described, _calendar_edge(), "edge-real.csv") == []


def test_the_clamp_is_what_keeps_the_description_loadable(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MUTATION: fall back to the local text and the loader refuses."""
    monkeypatch.setattr(
        taxonomy.parsing, "utc_moment", parsing.utc_canonical
    )
    with pytest.raises(Exception) as refusal:
        _described(tmp_path, "edge-mutant", _calendar_edge())
    assert "DT3" in str(refusal.value)


# -- 8. the offsets a twin's cells actually wear -----------------------


def _alternating_offsets() -> "list[str]":
    """100 noon timestamps, alternating no offset and `+01:00`."""
    base = datetime.datetime(2024, 1, 1, 12, 0)
    made: "list[str]" = []
    for place in range(100):
        moment = base + datetime.timedelta(days=place)
        made += [
            moment.strftime("%Y-%m-%dT%H:%M:%S")
            if place % 2 == 0
            else moment.strftime("%Y-%m-%dT%H:%M:%S+01:00")
        ]
    return made


@pytest.mark.parametrize("seed", [0, 4])
def test_a_published_offsetless_member_is_not_a_withheld_offset(
    tmp_path: pathlib.Path, seed: int
) -> None:
    """The twin wears two kinds of offset, so it reads back on the shared clock.

    THE REVIEW'S OWN REPRODUCTION (item 8): a column publishing
    `{"(none)": 50, "+01:00": 50}` -- a census that withholds nothing --
    was reported as a column whose every offset had been held back as
    too rare to publish, because the empty spelling was filtered out
    before the diversity was counted.
    """
    described = _described(tmp_path, "offsets", _alternating_offsets())
    block = described.block("value")
    assert block["datetimes_read_at"] == "utc"
    assert block["utc_offsets"] == {"(none)": 50, "+01:00": 50}
    facts = [
        fact for fact in _deviations(described, seed)
        if fact[0] == "datetimes_read_at"
    ]
    assert facts == []
    made = _twin(described, seed)
    wearing = collections.Counter(
        "+01:00" if cell.endswith("+01:00") else "(none)" for cell in made
    )
    assert wearing == {"(none)": 50, "+01:00": 50}


def test_a_column_whose_offsets_really_were_withheld_still_says_so(
    tmp_path: pathlib.Path,
) -> None:
    """The sentence the repair must not silence, measured on its own shape.

    Ten rare offsets over a hundred noon timestamps at a floor of eleven:
    every offset stands below the line, the census is one pool, and the
    twin writes one kind of offset and reads back on the local clock. The
    deviation is what tells the person so, and narrowing item 8's count
    must not take it away.
    """
    base = datetime.datetime(2024, 1, 1, 12, 0)
    cells: "list[str]" = []
    for place in range(100):
        moment = base + datetime.timedelta(days=place)
        hours = 1 + place % 10
        cells += [moment.strftime(f"%Y-%m-%dT%H:%M:%S+{hours:02d}:00")]
    described = _described(tmp_path, "pooled", cells)
    block = described.block("value")
    assert block["utc_offsets"] == {"(withheld)": 100}
    assert block["datetimes_read_at"] == "utc"
    facts = [
        fact for fact in _deviations(described, 0)
        if fact[0] == "datetimes_read_at"
    ]
    assert facts == [("datetimes_read_at", "utc", "local")]


# -- 9. an exactly conforming clock twin -------------------------------


@pytest.mark.parametrize("seed", [0, 1])
def test_a_twin_holding_the_whole_multiset_misses_nothing(
    tmp_path: pathlib.Path, seed: int
) -> None:
    """A rung the twin holds exactly is not a rung the twin missed (item 9).

    THE REVIEW'S OWN REPRODUCTION: every minute of a day once, 1,440
    rows. Seeds 0 and 1 reproduce the real column's whole multiset and
    validation reports no miss, yet the twin's report marked p99 as
    outside its window -- published `23:44`, achieved `23:44`, allowed
    `23:41` to `23:43`. Two things were wrong and both are repaired: the
    window omitted G7A.4's all-different step, and the report had no
    equality reading of its own.
    """
    cells = _every_minute_of_a_day()
    described = _described(tmp_path, "day", cells)
    twin = generation.generate(described.loaded, seed)
    made = [row[0] for row in twin.rows]
    assert collections.Counter(made) == collections.Counter(cells)
    assert twin.deviations == ()
    for found in twin.approximations:
        if found.achieved == found.published:
            assert found.inside, found
    assert _missed(described, made, f"day-{seed}.csv") == []


def test_the_window_carries_the_all_different_step(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MUTATION: the interpolation's window alone, and the equality reading
    withdrawn, and an exactly conforming twin is named for a rung it holds."""
    described = _described(tmp_path, "day", _every_minute_of_a_day())
    monkeypatch.setattr(generation, "_body_bounds", lambda layout: {})
    monkeypatch.setattr(generation, "_held_exactly", lambda measured: measured)
    twin = generation.generate(described.loaded, 0)
    named = [note.fact for note in twin.deviations]
    assert "clock_percentiles.p99" in named


# -- 10. tail moments a column could not hold --------------------------


def _hundred_dates() -> "list[str]":
    """A hundred dates whose tails publish both of their distances."""
    first = datetime.date(2020, 1, 1)
    spread = [0, 37, 71, 103, 149, 181, 223, 269, 307, 359]
    made: "list[str]" = []
    for step in range(10):
        for place in range(10):
            made += [
                (first + datetime.timedelta(days=spread[place] + 400 * step)).isoformat()
            ]
    return sorted(made)


def _with_distances(document: "dict", mean: float, root: float) -> "dict":
    """The same document with both tail distances written over."""
    changed = copy.deepcopy(document)
    for block in changed["columns"]:
        for side in ("low_tail", "high_tail"):
            tail = block.get(side)
            if tail:
                tail["mean_distance"] = mean
                tail["rms_distance"] = root
    return changed


@pytest.mark.parametrize(
    "mean,root",
    [(1e308, 1e308), (1.0, 1e308), (1e10, 1e10)],
)
def test_a_tail_moment_no_tail_could_hold_is_refused(
    tmp_path: pathlib.Path, mean: float, root: float
) -> None:
    """DT3's feasible bounds, on the review's own numbers (item 10).

    THE REVIEW'S OWN REPRODUCTION: setting a valid 100-date profile's
    tail distances to `1e308` loaded, and generation then raised
    `ValueError: cannot convert float NaN to integer`; a mean of `1`
    beside that root raised `OverflowError`. A description the loader
    accepts is one the generator builds from, so both are refused here.
    `1e10` days is the same rule at a scale a reader can check: the
    supported calendar holds about 3.65 million of them.
    """
    described = _described(tmp_path, "dates", _hundred_dates())
    assert described.block("value")["low_tail"]["mean_distance"] is not None
    broken = _with_distances(described.document, mean, root)
    written = fixtures.write_profile(tmp_path, "broken.json", broken)
    with pytest.raises(Exception) as refusal:
        contract.load_profile(str(written))
    assert "DT3" in str(refusal.value)


def test_the_bounds_refuse_nothing_a_real_description_publishes(
    tmp_path: pathlib.Path,
) -> None:
    """The same hundred dates load and generate as they always did.

    The bound of DT3 is the WIDEST space any column can be written in,
    so nothing a narrower member would allow is refused. This is the
    other half of the guard above: a rule that refused a description the
    producer writes would be worse than the crash it prevents.
    """
    described = _described(tmp_path, "dates", _hundred_dates())
    assert json.loads(
        json.dumps(described.block("value")["low_tail"])
    )["rows"] >= 1
    made = _twin(described, 0)
    assert len(made) == 100
    assert _missed(described, _hundred_dates(), "dates-real.csv") == []
