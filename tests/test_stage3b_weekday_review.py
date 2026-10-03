"""The third review of landing 3b.1 (plan P4-D355), one witness per finding, as plan P4-D365 left it.

Each test reproduces the review's own failure scenario, seeded, and
holds the repair. The mutation that turns each red is named in its own
docstring; the gate's standing record is `tests/test_stage3b_gate.py`.
Landing 3b.G (plan P4-D365, the owner's principle of 2026-10-01) retired
the full-fill certificate, the withholding's certificate, its bands, its
cap and its ties refusal: the witnesses that held only those are gone,
and each one that held a twin, a hole, a spelling, a storage or a report
is kept, its expectation moved to what the census now publishes.
"""

from __future__ import annotations

import datetime
import pathlib
import random
import re

import pytest

import fixtures
import kpi_shapes
from synthtwin import calendar_rules, contract, errors, parsing, profile, reading, taxonomy


def _day(cell: str) -> int:
    """An ISO date as a day number counted from 1970-01-01."""
    return parsing.days_from_civil(int(cell[0:4]), int(cell[5:7]), int(cell[8:10]))


# -- finding 10: a census over thousands of years walks no day of its span ---------


def _spread_over(years: int) -> "list[str]":
    """100 dates of June 15, one in each of 100 years spread over `years`."""
    return [f"{(step * years // 100) + 1:04d}-06-15" for step in range(100)]


def _days_walked(monkeypatch: pytest.MonkeyPatch, cells: "list[str]") -> "tuple[int, list[object]]":
    """How many days the weekday rules looked at while describing `cells`, and the census."""
    walked = [0]
    weekday_of = calendar_rules.weekday_of

    def counted(day: int) -> int:
        walked[0] += 1
        return weekday_of(day)

    with monkeypatch.context() as patched:
        patched.setattr(calendar_rules, "weekday_of", counted)
        described = taxonomy.profile_column("event_day", 1, cells, len(cells), taxonomy.Settings())
    return walked[0], described.details["weekday_census"]


def test_a_census_over_thousands_of_years_walks_no_day_of_its_span(monkeypatch: pytest.MonkeyPatch) -> None:
    """100 dates over 400, 2,000 and 6,000 years cost the same, and publish the same census.

    Every date is different. On the reviewed tree the certificate
    enumerated every day of the span first (quadratic: 0.63 s at 400
    years, 19.3 s at 2,000 and 316 s at 6,000), and the ties refusal
    then withheld it. Since plan P4-D365 the census the menu offers is
    published, and the days the weekday rules look at are the body's own,
    a few times over, at every span: no rule walks the days between the
    boundaries of an ISO column. Red when a rule walks the span (the
    room rule asked without a hole, say); the copying itself is held by
    `tests/test_no_quadratic_list_growth.py`.
    """
    found = {years: _days_walked(monkeypatch, _spread_over(years)) for years in (400, 2000, 6000)}
    counts = {years: found[years][0] for years in found}
    assert counts[400] == counts[2000] == counts[6000], counts
    assert counts[400] <= 300, counts
    for years in found:
        assert found[years][1], years


def test_the_loaders_check_walks_no_day_of_its_span(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The loader holds a census of 100 dates over 400 or 6,000 years to its shape without looking at a day.

    `calendar_rules.shape_breach` is a function of the census, the body
    and the line (plan P4-D365): loading either description asks
    `calendar_rules.weekday_of` of no day at all. Red when the loader asks
    a rule of the span again.
    """
    for years in (400, 6000):
        cells = _spread_over(years)
        described = kpi_shapes.describe(tmp_path / str(years), "event", "event_day\n" + "".join(f"{cell}\n" for cell in cells), 11)
        assert described.block("event_day")["weekday_census"], years
        written = fixtures.write_profile(tmp_path / str(years), "again-profile.json", described.document)
        walked = [0]
        weekday_of = calendar_rules.weekday_of

        def counted(day: int) -> int:
            walked[0] += 1
            return weekday_of(day)

        with monkeypatch.context() as patched:
            patched.setattr(calendar_rules, "weekday_of", counted)
            contract.load_profile(str(written))
        assert walked[0] == 0, (years, walked[0])


# -- finding 1: an empty weekend is published, and its twins meet it --------


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


def test_a_business_year_publishes_its_empty_weekend_and_its_twins_meet_it(tmp_path: pathlib.Path) -> None:
    """The review's 1,035 business-day rows publish Monday to Friday and an empty weekend, met by every twin.

    The reviewed tree published the seven counts with `[Sat-Sun] 0`, and
    the review withheld them because the empty weekend, beside the p05
    rung, pinned every business day of January 2 to 15 to one row -- a
    reader's reconstruction, which the owner's principle of 2026-10-01
    takes off the table. Since plan P4-D365 the census publishes, held
    to its shape on load, and the twins of seeds 0 to 2 meet it with
    nothing missed. Red when the certificate's baseline rule comes back.
    """
    cells = _business_year()
    described = kpi_shapes.describe(tmp_path, "business", "event_day\n" + "".join(f"{cell}\n" for cell in cells), 11)
    block = described.block("event_day")
    groups = tuple((group["first"], group["last"], group["count"]) for group in block["weekday_census"])
    assert groups and groups[-1] == (5, 6, 0), groups
    for seed in (0, 1, 2):
        twin = kpi_shapes.twin_text(described, seed)
        assert kpi_shapes.missed(kpi_shapes.measure(described, twin, f"twin-{seed}.csv")) == [], seed


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
    days = tuple(sorted(_day(cell) for cell in cells))
    decided = taxonomy.weekday_decision(
        block, days, block["n_distinct"], taxonomy.Settings(small_cell_floor=11), texts=len(set(cells)) + 1
    )
    assert decided.reason == calendar_rules.REASON_TEXTS, decided.reason


# -- finding 6: a published absent day is a hole ---------------------------------


def test_a_published_absent_day_is_a_hole_the_producer_reads(tmp_path: pathlib.Path) -> None:
    """A declared missing day the description publishes is a hole, and the census beside it is decided on its dates.

    The gate's five weeks around 1900-01-01, described with that day
    DECLARED missing rather than judged: `sentinel_verdicts` is empty,
    and `missing_by_source` and the settings' `built_in_dates` publish
    the day, which `calendar_rules.public_holes` reads as a hole between
    the boundaries. Five weeks of about five dates a weekday are withheld,
    `few_dates`; the seven counts the menu offers, copied onto the
    description, load, the loader holding a census to its shape alone
    (WC7, which refused them, is retired). Red when the published absent
    spellings leave the holes.
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
    days = sorted(_day(cell) for cell in present)
    body = days[block["low_tail"]["rows"]: len(days) - block["high_tail"]["rows"]]
    absent = taxonomy.published_absent(block, settings)
    assert calendar_rules.public_holes({}, block["format"], body[0], body[-1], (), absent) == (_day("1900-01-01"),)
    decided = taxonomy.weekday_decision(block, tuple(days), block["n_distinct"], settings, texts=len(set(present)))
    assert decided.reason == calendar_rules.REASON_FEW_DATES, decided.reason
    offered, _entry = calendar_rules.menu_groups(calendar_rules.body_bins(body), 11)
    doctored = dict(document)
    doctored["columns"] = [
        dict(block, weekday_census=[{"first": first, "last": last, "count": count} for first, last, count in offered])
    ]
    contract.load_profile(str(fixtures.write_profile(tmp_path, "doctored-profile.json", doctored)))


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
    with pytest.raises(errors.ProfileError) as refusal:
        contract.load_profile(str(fixtures.write_profile(tmp_path, "doctored-profile.json", doctored)))
    assert contract.INVARIANTS["WC6"] in str(refusal.value)


# -- item 2: a withholding names no rule the table decides ---------------------


def _business_weeks(weekend: "list[str]") -> "list[str]":
    """Four rows on every business date of 2024's first 364 days, and `weekend`, shuffled with `Random(2)`."""
    start = datetime.date(2024, 1, 1)
    days = [start + datetime.timedelta(days=step) for step in range(364)]
    cells = [day.isoformat() for day in days if day.weekday() < 5 for _ in range(4)] + weekend
    random.Random(2).shuffle(cells)
    return cells


def test_a_withheld_census_names_no_rule_the_table_decides() -> None:
    """1,040 business-day rows beside ONE Saturday row are withheld in the shared sentence; thirteen publish.

    The review's shape: the weekend holds one row, so no grouping of the
    menu holds the line in every group (`menu`), and on the reviewed tree
    the sentence "no grouping holds the line in every group" told a
    reader the weekend held one to ten rows. The sentence names no rule:
    the one every rule the table's own numbers decide shares, kept by
    plan P4-D365 under the owner's rule that a guard goes only at a high
    price. With thirteen weekend rows the census publishes. The owner
    accepted on 2026-09-30 that a withheld census may still tell a reader
    a half of the week holds 1 to 10 rows (K-S3-34). Red when the
    no-grouping sentence comes back.
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
    assert thirteen.details["weekday_census"], "thirteen weekend rows publish"
    block = dict(one.details, n_present=one.n_present, n_distinct=one.n_distinct, sentinel_verdicts=[])
    days = tuple(sorted(_day(cell) for cell in cells))
    decided = taxonomy.weekday_decision(block, days, one.n_distinct, taxonomy.Settings(), texts=len(set(cells)))
    assert decided.reason == calendar_rules.REASON_MENU and decided.said == calendar_rules.REASON_UNSAID


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


@pytest.mark.parametrize(("ways", "extra"), [(2, 1), (2, 5), (1, 5)])
def test_no_verdict_beside_a_short_written_form_gives_its_count_back(tmp_path: pathlib.Path, ways: int, extra: int) -> None:
    """549 dates written two ways (or one), and `extra` more written another way: no verdict gives the extra back.

    The description publishes the month-name styles' counts. On the
    repair under review the report of the longer file printed its present
    cells and no unparsed ones, every named style HELD -- the file's tally
    equal to the count a reader holds -- and the extra style "fewer than
    11" asked "at most" the extra rows: the present cells less the
    published counts is the extra, and with one extra row "at most 1"
    beside "fewer than 11" said it outright. Now a verdict is shown only
    where the ranges the lines print settle it, and the bound prints as
    no number: written two ways, nothing is settled and every line is
    withheld; written one way, the one style holds far more than its
    floor whatever the extra rows hold, so it is shown met -- WITHIN-BOUND,
    never the HELD that equals its count. The file without the extra
    rows still prints its counts, HELD. Red when the verdicts beside a
    short line are shown again (`validation._settled_verdict` bypassed),
    when a floor's worth met is shown HELD, or when the bound prints its
    number.
    """
    draw = random.Random(9)
    days = [datetime.date(2023, 1, 1) + datetime.timedelta(days=draw.randrange(700)) for _ in range(600)]
    days = [day for day in days if day.month != 5]
    real = [
        f"{day.day} {day.strftime('%B') if place % ways else day.strftime('%b')} {day.year}"
        for place, day in enumerate(days)
    ]
    described = kpi_shapes.describe(tmp_path, "visits", "visit\n" + "".join(f"{cell}\n" for cell in real), 11)
    styles = described.block("visit")["month_name_styles"]
    assert sorted(styles.values()) == sorted([len(real) - len(real) // ways, len(real) // ways][2 - ways:]), styles
    third = [f"{day.day} {day.strftime('%b').upper()} {day.year}" for day in days[:extra]]
    for cells, short in ((real + third, True), (real, False)):
        outcome = kpi_shapes.measure(described, "visit\n" + "".join(f"{cell}\n" for cell in cells), "file.csv")
        names = {check.subcheck: check for check in outcome.checks if check.fact == "datetime.month_name_styles"}
        assert len(names) == ways + 1, sorted(names)
        if not short:
            assert {check.verdict for check in names.values()} == {"HELD"}, names
            continue
        unnamed = names.pop("names.unnamed")
        assert unnamed.achieved == "fewer than 11" and unnamed.verdict == "WITHHELD" and unnamed.citation, unnamed
        expected = "WITHHELD" if ways == 2 else "WITHIN-BOUND"
        assert all(check.verdict == expected for check in names.values()), names
        shown = [check.published + " " + check.achieved for check in [unnamed, *names.values()]]
        assert all(not any(ch.isdigit() for ch in text.replace("11", "")) for text in shown), shown


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
    is MISSED and the line says so without a number -- and says what the
    counts are: the moved cells counted on their weekdays, as the tally
    equal to the published counts shows, where the note said the census
    was counted without them (the review's second round). Red when the
    validator counts no hole, and when the note says the cells were left
    out.
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
    assert any("counted on the weekdays they fall on" in line for line in check.note), check.note
    assert not any("without them" in line for line in check.note), check.note


def _published_fixtures() -> "dict[str, tuple[str, list[str]]]":
    """Every fixture the gate publishes a census on, the review's May column, and three it now publishes."""
    import test_stage3b_gate as gate

    return {
        "one_autumn": ("visit", [gate._day_first(day) for day in gate._one_autumn()]),
        "placeholder_read_as_missing": ("born", gate._with_a_placeholder_day()),
        "thin_midweek": ("visit_date", gate._thin_midweek(1)),
        "twenty_sessions": ("session_date", gate._twenty_sessions(0)),
        "mays_five_times": ("visit", _mays_five_times()),
        "straddling_february": ("seen_on", [gate._month_first(day) for day in gate._straddling_february()]),
        "walk_case": ("seen_on", gate._walk_case(0)),
        "business_days": ("log_date", gate._business_days(1, 1)),
    }


@pytest.mark.parametrize("name", sorted(_published_fixtures()))
def test_every_published_fixture_generates_twins_that_meet_it(tmp_path: pathlib.Path, name: str) -> None:
    """Every column the gate publishes a census on generates twins meeting everything, the count of different days included.

    The gate certified `_straddling_february` and never generated it; on
    the reviewed tree its twins at seeds 0 to 4 held 84 different days
    against 85 published, both distinct counts MISSED while the census
    was HELD. Every fixture the gate publishes a census on -- since plan
    P4-D365 also the 1,001 different dates and the business days the ties
    refusal withheld, and since its review (item 3) `_straddling_february`
    again, the room rule no longer asked beside width holes -- is
    generated here at five seeds and validated: nothing is missed.
    (October to December, 7.3 dates a weekday, is withheld by the mean
    of seven and a half since the same review, item 1.) Red when the day
    pass reads its holes off the absent spellings alone.
    """
    column, cells = _published_fixtures()[name]
    described = kpi_shapes.describe(tmp_path, name, f"{column}\n" + "".join(f"{cell}\n" for cell in cells), 11)
    assert described.block(column)["weekday_census"], name
    for seed in range(5):
        twin = kpi_shapes.twin_text(described, seed)
        assert kpi_shapes.missed(kpi_shapes.measure(described, twin, f"twin-{seed}.csv")) == [], (name, seed)


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


# -- the schedules the certificate withheld, published now (plan P4-D365) -----------


def _weekly_clinic(shape: int) -> "list[str]":
    """500 visits over 39 weekly clinic days, some moved a day either way (the sparse schedules measured)."""
    draw = random.Random(1000 + shape)
    first = datetime.date(2024, 1, 1) + datetime.timedelta(days=draw.randrange(100))
    days = [first + datetime.timedelta(days=7 * week + draw.choice([0, 0, 0, 1, -1])) for week in range(39)]
    weights = [draw.uniform(0.2, 3.0) for _ in days]
    return [draw.choices(days, weights)[0].isoformat() for _ in range(500)]


def _one_weekday_clinic(seed: int, weeks: int, weekday: int, rows: int) -> "list[str]":
    """`rows` visits drawn with `Random(seed)` over `weeks` weekly clinic days on one weekday of 2024."""
    draw = random.Random(seed)
    days = [datetime.date(2024, 1, 1) + datetime.timedelta(days=7 * week + weekday) for week in range(weeks)]
    weights = [draw.uniform(0.5, 1.5) for _ in days]
    return [draw.choices(days, weights)[0].isoformat() for _ in range(rows)]


def _weekly_schedule(shape: int) -> "list[str]":
    """Weekly sessions on one to three weekdays, drawn with `Random(77000 + shape)` (the review's seeded schedules)."""
    draw = random.Random(77000 + shape)
    first = datetime.date(2023, 1, 1) + datetime.timedelta(days=draw.randrange(300))
    weeks = draw.randint(15, 70)
    allowed = sorted(draw.sample(range(7), draw.randint(1, 3)))
    days = sorted({
        first + datetime.timedelta(days=7 * week + draw.choice(allowed))
        for week in range(weeks)
        if draw.random() < 0.9
    })
    rows = draw.randint(200, 1500)
    weights = [draw.choice([draw.uniform(0.2, 1), draw.paretovariate(1.3)]) for _ in days]
    return [draw.choices(days, weights)[0].isoformat() for _ in range(rows)]


def _moved(cells: "list[str]", source: str, target: str, rows: int) -> "list[str]":
    """`cells` with the first `rows` cells written `source` written `target` instead."""
    left = rows
    moved: "list[str]" = []
    for cell in cells:
        if cell == source and left > 0:
            cell, left = target, left - 1
        moved += [cell]
    return moved


def _published_and_met(tmp_path: pathlib.Path, name: str, cells: "list[str]", seeds: "tuple[int, ...]" = (0, 1, 2)) -> "list[tuple[int, int, int]]":
    """The census a column publishes, every twin of `seeds` asserted to miss nothing."""
    described = kpi_shapes.describe(tmp_path / name, name, "visit\n" + "".join(f"{cell}\n" for cell in cells), 11)
    groups = [(group["first"], group["last"], group["count"]) for group in described.block("visit")["weekday_census"]]
    for seed in seeds:
        twin = kpi_shapes.twin_text(described, seed)
        assert kpi_shapes.missed(kpi_shapes.measure(described, twin, f"twin-{seed}.csv")) == [], (name, seed)
    return groups


def test_the_schedules_the_certificate_withheld_publish_and_their_twins_meet_them(tmp_path: pathlib.Path) -> None:
    """Weekly clinics and sessions the certificate withheld publish their census, met by their twins (plan P4-D365).

    * 500 visits over 39 weekly clinic days, some moved a day either way
      (`_weekly_clinic(6)`), whose withholding the certificate could not
      certify until the third review's repair;
    * 800 visits over 20 Fridays (`_one_weekday_clinic(4, 20, 4, 800)`)
      and 212 over 26 Tuesdays, the clinics the 20,000-arrangement cap
      withheld;
    * the weekly Wednesday sessions of the owner's "Keep as built" of
      2026-09-29 (`_weekly_schedule(60)`), withheld whatever they held.

    Each publishes, and its twins at seeds 0 to 2 miss nothing. With
    thirty Wednesday rows moved to the Sunday before, that Sunday is the
    one date of its group: withheld, `few_dates`, which the twin could
    not meet keeping the count of different values. With one row moved,
    the weekend holds one row and no grouping of the menu holds the line:
    withheld, `menu`. Red when any of the retired guards comes back, or
    the few-dates rule goes.
    """
    assert _published_and_met(tmp_path, "clinic", _weekly_clinic(6))
    assert _published_and_met(tmp_path, "fridays", _one_weekday_clinic(4, 20, 4, 800))
    assert _published_and_met(tmp_path, "tuesdays", _one_weekday_clinic(0, 26, 1, 212))
    sessions = _weekly_schedule(60)
    assert {datetime.date.fromisoformat(cell).weekday() for cell in sessions} == {2}
    assert _published_and_met(tmp_path, "sessions", sessions)
    for rows, reason in ((30, calendar_rules.REASON_FEW_DATES), (1, calendar_rules.REASON_MENU)):
        cells = _moved(sessions, "2023-07-26", "2023-07-23", rows)
        moved = taxonomy.profile_column("visit", 1, cells, len(cells), taxonomy.Settings())
        assert moved.details["weekday_census"] == [], rows
        block = dict(moved.details, n_present=moved.n_present, n_distinct=moved.n_distinct, sentinel_verdicts=[])
        days = tuple(sorted(_day(cell) for cell in cells))
        decided = taxonomy.weekday_decision(block, days, moved.n_distinct, taxonomy.Settings(), texts=len(set(cells)))
        assert decided.reason == reason, (rows, decided.reason)


def _heaped_visits(seed: int) -> "list[str]":
    """The review's draw: 100 to 1,000 ISO visits over 28 to 730 days, seeded
    weekday weights, the 1st and 15th weighted eight times."""
    draw = random.Random(seed)
    rows = draw.choice([100, 120, 180, 300, 500, 1000])
    span = draw.choice([28, 45, 70, 120, 365, 730])
    days = [datetime.date(2023, 1, 2) + datetime.timedelta(days=step) for step in range(span)]
    weights = [draw.choice([0, 1, 2, 10]) for _ in range(7)]
    heaped = [weights[day.weekday()] * (8 if day.day in (1, 15) else 1) for day in days]
    if sum(heaped) == 0:
        return []
    return [day.isoformat() for day in draw.choices(days, weights=heaped, k=rows)]


def test_the_day_pass_keeps_the_days_it_found_where_the_census_allows_them(tmp_path: pathlib.Path) -> None:
    """500 visits over 70 days on four weekdays: every twin holds its 39 days and misses nothing.

    The review's second probe (`Random(8442)`). The census moves stranded
    a day the repair could not put back, because step 8.1 moves a rank only
    inside its own group and the one free day stood in another group of
    its gap: seeds 1, 2 and 4 held 38 of 39 days, both counts MISSED, while
    a twin with the pass bypassed held 39. Step 8.3 exchanges ranks across
    groups, keeping every group's count. Red when step 8.3 is withdrawn.
    """
    cells = _heaped_visits(8442)
    described = kpi_shapes.describe(tmp_path, "heaped", "visit\n" + "".join(f"{cell}\n" for cell in cells), 11)
    block = described.block("visit")
    assert block["weekday_census"] and block["n_distinct"] == 39, (block["n_distinct"], block["weekday_census"])
    for seed in range(5):
        twin = kpi_shapes.twin_text(described, seed)
        assert len(set(twin.splitlines()[1:])) == 39, seed
        assert kpi_shapes.missed(kpi_shapes.measure(described, twin, f"twin-{seed}.csv")) == [], seed


def test_where_the_census_costs_a_day_the_report_says_the_count_gave_way(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A twin short of a day the census cost it names that cause, not a shortage of spellings.

    Where the day pass finds no placement of the twin's dates meeting both
    the census and the count of different days, the census is kept and the
    count gives way, and the report says so: its general reason for a
    short count -- "the ways of writing a value ... could not supply that
    many" -- was false there. Reached here by withdrawing step 8.3 on the
    review's probe, whose seed 1 then holds 38 of 39 days with a day of
    its body still free, so the note blames no tail (a column that reaches
    it with step 8.3 in place is the next test's). Red when the day pass
    names no cause, the recount prints its own over it, or the note blames
    the tails while a day the census allows stands free.
    """
    from synthtwin import generation

    cells = _heaped_visits(8442)
    described = kpi_shapes.describe(tmp_path, "heaped", "visit\n" + "".join(f"{cell}\n" for cell in cells), 11)
    kept = generation.generate(described.loaded, 1)
    assert not [note for note in kept.deviations if note.fact.startswith("n_distinct")], kept.deviations
    monkeypatch.setattr(generation, "_weekday_exchanged", lambda *arguments: None)
    short = generation.generate(described.loaded, 1)
    named = [note for note in short.deviations if note.fact == "n_distinct"]
    caused = [note for note in named if "kept the counts per day of the week" in note.note]
    assert [(note.published, note.achieved) for note in caused] == [("39", "38")], named
    assert not [note for note in caused if "in its tails" in note.note], named
    assert not [note for note in short.deviations if "could not supply" in note.note], named
    assert not [note for note in short.deviations if note.fact == calendar_rules.WEEKDAY_CENSUS]


def _business_days_spilling_over_a_weekend(seed: int) -> "list[str]":
    """13 weeks of Monday-to-Friday visits from 2 January 2023, 20 to 30 a day
    drawn with `Random(seed)`, then 25, 5 and 1 on the Saturday, Sunday and
    Monday after the last Friday."""
    draw = random.Random(seed)
    cells: "list[str]" = []
    for step in range(7 * 13):
        day = datetime.date(2023, 1, 2) + datetime.timedelta(days=step)
        if day.weekday() < 5:
            cells += [day.isoformat()] * draw.randint(20, 30)
    for step, rows in ((0, 25), (1, 5), (2, 1)):
        cells += [(datetime.date(2023, 4, 1) + datetime.timedelta(days=step)).isoformat()] * rows
    draw.shuffle(cells)
    return cells


def _heaped_year(seed: int) -> "list[str]":
    """The second skeptic's draw (`Random(seed)`): 5,000 to 20,000 ISO visits
    over one to four years from 2 January 2023, seeded weekday weights, one
    to three days of the month heaped."""
    draw = random.Random(seed)
    rows = draw.choice([5000, 10000, 20000])
    span = draw.choice([365, 730, 1460])
    days = [datetime.date(2023, 1, 2) + datetime.timedelta(days=step) for step in range(span)]
    weights = [draw.choice([0, 0, 1, 2, 10, 20]) for _ in range(7)]
    heaped = draw.sample(range(1, 29), draw.choice([1, 2, 3]))
    times = draw.choice([4, 8, 16])
    weighted = [weights[day.weekday()] * (times if day.day in heaped else 1) for day in days]
    return [day.isoformat() for day in draw.choices(days, weights=weighted, k=rows)]


def test_a_day_the_twins_own_tails_cost_is_not_called_unplaceable(tmp_path: pathlib.Path) -> None:
    """SLOW. A count short in the twin's own tails says so, and never that no placement of the dates exists.

    A business-day log whose last rows spill over a weekend, and the
    second skeptic's column (`Random(9320)`, 20,000 visits over 2023 on
    five weekdays). Since plan P4-D375 each publishes both tail pairs and
    the high tail's end stands at least at its pair's reach, so the log's
    twin writes the lone Monday after the weekend and each twin holds as
    many different days as its column: no count is short. The note is asked of the descriptions
    written before that plan, a pair withheld -- the log's high one, both
    of the year's: the twin rebuilds such a tail from its boundary and
    rows with fewer different days than the real one, and its body
    already holds every weekday between the boundaries, so no move can
    put the days back. The report said no placement of the column's dates
    between the rungs met both counts -- which the real table refutes,
    being one. Red when the note is the old one, and when it does not
    name the tails.
    """
    from synthtwin import generation

    for name, cells, seeds, sides in (
        ("log", _business_days_spilling_over_a_weekend(1), (0, 1, 2), ("high",)),
        ("year", _heaped_year(9320), (0,), ("low", "high")),
    ):
        fresh = kpi_shapes.describe(tmp_path / name, name, "visit\n" + "".join(f"{cell}\n" for cell in cells), 11)
        block = fresh.block("visit")
        assert block["weekday_census"] and block["n_distinct"] == len(set(cells)), name
        assert block["high_tail"]["values"] is None, name
        assert block["high_tail"]["mean_distance"] is not None, name
        for seed in seeds:
            written = set(kpi_shapes.twin_text(fresh, seed).splitlines()[1:])
            assert len(written) == len(set(cells)), (name, seed)
            named = [note for note in generation.generate(fresh.loaded, seed).deviations if note.fact == "n_distinct"]
            assert named == [], (name, seed, named)
        described = kpi_shapes.written_before_p4d375(fresh, sides, taxonomy.TAIL_PINS_END)
        low, high = block["low_tail"]["boundary"], block["high_tail"]["boundary"]
        for seed in seeds:
            written = set(kpi_shapes.twin_text(described, seed).splitlines()[1:])
            weekdays = {cell for cell in cells if low <= cell <= high}
            assert {cell for cell in written if low <= cell <= high} == weekdays, (name, seed)
            named = [note for note in generation.generate(described.loaded, seed).deviations if note.fact == "n_distinct"]
            caused = [note for note in named if "kept the counts per day of the week" in note.note]
            assert [note.published for note in caused] == [str(len(set(cells)))], (name, seed, named)
            assert int(caused[0].achieved) == len(written) < len(set(cells)), (name, seed)
            assert "No placement of this column's dates" not in caused[0].note, caused[0].note
            assert "in its tails hold fewer different days" in caused[0].note, caused[0].note


def test_no_twin_of_the_reviews_draws_loses_a_day_to_the_census(tmp_path: pathlib.Path) -> None:
    """SLOW. Over the review's draws at seeds 8300 to 8499, no twin of a census column misses a count of different values.

    101 of the 200 draws publish a census; of their 505 twins at seeds 0
    to 4, ten lost a day to the census moves (four columns), and every one
    held it with the day pass bypassed. None does now. Since the weekday
    guards were dropped (plan P4-D365) 153 of the 200 publish, and none of
    their twins loses a day either. Pinned in the ledger's slow nodes. Red
    when step 8.3 is withdrawn.
    """
    columns = 0
    lost: "list[tuple[int, int]]" = []
    for draw in range(8300, 8500):
        cells = _heaped_visits(draw)
        if not cells:
            continue
        described = kpi_shapes.describe(
            tmp_path / f"d{draw}", "visit", "visit\n" + "".join(f"{cell}\n" for cell in cells), 11
        )
        if not described.block("visit")["weekday_census"]:
            continue
        columns += 1
        for seed in range(5):
            outcome = kpi_shapes.measure(described, kpi_shapes.twin_text(described, seed), f"twin-{seed}.csv")
            if [name for name in kpi_shapes.missed(outcome) if "distinct" in name]:
                lost += [(draw, seed)]
    assert columns >= 100, columns
    assert lost == [], lost


# -- the markets and logs the band search was built for, published now ------------


def _weekend_market(seed: int, midweek: int) -> "list[str]":
    """400 to 1,200 weekend rows over 180 to 364 days of 2024 and `midweek`
    Wednesday rows, drawn with `Random(4000 + seed)` (the second skeptic's markets)."""
    draw = random.Random(4000 + seed)
    span = [datetime.date(2024, 1, 1) + datetime.timedelta(days=step) for step in range(draw.randint(180, 364))]
    weekends = [day for day in span if day.weekday() >= 5]
    wednesdays = [day for day in span if day.weekday() == 2]
    weights = [draw.uniform(0.5, 1.5) for _ in weekends]
    cells = [draw.choices(weekends, weights)[0].isoformat() for _ in range(draw.randint(400, 1200))]
    cells += [draw.choice(wednesdays).isoformat() for _ in range(midweek)]
    draw.shuffle(cells)
    return cells


def _business_log(seed: int, weekend: int) -> "list[str]":
    """400 to 2,000 business-day rows over 120 to 364 days of 2023 and `weekend`
    weekend rows, drawn with `Random(4100 + seed)` (the second skeptic's logs)."""
    draw = random.Random(4100 + seed)
    span = [datetime.date(2023, 1, 2) + datetime.timedelta(days=step) for step in range(draw.randint(120, 364))]
    weekdays = [day for day in span if day.weekday() < 5]
    weekends = [day for day in span if day.weekday() >= 5]
    weights = [draw.uniform(0.5, 1.5) for _ in weekdays]
    cells = [draw.choices(weekdays, weights)[0].isoformat() for _ in range(draw.randint(400, 2000))]
    cells += [draw.choice(weekends).isoformat() for _ in range(weekend)]
    draw.shuffle(cells)
    return cells


# The weekend markets and the business log the band searches were built
# for, each beside thirty to forty rows of the other half of the week.
_HALF_BY_HALF = (
    ("market 18 beside 30", lambda: _weekend_market(2118, 30)),
    ("market 5 beside 35", lambda: _weekend_market(2105, 35)),
    ("market 2 beside 40", lambda: _weekend_market(2, 40)),
    ("log 0 beside 40", lambda: _business_log(0, 40)),
)


@pytest.mark.parametrize("name", [name for name, _build in _HALF_BY_HALF])
def test_the_markets_publish_and_their_twins_meet_them(tmp_path: pathlib.Path, name: str) -> None:
    """Every market and log the band search held back publishes its census, met by its twins (plan P4-D365).

    The weekend markets beside thirty to forty Wednesday rows, and the
    business log beside forty weekend rows: the bands withheld some of
    them and searched the rest for minutes. Each publishes now, every
    group nought or at least the line, and its twins at seeds 0 to 2 miss
    nothing. Red when the band comes back.
    """
    build = dict(_HALF_BY_HALF)[name]
    groups = _published_and_met(tmp_path, name.replace(" ", "_"), build())
    assert groups and all(calendar_rules.calendar_floor_ok(count, 11) for _first, _last, count in groups), groups


# The critic's moves: whole Mondays of May to the Saturday after, then
# single rows of 27 May to 11 May. Each pair (whole Mondays, single rows)
# gives a weekend of `1 + 4 * whole + single` rows.
WEEKEND_MOVES = ((0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (2, 3), (3, 0), (3, 1))


def weekend_moved(whole: int, single: int) -> "list[str]":
    """Four rows on every business date of the 364 days from 2024-01-01 and one
    Saturday row, `whole` Mondays of May moved to their Saturdays and `single`
    rows of 27 May to 11 May, shuffled with `Random(9)` (the critic's construction)."""
    start = datetime.date(2024, 1, 1)
    days = [start + datetime.timedelta(days=step) for step in range(364)]
    cells = [day.isoformat() for day in days if day.weekday() < 5 for _ in range(4)] + ["2024-06-15"]
    for monday, saturday in (("2024-05-06", "2024-05-11"), ("2024-05-13", "2024-05-18"), ("2024-05-20", "2024-05-25"))[:whole]:
        cells = [saturday if cell == monday else cell for cell in cells]
    cells = _moved(cells, "2024-05-27", "2024-05-11", single)
    random.Random(9).shuffle(cells)
    return cells


# -- the review of landing 3b.D1 (plan P4-D365), item 1: a missed census is not said to be met --


def test_a_census_the_twin_misses_is_not_said_to_be_met(tmp_path: pathlib.Path) -> None:
    """The calendar sentence is read off the day pass's measurement, not off the census.

    The review's scenario: 400 rows, 1 January to 9 April 2024, each date
    four times, its census replaced by Monday to Saturday nought and
    Sunday the whole body. The loader accepts it, and the body boundaries
    (a Thursday and a Saturday) leave no twin able to meet it. At seed 0
    the twin files `weekday_census` as a deviation, and on the reviewed
    tree the sentence on how the column is spread still said "the
    published counts per day of the week are met". Red when the sentence
    is read off the census alone again, or when it calls the weekday
    unpublished.
    """
    import copy

    from synthtwin import generation

    days = [datetime.date(2024, 1, 1) + datetime.timedelta(days=step) for step in range(100)]
    cells = [day.isoformat() for day in days for _ in range(4)]
    described = kpi_shapes.describe(tmp_path, "sundays", "visit\n" + "".join(f"{cell}\n" for cell in cells), 11)
    document = copy.deepcopy(described.document)
    block = document["columns"][0]
    body = 400 - block["low_tail"]["rows"] - block["high_tail"]["rows"]
    block["weekday_census"] = [{"first": 0, "last": 5, "count": 0}, {"first": 6, "last": 6, "count": body}]
    loaded = contract.load_profile(str(fixtures.write_profile(tmp_path, "edited.json", document)))
    twin = generation.generate(loaded, 0)
    assert [note.fact for note in twin.deviations if note.fact == calendar_rules.WEEKDAY_CENSUS], twin.deviations
    spread = [remark for remark in twin.remarks if remark.subject == "how these dates are spread across the calendar"]
    assert len(spread) == 1, twin.remarks
    said = f"{spread[0].held} {spread[0].note}"
    assert "counts per day of the week are met" not in said, said
    assert "counts per day of the week are not met" in said, said
    assert "which days of the week the values fall on" not in said, said
    # The column's own block carries the same sentence as the twin's list.
    assert spread[0] in twin.outcomes[0].remarks
    # The published census as it was: the sentence still says it is met.
    met = generation.generate(described.loaded, 0)
    assert not [note for note in met.deviations if note.fact == calendar_rules.WEEKDAY_CENSUS], met.deviations
    kept = [remark for remark in met.remarks if remark.subject == "how these dates are spread across the calendar"]
    assert "the published counts per day of the week are met" in kept[0].held, kept


# -- the review of landing 3b.D1, item 2: the producer's two rules are conservative, and say so --


def test_the_few_dates_rule_withholds_a_census_its_twins_meet_and_is_called_conservative(
    tmp_path: pathlib.Path,
) -> None:
    """1 to 21 January 2024, a hundred rows each: withheld, and met once restored.

    The review's scenario. Each weekday alone holds two or three of the
    body's dates, so the few-dates rule withholds the census. Restored to
    the census the menu would publish, its twins at seeds 0 to 2 hold all
    21 dates, file no deviation and miss no check, the weekday groups
    HELD. So the rule is not what no twin can meet: it is a conservative
    rule set on measured cases where twins missed, and its price is a
    census withheld that a twin would have met (plan P4-D365 counts 50
    such columns). The thresholds stay. Red when the contract, the
    module's docstring, either rule's docstring or the comment above
    either rule's reason or the few-dates thresholds calls a withheld
    census one no twin can meet again, or the rule stops withholding
    this column.
    """
    from synthtwin import generation, rendering, validation

    days = [datetime.date(2024, 1, 1) + datetime.timedelta(days=step) for step in range(21)]
    cells = [day.isoformat() for day in days for _ in range(100)]
    described = kpi_shapes.describe(tmp_path, "january", "visit\n" + "".join(f"{cell}\n" for cell in cells), 11)
    block = described.block("visit")
    assert block["weekday_census"] == [] and block["n_distinct"] == 21, block["weekday_census"]
    body = sorted(cells)[block["low_tail"]["rows"] : len(cells) - block["high_tail"]["rows"]]
    counts = [0] * 7
    for cell in body:
        counts[datetime.date.fromisoformat(cell).weekday()] += 1
    groups = tuple((weekday, weekday, counts[weekday]) for weekday in range(7))
    assert calendar_rules.few_dates(groups, [_day(cell) for cell in body])
    document = dict(described.document)
    document["columns"] = [dict(document["columns"][0], weekday_census=[{"first": first, "last": last, "count": count} for first, last, count in groups])]
    restored = contract.load_profile(str(fixtures.write_profile(tmp_path, "restored.json", document)))
    for seed in range(3):
        twin = generation.generate(restored, seed)
        assert len(set(twin.columns[0])) == 21, seed
        assert list(twin.deviations) == [], (seed, twin.deviations)
        checked = validation.measure(restored, str(fixtures.write(tmp_path, f"twin-{seed}.csv", rendering.twin_csv(twin))))
        assert kpi_shapes.missed(checked) == [], seed
        held = [check.verdict for check in checked.checks if check.subcheck == "weekday_census.groups"]
        assert held == [validation.HELD], (seed, held)
    contract_text = (fixtures.REPO_ROOT / "docs" / "spec" / "profile-contract-v6.md").read_text(encoding="utf-8")
    start = contract_text.index("WHAT THE PRODUCER WITHHOLDS BESIDE THEM")
    paragraph = " ".join(contract_text[start : contract_text.index("A FORM HOLE is", start)].split())
    assert "what no twin can meet" not in paragraph, paragraph
    assert "only by splitting" not in paragraph, paragraph
    assert "conservative" in paragraph.lower(), paragraph
    for said in (calendar_rules.few_dates.__doc__ or "", calendar_rules.room_short.__doc__ or ""):
        said = " ".join(said.split())
        assert "only by splitting" not in said and "is left empty, and with no free day" not in said, said
        assert "conservative" in said.lower(), said
    module = " ".join((calendar_rules.__doc__ or "").split())
    assert "whose twin cannot keep" not in module and "decided by what the twin can meet" not in module and "conservative" in module.lower(), module
    source = pathlib.Path(calendar_rules.__file__).read_text(encoding="utf-8").split("\n")
    for constant in ("REASON_FEW_DATES", "REASON_ROOM", "FEWEST_REAL_DATES"):
        end = next(index for index, line in enumerate(source) if line.startswith(f"{constant} = "))
        start = end
        while start > 0 and source[start - 1].startswith("#"):
            start = start - 1
        comment = " ".join(" ".join(source[start:end]).replace("#", " ").split())
        assert "conservative" in comment.lower() and "the day pass splits a date's rows" not in comment, (constant, comment)
