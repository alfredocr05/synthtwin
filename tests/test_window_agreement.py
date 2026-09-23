"""Landing 2b.1, part 2: one window, printed once, by two reports.

The twin's own report and the quality report both print the window
method G12.2 and G12.3 allow each rung and each moment. They are
written by two modules that may not import each other (validation
method V1.4), and before this landing they drew two different windows
for one fact, in two ways:

1. THE WIDEST STRATUM. The generator read it off the layout it built;
   the validator estimated it from the description, and the estimate
   was narrower. On a 2,000-row rounded-income column the twin report
   said p75 was allowed anywhere from 55673.3 to 63799.2 and inside,
   and the quality report said 59624.75 to 60275.25 and MISSED.
2. THE LAST DIGITS (residual R-P4-61). One method, two operation
   orders: on the values 1 to 60 at seed 7 the skew range read
   ...745 in one report and ...754 in the other.

Both now read the widest stratum off the description alone -- G5.2a's
cap, which G5.2b's band floor and G5.2a's levelling keep every stratum
under wherever the carrier and reach steps move no cell -- and both
follow one operation order, stated in G12.2, G12.3 and G12.3a.

Every table is built by seeded neutral code at runtime (plan D13).
"""

import dataclasses
import importlib.util
import math
import pathlib
import random
import re

import pytest

from synthtwin import contract, generation, parsing, profile, reading, rendering
from synthtwin import taxonomy, validation
from tests import fixtures
from tests.test_stage2_round_trip import _exit_of

SEEDS = ("1", "7", "23")

ORACLE_PATH = (
    pathlib.Path(__file__).resolve().parent.parent
    / "tools"
    / "reference"
    / "make_generation_reference_vectors.py"
)


def _oracle():
    """The independent oracle, loaded from its path (it is not a package)."""
    spec = importlib.util.spec_from_file_location(
        "make_generation_reference_vectors", ORACLE_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# -- the shapes the gate names --------------------------------------------


def _weight(draw: random.Random, rows: int) -> "list[str]":
    return [f"{draw.gauss(80, 16):.1f}" for _ in range(rows)]


def _uniform_three_figures(draw: random.Random, rows: int) -> "list[str]":
    return [f"{draw.random():.3f}" for _ in range(rows)]


def _income(draw: random.Random, rows: int) -> "list[str]":
    return [
        str(int(round(draw.lognormvariate(10.8, 0.7), -2)))
        for _ in range(rows)
    ]


def _creatinine(draw: random.Random, rows: int) -> "list[str]":
    return ["%.2f" % math.exp(draw.gauss(0.0, 0.35)) for _ in range(rows)]


def _body_mass(draw: random.Random, rows: int) -> "list[str]":
    return [f"{draw.gauss(27, 4):.1f}" for _ in range(rows)]


def _kilograms(draw: random.Random, rows: int) -> "list[str]":
    return [f"{draw.gauss(80, 16):.1f} kg" for _ in range(rows)]


def _percent(draw: random.Random, rows: int) -> "list[str]":
    return [f"{draw.gauss(55, 12):.1f}%" for _ in range(rows)]


GATE = [
    ("weight", _weight),
    ("uniform_three_figures", _uniform_three_figures),
    ("income", _income),
    ("creatinine", _creatinine),
    ("body_mass", _body_mass),
    ("kilograms", _kilograms),
    ("percent", _percent),
]
SIZES = (500, 2000, 4000)
CASES = [(name, build, rows) for name, build in GATE for rows in SIZES]

# ONE GATE CASE USED TO MISS ONE OBLIGATION THAT IS NOT A WINDOW, and
# the repair of it is why this map is empty (integration repair of
# landing 2b.1). The 2,000-row uniform column publishes 862 different
# numbers and its twin held 861 at every seed: its first positive
# stratum's grid value reads as `0.000`, method G5.5's plain sign repair
# sent it to the published maximum `1.000` -- a number another stratum
# already held, which spends one of the column's different numbers --
# and G6.5a's separation walk could not bring it back, because every grid
# point within its reach was held. The same shortfall of one number was
# measured on one-figure columns that cross zero. G5.5 now repairs a
# stratum on a grid onto the nearest free grid point of its own side of
# zero instead, so no two strata land on one number and the count comes
# back; measured by withdrawing that repair alone, which restores the
# miss on this shape and no other change does.
#
# The map stays here, empty, because the assertion below reads it: a
# shape that begins to miss an obligation again turns this gate red
# rather than being written into the map without a reason.
CARRIED: "dict[tuple[str, int], list[str]]" = {}

# The facts whose windows both reports print: the nine interior rungs and
# the four moments.
_INTERIOR = ("p01", "p05", "p10", "p25", "p50", "p75", "p90", "p95", "p99")
_MOMENTS = ("mean", "std", "skew", "kurtosis")


def _twin_windows(text: str) -> "dict[str, tuple[str, str]]":
    """Every rung and moment window the twin's own report prints."""
    found: "dict[str, tuple[str, str]]" = {}
    fact = ""
    for line in text.splitlines():
        named = re.fullmatch(r"  .* \(([^()]+)\)", line)
        if named:
            fact = named.group(1)
            continue
        window = re.fullmatch(r"    allowed anywhere from (\S+) to (\S+): .*", line)
        if window and fact:
            last = fact.split(".")[-1]
            if last in _INTERIOR or last in _MOMENTS:
                assert last not in found, ("one fact printed twice", fact)
                found[last] = (window.group(1), window.group(2))
            fact = ""
    return found


def _quality_windows(text: str) -> "dict[str, tuple[str, str, str]]":
    """Every rung and moment window the quality report prints, with its verdict."""
    found: "dict[str, tuple[str, str, str]]" = {}
    subcheck = ""
    verdict = ""
    for line in text.splitlines():
        head = re.fullmatch(r"  (\S.*?) \[[^\]]+\]: (\S+)", line)
        if head:
            subcheck = head.group(1).split(" ")[-1]
            verdict = head.group(2)
            continue
        window = re.fullmatch(
            r"      the description asks for: .*\(between (\S+) and (\S+)\)", line
        )
        if window and subcheck:
            last = subcheck.split(".")[-1]
            if subcheck.split(".")[0] in ("ladder", "moments") and (
                last in _INTERIOR or last in _MOMENTS
            ):
                # A MISSED check is printed twice -- once where the report
                # opens on what was missed and once in its place -- and
                # it must be the same window both times.
                if last in found:
                    assert found[last][:2] == (window.group(1), window.group(2)), (
                        "one fact printed with two windows",
                        subcheck,
                    )
                    continue
                found[last] = (window.group(1), window.group(2), verdict)
            subcheck = ""
    return found


def _missed(text: str) -> "list[str]":
    return [line for line in text.splitlines() if line.endswith(": MISSED")]


def _one_file(folder: pathlib.Path, pattern: str) -> str:
    found = sorted(folder.glob(pattern))
    assert len(found) == 1, (folder, pattern, found)
    return found[0].read_text(encoding="utf-8")


def _described_files(
    folder: pathlib.Path, cells: "list[str]", seed: str
) -> "tuple[pathlib.Path, pathlib.Path, pathlib.Path]":
    """Describe the real table and build its twin; return the three paths."""
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "real.csv"
    table.write_text(
        fixtures.rows_to_csv(["value"], [[cell] for cell in cells]),
        encoding="utf-8",
        newline="",
    )
    assert _exit_of(
        ["profile", str(table), "--out-dir", str(folder), "--replace"]
    ) == 0
    described = folder / "real-profile.json"
    assert _exit_of(
        [
            "generate",
            str(described),
            "--out-dir",
            str(folder),
            "--seed",
            seed,
            "--replace",
        ]
    ) == 0
    return table, described, folder / "real-twin.csv"


def _validated(
    described: pathlib.Path, checked: pathlib.Path, into: pathlib.Path
) -> "tuple[int, str]":
    into.mkdir(parents=True, exist_ok=True)
    code = _exit_of(
        [
            "validate",
            str(described),
            "--twin",
            str(checked),
            "--out-dir",
            str(into),
            "--replace",
        ]
    )
    return code, _one_file(into, "*quality*.txt")


# -- the gate ---------------------------------------------------------------


@pytest.mark.parametrize(
    "name,build,rows", CASES, ids=[f"{case[0]}-{case[2]}" for case in CASES]
)
def test_the_two_reports_print_one_window_and_the_faithful_twin_misses_nothing(
    tmp_path: pathlib.Path, name: str, build, rows: int
) -> None:
    """Faithful twins pass, the real table passes, and every window agrees.

    The windows are compared as the two reports PRINT them, digit for
    digit, on every rung and moment line where the quality report prints
    a window at all -- a line that holds the published value exactly is
    HELD and prints none, which is why the count compared is asserted
    separately rather than assumed to be thirteen.
    """
    cells = build(random.Random(rows * 31 + len(name)), rows)
    compared = 0
    for seed in SEEDS:
        folder = tmp_path / seed
        table, described, twin = _described_files(folder, cells, seed)
        twin_report = _one_file(folder, "*report*.txt")
        code, quality = _validated(described, twin, folder / "check-twin")
        carried = CARRIED.get((name, rows), [])
        missed = sorted(
            {line.strip().split(" [")[0] for line in _missed(quality)}
        )
        assert missed == carried, (name, rows, seed, _missed(quality))
        assert (code == 0) == (carried == []), (name, rows, seed, code)
        assert "OUTSIDE the range" not in twin_report, (name, rows, seed)
        printed = _twin_windows(twin_report)
        # Every interior rung and every moment has a window in the twin
        # report: nothing withheld on these shapes.
        assert set(printed) == set(_INTERIOR) | set(_MOMENTS), (
            name,
            rows,
            seed,
            sorted(printed),
        )
        for fact, (low, high, verdict) in _quality_windows(quality).items():
            assert printed[fact] == (low, high), (
                name,
                rows,
                seed,
                fact,
                printed[fact],
                (low, high),
                verdict,
            )
            compared += 1
        if seed == SEEDS[0]:
            code, quality = _validated(described, table, folder / "check-real")
            assert code == 0, (name, rows, "the real table", _missed(quality))
    # At least the four moments and a rung per seed were compared.
    assert compared >= 5 * len(SEEDS), (name, rows, compared)


def _scaled(cell: str, factor: float) -> str:
    """One cell with its number multiplied, written the way it was."""
    found = re.fullmatch(r"(-?\d+)(?:\.(\d+))?(.*)", cell)
    assert found is not None, cell
    number = float(found.group(1) + ("." + found.group(2) if found.group(2) else ""))
    rest = found.group(3)
    if found.group(2) is not None:
        figures = len(found.group(2))
        return f"{number * factor:.{figures}f}{rest}"
    if number % 100 == 0:
        return f"{int(round(number * factor, -2))}{rest}"
    return f"{int(round(number * factor))}{rest}"


@pytest.mark.parametrize("name,build", GATE, ids=[shape[0] for shape in GATE])
def test_a_twin_scaled_by_three_or_five_percent_is_caught_inside_the_ladder(
    tmp_path: pathlib.Path, name: str, build
) -> None:
    """The windows are honest AND they still bind (the power mutant).

    A checker whose windows only ever widen can make every twin pass. So a
    faithful twin is scaled by 1.03 and by 1.05 -- every number, written
    in its own form -- and the check must name at least one INTERIOR rung
    or moment MISSED. The two exact ends are not counted: they would catch
    any scaling on their own, and stage 3 stops publishing them exactly.
    """
    rows = 2000
    cells = build(random.Random(rows * 31 + len(name)), rows)
    table, described, twin = _described_files(tmp_path, cells, "1")
    lines = twin.read_text(encoding="utf-8").splitlines()
    for factor in (1.03, 1.05):
        scaled = tmp_path / f"scaled-{factor}.csv"
        scaled.write_text(
            fixtures.rows_to_csv(
                [lines[0]],
                [[_scaled(line.strip('"'), factor)] for line in lines[1:]],
            ),
            encoding="utf-8",
            newline="",
        )
        code, quality = _validated(
            described, scaled, tmp_path / f"check-{factor}"
        )
        caught = [
            fact
            for fact, (_low, _high, verdict) in _quality_windows(quality).items()
            if verdict == validation.MISSED
        ]
        assert code != 0, (name, factor)
        assert caught, (name, factor, _missed(quality))


def test_the_skew_range_the_residual_was_opened_on_is_printed_once(
    tmp_path: pathlib.Path,
) -> None:
    """R-P4-61's own shape: evenly spaced values, generated at seed 7.

    The twin report gave the skew range of the values 1 to 60 as
    -2.282203333063573 to 2.2822033330635745 and the quality report as
    -2.282203333063573 to 2.2822033330635754. One method, one run, two
    numbers.

    THE SAME SIXTY VALUES TWO APART (measured at the merge of the number
    review's repair into the integration). Plan P4-D147 fills a
    saturated integer grid with its integers in order, so the twin of 1
    to 60 holds every rung and every moment exactly and prints no window
    to compare; the odd numbers 1 to 119 are the same flat shape on a
    grid with room, and both reports print a skew window again. Since
    plan P4-D341 the odd numbers run to the population floor, because
    the command describes no smaller table; the shape is unchanged.
    """
    # AT THE POPULATION FLOOR (plan P4-D341): the command describes no
    # smaller table. The shape is the EVENLY SPACED odd numbers on a
    # grid with room, which is the same shape at any length, so the
    # count is read from the rule and the spacing is unchanged.
    cells = [
        str(value)
        for value in range(1, 2 * parsing.POPULATION_FLOOR + 1, 2)
    ]
    _table, described, twin = _described_files(tmp_path, cells, "7")
    printed = _twin_windows(_one_file(tmp_path, "*report*.txt"))
    code, quality = _validated(described, twin, tmp_path / "check")
    assert code == 0, _missed(quality)
    windows = _quality_windows(quality)
    assert "skew" in windows and "skew" in printed
    for fact, (low, high, _verdict) in windows.items():
        assert printed[fact] == (low, high), (fact, printed[fact], (low, high))


# -- the widest stratum, from the description alone -----------------------


def _describe(
    folder: pathlib.Path,
    name: str,
    cells: "list[str]",
    floor: int = 1,
    forced: "list[str] | None" = None,
) -> contract.ColumnBlock:
    path = fixtures.write(folder, f"{name}.csv", "value\n" + "\n".join(cells) + "\n")
    document = profile.build_document(
        reading.read_table(str(path), first_row=reading.FIRST_ROW_AUTOMATIC, small_cell_floor=floor),
        taxonomy.Settings(small_cell_floor=floor),
        [],
        forced_measurements=forced or [],
    )
    loaded = contract.load_profile(
        str(fixtures.write_profile(folder, f"{name}-profile.json", document))
    )
    return loaded.columns[0]


def _views(
    column: contract.ColumnBlock,
) -> "list[tuple[contract.ColumnBlock, contract.NumericFacts, int | None]]":
    """Every view the generator lays out with its own block, and its grain."""
    facts = column.facts
    if isinstance(facts, contract.AffixedFacts):
        return [
            (one[1], one[2], one[2].n_distinct_values)
            for one in generation._wrappers_of(facts, column)
        ]
    if isinstance(facts, contract.JoinedFacts):
        return [
            (
                generation._part_view(column, place),
                facts.parts[place],
                facts.parts[place].n_distinct_values,
            )
            for place in range(facts.n_parts)
        ]
    if isinstance(facts, contract.CompoundFacts):
        return [
            (
                contract.compound_numbers_view(column),
                facts.numbers,
                facts.numbers.n_distinct_values,
            )
        ]
    assert isinstance(facts, contract.NumericFacts), type(facts)
    return [(column, facts, None)]


def _agreement_columns(folder: pathlib.Path) -> "list[tuple[str, contract.ColumnBlock, int]]":
    draw = random.Random(2026)
    built: "list[tuple[str, contract.ColumnBlock, int]]" = []
    for name, shape in GATE:
        for rows in (500, 2000):
            built += [
                (f"{name}-{rows}", _describe(folder, f"{name}-{rows}", shape(draw, rows)), 1)
            ]
    readings = [
        (f"{value:.1f} H" if value > 11 else (f"{value:.1f} L" if value < 4 else f"{value:.1f}"))
        for value in [draw.gauss(7.5, 2.5) for _ in range(300)]
    ]
    built += [("three_wrappers", _describe(folder, "three_wrappers", readings), 1)]
    lab = [
        "NOT DETECTED" if draw.random() < 0.15 else "%.2f" % draw.lognormvariate(0, 0.5)
        for _ in range(2000)
    ]
    built += [("numbers_and_a_label", _describe(folder, "numbers_and_a_label", lab), 1)]
    pressure = random.Random(5)
    bp = [f"{pressure.randint(105, 145)}/{pressure.randint(65, 95)}" for _ in range(120)]
    built += [("joined", _describe(folder, "joined", bp, floor=11, forced=["value"]), 11)]
    withheld = [str(draw.randint(1, 40)) for _ in range(60)]
    built += [("withheld_mode", _describe(folder, "withheld_mode", withheld, floor=11), 11)]
    # A LARGE COLUMN WHOSE PAIR THE FLOOR WITHHOLDS (landing 2b.1, repair):
    # 2,500 thousandths hold no number eleven times, so the pair is
    # withheld and the floor, not the count or the ladder, is the cap.
    thousandths = [f"{draw.random():.3f}" for _ in range(2500)]
    built += [
        ("withheld_by_the_floor", _describe(folder, "withheld_by_the_floor", thousandths, floor=11), 11)
    ]
    signed = [f"{draw.gauss(0, 5):.1f}" for _ in range(2000)]
    built += [("signed", _describe(folder, "signed", signed), 1)]
    built += [("witness", _describe(folder, "witness", WITNESS), 1)]
    return built


def test_the_three_writings_read_one_widest_stratum_off_every_view(
    tmp_path: pathlib.Path,
) -> None:
    """Generator, validator and oracle: one number, from the block alone.

    Over plain columns, each wrapper of an affixed column (one wrapper and
    three), each position of a joined column, the numeric half of a
    compound column, and a column whose mode pair is withheld -- where
    the cap is the count and ladder bound rather than the mode count.
    """
    oracle = _oracle()
    roles: "set[str]" = set()
    withheld = 0
    floored = 0
    for name, column, floor in _agreement_columns(tmp_path):
        roles.add(type(column.facts).__name__)
        for view, facts, _grain in _views(column):
            numbers = validation._numeric_cells(facts)
            assert view.n_numeric == numbers, (name, view.n_numeric, numbers)
            ladder = list(facts.percentiles.rungs[:1])
            rungs: "dict[int, float | None]" = {}
            for index in range(len(contract.LADDER_PERCENTS)):
                rungs[contract.LADDER_PERCENTS[index]] = facts.percentiles.rungs[index]
            for index in range(len(contract.FINER_LADDER_KEYS)):
                key = contract.FINER_LADDER_KEYS[index]
                rungs[int(key[1:])] = facts.percentiles_between[index]
            ladder = [rungs[percent] for percent in range(101)]
            assert None not in ladder, name
            bound = oracle.stratum_cap(
                {
                    "mode": facts.mode,
                    "mode_count": facts.mode_count,
                    "n_distinct_values": facts.n_distinct_values,
                },
                ladder,
                numbers,
                floor,
            )
            third = bound if bound > 0 else numbers
            first = generation._window_stratum(view, facts, floor)
            second = validation._window_stratum(facts, floor)
            assert first == second == third, (name, first, second, third)
            if facts.mode is None:
                withheld += 1
                # THE FLOOR BINDS HERE, and no number of the column was
                # held by `floor` cells, which is what the pair's absence
                # proves.
                if validation._stratum_bound(facts, 1) > second:
                    floored += 1
                    assert second <= floor - 1, (name, second, floor)
    assert {"NumericFacts", "AffixedFacts", "JoinedFacts", "CompoundFacts"} <= roles
    assert withheld >= 1
    assert floored >= 1, "no column here is capped by its publication floor"


# The 12-row column the search found: seven cells of -29 and one of -28
# beside a zero and three positive cells. Its `mode_count` is 7, and the
# band share gave the negatives ONE stratum, which then held eight cells.
WITNESS = [
    "-28", "-29", "30", "-29", "-29", "0", "-29", "-29", "30", "-29", "-29", "26",
]


def test_no_band_gets_fewer_strata_than_its_cells_need_under_the_cap(
    tmp_path: pathlib.Path,
) -> None:
    """G5.2b's floor, on the witness, in the generator and in the oracle."""
    column = _describe(tmp_path, "witness", WITNESS)
    facts = column.facts
    assert isinstance(facts, contract.NumericFacts)
    assert facts.mode_count == 7 and facts.n_negative == 8
    layout, _notes, _content = generation._numeric_layout(column, facts, None, 1)
    assert max(layout.sizes) <= 7, layout.sizes
    negative = len([band for band in layout.bands if band == "negative"])
    positive = len([band for band in layout.bands if band == "positive"])
    assert (negative, positive) == (2, 2), layout.bands
    oracle = _oracle()
    ladder = list(generation._merged_rungs(facts) or ())
    assert oracle.band_strata(
        8, 1, 3, 5, ladder, 12, True, -1, oracle.stratum_cap(
            {"mode": facts.mode, "mode_count": facts.mode_count,
             "n_distinct_values": facts.n_distinct_values},
            ladder,
            12,
            1,
        )
    ) == (negative, positive)


def test_no_stratum_stands_above_the_window_where_no_carrier_moves_a_cell(
    tmp_path: pathlib.Path,
) -> None:
    """The promise the shared window rests on, over randomised columns.

    Mixed signs, a few numbers with very uneven counts, whole numbers and
    one or two figures, raised floors. Where the column publishes whole
    numbers or no point-free count, G5.2b's carrier and reach steps move
    no cell, and no stratum may hold more than the window reads.
    """
    draw = random.Random(20260915)
    checked = 0
    for trial in range(160):
        rows = draw.choice([12, 20, 40, 80, 150, 400])
        kind = draw.choice(["whole", "one", "two"])
        centres = sorted(draw.uniform(-50, 50) for _ in range(draw.choice([2, 3, 5, 8, 20])))
        weights = [draw.paretovariate(1.0) for _ in centres]
        cells: "list[str]" = []
        for _ in range(rows):
            value = draw.choices(centres, weights)[0] + draw.gauss(0, draw.choice([0, 0.3, 3]))
            if draw.random() < 0.1:
                value = 0.0
            if kind == "whole":
                cells += [str(int(round(value)))]
            elif kind == "one":
                cells += [f"{value:.1f}"]
            else:
                cells += [f"{value:.2f}"]
        chosen = draw.choice([1, 1, 5, 11])
        column = _describe(tmp_path, f"t{trial}", cells, floor=chosen)
        facts = column.facts
        if not isinstance(facts, contract.NumericFacts):
            continue
        if not facts.integer_valued and generation._whole_demand(facts) > 0:
            continue
        layout, _notes, _content = generation._numeric_layout(column, facts, None, chosen)
        widest = generation._window_stratum(column, facts, chosen)
        assert max(layout.sizes) <= widest, (trial, cells, layout.sizes, widest)
        checked += 1
    column = _describe(tmp_path, "witness", WITNESS)
    assert isinstance(column.facts, contract.NumericFacts)
    layout, _notes, _content = generation._numeric_layout(column, column.facts, None, 1)
    assert max(layout.sizes) <= generation._window_stratum(column, column.facts, 1)
    assert checked >= 100, checked


# -- the one operation order ------------------------------------------------


def test_the_moment_windows_are_one_computation_bit_for_bit() -> None:
    """G12.3 and G12.3a, as the two modules compute them from one rank form.

    Random rank windows over columns of very different scales, signs and
    lengths. Every end of the mean, skew and kurtosis windows is compared
    for equality, not closeness: the reports print them in full.
    """
    draw = random.Random(61)
    compared = 0
    for _trial in range(400):
        held = draw.randint(4, 80)
        scale = 10 ** draw.randint(-3, 6)
        middles = sorted(draw.gauss(0, 1) * scale + draw.choice([0, scale * 5]) for _ in range(held))
        lows = [value - abs(draw.gauss(0, 0.2)) * scale for value in middles]
        highs = [value + abs(draw.gauss(0, 0.2)) * scale for value in middles]
        lows = sorted(lows)
        highs = sorted(highs)
        middles = [min(max(middles[k], lows[k]), highs[k]) for k in range(held)]
        theirs = validation._moment_windows(lows, highs, middles, held)
        steps = [max(middles[k] - lows[k], highs[k] - middles[k]) for k in range(held)]
        reach = generation._root_mean_square(steps)
        assert theirs["mean"] == (generation._average(lows), generation._average(highs))
        spread = taxonomy.spread_of(list(middles))
        assert spread is not None
        room = reach * math.sqrt(held / (held - 1))
        assert theirs["std"] == (max(0.0, spread - room), spread + room)
        assert theirs["skew"] == generation._shape_window(lows, highs, middles, reach, held)
        assert theirs["kurtosis"] == generation._tails_window(
            lows, highs, middles, reach, held
        )
        compared += 1
    assert compared == 400


def test_the_rung_windows_read_the_ladder_at_one_exact_share(
    tmp_path: pathlib.Path,
) -> None:
    """G12.2's rung form: the same fraction, read the same way, both sides."""
    column = _describe(tmp_path, "weight", _weight(random.Random(3), 1500))
    facts = column.facts
    assert isinstance(facts, contract.NumericFacts)
    twin = generation.generate(
        contract.load_profile(str(tmp_path / "weight-profile.json")), 4
    )
    made = {
        one.fact.split(".")[-1]: (one.lowest, one.highest)
        for one in twin.approximations
        if one.fact.startswith("percentiles.p")
    }
    measured = validation.measure(
        contract.load_profile(str(tmp_path / "weight-profile.json")),
        str(fixtures.write(tmp_path, "twin.csv", rendering.twin_csv(twin))),
    )
    seen = 0
    for check in measured.checks:
        found = re.search(r"\(between (\S+) and (\S+)\)$", check.published)
        if check.subcheck.startswith("ladder.p") and found:
            assert made[check.subcheck.split(".")[-1]] == (found.group(1), found.group(2))
            seen += 1
    assert seen >= 5, seen


def test_a_withheld_style_share_widens_both_windows_alike(
    tmp_path: pathlib.Path,
) -> None:
    """The half unit G12.2 grants, counted the same way by both reports.

    Six whole-number cells beside three hundred of tenths, at a floor of
    eleven: the `plain` count is too small to publish and becomes a
    withheld share, which G6.4 writes plain. The twin report granted the
    half unit for it and the quality report, looking for a `plain` key,
    did not -- so every window of such a column was half a unit apart.
    """
    draw = random.Random(11)
    # TEN TENTHS, TEN WHOLE NUMBERS AND TEN EXPONENT CELLS (plans P4-D221
    # and P4-D222; stage 2 closed by the owner rulings of 2026-09-17). Three
    # hundred tenths beside them now count the rare forms into the tenths,
    # and a withheld share stands only where no form reaches the line:
    # thirty cells at a floor of eleven are one pool of every form.
    cells = [f"{draw.gauss(80, 16):.1f}" for _ in range(10)]
    cells += [str(draw.randint(60, 100)) for _ in range(10)]
    cells += [f"{draw.randint(60, 100)}e0" for _ in range(10)]
    column = _describe(tmp_path, "withheld_style", cells, floor=11)
    facts = column.facts
    assert isinstance(facts, contract.NumericFacts)
    assert contract.WITHHELD in facts.numeric_styles
    assert "plain" not in facts.numeric_styles
    assert validation._half_unit(facts) == 0.5
    described = contract.load_profile(str(tmp_path / "withheld_style-profile.json"))
    twin = generation.generate(described, 2)
    made = {
        one.fact.split(".")[-1]: (one.lowest, one.highest)
        for one in twin.approximations
    }
    measured = validation.measure(
        described, str(fixtures.write(tmp_path, "twin.csv", rendering.twin_csv(twin)))
    )
    seen = 0
    for check in measured.checks:
        found = re.search(r"\(between (\S+) and (\S+)\)$", check.published)
        head = check.subcheck.split(".")[0]
        if found and head in ("ladder", "moments"):
            last = check.subcheck.split(".")[-1]
            assert made[last] == (found.group(1), found.group(2)), check.subcheck
            seen += 1
    # EIGHT on the pooled column of thirty, where the column of 311 showed
    # ten or more (plan P4-D222): a short column interpolates fewer rungs.
    assert seen >= 8, seen


# -- the written grid and the nearest giver (landing 2b.1, repair) ----------


def _dropped_zero(text: str) -> str:
    """A number as a spreadsheet writes it: `37.0` becomes `37`."""
    return text.rstrip("0").rstrip(".") if "." in text else text


def test_the_generator_and_the_oracle_read_one_integer_grid(
    tmp_path: pathlib.Path,
) -> None:
    """A whole-valued column is on the integers in BOTH writings (P4-D66.3).

    THE MIRROR WAS PINNED BY NOTHING, and a mutation check is what
    found it: withdrawing this rule from the oracle left all 365 tests
    of the reference and agreement files passing, because no committed
    frozen case has a whole-valued column with a NON-EMPTY fraction
    census and both writings agree on every other shape.

    That census is the shape the rule turns on. A column a spreadsheet
    exported as `44.0` publishes `integer_valued: true` AND a census of
    one figure, and both writings used to read the census first -- so
    both put the column on the grid of tenths, and the separation walk
    moved a stratum onto a value no whole-number column holds. The
    control below is the same census on a column that is NOT whole,
    where the census IS the grid, so the test can tell the rule from
    its absence.
    """
    oracle = _oracle()
    draw = random.Random(11)
    whole = [f"{draw.randrange(10, 90)}.0" for _ in range(600)]
    column = _describe(tmp_path, "whole_with_width", whole)
    facts = column.facts
    assert isinstance(facts, contract.NumericFacts)
    assert facts.integer_valued is True
    assert facts.fraction_widths == {"1": 600}, dict(facts.fraction_widths)
    assert generation._pinned_fraction(column, facts) == 0
    assert (
        oracle.grid_of(
            dict(facts.fraction_widths), facts.integer_valued, column.n_numeric
        )
        == 0
    )
    # THE CONTROL: the same census, values that are not whole. Here the
    # census is the grid, and both writings must still say so.
    tenths = [f"{draw.gauss(37, 0.5):.1f}" for _ in range(600)]
    other = _describe(tmp_path, "tenths_control", tenths)
    theirs = other.facts
    assert isinstance(theirs, contract.NumericFacts)
    assert theirs.integer_valued is False
    assert generation._pinned_fraction(other, theirs) == 1
    assert (
        oracle.grid_of(
            dict(theirs.fraction_widths), theirs.integer_valued, other.n_numeric
        )
        == 1
    )


def test_the_generator_and_the_oracle_read_one_written_grid(
    tmp_path: pathlib.Path,
) -> None:
    """G5.2a step 1's grid, read by both writings off described columns.

    A column of tenths, one of tenths written as a spreadsheet writes them
    (`37` beside `37.4`), a zero-inflated one, a column of two widths, a
    whole-number one and one whose point-free cells are too few to be the
    rest of the column: the first three are on a grid of one figure and
    the last three on none.
    """
    oracle = _oracle()
    draw = random.Random(7)
    shapes = {
        "tenths": ([f"{draw.gauss(37, 0.5):.1f}" for _ in range(600)], 1),
        "spreadsheet": ([_dropped_zero(f"{draw.gauss(37, 0.5):.1f}") for _ in range(600)], 1),
        "zero_inflated": (
            ["0" if draw.random() < 0.3 else f"{draw.lognormvariate(1, 0.6):.1f}" for _ in range(600)],
            1,
        ),
        # Two widths are the grid of the commonest since the stage-2b
        # integration (G5.2a step 1): here the two-place cells are.
        "two_widths": (
            [_dropped_zero(f"{round(draw.lognormvariate(1.5, 0.6) * 4) / 4:.2f}") for _ in range(600)],
            2,
        ),
        "whole": ([str(int(draw.gauss(70, 9))) for _ in range(600)], -1),
        "plus_signs": (
            [(f"+{draw.randint(1, 9)}" if draw.random() < 0.2 else f"{draw.gauss(5, 2):.1f}") for _ in range(600)],
            1,
        ),
    }
    for name, (cells, expected) in shapes.items():
        column = _describe(tmp_path, name, cells)
        facts = column.facts
        assert isinstance(facts, contract.NumericFacts), (name, type(facts))
        mine = generation._written_grid(column, facts)
        theirs = oracle.written_grid(
            dict(facts.fraction_widths),
            facts.integer_valued,
            column.n_numeric,
            oracle.named_point_free(dict(facts.numeric_styles)),
        )
        assert mine == theirs == expected, (name, mine, theirs, dict(facts.fraction_widths))

    # AND A COLUMN WHOSE POINT-FREE CELLS ARE AN ANONYMOUS POOL (landing
    # 2b.7). Ten `-1e-2` cells under a floor of eleven are pooled, so the
    # styles map NAMES no point-free form at all: 490 cells at one width
    # do not cover the column, and neither writing may read a grid. Read
    # off the pooled share instead, both would read the grid of tenths,
    # which `-0.01` is not a point of.
    # ...and one `-1E-2` (plan P4-D221). SINCE PLAN P4-D222 (stage 2 closed
    # by the owner rulings of 2026-09-17) the eleven are counted into the
    # decimals, and the width census is one pool: its minimum, -0.01, needs
    # two figures after the point, which no width it names holds.
    pooled = (
        [f"{draw.gauss(37, 0.5):.1f}" for _ in range(490)]
        + ["-1e-2"] * 10
        + ["-1E-2"]
    )
    column = _describe(tmp_path, "withheld_pool", pooled, floor=11)
    facts = column.facts
    assert isinstance(facts, contract.NumericFacts)
    assert dict(facts.numeric_styles) == {"decimal": 501}, dict(facts.numeric_styles)
    assert dict(facts.fraction_widths) == {"(withheld)": 501}, dict(facts.fraction_widths)
    mine = generation._written_grid(column, facts)
    theirs = oracle.written_grid(
        dict(facts.fraction_widths),
        facts.integer_valued,
        column.n_numeric,
        oracle.named_point_free(dict(facts.numeric_styles)),
    )
    assert mine == theirs == -1, (mine, theirs)


def test_the_nearest_giver_is_one_rule_in_the_generator_and_the_oracle() -> None:
    """G5.2's cell step on a written grid, generator against oracle.

    Random bands of strata with random point-free demands. On a written
    grid each taker takes its even share from the nearest givers, the
    lower of two equally near; off a grid the cells still come from the
    lowest strata upward, and both writings must agree on both.
    """
    oracle = _oracle()
    draw = random.Random(20260916)
    moved_near = 0
    for trial in range(600):
        count = draw.randint(3, 40)
        sizes = [draw.choice([1, 1, 2, 3, 5, 8, 13, 40]) for _ in range(count)]
        bands = ["positive"] * count
        ladder = sorted(round(draw.uniform(0.1, 60.0), 1) for _ in range(101))
        cells = sum(sizes)
        plain = draw.randint(0, cells)
        published = {"plain": plain, "decimal": cells - plain}
        for grid in (-1, 1):
            flags = generation._carrier_flags(sizes, bands, tuple(ladder), False)
            mine = generation._carrier_sizes(list(sizes), bands, flags, plain, 0, grid)
            theirs = oracle.carrier_split(
                list(sizes), bands, ladder, False, published, 0, cells, grid
            )
            assert mine == theirs, (trial, grid, sizes, plain, mine, theirs)
            if grid == 1 and mine != generation._carrier_sizes(
                list(sizes), bands, flags, plain, 0, -1
            ):
                moved_near += 1
    # Measured: the nearest order changes the answer on 25 of the 600.
    assert moved_near >= 20, moved_near


def test_a_withheld_pair_the_description_contradicts_is_not_read_as_the_floor(
    tmp_path: pathlib.Path,
) -> None:
    """The floor term of G5.2a's cap, and its two exceptions, in all three.

    A withheld pair under a floor of 11 caps every stratum at 10. But a
    description whose COUNT OF DIFFERENT NUMBERS leaves the commonest
    holding 11 cells or more proves a number held that often, so the pair
    was not withheld by the floor and the term stands aside. The columns
    are described and then have their pair withheld by hand, which is
    exactly the contradiction no profiler writes.

    A FLAT LADDER IS NO LONGER ONE OF THOSE PROOFS (Codex review of
    landing 2b.1, item 2). It was, and it was wrong: rungs are compared as
    binary64, so a run of equal rungs proves that many equal ROUNDED
    values and says nothing about how often one exact value was held. The
    companion test below builds the column that separates the two.

    AND THE HEAP READING HAS TO BE CLOSED BEFORE THE FLOOR TERM CAN
    STAND (method G5.2a-2, stage 3 landing 3.5). The pair is withheld
    on a second ground now -- a count whose complement against the
    numbers the statistics used is a group below the line -- so a
    withheld pair proves the SMALL reading only where the other bounds
    already put the cap at or below `K - L`. The flat column is
    therefore 60 cells of one value among 85 rather than among 66: at
    66 the count bound is 60 and `K - L` is 55, so the withheld pair is
    the heap reading and proves nothing, which is a true answer to a
    different question than this test asks.
    """
    oracle = _oracle()
    draw = random.Random(11)
    free = [f"{draw.random():.3f}" for _ in range(900)]
    flat = ["5"] * 60 + [str(value) for value in range(6, 31)]
    few = [str(draw.randint(1, 30)) for _ in range(400)]
    outcomes = {}
    for name, cells in (("free", free), ("flat", flat), ("few", few)):
        column = _describe(tmp_path, name, cells, floor=11)
        facts = column.facts
        assert isinstance(facts, contract.NumericFacts), name
        facts = dataclasses.replace(facts, mode=None, mode_count=0)
        numbers = validation._numeric_cells(facts)
        rungs = generation._merged_rungs(facts)
        assert rungs is not None, name
        first = generation._stratum_cap(facts, rungs, numbers, 11)
        second = validation._stratum_bound(facts, 11)
        third = oracle.stratum_cap(
            {"mode": None, "mode_count": 0, "n_distinct_values": facts.n_distinct_values},
            list(rungs),
            numbers,
            11,
        )
        assert first == second == third, (name, first, second, third)
        outcomes[name] = (first, generation._stratum_cap(facts, rungs, numbers, 1))
    assert outcomes["free"][0] == 10, outcomes
    # THE COUNT OF DIFFERENT NUMBERS IS THE PROOF THAT SURVIVES: 400 cells
    # over thirty numbers hold one of them at least fourteen times, so that
    # description's pair was not withheld by the floor.
    assert outcomes["few"][0] == outcomes["few"][1], outcomes
    assert outcomes["few"][1] > 10, outcomes
    # AND THE FLAT LADDER IS NO LONGER A PROOF: its own count of different
    # numbers does not reach the floor, so the floor binds after all.
    assert outcomes["flat"][0] == 10, outcomes
    assert outcomes["flat"][1] > 10, outcomes


def test_equal_rounded_rungs_prove_no_exact_identity(
    tmp_path: pathlib.Path,
) -> None:
    """A producer-valid description whose ladder is flat only by rounding.

    THE COLUMN THE WITHDRAWN RULE GOT WRONG (Codex review of landing 2b.1,
    item 2). A hundred exact decimals `1.0000000000000001` upward, four
    cells each: every one is a different number, none is held by more than
    four cells, and the profiler withholds the mode pair because four is
    under the floor of eleven. Every rung of the ladder is nevertheless
    EQUAL, because the hundred decimals round to one binary64 value.

    Read as proof, that flat run said some number was held eleven times or
    more and stood the floor term aside, capping a stratum at 21 where the
    withheld pair proves 10. Nothing is hand-contradicted here: this is a
    description the producer writes.
    """
    oracle = _oracle()
    cells = [f"1.{place:016d}" for place in range(1, 101) for _each in range(4)]
    column = _describe(tmp_path, "rounded", cells, floor=11)
    facts = column.facts
    assert isinstance(facts, contract.NumericFacts)
    assert facts.mode is None and facts.mode_count == 0
    assert facts.n_distinct_values == 100, facts.n_distinct_values
    numbers = validation._numeric_cells(facts)
    rungs = generation._merged_rungs(facts)
    assert rungs is not None
    # A HUNDRED DIFFERENT EXACT DECIMALS, and a ladder that cannot see
    # them: 101 rungs carry only 46 different binary64 values, and the
    # longest run of equal rungs is 4.
    assert len({cell for cell in cells}) == 100
    assert len(set(rungs)) < len(rungs), len(set(rungs))
    longest = 1
    run = 1
    for place in range(1, len(rungs)):
        if rungs[place] == rungs[place - 1]:
            run = run + 1
            longest = max(longest, run)
        else:
            run = 1
    assert longest == 4, longest
    # THE WITHDRAWN PROOF WOULD HAVE STOOD THE FLOOR ASIDE, and the
    # count of different numbers does not: that is the whole of the
    # defect, written as arithmetic so the gate cannot drift from it.
    assert ((longest - 1) * (numbers - 1)) // 100 >= 11
    assert -((-numbers) // facts.n_distinct_values) == 4
    first = generation._stratum_cap(facts, rungs, numbers, 11)
    second = validation._stratum_bound(facts, 11)
    third = oracle.stratum_cap(
        {
            "mode": None,
            "mode_count": 0,
            "n_distinct_values": facts.n_distinct_values,
        },
        list(rungs),
        numbers,
        11,
    )
    assert first == second == third == 10, (first, second, third)
