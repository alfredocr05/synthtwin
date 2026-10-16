"""The analyst battery's own guarantees: its controls can fail, and it scores only what it says (plan P4-D398).

A check that cannot fail is a defect (CLAUDE.md, "Built-in
validation"). The battery's KPIs carry `controls_hold`, and a run whose
controls do not behave as controls is void; these tests show the
mechanism biting rather than assume it:

* a run whose shuffled twin is really a fresh replicate, or whose
  replicate is really a shuffle, is void on every KPI that reads them;
* the half split is a partition, and on ST2 it never splits a subject;
* the shuffled twin keeps every column's cells, as written, and only
  their order changes;
* an estimate whose smallest defining cell is under 22 rows is never
  scored, whatever its value;
* the report reading finds a block of family lines where one exists, so
  K-BC-11's "no line exists" is a reading and not a constant.

ST2 at 1,500 rows keeps the whole file to a few seconds.
"""

from __future__ import annotations

import dataclasses
import math
import pathlib

import pytest

import analyst_battery as B
import analyst_tables as T


@pytest.fixture(scope="module")
def small_run(tmp_path_factory: pytest.TempPathFactory) -> B.TableRun:
    """ST2 at 1,500 rows, seed 1, today's twin at seed 0, both controls."""
    return B.run_table("ST2", 1500, 1, (0,), "fast", tmp_path_factory.mktemp("battery-small"))


def _swapped(run: B.TableRun, side: str, by: str) -> B.TableRun:
    sides = dict(run.sides)
    sides[side] = run.sides[by]
    return dataclasses.replace(run, sides=sides)


def test_a_run_whose_controls_are_swapped_is_void(small_run: B.TableRun) -> None:
    """The shuffled twin replaced by the replicate, or the replicate by the shuffle: controls_hold is false."""
    assert B.kpi_01([small_run])["controls_hold"] is True
    assert B.kpi_06([small_run])["controls_hold"] is True
    for side, by in (("shuffled", "replicate"), ("replicate", "shuffled")):
        broken = _swapped(small_run, side, by)
        assert B.kpi_01([broken])["controls_hold"] is False, (side, by)
        assert B.kpi_06([broken])["controls_hold"] is False, (side, by)
        assert B.controls_failing(B.kpi_values([broken])), (side, by)


def test_the_replicate_control_is_a_binomial_bound_under_the_fresh_share() -> None:
    """At many estimates a share far under 77 % fails; at few, only a share under 30 % does."""
    assert B.replicate_holds(0.77, 400) and not B.replicate_holds(0.60, 400)
    assert B.replicate_holds(0.40, 8) and not B.replicate_holds(0.25, 8)
    assert not B.replicate_holds(math.nan, 100) and not B.replicate_holds(0.9, 0)


def test_the_half_split_is_a_partition_and_keeps_a_subject_whole() -> None:
    """Each split puts every row in exactly one half; on ST2 a subject's rows share a half."""
    view = B.read(T.text("ST2", 1500, 1), "ST2")
    groups = B.groups_of(view, "ST2", 1)
    sid = view.text("sid")
    for s in range(4):
        a, b = B.split(groups, s)
        assert sorted(a + b) == list(range(view.rows)) and not set(a) & set(b)
        half_of: "dict[str | None, int]" = {}
        for i in a:
            half_of[sid[i]] = 0
        assert all(sid[i] not in half_of for i in b)
    flat = B.groups_of(B.read(T.text("ST1", 600, 1), "ST1"), "ST1", 1)
    assert len(set(flat)) == 16


def test_the_shuffled_twin_keeps_every_column_s_cells() -> None:
    """Every column holds the same cells, as written; the rows are not the table's rows."""
    text = T.text("ST1", 800, 3)
    shuffled = B.shuffled_text(text, 9)
    columns = [sorted(c) for c in zip(*(line.split(",") for line in text.splitlines()))]
    again = [sorted(c) for c in zip(*(line.split(",") for line in shuffled.splitlines()))]
    assert columns == again
    assert sum(a == b for a, b in zip(text.splitlines()[1:], shuffled.splitlines()[1:])) < 10


def test_an_estimate_under_the_support_floor_is_never_scored(tmp_path: pathlib.Path) -> None:
    """A rate over 21 rows is left out of the yardstick however its halves agree; at 22 it is scored."""
    rows = [{"x": float(i < 21), "y": float(i % 2)} for i in range(400)]
    import pandas

    view = B.View(pandas.DataFrame(rows), "made up")

    def rates(v: B.View) -> "list[B.Estimate]":
        x, y = v.num("x"), v.num("y")
        out = B.rate("few", "F1", y, [a == 1.0 for a in x])
        return out + [dataclasses.replace(e, key="many", support=22) for e in out]

    y = B.yardstick([B.Analysis("rates", rates)], view, [i % 16 for i in range(400)])
    assert "few" not in y.h
    assert "many" in y.h


def test_the_report_reading_finds_family_lines_where_a_block_exists() -> None:
    """A block under the heading is read line by line; no heading, no block; carried means not 'not carried'."""
    report = "\n".join([
        "Something before.", "", B.REPORT_HEADING + ":",
        "F1 subgroup rates: carried", "F6 time to event: not carried (method)",
        "F10 your code runs: approximate", "", "after"])
    reading = B.report_reading(report)
    assert reading == {"block": True, "named": ["F1", "F6", "F10"], "carried": ["F1"]}
    assert B.report_reading("no block here") == {"block": False, "named": [], "carried": []}
    assert B.kpi_11([]) == {"families_unnamed": 10, "overclaims": 0, "report_block": False}


def test_a_value_the_ledger_cannot_hold_is_written_as_none() -> None:
    """NaN and the infinities become None, at any depth; other values stand."""
    assert B.finite({"a": math.nan, "b": {"c": math.inf}, "d": 1.5, "e": True}) == {
        "a": None, "b": {"c": None}, "d": 1.5, "e": True}
