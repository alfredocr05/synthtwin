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
- **P4-D153** a case split leaves no count of one, in the census or its pool;
- **P4-D154** letters inside `a` to `f` that never trade places with a
  figure are letters, not hexadecimal;
- **P4-D155** the lone figure 0 is a whole number one figure long;
- **P4-D156** a sign before figures is written where the census proves it;
- **P4-D157** a fold-collision partner wears the layout its identity
  reserved, and the twin's report recounts every layout;
- **P4-D158** a spelling the table declares absent is never invented, in
  any column;
- **P4-D159** validation recounts a form under the submitted census's case
  convention. (Review item 8, the two presence counts of a column whose
  built-in hole spellings are pooled, is residual R-P3-11, which the plan
  records as the owner's pending decision; it is not decided here.)

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
from tests.test_stage2_round_trip import _exit_of

ROWS = 800


def _round_trip(
    folder: pathlib.Path,
    columns: "dict[str, list[str]]",
    flags: "tuple[str, ...]" = (),
    seed: str = "4",
) -> dict:
    """Describe, build, validate the twin AND the table; hand back all four.

    A second column stands beside a column under test unless the caller
    gives one, because a one-column table holding an empty cell is
    refused (plan P4-D74).
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
    assert _exit_of(
        ["profile", str(table), "--out-dir", str(folder), "--replace", *flags]
    ) == 0
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
    its count and by its complement. Blind to case, it names nothing.
    """
    result = _round_trip(
        tmp_path, {"value": _one_capital()},
        ("--code", "value", "--smallest-group", "20"),
    )
    forms = _column(result)["shape_forms"]
    assert 1 not in forms.values(), forms
    assert forms == {"@@@-%%%%%": 800}
    _both_pass(result)


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
    _both_pass(result)


def test_a_rest_of_two_or_more_is_still_split_off_and_pooled(
    tmp_path: pathlib.Path,
) -> None:
    """The rule withdraws a count of one and nothing more."""
    cells = [f"abc-{index:05d}" for index in range(795)] + ["ABC-00799"] * 5
    result = _round_trip(
        tmp_path, {"value": cells},
        ("--code", "value", "--smallest-group", "20"),
    )
    assert _column(result)["shape_forms"] == {
        "&&&-%%%%%": 795, "(withheld)": 5,
    }
    _both_pass(result)


def test_a_remainder_of_one_is_not_split_off_even_where_the_pool_is_larger(
    tmp_path: pathlib.Path,
) -> None:
    """The per-form half of P4-D153, beside another form's pooled cells.

    One capitalised code joins nine cells of a rarer form in the pool, so
    the pool is ten and the census-wide half says nothing; the per-form
    half still names the form blind to case.
    """
    cells = (
        [f"abc-{index:05d}" for index in range(790)] + ["ABC-00799"]
        + [f"ab-{index}" for index in range(9)]
    )
    result = _round_trip(
        tmp_path, {"value": cells},
        ("--code", "value", "--smallest-group", "20"),
    )
    forms = _column(result)["shape_forms"]
    assert "&&&-%%%%%" not in forms, forms
    assert forms["@@@-%%%%%"] == 791
    _both_pass(result)


def test_the_loader_refuses_a_lower_case_key_beside_a_pool_of_one(
    tmp_path: pathlib.Path,
) -> None:
    """SF1's third line, which the review asked the loader to enforce."""
    result = _round_trip(
        tmp_path, {"value": _one_capital()},
        ("--code", "value", "--smallest-group", "20"),
    )
    document = result["document"]
    for column in document["columns"]:
        if column["name"] == "value":
            column["shape_forms"] = {"&&&-%%%%%": 799, "(withheld)": 1}
    edited = fixtures.write_profile(tmp_path, "edited.json", document)
    with pytest.raises(errors.ProfileError) as refused:
        contract.load_profile(str(edited))
    assert "SF1" in str(refused.value)


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


def test_withdrawing_the_lone_nought_moves_the_frozen_edge_spacing_cells(
    monkeypatch,
) -> None:
    """The oracle's mirror of P4-D155 holds a committed byte up."""
    from tests.test_generation_reference import gen

    before, _claims = gen.build_case("identifier_edge_spacing")
    assert "0" in before["cells"]
    original = gen.identifier_family

    def refused_nought(band, whole_numbers, length):
        found = original(band, whole_numbers, length)
        if whole_numbers and band == gen.FIGURES and length == 1:
            return gen.DIGITS, length, gen._not_a_leading_zero, ""
        return found

    monkeypatch.setattr(gen, "identifier_family", refused_nought)
    after, _claims = gen.build_case("identifier_edge_spacing")
    assert after["cells"] != before["cells"]


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
