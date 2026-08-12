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
    canonical,
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
SHAPES = {
    "quarter": ["2024-Q1", "2024-Q2", "2024-Q3", "2024-Q4"],
    "date": ["2024-01-05", "2024-02-19", "2024-07-30", "2024-11-02"],
    "minute": [
        "2024-01-05 09:15",
        "2024-02-19 13:40",
        "2024-07-30 21:05",
        "2024-11-02 04:55",
    ],
    "second": [
        "2024-01-05 09:15:07",
        "2024-02-19 13:40:44",
        "2024-07-30 21:05:19",
        "2024-11-02 04:55:02",
    ],
    "subsecond": [
        "2024-01-05 09:15:07.250",
        "2024-02-19 13:40:44.100",
        "2024-07-30 21:05:19.900",
        "2024-11-02 04:55:02.025",
    ],
    "offsets": [
        "2024-01-05 09:15:07+02:00",
        "2024-02-19 13:40:44+02:00",
        "2024-07-30 21:05:19-05:00",
        "2024-11-02 04:55:02-05:00",
    ],
}

# The fields a person can recount on the twin. `format` is REPORT-ONLY
# and deliberately absent: the twin is written in ISO syntax at the
# recorded detail, not in the source's lexical family (residual R-P2-7).
CARRIED = (
    "resolution",
    "time_precision",
    "subsecond_digits",
    "datetimes_read_at",
    "utc_offsets",
    "earliest_utc_offset",
    "latest_utc_offset",
    "earliest",
    "latest",
)


def _rows(values: "list[str]", copies: int) -> "list[str]":
    """Enough rows of a small set of values to clear the smallest group."""
    return [values[index % len(values)] for index in range(copies)]


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
    target = folder / name
    target.write_text(
        canonical.serialize(document), encoding="utf-8", newline="\n"
    )
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
    document = _document(folder, _rows(SHAPES[shape], 40))
    block = document["columns"][0]
    assert block["role"] == "datetime", block["role"]
    described = _loaded(folder, document)
    built = generation.generate(described, 3)
    again = _redescribed(folder, built)["columns"][0]
    for key in CARRIED:
        assert again[key] == block[key], f"{shape}: {key}"
    named = [
        deviation.fact
        for deviation in built.deviations
        if deviation.column == "when"
    ]
    assert "earliest" not in named
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
    document = _document(folder, _rows(SHAPES["second"], 40))
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
    document = _document(folder, _rows(SHAPES["second"], 40))
    edited = copy.deepcopy(document)
    edited["columns"][0]["earliest"] = spelling
    with pytest.raises(errors.ProfileError) as raised:
        _loaded(folder, edited, "edited.json")
    assert "earliest" in f"{raised.value}"


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
    document = _document(folder, _rows(SHAPES["second"], 40))
    assert document["columns"][0]["latest"] == "2024-11-02 04:55:02"
    assert document["columns"][0]["datetimes_read_at"] == "local"
    document["columns"][0]["latest"] = "2024-11-02 04:55:60"
    document["columns"][0]["date_percentiles"]["max"] = "2024-11-02 04:55:60"
    described = _loaded(folder, document, "leap.json")
    built = generation.generate(described, 3)

    named = [
        deviation.fact
        for deviation in built.deviations
        if deviation.column == "when"
    ]
    assert "latest" not in named
    assert "date_percentiles.max" not in named

    present = [cell for cell in built.columns[0] if cell != ""]
    assert "2024-11-02T04:55:60" in present
    again = _redescribed(folder, built)["columns"][0]
    assert again["latest"] == "2024-11-02 04:55:60"
    assert again["date_percentiles"]["max"] == "2024-11-02 04:55:60"


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
    document = _document(folder, _rows(SHAPES["offsets"], 40))
    assert document["columns"][0]["datetimes_read_at"] == "utc"
    shared = copy.deepcopy(document)
    end = shared["columns"][0]["latest"]
    moved = f"{end[0:17]}60"
    shared["columns"][0]["latest"] = moved
    shared["columns"][0]["date_percentiles"]["max"] = moved
    with pytest.raises(errors.ProfileError) as raised:
        _loaded(folder, shared, "shared.json")
    message = f"{raised.value}"
    assert "D10" in message
    assert "when" in message
    assert moved in message

    minutes = _document(folder, _rows(SHAPES["minute"], 40))
    assert minutes["columns"][0]["time_precision"] == "minute"
    finish = minutes["columns"][0]["latest"]
    seconds = f"{finish[0:17]}07"
    minutes["columns"][0]["latest"] = seconds
    minutes["columns"][0]["date_percentiles"]["max"] = seconds
    with pytest.raises(errors.ProfileError) as second:
        _loaded(folder, minutes, "minutes.json")
    assert "D10" in f"{second.value}"
    assert seconds in f"{second.value}"


def test_a_ladder_end_that_is_not_the_column_s_own_end_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    """The two ends of the ladder ARE the first and last values (D11).

    Nothing tied them, and the pair being untied cost an exact fact
    silently: the generator pins its first cell to `earliest` and
    interpolates the rest inside the ladder, so a ladder beginning
    before `earliest` gave a twin holding instants EARLIER than the end
    it published, and describing that twin again found a different
    `earliest` with no deviation named for it anywhere (review item
    P2-C3-F2, found beside it).
    """
    folder = tmp_path / "ladder"
    folder.mkdir(parents=True, exist_ok=True)
    document = _document(folder, _rows(SHAPES["second"], 40))
    block = document["columns"][0]
    assert block["date_percentiles"]["min"] == block["earliest"]
    assert block["date_percentiles"]["max"] == block["latest"]

    early = copy.deepcopy(document)
    early["columns"][0]["date_percentiles"]["min"] = "2020-01-01 00:00:00"
    early["columns"][0]["date_percentiles"]["p01"] = "2020-01-01 00:00:00"
    with pytest.raises(errors.ProfileError) as raised:
        _loaded(folder, early, "early.json")
    assert "D11" in f"{raised.value}"

    late = copy.deepcopy(document)
    late["columns"][0]["date_percentiles"]["max"] = "2030-01-01 00:00:00"
    with pytest.raises(errors.ProfileError) as second:
        _loaded(folder, late, "late.json")
    assert "D11" in f"{second.value}"


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
    document = _document(folder, _rows(SHAPES["offsets"], 40))
    edited = copy.deepcopy(document)
    edited["columns"][0]["utc_offsets"] = {spelling: 40}
    edited["columns"][0]["earliest_utc_offset"] = spelling
    edited["columns"][0]["latest_utc_offset"] = spelling
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
    document = _document(folder, _rows(SHAPES["offsets"], 40))
    edited = copy.deepcopy(document)
    edited["columns"][0]["utc_offsets"] = {spelling: 40}
    edited["columns"][0]["earliest_utc_offset"] = spelling
    edited["columns"][0]["latest_utc_offset"] = spelling
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
    document = _document(folder, _rows(SHAPES["date"], 40))
    assert document["columns"][0]["resolution"] == "date"
    document["columns"][0]["utc_offsets"] = {"+02:00": 40}
    document["columns"][0]["earliest_utc_offset"] = "+02:00"
    document["columns"][0]["latest_utc_offset"] = "+02:00"
    with pytest.raises(errors.ProfileError) as raised:
        _loaded(folder, document, "edited.json")
    assert "D9" in f"{raised.value}"
