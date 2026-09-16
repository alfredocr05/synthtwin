"""Landing 2b.18's repair pass: what a census of layouts may say, and to whom.

The skeptic's verdict on landing 2b.18 found one defect the disclosure
rule forbids outright and four shapes of record number the census still
lost, every one of them silent or failing its own description. Each was
reproduced on the landing's own commit before anything here was built:

- **A count of one, a pool of one and a complement of one** (plan
  P4-D124). `REC` and seven figures on 799 rows beside one `TMP-42`
  published `{"@@@%%%%%%%": 799, "@@@-%%": 1}`; 800 random codes
  published 56 layouts of one cell; a UUID column with one upper-case row
  published 800 masks of one cell each; at a floor of eleven the odd row
  became `(withheld): 1`; and one `REC 123456` left `799` against 800
  present cells.
- **A short hexadecimal token** (plan P4-D125). Eight lower-case or six
  upper-case hexadecimal characters published a layout led by a nought,
  which the twin could not fill, and the twin failed its own description
  at exit 3 on five runs of five, writing `A-------`.
- **A zero fill's width** (plan P4-D126). `%08d` over 1 to 499,999 opened
  `00` on 800 real cells and 78 twin cells.
- **A national number written in groups** (plan P4-D127). `657 240 7282`
  published no layout at all, and the twin wrote `!          5`.
- **The cells no named layout serves** (plan P4-D128). 800 random codes of
  capitals and figures at a floor of eleven pooled 448 cells, and the twin
  wrote them `A-----2S`, so `[A-Z0-9]{8}` matched 800 real cells and 352
  twin cells; and the figures of every filling leaned on the nought, 44.8
  per cent of them on a thirteen-figure code against 11.4 per cent real.

Every shape is a ROUND TRIP -- described, built, described again, the
census asserted to come back, and BOTH files validated at exit 0 -- with a
regular expression, a length test and a case test written against the
twin and run UNCHANGED on the real table, asserting the same match count
on both. Every table is built by seeded neutral code at runtime (plan D13).
"""

import pathlib
import random
import re
import tempfile

import pytest

from synthtwin import parsing, profile, reading, taxonomy
from tests import fixtures
from tests.test_landing_2b18_identifier_layout import _round_trip

ROWS = 800
SOURCE_SEEDS = (1, 2, 3)
HEX = "0123456789abcdef"


# ------------------------------------------------------------- the shapes


def hex_token_cells(seed: int, width: int, upper: bool) -> "list[str]":
    """A bare hexadecimal token of one width and one case."""
    draw = random.Random(seed)
    alphabet = HEX.upper() if upper else HEX
    return [
        "".join(draw.choice(alphabet) for _c in range(width))
        for _row in range(ROWS)
    ]


def small_padded_cells(seed: int) -> "list[str]":
    """`%08d` over numbers well short of the width: a fill two or more deep."""
    draw = random.Random(seed)
    return [f"{draw.randrange(1, 500000):08d}" for _row in range(ROWS)]


def grouped_number_cells(seed: int) -> "list[str]":
    """A national number written in three groups: `657 240 7282`."""
    draw = random.Random(seed)
    return [
        f"{draw.randrange(400, 800)} {draw.randrange(1000):03d} "
        f"{draw.randrange(10000):04d}"
        for _row in range(ROWS)
    ]


def one_capital_uuid_cells(seed: int) -> "list[str]":
    """799 lower-case UUIDs and one written in capitals."""
    draw = random.Random(seed)
    built = []
    for row in range(ROWS):
        figures = "".join(draw.choice(HEX) for _c in range(32))
        value = (
            f"{figures[:8]}-{figures[8:12]}-{figures[12:16]}"
            f"-{figures[16:20]}-{figures[20:]}"
        )
        built += [value.upper() if row == 17 else value]
    return built


def alphanumeric_cells(seed: int) -> "list[str]":
    """Eight capitals and figures in any order: a booking reference."""
    draw = random.Random(seed)
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return [
        "".join(draw.choice(alphabet) for _c in range(8)) for _row in range(ROWS)
    ]


def _count(cells: "list[str]", test) -> int:
    return len([cell for cell in cells if test(cell)])


def _three_checks(real, twin, pattern, length, case) -> None:
    """The regex, the length test and the case test, equal on both files."""
    rule = re.compile(pattern)
    for name, test in (
        ("regex", lambda cell: rule.fullmatch(cell) is not None),
        ("length", length),
        ("case", case),
    ):
        assert _count(real, test) == _count(twin, test), (
            name, _count(real, test), _count(twin, test)
        )


def _no_disclosure(column: dict) -> None:
    """No count of one, no pool of one, no total left over by one."""
    census = column["layout_forms"]
    for key in census:
        assert census[key] >= 2, (key, census[key])
    named = sum(census.values())
    assert column["n_present"] - named != 1
    covered_code = sum(
        census[key]
        for key in census
        if key != "(withheld)" and set(key) <= set("%@&~^!-_")
    )
    if covered_code:
        assert column["n_code_alphabet"] - covered_code != 1


SHAPES = {
    # P4-D125: the hexadecimal tokens the landing's own shapes never reached.
    "hex_lower_8": (
        lambda seed: hex_token_cells(seed, 8, False),
        None,
        r"[0-9a-f]{8}",
        lambda cell: len(cell) == 8,
        lambda cell: cell.lower() == cell,
    ),
    "hex_upper_6": (
        lambda seed: hex_token_cells(seed, 6, True),
        None,
        r"[0-9A-F]{6}",
        lambda cell: len(cell) == 6,
        lambda cell: cell.upper() == cell,
    ),
    # P4-D126: the width of the fill, which `lstrip` code reads.
    "small_padded": (
        small_padded_cells,
        None,
        r"00[0-9]{6}",
        lambda cell: len(cell.lstrip("0")) <= 5,
        lambda cell: cell.isdigit(),
    ),
    # P4-D127: a space between groups.
    "grouped_number": (
        grouped_number_cells,
        None,
        r"[0-9]{3} [0-9]{3} [0-9]{4}",
        lambda cell: len(cell) == 12,
        lambda cell: " " in cell,
    ),
    # P4-D128: the cells a floor of eleven pools, written to mixes.
    "alphanumeric_floor_11": (
        alphanumeric_cells,
        11,
        r"[A-Z0-9]{8}",
        lambda cell: len(cell) == 8,
        lambda cell: cell.upper() == cell,
    ),
    # P4-D124 and P4-D128: at a floor of one the layouts of one cell are
    # no longer named, and their cells are written to mixes.
    "alphanumeric_floor_1": (
        alphanumeric_cells,
        None,
        r"[A-Z0-9]{8}",
        lambda cell: len(cell) == 8,
        lambda cell: any("0" <= c <= "9" for c in cell),
    ),
}


@pytest.mark.parametrize("name", sorted(SHAPES))
@pytest.mark.parametrize("source_seed", SOURCE_SEEDS)
def test_the_twin_wears_the_layouts_the_census_may_publish(
    name: str, source_seed: int, tmp_path: pathlib.Path
) -> None:
    """The round trip, the disclosure rule, and three checks on both files."""
    make, floor, pattern, length, case = SHAPES[name]
    cells = make(source_seed)
    got = _round_trip(tmp_path / f"{name}-{source_seed}", cells, floor=floor)
    published = got["source"]["layout_forms"]
    assert published, f"{name} publishes no layout at all"
    _no_disclosure(got["source"])
    assert got["twin_profile"]["layout_forms"] == published, (
        f"{name}: published {published}, the twin described again says "
        f"{got['twin_profile']['layout_forms']}"
    )
    assert got["twin_exit"] == 0, f"{name}: the twin misses its description"
    assert got["real_exit"] == 0, f"{name}: the table misses its description"
    _three_checks(cells, got["cells"], pattern, length, case)


@pytest.mark.parametrize("source_seed", SOURCE_SEEDS)
def test_a_hexadecimal_column_is_one_convention_whatever_one_cell_s_case(
    source_seed: int, tmp_path: pathlib.Path
) -> None:
    """P4-D125: one upper-case UUID no longer turns the column plain.

    On the landing's commit the column published 800 masks of one cell at
    a floor of one -- each the letter-and-figure mask of one person's UUID
    -- and `{"(withheld)": 800}` at a floor of eleven, where the twin wrote
    `A----...J` on every row. The census is now one layout at both floors.

    THE CASE OF THE ONE CELL IS NOT CARRIED, and that is the disclosure
    rule rather than a defect: it is a count of one. So the case-blind
    pattern matches every cell of both files, and the lower-case test
    counts 799 real cells and 800 twin cells, which this test pins.
    """
    cells = one_capital_uuid_cells(source_seed)
    layout = "~~~~~~~~-~~~~-~~~~-~~~~-~~~~~~~~~~~~"
    for floor in (None, 11):
        got = _round_trip(
            tmp_path / f"uuid-{source_seed}-{floor}", cells, floor=floor
        )
        assert got["source"]["layout_forms"] == {layout: ROWS}
        assert got["twin_exit"] == 0 and got["real_exit"] == 0
        rule = r"(?i)[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
        _three_checks(
            cells,
            got["cells"],
            rule,
            lambda cell: len(cell) == 36,
            lambda cell: cell.count("-") == 4,
        )
        lower = lambda cell: cell.lower() == cell  # noqa: E731
        assert (_count(cells, lower), _count(got["cells"], lower)) == (
            ROWS - 1, ROWS
        )


@pytest.mark.parametrize("source_seed", SOURCE_SEEDS)
def test_every_depth_of_fill_the_census_names_comes_back(
    source_seed: int, tmp_path: pathlib.Path
) -> None:
    """P4-D126: the fill is marked nought by nought, and read the same way.

    `^0`, `^00` and `^000` count the same cells on both files: each depth
    the census names is written at exactly that depth, and a depth too
    rare to name was counted under the next shallower one, which is true of
    it. On the landing's commit `^00` counted 800 real cells and 78 twin.
    """
    cells = small_padded_cells(source_seed)
    got = _round_trip(tmp_path / f"fill-{source_seed}", cells)
    published = got["source"]["layout_forms"]
    assert all(key[:2] == "!!" for key in published), published
    deepest = max(parsing.layout_fill(key) for key in published)
    for depth in range(1, deepest + 1):
        opens = lambda cell, d=depth: cell[:d] == "0" * d  # noqa: E731
        assert _count(cells, opens) == _count(got["cells"], opens), depth
    assert got["twin_exit"] == 0 and got["real_exit"] == 0


# ------------------------------------------------ the disclosure rule, alone


def _describe(values: "list[str]", floor: int) -> dict:
    """The identifier block of one declared column, at a chosen floor."""
    folder = pathlib.Path(tempfile.mkdtemp())
    rows = [[value, f"row{index % 7}"] for index, value in enumerate(values)]
    table = fixtures.write(
        folder, "thing.csv", fixtures.rows_to_csv(["value", "other"], rows)
    )
    document = profile.build_document(
        reading.read_table(f"{table}"),
        taxonomy.Settings(small_cell_floor=floor),
        ["value"],
    )
    return document["columns"][0]


def _records(seed: int, rows: int) -> "list[str]":
    draw = random.Random(seed)
    return [f"REC{draw.randrange(1000000, 9999999)}" for _row in range(rows)]


@pytest.mark.parametrize("floor", (1, 11))
def test_one_odd_row_is_never_counted_or_left_over(floor: int) -> None:
    """P4-D124, on the skeptic's own reproductions.

    Measured on the landing's commit: `{"@@@%%%%%%%": 799, "@@@-%%": 1}` at
    a floor of one, `{"(withheld)": 1, "@@@%%%%%%%": 799}` at eleven, and
    `{"@@@%%%%%%%": 799}` beside 800 present cells for the spaced odd row
    at both. WHAT IT COSTS, stated rather than hidden: a column whose one
    named layout would leave one cell over publishes no layout at all.
    """
    for odd in ("TMP-42", "REC 123456", "REC1234  5"):
        values = _records(1, ROWS - 1)
        values = values[:300] + [odd] + values[300:]
        column = _describe(values, floor)
        _no_disclosure(column)
        assert column["layout_forms"] == {}, (odd, column["layout_forms"])


def test_the_smallest_layout_is_taken_back_and_the_rest_stay() -> None:
    """P4-D124: a second system keeps the census once one layout goes.

    573 cells of `REC` and seven figures, 226 of `E` and six, and one
    `TMP-42`: the smallest named layout is taken back, which leaves 227
    cells over, and the larger one is still published.
    """
    draw = random.Random(5)
    values = _records(5, 573) + [
        f"E{draw.randrange(100000, 999999)}" for _row in range(226)
    ] + ["TMP-42"]
    column = _describe(values, 1)
    assert column["layout_forms"] == {"@@@%%%%%%%": 573}
    _no_disclosure(column)


def test_a_layout_of_one_cell_is_never_named_and_its_cells_are_left_over() -> None:
    """P4-D124: on 800 random codes, 56 layouts of one cell reached the page."""
    column = _describe(alphanumeric_cells(1), 1)
    census = column["layout_forms"]
    assert census and min(census.values()) >= 2
    assert column["n_present"] - sum(census.values()) >= 2
    _no_disclosure(column)


def test_a_complement_of_one_inside_the_code_alphabet_is_taken_back() -> None:
    """P4-D124: the totals a reader subtracts from are not only `n_present`.

    700 codes of `REC` and seven figures, 97 of `REC.` and six figures, one
    code `AB-12` and two cells holding a double space, which no layout
    describes. Against `n_present` three cells are left over; against
    `n_code_alphabet`, which counts the 700 and `AB-12`, ONE would be --
    so the code-alphabet layout is taken back and the other stays.
    """
    draw = random.Random(9)
    values = (
        _records(9, 700)
        + [f"REC.{draw.randrange(100000, 999999)}" for _row in range(97)]
        + ["AB-12", "AB  12345", "CD  67890"]
    )
    column = _describe(values, 1)
    assert column["n_code_alphabet"] == 701
    assert column["layout_forms"] == {"@@@.%%%%%%": 97}
    _no_disclosure(column)


def test_the_count_before_the_whole_census_rule_is_every_named_layout() -> None:
    """`layout_census` is the per-layout rules alone, which the validator reads."""
    values = _records(1, ROWS - 1) + ["TMP-42"]
    assert taxonomy.layout_census(values, 1, len(set(values))) == {
        "@@@%%%%%%%": ROWS - 1
    }
    assert _describe(values, 1)["layout_forms"] == {}


def test_a_conforming_file_is_not_told_it_lost_a_layout_it_holds(
    tmp_path: pathlib.Path,
) -> None:
    """P4-D124: the validator recounts the census, not the file's own census.

    The table holds 700 codes `@@@%%%%%%%`, two `@@@.%%%%%%` and 98 cells
    with a double space, so it publishes both layouts with 98 cells over.
    The checked file holds the same 700 and two, 97 cells `@@@,%%%%%%` and
    ONE cell with a double space: it meets every published fact. Its own
    description would leave one cell over, take back the smallest layout
    -- the published two -- and, read off that description, the file would
    be told it MISSED a layout it holds at the published count.
    """
    from tests.test_stage2_round_trip import _exit_of

    draw = random.Random(3)
    codes = _records(3, 702)
    shared = codes[:700] + [
        f"{codes[700][:3]}.{codes[700][4:]}",
        f"{codes[701][:3]}.{codes[701][4:]}",
    ]
    spaced = [f"AB  {100000 + index}" for index in range(98)]
    commas = [
        f"XYZ,{draw.randrange(100000, 999999)}" for _row in range(97)
    ]
    real = shared + spaced
    checked = shared + commas + ["ZZ  999999"]
    assert len(set(checked)) == len(checked) == len(real) == len(set(real))

    def write(name: str, values: "list[str]") -> pathlib.Path:
        path = tmp_path / name
        path.write_text(
            fixtures.rows_to_csv(
                ["value", "other"],
                [[value, f"row{index % 7}"] for index, value in enumerate(values)],
            ),
            encoding="utf-8",
            newline="",
        )
        return path

    table = write("real.csv", real)
    assert _exit_of(
        ["profile", str(table), "--out-dir", str(tmp_path), "--replace",
         "--identifier", "value"]
    ) == 0
    import json

    published = json.loads(
        (tmp_path / "real-profile.json").read_text(encoding="utf-8")
    )["columns"][0]
    assert published["layout_forms"] == {"@@@%%%%%%%": 700, "@@@.%%%%%%": 2}
    other = write("other.csv", checked)
    assert _describe(checked, 1)["layout_forms"] == {
        "@@@%%%%%%%": 700, "@@@,%%%%%%": 97
    }
    folder = tmp_path / "check"
    folder.mkdir()
    assert _exit_of(
        ["validate", str(tmp_path / "real-profile.json"), "--twin", str(other),
         "--out-dir", str(folder), "--replace"]
    ) == 0


# --------------------------------------------------------- the fill, alone


def test_the_fill_is_every_nought_before_the_figures_and_never_the_last() -> None:
    """P4-D126's reading, and the one step it takes when a depth is rare."""
    plain = parsing.LAYOUT_PLAIN
    assert parsing.layout_form("00282669", plain) == "!!%%%%%%"
    assert parsing.layout_form("0", plain) == "%"
    assert parsing.layout_form("000", plain) == "!!%"
    assert parsing.layout_form("0a1", plain) == "%&%"
    assert parsing.layout_form("00ab", parsing.LAYOUT_HEX_LOWER) == "~~~~"
    assert parsing.layout_shallower("!!!%%") == "!!%%%"
    assert parsing.layout_shallower("!%%%%") == ""
    assert not parsing.is_a_layout_form("%!%")
    assert not parsing.is_a_layout_form("!@%")
    assert not parsing.is_a_layout_form("!!")


def test_a_rare_depth_is_counted_one_nought_shallower() -> None:
    """Three cells two noughts deep and one three deep, at a line of two."""
    values = (
        [f"0{index:07d}" for index in range(1000000, 1000040)]
        + ["00123456", "00234567", "00345678", "00045678"]
    )
    census = taxonomy.layout_census(values, 1, len(set(values)))
    assert census == {"!%%%%%%%": 40, "!!%%%%%%": 4}


# ------------------------------------------------- the space and the case


def test_a_space_stands_between_two_characters_and_nowhere_else() -> None:
    """P4-D127: one interior space at a time; no opening, closing or double."""
    plain = parsing.LAYOUT_PLAIN
    assert parsing.layout_form("657 240 7282", plain) == "%%% %%% %%%%"
    for refused in (" 657", "657 ", "65  7", "65\t7"):
        assert parsing.layout_form(refused, plain) == ""
    assert parsing.is_a_layout_form("%%% %%%")
    for refused in (" %%", "%% ", "%  %"):
        assert not parsing.is_a_layout_form(refused)


def test_the_hexadecimal_case_is_the_case_most_letters_wear() -> None:
    """P4-D125: case decides the marks, never whether a column is hexadecimal."""
    assert parsing.layout_convention(["ab12", "CD34", "ef56"]) == (
        parsing.LAYOUT_HEX_LOWER
    )
    assert parsing.layout_convention(["AB12", "CD34", "ef56"]) == (
        parsing.LAYOUT_HEX_UPPER
    )
    assert parsing.layout_convention(["ab", "CD"]) == parsing.LAYOUT_HEX_LOWER
    assert parsing.layout_convention(["ab12", "gh34"]) == parsing.LAYOUT_PLAIN
    assert parsing.layout_convention(["1234"]) == parsing.LAYOUT_PLAIN


# ------------------------------------------------------- the figures of a fill


def test_the_figures_of_a_filling_do_not_lean_on_the_nought(
    tmp_path: pathlib.Path,
) -> None:
    """P4-D128: the share of noughts among the twin's figures is the table's.

    Measured on the landing's commit, 800 thirteen-figure codes with a
    leading nought on three in ten: 44.8 per cent of the twin's figures were
    noughts against 11.4 per cent of the table's; on 800 UUIDs, 57 per cent
    once the stride was first moved to sixty-four bits. The bound here is
    wide enough for a seed and far narrower than either.
    """
    draw = random.Random(1)
    cells = [
        ("0" if draw.random() < 0.3 else str(draw.randrange(1, 10)))
        + "".join(str(draw.randrange(10)) for _c in range(12))
        for _row in range(ROWS)
    ]

    def noughts(values: "list[str]") -> float:
        figures = [c for value in values for c in value if "0" <= c <= "9"]
        return len([c for c in figures if c == "0"]) / len(figures)

    got = _round_trip(tmp_path / "ean", cells)
    assert got["twin_exit"] == 0 and got["real_exit"] == 0
    assert abs(noughts(got["cells"]) - noughts(cells)) < 0.03
    uuids = _round_trip(tmp_path / "uuid", one_capital_uuid_cells(2))
    assert abs(noughts(uuids["cells"]) - noughts(one_capital_uuid_cells(2))) < 0.03


# ------------------------- the rules the first mutation run could not see


def test_a_pool_of_one_cell_is_not_written() -> None:
    """P4-D124: at a floor of eleven, one odd cell is no `(withheld): 1`."""
    values = _records(4, 40) + ["TMP-42"]
    assert taxonomy.layout_census(values, 11, len(set(values))) == {
        "@@@%%%%%%%": 40
    }


def test_a_written_pool_is_given_up_before_a_named_layout_is() -> None:
    """P4-D124: where the pool leaves one cell over, the pool goes first.

    700 codes `@@@%%%%%%%`, twenty `@@@.%%%%%%`, five cells each wearing a
    layout of its own -- a pool of five at a floor of eleven -- and one cell
    with a double space, which no layout describes. Written with the pool,
    the census leaves ONE cell over; without the pool it leaves six, and
    both named layouts stay.
    """
    draw = random.Random(21)
    values = (
        _records(21, 700)
        + [f"REC.{draw.randrange(100000, 999999)}" for _row in range(20)]
        + ["A-1111", "B.2222", "C_3333", "D:4444", "E#55555", "AB  12"]
    )
    column = _describe(values, 11)
    assert column["layout_forms"] == {"@@@%%%%%%%": 700, "@@@.%%%%%%": 20}
    _no_disclosure(column)


def test_a_deeper_fill_is_never_the_layout_taken_back() -> None:
    """P4-D124 with P4-D126: only a layout nothing shallower stands behind.

    `!%%%%%%%` 700, `!!%%%%%%` 50, `%%%%%%%%` 99 and one cell with a double
    space: one cell is left over. The smallest named layout is `!!%%%%%%`,
    but taking it back would move its cells under `!%%%%%%%` and leave the
    one cell over where it was, so `%%%%%%%%` is taken back instead -- and
    the real table still recounts to what is published.
    """
    draw = random.Random(22)
    values = (
        [f"0{draw.randrange(1000000, 9999999)}" for _row in range(700)]
        + [f"00{draw.randrange(100000, 999999)}" for _row in range(50)]
        + [f"{draw.randrange(10000000, 99999999)}" for _row in range(99)]
        + ["12  3456"]
    )
    assert len(set(values)) == len(values)
    column = _describe(values, 1)
    assert column["layout_forms"] == {"!!%%%%%%": 50, "!%%%%%%%": 700}
    _no_disclosure(column)


def test_a_loader_refuses_a_layout_of_one_cell_at_a_floor_of_one(
    tmp_path: pathlib.Path,
) -> None:
    """LF1's line is two at a floor of one, where the floor alone admits one."""
    from synthtwin import contract, errors

    values = _records(6, 60)
    folder = tmp_path / "one"
    folder.mkdir()
    rows = [[value, f"row{index % 7}"] for index, value in enumerate(values)]
    table = fixtures.write(
        folder, "thing.csv", fixtures.rows_to_csv(["value", "other"], rows)
    )
    document = profile.build_document(
        reading.read_table(f"{table}"), taxonomy.Settings(), ["value"]
    )
    document["columns"][0]["layout_forms"] = {"@@@%%%%%%%": 59, "@@@-%%": 1}
    written = fixtures.write_profile(folder, "thing-profile.json", document)
    with pytest.raises(errors.ProfileError) as refused:
        contract.load_profile(str(written))
    assert "LF1" in str(refused.value)
