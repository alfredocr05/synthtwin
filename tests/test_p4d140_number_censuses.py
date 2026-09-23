"""The final Codex review of the number censuses, reproduced and gated.

Plans P4-D140 to P4-D147. Every test below is built from the review's own
reproduction, run through the real command line: a realistic source is
written, described, twinned, the twin is described again, and BOTH the
twin and the real table are checked against the description.

WHAT IS PINNED HERE:

- the disclosure rule, stated once as `parsing.census_nameable`, and the
  two censuses the review read a single person off: one wide-key spelling
  (`wide_runs`) and one ungrouped price (`thousands_marks`) -- adjacent
  inputs now publish one description, and the loader refuses the counts
  the rule forbids;
- a census of marks is spent as the whole of the grouped cells, the bare
  remainder included, and checked where it names one mark as well as two;
- one evidence rule for both grouping keys, so a declared decimal comma
  publishes a description its own loader reads;
- a declared decimal comma reaches the bare cells beside a unit;
- an exponent that reads back as its value is its own value's spelling;
- a plus does not hide a pad;
- a saturated integer grid keeps every one of its numbers.

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

from synthtwin import contract, errors, parsing


def _exit_of(argv: "list[str]") -> int:
    """Run one synthtwin command in this process and return its exit code.

    Written out here rather than imported, on the ground
    `tests/test_stage2_round_trip.py` states: a helper shared between test
    files ties one gate to another.
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


def _write(path: pathlib.Path, header: "list[str]", rows: "list[list[str]]") -> None:
    path.write_text(fixtures.rows_to_csv(header, rows), encoding="utf-8", newline="")


def _describe(
    folder: pathlib.Path,
    header: "list[str]",
    rows: "list[list[str]]",
    floor: str = "11",
    flags: "tuple[str, ...]" = (),
) -> "tuple[int, pathlib.Path]":
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "real.csv"
    _write(table, header, rows)
    code = _exit_of(
        ["profile", str(table), "--out-dir", str(folder), "--replace",
         "--smallest-group", floor] + list(flags)
    )
    return code, folder / "real-profile.json"


def _block(described: pathlib.Path, index: int = 0) -> "dict[str, object]":
    found: "dict[str, object]" = json.loads(
        described.read_text(encoding="utf-8")
    )["columns"][index]
    return found


def _validate(described: pathlib.Path, target: pathlib.Path, out: pathlib.Path) -> "tuple[int, list[str], str]":
    """Check one file against one description: the exit, the missed lines, the page."""
    out.mkdir(parents=True, exist_ok=True)
    code = _exit_of(
        ["validate", str(described), "--twin", str(target), "--out-dir",
         str(out), "--replace"]
    )
    missed: "list[str]" = []
    page = ""
    for report in sorted(out.glob("*.txt")):
        text = report.read_text(encoding="utf-8")
        page = page + text
        for line in text.splitlines():
            stripped = line.strip()
            if "MISSED" not in stripped:
                continue
            if "CHECKABLE" in stripped or "set by the description" in stripped:
                continue
            missed += [stripped.split(" ")[0]]
    return code, missed, page


def _round_trip(
    folder: pathlib.Path,
    header: "list[str]",
    rows: "list[list[str]]",
    seed: str,
    floor: str = "11",
    flags: "tuple[str, ...]" = (),
) -> "dict[str, object]":
    """Describe, build, describe the twin; check the twin and the real table."""
    code, described = _describe(folder, header, rows, floor, flags)
    assert code == 0
    assert (
        _exit_of(
            ["generate", str(described), "--out-dir", str(folder), "--seed",
             seed, "--replace"]
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
            ["profile", str(copied), "--out-dir", str(again), "--replace",
             "--smallest-group", floor] + list(flags)
        )
        == 0
    )
    written = list(csv.reader(io.StringIO(twin.read_text(encoding="utf-8"))))
    twin_exit, twin_missed, _page = _validate(described, twin, folder / "check-twin")
    real_exit, real_missed, _page = _validate(
        described, folder / "real.csv", folder / "check-real"
    )
    return {
        "described": described,
        "first": _block(described),
        "second": _block(again / "twin-profile.json"),
        "header": written[0],
        "rows": written[1:],
        "twin": twin,
        "twin_exit": twin_exit,
        "twin_missed": twin_missed,
        "real_exit": real_exit,
        "real_missed": real_missed,
    }


# -- P4-D140: the disclosure rule, once --------------------------------


def test_the_rule_names_no_count_and_no_complement_below_the_floor() -> None:
    """The truth table of `parsing.census_nameable`, at floors one and eleven."""
    assert parsing.census_floor(1) == 2
    assert parsing.census_floor(11) == 11
    # Every printed count reaches the census floor...
    assert parsing.census_nameable([11], [], 11)
    assert not parsing.census_nameable([10], [], 11)
    assert not parsing.census_nameable([1], [], 1)
    assert parsing.census_nameable([2], [], 1)
    # ...and so does every complement a reader can take, or it is nought.
    assert parsing.census_nameable([1200], [1200], 11)
    assert not parsing.census_nameable([1199], [1200], 11)
    assert not parsing.census_nameable([1190], [1200], 11)
    assert parsing.census_nameable([1189], [1200], 11)
    # Against EVERY population handed in.
    assert not parsing.census_nameable([800], [800, 801], 11)
    assert parsing.census_nameable([800], [800, 811], 11)
    # A pool is a count like any other.
    assert not parsing.census_nameable([800, 5], [805], 11)


def _wide_keys() -> "list[str]":
    """The review's column: 800 keys past 2**53, each its own value's text."""
    return [str(10**17 + step * 128) for step in range(800)]


def test_one_respelled_wide_key_moves_nothing_a_reader_can_see(
    tmp_path: pathlib.Path,
) -> None:
    """THE FIRST BLOCKER, AS A TEST (plan P4-D140).

    Measured before the repair: cell 432 changed from `100000000000055296`
    to `100000000000055297` -- the same double -- and the two descriptions
    differed ONLY in `wide_runs: canonical` against `respelled`, so a
    reader who knew the other 799 cells read the last one's spelling off
    the word. Now both descriptions are the same bytes, and both files
    still validate at exit 0.
    """
    cells = _wide_keys()
    changed = list(cells)
    changed[432] = "100000000000055297"
    assert float(changed[432]) == float(cells[432])
    kept = _round_trip(tmp_path / "kept", ["code"], [[c] for c in cells], "1")
    moved = _round_trip(tmp_path / "moved", ["code"], [[c] for c in changed], "1")
    assert kept["first"] == moved["first"]
    assert kept["first"]["wide_runs"] == "canonical"
    for run in (kept, moved):
        assert run["twin_exit"] == 0, run["twin_missed"]
        assert run["real_exit"] == 0, run["real_missed"]


def test_a_group_of_respelled_keys_still_moves_the_word_and_the_ceiling_bites(
    tmp_path: pathlib.Path,
) -> None:
    """The word still says what a GROUP of cells does, and the check can fail.

    Eleven respelled keys at a floor of eleven publish `respelled`; the
    canonical description handed a file with eleven respelled keys misses
    `styles.canonical.wide`, and one with ten does not.
    """
    cells = _wide_keys()
    group = list(cells)
    for step in range(11):
        group[step * 50] = f"{int(group[step * 50]) + 1}"
    for place in range(len(cells)):
        assert float(group[place]) == float(cells[place])
    code, described = _describe(tmp_path / "group", ["code"], [[c] for c in group])
    assert code == 0
    assert _block(described)["wide_runs"] == "respelled"
    code, described = _describe(tmp_path / "canon", ["code"], [[c] for c in cells])
    assert code == 0
    assert _block(described)["wide_runs"] == "canonical"
    ten = list(cells)
    for step in range(10):
        ten[step * 50] = f"{int(ten[step * 50]) + 1}"
    for tag, spelled, expected in (("eleven", group, 3), ("ten", ten, 0)):
        target = tmp_path / f"{tag}.csv"
        _write(target, ["code"], [[c] for c in spelled])
        exit_code, missed, _page = _validate(described, target, tmp_path / f"check-{tag}")
        assert exit_code == expected, (tag, missed)
        assert ("styles.canonical.wide" in missed) == (expected == 3), (tag, missed)


def _prices(bare: "set[int]") -> "list[str]":
    return [
        f"{10000 + step}.5" if step in bare else f"{10000 + step:,}.5"
        for step in range(1200)
    ]


def test_one_ungrouped_price_is_not_read_off_by_subtraction(
    tmp_path: pathlib.Path,
) -> None:
    """THE SECOND BLOCKER, AS A TEST (plan P4-D140).

    Measured before the repair: 1,200 grouped prices at a floor of eleven,
    the comma taken off cell 432 alone, published `{",": 1199}` beside a
    row count of 1,200. The one-bare column now publishes no count, the
    all-bare column and the one-grouped column publish the same state, and
    every file still validates.
    """
    grouped = _round_trip(tmp_path / "all", ["v"], [[c] for c in _prices(set())], "4")
    one_bare = _round_trip(tmp_path / "one", ["v"], [[c] for c in _prices({432})], "4")
    assert grouped["first"]["thousands_marks"] == {",": 1200}
    assert one_bare["first"]["thousands_marks"] == {}
    for run in (grouped, one_bare):
        assert run["twin_exit"] == 0, run["twin_missed"]
        assert run["real_exit"] == 0, run["real_missed"]
    # NOUGHT AND ONE ARE ONE STATE where the mark is implied.
    everyone = set(range(1200))
    code, all_bare = _describe(tmp_path / "bare", ["v"], [[c] for c in _prices(everyone)])
    assert code == 0
    code, one_grouped = _describe(
        tmp_path / "onegrouped", ["v"], [[c] for c in _prices(everyone - {432})]
    )
    assert code == 0
    assert _block(all_bare)["thousands_marks"] == {}
    assert _block(one_grouped)["thousands_marks"] == {}
    assert _block(all_bare)["group_separator"] == _block(one_grouped)["group_separator"]


def _without_a_majority() -> "list[str]":
    """600 prices grouped with a comma beside 600 with a space: no mark published."""
    return [
        f"{10000 + i:,}.5" if i < 600 else f"{10000 + i:,}.5".replace(",", " ")
        for i in range(1200)
    ]


@pytest.mark.parametrize(
    "cells,census,refused",
    [
        (_prices(set()), {",": 1199}, "TM1"),
        # On a column publishing NO mark, so that nothing but the refusal
        # of the unavailable state itself can stop it.
        (_without_a_majority(), {"(unavailable)": 0}, "TM1"),
        (_prices(set()), {",": 1200}, ""),
    ],
)
def test_the_loader_refuses_a_census_the_rule_forbids(
    tmp_path: pathlib.Path,
    cells: "list[str]",
    census: "dict[str, int]",
    refused: str,
) -> None:
    """Enforced where a description is READ, not only where it is written."""
    code, described = _describe(tmp_path / "base", ["v"], [[c] for c in cells])
    assert code == 0
    document = json.loads(described.read_text(encoding="utf-8"))
    document["columns"][0]["thousands_marks"] = census
    edited = fixtures.write_profile(tmp_path, "edited-profile.json", document)
    if not refused:
        contract.load_profile(str(edited))
        return
    with pytest.raises(errors.ProfileError) as stopped:
        contract.load_profile(str(edited))
    assert refused in str(stopped.value), str(stopped.value)


@pytest.mark.parametrize(
    "key,cells,census,refused",
    [
        # 1,200 signed decimals: a count leaving ONE unsigned is refused.
        ("decimal_plus", [f"+{10 + step}.5" for step in range(1200)], {"+": 1199}, "DP1"),
        ("decimal_plus", [f"+{10 + step}.5" for step in range(1200)], {"+": 1200}, ""),
        # 600 negatives: notations leaving ONE negative uncounted are refused.
        ("negative_notations", [f"-{10 + step}.5" for step in range(600)], {"minus": 599}, "NS2"),
        ("negative_notations", [f"-{10 + step}.5" for step in range(600)], {"minus": 600}, ""),
    ],
)
def test_the_loader_refuses_a_complement_of_one_on_every_census(
    tmp_path: pathlib.Path,
    key: str,
    cells: "list[str]",
    census: "dict[str, int]",
    refused: str,
) -> None:
    """The same rule on the two sibling censuses, read where a description is read."""
    code, described = _describe(tmp_path / "base", ["v"], [[c] for c in cells])
    assert code == 0
    document = json.loads(described.read_text(encoding="utf-8"))
    document["columns"][0][key] = census
    edited = fixtures.write_profile(tmp_path, "edited-profile.json", document)
    if not refused:
        contract.load_profile(str(edited))
        return
    with pytest.raises(errors.ProfileError) as stopped:
        contract.load_profile(str(edited))
    assert refused in str(stopped.value), str(stopped.value)


# -- P4-D142: the census of marks is the whole of the grouped cells ----------


def _marks_of(rows: "list[list[str]]") -> "dict[str, int]":
    counted: "dict[str, int]" = {}
    for row in rows:
        cell = row[0]
        mark = "bare"
        for candidate in (",", " "):
            if candidate in cell:
                mark = candidate
        counted[mark] = counted.get(mark, 0) + 1
    return counted


GROUPING_SHAPES = {
    "comma-and-bare": ([f"{10000 + i:,}.5" if i < 800 else f"{10000 + i}.5" for i in range(1200)], {",": 800, "bare": 400}),
    "comma-space-bare": (
        [
            f"{10000 + i:,}.5" if i < 800 else (
                f"{10000 + i:,}.5".replace(",", " ") if i < 1000 else f"{10000 + i}.5"
            )
            for i in range(1200)
        ],
        {",": 800, " ": 200, "bare": 200},
    ),
    "no-majority": (
        [f"{10000 + i:,}.5" if i < 600 else f"{10000 + i:,}.5".replace(",", " ") for i in range(1200)],
        {",": 600, " ": 600},
    ),
}


@pytest.mark.parametrize("shape", sorted(GROUPING_SHAPES))
def test_every_published_mark_count_and_the_bare_remainder_come_back(
    shape: str, tmp_path: pathlib.Path
) -> None:
    """THE REVIEW'S ITEM 3, its three shapes, at seed 4 and a floor of eleven.

    Measured before the repair: `comma-and-bare` twinned as 1,200 grouped
    cells with nothing missed and nothing withheld; `comma-space-bare` as
    1,000 commas and 200 spaces with the check withheld; and `no-majority`
    as no grouped cell at all.
    """
    cells, expected = GROUPING_SHAPES[shape]
    run = _round_trip(tmp_path / shape, ["v"], [[c] for c in cells], "4")
    assert _marks_of(run["rows"]) == expected
    assert run["second"]["thousands_marks"] == run["first"]["thousands_marks"]
    assert run["twin_exit"] == 0, run["twin_missed"]
    assert run["real_exit"] == 0, run["real_missed"]


@pytest.mark.parametrize(
    "shape,rewrite",
    [
        ("comma-and-bare", "group-every-cell"),
        ("no-majority", "strip-every-mark"),
    ],
)
def test_a_twin_losing_the_census_is_missed_not_withheld(
    shape: str, rewrite: str, tmp_path: pathlib.Path
) -> None:
    """The check can fail, on the two writings the generator used to produce."""
    cells, _expected = GROUPING_SHAPES[shape]
    run = _round_trip(tmp_path / shape, ["v"], [[c] for c in cells], "4")
    spoiled: "list[list[str]]" = []
    for row in run["rows"]:
        cell = row[0]
        if rewrite == "group-every-cell" and "," not in cell:
            whole, _point, rest = cell.partition(".")
            cell = f"{int(whole):,}.{rest}"
        if rewrite == "strip-every-mark":
            cell = cell.replace(",", "").replace(" ", "")
        spoiled += [[cell]]
    target = tmp_path / "spoiled.csv"
    _write(target, run["header"], spoiled)
    code, missed, _page = _validate(run["described"], target, tmp_path / "check-spoiled")
    assert code == 3
    assert "spelling.thousands_marks" in missed, missed


# -- P4-D141: one evidence rule for both grouping keys -----------------


def test_a_declared_decimal_comma_with_two_marks_publishes_a_loadable_description(
    tmp_path: pathlib.Path,
) -> None:
    """THE REVIEW'S ITEM 7, AS A TEST.

    Measured before the repair: `group_separator: "."` beside
    `thousands_marks: {" ": 20}`, which the loader refuses under TM1, so
    the table could not be twinned at all. With a unit on every cell the
    same held.
    """
    for suffix in ("", " EUR"):
        cells = [f"{1097 + i}.001,01{suffix}" for i in range(780)]
        cells += [f"{197 + i} 001,01{suffix}" for i in range(20)]
        folder = tmp_path / f"marks{len(suffix)}"
        run = _round_trip(folder, ["v"], [[c] for c in cells], "1", flags=("--decimal-comma", "v"))
        assert run["first"]["group_separator"] == "."
        assert run["first"]["thousands_marks"] == {" ": 20, ".": 780}
        assert run["twin_exit"] == 0, run["twin_missed"]
        assert run["real_exit"] == 0, run["real_missed"]


# -- P4-D143: a declared decimal comma reaches bare cells beside a unit ---


@pytest.mark.parametrize("wrapped", [600, 400])
def test_bare_prices_beside_a_unit_are_read_in_the_declared_grammar(
    wrapped: int, tmp_path: pathlib.Path
) -> None:
    """THE REVIEW'S ITEM 4, AS A TEST.

    Measured before the repair: with 600 of 800 cells wearing ` EUR` the
    description published `n_affixed: 600`, which its own loader refuses;
    with 400 the column fell to free text.
    """
    cells = [f"{100 + i},25" + (" EUR" if i < wrapped else "") for i in range(800)]
    run = _round_trip(
        tmp_path / f"eur{wrapped}", ["price"], [[c] for c in cells], "1",
        flags=("--decimal-comma", "price"),
    )
    assert run["first"]["role"] == "affixed_number"
    assert run["first"]["n_affixed"] == 800
    for row in run["rows"]:
        if row[0]:
            assert "," in row[0] and "." not in row[0], row[0]
    assert run["twin_exit"] == 0, run["twin_missed"]
    assert run["real_exit"] == 0, run["real_missed"]


# -- P4-D144: an exponent that reads back is its own value's spelling ----


@pytest.mark.parametrize(
    "shape", ["precise", "engineering", "two_before_the_point", "zero_before_the_point"]
)
def test_a_real_exponent_export_meets_its_own_description(
    shape: str, tmp_path: pathlib.Path
) -> None:
    """THE REVIEW'S ITEM 5, AS A TEST.

    Measured before the repair: `%.18e` failed its own description on 799
    spellings of 800, and `1200e-3` engineering notation failed too. The
    last two shapes put the point somewhere other than after the first
    figure -- `12.00e2` and `0.01200e5` -- which the repair pass found no
    test depended on: a validator refusing a point away from the first
    figure passed every shape above.
    """
    draw = random.Random(23)
    if shape == "precise":
        cells = [f"{draw.uniform(10, 999):.18e}" for _ in range(800)]
    elif shape == "engineering":
        cells = [f"{1200 + i}e-3" for i in range(800)]
    elif shape == "two_before_the_point":
        cells = [f"{12 + i / 100:.2f}e2" for i in range(800)]
    else:
        cells = [f"0.0{1200 + i}e5" for i in range(800)]
    run = _round_trip(tmp_path / shape, ["v"], [[c] for c in cells], "1")
    assert run["real_exit"] == 0, run["real_missed"]
    assert run["twin_exit"] == 0, run["twin_missed"]


# -- P4-D145: a plus does not hide a pad -------------------------------


def test_plus_signed_padded_keys_keep_their_field(tmp_path: pathlib.Path) -> None:
    """THE REVIEW'S ITEM 6, AS A TEST, and the check that can fail.

    Measured before the repair: `field_widths {"20": 800}` beside
    `pad_widths {}`, and every 21-character source cell written as 19
    characters with nothing missed.
    """
    cells = ["+" + str(10**17 + i * 128).rjust(20, "0") for i in range(800)]
    run = _round_trip(tmp_path / "plus", ["v"], [[c] for c in cells], "1")
    assert run["first"]["pad_widths"] == {"20": 800}
    assert run["second"]["pad_widths"] == {"20": 800}
    for row in run["rows"]:
        assert len(row[0]) == 21 and row[0][:2] == "+0", row[0]
    assert run["twin_exit"] == 0, run["twin_missed"]
    assert run["real_exit"] == 0, run["real_missed"]
    stripped = [["+" + row[0][1:].lstrip("0")] for row in run["rows"]]
    target = tmp_path / "stripped.csv"
    _write(target, run["header"], stripped)
    code, missed, _page = _validate(run["described"], target, tmp_path / "check-stripped")
    assert code == 3
    assert "pads.published.20" in missed, missed


# -- P4-D147: a saturated integer grid keeps every number ---------------


@pytest.mark.parametrize("seed", ["4", "1", "7"])
def test_a_saturated_integer_grid_keeps_every_number(
    seed: str, tmp_path: pathlib.Path
) -> None:
    """THE MERGE REVIEW'S ITEM 6, AS A TEST.

    Measured before the repair: 400 different spellings of 395, 392 and 391
    numbers at seeds 4, 1 and 7, with `distinct.n_distinct_values` MISSED
    on the twin while the real table met it.
    """
    rows = [[f"+{i}.0", f"row{i % 7}"] for i in range(1, 401)]
    run = _round_trip(tmp_path / f"grid{seed}", ["value", "other"], rows, seed, floor="1")
    values = [row[0] for row in run["rows"]]
    assert len(set(values)) == 400
    assert len({float(value) for value in values}) == 400
    for value in values:
        assert float(value) == int(float(value)), value
    assert run["twin_exit"] == 0, run["twin_missed"]
    assert run["real_exit"] == 0, run["real_missed"]


def test_a_plus_is_never_padded_past_the_census_of_padded_plus_cells(
    tmp_path: pathlib.Path,
) -> None:
    """The second tier's bound (plan P4-D145), on a column with no padded plus.

    Eight `+1`, eight `-99` and nine `-02`: every padded cell of the source
    is `leading_zero`, so the census holds no plus-signed padded cell. The
    twin draws eight values for the nine padded cells, and without the
    bound the second tier made up the count with `+01`, a spelling no cell
    of the source wore.
    """
    # AT THE POPULATION FLOOR ON ABSENT CELLS (plan P4-D341): the
    # command refuses a smaller table and writes nothing, while the
    # shape here is the NINE padded cells and the sixteen unpadded ones
    # beside them. `NA` is one of this format's own spellings for "no
    # value", so the padded census -- and the twin's draw against it --
    # are exactly what the shape produced before.
    rows = [["+1"]] * 8 + [["-99"]] * 8 + [["-02"]] * 9
    rows = rows + [["NA"]] * (parsing.POPULATION_FLOOR - len(rows))
    for seed in ("3", "11", "29"):
        run = _round_trip(tmp_path / f"signed{seed}", ["reading"], rows, seed, floor="1")
        assert run["first"]["pad_widths"] == {"2": 9}
        written = {row[0] for row in run["rows"] if row[0]}
        assert not [cell for cell in written if cell[:2] == "+0"], written


# -- P4-D148, P4-D149 and P4-D145's amendment: the repair pass --------------


def _codes(extra: "list[str]", plus: bool) -> "list[list[str]]":
    """800 padded five-figure codes beside fifty short ones, and ``extra``."""
    cells = [f"{100 + i % 900:05d}" if not plus else f"{100 + i:05d}" for i in range(800)]
    cells += [f"+{k + 1}" if plus else str(k + 1) for k in range(50)]
    cells += extra
    return [[cell, f"r{index % 7}"] for index, cell in enumerate(cells)]


def _rest(block: "dict[str, object]", key: str, width: str) -> int:
    census = block[key]
    assert isinstance(census, dict)
    return int(census[width]) if width in census else 0


@pytest.mark.parametrize(
    "plus,extra",
    [(False, "12345"), (True, "+00123")],
)
def test_the_width_censuses_leave_no_one_to_subtract(
    plus: bool, extra: str, tmp_path: pathlib.Path
) -> None:
    """THE REPAIR PASS'S BLOCKER, AS A TEST (plan P4-D148).

    Measured before: 800 padded codes and fifty short ones beside one
    unpadded `12345` published `field_widths {"5": 801}` beside `pad_widths
    {"5": 800}`, and beside one `+00123` published `pad_widths {"5": 801}`
    beside `leading_zero: 800` -- each difference exactly one person. Now
    every difference a reader can take is nought or a group, and every
    file validates.
    """
    floor = 11
    for label, rows in (("without", _codes([], plus)), ("with", _codes([extra], plus))):
        run = _round_trip(
            tmp_path / label, ["code", "label"], rows, "4", floor=str(floor)
        )
        block = run["first"]
        styles = block["numeric_styles"]
        assert isinstance(styles, dict)
        padded = block["pad_widths"]
        assert isinstance(padded, dict)
        plus_cells = sum(padded.values()) - int(styles.get("leading_zero", 0))
        assert plus_cells == 0 or plus_cells >= floor, block
        unpadded = _rest(block, "field_widths", "5") - _rest(block, "pad_widths", "5")
        if "5" in block["field_widths"]:  # type: ignore[operator]
            assert unpadded == 0 or unpadded >= floor, block
        # THE TWIN OF THE CODES WITH ONE `12345` MISSES ITS MEAN, and says
        # so (measured at the merge of this repair into the integration).
        # That one far value is the column's maximum: the real mean is
        # 485.57 and the twin, spreading the top rung's stretch between
        # 999 and 12345, holds 528.4 to 530.7 on seeds 0 to 7, outside a
        # window (497.1 to 580.3) that does not reach the published value.
        # This branch passed it on the window alone; the integration's
        # V6.1-A2 no longer takes such a window as a pass, and it is right
        # not to. It is the tail defect of STATE landing 3, not a census
        # this test is about, so the miss is pinned to the mean alone.
        if label == "with" and not plus:
            assert run["twin_exit"] == 3, run["twin_missed"]
            assert set(run["twin_missed"]) == {"moments.mean"}, run["twin_missed"]
        else:
            assert run["twin_exit"] == 0, run["twin_missed"]
        assert run["real_exit"] == 0, run["real_missed"]
        if label == "with":
            # SINCE PLAN P4-D222 (stage 2 closed by the owner rulings of
            # 2026-09-17) the one unpadded five-figure cell is counted into
            # the commonest unpadded width, so no whole-number width of five
            # is left over the padded count.
            assert block["field_widths"] == {"2": 51, "5": 800}, block
            assert block["pad_widths"] == {"5": 800}, block


@pytest.mark.parametrize(
    "key,census,refused",
    [
        ("field_widths", {"(withheld)": 9, "2": 41, "5": 801}, "P6c"),
        ("pad_widths", {"5": 801}, "P5b"),
    ],
)
def test_the_loader_refuses_a_width_complement_of_one(
    key: str, census: "dict[str, int]", refused: str, tmp_path: pathlib.Path
) -> None:
    """Enforced where a description is READ (plan P4-D148)."""
    rows = _codes(["12345" if key == "field_widths" else "+00123"], key == "pad_widths")
    code, described = _describe(tmp_path / "base", ["code", "label"], rows)
    assert code == 0
    document = json.loads(described.read_text(encoding="utf-8"))
    document["columns"][0][key] = census
    edited = fixtures.write_profile(tmp_path, "edited-profile.json", document)
    with pytest.raises(errors.ProfileError) as stopped:
        contract.load_profile(str(edited))
    assert refused in str(stopped.value), str(stopped.value)


def test_a_held_back_padded_form_publishes_no_width_its_twin_misses(
    tmp_path: pathlib.Path,
) -> None:
    """Plan P4-D145's amendment: a regression the plus-signed pad brought, measured.

    Eight values written `+0100` twice and `0100` once at a floor of eleven
    published `pad_widths {"4": 24}` beside a held-back `leading_zero`, and
    the twin -- writing the held-back cells as their own values are --
    missed `pads.published.4` at exit 3.
    """
    # THE EIGHT VALUES STAY EIGHT AND THE TABLE REACHES THE POPULATION
    # FLOOR ON ABSENT CELLS (plan P4-D341). The shape is that the eight
    # plainly written cells are BELOW the floor of eleven and so are
    # held back into the commonest form; grown to thirty-four values
    # they clear it, publish `leading_zero` themselves and the
    # reproduction is gone. `NA` is one of this format's own spellings
    # for "no value", so every numeric census over the twenty-four
    # present cells is the one this witness was written with.
    values = 8
    rows = []
    for value in range(100, 100 + values):
        for turn in range(3):
            rows += [[f"+0{value}" if turn % 2 == 0 else f"0{value}"]]
    present = len(rows)
    rows = rows + [["NA"]] * (parsing.POPULATION_FLOOR - present)
    run = _round_trip(tmp_path / "pooled", ["offset"], rows, "4")
    # THE EIGHT PADDED CELLS ARE COUNTED INTO THE PLUS-SIGNED FORM (plan
    # P4-D222; stage 2 closed by the owner rulings of 2026-09-17), where
    # plan P4-D221 pooled the whole map with them. Counting the sixteen
    # plus-signed padded cells as padded would leave eight plus-signed
    # cells unpadded by subtraction, so the padded census counts none and
    # the twin misses no width.
    assert run["first"]["numeric_styles"] == {"leading_plus": present}
    assert run["first"]["pad_widths"] == {}
    assert run["twin_exit"] == 0, run["twin_missed"]
    assert run["real_exit"] == 0, run["real_missed"]
    # ...AND THE LOADER REFUSES THE CENSUS THAT WOULD LEAVE EIGHT BY
    # SUBTRACTION (P5b).
    document = json.loads(run["described"].read_text(encoding="utf-8"))
    document["columns"][0]["pad_widths"] = {"4": 2 * values}
    edited = fixtures.write_profile(tmp_path, "edited-profile.json", document)
    with pytest.raises(errors.ProfileError) as stopped:
        contract.load_profile(str(edited))
    assert "P5b" in str(stopped.value), str(stopped.value)


def _mean(values: "list[float]") -> float:
    return sum(values) / len(values)


def test_grouped_and_bare_amounts_keep_their_sizes(tmp_path: pathlib.Path) -> None:
    """THE REPAIR PASS'S GROUPING FINDING, AS A TEST (plan P4-D149).

    Measured before: 1,500 amounts, 915 grouped and 585 bare with means of
    489,137 and 483,357, came back with a grouped mean of 289,169 and a bare
    mean of 795,007, every bare cell larger than every grouped one.
    """
    draw = random.Random(11)
    rows = []
    for index in range(1500):
        value = draw.randint(1000, 999999) + 0.25
        text = f"{value:,.2f}" if draw.random() < 0.6 else f"{value:.2f}"
        rows += [[text, f"r{index % 5}"]]
    run = _round_trip(tmp_path / "amounts", ["amount", "label"], rows, "4")
    grouped = [float(row[0].replace(",", "")) for row in run["rows"] if "," in row[0]]
    bare = [float(row[0]) for row in run["rows"] if row[0] and "," not in row[0]]
    assert grouped and bare
    overall = _mean(grouped + bare)
    assert abs(_mean(grouped) - _mean(bare)) < 0.1 * overall, (_mean(grouped), _mean(bare))
    assert min(bare) < max(grouped)
    assert run["twin_exit"] == 0, run["twin_missed"]
    assert run["real_exit"] == 0, run["real_missed"]


def test_bracketed_and_minus_debts_keep_their_sizes(tmp_path: pathlib.Path) -> None:
    """The same finding on the census of negative notations (plan P4-D149)."""
    draw = random.Random(12)
    rows = []
    for index in range(1200):
        value = draw.randint(1, 99999) + 0.5
        text = f"({value:.2f})" if draw.random() < 0.3 else f"-{value:.2f}"
        rows += [[text, f"r{index % 5}"]]
    run = _round_trip(tmp_path / "debts", ["debt", "label"], rows, "4")
    assert set(run["first"]["negative_notations"]) == {"brackets", "minus"}  # type: ignore[arg-type]
    brackets = [float(row[0][1:-1]) for row in run["rows"] if row[0][:1] == "("]
    minus = [-float(row[0]) for row in run["rows"] if row[0][:1] == "-"]
    assert brackets and minus
    overall = _mean(brackets + minus)
    assert abs(_mean(brackets) - _mean(minus)) < 0.1 * overall, (_mean(brackets), _mean(minus))
    assert run["twin_exit"] == 0, run["twin_missed"]
    assert run["real_exit"] == 0, run["real_missed"]


@pytest.mark.parametrize("seed", ["1", "4"])
def test_offsets_written_both_ways_keep_their_spellings_and_widths(
    seed: str, tmp_path: pathlib.Path
) -> None:
    """THE REPAIR PASS'S DISTINCTNESS FINDING, AS A TEST (plan P4-D145).

    Measured before: 1,200 offsets written `+0123` or `0123` publish 917
    spellings; the twin kept every width but held 776 and 768 spellings on
    seeds 1 and 4, reported as an authorized deviation.
    """
    draw = random.Random(5)
    rows = []
    for _index in range(1200):
        offset = draw.randint(0, 999)
        text = f"+{offset:04d}" if draw.random() < 0.6 else f"{offset:04d}"
        change = draw.randint(-5000, 5000) / 100
        rows += [[text, f"{change:+.2f}"]]
    run = _round_trip(tmp_path / f"offsets{seed}", ["offset", "delta"], rows, seed)
    written = [row[0] for row in run["rows"]]
    assert len(set(written)) == run["first"]["n_distinct"]
    assert run["second"]["pad_widths"] == run["first"]["pad_widths"]
    assert run["twin_exit"] == 0, run["twin_missed"]
    assert run["real_exit"] == 0, run["real_missed"]
