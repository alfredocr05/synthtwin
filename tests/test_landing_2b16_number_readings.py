"""Landing 2b.16: a padded cell is never written wider than its field.

The audit's missed item M4, which plan P4-D66.4 closed by half. That
decision made G6.3's rule 2 run in both directions -- the padded style
moves onto a value a published field can hold, and off a value none can
-- and left the case where there is no partner to exchange with, sending
it to the VALUE draw of G5 instead. It cannot go there: contract 9.4
says a named field width is honoured by PADDING and never by adjusting a
value, because `000123` and `123` read back as the same number and no
rung, endpoint or statistic may be spent to reach one. So the census is
unmeetable on the values in hand, something must be missed, and the only
question is what.

MEASURED ON THE BASE of this landing, eight hundred five-figure postal
codes at floor eleven: the description publishes `pad_widths {5: 85}` at
seed 7, the twin drew 84 values narrow enough for the field, and it
wrote `099613` -- six characters in a five-character field -- while
missing `pads.published.5` at 84 all the same. The census was missed in
both writings. What differs is the cell, and the cell is the half a
person meets: a fixed-width slice, a length check and a code lookup all
run on a twin whose every cell is five characters, and none of them runs
on one holding a six-character code the real column never wrote.

WHAT IS PINNED HERE:

- no cell of the twin is wider than the field width its own description
  publishes, on any seed, whether the census can be met or not;
- where the census CAN be met, the round trip returns it and the forms
  map exactly, and the twin and the real table both validate at exit 0;
- where it cannot, the shortfall is NAMED -- the width census and the
  forms map are both missed, every miss naming the one cell -- rather
  than paid for with a spelling no real cell of the column wears;
- and the mutation check: with the give-up withdrawn, the first test
  here goes red on the six-character cell.

Every table is built by seeded neutral code at runtime (plan D13).
"""

import csv
import io
import json
import pathlib
import random
import sys

import pytest

from tests import fixtures

ROWS = 800

# Seven seeds, and the two that cannot meet their own census are among
# them deliberately: a gate that ran only on the seeds where everything
# fits would pass with the repair withdrawn.
SEEDS = (1, 2, 3, 5, 7, 11, 13)

# The seed whose census the twin's own draw cannot reach, and what it
# reaches instead. Pinned as a pair so that a change to either number is
# a visible decision rather than a quiet one.
UNMEETABLE_SEED = 7
PUBLISHED_AT_THAT_SEED = {"5": 85}
WRITTEN_AT_THAT_SEED = {"5": 84}


def _exit_of(argv: "list[str]") -> int:
    """Run one synthtwin command in this process and return its exit code.

    Written out here rather than imported from another test module, on
    the same ground `tests/test_stage2_round_trip.py` states: a helper
    shared between test files ties one gate to another, and a gate that
    fails because its neighbour moved is a gate nobody trusts.
    """
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


def _round_trip(
    folder: pathlib.Path,
    cells: "list[str]",
    seed: str,
    flags: "tuple[str, ...]" = (),
) -> "tuple[dict[str, object], dict[str, object], list[str], int, int]":
    """Describe, build, describe the twin; check the twin and the table.

    ``flags`` are declarations, and they are passed to BOTH descriptions:
    a twin described under other declarations than its source is a twin
    measured in a grammar nobody wrote it in.
    """
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "real.csv"
    table.write_text(
        fixtures.rows_to_csv(["code"], [[cell] for cell in cells]),
        encoding="utf-8",
        newline="",
    )
    assert (
        _exit_of(
            [
                "profile",
                str(table),
                "--out-dir",
                str(folder),
                "--replace",
                "--smallest-group",
                "11",
            ]
            + list(flags)
        )
        == 0
    )
    described = folder / "real-profile.json"
    assert (
        _exit_of(
            [
                "generate",
                str(described),
                "--out-dir",
                str(folder),
                "--seed",
                seed,
                "--replace",
            ]
        )
        == 0
    )
    twin = folder / "real-twin.csv"
    again = folder / "again"
    again.mkdir()
    copied = again / "twin.csv"
    copied.write_bytes(twin.read_bytes())
    assert (
        _exit_of(
            [
                "profile",
                str(copied),
                "--out-dir",
                str(again),
                "--replace",
                "--smallest-group",
                "11",
            ]
            + list(flags)
        )
        == 0
    )
    first = json.loads(described.read_text(encoding="utf-8"))["columns"][0]
    second = json.loads(
        (again / "twin-profile.json").read_text(encoding="utf-8")
    )["columns"][0]
    written = [
        row[0]
        for row in csv.reader(io.StringIO(twin.read_text(encoding="utf-8")))
    ][1:]
    checked = folder / "check-twin"
    checked.mkdir()
    twin_exit = _exit_of(
        [
            "validate",
            str(described),
            "--twin",
            str(twin),
            "--out-dir",
            str(checked),
            "--replace",
        ]
    )
    real_checked = folder / "check-real"
    real_checked.mkdir()
    real_exit = _exit_of(
        [
            "validate",
            str(described),
            "--twin",
            str(table),
            "--out-dir",
            str(real_checked),
            "--replace",
        ]
    )
    return first, second, written, twin_exit, real_exit


def _missed(folder: pathlib.Path) -> "list[str]":
    """Every obligation the quality report names as missed."""
    found: "list[str]" = []
    for page in sorted((folder / "check-twin").glob("*.txt")):
        for line in page.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if "MISSED" not in stripped:
                continue
            if "CHECKABLE" in stripped or "set by the description" in stripped:
                continue
            found += [stripped.split(" ")[0]]
    return found


def _postal_codes(seed: int) -> "list[str]":
    """A realistic five-figure code column, written by a seeded script."""
    draw = random.Random(seed)
    return [f"{draw.randrange(0, 99999):05d}" for _ in range(ROWS)]


@pytest.mark.parametrize("seed", SEEDS)
def test_no_twin_cell_is_wider_than_the_field_its_description_publishes(
    seed: int, tmp_path: pathlib.Path
) -> None:
    """THE DEFECT, AS A TEST (audit item M4).

    Before this landing the twin of this column wrote `099613` at seed 7
    and `010035` at seed 11: six characters in a field its own
    description publishes as five.
    """
    cells = _postal_codes(seed)
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / f"codes-{seed}", cells, str(seed)
    )
    assert first["pad_widths"]
    for cell in written:
        if cell:
            assert len(cell) == 5, cell
    # The real table still meets its own description, which is what
    # keeps a repair of the twin from being bought from the file.
    assert real_exit == 0
    # ...and where the census CAN be met, the round trip returns every
    # fact of it, and nothing is missed.
    if twin_exit == 0:
        assert second["pad_widths"] == first["pad_widths"]
        assert second["numeric_styles"] == first["numeric_styles"]
        assert _missed(tmp_path / f"codes-{seed}") == []


def test_where_the_census_cannot_be_met_the_field_holds_and_the_miss_is_named(
    tmp_path: pathlib.Path,
) -> None:
    """The pinned case: 85 padded cells asked for, 84 values to wear them.

    This is the shape plan P4-D66.4 carried. The repair cannot reach the
    published count -- no value in hand can wear the field -- so it
    keeps the FIELD and gives the form up, and both counts are named.
    """
    folder = tmp_path / "unmeetable"
    first, second, written, twin_exit, real_exit = _round_trip(
        folder, _postal_codes(UNMEETABLE_SEED), str(UNMEETABLE_SEED)
    )
    assert first["pad_widths"] == PUBLISHED_AT_THAT_SEED
    assert second["pad_widths"] == WRITTEN_AT_THAT_SEED
    for cell in written:
        if cell:
            assert len(cell) == 5, cell
    assert real_exit == 0
    # Not silent: the width census and the forms map are both named, and
    # the report says so rather than passing the cell over.
    assert twin_exit == 3
    missed = _missed(folder)
    assert "pads.published.5" in missed
    assert "styles.exact.leading_zero" in missed


EUROPEAN_SEEDS = (1, 7)
DECLARED = ("--decimal-comma", "code")


def _euro_prices(seed: int) -> "list[str]":
    """A European price export, written by a seeded script."""
    draw = random.Random(seed)
    return [
        f"{round(draw.lognormvariate(6.4, 1.0), 2):.2f}".replace(".", ",")
        + " EUR"
        for _ in range(ROWS)
    ]


@pytest.mark.parametrize("seed", EUROPEAN_SEEDS)
def test_a_declared_european_price_column_comes_back_as_money(
    seed: int, tmp_path: pathlib.Path
) -> None:
    """THE DEFECT, AS A TEST (audit item NC-11).

    Before this landing the same column was described as free text and
    its twin held `)!!!!! !!!!!`: no numeric cell, no ladder, no mean,
    and `synthtwin validate` exit 0 on both files, so nothing said a
    word about it.
    """
    cells = _euro_prices(seed)
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / f"euro-{seed}", cells, str(seed), DECLARED
    )
    assert first["role"] == "affixed_number"
    assert first["affix_suffix"] == " EUR"
    # The twin is money, written the way the source writes it.
    for cell in written:
        if not cell:
            continue
        assert cell[len(cell) - 4 :] == " EUR", cell
        core = cell[: len(cell) - 4]
        assert "," in core, cell
        assert "." not in core, cell
    # ...and the round trip returns the facts and the spellings.
    assert second["role"] == first["role"]
    assert second["affix_suffix"] == first["affix_suffix"]
    assert second["numeric_styles"] == first["numeric_styles"]
    assert second["fraction_widths"] == first["fraction_widths"]
    assert second["percentiles"]["min"] == first["percentiles"]["min"]
    assert second["percentiles"]["max"] == first["percentiles"]["max"]
    assert twin_exit == 0
    assert real_exit == 0
    assert _missed(tmp_path / f"euro-{seed}") == []


def test_a_declared_european_percentage_is_read_the_same_way(
    tmp_path: pathlib.Path,
) -> None:
    """The other commonest European export: `37,5 %`."""
    draw = random.Random(1)
    cells = [
        f"{round(draw.uniform(0, 100), 1):.1f}".replace(".", ",") + " %"
        for _ in range(ROWS)
    ]
    first, _second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "pct", cells, "1", DECLARED
    )
    assert first["role"] == "affixed_number"
    assert first["affix_suffix"] == " %"
    for cell in written:
        if cell:
            assert cell[len(cell) - 2 :] == " %", cell
            assert "," in cell[: len(cell) - 2], cell
    assert twin_exit == 0
    assert real_exit == 0


def test_a_wrapper_that_carries_a_mark_is_copied_and_never_translated(
    tmp_path: pathlib.Path,
) -> None:
    """The wrapper is the FILE's text; only the core is the number.

    Measured before the reading and the writeback were held to the core:
    the twin's cells were right and BOTH files were reported at exit 3
    with `styles.at-least.decimal` MISSED, because the reading turned
    `U.S.$ 129,58` into `U,S,$ 129.58` and counted it a straggler.
    """
    for prefix, suffix in (("U.S.$ ", ""), ("", " kg.")):
        draw = random.Random(1)
        cells = []
        for _ in range(ROWS):
            body = f"{round(draw.uniform(10, 900), 2):.2f}".replace(".", ",")
            cells += [f"{prefix}{body}{suffix}"]
        folder = tmp_path / f"marked-{len(prefix)}-{len(suffix)}"
        first, _second, written, twin_exit, real_exit = _round_trip(
            folder, cells, "1", DECLARED
        )
        assert first["role"] == "affixed_number"
        assert first["affix_prefix"] == prefix
        assert first["affix_suffix"] == suffix
        for cell in written:
            if not cell:
                continue
            assert cell[: len(prefix)] == prefix, cell
            if suffix:
                assert cell[len(cell) - len(suffix) :] == suffix, cell
        assert twin_exit == 0, (prefix, suffix)
        assert real_exit == 0, (prefix, suffix)
        assert _missed(folder) == []


def test_an_undeclared_column_of_prices_is_left_exactly_as_it_was(
    tmp_path: pathlib.Path,
) -> None:
    """The no-regression control: the declaration changes only what it names.

    The same column written with a POINT and declared nothing must come
    back the way it always did -- a point in every core, and exit 0 --
    because a reading that moved on an undeclared column would move
    every affixed column in the world with it.
    """
    draw = random.Random(1)
    cells = [
        f"{round(draw.lognormvariate(6.4, 1.0), 2):.2f} EUR"
        for _ in range(ROWS)
    ]
    first, _second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "undeclared", cells, "1"
    )
    assert first["role"] == "affixed_number"
    for cell in written:
        if cell:
            assert "." in cell[: len(cell) - 4], cell
            assert "," not in cell, cell
    assert twin_exit == 0
    assert real_exit == 0


def _euro_grouped_prices(seed: int) -> "list[str]":
    """A European price export that GROUPS its thousands, seeded.

    `92.959,11 EUR`: the point between thousands and the comma before
    the cents, which is how a German, Spanish or Italian export writes
    a four-figure amount. Every cell is at or past a thousand, so every
    cell proves the mark.
    """
    draw = random.Random(seed)
    out: "list[str]" = []
    for _ in range(ROWS):
        amount = draw.randrange(100000, 9999999) / 100
        whole = int(amount)
        cents = int(round((amount - whole) * 100))
        grouped = f"{whole:,}".replace(",", ".")
        out += [f"{grouped},{cents:02d} EUR"]
    return out


def _grouping_in(core: str) -> "tuple[int, bool]":
    """How many whole figures this core writes, and whether it is grouped."""
    figures = 0
    for letter in core:
        if letter == ",":
            break
        if letter != ".":
            figures += 1
    pointed = False
    for letter in core:
        if letter == ".":
            pointed = True
    return figures, pointed


@pytest.mark.parametrize("seed", EUROPEAN_SEEDS)
def test_a_declared_european_price_that_groups_its_thousands_keeps_the_mark(
    seed: int, tmp_path: pathlib.Path
) -> None:
    """THE DEFECT, AS A TEST (plan P4-D108, the skeptic's MAJOR finding).

    The tally the affixed block reads its cores off was built WITHOUT
    the declaration the cores were classified under, so every rule that
    asks the record which grammar this column writes -- the mark between
    thousands above all -- answered for an undeclared column. Measured
    on the base of this repair, 800 cells of `92.959,11 EUR` at floor
    eleven: `group_separator: ""` and `thousands_marks: {}` about a
    column where 800 of 800 cells carry a grouping point, the twin
    wrote `62391,86 EUR` with 0 of 800 grouped, and the twin AND the
    real table validated at exit 0 with nothing missed -- so a spelling
    every real cell wore was lost in silence.
    """
    cells = _euro_grouped_prices(seed)
    folder = tmp_path / f"grouped-{seed}"
    first, second, written, twin_exit, real_exit = _round_trip(
        folder, cells, str(seed), DECLARED
    )
    assert first["role"] == "affixed_number"
    # THE MARK THE CORES WEAR, read in the column's OWN grammar: the
    # point `42.037,34` writes, never the comma that column spends on
    # its decimals.
    assert first["group_separator"] == "."
    assert first["thousands_marks"] == {".": ROWS}
    # ...and the twin writes it, on every cell that can wear it.
    grouped = 0
    for cell in written:
        if not cell:
            continue
        assert cell[len(cell) - 4 :] == " EUR", cell
        core = cell[: len(cell) - 4]
        assert "," in core, cell
        figures, pointed = _grouping_in(core)
        if figures >= 4:
            assert pointed, cell
            grouped += 1
    assert grouped >= 11
    # ...so the twin's own re-description says what its source said.
    assert second["role"] == first["role"]
    assert second["group_separator"] == first["group_separator"]
    assert second["numeric_styles"] == first["numeric_styles"]
    assert second["fraction_widths"] == first["fraction_widths"]
    assert twin_exit == 0
    assert real_exit == 0
    assert _missed(folder) == []


def test_a_declared_grouped_column_keeps_its_mark_beside_a_kept_stand_in(
    tmp_path: pathlib.Path,
) -> None:
    """The stand-in pass reads the cores in the same grammar (P4-D108).

    The third tally built from cores is the one the stand-in judgement
    runs over, and it dropped the declaration exactly as the other two
    did. A column carrying `-999,0 EUR` the owner has told this tool to
    KEEP must still publish the mark its other cells wear.
    """
    cells = _euro_grouped_prices(3)
    kept = 20
    for step in range(kept):
        cells[step * 7] = "-999,0 EUR"
    folder = tmp_path / "grouped-kept"
    first, _second, written, twin_exit, real_exit = _round_trip(
        folder,
        cells,
        "3",
        DECLARED + ("--keep-value", "-999,0 EUR"),
    )
    assert first["role"] == "affixed_number"
    assert first["n_present"] == ROWS
    assert first["group_separator"] == "."
    assert first["thousands_marks"] == {".": ROWS - kept}
    written_grouped = 0
    for cell in written:
        if not cell:
            continue
        figures, pointed = _grouping_in(cell[: len(cell) - 4])
        if figures >= 4 and pointed:
            written_grouped += 1
    assert written_grouped >= 11
    assert twin_exit == 0
    assert real_exit == 0


def test_an_undeclared_grouped_price_column_still_publishes_the_comma(
    tmp_path: pathlib.Path,
) -> None:
    """The no-regression control, on the shape the repair moves.

    `92,959.11 EUR` declared nothing is the commonest grouped affix
    there is, and it must come back exactly as it always did: a comma
    between thousands, a point before the cents. A repair that reached
    an undeclared column would move every affixed column in the world.
    """
    draw = random.Random(29)
    cells = [
        f"{draw.randrange(100000, 9999999) / 100:,.2f} EUR"
        for _ in range(ROWS)
    ]
    folder = tmp_path / "undeclared-grouped"
    first, second, written, twin_exit, real_exit = _round_trip(
        folder, cells, "29", ()
    )
    assert first["role"] == "affixed_number"
    assert first["group_separator"] == ","
    assert first["thousands_marks"] == {",": ROWS}
    assert second["group_separator"] == ","
    for cell in written:
        if not cell:
            continue
        core = cell[: len(cell) - 4]
        assert "," in core, cell
        assert "." in core, cell
    assert twin_exit == 0
    assert real_exit == 0
    assert _missed(folder) == []


def test_a_column_of_month_codes_keeps_its_two_character_field(
    tmp_path: pathlib.Path,
) -> None:
    """The shape plan P4-D66.4 was opened on, at the seed that failed.

    Month codes `01` to `12`: the twin wrote `012` at seed 11, three
    characters in a two-character field, three cells of eight hundred.
    """
    draw = random.Random(11)
    cells = [f"{draw.randrange(1, 13):02d}" for _ in range(ROWS)]
    first, _second, written, _twin_exit, real_exit = _round_trip(
        tmp_path / "months", cells, "11"
    )
    assert first["pad_widths"]
    for cell in written:
        if cell:
            assert len(cell) <= 2, cell
    assert real_exit == 0


# THE PADDED WIDE KEYS NOTHING CHECKED (landing 2b.16 part 2, plan
# P4-D107). Nineteen characters of field holding a seventeen-figure
# key, which is the shape a real accession or account export writes.
KEY_WIDTH = 19


def _canonical_wide_keys(
    seed: int, width: int = KEY_WIDTH, sign: str = ""
) -> "list[str]":
    """Padded keys whose runs ARE the text their own values write.

    The value is snapped to its own double before it is written, which
    is what makes the column canonical rather than nearly so: past
    2**53 a drawn integer is usually NOT held exactly, so a column
    written from the draw is `respelled` and would pin nothing.
    """
    draw = random.Random(seed)
    cells: "list[str]" = []
    while len(cells) < ROWS:
        value = float(draw.randrange(10**16, 9 * 10**16))
        figures = f"{int(value)}"
        if len(figures) > width:
            continue
        cells += [sign + figures.rjust(width, "0")]
    return cells


def _a_value_preserving_neighbour(text: str) -> str:
    """A DIFFERENT run of figures, in the same field, reading back the same.

    The respelling the padded form hid: past 2**53 the spacing between
    doubles reaches two, so a run one or two away denotes the very same
    number, and padded into the same field it wears the same form and
    the same width as the run it replaced.
    """
    sign = ""
    body = text
    if body[:1] == "+" or body[:1] == "-":
        sign = body[:1]
        body = body[1:]
    figures = body
    while figures[:1] == "0" and len(figures) > 1:
        figures = figures[1:]
    value = float(figures)
    whole = int(figures)
    for step in (1, -1, 2, -2):
        candidate = f"{whole + step}"
        if float(candidate) == value and len(candidate) == len(figures):
            return sign + candidate.rjust(len(body), "0")
    return text


def _accused_of_respelling(folder: pathlib.Path, cells: "list[str]") -> int:
    """Check a file against a description already written, and count the misses.

    The attack the word exists to catch: the description is published
    from the CANONICAL column, and the file handed to the checker is
    that column respelled cell by cell.
    """
    written = folder / "respelled.csv"
    written.write_text(
        fixtures.rows_to_csv(["code"], [[cell] for cell in cells]),
        encoding="utf-8",
        newline="",
    )
    out = folder / "attack"
    out.mkdir()
    code = _exit_of(
        [
            "validate",
            str(folder / "real-profile.json"),
            "--twin",
            str(written),
            "--out-dir",
            str(out),
            "--replace",
        ]
    )
    named = 0
    for report in out.glob("*.txt"):
        for line in report.read_text(encoding="utf-8").splitlines():
            if "styles.canonical.wide" in line and "MISSED" in line:
                named += 1
    assert named > 0, "the report never named the subcheck"
    return code


@pytest.mark.parametrize("seed", [1, 7])
def test_a_padded_column_of_wide_keys_is_asked_the_canonical_question(
    seed: int, tmp_path: pathlib.Path
) -> None:
    """The limit landing 2b.13 named, closed by reading the pad first.

    MEASURED ON THE BASE of this landing, through the real reader,
    producer, loader and validator: 800 zero-padded nineteen-wide keys
    at floor eleven, every cell respelled into the value-preserving
    neighbour a double cannot tell apart -- 786 of 800 moved at seed 1,
    780 at seed 7 -- published `wide_runs: none`, and the twin, the real
    table and the canonical description handed the respelled file ALL
    exited 0 with nothing named. Nothing checked the column.

    The shape is asserted before the answer, because a column of narrow
    padded codes passes every line below with the defect still in place.
    """
    cells = _canonical_wide_keys(seed)
    folder = tmp_path / "padded"
    first, second, written, twin_exit, real_exit = _round_trip(
        folder, cells, str(seed)
    )
    # The shape the question turns on.
    assert first["numeric_styles"] == {"leading_zero": ROWS}, first[
        "numeric_styles"
    ]
    assert first["pad_widths"] == {f"{KEY_WIDTH}": ROWS}, first["pad_widths"]
    # ...and the answer, which was `none` before this landing.
    assert first["wide_runs"] == "canonical", first["wide_runs"]
    assert second["wide_runs"] == "canonical", second["wide_runs"]
    assert twin_exit == 0
    assert real_exit == 0
    for cell in written:
        if cell:
            assert len(cell) == KEY_WIDTH, cell
            figures = cell
            while figures[:1] == "0" and len(figures) > 1:
                figures = figures[1:]
            assert figures == f"{int(float(cell))}", cell
    # ...AND THE CHECK CAN FAIL, which is the half that makes the rest
    # worth asserting. The same description, the same field, the same
    # form on every cell -- and a run the value does not write.
    respelled = [_a_value_preserving_neighbour(cell) for cell in cells]
    moved = 0
    for before, after in zip(cells, respelled):
        assert float(before) == float(after)
        assert len(before) == len(after)
        if before != after:
            moved += 1
    assert moved > 700, moved
    assert _accused_of_respelling(folder, respelled) == 3


@pytest.mark.parametrize("seed", [1, 7])
def test_a_real_padded_export_that_respells_its_keys_is_never_accused(
    seed: int, tmp_path: pathlib.Path
) -> None:
    """The other direction, which is the one that must not break.

    A real export of literal seventeen-figure keys writes runs that are
    NOT their values' canonical text -- measured on this base, 663 of
    800 at seed 1 and 657 of 800 at seed 7 of a column drawn the way a
    real one is. Holding such a file to a ceiling of nought is the false
    accusation plan P4-D66.2 exists to end, so the column says
    `respelled` about its own writer and the fact is LISTED rather than
    checked.
    """
    cells = [
        _a_value_preserving_neighbour(cell)
        for cell in _canonical_wide_keys(seed)
    ]
    first, _second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "respelled", cells, str(seed)
    )
    assert first["numeric_styles"] == {"leading_zero": ROWS}, first[
        "numeric_styles"
    ]
    assert first["wide_runs"] == "respelled", first["wide_runs"]
    # The REAL table meets its own description, which is the whole point.
    assert real_exit == 0
    assert twin_exit == 0


def test_a_plus_signed_padded_column_reads_its_pad_off_too(
    tmp_path: pathlib.Path,
) -> None:
    """The form the rule already admitted, whose pad it never read.

    `+0019094652364241860` is `leading_plus`, not `leading_zero`, so
    this question was asked of it before this landing -- and its PADDED
    figures were compared with its value's. Measured on this base: a
    column of 800 plus-signed padded keys, every one written
    canonically, was counted 800 of 800 NOT canonical, so the column
    published `respelled` about a file that respells nothing. That is a
    defect in the form the old bound kept, not in the one it excluded,
    and one reading answers both.
    """
    cells = _canonical_wide_keys(1, sign="+")
    folder = tmp_path / "plus"
    first, second, written, twin_exit, real_exit = _round_trip(
        folder, cells, "1"
    )
    assert first["numeric_styles"] == {"leading_plus": ROWS}, first[
        "numeric_styles"
    ]
    assert first["wide_runs"] == "canonical", first["wide_runs"]
    assert second["wide_runs"] == "canonical", second["wide_runs"]
    assert twin_exit == 0
    assert real_exit == 0
    # AND THE WIDTH COMES BACK, which this test did not ask and which was
    # lost on every cell (plan P4-D145, the final Codex review's item 6):
    # a plus hid the pad from the census, so the description published
    # `pad_widths {}` and the twin wrote every key two characters short
    # while the canonical flags and both exit codes above stayed green.
    assert first["pad_widths"] == {f"{KEY_WIDTH}": ROWS}, first["pad_widths"]
    assert second["pad_widths"] == first["pad_widths"], second["pad_widths"]
    for cell in written:
        if cell:
            assert len(cell) == KEY_WIDTH + 1, cell
            assert cell[:2] == "+0", cell
    respelled = [_a_value_preserving_neighbour(cell) for cell in cells]
    assert _accused_of_respelling(folder, respelled) == 3


def test_a_narrow_padded_code_column_still_says_none(
    tmp_path: pathlib.Path,
) -> None:
    """And the ordinary padded column is untouched, which is the control.

    Five-figure postal codes: no cell is anywhere near the bound, so
    the word stays `none`, the fact is LISTED, and both files pass. A
    rule that read the pad off and then forgot the bound would call
    this column canonical and file a ceiling on it.
    """
    draw = random.Random(1)
    cells = [f"{draw.randrange(0, 99999):05d}" for _ in range(ROWS)]
    first, second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "codes", cells, "1"
    )
    assert first["pad_widths"], first["pad_widths"]
    assert first["wide_runs"] == "none", first["wide_runs"]
    assert second["wide_runs"] == "none", second["wide_runs"]
    assert twin_exit == 0
    assert real_exit == 0
