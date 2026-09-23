"""Stage 2: the branches the audit found no test pinning.

The stage 2 audit read every branch the landing added and grepped the
suite for a test that would turn red if it regressed. The refusals to
publish a thousands mark, most of the loader's refusals for the moment
census and the midnight statement, and the loader's check on the mark
itself were measured by hand once and pinned by nothing. Each is pinned
here by building the table or editing a description the producer really
wrote, so a regression is a red test rather than a finding.
"""

import copy
import json
import pathlib
import sys

import pytest

from synthtwin import contract, errors, parsing
from tests import fixtures


def _exit_of(argv: "list[str]") -> int:
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


def _described(
    folder: pathlib.Path, header: "list[str]", rows: "list[list[str]]", *flags: str
) -> "dict[str, object]":
    """Describe one table through the command, at the population floor.

    THE TABLE IS PADDED WITH ABSENT ROWS AND A KEEPER COLUMN (plan
    P4-D341, and the repair of landing 3.2). `synthtwin profile`
    refuses a table whose POPULATION is under
    `parsing.POPULATION_FLOOR`, and that population is the rows that
    HOLD A VALUE -- so absent padding alone cannot reach it. Every
    shape in this file is a shape of a column's PRESENT values: how
    many cells wear a thousands mark, how many are bare, how many
    moments stand off midnight. `NA` is one of this format's own
    eighteen spellings for "no value", so every one of those counts,
    and every census and refusal taken over them, is exactly what the
    shape produced before; `held` carries a value on every row so the
    table reaches the floor without any of the shapes moving, and it is
    added LAST so the column under test keeps its place. A table
    already at the floor is unchanged.
    """
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "t.csv"
    padding = parsing.POPULATION_FLOOR - len(rows)
    padded = list(rows) + [
        ["NA"] * len(header) for _row in range(padding)
    ]
    names = list(header)
    if padding > 0:
        names = names + [fixtures.KEEPER_NAME]
        padded = [list(row) + [fixtures.KEEPER_VALUE] for row in padded]
    table.write_text(
        fixtures.rows_to_csv(names, padded), encoding="utf-8", newline=""
    )
    assert _exit_of(["profile", str(table), "--out-dir", str(folder), "--replace", *flags]) == 0
    loaded: "dict[str, object]" = json.loads(
        (folder / "t-profile.json").read_text(encoding="utf-8")
    )
    return loaded


def _refused(folder: pathlib.Path, document: "dict[str, object]") -> str:
    path = fixtures.write_profile(folder, "edited.json", document)
    with pytest.raises(errors.ProfileError) as refused:
        contract.load_profile(str(path))
    return str(refused.value)


# -- the refusals to publish a mark ------------------------------------


def _mark(tmp_path: pathlib.Path, cells: "list[str]", *flags: str) -> str:
    document = _described(tmp_path, ["v"], [[cell] for cell in cells], *flags)
    columns = document["columns"]
    assert isinstance(columns, list)
    return str(columns[0].get("group_separator"))


def test_a_padded_cell_holding_a_comma_withholds_the_mark(tmp_path: pathlib.Path) -> None:
    cells = [f"{1000 + place * 7:,}" for place in range(40)] + ["01,234,000"]
    assert _mark(tmp_path, cells) == ""


def test_the_proving_cells_must_reach_the_smallest_group(tmp_path: pathlib.Path) -> None:
    cells = [f"{1000 + place * 7:,}" for place in range(8)] + [f"{place}" for place in range(40)]
    # Eight proving cells: named at a floor of one, withheld at nine and
    # at the default of 11 (plan P4-D316).
    assert _mark(tmp_path / "at-one", cells, "--smallest-group", "1") == ","
    assert _mark(tmp_path / "at-nine", cells, "--smallest-group", "9") == ""
    assert _mark(tmp_path / "at-default", cells) == ""


def test_bare_cells_that_outnumber_the_grouped_withhold_the_mark(tmp_path: pathlib.Path) -> None:
    grouped = [f"{2000 + place * 11:,}" for place in range(20)]
    bare = [f"{3000 + place * 13}" for place in range(21)]
    assert _mark(tmp_path / "fewer", grouped + bare) == ""
    assert _mark(tmp_path / "more", grouped + bare[:19]) == ","


def test_a_lone_group_is_proof_and_a_bracket_is_not_a_figure(tmp_path: pathlib.Path) -> None:
    """More bracketed negatives than grouped cells, so only the bracket rule publishes.

    Counted as figures, `(123.45)` is a bare four-figure cell, and 25 of
    them outnumber the 20 grouped cells: the mark would be withheld.
    """
    cells = [f"{1000 + place * 97:,}" for place in range(20)] + ["(123.45)"] * 25
    assert _mark(tmp_path, cells) == ","


def test_a_decimal_comma_column_grouped_with_points_publishes_a_point(
    tmp_path: pathlib.Path,
) -> None:
    cells = [f"{1000 + place * 97}.{place % 1000:03d},{place % 100:02d}" for place in range(30)]
    assert _mark(tmp_path, cells, "--decimal-comma", "v") == "."
    plain = [f"{1000 + place * 97},{place % 100:02d}" for place in range(30)]
    assert _mark(tmp_path / "plain", plain, "--decimal-comma", "v") == ""


# -- the loader's refusals ---------------------------------------------


def _numbers_document(tmp_path: pathlib.Path) -> "dict[str, object]":
    return _described(
        tmp_path / "numbers", ["v"], [[f"{1000 + place * 97:,}"] for place in range(30)]
    )


def _moments_document(tmp_path: pathlib.Path, suffix: str = " 10:15:00") -> "dict[str, object]":
    return _described(
        tmp_path / "moments",
        ["when"],
        [[f"2024-01-{(place % 28) + 1:02d}{suffix}"] for place in range(60)],
        "--smallest-group",
        "11",
    )


def _column(document: "dict[str, object]") -> "dict[str, object]":
    columns = document["columns"]
    assert isinstance(columns, list)
    found: "dict[str, object]" = columns[0]
    return found


def test_the_loader_refuses_a_mark_it_never_writes(tmp_path: pathlib.Path) -> None:
    document = copy.deepcopy(_numbers_document(tmp_path))
    # An apostrophe was the refused mark until landing 2b.2 read it; an
    # underscore is a mark no reader of numbers groups with.
    _column(document)["group_separator"] = "_"
    assert "group_separator" in _refused(tmp_path, document)


def test_the_loader_refuses_a_point_on_a_column_without_a_decimal_comma(
    tmp_path: pathlib.Path,
) -> None:
    document = copy.deepcopy(_numbers_document(tmp_path))
    column = _column(document)
    column["group_separator"] = "."
    # THE CENSUS OF MARKS MOVES WITH THE MARK (landing 2b.7). A census
    # still naming the comma would be refused first, by TM1, for a mark
    # it does not count, and this test would never reach the rule it is
    # about: the point on a column declared nothing.
    marks = column["thousands_marks"]
    assert isinstance(marks, dict) and "," in marks, marks
    column["thousands_marks"] = {".": marks[","]}
    assert "GS1" in _refused(tmp_path, document)


def test_the_loader_refuses_a_census_name_it_never_writes(tmp_path: pathlib.Path) -> None:
    document = copy.deepcopy(_moments_document(tmp_path))
    _column(document)["datetime_separators"] = {"tab": 60}
    assert "datetime_separators" in _refused(tmp_path, document)


def test_the_loader_refuses_a_census_that_does_not_count_the_clocks(
    tmp_path: pathlib.Path,
) -> None:
    document = copy.deepcopy(_moments_document(tmp_path))
    _column(document)["datetime_separators"] = {"space": 59}
    assert "D13" in _refused(tmp_path, document)


def test_the_loader_refuses_a_pool_no_unnamed_mark_could_hold(tmp_path: pathlib.Path) -> None:
    document = copy.deepcopy(_moments_document(tmp_path))
    _column(document)["datetime_separators"] = {
        "lower_t": 16, "space": 17, "upper_t": 26, "(withheld)": 1
    }
    assert "D12" in _refused(tmp_path, document)


def test_the_loader_refuses_midnight_beside_a_moment_off_midnight(
    tmp_path: pathlib.Path,
) -> None:
    document = copy.deepcopy(_moments_document(tmp_path))
    _column(document)["all_at_midnight"] = True
    assert "D14" in _refused(tmp_path, document)


def test_the_loader_refuses_midnight_below_the_smallest_group(tmp_path: pathlib.Path) -> None:
    document = _described(
        tmp_path / "few",
        ["when"],
        [[f"2024-01-{place + 1:02d} 00:00:00"] for place in range(8)],
        "--smallest-group",
        "11",
    )
    edited = copy.deepcopy(document)
    column = _column(edited)
    assert column["all_at_midnight"] is False
    column["all_at_midnight"] = True
    assert "D14" in _refused(tmp_path, edited)


def test_a_labelled_decimal_comma_column_grouped_with_points_is_built(
    tmp_path: pathlib.Path,
) -> None:
    """The profiler's own `.` on a labelled column is one the loader accepts.

    Found closing stage 2: GS1's first version refused a `.` on any block
    nested in another role, and a declared decimal-comma column that
    carries labels beside its numbers publishes exactly that, so
    `generate` refused the description `profile` had just written.
    """
    cells = [f"{1000 + place * 97}.{place % 1000:03d},{place % 100:02d}" for place in range(300)]
    cells += ["pending review"] * 30 + ["not measured"] * 30
    folder = tmp_path / "labelled"
    document = _described(folder, ["v"], [[cell] for cell in cells], "--decimal-comma", "v")
    column = _column(document)
    assert column["role"] == "numbers_with_labels", column["role"]
    numbers = column["numbers"]
    assert isinstance(numbers, dict) and numbers["group_separator"] == "."
    assert _exit_of(
        ["generate", str(folder / "t-profile.json"), "--out-dir", str(folder), "--seed", "4", "--replace"]
    ) == 0
    written = (folder / "t-twin.csv").read_text(encoding="utf-8")
    assert "." in written and "," in written
