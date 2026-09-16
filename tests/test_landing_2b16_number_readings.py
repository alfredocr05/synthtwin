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
