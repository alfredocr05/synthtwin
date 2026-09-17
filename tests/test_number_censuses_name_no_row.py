"""The older censuses of how numbers were written name no row (plans P4-D221, P4-D222).

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

THE FIRST REPAIR (P4-D221) pooled what it could not name, and a pool below
the line took the commonest named form in, so one odd cell pooled the whole
map: 999 prices and one `120` came back as integers and fifteen-place
decimals, and 1,999 seven-wide padded codes with one `4521` came back
unpadded. It also treated the six forms as an open vocabulary, so five
forms of one cell each read straight off a pool of five. THE SECOND
(P4-D222) counts a form or width below the line into the commonest named
one, as ruling 4 of 2026-09-17 counts missing-value words below a raised
floor as absent: no pool stands beside a named count, and the twin writes
the column's own form and width.

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

from synthtwin import contract, errors, parsing, profile, reading, taxonomy, validation
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
        # A pool stands alone; every count printed reaches the line.
        assert "(withheld)" not in counts or len(counts) == 1, (census, counts)
        for key in sorted(counts):
            assert counts[key] >= line, (census, key, counts)
    styles = block["numeric_styles"]
    assert isinstance(styles, dict)
    assert sum(styles.values()) == numbers
    for census, form in (
        ("fraction_widths", parsing.STYLE_DECIMAL),
        ("pad_widths", parsing.STYLE_LEADING_ZERO),
    ):
        counts = block[census]
        assert isinstance(counts, dict)
        printed = sum(counts.values())
        if form in styles and census == "fraction_widths":
            assert printed == styles[form], (census, counts, styles)
        if printed and form in styles:
            rest = styles[form] - printed
            assert rest == 0 or rest >= line, (census, rest)


@pytest.mark.parametrize("floor", [1, 11])
def test_a_padded_an_exponent_and_a_three_place_cell_are_named_nowhere(
    tmp_path: pathlib.Path, floor: int
) -> None:
    """THE GATE: none of the three cells is published, and both files pass."""
    cells = _prices()
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "prices", cells, ("--smallest-group", f"{floor}"), True
    )
    assert (twin_exit, real_exit) == (0, 0)
    _names_no_row(first, floor)
    _names_no_row(second, floor)
    assert first["numeric_styles"] == {"decimal": ROWS}
    assert first["fraction_widths"] == {"2": ROWS}
    assert first["pad_widths"] == {}
    assert first["field_widths"] == {}
    # THE TWIN WRITES THE COLUMN'S OWN FORM AND WIDTH.
    assert all(parsing.fraction_width(cell) == 2 for cell in written)
    # NAMES NONE, measured: each of the three written another rare way --
    # a plus in place of the pad, an upper-case exponent, a fourth place
    # of the same value -- gives the same description, byte for byte.
    as_written = _description_text(tmp_path / "as-written", cells, floor)
    otherwise = _description_text(
        tmp_path / "otherwise", _prices("+42", "1.5E3", "12.3450"), floor
    )
    assert as_written == otherwise


@pytest.mark.parametrize(
    "floor, singles",
    # Values inside the prices' own range: a lone 2,500 among prices up to
    # 900 is a heavy tail whose mean the twin misses on 039df54 as well
    # (stage 3, deferred by the owner rulings of 2026-09-17).
    [(1, ("70", "+80", "090", "1.5e2", "2.5E2")), (11, ("70", "+80", "090", "1.5e2", "2.5E2"))],
)
def test_five_rare_forms_are_counted_into_the_commonest_and_give_back_no_count(
    tmp_path: pathlib.Path, floor: int, singles: "tuple[str, ...]"
) -> None:
    """The final skeptic's first BLOCKER: a pool at full capacity gave counts back.

    `{"decimal": 995, "(withheld)": 5}` at a floor of one said each of the
    five other forms was written by exactly one cell, and `{"decimal":
    1950, "(withheld)": 50}` at eleven said ten each. Counted into the
    decimals, the forms map says neither, and the twin writes decimals.
    """
    each = parsing.census_floor(floor) - 1
    draw = random.Random(31)
    cells = [f"{draw.uniform(10, 900):.2f}" for _row in range(3000)]
    place = 0
    for text in singles:
        for _copy in range(each):
            cells[place * 7 + 1] = text
            place = place + 1
    first, _second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "five", cells, ("--smallest-group", f"{floor}"), True
    )
    assert first["numeric_styles"] == {"decimal": 3000}
    assert first["fraction_widths"] == {"2": 3000}
    assert first["field_widths"] == {}
    assert (twin_exit, real_exit) == (0, 0)
    assert all(parsing.numeric_style(cell) == parsing.STYLE_DECIMAL for cell in written)
    # ...and the same values written as two-place decimals describe alike.
    none_of_them = list(cells)
    for index in range(3000):
        if parsing.numeric_style(none_of_them[index]) != parsing.STYLE_DECIMAL:
            none_of_them[index] = f"{float(none_of_them[index]):.2f}"
    assert _description_text(tmp_path / "a", cells, floor) == _description_text(
        tmp_path / "b", none_of_them, floor
    )


@pytest.mark.parametrize(
    "name, cells, form, widths",
    [
        (
            "one-whole-price",
            [f"{value * 0.37 + 10:.2f}" for value in range(999)] + ["120"],
            {"decimal": 1000},
            ("fraction_widths", {"2": 1000}),
        ),
        (
            "one-short-code",
            [f"{value * 13 + 1:07d}" for value in range(1999)] + ["4521"],
            {"leading_zero": 2000},
            ("pad_widths", {"7": 2000}),
        ),
        (
            "one-two-place-reading",
            [f"{value % 150 / 10 + 3:.1f}" for value in range(799)] + ["4.20"],
            {"decimal": 800},
            ("fraction_widths", {"1": 800}),
        ),
    ],
)
def test_one_odd_cell_leaves_the_twin_its_forms_and_widths(
    tmp_path: pathlib.Path,
    name: str,
    cells: "list[str]",
    form: "dict[str, int]",
    widths: "tuple[str, dict[str, int]]",
) -> None:
    """The final skeptic's fourth BLOCKER, on its three columns, at the default floor."""
    first, _second, written, twin_exit, real_exit = _round_trip(
        tmp_path / name, cells, ("--smallest-group", "1"), True
    )
    assert first["numeric_styles"] == form
    assert first[widths[0]] == widths[1]
    assert (twin_exit, real_exit) == (0, 0)
    style = next(iter(form))
    assert all(parsing.numeric_style(cell) == style for cell in written)
    width = int(next(iter(widths[1])))
    if style == parsing.STYLE_DECIMAL:
        assert all(parsing.fraction_width(cell) == width for cell in written)
    else:
        assert all(parsing.pad_width(cell) == width for cell in written)


def test_a_file_that_keeps_two_of_twelve_published_exponents_is_missed(
    tmp_path: pathlib.Path,
) -> None:
    """The final skeptic's MAJOR finding, on the branch it was measured on.

    600 two-place prices, 12 of them written with an exponent, publish
    `{"decimal": 588, "exponent_lower": 12}` at a floor of eleven. A file
    rewriting ten of the twelve exponents describes itself as 600 decimals
    and misses; the first repair read that absent form as a pool the file
    might hold and withheld the verdict.
    """
    draw = random.Random(11)
    cells = [f"{draw.uniform(1, 99):.2f}" for _row in range(600)]
    for index in range(12):
        cells[index * 40] = f"{draw.uniform(1, 9):.1f}e2"
    table = fixtures.write(
        tmp_path, "real.csv",
        fixtures.rows_to_csv(["value"], [[cell] for cell in cells]),
    )
    document = profile.build_document(
        reading.read_table(f"{table}"), taxonomy.Settings(small_cell_floor=11), []
    )
    written = fixtures.write_profile(tmp_path, "real-profile.json", document)
    loaded = contract.load_profile(f"{written}")
    facts = loaded.columns[0].facts
    assert isinstance(facts, contract.NumericFacts)
    assert facts.numeric_styles == {"decimal": 588, "exponent_lower": 12}
    moved = list(cells)
    for index in range(10):
        moved[index * 40] = f"{float(moved[index * 40]):.2f}"
    measured = fixtures.write(
        tmp_path, "moved.csv",
        fixtures.rows_to_csv(["value"], [[cell] for cell in moved]),
    )
    outcome = validation.measure(loaded, f"{measured}")
    verdicts = {
        check.subcheck: check.verdict
        for check in outcome.checks
        if check.subcheck
        in ("styles.published.exponent_lower", "styles.published.decimal")
    }
    assert verdicts == {
        "styles.published.exponent_lower": validation.MISSED,
        "styles.published.decimal": validation.MISSED,
    }, verdicts
    # ...while the real table meets its own description.
    own = validation.measure(loaded, f"{table}")
    assert not [check for check in own.checks if check.verdict == validation.MISSED]


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
        fraction_widths={"2": 1198},
    )
    _refused_by(
        tmp_path, document, "P5",
        fraction_widths={"2": 1199, "3": 1},
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
        field_widths={"5": 799, "4": 1},
    )


def test_a_pool_stands_only_alone_and_only_where_it_names_no_one(
    tmp_path: pathlib.Path,
) -> None:
    """P6, P5, P6c and P8: no pool beside a named count, no pool of every form."""
    document = _document(tmp_path, 11, _prices())
    _refused_by(
        tmp_path, document, "P6",
        numeric_styles={"(withheld)": 11, "decimal": 1189},
        fraction_widths={"2": 1189},
    )
    _refused_by(
        tmp_path, document, "P5",
        fraction_widths={"2": 1189, "(withheld)": 11},
    )
    whole = _document(
        tmp_path / "codes", 11, [f"0{1000 + index}" for index in range(800)]
    )
    _refused_by(
        tmp_path, whole, "P6c",
        field_widths={"5": 789, "(withheld)": 11},
    )
    short = _document(tmp_path / "short", 11, _prices()[:40])
    columns = short["columns"]
    assert isinstance(columns, list)
    assert columns[0]["fraction_widths"] == {"2": 40}
    _refused_by(
        tmp_path / "short", short, "P8",
        numeric_styles={"(withheld)": 40},
    )
    # SIX FORMS OF ONE CELL EACH: a pool of six at a floor of one would say
    # every form was written, so the producer names its default form.
    six = _document(tmp_path / "six", 1, ["7", "+8", "09", "1.5", "1.5e3", "2.5E3"])
    columns = six["columns"]
    assert isinstance(columns, list)
    assert columns[0]["numeric_styles"] == {"decimal": 6}
    _refused_by(
        tmp_path / "six", six, "P6",
        numeric_styles={"(withheld)": 6},
        fraction_widths={}, pad_widths={}, field_widths={},
    )


@pytest.mark.parametrize(
    "field, census",
    [
        ("numeric_styles", {"decimal": 1198, "exponent_lower": 1, "leading_zero": 1}),
        ("fraction_widths", {"2": 1199, "3": 1}),
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
    document = _document(tmp_path, 1, ["70", "7.5", "+80", "090", "1.5e2"])
    columns = document["columns"]
    assert isinstance(columns, list)
    assert columns[0]["numeric_styles"] == {"(withheld)": 5}
    profile.check_publication(document)


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


# -- what follows a census counted into its commonest (plan P4-D222) ----


def _loads(tmp_path: pathlib.Path, document: "dict[str, object]") -> None:
    written = fixtures.write_profile(tmp_path, "loads.json", document)
    contract.load_profile(f"{written}")


def test_signed_decimals_are_counted_over_the_published_decimal_count(
    tmp_path: pathlib.Path,
) -> None:
    """`decimal_plus` reads the `decimal` count the forms map publishes.

    1,199 signed prices and one whole number at a floor of one publish
    `{"decimal": 1200}`. Counted over the 1,199 cells that carry a point,
    every one is signed and the census named `{"+": 1199}` -- which leaves
    one of the published 1,200 unsigned, a count of one the loader's DP1
    refuses and a reader reads off.
    """
    draw = random.Random(3)
    cells = [f"+{draw.uniform(10, 900):.2f}" for _row in range(1199)] + ["120"]
    document = _document(tmp_path, 1, cells)
    columns = document["columns"]
    assert isinstance(columns, list)
    assert columns[0]["numeric_styles"] == {"decimal": 1200}
    assert columns[0]["decimal_plus"] == {"(unavailable)": 0}
    _loads(tmp_path, document)


def test_a_wide_run_counted_into_the_decimals_is_no_wide_run(
    tmp_path: pathlib.Path,
) -> None:
    """`wide_runs` reads only the point-free forms the forms map names.

    One seventeen-figure key among 799 amounts at a floor of one is
    counted into `decimal`; asked of it, the word said `canonical` beside
    a map naming no point-free form, which invariant WR1 refuses.
    """
    draw = random.Random(5)
    cells = [f"{draw.uniform(10, 900):.2f}" for _row in range(799)]
    cells += ["12345678901234567"]
    document = _document(tmp_path, 1, cells)
    columns = document["columns"]
    assert isinstance(columns, list)
    assert columns[0]["numeric_styles"] == {"decimal": 800}
    assert columns[0]["wide_runs"] == "none"
    _loads(tmp_path, document)


def test_a_pooled_forms_map_says_nothing_of_signed_decimals(
    tmp_path: pathlib.Path,
) -> None:
    """Beside a pooled map, `decimal_plus` is unavailable with or without a point."""
    with_point = _document(tmp_path / "a", 1, ["70", "7.5", "+80", "090", "1.5e2"])
    without = _document(tmp_path / "b", 1, ["70", "+75", "8.0e1", "090", "1.5E2"])
    for document in (with_point, without):
        columns = document["columns"]
        assert isinstance(columns, list)
        assert "(withheld)" in columns[0]["numeric_styles"]
        assert columns[0]["decimal_plus"] == {"(unavailable)": 0}


def test_unpadded_widths_too_thin_to_name_pool_the_whole_number_census(
    tmp_path: pathlib.Path,
) -> None:
    """No unpadded width at the line beside unpadded cells: `field_widths` is one pool.

    Three padded codes and three plus-signed numbers at a floor of three,
    with two decimals counted into the plus-signed form: the plus-signed
    cells are written two at three figures and one at one, neither at the
    line, so a width named for them would be a count of fewer than three
    beside the padded census.
    """
    cells = ["0001", "0002", "0003", "+123", "+456", "+7", "1.5", "2.5"]
    document = _document(tmp_path, 3, cells)
    columns = document["columns"]
    assert isinstance(columns, list)
    assert columns[0]["numeric_styles"] == {"leading_plus": 5, "leading_zero": 3}
    assert columns[0]["pad_widths"] == {"4": 3}
    assert columns[0]["field_widths"] == {"(withheld)": 8}
    _loads(tmp_path, document)
    # ...and with nothing counted in: named at the padded width, the three
    # plus-signed cells would be said to be four figures wide.
    plain = _document(tmp_path / "none-taken", 3, cells[:6])
    columns = plain["columns"]
    assert isinstance(columns, list)
    assert columns[0]["numeric_styles"] == {"leading_plus": 3, "leading_zero": 3}
    assert columns[0]["field_widths"] == {"(withheld)": 6}
    _loads(tmp_path / "none-taken", plain)


def test_a_pad_width_below_the_line_moves_in_both_width_censuses(
    tmp_path: pathlib.Path,
) -> None:
    """A padded cell counted into the commonest pad width is counted there as a field too.

    Two hundred five-figure padded codes, eleven at seven and nine figures,
    beside three hundred plain three-figure numbers at a floor of eleven:
    the padded census counts the eleven at five, and so must the field
    census. Counted at the commonest FIELD width instead -- three -- the two
    censuses disagree at five by eleven cells, which the loader refuses.
    """
    cells = (
        [f"{index:05d}" for index in range(200)]
        + [f"{index:09d}" for index in range(5)]
        + [f"{index:07d}" for index in range(6)]
        + [f"{100 + index}" for index in range(300)]
    )
    document = _document(tmp_path, 11, cells)
    columns = document["columns"]
    assert isinstance(columns, list)
    assert columns[0]["pad_widths"] == {"5": 211}
    assert columns[0]["field_widths"] == {"3": 300, "5": 211}
    _loads(tmp_path, document)


def test_a_pooled_forms_map_has_no_whole_number_widths(tmp_path: pathlib.Path) -> None:
    """P8 over `field_widths` too: a map naming no form names no point-free one."""
    short = _document(tmp_path / "short", 11, [f"{index * 7 + 10}" for index in range(10)] + ["1.5"] * 5)
    columns = short["columns"]
    assert isinstance(columns, list)
    assert columns[0]["numeric_styles"] == {"(withheld)": 15}
    assert columns[0]["field_widths"] == {}
    _refused_by(tmp_path / "short", short, "P8", field_widths={"(withheld)": 15})


@pytest.mark.parametrize("floor", [1, 11])
def test_rare_point_carrying_cells_counted_into_a_padded_form_pass_both_ways(
    tmp_path: pathlib.Path, floor: int
) -> None:
    """The recount of cells needing a point reads only the forms a description names.

    Forty padded codes beside two upper-case exponent cells and one decimal
    at a floor of eleven publish `{"leading_zero": 43}`: the decimal's value
    has no point-free spelling, so the table and its twin each hold a cell
    that needs a point where no point-carrying form is named. Read over
    every cell, that cell was owed by `styles.spill` and the table missed
    its own description.
    """
    cells = [f"{index * 13 + 1:04d}" for index in range(40)] + ["1.23E2", "4.56E2", "2.5"]
    first, _second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "padded", cells, ("--smallest-group", f"{floor}"), True
    )
    if floor == 11:
        assert first["numeric_styles"] == {"leading_zero": 43}
    assert (twin_exit, real_exit) == (0, 0)


def test_a_width_counted_away_leaves_no_pool_behind(tmp_path: pathlib.Path) -> None:
    """A width emptied by the count into the commonest pools nothing.

    Three plus-signed numbers at a floor of one, two of one figure and one
    of five: the five-figure cell is counted into the one-figure width, and
    the width it left, now holding nothing, used to read as a width below
    the line and pooled the whole census.
    """
    document = _document(tmp_path, 1, ["+7", "+3", "+43994"])
    columns = document["columns"]
    assert isinstance(columns, list)
    assert columns[0]["numeric_styles"] == {"leading_plus": 3}
    assert columns[0]["field_widths"] == {"1": 3}
    _loads(tmp_path, document)
