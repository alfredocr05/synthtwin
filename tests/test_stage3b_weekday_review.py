"""The third review of landing 3b.1 (plan P4-D355), one witness per finding.

Each test reproduces the review's own failure scenario, seeded, and
holds the repair. The mutation that turns each red is named in its own
docstring; the gate's standing record is `tests/test_stage3b_gate.py`.
"""

from __future__ import annotations

import dataclasses
import datetime
import pathlib
import random

import pytest

import calendar_certificate_verify as verifier
import fixtures
import kpi_shapes
from synthtwin import calendar_certificate, calendar_rules, contract, errors, parsing, profile, reading, taxonomy


# -- finding 10: a refusal the published numbers decide walks no day ---------


def _spread_over(years: int) -> "list[str]":
    """100 dates of June 15, one in each of 100 years spread over `years`."""
    return [f"{(step * years // 100) + 1:04d}-06-15" for step in range(100)]


def _days_walked(monkeypatch: pytest.MonkeyPatch, cells: "list[str]") -> "tuple[int, list[str]]":
    """How many days the weekday rules looked at while describing `cells`."""
    walked = [0]
    weekday_of = calendar_rules.weekday_of

    def counted(day: int) -> int:
        walked[0] += 1
        return weekday_of(day)

    calendar_certificate._ANSWERS.clear()
    with monkeypatch.context() as patched:
        patched.setattr(calendar_rules, "weekday_of", counted)
        described = taxonomy.profile_column("event_day", 1, cells, len(cells), taxonomy.Settings())
    calendar_certificate._ANSWERS.clear()
    return walked[0], described.publication_notes


def test_a_census_refused_on_its_repeats_walks_no_day_of_its_span(monkeypatch: pytest.MonkeyPatch) -> None:
    """100 dates over 400, 2,000 and 6,000 years cost the same, and are refused the same way.

    Every date is different, so no day can hold eleven rows in any table
    a reader allows -- a refusal three published numbers decide. On the
    reviewed tree the certificate enumerated every day of the span first,
    each class of days grown by copying (quadratic: 0.63 s at 400 years,
    19.3 s at 2,000 and 316 s at 6,000). Counted machine-free here: the
    days the weekday rules look at are the body's own cells at every
    span. Red when the refusal is asked after the walk (the producer's
    and `check`'s, together); the copying itself is held by
    `tests/test_no_quadratic_list_growth.py`.
    """
    found = {years: _days_walked(monkeypatch, _spread_over(years)) for years in (400, 2000, 6000)}
    counts = {years: found[years][0] for years in found}
    assert counts[400] == counts[2000] == counts[6000], counts
    assert counts[400] <= 100, counts
    for years in found:
        assert any("repeat too little" in sentence for sentence in found[years][1]), found[years][1]


def test_the_loaders_refusal_walks_no_day_of_its_span(monkeypatch: pytest.MonkeyPatch) -> None:
    """The loader's check of a census on the same numbers costs the same at every span.

    `calendar_certificate.check`, asked as the loader asks it -- the
    reader's bounds on both sides -- with the seven counts of 100
    all-different dates: its answer is `ties` at 400 and at 6,000 years,
    and the days it looks at do not grow with the span. Red when `check`
    builds the facts of the span before its refusals.
    """
    walked = [0]
    weekday_of = calendar_rules.weekday_of

    def counted(day: int) -> int:
        walked[0] += 1
        return weekday_of(day)

    answers: "dict[int, tuple[str, int]]" = {}
    for years in (400, 6000):
        cells = _spread_over(years)
        days = sorted(
            parsing.days_from_civil(int(cell[0:4]), 6, 15) for cell in cells
        )
        body = days[5:95]
        groups, _entry = calendar_rules.menu_groups(calendar_rules.body_bins(body), 3)
        calendar_certificate._ANSWERS.clear()
        walked[0] = 0
        with monkeypatch.context() as patched:
            patched.setattr(calendar_rules, "weekday_of", counted)
            verdict = calendar_certificate.check(
                100, 5, 5, body[0], body[-1], (), 90, 90, 3, groups
            )
        answers[years] = (verdict.reason, walked[0])
    calendar_certificate._ANSWERS.clear()
    assert answers[400] == answers[6000], answers
    assert answers[400][0] == calendar_rules.REASON_TIES, answers


# -- finding 1: the baseline holds no census information, its noughts included --


def _business_year() -> "list[str]":
    """The review's 1,035 rows: 260 business dates of 2024, a tail listed at each end.

    Each business date once where its index is below 20 or above 249 and
    four times otherwise, forty copies of January 1 and forty-five of
    December 27, shuffled with `Random(2)`.
    """
    start = datetime.date(2024, 1, 1)
    days = [start + datetime.timedelta(days=step) for step in range(364)]
    business = [day for day in days if day.weekday() < 5]
    cells = [day.isoformat() for place, day in enumerate(business) for _ in range(1 if place < 20 or place > 249 else 4)]
    cells += ["2024-01-01"] * 40 + ["2024-12-27"] * 45
    random.Random(2).shuffle(cells)
    return cells


def test_a_weekday_counted_empty_is_no_part_of_the_baseline(tmp_path: pathlib.Path) -> None:
    """Business dates whose empty weekend pins every business day before the p05 rung are withheld.

    The body's 258 different dates must stand on every business date
    between its boundaries once the weekend is known empty, and the p05
    rung leaves ten body rows before January 16: under the census every
    business day of January 2 to 15 holds exactly one row, where stage 3
    alone lets a Saturday take any of them (moving January 3 to January 6
    changes no stage-3 fact). The reviewed tree published the seven
    counts with `[Sat-Sun] 0`, its certificate and its brute force both
    holding the weekend empty on the side meant to know nothing of the
    census. Now the census is withheld and the menu's census copied onto
    the description is refused on load (WC8). Red when `_stage3_table`
    holds the census's empty weekdays empty again.
    """
    cells = _business_year()
    moved = ["2024-01-06" if cell == "2024-01-03" else cell for cell in cells]
    plain = taxonomy.profile_column("event_day", 1, cells, len(cells), taxonomy.Settings(), calendar_census=False)
    other = taxonomy.profile_column("event_day", 1, moved, len(moved), taxonomy.Settings(), calendar_census=False)
    assert dataclasses.asdict(plain) == dataclasses.asdict(other), "the move changes a stage-3 fact"

    described = kpi_shapes.describe(tmp_path, "business", "event_day\n" + "".join(f"{cell}\n" for cell in cells), 11)
    block = described.block("event_day")
    assert block["date_percentiles"]["p05"] == "2024-01-16"
    assert block["weekday_census"] == []
    days = sorted(verifier.day_number(cell) for cell in cells)
    body = days[block["low_tail"]["rows"]: len(days) - block["high_tail"]["rows"]]
    offered, _entry = calendar_rules.menu_groups(calendar_rules.body_bins(body), 11)
    assert offered[-1] == (5, 6, 0), offered
    doctored = dict(described.document)
    doctored["columns"] = [
        dict(block, weekday_census=[{"first": first, "last": last, "count": count} for first, last, count in offered])
    ]
    calendar_certificate._ANSWERS.clear()
    with pytest.raises(errors.ProfileError) as refusal:
        contract.load_profile(str(fixtures.write_profile(tmp_path, "doctored-profile.json", doctored)))
    calendar_certificate._ANSWERS.clear()
    assert contract.INVARIANTS["WC8"] in str(refusal.value)


# -- finding 7: repeated unparsed cells do not hide a second spelling ----------


def test_ten_copies_of_one_impossible_date_hide_no_second_spelling(tmp_path: pathlib.Path) -> None:
    """A day written twice beside ten copies of one unreadable text publishes no census.

    The gate's 1,000 admissions, one repeated date of them written once
    with a blank after it, and ten cells of `2021-02-30`: 520 different
    values of which ONE is unreadable, so 519 texts name 518 days. The
    reviewed tree asked the published count less the unparsed ROWS --
    520 less 10 -- which is no more than 518, and published the seven
    counts although one day had two spellings (WC6 (b)). Red when the
    rule is asked of those rows again.
    """
    import test_stage3b_gate as gate

    cells = gate._battery_admissions(1000)["admission_date"]
    repeated = next(cell for cell in cells if cells.count(cell) > 1)
    place = cells.index(repeated)
    written = [f'"{cell} "' if index == place else cell for index, cell in enumerate(cells)]
    written += ["2021-02-30"] * 10
    described = kpi_shapes.describe(tmp_path, "admissions", "admission_date\n" + "".join(f"{cell}\n" for cell in written), 11)
    block = described.block("admission_date")
    assert (block["n_distinct"], block["n_unparsed"]) == (len(set(cells)) + 2, 10), block["n_distinct"]
    assert block["weekday_census"] == []
    days = tuple(sorted(verifier.day_number(cell) for cell in cells))
    decided = taxonomy.weekday_decision(
        block, days, block["n_distinct"], taxonomy.Settings(small_cell_floor=11), texts=len(set(cells)) + 1
    )
    assert decided.reason == calendar_rules.REASON_SPELLINGS, decided.reason


# -- finding 6: the loader holds the holes a published absent spelling names ----


def test_a_published_absent_day_is_a_hole_the_loader_holds(tmp_path: pathlib.Path) -> None:
    """A declared missing day the description publishes leaves a group few dates, on load as at the producer.

    The gate's five weeks around 1900-01-01, described with that day
    DECLARED missing rather than judged: `sentinel_verdicts` is empty,
    and `missing_by_source` and the settings' `built_in_dates` publish
    the day. Its Mondays leave three dates besides the knot days once the
    day is a hole, so the producer withholds; the seven counts the menu
    offers, copied onto the description, loaded on the reviewed tree,
    whose loader read holes off the forms and the decisions alone. Now
    they are refused (WC7). Red when the loader leaves the published
    absent spellings out of its holes.
    """
    import test_stage3b_gate as gate

    cells = gate._around_a_placeholder_day()
    table = fixtures.write(tmp_path, "around.csv", "seen_on\n" + "".join(f"{cell}\n" for cell in cells))
    settings = taxonomy.Settings(small_cell_floor=11, declared_missing_values=("1900-01-01",))
    document = profile.build_document(reading.read_table(str(table), small_cell_floor=11), settings, [], [], [])
    block = document["columns"][0]
    assert block["sentinel_verdicts"] == [] and block["missing_by_source"] == {"1900-01-01": 20}
    assert document["settings"]["declared_missing_values"]["built_in_dates"] == ["1900-01-01"]
    assert block["weekday_census"] == []
    present = [cell for cell in cells if cell != "1900-01-01"]
    days = sorted(verifier.day_number(cell) for cell in present)
    body = days[block["low_tail"]["rows"]: len(days) - block["high_tail"]["rows"]]
    offered, _entry = calendar_rules.menu_groups(calendar_rules.body_bins(body), 11)
    doctored = dict(document)
    doctored["columns"] = [
        dict(block, weekday_census=[{"first": first, "last": last, "count": count} for first, last, count in offered])
    ]
    calendar_certificate._ANSWERS.clear()
    with pytest.raises(errors.ProfileError) as refusal:
        contract.load_profile(str(fixtures.write_profile(tmp_path, "doctored-profile.json", doctored)))
    calendar_certificate._ANSWERS.clear()
    assert contract.INVARIANTS["WC7"] in str(refusal.value)


# -- finding 8: the loader holds the storage a workbook publishes ------------------


def test_a_census_beside_values_a_workbook_publishes_stored_two_ways_is_refused(tmp_path: pathlib.Path) -> None:
    """The counts of an all-number book copied beside `text: 138, number: 687` are refused on load (WC6).

    The gate's 825 weekday-shaped dates stored as date cells publish the
    seven counts; stored with every sixth cell as ISO text they publish
    none, and the workbook block publishes both classes holding cells.
    The reviewed tree's loader never compared the two, so the first
    description's census copied onto the second loaded. Red when the
    loader's storage half of WC6 is withdrawn.
    """
    import test_stage3b_gate as gate

    draw = random.Random(3100)
    cells: "list[str]" = []
    for step in range(730):
        day = datetime.date(2022, 1, 3) + datetime.timedelta(days=step)
        times = draw.choice((0, 1, 2, 3)) if day.weekday() < 5 else draw.choice((0, 0, 0, 1))
        cells += [day.isoformat()] * times
    draw.shuffle(cells)
    found = {}
    for name, every in (("dates", 0), ("mixed", 6)):
        path = tmp_path / f"{name}.xlsx"
        path.write_bytes(gate._date_book(cells, every))
        found[name] = profile.build_document(
            reading.read_table(str(path), small_cell_floor=11), taxonomy.Settings(small_cell_floor=11), [], [], []
        )
    census = found["dates"]["columns"][0]["weekday_census"]
    mixed = found["mixed"]
    classes = mixed["source"]["workbook"]["columns"][0]["cell_classes"]
    assert census and classes["text"] > 0 and classes["number"] > 0, classes
    assert mixed["columns"][0]["weekday_census"] == []
    doctored = dict(mixed)
    doctored["columns"] = [dict(mixed["columns"][0], weekday_census=census)]
    calendar_certificate._ANSWERS.clear()
    with pytest.raises(errors.ProfileError) as refusal:
        contract.load_profile(str(fixtures.write_profile(tmp_path, "doctored-profile.json", doctored)))
    calendar_certificate._ANSWERS.clear()
    assert contract.INVARIANTS["WC6"] in str(refusal.value)
