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

import importlib.util
import math
import pathlib
import random
import re

import pytest

from synthtwin import contract, generation, profile, reading, rendering
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

# ONE GATE CASE MISSES ONE OBLIGATION THAT IS NOT A WINDOW, and it is
# pinned here by name rather than left out. The 2,000-row uniform column
# publishes 862 different numbers and its twin holds 861 at every seed:
# its first positive stratum's grid value reads as `0.000`, method G5.5's
# sign repair sends it to the published maximum `1.000`, and G6.5a's
# separation walk cannot bring it back, because every grid point within
# its reach is held. The same shortfall of one number is measured on
# one-figure columns that cross zero at 2,000 and 4,000 rows. It belongs
# to part 1's grid value rule and G6.5a, not to the windows, and it is
# carried in the landing's report. The assertion below turns red the
# moment it is repaired, so this entry cannot outlive the defect.
CARRIED = {("uniform_three_figures", 2000): ["distinct.n_distinct_values"]}

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
    """R-P4-61's own witness: the values 1 to 60, generated at seed 7.

    The twin report gave the skew range as -2.282203333063573 to
    2.2822033330635745 and the quality report as -2.282203333063573 to
    2.2822033330635754. One method, one run, two numbers.
    """
    cells = [str(value) for value in range(1, 61)]
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
        reading.read_table(str(path), first_row=reading.FIRST_ROW_AUTOMATIC),
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


def _agreement_columns(folder: pathlib.Path) -> "list[tuple[str, contract.ColumnBlock]]":
    draw = random.Random(2026)
    built: "list[tuple[str, contract.ColumnBlock]]" = []
    for name, shape in GATE:
        for rows in (500, 2000):
            built += [(f"{name}-{rows}", _describe(folder, f"{name}-{rows}", shape(draw, rows)))]
    readings = [
        (f"{value:.1f} H" if value > 11 else (f"{value:.1f} L" if value < 4 else f"{value:.1f}"))
        for value in [draw.gauss(7.5, 2.5) for _ in range(300)]
    ]
    built += [("three_wrappers", _describe(folder, "three_wrappers", readings))]
    lab = [
        "NOT DETECTED" if draw.random() < 0.15 else "%.2f" % draw.lognormvariate(0, 0.5)
        for _ in range(2000)
    ]
    built += [("numbers_and_a_label", _describe(folder, "numbers_and_a_label", lab))]
    pressure = random.Random(5)
    bp = [f"{pressure.randint(105, 145)}/{pressure.randint(65, 95)}" for _ in range(120)]
    built += [("joined", _describe(folder, "joined", bp, floor=11, forced=["value"]))]
    withheld = [str(draw.randint(1, 40)) for _ in range(60)]
    built += [("withheld_mode", _describe(folder, "withheld_mode", withheld, floor=11))]
    signed = [f"{draw.gauss(0, 5):.1f}" for _ in range(2000)]
    built += [("signed", _describe(folder, "signed", signed))]
    built += [("witness", _describe(folder, "witness", WITNESS))]
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
    for name, column in _agreement_columns(tmp_path):
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
            )
            third = bound if bound > 0 else numbers
            first = generation._window_stratum(view, facts)
            second = validation._window_stratum(facts)
            assert first == second == third, (name, first, second, third)
            if facts.mode is None:
                withheld += 1
    assert {"NumericFacts", "AffixedFacts", "JoinedFacts", "CompoundFacts"} <= roles
    assert withheld >= 1


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
    layout, _notes, _content = generation._numeric_layout(column, facts, None)
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
        column = _describe(tmp_path, f"t{trial}", cells, floor=draw.choice([1, 1, 5, 11]))
        facts = column.facts
        if not isinstance(facts, contract.NumericFacts):
            continue
        if not facts.integer_valued and generation._whole_demand(facts) > 0:
            continue
        layout, _notes, _content = generation._numeric_layout(column, facts, None)
        widest = generation._window_stratum(column, facts)
        assert max(layout.sizes) <= widest, (trial, cells, layout.sizes, widest)
        checked += 1
    column = _describe(tmp_path, "witness", WITNESS)
    assert isinstance(column.facts, contract.NumericFacts)
    layout, _notes, _content = generation._numeric_layout(column, column.facts, None)
    assert max(layout.sizes) <= generation._window_stratum(column, column.facts)
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
    cells = [f"{draw.gauss(80, 16):.1f}" for _ in range(300)]
    cells += [str(draw.randint(60, 100)) for _ in range(6)]
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
    assert seen >= 10, seen
