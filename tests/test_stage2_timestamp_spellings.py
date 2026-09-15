"""Landing 2b.3's gate: every way a timestamp is spelled survives.

The stage 2 gate, held literally, for the spellings stage 2 did not
reach: each shape is described, built, the TWIN IS DESCRIBED AGAIN under
the same declarations, and the facts the landing publishes or reads by
must come back; the twin and the real table must both meet the
description with nothing missed. The fact itself is asserted -- the
number of `t` marks, of bare dates, of values at midnight -- and never merely
that one exists.

The shapes are the commonest real ones first, at hundreds to a few
thousand rows and on several seeds:

- a stamp with a rare mark held back at a raised floor, and a slashed
  stamp whose every mark is held back (the withheld pool, T1);
- dates stored bare beside the same dates with a midnight clock, and a
  warehouse export writing bare dates beside `T00:00:00Z` (owner decision
  4 narrowed, C);
- a column only partly at midnight, one stray time among values at midnight, and a
  CET/CEST export at local midnight on two offsets (E);
- a spelling one column's placeholder pass judged absent while another
  column keeps it as a value (L);
- the year-first slashed stamp `2024/03/17 14:05`, which was read as free
  text;
- and the validator's new checks, each shown able to fail (I).

Every table is built by seeded neutral code at runtime (plan D13).
"""

import csv
import datetime
import io
import json
import pathlib
import random
import typing

import pytest

from synthtwin import contract, generation, validation
from tests import fixtures
from tests.test_stage2_round_trip import _exit_of, _round_trip


def _minutes(count: int, mark: str, seed: int, days: int = 280) -> "list[str]":
    """Moments to the minute, never at midnight, written with one mark."""
    draw = random.Random(seed)
    start = datetime.datetime(2025, 3, 1)
    cells = []
    for _ in range(count):
        moment = start + datetime.timedelta(
            days=draw.randrange(0, days), minutes=draw.randrange(1, 1440)
        )
        cells += [moment.strftime(f"%Y-%m-%d{mark}%H:%M")]
    return cells


def _days(count: int, suffix: str, seed: int, days: int = 700) -> "list[str]":
    draw = random.Random(seed)
    start = datetime.date(2024, 1, 1)
    return [
        (start + datetime.timedelta(days=draw.randrange(0, days))).isoformat() + suffix
        for _ in range(count)
    ]


def _shuffled(cells: "list[str]", seed: int) -> "list[str]":
    cells = list(cells)
    random.Random(seed).shuffle(cells)
    return cells


def _marks(written: "list[str]") -> "dict[str, int]":
    counted: "dict[str, int]" = {}
    for cell in written:
        if len(cell) > 10:
            counted[cell[10]] = counted.get(cell[10], 0) + 1
    return counted


def _at_midnight(cell: str) -> bool:
    """A written cell names midnight: a bare date, or a clock of zeros."""
    if len(cell) == 10:
        return True
    clock = cell[11:].split("+")[0].split("-")[0].rstrip("Z")
    return set(clock.replace(":", "").replace(".", "")) <= {"0"}


def _table(
    folder: pathlib.Path,
    header: "list[str]",
    rows: "list[list[str]]",
    flags: "tuple[str, ...]",
    seed: str,
) -> "tuple[list[dict], list[dict], list[list[str]], int, int]":
    """The round trip over a table of several columns."""
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "real.csv"
    table.write_text(fixtures.rows_to_csv(header, rows), encoding="utf-8", newline="")
    assert _exit_of(["profile", str(table), "--out-dir", str(folder), "--replace"] + list(flags)) == 0
    profile = folder / "real-profile.json"
    assert _exit_of(
        ["generate", str(profile), "--out-dir", str(folder), "--seed", seed, "--replace"]
    ) == 0
    twin = folder / "real-twin.csv"
    again = folder / "again"
    again.mkdir()
    (again / "twin.csv").write_bytes(twin.read_bytes())
    assert _exit_of(
        ["profile", str(again / "twin.csv"), "--out-dir", str(again), "--replace"] + list(flags)
    ) == 0
    first = json.loads(profile.read_text(encoding="utf-8"))["columns"]
    second = json.loads((again / "twin-profile.json").read_text(encoding="utf-8"))["columns"]
    written = list(csv.reader(io.StringIO(twin.read_text(encoding="utf-8"))))[1:]
    (folder / "check-twin").mkdir()
    twin_exit = _exit_of(
        ["validate", str(profile), "--twin", str(twin), "--out-dir", str(folder / "check-twin"), "--replace"]
    )
    (folder / "check-real").mkdir()
    real_exit = _exit_of(
        ["validate", str(profile), "--twin", str(table), "--out-dir", str(folder / "check-real"), "--replace"]
    )
    return first, second, written, twin_exit, real_exit


def _validate(profile: pathlib.Path, cells: "list[str]", folder: pathlib.Path) -> "tuple[int, str]":
    """Validate a hand-made file against a description; the code and the report."""
    folder.mkdir(parents=True, exist_ok=True)
    made = folder / "made.csv"
    made.write_text(
        fixtures.rows_to_csv(["value"], [[cell] for cell in cells]), encoding="utf-8", newline=""
    )
    code = _exit_of(
        ["validate", str(profile), "--twin", str(made), "--out-dir", str(folder), "--replace"]
    )
    return code, (folder / "made-quality.txt").read_text(encoding="utf-8")


# -- T1: the withheld pool is written with the marks the census leaves unnamed


@pytest.mark.parametrize("seed", ["0", "4", "31"])
def test_a_rare_lower_case_t_held_back_comes_back(tmp_path: pathlib.Path, seed: str) -> None:
    """870 `T`, 22 spaces and 8 `t` at a floor of 20: the 8 were the `t`."""
    cells = _shuffled(_minutes(870, "T", 1) + _minutes(22, " ", 2) + _minutes(8, "t", 3), 5)
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "rare-t", cells, ("--smallest-group", "20"), True, seed
    )
    assert first["datetime_separators"] == {"(withheld)": 8, "space": 22, "upper_t": 870}
    assert second["datetime_separators"] == first["datetime_separators"]
    assert _marks(written) == {"T": 870, " ": 22, "t": 8}
    assert (twin_exit, real_exit) == (0, 0)


@pytest.mark.parametrize("seed", ["0", "4"])
def test_a_pool_over_two_unnamed_marks_is_split_evenly(tmp_path: pathlib.Path, seed: str) -> None:
    """880 `T` beside 12 spaces and 8 `t`, both held back: ten of each come back."""
    cells = _shuffled(_minutes(880, "T", 1) + _minutes(12, " ", 2) + _minutes(8, "t", 3), 5)
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "two-pooled", cells, ("--smallest-group", "20"), True, seed
    )
    assert first["datetime_separators"] == {"(withheld)": 20, "upper_t": 880}
    assert second["datetime_separators"] == first["datetime_separators"]
    assert _marks(written) == {"T": 880, " ": 10, "t": 10}
    assert (twin_exit, real_exit) == (0, 0)


@pytest.mark.parametrize("seed", ["0", "9"])
def test_a_slashed_stamp_whose_every_mark_is_held_back_keeps_its_space(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """The only mark a slashed stamp's reader takes is a space, so the twin writes one."""
    draw = random.Random(3)
    cells = [
        (datetime.datetime(2023, 1, 1) + datetime.timedelta(minutes=draw.randrange(0, 900000))).strftime(
            "%m/%d/%Y %H:%M"
        )
        for _ in range(600)
    ]
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "slashed-pool", cells, ("--smallest-group", "700"), True, seed
    )
    assert first["datetime_separators"] == {"(withheld)": 600}
    assert _marks(written) == {" ": 600}
    assert second["datetime_separators"] == first["datetime_separators"]
    assert (twin_exit, real_exit) == (0, 0)


def test_two_days_and_a_pooled_spelling_keep_the_kind_but_not_the_count(
    tmp_path: pathlib.Path,
) -> None:
    """DESIGNED NOT TO RETURN, pinned so a change to it is a visible decision.

    Sixty and sixty values at midnight on two days beside five `T` spellings of the
    first day, at a floor of 11. The pool is written with the marks the
    census leaves unnamed, and marks are given to ranks without regard to
    value, so the pooled spellings land on both days: the column keeps
    its kind -- it no longer reads back as a column of two values -- but
    holds five different spellings where the real table held three. The
    named count moves, and nothing says it moves except the distinct-count
    window of the quality report.
    """
    cells = ["2025-01-01 00:00:00"] * 60 + ["2025-01-02 00:00:00"] * 60 + ["2025-01-01T00:00:00"] * 5
    first, second, _written, twin_exit, _real = _round_trip(
        tmp_path / "two-days", _shuffled(cells, 1), ("--smallest-group", "11"), False, "0"
    )
    assert (first["role"], first["n_distinct"], first["n_distinct_folded"]) == ("datetime", 3, 3)
    assert second["role"] == "datetime"
    assert (second["n_distinct"], second["n_distinct_folded"]) == (5, 4)
    assert twin_exit == 0


# -- C: a column mixing bare dates with midnight moments keeps both forms


@pytest.mark.parametrize(
    "rows, bare, suffix, seed",
    [
        (400, 280, " 00:00:00", "0"),
        (400, 280, " 00:00:00", "1"),
        (2000, 1900, " 00:00:00", "0"),
        (800, 600, "T00:00:00", "1"),
        (1500, 900, " 00:00", "4"),
    ],
)
def test_bare_dates_beside_midnight_moments_come_back_as_both(
    tmp_path: pathlib.Path, rows: int, bare: int, suffix: str, seed: str
) -> None:
    """Every bare-date rank is written bare, every other at midnight, at the published counts."""
    cells = _shuffled(_days(bare, "", 1) + _days(rows - bare, suffix, 2), 3)
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "mixed", cells, (), True, seed
    )
    assert first["format"] == "iso-mixed" and first["all_at_midnight"] is True
    for key in ("format", "resolution_mix", "datetime_separators", "all_at_midnight", "n_at_midnight", "time_precision"):
        assert second[key] == first[key], (key, first[key], second[key])
    assert sum(1 for cell in written if len(cell) == 10) == bare
    assert all(_at_midnight(cell) for cell in written)
    assert (twin_exit, real_exit) == (0, 0)


@pytest.mark.parametrize("seed", ["1", "2"])
def test_bare_dates_beside_utc_midnight_moments_keep_their_forms_and_their_offsets(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """The warehouse export: date-only fields bare, datetime fields `T00:00:00Z`."""
    cells = _shuffled(_days(490, "", 4) + _days(210, "T00:00:00Z", 5), 6)
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "bare-z", cells, (), True, seed
    )
    assert first["datetimes_read_at"] == "utc" and first["all_at_midnight"] is True
    for key in ("format", "resolution_mix", "utc_offsets", "datetime_separators", "all_at_midnight", "n_at_midnight"):
        assert second[key] == first[key], (key, first[key], second[key])
    assert sum(1 for cell in written if len(cell) == 10) == 490
    assert sum(1 for cell in written if cell.endswith("T00:00:00Z")) == 210
    assert second["date_percentiles"] == first["date_percentiles"]
    assert (twin_exit, real_exit) == (0, 0)


# -- E: a column partly at midnight, and midnight on two offsets


def _partly(count: int, share: float, seed: int, days: int = 700, form: str = "%Y-%m-%d %H:%M:%S") -> "list[str]":
    draw = random.Random(seed)
    start = datetime.datetime(2024, 1, 1)
    cells = []
    for _ in range(count):
        moment = start + datetime.timedelta(days=draw.randrange(0, days))
        if draw.random() >= share:
            moment = moment + datetime.timedelta(minutes=draw.randrange(1, 1440))
        cells += [moment.strftime(form)]
    return cells


@pytest.mark.parametrize(
    "cells_of, seed",
    [
        (lambda: _partly(400, 0.9, 1), "0"),
        (lambda: _partly(400, 0.9, 1), "1"),
        (lambda: _partly(2000, 0.7, 2), "4"),
        (lambda: _partly(2000, 0.7, 21, days=30), "3"),
        (lambda: _partly(600, 191 / 600, 22, days=900, form="%Y-%m-%d %H:%M"), "7"),
        (lambda: _days(999, " 00:00:00", 3) + ["2024-05-05 14:30:00"], "5"),
    ],
    ids=["400-at-90", "400-at-90-seed1", "2000-at-70", "2000-over-30-days", "minutes", "one-stray-time"],
)
def test_a_column_partly_at_midnight_keeps_its_count_of_values_at_midnight(
    tmp_path: pathlib.Path, cells_of: object, seed: str
) -> None:
    """The published count of values at midnight is written, exactly, and read back."""
    cells = cells_of()  # type: ignore[operator]
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "partly", cells, (), True, seed
    )
    real = sum(1 for cell in cells if _at_midnight(cell))
    assert first["all_at_midnight"] is False
    assert first["n_at_midnight"] == real
    assert sum(1 for cell in written if _at_midnight(cell)) == real
    assert second["n_at_midnight"] == first["n_at_midnight"]
    # The rung ranks are written at their published rungs and no moved rank
    # passes one, so the ladder comes back exactly.
    assert second["date_percentiles"] == first["date_percentiles"]
    assert (twin_exit, real_exit) == (0, 0)


@pytest.mark.parametrize("seed", ["5", "9", "0"])
def test_a_cet_export_at_midnight_on_two_offsets_stays_at_local_midnight(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """Winter days at +01:00 and summer days at +02:00, every one a local midnight."""
    draw = random.Random(4)
    cells = []
    for _ in range(900):
        day = datetime.date(2023, 2, 1) + datetime.timedelta(days=draw.randrange(0, 900))
        offset = "+02:00" if 4 <= day.month <= 10 else "+01:00"
        cells += [f"{day.isoformat()}T00:00:00{offset}"]
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "cet", cells, (), True, seed
    )
    assert first["datetimes_read_at"] == "utc" and first["all_at_midnight"] is True
    for key in ("all_at_midnight", "n_at_midnight", "utc_offsets", "datetime_separators", "datetimes_read_at"):
        assert second[key] == first[key], (key, first[key], second[key])
    assert all(cell[11:19] == "00:00:00" for cell in written)
    # EVERY RUNG ON THE SHARED CLOCK, EXACTLY: each rung's rank is written
    # at its published instant and no rank passes one, so the twin read
    # again selects the same eleven instants. Counted in days, a rung
    # published at 23:00 was written on the day before, a day early.
    assert second["date_percentiles"] == first["date_percentiles"]
    assert (twin_exit, real_exit) == (0, 0)


# -- I: the marks and the values at midnight are obligations a file can miss


def _misses(report: str, fact: str) -> bool:
    return any("MISSED" in line and f"[{fact}]" in line for line in report.splitlines())


def test_a_space_column_rewritten_with_a_t_misses_its_marks(tmp_path: pathlib.Path) -> None:
    cells = [cell.replace("T", " ") for cell in _minutes(1200, "T", 11)]
    first, _second, written, twin_exit, real_exit = _round_trip(tmp_path / "space", cells, (), True, "11")
    assert first["datetime_separators"] == {"space": 1200}
    assert (twin_exit, real_exit) == (0, 0)
    code, report = _validate(
        tmp_path / "space" / "real-profile.json",
        [cell.replace(" ", "T") for cell in written],
        tmp_path / "rewritten",
    )
    assert code == 3
    assert _misses(report, "datetime.datetime_separators")


def test_a_midnight_column_moved_off_midnight_misses_the_statement(tmp_path: pathlib.Path) -> None:
    cells = _days(900, " 00:00:00", 12)
    _first, _second, written, twin_exit, real_exit = _round_trip(tmp_path / "midnight", cells, (), True, "11")
    assert (twin_exit, real_exit) == (0, 0)
    ordered = sorted(range(len(written)), key=lambda place: written[place])
    ends = {ordered[0], ordered[-1]}
    moved = [cell if place in ends else cell[:11] + "09:30:00" for place, cell in enumerate(written)]
    code, report = _validate(tmp_path / "midnight" / "real-profile.json", moved, tmp_path / "moved")
    assert code == 3
    assert _misses(report, "datetime.all_at_midnight")


def test_a_partly_midnight_column_moved_off_midnight_misses_the_count(tmp_path: pathlib.Path) -> None:
    cells = _partly(800, 0.6, 24, days=400)
    _first, _second, written, twin_exit, real_exit = _round_trip(tmp_path / "partly", cells, (), True, "3")
    assert (twin_exit, real_exit) == (0, 0)
    moved = [cell[:11] + "12:00:00" if _at_midnight(cell) else cell for cell in written]
    code, report = _validate(tmp_path / "partly" / "real-profile.json", moved, tmp_path / "moved")
    assert code == 3
    assert _misses(report, "datetime.n_at_midnight")


def test_a_pooled_mark_the_census_names_is_bounded_by_the_pool(tmp_path: pathlib.Path) -> None:
    """Writing the pooled `t` values with a mark the census does not name at all."""
    cells = _shuffled(_minutes(870, "T", 1) + _minutes(22, " ", 2) + _minutes(8, "t", 3), 5)
    _first, _second, written, twin_exit, _real = _round_trip(
        tmp_path / "pool", cells, ("--smallest-group", "20"), False, "0"
    )
    assert twin_exit == 0
    # Thirty values of the commonest mark given a lower-case t: more values
    # wear a mark the census leaves unnamed than the pool holds.
    changed = 0
    rewritten = []
    for cell in written:
        if len(cell) > 10 and cell[10] == "T" and changed < 30:
            cell = cell[:10] + "t" + cell[11:]
            changed += 1
        rewritten += [cell]
    code, report = _validate(tmp_path / "pool" / "real-profile.json", rewritten, tmp_path / "t-heavy")
    assert code == 3
    assert _misses(report, "datetime.datetime_separators")


# -- L: a judged spelling is one column's business; a declaration reaches the table


def _placeholder_rows(count: int, seed: int) -> "list[list[str]]":
    draw = random.Random(seed)
    rows = []
    for place in range(count):
        discharge = (
            "1900-01-01 00:00:00"
            if draw.random() < 0.02
            else (datetime.date(2018, 1, 1) + datetime.timedelta(days=draw.randrange(2000))).isoformat()
            + " 00:00:00"
        )
        birth = (
            "1900-01-01 00:00:00"
            if draw.random() < 0.15
            else (datetime.date(1895, 1, 1) + datetime.timedelta(days=draw.randrange(38000))).isoformat()
            + " 00:00:00"
        )
        rows += [[str(place), discharge, birth]]
    return rows


@pytest.mark.parametrize("seed", ["11", "12"])
def test_a_placeholder_judged_absent_in_one_column_stays_a_value_in_another(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """The birth column keeps its `1900-01-01 00:00:00` cells, and so does its twin."""
    first, second, written, twin_exit, real_exit = _table(
        tmp_path / "placeholder",
        ["id", "discharge", "birth"],
        _placeholder_rows(1500, 77),
        ("--identifier", "id"),
        seed,
    )
    assert first[1]["missing_by_source"] == {"1900-01-01 00:00:00": 21}
    assert first[2]["n_present"] == 1500 and first[2]["missing_by_source"] == {}
    assert second[2]["datetime_separators"] == first[2]["datetime_separators"] == {"space": 1500}
    assert sum(1 for row in written if "T" in row[2]) == 0
    report = (tmp_path / "placeholder" / "real-twin-report.txt").read_text(encoding="utf-8")
    assert "datetime_separators" not in report
    # The real table meets its own description: it failed 24 obligations
    # while the judged spelling was read as a declaration of the table.
    assert (twin_exit, real_exit) == (0, 0)


def test_a_declaration_sharing_a_day_with_a_judged_spelling_keeps_its_reach(
    tmp_path: pathlib.Path,
) -> None:
    """A person's own `--missing-value` is a declaration of the whole table.

    The column holds the declared `1900-01-01T00:00:00` and, beside it, a
    `1900-01-01 00:00:00` its placeholder pass judged absent. The judged
    test matches by the DAY, so it cannot tell the two keys apart; the
    column counts cells absent by declaration, so both keep their
    table-wide reach, and the declaration is never narrowed.
    """
    draw = random.Random(90)
    rows = []
    for place in range(1200):
        roll = draw.random()
        if roll < 0.03:
            first_cell = "1900-01-01T00:00:00"
        elif roll < 0.06:
            first_cell = "1900-01-01 00:00:00"
        else:
            first_cell = (datetime.date(2018, 1, 1) + datetime.timedelta(days=draw.randrange(2000))).isoformat() + "T00:00:00"
        second_cell = (datetime.date(1895, 1, 1) + datetime.timedelta(days=draw.randrange(38000))).isoformat() + "T00:00:00"
        rows += [[str(place), first_cell, second_cell]]
    folder = tmp_path / "declared"
    first, _second, written, twin_exit, real_exit = _table(
        folder, ["id", "a", "b"], rows,
        ("--identifier", "id", "--missing-value", "1900-01-01T00:00:00"), "1",
    )
    assert set(first[1]["missing_by_source"]) == {"1900-01-01 00:00:00", "1900-01-01T00:00:00"}
    described = contract.load_profile(str(folder / "real-profile.json"))
    assert "1900-01-01T00:00:00" in validation.declared_spellings(described)
    assert "1900-01-01T00:00:00" in generation._every_hole_spelling(described)
    assert sum(1 for row in written if row[2] == "1900-01-01T00:00:00") == 0
    assert (twin_exit, real_exit) == (0, 0)


@pytest.mark.parametrize("declared", ["nothing", "the-judged-spelling", "na"])
def test_both_writings_of_the_judged_rule_answer_alike(
    tmp_path: pathlib.Path, declared: str
) -> None:
    """The generator's rule and the validator's, key by key, on real descriptions.

    The validator may not import the generator (V1.4), so the rule that a
    judged spelling is one column's business is written twice; this walks
    both over every published hole spelling of a table with a judged
    placeholder, declared and not.
    """
    flags: "tuple[str, ...]" = ("--identifier", "id")
    rows = _placeholder_rows(1500, 77)
    if declared == "the-judged-spelling":
        flags = flags + ("--missing-value", "1900-01-01 00:00:00")
    if declared == "na":
        flags = flags + ("--missing-value", "NA")
        rows = _placeholder_rows_beside_na(1500, 79, " ")
    folder = tmp_path / "rule"
    folder.mkdir()
    table = folder / "real.csv"
    table.write_text(
        fixtures.rows_to_csv(["id", "discharge", "birth"], rows),
        encoding="utf-8",
        newline="",
    )
    assert _exit_of(["profile", str(table), "--out-dir", str(folder), "--replace"] + list(flags)) == 0
    described = contract.load_profile(str(folder / "real-profile.json"))
    asked = 0
    for column in described.columns:
        comma = generation._declared_a_decimal_comma(column, described)
        for spelling in sorted(column.missing_by_source):
            mine = generation._judged_here_alone(column, spelling, comma, described)
            theirs = validation._judged_here_alone(column, spelling, described)
            assert mine == theirs, (column.name, spelling)
            asked += 1
    assert asked >= 1
    judged = "1900-01-01 00:00:00" not in generation._every_hole_spelling(described)
    # Undeclared, or beside a declared `NA` sharing no day with it, the judged
    # spelling stays in its own column; declared itself, it reaches the table.
    assert judged is (declared != "the-judged-spelling")
    assert ("1900-01-01 00:00:00" in validation.declared_spellings(described)) is (not judged)


# -- the year-first slashed stamp is read as a moment


@pytest.mark.parametrize("form, precision, seed", [("%Y/%m/%d %H:%M", "minute", "2"), ("%Y/%m/%d %H:%M:%S", "second", "3")])
def test_a_year_first_slashed_stamp_is_a_column_of_moments(
    tmp_path: pathlib.Path, form: str, precision: str, seed: str
) -> None:
    """Read as `slashed-iso-datetime`; the twin writes ISO by owner decision 5."""
    draw = random.Random(2)
    cells = [
        (datetime.datetime(2022, 1, 1) + datetime.timedelta(seconds=draw.randrange(0, 800 * 86400))).strftime(form)
        for _ in range(500)
    ]
    first, second, written, twin_exit, real_exit = _round_trip(tmp_path / "slash", cells, (), True, seed)
    assert (first["role"], first["format"], first["time_precision"]) == ("datetime", "slashed-iso-datetime", precision)
    # The one fact designed not to return: the twin's cells are ISO.
    assert second["format"] == "iso-datetime"
    for key in ("role", "resolution", "time_precision", "datetime_separators", "n_present", "earliest", "latest"):
        assert second[key] == first[key], (key, first[key], second[key])
    assert all(cell[4] == "-" and cell[10] == " " for cell in written)
    assert (twin_exit, real_exit) == (0, 0)


# -- the repair pass of landing 2b.3: what its skeptic found


def _placeholder_rows_beside_na(count: int, seed: int, mark: str) -> "list[list[str]]":
    """A discharge column with a declared `NA` and a judged placeholder; a birth column keeping it."""
    draw = random.Random(seed)
    rows = []
    for place in range(count):
        roll = draw.random()
        if roll < 0.05:
            discharge = "NA"
        elif roll < 0.07:
            discharge = f"1900-01-01{mark}00:00:00"
        else:
            day = datetime.date(2018, 1, 1) + datetime.timedelta(days=draw.randrange(2000))
            discharge = f"{day.isoformat()}{mark}00:00:00"
        if draw.random() < 0.15:
            birth = f"1900-01-01{mark}00:00:00"
        else:
            day = datetime.date(1895, 1, 1) + datetime.timedelta(days=draw.randrange(38000))
            birth = f"{day.isoformat()}{mark}00:00:00"
        rows += [[str(place), discharge, birth]]
    return rows


@pytest.mark.parametrize("mark, seed", [(" ", "0"), (" ", "4"), ("T", "11")])
def test_a_judged_placeholder_beside_a_declared_na_stays_one_columns_business(
    tmp_path: pathlib.Path, mark: str, seed: str
) -> None:
    """The commonest declaration, `--missing-value NA`, held in the judging column too.

    The discharge column counts cells absent by declaration, and the rule
    that stopped there carried its judged `1900-01-01 00:00:00` to the whole
    table: the birth column's twin wrote 75 of its values with a `T` and the
    real table missed 12 obligations of its own description. The day's keys
    hold exactly the cells the verdict took, so nothing declared shares it.
    """
    first, second, written, twin_exit, real_exit = _table(
        tmp_path / "beside-na",
        ["id", "discharge", "birth"],
        _placeholder_rows_beside_na(1500, 79, mark),
        ("--identifier", "id", "--missing-value", "NA"),
        seed,
    )
    judged = f"1900-01-01{mark}00:00:00"
    assert set(first[1]["missing_by_source"]) == {"NA", judged}
    assert first[1]["missing_by_class"]["(declared-missing)"] == first[1]["missing_by_source"]["NA"]
    assert first[2]["n_present"] == 1500 and first[2]["missing_by_source"] == {}
    name = {" ": "space", "T": "upper_t"}[mark]
    assert second[2]["datetime_separators"] == first[2]["datetime_separators"] == {name: 1500}
    assert sum(1 for row in written if len(row[2]) > 10 and row[2][10] != mark) == 0
    assert (twin_exit, real_exit) == (0, 0)


def _bare_beside(
    count: int, share: float, seed: int, offset_of: "typing.Callable[[datetime.date], str]", days: int = 1000
) -> "list[str]":
    """Bare dates beside `T00:00:00` moments carrying a real offset, on the same days."""
    draw = random.Random(seed)
    start = datetime.date(2022, 1, 1)
    cells = []
    for _ in range(count):
        day = start + datetime.timedelta(days=draw.randrange(days))
        if draw.random() < share:
            cells += [day.isoformat()]
        else:
            cells += [f"{day.isoformat()}T00:00:00{offset_of(day)}"]
    return cells


def _cet(day: datetime.date) -> str:
    return "+02:00" if 4 <= day.month <= 10 else "+01:00"


@pytest.mark.parametrize(
    "cells_of, seed",
    [
        (lambda: _bare_beside(800, 0.5, 72, lambda day: "+02:00"), "0"),
        (lambda: _bare_beside(800, 0.5, 72, lambda day: "+02:00"), "4"),
        (lambda: _bare_beside(1200, 0.5, 52, _cet), "11"),
        (lambda: _bare_beside(2500, 0.3, 71, _cet), "4"),
        (lambda: _bare_beside(1000, 0.7, 73, lambda day: "-05:00"), "0"),
        (lambda: _bare_beside(900, 0.6, 93, lambda day: "+02:00", days=5), "4"),
    ],
    ids=["plus-two", "plus-two-seed-4", "cet", "cet-2500", "minus-five", "five-days"],
)
def test_bare_dates_beside_moments_at_local_midnight_on_a_real_offset_keep_their_ladder(
    tmp_path: pathlib.Path, cells_of: object, seed: str
) -> None:
    """A European or American warehouse export: date fields bare, datetime fields at local midnight.

    Its rungs are published on the shared clock at 22:00 or 05:00 where a
    moment stood there and at 00:00 where a bare date did. Every rung rank,
    and every rank between two rungs of one instant, takes the form and the
    offset its instant stands at midnight under; on 53bb012 the rungs came
    back 22 hours early and cells were written `T02:00:00+02:00`.
    """
    cells = cells_of()  # type: ignore[operator]
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "bare-offset", cells, (), True, seed
    )
    assert first["format"] == "iso-mixed" and first["datetimes_read_at"] == "utc"
    assert first["all_at_midnight"] is True
    for key in (
        "resolution_mix", "utc_offsets", "datetime_separators", "all_at_midnight", "n_at_midnight",
        "earliest", "latest", "earliest_utc_offset", "latest_utc_offset", "date_percentiles",
    ):
        assert second[key] == first[key], (key, first[key], second[key])
    assert sum(1 for cell in written if len(cell) == 10) == sum(1 for cell in cells if len(cell) == 10)
    assert all(_at_midnight(cell) for cell in written)
    assert (twin_exit, real_exit) == (0, 0)


def test_bare_dates_rewritten_with_a_clock_miss_the_marks(tmp_path: pathlib.Path) -> None:
    """1,900 bare dates beside 100 midnight moments with a space; the bare dates given a `T` or a `t`.

    The twin writes a column wholly at midnight with its bare dates bare, so
    a file writing them with a clock has 1,900 cells wearing a mark the
    census never names. The clock-writing cells beyond the published count
    widened the bound only where the twin itself writes whole dates with a
    clock, and that is not this column.
    """
    cells = _shuffled(_days(1900, "", 1) + _days(100, " 00:00:00", 2), 3)
    _first, _second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "bare", cells, (), True, "0"
    )
    assert (twin_exit, real_exit) == (0, 0)
    for mark in ("T", "t"):
        clocked = [f"{cell}{mark}00:00:00" if len(cell) == 10 else cell for cell in written]
        code, report = _validate(
            tmp_path / "bare" / "real-profile.json", clocked, tmp_path / f"clocked-{mark}"
        )
        assert code == 3
        assert _misses(report, "datetime.datetime_separators")


@pytest.mark.parametrize("seed", ["0", "4"])
def test_an_odd_pool_gives_its_remainder_to_the_space_before_the_lower_case_t(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """880 `T` beside 11 spaces and 10 `t`, both held back at a floor of 12: 11 and 10 come back."""
    cells = _shuffled(_minutes(880, "T", 1) + _minutes(11, " ", 2) + _minutes(10, "t", 3), 5)
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "odd-pool", cells, ("--smallest-group", "12"), True, seed
    )
    assert first["datetime_separators"] == {"(withheld)": 21, "upper_t": 880}
    assert second["datetime_separators"] == first["datetime_separators"]
    assert _marks(written) == {"T": 880, " ": 11, "t": 10}
    assert (twin_exit, real_exit) == (0, 0)


@pytest.mark.parametrize("days, seed", [(3, "0"), (6, "4")])
def test_a_pooled_mark_meeting_an_absent_spelling_keeps_a_mark_the_census_leaves_unnamed(
    tmp_path: pathlib.Path, days: int, seed: str
) -> None:
    """Midnight stamps with a `T` over a few days, eight with a `t`, and each day's spaced spelling declared absent.

    The pool's share given a space meets an absent spelling on every day.
    Offered the marks the allocation writes, it takes the `t` the census
    leaves unnamed and the pool comes back; offered only the named `T`, four
    of the eight became `T` and the twin described again named 884 `T`.
    """
    draw = random.Random(7)
    start = datetime.date(2024, 1, 1)

    def stamps(count: int, mark: str) -> "list[str]":
        return [
            f"{(start + datetime.timedelta(days=draw.randrange(days))).isoformat()}{mark}00:00:00"
            for _ in range(count)
        ]

    declared = [f"{(start + datetime.timedelta(days=day)).isoformat()} 00:00:00" for day in range(days)]
    holes: "list[str]" = []
    flags: "tuple[str, ...]" = ("--smallest-group", "20")
    for spelling in declared:
        holes += [spelling] * 25
        flags = flags + ("--missing-value", spelling)
    cells = _shuffled(stamps(880, "T") + stamps(12, " ") + stamps(8, "t") + holes, 6)
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "offer", cells, flags, True, seed
    )
    assert first["datetime_separators"] == {"(withheld)": 8, "upper_t": 880}
    assert second["datetime_separators"] == first["datetime_separators"]
    assert _marks([cell for cell in written if cell and cell not in declared]) == {"T": 880, "t": 8}
    assert (twin_exit, real_exit) == (0, 0)


@pytest.mark.parametrize("seed", ["4", "0"])
def test_a_column_with_no_value_at_midnight_gets_a_twin_with_none(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """Minute stamps none of which stands at midnight: `n_at_midnight` 0 comes back as 0.

    At a floor of one the nought says no value stood there, and a twin
    interpolated to the minute put one there by chance on seed 4, which read
    back as a count of 1.
    """
    cells = _minutes(1200, " ", 11)
    assert sum(1 for cell in cells if _at_midnight(cell)) == 0
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "none", cells, (), True, seed
    )
    assert first["n_at_midnight"] == 0
    assert sum(1 for cell in written if _at_midnight(cell)) == 0
    assert second["n_at_midnight"] == 0
    assert (twin_exit, real_exit) == (0, 0)
