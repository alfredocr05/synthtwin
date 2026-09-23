"""The tail rule of stage 3, measured on the shapes it was built for.

Landing 3.3 withholds every rung whose type-7 reading touches one of the
outermost max(`small_cell_floor`, 3) values of a column and publishes
what those rows look like as a GROUP instead (contract 6.7a, method
G5.3b to G5.3e). This file holds the four claims that made the landing
worth its cost, each over columns built at runtime from a fixed seed and
each measured through the product's own path -- the real reader, the
real producer, the strict loader, the real generator and the real
validator, with nothing stubbed:

* NOTHING PUBLISHED NAMES A LONE VALUE. No number in a description, a
  summary, a twin's report or a quality report equals one of the
  outermost values of the real column unless a group of at least the
  floor holds it. Measured before the rule, a description published 13
  to 46 such numbers per shape.
* THE FACTS DO NOT SOLVE FOR A WITHHELD END. The skeptic's own attack:
  the rows, the two distances, the grid and the sign counts leave more
  than one value possible for the end, so a reader who back-solves the
  lattice cannot recover it.
* AN ORDINAL SCALE KEEPS ITS OWN VALUES. On a bounded scale the tail is
  published by its values (G5.3e), so the twin writes the scale's own
  ends and no value the scale does not have -- a pain score of 0 to 10
  wrote 50 cells at 11 and none at 10 before the listed tail.
* AND THE TWIN STILL MEETS ITS DESCRIPTION. Every twin of the battery
  and every real table validates without a missed obligation.

The mutation tests beside them withdraw one rule each: a guard that
cannot fail is not a guard.
"""

from __future__ import annotations

import collections
import decimal
import math
import pathlib
import random
import re

import fixtures
import kpi_shapes
import pytest
import tail_rule
from synthtwin import (
    contract,
    generation,
    parsing,
    quality,
    rendering,
    summary,
)

FLOOR = 11
SEED = 4


# -- the shapes ---------------------------------------------------------


def _ordinal_columns() -> "list[tuple[str, list[str]]]":
    """Six bounded clinical scales, each drawn from its own seed.

    The shapes the skeptic's finding B1 was measured on: a pain score, a
    Glasgow coma score, a surgical risk grade, an Apgar score, a count
    children and a Likert item. Every one of them is a scale with an end
    a handful of rows hold, which is what a listed tail is for.
    """
    built: "list[tuple[str, list[str]]]" = []
    draw = random.Random(1)
    built += [(
        "pain",
        [
            str(draw.choices(range(11), weights=[30, 10, 12, 14, 12, 10, 8, 6, 4, 2, 0.4])[0])
            for _row in range(900)
        ],
    )]
    draw = random.Random(101)
    built += [(
        "gcs",
        [
            str(
                draw.choices(
                    range(3, 16),
                    weights=[0.4, 0.3, 0.4, 0.5, 0.6, 0.8, 1, 1.5, 2, 3, 6, 12, 70],
                )[0]
            )
            for _row in range(900)
        ],
    )]
    draw = random.Random(201)
    built += [(
        "risk_grade",
        [
            str(draw.choices(range(1, 6), weights=[20, 45, 30, 5, 0.2])[0])
            for _row in range(900)
        ],
    )]
    draw = random.Random(301)
    built += [(
        "apgar",
        [
            str(
                draw.choices(
                    range(11), weights=[0.2, 0.2, 0.3, 0.4, 0.5, 0.8, 1.5, 4, 20, 55, 17]
                )[0]
            )
            for _row in range(900)
        ],
    )]
    draw = random.Random(401)
    built += [(
        "children",
        [str(min(12, int(draw.gammavariate(1.6, 1.1)))) for _row in range(900)],
    )]
    draw = random.Random(501)
    built += [(
        "likert",
        [
            str(draw.choices(range(1, 6), weights=[5, 20, 40, 30, 0.3])[0])
            for _row in range(900)
        ],
    )]
    return built


def _measured_columns() -> "list[tuple[str, list[str]]]":
    """Four measured columns: normal, lognormal, a heavy tail and ages."""
    built: "list[tuple[str, list[str]]]" = []
    draw = random.Random(7)
    built += [("normal", [f"{draw.gauss(50, 10):.2f}" for _row in range(600)])]
    draw = random.Random(17)
    built += [(
        "lognormal",
        [f"{draw.lognormvariate(3, 0.5):.2f}" for _row in range(600)],
    )]
    draw = random.Random(27)
    built += [(
        "charges",
        [f"{1000 * draw.paretovariate(1.5):.2f}" for _row in range(600)],
    )]
    draw = random.Random(37)
    built += [(
        "age",
        [str(max(18, min(99, int(draw.gauss(58, 17))))) for _row in range(600)],
    )]
    return built


def _described(folder: pathlib.Path, name: str, cells: "list[str]"):
    """One column through the whole product path, at the landing's floor."""
    text = "value\n" + "\n".join(cells) + "\n"
    return kpi_shapes.describe(folder / name, name, text, FLOOR)


# -- 1. nothing published names a lone value ---------------------------


_NUMBER = re.compile(r"(?<![A-Za-z0-9.])-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")

# The keys of a numeric block that carry a VALUE of the column rather
# than a count of rows: a rung, a moment, the mode, an empty-stretch
# edge, and the two distances a tail publishes.
_VALUE_KEYS = (
    "percentiles",
    "percentiles_between",
    ".mean",
    ".std",
    ".skew",
    ".kurtosis",
    ".mode",
    "empty_edges",
    "tails",
)
_COUNT_KEYS = (".percent", ".rows", ".mode_count", ".values")


def _numbers_under(node: object, path: str = ""):
    """Every number a block carries, with the path it stands at."""
    if isinstance(node, dict):
        for key in node:
            yield from _numbers_under(node[key], f"{path}.{key}")
        return
    if isinstance(node, list):
        for place in range(len(node)):
            yield from _numbers_under(node[place], f"{path}[{place}]")
        return
    if isinstance(node, bool):
        return
    if isinstance(node, (int, float)):
        yield path, float(node)


def _lone_outer_values(cells: "list[str]", listed: "set[float]") -> "set[float]":
    """The outermost values of a column that too few rows hold.

    The rows the tail rule withholds are the outermost max(floor, 3) on
    each side; a value a LISTED tail names is published on purpose
    (G5.3e, the owner's ruling of 2026-09-22) and is not counted here.
    """
    values = sorted(
        value
        for value in (parsing.parse_number(cell) for cell in cells)
        if value is not None
    )
    counted = collections.Counter(values)
    units = max(FLOOR, 3)
    outer = values[:units] + values[len(values) - units:]
    return {
        value
        for value in outer
        if counted[value] < units and value not in listed
    }


def _leaks(described, cells: "list[str]", texts: "dict[str, str]") -> "list[tuple]":
    """Every published number that equals a lone outermost value."""
    block = described.document["columns"][0]
    listed: "set[float]" = set()
    tails = block.get("tails") or {}
    for side in ("low", "high"):
        if isinstance(tails.get(side), dict):
            listed = listed | set(tails[side]["values"])
    lone = _lone_outer_values(cells, listed)
    found: "list[tuple]" = []
    for path, number in _numbers_under(block):
        if not any(key in path for key in _VALUE_KEYS):
            continue
        if any(key in path for key in _COUNT_KEYS):
            continue
        if number in lone:
            found += [("description", path, number)]
    for label in sorted(texts):
        # A page may quote this repository's own documents, and a
        # section number is not a value of anybody's column.
        body = "\n".join(
            line for line in texts[label].splitlines() if "docs/spec" not in line
        )
        for token in _NUMBER.findall(body):
            try:
                number = float(token)
            except ValueError:
                continue
            if number in lone and "." in token:
                found += [(label, token)]
    return found


@pytest.mark.parametrize(
    "name", [name for name, _cells in _ordinal_columns() + _measured_columns()]
)
def test_no_published_page_names_a_value_too_few_rows_hold(
    tmp_path: pathlib.Path, name: str
) -> None:
    """The measurement the landing exists for, on ten shapes.

    MEASURED BEFORE THE TAIL RULE, over sixteen shapes at a floor of
    eleven: a description published between 13 and 46 numbers equal to a
    value fewer than eleven rows held -- the two ends, the rungs beside
    them and the moments that read them. With the rule, none: the rungs
    that would touch those rows are withheld and what stands in their
    place is the GROUP (contract 6.7a).

    The four pages a run writes are read as well as the description,
    because a number withheld in one and printed in another is not
    withheld.
    """
    cells = dict(_ordinal_columns() + _measured_columns())[name]
    described = _described(tmp_path, name, cells)
    outcome = kpi_shapes.measure(described, described.table.read_text(), "real.csv")
    twin = generation.generate(described.loaded, SEED)
    twin_text = rendering.twin_csv(twin)
    pages = {
        "summary": summary.render(described.document, ""),
        "quality": quality.quality_report(described.loaded, outcome),
        "report": rendering.report(described.loaded, twin),
        "quality_twin": quality.quality_report(
            described.loaded,
            kpi_shapes.measure(described, twin_text, "twin.csv"),
        ),
    }
    assert _leaks(described, cells, pages) == []


# -- 2. the facts do not solve for a withheld end ----------------------


def _feasible_maxima(summed: int, squared: int, rows: int) -> "set[int]":
    """Which largest step a tail of whole steps could hold.

    The skeptic's own attack, written out: with `rows` rows whose
    distances from the boundary are whole numbers of grid steps summing
    to `summed` and squaring to `squared`, which values can the LARGEST
    of them take? Where exactly one can, the published facts name the
    withheld end in all but name. The walk is a bounded counted subset
    sum over the steps, which is what makes the answer a proof rather
    than a search.
    """
    if summed == 0:
        return {0} if squared == 0 else set()
    largest = min(math.isqrt(squared), summed)
    rows = min(rows, summed)
    reach = [[0] * (summed + 1) for _place in range(rows + 1)]
    reach[0][0] = 1
    found: "set[int]" = set()
    for step in range(1, largest + 1):
        square = step * step
        for count in range(1, rows + 1):
            before, now = reach[count - 1], reach[count]
            for total in range(step, summed + 1):
                if before[total - step]:
                    now[total] |= before[total - step] << square
        left, over = summed - step, squared - square
        if left >= 0 and over >= 0:
            for count in range(0, rows):
                if (reach[count][left] >> over) & 1:
                    found.add(step)
                    break
    return found


def _solved_sides(described, cells: "list[str]") -> "list[tuple]":
    """Which withheld ends the published facts determine, if any."""
    block = described.document["columns"][0]
    tails = block.get("tails")
    if not tails or tails.get("low") is None:
        return []
    if block.get("integer_valued"):
        unit = decimal.Decimal(1)
    else:
        widths = [key for key in block.get("fraction_widths", {}) if key.isdigit()]
        if len(widths) != 1:
            return []
        unit = decimal.Decimal(1).scaleb(-int(widths[0]))
    values = sorted(
        value
        for value in (parsing.parse_number(cell) for cell in cells)
        if value is not None
    )
    counted = collections.Counter(values)
    solved: "list[tuple]" = []
    for side in ("low", "high"):
        published = tails[side]
        if published["values"]:
            continue
        rows = published["rows"]
        mean = published["mean_distance"]
        root = published["rms_distance"]
        if mean == 0:
            continue
        boundary = decimal.Decimal(
            repr(tail_rule.rung_of(block, published["percent"]))
        ) / unit
        over = (
            boundary - boundary.to_integral_value(rounding=decimal.ROUND_FLOOR)
            if side == "low"
            else boundary.to_integral_value(rounding=decimal.ROUND_CEILING) - boundary
        )
        summed = decimal.Decimal(rows) * decimal.Decimal(mean) / unit
        squared = (
            decimal.Decimal(rows)
            * decimal.Decimal(root)
            * decimal.Decimal(root)
            / (unit * unit)
        )
        first = summed - rows * over
        second = squared - 2 * over * summed + rows * over * over
        whole_first = int(first.to_integral_value())
        whole_second = int(second.to_integral_value())
        if abs(first - whole_first) > decimal.Decimal("1e-4"):
            continue
        if abs(second - whole_second) > decimal.Decimal("1e-3"):
            continue
        if whole_first * min(rows, whole_first) * math.isqrt(whole_second) > 3_000_000:
            continue
        maxima = _feasible_maxima(whole_first, whole_second, rows)
        extreme = values[0] if side == "low" else values[len(values) - 1]
        if len(maxima) == 1 and counted[extreme] < max(FLOOR, 3):
            solved += [(side, extreme, counted[extreme])]
    return solved


@pytest.mark.parametrize(
    "name", [name for name, _cells in _ordinal_columns() + _measured_columns()]
)
def test_the_published_facts_do_not_solve_for_a_withheld_end(
    tmp_path: pathlib.Path, name: str
) -> None:
    """The skeptic's finding B2, asked of every shape here.

    A tail on a grid publishes its rows, its mean distance and its
    root-mean-square, and those three are whole numbers of grid steps:
    a reader can walk every set of steps that meets them and ask which
    largest step is possible. Where exactly one is, the end is named in
    all but name -- and the producer's answer is to LIST that tail's
    values instead (contract 6.7, TL6), which says so outright rather
    than leaving it to be recovered.

    So the claim here is not that the walk finds nothing: it is that no
    tail this battery describes leaves its withheld end solvable.
    """
    cells = dict(_ordinal_columns() + _measured_columns())[name]
    described = _described(tmp_path, name, cells)
    assert _solved_sides(described, cells) == []


# -- 3. an ordinal scale keeps its own values --------------------------


@pytest.mark.parametrize("name", [name for name, _cells in _ordinal_columns()])
def test_an_ordinal_twin_writes_the_scale_and_nothing_outside_it(
    tmp_path: pathlib.Path, name: str
) -> None:
    """The skeptic's finding B1, repaired by the listed tail (G5.3e).

    MEASURED BEFORE IT: a pain score of 0 to 10 at a floor of eleven
    published no end, its twin wrote 50 cells at 11 -- a value the scale
    does not have -- and none at 10, and the twin's mean stood 25 per
    cent above the table's with nothing missed. The listed tail
    publishes the tail's own values, so the twin writes the scale's own
    ends; the owner's ruling of 2026-09-22 is what allows it.
    """
    cells = dict(_ordinal_columns())[name]
    described = _described(tmp_path, name, cells)
    block = described.document["columns"][0]
    assert block["tails"]["low"]["values"], "a bounded scale lists its low tail"
    assert block["tails"]["high"]["values"], "and its high tail"
    values = sorted(
        value
        for value in (parsing.parse_number(cell) for cell in cells)
        if value is not None
    )
    scale = set(values)
    twin = generation.generate(described.loaded, SEED)
    written = [
        parsing.parse_number(cell) for cell in twin.columns[0] if cell != ""
    ]
    assert [value for value in written if value not in scale] == [], (
        "no twin cell may stand outside the scale the column holds"
    )
    assert min(written) == values[0] and max(written) == values[-1], (
        "the listed tails carry the scale's own two ends"
    )


# -- 4. and the twin still meets its description -----------------------


@pytest.mark.parametrize(
    "name", [name for name, _cells in _ordinal_columns() + _measured_columns()]
)
def test_every_twin_and_every_table_of_the_battery_is_checked_clean(
    tmp_path: pathlib.Path, name: str
) -> None:
    """Both files, through the real validator, with no carve-out.

    The real table is checked against its own description as well as the
    twin, because a rule that made the twin pass by weakening the check
    would pass here twice and mean nothing.
    """
    cells = dict(_ordinal_columns() + _measured_columns())[name]
    described = _described(tmp_path, name, cells)
    real = kpi_shapes.measure(described, described.table.read_text(), "real.csv")
    assert kpi_shapes.missed(real) == []
    twin = generation.generate(described.loaded, SEED)
    outcome = kpi_shapes.measure(described, rendering.twin_csv(twin), "twin.csv")
    assert kpi_shapes.missed(outcome) == []


# -- 4a. the real cells the twin's own range covers --------------------


@pytest.mark.parametrize(
    "name", [name for name, _cells in _ordinal_columns() + _measured_columns()]
)
def test_no_real_cell_stands_outside_the_twin_s_own_range(
    tmp_path: pathlib.Path, name: str
) -> None:
    """The skeptic's finding B6, and why the derived end is biased outward.

    Code developed on a twin is run against the real table, so a real
    value outside the twin's range is a value that code has never seen.
    The fitted end of a light tail stands INSIDE the real extreme --
    16 real cells of a 20,000-row normal column fell outside its twin's
    range before the outward move of plan P4-D326, and 2 of a
    hundred-row one. The move takes the end out to where the largest of
    the tail's rows is expected to stand, held under the tail's own
    bound, and what is left is the ceiling this asserts: on a BOUNDED
    scale no cell at all, because a listed tail carries the scale's own
    ends; on a measured column at most ONE -- the single most extreme
    value of a heavy tail, which stands where no pair of moments can
    predict it. Measured over this battery: none on the six scales,
    none on the normal and the age columns, and one each on the
    lognormal and the Pareto charges.
    """
    cells = dict(_ordinal_columns() + _measured_columns())[name]
    described = _described(tmp_path, name, cells)
    values = [
        value
        for value in (parsing.parse_number(cell) for cell in cells)
        if value is not None
    ]
    twin = generation.generate(described.loaded, SEED)
    written = [
        parsing.parse_number(cell) for cell in twin.columns[0] if cell != ""
    ]
    outside = [
        value
        for value in values
        if value < min(written) or value > max(written)
    ]
    ceiling = 0 if name in dict(_ordinal_columns()) else 1
    assert len(outside) <= ceiling, (min(written), max(written), outside[:6])


# -- 5. the counts a listed tail solves for ----------------------------


@pytest.mark.parametrize("name", [name for name, _cells in _ordinal_columns()])
def test_a_listed_tail_meets_the_mean_distance_it_publishes(
    tmp_path: pathlib.Path, name: str
) -> None:
    """G5.3e's counts, checked against the two moments they answer to.

    The counts are solved so that the summed distance equals `m * d1`
    exactly wherever whole counts on three values can reach it, which on
    a grid they always can: every distance is a whole number of steps
    and so is the target. The check is the arithmetic itself, taken over
    exact rationals here rather than in binary64.
    """
    cells = dict(_ordinal_columns())[name]
    described = _described(tmp_path, name, cells)
    facts = described.loaded.columns[0].facts
    ladder = contract.tail_ladder(facts)
    assert ladder is not None
    for side in (ladder.low, ladder.high):
        assert side is not None
        assert side.listed, "every tail of a bounded scale is a listed one"
        rows = side.rows
        assert sum(side.counts) == rows
        assert all(count >= 1 for count in side.counts)
        summed = sum(
            decimal.Decimal(repr(abs(side.boundary - value))) * count
            for value, count in zip(side.listed, side.counts)
        )
        wanted = decimal.Decimal(rows) * decimal.Decimal(
            repr(
                facts.tails.low.mean_distance
                if side is ladder.low
                else facts.tails.high.mean_distance
            )
        )
        assert abs(summed - wanted) <= decimal.Decimal("1e-9") * max(
            abs(wanted), decimal.Decimal(1)
        ), (side.listed, side.counts, summed, wanted)


# -- 6. the mutants ----------------------------------------------------


def test_the_listed_tail_is_what_keeps_an_ordinal_scale(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mutant 1: withdraw G5.3e's listing, and the scale goes.

    The producer publishes no `values` for either tail, so the twin
    reads the smooth shape of G5.3b and rounds it onto the grid: the
    cells then stand outside the scale the column holds, which is the
    defect the listed tail closes.
    """
    cells = dict(_ordinal_columns())["pain"]
    described = _described(tmp_path, "pain-listed", cells)
    scale = {
        value
        for value in (parsing.parse_number(cell) for cell in cells)
        if value is not None
    }
    twin = generation.generate(described.loaded, SEED)
    held = [parsing.parse_number(cell) for cell in twin.columns[0] if cell != ""]
    assert [value for value in held if value not in scale] == []

    monkeypatch.setattr(
        contract, "_listed_counts", lambda listed, boundary, rows, mean, root: ()
    )
    # The counts gone, the reader falls back to its shape: the ladder is
    # rebuilt from the same published facts and nothing else moves.
    facts = described.loaded.columns[0].facts
    stripped = contract.dataclasses.replace(
        facts,
        tails=contract.dataclasses.replace(
            facts.tails,
            low=contract.dataclasses.replace(facts.tails.low, values=()),
            high=contract.dataclasses.replace(facts.tails.high, values=()),
        ),
    )
    ladder = contract.tail_ladder(stripped)
    assert ladder is not None
    off = [value for value in ladder if value not in scale]
    assert off, "without the listing the ladder leaves the scale"


def test_the_band_share_is_what_keeps_a_listed_tail_s_own_values(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mutant 2: withdraw the band share of a listed tail (G5.3e, G5.2b).

    Every value a listed tail names is a value of the real column and is
    checked as one, so the band it belongs to needs a stratum for each of
    them. MEASURED on the mode column of the second Codex round -- seven
    one-place values, three of them negative -- the share gave the
    negative band two strata against a listed tail naming `-1.8` and
    `-0.9` and an interior run of `-0.6`: the twin wrote no `-0.9` at
    all and `validate` MISSED `tails.low.values` at every seed. With the
    share the twin writes the column's own seven numbers and no other;
    withdrawn, it drops one of them and invents `3.4` in its place.
    """
    values = (-1.8, -0.9, -0.6, 0.8, 1.8, 3.3, 3.5)
    counts = (9, 18, 28, 23, 8, 30, 23)
    cells: "list[str]" = []
    for value, count in zip(values, counts):
        cells += [f"{value:.1f}"] * count
    described = _described(tmp_path, "mode", cells)
    held = sorted(
        {
            parsing.parse_number(cell)
            for cell in generation.generate(described.loaded, SEED).columns[0]
            if cell != ""
        }
    )
    assert held == list(values), held

    monkeypatch.setattr(
        generation,
        "_listed_needs",
        lambda facts, negatives, zeros, positives: (0, 0),
    )
    after = sorted(
        {
            parsing.parse_number(cell)
            for cell in generation.generate(described.loaded, SEED).columns[0]
            if cell != ""
        }
    )
    assert after != held, after
    assert [value for value in after if value not in values], (
        "without the share the twin writes a number the column does not hold"
    )


def test_the_grid_staircase_is_what_keeps_a_tail_s_rows_apart(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mutant 3: withdraw G5.3b's grid staircase, and two rows share a value.

    The reading `a(s)` is smooth, and rounding it onto a published grid
    puts two rows of a short tail on one value, which costs the twin a
    NUMBER: measured on five hundred laboratory readings at one place,
    thirty-one different numbers published and the twin holding
    twenty-six, with `n_distinct_values` MISSED on a twin whose own
    report named it. The claim is asserted on the ladder itself, which
    is where the rule acts and where a later walk cannot cover for it;
    the twin's own cells are held to the same rule by the frozen case
    `tail_shape_ends` of method section G14.3, whose committed bytes
    move when this is withdrawn.
    """
    draw = random.Random(41)
    cells = [f"{round(draw.gauss(4.2, 2.0), 1):.1f}" for _row in range(500)]
    described = _described(tmp_path, "labs", cells)
    facts = described.loaded.columns[0].facts
    ladder = contract.tail_ladder(facts)
    assert ladder is not None and ladder.low is not None
    assert ladder.low.steps, "a tail on a grid reads its rows through the staircase"
    assert len(set(ladder.low.steps)) == len(ladder.low.steps), (
        "every row of the tail stands on its own grid point"
    )

    monkeypatch.setattr(contract, "_tail_steps", lambda side, figures: ())
    without = contract.tail_ladder(facts)
    assert without is not None and without.low is not None
    assert not without.low.steps
    smooth = [
        contract.tail_read(without, rank, facts.n_used_in_statistics)
        for rank in range(without.low.rows)
    ]
    placed = [round(value, 1) for value in smooth]
    assert len(set(placed)) < len(placed), (
        "without the staircase two rows of the tail round onto one value"
    )


def test_a_derived_end_stays_inside_what_a_padded_column_can_write(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mutant 4: withdraw the pad ceiling, and the census goes with it.

    1,200 offsets written `+0123` and `0123` publish `pad_widths
    {"4": 1200}` -- every cell wears a pad, so no value of the column
    reaches four figures. A derived end above 999 is a value those
    facts rule out and one no form the block publishes can write:
    `+1006` wears no pad, and ten such cells send P4-D148's plus route
    the other way, so the twin's own description counts 482 padded
    cells of 1,200 (method G5.3b step 4).
    """
    draw = random.Random(5)
    rows: "list[str]" = []
    for _row in range(1200):
        offset = draw.randint(0, 999)
        text = f"+{offset:04d}" if draw.random() < 0.6 else f"{offset:04d}"
        change = draw.randint(-5000, 5000) / 100
        rows += [f"{text},{change:+.2f}"]
    described = kpi_shapes.describe(
        tmp_path / "offsets",
        "offsets",
        "offset,delta\n" + "\n".join(rows) + "\n",
        FLOOR,
    )
    facts = described.loaded.columns[0].facts
    assert described.block("offset")["pad_widths"] == {"4": 1200}
    ladder = contract.tail_ladder(facts)
    assert ladder is not None
    assert ladder[len(ladder) - 1] <= 999.0, ladder[len(ladder) - 1]

    twin = generation.generate(described.loaded, SEED)
    written = [cell for cell in twin.columns[0] if cell != ""]
    again = kpi_shapes.describe(
        tmp_path / "offsets-again",
        "again",
        "offset\n" + "\n".join(written) + "\n",
        FLOOR,
    )
    assert again.block("offset")["pad_widths"] == {"4": 1200}

    monkeypatch.setattr(
        contract, "_within_the_pad", lambda value, low, boundary, facts: value
    )
    loosened = contract.tail_ladder(facts)
    assert loosened is not None
    assert loosened[len(loosened) - 1] > 999.0, (
        "without the ceiling the derived end leaves what a pad can hold"
    )
    unpadded = kpi_shapes.describe(
        tmp_path / "offsets-loose",
        "loose",
        "offset\n"
        + "\n".join(
            cell
            for cell in generation.generate(described.loaded, SEED).columns[0]
            if cell != ""
        )
        + "\n",
        FLOOR,
    )
    assert unpadded.block("offset")["pad_widths"] != {"4": 1200}, (
        "without the ceiling the twin's own description loses the census"
    )


def test_a_derived_end_stays_above_the_mark_between_thousands(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mutant 5: withdraw the marks clamp, and a cell loses its comma.

    240 prices written `92,959.11` publish `thousands_marks {",": 240}`
    -- a cell carries a mark exactly where its number reaches a
    thousand, so every value of this column does. The low tail's reach
    carries its derived end past nought, G5.5a holds it at the smallest
    grid step there is, and 0.01 is a cell with no mark in it: the
    walk that fixes how many cells reach a thousand may move neither
    end, so the twin's own census comes back one short.
    """
    draw = random.Random(29)
    cells = [
        f'"{draw.randrange(100000, 9999999) / 100:,.2f}"'
        for _row in range(240)
    ]
    described = _described(tmp_path, "prices", cells)
    assert described.block("value")["thousands_marks"] == {",": 240}
    facts = described.loaded.columns[0].facts
    ladder = contract.tail_ladder(facts)
    assert ladder is not None
    assert ladder[0] >= 1000.0, ladder[0]
    written = [
        cell
        for cell in generation.generate(described.loaded, SEED).columns[0]
        if cell != ""
    ]
    assert [cell for cell in written if "," not in cell] == []

    monkeypatch.setattr(
        contract, "_within_the_marks", lambda value, low, boundary, facts: value
    )
    loosened = contract.tail_ladder(facts)
    assert loosened is not None
    assert loosened[0] < 1000.0
    bare = [
        cell
        for cell in generation.generate(described.loaded, SEED).columns[0]
        if cell != "" and "," not in cell
    ]
    assert bare, "without the clamp the twin writes a cell with no mark"


def test_a_tail_row_can_move_for_a_field_width(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mutant 6: withdraw the tail's room, and a padded cell goes.

    120 record codes `S00042`: eleven of them hold a value under ten
    thousand, so eleven cells are published padded at five figures
    while 109 wear the field plainly. The twin's tail staircase puts
    TEN of its rows under ten thousand and the eleventh at 10009, and
    no interior stratum can reach four figures -- so the width G6.6
    serves has to come from a tail row, which may take any value
    between its two neighbours because no rung is published there.
    """
    draw = random.Random(14)
    sites = ["north", "south", "east", "west"]
    rows: "list[str]" = []
    for _row in range(120):
        sbp = f"{draw.randint(90, 180)}" if draw.random() < 0.9 else "ND"
        rows += [
            f"S{draw.randint(1, 99999):05d},{sbp},{draw.choice(sites)}"
        ]
    described = kpi_shapes.describe(
        tmp_path / "records",
        "records",
        "record_id,sbp,site\n" + "\n".join(rows) + "\n",
        FLOOR,
    )
    block = described.block("record_id")
    inner = block["numbers"] if "numbers" in block else block
    assert inner["pad_widths"] == {"5": 11}
    written = [
        cell
        for cell in generation.generate(described.loaded, SEED).columns[0]
        if cell != ""
    ]
    assert len([cell for cell in written if cell[:2] == "S0"]) == 11

    monkeypatch.setattr(
        generation,
        "_tail_room",
        lambda place, moved, tails, layout, rungs, column: (
            generation._share_of(place, layout, rungs, column.n_numeric)
        ),
    )
    narrowed = [
        cell
        for cell in generation.generate(described.loaded, SEED).columns[0]
        if cell != ""
    ]
    assert len([cell for cell in narrowed if cell[:2] == "S0"]) < 11, (
        "without the tail's room the twin is a padded cell short"
    )


def _wholly_inside(
    start: int,
    lengths: "list[int]",
    rungs: object,
    numbers: int,
    reaching: bool = False,
) -> "tuple[int, int]":
    """The rule landing 3.3 replaced: a run must lie WHOLLY inside a tail.

    The old code, put back, which is what a mutation test owes: the
    leading runs are counted while the next one still ends at or before
    the tail's last row, and the trailing runs while the next one still
    begins at or after the tail's first.
    """
    if not isinstance(rungs, contract.ShapedLadder):
        return 0, 0
    lead = 0
    low = rungs.low
    if low is not None and low.listed:
        reach = start
        for length in lengths:
            if reach + length > low.rows:
                break
            reach = reach + length
            lead = lead + 1
    trail = 0
    high = rungs.high
    if high is not None and high.listed:
        reach = start + sum(lengths)
        for place in range(len(lengths)):
            length = lengths[len(lengths) - 1 - place]
            if reach - length < numbers - high.rows:
                break
            if place >= len(lengths) - lead:
                break
            reach = reach - length
            trail = trail + 1
    return lead, trail


def test_a_listed_value_standing_inside_the_boundary_too_is_still_written(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mutant 8: count only the runs lying WHOLLY inside a tail (G5.3e).

    A TAIL'S INNERMOST LISTED VALUE IS OFTEN THE VALUE JUST INSIDE THE
    BOUNDARY AS WELL, and the ladder then reads one number across the
    edge. Such a run lies wholly inside nothing, so the narrower rule
    passed over it, the layout joined it to its neighbours, and the
    stratum that swallowed it read its own share instead -- a number the
    tail does not name.

    MEASURED on the 240 clinical codes of KPI K-P4-11's ClinVar system,
    AT THAT KPI'S OWN FLOOR OF ONE, which is where it was found: the
    high tail lists two values, the inner one stands at eleven ranks of
    which the outer two are the tail's, and under the narrower rule the
    twin wrote five cells at `920759` where the table holds `920760` --
    so `validate` MISSED `tails.high.values` and one of the eighteen
    systems stopped validating clean.
    """
    import test_p4d19_declared_codes as codes

    system = "clinvar"
    described = kpi_shapes.describe(
        tmp_path / system,
        system,
        fixtures.single_column_table(system, codes._SYSTEMS[system]),
        1,
    )
    side = described.document["columns"][0]["tails"]["high"]
    assert side["values"], "this column's high tail is published by its values"
    listed = tuple(side["values"])

    # THE KPI'S OWN SEED. The eighteen systems are generated at seed 3
    # and the defect showed there; at four other seeds the walk landed
    # this column's inner run on the listed value by luck, which is
    # what a rule is for.
    seed = 3

    def cores() -> "set[float]":
        return {
            float(cell[3:])
            for cell in generation.generate(described.loaded, seed).columns[0]
            if cell != ""
        }

    held = cores()
    assert all(value in held for value in listed), sorted(held)[-4:]
    assert not kpi_shapes.missed(
        kpi_shapes.measure(
            described,
            rendering.twin_csv(generation.generate(described.loaded, seed)),
            "cut.csv",
        )
    )

    monkeypatch.setattr(generation, "_listed_runs", _wholly_inside)
    without = cores()
    assert [value for value in listed if value not in without], (
        "with the narrower rule the twin still writes every value the "
        "tail names, so this case is no witness for it"
    )
    assert kpi_shapes.missed(
        kpi_shapes.measure(
            described,
            rendering.twin_csv(generation.generate(described.loaded, seed)),
            "narrow.csv",
        )
    ) == [f"{system}:tails.high.values"]


def test_a_count_column_beside_a_zero_heap_keeps_its_ones(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The repair found while building the landing (plan P4-D327).

    A band's ranks are read at that band's own sign (method G5.2a step
    1a). The positive band begins where the zero stratum ends and the
    ladder does not know it: it crosses from the last rung reading
    nought to the first reading one by a straight line, the integer
    rule takes the band's first ranks back to nought, G5.5 repairs that
    run to one BESIDE the real plateau of one, and G6.5a's separation
    then walks every stratum above it up by one.

    MEASURED on 2,000 counts drawn `int(expovariate(0.2))` at seed 7
    beside a constant column, twin seed 4, at a floor of one and at
    eleven alike -- the two floors write the same cells here, which is
    why one run answers for both. With the step the twin writes the
    value one in 324 cells against the table's 317 and its mean stands
    1.3 per cent above the table's; withdrawn, it writes one in FOUR
    cells, two in 320 against 236, and its mean 19.3 per cent high --
    with nothing missed either way, which is why this is measured here
    rather than left to `validate`.
    """
    draw = random.Random(7)
    counts = [str(int(draw.expovariate(0.2))) for _row in range(2000)]
    assert counts.count("1") == 317 and counts.count("0") == 386
    real = sum(float(cell) for cell in counts) / len(counts)
    text = "count,site\n" + "\n".join(f"{cell},A" for cell in counts) + "\n"
    described = kpi_shapes.describe(tmp_path / "counts", "counts", text, FLOOR)

    def written() -> "list[str]":
        return [
            cell
            for cell in generation.generate(described.loaded, SEED).columns[0]
            if cell != ""
        ]

    held = written()
    mean = sum(float(cell) for cell in held) / len(held)
    assert held.count("1") == 324, held.count("1")
    assert abs(mean / real - 1) < 0.02, mean

    monkeypatch.setattr(generation, "_band_signed", lambda held, band: held)
    without = written()
    astray = sum(float(cell) for cell in without) / len(without)
    assert without.count("1") == 4, without.count("1")
    assert astray / real - 1 > 0.15, astray


def _groups_of(cells: "list[str]", floor: int) -> "list[dict[str, int]]":
    """The groups of bins one column's own interior cells make (G6.7a).

    A RECOUNT OF THE TABLE, not a reading of the key under test. The
    scale is the two boundary rungs, a value outside it is in no bin,
    and the interior cells are grouped left to right: a group closes
    when it holds `max(floor, 3)` of them and a short last group joins
    the one before it.
    """
    values = sorted(
        value
        for value in (parsing.parse_number(cell) for cell in cells)
        if value is not None
    )
    count = len(values)
    units = tail_rule.units(floor)
    percent = tail_rule.percent_of(count, floor)
    assert percent is not None, "this column is too small for a tail block"
    low_rows = tail_rule.rows_of(count, percent, True)
    high_rows = tail_rule.rows_of(count, 100 - percent, False)
    lowest = float(tail_rule.rung_at(values, percent))
    highest = float(tail_rule.rung_at(values, 100 - percent))
    interior = values[low_rows : count - high_rows]
    if len(interior) < units:
        return []
    counted = collections.Counter(
        parsing.scale_bin(value, lowest, highest) for value in interior
    )
    groups: "list[dict[str, int]]" = []
    first = 0
    running = 0
    for place in range(32):
        running = running + counted[place]
        if running >= units:
            groups += [{"first": first, "last": place, "count": running}]
            first = place + 1
            running = 0
    if running > 0 and groups:
        last = groups[len(groups) - 1]
        groups[len(groups) - 1] = {
            "first": last["first"],
            "last": 31,
            "count": last["count"] + running,
        }
    elif running > 0:
        groups += [{"first": 0, "last": 31, "count": running}]
    return groups


def test_the_histogram_survives_the_floor_in_groups(
    tmp_path: pathlib.Path,
) -> None:
    """The shape of a column still reaches a reader at a floor of eleven.

    THE CENSUS OF EVERY BIN IS ALL OR NOTHING and vanishes at any floor
    above one on every column whose bins are not all crowded: before
    stage 3 a description of any of the ten columns below published no
    histogram at all at this floor. `bin_groups` carries the same shape
    in groups that clear the floor (method G6.7a), and what is asserted
    here is the recount of each table beside the key it publishes --
    the groups themselves, not their number -- so a producer that
    published the wrong groups fails as loudly as one that published
    none.
    """
    counted: "dict[str, int]" = {}
    for name, cells in _ordinal_columns() + _measured_columns():
        described = _described(tmp_path, name, cells)
        block = described.document["columns"][0]
        assert block["bin_groups"] == _groups_of(cells, FLOOR), name
        assert block["value_histogram"] == {}, name
        counted[name] = len(block["bin_groups"])
    assert all(number > 0 for number in counted.values()), counted
    assert sum(counted.values()) >= 30, counted


def test_a_tail_stands_at_both_ends_of_the_binary64_range(
    tmp_path: pathlib.Path,
) -> None:
    """The whole range, described, generated and checked (the skeptic's B4).

    THE MEAN SQUARE OF A DISTANCE IS THE SQUARE OF A COLUMN'S UNIT and
    the range does not hold it: on p-values reaching 1e-300 it underflows
    to nought while the mean distance does not, and on magnitudes near
    1e300 it overflows. The prototype published `mean_square_distance`
    and crashed on both -- `ZeroDivisionError` where the shape divided by
    a nought mean square, `OverflowError` where the producer squared a
    distance it could not hold. What is published is the ROOT-mean-square
    in the column's own unit (contract 6.7a), which is the same number
    and one this format holds at either end.

    Three columns, each through the whole path -- read, describe, load,
    generate, validate -- and each asked for the same two things: that
    nothing raises, and that the REAL table meets its own description.
    """
    draw = random.Random(9)
    columns = {
        # A p-value column whose smallest values are subnormal.
        "p_value": [f"{draw.paretovariate(0.35) * 1e-300:.3e}" for _row in range(400)],
        # ...and one whose largest reach the other end of the range.
        "vast": [f"{draw.paretovariate(0.35) * 1e295:.3e}" for _row in range(400)],
        # ...and one whose whole column lies among the subnormals, where
        # the format's own steps are the only grid there is.
        "subnormal": [repr(step * 5e-324) for step in range(1, 401)],
    }
    for name, cells in columns.items():
        described = _described(tmp_path, name, cells)
        side = described.document["columns"][0]["tails"]["high"]
        assert side["rms_distance"] >= side["mean_distance"] > 0.0, (name, side)
        assert math.isfinite(side["rms_distance"]), (name, side)
        twin = generation.generate(described.loaded, SEED)
        written = rendering.twin_csv(twin)
        assert len([cell for cell in twin.columns[0] if cell != ""]) == len(cells)
        kpi_shapes.measure(described, written, f"{name}-twin.csv")
        assert not kpi_shapes.missed(
            kpi_shapes.measure(
                described, "value\n" + "\n".join(cells) + "\n", f"{name}-real.csv"
            )
        ), name
