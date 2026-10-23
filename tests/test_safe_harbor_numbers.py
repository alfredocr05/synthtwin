"""P4-D427 (lane SH): ages over 89 and five-figure ZIP codes in number columns.

TWO LIVE SAFE HARBOR EXPOSURES, measured on b85200be (the orchestrator's
LANE SH NOTE of 2026-10-23; wave6/SH/probe-base-600.log and
probe-base-20000.log):

1. AGES OVER 89 (45 CFR 164.514(b)(2)(i)(C)). 20,000 ages from 18 to 103,
   nobody answering, published `max` 103, `p99` 99, `p98` 94 and the high
   tail's values 99 to 103, and the twin wrote 580 cells above 90; one
   `999` placeholder cell or twenty left them so (ZR-b's verify 2, item 2).
2. FIVE-FIGURE ZIP CODES READ AS NUMBERS (ZR-b's verify 2, item 1). Alone
   they are held by P4-D401's questions; beside one `UNKNOWN` cell or three
   `HOMELESS`, with or without a leading zero, the column was read as a
   count and 38 or 39 real ZIPs printed at 600 rows (44 at 20,000), the
   twin writing over 400 real ZIP cells (over 13,000).

THE RULE (lane ZR-b's page, ZS.1 and ZS.3). A number column whose present
numbers, all-nines placeholders of either sign aside (at most one present
cell in three), lie within 0 to 125 and include one above 89 is put the
Safe Harbor question, and while it is open every value above 89 is read
as 90 for the whole description (`top_coded`), the twin writes none above
90, and validate reads the real column under the same top-code, so the
real table and the twin both validate. A number column whose present
cells are five-figure whole numbers, padded or not, beside at most one in
three set aside as words, is held whole until the question is answered
`no`; where a question offering `identifier` is already put to it, that
question holds it and no second one is added. `no` describes the column
as before; `yes` holds it as P4-D401 holds a column whose question is
open.

THE GATE: K-S3-64's Safe Harbor number shapes (`shapes.SAFE_HARBOR_NUMBERS`)
at 600 rows, and one of each class at 20,000 (every shape at both sizes
through `tools/measurements/kpi_run.py --slow`): 0 ZIPs and 0 ages over 89
in any file -- the description, its summary, the questions file, the
screen, the twin's report and the quality reports -- and in the twin,
the question put. The mutants of wave6/SH/sh_mutants.py turn it red.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from synthtwin import asking, cli, taxonomy

import unanswered_identifier_shapes as shapes

# Validation limits of the held block (plan P4-D427, stated): at 20,000
# rows a column of five-figure numbers beside ONE word is published with
# `all_whole_numbers` false beside every cell counted in figures (the
# census line absorbs the one), and the held generator writes whole
# numbers only, so the twin misses that one fact (exit 3); owner CODES-1
# part C, as the held shapes' `shapes.VALIDATION_LIMITS` are.
_HELD_LIMITS_AT_20000 = ("zip5word_unknown", "zip5word52_unknown")


def _check(seen: "dict[str, object]", kind: str, rows: int) -> None:
    assert seen["profile_exit"] == 0 and seen["generate_exit"] == 0, seen
    if not (rows >= 20000 and kind in _HELD_LIMITS_AT_20000):
        assert seen["validate_exit"] == 0, seen
    assert seen["description_values"] == 0, seen
    assert seen["description_fragments"] == 0, seen
    assert seen["twin_cells"] == 0, seen
    assert seen["twin_fragments"] == 0, seen
    asked = seen["asked"]
    assert isinstance(asked, list) and len(asked) == 1, seen
    if kind in shapes.AGES:
        # THE REAL TABLE MEETS ITS OWN DESCRIPTION, read under the top-code.
        assert seen["validate_real_exit"] == 0, seen
        assert seen["top_coded"] == taxonomy.TOP_CODE, seen
        assert asked[0] == [asking.ANSWER_SAFE_HARBOR_NO, asking.ANSWER_SAFE_HARBOR_YES]
        assert seen["read_as_now"] == [asking.SAFE_HARBOR_TOP_CODED]
        assert "THE SAFE HARBOR QUESTION" in f"{seen['screen']}"
    else:
        assert seen["role"] == taxonomy.ROLE_IDENTIFIER, seen
        # ONE QUESTION A COLUMN: the Safe Harbor question, or the question
        # offering `identifier` already put, which holds it meanwhile.
        offered = asked[0]
        assert isinstance(offered, list)
        assert (
            offered == [asking.ANSWER_SAFE_HARBOR_NO, asking.ANSWER_SAFE_HARBOR_YES]
            and seen["read_as_now"] == [asking.ANSWER_SAFE_HARBOR_YES]
        ) or (
            asking.ANSWER_IDENTIFIER in offered
            and seen["read_as_now"] == [asking.ANSWER_IDENTIFIER]
        ), seen


@pytest.mark.parametrize("kind", shapes.SAFE_HARBOR_NUMBERS)
def test_no_zip_and_no_age_over_89_is_published_at_600_rows(
    tmp_path: pathlib.Path, kind: str
) -> None:
    """0 ZIPs, 0 ages over 89 in every file and the twin; the question put."""
    _check(shapes.run_safe_harbor(tmp_path, kind, 600), kind, 600)


@pytest.mark.parametrize(
    "kind", ["ages", "ages999x20", "zip5word_homeless", "zip5word52_unknown"]
)
def test_no_zip_and_no_age_over_89_is_published_at_20000_rows(
    tmp_path: pathlib.Path, kind: str
) -> None:
    """The owner's table floor: the same at 20,000 rows."""
    _check(shapes.run_safe_harbor(tmp_path, kind, 20000), kind, 20000)


# -- the reach, cell by cell ----------------------------------------------


def _ages(*extra: str) -> "list[str]":
    return [f"{age}" for age in range(18, 104)] + list(extra)


def test_the_top_code_reads_every_value_above_89_as_90() -> None:
    coded = taxonomy.top_coded_cells(_ages("", "N/A"))
    assert coded is not None
    assert max(float(cell) for cell in coded if cell[:1].isdigit()) == 90.0
    assert coded[-2:] == ["", "N/A"]
    assert coded[:72] == [f"{age}" for age in range(18, 90)]


@pytest.mark.parametrize("placeholder", ["999", "9999", "-9", "-99", "-999", "999.0"])
def test_an_all_nines_placeholder_of_either_sign_is_set_aside_and_kept(
    placeholder: str,
) -> None:
    """ZR-b's verify 2, item 2: one `999` turned the reach off."""
    for times in (1, 20):
        coded = taxonomy.top_coded_cells(_ages(*([placeholder] * times)))
        assert coded is not None, (placeholder, times)
        assert coded[-times:] == [placeholder] * times


def test_placeholders_over_a_third_of_the_cells_are_values() -> None:
    assert taxonomy.top_coded_cells(_ages(*(["999"] * 50))) is None


@pytest.mark.parametrize(
    "cells",
    [
        [f"{age}" for age in range(18, 90)],  # nothing above 89
        _ages("126"),  # a value above 125
        _ages("-1"),  # a negative value that is not nines alone
    ],
)
def test_the_top_code_does_not_reach(cells: "list[str]") -> None:
    assert taxonomy.top_coded_cells(cells) is None


def test_the_top_code_keeps_the_decimals_and_the_comma() -> None:
    assert taxonomy.top_coded_cells(["45.5", "93.25", "70"]) == ["45.5", "90.00", "70"]
    assert taxonomy.top_coded_cells(["45,5", "93,25"], comma=True) == ["45,5", "90,00"]
    assert taxonomy.at_most_the_top_code(["91", "90.5", "88", "999", "x"]) == [
        "90", "90.0", "88", "999", "x"
    ]


@pytest.mark.parametrize(
    ("cells", "reached"),
    [
        (["02100"] * 20 + ["UNKNOWN"], True),
        (["52240"] * 20 + ["HOMELESS"] * 3, True),
        (["52240.0"] * 20 + ["-1", "0"], True),
        (["52240"] * 20, True),
        (["52240"] * 4 + ["UNKNOWN"] * 3, False),  # more than a third set aside
        (["52240"] * 20 + ["2100"], False),  # four figures
        (["52240"] * 20 + ["5224a"], False),
    ],
)
def test_five_figures_beside_a_few_words(cells: "list[str]", reached: bool) -> None:
    assert taxonomy.five_figures_beside_words(cells) is reached


# -- the answers ----------------------------------------------------------


def _answered(folder: pathlib.Path, kind: str, answer: str) -> "dict[str, object]":
    """Profile unanswered, answer the Safe Harbor question, profile with the answers twice."""
    table, _real = shapes.write_safe_harbor_table(folder, kind, 600)
    with shapes.nobody_at_the_keyboard():
        assert cli.main(["profile", f"{table}", "--out-dir", f"{folder}", "--replace"]) == 0
        questions = folder / f"{kind}_long-questions.json"
        written = json.loads(questions.read_text(encoding="utf-8"))
        for entry in written["asked"]:
            if entry["column"] == kind:
                entry["your_answer"] = answer
        answers = folder / "answers.json"
        answers.write_text(json.dumps(written), encoding="utf-8", newline="\n")
        assert cli.main(["profile", f"{table}", "--out-dir", f"{folder}", "--replace",
                         "--answers", f"{answers}"]) == 0
        first = json.loads((folder / f"{kind}_long-profile.json").read_text(encoding="utf-8"))
        # ...and the file that run wrote, handed back unchanged (P4-D408).
        kept = folder / "kept.json"
        kept.write_text(questions.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
        assert cli.main(["profile", f"{table}", "--out-dir", f"{folder}", "--replace",
                         "--answers", f"{kept}"]) == 0
    second = json.loads((folder / f"{kind}_long-profile.json").read_text(encoding="utf-8"))
    carried = json.loads(questions.read_text(encoding="utf-8"))
    assert first == second
    block = [one for one in first["columns"] if one["name"] == kind][0]
    return {"block": block, "carried": carried[asking.ANSWERED_BEFORE],
            "asked": [entry for entry in carried["asked"] if entry["column"] == kind]}


def test_no_describes_the_ages_as_before(tmp_path: pathlib.Path) -> None:
    seen = _answered(tmp_path, "ages", asking.ANSWER_SAFE_HARBOR_NO)
    block = seen["block"]
    assert isinstance(block, dict)
    assert "top_coded" not in block
    rungs = list(block["percentiles"].values()) + list(block["percentiles_between"].values())
    assert max(rung for rung in rungs if rung is not None) > 90
    assert [(entry["column"], entry["your_answer"]) for entry in seen["carried"]] == [
        ("ages", asking.ANSWER_SAFE_HARBOR_NO)
    ]
    assert seen["asked"] == []


@pytest.mark.parametrize("kind", ["ages", "zip5word_homeless"])
def test_yes_holds_the_column_without_counting_the_table_in_it(
    tmp_path: pathlib.Path, kind: str
) -> None:
    """`yes` is P4-D401's held block, never a person column (86 'people' refused)."""
    seen = _answered(tmp_path, kind, asking.ANSWER_SAFE_HARBOR_YES)
    block = seen["block"]
    assert isinstance(block, dict)
    assert block["role"] == taxonomy.ROLE_IDENTIFIER
    assert [(entry["column"], entry["your_answer"]) for entry in seen["carried"]] == [
        (kind, asking.ANSWER_SAFE_HARBOR_YES)
    ]


def test_no_lifts_the_hold_on_five_figures(tmp_path: pathlib.Path) -> None:
    seen = _answered(tmp_path, "zip5word_homeless", asking.ANSWER_SAFE_HARBOR_NO)
    block = seen["block"]
    assert isinstance(block, dict)
    assert block["role"] == taxonomy.ROLE_COUNT


def test_the_question_is_the_owners_sentence() -> None:
    """The owner's Z1 wording, verbatim in plan-dec/OWNER-ANSWERS.md (2026-10-16)."""
    assert asking.safe_harbor_sentence("age") == (
        "Could a value of 'age' name a person, a place smaller than a state, a "
        "birth date, or a record, account or device number?"
    )
    assert "an age over 89 years" in asking.SAFE_HARBOR_CLASSES
    assert "45 CFR 164.514(b)(2)(i)" in asking.SAFE_HARBOR_CLASSES
