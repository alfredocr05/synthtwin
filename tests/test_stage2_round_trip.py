"""Stage 2's gate: a round trip per shape.

The gate stage 2 was held to reads "the twin writes values the way the
source wrote them; a round-trip test per shape". An audit after the
landing found no test that did the round trip at all: the witnesses
looked at the twin's cells and never described the twin again, and the
comma witness passed with one grouped cell in six hundred. Whole numbers
grouped with a comma -- the commonest grouped column -- came back bare,
400 cells of 400, with every test green.

So each shape here is described, built, and the TWIN IS DESCRIBED AGAIN
under the same declarations; the two descriptions must agree on every
fact stage 2 publishes or reads by, and the twin -- and, where its own
spelling is one this tool publishes, the real table -- must meet the
description with nothing missed. A shape whose facts are designed not to
come back is pinned separately below, with what it does instead, so a
change to that design is a visible decision rather than a quiet one.

Every table is built by seeded neutral code at runtime (plan D13).
"""

import csv
import datetime
import io
import json
import pathlib
import random
import sys

import pytest

from synthtwin import parsing
from tests import fixtures

FACTS = (
    "role",
    "group_separator",
    "datetime_separators",
    "all_at_midnight",
    # ...and the two landing 2b.3 made the twin keep: the count of values
    # at midnight and the census of written forms.
    "n_at_midnight",
    "resolution_mix",
    "format",
    "resolution",
    "time_precision",
)
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


def describe_with_the_producer(
    table: pathlib.Path, description: pathlib.Path, flags: "tuple[str, ...]"
) -> None:
    """Write the description `synthtwin profile` would write, without it.

    `profile.build_document` describes a table of any size and refuses
    none; only the command applies the population floor (plan P4-D341).
    The two flags the callers of this pass are `--smallest-group` and
    `--identifier`, so the settings are built from that one number, the
    table is read at the same floor and the named columns are declared,
    exactly as the command does all three.

    WHAT IT DELIBERATELY DOES NOT DO is derive `person_columns`. That
    key records what the COMMAND counted the population by, and nothing
    here counts a population: a description written by the producer
    says the population was counted in rows, which is what a caller who
    never ran the gate did.

    AND IT REFUSES A FLAG IT DOES NOT IMPLEMENT (repair of landing
    3.2). It read `--smallest-group` and `--identifier` and dropped
    every other flag in silence, while `test_files_review_repairs._trip`
    hands it whole `flags` tuples: a caller passing `--first-row`,
    `--sheet`, `--code`, `--decimal-comma` or `--metadata-rows` would
    have described a DIFFERENT table from the one its test named, with
    nothing anywhere saying so. Every by_command=False call site passes
    only the two today, so this refuses nothing that exists; what it
    stops is the next one.
    """
    from synthtwin import profile as producer, reading, taxonomy

    floor = taxonomy.Settings().small_cell_floor
    declared: "list[str]" = []
    place = 0
    for flag in flags:
        if flag == "--smallest-group":
            floor = int(flags[place + 1])
        elif flag == "--identifier":
            declared += [flags[place + 1]]
        elif flag[:2] == "--":
            raise AssertionError(
                f"describe_with_the_producer does not implement {flag}: it "
                f"builds the settings from --smallest-group and "
                f"--identifier alone, so a table described here under any "
                f"other flag is not the table the command would describe. "
                f"Implement the flag here, or drive the case by_command"
            )
        place = place + 1
    settings = taxonomy.Settings(small_cell_floor=floor)
    read = reading.read_table(
        str(table), "auto", small_cell_floor=settings.small_cell_floor
    )
    document = producer.build_document(read, settings, declared)
    # THE BYTES ARE `fixtures.write_profile`'s, not this module's: a
    # description written here would carry the platform's line ending
    # and the loader would be right to refuse it (plan D12), and the
    # rule that keeps that in one place is
    # tests/test_description_line_endings.py.
    fixtures.write_profile(
        description.parent, description.name, document
    )


def at_the_floor(cells: "list[str]") -> "list[str]":
    """``cells`` padded to the population floor with ABSENT cells.

    `synthtwin profile` refuses a table under `parsing.POPULATION_FLOOR`
    and writes nothing (plan P4-D341), so a shape written to exercise a
    column rule and not a size has to reach it. The padding is `NA`,
    one of this format's own eighteen spellings for "no value": it
    leaves the column's PRESENT values exactly as they were, so the
    role, every census and every published count over them are the ones
    the shape produced before, and it is a ROW where an empty line in a
    one-column file would only be a blank line.

    Shapes already at the floor come back unchanged.

    THE PADDING NO LONGER REACHES THE FLOOR ON ITS OWN (repair of
    landing 3.2). The population is the rows that HOLD A VALUE, so a
    column of twenty real cells followed by eighty `NA` cells is a
    population of twenty and the command refuses it -- which is the
    whole point of that repair, and this helper is the case its skeptic
    named. What reaches the floor is the padding PLUS a column that
    holds a value on every row, which `keeper_column` adds and every
    harness here asks for through `rows_at_the_floor`.
    """
    return list(cells) + ["NA"] * (parsing.POPULATION_FLOOR - len(cells))


# The keeper column lives in `tests/fixtures.py`, where every harness
# that writes a one-column table can reach it; these names are the
# ones this module's callers already import.
KEEPER_NAME = fixtures.KEEPER_NAME
KEEPER_VALUE = fixtures.KEEPER_VALUE
rows_at_the_floor = fixtures.rows_at_the_floor


def _round_trip(
    folder: pathlib.Path,
    cells: "list[str]",
    flags: "tuple[str, ...]" = (),
    check_real: bool = True,
    seed: str = "4",
    header: str = "value",
    by_command: bool = True,
) -> "tuple[dict[str, object], dict[str, object], list[str], int, int]":
    """Describe, build, describe the twin; check the twin and the real table.

    ``by_command`` FALSE DESCRIBES WITH THE PRODUCER (plan P4-D341).
    `synthtwin profile` refuses a table under the population floor and
    writes nothing, and a shape whose ROLE depends on how many rows the
    table has -- the categorical ceiling is a share of them -- cannot be
    padded up to that floor without becoming a different shape. The
    producer describes a table of any size and refuses none, so such a
    shape is described that way and its twin is still built and checked
    through `generate` and `validate`, which is what those tests are
    about. Both the twin's re-description and the checks are the
    command's either way.
    """
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "real.csv"
    # THE KEEPER COLUMN IS THE COMMAND'S PATH ONLY. The producer
    # refuses no table for its size, so a shape described that way is
    # written exactly as it always was and its document has one column.
    names, built = (
        rows_at_the_floor(header, cells)
        if by_command
        else ([header], [[cell] for cell in cells])
    )
    table.write_text(
        fixtures.rows_to_csv(names, built),
        encoding="utf-8",
        newline="",
    )
    described = ["profile", str(table), "--out-dir", str(folder), "--replace"]
    profile = folder / "real-profile.json"
    if by_command:
        assert _exit_of(described + list(flags)) == 0
    else:
        describe_with_the_producer(table, profile, flags)
    assert _exit_of(
        ["generate", str(profile), "--out-dir", str(folder), "--seed", seed, "--replace"]
    ) == 0
    twin = folder / "real-twin.csv"
    again = folder / "again"
    again.mkdir()
    copied = again / "twin.csv"
    copied.write_bytes(twin.read_bytes())
    redescribed = ["profile", str(copied), "--out-dir", str(again), "--replace"]
    if by_command:
        assert _exit_of(redescribed + list(flags)) == 0
    else:
        describe_with_the_producer(
            copied, again / "twin-profile.json", flags
        )
    first = json.loads(profile.read_text(encoding="utf-8"))["columns"][0]
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
        ["validate", str(profile), "--twin", str(twin), "--out-dir", str(checked), "--replace"]
    )
    real_exit = 0
    if check_real:
        real_checked = folder / "check-real"
        real_checked.mkdir()
        real_exit = _exit_of(
            ["validate", str(profile), "--twin", str(table), "--out-dir", str(real_checked), "--replace"]
        )
    return first, second, written, twin_exit, real_exit


def _grouped(value: float, decimals: int) -> str:
    return f"{value:,.{decimals}f}"


def _numbers(seed: int) -> random.Random:
    return random.Random(seed)


def _moments(count: int, mark: str, seed: int) -> "list[str]":
    draw = random.Random(seed)
    start = datetime.datetime(2025, 3, 1)
    return [
        (start + datetime.timedelta(minutes=draw.randrange(0, 400000))).strftime(
            f"%Y-%m-%d{mark}%H:%M:%S"
        )
        for _ in range(count)
    ]


def _days(count: int, suffix: str, seed: int) -> "list[str]":
    draw = random.Random(seed)
    start = datetime.date(2025, 3, 1)
    return [
        (start + datetime.timedelta(days=draw.randrange(0, 300))).isoformat() + suffix
        for _ in range(count)
    ]


def _shapes() -> "dict[str, tuple[list[str], tuple[str, ...], bool, str]]":
    """Name -> (cells, declarations, check the real table too, published mark)."""
    whole = _numbers(1)
    dollars = _numbers(2)
    signed = _numbers(3)
    decimals = _numbers(4)
    stragglers = _numbers(5)
    brackets = _numbers(6)
    small = _numbers(7)
    euro = _numbers(8)
    millions = _numbers(9)
    return {
        "whole numbers 12,345": (
            [f"{whole.randint(1000, 99999):,}" for _ in range(ROWS)], (), True, ","
        ),
        "dollars $12,345": (
            [f"${dollars.randint(1000, 99999):,}" for _ in range(ROWS)], (), True, ","
        ),
        "signed +1,234 and -1,234": (
            [f"{signed.choice('+-')}{signed.randint(1000, 9999):,}" for _ in range(ROWS)],
            (),
            True,
            ",",
        ),
        "decimals 2,198.92": (
            [_grouped(decimals.uniform(1000, 99999), 2) for _ in range(ROWS)], (), True, ","
        ),
        "a few bare stragglers": (
            [_grouped(stragglers.uniform(1000, 9999), 2) for _ in range(ROWS - 5)]
            + [f"{stragglers.uniform(1000, 9999):.2f}" for _ in range(5)],
            (),
            True,
            ",",
        ),
        "accounting brackets": (
            [_grouped(brackets.uniform(1000, 9999), 2) for _ in range(ROWS - 20)]
            + [f"({brackets.uniform(100, 999):.2f})" for _ in range(20)],
            (),
            False,
            ",",
        ),
        "grouped beside values under a thousand": (
            [_grouped(small.uniform(1000, 9999), 2) for _ in range(ROWS - 60)]
            + [f"{small.uniform(1, 999):.2f}" for _ in range(60)],
            (),
            True,
            ",",
        ),
        "a declared decimal comma grouped with points": (
            [
                _grouped(euro.uniform(1000, 99999), 2)
                .replace(",", "_")
                .replace(".", ",")
                .replace("_", ".")
                for _ in range(ROWS)
            ],
            ("--decimal-comma", "value"),
            True,
            ".",
        ),
        "millions 1,234,567": (
            [f"{millions.randint(1000000, 9999999):,}" for _ in range(ROWS)], (), True, ","
        ),
        "one grouped cell among bare ones": (
            [_grouped(4321.5, 2)] + [f"{1000 + place * 3.5:.2f}" for place in range(ROWS - 1)],
            (),
            True,
            "",
        ),
        "moments with a space": (_moments(ROWS, " ", 11), (), True, ""),
        "moments with a T": (_moments(ROWS, "T", 12), (), True, ""),
        "moments with a t": (_moments(ROWS, "t", 13), (), True, ""),
        "a mix of all three marks": (
            _moments(180, " ", 14) + _moments(30, "T", 15) + _moments(30, "t", 16),
            (),
            True,
            "",
        ),
        "dates at midnight to the second": (_days(ROWS, " 00:00:00", 17), (), True, ""),
        "dates at midnight to the minute": (_days(ROWS, " 00:00", 18), (), True, ""),
        "dates at midnight with a fraction": (_days(ROWS, " 00:00:00.000", 19), (), True, ""),
        "dates at midnight with a T": (_days(ROWS, "T00:00:00", 20), (), True, ""),
        "dates at midnight with one offset": (_days(ROWS, "T00:00:00+02:00", 21), (), True, ""),
    }


def test_the_producer_helper_refuses_a_flag_it_does_not_implement(
    tmp_path: pathlib.Path,
) -> None:
    """A flag dropped in silence describes a different table (landing 3.2).

    The two it does implement go through; anything else stops the test
    that asked for it rather than quietly describing something else.
    """
    folder = tmp_path / "flags"
    folder.mkdir()
    table = folder / "real.csv"
    table.write_text(
        fixtures.rows_to_csv(["value"], [["1"] for _ in range(ROWS)]),
        encoding="utf-8",
        newline="",
    )
    describe_with_the_producer(
        table, folder / "real-profile.json", ("--smallest-group", "11")
    )
    with pytest.raises(AssertionError) as caught:
        describe_with_the_producer(
            table, folder / "other-profile.json", ("--first-row", "data")
        )
    assert "--first-row" in f"{caught.value}"


@pytest.mark.parametrize("shape", sorted(_shapes()))
def test_every_stage_2_fact_comes_back_from_the_twin(
    tmp_path: pathlib.Path, shape: str
) -> None:
    """The twin, described again, publishes what the real table published."""
    cells, flags, check_real, mark = _shapes()[shape]
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "shape", cells, flags, check_real
    )
    differ = {
        key: (first.get(key), second.get(key))
        for key in FACTS
        if first.get(key) != second.get(key)
    }
    assert differ == {}, (shape, differ)
    assert twin_exit == 0, (shape, "the twin missed an obligation")
    assert real_exit == 0, (shape, "the real table missed its own description")
    if first["role"] != "datetime":
        # The mark itself, not only its agreement: an empty mark on both
        # sides would agree while the defect stood.
        assert first.get("group_separator", "") == mark, (shape, first.get("group_separator"))
        if mark:
            assert any(mark in cell for cell in written), shape
    else:
        census = first["datetime_separators"]
        assert isinstance(census, dict) and census, shape
        if shape.startswith("dates at midnight"):
            assert first["all_at_midnight"] is True, shape
            for cell in written:
                assert cell[11:16] == "00:00", (shape, cell)


def test_a_mark_held_by_too_few_values_comes_back_held_back(
    tmp_path: pathlib.Path,
) -> None:
    """A mark too rare to name is counted into the commonest, and the twin writes it.

    Until landing 2b.3 this test pinned the loss: the six `t` were written
    with the commonest mark and the twin came back as 206 spaces. From
    landing 2b.3 the census published `{"(withheld)": 6, "space": 200,
    "upper_t": 34}`, which named the six as the one mark left: the marks
    are a closed vocabulary. SINCE PLAN P4-D220 (stage 2 closed by the
    owner rulings of 2026-09-17) the whole census pooled, and the twin
    wrote a space and a `t` on one value each and a `T` on the rest -- 238
    `T` where the table wrote 200 spaces. SINCE PLAN P4-D222 the six are
    counted into the commonest mark, and the twin writes the table's own
    spaces and capital Ts.
    """
    cells = _moments(200, " ", 31) + _moments(34, "T", 32) + _moments(6, "t", 33)
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "pooled", cells, ("--smallest-group", "30"), True
    )
    assert first["datetime_separators"] == {"space": 206, "upper_t": 34}
    assert second["datetime_separators"] == first["datetime_separators"]
    assert sum(1 for cell in written if cell[10] == "t") == 0
    assert sum(1 for cell in written if cell[10] == " ") == 206
    report = (tmp_path / "pooled" / "real-twin-report.txt").read_text(encoding="utf-8")
    assert "'value' -- datetime_separators" not in report
    assert (twin_exit, real_exit) == (0, 0)


def test_a_column_of_dates_and_midnight_moments_keeps_both_forms(
    tmp_path: pathlib.Path,
) -> None:
    """Owner decision 4 narrowed: the bare dates stay bare, the moments stay at midnight.

    Until landing 2b.3 this test pinned the loss: every cell came back as a
    moment. A column whose every value stands at midnight is generated in
    whole days, so a bare date spells each of its ranks exactly.
    """
    cells = _days(120, "", 41) + _days(120, " 00:00:00", 42)
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "mixed", cells, (), True
    )
    assert first["format"] == "iso-mixed" and first["all_at_midnight"] is True
    assert second["format"] == "iso-mixed"
    assert second["resolution_mix"] == first["resolution_mix"] == {"iso-date": 120, "iso-datetime": 120}
    assert sum(1 for cell in written if len(cell) == 10) == 120
    assert sum(1 for cell in written if len(cell) == 19 and cell.endswith(" 00:00:00")) == 120
    assert (twin_exit, real_exit) == (0, 0)


def _only_the_marks_missed(folder: pathlib.Path) -> "list[str]":
    """The MISSED subchecks of a twin's quality report, by fact.

    Since landing 2b.3 the census of marks is an obligation, so the
    absent-spelling repair's shortfall -- a deviation the twin's own
    report already names -- is also a miss of `datetime_separators`.
    That is the consistent outcome, and these tests pin that it is the
    ONLY one.
    """
    text = (folder / "check-twin" / "real-twin-quality.txt").read_text(encoding="utf-8")
    return sorted(
        {
            line.split("[")[1].split("]")[0]
            for line in text.splitlines()
            if line.rstrip().endswith(": MISSED") and "[" in line
        }
    )


def test_a_value_on_a_day_declared_absent_is_given_another_mark_and_named(
    tmp_path: pathlib.Path,
) -> None:
    """The source's own spelling of that day reads as absent, so it cannot be kept.

    At seed 4 the twin places values on that day: they are written with
    another mark, the census falls short, and the report names it.

    THE SEED MOVED FROM 0 TO 4 AT LANDING 2b.6, and which seed exercises
    this is now a property of the construction rather than an accident.
    Under the stratified placement this test was written against, 240
    ranks over 220 days gave every day about one rank, so the declared
    day was hit at essentially every seed. Ranks are drawn independently
    inside their gap now, so a particular day is hit at some seeds and
    not others: measured over seeds 0 to 39, a present rank lands on the
    declared day at 16 of them and not at the other 24. Seed 0 is one of
    the 24, so leaving it here would have left this test asserting a
    repair it never triggered -- the very thing the closure review found
    the first version of it doing. At seeds 1, 4 and 8 it fired, and the
    twin still exits 3 with exactly the mark census missed.

    AND IT MOVED FROM 4 TO 2 WHEN A GAP'S DRAWS STOPPED GIVING ITS TWO
    PINNED DAYS A WHOLE DAY'S MASS EACH (plan P4-D130). Measured again over
    seeds 0 to 39: a present rank lands on the declared day at 21 of them
    -- 0, 2, 3, 6, 7, 9, 11, 13, 14, 15, 16, 19, 20, 23, 26, 27, 31, 35,
    36, 38 and 39 -- and at every one of the 21 the twin exits 3 with the
    mark census and nothing else missed. Seed 4 is not among them.
    """
    cells = _days(220, " 00:00:00", 51) + ["2025-06-01 00:00:00"] * 20
    first, second, written, twin_exit, _real = _round_trip(
        tmp_path / "declared",
        cells,
        ("--missing-value", "2025-06-01 00:00:00"),
        False,
        seed="2",
    )
    # The twenty absent cells are written in their declared spelling, and
    # no present value wears it: described again, the twin holds exactly
    # as many values as the real table did.
    assert written.count("2025-06-01 00:00:00") == 20
    assert second["n_present"] == first["n_present"]
    moved = sum(1 for cell in written if cell and cell[10] == "T")
    assert moved > 0
    report = (tmp_path / "declared" / "real-twin-report.txt").read_text(encoding="utf-8")
    assert "datetime_separators" in report
    # SINCE PLAN P4-D222 (stage 2 closed by the owner rulings of
    # 2026-09-17) a mark fewer values than the line wrote is counted into
    # the commonest, so the twin described again counts its moved values
    # as spaces -- as the real table's own description would -- and the
    # census is met; the report still names the move.
    if moved < 2:
        assert twin_exit == 0
        assert _only_the_marks_missed(tmp_path / "declared") == []
    else:
        assert twin_exit == 3
        assert _only_the_marks_missed(tmp_path / "declared") == [
            "datetime.datetime_separators"
        ]


def test_a_repair_never_turns_a_column_of_dates_into_two_values(
    tmp_path: pathlib.Path,
) -> None:
    """The stage 2 closure review's reproduction: three spellings stay three."""
    block = [
        "2025-01-01 00:00:00",
        "2025-01-02 00:00:00",
        "2025-01-02t00:00:00",
        "2025-01-02t00:00:00",
        "2025-01-01T00:00:00",
    ]
    first, second, _written, twin_exit, _real = _round_trip(
        tmp_path / "three",
        block * 48,
        ("--missing-value", "2025-01-01T00:00:00"),
        False,
    )
    assert first["role"] == "datetime"
    assert second["role"] == "datetime", second["role"]
    # REPAIRED AT LANDING 2b.6, and re-pinned to the better behaviour
    # rather than to the shortfall it used to pin. This shape is 240
    # cells over TWO days with one spelling of the first declared
    # absent. Under the stratified placement each rank sat in its own
    # slice of a two-day range, so a large block of ranks landed on the
    # declared day, every one of them had to be given another mark, and
    # the census of marks then fell short: the twin missed
    # `datetime.datetime_separators` and exited 3. Ranks are drawn
    # across the gap now, the marks the census asks for are all
    # writable, and the twin holds the published census exactly --
    # measured: the real column publishes 96 `t` and 96 spaces, and the
    # twin writes 96 and 96.
    assert twin_exit == 0
    assert _only_the_marks_missed(tmp_path / "three") == []
    assert second["datetime_separators"] == first["datetime_separators"]


def test_labels_beside_decimal_comma_numbers_stay_labels(tmp_path: pathlib.Path) -> None:
    """The review's reproduction: `1,234,567` beside `2.397,25` is a label, and stays one."""
    # AT THE POPULATION FLOOR (plan P4-D341): the command refuses a
    # smaller table and writes nothing. The SHAPE is the two labels
    # beside a column of decimal-comma numbers, so the two labels keep
    # their five cells each and the numbers are counted up to the floor
    # from them.
    labels = 10
    numbers = [
        f"{1200.25 + 97 * place:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
        for place in range(parsing.POPULATION_FLOOR - labels)
    ]
    cells = numbers + ["1,234,567"] * 5 + ["2,345,678"] * 5
    first, second, _written, twin_exit, _real = _round_trip(
        tmp_path / "labels", cells, ("--decimal-comma", "v"), False, header="v"
    )
    assert first["role"] == "numbers_with_labels"
    assert second["role"] == "numbers_with_labels", second["role"]
    assert second["n_label_cells"] == first["n_label_cells"]
    assert twin_exit == 0


def test_a_grouped_end_is_not_mistaken_for_an_absent_spelling(tmp_path: pathlib.Path) -> None:
    """The review's reproduction: `-999.000` is a value, `-999,000` is absent."""
    # ...and at the floor for the same reason: the ten `-999,000` cells
    # are the shape and the grouped numbers are counted up to it. The
    # ABSENT cells are counted on top of the floor and not inside it
    # (repair of landing 3.2): the population is the rows that hold a
    # value, and `--missing-value -999` is what makes these ten hold
    # none, so a table of exactly the floor would be a population of
    # ninety and the command would be right to refuse it. `keeper_column`
    # cannot see this, because the spelling is absent only under a flag
    # it is not given.
    absent = 10
    cells = [
        f"{-1000000 + 25 * place:,}".replace(",", ".")
        for place in range(parsing.POPULATION_FLOOR)
    ]
    cells += ["-999,000"] * absent
    first, second, _written, twin_exit, _real = _round_trip(
        tmp_path / "end",
        cells,
        ("--decimal-comma", "v", "--missing-value", "-999"),
        False,
        header="v",
    )
    assert second["n_present"] == first["n_present"]
    assert second["n_missing"] == first["n_missing"]
    assert twin_exit == 0


def test_a_twin_too_small_to_prove_its_mark_says_so(tmp_path: pathlib.Path) -> None:
    """The review's reproduction at a raised floor: the loss is named, not silent."""
    cells = ["1,040.16", "1,091.80", "801.65", "766.75", "229.49",
             "540.78", "283.64", "180.77", "115.02", "222.04"]
    # DESCRIBED BY THE PRODUCER (plan P4-D341): TEN cells is the shape
    # -- a twin with too few slots to prove the mark -- and a table
    # grown to the population floor has room and proves it. The
    # producer refuses no table for its size, and the twin is still
    # built and reported on by the commands, which is where the loss
    # has to be named.
    first, second, _written, _twin_exit, _real = _round_trip(
        tmp_path / "small",
        cells,
        ("--smallest-group", "2"),
        False,
        by_command=False,
    )
    assert first["group_separator"] == ","
    report = (tmp_path / "small" / "real-twin-report.txt").read_text(encoding="utf-8")
    if second["group_separator"] != ",":
        assert "group_separator" in report


def test_an_ordinary_blank_raises_no_warning_about_absent_spellings(
    tmp_path: pathlib.Path,
) -> None:
    """The review's reproduction: a pooled blank is not a declared absent spelling."""
    cells = [f"2025-01-{(place % 28) + 1:02d} 00:00:00" for place in range(240)] + [""]
    first, second, _written, twin_exit, _real = _round_trip(
        tmp_path / "blank", cells, ("--smallest-group", "11"), False
    )
    report = (tmp_path / "blank" / "real-twin-report.txt").read_text(encoding="utf-8")
    assert "counted in a group too small to name" not in report
    assert "missing_by_class" not in report
    assert twin_exit == 0


@pytest.mark.parametrize("seed", ["0", "4", "31"])
def test_a_case_only_respelling_never_turns_moments_into_two_values(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """The confirmation review's reproduction: a `t` beside a `T` is one value.

    Ten cells of three case-folded values, with one lower-case spelling
    declared absent. The census repair used to hand a last copy the mark
    that folded it onto an existing value, and the twin read back as a
    column of two values -- binary -- with nothing said. Every seed from
    0 to 31 did it.
    """
    cells = (
        ["2025-01-01 00:00:00"] * 2
        + ["2025-01-02 00:00:00"]
        + ["2025-01-02T00:00:00"] * 2
        + ["2025-01-02t00:00:00"]
        + ["2025-01-01t00:00:00"] * 4
    )
    # FLOOR ONE (plan P4-D316): ten cells whose separators are counts of
    # one to four, which only a floor below eleven names.
    # AT THE POPULATION FLOOR ON ABSENT CELLS (plan P4-D341): the
    # command refuses a smaller table, and what this witness is about is
    # the TEN cells' own spellings and the counts of one to four they
    # stand on. `at_the_floor` pads with `NA`, which leaves every one of
    # those -- and the separator census taken over them -- exactly as it
    # was.
    first, second, _written, twin_exit, _real = _round_trip(
        tmp_path / "case",
        at_the_floor(cells),
        ("--missing-value", "2025-01-01t00:00:00", "--smallest-group", "1"),
        False,
        seed=seed,
    )
    assert (first["role"], first["n_distinct"], first["n_distinct_folded"]) == (
        "datetime", 4, 3
    )
    assert second["role"] == "datetime", second["role"]
    assert isinstance(second["n_distinct_folded"], int)
    assert second["n_distinct_folded"] >= 3
    # REPAIRED AT LANDING 2b.6, on the same cause as the three-spelling
    # shape above and re-pinned the same way. Ten cells over two days
    # left the stratified placement no room: ranks piled onto the
    # declared-absent spelling's day, the census repair could not give
    # them all a mark the census names, and the twin missed
    # `datetime.datetime_separators`. Measured after the change at all
    # three seeds: the real column publishes one `t`, three spaces and
    # two `T`, and the twin writes exactly that, holding four different
    # values as the real column does.
    assert twin_exit == 0
    assert _only_the_marks_missed(tmp_path / "case") == []
    # SINCE PLAN P4-D222 (stage 2 closed by the owner rulings of
    # 2026-09-17) the real column's one `t` is counted into the commonest
    # mark: a census naming three spaces and two `T` beside six values named
    # the one left, and plan P4-D220's whole pool lost the spaces. The twin
    # writes four spaces and two `T`, holding three different values where
    # the real column holds four, and as many case-folded values, so the
    # shape is still no binary column.
    assert first["datetime_separators"] == {"space": 4, "upper_t": 2}
    assert second["datetime_separators"] == first["datetime_separators"]
    assert first["n_distinct"] == 4


@pytest.mark.parametrize("seed", ["0", "4"])
def test_a_day_whose_every_spelling_is_absent_gets_no_value(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """The confirmation review's reproduction: a wholly absent day is stepped past.

    January 2 is written three ways and every one is declared absent, so
    no value of the twin may land on it: a whole-day rank that would is
    moved to the nearest present day inside its own window, and the twin
    holds as many values as the real table.
    """
    cells = (
        ["2025-01-01 00:00:00"] * 20
        + ["2025-01-03 00:00:00"] * 20
        + ["2025-01-04 00:00:00"] * 20
        + ["2025-01-02 00:00:00"] * 5
        + ["2025-01-02T00:00:00"] * 5
        + ["2025-01-02t00:00:00"] * 5
    )
    flags = (
        "--missing-value", "2025-01-02 00:00:00",
        "--missing-value", "2025-01-02T00:00:00",
        "--missing-value", "2025-01-02t00:00:00",
    )
    # AT THE POPULATION FLOOR ON ABSENT CELLS (plan P4-D341): the
    # command refuses a smaller table, and what this witness is about
    # is the sixty PRESENT moments and the fifteen cells of the wholly
    # absent day. `at_the_floor` pads with `NA`, so both of those stay
    # exactly what they were and only the absent total grows.
    padding = parsing.POPULATION_FLOOR - len(cells)
    first, second, written, twin_exit, _real = _round_trip(
        tmp_path / "absent-day", at_the_floor(cells), flags, True, seed=seed
    )
    assert second["n_present"] == first["n_present"] == 60
    assert second["n_missing"] == first["n_missing"] == 15 + padding
    assert twin_exit == 0
    # THE TWIN'S PRESENT MOMENTS: not a blank, not one of the absent
    # cells the padding to the floor added, and not the wholly absent
    # day. A moment is what starts with the month these cells are in,
    # which is the test the padding cannot pass.
    present = [
        cell
        for cell in written
        if cell.startswith("2025-01-") and not cell.startswith("2025-01-02")
    ]
    assert len(present) == 60


def test_a_column_of_dates_that_collapses_to_two_days_is_named(
    tmp_path: pathlib.Path,
) -> None:
    """A twin read back as a column of two values says so (confirmation review)."""
    cells = ["2025-01-01"] * 10 + ["2025-01-02", "2025-01-03"]
    # DESCRIBED BY THE PRODUCER (plan P4-D341): the shape is TWELVE
    # cells collapsing to two days, and a table at the population floor
    # the command requires does not collapse.
    first, second, _written, _twin_exit, _real = _round_trip(
        tmp_path / "days", cells, (), False, seed="0", by_command=False
    )
    assert first["role"] == "datetime"
    report = (tmp_path / "days" / "real-twin-report.txt").read_text(encoding="utf-8")
    if second["role"] != "datetime":
        assert "n_distinct_folded" in report


def test_a_sparse_signed_column_meets_every_published_rung(
    tmp_path: pathlib.Path,
) -> None:
    """Landing 2b.2's carried seed-19 rung, closed and pinned here.

    Landing 2b.2 reported one seed of this shape still missing
    `ladder.p95` and carried it as the percentile-rung defect; the two
    landings after it repeated the sentence without measuring it again,
    the last of them recording that it could not find the shape.

    MEASURED AGAINST THE COMMIT THE CARRY ITSELF NAMES. At 53bb012 this
    column's twin exits 3 reading `ladder.p95 [numeric.percentiles]:
    MISSED`, on seed 19 alone of the six seeds the carry was taken
    over; on this tree all six exit 0. So the carry is closed rather
    than waiting on stage 3's tail shape, and this is what keeps it
    closed.

    IT ASSERTS IT IS THE SHAPE THE RUNG TURNS ON BEFORE IT ASSERTS THE
    ANSWER. A column of plain whole numbers passes this test with the
    defect still in place, so the fixture is held to the mixture that
    reproduced it: 900 cells, every one carrying a sign, about half
    written as whole numbers and half at two decimal places.
    """
    draw = _numbers(19)
    cells: "list[str]" = []
    for _step in range(900):
        if draw.random() < 0.5:
            cells += [f"{round(draw.gauss(0, 300)):+d}"]
        else:
            cells += [f"{round(draw.gauss(0, 300), 2):+.2f}"]
    first, second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "rungs", cells, (), True, seed="19", header="change"
    )
    # The shape the rung turns on, asserted first.
    assert first["n_present"] == 900, first["n_present"]
    styles = first["numeric_styles"]
    assert styles["leading_plus"] > 200, styles
    assert styles["decimal"] > 200, styles
    assert first["percentiles"]["p95"] is not None
    # ...and then the answer.
    assert "numeric.percentiles" not in _only_the_marks_missed(
        tmp_path / "rungs"
    )
    assert twin_exit == 0
    assert real_exit == 0
    assert second["percentiles"]["p95"] is not None


def _wide_keys(seed: int, count: int = 800) -> "list[str]":
    """Canonical seventeen-figure keys: the figures each value itself writes."""
    draw = _numbers(seed)
    cells: "list[str]" = []
    for _step in range(count):
        cells += [f"{int(float(draw.randrange(10 ** 16, 10 ** 17)))}"]
    return cells


def _a_value_preserving_neighbour(text: str) -> str:
    """A DIFFERENT run of figures reading back as the same double.

    Past 2**53 the spacing between doubles reaches two, so a run one or
    two away from this one denotes the very same number. That is the
    respelling no published fact could see before `wide_runs`.
    """
    value = float(text)
    whole = int(text)
    for step in (1, -1, 2, -2, 3, -3):
        candidate = f"{whole + step}"
        if float(candidate) == value and candidate != text:
            return candidate
    return text


@pytest.mark.parametrize("seed", [1, 7])
def test_a_column_of_wide_keys_keeps_the_spelling_its_own_values_write(
    seed: int, tmp_path: pathlib.Path
) -> None:
    """Landing 2b.13's canonical question, asked at last (plan P4-D90).

    Plan P4-D66.2 admitted the figures of a whole number past 2**53 as a
    spelling of its own value, so that a real export of seventeen-figure
    accession numbers stopped being told its own file failed its own
    description. The canonical question went with it: `styles.spelled`
    asks whether a cell DENOTES its value, and past that bound more than
    one run of figures does, while the ceiling beside it reads the
    published count of the form -- which on a column of identifiers is
    the row count, so it licenses every cell.

    MEASURED BEFORE THE FACT EXISTED: this very column, respelled cell
    by cell into the value-preserving neighbours a double cannot tell
    apart -- 790 of 800 moved at seed 1, 783 of 800 at seed 7 --
    validated against its own description at exit 0 with nothing missed.

    So this asserts the shape FIRST, because a column of narrow whole
    numbers passes every line below with the defect still in place: the
    keys have to be wide enough that a neighbour exists at all.
    """
    cells = _wide_keys(seed)
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "wide", cells, (), True, seed=str(seed), header="record_id"
    )
    # The shape the question turns on, asserted before the answer.
    assert first["n_present"] == 800, first["n_present"]
    assert first["numeric_styles"] == {"plain": 800}, first["numeric_styles"]
    assert first["wide_runs"] == "canonical", first["wide_runs"]
    moved = 0
    for cell in cells:
        if _a_value_preserving_neighbour(cell) != cell:
            moved += 1
    assert moved > 700, moved
    # ...and then the answer: the twin comes back canonical, and BOTH
    # files meet the description.
    assert second["wide_runs"] == "canonical", second["wide_runs"]
    assert twin_exit == 0
    assert real_exit == 0
    for cell in written:
        if cell:
            assert cell == f"{int(float(cell))}", cell
    # ...AND THE CHECK CAN FAIL, which is the half that makes the rest
    # worth asserting. The same description, a file respelled into the
    # neighbours, and the subcheck names itself.
    respelled = [_a_value_preserving_neighbour(cell) for cell in cells]
    for before, after in zip(cells, respelled):
        assert float(before) == float(after)
    folder = tmp_path / "wide"
    bad = folder / "respelled.csv"
    bad.write_text(
        fixtures.rows_to_csv(["record_id"], [[cell] for cell in respelled]),
        encoding="utf-8",
        newline="",
    )
    checked = folder / "check-respelled"
    checked.mkdir()
    code = _exit_of(
        [
            "validate",
            str(folder / "real-profile.json"),
            "--twin",
            str(bad),
            "--out-dir",
            str(checked),
            "--replace",
        ]
    )
    assert code == 3, code
    missed: "list[str]" = []
    for report in checked.glob("*.txt"):
        for line in report.read_text(encoding="utf-8").splitlines():
            if "MISSED" in line:
                missed += [line.strip()]
    assert any("styles.canonical.wide" in line for line in missed), missed


def test_a_real_export_that_respells_its_wide_keys_is_not_accused(
    tmp_path: pathlib.Path,
) -> None:
    """The false accusation plan P4-D66.2 ended, kept ended (plan P4-D90).

    A real export of literal seventeen-figure identifiers writes runs
    that are NOT their values' canonical text -- measured, 690 of 800
    cells at one seed. A ceiling of nought asked of every column would
    fail that file on two-thirds of its cells, which is exactly the
    accusation the ceiling must not make. The column publishes
    `respelled`, the obligation is LISTED rather than checked, and the
    file meets its own description.
    """
    draw = _numbers(101)
    cells: "list[str]" = []
    for _step in range(800):
        cells += [f"{draw.randrange(10 ** 16, 10 ** 17)}"]
    odd = 0
    for cell in cells:
        if cell != f"{int(float(cell))}":
            odd += 1
    # The shape: this really is an export whose runs are not canonical.
    assert odd > 400, odd
    first, second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "literal", cells, (), True, seed="1", header="record_id"
    )
    assert first["wide_runs"] == "respelled", first["wide_runs"]
    assert twin_exit == 0
    assert real_exit == 0
    assert "numeric.wide_runs" not in _only_the_marks_missed(
        tmp_path / "literal"
    )
    assert second["wide_runs"] == "canonical", second["wide_runs"]


def _wide_lines_of_the_real_report(folder: pathlib.Path) -> "list[str]":
    """Every line of the REAL table's quality report naming the wide ceiling.

    `_only_the_marks_missed` above reads the TWIN's report. These tests
    need the other one: the repair pass of landing 2b.13 (plan P4-D91)
    is about a REAL table being accused, and an exit code alone would
    not say which obligation accused it.
    """
    lines: "list[str]" = []
    for report in sorted((folder / "check-real").glob("*.txt")):
        for line in report.read_text(encoding="utf-8").splitlines():
            if "styles.canonical.wide" in line:
                lines += [line.strip()]
    return lines


def _grouped_figures(text: str) -> str:
    """A run of figures with a comma between its thousands."""
    out = ""
    place = 0
    for character in reversed(text):
        if place > 0 and place % 3 == 0:
            out = "," + out
        out = character + out
        place += 1
    return out


WIDE_DRESSES = (
    ("grouped", _grouped_figures, "plain"),
    ("space_padded", lambda text: " " + text, "plain"),
    ("leading_plus", lambda text: "+" + text, "leading_plus"),
)


@pytest.mark.parametrize("notation", ["brackets", "minus_sign", "one_space"])
def test_a_real_export_whose_wide_keys_wear_a_sign_or_a_space_is_not_accused(
    notation: str, tmp_path: pathlib.Path
) -> None:
    """The false accusation P4-D66.2 ended, restored and ended again (P4-D91).

    Landing 2b.13 published `wide_runs` from the RAW cell text while the
    ceiling recounted the NORMALISED text, so the two disagreed about
    every spelling `number_core` takes off. A cell the producer left out
    of its word was a cell the checker counted, and the file was held to
    a ceiling of nought its own description never claimed.

    MEASURED ON THAT TREE, through the real command line at 800 rows:
    ONE cell of eight hundred given a leading space and respelled made
    the REAL table exit 3 on `styles.canonical.wide` while its twin
    exited 0; the bracketed and minus-signed columns below did the same
    with 388 and 392 cells moved. Each is a perfectly good export.
    """
    draw = _numbers(311)
    cells: "list[str]" = []
    moved = 0
    for step in range(800):
        figures = f"{int(float(draw.randrange(10 ** 16, 10 ** 17)))}"
        if notation == "one_space":
            cells += [figures]
            continue
        if step % 2 == 0:
            cells += [figures]
            continue
        neighbour = _a_value_preserving_neighbour(figures)
        if neighbour != figures:
            moved += 1
        cells += [f"({neighbour})" if notation == "brackets" else "\u2212" + neighbour]
    if notation == "one_space":
        # The minimal case: ONE sloppy cell in eight hundred.
        neighbour = _a_value_preserving_neighbour(cells[417])
        assert neighbour != cells[417]
        cells[417] = " " + neighbour
        moved = 1
    # The shape, asserted before the answer: these really are wide runs
    # written in a notation the raw-text test refused.
    assert moved > 0, moved
    first, second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "worn", cells, (), True, seed="1", header="ledger_key"
    )
    assert first["n_present"] == 800, first["n_present"]
    assert first["numeric_styles"] == {"plain": 800}, first["numeric_styles"]
    if notation != "one_space":
        assert first["negative_form"] == notation, first["negative_form"]
    # ...and the answer: the column says what it is, and NEITHER file is
    # accused. The word is `respelled` where a group of these cells are,
    # which is the true statement about this export -- and `canonical`
    # where ONE cell is (plan P4-D140, the final Codex review's first
    # BLOCKER): a word one cell can move tells the reader who knows every
    # other cell what that cell wrote, so the word moves at the census
    # floor, and the canonical ceiling tolerates fewer respelled runs
    # than that floor, which is what still keeps this real table
    # unaccused.
    expected = "canonical" if notation == "one_space" else "respelled"
    assert first["wide_runs"] == expected, first["wide_runs"]
    assert twin_exit == 0
    assert real_exit == 0
    held = [line for line in _wide_lines_of_the_real_report(tmp_path / "worn")
            if line.endswith(": MISSED")]
    assert held == [], held
    assert second["wide_runs"] == "canonical", second["wide_runs"]


@pytest.mark.parametrize("dress", WIDE_DRESSES, ids=[d[0] for d in WIDE_DRESSES])
def test_a_wide_column_that_groups_or_pads_its_keys_still_says_so(
    dress: "tuple[str, object, str]", tmp_path: pathlib.Path
) -> None:
    """A word that was false about its own file, and a check that slept (P4-D91).

    Where the raw-text class test refused a spelling, the column
    published `none` -- "fewer such cells than the floor" -- while
    holding eight hundred of them, and the ceiling was listed as having
    nothing to govern. MEASURED on that tree: 800 grouped wide keys with
    every one respelled (780 cells moved) published `none` and nothing
    saw it; 800 space-padded keys published `none` while the TWIN of the
    same column published `canonical`; 800 plus-signed keys, every one
    respelled, published `none`.

    So this asserts the word, and then asserts the ceiling CAN STILL
    FAIL on the same shape -- a word that is merely truthful would be
    worth nothing if the check beside it never fired.
    """
    _name, wear, form = dress
    figures = _wide_keys(313)
    cells = [wear(figure) for figure in figures]
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "dressed", cells, (), True, seed="1", header="record_id"
    )
    # The shape: the cells wear the spelling, and the form is the one
    # the class admits.
    assert first["n_present"] == 800, first["n_present"]
    assert first["numeric_styles"] == {form: 800}, first["numeric_styles"]
    # ...and the answer.
    assert first["wide_runs"] == "canonical", first["wide_runs"]
    assert second["wide_runs"] == "canonical", second["wide_runs"]
    assert twin_exit == 0
    assert real_exit == 0
    for cell in written:
        if not cell:
            continue
        # The figures this twin cell carries, with the dress taken off:
        # the marks, the surrounding space and the sign, which is what
        # `number_core` takes off before the form is read.
        bare = cell.strip()
        for mark in (",", " ", "+"):
            bare = bare.replace(mark, "")
        assert bare == f"{int(float(bare))}", cell
    # ...AND THE CHECK CAN FAIL. The same description, the same
    # spelling, every run respelled into its value-preserving neighbour.
    respelled = [wear(_a_value_preserving_neighbour(figure)) for figure in figures]
    moved = 0
    for before, after in zip(cells, respelled):
        if before != after:
            moved += 1
    assert moved > 700, moved
    folder = tmp_path / "dressed"
    bad = folder / "respelled.csv"
    bad.write_text(
        fixtures.rows_to_csv(["record_id"], [[cell] for cell in respelled]),
        encoding="utf-8",
        newline="",
    )
    checked = folder / "check-respelled"
    checked.mkdir()
    code = _exit_of(
        [
            "validate",
            str(folder / "real-profile.json"),
            "--twin",
            str(bad),
            "--out-dir",
            str(checked),
            "--replace",
        ]
    )
    assert code == 3, code
    missed: "list[str]" = []
    for report in checked.glob("*.txt"):
        for line in report.read_text(encoding="utf-8").splitlines():
            if "MISSED" in line:
                missed += [line.strip()]
    assert any("styles.canonical.wide" in line for line in missed), missed


@pytest.mark.parametrize("floor,word", [("11", "none"), ("1", "canonical")])
def test_the_wide_run_word_is_held_to_the_smallest_group_size(
    floor: str, word: str, tmp_path: pathlib.Path
) -> None:
    """The word names a FORM, so the floor holds it as NS1 holds its sibling.

    Five wide keys among 795 narrow ones: the forms map leaves the whole
    column as room, so nothing but the FLOOR can decide this, and the
    same column answers differently at eleven and at one. Landing
    2b.13's first version read no floor at all and published `canonical`
    at both.
    """
    draw = _numbers(317)
    cells: "list[str]" = []
    for _step in range(795):
        cells += [f"{draw.randrange(100, 9999)}"]
    for _step in range(5):
        cells += [f"{int(float(draw.randrange(10 ** 16, 10 ** 17)))}"]
    first, _second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "floored",
        cells,
        ("--smallest-group", floor),
        True,
        seed="1",
        header="record_id",
    )
    # The shape: the room is the whole column, so only the floor can bite.
    assert first["numeric_styles"] == {"plain": 800}, first["numeric_styles"]
    assert first["wide_runs"] == word, first["wide_runs"]
    assert twin_exit == 0
    assert real_exit == 0


def test_a_lone_wide_key_the_styles_floor_pooled_is_not_named_by_the_word(
    tmp_path: pathlib.Path,
) -> None:
    """The word must not say what the forms map pooled to avoid saying (P4-D91).

    One wide key beside 799 charge amounts at a floor of eleven: the
    publication floor pools the lone `plain` cell into `(withheld)`
    precisely so that no reader can tell what form it wore. Landing
    2b.13's first version then published `wide_runs: canonical` beside
    it and filed the ceiling as HELD, which tells the reader exactly
    what the pool was hiding.
    """
    draw = _numbers(319)
    cells: "list[str]" = []
    for _step in range(799):
        cells += [f"{draw.uniform(10, 9000):.2f}"]
    cells += [f"{int(float(draw.randrange(10 ** 16, 10 ** 17)))}"]
    first, _second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "pooled",
        cells,
        ("--smallest-group", "11"),
        True,
        seed="1",
        header="amount",
    )
    # The shape: the one cell is named nowhere -- since plan P4-D222
    # (stage 2 closed by the owner rulings of 2026-09-17) it is counted
    # into the decimals, where plan P4-D221 pooled the whole map with it.
    assert first["numeric_styles"] == {"decimal": 800}, first["numeric_styles"]
    # ...and the answer: the word says nothing about it, and the ceiling
    # is listed rather than held.
    assert first["wide_runs"] == "none", first["wide_runs"]
    # THE TWIN'S ONE MISS IS ITS MEAN, AND IT IS A TRUE ONE (validation
    # method V6.1-A2, the stage-2b integration). One value of 10**16
    # beside 799 amounts under 9,000 publishes a mean of about 3.7e13;
    # the construction's window for it runs from 6.9e13 to 2.8e14 and
    # the twin holds 1.5e14, four times the published mean. That used to
    # be WITHIN-BOUND. It is MISSED now, and nothing else is.
    missed = [
        line.strip()
        for line in (tmp_path / "pooled" / "check-twin" / "real-twin-quality.txt")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.rstrip().endswith(": MISSED")
    ]
    assert set(missed) <= {
        "moments.mean [numeric.mean]: MISSED",
        "moments.std [numeric.std]: MISSED",
    }, missed
    assert twin_exit in (0, 3)
    assert real_exit == 0
    for line in _wide_lines_of_the_real_report(tmp_path / "pooled"):
        assert not line.endswith(": HELD"), line


def test_no_stage_2_test_throws_away_what_the_command_returned() -> None:
    """`cli.main()` RETURNS its exit code, and a call that drops it tests nothing.

    Found by the stage 2 confirmation review: four helpers called it as a
    bare statement and fell through to success, so a validation that
    missed an obligation passed the gate test.
    """
    import ast

    folder = pathlib.Path(__file__).resolve().parent
    dropped = []
    for path in sorted(folder.glob("test_*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        # A call inside `with pytest.raises(...)` returns nothing to read:
        # it is expected to raise, and the block checks what it raised.
        expecting: "set[int]" = set()
        for block in ast.walk(tree):
            if not isinstance(block, ast.With):
                continue
            for item in block.items:
                context = item.context_expr
                if (
                    isinstance(context, ast.Call)
                    and isinstance(context.func, ast.Attribute)
                    and context.func.attr == "raises"
                ):
                    for inner in ast.walk(block):
                        expecting.add(id(inner))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Expr) or not isinstance(node.value, ast.Call):
                continue
            if id(node) in expecting:
                continue
            called = node.value.func
            if isinstance(called, ast.Attribute) and called.attr == "main":
                if isinstance(called.value, ast.Name) and called.value.id == "cli":
                    dropped += [f"{path.name}:{node.lineno}"]
    assert dropped == [], dropped

