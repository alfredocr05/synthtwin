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
import re

import pytest

import calendar_certificate_brute as brute_force
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
    assert decided.reason == calendar_rules.REASON_TEXTS, decided.reason


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


# -- item 2: a withholding is certified the way a publication is ---------------


def _business_weeks(weekend: "list[str]") -> "list[str]":
    """Four rows on every business date of 2024's first 364 days, and `weekend`, shuffled with `Random(2)`."""
    start = datetime.date(2024, 1, 1)
    days = [start + datetime.timedelta(days=step) for step in range(364)]
    cells = [day.isoformat() for day in days if day.weekday() < 5 for _ in range(4)] + weekend
    random.Random(2).shuffle(cells)
    return cells


def test_a_withheld_census_names_no_rule_the_table_decides() -> None:
    """1,040 business-day rows beside ONE Saturday row are withheld in the shared sentence, inside a certified band.

    The review's shape: the published count of different days forces at
    least 135 weekday rows, so on the reviewed tree the sentence "no
    grouping holds the line in every group" told a reader the weekend
    held one to ten rows, while the same facts with thirteen weekend rows
    published the seven counts. Now the census is withheld because its
    weekend lies in its BAND -- one row to the line more than the least
    any table of its facts holds there -- which the producer ALWAYS
    withholds, and the withholding is certified: the tables it keeps back
    include one putting the line on a day of every class, so being told
    "withheld" confines no set of days. The sentence names no rule. The
    thirteen-row table still publishes. Red when the no-grouping sentence
    comes back, or the band is withdrawn (the reason falls to `menu`).
    """
    cells = _business_weeks(["2024-06-15"])
    change = dict(zip(["2024-05-06", "2024-05-13", "2024-05-20"], ["2024-05-11", "2024-05-18", "2024-05-25"]))
    moved = [change.get(cell, cell) for cell in cells]
    one = taxonomy.profile_column("event_day", 1, cells, len(cells), taxonomy.Settings())
    thirteen = taxonomy.profile_column("event_day", 1, moved, len(moved), taxonomy.Settings())
    assert one.details["weekday_census"] == []
    assert [sentence for sentence in one.publication_notes if "not counted" in sentence] == [
        taxonomy.rendered(taxonomy.NOTE_WEEKDAY_WITHHELD_NARROWED, (11,))
    ]
    assert not any("neither each day alone" in sentence for sentence in one.publication_notes)
    assert thirteen.details["weekday_census"], "thirteen weekend rows lie outside the band and publish"
    block = dict(one.details, n_present=one.n_present, n_distinct=one.n_distinct, sentinel_verdicts=[])
    days = tuple(sorted(verifier.day_number(cell) for cell in cells))
    decided = taxonomy.weekday_decision(block, days, one.n_distinct, taxonomy.Settings(), texts=len(set(cells)))
    assert decided.reason == calendar_rules.REASON_BAND and decided.said == calendar_rules.REASON_UNSAID
    assert decided.withheld is not None and decided.withheld.holds
    least, most = decided.withheld.weekend
    assert least <= 1 and most >= 11, decided.withheld.weekend


def _outcome(instance: dict, table: "tuple[int, ...]", answer: calendar_certificate.Withholding) -> object:
    """What the producer publishes for one table of a tiny body: `withheld`, or its census.

    The producer's order, written from `taxonomy.weekday_decision`, on
    the brute force's line of three with the count of different days
    exact; WC7 is not asked, as in the gate's brute force (a body of
    seven days is all few dates), and leaving it out withholds less.
    """
    different = instance["different"]
    if not answer.holds:
        return "withheld"
    groups, _entry = calendar_rules.menu_groups(brute_force.census_of(table), brute_force.LINE)
    if not groups or calendar_certificate.in_band(tuple(groups), answer):
        return "withheld"
    facts = calendar_certificate.facts_of(
        instance["body"], 0, 0, instance["low"], instance["high"], tuple(instance["rungs"]),
        different, different, brute_force.LINE, tuple(groups), -1, (),
    )
    if not calendar_certificate.certify(facts).holds:
        return "withheld"
    return tuple(groups)


def withholding_battery(trials: int = 400, larger: int = 200) -> "dict[str, int]":
    """Every table of every tiny body, grouped by what the producer says of it, judged.

    For each set of stage-3 facts the brute force draws, EVERY table
    meeting them alone is enumerated and given its outcome
    (`_outcome`); the tables withheld together, and the tables of each
    published census, are asked whether they confine a set of days the
    facts alone do not (`brute_force.pins_of`) -- what a reader told
    only that outcome can conclude.
    """
    totals = {"facts": 0, "withheld_unsound": 0, "published_unsound": 0, "published": 0}
    for seed, count, larger_bodies in ((0, trials, False), (1, larger, True)):
        draw = random.Random(seed)
        for _trial in range(count):
            instance = brute_force.instance(draw, larger_bodies)
            if instance is None:
                continue
            totals["facts"] += 1
            different = instance["different"]
            everything = brute_force.tables(instance, False)
            answer = calendar_certificate.withholding(
                instance["body"], 0, 0, instance["low"], instance["high"], tuple(instance["rungs"]),
                different, different, brute_force.LINE,
            )
            outcomes: "dict[object, list[tuple[int, ...]]]" = {}
            for table in everything:
                bucket = outcomes.setdefault(_outcome(instance, table, answer), [])
                bucket += [table]
            for outcome, chosen in outcomes.items():
                if outcome == "withheld":
                    totals["withheld_unsound"] += bool(brute_force.pins_of(instance, chosen, everything))
                    continue
                totals["published"] += 1
                empty = {day for first, last, count in outcome for day in range(first, last + 1) if count == 0}
                zero = 0
                for place in range(instance["span"]):
                    if brute_force.weekday(instance["low"] + place) in empty:
                        zero |= 1 << place
                totals["published_unsound"] += bool(brute_force.pins_of(instance, chosen, everything, zero))
    return totals


def test_no_withholding_confines_a_set_of_days() -> None:
    """Over 400 tiny bodies and 200 larger ones, no outcome confines a set of days the facts alone do not.

    The reviewed tree's rule -- withhold wherever no grouping met the
    line, and say so -- left a withheld set confining a set of days on
    one of the 400 tiny bodies. Now no withheld set and no published
    census's own tables confine any, and some censuses still publish.
    Red when the withholding's certificate is withdrawn (every
    withholding taken as certified, no band).
    """
    totals = withholding_battery()
    assert totals["withheld_unsound"] == 0 and totals["published_unsound"] == 0, totals
    assert totals["published"] > 0, totals


# -- item 3: a report keeps a short count back from its complements too -----------


def test_a_missed_weekday_line_gives_no_count_back_by_subtraction(tmp_path: pathlib.Path) -> None:
    """The gate's missed-weekday file: its report prints no group count a subtraction reaches.

    The battery's admissions, every Sunday strictly between the
    boundaries moved to the Monday after it but three. On the reviewed
    tree the report printed present 1000, unparsed 0, tail rows 14 and
    12 and the six counts Monday to Saturday beside "Sunday fewer than
    11", and 1000 - 14 - 12 - 971 is 3. Now the line prints no count of
    any group: Sunday is named short, the others are kept back, so the
    body less what is printed is no number of a group. Red when the
    other groups' counts are printed again.
    """
    import test_stage3b_gate as gate
    from synthtwin import quality, validation

    cells = gate._battery_admissions(1000)["admission_date"]
    described = kpi_shapes.describe(tmp_path, "admissions", "admission_date\n" + "".join(f"{c}\n" for c in cells), 11)
    block = described.block("admission_date")
    low = datetime.date.fromisoformat(block["low_tail"]["boundary"])
    high = datetime.date.fromisoformat(block["high_tail"]["boundary"])
    kept = 0
    moved: "list[str]" = []
    for cell in cells:
        day = datetime.date.fromisoformat(cell)
        if low < day < high and day.weekday() == 6:
            if kept < 3:
                kept += 1
            else:
                day += datetime.timedelta(days=1)
        moved += [day.isoformat()]
    outcome = kpi_shapes.measure(described, "admission_date\n" + "".join(f"{c}\n" for c in moved), "moved.csv")
    [check] = [check for check in outcome.checks if check.fact == "datetime.weekday_census"]
    assert check.verdict == validation.MISSED
    assert "Sunday fewer than 11" in check.achieved, check.achieved
    numbers = [int(word) for word in check.achieved.replace(",", " ").split() if word.isdigit()]
    assert numbers == [11], check.achieved
    printed = quality.quality_report(described.loaded, outcome)
    found = [line for line in printed.splitlines() if "found to hold" in line and "Sunday" in line]
    assert found and all(re.findall(r"day (\d+)\b", line) == [] for line in found), found


def test_naming_the_short_groups_is_withheld_where_it_would_give_a_count_back() -> None:
    """Beside a total of twelve, one short group holds one: no group is named.

    `_short_counts_pinned` is the rule, asked here of the counts
    themselves: eleven on Monday and one on Sunday leave the Sunday one
    and only one value once a reader holds the total, so naming it is
    withheld; the gate's moved admissions leave Sunday any of one to ten.
    Red when the short groups are named whatever their total.
    """
    from synthtwin import validation

    assert validation._short_counts_pinned([11, 0, 0, 0, 0, 0, 1], [6], 11)
    assert validation._short_counts_pinned([0, 0, 0, 0, 0, 0, 7], [6], 11)
    assert not validation._short_counts_pinned([273, 173, 155, 149, 149, 72, 3], [6], 11)
    assert not validation._short_counts_pinned([30, 5, 0, 0, 0, 0, 4], [1, 6], 11)


def test_a_written_form_below_the_line_gives_no_count_back_by_subtraction(tmp_path: pathlib.Path) -> None:
    """A width census's counts are kept back beside one below the line (the weekday line's sibling).

    600 visits written `mm/dd/yyyy` publish `date_field_widths
    {padded}`. A file of the same visits with five of them written
    `m/d/yyyy` holds five cells of a width nobody published: the line for
    them prints "fewer than 11", and on the reviewed tree the `padded`
    line printed 595 beside it, while the file's parsed cells, 600, are
    printed by the lines beside -- 600 less 595 is the five. Now neither
    prints a count. Red when the complementary rule is withdrawn from the
    written forms.
    """
    draw = random.Random(4)
    days = [datetime.date(2024, 1, 1) + datetime.timedelta(days=draw.randrange(700)) for _ in range(600)]
    real = [f"{day.month:02d}/{day.day:02d}/{day.year}" for day in days]
    described = kpi_shapes.describe(tmp_path, "visits", "visit\n" + "".join(f"{cell}\n" for cell in real), 11)
    assert list(described.block("visit")["date_field_widths"]) == ["padded"]
    small = [place for place, day in enumerate(days) if day.month < 10 and day.day < 10][:5]
    assert len(small) == 5
    written = [
        f"{day.month}/{day.day}/{day.year}" if place in small else real[place]
        for place, day in enumerate(days)
    ]
    outcome = kpi_shapes.measure(described, "visit\n" + "".join(f"{cell}\n" for cell in written), "file.csv")
    widths = [check for check in outcome.checks if check.fact == "datetime.date_field_widths"]
    shown = {check.subcheck: check.achieved for check in widths}
    assert shown["widths.unnamed"] == "fewer than 11", shown
    assert all(not any(ch.isdigit() for ch in text.replace("11", "")) for text in shown.values()), shown


# -- items 4 and 5: the twin meets the census on the holes it was certified with,
# -- and keeps its count of different days --------------------------------------


def _mays_five_times() -> "list[str]":
    """The gate's three Mays five times over, written `17 May 2023`, shuffled with `Random(3)`."""
    import test_stage3b_gate as gate

    cells = [f"{day.day} May {day.year}" for day in gate._mays_only() * 5]
    random.Random(3).shuffle(cells)
    return cells


def test_the_day_pass_keeps_every_date_off_the_form_holes(tmp_path: pathlib.Path) -> None:
    """745 dates of three Mays: the twin's body holds no day outside May, and meets its census.

    `month_name_styles {title-either-space-no-comma}` tells a reader every
    cell is in May, and the census was certified with every other day a
    hole. On the reviewed tree the twin at seed 0 held 350 cells outside
    May, five of them moved there by the day pass itself, and validation
    missed nothing. Now the pass keeps every rank off the holes the
    description publishes (`calendar_rules.public_holes`) and the twin's
    cells between the two boundaries all fall in May. Red when the day
    pass reads its holes off the absent spellings alone again.
    """
    cells = _mays_five_times()
    described = kpi_shapes.describe(tmp_path, "mays", "visit\n" + "".join(f"{cell}\n" for cell in cells), 11)
    block = described.block("visit")
    assert block["month_name_styles"] == {"title-either-space-no-comma": 745} and block["weekday_census"]
    low = datetime.date.fromisoformat(block["low_tail"]["boundary"])
    high = datetime.date.fromisoformat(block["high_tail"]["boundary"])
    twin = kpi_shapes.twin_text(described, 0)
    written = [datetime.datetime.strptime(cell, "%d %B %Y").date() for cell in twin.splitlines()[1:] if cell]
    inside = [day for day in written if low <= day <= high]
    assert inside and all(day.month == 5 for day in inside), sorted({day for day in inside if day.month != 5})[:5]
    assert kpi_shapes.missed(kpi_shapes.measure(described, twin, "twin.csv")) == []


def test_a_file_with_a_date_on_a_form_hole_misses_the_census(tmp_path: pathlib.Path) -> None:
    """The validator holds the same holes: a body date moved outside May, same weekday, misses the census.

    Three of the real column's body dates moved five weeks earlier, into
    April, keep every weekday count; on the reviewed tree the file was
    HELD. It stands on days the description holds empty, so the census
    is MISSED and the line says so without a number. Red when the
    validator counts no hole.
    """
    from synthtwin import validation

    cells = _mays_five_times()
    described = kpi_shapes.describe(tmp_path, "mays", "visit\n" + "".join(f"{cell}\n" for cell in cells), 11)
    block = described.block("visit")
    low = datetime.date.fromisoformat(block["low_tail"]["boundary"])
    high = datetime.date.fromisoformat(block["high_tail"]["boundary"])
    moved: "list[str]" = []
    changed = 0
    for cell in cells:
        day = datetime.datetime.strptime(cell, "%d %B %Y").date()
        if changed < 3 and low < day - datetime.timedelta(days=35) and day.day <= 20 and day < high:
            earlier = day - datetime.timedelta(days=35)
            moved += [f"{earlier.day} {earlier.strftime('%B')} {earlier.year}"]
            changed += 1
        else:
            moved += [cell]
    assert changed == 3
    outcome = kpi_shapes.measure(described, "visit\n" + "".join(f"{cell}\n" for cell in moved), "moved.csv")
    [check] = [check for check in outcome.checks if check.fact == "datetime.weekday_census"]
    assert check.verdict == validation.MISSED, check
    assert check.achieved == check.published, (check.achieved, check.published)
    assert any("days its description holds no value on" in line for line in check.note), check.note


def _certified_fixtures() -> "dict[str, tuple[str, list[str]]]":
    """Every fixture the gate certifies a census on, and the review's May column."""
    import test_stage3b_gate as gate

    return {
        "straddling_february": ("seen_on", [f"{day.month}/{day.day}/{day.year}" for day in gate._straddling_february()]),
        "one_autumn": ("visit", [gate._day_first(day) for day in gate._one_autumn()]),
        "placeholder_read_as_missing": ("born", gate._with_a_placeholder_day()),
        "placeholder_kept": ("seen_on", gate._around_a_placeholder_day()),
        "thin_midweek": ("visit_date", gate._thin_midweek(1)),
        "twenty_sessions": ("session_date", gate._twenty_sessions(0)),
        "mays_five_times": ("visit", _mays_five_times()),
    }


@pytest.mark.parametrize("name", sorted(_certified_fixtures()))
def test_every_certified_fixture_generates_twins_that_meet_it(tmp_path: pathlib.Path, name: str) -> None:
    """Every column the gate certifies generates twins meeting everything, the count of different days included.

    The gate certified `_straddling_february` and never generated it; on
    the reviewed tree its twins at seeds 0 to 4 held 84 different days
    against 85 published, both distinct counts MISSED while the census
    was HELD -- the census moves stranded a day the count repair could
    not put back. Every fixture the gate publishes a census on is
    generated here at five seeds and validated: nothing is missed. Red
    when the day pass reads its holes off the absent spellings alone (the
    straddling column's twins lose a day again).
    """
    column, cells = _certified_fixtures()[name]
    described = kpi_shapes.describe(tmp_path, name, f"{column}\n" + "".join(f"{cell}\n" for cell in cells), 11)
    assert described.block(column)["weekday_census"], name
    for seed in range(5):
        twin = kpi_shapes.twin_text(described, seed)
        assert kpi_shapes.missed(kpi_shapes.measure(described, twin, f"twin-{seed}.csv")) == [], (name, seed)


# -- item 9: the oracle reads the holes under the column's own member ------------


def test_the_oracle_reads_an_absent_day_under_the_columns_own_member(tmp_path: pathlib.Path) -> None:
    """`weekday_hole_left` written `mm/dd/yyyy`: oracle and generator agree cell for cell.

    The frozen case's own column, its twenty absent cells spelled
    `02/23/2024` and its dates read month first at padded widths, its
    tails, rungs, seed 415 and given words kept. On the reviewed tree the
    oracle read an absent spelling as an ISO date alone, so it held no
    hole here and seven rows parted from the shipped generator's; G7.3f
    reads every spelling under the column's own member. Red when the
    oracle reads the ISO spelling alone again.
    """
    import test_generation_reference as reference
    from synthtwin import generation

    oracle = reference.gen
    original = oracle.CASE_BUILDERS["weekday_hole_left"]

    def month_first() -> dict:
        spec = original()
        column = dict(spec["column"])
        column["format"] = "month-first-date"
        column["resolution_mix"] = {"month-first-date": 132}
        column["date_field_widths"] = {"padded": 132}
        column["missing_by_source"] = {"02/23/2024": 20}
        return dict(spec, column=column)

    with pytest.MonkeyPatch.context() as patched:
        patched.setitem(oracle.CASE_BUILDERS, "weekday_hole_left", month_first)
        built = oracle.build_case("weekday_hole_left")
    case = built[0] if isinstance(built, tuple) else built
    profile_ = reference._load(case, "weekday_hole_left", tmp_path)
    written = [row[0] for row in generation.generate(profile_, reference.SEEDS["weekday_hole_left"]).rows]
    assert "02/23/2024" in case["cells"]
    apart = [(place, mine, theirs) for place, (mine, theirs) in enumerate(zip(written, case["cells"])) if mine != theirs]
    assert apart == [], apart[:8]


def _weekly_clinic(shape: int) -> "list[str]":
    """500 visits over 39 weekly clinic days, some moved a day either way (the sparse schedules measured)."""
    draw = random.Random(1000 + shape)
    first = datetime.date(2024, 1, 1) + datetime.timedelta(days=draw.randrange(100))
    days = [first + datetime.timedelta(days=7 * week + draw.choice([0, 0, 0, 1, -1])) for week in range(39)]
    weights = [draw.uniform(0.2, 3.0) for _ in days]
    return [draw.choices(days, weights)[0].isoformat() for _ in range(500)]


def test_a_column_of_few_dates_certifies_its_withholding(tmp_path: pathlib.Path) -> None:
    """500 visits over 39 weekly clinic days still publish their census beside a certified withholding.

    The withholding's certificate asks its network for tables of the
    column's own few different days, and the cheapest table spreads its
    cells over every class: 471 rows on 26 to 36 days over 57 classes
    found none, so the withholding of 39 of 80 sparse schedules could not
    be certified and their censuses were withheld whatever they held.
    Merging the cells of one stretch's half of the week into one part --
    no bounded total moves -- finds the tables. Red when the merge is
    withdrawn (the census is withheld, `uncertified`).
    """
    cells = _weekly_clinic(6)
    described = kpi_shapes.describe(tmp_path, "clinic", "visit\n" + "".join(f"{cell}\n" for cell in cells), 11)
    block = described.block("visit")
    assert block["weekday_census"], [entry["note"] for entry in described.document["publication_notes"]]
    days = tuple(sorted(verifier.day_number(cell) for cell in cells))
    decided = taxonomy.weekday_decision(block, days, block["n_distinct"], taxonomy.Settings(small_cell_floor=11), texts=len(set(cells)))
    assert decided.withheld is not None and decided.withheld.holds
