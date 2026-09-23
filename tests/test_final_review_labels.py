"""The final review of the labels, identifiers and missing values: every item.

The review read the merged tree once and reproduced ten defects in this
area, two of them blockers, plus two the merge review named beside them
and the failures the whole suite attributed to the landings that built
the area. Each is pinned here by its own reproduction, as a ROUND TRIP
wherever the defect is one a person meets: a realistic table is written,
described, a twin is built, and BOTH the twin and the real table are
validated at exit 0 -- beside the specific fact the defect broke, asserted
on the files themselves.

- **P4-D150** the disclosure rule written once, `parsing.census_names_one_row`,
  which the producer and the loader both ask of every census the stage
  added;
- **P4-D151** a layout census that writes only its pool is asked it too;
- **P4-D152** an empty layout census is asked nothing, so a sparse
  identifier's description loads;
- **P4-D153** a case split leaves no count of one, in the census or its pool,
  and **P4-D160** the lower-case key alone counts its whole form, and no
  reading of the form census -- pool, `n_present`, `n_code_alphabet` --
  names one row;
- **P4-D154** letters inside `a` to `f` that never trade places with a
  figure are letters, not hexadecimal;
- **P4-D155** the lone figure 0 is a whole number one figure long, and
  **P4-D162** it is the last one, and walked late;
- **P4-D156** a sign before figures is written where the census proves it,
  and **P4-D163** a layout the first packing leaves short is a reason to
  look at the next packing;
- **P4-D157** a fold-collision partner wears the layout its identity
  reserved, and the twin's report recounts every layout;
- **P4-D158** a spelling the table declares absent is never invented, in
  any column;
- **P4-D159** validation recounts a form under the submitted census's case
  convention;
- review item 8, residual R-P3-11, is closed by the owner's ruling of
  2026-09-17, option A (plan P4-D200): pooled missing-value words count
  as absent up to the pool's total, so the real table holds its own
  presence counts, and the round-2 witness beside it is still missed.

Every table is built by seeded neutral code at runtime (plan D13).
"""

import csv
import io
import json
import pathlib
import random
import re

import pytest

from synthtwin import contract, errors, generation, parsing
from tests import fixtures
from tests.test_stage2_round_trip import _exit_of, describe_with_the_producer

ROWS = 800


def _round_trip(
    folder: pathlib.Path,
    columns: "dict[str, list[str]]",
    flags: "tuple[str, ...]" = (),
    seed: str = "4",
    by_command: bool = True,
) -> dict:
    """Describe, build, validate the twin AND the table; hand back all four.

    A second column stands beside a column under test unless the caller
    gives one, because a one-column table holding an empty cell is
    refused (plan P4-D74).

    ``by_command`` FALSE DESCRIBES WITH THE PRODUCER (plan P4-D341).
    `synthtwin profile` refuses a table whose POPULATION is under the
    floor and writes nothing, and a column declared with `--identifier`
    whose values repeat is what the population is counted by -- so a
    shape built from a handful of repeated record numbers is a handful
    of PEOPLE however many rows it has, and no padding reaches the
    floor. `build_document` describes a table of any size and refuses
    none, so such a shape is described that way; the twin is still
    built and both files still checked through `generate` and
    `validate`, which the floor does not govern.
    """
    folder.mkdir(parents=True, exist_ok=True)
    names = list(columns)
    size = len(columns[names[0]])
    if len(names) == 1:
        columns = dict(columns)
        columns["other"] = [f"row{index % 7}" for index in range(size)]
        names = names + ["other"]
    rows = [[columns[name][index] for name in names] for index in range(size)]
    table = folder / "real.csv"
    table.write_text(
        fixtures.rows_to_csv(names, rows), encoding="utf-8", newline=""
    )
    if by_command:
        assert _exit_of(
            ["profile", str(table), "--out-dir", str(folder), "--replace",
             *flags]
        ) == 0
    else:
        describe_with_the_producer(table, folder / "real-profile.json", flags)
    described = folder / "real-profile.json"
    generated = _exit_of(
        ["generate", str(described), "--out-dir", str(folder), "--seed", seed,
         "--replace"]
    )
    result: dict = {
        "document": json.loads(described.read_text(encoding="utf-8")),
        "generated": generated,
        "profile": described,
        "table": table,
    }
    if generated != 0:
        return result
    twin = folder / "real-twin.csv"
    written = list(csv.reader(io.StringIO(twin.read_text(encoding="utf-8"))))
    result["twin"] = {
        name: [row[place] for row in written[1:]]
        for place, name in enumerate(written[0])
    }
    result["report"] = "".join(
        path.read_text(encoding="utf-8")
        for path in sorted(folder.iterdir())
        if path.is_file() and path.suffix == ".txt"
    )
    for side, path in (("twin_exit", twin), ("real_exit", table)):
        checked = folder / side
        checked.mkdir()
        result[side] = _exit_of(
            ["validate", str(described), "--twin", str(path), "--out-dir",
             str(checked), "--replace"]
        )
    return result


def _column(result: dict, name: str = "value") -> dict:
    for column in result["document"]["columns"]:
        if column["name"] == name:
            return column
    raise AssertionError(name)


def _matching(cells: "list[str]", pattern: str) -> int:
    rule = re.compile(pattern)
    return len([cell for cell in cells if rule.fullmatch(cell)])


def _both_pass(result: dict) -> None:
    assert result["generated"] == 0
    assert (result["twin_exit"], result["real_exit"]) == (0, 0)


# ---------------------------------------------- P4-D150, the shared rule


def test_the_shared_rule_names_a_count_of_one_and_a_difference_of_one() -> None:
    """One question, three answers: a count of one, a difference, nothing."""
    assert parsing.census_names_one_row({"a": 1}, []) == -2
    assert parsing.census_names_one_row({"a": 5}, [(9, 5), (6, 5)]) == 1
    assert parsing.census_names_one_row({"a": 5}, [(7, 5)]) == -1
    # An absent census covers nothing and leaves nothing to subtract.
    assert parsing.census_names_one_row({}, [(1, 0)]) == -1


# ------------------------- P4-D153, the case census publishing one person


def _one_capital(rows: int = ROWS) -> "list[str]":
    return [f"abc-{index:05d}" for index in range(rows - 1)] + ["ABC-00799"]


def test_one_capitalised_code_is_not_published_as_a_count_of_one(
    tmp_path: pathlib.Path,
) -> None:
    """The review's blocker: 799 lower-case codes beside ONE in capitals.

    At a floor of twenty the census published `{"&&&-%%%%%": 799,
    "(withheld)": 1}`, which names the one differently written cell by
    its count and by its complement. Blind to case it named nothing but
    turned the twin's codes into capitals (the skeptic's regression); the
    lower-case key alone counts the whole form and keeps the convention
    (plan P4-D160).
    """
    result = _round_trip(
        tmp_path, {"value": _one_capital()},
        ("--code", "value", "--smallest-group", "20"),
    )
    forms = _column(result)["shape_forms"]
    assert 1 not in forms.values(), forms
    assert forms == {"&&&-%%%%%": 800}
    _both_pass(result)
    twin = result["twin"]["value"]
    assert _matching(twin, r"[a-z]{3}-[0-9]{5}") >= 798
    assert _matching(twin, r"[A-Z]{3}-[0-9]{5}") == 0


def test_the_merge_review_s_random_codes_publish_no_pool_of_one(
    tmp_path: pathlib.Path,
) -> None:
    """The merge review's reproduction, at a floor of eleven, as free text."""
    draw = random.Random(1)
    cells = []
    for row in range(ROWS):
        code = (
            "".join(draw.choice("abcdefghjklmnop") for _letter in range(3))
            + "-" + str(draw.randrange(100, 1000))
        )
        cells += [code.upper() if row == 17 else code]
    result = _round_trip(
        tmp_path, {"value": cells}, ("--smallest-group", "11")
    )
    forms = _column(result)["shape_forms"]
    assert 1 not in forms.values(), forms
    assert forms == {"&&&-%%%": 800}
    _both_pass(result)
    assert _matching(result["twin"]["value"], r"[a-z]{3}-[0-9]{3}") >= 798


def test_a_rest_under_the_line_is_counted_under_the_lower_case_key(
    tmp_path: pathlib.Path,
) -> None:
    """Five capitals under a floor of twenty: the lower-case key counts all.

    It named 795 and pooled five; the lower-case key named without the
    form's own key now counts every cell of the form, and the real file,
    capitals and all, is recounted under it (plan P4-D160).
    """
    cells = [f"abc-{index:05d}" for index in range(795)] + ["ABC-00799"] * 5
    result = _round_trip(
        tmp_path, {"value": cells},
        ("--code", "value", "--smallest-group", "20"),
    )
    assert _column(result)["shape_forms"] == {"&&&-%%%%%": 800}
    _both_pass(result)


def test_a_rest_at_the_line_still_names_both_keys(
    tmp_path: pathlib.Path,
) -> None:
    """Twenty capitals at a floor of twenty: both keys, as before."""
    cells = [f"abc-{index:05d}" for index in range(780)] + ["ABC-00799"] * 20
    result = _round_trip(
        tmp_path, {"value": cells},
        ("--code", "value", "--smallest-group", "20"),
    )
    assert _column(result)["shape_forms"] == {
        "&&&-%%%%%": 780, "@@@-%%%%%": 20,
    }
    _both_pass(result)


def test_a_capital_beside_another_form_s_pool_keeps_the_lower_case_key(
    tmp_path: pathlib.Path,
) -> None:
    """One capitalised code beside nine cells of a rarer, pooled form."""
    cells = (
        [f"abc-{index:05d}" for index in range(790)] + ["ABC-00799"]
        + [f"ab-{index}" for index in range(9)]
    )
    result = _round_trip(
        tmp_path, {"value": cells},
        ("--code", "value", "--smallest-group", "20"),
    )
    assert _column(result)["shape_forms"] == {
        "&&&-%%%%%": 791, "(withheld)": 9,
    }
    _both_pass(result)
    assert _matching(result["twin"]["value"], r"[A-Z]{3}-[0-9]{5}") == 0


def test_a_pool_of_one_rare_form_is_not_published(
    tmp_path: pathlib.Path,
) -> None:
    """The skeptic's (a): 799 `ABC-00001` beside one `WXYZ-123456`.

    Both commits published `{"(withheld)": 1, "@@@-%%%%%": 799}`: a pool
    of one, and a named form one short of `n_present`. No census naming
    the 799 can avoid both, so the form joins the pool (plan P4-D160).
    """
    cells = [f"ABC-{index:05d}" for index in range(799)] + ["WXYZ-123456"]
    result = _round_trip(
        tmp_path, {"value": cells},
        ("--code", "value", "--smallest-group", "20"),
    )
    column = _column(result)
    forms = column["shape_forms"]
    assert 1 not in forms.values(), forms
    assert column["n_present"] - sum(forms.values()) != 1
    assert forms == {"(withheld)": 800}
    _both_pass(result)


def test_a_form_one_short_of_the_present_cells_is_not_published(
    tmp_path: pathlib.Path,
) -> None:
    """The skeptic's (c): one cell too long to have a form beside 799."""
    cells = [f"ABC-{index:05d}" for index in range(799)] + [
        "x" * 40 + "-" + "y" * 63
    ]
    result = _round_trip(
        tmp_path, {"value": cells},
        ("--code", "value", "--smallest-group", "20"),
    )
    column = _column(result)
    assert column["n_present"] == 800
    assert column["shape_forms"] == {}
    _both_pass(result)


def _one_code_word_beside_forms() -> "list[str]":
    draw = random.Random(3)
    cells = [
        "".join(draw.choice("abcdefghjk") for _letter in range(4))
        + "-" + str(draw.randrange(10, 99))
        for _row in range(700)
    ]
    cells += ["abcdef"] + [
        "".join(draw.choice("abcdefghjk") for _letter in range(2))
        + "." + str(draw.randrange(10, 99))
        for _row in range(97)
    ] + ["hello world one", "hello world two"]
    draw.shuffle(cells)
    return cells


def test_a_free_text_census_leaves_no_code_alphabet_cell_over(
    tmp_path: pathlib.Path,
) -> None:
    """`n_code_alphabet` 701 beside code-alphabet forms counting 700.

    The one code-alphabet cell with no form is named by subtraction, so
    the form made of that alphabet is no longer named (plan P4-D160).
    """
    result = _round_trip(
        tmp_path, {"value": _one_code_word_beside_forms()},
        ("--smallest-group", "11"),
    )
    column = _column(result)
    assert column["role"] == "free_text"
    assert column["n_code_alphabet"] == 701
    assert column["shape_forms"] == {"&&.%%": 97}
    _both_pass(result)


@pytest.mark.parametrize(
    ("census", "rule"),
    [
        ({"&&&-%%%%%": 799, "(withheld)": 1}, "SF1"),
        ({"@@@-%%%%%": 799, "(withheld)": 1}, "SF1"),
        ({"@@@-%%%%%": 799}, "SF3"),
    ],
)
def test_the_loader_refuses_a_census_that_names_one_row(
    tmp_path: pathlib.Path, census: "dict[str, int]", rule: str
) -> None:
    """SF1's pool line and SF3's difference line, asked of every census."""
    result = _round_trip(
        tmp_path, {"value": _one_capital()},
        ("--code", "value", "--smallest-group", "20"),
    )
    document = result["document"]
    for column in document["columns"]:
        if column["name"] == "value":
            column["shape_forms"] = census
    edited = fixtures.write_profile(tmp_path, "edited.json", document)
    with pytest.raises(errors.ProfileError) as refused:
        contract.load_profile(str(edited))
    assert rule in str(refused.value)


def test_the_loader_refuses_a_code_alphabet_difference_of_one(
    tmp_path: pathlib.Path,
) -> None:
    """SF3's free-text line, on the producer's own document put back."""
    result = _round_trip(
        tmp_path, {"value": _one_code_word_beside_forms()},
        ("--smallest-group", "11"),
    )
    document = result["document"]
    for column in document["columns"]:
        if column["name"] == "value":
            column["shape_forms"] = {"&&&&-%%": 700, "&&.%%": 97}
    edited = fixtures.write_profile(tmp_path, "edited.json", document)
    with pytest.raises(errors.ProfileError) as refused:
        contract.load_profile(str(edited))
    assert "SF3" in str(refused.value)
    assert "n_code_alphabet" in str(refused.value)


# ------------------ P4-D151 and P4-D152, the layout census's complement


def _one_spaced_beside_codes() -> "list[str]":
    return [
        "G" + "".join("G" if (index >> bit) & 1 else "1" for bit in range(10))
        + "123456789"
        for index in range(800)
    ] + [" " + "G" * 18 + " "]


def test_a_pool_alone_leaves_no_row_over_and_the_description_loads(
    tmp_path: pathlib.Path,
) -> None:
    """The review's second blocker: `{"(withheld)": 800}` beside 801 cells.

    The census covered every cell but one and wrote only its pool, and the
    rule that gives a pool up was never asked, because it ran only while a
    layout was named. The producer published it and its own loader then
    refused the document.
    """
    result = _round_trip(
        tmp_path, {"value": _one_spaced_beside_codes()},
        ("--identifier", "value", "--smallest-group", "11"),
    )
    column = _column(result)
    counted = sum(column["layout_forms"].values())
    assert column["n_present"] == 801
    assert column["n_present"] - counted != 1 or counted == 0
    _both_pass(result)


def test_a_sparse_identifier_s_empty_census_loads(tmp_path: pathlib.Path) -> None:
    """One record number and 799 empty cells, at floors one and eleven."""
    for floor in ("1", "11"):
        result = _round_trip(
            tmp_path / floor, {"value": ["REC12345"] + [""] * 799},
            ("--identifier", "value", "--smallest-group", floor),
        )
        column = _column(result)
        assert (column["n_present"], column["layout_forms"]) == (1, {})
        _both_pass(result)


# ------------------------------------------ P4-D154, the hexadecimal guess


def test_a_letter_that_never_trades_places_with_a_figure_is_a_letter(
    tmp_path: pathlib.Path,
) -> None:
    """`A1000000` to `F1000799`: a letter and seven figures, 800 of 800."""
    cells = ["ABCDEF"[index % 6] + str(1000000 + index) for index in range(800)]
    result = _round_trip(tmp_path, {"value": cells}, ("--identifier", "value"))
    assert _column(result)["layout_forms"] == {"@%%%%%%%": 800}
    rule = re.compile(r"[A-Z][0-9]{7}")
    for cells_of in (cells, result["twin"]["value"]):
        assert len([cell for cell in cells_of if rule.fullmatch(cell)]) == 800
    _both_pass(result)


# ------------------------------------------------ P4-D155, the lone nought


def test_a_whole_number_identifier_holding_nought_keeps_its_layout(
    tmp_path: pathlib.Path,
) -> None:
    """0 to 119: the twin wrote twenty-one three-figure cells against twenty."""
    cells = [f"{number}" for number in range(120)]
    result = _round_trip(
        tmp_path, {"value": cells},
        ("--identifier", "value", "--smallest-group", "10"),
    )
    assert _column(result)["layout_forms"] == {"%%%": 20}
    three = [cell for cell in result["twin"]["value"] if len(cell) == 3]
    assert len(three) == 20
    assert "0" in result["twin"]["value"]
    _both_pass(result)


@pytest.mark.parametrize(
    ("rows", "lengths"), [(800, [9, 90, 701, 0]), (2000, [9, 90, 900, 1001])]
)
def test_a_column_counted_from_one_is_not_written_holding_nought(
    tmp_path: pathlib.Path, rows: int, lengths: "list[int]"
) -> None:
    """The skeptic's regression of P4-D155: `1` to `800` came back with `0`.

    The twin wrote ten one-figure cells and 89 two-figure ones against the
    table's nine and ninety. The lone 0 is the last one-figure number and
    is walked after every number shorter than the shortest named layout of
    figures alone (plan P4-D162), so `1` to `2000` keeps 900 three-figure
    cells as well.
    """
    cells = [f"{number}" for number in range(1, rows + 1)]
    result = _round_trip(tmp_path, {"value": cells}, ("--identifier", "value"))
    twin = result["twin"]["value"]
    assert "0" not in twin
    assert [
        len([cell for cell in twin if len(cell) == size]) for size in (1, 2, 3, 4)
    ] == lengths
    _both_pass(result)


@pytest.mark.parametrize(
    ("first", "rows", "floor", "nought"),
    [(1, 11, "3", False), (0, 102, "1", True)],
)
def test_the_oracle_and_the_product_walk_the_lone_nought_alike(
    tmp_path: pathlib.Path, first: int, rows: int, floor: str, nought: bool
) -> None:
    """P4-D162's walk, product and oracle, on the column the product wrote.

    `1` to `11` at a floor of three pools both layouts, so no layout of
    figures alone is named and the lone 0 comes after every published
    length: the eleven cells are `1` to `11`. `0` to `101` names `%%%`, so
    0 comes after the two-figure numbers and is the hundredth short cell.
    No frozen case holds this walk: both branch vector files stand within
    two kilobytes of the provenance cap, and a case of an identifier
    column costs about two.
    """
    from tests.test_generation_reference import gen

    cells = [f"{number}" for number in range(first, first + rows)]
    # THE ELEVEN-CELL CASE IS DESCRIBED BY THE PRODUCER (plan P4-D341):
    # the command refuses a table under the population floor and writes
    # nothing, and eleven cells is the shape -- `1` to `11` at a floor
    # of three is what pools both layouts and puts the lone 0 after
    # every published length. Grown to a hundred it is a different
    # walk. The 102-cell case is over the floor and is the command's,
    # which keeps one of the two on the shipped path.
    result = _round_trip(
        tmp_path, {"value": cells},
        ("--identifier", "value", "--smallest-group", floor),
        by_command=rows >= parsing.POPULATION_FLOOR,
    )
    _both_pass(result)
    written = sorted(set(result["twin"]["value"]))
    assert ("0" in written) is nought
    assert len(written) == rows
    column = _column(result)
    assert sorted(set(gen._identifier_content(dict(column)))) == written


def test_the_oracle_writes_the_lone_nought_last_and_its_mutant_moves_cells(
    monkeypatch,
) -> None:
    """The oracle's mirror of P4-D155 and P4-D162 holds a committed byte up.

    `identifier_edge_spacing` holds one identity of one figure: `1`, the
    first one-figure number. Withdrawing P4-D162's order (the ten figures
    counted from `0`) writes `0` there instead.
    """
    from tests.test_generation_reference import gen

    before, _claims = gen.build_case("identifier_edge_spacing")
    assert "1" in before["cells"] and "0" not in before["cells"]
    assert gen.identifier_family(gen.FIGURES, True, 1)[0][0] == "1"
    original = gen.identifier_family

    def nought_first(band, whole_numbers, length):
        found = original(band, whole_numbers, length)
        if whole_numbers and band == gen.FIGURES and length == 1:
            return gen.DIGITS, length, None, ""
        return found

    monkeypatch.setattr(gen, "identifier_family", nought_first)
    after, _claims = gen.build_case("identifier_edge_spacing")
    assert after["cells"] != before["cells"]
    assert "0" in after["cells"]


# --------------------------------------------------- P4-D156, the proven sign


@pytest.mark.parametrize("sign", ["-", "+"])
def test_a_signed_record_number_keeps_its_layout(
    tmp_path: pathlib.Path, sign: str
) -> None:
    """`-1000000` upward: 0 of 800 twin cells kept `-%%%%%%%`."""
    cells = [f"{sign}{1000000 + index}" for index in range(800)]
    result = _round_trip(tmp_path, {"value": cells}, ("--identifier", "value"))
    layout = sign + "%" * 7
    assert _column(result)["layout_forms"] == {layout: 800}
    rule = re.compile(re.escape(sign) + r"[0-9]{7}")
    assert len(
        [cell for cell in result["twin"]["value"] if rule.fullmatch(cell)]
    ) == 800
    assert "formula" in result["report"]
    _both_pass(result)


def test_signed_and_unsigned_record_numbers_each_keep_their_layout(
    tmp_path: pathlib.Path,
) -> None:
    """400 `-10000` upward beside 400 `20000` upward (skeptic, MINOR).

    The first packing put the slot pinned to six characters in the figures
    band, which wrote `100000`: 399 and 401 against 400 and 400, twin exit
    3. The next packing that meets every other count is taken (P4-D163).
    """
    cells = [f"-{10000 + index}" for index in range(400)] + [
        f"{20000 + index}" for index in range(400)
    ]
    result = _round_trip(tmp_path, {"value": cells}, ("--identifier", "value"))
    assert _column(result)["layout_forms"] == {"%%%%%": 400, "-%%%%%": 400}
    twin = result["twin"]["value"]
    assert _matching(twin, r"[0-9]{5}") == 400
    assert _matching(twin, r"-[0-9]{5}") == 400
    assert "layout_forms" not in result["report"]
    _both_pass(result)


def test_a_sign_before_a_letter_is_still_refused() -> None:
    """Only a sign before figures is proven; `=`, `@` and text stay barred."""
    assert generation._signs_a_number("-%%%%")
    assert generation._signs_a_number("+%%.%")
    assert not generation._signs_a_number("-@@%")
    assert not generation._signs_a_number("=%%%")
    assert not generation._signs_a_number("-")


# ----------------------------------------------- P4-D157, partners' layouts


def test_case_folded_partners_pay_the_layout_census(
    tmp_path: pathlib.Path,
) -> None:
    """`G` and four figures on 600 rows beside `g` on 200: the twin wrote 500/300."""
    cells = [f"G{index:04d}" for index in range(600)] + [
        f"g{index:04d}" for index in range(200)
    ]
    for seed in ("1", "4", "7"):
        result = _round_trip(
            tmp_path / seed, {"value": cells}, ("--identifier", "value"), seed
        )
        assert _column(result)["layout_forms"] == {"&%%%%": 200, "@%%%%": 600}
        for cells_of in (cells, result["twin"]["value"]):
            assert _matching(cells_of, r"[A-Z][0-9]{4}") == 600
            assert _matching(cells_of, r"[a-z][0-9]{4}") == 200
        _both_pass(result)


def test_a_two_letter_partner_turns_both_letters(tmp_path: pathlib.Path) -> None:
    """`AB` beside `ab`: a partner wears the named layout, not `aB`."""
    cells = [f"AB{index:04d}" for index in range(500)] + [
        f"ab{index:04d}" for index in range(300)
    ]
    result = _round_trip(tmp_path, {"value": cells}, ("--identifier", "value"))
    for cells_of in (cells, result["twin"]["value"]):
        assert _matching(cells_of, r"[a-z]{2}[0-9]{4}") == 300
        assert _matching(cells_of, r"[A-Z]{2}[0-9]{4}") == 500
    _both_pass(result)


def test_the_twin_s_report_names_a_layout_it_did_not_hold(
    tmp_path: pathlib.Path, monkeypatch
) -> None:
    """The recount P4-D157 adds: a layout miss can no longer go unnamed."""
    cells = [f"G{index:04d}" for index in range(600)] + [
        f"g{index:04d}" for index in range(200)
    ]
    result = _round_trip(tmp_path, {"value": cells}, ("--identifier", "value"))
    described = contract.load_profile(str(result["profile"]))

    def no_partner_layout(layout, convention, count, facts):
        return ["" for _each in range(count)]

    monkeypatch.setattr(generation, "_partner_layouts", no_partner_layout)
    twin = generation.generate(described, 4)
    named = [note.fact for note in twin.deviations]
    assert "layout_forms.&%%%%" in named
    assert "layout_forms.@%%%%" in named


# ------------------------------------------ P4-D158, the table's own holes


def test_a_declared_identifier_never_writes_another_column_s_hole(
    tmp_path: pathlib.Path,
) -> None:
    """`FPQ7317879` declared absent beside `REC` numbers: eight obligations missed."""
    cells = [f"REC{1000000 + index}" for index in range(800)]
    other = ["FPQ7317879"] * 20 + ["ordinary"] * 780
    result = _round_trip(
        tmp_path, {"value": cells, "other": other},
        ("--identifier", "value", "--missing-value", "FPQ7317879"),
    )
    assert "FPQ7317879" not in result["twin"]["value"]
    _both_pass(result)


def test_a_free_text_column_never_writes_another_column_s_hole(
    tmp_path: pathlib.Path,
) -> None:
    """The review's `lower_codes(1)` fixture beside a declared `y6o-7p3`."""
    from tests.test_landing_2b18_forms_and_spellings import lower_codes

    other = ["y6o-7p3"] * 20 + ["ordinary"] * 780
    result = _round_trip(
        tmp_path, {"value": lower_codes(1), "other": other},
        ("--missing-value", "y6o-7p3"),
    )
    assert _column(result)["role"] == "free_text"
    assert "y6o-7p3" not in result["twin"]["value"]
    _both_pass(result)


def test_the_oracle_recounts_presence_as_a_reader_counts_it() -> None:
    """Review item 10: the oracle certified `NA` as a present record number."""
    from tests.test_generation_reference import gen

    case, _claims = gen.build_case("identifier_absent_words")
    assert "NA" not in case["cells"]
    column = gen._universal(
        "column_1", "identifier", "code", "identifier", "ok",
        n_present=20, n_missing=0, n_distinct=20, n_distinct_folded=20,
        n_numeric=0, n_not_numeric=20, n_out_of_range=0, n_contradictory=0,
        min_length=2, max_length=2, all_whole_numbers=False,
        n_all_digits=0, n_code_alphabet=20,
        n_distinct_by_occurrences={"1": 20}, layout_forms={"@@": 20},
    )
    written = list(case["content"])
    written[0] = "NA"
    with pytest.raises(AssertionError) as refused:
        gen._identifier_recount(column, written)
    assert "n_present" in str(refused.value)


# ------------------------------------------------ P4-D159, the validator


def test_a_faithful_form_is_not_missed_when_its_case_convention_changes(
    tmp_path: pathlib.Path,
) -> None:
    """`ab123` and `cd456` beside `00xy` and one `00XY`, as codes at eleven."""
    cells = (
        ["ab123"] * 100 + ["cd456"] * 100
        + [f"{index:02d}xy" for index in range(99)] + ["00XY"]
    )
    result = _round_trip(
        tmp_path, {"value": cells},
        ("--code", "value", "--smallest-group", "11"),
    )
    assert _column(result)["shape_forms"] == {"%%@@": 100, "@@%%%": 200}
    _both_pass(result)


# ------------------ residual R-P3-11 (review item 8), closed 2026-09-17


def test_a_real_table_whose_hole_spellings_are_pooled_holds_both_counts(
    tmp_path: pathlib.Path,
) -> None:
    """280 record numbers beside ten `NA` and ten `N/A`, at a floor of twenty.

    Neither spelling reaches the floor, so the description pools both.
    Counted by blankness the real file was 300 present and nought missing
    against its own 280 and 20, exit 3 on exactly the two presence counts
    -- residual R-P3-11, pinned here at that size until the owner ruled.
    The ruling of 2026-09-17 took option A (plan P4-D200): the pooled
    words count as absent, up to the pool's total of twenty, so the table
    passes its own description and its twin still does.
    """
    cells = [f"R{index:07d}" for index in range(280)] + ["NA"] * 10 + [
        "N/A"
    ] * 10
    result = _round_trip(
        tmp_path, {"value": cells},
        ("--identifier", "value", "--smallest-group", "20"),
    )
    column = _column(result)
    assert (column["n_present"], column["n_missing"]) == (280, 20)
    assert column["n_missing_withheld"] == 20
    assert result["generated"] == 0
    assert (result["twin_exit"], result["real_exit"]) == (0, 0)
    report = (tmp_path / "real_exit" / "real-quality.txt").read_text(
        encoding="utf-8"
    )
    assert "presence.n_present [universal.n_present]: HELD" in report
    assert "presence.n_missing [universal.n_missing]: HELD" in report


def test_a_file_spelling_a_description_s_empty_holes_is_still_missed(
    tmp_path: pathlib.Path,
) -> None:
    """The round-2 witness, with the measured file pooling its own spellings.

    The description is written from thirty EMPTY holes, so it pools
    nothing; the measured file spells them 25 `n/a` and 5 `N/A`, which its
    OWN description would pool, and the presence counts are taken by
    blankness and missed.
    """
    # THIRTY HOLES, AND VALUES ENOUGH TO REACH THE POPULATION FLOOR
    # (plan P4-D341): the command refuses a smaller table and writes
    # nothing. What this witness needs is thirty empty holes and a
    # measured file that spells them 25 and 5 -- the pool and the
    # pooled -- so the holes stay thirty and the values are counted up
    # to the floor from them.
    _HOLES = 30
    values = [
        f"{10 + index * 3}.5"
        for index in range(parsing.POPULATION_FLOOR - _HOLES)
    ]
    result = _round_trip(
        tmp_path / "described", {"value": values + [""] * _HOLES},
        ("--smallest-group", "11"),
    )
    assert _column(result)["n_missing_withheld"] == 0
    spelled = values + ["n/a"] * 25 + ["N/A"] * 5
    other = tmp_path / "spelled.csv"
    other.write_text(
        fixtures.rows_to_csv(
            ["value", "other"],
            [[cell, f"row{index % 7}"] for index, cell in enumerate(spelled)],
        ),
        encoding="utf-8",
        newline="",
    )
    checked = tmp_path / "checked"
    checked.mkdir()
    code = _exit_of(
        ["validate", str(result["profile"]), "--twin", str(other),
         "--out-dir", str(checked), "--replace"]
    )
    report = (checked / "spelled-quality.txt").read_text(encoding="utf-8")
    assert code == 3
    assert "presence.n_present [universal.n_present]: MISSED" in report
