"""The older censuses of how numbers were written name no row (plan P4-D221).

`numeric_styles`, `fraction_widths`, `pad_widths` and `field_widths` were
the last censuses of a column of numbers that did not ask the one
disclosure rule, `parsing.census_nameable` with its line
`parsing.census_floor`. Each named a count where it reached the SETTINGS
floor and pooled the rest, so 1,200 two-place prices with one padded cell,
one exponent cell and one cell at three places published
`{"decimal": 1198, "exponent_lower": 1, "leading_zero": 1}`,
`fraction_widths {"2": 1197, "3": 1}` and `pad_widths {"4": 1}` at the
default floor of one, and pools of one and two at a floor of eleven, and
every one of those descriptions loaded. The pad census beside
`n_numeric` also left a complement of one that plan P4-D148 carried to the
owner. Stage 2 closed by the owner rulings of 2026-09-17 with these carried
to the landing that repairs them.

THE GATE, held literally: that 1,200-row column, described at floors one
and eleven, built, described again, and both the twin and the real table
validated at exit 0 -- and the description names none of the three cells:
no count of one is named, none is pooled, and none is left by subtraction
from `n_numeric` or from any total the description prints. "Names none"
is measured as well as read: the same table with each of the three cells
written another rare way gives a byte-identical description.

Every table is built by seeded neutral code at runtime (plan D13).
"""

import json
import pathlib
import random

import pytest

from synthtwin import contract, errors, parsing, profile, reading, taxonomy
from tests import fixtures
from tests.test_stage2_round_trip import _exit_of, _round_trip

ROWS = 1200
CENSUSES = ("numeric_styles", "fraction_widths", "pad_widths", "field_widths")


def _prices(padded: str = "0042", exponent: str = "1.5e3", wide: str = "12.345") -> "list[str]":
    """1,200 prices at two places, three of them written another way."""
    draw = random.Random(7)
    cells = [f"{draw.uniform(10, 900):.2f}" for _row in range(ROWS)]
    cells[100] = padded
    cells[500] = exponent
    cells[900] = wide
    return cells


def _description_text(folder: pathlib.Path, cells: "list[str]", floor: int) -> str:
    """What `synthtwin profile` writes for a one-column table, as text."""
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "real.csv"
    table.write_text(
        fixtures.rows_to_csv(["value"], [[cell] for cell in cells]),
        encoding="utf-8",
        newline="",
    )
    assert _exit_of(
        [
            "profile", str(table), "--out-dir", str(folder), "--replace",
            "--smallest-group", str(floor),
        ]
    ) == 0
    return (folder / "real-profile.json").read_text(encoding="utf-8")


def _names_no_row(block: "dict[str, object]", floor: int) -> None:
    """The three tests, asked of every count the four censuses print."""
    line = parsing.census_floor(floor)
    numbers = block["n_numeric"]
    assert isinstance(numbers, int)
    for census in CENSUSES:
        counts = block[census]
        assert isinstance(counts, dict)
        for key in sorted(counts):
            # No named count of one, and no pooled count of one.
            assert counts[key] >= line, (census, key, counts)
    styles = block["numeric_styles"]
    assert isinstance(styles, dict)
    # No complement of one by subtraction from `n_numeric`, from the
    # count of a named form, or from the forms map's pool.
    assert sum(styles.values()) == numbers
    for census, form in (
        ("fraction_widths", parsing.STYLE_DECIMAL),
        ("pad_widths", parsing.STYLE_LEADING_ZERO),
    ):
        counts = block[census]
        assert isinstance(counts, dict)
        printed = sum(counts.values())
        if printed and form not in styles:
            raise AssertionError((census, "counts a form the map holds back"))
        if form in styles and census == "fraction_widths":
            assert printed == styles[form], (census, counts, styles)
        rest = numbers - printed
        assert rest == 0 or rest >= line, (census, rest)
    fields = block["field_widths"]
    assert isinstance(fields, dict)
    named = 0
    for form in (
        parsing.STYLE_PLAIN, parsing.STYLE_LEADING_PLUS, parsing.STYLE_LEADING_ZERO
    ):
        named = named + (styles[form] if form in styles else 0)
    held = sum(fields.values()) - named
    pool = styles["(withheld)"] if "(withheld)" in styles else 0
    assert held == 0 or held >= line, (fields, styles)
    assert held == 0 or pool - held == 0 or pool - held >= line, (fields, styles)


@pytest.mark.parametrize("floor", [1, 11])
def test_a_padded_an_exponent_and_a_three_place_cell_are_named_nowhere(
    tmp_path: pathlib.Path, floor: int
) -> None:
    """THE GATE: none of the three cells is published, and both files pass."""
    cells = _prices()
    first, second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "prices", cells, ("--smallest-group", f"{floor}"), True
    )
    assert (twin_exit, real_exit) == (0, 0)
    _names_no_row(first, floor)
    _names_no_row(second, floor)
    styles = first["numeric_styles"]
    assert isinstance(styles, dict)
    assert parsing.STYLE_LEADING_ZERO not in styles
    assert parsing.STYLE_EXPONENT_LOWER not in styles
    assert "3" not in first["fraction_widths"]
    assert first["pad_widths"] == {}
    if floor == 1:
        # The two held-back forms are a pool of two, a group at this floor,
        # beside the named decimals; the widths of those decimals leave one
        # cell at three places, so that census is one pool.
        assert styles == {"(withheld)": 2, "decimal": 1198}
        assert first["fraction_widths"] == {"(withheld)": 1198}
    else:
        # A pool of two is below the line of eleven, so it takes in the
        # decimals, and a form held back has no widths published.
        assert styles == {"(withheld)": ROWS}
        assert first["fraction_widths"] == {}
    assert first["field_widths"] == {}
    # NAMES NONE, measured: each of the three written another rare way --
    # a plus in place of the pad, an upper-case exponent, a fourth place
    # of the same value -- gives the same description, byte for byte.
    as_written = _description_text(tmp_path / "as-written", cells, floor)
    otherwise = _description_text(
        tmp_path / "otherwise", _prices("+42", "1.5E3", "12.3450"), floor
    )
    assert as_written == otherwise


def test_the_producer_folds_a_pool_below_the_line_into_the_smallest_named_count() -> None:
    """The forms map and a width census, read off the producer's own rule."""
    assert parsing.pooled_census(
        {"decimal": 1198, "exponent_lower": 1, "leading_zero": 1}, 1200, 1, False
    ) == {"(withheld)": 2, "decimal": 1198}
    assert parsing.pooled_census(
        {"decimal": 1198, "exponent_lower": 1, "leading_zero": 1}, 1200, 11, False
    ) == {"(withheld)": 1200}
    # A pool that reaches the line keeps every named count.
    assert parsing.pooled_census(
        {"plain": 20, "leading_zero": 12, "decimal": 1, "leading_plus": 10},
        43, 11, False,
    ) == {"(withheld)": 11, "leading_zero": 12, "plain": 20}
    # One smallest named count is taken in, and no more.
    assert parsing.pooled_census(
        {"decimal": 1000, "plain": 50, "exponent_upper": 1}, 1051, 11, False
    ) == {"(withheld)": 51, "decimal": 1000}


def _document(tmp_path: pathlib.Path, floor: int, cells: "list[str]") -> "dict[str, object]":
    """The producer's document of a one-column table, before it is written."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    table = fixtures.write(
        tmp_path, "prices.csv",
        fixtures.rows_to_csv(["value"], [[cell] for cell in cells]),
    )
    document = profile.build_document(
        reading.read_table(f"{table}"), taxonomy.Settings(small_cell_floor=floor), []
    )
    assert isinstance(document, dict)
    return document


def _refused_by(
    tmp_path: pathlib.Path, document: "dict[str, object]", rule: str, **fields: object
) -> None:
    edited = json.loads(json.dumps(document))
    for key in sorted(fields):
        edited["columns"][0][key] = fields[key]
    written = fixtures.write_profile(tmp_path, f"{rule}.json", edited)
    with pytest.raises(errors.ProfileError) as refused:
        contract.load_profile(f"{written}")
    assert f"it is called {rule} " in f"{refused.value}", f"{refused.value}"


def test_the_loader_names_no_count_of_one_at_a_floor_of_one(tmp_path: pathlib.Path) -> None:
    """P2, P5, P6b and P6c at a floor of one, where only the line of two refuses."""
    document = _document(tmp_path, 1, _prices())
    _refused_by(
        tmp_path, document, "P2",
        numeric_styles={"decimal": 1198, "exponent_lower": 1, "leading_zero": 1},
        fraction_widths={"(withheld)": 1198},
    )
    _refused_by(
        tmp_path, document, "P5",
        fraction_widths={"2": 1197, "3": 1},
    )
    _refused_by(
        tmp_path, document, "P5",
        fraction_widths={"2": 1197, "(withheld)": 1},
    )
    whole = _document(
        tmp_path / "codes", 1, [f"0{1000 + index}" for index in range(799)] + ["12345"]
    )
    _refused_by(
        tmp_path, whole, "P2",
        numeric_styles={"leading_zero": 799, "plain": 1},
        pad_widths={"5": 799},
        field_widths={"5": 800},
    )
    _refused_by(
        tmp_path, whole, "P6b",
        numeric_styles={"leading_zero": 800},
        pad_widths={"5": 799, "6": 1},
        field_widths={"5": 799, "6": 1},
    )
    _refused_by(
        tmp_path, whole, "P6c",
        numeric_styles={"leading_zero": 800},
        pad_widths={"5": 800},
        field_widths={"5": 799, "(withheld)": 1},
    )


def test_a_pool_beside_a_named_count_is_held_by_the_loader(tmp_path: pathlib.Path) -> None:
    """P6, P8 and P9c: a pool reaches the line and leaves nothing to subtract."""
    document = _document(tmp_path, 11, _prices())
    _refused_by(
        tmp_path, document, "P6",
        numeric_styles={"(withheld)": 2, "decimal": 1198},
    )
    ones = _document(tmp_path / "one", 1, _prices())
    _refused_by(
        tmp_path, ones, "P8",
        pad_widths={"(withheld)": 2},
    )
    _refused_by(
        tmp_path, ones, "P9c",
        field_widths={"(withheld)": 2},
        numeric_styles={"(withheld)": 3, "decimal": 1197},
        fraction_widths={"(withheld)": 1197},
    )
    # ...and at a floor of one a pool of two beside a named count loads:
    # S13 as amended, where a count of one is pooled rather than named.
    written = fixtures.write_profile(tmp_path, "ones.json", ones)
    loaded = contract.load_profile(f"{written}")
    facts = loaded.columns[0].facts
    assert isinstance(facts, contract.NumericFacts)
    assert facts.numeric_styles == {"(withheld)": 2, "decimal": 1198}


@pytest.mark.parametrize(
    "field, census",
    [
        ("numeric_styles", {"decimal": 1198, "exponent_lower": 1, "leading_zero": 1}),
        ("fraction_widths", {"2": 1197, "3": 1}),
        ("pad_widths", {"4": 1}),
        ("field_widths", {"4": 1}),
    ],
)
def test_the_publication_guard_names_no_count_of_one_at_a_floor_of_one(
    tmp_path: pathlib.Path, field: str, census: "dict[str, int]"
) -> None:
    """The half that WRITES says what the loader says, at the line of two."""
    document = _document(tmp_path, 1, _prices())
    profile.check_publication(document)
    columns = document["columns"]
    assert isinstance(columns, list)
    columns[0][field] = census
    with pytest.raises(errors.ProfileError) as refused:
        profile.check_publication(document)
    assert "before writing anything" in f"{refused.value}"


def test_the_publication_guard_lets_a_pool_stand_at_a_floor_of_one(
    tmp_path: pathlib.Path,
) -> None:
    """S13 as amended, on the writing half: a pool here is the rule working."""
    document = _document(tmp_path, 1, _prices())
    columns = document["columns"]
    assert isinstance(columns, list)
    assert columns[0]["numeric_styles"] == {"(withheld)": 2, "decimal": 1198}
    assert columns[0]["fraction_widths"] == {"(withheld)": 1198}
    profile.check_publication(document)


def test_a_pool_of_whole_number_widths_reaches_the_line(tmp_path: pathlib.Path) -> None:
    """P6c's own line, where no other route of P6c or P9c can refuse."""
    document = _document(
        tmp_path, 1, [f"{10000 + index * 7}" for index in range(800)]
    )
    columns = document["columns"]
    assert isinstance(columns, list)
    assert columns[0]["numeric_styles"] == {"plain": 800}
    assert columns[0]["pad_widths"] == {}
    _refused_by(tmp_path, document, "P6c", field_widths={"5": 799, "(withheld)": 1})


def test_the_plus_route_is_asked_at_a_floor_of_one(tmp_path: pathlib.Path) -> None:
    """P5b at the default floor, where it once stood aside (plan P4-D148).

    800 padded keys, two plus-signed padded keys and one plus-signed key
    with no pad: counting the two padded ones would leave the one unpadded
    plus-signed key by subtraction from the named `leading_plus` count, so
    the census counts the `leading_zero` cells alone -- at a floor of one
    too, where the rule used to be skipped.
    """
    cells = (
        [f"0{1000 + index}" for index in range(800)]
        + ["+01800", "+01801"]
        + ["+5"]
    )
    document = _document(tmp_path, 1, cells)
    columns = document["columns"]
    assert isinstance(columns, list)
    assert columns[0]["numeric_styles"] == {"leading_plus": 3, "leading_zero": 800}
    assert columns[0]["pad_widths"] == {"5": 800}
    _refused_by(tmp_path, document, "P5b", pad_widths={"5": 802})


def test_a_width_a_file_folds_into_its_pool_is_withheld_not_missed(
    tmp_path: pathlib.Path,
) -> None:
    """The checker reads an absent key through the fold (validation V5.3-A3).

    A description publishing 400 cells at two places, measured against a
    file holding 398 of them and two at three places: that file describes
    itself as one pool of 400, so how many of its cells sit at two places
    is a count its own description does not print, and the check is
    withheld rather than told the file holds fewer than the floor.
    """
    from synthtwin import validation

    draw = random.Random(11)
    cells = [f"{draw.uniform(10, 900):.2f}" for _row in range(400)]
    table = fixtures.write(
        tmp_path, "real.csv",
        fixtures.rows_to_csv(["value"], [[cell] for cell in cells]),
    )
    document = profile.build_document(
        reading.read_table(f"{table}"), taxonomy.Settings(small_cell_floor=11), []
    )
    written = fixtures.write_profile(tmp_path, "real-profile.json", document)
    loaded = contract.load_profile(f"{written}")
    moved = list(cells)
    moved[3] = moved[3] + "5"
    moved[7] = moved[7] + "5"
    measured = fixtures.write(
        tmp_path, "moved.csv",
        fixtures.rows_to_csv(["value"], [[cell] for cell in moved]),
    )
    outcome = validation.measure(loaded, f"{measured}")
    verdicts = [
        check.verdict
        for check in outcome.checks
        if check.subcheck == "widths.published.2"
    ]
    assert verdicts == [validation.WITHHELD], verdicts
