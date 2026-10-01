"""A declared record number counting from nought keeps its layout census.

THE DEFECT, AS MEASURED (repair of the stage-2b integration). Method
G9.6 writes a whole-number record number in the figures band with no
leading nought, so that its length is its count of figures -- and the
rule was applied to the lone figure `0` as well, which leads nothing.
The band therefore held nine one-figure values where there are ten. A
declared column `0` to `119` holds ten one-figure values, ninety of two
figures and twenty of three; at a smallest group of ten it publishes
`layout_forms {'%%%': 20}` and holds the rest back, and the twin, able
to write only nine short values, spilled the tenth into three figures:
`%%%` asked 20 and held 21, twin exit 3. The same count showed as 200
against 201 in `tests/test_stage2_timestamp_spellings.py`.

Both halves of the rule are held here: the generator, through the
commands a person runs, and the independent oracle, from its path.
"""

import contextlib
import importlib.util
import io
import pathlib
import sys

REPOSITORY = pathlib.Path(__file__).resolve().parent.parent
ORACLE = REPOSITORY / "tools" / "reference" / "make_generation_reference_vectors.py"


def _exit_of(argv: "list[str]") -> int:
    """Run one synthtwin command in this process, quietly."""
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


def _missed(folder: pathlib.Path) -> "list[str]":
    lines: "list[str]" = []
    for report in sorted(folder.glob("*.txt")):
        for line in report.read_text(encoding="utf-8").splitlines():
            if line.rstrip().endswith("MISSED"):
                lines += [line.strip()]
    return lines


def test_a_record_number_counting_from_nought_meets_its_layout_census(
    tmp_path: pathlib.Path,
) -> None:
    """The measured column: `0` to `119` beside `1` to `120`, both declared."""
    table = tmp_path / "pairs.csv"
    table.write_bytes(
        (
            "first_id,second_id\n"
            + "".join(f"{i},{i + 1}\n" for i in range(120))
        ).encode("utf-8")
    )
    assert _exit_of([
        "profile", str(table), "--out-dir", str(tmp_path),
        "--identifier", "first_id", "--identifier", "second_id",
        "--smallest-group", "10",
    ]) == 0
    described = tmp_path / "pairs-profile.json"
    assert _exit_of([
        "generate", str(described), "--out-dir", str(tmp_path), "--seed", "4",
    ]) == 0
    twin = tmp_path / "pairs-twin.csv"
    cells = [
        line.split(",")[0]
        for line in twin.read_text(encoding="utf-8").splitlines()[1:]
    ]
    assert sum(1 for cell in cells if len(cell) == 3) == 20
    assert "0" in cells
    checked = tmp_path / "checked"
    checked.mkdir()
    code = _exit_of([
        "validate", str(described), "--twin", str(twin),
        "--out-dir", str(checked),
    ])
    assert code == 0, _missed(checked)


def test_the_oracle_writes_ten_one_figure_whole_numbers() -> None:
    """The oracle's figures band holds `0` to `99` in two figures or fewer.

    A hundred distinct whole numbers of one or two figures exist only if
    the lone nought is one of them; the withdrawn reading held ninety-nine
    and could not build this column at all within its published length.
    """
    spec = importlib.util.spec_from_file_location("oracle_lone_nought", ORACLE)
    oracle = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(oracle)
    column = oracle._universal(
        "column_1", "identifier", "code", "identifier", "ok",
        n_present=100, n_missing=0, n_distinct=100, n_distinct_folded=100,
        n_numeric=100, n_not_numeric=0, n_out_of_range=0, n_contradictory=0,
        min_length=1, max_length=2, all_whole_numbers=True,
        n_all_digits=100, n_code_alphabet=100,
        n_distinct_by_occurrences={"1": 100},
    )
    cells = oracle._identifier_content(column)
    assert sorted(cells, key=lambda cell: (len(cell), cell)) == [
        f"{number}" for number in range(100)
    ]
