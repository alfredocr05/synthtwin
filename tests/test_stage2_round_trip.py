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

from tests import fixtures

FACTS = (
    "role",
    "group_separator",
    "datetime_separators",
    "all_at_midnight",
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


def _round_trip(
    folder: pathlib.Path,
    cells: "list[str]",
    flags: "tuple[str, ...]" = (),
    check_real: bool = True,
    seed: str = "4",
    header: str = "value",
) -> "tuple[dict[str, object], dict[str, object], list[str], int, int]":
    """Describe, build, describe the twin; check the twin and the real table."""
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "real.csv"
    table.write_text(
        fixtures.rows_to_csv([header], [[cell] for cell in cells]),
        encoding="utf-8",
        newline="",
    )
    described = ["profile", str(table), "--out-dir", str(folder), "--replace"]
    assert _exit_of(described + list(flags)) == 0
    profile = folder / "real-profile.json"
    assert _exit_of(
        ["generate", str(profile), "--out-dir", str(folder), "--seed", seed, "--replace"]
    ) == 0
    twin = folder / "real-twin.csv"
    again = folder / "again"
    again.mkdir()
    copied = again / "twin.csv"
    copied.write_bytes(twin.read_bytes())
    redescribed = ["profile", str(copied), "--out-dir", str(again), "--replace"]
    assert _exit_of(redescribed + list(flags)) == 0
    first = json.loads(profile.read_text(encoding="utf-8"))["columns"][0]
    second = json.loads(
        (again / "twin-profile.json").read_text(encoding="utf-8")
    )["columns"][0]
    written = [
        row[0]
        for row in csv.reader(io.StringIO(twin.read_text(encoding="utf-8")))
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


def test_a_mark_held_by_too_few_values_is_written_with_the_commonest(
    tmp_path: pathlib.Path,
) -> None:
    """By design the pooled marks do not come back: the report says so."""
    cells = _moments(200, " ", 31) + _moments(34, "T", 32) + _moments(6, "t", 33)
    first, second, written, twin_exit, _real = _round_trip(
        tmp_path / "pooled", cells, ("--smallest-group", "30"), False
    )
    assert first["datetime_separators"] == {"(withheld)": 6, "space": 200, "upper_t": 34}
    assert second["datetime_separators"] == {"space": 206, "upper_t": 34}
    report = (tmp_path / "pooled" / "real-twin-report.txt").read_text(encoding="utf-8")
    assert "datetime_separators" in report
    assert twin_exit == 0


def test_a_column_of_dates_and_midnight_moments_is_written_as_moments(
    tmp_path: pathlib.Path,
) -> None:
    """Every value stays at midnight; the bare dates gain a midnight clock (carried)."""
    cells = _days(120, "", 41) + _days(120, " 00:00:00", 42)
    first, second, written, twin_exit, _real = _round_trip(
        tmp_path / "mixed", cells, (), False
    )
    assert first["format"] == "iso-mixed" and first["all_at_midnight"] is True
    assert second["format"] == "iso-datetime"
    assert all(len(cell) == 19 and cell.endswith(" 00:00:00") for cell in written)
    assert twin_exit == 0


def test_a_value_on_a_day_declared_absent_is_given_another_mark_and_named(
    tmp_path: pathlib.Path,
) -> None:
    """The source's own spelling of that day reads as absent, so it cannot be kept.

    At seed 0 the twin places values on that day (the stage 2 closure
    review measured seed 4 placed none, so the first version of this test
    exercised nothing): they are written with another mark, the census
    falls short, and the report names it.
    """
    cells = _days(220, " 00:00:00", 51) + ["2025-06-01 00:00:00"] * 20
    first, second, written, twin_exit, _real = _round_trip(
        tmp_path / "declared",
        cells,
        ("--missing-value", "2025-06-01 00:00:00"),
        False,
        seed="0",
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
    assert twin_exit == 0


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
    assert twin_exit == 0


def test_labels_beside_decimal_comma_numbers_stay_labels(tmp_path: pathlib.Path) -> None:
    """The review's reproduction: `1,234,567` beside `2.397,25` is a label, and stays one."""
    numbers = [
        f"{1200.25 + 97 * place:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
        for place in range(40)
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
    cells = [f"{-1000000 + 25 * place:,}".replace(",", ".") for place in range(41)]
    cells += ["-999,000"] * 10
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
    first, second, _written, _twin_exit, _real = _round_trip(
        tmp_path / "small", cells, ("--smallest-group", "2"), False
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
    first, second, _written, twin_exit, _real = _round_trip(
        tmp_path / "case",
        cells,
        ("--missing-value", "2025-01-01t00:00:00"),
        False,
        seed=seed,
    )
    assert (first["role"], first["n_distinct"], first["n_distinct_folded"]) == (
        "datetime", 4, 3
    )
    assert second["role"] == "datetime", second["role"]
    assert isinstance(second["n_distinct_folded"], int)
    assert second["n_distinct_folded"] >= 3
    assert twin_exit == 0
    report = (tmp_path / "case" / "real-twin-report.txt").read_text(encoding="utf-8")
    assert "datetime_separators" in report


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
    first, second, written, twin_exit, _real = _round_trip(
        tmp_path / "absent-day", cells, flags, True, seed=seed
    )
    assert second["n_present"] == first["n_present"] == 60
    assert second["n_missing"] == first["n_missing"] == 15
    assert twin_exit == 0
    present = [cell for cell in written if cell and not cell.startswith("2025-01-02")]
    assert len(present) == 60


def test_a_column_of_dates_that_collapses_to_two_days_is_named(
    tmp_path: pathlib.Path,
) -> None:
    """A twin read back as a column of two values says so (confirmation review)."""
    cells = ["2025-01-01"] * 10 + ["2025-01-02", "2025-01-03"]
    first, second, _written, _twin_exit, _real = _round_trip(
        tmp_path / "days", cells, (), False, seed="0"
    )
    assert first["role"] == "datetime"
    report = (tmp_path / "days" / "real-twin-report.txt").read_text(encoding="utf-8")
    if second["role"] != "datetime":
        assert "n_distinct_folded" in report


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

