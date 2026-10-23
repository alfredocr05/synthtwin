"""The extra review of c5d09d5: its ten date items, each reproduced.

Every test here is built from the reviewer's OWN reproduction, with the
numbers that review measured, and every one of them turns red against
the code as it stood: the reproductions were run against c5d09d5 first
and are recorded in the plan entries P4-D250 to P4-D259.

Where a finding is about what a twin holds, the test does the round
trip stage 2's gate asks for -- describe, build, describe the twin
again, and validate the twin AND the real table at exit 0 -- because a
cell that looks right and reads back wrong is the failure this project
treats as its worst.

Every table is built by seeded neutral code at runtime (plan D13).
"""

import csv
import datetime
import io
import json
import pathlib
import sys

import pytest

from synthtwin import contract, dialect, parsing, taxonomy, validation
from tests import fixtures, workbooks

ROWS = 240


def _exit_of(argv: "list[str]") -> int:
    """Run one synthtwin command in this process and return its exit code."""
    from synthtwin import cli

    before = sys.argv
    sys.argv = ["synthtwin"] + argv
    try:
        code = cli.main()
    except SystemExit as stop:
        return 0 if stop.code is None else int(stop.code)
    finally:
        sys.argv = before
    return code


def _described(
    folder: pathlib.Path,
    cells: "list[str]",
    flags: "tuple[str, ...]" = (),
) -> "dict[str, object]":
    """Describe a one-column table of these cells and load the block."""
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "real.csv"
    table.write_text(
        fixtures.rows_to_csv(["value"], [[cell] for cell in cells]),
        encoding="utf-8",
        newline="",
    )
    assert _exit_of(
        ["profile", str(table), "--out-dir", str(folder), "--replace"]
        + list(flags)
    ) == 0
    document = json.loads(
        (folder / "real-profile.json").read_text(encoding="utf-8")
    )
    block = document["columns"][0]
    assert isinstance(block, dict)
    return block


def _round_trip(
    folder: pathlib.Path,
    cells: "list[str]",
    flags: "tuple[str, ...]" = (),
    seed: str = "4",
) -> "tuple[dict[str, object], dict[str, object], list[str], int, int]":
    """Describe, build, describe the twin; check the twin and the table."""
    first = _described(folder, cells, flags)
    profile = folder / "real-profile.json"
    assert _exit_of(
        [
            "generate", str(profile), "--out-dir", str(folder),
            "--seed", seed, "--replace",
        ]
    ) == 0
    twin = folder / "real-twin.csv"
    again = folder / "again"
    again.mkdir()
    copied = again / "twin.csv"
    copied.write_bytes(twin.read_bytes())
    assert _exit_of(
        ["profile", str(copied), "--out-dir", str(again), "--replace"]
        + list(flags)
    ) == 0
    second = json.loads(
        (again / "twin-profile.json").read_text(encoding="utf-8")
    )["columns"][0]
    written = [
        row[0]
        for row in csv.reader(io.StringIO(twin.read_text(encoding="utf-8")))
        if row
    ][1:]
    checked = folder / "check-twin"
    checked.mkdir()
    twin_exit = _exit_of(
        [
            "validate", str(profile), "--twin", str(twin),
            "--out-dir", str(checked), "--replace",
        ]
    )
    real_checked = folder / "check-real"
    real_checked.mkdir()
    real_exit = _exit_of(
        [
            "validate", str(profile), "--twin", str(folder / "real.csv"),
            "--out-dir", str(real_checked), "--replace",
        ]
    )
    return first, second, written, twin_exit, real_exit


def _misses(folder: pathlib.Path) -> "list[str]":
    """The MISSED obligations a quality report names, by fact."""
    found: "dict[str, int]" = {}
    for path in sorted(folder.iterdir()):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.rstrip().endswith(": MISSED"):
                found[line.strip().split(" [")[0]] = 1
    return sorted(found)


# -- item 1: a timestamp census published a singleton ------------------


def test_a_rare_iso_form_is_counted_into_the_commonest(
    tmp_path: pathlib.Path,
) -> None:
    """The reviewer's own shape, at a floor of eleven (plan P4-D250).

    118 ISO dates, one `2024-07-01T00:00:00` and one unreadable word
    published `resolution_mix {"iso-date": 118, "iso-datetime": 1}` and
    `datetime_separators {"(withheld)": 1}`: a form held by one row and
    a pool of one beside it. The form is counted into the commonest
    form now and the column is published wholly in it.
    """
    start = datetime.date(2024, 3, 1)
    cells = [
        (start + datetime.timedelta(days=place)).isoformat()
        for place in range(118)
    ]
    cells += ["2024-07-01T00:00:00", "plain"]
    block = _described(
        tmp_path / "rare", cells, ("--smallest-group", "11")
    )
    assert block["resolution_mix"] == {"iso-date": 119}
    assert block["datetime_separators"] == {}
    assert block["format"] == "iso-date"
    assert block["resolution"] == "date"
    assert block["time_precision"] == "date"
    # Nothing anywhere in the block names a count of one.
    for key in sorted(block):
        value = block[key]
        if isinstance(value, dict):
            for name in sorted(value):
                assert value[name] != 1 or name == "value", (key, name)


def test_a_rare_whole_date_is_counted_into_the_moments(
    tmp_path: pathlib.Path,
) -> None:
    """The same rule from the other side: the rare form is the date."""
    start = datetime.datetime(2024, 3, 1)
    cells = [
        (start + datetime.timedelta(days=place)).strftime("%Y-%m-%d %H:%M:%S")
        for place in range(118)
    ]
    cells += ["2024-08-01", "plain"]
    block = _described(
        tmp_path / "rare-date", cells, ("--smallest-group", "11")
    )
    assert block["resolution_mix"] == {"iso-datetime": 119}
    assert block["format"] == "iso-datetime"
    assert block["datetime_separators"] == {"space": 119}


def test_both_iso_forms_above_the_line_are_published_apart(
    tmp_path: pathlib.Path,
) -> None:
    """And a column whose two forms the rule can name keeps both.

    The mutation guard on the absorption: a rule that collapsed every
    joint column would pass the two tests above and fail this one.
    """
    start = datetime.date(2024, 3, 1)
    dates = [
        (start + datetime.timedelta(days=place)).isoformat()
        for place in range(60)
    ]
    stamps = [f"{day} 08:30:00" for day in dates]
    block = _described(
        tmp_path / "both", dates + stamps, ("--smallest-group", "11")
    )
    assert block["format"] == "iso-mixed"
    assert block["resolution_mix"] == {"iso-date": 60, "iso-datetime": 60}


def test_the_loader_refuses_a_form_census_naming_one_row(
    tmp_path: pathlib.Path,
) -> None:
    """RM3: the document the producer no longer writes is refused.

    And a census naming ONE form is exempt whatever its count, because
    that count is the parsed total the block prints two fields away.
    """
    start = datetime.date(2024, 3, 1)
    dates = [
        (start + datetime.timedelta(days=place)).isoformat()
        for place in range(60)
    ]
    folder = tmp_path / "forged"
    _described(folder, dates + [f"{day} 08:30:00" for day in dates])
    document = json.loads(
        (folder / "real-profile.json").read_text(encoding="utf-8")
    )
    parsed = document["columns"][0]["resolution_mix"]["iso-date"]
    parsed = parsed + document["columns"][0]["resolution_mix"]["iso-datetime"]
    document["columns"][0]["resolution_mix"] = {
        "iso-date": 1, "iso-datetime": parsed - 1
    }
    written = fixtures.write_profile(folder, "forged.json", document)
    with pytest.raises(Exception) as raised:
        contract.load_profile(f"{written}")
    assert contract.INVARIANTS["RM3"] in f"{raised.value}"


# -- item 2: placeholder judging ignored the declared order ------------


def test_placeholder_judging_reads_the_declared_order(
    tmp_path: pathlib.Path,
) -> None:
    """The reviewer's own shape, declared day first (plan P4-D251).

    Judging read the three reference days MONTH first, called the
    twenty January dates outliers and removed them; the description was
    then written day first over what was left and published 380 present
    with an earliest of `1900-01-12`.
    """
    cells = (
        ["01/01/1900"] * 20
        + ["12/01/1900"] * 125
        + ["12/02/1900"] * 125
        + ["12/03/1900"] * 130
    )
    block = _described(
        tmp_path / "declared",
        cells,
        ("--day-first", "--smallest-group", "11"),
    )
    assert block["n_present"] == 400
    assert block["n_missing"] == 0
    # READ DAY FIRST, which is what the twenty 1 January cells prove:
    # the two tail boundaries stand where a day-first reading puts them
    # (stage 3, plan P4-D328 -- the two ends this asserted are published
    # nowhere), and the outermost of all is `1900-01-01`, held by the
    # low tail's own rows.
    assert block["low_tail"]["boundary"] == "1900-01-12"
    assert block["low_tail"]["rows"] == 20
    assert block["low_tail"]["values"] == ["1900-01-01"]
    assert block["high_tail"]["boundary"] == "1900-02-12"
    assert block["high_tail"]["values"] == ["1900-03-12"]
    assert block["missing_by_source"] == {}


def test_a_placeholder_day_is_still_judged_where_it_is_one(
    tmp_path: pathlib.Path,
) -> None:
    """...and the pass still judges a real placeholder, day first.

    The mutation guard: a repair that stopped judging altogether would
    pass the test above and fail this one.
    """
    cells = (
        ["01/01/1900"] * 20
        + ["12/01/2020"] * 125
        + ["12/02/2020"] * 125
        + ["12/03/2020"] * 130
    )
    block = _described(
        tmp_path / "judged",
        cells,
        ("--day-first", "--smallest-group", "11"),
    )
    assert block["n_present"] == 380
    assert block["n_missing"] == 20
    assert block["missing_by_source"] == {"01/01/1900": 20}


# -- item 3: a midnight column acquired invented times -----------------


def test_a_midnight_column_on_three_offsets_stays_at_midnight(
    tmp_path: pathlib.Path,
) -> None:
    """The reviewer's own shape at seed 4 (plan P4-D254).

    The twin held 109 of 120 cells at midnight, eleven wearing times such
    as `03:17:59+01:00`, because the offsets were spent lexically and
    left the snapping pass no local midnight inside those ranks' gaps.
    """
    cells: "list[str]" = []
    for _repeat in range(20):
        for day in ("2024-03-01", "2024-03-02"):
            for offset in ("Z", "+01:00", "-05:00"):
                cells += [f"{day}T00:00:00{offset}"]
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "at-midnight", cells
    )
    assert first["all_at_midnight"] is True
    assert first["n_at_midnight"] == 120
    assert second["all_at_midnight"] is True
    assert second["n_at_midnight"] == 120
    assert second["utc_offsets"] == first["utc_offsets"]
    off = [cell for cell in written if "T00:00:00" not in cell]
    assert off == []
    assert (twin_exit, real_exit) == (0, 0)


# -- item 4: distinct-date restoration missed feasible targets ---------


def test_four_iso_dates_come_back_as_four(tmp_path: pathlib.Path) -> None:
    """The reviewer's first case at seed 4 (plan P4-D258).

    Seven different dates came back where the source held four, and the
    same restoration pass run again brought them to four -- so the cap,
    and not the rule, was what stopped it.
    """
    cells = (
        ["2020-04-26"] * 379
        + ["2021-06-14"] * 37
        + ["2022-09-02"] * 102
        + ["2022-12-15"] * 382
    )
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "four", cells
    )
    assert first["n_distinct"] == 4
    assert len(set(written)) == 4
    assert second["n_distinct"] == 4
    assert (twin_exit, real_exit) == (0, 0)


def test_three_textual_dates_come_back_as_three(
    tmp_path: pathlib.Path,
) -> None:
    """The reviewer's second case, which repetition alone did not fix.

    Its `02-Mar-2021` run could merge onto `04-May-2021` and keep the
    width census exact, but neither was the other's rank neighbour; its
    one `05-Apr-2020` cell sits in a gap whose every other day shows no
    width at all, so its merge has to be paid for elsewhere.
    """
    cells = ["15-Mar-2020"] * 5 + ["19-Nov-2020"] * 12 + ["04-May-2021"] * 223
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "three", cells
    )
    assert first["n_distinct"] == 3
    assert len(set(written)) == 3
    assert second["n_distinct"] == 3
    assert second["date_field_widths"] == first["date_field_widths"]
    assert (twin_exit, real_exit) == (0, 0)


# -- item 5: a below-floor keep declaration disappeared ----------------


def test_a_kept_placeholder_below_the_floor_survives_validation(
    tmp_path: pathlib.Path,
) -> None:
    """The reviewer's own shape (plan P4-D252).

    Five `01/01/1900` cells kept by declaration, beside 395 month-first
    dates, at a floor of eleven: the column's own verdict is withheld
    for its size, and the settings recorded the person's spelling
    nowhere, so validation re-judged the five cells as holes and the
    unchanged source missed fourteen obligations.
    """
    folder = tmp_path / "kept"
    folder.mkdir()
    start = datetime.date(2020, 1, 1)
    cells = ["01/01/1900"] * 5 + [
        (start + datetime.timedelta(days=place)).strftime("%m/%d/%Y")
        for place in range(395)
    ]
    block = _described(
        folder,
        cells,
        ("--smallest-group", "11", "--keep-value", "01/01/1900"),
    )
    assert block["n_present"] == 400
    assert block["sentinel_verdicts"] == []
    assert block["n_sentinel_candidates_unpublished"] == 1
    document = json.loads(
        (folder / "real-profile.json").read_text(encoding="utf-8")
    )
    settings = document["settings"]["kept_values"]
    assert settings["built_in_dates"] == ["1900-01-01"]
    assert settings["values_recorded"] is False
    checked = folder / "check-real"
    checked.mkdir()
    assert _exit_of(
        [
            "validate", str(folder / "real-profile.json"),
            "--twin", str(folder / "real.csv"),
            "--out-dir", str(checked), "--replace",
        ]
    ) == 0
    assert _misses(checked) == []


def test_a_spelling_that_denotes_no_placeholder_is_still_the_persons_own(
    tmp_path: pathlib.Path,
) -> None:
    """The mutation guard: only the two members reach that list."""
    texts, numbers, days = taxonomy.built_in_values_named(("01/01/1900",))
    assert days == ("1900-01-01",)
    assert (texts, numbers) == ((), ())
    assert taxonomy.built_in_values_named(("03/07/2021",))[2] == ()
    assert taxonomy.built_in_values_named(("12/31/9999",))[2] == (
        "9999-12-31",
    )


# -- item 6: width validation counted judged-missing cells -------------


def test_the_width_recount_leaves_out_judged_holes(
    tmp_path: pathlib.Path,
) -> None:
    """The reviewer's own shape (plan P4-D253).

    The description publishes `date_field_widths
    {"second-field-padded": 380}` over the cells it reads; the recount
    walked all 400, folded them into another width class, and the
    unchanged source was told it missed two obligations, one of them
    printing "published 380, achieved 380".
    """
    folder = tmp_path / "widths"
    folder.mkdir()
    cells = (
        ["01/01/1900"] * 20
        + ["12/01/2020"] * 125
        + ["12/02/2020"] * 125
        + ["12/03/2020"] * 130
    )
    block = _described(
        folder, cells, ("--day-first", "--smallest-group", "11")
    )
    assert block["date_field_widths"] == {"second-field-padded": 380}
    checked = folder / "check-real"
    checked.mkdir()
    assert _exit_of(
        [
            "validate", str(folder / "real-profile.json"),
            "--twin", str(folder / "real.csv"),
            "--out-dir", str(checked), "--replace",
        ]
    ) == 0
    assert _misses(checked) == []


def test_a_width_miss_prints_the_measurement_that_decided_it(
    tmp_path: pathlib.Path,
) -> None:
    """The line a file misses shows the count that missed it.

    The printing half of plan P4-D253. The verdict is settled by the
    RECOUNT of the file's own cells and the number printed beside it was
    the census of that file's description, so a miss read "the
    description asks for: 380 / the file was found to hold: 380" and
    told a reader nothing. Asked here of the checker directly, because
    the shape that separated the two numbers end to end is the one the
    same plan entry repaired.
    """
    folder = tmp_path / "printed"
    folder.mkdir()
    cells = [f"11/{1 + place % 9:02d}/2020" for place in range(ROWS)]
    block = _described(folder, cells)
    assert block["date_field_widths"] == {"second-field-padded": ROWS}
    description = contract.load_profile(f"{folder / 'real-profile.json'}")
    column = description.columns[0]
    facts = column.facts
    assert isinstance(facts, contract.DatetimeFacts)
    # The same description read back beside cells that show no width at
    # all: what decides the verdict is the recount, which is nought.
    checks = validation._written_form_checks(
        column,
        facts,
        block,
        description.settings.small_cell_floor,
        [f"11/{10 + place % 9}/2020" for place in range(ROWS)],
    )
    named = [
        check
        for check in checks
        if check.subcheck == "widths.second-field-padded"
    ]
    assert len(named) == 1
    assert named[0].verdict == validation.MISSED
    assert named[0].published == f"{ROWS}"
    assert named[0].achieved != f"{ROWS}", named[0].achieved


def test_a_below_floor_judged_placeholder_leaves_the_recount_too(
    tmp_path: pathlib.Path,
) -> None:
    """The same defect where the column's own verdict is WITHHELD.

    THE SKEPTIC'S FINDING 1 ON THE REPAIR OF ITEM 6 (plan P4-D253.1).
    P4-D253 read the judged spellings out of the verdicts the
    description PUBLISHES, so a column holding fewer placeholders than
    the line publishes no verdict, no spelling, and nothing for the hole
    rule to drop: five `01/01/1900` beside 395 month-first dates of 2020
    at a floor of eleven publish `n_present 395`, `n_missing 5`,
    `missing_by_class {"(withheld)": 5}` and `date_field_widths
    {"padded": 330}`, and the UNCHANGED SOURCE was told it missed
    `widths.padded` -- "the description asks for: 330 / the file was
    found to hold: 335". Measured on the commit under review and on the
    first repair of item 6 alike. (The census reads `{"padded": 395}`
    since the integration of 2026-09-18 folded in the disclosure pass's
    P4-D278, which counts the cells showing no width into the commonest
    one; the defect this pins is the verdict, not the figure.)

    The numeric sibling of this exact table -- five `-999` beside 395
    decimals at the same floor -- validates at exit 0, because a
    stand-in nothing names is left undecided and settled from the
    published count of holes. This asserts the day is settled the same
    way.
    """
    folder = tmp_path / "sub-floor"
    folder.mkdir()
    day = datetime.date(2020, 1, 1)
    cells = ["01/01/1900"] * 5
    for step in range(395):
        moved = day + datetime.timedelta(days=step)
        cells += [f"{moved.month:02d}/{moved.day:02d}/{moved.year}"]
    block = _described(folder, cells, ("--smallest-group", "11"))
    # The description withholds the verdict, exactly as the floor says
    # it must: nothing about those five cells is named.
    assert block["n_present"] == 395
    assert block["sentinel_verdicts"] == []
    assert block["n_sentinel_candidates_unpublished"] == 1
    assert block["missing_by_source"] == {}
    # 330 UNTIL THE INTEGRATION OF 2026-09-18, when the disclosure pass's
    # P4-D278 made the census absorb the cells that show no width: the
    # same 395 parsed cells, counted against the parsed total the reader
    # actually subtracts from. What this test pins is unchanged -- the
    # unchanged source must not be told it missed `widths.padded` -- and
    # the two assertions below are where that is measured.
    assert block["date_field_widths"] == {"padded": 395}
    checked = folder / "check-real"
    checked.mkdir()
    assert _exit_of(
        [
            "validate", str(folder / "real-profile.json"),
            "--twin", str(folder / "real.csv"),
            "--out-dir", str(checked), "--replace",
        ]
    ) == 0
    assert _misses(checked) == []


def test_a_placeholder_day_the_description_settles_is_not_dropped_twice(
    tmp_path: pathlib.Path,
) -> None:
    """The settlement is for the days no verdict names, and no others.

    The narrowness of plan P4-D253.1, asked of the rule directly. A day
    the description publishes a verdict for is settled BY that verdict --
    `read_as_missing` makes its cells holes through the spellings the
    verdict prints, and a kept day's cells are values -- so neither may
    be handed to the caller as undecided. Withdrawing that guard would
    delete a kept placeholder's cells from every recount on any column
    whose description also leaves a hole it cannot name, which is a
    larger version of the defect this whole item is about.
    """
    named = validation._placeholder_days_named(
        {
            "sentinel_verdicts": [
                {
                    "candidate": "1900-01-01",
                    "verdict": taxonomy.VERDICT_KEPT,
                    "reason": "kept_by_you",
                    "spellings": ["01/01/1900"],
                }
            ]
        }
    )
    assert named == {"1900-01-01": 1}
    # A settled day is never handed back as unsettled...
    assert not validation._an_unnamed_placeholder_day("01/01/1900", named)
    # ...and the OTHER member, which this description says nothing
    # about, still is -- in every spelling that writes it.
    assert validation._an_unnamed_placeholder_day("9999-12-31", named)
    assert validation._an_unnamed_placeholder_day("12/31/9999", named)
    assert validation._an_unnamed_placeholder_day("01/01/1900", {})
    # A day nothing names and nothing writes is no candidate at all.
    assert not validation._an_unnamed_placeholder_day("03/17/2024", {})
    assert not validation._an_unnamed_placeholder_day("", {})
    assert not validation._an_unnamed_placeholder_day("-999", {})


def test_a_kept_placeholder_survives_a_hole_the_description_cannot_name(
    tmp_path: pathlib.Path,
) -> None:
    """The settlement reaches the unnamed day and stops there.

    The wiring of plan P4-D253.1, end to end. Thirty `01/01/1900`
    declared kept -- so the description publishes the verdict
    `kept_by_you` for `1900-01-01` and counts those cells as values --
    beside five `12/31/9999`, whose own verdict the floor of eleven
    withholds, and 365 ordinary padded dates. The description publishes
    `n_present 395` and `date_field_widths {"padded": 395}`.

    A repair that settled EVERY placeholder-shaped cell rather than the
    ones no verdict names would delete the thirty kept cells from the
    recount as well, and the unchanged source would miss `widths.padded`
    at 365 against 395 -- a larger version of the defect the item is
    about, in the other direction. Measured: it does, at exit 3.
    """
    folder = tmp_path / "kept-beside-unnamed"
    folder.mkdir()
    cells = ["01/01/1900"] * 30 + ["12/31/9999"] * 5
    step = 0
    while len(cells) < 400:
        cells += [
            f"{1 + step % 9:02d}/{1 + (step // 9) % 9:02d}/{2000 + step // 81}"
        ]
        step = step + 1
    block = _described(
        folder,
        cells,
        ("--smallest-group", "11", "--keep-value", "01/01/1900"),
    )
    assert block["n_present"] == 395
    assert block["date_field_widths"] == {"padded": 395}
    verdicts = block["sentinel_verdicts"]
    assert isinstance(verdicts, list)
    assert len(verdicts) == 1
    assert verdicts[0]["candidate"] == "1900-01-01"
    assert verdicts[0]["verdict"] == taxonomy.VERDICT_KEPT
    assert block["n_sentinel_candidates_unpublished"] == 1
    checked = folder / "check-real"
    checked.mkdir()
    assert _exit_of(
        [
            "validate", str(folder / "real-profile.json"),
            "--twin", str(folder / "real.csv"),
            "--out-dir", str(checked), "--replace",
        ]
    ) == 0
    assert _misses(checked) == []


# -- item 7: the exact single-width repair lost the field --------------


def test_the_twin_keeps_the_named_width_field(
    tmp_path: pathlib.Path,
) -> None:
    """The reviewer's own shape at seed 4 (plan P4-D256).

    240 cells whose first field is eleven publish the single entry
    `second-field-padded`; the twin put its dates on days whose two
    fields both show, so its own census folded to `padded` and it
    missed both width obligations.
    """
    cells = [
        f"11/{1 + place % 9:02d}/{2020 + (place // 9) % 2}"
        for place in range(ROWS)
    ]
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "field", cells
    )
    assert first["date_field_widths"] == {"second-field-padded": ROWS}
    assert second["date_field_widths"] == {"second-field-padded": ROWS}
    assert (twin_exit, real_exit) == (0, 0)


def test_which_days_can_show_a_named_width() -> None:
    """The rule itself, on the four shapes a slashed date takes."""
    member = "month-first-date"
    assert parsing.day_shows_width("second-field-padded", member, 11, 5)
    assert not parsing.day_shows_width("second-field-padded", member, 5, 5)
    assert not parsing.day_shows_width("second-field-padded", member, 11, 15)
    # A JOINT word is met by either field, because a cell showing one
    # is folded into the joint word its column's own cells wrote.
    assert parsing.day_shows_width("padded", member, 5, 5)
    assert parsing.day_shows_width("padded", member, 11, 5)
    assert not parsing.day_shows_width("padded", member, 11, 15)
    assert parsing.day_shows_width("first-field-padded", member, 5, 15)
    # Day first turns the two fields around, and nothing else.
    assert parsing.day_shows_width(
        "second-field-padded", "day-first-date", 5, 15
    )


# -- item 8: an all-May column's permitted spelling --------------------


def test_an_all_may_column_accepts_a_resolved_length(
    tmp_path: pathlib.Path,
) -> None:
    """The reviewer's own shape at seed 4 (plan P4-D257).

    May is its own abbreviation, so the source publishes `either` and
    every twin cell of another month must resolve it; the checker
    counted all 240 as styles nobody published.
    """
    cells = [
        f"{1 + place % 28:02d}-MAY-{2020 + place // 28}"
        for place in range(ROWS)
    ]
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "may", cells
    )
    assert first["month_name_styles"] == {"upper-either-hyphen-no-comma": ROWS}
    assert (twin_exit, real_exit) == (0, 0)


def test_the_permitted_reading_of_either_keeps_the_other_three_exact() -> None:
    """The mutation guard: case, mark and comma are still exact."""
    assert parsing.name_style_agrees(
        "upper-either-hyphen-no-comma", "upper-abbreviated-hyphen-no-comma"
    )
    assert parsing.name_style_agrees(
        "upper-either-hyphen-no-comma", "upper-full-hyphen-no-comma"
    )
    assert not parsing.name_style_agrees(
        "upper-either-hyphen-no-comma", "title-abbreviated-hyphen-no-comma"
    )
    assert not parsing.name_style_agrees(
        "upper-either-hyphen-no-comma", "upper-abbreviated-space-no-comma"
    )
    assert not parsing.name_style_agrees(
        "upper-abbreviated-hyphen-no-comma", "upper-full-hyphen-no-comma"
    )


# -- item 9: XLSX serialisation destroyed the precision ----------------


def test_a_workbook_twin_keeps_its_published_subsecond_precision(
    tmp_path: pathlib.Path,
) -> None:
    """The reviewer's own shape at seed 4 (plan P4-D259).

    240 serials formatted to the millisecond publish `subsecond` and
    three figures; the twin, whose thousandths are nought, was read back
    as whole seconds and missed both obligations.
    """
    folder = tmp_path / "book"
    folder.mkdir()
    book = folder / "real.xlsx"
    book.write_bytes(workbooks.subsecond_book(ROWS))
    assert _exit_of(
        ["profile", str(book), "--out-dir", str(folder), "--replace"]
    ) == 0
    first = json.loads(
        (folder / "real-profile.json").read_text(encoding="utf-8")
    )["columns"][0]
    assert first["time_precision"] == "subsecond"
    assert first["subsecond_digits"] == 3
    assert _exit_of(
        [
            "generate", str(folder / "real-profile.json"),
            "--out-dir", str(folder), "--seed", "4", "--replace",
        ]
    ) == 0
    twin = folder / "real-twin.xlsx"
    assert twin.exists()
    again = folder / "again"
    again.mkdir()
    copied = again / "twin.xlsx"
    copied.write_bytes(twin.read_bytes())
    assert _exit_of(
        ["profile", str(copied), "--out-dir", str(again), "--replace"]
    ) == 0
    second = json.loads(
        (again / "twin-profile.json").read_text(encoding="utf-8")
    )["columns"][0]
    assert second["time_precision"] == "subsecond"
    assert second["subsecond_digits"] == 3
    checked = folder / "check-twin"
    checked.mkdir()
    assert _exit_of(
        [
            "validate", str(folder / "real-profile.json"), "--twin", str(twin),
            "--out-dir", str(checked), "--replace",
        ]
    ) == 0
    assert _misses(checked) == []


def test_a_figure_free_format_code_strands_the_precision_it_cannot_write(
    tmp_path: pathlib.Path,
) -> None:
    """The other half of item 9 (plan P4-D259.1).

    THE SKEPTIC'S FINDING 2 ON THE REPAIR OF ITEM 9. The same 240 serials
    under `yyyy-mm-dd hh:mm:ss` -- the code pandas 3.0.5 `to_excel`
    writes by default -- publish `subsecond` and three figures, correctly:
    the fraction IS stored. Their twin stands at the whole second, because
    the generation method writes the twin's fractional digits as zeros
    and says why (`docs/spec/generation-method-v1.md` G7.3: the
    description publishes how many figures there are and nothing about
    their values, so any other digit would be an invented fact), and a
    day count stores a whole second exactly as it stores no figures at
    all. So the twin missed `precision.time_precision` and
    `counts.subsecond_digits` at exit 3, on the reviewed commit and on
    the first repair of item 9 alike.

    Neither obligation is one a conforming twin can meet under that
    code, and this module refuses a check whose only outcome is a lesser
    one, so both are LISTED with the reason and the file is not accused.
    A code that DOES show the figures is checked exactly as before, which
    the test above this one asserts end to end.
    """
    folder = tmp_path / "figure-free"
    folder.mkdir()
    book = folder / "real.xlsx"
    book.write_bytes(workbooks.subsecond_book(ROWS, figures=False))
    assert _exit_of(
        ["profile", str(book), "--out-dir", str(folder), "--replace"]
    ) == 0
    description = contract.load_profile(f"{folder / 'real-profile.json'}")
    first = json.loads(
        (folder / "real-profile.json").read_text(encoding="utf-8")
    )["columns"][0]
    # The description is RIGHT: the stored fraction is a millisecond.
    assert first["time_precision"] == "subsecond"
    assert first["subsecond_digits"] == 3
    form = description.source.workbook
    assert form is not None
    assert dialect.sheet_format_figures(form.columns[0].format_code) == 0
    assert validation.subsecond_figures_unwritable(
        description, description.columns[0]
    )
    assert _exit_of(
        [
            "generate", str(folder / "real-profile.json"),
            "--out-dir", str(folder), "--seed", "4", "--replace",
        ]
    ) == 0
    twin = folder / "real-twin.xlsx"
    checked = folder / "check-twin"
    checked.mkdir()
    assert _exit_of(
        [
            "validate", str(folder / "real-profile.json"), "--twin", str(twin),
            "--out-dir", str(checked), "--replace",
        ]
    ) == 0
    assert _misses(checked) == []
    # ...and the real workbook is not accused of it either.
    real_checked = folder / "check-real"
    real_checked.mkdir()
    assert _exit_of(
        [
            "validate", str(folder / "real-profile.json"), "--twin", str(book),
            "--out-dir", str(real_checked), "--replace",
        ]
    ) == 0


def test_a_format_that_shows_the_figures_still_owes_them(
    tmp_path: pathlib.Path,
) -> None:
    """The stranding is the figure-free code and nothing wider.

    The narrowness of plan P4-D259.1, asked of the predicate directly.
    A description whose own format code shows three figures owes both
    obligations, which is item 9's first half; a repair that stranded
    every subsecond workbook column would turn the test above it into a
    check of nothing.
    """
    folder = tmp_path / "shown"
    folder.mkdir()
    book = folder / "real.xlsx"
    # AT THE POPULATION FLOOR (plan P4-D341): the command refuses a
    # smaller table and writes nothing, and what this asks is a
    # question about the FORMAT CODE, which the row count settles
    # nothing about.
    book.write_bytes(workbooks.subsecond_book(parsing.POPULATION_FLOOR))
    assert _exit_of(
        ["profile", str(book), "--out-dir", str(folder), "--replace"]
    ) == 0
    description = contract.load_profile(f"{folder / 'real-profile.json'}")
    form = description.source.workbook
    assert form is not None
    assert dialect.sheet_format_figures(form.columns[0].format_code) == 3
    assert not validation.subsecond_figures_unwritable(
        description, description.columns[0]
    )


def test_the_figures_a_date_format_shows() -> None:
    """The rule itself, and the shapes that show none."""
    assert dialect.sheet_format_figures("yyyy-mm-dd hh:mm:ss.000") == 3
    assert dialect.sheet_format_figures("yyyy-mm-dd hh:mm:ss.0") == 1
    assert dialect.sheet_format_figures("yyyy-mm-dd hh:mm:ss") == 0
    assert dialect.sheet_format_figures("General") == 0
    assert dialect.sheet_format_figures('"0.00"yyyy-mm-dd') == 0
    # And the reader writes them, nought or not.
    assert dialect.sheet_serial_moment("45300.5", "datetime", False, 3) == (
        "2024-01-09 12:00:00.000"
    )
    assert dialect.sheet_serial_moment("45300.5", "datetime", False, 0) == (
        "2024-01-09 12:00:00"
    )


# -- item 10: a tied endpoint changed the published offset -------------


def test_a_column_tied_at_its_ends_keeps_its_offsets_and_its_tails(
    tmp_path: pathlib.Path,
) -> None:
    """The reviewer's own shape at seed 4, re-derived at stage 3.

    IT WAS FROZEN FOR PLAN P4-D255, which held a rank standing on an
    end's instant to an offset that could not out-sort the end's own.
    Both end offsets are published nowhere since the tail landing (plan
    P4-D328): the description names no offset for an end row because it
    describes no end row, so the rule is gone and the fields with it.
    What this shape still pins is that a column tied at both ends comes
    back whole -- the same census of offsets, the same two boundaries
    and counts, and nothing missed on either file -- which is what the
    defect P4-D255 repaired cost it. The twin's own re-description of
    that low tail publishes its SHAPE rather than the three values the
    real column lists, and the assertions below say exactly why: the
    counts are the one thing the description withholds there, so the
    twin chose 1, 1 and 20 where the real column had 2, 2 and 18, and a
    value one cell holds is one plan P4-D342 will not list.
    """
    cells: "list[str]" = []
    for place in range(120):
        day = datetime.date(2024, 3, 1) + datetime.timedelta(days=place % 3)
        clock = "00:00:00" if place < 12 else "12:00:00"
        offset = "+01:00" if place % 2 == 0 else "+02:00"
        cells += [f"{day.isoformat()}T{clock}{offset}"]
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "tied", cells
    )
    assert second["utc_offsets"] == first["utc_offsets"]
    assert second["datetimes_read_at"] == first["datetimes_read_at"]
    for side in ("low_tail", "high_tail"):
        for key in ("boundary", "rows"):
            assert second[side][key] == first[side][key], (side, key)
    # THE TWIN STANDS ITS LOW TAIL ON THE SAME THREE INSTANTS and is
    # free to choose how many cells go on each, because the description
    # withholds that tail's mean (plan P4-D329): the counts are the one
    # thing it does not publish. MEASURED: it puts 1, 1 and 20 cells
    # where the real column had 2, 2 and 18, and a value ONE cell holds
    # is a value plan P4-D342 will not list -- so the twin's own
    # description publishes that tail's shape instead of a list. Both
    # halves are asserted, so a change to either is visible here.
    listed = first["low_tail"]["values"]
    assert isinstance(listed, list) and len(listed) == 3
    member = first["format"]
    held = []
    for value in listed:
        count = 0
        for cell in written:
            found = parsing.parse_datetime(cell, member)
            if found is None:
                continue
            shifted = parsing.utc_canonical(found[0], found[1])
            if shifted == value:
                count += 1
        held += [count]
    assert sorted(held) == [1, 1, 20], held
    assert min(held) < taxonomy.TAIL_SHARED_CELLS
    assert second["low_tail"]["values"] is None
    assert second["high_tail"]["values"] == first["high_tail"]["values"]
    assert (twin_exit, real_exit) == (0, 0)


def test_the_endpoint_offsets_are_recounted_on_the_twin() -> None:
    """The report's own detector, asked of cells that break the rule.

    The mutation guard on the recount half: `generation` has to read the
    end offsets off the ORDERED cells, as the describing step does.
    """
    ordered = taxonomy.ordered_moments(
        [
            ("2024-03-01 12:00:00", "+01:00"),
            ("2024-03-01 13:00:00", "+02:00"),
            ("2024-03-01 09:00:00", "+01:00"),
        ],
        "utc",
    )
    # The first two name one instant; the larger offset is the LAST.
    assert ordered[2] == "2024-03-01 11:00:00"
    assert ordered[4] == "+02:00"
    assert ordered[3] == "+01:00"
