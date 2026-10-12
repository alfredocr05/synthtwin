"""Lane J of stage 3b: the weekday and the hour of a timestamp, met together (plan P4-D379).

PLAN.md's row J asks that OR starts, admissions and the 10,000-row clinic, each publishing
a weekday census (landing 3b.D2, plan P4-D367) beside an hour census (landing 3b.2-H, plan
P4-D371), meet both. Batch 2b's integration found they need not: the hour pass keeps each
rank's day standing, and a rank the weekday pass left on its gap's end day, at a clock no
published hour reaches there, stayed off its hour. Its four columns -- five noon stamps a day
for 118 days, two clocks a day, D2's leap column and T2's review column of eleven 23:59:60 a
date -- missed the hour census at 4, 7, 5 and 10 seeds of 10 at the floor of 11, and the
review column its count of different values and its count at midnight as well; none did with
the weekday census withdrawn.

Method G7.3g step 3's ESCAPE PAID BACK: where a weekday census stands, a unit with no place
on a day of its standing takes one on the nearest day of another, while as many ranks of that
standing move by whole days onto days of its own, so every weekday count and every field of
their clocks is kept. Here, the seven columns at the floors of 11 and 36 and seeds 0 to 9:
both censuses published (T2's review column withholds its weekday census at 36), the source
and every twin missing nothing and filing no deviation; the round withdrawn, the integration's
four columns miss again, each said by a deviation; with one census alone, the round changes
no twin.
"""

from __future__ import annotations

import copy
import datetime
import random

import pytest

import fixtures
import kpi_shapes
from synthtwin import contract, generation, rendering

SEEDS = range(10)
FLOORS = (11, 36)

_YEAR = [datetime.date(2023, 1, 1) + datetime.timedelta(days=step) for step in range(365)]
_TWO_YEARS = [datetime.date(2023, 1, 1) + datetime.timedelta(days=step) for step in range(731)]


def _at(day: datetime.date, hours: int, minutes: int, seconds: int = 0) -> datetime.datetime:
    return datetime.datetime(day.year, day.month, day.day, hours, minutes, seconds)


def _weighted_days(draw: random.Random, span: "list[datetime.date]", weights: "tuple[float, ...]", rows: int) -> "list[datetime.date]":
    return draw.choices(span, weights=[weights[day.weekday()] for day in span], k=rows)


def _or_starts() -> "list[str]":
    """T2's OR starts: ten rooms at 07:30 on each of 100 weekdays, and one to three cases a
    room from 09:00 on five-minute slots (`tests/test_stage3b_hour.py`)."""
    draw = random.Random(71005)
    found: "list[str]" = []
    for day in [day for day in _TWO_YEARS if day.weekday() < 5][:100]:
        for _room in range(10):
            found += [_at(day, 7, 30).strftime("%m/%d/%Y %H:%M")]
            for _case in range(draw.randint(1, 3)):
                minutes = 9 * 60 + 5 * draw.randrange(96)
                found += [_at(day, minutes // 60, minutes % 60).strftime("%m/%d/%Y %H:%M")]
    return found


def _admissions() -> "list[str]":
    """D2's admissions: 1,000 over two years, Monday heaviest, to the second."""
    draw = random.Random(673)
    found: "list[str]" = []
    for day in _weighted_days(draw, _TWO_YEARS, (1.45, 1.2, 1.15, 1.1, 1.1, 0.55, 0.5), 1000):
        found += [_at(day, draw.randrange(24), draw.randrange(60), draw.randrange(60)).strftime("%Y-%m-%d %H:%M:%S")]
    return found


def _clinic() -> "list[str]":
    """D2's clinic at 10,000 rows: weekday appointments, 08:00 to 16:45, most on the quarter
    hour (`2023/03/17 09:30`)."""
    draw = random.Random(671)
    found: "list[str]" = []
    for day in _weighted_days(draw, _YEAR, (1.0, 1.2, 1.0, 1.1, 0.9, 0.0, 0.0), 10000):
        minute = draw.choice((0, 15, 30, 45)) if draw.random() < 0.8 else draw.randrange(60)
        found += [_at(day, draw.randrange(8, 17), minute).strftime("%Y/%m/%d %H:%M")]
    return found


def _stamps(first: datetime.date, days: int, clocks: "list[str]") -> "list[str]":
    """Each of `clocks` on each of `days` days from `first`."""
    found: "list[str]" = []
    for step in range(days):
        found += [f"{(first + datetime.timedelta(days=step)).isoformat()} {clock}" for clock in clocks]
    return found


COLUMNS = {
    "or_start": _or_starts,
    "admissions": _admissions,
    "clinic": _clinic,
    # The integration's four (batch 2b, 2026-10-12).
    "noon": lambda: _stamps(datetime.date(2024, 1, 1), 118, ["12:00:00"] * 5),
    "two_clocks": lambda: _stamps(datetime.date(2024, 1, 1), 90, ["08:00:00"] * 3 + ["20:30:00"] * 3),
    "leap": lambda: _stamps(datetime.date(2016, 12, 1), 118, ["12:00:00"] * 5) + ["2016-12-31 23:59:60"] * 50,
    "codex": lambda: _stamps(datetime.date(2024, 1, 1), 100, ["23:59:60"] * 11),
}
INTEGRATION = ("noon", "two_clocks", "leap", "codex")


@pytest.fixture(scope="module")
def described(tmp_path_factory: pytest.TempPathFactory) -> "dict[tuple[str, int], kpi_shapes.Described]":
    folder = tmp_path_factory.mktemp("joint")
    found: "dict[tuple[str, int], kpi_shapes.Described]" = {}
    for name, build in COLUMNS.items():
        text = name + "\n" + "\n".join(build()) + "\n"
        for floor in FLOORS:
            found[(name, floor)] = kpi_shapes.describe(folder / f"{name}-{floor}", name, text, floor)
    return found


def _one_census(table: kpi_shapes.Described, key: str) -> kpi_shapes.Described:
    """The description with one census, `key`, withdrawn, as a description withholding it reads."""
    document = copy.deepcopy(table.document)
    for column in document["columns"]:
        column[key] = []
    loaded = contract.load_profile(str(fixtures.write_profile(table.folder, f"without-{key}.json", document)))
    return kpi_shapes.Described(table.folder, table.table, document, loaded)


def _withdrawn(monkeypatch: pytest.MonkeyPatch) -> None:
    """G7.3g step 3 as it stood before lane J: no escape paid back."""
    monkeypatch.setattr(generation, "_clock_paid_escape", lambda *_args: None)


@pytest.mark.parametrize("floor", FLOORS)
@pytest.mark.parametrize("name", sorted(COLUMNS))
def test_both_censuses_are_met_together(described: "dict[tuple[str, int], kpi_shapes.Described]", name: str, floor: int) -> None:
    """Both censuses published, and the source and every twin at seeds 0 to 9 missing nothing
    and filing no deviation."""
    table = described[(name, floor)]
    block = table.block(name)
    assert block["hour_census"], (name, floor)
    assert bool(block["weekday_census"]) == ((name, floor) != ("codex", 36)), (name, floor)
    source = table.table.read_text(encoding="utf-8")
    assert kpi_shapes.missed(kpi_shapes.measure(table, source, "source.csv")) == []
    for seed in SEEDS:
        twin = generation.generate(table.loaded, seed)
        assert [deviation.fact for deviation in twin.deviations] == [], (name, floor, seed)
        written = rendering.twin_csv(twin)
        assert kpi_shapes.missed(kpi_shapes.measure(table, written, f"twin-{seed}.csv")) == [], (name, floor, seed)


@pytest.mark.parametrize("name", INTEGRATION)
def test_without_the_round_paid_back_the_integrations_columns_miss_and_say_so(
    described: "dict[tuple[str, int], kpi_shapes.Described]", name: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The mutant: the round withdrawn, each of the four columns at the floor of 11 has twins
    short of the hour census again, and each such twin files the deviation naming it."""
    table = described[(name, 11)]
    _withdrawn(monkeypatch)
    short: "list[int]" = []
    for seed in SEEDS:
        twin = generation.generate(table.loaded, seed)
        missed = kpi_shapes.missed(kpi_shapes.measure(table, rendering.twin_csv(twin), f"unpaid-{seed}.csv"))
        if f"{name}:hour_census.groups" in missed:
            short += [seed]
            assert "hour_census" in [deviation.fact for deviation in twin.deviations], (name, seed)
    assert short, name


@pytest.mark.parametrize("withdrawn", ("weekday_census", "hour_census"))
def test_with_one_census_alone_the_round_changes_no_twin(
    described: "dict[tuple[str, int], kpi_shapes.Described]", withdrawn: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """With either census withdrawn from the four columns' descriptions, every twin at seeds 0
    to 9 is byte for byte the twin the round withdrawn writes."""
    for name in INTEGRATION:
        table = _one_census(described[(name, 11)], withdrawn)
        with_round = [kpi_shapes.twin_text(table, seed) for seed in SEEDS]
        with monkeypatch.context() as patch:
            _withdrawn(patch)
            assert [kpi_shapes.twin_text(table, seed) for seed in SEEDS] == with_round, name
