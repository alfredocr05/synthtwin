"""P4-D427 (lane SH): ages over 89 and ZIP codes in columns of numbers.

TWO LIVE SAFE HARBOR EXPOSURES, measured on b85200be (the orchestrator's
LANE SH NOTE of 2026-10-23; wave6/SH/probe-base-600.log and
probe-base-20000.log), and the escapes the orchestrator's LANE SH addenda
1 to 5, skeptic 1 of lane SH (wave6/SH-sk1.md) and Codex's review of the
lane measured on its first head, 28e5d2f5:

1. AGES OVER 89 (45 CFR 164.514(b)(2)(i)(C)). 20,000 ages from 18 to 103,
   nobody answering, published `max` 103, `p99` 99, `p98` 94 and the high
   tail's values 99 to 103; and on 28e5d2f5 the column's ROLE (60 and 95
   read binary, 95 alone constant, `NN years` read as labels), an OUTLIER
   (one `130` or `126`), PLACEHOLDERS on a third of the rows (`999`,
   `-1`, `888`), WORDS of any share (`UNK`, 800 different words) and the
   profiler's own number grammar (`99,000e-3`) each still printed ages
   above 89.
2. ZIP CODES READ AS NUMBERS (ZR-b's verifies 2 to 6). Five-figure ZIPs
   beside one `UNKNOWN` cell or three `HOMELESS` printed 38 to 44 real
   ZIPs; and on 28e5d2f5 ZIPs read binary or constant, ZIPs that lost
   their leading zero (four figures) beside five-figure ones or beside
   `99999`, `-99`, `-9999` or `999999` of any share, beside words in a
   label role, with a `+` sign or beside ZIP+4 cells each printed every
   real ZIP.

THE RULE (lane ZR-b's page, ZS.1 and ZS.3, as the addenda correct it;
`taxonomy.safe_harbor_reach`). The reach is judged on the BULK of a
column's present cells, in every role that prints a value: words, the
column's missing values, placeholders written as nines alone, one-figure
negatives (every negative for ZIPs) and up to three values outside the
reach that the floor's rows repeat are set aside whatever their share (a
measurement's tail past the reach is many values and stays). AGES: the
cells that remain within 0 to 125 but for fewer than the floor's rows or
one in twenty, one of 90 or more, a unit word after the number read with
it, at most half of them written with a leading zero; while the Safe Harbor
question is open every value from 90 to 125 is read as 90 for the whole
description (`top_coded`), in the column's own form (`+90`, `90 years`),
the twin writes none above 90, and validate reads the checked file under
the same top-code. ZIPS: at least two in three of the cells that remain
whole numbers of four or five figures, padded, signed or not, or ZIP+4
forms; the column is held whole until `no`.
Where a question offering `identifier` is already put to the column, that
question holds it and no second one is added.

THE GATE: K-S3-64's Safe Harbor number shapes (`shapes.SAFE_HARBOR_NUMBERS`)
at 600 and at 20,000 rows, the owner's table floor: 0 ZIPs and 0 ages
over 89 in any file -- the description, its summary, the questions file,
the screen, the twin's report and the quality reports -- and in the twin,
the question put; and (the orchestrator's LANE SH ADDENDUM 6) a column
put any open question offering `identifier` -- the date-count question
at any width among them -- is held whole meanwhile (`acct_date_count`).
The mutants of wave6/SH/r1/sh_mutants_r1.py turn it red.

THE SECOND REPAIR (the combined verify on 9ccb6bc7, wave6/SH-verify.md):
the column's other question answered -- the padded question `measurement`
for NAACCR's three-figure ages, the date-count, person or two-numbers
question `measurement` or `keep` for ZIP codes --
puts the Safe Harbor question in that run, one question a column, and
publishes no age over 89 and no ZIP meanwhile
(`shapes.SAFE_HARBOR_ANSWERED`, at 600 and 20,000 rows); every open
question offering `identifier` counts as the one put (ZIP+4 cells); an
undeclared decimal comma is read where the point reads no number; a
nine-figure whole number is a ZIP+4 written without its hyphen; and the
twin's clamp keeps the declared missing cells. The mutants of
wave6/SH/r2/sh_mutants_r2.py turn it red.

THE THIRD REPAIR (verify 2 on 9a333e46, wave6/SH-verify2.md, and the
orchestrator's rulings R1 and R2 of 2026-10-25, HIPAA first): `code` is no
release either. A ZIP-shaped column answered or declared `code` stays held
and is put the Safe Harbor question in that run, only `no` freeing it
(LANE SH ADDENDA 7 and 8: 40 of 40 ZIPs printed at 20,000 rows on
9a333e46, and the zoo's own `patients.zip5`, 12 of 12 on every twin cell);
and a column in the age reach is top-coded whatever its other answer,
`code` included (NAACCR's ages answered `code` printed 93 and 100 to 105,
the twin 572 cells over 90). The zoo answers that question truthfully:
`yes`, a ZIP names a place smaller than a state. The mutants of
wave6/SH/r3/sh_mutants_r3.py turn it red.
"""

from __future__ import annotations

import contextlib
import io
import json
import pathlib
import re
import time

import pytest

from synthtwin import asking, cli, taxonomy

import unanswered_identifier_shapes as shapes

# The held block's validation limit at 20,000 rows (plan P4-D427, stated).
_HELD_LIMITS_AT_20000 = shapes.SAFE_HARBOR_HELD_LIMITS_AT_20000
# A column held as record numbers: its real table misses the census of
# repetition its held block publishes absorbed, as every held block's
# real table does (plan P4-D401; measured on the held ZIP shapes, which
# no top-code reaches).
_HELD_REAL_MISSES = {"distinct.n_distinct_by_occurrences"}
_SUMMARY_LINE = "ages over 89: every value above 89 is read as 90"
_MISSED = re.compile(r"^\s+(\S+) \[[^\]]+\]: MISSED", re.M)


def _check(seen: "dict[str, object]", kind: str, rows: int) -> None:
    assert seen["profile_exit"] == 0 and seen["generate_exit"] == 0, seen
    if not (
        (rows >= 20000 and kind in _HELD_LIMITS_AT_20000)
        or (rows < 20000 and kind in shapes.SAFE_HARBOR_HELD_LIMITS_AT_600)
    ):
        assert seen["validate_exit"] == 0, seen
    elif kind in shapes.AGES:
        # ...and a limit of the twin is the control table's own, never the
        # top-code's (the second repair: `ages4ph`, `agescomma`).
        assert seen["twin_misses"] == seen["control_twin_misses"], seen
    assert seen["description_values"] == 0, seen
    assert seen["description_fragments"] == 0, seen
    assert seen["twin_cells"] == 0, seen
    assert seen["twin_fragments"] == 0, seen
    asked = seen["asked"]
    assert isinstance(asked, list) and len(asked) == 1, seen
    offered = asked[0]
    assert isinstance(offered, list)
    harbor = [asking.ANSWER_SAFE_HARBOR_NO, asking.ANSWER_SAFE_HARBOR_YES]
    if kind in shapes.AGES:
        assert seen["top_coded"] == taxonomy.TOP_CODE, seen
        # THE SUMMARY SAYS SO (skeptic 1 of lane SH, item 11).
        assert _SUMMARY_LINE in f"{seen['summary']}", seen
        # THE REAL TABLE MEETS ITS OWN DESCRIPTION, read under the top-code.
        if seen["role"] == taxonomy.ROLE_IDENTIFIER:
            assert set(_MISSED.findall(f"{seen['real_quality']}")) <= _HELD_REAL_MISSES, seen
        else:
            assert seen["validate_real_exit"] == 0, seen
        assert (
            offered == harbor and seen["read_as_now"] == [asking.SAFE_HARBOR_TOP_CODED]
            and "THE SAFE HARBOR QUESTION" in f"{seen['screen']}"
        ) or (
            asking.ANSWER_IDENTIFIER in offered
            and seen["read_as_now"] == [asking.ANSWER_IDENTIFIER]
            and seen["role"] == taxonomy.ROLE_IDENTIFIER
        ), seen
    else:
        assert seen["role"] == taxonomy.ROLE_IDENTIFIER, seen
        # ONE QUESTION A COLUMN: the Safe Harbor question, or the question
        # offering `identifier` already put, which holds it meanwhile.
        assert (
            offered == harbor and seen["read_as_now"] == [asking.ANSWER_SAFE_HARBOR_YES]
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


@pytest.mark.parametrize("kind", shapes.SAFE_HARBOR_NUMBERS)
def test_no_zip_and_no_age_over_89_is_published_at_20000_rows(
    tmp_path: pathlib.Path, kind: str
) -> None:
    """The owner's table floor: the same at 20,000 rows, where each shape was measured live."""
    _check(shapes.run_safe_harbor(tmp_path, kind, 20000), kind, 20000)


@pytest.mark.parametrize(("kind", "answer"), shapes.SAFE_HARBOR_ANSWERED)
@pytest.mark.parametrize("rows", [600, 20000])
def test_an_answer_to_the_other_question_puts_the_safe_harbor_question(
    tmp_path: pathlib.Path, kind: str, answer: str, rows: int
) -> None:
    """Items 1 and 6 of the second repair: no other answer frees an age over 89 or a ZIP.

    NAACCR's Age at Diagnosis answered `measurement` printed 91 to 105
    and its twin wrote 606 cells over 90, and answered `code` 93 and 100
    to 105 with 572 cells over 90; ZIP codes answered `measurement`,
    `keep` or `code` printed 40 of 40 (the third repair: `code` too, the
    orchestrator's rulings R1 and R2). Each answer is kept, the
    Safe Harbor question is the one question put, and the column is
    top-coded (ages) or held (ZIPs) until `no`.
    """
    seen = shapes.run_safe_harbor(tmp_path, kind, rows, answer)
    assert seen["profile_exit"] == 0 and seen["generate_exit"] == 0, seen
    assert seen["description_values"] == 0, seen
    assert seen["description_fragments"] == 0, seen
    assert seen["twin_cells"] == 0, seen
    assert seen["twin_fragments"] == 0, seen
    assert seen["asked"] == [[asking.ANSWER_SAFE_HARBOR_NO, asking.ANSWER_SAFE_HARBOR_YES]], seen
    if kind in shapes.ZIP_KINDS:
        assert seen["role"] == taxonomy.ROLE_IDENTIFIER, seen
        assert seen["read_as_now"] == [asking.ANSWER_SAFE_HARBOR_YES], seen
    else:
        assert seen["top_coded"] == taxonomy.TOP_CODE, seen
        assert seen["read_as_now"] == [asking.SAFE_HARBOR_TOP_CODED], seen
        assert seen["validate_real_exit"] == 0, seen
        # THE TOP-CODE COSTS THE TWIN NO FACT: it misses what the twin of
        # the table written with every age above 89 as `090` misses, which
        # no top-code touches -- answered `measurement`, the padding and
        # styles of the unpadded `999` (at 20,000 rows) -- a generation
        # limit outside lane SH (wave6/SH/r2, wave6/SH-verify.md).
        assert seen["twin_misses"] == seen["control_twin_misses"], seen


@pytest.mark.parametrize("rows", [600, 20000])
def test_the_zoos_zip_codes_answered_code_stay_held(tmp_path: pathlib.Path, rows: int) -> None:
    """The third repair (ruling R1; LANE SH ADDENDA 8 and 9): the zoo's own `zip5`, answered `code`.

    On 9a333e46 its answer `code` printed 11 of 12 real ZIPs at 600 rows
    and 12 of 12 at 20,000, written on every twin cell. Now the Safe
    Harbor question follows that answer in the next run, one question at
    a time; the zoo answers it truthfully, `yes` (a place smaller than a
    state), and the column stays held: 0 real ZIPs in any file and the
    twin, `zip4`'s heads among them, and the analyst's `levels zip5`
    fails, the HIPAA price K-HZ-02 counts.
    """
    seen = shapes.run_zoo_zips(tmp_path, rows)
    assert seen["steps"] == {"profile": 0, "answers": 0, "generate": 0, "validate": 0}, seen
    assert seen["description_values"] == 0, seen
    assert seen["description_fragments"] == 0, seen
    assert seen["twin_cells"] == 0, seen
    assert seen["twin_fragments"] == 0, seen
    roles = seen["roles"]
    assert isinstance(roles, dict)
    assert roles["zip5"] == roles["zip4"] == taxonomy.ROLE_IDENTIFIER, seen
    asked = seen["asked"]
    assert isinstance(asked, list) and len(asked) == 2, seen
    assert asked[0][1] == asking.ANSWER_CODE, seen
    assert asked[1] == ([asking.ANSWER_SAFE_HARBOR_NO, asking.ANSWER_SAFE_HARBOR_YES],
                        asking.ANSWER_SAFE_HARBOR_YES), seen
    assert "levels zip5" in f"{seen['analyst']}", seen


# -- the reach, cell by cell ----------------------------------------------


def _ages(*extra: str) -> "list[str]":
    return [f"{age}" for age in range(18, 104)] + list(extra)


def _reach(
    cells: "list[str]", absent: "frozenset[str]" = frozenset([""]), levels: bool = False
) -> str:
    return taxonomy.safe_harbor_reach(cells, False, absent, 11, levels)


_FOUR = [f"{2100 + 7 * k}" for k in range(40)]
_WORDS = [f"w{chr(97 + place % 26)}{chr(97 + place // 26)}" for place in range(80)]


@pytest.mark.parametrize(
    ("cells", "reach"),
    [
        (_ages(), taxonomy.SAFE_HARBOR_AGES),
        ([f"{age}" for age in range(18, 90)], ""),  # nothing above 89
        # AN OUTLIER DOES NOT SWITCH THE TOP-CODE OFF (addendum 1 (2)): a
        # lone value above 125 or a negative stands among the remaining.
        (_ages("126"), taxonomy.SAFE_HARBOR_AGES),
        (_ages("-1"), taxonomy.SAFE_HARBOR_AGES),
        (["60"] * 100 + ["95"] * 99 + ["130"], taxonomy.SAFE_HARBOR_AGES),
        # ...nor does a placeholder share (addenda 1 (2), 2 (1)): set aside.
        (["60"] * 65 + ["95"] * 65 + ["999"] * 70, taxonomy.SAFE_HARBOR_AGES),
        (["60"] * 65 + ["95"] * 65 + ["-1"] * 70, taxonomy.SAFE_HARBOR_AGES),
        (["60"] * 65 + ["95"] * 65 + ["888"] * 70, taxonomy.SAFE_HARBOR_AGES),
        # ...and every role (addendum 1 (1)): two values, one value.
        (["60"] * 100 + ["95"] * 100, taxonomy.SAFE_HARBOR_AGES),
        (["95"] * 200, taxonomy.SAFE_HARBOR_AGES),
        # LABELS (addenda 2 (2), 3 (2)): a unit word, and words of any share.
        ([f"{age} years" for age in range(18, 105)], taxonomy.SAFE_HARBOR_AGES),
        (["60"] * 65 + ["95"] * 65 + ["UNK"] * 70, taxonomy.SAFE_HARBOR_AGES),
        (["60"] * 60 + ["95"] * 60 + _WORDS, taxonomy.SAFE_HARBOR_AGES),
        # THE CEILING IS 125 (skeptic 1, item 10): 115 is in the reach.
        ([f"{age}" for age in range(18, 90)] + ["115"], taxonomy.SAFE_HARBOR_AGES),
        # A FEW PADDED CELLS ARE AGES STILL (skeptic 1, item 5); a column of
        # them is a code's spelling.
        (_ages("07"), taxonomy.SAFE_HARBOR_AGES),
        (["095", "060", "070"] * 20, ""),
        # THE PROFILER'S OWN GRAMMAR (Codex's review, item 5).
        ([f"{18 + place % 72}" for place in range(499)] + ["95"] + ["99,000e-3"] * 100,
         taxonomy.SAFE_HARBOR_AGES),
        # ...and the bulk: more than the floor's rows and one remaining
        # cell in twenty outside.
        ([f"{age}" for age in range(18, 104)] + [f"{200 + place}" for place in range(50)], ""),
        # A MEASUREMENT'S TAIL PAST 125 IS NO PLACEHOLDER (measured on
        # 4282f7ee: setting every repeated value aside top-coded the
        # analyst tables' glucose, sbp, crp and follow-up days): systolic
        # pressures from 95 to 139, each on 20 rows, two in three within
        # 0 to 125, stay out of the reach...
        ([f"{95 + place % 45}" for place in range(900)], ""),
        # ...while three placeholders on the floor's rows are set aside,
        # and a few typing slips (one remaining cell in twenty) stand.
        (_ages() * 5 + ["777"] * 100 + ["888"] * 100 + ["555"] * 100, taxonomy.SAFE_HARBOR_AGES),
        # ...and a one-figure negative beside them, set aside as `-d`.
        (_ages() * 5 + ["777"] * 100 + ["888"] * 100 + ["555"] * 100 + ["-1"] * 90,
         taxonomy.SAFE_HARBOR_AGES),
        (_ages() * 5 + [f"{300 + place}" for place in range(21)], taxonomy.SAFE_HARBOR_AGES),
        # ...and `999` beside three more placeholders, each on 6 % of the
        # rows: nines alone are set aside before the three are counted
        # (the second repair, item 7: read as an ordinary value, the
        # fourth placeholder stood as strays and the reach was lost).
        (_ages() * 5 + ["777"] * 30 + ["888"] * 30 + ["555"] * 30 + ["999"] * 30,
         taxonomy.SAFE_HARBOR_AGES),
        # AN UNDECLARED DECIMAL COMMA (the second repair, item 3): `94,8`
        # read with its comma for the point where the point reads none.
        ([f"{age},5" for age in range(18, 104)], taxonomy.SAFE_HARBOR_AGES),
        # ZIPS (addenda 1 (3), 3 (1), 4 and 5; skeptic 1, item 8; Codex,
        # item 6): four figures beside five, placeholders of any share,
        # 99999 a ZIP, ZIP+4 cells, a plus sign, words of any share.
        (["52240"] * 20 + ["2100"], taxonomy.SAFE_HARBOR_ZIPS),
        (["2100", "2107", "52240", "52247"] * 50, taxonomy.SAFE_HARBOR_ZIPS),
        ([f"0{zip_code}" for zip_code in _FOUR] * 3 + ["-99"] * 70, taxonomy.SAFE_HARBOR_ZIPS),
        (_FOUR * 3 + ["99999"] * 11, taxonomy.SAFE_HARBOR_ZIPS),
        (_FOUR * 3 + ["-9999"] * 30 + ["999999"] * 30, taxonomy.SAFE_HARBOR_ZIPS),
        (["52240"] * 200 + ["UNKNOWN"] + ["52240-1000"] * 20, taxonomy.SAFE_HARBOR_ZIPS),
        # ...a ZIP+4 cell is a five-figure value, whatever its share.
        (["52240"] * 20 + ["52240-1000"] * 20, taxonomy.SAFE_HARBOR_ZIPS),
        ([f"+{52200 + place % 80}" for place in range(597)] + ["UNKNOWN"] * 3,
         taxonomy.SAFE_HARBOR_ZIPS),
        (["02100"] * 20 + ["UNKNOWN"] * 20, taxonomy.SAFE_HARBOR_ZIPS),
        # NINE FIGURES ARE A ZIP+4 WITHOUT ITS HYPHEN (the second repair,
        # item 4), padded or not, beside words.
        ([f"5224{place % 10}{1000 + place}" for place in range(300)] + ["UNKNOWN"] * 3,
         taxonomy.SAFE_HARBOR_ZIPS),
        ([f"0210{place % 10}{1000 + place}" for place in range(300)] + ["UNKNOWN"] * 3,
         taxonomy.SAFE_HARBOR_ZIPS),
        # FOUR FIGURES BESIDE OTHER WIDTHS are a count as often as ZIP
        # codes that lost their zero (lane ZR-b's page): reached where the
        # role prints levels (below), not as a count -- birth weights in
        # grams from 700 -- but every one of four, placeholders aside, is
        # the fixed-width question's shape, and reached.
        ([f"{700 + 13 * place}" for place in range(300)], ""),
        (_FOUR * 3 + ["-9999"] * 7, taxonomy.SAFE_HARBOR_ZIPS),
        # ...and no ZIP is grouped between thousands or padded to four.
        ([f"{12000 + 7 * place:,}" for place in range(300)], ""),
        ([f"0{100 + place}" for place in range(300)] + ["52240"], ""),
        # ...nor a placeholder: one value grouped on fourteen rows beside
        # the same value ungrouped (the mixture reader's column).
        (["1,234.00"] * 7 + ["1 234.00"] * 7 + ["1234.00"] * 86, ""),
        (["52240"] * 20 + ["5224a"] * 20, ""),  # other forms past the bulk
        (["123456"] * 20 + ["1234567"] * 20, ""),
    ],
)
def test_the_reach_is_judged_on_the_bulk(cells: "list[str]", reach: str) -> None:
    assert _reach(cells) == reach


@pytest.mark.parametrize(
    ("cells", "reach"),
    [
        # A ROLE THAT PRINTS LEVELS (addendum 5): two four-figure ZIPs,
        # one, and forty beside a placeholder share.
        (["2100"] * 100 + ["2107"] * 100, taxonomy.SAFE_HARBOR_ZIPS),
        (["2100"] * 200, taxonomy.SAFE_HARBOR_ZIPS),
        (_FOUR * 3 + ["-9999"] * 30, taxonomy.SAFE_HARBOR_ZIPS),
        # ...a padded four-figure code is none, at any role.
        ([f"0{100 + place}" for place in range(40)] * 3, ""),
        # ...and four figures beside a few of three, as levels only.
        (_FOUR * 3 + ["815", "920"], taxonomy.SAFE_HARBOR_ZIPS),
    ],
)
def test_four_figures_alone_are_reached_where_the_role_prints_levels(
    cells: "list[str]", reach: str
) -> None:
    assert _reach(cells, levels=True) == reach
    assert _reach(cells) == ("" if reach == "" or "815" in cells else reach)



def test_an_answered_padded_question_ends_the_padded_test() -> None:
    """The second repair, item 1: three-figure ages answered `measurement` are ages."""
    cells = [f"{age:03d}" for age in range(0, 106)] * 3 + ["999"] * 6
    assert _reach(cells) == ""
    assert taxonomy.safe_harbor_reach(
        cells, False, frozenset([""]), 11, False, True
    ) == taxonomy.SAFE_HARBOR_AGES


def test_absent_cells_are_set_aside() -> None:
    """Codex's review, item 1: a declared missing `-1` is absent, not an outlier."""
    cells = _ages() * 7 + ["-1"] * 300
    assert _reach(cells, frozenset(["", "-1"])) == taxonomy.SAFE_HARBOR_AGES
    coded = taxonomy.top_coded_cells(["95", "93", "-1", ""], False, frozenset(["95", ""]))
    assert coded == ["95", "90", "-1", ""]


def test_the_top_code_reads_every_value_from_90_to_125_as_90() -> None:
    coded = taxonomy.top_coded_cells(_ages("", "N/A", "115", "130", "999"))
    assert max(float(cell) for cell in coded[:86]) == 90.0
    assert coded[86:] == ["", "N/A", "90", "130", "999"]
    assert coded[:72] == [f"{age}" for age in range(18, 90)]


def test_the_top_code_keeps_each_cells_own_form() -> None:
    """Its sign (skeptic 1, item 12), spaces, unit word, decimals, comma and padding."""
    assert taxonomy.top_coded_cells(
        ["+95", " 95", "95 years", "095", "45.5", "93.25", "99,000e-3", "1e2", "89.5"]
    ) == ["+90", " 90", "90 years", "090", "45.5", "90.00", "90", "90", "89.5"]
    assert taxonomy.top_coded_cells(["45,5", "93,25"], comma=True) == ["45,5", "90,00"]
    # ...and an undeclared decimal comma keeps its comma (the second repair, item 3).
    assert taxonomy.top_coded_cells(["45,5", "94,8", "101,102"]) == ["45,5", "90,0", "101,102"]


def test_the_twin_writes_none_above_90_and_keeps_its_counts() -> None:
    assert taxonomy.at_most_the_top_code(["91", "90.5", "88", "999", "x", "+91"]) == [
        "90", "89.9", "88", "999", "x", "+90"
    ]
    # ...the count of different values kept where a free one lies above 89.
    assert taxonomy.at_most_the_top_code(["90.0", "90.4", "90.7", "92", "89.9"]) == [
        "90.0", "89.8", "89.7", "90", "89.9"
    ]
    # ...or down to the column's least value (a tail of 99 beside 60 and 90).
    assert taxonomy.at_most_the_top_code(["60", "90", "99", "99"]) == ["60", "90", "89", "89"]


def test_the_twins_clamp_keeps_the_missing_cells() -> None:
    """The second repair, item 5: `--missing-value 95` had its missing cells written 90."""
    assert taxonomy.at_most_the_top_code(["95", "91", " 95", "60"], frozenset(["95"])) == [
        "95", "90", " 95", "60"
    ]


def test_the_twin_keeps_how_many_cells_each_value_holds() -> None:
    """Codex's review, item 3: five copies of one value stay one value."""
    cells = [f"{18 + 71.9 * place / 594:.3f}" for place in range(595)] + ["90.704"] * 5
    written = taxonomy.at_most_the_top_code(cells)
    assert len(set(written)) == len(set(cells)) == 596
    assert len(set(written[-5:])) == 1


def test_the_twins_search_ends_at_any_precision() -> None:
    """Codex's review, item 4: twenty decimals searched 1e-20 at a time."""
    cells = [f"{18 + 71.9 * place / 594:.20f}" for place in range(595)]
    cells += ["90.70427430271596000000"] * 5
    started = time.monotonic()
    written = taxonomy.at_most_the_top_code(cells)
    assert time.monotonic() - started < 5
    assert len(set(written)) == 596
    assert written[-1] == "90.00000000000000000000"


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


# A ZIP SHAPE ONLY THIS LANE HOLDS (batch 4k's merge of lane SH): since
# lane CODES-3 (plan P4-D428) the padded `zip5word_homeless` is held as
# keys beside words, read `identifier` and put the person question, and
# the unpadded one is put the date-count question first; so the Safe
# Harbor question these tests answer is put to `zip_mixed`, ZIPs of four
# and five figures and no word, read as a count.
@pytest.mark.parametrize("kind", ["ages", "zip_mixed", "zip4_binary"])
def test_yes_holds_the_column_and_closes_the_question(
    tmp_path: pathlib.Path, kind: str
) -> None:
    """`yes` is P4-D401's held block, never a person column, and is not asked again.

    Codex's review, item 8: a ZIP column answered `yes` stayed among the
    columns held for their figures and was asked the same question again.
    """
    seen = _answered(tmp_path, kind, asking.ANSWER_SAFE_HARBOR_YES)
    block = seen["block"]
    assert isinstance(block, dict)
    assert block["role"] == taxonomy.ROLE_IDENTIFIER
    assert [(entry["column"], entry["your_answer"]) for entry in seen["carried"]] == [
        (kind, asking.ANSWER_SAFE_HARBOR_YES)
    ]
    assert seen["asked"] == []


def test_no_lifts_the_hold_on_zip_shaped_numbers(tmp_path: pathlib.Path) -> None:
    seen = _answered(tmp_path, "zip_mixed", asking.ANSWER_SAFE_HARBOR_NO)
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


def test_no_is_true_of_a_measurement() -> None:
    """Skeptic 1, item 7, and the orchestrator's addendum 1 (4): a pulse is no category."""
    document: "dict[str, object]" = {
        "columns": [{"name": "pulse", "role": "count", "top_coded": 90}]
    }
    question = asking.safe_harbor_questions(document, (), [])[0]
    meaning = {choice.answer: choice.means for choice in question.choices}
    assert meaning[asking.ANSWER_SAFE_HARBOR_NO] == (
        "none of these: the values are measurements, counts, codes or categories "
        "that name no person, place, date or record"
    )
    assert "placeholders and words set aside" in question.shape


def test_no_second_question_beside_an_open_one() -> None:
    """MUST NOT: a second question where one is put (the person question keeps its place)."""
    document: "dict[str, object]" = {
        "columns": [{"name": "age", "role": "count", "top_coded": 90},
                    {"name": "zip", "role": "count"}]
    }
    person = asking.Question("age", "count", asking.BECAUSE_REPEATS_AND_MANY, "", [],
                             asking.ANSWER_KEEP)
    held = asking.Question("zip", "count", asking.BECAUSE_REPEATS_AND_MANY, "", [],
                           asking.ANSWER_KEEP)
    assert asking.safe_harbor_questions(document, ("zip",), [person, held]) == []
    assert [one.name for one in asking.safe_harbor_questions(document, ("zip",), [])] == [
        "age", "zip"
    ]


# -- the escapes Codex's review and skeptic 1 measured on 28e5d2f5 ---------


def _profile(folder: pathlib.Path, name: str, lines: "list[str]", *typed: str) -> int:
    table = folder / f"{name}.csv"
    table.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    with shapes.nobody_at_the_keyboard():
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return cli.main(["profile", f"{table}", "--out-dir", f"{folder}", "--replace"]
                            + list(typed))


def _block(folder: pathlib.Path, name: str, column: str) -> "dict[str, object]":
    document = json.loads((folder / f"{name}-profile.json").read_text(encoding="utf-8"))
    return [one for one in document["columns"] if one["name"] == column][0]


def _published_numbers(block: "dict[str, object]") -> "list[float]":
    """Every number the block publishes as a value: rungs, mode, tails."""
    found: "list[float]" = []
    for key in ("percentiles", "percentiles_between"):
        rungs = block.get(key)
        if isinstance(rungs, dict):
            found += [value for value in rungs.values() if isinstance(value, (int, float))]
    mode = block.get("mode")
    if isinstance(mode, (int, float)):
        found += [mode]
    tails = block.get("tails")
    if isinstance(tails, dict):
        for side in tails.values():
            if isinstance(side, dict):
                found += [one for one in side.get("values", []) if isinstance(one, (int, float))]
    return found


@pytest.mark.parametrize("missing", ["-1", "95"])
def test_declared_missing_values_keep_their_cells(tmp_path: pathlib.Path, missing: str) -> None:
    """Codex's review, item 1: `-1` declared missing turned the top-code off; `95` lost its cells."""
    ages = [f"{18 + place % 86}" for place in range(86 * 7)]
    lines = ["pid,age"] + [f"P{row:05d},{cell}" for row, cell in enumerate(ages + [missing] * 11)]
    assert _profile(tmp_path, "t", lines, "--missing-value", missing) == 0
    block = _block(tmp_path, "t", "age")
    assert block["top_coded"] == taxonomy.TOP_CODE
    assert block["n_missing"] == 11 + (7 if missing == "95" else 0)
    assert max(_published_numbers(block)) <= taxonomy.TOP_CODE
    # ...AND THE TWIN KEEPS THEM (the second repair, item 5): its clamp
    # wrote the 18 missing `95` cells as 90, and the twin failed (exit 3).
    described = f"{tmp_path / 't-profile.json'}"
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        assert cli.main(["generate", described, "--out-dir", f"{tmp_path}", "--seed", "0",
                         "--replace"]) == 0
        assert cli.main(["validate", described, "--twin", f"{tmp_path / 't-twin.csv'}",
                         "--out-dir", f"{tmp_path}", "--replace"]) == 0


def test_a_missing_value_of_90_holds_the_column(tmp_path: pathlib.Path) -> None:
    """Codex's review, item 1: with 90 declared missing, ages read as 90 became missing."""
    ages = [f"{18 + place % 86}" for place in range(86 * 7)]
    lines = ["pid,age"] + [f"P{row:05d},{cell}" for row, cell in enumerate(ages)]
    assert _profile(tmp_path, "t", lines, "--missing-value", "90") == 0
    block = _block(tmp_path, "t", "age")
    assert block["role"] == taxonomy.ROLE_IDENTIFIER
    assert block["n_missing"] == 7
    asked = json.loads((tmp_path / "t-questions.json").read_text(encoding="utf-8"))["asked"]
    held = [entry for entry in asked if entry["column"] == "age"]
    assert [entry["read_as_now"] for entry in held] == [asking.ANSWER_SAFE_HARBOR_YES]
    assert "cannot be read as 90" in held[0]["what_synthtwin_saw"]


def test_ages_held_in_people_validate_as_described(tmp_path: pathlib.Path) -> None:
    """Codex's review, item 2: the count in people held ages built from other cells."""
    lines = ["pid,age"] + [
        f"P{person:04d},{20 + person % 85}" for person in range(100) for _visit in range(10)
    ]
    assert _profile(tmp_path, "t", lines, "--identifier", "pid") == 0
    block = _block(tmp_path, "t", "age")
    assert block["role"] == taxonomy.ROLE_IDENTIFIER
    assert block["top_coded"] == taxonomy.TOP_CODE
    (tmp_path / "real").mkdir()
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        checked = cli.main(["validate", f"{tmp_path / 't-profile.json'}", "--twin",
                            f"{tmp_path / 't.csv'}", "--out-dir", f"{tmp_path / 'real'}",
                            "--replace"])
    # A held block's real table misses its census of repetition (exit 3).
    assert checked in (0, 3), checked
    report = (tmp_path / "real" / "t-quality.txt").read_text(encoding="utf-8")
    assert set(_MISSED.findall(report)) <= _HELD_REAL_MISSES


def test_the_profilers_own_number_grammar_is_top_coded(tmp_path: pathlib.Path) -> None:
    """Codex's review, item 5: `99,000e-3` reads 99 and was published as 99."""
    cells = [f"{18 + place % 72}" for place in range(499)] + ["95"] + ['"99,000e-3"'] * 100
    lines = ["pid,age"] + [f"P{row:05d},{cell}" for row, cell in enumerate(cells)]
    assert _profile(tmp_path, "t", lines) == 0
    block = _block(tmp_path, "t", "age")
    assert block["top_coded"] == taxonomy.TOP_CODE
    assert max(_published_numbers(block)) <= taxonomy.TOP_CODE


def test_a_padded_cell_answered_measurement_is_top_coded(tmp_path: pathlib.Path) -> None:
    """Skeptic 1, item 5: one `07` took ages answered `measurement` out of the reach."""
    table, _real = shapes.write_safe_harbor_table(tmp_path, "ages", 20000)
    lines = table.read_text(encoding="utf-8").splitlines() + ["P999999,07"]
    assert _profile(tmp_path, "ages_long", lines, "--measurement", "ages") == 0
    block = _block(tmp_path, "ages_long", "ages")
    assert block["top_coded"] == taxonomy.TOP_CODE
    assert max(_published_numbers(block)) <= taxonomy.TOP_CODE
    asked = json.loads((tmp_path / "ages_long-questions.json").read_text(encoding="utf-8"))
    assert [entry["read_as_now"] for entry in asked["asked"] if entry["column"] == "ages"] == [
        asking.SAFE_HARBOR_TOP_CODED
    ]


def test_an_answer_beside_a_new_reading_is_refused(tmp_path: pathlib.Path) -> None:
    """Codex's review, item 7: `yes` beside a first-row answer was dropped in silence.

    The header `column_2,column_1,age` reads as a record too (its words
    stand in the first rows' cells), so the first-row question is put
    beside the Safe Harbor question of the ages; answered together, the
    run refuses them as every answer naming a column beside a new reading
    is refused (plan P4-D408), and asks for two runs.
    """
    lines = ["column_2,column_1,age"]
    for place in range(600):
        second = "column_1" if place < 11 else f"S{place:05d}"
        age = "age" if place < 11 else f"{95 if place % 30 == 0 else 18 + place % 70}"
        lines += [f"P{place % 12 + 1:05d},{second},{age}"]
    assert _profile(tmp_path, "t", lines) == 0
    document = json.loads((tmp_path / "t-questions.json").read_text(encoding="utf-8"))
    about = [entry for entry in document["about_your_file"]
             if entry["column"] == asking.FIRST_ROW_SUBJECT]
    harbor = [entry for entry in document["asked"]
              if entry["read_as_now"] == asking.SAFE_HARBOR_TOP_CODED]
    assert len(about) == 1 and len(harbor) == 1
    about[0]["your_answer"] = asking.ANSWER_FIRST_ROW_NAMES
    harbor[0]["your_answer"] = asking.ANSWER_SAFE_HARBOR_YES
    answers = tmp_path / "answers.json"
    answers.write_text(json.dumps(document), encoding="utf-8", newline="\n")
    assert _profile(tmp_path, "t", lines, "--answers", f"{answers}") == 2
