"""Gate file of the 4w integration: `validate` of a twin drawn from the inside record is not a rubber stamp.

A column drawn from the inside record is written with the description's twin's own cells (lane IN-2b), so no
obligation of a number or a label is excused; `synthtwin validate` excuses only the calendar counts of a made-up date
column that moves as a whole, a person's timeline or a chained date (`cli._INSIDE_EXCUSED_DATE_FACTS`), and nothing
else.

WHAT IT HOLDS (each clause red on its mutant):

* The faithful drawn twin validates with exit 0 and no MISSED (mutant: nothing is excused, so exit 3).
* A damaged drawn twin (the age column blanked on every third row, which the presence obligations of a drawn column
  never excuse) still exits 3 (mutant: every MISSED check of a drawn column is relabelled, so exit 0).
"""

from __future__ import annotations

import contextlib
import dataclasses
import io
import pathlib
import typing

import pytest

import reliability_battery as B
import reliability_tables as T
from synthtwin import cli, inside, installation


@pytest.fixture(scope="module", autouse=True)
def _inside_record_switched_on() -> "typing.Iterator[None]":
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr("synthtwin.cli._INSIDE_RECORD_SHIPPED", True)
        yield


def _places(folder: pathlib.Path) -> inside.Places:
    return inside.Places(pathlib.Path(folder, "installation", "synthtwin", "inside"), (), (),
                         installation.system_name(), ())


@pytest.fixture(scope="module")
def made(tmp_path_factory: pytest.TempPathFactory) -> "tuple[pathlib.Path, pathlib.Path, pathlib.Path]":
    folder = tmp_path_factory.mktemp("inside-validate") / "product"
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr("synthtwin.cli._INSIDE_RECORD_SHIPPED", True)
        patch.setattr(inside, "default_places", lambda: _places(folder))
        B.make_twins(folder, "T2", T.text("T2", 20000, 1), (0,), False)
    return folder, folder / "out" / "visits-profile.json", folder / "out" / "visits-twin.csv"


def _validate(folder: pathlib.Path, description: pathlib.Path) -> int:
    places = _places(folder)
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr("synthtwin.cli._INSIDE_RECORD_SHIPPED", True)
        patch.setattr(inside, "default_places", lambda: places)
        with B.installed(folder), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return int(cli.main(["validate", f"{description}", "--replace"], small_tables_refused=False))


def test_the_faithful_drawn_twin_validates(made) -> None:  # type: ignore[no-untyped-def]
    folder, description, _twin = made
    assert _validate(folder, description) == 0


def test_a_damaged_drawn_twin_still_exits_three(made) -> None:  # type: ignore[no-untyped-def]
    folder, description, twin = made
    kept = twin.read_bytes()
    lines = kept.decode("utf-8").split("\n")
    header = lines[0].split(",")
    at = header.index("age")
    damaged = [lines[0]]
    for number, line in enumerate(lines[1:]):
        cells = line.split(",")
        if len(cells) == len(header) and number % 3 == 0:
            cells[at] = ""
        damaged.append(",".join(cells))
    try:
        twin.write_bytes("\n".join(damaged).encode("utf-8"))
        assert _validate(folder, description) == 3
    finally:
        twin.write_bytes(kept)


# -- the owner's ruling of 2026-11-22 (batch 4z's fix round): excuse only what the made-up day moves ---------------


def _relabelled(folder: pathlib.Path, description: pathlib.Path, facts: "tuple[str, ...]") -> "dict[str, str]":
    """validate run as shipped, with one MISSED check of each of ``facts`` added on the made-up visit dates before the
    excusal reads the outcome: what the excusal made of each (its verdict after)."""
    from synthtwin import validation

    places = _places(folder)
    after: "dict[str, str]" = {}
    original = cli._outcome_of_a_drawn_twin

    def fabricated(described: str, measured: str, outcome: "typing.Any") -> "typing.Any":
        model = next(check for check in outcome.checks if check.column == "visit_date")
        added = tuple(dataclasses.replace(model, fact=fact, subcheck=f"{fact}.added", verdict=validation.MISSED,
                                          citation="") for fact in facts)
        relabelled = original(described, measured, dataclasses.replace(outcome, checks=outcome.checks + added))
        for check in relabelled.checks:
            if check.column == "visit_date" and check.subcheck.endswith(".added"):
                after[check.fact] = check.verdict
        return relabelled

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr("synthtwin.cli._INSIDE_RECORD_SHIPPED", True)
        patch.setattr(inside, "default_places", lambda: places)
        patch.setattr(cli, "_outcome_of_a_drawn_twin", fabricated)
        with B.installed(folder), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            code = int(cli.main(["validate", f"{description}", "--replace"], small_tables_refused=False))
    assert code in (0, 3), code
    return after


def test_only_what_the_made_up_day_moves_is_excused(made) -> None:  # type: ignore[no-untyped-def]
    """The day-of-month counts, the heavy days, the distinct days and the day-level ladder: excused; the weekday counts
    and the clock's hour, minute and second counts: still MISSED (red where the weekday or the clock is excused)."""
    from synthtwin import validation

    folder, description, _twin = made
    excused = ("datetime.day_of_month_census", "datetime.heavy_dates", "datetime.n_distinct",
               "datetime.date_percentiles", "datetime.high_tail.boundary")
    kept = ("datetime.weekday_census", "datetime.hour_census", "datetime.minute_census", "datetime.n_at_midnight",
            "datetime.second_census")
    after = _relabelled(folder, description, excused + kept)
    assert after, "premise: the visit dates are made up by the record's dates zone and named in the twin's report"
    for fact in excused:
        assert after[fact] == validation.AUTHORIZED_DEVIATION, fact
    for fact in kept:
        assert after[fact] == validation.MISSED, fact


def test_a_ladder_or_tail_is_excused_only_inside_the_real_months(made) -> None:  # type: ignore[no-untyped-def]
    """One twin visit date moved five years past the real last month: its ladder and tail misses stay MISSED, while its
    day-of-month miss is still excused (red where the range is not read)."""
    from synthtwin import validation

    folder, description, twin = made
    kept = twin.read_bytes()
    lines = kept.decode("utf-8").split("\n")
    at = lines[0].split(",").index("visit_date")
    for number in range(1, len(lines)):
        cells = lines[number].split(",")
        if len(cells) > at and cells[at][:4].isdigit():
            cells[at] = f"{int(cells[at][:4]) + 5}{cells[at][4:]}"
            lines[number] = ",".join(cells)
            break
    try:
        twin.write_bytes("\n".join(lines).encode("utf-8"))
        after = _relabelled(folder, description, ("datetime.date_percentiles", "datetime.low_tail.rows",
                                                  "datetime.day_of_month_census"))
    finally:
        twin.write_bytes(kept)
    assert after["datetime.date_percentiles"] == validation.MISSED
    assert after["datetime.low_tail.rows"] == validation.MISSED
    assert after["datetime.day_of_month_census"] == validation.AUTHORIZED_DEVIATION


def test_the_real_months_are_read_off_the_record_calendar() -> None:
    """`inside_dates.outside_the_real_months`: a date in a month the real column holds none of is counted; blanks, other
    words and the month's other days are not; a column the zone does not hold reads None."""
    import datetime

    from synthtwin import inside_dates

    real = [f"{datetime.date(2021, 3, 1) + datetime.timedelta(days=day % 400):%Y-%m-%d}" for day in range(2000)]
    zone = inside_dates.build_zone({"seen_on": real})
    assert inside_dates.outside_the_real_months(zone, "seen_on", real) == 0
    inside_cells = ["2021-03-31", "2022-04-30", "", "pending", "2021-03-01"]
    assert inside_dates.outside_the_real_months(zone, "seen_on", inside_cells) == 0
    assert inside_dates.outside_the_real_months(zone, "seen_on", inside_cells + ["2021-02-28", "2022-05-01"]) == 2
    assert inside_dates.outside_the_real_months(zone, "other", inside_cells) is None


def test_a_weekday_or_clock_census_is_judged_at_the_draws_precision() -> None:
    """Each group within three standard deviations of a draw at its published share, plus one: no loss (excused); one
    group further off, a group short or named otherwise: MISSED (red where every census is excused, or none)."""
    published = "Monday 3169, Tuesday 4107, Wednesday 4779, Thursday 3038, Friday 4344, Saturday 300, Sunday 263"
    drawn = "Monday 3173, Tuesday 4061, Wednesday 4771, Thursday 3031, Friday 4394, Saturday 301, Sunday 269"
    assert cli._within_its_sampling_window(published, drawn)
    assert cli._within_its_sampling_window(published, published)
    shifted = "Monday 3169, Tuesday 3807, Wednesday 5079, Thursday 3038, Friday 4344, Saturday 300, Sunday 263"
    assert not cli._within_its_sampling_window(published, shifted), "a weekday effect moved by 300 of 4,107"
    assert not cli._within_its_sampling_window(published, drawn.replace("Sunday 269", "Sunday 330"))
    assert not cli._within_its_sampling_window(published, drawn.replace("Saturday", "Sat"))
    assert not cli._within_its_sampling_window(published, "Monday fewer than 11, Tuesday 4061")
    assert not cli._within_its_sampling_window("", drawn)
