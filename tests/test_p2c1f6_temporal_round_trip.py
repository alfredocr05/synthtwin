"""Every temporal fact a description carries survives the twin.

Review item P2-C1-F6. Three separate ways a fact the loader accepted was
changed on the way out:

* the contract permitted a column whose values are dates AND times while
  the finest detail it writes is a whole date. No cell can hold both:
  written as a whole date the column reads back as a column of dates, so
  the published form is lost, and written with seconds it reads back at
  the second, so the published detail is lost. The producer cannot make
  such a column -- a value with no time of day does not read as a date
  and time at all -- so the pair is refused where it is decided, in the
  contract and its loader, and the rendering grammar covers every pair
  that remains;
* the loader read a published instant as a SHAPE, so `2024-99-99` was
  accepted and the generator then did calendar arithmetic on it and
  wrote a real date somewhere else entirely. The same held for an offset
  of `+99:99`. Both are now ranges the contract states and the loader
  enforces;
* the ends were read back from the written cell instead of being assumed
  from the writing rule, which is right, but the first repair then wrote
  the following minute for an end carrying the last second of a leap
  minute and called the loss permitted. Both ends are exact facts and no
  owner decision took that back, so an end is now written from the
  published instant's own fields and survives (review item P2-C2-F5).
  The read-back check stays. The two descriptions it used to name --
  whole minutes with an end carrying seconds, and a sixtieth second on
  the shared clock -- are refused by D10 rather than accepted and
  reported, and D11 ties the ladder's ends to the column's own two ends
  (review item P2-C3-F2).

The round trip is the test that matters: describe a table, build a twin,
describe the TWIN, and require the same temporal facts back.
"""

import copy
import json
import pathlib
import typing

import pytest

import fixtures
from synthtwin import (
    contract,
    errors,
    generation,
    profile,
    reading,
    taxonomy,
)

Document = dict[str, typing.Any]

# One table for every resolution and precision pair the contract permits,
# so the rendering grammar is exercised at each of them rather than at
# the two a fixture happens to reach.
#
# EACH SHAPE IS WRITTEN AS A SPREAD OF DIFFERENT VALUES since stage 3
# (plan P4-D328). The four repeated values these shapes held publish no
# tail at all at a floor of eleven -- ten cells on each of four values
# leave no value between the two boundaries (contract TL2) -- so the
# round trip they exist to measure would have nothing to carry. The
# spread keeps each shape's own resolution, precision and clock and
# gives the column forty different values, which is what a tail needs.
def _spread(pattern: str, copies: int) -> "list[str]":
    """`copies` different values of one shape, a day apart inside a year."""
    made: "list[str]" = []
    for index in range(copies):
        month = 1 + index // 28
        day = 1 + index % 28
        made += [pattern.format(month=month, day=day)]
    return made


SHAPES = {
    "quarter": "{month:04d}-Q1",
    "date": "2024-{month:02d}-{day:02d}",
    "minute": "2024-{month:02d}-{day:02d} 09:15",
    "second": "2024-{month:02d}-{day:02d} 09:15:07",
    "subsecond": "2024-{month:02d}-{day:02d} 09:15:07.250",
    "offsets": "2024-{month:02d}-{day:02d} 09:15:07+02:00",
}

# The quarter shape needs a year of its own per value, and the offset
# shape needs a second offset for the shared clock to be published.
def _values(shape: str, copies: int) -> "list[str]":
    """The `copies` different values of one shape."""
    if shape == "quarter":
        return [f"{1990 + index // 4:04d}-Q{1 + index % 4}" for index in range(copies)]
    made = _spread(SHAPES[shape], copies)
    if shape == "offsets":
        made = [
            value if index % 2 == 0 else f"{value[0:19]}-05:00"
            for index, value in enumerate(made)
        ]
    return made


# The fields a person can recount on the twin. `format` is REPORT-ONLY
# and deliberately absent: the twin is written in ISO syntax at the
# recorded detail, not in the source's lexical family (residual R-P2-7).
# STAGE 3: the two ends and their offsets are no longer published, so
# what a twin carries back of the two TAILS is each boundary, the count
# of cells beyond it and -- where the tail publishes them -- the values
# it holds, all three EXACT-OBSERVABLE, beside the unit the distances
# are counted in. The two DISTANCES are APPROXIMATED inside the window
# of G12.14 and are not compared here; `synthtwin validate` is where
# they are measured, and `tests/test_p3v4f4_datetime_windows.py` holds
# the two writings of that window to agreeing.
CARRIED = (
    "resolution",
    "time_precision",
    "subsecond_digits",
    "datetimes_read_at",
    "utc_offsets",
    "tail_unit",
)
# WHETHER A TAIL PUBLISHES ITS VALUES IS NOT A FACT THE TWIN OWES. It is
# a decision about the whole column: a tail whose published numbers would
# settle a count below the floor publishes its values instead (plan
# P4-D329), and that question is asked with the column's own distinctness
# beside it. The twin of an all-different column repeats values in its
# body, so its own tail is not pinned where the source's was, and it
# publishes the two distances where the source published its values --
# while holding exactly the same outer values, which is what
# `synthtwin validate` measures.
EXACT_IN_A_TAIL = ("boundary", "rows")


def _rows(shape: str, copies: int) -> "list[str]":
    """Enough different values of one shape for both tails to exist."""
    return _values(shape, copies)


def _document(folder: pathlib.Path, values: "list[str]") -> Document:
    """The producer's own description of a one-column table of dates."""
    path = fixtures.write(
        folder, "table.csv", fixtures.single_column_table("when", values)
    )
    table = reading.read_table(str(path))
    built = profile.build_document(table, taxonomy.Settings(), [])
    return typing.cast(Document, json.loads(json.dumps(built)))


def _loaded(
    folder: pathlib.Path, document: Document, name: str = "profile.json"
) -> contract.Profile:
    """Load a description from a file of its own canonical bytes."""
    target = fixtures.write_profile(folder, name, document)
    return contract.load_profile(str(target))


def _redescribed(
    folder: pathlib.Path, built: generation.Twin
) -> Document:
    """Write the twin as a table, read it back, and describe THAT."""
    lines = [",".join(built.names)]
    for row in built.rows:
        lines = lines + [",".join(row)]
    path = fixtures.write(folder, "twin.csv", "\n".join(lines) + "\n")
    table = reading.read_table(str(path))
    again = profile.build_document(table, taxonomy.Settings(), [])
    return typing.cast(Document, json.loads(json.dumps(again)))


@pytest.mark.parametrize("shape", sorted(SHAPES))
def test_a_temporal_column_reprofiles_to_the_facts_it_published(
    tmp_path: pathlib.Path, shape: str
) -> None:
    """Description in, twin out, description again: the same facts.

    Every field checked here is EXACT-OBSERVABLE, which is a promise
    that a person can read the twin and find the published answer. The
    check is made by describing the twin with the shipped producer, so
    it is the same measurement a person would make.
    """
    folder = tmp_path / shape
    folder.mkdir(parents=True, exist_ok=True)
    document = _document(folder, _rows(shape, 40))
    block = document["columns"][0]
    assert block["role"] == "datetime", block["role"]
    described = _loaded(folder, document)
    built = generation.generate(described, 3)
    again = _redescribed(folder, built)["columns"][0]
    for key in CARRIED:
        assert again[key] == block[key], f"{shape}: {key}"
    for side in ("low_tail", "high_tail"):
        published = block[side]
        recounted = again[side]
        assert (published is None) == (recounted is None), f"{shape}: {side}"
        if published is None:
            continue
        for key in EXACT_IN_A_TAIL:
            assert recounted[key] == published[key], f"{shape}: {side}.{key}"
    named = [
        deviation.fact
        for deviation in built.deviations
        if deviation.column == "when"
    ]
    assert "low_tail.rows" not in named
    assert "high_tail.rows" not in named
    assert "latest" not in named


def test_the_pair_no_cell_can_hold_is_refused_by_the_loader(
    tmp_path: pathlib.Path,
) -> None:
    """Dates AND times, whose finest detail is a whole date, is refused.

    The producer cannot make this pair and no cell can hold it, so it is
    settled where it is decided. Before the repair the loader accepted
    it and the twin wrote seconds, reprofiling at the second while
    recording no deviation at all.
    """
    folder = tmp_path / "pair"
    folder.mkdir(parents=True, exist_ok=True)
    document = _document(folder, _rows("second", 40))
    assert document["columns"][0]["resolution"] == "datetime"
    document["columns"][0]["time_precision"] = "date"
    with pytest.raises(errors.ProfileError) as raised:
        _loaded(folder, document, "edited.json")
    message = f"{raised.value}"
    assert "D6" in message
    assert "when" in message


@pytest.mark.parametrize(
    "spelling",
    ["2024-99-99 00:00:00", "2024-02-30 00:00:00", "2024-01-05 24:00:00",
     "2024-01-05 09:60:07"],
)
def test_an_instant_the_calendar_or_the_clock_has_not_is_refused(
    tmp_path: pathlib.Path, spelling: str
) -> None:
    """The published instants carry ranges, not only a shape.

    Each of these has the right characters in the right places and names
    no instant at all. Accepting one let the generator do day and second
    arithmetic on it and write a plausible date somewhere else in the
    calendar, so the exact endpoint text was not preserved and nothing
    said so.
    """
    folder = tmp_path / "calendar"
    folder.mkdir(parents=True, exist_ok=True)
    document = _document(folder, _rows("second", 40))
    edited = copy.deepcopy(document)
    edited["columns"][0]["low_tail"]["boundary"] = spelling
    with pytest.raises(errors.ProfileError) as raised:
        _loaded(folder, edited, "edited.json")
    assert "low_tail" in f"{raised.value}"


def test_the_last_second_of_a_leap_minute_is_written_back_exactly(
    tmp_path: pathlib.Path,
) -> None:
    """A leap second is a real reading, and the twin gives it back.

    The shipped date reader accepts a sixtieth second and a real table
    can hold one, so refusing it in the loader would make a description
    the producer wrote unloadable. Accepting it and then writing the
    following minute is the other half of the same mistake: the plan
    makes both ends exact and no owner decision took that back.

    This is the scenario review item P2-C2-F5 states. The end is written
    from its own published fields rather than through the whole-second
    space the ranks between the ends travel in, so it survives, and a
    boundary filter written against the twin selects the same rows the
    real table's own end would select.
    """
    folder = tmp_path / "leap"
    folder.mkdir(parents=True, exist_ok=True)
    document = _document(folder, _rows("second", 40))
    assert document["columns"][0]["datetimes_read_at"] == "local"
    # STAGE 3: what a leap second can stand on is a published value, and
    # the published values of this role are the two tail boundaries and
    # the rungs between them. The high boundary carries it here.
    boundary = document["columns"][0]["high_tail"]["boundary"]
    leap = f"{boundary[0:17]}60"
    document["columns"][0]["high_tail"]["boundary"] = leap
    for name in ("p50", "p75", "p90", "p95"):
        rung = document["columns"][0]["date_percentiles"][name]
        if rung == boundary:
            document["columns"][0]["date_percentiles"][name] = leap
    described = _loaded(folder, document, "leap.json")
    built = generation.generate(described, 3)

    named = [
        deviation.fact
        for deviation in built.deviations
        if deviation.column == "when"
    ]
    assert "high_tail.rows" not in named
    assert "date_percentiles.p95" not in named

    present = [cell for cell in built.columns[0] if cell != ""]
    # Written with the source's own space since plan P4-D39, and from
    # the boundary's own fields where its seconds field is 60 (G7.5).
    assert leap in present
    again = _redescribed(folder, built)["columns"][0]
    assert again["high_tail"]["boundary"] == leap


def test_an_end_no_cell_of_this_shape_can_show_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    """The two descriptions whose own facts cannot all hold are refused.

    A sixtieth second published while the description says its instants
    are written on the shared clock reads back as the following minute
    whatever cell carries it, and a column recording whole minutes has
    no seconds field for an end that carries seconds. The producer
    writes neither pair, and both ends are exact facts with no corner
    and no exception, so each pair is settled where the whole-date-
    beside-date-and-time pair above is settled: in the description, by
    D10, and not in the twin.

    An earlier repair accepted both and named the changed end in the
    report instead. That is an exception beside a sentence that says
    there is none, and this test used to require it (review item
    P2-C3-F2).
    """
    folder = tmp_path / "cannot"
    folder.mkdir(parents=True, exist_ok=True)
    document = _document(folder, _rows("offsets", 40))
    assert document["columns"][0]["datetimes_read_at"] == "utc"
    shared = copy.deepcopy(document)
    end = shared["columns"][0]["high_tail"]["boundary"]
    moved = f"{end[0:17]}60"
    shared["columns"][0]["high_tail"]["boundary"] = moved
    with pytest.raises(errors.ProfileError) as raised:
        _loaded(folder, shared, "shared.json")
    message = f"{raised.value}"
    assert "D10" in message
    assert "when" in message
    assert moved in message

    minutes = _document(folder, _rows("minute", 40))
    assert minutes["columns"][0]["time_precision"] == "minute"
    finish = minutes["columns"][0]["low_tail"]["boundary"]
    seconds = f"{finish[0:17]}07"
    minutes["columns"][0]["low_tail"]["boundary"] = seconds
    with pytest.raises(errors.ProfileError) as second:
        _loaded(folder, minutes, "minutes.json")
    assert "D10" in f"{second.value}"
    assert seconds in f"{second.value}"


def test_a_ladder_rung_outside_the_tail_rule_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    """The ladder is published between the two boundaries (D11).

    Stage 3 replaces the tie between the ladder's ends and the column's
    two endpoints, which are no longer published: what D11 says now is
    that both ends of the ladder are empty, that a rung inside a tail is
    empty, that a rung read off a boundary's own rank IS that boundary,
    and that every published rung lies between the two. Each clause is
    broken here in turn, and the loader refuses each -- untied, a
    hand-made document could publish a rung at a rank the construction
    pins elsewhere, and the twin would hold a value its own description
    contradicts.
    """
    folder = tmp_path / "ladder"
    folder.mkdir(parents=True, exist_ok=True)
    document = _document(folder, _rows("second", 40))
    block = document["columns"][0]
    assert block["date_percentiles"]["min"] is None
    assert block["date_percentiles"]["max"] is None
    low = block["low_tail"]["boundary"]
    assert isinstance(low, str)

    filled = copy.deepcopy(document)
    filled["columns"][0]["date_percentiles"]["min"] = low
    with pytest.raises(errors.ProfileError) as raised:
        _loaded(folder, filled, "filled.json")
    assert "D11" in f"{raised.value}"

    emptied = copy.deepcopy(document)
    emptied["columns"][0]["date_percentiles"]["p50"] = None
    with pytest.raises(errors.ProfileError) as second:
        _loaded(folder, emptied, "emptied.json")
    assert "D11" in f"{second.value}"

    outside = copy.deepcopy(document)
    outside["columns"][0]["high_tail"]["boundary"] = low
    with pytest.raises(errors.ProfileError) as third:
        _loaded(folder, outside, "outside.json")
    assert "D11" in f"{third.value}" or "TL2" in f"{third.value}"


@pytest.mark.parametrize("spelling", ["+99:99", "+15:00", "-14:30", "+02:60"])
def test_an_offset_no_zone_uses_is_refused(
    tmp_path: pathlib.Path, spelling: str
) -> None:
    """The offset range is checked, not only the offset's shape.

    No zone stands further than fourteen hours from the shared clock and
    no zone's minute field reaches sixty. The generator does whole-second
    arithmetic with both fields, so an accepted `+99:99` moved a written
    cell to an instant no offset could produce.
    """
    folder = tmp_path / "offsets"
    folder.mkdir(parents=True, exist_ok=True)
    document = _document(folder, _rows("offsets", 40))
    edited = copy.deepcopy(document)
    edited["columns"][0]["utc_offsets"] = {spelling: 40}
    with pytest.raises(errors.ProfileError) as raised:
        _loaded(folder, edited, "edited.json")
    assert "utc_offsets" in f"{raised.value}"


@pytest.mark.parametrize("spelling", ["+14:00", "-13:59", "Z"])
def test_an_offset_at_the_edge_of_the_range_is_accepted(
    tmp_path: pathlib.Path, spelling: str
) -> None:
    """The boundary is stated in both directions, so the range is a fact."""
    folder = tmp_path / "edge"
    folder.mkdir(parents=True, exist_ok=True)
    document = _document(folder, _rows("offsets", 40))
    edited = copy.deepcopy(document)
    edited["columns"][0]["utc_offsets"] = {spelling: 40}
    edited["columns"][0]["datetimes_read_at"] = "local"
    described = _loaded(folder, edited, f"edge-{len(spelling)}.json")
    built = generation.generate(described, 3)
    present = [cell for cell in built.columns[0] if cell != ""]
    assert present
    for cell in present:
        assert cell.endswith(spelling), cell


def test_an_offset_on_a_column_with_no_time_of_day_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    """A whole date has no clock for an offset to move (invariant D9).

    A cell written `2024-03-15+02:00` reads back as no date at all, so
    the offset would be a published fact the twin could not carry.
    """
    folder = tmp_path / "dated"
    folder.mkdir(parents=True, exist_ok=True)
    document = _document(folder, _rows("date", 40))
    assert document["columns"][0]["resolution"] == "date"
    document["columns"][0]["utc_offsets"] = {"+02:00": 40}
    with pytest.raises(errors.ProfileError) as raised:
        _loaded(folder, document, "edited.json")
    assert "D9" in f"{raised.value}"
