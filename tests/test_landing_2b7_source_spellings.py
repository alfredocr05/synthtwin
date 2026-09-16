"""Landing 2b.7 part 2: a real export meets its own description.

THREE DEFECTS THESE TESTS CLOSE, every one of them reproduced on this
branch before anything changed, over 800-row columns at two generation
seeds.

1. A REAL TABLE FAILED ITS OWN DESCRIPTION (plan P4-D66.2; audit items
   NC-1, NC-2, NC-6, NC-12 and the missed item M2). Describe a real
   Excel export of `2.29E+05`, a SAS `E10.4` export of `7.2960E+02`, a
   Fortran-style `6E9`, a Stata export of `.05`, or a column of
   seventeen-figure accession numbers, and then validate THAT FILE
   against the description it just produced: exit 3, `styles.spelled`
   MISSED, and the report withholds which cells failed. Seven shapes,
   fourteen runs, every one of them accusing a file this tool was
   pointed at. The spellings are all spellings of the values the cells
   read back as -- a mantissa padded to a fixed count of figures, an
   exponent written without its `+`, a value below one written without
   its leading `0`, and the figures of a whole number past what
   binary64 keeps.

2. A WHOLE-NUMBER COLUMN CAME BACK NOT WHOLE (plan P4-D66.3; audit item
   NC-10). A column pandas exported as `44.0` publishes every value
   whole AND every cell one figure wide, and the separation walk read
   the width instead of the wholeness: it moved strata onto `25.6`, and
   the twin re-described itself as a `continuous` column where the
   source was a `count` -- `axes.role`, `axes.statistical_type` and
   `type.integer_valued` all MISSED, 23 cells of 800 at seed 1.

3. A PADDED CELL OVERFLOWED ITS OWN FIELD (plan P4-D66.4; the audit's
   missed item M4). A column of month codes `01` to `12`, every cell
   two characters, came back holding `012` -- three characters in a
   two-character field.

Every test here drives the real command line in this process: describe
a realistic table, build the twin, describe the TWIN again, and
validate both the twin and the real table, reading what `cli.main`
returned rather than trusting that a file was written.
"""

from __future__ import annotations

import csv
import io
import json
import pathlib
import random
import sys

import pytest

from tests import fixtures

# The floor these shapes are described at, as the rest of this landing
# uses: eleven is the floor the audit measured at.
FLOOR = ("--smallest-group", "11")
ROWS = 800


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


def _cells_of(path: pathlib.Path) -> "list[str]":
    """The first column of a written table, without its header."""
    rows = list(csv.reader(io.StringIO(path.read_text(encoding="utf-8"))))
    return [row[0] for row in rows[1:]]


def _round_trip(
    folder: pathlib.Path,
    cells: "list[str]",
    seed: str = "4",
    header: str = "value",
) -> "tuple[dict[str, object], dict[str, object], list[str], int, int]":
    """Describe, build, describe the TWIN, check the twin and the real table.

    The twin is described again because that is the gate this landing is
    held to: a fact that does not come back is a fact the twin did not
    keep, and validating alone would not have caught a re-described role.
    """
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "real.csv"
    table.write_text(
        fixtures.rows_to_csv([header], [[cell] for cell in cells]),
        encoding="utf-8",
        newline="",
    )
    assert (
        _exit_of(
            ["profile", str(table), "--out-dir", str(folder), "--replace"]
            + list(FLOOR)
        )
        == 0
    )
    described = folder / "real-profile.json"
    assert (
        _exit_of(
            [
                "generate", str(described), "--out-dir", str(folder),
                "--seed", seed, "--replace",
            ]
        )
        == 0
    )
    twin = folder / "real-twin.csv"
    written = _cells_of(twin)
    again = folder / "again"
    again.mkdir()
    copied = again / "twin.csv"
    copied.write_text(twin.read_text(encoding="utf-8"), encoding="utf-8",
                      newline="")
    assert (
        _exit_of(
            ["profile", str(copied), "--out-dir", str(again), "--replace"]
            + list(FLOOR)
        )
        == 0
    )
    checked = folder / "check-twin"
    checked.mkdir()
    twin_exit = _exit_of(
        [
            "validate", str(described), "--twin", str(twin),
            "--out-dir", str(checked), "--replace",
        ]
    )
    checked_real = folder / "check-real"
    checked_real.mkdir()
    real_exit = _exit_of(
        [
            "validate", str(described), "--twin", str(table),
            "--out-dir", str(checked_real), "--replace",
        ]
    )
    source = json.loads(described.read_text(encoding="utf-8"))["columns"][0]
    twin_block = json.loads(
        (again / "twin-profile.json").read_text(encoding="utf-8")
    )["columns"][0]
    return source, twin_block, written, twin_exit, real_exit


# -- 1. the real table meets its own description ------------------------


def _excel_scientific(rows: int) -> "list[str]":
    """What Excel writes for a large column in scientific format."""
    draw = random.Random("excel-scientific")
    return ["%.2E" % draw.lognormvariate(11.0, 1.2) for _ in range(rows)]


@pytest.mark.parametrize("seed", ["1", "7"])
def test_a_real_excel_export_meets_its_own_description(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """THE COMMONEST SHAPE FIRST: `2.29E+05`, three mantissa figures.

    Measured before the repair: 800 of 800 real cells carry a mantissa
    of three figures, and validating the real file against its own
    description exited 3 with `styles.spelled` MISSED on every seed.
    The mantissa width is not a published fact, so the twin does not
    keep it -- that is the carried half of NC-1 and this test does not
    claim it. What it claims is the half that is a false accusation:
    the file's own cells are spellings of their own values.
    """
    cells = _excel_scientific(ROWS)
    source, _twin_block, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "excel", cells, seed=seed, header="amount"
    )
    assert source["numeric_styles"] == {"exponent_upper": ROWS}
    assert real_exit == 0
    assert twin_exit == 0


@pytest.mark.parametrize("seed", ["1", "7"])
def test_a_real_sas_export_and_its_zero_meet_their_description(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """SAS `E10.4`, and the zero cell, which has no figures to pad.

    `0.00E+00` is the shape the audit's design notes single out: the
    figures of zero are just `0`, so a rule built from the value's own
    figures has to admit a mantissa that is all zeros. A fifth of this
    column is zero and the real file exited 3 before the repair.
    """
    draw = random.Random("sas-e10-4")
    cells = [
        "%.2E" % (0.0 if draw.random() < 0.2 else draw.uniform(1.0, 900.0))
        for _ in range(ROWS)
    ]
    source, _twin_block, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "sas", cells, seed=seed, header="reading"
    )
    assert source["n_zero"] > 100
    assert real_exit == 0
    assert twin_exit == 0


@pytest.mark.parametrize("seed", ["1", "7"])
def test_an_exponent_with_no_sign_meets_its_description(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """`6E9`: no `+` on the exponent and one digit, not two.

    Fortran list-directed output, JavaScript and Julia all write this.
    G6.3 writes `6e+09`, which differs from the file's own cell in no
    figure of the number.
    """
    draw = random.Random("no-sign-exponent")
    cells = [
        f"{draw.randrange(1, 10)}E{draw.randrange(3, 10)}"
        for _ in range(ROWS)
    ]
    _source, _twin_block, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "nosign", cells, seed=seed, header="capacity"
    )
    assert real_exit == 0
    assert twin_exit == 0


@pytest.mark.parametrize("seed", ["1", "7"])
def test_a_real_stata_export_with_no_leading_zero_meets_its_description(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """`.05` and `-.23`, and the zero cell `.000` beside them.

    The zero cell is why this is a NOTATION restored before the
    spellings are offered rather than a shape tested against the
    fixed-point text: the bare spelling of a cell that rounds to
    nothing is `.000`, whose restored text is offered only by the
    census width.
    """
    draw = random.Random("stata-bare-point")
    cells: "list[str]" = []
    for _each in range(ROWS):
        text = "%.3f" % draw.uniform(-0.999, 0.999)
        if text[:2] == "0.":
            cells += [f".{text[2:]}"]
        else:
            cells += [f"-.{text[3:]}"]
    source, _twin_block, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "stata", cells, seed=seed, header="change"
    )
    assert source["fraction_widths"] == {"3": ROWS}
    assert real_exit == 0
    assert twin_exit == 0


@pytest.mark.parametrize("seed", ["1", "7"])
def test_whole_numbers_past_binary64_meet_their_description(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """Seventeen-figure identifiers, whose last figure the format loses.

    `88618223144562695` and `88618223144562696` are ONE binary64, and
    only the second is what `repr` produces -- so every cell whose last
    figure the format cannot keep was counted as a spelling outside the
    six forms. About half of them are, because about half of the real
    values end in an odd figure.

    The twin's own parity is NOT claimed here and is carried: it writes
    a last figure that is always even, which no published fact covers.
    """
    draw = random.Random("seventeen-figures")
    cells = [str(draw.randrange(10 ** 16, 10 ** 17)) for _ in range(ROWS)]
    odd = len([cell for cell in cells if cell[-1:] in "13579"])
    assert odd > 300, odd
    _source, _twin_block, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "wide", cells, seed=seed, header="accession"
    )
    assert real_exit == 0
    assert twin_exit == 0


def test_a_spelling_of_no_permitted_form_is_still_missed(
    tmp_path: pathlib.Path,
) -> None:
    """THE WIDENING IS STILL FALSIFIABLE, which is the point of this test.

    `46E+02` reads back as 4600 and is a spelling of that number in
    nobody's grammar: the family pairs ONE figure before the point with
    the matching exponent, and this pairs two with an exponent one
    smaller. It is admitted by no rule this landing added -- the padded
    mantissa must carry the value's own decimal place -- so the file
    holding it must still be MISSED. A check that cannot fail is the
    failure mode a widening of a permitted family invites, and this is
    what stops this one becoming it.
    """
    cells = ["%.2E" % (4600.0 + 100.0 * (step % 7)) for step in range(300)]
    folder = tmp_path / "unfamiliar"
    folder.mkdir()
    table = folder / "real.csv"
    table.write_text(
        fixtures.rows_to_csv(["amount"], [[cell] for cell in cells]),
        encoding="utf-8",
        newline="",
    )
    assert (
        _exit_of(
            ["profile", str(table), "--out-dir", str(folder), "--replace"]
            + list(FLOOR)
        )
        == 0
    )
    described = folder / "real-profile.json"
    # The same file with ONE cell re-spelled into a pairing the family
    # does not hold. Nothing else about the file changes.
    spoiled = folder / "spoiled.csv"
    changed = ["46E+02"] + cells[1:]
    spoiled.write_text(
        fixtures.rows_to_csv(["amount"], [[cell] for cell in changed]),
        encoding="utf-8",
        newline="",
    )
    checked = folder / "check"
    checked.mkdir()
    assert (
        _exit_of(
            [
                "validate", str(described), "--twin", str(spoiled),
                "--out-dir", str(checked), "--replace",
            ]
        )
        == 3
    )


# -- 2. a whole-number column stays whole -------------------------------


@pytest.mark.parametrize("seed", ["1", "7"])
def test_a_whole_column_written_with_a_point_stays_whole(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """`44.0`: every value whole, every cell one figure wide.

    The two facts answer different questions and the separation walk
    read the wrong one. Measured before the repair: 23 non-whole twin
    cells of 800 at seed 1 and 19 at seed 7, `25.6` and `30.6` among
    them, with the twin re-describing itself as `continuous`.

    The twin is DESCRIBED AGAIN here rather than only validated,
    because the fact that broke is the one a re-description carries:
    the role and the statistical type a reader infers.
    """
    draw = random.Random("pandas-whole-with-point")
    cells = ["%.1f" % draw.randrange(0, 121) for _each in range(ROWS)]
    source, twin_block, written, twin_exit, real_exit = _round_trip(
        tmp_path / "counts", cells, seed=seed, header="visits"
    )
    assert source["integer_valued"] is True
    assert source["role"] == "count"
    assert source["fraction_widths"] == {"1": ROWS}
    # THE FACT ITSELF: no twin cell holds a value with a fraction.
    not_whole = [cell for cell in written if float(cell) != int(float(cell))]
    assert not_whole == []
    # ...and it comes back when the twin is described again.
    assert twin_block["integer_valued"] is True
    assert twin_block["role"] == "count"
    assert twin_block["fraction_widths"] == {"1": ROWS}
    assert twin_exit == 0
    assert real_exit == 0


def test_the_integer_grid_is_read_from_the_wholeness_not_the_census(
    tmp_path: pathlib.Path,
) -> None:
    """The rule, driven directly, so a column reaching it by luck pins nothing.

    A census of one width and a whole-valued column: the grid is the
    INTEGERS, not that width. Before this landing the census was read
    first and answered `1`.
    """
    from synthtwin import contract, generation

    draw = random.Random("integer-grid-unit")
    cells = ["%.1f" % draw.randrange(10, 90) for _each in range(400)]
    folder = tmp_path / "unit"
    folder.mkdir()
    table = folder / "real.csv"
    table.write_text(
        fixtures.rows_to_csv(["reading"], [[cell] for cell in cells]),
        encoding="utf-8",
        newline="",
    )
    assert (
        _exit_of(
            ["profile", str(table), "--out-dir", str(folder), "--replace"]
            + list(FLOOR)
        )
        == 0
    )
    loaded = contract.load_profile(f"{folder / 'real-profile.json'}")
    column = loaded.columns[0]
    facts = column.facts
    assert isinstance(facts, contract.NumericFacts)
    # The fixture is the shape the rule turns on, asserted rather than
    # assumed: a NON-EMPTY census on a whole-valued column.
    assert facts.integer_valued is True
    assert facts.fraction_widths == {"1": 400}
    assert generation._pinned_fraction(column, facts) == 0


# -- 3. a padded cell never overflows its field -------------------------


def test_a_padded_value_no_field_can_hold_gives_the_style_up() -> None:
    """The exchange of G6.3's rule 2, in the direction that was missing.

    Driven directly, because what is under test is the LAST pass and a
    column reaching it by chance would pin nothing. A value of 12 needs
    two figures, so no cell of it can be written in a two-character
    field with a zero in front; a value of 5 can. Before this landing
    the style stayed where it was and the writer put a zero in front of
    the 12 anyway, writing `012` in a field of two.

    THE CENSUS COUNTS FEWER CELLS THAN WEAR THE STYLE, and that shape
    is the whole point of this fixture rather than an incidental
    detail. The first writing of this test gave the census two cells
    and three wore the style, and the MUTATION CHECK caught it: the
    walks that already existed served that case themselves, so the test
    passed with this landing's pass withdrawn and pinned nothing at
    all. Here one cell is counted and two wear the style -- which is
    what a POOLED pad census leaves behind, the withheld key naming no
    width -- so the earlier walks stop with the count served and the
    overflowing cell still wearing the style, and only this pass moves
    it.

    The count of padded cells is unchanged by the exchange, which is
    what keeps every published style count exactly where it was.
    """
    from synthtwin import generation

    styles = ["leading_zero", "leading_zero", "plain"]
    holds = [12.0, 3.0, 5.0]
    moved = generation._padded_style_swaps(
        styles, holds, {"2": 1}, [], True
    )
    assert moved[0] != "leading_zero"
    assert len([name for name in moved if name == "leading_zero"]) == len(
        [name for name in styles if name == "leading_zero"]
    )
    for place in range(len(moved)):
        if moved[place] == "leading_zero":
            assert generation._pad_need(holds[place], True) < 2


def test_a_padded_cell_with_no_partner_keeps_the_style() -> None:
    """And where no cell can take it, nothing is invented.

    Every cell not wearing the padded style here already needs the
    whole field, so there is no exchange to make. The pass must leave
    the column exactly as it found it rather than move a style onto a
    value that cannot wear it -- which is the measured shape of the
    month column this landing does NOT close, and the reason it is
    carried rather than claimed.
    """
    from synthtwin import generation

    styles = ["leading_zero", "leading_zero", "leading_zero", "plain", "plain"]
    holds = [12.0, 3.0, 4.0, 11.0, 10.0]
    assert generation._padded_style_swaps(
        styles, holds, {"2": 3}, [], True
    ) == styles
