"""A measurement's twin stays inside the real column's two ends on the route that writes the inside record (lane ZOO-Y, plan P4-D517).

The description publishes no end of a column whose outer rows are fewer
than its floor allows, so the twin draws its tails from the published
distances alone and passes the real column's end. MEASURED (lane ZOO-X's
data-type zoo, 20,000 rows, the floor on, the shipped route): a count
capped at 49 came back with a 55, and days to an event or to censoring
that stop at 1,500 came back with 1,714 -- a survival analysis meeting
days the study never watched. The inside record's marginals zone keeps
each number column's quantile function, its first and last points the
real least and greatest values, so `generation._inside_ranged` draws a
cell past either end again inside the real column's outer hundredth, at
the cell's own decimals. Only a published measurement (`count` or
`continuous`, not top-coded) is read: a code, an identifier, a held
column and an age stay as their own rules write them. The tables are
invented here.
"""

from __future__ import annotations

import pathlib
import random

import kpi_shapes
from synthtwin import generation, inside, twinstore


def _described(folder: pathlib.Path) -> "kpi_shapes.Described":
    draw = random.Random(11)
    lines = ["days,result,code"]
    for _row in range(1200):
        lines += [f"{min(int(draw.expovariate(1 / 300)) + 1, 900)},{draw.gauss(5, 1):.2f},{draw.choice(('A1', 'B2'))}"]
    return kpi_shapes.describe(folder, "ranged", "\n".join(lines) + "\n", 11, measured=["days", "result"])


def _zones(described: "kpi_shapes.Described") -> "dict[str, object]":
    import csv

    with described.table.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    columns = {name: [row[place] for row in rows[1:]] for place, name in enumerate(rows[0])}
    return inside.build_record(columns)["zones"]  # type: ignore[return-value]


def _held(cells: "list[str]") -> "twinstore.HeldColumn":
    return twinstore.held_column(cells)


def test_cells_past_the_real_ends_are_drawn_again_inside_them(tmp_path: pathlib.Path) -> None:
    """Two days past the real greatest (900) and one result under the real least: inside, at their own decimals."""
    described = _described(tmp_path)
    zones = _zones(described)
    real_days = zones["marginals"]["days"]["quantiles"]  # type: ignore[index]
    real_results = zones["marginals"]["result"]["quantiles"]  # type: ignore[index]
    days = ["12", "1714", "450", "955"] + ["300"] * 20
    results = ["4.50", f"{real_results[0] - 3:.2f}", "6.10"] + ["5.00"] * 21
    codes = ["A1"] * 24
    finished = [_held(days), _held(results), _held(codes)]
    changed = generation._inside_ranged(described.loaded, zones, finished, {"days": 0, "result": 1, "code": 2}, 0)
    assert changed == {"days", "result"}
    after_days = twinstore.column_cells(finished[0])
    after_results = twinstore.column_cells(finished[1])
    assert after_days[0] == "12" and after_days[2] == "450" and after_days[4:] == days[4:]
    for cell in (after_days[1], after_days[3]):
        assert "." not in cell and real_days[900] <= float(cell) <= real_days[-1], cell
    # Two spellings past the end take two new spellings, so the column's counts stand: the real days stop at 900,
    # every point of their outer hundredth is 900, and the second takes the free value nearest it.
    assert after_days[1] != after_days[3] and {after_days[1], after_days[3]} & {"900"}
    assert after_results[0] == "4.50" and after_results[2] == "6.10"
    assert len(after_results[1].split(".")[1]) == 2 and real_results[0] <= float(after_results[1]) <= real_results[10]
    assert twinstore.column_cells(finished[2]) == codes


def test_cells_inside_the_ends_and_other_roles_are_left_as_they_are(tmp_path: pathlib.Path) -> None:
    """Every cell inside the real ends: nothing moves; a column the marginals do not read as numbers is never read."""
    described = _described(tmp_path)
    zones = _zones(described)
    finished = [_held(["300"] * 24), _held(["5.00"] * 24), _held(["A1"] * 24)]
    assert generation._inside_ranged(described.loaded, zones, finished, {"days": 0, "result": 1, "code": 2}, 0) == set()
    marginals = dict(zones["marginals"])  # type: ignore[arg-type]
    marginals["days"] = dict(marginals["days"], kind="identifier")
    finished = [_held(["9999"] * 24), _held(["5.00"] * 24), _held(["A1"] * 24)]
    assert generation._inside_ranged(
        described.loaded, {"marginals": marginals}, finished, {"days": 0, "result": 1, "code": 2}, 0) == set()


def test_a_spelling_past_an_end_with_no_free_value_inside_stays(tmp_path: pathlib.Path) -> None:
    """Every whole value of the outer tenth held by a cell inside the ends: the cell past the end keeps its spelling."""
    described = _described(tmp_path)
    zones = _zones(described)
    real_days = zones["marginals"]["days"]["quantiles"]  # type: ignore[index]
    inner = [f"{day}" for day in range(int(real_days[900]), 901)]
    days = inner + ["1714"]
    finished = [_held(days), _held(["5.00"] * len(days)), _held(["A1"] * len(days))]
    generation._inside_ranged(described.loaded, zones, finished, {"days": 0, "result": 1, "code": 2}, 0)
    assert twinstore.column_cells(finished[0])[-1] == "1714"
    assert generation._free_inside([1.0] * 1001, True, 0, {1.0}, False) == ""
    ramp = [step / 200 for step in range(1001)]
    assert generation._free_inside(ramp, True, 1, {5.0}, True) == "+4.9"
    assert generation._free_inside(ramp, False, 1, {0.0}, False) == "0.1"


def test_the_draw_is_a_function_of_the_seed(tmp_path: pathlib.Path) -> None:
    """The days capped at 900 hold one value in their outer hundredth; the results' outer hundredth varies with the seed."""
    described = _described(tmp_path)
    zones = _zones(described)
    made = []
    for seed in (0, 0, 7):
        finished = [_held(["1714"] * 24), _held(["-9.99"] * 24), _held(["A1"] * 24)]
        generation._inside_ranged(described.loaded, zones, finished, {"days": 0, "result": 1, "code": 2}, seed)
        made += [twinstore.column_cells(finished[1])]
    assert made[0] == made[1] and made[0] != made[2]


def test_a_column_carrying_a_cap_or_published_key_by_key_is_never_moved(tmp_path: pathlib.Path) -> None:
    """A year cut, a key's own blocks, any cap or hold: the column stays as its own rules wrote it (batch 4z's fix round).

    The outside review of batch 4z, item 2, measured on the shipped route at
    20,000 rows: a keyed measurement column whose age key level is capped at
    90 had its 4,000 age cells (90, under the WHOLE column's real least
    value) written 100 by this pass, and a column of birth years pooled at
    the year cut wrote 1930 where the description writes 1937. Here the
    same days column, given each mark in turn, keeps the cells past its real
    ends that the plain column has drawn again.
    """
    import dataclasses

    described = _described(tmp_path)
    zones = _zones(described)
    places = {"days": 0, "result": 1, "code": 2}

    def ranged(profile: object) -> "list[str]":
        finished = [_held(["1714"] * 12 + ["300"] * 12), _held(["5.00"] * 24), _held(["A1"] * 24)]
        generation._inside_ranged(profile, zones, finished, places, 0)  # type: ignore[arg-type]
        return twinstore.column_cells(finished[0])

    assert ranged(described.loaded)[0] != "1714", "the plain column is drawn again inside its real end"
    days = next(column for column in described.loaded.columns if column.name == "days")
    pooled = next(column for column in described.loaded.columns if column.name == "code")
    for mark in ({"top_coded_year": 1937}, {"keyed_by": "code"}, {"key_blocks": (("A1", days),)},
                 {"top_coded_words": True}, {"computed_from": "result"}, {"key_pool": pooled},
                 {"present_count_withheld": True}, {"top_coded": 90}):
        marked = dataclasses.replace(days, **mark)  # type: ignore[arg-type]
        columns = tuple(marked if column.name == "days" else column for column in described.loaded.columns)
        profile = dataclasses.replace(described.loaded, columns=columns)
        assert ranged(profile)[:12] == ["1714"] * 12, mark
