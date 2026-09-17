"""A column written at several fraction widths is on its commonest one's grid.

THE DEFECT, AS MEASURED (repair of the stage-2b integration; method
G5.2a step 1). A census naming more than one width was read as no grid,
the ladder was interpolated continuously, and the writer met the census
with whatever values it had: 400 one-place readings with one cell
written `4.20` came back holding `5.020207149207973` six times and 26
different numbers against 27, exit 3 at every floor, while the real
table passed. Money written by the shortest round trip did the same.

Held here: that twin misses nothing at a floor of one, and the real table
none at eleven; the
implementation and the method oracle choose the same grid on every
census a battery of real descriptions publishes; and a census the rule
must not read as a grid is refused by both.
"""

import contextlib
import importlib.util
import io
import json
import pathlib
import random
import sys

import pytest

import fixtures
from synthtwin import contract, generation

REPOSITORY = pathlib.Path(__file__).resolve().parent.parent
ORACLE = REPOSITORY / "tools" / "reference" / "make_generation_reference_vectors.py"


def _oracle():
    spec = importlib.util.spec_from_file_location("oracle_width_grid", ORACLE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _exit_of(argv: "list[str]") -> int:
    from synthtwin import cli

    before = sys.argv
    sys.argv = ["synthtwin"] + argv
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = cli.main()
    except SystemExit as stop:
        return 0 if stop.code is None else int(stop.code)
    finally:
        sys.argv = before
    return code


def _readings() -> "list[str]":
    draw = random.Random(3)
    cells = [f"{draw.gauss(4.2, 0.5):.1f}" for _cell in range(400)]
    cells[10] = cells[10] + "0"
    return cells


@pytest.mark.parametrize("floor", ["1", "11"])
def test_one_padded_reading_no_longer_costs_the_twin_its_widths(
    tmp_path: pathlib.Path, floor: str
) -> None:
    """At a floor of one the twin is on the grid; at eleven the real table passes.

    At eleven the census pools the `4.20` cell, and a pooled width is not
    read as a grid, so only the validator's half of the repair -- the
    pool permits its own count of unnamed widths -- is held there.
    """
    table = fixtures.write(
        tmp_path, "readings.csv", fixtures.single_column_table("k", _readings())
    )
    assert _exit_of(["profile", str(table), "--out-dir", str(tmp_path),
                     "--smallest-group", floor]) == 0
    described = tmp_path / "readings-profile.json"
    real = tmp_path / "real"
    real.mkdir()
    assert _exit_of(["validate", str(described), "--twin", str(table),
                     "--out-dir", str(real)]) == 0
    if floor != "1":
        return
    assert _exit_of(["generate", str(described), "--out-dir", str(tmp_path),
                     "--seed", "1"]) == 0
    twin = tmp_path / "readings-twin.csv"
    cells = twin.read_text(encoding="utf-8").splitlines()[1:]
    assert all(len(cell.split(".")[-1]) <= 2 for cell in cells), cells[:5]
    checked = tmp_path / "checked"
    checked.mkdir()
    assert _exit_of(["validate", str(described), "--twin", str(twin),
                     "--out-dir", str(checked)]) == 0


def _battery() -> "list[list[str]]":
    columns: "list[list[str]]" = []
    for seed in range(24):
        draw = random.Random(seed)
        size = draw.choice((60, 200))
        kind = seed % 6
        cells: "list[str]" = []
        for _cell in range(size):
            if kind == 0:
                cells += [repr(round(draw.lognormvariate(3, 1), 2))]
            elif kind == 1:
                cells += [f"{draw.gauss(4, 1):.1f}" + ("0" if draw.random() < 0.1 else "")]
            elif kind == 2:
                cells += ["0" if draw.random() < 0.3 else repr(round(draw.random() * 9, 2))]
            elif kind == 3:
                cells += [f"{draw.gauss(50, 9):.{draw.choice((1, 2, 3))}f}"]
            elif kind == 4:
                cells += [repr(round(draw.gauss(2, 0.7), 3))]
            else:
                cells += [f"{draw.gauss(8, 2):.2f}" if draw.random() < 0.5 else f"{draw.randrange(20)}"]
        columns += [cells]
    return columns


def test_the_implementation_and_the_oracle_choose_the_same_grid(
    tmp_path: pathlib.Path,
) -> None:
    oracle = _oracle()
    several = 0
    for index, cells in enumerate(_battery()):
        for floor in ("1", "11"):
            stem = f"b{index}f{floor}"
            table = fixtures.write(
                tmp_path, f"{stem}.csv", fixtures.single_column_table("v", cells)
            )
            assert _exit_of(["profile", str(table), "--out-dir", str(tmp_path),
                             "--smallest-group", floor]) == 0
            path = tmp_path / f"{stem}-profile.json"
            document = json.loads(path.read_text(encoding="utf-8"))
            block = document["columns"][0]
            if "fraction_widths" not in block:
                continue
            loaded = contract.load_profile(str(path))
            column = loaded.columns[0]
            facts = column.facts
            assert isinstance(facts, contract.NumericFacts)
            widths = block["fraction_widths"]
            if len(widths) > 1:
                several = several + 1
            expected = oracle.written_grid(
                widths,
                block["integer_valued"],
                block["n_numeric"],
                oracle.named_point_free(block["numeric_styles"]),
            )
            assert generation._written_grid(column, facts) == expected, (
                stem, widths, block["numeric_styles"],
            )
    assert several >= 20, several


def test_a_census_that_does_not_cover_the_column_is_no_grid() -> None:
    """A width census short of the numeric cells names no grid in the oracle."""
    oracle = _oracle()
    assert oracle.commonest_width_grid({"1": 300, "2": 50}, 400, 50) == 1
    assert oracle.commonest_width_grid({"1": 300, "2": 50}, 400, 0) == -1
    assert oracle.commonest_width_grid({"1": 100, "2": 100}, 200, 0) == 2
    assert oracle.commonest_width_grid({"(withheld)": 5, "3": 95}, 100, 0) == -1
